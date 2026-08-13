"""Focused Stage-A tests. No test calls the real reference LB kernel."""

import os
import time

import numpy as np
import pytest

from puckworks.analysis import rp_d_lc_001b_virtual_fixture as vf
from puckworks.validation.slow import rp_d_lc_001b as drv
from puckworks.validation.slow import rp_d_lc_001b_process_pool as eng
from puckworks.validation.slow import rp_d_lc_001b_scaling_benchmark as bench


def arithmetic_worker(task):
    started = time.monotonic()
    if task.get("delay"):
        time.sleep(task["delay"])
    return eng.success_result(task["case_id"], os.getpid(), started, time.monotonic(),
                              {"value": task["value"] * 2})


def failed_worker(task):
    started = time.monotonic()
    return eng.failure_result(task["case_id"], os.getpid(), started, time.monotonic(),
                              RuntimeError("controlled"))


def rows():
    return [
        {"case_id": "normal", "audit_of_case_id": None, "replicate_of_case_id": None},
        {"case_id": "independent", "audit_of_case_id": None, "replicate_of_case_id": None},
        {"case_id": "audit", "audit_of_case_id": "normal", "replicate_of_case_id": None},
        {"case_id": "replicate", "audit_of_case_id": None,
         "replicate_of_case_id": "independent"},
    ]


def test_jobs_one_preserves_serial_path_and_creates_no_pool(monkeypatch, tmp_path):
    seen = []
    monkeypatch.setattr(drv, "require_execution_authorisation", lambda *a, **k: {"stage": "P0"})
    monkeypatch.setattr(vf, "validate_production_runs_dir",
                        lambda p, **k: tmp_path / "external")
    monkeypatch.setattr(drv, "_orchestrate", lambda *a: seen.append("serial") or {})
    monkeypatch.setattr(drv, "_orchestrate_parallel",
                        lambda *a: (_ for _ in ()).throw(AssertionError("pool path reached")))
    drv.execute_phase("P0", tmp_path / "external", jobs=1)
    assert seen == ["serial"]


@pytest.mark.parametrize("jobs", [2, 4])
def test_deterministic_waves_wait_for_audit_and_replicate_bases(jobs):
    tasks = rows()
    dependencies = {r["case_id"]: drv._row_dependency_ids(r) for r in tasks}
    waves = eng.deterministic_waves(tasks, jobs, dependencies)
    positions = {cid: wi for wi, wave in enumerate(waves) for cid in wave}
    assert positions["audit"] > positions["normal"]
    assert positions["replicate"] > positions["independent"]
    assert all(len(w) <= jobs for w in waves)


def test_real_spawn_pool_returns_canonical_order_despite_out_of_order_completion():
    tasks = [{"case_id": "a", "value": 1, "delay": 0.04},
             {"case_id": "b", "value": 2, "delay": 0.0}]
    with eng.DeterministicWavePool(2, arithmetic_worker) as pool:
        result = pool.run_wave(tasks)
    assert [r["case_id"] for r in result] == ["a", "b"]
    assert [r["payload"]["value"] for r in result] == [2, 4]
    assert pool.worker_calls == 2


def test_parent_only_consumer_is_canonical_and_worker_accounting_exact():
    persisted = []
    result = drv._run_parallel_waves(
        rows(), 2, arithmetic_worker,
        prepare=lambda row: {"case_id": row["case_id"], "value": 3},
        consume=lambda row, worker_result: persisted.append(row["case_id"]) or True,
    )
    assert persisted == ["normal", "independent", "audit", "replicate"]
    counts = result["accounting"]
    assert counts["worker_calls"] == counts["newly_dispatched_rows"] == 4
    assert counts["waves_dispatched"] == 2


