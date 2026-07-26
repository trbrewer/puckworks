"""Paper 3 MC15 — curated-corpus method and denominators (plus the U7 protocol table).

MC15's core sentence: "Twenty-five components do not represent 25 independent studies or 25
independent bodies of evidence. The generated summary should make this impossible to misread."
These tests hold the generated summary to that standard — the denominators must be derived, must
disagree with the component count, and the manuscript prose must not drift from them.
"""
import json

import pytest

import puckworks.models  # noqa: F401  (registers components)
from puckworks import registry as R
from puckworks.paper3 import corpus as C


@pytest.fixture(scope="module")
def d():
    return C.denominators()


def test_the_component_count_matches_the_live_registry(d):
    assert d["n_components"] == len(R.components())


def test_components_outnumber_their_source_publications(d):
    """THE POINT OF MC15. If these were equal, the corpus really would be one study per component
    and the whole denominator discussion would be unnecessary — so a reader could not misread it.
    They are not equal, and the ratio is what the manuscript must state."""
    assert d["n_unique_source_publications"] < d["n_components"], (
        d["n_unique_source_publications"], d["n_components"])
    assert d["components_per_publication"] > 1.0


def test_independent_evidence_is_a_minority_and_is_derived(d):
    """The sharper denominator: most components rest on a reconstruction of their own source's
    output rather than on anything independent of it."""
    assert d["n_components_with_independent_evidence"] < d["n_components"]
    strengths = {c.evidence_strength for c in R.components()}
    reconstruction_like = {"post_fit_reconstruction", "source_curve_reproduction",
                           "qualitative_capacity", "exploratory_synthesis"}
    assert reconstruction_like & strengths, (
        "no reconstruction-class evidence in the registry — re-derive this denominator")
    expected = sum(1 for c in R.components()
                   if c.evidence_strength not in reconstruction_like)
    assert d["n_components_with_independent_evidence"] == expected


def test_all_the_denominators_the_review_asked_for_are_reported(d):
    for key in ("n_unique_source_publications", "n_unique_dataset_sources", "n_manifest_records",
                "components_by_provenance_class", "components_by_evidence_relation",
                "n_components_with_independent_evidence", "n_rights_or_data_blocked",
                "n_calibration_only", "n_reference_only"):
        assert key in d, key


def test_project_created_components_are_counted_separately(d):
    """A project_synthesis component counted alongside published ports would inflate the apparent
    literature base with our own work."""
    by_class = d["components_by_provenance_class"]
    assert "published_port" in by_class
    assert set(by_class) <= {"published_port", "project_model", "project_synthesis",
                             "reference_only"}, by_class
    assert sum(by_class.values()) == d["n_components"]


def test_the_method_covers_every_aspect_the_review_enumerated():
    for key in ("seed_papers", "sources_searched", "search_dates", "search_strings",
                "citation_tracing", "inclusion_rules", "exclusion_rules",
                "derivative_and_duplicate_handling", "language_limits",
                "inaccessible_and_rights_blocked", "project_vs_published",
                "response_to_interface_gaps"):
        assert key in C.CORPUS_METHOD, key
        assert len(C.CORPUS_METHOD[key]) > 40, f"{key} is a stub"


def test_the_method_does_not_claim_to_be_systematic():
    """MC15 accepts a curated corpus; it does not accept one dressed up as systematic."""
    status = C.CORPUS_METHOD["status"]
    assert "not systematic" in status.lower()
    assert "no indexed database search has been executed" in status.lower()
    blob = " ".join(C.CORPUS_METHOD.values()).lower()
    assert "exhaustive" not in blob, "the method claims exhaustiveness somewhere"


def test_the_protocol_table_records_what_was_not_evaluated():
    """U7. The coarse particle class has no published radius; the table must say so rather than
    quietly omitting the row or substituting a value."""
    rows = {name: (value, why) for name, value, why in C.PROTOCOL_CHOICES}
    assert "Coarse particle class" in rows
    assert "not evaluated" in rows["Coarse particle class"][0].lower()
    assert "Integration horizon" in rows and "Initial condition" in rows


def test_generated_artifacts_and_the_manuscript_block_are_fresh():
    assert C.verify() == []


def test_the_manuscript_prose_agrees_with_the_generated_counts(d):
    """Generated table beside hand-written prose is only an improvement if they agree."""
    raw = C.MANUSCRIPT.read_text(encoding="utf-8")
    # reflow- and markup-insensitive: line wrapping and bold markers must not break this
    text = " ".join(raw.replace("**", "").split())
    claim = (f"{d['n_components']} components derive from "
             f"{d['n_unique_source_publications']} source publications, and only "
             f"{d['n_components_with_independent_evidence']} of the {d['n_components']} carry "
             f"evidence beyond a reconstruction")
    assert claim in text, f"prose does not state the generated counts; expected: {claim!r}"


def test_the_staleness_guard_is_not_vacuous(tmp_path, monkeypatch):
    import shutil
    copy = tmp_path / "draft.md"
    shutil.copy(C.MANUSCRIPT, copy)
    text = copy.read_text(encoding="utf-8")
    copy.write_text(text.split(C._BEGIN)[0] + C._BEGIN + "\ntampered\n" + C._END
                    + text.split(C._END, 1)[1], encoding="utf-8")
    monkeypatch.setattr(C, "MANUSCRIPT", copy)
    assert "STALE" in C.splice(write_it=False)


def test_the_json_is_machine_readable():
    payload = json.loads(C.DENOM_JSON.read_text(encoding="utf-8"))
    assert payload["n_components"] and payload["components_by_evidence_relation"]
