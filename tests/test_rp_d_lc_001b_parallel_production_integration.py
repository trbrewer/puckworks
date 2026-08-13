"""Focused official-parent integration tests. The real reference solver is never called."""

import json
import os
import time

import numpy as np
import pytest

from puckworks.analysis import rp_d_lc_001b_virtual_fixture as vf
from puckworks.validation.slow import rp_d_lc_001b as drv
from puckworks.validation.slow import rp_d_lc_001b_process_pool as eng


def fake_result(task):
    row = task["row"]
    mask, _meta, _kind = drv.resolve_row(row)
    ux = np.zeros(mask.shape)
    for x in range(mask.shape[0]):
        fluid = ~mask[x]
        if fluid.any():
            ux[x][fluid] = 1.0 / int(fluid.sum())
    zero = np.zeros(mask.shape)
    steps = 3000 if task.get("audit") is None else task["audit"]["target_steps"]
    return {"ux": ux, "uy": zero.copy(), "uz": zero.copy(),
            "rho": np.ones(mask.shape), "steps": steps}


def fake_worker(task):
    started = time.monotonic()
    return eng.success_result(task["case_id"], os.getpid(), started, time.monotonic(),
                              fake_result(task))


def fake_provider(mask, g, phase, row, tau=None, audit=None, backend="reference"):
    return fake_result({"row": row, "audit": audit})


class InlineWavePool:
    """Private deterministic pool seam: returns reversed completion order to the engine."""

    instances = []

    def __init__(self, jobs, worker):
        self.jobs, self.worker = jobs, worker
        self.worker_calls = 0
        self.dispatched = []
        self.__class__.instances.append(self)

    def __enter__(self):
        return self

    def run_wave(self, tasks):
        self.dispatched.append([t["case_id"] for t in tasks])
        self.worker_calls += len(tasks)
        return [self.worker(task) for task in reversed(tasks)][::-1]

    def __exit__(self, *args):
        return False


def two_row_p0():
    rows = vf.execution_matrix()["rows"]
    audit = next(r for r in rows if r["phase"] == "P0" and r.get("audit_of_case_id"))
    base = next(r for r in rows if r["case_id"] == audit["audit_of_case_id"])
    return [base, audit]


def validated_predecessor_stub(row, status="NORMAL_CONVERGED"):
    return {"case_id": row["case_id"], "phase": row["phase"], "row": row,
            "run_mode": row["run_mode"], "completed_steps": 3000, "status": status}


@pytest.fixture()
def small_parallel(monkeypatch):
    rows = two_row_p0()
    matrix = {"rows": rows}
    monkeypatch.setattr(vf, "execution_matrix", lambda: matrix)
    monkeypatch.setattr(vf, "derive_expected_rows",
                        lambda phase, matrix_rows, predecessor_records=None:
                        (list(rows), {"test_only": True}))
    monkeypatch.setattr(vf, "PHASE_AGGREGATE_SCIENCE", {})
    monkeypatch.setattr(eng, "DeterministicWavePool", InlineWavePool)
    InlineWavePool.instances.clear()
    return rows


def authority(jobs=4):
    return vf._test_only_execution_authority(
        "P0", execution_engine=eng.execution_engine_identity(jobs))


def test_official_parallel_parent_persists_canonically_and_audit_waits(
        small_parallel, tmp_path):
    events = []
    manifest = drv._test_only_execute_parallel(
        "P0", tmp_path, fake_worker, authority(), jobs=4, progress=events.append)
    rows = small_parallel
    assert manifest["terminal_status"] == "PHASE_COMPLETE"
    assert [e["case_id"] for e in manifest["completed"]] == [r["case_id"] for r in rows]
    pool = InlineWavePool.instances[-1]
    assert pool.dispatched == [[rows[0]["case_id"]], [rows[1]["case_id"]]]
    assert manifest["execution_counts"]["n_worker_calls"] == 2
    assert manifest["execution_counts"]["n_waves"] == 2
    assert len(events) == 2 and [e["wave_index"] for e in events] == [1, 2]
    assert all("elapsed_wave_seconds" in event for event in events)
    assert "RP_D_LC_001B_PARALLEL_PROGRESS" not in json.dumps(manifest)
    normal, _ = vf.read_case_record(tmp_path, rows[0]["case_id"])
    audit, _ = vf.read_case_record(tmp_path, rows[1]["case_id"])
    assert normal["status"] == "NORMAL_CONVERGED"
    assert audit["row"]["audit_of_case_id"] == normal["case_id"]
    assert audit["audit"]["base_record_sha256"] == vf.record_hash(normal)
    assert audit["completed_steps"] == audit["audit"]["target_steps"]


