"""Calibrated connected-porosity shapes, conditional reciprocal coffee transfer.

Wadsworth et al., RSOS 13,252031, doi:10.1098/rsos.252031, CC BY 4.0.
Task-local arms and authority; no production or predecessor mutations.
"""
from __future__ import annotations

import json
import time
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

from puckworks.analysis import wadsworth_held_coffee_permeability as p
from puckworks.analysis import wadsworth_measured_surface_permeability as s
from puckworks.models.wadsworth2026.permeability import B_PERC, k_star

TASK = "SCI-MD-WADSWORTH-PERCOLATION-KC-TRANSFER-001"
ARMS = ("PER1", "KC1", "N", "S3")
PAIRS = (("PER1", "KC1"), ("PER1", "N"), ("KC1", "N"), ("PER1", "S3"), ("KC1", "S3"))
COFFEES, K0, S0 = p.COFFEES, p.K0, s.S0
METHODS = "docs/analysis/sci_md_wadsworth_percolation_kc_transfer_001/METHODS.md"
PARENT_FREEZE = "f44693c947ddae7a62a503bbdcbeb8a97406fb5b07ae49d196b9feef0161e2d9"
PARENT_RESULT = "35d44b6a42429374cc7c2643062cc3c00b1623919721af02ab2150bae9ea3e3e"
OBSERVATIONS = "901e04ce19ab3b29a1a77f7617e5f975c70f661fa7579df1d9a335f6527c68e2"
PARENT_FOLDS = "5b5966ceeaf0cd815cd6bfb69237461bffb30bc3193b8d74406ee592950b63f4"
PINS = dict(main="21669a427145194e1f4003e3cf1b97dedefe2679",
            base="6a97530d746269cf9e9d46dbcbdfd83e54a2caf5",
            base_parent_PR382="9f311e70bd08ae16387c9ac40aa9c71595f95a65",
            EWP="f44c33dbb9b4fb80143e360e6f4a90f8ac0aa516")
EXPOSURE = ["SOURCE_INTERNAL", "TARGET_EXPOSED", "RETROSPECTIVE",
            "CONDITIONAL_ON_TABULATED_CONNECTED_SURFACE_AREA_AND_POROSITY"]


def fold_manifest(records):
    return [dict(source=c, target=COFFEES[1-COFFEES.index(c)],
                 training=[r.identity for r in records if r.coffee == c],
                 evaluation=[r.identity for r in records if r.coffee != c],
                 exposure=EXPOSURE, conditioning={a: ([] if a == "N" else
                     ["s_p_connected_per_m", "phi_p_connected"]) for a in ARMS}) for c in COFFEES]


