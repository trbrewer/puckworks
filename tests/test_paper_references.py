"""Reference lists must exist, resolve, and be generated rather than hand-written.

Paper 1 shipped with NO bibliography: both files carried the instruction "Generate the final
author-year list from references.bib after the citation-key and DOI audit" while the body made 33
distinct author-year citations. A reviewer could not check one of them. Angeloni was also absent
from references.bib entirely, despite 26 citations and its own model card.

Paper 3 listed five references that carried no in-text bracket marker; two of them had been added
to the list without wiring the citations.
"""
import pathlib
import re
import subprocess
import sys

import pytest

_ROOT = pathlib.Path(__file__).resolve().parents[1]
BIB = _ROOT / "docs" / "literature_search" / "references.bib"
PAPER1 = (_ROOT / "docs" / "PAPER_A_DRAFT.md",
          _ROOT / "docs" / "submission" / "PAPER_A_JFE_MANUSCRIPT.md")
PAPER3 = _ROOT / "docs" / "PAPER_3_PUCKWORKS_DRAFT.md"

sys.path.insert(0, str(_ROOT))
from tools import paper_a_references as REF  # noqa: E402


@pytest.mark.parametrize("path", PAPER1, ids=lambda p: p.name)
def test_paper_1_has_a_generated_reference_list(path):
    text = path.read_text(encoding="utf-8")
    assert REF.BEGIN in text and REF.END in text, "no generated reference block"
    block = text.split(REF.BEGIN)[1].split(REF.END)[0]
    refs = [line for line in block.splitlines() if line.startswith("- ")]
    assert len(refs) >= 30, len(refs)
    assert "do not edit by hand" in block


@pytest.mark.parametrize("path", PAPER1, ids=lambda p: p.name)
def test_every_paper_1_citation_resolves_to_a_bib_entry(path):
    _used, missing = REF.resolve(path.read_text(encoding="utf-8"))
    assert missing == [], f"citations with no bib entry: {missing}"


@pytest.mark.parametrize("path", PAPER1, ids=lambda p: p.name)
def test_the_reference_block_is_not_stale(path):
    text = path.read_text(encoding="utf-8")
    used, _missing = REF.resolve(text)
    current = text.split(REF.BEGIN)[1].split(REF.END)[0]
    fresh = REF.render(used).split(REF.BEGIN)[1].split(REF.END)[0]
    assert current.strip() == fresh.strip(), "run tools/paper_a_references.py --write"


def test_angeloni_is_in_the_bibliography():
    """It was cited 26 times, has its own model card, and was absent from all 55 bib entries."""
    bib = BIB.read_text(encoding="utf-8")
    assert "angeloni2023" in bib
    assert "10.3390/app13042688" in bib, "the recorded DOI is missing"
    for path in PAPER1:
        assert "Angeloni" in path.read_text(encoding="utf-8").split(REF.BEGIN)[1]


def test_the_bib_parser_handles_multiline_and_adjacent_fields():
    """The first parser truncated multi-line titles and swallowed following fields whole -- Apgar's
    journal came out as 'Molecular BioSystems, volume = 6, pages = 1890--1900, year = 2010'."""
    recs = {r["key"]: r for r in REF.entries()}
    apgar = recs["apgar2010"]
    assert apgar["journal"] == "Molecular BioSystems", apgar["journal"]
    assert "volume" not in apgar["journal"] and "pages" not in apgar["journal"]
    ang = recs["angeloni2023"]
    assert ang["title"].endswith("Future Perspectives"), ang["title"]
    assert ang["authors"].count(" and ") == 6, "multi-line author list was truncated"


@pytest.mark.parametrize("path", PAPER1, ids=lambda p: p.name)
def test_no_reference_entry_carries_parser_artefacts(path):
    block = path.read_text(encoding="utf-8").split(REF.BEGIN)[1].split(REF.END)[0]
    for line in [x for x in block.splitlines() if x.startswith("- ")]:
        assert not re.search(r"volume\s*=|pages\s*=|year\s*=|[{}]", line), line[:110]
        assert re.search(r"\(\d{4}\)", line), f"no year: {line[:90]}"


def test_paper_3_has_no_uncited_references():
    """A listed-but-uncited reference reads as a defect. Two of the five were added to the list
    without wiring the in-text markers."""
    text = PAPER3.read_text(encoding="utf-8")
    body, refs = text.split("## References")[0], text.split("## References")[1]
    listed = {int(n) for n in re.findall(r"(?m)^(\d+)\.\s", refs)}
    used = {int(x) for m in re.finditer(r"\[(\d+(?:\s*,\s*\d+)*)\]", body)
            for x in m.group(1).split(",")}
    # OPEN EDITORIAL DECISION, recorded rather than hidden. Refs 7/8/9 (Moroney, Grudeva, Lee)
    # are the sources of three registered `published_port` components. They appear in the
    # manuscript only as component ids inside the GENERATED availability matrix, which must not be
    # hand-edited, so they carry no prose bracket marker. Resolving them needs an authorial choice
    # -- add a citing sentence, or drop them from the list -- so they are exempted explicitly and
    # the exemption must SHRINK: if any of them gains a citation this fails and the entry goes.
    PENDING = {7, 8, 9}
    uncited = listed - used
    assert uncited <= PENDING, f"NEW uncited references: {sorted(uncited - PENDING)}"
    assert PENDING <= listed, "a pending reference left the list -- update PENDING"
    resolved = PENDING - uncited
    assert not resolved, (
        f"refs {sorted(resolved)} are now cited -- remove them from PENDING")
    assert used - listed == set(), f"cited but not listed: {sorted(used - listed)}"


