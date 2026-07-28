"""The Paper A submission contract must be non-vacuous on each of the drifts it now covers.

Third review P0-6. The predecessor was a five-banned/six-required phrase guard, and it passed while
the package used a different title and abstract, the abstract was over the venue limit, keyword
lists disagreed, the cover-letter text quoted the retired title, supporting records disagreed over
an 18- versus 29-point grid, six cited works were missing from the bibliography, the supplement did
not exist, and the manifest was stale and dirty.

Each test below injects one of those faults into a sandbox and requires the contract to catch it.
A contract that reports "OK" is only meaningful if it can say "not OK".
"""
import json
import shutil
import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

# The contract composes the front-matter checker, which parses YAML; pyyaml is a radar/dev extra.
pytest.importorskip("yaml", reason="pyyaml is a radar/dev extra")

from tools import paper_a_consistency as C  # noqa: E402
from tools import paper_a_supplement as S  # noqa: E402


def test_the_contract_passes_on_the_current_tree():
    assert C.check_paper_a(include_release=False) == []


def test_the_release_gate_still_blocks():
    """`submission` mode must FAIL while the manifest is dirty and the metadata unresolved. If this
    ever passes, the release really is ready — update this test deliberately."""
    blockers = C._release_state()
    assert blockers, "release gate reports ready; verify that is genuinely true"


# ── non-vacuity: each drift class the review found must be catchable ──────────────────────────
@pytest.fixture
def sandbox(tmp_path, monkeypatch):
    """Copy every submission artefact and point the contract at the copies."""
    names = {
        "CANONICAL": C.CANONICAL, "CONVERSION": C.CONVERSION, "PACKAGE": C.PACKAGE,
        "HIGHLIGHTS": C.HIGHLIGHTS, "COVER_LETTER": C.COVER_LETTER, "SUPPLEMENT": C.SUPPLEMENT,
    }
    copies = {}
    for attr, src in names.items():
        dst = tmp_path / src.name
        if src.exists():
            shutil.copy(src, dst)
        monkeypatch.setattr(C, attr, dst)
        copies[attr] = dst
    monkeypatch.setattr(C, "SUBMISSION_FILES",
                        (copies["CONVERSION"], copies["PACKAGE"],
                         copies["HIGHLIGHTS"], copies["COVER_LETTER"]))
    return copies


def _problems(fn):
    return fn()


def test_a_retired_overclaim_phrase_is_caught(sandbox):
    p = sandbox["CONVERSION"]
    p.write_text(p.read_text() + "\nThe identifiability ratio was 2.1.\n", encoding="utf-8")
    assert any("identifiability ratio" in x for x in C._phrase_drift())


def test_re_promoting_the_table_7_intersection_is_caught(sandbox):
    """MC7: the assay and the model inventory are not demonstrably commensurate, so the previous
    round's 'conditional one-dimensional intersection band' must not return."""
    p = sandbox["CONVERSION"]
    p.write_text(p.read_text() + "\nThis gives a conditional one-dimensional intersection band.\n",
                 encoding="utf-8")
    assert any("intersection band" in x for x in C._phrase_drift())


def test_losing_a_required_correction_is_caught(sandbox):
    p = sandbox["CONVERSION"]
    p.write_text(p.read_text().replace("orthogonal same-campaign inventory assay", "assay"),
                 encoding="utf-8")
    assert any("orthogonal same-campaign inventory assay" in x for x in C._phrase_drift())


def test_an_unresolved_placeholder_is_caught(sandbox):
    p = sandbox["PACKAGE"]
    p.write_text(p.read_text() + "\nCorresponding author: [insert name].\n", encoding="utf-8")
    assert any("placeholder" in x for x in C._placeholders_and_process_language())


def test_repository_process_language_in_a_submission_file_is_caught(sandbox):
    p = sandbox["COVER_LETTER"]
    p.write_text(p.read_text() + "\nThe novelty search remains a PI action.\n", encoding="utf-8")
    assert any("PI action" in x for x in C._placeholders_and_process_language())


def test_a_dangling_supplementary_reference_is_caught(sandbox):
    """The exact P0-3 fault: the article promises an item the supplement does not define."""
    p = sandbox["CONVERSION"]
    p.write_text(p.read_text() + "\nSee Supplementary Table S99 for details.\n", encoding="utf-8")
    problems = C._supplementary_targets()
    assert any("S99" in x for x in problems), problems


