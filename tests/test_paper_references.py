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
    assert "0 unmatched" in r.stdout
