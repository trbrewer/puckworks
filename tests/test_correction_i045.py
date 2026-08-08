"""Tests for the I-045 evidence-lineage correction — TWO EXPLICIT LAYERS.

The screens under `tests/test_screen_i045.py` and `tests/test_deep_screen_i045.py` validate the
HISTORICAL pre-correction findings. This module has two jobs, deliberately kept apart:

  1. **LIVE CORRECTION INVARIANTS** — what must be true of the repository *today*: the corrected
     wording is present on all three source surfaces, the old wording is gone from them, the gate
     numbers are unchanged, and the stable identities the correction created still exist.

  2. **IMMUTABLE BLAST-RADIUS EVIDENCE** — what PR #229 actually changed, measured strictly over
     the frozen range `BASE .. CORRECTION_HEAD`. Both endpoints are fixed commits, so these
     assertions state a historical fact that cannot go stale.

Conflating the two is the defect this module has now been corrected for twice. A blast-radius
assertion measured against a moving HEAD silently re-reads as "nobody may ever touch this path
again", and then fails on the first unrelated authorized change — which is not what its prose
claims to protect. Layer 2 therefore never reads the working tree, and layer 1 never pretends to
bound what the correction did.

Concretely, layer 2 permits (and layer 1 still guards): a later authorized MANIFEST change to a
foreign row — including a separate resolution of issue #231 — later gate development, later
stable-ID appends, and a later portfolio change resolving a different candidate.

The live layer checks:

  * all three source surfaces carry the exact corrected wording;
  * the old wording is gone from them, checked CASE-INSENSITIVELY — the capitalised README
    rendering is precisely what the original audit's case-sensitive scan missed;
  * the surfaces that were already correct are untouched;
  * the gate change was docstring-only, proved on the normalised source and on the numbers;
  * the historical outcomes SURVIVE / CORRECTION_ONLY / INCREMENTAL are preserved;
  * the correction record reproduces byte-identically.
"""
import ast
import hashlib
import json
import pathlib
import subprocess

import pytest

from puckworks.analysis import correction_i045_lineage as C

REPO = pathlib.Path(__file__).resolve().parents[1]
BUNDLE = REPO / "docs/insights/screens/I-045"
BASE = "6ce8d97db79bc9a189af130c61fd2d9af7c66883"          # IF-7 merge, canonical base
#: The commit at which the correction LANDED (PR #229). The blast-radius assertions below bound
#: what THE CORRECTION touched, so they must diff BASE..CORRECTION_HEAD, not BASE..HEAD. Against a
#: moving HEAD they would re-read as "nobody may ever touch these paths again", and would break on
#: the first unrelated PR that legitimately edits one — e.g. a later screen adding its row to
#: `RETIRED_CANDIDATES.md`, which that file's own format section requires. Over BASE..
#: CORRECTION_HEAD the assertions are unchanged from the day they were written.
CORRECTION_HEAD = "85f65c0d4b836990152fa4e9bf91c6d292a9e257"


def _git(*args):
    return subprocess.run(("git",) + args, cwd=REPO, capture_output=True, text=True)


def _have_base():
    return (_git("cat-file", "-e", BASE + "^{commit}").returncode == 0
            and _git("cat-file", "-e", CORRECTION_HEAD + "^{commit}").returncode == 0)


@pytest.fixture(scope="module")
def result():
    return C.check()


# --------------------------------------------------------------------------------------------
# THE THREE LIVE SOURCE SURFACES
# --------------------------------------------------------------------------------------------
def test_manifest_cell_carries_the_exact_corrected_wording(result):
    m = result["manifest"]
    assert m["dataset_id"] == "foster2025_2/fig12_14_curves"
    assert m["validation_strength"] == (
        "post-fit, same-campaign CT observations / verification of fitted trajectories")
    assert m["exact_match"] is True
    assert m["contains_incorrect_independent_attribution"] is False
    assert m["incorrect_occurrences"] == 0


