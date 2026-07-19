"""Selected-reference-only PUBLIC_ARTIFACT path for brewer2026.lb_reference (#70).

The repository's first tightly-bounded public-artifact path: a request that selects EXACTLY the
affirmatively-reviewed first-party LB code-verification runner passes the PUBLIC_ARTIFACT rights preflight
and executes precisely that one native producer. This is NOT a generic public-execution bypass — a broad
or default public request, a Grudeva selection, or an unreviewed selection still blocks before any
producer, and the LB clearance never propagates to another component.
"""
import json
import os

import pytest

import puckworks
import tools.lab_batch as lab_batch
from puckworks.product import lab
from puckworks.product import lab_rights_gate as gate
from puckworks.product import lab_runners

LB = "brewer2026.lb_reference"


def _lb_only_env(out_dir, context="PUBLIC_ARTIFACT"):
    # the SELECTED safe request is explicit: no common-scenario lens, exactly one native reference
    return {"LAB_PRESET": "pv19_named", "LAB_LENS_SELECTION_POLICY": "none",
            "LAB_REFERENCE_SELECTION_POLICY": "selected", "LAB_REFERENCE_IDS": LB,
            "LAB_EXECUTION_CONTEXT": context, "LAB_OUT_DIR": str(out_dir)}


@pytest.fixture
def spy(monkeypatch):
    """Record producer/preflight call order so we can prove preflight runs BEFORE any producer."""
    events = []
    orig_pre = gate.preflight
    monkeypatch.setattr(gate, "preflight",
                        lambda req, ctx: (events.append(("preflight", ctx)), orig_pre(req, ctx))[1])
    orig_exec = lab_runners.execute_runner
    monkeypatch.setattr(lab_runners, "execute_runner",
                        lambda cid: (events.append(("native_producer", cid)), orig_exec(cid))[1])
    return events


# ── positive path ────────────────────────────────────────────────────────────────────
def test_selected_lb_only_public_artifact_preflight_allows(tmp_path):
    req = lab.ScenarioRequest("pv19_named", lens_selection_policy="none",
                              reference_selection_policy="selected", requested_reference_runner_ids=(LB,))
    v = gate.preflight(req, "PUBLIC_ARTIFACT")
    assert v["blocked"] is False
    # allowed because THIS component has explicit affirmative code + output rights (not NOT_REVIEWED)
    row = [r for r in v["requested"] if r.get("component_id") == LB][0]
    assert row["code_rights_state"] == "CLEAR" and row["output_redistribution_state"] == "CLEAR"
    assert row["code_execution_allowed"] and row["output_publication_allowed"] and not row["blocked"]
    # exactly one requested component, and it is the LB runner (no common lens rows)
    assert [r["component_id"] for r in v["requested"]] == [LB]


def test_preflight_runs_before_and_exactly_one_native_producer_executes(tmp_path, spy):
    rep = lab_batch.run(_lb_only_env(tmp_path / "lb"))
    # preflight is the FIRST recorded event; the only producer is the one LB native reference
    assert spy[0] == ("preflight", "PUBLIC_ARTIFACT")
    native = [e for e in spy if e[0] == "native_producer"]
    assert native == [("native_producer", LB)]
    # authoritative counts: NO common-scenario producer, exactly one native reference
    assert rep["counts"]["common_scenario_producer_invocations"] == 0
    assert rep["counts"]["executed_common_scenario_lenses"] == 0
    assert rep["counts"]["executed_native_references"] == 1


def test_public_artifact_contents(tmp_path):
    lab_batch.run(_lb_only_env(tmp_path / "lb"))
    out = tmp_path / "lb"
    # the CLEARED rights-preflight record + execution context travel with the artifact
    pf = json.loads((out / "guided_pull_lab.rights_preflight.json").read_text())
    assert pf["execution_context"] == "PUBLIC_ARTIFACT" and pf["blocked"] is False
    manifest = json.loads((out / "artifact_manifest.json").read_text())
    assert manifest["execution_context"] == "PUBLIC_ARTIFACT"
    assert manifest["rights_preflight"]["blocked"] is False
    art = json.loads((out / "guided_pull_lab.json").read_text())
    r = [x for x in art["executed_reference_results"] if x["component_id"] == LB][0]
    assert r["component_id"] == LB                                       # component identity
    assert r["outputs"] and all("unit" in o and "role" in o for o in r["outputs"])   # units + roles
    assert "does not validate porous coffee-bed" in r["fidelity_ceiling"]            # fidelity ceiling
    assert r["scientific_payload_hash"]                                   # deterministic scientific hash
    roles = {o["role"] for o in r["outputs"]}
    assert {"simulated", "analytic_reference", "derived"} <= roles


def test_repeated_run_yields_the_same_scientific_hash(tmp_path):
    a = lab_batch.run(_lb_only_env(tmp_path / "a"))
    b = lab_batch.run(_lb_only_env(tmp_path / "b"))
    assert a["integrity"]["scientific_payload_sha256"] == b["integrity"]["scientific_payload_sha256"]
    # the LB reference summary itself is byte-identical across the two runs
    ra = [x for x in a["executed_reference_results"] if x["component_id"] == LB][0]
    rb = [x for x in b["executed_reference_results"] if x["component_id"] == LB][0]
    assert ra["scientific_payload_hash"] == rb["scientific_payload_hash"]


def test_artifact_makes_no_espresso_comparability_claim(tmp_path):
    art = json.loads((lab_batch.run(_lb_only_env(tmp_path / "lb")) and
                      (tmp_path / "lb" / "guided_pull_lab.json")).read_text())
    r = [x for x in art["executed_reference_results"] if x["component_id"] == LB][0]
    # the reference explicitly disclaims espresso/beverage comparability, and no Cameron lens ran
    assert "not the common" in r["caveat"].lower()
    assert "predict espresso extraction" in r["fidelity_ceiling"]
    assert art["counts"]["executed_common_scenario_lenses"] == 0


