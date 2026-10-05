"""Small runner controls; no full-mesh campaign hidden in pytest."""
import json
from pathlib import Path
import time
from unittest.mock import patch

import numpy as np
import pytest

from puckworks.models.pannusch2024 import prefix_conditioned as pc, state_envelope as se, stateful_fv as sf
from tools import pannusch_prefix_conditioned_verification as runner
from test_pannusch_prefix_conditioned import fixed_query


def test_fixture_and_generator_are_constructed_only_from_U():
    p, u = runner.fixture(n=4, h=.5)
    with patch.object(sf, 'simulate_stateful_fv', side_effect=AssertionError('generator must not evaluate model')):
        s = runner.generating_state(u)
    assert pc._residuals(pc._base_polytope(u), se._concentrations(s)*u.capacities_m3).feasible
    assert s.inventory_kg == pytest.approx(1e-4, rel=1e-14)
    assert tuple(p.flow_history.times_s) == (7., 10., 17.)


def test_representative_pattern_at_small_mesh_and_fine_pullback_replay():
    p, u = runner.fixture(n=4, h=.5)
    s = runner.generating_state(u)
    forward = sf.simulate_stateful_fv(plan=p, initial_state=s, observation_times_s=(7., 10., 12.),
                                     fraction_windows_s=runner.EARLY, stop_time_s=12.)
    assert len(forward.fractions) == 2
    assert forward.status == 'PLANNED_STOP'
    runner._check_generation(forward)
    d = .01*u.inventory_scale_kg
    bands = [(max(0., f.solute_kg-d), f.solute_kg+d) for f in forward.fractions]
    for n in (4, 8):
        current, unused = runner.fixture(n=n, h=.5)
        responses = [se.build_delivery_response(current, solute='caffeine', window_s=w)
                     for w in (*runner.EARLY, runner.TARGET)]
        if n == 8:
            responses = [pc.pull_back_equal_children(r, u) for r in responses]
            assert isinstance(responses[0], pc.FVEqualChildPullback)
            assert responses[0].identity_sha256 != responses[0].native.identity_sha256
        obs = [pc.FVFractionObservation(str(i), r, b, 'SMALL_SYNTHETIC')
               for i, (r, b) in enumerate(zip(responses, bands))]
        result = pc.replay_conditioned_extrema(pc.bound_future_delivery(
            pc.condition_on_fractions(u, current, obs), responses[-1], epsilon_kg=1e-9))
        assert result.bounds == 'QUALIFIED', result.to_json()
        assert result.compatibility == 'ESTABLISHED'
        for e in (result.minimum, result.maximum):
            assert e.witness.final_residuals.feasible
            assert len(e.witness.replay.windows) == 3
            assert all(r.contained for r in e.witness.replay.windows)
            if n == 8:
                assert e.witness.replay.replay_state_identity != e.witness.state.identity_sha256


def test_exact_equal_child_mass_lift_and_response_pullback():
    r = fixed_query()
    coarse = r.conditioned_set.original
    fine_plan = type(r.target.plan)(r.target.plan.temperature_history, r.target.plan.flow_history,
        r.target.plan.t_span_s, sf.FVSettings(cells=8, h_max_s=.02))
    native = se.build_delivery_response(fine_plan, solute='caffeine', window_s=r.target.window_s)
    mapped = pc.pull_back_equal_children(native, coarse)
    s = coarse.upper
    fine = pc._lift_state(s)
    m = se._concentrations(s)*coarse.capacities_m3
    fm = se._concentrations(fine)*sf.fv._System(s.solute, s.grind, 8).capacities
    np.testing.assert_array_equal(fm, np.repeat(m/2, 2))
    assert abs(pc._dotq(native.weights, fm)-pc._dotq(mapped.weights, m)) <= pc._dotq(mapped.mapping_roundoff_allowances, m)
    with pytest.raises(ValueError): mapped.weights.setflags(write=True)
    with pytest.raises(ValueError): native.validate(coarse)


def test_budget_failure_timeout_counts_and_prevents_output_reset(tmp_path):
    common = tmp_path/'git'; common.mkdir()
    with patch.object(runner.subprocess, 'check_output', return_value=str(common)):
        b = runner.Budget(tmp_path/'evidence')
        with pytest.raises(RuntimeError, match='injected'):
            b.run('failure', 'forward', 1, lambda: (_ for _ in ()).throw(ValueError('injected')))
        with pytest.raises(TimeoutError, match='EXTERNAL'):
            b.run('timeout', 'forward', 1, lambda: time.sleep(2), deadline_s=.02)
        assert sum(r['charged_propagations'] for r in b.data['executions']) == 2
        assert all(r['status'] == 'FAILED' for r in b.data['executions'])
        with pytest.raises(RuntimeError, match='REPEAT'):
            b.run('failure', 'forward', 1, lambda: None)
        b.lock.close()
        with pytest.raises(ValueError, match='CANNOT_RESET'):
            runner.Budget(tmp_path/'other')
    public = json.loads((tmp_path/'evidence'/'resources.json').read_text())
    assert 'evidence_dir' not in public


def test_budget_propagation_lp_wall_limits_and_immutable_pipe_receipt(tmp_path):
    common = tmp_path/'git'; common.mkdir()
    with patch.object(runner.subprocess, 'check_output', return_value=str(common)):
        b = runner.Budget(tmp_path/'evidence')
        received = b.run('small-response', 'response', 2, lambda: fixed_query(n=1).target)
        with pytest.raises(ValueError): received.weights.setflags(write=True)
        assert b.data['executions'][0]['exponential_actions'] > 0
        b.data['executions'] = [dict(label=str(i), kind='forward', charged_propagations=1,
                                    status='RETURNED') for i in range(64)]
        with pytest.raises(RuntimeError, match='PROPAGATION_LIMIT'):
            b.run('overflow', 'forward', 1, lambda: None)
        b.data['executions'] = [dict(label=str(i), kind='lp', charged_propagations=0,
                                    status='RETURNED') for i in range(160)]
        with pytest.raises(RuntimeError, match='LP_LIMIT'):
            b.run('overflow', 'lp', 0, lambda: None)
        b.prior_wall = 1801.
        with pytest.raises(RuntimeError, match='WALL_LIMIT'):
            b.run('wall', 'forward', 1, lambda: None)
        b.lock.close()


def test_specification_and_runner_keep_004_failure_and_fixed_campaign_scope():
    spec = Path('docs/analysis/model_pannusch2024_prefix_conditioned_006/CONTRACT.md').read_text()
    assert 'resolved_temporal_decrease=FAIL' in spec
    assert runner.EARLY == ((7., 10.), (10., 12.))
    assert runner.TARGET == (12., 17.) and runner.EPSILON_KG == 1e-9


def test_native_response_reuse_reconstructs_and_validates_identity_without_propagation():
    r = fixed_query(n=1).target
    data = pc._json_value(r, True, True)
    with patch.object(se, 'expm_multiply', side_effect=AssertionError('must reuse')):
        restored = runner._restore_native(data)
    assert restored.identity_sha256 == r.identity_sha256
    np.testing.assert_array_equal(restored.weights, r.weights)
    with pytest.raises(ValueError): restored.weights.setflags(write=True)
    data['weights'][0] += 1e-3
    with pytest.raises(RuntimeError, match='IDENTITY'):
        runner._restore_native(data)
