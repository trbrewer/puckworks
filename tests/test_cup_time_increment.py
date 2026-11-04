"""Synthetic pre-chemistry verification of the approved analysis contract."""

import numpy as np
import pytest

from puckworks.analysis import cup_time_increment as model


def test_conserving_interpolation_endpoints_constant_and_asymmetric():
    mids = [1, 3, 5]
    for values in ([2, 2, 2], [1, 2, 5]):
        assert model.crossing_solute(4, 2, 2, 4, 0, mids, values) == 0
        assert model.crossing_solute(4, 2, 2, 4, 1, mids, values) == pytest.approx(0.08)
    for u in (0, 0.1, 0.5, 0.9, 1):
        assert model.crossing_solute(4, 2, 2, 4, u, mids, [2, 2, 2]) == pytest.approx(0.08*u)
    assert model.linear_integral(mids, [1, 2, 5], 2, 4) / 2 == pytest.approx(2.25)
    assert model.crossing_solute(4, 2, 2, 4, 0.5, mids, [1, 2, 5]) == pytest.approx(
        0.08 * 1.75 / 4.5)


def test_interpolation_zero_denominator_and_edge_extension():
    assert model.crossing_solute(4, 0, 2, 4, 0.8, [3], [0]) == 0
    with pytest.raises(ValueError, match="nonpositive interpolation denominator"):
        model.crossing_solute(4, 2, 2, 4, 1, [1, 3, 5], [0, 0, 0])
    assert model.linear_integral([3, 5], [2, 4], 0, 8) == pytest.approx(24)


def synthetic_rows():
    rows = []
    cumulative = 0.0
    for i in range(1, 17):
        mass = 0 if i < 3 else 2.0
        # None deliberately tests that structural zeros do not enter interpolation.
        c = None if mass == 0 else float(i)
        rows.append(dict(shot=1, vial=i, mass_g=mass, t_start_s=2*(i-1), t_end_s=2*i,
                         b_start_g=cumulative, b_end_g=cumulative+mass,
                         tds_pct=c, solute_g=0 if mass == 0 else mass*c/100))
        cumulative += mass
    return rows


