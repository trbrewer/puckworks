"""Insight Foundry structural integrity (blueprint §18.1).

The Foundry needs structural correctness, not candidate governance: these tests check that the
overlay never becomes an authority, never promotes an evidence label, never emits a verdict, and
never lets a generated artifact drift from the tree. They do NOT check that any candidate is a
good idea — that is human triage, and asserting it here would be the layer scoring its own output.
"""
import json
import re
import subprocess
import sys
from pathlib import Path

import pytest

from puckworks import registry as R
from puckworks.insights import (corpus_map as CM, export as EX,
                                extract as X, schema as S, tension_atlas as TA)

_ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture(scope="module")
def state():
    return EX.build_all()


@pytest.fixture(scope="module")
def corpus(state):
    return state["corpus"]


# ---- provenance and resolution ------------------------------------------------------------


def test_every_entity_carries_a_source_path_and_commit(corpus):
    for e in corpus["entities"]:
        p = e["provenance"]
        assert p["source_path"], "entity %s has no source_path" % e["id"]
        assert p["source_commit"] == corpus["commit"], \
            "entity %s is pinned to a different commit" % e["id"]


def test_every_relation_carries_provenance_and_a_valid_confidence(corpus):
    for r in corpus["relations"]:
        assert r["type"] in S.RELATION_TYPES
        p = r["provenance"]
        assert p["source_path"], "relation %s has no source_path" % r
        assert p["confidence"] in S.RELATION_CONFIDENCES


def test_no_dangling_relations(corpus):
    ids = {e["id"] for e in corpus["entities"]}
    for r in corpus["relations"]:
        assert r["source"] in ids and r["target"] in ids, "dangling relation %s" % r


def test_every_model_id_resolves_to_the_live_registry(corpus):
    R.load_builtin_components()
    live = {c.name for c in R.components()}
    got = {e["label"] for e in CM.entities_of(corpus, "model")}
    assert got == live


def test_every_dataset_id_resolves_to_the_manifest(corpus):
    import csv
    with X.MANIFEST_PATH.open(newline="", encoding="utf-8") as fh:
        manifest = {(row["dataset_id"] or "").strip()
                    for row in csv.DictReader(fh) if (row["dataset_id"] or "").strip()}
    got = {e["label"] for e in CM.entities_of(corpus, "dataset")}
    assert got == manifest


def test_unresolved_cards_are_flagged_not_guessed(corpus):
    # a component whose card cannot be resolved carries card_path=None AND a build warning;
    # it must never be attached to a plausible-looking neighbour
    unresolved = [e for e in CM.entities_of(corpus, "model")
                  if e["attrs"]["card_resolution"] == "UNRESOLVED"]
    for e in unresolved:
        assert e["attrs"]["card_path"] is None
        assert any(e["label"] in w for w in corpus["warnings"] if w.startswith("UNRESOLVED_CARD"))
    for e in CM.entities_of(corpus, "model"):
        if e["attrs"]["card_path"]:
            assert (_ROOT / e["attrs"]["card_path"]).exists()


def test_source_card_resolution_refuses_ambiguity():
    stems = {"romancorrochano2017_extraction", "romancorrochano2017_permeability",
             "wadsworth2026_grindmap", "waszkiewicz2025"}
    # exact stem wins
    assert X.resolve_source_card("waszkiewicz2025", stems) == "waszkiewicz2025"
    # a two-card cell resolves to its first named card once the parenthetical is dropped
    assert X.resolve_source_card("wadsworth2026_grindmap / wadsworth2026 (one paper)",
                                 stems) == "wadsworth2026_grindmap"
    # a prefix with TWO candidate cards is ambiguous -> refuse, do not pick one
    assert X.resolve_source_card("romancorrochano2017", stems) is None
    # a cell naming no card at all
    assert X.resolve_source_card("(registry [RS])", stems) is None


# ---- the no-promotion rule ------------------------------------------------------------------


def test_model_evidence_strength_is_verbatim_from_the_live_registry(corpus):
    R.load_builtin_components()
    for e in CM.entities_of(corpus, "model"):
        live = R.get(e["label"])
        assert e["attrs"]["evidence_strength"] == live.evidence_strength
        assert e["attrs"]["valid_range"] == live.valid_range
        assert e["attrs"]["provenance_class"] == live.provenance_class


