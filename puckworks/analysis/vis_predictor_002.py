"""Post-hoc reset-flag exclusion rerun; all numerical science comes from pinned 001.

The parent bundle and private caches are read-only. Only whole stored shots with
reset_like=True are excluded; surviving observations and original folds are reused.
"""
from __future__ import annotations

import argparse
import csv
from dataclasses import asdict
import hashlib
import json
from pathlib import Path
import pickle
import subprocess
import time

import numpy as np
import scipy

from puckworks.analysis import vis_predictor_001 as shared
from puckworks.empirical.visualizer import (
    MODELS, Settings, coordinates, encode, fitted_model, load_model, predict,
)

BASE = "65f51c63856677eccc4ba5a45ce555ea0c4eab99"
TASK = "PW-VIS-PREDICTOR-002"
ROOT = shared.ROOT
PARENT = ROOT / "docs/research/VIS_PREDICTOR_001"
OUT = ROOT / "docs/research/VIS_PREDICTOR_002"
CONTRASTS = (("AR", "M0R"), ("AR", "T0"), ("AR", "R0"), ("M0R", "R0"),
             ("L0R", "T0"), ("L0R", "R0"), ("R0", "C0"), ("T0", "C0"))
C0_REFERENCE = dict(rmse_g_s=1.2084042519, nrmse=1.6547408860)
C0_ATOL = 1e-9  # supplied references are rounded to ten decimal places


def validate_locations(output, private, parent_private):
    """Reject overlapping/symlink-resolved output roots before creating any file."""
    output, private, parent_private = map(lambda p: Path(p).resolve(),
                                          (output, private, parent_private))
    protected = (PARENT.resolve(), parent_private)
    for destination in (output, private):
        if "VIS_PREDICTOR_001" in destination.parts:
            raise ValueError("002 output overlaps read-only 001 artifacts")
        for source in protected:
            if destination == source or source in destination.parents or destination in source.parents:
                raise ValueError("002 output overlaps read-only 001 artifacts")
    if output == private or output in private.parents or private in output.parents:
        raise ValueError("Public and private output roots overlap")
    if private == ROOT or ROOT in private.parents:
        raise ValueError("Private output must remain outside Git")
    return output, private, parent_private


def verify_parent(parent_private):
    """Authenticate pinned parent artifacts and unchanged scientific evaluator."""
    for name in ("FROZEN_MANIFEST.json", "STARTS.json", "SCORING_RECEIPT.json"):
        path = PARENT / name
        committed = subprocess.check_output(["git", "show", f"{BASE}:{path.relative_to(ROOT)}"], cwd=ROOT)
        if path.read_bytes() != committed:
            raise RuntimeError("Parent bundle differs from pinned head")
    for name in ("puckworks/empirical/visualizer.py", "puckworks/analysis/pressure_peak_x1.py",
                 "puckworks/analysis/cor15_shape_001.py"):
        expected = subprocess.check_output(["git", "show", f"{BASE}:{name}"], cwd=ROOT)
        if (ROOT / name).read_bytes() != expected:
            raise RuntimeError("Pinned scientific evaluator changed")
    if np.__version__ != "2.0.2" or scipy.__version__ != "1.13.1":
        raise RuntimeError("002 execution requires the final 001 NumPy/SciPy runtime")
    manifest = json.loads((PARENT / "FROZEN_MANIFEST.json").read_text())
    prediction_sha = json.loads((PARENT / "SCORING_RECEIPT.json").read_text())["private_predictions_sha256"]
    for file, digest in (("windows.pkl", manifest["windows_sha256"]),
                         ("corpus-folds.json", manifest["corpus_fold_sha256"]),
                         ("predictions.pkl", prediction_sha)):
        if shared.sha(parent_private / file) != digest:
            raise RuntimeError("Parent private cache identity mismatch: " + file)
    return manifest, prediction_sha


def unflagged_shots(shots):
    """Delete only stored reset_like=True shots, preserving object order and folds."""
    if any(type(s.flags.get("reset_like")) is not bool for s in shots):
        raise ValueError("Missing/non-boolean stored reset flag")
    return [s for s in shots if not s.flags["reset_like"]]


def require_unflagged(shots):
    """Guard every 002 fit, calibration, score, audit and reporting entry point."""
    if not shots or any(s.flags.get("reset_like") is not False for s in shots):
        raise RuntimeError("002 requires only stored unflagged shots")


def shot_bytes_digest(shots):
    """Aggregate continuity digest over complete ordered shot objects; no public IDs."""
    digest = hashlib.sha256()
    for shot in shots:
        digest.update(hashlib.sha256(pickle.dumps(shot, protocol=5)).digest())
    return digest.hexdigest()