def test_exact_parallel_resume_reuses_records_with_zero_worker_calls(
        small_parallel, tmp_path):
    first = drv._test_only_execute_parallel(
        "P0", tmp_path, fake_worker, authority(), jobs=4, progress=lambda event: None)
    (tmp_path / "manifest_P0.json").unlink()
    InlineWavePool.instances.clear()
    again = drv._test_only_execute_parallel(
        "P0", tmp_path, fake_worker, authority(), jobs=4, progress=lambda event: None)
    assert again["execution_counts"]["n_worker_calls"] == 0
    assert again["execution_counts"]["n_reused_case_records"] == 2
    assert InlineWavePool.instances[-1].worker_calls == 0
    assert [e["record_sha256"] for e in again["completed"]] == [
        e["record_sha256"] for e in first["completed"]]


def test_frozen_p1b_cross_phase_dependencies_preflight_and_seed(monkeypatch):
    rows = vf.execution_matrix()["rows"]
    p1b = [row for row in rows if row["phase"] == "P1b"]
    p1b_ids = {row["case_id"] for row in p1b}
    external_pairs = [(row, row["audit_of_case_id"]) for row in p1b
                      if row.get("audit_of_case_id") not in (None, *p1b_ids)]
    assert len(external_pairs) == 48
    assert {next(base["phase"] for base in rows if base["case_id"] == dependency)
            for _row, dependency in external_pairs} == {"P1a"}
    by_id = {row["case_id"]: row for row in rows}
    predecessors = {dependency: validated_predecessor_stub(by_id[dependency])
                    for _row, dependency in external_pairs}
    seeded = drv._parallel_dependency_preflight("P1b", p1b, rows, predecessors)
    assert set(seeded) == set(predecessors)
    assert all(row["audit_of_case_id"] in p1b_ids for row in p1b
               if row.get("audit_of_case_id") and row["forcing_level"] in ("low", "high"))


def test_missing_p1b_predecessor_refuses_before_pool_or_authority(monkeypatch, tmp_path):
    rows = vf.execution_matrix()["rows"]
    audit = next(row for row in rows if row["phase"] == "P1b"
                 and row.get("audit_of_case_id")
                 and next(base for base in rows
                          if base["case_id"] == row["audit_of_case_id"])["phase"] == "P1a")
    base = next(row for row in rows if row["case_id"] == audit["audit_of_case_id"])
    monkeypatch.setattr(vf, "execution_matrix", lambda: {"rows": [base, audit]})
    monkeypatch.setattr(vf, "derive_expected_rows",
                        lambda *args, **kwargs: ([audit], {"test_only": True}))
    monkeypatch.setattr(eng, "DeterministicWavePool", InlineWavePool)
    InlineWavePool.instances.clear()
    auth = vf._test_only_execution_authority(
        "P1b", execution_engine=eng.execution_engine_identity(4))
    with pytest.raises(RuntimeError, match=(
            "phase P1b dependent .* requires external base .* predecessor phase P1a.*missing")):
        drv._test_only_execute_parallel(
            "P1b", tmp_path, fake_worker, auth, jobs=4, records={},
            progress=lambda event: None)
    assert not InlineWavePool.instances
    assert not (tmp_path / "execution_authority_P1b.json").exists()


@pytest.mark.parametrize("mutation", ["failed", "refused", "envelope", "incompatible"])
def test_invalid_external_predecessor_cannot_seed_readiness(mutation):
    rows = vf.execution_matrix()["rows"]
    audit = next(row for row in rows if row["phase"] == "P1b"
                 and row.get("audit_of_case_id")
                 and next(base for base in rows
                          if base["case_id"] == row["audit_of_case_id"])["phase"] == "P1a")
    base = next(row for row in rows if row["case_id"] == audit["audit_of_case_id"])
    rec = validated_predecessor_stub(base)
    if mutation == "failed":
        rec["status"] = "NORMAL_UNCONVERGED"
    elif mutation == "refused":
        rec["status"] = "REFUSED_AFTER_PHASE_STOP"
    elif mutation == "envelope":
        rec = {"case_id": base["case_id"], "phase": base["phase"],
               "artifact_kind": "DIAGNOSTIC_FAILURE_ENVELOPE"}
    else:
        rec["row"] = dict(base, forcing_repr="incompatible")
    with pytest.raises(RuntimeError, match="not a completed compatible record|incompatible"):
        drv._parallel_dependency_preflight(
            "P1b", [audit], rows, {base["case_id"]: rec})


