"""Small 007 runner/accounting checks, full campaign stays outside ordinary CI."""
from dataclasses import replace
import json
from pathlib import Path
import time
from unittest.mock import patch

import numpy as np
import pytest

from puckworks.models.pannusch2024 import common_past_contrast as cc, prefix_conditioned as pc, state_envelope as se, stateful_fv as sf
from tools import pannusch_common_past_contrast_verification as runner
from test_pannusch_common_past_contrast import inputs, query


def test_fixed_fixture_generation_then_four_small_operators_and_lift():
    a, b, u = runner.fixture(n=4, h=.5)
    assert a.temperature_history.times_s == (7., 12., 14.5, 17.)
    assert a.temperature_history.temperatures_K == tuple(t+273.15 for t in (90., 90., 86., 94.))
    with patch.object(sf, 'simulate_stateful_fv', side_effect=AssertionError('generation must use only U')):
        generator = runner.generating_state(u)
    forward = sf.simulate_stateful_fv(plan=a, initial_state=generator, observation_times_s=(7., 10., 12.),
        fraction_windows_s=runner.EARLY, stop_time_s=12.)
    runner._check_generation(forward)
    assert len(forward.fractions) == 2 and forward.plan.identity_sha256 == a.identity_sha256
    d = .01*u.inventory_scale_kg
    bands = [(max(0., f.solute_kg-d), f.solute_kg+d) for f in forward.fractions]
    kw = dict(branch_time_s=12., epsilon_kg=1e-9, delta_kg=1e-6, comparison_basis='MATCHED_COLLECTED_VOLUME')
    for n, h in ((4, .5), (4, .25), (4, .125), (8, .5)):
        pa, pb, unused = runner.fixture(n=n, h=h)
        responses = [se.build_delivery_response(p, solute='caffeine', window_s=w) for p, w in
                     ((pa, runner.EARLY[0]), (pa, runner.EARLY[1]), (pa, runner.TARGET), (pb, runner.TARGET))]
        if n == 8:
            responses = [pc.pull_back_equal_children(r, u) for r in responses]
        obs = tuple(pc.FVFractionObservation(str(i), r, band, 'SYNTHETIC_BAND')
                    for i, (r, band) in enumerate(zip(responses, bands)))
        for supplied in ((), obs):
            if n == 4:
                out = cc.bound_common_past_contrast(pc.condition_on_fractions(u, pa, supplied), *responses[-2:], **kw)
            else:
                out = cc.bound_mapped_common_past_contrast(u, *responses[-2:], observations=supplied, **kw)
                if not supplied:
                    with pytest.raises(ValueError, match='MESH_MISMATCH'):
                        pc.condition_on_fractions(u, pa, ())
            result = cc.replay_common_past_extrema(out)
            assert result.bounds == 'QUALIFIED', result.to_json()
            assert result.forward_calls == 4 and result.compatibility == 'ESTABLISHED'
            assert all(abs(v-1e-5) <= result.receipt.volume_rounding_allowance_m3 for v in result.receipt.target_volumes_m3)
            assert result.receipt.target_volumes_m3 == result.receipt.post_branch_volumes_m3
            for e in (result.minimum, result.maximum):
                assert e.witness.final_residuals.feasible and e.witness.replay.prefix_bitwise_equal
                if n == 8:
                    m = e.witness.masses_kg
                    lifted = pc._lift_state(e.witness.state)
                    assert np.array_equal(se._concentrations(lifted)*sf.fv._System('caffeine', 1.7, n).capacities, np.repeat(m/2, 2))
                    assert e.witness.replay.replay_state_identity == lifted.identity_sha256
        if n == 8:
            with pytest.raises(ValueError, match='MIXED_NATIVE|INCOMPATIBLE_RESPONSE'):
                cc.bound_mapped_common_past_contrast(u, responses[-2], responses[-1], observations=(
                    replace(obs[0], response=obs[0].response.native),), **kw)
            changed = responses[-1]
            object.__setattr__(changed, 'mapping', 'ALTERED')
            with pytest.raises(ValueError, match='IDENTITY'):
                cc.bound_mapped_common_past_contrast(u, responses[-2], changed, **kw)


def test_no_tolerant_replay_can_replace_structural_proof_and_failed_receipts_survive():
    c, a, b = inputs()
    r = query(c, a, b)
    original = sf.simulate_stateful_fv
    def unsupported(**kwargs):
        f = original(**kwargs)
        return replace(f, observation_status=('UNSUPPORTED',)*len(f.observation_status))
    with patch.object(sf, 'simulate_stateful_fv', side_effect=unsupported):
        out = cc.replay_common_past_extrema(r)
    assert out.compatibility == 'UNRESOLVED'
    assert out.minimum.witness.replay.branch_a.status == 'UNRESOLVED'
    def bad_trace(**kwargs):
        f = original(**kwargs)
        if kwargs['plan'].identity_sha256 == b.plan.identity_sha256:
            raw = f.raw_primary_masses_kg.copy()
            raw[1, 0] = np.nextafter(raw[1, 0], np.inf)
            f = replace(f, raw_primary_masses_kg=raw)
        return f
    with patch.object(sf, 'simulate_stateful_fv', side_effect=bad_trace):
        out = cc.replay_common_past_extrema(r)
    assert out.minimum.witness.replay.termination == 'COMMON_PREFIX_BITWISE_REPLAY_MISMATCH'
    assert out.compatibility == 'UNRESOLVED'
    def wrong_state(**kwargs):
        f = original(**kwargs)
        return replace(f, root_state=c.original.upper)
    with patch.object(sf, 'simulate_stateful_fv', side_effect=wrong_state):
        out = cc.replay_common_past_extrema(r)
    assert out.bounds != 'QUALIFIED'
    assert out.minimum.witness.replay.termination == 'REPLAY_STATE_PLAN_OR_WINDOW_MISMATCH'


