"""Synthetic fixtures only. No original source rows or fitted values copied."""
from copy import deepcopy
import math

import pytest

from puckworks.analysis import grudeva_pooled_tail_delivery as p
from puckworks.analysis import grudeva_pooled_tail_scoring as s


def source_rows():
    rows = []
    for shot in range(1, 15):
        for vial in range(1, 19):
            mass = 0. if vial == 1 else 1.
            rows.append({'shot': shot, 'vial': vial, 'window': 'regular16' if vial <= 16 else 'terminal',
                         'mass_g': mass, 'tds_pct': None if mass == 0 else 10.,
                         'discrepancy_at_source_precision': False})
    return rows


def fixture(N=13):
    early, queries, support, cohort, pools = p.project(source_rows(), (.003, .004))
    if N != 13:
        for c in cohort[N:]:
            c['eligible'] = False; c['reason'] = 'SYNTHETIC_EXCLUSION'
        queries = [q for q in queries if q['shot'] <= N]
        early = [e for e in early if e['shot'] <= N]
    outcomes = [{'shot': q['shot'], 'vial': q['vial'], 'q': .1} for q in queries]
    predictions = {}
    for arm in p.md.ARMS:
        error = .2 if arm == 'C2' else .4
        predictions[arm] = [dict(q, status='QUALIFIED', feature_extrapolation=[], prediction={
            'tds_percent': 10+error, 'solute_kg': q['mass_kg']*(10+error)/100,
            'allowance_kg': 0., 'numerical_qualified': True}) for q in queries]
    return early, queries, outcomes, predictions, cohort


def set_error(row, error):
    row['prediction']['tds_percent'] = 10+error
    row['prediction']['solute_kg'] = row['mass_kg']*(10+error)/100


def test_mass_and_solute_conservation_weighted_not_arithmetic():
    gs = [p.Geometry(1, i, 0. if i == 1 else (1. if i == 2 else 3.)) for i in range(1, 17)]
    b, status = p.boundaries(gs, (.004, .003))
    assert status == 'QUALIFIED' and (b['k1'], b['k2']) == (3, 4)
    pools = p.pooled_input(gs, b, {2: .1, 3: .3, 4: .2})
    assert pools[0]['q'] == pytest.approx(.25)
    assert pools[0]['q'] != pytest.approx(.2)
    for pool in pools:
        assert pool['mass_kg'] == math.fsum(r['mass_kg'] for r in pool['vials'])
        assert pool['solute_kg'] == math.fsum(r['solute_kg'] for r in pool['vials'])
        assert pool['mass_kg']*pool['q'] == pytest.approx(pool['solute_kg'], abs=1e-18)
    assert pools[0]['vials'][0]['solute_kg'] == 0 and pools[0]['vials'][0]['q'] is None
    assert pools[0]['original_assays'] == 2


def test_decimal_ties_earlier_index_and_original_origin():
    gs = [p.Geometry(1, i, 0. if i < 3 else 1.) for i in range(1, 17)]
    b, _ = p.boundaries(gs, (.0015, .0015))
    assert (b['k1'], b['k2']) == (3, 4)
    assert b['cumulative_kg'][:4] == [0., 0., .001, .002]
    assert b['m1_kg']+b['m2_kg'] == .002
    with pytest.raises(ValueError):
        p.boundaries(list(reversed(gs)), (.0015, .0015))
    gs[0] = p.Geometry(1, 1, None)
    assert p.boundaries(gs, (.003, .004))[1] == 'UNAVAILABLE_MEASURED_MASS_PREFIX'


@pytest.mark.parametrize('shot,vial', [(6, 3), (13, 2)])
def test_accepted_missing_cases_do_not_rescue_boundaries(shot, vial):
    rows = source_rows(); before = p.project(rows, (.003, .004))
    next(r for r in rows if (r['shot'], r['vial']) == (shot, vial))['tds_pct'] = 0.
    after = p.project(rows, (.003, .004))
    assert before[4][shot-1]['selection'] == after[4][shot-1]['selection']
    assert after[3][shot-1]['reason'] == 'UNAVAILABLE_POOLED_CHEMISTRY'
    assert len({e['shot'] for e in after[0]}) == 12
    assert after[4][shot-1]['pools'][0]['solute_kg'] is None
    assert after[4][shot-1]['selection']['prefix_kg'] == .007


