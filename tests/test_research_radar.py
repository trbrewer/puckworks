"""Offline tests for the hardened research radar (issue #42).

No test touches the network — discovery runs against frozen fixtures, and pacing/HTTP use injected
clocks/openers. The tests pin the guardrails (no PDF/full-text, no repo write, no external contact)
and the safety hardening (pacing, structured queries, lookback, cross-month dedup, source health,
sanitization, caps, labels).
"""
import sys
import urllib.error
import urllib.parse
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT / "tools"))
import research_radar as R          # noqa: E402
import research_radar_issue as RI   # noqa: E402

FIX = _ROOT / "tests" / "fixtures" / "research_radar"


def _query(qid="q", groups=None, exclusions=None, sources=("arxiv", "crossref"),
           enabled=True, cap=10, lookback=3650):
    return {"id": qid, "title": qid, "enabled": enabled, "lookback_days": lookback,
            "maximum_candidates": cap, "source_families": list(sources),
            "concept_groups": groups or [["coffee", "permeability", "porous"]],
            "exclusions": exclusions or [], "last_human_review": "2026-07-17", "owner": "maintainer"}


def _cfg(*queries):
    return {"version": 1, "defaults": {"lookback_days": 3650}, "queries": list(queries)}


def _scan(cfg, **kw):
    kw.setdefault("scan_date", "2026-07-17")
    return R.scan(cfg, fixtures_dir=FIX, **kw)


# ── normalization ────────────────────────────────────────────────────────────────
@pytest.mark.parametrize("raw,expected", [
    ("10.1000/ABC.1", "10.1000/abc.1"), ("https://doi.org/10.1000/abc.1", "10.1000/abc.1"),
    ("doi:10.1000/ABC.1", "10.1000/abc.1"), (None, "")])
def test_doi_normalization(raw, expected):
    assert R.normalize_doi(raw) == expected


@pytest.mark.parametrize("raw,expected", [
    ("arXiv:2506.12345v2", "2506.12345"), ("http://arxiv.org/abs/2506.12345v1", "2506.12345"),
    ("2506.12345", "2506.12345"), (None, "")])
def test_arxiv_id_normalization(raw, expected):
    assert R.normalize_arxiv_id(raw) == expected


def test_title_fallback_key():
    assert R.title_key("Permeability of Coffee Beds!") == R.title_key("permeability   of coffee beds")


# ── parsing ───────────────────────────────────────────────────────────────────────
def test_parse_arxiv():
    cands = R.parse_arxiv((FIX / "arxiv.xml").read_text(), "q")
    assert len(cands) == 3 and cands[0].arxiv_id == "2506.12345" and cands[0].doi == "10.1000/shared.dup.1"


def test_parse_crossref():
    cands = R.parse_crossref((FIX / "crossref.json").read_text(), "q")
    assert len(cands) == 2 and "<" not in cands[0].abstract_excerpt


@pytest.mark.parametrize("bad", ["not xml", "<feed><entry></feed>", "", "{"])
def test_parse_arxiv_malformed(bad):
    assert R.parse_arxiv(bad, "q") == []


@pytest.mark.parametrize("bad", ["{bad", "", "[]", '{"message": 5}'])
def test_parse_crossref_malformed(bad):
    assert R.parse_crossref(bad, "q") == []


# ── sanitization (Phase 17) ─────────────────────────────────────────────────────────
def test_sanitize_neutralizes_mentions_and_refs():
    out = R.sanitize_text("hello @evil and #123 issue")
    assert "@ evil" in out and "# 123" in out and "@evil" not in out


def test_sanitize_strips_html_bidi_newlines_and_pipes():
    rlo = chr(0x202E)  # right-to-left override, built via chr() so no literal bidi char sits in source
    raw = "Ti<script>x</script>tle" + rlo + "en\nline | pipe"
    out = R.sanitize_text(raw)
    assert "<script>" not in out and rlo not in out and "\n" not in out and "\\|" in out


