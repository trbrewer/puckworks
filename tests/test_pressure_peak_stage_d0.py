"""D0 objective/weight isolation, then self-contained committed-field twins."""
import copy
import hashlib

import numpy as np
from numpy.testing import assert_allclose
import pytest

from puckworks.analysis import pressure_peak_stage_d0 as T


def _assert_replayed_fields(actual, expected, path="record"):
    """Use the approved float tolerance while preserving exact record structure."""
    if isinstance(actual, np.generic):
        actual = actual.item()
    if isinstance(expected, np.generic):
        expected = expected.item()
    if isinstance(expected, dict):
        assert isinstance(actual, dict), path
        assert actual.keys() == expected.keys(), path
        for key in expected:
            _assert_replayed_fields(actual[key], expected[key], f"{path}.{key}")
    elif isinstance(expected, (list, tuple)):
        assert isinstance(actual, (list, tuple, np.ndarray)), path
        assert len(actual) == len(expected), path
        for index, (left, right) in enumerate(zip(actual, expected)):
            _assert_replayed_fields(left, right, f"{path}[{index}]")
    elif isinstance(expected, float):
        assert isinstance(actual, float), path
        assert_allclose(actual, expected, rtol=1e-12, atol=0, err_msg=path)
    else:
        assert type(actual) is type(expected), path
        assert actual == expected, path


def test_replayed_fields_tolerance_and_exact_structure():
    expected = dict(count=0, flag=False, zero=0., missing=None, held_out=[
        dict(brew="6-1", fold="HYD-LOCO-6.0", predicted_onset_s=12.371027292378741),
        dict(brew="6-2", fold="HYD-LOCO-6.0", predicted_onset_s=12.357311255327197)])
    actual = copy.deepcopy(expected)
    actual["held_out"][0]["predicted_onset_s"] = 12.37102729237874
    _assert_replayed_fields(actual, expected)
    changed_float = copy.deepcopy(actual)
    changed_float["held_out"][0]["predicted_onset_s"] *= 1+2e-12
    changed_id = copy.deepcopy(actual)
    changed_id["held_out"][0]["brew"] = "6-2"
    changed_fold = copy.deepcopy(actual)
    changed_fold["held_out"][0]["fold"] = "HYD-LOCO-5.0"
    invalid = [changed_float, changed_id, changed_fold,
        dict(actual, count=1), dict(actual, count=0.), dict(actual, flag=0),
        dict(actual, zero=1e-30), dict(actual, missing=False), dict(actual, extra=None),
        {k:v for k,v in actual.items() if k!="count"},
        dict(actual, held_out=actual["held_out"][:1]),
        dict(actual, held_out=actual["held_out"][::-1])]
    for record in invalid:
        with pytest.raises(AssertionError):
            _assert_replayed_fields(record, expected)


@pytest.fixture(scope="module")
def predecessor():
    rows = T.D.read_table(T.OUT/"RESULT_TABLE.csv") if (T.OUT/"RESULT_TABLE.csv").exists() else T.E.read_table()
    rows = [dict(r,record_type="fit") if r["record_type"]=="point_replay" else r for r in rows]
    inputs = next(r for r in rows if r["record_type"] == "inputs")
    return T.context_from_fixture(inputs), rows


@pytest.mark.parametrize("form,fold", [(f,g) for f in T.FORMS for g in T.FOLDS])
def test_prerefit_unit_multiplicity_objective(predecessor, form, fold):
    ctx, rows = predecessor
    saved = next(r for r in rows if r["record_type"] == "fit" and r["candidate"] == form and r["fold"] == fold)
    point_seed = saved["onset_seed_Pd_bar"]
    assert T.E.start_values(form, {"Pd_bar": point_seed}) == T.E.start_values(form, ctx.saved[fold])
    evaluate, train, held, weights = T.evaluator(ctx, np.ones(len(ctx.brews.ids)), fold, saved["Mc_fixed_g"], form)
    z = T.E.coordinates(T.E.parameters(saved["parameters"], form), form)
    residual = evaluate(z)[0]
    assert_allclose(residual@residual, saved["objective"]["objective"], rtol=1e-12, atol=0)
    assert_allclose(weights, T.D.condition_weights(ctx.brews.condition[train]), rtol=1e-12, atol=0)
    assert list(train) == saved["training_indices"]


