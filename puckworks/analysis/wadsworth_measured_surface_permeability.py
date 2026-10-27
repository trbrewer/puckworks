"""Frozen measured-surface replacement comparison, conditional and retrospective.

Wadsworth et al., RSOS 13,252031, doi:10.1098/rsos.252031, CC BY 4.0.
No parent scientific code or production defaults are modified.
"""
from __future__ import annotations

import csv
import io
import json
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

from puckworks.analysis import wadsworth_held_coffee_permeability as p

TASK = "SCI-MD-WADSWORTH-MEASURED-SURFACE-PERMEABILITY-001"
ARMS = ("S3", "E3", "W3", "N")
COMPARATORS = ("E3", "W3", "N")
COFFEES = p.COFFEES
S0 = 1e4
METHODS = "docs/analysis/sci_md_wadsworth_measured_surface_permeability_001/METHODS.md"
PARENT_MEMBERSHIP = "f72c57505fab4b7bf42876970c89207b36f3f1975e0b79081b09ca10563a8821"
PARENT_FOLDS = "4db17f4379b600c6ccca735ec4f96fc48f2f490240ad0b07c155eb1dd8e2a8fe"
PARENT_FREEZE = "1f2ccc1c4ce94f0d1654d113b322a936a924664f12c108978d056d4da417d624"
PARENT_RESULT = "7a724f317f638e303e69bbd403ebf742efc98ee18baa8292e17c47dc5b7c4467"
PARENT_MANIFEST = "4d81a65e5020868cef1b65102ef4c7c6f810f29e5ef097a356b047a229981599"
PINS = dict(pw_main="21669a427145194e1f4003e3cf1b97dedefe2679",
            base_scientific_parent="7c04a644c7b74be53ffb1cf611ebfb7ab06c5fd2",
            base_git_parent="097e5c7f0bdc1bef38d56938374f936003d55a39",
            pr380_git_parent="d41af1d08cda65864fdbdf5c6e1814cc027c5ef1",
            ewp_read_only="f44c33dbb9b4fb80143e360e6f4a90f8ac0aa516")
EXPOSURE = ["SOURCE_INTERNAL", "TARGET_EXPOSED", "RETROSPECTIVE"]
CONDITIONING = {"S3": ["s_p_connected_per_m", "phi_p_connected"],
                "E3": ["R_mean_m", "phi_p_connected"],
                "W3": ["R_mean_m", "phi_p_connected"], "N": []}


@dataclass(frozen=True)
class Record(p.Record):
    s: float


def join_surface(records, rows):
    """Independent keyed join, never positional or based on a substitute column."""
    mapping = {}
    for row in rows:
        key = (row["coffee"], int(row["G"]))
        p.require(key not in mapping, "duplicate surface identity")
        mapping[key] = row["s_p_connected_per_m"]
    expected = {(c, g) for c in COFFEES for g in range(1, 12)}
    p.require(set(mapping) == expected, "surface membership drift")
    p.require(mapping[("Guayacan", 2)] == "", "excluded surface missingness drift")
    p.require([r.identity for r in records] == [[c, g] for c in COFFEES for g in range(1, 12)
                                               if (c, g) != ("Guayacan", 2)], "parent row order drift")
    augmented = []
    for record in records:
        surface = float(mapping[tuple(record.identity)])
        p.require(np.isfinite(surface) and surface > 0, "invalid connected surface area")
        augmented.append(Record(**asdict(record), s=surface))
    return augmented


def load_table(path):
    raw = Path(path).read_bytes()
    p.require(p.sha(raw) == p.SOURCE_SHA and len(raw) == 2315 and raw.count(b"\r\n") == 23,
              "source bytes drift")
    records = p.load_table(path)  # Authenticated immutable parent reader, including blob check.
    rows = list(csv.DictReader(io.StringIO(raw.decode(), newline="")))
    return join_surface(records, rows)


def fold_manifest(records):
    return [{"source": c, "target": COFFEES[1-COFFEES.index(c)],
             "training": [r.identity for r in records if r.coffee == c],
             "evaluation": [r.identity for r in records if r.coffee != c],
             "exposure": EXPOSURE, "conditioning": CONDITIONING} for c in COFFEES]


