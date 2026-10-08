"""G0 resource-policy checks: no scientific trajectory or original-ledger writes."""
import json
from pathlib import Path
import runpy
import sys
from types import SimpleNamespace

import pytest
from puckworks.analysis import grudeva2026_baseline_observation_005 as obs
from puckworks.analysis import grudeva2026_baseline_observation_005_report as report

ROOT = Path(__file__).parents[1]


def archive(tmp_path):
    runner = runpy.run_path(str(ROOT/'tools/run_grudeva2026_baseline_observation_005.py'))
    local = tmp_path/'root'
    (local/'tools').mkdir(parents=True)
    for name in ('grudeva2026_bed_accuracy_004_invoke.py', 'grudeva2026_baseline_observation_005_invoke.py'):
        (local/'tools'/name).write_bytes((ROOT/'tools'/name).read_bytes())
    docs = local/'docs/analysis/model_grudeva2026_baseline_observation_005'
    docs.mkdir(parents=True)
    (docs/'MATRIX.json').write_text(json.dumps({'controller_sha256':report.OLD_CONTROLLER_SHA256}))
    (docs/'RESULTS.json').write_text('{}')
    runner['initialize'].__globals__['ROOT'] = local
    folder = tmp_path/'archive'
    runner['initialize'](folder)
    (folder/'old.log').write_text('historical synthetic software record\n')
    rows = [dict(event='start', name='old', kind='short', phase='development', time_ceiling=300., memory_bytes=2*1024**3),
            dict(event='end', name='old', seconds=.25, peak_rss_bytes=1024, log_sha256=obs.sha(folder/'old.log'))]
    (folder/'invocations.jsonl').write_text(''.join(json.dumps(v)+'\n' for v in rows))
    runner['amend_resources'](folder)
    return folder, runner


def test_amendment_preserves_history_and_enforces_actual_child_limit(tmp_path, capsys):
    folder, _ = archive(tmp_path)
    before = (folder/'invocations-before-8gib.jsonl').read_bytes()
    binding = obs.read_json(folder/'resource-amendment.json')
    assert binding['starting_seconds'] == .25
    allocation = folder/'allocation.json'
    allocation.write_text(obs.canonical(dict(attempt='enforcement-software-test', kind='short',
        controller_sha256=obs.sha(folder/'invoke.py'), resource_amendment_sha256=obs.sha(folder/'resource-amendment.json'))))
    command = ['enforcement-software-test', 'short', 'development',
               sys.executable, '-c', 'import resource,time; print(resource.getrlimit(resource.RLIMIT_AS)); time.sleep(.15)',
               '--allocation', str(allocation), '--output', str(folder/'none.json')]
    controller = runpy.run_path(str(folder/'invoke.py'))
    # This ordinary software child allocates no numerical arrays; host capacity
    # is tested at every actual scientific start, not required of CI hardware.
    controller['main'].__globals__['headroom'] = lambda folder: {'software_test': True}
    assert controller['main'](command) == 0
    assert '(8589934592, 8589934592)' in capsys.readouterr().out
    assert (folder/'invocations.jsonl').read_bytes().startswith(before)
    result = report.resource_audit(folder)
    assert result['passed'], result['reasons']
    assert result['short'] == 2 and result['full'] == 0
    assert result['ends']['enforcement-software-test']['enforced_rlimit_as'] == [8*1024**3]*2


@pytest.mark.parametrize('damage', ['limit', 'policy', 'controller', 'unresolved', 'malformed', 'historical'])
def test_resource_policy_rejects_wrong_identity_limit_and_ledger(tmp_path, damage):
    folder, _ = archive(tmp_path)
    if damage == 'controller':
        with (folder/'invoke.py').open('a') as f:
            f.write('# wrong enforcement bytes\n')
    elif damage == 'historical':
        rows = [json.loads(v) for v in (folder/'invocations.jsonl').read_text().splitlines()]
        rows[0]['memory_bytes'] = 8*1024**3
        (folder/'invocations.jsonl').write_text(''.join(json.dumps(v)+'\n' for v in rows))
    else:
        row = dict(event='start', name='new', kind='short', phase='development', time_ceiling=300,
                   memory_bytes=4*1024**3 if damage == 'limit' else 8*1024**3,
                   resource_policy='wrong' if damage == 'policy' else report.RESOURCE_POLICY,
                   controller_sha256=obs.sha(folder/'invoke.py'),
                   resource_amendment_sha256=obs.sha(folder/'resource-amendment.json'))
        with (folder/'invocations.jsonl').open('a') as f:
            f.write(json.dumps(row)+'\n')
            if damage == 'malformed':
                f.write(json.dumps(dict(event='end', name='new', seconds='bad', peak_rss_bytes=0))+'\n')
    result = report.resource_audit(folder)
    assert not result['passed'] and result['reasons']


def test_amendment_refuses_unresolved_original_ledger(tmp_path):
    folder, runner = archive(tmp_path)
    (folder/'resource-amendment.json').unlink()
    (folder/'invoke.py').write_bytes((folder/'invoke-2gib.py').read_bytes())
    with (folder/'invocations.jsonl').open('a') as f:
        f.write(json.dumps(dict(event='start', name='lost', kind='short', phase='development', time_ceiling=300, memory_bytes=2*1024**3))+'\n')
    with pytest.raises(ValueError, match='unresolved'):
        runner['amend_resources'](folder)


