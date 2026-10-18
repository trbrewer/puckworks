"""Source-independent tests; no retained model, private record or historical runner."""
from copy import deepcopy
from fractions import Fraction
import math

import numpy as np
import pytest

from puckworks.analysis import five_cqa_decision_resolution as m


def metric(r=1., b=.6, u=1e-10, windows=4):
    return dict(zip(m.METRICS, (r, b, abs(b), u, u, u)), windows=windows,
                assayed_beverage_kg=.02, observed_assayed_five_cqa_kg=.00002,
                predicted_assayed_five_cqa_kg=.00003)


def fixture_shots():
    data = {}
    for panel, cs in m.PANELS.items():
        data[panel] = {}
        for ai, arm in enumerate(m.ARMS):
            rows = []
            for i, (shot, condition) in enumerate(m.members(cs).items()):
                n = 3 if shot == 'PRED-E07-R1' else 4
                v = metric(1 + i / 20 - ai / 10, .6 - ai / 20, windows=n)
                full = v if n == 4 else None
                rows.append({'shot': shot, 'condition': condition, 'full': full, 'bounds': m.metric_bounds(full),
                             'supported_subset_diagnostic': v, 'coverage': {'intended': 4, 'supported': n, 'qualified': n}})
            data[panel][arm] = rows
    return data


def fraction_rows(errors, masses, allowances=None):
    allowances = allowances or [0.] * len(errors)
    observed = [{'shot': 'synthetic', 'fraction': i, 'mass_kg': mass, 'q': .001, 'supported': True}
                for i, mass in enumerate(masses)]
    predicted = [{'shot': 'synthetic', 'fraction': i, 'five_cqa_mg_g': 1 + e,
                  'allowance_kg': u, 'supported': True, 'numerical_qualified': True}
                 for i, (e, u) in enumerate(zip(errors, allowances))]
    return observed, predicted


def test_unequal_masses_units_and_allowances():
    o, p = fraction_rows([1., -1.], [.001, .003], [1e-8, 6e-8])
    result, v, detail = m.fraction_metric(o, p)
    assert result['R_mg_g'] == 1
    assert result['B_mg_g'] == -.5 and v == .75
    assert result['R_allowance_mg_g'] == pytest.approx(math.sqrt(.25 * .01**2 + .75 * .02**2))
    assert result['B_allowance_mg_g'] == pytest.approx(.0175)
    assert detail['weights'] == [.25, .75]
    # Deliberately inconsistent delivered mass is irrelevant: stored concentration controls.
    p[0]['five_cqa_kg'] = 1000
    assert m.fraction_metric(o, p)[0] == result


@pytest.mark.parametrize('errors,masses,b,v', [([2, 2], [1, 3], 2, 0),
                                                ([3, -1], [1, 3], 0, 3)])
def test_constant_and_zero_mean_residuals(errors, masses, b, v):
    result, variation, _ = m.fraction_metric(*fraction_rows(errors, masses))
    assert result['B_mg_g'] == b and variation == v
    assert result['R_mg_g']**2 == pytest.approx(b*b+v)


def test_absolute_bias_before_mean_and_average_squares():
    values = [metric(1, .5), metric(2, -.5)]
    result = m.mean_metrics(values)
    assert result['B_mg_g'] == 0 and result['absB_mg_g'] == .5
    assert np.mean([m.shot_components(v)['B2'] for v in values]) == .25
    assert np.mean([m.shot_components(v)['R2'] for v in values]) == 2.5
    assert result['R_mg_g']**2 != 2.5


def test_nested_deletion_not_pooled():
    shots = fixture_shots()['temperature_stress']['L1M']
    for r, x in zip(shots, range(1, 7)):
        r['full'] = metric(x)
    result = m.aggregate(shots, m.PANELS['temperature_stress'], shots[0]['shot'])
    assert result['full_scope_metrics']['R_mg_g'] == 3.75
    assert result['original_shots'] == 6
    assert np.mean(range(2, 7)) == 4