def test_prerefit_real_draw_weights_and_membership(predecessor):
    ctx, _ = predecessor
    indices, samples = T.C2.paired_samples(ctx.brews)
    assert np.array_equal(samples, T.C1.B.brew_samples(ctx.brews, 200, T.C1.SEED))
    assert np.array_equal(samples[0], np.bincount(indices[0], minlength=len(ctx.brews.ids)))
    sample = samples[0]
    for held in [None, *ctx.brews.groups]:
        fold = "DESCRIPTIVE_ALL" if held is None else ctx.brews.fold[held[0]]
        train = np.flatnonzero(sample > 0) if held is None else np.flatnonzero(
            (sample > 0) & (ctx.brews.condition != ctx.brews.condition[held[0]]))
        expected = np.array([sample[i]/np.sum(ctx.brews.condition == ctx.brews.condition[i]) for i in train])
        expected /= expected.sum()
        actual_train, actual_held, actual = T.training(ctx, sample, fold)
        assert np.array_equal(actual_train, train)
        assert held is None if actual_held is None else np.array_equal(actual_held, held)
        assert_allclose(actual, expected, rtol=1e-12, atol=0)


def test_prerefit_training_isolation(predecessor):
    ctx, _ = predecessor
    sample = T.C2.paired_samples(ctx.brews)[1][0]
    fold = "HYD-LOCO-2.0"
    evaluate, train, _, _ = T.evaluator(ctx, sample, fold, 29., "LC")
    z = T.E.coordinates([1.,15.,2.,4.,.1], "LC")
    before = evaluate(z)
    changed = copy.deepcopy(ctx)
    unused = np.setdiff1d(np.arange(len(sample)), train)
    changed.coarse.pressure[unused] = np.nan
    changed.coarse.flow[unused] = np.nan
    changed.coarse.mask[unused] = False
    after = T.evaluator(changed, sample, fold, 29., "LC")[0](z)
    for left, right in zip(before, after):
        assert_allclose(left, right, rtol=1e-12, atol=0)


def test_prerefit_plan_pin_and_no_finite_deadline(tmp_path):
    T.verify_plan()
    path = tmp_path/"PLAN.md"
    path.write_text("changed")
    with pytest.raises(RuntimeError, match="changed"):
        T.verify_plan(path)
    budget = T.C0.Deadline(float("inf"))
    budget.check()
    assert np.isinf(budget.end)


@pytest.fixture(scope="module")
def rows():
    return T.D.read_table(T.OUT/"RESULT_TABLE.csv")


@pytest.fixture(scope="module")
def ctx(rows):
    return T.context_from_fixture(next(r for r in rows if r["record_type"]=="inputs"))


def test_committed_scope_sources_and_rules(rows):
    p=next(r for r in rows if r["record_type"]=="provenance")
    assert p["plan_sha256"]==T.PLAN_SHA256
    assert (p["refit_count"],p["fit_count"],p["scheduled_start_count"],p["point_replay_count"])==(200,4800,43200,28)
    assert p["call_path"]["wall_clock_cap"] is None
    for path,digest in p["source_sha256"].items():
        if not path.startswith("external/"):
            assert hashlib.sha256((T.ROOT/path).read_bytes()).hexdigest()==digest
    auth=next(r for r in rows if r["record_type"]=="source_authentication")
    for path,digest in auth["expected_sha256"].items():
        assert auth["actual_sha256"][path]==digest
    summary=(T.OUT/"SUMMARY.md").read_text()
    assert '\u2014' not in summary
    for rule in (T.OUT/"PLAN.md").read_text().splitlines():
        if rule.startswith(tuple(f"R{i}." for i in range(1,10))):
            assert rule in summary
    assert T.INHERITED in summary
    assert len(p["external_start_records"])==4800


def test_committed_sampler_and_membership(rows,ctx):
    pairing=next(r for r in rows if r["record_type"]=="pairing")
    indices,samples=T.C2.paired_samples(ctx.brews)
    assert np.array_equal(indices,pairing["draw_indices"])
    assert np.array_equal(samples,pairing["multiplicities"])
    for row in (r for r in rows if r["record_type"]=="refit"):
        train,held,weights=T.training(ctx,samples[row["draw"]],row["fold"])
        assert list(train)==row["training_indices"]
        assert_allclose(weights,row["weights"],rtol=1e-12,atol=0)
        if held is not None:
            assert not set(train)&set(held)


