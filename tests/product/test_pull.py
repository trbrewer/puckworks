"""Core tests for the Guided Espresso Pull (issue #48).

Offline, deterministic, CPU-only. Covers recipe validation, the bean-label/profile separation, the
domain warn/reject engine (no silent clamp), determinism, stage completeness, full component
coverage, parallel-lens safety, conservation, and export/CLI paths.
"""
import json
import math
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
    r, c = _guided(grind_setting=2.45)   # below evidence range but computable
    run = p.simulate_pull(r, c)
    gs = [f for f in run.domain_findings if f.field == "grind_setting"][0]
    assert gs.status is p.DomainStatus.WARNING and gs.status is not p.DomainStatus.IN_DOMAIN


# ── temperature is recorded-only, not a model input (1C/1D) ───────────────────────
def test_temperature_is_recorded_only_and_changes_nothing():
    from dataclasses import replace
    r, c = p.load_pull_preset("guided_v1")
    a = p.pull_run_to_dict(p.simulate_pull(replace(r, brew_temperature_c=86.0), c))
    b = p.pull_run_to_dict(p.simulate_pull(replace(r, brew_temperature_c=94.0), c))
    # the computed numbers (traces + final observables) must be identical; only the *recorded* value
    # (recipe echo, run_id, and the temperature it reports back) may differ.
    assert a["traces"] == b["traces"], "temperature changed a model trace but must be recorded-only"
    assert a["final_observables"] == b["final_observables"], "temperature changed a final observable"
    run = p.simulate_pull(replace(r, brew_temperature_c=70.0), c)   # a valid, but recorded-only, value
    temp = [f for f in run.domain_findings if f.field == "brew_temperature_c"][0]
    assert temp.status is p.DomainStatus.NOT_APPLICABLE     # never WARNING (model does not use it)
    assert not any(w.startswith("brew_temperature_c") for w in run.warnings)


def test_out_of_liquid_temperature_is_rejected():
    r, c = _guided(brew_temperature_c=150.0)
    with pytest.raises(p.PullDomainError, match="rejected"):
        p.simulate_pull(r, c)


# ── unsupported recipe fields are rejected, never silently accepted (1D) ──────────
@pytest.mark.parametrize("field,value", [
    ("preinfusion_s", 5.0),
    ("preinfusion_pressure_bar", 3.0),
    ("basket_diameter_mm", 58.0),
])
def test_unsupported_recipe_fields_are_rejected(field, value):
    from dataclasses import replace
    r, c = p.load_pull_preset("guided_v1")
    with pytest.raises(p.PullDomainError, match="rejected"):
        p.simulate_pull(replace(r, **{field: value}), c)


# ── every active input actually changes a numerical result (1D) ───────────────────
@pytest.mark.parametrize("field,value", [
    ("dose_g", 18.0), ("target_beverage_g", 36.0), ("pressure_bar", 7.0), ("grind_setting", 1.9),
])
def test_active_inputs_change_the_calculation(field, value):
    from dataclasses import replace
    r, c = p.load_pull_preset("guided_v1")
    base = p.pull_run_to_dict(p.simulate_pull(r, c))["final_observables"]
    changed = p.pull_run_to_dict(p.simulate_pull(replace(r, **{field: value}), c))["final_observables"]
    assert base != changed, f"{field} is an active control but changed nothing"


# ── configuration enforcement (1E) ────────────────────────────────────────────────
def test_unknown_config_is_rejected():
    from dataclasses import replace
    r, c = p.load_pull_preset("guided_v1")
    with pytest.raises(p.PullDomainError, match="config_id"):
        p.simulate_pull(r, replace(c, config_id="mystery"))
    with pytest.raises(p.PullDomainError, match="config_version"):
        p.simulate_pull(r, replace(c, config_version=99))


def test_unsupported_stage_override_is_rejected():
    from dataclasses import replace
    r, c = p.load_pull_preset("guided_v1")
    bad = replace(c, stage_components={"grind": "foster2025.machine_mode",
                                       "machine_flow": "cameron2020.extraction_bdf",
                                       "extraction": "cameron2020.extraction_bdf"})
    with pytest.raises(p.PullDomainError, match="stage_components"):
        p.simulate_pull(r, bad)


def test_nonempty_lens_request_is_rejected():
    from dataclasses import replace
    r, c = p.load_pull_preset("guided_v1")
    with pytest.raises(p.PullDomainError, match="lenses"):
        p.simulate_pull(r, replace(c, lenses=("mo2023_2.coupled_bed",)))