def test_entire_paired_family_and_independent_identity():
    shots = m.validate_shots(fixture_shots())
    public, private, error = m.analyze(shots)
    assert error < 1e-14
    for panel, n in [('primary', 12), ('temperature_stress', 6)]:
        assert len(private[panel]['deletions']) == n
        assert public[panel]['actual_shots_per_deletion'] == n-1
        for s in private[panel]['deletions']:
            assert len(s['retained_members']) == n-1 and s['scored_windows_per_arm'] == 4*(n-1)
            assert s['deleted'] not in s['retained_members']
            for c in s['comparisons'].values():
                assert len(c['paired_shots']) == n-1
                assert c[m.CB] + c[m.CV] == pytest.approx(c['R_improvement_mg_g'])
                assert c['candidate_adequacy'] == 'FAIL'
                if panel == 'temperature_stress':
                    assert 'condition_wins' not in c['components']
                    assert c['status'] == 'SECONDARY_DIAGNOSTIC'


def test_public_projection_has_no_deletion_vectors_or_condition_ranges():
    public, _, _ = m.analyze(fixture_shots())
    forbidden = {'paired_shots', 'deleted', 'retained_members', 'shot', 'candidate', 'reference', 'conditions'}
    def walk(x):
        if isinstance(x, dict):
            assert not (set(x) & forbidden)
            for v in x.values():
                walk(v)
        elif isinstance(x, list):
            for v in x:
                walk(v)
    walk(public)
    for panel in public.values():
        for comp in panel['deletions'].values():
            assert 'condition_contrasts' not in comp


def test_opposing_contributions_on_rmse_scale():
    pair = m.paired_shot(metric(1, .9), metric(2, 0))
    assert pair[m.CB] == pytest.approx(-.27)
    assert pair[m.CV] == pytest.approx(1.27)
    assert pair[m.CB]+pair[m.CV] == pytest.approx(1)


@pytest.mark.parametrize('a,b', [([-2., 3.], [1., 4.]), ([-3., -2.], [.25, 2.]), ([0., 2.], [.5, 3.])])
def test_outward_signed_division_exact_rationals(a, b):
    result = m.divide(a, b)
    exact = [Fraction(x)/Fraction(y) for x in a for y in b]
    assert Fraction(result[0]) <= min(exact) and Fraction(result[1]) >= max(exact)
    for fn, exact_values in [(m.add, [Fraction(a[0])+Fraction(b[0]), Fraction(a[1])+Fraction(b[1])]),
                             (m.subtract, [Fraction(a[0])-Fraction(b[1]), Fraction(a[1])-Fraction(b[0])])]:
        result = fn(a, b)
        assert Fraction(result[0]) <= exact_values[0] and Fraction(result[1]) >= exact_values[1]


@pytest.mark.parametrize('values,expected', [([-2., 3.], [0., 9.]), ([-3., -2.], [4., 9.]), ([2., 3.], [4., 9.])])
def test_signed_square(values, expected):
    result = m.square(values)
    assert result[0] <= expected[0] and result[1] >= expected[1]
    if expected[0] == 0:
        assert result[0] == 0


def test_negative_point_variation_not_excused_by_allowance():
    with pytest.raises(m.IntegrityError, match='NEGATIVE_POINT'):
        m.shot_components(metric(.5, 1., 100.))
    point = m.shot_components(metric(1, math.nextafter(1, math.inf), .01))
    assert point['V'] == 0 and point['negative_roundoff_clamped']


def test_relaxed_negative_V_endpoint_not_negative_point():
    c = m.shot_components(metric(1, 1, .1))
    assert c['V'] == 0 and c['V_unconstrained_bounds'][0] < 0 and c['V_bounds'][0] == 0


def test_exact_zero_point_and_zero_containing_denominator():
    zero = m.paired_shot(metric(0, 0, 0), metric(0, 0, 0))
    assert zero[m.CB] == zero[m.CV] == 0
    assert zero[m.CB+'_bounds'] == zero[m.CV+'_bounds'] == [0, 0]
    unresolved = m.paired_shot(metric(0, 0, .1), metric(0, 0, .1))
    assert unresolved[m.CB] == unresolved[m.CV] == 0
    assert unresolved[m.CB+'_bounds'] is unresolved[m.CV+'_bounds'] is None
    assert m.divide([-1, 2], [0, 1]) is None