def test_dataset_validation_strength_is_verbatim_from_the_manifest(corpus):
    import csv
    with X.MANIFEST_PATH.open(newline="", encoding="utf-8") as fh:
        rows = {(r["dataset_id"] or "").strip(): r for r in csv.DictReader(fh)}
    for e in CM.entities_of(corpus, "dataset"):
        row = rows[e["label"]]
        assert e["attrs"]["validation_strength"] == (row["validation_strength"] or "").strip()
        assert e["attrs"]["caveat"] == (row["caveat"] or "").strip()


def test_assert_verbatim_rejects_a_reworded_label():
    with pytest.raises(S.SchemaError):
        S.assert_verbatim({"evidence_strength": "independent"}, "evidence_strength",
                          "independent within-rig (equilibrium) / post-fit")


def test_lineage_tags_are_additive_and_never_collapse_a_mixed_cell():
    mixed = "independent within-rig (equilibrium) / post-fit (9-bar Q(t) reproduction)"
    tags = S.derive_lineage_tags(mixed)
    assert "independent" in tags and "post_fit" in tags, tags
    assert "mixed_strength" in tags, "a cell naming two strengths must be marked mixed"
    # a single-strength cell is not marked mixed
    assert "mixed_strength" not in S.derive_lineage_tags("post-fit reconstruction")
    # nothing is invented for an unreadable cell
    assert S.derive_lineage_tags("") == ("unclassified",)


def test_every_derived_lineage_tag_is_in_the_vocabulary(corpus):
    for e in CM.entities_of(corpus, "dataset"):
        for t in e["attrs"]["lineage_tags"]:
            assert t in S.LINEAGE_TAGS


def test_observable_matrix_has_no_validation_cells(corpus):
    # the foundation knows what a card SAYS a component outputs; it has no evidence that a
    # component was VALIDATED on an observable, so no such cell may exist
    header, rows = CM.model_observable_matrix(corpus)
    values = {cell for row in rows for cell in row[3:]}
    assert values <= {"predicts", "-"}, values


# ---- discovery is not evidence ---------------------------------------------------------------


def test_llm_suggested_relations_may_not_drive_scoring():
    assert not S.scoring_admissible("llm_suggested")
    for c in ("explicit", "deterministically_inferred", "human_confirmed",
              "scientifically_tested"):
        assert S.scoring_admissible(c)
    with pytest.raises(S.SchemaError):
        S.scoring_admissible("invented_confidence")


def test_the_foundation_emits_no_llm_suggested_relations(corpus):
    assert not [r for r in corpus["relations"]
                if r["provenance"]["confidence"] == "llm_suggested"]


def test_typed_overlap_relations_only_where_the_card_says_so(corpus):
    # a COMPETES_WITH / COMPLEMENTS edge must quote a sentence containing its marker word; a
    # mention with no marker stays colourless
    for r in corpus["relations"]:
        if r["type"] not in ("COMPETES_WITH", "COMPLEMENTS"):
            continue
        quoted = (r["attrs"].get("quoted") or "").lower()
        markers = (X._COMPETES_MARKERS if r["type"] == "COMPETES_WITH"
                   else X._COMPLEMENTS_MARKERS)
        assert any(m in quoted for m in markers), \
            "%s edge %s->%s quotes no marker word" % (r["type"], r["source"], r["target"])


# ---- tension atlas ----------------------------------------------------------------------------


def test_every_tension_is_source_bound_and_unreviewed(state):
    for t in state["tensions"]:
        assert t.provenance, "%s carries no provenance" % t.tension_id
        for p in t.provenance:
            assert p.source_path
        assert t.entity_ids
        assert t.human_status == "UNREVIEWED", \
            "%s was pre-adjudicated by a lens" % t.tension_id
        assert t.lens in S.LENSES


def test_tension_ids_are_unique_and_ordered(state):
    ids = [t.tension_id for t in state["tensions"]]
    assert len(set(ids)) == len(ids)
    assert ids == sorted(ids)


def test_deferred_lenses_are_declared_not_silently_absent(state):
    implemented = {t.lens for t in state["tensions"]}
    for lens in ("observational_equivalence", "regime_transition"):
        assert lens not in implemented
        assert lens in TA.DEFERRED_LENSES and TA.DEFERRED_LENSES[lens]