def test_nonconstant_pressure_profile_is_rejected():
    with pytest.raises(p.PullDomainError, match="pressure_profile"):
        p.PullConfig(config_id="guided_v1", config_version=1,
                     stage_components={"grind": "cameron2020.extraction_bdf",
                                       "machine_flow": "cameron2020.extraction_bdf",
                                       "extraction": "cameron2020.extraction_bdf"},
                     pressure_profile="ramp")


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
    cam = by_id["cameron2020.extraction_bdf"]
    assert cam.disposition is p.ComponentDisposition.EXECUTED_PRIMARY and cam.executed is True
    # a known calibration component is labelled calibration-only
    assert by_id["wadsworth2026.permeability"].disposition is p.ComponentDisposition.CALIBRATION_ONLY
    # the optional GPU component is not silently primary
    assert by_id["brewer2026.lb_taichi"].disposition is p.ComponentDisposition.EXCLUDED_OPTIONAL_DEPENDENCY
    for c in RUN.coverage:
        assert c.reason, f"{c.component_id} has no disposition reason"


def test_only_the_primary_is_marked_executed():
    executed = [c for c in RUN.coverage if c.executed]
    assert [c.component_id for c in executed] == ["cameron2020.extraction_bdf"]
    # nothing is described as "compared" — no parallel lens is executed
    for c in RUN.coverage:
        assert "compared" not in c.reason.lower()


def test_coverage_serializes_executed_flag():
    cov = p.pull_run_to_dict(RUN)["coverage"]
    cam = [c for c in cov if c["component_id"] == "cameron2020.extraction_bdf"][0]
    assert cam["disposition"] == "executed_primary" and cam["executed"] is True
    assert all("compared_as_lens" != c["disposition"] for c in cov)


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


# ── authoritative traces (1A/1B) ──────────────────────────────────────────────────
def _trace(run, tid):
    return [t for t in run.traces if t.trace_id == tid][0]


def _series(trace, sid):
    return [s for s in trace.series if s.series_id == sid][0]


def test_traces_are_present_and_well_formed():
    ids = {t.trace_id for t in RUN.traces}
    assert {"machine_flow_time", "extraction_time", "bed_liquid_profile"} <= ids
    for t in RUN.traces:
        assert t.axis_values and t.series and t.axis_unit and t.component_id == "cameron2020.extraction_bdf"
        assert t.evidence_badge == "EXPLORATORY_SIMULATION" and t.fidelity_ceiling
        for s in t.series:
            assert len(s.values) == len(t.axis_values)          # series length matches axis
            assert s.role in p.SERIES_ROLES and s.unit
            assert all(math.isfinite(v) for v in s.values)      # no non-finite values


def test_prescribed_pressure_is_labelled_prescribed_not_measured():
    s = _series(_trace(RUN, "machine_flow_time"), "prescribed_pressure_bar")
    assert s.role == "prescribed_input"          # never "measured" / "simulated"
    assert set(s.values) == {RUN.recipe.pressure_bar}   # constant prescribed input


def test_trace_time_endpoint_equals_shot_time():
    t = _trace(RUN, "extraction_time")
    assert abs(t.axis_values[-1] - RUN.final_observables["shot_duration_s"]["value"]) < 0.05


def test_cumulative_beverage_endpoint_matches_final_beverage():
    s = _series(_trace(RUN, "machine_flow_time"), "cumulative_beverage_g")
    assert s.role == "derived"
    assert abs(s.values[-1] - RUN.final_observables["beverage_mass_g"]["value"]) < 1e-6


def test_cumulative_extracted_endpoint_matches_final_extracted():
    s = _series(_trace(RUN, "extraction_time"), "cumulative_extracted_g")
    assert s.role == "simulated"
    assert abs(s.values[-1] - RUN.final_observables["extracted_mass_g"]["value"]) < 0.01


def test_derived_yield_endpoint_matches_final_EY():
    s = _series(_trace(RUN, "extraction_time"), "extraction_yield_pct")
    assert s.role == "derived"
    assert abs(s.values[-1] - RUN.final_observables["extraction_yield_pct"]["value"]) < 0.01


def test_traces_preserve_solver_precision_in_json():
    js = p.pull_run_to_dict(RUN)
    ex = [t for t in js["traces"] if t["trace_id"] == "extraction_time"][0]
    vals = [s for s in ex["series"] if s["series_id"] == "cumulative_extracted_g"][0]["values"]
    # display observable is rounded to 3 dp; the trace keeps full precision (more significant digits)
    assert any(len(repr(v).split(".")[-1]) > 4 for v in vals if isinstance(v, float))


def test_traces_are_deterministic_in_json():
    assert p.pull_run_to_json(_shared_run()) == p.pull_run_to_json(_shared_run())


