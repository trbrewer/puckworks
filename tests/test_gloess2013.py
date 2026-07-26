"""gloess2013 DE-espresso endpoint intake (card `docs/cards/gloess2013.md`).

Data-only: no model, no component, no gate. The point of these tests is the PRECISION
DISTINCTION -- the card's exact text/table values must stay separable from its figure reads,
because the headline TDS and EY are figure reads and must never be treated as precise.
"""
from puckworks import data as d

TEXT, FIGURE = "text_table", "figure_read"


def _by_quantity():
    return {r["quantity"]: r for r in d.gloess_de_espresso()}


def test_only_the_de_espresso_condition_is_transcribed():
    """The paper compares nine brew methods; eight are non-espresso and deliberately absent."""
    rows = d.gloess_de_espresso()
    assert len(rows) == 17
    q = _by_quantity()
    assert q["dose"]["value"] == 16.01           # the DE operating point, per Table 1
    assert q["shot_time"]["value"] == 28.7
    assert q["pressure"]["value"] == 9.0
    assert q["inlet_temperature"]["value"] == 92.0


def test_every_row_declares_how_it_was_extracted():
    """A value with no stated extraction route cannot be trusted at any precision."""
    for r in d.gloess_de_espresso():
        assert r["extraction_method"] in (TEXT, FIGURE), r
        assert r["unit"] and r["basis"] and r["source_location"]


def test_exact_values_keep_their_published_uncertainty():
    q = _by_quantity()
    for name, val, unc in (("dose", 16.01, 0.01), ("shot_time", 28.7, 0.2),
                           ("caffeine", 21.0, 0.4), ("cqa_3", 5.8, 0.2), ("cqa_5", 2.8, 0.2)):
        assert q[name]["extraction_method"] == TEXT
        assert q[name]["value"] == val
        assert q[name]["uncertainty"] == unc


def test_headline_tds_and_ey_are_figure_reads_carrying_no_uncertainty():
    """THE load-bearing caveat: the two numbers a reader is most likely to reuse are the least
    precise ones here. The ESM tables that would fix this were not retrieved."""
    q = _by_quantity()
    for name in ("tds", "extraction_yield", "ph", "headspace_intensity",
                 "titratable_acidity_to_ph_6_6", "titratable_acidity_to_ph_8_0",
                 "esterified_fatty_acids"):
        assert q[name]["extraction_method"] == FIGURE, name
        assert q[name]["uncertainty"] == "", f"{name}: a figure read must not carry an uncertainty"


def test_the_endpoint_sits_below_camerons_inventory_ceiling():
    """The one registry-relevant cross-check: an independent Dalla Corte espresso at ~20 % EY is
    comfortably under cameron2020's 29.6 % per-bed-volume inventory ceiling. COMPATIBILITY only --
    one pooled composite on one coffee, with a figure-read EY, gates nothing."""
    q = _by_quantity()
    assert 0.0 < q["extraction_yield"]["value"] < 29.6


def test_beverage_is_a_volume_so_mass_conversion_stays_an_assumption():
    """No density is given, so volume -> beverage_g is an assumption, not data."""
    q = _by_quantity()
    assert q["beverage_volume"]["unit"] == "ml"
    assert not any(r["unit"] == "g" and r["quantity"].startswith("beverage")
                   for r in d.gloess_de_espresso())


def test_psd_is_mode_and_fwhm_only():
    """Mode + FWHM cannot reconstruct a distribution -- unusable for any PSD model."""
    q = _by_quantity()
    assert q["psd_mode"]["value"] == 400.0 and q["psd_fwhm"]["value"] == 220.0
    assert not any("bin" in r["quantity"] for r in d.gloess_de_espresso())
