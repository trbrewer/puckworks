"""WP2.4 — the Paper-3 per-claim evidence graph: reconciliation against the LIVE registry,
the integrity guards that forbid promoting a claim's tier by inference or mislabelling
code/source-curve checks as empirical/independent, deterministic generated artifacts, and the
draft-vs-strict CI contract.
"""
import copy
import json

from puckworks.paper3 import evidence_graph as EG


def test_draft_reconcile_is_clean():
    # the committed EVIDENCE_LINKS.json must reconcile with the registry in DRAFT mode
    assert EG.reconcile() == []


def test_every_registry_wiring_is_covered_and_no_orphans():
    links = EG.load_links()
    wirings, _ = EG.registry_gate_wirings()
    covered = {(l["component"], l["gate"]) for l in links}
    assert set(wirings) <= covered                      # bijection: no missing wiring
    assert covered <= set(wirings)                      # ...and no orphan links
    # bootstrap now finds nothing to add (graph is complete)
    assert EG.bootstrap_missing() == []


def test_bootstrap_never_infers_a_tier():
    # a fresh bootstrap of an empty graph must leave every per-gate tier BLANK and unadjudicated
    drafts = EG.bootstrap_missing(links=[])
    assert drafts, "expected draft skeletons for the live wirings"
    for d in drafts:
        assert d["adjudication_status"] == "NEEDS_ADJUDICATION"
        assert d["evidence_strength"] is None           # never promoted by automation
        assert d["claim"] is None and d["observable"] is None
        # the component's declared tier is carried only as context, clearly separate
        assert d["component_evidence_strength"] is not None


def test_strict_mode_fails_while_drafts_remain():
    links = EG.load_links()
    n_draft = sum(1 for l in links if l["adjudication_status"] == "NEEDS_ADJUDICATION")
    problems = EG.reconcile(strict=True)
    if n_draft:
        assert any("STRICT" in p for p in problems)
    else:
        assert problems == []                           # fully adjudicated -> strict is clean


def test_adjudicated_links_are_complete():
    for l in EG.load_links():
        if l["adjudication_status"] != "ADJUDICATED":
            continue
        for f in EG._REQUIRED_WHEN_ADJUDICATED:
            assert l.get(f) not in (None, "", []), "%s missing %s" % (l["link_id"], f)
        assert l["dataset_ids"] is not None             # [] allowed, null not
        assert l["evidence_strength"] in EG.EVIDENCE_STRENGTHS
        assert l["independence"] in EG.INDEPENDENCE_KINDS


def _adjudicated_example():
    """A minimal VALID adjudicated link built on a real wiring, for guard tests to mutate."""
    wirings, _ = EG.registry_gate_wirings()
    comp, gate = ("cameron2020.extraction_bdf", "gate_cameron_conservation")
    assert (comp, gate) in wirings
    return {
        "link_id": comp + "::" + gate, "component": comp, "gate": gate,
        "card": "cameron2020", "claim": "mass is conserved in the solver",
        "observable": "EY mass-budget residual", "source_cards": ["cameron2020"],
        "dataset_ids": [], "dataset_role": {},
        "independence": "code_verification", "evidence_strength": "code_verification",
        "component_evidence_strength": "code_verification",
        "caveat": "self-consistency only", "claim_not_supported": "no empirical match",
        "conflict_note": None, "adjudication_status": "ADJUDICATED",
    }


def test_guard_code_verification_cannot_be_empirical():
    bad = _adjudicated_example()
    bad["independence"] = "post_fit_reconstruction"     # code check mislabelled as empirical
    problems = EG.reconcile(links=EG.load_links() + [_orphan_free(bad)])
    assert any("code/conservation check is not empirical" in p for p in problems)


def test_guard_source_curve_not_independent():
    bad = _adjudicated_example()
    bad["evidence_strength"] = "source_curve_reproduction"
    bad["independence"] = "independent"                 # forbidden combination
    problems = EG.reconcile(links=EG.load_links() + [_orphan_free(bad)])
    assert any("may not be labelled independent" in p for p in problems)


def test_guard_post_fit_cannot_be_top_tier():
    bad = _adjudicated_example()
    bad["independence"] = "post_fit_reconstruction"
    bad["evidence_strength"] = "controlled_independent"
    problems = EG.reconcile(links=EG.load_links() + [_orphan_free(bad)])
    assert any("post-fit reconstruction cannot be tier" in p for p in problems)


def _orphan_free(link):
    """Give an extra test link a distinct id so only the guard (not duplicate/orphan) fires."""
    link = copy.deepcopy(link)
    link["link_id"] = link["link_id"] + "::guardtest"
    return link


def test_bad_dataset_id_is_rejected():
    bad = _adjudicated_example()
    bad["dataset_ids"] = ["not/a/real/dataset"]
    bad["dataset_role"] = {"not/a/real/dataset": "eval"}
    problems = EG.reconcile(links=EG.load_links() + [_orphan_free(bad)])
    assert any("not in MANIFEST" in p for p in problems)


def test_generation_is_deterministic_and_bannered():
    a = EG.generate()
    b = EG.generate()
    assert a == b
    expected = {"evidence_graph_matrix.csv", "evidence_graph_matrix.md",
                "evidence_graph.json", "evidence_adjudication_queue.md",
                "evidence_conflicts.md"}
    assert set(a) == expected
    for content in a.values():
        assert "GENERATED" in content                   # banner present
        assert "timestamp" not in content.lower()
    doc = json.loads(a["evidence_graph.json"])
    assert doc["content_sha256"] == json.loads(EG.generate()["evidence_graph.json"])["content_sha256"]


def test_generated_artifacts_verify(tmp_path):
    EG.write(root=tmp_path)
    assert EG.verify(root=tmp_path) == []
    target = tmp_path / EG.GENERATED_REL / "evidence_graph_matrix.md"
    target.write_text(target.read_text() + "\nHAND EDIT\n", encoding="utf-8")
    assert "evidence_graph_matrix.md" in EG.verify(root=tmp_path)


def test_kappa_t_degeneracy_splits_into_two_links():
    links = [l for l in EG.load_links() if l["gate"] == "gate_kappa_t_degeneracy"]
    assert len(links) >= 2, "gate_kappa_t_degeneracy must be split into >=2 claim links"
    assert len({l["link_id"] for l in links}) == len(links)   # distinct link_ids


def test_conflicts_report_surfaces_constants():
    md = EG.generate()["evidence_conflicts.md"]
    assert "c_sat" in md                                # the un-reconciled saturation constant
    assert "212.4" in md and "224" in md and "170" in md
