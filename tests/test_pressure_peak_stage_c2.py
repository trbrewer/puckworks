"""C2 training separation, floor-free fits, parent identities and recovery."""
import json
import os
from pathlib import Path
import time
from types import SimpleNamespace

import numpy as np
import pytest

from puckworks.analysis import pressure_peak_stage_c2 as C


def synthetic(c0=False, high=False):
    t = np.linspace(0., 100., 31)
    early = np.array([.8, 1.3, 2., 3.5, 5., 7., 9., 13.])
    if high:
        early += 6.
    pressure = early[:, None]*(1+.02*np.sin(t/12))[None, :]
    expected = np.array([1.6, 6.4, .55, 3., 8.]) if c0 else np.array([1.6, 16., .55, 3.2, 3., 8.])
    target = (C.C0.flow_curve(expected[:3], pressure, t, 29.) if c0 else
              C.C1.flow_curve(expected[:4], pressure, t, 29.))[0]
    timing = expected[1:] if c0 else expected[[3, 2, 4, 5]]
    delay = C.C0.onset_curve(timing, early)[0]
    args = (pressure, t, target, np.broadcast_to(t >= 20., target.shape), early, delay,
            np.full(len(early), 1/len(early)), 29., C.C0.Deadline(time.monotonic()+60))
    return expected, args


@pytest.mark.parametrize("c0,kind", [(False, "onset"), (False, "joint"), (False, "fixed"),
                                   (True, "onset"), (True, "joint")])
def test_synthetic_recovery_and_training_floor_inactive(c0, kind):
    expected, args = synthetic(c0)
    fit = C.fit_c0 if c0 else C.fit_t2
    kwargs = {"pd_fixed": expected[3]} if kind == "fixed" else {}
    record = fit(kind, *args, **kwargs)
    names = ("a_g_s_bar", "Pstar_bar", "P0_bar", "b_s_bar", "t0_s") if c0 else C.FIELDS
    fields = [k for k in names if k in record]
    np.testing.assert_allclose([record[k] for k in fields], [expected[names.index(k)] for k in fields],
                               rtol=2e-5, atol=1e-7)
    if kind != "fixed":
        margin = args[4]-record["P0_bar"]
        assert np.all(margin >= C.C0.EPSILON)
        coef = C.C0.physical_onset(record) if c0 else C.C1.onset_parameters(record)
        ps, p0, b, t0 = coef
        np.testing.assert_allclose(C.C0.onset_curve(coef, args[4])[0],
                                   t0+b*np.exp(args[4]/ps)/(args[4]-p0), rtol=1e-12, atol=0)


@pytest.mark.parametrize("c0", [False, True])
@pytest.mark.parametrize("kind", ["onset", "joint"])
def test_cap_at_five_reproduces_uncapped_parent(c0, kind):
    _, args = synthetic(c0, high=True)
    np.testing.assert_allclose(C.onset_cap(args[4]), 5., rtol=0, atol=0)
    parent, fit = (C.C0.fit, C.fit_c0) if c0 else (C.C1.fit, C.fit_t2)
    C.assert_parameters(fit(kind, *args), parent(kind, *args))


@pytest.mark.parametrize("c0", [False, True])
def test_flow_only_identity_does_not_use_onset_cap(c0):
    _, args = synthetic(c0)
    args = (*args[:4], np.full_like(args[4], np.nan), *args[5:])
    parent, fit = (C.C0.fit, C.fit_c0) if c0 else (C.C1.fit, C.fit_t2)
    C.assert_parameters(fit("flow", *args), parent("flow", *args))


def test_t2_fixed_flow_threshold_remains_uncapped():
    expected, args = synthetic()
    expected[2] = 1.1  # Above min(Pe)-0.01; legal for the separate flow threshold.
    target = C.C1.flow_curve(expected[:4], args[0], args[1], 29.)[0]
    changed = (*args[:2], target, *args[3:])
    record = C.fit_t2("fixed", *changed, pd_fixed=expected[3])
    C.assert_parameters(record, C.C1.fit("fixed", *changed, pd_fixed=expected[3]))
    assert record["P0_bar"] > C.onset_cap(args[4])
    np.testing.assert_allclose(C.C1.flow_parameters(record), expected[:4], rtol=2e-5, atol=1e-7)


