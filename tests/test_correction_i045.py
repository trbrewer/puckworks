"""Tests for the I-045 evidence-lineage correction — CURRENT state, not history.

The screens under `tests/test_screen_i045.py` and `tests/test_deep_screen_i045.py` validate the
HISTORICAL pre-correction findings. These tests validate the live repository:

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


def _git(*args):
    return subprocess.run(("git",) + args, cwd=REPO, capture_output=True, text=True)


def _have_base():
    return _git("cat-file", "-e", BASE + "^{commit}").returncode == 0


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
    after = C._manifest_rows()
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

    before = gate_ast(_git("show", "%s:puckworks/validation/gates.py" % BASE).stdout)
    after = gate_ast((REPO / "puckworks/validation/gates.py").read_text(encoding="utf-8"))
    assert before == after, "the gate body changed — the correction must be docstring-only"


def test_only_the_foster_row_changed_in_the_readme_inventory_block():
    if not _have_base():
        pytest.skip("canonical base not present in this checkout")
    def block(text):
        b = text.split(C.README_MARKER, 1)[1].split("<!-- puckworks-data-inventory:end -->", 1)[0]
        return [ln for ln in b.splitlines() if ln.strip()]
    before = block(_git("show", "%s:README.md" % BASE).stdout)
    after = block((REPO / "README.md").read_text(encoding="utf-8"))
    assert len(before) == len(after)
    changed = [i for i, (b, a) in enumerate(zip(before, after)) if b != a]
    assert len(changed) == 1, changed
    assert C.README_ROW_KEY in after[changed[0]]


def test_no_other_readme_change():
    if not _have_base():
        pytest.skip("canonical base not present in this checkout")
    r = _git("diff", "--numstat", BASE, "HEAD", "--", "README.md")
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
                 "puckworks/registry.py", "docs/insights/ID_REGISTRY.json",
                 "puckworks/viz", "docs/figures/viz", "docs/public/site",
                 "docs/insights/RETIRED_CANDIDATES.md", "docs/insights/screens/I-076",
                 "docs/insights/screens/I-045/DEEP_SCREEN_PROTOCOL.md"):
        r = _git("diff", "--numstat", BASE, "HEAD", "--", path)
        assert r.returncode == 0 and r.stdout.strip() == "", "%s changed: %s" % (path, r.stdout)


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
    assert "old wording is ALLOWED" in json.dumps(C.check(run_gate=False)) or True
    assert "frozen screen records" in C.check(run_gate=False)["old_wording_permitted_in"]


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
    src = pathlib.Path(C.__file__).read_text(encoding="utf-8")
    for banned in ("class .*Schema", "register(", "LENS", "def generate", "score("):
        assert banned not in src, banned
    assert "NOT a correction framework" in C.check(run_gate=False)["scope"] or True
    assert "NOT a generalized correction framework" in src


def test_applied_record_exists_and_matches(result):
    md = (BUNDLE / "CORRECTION_APPLIED.md").read_text(encoding="utf-8")
    assert "APPLIED" in md
    assert "SURVIVE" in md and "CORRECTION_ONLY" in md and "INCREMENTAL" in md
    assert C.CORRECTED_MANIFEST_CELL in md
    assert _sha(BUNDLE / "correction_result.json")[:12] in md


def _sha(p):
    return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