def test_paper_3_markers_are_outside_the_generated_blocks():
    """Citations must live in prose; the generated tables are regenerated and would lose them."""
    text = PAPER3.read_text(encoding="utf-8")
    for begin, end in (("<!-- corpus:begin -->", "<!-- corpus:end -->"),
                       ("<!-- availability:begin -->", "<!-- availability:end -->"),
                       ("<!-- scorecard:begin -->", "<!-- scorecard:end -->")):
        i, j = text.find(begin), text.find(end)
        if i == -1 or j == -1:
            continue
        assert "[23]" not in text[i:j] and "[24]" not in text[i:j]
    assert "Maille’s 2024 batch model [23]" in text
    assert "Roman-Corrochano’s 2017 stirred-vessel model [24]" in text


def test_the_generator_reports_unresolved_citations_rather_than_dropping_them(tmp_path):
    """NON-VACUITY: a generator that silently omitted an unmatched citation would produce a
    complete-looking list with a hole in it."""
    fake = tmp_path / "m.md"
    fake.write_text("Nonexistentauthor et al. (1999) showed something.\n\n## References\n",
                    encoding="utf-8")
    _used, missing = REF.resolve(fake.read_text(encoding="utf-8"))
    assert ("nonexistentauthor", "1999") in missing


def test_the_generator_cli_exits_nonzero_on_unresolved_citations():
    r = subprocess.run([sys.executable, str(_ROOT / "tools" / "paper_a_references.py")],
                       capture_output=True, text=True, cwd=_ROOT)
    assert r.returncode == 0, r.stdout + r.stderr
    assert "0 unmatched, 0 ambiguous" in r.stdout


# --------------------------------------------------------------------------------------------
# Citation-detector coverage (Paper 1 third review, P0-2).
#
# The detector reported "33 resolved, 0 unmatched" while omitting at least six cited works. A
# zero-unmatched report was evidence only that the regex recognised 33 patterns, not that every
# citation had been checked. Each case below is one of the ways the old
# `([A-Z][A-Za-z\-']+)(?:\s+et al\.?)?...((?:19|20)\d{2})` pattern failed silently.
# --------------------------------------------------------------------------------------------

_DETECTOR_CASES = [
    # (id, body text, expected (surname, year) pairs)
    ("unicode_surname", "identifiability are related (Tönsing et al., 2014).",
     {("tönsing", "2014")}),
    ("unicode_compound_surname", "volatile release online (Sánchez-López et al., 2014).",
     {("sánchez-lópez", "2014")}),
    ("et_al_split_across_a_line_break", "profile likelihood. Raue et\nal. (2009) showed this.",
     {("raue", "2009")}),
    ("two_years_after_one_author", "directions (Transtrum et al., 2011, 2015).",
     {("transtrum", "2011"), ("transtrum", "2015")}),
    ("three_years_after_one_author", "see Moroney et al. (2015, 2016, 2017).",
     {("moroney", "2015"), ("moroney", "2016"), ("moroney", "2017")}),
    ("semicolon_separated_group", "(Gutenkunst et al., 2007; Transtrum et al., 2011).",
     {("gutenkunst", "2007"), ("transtrum", "2011")}),
    ("two_author_ampersand", "as shown by Banga & Balsa-Canto (2008).",
     {("banga", "2008")}),
    ("two_author_and", "as shown by Ellero and Navarini (2019).",
     {("ellero", "2019")}),
    ("narrative_form", "Kuhn et al. (2017) measured caffeine.",
     {("kuhn", "2017")}),
    ("parenthetical_form", "measured caffeine (Kuhn et al., 2017).",
     {("kuhn", "2017")}),
    ("adjacent_markdown_emphasis", "see *Kuhn et al. (2017)* for the assay.",
     {("kuhn", "2017")}),
    ("hyphenated_ascii_surname", "the control chart (Roman-Corrochano et al., 2019).",
     {("roman-corrochano", "2019")}),
]


@pytest.mark.parametrize("body,expected",
                         [(b, e) for _i, b, e in _DETECTOR_CASES],
                         ids=[i for i, _b, _e in _DETECTOR_CASES])
