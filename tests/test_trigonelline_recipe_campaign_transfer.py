"""Synthetic risk checks; no private observations or outcome fixtures."""
from copy import deepcopy
from dataclasses import asdict
import json

import numpy as np
import pytest

from puckworks.analysis import trigonelline_recipe_campaign_transfer as t


def cohort():
    records = []
    for i, g in enumerate(t.FIT_GROUPS):
        for j in range(3):
            early = [.002+.00011*i+.00013*j, .003+.000013*i*i+.00007*j*j]
            edges = [sum(early), .021, .035, .05, .064+.0001*i]
            windows = [dict(fraction=f, start_kg=edges[k], end_kg=edges[k+1],
                            mass_kg=edges[k+1]-edges[k], q=.0015-.0002*k+.00001*i,
                            coordinate_allowance_kg=0.) for k, f in enumerate(t.FRACTIONS)]
            records.append(dict(shot=g.replace('-C', '-E')+f'-R{j+1}', group=g,
                                early_values=early, recipe=list(t.FIT_RECIPES[i]), windows=windows))
    return records


def targets():
    result = []
    for g, recipe in zip(t.TARGET_GROUPS, t.TARGET_RECIPES):
        for j in range(3):
            edges = [.006, .02, .034, .048, .06]
            for k, f in enumerate(t.FRACTIONS):
                result.append(dict(shot=g.replace('-C', '-E')+f'-R{j+1}', condition=g,
                    early_values=[.002, .004], recipe=list(recipe), fraction=f,
                    start_kg=edges[k], b1=edges[k+1], mass_kg=edges[k+1]-edges[k],
                    coordinate_allowance_kg=0., supported=True))
    return result


def design_records():
    designs, register, pred = {'FIT': [], 'PRED': []}, [], []
    expected = dict(zip(t.FIT_GROUPS, t.FIT_RECIPES)) | dict(zip(t.TARGET_GROUPS, t.TARGET_RECIPES))
    for g, (grind, temp, flow) in expected.items():
        label = g.split('-')[0]; i = int(g[-2:])
        designs[label].append(dict(exp=i, grind=grind, temp0=temp, temp1=temp,
                                  flow0=flow, flow1=flow, dose=20, date='SYNTHETIC'))
        for j in (1, 2, 3):
            register.append(dict(condition_id=g, shot_id=g.replace('-C', '-E')+f'-R{j}',
                source_experiment_id=str(i), physical_replicate_id=str(j),
                campaign_id='FIT_2021_12' if label == 'FIT' else 'PREDICTION_2022_03',
                machine='DE1', dose_g='20', grind_setting=str(grind),
                nominal_temperature_program_id=f'CONST-{temp}C', nominal_flow_program_id=f'CONST-{flow}ML_S',
                collection_date='SYNTHETIC', coffee_product='SYNTHETIC', coffee_lot_id='UNKNOWN',
                roast_batch_id='UNKNOWN', source_id='SYNTHETIC'))
        if label == 'PRED':
            pred.append(dict(condition_id=g, temperature_start_C=temp, temperature_end_C=temp,
                             flow_start_mL_s=flow, flow_end_mL_s=flow))
    return designs, register, pred


def folds(records):
    return [dict(group=g, domain_kg=max(w['end_kg'] for s in records if s['group'] != g for w in s['windows']),
        held_shots=[s['shot'] for s in records if s['group'] == g],
        training_shots=[s['shot'] for s in records if s['group'] != g],
        support=[[s['shot'], w['fraction']] for s in records if s['group'] == g for w in s['windows']
                 if w['end_kg'] <= max(v['end_kg'] for a in records if a['group'] != g for v in a['windows'])])
        for g in t.FIT_GROUPS]


def test_all_15_recipe_assignments_and_shot_join():
    d, r, p = design_records()
    joined, inspection = t.recipe_join(d, r, p)
    assert len(joined) == 19 and len(inspection) == 57
    d['FIT'][0]['temp0'], d['FIT'][1]['temp0'] = d['FIT'][1]['temp0'], d['FIT'][0]['temp0']
    with pytest.raises(t.Stop, match='RECIPE_IDENTITY'):
        t.recipe_join(d, r, p)
    d, r, p = design_records(); r[0]['shot_id'] = r[1]['shot_id']
    with pytest.raises(t.Stop, match='SHOT_RECIPE_JOIN'):
        t.recipe_join(d, r, p)
    d, r, p = design_records(); d['FIT'] = d['FIT'][8:11]+d['FIT'][13:]
    with pytest.raises(t.Stop, match='FIFTEEN'):
        t.recipe_join(d, r, p)


