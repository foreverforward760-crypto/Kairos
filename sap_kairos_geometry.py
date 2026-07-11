"""
LUMINARK Kairos Geometry Engine v1.0
Designed for human behaviour, therapy, and experimental contexts.
Regression, oscillation, and voluntary return are allowed and meaningful.
Kairos: the opportune moment for change.
"""

import numpy as np
from typing import Dict, List, Tuple, Optional

STAGE_METADATA_KAIROS = {
    0: {"name": "PLENARA", "human_name": "Open Field", "arc": "neutral", "polyvagal": "ventral",
        "trickster": "Coyote: 'The pause is not empty – it is full of potential.'"},
    1: {"name": "SPARK OF NAVIGATION", "human_name": "Awakening", "arc": "descending", "polyvagal": "sympathetic",
        "trickster": "Anansi: 'The first impulse is fragile – protect it.'"},
    2: {"name": "FORGE OF POLARITY", "human_name": "Forming Identity", "arc": "descending", "polyvagal": "dorsal",
        "trickster": "Loki: 'Boundaries create tension – that tension is creative.'"},
    3: {"name": "ENGINE OF EXPRESSION", "human_name": "Discipline & Control", "arc": "descending", "polyvagal": "sympathetic",
        "trickster": "Br'er Rabbit: 'Your discipline may be hiding unprocessed pain.'"},
    4: {"name": "CRUCIBLE OF EQUILIBRIUM", "human_name": "Testing Ground", "arc": "descending", "polyvagal": "dorsal",
        "trickster": "Eshu: 'Stability is a pause, not a destination.'"},
    5: {"name": "DYNAMO OF WILL", "human_name": "Choice Point", "arc": "bifurcation", "polyvagal": "ventral",
        "trickster": "Coyote: 'Every choice opens and closes worlds – you have agency.'"},
    6: {"name": "NEXUS OF HARMONY", "human_name": "Integration", "arc": "ascending", "polyvagal": "ventral",
        "trickster": "Anansi: 'Weaving the threads of healing takes time – be patient.'"},
    7: {"name": "LENS OF DISTILLATION", "human_name": "Insight & Isolation", "arc": "ascending", "polyvagal": "sympathetic",
        "trickster": "Loki: 'Isolation can become a trap – reach out.'"},
    8: {"name": "VESSEL OF GROUNDING", "human_name": "The Permanence Trap", "arc": "ascending", "polyvagal": "dorsal",
        "trickster": "Br'er Rabbit: 'Surrender is the only escape from the trap.'"},
    9: {"name": "TRANSPARENCY OF THE GUIDE", "human_name": "Dissolution & Renewal", "arc": "ascending", "polyvagal": "ventral",
        "trickster": "Eshu: 'You have become the threshold – now rest.'"},
}

# STAGE_CENTROIDS -- reconciled against the confirmed N/S/D/T/C axes
# (Complexity, Stability, Adaptability, Tension, Coherence -- see
# docs/NSDT_REFERENCE.md and sap_kairos_tumbling_inversion.py).
#
# These were previously hand-picked under a DIFFERENT, now-superseded axis
# guess (c/s/t/a/coh -- Connection/Stability/Tension/Agency/Coherence, from
# sap_energy_layer.py), which conflicted with the confirmed axes on 3 of 5
# positions. No canonical centroid table exists anywhere in the SAPP source
# material (confirmed by reading SAPP_Framework_v25_FINAL.html), so there
# was never a "correct" table to restore -- this is a from-scratch rebuild,
# done deliberately rather than guessed a second time:
#
#   - S (Stability) and C (Coherence) are SOLVED from the confirmed
#     compute_inversion() formulas (sap_kairos_tumbling_inversion.py) so
#     that each stage's known parity (even = Physically Stable / Consciously
#     Unstable, odd = the inverse) is produced by construction, not by
#     coincidence -- verified by round-tripping every centroid back through
#     compute_inversion() (see the derivation script noted below).
#   - T (Tension) and D (Adaptability) are seeded from each stage's existing
#     `polyvagal` field above (ventral/sympathetic/dorsal) -- an
#     already-present, code-grounded signal, not a fresh invention.
#   - N (Complexity) has no formula pull anywhere in compute_inversion() --
#     it's unpacked there but never used -- so it's an explicit, disclosed,
#     standalone curve (rises through the structure-building stages, peaks
#     at Integration/Insight, eases at Crystallization, falls back toward
#     Stage 0's simplicity by Stage 9), not derived from anything.
#
# Net effect: axis directionality (which of physical/consciousness stability
# is higher) is now formula-guaranteed correct for every stage. The specific
# depth of each value is still an engineering judgment call, same as before
# -- it's reconciled with the confirmed framework, not independently
# validated against real client data.
STAGE_CENTROIDS = {
    0: [0.0, 3.93, 8.0, 2.5, 2.0],
    1: [1.5, 4.43, 5.5, 7.0, 7.5],
    2: [3.0, 7.79, 2.0, 6.5, 6.0],
    3: [4.0, 4.14, 5.5, 7.0, 8.1],
    4: [4.5, 8.21, 2.0, 6.5, 6.4],
    5: [5.5, 1.79, 8.0, 2.5, 6.4],
    6: [7.0, 7.5, 8.0, 2.5, 1.0],
    7: [7.5, 3.29, 5.5, 7.0, 9.5],
    8: [6.0, 9.93, 2.0, 6.5, 5.6],
    9: [3.0, 3.93, 8.0, 2.5, 4.0],
}

