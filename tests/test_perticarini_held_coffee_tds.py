"""Synthetic contract tests; no new private results are test fixtures."""
import copy
import itertools
import json
import math
from pathlib import Path

import numpy as np
import pytest

from puckworks.analysis import perticarini_held_coffee_tds as m


def rows():
    out = []
    for coffee in m.COFFEES:
        grinds = ('extra_fine', 'fine', 'optimal', 'coarse', 'extra_coarse') if coffee == 'cibao' else ('fine', 'optimal', 'coarse')
        for g, grind in enumerate(grinds):
            extreme = grind.startswith('extra_')
            for temp in ([93.4] if extreme else [93.4, 90.4]):
                for pressure in ([6, 9, 12] if extreme else [6, 9]):
                    out.append(dict(source_condition_id=f'{coffee}/{grind}/{temp}/{pressure}',
                        coffee_id=coffee, grind_id=grind, temperature_degC=temp,
                        nominal_pressure_bar=pressure, tau_s=19+g*7+pressure/3+(temp-90.4)/2,
                        tds_mean_pct=8+g*.3+pressure*.04+(temp-90.4)*.06,
                        ey_mean_pct=20, tds_sd_pct=0, chemical_sample_n=3))
    return out


def test_source_authentication_exact_view_and_drift(tmp_path):
    # Canonical identity verification only, no real fit or old campaign.
    root = Path(__file__).resolve().parents[1]
    observations, receipt = m.authenticate(root)
    assert len(observations) == 30 and receipt['compared_fields'] == 990
    assert receipt['reported_chemical_extractions'] == {'cibao': 54, 'modoetia': 36}
    assert receipt['raw_shot_records_available'] == 0
    assert len({o['source_condition_id'] for o in observations}) == 30
    from puckworks.analysis import perticarini2024_pressure_chemistry as a
    from puckworks.analysis import perticarini2024_pressure_grind as d
    import shutil
    for _, filename, _ in d.INPUTS:
        dest = tmp_path/filename
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(root/'puckworks/data'/filename, dest)
    before, _ = a.load_observations(tmp_path)
    for _, filename, _ in d.INPUTS:
        p = tmp_path/filename
        lines = p.read_text().splitlines()
        p.write_text('\n'.join([lines[0], *reversed(lines[1:])])+'\n')
    after, _ = a.load_observations(tmp_path)
    assert before == after  # full-key join, never positional
    p = tmp_path/d.INPUTS[1][1]
    p.write_text(p.read_text()+p.read_text().splitlines()[1]+'\n')
    with pytest.raises(ValueError, match='Duplicate'):
        a.load_observations(tmp_path)


@pytest.mark.parametrize('arm,count', [('D3', 3), ('R3', 3), ('T2', 2), ('N', 1)])
def test_fit_weighted_literal_source_only_and_inverse(arm, count):
    source, target = rows()[:18], rows()[18:]
    w = np.array([0, 2, 1]*6)
    pred, diag = m.fit(source, target, arm, w)
    literal = [r for r, n in zip(source, w) for _ in range(n)]
    other, check = m.fit(literal, target, arm, np.ones(len(literal)))
    np.testing.assert_allclose(pred, other, atol=1e-12)
    np.testing.assert_allclose(diag['center'], check['center'], atol=1e-12)
    assert diag['rank'] == len(diag['coefficients']) == count
    changed = copy.deepcopy(target)
    for row in changed:
        row['tds_mean_pct'] = 1e50
        row['ey_mean_pct'] = -1e50
        row['tds_sd_pct'] = -1
    p2, d2 = m.fit(source, changed, arm, w)
    np.testing.assert_array_equal(pred, p2)
    assert diag == d2
    zero = copy.deepcopy(source)
    zero[0]['tau_s'] = 1e80
    _, dz = m.fit(zero, target, arm, w)
    np.testing.assert_array_equal(diag['center'], dz['center'])
    assert diag['inverse_max_difference'] < 1e-10


