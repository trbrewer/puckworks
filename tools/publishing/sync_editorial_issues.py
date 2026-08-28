from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from dataclasses import asdict, dataclass
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Protocol
from zoneinfo import ZoneInfo

from tools.publishing.common import TERMINAL_SCHEDULE_STATUSES, ValidationError, load_yaml, parse_date
from tools.publishing.generate_editorial_digest import generate
from tools.publishing.validate_schedule import validate

MANAGED_START = "<!-- publishing-managed:start -->"
MANAGED_END = "<!-- publishing-managed:end -->"
REMINDER_LABELS = ("editorial", "publish-reminder")


class IssueClient(Protocol):
    def issues(self) -> list[dict[str, object]]: ...
    def ensure_labels(self) -> None: ...
    def request(self, method: str, path: str, payload: object | None = None) -> object: ...


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
            result = self.request("GET", f"/issues?state=all&labels=editorial&per_page=100&page={page}")
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
    due_dates = (parse_date(item["draft_due"], "draft_due"), parse_date(item["publish_date"], "publish_date"))
    earliest = min(due - timedelta(days=max(reminder_days)) for due in due_dates)
    return today >= earliest


def _milestone_state(value: object, today: date) -> str:
    milestone = parse_date(value, "milestone")
    return "upcoming" if milestone > today else "due" if milestone == today else "overdue"


def reminder_managed(item: dict[str, object], today: date) -> str:
    return "\n".join([
        MANAGED_START, f"# Editorial reminder: {item['title']}", "",
        f"- Schedule item ID: `{item['id']}`", f"- Title: {item['title']}",
        f"- Current status: `{item['status']}`",
        f"- Draft due date: `{item['draft_due']}` ({_milestone_state(item['draft_due'], today)})",
        f"- Publication date: `{item['publish_date']}` ({_milestone_state(item['publish_date'], today)})",
        f"- Evaluation date (America/Chicago): `{today}`", "",
        "Human review and manual publication are mandatory.", MANAGED_END,
    ])


def reminder_block(item: dict[str, object], today: date) -> str:
    return f"<!-- publishing-schedule-id: {item['id']} -->\n{reminder_managed(item, today)}"


def merge_managed(existing_body: str, managed: str, identity_marker: str) -> str:
    starts, ends = existing_body.count(MANAGED_START), existing_body.count(MANAGED_END)
    if starts != ends or starts > 1:
        raise ValidationError("issue body has malformed publishing managed-region markers")
    body = existing_body
    if starts == 1:
        start = body.index(MANAGED_START)
        end = body.index(MANAGED_END, start) + len(MANAGED_END)
        body = body[:start] + managed + body[end:]
    elif body.strip():
        body = body.rstrip() + "\n\n" + managed + "\n"
    else:
        body = managed
    body = body.replace(identity_marker, "")
    separator = "" if not body or body.startswith("\n") else "\n"
    return identity_marker + separator + body


def _labels(issue: dict[str, object]) -> set[str]:
    result: set[str] = set()
    labels = issue.get("labels", [])
    for label in labels if isinstance(labels, list) else []:
        if isinstance(label, str):
            result.add(label)
        elif isinstance(label, dict) and isinstance(label.get("name"), str):
            result.add(str(label["name"]))
    return result


def _patch_action(existing: dict[str, object], *, title: str, body: str, state: str, labels: tuple[str, ...]) -> IssueAction | None:
    payload: dict[str, object] = {}
    if existing.get("title") != title:
        payload["title"] = title
    if str(existing.get("body", "")) != body:
        payload["body"] = body
    if existing.get("state", "open") != state:
        payload["state"] = state
    existing_labels = _labels(existing)
    if not set(labels).issubset(existing_labels):
        payload["labels"] = sorted(existing_labels | set(labels))
    return IssueAction("PATCH", f"/issues/{existing['number']}", payload) if payload else None


