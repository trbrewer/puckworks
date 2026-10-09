"""Manufactured offline cases only: no owner archives or canonical simulations."""
from copy import deepcopy
import json
from types import SimpleNamespace

import numpy as np
import pytest

from puckworks.analysis import grudeva2026_publication_reconciliation_009 as s
from puckworks.analysis import grudeva2026_publication_reconciliation_009_io as io


@pytest.fixture
def fixture():
    return json.loads((s.ROOT/s.FIXTURE).read_text())


@pytest.fixture
def run(fixture):
    ts = sorted({r['t'] for key in ('figure3', 'figure3_fronts', 'figure4') for r in fixture[key]})
    z = sorted({r['z'] for r in fixture['figure3']})
    fronts = {r['t']: r['z'] for r in fixture['figure3_fronts']}
    profiles = {(r['t'], r['z']): r['c'] for r in fixture['figure3']}
    outlet = {r['t']: r['c'] for r in fixture['figure4']}
    arrival = fixture['figure4_event']['t']
    return dict(z=z, arrival=arrival,
                records=[[t, fronts.get(t, 1.), outlet.get(t, 0.), 0., 0., 0., 0., 0.] for t in ts],
                observations=[dict(t=t, liquid_profile=[profiles.get((t, x), 0.) for x in z]) for t in ts],
                events=[dict(kind='first_drip', t=1., outlet_left=0., outlet_right=1.),
                        dict(kind='desaturation_exit', t=arrival, outlet_left=1., outlet_right=.3)])


def scored(run, fixture, key='P0'):
    return s.score_input(key, run, dict(qualified=True), fixture)


def row(result, target):
    return next(r for r in result['rows'] if r['target_id'] == target)


def adjust(run, fixture, target_id, value):
    target = next(t for t in s.targets(fixture) if t['target_id'] == target_id)
    family = target['family']
    if family == 'figure4_arrival':
        run['arrival'] = value
        run['events'][1]['t'] = value
        return
    i = next(i for i, r in enumerate(run['observations']) if r['t'] == target['coordinates']['t'])
    if family == 'figure3_concentration':
        j = run['z'].index(target['coordinates']['z'])
        run['observations'][i]['liquid_profile'][j] = value
    else:
        run['records'][i][1 if family == 'figure3_front' else 2] = value


def test_target_inventory_order_and_boundaries(fixture):
    targets = s.targets(fixture)
    assert len(targets) == 31
    assert {f: sum(t['family'] == f for t in targets) for f in s.LIMITS} == s.COUNTS
    assert [t['target_id'] for t in targets[:3]] == ['F3C-001', 'F3C-002', 'F3C-003']
    assert sum(t['family'] == 'figure3_front' and t['coordinates']['t'] == 6.4 for t in targets) == 0
    assert all(t['curve'] == s.CURVE and t['units'] == 'dimensionless' for t in targets)


@pytest.mark.parametrize('change', ['curve', 'axes', 'count', 'nonfinite'])
def test_bad_fixture_structure(fixture, change):
    if change == 'curve': fixture['source']['curve_identity'] = 'epsilon=.01 full model'
    if change == 'axes': fixture['source']['axes'] = 'seconds'
    if change == 'count': fixture['figure3'].pop()
    if change == 'nonfinite': fixture['figure3'][0]['c'] = np.nan
    with pytest.raises(ValueError): s.targets(fixture)


def test_exact_124_rows_and_partition(run, fixture):
    report = s.assess({k: run for k in s.INPUTS}, {k: dict(qualified=True) for k in s.INPUTS}, fixture)
    assert report['complete'] and report['exit_code'] == 0
    assert report['primary_outcome'] == s.AGREEMENT
    assert sum(len(x['rows']) for x in report['inputs'].values()) == 124
    for x in report['inputs'].values():
        for f in x['families'].values():
            assert f['requested'] == f['included'] + f['excluded'] + f['unavailable']
            assert f['status'] == 'PASS'


def test_qualified_profile_not_legacy(run, fixture):
    run['liquid_profiles'] = [[999.]]
    i = next(i for i, x in enumerate(run['observations']) if x['t'] == 3.2)
    run['observations'][i]['legacy_liquid_profile'] = [999.]*len(run['z'])
    assert row(scored(run, fixture), 'F3C-004')['signed_residual'] == 0
    run['observations'][i].pop('liquid_profile')
    r = row(scored(run, fixture), 'F3C-004')
    assert r['status'] == 'UNAVAILABLE' and r['model'] is None
    assert 'legacy' in r['reason']