@pytest.mark.parametrize('v,u,t,status', [(1, 0, 1, 'PASS'), (1.1, .1, 1, 'UNRESOLVED'),
                                        (1.2, .1, 1, 'FAIL'), (None, None, 1, 'INCOMPLETE_SUPPORT')])
def test_historical_inclusive_limits(v, u, t, status):
    assert m.upper(v, u, t) == status


def test_conjunction_and_strict_wins_and_zero_reference_relative_rule():
    assert m.conjunction(['FAIL', 'INCOMPLETE_SUPPORT']) == 'FAIL'
    assert m.conjunction(['UNRESOLVED', 'INCOMPLETE_SUPPORT']) == 'INCOMPLETE_SUPPORT'
    assert m.conjunction(['PASS', 'PASS']) == 'PASS'
    rows = fixture_shots()['primary']['L1M']
    for row in rows:
        row['full'] = metric(0, 0, 0)
    panel = m.aggregate(rows, m.PANELS['primary'])
    comp = m.comparison(panel, panel)
    assert comp['definite_condition_wins'] == comp['possible_condition_wins'] == 0
    assert comp['components']['relative_gain'] == 'PASS'  # Historical 5CQA, unlike caffeine.
    assert comp['relative_improvement'] is None and comp['relative_improvement_lower_bound'] is None
    a, b = deepcopy(panel), deepcopy(panel)
    for c in a['conditions']:
        a['conditions'][c]['full_scope_metrics'] = metric(.25, 0, .125)
        b['conditions'][c]['full_scope_metrics'] = metric(.5, 0, .125)
    comp = m.comparison(a, b)
    assert comp['definite_condition_wins'] == 0 and comp['possible_condition_wins'] == 4


def test_relative_ratio_guard_does_not_change_component():
    rows = fixture_shots()['primary']['L1M']
    for row in rows:
        row['full'] = metric(.1, 0, .2)
    panel = m.aggregate(rows, m.PANELS['primary'])
    comp = m.comparison(panel, panel)
    assert comp['relative_improvement'] == 0
    assert comp['relative_improvement_lower_bound'] is None
    assert comp['components']['relative_gain'] == 'UNRESOLVED'


def test_incomplete_flow_original_denominator_failure_witness():
    rows = fixture_shots()['flow_stress']['L1M'][:3]
    for row in rows[1:]:
        row['full'] = metric(.24, .24, 0)
    result = m.condition_result(rows)
    assert result['full_scope_metrics'] is None and result['adequacy'] == 'FAIL'
    assert result['complete_shot_full_condition_lower_bounds']['absB_mg_g'] == .16
    for row in rows[1:]:
        row['full'] = metric(.1, .1, 0)
    assert m.condition_result(rows)['adequacy'] == 'INCOMPLETE_SUPPORT'


@pytest.mark.parametrize('mutation', ['missing', 'duplicate', 'condition', 'arm', 'panel', 'nan', 'allowance', 'coverage', 'field'])
def test_invalid_shot_records_rejected(mutation):
    data = fixture_shots(); rows = data['primary']['L1M']
    if mutation == 'missing': rows.pop()
    elif mutation == 'duplicate': rows[-1] = deepcopy(rows[0])
    elif mutation == 'condition': rows[0]['condition'] = 'PRED-C03'
    elif mutation == 'arm': data['primary'].pop('L12')
    elif mutation == 'panel': data['extra'] = data['primary']
    elif mutation == 'nan': rows[0]['full']['R_mg_g'] = float('nan')
    elif mutation == 'allowance': rows[0]['full']['R_allowance_mg_g'] = -1
    elif mutation == 'coverage': rows[0]['coverage']['intended'] = 3
    elif mutation == 'field': rows[0]['support_diagnostic'] = rows[0].pop('supported_subset_diagnostic')
    with pytest.raises((m.IntegrityError, KeyError)):
        m.validate_shots(data)