def authenticate_parent(bundle, root, records):
    bundle, root = Path(bundle), Path(root)
    manifest_bytes = (bundle/"ARTIFACTS.json").read_bytes()
    p.require(p.sha(manifest_bytes) == PARENT_MANIFEST, "parent manifest identity mismatch")
    manifest = json.loads(manifest_bytes)
    for required in ("FREEZE.json", "RESULT.json", "DRAWS.jsonl", "PREDICTIONS.csv", "FOLDS.json"):
        p.require(required in manifest, "missing required parent manifest entry")
    for name, expected in manifest.items():
        p.require(Path(name).name == name, "invalid parent artifact name")
        p.require(p.sha((bundle/name).read_bytes()) == expected, "parent artifact hash mismatch: " + name)
    p.require(manifest["FREEZE.json"] == PARENT_FREEZE and manifest["RESULT.json"] == PARENT_RESULT,
              "pinned parent authority mismatch")
    frozen = json.loads((bundle/"FREEZE.json").read_text())
    old = json.loads((bundle/"RESULT.json").read_text())
    for name, expected in frozen["files"].items():
        p.require(p.sha((root/name).read_bytes()) == expected, "parent scientific file drift: " + name)
    ids = [r.identity for r in records]
    p.require(p.sha(p.canonical(ids)) == PARENT_MEMBERSHIP == frozen["membership_sha256"],
              "parent membership mismatch")
    p.require(frozen["membership"] == ids and p.sha(p.canonical(frozen["folds"])) == PARENT_FOLDS,
              "parent annotated fold mismatch")
    for new, previous in zip(fold_manifest(records), frozen["folds"]):
        for key in ("source", "training", "evaluation"):
            p.require(new[key] == previous[key], "parent fold list mismatch")
    prediction_rows = list(csv.DictReader((bundle/"PREDICTIONS.csv").open()))
    lookup = {(r.coffee, r.G): r for r in records}
    seen = set()
    for row in prediction_rows:
        key = (row["coffee"], int(row["G"]))
        arm_key = (*key, row["arm"])
        p.require(key in lookup and row["arm"] in p.ARMS and arm_key not in seen,
                  "parent observation identity drift")
        seen.add(arm_key)
        p.require(all(float(row[name]) == getattr(lookup[key], name)
                      for name in ("R", "phi", "k", "k_err")), "parent observation value drift")
    p.require(len(seen) == 63 and old["status"] == "COMPLETED_PRIVATE", "parent coverage/status mismatch")
    p.require(old["counts"] == dict(requested=2000, completed=2000, failed=0, unattempted=0),
              "parent campaign incomplete")
    return old, dict(manifest_sha256=p.sha(manifest_bytes), artifacts=manifest,
                     freeze_sha256=PARENT_FREEZE, result_sha256=PARENT_RESULT,
                     membership_sha256=PARENT_MEMBERSHIP, annotated_folds_sha256=PARENT_FOLDS,
                     observations="All63 retained-arm observation rows match exactly")


def surface_features(records, s0=S0):
    p.require(np.isfinite(s0) and s0 > 0, "invalid surface reference unit")
    s = np.array([r.s for r in records], dtype=np.float64)
    phi = np.array([r.phi for r in records], dtype=np.float64)
    p.require(np.all(np.isfinite(s)) and np.all(s > 0), "invalid surface predictor")
    p.require(np.all(np.isfinite(phi)) and np.all((phi > 0) & (phi < 1)), "invalid porosity predictor")
    return np.column_stack((np.log(s/s0), np.log(phi)))


