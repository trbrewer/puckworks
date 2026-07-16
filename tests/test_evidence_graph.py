"""WP2.4 (schema v2) — the Paper-3 per-claim evidence graph: reconciliation against the LIVE
registry, the scope-aware strict modes (paper3 release gate vs all), the mechanical integrity
guards (no inferred promotion; code/conservation not empirical; fit/eval overlap not independent;
stale component tier; placeholders), the applied semantic corrections, and deterministic
generated artifacts.
"""
import copy

from puckworks.paper3 import evidence_graph as EG


def test_draft_reconcile_is_clean():
    assert EG.reconcile() == []


def test_paper3_strict_release_gate_is_clean():
    # every ASSERTED Paper-3 claim (owner=paper3, use in method/primary) is admissible today
    assert EG.reconcile(strict=True, scope="paper3") == []


def test_all_strict_fails_while_drafts_remain():
    problems = EG.reconcile(strict=True, scope="all")
    n_draft = sum(1 for l in EG.load_links()
                  if l["adjudication_status"] == "NEEDS_ADJUDICATION")
    if n_draft:
        assert any("STRICT(all)" in p for p in problems)
    else:
        assert problems == []


def test_every_registry_wiring_is_covered_and_no_orphans():
    links = EG.load_links()
    wirings, _ = EG.registry_gate_wirings()
    covered = {(l["component"], l["gate"]) for l in links}
    assert set(wirings) == covered
    assert EG.bootstrap_missing() == []


def test_bootstrap_never_infers_a_verdict():
    for d in EG.bootstrap_missing(links=[]):
        assert d["adjudication_status"] == "NEEDS_ADJUDICATION"
        assert d["evidence_strength"] is None                # tier never inferred
        assert d["relationship"] is None and d["sources"] is None
        assert d["claim_owner"] is None and d["paper3_use"] is None
        assert d["support_status"] == "needs_adjudication"
        assert d["component_evidence_strength"] is not None   # context only, carried separately


def test_adjudicated_links_are_complete_and_typed():
    for l in EG.load_links():
        if l["adjudication_status"] != "ADJUDICATED":
            continue
        for f in EG._REQUIRED_WHEN_ADJUDICATED:
            assert l.get(f) not in (None, "", []), "%s missing %s" % (l["link_id"], f)
        assert l["evidence_strength"] in EG.EVIDENCE_STRENGTHS
        assert l["relationship"] in EG.RELATIONSHIPS
        assert l["claim_owner"] in EG.CLAIM_OWNERS
        assert l["paper3_use"] in EG.PAPER3_USES
        assert l["support_status"] in EG.SUPPORT_STATUS
        assert l["reality_facing"] in (True, False)
        assert l["sources"] is not None
        for s in l["sources"]:
            assert s["dataset_status"] in EG.DATASET_STATUS
            assert s["evidence_role"] in EG.EVIDENCE_ROLES
            assert s["independence"] in EG.SOURCE_INDEPENDENCE


def test_component_evidence_matches_live_registry():
    _, ctx = EG.registry_gate_wirings()
    for l in EG.load_links():
        assert l["component_evidence_strength"] == ctx[l["component"]]["component_evidence_strength"]


def _adj(link_id):
    return copy.deepcopy(next(l for l in EG.load_links() if l["link_id"] == link_id))


def _with_id(link, suffix):
    link = copy.deepcopy(link)
    link["link_id"] = link["link_id"] + suffix
    return link


def test_guard_code_verification_not_empirical():
    bad = _with_id(_adj("cameron2020.extraction_bdf::gate_cameron_conservation"), "::g")
    bad["relationship"] = "post_fit_same_data"
    assert any("used as empirical" in p for p in EG.reconcile(links=EG.load_links() + [bad]))


def test_guard_fit_eval_overlap_not_independent():
    bad = _with_id(_adj("waszkiewicz2025.poroelastic::gate_waszkiewicz_static_refit"), "::g")
    bad["relationship"] = "independent_external"            # static_refit overlaps fit/eval
    probs = EG.reconcile(links=EG.load_links() + [bad])
    assert any("independent_external" in p and "overlap" in p for p in probs)


def test_guard_stale_component_tier():
    bad = _with_id(_adj("cameron2020.extraction_bdf::gate_cameron_conservation"), "::g")
    bad["component_evidence_strength"] = "controlled_independent"
    assert any("!= live registry" in p for p in EG.reconcile(links=EG.load_links() + [bad]))


def test_guard_placeholder_rejected():
    bad = _with_id(_adj("cameron2020.extraction_bdf::gate_cameron_conservation"), "::g")
    bad["caveat"] = "TODO write this"
    assert any("placeholder" in p for p in EG.reconcile(links=EG.load_links() + [bad]))