def test_atlas_reaches_the_blueprint_phase_2_floor(state):
    # blueprint §16 Phase 2 acceptance: at least 50 source-bound rows
    assert len(state["tensions"]) >= 50


def test_disagreement_rows_claim_comparability_not_agreement(state):
    for t in state["tensions"]:
        if t.difference_type == "comparable_not_yet_executed":
            assert "NOT established" in t.difference_summary


# ---- candidates -------------------------------------------------------------------------------


def test_every_candidate_has_a_question_cheap_test_and_stop_condition(state):
    for c in state["candidates"]:
        assert c.question.strip() and c.cheap_test.strip() and c.stop_condition.strip()
        assert c.survive_if and c.retire_if and c.inconclusive_if
        assert re.fullmatch(r"I-\d{3}", c.id)


def test_the_generator_emits_seeds_only(state):
    for c in state["candidates"]:
        assert c.status == "SEED"
        assert c.status in S.GENERATOR_EMITTABLE_STATUSES


def test_generated_candidates_carry_no_scores(state):
    # scoring is a human triage aid applied AFTER a person reads the portfolio; a generator that
    # scored its own output would be an LLM score standing in for a scientific decision
    for c in state["candidates"]:
        assert c.scores == {}
        assert c.history == ()


def test_candidate_ids_are_unique_and_dense(state):
    ids = [c.id for c in state["candidates"]]
    assert len(set(ids)) == len(ids)
    assert ids == ["I-%03d" % i for i in range(1, len(ids) + 1)]


def test_every_candidate_binds_to_tensions_and_entities(state):
    tension_ids = {t.tension_id for t in state["tensions"]}
    entity_ids = {e["id"] for e in state["corpus"]["entities"]}
    for c in state["candidates"]:
        assert c.tension_ids and set(c.tension_ids) <= tension_ids
        assert c.entity_ids and set(c.entity_ids) <= entity_ids
        for track in c.audience_tracks:
            assert track in S.AUDIENCE_TRACKS


def test_every_tension_row_reaches_a_candidate(state):
    orphans = [t.tension_id for t in state["tensions"] if not t.candidate_id]
    assert not orphans, "tension rows with no candidate template: %s" % orphans[:10]


def test_candidate_status_vocabulary_rejects_an_invented_state():
    with pytest.raises(S.SchemaError):
        S.Candidate(id="I-001", title="t", question="q?", lens="model_disagreement",
                    tension_ids=("T-0001",), entity_ids=("model:x",), cheap_test="t",
                    stop_condition="s", status="PROBABLY_TRUE")


def test_a_candidate_without_a_stop_condition_is_rejected():
    with pytest.raises(S.SchemaError):
        S.Candidate(id="I-001", title="t", question="q?", lens="model_disagreement",
                    tension_ids=("T-0001",), entity_ids=("model:x",), cheap_test="t",
                    stop_condition="   ")


# ---- generated artifacts ------------------------------------------------------------------------


def test_generated_artifacts_are_in_sync_with_the_tree():
    problems = EX.verify()
    assert not problems, "\n".join(problems)


def test_the_build_is_deterministic():
    a = EX.generate_all(commit="FIXED")
    b = EX.generate_all(commit="FIXED")
    assert a == b


def test_no_wall_clock_timestamp_leaks_into_a_tracked_artifact():
    # a timestamp would make every regeneration a diff, which is what makes drift undetectable
    for rel, _ in EX.ARTIFACTS:
        text = (_ROOT / rel).read_text(encoding="utf-8")
        assert "generated_at" not in text, rel
    man = json.loads((_ROOT / (EX.GENERATED_REL + "/snapshot_manifest.json")).read_text())
    assert "generated_at" not in man


def test_snapshot_manifest_pins_one_commit_and_hashes_every_input():
    man = json.loads((_ROOT / (EX.GENERATED_REL + "/snapshot_manifest.json")).read_text())
    corpus = json.loads((_ROOT / (EX.GENERATED_REL + "/corpus_map.json")).read_text())
    assert man["commit"] == corpus["commit"]
    assert man["inputs"] and all(d["sha256"] and d["path"] for d in man["inputs"])
    assert man["outputs"] and all(d["sha256"] for d in man["outputs"])
    for rel, _ in EX.ARTIFACTS:
        assert any(o["path"] == rel for o in man["outputs"]), rel


