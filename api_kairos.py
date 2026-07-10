"""
LUMINARK Kairos Engine v1.0 – Therapeutic API with session tracking, journaling, and coaching.
Kairos: the opportune moment for change.

Configuration (environment variables, all optional):
  KAIROS_STORAGE_BACKEND   "memory" (default) or "file". "memory" sessions do
                            not survive a process restart and are not shared
                            across multiple uvicorn workers -- use "file" for
                            anything beyond local single-process dev.
  KAIROS_DATA_DIR           Directory for session JSON files when
                            KAIROS_STORAGE_BACKEND="file". Defaults to
                            "./kairos_data".
  KAIROS_API_KEY             If set, every request (except /health) must send
                            a matching "X-API-Key" header. If unset, the API
                            is open -- fine for local dev, not for anything
                            network-reachable.
  KAIROS_ALLOWED_ORIGINS   Comma-separated list of origins allowed to call
                            this API from a browser (CORS). If unset, no CORS
                            middleware is added (safe default: no browser
                            can call this cross-origin).
  KAIROS_ENABLE_AI_SCORING  "true" to turn on POST /score-nsdt (AI-assisted
                            NSDT scoring via Claude). Off by default. See
                            sap_kairos_ai_scoring.py.
  ANTHROPIC_API_KEY         Required if KAIROS_ENABLE_AI_SCORING is on.
  KAIROS_AI_SCORING_MODEL   Claude model for /score-nsdt. Defaults to
                            "claude-sonnet-5".
  KAIROS_ENABLE_AI_READINGS "true" to turn on POST /reading and
                            POST /elaborate (AI-deepened, consumer-facing
                            readings via Claude -- narrative, a story/quote
                            parallel, a Trickster Take, and follow-up
                            questions). Off by default. See
                            sap_kairos_ai_reading.py. Stage classification
                            itself is NOT done here -- the caller supplies
                            an already-determined stage (e.g. from the
                            webapp's own digit-root arithmetic); this only
                            generates the narrative layer around it.
  ANTHROPIC_API_KEY         Also required for AI readings (shared with
                            KAIROS_ENABLE_AI_SCORING).
  KAIROS_AI_READING_MODEL   Claude model for /reading and /elaborate.
                            Defaults to "claude-sonnet-5".
"""

import os
import time
import math
import numpy as np
from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator
from typing import Optional
from dataclasses import asdict

from sap_kairos_bayesian import KairosBayesian
from sap_kairos_session import KairosSession, KairosSnapshot
from sap_kairos_ai_scoring import score_nsdt_from_notes, AIScoreError, is_ai_scoring_configured
from sap_kairos_ai_reading import (
    generate_ai_reading,
    elaborate_reading,
    AIReadingError,
    is_ai_readings_configured,
)
from sap_kairos_public_content import DATA_HANDLING_NOTE
from sap_kairos_tumbling_inversion import compute_inversion, compute_arc_direction, divergence_category
from sap_kairos_stage_paradox import (
    detect_middle_path,
    classify_flow_quality,
    classify_crucible_mode,
    classify_crystallization,
)
from sap_kairos_disruption_loops import loop_for_cynical_pattern
from sap_kairos_nsdt_estimator import estimate_nsdt_from_text, NSDTEstimateError

# --- Configuration (env-driven, all backwards-compatible defaults) ---
KAIROS_STORAGE_BACKEND = os.environ.get("KAIROS_STORAGE_BACKEND", "memory")
KAIROS_DATA_DIR = os.environ.get("KAIROS_DATA_DIR", "./kairos_data")
KAIROS_API_KEY = os.environ.get("KAIROS_API_KEY")  # unset => no auth enforced
KAIROS_ALLOWED_ORIGINS = os.environ.get("KAIROS_ALLOWED_ORIGINS", "")

app = FastAPI(title="LUMINARK Kairos Engine", version="1.0")

if KAIROS_ALLOWED_ORIGINS:
    _origins = [o.strip() for o in KAIROS_ALLOWED_ORIGINS.split(",") if o.strip()]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

_sessions: dict[str, KairosSession] = {}


def require_api_key(x_api_key: Optional[str] = Header(default=None)):
    """No-op when KAIROS_API_KEY is unset (dev mode). When set, every
    protected request must include a matching X-API-Key header."""
    if KAIROS_API_KEY and x_api_key != KAIROS_API_KEY:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")


