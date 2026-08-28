from __future__ import annotations

import argparse
import re
from datetime import timedelta
from pathlib import Path
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from tools.publishing.common import (
    ARCHETYPES, CheckResult, SCHEDULE_STATUSES, ValidationError, load_yaml, parse_date,
    print_result,
)


def validate(path: Path) -> CheckResult:
    errors: list[str] = []
    try:
        doc = load_yaml(path)
    except ValidationError as exc:
        return CheckResult(path, (str(exc),))
    if doc.get("schema_version") != 1:
        errors.append("schema_version must be 1")
    if doc.get("timezone") != "America/Chicago":
        errors.append("timezone must be America/Chicago")
    try:
        ZoneInfo(str(doc.get("timezone")))
    except ZoneInfoNotFoundError:
        errors.append("timezone must be a valid IANA timezone")
    defaults = doc.get("defaults", {})
    if not isinstance(defaults, dict) or defaults.get("reminder_days_before") != [7, 2]:
        errors.append("defaults.reminder_days_before must be [7, 2]")
    items = doc.get("items")
    if not isinstance(items, list):
        return CheckResult(path, tuple(errors + ["items must be a list"]))
    ids: set[str] = set()
    slugs: set[str] = set()
    for index, item in enumerate(items):
        prefix = f"items[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{prefix} must be a mapping")
            continue
        item_id, slug = item.get("id"), item.get("slug")
        if not isinstance(item_id, str) or not re.fullmatch(r"[a-z0-9-]+", item_id):
            errors.append(f"{prefix}.id is invalid")
        elif item_id in ids:
            errors.append(f"{prefix}.id is duplicated")
        else:
            ids.add(item_id)
        if not isinstance(slug, str) or not re.fullmatch(r"[a-z0-9-]+", slug):
            errors.append(f"{prefix}.slug is invalid")
        elif slug in slugs:
            errors.append(f"{prefix}.slug is duplicated")
        else:
            slugs.add(slug)
        if item.get("status") not in SCHEDULE_STATUSES:
            errors.append(f"{prefix}.status is invalid")
        if item.get("archetype") not in ARCHETYPES:
            errors.append(f"{prefix}.archetype is invalid")
        if item.get("delivery") not in {"email", "web_only"}:
            errors.append(f"{prefix}.delivery is invalid")
        for field in ("title", "owner", "publish_time_local", "platforms", "source_triggers", "notes"):
            if field not in item:
                errors.append(f"{prefix}.{field} is required")
        if not re.fullmatch(r"(?:[01]\d|2[0-3]):[0-5]\d", str(item.get("publish_time_local", ""))):
            errors.append(f"{prefix}.publish_time_local must be HH:MM")
        triggers = item.get("source_triggers")
        if not isinstance(triggers, list) or any(
            not re.fullmatch(r"PW-PUB-\d{4}-\d{3}", str(value)) for value in triggers
        ):
            errors.append(f"{prefix}.source_triggers must contain trigger IDs")
        elif any(not (path.parent / "triggers" / f"{value}.yml").is_file() for value in triggers):
            errors.append(f"{prefix}.source_triggers contains a missing manifest")
        try:
            draft_due = parse_date(item.get("draft_due"), f"{prefix}.draft_due")
            publish = parse_date(item.get("publish_date"), f"{prefix}.publish_date")
            if draft_due > publish:
                errors.append(f"{prefix}.draft_due must not follow publish_date")
        except ValidationError as exc:
            errors.append(str(exc))
            continue
        platforms = item.get("platforms")
        if not isinstance(platforms, dict) or not isinstance(platforms.get("substack"), dict):
            errors.append(f"{prefix}.platforms.substack is required")
            continue
        substack, medium = platforms["substack"], platforms.get("medium", {})
        if substack.get("enabled") is not True:
            errors.append(f"{prefix}.substack must be enabled as source of record")
        if substack.get("send_email") != (item.get("delivery") == "email"):
            errors.append(f"{prefix}: delivery and substack.send_email disagree")
        if isinstance(medium, dict) and medium.get("enabled"):
            try:
                not_before = parse_date(medium.get("publish_not_before"), f"{prefix}.medium.publish_not_before")
                if not_before < publish + timedelta(days=int(defaults.get("medium_lag_days", 7))):
                    errors.append(f"{prefix}.medium.publish_not_before violates the lag")
            except ValidationError as exc:
                errors.append(str(exc))
        status = item.get("status")
        if status == "published":
            if not substack.get("url"):
                errors.append(f"{prefix}: published requires the Substack URL")
            if not item.get("reminder_issue_number"):
                errors.append(f"{prefix}: published requires reminder_issue_number")
            if isinstance(medium, dict) and medium.get("url"):
                if medium.get("canonical_url") != substack.get("url"):
                    errors.append(f"{prefix}: Medium canonical must equal the exact Substack URL")
        elif substack.get("url"):
            errors.append(f"{prefix}: non-published item must not record a Substack public URL")
        if isinstance(medium, dict) and medium.get("url") and not medium.get("canonical_url"):
            errors.append(f"{prefix}: Medium URL requires canonical_url")
    return CheckResult(path, tuple(errors))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("path", nargs="?", type=Path, default=Path("content/schedule.yml"))
    return print_result(validate(parser.parse_args().path))


if __name__ == "__main__":
    raise SystemExit(main())
