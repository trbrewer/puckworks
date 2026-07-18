"""Core tests for the Guided Espresso Pull (issue #48).

Offline, deterministic, CPU-only. Covers recipe validation, the bean-label/profile separation, the
domain warn/reject engine (no silent clamp), determinism, stage completeness, full component
coverage, parallel-lens safety, conservation, and export/CLI paths.
"""
import json
import re

import puckworks
import puckworks.product as p
import pytest


def _shared_run():
    recipe, config = p.load_pull_preset("pv19_named")
    return p.simulate_pull(recipe, config)


RUN = _shared_run()


# ── recipe validation + units (1) ────────────────────────────────────────────────
def test_recipe_requires_finite_numbers_and_grind():
    with pytest.raises(p.PullDomainError):
        p.PullRecipe(dose_g=float("nan"), target_beverage_g=40, brew_temperature_c=93,
                     pressure_bar=9, grinder_model="EK43", coffee_profile="reference", grind_setting=1.7)
    with pytest.raises(p.PullDomainError, match="grind_setting.*or.*mean_particle_radius_m"):
        p.PullRecipe(dose_g=20, target_beverage_g=40, brew_temperature_c=93, pressure_bar=9,
                     grinder_model="EK43", coffee_profile="reference")


def test_stage_inputs_outputs_carry_units():
    for s in RUN.stages:
        for io in (s.inputs, s.outputs):
            for name, spec in io.items():
                assert "value" in spec and "unit" in spec, f"{s.stage_id}.{name} missing value/unit"


# ── bean_label vs coffee_profile (2,3,4) ──────────────────────────────────────────
def test_bean_label_does_not_change_any_numeric_result():
    r1, c = p.load_pull_preset("guided_v1")
    from dataclasses import replace
    a = p.pull_run_to_dict(p.simulate_pull(replace(r1, bean_label="light ethiopian natural"), c))
    b = p.pull_run_to_dict(p.simulate_pull(replace(r1, bean_label="dark robusta"), c))
    a["recipe"]["bean_label"] = b["recipe"]["bean_label"] = None   # ignore the label field itself
    assert a == b, "bean_label changed a numeric/model result"


def test_unknown_coffee_profile_rejected():
    r, c = p.load_pull_preset("guided_v1")
    from dataclasses import replace
    with pytest.raises(p.PullDomainError, match="unknown coffee_profile"):
        p.simulate_pull(replace(r, coffee_profile="ethiopian-natural-light"), c)


# ── grinder dial / particle radius (5,6) ──────────────────────────────────────────
def test_both_dial_and_radius_rejected():
    with pytest.raises(p.PullDomainError, match="not both"):
        p.PullRecipe(dose_g=20, target_beverage_g=40, brew_temperature_c=93, pressure_bar=9,
                     grinder_model="EK43", coffee_profile="reference", grind_setting=1.7,
                     mean_particle_radius_m=1e-4)


def test_radius_only_has_no_verified_adapter_yet():
    r = p.PullRecipe(dose_g=20, target_beverage_g=40, brew_temperature_c=93, pressure_bar=9,
                     grinder_model="EK43", coffee_profile="reference", mean_particle_radius_m=1e-4)
    _, c = p.load_pull_preset("guided_v1")
    with pytest.raises(p.PullDomainError, match="no verified dial adapter"):
        p.simulate_pull(r, c)


# ── domain engine: reject / warn / strict / no clamp (7,8,9,10,25) ────────────────
def _guided(**over):
    r, c = p.load_pull_preset("guided_v1")
    from dataclasses import replace
    return replace(r, **over), c


def test_hard_invalid_rejected():
    r, c = _guided(pressure_bar=-1.0)
    with pytest.raises(p.PullDomainError, match="rejected"):
        p.simulate_pull(r, c)


def test_evidence_departure_warns_in_warn_mode():
    r, c = _guided(grind_setting=2.45)      # inside solver-safe, outside evidence 1.1-2.3
    run = p.simulate_pull(r, c)
    assert run.completion_state == "completed_with_warnings" and run.warnings
    assert any(f.status is p.DomainStatus.WARNING and f.field == "grind_setting"
               for f in run.domain_findings)


def test_same_departure_rejected_in_strict_mode():
    r, c = _guided(grind_setting=2.45)
    from dataclasses import replace
    with pytest.raises(p.PullDomainError, match="strict domain"):
        p.simulate_pull(r, replace(c, domain_policy="strict"))


def test_no_silent_clamp():
    r, c = _guided(grind_setting=2.45)
    run = p.simulate_pull(r, c)
    # the supplied (out-of-range) value is preserved, not clamped to the range edge
    assert run.recipe.grind_setting == 2.45
    assert p.pull_run_to_dict(run)["stages"][0]["inputs"]["grind_setting"]["value"] == 2.45


def test_out_of_range_is_never_labelled_in_domain():
    r, c = _guided(brew_temperature_c=70.0)   # below evidence range but computable
    run = p.simulate_pull(r, c)
    temp = [f for f in run.domain_findings if f.field == "brew_temperature_c"][0]
    assert temp.status is p.DomainStatus.WARNING and temp.status is not p.DomainStatus.IN_DOMAIN


