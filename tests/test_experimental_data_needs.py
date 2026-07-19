"""Experimental-data campaign catalog + validator (Phase 3, #46).

Offline + deterministic. Every campaign validates against the live registry (components + gates), the
quantity ontology, and the structured measurement-agenda blockers; campaign IDs are stable; the generated
table is deterministic and current; README/CONTRIBUTING link the page; the issue form parses; and no
measured value / invented threshold / private data appears.
"""
import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT / "tools") not in sys.path:
    sys.path.insert(0, str(_ROOT / "tools"))

pytest.importorskip("yaml", reason="pyyaml is a radar/dev extra")
import experimental_data_needs as EDN  # noqa: E402


def test_catalog_validates():
    assert EDN.validate() == []


def test_every_target_component_and_gate_exists():
    import puckworks
    from puckworks.validation import gates as G
    comps = {c.name for c in puckworks.components()}
    for c in EDN.load_catalog()["campaigns"]:
        for comp in c["target_components"]:
            assert comp in comps
        for g in c["target_gates"]:
            assert hasattr(G, g)


def test_every_quantity_definition_exists():
    from puckworks.product import quantity_semantics as qs
    known = {qs.CAMERON_EY.quantity_id} | {q.quantity_id for q in qs._CANDIDATE_OUTPUT.values()}
    for c in EDN.load_catalog()["campaigns"]:
        for q in c["quantity_definitions"]:
            assert q in known


def test_every_measurement_agenda_blocker_is_mapped_or_deferred():
    from puckworks.product import quantity_semantics as qs
    agenda = {a["blocker_id"] for a in qs.measurement_agenda()}
    cat = EDN.load_catalog()
    mapped = {b for c in cat["campaigns"] for b in c["measurement_agenda_blockers"]}
    deferred = set(cat.get("deferred_blockers", []))
    assert agenda <= (mapped | deferred), agenda - (mapped | deferred)
    # today all three real blockers are mapped
    assert {"mo2023_2.coupled_bed#0", "pannusch2024.solver#0", "pannusch2024.solver#1"} <= mapped


def test_campaign_ids_stable_and_unique():
    ids = [c["campaign_id"] for c in EDN.load_catalog()["campaigns"]]
    assert ids == sorted(ids) and len(ids) == len(set(ids))
    assert ids == ["EXP-00%d" % i for i in range(1, 9)]


def test_generated_table_is_deterministic_and_current():
    a = EDN.render_table()
    b = EDN.render_table()
    assert a == b
    assert EDN._write_generated_table(check=True) == 0     # committed doc is up to date


def test_readme_and_contributing_link_the_page():
    readme = (_ROOT / "README.md").read_text(encoding="utf-8")
    contributing = (_ROOT / "CONTRIBUTING.md").read_text(encoding="utf-8")
    assert "docs/EXPERIMENTAL_DATA_NEEDS.md" in readme
    assert "docs/EXPERIMENTAL_DATA_NEEDS.md" in contributing


def test_issue_form_parses_and_has_required_declarations():
    yaml = pytest.importorskip("yaml")
    form = _ROOT / ".github" / "ISSUE_TEMPLATE" / "experimental-data-submission.yml"
    d = yaml.safe_load(form.read_text(encoding="utf-8"))
    assert d["name"] and d["body"]
    ids = {b.get("id") for b in d["body"] if isinstance(b, dict)}
    assert {"campaign_id", "proposed_license", "declaration"} <= ids


def test_no_measured_value_or_invented_threshold_presented_as_data():
    raw = (_ROOT / "docs" / "data_requests" / "experimental_campaigns.yml").read_text(encoding="utf-8")
    # unknown quantitative values must use the explicit placeholders, not numbers presented as measured
    for c in EDN.load_catalog()["campaigns"]:
        assert c["replication_design_status"] in EDN._PLACEHOLDERS or "PILOT" in str(c)
    # no wall-clock, no private path
    low = raw.lower()
    for bad in ("/users/", "/home/", "wall_clock", "generated_at"):
        assert bad not in low


def test_no_private_or_rights_pending_raw_data_committed():
    # the catalog references EXTERNAL repositories/DOIs; it must not embed raw shot data inline
    raw = (_ROOT / "docs" / "data_requests" / "experimental_campaigns.yml").read_text(encoding="utf-8")
    assert "REQUIRED_FROM_CONTRIBUTOR" in raw       # licences come from the contributor, not assumed
    assert "elapsed_s" not in raw and "weight_g" not in raw   # no embedded raw time series