@pytest.mark.parametrize('family,boundary', [('figure3_concentration', 'model_front'),
                                            ('figure4_concentration', 'model_arrival')])
@pytest.mark.parametrize('direction', [-1, 1])
def test_displacement_masks_both_directions_and_closed_edges(fixture, family, boundary, direction):
    target = next(t for t in s.targets(fixture) if t['family'] == family and t['coordinates'].get('t') != .4)
    reference = fixture['figure3_fronts'][1]['z'] if family.startswith('figure3') else fixture['figure4_event']['t']
    model = reference+direction*.1
    excluded, mask = s.publication_mask(target, {boundary: model}, fixture)
    axis = mask['axis']
    for x in (mask['low'], mask['high'], (model+reference)/2):
        target['coordinates'][axis] = x
        assert s.publication_mask(target, {boundary: model}, fixture)[0]
    for x in (np.nextafter(mask['low'], -np.inf), np.nextafter(mask['high'], np.inf)):
        target['coordinates'][axis] = x
        assert not s.publication_mask(target, {boundary: model}, fixture)[0]


def test_post_exit_boundary_no_intermethod_override(fixture):
    target = next(t for t in s.targets(fixture) if t['target_id'] == 'F3C-019')
    excluded, mask = s.publication_mask(target, dict(model_front=1.), fixture)
    assert excluded and mask['reference_boundary'] == 1.
    assert 'NOT_MEASURED' in mask['convention']
    assert len(fixture['figure3_fronts']) == 3
    fixture['figure3_fronts'].append(dict(t=6.4, z=1.))
    with pytest.raises(ValueError): s.publication_mask(target, dict(model_front=1.), fixture)


@pytest.mark.parametrize('family', list(s.LIMITS))
def test_acceptance_limit_is_inclusive_full_precision(run, fixture, family):
    target = next(t for t in s.targets(fixture) if t['family'] == family and
                  t['target_id'] not in ('F3C-001', 'F3C-002', 'F3C-003'))
    # Use binary-exact residuals to test the comparator itself, without decimal subtraction drift.
    fixture_key = dict(figure3_concentration='figure3', figure3_front='figure3_fronts',
                       figure4_concentration='figure4', figure4_arrival='figure4_event')[family]
    index = int(target['target_id'][-3:])-1
    entry = fixture[fixture_key] if family == 'figure4_arrival' else fixture[fixture_key][index]
    field = 't' if family == 'figure4_arrival' else 'z' if family == 'figure3_front' else 'c'
    entry[field] = 0.
    adjust(run, fixture, target['target_id'], s.LIMITS[family])
    r = row(scored(run, fixture), target['target_id'])
    assert r['status'] == 'PASS' and r['absolute_residual'] == s.LIMITS[family]
    adjust(run, fixture, target['target_id'], np.nextafter(s.LIMITS[family], np.inf))
    assert row(scored(run, fixture), target['target_id'])['status'] == 'FAIL'


@pytest.mark.parametrize('change', ['missing', 'empty', 'nan', 'inf', 'misalignment', 'duplicate', 'near_duplicate', 'wrong_z', 'duplicate_z'])
def test_unavailable_before_exclusion(run, fixture, change):
    # F3C-001 is masked in this manufactured exact-reference case.
    i = next(i for i, o in enumerate(run['observations']) if o['t'] == .4)
    j = run['z'].index(fixture['figure3'][0]['z'])
    if change == 'missing': run['observations'][i].pop('liquid_profile')
    if change == 'empty': run['records'] = []; run['observations'] = []
    if change in ('nan', 'inf'): run['observations'][i]['liquid_profile'][j] = float(change)
    if change == 'misalignment': run['records'][i][0] += .01
    if change in ('duplicate', 'near_duplicate'):
        run['records'].insert(i+1, deepcopy(run['records'][i]))
        run['observations'].insert(i+1, deepcopy(run['observations'][i]))
        if change == 'near_duplicate':
            run['records'][i+1][0] += 1e-13; run['observations'][i+1]['t'] += 1e-13
    if change == 'wrong_z': run['z'][j] += 1e-14
    if change == 'duplicate_z': run['z'][j+1] = run['z'][j]
    r = row(scored(run, fixture), 'F3C-001')
    assert r['status'] == 'UNAVAILABLE' and r['model'] is None and r['reason']


