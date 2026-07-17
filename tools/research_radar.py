#!/usr/bin/env python3
"""Puckworks research radar — metadata discovery and triage (issue #42).

Discovers candidate literature/venue metadata from OFFICIAL metadata APIs (arXiv, Crossref),
normalizes and deduplicates it, and emits a deterministic triage worklist. It is a *discovery*
tool only:

    * discovery metadata is NOT evidence;
    * it never downloads PDFs or full text, and never bypasses a paywall;
    * it never edits a model card, a manuscript, the roadmap, or a submission plan;
    * it never contacts anyone and never submits anything.

Every candidate is a triage item for a human. See docs/RESEARCH_RADAR.md for the policy.

Commands
    python tools/research_radar.py scan   --config docs/research/radar_queries.yml \\
        --date 2026-07-17 --out out/radar
    python tools/research_radar.py scan   --offline-fixtures tests/fixtures/research_radar ...
    python tools/research_radar.py render --candidates out/radar/candidates.json --date 2026-07-17
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
from pathlib import Path
from typing import Callable, Iterable

USER_AGENT = "puckworks-research-radar/1.0 (+https://github.com/trbrewer/puckworks; mailto:brewer@synthetik-technologies.com)"
ARXIV_ENDPOINT = "http://export.arxiv.org/api/query"
CROSSREF_ENDPOINT = "https://api.crossref.org/works"
MAX_ABSTRACT_CHARS = 500          # short metadata excerpt only — never full text
TRIAGE_STATES = (
    "new", "inspect", "relevant", "already-covered", "out-of-scope", "method-only",
    "data-opportunity", "collaboration-opportunity", "venue-opportunity", "rejected-with-reason",
)


# ─────────────────────────────── candidate record ────────────────────────────────
@dataclass
class Candidate:
    source: str                       # "arxiv" | "crossref"
    title: str
    authors: list[str]
    date: str                         # publication/preprint date (YYYY or YYYY-MM-DD)
    doi: str | None
    arxiv_id: str | None
    venue: str | None
    url: str | None
    abstract_excerpt: str
    query_id: str
    match_reasons: list[str] = field(default_factory=list)
    score: float = 0.0                # ordering ONLY — never a decision
    triage_state: str = "new"

    def identity(self) -> str:
        if self.doi:
            return "doi:" + normalize_doi(self.doi)
        if self.arxiv_id:
            return "arxiv:" + normalize_arxiv_id(self.arxiv_id)
        return "title:" + title_key(self.title)


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
    a = re.sub(r"v\d+$", "", a)       # drop version suffix
    return a.strip()


def title_key(title: str | None) -> str:
    if not title:
        return ""
    t = title.lower()
    t = re.sub(r"[^a-z0-9 ]+", " ", t)
    return re.sub(r"\s+", " ", t).strip()


# ─────────────────────────────── parsing ─────────────────────────────────────────
_ATOM = "{http://www.w3.org/2005/Atom}"
_ARXIV_NS = "{http://arxiv.org/schemas/atom}"


def parse_arxiv(xml_text: str, query_id: str) -> list[Candidate]:
    """Parse an arXiv Atom feed. Returns [] on malformed input (never raises)."""
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
        authors = [a.findtext(f"{_ATOM}name", "").strip()
                   for a in entry.findall(f"{_ATOM}author")]
        out.append(Candidate(
            source="arxiv", title=re.sub(r"\s+", " ", title), authors=[a for a in authors if a],
            date=published, doi=doi, arxiv_id=arxiv_id or None,
            venue="arXiv", url=raw_id or None,
            abstract_excerpt=re.sub(r"\s+", " ", summary)[:MAX_ABSTRACT_CHARS],
            query_id=query_id,
        ))
    return out


def parse_crossref(json_text: str, query_id: str) -> list[Candidate]:
    """Parse a Crossref /works response. Returns [] on malformed input (never raises)."""
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
            date=date, doi=it.get("DOI"), arxiv_id=None, venue=venue,
            url=it.get("URL"),
            abstract_excerpt=re.sub(r"\s+", " ", excerpt)[:MAX_ABSTRACT_CHARS],
            query_id=query_id,
        ))
    return out


# ─────────────────────────────── scoring / filtering ─────────────────────────────
def score_candidate(cand: Candidate, terms: Iterable[str]) -> None:
    """Attach match_reasons + an ordering score. NOT a relevance decision."""
    haystack = (cand.title + " " + cand.abstract_excerpt).lower()
    reasons = sorted({t for t in terms if t.lower() in haystack})
    cand.match_reasons = reasons
    cand.score = float(len(reasons))


def apply_exclusions(cands: list[Candidate], exclusions: Iterable[str]) -> list[Candidate]:
    ex = [e.lower() for e in exclusions if e]
    if not ex:
        return list(cands)
    keep = []
    for c in cands:
        hay = (c.title + " " + c.abstract_excerpt).lower()
        if not any(e in hay for e in ex):
            keep.append(c)
    return keep


def dedupe(cands: Iterable[Candidate]) -> list[Candidate]:
    """Deduplicate by DOI, then arXiv id, then normalized-title fallback (first wins)."""
    seen: dict[str, Candidate] = {}
    for c in cands:
        key = c.identity()
        if key not in seen:
            seen[key] = c
    return list(seen.values())


def exclude_recorded(cands: Iterable[Candidate], recorded_ids: set[str]) -> list[Candidate]:
    return [c for c in cands if c.identity() not in recorded_ids]


def sort_candidates(cands: list[Candidate]) -> list[Candidate]:
    """Deterministic ordering: score desc, then date desc, then identity asc."""
    return sorted(cands, key=lambda c: (-c.score, _neg_date(c.date), c.identity()))


def _neg_date(date: str) -> str:
    # Invert an ISO-ish date for descending sort while keeping string comparison stable.
    digits = re.sub(r"\D", "", date or "").ljust(8, "0")[:8]
    return "".join(chr(ord("9") - int(d)) for d in digits)


# ─────────────────────────────── config ──────────────────────────────────────────
def load_config(path: str | Path) -> dict:
    import yaml  # declared in the `radar` / `dev` extras — not a core dependency

    with open(path, encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def validate_config(cfg: dict) -> list[str]:
    problems: list[str] = []
    queries = cfg.get("queries")
    if not isinstance(queries, list) or not queries:
        return ["config has no 'queries' list"]
    seen = set()
    for q in queries:
        qid = q.get("id", "<no id>")
        if qid in seen:
            problems.append(f"duplicate query id: {qid}")
        seen.add(qid)
        for f in ("id", "title", "enabled", "source_families", "terms", "max_candidates"):
            if f not in q:
                problems.append(f"{qid}: missing field {f!r}")
        for src in q.get("source_families", []):
            if src not in ("arxiv", "crossref"):
                problems.append(f"{qid}: unsupported source family {src!r}")
    return problems


# ─────────────────────────────── fetching ────────────────────────────────────────
def _http_get(url: str, *, timeout: float = 20.0, retries: int = 2,
              opener: Callable[..., object] = urllib.request.urlopen,
              sleep: Callable[[float], None] = None) -> str | None:
    """GET text with a bounded retry. Returns None on timeout / repeated failure / rate limit.

    `opener` and `sleep` are injectable for tests — no live network in the test lane.
    """
    import time as _time
    sleep = sleep or _time.sleep
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    attempt = 0
    while attempt <= retries:
        try:
            resp = opener(req, timeout=timeout)
            data = resp.read()
            return data.decode("utf-8", "replace") if isinstance(data, bytes) else str(data)
        except urllib.error.HTTPError as exc:
            if exc.code == 429 and attempt < retries:   # rate limited — back off and retry
                sleep(1.0 + attempt)
                attempt += 1
                continue
            return None
        except (urllib.error.URLError, TimeoutError, OSError):
            if attempt < retries:
                sleep(0.5 + attempt)
                attempt += 1
                continue
            return None
    return None


def _fixture_text(fixtures_dir: Path, source: str, query_id: str) -> str | None:
    ext = "xml" if source == "arxiv" else "json"
    for name in (f"{source}_{query_id}.{ext}", f"{source}.{ext}"):
        p = fixtures_dir / name
        if p.exists():
            return p.read_text(encoding="utf-8")
    return None


def fetch_source(source: str, query: dict, *, fixtures_dir: Path | None,
                 http_get: Callable[..., str | None] = _http_get) -> str | None:
    if fixtures_dir is not None:
        return _fixture_text(fixtures_dir, source, query["id"])
    terms = " ".join(query.get("terms", []))
    n = int(query.get("max_candidates", 10))
    if source == "arxiv":
        q = urllib.parse.quote(f'all:"{terms}"') if terms else "all:coffee"
        url = f"{ARXIV_ENDPOINT}?search_query={q}&max_results={n}&sortBy=submittedDate&sortOrder=descending"
    else:
        params = urllib.parse.urlencode({"query": terms, "rows": n,
                                         "mailto": "brewer@synthetik-technologies.com"})
        url = f"{CROSSREF_ENDPOINT}?{params}"
    return http_get(url)


# ─────────────────────────────── scan ────────────────────────────────────────────
def scan(cfg: dict, *, fixtures_dir: Path | None = None,
         recorded_ids: set[str] | None = None,
         http_get: Callable[..., str | None] = _http_get) -> list[Candidate]:
    recorded_ids = recorded_ids or set()
    collected: list[Candidate] = []
    for query in cfg.get("queries", []):
        if not query.get("enabled", False):
            continue
        per_query: list[Candidate] = []
        for source in query.get("source_families", []):
            text = fetch_source(source, query, fixtures_dir=fixtures_dir, http_get=http_get)
            if not text:
                continue
            parsed = parse_arxiv(text, query["id"]) if source == "arxiv" \
                else parse_crossref(text, query["id"])
            for c in parsed:
                score_candidate(c, query.get("terms", []))
            per_query.extend(parsed)
        per_query = apply_exclusions(per_query, query.get("exclusions", []))
        per_query = sort_candidates(per_query)[: int(query.get("max_candidates", 10))]
        collected.extend(per_query)
    collected = dedupe(collected)
    collected = exclude_recorded(collected, recorded_ids)
    return sort_candidates(collected)


# ─────────────────────────────── rendering ───────────────────────────────────────
def radar_issue_title(date: str) -> str:
    """`Research radar — YYYY-MM` from a YYYY-MM-DD date. Monthly rolling issue."""
    m = re.match(r"(\d{4})-(\d{2})", date or "")
    ym = f"{m.group(1)}-{m.group(2)}" if m else "unknown"
    return f"Research radar — {ym}"


def render_markdown(cands: list[Candidate], date: str, cfg: dict | None = None) -> str:
    query_ids = sorted({c.query_id for c in cands})
    lines = [
        f"# {radar_issue_title(date)}",
        "",
        f"- **Scan date:** {date}",
        f"- **Queries with hits:** {', '.join(query_ids) or '(none)'}",
        f"- **Candidates:** {len(cands)}",
        "",
        "> **Discovery is not validation.** Every item below is a triage candidate for a human.",
        "> A hit does not change a model card, a claim, a manuscript, the roadmap, a submission",
        "> plan, or create any external contact. Official organizer/journal pages remain",
        "> authoritative for calls and deadlines.",
        "",
        "| # | title | source | date | id | matched | triage |",
        "|---|---|---|---|---|---|---|",
    ]
    for i, c in enumerate(cands, 1):
        ident = (f"[doi:{normalize_doi(c.doi)}](https://doi.org/{normalize_doi(c.doi)})"
                 if c.doi else (f"[arXiv:{c.arxiv_id}]({c.url})" if c.arxiv_id else "—"))
        title = c.title.replace("|", "\\|")
        reasons = ", ".join(c.match_reasons) or "—"
        lines.append(
            f"| {i} | {title} | {c.source} | {c.date or '—'} | {ident} | {reasons} | `new` |"
        )
    lines += [
        "",
        "### Triage states",
        "`" + "` · `".join(TRIAGE_STATES) + "`",
        "",
        "Assign a state per candidate. Do not reduce triage to a single opaque score.",
    ]
    return "\n".join(lines) + "\n"


def write_outputs(cands: list[Candidate], date: str, out_dir: Path, cfg: dict | None = None) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    payload = {
        "scan_date": date,
        "issue_title": radar_issue_title(date),
        "candidate_count": len(cands),
        # `identity` is added so downstream tooling (the weekly workflow) can dedupe against an
        # existing issue without re-deriving DOI/arXiv/title identity.
        "candidates": [{**asdict(c), "identity": c.identity()} for c in cands],
    }
    json_path = out_dir / "candidates.json"
    md_path = out_dir / "radar.md"
    json_path.write_text(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
                         encoding="utf-8")
    md_path.write_text(render_markdown(cands, date, cfg), encoding="utf-8")
    return {"json": str(json_path), "md": str(md_path), "count": len(cands)}


# ─────────────────────────────── CLI ─────────────────────────────────────────────
def _recorded_ids_from(path: str | None) -> set[str]:
    if not path:
        return set()
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    ids = set()
    for c in data.get("candidates", []):
        ids.add(Candidate(**{k: c.get(k) for k in (
            "source", "title", "authors", "date", "doi", "arxiv_id", "venue", "url",
            "abstract_excerpt", "query_id")}).identity())
    return ids


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("scan", help="discover candidates from metadata sources")
    s.add_argument("--config", default="docs/research/radar_queries.yml")
    s.add_argument("--offline-fixtures", default=None,
                   help="directory of frozen API responses (no network)")
    s.add_argument("--date", required=True, help="scan date YYYY-MM-DD (explicit; no wall clock)")
    s.add_argument("--recorded", default=None, help="prior candidates.json to exclude")
    s.add_argument("--out", default="out/radar")

    r = sub.add_parser("render", help="re-render Markdown+JSON from a candidates.json")
    r.add_argument("--candidates", required=True)
    r.add_argument("--date", required=True)
    r.add_argument("--out", default="out/radar")

    v = sub.add_parser("verify", help="validate the query configuration")
    v.add_argument("--config", default="docs/research/radar_queries.yml")

    args = ap.parse_args(argv)

    if args.cmd == "verify":
        cfg = load_config(args.config)
        problems = validate_config(cfg)
        if problems:
            print("INVALID query config:", file=sys.stderr)
            for p in problems:
                print("  -", p, file=sys.stderr)
            return 1
        n = sum(1 for q in cfg["queries"] if q.get("enabled"))
        print(f"query config OK: {len(cfg['queries'])} queries ({n} enabled)")
        return 0

    if args.cmd == "scan":
        cfg = load_config(args.config)
        problems = validate_config(cfg)
        if problems:
            print("INVALID query config; fix before scanning:", *problems, sep="\n  ", file=sys.stderr)
            return 1
        fixtures = Path(args.offline_fixtures) if args.offline_fixtures else None
        cands = scan(cfg, fixtures_dir=fixtures, recorded_ids=_recorded_ids_from(args.recorded))
        info = write_outputs(cands, args.date, Path(args.out), cfg)
        print(f"scan complete: {info['count']} candidates -> {info['json']}, {info['md']}")
        return 0

    if args.cmd == "render":
        data = json.loads(Path(args.candidates).read_text(encoding="utf-8"))
        cands = [Candidate(**{k: c.get(k) for k in (
            "source", "title", "authors", "date", "doi", "arxiv_id", "venue", "url",
            "abstract_excerpt", "query_id", "match_reasons", "score", "triage_state")})
            for c in data.get("candidates", [])]
        info = write_outputs(cands, args.date, Path(args.out))
        print(f"render complete: {info['count']} candidates -> {info['json']}, {info['md']}")
        return 0

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
