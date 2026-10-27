"""Frozen retrospective Table 1 comparison; no production model changes.

Wadsworth et al., RSOS 13, 252031, doi:10.1098/rsos.252031, CC BY 4.0.
The source is authenticated before parsing; reported errors are never weights.
"""
from __future__ import annotations

import csv
import hashlib
import io
import json
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

TASK = "SCI-MD-WADSWORTH-HELD-COFFEE-PERMEABILITY-001"
COFFEES = ("Guayacan", "Tumba")
ARMS = ("W3", "E3", "N")
PAIRS = (("W3", "E3"), ("W3", "N"), ("E3", "N"))
SOURCE = "puckworks/data/wadsworth2026/wadsworth2026_table1_full.csv"
SOURCE_SHA = "3b0139fe02108d3dfcd1441d9e4062e86d9b7e1a8505141a7beefd9366ebf20f"
SOURCE_BLOB = "37b4136bfa1a84df159f41c01245000288db4ebf"
METHODS = "docs/analysis/sci_md_wadsworth_held_coffee_permeability_001/METHODS.md"
PINS = {
    "pw_main": "21669a427145194e1f4003e3cf1b97dedefe2679",
    "base_scientific_parent": "097e5c7f0bdc1bef38d56938374f936003d55a39",
    "base_git_parent": "d41af1d08cda65864fdbdf5c6e1814cc027c5ef1",
    "scientific_predecessor": "cc6e3d66eb5192e08e0949373548bb3a04ee69fd",
    "ewp_read_only": "f44c33dbb9b4fb80143e360e6f4a90f8ac0aa516",
}
R0, K0 = 1e-3, 1e-10
EXPOSURE = ["SOURCE_INTERNAL", "TARGET_EXPOSED", "RETROSPECTIVE",
            "CONDITIONAL_ON_MEASURED_RADIUS_AND_CONNECTED_POROSITY"]


class QualificationError(ValueError):
    """Required numerical or source qualification failed; no rescue permitted."""

    def __init__(self, reason, diagnostics=None):
        super().__init__(reason)
        self.diagnostics = diagnostics


def require(condition, reason):
    if not condition:
        raise QualificationError(reason)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()