def test_committed_Mc_onset_assertion_twins(rows,ctx):
    sample=next(r for r in rows if r["record_type"]=="pairing")["multiplicities"]
    bank={r["draw"]:r["bank"] for r in rows if r["record_type"]=="onset_Mc_assertions"}
    assert set(bank)==set(range(200))
    for draw,folds in bank.items():
        assert set(folds)==set(T.FOLDS)
        for fold,record in folds.items():
            assert_allclose(record["mc"],record["expected_mc"],rtol=1e-12,atol=0)
            for field in ("Pd_bar","P0_bar","b_s_bar","t0_s","objective_sum_squares"):
                assert_allclose(record["onset"][field],record["expected_onset"][field],rtol=1e-12,atol=0)
            train,held,_=T.training(ctx,np.array(sample[draw]),fold)
            audit=T.C2.margin_audit(record["onset"],ctx,train,held)
            _assert_replayed_fields(audit, record["margin"], f"draw={draw}.{fold}.margin")


def test_committed_objectives_starts_and_selection(rows,ctx):
    fits=[r for r in rows if r["record_type"]=="refit"]
    assert len(fits)==4800
    assert {(r["draw"],r["candidate"],r["fold"]) for r in fits}=={(i,f,g) for i in range(200) for f in T.FORMS for g in T.FOLDS}
    for row in fits:
        form=row["candidate"]
        attempts=[dict(zip(row["start_columns"],r)) for r in row["starts_compact"]]
        assert len(attempts)==(6 if form=="A" else 12)+int(row["fallback"])
        selected=attempts[row["selected_start"]]
        assert selected["success"]
        assert_allclose(selected["objective"],min(s["objective"] for s in attempts if s["success"]),rtol=1e-12,atol=0)
        assert_allclose(np.array(row["weights"])@row["training_mse"],row["objective"],rtol=1e-12,atol=0)
        assert_allclose(T.E.physical(np.array(selected["final_coordinates"]),form),T.E.parameters(row["parameters"],form),rtol=1e-12,atol=0)
        objectives=[s["objective"] for s in attempts]
        assert row["start_disagreement"]==(max(objectives)-min(objectives)>1e-6*max(1,row["objective"]))
        for r in attempts:
            assert np.isfinite(r["objective"]) and np.isfinite(r["initial_objective"])
            assert r["nfev"]<=1500
            assert all(r[k]>=0 for k in ("initial_structural","initial_numerical","final_structural","final_numerical"))
    baseline=[r for r in rows if r["record_type"]=="T2F_refit_replay"]
    assert len(baseline)==200
    for row in baseline:
        assert set(row["folds"])==set(T.FOLDS)
        for record in row["folds"].values():
            assert_allclose(np.array(record["weights"])@record["training_mse"],record["objective"],rtol=1e-12,atol=0)
            assert_allclose(record["objective"],record["saved_objective"],rtol=1e-12,atol=0)


def test_committed_metrics_intervals_and_grades(rows,ctx):
    samples=next(r for r in rows if r["record_type"]=="pairing")["multiplicities"]
    draw={r["draw"]:r for r in rows if r["record_type"]=="draw_metrics"}
    for index,row in draw.items():
        for form in (*T.FORMS,"T2-F"):
            expected=row["values"][form]["metrics"]
            actual=T.metric_values(ctx,row["values"][form]["arrays"],np.array(samples[index]))
            for key,value in actual.items():
                if value is None:
                    assert expected[key] is None
                else:
                    _assert_replayed_fields(value, expected[key], f"draw={index}.{form}.{key}")
    for row in (r for r in rows if r["record_type"]=="paired"):
        left,right=row["candidate"].split(" - ")
        values=[None if None in (draw[i]["values"][left]["metrics"][row["metric"]],draw[i]["values"][right]["metrics"][row["metric"]]) else
            draw[i]["values"][left]["metrics"][row["metric"]]-draw[i]["values"][right]["metrics"][row["metric"]] for i in range(200)]
        _assert_replayed_fields(values, row["differences"], f"{row['candidate']}.{row['metric']}.differences")
        _assert_replayed_fields(T.distribution(values), row["distribution"], f"{row['candidate']}.{row['metric']}.distribution")
    for row in (r for r in rows if r["record_type"]=="reading"):
        assert row["grades"]["onset"]=="NOT_SCORED"
        for key,saved in row["distributions"].items():
            _assert_replayed_fields(T.distribution([draw[i]["values"][row["candidate"]]["metrics"][key] for i in range(200)]),
                                   saved, f"{row['candidate']}.{key}.distribution")
        assert T.S.peak_grade(row["distributions"]["nominal_peak_bar"]["interval"])==row["grades"]["peak"]
        assert T.S.slope_grade(row["distributions"]["slope_g_s_bar"]["interval"])==row["grades"]["slope"]
        assert T.C0.bias_grade(row["center"]["low_pressure_bias_g_s"])==row["grades"]["low_pressure_bias"]
        assert row["scale_consistency"]["P0_consistency"]=="NOT_APPLICABLE"