class KairosInput(BaseModel):
    system_id: str
    nsdt: list[float] = Field(..., min_items=5, max_items=5)
    allow_regression: bool = True
    temperature: float = 0.7
    beta: float = 0.6
    journal_entry: Optional[str] = None

    @field_validator('nsdt')
    @classmethod
    def validate_nsdt(cls, v):
        for i, val in enumerate(v):
            if not isinstance(val, (int, float)):
                raise ValueError(f"nsdt[{i}] must be a number")
            if math.isnan(val) or math.isinf(val):
                raise ValueError(f"nsdt[{i}] is NaN or Inf")
            if val < 0.0 or val > 10.0:
                raise ValueError(f"nsdt[{i}] out of range 0-10")
        return v


class ScoreNSDTInput(BaseModel):
    notes: str
    system_id: Optional[str] = None


class ReadingInput(BaseModel):
    stage: int = Field(..., ge=0, le=9)
    canonical_name: str
    text: str
    domain: Optional[str] = None
    system_id: Optional[str] = None

    @field_validator('text')
    @classmethod
    def validate_text(cls, v):
        if not v or not v.strip():
            raise ValueError("text must not be empty")
        return v


class ThreadTurn(BaseModel):
    question: str
    answer: str


class ElaborateInput(BaseModel):
    stage: int = Field(..., ge=0, le=9)
    canonical_name: str
    original_text: str
    thread: list[ThreadTurn] = Field(..., min_items=1)


def get_or_create_session(system_id: str) -> KairosSession:
    if system_id not in _sessions:
        kwargs = {"storage_backend": KAIROS_STORAGE_BACKEND}
        if KAIROS_STORAGE_BACKEND == "file":
            kwargs["data_dir"] = KAIROS_DATA_DIR
        _sessions[system_id] = KairosSession(system_id, **kwargs)
    return _sessions[system_id]


# First-pass negation cues so obvious phrasing like "not scared anymore" or
# "don't feel stuck" doesn't trigger the matching keyword response below.
# This is still simple substring/window matching, not real NLP -- it will
# miss more complex negation, sarcasm, or double negatives.
_NEGATION_CUES = ("not ", "n't", "no longer", "stopped feeling", "without", "isn't", "wasn't", "aren't")


def _mentioned_without_negation(text: str, phrase: str, window: int = 25) -> bool:
    idx = text.find(phrase)
    if idx == -1:
        return False
    preceding = text[max(0, idx - window):idx]
    return not any(cue in preceding for cue in _NEGATION_CUES)


def generate_coaching_response(stage: int, trap_energy: float, journal_entry: Optional[str]) -> str:
    if journal_entry:
        jl = journal_entry.lower()
        if _mentioned_without_negation(jl, "stuck") or _mentioned_without_negation(jl, "can't move"):
            return "It sounds like you feel stuck. Stage progression can feel slow – that's normal. What would one small step look like?"
        if _mentioned_without_negation(jl, "scared") or _mentioned_without_negation(jl, "fear"):
            return "Fear is a signal, not a stop sign. At Stage 5, fear often means you care. What is the smallest risk you could take today?"
        if _mentioned_without_negation(jl, "angry"):
            return "Anger often masks grief or unmet need. Can you feel what is underneath?"
    if stage == 8:
        if trap_energy > 0.7:
            return "High certainty can be a trap. What would it mean to say 'I don't know'?"
        return "Stage 8 invites you to question your own mastery. Who would you be without the story of having arrived?"
    if stage == 7:
        return "Insight without connection can become isolation. Can you share what you're learning with one trusted person?"
    if stage == 5:
        return "You are at a kairos moment. No decision is permanent – but indecision is also a choice. What feels most alive?"
    return "Trust the process. The stage you are in is exactly where you need to be."


def _to_tumbling_scale(vec: list[float]) -> list[float]:
    """Rescale an NSDT vector from this API's public 0-10 input contract to
    the 0-100 scale the canonical Tumbling Inversion formulas are written
    against (every threshold in TUMBLING_INVERSION_v8.2.md and the user's
    own test suite -- 50, 70, 55, 60, 100-T, etc. -- is calibrated for 0-100).
    Keeping /analyze and /reading on 0-10 preserves the existing public
    contract and matches what sap_kairos_ai_scoring.py already asks Claude
    to produce; this is the one seam where that gets bridged into the
    framework's native scale.
    """
    return [v * 10.0 for v in vec]