# ── first-drip correction (1C) ────────────────────────────────────────────────────
def test_first_drip_is_unavailable_not_zero():
    fd = RUN.final_observables["first_drip_s"]
    assert fd["value"] is None and fd["status"] == "unavailable"
    assert "saturated bed" in fd["reason"]
    # the old number survives only under an honest diagnostic name
    diag = RUN.final_observables["first_modeled_solute_arrival_s"]
    assert diag["status"] == "diagnostic" and diag["value"] is not None
    assert "first_drip" not in {s.stage_id for s in RUN.stages}   # not a stage
    ex = [s for s in RUN.stages if s.stage_id == "extraction"][0]
    assert "first_drip" not in ex.outputs and "first_modeled_solute_arrival" in ex.outputs


def test_markdown_shows_first_drip_unavailable():
    md = p.pull_run_to_markdown(RUN)
    assert "first_drip_s**: unavailable" in md
    assert "recorded-only" in md    # temperature marked recorded-only


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


def test_cli_strict_mode_rejects_out_of_range():
    from puckworks.product import _pull_cli as cli
    # out of evidence range under strict policy -> nonzero (rejected)
    assert cli.main(["run", "--preset", "guided_v1", "--grind-setting", "2.45",
                     "--domain-policy", "strict"]) == 2


def test_cli_summary_reports_first_drip_unavailable(capsys):
    from puckworks.product import _pull_cli as cli
    assert cli.main(["run", "--preset", "pv19_named", "--format", "summary"]) == 0
    err = capsys.readouterr().err
    assert "first drip: unavailable" in err and "recorded-only" in err


def test_cli_figures_report(tmp_path):
    pytest.importorskip("matplotlib")
    from puckworks.product import _pull_cli as cli
    d = tmp_path / "report"
    assert cli.main(["run", "--preset", "guided_v1", "--report-dir", str(d)]) == 0
    assert (d / "guided_pull_summary.png").exists()
    assert (d / "guided_pull_results.json").exists()


def test_cli_missing_viz_extra_message(tmp_path, monkeypatch, capsys):
    from puckworks.product import _pull_cli as cli
    import puckworks.product._pull as pull_mod

    def _no_mpl(*a, **k):
        raise ModuleNotFoundError("Guided pull figures require the `puckworks[viz]` optional dependencies")

    monkeypatch.setattr(pull_mod, "render_pull_report", _no_mpl)
    rc = cli.main(["run", "--preset", "guided_v1", "--report-dir", str(tmp_path / "r")])
    assert rc == 3 and "puckworks[viz]" in capsys.readouterr().err


# ── offline / no private data (23) ────────────────────────────────────────────────
def test_runs_offline_and_uses_no_private_paths():
    # the autouse network guard (conftest) already fails on any outbound connect; a run completing
    # proves it needs no network. Also assert no data-file dependency string leaked into output.
    js = p.pull_run_to_json(_shared_run())
    assert "visualizer" not in js.lower() and "/raw/" not in js


def test_pw_pull_001_fixed_preset_rejects_every_override():
    # PW-PULL-001: pv19_named has editable_fields=(); the empty tuple used to be falsy and disabled
    # enforcement, and grinder_model/domain_policy were exempt. A fixed preset must reject ALL overrides.
    from types import SimpleNamespace
    from puckworks.product._pull import load_pull_preset, PullDomainError
    from puckworks.product._pull_cli import _apply_overrides, _require_editable

    recipe, config = load_pull_preset("pv19_named")
    assert config.editable_fields == ()   # fixed preset

    def args(**kw):
        base = dict(dose_g=None, beverage_g=None, temperature_c=None, pressure_bar=None,
                    grind_setting=None, coffee_profile=None, bean_label=None, grinder_model=None)
        base.update(kw)
        return SimpleNamespace(**base)

    for kw in (dict(dose_g=99.0), dict(grinder_model="OTHER"), dict(pressure_bar=15.0),
               dict(beverage_g=80.0), dict(coffee_profile="x")):
        with pytest.raises(PullDomainError):
            _apply_overrides(recipe, config, args(**kw))
    with pytest.raises(PullDomainError):
        _require_editable(config, "domain_policy")   # domain_policy is not exempt either


def test_pw_pull_001_semantics_none_unrestricted_vs_empty_fixed():
    from types import SimpleNamespace
    from puckworks.product._pull import load_pull_preset, PullDomainError
    from puckworks.product._pull_cli import _apply_overrides

    def args(**kw):
        base = dict(dose_g=None, beverage_g=None, temperature_c=None, pressure_bar=None,
                    grind_setting=None, coffee_profile=None, bean_label=None, grinder_model=None)
        base.update(kw); return SimpleNamespace(**base)

    # guided_v1 lists dose_g as editable but NOT grinder_model
    recipe, config = load_pull_preset("guided_v1")
    _apply_overrides(recipe, config, args(dose_g=20.0))          # allowed
    with pytest.raises(PullDomainError):
        _apply_overrides(recipe, config, args(grinder_model="OTHER"))   # not in its editable set


