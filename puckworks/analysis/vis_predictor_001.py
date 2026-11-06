"""Reproduce the frozen Visualizer predictor benchmark; private records stay outside Git.

Phases: prepare (no fitting/scoring), fit (training only), score (cached held-outs),
deploy (all-user artifacts, excluded from scores). See the committed PLAN.md.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from concurrent.futures import ProcessPoolExecutor
import csv
from dataclasses import asdict
import gzip
import json
import multiprocessing
from pathlib import Path
import pickle
import subprocess
import time

import numpy as np

from puckworks.analysis.cor15_shape_001 import N, PD_BAR, PSTAR_BAR
from puckworks.analysis.pressure_peak_x1 import authenticate, project, sha
from puckworks.empirical.visualizer import (
    Design, MODELS, SEED, Settings, Shot, capacity_maximum, decode,
    extract_windows, fit_start, fitted_model, grouped_folds, load_model, save_model,
    start_schedule, recorded_pressure_range,
)
from puckworks.lib.visualizer_harvest import latest_index_rows

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "docs/research/VIS_PREDICTOR_001"
CREDIT = "Data source: Visualizer; thanks to the contributing users who made their shots public."
CONTRASTS = (("AR", "M0R"), ("AR", "T0"), ("AR", "R0"),
             ("M0R", "R0"), ("R0", "C0"), ("T0", "C0"))
SOURCES = ("puckworks/empirical/visualizer.py", "puckworks/analysis/vis_predictor_001.py",
           "puckworks/analysis/pressure_peak_x1.py", "puckworks/analysis/cor15_shape_001.py")


def write_json(path, value):
    Path(path).write_text(json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n")


def csv_write(path, rows):
    if not rows:
        return
    fields = list(dict.fromkeys(k for row in rows for k in row))
    with Path(path).open("w", newline="") as f:
        writer = csv.DictWriter(f, fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def check_private(path):
    path = Path(path).resolve()
    if path == ROOT or ROOT in path.parents:
        raise ValueError("Private output must be outside repository")
    path.mkdir(parents=True, exist_ok=True)
    return path


def release_ok(indices, shots, universe=None):
    """20 shots/10 users, including the complementary group (empty cells allowed)."""
    chosen = set(indices)
    if not chosen:
        return True
    users = {shots[i].user for i in chosen if shots[i].user}
    if len(chosen) < 20 or len(users) < 10:
        return False
    if universe is not None:
        remaining = set(universe) - chosen
        if remaining and (len(remaining) < 20 or
                          len({shots[i].user for i in remaining if shots[i].user}) < 10):
            return False
    return True


def prepare(root, inventory, private, output_root=None):
    """Authenticate/read allowed channels, extract and freeze; no model score is computed."""
    out = OUT if output_root is None else Path(output_root).resolve()
    started = time.process_time()
    frozen_path = out / "FROZEN_MANIFEST.json"
    existing = json.loads(frozen_path.read_text()) if frozen_path.exists() else None
    snapshot, audit = authenticate(root, inventory)
    winners = latest_index_rows(snapshot._cfg)
    wanted = {"id": True, "updated_at": True, "content_sha256": True, "hashed_user": True,
              "hydraulic": {"time__s": True, "pressure__Pa": True, "weight__kg": True,
                            "mass_flow_from_scale__kg_per_s": True, "flow_reported__native": "LENGTH"}}
    shots, records, seen = [], [], set()
    counts = Counter()
    census_users = defaultdict(set)
    for shard in sorted(Path(root).glob("shard_*.jsonl.gz")):
        with gzip.open(shard, "rt") as f:
            for line in f:
                rec, _ = project(line, wanted)
                sid = rec["id"]
                winner = winners.get(sid)
                if (not winner or sid in seen or str(rec.get("updated_at")) != winner["updated_at"]
                        or rec.get("content_sha256") != winner["content_sha256"]):
                    continue
                seen.add(sid)
                user = rec.get("hashed_user") or ""
                counts["canonical"] += 1
                census_users["canonical"].add(user)
                h = rec.get("hydraulic", {})
                t, p, w = (h.get(k) or [] for k in ("time__s", "pressure__Pa", "weight__kg"))
                common = len(t) >= 2 and len(t) == len(p) == len(w)
                if common:
                    counts["pressure_weight_common_time"] += 1
                    census_users["pressure_weight_common_time"].add(user)
                windows, flags, reason = extract_windows(t, p, w, h.get("mass_flow_from_scale__kg_per_s"),
                    generic_flow_present=bool(h.get("flow_reported__native")))
                if windows and not user:
                    windows, reason = [], "missing_user_linkage"
                counts[reason] += 1
                record = dict(key=sid, user=user, content_sha256=rec.get("content_sha256"),
                              reason=reason)
                if windows:
                    shots.append(Shot(sid, user, windows, flags))
                    census_users["retained"].add(user)
                    record["windows"] = [[x.start_s, x.end_s, x.role] for x in windows]
                records.append(record)
    if seen != set(winners):
        raise RuntimeError("Incomplete canonical join")
    shots.sort(key=lambda s: s.key)
    folds = grouped_folds([s.user for s in shots])
    for s in shots:
        s.fold = folds[s.user]
    for r in records:
        if r["reason"] == "retained":
            r["fold"] = folds[r["user"]]
    write_json(private / "corpus-folds.json", sorted(records, key=lambda r: r["key"]))
    with (private / "windows.pkl").open("wb") as f:
        pickle.dump(shots, f, protocol=5)
    historical = [dict(source="D0_A_DESCRIPTIVE_ALL", n=N, Pd=PD_BAR, kappa=1 / PSTAR_BAR)]
    with (ROOT / "docs/research/JOINT_CLOCK_001/FITS.csv").open() as f:
        for row in csv.DictReader(f):
            if row["fold"] == "DESCRIPTIVE_ALL":
                historical.append(dict(source=row["key"], n=float(row["n"]),
                                       Pd=float(row["Pd_bar"]), kappa=1 / float(row["Pstar_bar"])))
    write_json(out / "STARTS.json", historical)
    fold_rows = [dict(fold=f, shots=sum(s.fold == f for s in shots),
                      users=len({s.user for s in shots if s.fold == f})) for f in range(5)]
    if any(r["shots"] < 20 or r["users"] < 10 for r in fold_rows):
        raise RuntimeError("Fold counts need release suppression")
    # Public funnel has only large cumulative groups; detailed reasons remain private.
    funnel = [dict(stage=k, shots=counts[k], users=len(census_users[k] - {""}))
              for k in ("canonical", "pressure_weight_common_time", "retained")]
    csv_write(out / "FUNNEL.csv", funnel)
    csv_write(out / "FOLD_MANIFEST.csv", fold_rows)
    base = existing["base_sha"] if existing else subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    manifest = dict(base_sha=base, snapshot=audit, settings=asdict(Settings()),
                    corpus_fold_sha256=sha(private / "corpus-folds.json"),
                    windows_sha256=sha(private / "windows.pkl"),
                    starts_sha256=sha(out / "STARTS.json"), folds=fold_rows,
                    shots=len(shots), users=len(folds),
                    windows=sum(len(s.windows) for s in shots), seed=SEED)
    if existing is not None and manifest != existing:
        write_json(private / "mismatched-preparation.json", manifest)
        raise RuntimeError("Preparation differs from frozen manifest; no scoring")
    write_json(frozen_path, manifest)
    write_json(private / "preparation.json", dict(counts=dict(counts), audit=audit,
               core_hours=(time.process_time() - started) / 3600))
    print(json.dumps(dict(funnel=funnel, folds=fold_rows, windows=manifest["windows"])))


def verify_freeze(private, output_root=None):
    """Require the exact PLAN and manifest already committed, and matching private bytes."""
    out = OUT if output_root is None else Path(output_root).resolve()
    for name in ("PLAN.md", "FROZEN_MANIFEST.json", "STARTS.json", "FOLD_MANIFEST.csv"):
        relative = str((out / name).relative_to(ROOT))
        committed = subprocess.check_output(["git", "show", "HEAD:" + relative], cwd=ROOT)
        if committed != (out / name).read_bytes():
            raise RuntimeError("Uncommitted freeze: " + name)
    manifest = json.loads((out / "FROZEN_MANIFEST.json").read_text())
    if manifest["settings"] != asdict(Settings()):
        raise RuntimeError("Engineering settings changed after freeze")
    for filename, key in (("corpus-folds.json", "corpus_fold_sha256"),
                          ("windows.pkl", "windows_sha256")):
        if sha(private / filename) != manifest[key]:
            raise RuntimeError("Private frozen file changed")
    if sha(out / "STARTS.json") != manifest["starts_sha256"]:
        raise RuntimeError("Starts changed")
    return manifest


_FIT_DESIGN = None
_FIT_MODEL = None


def _one_start(theta):
    return fit_start(_FIT_DESIGN, _FIT_MODEL, theta)


def resume_contract(manifest, fold, output_root):
    """Bind cached fits to task/cohort/plan/fold and the unchanged numerical code."""
    out = Path(output_root).resolve()
    import platform
    import scipy
    return dict(task_id=manifest.get("task_id", "PW-VIS-PREDICTOR-001"), fold=str(fold),
                corpus_fold_sha256=manifest["corpus_fold_sha256"],
                windows_sha256=manifest["windows_sha256"], plan_sha256=sha(out / "PLAN.md"),
                starts_sha256=sha(out / "STARTS.json"), settings=asdict(Settings()),
                integration=dict(max_pressure_step_bar=.1),
                runtime=dict(python=platform.python_version(), numpy=np.__version__, scipy=scipy.__version__),
                evaluator_sha256=sha(ROOT / "puckworks/empirical/visualizer.py"))


def resume_matches(saved, model, contract):
    """A foreign/stale artifact must never satisfy a requested fit's skip check."""
    return (isinstance(saved, dict) and saved.get("model") == model and saved.get("settings") == contract["settings"]
            and saved.get("integration") == contract["integration"]
            and saved.get("metadata", {}).get("resume_contract") == contract)