def compute_tumbling_inversion_state(nsdt: list[float], dominant_stage: int, session: KairosSession, cynical_loop: bool) -> dict:
    """The real Tumbling Inversion computation for a reading -- this is the
    framework itself running as code, not descriptive text. See
    sap_kairos_tumbling_inversion.py and sap_kairos_stage_paradox.py.

    `nsdt` arrives on this API's public 0-10 scale; it's rescaled to the
    framework's native 0-100 scale before any Tumbling Inversion math runs.

    Stage 5's Middle Path Gateway is sticky on the session once accessed
    (mutates `session`, matching the framework's own claim that a conscious
    choice at Stage 5 reorganizes every remaining stage in the cycle, not
    just the moment it happens).
    """
    nsdt_100 = _to_tumbling_scale(nsdt)
    history_100 = [_to_tumbling_scale(v) for v in session.get_nsdt_history(limit=4)] + [nsdt_100]

    inv = compute_inversion(nsdt_100, dominant_stage)

    mp = detect_middle_path(nsdt_100)
    if dominant_stage == 5 and mp["middle_path_accessed"]:
        session.mark_middle_path_accessed()
    middle_path_accessed = session.middle_path_accessed

    arc_direction, arc_confidence = compute_arc_direction(history_100)

    stage_paradox = None
    if dominant_stage == 6:
        stage_paradox = classify_flow_quality(nsdt_100, middle_path_accessed)
    elif dominant_stage == 7:
        stage_paradox = classify_crucible_mode(nsdt_100, middle_path_accessed, nsdt_history=history_100)
    elif dominant_stage == 8:
        stage_paradox = classify_crystallization(nsdt_100, middle_path_accessed, nsdt_history=history_100)

    disruption_loop = loop_for_cynical_pattern() if cynical_loop else None

    return {
        "parity": inv.parity,
        "physical_stability": inv.physical_stability,
        "consciousness_stability": inv.consciousness_stability,
        "divergence": inv.divergence,
        "divergence_category": divergence_category(inv.divergence),
        "geometric_form": inv.geometric_form,
        "arc_direction": arc_direction,
        "arc_confidence": arc_confidence,
        "middle_path_accessed": middle_path_accessed,
        "witness_score": mp["witness_score"],
        "stage_paradox": stage_paradox,
        "disruption_loop": disruption_loop,
    }


@app.post("/analyze", dependencies=[Depends(require_api_key)])
def analyze_kairos(inp: KairosInput):
    engine = KairosBayesian(
        temperature=inp.temperature,
        beta=inp.beta,
        allow_regression=inp.allow_regression
    )
    session = get_or_create_session(inp.system_id)
    prev = session.get_previous_stage()
    if prev is not None:
        engine.previous_stage = prev

    x = np.array(inp.nsdt)
    result = engine.forward(x)

    regression_count = session.get_regression_count()
    cynical_loop = session.detect_cynical_loop()

    tumbling_inversion = compute_tumbling_inversion_state(inp.nsdt, result["dominant_stage"], session, cynical_loop)

    snapshot = KairosSnapshot(
        timestamp=time.time(),
        dominant_stage=result["dominant_stage"],
        expected_stage=result["expected_stage"],
        entropy=result["entropy"],
        trap_energy=result["trap_energy"],
        therapeutic_note=result["therapeutic_note"],
        somatic_invitation=result["somatic_invitation"],
        trickster_wisdom=result["trickster_wisdom"],
        nsdt=inp.nsdt,
    )
    session.add_snapshot(snapshot)

    coaching = generate_coaching_response(result["dominant_stage"], result["trap_energy"], inp.journal_entry)

    journal_prompt = None
    if result["dominant_stage"] == 8:
        journal_prompt = "What would you lose if you let go of the need to be certain?"
    elif result["dominant_stage"] == 7:
        journal_prompt = "What insight feels too heavy to share? Who could you share it with?"
    elif result["dominant_stage"] == 5:
        journal_prompt = "What is the decision you are avoiding? What would you choose if you knew you couldn't fail?"

    result.update({
        "system_id": inp.system_id,
        "tumbling_inversion": tumbling_inversion,
        "session": {
            "total_snapshots": len(session.snapshots),
            "regression_count_8_to_7": regression_count,
            "cynical_loop_detected": cynical_loop,
        },
        "coaching_response": coaching,
        "journal_prompt": journal_prompt,
    })
    return result


@app.get("/history/{system_id}", dependencies=[Depends(require_api_key)])
def get_history(system_id: str, limit: int = 20):
    session = get_or_create_session(system_id)
    history = session.get_history(limit)
    return {"system_id": system_id, "history": [asdict(s) for s in history]}


@app.post("/reset/{system_id}", dependencies=[Depends(require_api_key)])
def reset_session(system_id: str):
    if system_id in _sessions:
        del _sessions[system_id]
    return {"status": "reset", "system_id": system_id}


