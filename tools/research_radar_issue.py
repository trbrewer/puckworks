#!/usr/bin/env python3
"""Offline-testable issue logic for the research radar (issue #42).

Separated from the workflow YAML so the substantial logic — cross-month deduplication, stable
candidate markers, safe rendering of untrusted metadata, label selection, body-size caps, and the
create/comment/skip/needs-human decision — is unit-tested. The workflow does only thin GitHub I/O:
it fetches candidate markers from ALL radar issues and the current monthly issue, then executes the
plan this module computes.

Guarantees:
  * monthly radar issues use labels [research-radar, triage] — never `standing` (reserved for #42);
  * a candidate already posted in ANY month (open or closed) is not re-posted;
  * a closed current-month issue is never silently duplicated — it needs a human;
  * untrusted titles/authors/venues/URLs are sanitized; the body is capped.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

# Import sibling module (works when tools/ is on sys.path or run as a script).
sys.path.insert(0, str(Path(__file__).resolve().parent))
import research_radar as R  # noqa: E402

MONTHLY_LABELS = ["research-radar", "triage"]     # NOT `standing`
MAX_ISSUE_BODY_BYTES = 60_000                     # < GitHub's 65536 comment limit
MARKER_RE = re.compile(r"<!--\s*radar-candidate:([0-9a-f]{64})\s*-->")


def candidate_marker(identity: str) -> str:
    h = hashlib.sha256(identity.encode("utf-8")).hexdigest()
    return f"<!-- radar-candidate:{h} -->"


def marker_hash(identity: str) -> str:
    return hashlib.sha256(identity.encode("utf-8")).hexdigest()


def parse_markers(text: str) -> set[str]:
    """Every candidate hash referenced in a blob of issue bodies/comments."""
    return set(MARKER_RE.findall(text or ""))


def new_candidates(candidates: list[dict], seen_hashes: set[str]) -> list[dict]:
    """Candidates whose stable-identity marker hash is not already recorded anywhere."""
    out = []
    for c in candidates:
        ident = c.get("identity") or ""
        if marker_hash(ident) not in seen_hashes:
            out.append(c)
    return out


def choose_labels() -> list[str]:
    return list(MONTHLY_LABELS)


def select_monthly_issue(issues: list[dict], title: str) -> dict | None:
    """Find the current monthly issue by exact title among radar issues (ANY state). Lowest number
    wins deterministically. Pull requests are ignored."""
    matches = [i for i in issues if i.get("title") == title and not i.get("pull_request")]
    return sorted(matches, key=lambda i: i.get("number", 1 << 30))[0] if matches else None


def _fmt_candidate(c: dict) -> str:
    title = R.sanitize_text(c.get("title"))
    source = R.sanitize_text(str(c.get("source", "")), max_len=40)
    date = R.sanitize_text(str(c.get("date") or "—"), max_len=20)
    doi = c.get("doi")
    arxiv = c.get("arxiv_id")
    url = R.safe_url(c.get("url"))
    if doi:
        ident = f"doi:{R.normalize_doi(doi)}"
    elif arxiv:
        ident = f"arXiv:{R.normalize_arxiv_id(arxiv)}"
    else:
        ident = "no-id"
    link = f" ([{ident}]({url}))" if url else f" ({ident})"
    reasons = ", ".join(R.sanitize_text(r, max_len=40) for r in (c.get("match_reasons") or [])) or "—"
    qid = R.sanitize_text(str(c.get("query_id", "")), max_len=60)
    return (f"{candidate_marker(c.get('identity',''))}\n"
            f"- **{title}** — {source} · {date}{link}  \n"
            f"  found by `{qid}`; matched: {reasons} · triage: `new`")


def render_issue_body(scan: dict, fresh: list[dict], *, max_bytes: int = MAX_ISSUE_BODY_BYTES) -> str:
    header = [
        f"#### Scan {R.sanitize_text(str(scan.get('scan_date')), max_len=20)} — "
        f"{len(fresh)} new candidate(s)  ·  total scan status: "
        f"{R.sanitize_text(str(scan.get('total_status')), max_len=20)}",
        "",
        "**Source health:** " + "; ".join(
            f"{R.sanitize_text(r.get('source',''), max_len=20)}={r.get('status')}"
            f" ({r.get('queries_succeeded')}/{r.get('queries_attempted')})"
            for r in scan.get("source_runs", [])),
        "",
        "> **Discovery is not validation.** Every item is a triage candidate for a human — it",
        "> changes no card, claim, manuscript, roadmap entry, or submission plan, and creates no",
        "> external contact.",
        "",
    ]
    footer = [
        "",
        "_" + R.ARXIV_ACK + " Crossref metadata via the polite pool._",
    ]
    body_lines = list(header)
    omitted = 0
    for c in fresh:
        entry = _fmt_candidate(c)
        trial = "\n".join(body_lines + [entry] + footer)
        if len(trial.encode("utf-8")) > max_bytes:
            omitted += 1
            continue
        body_lines.append(entry)
    if omitted:
        body_lines.append(f"\n_+{omitted} further candidate(s) omitted by the issue-body cap; see "
                          "the workflow artifact for the full set._")
    return "\n".join(body_lines + footer)


def build_issue_plan(scan: dict, seen_hashes: set[str], issues: list[dict], *,
                     publish: bool) -> dict:
    """Decide what to do this run. Returns a plan dict the workflow executes."""
    title = scan.get("issue_title") or R.radar_issue_title(scan.get("scan_date", ""))
    if scan.get("total_status") == "failed":
        return {"action": "skip", "reason": "total scan status is failed; not writing an issue",
                "title": title, "labels": choose_labels()}

    fresh = new_candidates(scan.get("candidates", []), seen_hashes)
    existing = select_monthly_issue(issues, title)

    if existing and str(existing.get("state", "")).lower() == "closed":
        return {"action": "needs_human",
                "reason": f"current-month issue #{existing.get('number')} is closed; "
                          "not creating a duplicate — a human should reopen or start next month",
                "title": title, "labels": choose_labels(),
                "existing_number": existing.get("number"), "new_count": len(fresh)}

    if not fresh:
        return {"action": "skip", "reason": "no new candidates to append", "title": title,
                "labels": choose_labels(),
                "existing_number": existing.get("number") if existing else None}

    body = render_issue_body(scan, fresh)
    base = {"title": title, "labels": choose_labels(), "body": body, "new_count": len(fresh),
            "body_bytes": len(body.encode("utf-8")),
            "existing_number": existing.get("number") if existing else None}
    if not publish:
        return {**base, "action": "dry-run",
                "reason": "publish disabled (manual dispatch default is scan+artifact only)"}
    return {**base, "action": ("comment" if existing else "create"),
            "reason": "append new candidates" if existing else "open the monthly radar issue"}


# ─────────────────────────────── CLI (for the workflow) ──────────────────────────
def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Compute the monthly radar issue plan.")
    ap.add_argument("--candidates", required=True, help="candidates.json from a scan")
    ap.add_argument("--seen", default=None, help="file of prior issue bodies/comments (markers)")
    ap.add_argument("--issues", default=None, help="JSON list of radar issues (title,number,state)")
    ap.add_argument("--publish", action="store_true")
    ap.add_argument("--out", required=True, help="write the plan JSON here")
    args = ap.parse_args(argv)

    scan = json.loads(Path(args.candidates).read_text(encoding="utf-8"))
    seen = parse_markers(Path(args.seen).read_text(encoding="utf-8")) if args.seen and Path(args.seen).exists() else set()
    issues = json.loads(Path(args.issues).read_text(encoding="utf-8")) if args.issues and Path(args.issues).exists() else []
    plan = build_issue_plan(scan, seen, issues, publish=args.publish)
    # Never emit the body to stdout logs; write it to the plan file only.
    Path(args.out).write_text(json.dumps(plan, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"plan: action={plan['action']} reason={plan['reason']} "
          f"new={plan.get('new_count', 0)} body_bytes={plan.get('body_bytes', 0)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