def test_prefix_mass_clock_and_conservation():
    rows = synthetic_rows()
    for mass in model.ENDPOINTS:
        primary = model.prefix_observation(rows, mass)
        assert primary['duration_s'] == pytest.approx(4 + mass)
        full = int(mass // 2)
        expected = sum(2 * i / 100 for i in range(3, 3 + full))
        expected += (mass - 2*full) * (3 + full) / 100
        assert primary['prefix_solute_g'] == pytest.approx(expected)
        u2 = model.prefix_observation(rows, mass, 'u2')
        root = model.prefix_observation(rows, mass, 'sqrt')
        assert u2['duration_s'] <= primary['duration_s'] <= root['duration_s']
        assert u2['concentration_tds_pp'] == primary['concentration_tds_pp']
    with pytest.raises(ValueError, match='combined'):
        model.prefix_observation(rows, 19.8, 'u2', True)


@pytest.mark.parametrize('sign', [-1, 1])
def test_signed_ols_loso_and_press_against_matrix_oracle(sign):
    t = np.linspace(11, 32, 11)
    x = np.log(t/20)
    y = 8 + sign*3*x + 0.1*np.sin(np.arange(11))
    metrics, folds = model.point_analysis(t, y)
    assert np.sign(metrics['beta']) == sign
    assert metrics['A0_press_max_abs_difference_pp'] < 1e-10
    assert metrics['A1_press_max_abs_difference_pp'] < 1e-10
    design = np.column_stack([np.ones(11), x])
    h = np.diag(design @ np.linalg.inv(design.T @ design) @ design.T)
    for i, fold in enumerate(folds):
        train = np.arange(11) != i
        coeff = np.linalg.lstsq(design[train], y[train], rcond=None)[0]
        assert fold['A1_prediction_pp'] == pytest.approx(design[i] @ coeff, abs=1e-12)
        assert fold['A1_h_ii'] == pytest.approx(h[i], abs=1e-12)
    assert metrics['descriptive_all_df'] == 9


def test_grouped_bootstrap_holds_all_copies_and_is_weighted():
    t, y = np.array([10, 20, 30, 40.]), np.array([5, 7, 4, 2.])
    w = np.array([2, 0, 3, 6])
    metrics, folds = model.loso(t, y, w)
    assert len(folds) == 3
    for f in folds:
        held = f['held_index']
        expanded = np.repeat(np.arange(4), w)
        train = expanded[expanded != held]
        design = np.column_stack([np.ones(len(train)), np.log(t[train]/20)])
        coeff = np.linalg.lstsq(design, y[train], rcond=None)[0]
        expected = coeff @ [1, np.log(t[held]/20)]
        assert f['training_copies'] == 11 - w[held]
        assert f['A1_prediction_pp'] == pytest.approx(expected)
        altered = y.copy()
        altered[held] += 999
        other = next(f for f in model.loso(t, altered, w)[1] if f['held_index'] == held)
        assert other['A1_prediction_pp'] == f['A1_prediction_pp']
        assert other['A0_prediction_pp'] == f['A0_prediction_pp']
    expected = np.sqrt(sum(f['held_copies']*f['A1_error_pp']**2 for f in folds)/11)
    assert metrics['rmse_A1_pp'] == pytest.approx(expected)


def test_degenerate_draws_are_retained_with_defined_denominators():
    t, y = np.array([10, 20, 30.]), np.array([3, 5, 2.])
    two = model.bootstrap_draw(t, y, [5, 6, 0])
    one = model.bootstrap_draw(t, y, [11, 0, 0])
    valid = model.bootstrap_draw(t, y, [3, 4, 4])
    assert two['unfit_slope_folds'] == 2
    assert np.isfinite(two['rmse_A0_pp']) and np.isnan(two['delta_pp'])
    assert np.isfinite(two['beta'])
    assert one['empty_training_folds'] == 1 and one['unfit_slope_folds'] == 1
    assert np.isnan(one['rmse_A0_pp']) and np.isnan(one['beta'])
    report = model.uncertainty_summary({'delta_pp': 0.0}, [one, two, valid],
                                       [{'delta_pp': -1.}, {'delta_pp': 0.}])
    assert report['bootstrap_requested'] == 3
    assert report['delta_pp_boot_defined'] == 1
    assert report['beta_boot_defined'] == 2
    assert report['bootstrap_unfit_slope_draws'] == 2
    assert report['permutation_percentile'] == 75


def test_frozen_streams_and_vocabulary():
    counts, permutations = model.resampling_indices()
    again, again_p = model.resampling_indices()
    assert counts.shape == permutations.shape == (2000, 11)
    assert np.all(counts.sum(axis=1) == 11)
    np.testing.assert_array_equal(counts, again)
    np.testing.assert_array_equal(permutations, again_p)
    np.testing.assert_array_equal(np.sort(permutations, axis=1), np.tile(np.arange(11), (2000, 1)))
    assert tuple(v[1] for v in model.VARIANTS) == (19.8, 19.8, 19.8, 19.8, 9.9, 14.85)
    record = dict(delta_pp=-0.1, delta_pp_boot_low=-0.2, delta_pp_boot_high=0.0,
                  beta_boot_low=1., beta_boot_high=2.)
    assert model.vocabulary(record) == ('reduction', 'prediction difference unresolved', 'resolved')
    record['delta_pp_boot_high'] = -0.001
    assert model.vocabulary(record)[1] == 'resolved held-out error reduction'
    record.update(delta_pp=0.1, delta_pp_boot_low=0.001, delta_pp_boot_high=0.2)
    assert model.vocabulary(record)[1] == 'resolved held-out error increase'
