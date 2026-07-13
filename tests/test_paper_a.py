"""Fast structural guards for Paper A observable contracts (review AR-06/MAJ-08).

These do NOT run PDE solves (the slow analyses stay out of CI); they pin the
matched-endpoint contract so a whole-cup path cannot silently revert to a fixed
integration time when the manuscript claims a fixed beverage mass.
"""
import inspect

from puckworks.validation.slow import angeloni_bracket as ab


def test_matched_bounds_is_mass_consistent():
    """t_end = 40 mL / flow, integrated from 0 (review B1/MAJ-08/MAJ-09)."""
    assert ab._V_TARGET_ML == 40.0
    lo, hi = ab._matched_bounds(2.0)
    assert lo == 0.0 and abs(hi - 20.0) < 1e-9        # 40 mL / 2 mL/s = 20 s
    lo, hi = ab._matched_bounds(1.6)
    assert abs(hi - 25.0) < 1e-9                        # 40 / 1.6 = 25 s


def test_species_bracket_has_no_fixed_time_param():
    """The pooled species bracket must not expose a fixed t_shot_s knob -- it now
    integrates to the matched 40 mL endpoint (review MAJ-08)."""
    params = inspect.signature(ab.gate_pannusch_angeloni_species_bracket).parameters
    assert "t_shot_s" not in params
    src = inspect.getsource(ab.gate_pannusch_angeloni_species_bracket)
    assert "_matched_bounds" in src                    # uses the matched endpoint
    assert "[0.0, t_shot_s]" not in src                # not the old fixed-time bounds
