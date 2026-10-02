"""Manufactured observations only; no private Grudeva outcome access."""
from copy import deepcopy
from dataclasses import replace
from decimal import Decimal
import math

import pytest

from puckworks.analysis import grudeva_stopping_decision as p
from puckworks.analysis import grudeva_stopping_decision_scoring as s


def geometry(masses=(.001, .004, .005), anchor=.008, shot=1):
    out = []
    x = Decimal(str(anchor))
    for vial, mass in enumerate(masses, 14):
        end = x + Decimal(str(mass))
        out.append({'shot': shot, 'vial': vial, 'mass_kg': mass,
                    'start_kg': float(x), 'end_kg': float(end)})
        x = end
    return out


def state(logit=0., arm='C2'):
    model = p.md.synthetic_model(arm)
    model = replace(model, theta=tuple((logit,) + (0.,) * len(model.means) for _ in range(5)))
    return model.condition(p.md.EarlyInput(arm, model.means, 'SYNTHETIC'))


def observations(qs, percentages):
    return [{'shot': q['shot'], 'vial': q['vial'], 'mass_g': 1000 * q['mass_kg'],
             'tds_percent': percent} for q, percent in zip(qs, percentages)]


def selection(vial=14, mass=.009, status='QUALIFIED'):
    return {'status': status, 'selected_vial': vial, 'selected_mass_kg': mass,
            'prediction': None, 'feature_extrapolation': []}


def test_exact_frozen_identities_and_wrong_model_rejection():
    models = p.verify_dependencies()
    assert {a: m.sha256 for a, m in models.items()} == p.MODEL_IDS
    changed = dict(models)
    changed['C2'] = p.md.synthetic_model()
    with pytest.raises(ValueError, match='MODEL_IDENTITY'):
        p.verify_models(changed)


def test_anchor_recorded_boundaries_and_no_partial_vials():
    st = state()
    qs = geometry()
    assert p.eligible_boundaries(qs, st.b_anchor) == [(14, .009), (15, .013), (16, .018)]
    assert p.model_decision(st, qs, p.CONTRACTS[0])['selected_mass_kg'] == .009
    with pytest.raises(ValueError, match='ANCHOR'):
        p.eligible_boundaries(qs, .007)
    with pytest.raises(ValueError, match='CONTIGUOUS'):
        p.eligible_boundaries([qs[0], qs[2]], st.b_anchor)
    bad = deepcopy(qs)
    bad[0]['partial_vial_mass'] = .0005
    with pytest.raises(ValueError, match='STRICT'):
        p.eligible_boundaries(bad, st.b_anchor)


def test_earliest_qualified_boundary_no_feasible_abstention_and_extrapolation():
    st = state(-5.)
    assert p.model_decision(st, geometry(), p.CONTRACTS[0])['status'] == 'ABSTAIN'
    st = state()
    inp = replace(st.inputs, values=(.001, .007, .15, .10))
    st = st.model.condition(inp)
    result = p.model_decision(st, geometry(), p.CONTRACTS[0])
    assert result['status'] == 'QUALIFIED'
    assert 'm1_kg' in result['feature_extrapolation']
    assert result['selected_vial'] == 14


def test_disconnected_ranges_and_root_enclosure_are_not_feasible_points():
    model = p.md.Model.load(p.ROOT / 'docs/analysis/sci_md_mass_delivery_006/models/C2.json')
    st = model.condition(p.md.EarlyInput('C2',
        (.0030670000000000003, .0032029999999999997, .2974564005, .0931364597), 'SYNTHETIC'))
    result = p.stop.solve_stopping_ranges(st, p.stop.StoppingQuery(.007, model.domain_kg,
                                                                  suffix_tds_max_percent=4.9))
    assert len(result.components) == 2
    assert p.boundary_status(result, .008) == 'QUALIFIED'
    assert p.boundary_status(result, .05) == 'EXCLUDED'
    assert p.boundary_status(result, .068) == 'QUALIFIED'
    e = result.components[0].upper
    for b in (e.lower_kg, (e.lower_kg + e.upper_kg) / 2, e.upper_kg):
        assert p.boundary_status(result, b) == 'NUMERICALLY_UNRESOLVED'
    cs = [{'vial': i, 'mass_kg': b, 'status': p.boundary_status(result, b)}
          for i, b in enumerate((.05, .068, .069))]
    assert p.choose_boundary(cs)['mass_kg'] == .068