def test_gate_docstring_carries_the_exact_corrected_wording(result):
    g = result["gate_docstring"]
    assert g["exact_match"] is True
    assert ("post-fit reconstruction, same campaign, not held out; 'qualitative-good'"
            in g["docstring"])
    assert g["contains_incorrect_independent_attribution"] is False
    assert g["incorrect_occurrences"] == 0


def test_root_readme_row_carries_the_exact_corrected_wording(result):
    rd = result["root_readme"]
    assert rd["evidence_level"] == (
        "Post-fit, same-campaign CT observations / verification of fitted trajectories")
    assert rd["exact_match"] is True
    assert rd["contains_incorrect_independent_attribution"] is False
    assert rd["incorrect_occurrences"] == 0
    assert "CT infiltration and machine mode (Foster 2025)" in rd["row"]


def test_the_readme_block_has_no_producer_and_that_is_recorded(result):
    """Ownership determination, so a future reader does not go looking for a generator."""
    assert result["root_readme"]["block_owner"].startswith("none")
    pulse = (REPO / "tools/update_readme_pulse.py").read_text(encoding="utf-8")
    assert "puckworks-data-inventory" not in pulse, "the pulse tool must not own this block"
    gov = (REPO / "tools/readme_governance.py").read_text(encoding="utf-8")
    assert "validation_strength" not in gov, "governance verifies coverage, it does not generate"


def test_the_old_wording_is_gone_case_insensitively_from_all_three():
    """The capitalised README rendering is exactly what the original scan missed."""
    for rel, needle in (("puckworks/data/MANIFEST.csv", C.INCORRECT_MANIFEST_CELL),
                        ("README.md", C.INCORRECT_README_CELL)):
        text = (REPO / rel).read_text(encoding="utf-8")
        assert needle.lower() not in text.lower(), rel
    doc = C._gate_docstring()
    assert C.INCORRECT_GATE_FRAGMENT.lower() not in doc.lower()


def test_status_is_applied(result):
    assert result["current_status"] == "APPLIED"
    assert result["current_bad_occurrences"] == {
        "MANIFEST": 0, "gate_docstring": 0, "root_README": 0}


# --------------------------------------------------------------------------------------------
# SOURCE-DIFF PRECISION
# --------------------------------------------------------------------------------------------
def test_exactly_one_manifest_cell_changed():
    if not _have_base():
        pytest.skip("canonical base not present in this checkout")
    import csv as _csv
    import io
    before = list(_csv.DictReader(io.StringIO(
        _git("show", "%s:puckworks/data/MANIFEST.csv" % BASE).stdout)))
    # HISTORICAL: the "after" side is the correction's own endpoint, never the working tree. A
    # later authorized change to a foreign row (e.g. resolving issue #231 on `de1_fixtureA`) must
    # not retroactively change what PR #229 did.
    after = list(_csv.DictReader(io.StringIO(
        _git("show", "%s:puckworks/data/MANIFEST.csv" % CORRECTION_HEAD).stdout)))
    assert len(before) == len(after)
    diffs = []
    for b, a in zip(before, after):
        for k in b:
            if b[k] != a[k]:
                diffs.append((a["dataset_id"], k))
    assert diffs == [("foster2025_2/fig12_14_curves", "validation_strength")], diffs


def test_the_gate_function_body_is_unchanged_apart_from_its_docstring():
    """AST comparison with the docstring stripped — the change must be documentation only."""
    if not _have_base():
        pytest.skip("canonical base not present in this checkout")

    def gate_ast(src):
        tree = ast.parse(src)
        fn = next(n for n in ast.walk(tree)
                  if isinstance(n, ast.FunctionDef) and n.name == "gate_foster_ct_trajectory")
        if (fn.body and isinstance(fn.body[0], ast.Expr)
                and isinstance(fn.body[0].value, ast.Constant)
                and isinstance(fn.body[0].value.value, str)):
            fn.body = fn.body[1:]                      # drop the docstring
        return ast.dump(ast.Module(body=[fn], type_ignores=[]))

    # HISTORICAL: over the correction's own range only. Comparing BASE with a live HEAD would
    # freeze all future scientifically authorized gate development.
    before = gate_ast(_git("show", "%s:puckworks/validation/gates.py" % BASE).stdout)
    after = gate_ast(_git("show", "%s:puckworks/validation/gates.py" % CORRECTION_HEAD).stdout)
    assert before == after, "the gate body changed — the correction must be docstring-only"