def authenticate_pr382(bundle, root, records):
    """Authenticate pinned bytes first; an unanchored manifest never authenticates itself."""
    bundle, root = Path(bundle), Path(root)
    frozen_bytes, result_bytes = (bundle/"FREEZE.json").read_bytes(), (bundle/"RESULT.json").read_bytes()
    p.require(p.sha(frozen_bytes) == PARENT_FREEZE, "PR382 FREEZE identity mismatch")
    p.require(p.sha(result_bytes) == PARENT_RESULT, "PR382 RESULT identity mismatch")
    frozen, parent = json.loads(frozen_bytes), json.loads(result_bytes)
    p.require(parent["freeze_sha256"] == PARENT_FREEZE, "PR382 RESULT/FREEZE relationship mismatch")
    p.require(parent["status"] == "COMPLETED_PRIVATE" and parent["counts"] ==
              dict(requested=2000, completed=2000, failed=0, unattempted=0), "PR382 incomplete authority")
    for name, expected in frozen["files"].items():
        p.require(p.sha((root/name).read_bytes()) == expected, "PR382 bound scientific file drift: "+name)
    ids, observations = [r.identity for r in records], [asdict(r) for r in records]
    p.require(p.sha(p.canonical(ids)) == s.PARENT_MEMBERSHIP == frozen["membership_sha256"]
              and frozen["ordered_membership"] == ids, "PR382 membership/order mismatch")
    p.require(p.sha(p.canonical(observations)) == OBSERVATIONS == frozen["augmented_observations_sha256"]
              and observations == frozen["augmented_observations"], "PR382 complete observation mismatch")
    p.require(p.sha(p.canonical(frozen["annotated_folds"])) == PARENT_FOLDS ==
              frozen["annotated_folds_sha256"] and s.fold_manifest(records) == frozen["annotated_folds"],
              "PR382 annotated fold mismatch")
    for expected, actual in zip(fold_manifest(records), parent["point"]["folds"]):
        for key in ("source", "target", "training", "evaluation"):
            p.require(expected[key] == actual[key], "PR382 reciprocal role mismatch")
    p.require(set(parent["point"]["predictions"]) == set(s.ARMS) and
              all(len(v) == 21 for v in parent["point"]["predictions"].values()), "PR382 point coverage mismatch")
    receipt = dict(freeze_sha256=PARENT_FREEZE, result_sha256=PARENT_RESULT,
        bound_files=frozen["files"], membership_sha256=s.PARENT_MEMBERSHIP,
        observations_sha256=OBSERVATIONS, annotated_folds_sha256=PARENT_FOLDS,
        anchored="Pinned FREEZE/RESULT, relationship, scientific files, all observations/order/folds and RESULT summaries",
        draw_authentication="UNANCHORED_NUMERICAL_CONSISTENCY_ONLY", manifest_is_independent_anchor=False)
    manifest_file = bundle/"ARTIFACTS.json"
    if manifest_file.exists():
        manifest = json.loads(manifest_file.read_text())
        for name, expected in manifest.items():
            p.require(Path(name).name == name, "unsafe parent manifest filename")
            p.require(p.sha((bundle/name).read_bytes()) == expected, "parent checksum consistency failure: "+name)
        receipt.update(unanchored_manifest_sha256=p.sha(manifest_file.read_bytes()),
                       checksum_consistency_entries=len(manifest), unanchored_checksums=manifest)
    status = json.loads((root/"docs/analysis/sci_md_wadsworth_measured_surface_permeability_001/STATUS.json").read_text())
    verification = bundle/"SAVED_ARITHMETIC_VERIFICATION.json"
    p.require(p.sha(verification.read_bytes()) == status["saved_arithmetic_verification_sha256"],
              "PR382 saved verification identity mismatch")
    receipt["anchored_saved_verification_sha256"] = p.sha(verification.read_bytes())
    receipt["saved_verification_limitation"] = "Anchored verification reports consistency but does not bind draw-file bytes"
    return parent, receipt


def offsets(records, arm, normalization_shift=0.0):
    # Surface features use only the explicitly connected fields.
    if arm == "N":
        return np.full(len(records), normalization_shift, dtype=np.float64)
    features = s.surface_features(records)
    phi = np.array([r.phi for r in records], dtype=np.float64)
    t, u = features.T
    p.require(B_PERC == 4.4, "native exponent drift")
    if arm == "PER1":
        value = np.log(2/(K0*S0**2))+np.log1p(-phi)+B_PERC*u-2*t
        native = np.log(k_star(phi, np.array([r.s for r in records]))/K0)+B_PERC*u
        p.require(np.all(np.abs(value-native) <= 1e-9*np.maximum(1, np.abs(value))), "native percolation identity")
    elif arm == "KC1":
        value = np.log(1/(5*K0*S0**2))+3*u-2*t
    else:
        raise p.QualificationError("unknown intercept arm")
    value = value+normalization_shift
    p.require(np.all(np.isfinite(value)), "nonfinite shape offset")
    return value


def phi_difference(records):
    phi = np.array([r.phi for r in records], dtype=np.float64)
    return np.log(10)+np.log1p(-phi)+1.4*np.log(phi)