def test_sanitize_escapes_markdown_link_injection():
    out = R.sanitize_text("click [here](javascript:alert(1))")
    assert "\\[" in out and "\\]" in out


def test_sanitize_bounds_length_and_adds_no_hidden_chars():
    out = R.sanitize_text("x" * 5000, max_len=100)
    assert len(out) <= 100 and not (set(out) & set(R._BIDI_ZW))


@pytest.mark.parametrize("url,ok", [
    ("https://ok.example/x", True), ("http://insecure", False),
    ("javascript:alert(1)", False), ("data:text/html,x", False), (None, False)])
def test_safe_url(url, ok):
    assert (R.safe_url(url) is not None) == ok


# ── structured queries (Phase 12) ───────────────────────────────────────────────────
def test_arxiv_query_ors_within_group_ands_across_groups():
    q = R.build_arxiv_query([["espresso", "coffee extraction"], ["porous media", "packed bed"]])
    assert q == '(all:"espresso" OR all:"coffee extraction") AND (all:"porous media" OR all:"packed bed")'


def test_crossref_query_uses_first_synonym_per_group():
    assert R.build_crossref_query([["espresso", "coffee"], ["porous", "bed"]]) == "espresso porous"


def test_query_build_handles_empty_groups():
    assert R.build_arxiv_query([]) == "" and R.build_crossref_query([[]]) == ""


def test_source_url_crossref_is_https_encoded():
    url = R.build_source_url("crossref", _query(groups=[["coffee bed"]]), "2026-06-01")
    assert url.startswith("https://api.crossref.org") and "from-index-date" in url and "mailto=" in url


def test_source_url_arxiv_boolean_and_max_results():
    url = R.build_source_url("arxiv", _query(groups=[["a"], ["b"]], cap=7), "2026-06-01")
    assert "max_results=7" in url and "AND" in urllib.parse.unquote(url)


# ── rate limiting (Phase 11) ────────────────────────────────────────────────────────
def test_arxiv_limiter_spaces_requests_by_three_seconds():
    clock = {"t": 0.0}
    slept = []

    def now():
        return clock["t"]

    def sleep(s):
        slept.append(s)
        clock["t"] += s

    lim = R.RateLimiter(3.0, now=now, sleep=sleep)
    lim.wait()
    lim.wait()
    assert slept and abs(slept[0] - 3.0) < 1e-9


def test_source_policies_differ():
    lims = R.make_limiters()
    assert lims["arxiv"].min_interval == 3.0 and lims["crossref"].min_interval == 1.0


def test_offline_scan_never_sleeps(monkeypatch):
    import time
    monkeypatch.setattr(time, "sleep", lambda *_: (_ for _ in ()).throw(AssertionError("slept!")))
    _scan(_cfg(_query()))


# ── fetch: timeout / 429 / non-429 (Phase 11) ───────────────────────────────────────
def test_timeout_bounded_retries():
    calls = {"n": 0}

    def opener(req, timeout=None):
        calls["n"] += 1
        raise urllib.error.URLError("timed out")

    text, status = R._http_get("http://x", retries=2, opener=opener, sleep=lambda *_: None)
    assert text is None and status == "timeout" and calls["n"] == 3


def test_rate_limit_429_retries_then_gives_up():
    calls = {"n": 0}

    def opener(req, timeout=None):
        calls["n"] += 1
        raise urllib.error.HTTPError("http://x", 429, "Too Many", {}, None)

    text, status = R._http_get("http://x", retries=2, opener=opener, sleep=lambda *_: None)
    assert text is None and status == "rate_limited" and calls["n"] == 3


def test_non_429_fails_fast():
    calls = {"n": 0}

    def opener(req, timeout=None):
        calls["n"] += 1
        raise urllib.error.HTTPError("http://x", 404, "NF", {}, None)

    text, status = R._http_get("http://x", retries=3, opener=opener, sleep=lambda *_: None)
    assert status == "error" and calls["n"] == 1


# ── lookback window (Phase 13) ──────────────────────────────────────────────────────
def test_date_window():
    assert R.date_window("2026-07-17", 21) == ("2026-06-26", "2026-07-17")