def test_matching_allowance_no_nearby_substitution(run, fixture):
    i = next(i for i, o in enumerate(run['observations']) if o['t'] == 3.2)
    for offset, status in [(1e-13, 'PASS'), (3e-13, 'UNAVAILABLE')]:
        run['records'][i][0] = run['observations'][i]['t'] = 3.2+offset
        assert row(scored(run, fixture), 'F3C-004')['status'] == status
    assert s.unique_match([0.], s.TIME_ATOL, s.TIME_ATOL) == 0
    with pytest.raises(ValueError): s.unique_match([0.], np.nextafter(s.TIME_ATOL, np.inf), s.TIME_ATOL)


@pytest.mark.parametrize('prerequisite', ['front', 'arrival', 'events'])
def test_missing_mask_prerequisite(run, fixture, prerequisite):
    target = 'F4C-001'
    if prerequisite == 'front':
        run['records'][0][1] = np.nan
        target = 'F3C-001'
    if prerequisite == 'arrival': run['arrival'] = None
    if prerequisite == 'events': run['events'] = []
    assert row(scored(run, fixture), target)['classification'] == 'UNAVAILABLE'


@pytest.mark.parametrize('change', ['event_record', 'event_side', 'observations'])
def test_malformed_record_objects_stay_unavailable(run, fixture, change):
    if change == 'event_record': run['events'] = [None, None]
    if change == 'event_side': run['events'][1]['sides'] = [None, None]
    if change == 'observations': run['observations'] = [None]
    r = row(scored(run, fixture), 'F4C-001')
    assert r['status'] == 'UNAVAILABLE' and r['model'] is None


def test_limits_not_008_policy_and_exclusions_not_passes(run, fixture):
    target = fixture['figure3'][3]
    adjust(run, fixture, 'F3C-004', target['c']+.005)
    report = scored(run, fixture)
    assert row(report, 'F3C-004')['status'] == 'PASS'  # exceeds 008's .001
    excluded = row(report, 'F3C-001')
    assert excluded['status'] == 'EXCLUDED'
    adjust(run, fixture, 'F3C-001', 100.)
    assert scored(run, fixture)['families']['figure3_concentration']['max_absolute'] < .006


@pytest.mark.parametrize('kind', ['shared', 'different_target', 'opposite', 'support_difference'])
def test_shared_witness_requires_same_included_target_and_direction(run, fixture, kind):
    p, c = deepcopy(run), deepcopy(run)
    adjust(p, fixture, 'F4C-005', fixture['figure4'][4]['c']+.03)
    key = 'F4C-006' if kind == 'different_target' else 'F4C-005'
    adjust(c, fixture, key, fixture['figure4'][int(key[-3:])-1]['c']+(-.03 if kind == 'opposite' else .03))
    if kind == 'support_difference': adjust(c, fixture, 'F4A-001', 6.7)
    r = s.pair_summary(scored(p, fixture), scored(c, fixture, 'C0'))
    assert r['shared_discrepancy'] == (kind == 'shared')
    if kind == 'support_difference': assert r['families']['figure4_concentration']['support_differences']


def test_refinement_mixed_and_incomplete_preserve_primary_shared(run, fixture):
    runs = {k: deepcopy(run) for k in s.INPUTS}
    admissions = {k: dict(qualified=True) for k in s.INPUTS}
    for k in ('P0', 'C0'): adjust(runs[k], fixture, 'F4C-005', .2)
    report = s.assess(runs, admissions, fixture)
    assert report['complete'] and report['primary_outcome'] == s.SHARED and report['mixed_findings']
    assert report['refinement_outcomes']['P1'] == 'PASS'
    assert report['refinement_outcomes']['family_verdict_changes']
    runs['P0']['observations'][0].pop('liquid_profile')
    report = s.assess(runs, admissions, fixture)
    assert not report['complete'] and report['exit_code'] == 3
    assert report['primary_outcome'] == s.SHARED and report['shared_discrepancy']
    admissions['P0']['qualified'] = False
    report = s.assess(runs, admissions, fixture)
    assert report['primary_outcome'] == s.INCOMPLETE and not report['shared_discrepancy']


