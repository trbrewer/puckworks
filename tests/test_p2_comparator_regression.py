"""F14: the named comparator must be the one the predicate actually evaluates."""
from puckworks import harness


def test_ladder_distinguishes_constant_and_flexible_comparators():
    result = harness.kappa_t_ladder()
    # The actual 9-bar trace separates the two decisions, so a constant/cubic
    # mix-up cannot hide behind two true predicates or an implementation mock.
    assert result['rung4_phi_of_t'] < result['rung1_const_kappa']
    assert result['flexible_cubic_null'] < result['rung4_phi_of_t']
    assert result['rung4_beats_flexible_benchmark'] is False
    assert result['rung4_beats_best_constant'] is True


def test_early_maximum_does_not_identify_the_release_mechanism():
    import numpy as np
    # A finite-rate, positive, conserving reservoir dM/dt=-kM releases
    # M(0)*(1-exp(-k*dt)) in the first bin and less in each equal later bin.
    # Its early/peak ratio is exactly one at every finite positive k tested.
    boundaries = np.arange(0., 61., 5.)
    for rate in (0.01, 0.1, 1.):
        fraction_release = -np.diff(np.exp(-rate * boundaries))
        assert fraction_release[0] / max(fraction_release) == 1.
        assert np.isclose(sum(fraction_release), 1-np.exp(-rate*boundaries[-1]))
    assert harness.dissolution_speed_test()['favors'] == 'not identified by early-to-peak ratio'
