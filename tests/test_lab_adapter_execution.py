"""Adapter-driven common-scenario lens execution (PV-19B Phase 2, schema v5, #70).

Offline + deterministic. Guards that the Laboratory executes ONLY the selected, ready, in-domain lenses:
the producer is never called for a lens that is not selected, not ready, or domain-blocked; a fake
adapter runs independently of Cameron; one adapter failing never erases another; the executed count
equals the number of producer invocations; scenario preparation calls no producer; and reference
selection resolves COMPONENTS (a registered component with no runner is RUNNER_NOT_IMPLEMENTED, not
"unknown").
"""

import pytest

import puckworks.product as prod
from puckworks.product import lab


@pytest.fixture
def count_producer(monkeypatch):
    """Count real simulate_pull invocations."""
    calls = {"n": 0}
    real = prod.simulate_pull

    def counting(*a, **k):
        calls["n"] += 1
        return real(*a, **k)
    monkeypatch.setattr(prod, "simulate_pull", counting)
    return calls


def _run(**kw):
    ex = lab.execute_scenario(lab.ScenarioRequest("pv19_named", **kw))
    return ex, lab.build_comparison(ex)


# ── scenario preparation calls no producer ──────────────────────────────────────────
def test_prepare_scenario_calls_no_producer(count_producer):
    prepared = lab.prepare_scenario(lab.ScenarioRequest("pv19_named"))
    assert count_producer["n"] == 0
    assert prepared.recipe_obj is not None
    assert "dose_g" in prepared.shared_quantities and prepared.shared_quantities["dose_g"]["unit"] == "g"
    # a PreparedScenario carries no model output
    assert not hasattr(prepared, "pull_run")


# ── selection policy gates execution ────────────────────────────────────────────────
def test_none_policy_runs_no_producer(count_producer):
    ex, r = _run(lens_selection_policy="none")
    assert count_producer["n"] == 0
    assert r["counts"]["executed_common_scenario_lenses"] == 0
    assert r["counts"]["common_scenario_producer_invocations"] == 0
    assert ex.pull_run is None


def test_primary_policy_runs_cameron_exactly_once(count_producer):
    ex, r = _run()                                       # default primary
    assert count_producer["n"] == 1
    assert r["counts"]["executed_common_scenario_lenses"] == 1


def test_selected_cameron_runs_once(count_producer):
    _, r = _run(lens_selection_policy="selected", requested_lens_ids=("cameron2020.extraction_bdf",))
    assert count_producer["n"] == 1 and r["counts"]["executed_common_scenario_lenses"] == 1


def test_selected_cameron_twice_is_canonicalized_no_duplicate_execution(count_producer):
    _, r = _run(lens_selection_policy="selected",
                requested_lens_ids=("cameron2020.extraction_bdf", "cameron2020.extraction_bdf"))
    assert count_producer["n"] == 1                      # deduped -> one execution
    assert r["counts"]["executed_common_scenario_lenses"] == 1


def test_selected_registered_non_ready_component_runs_no_producer(count_producer):
    # mo has no adapter -> declined without running Cameron's (or any) producer
    _, r = _run(lens_selection_policy="selected", requested_lens_ids=("mo2023_2.coupled_bed",))
    assert count_producer["n"] == 0
    rec = {ls["component_id"]: ls for ls in r["lens_selection"]}["mo2023_2.coupled_bed"]
    assert rec["lens_request_state"] == "REQUESTED_BUT_NOT_EXECUTABLE"
    assert rec["adapter_readiness"] == "NO_ADAPTER"


def test_domain_blocked_cameron_runs_no_producer(count_producer):
    _, r = _run(domain_policy="strict", overrides={"pressure_bar": 20.0})
    assert count_producer["n"] == 0
    assert r["domain"]["blocked"] is True and r["domain"]["producer_executed"] is False
    le = {x["component_id"]: x for x in r["lens_execution"]}["cameron2020.extraction_bdf"]
    assert le["adapter_readiness"] == "OUTSIDE_DOMAIN" and le["producer_invoked"] is False


def test_rights_blocked_lens_is_declined_without_execution(count_producer):
    _, r = _run(lens_selection_policy="selected", requested_lens_ids=("grudeva2025.reduced",))
    assert count_producer["n"] == 0
    le = {x["component_id"]: x for x in r["lens_execution"]}["grudeva2025.reduced"]
    assert le["adapter_readiness"] == "RIGHTS_BLOCKED" and le["producer_invoked"] is False


def test_executed_count_equals_producer_invocations(count_producer):
    _, r = _run()
    assert r["counts"]["executed_common_scenario_lenses"] == r["counts"][
        "common_scenario_producer_invocations"] == count_producer["n"]


