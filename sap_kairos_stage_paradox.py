"""
Kairos Stage Paradox Engine -- Stages 5 through 8.

Implements the four stage-specific mechanisms described in the Tumbling
Inversion Principle's philosophical architecture (TUMBLING_INVERSION_v8.2.md
Parts 2-6): the Stage 5 Middle Path Gateway, the Stage 6 Conductor's
Paradox, the Stage 7 Individuation Crucible, and the Stage 8
Crystallization Paradox with its Gratitude Mechanism.

These are deterministic classifiers over the same 5-element NSDT vector
used everywhere else in this project ([Complexity, Stability, Adaptability,
Tension, Coherence]) -- not new free parameters, and not decided by an LLM.
Where this module is fed an NSDT vector that Claude estimated from freeform
text (see sap_kairos_ai_reading.py), the classification itself still runs
here, in code, the same way it would for a vector entered directly.
"""

from typing import Dict, List, Optional

from sap_kairos_tumbling_inversion import compute_inversion, compute_arc_direction


def detect_middle_path(nsdt_vector: List[float]) -> Dict:
    """Stage 5 Middle Path Gateway.

    witness_score = (Adaptability * 0.4) + (Coherence * 0.4) - (Tension * 0.2)
    Accessed when witness_score > 50 -- consciousness has stepped outside
    the tumbling axis far enough to observe it rather than just ride it.
    """
    N, S, D, T, C = nsdt_vector
    witness_score = (D * 0.4) + (C * 0.4) - (T * 0.2)
    accessed = witness_score > 50
    return {"middle_path_accessed": accessed, "witness_score": round(witness_score, 1)}


def classify_flow_quality(nsdt_vector: List[float], middle_path_accessed: bool) -> Dict:
    """Stage 6 -- the Conductor's Paradox.

    conductor_score = (Coherence * 0.5) + (Adaptability * 0.3)
                       + (100 - |Tension - 50|) * 0.2
    (the last term rewards Tension sitting near the productive middle,
    not near either extreme -- the Polarity Load principle applied to
    peak performance.)

    Sustainable Flow requires the Middle Path already accessed at Stage 5
    AND conductor_score >= 50 AND not (high physical stability paired with
    low consciousness stability, i.e. the peak that only looks stable).
    Everything else is Brittle Flow.
    """
    N, S, D, T, C = nsdt_vector
    conductor_score = (C * 0.5) + (D * 0.3) + (100 - abs(T - 50)) * 0.2
    inv = compute_inversion(nsdt_vector, 6)

    brittle_signature = inv.physical_stability > 70 and inv.consciousness_stability < 50
    sustainable = middle_path_accessed and conductor_score >= 50 and not brittle_signature

    if sustainable:
        return {
            "flow_type": "sustainable",
            "conductor_score": round(conductor_score, 1),
            "directive": (
                "Sustainable Flow -- the Witness Position remains active beneath the peak "
                "performance. You're harvesting this flow state while staying aware it's "
                "temporary; Stage 7 will arrive as conscious extraction, not crisis."
            ),
            "stage_7_arrival": "invitation",
        }
    return {
        "flow_type": "brittle",
        "conductor_score": round(conductor_score, 1),
        "directive": (
            "Brittle Flow -- there's no meta-awareness beneath this peak; you HAVE BECOME "
            "the flow rather than experiencing it. When Stage 7 arrives, it will arrive as "
            "ambush rather than invitation."
        ),
        "stage_7_arrival": "ambush",
    }


def classify_crucible_mode(
    nsdt_vector: List[float],
    middle_path_accessed: bool,
    nsdt_history: Optional[List[List[float]]] = None,
) -> Dict:
    """Stage 7 -- the Individuation Crucible.

    distillation_score = (Adaptability * 0.4) + (Coherence * 0.4)
                          + (100 - Tension) * 0.2
    Conscious Distillation requires the Middle Path already accessed,
    distillation_score >= 55, and consciousness reading more stable than
    the physical situation (the breakdown is being conducted, not just
    endured). Everything else is Chaotic Collapse.

    Shadow surfacing (the Concealed Self resurfacing for integration) is
    flagged when current Tension > 60 and Coherence has risen versus the
    previous entry in nsdt_history.
    """
    N, S, D, T, C = nsdt_vector
    distillation_score = (D * 0.4) + (C * 0.4) + (100 - T) * 0.2
    inv = compute_inversion(nsdt_vector, 7)

    distillation = (
        middle_path_accessed
        and distillation_score >= 55
        and inv.consciousness_stability > inv.physical_stability
    )

    shadow_surfacing = False
    if nsdt_history and len(nsdt_history) >= 2:
        previous_C = nsdt_history[-2][4]
        shadow_surfacing = T > 60 and C > previous_C

    if distillation:
        result = {
            "crucible_mode": "distillation",
            "distillation_score": round(distillation_score, 1),
            "directive": (
                "Conscious Distillation -- this breakdown burns the costume, not the wearer. "
                "What's being extracted is the accumulated identity structure -- the roles, "
                "the attachments -- not your essential self."
            ),
        }
    else:
        result = {
            "crucible_mode": "collapse",
            "distillation_score": round(distillation_score, 1),
            "directive": (
                "Chaotic Collapse -- without the Witness Position, this feels like fighting "
                "the burn rather than being refined by it. There's no framework yet for "
                "reading the breakdown as directed."
            ),
        }
    result["shadow_surfacing"] = shadow_surfacing
    return result


def classify_crystallization(
    nsdt_vector: List[float],
    middle_path_accessed: bool,
    nsdt_history: Optional[List[List[float]]] = None,
) -> Dict:
    """Stage 8 -- the Crystallization Paradox.

    divergence = |Stability - Tension| (Revealed Self vs. Concealed Self).
    Gratitude engages automatically when divergence < 25, or when the
    Middle Path was accessed, the arc reads ascending, and divergence < 30.
    Dissolution requires gratitude engaged AND divergence < 30; everything
    else is Shattering.
    """
    N, S, D, T, C = nsdt_vector
    divergence = abs(S - T)

    arc = "indeterminate"
    if nsdt_history and len(nsdt_history) >= 2:
        arc, _ = compute_arc_direction(nsdt_history)

    gratitude_engaged = divergence < 25 or (
        middle_path_accessed and arc == "ascending" and divergence < 30
    )
    dissolution = gratitude_engaged and divergence < 30

    if dissolution:
        directive = (
            "Dissolution -- the crystal is returning to solution, not shattering. The "
            "structure reorganizes but what it learned is preserved, the way a dissolved "
            "crystal's information survives in solution."
        )
        trajectory = "dissolution"
    else:
        directive = (
            "Shattering -- this is the Crystallization Paradox at its most dangerous: "
            "maximum structural perfection is also maximum brittleness. The divergence "
            "between what's projected and what's actually being carried is too wide to "
            "hold at once."
        )
        trajectory = "shattering"

    return {
        "trajectory": trajectory,
        "divergence": round(divergence, 1),
        "gratitude_engaged": gratitude_engaged,
        "arc": arc,
        "directive": directive,
    }


def engage_gratitude_mechanism(nsdt_vector: List[float]) -> List[float]:
    """Apply the Stage 8 Gratitude Mechanism: converge Stability and
    Tension toward their average (closing the Revealed/Concealed gap) and
    boost Coherence, capped at 100. Complexity and Adaptability are left
    untouched -- gratitude isn't claimed here to change what happened,
    only how the divergence it created is held."""
    N, S, D, T, C = nsdt_vector
    avg = (S + T) / 2
    new_C = min(100, C + 10)
    return [N, avg, D, avg, new_C]