def test_empty_family_cannot_pass_and_failure_survives_incompleteness(run, fixture):
    result = scored(run, fixture)
    rows = [r for r in result['rows'] if r['family'] == 'figure4_concentration']
    rows[0].update(status='FAIL', absolute_residual=.5)
    rows[1].update(classification='UNAVAILABLE', status='UNAVAILABLE')
    summary = s.summarize(rows)
    assert summary['qualified_failure'] and summary['status'] == 'INCOMPLETE'
    for r in rows: r.update(classification='EXCLUDED', status='EXCLUDED')
    assert s.summarize(rows)['status'] == 'INCOMPLETE'


def test_same_fail_labels_do_not_hide_changed_refinement_witnesses(run, fixture):
    runs = {k: deepcopy(run) for k in s.INPUTS}
    for k in s.INPUTS:
        adjust(runs[k], fixture, 'F4C-005' if k.endswith('0') else 'F4C-006', .2)
    r = s.assess(runs, {k: dict(qualified=True) for k in s.INPUTS}, fixture)
    assert r['primary_outcome'] == s.SHARED and r['mixed_findings']
    assert not r['refinement_outcomes']['family_verdict_changes']
    persistence = r['refinement_outcomes']['witness_persistence']['figure4_concentration']
    assert persistence == dict(persistent_shared_ids=[], direction_changed_shared_ids=[], primary_only_shared_ids=['F4C-005'],
                               refinement_only_shared_ids=['F4C-006'])


def test_shared_sign_reversal_is_not_persistent_discrepancy(run, fixture):
    runs = {k: deepcopy(run) for k in s.INPUTS}
    for k in s.INPUTS:
        adjust(runs[k], fixture, 'F4C-005', fixture['figure4'][4]['c']+(.03 if k.endswith('0') else -.03))
    r = s.assess(runs, {k: dict(qualified=True) for k in s.INPUTS}, fixture)
    persistence = r['refinement_outcomes']['witness_persistence']['figure4_concentration']
    assert persistence['persistent_shared_ids'] == []
    assert persistence['direction_changed_shared_ids'] == ['F4C-005']
    assert r['mixed_findings'] and r['primary_outcome'] == s.SHARED


def test_arithmetic_and_exact_tie_reporting(run, fixture):
    for p, c, ref in [(1e12, 1e12+.1, .2), (.001, .003, 1.), (0., 0., 0.)]:
        assert s.residual_identity(p, c, ref)['identity_passed']
    rows = scored(run, fixture)['rows'][22:24]
    for r in rows: r.update(classification='INCLUDED', absolute_residual=.125, signed_residual=.125, status='FAIL')
    assert [r['target_id'] for r in s.summarize(rows)['maxima']] == ['F4C-001', 'F4C-002']
    rows[1]['absolute_residual'] = np.nextafter(.125, np.inf)
    assert [r['target_id'] for r in s.summarize(rows)['maxima']] == ['F4C-002']


def test_front_arrival_scores_survive_concentration_masks(run, fixture):
    adjust(run, fixture, 'F3F-002', .1)
    adjust(run, fixture, 'F4A-001', 7.)
    r = scored(run, fixture)
    assert row(r, 'F3F-002')['status'] == row(r, 'F4A-001')['status'] == 'FAIL'
    assert row(r, 'F3C-004')['status'] == row(r, 'F4C-001')['status'] == 'EXCLUDED'


def test_frozen_contract_and_historical_preservation(monkeypatch):
    contract = io.READ(s.DOCS/'CONTRACT.json')
    monkeypatch.setattr(io.obs, 'environment', lambda: contract['environment'])
    old, fixture = io.check_contract(contract)
    assert old['inputs']['P1']['certificate']['sha256'] == '79fdadc149c89eed161d5bc62433e6ad5d2a512fa6b2ab46e2f683168f03f31c'
    bindings = io.READ(s.ROOT/io.PRIOR/'EVIDENCE_BINDINGS.json')['verified_numerical_contents']['P1']
    assert bindings['segments'][2]['original_numerical_replay'] == 'FAILED'
    assert bindings['original_failed_metadata_preserved'] and bindings['observation_origin'] == 'DIAGNOSTIC_ONLY'
    assert fixture['figure5']['status'] == 'FIG5_REFERENCE_INCOMPLETE'