def test_a_missing_supplement_entirely_is_caught(sandbox):
    sandbox["SUPPLEMENT"].unlink()
    assert any("no supplement exists" in x for x in C._supplementary_targets())


def test_a_grid_record_disagreement_is_caught(tmp_path, monkeypatch):
    """The 18-versus-29 fault: the supporting note disagreeing with the machine-readable record."""
    notes = tmp_path / "notes.md"
    notes.write_text("the grid used **18** points\n", encoding="utf-8")
    monkeypatch.setattr(C, "P05_NOTES", notes)
    assert any("29-point" in x for x in C._grid_record())


def test_a_stale_manifest_is_a_release_blocker(tmp_path, monkeypatch):
    m = tmp_path / "manifest.json"
    m.write_text(json.dumps({"git_dirty": True, "bundle_matches_head": False,
                             "release_fresh": False, "timestamp_utc": None}), encoding="utf-8")
    monkeypatch.setattr(C, "MANIFEST", m)
    blockers = C._release_state()
    for expected in ("git_dirty=true", "bundle_matches_head=false", "release_fresh=false",
                     "no generation timestamp"):
        assert any(expected in b for b in blockers), expected


def test_a_clean_manifest_clears_those_blockers(tmp_path, monkeypatch):
    """NON-VACUITY of the release gate itself: it must be capable of passing its manifest checks,
    or it would be an unconditional failure rather than a gate."""
    m = tmp_path / "manifest.json"
    m.write_text(json.dumps({"git_dirty": False, "bundle_matches_head": True,
                             "release_fresh": True, "timestamp_utc": "2026-07-27T00:00:00Z"}),
                 encoding="utf-8")
    monkeypatch.setattr(C, "MANIFEST", m)
    blockers = C._release_state()
    assert not any("manifest" in b for b in blockers), blockers


# ── the supplement generator ──────────────────────────────────────────────────────────────────
def test_the_supplement_is_current():
    assert S.OUT.exists(), "no supplement"
    assert S.OUT.read_text(encoding="utf-8") == S.build(), (
        "run python tools/paper_a_supplement.py --write")


def test_supplementary_table_s2_reports_all_eighteen_panel_objective_cells():
    """The manuscript relies on all six solute x variety panels under three objectives; the
    supplement must actually carry them, with denominators."""
    text = S.table_s2()
    rec = json.loads(S.OBJECTIVE_JSON.read_text(encoding="utf-8"))
    n = rec["n_rate_grid"]
    for panel in rec["panels"]:
        variety, solute = panel.split(":")
        assert f"| {variety} | {solute} |" in text
    # six panels x three objectives x four thresholds
    assert text.count(f"/{n} |") == 6 * 3 * 4
    assert "16 of 18" in text, "the boundary-reaching count must be stated"
    assert "interior in 13 of 18" in text, "the interior-minimum count must be stated"


def test_supplementary_table_s4_reports_both_losses():
    """MC6: the external panel must show the absolute-residual result, not only MAPE."""
    text = S.table_s4()
    assert "min MAPE (%)" in text and "min nRMSE (%)" in text
    assert "range ratio (MAPE)" in text and "range ratio (nRMSE)" in text


def test_every_supplementary_item_is_real_not_a_stub():
    """This test previously required NOT-YET-AVAILABLE stubs to be present, because S3 (endpoint
    propagation) and S6 (numerical convergence) had not been run and the supplement had to say so
    rather than omit them silently.

    Both have since been run and archived, so the assertion is INVERTED rather than deleted: no
    cited supplementary item may be a stub. If a future item is added before its analysis exists,
    the stub mechanism is still in `tools/paper_a_supplement.py` and this test will fail, which is
    the signal to use it."""
    text = S.build()
    assert "NOT YET AVAILABLE" not in text, (
        "a supplementary item is a stub; either run the analysis or explain the exemption here")
    # Sequential within each item type after the fourth review's P0-5 rebuild: Methods S1-S2,
    # Note S1, Tables S1-S5, Figures S1-S4.
    for item in ("S1", "S2"):
        assert f"Supplementary Methods {item}" in text, item
    assert "Supplementary Note S1" in text
    for item in ("S1", "S2", "S3", "S4", "S5"):
        assert f"Supplementary Table {item}" in text, item
    for item in ("S1", "S2", "S3", "S4"):
        assert f"Supplementary Figure {item}" in text, item
    # the two that were stubs must now carry real, producer-backed content
    assert "38 mL" in text and "42 mL" in text, "S3 endpoint propagation is not populated"
    assert "axial nodes" in text and "1e-07" in text, "S5 convergence is not populated"