def test_support_floor_and_held_domains():
    r = cohort()
    # Preserve the 180/177 accounting without relying on private observations.
    r[0]['windows'] = r[0]['windows'][:1]
    q = targets(); f = folds(r)
    support = t.support_guards(r, q, f)
    assert support['B_floor_kg'] > .06
    assert support['held_total'] < 177  # largest source design endpoints lack held support
    q[-1]['b1'] = .1
    with pytest.raises(t.Stop, match='BOOTSTRAP_SUPPORT_FLOOR'):
        t.support_guards(r, q, f)
    q = targets(); q[0]['start_kg'] = .005
    with pytest.raises(t.Stop, match='PREFIX'):
        t.support_guards(r, q, f)
    f[0]['support'] = []
    with pytest.raises(t.Stop, match='MASK'):
        t.support_guards(r, targets(), f)


def test_matched_18_global_offsets_and_penalty():
    r = cohort()
    for arm in ('R18', 'Q18'):
        p = t.Problem(r, arm, .01)
        x = p.starts[1].copy(); x[15:] = [.3, -.2, .1]
        base = p.model(p.starts[1]).logits([s['early_values'] for s in r], [s['recipe'] for s in r])
        logits = p.model(x).logits([s['early_values'] for s in r], [s['recipe'] for s in r])
        assert len(x) == 18
        np.testing.assert_allclose(np.diff(logits-base, axis=1), 0, atol=2e-15)
        np.testing.assert_allclose(p.residual(x)[-3:] @ p.residual(x)[-3:], .01*np.mean(x[15:]**2))
    assert len(t.Problem(r, 'D0', .01).starts[0]) == 15
    p = t.Problem(r, 'D0', .01)
    assert len(p.residual(p.starts[1])) == 180+10+9


def test_training_transforms_and_integer_replication():
    r = cohort(); c = np.tile([2, 0, 1], 15)
    literal = [deepcopy(s) for s, n in zip(r, c) for _ in range(n)]
    for arm in t.ARMS:
        a = t.Problem(r, arm, None if arm == 'K0' else .01, c)
        b = t.Problem(literal, arm, None if arm == 'K0' else .01)
        np.testing.assert_allclose(a.means, b.means, atol=1e-17)
        np.testing.assert_allclose(a.extra_mean, b.extra_mean, atol=1e-14)
        np.testing.assert_allclose(a.extra_sd, b.extra_sd, atol=1e-14)
        assert a.domain == b.domain
        if arm != 'K0':
            ra, rb = a.residual(a.starts[0]), b.residual(a.starts[0])
            np.testing.assert_allclose(ra @ ra, rb @ rb, rtol=1e-13)
        else:
            np.testing.assert_allclose(a.weights @ a.q, b.weights @ b.q)
    sw = t.training_weights(r, c)
    for g in t.FIT_GROUPS:
        assert sum(w for s, w in zip(r, sw) if s['group'] == g) == pytest.approx(1/15)


def test_zero_weight_rows_cannot_enlarge_domain_or_break_geometry():
    r = cohort(); c = np.ones(45, int); c[-1] = 0
    a = t.Problem(r, 'Q18', .01, c)
    r[-1]['windows'][0].update(start_kg=-1, end_kg=100)
    b = t.Problem(r, 'Q18', .01, c)
    assert a.domain == b.domain
    np.testing.assert_array_equal(a.means, b.means)
    with pytest.raises(t.Stop, match='QUALIFIED_TRAINING'):
        t.Problem(r, 'Q18', .01)


def test_held_chemistry_cannot_enter_fold_fitting_and_march_rejected():
    r = cohort(); fold = folds(r)[0]
    train = [s for s in r if s['group'] != fold['group']]
    before = t.Problem(train, 'R18', .01)
    for s in r[:3]:
        for w in s['windows']: w['q'] = 1e99
    after = t.Problem([s for s in r if s['group'] != fold['group']], 'R18', .01)
    np.testing.assert_array_equal(before.residual(before.starts[0]), after.residual(after.starts[0]))
    r[0]['shot'] = 'PRED-E01-R1'
    with pytest.raises(t.Stop, match='FIT_ONLY'):
        t.Problem(r, 'R18', .01)


def test_target_recipes_only_affect_r18_and_quadrature_qualifies():
    r, q = cohort(), targets()
    changed = deepcopy(q)
    for v in changed: v['recipe'] = [2., 100., 4.]
    for arm in t.ARMS:
        p = t.Problem(r, arm, None if arm == 'K0' else .01)
        x = [.002] if arm == 'K0' else p.starts[0].copy()
        if arm in ('R18', 'Q18'): x[15:] = [.2, .3, .4]
        model = p.model(x)
        a, b = t.predict(model, q), t.predict(model, changed)
        assert len(a) == 48 and max(v['allowance_kg'] for v in a) < 1e-9
        assert ([v['prediction_mg_g'] for v in a] != [v['prediction_mg_g'] for v in b]) == (arm == 'R18')
        assert all(v['adaptive_error_kg'] >= 0 for v in a)
    p = t.Problem(r, 'K0', None)
    np.testing.assert_allclose([v['prediction_mg_g'] for v in t.predict(p.model([.002]), q)], 2., atol=1e-14)