def fit(train, target, arm, weights, normalization_shift=0.0):
    """One fit with independent algebra/QR and checked inverse-map verification."""
    p.require(arm in ARMS, "unknown task arm")
    w = np.asarray(weights, dtype=np.float64)
    p.require(w.shape == (len(train),) and np.all(np.isfinite(w)) and np.all(w >= 0)
              and np.isfinite(w.sum()) and w.sum() > 0, "invalid source weights")
    if arm == "S3":
        pred, diag = s.fit_s3(train, target, w)
        both_x = s.surface_features(train+target)
        standardized = np.column_stack((np.ones(len(both_x)), (both_x-diag["center"])/diag["scale"]))
        both = standardized @ np.array(diag["scaled_coefficients"])
        coef = diag["coefficients"]
        mapped = coef["sIntercept"]+both_x @ [coef["sSlope"], coef["sPhi"]]
        diag["inverse_coefficient_max_log_difference"] = float(np.max(np.abs(mapped-both)))
    else:
        source_offset, target_offset = offsets(train, arm, normalization_shift), offsets(target, arm, normalization_shift)
        z = np.log(np.array([r.k for r in train], dtype=np.float64)/K0)
        p.require(np.all(np.isfinite(z)), "invalid source response")
        coefficient = float(np.average(z-source_offset, weights=w))
        active = w > 0
        matrix = np.sqrt(w[active, None])
        q, qr = np.linalg.qr(matrix, mode="reduced")
        qr_coefficient = float(np.linalg.solve(qr, q.T @ ((z-source_offset)[active]*np.sqrt(w[active])))[0])
        both = np.r_[source_offset, target_offset]+coefficient
        alternate = np.r_[source_offset, target_offset]+qr_coefficient
        discrepancy = np.abs(both-alternate)
        p.require(np.all(discrepancy <= 1e-9*np.maximum(1, np.abs(both))), "analytic intercept/QR disagreement")
        singular = float(np.sqrt(w.sum()))
        threshold = float(np.finfo(float).eps*max(matrix.shape)*singular)
        p.require(singular > threshold, "intercept rank failure")
        sse = float(np.sum(w*(both[:len(train)]-z)**2))
        p.require(np.isfinite(sse), "nonfinite training SSE")
        pred = both[len(train):]
        diag = dict(arm=arm, coefficients={"c": coefficient}, center=[], scale=[],
                    training_sse=sse, training_weight=float(w.sum()), rank=1,
                    singular_values=[singular], rank_threshold=threshold, condition_number=1.0,
                    weighted_shape=list(matrix.shape), qr_max_log_difference=float(discrepancy.max()),
                    inverse_coefficient_max_log_difference=0.0)
    native = p.checked_k(both)
    inverse = np.abs(np.log(native/K0)-both)
    p.require(np.all(inverse <= 1e-9*np.maximum(1, np.abs(both))), "permeability inverse-map disagreement")
    diag["inverse_permeability_max_log_difference"] = float(inverse.max())
    diag["coefficient_count"] = 3 if arm == "S3" else 1
    return pred, diag


def comparisons(scores, pairs=PAIRS):
    return {a+"/"+b: {scope: {metric: p.contrast(scores[a][scope][metric], scores[b][scope][metric])
                             for metric in ("log_rmse", "abs_rmse")}
                      for scope in (*COFFEES, "aggregate")} for a, b in pairs}


class Executor:
    def __init__(self, output):
        self.output, self.started, self.fits, self.finished = Path(output), None, 0, 0

    def event(self, item):
        with (self.output/"EXECUTION.jsonl").open("a") as stream:
            stream.write(p.canonical(item).decode()+"\n")

    def check(self):
        p.require(self.started is None or time.monotonic()-self.started <= 1800, "scientific budget exhausted")

    def fit(self, train, held, arm, weights, label, source):
        if self.started is None:
            self.started = time.monotonic()
        self.check()
        self.fits += 1
        key = dict(fit=self.fits, label=label, source=source, arm=arm)
        self.event(dict(event="FIT_START", **key))
        try:
            value = fit(train, held, arm, weights)
            self.finished += 1
            self.event(dict(event="FIT_FINISH", status="PASS", **key))
            return value
        except Exception as exc:
            self.event(dict(event="FIT_FAILURE", reason=str(exc), **key))
            raise


