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
