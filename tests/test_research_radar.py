"""Offline tests for the research radar (issue #42, tools/research_radar.py).

No test in this module touches the network — discovery runs against frozen fixtures only. The
tests also pin the guardrails: no PDF/full-text storage, no repository write during a scan, and
no external-contact code path.
"""
import sys
import urllib.error
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT / "tools"))
import research_radar as R   # noqa: E402

FIX = _ROOT / "tests" / "fixtures" / "research_radar"


def _query(qid="q", terms=None, exclusions=None, sources=("arxiv", "crossref"), enabled=True, cap=10):
    return {
        "id": qid, "title": qid, "enabled": enabled, "source_families": list(sources),
        "terms": terms or ["coffee", "permeability", "porous"], "exclusions": exclusions or [],
        "max_candidates": cap,
    }


# ── normalization ────────────────────────────────────────────────────────────────
@pytest.mark.parametrize("raw,expected", [
    ("10.1000/ABC.1", "10.1000/abc.1"),
    ("https://doi.org/10.1000/abc.1", "10.1000/abc.1"),
    ("doi:10.1000/ABC.1", "10.1000/abc.1"),
    ("  10.1000/abc.1  ", "10.1000/abc.1"),
    (None, ""),
])
def test_doi_normalization(raw, expected):
    assert R.normalize_doi(raw) == expected


@pytest.mark.parametrize("raw,expected", [
    ("arXiv:2506.12345v2", "2506.12345"),
    ("http://arxiv.org/abs/2506.12345v1", "2506.12345"),
    ("2506.12345", "2506.12345"),
    (None, ""),
])
def test_arxiv_id_normalization(raw, expected):
    assert R.normalize_arxiv_id(raw) == expected


def test_title_key_fallback_normalizes_punctuation_and_case():
    a = R.title_key("Permeability of Coffee Beds!")
    b = R.title_key("permeability   of coffee beds")
    assert a == b == "permeability of coffee beds"


# ── parsing (source normalization + malformed) ────────────────────────────────────
def test_parse_arxiv_source_normalization():
    cands = R.parse_arxiv((FIX / "arxiv.xml").read_text(), "q")
    assert len(cands) == 3
    c = cands[0]
    assert c.source == "arxiv" and c.arxiv_id == "2506.12345"          # version stripped
    assert c.doi == "10.1000/shared.dup.1" and c.authors[:1] == ["A. Researcher"]


def test_parse_crossref_source_normalization():
    cands = R.parse_crossref((FIX / "crossref.json").read_text(), "q")
    assert len(cands) == 2
    c = cands[0]
    assert c.source == "crossref" and c.doi == "10.1000/shared.dup.1"
    assert c.date == "2026-06-20" and "<" not in c.abstract_excerpt      # HTML stripped


@pytest.mark.parametrize("bad", ["not xml at all", "<feed><entry></feed>", "", "{"])
def test_parse_arxiv_malformed_returns_empty(bad):
    assert R.parse_arxiv(bad, "q") == []


@pytest.mark.parametrize("bad", ["{not json", "", "[]", '{"message": 5}'])
def test_parse_crossref_malformed_returns_empty(bad):
    assert R.parse_crossref(bad, "q") == []


# ── dedupe ────────────────────────────────────────────────────────────────────────
def test_title_fallback_deduplication():
    a = R.Candidate("arxiv", "Same Title Here", [], "2026", None, None, None, None, "", "q")
    b = R.Candidate("crossref", "same title here", [], "2026", None, None, None, None, "", "q")
    assert len(R.dedupe([a, b])) == 1


def test_cross_source_doi_duplicate_collapses():
    cands = R.scan(_wrap(_query(sources=("arxiv", "crossref"))), fixtures_dir=FIX)
    dois = [R.normalize_doi(c.doi) for c in cands if c.doi]
    assert dois.count("10.1000/shared.dup.1") == 1, "cross-source DOI duplicate not collapsed"


# ── fetch: timeout + rate-limit (injected opener; NO network) ─────────────────────
def test_source_timeout_returns_none_after_bounded_retries():
    calls = {"n": 0}

    def opener(req, timeout=None):
        calls["n"] += 1
        raise urllib.error.URLError("timed out")

    out = R._http_get("http://example/x", retries=2, opener=opener, sleep=lambda *_: None)
    assert out is None and calls["n"] == 3            # initial + 2 retries, bounded


def test_rate_limit_429_is_retried_then_gives_up():
    calls = {"n": 0}

    def opener(req, timeout=None):
        calls["n"] += 1
        raise urllib.error.HTTPError("http://x", 429, "Too Many Requests", {}, None)

    out = R._http_get("http://x", retries=2, opener=opener, sleep=lambda *_: None)
    assert out is None and calls["n"] == 3


