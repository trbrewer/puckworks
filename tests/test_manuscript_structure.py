"""Structural integrity of the three manuscripts under external review.

A structural pass found what the numeral and citation audits could not: tables that carried no
number or caption at all. Paper 1 had FIVE substantive tables and not one was numbered, so a
reviewer could not refer to any of them. Paper 3 had a dangling `Table 2b` reference -- prose I
wrote pointing at a generated block that had no caption.

Captions for the GENERATED blocks live in their renderers, not in the manuscript, so a caption
cannot drift from the table it labels.
"""
import pathlib
import re

import pytest

_ROOT = pathlib.Path(__file__).resolve().parents[1]
PAPERS = {
    "Paper 1 draft": _ROOT / "docs" / "PAPER_A_DRAFT.md",
    "Paper 1 JFE": _ROOT / "docs" / "submission" / "PAPER_A_JFE_MANUSCRIPT.md",
    "Paper 2 (B2)": _ROOT / "docs" / "PAPER_B2_TEMPORAL_DRAFT.md",
    "Paper 3": _ROOT / "docs" / "PAPER_3_PUCKWORKS_DRAFT.md",
}
#: Table numbers belonging to OTHER papers. Paper 1 cites Angeloni's Table 7 and says so
#: explicitly ("their Table 7", "Angeloni 2023, Table 7"); it is not Paper 1's own table.
EXTERNAL = {"Paper 1 draft": {"7"}, "Paper 1 JFE": {"7"}}


def _body(text):
    return text.split("## References")[0]


@pytest.mark.parametrize("name", list(PAPERS), ids=list(PAPERS))
def test_every_table_is_numbered_and_captioned(name):
    text = PAPERS[name].read_text(encoding="utf-8")
    lines = _body(text).splitlines()
    uncaptioned = []
    for i in range(len(lines) - 1):
        if lines[i].strip().startswith("|") and re.match(r"^\s*\|[\s:|-]+\|\s*$", lines[i + 1]):
            # Scan back over the blank line to the whole preceding PARAGRAPH, not a fixed number
            # of lines. A three-line window could not see a caption that wrapped to four, so a
            # correctly captioned table read as uncaptioned -- the heuristic was measuring caption
            # length, not caption presence.
            #: HTML comments are splice markers and generation banners, not prose. Treating them
            #: as a paragraph hid the caption sitting immediately above a generated block.
            def _prose(k):
                s = lines[k].strip()
                return bool(s) and not s.startswith("<!--")

            j = i
            # Walk back over any number of blank/marker-only paragraphs to the nearest prose one.
            while j > 0 and not _prose(j - 1):
                j -= 1
            start = j
            while start > 0 and _prose(start - 1):
                start -= 1
            window = "\n".join(lines[start:i])
            if not re.search(r"\*\*Table [0-9A-Za-z]+\.", window):
                uncaptioned.append(f"L{i+1}: {lines[i][:70]}")
    assert not uncaptioned, f"{name} has uncaptioned tables:\n  " + "\n  ".join(uncaptioned)


@pytest.mark.parametrize("name", list(PAPERS), ids=list(PAPERS))
def test_every_table_reference_resolves(name):
    text = PAPERS[name].read_text(encoding="utf-8")
    declared = set(re.findall(r"\*\*Table ([0-9A-Za-z]+)\.", text))
    referenced = set(re.findall(r"\bTable ([0-9]+[a-z]?)\b", _body(text)))
    dangling = sorted(referenced - declared - EXTERNAL.get(name, set()))
    assert not dangling, f"{name} references undeclared tables: {dangling}"


@pytest.mark.parametrize("name", list(PAPERS), ids=list(PAPERS))
def test_table_numbers_are_unique(name):
    nums = re.findall(r"\*\*Table ([0-9A-Za-z]+)\.", PAPERS[name].read_text(encoding="utf-8"))
    dupes = {n for n in nums if nums.count(n) > 1}
    assert not dupes, f"{name} reuses table numbers: {sorted(dupes)}"


@pytest.mark.parametrize("name", list(PAPERS), ids=list(PAPERS))
def test_section_numbering_has_no_duplicates_or_gaps(name):
    body = _body(PAPERS[name].read_text(encoding="utf-8"))
    nums = [m.group(1) for m in re.finditer(r"(?m)^#{2,4}\s+(\d+(?:\.\d+)*[a-z]?)\.?\s+\S", body)]
    dupes = {n for n in nums if nums.count(n) > 1}
    assert not dupes, f"{name} has duplicate section numbers: {sorted(dupes)}"
    tops = sorted({int(n.split(".")[0]) for n in nums if n.split(".")[0].isdigit()})
    gaps = [f"{a}->{b}" for a, b in zip(tops, tops[1:]) if b != a + 1]
    assert not gaps, f"{name} has gaps in top-level numbering: {gaps}"


def test_generated_table_captions_live_in_their_generators():
    """A caption hand-written into the manuscript beside a generated block would be silently
    dropped the next time the block is regenerated."""
    from puckworks.paper3 import availability, corpus
    assert "Table 1a. Corpus denominators" in corpus.render(corpus.denominators())
    assert "Table 1b. Corpus-construction method" in corpus.render_method()
    assert "Table 1c. Protocol choices" in corpus.render_protocol()
    m = availability.matrix()
    rendered = availability.render_matrix(m)
    assert "Table 1f. Availability matrix" in rendered
    assert "Table 1g. Availability by component" in rendered
    s = availability.implementation_status()
    assert "Table 1h. Implementation status" in availability.render_implementation_status(s)


def test_paper_3_generated_blocks_are_current():
    """The captions were added to the renderers; the manuscript must carry the regenerated text."""
    from puckworks.paper3 import availability, corpus
    assert corpus.splice(write_it=False) == ""
    assert availability.splice(write_it=False) == ""