@pytest.mark.parametrize('change', ['fixture', 'input', 'coordinates', 'order', 'policy', 'base'])
def test_contract_identity_rejection(monkeypatch, change):
    contract = io.READ(s.DOCS/'CONTRACT.json')
    monkeypatch.setattr(io.obs, 'environment', lambda: contract['environment'])
    if change == 'fixture': contract['fixture']['sha256'] = '0'*64
    if change == 'input': contract['inputs']['P0']['attempt'] = 'repeat'
    if change == 'coordinates': contract['targets'][0]['coordinates']['z'] += .001
    if change == 'order': contract['targets'].reverse()
    if change == 'policy': contract['limits']['figure3_concentration'] = .1
    if change == 'base': contract['base']['head'] = io.BASE['parents'][0]
    with pytest.raises(ValueError): io.check_contract(contract)


@pytest.mark.parametrize('change', ['old_receipt', 'head', 'attempt', 'job', 'pending', 'coverage'])
def test_integration_rejects_previous_merge_or_incomplete_jobs(change):
    receipt = io.READ(s.DOCS/'INTEGRATION.json')
    if change == 'old_receipt': receipt = io.READ(s.ROOT/io.PRIOR/'INTEGRATION.json')
    if change == 'head': receipt['workflow_runs'][0]['head_sha'] = io.BASE['parents'][1]
    if change == 'attempt': receipt['workflow_runs'][0]['jobs_evidence']['jobs'][0]['run_attempt'] += 1
    if change == 'job': receipt['workflow_runs'][0]['jobs_evidence']['jobs'][0]['conclusion'] = 'failure'
    if change == 'pending': receipt['workflow_runs'][0]['status'] = 'in_progress'
    if change == 'coverage': receipt['workflow_runs'].pop()
    with pytest.raises((ValueError, KeyError)): io.integration(receipt)


def test_review_must_bind_actual_freeze():
    contract = io.READ(s.DOCS/'CONTRACT.json')
    review = dict(passed=True, nonhuman=True, contract_sha256='wrong', implementation=contract['implementation'])
    with pytest.raises(ValueError): io.check_review(review, contract, io.obs.sha(s.DOCS/'CONTRACT.json'))


def test_execution_is_offline_and_nonoverwriting(tmp_path, monkeypatch, run, fixture):
    from puckworks.models.grudeva2026 import reduced, verification
    from puckworks.analysis import grudeva2026_reference_002 as reference
    from puckworks.analysis import grudeva2026_bed_accuracy_004 as bed
    from puckworks.analysis import grudeva2026_replay_certificate_007 as certificate
    def forbidden(*args, **kwargs): raise AssertionError('solver/008/certification invoked')
    for module, names in [(reduced, ['simulate', 'solve_ivp']), (verification, ['simulate']),
                          (reference, ['simulate']), (bed, ['simulate']),
                          (io.admission, ['execute']), (s.prior, ['compare']),
                          (certificate, ['certify'])]:
        for name in names:
            if hasattr(module, name): monkeypatch.setattr(module, name, forbidden)
    contract = io.READ(s.DOCS/'CONTRACT.json')
    monkeypatch.setattr(io, 'check_contract', lambda c: (c, fixture))
    expected = io.READ(s.ROOT/io.PRIOR/'EVIDENCE_BINDINGS.json')['verified_numerical_contents']
    def loader(identity, *args): return run, expected[identity]
    monkeypatch.setattr(io.admission, 'admit_production', loader)
    monkeypatch.setattr(io.admission, 'admit_comparator', loader)
    review = tmp_path/'review.json'
    review.write_text(json.dumps(dict(passed=True, nonhuman=True, contract_sha256=io.obs.sha(s.DOCS/'CONTRACT.json'),
                                     implementation=contract['implementation'])))
    args = SimpleNamespace(evidence=tmp_path, output=tmp_path/'attempt', contract=s.DOCS/'CONTRACT.json',
                           integration=s.DOCS/'INTEGRATION.json', review=review)
    result = io.execute(args)
    assert result['complete'] and result['new_production_simulations'] == result['new_comparator_simulations'] == 0
    ledger = [json.loads(x) for x in (args.output/'ledger.jsonl').read_text().splitlines()]
    assert [x['event'] for x in ledger] == ['start', 'end'] and ledger[-1]['status'] == 'COMPLETED'
    with pytest.raises(FileExistsError): io.execute(args)