def prepare(parent_private, private, output):
    """Filter authenticated parent objects without extraction or fold generation."""
    started = time.process_time()
    parent, prediction_sha = verify_parent(parent_private)
    with (parent_private / "windows.pkl").open("rb") as f:
        original = pickle.load(f)
    shots = unflagged_shots(original)
    require_unflagged(shots)
    if len(original) != parent["shots"]:
        raise RuntimeError("Parent shot count mismatch")
    # No clone/re-extraction/reassignment: retained objects are the original objects.
    keep = {s.key for s in shots}
    if len(keep) != len(shots):
        raise RuntimeError("Duplicate logical shots")
    records = json.loads((parent_private / "corpus-folds.json").read_text())
    for record in records:
        if record["reason"] == "retained" and record["key"] not in keep:
            record["reason"] = "excluded_reset_like"
    membership = {r["key"]: r for r in records if r["reason"] == "retained"}
    if set(membership) != keep or any(membership[s.key]["fold"] != s.fold for s in shots):
        raise RuntimeError("Parent membership/fold continuity failure")
    public_folds = [dict(fold=f, shots=sum(s.fold == f for s in shots),
                        users=len({s.user for s in shots if s.fold == f})) for f in range(5)]
    if any(r["shots"] < 20 or r["users"] < 10 for r in public_folds):
        raise RuntimeError("Updated fold partition needs release suppression")
    body = pickle.dumps(shots, protocol=5)
    corpus_body = json.dumps(records, indent=2, sort_keys=True, allow_nan=False) + "\n"
    manifest = dict(task_id=TASK, base_sha=BASE, snapshot=parent["snapshot"],
        settings=asdict(Settings()), seed=parent["seed"], exclusion="stored reset_like == True",
        correction_status="post_hoc_from_001_breakdowns", fold_assignment="inherited_001_no_regeneration",
        parent_corpus_fold_sha256=parent["corpus_fold_sha256"], parent_windows_sha256=parent["windows_sha256"],
        parent_predictions_sha256=prediction_sha,
        corpus_fold_sha256=hashlib.sha256(corpus_body.encode()).hexdigest(),
        windows_sha256=hashlib.sha256(body).hexdigest(), starts_sha256=parent["starts_sha256"],
        survivor_object_sha256=shot_bytes_digest(shots),
        folds=public_folds, shots=len(shots), users=len({s.user for s in shots}),
        windows=sum(len(s.windows) for s in shots), excluded_shots=len(original)-len(shots))
    frozen = output / "FROZEN_MANIFEST.json"
    if frozen.exists() and json.loads(frozen.read_text()) != manifest:
        raise RuntimeError("002 preparation differs from frozen manifest; preserve existing files")
    for path, content in ((private / "windows.pkl", body),
                          (private / "corpus-folds.json", corpus_body.encode())):
        if path.exists() and path.read_bytes() != content:
            raise RuntimeError("Existing 002 private cache mismatch")
        path.write_bytes(content)
    (output / "STARTS.json").write_bytes((PARENT / "STARTS.json").read_bytes())
    shared.write_json(frozen, manifest)
    shared.csv_write(output / "FOLD_MANIFEST.csv", public_folds)
    with (PARENT / "FUNNEL.csv").open() as f:
        funnel = list(csv.DictReader(f))
    funnel[-1]["stage"] = "001_structurally_usable"
    funnel.append(dict(stage="002_unflagged", shots=len(shots), users=manifest["users"]))
    shared.csv_write(output / "FUNNEL.csv", funnel)
    shared.write_json(output / "CONTINUITY.json", dict(parent_shots=len(original),
        excluded_shots=manifest["excluded_shots"], surviving_shots=len(shots),
        surviving_users=manifest["users"], observations_and_folds_unchanged=True,
        survivor_object_sha256=manifest["survivor_object_sha256"], fold_generator_called=False))
    shared.write_json(private / "preparation.json", dict(core_hours=(time.process_time()-started)/3600))
    print(json.dumps(dict(funnel=funnel, folds=public_folds, windows=manifest["windows"])))


def verified_shots(private, output):
    """Require committed 002 freeze, matching bytes and exclusion before consumption."""
    manifest = shared.verify_freeze(private, output)
    if manifest.get("task_id") != TASK or manifest.get("base_sha") != BASE:
        raise RuntimeError("Not the 002 cohort")
    with (private / "windows.pkl").open("rb") as f:
        shots = pickle.load(f)
    require_unflagged(shots)
    if shot_bytes_digest(shots) != manifest["survivor_object_sha256"]:
        raise RuntimeError("Surviving observations/folds changed")
    return shots, manifest