def evaluate(records, weights=None, executor=None, label="synthetic"):
    if weights is None:
        weights = {c: np.ones(sum(r.coffee == c for r in records), dtype=int) for c in COFFEES}
    predictions = {a: np.full(len(records), np.nan) for a in ARMS}
    diagnostics, folds, identities = {}, [], []
    for source in COFFEES:
        target = COFFEES[1-COFFEES.index(source)]
        train = [r for r in records if r.coffee == source]
        indices = [i for i, r in enumerate(records) if r.coffee == target]
        held = [records[i] for i in indices]
        diagnostics[source] = {}
        for arm in ARMS:
            pred, diag = (fit(train, held, arm, weights[source]) if executor is None else
                          executor.fit(train, held, arm, weights[source], label, source))
            predictions[arm][indices] = pred
            diag.update(source=source, target=target)
            diagnostics[source][arm] = diag
        for comparator in ("KC1", "N"):
            baseline = diagnostics[source][comparator]["training_sse"]
            p.require(diagnostics[source]["S3"]["training_sse"] <= baseline+1e-12*max(1, baseline),
                      "S3 nesting arithmetic failure: "+comparator)
        expected = phi_difference(held)-np.average(phi_difference(train), weights=weights[source])
        difference = predictions["PER1"][indices]-predictions["KC1"][indices]
        error = np.abs(difference-expected)
        p.require(np.all(error <= 1e-9*np.maximum(1, np.abs(expected))), "centered porosity-shape identity failure")
        identities.append(dict(source=source, maximum_log_difference=float(error.max())))
        active = [r for r, w in zip(train, weights[source]) if w > 0]
        ranges = {key: [min(getattr(r, key) for r in active), max(getattr(r, key) for r in active)] for key in ("s", "phi")}
        folds.append(dict(source=source, target=target, training=[r.identity for r in train],
            evaluation=[r.identity for r in held], training_weights=list(map(int, weights[source])),
            evaluation_weights=list(map(int, weights[target])), source_marginal_ranges=ranges,
            marginal_flags=[dict(identity=r.identity, flags={key: not lo <= getattr(r, key) <= hi
                for key, (lo, hi) in ranges.items()}) for r in held]))
    scores = {a: p.score(records, predictions[a], weights) for a in ARMS}
    return dict(scores=scores, contrasts=comparisons(scores),
                context_contrasts=comparisons(scores, (("S3", "N"),)), diagnostics=diagnostics,
                folds=folds, shape_identity_checks=identities,
                predictions={a: v.tolist() for a, v in predictions.items()})


def close_score(actual, previous, metric):
    unit = K0 if metric.startswith("abs") else 1.0
    p.require(abs(actual-previous) <= 1e-10*max(unit, abs(previous)), "PR382 score/interval reproduction failure")


def reproduce_point(current, previous, weights=None, saved_weights=None):
    if weights is not None:
        p.require({c: list(map(int, weights[c])) for c in COFFEES} == saved_weights, "PR382 multiplicity consistency failure")
    for new, old in zip(current["folds"], previous["folds"]):
        for key in ("source", "target", "training", "evaluation", "training_weights", "evaluation_weights"):
            p.require(new[key] == old[key], "PR382 role reproduction failure")
    maximum = 0.0
    for arm in ("S3", "N"):
        discrepancy = np.abs(np.array(current["predictions"][arm])-previous["predictions"][arm])
        p.require(np.all(discrepancy <= 1e-10), "PR382 log-prediction reproduction failure")
        maximum = max(maximum, float(discrepancy.max()))
        for scope, metrics in previous["scores"][arm].items():
            for metric, value in metrics.items():
                close_score(current["scores"][arm][scope][metric], value, metric)
    return dict(status="PASS", max_log_prediction_difference=maximum,
                interpretation="UNANCHORED_DRAW_NUMERICAL_CONSISTENCY" if weights is not None else "ANCHORED_RESULT_POINT_REPRODUCTION")


def summarize(point, draws, context=False):
    score_rows, contrast_rows = [], []
    for arm in ARMS:
        for scope, metrics in point["scores"][arm].items():
            for metric, value in metrics.items():
                ci = p.interval([d["result"]["scores"][arm][scope][metric] for d in draws])
                score_rows.append(dict(arm=arm, scope=scope, metric=metric, point=value, ci_low=ci[0], ci_high=ci[1]))
    key = "context_contrasts" if context else "contrasts"
    for pair, scopes in point[key].items():
        for scope, metrics in scopes.items():
            for metric, estimates in metrics.items():
                for kind, value in estimates.items():
                    samples = [d["result"][key][pair][scope][metric][kind] for d in draws]
                    ci = p.interval(samples)
                    contrast_rows.append(dict(pair=pair, scope=scope, metric=metric, kind=kind, point=value,
                        ci_low=ci[0] if ci else None, ci_high=ci[1] if ci else None,
                        undefined=sum(v is None for v in samples), grade=p.grade(value) if kind == "gain" else None,
                        ci_grades=p.grade_interval(ci) if kind == "gain" else None,
                        boundary_sensitivity=[dict(lower=l, upper=u, point_grade=p.grade(value, l, u),
                            ci_grades=p.grade_interval(ci, l, u)) for l in (.075, .10, .125)
                            for u in (.1875, .25, .3125)] if kind == "gain" else None))
    return score_rows, contrast_rows


