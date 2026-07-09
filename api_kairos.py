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

    snapshot = KairosSnapshot(
        timestamp=time.time(),
        dominant_stage=result["dominant_stage"],
        expected_stage=result["expected_stage"],
        entropy=result["entropy"],
        trap_energy=result["trap_energy"],
        therapeutic_note=result["therapeutic_note"],
        somatic_invitation=result["somatic_invitation"],
        trickster_wisdom=result["trickster_wisdom"],
    )
    session.add_snapshot(snapshot)

    regression_count = session.get_regression_count()
    cynical_loop = session.detect_cynical_loop()
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


@app.get("/health")
def health():
    return {"status": "ok", "engine": "LUMINARK Kairos", "active_sessions": len(_sessions)}
