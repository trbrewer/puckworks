"""Numerical/contract verification only; no new scientific acceptance bands."""
import numpy as np
import pytest

from puckworks.analysis import cor15_shape_001 as c


def test_form_a_units_and_independent_amplitudes():
    p = np.array([.5, 1, 2, 3, 4.5])*100000
    expected = c.PD_BAR*(1-np.exp(-(p/100000/c.PD_BAR)**c.N))*np.exp(-p/100000/c.PSTAR_BAR)
    np.testing.assert_allclose(c.fa_shape(p), expected, rtol=1e-14)
    for amplitude in (1e-7, 3e-6):
        r = c.fit(p, amplitude*expected, 'FA')
        assert r['amplitude'] == pytest.approx(amplitude, rel=1e-12)
        np.testing.assert_allclose(c.predict(p, r), amplitude*expected, rtol=1e-12)


@pytest.mark.parametrize('p0', [-150000, 0, 70000, 180000])
def test_threshold_recovers_affine_and_active_sets(p0):
    p = np.array([.5, 1, 1.5, 2, 3, 4.5])*100000
    q = 2e-11*np.maximum(p-p0, 0)
    r = c.fit_threshold(p, q)
    assert r['P0_Pa'] == pytest.approx(p0, abs=1e-8)
    np.testing.assert_allclose(r['pred'], q, atol=1e-19)


def test_power_q_objective_not_log_objective_and_reference_is_matched():
    p = np.array([.4, .8, 1.5, 2.5, 4.4])*100000
    r = c.fit(p, 2e-6*(p/100000)**1.6, 'L2')
    assert r['m'] == pytest.approx(1.6, abs=1e-7)
    assert r['amplitude'] == pytest.approx(2e-6, rel=1e-7)
    shape = c.fa_shape(p)
    rf = c.fit(p, shape, 'L2')
    grid = np.linspace(0, 4, 4001)
    losses = [c.amplitude_fit(shape, (p/100000)**m)[2] for m in grid]
    assert rf['m'] == pytest.approx(grid[np.argmin(losses)], abs=.001)
    log_slope = np.polyfit(np.log(p), np.log(shape), 1)[0]
    assert abs(rf['m']-log_slope) > .1
    assert c.fit(p, shape*1000, 'L2')['m'] == pytest.approx(rf['m'], abs=1e-7)


def test_free_pressure_scale_and_boundaries():
    p = np.array([.4, .8, 1.5, 2.5, 4.4])*100000
    r = c.fit(p, 3e-6*c.fa_shape(p, 1/2.3), 'FA-S')
    assert r['Pstar_bar'] == pytest.approx(2.3, rel=1e-7)
    np.testing.assert_allclose(c.predict(p, r), r['pred'], rtol=1e-10)
    zero = c.fit(p, np.full_like(p, 2e-6), 'L2')
    assert zero['m'] == 0
    inf = c.fit(p, 3e-6*c.fa_shape(p, 0), 'FA-S')
    assert inf['inverse_Pstar_bar'] == 0


def test_shared_calibration_and_fixed_normalization():
    contract, coords = c.read_inputs()
    central = c.realize(contract, coords)
    offsets = np.zeros(12+2*len(coords)); offsets[0] = 1
    moved = c.realize(contract, coords, offsets)
    a = np.array([r['panel']=='a' for r in coords])
    assert np.all(moved[a, 1] < central[a, 1])
    np.testing.assert_array_equal(moved[~a], central[~a])
    np.testing.assert_array_equal(moved[:, 0], central[:, 0])
    q = np.array([1., 2.]); fa = np.array([.5, 1.5]); l0 = np.array([1.1, 2.2])
    central_s2 = 3.0
    assert c.matched_contrast(q, fa, l0, central_s2) == pytest.approx((.25-.025)/3)
    # Never substitute a draw-specific denominator or subtract interval endpoints.
    assert c.matched_contrast(q+1, fa, l0, central_s2) == pytest.approx((2.25-.725)/3)


def test_intake_is_means_not_steps_or_reconstructed_beds():
    contract, rows = c.read_inputs()
    assert len(rows) == 108
    assert len({r['series'] for r in rows}) == 12
    assert sum(r['series']=='A-480' for r in rows) == 7
    assert sum(r['series']=='C-360' for r in rows) == 10
    assert len({r['point_id'] for r in rows}) == 108
    assert all(r['sd_y_status']=='unresolved_not_zero' for r in rows if not r['sd_top_px'])
    for name, expected in [('n',c.N),('Pd_bar',c.PD_BAR),('Pstar_bar',c.PSTAR_BAR)]:
        assert contract['frozen_shape'][name] == expected


def test_report_pairs_retain_central_scales_and_identical_twelve_series():
    """Audit serialized paired results independently of the fitter."""
    import csv
    import json
    from collections import defaultdict
    contrast = list(csv.DictReader((c.OUTPUT/'CONTRASTS.csv').open()))
    scales = {r['series']: float(r['S2_m6_s2']) for r in contrast}
    grouped = defaultdict(list)
    pooled = {}
    with (c.OUTPUT/'READING_REALIZATIONS.csv').open() as f:
        for r in csv.DictReader(f):
            draw = int(r['realization'])
            if r['series']=='POOLED':
                pooled[draw] = float(r['D_series'])
            else:
                assert float(r['S2_central_m6_s2']) == scales[r['series']]
                d = (float(r['FA_MSE_m6_s2'])-float(r['L0_MSE_m6_s2']))/scales[r['series']]
                assert float(r['D_series']) == pytest.approx(d, abs=1e-15)
                assert float(r['m_minus_m_FA']) == pytest.approx(float(r['m'])-float(r['m_FA']), abs=1e-15)
                grouped[draw].append(d)
    assert len(grouped) == len(pooled) == 4096
    for draw, ds in grouped.items():
        assert len(ds) == 12
        assert np.mean(ds) == pytest.approx(pooled[draw], abs=1e-15)
    result = json.loads((c.OUTPUT/'RESULT.json').read_text())
    np.testing.assert_allclose(np.quantile(list(pooled.values()), [.025,.975]), result['D_reading_interval'])