def reproduce_summaries(scores, context, parent):
    count, largest_scaled = 0, 0.0
    for old in [x for x in parent["scores"] if x["arm"] in ("S3", "N")]+[
            x for x in parent["contrasts"] if x["pair"] == "S3/N"]:
        keys = ("arm", "scope", "metric") if "arm" in old else ("pair", "scope", "metric", "kind")
        new = next(x for x in (scores if "arm" in old else context) if all(x[k] == old[k] for k in keys))
        for key in ("point", "ci_low", "ci_high"):
            if old[key] is None:
                p.require(new[key] is None, "PR382 undefined reproduction failure")
            else:
                metric = "gain" if old.get("kind") == "gain" else old["metric"]
                close_score(new[key], old[key], metric)
                unit = K0 if metric.startswith("abs") else 1.0
                largest_scaled = max(largest_scaled, abs(new[key]-old[key])/max(unit, abs(old[key])))
                count += 1
        for key in ("undefined", "grade", "ci_grades", "boundary_sensitivity"):
            if key in old:
                p.require(new[key] == old[key], "PR382 contrast classification reproduction failure")
    return dict(status="PASS", anchored_to=PARENT_RESULT, scalar_comparisons=count,
                maximum_scaled_difference=largest_scaled, coverage="S3/N all scores, aggregate/directional intervals, contrast summaries")


def oriented_contrast(point, draws, a, b, metric):
    # Recalculate reverse gains from losses; never negate a percentage gain.
    at = lambda e: p.contrast(e["scores"][a]["aggregate"][metric], e["scores"][b]["aggregate"][metric])
    values = [at(d["result"]) for d in draws]
    return dict(point=at(point), delta_ci=p.interval([x["delta"] for x in values]),
                gain_ci=p.interval([x["gain"] for x in values]))


def decisions(point, draws, metric="log_rmse", complete=True):
    if not complete:
        return dict(primary="INCOMPLETE", preference="INCOMPLETE")
    main = oriented_contrast(point, draws, "PER1", "KC1", metric)["delta_ci"]
    unit = "LOG" if metric == "log_rmse" else "ABSOLUTE"
    primary = (f"PER1_LOWER_CONDITIONAL_{unit}_LOSS_THAN_KC1" if main[1] < 0 else
               f"KC1_LOWER_CONDITIONAL_{unit}_LOSS_THAN_PER1" if main[0] > 0 else
               "CALIBRATED_SHAPE_COMPARISON_UNRESOLVED")
    shapes = {}
    for arm in ("PER1", "KC1"):
        evidence, failed_aggregate, adverse, directions, reversals = {}, [], [], {}, []
        for other in ARMS:
            if other == arm:
                continue
            contrast = oriented_contrast(point, draws, arm, other, metric)
            evidence[other] = contrast
            ci = contrast["delta_ci"]
            if ci[1] >= 0:
                failed_aggregate.append(other)
            if ci[0] > 0:
                adverse.append(other)
            directions[other] = {c: point["scores"][arm][c][metric] <= point["scores"][other][c][metric] for c in COFFEES}
            deltas = [point["scores"][arm][c][metric]-point["scores"][other][c][metric] for c in COFFEES]
            if deltas[0]*deltas[1] < 0:
                reversals.append(other)
        wins = not failed_aggregate and all(all(v.values()) for v in directions.values())
        s3_ci = evidence["S3"]["delta_ci"]
        shapes[arm] = dict(qualification="CONDITIONAL_PREFERENCE_OVER_TESTED_ARMS" if wins else
            "NO_PUBLISHED_SHAPE_CONDITIONAL_PREFERENCE", comparisons=evidence,
            failed_aggregate_requirements=failed_aggregate, resolved_adverse_comparators=adverse,
            direction_no_higher=directions, directional_reversals=reversals,
            comparison_to_S3="SHAPE_LOWER" if s3_ci[1] < 0 else "S3_LOWER" if s3_ci[0] > 0 else "UNRESOLVED")
    winners = [a for a, v in shapes.items() if v["qualification"] == "CONDITIONAL_PREFERENCE_OVER_TESTED_ARMS"]
    return dict(primary=primary, preference="CONDITIONAL_PREFERENCE_OVER_TESTED_ARMS" if winners else
                "NO_PUBLISHED_SHAPE_CONDITIONAL_PREFERENCE", winners=winners, shapes=shapes,
                interpretation="PRIMARY" if metric == "log_rmse" else "ABSOLUTE_UNIT_SENSITIVITY_ONLY")


