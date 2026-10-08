"""Offline reporter adversarial support, disposition and identity checks."""
from copy import deepcopy
import json
from pathlib import Path
import subprocess
import sys

import numpy as np
import pytest

from puckworks.analysis import grudeva2026_baseline_observation_005 as obs
from puckworks.analysis import grudeva2026_baseline_observation_005_report as report


def plan():
    return dict(sources=obs.sources(), reporter_sha256=obs.sha(report.__file__),
                request_hashes={k: obs.digest(v) for k, v in obs.requests().items()},
                runs={k: {'file': k+'.json', 'attempt': k, 'controls': obs.controls(k)}
                      for k in [*obs.ROWS, 'repeat', 'control']},
                feasibility={'disposition': 'RESOURCE_FEASIBILITY_BLOCKED'})


def synthetic_observations():
    t, z = obs.observation_support(8.)
    return dict(arrival=6.5, z=z.tolist(), activation=(6.5*z).tolist(),
                grain_history_activation=(6.5*np.array(obs.HISTORY_Z)).tolist(),
                records=[[v, min(v/6.5, 1.), 0., 0., 0., 0., 0., 0.] for v in t],
                observations=[dict(t=v, liquid_profile=[0.]*len(z), grain_profile=[0.]*len(z),
                                   grain_history=[0.]*7) for v in t])


def test_inherited_masks_counts_and_endpoint_are_preserved():
    a = synthetic_observations()
    b = deepcopy(a)
    t, z = obs.observation_support(8.)
    index = int(np.flatnonzero(t == 7.)[0])
    b['observations'][index]['liquid_profile'][-1] = .01
    b['observations'][index]['grain_profile'][-1] = .001
    b['observations'][index]['grain_history'][-1] = .001
    values = report.refinement(a, b)  # also asserts exact inherited gate/count parity
    assert not values['liquid_profiles']['passed']
    assert values['liquid_profiles']['location']['t'] == 7.
    assert values['liquid_profiles']['location']['z'] == 1.
    assert values['grain_profiles']['location']['z'] == 1.
    assert values['grain_histories']['requested'] == 395*7
    assert values['cup']['included'] == 395
    assert values['cup']['excluded'] == 0
    for row in values.values():
        assert row['requested'] == row['included']+row['excluded']+row['unavailable']


def test_missing_even_excluded_data_and_empty_support_cannot_pass():
    missing = report.metric([0., np.nan], [True, False], [True, False], .001)
    assert not missing['passed'] and missing['unavailable'] == 1
    assert not report.metric([0., 0.], False, True, .001)['passed']
    for row in report.unavailable_metrics('missing').values():
        assert not row['passed'] and row['included'] == row['excluded'] == 0
        assert row['unavailable'] == row['requested']


def test_wrong_identities_and_multiple_failures_remain_individual_reasons(tmp_path, monkeypatch):
    from puckworks.models.grudeva2026 import reduced
    monkeypatch.setattr(reduced, 'simulate', lambda *a, **k: pytest.fail('offline reporter launched a solver'))
    matrix = tmp_path/'matrix.json'
    p = plan()
    p['sources'] = {}
    p['request_hashes'] = {}
    matrix.write_text(json.dumps(p))
    result = report.report(tmp_path, matrix)
    assert result['disposition'] == report.OBSERVER_INCOMPLETE
    assert set(result['blocks']) >= {'SOURCE_IDENTITY_BLOCKED', 'SUPPORT_IDENTITY_BLOCKED',
                                     'RESOURCE_ACCOUNTING_BLOCKED', 'RESOURCE_FEASIBILITY_BLOCKED'}
    assert len(result['runs']) == 7
    assert all(r['reasons'] for r in result['runs'].values())
    assert result['production_numerics'] == 'NOT_EXECUTED'
    assert result['physical_validation'] == 'NOT_ESTABLISHED'


def test_unresolved_resource_start_prevents_qualification(tmp_path):
    (tmp_path/'invocations.jsonl').write_text(json.dumps({'event': 'start', 'name': 'lost', 'kind': 'full'})+'\n')
    r = report.resource_audit(tmp_path)
    assert not r['passed']
    assert 'unresolved attempt starts/ends' in r['reasons']
    assert r['full'] == 1