def c0_reproduction(shots, parent_shots, parent_cache):
    """Recompute C0 from early observations; compare rounded references and parent cache."""
    require_unflagged(shots)
    lookup = {s.key: i for i, s in enumerate(parent_shots)}
    errors, normalized = [], []
    maximum_prediction_difference = 0.0
    saved = fitted_model("C0", {})
    for shot in shots:
        early = [w for w in shot.windows if w.role == "calibration"]
        later = [w for w in shot.windows if w.role == "score"]
        prediction, _ = predict(saved, early, later)
        parent_index = lookup[shot.key]
        previous = parent_shots[parent_index]
        if pickle.dumps(previous, protocol=5) != pickle.dumps(shot, protocol=5):
            raise RuntimeError("C0 survivor window/fold mismatch")
        mask = np.array([w.role == "score" for w in previous.windows])
        old = parent_cache["prediction"]["C0"][parent_index][mask]
        maximum_prediction_difference = max(maximum_prediction_difference, float(np.max(np.abs(prediction-old))))
        err = np.sqrt(np.mean((prediction-np.array([w.flow_g_s for w in later]))**2))
        scale = max(np.sqrt(np.mean([w.flow_g_s**2 for w in early])), .1)
        errors.append(err)
        normalized.append(err/scale)
    ids = range(len(shots))
    values = dict(rmse_g_s=shared.user_mean(errors, shots, ids),
                  nrmse=shared.user_mean(normalized, shots, ids))
    passed = (all(abs(values[k]-C0_REFERENCE[k]) <= C0_ATOL for k in values)
              and maximum_prediction_difference <= C0_ATOL)
    return dict(passed=passed, **values, reference=C0_REFERENCE, absolute_tolerance=C0_ATOL,
                maximum_parent_prediction_difference=maximum_prediction_difference,
                shots=len(shots), users=len({s.user for s in shots}))


def check_c0(parent_private, private, output):
    """Mandatory stop-on-discrepancy reproduction, before nonlinear fits or interpretation."""
    shots, manifest = verified_shots(private, output)
    started = time.process_time()
    with (parent_private / "windows.pkl").open("rb") as f:
        original = pickle.load(f)
    with (parent_private / "predictions.pkl").open("rb") as f:
        cache = pickle.load(f)
    result = c0_reproduction(shots, original, cache)
    result.update(windows_sha256=manifest["windows_sha256"], plan_sha256=shared.sha(output / "PLAN.md"),
                  core_hours=(time.process_time()-started)/3600)
    shared.write_json(output / "C0_REPRODUCTION.json", result)
    if not result["passed"]:
        raise RuntimeError("STOP: C0 reproduction discrepancy; no fitting or interpretation")
    print(json.dumps(result))


def require_c0(output, manifest):
    receipt = json.loads((output / "C0_REPRODUCTION.json").read_text())
    if (not receipt["passed"] or receipt["windows_sha256"] != manifest["windows_sha256"]
            or receipt["plan_sha256"] != shared.sha(output / "PLAN.md")):
        raise RuntimeError("Missing/mismatched C0 reproduction")


def require_models(output, manifest, deployment=False):
    """Validate provenance at audit/scoring, independently of the fitting skip guard."""
    for fold in (["all"] if deployment else range(5)):
        folder = "deployment" if fold == "all" else f"fold_{fold}"
        contract = shared.resume_contract(manifest, fold, output)
        for model in MODELS:
            saved = load_model(output / "models" / folder / (model + ".json"))
            if not shared.resume_matches(saved, model, contract):
                raise RuntimeError("Foreign/stale model in 002: " + folder + "/" + model)


def require_audit(private, output, manifest, deployment=False):
    """Require a complete, current CV or deployment numerical receipt."""
    filename = "deployment_quadrature.json" if deployment else "quadrature.json"
    receipt = json.loads((private / filename).read_text())
    folders = ["deployment"] if deployment else [f"fold_{f}" for f in range(5)]
    expected = {(folder, m) for folder in folders for m in MODELS}
    rows = receipt.get("rows", [])
    if (not receipt.get("passed") or len(rows) != len(expected)
            or {(r["folder"], r["model"]) for r in rows} != expected
            or not all(r["passed"] for r in rows)
            or receipt.get("windows_sha256") != manifest["windows_sha256"]
            or receipt.get("plan_sha256") != shared.sha(output / "PLAN.md")
            or receipt.get("auditor_sha256") != shared.sha(ROOT / "puckworks/empirical/visualizer.py")):
        raise RuntimeError("Incomplete/foreign 002 numerical audit")
    for row in rows:
        if row["model_sha256"] != shared.sha(output / "models" / row["folder"] / (row["model"] + ".json")):
            raise RuntimeError("002 model changed after audit")