def test_guard_bad_dataset_id():
    bad = _with_id(_adj("liang2021.desorption::gate_liang_kemax_refit"), "::g")
    bad["sources"][0]["dataset_manifest_ids"] = ["not/a/real/dataset"]
    assert any("not in MANIFEST" in p for p in EG.reconcile(links=EG.load_links() + [bad]))


def test_semantic_corrections_applied():
    links = {l["link_id"]: l for l in EG.load_links()}
    # #1 infiltration: same fixture fits and evaluates -> NOT within_campaign_held_out
    inf = links["foster2025.infiltration::gate_infiltration_triangle"]
    assert inf["relationship"] == "same_campaign_not_held_out"
    assert inf["evidence_strength"] == "sign_or_compatibility"     # not the registry's controlled_independent
    assert inf["component_evidence_strength"] == "controlled_independent"
    # #2 composition diagnostic: residual-based, not pure code verification
    comp = links["brewer2026.coupled_kappa_t::gate_kappa_t_composition_diagnostic"]
    assert comp["evidence_strength"] == "exploratory_synthesis"
    assert comp["relationship"] == "post_fit_same_data"
    # #3 waszkiewicz static refit: tier and relationship aligned
    ws = links["waszkiewicz2025.poroelastic::gate_waszkiewicz_static_refit"]
    assert ws["evidence_strength"] == "post_fit_reconstruction"
    assert ws["relationship"] == "post_fit_same_data"


def test_kappa_t_degeneracy_splits_into_two_links():
    links = [l for l in EG.load_links() if l["gate"] == "gate_kappa_t_degeneracy"]
    assert len(links) == 2
    rels = {l["evidence_strength"] for l in links}
    assert "code_verification" in rels and "post_fit_reconstruction" in rels


def test_sources_use_manifest_provenance_not_name_prefix():
    # g10 intersource pulls three DISTINCT source papers (not the component-name prefix)
    l = next(l for l in EG.load_links()
             if l["link_id"] == "sourcing2026.g10_liquor_rheology::gate_g10_intersource_spread")
    cards = {s["source_card"] for s in l["sources"]}
    assert {"khomyakov2020", "telisromero2001", "telisromero2000"} <= cards


def test_generation_is_deterministic_and_bannered():
    import json
    a = EG.generate()
    assert a == EG.generate()
    expected = {"evidence_graph_matrix.csv", "evidence_graph_matrix.md", "evidence_graph.json",
                "evidence_graph_summary.json", "paper3_priority_evidence_matrix.md",
                "evidence_adjudication_queue.md", "evidence_conflicts.md"}
    assert set(a) == expected
    for content in a.values():
        assert "GENERATED" in content
        assert "timestamp" not in content.lower()
    summary = json.loads(a["evidence_graph_summary.json"])
    assert summary["paper3_scope_strict_clean"] is True
    assert summary["n_asserted_paper3_claims"] == summary["n_asserted_paper3_admissible"]


def test_generated_artifacts_stale_then_fresh(tmp_path):
    EG.write(root=tmp_path)
    assert EG.verify(root=tmp_path) == []
    target = tmp_path / EG.GENERATED_REL / "evidence_graph_matrix.md"
    target.write_text(target.read_text() + "\nHAND EDIT\n", encoding="utf-8")
    assert "evidence_graph_matrix.md" in EG.verify(root=tmp_path)


def test_priority_gates_are_adjudicated():
    # PR C acceptance: the 7 priority gates are honestly resolved (paper3 strict already green)
    priority = {
        "gate_g10_telisromero_full_table", "gate_g10_telisromero2000_thermal",
        "gate_g10_viscosity_bulk_negligible", "gate_g3_pump_envelope_bounds_quadratic",
        "gate_foster_fig15_flowmin", "gate_mo2_swelling_flow_decay", "gate_inertial_de1_audit",
    }
    by_gate = {l["gate"]: l for l in EG.load_links()}
    for g in priority:
        assert by_gate[g]["adjudication_status"] == "ADJUDICATED", g
        assert by_gate[g]["evidence_strength"] in EG.EVIDENCE_STRENGTHS
        assert by_gate[g]["sources"] is not None
    # the two reality-facing asserted results must be admissible (release-gated)
    assert by_gate["gate_g10_viscosity_bulk_negligible"]["support_status"] == "admissible"
    assert by_gate["gate_inertial_de1_audit"]["support_status"] == "admissible"


def test_conflicts_report_surfaces_constants_and_infiltration():
    md = EG.generate()["evidence_conflicts.md"]
    assert "c_sat" in md and "212.4" in md and "224" in md and "170" in md
    assert "controlled_independent" in md            # the infiltration tier discrepancy note