# ── endpoint propagation (third review P0-4) ──────────────────────────────────────────────────
def test_the_endpoint_propagation_is_archived_and_covers_all_three_proxies():
    """The review's one remaining scientific closure: the headline benchmark could not stay
    conditioned on a single untested endpoint proxy."""
    rec = json.loads(C.ENDPOINT_JSON.read_text(encoding="utf-8"))
    assert sorted(rec["v_targets"]) == [38.0, 40.0, 42.0]
    assert len(rec["rows"]) == 3
    for r in rec["rows"]:
        for k in ("pooled_model_mape", "pooled_const_mape", "paired_difference_pp",
                  "clustered_range_within_group", "n_model_worse_than_const", "n_points"):
            assert k in r, k
        assert r["n_points"] == 108


def test_the_level_only_null_does_not_move_with_the_endpoint():
    """A correctness check on the pipeline, not a coincidence: the constant is fitted to MEASURED
    concentrations, which do not depend on where the solver terminates. If the baseline moved too,
    the sweep would not be doing what the paper claims."""
    rec = json.loads(C.ENDPOINT_JSON.read_text(encoding="utf-8"))
    nulls = {r["pooled_const_mape"] for r in rec["rows"]}
    assert len(nulls) == 1, f"the level-only baseline moved with the endpoint: {nulls}"


def test_the_manuscript_reports_the_endpoint_dependence_it_found():
    """The sweep found the effect SIZE stable but the inferential reading endpoint-dependent: at
    38 mL the primary range excludes zero. The review's decision rule says that dependence becomes
    part of the conclusion rather than being buried."""
    rec = json.loads(C.ENDPOINT_JSON.read_text(encoding="utf-8"))
    man = C.CONVERSION.read_text(encoding="utf-8")
    lo38, hi38 = next(r["clustered_range_within_group"] for r in rec["rows"]
                      if r["v_target_ml"] == 38.0)
    assert not (lo38 <= 0 <= hi38), "38 mL no longer excludes zero — update this test and the prose"
    assert not rec["conclusion_stable"]
    assert "not endpoint-invariant" in man
    # every per-endpoint headline value is printed
    for r in rec["rows"]:
        assert f"{r['pooled_model_mape']:.2f}" in man
        assert f"{abs(r['paired_difference_pp']):.3f}" in man


def test_the_endpoint_sweep_is_distinguished_from_the_blind_residual_sweep():
    """They are DIFFERENT estimands, and the manuscript previously risked reading the ~5 pp
    movement in one as evidence about the other."""
    man = C.CONVERSION.read_text(encoding="utf-8")
    assert "different estimands" in man
    assert "a shift common to both cancels" in man


# ── PDE discretisation convergence (third review MC4.4) ───────────────────────────────────────
def test_the_pde_convergence_study_is_archived_and_covers_the_requested_grid():
    """The convergence reported in the main text was of the RATE-PARAMETER grid. The review asked
    for convergence of the PDE discretisation itself, which is a different quantity and is
    load-bearing because the temporal result depends on outlet-trajectory shape."""
    rec = json.loads(S.CONVERGENCE_JSON.read_text(encoding="utf-8"))
    assert rec["node_counts"] == [100, 200, 400]
    assert rec["tolerances"] == [1e-5, 1e-6, 1e-7]
    assert len(rec["cells"]) == 9, "3 resolutions x 3 tolerances"
    for v in rec["cells"].values():
        for k in ("whole_cup", "early", "middle", "late", "rate_at_min", "range_ratio"):
            assert k in v, k


def test_the_production_configuration_is_converged():
    """If a future change makes the production mesh or tolerance materially disagree with the
    reference, that is a NEW numerical fact and this must fail rather than pass quietly."""
    rec = json.loads(S.CONVERGENCE_JSON.read_text(encoding="utf-8"))
    w = rec["worst_case_rel_dev_pct"]
    assert w["whole_cup"] < 0.01, w
    assert w["late_fraction"] < 0.01, w
    assert w["range_ratio"] < 0.1, w
    assert rec["rate_at_min_invariant_across_all_cells"] is True, (
        "the profiled minimum moved with the discretisation -- the identifiability result would "
        "then be partly a numerical artefact")