@pytest.mark.parametrize('damaged', [False, True])
def test_cli_json_disposition_and_exit_code_consistency(tmp_path, damaged):
    matrix, output = tmp_path/'matrix.json', tmp_path/'result.json'
    matrix.write_text('{"x":1e999}' if damaged else json.dumps(plan()))
    root = Path(__file__).resolve().parents[1]
    r = subprocess.run([sys.executable, '-m', report.__name__, '--runs-directory', str(tmp_path),
                        '--matrix', str(matrix), '--output', str(output)], cwd=root, capture_output=True, text=True)
    assert r.returncode == 2
    result = json.loads(output.read_text())
    assert result['disposition'] == report.OBSERVER_INCOMPLETE
    assert result['disposition'] in r.stdout


def test_fixture_pass_flag_is_not_trusted(tmp_path):
    fixtures = {'sources': obs.sources(), 'passed': True, 'fixtures': {}}
    path = tmp_path/'fixtures.json'
    path.write_text(json.dumps(fixtures))
    p = {'fixtures': {'file': path.name, 'sha256': obs.sha(path)}}
    result = report.fixture_audit(tmp_path, p)
    assert not result['passed']
    assert len(result['reasons']) >= 8


def test_wrong_run_source_configuration_support_and_result_are_all_reported():
    failures = report.check_run({'sources': {}, 'controls': {}, 'parameters': {},
                                  'public_result': {}, 'public_result_sha256': 'wrong'},
                                 obs.controls('normal'), 'frozen')
    assert 'source identity mismatch' in failures
    assert 'configuration mismatch' in failures
    assert 'public/diagnostic support identity mismatch' in failures
    assert 'public Result identity mismatch' in failures
    assert 'matrix identity mismatch' in failures


def test_blocked_matrix_cannot_launch_full_runner(tmp_path, monkeypatch):
    import runpy
    runner = runpy.run_path(str(Path(__file__).parents[1]/'tools/run_grudeva2026_baseline_observation_005.py'))
    matrix = tmp_path/'matrix.json'
    matrix.write_text(json.dumps(plan()))
    monkeypatch.setenv('GRUDEVA005_ATTEMPT', 'synthetic-no-invocation')
    monkeypatch.setattr(obs, 'execute', lambda *a, **k: pytest.fail('blocked full run launched'))
    with pytest.raises(SystemExit) as result:
        runner['main'](['run', '--row', 'normal', '--matrix', str(matrix), '--output', str(tmp_path/'out.json')])
    assert result.value.code == 2


@pytest.mark.parametrize('failed_gate', ['diagnostic_inlet', 'diagnostic_liquid_profile_bounds',
                                        'diagnostic_grain_profile_bounds', 'diagnostic_grain_history_bounds'])
def test_failed_observer_endpoint_or_point_bounds_cannot_be_attributed_to_production(tmp_path, monkeypatch, failed_gate):
    # Isolate report disposition from already-tested capture/identity checks.
    # All seven raw executions exist, neutrality is exact, and refinement agrees.
    p = plan()
    p['feasibility'] = {'disposition': 'FEASIBLE'}
    controller = tmp_path/'invoke.py'
    controller.write_text('# synthetic accounting fixture\n')
    p['controller_sha256'] = obs.sha(controller)
    matrix = tmp_path/'matrix.json'
    matrix.write_text(json.dumps(p))
    starts, ends = {}, {}
    for name in p['runs']:
        path = tmp_path/(name+'.json')
        public = {'status': 'COMPLETED'}
        path.write_text(obs.canonical(dict(public_result=public, public_result_sha256=obs.digest(public),
                                           environment={'synthetic': True})))
        starts[name] = {'kind': 'full'}
        ends[name] = {'artifact_sha256': obs.sha(path), 'exit_code': 2}
    monkeypatch.setattr(report, 'resource_audit', lambda folder: dict(passed=True, reasons=[], full=7,
                                                                     starts=starts, ends=ends))
    monkeypatch.setattr(report, 'fixture_audit', lambda *args: dict(passed=True, reasons=[]))
    monkeypatch.setattr(report, 'check_run', lambda *args: [])
    observed = synthetic_observations()
    observed['audits'] = {}
    monkeypatch.setattr(obs, 'observe_saved', lambda path: deepcopy(observed))
    keys = ['independent_inventory_sums', 'public_inventory_algebra', 'public_profile_reconstruction',
            'public_cup_outlet_reconstruction', 'tail_weights_rates', 'cup_quadrature', 'diagnostic_inlet',
            'diagnostic_liquid_profile_bounds', 'diagnostic_grain_profile_bounds', 'diagnostic_grain_history_bounds']
    monkeypatch.setattr(report, 'numeric_gates', lambda *args: {k: k != failed_gate for k in keys})
    r = report.report(tmp_path, matrix)
    assert r['neutrality']['passed'] and r['deterministic_repeat']['passed']
    assert all(g['passed'] for pair in r['refinements'].values() for g in pair.values())
    assert not r['observer_qualified']
    assert r['disposition'] == report.OBSERVER_INCOMPLETE
    assert r['production_numerics'] == 'INCOMPLETE'
    assert any(failed_gate in reason for reason in r['reasons'])