def fit_s3(train, target, weights, s0=S0):
    x, tx = surface_features(train, s0), surface_features(target, s0)
    w = np.asarray(weights, dtype=np.float64)
    p.require(w.shape == (len(train),) and np.all(np.isfinite(w)) and np.all(w >= 0)
              and w.sum() > 0, "invalid training weights")
    z = np.log(np.array([r.k for r in train], dtype=np.float64)/p.K0)
    p.require(np.all(np.isfinite(z)), "invalid training response")
    center = np.average(x, axis=0, weights=w)
    scale = np.sqrt(np.average((x-center)**2, axis=0, weights=w))
    p.require(np.all(np.isfinite(scale)) and np.all(scale > 0), "zero/nonfinite feature scale")
    design = np.column_stack((np.ones(len(train)), (x-center)/scale))
    target_design = np.column_stack((np.ones(len(target)), (tx-center)/scale))
    active = w > 0
    matrix = design[active]*np.sqrt(w[active, None])
    response = z[active]*np.sqrt(w[active])
    u, singular, vt = np.linalg.svd(matrix, full_matrices=False)
    threshold = np.finfo(float).eps*max(matrix.shape)*singular[0]
    rank = int(np.count_nonzero(singular > threshold))
    if rank != 3:
        raise p.QualificationError("S3 rank failure", dict(arm="S3", rank=rank,
            singular_values=singular.tolist(), rank_threshold=float(threshold),
            weighted_shape=list(matrix.shape), center=center.tolist(), scale=scale.tolist()))
    beta = vt.T @ ((u.T @ response)/singular)
    q, qr = np.linalg.qr(matrix, mode="reduced")
    qr_beta = np.linalg.solve(qr, q.T @ response)
    both = np.vstack((design, target_design))
    predicted, qr_predicted = both @ beta, both @ qr_beta
    p.require(np.all(np.isfinite(predicted)) and np.all(np.isfinite(qr_predicted)), "nonfinite S3 fit")
    discrepancy = np.abs(predicted-qr_predicted)
    p.require(np.all(discrepancy <= 1e-9*np.maximum(1, np.abs(predicted))), "S3 SVD/QR disagreement")
    slopes = beta[1:]/scale
    coefficients = np.r_[beta[0]-center @ slopes, slopes]
    direct = np.column_stack((np.ones(len(both)), np.vstack((x, tx)))) @ coefficients
    p.require(np.all(np.abs(direct-predicted) <= 1e-9*np.maximum(1, np.abs(predicted))),
              "S3 inverse-map disagreement")
    p.checked_k(predicted)
    sse = float(np.sum(w*(predicted[:len(train)]-z)**2))
    p.require(np.isfinite(sse), "nonfinite S3 objective")
    return predicted[len(train):], dict(arm="S3",
        coefficients=dict(zip(("sIntercept", "sSlope", "sPhi"), map(float, coefficients))),
        center=center.tolist(), scale=scale.tolist(), scaled_coefficients=beta.tolist(),
        singular_values=singular.tolist(), condition_number=float(singular[0]/singular[-1]),
        rank=rank, rank_threshold=float(threshold), weighted_shape=list(matrix.shape),
        training_weight=float(w.sum()), training_sse=sse,
        qr_max_log_difference=float(discrepancy.max()))


def comparisons(scores):
    return {f"S3/{b}": {scope: {metric: p.contrast(scores["S3"][scope][metric], scores[b][scope][metric])
                                 for metric in ("log_rmse", "abs_rmse")}
                         for scope in (*COFFEES, "aggregate")} for b in COMPARATORS}


