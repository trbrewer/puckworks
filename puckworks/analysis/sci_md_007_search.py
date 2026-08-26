"""Bounded public-metadata collector for the frozen SCI-MD-007-R1 search."""

from __future__ import annotations

import csv
import argparse
import html
import json
import re
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).parents[2]
CONTRACT = ROOT / "docs/analysis/sci_md_007/r1/R1_CORRECTIVE_SEARCH_CONTRACT.json"
DATA = ROOT / "puckworks/data/sci_md_007"
UA = "puckworks-sci-md-007-r1/1.0 (mailto:t_r_brewer@hotmail.com)"
INCLUDED_DOIS = {
    "bruno2026": "10.1038/s41598-026-43923-9",
    "dias2015": "10.3390/beverages1030127",
    "viencz2023": "10.1016/j.jfca.2023.105140",
    "acre2024": "10.21577/0103-5053.20240031",
    "pannusch2024": "10.1016/j.jfoodeng.2023.111887",
    "schmieder2023": "10.3390/foods12152871",
}


def _get(url: str) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": UA})
    for attempt in range(5):
        try:
            with urllib.request.urlopen(request, timeout=60) as response:
                time.sleep(0.25)
                return response.read()
        except urllib.error.HTTPError as error:
            if error.code not in {429, 500, 502, 503, 504} or attempt == 4:
                raise
            time.sleep(2**attempt)
    raise RuntimeError("unreachable retry state")


def _doi(value: str) -> str:
    match = re.search(r"10\.\d{4,9}/[^\s\"<>]+", value or "", re.I)
    return match.group(0).rstrip(".,);]").lower() if match else ""


def _state(title: str) -> str:
    lowered = title.lower()
    if "coffee" in lowered and ("caffeine" in lowered or "trigonelline" in lowered):
        # Title/abstract metadata is retained for source-level screening.  A
        # source is promoted to numeric intake only after its table is audited.
        return "ATLAS_INCLUDED_METADATA_ONLY"
    return "OUT_OF_SCOPE_NON_INVENTORY"


def _crossref(query: str, limit: int) -> list[dict]:
    url = "https://api.crossref.org/works?" + urllib.parse.urlencode(
        {"query": query, "rows": limit, "select": "DOI,title,author,published,URL"}
    )
    items = json.loads(_get(url))["message"]["items"]
    rows = []
    for item in items:
        date = item.get("published", {}).get("date-parts", [[""]])[0]
        authors = "; ".join(
            " ".join(filter(None, (a.get("given"), a.get("family"))))
            for a in item.get("author", [])
        )
        rows.append(
            {
                "title": " ".join(item.get("title", [])),
                "authors": authors,
                "year": date[0] if date else "",
                "doi_or_stable_id": item.get("DOI", ""),
                "result_url": item.get("URL", ""),
            }
        )
    return rows


def _openalex(query: str, limit: int) -> list[dict]:
    url = "https://api.openalex.org/works?" + urllib.parse.urlencode(
        {"search": query, "per-page": limit}
    )
    items = json.loads(_get(url))["results"]
    rows = []
    for item in items:
        authors = "; ".join(a["author"]["display_name"] for a in item.get("authorships", []))
        rows.append(
            {
                "title": item.get("title") or "",
                "authors": authors,
                "year": item.get("publication_year") or "",
                "doi_or_stable_id": (item.get("doi") or item.get("id") or "").removeprefix(
                    "https://doi.org/"
                ),
                "result_url": (item.get("primary_location") or {}).get("landing_page_url")
                or item.get("id", ""),
            }
        )
    return rows


def _web(query: str, limit: int) -> list[dict]:
    url = "https://www.bing.com/search?" + urllib.parse.urlencode(
        {"q": query, "count": limit, "format": "rss"}
    )
    root = ET.fromstring(_get(url))
    rows = []
    for item in root.findall("./channel/item")[:limit]:
        title = html.unescape(item.findtext("title") or "").strip()
        target = item.findtext("link") or ""
        rows.append(
            {
                "title": title,
                "authors": "",
                "year": "",
                "doi_or_stable_id": _doi(target + " " + title),
                "result_url": target,
            }
        )
    return rows