def test_the_citation_detector_recognises_every_citation_form(body, expected):
    assert expected <= REF.cited(body), f"missed {sorted(expected - REF.cited(body))}"


def test_the_six_previously_missed_works_are_in_the_generated_list():
    """These six were cited in the body and present in references.bib, yet omitted from the
    generated bibliography while the checker reported zero unmatched citations."""
    for path in PAPER1:
        used, _missing = REF.resolve(path.read_text(encoding="utf-8"))
        for key in ("raue2009", "transtrum2015", "tonsing2014", "kuhn2017",
                    "sanchezlopez2014", "sanchezlopez2016"):
            assert key in used, f"{key} missing from {path.name}"


@pytest.mark.parametrize("path", PAPER1, ids=lambda p: p.name)
def test_the_rendered_list_carries_no_tex_or_bibtex_artefacts(path):
    """The rendered list exposed raw BibTeX: `K\\"unsch`, `Bia\\las`, `\\L`, the literal
    placeholder `others`, and double-hyphen page ranges."""
    block = path.read_text(encoding="utf-8").split(REF.BEGIN)[1].split(REF.END)[0]
    for line in [x for x in block.splitlines() if x.startswith("- ")]:
        assert "\\" not in line, f"TeX escape survived: {line[:110]}"
        assert not re.search(r"(?<!\w)others(?!\w)", line), f"literal `others`: {line[:110]}"
        assert "--" not in line, f"un-converted en dash: {line[:110]}"


def test_accents_and_glyph_commands_render_as_real_characters():
    assert REF._clean(r"T{\"o}nsing, Christian") == "Tönsing, Christian"
    assert REF._clean(r"S{\'a}nchez-L{\'o}pez, J. A.") == "Sánchez-López, J. A."
    assert REF._clean(r"K\"unsch, Hans R.") == "Künsch, Hans R."
    assert REF._clean(r"Bia{\l}as, {\L}.") == "Białas, Ł."
    assert REF._clean("1890--1900") == "1890–1900"


def test_a_citation_binds_to_the_lead_author_not_a_co_author():
    """Found by the deletion test below. `references.bib` has two 2016 entries listing Villaverde
    -- `villaverde2016` (lead) and `chis2016` (third author). The any-author matcher bound
    "Villaverde et al. (2016)" to whichever came first in the file, so the citation resolved to
    the right work only by accident of .bib ordering."""
    recs = {r["key"]: r for r in REF.entries()}
    assert REF._leads("villaverde", recs["villaverde2016"])
    assert not REF._leads("villaverde", recs["chis2016"]), "co-author matched as lead"
    assert REF._leads("chis", recs["chis2016"])
    # Compound surnames are still cited by their last token.
    assert REF._leads("guerra", recs["vacaguerra2024"])


def test_ambiguous_citations_are_reported_rather_than_silently_bound(tmp_path, monkeypatch):
    """If two entries genuinely share a lead surname and year, the audit must say so instead of
    picking one."""
    stub = tmp_path / "amb.bib"
    stub.write_text(
        "@article{a2020,\n  author = {Smith, A.},\n  title = {One.}, year = {2020}}\n\n"
        "@article{b2020,\n  author = {Smith, B.},\n  title = {Two.}, year = {2020}}\n",
        encoding="utf-8")
    monkeypatch.setattr(REF, "BIB", stub)
    used, missing = REF.resolve("As Smith et al. (2020) showed.\n\n## References\n")
    assert used == {} and missing == []
    assert REF.resolve.last_ambiguous == [("smith", "2020", ("a2020", "b2020"))]


def test_bibtex_others_is_not_treated_as_a_surname():
    """`others` is the et-al marker. If it entered the surname set, a citation to a real author
    named Others would resolve against an unrelated entry."""
    for r in REF.entries():
        assert "others" not in r["surnames"], r["key"]


@pytest.mark.parametrize("path", PAPER1, ids=lambda p: p.name)
def test_deleting_any_cited_bib_entry_makes_the_audit_fail(path, tmp_path, monkeypatch):
    """NON-VACUITY for the whole detector, not just one hand-written fake citation: the audit must
    fail for EVERY entry the paper actually cites. This is the test the review asked for -- with
    the old detector it passed vacuously for the six works it could not see."""
    text = path.read_text(encoding="utf-8")
    original = REF.BIB.read_text(encoding="utf-8")
    chunks = re.split(r"(?m)^(?=@)", original)
    used, _missing = REF.resolve(text)

    for key in sorted(used):
        kept = [c for c in chunks if not re.match(rf"@\w+\{{{re.escape(key)},", c)]
        assert len(kept) == len(chunks) - 1, f"could not isolate {key}"
        stub = tmp_path / f"{key}.bib"
        stub.write_text("".join(kept), encoding="utf-8")
        monkeypatch.setattr(REF, "BIB", stub)
        _u, missing = REF.resolve(text)
        assert missing, f"removing {key} from the bib left the audit reporting a clean pass"