# ── a fake adapter executes independently of Cameron ────────────────────────────────
def _fake_adapter(component_id, *, raises=False):
    def ev(prepared):
        return ()
    def prep(prepared):
        return prepared.recipe_obj, prepared.config_obj, {"note": "fake"}
    def producer(recipe, config):
        if raises:
            raise RuntimeError("fake adapter boom")
        return {"final_observables": {}, "traces": [], "warnings": [], "run_id": "fake"}
    def translate(run):
        return {"observables": [], "traces": []}
    return lab.LensAdapterSpec(
        adapter_id=f"fake_{component_id}", adapter_version="0", component_id=component_id,
        runtime_class="interactive-fast", is_primary=False, accepted_scenario_quantities=(),
        required_fixed_inputs=(), evidence={"note": "fake"}, evaluate_domain=ev, prepare_inputs=prep,
        producer=producer, translate_outputs=translate)


def test_fake_adapter_executes_without_invoking_cameron(count_producer, monkeypatch):
    # a registered component with no rights block; give it a fake adapter that does NOT call simulate_pull
    target = "mo2023_2.coupled_bed"
    monkeypatch.setitem(lab.ADAPTERS, target, _fake_adapter(target))
    _, r = _run(lens_selection_policy="selected", requested_lens_ids=(target,))
    assert count_producer["n"] == 0                      # Cameron's producer NOT invoked
    le = {x["component_id"]: x for x in r["lens_execution"]}[target]
    assert le["status"] == "executed" and le["producer_invoked"] is True


def test_one_adapter_failure_does_not_erase_another(count_producer, monkeypatch):
    target = "mo2023_2.coupled_bed"
    monkeypatch.setitem(lab.ADAPTERS, target, _fake_adapter(target, raises=True))
    _, r = _run(lens_selection_policy="selected",
                requested_lens_ids=("cameron2020.extraction_bdf", target))
    states = {x["component_id"]: x["status"] for x in r["lens_execution"]}
    assert states["cameron2020.extraction_bdf"] == "executed"   # Cameron still executed
    assert states[target] == "FAILED"                          # the fake failed, isolated
    assert count_producer["n"] == 1


# ── reference selection resolves COMPONENTS, not just runner registrations ───────────
def test_reference_selection_registered_component_without_runner_is_not_implemented():
    # mo is a registered component with no runner -> RUNNER_NOT_IMPLEMENTED, not "unknown"
    ex = lab.execute_scenario(lab.ScenarioRequest(
        "pv19_named", reference_selection_policy="selected",
        requested_reference_runner_ids=("mo2023_2.coupled_bed",)))
    r = lab.build_comparison(ex)
    rec = {x["component_id"]: x for x in r["reference_selection"]}["mo2023_2.coupled_bed"]
    assert rec["native_runner_execution_state"] == "RUNNER_NOT_IMPLEMENTED"


def test_reference_selection_rights_blocked_component_is_not_executed():
    ex = lab.execute_scenario(lab.ScenarioRequest(
        "pv19_named", reference_selection_policy="selected",
        requested_reference_runner_ids=("grudeva2025.reduced",)))
    r = lab.build_comparison(ex)
    rec = {x["component_id"]: x for x in r["reference_selection"]}["grudeva2025.reduced"]
    assert rec["native_runner_execution_state"] == "RIGHTS_BLOCKED"
    assert "grudeva2025.reduced" not in {x["component_id"] for x in r["executed_reference_results"]}


def test_reference_selection_non_registered_id_is_unknown():
    ex = lab.execute_scenario(lab.ScenarioRequest(
        "pv19_named", reference_selection_policy="selected",
        requested_reference_runner_ids=("not.a.component",)))
    with pytest.raises(ValueError):                       # non-registered id is 'unknown' at resolution
        lab.build_comparison(ex)


# ── back-compat: no bare PullRun recovers scenario identity ──────────────────────────
def test_bare_pullrun_cannot_be_fed_to_build_comparison():
    run = lab.run_scenario("guided_v1")
    with pytest.raises(TypeError):
        lab.build_comparison(run)


def test_run_scenario_wrapper_still_returns_a_pullrun():
    run = lab.run_scenario("guided_v1", dose_g=19.0)
    assert run["schema_version"] == 1 and run["recipe"]["dose_g"] == 19.0


def test_all_ready_policy_selects_only_ready_adapters(count_producer):
    _, r = _run(lens_selection_policy="all_ready")
    executed = {x["component_id"] for x in r["lens_execution"] if x["status"] == "executed"}
    assert executed == {"cameron2020.extraction_bdf"}     # only Cameron is ready today
    assert count_producer["n"] == 1