# ── determinism (11,12) ───────────────────────────────────────────────────────────
def test_pv19_named_is_deterministic_and_fixed():
    a = p.pull_run_to_json(_shared_run())
    b = p.pull_run_to_json(_shared_run())
    assert a == b
    recipe, config = p.load_pull_preset("pv19_named")
    assert config.editable_fields == ()          # fixed reference


def test_guided_v1_deterministic_for_identical_inputs():
    r, c = p.load_pull_preset("guided_v1")
    assert p.pull_run_to_json(p.simulate_pull(r, c)) == p.pull_run_to_json(p.simulate_pull(r, c))


# ── stage completeness (13) ───────────────────────────────────────────────────────
def test_every_primary_stage_is_fully_labelled():
    assert [s.stage_id for s in RUN.stages] == ["grind", "machine_flow", "extraction"]
    for s in RUN.stages:
        assert s.method_name and s.method_plain and s.inputs and s.outputs
        assert s.evidence_strength and s.valid_range and s.caveat and s.evidence_badge == "simulated"


# ── coverage ledger (14,17) ───────────────────────────────────────────────────────
def test_every_registered_component_appears_in_coverage():
    puckworks.load_builtin_components()
    covered = {c.component_id for c in RUN.coverage}
    registered = {c.name for c in puckworks.components()}
    assert covered == registered, f"coverage missing: {registered - covered}"


def test_primary_and_calibration_dispositions():
    by_id = {c.component_id: c for c in RUN.coverage}
    assert by_id["cameron2020.extraction_bdf"].disposition is p.ComponentDisposition.USED_PRIMARY
    # a known calibration component is labelled calibration-only
    assert by_id["wadsworth2026.permeability"].disposition is p.ComponentDisposition.CALIBRATION_ONLY
    # the optional GPU component is not silently primary
    assert by_id["brewer2026.lb_taichi"].disposition is p.ComponentDisposition.EXCLUDED_OPTIONAL_DEPENDENCY
    for c in RUN.coverage:
        assert c.reason, f"{c.component_id} has no disposition reason"


# ── parallel-lens safety (15,16) ──────────────────────────────────────────────────
def test_lenses_empty_and_no_consensus_average():
    assert RUN.lenses == ()
    # final observables never contain an averaged/blended consensus field
    keys = " ".join(RUN.final_observables).lower()
    assert "consensus" not in keys and "average" not in keys and "blended" not in keys


# ── conservation / mass balance (19) ──────────────────────────────────────────────
def test_extraction_mass_is_self_consistent():
    obs = RUN.final_observables
    ey = obs["extraction_yield_pct"]["value"]
    dissolved = [s for s in RUN.stages if s.stage_id == "extraction"][0].outputs["dissolved_mass"]["value"]
    extracted = obs["extracted_mass_g"]["value"]
    # extracted mass = EY% * dose; dissolved-in-cup consistent within model tolerance
    assert abs(extracted - ey / 100.0 * RUN.recipe.dose_g) < 0.02   # within display rounding
    assert abs(dissolved - extracted) < 0.5     # holdup difference is bounded


# ── export (20,21) ────────────────────────────────────────────────────────────────
def test_json_is_deterministic_and_dict_matches():
    js = p.pull_run_to_json(RUN)
    assert json.loads(js) == p.pull_run_to_dict(RUN)     # lossless dict<->json
    assert '"run_id"' in js and not re.search(r"\bNaN\b|\bInfinity\b", js)
    # no wall-clock time in the deterministic payload
    assert "started_at" not in p.pull_run_to_dict(RUN)


def test_markdown_has_domain_and_evidence_and_coverage():
    md = p.pull_run_to_markdown(RUN)
    for token in ("Final observables", "Component coverage", "What this does not prove",
                  "extraction_yield_pct", "simulated"):
        assert token in md, token
    assert "flavor prediction" not in md.lower()   # the disclaimer may say what it does NOT do


# ── CLI (22) ──────────────────────────────────────────────────────────────────────
def test_cli_paths():
    from puckworks.product import _pull_cli as cli
    assert cli.main(["presets"]) == 0
    assert cli.main(["run", "--preset", "pv19_named", "--format", "summary"]) == 0
    assert cli.main(["run", "--preset", "guided_v1", "--grind-setting", "2.45"]) == 0   # warn -> 0
    assert cli.main(["run", "--preset", "guided_v1", "--pressure-bar", "-1"]) == 2      # reject
    assert cli.main(["run", "--preset", "guided_v1", "--coffee-profile", "nope"]) == 2  # unknown


def test_cli_writes_json_and_markdown(tmp_path):
    from puckworks.product import _pull_cli as cli
    base = tmp_path / "out" / "guided"
    assert cli.main(["run", "--preset", "guided_v1", "--out", str(base)]) == 0
    assert base.with_suffix(".json").exists() and base.with_suffix(".md").exists()


# ── offline / no private data (23) ────────────────────────────────────────────────
def test_runs_offline_and_uses_no_private_paths():
    # the autouse network guard (conftest) already fails on any outbound connect; a run completing
    # proves it needs no network. Also assert no data-file dependency string leaked into output.
    js = p.pull_run_to_json(_shared_run())
    assert "visualizer" not in js.lower() and "/raw/" not in js
