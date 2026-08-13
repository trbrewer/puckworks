"""Process-level reference execution engine for RP-D-LC-001b.

This module schedules independent existing rows.  It owns no scientific policy and performs no
durable write: readiness and result consumption are parent callbacks.  Production uses the same
strict wave primitive as the performance-only harness and private deterministic tests.
"""

from __future__ import annotations

from concurrent.futures import ProcessPoolExecutor, as_completed
import math
import multiprocessing
import os

REFERENCE_EXECUTION_ENGINE_VERSION = "PROCESS_POOL_V1"
DEFAULT_REFERENCE_WORKERS = 1
MAX_REFERENCE_WORKERS = 32
MULTIPROCESSING_START_METHOD = "spawn"
SCHEDULER_POLICY = "CANONICAL_BOUNDED_WAVES_V1"
WORKER_RESULT_SCHEMA_VERSION = 1
EXECUTION_MODES = ("SERIAL_REFERENCE", "PROCESS_POOL_REFERENCE")
THREAD_LIMIT_ENV = (
    "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS", "BLIS_NUM_THREADS",
)


def validate_jobs(jobs):
    if isinstance(jobs, bool) or not isinstance(jobs, int):
        raise ValueError("--jobs must be an integer from 1 through 32")
    if not 1 <= jobs <= MAX_REFERENCE_WORKERS:
        raise ValueError("--jobs %r is unsupported; valid reference worker counts are 1..32"
                         % (jobs,))
    return jobs


def execution_engine_identity(jobs):
    jobs = validate_jobs(jobs)
    return {
        "version": REFERENCE_EXECUTION_ENGINE_VERSION,
        "execution_mode": ("SERIAL_REFERENCE" if jobs == 1 else "PROCESS_POOL_REFERENCE"),
        "requested_workers": jobs,
        "multiprocessing_start_method": MULTIPROCESSING_START_METHOD,
        "worker_thread_limit_policy": {name: "1" for name in THREAD_LIMIT_ENV},
        "scheduler_policy": SCHEDULER_POLICY,
    }


def apply_worker_thread_limits():
    """Apply process-local limits; never edits a shell or persistent configuration."""
    for name in THREAD_LIMIT_ENV:
        os.environ[name] = "1"


def worker_initializer():
    # The parent also sets these before spawn so NumPy imports in child bootstrap see the limits.
    apply_worker_thread_limits()


def success_result(case_id, worker_pid, started, ended, payload):
    return {
        "schema_version": WORKER_RESULT_SCHEMA_VERSION,
        "case_id": case_id,
        "worker_pid": worker_pid,
        "execution_mode": "PROCESS_POOL_REFERENCE",
        "worker_started_monotonic": started,
        "worker_ended_monotonic": ended,
        "success": True,
        "payload": payload,
        "failure": None,
    }


def failure_result(case_id, worker_pid, started, ended, exc):
    return {
        "schema_version": WORKER_RESULT_SCHEMA_VERSION,
        "case_id": case_id,
        "worker_pid": worker_pid,
        "execution_mode": "PROCESS_POOL_REFERENCE",
        "worker_started_monotonic": started,
        "worker_ended_monotonic": ended,
        "success": False,
        "payload": None,
        "failure": {"type": type(exc).__name__, "message": str(exc)},
    }