def test_allocation_only_authorizes_exact_replacement_pilot(tmp_path, monkeypatch):
    folder, runner = archive(tmp_path)
    matrix = folder/'matrix.json'; matrix.write_text('{}')
    allocation = folder/'allocation.json'
    args = SimpleNamespace(pilot=True, row='combined', output=folder/'pilot.json', allocation=allocation, matrix=matrix)
    spec = dict(attempt='pilot-combined-8gib', kind='short', row='combined', output='pilot.json',
                role='replacement_pilot', sources=obs.sources(), controls=obs.controls('combined'),
                request_hashes={k:obs.digest(v) for k,v in obs.requests(.4).items()},
                controller_sha256=obs.sha(folder/'invoke.py'), resource_amendment_sha256=obs.sha(folder/'resource-amendment.json'),
                matrix_sha256=obs.sha(matrix), runner_sha256=obs.sha(ROOT/'tools/run_grudeva2026_baseline_observation_005.py'))
    monkeypatch.setenv('GRUDEVA005_ATTEMPT', 'pilot-combined-8gib')
    monkeypatch.setenv('GRUDEVA005_RESOURCE_POLICY', report.RESOURCE_POLICY)
    allocation.write_text(obs.canonical(spec))
    assert runner['allocation_gate'](args)['role'] == 'replacement_pilot'
    spec['role'] = 'force'; allocation.write_text(obs.canonical(spec))
    with pytest.raises(ValueError, match='unauthorized'):
        runner['allocation_gate'](args)
    spec['role'] = 'combined_feasibility_probe'; allocation.write_text(obs.canonical(spec))
    with pytest.raises(ValueError, match='exact combined'):
        runner['allocation_gate'](args)


def test_allocation_receipt_change_cannot_restamp_scientific_identity(tmp_path):
    p = obs.read_json(ROOT/'docs/analysis/model_grudeva2026_baseline_observation_005/MATRIX.json')
    path = tmp_path/'before.json'; path.write_text(obs.canonical(p))
    specification = {'captured_matrix': {'file':path.name, 'sha256':obs.sha(path)}}
    p['feasibility'] = {'disposition':'FEASIBLE'}
    assert report.captured_matrix_hash(tmp_path,p,specification,'different-current-hash') == obs.sha(path)
    p['request_hashes']['diagnostic_times'] = 'changed'
    with pytest.raises(ValueError, match='scientific identity changed'):
        report.captured_matrix_hash(tmp_path,p,specification,'new')


def test_only_named_corrective_recapture_with_current_qualified_fixtures(tmp_path, monkeypatch):
    folder, runner = archive(tmp_path)
    matrix = folder/'matrix.json'; matrix.write_text('{}')
    (folder/'persistence-amendment.json').write_text('{}')
    fixtures = []
    for name in ('current.json', 'minimum.json'):
        path = folder/name
        path.write_text(obs.canonical({'exit_code':0, 'sources':obs.sources()}))
        fixtures.append({'file':name, 'sha256':obs.sha(path)})
    allocation = folder/'recapture-allocation.json'
    args = SimpleNamespace(pilot=False, row='combined', output=folder/'recapture.json', allocation=allocation, matrix=matrix)
    spec = dict(attempt='combined-persistence-recapture', kind='full', row='combined', output='recapture.json',
                role='combined_persistence_recapture', sources=obs.sources(), controls=obs.controls('combined'),
                request_hashes={k:obs.digest(v) for k,v in obs.requests().items()},
                controller_sha256=obs.sha(folder/'invoke.py'), resource_amendment_sha256=obs.sha(folder/'resource-amendment.json'),
                persistence_amendment_sha256=obs.sha(folder/'persistence-amendment.json'),
                persistence_tests=fixtures, remaining_panel_estimate={'planning_only':True},
                matrix_sha256=obs.sha(matrix), runner_sha256=obs.sha(ROOT/'tools/run_grudeva2026_baseline_observation_005.py'))
    monkeypatch.setenv('GRUDEVA005_ATTEMPT', spec['attempt'])
    monkeypatch.setenv('GRUDEVA005_RESOURCE_POLICY', report.RESOURCE_POLICY)
    allocation.write_text(obs.canonical(spec))
    assert runner['allocation_gate'](args)['role'] == 'combined_persistence_recapture'
    spec['attempt'] = 'second-recapture'
    monkeypatch.setenv('GRUDEVA005_ATTEMPT', spec['attempt'])
    allocation.write_text(obs.canonical(spec))
    with pytest.raises(ValueError, match='exact corrective'):
        runner['allocation_gate'](args)
    spec['attempt'] = 'combined-persistence-recapture'
    monkeypatch.setenv('GRUDEVA005_ATTEMPT', spec['attempt'])
    spec['persistence_tests'] = []
    allocation.write_text(obs.canonical(spec))
    with pytest.raises(ValueError, match='qualified tests'):
        runner['allocation_gate'](args)


def test_persistence_controller_history_prefix_cannot_be_rewritten(tmp_path):
    folder, _ = archive(tmp_path)
    prefix = folder/'invocations-before-persistence-controller.jsonl'
    prefix.write_bytes((folder/'invocations.jsonl').read_bytes())
    previous = obs.sha(folder/'invoke.py')
    (folder/'invoke-before-persistence.py').write_bytes((folder/'invoke.py').read_bytes())
    amendment = dict(previous_controller_sha256=previous, controller_sha256=previous,
                     resource_amendment_sha256=obs.sha(folder/'resource-amendment.json'),
                     historical_ledger_sha256=obs.sha(prefix))
    (folder/'persistence-amendment.json').write_text(obs.canonical(amendment))
    assert report.resource_audit(folder)['passed']
    amendment['previous_controller_sha256'] = 'wrong'
    (folder/'persistence-amendment.json').write_text(obs.canonical(amendment))
    assert not report.resource_audit(folder)['passed']
    amendment['previous_controller_sha256'] = previous
    (folder/'persistence-amendment.json').write_text(obs.canonical(amendment))
    prefix.write_text('')
    assert not report.resource_audit(folder)['passed']