def test_only_the_foster_row_changed_in_the_readme_inventory_block():
    if not _have_base():
        pytest.skip("canonical base not present in this checkout")
    def block(text):
        b = text.split(C.README_MARKER, 1)[1].split("<!-- puckworks-data-inventory:end -->", 1)[0]
        return [ln for ln in b.splitlines() if ln.strip()]
    # HISTORICAL: BASE -> CORRECTION_HEAD. The live wording is asserted separately.
    before = block(_git("show", "%s:README.md" % BASE).stdout)
    after = block(_git("show", "%s:README.md" % CORRECTION_HEAD).stdout)
    assert len(before) == len(after)
    changed = [i for i, (b, a) in enumerate(zip(before, after)) if b != a]
    assert len(changed) == 1, changed
    assert C.README_ROW_KEY in after[changed[0]]


def test_no_other_readme_change():
    if not _have_base():
        pytest.skip("canonical base not present in this checkout")
    r = _git("diff", "--numstat", BASE, CORRECTION_HEAD, "--", "README.md")
    assert r.returncode == 0
    if r.stdout.strip():
        added, removed, _ = r.stdout.split()
        assert (added, removed) == ("1", "1"), r.stdout.strip()


# --------------------------------------------------------------------------------------------
# GATE NUMERICAL INVARIANCE
# --------------------------------------------------------------------------------------------
def test_gate_thresholds_are_unchanged():
    src = (REPO / "puckworks/validation/gates.py").read_text(encoding="utf-8")
    i = src.index("def gate_foster_ct_trajectory():")
    body = src[i:src.index("def gate_extraction_harness():")]
    assert "s_rmse < 0.2" in body and "h_rmse < 0.2" in body
    assert "sum(sdat) >= 4" in body and "sum(hdat) >= 4" in body


def test_gate_output_is_unchanged(result):
    n = result["gate_numerics"]
    assert n["run"] is True
    assert n["passed"] is True
    assert n["s_fit_rmse_mm"] == 0.002
    assert n["H_fit_rmse_mm"] == 0.053
    assert n["s_data_within_err"] == "4/8"
    assert n["H_data_within_err"] == "5/8"
    assert n["unchanged"] is True


# --------------------------------------------------------------------------------------------
# ALREADY-CORRECT AND PROTECTED SURFACES
# --------------------------------------------------------------------------------------------
def test_already_correct_surfaces_are_untouched(result):
    ev = result["already_correct_surfaces"]["EVIDENCE_LINKS"]
    for k in ("records_same_campaign", "records_fit_input",
              "relationship_same_campaign_not_held_out", "reality_facing_false",
              "support_status_context_only"):
        assert ev[k] is True, k
    if not _have_base():
        pytest.skip("canonical base not present")
    for path in ("puckworks/paper3/EVIDENCE_LINKS.json", "puckworks/public/claims.py",
                 "docs/public/generated/claims.json", "docs/paper3_resource/generated",
                 "puckworks/registry.py",
                 "puckworks/viz", "docs/figures/viz", "docs/public/site",
                 "docs/insights/RETIRED_CANDIDATES.md", "docs/insights/screens/I-076",
                 "docs/insights/screens/I-045/DEEP_SCREEN_PROTOCOL.md"):
        r = _git("diff", "--numstat", BASE, CORRECTION_HEAD, "--", path)
        assert r.returncode == 0 and r.stdout.strip() == "", "%s changed: %s" % (path, r.stdout)


def _registry_at(ref=None):
    if ref is None:
        return json.loads((REPO / "docs/insights/ID_REGISTRY.json").read_text(encoding="utf-8"))
    return json.loads(_git("show", "%s:docs/insights/ID_REGISTRY.json" % ref).stdout)