def validate_worker_result(result, expected_case_id, dispatched_ids):
    fields = {
        "schema_version", "case_id", "worker_pid", "execution_mode",
        "worker_started_monotonic", "worker_ended_monotonic", "success", "payload", "failure",
    }
    if not isinstance(result, dict) or set(result) != fields:
        raise RuntimeError("malformed process-pool worker result")
    if result["schema_version"] != WORKER_RESULT_SCHEMA_VERSION:
        raise RuntimeError("worker result has an unsupported schema version")
    cid = result["case_id"]
    if cid != expected_case_id or cid not in dispatched_ids:
        raise RuntimeError("worker returned case_id %r for dispatched row %r" %
                           (cid, expected_case_id))
    if isinstance(result["worker_pid"], bool) or not isinstance(result["worker_pid"], int):
        raise RuntimeError("worker result carries an invalid PID")
    if result["execution_mode"] != "PROCESS_POOL_REFERENCE":
        raise RuntimeError("worker result carries the wrong execution mode")
    start, end = result["worker_started_monotonic"], result["worker_ended_monotonic"]
    if not all(isinstance(x, (int, float)) and math.isfinite(x) for x in (start, end)):
        raise RuntimeError("worker timing is non-finite")
    if end < start:
        raise RuntimeError("worker end time precedes start time")
    if not isinstance(result["success"], bool):
        raise RuntimeError("worker success is not boolean")
    if result["success"]:
        if result["failure"] is not None:
            raise RuntimeError("successful worker result carries a failure")
    elif not isinstance(result["failure"], dict):
        raise RuntimeError("failed worker result carries no structured failure")
    return result


class DeterministicWavePool:
    """One spawn pool per phase, with complete-wave barriers and canonical return order."""

    def __init__(self, jobs, worker):
        self.jobs = validate_jobs(jobs)
        if self.jobs == 1:
            raise ValueError("the process-pool path requires jobs > 1")
        self.worker = worker
        self._pool = None
        self.waves_dispatched = 0
        self.worker_calls = 0

    def __enter__(self):
        apply_worker_thread_limits()
        context = multiprocessing.get_context(MULTIPROCESSING_START_METHOD)
        self._pool = ProcessPoolExecutor(
            max_workers=self.jobs, mp_context=context, initializer=worker_initializer,
        )
        return self

    def run_wave(self, canonical_tasks):
        tasks = list(canonical_tasks)
        if not tasks or len(tasks) > self.jobs:
            raise ValueError("a deterministic wave must contain 1..jobs tasks")
        ids = [task["case_id"] for task in tasks]
        if len(ids) != len(set(ids)):
            raise RuntimeError("a wave contains a duplicate case ID")
        dispatched = set(ids)
        futures = {self._pool.submit(self.worker, task): task["case_id"] for task in tasks}
        self.waves_dispatched += 1
        self.worker_calls += len(tasks)
        returned = {}
        try:
            for future in as_completed(futures):
                expected = futures[future]
                result = validate_worker_result(future.result(), expected, dispatched)
                if result["case_id"] in returned:
                    raise RuntimeError("duplicate worker result for %r" % result["case_id"])
                returned[result["case_id"]] = result
        except KeyboardInterrupt:
            for future in futures:
                future.cancel()
            self._pool.shutdown(wait=True, cancel_futures=True)
            self._pool = None
            raise
        if set(returned) != dispatched:
            raise RuntimeError("a deterministic wave returned an incomplete result set")
        return [returned[cid] for cid in ids]

    def __exit__(self, exc_type, exc, tb):
        if self._pool is not None:
            self._pool.shutdown(wait=True, cancel_futures=exc_type is not None)
        return False


def deterministic_waves(canonical_tasks, jobs, dependency_ids=None):
    """Pure wave planner used by tests and the parent readiness loop.

    Dependencies are case-ID sets. A complete ready set is ordered by canonical task order, then
    its first ``jobs`` entries form the next wave. Completion is simulated only for planning.
    """
    jobs = validate_jobs(jobs)
    tasks = list(canonical_tasks)
    deps = dict(dependency_ids or {})
    done = set()
    pending = list(tasks)
    waves = []
    while pending:
        ready = [t for t in pending if set(deps.get(t["case_id"], ())) <= done]
        if not ready:
            raise RuntimeError("row dependency graph is blocked or cyclic")
        wave = ready[:jobs]
        waves.append([t["case_id"] for t in wave])
        selected = {t["case_id"] for t in wave}
        done.update(selected)
        pending = [t for t in pending if t["case_id"] not in selected]
    return waves
