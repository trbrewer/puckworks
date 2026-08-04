"""Insight Foundry structural integrity (blueprint §18.1).

The Foundry needs structural correctness, not candidate governance: these tests check that the
overlay never becomes an authority, never promotes an evidence label, never emits a verdict, and
never lets a generated artifact drift from the tree. They do NOT check that any candidate is a
good idea — that is human triage, and asserting it here would be the layer scoring its own output.
"""
import copy
import json
import re
import subprocess
import sys
from pathlib import Path

import pytest

from puckworks import registry as R
from puckworks.insights import (corpus_map as CM, export as EX, extract as X,
                                ids as IDS, schema as S, tension_atlas as TA)

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


def test_tension_ids_are_unique_and_registry_backed(state):
    # IDs are NOT sort positions any more — they come from the fingerprint registry, so they are
    # unique and well-formed but deliberately not in ascending order down the sorted atlas
    ids = [t.tension_id for t in state["tensions"]]
    assert len(set(ids)) == len(ids)
    assert all(re.fullmatch(r"T-\d{4}", i) for i in ids)
    reg = IDS.load()
    for t in state["tensions"]:
        assert reg["tensions"].get(IDS.tension_fingerprint(t)) == t.tension_id


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


def test_candidate_ids_are_unique_and_registry_backed(state):
    # not dense: a retired candidate keeps its number for good, so gaps are correct and expected
    ids = [c.id for c in state["candidates"]]
    assert len(set(ids)) == len(ids)
    reg = IDS.load()
    for c in state["candidates"]:
        fp = IDS.candidate_fingerprint(c.lens, c.difference_type, c.grouping_key)
        assert reg["candidates"].get(fp) == c.id


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


#: The Project pack contract: exactly these twelve names, in this order.
EXPECTED_PACK = [
    "01_INSIGHT_SNAPSHOT.md", "02_corpus_map.json", "03_tension_atlas.csv",
    "04_candidate_portfolio.md", "05_candidate_portfolio.json",
    "06_evidence_lineage_index.csv", "07_model_observable_matrix.csv",
    "08_closure_portability_index.csv", "09_public_claim_inventory.md",
    "10_PROJECT_INSTRUCTIONS.md", "11_CHAT_PROMPTS.md", "12_SOURCE_MANIFEST.json",
]


def test_the_pack_is_exactly_the_twelve_contract_files():
    names = [n for n, _ in EX.PACK] + [EX.PACK_MANIFEST_NAME]
    assert names == EXPECTED_PACK
    # a ChatGPT Pro Project takes 40 files (blueprint §14.1); twelve leaves ample headroom
    assert len(names) <= 40
    tracked = {rel for rel, _ in EX.ARTIFACTS} | {
        "docs/insights/chatgpt_project/PROJECT_INSTRUCTIONS.md",
        "docs/insights/chatgpt_project/CHAT_PROMPTS.md"}
    for _, src in EX.PACK:
        assert src in tracked, "%s is not a tracked file" % src


def test_every_pack_file_referenced_by_the_project_instructions_exists():
    """A Project instruction naming a file the pack does not contain sends a chat looking for
    something that was never uploaded."""
    referenced = set()
    for rel in ("docs/insights/chatgpt_project/PROJECT_INSTRUCTIONS.md",
                "docs/insights/chatgpt_project/CHAT_PROMPTS.md"):
        text = (_ROOT / rel).read_text(encoding="utf-8")
        referenced |= set(re.findall(r"\b\d{2}_[A-Za-z0-9_]+", text))
    assert referenced, "expected the instructions to name pack files"
    packed_stems = {n.rsplit(".", 1)[0] for n in EXPECTED_PACK}
    for ref in sorted(referenced):
        assert ref in packed_stems or ref in EXPECTED_PACK, \
            "Project instructions reference %r, which is not in the pack" % ref


def test_source_manifest_binds_every_packed_file_to_a_path_and_hash(state):
    man = json.loads(EX.pack_source_manifest(state))
    assert man["corpus_source_commit"] == state["corpus"]["commit"]
    assert man["file_count"] == len(EXPECTED_PACK)
    entries = {f["packed_as"]: f for f in man["files"]}
    assert sorted(entries) == sorted(EXPECTED_PACK)
    for name, _src in EX.PACK:
        e = entries[name]
        assert e["present"], "%s has no source file" % name
        assert re.fullmatch(r"[0-9a-f]{64}", e["sha256"]), name
        assert (_ROOT / e["source_path"]).exists()
        # the hash must be the source file's actual content hash
        assert e["sha256"] == S.sha256_path(_ROOT / e["source_path"])


