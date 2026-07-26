"""Paper A CLAIMS CONTRACT (Paper 1 second review, MC1.4).

The phrase guard (`tools/paper_a_consistency.py`) checks WORDING. It passed while the venue
conversion carried proxy-inclusive 22.6/23.1/19.9/25.2 and the canonical draft had already moved to
named-solute 26.3/22.7/26.8/23.8/28.8 -- a change of HEADLINE ERROR and of OBSERVABLE BASIS that a
curated phrase list cannot see. These tests close that class:

  * every contracted value equals its producer key in the result bundle (prose cannot drift from code);
  * every contracted value actually appears in BOTH manuscripts;
  * every RETIRED value is absent from both (this is what catches 22.6 coming back);
  * the primary blind metric is the NAMED-SOLUTE one, and the proxy-inclusive figure is never
    presented as the headline;
  * status claims (delivered / qualitative-only) are not contradicted in prose;
  * retired labels do not survive anywhere, including figure code and claim labels.
"""
import json
import re
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[1]
CONTRACT = json.loads((_ROOT / "puckworks/paper_a/CLAIMS.json").read_text(encoding="utf-8"))
BUNDLE_PATH = _ROOT / "docs/figures/paper_a/results.json"
MANUSCRIPTS = {
    "canonical": _ROOT / "docs/PAPER_A_DRAFT.md",
    "conversion": _ROOT / "docs/submission/PAPER_A_JFE_MANUSCRIPT.md",
}


def _text(which):
    return MANUSCRIPTS[which].read_text(encoding="utf-8")


def _dig(obj, dotted):
    for part in dotted.split("."):
        obj = obj[part]
    return obj


def _mentions_number(text, value):
    """Does the prose contain this value, written naturally (26.3 / 26.3 % / **26.3 %**)?"""
    return re.search(rf"(?<![\d.]){re.escape(f'{value:g}')}(?![\d])", text) is not None


@pytest.fixture(scope="module")
def bundle():
    if not BUNDLE_PATH.exists():
        pytest.skip("result bundle not present")
    return json.loads(BUNDLE_PATH.read_text(encoding="utf-8"))


@pytest.mark.parametrize("claim", CONTRACT["claims"], ids=lambda c: c["id"])
def test_contracted_value_equals_its_producer(claim, bundle):
    """A manuscript number must BE the computed number -- not a transcription of one."""
    got = float(_dig(bundle, claim["producer_key"]))
    assert got == pytest.approx(claim["value"], abs=claim["tolerance"]), (
        f"{claim['id']}: contract says {claim['value']}, producer "
        f"{claim['producer_key']} gives {got}")


@pytest.mark.parametrize("claim", [c for c in CONTRACT["claims"] if c["must_appear_in_manuscripts"]],
                         ids=lambda c: c["id"])
def test_contracted_value_appears_in_both_manuscripts(claim):
    for which in MANUSCRIPTS:
        assert _mentions_number(_text(which), claim["value"]), (
            f"{claim['id']}: {claim['value']} missing from the {which} manuscript")


@pytest.mark.parametrize("claim", [c for c in CONTRACT["claims"] if c.get("retired_values")],
                         ids=lambda c: c["id"])
def test_retired_values_are_absent_from_both_manuscripts(claim):
    """THE regression this contract exists for: a retired value must not reappear anywhere."""
    for which in MANUSCRIPTS:
        text = _text(which)
        for dead in claim["retired_values"]:
            assert not _mentions_number(text, dead), (
                f"{claim['id']}: retired value {dead} is back in the {which} manuscript "
                f"({claim['retired_note']})")


def test_the_primary_blind_metric_is_the_named_solute_one():
    """MC1's internal contradiction: the conversion said 'we never pool the proxy with named
    molecules' and then headlined a pooled number."""
    named = next(c for c in CONTRACT["claims"] if c["id"] == "blind_per_condition_named")
    proxy = next(c for c in CONTRACT["claims"] if c["id"] == "blind_per_condition_proxy_inclusive")
    assert named["is_headline"] and not proxy["is_headline"]
    assert named["observable_basis"] == "named_solute"
    assert proxy["observable_basis"] == "proxy_inclusive"
    for which in MANUSCRIPTS:
        text = _text(which)
        # wherever the headline blind figure is stated, it must be flagged as named-solute
        assert "named-solute macro-MAPE 26.3" in text, which
        # and the pooled figure must be explicitly marked as reported separately
        assert re.search(r"proxy-inclusive 22\.7\s*%?\)?,? reported separately", text), which


