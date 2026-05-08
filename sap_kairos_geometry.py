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
    8: {"name": "VESSEL OF GROUNDING", "human_name": "False Heaven / False Hell", "arc": "ascending", "polyvagal": "dorsal",
        "trickster": "Br'er Rabbit: 'Surrender is the only escape from the trap.'"},
    9: {"name": "TRANSPARENCY OF THE GUIDE", "human_name": "Dissolution & Renewal", "arc": "ascending", "polyvagal": "ventral",
        "trickster": "Eshu: 'You have become the threshold – now rest.'"},
}

# Reuse centroids from canonical SAP (same 5D coordinates)
STAGE_CENTROIDS = {
    0: [0.0, 0.0, 0.0, 0.0, 0.0],
    1: [1.0, 8.0, 1.0, 1.0, 1.0],
    2: [2.0, 7.0, 2.0, 2.0, 2.0],
    3: [4.0, 7.0, 2.5, 3.0, 4.0],
    4: [3.5, 6.5, 3.0, 3.5, 5.0],
    5: [5.0, 4.0, 5.0, 5.0, 4.5],
    6: [6.0, 5.5, 4.0, 6.0, 6.5],
    7: [6.5, 3.0, 7.0, 7.0, 3.5],
    8: [7.5, 7.0, 8.0, 2.0, 2.0],
    9: [8.0, 2.0, 8.5, 1.5, 1.5],
}

AXIS_WEIGHTS = [1.0, 1.5, 1.5, 1.0, 0.8]
AXIS_SCALES = [10.0, 10.0, 10.0, 10.0, 10.0]

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