def test_independent_lambda_selection_and_numerical_guard():
    candidates = lambda losses: [dict(lambda_=lam, loss=loss, allowance=1e-12)
                                for lam, loss in zip(t.LAMBDAS, losses)]
    selections = []
    for losses in ([1., 2., 3., 4.], [4., 1., 3., 4.], [4., 3., 2., 1.]):
        c = [dict(**{'lambda': v.pop('lambda_')}, **v) for v in candidates(losses)]
        selections.append(t.select_lambda(c))
    assert selections == [.0001, .01, 100.]
    c = [{'lambda': lam, 'loss': 1., 'allowance': 1e-12} for lam in t.LAMBDAS]
    assert t.select_lambda(c) == 100.
    with pytest.raises(t.Stop, match='COMPLETE_LAMBDA'):
        t.select_lambda(c[:-1])
    c[0]['allowance'] = 1e-4
    with pytest.raises(t.Stop, match='NUMERICALLY_UNRESOLVED'):
        t.select_lambda(c)


def test_complete_paired_draws_and_all_conditions():
    c = t.paired_multiplicities()
    assert c.shape == (2000, 19, 3) and c.dtype == np.int64
    assert np.all(c.sum(axis=2) == 3)
    np.testing.assert_array_equal(c, t.paired_multiplicities())
    assert not np.array_equal(c[:, 0], c[:, 15])
    with pytest.raises(t.Stop, match='EXACTLY_2000'):
        t.paired_multiplicities(1999)
    r, q = cohort(), targets(); p = t.Problem(r, 'K0', None)
    predictions = t.predict(p.model([.002]), q)
    observed = [dict(shot=v['shot'], fraction=v['fraction'], q=.001) for v in q]
    result = t.score(predictions, observed, c[0, 15:].ravel())
    assert set(result['conditions']) == set(t.TARGET_GROUPS)
    assert result['aggregate']['L'] == pytest.approx(1.)
    with pytest.raises(t.Stop, match='CONDITION_MISSING'):
        t.score(predictions, observed, np.zeros(12, int))


def test_no_success_only_intervals_zero_reference_and_preference_conjunction():
    with pytest.raises(t.Stop, match='COMPLETE_PAIRED'):
        t.interval_summary([1.]*1999, [[1., 1.]]*1999)
    ci = t.interval_summary([None]+[.1]*1999, [None]+[[.1, .1]]*1999)
    assert ci['ci'] is None and ci['undefined'] == 1
    assert t.contrast({'L': 1., 'L_allowance': 0.}, {'L': 0., 'L_allowance': 0.})['gain'] is None
    conditions = {b: {c: -.1 for c in t.TARGET_GROUPS} for b in t.ARMS[1:]}
    intervals = {'Q18': [-.2, -.1], 'D0': [-.1, .1], 'K0': [-.1, .1]}
    assert t.decision(intervals, conditions)['preference'] == 'RECIPE_INCREMENT_UNRESOLVED'
    intervals = {b: [-.2, -.1] for b in t.ARMS[1:]}
    assert t.decision(intervals, conditions)['preference'] == 'RECIPE_CONDITIONAL_TRANSFER_PREFERENCE'
    conditions['D0']['PRED-C06'] = .01
    assert t.decision(intervals, conditions)['preference'] == 'RECIPE_INCREMENT_UNRESOLVED'
    intervals['Q18'] = [0., .1]
    assert t.decision(intervals, conditions)['comparison'] == 'RECIPE_MASS_COMPARISON_UNRESOLVED'
    intervals['Q18'] = [.01, .1]
    assert t.decision(intervals, conditions)['preference'] == 'RECIPE_NOT_SELECTED'
    assert t.decision(intervals, conditions, False)['preference'] == 'INCOMPLETE'


def test_closed_grade_intersections():
    assert t.grades([0., .1]) == ['small', 'moderate']
    assert t.grades([-.1, 0.]) == ['worse', 'small']
    assert t.grades([.25, .25]) == ['large']
    assert len({(lo, hi) for lo in (.075, .1, .125) for hi in (.1875, .25, .3125)}) == 9


