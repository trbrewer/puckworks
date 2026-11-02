"""C3e synthetic numerics and committed-field replays; no fitting in CI."""
import copy
import hashlib
import time
from types import SimpleNamespace

import numpy as np
from numpy.testing import assert_allclose
import pytest

from puckworks.analysis import pressure_peak_stage_c3e as E


def budget():
    return E.C.C0.Deadline(time.monotonic()+120)


def close(actual, expected):
    if isinstance(expected, dict):
        for key, value in expected.items():
            close(actual.get(key), value)
    elif isinstance(expected, (list, tuple)):
        assert len(actual) == len(expected)
        for left, right in zip(actual, expected):
            close(left, right)
    elif isinstance(expected, float):
        assert_allclose(actual, expected, rtol=1e-12, atol=0)
    else:
        assert actual == expected


def test_numerical_scope_and_starts():
    saved = dict(Pd_bar=7.37)
    assert len(E.SCHEDULE) == 56
    assert sum(len(E.start_values(f, saved)) for f, _ in E.SCHEDULE) == 504
    for form in E.FORMS:
        values = E.start_values(form, saved)
        expected = E.S.start_values("A", saved)
        if form in ("M2", "LC"):
            expected = [(g, [*p, v]) for g, p in expected for v in (0., .3 if form == "M2" else .1)]
        close(values, expected)
        lo, hi = E.bounds(form)
        assert np.isinf(hi[2])
        for _, p in values:
            assert_allclose(E.physical(E.coordinates(p, form), form), p, rtol=1e-12, atol=0)
        if len(lo) == 5:
            assert_allclose([lo[4], hi[4]], [0., 10. if form == "M2" else 1.], rtol=1e-12, atol=0)


def test_numerical_identities_derivatives_and_limits():
    fixture = E.numerical_fixtures(budget())
    assert fixture["nested_identities"] and fixture["exact_zero_clock"]
    assert all(v["half_step_error_decreases"] for v in fixture["smooth_jacobians"].values())
    t = np.linspace(0., 100., 201)
    pressure = np.full((1,len(t)),2.)
    for p,column in (([1.,20.,1.,4.,.4],4),([1.,20.,3.,4.,1.],2)):
        jac = E.flow(p,pressure,t,28.7,"LC")[1]
        assert_allclose(jac[...,column],0.,rtol=1e-12,atol=0)


def test_numerical_m1_exact_recovery_solution():
    t = np.linspace(0., 100., 201)
    pressure = np.full((1, len(t)), 2.)
    p, mc = np.array([1.2, 20., 2., 4.]), 28.7
    q, m, cap = E.flow(p, pressure, t, mc, "M1", False)
    exposure = cap[0, 0]*t/mc
    expected_mass = mc*np.log1p(np.expm1(exposure)/np.e)
    assert_allclose(m[0], expected_mass, rtol=1e-12, atol=0)
    assert_allclose(q[0], cap[0]*(1-(1-np.exp(-1))*np.exp(-m[0]/mc)), rtol=1e-12, atol=0)


def test_numerical_clock_no_pause_and_grid_direction():
    # Independent physical ODE, RK4, as a convergence reference. No tolerance band.
    p, mc = np.array([1.2, 20., 2.3, 4., .3]), 28.7
    c = E.capacity(p, np.array([2.]), "M2")[0][0]
    m = 0.
    dt = .01
    for j in range(10000):
        t = j*dt
        def rhs(s, mass):
            return c*np.exp(-np.exp(-(mass+p[4]*s)/mc))
        a = rhs(t, m)
        b = rhs(t+dt/2, m+dt*a/2)
        d = rhs(t+dt/2, m+dt*b/2)
        e = rhs(t+dt, m+dt*d)
        m += dt*(a+2*b+2*d+e)/6
    errors = []
    for step in (.5, .25):
        t = np.arange(0., 100.+step/2, step)
        _, mass, _ = E.flow(p, np.full((1, len(t)), 2.), t, mc, "M2", False)
        errors.append(abs(mass[0, -1]-m))
    assert errors[1] < errors[0]
    t = np.linspace(0., 100., 201)
    cap, dc = E.capacity(p, np.zeros((1, len(t))), "M2")
    mass, state, _ = E._clock_state(cap, dc, t, mc, p[4])
    assert_allclose(mass, 0., rtol=1e-12, atol=0)
    assert_allclose(state[0], p[4]*t/mc, rtol=1e-12, atol=0)