def test_suffix_value_invariance_and_typed_arm_firewall():
    rows = source_rows(); before = p.project(rows, (.003, .004))
    for r in rows:
        if r['vial'] > 8:
            r['tds_pct'] = 79.
    after = p.project(rows, (.003, .004))
    assert before == after
    models = {a: p.md.synthetic_model(a) for a in p.md.ARMS}
    assert p.predict_records(models, before[0], before[1]) == p.predict_records(models, after[0], after[1])
    for arm, forbidden in [('C0', 'q1'), ('C0', 'q2'), ('C1', 'q2')]:
        entry = deepcopy(next(e for e in before[0] if e['arm'] == arm))
        entry['input']['values'][forbidden] = .1
        with pytest.raises(ValueError):
            p.input_index([entry])
    bad = deepcopy(before[1]); bad[0]['later_tds'] = 10.
    with pytest.raises(ValueError):
        p.predict_records(models, before[0], bad)


def test_runtime_interval_additivity_order_and_extrapolation():
    early, queries, *_ = p.project(source_rows(), (.003, .004))
    models = {a: p.md.synthetic_model(a) for a in p.md.ARMS}
    ps, states = p.predict_records(models, early, queries)
    reverse, _ = p.predict_records(models, early, queries[::-1])
    for a in p.md.ARMS:
        assert ps[a] == reverse[a][::-1]
        state = p.md.State.from_dict(states[a+'/1'])
        shot = [r for r in ps[a] if r['shot'] == 1]
        whole = state.predict_intervals([shot[0]['start_kg']], [shot[-1]['end_kg']])[0]
        assert abs(math.fsum(r['prediction']['solute_kg'] for r in shot)-whole.solute_kg) <= whole.allowance_kg+math.fsum(r['prediction']['allowance_kg'] for r in shot)
        assert all(r['prediction']['allowance_kg'] <= 1e-9 for r in shot)
        assert shot[0]['feature_extrapolation'] == list(state.feature_extrapolation)
        batch, _ = p.predict_records(models, [e for e in early if e['shot'] == 1], [queries[0]])
        assert batch[a][0] == shot[0]


def test_unknown_coordinates_domain_zero_and_nonfinite_units():
    early, queries, *_ = p.project(source_rows(), (.003, .004))
    models = {a: p.md.synthetic_model(a) for a in p.md.ARMS}
    es = [e for e in early if e['shot'] == 1]
    q = queries[0]
    for changed, status in [(dict(q, start_kg=None), 'UNAVAILABLE'),
                            (dict(q, start_kg=.001, end_kg=.002), 'BEFORE'),
                            (dict(q, start_kg=.080, end_kg=.081), 'INVALID_INTERVAL')]:
        pred, _ = p.predict_records(models, es, [changed])
        assert status in pred['C2'][0]['status']
    zero = dict(q, end_kg=q['start_kg'], mass_kg=0.)
    ps, _ = p.predict_records(models, es, [zero]); v = ps['C2'][0]['prediction']
    assert v['solute_kg'] == 0 and v['tds_percent'] is None
    for change in ({'mass_kg': float('nan')}, {'start_kg': float('inf')}, {'mass_kg': '1'}):
        with pytest.raises(ValueError):
            p.checked_query(dict(q, **change))
    for k, v in [('mass_unit', 'g'), ('concentration_unit', 'percent'), ('basis', 'VOLUME')]:
        wrong = deepcopy(es); wrong[0]['input'][k] = v
        with pytest.raises(ValueError):
            p.input_index(wrong)


