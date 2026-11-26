import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import math

from sap_kairos_tumbling_inversion import (
    compute_inversion,
    compute_arc_direction,
    divergence_category,
)


def test_even_stage_formula_and_parity():
    state = compute_inversion([5, 80, 40, 20, 60], 2)
    assert state.parity == "even"
    assert state.physical_stability == 80.0
    assert state.consciousness_stability == 50.0
    assert state.divergence == 60
    assert state.geometric_form == "Line/Spindle"


def test_odd_stage_parity():
    state = compute_inversion([5, 40, 80, 20, 80], 3)
    assert state.parity == "odd"


def test_zero_and_nine_are_boundary_stages():
    assert compute_inversion([1, 50, 50, 50, 50], 0).parity == "boundary"
    assert compute_inversion([1, 50, 50, 50, 50], 9).parity == "boundary"


def test_arc_direction_requires_history():
    assert compute_arc_direction([]) == ("indeterminate", 0.0)
    assert compute_arc_direction([[1, 2, 3, 4, 5]]) == ("indeterminate", 0.0)


def test_descending_arc():
    history = [[1, 50, 50, 50, 50], [1, 60, 40, 40, 40]]
    arc, confidence = compute_arc_direction(history)
    assert arc == "descending"
    assert confidence > 0


def test_ascending_arc():
    history = [[1, 60, 40, 40, 40], [1, 50, 50, 50, 50]]
    arc, confidence = compute_arc_direction(history)
    assert arc == "ascending"
    assert confidence > 0


def test_divergence_categories():
    assert divergence_category(14.9) == "converged (aligned)"
    assert divergence_category(15) == "moderate"
    assert divergence_category(35) == "diverged (high misalignment)"