def test_non_429_http_error_is_not_retried():
    calls = {"n": 0}

    def opener(req, timeout=None):
        calls["n"] += 1
        raise urllib.error.HTTPError("http://x", 404, "Not Found", {}, None)

    out = R._http_get("http://x", retries=3, opener=opener, sleep=lambda *_: None)
    assert out is None and calls["n"] == 1            # 404 fails fast


# ── scan behaviors ────────────────────────────────────────────────────────────────
def _wrap(*queries):
    return {"version": 1, "queries": list(queries)}


def test_deterministic_ordering_is_stable_across_runs():
    cfg = _wrap(_query())
    a = [c.identity() for c in R.scan(cfg, fixtures_dir=FIX)]
    b = [c.identity() for c in R.scan(cfg, fixtures_dir=FIX)]
    assert a == b, "scan ordering is not stable across identical runs"


def test_exclusion_terms_drop_candidates():
    with_ex = R.scan(_wrap(_query(exclusions=["marketing", "barista training"])), fixtures_dir=FIX)
    titles = " ".join(c.title.lower() for c in with_ex)
    assert "barista training guide" not in titles
    without = R.scan(_wrap(_query(exclusions=[])), fixtures_dir=FIX)
    assert any("barista training guide" in c.title.lower() for c in without)


def test_disabled_query_is_not_scanned():
    assert R.scan(_wrap(_query(enabled=False)), fixtures_dir=FIX) == []


def test_candidate_already_recorded_is_excluded():
    first = R.scan(_wrap(_query()), fixtures_dir=FIX)
    recorded = {c.identity() for c in first}
    again = R.scan(_wrap(_query()), fixtures_dir=FIX, recorded_ids=recorded)
    assert again == []


def test_match_reasons_explain_each_candidate():
    cands = R.scan(_wrap(_query(terms=["permeability", "coffee"])), fixtures_dir=FIX)
    hit = next(c for c in cands if "permeability" in c.title.lower())
    assert "permeability" in hit.match_reasons and hit.score >= 1


# ── issue title + monthly de-dup ──────────────────────────────────────────────────
def test_issue_title_generation():
    assert R.radar_issue_title("2026-07-17") == "Research radar — 2026-07"


def test_no_duplicate_monthly_issue_same_month_same_title():
    assert R.radar_issue_title("2026-07-01") == R.radar_issue_title("2026-07-31")
    assert R.radar_issue_title("2026-07-01") != R.radar_issue_title("2026-08-01")


# ── guardrails ────────────────────────────────────────────────────────────────────
def test_no_pdf_or_full_text_stored():
    src = (_ROOT / "tools" / "research_radar.py").read_text()
    assert ".pdf" not in src.lower(), "radar must not reference PDF download"
    # abstract excerpts are bounded metadata, never full text
    cands = R.scan(_wrap(_query()), fixtures_dir=FIX)
    for c in cands:
        assert len(c.abstract_excerpt) <= R.MAX_ABSTRACT_CHARS
        assert not hasattr(c, "full_text")


def test_no_external_contact_or_submission_code():
    src = (_ROOT / "tools" / "research_radar.py").read_text().lower()
    for forbidden in ("smtplib", "sendmail", "send_message", "requests.post", "submit("):
        assert forbidden not in src, f"radar must not contain {forbidden!r}"


def test_scan_does_not_write_to_the_repository(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    before = set(tmp_path.rglob("*"))
    R.scan(_wrap(_query()), fixtures_dir=FIX)          # scan returns data; it must not write
    assert set(tmp_path.rglob("*")) == before


def test_write_outputs_is_confined_to_the_given_directory(tmp_path):
    cands = R.scan(_wrap(_query()), fixtures_dir=FIX)
    info = R.write_outputs(cands, "2026-07-17", tmp_path / "radar")
    written = {Path(info["json"]).resolve(), Path(info["md"]).resolve()}
    assert all(str(p).startswith(str((tmp_path / "radar").resolve())) for p in written)


# ── config ────────────────────────────────────────────────────────────────────────
def test_shipped_query_config_validates():
    pytest.importorskip("yaml", reason="pyyaml is a radar/dev extra, absent in the min-deps lane")
    cfg = R.load_config(_ROOT / "docs" / "research" / "radar_queries.yml")
    assert R.validate_config(cfg) == []
    assert any(q["enabled"] for q in cfg["queries"])


def test_render_is_deterministic_from_candidates(tmp_path):
    cands = R.scan(_wrap(_query()), fixtures_dir=FIX)
    R.write_outputs(cands, "2026-07-17", tmp_path / "a")
    R.write_outputs(cands, "2026-07-17", tmp_path / "b")
    assert (tmp_path / "a" / "radar.md").read_text() == (tmp_path / "b" / "radar.md").read_text()
    assert (tmp_path / "a" / "candidates.json").read_text() == (tmp_path / "b" / "candidates.json").read_text()