def test_shared_boundary_roundoff_is_recorded_not_domain_clipping():
    anchor = .007
    before = math.nextafter(anchor, 0.)
    q = {'start_kg': before, 'end_kg': .008}
    a, b, allowance = p.runtime_coordinates(q, anchor)
    assert a == anchor and b == .008 and allowance == 2*(anchor-before)
    q['start_kg'] = anchor-.001
    assert p.runtime_coordinates(q, anchor)[0] < anchor
    q = {'start_kg': before, 'end_kg': before}
    a, b, allowance = p.runtime_coordinates(q, anchor)
    assert a == b == anchor
    st = p.md.synthetic_model('C0').condition(p.md.EarlyInput('C0', (.003, .004)))
    with pytest.raises(ValueError, match='BEFORE'):
        st.predict_intervals([before], [.008])


def test_fixed_primary_and_all_decision_axes():
    _, q, o, ps, c = fixture()
    r, shot = s.evaluate(q, o, ps, c)
    assert r['primary_candidate'] == 'C2'
    assert r['decision_vector'] == {'coverage': 'PASS', 'numerical': 'PASS',
        'adequacy': {'C0': 'PASS', 'C1': 'PASS', 'C2': 'PASS'}, 'I0': 'PASS', 'I1': 'PASS'}
    assert r['disposition'] == 'FROZEN_C2_TRANSFER_EARNED_ON_QUALIFIED_POOLED_PREFIX_COHORT'
    assert r['arms']['C2']['full_scope_metrics']['R_pp'] == pytest.approx(.2)
    assert len(shot['C2']) == 13
    ps['C1'].pop()
    with pytest.raises(ValueError, match='DENOMINATOR'):
        s.evaluate(q, o, ps, c)


def test_equal_shot_weighting_and_bias_noncancellation():
    _, q, o, ps, c = fixture(N=10)
    for rows in ps.values():
        for r in rows:
            set_error(r, .6 if r['shot'] <= 5 else -.6)
    result, _ = s.evaluate(q, o, ps, c)
    m = result['arms']['C2']['full_scope_metrics']
    assert m['B_pp'] == pytest.approx(0) and m['absB_pp'] == pytest.approx(.6)
    assert result['decision_vector']['adequacy']['C2'] == 'FAIL'
    # Unequal target mass between shots must not weight the across-shot mean.
    shots = []
    for mass, error in [(1., .2), (100., .8)]:
        qq = [{'mass_kg': mass, 'vial': 1}]
        pp = [{'status': 'QUALIFIED', 'prediction': {'solute_kg': mass*(10+error)/100,
            'tds_percent': 10+error, 'allowance_kg': 0., 'numerical_qualified': True}}]
        shots.append(s.shot_metrics(qq, [{'q': .1}], pp))
    assert s.aggregate(shots)['full_scope_metrics']['R_pp'] == pytest.approx(.5)


def test_minimum_coverage_and_individual_seventy_five_percent():
    _, q, o, ps, c = fixture(N=9)
    r, _ = s.evaluate(q, o, ps, c)
    assert r['decision_vector']['coverage'] == 'EVIDENCE_LIMITED'
    assert r['disposition'] == 'MIXED_BLOCKED_OR_UNRESOLVED'
    _, q, o, ps, c = fixture(N=13)
    for rows in ps.values():
        for r in rows:
            set_error(r, .7 if r['shot'] <= 4 else .1)
    r, _ = s.evaluate(q, o, ps, c)
    assert r['arms']['C2']['full_scope_metrics']['absB_pp'] < .5
    assert r['arms']['C2']['definite_adequate_shots'] == 9
    assert r['arms']['C2']['adequacy'] == 'FAIL'


def test_paired_gain_and_numerical_straddle_near_zero():
    _, q, o, ps, c = fixture()
    for r in ps['C2']:
        set_error(r, .5)
        r['prediction']['allowance_kg'] = 1e-9
    result, _ = s.evaluate(q, o, ps, c)
    assert result['decision_vector']['adequacy']['C2'] == 'NUMERICALLY_UNRESOLVED'
    for a in ('C0', 'C1'):
        for r in ps[a]:
            set_error(r, 0.)
    result, _ = s.evaluate(q, o, ps, c)
    assert result['increments']['I0']['relative_improvement'] is None
    assert result['increments']['I0']['components']['relative_gain'] == 'FAIL'
    assert result['disposition'] == 'SIMPLER_FROZEN_TRANSFER_SUFFICIENT_ON_QUALIFIED_COHORT'


