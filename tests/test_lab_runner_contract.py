"""Native reference runner contract v2 (PV-19B Phase 4, #70).

Offline + deterministic. Guards single-sourcing of the reference-summary producers (the gate and the
runner consume the same computation), the single authoritative Foster first-drip threshold constant (no
duplicated literal in the runner), full producer precision preserved (display rounding is separate and
never before hashing), the complete failure result schema with a sanitized path-free error, and the
finite execution-state vocabulary.
"""
import ast

from puckworks.models.foster2025 import infiltration as inf
from puckworks.product import lab_reference_producers as P
from puckworks.product import lab_runners as lr
from puckworks.validation import gates as G


# ── single-sourced threshold ────────────────────────────────────────────────────────
def test_first_drip_threshold_is_a_single_named_constant():
    assert inf.FIRST_DRIP_THRESHOLD_G == 0.5
    # the gate consumes the shared helper (not a private argmax literal)
    gsrc = open(G.__file__).read()
    assert "observed_first_drip_s" in gsrc
    # the runner module must not carry the threshold (or the band) as an executable literal
    tree = ast.parse(open(lr.__file__).read())
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, float):
            assert node.value not in (0.5, 0.7, 1.2), f"runner carries a threshold/band literal {node.value}"


def test_no_false_first_drip_crossing_in_the_model_helper():
    assert inf.observed_first_drip_s([0, 1, 2], [0.0, 0.1, 0.2]) is None       # never t[0]
    assert inf.observed_first_drip_s([0, 1, 2], [0.0, 0.6, 0.7]) == 1.0


# ── the gate and the runner consume the SAME summary computation ────────────────────
def test_gate_and_runner_agree_because_they_share_the_producer():
    # foster: the summary's observed drip + bracket verdict match the gate's, to full precision
    s = P.foster_first_drip_summary()
    gate = G.gate_infiltration_triangle()
    assert s["values"]["observed_first_drip_s"] == gate["observed_s"]
    within = s["values"]["observation_within_bracket"]
    assert within == gate["passed"]
    # wadsworth: the summary's gm ratio rounds to the gate's reported ratio
    sw = P.wadsworth_collapse_summary()
    gw = G.gate_wadsworth_collapse()
    assert round(sw["values"]["percolation_collapse_gm_ratio"], 3) == gw["geometric_mean_ratio"]


def test_runner_verdict_is_the_gate_verdict_not_a_recompute():
    for cid, gate_name in [("foster2025.infiltration", "gate_infiltration_triangle"),
                           ("wadsworth2026.permeability", "gate_wadsworth_collapse"),
                           ("waszkiewicz2025.poroelastic", "gate_waszkiewicz_static_refit")]:
        r = lr.execute_runner(cid)
        assert r["gate_authority"]["gate"] == gate_name
        assert r["gate_authority"]["verdict"]["passed"] == bool(getattr(G, gate_name)()["passed"])


# ── full precision preserved; display rounding separate ─────────────────────────────
def test_full_precision_stored_and_display_value_is_separate():
    r = lr.execute_runner("wadsworth2026.permeability")
    gm = {o["name"]: o for o in r["outputs"]}["percolation_collapse_gm_ratio"]
    summary = P.wadsworth_collapse_summary()["values"]["percolation_collapse_gm_ratio"]
    assert gm["value"] == summary                       # exact producer precision, not pre-rounded
    assert gm["display_value"] == round(summary, 6)     # a separate display companion
    # the scientific hash covers the full-precision value
    assert r["scientific_payload_hash"]


# ── complete failure schema + sanitized error ──────────────────────────────────────
def test_failure_result_has_the_full_schema_and_a_sanitized_error(monkeypatch):
    spec, _ = lr.RUNNERS["wadsworth2026.permeability"]

    def boom():
        raise FileNotFoundError(2, "No such file or directory: '/Users/secret/private/data.json'")
    monkeypatch.setitem(lr.RUNNERS, "wadsworth2026.permeability", (spec, boom))
    r = lr.execute_runner("wadsworth2026.permeability")
    assert r["status"] == "FAILED" and r["execution_state"] == "FAILED"
    assert r["error_code"] == "FileNotFoundError"
    # required fields present even on failure
    for k in ("component_id", "runner_id", "native_inputs", "outputs", "evidence",
              "code_rights_state", "output_publication_allowed"):
        assert k in r
    # no filesystem path leaks into the published error
    assert "/Users/secret" not in r["error"] and "<path>" in r["error"]


def test_execution_state_vocabulary_is_finite_and_consistent():
    r = lr.execute_runner("foster2025.infiltration")
    assert r["execution_state"] == "EXECUTED" and r["execution_state"] in lr.EXECUTION_STATES
    assert "FAILED" in lr.EXECUTION_STATES and "RIGHTS_BLOCKED" in lr.EXECUTION_STATES


def test_runner_result_carries_centralized_code_data_output_rights():
    r = lr.execute_runner("waszkiewicz2025.poroelastic")
    from puckworks import rights
    rec = rights.rights_record("waszkiewicz2025.poroelastic")
    assert r["code_rights_state"] == rec.code_rights_state
    assert r["output_redistribution_state"] == rec.output_redistribution_state
    # outputs not cleared for public redistribution are flagged (NOT_REVIEWED today)
    assert r["output_publication_allowed"] is False
