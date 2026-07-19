#!/usr/bin/env python3
"""Puckworks research radar — metadata discovery and triage (issue #42).

Discovers candidate literature metadata from OFFICIAL metadata APIs (arXiv, Crossref), paces
requests per source policy, normalizes/deduplicates/merges across sources, sanitizes untrusted
text, and emits a deterministic, capped triage worklist plus a per-source health report. It is a
*discovery* tool only:

    * discovery metadata is NOT evidence;
    * it never downloads PDFs or full text, and never bypasses a paywall;
    * it never edits a model card, a manuscript, the roadmap, or a submission plan;
    * it never contacts anyone and never submits anything.

Thanks to arXiv for use of its open-access interoperability (this does not imply arXiv endorses
Puckworks). Crossref metadata is used via the polite pool with an identifying User-Agent/mailto.

Commands
    python tools/research_radar.py scan --config docs/research/radar_queries.yml \\
        --date 2026-07-17 --out out/radar
    python tools/research_radar.py scan --offline-fixtures tests/fixtures/research_radar ...
    python tools/research_radar.py render --candidates out/radar/candidates.json
    python tools/research_radar.py verify --config docs/research/radar_queries.yml

Network is used ONLY by `scan` without --offline-fixtures. Tests always use --offline-fixtures.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from dataclasses import asdict, dataclass, field
from datetime import date as _date
from datetime import timedelta
from pathlib import Path
from typing import Callable, Iterable

USER_AGENT = "puckworks-research-radar/1.0 (+https://github.com/trbrewer/puckworks; mailto:t_r_brewer@hotmail.com)"
ARXIV_ENDPOINT = "http://export.arxiv.org/api/query"
CROSSREF_ENDPOINT = "https://api.crossref.org/works"
CROSSREF_MAILTO = "t_r_brewer@hotmail.com"
MAX_ABSTRACT_CHARS = 500          # short metadata excerpt only — never full text
MAX_TITLE_CHARS = 300

# Source-specific request pacing (seconds between requests, including successful ones).
SOURCE_MIN_INTERVAL = {"arxiv": 3.0, "crossref": 1.0}

# Global output caps (issue-body cap lives in research_radar_issue).
MAX_CANDIDATES_PER_SCAN = 60
MAX_CANDIDATES_PER_SOURCE = 40

ARXIV_ACK = "Thank you to arXiv for use of its open access interoperability."

TRIAGE_STATES = (
    "new", "inspect", "relevant", "already-covered", "out-of-scope", "method-only",
    "data-opportunity", "collaboration-opportunity", "venue-opportunity", "rejected-with-reason",
)
_SUPPORTED_SOURCES = ("arxiv", "crossref")


# ─────────────────────────────── records ─────────────────────────────────────────
@dataclass
class Candidate:
    source: str
    title: str
    authors: list[str]
    date: str                         # earliest (preprint) date, YYYY or YYYY-MM-DD
    published_date: str | None        # formal publication date, if distinct
    doi: str | None
    arxiv_id: str | None
    venue: str | None
    url: str | None
    abstract_excerpt: str
    query_id: str
    match_reasons: list[str] = field(default_factory=list)
    score: float = 0.0                # ordering ONLY — never a decision
    sources: list[str] = field(default_factory=list)
    date_precision: str = "unknown"   # day | month | year | unknown
    date_quality: str = "unknown"     # verified_within_window | partial_date | future_date | ...
    triage_state: str = "new"

    def identity(self) -> str:
        if self.doi:
            return "doi:" + normalize_doi(self.doi)
        if self.arxiv_id:
            return "arxiv:" + normalize_arxiv_id(self.arxiv_id)
        if self.url and self.url.startswith("https://"):
            return "url:" + self.url.rstrip("/").lower()
        return "title:" + title_key(self.title)


@dataclass
class SourceRun:
    source: str = ""
    status: str = "success"           # success | partial | failed | rate_limited | disabled
    queries_attempted: int = 0
    queries_succeeded: int = 0
    candidates_received: int = 0
    candidates_retained: int = 0
    attempts: int = 0
    error_category: str | None = None
    error_summary: str | None = None


@dataclass
class ScanResult:
    scan_date: str
    lookback_days: int                # DEFAULT lookback; per-query windows live in query_runs
    date_from: str                    # min across queries
    date_to: str                      # scan date
    total_status: str                 # success | partial | failed
    candidates: list[Candidate]
    source_runs: list[SourceRun]
    counts: dict
    query_runs: list[dict] = field(default_factory=list)   # per-query {id, lookback_days, from, to}
    heterogeneous_windows: bool = False


# ─────────────────────────────── normalization ───────────────────────────────────
def normalize_doi(doi: str | None) -> str:
    if not doi:
        return ""
    d = doi.strip().lower()
    d = re.sub(r"^https?://(dx\.)?doi\.org/", "", d)
    d = re.sub(r"^doi:", "", d)
    return d.strip()


def normalize_arxiv_id(arxiv_id: str | None) -> str:
    if not arxiv_id:
        return ""
    a = arxiv_id.strip().lower()
    a = re.sub(r"^https?://arxiv\.org/abs/", "", a)
    a = re.sub(r"^arxiv:", "", a)
    a = re.sub(r"v\d+$", "", a)
    return a.strip()


def title_key(title: str | None) -> str:
    if not title:
        return ""
    t = title.lower()
    t = re.sub(r"[^a-z0-9 ]+", " ", t)
    return re.sub(r"\s+", " ", t).strip()


# ─────────────────────────────── sanitization ────────────────────────────────────
_BIDI_ZW = "".join(chr(c) for c in (
    0x200B, 0x200C, 0x200D, 0x200E, 0x200F,
    0x202A, 0x202B, 0x202C, 0x202D, 0x202E,
    0x2066, 0x2067, 0x2068, 0x2069, 0xFEFF))
_BIDI_RE = re.compile("[" + re.escape(_BIDI_ZW) + "]")
_CTRL_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")


def sanitize_text(text: str | None, *, max_len: int = MAX_TITLE_CHARS) -> str:
    """Render untrusted metadata inert for a GitHub issue: strip control/bidi chars and HTML,
    collapse newlines, escape table/link metacharacters, neutralize @mentions and #refs, and
    bound length. Introduces no zero-width/bidi characters of its own."""
    if not text:
        return ""
    s = _BIDI_RE.sub("", text)
    s = _CTRL_RE.sub("", s)
    s = re.sub(r"<[^>]*>", "", s)                       # strip raw HTML tags
    s = s.replace("\r", " ").replace("\n", " ")
    s = re.sub(r"\s+", " ", s).strip()
    s = s.replace("|", "\\|")                            # no Markdown table injection
    s = s.replace("[", "\\[").replace("]", "\\]")        # no Markdown link injection
    s = re.sub(r"(?<!\w)@(?=\w)", "@ ", s)               # neutralize @mentions
    s = re.sub(r"(?<!\w)#(?=\d)", "# ", s)               # break #123 issue references
    if len(s) > max_len:
        s = s[: max(0, max_len - 3)].rstrip() + "..."
    return s


def safe_url(url: str | None) -> str | None:
    """Return the URL only if it is HTTPS; reject javascript:/data:/other schemes."""
    if not url or not isinstance(url, str):
        return None
    u = url.strip()
    return u if u.lower().startswith("https://") else None


# ─────────────────────────────── parsing ─────────────────────────────────────────
_ATOM = "{http://www.w3.org/2005/Atom}"
_ARXIV_NS = "{http://arxiv.org/schemas/atom}"


def parse_arxiv(xml_text: str, query_id: str) -> list[Candidate]:
    out: list[Candidate] = []
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError:
        return out
    for entry in root.findall(f"{_ATOM}entry"):
        title = (entry.findtext(f"{_ATOM}title") or "").strip()
        if not title:
            continue
        summary = (entry.findtext(f"{_ATOM}summary") or "").strip()
        raw_id = (entry.findtext(f"{_ATOM}id") or "").strip()
        arxiv_id = normalize_arxiv_id(raw_id)
        doi = entry.findtext(f"{_ARXIV_NS}doi")
        published = (entry.findtext(f"{_ATOM}published") or "").strip()[:10]
        authors = [a.findtext(f"{_ATOM}name", "").strip() for a in entry.findall(f"{_ATOM}author")]
        out.append(Candidate(
            source="arxiv", title=re.sub(r"\s+", " ", title), authors=[a for a in authors if a],
            date=published, published_date=None, doi=doi, arxiv_id=arxiv_id or None,
            venue="arXiv", url=safe_url(raw_id) or raw_id or None,
            abstract_excerpt=re.sub(r"\s+", " ", summary)[:MAX_ABSTRACT_CHARS],
            query_id=query_id, sources=["arxiv"]))
    return out


def parse_crossref(json_text: str, query_id: str) -> list[Candidate]:
    out: list[Candidate] = []
    try:
        data = json.loads(json_text)
        items = data["message"]["items"]
    except (ValueError, KeyError, TypeError):
        return out
    for it in items:
        title = " ".join(it.get("title") or []).strip()
        if not title:
            continue
        authors = []
        for a in it.get("author", []) or []:
            name = " ".join(x for x in (a.get("given"), a.get("family")) if x).strip()
            if name:
                authors.append(name)
        parts = (it.get("issued", {}).get("date-parts") or [[None]])[0]
        date = "-".join(f"{p:02d}" if i else str(p) for i, p in enumerate(parts) if p is not None)
        venue = " ".join(it.get("container-title") or []) or it.get("type")
        excerpt = re.sub(r"<[^>]+>", "", it.get("abstract", "") or "").strip()
        out.append(Candidate(
            source="crossref", title=re.sub(r"\s+", " ", title), authors=authors,
            date=date, published_date=date, doi=it.get("DOI"), arxiv_id=None, venue=venue,
            url=safe_url(it.get("URL")),
            abstract_excerpt=re.sub(r"\s+", " ", excerpt)[:MAX_ABSTRACT_CHARS],
            query_id=query_id, sources=["crossref"]))
    return out


# ─────────────────────────────── query building ──────────────────────────────────
def _terms(concept_groups) -> list[list[str]]:
    return [[t for t in group if t] for group in (concept_groups or []) if any(group)]


def build_arxiv_query(concept_groups) -> str:
    """AND across concept groups, OR within a synonym group, quoted, field-prefixed all:."""
    parts = []
    for group in _terms(concept_groups):
        ors = " OR ".join('all:"%s"' % t for t in group)
        parts.append("(" + ors + ")")
    return " AND ".join(parts)


def build_crossref_query(concept_groups) -> str:
    """Crossref free-text bibliographic query (Crossref ranks rather than ANDing): first synonym
    of each concept group."""
    return " ".join(group[0] for group in _terms(concept_groups) if group)


def all_terms(query: dict) -> list[str]:
    return [t for group in _terms(query.get("concept_groups")) for t in group]


# ─────────────────────────────── scoring / filtering ─────────────────────────────
def score_candidate(cand: Candidate, terms: Iterable[str]) -> None:
    haystack = (cand.title + " " + cand.abstract_excerpt).lower()
    cand.match_reasons = sorted({t for t in terms if t.lower() in haystack})
    cand.score = float(len(cand.match_reasons))


def apply_exclusions(cands: list[Candidate], exclusions: Iterable[str]) -> list[Candidate]:
    ex = [e.lower() for e in (exclusions or []) if e]
    if not ex:
        return list(cands)
    return [c for c in cands
            if not any(e in (c.title + " " + c.abstract_excerpt).lower() for e in ex)]


def apply_required_any(cands: list[Candidate], required_any: Iterable[str]) -> list[Candidate]:
    """Keep only candidates whose title/abstract contains at least one required domain anchor.
    Tightens broad free-text sources (e.g. a generic 'model' Crossref hit) — with no anchors
    configured, this is a no-op."""
    anchors = [a.lower() for a in (required_any or []) if a]
    if not anchors:
        return list(cands)
    return [c for c in cands
            if any(a in (c.title + " " + c.abstract_excerpt).lower() for a in anchors)]


def classify_date(date: str | None, date_from: str, date_to: str) -> tuple[str, str]:
    """Return (precision, quality). Precision: day|month|year|unknown. Quality:
    verified_within_window | partial_date | future_date | out_of_window | invalid | unknown.
    A year/month-only date does NOT satisfy a day-level recency window (partial_date); a full
    future date is future_date (forthcoming), not 'already published'; impossible dates are invalid."""
    d = (date or "").strip()
    if not d:
        return "unknown", "unknown"
    if re.fullmatch(r"\d{4}", d):
        precision = "year"
    elif re.fullmatch(r"\d{4}-\d{2}", d):
        precision = "month"
    elif re.fullmatch(r"\d{4}-\d{2}-\d{2}", d[:10]) and len(d) >= 10:
        precision = "day"
    else:
        return "unknown", "unknown"

    if precision == "day":
        try:
            _date.fromisoformat(d[:10])
        except ValueError:
            return "day", "invalid"
        if d[:10] > date_to:
            return "day", "future_date"
        if d[:10] < date_from:
            return "day", "out_of_window"
        return "day", "verified_within_window"
    # year/month-only: cannot satisfy a day window; classify future vs uncertain by the coarse bound
    coarse = d if precision == "month" else d + "-01"
    if coarse > date_to[:7] + "-99":   # entirely after the window's month
        return precision, "future_date"
    return precision, "partial_date"


# quality classes that a scan RETAINS (each still human-triaged); out_of_window/invalid are dropped
_RETAINED_QUALITY = {"verified_within_window", "partial_date", "future_date", "unknown"}


def within_window(cand: Candidate, date_from: str, date_to: str) -> bool:
    """Retain a candidate unless its full date is out of window or impossible. Partial/future/unknown
    dates are retained but tagged (see classify_date) so they are never treated as ordinary recent."""
    precision, quality = classify_date(cand.date, date_from, date_to)
    cand.date_precision, cand.date_quality = precision, quality
    return quality in _RETAINED_QUALITY


def parse_query_subset(raw: str | None, cfg: dict) -> list[str]:
    """Parse a comma-separated query-id subset safely. Rejects empty members, duplicates, option-
    looking tokens, and unknown/unconfigured ids. Never lets a value become another CLI option."""
    if not raw or not raw.strip():
        return []
    known = {q.get("id") for q in cfg.get("queries", [])}
    seen: list[str] = []
    for token in raw.split(","):
        t = token.strip()
        if not t:
            raise ValueError("empty query-subset member")
        if t.startswith("-"):
            raise ValueError(f"query id must not look like an option: {t!r}")
        if not re.fullmatch(r"[A-Za-z0-9._-]+", t) or t.startswith("-"):
            raise ValueError(f"invalid query id: {t!r}")
        if t in seen:
            raise ValueError(f"duplicate query id in subset: {t!r}")
        if t not in known:
            raise ValueError(f"unknown query id: {t!r}")
        seen.append(t)
    return seen


def merge_candidates(cands: Iterable[Candidate]) -> list[Candidate]:
    """Merge records that resolve to the same identity across sources; keep both identifiers, the
    more complete author list, the earliest preprint date, and the formal publication date."""
    by_id: dict[str, Candidate] = {}
    order: list[str] = []
    for c in cands:
        key = c.identity()
        if key not in by_id:
            by_id[key] = c
            order.append(key)
            continue
        base = by_id[key]
        base.doi = base.doi or c.doi
        base.arxiv_id = base.arxiv_id or c.arxiv_id
        base.venue = base.venue or c.venue
        base.url = base.url or c.url
        if len(c.authors) > len(base.authors):
            base.authors = c.authors
        dates = [d for d in (base.date, c.date) if d]
        if dates:
            base.date = min(dates)
        base.published_date = base.published_date or c.published_date or c.date
        for s in c.sources:
            if s not in base.sources:
                base.sources.append(s)
        base.source = "+".join(sorted(set(base.sources)))
        base.match_reasons = sorted(set(base.match_reasons) | set(c.match_reasons))
        base.score = max(base.score, c.score)
    return [by_id[k] for k in order]


def exclude_recorded(cands: Iterable[Candidate], recorded_ids: set[str]) -> list[Candidate]:
    return [c for c in cands if c.identity() not in recorded_ids]


def sort_candidates(cands: list[Candidate]) -> list[Candidate]:
    return sorted(cands, key=lambda c: (-c.score, _neg_date(c.date), c.identity()))


def _neg_date(date: str) -> str:
    digits = re.sub(r"\D", "", date or "").ljust(8, "0")[:8]
    return "".join(chr(ord("9") - int(d)) for d in digits)


def date_window(scan_date: str, lookback_days: int) -> tuple[str, str]:
    y, m, d = (int(x) for x in scan_date.split("-"))
    to = _date(y, m, d)
    frm = to - timedelta(days=int(lookback_days))
    return frm.isoformat(), to.isoformat()


# ─────────────────────────────── config ──────────────────────────────────────────
def load_config(path: str | Path) -> dict:
    import yaml  # radar/dev extra — not a core dependency

    with open(path, encoding="utf-8") as fh:
        return yaml.safe_load(fh)


_QUERY_FIELDS = {"id", "title", "enabled", "lookback_days", "maximum_candidates", "global_priority",
                 "concept_groups", "required_any", "exclusions", "source_families",
                 "source_queries", "relevance_notes", "coupled_cards", "last_human_review", "owner"}
_ISO_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def _is_int(v) -> bool:
    return isinstance(v, int) and not isinstance(v, bool)


def _valid_iso_date(v) -> bool:
    if isinstance(v, _date):          # YAML parses an unquoted ISO date to a datetime.date
        return True
    if not isinstance(v, str) or not _ISO_DATE.match(v):
        return False
    try:
        _date.fromisoformat(v)
        return True
    except ValueError:
        return False


def validate_config(cfg: dict) -> list[str]:
    problems: list[str] = []
    queries = cfg.get("queries")
    if not isinstance(queries, list) or not queries:
        return ["config has no 'queries' list"]
    seen = set()
    for q in queries:
        qid = q.get("id", "<no id>")
        if not isinstance(qid, str) or not qid:
            problems.append("a query has an empty/non-string id")
        if qid in seen:
            problems.append(f"duplicate query id: {qid}")
        seen.add(qid)
        for f in q:
            if f not in _QUERY_FIELDS:
                problems.append(f"{qid}: unknown query field {f!r}")
        if not isinstance(q.get("title"), str) or not q.get("title"):
            problems.append(f"{qid}: title must be a non-empty string")
        if not isinstance(q.get("enabled"), bool):
            problems.append(f"{qid}: enabled must be a boolean")
        if not _is_int(q.get("lookback_days")) or q.get("lookback_days", 0) <= 0:
            problems.append(f"{qid}: lookback_days must be a positive integer")
        mc = q.get("maximum_candidates")
        if not _is_int(mc) or mc <= 0 or mc > 100:
            problems.append(f"{qid}: maximum_candidates must be a positive integer <= 100")
        groups = q.get("concept_groups")
        if not isinstance(groups, list) or not groups:
            problems.append(f"{qid}: concept_groups must be a non-empty list of string lists")
        else:
            for g in groups:
                if not isinstance(g, list) or not g or not all(isinstance(t, str) and t for t in g):
                    problems.append(f"{qid}: each concept group must be a non-empty list of strings")
        if "exclusions" in q and not (isinstance(q["exclusions"], list)
                                      and all(isinstance(t, str) for t in q["exclusions"])):
            problems.append(f"{qid}: exclusions must be a list of strings")
        if "required_any" in q and not (isinstance(q["required_any"], list)
                                        and all(isinstance(t, str) and t for t in q["required_any"])):
            problems.append(f"{qid}: required_any must be a list of non-empty strings")
        for src in q.get("source_families", _SUPPORTED_SOURCES):
            if src not in _SUPPORTED_SOURCES:
                problems.append(f"{qid}: unsupported source family {src!r}")
        if not _valid_iso_date(q.get("last_human_review")):
            problems.append(f"{qid}: last_human_review must be a real ISO date")
        if not isinstance(q.get("owner"), str) or not q.get("owner"):
            problems.append(f"{qid}: owner must be a non-empty string")
    return problems


# ─────────────────────────────── rate limiting + fetch ───────────────────────────
class RateLimiter:
    """Enforce a minimum interval between requests for one source. Every request participates —
    the limiter waits before the call, not only after an error. Clock/sleep are injectable."""

    def __init__(self, min_interval: float, *, now: Callable[[], float] | None = None,
                 sleep: Callable[[float], None] | None = None):
        import time as _time
        self.min_interval = float(min_interval)
        self._now = now or _time.monotonic
        self._sleep = sleep or _time.sleep
        self._last: float | None = None

    def wait(self) -> None:
        if self._last is not None:
            remaining = self.min_interval - (self._now() - self._last)
            if remaining > 0:
                self._sleep(remaining)
        self._last = self._now()


def _http_get(url: str, *, timeout: float = 20.0, retries: int = 2,
              opener: Callable[..., object] = urllib.request.urlopen,
              limiter: RateLimiter | None = None,
              sleep: Callable[[float], None] | None = None) -> tuple[str | None, str]:
    """GET text with pacing + bounded retry. Returns (text|None, status) where status is
    'ok' | 'timeout' | 'rate_limited' | 'error'."""
    import time as _time
    sleep = sleep or _time.sleep
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    attempt = 0
    last_status = "error"
    while attempt <= retries:
        if limiter is not None:
            limiter.wait()                       # pace BEFORE every request, including retries
        try:
            resp = opener(req, timeout=timeout)
            data = resp.read()
            return (data.decode("utf-8", "replace") if isinstance(data, bytes) else str(data)), "ok"
        except urllib.error.HTTPError as exc:
            if exc.code == 429:
                last_status = "rate_limited"
                if attempt < retries:
                    retry_after = exc.headers.get("Retry-After") if getattr(exc, "headers", None) else None
                    try:
                        sleep(float(retry_after) if retry_after else (1.0 + attempt))
                    except (TypeError, ValueError):
                        sleep(1.0 + attempt)
                    attempt += 1
                    continue
                return None, "rate_limited"
            return None, "error"
        except (urllib.error.URLError, TimeoutError, OSError):
            last_status = "timeout"
            if attempt < retries:
                sleep(0.5 + attempt)
                attempt += 1
                continue
            return None, "timeout"
    return None, last_status


def _fixture_text(fixtures_dir: Path, source: str, query_id: str) -> str | None:
    ext = "xml" if source == "arxiv" else "json"
    for name in (f"{source}_{query_id}.{ext}", f"{source}.{ext}"):
        p = fixtures_dir / name
        if p.exists():
            return p.read_text(encoding="utf-8")
    return None


def build_source_url(source: str, query: dict, date_from: str) -> str:
    n = int(query.get("maximum_candidates", 8))
    groups = query.get("concept_groups")
    if source == "arxiv":
        q = urllib.parse.quote(build_arxiv_query(groups) or 'all:"coffee"')
        return (f"{ARXIV_ENDPOINT}?search_query={q}&max_results={n}"
                f"&sortBy=submittedDate&sortOrder=descending")
    params = urllib.parse.urlencode({
        "query.bibliographic": build_crossref_query(groups) or "coffee",
        "filter": f"from-index-date:{date_from}",
        "rows": n, "mailto": CROSSREF_MAILTO, "sort": "published", "order": "desc"})
    return f"{CROSSREF_ENDPOINT}?{params}"


# ─────────────────────────────── scan ────────────────────────────────────────────
def scan(cfg: dict, *, scan_date: str, fixtures_dir: Path | None = None,
         recorded_ids: set[str] | None = None, query_subset: list[str] | None = None,
         http_get: Callable[..., tuple[str | None, str]] = _http_get,
         limiters: dict | None = None) -> ScanResult:
    recorded_ids = recorded_ids or set()
    default_lookback = int(cfg.get("defaults", {}).get("lookback_days", 21))
    collected: list[Candidate] = []
    runs = {s: SourceRun(source=s) for s in _SUPPORTED_SOURCES}
    query_runs: list[dict] = []

    for query in cfg.get("queries", []):
        if query_subset and query["id"] not in query_subset:
            continue
        if not query.get("enabled", False):
            continue
        lookback = int(query.get("lookback_days", default_lookback))
        date_from, date_to = date_window(scan_date, lookback)
        query_runs.append({"query_id": query["id"], "lookback_days": lookback,
                           "date_from": date_from, "date_to": date_to})
        per_query: list[Candidate] = []
        for source in query.get("source_families", _SUPPORTED_SOURCES):
            run = runs[source]
            run.queries_attempted += 1
            run.attempts += 1
            if fixtures_dir is not None:
                text = _fixture_text(fixtures_dir, source, query["id"])
                status = "ok" if text is not None else "error"
            else:
                url = build_source_url(source, query, date_from)
                text, status = http_get(url, limiter=(limiters or {}).get(source))
            if status != "ok" or not text:
                run.error_category = status
                run.error_summary = f"{source} query {query['id']}: {status}"
                continue
            run.queries_succeeded += 1
            parsed = (parse_arxiv(text, query["id"]) if source == "arxiv"
                      else parse_crossref(text, query["id"]))
            run.candidates_received += len(parsed)
            for c in parsed:
                score_candidate(c, all_terms(query))
            per_query.extend(parsed)
        per_query = apply_exclusions(per_query, query.get("exclusions", []))
        per_query = apply_required_any(per_query, query.get("required_any", []))
        per_query = [c for c in per_query if within_window(c, date_from, date_to)]
        per_query = sort_candidates(per_query)[: int(query.get("maximum_candidates", 8))]
        collected.extend(per_query)

    merged = merge_candidates(collected)
    fresh = exclude_recorded(merged, recorded_ids)
    fresh = sort_candidates(fresh)
    capped = _apply_caps(fresh)

    for run in runs.values():
        run.candidates_retained = sum(1 for c in capped if run.source in c.sources)
        if run.queries_attempted == 0:
            run.status = "disabled"
        elif run.queries_succeeded == run.queries_attempted:
            run.status = "success"
        elif run.queries_succeeded == 0:
            run.status = "rate_limited" if run.error_category == "rate_limited" else "failed"
        else:
            run.status = "partial"

    lookbacks = {qr["lookback_days"] for qr in query_runs}
    heterogeneous = len(lookbacks) > 1
    date_from = min((qr["date_from"] for qr in query_runs), default=date_window(scan_date, default_lookback)[0])
    date_to = date_window(scan_date, default_lookback)[1]
    counts = {"discovered": sum(r.candidates_received for r in runs.values()),
              "merged": len(merged), "omitted_prior_identity": len(merged) - len(fresh),
              "omitted_by_cap": len(fresh) - len(capped), "retained": len(capped),
              "verified_within_window": sum(1 for c in capped if c.date_quality == "verified_within_window"),
              "partial_or_future_date": sum(1 for c in capped if c.date_quality in ("partial_date", "future_date"))}
    return ScanResult(scan_date=scan_date, lookback_days=default_lookback, date_from=date_from,
                      date_to=date_to, total_status=_total_status(runs.values()),
                      candidates=capped, source_runs=list(runs.values()), counts=counts,
                      query_runs=query_runs, heterogeneous_windows=heterogeneous)


def _apply_caps(cands: list[Candidate]) -> list[Candidate]:
    per_source: dict[str, int] = {}
    kept = []
    for c in cands:
        primary = c.sources[0] if c.sources else c.source
        if per_source.get(primary, 0) >= MAX_CANDIDATES_PER_SOURCE:
            continue
        per_source[primary] = per_source.get(primary, 0) + 1
        kept.append(c)
        if len(kept) >= MAX_CANDIDATES_PER_SCAN:
            break
    return kept


def _total_status(runs: Iterable[SourceRun]) -> str:
    active = [r for r in runs if r.status != "disabled"]
    if not active:
        return "failed"
    if all(r.status == "success" for r in active):
        return "success"
    if all(r.status in ("failed", "rate_limited") for r in active):
        return "failed"
    return "partial"


# ─────────────────────────────── rendering ───────────────────────────────────────
def radar_issue_title(date: str) -> str:
    m = re.match(r"(\d{4})-(\d{2})", date or "")
    ym = f"{m.group(1)}-{m.group(2)}" if m else "unknown"
    return f"Research radar — {ym}"


def render_markdown(result: ScanResult) -> str:
    lines = [
        f"# {radar_issue_title(result.scan_date)}",
        "",
        f"- **Scan date:** {result.scan_date}  ·  **window:** {result.date_from} -> {result.date_to}"
        f" ({result.lookback_days} d lookback)",
        f"- **Total scan status:** {result.total_status}",
        f"- **Candidates:** discovered {result.counts['discovered']} · merged "
        f"{result.counts['merged']} · omitted(prior) {result.counts['omitted_prior_identity']} · "
        f"omitted(cap) {result.counts['omitted_by_cap']} · retained {result.counts['retained']}",
        "",
        "### Source health",
    ]
    for r in result.source_runs:
        lines.append(
            f"- **{r.source}** — {r.status}: {r.queries_succeeded}/{r.queries_attempted} queries, "
            f"received {r.candidates_received}, retained {r.candidates_retained}"
            + (f" · error: {r.error_category}" if r.error_category else ""))
    lines += ["", "> **Discovery is not validation.** Every item is a triage candidate for a human.",
              "", "### Candidates"]
    for i, c in enumerate(result.candidates, 1):
        ident = (f"doi:{normalize_doi(c.doi)}" if c.doi
                 else (f"arXiv:{c.arxiv_id}" if c.arxiv_id else "no-id"))
        url = safe_url(c.url)
        link = f" ([{ident}]({url}))" if url else f" ({ident})"
        reasons = ", ".join(sanitize_text(r, max_len=40) for r in c.match_reasons) or "—"
        lines.append(f"{i}. **{sanitize_text(c.title)}** — {c.source} · {c.date or '—'}{link}  ")
        lines.append(f"   found by `{sanitize_text(c.query_id, max_len=60)}`; matched: "
                     f"{reasons} · triage: `new`")
    lines += ["", "### Triage states", "`" + "` · `".join(TRIAGE_STATES) + "`", "",
              f"_{ARXIV_ACK} Crossref metadata via the polite pool._"]
    return "\n".join(lines) + "\n"


def result_to_dict(result: ScanResult) -> dict:
    return {
        "scan_date": result.scan_date, "lookback_days": result.lookback_days,
        "date_from": result.date_from, "date_to": result.date_to,
        "total_status": result.total_status, "issue_title": radar_issue_title(result.scan_date),
        "counts": result.counts, "source_runs": [asdict(r) for r in result.source_runs],
        "query_runs": result.query_runs, "heterogeneous_windows": result.heterogeneous_windows,
        "candidates": [{**asdict(c), "identity": c.identity()} for c in result.candidates],
        "arxiv_acknowledgment": ARXIV_ACK,
    }


def write_outputs(result: ScanResult, out_dir: Path) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "candidates.json").write_text(
        json.dumps(result_to_dict(result), indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8")
    (out_dir / "radar.md").write_text(render_markdown(result), encoding="utf-8")
    return {"json": str(out_dir / "candidates.json"), "md": str(out_dir / "radar.md"),
            "count": len(result.candidates), "status": result.total_status}


# ─────────────────────────────── CLI ─────────────────────────────────────────────
def _result_from_dict(d: dict) -> ScanResult:
    cands = [Candidate(**{k: c.get(k) for k in (
        "source", "title", "authors", "date", "published_date", "doi", "arxiv_id", "venue",
        "url", "abstract_excerpt", "query_id", "match_reasons", "score", "sources",
        "date_precision", "date_quality", "triage_state") if k in c})
        for c in d.get("candidates", [])]
    runs = [SourceRun(**{k: r.get(k) for k in SourceRun().__dict__}) for r in d.get("source_runs", [])]
    return ScanResult(scan_date=d["scan_date"], lookback_days=d["lookback_days"],
                      date_from=d["date_from"], date_to=d["date_to"],
                      total_status=d["total_status"], candidates=cands, source_runs=runs,
                      counts=d["counts"], query_runs=d.get("query_runs", []),
                      heterogeneous_windows=d.get("heterogeneous_windows", False))


def _recorded_ids_from(path: str | None) -> set[str]:
    if not path:
        return set()
    p = Path(path)
    if not p.exists():
        return set()
    data = json.loads(p.read_text(encoding="utf-8"))
    return {c["identity"] for c in data.get("candidates", []) if c.get("identity")}


def make_limiters() -> dict:
    return {s: RateLimiter(iv) for s, iv in SOURCE_MIN_INTERVAL.items()}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("scan")
    s.add_argument("--config", default="docs/research/radar_queries.yml")
    s.add_argument("--offline-fixtures", default=None)
    s.add_argument("--date", required=True)
    s.add_argument("--recorded", default=None)
    s.add_argument("--queries", default=None, help="comma-separated query-id subset")
    s.add_argument("--out", default="out/radar")

    r = sub.add_parser("render")
    r.add_argument("--candidates", required=True)
    r.add_argument("--out", default="out/radar")

    v = sub.add_parser("verify")
    v.add_argument("--config", default="docs/research/radar_queries.yml")

    args = ap.parse_args(argv)

    if args.cmd == "verify":
        cfg = load_config(args.config)
        problems = validate_config(cfg)
        if problems:
            print("INVALID query config:", *problems, sep="\n  ", file=sys.stderr)
            return 1
        print(f"query config OK: {len(cfg['queries'])} queries "
              f"({sum(1 for q in cfg['queries'] if q.get('enabled'))} enabled)")
        return 0

    if args.cmd == "scan":
        cfg = load_config(args.config)
        problems = validate_config(cfg)
        if problems:
            print("INVALID query config; fix before scanning:", *problems, sep="\n  ", file=sys.stderr)
            return 1
        try:
            _date.fromisoformat(args.date)                 # reject impossible scan dates
        except ValueError:
            print(f"INVALID --date: {args.date!r} is not a real YYYY-MM-DD date", file=sys.stderr)
            return 1
        fixtures = Path(args.offline_fixtures) if args.offline_fixtures else None
        try:
            subset = parse_query_subset(args.queries, cfg) or None
        except ValueError as exc:
            print(f"INVALID --queries: {exc}", file=sys.stderr)
            return 1
        result = scan(cfg, scan_date=args.date, fixtures_dir=fixtures,
                      recorded_ids=_recorded_ids_from(args.recorded), query_subset=subset,
                      limiters=None if fixtures is not None else make_limiters())
        info = write_outputs(result, Path(args.out))
        print(f"scan complete: status={info['status']} {info['count']} candidates "
              f"-> {info['json']}, {info['md']}")
        return 0

    if args.cmd == "render":
        result = _result_from_dict(json.loads(Path(args.candidates).read_text(encoding="utf-8")))
        info = write_outputs(result, Path(args.out))
        print(f"render complete: {info['count']} candidates -> {info['json']}, {info['md']}")
        return 0

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