def test_within_window_keeps_recent_and_yearonly_drops_old():
    def c(d):
        return R.Candidate("s", "t", [], d, None, None, None, None, None, "", "q")
    assert R.within_window(c("2026-07-01"), "2026-06-26", "2026-07-17")
    assert R.within_window(c("2026"), "2026-06-26", "2026-07-17")
    assert not R.within_window(c("2026-01-01"), "2026-06-26", "2026-07-17")


def test_scan_applies_lookback():
    res = R.scan(_cfg(_query(lookback=10)), scan_date="2026-07-17", fixtures_dir=FIX)
    assert res.candidates == []


# ── scan behaviors ──────────────────────────────────────────────────────────────────
def test_cross_source_doi_duplicate_merges():
    res = _scan(_cfg(_query()))
    ids = [R.normalize_doi(c.doi) for c in res.candidates if c.doi]
    assert ids.count("10.1000/shared.dup.1") == 1
    merged = [c for c in res.candidates if c.doi and R.normalize_doi(c.doi) == "10.1000/shared.dup.1"][0]
    assert "arxiv" in merged.sources and "crossref" in merged.sources


def test_merge_keeps_more_complete_authors():
    a = R.Candidate("arxiv", "Same Work", ["A"], "2026-06-01", None, None, None, None, None, "", "q", sources=["arxiv"])
    b = R.Candidate("crossref", "same work", ["A", "B", "C"], "2026-06-02", "2026-06-02", None, None, None, None, "", "q", sources=["crossref"])
    merged = R.merge_candidates([a, b])
    assert len(merged) == 1 and merged[0].authors == ["A", "B", "C"] and merged[0].date == "2026-06-01"


def test_exclusions_drop_candidates():
    with_ex = _scan(_cfg(_query(exclusions=["barista training", "marketing"])))
    assert not any("barista training guide" in c.title.lower() for c in with_ex.candidates)
    without = _scan(_cfg(_query(exclusions=[])))
    assert any("barista training guide" in c.title.lower() for c in without.candidates)


def test_disabled_query_not_scanned():
    assert _scan(_cfg(_query(enabled=False))).candidates == []


def test_already_recorded_excluded():
    first = _scan(_cfg(_query()))
    recorded = {c.identity() for c in first.candidates}
    assert _scan(_cfg(_query()), recorded_ids=recorded).candidates == []


def test_deterministic_ordering():
    a = [c.identity() for c in _scan(_cfg(_query())).candidates]
    b = [c.identity() for c in _scan(_cfg(_query())).candidates]
    assert a == b


def test_query_subset_limits_scan():
    cfg = _cfg(_query("keep"), _query("drop"))
    res = R.scan(cfg, scan_date="2026-07-17", fixtures_dir=FIX, query_subset=["keep"])
    assert all(c.query_id == "keep" for c in res.candidates)


# ── source health (Phase 16) ────────────────────────────────────────────────────────
def test_source_failure_is_not_a_silent_empty_success():
    def http_get(url, limiter=None):
        if "arxiv" in url:
            return None, "timeout"
        return '{"message":{"items":[]}}', "ok"
    res = R.scan(_cfg(_query(groups=[["coffee"]])), scan_date="2026-07-17", http_get=http_get, limiters={})
    arxiv = [r for r in res.source_runs if r.source == "arxiv"][0]
    assert arxiv.status in ("failed", "rate_limited") and arxiv.error_category == "timeout"
    assert res.total_status in ("partial", "failed")


def test_all_sources_ok_is_success():
    assert _scan(_cfg(_query())).total_status == "success"


# ── caps (Phase 18) ─────────────────────────────────────────────────────────────────
def test_global_scan_cap(monkeypatch):
    monkeypatch.setattr(R, "MAX_CANDIDATES_PER_SCAN", 1)
    res = _scan(_cfg(_query(cap=100)))
    assert len(res.candidates) <= 1 and res.counts["retained"] <= 1


