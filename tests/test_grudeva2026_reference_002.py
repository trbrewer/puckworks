"""Independent numerical fixtures for the isolated reference diagnostic."""
import ast
import json
from pathlib import Path

import numpy as np
import pytest

from puckworks.analysis import grudeva2026_reference_002 as ref


def test_legacy_effective_coefficients_and_separate_source_values():
    a = ref.normalization_audit()
    assert a['passed']
    assert a['effective_fines'] == pytest.approx(3.2, abs=1e-14)
    assert a['effective_boulder_flux'] == pytest.approx(2.4, abs=1e-14)
    assert a['table1_ratio'] != a['table2_initial']
    assert a['legacy_explicit_D1_dt_over_dr2'] > 1


@pytest.mark.parametrize('c', [0., .2, .6, .95, 1.])
def test_storage_jump_front(c):
    expected = (1-c)/(1+3.2*1.388-4.2*c)
    assert ref.jump_speed(c) == pytest.approx(expected, rel=1e-12)


def test_conservative_shell_exchange_and_unconditional_stability():
    op = ref.shell_operator(40, 1.)
    c = np.full((40, 3), 1.388)
    boundary = np.array([0., 1.388, 1.6])
    after = ref.shell_step(c, boundary, .3, op)
    loss = op[0]@(c-after)
    surface = .3*op[-1]*(after[-1]-boundary)
    assert loss == pytest.approx(surface, abs=1e-12)
    assert np.min(after) >= 0
    assert loss[0] > 0 and abs(loss[1]) < 1e-12 and loss[2] < 0


def test_manufactured_moving_liquid_transport():
    eta = np.linspace(0., 1., 23)
    s, speed, dt, slope = .3, .1, .07, .2
    actual = ref.liquid_step(slope*s*eta, np.full(23, slope), eta, s+speed*dt, speed, dt)
    assert actual == pytest.approx(slope*(s+speed*dt)*eta, abs=1e-12)


def test_sample_scheduler_neither_advances_early_nor_takes_zero_step():
    target = 1.
    t = target-.001
    assert .001 < target-t  # subtraction and addition have different rounding
    assert t+.001 == target
    assert ref.reached_sample(t, .001, target)
    assert not ref.reached_sample(target-2e-12, 1e-12, target)


def test_short_radial_time_translation_and_uptake():
    ages = np.array([0., .02, .1, .3])
    a = ref.grain_history(4.3+ages, .2, .5, .2, shells=64)
    b = ref.grain_history(15.3+ages, .2, .5, .2, shells=64)
    assert a['mean'] == pytest.approx(b['mean'], abs=1e-10)
    assert a['flux'][1:] == pytest.approx(b['flux'][1:], abs=1e-9)
    assert a['flux'][0] is None and a['flux'][-1] < 0
    json.dumps(a, allow_nan=False)


def test_core_does_not_import_baseline_or_execute_on_import():
    tree = ast.parse(Path(ref.__file__).read_text())
    imports = [n.module for n in ast.walk(tree) if isinstance(n, ast.ImportFrom)]
    assert not any(n and 'grudeva2026' in n for n in imports)
    for args in ({'dt': 0}, {'bed': True}, {'diffusivity': -1}):
        with pytest.raises(ValueError):
            ref.Controls(**args)


def test_terminal_scheduler_records_horizon_even_with_sub_ulp_remainder():
    # Exercise the same schedule policy without another coupled scientific run.
    for dt in (.001, .0005):
        target, t, recorded = 8., 7.975, False
        for _ in range(100):
            step = min(dt, target-t)
            if ref.reached_sample(t, step, target):
                t, recorded = target, True
                break
            t += step
        assert recorded and t == 8.


def test_refinement_does_not_extend_missing_endpoint_or_pass_empty_support():
    from puckworks.analysis.grudeva2026_reference_002_report import refinement
    # Saved synthetic arrays only; a huge value at unsupported t=8 must not
    # enter any local/phase metric via np.interp's endpoint extension.
    a = np.zeros((3, 10))
    a[:, 0] = [0., 7.975, 8.]
    a[-1, 1:8] = 100.
    b = a[:2].copy()
    report = refinement({'records': a, 'arrival': 6.5}, {'records': b, 'arrival': 6.5})
    assert report['unavailable_outlet'] == 1
    assert report['included_outlet'] == 2
    assert report['outlet_max_absolute'] == report['phase_or_cup_max_absolute_diagnostic'] == 0
    a[:, 0] = [6.49, 6.5, 6.51]
    b = a.copy()
    empty = refinement({'records': a, 'arrival': 6.5}, {'records': b, 'arrival': 6.5})
    assert not empty['passed'] and empty['included_outlet'] == 0