def compare_parent(parent_private, private, output):
    """Compare cached 001/002 predictions on exactly the same surviving shot windows."""
    shots, _ = verified_shots(private, output)
    with (parent_private / "windows.pkl").open("rb") as f:
        parent_shots = pickle.load(f)
    lookup = {s.key: i for i, s in enumerate(parent_shots)}
    with (parent_private / "predictions.pkl").open("rb") as f:
        parent_cache = pickle.load(f)
    with (private / "predictions.pkl").open("rb") as f:
        cache = pickle.load(f)
    if cache.get("provenance") != shared.prediction_provenance(output):
        raise RuntimeError("Foreign/stale 002 prediction cache")
    for shot in shots:
        if pickle.dumps(shot, protocol=5) != pickle.dumps(parent_shots[lookup[shot.key]], protocol=5):
            raise RuntimeError("Matched comparison observations/folds changed")
    rows = []
    for subset, ids in (("overall", list(range(len(shots)))),
                        ("pressure_varying", [i for i, s in enumerate(shots) if s.pressure_varying])):
        if not shared.release_ok(ids, shots, range(len(shots))):
            continue
        groups = [[i for i in ids if shots[i].fold == fold] for fold in range(5)]
        folds = ["all", *range(5)] if all(shared.release_ok(g, shots, ids) for g in groups) else ["all"]
        for fold in folds:
            group = ids if fold == "all" else [i for i in ids if shots[i].fold == fold]
            for model in MODELS:
                old_errors, new_errors, scales = [], [], []
                for i in group:
                    shot = shots[i]
                    j = lookup[shot.key]
                    mask = np.array([w.role == "score" for w in shot.windows])
                    q = np.array([w.flow_g_s for w in shot.windows])[mask]
                    old_errors.append(np.sqrt(np.mean((parent_cache["prediction"][model][j][mask]-q)**2)))
                    new_errors.append(np.sqrt(np.mean((cache["prediction"][model][i][mask]-q)**2)))
                    scales.append(max(np.sqrt(np.mean([w.flow_g_s**2 for w in shot.windows
                                                      if w.role == "calibration"])), .1))
                for metric in ("rmse_g_s", "nrmse"):
                    divisor = np.array(scales) if metric == "nrmse" else 1
                    old = shared.user_mean(np.array(old_errors)/divisor, shots, group)
                    new = shared.user_mean(np.array(new_errors)/divisor, shots, group)
                    rows.append(dict(subset=subset, fold=fold, model=model, metric=metric,
                                     parent_full_cohort_fit=old, filtered_fit=new, difference=new-old,
                                     shots=len(group), users=len({shots[i].user for i in group})))
    shared.csv_write(output / "MATCHED_COMPARISON.csv", rows)


