"""Saved-artifact QA: independent weighted normal equations, no original reads."""

import csv
import hashlib
import json
from pathlib import Path

import numpy as np
import pytest


DOC = Path(__file__).resolve().parents[1] / 'docs/analysis/pw_cup_time_increment_001'
SHOTS = (1, 2, 3, 4, 5, 7, 8, 9, 10, 11, 12)


def rows(name):
    with (DOC / name).open() as stream:
        return list(csv.DictReader(line for line in stream if not line.startswith('#')))


def vectorized_normal_equations(x, y, weights):
    """Independent all-copy deletion oracle, unlike the explicit-fold fitter."""
    w = weights
    n = w.sum(axis=1)
    sx, sy = (w*x).sum(axis=1), (w*y).sum(axis=1)
    sxx, sxy = (w*x*x).sum(axis=1), (w*x*y).sum(axis=1)
    beta = (n*sxy-sx*sy)/(n*sxx-sx*sx)
    held_n = n[:, None]-w
    held_x, held_y = sx[:, None]-w*x, sy[:, None]-w*y
    held_xx, held_xy = sxx[:, None]-w*x*x, sxy[:, None]-w*x*y
    fold_beta = (held_n*held_xy-held_x*held_y)/(held_n*held_xx-held_x*held_x)
    e0 = y-held_y/held_n
    e1 = y-((held_y-fold_beta*held_x)/held_n+fold_beta*x)
    r0 = np.sqrt((w*e0**2).sum(axis=1)/n)
    r1 = np.sqrt((w*e1**2).sum(axis=1)/n)
    return r0, r1, r1-r0, beta


def test_saved_identity_timing_and_rights():
    execution = json.loads((DOC/'EXECUTION.json').read_text())
    for name, expected in execution['output_sha256'].items():
        assert hashlib.sha256((DOC/name).read_bytes()).hexdigest() == expected
    assert execution['primary_shots'] == list(SHOTS)
    assert execution['frozen_endpoints_g'] == [19.8, 9.9, 14.85]
    assert hashlib.sha256((DOC/'QA.json').read_bytes()).hexdigest() == execution['pre_chemistry_qa_sha256']
    checks = rows('timing_reconciliation.csv')
    assert {(int(r['shot']), float(r['mass_g'])) for r in checks} == {
        (shot, mass) for shot in SHOTS for mass in (19.8, 9.9, 14.85)}
    assert max(abs(float(r['difference_s'])) for r in checks) <= 1e-10
    for path in DOC.glob('*.csv'):
        text = path.read_text()
        assert '# author: Dr. Yoana Grudeva' in text
        assert '# rights: PERMISSION_DOCUMENTED; no SPDX licence; not relicensed under MIT' in text
        assert '567ad8f3808eb74fbe3e470eaa333161bf2eac1c' in text
        assert 'docs/permissions/grudeva2025.md' in text


def test_plot_metadata():
    Image = pytest.importorskip('PIL.Image')
    for path in DOC.glob('*.png'):
        with Image.open(path) as img:
            assert img.info['author'] == 'Dr. Yoana Grudeva'
            assert img.info['upstream_commit'] == '567ad8f3808eb74fbe3e470eaa333161bf2eac1c'
            assert 'docs/permissions/grudeva2025.md' in img.info['permissions']


def test_all_saved_draws_against_independent_grouped_oracle():
    observations, summaries = rows('observations.csv'), rows('summaries.csv')
    boots, perms = rows('bootstrap_draws.csv'), rows('permutation_draws.csv')
    folds = rows('folds.csv')
    assert len(observations) == len(folds) == 66
    assert len(boots) == len(perms) == 12000
    original_counts = original_permutations = None
    for summary in summaries:
        name = summary['variant']
        obs = [r for r in observations if r['variant'] == name]
        assert tuple(int(r['shot']) for r in obs) == SHOTS
        assert {float(r['mass_g']) for r in obs} == {float(summary['mass_g'])}
        t = np.array([float(r['duration_s']) for r in obs])
        x = np.log(t/20)
        y = np.array([float(r['concentration_tds_pp']) for r in obs])
        boot = [r for r in boots if r['variant'] == name]
        perm = [r for r in perms if r['variant'] == name]
        assert [int(r['draw']) for r in boot] == list(range(1, 2001))
        assert [int(r['draw']) for r in perm] == list(range(1, 2001))
        w = np.array([[int(v) for v in r['multiplicities_in_PRIMARY_SHOTS_order'].split(';')]
                      for r in boot])
        p = np.array([[SHOTS.index(int(v)) for v in r['duration_source_shots'].split(';')]
                      for r in perm])
        assert np.all(w.sum(axis=1) == 11)
        np.testing.assert_array_equal(np.sort(p, axis=1), np.tile(np.arange(11), (2000, 1)))
        if original_counts is None:
            original_counts, original_permutations = w, p
        else:
            np.testing.assert_array_equal(w, original_counts)
            np.testing.assert_array_equal(p, original_permutations)
        oracle = vectorized_normal_equations(x, y, w)
        for key, values in zip(('rmse_A0_pp', 'rmse_A1_pp', 'delta_pp', 'beta'), oracle):
            saved = np.array([float(r[key]) for r in boot])
            np.testing.assert_allclose(saved, values, rtol=0, atol=1e-10)
            interval = np.quantile(saved, [0.025, 0.975], method='linear')
            np.testing.assert_allclose(interval, [float(summary[key+'_boot_low']),
                                                  float(summary[key+'_boot_high'])], rtol=0, atol=1e-12)
            assert int(summary[key+'_boot_defined']) == 2000
            assert int(summary[key+'_boot_undefined']) == 0
        implied = np.array([float(r['implied_change_pp']) for r in boot])
        np.testing.assert_allclose(implied, oracle[3]*np.log(t.max()/t.min()), rtol=0, atol=1e-10)
        permutation_oracle = vectorized_normal_equations(x[p], y, np.ones((2000, 11)))
        for key, values in zip(('rmse_A0_pp', 'rmse_A1_pp', 'delta_pp'), permutation_oracle):
            np.testing.assert_allclose([float(r[key]) for r in perm], values, rtol=0, atol=1e-10)
        deltas = np.array([float(r['delta_pp']) for r in perm])
        point_delta = float(summary['delta_pp'])
        percentile = 100*(np.sum(deltas < point_delta)+0.5*np.sum(deltas == point_delta))/2000
        assert float(summary['permutation_percentile']) == percentile
        assert sum(int(r['unfit_slope_folds']) > 0 for r in boot) == int(summary['bootstrap_unfit_slope_draws'])
        assert sum(int(r['unfit_slope_folds']) for r in boot) == int(summary['bootstrap_unfit_slope_folds'])
        point_folds = [r for r in folds if r['variant'] == name]
        for arm in ('A0', 'A1'):
            errors = np.array([float(r[arm+'_error_pp']) for r in point_folds])
            predicted = np.array([float(r[arm+'_alpha']) + float(r[arm+'_beta'])*x[i]
                                  for i, r in enumerate(point_folds)])
            np.testing.assert_allclose(y-predicted, errors, rtol=0, atol=1e-12)
            assert abs(np.sqrt(np.mean(errors**2))-float(summary['rmse_'+arm+'_pp'])) < 1e-12
            np.testing.assert_allclose(errors, [float(r[arm+'_press_error_pp']) for r in point_folds],
                                       rtol=0, atol=1e-10)
        assert int(summary['shots_A1_better']) == sum(
            float(r['paired_squared_error_difference_pp2']) < 0 for r in point_folds)