def test_failed_full_attempt_remains_executed_without_reconstructable_output(tmp_path):
    matrix = tmp_path/'matrix.json'
    matrix.write_text(json.dumps(plan()))
    (tmp_path/'invocations.jsonl').write_text(json.dumps({'event': 'start', 'name': 'normal', 'kind': 'full'})+'\n')
    r = report.report(tmp_path, matrix)
    assert r['production_numerics'] == 'INCOMPLETE'
    assert r['disposition'] == report.OBSERVER_INCOMPLETE
    assert 'unresolved attempt starts/ends' in r['reasons']


def test_numeric_gates_check_diagnostic_bounds_without_a_unit_grain_cap():
    bound_rows = [dict(t=8., liquid_profile=[0., 1.], grain_profile=[0., 12.], grain_history=[12.]*7)]
    a = dict(horizon=8., max_normalized_conservation=0., aqueous_min=0., aqueous_max=1.,
             grain_mean_min=0., phase_min=0., front_wet_excess=0., front_decrease=0.,
             cup_quadrature_refinement_max=0., cup_state_integral_max=0.,
             independent_sum_allowance_fraction=0., public_inventory_allowance_fraction=0.,
             public_profile_reconstruction_error=0., public_cup_error=0., public_outlet_error=0.,
             diagnostic_inlet_mean_error=0., spectrum={'weight_error':0., 'rate_relative_error':0.},
             diagnostic_bounds=obs.diagnostic_bounds(bound_rows, [0., 1.]))
    run = dict(audits=a, events=[{}, {}], arrival=6.5, activation=[0.]*220,
               grain_history_activation=[0.]*7, unavailable_times=[])
    meta = dict(public_result={'status':'COMPLETED'}, segments=[{'success':True}])
    assert all(report.numeric_gates(run, meta).values())
    for field in ('liquid_profile', 'grain_profile', 'grain_history'):
        a['diagnostic_bounds'][field]['minimum'] = -7/6
    gates = report.numeric_gates(run, meta)
    assert gates['aqueous_bounds'] and gates['grain_bounds']
    assert not gates['diagnostic_liquid_profile_bounds']
    assert not gates['diagnostic_grain_profile_bounds']
    assert not gates['diagnostic_grain_history_bounds']


def test_observer_inlet_stop_retains_precise_block_without_production_attribution(tmp_path):
    p = plan()
    p['feasibility'] = {'disposition':'FEASIBLE', 'execution_block':'OBSERVER_DIAGNOSTIC_INLET_BLOCKED'}
    matrix = tmp_path/'matrix.json'; matrix.write_text(obs.canonical(p))
    result = report.report(tmp_path, matrix)
    assert 'OBSERVER_DIAGNOSTIC_INLET_BLOCKED' in result['blocks']
    assert result['disposition'] == report.OBSERVER_INCOMPLETE
    assert result['production_numerics'] == 'NOT_EXECUTED'