def test_pack_manifest_records_the_renamed_portability_index():
    """The packed name is `08_closure_portability_index.csv` by contract, but its source is the
    renamed calibration-artifact index — the manifest is what makes that mapping followable."""
    entry = dict(EX.PACK)["08_closure_portability_index.csv"]
    assert entry.endswith("calibration_artifact_portability_index.csv")


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


# ---- stable identity ---------------------------------------------------------------------------


def _synthetic_tension(entity_id="model:aaa_synthetic_probe", dtype="synthetic_probe"):
    """A tension row that sorts FIRST in the atlas.

    The sort key is `(lens, entity_ids, difference_summary)`, so sorting first needs the
    alphabetically first implemented lens AND an entity id below every real one — this is the
    adversarial case for positional IDs, and it has to actually be adversarial to prove anything.
    """
    return S.Tension(
        tension_id="", lens="calibration_artifact_portability", entity_ids=(entity_id,),
        difference_type=dtype, canonical_discriminator="synthetic",
        difference_summary="AAA synthetic probe row that sorts before every real row",
        provenance=(S.Provenance(source_path="puckworks/registry.py", source_locator="probe"),))


def test_inserting_an_early_sorting_tension_does_not_renumber_existing_ids(state):
    """The defect this registry exists to prevent: a new row that sorts first must NOT shift the
    number of every row after it. `T-0042` is quoted in decision records and screen bundles."""
    before = {IDS.tension_fingerprint(t): t.tension_id for t in state["tensions"]}
    high_before = IDS.load()["high_water"]["T"]

    alloc = IDS.Allocator()
    probe = _synthetic_tension()
    rows = sorted([probe] + list(state["tensions"]),
                  key=lambda t: (t.lens, tuple(t.entity_ids), t.difference_summary))
    assert rows[0] is probe, "the probe must sort first for this test to be meaningful"

    assigned = {}
    for t in rows:
        assigned[IDS.tension_fingerprint(t)] = alloc.tension_id(t)

    for fp, old_id in before.items():
        assert assigned[fp] == old_id, "row %s was renumbered to %s" % (old_id, assigned[fp])
    probe_id = assigned[IDS.tension_fingerprint(probe)]
    assert probe_id == "T-%04d" % (high_before + 1), probe_id
    # the in-memory allocation must not have touched the tracked registry
    assert IDS.load()["high_water"]["T"] == high_before


def test_inserting_an_early_sorting_candidate_does_not_renumber_existing_ids(state):
    before = {IDS.candidate_fingerprint(c.lens, c.difference_type, c.grouping_key): c.id
              for c in state["candidates"]}
    high_before = IDS.load()["high_water"]["I"]
    alloc = IDS.Allocator()
    # "aaa" sorts before every real grouping key in every real lens
    new_id = alloc.candidate_id("calibration_artifact_portability", "calibration_artifact_producer",
                                ("aaa_synthetic",))
    assert new_id == "I-%03d" % (high_before + 1)
    for fp, old_id in before.items():
        assert alloc.registry["candidates"][fp] == old_id


def test_an_id_is_never_reused_after_its_record_disappears():
    reg = {"registry_version": 1, "high_water": {"T": 7, "I": 3},
           "tensions": {"deadfp": "T-0007"}, "candidates": {}}
    alloc = IDS.Allocator(reg)
    fresh = alloc.tension_id(_synthetic_tension())
    assert fresh == "T-0008", "a retired number must not be handed to a different record"
    # the retired entry survives, so if its record ever returns it gets its ORIGINAL id back
    assert alloc.registry["tensions"]["deadfp"] == "T-0007"


def test_identity_is_wording_invariant(state):
    """Rewriting a row's prose must not mint a new ID — otherwise every editorial improvement
    silently breaks persistent references."""
    t = state["tensions"][0]
    fp = IDS.tension_fingerprint(t)
    reworded = copy.copy(t)
    reworded.difference_summary = "completely different prose describing the same two entities"
    reworded.evidence_basis = "rewritten"
    reworded.why_it_matters = "rewritten"
    reworded.candidate_discriminator = "rewritten prose discriminator"
    assert IDS.tension_fingerprint(reworded) == fp


def test_identity_changes_when_the_entities_change(state):
    """The converse guard: a row about a different entity set is a different row, and must not
    inherit the old row's ID."""
    t = state["tensions"][0]
    moved = copy.copy(t)
    moved.entity_ids = tuple(list(t.entity_ids) + ["model:cameron2020.extraction_bdf"])
    assert IDS.tension_fingerprint(moved) != IDS.tension_fingerprint(t)