def test_pw_pull_001_editable_fields_none_is_unrestricted():
    # None means unrestricted (the backward-compatible default); a tuple (incl. ()) restricts.
    from types import SimpleNamespace
    from puckworks.product._pull import PullConfig
    from puckworks.product._pull_cli import _apply_overrides, load_pull_preset
    recipe, config = load_pull_preset("guided_v1")
    open_cfg = PullConfig(config_id="x", config_version=1,
                          stage_components=dict(config.stage_components), editable_fields=None)
    args = SimpleNamespace(dose_g=1.0, beverage_g=None, temperature_c=None, pressure_bar=None,
                           grind_setting=None, coffee_profile=None, bean_label=None,
                           grinder_model="ANY")
    _apply_overrides(recipe, open_cfg, args)   # unrestricted: no raise


def test_pw_pull_003_hard_ceilings_reject_absurd_inputs():
    # PW-PULL-003: dose/beverage/pressure had only >0 lower bounds; an absurd value reached the solver.
    from dataclasses import replace
    from puckworks.product._pull import (evaluate_domain, load_pull_preset, DomainStatus)
    recipe, _ = load_pull_preset("pv19_named")
    for field, bad in (("dose_g", 1e9), ("target_beverage_g", 1e9), ("pressure_bar", 1e6)):
        findings = evaluate_domain(replace(recipe, **{field: bad}))
        assert any(f.status is DomainStatus.REJECTED and f.field == field for f in findings), field


def test_pw_pull_003_solver_finite_guards():
    from puckworks.product._pull import _require_finite, _require_finite_positive, PullExecutionError
    assert _require_finite_positive("q", 1.5) == 1.5
    for bad in (0.0, -1.0, float("inf"), float("nan")):
        with pytest.raises(PullExecutionError):
            _require_finite_positive("q", bad)
    with pytest.raises(PullExecutionError):
        _require_finite("ey", float("nan"))


def test_pw_pull_003_nonfinite_flux_is_controlled_error_not_leak(monkeypatch):
    # a solver that returns a non-finite Darcy flux must raise PullExecutionError, not ZeroDivision/inf
    from puckworks.product import _pull
    from puckworks.models.cameron2020 import extraction_bdf as cam
    recipe, config = _pull.load_pull_preset("pv19_named")
    monkeypatch.setattr(cam, "darcy_flux", lambda *a, **k: 0.0)
    with pytest.raises(_pull.PullExecutionError):
        _pull.simulate_pull(recipe, config)


def test_pw_pull_004_exactly_one_terminal_event_success_and_failure():
    import unittest.mock as mock
    from puckworks.product._pull import (simulate_pull, load_pull_preset, PullEvent, PullExecutionError)
    from puckworks.models.cameron2020 import extraction_bdf as cam
    recipe, config = load_pull_preset("pv19_named")

    # success: exactly one terminal event, RUN_COMPLETED, no RUN_FAILED
    ev = []
    simulate_pull(recipe, config, progress=lambda e, p: ev.append(e))
    terminals = [e for e in ev if e in (PullEvent.RUN_COMPLETED, PullEvent.RUN_FAILED)]
    assert terminals == [PullEvent.RUN_COMPLETED]

    # a producer-phase (solver) failure emits exactly one RUN_FAILED, then re-raises
    ev2 = []
    with mock.patch.object(cam, "darcy_flux", return_value=0.0):
        with pytest.raises(PullExecutionError):
            simulate_pull(recipe, config, progress=lambda e, p: ev2.append((e, p.get("category"))))
    fails = [(e, c) for e, c in ev2 if e == PullEvent.RUN_FAILED]
    assert fails == [(PullEvent.RUN_FAILED, "execution")]


def test_pw_pull_005_series_and_trace_invariants():
    from puckworks.product._pull import PullSeries, PullTrace, PullDomainError

    def series(sid, vals):
        return PullSeries(sid, "l", tuple(float(v) for v in vals), "u", "simulated", "m", "c")

    # empty series values rejected
    with pytest.raises(PullDomainError):
        series("s", ())
    good = series("s", [1.0, 2.0, 3.0])

    def trace(axis, series_list):
        return PullTrace("t", "st", "comp", "ax", "u", tuple(float(a) for a in axis),
                         tuple(series_list), "m", "b", "e", "f", "a", "c")

    trace([0.0, 1.0, 2.0], [good])                              # valid
    with pytest.raises(PullDomainError):                        # no series
        trace([0.0, 1.0, 2.0], [])
    with pytest.raises(PullDomainError):                        # non-increasing axis
        trace([0.0, 0.0, 1.0], [good])
    with pytest.raises(PullDomainError):                        # duplicate series ids
        trace([0.0, 1.0, 2.0], [good, series("s", [4.0, 5.0, 6.0])])
    with pytest.raises(PullDomainError):                        # length mismatch
        trace([0.0, 1.0], [good])