def test_committed_scale_pairing(rows):
    onset={r["draw"]:r["bank"]["DESCRIPTIVE_ALL"]["onset"]["Pd_bar"] for r in rows if r["record_type"]=="onset_Mc_assertions"}
    for form in T.FORMS:
        flow={r["draw"]:r["parameters"]["Pd_bar"] for r in rows if r["record_type"]=="refit" and r["candidate"]==form and r["fold"]=="DESCRIPTIVE_ALL"}
        actual=T.D.plain(T.scale_comparison([flow[i] for i in range(200)],[onset[i] for i in range(200)],form=="A"))
        saved=next(r for r in rows if r["record_type"]=="reading" and r["candidate"]==form)["scale_consistency"]
        _assert_replayed_fields(actual, saved, f"{form}.scale_consistency")


@pytest.mark.parametrize("form,fold",[(f,g) for f in T.FORMS for g in (*T.FOLDS,*T.C.OMITTED)])
def test_committed_point_twin(rows,ctx,form,fold):
    row=next(r for r in rows if r["record_type"]=="point_replay" and r["candidate"]==form and r["fold"]==fold)
    _,train,held,_=T.C.design(ctx.brews.condition,fold)
    p=T.E.parameters(row["parameters"],form)
    q=T.E.flow(p,ctx.coarse.pressure[train],ctx.coarse.t,row["Mc_fixed_g"],form,False)[0]
    objective=T.C.objective_parts(ctx.brews.condition[train],T.C.trace_mse(q,ctx.coarse.flow[train],ctx.coarse.mask[train]))
    assert_allclose(objective["objective"],row["objective"]["objective"],rtol=1e-12,atol=0)
    predicted=T.E.brew_records(ctx,p,row["Mc_fixed_g"],form,train,held)
    for actual,saved in zip(predicted,row["brew_predictions"]):
        for key in ("endpoint_prediction_g_s","endpoint_residual_g_s","trace_mse","predicted_late_trend_g_s_s"):
            assert_allclose(actual[key],saved[key],rtol=1e-12,atol=0)
    evaluate=T.E.Evaluator(ctx.coarse.pressure[train],ctx.coarse.t,ctx.coarse.flow[train],ctx.coarse.mask[train],
        ctx.brews.condition[train],row["Mc_fixed_g"],form,T.C0.Deadline(float("inf")))
    checks=[(row["starts"][row["selected_start"]]["final_coordinates"],row["jacobian_check"])]
    checks += [(s["initial_coordinates"],s["initial_jacobian_check"]) for s in row["starts"] if "initial_jacobian_check" in s]
    for z,check in checks:
        assert_allclose(np.linalg.norm(evaluate(np.array(z))[1]),check["analytic_norm"],rtol=1e-12,atol=0)
        assert check["half_step_error_decreases"]==(check["half_absolute_error"]<check["full_absolute_error"])
        for relative,absolute in (("full_relative_error","full_absolute_error"),("half_relative_error","half_absolute_error")):
            if check["analytic_norm"]:
                assert_allclose(check[relative],check[absolute]/check["analytic_norm"],rtol=1e-12,atol=0)


@pytest.mark.slow
def test_raw_authentication_and_input_twin(rows):
    if not T.RAW.exists() or not T.CACHE.exists():
        pytest.skip("Owner raw records are not mounted")
    inputs=next(r for r in rows if r["record_type"]=="inputs")
    sources=T.E.source_hashes(T.RAW,T.CACHE,inputs["brew_ids"])
    source=next(r for r in rows if r["record_type"]=="source_authentication")
    assert sources==source["actual_sha256"]
    ctx=T.D.load_context(T.RAW,T.CACHE)
    actual=T.C.input_fixture(ctx)
    for key in ("fit_pressure","fit_observed_flow","fine_pressure","fine_observed_flow","endpoint_pressure","endpoint_observed_g_s","early_pressure_bar","observed_onsets_s"):
        assert_allclose(actual[key],inputs[key],rtol=1e-12,atol=0)
    assert actual["brew_ids"]==inputs["brew_ids"]


@pytest.mark.slow
def test_all_committed_T2F_objective_trajectories(rows,ctx):
    """CSV-only numerical twin, also runnable when private raw data are absent."""
    for row in (r for r in rows if r["record_type"]=="T2F_refit_replay"):
        for record in row["folds"].values():
            train=np.array(record["training_indices"])
            p=record["parameters"]
            q=T.C1.flow_curve(T.C1.flow_parameters(p),ctx.coarse.pressure[train],ctx.coarse.t,p["Mc_fixed_g"])[0]
            mse=T.C.trace_mse(q,ctx.coarse.flow[train],ctx.coarse.mask[train])
            assert_allclose(mse,record["training_mse"],rtol=1e-12,atol=0)