def test_unresolved_region_and_partial_component():
    st = state()
    result = p.stop.solve_stopping_ranges(st, p.stop.StoppingQuery(.009, .018, solute_min_kg=.0001))
    c = result.components[0]
    left = replace(c.lower, lower_kg=.010, upper_kg=.010, qualification='UNRESOLVED_ADJACENCY')
    changed = replace(result, components=(replace(c, lower=left, interior_min_kg=.010, partial=True),),
                      unresolved_regions=(p.stop.UnresolvedRegion(.009, .010, 'SYNTHETIC', ()),))
    assert p.boundary_status(changed, .0095) == 'NUMERICALLY_UNRESOLVED'
    assert p.boundary_status(changed, .010) == 'NUMERICALLY_UNRESOLVED'
    assert p.boundary_status(changed, .012) == 'QUALIFIED'


@pytest.mark.parametrize('contract,delta', list(zip(p.CONTRACTS, ['.005', '.0025', '.0075',
                                                         '0.006666666666666666666666666667', '.004'])))
def test_fixed_rule_frozen_deltas_and_boundary_selection(contract, delta):
    assert contract.nominal_delta_kg == Decimal(delta)
    qs = geometry()
    d = p.fixed_decision(qs, contract)
    target = Decimal('.008') + Decimal(delta)
    assert d['selected_mass_kg'] == next(q['end_kg'] for q in qs
                                        if Decimal(str(q['end_kg'])) >= target)
    assert d['prediction'] is None


def test_fixed_primary_exact_five_grams_at_boundary_and_abstention():
    assert p.CONTRACTS[0].nominal_delta_kg * 1000 == Decimal('5.000')
    assert p.fixed_decision(geometry(), p.CONTRACTS[0])['selected_vial'] == 15
    assert p.fixed_decision(geometry((.001, .001, .001)), p.CONTRACTS[0])['status'] == 'ABSTAIN'


def test_mass007_pool_origin_and_later_chemistry_invariance():
    rows = [{'shot': shot, 'vial': vial, 'window': 'regular16' if vial <= 16 else 'terminal',
             'mass_g': 0. if vial == 1 else 1., 'tds_pct': 10.,
             'discrepancy_at_source_precision': False}
            for shot in range(1, 15) for vial in range(1, 19)]
    first = p.parent.project(rows, (.003, .004))
    for r in rows:
        if r['vial'] > 8:
            r['tds_pct'] = 79.
    second = p.parent.project(rows, (.003, .004))
    assert first == second
    assert first[4][0]['selection']['prefix_kg'] == .007
    inp = p.parent.input_index(first[0])['C2', 1]
    st = p.md.synthetic_model().condition(inp)
    for policy in (lambda qs: p.model_decision(st, qs, p.CONTRACTS[0]),
                   lambda qs: p.fixed_decision(qs, p.CONTRACTS[0])):
        assert policy([q for q in first[1] if q['shot'] == 1]) == policy(
            [q for q in second[1] if q['shot'] == 1])


@pytest.mark.parametrize('mass,tds,expected,deficit_mg,deficit_pp', [
    (.005, 2., 'SUCCESS', 0., 0.), (.002, 3., 'FALSE_FEASIBLE', 40., 0.),
    (.01, 1.5, 'FALSE_FEASIBLE', 0., .5), (.004, 1., 'FALSE_FEASIBLE', 60., 1.),
])
def test_analytical_success_and_each_constraint_failure(mass, tds, expected, deficit_mg, deficit_pp):
    qs = geometry((mass,))
    endpoints = s.observed_endpoints(qs, observations(qs, [tds]))
    r = s.classify(selection(mass=qs[0]['end_kg']), endpoints, p.CONTRACTS[0])
    assert r['classification'] == expected
    assert r['solute_deficit_mg'] == pytest.approx(deficit_mg)
    assert r['tds_deficit_pp'] == pytest.approx(deficit_pp)