def deletion_analysis(records, point, executor=None):
    cases = [("record", r.identity) for r in records]+[("setting", g) for g in range(1, 12)]
    results, summaries = [], []
    for kind, key in cases:
        if executor:
            executor.check()
        kept = [r for r in records if (r.identity != key if kind == "record" else r.G != key)]
        results.append(dict(kind=kind, deleted=key, retained=[r.identity for r in kept],
                            result=evaluate(kept, executor=executor, label=f"delete:{kind}:{key}")))
        if executor:
            p.write_json(executor.output/"DELETIONS_PARTIAL.json", results)
    for kind in ("record", "setting"):
        selected = [x for x in results if x["kind"] == kind]
        for pair, scopes in point["contrasts"].items():
            for scope, metrics in scopes.items():
                for metric, original in metrics.items():
                    values = [x["result"]["contrasts"][pair][scope][metric] for x in selected]
                    delta = [x["delta"] for x in values]
                    gain = [x["gain"] for x in values]
                    summaries.append(dict(kind=kind, pair=pair, scope=scope, metric=metric,
                        delta_range=[min(delta), max(delta)], gain_range=None if any(v is None for v in gain)
                        else [min(gain), max(gain)], undefined_gains=sum(v is None for v in gain),
                        ties=[x["deleted"] for x, v in zip(selected, values) if v["delta"] == 0],
                        point_ranking_reversals=[x["deleted"] for x, v in zip(selected, values)
                                                if v["delta"]*original["delta"] < 0]))
    return dict(results=results, summaries=summaries, interpretation="INFLUENCE_NOT_CI")


def prediction_rows(records, point):
    rows = []
    for i, r in enumerate(records):
        source = next(f for f in point["folds"] if f["target"] == r.coffee)
        for arm in ARMS:
            pred = point["predictions"][arm][i]
            ranges = {} if arm == "N" else source["source_marginal_ranges"]
            rows.append(dict(**asdict(r), arm=arm, z_hat=pred, k_hat_m2=float(p.checked_k([pred])[0]),
                log_error=pred-float(np.log(r.k/K0)), error_m2=float(p.checked_k([pred])[0])-r.k,
                source_feature_ranges=ranges, marginal_flags={key: not lo <= getattr(r, key) <= hi
                    for key, (lo, hi) in ranges.items()}, joint_support="NOT_ESTABLISHED_BY_MARGINAL_CONTAINMENT"))
    return rows


def freeze(root, records, authority, inspection):
    names = [METHODS, "puckworks/analysis/wadsworth_percolation_kc_transfer.py",
             "tools/wadsworth_percolation_kc_transfer.py", "tests/test_wadsworth_percolation_kc_transfer.py",
             "puckworks/analysis/wadsworth_measured_surface_permeability.py",
             "puckworks/analysis/wadsworth_held_coffee_permeability.py", p.SOURCE,
             "puckworks/models/wadsworth2026/permeability.py", "puckworks/validation/gates.py",
             "puckworks/data/wadsworth2026/PROVENANCE.md", "docs/cards/wadsworth2026.md",
             "docs/permissions/wadsworth2026.md"]
    folds = fold_manifest(records)
    return dict(task=TASK, frozen_utc=datetime.now(timezone.utc).isoformat(), pins=PINS,
        files={n: p.sha((root/n).read_bytes()) for n in names}, parent_authority=authority,
        observations=[asdict(r) for r in records], observations_sha256=OBSERVATIONS,
        membership=[r.identity for r in records], membership_sha256=s.PARENT_MEMBERSHIP,
        folds=folds, folds_sha256=p.sha(p.canonical(folds)), inspection=inspection,
        exposure=EXPOSURE, constants=dict(k0=K0, s0=S0, exponent=B_PERC, threshold=0),
        coefficients=dict(PER1=1, KC1=1, N=1, S3=3), seed=20261027, stream_order=list(COFFEES),
        draws=2000, deletions=dict(records=21, settings=11), expected_fits=16264,
        scientific_seconds_limit=1800, qualification_seconds_limit=1200,
        numerical_policy="Exact METHODS and code bytes bound before first real fit",
        numpy_version=np.__version__, status="FROZEN_BEFORE_REAL_FITTING")