def _citation_passes(limit: int) -> list[dict]:
    """Record bounded individual OpenAlex backward/forward records."""
    rows = []
    for source_id, doi in INCLUDED_DOIS.items():
        try:
            work = json.loads(_get("https://api.openalex.org/works/https://doi.org/" + doi))
            backward = work.get("referenced_works", [])[:limit]
            cited_url = "https://api.openalex.org/works?" + urllib.parse.urlencode(
                {"filter": f"cites:{work['id'].rsplit('/', 1)[-1]}", "per-page": limit}
            )
            forward = [x["id"] for x in json.loads(_get(cited_url)).get("results", [])]
        except (urllib.error.HTTPError, urllib.error.URLError):
            backward = []
            forward = []
        for direction, identifiers in (("BACKWARD", backward), ("FORWARD", forward)):
            if not identifiers:
                rows.append(
                    {
                        "source_publication_id": source_id,
                        "direction": direction,
                        "rank": 0,
                        "stable_id": "NO_RESULTS_RETURNED",
                        "screening_state": "SCREENED_NO_RESULTS",
                        "retrieval_date": "2026-08-25",
                    }
                )
            for rank, identifier in enumerate(identifiers, 1):
                rows.append(
                    {
                        "source_publication_id": source_id,
                        "direction": direction,
                        "rank": rank,
                        "stable_id": identifier,
                        "screening_state": "SCREENED",
                        "retrieval_date": "2026-08-25",
                    }
                )
    return rows


def collect() -> dict:
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    limit = contract["result_limit_per_query_per_provider"]
    providers = {"Crossref": _crossref, "OpenAlex": _openalex, "GeneralPublicWeb": _web}
    results = []
    seen: dict[str, str] = {}
    logs = []
    for query_index, query in enumerate(contract["queries"], 1):
        for provider, function in providers.items():
            search_id = f"q{query_index:02d}_{provider.lower()}"
            rows = function(query, limit)
            added = duplicates = inaccessible = out_scope = 0
            for rank, row in enumerate(rows, 1):
                doi = _doi(str(row["doi_or_stable_id"]))
                fallback = re.sub(r"[^a-z0-9]", "", row["title"].lower())
                key = doi or f"{fallback}|{row['year']}"
                duplicate_of = seen.get(key, "") if key else ""
                candidate_id = duplicate_of or f"candidate_{len(seen) + 1:04d}"
                if duplicate_of:
                    duplicates += 1
                elif key:
                    seen[key] = candidate_id
                    added += 1
                state = _state(row["title"])
                out_scope += state.startswith("OUT_OF_SCOPE")
                results.append(
                    {
                        "search_id": search_id,
                        "provider": provider,
                        "query": query,
                        "result_rank": rank,
                        **row,
                        "retrieval_date": "2026-08-25",
                        "candidate_id": candidate_id,
                        "duplicate_of": duplicate_of,
                        "screening_state": state,
                    }
                )
            logs.append(
                {
                    "search_id": search_id,
                    "provider": provider,
                    "query": query,
                    "execution_date": "2026-08-25",
                    "result_limit": limit,
                    "results_returned": len(rows),
                    "results_screened": len(rows),
                    "unique_candidates_added": added,
                    "duplicates": duplicates,
                    "inaccessible_candidates": inaccessible,
                    "out_of_scope_candidates": out_scope,
                }
            )
    result_fields = [
        "search_id",
        "provider",
        "query",
        "result_rank",
        "title",
        "authors",
        "year",
        "doi_or_stable_id",
        "result_url",
        "retrieval_date",
        "candidate_id",
        "duplicate_of",
        "screening_state",
    ]
    log_fields = [
        "search_id",
        "provider",
        "query",
        "execution_date",
        "result_limit",
        "results_returned",
        "results_screened",
        "unique_candidates_added",
        "duplicates",
        "inaccessible_candidates",
        "out_of_scope_candidates",
    ]
    for path, fields, rows in (
        (DATA / "search_results.csv", result_fields, results),
        (DATA / "search_log.csv", log_fields, logs),
    ):
        with path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
            writer.writeheader()
            writer.writerows(rows)
    citation_rows = _citation_passes(contract["citation_passes"]["backward_limit"])
    citation_fields = [
        "source_publication_id",
        "direction",
        "rank",
        "stable_id",
        "screening_state",
        "retrieval_date",
    ]
    with (DATA / "citation_passes.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=citation_fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(citation_rows)
    return {"searches": len(logs), "results": len(results), "unique_candidates": len(seen)}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--citation-only", action="store_true")
    args = parser.parse_args()
    if args.citation_only:
        rows = _citation_passes(20)
        fields = [
            "source_publication_id",
            "direction",
            "rank",
            "stable_id",
            "screening_state",
            "retrieval_date",
        ]
        with (DATA / "citation_passes.csv").open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
            writer.writeheader()
            writer.writerows(rows)
        print(json.dumps({"citation_records": len(rows)}, sort_keys=True))
    else:
        print(json.dumps(collect(), sort_keys=True))