def test_the_manuscript_distinguishes_the_two_convergence_claims():
    # Whitespace-normalised: the alternation above existed only to cope with ONE known line break,
    # which is a fragile way to spell "ignore wrapping" and missed every other one.
    man = " ".join(C.CONVERSION.read_text(encoding="utf-8").split())
    assert "**rate-parameter** grid, which is a different quantity" in man
    assert "identical in every configuration" in man
    assert "Supplementary Table S5" in man


def test_the_numerical_scheme_and_boundary_treatment_are_stated():
    """MC4.4 also asked for the stencil and the boundary treatment, which need no computation."""
    man = C.CONVERSION.read_text(encoding="utf-8")
    assert "five-point\nbiased-upwind first derivative" in man or \
           "five-point biased-upwind first derivative" in man
    assert "Dirichlet inlet condition" in man


def test_the_unverified_stencil_attribution_is_not_cited():
    """The implementation docstring attributes the stencil to Carver & Hinds (1978). That is not
    on the source card and its metadata has not been verified here, so it must not appear in the
    manuscript or the reference list -- fabricating a bibliographic entry is precisely the class
    of defect these reviews exist to catch."""
    rec = json.loads(S.CONVERGENCE_JSON.read_text(encoding="utf-8"))
    assert "scheme_attribution_note" in rec, "the decision must be recorded, not silent"
    for path in (C.CONVERSION, C.CANONICAL):
        assert "Carver" not in path.read_text(encoding="utf-8"), path.name


def test_solver_warnings_are_recorded_rather_than_suppressed():
    rec = json.loads(S.CONVERGENCE_JSON.read_text(encoding="utf-8"))
    assert "num_jac" in rec["solver_warnings"]
    assert "recorded rather than suppressed" in rec["solver_warnings"]


def test_the_jacobian_is_described_as_a_sparsity_pattern_not_an_analytic_jacobian():
    """A sparsity PATTERN is not an analytic Jacobian, and the record said so all along.

    Fourth review P0-4: the manuscript and the convergence table both said "analytic Jacobian
    sparsity pattern" while the same record's solver-warning field explained that scipy estimates
    the entries by finite differences in `num_jac` -- which is where the recorded warnings came
    from. The document contradicted itself, and nothing checked it.
    """
    import json

    for path in (C.CONVERSION, C.CANONICAL):
        text = path.read_text(encoding="utf-8")
        assert "analytic Jacobian" not in text, f"{path.name} still claims an analytic Jacobian"
        assert "numerically estimated Jacobian" in text, (
            f"{path.name} does not say the Jacobian entries are estimated")

    rec = json.loads(S.CONVERGENCE_JSON.read_text(encoding="utf-8"))
    assert "analytic Jacobian" not in rec["scheme"]
    assert "sparsity pattern" in rec["scheme"]
    assert "numerically estimated" in rec["scheme"]


def test_the_convergence_conclusion_is_scoped_to_the_panels_actually_swept():
    """"Converged" may not be asserted for solutes and trajectories that were never swept."""
    # Whitespace-normalised: these phrases wrap across lines in the manuscript, and a raw `in`
    # check on the file would report a present sentence as missing.
    text = " ".join(C.CONVERSION.read_text(encoding="utf-8").split())
    assert "not a global convergence proof" in text, (
        "the convergence conclusion is not scoped to the tested panels")
    for owed in ("5-CQA", "time-varying-flow trajectory", "positive-control"):
        assert owed in text, f"the untested case {owed!r} is not disclosed"
    assert "have not been run" in text, (
        "the untested sweeps are named but not declared unrun")


@pytest.mark.skipif(
    "solver_health" not in json.loads(S.CONVERGENCE_JSON.read_text(encoding="utf-8")),
    reason="the archived convergence record predates the solver-health instrumentation; "
           "re-run puckworks.validation.slow.angeloni_bracket.numerical_convergence to populate it")