AXIS_WEIGHTS = [1.0, 1.5, 1.5, 1.0, 0.8]  # positional tuning, carried over unchanged --
# still weights Stability (index 1) and Adaptability (index 2, formerly the
# old "Tension" guess) most heavily in nearest-centroid distance; no
# axis-identity-specific assumption baked into the weights themselves.
AXIS_SCALES = [10.0, 10.0, 10.0, 10.0, 10.0]

# --- Stage 8 Dual-Chamber Trap (README: "Constitutional Constraints") ---
# TrapScore amplifier applied to Stage 8 readings. Constitutional constant,
# not derived -- see README.md.
STAGE8_TRAP_SCORE_AMPLIFIER = 1.45

STAGE8_CHAMBER_ARRIVAL = "Illusion of Arrival"
STAGE8_CHAMBER_PERMANENCE = "Illusion of Permanence"


def classify_stage8_chamber(x: List[float]) -> str:
    """LEGACY, first-pass heuristic Stage 8 chamber classifier -- prefer the
    real `stage_paradox` field (Crystallization Paradox / Gratitude
    Mechanism, sap_kairos_stage_paradox.classify_crystallization()) for any
    Stage 8 reading; this function predates that and is kept only for the
    backward-compatible `chamber` API field.

    README defines two Stage 8 chambers: Chamber A "Illusion of Arrival"
    (high-frequency trap -- a permanent blissful/righteous state believed
    achieved) and Chamber B "Illusion of Permanence" (low-frequency trap --
    a state of suffering/stagnation believed inescapable).

    This was never a validated clinical instrument, and its one signal is
    now doubly unconfirmed: it reads NSDT axis 0 as a valence proxy
    (>= 5.0 -> Chamber A, below -> Chamber B), but axis 0 is now confirmed
    to be Complexity (see docs/NSDT_REFERENCE.md), which has no obvious
    relationship to "valence" at all -- the original guess was built
    against a different, superseded axis (Connection). Nothing here was
    changed, because there's no confirmed axis to swap in that means
    "valence" either. Treat `chamber` as a legacy label, not a finding.
    """
    valence_proxy = x[0]
    return STAGE8_CHAMBER_ARRIVAL if valence_proxy >= 5.0 else STAGE8_CHAMBER_PERMANENCE


class KairosGeometry:
    def __init__(self, allow_regression: bool = True):
        self.allow_regression = allow_regression

    def get_adjacency(self) -> np.ndarray:
        A = np.eye(10)
        for i in range(10):
            if i > 0:
                A[i, i-1] = 1.0
            if i < 9:
                A[i, i+1] = 1.0
        if not self.allow_regression:
            A[8, 7] = 0.0
        # Stage 5 is a free choice point (kairos moment)
        A[5, :] = 1.0
        return A

    def is_transition_allowed(self, prev: Optional[int], new: int) -> Tuple[bool, str]:
        if prev is None:
            return True, "initial"
        A = self.get_adjacency()
        if A[prev, new] > 0:
            if prev == 8 and new == 7:
                return True, "kairos: regression from Stage 8 → 7 (refusal of dissolution)"
            if prev == 5 and new < 5:
                return True, "kairos: voluntary regression at choice point"
            return True, f"allowed transition {prev} → {new}"
        return False, f"forbidden transition {prev} → {new}"

    def get_metadata(self, stage: int) -> dict:
        return STAGE_METADATA_KAIROS.get(stage, {})

    def get_trickster_wisdom(self, stage: int) -> str:
        return self.get_metadata(stage).get("trickster", "The journey continues.")