def plan_actions(issues: list[dict[str, object]], schedule_path: Path, today: date, root: Path = Path(".")) -> list[IssueAction]:
    result = validate(schedule_path)
    if not result.ok:
        raise ValidationError("invalid schedule: " + "; ".join(result.errors))
    schedule = load_yaml(schedule_path)
    actions: list[IssueAction] = []
    for item in schedule["items"]:
        marker = f"<!-- publishing-schedule-id: {item['id']} -->"
        matches = [issue for issue in issues if marker in str(issue.get("body", ""))]
        if len(matches) > 1:
            raise ValidationError(f"multiple issues contain schedule marker for {item['id']}")
        existing = matches[0] if matches else None
        terminal = item["status"] in TERMINAL_SCHEDULE_STATUSES
        active = reminder_is_due(item, today, schedule["defaults"]["reminder_days_before"])
        if existing:
            body = merge_managed(str(existing.get("body", "")), reminder_managed(item, today), marker)
            action = _patch_action(existing, title=f"Editorial reminder: {item['title']}", body=body,
                                   state="closed" if terminal else "open", labels=REMINDER_LABELS)
            if action:
                actions.append(action)
        elif active and not terminal:
            actions.append(IssueAction("POST", "/issues", {
                "title": f"Editorial reminder: {item['title']}", "body": reminder_block(item, today),
                "labels": list(REMINDER_LABELS),
            }))
    if today.weekday() == 0:
        title = f"Editorial digest: {today}"
        marker = f"<!-- publishing-editorial-digest: {today} -->"
        matches = [issue for issue in issues if marker in str(issue.get("body", ""))]
        if len(matches) > 1:
            raise ValidationError(f"multiple issues contain editorial digest marker for {today}")
        digest = generate(schedule_path, today, root)
        digest_content = digest.removeprefix(marker).lstrip("\n")
        managed = "\n".join([MANAGED_START, digest_content, MANAGED_END])
        existing = matches[0] if matches else None
        if existing:
            body = merge_managed(str(existing.get("body", "")), managed, marker)
            action = _patch_action(existing, title=title, body=body, state="open", labels=("editorial",))
            if action:
                actions.append(action)
        else:
            actions.append(IssueAction("POST", "/issues", {
                "title": title, "body": f"{marker}\n{managed}", "labels": ["editorial"],
            }))
    return actions


def apply_actions(api: IssueClient, actions: list[IssueAction]) -> None:
    if actions:
        api.ensure_labels()
    for action in actions:
        api.request(action.method, action.path, action.payload)


def synchronize(api: IssueClient, schedule_path: Path, today: date, root: Path = Path("."), *, dry_run: bool = True) -> list[IssueAction]:
    actions = plan_actions(api.issues(), schedule_path, today, root)
    if not dry_run:
        apply_actions(api, actions)
    return actions


def _load_issue_fixture(path: Path) -> list[dict[str, object]]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValidationError(f"cannot read issue fixture {path}: {exc}") from exc
    if not isinstance(value, list) or any(not isinstance(item, dict) for item in value):
        raise ValidationError("--issues-json must contain an array of issue objects")
    return value


def main(argv: list[str] | None = None, *, client_factory: type[GitHubIssues] = GitHubIssues) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--schedule", type=Path, default=Path("content/schedule.yml"))
    parser.add_argument("--date", type=date.fromisoformat)
    parser.add_argument("--issues-json", type=Path)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--apply", action="store_true", help="apply the planned GitHub issue writes")
    mode.add_argument("--dry-run", action="store_true", help="plan only (the default)")
    args = parser.parse_args(argv)
    today = args.date or datetime.now(ZoneInfo("America/Chicago")).date()
    try:
        if args.apply:
            if args.issues_json:
                parser.error("--issues-json cannot be used with --apply")
            token, repository = os.environ.get("GITHUB_TOKEN"), os.environ.get("GITHUB_REPOSITORY")
            if not token or not repository:
                parser.error("--apply requires GITHUB_TOKEN and GITHUB_REPOSITORY")
            api = client_factory(repository, token)
            actions = plan_actions(api.issues(), args.schedule, today)
            apply_actions(api, actions)
        else:
            if args.issues_json:
                issues = _load_issue_fixture(args.issues_json)
            else:
                issues = []
                print("warning: planning from an empty issue list; remote deduplication was not evaluated", file=sys.stderr)
            actions = plan_actions(issues, args.schedule, today)
    except ValidationError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(json.dumps([asdict(action) for action in actions], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