def test_missing_scenario_record_is_not_intentional_deletion():
    rows = fixture_shots()['primary']['L1M']
    with pytest.raises(m.IntegrityError):
        m.aggregate(rows[:-1], m.PANELS['primary'], rows[0]['shot'])
    with pytest.raises(m.IntegrityError):
        m.aggregate(rows, m.PANELS['primary'], 'not-a-shot')


def test_policy_sensitivity_is_not_a_bound():
    public, private, _ = m.analyze(fixture_shots())
    policy = private['primary']['policy']['L12_vs_L1M:deletions']
    assert policy['evidence']['kind'] == 'sensitivity'
    assert len(policy['evidence']['basis']['tested_sensitivities']) == 12
    assert policy['resolution'] == 'UNRESOLVED' and policy['contractual'] == 'UNAVAILABLE'
    assert public['primary']['baseline']['L12_vs_L1M']['policy_interpretation']['resolution'] == 'PASS'


def synthetic_admission(tmp_path):
    root = tmp_path/'repo'; history = root/'docs/analysis/sci_md_5cqa_assay_002'
    history.mkdir(parents=True); directory = tmp_path/'retained'; directory.mkdir()
    data = {'shot_results.json': {}, 'scores.json': {'task': m.OLD_TASK},
            'predictions.json': {}, 'observed_suffix.json': [], 'states.json': {}}
    hashes = {}
    def save(n, v):
        m.write(directory/n, v); data[n] = v; hashes[n] = m.sha((directory/n).read_bytes())
    for n, v in list(data.items()): save(n, v)
    freeze = {'task': m.OLD_TASK, 'producer_commit': 'synthetic_commit', 'producer_tree': 'synthetic_tree',
              'arms': list(m.ARMS), 'panels': {p:list(cs) for p,cs in m.PANELS.items()},
              'artifacts': {n:hashes[n] for n in ['predictions.json','states.json']}}
    save('freeze.json', freeze)
    approval = {'task':m.OLD_TASK, 'status':'APPROVED', 'independent':True, 'unresolved_blocking_findings':[],
                'reviewed_head':'synthetic_commit', 'reviewed_tree':'synthetic_tree', 'freeze_sha256':hashes['freeze.json']}
    m.write(history/'INDEPENDENT_APPROVAL.json', approval)
    ah = m.sha((history/'INDEPENDENT_APPROVAL.json').read_bytes())
    save('score_receipt.json', {'task':m.OLD_TASK,'status':'STARTED','freeze_sha256':hashes['freeze.json'],
                              'review_sha256':ah,'predictions_sha256':hashes['predictions.json']})
    save('score_completion.json', {'task':m.OLD_TASK,'status':'COMPLETE','scientific_score_passes':1,
        'freeze_sha256':hashes['freeze.json'], 'review_sha256':ah,
        'files':{n:hashes[n] for n in ['scores.json','shot_results.json','observed_suffix.json','score_receipt.json']}})
    for n, name in m.FALLBACK.items(): (history/name).write_bytes((directory/n).read_bytes())
    manifest = {'input_byte_sha256':hashes, 'core_artifacts':['shot_results.json','scores.json','freeze.json','score_receipt.json','score_completion.json'],
        'historical_producer':'synthetic_commit','historical_tree':'synthetic_tree',
        'repository_file_byte_sha256':{str(p.relative_to(root)):m.sha(p.read_bytes()) for p in history.iterdir()}}
    return directory, history, root, manifest


def test_nested_chain_and_explicit_public_fallback(tmp_path):
    directory, history, root, manifest = synthetic_admission(tmp_path)
    for n in m.FALLBACK: (directory/n).unlink()
    data, availability, blockers = m.admit(directory, m.Inputs(), manifest, history=history, root=root)
    assert not blockers
    assert all(availability[n]['public_copy'] == public for n,public in m.FALLBACK.items())
    assert data['score_receipt.json']['status'] == 'STARTED'
    assert data['score_completion.json']['files']['shot_results.json'] == manifest['input_byte_sha256']['shot_results.json']


