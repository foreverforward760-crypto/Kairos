"""
Kairos Tumbling Inversion Engine

The generative mechanism of the SAP cycle, ported from the canonical
Tumbling Inversion Principle (Stanfield's Axiom of Perceived Perpetuity,
"The Framework" v25 Part VII / TUMBLING_INVERSION_v8.2.md).

Core insight:
  Even stages (2, 4, 6, 8): Physically Stable / Consciously Unstable
  Odd stages  (1, 3, 5, 7, 9): Physically Unstable / Consciously Stable

The inversion is not a flaw -- it is the mechanism of forward motion.
Picture a cylinder rolling down a slope, alternating between resting on a
stable face and tumbling over its edge into the next. Neither state (the
resting face, the tumble) can be held indefinitely, so the cycle keeps
moving. This module computes that state from an NSDT vector, rather than
just describing it.

NSDT vector indices (see docs/NSDT_REFERENCE.md):
  [0] N  Complexity
  [1] S  Stability
  [2] D  Adaptability
  [3] T  Tension
  [4] C  Coherence
"""

from dataclasses import dataclass
from typing import List, Tuple
import math


@dataclass
class InversionState:
    """State of the tumbling inversion for a given NSDT vector."""
    stage: int
    parity: str                     # 'even', 'odd', 'boundary'
    physical_stability: float       # 0-100, high = stable
    consciousness_stability: float  # 0-100, high = stable
    divergence: float               # 0-100, |Revealed Self - Concealed Self|
    geometric_form: str
    message: str


def compute_inversion(nsdt_vector: List[float], stage: int) -> InversionState:
    """Compute the inversion state from an NSDT vector and its stage.

    Physical stability reads mostly from Stability, tempered by Tension
    (high tension erodes physical stability). Consciousness stability
    reads from Adaptability and Coherence -- the capacity to meet and
    integrate what's happening, not just endure it.

    Divergence is the gap between the Revealed Self (the stability a
    system projects) and the Concealed Self (the tension it's actually
    carrying) -- the same gap the Stage 8 Gratitude Mechanism exists to
    close.
    """
    N, S, D, T, C = nsdt_vector

    physical = (S * 0.7) + (100 - T) * 0.3
    conscious = (D * 0.5) + (C * 0.5)

    revealed = S
    concealed = T
    divergence = abs(revealed - concealed)

    if stage == 0 or stage == 9:
        parity = "boundary"
        geometric = "Circle" if stage == 0 else "Nonagon → Circle"
    elif stage % 2 == 0:
        parity = "even"
        geometric = {2: "Line/Spindle", 4: "Square/Foundation", 6: "Hexagon", 8: "Octagon"}.get(stage, "Polygon")
    else:
        parity = "odd"
        geometric = {1: "Point/Spark", 3: "Triangle", 5: "Perpendicular Axis", 7: "Heptagon", 9: "Nonagon"}.get(stage, "Polygon")

    if parity == "even":
        msg = (f"Even stage {stage} -- Physically Stable / Consciously Unstable. "
               f"Physical stability = {physical:.1f}, consciousness stability = {conscious:.1f}.")
    elif parity == "odd":
        msg = (f"Odd stage {stage} -- Physically Unstable / Consciously Stable. "
               f"Physical stability = {physical:.1f}, consciousness stability = {conscious:.1f}.")
    else:
        msg = f"Boundary stage {stage} -- dissolution or primordial potential."

    return InversionState(
        stage=stage,
        parity=parity,
        physical_stability=round(physical, 1),
        consciousness_stability=round(conscious, 1),
        divergence=round(divergence, 1),
        geometric_form=geometric,
        message=msg,
    )


def compute_arc_direction(history: List[List[float]]) -> Tuple[str, float]:
    """Determine ascending vs. descending arc from NSDT history (recent
    vectors, oldest first).

    Descending: Stability rising while Adaptability falls -- structure is
    hardening faster than the capacity to meet it is growing.
    Ascending: Tension rising alongside recovering Coherence -- friction
    that's being integrated rather than avoided.
    """
    if len(history) < 2:
        return ("indeterminate", 0.0)

    deltas = []
    for i in range(1, len(history)):
        prev = history[i - 1]
        curr = history[i]
        deltas.append([curr[j] - prev[j] for j in range(5)])

    avg_delta_S = sum(d[1] for d in deltas) / len(deltas)
    avg_delta_D = sum(d[2] for d in deltas) / len(deltas)
    avg_delta_T = sum(d[3] for d in deltas) / len(deltas)
    avg_delta_C = sum(d[4] for d in deltas) / len(deltas)

    descending_score = avg_delta_S - avg_delta_D
    ascending_score = avg_delta_T + avg_delta_C

    if descending_score > 5 and ascending_score < -2:
        arc = "descending"
        confidence = min(100, descending_score * 5)
    elif ascending_score > 5 and descending_score < -2:
        arc = "ascending"
        confidence = min(100, ascending_score * 5)
    else:
        arc = "plateau"
        confidence = 50.0

    return (arc, round(confidence, 1))


def divergence_category(divergence: float) -> str:
    """Categorize divergence between the Revealed Self and Concealed Self."""
    if divergence < 15:
        return "converged (aligned)"
    elif divergence < 35:
        return "moderate"
    else:
        return "diverged (high misalignment)"
