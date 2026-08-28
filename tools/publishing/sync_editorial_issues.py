from __future__ import annotations

import argparse
import json
import os
import urllib.error
import urllib.request
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
        result = self.request("GET", "/issues?state=all&labels=editorial&per_page=100")
        return [item for item in result if "pull_request" not in item]  # type: ignore[union-attr]

    def ensure_labels(self) -> None:
        for name, color in (("editorial", "1d76db"), ("publish-reminder", "fbca04")):
            try:
                self.request("POST", "/labels", {"name": name, "color": color})
            except urllib.error.HTTPError as exc:
                if exc.code != 422:
                    raise


def reminder_body(item: dict[str, object], today: date) -> str:
    marker = f"<!-- publishing-schedule-id: {item['id']} -->"
    return "\n".join([
        marker, f"# Editorial reminder: {item['title']}", "",
        f"- Status: `{item['status']}`", f"- Draft due: `{item['draft_due']}`",
        f"- Publication date: `{item['publish_date']}`", f"- Evaluated locally: `{today}`",
        "", "Human review and manual publication are mandatory. This issue cannot approve or publish.",
    ])


def synchronize(api: GitHubIssues, schedule_path: Path, today: date, root: Path = Path(".")) -> None:
    result = validate(schedule_path)
    if not result.ok:
        raise ValueError("invalid schedule: " + "; ".join(result.errors))
    schedule = load_yaml(schedule_path)
    api.ensure_labels()
    issues = api.issues()
    for item in schedule["items"]:
        marker = f"<!-- publishing-schedule-id: {item['id']} -->"
        existing = next((i for i in issues if marker in str(i.get("body", ""))), None)
        due_dates = (parse_date(item["draft_due"], "draft_due"), parse_date(item["publish_date"], "publish_date"))
        reminder_days = schedule["defaults"]["reminder_days_before"]
        active = any(today == due - timedelta(days=days) for due in due_dates for days in reminder_days)
        terminal = item["status"] in TERMINAL_SCHEDULE_STATUSES
        body = reminder_body(item, today)
        if existing:
            state = "closed" if terminal else "open"
            api.request("PATCH", f"/issues/{existing['number']}", {"body": body, "state": state})
        elif active and not terminal:
            api.request("POST", "/issues", {"title": f"Editorial reminder: {item['title']}", "body": body, "labels": ["editorial", "publish-reminder"]})
    if today.weekday() == 0:
        title = f"Editorial digest: {today}"
        marker = f"<!-- publishing-digest-date: {today} -->"
        body = generate(schedule_path, today, root)
        existing = next((i for i in issues if marker in str(i.get("body", ""))), None)
        if existing:
            api.request("PATCH", f"/issues/{existing['number']}", {"title": title, "body": body, "state": "open"})
        else:
            api.request("POST", "/issues", {"title": title, "body": body, "labels": ["editorial"]})


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--schedule", type=Path, default=Path("content/schedule.yml"))
    parser.add_argument("--date", type=date.fromisoformat)
    args = parser.parse_args()
    token, repository = os.environ.get("GITHUB_TOKEN"), os.environ.get("GITHUB_REPOSITORY")
    if not token or not repository:
        parser.error("GITHUB_TOKEN and GITHUB_REPOSITORY are required")
    timezone = ZoneInfo("America/Chicago")
    today = args.date or datetime.now(timezone).date()
    synchronize(GitHubIssues(repository, token), args.schedule, today)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
