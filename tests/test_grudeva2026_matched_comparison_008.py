"""Manufactured 008 policy/adapter tests; never run canonical trajectories."""
import copy
import json
from types import SimpleNamespace

import numpy as np
import pytest

from puckworks.analysis import grudeva2026_matched_comparison_008 as m
from puckworks.analysis import grudeva2026_matched_comparison_008_io as io
from puckworks.analysis import grudeva2026_baseline_observation_005_report as previous


@pytest.fixture
def run():
    t, z = m.support()
    records = np.zeros((len(t), 8))
    records[:, 0] = t
    records[:, 1] = np.minimum(t/5, 1)
    records[:, 2:] = .1
    return dict(records=records.tolist(), observations=[dict(t=float(time),
                liquid_profile=np.zeros(len(z)).tolist(), grain_profile=np.zeros(len(z)).tolist(),
                grain_history=[0.]*7) for time in t], z=z.tolist(),
                grain_history_z=list(m.obs.HISTORY_Z), activation=(z*5).tolist(),
                grain_history_activation=(np.array(m.obs.HISTORY_Z)*5).tolist(), arrival=5.,
                events=[dict(kind='first_drip', t=1., outlet_left=0., outlet_right=1.),
                        dict(kind='desaturation_exit', t=5., outlet_left=1., outlet_right=.1)])


def test_shared_mask_and_difference_parity(run):
    other = copy.deepcopy(run)
    other['arrival'] = 5.03
    other['events'][1]['t'] = 5.03
    other['records'] = np.asarray(other['records'])
    other['records'][:, 1] *= .99
    other['records'] = other['records'].tolist()
    for o in other['observations']:
        o['grain_profile'] = [1e-5]*220
        o['grain_history'] = [2e-5]*7
    actual, _ = m.compare(run, other)
    inherited = previous.refinement(run, other)
    for name in m.LIMITS:
        for key in ('included', 'excluded', 'unavailable', 'max_absolute'):
            assert actual['families'][name][key] == inherited[name][key]
    assert actual['families']['grain_profiles']['signed_difference'] == -1e-5
    assert actual['families']['arrival']['signed_difference'] == 5.-5.03


@pytest.mark.parametrize('family', m.LIMITS)
def test_exact_limit_and_next_float(family):
    limit = m.LIMITS[family]
    row, _ = m.metric([limit], [0.], True, True, limit)
    assert row['status'] == 'PASS'
    row, _ = m.metric([np.nextafter(limit, np.inf)], [0.], True, True, limit)
    assert row['status'] == 'FAIL'


@pytest.mark.parametrize('name,value', [('grain_profiles', 3e-4), ('grain_histories', 3e-4),
                                     ('cup', 7e-5), ('liquid_inventory', 7e-5),
                                     ('fines_inventory', 7e-5), ('boulder_inventory', 7e-5)])
def test_inter_method_not_refinement_limit(name, value):
    assert m.metric([value], [0], True, True, m.LIMITS[name])[0]['status'] == 'PASS'
    assert previous.BUDGETS[name] < value


def test_masks_events_endpoint_and_seven_histories(run):
    result, arrays = m.compare(run, run)
    t, z = m.support()
    assert len(result['histories']) == 7
    assert [r['history_z'] for r in result['histories']] == list(m.obs.HISTORY_Z)
    assert arrays['grain_histories']['selected'][-1, -1]
    assert arrays['grain_profiles']['selected'][-1, -1]
    assert arrays['liquid_profiles']['selected'][-1, -1]
    assert not arrays['outlet']['selected'][np.flatnonzero(t == 1)[0]]
    wet = np.flatnonzero(t == .5)[0]
    assert not arrays['liquid_profiles']['selected'][wet, np.flatnonzero(z == .5)[0]]
    # Fixed-z histories use age only; profiles also exclude the front margin.
    k = np.flatnonzero(t == .15)[0]
    j = np.flatnonzero(z == .025)[0]
    assert arrays['grain_histories']['selected'][k, 0]
    assert not arrays['grain_profiles']['selected'][k, j]
    assert all(arrays[n]['selected'].all() for n in ('cup', 'liquid_inventory', 'fines_inventory', 'boulder_inventory'))


@pytest.mark.parametrize('field', ['liquid_profile', 'grain_profile', 'grain_history'])
def test_nonfinite_not_hidden_by_exclusion(run, field):
    run['observations'][0][field][0] = float('nan')
    result, _ = m.compare(run, run)
    family = dict(liquid_profile='liquid_profiles', grain_profile='grain_profiles', grain_history='grain_histories')[field]
    assert result['families'][family]['unavailable'] == 1
    assert result['disposition'] == m.INCOMPLETE