# ── config validation (Phase 24) ────────────────────────────────────────────────────
def test_shipped_config_validates():
    pytest.importorskip("yaml", reason="pyyaml is a radar/dev extra, absent in the min-deps lane")
    cfg = R.load_config(_ROOT / "docs" / "research" / "radar_queries.yml")
    assert R.validate_config(cfg) == []


@pytest.mark.parametrize("mut,needle", [
    (lambda q: q.update(surprise=1), "unknown query field"),
    (lambda q: q.update(enabled="yes"), "enabled must be a boolean"),
    (lambda q: q.update(lookback_days=True), "lookback_days"),
    (lambda q: q.update(lookback_days=0), "lookback_days"),
    (lambda q: q.update(maximum_candidates=999), "maximum_candidates"),
    (lambda q: q.update(concept_groups=[]), "concept_groups"),
    (lambda q: q.update(concept_groups="coffee"), "concept_groups"),
    (lambda q: q.update(exclusions="x"), "exclusions must be a list"),
    (lambda q: q.update(source_families=["scholar"]), "unsupported source family"),
    (lambda q: q.update(last_human_review="2026-13-40"), "last_human_review"),
    (lambda q: q.update(owner=""), "owner"),
])
def test_config_rejects_bad_fields(mut, needle):
    q = _query()
    mut(q)
    problems = R.validate_config({"queries": [q]})
    assert any(needle in p for p in problems), problems


def test_config_rejects_duplicate_ids():
    problems = R.validate_config({"queries": [_query("dup"), _query("dup")]})
    assert any("duplicate query id" in p for p in problems)


# ── issue module (Phases 14/18/19/22/23) ────────────────────────────────────────────
def test_marker_is_hashed_not_raw_title():
    m = RI.candidate_marker("doi:10.1/x")
    assert "10.1/x" not in m and RI.marker_hash("doi:10.1/x") in m


def test_new_candidates_excludes_seen_hashes():
    cands = [{"identity": "doi:10.1/a"}, {"identity": "arxiv:2506.1"}]
    fresh = RI.new_candidates(cands, {RI.marker_hash("doi:10.1/a")})
    assert [c["identity"] for c in fresh] == ["arxiv:2506.1"]


def test_parse_markers_roundtrip():
    body = "x\n" + RI.candidate_marker("doi:10.1/a") + "\n" + RI.candidate_marker("arxiv:2506.1")
    assert RI.parse_markers(body) == {RI.marker_hash("doi:10.1/a"), RI.marker_hash("arxiv:2506.1")}


def test_monthly_labels_never_standing():
    assert "standing" not in RI.choose_labels() and RI.choose_labels() == ["research-radar", "triage"]


def test_select_monthly_issue_all_states():
    issues = [{"number": 9, "title": "Research radar — 2026-07", "state": "open"},
              {"number": 3, "title": "Research radar — 2026-07", "state": "open"}]
    assert RI.select_monthly_issue(issues, "Research radar — 2026-07")["number"] == 3


def _scan_dict(cands):
    return {"scan_date": "2026-07-17", "issue_title": "Research radar — 2026-07",
            "total_status": "success", "source_runs": [{"source": "arxiv", "status": "success",
            "queries_succeeded": 1, "queries_attempted": 1}], "candidates": cands}


def test_plan_create_when_no_issue():
    plan = RI.build_issue_plan(_scan_dict([{"identity": "doi:10.1/a", "title": "T"}]), set(), [], publish=True)
    assert plan["action"] == "create" and plan["labels"] == ["research-radar", "triage"]


def test_plan_comment_when_open_issue_exists():
    issues = [{"number": 5, "title": "Research radar — 2026-07", "state": "open"}]
    plan = RI.build_issue_plan(_scan_dict([{"identity": "doi:10.1/a", "title": "T"}]), set(), issues, publish=True)
    assert plan["action"] == "comment" and plan["existing_number"] == 5


def test_plan_needs_human_when_month_issue_closed():
    issues = [{"number": 5, "title": "Research radar — 2026-07", "state": "closed"}]
    plan = RI.build_issue_plan(_scan_dict([{"identity": "doi:10.1/a", "title": "T"}]), set(), issues, publish=True)
    assert plan["action"] == "needs_human"


