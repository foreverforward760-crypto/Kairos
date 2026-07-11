"""
sap_kairos_ai_scoring.py
AI-assisted NSDT scoring: turns freeform session notes into a proposed 5-axis
NSDT vector using Claude, with per-axis reasoning for a practitioner to review.

Deliberately does NOT tell the model about the stage taxonomy (STAGE_CENTROIDS,
stage names, chambers, etc.) -- it only sees the raw axis definitions below,
which mirror docs/NSDT_REFERENCE.md's "Inferred (best guess, unconfirmed)"
table. This keeps the two systems separate: Claude reads raw signal from
notes, and the deterministic geometry engine (sap_kairos_geometry.py /
sap_kairos_bayesian.py) does the actual stage classification. Showing Claude
the stage taxonomy would let it reverse-engineer a "convenient" vector instead
of independently scoring what it's reading -- and would make stage
classification opaque/LLM-driven instead of the disclosed, inspectable math
the rest of this project is built on.

Disabled by default. Requires both:
  - KAIROS_ENABLE_AI_SCORING=true
  - ANTHROPIC_API_KEY set

Human stays in the loop: this module only ever returns a *proposed* vector
with reasoning. Nothing in this file calls /analyze or otherwise auto-submits
a score -- that decision belongs to whoever is reviewing the output.
"""

import json
import os
import re
from typing import Dict, Optional

import anthropic

DEFAULT_MODEL = "claude-sonnet-5"

# Axis definitions handed to the model verbatim. If docs/NSDT_REFERENCE.md's
# axis table changes, update this to match -- it is the model's entire
# understanding of what it's scoring.
AXIS_DEFINITIONS = """\
Score the following five axes, each 0.0-10.0. These labels are a working,
UNCONFIRMED interpretation carried over from this project's own code
(variable names in sap_energy_layer.py) -- treat them as directional guidance,
not a validated clinical instrument, and say so in your reasoning if the notes
don't clearly support a confident score.

0. Connection (c) -- degree of felt connection to others / self, evident in the notes.
1. Stability (s) -- how settled, secure, or certain the person's stated position feels.
2. Tension (t) -- felt tension, threat, or unresolved pressure.
3. Agency (a) -- sense of choice, capacity to act, felt agency (not actual capability).
4. Coherence (coh) -- internal narrative coherence / certainty of the story being told.

Scoring guidance:
- Use 5.0 for "genuinely unclear from the notes" rather than forcing a confident
  number -- an honest 5.0 is more useful than invented precision.
- Score what's actually in the notes, not what you'd expect for that kind of
  situation in general.
- Score these axes independently of one another; don't let a strong reading on
  one axis pull the others toward a "consistent story" if the notes don't
  support it.
"""

RESPONSE_SCHEMA_INSTRUCTIONS = """\
Respond with ONLY a single JSON object, no other text, matching exactly this shape:
{
  "nsdt": [<connection>, <stability>, <tension>, <agency>, <coherence>],
  "reasoning": {
    "connection": "<one or two sentences>",
    "stability": "<one or two sentences>",
    "tension": "<one or two sentences>",
    "agency": "<one or two sentences>",
    "coherence": "<one or two sentences>"
  },
  "confidence": "low" | "medium" | "high",
  "caveats": "<anything the practitioner should know before trusting this score, or empty string>"
}
All five nsdt values must be numbers between 0.0 and 10.0.
"""


class AIScoreError(Exception):
    """Raised for any failure in the AI scoring path (config, API, parsing)."""


def is_ai_scoring_configured() -> bool:
    enabled = os.environ.get("KAIROS_ENABLE_AI_SCORING", "").strip().lower() in ("1", "true", "yes")
    return enabled and bool(os.environ.get("ANTHROPIC_API_KEY"))


def _extract_json(text: str) -> dict:
    """Claude is asked to return bare JSON, but be defensive: strip code
    fences / leading-trailing prose if present, then parse the first
    top-level {...} block found."""
    text = text.strip()
    fence_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if fence_match:
        text = fence_match.group(1)
    else:
        brace_match = re.search(r"\{.*\}", text, re.DOTALL)
        if brace_match:
            text = brace_match.group(0)
    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        raise AIScoreError(f"Could not parse Claude's response as JSON: {e}") from e


def _validate_scoring_response(data: dict) -> dict:
    if "nsdt" not in data or not isinstance(data["nsdt"], list) or len(data["nsdt"]) != 5:
        raise AIScoreError("Claude's response did not include a 5-element 'nsdt' array")
    clamped = []
    for i, v in enumerate(data["nsdt"]):
        try:
            v = float(v)
        except (TypeError, ValueError):
            raise AIScoreError(f"nsdt[{i}] is not a number: {v!r}")
        clamped.append(max(0.0, min(10.0, v)))
    data["nsdt"] = clamped
    data.setdefault("reasoning", {})
    data.setdefault("confidence", "unknown")
    data.setdefault("caveats", "")
    return data


def score_nsdt_from_notes(notes: str, model: Optional[str] = None) -> Dict:
    """Send freeform session notes to Claude and get back a proposed NSDT
    vector with per-axis reasoning. Raises AIScoreError on any failure --
    callers should surface that as a clear error, not silently fall back to
    a guessed vector."""
    if not is_ai_scoring_configured():
        raise AIScoreError(
            "AI-assisted NSDT scoring is disabled. Set KAIROS_ENABLE_AI_SCORING=true "
            "and ANTHROPIC_API_KEY to enable it."
        )
    if not notes or not notes.strip():
        raise AIScoreError("notes cannot be empty")

    client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from env
    model = model or os.environ.get("KAIROS_AI_SCORING_MODEL", DEFAULT_MODEL)

    try:
        response = client.messages.create(
            model=model,
            max_tokens=1024,
            system=(
                "You are assisting a therapist/coach in scoring session notes onto a "
                "5-axis vector for an internal tool. You are NOT told what the axes "
                "are used for downstream, and should not speculate about diagnosis, "
                "stage names, or any external framework -- score only what is asked."
            ),
            messages=[
                {
                    "role": "user",
                    "content": (
                        AXIS_DEFINITIONS
                        + '\n\nSession notes:\n"""\n'
                        + notes.strip()
                        + '\n"""\n\n'
                        + RESPONSE_SCHEMA_INSTRUCTIONS
                    ),
                }
            ],
        )
    except anthropic.APIError as e:
        raise AIScoreError(f"Claude API call failed: {e}") from e

    text_parts = [block.text for block in response.content if getattr(block, "type", None) == "text"]
    raw_text = "\n".join(text_parts)
    if not raw_text:
        raise AIScoreError("Claude returned no text content")

    data = _extract_json(raw_text)
    data = _validate_scoring_response(data)
    data["model"] = model
    return data