def test_numerical_capacity_peak_global_and_degeneracies():
    p = np.array([1.2, 20., 1., 4.])
    expected = p[3]*np.log1p(p[1]/p[3])
    for form in E.FORMS:
        values = np.r_[p, .3] if form in ("M2", "LC") else p
        assert_allclose(E.global_peak(values, form)["pressure_bar"], expected, rtol=1e-12, atol=0)
    # A mixture with well-separated component scales must consider both peaks.
    p = np.array([1., 1., 8., 6., .1])
    result = E.global_peak(p, "LC")
    dense = E.capacity(p, np.linspace(0., 30., 30001), "LC")[0]
    assert result["capacity_g_s"] >= dense.max()
    assert len(result["stationary_pressures_bar"]) >= 3


@pytest.mark.parametrize("form", E.FORMS)
def test_numerical_training_isolation_and_domain(form):
    conditions = np.repeat(E.C.CONDITIONS, 2)
    t = np.arange(0., 10.5, .5)
    pressure = np.broadcast_to(conditions[:, None], (len(conditions), len(t))).copy()
    grid = SimpleNamespace(t=t, pressure=pressure, flow=np.ones_like(pressure), mask=np.ones_like(pressure,dtype=bool))
    ctx = SimpleNamespace(brews=SimpleNamespace(condition=conditions), coarse=grid,
        saved={f: dict(Mc_fixed_g=28., Pd_bar=4.) for f in E.C.STANDARD})
    fold = "HYD-LOCO-1.0-OMIT-3.5"
    source, train, held, omitted = E.C.design(conditions, fold)
    p = E.start_values(form, ctx.saved[source])[-1][1]
    z = E.coordinates(p, form)
    before = E.training_evaluator(ctx, form, fold, budget())(z)
    changed = copy.deepcopy(ctx)
    unused = np.r_[held, omitted]
    changed.coarse.pressure[unused] = np.nan
    changed.coarse.flow[unused] = np.nan
    changed.coarse.mask[unused] = False
    after = E.training_evaluator(changed, form, fold, budget())(z)
    for a, b in zip(before, after):
        assert_allclose(a, b, rtol=1e-12, atol=0)
    assert not set(train)&set(unused)
    z[2] = .9
    with pytest.raises(ValueError, match="outside declared domain"):
        E.training_evaluator(ctx, form, fold, budget())(z)


@pytest.fixture(scope="module")
def rows():
    return E.read_table()


@pytest.fixture(scope="module")
def data(rows):
    r = next(r for r in rows if r["record_type"] == "inputs")
    arrays = ("conditions_bar", "fit_times_s", "fit_pressure", "fit_observed_flow", "fit_mask", "fine_times_s",
              "fine_pressure", "fine_observed_flow", "fine_mask", "endpoint_times_s", "endpoint_pressure", "endpoint_observed_g_s")
    return {k: np.asarray(v) if k in arrays else v for k, v in r.items()}


def test_committed_sources_scope_labels(rows):
    p = next(r for r in rows if r["record_type"] == "provenance")
    assert p["fit_count"] == 56 and p["start_count"] == 504
    assert p["bootstrap_count"] == p["onset_refits"] == p["profiling_count"] == 0
    assert p["cumulative_wall_seconds"] < p["cap_seconds"] == 7200
    assert p["plan_sha256"] == E.PLAN_SHA256
    for path, digest in p["source_sha256"].items():
        if not path.startswith("external/"):
            assert hashlib.sha256((E.ROOT/path).read_bytes()).hexdigest() == digest
    fits = [r for r in rows if r["record_type"] == "fit"]
    assert [(r["candidate"], r["fold"]) for r in fits] == list(E.SCHEDULE)
    assert all(r["status"] == "complete" and "TARGET_EXPOSED" in r["exposure"] for r in fits)
    summary = (E.OUT/"SUMMARY.md").read_text()
    assert '\u2014' not in summary
    assert all(s in summary for s in ("in-sample", "PHYSICAL_VALIDATION=NOT_ESTABLISHED", "3.5-bar information remains in Mc"))