def evaluate(records, weights=None):
    if weights is None:
        weights = {c: np.ones(sum(r.coffee == c for r in records), dtype=int) for c in COFFEES}
    predictions = {arm: np.full(len(records), np.nan) for arm in ARMS}
    diagnostics, folds = {}, []
    for source in COFFEES:
        target = COFFEES[1-COFFEES.index(source)]
        train = [r for r in records if r.coffee == source]
        indices = [i for i, r in enumerate(records) if r.coffee == target]
        held = [records[i] for i in indices]
        diagnostics[source] = {}
        for arm in ARMS:
            pred, diag = (fit_s3(train, held, weights[source]) if arm == "S3"
                          else p.fit(train, held, arm, weights[source]))
            predictions[arm][indices] = pred
            diag.update(source=source, target=target)
            diagnostics[source][arm] = diag
        n_sse = diagnostics[source]["N"]["training_sse"]
        for arm in ("S3", "E3"):
            p.require(diagnostics[source][arm]["training_sse"] <= n_sse+1e-12*max(1, n_sse),
                      arm+" nesting arithmetic failure")
        folds.append(dict(source=source, target=target, training=[r.identity for r in train],
            evaluation=[r.identity for r in held], training_weights=list(map(int, weights[source])),
            evaluation_weights=list(map(int, weights[target]))))
    scores = {arm: p.score(records, predictions[arm], weights) for arm in ARMS}
    return dict(scores=scores, contrasts=comparisons(scores), diagnostics=diagnostics, folds=folds,
                predictions={arm: value.tolist() for arm, value in predictions.items()})


def reproduce(current, previous, weights=None, saved_weights=None):
    """Compare only retained families; no refits or historical campaign execution."""
    if weights is not None:
        p.require({c: list(map(int, weights[c])) for c in COFFEES} == saved_weights,
                  "parent bootstrap multiplicity reproduction failure")
    p.require(current["folds"] == previous["folds"], "parent reciprocal roles reproduction failure")
    maximum = 0.0
    for arm in COMPARATORS:
        difference = np.abs(np.array(current["predictions"][arm])-previous["predictions"][arm])
        p.require(np.all(difference <= 1e-10), "parent log-prediction reproduction failure")
        maximum = max(maximum, float(difference.max()))
        for scope, metrics in previous["scores"][arm].items():
            for metric, value in metrics.items():
                unit = p.K0 if metric.startswith("abs") else 1.0
                p.require(abs(current["scores"][arm][scope][metric]-value) <= 1e-10*max(unit, abs(value)),
                          "parent native-unit score reproduction failure")
    return dict(status="PASS", max_log_prediction_difference=maximum,
                retained_arms=list(COMPARATORS), multiplicities="EXACT" if weights is not None else "UNIT")


def summarize(point, draws):
    scores, contrasts = [], []
    for arm in ARMS:
        for scope, metrics in point["scores"][arm].items():
            for metric, value in metrics.items():
                ci = p.interval([d["result"]["scores"][arm][scope][metric] for d in draws])
                scores.append(dict(arm=arm, scope=scope, metric=metric, point=value, ci_low=ci[0], ci_high=ci[1]))
    for pair, scopes in point["contrasts"].items():
        for scope, metrics in scopes.items():
            for metric, estimates in metrics.items():
                for kind, value in estimates.items():
                    samples = [d["result"]["contrasts"][pair][scope][metric][kind] for d in draws]
                    ci = p.interval(samples)
                    contrasts.append(dict(pair=pair, scope=scope, metric=metric, kind=kind, point=value,
                        ci_low=ci[0] if ci else None, ci_high=ci[1] if ci else None,
                        undefined=sum(v is None for v in samples),
                        grade=p.grade(value) if kind == "gain" else None,
                        ci_grades=p.grade_interval(ci) if kind == "gain" else None,
                        boundary_sensitivity=[dict(lower=l, upper=u, point_grade=p.grade(value, l, u),
                            ci_grades=p.grade_interval(ci, l, u))
                            for l in (.075, .10, .125) for u in (.1875, .25, .3125)] if kind == "gain" else None))
    return scores, contrasts


def decision(ci):
    if ci is None:
        return "INCOMPLETE"
    return ("S3_LOWER_CONDITIONAL_LOG_LOSS_THAN_E3" if ci[1] < 0 else
            "E3_LOWER_CONDITIONAL_LOG_LOSS_THAN_S3" if ci[0] > 0 else
            "SURFACE_RADIUS_COMPARISON_UNRESOLVED")