def fit_models(private, fold, workers, output_root=None):
    """One outer fold (or deployment); shared training never sees excluded users."""
    out = OUT if output_root is None else Path(output_root).resolve()
    global _FIT_DESIGN, _FIT_MODEL
    manifest = verify_freeze(private, out)
    legacy_resume = manifest.get("task_id", "PW-VIS-PREDICTOR-001") == "PW-VIS-PREDICTOR-001"
    with (private / "windows.pkl").open("rb") as f:
        all_shots = pickle.load(f)
    if manifest.get("task_id") == "PW-VIS-PREDICTOR-002":
        if any(s.flags.get("reset_like") is not False for s in all_shots):
            raise RuntimeError("Flagged/unknown reset status reached 002 fitting")
    training = [s for s in all_shots if fold == "all" or s.fold != int(fold)]
    if fold != "all":
        assert not ({s.user for s in training} & {s.user for s in all_shots if s.fold == int(fold)})
    # Large-array sort integrity failed under concurrent design construction on the
    # execution host. Serialize this preprocessing only; optimizer starts stay parallel.
    import fcntl
    with (private / ".design.lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        _FIT_DESIGN = Design(training)
    historical = json.loads((out / "STARTS.json").read_text())
    modeldir = out / "models" / ("deployment" if fold == "all" else "fold_" + str(fold))
    modeldir.mkdir(parents=True, exist_ok=True)
    private_modeldir = private / ("deployment" if fold == "all" else "fold_" + str(fold))
    private_modeldir.mkdir(exist_ok=True)
    import platform
    import scipy
    metadata = dict(role="deployment_only" if fold == "all" else "held_out_user_fold",
                    resume_contract=resume_contract(manifest, fold, out),
                    fold=fold, runtime=dict(python=platform.python_version(), numpy=np.__version__, scipy=scipy.__version__),
                    corpus_fold_sha256=manifest["corpus_fold_sha256"],
                    plan_sha256=sha(out / "PLAN.md"), starts_sha256=sha(out / "STARTS.json"),
                    code_sha256={p: sha(ROOT / p) for p in SOURCES},
                    training_shots=len(training), training_users=len({s.user for s in training}),
                    pressure_range_bar=recorded_pressure_range(_FIT_DESIGN.windows))
    c0_path = modeldir / "C0.json"
    if legacy_resume and c0_path.exists():
        load_model(c0_path)  # Authenticate and preserve the historical analytical artifact.
    else:
        save_model(c0_path, fitted_model("C0", {}, metadata))
    for model in MODELS[1:]:
        path = modeldir / (model + ".json")
        if path.exists():
            if legacy_resume:
                # The pinned 001 artifacts predate resume_contract. Retain their
                # authenticated hash/integration skip behavior without refitting.
                existing = load_model(path)
                if "n" in existing["parameters"] and existing.get("integration") != _FIT_DESIGN.integration:
                    raise RuntimeError("Cached pressure model uses different integration")
                continue
            try:
                existing = load_model(path)
            except (OSError, ValueError):
                existing = None  # malformed/hash-mismatched artifacts cannot be resumed
            if resume_matches(existing, model, metadata["resume_contract"]):
                continue
            # Preserve a stale artifact privately before performing the requested fit.
            stale = private_modeldir / (model + "_stale_" + sha(path) + ".json")
            stale.write_bytes(path.read_bytes())
        nested = None
        if model in ("AR", "A"):
            nested = load_model(modeldir / ("M0R.json" if model == "AR" else "M0.json"))
        starts = start_schedule(model, historical, nested)
        _FIT_MODEL = model
        with ProcessPoolExecutor(max_workers=workers, mp_context=multiprocessing.get_context("fork")) as pool:
            attempts = list(pool.map(_one_start, starts))
        if nested is not None:
            value, _ = _FIT_DESIGN.objective(model, starts[0])
            attempts.append(dict(theta=starts[0].tolist(), objective=value, success=True,
                                 message="exact monotone candidate", evaluations=1,
                                 iterations=0, core_hours=0.0))
        write_json(private_modeldir / (model + "_starts.json"), attempts)
        finite = [(i, a) for i, a in enumerate(attempts) if a["objective"] is not None and np.isfinite(a["objective"])]
        if not finite:
            raise RuntimeError("No finite start: " + model)
        i, best = min(finite, key=lambda pair: pair[1]["objective"])
        params = decode(model, best["theta"])
        md = dict(metadata, selected_start=i, training_objective_g_s=best["objective"],
                  selected_success=best["success"], starts=len(starts),
                  converged_starts=sum(a["success"] for a in attempts[:len(starts)]),
                  core_hours=sum(a["core_hours"] for a in attempts),
                  start_diagnostics=[{k: v for k, v in a.items() if k != "theta"} for a in attempts])
        if "n" in params:
            md["capacity_maximum"] = capacity_maximum(params, md["pressure_range_bar"])
        save_model(path, fitted_model(model, params, md))
        print(json.dumps(dict(fold=fold, model=model, objective=best["objective"],
                              parameters=params, core_hours=md["core_hours"])), flush=True)


def user_mean(values, shots, indices):
    groups = defaultdict(list)
    for i, v in zip(indices, values):
        groups[shots[i].user].append(float(v))
    return float(np.mean([np.mean(v) for v in groups.values()]))


def audit(private, deployment=False, output_root=None):
    """Audit all selected shapes on pressure covariates before any held-out scoring."""
    out = OUT if output_root is None else Path(output_root).resolve()
    from puckworks.empirical.visualizer import audit_quadrature
    verify_freeze(private, out)
    with (private / "windows.pkl").open("rb") as f:
        shots = pickle.load(f)
    folder_names = ["deployment"] if deployment else [f"fold_{i}" for i in range(5)]
    started = time.process_time()
    rows = []
    for folder in folder_names:
        for model in MODELS:
            path = out / "models" / folder / (model + ".json")
            saved = load_model(path)
            result = audit_quadrature(shots, saved)
            row = dict(folder=folder, model=model, model_sha256=sha(path), **result)
            rows.append(row)
            print(json.dumps(row), flush=True)
    receipt = dict(rows=rows, passed=all(row["passed"] for row in rows),
                   windows_sha256=sha(private / "windows.pkl"),
                   plan_sha256=sha(out / "PLAN.md"),
                   auditor_sha256=sha(ROOT / "puckworks/empirical/visualizer.py"),
                   core_hours=(time.process_time() - started) / 3600)
    write_json(private / ("deployment_quadrature.json" if deployment else "quadrature.json"), receipt)
    if not receipt["passed"]:
        raise RuntimeError("Quadrature audit failed; preserve version, no scoring")


def prediction_provenance(output_root):
    """Bind a cache to the exact cohort, plan, evaluator and CV model inventory."""
    out = Path(output_root).resolve()
    manifest = json.loads((out / "FROZEN_MANIFEST.json").read_text())
    return dict(task_id=manifest.get("task_id", "PW-VIS-PREDICTOR-001"),
                corpus_fold_sha256=manifest["corpus_fold_sha256"],
                windows_sha256=manifest["windows_sha256"], plan_sha256=sha(out / "PLAN.md"),
                evaluator_sha256=sha(ROOT / "puckworks/empirical/visualizer.py"),
                models={f"fold_{fold}/{model}": sha(out / "models" / f"fold_{fold}" / (model + ".json"))
                        for fold in range(5) for model in MODELS})


def score(private, output_root=None, contrast_pairs=CONTRASTS):
    """Score once; persist private predictions before aggregate-only export."""
    out = OUT if output_root is None else Path(output_root).resolve()
    verify_freeze(private, out)
    receipt = json.loads((private / "quadrature.json").read_text())
    if not receipt["passed"] or receipt["windows_sha256"] != sha(private / "windows.pkl"):
        raise RuntimeError("Missing/mismatched quadrature qualification")
    for row in receipt["rows"]:
        if row["model_sha256"] != sha(out / "models" / row["folder"] / (row["model"] + ".json")):
            raise RuntimeError("Model changed after quadrature audit")
    if (private / "predictions.pkl").exists():
        raise RuntimeError("Predictions already cached; use report, never silently rescore")
    with (private / "windows.pkl").open("rb") as f:
        shots = pickle.load(f)
    predictions = {m: [None] * len(shots) for m in MODELS}
    reconstruction = {m: [None] * len(shots) for m in MODELS}
    params = []
    start = time.process_time()
    for fold in range(5):
        ids = [i for i, s in enumerate(shots) if s.fold == fold]
        design = Design([shots[i] for i in ids])
        for model in MODELS:
            saved = load_model(out / "models" / f"fold_{fold}" / (model + ".json"))
            from puckworks.empirical.visualizer import encode
            theta = encode(model, saved["parameters"])
            if "n" in saved["parameters"] and saved.get("integration") != design.integration:
                raise RuntimeError("Saved pressure integration differs from scoring design")
            pred, _ = design.profile(model, theta)
            rec, _ = design.profile(model, theta, all_windows=True)
            for j, i in enumerate(ids):
                mask = design.shot_index == j
                predictions[model][i] = pred[mask]
                reconstruction[model][i] = rec[mask]
            md = saved["metadata"]
            params.append(dict(fold=fold, model=model, **saved["parameters"],
                **md.get("capacity_maximum", {}), training_pressure_min_bar=md["pressure_range_bar"][0],
                training_pressure_max_bar=md["pressure_range_bar"][1],
                selected_success=md.get("selected_success", True),
                training_objective_g_s=md.get("training_objective_g_s", ""),
                core_hours=md.get("core_hours", 0), model_sha256=sha(
                    out / "models" / f"fold_{fold}" / (model + ".json"))))
    csv_write(out / "FITTED_PARAMETERS.csv", params)
    with (private / "predictions.pkl").open("wb") as f:
        pickle.dump(dict(prediction=predictions, reconstruction=reconstruction,
                         provenance=prediction_provenance(out),
                         core_hours=(time.process_time() - start) / 3600), f, protocol=5)
    report(private, out, contrast_pairs)


def report(private, output_root=None, contrast_pairs=CONTRASTS):
    """Generate release-compliant aggregates using cached predictions; no refits."""
    out = OUT if output_root is None else Path(output_root).resolve()
    with (private / "windows.pkl").open("rb") as f:
        shots = pickle.load(f)
    with (private / "predictions.pkl").open("rb") as f:
        cache = pickle.load(f)
    if (json.loads((out / "FROZEN_MANIFEST.json").read_text()).get("task_id") == "PW-VIS-PREDICTOR-002"
            and cache.get("provenance") != prediction_provenance(out)):
        raise RuntimeError("Foreign/stale 002 prediction cache")
    all_ids = list(range(len(shots)))
    score_masks = [np.array([w.role == "score" for w in s.windows]) for s in shots]
    scale = np.array([max(np.sqrt(np.mean([w.flow_g_s ** 2 for w in s.windows
                                          if w.role == "calibration"])), .1) for s in shots])
    errors = {}
    for scope in ("prediction", "reconstruction"):
        errors[scope] = {}
        for model in MODELS:
            errors[scope][model] = np.array([np.sqrt(np.mean((cache[scope][model][i][mask] -
                np.array([w.flow_g_s for w in s.windows])[mask]) ** 2))
                for i, s in enumerate(shots) for mask in [score_masks[i] if scope == "prediction"
                                                         else np.ones(len(s.windows), dtype=bool)]])
    varying = [i for i, s in enumerate(shots) if s.pressure_varying]
    subsets = {"overall": all_ids, "pressure_varying": varying}
    results, contrasts = [], []
    for scope, values in errors.items():
        for subset, ids in subsets.items():
            if not release_ok(ids, shots, all_ids):
                continue
            fold_groups = [[i for i in ids if shots[i].fold == fold] for fold in range(5)]
            fold_safe = all(release_ok(group, shots, ids) for group in fold_groups)
            for fold in (("all", *range(5)) if fold_safe else ("all",)):
                group = ids if fold == "all" else [i for i in ids if shots[i].fold == fold]
                if not release_ok(group, shots, all_ids):
                    continue
                for model in MODELS:
                    for metric in ("rmse_g_s", "nrmse"):
                        e = values[model] if metric == "rmse_g_s" else values[model] / scale
                        results.append(dict(scope=scope, subset=subset, fold=fold, model=model,
                            metric=metric, value=user_mean(e[group], shots, group),
                            shots=len(group), users=len({shots[i].user for i in group})))
            if scope != "prediction":
                continue
            users = sorted({shots[i].user for i in ids})
            byuser = {u: [i for i in ids if shots[i].user == u] for u in users}
            draws = np.random.default_rng(SEED).integers(0, len(users), (1000, len(users)))
            for a, b in contrast_pairs:
                for metric in ("rmse_g_s", "nrmse"):
                    delta = values[a] - values[b]
                    if metric == "nrmse":
                        delta = delta / scale
                    paired = np.array([np.mean(delta[byuser[u]]) for u in users])
                    boot = np.mean(paired[draws], axis=1)
                    lo, hi = np.quantile(boot, [.025, .975])
                    contrasts.append(dict(subset=subset, contrast=f"{a}-{b}", metric=metric,
                        difference=float(np.mean(paired)), low=float(lo), high=float(hi),
                        shots=len(ids), users=len(users), resamples=1000))
    csv_write(out / "SCORES.csv", results)
    csv_write(out / "CONTRASTS.csv", contrasts)
    breakdowns = []
    # Whole partitions are suppressed, protecting complements and linked totals.
    partitions = {}
    for flag in shots[0].flags:
        partitions[flag] = {str(value): [i for i, s in enumerate(shots) if s.flags[flag] == value]
                            for value in sorted({s.flags[flag] for s in shots}, key=str)}
    for flag, groups in partitions.items():
        safe = all(release_ok(ids, shots, all_ids) for ids in groups.values())
        if not safe:
            breakdowns.append(dict(diagnostic=flag, group="partition_suppressed"))
            continue
        for group, ids in groups.items():
            for model in MODELS:
                breakdowns.append(dict(diagnostic=flag, group=group, model=model, shots=len(ids),
                    users=len({shots[i].user for i in ids}),
                    rmse_g_s=user_mean(errors["prediction"][model][ids], shots, ids),
                    nrmse=user_mean(errors["prediction"][model][ids] / scale[ids], shots, ids)))
    for name, selectors in (
        ("direction", {"rising": lambda w: w.pressure_change_bar > .25,
                       "falling": lambda w: w.pressure_change_bar < -.25,
                       "level": lambda w: abs(w.pressure_change_bar) <= .25}),
        ("pressure_band", {"0_3": lambda w: w.mean_pressure_bar < 3,
                           "3_6": lambda w: 3 <= w.mean_pressure_bar < 6,
                           "6_9": lambda w: 6 <= w.mean_pressure_bar < 9,
                           "9_plus": lambda w: w.mean_pressure_bar >= 9})):
        masks = {g: [np.array([w.role == "score" and selector(w) for w in s.windows])
                      for s in shots] for g, selector in selectors.items()}
        groups = {g: [i for i, mask in enumerate(mm) if mask.any()] for g, mm in masks.items()}
        if not all(release_ok(ids, shots, all_ids) for ids in groups.values()):
            breakdowns.append(dict(diagnostic=name, group="partition_suppressed"))
            continue
        for group, ids in groups.items():
            for model in MODELS:
                e = [np.sqrt(np.mean((cache["prediction"][model][i][masks[group][i]] -
                    np.array([w.flow_g_s for w in shots[i].windows])[masks[group][i]]) ** 2)) for i in ids]
                breakdowns.append(dict(diagnostic=name, group=group, model=model, shots=len(ids),
                    users=len({shots[i].user for i in ids}), rmse_g_s=user_mean(e, shots, ids),
                    nrmse=user_mean(np.array(e) / scale[ids], shots, ids)))
    csv_write(out / "BREAKDOWNS.csv", breakdowns)
    eligible = [r for r in results if r["scope"] == "prediction" and r["subset"] == "overall"
                and r["fold"] == "all" and r["metric"] == "rmse_g_s" and r["model"] in MODELS]
    best = min(eligible, key=lambda r: (r["value"], MODELS.index(r["model"])))
    write_json(out / "RECOMMENDATION.json", dict(model=best["model"], criterion="primary held-out user RMSE",
        rmse_g_s=best["value"], deployment_refits_used_for_selection=False,
        private_predictions_sha256=sha(private / "predictions.pkl")))
    aggregate_panel(shots, cache["prediction"], out)
    print(json.dumps(dict(best=best, contrasts=contrasts)))


def aggregate_panel(shots, predictions, output_root=None):
    """Fixed early-to-late bins with full linkage suppression; no selected shot trace."""
    out = OUT if output_root is None else Path(output_root).resolve()
    all_ids = set(range(len(shots)))
    rows = []
    prior = all_ids
    prior_users = {s.user for s in shots}
    for start in range(0, 30, 2):
        pairs = [(i, j) for i, s in enumerate(shots) for j, w in enumerate(s.windows)
                 if w.start_s == start]
        ids = {i for i, _ in pairs}
        if not ids:
            continue  # no estimate exists for an unsupported display bin
        users = {shots[i].user for i in ids}
        # Protect support changes too: neighboring means/counts cannot isolate a rare tail.
        if not release_ok(ids, shots, all_ids) or (not release_ok(ids - prior, shots) or not release_ok(prior - ids, shots)):
            continue
        # Changed shots can span many continuing users while only one user leaves.
        # Protect actual contributor-user transitions independently as frozen.
        if any(0 < len(change) < 10 for change in (users - prior_users, prior_users - users)):
            continue
        prior = ids
        prior_users = users
        for model in ("observed", *MODELS):
            values = [shots[i].windows[j].flow_g_s if model == "observed" else predictions[model][i][j]
                      for i, j in pairs]
            indices = [i for i, _ in pairs]
            rows.append(dict(start_s=start, model=model, mean_flow_g_s=user_mean(values, shots, indices),
                             shots=len(ids), users=len({shots[i].user for i in ids})))
    csv_write(out / "AGGREGATED_EXAMPLE.csv", rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("phase", choices=("prepare", "fit", "score", "report", "deploy", "audit", "audit-deployment"))
    parser.add_argument("--private", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=OUT)
    parser.add_argument("--root", type=Path)
    parser.add_argument("--inventory", type=Path)
    parser.add_argument("--fold", choices=list(map(str, range(5))))
    parser.add_argument("--workers", type=int, default=8)
    args = parser.parse_args()
    private = check_private(args.private)
    if args.phase == "prepare":
        prepare(args.root, args.inventory, private, args.output)
    elif args.phase in ("fit", "deploy"):
        fit_models(private, "all" if args.phase == "deploy" else args.fold, args.workers, args.output)
    elif args.phase in ("audit", "audit-deployment"):
        audit(private, deployment=args.phase == "audit-deployment", output_root=args.output)
    elif args.phase == "score":
        score(private, args.output)
    else:
        report(private, args.output)


if __name__ == "__main__":
    main()