@pytest.mark.slow
def test_all_committed_refit_objective_trajectories(rows,ctx):
    for row in (r for r in rows if r["record_type"]=="refit"):
        train=np.array(row["training_indices"])
        p=T.E.parameters(row["parameters"],row["candidate"])
        q=T.E.flow(p,ctx.coarse.pressure[train],ctx.coarse.t,row["parameters"]["Mc_fixed_g"],row["candidate"],False)[0]
        mse=T.C.trace_mse(q,ctx.coarse.flow[train],ctx.coarse.mask[train])
        assert_allclose(mse,row["training_mse"],rtol=1e-12,atol=0)


def test_committed_saved_details(rows,ctx):
    points={(r['candidate'],r['fold']):r for r in rows if r['record_type']=='point_replay'}
    refs={r['fold']:r for r in rows if r['record_type']=='point_reference'}
    for (form,fold),point in points.items():
        ref=refs[fold] if form=='A' else points['A',fold]
        for key,field in (('coarse_gain','objective'),('fine_gain','fine_objective')):
            assert_allclose(ref[field]['objective']-point[field]['objective'],point[key],rtol=1e-12,atol=0)
        if form=='LC':
            train=np.array(point['training_indices'])
            p=np.r_[T.E.parameters(ref['parameters'],'A'),0.]
            q=T.E.flow(p,ctx.coarse.pressure[train],ctx.coarse.t,point['Mc_fixed_g'],form,False)[0]
            objective=T.C.objective_parts(ctx.brews.condition[train],T.C.trace_mse(q,ctx.coarse.flow[train],ctx.coarse.mask[train]))['objective']
            assert_allclose(objective,point['nested_benchmark']['A_embedded_objective'],rtol=1e-12,atol=0)
    for row in (r for r in rows if r['record_type']=='saved_comparator'):
        for key,value in row['saved_metrics'].items():
            assert_allclose(row['metrics'][key],value,rtol=1e-12,atol=0)
        if 'onset' in row['arrays']:
            actual=T.C0.loss(ctx.brews,(np.array(row['arrays']['onset'])-ctx.delay)**2)
            assert_allclose(actual,row['saved_metrics']['onset_rmse_s'],rtol=1e-12,atol=0)
        for fold,record in row['objective_replays'].items():
            assert_allclose(record['actual'],record['saved'],rtol=1e-12,atol=0)
    replay=next(r for r in rows if r['record_type']=='T2F_interval_replay')
    for key,record in replay['comparisons'].items():
        values=[r['values']['T2-F']['metrics'][key] for r in rows if r['record_type']=='draw_metrics']
        assert_allclose(T.A.interval(values),record['saved'],rtol=1e-12,atol=0)


@pytest.mark.slow
def test_committed_held_out_trajectory_twins(rows,ctx):
    fits={(r['draw'],r['candidate'],r['fold']):r for r in rows if r['record_type']=='refit'}
    t2={r['draw']:r['folds'] for r in rows if r['record_type']=='T2F_refit_replay'}
    for row in (r for r in rows if r['record_type']=='draw_metrics'):
        for form in (*T.FORMS,'T2-F'):
            bank={fold:fits[row['draw'],form,fold] for fold in T.FOLDS} if form in T.FORMS else t2[row['draw']]
            actual=T.prediction_arrays(ctx,bank,form)
            for key,value in actual.items():
                assert_allclose(value,row['values'][form]['arrays'][key],rtol=1e-12,atol=0)


def test_committed_start_diagnostic_arithmetic(rows):
    for reading in (r for r in rows if r['record_type']=='reading'):
        fits=[r for r in rows if r['record_type']=='refit' and r['candidate']==reading['candidate']]
        assert sum(v['starts'] for v in reading['seed_group_totals'].values())==reading['start_totals']['scheduled']
        for key in ('initial_structural','initial_numerical','final_structural','final_numerical'):
            assert sum(v[key] for v in reading['seed_group_totals'].values())==reading['start_totals'][key]
        for key,value in reading['maximum_start_parameter_spans'].items():
            assert_allclose(max(r['parameter_ranges'][key][1]-r['parameter_ranges'][key][0] for r in fits),value,rtol=1e-12,atol=0)