def test_cap_binding_training_fit_keeps_floor_inactive():
    _, args = synthetic()
    early = args[4]
    # A truth on the cap exercises the active upper bound and the floor edge.
    delay = C.C0.onset_curve([3.2, C.onset_cap(early), 3., 8.], early)[0]
    record = C.fit_t2("onset", *args[:5], delay, *args[6:])
    assert record["P0_cap_binds"]
    assert np.all(early-record["P0_bar"] >= C.C0.EPSILON)
    np.testing.assert_allclose(record["P0_bar"], C.onset_cap(early), rtol=1e-7, atol=0)


def test_fold_cap_excludes_held_out_and_zero_multiplicity_brews(monkeypatch):
    t = np.array([0., 50., 100.])
    condition = np.repeat([1., 5., 9.], 2)
    early = np.array([.01, .8, .02, 4., 8., 9.])
    groups = [np.flatnonzero(np.isclose(condition, p)) for p in [1., 5., 9.]]
    pressure = np.repeat(condition[:, None], len(t), axis=1)
    brews = SimpleNamespace(ids=[str(i) for i in range(6)], condition=condition, pressure=pressure, t=t,
                            groups=groups, fold=[f"HYD-LOCO-{p}" for p in condition])
    course = SimpleNamespace(brews=brews, pressure=pressure, t=t, flow=np.ones_like(pressure),
                             mask=np.ones_like(pressure, dtype=bool))
    ctx = SimpleNamespace(coarse=course, fine=course, early=early, delay=np.full(6, 15.))
    sample = np.array([0, 2, 0, 2, 1, 1])
    def mc_fit(model, course, train, multiplicity, budget):
        np.testing.assert_allclose(multiplicity, sample, rtol=0, atol=0)
        return np.array([1., 7., 29.])
    def fake_fit(kind, pressure, t, target, mask, early, delay, weights, mc, budget, pd_fixed=None):
        return dict(a_g_s_bar=1.6, Pstar_bar=16., P0_bar=C.onset_cap(early)-.02,
                    Pd_bar=3.2 if pd_fixed is None else pd_fixed, b_s_bar=3., t0_s=8.,
                    Mc_fixed_g=mc, bound_hits=[], P0_cap_binds=False)
    monkeypatch.setattr(C.B, "fit_course", mc_fit)
    monkeypatch.setattr(C, "fit_t2", fake_fit)
    monkeypatch.setattr(C, "fit_c0", fake_fit)
    monkeypatch.setattr(C.C1, "fit", fake_fit)
    result = C.fit_folds(ctx, sample, time.monotonic()+60)
    for kind in C.ONSET_KINDS:
        for fold, audit in result[kind]["audits"].items():
            train = sample > 0
            if fold != "DESCRIPTIVE_ALL":
                train &= ~np.isclose(condition, float(fold.removeprefix("HYD-LOCO-")))
            np.testing.assert_allclose(audit["P0_upper_bar"], np.min(early[train])-.01, rtol=0, atol=0)
            assert audit["training_min_margin_bar"] >= .01
            for held in audit["held_out_floor_brews"]:
                record = result[kind]["bank"][fold]
                coef = C.C0.physical_onset(record) if kind.startswith("c0_") else C.C1.onset_parameters(record)
                np.testing.assert_allclose(held["predicted_onset_s"], C.C0.onset_curve(coef, [held["Pe_bar"]])[0][0],
                                           rtol=1e-12, atol=0)
        assert result[kind]["audits"]["HYD-LOCO-1.0"]["held_out_floor_brews"]
    for f, record in result["fixed"]["bank"].items():
        np.testing.assert_allclose(record["Pd_bar"], result["onset"]["bank"][f]["Pd_bar"], rtol=0, atol=0)


def test_resamples_match_c1_indices_and_order():
    brews = SimpleNamespace(ids=list(range(6)), groups=[np.array([0, 1]), np.array([2, 3, 4, 5])])
    indices, counts = C.paired_samples(brews)
    np.testing.assert_allclose(counts, C.C1.B.brew_samples(brews, 200, C.C1.SEED), rtol=0, atol=0)
    for index, count in zip(indices, counts):
        np.testing.assert_allclose(np.bincount(index, minlength=6), count, rtol=0, atol=0)