@app.post("/score-nsdt", dependencies=[Depends(require_api_key)])
def score_nsdt(inp: ScoreNSDTInput):
    """AI-assisted NSDT scoring (see sap_kairos_ai_scoring.py).

    Disabled unless the operator has set KAIROS_ENABLE_AI_SCORING=true and
    ANTHROPIC_API_KEY. Returns a *proposed* vector with per-axis reasoning --
    this never auto-submits to /analyze. The practitioner reviews and adjusts
    before using it, same as a manually-scored vector.
    """
    if not is_ai_scoring_configured():
        raise HTTPException(
            status_code=503,
            detail=(
                "AI-assisted NSDT scoring is disabled on this server. "
                "Set KAIROS_ENABLE_AI_SCORING=true and ANTHROPIC_API_KEY to enable it."
            ),
        )
    try:
        result = score_nsdt_from_notes(inp.notes)
    except AIScoreError as e:
        raise HTTPException(status_code=502, detail=str(e))

    result["disclosure"] = (
        "These session notes were sent to Anthropic's Claude API to generate this "
        "score. This is a proposed starting point, not a finished score -- review "
        "and adjust each axis before submitting it to /analyze. Axis definitions "
        "are an unconfirmed interpretation -- see docs/NSDT_REFERENCE.md."
    )
    result["system_id"] = inp.system_id
    return result


@app.post("/reading")
def get_ai_reading(inp: ReadingInput):
    """AI-deepened, consumer-facing reading (see sap_kairos_ai_reading.py).

    The STAGE NUMBER (0-9) is decided before this endpoint is called -- by
    the caller's own digit-root arithmetic on the submitted text, the app's
    intentional "find a pattern in literally anything" entry mechanic. That
    part stays as-is; it's the game, not a measurement.

    Everything downstream of that number is now the real engine, not
    narrative invention: this endpoint estimates an NSDT vector from the
    same text (sap_kairos_nsdt_estimator.py, blind to stage taxonomy), runs
    it through the actual Tumbling Inversion + stage paradox math
    (compute_tumbling_inversion_state -- the same function /analyze uses),
    and only then asks Claude to write the human-readable narrative *on top
    of* that computed state, not instead of it.

    If `system_id` is provided, the reading shares session history with
    that system's /analyze calls (arc direction, sticky Middle Path). If
    omitted, an ephemeral in-memory-only session is used for this one call.

    Disabled unless the operator has set KAIROS_ENABLE_AI_READINGS=true and
    ANTHROPIC_API_KEY.
    """
    if not is_ai_readings_configured():
        raise HTTPException(
            status_code=503,
            detail=(
                "AI-deepened readings are disabled on this server. "
                "Set KAIROS_ENABLE_AI_READINGS=true and ANTHROPIC_API_KEY to enable it."
            ),
        )

    if inp.system_id:
        session = get_or_create_session(inp.system_id)
    else:
        session = KairosSession(f"_ephemeral_reading_{id(inp)}", storage_backend="memory")

    try:
        nsdt_estimate = estimate_nsdt_from_text(inp.text)
    except NSDTEstimateError as e:
        raise HTTPException(status_code=502, detail=f"NSDT estimation failed: {e}")

    cynical_loop = session.detect_cynical_loop()
    tumbling_inversion = compute_tumbling_inversion_state(
        nsdt_estimate["nsdt"], inp.stage, session, cynical_loop
    )

    if inp.system_id:
        session.add_snapshot(KairosSnapshot(
            timestamp=time.time(),
            dominant_stage=inp.stage,
            expected_stage=float(inp.stage),
            entropy=0.0,
            trap_energy=0.0,
            therapeutic_note="",
            somatic_invitation="",
            trickster_wisdom="",
            nsdt=nsdt_estimate["nsdt"],
        ))

    try:
        result = generate_ai_reading(
            inp.stage, inp.canonical_name, inp.text, inp.domain,
            tumbling_inversion=tumbling_inversion,
        )
    except AIReadingError as e:
        raise HTTPException(status_code=502, detail=str(e))
    result["disclosure"] = DATA_HANDLING_NOTE
    result["tumbling_inversion"] = tumbling_inversion
    result["nsdt_estimate"] = nsdt_estimate
    return result


@app.post("/reading/elaborate")
def elaborate_ai_reading(inp: ElaborateInput):
    """Continue a reading's follow-up thread (see sap_kairos_ai_reading.py).

    Stateless: the full prior thread is supplied by the caller on every
    call and nothing is stored server-side. Disabled under the same flag
    as POST /reading.
    """
    if not is_ai_readings_configured():
        raise HTTPException(
            status_code=503,
            detail=(
                "AI-deepened readings are disabled on this server. "
                "Set KAIROS_ENABLE_AI_READINGS=true and ANTHROPIC_API_KEY to enable it."
            ),
        )
    try:
        result = elaborate_reading(
            inp.stage,
            inp.canonical_name,
            inp.original_text,
            [t.model_dump() for t in inp.thread],
        )
    except AIReadingError as e:
        raise HTTPException(status_code=502, detail=str(e))
    return result


@app.get("/health")
def health():
    return {"status": "ok", "engine": "LUMINARK Kairos", "active_sessions": len(_sessions)}