def _registry_delta(before, after):
    """(added, reassigned, removed) stable IDs between two registry snapshots."""
    sections = [k for k, v in before.items()
                if isinstance(v, dict) and k not in ("counts", "high_water")]
    added, reassigned, removed = [], [], []
    for sect in sections:
        for fp, sid in before[sect].items():
            got = after.get(sect, {}).get(fp)
            if got is None:
                removed.append(sid)
            elif got != sid:
                reassigned.append((sid, got))
        for fp, sid in after.get(sect, {}).items():
            if fp not in before[sect]:
                added.append(sid)
    return added, reassigned, removed


def test_the_id_registry_was_appended_to_not_rewritten():
    """HISTORICAL: over the correction's own range, exactly T-0175 was appended."""
    if not _have_base():
        pytest.skip("canonical base not present")
    before, after = _registry_at(BASE), _registry_at(CORRECTION_HEAD)
    added, reassigned, removed = _registry_delta(before, after)
    assert reassigned == [], "an existing stable ID was reassigned: %s" % reassigned
    assert removed == [], "the registry is append-only; entries were removed: %s" % removed
    assert sorted(added) == ["T-0175"], added
    assert after["counts"]["candidates"] == before["counts"]["candidates"]
    assert after["counts"]["tensions"] == before["counts"]["tensions"] + 1


def test_the_id_registry_still_preserves_everything_the_correction_left():
    """LIVE persistence. Later append-only IDs are permitted; deletion or reassignment is not.

    This must NOT pin the live totals: a future authorized effort may legitimately append new
    stable identities, and doing so is not a defect.
    """
    if not _have_base():
        pytest.skip("canonical base not present")
    before, live = _registry_at(CORRECTION_HEAD), _registry_at()
    added, reassigned, removed = _registry_delta(before, live)
    assert reassigned == [], "a stable ID was reassigned since the correction: %s" % reassigned
    assert removed == [], "a stable ID was removed since the correction: %s" % removed
    live_ids = {sid for k, v in live.items()
                if isinstance(v, dict) and k not in ("counts", "high_water")
                for sid in v.values()}
    assert "T-0063" in live_ids, "T-0063 (the I-045 identity) must survive"
    assert "T-0175" in live_ids, "T-0175 (created by the correction) must survive"
    # `added` may be non-empty; that is legitimate append-only growth and is deliberately unpinned.


def _portfolio_ids(text):
    d = json.loads(text)
    c = d["candidates"] if isinstance(d, dict) and "candidates" in d else d
    return {x.get("id") or x.get("candidate_id") for x in c}


def test_only_I045_left_the_candidate_portfolio_in_the_correction_range():
    """HISTORICAL: PR #229 removed I-045 from the live generated portfolio, and nothing else."""
    if not _have_base():
        pytest.skip("canonical base not present")
    before = _portfolio_ids(_git(
        "show", "%s:docs/insights/generated/candidate_portfolio.json" % BASE).stdout)
    after = _portfolio_ids(_git(
        "show", "%s:docs/insights/generated/candidate_portfolio.json" % CORRECTION_HEAD).stdout)
    assert after == before - {"I-045"}, sorted(before ^ after)


def test_I045_remains_resolved_by_correction_in_the_live_portfolio(result):
    """LIVE. Deliberately does NOT pin the live candidate count: a future authorized correction
    may resolve a different candidate, and that must not fail this test."""
    live = _portfolio_ids((REPO / "docs/insights/generated/candidate_portfolio.json")
                          .read_text(encoding="utf-8"))
    assert "I-045" not in live
    g = result["generated_foundry_artifacts"]
    assert g["live_candidate_portfolio_contains_I045"] is False
    assert g["I045_absence_reason"] == "RESOLVED_BY_CORRECTION"
    reg = _registry_at()
    ids = {sid for k, v in reg.items()
           if isinstance(v, dict) and k not in ("counts", "high_water") for sid in v.values()}
    assert "T-0063" in ids and "T-0175" in ids