def test_plan_dry_run_default():
    plan = RI.build_issue_plan(_scan_dict([{"identity": "doi:10.1/a", "title": "T"}]), set(), [], publish=False)
    assert plan["action"] == "dry-run"


def test_plan_skips_failed_scan():
    s = _scan_dict([{"identity": "doi:10.1/a", "title": "T"}])
    s["total_status"] = "failed"
    assert RI.build_issue_plan(s, set(), [], publish=True)["action"] == "skip"


def test_plan_skips_when_nothing_new():
    c = [{"identity": "doi:10.1/a", "title": "T"}]
    assert RI.build_issue_plan(_scan_dict(c), {RI.marker_hash("doi:10.1/a")}, [], publish=True)["action"] == "skip"


def test_issue_body_sanitizes_and_caps():
    evil = [{"identity": f"doi:10.1/{i}", "title": f"@evil <b>#{i}</b> " + "x" * 500,
             "source": "arxiv", "date": "2026-07-01", "match_reasons": ["coffee"], "query_id": "q"}
            for i in range(50)]
    body = RI.render_issue_body(_scan_dict(evil), evil, max_bytes=2000)
    assert len(body.encode("utf-8")) <= 2400 and "@evil" not in body and "<b>" not in body
    assert "omitted by the issue-body cap" in body


# ── acknowledgment (Phase 20) ───────────────────────────────────────────────────────
def test_arxiv_acknowledgment_present():
    res = _scan(_cfg(_query()))
    assert R.ARXIV_ACK in R.render_markdown(res)
    assert R.result_to_dict(res)["arxiv_acknowledgment"] == R.ARXIV_ACK


# ── guardrails ──────────────────────────────────────────────────────────────────────
def test_no_pdf_or_full_text():
    for mod in ("research_radar.py", "research_radar_issue.py"):
        assert ".pdf" not in (_ROOT / "tools" / mod).read_text().lower()
    for c in _scan(_cfg(_query())).candidates:
        assert len(c.abstract_excerpt) <= R.MAX_ABSTRACT_CHARS and not hasattr(c, "full_text")


def test_no_external_contact_or_submission_code():
    for mod in ("research_radar.py", "research_radar_issue.py"):
        src = (_ROOT / "tools" / mod).read_text().lower()
        for bad in ("smtplib", "sendmail", "send_message", "requests.post", "submit("):
            assert bad not in src