def test_resume_reuses_exact_row_without_worker_call():
    persisted = []
    result = drv._run_parallel_waves(
        rows()[:2], 2, arithmetic_worker,
        prepare=lambda row: None if row["case_id"] == "normal" else {
            "case_id": row["case_id"], "value": 2},
        consume=lambda row, worker_result: persisted.append(row["case_id"]) or True,
    )
    assert persisted == ["independent"]
    assert result["accounting"]["reused_rows"] == 1
    assert result["accounting"]["worker_calls"] == 1


def test_current_wave_failure_bounds_overshoot_and_refuses_later_rows():
    result = drv._run_parallel_waves(
        rows(), 2, failed_worker,
        prepare=lambda row: {"case_id": row["case_id"]},
        consume=lambda row, worker_result: worker_result["success"],
    )
    assert result["accounting"]["worker_calls"] == 2
    assert result["refused_after_parallel_stop"] == ["audit", "replicate"]


def test_worker_result_rejects_wrong_id_nonfinite_and_malformed():
    good = eng.success_result("a", 1, 1.0, 2.0, {})
    with pytest.raises(RuntimeError, match="case_id"):
        eng.validate_worker_result(good, "b", {"b"})
    bad = eng.success_result("a", 1, float("nan"), 2.0, {})
    with pytest.raises(RuntimeError, match="non-finite"):
        eng.validate_worker_result(bad, "a", {"a"})
    bad.pop("payload")
    with pytest.raises(RuntimeError, match="malformed"):
        eng.validate_worker_result(bad, "a", {"a"})


def test_execution_engine_identity_binds_workers_mode_spawn_threads_and_policy():
    serial = eng.execution_engine_identity(1)
    parallel = eng.execution_engine_identity(8)
    assert serial["execution_mode"] == "SERIAL_REFERENCE"
    assert parallel["execution_mode"] == "PROCESS_POOL_REFERENCE"
    assert parallel["requested_workers"] == 8
    assert parallel["multiprocessing_start_method"] == "spawn"
    assert set(parallel["worker_thread_limit_policy"].values()) == {"1"}
    assert parallel["scheduler_policy"] == "CANONICAL_BOUNDED_WAVES_V1"


@pytest.mark.parametrize("jobs", [0, 33, -1, True, 1.5])
def test_invalid_jobs_refuse(jobs):
    with pytest.raises(ValueError):
        eng.validate_jobs(jobs)


def test_branch_is_deauthorized_and_p3_p4_hard_refused():
    assert drv.AUTHORISED_SOLVING_PHASES == ()
    assert drv.AUTHORISED_ASSEMBLY_PHASES == ()
    assert drv.POST_FREEZE_EXECUTOR_READY is False
    for phase in ("P3", "P4"):
        with pytest.raises(drv.PostFreezeExecutorNotReady):
            drv.solve(None, 0.0, phase)


def test_p2b_jobs_greater_than_one_refuses_before_assembly(monkeypatch, tmp_path):
    monkeypatch.setattr(vf, "validate_production_runs_dir", lambda p, **k: tmp_path)
    monkeypatch.setattr(vf, "assemble_p2b_from_runs",
                        lambda *a, **k: (_ for _ in ()).throw(AssertionError("assembled")))
    with pytest.raises(ValueError, match="arithmetic"):
        drv.execute_phase("P2b", tmp_path, jobs=2)


def test_public_production_api_exposes_no_provider_or_authority_override():
    import inspect
    assert list(inspect.signature(drv.execute_phase).parameters) == [
        "phase", "runs_dir", "backend", "jobs"]
    assert list(inspect.signature(drv.run_phase).parameters) == [
        "mode", "out_dir", "backend", "runs_dir", "jobs"]


def test_benchmark_corpus_exact_and_has_no_production_case_id():
    corpus = bench.benchmark_corpus()
    assert len(corpus) == 32
    assert sum(t["S"] == 2 for t in corpus) == 16
    assert sum(t["S"] == 3 for t in corpus) == 16
    assert all(t["min_steps"] == t["max_steps"] == 600 for t in corpus)
    assert all(t["check"] == 200 and t["tau_plus"] == 2.0 for t in corpus)
    assert all("production_case_id" not in t and not t["case_id"].startswith("P0.")
               for t in corpus)
    assert bench.VALID_BENCHMARK_JOBS == (1, 4, 8, 16, 32)


