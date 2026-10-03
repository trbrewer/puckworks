"""Synthetic report-replay failure tests; no qualification trajectories."""
import pickle
from types import SimpleNamespace

import numpy as np
import pytest

from puckworks.analysis.foster2025_postsat import ExecutionLog, require_scalar_support


@pytest.mark.parametrize("receipt,result,accepted", [
    (None, SimpleNamespace(success=True), False),
    (False, SimpleNamespace(success=True), False),
    (True, SimpleNamespace(success=False), False),
    (True, {"success": False}, False),
    (True, {"sol": SimpleNamespace(success=False)}, False),
    (True, {}, False),
    (True, SimpleNamespace(success=True), True),
    (True, {"success": True}, True),
    (True, {"sol": SimpleNamespace(success=True)}, True),
])
def test_cached_replay_requires_receipt_and_result_success(tmp_path, receipt, result, accepted):
    log = ExecutionLog(tmp_path/"execution.jsonl", tmp_path/"cache", reuse=True)
    log.record_execution(dict(event="START", execution=1, name="synthetic", source_sha256=log.source_hash))
    if receipt is not None:
        log.record_execution(dict(event="END", execution=1, name="synthetic", success=receipt))
    (log.cache/"01-synthetic.pickle").write_bytes(pickle.dumps(result))

    def forbidden_solve():
        pytest.fail("replay must never call a trajectory")

    if accepted:
        assert log.successful(log.trajectory("synthetic", forbidden_solve))
    else:
        with pytest.raises(ValueError, match="successful|unsuccessful"):
            log.trajectory("synthetic", forbidden_solve)
    assert len([r for r in log.rows if r["event"] == "START"]) == 1


@pytest.mark.parametrize("change", [
    {"success": False}, {"t": np.array([5., 29.])},
    {"t": np.array([4., 30.])}, {"t": np.array([5., 5.])},
    {"t": np.array([5., np.inf])}, {"y": np.array([[0.002, np.nan]])},
    {"y": np.array([[0.003, 0.004]])}, {"sol": None},
])
def test_partial_or_mismatched_scalar_oracle_is_rejected_before_evaluation(change):
    def forbidden_dense_output(t):
        pytest.fail("support validation must precede dense output")

    result = SimpleNamespace(success=True, t=np.array([5., 30.]),
                             y=np.array([[0.002, 0.004]]), sol=forbidden_dense_output)
    require_scalar_support(result, 5., 30., 0.002, "synthetic")
    result.__dict__.update(change)
    with pytest.raises(ValueError, match="support/initial state"):
        require_scalar_support(result, 5., 30., 0.002, "synthetic")