@pytest.mark.parametrize("form,fold", [
    pytest.param(form,fold,marks=pytest.mark.slow if form=="M2" else ())
    for form,fold in E.SCHEDULE
])
def test_committed_fit_replays(rows, data, form, fold):
    row = next(r for r in rows if r["record_type"] == "fit" and r["candidate"] == form and r["fold"] == fold)
    source, train, held, omitted = E.C.design(data["conditions_bar"], fold)
    bank = data["saved_parameters_by_fold"][source]
    assert row["training_indices"] == list(train)
    assert row["held_out_indices"] == list(held) and row["omitted_indices"] == list(omitted)
    assert row["Mc_bank_training_indices"] == list(E.C.design(data["conditions_bar"],source)[1])
    assert_allclose(row["Mc_fixed_g"], bank["Mc_fixed_g"], rtol=1e-12, atol=0)
    lo, hi = E.bounds(form)
    starts = E.start_values(form, bank)
    assert len(starts) == len(row["starts"])
    ids = [data["brew_ids"][i] for i in train]
    for (group, original), attempt in zip(starts, row["starts"]):
        assert attempt["seed_group"] == group
        assert_allclose(attempt["original_start_coordinates"], E.coordinates(original,form), rtol=1e-12, atol=0)
        assert_allclose(attempt["initial_coordinates"], np.clip(E.coordinates(original,form),lo+1e-10,hi-1e-10), rtol=1e-12, atol=0)
        for phase in ("initial","final"):
            p = E.parameters(attempt[phase+"_parameters"],form)
            close(E.zero_counts(p,form,data["fit_pressure"][train],data["fit_mask"][train],data["conditions_bar"][train],ids), attempt[phase+"_training_counts"])
            q = E.flow(p,data["fit_pressure"][train],data["fit_times_s"],row["Mc_fixed_g"],form,False)[0]
            loss = E.C.objective_parts(data["conditions_bar"][train],E.C.trace_mse(q,data["fit_observed_flow"][train],data["fit_mask"][train]))["objective"]
            assert_allclose(loss,attempt["initial_objective" if phase=="initial" else "objective"],rtol=1e-12,atol=0)
    attempts = row["starts"]+([row["fallback"]] if row.get("fallback") else [])
    selected = attempts[row["selected_start"]]
    assert selected["success"]
    assert_allclose(selected["objective"],min(s["objective"] for s in attempts if s["success"]),rtol=1e-12,atol=0)
    p = E.parameters(row["parameters"],form)
    close(row["parameters"],selected["final_parameters"])
    close(E.S.seed_groups(attempts,row["selected_start"]),row["seed_audit"])
    for prefix in ("fit","fine"):
        q = E.flow(p,data[prefix+"_pressure"][train],data[prefix+"_times_s"],row["Mc_fixed_g"],form,False)[0]
        part = E.C.objective_parts(data["conditions_bar"][train],E.C.trace_mse(q,data[prefix+"_observed_flow"][train],data[prefix+"_mask"][train]))
        close(E.D.plain(part),row["objective" if prefix=="fit" else "fine_objective"])
    q,m,c = E.flow(p,data["endpoint_pressure"],data["endpoint_times_s"],row["Mc_fixed_g"],form,False)
    fine = E.flow(p,data["fine_pressure"],data["fine_times_s"],row["Mc_fixed_g"],form,False)[0]
    trace_mse = E.C.trace_mse(fine,data["fine_observed_flow"],data["fine_mask"])
    trends = (fine*np.array(data["late_weights"])).sum(axis=1)
    assert_allclose(trace_mse,[b["trace_mse"] for b in row["brew_predictions"]],rtol=1e-12,atol=0)
    assert_allclose(trends,[b["predicted_late_trend_g_s_s"] for b in row["brew_predictions"]],rtol=1e-12,atol=0)
    for i,b in enumerate(row["brew_predictions"]):
        assert b["role"] == ("training" if i in train else "held_out" if i in held else "omitted")
        assert_allclose([q[i,-1],m[i,-1],c[i,-1],q[i,-1]-data["endpoint_observed_g_s"][i]],
                        [b["endpoint_prediction_g_s"],b["hydraulic_mass_100_g"],b["capacity_100_g_s"],b["endpoint_residual_g_s"]],rtol=1e-12,atol=0)
        assert_allclose(q[i,-1],c[i,-1]*b["memory_multiplier_100"],rtol=1e-12,atol=0)
    close(E.D.plain(E.global_peak(p,form)),row["capacity_peak"])
    e = E.Evaluator(data["fit_pressure"][train],data["fit_times_s"],data["fit_observed_flow"][train],data["fit_mask"][train],data["conditions_bar"][train],row["Mc_fixed_g"],form,budget())
    diag = E.S.jacobian_diagnostic(e,np.array(selected["final_coordinates"]),lo,hi)
    assert_allclose(diag["analytic_norm"],row["jacobian_check"]["analytic_norm"],rtol=1e-12,atol=0)
    for key in ("full_branch_switches","half_branch_switches","half_step_error_decreases"):
        assert diag[key] == row["jacobian_check"][key]
    if form in ("M2","LC"):
        base = next(r for r in rows if r["record_type"]=="fit" and r["candidate"]=="A" and r["fold"]==fold)
        assert not row["nested_benchmark"]["materially_worse"]
        assert_allclose(row["nested_benchmark"]["A_embedded_objective"],base["objective"]["objective"],rtol=1e-12,atol=0)


