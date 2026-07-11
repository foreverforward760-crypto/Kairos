"""
sap_kairos_nsdt_estimator.py
AI-assisted NSDT estimation for the consumer /reading endpoint.

This is deliberately a separate module from sap_kairos_ai_scoring.py, which
scores a *different*, older 5-axis vocabulary (Connection/Stability/Tension/
Agency/Coherence, from sap_energy_layer.py) for practitioners. The Tumbling
Inversion engine (sap_kairos_tumbling_inversion.py, sap_kairos_stage_paradox.py)
is built against the canonical NSDT axes instead:

  [0] N  Complexity
  [1] S  Stability
  [2] D  Adaptability
  [3] T  Tension
  [4] C  Coherence

Same anti-circularity rule as sap_kairos_ai_scoring.py: Claude sees only the
axis definitions below, never stage names, geometric forms, or Tumbling
Inversion thresholds. It scores what's on the page; the deterministic engine
in sap_kairos_tumbling_inversion.py / sap_kairos_stage_paradox.py does 100%
of the actual classification. This keeps "the framework decides" honest even
when the input vector itself comes from an LLM read of freeform text.

Scores on this module's own 0.0-10.0 scale, matching the public /analyze
contract in api_kairos.py -- the 0-100 rescale for the Tumbling Inversion
math itself happens once, centrally, in compute_tumbling_inversion_state().
"""

import json
import os
import re
from typing import Dict, List, Optional

import anthropic

DEFAULT_MODEL = os.environ.get("KAIROS_AI_READING_MODEL", "claude-sonnet-5")

NSDT_AXIS_DEFINITIONS = """\
Read the text below and score it on five axes, each 0.0-10.0. Score only what \
the text itself supports -- do not infer a life stage, a narrative arc, or any \
kind of framework. You are not told what these scores are used for.

0. Complexity -- how many moving parts, competing threads, or layers of \
   circumstance are present in what's described (low = one simple thread; \
   high = many entangled factors).
1. Stability -- how settled, secure, or held the situation or the writer's \
   position feels right now (low = shaky/in flux; high = solid ground).
2. Adaptability -- how much active capacity to adjust, respond, or integrate \
   new information the writer is showing (low = rigid/stuck; high = flexibly \
   meeting what's happening).
3. Tension -- felt pressure, unresolved conflict, or strain in the text \
   (low = at ease; high = taut, urgent, or under strain).
4. Coherence -- how internally consistent and clear the account is -- does \
   the writer's own story hang together (low = fragmented/contradictory; \
   high = a clear, coherent thread).

Scoring guidance:
- Use 5.0 for "genuinely unclear from the text" rather than inventing precision.
- Score the five axes independently -- don't let a strong reading on one pull \
  the others toward a "consistent story" the text doesn't actually support.
- Base every score only on the text provided, not on genre expectations for \
  "this kind of situation" in general.
"""

NSDT_RESPONSE_SCHEMA = """\
Respond with ONLY a single JSON object, no other text, matching exactly this shape:
{
  "nsdt": [<complexity>, <stability>, <adaptability>, <tension>, <coherence>],
  "confidence": "low" | "medium" | "high"
}
All five nsdt values must be numbers between 0.0 and 10.0.
"""


class NSDTEstimateError(Exception):
    """Raised for any failure in the AI NSDT estimation path."""


def is_nsdt_estimation_configured() -> bool:
    return bool(os.environ.get("ANTHROPIC_API_KEY"))


def _extract_json(text: str) -> dict:
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
        raise NSDTEstimateError(f"Could not parse Claude's response as JSON: {e}") from e


def estimate_nsdt_from_text(text: str, model: Optional[str] = None) -> Dict:
    """Estimate an NSDT vector (0-10 scale) from freeform reader text.

    Returns {"nsdt": [N, S, D, T, C], "confidence": "low"|"medium"|"high"}.
    Falls back to a flat midpoint vector with confidence "unavailable" if AI
    estimation isn't configured or the call fails -- callers can check
    `confidence` to decide whether to surface that to the reader; a
    Tumbling Inversion reading can still run on a midpoint vector, it's
    just less specific.
    """
    if not text or not text.strip():
        raise NSDTEstimateError("text cannot be empty")

    if not is_nsdt_estimation_configured():
        return {"nsdt": [5.0, 5.0, 5.0, 5.0, 5.0], "confidence": "unavailable"}

    client = anthropic.Anthropic()
    model = model or DEFAULT_MODEL

    try:
        response = client.messages.create(
            model=model,
            max_tokens=300,
            system=(
                "You score freeform text on five independent axes for an internal tool. "
                "You are not told what the scores are used for downstream, and should not "
                "speculate about diagnosis, stage names, or any external framework."
            ),
            messages=[
                {
                    "role": "user",
                    "content": (
                        NSDT_AXIS_DEFINITIONS
                        + '\n\nText:\n"""\n'
                        + text.strip()[:4000]
                        + '\n"""\n\n'
                        + NSDT_RESPONSE_SCHEMA
                    ),
                }
            ],
        )
    except anthropic.APIError as e:
        raise NSDTEstimateError(f"Claude API call failed: {e}") from e

    raw_text = "\n".join(b.text for b in response.content if getattr(b, "type", None) == "text")
    if not raw_text:
        raise NSDTEstimateError("Claude returned no text content")

    data = _extract_json(raw_text)
    if "nsdt" not in data or not isinstance(data["nsdt"], list) or len(data["nsdt"]) != 5:
        raise NSDTEstimateError("Claude's response did not include a 5-element 'nsdt' array")

    clamped: List[float] = []
    for i, v in enumerate(data["nsdt"]):
        try:
            v = float(v)
        except (TypeError, ValueError):
            raise NSDTEstimateError(f"nsdt[{i}] is not a number: {v!r}")
        clamped.append(max(0.0, min(10.0, v)))

    return {"nsdt": clamped, "confidence": data.get("confidence", "unknown")}