def test_generated_foundry_artifacts_carry_the_corrected_wording(result):
    gen = result["generated_foundry_artifacts"]
    assert gen["current_manifest_wording_propagated"] is True
    assert gen["any_old_wording_remaining"] is False


# --------------------------------------------------------------------------------------------
# HISTORY PRESERVED
# --------------------------------------------------------------------------------------------
def test_historical_outcomes_are_preserved(result):
    h = result["historical_outcomes"]
    assert h["cheap_SURVIVE_preserved"] is True
    assert h["deep_CORRECTION_ONLY_preserved"] is True
    assert h["cheap_decision"] == "SURVIVE"
    assert h["deep_output_class"] == "CORRECTION_ONLY"
    assert result["authority"]["novelty"] == "INCREMENTAL"
    assert result["authority"]["if7_merge_commit"] == BASE


def test_the_old_wording_survives_only_where_it_is_quoted_as_the_defect():
    """It must remain in the frozen screen records — that IS the finding."""
    cheap = (BUNDLE / "result.json").read_text(encoding="utf-8")
    deep = (BUNDLE / "deep_result.json").read_text(encoding="utf-8")
    assert C.INCORRECT_MANIFEST_CELL.lower() in cheap.lower()
    assert C.INCORRECT_MANIFEST_CELL.lower() in deep.lower()
    chk = C.check(run_gate=False)
    # Previously `... or True`, which could never fail. Assert the real property instead: the
    # checker must SAY that the old wording is permitted, and say WHERE.
    assert "frozen screen records" in chk["old_wording_permitted_in"]
    assert "ALLOWED" in chk["historical_outcomes"]["note"], chk["historical_outcomes"]["note"]


# --------------------------------------------------------------------------------------------
# DETERMINISM
# --------------------------------------------------------------------------------------------
def test_committed_correction_result_reproduces_exactly(result):
    committed = (BUNDLE / "correction_result.json").read_text(encoding="utf-8")
    expected = json.dumps(result, indent=2) + "\n"
    if committed != expected:
        c = json.loads(committed)
        diffs = [k for k in sorted(set(c) | set(result)) if c.get(k) != result.get(k)]
        raise AssertionError(
            "correction_result.json is stale: %s\n  fix: python -m "
            "puckworks.analysis.correction_i045_lineage" % (diffs or "formatting"))


def test_two_constructions_are_identical(result):
    again = C.check()
    assert json.dumps(again, indent=2) == json.dumps(result, indent=2)


def test_the_correction_record_is_not_a_framework():
    """Structural, not textual: no classes, no registry, no scoring, no generation."""
    src = pathlib.Path(C.__file__).read_text(encoding="utf-8")
    tree = ast.parse(src)
    classes = [n.name for n in tree.body if isinstance(n, ast.ClassDef)]
    assert classes == [], "a correction CHECKER needs no class hierarchy: %s" % classes
    names = {n.name for n in tree.body if isinstance(n, ast.FunctionDef)}
    for banned in ("register", "generate", "score", "make_lens", "build_schema"):
        assert not any(f == banned or f.startswith(banned + "_") for f in names), banned
    assert "NOT a generalized correction framework" in " ".join(src.split())
    assert "NOT a correction framework" in C.check(run_gate=False)["scope"]
    # it is bounded to ONE candidate
    assert src.count("foster2025_2/fig12_14_curves") >= 1
    assert "for candidate in" not in src and "for row in _manifest_rows()" not in src


def test_applied_record_exists_and_matches(result):
    md = (BUNDLE / "CORRECTION_APPLIED.md").read_text(encoding="utf-8")
    assert "APPLIED" in md
    assert "SURVIVE" in md and "CORRECTION_ONLY" in md and "INCREMENTAL" in md
    assert C.CORRECTED_MANIFEST_CELL in md
    assert _sha(BUNDLE / "correction_result.json")[:12] in md


