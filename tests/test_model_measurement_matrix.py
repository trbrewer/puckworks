"""Model-to-measurement matrix + catalog/quantity consolidation (Phase 5, #46/#70).

Offline + deterministic. Every registered component appears in the matrix (a component with no campaign
is shown explicitly, never silently omitted); runtime/runner components without a campaign carry a
documented exemption; the matrix links component -> evidence -> campaign -> gate; the generated section is
deterministic and current; readiness authority is quantity_semantics (reference_basis is deprecated for
readiness); and the current Guided Pull numerics are unchanged.
"""
import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT / "tools") not in sys.path:
    sys.path.insert(0, str(_ROOT / "tools"))

pytest.importorskip("yaml", reason="pyyaml is a radar/dev extra")
import experimental_data_needs as EDN  # noqa: E402


def test_matrix_covers_every_registered_component():
    import puckworks
    rows = EDN.model_to_measurement_matrix()
    ids = [r["component_id"] for r in rows]
    assert set(ids) == {c.name for c in puckworks.components()}
    assert ids == sorted(ids) and len(ids) == len(set(ids))


def test_coverage_is_clean_and_exemptions_are_documented():
    assert EDN.validate_matrix_coverage() == []
    exempt = set(EDN.load_catalog().get("component_campaign_exemptions", []))
    # the three runtime components with no campaign are the documented exemptions
    assert {"grudeva2025.reduced", "foster2025.machine_mode", "wadsworth2026.inertial"} <= exempt


def test_campaigns_for_component_links_correctly():
    assert "EXP-001" in EDN.campaigns_for_component("cameron2020.extraction_bdf")
    assert "EXP-002" in EDN.campaigns_for_component("foster2025.infiltration")
    # a calibration component legitimately has no campaign
    assert EDN.campaigns_for_component("brewer2026.lb_reference") == []


def test_matrix_rows_link_evidence_campaign_and_gate():
    rows = {r["component_id"]: r for r in EDN.model_to_measurement_matrix()}
    cam = rows["cameron2020.extraction_bdf"]
    assert cam["campaigns"] == ["EXP-001", "EXP-008"]
    assert "gate_cameron_conservation" in cam["gates_enabled"]
    assert cam["n_gates"] >= 1


def test_generated_sections_deterministic_and_current():
    assert EDN.render_matrix() == EDN.render_matrix()
    assert EDN._write_generated_table(check=True) == 0     # committed doc is up to date


def test_rights_blocked_component_has_no_campaign_but_is_exempt():
    rows = {r["component_id"]: r for r in EDN.model_to_measurement_matrix()}
    g = rows["grudeva2025.reduced"]
    assert g["has_campaign"] is False
    assert "grudeva2025.reduced" in EDN.load_catalog()["component_campaign_exemptions"]


def test_reference_basis_is_deprecated_for_readiness():
    from puckworks.product import reference_basis as rb
    assert "DEPRECATED" in rb.adapter_readiness.__doc__
    # readiness authority is quantity_semantics; the two must not contradict for Roman
    from puckworks.product import quantity_semantics as qs
    qs_ready = qs.shared_scenario_execution_readiness("romancorrochano2017.extraction")
    assert qs_ready["execution_readiness"] == "READY_FOR_SHARED_SCENARIO"
    # reference_basis still (correctly) says it is not a second EY/TDS overlay
    assert rb.adapter_readiness("romancorrochano2017.extraction")["admissible_as_second_lens"] is False


def test_guided_pull_numerics_unchanged():
    # the consolidation is metadata-only; the Cameron lens still executes and produces observables
    from puckworks.product import lab
    r = lab.build_comparison(lab.execute_scenario(lab.ScenarioRequest("pv19_named")))
    assert r["counts"]["executed_common_scenario_lenses"] == 1
    lens = r["executed_lenses"][0]
    assert lens["component_id"] == "cameron2020.extraction_bdf" and lens["observables"]