def export_diagnostics(private, output):
    """Export saved parameters/bounds, audits, hashes and separate deployment cost."""
    manifest = json.loads((output / "FROZEN_MANIFEST.json").read_text())
    index, bounds, audits = [], [], []
    cost = dict(cross_validation=0.0, deployment=0.0)
    selected = dict(cross_validation=0, deployment=0)
    for fold in [*range(5), "all"]:
        folder = "deployment" if fold == "all" else f"fold_{fold}"
        role = "deployment" if fold == "all" else "cross_validation"
        for model in MODELS:
            path = output / "models" / folder / (model + ".json")
            saved = load_model(path)
            md = saved["metadata"]
            cost[role] += md.get("core_hours", 0.0)
            selected[role] += model != "C0"
            index.append(dict(folder=folder, model=model, role=role,
                model_sha256=shared.sha(path), shots=md["training_shots"],
                users=md["training_users"], selected_success=md.get("selected_success", True)))
            names, limits = coordinates(model)
            for name, value, (low, high) in zip(names, encode(model, saved["parameters"]), limits):
                parameter = name.removeprefix("log_")
                lower = bool(abs(value-low) <= 1e-7) if low is not None else False
                upper = bool(abs(value-high) <= 1e-7) if high is not None else False
                bounds.append(dict(folder=folder, model=model, role=role, coordinate=name,
                    parameter=parameter, value=saved["parameters"][parameter],
                    transformed_value=float(value), transformed_lower=low, transformed_upper=high,
                    lower_contact=lower, upper_contact=upper,
                    contact_tolerance=1e-7, shots=md["training_shots"], users=md["training_users"]))
    for filename in ("quadrature.json", "deployment_quadrature.json"):
        receipt = json.loads((private / filename).read_text())
        if not receipt["passed"]:
            raise RuntimeError("Cannot export a failed selected-model audit as qualified")
        for row in receipt["rows"]:
            audits.append(dict(**row, shots=manifest["shots"], users=manifest["users"]))
    shared.csv_write(output / "MODEL_INDEX.csv", index)
    shared.csv_write(output / "PARAMETER_BOUNDS.csv", bounds)
    shared.csv_write(output / "NUMERICAL_AUDITS.csv", audits)
    # Paired fold differences commute with the identical-shot equal-user mean.
    with (output / "SCORES.csv").open() as f:
        score_rows = [r for r in csv.DictReader(f)
                      if r["scope"] == "prediction" and r["fold"] != "all"]
    scores = {(r["subset"], r["fold"], r["metric"], r["model"]): r for r in score_rows}
    fold_contrasts = []
    for subset, fold, metric in sorted({k[:3] for k in scores}):
        for a, b in CONTRASTS:
            first, second = (scores[subset, fold, metric, m] for m in (a, b))
            fold_contrasts.append(dict(subset=subset, fold=fold, metric=metric,
                contrast=f"{a}-{b}", difference=float(first["value"])-float(second["value"]),
                shots=first["shots"], users=first["users"]))
    shared.csv_write(output / "FOLD_CONTRASTS.csv", fold_contrasts)
    other = {name: json.loads((private / name).read_text())["core_hours"]
             for name in ("preparation.json", "quadrature.json", "deployment_quadrature.json")}
    other["C0_reproduction"] = json.loads((output / "C0_REPRODUCTION.json").read_text())["core_hours"]
    with (private / "predictions.pkl").open("rb") as f:
        cache = pickle.load(f)
    if cache.get("provenance") != shared.prediction_provenance(output):
        raise RuntimeError("Foreign/stale 002 prediction cache")
    other["prediction_and_reconstruction"] = cache["core_hours"]
    accounting = dict(completed_shared_fits=selected, analytical_C0_models=6,
        optimizer_core_hours=cost, other_recorded_core_hours=other,
        recorded_total_core_hours=sum(cost.values())+sum(other.values()),
        accounting_scope="Recorded process CPU; benchmark and deployment optimization separate",
        excluded_unmetered="Fit driver/design overhead, repeated hash checks, report/bootstrap/comparison, figures, tests, review and hosted CI",
        deployment_excluded_from_scoring_and_contrasts=True)
    wall = private / "fit-wall.json"
    if wall.exists():
        accounting["fit_batch_wall_hours"] = json.loads(wall.read_text())["wall_hours"]
    shared.write_json(output / "ACCOUNTING.json", accounting)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("phase", choices=("prepare", "check-c0", "fit", "deploy", "audit", "audit-deployment", "score", "report", "export"))
    parser.add_argument("--private", type=Path, required=True)
    parser.add_argument("--parent-private", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=OUT)
    parser.add_argument("--fold", choices=list(map(str, range(5))))
    parser.add_argument("--workers", type=int, default=8)
    args = parser.parse_args()
    output, private, parent_private = validate_locations(args.output, args.private, args.parent_private)
    output.mkdir(parents=True, exist_ok=True)
    private.mkdir(parents=True, exist_ok=True)
    verify_parent(parent_private)
    if args.phase == "prepare":
        prepare(parent_private, private, output)
        return
    _, manifest = verified_shots(private, output)
    if args.phase == "check-c0":
        check_c0(parent_private, private, output)
        return
    require_c0(output, manifest)
    if args.phase in ("fit", "deploy"):
        if args.phase == "fit" and args.fold is None:
            parser.error("fit requires --fold")
        shared.fit_models(private, "all" if args.phase == "deploy" else args.fold, args.workers, output)
    elif args.phase in ("audit", "audit-deployment"):
        deployment = args.phase == "audit-deployment"
        require_models(output, manifest, deployment)
        shared.audit(private, deployment, output)
    elif args.phase == "export":
        require_models(output, manifest)
        require_models(output, manifest, True)
        require_audit(private, output, manifest)
        require_audit(private, output, manifest, True)
        export_diagnostics(private, output)
    else:
        require_models(output, manifest)
        if args.phase == "score":
            require_audit(private, output, manifest)
            shared.score(private, output, CONTRASTS)
        else:
            shared.report(private, output, CONTRASTS)
        compare_parent(parent_private, private, output)


if __name__ == "__main__":
    main()