def test_exact_reused_stopping_record_refuses_later_rows_without_worker_call(
        monkeypatch, tmp_path):
    rows = [row for row in vf.execution_matrix()["rows"]
            if row["phase"] == "P0" and not drv._row_dependency_ids(row)][:2]
    monkeypatch.setattr(vf, "execution_matrix", lambda: {"rows": rows})
    monkeypatch.setattr(vf, "derive_expected_rows",
                        lambda *args, **kwargs: (list(rows), {"test_only": True}))
    monkeypatch.setattr(vf, "PHASE_AGGREGATE_SCIENCE", {})
    monkeypatch.setattr(eng, "DeterministicWavePool", InlineWavePool)
    InlineWavePool.instances.clear()

    def unconverged_worker(task):
        result = fake_result(task)
        result["steps"] = vf.MAX_STEPS
        now = time.monotonic()
        return eng.success_result(task["case_id"], os.getpid(), now, now, result)

    auth = authority(1)
    first = drv._test_only_execute_parallel(
        "P0", tmp_path, unconverged_worker, auth, jobs=1, progress=lambda event: None)
    assert first["terminal_status"] == "PHASE_STOPPED_UNCONVERGED"
    assert first["execution_counts"]["n_worker_calls"] == 1
    (tmp_path / "manifest_P0.json").unlink()
    InlineWavePool.instances.clear()
    resumed = drv._test_only_execute_parallel(
        "P0", tmp_path, fake_worker, auth, jobs=1, progress=lambda event: None)
    assert resumed["terminal_status"] == "PHASE_STOPPED_UNCONVERGED"
    assert resumed["terminal_stop_reason"] == "NORMAL_UNCONVERGED"
    assert resumed["execution_counts"]["n_worker_calls"] == 0
    assert resumed["execution_counts"]["n_reused_case_records"] == 1
    assert [entry["case_id"] for entry in resumed["refused"]] == [rows[1]["case_id"]]
    assert InlineWavePool.instances[-1].worker_calls == 0


def test_reused_assurance_verdict_retains_stopping_effect(tmp_path):
    matrix = vf.execution_matrix()["rows"]
    replicate = next(row for row in matrix if row["phase"] == "P0"
                     and vf.row_scientific_role(row) == "EXECUTION_ASSURANCE_REPLICATE")
    path = tmp_path / "exact-reused-assurance.json"
    path.write_text("{}")
    state = {"completed": [], "failed": [], "diagnostic_completed": [],
             "diagnostic_failed": [], "terminal": "PHASE_COMPLETE", "stop_reason": None}
    sci = {"mach": {"pass": False}}
    rec = {"status": "NORMAL_CONVERGED", "run_mode": "NORMAL", "completed_steps": 3000}
    verdict = drv._parallel_record_entry(
        replicate, rec, path, "REUSED_EXACT_MATCH", sci, None, state)
    assert verdict["scientific_role"] == "EXECUTION_ASSURANCE_REPLICATE"
    assert verdict["effect"] == "STOPS_THE_PHASE"
    assert state["terminal"] == "PHASE_STOPPED_INVALID_CASE"


def test_jobs_mismatch_refuses_parallel_resume_before_worker_dispatch(
        small_parallel, tmp_path):
    drv._test_only_execute_parallel(
        "P0", tmp_path, fake_worker, authority(4), jobs=4, progress=lambda event: None)
    (tmp_path / "manifest_P0.json").unlink()
    InlineWavePool.instances.clear()
    with pytest.raises((vf.ResumeMismatch, vf.ExecutionAuthorityError, ValueError)):
        drv._test_only_execute_parallel(
            "P0", tmp_path, fake_worker, authority(8), jobs=8,
            progress=lambda event: None)
    assert not InlineWavePool.instances or InlineWavePool.instances[-1].worker_calls == 0


def test_public_safety_and_no_production_override(tmp_path):
    import inspect
    assert drv.AUTHORISED_SOLVING_PHASES == ()
    assert drv.AUTHORISED_ASSEMBLY_PHASES == ()
    assert drv.POST_FREEZE_EXECUTOR_READY is False
    assert list(inspect.signature(drv.execute_phase).parameters) == [
        "phase", "runs_dir", "backend", "jobs"]
    with pytest.raises(drv.ExecutionNotAuthorised):
        drv.execute_phase("P0", tmp_path / "never", jobs=4)
    assert not (tmp_path / "never").exists()