def test_registry_is_tracked_and_covers_the_current_corpus(state):
    assert (_ROOT / IDS.REGISTRY_REL).exists(), "the registry must be a tracked file"
    assert IDS.unrecorded(state) == []
    reg = IDS.load()
    assert reg["high_water"]["T"] >= len(state["tensions"])
    assert reg["high_water"]["I"] >= len(state["candidates"])


#: The seed watermark: the highest ID assigned before the correction pass (head e8054b3).
#: Anything at or below it was seeded; anything above was minted by this pass.
SEED_HIGH_WATER = {"T": 170, "I": 89}


def test_no_id_is_ever_shared_by_two_records():
    """The injectivity invariant that makes a stale reference safe: an ID resolves to the record
    it always meant, or to nothing — never to a DIFFERENT record."""
    reg = IDS.load()
    for bucket in ("tensions", "candidates"):
        ids = list(reg[bucket].values())
        dupes = {i for i in ids if ids.count(i) > 1}
        assert not dupes, "%s ids bound to more than one fingerprint: %s" % (bucket,
                                                                            sorted(dupes))


def test_the_seeded_ids_from_the_previous_head_survived(state):
    """The correction pass renamed two families, which changes sort order. Every ID assigned
    before it must still point at the record it always meant — that is what the registry was
    seeded to guarantee, and renaming a family must not have quietly reshuffled the numbering."""
    live_t = {t.tension_id for t in state["tensions"]}
    seeded_t = {i for i in live_t if int(i.split("-")[1]) <= SEED_HIGH_WATER["T"]}
    # the foster2025 card repair legitimately retired a handful of rows; the rest must survive
    assert len(seeded_t) >= SEED_HIGH_WATER["T"] - 10, len(seeded_t)

    live_i = {c.id for c in state["candidates"]}
    seeded_i = {i for i in live_i if int(i.split("-")[1]) <= SEED_HIGH_WATER["I"]}
    assert len(seeded_i) >= SEED_HIGH_WATER["I"] - 10, len(seeded_i)

    # and every newly minted ID is strictly above the seed watermark, never slotted into a gap
    for i in live_t - seeded_t:
        assert int(i.split("-")[1]) > SEED_HIGH_WATER["T"], i
    for i in live_i - seeded_i:
        assert int(i.split("-")[1]) > SEED_HIGH_WATER["I"], i


# ---- semantics guards --------------------------------------------------------------------------


def test_no_row_calls_a_same_stage_neighbour_an_established_consumer(state):
    """Sharing a stage is co-location. No output-to-input path was traced, so no generated text
    may assert one."""
    banned = ("runtime consumers on the same stage", "consumers on the same stage",
              "established consumer", "consuming components:")
    for t in state["tensions"]:
        blob = " ".join([t.difference_summary, t.evidence_basis, t.why_it_matters,
                         t.candidate_discriminator]).lower()
        for phrase in banned:
            assert phrase not in blob, "%s asserts a consuming relationship: %r" % (t.tension_id,
                                                                                   phrase)


def test_calibration_rows_declare_downstream_as_possible_not_established(state):
    rows = [t for t in state["tensions"]
            if t.difference_type == "calibration_artifact_producer"]
    assert rows, "expected calibration-artifact rows"
    for t in rows:
        assert "POSSIBLE DOWNSTREAM" in t.difference_summary, t.tension_id
        assert "NOT established" in t.difference_summary, t.tension_id
        # a screen is not cheap until a path is shown to exist
        assert t.cheap_test_possible in ("UNKNOWN", "NO"), (t.tension_id, t.cheap_test_possible)


def test_the_calibration_screen_checks_the_path_before_swapping(state):
    cands = [c for c in state["candidates"]
             if c.difference_type == "calibration_artifact_producer"]
    assert cands
    for c in cands:
        assert "Step 1" in c.cheap_test and "establish the path" in c.cheap_test, c.id
        assert c.cheap_test.index("Step 1") < c.cheap_test.index("Step 2"), c.id
        assert "consuming path" in c.inconclusive_if.lower(), c.id