def test_committed_readings_and_fd_arithmetic(rows):
    fits = [r for r in rows if r["record_type"]=="fit"]
    references = [r for r in rows if r["record_type"]=="reference"]
    saved = [r for r in rows if r["record_type"]=="reading"]
    assert all(r["claim"] == E.D.CLAIM for r in saved)
    # The inherited CSV writer supplies the envelope claim, not readings().
    close(E.readings(fits,references),[
        {k:v for k,v in r.items() if k != "claim"} for r in saved
    ])
    checks = []
    for r in fits:
        checks.append(r["jacobian_check"])
        checks.extend(s["initial_jacobian_check"] for s in r["starts"] if "initial_jacobian_check" in s)
    for check in checks:
        for relative,absolute in (("full_relative_error","full_absolute_error"),("half_relative_error","half_absolute_error"),("half_step_relative_change","half_step_absolute_change")):
            if check["analytic_norm"]:
                assert_allclose(check[relative],check[absolute]/check["analytic_norm"],rtol=1e-12,atol=0)
            else:
                assert check[relative] is None
        assert check["half_step_error_decreases"] == (check["half_absolute_error"]<check["full_absolute_error"])


@pytest.mark.parametrize("fold", E.FOLDS)
def test_committed_t2f_reference_replay(rows, data, fold):
    r = next(r for r in rows if r["record_type"]=="reference" and r["fold"]==fold)
    source,train,_,_ = E.C.design(data["conditions_bar"],fold)
    bank = data["saved_parameters_by_fold"][source]
    for prefix in ("fit","fine"):
        q = E.S.C1.flow_curve(E.S.C1.flow_parameters(bank),data[prefix+"_pressure"][train],data[prefix+"_times_s"],bank["Mc_fixed_g"])[0]
        part = E.C.objective_parts(data["conditions_bar"][train],E.C.trace_mse(q,data[prefix+"_observed_flow"][train],data[prefix+"_mask"][train]))
        close(E.D.plain(part),r["objective" if prefix=="fit" else "fine_objective"])
    if fold in E.C.STANDARD:
        assert_allclose(r["objective"]["objective"],bank["objective_sum_squares"],rtol=1e-12,atol=0)
    if fold=="DESCRIPTIVE_ALL":
        assert_allclose(r["objective"]["objective"],.0719361259858887,rtol=1e-12,atol=0)
    q = E.S.C1.flow_curve(E.S.C1.flow_parameters(bank),data["endpoint_pressure"],data["endpoint_times_s"],bank["Mc_fixed_g"])[0]
    assert_allclose(q[:,-1],[b["endpoint_prediction_g_s"] for b in r["brew_predictions"]],rtol=1e-12,atol=0)