@pytest.mark.parametrize('tds,label', [(1., 'ABSTAIN_CORRECT'), (3., 'ABSTAIN_MISSED_FEASIBLE')])
def test_abstention_is_never_success(tds, label):
    qs = geometry()
    r = s.classify(selection(None, None, 'ABSTAIN'),
                   s.observed_endpoints(qs, observations(qs, [tds] * 3)), p.CONTRACTS[0])
    assert r['classification'] == label
    m = s.aggregate([r])
    assert m['qualified_decisions'] == m['successes'] == 0
    assert m['abstentions'] == 1


def test_earliest_oracle_regret_and_false_feasible_later_opportunity():
    qs = geometry()
    ends = s.observed_endpoints(qs, observations(qs, [3., 3., 3.]))
    early = s.classify(selection(), ends, p.CONTRACTS[0])
    assert early['classification'] == 'FALSE_FEASIBLE'
    assert early['oracle_vial'] == 15
    assert early['additional_mass_to_later_feasible_g'] == 4.
    exact = s.classify(selection(15, .013), ends, p.CONTRACTS[0])
    late = s.classify(selection(16, .018), ends, p.CONTRACTS[0])
    assert exact['mass_regret_g'] == 0.
    assert late['mass_regret_g'] == 5.
    m = s.aggregate([exact, late])
    assert m['median_successful_mass_regret_g'] == 2.5
    assert m['maximum_successful_mass_regret_g'] == 5.
    assert m['exact_oracle_choices'] == m['successful_choices_later_than_oracle'] == 1


def test_unresolved_excluded_from_delivered_decisions():
    qs = geometry()
    r = s.classify(selection(None, None, 'NUMERICALLY_UNRESOLVED'),
                   s.observed_endpoints(qs, observations(qs, [3.] * 3)), p.CONTRACTS[0])
    m = s.aggregate([r])
    assert m['numerically_unresolved'] == 1
    assert m['qualified_decisions'] == m['successes'] == m['abstentions'] == 0


@pytest.mark.parametrize('value', [math.inf, -math.inf, math.nan, True, '2'])
def test_nonfinite_and_invalid_observation_numbers_rejected(value):
    qs = geometry()
    obs = observations(qs, [3.] * 3)
    obs[0]['tds_percent'] = value
    with pytest.raises(ValueError):
        s.observed_endpoints(qs, obs)


def synthetic_bundle(tmp_path, monkeypatch):
    out = tmp_path / 'bundle'
    out.mkdir()
    root = tmp_path / 'candidate'
    root.mkdir()
    (root / 'code.py').write_text('synthetic candidate\n')
    monkeypatch.setattr(p, 'ROOT', root)
    monkeypatch.setattr(p, 'verify_dependencies', lambda: None)
    monkeypatch.setattr(p.parent, 'verify_source', lambda _: None)
    monkeypatch.setattr(p.parent, 'git', lambda _, *args:
        '' if args[0] == 'status' else 'tree' if args[-1] == 'HEAD^{tree}' else 'head')
    qs, cohort, states = [], [], {}
    for shot in range(1, 12):
        qs.extend(geometry(shot=shot))
        cohort.append({'shot': shot, 'eligible': True, 'k2': 13})
        for arm in ('C0', 'C2'):
            states[f'{arm}/{shot}'] = state(arm=arm)
    decisions = p.construct(qs, cohort, states)
    obs = observations(qs, [3.] * len(qs))
    source = [dict(r, tds_pct=r['tds_percent']) for r in obs]
    calls = []
    def parse(_):
        calls.append('outcome_access')
        return source
    monkeypatch.setattr(p.parent.gc, 'parse_source', parse)
    for name, value in [('queries.json', qs), ('cohort.json', cohort),
                        ('decisions.json', decisions), ('counts.json', {'synthetic': True})]:
        p.write(out / name, value)
    freeze = {'task': p.TASK, 'head': 'head', 'tree': 'tree',
        'bases': {'puckworks': {'base': 'base'}}, 'primary': 'C2',
        'required_shots': 11, 'minimum_decisions': 9, 'minimum_successes': 9,
        'maximum_false_feasible': 1, 'outcome_joins_allowed': 1, 'claims': list(p.CLAIMS),
        'code_and_protocol': {'code.py': p.digest(root / 'code.py')},
        'artifacts': {n: p.digest(out / n) for n in
                      ('queries.json', 'cohort.json', 'decisions.json', 'counts.json')}}
    p.write(out / 'freeze.json', freeze)
    review = tmp_path / 'approval.json'
    p.write(review, {'task': p.TASK, 'status': 'APPROVED', 'independent': True,
        'reviewer': 'SYNTHETIC_TEST_ONLY', 'reviewed_head': 'head', 'reviewed_tree': 'tree',
        'reviewed_base': 'base', 'freeze_sha256': p.digest(out / 'freeze.json'),
        'future_chemistry_attached': False, 'unresolved_blocking_findings': [],
        'checks': dict.fromkeys(s.REVIEW_CHECKS, 'PASS')})
    return out, review, calls


