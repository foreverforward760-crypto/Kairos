"""
Kairos Stage Disruption Loops

A condensed, consumer-facing version of the "Seven Deadly Sins as Frequency
Disruptions" section of the SAPP Applied Architecture document. The
original source reframes the seven classical vices as self-perpetuating
stage-disruption loops rather than moral failings -- each one generates a
feedback loop that produces its own conditions for continuing, and each
has a named "ascending antidote" that breaks the loop rather than
suppressing the impulse.

This module keeps that reframing (structural loop, not moral failing) and
drops the theological/cultural-history framing that the original document
carries -- names only, loop mechanism, and antidote.

Not auto-detected from a single reading. Surfaced when the session's own
repeat-pattern detection (see KairosSession.detect_cynical_loop, an 8<->7
oscillation) fires, since that's the one loop pattern this project already
detects with any confidence from stage history alone.
"""

from typing import Dict, List

DISRUPTION_LOOPS: List[Dict[str, str]] = [
    {
        "name": "Pride",
        "loop_stage": "Stage 8 -- First Solidification",
        "mechanism": (
            "The self constructs itself as fixed and uniquely significant. Any challenge to "
            "that self reads as threat, which produces more rigidity, which makes the self "
            "harder to examine -- and each recognized limitation gets reframed as more proof "
            "of uniqueness."
        ),
        "antidote": "Humility -- not self-diminishment, accurate self-assessment held without defensiveness.",
    },
    {
        "name": "Greed",
        "loop_stage": "Stage 6 Material Density + Stage 8",
        "mechanism": (
            "The self identifies with what it has. Each acquisition delivers a brief Stage 6 "
            "satisfaction that reverts to baseline lack, and the lack reads as evidence more is "
            "needed. 'Enough' stays structurally unavailable while the self is identified with "
            "having rather than being."
        ),
        "antidote": "Generosity -- loosening identification with accumulation; each real act of giving re-establishes that the self is prior to what it holds.",
    },
    {
        "name": "Lust",
        "loop_stage": "Stage 2 Polarity Short-Circuit + Stage 5 Filter Collapse",
        "mechanism": (
            "Simulated encounter delivers the charge of genuine polarity without its substance, "
            "so the Stage 5 filter that selects for real resonance atrophies from disuse, which "
            "degrades the capacity for the real encounter further."
        ),
        "antidote": "Genuine encounter -- real stakes, real vulnerability, real consequence; the willingness to hold the threshold instead of collapsing it immediately.",
    },
    {
        "name": "Envy",
        "loop_stage": "Stage 4 Comparison Overload -- Ground Erosion",
        "mechanism": (
            "The stable ground of Stage 4 gets replaced with a constantly shifting comparison to "
            "others. Since there's always someone with more, the lack becomes structurally "
            "permanent: comparison, dissatisfaction, more comparison."
        ),
        "antidote": "Gratitude -- returning the self's reference point to its own position instead of its position relative to others.",
    },
    {
        "name": "Gluttony",
        "loop_stage": "Stage 6 Sensory Overload -- Prism Numbing",
        "mechanism": (
            "Overconsumption dulls the discrimination Stage 7 distillation needs. Each cycle of "
            "excess requires more stimulation for the same charge, dulling sensitivity further "
            "until there's nothing distinct left to distill from."
        ),
        "antidote": "Temperance -- not abstinence, calibration: choosing experience at the intensity where discrimination is still possible.",
    },
    {
        "name": "Wrath",
        "loop_stage": "Stage 6 High-Amplitude Polarity -- Fake Stage 7",
        "mechanism": (
            "Anger at maximum amplitude feels like clarity because of its intensity, not because "
            "it is clarity. Each cycle produces a felt sense of moral insight that justifies the "
            "next cycle as necessary truth-telling rather than disruption."
        ),
        "antidote": "Patience -- holding the threshold before acting, to tell a genuine moral response apart from a frequency disruption wearing its clothes.",
    },
    {
        "name": "Sloth",
        "loop_stage": "Stage 7 Avoidance + Stage 8 Inertia",
        "mechanism": (
            "The refusal of the inward work Stage 7 distillation requires, in favor of "
            "comfortable Stage 6 stimulation. Each avoidance reinforces the belief that the "
            "current state is permanent and no other state is available."
        ),
        "antidote": "Diligence -- applied inward: sitting with genuine complexity long enough for something to distill.",
    },
]

DISRUPTION_LOOPS_BY_NAME: Dict[str, Dict[str, str]] = {d["name"]: d for d in DISRUPTION_LOOPS}


def loop_for_cynical_pattern() -> Dict[str, str]:
    """The loop most directly matched to this project's existing 8<->7
    'cynical loop' detector (KairosSession.detect_cynical_loop): repeated
    oscillation between Vessel of Grounding and Lens of Distillation reads,
    structurally, as Wrath's loop -- a fake Stage 7 clarity that keeps
    re-justifying a return to Stage 8 certainty."""
    return DISRUPTION_LOOPS_BY_NAME["Wrath"]