def test_missing_activation_not_an_exclusion(run):
    run['activation'][0] = None
    run['grain_history_activation'][0] = None
    result, _ = m.compare(run, run)
    assert result['families']['grain_profiles']['unavailable'] == 395
    assert result['families']['grain_histories']['unavailable'] == 395


def test_each_required_history_must_be_nonempty(run):
    run['grain_history_activation'][-1] = 8.
    other = copy.deepcopy(run)
    other['observations'][-1]['grain_history'][0] = .01
    result, _ = m.compare(run, other)
    assert result['histories'][-1]['included'] == 0
    assert result['families']['grain_histories']['status'] == 'UNAVAILABLE'
    assert result['families']['grain_histories']['unavailable'] == 0
    assert result['disposition'] == m.INCOMPLETE
    assert result['qualified_disagreement_detected']


def test_unadmitted_input_has_all_required_reports():
    result = m.unavailable_pair('missing evidence')
    assert len(result['histories']) == 7
    assert all(r['requested'] == r['unavailable'] == 395 for r in result['histories'])
    assert not result['qualified_disagreement_detected']
    assert result['disposition'] == m.INCOMPLETE


def test_missing_and_empty_support(run):
    missing = copy.deepcopy(run)
    missing['records'].pop(0)
    missing['observations'].pop(0)
    result, _ = m.compare(run, missing)
    assert result['families']['front']['unavailable'] == 1
    missing['records'] = []
    missing['observations'] = []
    # Explicit empty 0x8 table is structurally aligned and unavailable.
    missing['records'] = np.empty((0, 8))
    result, _ = m.compare(run, missing)
    assert result['disposition'] == m.INCOMPLETE
    assert result['families']['front']['included'] == 0


@pytest.mark.parametrize('delta,unavailable', [(1e-13, 0), (3e-13, 1)])
def test_matching_allowance_no_nearest_substitution(run, delta, unavailable):
    other = copy.deepcopy(run)
    other['records'][10][0] += delta
    other['observations'][10]['t'] += delta
    result, _ = m.compare(run, other)
    assert result['families']['front']['unavailable'] == unavailable


@pytest.mark.parametrize('mutation', ['z', 'history', 'alignment', 'shape', 'length'])
def test_malformed_records_rejected(run, mutation):
    if mutation == 'z':
        run['z'][0] = .001
    if mutation == 'history':
        run['grain_history_z'][0] = .03
    if mutation == 'alignment':
        run['records'][0][0] = .001
    if mutation == 'shape':
        run['observations'][0]['grain_profile'].pop()
    if mutation == 'length':
        run['records'].pop()
    with pytest.raises(ValueError):
        m.compare(run, run)


def test_mixed_incomplete_and_disagreement(run):
    other = copy.deepcopy(run)
    other['records'][-1][3] += .01
    other['observations'][0]['grain_profile'][0] = None
    result, _ = m.compare(run, other)
    assert result['disposition'] == m.INCOMPLETE
    assert result['qualified_disagreement_detected']
    assert result['families']['cup']['status'] == 'FAIL'
    assert result['families']['cup']['signed_difference'] < 0


def test_incomplete_family_preserves_partial_excess():
    row, _ = m.metric([.01, np.nan], [0, 0], True, True, .001)
    assert row['status'] == 'UNAVAILABLE'
    assert row['qualified_disagreement_detected']
    assert row['requested'] == row['included']+row['excluded']+row['unavailable']


def test_primary_and_secondary_verdicts_independent(run):
    good, _ = m.compare(run, run)
    other = copy.deepcopy(run)
    other['records'][-1][3] += .01
    bad, _ = m.compare(run, other)
    for pairs in ([bad, good, good, good], [good, bad, good, good]):
        assert m.task_disposition(pairs) == m.DISAGREEMENT
        assert m.EXIT_CODES[m.task_disposition(pairs)] == 2
    assert m.task_disposition([good]*3) == m.INCOMPLETE
    assert m.EXIT_CODES[m.INCOMPLETE] == 3
    assert m.EXIT_CODES[m.AGREEMENT] == 0
    assert m.PAIRS == (('PRIMARY', 'P0', 'C0'), ('SECONDARY 1', 'P1', 'C0'),
                       ('SECONDARY 2', 'P0', 'C1'), ('SECONDARY 3', 'P1', 'C1'))


def test_event_side_admission(run):
    run['events'][0]['outlet_left'] = 1
    result, _ = m.compare(run, run)
    assert result['disposition'] == m.INCOMPLETE
    assert 'first-drip side' in result['reasons'][0]