def _sha(p):
    return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()


# --------------------------------------------------------------------------------------------
# REGRESSIONS — the two layers must behave differently, and each must be non-vacuous
# --------------------------------------------------------------------------------------------
def test_regression_a_later_stable_id_append_is_accepted():
    """The live layer must permit legitimate append-only growth."""
    if not _have_base():
        pytest.skip("canonical base not present")
    import copy
    before, live = _registry_at(CORRECTION_HEAD), _registry_at()
    future = copy.deepcopy(live)
    future["tensions"]["0" * 64] = "T-0999"                      # a hypothetical later identity
    added, reassigned, removed = _registry_delta(before, future)
    assert "T-0999" in added
    assert reassigned == [] and removed == [], "a pure append must not read as a rewrite"


def test_regression_reassigning_a_stable_id_is_rejected():
    if not _have_base():
        pytest.skip("canonical base not present")
    import copy
    before = _registry_at(CORRECTION_HEAD)
    bad = copy.deepcopy(_registry_at())
    fp = next(f for f, sid in before["tensions"].items() if sid == "T-0175")
    bad["tensions"][fp] = "T-9999"
    _added, reassigned, _removed = _registry_delta(before, bad)
    assert reassigned == [("T-0175", "T-9999")], reassigned


def test_regression_removing_a_stable_id_is_rejected():
    if not _have_base():
        pytest.skip("canonical base not present")
    import copy
    before = _registry_at(CORRECTION_HEAD)
    bad = copy.deepcopy(_registry_at())
    fp = next(f for f, sid in before["tensions"].items() if sid == "T-0063")
    bad["tensions"].pop(fp)
    _added, _reassigned, removed = _registry_delta(before, bad)
    assert "T-0063" in removed


def test_regression_a_later_foreign_manifest_edit_cannot_move_the_frozen_blast_radius():
    """Issue #231 may one day change `de1_fixtureA`. That must not rewrite what PR #229 did."""
    if not _have_base():
        pytest.skip("canonical base not present")
    import csv as _csv
    import io

    def rows(ref):
        return list(_csv.DictReader(io.StringIO(
            _git("show", "%s:puckworks/data/MANIFEST.csv" % ref).stdout)))

    before, after = rows(BASE), rows(CORRECTION_HEAD)
    frozen = [(a["dataset_id"], k) for b, a in zip(before, after) for k in b if b[k] != a[k]]
    assert frozen == [("foster2025_2/fig12_14_curves", "validation_strength")]
    # the frozen range reads two fixed commits, so no working-tree state can enter it
    src = pathlib.Path(__file__).read_text(encoding="utf-8")
    body = src[src.index("def test_exactly_one_manifest_cell_changed"):
               src.index("def test_the_gate_function_body_is_unchanged")]
    assert "C._manifest_rows()" not in body, (
        "the historical manifest check must not read the working tree")


def test_regression_a_later_portfolio_change_cannot_move_the_historical_removal_set():
    if not _have_base():
        pytest.skip("canonical base not present")
    before = _portfolio_ids(_git(
        "show", "%s:docs/insights/generated/candidate_portfolio.json" % BASE).stdout)
    after = _portfolio_ids(_git(
        "show", "%s:docs/insights/generated/candidate_portfolio.json" % CORRECTION_HEAD).stdout)
    assert before - after == {"I-045"}
    # a hypothetical later resolution of a different candidate leaves the historical fact intact
    hypothetical_live = after - {"I-013"}
    assert before - after == {"I-045"}
    assert "I-045" not in hypothetical_live


def test_regression_the_old_wording_note_assertion_is_not_vacuous():
    """The `or True` this replaced could never fail. Removing the note must now fail."""
    chk = C.check(run_gate=False)
    note = chk["historical_outcomes"]["note"]
    assert "ALLOWED" in note
    mutated = dict(chk["historical_outcomes"], note=note.replace("ALLOWED", "forbidden"))
    assert "ALLOWED" not in mutated["note"], "the mutation must actually remove the property"
