"""
LUMINARK Kairos Bayesian Engine v1.0
Soft, human-agency-aware inference with therapeutic guidance.
Kairos: the opportune moment for change.
"""

import numpy as np
from typing import Dict, List, Optional
from sap_kairos_geometry import KairosGeometry, STAGE_CENTROIDS, AXIS_WEIGHTS, AXIS_SCALES
from sap_energy_layer import SAPEnergy

class KairosBayesian:
    def __init__(self, temperature: float = 0.7, beta: float = 0.6, allow_regression: bool = True):
        self.temperature = temperature
        self.beta = beta
        self.allow_regression = allow_regression
        self.geometry = KairosGeometry(allow_regression=allow_regression)
        self.centroids = {k: np.array(v) for k, v in STAGE_CENTROIDS.items()}
        self.weights = AXIS_WEIGHTS
        self.scales = AXIS_SCALES
        self.previous_stage: Optional[int] = None
        self.path_energy: float = 0.0

    def _weighted_distance(self, x: np.ndarray, centroid: np.ndarray) -> float:
        diff = (x - centroid) / self.scales
        return np.sqrt(np.sum(self.weights * diff * diff))

    def _raw_logits(self, x: np.ndarray) -> np.ndarray:
        distances = [self._weighted_distance(x, self.centroids[s]) for s in range(10)]
        return -np.array(distances)

    def posterior(self, x: np.ndarray) -> np.ndarray:
        logits = self._raw_logits(x)
        logits = SAPEnergy.modulate_logits(logits, x.tolist(), self.beta)

        if self.previous_stage is not None:
            mask = self.geometry.get_adjacency()[self.previous_stage]
            logits = np.where(mask > 0, logits, -np.inf)

        logits = logits / max(self.temperature, 0.05)
        logits = logits - np.max(logits)
        exp = np.exp(logits)
        return exp / np.sum(exp)

    def _get_therapeutic_note(self, stage: int, entropy: float, trap_energy: float) -> str:
        if stage == 8:
            if trap_energy > 0.7:
                return "⚠️ Stage 8 High Trap: False certainty detected. Offer Release Protocol: gratitude, duality, Ma'at, or witness."
            else:
                return "Stage 8 detected. Kairos invitation: 'What would it mean to let go?'"
        if stage == 7 and self.previous_stage == 8:
            return "Regression from Stage 8 → 7 observed. This is a refusal of dissolution. Explore the fear beneath the certainty."
        if stage == 7:
            return "Stage 7: Insight without connection. Consider somatic grounding or reaching out to a trusted other."
        if stage == 5:
            return "Kairos: Bifurcation point. You have full agency to progress or return. No wrong choice – only honest choice."
        if stage == 0 and trap_energy > 0.5:
            return "Stage 0 with high energy: This is not collapse – it is a reset. Rest is productive."
        return "Continue holding space. Trust the process."

    def _get_somatic_invitation(self, stage: int, polyvagal: str) -> str:
        invites = {
            0: "Rest your hand on your heart. Breathe slowly for 1 minute.",
            1: "Notice the first spark of intention in your body. Where do you feel it?",
            2: "Place one hand on your belly, one on your chest. Feel the boundary between inner and outer.",
            3: "Take three deep breaths, exhaling longer than inhaling. Notice any tension.",
            4: "Stand up, stretch your arms wide. Feel the stability of the ground.",
            5: "Place your feet flat. Ask: 'What is mine to do?'",
            6: "Hum or chant a single note. Feel the vibration in your chest.",
            7: "Place a hand on your throat. Softly say: 'I am here. I am not alone.'",
            8: "Breathe into your back body. Imagine a soft space behind your heart.",
            9: "Lie down. Surrender your weight completely to the floor.",
        }
        return invites.get(stage, "Take three conscious breaths.")

    def forward(self, x: np.ndarray) -> Dict:
        posterior = self.posterior(x)
        dominant = int(np.argmax(posterior))
        expected = float(np.sum(np.arange(10) * posterior))
        entropy = -np.sum(posterior * np.log(posterior + 1e-12))
        trap_energy = SAPEnergy.trap_energy(dominant, x.tolist())

        self.path_energy += trap_energy
        self.previous_stage = dominant

        meta = self.geometry.get_metadata(dominant)
        trickster = self.geometry.get_trickster_wisdom(dominant)
        therapeutic_note = self._get_therapeutic_note(dominant, entropy, trap_energy)
        somatic_invitation = self._get_somatic_invitation(dominant, meta.get("polyvagal", "ventral"))

        release_protocol = None
        if dominant == 8:
            release_protocol = {
                "gratitude": "Acknowledge what the rigidity protected you from. Thank the structure.",
                "duality": "Identify the binary thinking driving the trap. Find the paradox.",
                "maat": "Examine your actions against truth, balance, reciprocity.",
                "witness": "Observe the rigidity without judgment. Become the space around it."
            }

        return {
            "posterior": posterior.tolist(),
            "dominant_stage": dominant,
            "stage_name": meta.get("human_name", meta.get("name", "")),
            "arc": meta.get("arc", ""),
            "polyvagal": meta.get("polyvagal", "unknown"),
            "expected_stage": round(expected, 4),
            "entropy": round(entropy, 4),
            "trap_energy": round(trap_energy, 4),
            "cumulative_path_energy": round(self.path_energy, 4),
            "therapeutic_note": therapeutic_note,
            "somatic_invitation": somatic_invitation,
            "trickster_wisdom": trickster,
            "release_protocol": release_protocol,
            "mode": "kairos",
            "regression_allowed": self.allow_regression,
        }

    def reset(self):
        self.previous_stage = None
        self.path_energy = 0.0