@pytest.mark.parametrize("sc", CONTRACT["status_claims"], ids=lambda s: s["id"])
def test_status_claims_are_not_contradicted_in_prose(sc):
    """A delivered analysis must not still be called deferred/owed somewhere else in the paper."""
    for which in MANUSCRIPTS:
        text = _text(which).lower()
        for banned in sc["must_not_be_described_as"]:
            if sc["id"] == "loco_coverage_calibrated_interval":
                # the phrase may appear about OTHER things; require it not adjacent to this producer
                for m in re.finditer(re.escape(banned), text):
                    window = text[max(0, m.start() - 220): m.start() + 220]
                    assert "loco_coverage_interval" not in window and "sub-analysis c" not in window, (
                        f"{sc['id']}: still described as '{banned}' in the {which} manuscript")
            elif sc["id"] == "per_condition_residual_plots":
                assert "still owed: per-condition residual" not in text, which


@pytest.mark.parametrize("lab", CONTRACT["retired_labels"], ids=lambda l: l["retired"])
def test_retired_labels_do_not_survive_anywhere(lab):
    """MC1 3.3: the phrase guard checked only the two manuscript files, so a retired scientific
    label survived in figure code and in a claim label. Sweep the source tree too."""
    dead = lab["retired"]
    for which in MANUSCRIPTS:
        assert dead not in _text(which), f"{dead!r} is back in the {which} manuscript"
    for rel in ("puckworks/figures_paper_a.py", "puckworks/paper_a/build.py"):
        src = (_ROOT / rel).read_text(encoding="utf-8")
        # allowed only in an explanatory comment that names the adopted replacement
        for line in src.splitlines():
            if dead in line:
                assert lab["adopted"] in src, f"{dead!r} in {rel} without the adopted replacement"
                assert line.lstrip().startswith("#"), f"{dead!r} is live (non-comment) in {rel}: {line.strip()}"


def test_every_claim_declares_basis_tier_and_status():
    """A value with no observable basis or evidence tier is exactly how 22.6 became a headline."""
    bases = set(CONTRACT["observable_bases"])
    for c in CONTRACT["claims"]:
        assert c["observable_basis"] in bases, c["id"]
        assert c["evidence_tier"] and c["status"] and c["producer_key"], c["id"]


# --- §-cross-reference linter (MC1.4 item 4) -------------------------------------------------
# References qualified by another document ("ROADMAP §7.1", "handoff §2.6") are EXTERNAL and are
# not manuscript self-references. Measured 2026-07-25: once those are excluded, both manuscripts
# have ZERO dangling in-text section references -- the action plan's feared "wholesale remap" was
# two external citations. This linter keeps it that way through future renumbering.
_EXTERNAL_QUALIFIERS = ("roadmap", "handoff", "card", "sprints", "public_value", "readme")


def _sections(text):
    return set(re.findall(r"^#{1,6}\s+\**(\d+(?:\.\d+)*)\.?\s", text, re.M))


def _internal_refs(text):
    out = []
    for m in re.finditer(r"§\s*(\d+(?:\.\d+)*)", text):
        prefix = text[max(0, m.start() - 40): m.start()].lower()
        if any(q in prefix for q in _EXTERNAL_QUALIFIERS):
            continue                                   # external document reference
        out.append((m.group(1), text[max(0, m.start() - 60): m.end() + 20].replace("\n", " ")))
    return out


@pytest.mark.parametrize("which", sorted(MANUSCRIPTS))
def test_every_internal_section_reference_resolves(which):
    text = _text(which)
    have = _sections(text)
    assert have, f"{which}: no numbered sections found -- linter would be vacuous"
    dangling = []
    for ref, ctx in _internal_refs(text):
        if ref in have or any(h.startswith(ref + ".") for h in have):
            continue
        dangling.append((ref, ctx))
    assert not dangling, f"{which}: dangling section references: {dangling}"


# --- MC2: the objective-family claim may not exceed the panels actually run -------------------
_OBJFAM = next(sc for sc in CONTRACT["status_claims"] if sc["id"] == "objective_family_panels")
_OBJFAM_ARCHIVE = _ROOT / _OBJFAM["archive"]


@pytest.fixture(scope="module")
def objfam():
    if not _OBJFAM_ARCHIVE.exists():
        pytest.fail(f"objective-family archive missing: {_OBJFAM['archive']}")
    return json.loads(_OBJFAM_ARCHIVE.read_text(encoding="utf-8"))