def certificate_fixture():
    live = dict(allowance_fraction=.5, event_state_error=0., accepted_state_error=0.)
    segments = [dict(live_replay=dict(live), capture_outcome='PASS', numerical_replay='PASS') for _ in range(3)]
    segments[-1].update(capture_outcome='FAILED', numerical_replay='FAILED', unavailable_reason='original failure')
    segments[-1]['live_replay']['accepted_state_error'] = 1e-12
    rows = [dict(segment=i, passed=True, event_gate=True, live_offline_fidelity=True,
                 original_accepted_error=s['live_replay']['accepted_state_error'],
                 original_accepted_gate=i < 2, coordinate_certificate=i == 2) for i, s in enumerate(segments)]
    analysis = dict(assessment='DIAGNOSTIC_ONLY', replay_admission='UNRESOLVED_ORIGINAL_FAILURE_PRESERVED',
                    metadata_sha256='meta', observations_sha256='obs', gates=dict.fromkeys(io.qualification.GATES, True))
    cert = dict(passed=True, analysis_sha256='analysis',
                captures=dict(combined=dict(passed=True, metadata_sha256='meta', segments=rows)))
    final = dict(disposition=io.qualification.QUALIFIED, qualification_gates=dict(replay=True),
                 reassessment=dict(analysis_sha256='analysis'))
    return [dict(segments=segments), 'meta', analysis, 'analysis', 'obs', cert, final]


def test_certificate_composition_preserves_diagnostic_origin():
    args = certificate_fixture()
    assert io.certificate_admission(*args)['qualified']
    assert args[2]['assessment'] == 'DIAGNOSTIC_ONLY'
    assert not io.certificate.replay_admission(args[0]['segments'][2]['live_replay'])


def test_accepted_qualification_binds_closed_certificate_ledger(tmp_path, monkeypatch):
    folder = tmp_path/'replay_certification'
    folder.mkdir()
    ledger = folder/'ledger.jsonl'
    ledger.write_text('{"event":"start"}\n{"event":"end"}\n')
    accounting = dict(all_new_starts_closed=True, ledgers=dict(replay_certification=dict(
        closed=True, unresolved=[], ledger_sha256=m.obs.sha(ledger))))
    result = dict(disposition=io.qualification.QUALIFIED, qualification_gates=dict(replay=True),
                  full_external_result={}, reassessment={})
    monkeypatch.setattr(io, 'READ', lambda p: accounting if p.name == 'REPLAY_ACCOUNTING.json' else result)
    monkeypatch.setattr(io, 'bound', lambda *args: result)
    assert io.accepted_qualification(tmp_path)[0] == result
    ledger.write_text('{"event":"start"}\n')
    with pytest.raises(ValueError, match='ledger differs'):
        io.accepted_qualification(tmp_path)


@pytest.mark.parametrize('mutation', ['metadata', 'observations', 'analysis', 'cert', 'events', 'failure', 'diagnostic'])
def test_certificate_wrong_bindings_rejected(mutation):
    args = certificate_fixture()
    if mutation == 'metadata': args[1] = 'wrong'
    if mutation == 'observations': args[4] = 'wrong'
    if mutation == 'analysis': args[3] = 'wrong'
    if mutation == 'cert': args[5]['passed'] = False
    if mutation == 'events': args[0]['segments'][2]['live_replay']['event_state_error'] = 1.
    if mutation == 'failure': args[0]['segments'][2]['capture_outcome'] = 'PASS'
    if mutation == 'diagnostic': args[2]['assessment'] = 'QUALIFIED'
    with pytest.raises(ValueError): io.certificate_admission(*args)


def test_identity_reader(tmp_path):
    path = tmp_path/'artifact.json'
    path.write_text('{"value": 1}')
    with pytest.raises(ValueError): io.bound(tmp_path, dict(file=path.name, sha256='wrong'))
    with pytest.raises(ValueError): io.bound(tmp_path, dict(file='../artifact.json', sha256='wrong'))
    path.write_text('{"value": 1e999}')
    with pytest.raises(ValueError): io.bound(tmp_path, dict(file=path.name, sha256=m.obs.sha(path)))


def test_saved_path_no_solver(run, monkeypatch):
    def forbidden(*args, **kwargs): raise AssertionError('solver invoked')
    import scipy.integrate
    from puckworks.models.grudeva2026 import reduced
    from puckworks.analysis import grudeva2026_bed_accuracy_004 as comparator
    monkeypatch.setattr(scipy.integrate, 'solve_ivp', forbidden)
    monkeypatch.setattr(reduced, 'solve_ivp', forbidden)
    monkeypatch.setattr(comparator, 'run', forbidden, raising=False)
    assert m.compare(run, run)[0]['disposition'] == m.AGREEMENT