def run(root, parent_bundle, output, inspection):
    root, parent_bundle, output = Path(root).resolve(), Path(parent_bundle).resolve(), Path(output).resolve()
    p.require(root not in output.parents and output != root and output != parent_bundle and
              parent_bundle not in output.parents, "output must be new and outside Git/predecessor bundle")
    output.mkdir(parents=True, exist_ok=False)
    executor = Executor(output)
    result = dict(task=TASK, status="NOT_RUN", pins=PINS, exposure=EXPOSURE,
        preparations=22, endpoints=21, coffees=2, espresso_shots=0, excluded=[["Guayacan", 2]],
        basis="TDS/EY NOT_APPLICABLE; connected phi dimensionless, s m^-1, k m^2; no density conversion",
        counts=dict(requested=2000, completed=0, failed=0, unattempted=2000),
        qa="NOT_RUN_AT_SCIENTIFIC_EXECUTION", independent_human_review=False)
    try:
        records = s.load_table(root/p.SOURCE)
        parent, authority = authenticate_pr382(parent_bundle, root, records)
        p.require(inspection["qualification_seconds"] <= 1200 and inspection["status"] == "PASS", "input qualification budget/status")
        frozen = freeze(root, records, authority, inspection)
        p.write_json(output/"FREEZE.json", frozen)
        p.write_json(output/"AUTHENTICATION.json", authority)
        p.write_json(output/"INSPECTION.json", inspection)
        p.write_json(output/"OBSERVATIONS.json", frozen["observations"])
        p.write_json(output/"MEMBERSHIP.json", frozen["membership"])
        p.write_json(output/"FOLDS.json", frozen["folds"])
        result["freeze_sha256"] = p.sha((output/"FREEZE.json").read_bytes())
        result["folds_sha256"] = frozen["folds_sha256"]
        point = evaluate(records, executor=executor, label="point")
        result["point_reproduction"] = reproduce_point(point, parent["point"])
        result["point"] = point
        checked = 0
        saved_path = parent_bundle/"DRAWS.jsonl"
        saved = saved_path.open() if saved_path.exists() else None
        try:
            with (output/"DRAWS.jsonl").open("w") as stream:
                def evaluator(rows, weights):
                    nonlocal checked
                    current = evaluate(rows, weights, executor, f"draw:{checked}")
                    if saved:
                        line = saved.readline()
                        p.require(bool(line), "missing parent consistency draw")
                        old = json.loads(line)
                        p.require(old["draw"] == checked and old["status"] == "COMPLETED", "parent consistency draw order/status")
                        current["parent_draw_consistency"] = reproduce_point(current, old["result"], weights, old["weights"])
                    checked += 1
                    return current

                def sink(item):
                    stream.write(p.canonical(item).decode()+"\n")
                    stream.flush()

                boot = p.bootstrap(records, n=2000, evaluator=evaluator, sink=sink)
                result["counts"], result["failed_draw"] = boot["counts"], boot["failure"]
                p.require(boot["failure"] is None, "required paired inference incomplete")
                p.require(saved is None or not saved.readline(), "extra parent consistency draws")
        finally:
            if saved:
                saved.close()
        result["unanchored_draw_consistency_count"] = checked if saved else 0
        scores, contrasts = summarize(point, boot["draws"])
        _, context = summarize(point, boot["draws"], context=True)
        result["summary_reproduction"] = reproduce_summaries(scores, context, parent)
        result.update(scores=scores, contrasts=contrasts, S3_N_reproduction_context=context)
        result["decisions"] = decisions(point, boot["draws"])
        result["absolute_sensitivity"] = decisions(point, boot["draws"], "abs_rmse")
        result["deletions"] = deletion_analysis(records, point, executor)
        executor.check()
        p.require(executor.fits == executor.finished == 16264, "required fit count mismatch")
        evaluations = [point]+[x["result"] for x in boot["draws"]]+[x["result"] for x in result["deletions"]["results"]]
        diagnostics = [v for e in evaluations for coffee in e["diagnostics"].values() for v in coffee.values()]
        result["numerical_diagnostics"] = dict(fits=executor.fits, fits_per_arm={a: 4066 for a in ARMS},
            max_condition=max(d["condition_number"] for d in diagnostics),
            max_qr_log_difference=max(d["qr_max_log_difference"] for d in diagnostics),
            max_inverse_coefficient_log_difference=max(d["inverse_coefficient_max_log_difference"] for d in diagnostics),
            max_inverse_permeability_log_difference=max(d["inverse_permeability_max_log_difference"] for d in diagnostics),
            max_shape_identity_log_difference=max(d["maximum_log_difference"] for e in evaluations for d in e["shape_identity_checks"]),
            rank_failures=0, nonfinite_predictions=0, coverage={a: 21 for a in ARMS})
        result["undefined_counts"] = dict(point=sum(x["point"] is None for x in contrasts),
                                         draw_contrasts=sum(x["undefined"] for x in contrasts))
        rows = prediction_rows(records, point)
        p.write_csv(output/"PREDICTIONS.csv", rows)
        p.write_csv(output/"SCORES.csv", scores)
        p.write_csv(output/"CONTRASTS.csv", contrasts)
        p.write_csv(output/"MULTIPLICITIES.csv", [dict(draw=d["draw"], coffee=c, G=r.G, multiplicity=w)
            for d in boot["draws"] for c in COFFEES
            for r, w in zip([r for r in records if r.coffee == c], d["weights"][c])])
        result["worst_cases"] = {a: {metric: max([r for r in rows if r["arm"] == a], key=lambda r: abs(r[metric]))
                                  for metric in ("log_error", "error_m2")} for a in ARMS}
        result["uncertainty"] = dict(conditional="Selected records, coffee pair and representations; within-coffee resampling coverage uncalibrated",
            measurement_CI="NOT_ESTIMABLE", coffee_population_CI="NOT_ESTIMABLE",
            excluded=["correlated geometry/segmentation error", "directional uncertainty", "physical replication",
                      "shared systematic effects", "prior representation selection"], simultaneous=False)
        result["parent_context"] = dict(preference=parent["preference"]["qualification"], reopened=False,
                                        separate_parent_campaigns=0, historical_QA_records="PRESERVED")
        result["successor"] = dict(task="SCI-MD-WADSWORTH-SOLID-FRACTION-PREFACTOR-001", execution="NOT_RUN",
            justification="NOT_JUSTIFIED", reason="No separately authorized remaining model decision; an unresolved comparison alone is insufficient")
        result["P1_blind_TDS"] = "OPEN"
        executor.check()
        result["status"] = "COMPLETED_PRIVATE"
    except (p.QualificationError, OSError, ValueError, np.linalg.LinAlgError, FloatingPointError) as exc:
        result.update(status="INCOMPLETE", decisions=dict(primary="INCOMPLETE", preference="INCOMPLETE"),
                      stop_reason=str(exc), failure_diagnostics=getattr(exc, "diagnostics", None))
        p.write_json(output/"FAILURE.json", dict(reason=str(exc), diagnostics=getattr(exc, "diagnostics", None),
                     fits_started=executor.fits, fits_finished=executor.finished, counts=result["counts"]))
    result["scientific_computation_seconds"] = 0 if executor.started is None else time.monotonic()-executor.started
    result["fit_counts"] = dict(started=executor.fits, finished=executor.finished)
    p.write_json(output/"RESULT.json", result)
    return result


def artifact_manifest(output):
    output = Path(output)
    p.write_json(output/"ARTIFACTS.json", {str(f.relative_to(output)): p.sha(f.read_bytes())
        for f in sorted(output.rglob("*")) if f.is_file() and f.name != "ARTIFACTS.json"})