def test_missing_suffix_does_not_remove_membership_or_bias_cancellation():
    _, q, o, ps, c = fixture()
    # Incomplete signed sum may be cancelled by missing outcomes. R still has a lower bound.
    for rows in ps.values():
        for r in rows:
            set_error(r, 5.)
    for x in o:
        if x['vial'] == 16:
            x['q'] = None
    r, shots = s.evaluate(q, o, ps, c)
    assert r['coverage']['eligible_shots'] == 13 and not r['coverage']['complete_panel']
    assert r['arms']['C2']['full_scope_lower_bounds']['absB_pp'] == 0
    assert r['arms']['C2']['full_scope_lower_bounds']['R_pp'] > 1
    assert r['disposition'] == 'FROZEN_CONDITIONAL_TRANSFER_INADEQUATE_ON_DECLARED_COHORT'
    assert r['arms']['C2']['full_scope_metrics'] is None


def test_numerical_ceiling_cannot_be_hidden_and_strict_json():
    _, q, o, ps, c = fixture()
    ps['C2'][0]['prediction']['allowance_kg'] = 1.00001e-9
    r, _ = s.evaluate(q, o, ps, c)
    assert r['decision_vector']['numerical'] == 'NUMERICALLY_UNRESOLVED'
    assert r['decision_vector']['coverage'] == 'EVIDENCE_LIMITED'
    assert r['decision_vector']['adequacy']['C2'] != 'PASS'
    for text in ('{"a":1,"a":2}', '{"a":NaN}'):
        with pytest.raises(ValueError):
            p.md.strict_json(text)


def test_report_cannot_predict_or_score_and_receipts_are_exclusive(tmp_path, monkeypatch):
    p.write(tmp_path/'scores.json', {'retained': True})
    p.write(tmp_path/'score_completion.json', {'status': 'COMPLETE', 'scores_sha256': p.digest(tmp_path/'scores.json')})
    monkeypatch.setattr(p, 'predict', lambda *a: pytest.fail('report predicted'))
    monkeypatch.setattr(s, 'evaluate', lambda *a: pytest.fail('report scored'))
    monkeypatch.setattr(s, 'project_outcomes', lambda *a: pytest.fail('report read outcomes'))
    assert s.report(tmp_path) == {'retained': True}
    with pytest.raises(FileExistsError):
        p.write(tmp_path/'scores.json', {})
    p.write(tmp_path/'score_receipt.json', {'status': 'STARTED'})
    with pytest.raises(ValueError, match='DUPLICATE_SCORE'):
        s.verify_before_score(tmp_path, None, None, None)


def test_independent_exact_freeze_required(tmp_path):
    p.write(tmp_path/'freeze.json', {})
    review = tmp_path/'review.json'; p.write(review, {'status': 'APPROVED', 'independent': False})
    with pytest.raises(ValueError, match='INDEPENDENT_EXACT'):
        s.verify_before_score(tmp_path, review, None, None)


def test_manifest_drift_and_path_escape(tmp_path):
    p.write(tmp_path/'x.json', {})
    p.write(tmp_path/'prepare_manifest.json', {'task': p.TASK, 'files': {'x.json': '0'*64}})
    with pytest.raises(ValueError, match='DRIFT'):
        p.verify_manifest(tmp_path, 'prepare_manifest.json')


def test_parent_identity_failures_before_any_prediction(tmp_path, monkeypatch):
    # Synthetic stand-in for accepted identities; no source-derived model copied.
    doc = tmp_path/'doc'; doc.mkdir()
    pin = {'producer_commit': 'a'*40, 'producer_tree': 'b'*40,
           'models': {}, 'runtime_modules': [p.RUNTIME], 'producer_files': {}}
    p.write(doc/'PARENT_006_HANDOFF.json', pin)
    monkeypatch.setattr(p, 'git', lambda *a: 'c'*40)
    with pytest.raises(ValueError, match='producer tree'):
        p.verify_dependencies(tmp_path, doc)
    monkeypatch.setattr(p, 'git', lambda *a: 'b'*40)
    with pytest.raises(ValueError, match='matrix'):
        p.verify_dependencies(tmp_path, doc)