def test_solver_health_is_recorded_for_every_profiled_solve():
    """The "warnings do not affect the results" claim needs evidence independent of agreement.

    Two configurations that exercise the same numerical path can agree while both are wrong, so
    successful termination, finite states, physical concentrations and a monotone accumulated
    volume are collected for every solve rather than inferred from cross-cell agreement.
    """
    import json

    rec = json.loads(S.CONVERGENCE_JSON.read_text(encoding="utf-8"))
    panels = rec.get("panels") or {"_": rec}
    for name, panel in panels.items():
        health = panel.get("solver_health")
        assert health, f"{name}: no solver-health record"
        assert health["all_cells_successful"], f"{name}: a solve did not terminate successfully"
        assert health["all_cells_finite"], f"{name}: a solve produced non-finite states"
        assert health["all_cells_volume_monotone"], f"{name}: accumulated volume decreased"
        assert health["worst_min_liquid"] >= -1e-6, (
            f"{name}: liquid concentration went negative by "
            f"{health['worst_min_liquid']} — an unphysical state, not merely an inaccurate one")
        assert health["worst_min_solid"] >= -1e-6, f"{name}: solid concentration went negative"
        assert not health["failure_messages"], health["failure_messages"]
        assert health["total_solves"] > 0


def test_every_supplementary_item_is_cited_by_the_main_text():
    """The SI-reference check ran in ONE direction only.

    It verified that everything the article cites exists in the supplement. Nothing verified the
    converse, so the SI could define — and the bundle could ship — items no reader is ever pointed
    at. Seven of the twelve were in that state: Figures S1-S4, Methods S2, Table S1 and Table S4.
    The SI's own opening line claimed "Every item here is cited by the main text", which made it a
    consistent falsehood rather than a detectable inconsistency: both documents agreed, and both
    were wrong.
    """
    import re

    art = C.CONVERSION.read_text(encoding="utf-8")
    si = S.OUT.read_text(encoding="utf-8")
    cited = {(k, n) for k, n in
             re.findall(r"Supplementary\s+(Table|Figure|Note|Method)s?\s+(S\d+)", art)}
    defined = {(k, n) for k, n in
               re.findall(r"(?m)^### Supplementary (Table|Figure|Note|Method)s?\s+(S\d+)", si)}
    assert defined, "no supplementary items parsed — the heading format changed"
    uncited = sorted(defined - cited)
    assert not uncited, (
        f"the supplement defines items the main text never cites: {uncited}. Either cite them or "
        f"remove them; a journal will not accept an uncited supplementary item, and the SI header "
        f"asserts that every item is cited")
    assert not sorted(cited - defined), sorted(cited - defined)


def test_no_regex_fragments_or_duplicated_anchors_leaked_into_the_prose():
    """Substitution accidents leave reader-visible debris that no content check looks for.

    The canonical draft carried `§4<!--sec:result3-->.<!--sec:result3-->.]*` — a duplicated section
    anchor and a stray `]*` from a regex that had been applied as literal text. It survived into a
    committed manuscript because every existing guard asks whether the CONTENT is right, and this
    is well-formedness.
    """
    import re

    for path in (C.CONVERSION, C.CANONICAL):
        text = path.read_text(encoding="utf-8")
        dup = re.findall(r"(<!--sec:[\w-]+-->)\s*\.?\s*\1", text)
        assert not dup, f"{path.name}: duplicated section anchor {dup}"
        # Regex metacharacter runs that cannot occur in ordinary prose or Markdown.
        for frag in (r".]*", r".)*", r"\1", r"(?:", r"(?m)", r"\s+"):
            assert frag not in text, f"{path.name}: regex fragment {frag!r} leaked into the prose"


def test_the_manuscript_does_not_deny_data_it_uses():
    """§5 said an empirical whole-cup comparison "is not available" two sentences after quoting
    one, and `identifiability.py` reads `schmieder_cup_masses()` at brew ratio 1/3 to compute it.

    Round-six P0-3. This is the hardest defect class to catch: the statement is not inconsistent
    with any producer value, so no numeral or claim check touches it. It is a false statement ABOUT
    the corpus, contradicted by a file sitting in the repository.
    """
    from puckworks import data as d

    cups = [r for r in d.schmieder_cup_masses() if r.get("brew_ratio") == "1/3"]
    assert cups, "the brew-ratio-1/3 cup measurements are gone; the §5 wording must be revisited"
    solutes = {r["component"] for r in cups}
    assert {"caffeine", "trigonelline", "5-CQA"} <= solutes, solutes

    text = " ".join(C.CONVERSION.read_text(encoding="utf-8").split())
    assert "empirical whole-cup comparison on this campaign is not available" not in text, (
        "the manuscript denies whole-cup data that the repository holds and the same paragraph uses")
    assert "Measured whole cups for this campaign ARE available" in text
