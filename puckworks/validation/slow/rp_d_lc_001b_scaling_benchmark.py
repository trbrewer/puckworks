"""Dormant scaling harness: PERFORMANCE_BENCHMARK_ONLY_NOT_SCIENTIFIC_EVIDENCE."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import time

from puckworks.analysis import rp_d_lc_001b_virtual_fixture as vf
from puckworks.validation.slow import rp_d_lc_001b as driver
from puckworks.validation.slow import rp_d_lc_001b_process_pool as engine

BENCHMARK_LABEL = "PERFORMANCE_BENCHMARK_ONLY_NOT_SCIENTIFIC_EVIDENCE"
BENCHMARK_SCHEMA_VERSION = 1
VALID_BENCHMARK_JOBS = (1, 4, 8, 16, 32)
FIXED_STEPS = 600
CHECK = 200
TASKS_PER_RESOLUTION = 16


def benchmark_corpus():
    tasks = []
    for S in (2, 3):
        for i in range(TASKS_PER_RESOLUTION):
            tasks.append({
                "case_id": "benchmark.S%d.repeat%02d" % (S, i),
                "benchmark_task_id": "S%d_reference_blocked_central_%02d" % (S, i),
                "S": S, "forcing_level": "central", "tau_plus": 2.0,
                "min_steps": FIXED_STEPS, "max_steps": FIXED_STEPS, "check": CHECK,
                "return_fields": list(driver.REQUIRED_FIELDS),
            })
    return tasks


def _benchmark_worker(task):
    started, pid = time.monotonic(), os.getpid()
    cid = task["case_id"]
    try:
        from puckworks.models.brewer2026 import lb_reference
        mask, meta = vf.build_fixture(task["S"], bridge=None, connected=False, variant="mirror")
        exact = vf.forcing_exact(task["S"], task["forcing_level"])
        g = float(exact)
        result = lb_reference.solve(
            mask, g=g, tau_plus=task["tau_plus"], min_steps=task["min_steps"],
            max_steps=task["max_steps"], check=task["check"], rtol=vf.RTOL,
            verbose=False, return_fields=tuple(task["return_fields"]),
        )
        row = {"case_id": task["benchmark_task_id"], "S": task["S"],
               "state": "reference_blocked", "variant": "mirror"}
        scientific = driver._fixture_scientific(result, mask, meta, g, row)
        compact = {"S": task["S"], "steps": int(result["steps"]),
                   "scientific_payload_sha256": vf.record_hash(scientific),
                   "voxel_count": int(mask.size)}
        return engine.success_result(cid, pid, started, time.monotonic(), compact)
    except BaseException as exc:
        if isinstance(exc, (KeyboardInterrupt, SystemExit)):
            raise
        return engine.failure_result(cid, pid, started, time.monotonic(), exc)


def validate_benchmark_result(result, task):
    engine.validate_worker_result(result, task["case_id"], {task["case_id"]})
    if not result["success"]:
        raise RuntimeError("benchmark worker failed: %r" % result["failure"])
    payload = result["payload"]
    if not isinstance(payload, dict) or set(payload) != {
            "S", "steps", "scientific_payload_sha256", "voxel_count"}:
        raise RuntimeError("malformed benchmark payload")
    if payload["S"] != task["S"] or payload["steps"] != FIXED_STEPS:
        raise RuntimeError("benchmark worker returned the wrong template or step count")
    digest = payload["scientific_payload_sha256"]
    if not isinstance(digest, str) or len(digest) != 64:
        raise RuntimeError("benchmark payload hash is malformed")
    return result


def run_benchmark(jobs, output):
    if jobs not in VALID_BENCHMARK_JOBS:
        raise ValueError("benchmark --jobs must be one of %r" % (VALID_BENCHMARK_JOBS,))
    out = Path(output)
    if not out.is_absolute():
        raise ValueError("benchmark output must be an absolute external path")
    repo = Path(__file__).resolve().parents[3]
    resolved = out.resolve(strict=False)
    if resolved == repo or repo in resolved.parents:
        raise ValueError("benchmark output may not be inside the repository")
    if out.exists():
        raise FileExistsError("benchmark output already exists: %s" % out)
    tasks = benchmark_corpus()
    started = time.monotonic()
    results = []
    if jobs == 1:
        for task in tasks:
            results.append(validate_benchmark_result(_benchmark_worker(task), task))
    else:
        with engine.DeterministicWavePool(jobs, _benchmark_worker) as pool:
            for i in range(0, len(tasks), jobs):
                wave_tasks = tasks[i:i + jobs]
                wave_results = pool.run_wave(wave_tasks)
                results.extend(validate_benchmark_result(r, t)
                               for r, t in zip(wave_results, wave_tasks))
    elapsed = time.monotonic() - started
    hashes = {}
    for task, result in zip(tasks, results):
        hashes.setdefault(task["S"], set()).add(result["payload"]["scientific_payload_sha256"])
    if any(len(v) != 1 for v in hashes.values()):
        raise RuntimeError("repeated identical benchmark tasks produced unequal payload hashes")
    summary = {
        "schema_version": BENCHMARK_SCHEMA_VERSION, "label": BENCHMARK_LABEL,
        "execution_engine": engine.execution_engine_identity(jobs), "jobs": jobs,
        "task_count": len(tasks), "S2_task_count": 16, "S3_task_count": 16,
        "fixed_steps_per_task": FIXED_STEPS, "wall_seconds": elapsed,
        "payload_hash_by_S": {"S%d" % k: next(iter(v)) for k, v in sorted(hashes.items())},
        "worker_failures": 0, "production_artifacts_created": 0,
        "tasks": [{"benchmark_task_id": t["benchmark_task_id"], **r["payload"]}
                  for t, r in zip(tasks, results)],
    }
    out.mkdir(parents=True)
    (out / "benchmark_summary.json").write_text(vf.canonical_json(summary) + "\n")
    (out / "benchmark_report.md").write_text(
        "# RP-D-LC-001b reference scaling benchmark\n\n"
        "`%s`\n\nJobs: %d  \nTasks: 32  \nWall seconds: %.6f\n"
        % (BENCHMARK_LABEL, jobs, elapsed))
    return summary


def main(argv=None):
    ap = argparse.ArgumentParser(description=BENCHMARK_LABEL)
    ap.add_argument("--jobs", required=True, type=int, choices=VALID_BENCHMARK_JOBS)
    ap.add_argument("--output", required=True)
    args = ap.parse_args(argv)
    print(json.dumps(run_benchmark(args.jobs, args.output), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
