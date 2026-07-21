"""Unit tests for the tour deep-dive notebook-formatting helpers (#43, ROADMAP §8).

Pure string builders (no IPython) — so the presentation contract is tested here, not embedded fragile in
notebook JSON.
"""
from puckworks.product import lab_component_stories as S
from puckworks.product import lab_tour_notebook_display as ND
from puckworks.viz.tour_style import TourFigureNarrative


def test_format_number_drops_trailing_zero():
    assert ND.format_number(20.0) == "20"
    assert ND.format_number(1.7) == "1.7"
    assert ND.format_number(9) == "9"


def test_humanize_fixed_is_readable_not_raw_params():
    got = ND.humanize_fixed({"dose_g": 20.0, "target_beverage_g": 40.0, "pressure_bar": 9.0,
                             "grind_setting": 1.7})
    assert got == ["Dose: 20 g", "Target beverage mass: 40 g", "Pressure: 9 bar", "Grind setting: 1.7"]
    # never leak a python parameter name
    joined = " ".join(got)
    for raw in ("dose_g", "pressure_bar", "=20.0", "grind_setting"):
        assert raw not in joined


def test_public_model_name_is_author_year_not_dotted_id():
    assert ND.public_model_name("cameron2020.extraction_bdf") == "Cameron (2020)"
    assert ND.public_model_name("brewer2026.lb_reference") == "Brewer (2026)"
    assert "part i" in ND.public_model_name("fasano2000_partI.fines_migration").lower()


def test_model_heading_never_carries_the_raw_id():
    story = S.component_story("cameron2020.extraction_bdf")
    h = ND.model_heading(story, "cameron2020.extraction_bdf")
    assert h.startswith("## ")
    assert "cameron2020.extraction_bdf" not in h and "Cameron (2020)" in h


def test_narrative_blocks_are_labelled_sections_not_one_italic_paragraph():
    nar = TourFigureNarrative(setup="A changes.", finding="B happens.", mechanism="Because C.",
                              scope="Only D.", takeaway="Note E.")
    blocks = ND.narrative_blocks(nar)
    assert blocks[0].startswith("**What changes.**")
    assert any(b.startswith("**What the model shows.**") for b in blocks)
    assert any(b.startswith("**Why this happens.**") for b in blocks)
    assert any(b.startswith("**What is interesting.**") for b in blocks)
    assert blocks[-1].startswith("> **Scope.**")
    # each section is its own block (blank-line separation happens between display() calls)
    assert len(blocks) == 5


def test_narrative_takeaway_is_optional():
    nar = TourFigureNarrative(setup="a", finding="b", mechanism="c", scope="d")
    blocks = ND.narrative_blocks(nar)
    assert len(blocks) == 4 and not any("interesting" in b.lower() for b in blocks)


def test_evidence_details_are_collapsed_and_complete():
    story = S.component_story("cameron2020.extraction_bdf")

    class _F:
        headline = "Pressure sweep"; viz_spec_id = "cameron_pressure_sweep"
        evidence_badge = "EXPLORATORY_SIMULATION"; evidence_strength = "qualitative"
        varied_input = "pressure_bar"; fixed_inputs = {"dose_g": 20.0}
        fidelity_ceiling = "exploratory only"; producer_ref = "mod:fn"

    det = ND.evidence_details_block("cameron2020.extraction_bdf", story,
                                    {"execution_status": "EXECUTED"}, "Cameron 2020", [_F()])
    assert det.startswith("<details>") and det.rstrip().endswith("</details>")
    for needle in ("cameron2020.extraction_bdf", "EXECUTED", "Cameron 2020", story.role[:10],
                   "Pressure sweep", "cameron_pressure_sweep", "qualitative", "exploratory only",
                   "`mod:fn`", "Dose: 20 g"):
        assert needle in det, f"details block missing {needle!r}"


def test_no_figure_block_uses_finite_reason_vocabulary():
    for reason in ("NO_DEFENSIBLE_PUBLIC_RELATIONSHIP_YET", "RIGHTS_BLOCKED",
                   "OPTIONAL_DEPENDENCY_UNAVAILABLE", "REFERENCE_ONLY", "TOO_EXPENSIVE_FOR_DEFAULT_TOUR"):
        block = ND.no_figure_block(reason, "note")
        assert block and "note" in block


def test_cup_and_intro_blocks_use_story_fields():
    story = S.component_story("cameron2020.extraction_bdf")
    assert ND.cup_block(story).startswith("**What this might mean for your cup.**")
    intro = ND.model_intro_blocks(story, "cameron2020.extraction_bdf")
    assert intro[0].startswith("## ") and intro[1].startswith("**What it computes.**")