def preference(point, intervals, metric="log_rmse", complete=True):
    if not complete:
        return dict(qualification="INCOMPLETE")
    direction = {b: {c: point["scores"]["S3"][c][metric] <= point["scores"][b][c][metric]
                     for c in COFFEES} for b in COMPARATORS}
    resolved_better = [b for b in COMPARATORS if intervals[b][0] > 0]
    wins = all(intervals[b][1] < 0 and all(direction[b].values()) for b in COMPARATORS)
    label = ("S3_CONDITIONAL_PREFERENCE" if wins else "SURFACE_REPRESENTATION_NOT_SELECTED"
             if resolved_better else "SURFACE_REPRESENTATION_PREFERENCE_UNRESOLVED")
    return dict(qualification=label, resolved_better_comparators=resolved_better,
                direction_no_higher=direction, direction_dependence=any(len(set(v.values())) > 1 for v in direction.values()),
                aggregate_delta_intervals=intervals)


def deletion_analysis(records, point, deadline=None):
    cases = [("record", r.identity) for r in records]+[("setting", g) for g in range(1, 12)]
    outputs = []
    for kind, key in cases:
        p.require(deadline is None or time.monotonic() < deadline, "scientific budget exhausted")
        kept = [r for r in records if (r.identity != key if kind == "record" else r.G != key)]
        outputs.append(dict(kind=kind, deleted=key, retained=[r.identity for r in kept], result=evaluate(kept)))
    summaries = []
    for kind in ("record", "setting"):
        for pair, scopes in point["contrasts"].items():
            for scope in scopes:
                for metric in ("log_rmse", "abs_rmse"):
                    values = [d["result"]["contrasts"][pair][scope][metric] for d in outputs if d["kind"] == kind]
                    delta, gain = [v["delta"] for v in values], [v["gain"] for v in values if v["gain"] is not None]
                    base = scopes[scope][metric]["delta"]
                    summaries.append(dict(kind=kind, pair=pair, scope=scope, metric=metric,
                        delta_range=[min(delta), max(delta)], gain_range=[min(gain), max(gain)] if gain else None,
                        undefined_gains=len(values)-len(gain), ties=sum(v == 0 for v in delta),
                        point_ranking_reversals=sum(v*base < 0 for v in delta)))
    return dict(results=outputs, summaries=summaries, interpretation="influence ranges, not CIs")


def prediction_rows(records, point):
    rows = []
    for i, record in enumerate(records):
        train = [r for r in records if r.coffee != record.coffee]
        for arm in ARMS:
            pred = point["predictions"][arm][i]
            keys = ("s", "phi") if arm == "S3" else ("R", "phi") if arm in ("E3", "W3") else ()
            ranges = {key: [min(getattr(r, key) for r in train), max(getattr(r, key) for r in train)] for key in keys}
            flags = {key: not lo <= getattr(record, key) <= hi for key, (lo, hi) in ranges.items()}
            rows.append(dict(**asdict(record), arm=arm, z_hat=pred, k_hat_m2=float(p.checked_k([pred])[0]),
                log_error=pred-float(np.log(record.k/p.K0)), error_m2=float(p.checked_k([pred])[0])-record.k,
                source_feature_ranges=ranges, marginal_extrapolation_flags=flags,
                joint_support="NOT_ESTABLISHED_BY_MARGINAL_CONTAINMENT"))
    return rows


