"""Small arithmetic/resource tests of 005's runner; no full-mesh execution."""
import json
from unittest.mock import patch

import numpy as np
import pytest

from tools import pannusch_state_envelope_verification as runner
from puckworks.models.pannusch2024 import state_envelope as se


def test_inventory_preserving_lift_and_transpose_over_same_coarse_states():
    m = np.arange(1., 13.)*1e-7  # three phases, N4; only a test vector
    fine = np.repeat(m/2, 2)
    g = np.arange(24.)/25
    projected = runner.lift_transpose(g)
    np.testing.assert_allclose(fine.reshape(3, 4, 2).sum(axis=2).ravel(), m, rtol=0, atol=0)
    assert np.dot(g, fine) == pytest.approx(np.dot(projected, m), rel=1e-15)


def test_uniform_sensitivity_optimizes_both_signs_instead_of_sampling_witnesses():
    from test_pannusch_state_envelope import inventory_fixture
    u, M = inventory_fixture()
    g = np.zeros(6); g[:2] = (-.3, .8)
    out = runner.sensitivity(u, g, np.zeros(6), se.FVEnvelopeSettings())
    lo, hi = out['maximum_absolute_difference_interval_kg']
    assert lo <= .8*M <= hi and hi-lo < 1e-10*M
    assert out['optimization_calls'] == 2
    assert out['minimum']['interval_kg'][0] <= -.3*M
    assert out['maximum']['interval_kg'][1] >= .8*M


def test_budget_reserves_failures_blocks_resets_and_enforces_aggregate_limits(tmp_path):
    common = tmp_path/'fake-git-common'; common.mkdir()
    with patch.object(runner.subprocess, 'check_output', return_value=str(common)):
        budget = runner.Budget(tmp_path/'evidence')
        with pytest.raises(RuntimeError, match='synthetic'):
            budget.run('fake-failure-no-integration', 1, lambda: (_ for _ in ()).throw(RuntimeError('synthetic')))
        assert budget.data['executions'][0]['status'] == 'FAILED'
        assert budget.data['executions'][0]['large_executions'] == 1
        with pytest.raises(RuntimeError, match='REPEAT'):
            budget.run('fake-failure-no-integration', 1, lambda: None)
        with pytest.raises(RuntimeError, match='EXECUTION_LIMIT'):
            budget.run('too-many', 28, lambda: None)
        budget.data['wall_s'] = 1800.
        with pytest.raises(RuntimeError, match='WALL_LIMIT'):
            budget.run('too-long', 0, lambda: None)
        budget.save(); budget.lock.close()
        with pytest.raises(ValueError, match='CANNOT_RESET'):
            runner.Budget(tmp_path/'other')
    public = json.loads((tmp_path/'evidence'/'resources.json').read_text())
    assert 'evidence_dir' not in public


def test_predeclared_fixture_has_matched_volume_with_phase_and_depth_uncertainty():
    a, b, lo, hi, nominal = runner.fixture(n=4)
    assert a.flow_history.integral(7, 17) == pytest.approx(b.flow_history.integral(7, 17), rel=1e-14)
    u = se.FVChemicalStateSet(lo, hi, (8e-5, 1.2e-4), 'SYNTHETIC',
        ((8e-6, 3e-5), (1e-5, 5e-5), (2e-5, 8e-5)))
    assert u.feasibility == 'ESTABLISHED_NONEMPTY'
    assert np.ptp(lo.liquid_cell_average_kg_m3) > 0
    assert np.all(u.upper_masses_kg > u.lower_masses_kg)