def test_the_word_closure_is_not_applied_to_every_calibration_component(state):
    """`execution_role == \'calibration\'` covers lookup tables, geometry generators and
    verification twins as well as closures, so the FOUNDRY\'s own framing must not call them all
    closures.

    Two sources of the word are exempt and must stay exactly as written: a component NAME
    (`maille2024.phi_closure`, `pannusch2024.closures`) and a verbatim registry `valid_range`
    (`sourcing2026.g10_liquor_rheology` declares "closures reproduce..."). Rewriting either would
    be the label-tampering this whole layer forbids — the test targets the sentences the Foundry
    itself writes.
    """
    rows = [t for t in state["tensions"]
            if t.difference_type == "calibration_artifact_producer"]
    assert rows
    for t in rows:
        assert "closure" not in t.why_it_matters.lower(), t.tension_id
        assert "closure" not in t.evidence_basis.lower(), t.tension_id
        assert "is a calibration component on stage" in t.difference_summary, t.tension_id
        for phrase in ("is a closure", "the closure is", "closure fitted", "closure producer"):
            assert phrase not in t.difference_summary.lower(), (t.tension_id, phrase)


def test_no_row_asserts_a_same_source_pair_is_base_plus_mechanism(state):
    """Sharing a source prefix does not make two components a base/superset pair."""
    rows = [t for t in state["tensions"]
            if t.difference_type == "same_source_pair_requires_composition_audit"]
    assert rows, "expected same-source pair rows"
    for t in rows:
        assert "RELATIONSHIP is unclassified" in t.difference_summary, t.tension_id
        blob = t.difference_summary.lower()
        for phrase in ("where one adds a mechanism", "base plus mechanism",
                       "one a superset", "the addition helps"):
            assert phrase not in blob, "%s presumes a base/superset pair: %r" % (t.tension_id,
                                                                                phrase)


def test_the_composition_screen_classifies_before_comparing(state):
    cands = [c for c in state["candidates"]
             if c.difference_type == "same_source_pair_requires_composition_audit"]
    assert cands
    for c in cands:
        assert "Step 1" in c.cheap_test and "classify" in c.cheap_test.lower(), c.id
        assert "ONLY for confirmed base/superset" in c.cheap_test, c.id
        assert c.cheap_test.index("Step 1") < c.cheap_test.index("Step 2"), c.id


def test_the_pv05_generalisation_candidate_is_preserved(state):
    """The published composition failure is separately evidence-backed and must not be folded
    into the unclassified same-source family."""
    published = [t for t in state["tensions"]
                 if t.difference_type == "published_composition_failure"]
    assert len(published) == 1, "expected exactly the one published PV-05 case"
    assert "PV-05" in published[0].difference_summary
    cands = [c for c in state["candidates"]
             if c.difference_type == "published_composition_failure"]
    assert len(cands) == 1 and "generalise" in cands[0].title.lower()


def test_the_portability_index_uses_calibration_not_closure_column_names(state):
    header = EX.render_calibration_artifact_index(state).splitlines()[0]
    assert "calibration_component" in header
    assert "possible_downstream_same_stage" in header
    assert "consuming_path_established" in header
    assert "closure_component" not in header
    assert "runtime_consumers_same_stage" not in header


# ---- the foster2025 first-drip repair ------------------------------------------------------------


def test_foster_card_now_exposes_first_drip_time(corpus):
    """The card gap that made the blueprint's flagship candidate invisible to the matrix."""
    preds = {r["source"] for r in CM.relations_of(corpus, "PREDICTS")
             if r["target"] == "observable:first_drip_time"}
    assert preds == {"model:foster2025.infiltration", "model:foster2025.machine_mode"}, preds
    header, rows = CM.model_observable_matrix(corpus)
    col = header.index("first_drip_time")
    by_model = {r[0]: r[col] for r in rows}
    assert by_model["foster2025.infiltration"] == "predicts"
    assert by_model["foster2025.machine_mode"] == "predicts"


def test_the_first_drip_blind_spot_rows_are_gone(state):
    """The card fix must actually retire the rows that reported the gap."""
    for t in state["tensions"]:
        if t.difference_type == "measured_but_unmodelled":
            assert t.shared_observable != "first_drip_time", t.tension_id
        if t.difference_type == "card_without_interface_mapping":
            assert "foster2025" not in t.difference_summary, t.tension_id


def test_first_drip_is_now_a_discriminator_with_data(state):
    rows = [t for t in state["tensions"]
            if t.difference_type == "discriminator_with_data"
            and t.shared_observable == "first_drip_time"]
    assert len(rows) == 1, "the flagship discriminator should be exactly one row"
    assert rows[0].data_available == "YES"


def test_foster_interface_mapping_claims_only_supported_outputs():
    """The added section must stay inside what the card and implementation support — no `flow`,
    `tds` or `extraction_yield` smuggled into a narrowly scoped repair."""
    parts = X.split_interface_mapping(X.card_sections("foster2025")["Interface mapping"])
    assert parts["has_outputs_marker"]
    produced = set(X.observables_in_text(parts["outputs"]))
    assert produced == {"first_drip_time", "wetting_front"}, produced
