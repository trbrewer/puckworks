from __future__ import annotations

import argparse
import json
import os
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

from tools.publishing.common import TERMINAL_SCHEDULE_STATUSES, load_yaml, parse_date
from tools.publishing.generate_editorial_digest import generate
from tools.publishing.validate_schedule import validate


class GitHubIssues:
    def __init__(self, repository: str, token: str) -> None:
        self.base = f"https://api.github.com/repos/{repository}"
        self.headers = {
            "Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28", "User-Agent": "puckworks-editorial-reminders/1",
        }

    def request(self, method: str, path: str, payload: object | None = None) -> object:
        data = json.dumps(payload).encode() if payload is not None else None
        request = urllib.request.Request(self.base + path, data=data, method=method, headers=self.headers)
        with urllib.request.urlopen(request, timeout=30) as response:
            return json.loads(response.read()) if response.length != 0 else {}

    def issues(self) -> list[dict[str, object]]:
        issues: list[dict[str, object]] = []
        for page in range(1, 101):
            result = self.request(
                "GET", f"/issues?state=all&labels=editorial&per_page=100&page={page}"
            )
            if not isinstance(result, list):
                raise ValueError("GitHub issues response must be a list")
            issues.extend(item for item in result if "pull_request" not in item)
            if len(result) < 100:
                return issues
        raise ValueError("GitHub issues pagination exceeded the safety limit")

    def ensure_labels(self) -> None:
        for name, color in (("editorial", "1d76db"), ("publish-reminder", "fbca04")):
            try:
                self.request("POST", "/labels", {"name": name, "color": color})
            except urllib.error.HTTPError as exc:
                if exc.code != 422:
                    raise


@dataclass(frozen=True)
class IssueAction:
    method: str
    path: str
    payload: dict[str, object]


def reminder_is_due(item: dict[str, object], today: date, reminder_days: list[int]) -> bool:
    """Return true throughout the catch-up window after the earliest reminder threshold."""
    due_dates = (
        parse_date(item["draft_due"], "draft_due"),
        parse_date(item["publish_date"], "publish_date"),
    )
    earliest = min(due - timedelta(days=max(reminder_days)) for due in due_dates)
    latest = max(due_dates)
    return earliest <= today <= latest


def reminder_block(item: dict[str, object], today: date) -> str:
    marker = f"<!-- publishing-schedule-id: {item['id']} -->"
    return "\n".join([
        marker, f"<!-- publishing-managed:start {item['id']} -->",
        f"# Editorial reminder: {item['title']}", "",
        f"- Status: `{item['status']}`", f"- Draft due: `{item['draft_due']}`",
        f"- Publication date: `{item['publish_date']}`", f"- Evaluated locally: `{today}`",
        "", "Human review and manual publication are mandatory. This issue cannot approve or publish.",
        f"<!-- publishing-managed:end {item['id']} -->",
    ])


def merge_managed(existing_body: str, block: str, key: str) -> str:
    """Replace only the automation-owned block and retain all human-authored issue text."""
    start = f"<!-- publishing-managed:start {key} -->"
    end = f"<!-- publishing-managed:end {key} -->"
    if start in existing_body and end in existing_body:
        before, remainder = existing_body.split(start, 1)
        _, after = remainder.split(end, 1)
        managed = block[block.index(start): block.index(end) + len(end)]
        return before + managed + after
    if not existing_body.strip():
        return block
    marker = block.splitlines()[0]
    addition = "\n".join(block.splitlines()[1:]) if marker in existing_body else block
    return existing_body.rstrip() + "\n\n" + addition + "\n"


def plan_actions(
    issues: list[dict[str, object]], schedule_path: Path, today: date, root: Path = Path(".")
) -> list[IssueAction]:
    result = validate(schedule_path)
    if not result.ok:
        raise ValueError("invalid schedule: " + "; ".join(result.errors))
    schedule = load_yaml(schedule_path)
    actions: list[IssueAction] = []
    for item in schedule["items"]:
        marker = f"<!-- publishing-schedule-id: {item['id']} -->"
        existing = next((i for i in issues if marker in str(i.get("body", ""))), None)
        reminder_days = schedule["defaults"]["reminder_days_before"]
        active = reminder_is_due(item, today, reminder_days)
        terminal = item["status"] in TERMINAL_SCHEDULE_STATUSES
        block = reminder_block(item, today)
        body = merge_managed(str(existing.get("body", "")), block, str(item["id"])) if existing else block
        if existing:
            state = "closed" if terminal else "open"
            actions.append(IssueAction("PATCH", f"/issues/{existing['number']}", {"body": body, "state": state}))
        elif active and not terminal:
            actions.append(IssueAction("POST", "/issues", {"title": f"Editorial reminder: {item['title']}", "body": body, "labels": ["editorial", "publish-reminder"]}))
    if today.weekday() == 0:
        title = f"Editorial digest: {today}"
        marker = f"<!-- publishing-digest-date: {today} -->"
        body = generate(schedule_path, today, root)
        existing = next((i for i in issues if marker in str(i.get("body", ""))), None)
        if existing:
            digest_block = "\n".join([
                f"<!-- publishing-managed:start digest-{today} -->", body,
                f"<!-- publishing-managed:end digest-{today} -->",
            ])
            merged = merge_managed(
                str(existing.get("body", "")), digest_block, f"digest-{today}"
            )
            actions.append(IssueAction("PATCH", f"/issues/{existing['number']}", {"title": title, "body": merged, "state": "open"}))
        else:
            actions.append(IssueAction("POST", "/issues", {"title": title, "body": "\n".join([f"<!-- publishing-managed:start digest-{today} -->", body, f"<!-- publishing-managed:end digest-{today} -->"]), "labels": ["editorial"]}))
    return actions


def synchronize(
    api: GitHubIssues, schedule_path: Path, today: date, root: Path = Path("."),
    *, dry_run: bool = True,
) -> list[IssueAction]:
    issues = api.issues()
    actions = plan_actions(issues, schedule_path, today, root)
    if dry_run:
        return actions
    api.ensure_labels()
    for action in actions:
        api.request(action.method, action.path, action.payload)
    return actions


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--schedule", type=Path, default=Path("content/schedule.yml"))
    parser.add_argument("--date", type=date.fromisoformat)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--apply", action="store_true", help="apply the planned GitHub issue writes")
    mode.add_argument("--dry-run", action="store_true", help="plan only (the default)")
    args = parser.parse_args()
    token, repository = os.environ.get("GITHUB_TOKEN"), os.environ.get("GITHUB_REPOSITORY")
    if not token or not repository:
        parser.error("GITHUB_TOKEN and GITHUB_REPOSITORY are required")
    timezone = ZoneInfo("America/Chicago")
    today = args.date or datetime.now(timezone).date()
    actions = synchronize(GitHubIssues(repository, token), args.schedule, today, dry_run=not args.apply)
    print(json.dumps([action.__dict__ for action in actions], indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