def test_scan_does_not_write_repo(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    before = set(tmp_path.rglob("*"))
    _scan(_cfg(_query()))
    assert set(tmp_path.rglob("*")) == before


def test_write_outputs_confined(tmp_path):
    info = R.write_outputs(_scan(_cfg(_query())), tmp_path / "radar")
    assert Path(info["json"]).resolve().is_relative_to((tmp_path / "radar").resolve())


# ══════════════════════════════════════════════════════════════════════════════════
# PR #45 REQUEST-CHANGES corrections: safe inputs, date quality, lookback, relevance (4A/D/E/F)
# ══════════════════════════════════════════════════════════════════════════════════
def test_parse_query_subset_valid():
    cfg = _cfg(_query("a"), _query("b"))
    assert R.parse_query_subset("a, b", cfg) == ["a", "b"]
    assert R.parse_query_subset("", cfg) == []


@pytest.mark.parametrize("raw", [
    "a,,b",              # empty member
    "a,a",               # duplicate
    "--queries",         # option-looking
    "-rf",               # option-looking
    "a;rm -rf /",        # shell metacharacters
    'a"quote',           # quote
    "a\nb",              # newline
    "unknown_id",        # not in config
])
def test_parse_query_subset_rejects_bad(raw):
    cfg = _cfg(_query("a"), _query("b"))
    with pytest.raises(ValueError):
        R.parse_query_subset(raw, cfg)


@pytest.mark.parametrize("date,expected_quality,expected_precision", [
    ("2026-07-01", "verified_within_window", "day"),
    ("2027-01-01", "future_date", "day"),
    ("2026-01-01", "out_of_window", "day"),
    ("2026-02-30", "invalid", "day"),
    ("2026", "partial_date", "year"),
    ("2026-06", "partial_date", "month"),
    ("2030", "future_date", "year"),
    ("", "unknown", "unknown"),
])
def test_classify_date(date, expected_quality, expected_precision):
    prec, qual = R.classify_date(date, "2026-06-26", "2026-07-17")
    assert (prec, qual) == (expected_precision, expected_quality)


def test_within_window_tags_and_drops_out_of_window():
    def c(d):
        return R.Candidate("s", "t", [], d, None, None, None, None, None, "", "q")
    keep = c("2026-07-01")
    assert R.within_window(keep, "2026-06-26", "2026-07-17")
    assert keep.date_quality == "verified_within_window"
    drop = c("2020-01-01")
    assert not R.within_window(drop, "2026-06-26", "2026-07-17")   # out_of_window dropped
    partial = c("2026")
    assert R.within_window(partial, "2026-06-26", "2026-07-17")    # retained but tagged
    assert partial.date_quality == "partial_date"


def test_scan_reports_heterogeneous_windows_and_query_runs():
    cfg = _cfg(_query("a", lookback=21), _query("b", lookback=45))
    res = R.scan(cfg, scan_date="2026-07-17", fixtures_dir=FIX)
    assert res.heterogeneous_windows is True
    ids = {qr["query_id"] for qr in res.query_runs}
    assert ids == {"a", "b"}
    looks = {qr["query_id"]: qr["lookback_days"] for qr in res.query_runs}
    assert looks == {"a": 21, "b": 45}
    # order-independence: reversing queries yields the same window set
    cfg2 = _cfg(_query("b", lookback=45), _query("a", lookback=21))
    res2 = R.scan(cfg2, scan_date="2026-07-17", fixtures_dir=FIX)
    assert {qr["date_from"] for qr in res.query_runs} == {qr["date_from"] for qr in res2.query_runs}


def test_required_any_anchor_filters_generic_hits():
    off_topic = R.Candidate("crossref", "A generic model of time series dynamics", [], "2026-07-01",
                            "2026-07-01", "10.1/x", None, None, None, "", "q")
    on_topic = R.Candidate("crossref", "A model of espresso extraction dynamics", [], "2026-07-01",
                           "2026-07-01", "10.1/y", None, None, None, "", "q")
    kept = R.apply_required_any([off_topic, on_topic], ["espresso", "coffee"])
    assert [c.doi for c in kept] == ["10.1/y"]
    # no anchors -> no-op
    assert len(R.apply_required_any([off_topic, on_topic], [])) == 2


def test_shipped_config_required_any_validates():
    pytest.importorskip("yaml", reason="pyyaml is a radar/dev extra")
    cfg = R.load_config(_ROOT / "docs" / "research" / "radar_queries.yml")
    assert R.validate_config(cfg) == []
    # a bad required_any is rejected
    bad = _query()
    bad["required_any"] = "espresso"   # string not list
    assert any("required_any" in p for p in R.validate_config({"queries": [bad]}))


# ── workflow trust boundaries (4B/4C) — static config checks ─────────────────────────
def test_radar_workflow_separates_permissions():
    pytest.importorskip("yaml")
    import yaml
    wf = yaml.safe_load((_ROOT / ".github" / "workflows" / "research-radar.yml").read_text())
    jobs = wf["jobs"]
    assert jobs["scan"]["permissions"] == {"contents": "read"}          # scan cannot write issues
    assert jobs["plan"]["permissions"] == {"contents": "read", "issues": "read"}
    assert jobs["publish"]["permissions"] == {"contents": "read", "issues": "write"}
    cond = jobs["publish"]["if"]
    assert "refs/heads/main" in cond and "trbrewer/puckworks" in cond
    assert "publish == 'true'" in cond and "status != 'failed'" in cond