def test_manufactured_execute_path_no_solver(run, monkeypatch, tmp_path):
    def forbidden(*args, **kwargs): raise AssertionError('solver invoked')
    from puckworks.models.grudeva2026 import reduced
    from puckworks.analysis import grudeva2026_bed_accuracy_004 as comparator
    monkeypatch.setattr(reduced, 'solve_ivp', forbidden)
    monkeypatch.setattr(comparator, 'run', forbidden)
    contract = tmp_path/'contract.json'
    contract.write_text('{"implementation": {}}')
    review = tmp_path/'review.json'
    review.write_text(json.dumps(dict(passed=True, nonhuman=True,
                                     contract_sha256=m.obs.sha(contract), implementation={})))
    ci = tmp_path/'ci.json'
    ci.write_text('{}')
    monkeypatch.setattr(io, 'check_contract', lambda value: None)
    monkeypatch.setattr(io, 'integration', lambda value: [])
    for name in ('admit_production', 'admit_comparator'):
        monkeypatch.setattr(io, name, lambda *args: (copy.deepcopy(run), dict(qualified=True)))
    args = SimpleNamespace(evidence=tmp_path, output=tmp_path/'attempt', contract=contract,
                           review=review, integration=ci, admission_only=False)
    result = io.execute(args)
    assert result['complete'] and result['disposition'] == m.AGREEMENT
    assert [p['pair'] for p in result['pairs']] == [p[0] for p in m.PAIRS]
    records = [json.loads(line) for line in (args.output/'ledger.jsonl').read_text().splitlines()]
    assert [r['event'] for r in records] == ['start', 'end']
    assert all(r['production_simulations'] == r['comparator_simulations'] == 0 for r in records)


def test_cli_implementation_failure(tmp_path, monkeypatch):
    monkeypatch.setattr(io, 'execute', lambda args: (_ for _ in ()).throw(ValueError('bad contract')))
    assert m.main(['--evidence', str(tmp_path), '--output', str(tmp_path/'new'),
                   '--integration', str(tmp_path/'ci')]) == 1


@pytest.fixture
def contract(tmp_path, monkeypatch):
    t, z = m.support()
    path = tmp_path/'support.json'
    path.write_text(json.dumps(dict(times=t.tolist(), z=z.tolist(), history_z=list(m.obs.HISTORY_Z))))
    monkeypatch.setattr(m, 'DOCS', tmp_path)
    monkeypatch.setattr(io, 'ROOT', tmp_path)
    monkeypatch.setattr(m.obs, 'environment', lambda: {})
    read = io.READ
    monkeypatch.setattr(io, 'READ', lambda p: {'parameters': {'declared': 1}} if p == io.QDOC/'PLAN.json' else read(p))
    source = tmp_path/'source.py'
    source.write_text('historical source')
    return dict(task=m.TASK, pairs=[list(p) for p in m.PAIRS], limits=m.LIMITS.copy(),
                sign='PRODUCTION_MINUS_COMPARATOR', normalization='phi_T*L*A*c_sat', units='dimensionless',
                support=m.support_identity(), parameters={'declared': 1}, canonical_physics=m.CANONICAL_PHYSICS.copy(),
                support_file=dict(file=path.name, sha256=m.obs.sha(path)), environment={}, exit_codes=m.EXIT_CODES.copy(),
                sources={'source.py': m.obs.sha(source)}, implementation={}, inputs=dict.fromkeys(['P0', 'P1', 'C0', 'C1']))


def test_manufactured_contract(contract):
    io.check_contract(contract)


@pytest.mark.parametrize('field', ['task', 'pairs', 'limits', 'sign', 'normalization', 'units', 'support',
                                 'parameters', 'canonical_physics', 'environment', 'exit_codes', 'sources', 'inputs'])
def test_wrong_contract_refused(contract, field):
    contract[field] = {} if isinstance(contract[field], dict) else 'wrong'
    if field == 'sources': contract[field] = {'source.py': 'wrong'}
    if field == 'environment': contract[field] = {'python': 'wrong'}
    with pytest.raises(ValueError): io.check_contract(contract)


@pytest.mark.parametrize('field', ['task', 'row', 'attempt', 'plan_sha256', 'controls', 'metadata', 'observations'])
def test_wrong_production_reuse_refused(tmp_path, monkeypatch, field):
    item = dict(task='manufactured006', row='spatial_512', attempt='006-spatial-512',
                plan_sha256='plan', controls=io.qualification.BASE, metadata={'id': 'meta'}, observations={'id': 'obs'})
    original = copy.deepcopy(item)
    meta = dict(task=item['task'], row=item['row'], attempt=item['attempt'], matrix_sha256='plan')
    plan = dict(reuse=dict(metadata=original['metadata'], observations=original['observations']))
    monkeypatch.setattr(io, 'READ', lambda p: plan)
    monkeypatch.setattr(io, 'accepted_qualification', lambda root: ({}, {}))
    monkeypatch.setattr(io.qualification, 'baseline_inputs', lambda *a, **k: meta)
    item[field] = 'wrong'
    with pytest.raises(ValueError): io.admit_production('P0', tmp_path, dict(inputs={'P0': item}))