def test_markdown_and_json_agree_on_the_candidate_count():
    portfolio = json.loads(
        (_ROOT / (EX.GENERATED_REL + "/candidate_portfolio.json")).read_text())
    md = (_ROOT / (EX.GENERATED_REL + "/candidate_portfolio.md")).read_text()
    n = portfolio["summary"]["total"]
    assert n == len(portfolio["candidates"])
    assert "**%d candidates, all `SEED`**" % n in md
    assert md.count("\n### I-") == n


def test_the_source_pack_stays_within_the_project_file_limit():
    # a ChatGPT Pro Project takes 40 files, 10 per upload (blueprint §14.1); the pack is the
    # reason the Project gets a generated snapshot instead of 100+ model cards
    assert len(EX.PACK) <= 10
    assert len({name for name, _ in EX.PACK}) == len(EX.PACK)
    tracked = {rel for rel, _ in EX.ARTIFACTS} | {
        "docs/insights/chatgpt_project/PROJECT_INSTRUCTIONS.md"}
    for _, src in EX.PACK:
        assert src in tracked, "%s is not a tracked artifact" % src


def test_verify_reports_drift_when_a_generated_file_is_hand_edited(tmp_path):
    target = _ROOT / (EX.GENERATED_REL + "/observable_index.csv")
    original = target.read_text(encoding="utf-8")
    try:
        target.write_text(original + "hand,edited,row\n", encoding="utf-8")
        problems = EX.verify()
        assert any(p.startswith("DRIFT") and "observable_index.csv" in p for p in problems), \
            problems
    finally:
        target.write_text(original, encoding="utf-8")
    assert not EX.verify()


def test_verify_reports_staleness_when_an_input_hash_moves(monkeypatch):
    real = CM._input_hashes

    def moved():
        out = [dict(d) for d in real()]
        out[0]["sha256"] = "0" * 64
        return out

    monkeypatch.setattr(CM, "_input_hashes", moved)
    problems = EX.verify()
    assert any(p.startswith("STALE") for p in problems), problems


# ---- the overlay never becomes an authority -------------------------------------------------


def test_the_foundry_writes_nothing_outside_its_own_directory():
    written = {rel for rel, _ in EX.ARTIFACTS} | {EX.GENERATED_REL + "/snapshot_manifest.json"}
    for rel in written:
        assert rel.startswith("docs/insights/"), rel


def test_registry_manifest_and_claims_are_untouched_by_a_build():
    authorities = ["puckworks/registry.py", "puckworks/data/MANIFEST.csv",
                   "docs/public/generated/claims.json"]
    before = {p: S.sha256_path(_ROOT / p) for p in authorities}
    EX.build_all()
    assert {p: S.sha256_path(_ROOT / p) for p in authorities} == before


def test_build_warnings_are_findings_not_failures(corpus):
    # the warnings are the point: unresolved cards, untraceable manifest cells, template
    # deviations. They must be reported, and each must name its subject.
    assert corpus["warnings"]
    prefixes = {w.split(":")[0] for w in corpus["warnings"]}
    assert prefixes <= {"UNRESOLVED_CARD", "TEMPLATE_DEVIATION", "MANIFEST_SOURCE_CARD_UNRESOLVED",
                        "NO_INTERFACE_MAPPING", "MISSING_MANIFEST", "MISSING_CLAIMS",
                        "MISSING_ANALYSIS", "CLAIM_DATASET_UNRESOLVED", "DANGLING_RELATION",
                        "MANIFEST_ROW_NO_ID"}, prefixes


def test_cli_build_and_verify_run_clean():
    for args in (["build"], ["verify"]):
        r = subprocess.run([sys.executable, "-m", "puckworks.insights"] + args,
                           capture_output=True, text=True, cwd=str(_ROOT))
        assert r.returncode == 0, r.stdout + r.stderr


def test_cli_card_materialises_one_shortlisted_candidate(tmp_path, monkeypatch, state):
    from puckworks.insights import cli
    card = state["candidates"][0]
    written = {}
    monkeypatch.setattr(Path, "write_text",
                        lambda self, text, **kw: written.update({str(self): text}))
    monkeypatch.setattr(Path, "mkdir", lambda self, **kw: None)
    assert cli.main(["card", card.id]) == 0
    (text,) = written.values()
    assert card.question in text
    assert "## Stop condition" in text and "## Decision rule" in text
    assert "SEED" in text