def test_present_mismatch_never_falls_back(tmp_path):
    directory, history, root, manifest = synthetic_admission(tmp_path)
    (directory/'scores.json').write_text('{}')
    data, available, blockers = m.admit(directory, m.Inputs(), manifest, history=history, root=root)
    assert 'scores.json' not in data and blockers
    assert available['scores.json']['status'] == 'INTEGRITY_BLOCKED'
    assert available['scores.json']['actual_sha256'] != available['scores.json']['expected_sha256']


@pytest.mark.parametrize('state', ['absent', 'mismatch'])
def test_optional_failure_scoped_without_core_block(tmp_path, state):
    directory, history, root, manifest = synthetic_admission(tmp_path)
    for n in ['predictions.json', 'observed_suffix.json', 'states.json']:
        if state == 'absent': (directory/n).unlink()
        else: (directory/n).write_text('{"changed":true}')
    data, available, blockers = m.admit(directory, m.Inputs(), manifest, history=history, root=root)
    assert not blockers and 'shot_results.json' in data
    assert all(n not in data for n in ['predictions.json', 'observed_suffix.json', 'states.json'])


def test_required_missing_record_blocks_empirical_core(tmp_path):
    directory, history, root, manifest = synthetic_admission(tmp_path)
    (directory/'shot_results.json').unlink()
    _, _, blockers = m.admit(directory, m.Inputs(), manifest, history=history, root=root)
    assert blockers[0]['artifact'] == 'shot_results.json'


def test_nested_completion_not_flat_caffeine_schema(tmp_path):
    directory, history, root, manifest = synthetic_admission(tmp_path)
    data = {n:m.read(directory/n) for n in manifest['input_byte_sha256']}
    data['score_completion.json']['shot_results_sha256'] = data['score_completion.json'].pop('files')['shot_results.json']
    with pytest.raises(KeyError):
        m.authenticate_links(data, manifest, m.read(history/'INDEPENDENT_APPROVAL.json'))


def test_json_duplicate_nonfinite_and_changed_input(tmp_path):
    p = tmp_path/'record.json'
    for text in ['{"a":1,"a":2}', '{"a":NaN}']:
        p.write_text(text)
        with pytest.raises(m.IntegrityError): m.read(p)
    p.write_text('{}'); inputs = m.Inputs(); inputs.load(p, m.sha(p.read_bytes()))
    p.write_text('[]')
    with pytest.raises(m.IntegrityError): inputs.recheck()


def test_arithmetic_tolerance_never_relaxes_decision():
    delta = math.ulp(1.)
    diffs = m.differences(1+delta, 1.)
    assert m.reconciliation_summary(diffs)['pass']
    assert m.upper(1+delta, 0, 1.) == 'FAIL'
    assert not m.reconciliation_summary(m.differences('FAIL', 'PASS'))['pass']


def test_resolver_uses_declared_source_environment(monkeypatch, tmp_path):
    monkeypatch.setenv('PANNUSCH2024_MENDELEY_FULL_REPOSITORY', str(tmp_path))
    assert m.resolve_retained() == tmp_path/'5cqa-assay-002-evidence-20260929T163451Z/run-001'


def test_output_refuses_repository_and_source(tmp_path):
    with pytest.raises(m.IntegrityError): m.run(tmp_path, tmp_path/'new')
    with pytest.raises(m.IntegrityError): m.run(tmp_path, m.ROOT/'new')