def test_predictor_isolation():
    source, target = rows()[:18], rows()[18:]
    for field, affected in [('tau_s', 'D3'), ('nominal_pressure_bar', 'R3')]:
        changed = copy.deepcopy(target)
        for r in changed:
            r[field] *= 2
        for arm in m.ARMS:
            p, _ = m.fit(source, target, arm, np.ones(18))
            q, _ = m.fit(source, changed, arm, np.ones(18))
            assert np.allclose(p, q) == (arm != affected)


def test_enumeration_probability_and_ordered_quantiles():
    r = rows()
    cases = m.combinations(r)
    assert len(cases) == 300 and sum(c['frequency'] for c in cases) == 2916
    assert sum(all(w == 1 for w in c['weights']) for c in cases) == 1
    ordered = []
    for a, b, c in itertools.product(itertools.product(range(3), repeat=3),
                                    itertools.product(range(2), repeat=2),
                                    itertools.product(range(3), repeat=3)):
        vectors = [np.bincount(x, minlength=k).tolist() for x, k in [(a, 3), (b, 2), (c, 3)]]
        ordered.append(sum((i+1)*v*v for i, vector in enumerate(vectors) for v in vector))
    values = [sum((i+1)*v*v for i, vector in enumerate(c['vectors']) for v in vector) for c in cases]
    np.testing.assert_array_equal(m.intervals(values, [c['frequency'] for c in cases]),
                                  np.quantile(ordered, [.025, .975], method='linear'))
    for case in cases:
        assert [sum(w for o, w in zip(r, case['weights']) if o['coffee_id'] == c) for c in m.COFFEES] == [18, 12]
        for coffee, grinds, _ in m.STRATA:
            for grind in grinds:
                assert len({w for o, w in zip(r, case['weights']) if (o['coffee_id'], o['grind_id']) == (coffee, grind)}) == 1


def test_invalid_rank_weights_finite_and_no_rescue():
    r = rows()
    for weights in [np.zeros(30), [-1]*30, [math.nan]*30, [1]]:
        with pytest.raises(m.QualificationError):
            m.fit(r, r, 'D3', weights)
    for field, value in [('tau_s', 0), ('nominal_pressure_bar', math.inf), ('tds_mean_pct', math.nan)]:
        bad = copy.deepcopy(r)
        bad[0][field] = value
        with pytest.raises(m.QualificationError):
            m.fit(bad, r, 'D3', np.ones(30))
    with pytest.raises(m.QualificationError):
        m.fit(r, r, 'D3', [1]+[0]*29)


def test_nesting_and_reciprocal_roles(tmp_path):
    r = rows()
    ex = m.Executor(tmp_path)
    case = m.combinations(r)[13]
    result = m.evaluate(r, case['weights'], ex, 'synthetic')
    assert ex.finished == 8
    assert all(len(v) == 30 for v in result['predictions'].values())
    for fold in result['folds']:
        source = fold['source']
        assert all(i.startswith(source+'/') for i in fold['training'])
        assert all(not i.startswith(source+'/') for i in fold['evaluation'])
        m.nesting(fold['diagnostics'])
        assert all(d['training_weight'] == (18 if source == 'cibao' else 12) for d in fold['diagnostics'].values())
    with pytest.raises(m.QualificationError, match='reset'):
        m.Executor(tmp_path)