def write_json(path, value):
    Path(path).write_text(json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n")


@dataclass(frozen=True)
class Record:
    coffee: str
    G: int
    R: float
    phi: float
    k: float
    k_err: float

    @property
    def identity(self):
        return [self.coffee, self.G]


def load_table(path):
    raw = Path(path).read_bytes()
    require(len(raw) == 2315 and sha(raw) == SOURCE_SHA, "source byte/hash drift")
    blob = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
    require(blob == SOURCE_BLOB and raw.count(b"\r\n") == 23, "source blob/CRLF drift")
    rows = list(csv.DictReader(io.StringIO(raw.decode(), newline="")))
    ids = [(r["coffee"], int(r["G"])) for r in rows]
    require(ids == [(c, g) for c in COFFEES for g in range(1, 12)], "identity/order drift")
    records = []
    for row in rows:
        radius = float(row["R_mean_m"])
        require(np.isfinite(radius) and radius > 0, "invalid radius")
        if (row["coffee"], int(row["G"])) == ("Guayacan", 2):
            require(all(row[k] == "" for k in ("phi_p_connected", "k_m2", "k_err_m2")),
                    "missingness drift")
            continue
        phi, k, err = (float(row[s]) for s in ("phi_p_connected", "k_m2", "k_err_m2"))
        require(np.all(np.isfinite([phi, k, err])) and 0 < phi < 1 and k > 0 and err >= 0,
                "invalid porosity/permeability/error")
        records.append(Record(row["coffee"], int(row["G"]), radius, phi, k, err))
    require(len(records) == 21, "eligibility drift")
    return records


def predictors(records, arm):
    radius = np.array([r.R for r in records], dtype=float) / R0
    phi = np.array([r.phi for r in records], dtype=float)
    require(np.all(np.isfinite(radius)) and np.all(radius > 0), "invalid radius predictor")
    require(np.all(np.isfinite(phi)) and np.all((phi > 0) & (phi < 1)), "invalid phi predictor")
    if arm == "W3":
        features = np.column_stack((-2 * radius, np.log(phi)))
        offset = np.log(2 * R0**2 / (9 * K0)) + 2 * np.log(radius) - np.log1p(-phi)
    elif arm == "E3":
        features = np.column_stack((np.log(radius), np.log(phi)))
        offset = np.zeros(len(records))
    elif arm == "N":
        features, offset = np.empty((len(records), 0)), np.zeros(len(records))
    else:
        raise QualificationError("unknown arm")
    return features, offset


def checked_k(z):
    z = np.asarray(z, dtype=float)
    require(np.all(np.isfinite(z)), "nonfinite log prediction")
    with np.errstate(over="ignore", under="ignore", invalid="ignore"):
        k = np.exp(np.log(K0) + z)
    require(np.all(np.isfinite(k)) and np.all(k > 0), "unrepresentable permeability prediction")
    return k


def fit(train, target, arm, weights):
    """SVD and independent QR solutions, with exact coefficient inverse map."""
    x, offset = predictors(train, arm)
    tx, toffset = predictors(target, arm)
    w = np.asarray(weights, dtype=float)
    require(w.shape == (len(train),) and np.all(np.isfinite(w)) and np.all(w >= 0)
            and w.sum() > 0, "invalid training weight")
    z = np.log(np.array([r.k for r in train]) / K0)
    require(np.all(np.isfinite(z)), "invalid training response")
    center = np.average(x, axis=0, weights=w)
    scale = np.sqrt(np.average((x - center)**2, axis=0, weights=w))
    require(np.all(np.isfinite(scale)) and np.all(scale > 0), "zero/nonfinite feature scale")
    design = np.column_stack((np.ones(len(train)), (x - center) / scale))
    tdesign = np.column_stack((np.ones(len(target)), (tx - center) / scale))
    active = w > 0
    weighted = design[active] * np.sqrt(w[active, None])
    response = (z - offset)[active] * np.sqrt(w[active])
    u, singular, vt = np.linalg.svd(weighted, full_matrices=False)
    threshold = np.finfo(float).eps * max(weighted.shape) * singular[0]
    rank = int(np.count_nonzero(singular > threshold))
    if rank != design.shape[1]:
        raise QualificationError("rank failure", {
            "arm": arm, "rank": rank, "singular_values": singular.tolist(),
            "rank_threshold": float(threshold), "weighted_shape": list(weighted.shape),
            "center": center.tolist(), "scale": scale.tolist(),
        })
    beta = vt.T @ ((u.T @ response) / singular)
    q, qr = np.linalg.qr(weighted, mode="reduced")
    beta_qr = np.linalg.solve(qr, q.T @ response)
    both = np.vstack((design, tdesign))
    offsets = np.concatenate((offset, toffset))
    svd_pred, qr_pred = offsets + both @ beta, offsets + both @ beta_qr
    require(np.all(np.isfinite(svd_pred)) and np.all(np.isfinite(qr_pred)), "nonfinite fit")
    discrepancy = np.abs(svd_pred - qr_pred)
    require(np.all(discrepancy <= 1e-9 * np.maximum(1, np.abs(svd_pred))), "SVD/QR disagreement")
    slopes = beta[1:] / scale
    coef = np.r_[beta[0] - center @ slopes, slopes]
    direct = offsets + np.column_stack((np.ones(len(both)), np.vstack((x, tx)))) @ coef
    require(np.all(np.abs(direct - svd_pred) <= 1e-9 * np.maximum(1, np.abs(svd_pred))),
            "coefficient inverse-map failure")
    checked_k(svd_pred)  # All source and held predictors, including zero-weight records.
    sse = float(np.sum(w * (svd_pred[:len(train)] - z)**2))
    require(np.isfinite(sse), "nonfinite training objective")
    names = {"W3": ["c", "a", "b"], "E3": ["e0", "eR", "ePhi"], "N": ["n0"]}[arm]
    coefficients = dict(zip(names, map(float, coef)))
    diagnostic = {
        "arm": arm, "coefficients": coefficients, "center": center.tolist(),
        "scale": scale.tolist(), "scaled_coefficients": beta.tolist(),
        "singular_values": singular.tolist(), "condition_number": float(singular[0]/singular[-1]),
        "rank": rank, "rank_threshold": float(threshold), "weighted_shape": list(weighted.shape),
        "training_weight": float(w.sum()), "training_sse": sse,
        "qr_max_log_difference": float(discrepancy.max()),
        "a_negative": bool(arm == "W3" and coef[1] < 0),
        "b_nonpositive": bool(arm == "W3" and coef[2] <= 0),
    }
    return svd_pred[len(train):], diagnostic


def score(records, predictions, weights):
    """Equal coffee MSE aggregation, followed by the square root."""
    metrics = {}
    for coffee in COFFEES:
        idx = np.array([i for i, r in enumerate(records) if r.coffee == coffee])
        w = np.asarray(weights[coffee], float)
        require(len(idx) == len(w) and np.all(w >= 0) and np.all(np.isfinite(w)) and w.sum() > 0,
                "invalid evaluation weights")
        truth = np.array([records[i].k for i in idx])
        error = np.asarray(predictions)[idx] - np.log(truth / K0)
        absolute = checked_k(np.asarray(predictions)[idx]) - truth
        with np.errstate(over="ignore", invalid="ignore"):
            metrics[coffee] = {
                "log_rmse": float(np.sqrt(np.average(error**2, weights=w))),
                "log_mae": float(np.average(np.abs(error), weights=w)),
                "log_bias": float(np.average(error, weights=w)),
                "abs_rmse": float(np.sqrt(np.average(absolute**2, weights=w))),
                "abs_mae": float(np.average(np.abs(absolute), weights=w)),
                "abs_bias": float(np.average(absolute, weights=w)),
            }
    metrics["aggregate"] = {}
    for name in metrics[COFFEES[0]]:
        values = np.array([metrics[c][name] for c in COFFEES])
        metrics["aggregate"][name] = float(np.sqrt(np.mean(values**2)) if name.endswith("rmse")
                                           else np.mean(values))
    require(all(np.isfinite(v) for scope in metrics.values() for v in scope.values()),
            "nonfinite required score")
    return metrics


def contrast(a, b):
    return {"delta": float(a - b), "gain": None if b == 0 else float(1 - a / b)}


def comparisons(scores):
    return {f"{a}/{b}": {scope: {metric: contrast(scores[a][scope][metric], scores[b][scope][metric])
                               for metric in ("log_rmse", "abs_rmse")}
                         for scope in (*COFFEES, "aggregate")} for a, b in PAIRS}


def evaluate(records, weights=None):
    counts = {c: sum(r.coffee == c for r in records) for c in COFFEES}
    if weights is None:
        weights = {c: np.ones(counts[c], dtype=int) for c in COFFEES}
    predictions = {a: np.full(len(records), np.nan) for a in ARMS}
    diagnostics, folds = [], []
    for source in COFFEES:
        target = COFFEES[1 - COFFEES.index(source)]
        train = [r for r in records if r.coffee == source]
        idx = [i for i, r in enumerate(records) if r.coffee == target]
        held = [records[i] for i in idx]
        fold_diags = {}
        for arm in ARMS:
            pred, diag = fit(train, held, arm, weights[source])
            predictions[arm][idx] = pred
            diag.update(source=source, target=target)
            diagnostics.append(diag)
            fold_diags[arm] = diag
        n_sse = fold_diags["N"]["training_sse"]
        require(fold_diags["E3"]["training_sse"] <= n_sse + 1e-12 * max(1, n_sse),
                "E3 nesting arithmetic failure")
        folds.append({"source": source, "target": target, "training": [r.identity for r in train],
                      "evaluation": [r.identity for r in held],
                      "training_weights": list(map(int, weights[source])),
                      "evaluation_weights": list(map(int, weights[target]))})
    scores = {arm: score(records, predictions[arm], weights) for arm in ARMS}
    return {"scores": scores, "contrasts": comparisons(scores), "diagnostics": diagnostics,
            "folds": folds, "predictions": {a: p.tolist() for a, p in predictions.items()}}


def bootstrap(records, n=2000, evaluator=evaluate, sink=None, deadline=None):
    """Two stable streams; each coffee's ONE vector serves both reciprocal roles."""
    streams = [np.random.default_rng(s) for s in np.random.SeedSequence(20261027).spawn(2)]
    sizes = [sum(r.coffee == c for r in records) for c in COFFEES]
    draws = []
    failure = None
    for draw in range(n):
        weights = {c: np.bincount(rng.integers(0, size, size=size), minlength=size)
                   for c, rng, size in zip(COFFEES, streams, sizes)}
        item = {"draw": draw, "weights": {c: w.tolist() for c, w in weights.items()}}
        try:
            require(deadline is None or time.monotonic() < deadline, "scientific budget exhausted")
            item["result"] = evaluator(records, weights)
            item["status"] = "COMPLETED"
        except (QualificationError, np.linalg.LinAlgError, FloatingPointError) as exc:
            item.update(status="FAILED", reason=str(exc), diagnostics=getattr(exc, "diagnostics", None))
            failure = item
        if sink is not None:
            sink(item)
        if failure is not None:
            break
        draws.append(item)
    return {"draws": draws, "failure": failure,
            "counts": {"requested": n, "completed": len(draws), "failed": int(failure is not None),
                       "unattempted": n - len(draws) - int(failure is not None)}}


def interval(values):
    if any(v is None for v in values):
        return None
    return np.percentile(values, [2.5, 97.5], method="linear").tolist()


def grade(gain, lower=0.10, upper=0.25):
    if gain is None:
        return "undefined"
    return "worse" if gain < 0 else "small" if gain < lower else "moderate" if gain < upper else "large"


def grade_interval(ci, lower=0.10, upper=0.25):
    if ci is None:
        return ["undefined"]
    lo, hi = ci
    return [name for name, left, right in (("worse", -np.inf, 0), ("small", 0, lower),
                                          ("moderate", lower, upper), ("large", upper, np.inf))
            if hi >= left and lo < right]


def decision(ci):
    if ci is None:
        return "INCOMPLETE"
    return ("W3_LOWER_CONDITIONAL_LOG_LOSS" if ci[1] < 0 else
            "E3_LOWER_CONDITIONAL_LOG_LOSS" if ci[0] > 0 else
            "HELD_COFFEE_COMPARISON_UNRESOLVED")


def summarize(point, draws):
    score_rows, contrast_rows = [], []
    for arm in ARMS:
        for scope, metrics in point["scores"][arm].items():
            for metric, value in metrics.items():
                ci = interval([d["result"]["scores"][arm][scope][metric] for d in draws])
                score_rows.append(dict(arm=arm, scope=scope, metric=metric, point=value,
                                       ci_low=ci[0], ci_high=ci[1]))
    for pair, scopes in point["contrasts"].items():
        for scope, metrics in scopes.items():
            for metric, values in metrics.items():
                for kind, value in values.items():
                    samples = [d["result"]["contrasts"][pair][scope][metric][kind] for d in draws]
                    ci = interval(samples)
                    contrast_rows.append(dict(pair=pair, scope=scope, metric=metric, kind=kind,
                        point=value, ci_low=None if ci is None else ci[0],
                        ci_high=None if ci is None else ci[1], undefined=sum(v is None for v in samples),
                        grade=grade(value) if kind == "gain" else None,
                        ci_grades=grade_interval(ci) if kind == "gain" else None,
                        boundary_sensitivity=[dict(lower=l, upper=u, point_grade=grade(value, l, u),
                                                  ci_grades=grade_interval(ci, l, u))
                                              for l in (.075, .10, .125) for u in (.1875, .25, .3125)]
                                              if kind == "gain" else None))
    return score_rows, contrast_rows


def preference(point, draws, metric="log_rmse"):
    evidence = {}
    for a in ARMS:
        others = [b for b in ARMS if a != b]
        upper = {b: interval([d["result"]["scores"][a]["aggregate"][metric] -
                              d["result"]["scores"][b]["aggregate"][metric] for d in draws])[1]
                 for b in others}
        direction_ok = all(point["scores"][a][c][metric] <= point["scores"][b][c][metric]
                           for b in others for c in COFFEES)
        evidence[a] = {"delta_ci_upper_against_each": upper, "both_directions_no_higher": direction_ok,
                       "conditional_preference": all(v < 0 for v in upper.values()) and direction_ok}
    winners = [a for a in ARMS if evidence[a]["conditional_preference"]]
    direction_winners = {c: min(ARMS, key=lambda a: point["scores"][a][c][metric]) for c in COFFEES}
    label = (f"{winners[0]}_CONDITIONAL_PREFERENCE" if winners else
             "DIRECTION_DEPENDENT_NO_CONDITIONAL_PREFERENCE" if len(set(direction_winners.values())) > 1
             else "BASELINE_BEST_POINT_UNRESOLVED" if set(direction_winners.values()) == {"N"}
             else "UNRESOLVED_NO_CONDITIONAL_PREFERENCE")
    return dict(qualification=label, evidence=evidence, direction_point_winners=direction_winners)


def deletion_analysis(records, point, deadline=None):
    results = []
    cases = [("record", r.identity) for r in records] + [("setting", g) for g in range(1, 12)]
    for kind, key in cases:
        require(deadline is None or time.monotonic() < deadline, "scientific budget exhausted")
        kept = [r for r in records if (r.identity != key if kind == "record" else r.G != key)]
        result = evaluate(kept)
        results.append(dict(kind=kind, deleted=key, retained=[r.identity for r in kept], result=result))
    summaries = []
    for kind in ("record", "setting"):
        for pair in point["contrasts"]:
            for scope in (*COFFEES, "aggregate"):
                for metric in ("log_rmse", "abs_rmse"):
                    base = point["contrasts"][pair][scope][metric]["delta"]
                    vals = [x["result"]["contrasts"][pair][scope][metric] for x in results if x["kind"] == kind]
                    deltas = [x["delta"] for x in vals]
                    gains = [x["gain"] for x in vals if x["gain"] is not None]
                    summaries.append(dict(kind=kind, pair=pair, scope=scope, metric=metric,
                        delta_range=[min(deltas), max(deltas)], gain_range=[min(gains), max(gains)] if gains else None,
                        undefined_gains=len(vals)-len(gains), ties=sum(d == 0 for d in deltas),
                        point_ranking_reversals=sum(d * base < 0 for d in deltas)))
    return dict(results=results, summaries=summaries, interpretation="influence ranges, not CIs")


def prediction_rows(records, point):
    rows = []
    for i, record in enumerate(records):
        source = [r for r in records if r.coffee != record.coffee]
        rmin, rmax = min(r.R for r in source), max(r.R for r in source)
        pmin, pmax = min(r.phi for r in source), max(r.phi for r in source)
        for arm in ARMS:
            pred = point["predictions"][arm][i]
            kp = float(checked_k([pred])[0])
            rows.append(dict(**asdict(record), arm=arm, z_hat=pred, k_hat_m2=kp,
                log_error=pred - float(np.log(record.k / K0)), error_m2=kp-record.k,
                source_R_min=rmin, source_R_max=rmax, source_phi_min=pmin, source_phi_max=pmax,
                radius_extrapolation=not rmin <= record.R <= rmax,
                porosity_extrapolation=not pmin <= record.phi <= pmax))
    return rows


def write_csv(path, rows):
    if not rows:
        Path(path).write_text("")
        return
    with Path(path).open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows({k: json.dumps(v) if isinstance(v, (dict, list)) else v for k, v in row.items()}
                        for row in rows)


def freeze(root, records):
    paths = [SOURCE, METHODS, "puckworks/analysis/wadsworth_held_coffee_permeability.py",
             "tools/wadsworth_held_coffee_permeability.py", "tests/test_wadsworth_held_coffee_permeability.py",
             "puckworks/data/wadsworth2026/PROVENANCE.md", "puckworks/models/wadsworth2026/permeability.py",
             "puckworks/validation/gates.py", "docs/cards/wadsworth2026.md",
             "docs/cards/wadsworth2026_grindmap.md", "docs/permissions/wadsworth2026.md",
             "docs/analysis/sci_md_pocketscience_grudeva_window_tds_001/STATUS.json"]
    folds = [{"source": c, "training": [r.identity for r in records if r.coffee == c],
              "evaluation": [r.identity for r in records if r.coffee != c], "exposure": EXPOSURE}
             for c in COFFEES]
    return dict(task=TASK, frozen_utc=datetime.now(timezone.utc).isoformat(), pins=PINS,
        files={p: sha((root/p).read_bytes()) for p in paths}, source_blob=SOURCE_BLOB,
        source_bytes=2315, membership=[r.identity for r in records], folds=folds,
        membership_sha256=sha(canonical([r.identity for r in records])), folds_sha256=sha(canonical(folds)),
        models={"W3": "z=o+c-2*a*r+b*ln(phi)", "E3": "z=e0+eR*ln(r)+ePhi*ln(phi)", "N": "z=mean_train(z)"},
        seed=20261027, draws=2000, stream_order=list(COFFEES), percentile="linear 2.5,97.5",
        metric="sqrt(0.5*MSE_Guayacan+0.5*MSE_Tumba)", R0=R0, k0=K0,
        policy="Exact METHODS.md bytes control numerical rules, comparisons, decisions and diagnostics",
        versions={"numpy": np.__version__}, status="FROZEN_BEFORE_FITTING_OR_SCORING")


def run(root, output):
    root, output = Path(root).resolve(), Path(output).resolve()
    require(root != output and root not in output.parents, "results must remain outside Git checkout")
    output.mkdir(parents=True, exist_ok=False)  # A scored policy cannot silently be replayed here.
    started, deadline = time.monotonic(), time.monotonic() + 1800
    result = {"task": TASK, "status": "NOT_RUN", "exposure": EXPOSURE, "pins": PINS,
              "samples": 22, "endpoints": 21, "coffees": 2, "espresso_shots": 0,
              "excluded": [["Guayacan", 2]], "basis": "TDS/EY NOT_APPLICABLE; no density conversion",
              "counts": dict(requested=2000, completed=0, failed=0, unattempted=2000)}
    try:
        records = load_table(root/SOURCE)
        frozen = freeze(root, records)
        write_json(output/"FREEZE.json", frozen)
        write_json(output/"FOLDS.json", frozen["folds"])
        result["freeze_sha256"] = sha((output/"FREEZE.json").read_bytes())
        point = evaluate(records)
        result["point"] = point
        with (output/"DRAWS.jsonl").open("w") as stream:
            def sink(item):
                stream.write(canonical(item).decode()+"\n")
                stream.flush()
            boot = bootstrap(records, sink=sink, deadline=deadline)
        result["counts"] = boot["counts"]
        result["failure"] = boot["failure"]
        weights_rows = [dict(draw=d["draw"], coffee=c, G=r.G, multiplicity=w)
                       for d in boot["draws"] + ([boot["failure"]] if boot["failure"] else [])
                       for c in COFFEES for r, w in zip([r for r in records if r.coffee == c], d["weights"][c])]
        write_csv(output/"MULTIPLICITIES.csv", weights_rows)
        predictions = prediction_rows(records, point)
        write_csv(output/"PREDICTIONS.csv", predictions)
        require(boot["failure"] is None, "required bootstrap inference incomplete")
        score_rows, contrast_rows = summarize(point, boot["draws"])
        result.update(scores=score_rows, contrasts=contrast_rows)
        write_csv(output/"SCORES.csv", score_rows)
        write_csv(output/"CONTRASTS.csv", contrast_rows)
        primary = next(r for r in contrast_rows if (r["pair"], r["scope"], r["metric"], r["kind"]) ==
                       ("W3/E3", "aggregate", "log_rmse", "delta"))
        result["decision"] = decision([primary["ci_low"], primary["ci_high"]])
        result["preference"] = preference(point, boot["draws"])
        result["absolute_preference"] = preference(point, boot["draws"], "abs_rmse")
        result["deletions"] = deletion_analysis(records, point, deadline)
        result["undefined_counts"] = {"point_contrasts": sum(r["point"] is None for r in contrast_rows),
                                      "bootstrap_contrasts": sum(r["undefined"] for r in contrast_rows)}
        result["coefficient_signs"] = {c: {flag: sum(d["result"]["diagnostics"][COFFEES.index(c)*3][flag]
                                                   for d in boot["draws"])/len(boot["draws"])
                                         for flag in ("a_negative", "b_nonpositive")} for c in COFFEES}
        for c in COFFEES:
            result["coefficient_signs"][c]["either_incompatible_sign"] = sum(
                d["result"]["diagnostics"][COFFEES.index(c)*3]["a_negative"] or
                d["result"]["diagnostics"][COFFEES.index(c)*3]["b_nonpositive"]
                for d in boot["draws"])/len(boot["draws"])
        result["worst_cases"] = {a: {m: max([r for r in predictions if r["arm"] == a],
                                           key=lambda r: abs(r[m])) for m in ("log_error", "error_m2")}
                                 for a in ARMS}
        all_diags = point["diagnostics"] + [x for d in boot["draws"] for x in d["result"]["diagnostics"]]
        all_diags += [x for d in result["deletions"]["results"] for x in d["result"]["diagnostics"]]
        result["numerical_diagnostics"] = dict(fits=len(all_diags),
            max_condition=max(d["condition_number"] for d in all_diags),
            max_qr_log_difference=max(d["qr_max_log_difference"] for d in all_diags),
            rank_failures=0, nonfinite_predictions=0, coverage={a:len(records) for a in ARMS})
        result["ranges"] = {c: {key: [min(getattr(r, key) for r in records if r.coffee == c),
                                      max(getattr(r, key) for r in records if r.coffee == c)]
                                for key in ("R", "phi", "k")} for c in COFFEES}
        result["uncertainty"] = {
            "conditional": "Within-coffee selected-record resampling model; coverage uncalibrated",
            "measurement_CI": "NOT_ESTIMABLE", "coffee_population_CI": "NOT_ESTIMABLE",
            "excluded": ["physical replicate variance", "directional measurement uncertainty",
                         "correlated segmentation/geometry error", "shared systematic effects", "prior selection"],
            "k_err": "standard deviation on the average; not Gaussian SD, SEM or replicate variance; unused"}
        result["status"] = "COMPLETED_PRIVATE"
    except (QualificationError, np.linalg.LinAlgError, FloatingPointError, OSError) as exc:
        result.update(status="INCOMPLETE", decision="INCOMPLETE", stop_reason=str(exc),
                      failure_diagnostics=getattr(exc, "diagnostics", None))
    result["scientific_computation_seconds"] = time.monotonic() - started
    write_json(output/"RESULT.json", result)
    write_json(output/"DIAGNOSTICS.json", {k: result.get(k) for k in
               ("numerical_diagnostics", "coefficient_signs", "ranges", "worst_cases", "uncertainty")})
    write_json(output/"ARTIFACTS.json", {p.name: sha(p.read_bytes()) for p in sorted(output.iterdir())
                                        if p.is_file() and p.name != "ARTIFACTS.json"})
    return result