def test_model_runtime_and_source_pins_fail_closed(tmp_path, monkeypatch):
    root = tmp_path; doc = root/'docs/analysis/sci_md_mass_delivery_007'; doc.mkdir(parents=True)
    runtime = root/p.RUNTIME; runtime.parent.mkdir(parents=True); runtime.write_text('synthetic runtime bytes')
    parser = root/p.PARSER; parser.write_text('synthetic parser bytes')
    models = {a: p.md.synthetic_model(a) for a in p.md.ARMS}
    pin = {'producer_commit': 'a'*40, 'producer_tree': 'b'*40, 'models': {},
           'runtime_modules': [p.RUNTIME], 'producer_files': {p.RUNTIME: p.digest(runtime)},
           'schema': p.md.VERSION, 'units': p.md.UNITS, 'claims': list(p.md.CLAIMS),
           'rights': 'SYNTHETIC_FIRST_PARTY', 'domain_kg': [0., .08]}
    for a, m in models.items():
        path = doc/(a+'.json'); m.save(path); relative = str(path.relative_to(root))
        pin['models'][a] = {'path': relative, 'model_sha256': m.sha256}
        pin['producer_files'][relative] = p.digest(path)
    p.write(doc/'PARENT_006_HANDOFF.json', pin)
    accepted = root/'docs/analysis/sci_md_grudeva_clock_001/SOURCE.json'; accepted.parent.mkdir()
    authority = {'upstream_commit': p.gc.SOURCE_COMMIT, 'files': {'exp13.csv': p.gc.SOURCE_SHA}}
    p.write(accepted, authority); p.write(doc/'SOURCE.json', authority)
    monkeypatch.setattr(p, 'git', lambda *a: 'b'*40)
    monkeypatch.setattr(p.subprocess, 'check_output', lambda argv: (root/argv[-1].split(':', 1)[1]).read_bytes())
    p.verify_dependencies(root, doc)
    for file in (runtime, doc/'C0.json'):
        old = file.read_bytes(); file.write_bytes(old+b'\n')
        with pytest.raises(ValueError, match='byte hash'):
            p.verify_dependencies(root, doc)
        file.write_bytes(old)
    path = doc/'PARENT_006_HANDOFF.json'
    pin['models']['C2']['model_sha256'] = '0'*64; path.write_text(p.md.canonical(pin))
    with pytest.raises(ValueError, match='canonical'):
        p.verify_dependencies(root, doc)
    pin['models']['C2']['model_sha256'] = models['C2'].sha256; path.write_text(p.md.canonical(pin))
    (doc/'SOURCE.json').write_text('{}')
    with pytest.raises(ValueError, match='source record'):
        p.verify_dependencies(root, doc)


def test_numerically_unresolved_increment_threshold_and_wins():
    _, q, o, ps, c = fixture()
    for r in ps['C0']:
        set_error(r, .5)
    for r in ps['C2']:
        set_error(r, .4); r['prediction']['allowance_kg'] = 1e-10
    result, _ = s.evaluate(q, o, ps, c)
    assert result['increments']['I0']['components']['absolute_gain'] == s.UNRESOLVED
    assert result['increments']['I0']['status'] == s.UNRESOLVED
    # Large mean gain cannot compensate for too few paired wins.
    for r in ps['C0']:
        set_error(r, 4. if r['shot'] <= 9 else .1)
    result, _ = s.evaluate(q, o, ps, c)
    assert result['increments']['I0']['components']['absolute_gain'] == 'PASS'
    assert result['increments']['I0']['components']['paired_shot_wins'] == 'FAIL'


def test_source_nonfinite_and_excluded_extra_block():
    rows = source_rows(); rows[-1]['tds_pct'] = 99.
    original = p.project(rows, (.003,.004))
    for r in rows:
        if r['shot'] == 14 or r['vial'] > 16:
            r['tds_pct'] = -12345.
    assert p.project(rows, (.003,.004)) == original
    rows[2]['tds_pct'] = float('nan')
    with pytest.raises(ValueError):
        p.project(rows, (.003,.004))