def test_metrics_decisions_orientation_grades():
    r = rows()
    pred = {a: [o['tds_mean_pct']+(1 if o['coffee_id'] == 'cibao' else 3) for o in r] for a in m.ARMS}
    score = m.metrics(r, pred, np.ones(30))
    assert score['D3']['aggregate']['rmse'] == pytest.approx(np.sqrt(5))
    assert m.contrast(2, 1)['gain'] == -1 and m.contrast(1, 2)['gain'] == .5
    assert m.contrast(1, 0)['gain'] is None
    assert m.intervals([1, None], [1, 2]) is None
    assert m.grade_set([0, .10]) == ['small', 'moderate']
    assert m.grade_set([.10, .25]) == ['moderate', 'large']
    assert m.grade_set([-.1, 0]) == ['worse', 'small']
    for lo, hi in itertools.product((.075, .1, .125), (.1875, .25, .3125)):
        assert m.grade(lo, lo, hi) == 'moderate'
        assert m.grade(hi, lo, hi) == 'large'
    # Winning D3/R3 alone is insufficient, and zero-touch stays unresolved.
    for a, value in [('D3', 2), ('R3', 3), ('T2', 1), ('N', 1.5)]:
        for s in ('aggregate', *m.COFFEES):
            score[a][s]['rmse'] = value
    decision = m.decisions(score, [score], [2916])
    assert decision['primary'] == 'DURATION_OBSERVER_LOWER_CONDITIONAL_TDS_LOSS'
    assert decision['overall'] == 'NO_CONDITIONAL_OBSERVER_PREFERENCE'
    score['R3']['aggregate']['rmse'] = 2
    assert m.decisions(score, [score], [2916])['primary'] == 'DURATION_PRESSURE_COMPARISON_UNRESOLVED'
    _, contrasts = m.summarize(score, [score], [2916])
    assert all(len(c['boundary_checks']) == 9 for pair in contrasts.values() for c in pair.values())


def test_deletion_memberships_counts():
    r = rows()
    ds = m.deletions(r)
    assert len(ds) == 38 and sum(d['kind'] == 'block' for d in ds) == 8
    assert 4*2*(1+300+len(ds)) == 2712
    for d in ds:
        if d['kind'] == 'block':
            assert len({r[i]['coffee_id'] for i in d['removed']}) == 1
        assert set(d['removed']) and len(d['removed']) < 18


def test_campaign_failure_preserves_first_combination(tmp_path, monkeypatch):
    r = rows()
    cases = m.combinations(r)
    m.save(tmp_path/'FREEZE.json', dict(files={}, observations_sha256=m.sha(m.canonical(r)),
                                      combinations_sha256=m.sha(m.canonical(cases))))
    monkeypatch.setattr(m, 'authenticate', lambda root: (r, {}))
    original = m.fit
    calls = 0
    def failing(*args):
        nonlocal calls
        calls += 1
        if calls == 9:
            raise m.QualificationError('synthetic required failure')
        return original(*args)
    monkeypatch.setattr(m, 'fit', failing)
    with pytest.raises(m.QualificationError, match='synthetic required'):
        m.run(tmp_path, tmp_path)
    failure = json.loads((tmp_path/'FAILURE.json').read_text())
    assert (failure['completed'], failure['failed'], failure['unattempted']) == (0, 1, 299)
    assert failure['represented_frequency'] == 0 and calls == 9
    assert json.loads((tmp_path/'CURRENT_CASE.json').read_text())['case'] == cases[0]
    assert not (tmp_path/'RESULT_SCIENCE.json').exists()


def test_complete_synthetic_campaign(tmp_path, monkeypatch):
    r = rows()
    cases = m.combinations(r)
    m.save(tmp_path/'FREEZE.json', dict(files={}, observations_sha256=m.sha(m.canonical(r)),
                                      combinations_sha256=m.sha(m.canonical(cases))))
    monkeypatch.setattr(m, 'authenticate', lambda root: (r, {}))
    result = m.run(tmp_path, tmp_path)
    assert result['counts'] == dict(requested=300, completed=300, failed=0, unattempted=0,
        represented_frequency=2916, requested_frequency=2916, fits=2712, fits_per_arm=678,
        block_deletions=8, condition_deletions=30)
    saved = [json.loads(line) for line in (tmp_path/'COMBINATIONS.jsonl').read_text().splitlines()]
    assert len(saved) == 300
    one = next(c for c in saved if all(w == 1 for w in c['weights']))
    assert one['result']['scores'] == result['point']['scores']
    events = [json.loads(line) for line in (tmp_path/'EXECUTION.jsonl').read_text().splitlines()]
    assert sum(e['event'] == 'start' for e in events) == 2712
    assert sum(e['event'] == 'finish' for e in events) == 2712