def test_actual_call_limit_failure_and_no_retry(tmp_path, monkeypatch):
    def exhausted(fun, initial, **kwargs):
        for _ in range(8001): fun(initial)
    monkeypatch.setattr(t, 'least_squares', exhausted)
    e = t.Executor(tmp_path, t.time.time())
    # The budget test counts calls, without running 8000 expensive integrations.
    monkeypatch.setattr(t.Problem, 'residual', lambda self, x: np.ones(2))
    with pytest.raises(t.Stop, match='ACTUAL_RESIDUAL_CALL_CAP'):
        e.fit(cohort(), 'D0', .01, 'synthetic.failure')
    assert (tmp_path/'residual_calls.bin').stat().st_size == 8000
    events = [json.loads(line) for line in (tmp_path/'execution.jsonl').read_text().splitlines()]
    assert events[-1]['event'] == 'FAILED' and events[-1]['calls'] == 8000
    assert e.starts == 1


def test_finite_unsuccessful_start_is_recorded_and_all_three_attempted(tmp_path, monkeypatch):
    from types import SimpleNamespace
    calls = []
    def solve(fun, initial, **kwargs):
        calls.append(initial)
        return SimpleNamespace(fun=fun(initial), x=initial, success=len(calls) != 1,
                               status=0 if len(calls) == 1 else 1, message='synthetic', nfev=1, njev=1)
    monkeypatch.setattr(t, 'least_squares', solve)
    e = t.Executor(tmp_path, t.time.time())
    model = e.fit(cohort(), 'Q18', .01, 'synthetic.three')
    assert len(calls) == 3 and e.unsuccessful == 1 and e.finished == 3
    assert asdict(model)['schema'] == t.SCHEMA


def test_model_schema_and_zero_scale_rejected():
    r = cohort()
    for s in r: s['recipe'] = [1.7, 89., 2.]
    with pytest.raises(t.Stop, match='ZERO_EXTRA_SCALE'):
        t.Problem(r, 'R18', .01)
    r = cohort(); p = t.Problem(r, 'D0', .01)
    record = asdict(p.model(p.starts[0])); record['schema'] = 'predecessor'
    with pytest.raises(t.Stop, match='MODEL_SCHEMA'):
        t.Model(**record)


def test_absent_or_drifted_historical_authority_stops_before_source_reads(tmp_path):
    old = tmp_path/'prior'; old.mkdir()
    (old/'freeze.json').write_text('{}')
    with pytest.raises(t.Stop, match='OLD_FREEZE_AUTHORITY_DRIFT'):
        t.qualify(tmp_path/'new', old, t.time.time())


def test_first_failed_draw_retains_vectors_and_exact_counts(tmp_path, monkeypatch):
    from types import SimpleNamespace
    monkeypatch.setattr(t, 'verify_freeze', lambda out: {'session_started_unix': t.time.time()})
    monkeypatch.setattr(t, 'tune', lambda *args: {a: .01 for a in t.NONLINEAR})
    monkeypatch.setattr(t, 'reproduce', lambda *args: None)
    for key in ('OPENBLAS_NUM_THREADS', 'OMP_NUM_THREADS', 'MKL_NUM_THREADS'):
        monkeypatch.setenv(key, '1')
    for name, value in [('training.json', cohort()), ('queries.json', targets()), ('folds.json', []),
                        ('FREEZE.json', {}), ('TUNING.json', {})]:
        t.write(tmp_path/name, value)
    np.save(tmp_path/'multiplicities.npy', t.paired_multiplicities(), allow_pickle=False)
    class FailureExecutor:
        def __init__(self, out, session_started):
            self.started = t.time.time(); self.starts = self.finished = self.analytic = 0
            self.calls = SimpleNamespace(tell=lambda: 0)
            self.events = []
            self.out = out
        def fit(self, records, arm, lam, name, multiplicities=None):
            if name.startswith('draw.'):
                t.write(self.out/'retained_draw_start.json', self.events[-1])
                raise t.Stop('SYNTHETIC_REQUIRED_DRAW_FAILURE')
            p = t.Problem(records, arm, lam)
            return p.model([.001] if arm == 'K0' else p.starts[1])
        def event(self, event): self.events.append(event)
    monkeypatch.setattr(t, 'Executor', FailureExecutor)
    from puckworks.analysis import pannusch_conditional_trigonelline_delivery as source
    monkeypatch.setattr(source.source, 'rows', lambda path: [])
    monkeypatch.setattr(source, 'analyte_index', lambda *args: {(q['shot'], q['fraction']): {} for q in targets()})
    monkeypatch.setattr(source, 'source_value', lambda *args: .001)
    with pytest.raises(t.Stop, match='REQUIRED_DRAW_FAILURE'):
        t.run(tmp_path, tmp_path/'unused_prior')
    result = t.read(tmp_path/'FAILURE.json')
    assert (result['draws_completed'], result['draws_failed'], result['draws_unattempted']) == (0, 1, 1999)
    assert result['preference'] == 'INCOMPLETE'
    start = t.read(tmp_path/'retained_draw_start.json')
    assert start['draw'] == 0 and np.asarray(start['multiplicities']).shape == (19, 3)