def freeze(root, records, receipt):
    paths = [METHODS, "puckworks/analysis/wadsworth_measured_surface_permeability.py",
             "tools/wadsworth_measured_surface_permeability.py", "tests/test_wadsworth_measured_surface_permeability.py",
             "tests/test_pocketscience2024_assay.py", p.SOURCE,
             "puckworks/analysis/wadsworth_held_coffee_permeability.py", p.METHODS,
             "docs/analysis/sci_md_wadsworth_held_coffee_permeability_001/STATUS.json",
             "puckworks/data/wadsworth2026/PROVENANCE.md", "docs/permissions/wadsworth2026.md"]
    observations, folds = [asdict(r) for r in records], fold_manifest(records)
    return dict(task=TASK, frozen_utc=datetime.now(timezone.utc).isoformat(), pins=PINS,
        files={name: p.sha((root/name).read_bytes()) for name in paths}, parent_authority=receipt,
        ordered_membership=[r.identity for r in records], membership_sha256=PARENT_MEMBERSHIP,
        augmented_observations=observations, augmented_observations_sha256=p.sha(p.canonical(observations)),
        annotated_folds=folds, annotated_folds_sha256=p.sha(p.canonical(folds)),
        old_annotated_folds_sha256=PARENT_FOLDS, exposure=EXPOSURE, conditioning=CONDITIONING,
        equations=dict(S3="sIntercept+sSlope*ln(s_p/s0)+sPhi*ln(phi)",
                       E3="e0+eR*ln(R/R0)+ePhi*ln(phi)", W3="o+c-2*a*(R/R0)+b*ln(phi)", N="mean_train(z)"),
        constants=dict(R0=p.R0, s0=S0, k0=p.K0), seed=20261027, draws=2000,
        stream_order=list(COFFEES), sampling="rng.integers then bincount; one coffee vector in both roles",
        percentiles="2.5,97.5; linear", metric="sqrt(0.5*MSE_Guayacan+0.5*MSE_Tumba)",
        policy="Exact METHODS bytes bind numerical rules, decisions, diagnostics and reproduction tolerances",
        numpy_version=np.__version__, status="FROZEN_BEFORE_NEW_FITTING_OR_SCORING")


