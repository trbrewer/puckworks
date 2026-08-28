from __future__ import annotations

import argparse
from datetime import date, timedelta
from pathlib import Path

from tools.publishing.common import ValidationError, load_yaml, parse_date, parse_frontmatter
from tools.publishing.scan_triggers import scan
from tools.publishing.validate_draft import validate as validate_draft
from tools.publishing.validate_evidence import validate_ledger
from tools.publishing.validate_schedule import validate as validate_schedule


def generate(schedule_path: Path, today: date, root: Path = Path(".")) -> str:
    schedule = load_yaml(schedule_path)
    schedule_result = validate_schedule(schedule_path)
    upcoming: list[str] = []
    overdue: list[str] = []
    missing_urls: list[str] = []
    canonical: list[str] = []
    for item in schedule.get("items", []):
        due = parse_date(item["draft_due"], f"{item['id']}.draft_due")
        publish = parse_date(item["publish_date"], f"{item['id']}.publish_date")
        if today <= publish <= today + timedelta(days=14):
            upcoming.append(f"- `{item['id']}` — {item['title']} ({publish})")
        if due < today and item["status"] == "planned":
            overdue.append(f"- `{item['id']}` — draft due {due}")
        platforms = item["platforms"]
        if item["status"] == "published":
            for name, config in platforms.items():
                if config.get("enabled") and not config.get("url"):
                    missing_urls.append(f"- `{item['id']}` — missing {name} URL")
        medium = platforms.get("medium", {})
        if medium.get("url") and not medium.get("canonical_url"):
            canonical.append(f"- `{item['id']}` — Medium canonical unverified")
    evidence_blocked: list[str] = []
    human_review: list[str] = []
    draft_diagnostics: list[str] = []
    used_triggers: set[str] = set()
    for path in sorted((root / "content/drafts").glob("*.md")):
        try:
            meta, _ = parse_frontmatter(path)
        except (ValidationError, OSError):
            continue
        if meta.get("status") == "evidence_review":
            evidence_blocked.append(f"- `{path}`")
        if meta.get("status") == "human_review":
            human_review.append(f"- `{path}`")
        source_event = meta.get("source_event", {})
        if isinstance(source_event, dict) and source_event.get("trigger_id"):
            used_triggers.add(str(source_event["trigger_id"]))
        result = validate_draft(path, content_root=root.resolve())
        if not result.ok:
            draft_diagnostics.append(f"- `{path}`: {'; '.join(result.errors)}")
    triggers = scan(root / "content/triggers")
    eligible = [
        path for path in triggers["eligible"]
        if Path(path).stem not in used_triggers
    ]
    ledger_diagnostics: list[str] = []
    for path in sorted((root / "content/evidence").glob("*.yml")):
        result = validate_ledger(path)
        if not result.ok:
            ledger_diagnostics.append(f"- `{path}`: {'; '.join(result.errors)}")

    def section(title: str, rows: list[str]) -> list[str]:
        return [f"## {title}", "", *(rows or ["- None"]), ""]

    lines = [f"<!-- publishing-digest-date: {today} -->", f"# Editorial digest: {today}", ""]
    lines += section("Posts due in the next 14 days", upcoming)
    lines += section("Overdue drafts", overdue)
    lines += section("Drafts blocked by evidence", evidence_blocked)
    lines += section("Drafts awaiting human review", human_review)
    lines += section("Missing platform URLs", missing_urls)
    lines += section("Medium canonical URL unverified", canonical)
    lines += section("Eligible new trigger manifests", [f"- `{p}`" for p in eligible])
    diagnostics = [f"- `{d['path']}`: {'; '.join(d['errors'])}" for d in triggers["diagnostics"]]
    lines += section("Trigger diagnostics", diagnostics)
    lines += section("Draft diagnostics", draft_diagnostics)
    lines += section("Evidence-ledger diagnostics", ledger_diagnostics)
    lines += section("Schedule diagnostics", [f"- {error}" for error in schedule_result.errors])
    lines += ["This digest is an editorial reminder only. It cannot approve or publish content.", ""]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--schedule", type=Path, default=Path("content/schedule.yml"))
    parser.add_argument("--date", type=date.fromisoformat, default=date.today())
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = generate(args.schedule, args.date)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(result, encoding="utf-8")
    else:
        print(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