def test_replay_hull_containment_not_overlap():
    c, a, b = inputs()
    w = query(c, a, b).minimum.witness
    forward = sf.simulate_stateful_fv(plan=a.plan, initial_state=w.state,
        observation_times_s=(7., 7.1, 7.2), fraction_windows_s=(a.window_s,))
    value = forward.fractions[0].solute_kg
    obs = pc.FVFractionObservation('narrow', a, (value, value), 'EXACT_SYNTHETIC_STRESS')
    row = cc._window_replay(a, forward.fractions[0], forward, w.masses_kg, obs)
    assert row.combined_interval_kg[0] < value < row.combined_interval_kg[1]
    assert not row.contained and row.status == 'UNRESOLVED'


def test_invalid_reconstructed_state_and_excessive_repair_do_not_qualify():
    c, a, b = inputs()
    r = query(c, a, b)
    w = r.minimum.witness
    altered = replace(w, masses_kg=w.masses_kg*2)
    out = cc.replay_common_past_extrema(replace(r, minimum=replace(r.minimum, witness=altered)))
    assert out.minimum.status != 'QUALIFIED'
    assert out.minimum.witness.replay.termination == 'WITNESS_CHANGED_OR_OUTSIDE_JOINT_SET'
    # 006 bounded repair is consumed directly: a proposal exceeding the cap
    # cannot be called a compatible extremum, even for a feasible replacement.
    mass = c.original.upper_masses_kg*10
    evidence = replace(r.core.inner_optimizations[0], raw_masses_kg=mass)
    candidate = pc._candidate(c.original, r.core.inner, evidence, r.objective, search=r.core.search)
    assert candidate.status == 'UNRESOLVED'


def test_budget_failure_timeout_and_persistent_limits(tmp_path):
    common = tmp_path/'git'; common.mkdir()
    with patch.object(runner.subprocess, 'check_output', return_value=str(common)):
        budget = runner.Budget(tmp_path/'evidence')
        with pytest.raises(RuntimeError, match='injected'):
            budget.run('fail', 'forward', 1, lambda: (_ for _ in ()).throw(ValueError('injected')))
        with pytest.raises(TimeoutError):
            budget.run('timeout', 'forward', 1, lambda: time.sleep(2), deadline_s=.02)
        assert sum(r['charged_propagations'] for r in budget.data['executions']) == 2
        with pytest.raises(RuntimeError, match='REPEAT'):
            budget.run('fail', 'forward', 1, lambda: None)
        budget.data['executions'] = [dict(label=str(i), kind='forward', charged_propagations=1,
                                        status='RETURNED') for i in range(80)]
        with pytest.raises(RuntimeError, match='PROPAGATION_LIMIT'):
            budget.run('overflow', 'forward', 1, lambda: None)
        budget.data['executions'] = [dict(label=str(i), kind='lp', charged_propagations=0,
                                        status='RETURNED') for i in range(160)]
        with pytest.raises(RuntimeError, match='LP_LIMIT'):
            budget.run('overflow', 'lp', 0, lambda: None)
        budget.prior_wall = 1801.
        with pytest.raises(RuntimeError, match='WALL_LIMIT'):
            budget.run('wall', 'forward', 1, lambda: None)
        budget.lock.close()
        with pytest.raises(ValueError, match='CANNOT_RESET'):
            runner.Budget(tmp_path/'other')
    public = json.loads((tmp_path/'evidence'/'resources.json').read_text())
    assert 'evidence_dir' not in public


def test_cli_nonzero_on_unqualified_or_exception_and_no_unbounded_retry(monkeypatch, tmp_path):
    for name in ('OPENBLAS_NUM_THREADS', 'OMP_NUM_THREADS', 'MKL_NUM_THREADS'):
        monkeypatch.setenv(name, '1')
    with patch.object(runner.subprocess, 'check_output', return_value=str(tmp_path)):
        with patch.object(runner, 'execute', return_value={'disposition': 'IMPLEMENTED_QUALIFICATION_INCOMPLETE'}):
            assert runner.main(['--output', str(tmp_path/'evidence')]) == 1
        with patch.object(runner, 'execute', side_effect=RuntimeError('budget exceeded')):
            assert runner.main(['--output', str(tmp_path/'evidence')]) == 1
    spec = Path('docs/analysis/model_pannusch2024_common_past_contrast_007/CONTRACT.md').read_text()
    assert '65' in spec and '80' in spec and 'PHYSICAL_VALIDATION=NOT_ESTABLISHED' in spec
    assert runner.LEVELS == ((400, .02), (400, .01), (400, .005), (800, .02))
