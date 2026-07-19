"""Rights-safe Laboratory execution service (accessibility mission Phase 1, #43/#70).

Offline + deterministic. The one service every surface (batch, Colab, Streamlit) uses: it requires an
explicit execution context, runs the rights preflight BEFORE any producer, blocks the whole request on
one blocked selection, and returns a typed blocked result carrying NO scientific output. A genuine
execution exception is NOT a rights denial.
"""
import pytest

from puckworks.product import lab
from puckworks.product import lab_rights_gate as gate
from puckworks.product import lab_runners
from puckworks.product import lab_service as S

LB = "brewer2026.lb_reference"


@pytest.fixture
def spy(monkeypatch):
    """Record preflight + every producer call, in order, to prove preflight-before-producer and count
    producers. `simulate_pull` is the common-scenario (Cameron) producer; `execute_runner` is a native
    reference producer."""
    import puckworks.product as prod
    events = []
    orig_pre = gate.preflight
    monkeypatch.setattr(gate, "preflight",
                        lambda req, ctx: (events.append(("preflight", ctx)), orig_pre(req, ctx))[1])
    orig_sim = prod.simulate_pull
    monkeypatch.setattr(prod, "simulate_pull",
                        lambda *a, **k: (events.append(("lens_producer",)), orig_sim(*a, **k))[1])
    orig_exec = lab_runners.execute_runner
    monkeypatch.setattr(lab_runners, "execute_runner",
                        lambda cid: (events.append(("native_producer", cid)), orig_exec(cid))[1])
    return events


def _lb_only():
    return lab.ScenarioRequest("pv19_named", lens_selection_policy="none",
                               reference_selection_policy="selected", requested_reference_runner_ids=(LB,))


def test_explicit_context_is_required():
    with pytest.raises(ValueError):
        S.execute_lab_request(_lb_only(), execution_context="NOT_A_CONTEXT")
    with pytest.raises(TypeError):
        S.execute_lab_request(_lb_only())          # context is keyword-only + required


def test_allowed_public_artifact_runs_only_selected_producers_after_preflight(spy):
    r = S.execute_lab_request(_lb_only(), execution_context="PUBLIC_ARTIFACT")
    assert r.blocked is False and r.has_science and r.report is not None
    assert r.selected_component_ids == (LB,)
    # preflight is FIRST; the only producer is the one selected native reference; no common lens
    assert spy[0] == ("preflight", "PUBLIC_ARTIFACT")
    assert [e for e in spy if e[0] == "native_producer"] == [("native_producer", LB)]
    assert not any(e[0] == "lens_producer" for e in spy)
    assert r.report["counts"]["common_scenario_producer_invocations"] == 0
    assert r.report["counts"]["executed_native_references"] == 1


def test_blocked_public_request_invokes_zero_producers_and_carries_no_science(spy):
    r = S.execute_lab_request(lab.ScenarioRequest("pv19_named"), execution_context="PUBLIC_ARTIFACT")
    assert r.blocked is True and r.report is None and r.has_science is False
    # preflight ran; NO producer of any kind ran
    assert spy == [("preflight", "PUBLIC_ARTIFACT")]
    # the blocked record carries ONLY the rights decision — no scientific field
    rec = r.blocked_record()
    blob = str(rec)
    for forbidden in ("scientific_payload", "observabl", "executed_reference_results", "trace", "outputs"):
        assert forbidden not in blob
    assert rec["blocked"] is True and rec["execution_context"] == "PUBLIC_ARTIFACT"


def test_blocked_grudeva_private_request_invokes_zero_producers(spy):
    req = lab.ScenarioRequest("pv19_named", lens_selection_policy="none",
                              reference_selection_policy="selected",
                              requested_reference_runner_ids=("grudeva2025.reduced",))
    r = S.execute_lab_request(req, execution_context="LOCAL_PRIVATE")
    assert r.blocked is True and r.report is None          # RIGHTS_BLOCKED blocks even locally
    assert spy == [("preflight", "LOCAL_PRIVATE")]         # zero producers
    assert any("grudeva2025.reduced" in b for b in r.blockers)


def test_local_private_not_reviewed_stays_inspectable_and_runs_selected_producers(spy):
    # default LOCAL_PRIVATE: the primary Cameron lens (NOT_REVIEWED) runs locally + interactive-fast refs
    r = S.execute_lab_request(lab.ScenarioRequest("pv19_named"), execution_context="LOCAL_PRIVATE")
    assert r.blocked is False and r.has_science
    assert spy[0][0] == "preflight"
    assert [e for e in spy if e[0] == "lens_producer"] == [("lens_producer",)]      # exactly one lens
    native = sorted(e[1] for e in spy if e[0] == "native_producer")
    assert native == sorted(lab_runners.INTERACTIVE_FAST)  # exactly the selected interactive-fast refs
    assert r.report["counts"]["common_scenario_producer_invocations"] == 1


def test_selected_native_reference_executes_exactly_once(spy):
    S.execute_lab_request(_lb_only(), execution_context="LOCAL_PRIVATE")
    assert [e for e in spy if e[0] == "native_producer"].count(("native_producer", LB)) == 1


def test_unknown_selected_id_fails_distinctly(spy):
    req = lab.ScenarioRequest("pv19_named", lens_selection_policy="none",
                              reference_selection_policy="selected",
                              requested_reference_runner_ids=("not.a.component",))
    r = S.execute_lab_request(req, execution_context="PUBLIC_ARTIFACT")
    assert r.blocked is True and r.report is None
    assert any("unknown reference id" in b for b in r.blockers)
    assert not any(e[0] in ("lens_producer", "native_producer") for e in spy)


def test_execution_exception_is_not_a_rights_denial(monkeypatch):
    # a genuine producer failure must PROPAGATE as an exception, never masquerade as blocked=True
    def boom(*a, **k):
        raise RuntimeError("simulated execution failure")
    monkeypatch.setattr(lab, "execute_scenario", boom)
    with pytest.raises(RuntimeError, match="simulated execution failure"):
        S.execute_lab_request(_lb_only(), execution_context="LOCAL_PRIVATE")


def test_raise_on_block_raises_typed_blocked_carrying_no_science():
    with pytest.raises(S.LabRequestBlocked) as exc:
        S.execute_lab_request(lab.ScenarioRequest("pv19_named"), execution_context="PUBLIC_ARTIFACT",
                              raise_on_block=True)
    assert exc.value.result.blocked is True and exc.value.result.report is None


def test_hashes_are_deterministic_across_two_service_runs():
    a = S.execute_lab_request(_lb_only(), execution_context="PUBLIC_ARTIFACT")
    b = S.execute_lab_request(_lb_only(), execution_context="PUBLIC_ARTIFACT")
    assert (a.report["integrity"]["scientific_payload_sha256"]
            == b.report["integrity"]["scientific_payload_sha256"])


def test_result_invariants_enforced():
    # a blocked result may not carry a report; an allowed result must
    with pytest.raises(ValueError):
        S.LabRequestResult("PUBLIC_ARTIFACT", blocked=True, rights_preflight={}, selected_component_ids=(),
                           report={"x": 1})
    with pytest.raises(ValueError):
        S.LabRequestResult("LOCAL_PRIVATE", blocked=False, rights_preflight={}, selected_component_ids=(),
                           report=None)