def test_once_only_score_immutable_decisions_private_output_and_no_fit(tmp_path, monkeypatch):
    import scipy.optimize
    from puckworks.analysis import conditional_tail_training as training
    def forbidden(*a, **k):
        pytest.fail('fitting, optimization or decision regeneration invoked')
    for name in ('least_squares', 'minimize', 'minimize_scalar', 'curve_fit', 'root', 'brentq'):
        monkeypatch.setattr(scipy.optimize, name, forbidden)
    monkeypatch.setattr(training, 'fit', forbidden)
    monkeypatch.setattr(training, 'develop', forbidden)
    monkeypatch.setattr(p.parent.gc, 'fit', forbidden)
    out, review, calls = synthetic_bundle(tmp_path, monkeypatch)
    before = (out / 'decisions.json').read_bytes()
    monkeypatch.setattr(p, 'construct', forbidden)
    monkeypatch.setattr(p, 'model_decision', forbidden)
    monkeypatch.setattr(p, 'fixed_decision', forbidden)
    result = s.score(out, review, tmp_path)
    assert result['disposition'] == s.INADEQUATE
    assert len(calls) == 1
    assert (out / 'decisions.json').read_bytes() == before
    for contract in p.CONTRACTS:
        assert result['metrics'][contract.name]['FIXED']['eligible_physical_shots'] == 11
    text = (out / 'scores.json').read_text()
    assert str(tmp_path) not in text
    assert 'selected_vial' not in text and 'tds_percent' not in text
    with pytest.raises(ValueError, match='DUPLICATE_SCORE'):
        s.score(out, review, tmp_path)
    assert len(calls) == 1
    with pytest.raises(FileExistsError):
        p.write(out / 'scores.json', {})


@pytest.mark.parametrize('mutation', ['approval_absent', 'approval_rejected', 'freeze', 'decisions',
                                     'receipt', 'extra_freeze', 'extra_review', 'code'])
def test_chronology_refusals_precede_outcome_access(tmp_path, monkeypatch, mutation):
    out, review, calls = synthetic_bundle(tmp_path, monkeypatch)
    if mutation == 'approval_absent':
        review.unlink()
    elif mutation == 'approval_rejected':
        r = p.read(review)
        r['status'] = 'REJECTED'
        review.write_text(p.md.canonical(r))
    elif mutation in ('freeze', 'extra_freeze'):
        f = p.read(out / 'freeze.json')
        f['extra'] = 'tamper'
        (out / 'freeze.json').write_text(p.md.canonical(f))
    elif mutation == 'decisions':
        (out / 'decisions.json').write_text('[]')
    elif mutation == 'receipt':
        p.write(out / 'score_receipt.json', {'status': 'STARTED'})
    elif mutation == 'extra_review':
        r = p.read(review)
        r['extra'] = 'tamper'
        review.write_text(p.md.canonical(r))
    else:
        (p.ROOT / 'code.py').write_text('changed')
    with pytest.raises((ValueError, OSError)):
        s.score(out, review, tmp_path)
    assert calls == []


def test_unexpected_observation_fields_and_partial_vial_rejected():
    qs = geometry()
    obs = observations(qs, [3.] * 3)
    obs[0]['private_extra'] = 1
    with pytest.raises(ValueError, match='STRICT'):
        s.observed_endpoints(qs, obs)
    ends = s.observed_endpoints(qs, observations(qs, [3.] * 3))
    with pytest.raises(ValueError, match='OBSERVED_ENDPOINTS'):
        s.classify(selection(14, .0085), ends, p.CONTRACTS[0])