def check_saved_training_margins(rows, early):
    diagnostics = json.loads(rows[0]["diagnostics"])
    folds = np.array(diagnostics["pairing"]["brew_folds"])
    brews = np.array(diagnostics["pairing"]["brew_order"])
    samples = np.array(diagnostics["pairing"]["multiplicities"])
    checked = 0
    for row in rows[:5]:
        if row["fit_type"] == "fixed":
            continue
        cases = [(np.ones(len(early)), json.loads(row["parameters_by_fold"]), json.loads(row["margin_audit_by_fold"]))]
        cases += list(zip(samples, json.loads(row["refit_parameters_by_fold"]), json.loads(row["refit_margin_audit_by_fold"])))
        for sample, bank, audits in cases:
            for fold, record in bank.items():
                train = (sample > 0) & ((folds != fold) if fold != "DESCRIPTIVE_ALL" else True)
                cap = min(5., float(early[train].min())-.01)
                margin = early[train]-record["P0_bar"]
                np.testing.assert_allclose(audits[fold]["P0_upper_bar"], cap, rtol=0, atol=0)
                np.testing.assert_allclose(audits[fold]["training_min_Pe_bar"], early[train].min(), rtol=0, atol=0)
                assert record["P0_bar"] <= cap
                np.testing.assert_allclose(np.maximum(margin, .01), margin, rtol=0, atol=0)
                np.testing.assert_allclose(audits[fold]["training_min_margin_bar"], margin.min(), rtol=0, atol=0)
                coef = C.C0.physical_onset(record) if row["fit_type"].startswith("c0_") else C.C1.onset_parameters(record)
                ps, p0, b, t0 = coef
                np.testing.assert_allclose(C.C0.onset_curve(coef, early[train])[0],
                                           t0+b*np.exp(early[train]/ps)/(early[train]-p0), rtol=1e-12, atol=0)
                held_floor = (folds == fold) & (early-p0 < .01)
                assert {v["brew"] for v in audits[fold]["held_out_floor_brews"]} == set(brews[held_floor])
                for held in audits[fold]["held_out_floor_brews"]:
                    assert held["margin_bar"] < .01
                    np.testing.assert_allclose(held["margin_bar"], held["Pe_bar"]-p0, rtol=0, atol=0)
                    np.testing.assert_allclose(held["predicted_onset_s"], C.C0.onset_curve(coef, [held["Pe_bar"]])[0][0],
                                               rtol=1e-12, atol=0)
                checked += 1
    assert checked == 9648
    return checked


def test_saved_training_caps_and_floor_audits_for_every_fold_and_draw():
    """Mandatory CI check: only the committed RESULT_TABLE.csv is required."""
    rows = C.read_results()
    early = np.array(json.loads(rows[0]["diagnostics"])["pairing"]["early_pressure_bar"])
    assert check_saved_training_margins(rows, early) == 9648


@pytest.mark.external_data
def test_raw_training_margins_for_all_9648_saved_onset_fits(monkeypatch, tmp_path):
    """Local full check independently rederives Pe from native brew traces."""
    raw_name = os.environ.get("PRESSURE_PEAK_C2_RAW")
    if not raw_name:
        pytest.skip("Full 9,648-fit audit requires native traces: set PRESSURE_PEAK_C2_RAW; CSV-only audit runs in CI")
    raw = Path(raw_name)
    if not (raw/"measurements_time_dependent").is_dir():
        pytest.skip("PRESSURE_PEAK_C2_RAW has no measurements_time_dependent native traces; CSV-only audit runs in CI")
    rows = C.read_results()
    pairing = json.loads(rows[0]["diagnostics"])["pairing"]
    monkeypatch.setattr(C.A, "ROOT", tmp_path)  # Detector's derived cache stays outside the checkout.
    _, pressure, _ = C.B.measure_onsets(SimpleNamespace(ids=pairing["brew_order"]), raw)
    np.testing.assert_allclose(pressure[:, 0], pairing["early_pressure_bar"], rtol=0, atol=0)
    assert check_saved_training_margins(rows, pressure[:, 0]) == 9648


def test_deadline_is_not_extended():
    with pytest.raises(TimeoutError, match="two-hour"):
        C.C0.Deadline(time.monotonic()-1).check()