def test_benchmark_result_contract_rejects_malformed_payload():
    task = bench.benchmark_corpus()[0]
    result = eng.success_result(task["case_id"], 1, 1.0, 2.0, {"wrong": True})
    with pytest.raises(RuntimeError, match="malformed benchmark"):
        bench.validate_benchmark_result(result, task)


def test_benchmark_worker_uses_p0_extraction_and_identity_free_hash(monkeypatch, tmp_path):
    from puckworks.models.brewer2026 import lb_reference

    real_solve_calls = []
    phases = []
    original_extract = drv._fixture_scientific

    def fake_solve(mask, **kwargs):
        shape = mask.shape
        return {"ux": np.full(shape, 1.0e-6), "rho": np.ones(shape),
                "uy": np.zeros(shape), "uz": np.zeros(shape), "steps": 600}

    def checked_extract(result, mask, meta, g, row):
        phases.append(row["phase"])
        return original_extract(result, mask, meta, g, row)

    monkeypatch.setattr(lb_reference, "solve", fake_solve)
    monkeypatch.setattr(drv, "_fixture_scientific", checked_extract)
    tasks = [dict(bench.benchmark_corpus()[0]), dict(bench.benchmark_corpus()[0])]
    tasks[1]["case_id"] = "benchmark.S2.repeat99"
    tasks[1]["benchmark_task_id"] = "S2_reference_blocked_central_99"
    results = [bench.validate_benchmark_result(bench._benchmark_worker(task), task)
               for task in tasks]
    hashes = [result["payload"]["scientific_payload_sha256"] for result in results]
    assert phases == ["P0", "P0"]
    assert hashes[0] == hashes[1]

    mask, meta = vf.build_fixture(2, bridge=None, connected=False, variant="mirror")
    exact = vf.forcing_exact(2, "central")
    result = fake_solve(mask)
    row = {"case_id": tasks[0]["benchmark_task_id"], "phase": "P0", "S": 2,
           "state": "reference_blocked", "variant": "mirror"}
    scientific = original_extract(result, mask, meta, float(exact), row)
    changed = dict(scientific)
    changed["Q_volume"] = scientific["Q_volume"] + 1.0
    assert bench._benchmark_scientific_payload_hash(tasks[0], scientific,
                                                    meta["mask_sha256"]) != \
        bench._benchmark_scientific_payload_hash(tasks[0], changed, meta["mask_sha256"])
    assert bench._benchmark_scientific_payload_hash(tasks[0], scientific,
                                                    meta["mask_sha256"]) != \
        bench._benchmark_scientific_payload_hash(bench.benchmark_corpus()[16], scientific,
                                                 meta["mask_sha256"])
    assert real_solve_calls == []
    assert list(tmp_path.iterdir()) == []


def test_jobs_one_benchmark_entry_reasserts_thread_limits(monkeypatch, tmp_path):
    for name in eng.THREAD_LIMIT_ENV:
        monkeypatch.setenv(name, "not-one")
    with pytest.raises(FileExistsError):
        bench.run_benchmark(1, tmp_path)
    assert {name: os.environ[name] for name in eng.THREAD_LIMIT_ENV} == {
        name: "1" for name in eng.THREAD_LIMIT_ENV}


def test_reference_solver_was_not_called(monkeypatch):
    from puckworks.models.brewer2026 import lb_reference
    calls = []
    monkeypatch.setattr(lb_reference, "solve", lambda *a, **k: calls.append(1))
    eng.deterministic_waves(rows(), 2,
                            {r["case_id"]: drv._row_dependency_ids(r) for r in rows()})
    assert calls == []