# ── negative coverage: this is NOT a generic bypass ──────────────────────────────────
def test_broad_default_public_request_still_blocks_before_any_producer(tmp_path, spy):
    # a default public artifact request selects the primary Cameron lens (NOT_REVIEWED) -> hard block
    with pytest.raises(RuntimeError) as exc:
        lab_batch.run({"LAB_PRESET": "pv19_named", "LAB_EXECUTION_CONTEXT": "PUBLIC_ARTIFACT",
                       "LAB_OUT_DIR": str(tmp_path / "broad")})
    assert "rights preflight blocked" in str(exc.value)
    # preflight ran; NO producer of any kind ran
    assert ("preflight", "PUBLIC_ARTIFACT") in spy
    assert not any(e[0] == "native_producer" for e in spy)
    # a blocked request leaves NO final artifact directory — only the preflight-denial record
    assert not (tmp_path / "broad").is_dir()
    assert (tmp_path / "broad.rights_preflight.json").exists()
    denial = json.loads((tmp_path / "broad.rights_preflight.json").read_text())
    assert denial["blocked"] is True
    assert not (tmp_path / "broad").exists()      # no guided_pull_lab.json / scientific output written


def test_grudeva_selection_hard_blocks_even_locally(tmp_path):
    req = lab.ScenarioRequest("pv19_named", lens_selection_policy="none",
                              reference_selection_policy="selected",
                              requested_reference_runner_ids=("grudeva2025.reduced",))
    for ctx in ("LOCAL_PRIVATE", "PUBLIC_BATCH", "PUBLIC_ARTIFACT"):
        v = gate.preflight(req, ctx)
        assert v["blocked"] is True
        assert any("grudeva2025.reduced" in b for b in v["blockers"])
    # grudeva is never a native runner
    assert "grudeva2025.reduced" not in lab_runners.RUNNERS


def test_roman_remains_deferred_and_unregistered_as_a_producer():
    assert lab_runners.has_runner("romancorrochano2017.extraction") is False
    # not selectable as a public producer (no runner) and not affirmatively cleared
    from puckworks import rights
    assert not rights.may_execute_in_public_batch("romancorrochano2017.extraction").allowed


def test_the_other_native_runners_are_not_made_outward_clear_by_the_lb_decision():
    from puckworks import rights
    for cid in ("waszkiewicz2025.poroelastic", "wadsworth2026.permeability", "foster2025.infiltration"):
        req = lab.ScenarioRequest("pv19_named", lens_selection_policy="none",
                                  reference_selection_policy="selected",
                                  requested_reference_runner_ids=(cid,))
        v = gate.preflight(req, "PUBLIC_ARTIFACT")
        assert v["blocked"] is True                          # still NOT_REVIEWED for outward use
        assert rights.rights_record(cid).code_rights_state == "NOT_REVIEWED"


def test_a_mixed_request_with_lb_plus_an_unreviewed_runner_blocks(tmp_path, spy):
    # LB is cleared but Waszkiewicz is not: ONE blocked selection blocks the WHOLE request before producers
    with pytest.raises(RuntimeError):
        lab_batch.run({"LAB_PRESET": "pv19_named", "LAB_LENS_SELECTION_POLICY": "none",
                       "LAB_REFERENCE_SELECTION_POLICY": "selected",
                       "LAB_REFERENCE_IDS": f"{LB},waszkiewicz2025.poroelastic",
                       "LAB_EXECUTION_CONTEXT": "PUBLIC_ARTIFACT", "LAB_OUT_DIR": str(tmp_path / "mix")})
    assert not any(e[0] == "native_producer" for e in spy)   # zero producers on a blocked mixed request
    assert not (tmp_path / "mix").is_dir()


def test_unknown_reference_id_fails_distinctly():
    # a non-registered id is surfaced as a DISTINCT unknown+blocked preflight row (never a silent drop),
    # blocking the request before any producer
    req = lab.ScenarioRequest("pv19_named", lens_selection_policy="none",
                              reference_selection_policy="selected",
                              requested_reference_runner_ids=("not.a.component",))
    v = gate.preflight(req, "PUBLIC_ARTIFACT")
    assert v["blocked"] is True
    unknown_rows = [r for r in v["requested"] if r.get("unknown")]
    assert unknown_rows and "unknown reference id" in unknown_rows[0]["blocker"]
    assert unknown_rows[0]["component_id"] is None


def test_no_context_env_or_flag_can_turn_the_lb_record_into_a_generic_bypass():
    # there is no allow-rights-blocked / force flag anywhere in the batch boundary
    src = open(lab_batch.__file__).read() + open(gate.__file__).read()
    for token in ("allow-rights-blocked", "allow_rights_blocked", "force_public", "FORCE_PUBLIC",
                  "skip_preflight", "bypass"):
        assert token not in src
    # PUBLIC_ARTIFACT with a broad selection cannot be coerced clear by any env var: still blocked
    req = lab.ScenarioRequest("pv19_named")                  # default primary Cameron lens
    assert gate.preflight(req, "PUBLIC_ARTIFACT")["blocked"] is True


def test_only_the_lb_component_is_affirmatively_public_live_today():
    # the set of components that pass BOTH public-execution and output-publication clearance is exactly {LB}
    from puckworks import rights
    live = sorted(c.name for c in puckworks.components()
                  if rights.may_execute_in_public_batch(c.name).allowed
                  and rights.may_publish_outputs(c.name).allowed)
    assert live == [LB]