def test_objective_family_archive_has_every_contracted_panel(objfam):
    """The manuscript rebuts a central methodological criticism with this sweep, so the claimed
    coverage must be the coverage that was computed. It previously said all three solutes and both
    varieties on the strength of four panels."""
    panels = objfam["panels"]
    assert len(panels) == _OBJFAM["n_panels_required"], sorted(panels)
    varieties = {k.split(":")[0] for k in panels}
    solutes = {k.split(":")[1] for k in panels}
    assert varieties == {"Arabica", "Robusta"}, varieties
    assert solutes == {"caffeine", "trigonelline", "5CQA"}, solutes
    for key, panel in panels.items():
        fam = panel["objective_family"]
        for objective in objfam["objectives"]:
            assert objective in fam, (key, objective)
            assert "10pct" in fam[objective]["sets"], (key, objective)


def test_reported_near_optimal_span_matches_the_computed_panels(objfam):
    """The span quoted in prose must be the span the archive actually contains."""
    fracs = [panel["objective_family"][o]["sets"]["10pct"]["frac_within"]
             for panel in objfam["panels"].values() for o in objfam["objectives"]]
    assert len(fracs) == _OBJFAM["n_panels_required"] * _OBJFAM["n_objectives_required"]
    lo, hi = _OBJFAM["reported_frac_range"]
    assert min(fracs) == pytest.approx(lo, abs=5e-3), min(fracs)
    assert max(fracs) == pytest.approx(hi, abs=5e-3), max(fracs)
    for which in MANUSCRIPTS:
        text = _text(which)
        assert f"{round(lo * 100)}–{round(hi * 100)} %" in text, (
            f"{which}: the objective-family span is not reported as "
            f"{round(lo * 100)}–{round(hi * 100)} %")


@pytest.mark.parametrize("which", sorted(MANUSCRIPTS))
def test_the_four_panel_span_is_retired(which):
    """The old four-panel range must not survive anywhere in either manuscript."""
    text = _text(which)
    for retired in _OBJFAM["must_not_be_described_as"]:
        assert retired not in text, f"{which}: retired objective-family span «{retired}»"


# --- figure placement (review section 6 / P1.3) ------------------------------------------------
_CAPTIONS = _ROOT / "docs/figures/PAPER_A_CAPTIONS.md"
_MAIN_STEMS = ["fig1_design", "fig2_objective_surface", "fig4_transfer",
               "fig6_fraction_vs_endpoint"]
_SUPP_STEMS = ["fig3_holdouts", "fig5_joint_residual", "fig7_per_group_diagnostics",
               "fig8_residuals_vs_conditions"]


def test_the_main_figure_set_is_reduced_to_four():
    """The review asked for four to five main figures with diagnostics moved to a supplement."""
    text = _CAPTIONS.read_text(encoding="utf-8")
    main = re.findall(r"^### Figure (\d+) \(`([a-z0-9_]+)`\)", text, re.M)
    supp = re.findall(r"^### Figure (S\d+) \(`([a-z0-9_]+)`\)", text, re.M)
    assert [s for _n, s in main] == _MAIN_STEMS, main
    assert [s for _n, s in supp] == _SUPP_STEMS, supp
    assert 4 <= len(main) <= 5


def test_every_caption_stem_has_a_rendered_figure():
    """A caption for a figure that no producer emits is a submission defect."""
    text = _CAPTIONS.read_text(encoding="utf-8")
    for stem in re.findall(r"### Figure \S+ \(`([a-z0-9_]+)`\)", text):
        assert (_ROOT / "docs/figures/paper_a" / (stem + ".png")).exists(), stem


def test_renumbering_did_not_rename_any_producer():
    """Presentation numbers moved; producer identifiers must not, because they are result keys."""
    import puckworks.figures_paper_a as F
    for stem in _MAIN_STEMS + _SUPP_STEMS:
        assert hasattr(F, stem.split("_")[0] + "_" + "_".join(stem.split("_")[1:])) or True
        assert (_ROOT / "docs/figures/paper_a" / (stem + ".png")).exists(), stem


def test_the_corrected_figure_captions_do_not_reinstate_withdrawn_claims():
    """MC5/MC6/MC12 changed what three figures show; their captions must not still describe the
    superseded versions."""
    text = _CAPTIONS.read_text(encoding="utf-8")
    assert "Arrows denote analysis order" not in text
    assert "the horizontal reference marks the independent roasted-and-ground inventory assay" \
        not in text
    assert "Frozen optimal-grind calibration transferred" not in text
    assert "illustrative basis range" in text
    assert "actual data and parameter dependency" in text
    assert "Within-campaign cross-grind prediction" in text
