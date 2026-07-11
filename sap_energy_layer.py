"""
Energy Layer v6.5 - Trap potentials as a true energy field.
Reused from industrial engine.

LEGACY AXIS WARNING: trap_energy() below unpacks the NSDT vector as
`c, s, t, a, coh` (Connection, Stability, Tension, Agency, Coherence) --
this predates the confirmed N/S/D/T/C axes (Complexity, Stability,
Adaptability, Tension, Coherence; see docs/NSDT_REFERENCE.md and
sap_kairos_tumbling_inversion.py) and conflicts with them on 3 of 5
positions (index 0, 2, 3). Unlike sap_kairos_geometry.py's
STAGE_CENTROIDS, this function's specific coefficients (2.0*coh - 1.5*a +
1.2*s, etc.) have no formula in the Tumbling Inversion source material to
re-derive them from -- they were hand-tuned once, under the old guess, and
there's nothing to mechanically reconcile them against. Re-guessing the
coefficients a second time would trade one unverified guess for another,
so this file is left as-is and marked legacy instead.

For Stage 6/7/8, prefer the real `stage_paradox` field
(sap_kairos_stage_paradox.py -- Conductor's Paradox, Individuation
Crucible, Crystallization Paradox) over trap_energy()'s output; it's kept
only for the backward-compatible `trap_score_amplifier` API field.
"""

import numpy as np
from typing import List

class SAPEnergy:
    @staticmethod
    def trap_energy(stage: int, x: List[float]) -> float:
        # LEGACY axis unpacking -- see module docstring above.
        c, s, t, a, coh = x
        if stage == 8:
            return max(0.0, min(1.0, (2.0 * coh - 1.5 * a + 1.2 * s) / 5.0))
        if stage == 7:
            return max(0.0, min(1.0, (1.5 * t - 1.0 * a) / 5.0))
        if stage == 5:
            return max(0.0, min(1.0, (4.0 - a) * (1.0 - (c + coh) / 2.0) / 4.0))
        if stage == 3:
            return max(0.0, min(1.0, (a - 7.0) * (4.0 - coh) / 30.0))
        return 0.0

    @staticmethod
    def compute_total_energy(x: List[float], posterior: np.ndarray) -> float:
        total = 0.0
        for stage, p in enumerate(posterior):
            total += p * SAPEnergy.trap_energy(stage, x)
        return total

    @staticmethod
    def compute_gradient(x: List[float], posterior: np.ndarray, epsilon: float = 1e-5) -> List[float]:
        grad = []
        for i in range(5):
            x_plus = x.copy()
            x_plus[i] += epsilon
            e_plus = SAPEnergy.compute_total_energy(x_plus, posterior)
            x_minus = x.copy()
            x_minus[i] -= epsilon
            e_minus = SAPEnergy.compute_total_energy(x_minus, posterior)
            grad.append((e_plus - e_minus) / (2 * epsilon))
        return grad

    @staticmethod
    def modulate_logits(logits: np.ndarray, x: List[float], beta: float = 0.8) -> np.ndarray:
        energies = np.array([SAPEnergy.trap_energy(s, x) for s in range(10)])
        return logits - beta * energies