def window_fixture():
    observed, predictions, states = [], {a: [] for a in m.ARMS}, {}
    for s, c in m.members(tuple(c for cs in m.PANELS.values() for c in cs)).items():
        for f in m.FRACTIONS:
            supported = (s, f) != ('PRED-E07-R1', 10)
            r = {'shot': s, 'condition': c, 'fraction': f, 'campaign': 'PREDICTION_2022_03',
                 'analyte': '5CQA', 'analyte_eligible': True, 'supported': supported,
                 'reason': '' if supported else 'OUTSIDE_COMMON_TRAINING_MASS_DOMAIN',
                 'b0': f*.005, 'b1': (f+1)*.005, 'mass_kg': .005, 'q': .001}
            observed.append(r)
            for ai, a in enumerate(m.ARMS):
                p = {k:v for k,v in r.items() if k != 'q'}
                p.update(five_cqa_mg_g=1.5-ai*.1 if supported else None, allowance_kg=1e-12 if supported else None,
                         numerical_qualified=supported, species='5CQA' if supported else None,
                         coordinate_allowance_kg=0., integration_start_kg=r['b0'], start_kg=r['b0'], end_kg=r['b1'],
                         units=[['concentration_display','mg/g'],['beverage','kg']], feature_extrapolation=[], model_sha256=a)
                predictions[a].append(p)
        for a in m.ARMS:
            names = {'L1M':['m1_kg','m2_kg','q1_kg_kg'], 'L2M':['m1_kg','m2_kg','q2_kg_kg'],
                     'L12':['m1_kg','m2_kg','q1_kg_kg','q2_kg_kg']}[a]
            states[a+':'+s] = {'species':'5CQA', 'model_sha256':a, 'feature_extrapolation':[],
                'inputs':dict.fromkeys(names, .1) | {'species':'5CQA','arm':a},
                'model':{'species':'5CQA','arm':a,'feature_order':names,'input_order':names,
                         'minima':[0.]*len(names),'maxima':[1.]*len(names)}}
    return observed, predictions, states


@pytest.mark.parametrize('mutation', ['missing','duplicate','species','campaign','support','coordinate','nonfinite'])
def test_optional_window_identity_failures(mutation):
    observed, predictions, _ = window_fixture()
    rows = predictions['L12']
    if mutation == 'missing': rows.pop()
    elif mutation == 'duplicate': rows[-1] = deepcopy(rows[0])
    elif mutation == 'species': rows[0]['species'] = 'caffeine'
    elif mutation == 'campaign': rows[0]['campaign'] = 'FIT_2021_12'
    elif mutation == 'support': rows[0]['supported'] = False
    elif mutation == 'coordinate': rows[0]['b0'] += .001
    elif mutation == 'nonfinite': rows[0]['five_cqa_mg_g'] = float('inf')
    with pytest.raises(m.IntegrityError): m.prediction_indexes(predictions)


def test_flags_from_either_optional_route_and_conflict():
    _, predictions, states = window_fixture()
    a, _ = m.detailed_flags(predictions=predictions)
    b, _ = m.detailed_flags(states=states)
    assert a == b and a['L12']['primary']['shots'] == 0
    states['L12:PRED-E01-R1']['inputs']['q1_kg_kg'] = 2.
    with pytest.raises(m.IntegrityError, match='FLAG_DOMAIN'):
        m.detailed_flags(states=states)
    states['L12:PRED-E01-R1']['feature_extrapolation'] = ['q1_kg_kg']
    assert m.detailed_flags(states=states)[0]['L12']['primary']['shots'] == 1
    with pytest.raises(m.IntegrityError, match='STATE_PREDICTION_FLAG'):
        m.detailed_flags(predictions, states)


def test_optional_direct_check_on_complete_synthetic_crosswalk():
    observed, predictions, _ = window_fixture()
    shots = fixture_shots()
    for panel in m.PANELS:
        for a in m.ARMS:
            for row in shots[panel][a]:
                o = [r for r in observed if r['shot'] == row['shot'] and r['supported']]
                p = [r for r in predictions[a] if r['shot'] == row['shot'] and r['supported']]
                values, _, _ = m.fraction_metric(o, p)
                row['supported_subset_diagnostic'].update(values)
    summary, _ = m.direct_check(observed, predictions, shots)
    assert summary['pass'] and summary['supported_prediction_slots'] == 285
    shots['primary']['L12'][0]['full']['R_mg_g'] += .01
    summary, _ = m.direct_check(observed, predictions, shots)
    assert not summary['pass']


def test_bound_parser_rejects_exponent_overflow():
    with pytest.raises(m.IntegrityError): m.parse('{"a":1e400}')