def run(root, parent_bundle, output):
    root, parent_bundle, output = Path(root).resolve(), Path(parent_bundle).resolve(), Path(output).resolve()
    p.require(output != root and root not in output.parents and output != parent_bundle
              and parent_bundle not in output.parents, "output must be new, private and outside parent bundle")
    output.mkdir(parents=True, exist_ok=False)
    started, deadline = time.monotonic(), time.monotonic()+1800
    result = dict(task=TASK, status="NOT_RUN", pins=PINS, exposure=EXPOSURE, conditioning=CONDITIONING,
                  samples=22, endpoints=21, coffees=2, espresso_shots=0, excluded=[["Guayacan", 2]],
                  basis="TDS/EY NOT_APPLICABLE; no density conversion",
                  counts=dict(requested=2000, completed=0, failed=0, unattempted=2000))
    try:
        records = load_table(root/p.SOURCE)
        parent, authority = authenticate_parent(parent_bundle, root, records)
        frozen = freeze(root, records, authority)
        p.write_json(output/"FREEZE.json", frozen)
        p.write_json(output/"FOLDS.json", frozen["annotated_folds"])
        p.write_json(output/"FEATURE_RECEIPT.json", dict(column="s_p_connected_per_m", units="m^-1",
                     observations=frozen["augmented_observations"], sha256=frozen["augmented_observations_sha256"],
                     excluded=dict(coffee="Guayacan", G=2, surface_field=""), parent_observations="UNCHANGED"))
        result["freeze_sha256"] = p.sha((output/"FREEZE.json").read_bytes())
        point = evaluate(records)
        result["point_reproduction"] = reproduce(point, parent["point"])
        result["point"] = point
        checked = 0
        with (parent_bundle/"DRAWS.jsonl").open() as saved, (output/"DRAWS.jsonl").open("w") as stream:
            def evaluator(rows, weights):
                nonlocal checked
                line = saved.readline()
                p.require(bool(line), "missing parent draw")
                old = json.loads(line)
                p.require(old["draw"] == checked and old["status"] == "COMPLETED", "parent draw order/status drift")
                current = evaluate(rows, weights)
                current["parent_reproduction"] = reproduce(current, old["result"], weights, old["weights"])
                checked += 1
                return current

            def sink(item):
                stream.write(p.canonical(item).decode()+"\n")
                stream.flush()

            boot = p.bootstrap(records, evaluator=evaluator, sink=sink, deadline=deadline)
            result["counts"], result["failed_draw"] = boot["counts"], boot["failure"]
            p.require(boot["failure"] is None, "required draw incomplete")
            p.require(not saved.readline(), "unexpected extra parent draws")
        result["parent_draws_reproduced"] = checked
        p.write_csv(output/"MULTIPLICITIES.csv", [dict(draw=d["draw"], coffee=c, G=r.G, multiplicity=w)
            for d in boot["draws"] for c in COFFEES
            for r, w in zip([r for r in records if r.coffee == c], d["weights"][c])])
        scores, contrasts = summarize(point, boot["draws"])
        result.update(scores=scores, contrasts=contrasts)
        p.write_csv(output/"SCORES.csv", scores)
        p.write_csv(output/"CONTRASTS.csv", contrasts)
        for metric, key in (("log_rmse", "preference"), ("abs_rmse", "absolute_preference")):
            intervals = {b: next([x["ci_low"], x["ci_high"]] for x in contrasts if
                (x["pair"], x["scope"], x["metric"], x["kind"]) == ("S3/"+b, "aggregate", metric, "delta"))
                for b in COMPARATORS}
            result[key] = preference(point, intervals, metric)
        result["decision"] = decision(result["preference"]["aggregate_delta_intervals"]["E3"])
        result["deletions"] = deletion_analysis(records, point, deadline)
        predicted_rows = prediction_rows(records, point)
        p.write_csv(output/"PREDICTIONS.csv", predicted_rows)
        result["worst_cases"] = {arm: {metric: max([r for r in predicted_rows if r["arm"] == arm],
            key=lambda r: abs(r[metric])) for metric in ("log_error", "error_m2")} for arm in ARMS}
        result["ranges"] = {c: {key: [min(getattr(r, key) for r in records if r.coffee == c),
            max(getattr(r, key) for r in records if r.coffee == c)] for key in ("R", "s", "phi", "k")} for c in COFFEES}
        fits = [d for evaluation in [point]+[x["result"] for x in boot["draws"]]+
                [x["result"] for x in result["deletions"]["results"]]
                for source in evaluation["diagnostics"].values() for d in source.values()]
        p.require(len(fits) == 16264, "fit instance count mismatch")
        result["numerical_diagnostics"] = dict(fits=len(fits), max_condition=max(d["condition_number"] for d in fits),
            max_qr_log_difference=max(d["qr_max_log_difference"] for d in fits), rank_failures=0,
            nonfinite_predictions=0, coverage={a: len(records) for a in ARMS})
        result["W3_sign_frequencies"] = {c: {flag: sum(d["result"]["diagnostics"][c]["W3"][flag]
            for d in boot["draws"])/2000 for flag in ("a_negative", "b_nonpositive")} for c in COFFEES}
        result["undefined_counts"] = dict(point=sum(x["point"] is None for x in contrasts),
                                           draws=sum(x["undefined"] for x in contrasts))
        result["uncertainty"] = dict(conditional="within-coffee selected-record resampling; coverage uncalibrated",
            measurement_CI="NOT_ESTIMABLE", coffee_population_CI="NOT_ESTIMABLE",
            excluded=["correlated predictor/response geometry errors", "segmentation effects", "physical replication",
                      "directional uncertainty", "shared systematic error", "prior model/representation selection"])
        result["parent_context"] = dict(decision=parent["decision"], preference=parent["preference"]["qualification"],
                                        reopened=False, separate_parent_campaigns=0)
        result["status"] = "COMPLETED_PRIVATE"
    except (p.QualificationError, OSError, ValueError, np.linalg.LinAlgError, FloatingPointError) as exc:
        result.update(status="INCOMPLETE", decision="INCOMPLETE", preference=dict(qualification="INCOMPLETE"),
                      stop_reason=str(exc), failure_diagnostics=getattr(exc, "diagnostics", None))
    result["scientific_computation_seconds"] = time.monotonic()-started
    p.write_json(output/"RESULT.json", result)
    p.write_json(output/"DIAGNOSTICS.json", {key: result.get(key) for key in
                 ("point_reproduction", "parent_draws_reproduced", "numerical_diagnostics", "W3_sign_frequencies", "ranges")})
    p.write_json(output/"ARTIFACTS.json", {f.name: p.sha(f.read_bytes()) for f in sorted(output.iterdir())
                                          if f.is_file() and f.name != "ARTIFACTS.json"})
    return result