def test_serial_and_parallel_official_science_are_equal(small_parallel, tmp_path):
    serial_dir, parallel_dir = tmp_path / "serial", tmp_path / "parallel"
    serial_auth = vf._test_only_execution_authority(
        "P0", execution_engine=eng.execution_engine_identity(1))
    serial = drv._test_only_execute("P0", serial_dir, fake_provider, serial_auth)
    parallel = drv._test_only_execute_parallel(
        "P0", parallel_dir, fake_worker, authority(), jobs=4, progress=lambda event: None)
    for row in small_parallel:
        a, _ = vf.read_case_record(serial_dir, row["case_id"])
        b, _ = vf.read_case_record(parallel_dir, row["case_id"])
        for field in ("case_id", "row", "geometry", "scientific", "status"):
            assert a[field] == b[field]
        if row.get("audit_of_case_id"):
            # The audit's base file hash legitimately differs because the base official record
            # binds serial versus process-pool execution authority. All scientific lineage and
            # target fields remain exact.
            assert {k: v for k, v in a["audit"].items() if k != "base_record_sha256"} == {
                k: v for k, v in b["audit"].items() if k != "base_record_sha256"}
            assert a["solver_config"]["min_steps"] == b["solver_config"]["min_steps"]
            assert a["solver_config"]["max_steps"] == b["solver_config"]["max_steps"]
        else:
            assert a["audit"] == b["audit"]
            assert a["scientific_payload_sha256"] == b["scientific_payload_sha256"]
            assert a["solver_config"] == b["solver_config"]
    for field in ("phase_universe_case_ids", "completed", "failed", "refused",
                  "diagnostic_completed", "diagnostic_failed", "adaptive", "phase_science",
                  "replicates", "terminal_status", "terminal_stop_reason"):
        if field == "completed":
            # File hashes legitimately bind different execution authorities; ordering, status,
            # roles, reasons and scientific records above are exact.
            assert [e["case_id"] for e in serial[field]] == [e["case_id"]
                                                               for e in parallel[field]]
        else:
            assert serial[field] == parallel[field]


def test_tau_worker_failure_creates_parent_envelope_and_does_not_stop(monkeypatch, tmp_path):
    rows = vf.execution_matrix()["rows"]
    tau = next(r for r in rows if vf.row_scientific_role(r) ==
               "TAU_RELAXATION_DIAGNOSTIC_NON_ADJUDICATIVE")
    normal = next(r for r in rows if r["phase"] == tau["phase"]
                  and vf.row_scientific_role(r) == "DECISION_BEARING"
                  and not r.get("audit_of_case_id"))
    chosen = [normal, tau] if rows.index(normal) < rows.index(tau) else [tau, normal]
    monkeypatch.setattr(vf, "execution_matrix", lambda: {"rows": chosen})
    monkeypatch.setattr(vf, "derive_expected_rows",
                        lambda *args, **kwargs: (list(chosen), {"test_only": True}))
    monkeypatch.setattr(vf, "PHASE_AGGREGATE_SCIENCE", {})
    monkeypatch.setattr(eng, "DeterministicWavePool", InlineWavePool)

    def worker(task):
        if task["case_id"] == tau["case_id"]:
            now = time.monotonic()
            return eng.failure_result(task["case_id"], os.getpid(), now, now,
                                      RuntimeError("controlled row failure"))
        return fake_worker(task)

    auth = vf._test_only_execution_authority(
        tau["phase"], execution_engine=eng.execution_engine_identity(4))
    man = drv._test_only_execute_parallel(
        tau["phase"], tmp_path, worker, auth, jobs=4, progress=lambda event: None)
    assert man["terminal_status"] == "PHASE_COMPLETE"
    assert [e["case_id"] for e in man["diagnostic_failed"]] == [tau["case_id"]]
    assert man["execution_counts"]["n_new_diagnostic_failure_envelopes"] == 1
    assert not (tmp_path / vf.case_record_filename(tau["case_id"])).exists()
    (tmp_path / ("manifest_%s.json" % tau["phase"])).unlink()
    InlineWavePool.instances.clear()
    resumed = drv._test_only_execute_parallel(
        tau["phase"], tmp_path, worker, auth, jobs=4, progress=lambda event: None)
    assert resumed["terminal_status"] == "PHASE_COMPLETE"
    assert resumed["execution_counts"]["n_worker_calls"] == 0
    assert resumed["execution_counts"]["n_reused_diagnostic_failure_envelopes"] == 1
    assert InlineWavePool.instances[-1].worker_calls == 0


def test_parent_interrupt_writes_no_manifest_and_keeps_authority(monkeypatch, small_parallel,
                                                                 tmp_path):
    class InterruptPool(InlineWavePool):
        def run_wave(self, tasks):
            self.worker_calls += len(tasks)
            raise KeyboardInterrupt

    monkeypatch.setattr(eng, "DeterministicWavePool", InterruptPool)
    with pytest.raises(KeyboardInterrupt):
        drv._test_only_execute_parallel(
            "P0", tmp_path, fake_worker, authority(), jobs=4, progress=lambda event: None)
    assert (tmp_path / "execution_authority_P0.json").exists()
    assert not (tmp_path / "manifest_P0.json").exists()
    assert not list(tmp_path.glob("case_*.json"))