def test_committed_c3d_replay(rows, data):
    replay = next(r for r in rows if r["record_type"]=="c3d_replay")["fits"]
    saved = [r for r in E.S.read_table() if r["record_type"]=="fit" and r["candidate"]=="A"]
    assert len(replay)==len(saved)==5
    for r,s in zip(replay,saved):
        assert r["fold"]==s["fold"]
        close(r["parameters"],s["parameters"])
        assert_allclose(r["objective"],s["objective"]["objective"],rtol=1e-12,atol=0)
        p = E.parameters(r["parameters"],"A")
        q = E.flow(p,data["endpoint_pressure"],data["endpoint_times_s"],r["parameters"]["Mc_fixed_g"],"A",False)[0]
        assert_allclose(q[:,-1],r["endpoint_predictions_g_s"],rtol=1e-12,atol=0)
        assert_allclose(r["endpoint_predictions_g_s"],[b["endpoint_prediction_g_s"] for b in s["brew_predictions"]],rtol=1e-12,atol=0)


def test_committed_all_forms_quick_csv_twin(rows, data):
    """Quick CI arithmetic for every fit; full M2 trajectory replays are slow."""
    for row in (r for r in rows if r['record_type']=='fit'):
        form = row['candidate']
        source,train,held,omitted = E.C.design(data['conditions_bar'],row['fold'])
        assert row['training_indices']==list(train)
        assert row['held_out_indices']==list(held) and row['omitted_indices']==list(omitted)
        assert_allclose(row['Mc_fixed_g'],data['saved_parameters_by_fold'][source]['Mc_fixed_g'],rtol=1e-12,atol=0)
        for field in ('objective','fine_objective'):
            part = row[field]
            expected = E.C.objective_parts(data['conditions_bar'][train],np.array(part['brew_mse']))
            close(E.D.plain(expected),part)
        attempts = row['starts']+([row['fallback']] if row.get('fallback') else [])
        selected = attempts[row['selected_start']]
        close(row['parameters'],selected['final_parameters'])
        assert_allclose(row['objective']['objective'],min(s['objective'] for s in attempts if s['success']),rtol=1e-12,atol=0)
        p = E.parameters(row['parameters'],form)
        cap = E.capacity(p,data['endpoint_pressure'][:,-1],form)[0]
        for i,b in enumerate(row['brew_predictions']):
            assert_allclose(b['endpoint_observed_g_s'],data['endpoint_observed_g_s'][i],rtol=1e-12,atol=0)
            assert_allclose(b['endpoint_residual_g_s'],b['endpoint_prediction_g_s']-b['endpoint_observed_g_s'],rtol=1e-12,atol=0)
            assert_allclose(b['capacity_100_g_s'],cap[i],rtol=1e-12,atol=0)
            x = b['hydraulic_mass_100_g']+(p[4]*data['endpoint_times_s'][-1] if form=='M2' else 0.)
            assert_allclose(b['conditioning_X_100_g'],x,rtol=1e-12,atol=0)
            memory = 1-(1-np.exp(-1))*np.exp(-x/row['Mc_fixed_g']) if form=='M1' else np.exp(-np.exp(-x/row['Mc_fixed_g']))
            assert_allclose(b['endpoint_prediction_g_s'],cap[i]*memory,rtol=1e-12,atol=0)
        close(E.S.condition_records(row['brew_predictions']),row['condition_predictions'])
        for (group,start),attempt in zip(E.start_values(form,data['saved_parameters_by_fold'][source]),row['starts']):
            assert group==attempt['seed_group']
            assert_allclose(attempt['original_start_coordinates'],E.coordinates(start,form),rtol=1e-12,atol=0)
            for phase in ('initial','final'):
                params=E.parameters(attempt[phase+'_parameters'],form)
                counts=E.zero_counts(params,form,data['fit_pressure'][train],data['fit_mask'][train],data['conditions_bar'][train],[data['brew_ids'][i] for i in train])
                close(counts,attempt[phase+'_training_counts'])
        if form in ('M2','LC'):
            assert not row['nested_benchmark']['materially_worse']
