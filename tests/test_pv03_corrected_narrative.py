"""Guard the corrected PV-03 'The Cup Hides the Clock' public narrative (v0.4.0 line).

The superseded fixed-25 s transfer-failure story must not reappear in the two live public documents.
This does NOT apply to historical review records that intentionally describe the correction
(e.g. docs/PAPER_*_DETAILED_REVIEW.md), only to the current authorities below.
"""
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[1]

# The current public-facing authorities for the PV-03 story.
LIVE_DOCS = [
    _ROOT / "docs" / "PUBLIC_VALUE.md",
    _ROOT / "docs" / "ANALYSIS_transfer.md",
]

# Superseded PV-03 claims (matched-endpoint result retired them). Exact enough not to collide with the
# legitimate, separate grinder-dial non-portability claims elsewhere in PUBLIC_VALUE.md.
SUPERSEDED = [
    "25–49",
    "25-49",
    "did not transfer across grind",
    "reveals the transfer failure",
    "predicted the cup to about 7",
    "We got a great result. Then we changed the grind",
]

# Corrected matched-endpoint facts that must be present in the PV-03 story.
CORRECTED_MARKERS = ["1,930", "−0.99", "8.2%", "8.6%", "50 of 108", "76%", "Jaccard"]


@pytest.mark.parametrize("doc", LIVE_DOCS, ids=lambda p: p.name)
def test_no_superseded_pv03_transfer_failure_claims(doc):
    text = doc.read_text(encoding="utf-8")
    hits = [p for p in SUPERSEDED if p in text]
    assert not hits, f"{doc.name} still contains superseded PV-03 claim(s): {hits}"


def test_public_value_pv03_uses_corrected_matched_endpoint_facts():
    text = (_ROOT / "docs" / "PUBLIC_VALUE.md").read_text(encoding="utf-8")
    # locate the PV-03 section body
    assert "### PV-03" in text, "PV-03 section missing from PUBLIC_VALUE.md"
    start = text.index("### PV-03")
    end = text.find("\n### ", start + 1)
    section = text[start: end if end != -1 else len(text)]
    missing = [m for m in CORRECTED_MARKERS if m not in section]
    assert not missing, f"PV-03 section missing corrected facts: {missing}"
    # the corrected story must not claim the mechanism transferred
    assert "mechanism transferred" not in section.lower() or "not" in section.lower()


def test_analysis_transfer_is_internally_coherent():
    text = (_ROOT / "docs" / "ANALYSIS_transfer.md").read_text(encoding="utf-8")
    # no leftover "under revision / provisional" banner over stale prose
    assert "Under revision" not in text and "provisional until this banner" not in text
    # names the corrected authority and the reproduction path
    assert "PAPER_A_DRAFT.md" in text
    assert "angeloni_bracket" in text
