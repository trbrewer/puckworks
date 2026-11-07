"""Release aggregate metadata availability only; no shot values or hydraulics."""

from __future__ import annotations

import argparse
from collections import Counter
import csv
from datetime import datetime
import json
from pathlib import Path

from puckworks.analysis.pressure_peak_x1 import authenticate
from puckworks.analysis.vis_metadata_probe_001 import token

REQUIRED_PATHS = {
    "machine", "device", "metadata.machine", "metadata.device", "brewdata.machine",
    "parser", "integration_source", "brewdata.parser",
    "profile_title", "profile_url", "brewdata.profile", "brewdata.frames",
    "brewdata.stage", "brewdata.control_mode", "brewdata.scale", "scale_connected",
    "metadata.scale", "metadata.scale_connected", "flow_source", "weight_source",
    "data.espresso_state_change", "data.espresso_flow_weight", "data.espresso_weight",
    "PROFILE.steps", "PROFILE.frames", "PROFILE.stages", "PROFILE.steps[].pump",
    "PROFILE.steps[].limiter", "PROFILE.control_mode", "PROFILE.maximum_flow",
}
NOT_CAPTURED_PATHS = {
    "PROFILE.steps[].limiter.value", "PROFILE.steps[].limiter.range",
    "PROFILE.steps[].exit.condition", "PROFILE.steps[].exit.value",
    "PROFILE.advanced_shot", "PROFILE.settings_profile_type",
    "GOAL_SENTINEL_DISTINCTION",  # -1/zero/positive was lost by type-only capture.
}
NORMALIZED_PATHS = {
    "machine": ("machine",), "brewdata.parser": ("context", "integration_source"),
    "parser": ("context", "integration_source"),
    "integration_source": ("context", "integration_source"),
    "bean_weight": ("context", "dose__kg"),
    **{k: ("context", k) for k in ("grinder_model", "grinder_setting", "roast_level")},
    **{"data." + raw: ("hydraulic", normalized) for raw, normalized in (
        ("espresso_pressure", "pressure__Pa"), ("espresso_pressure_goal", "pressure_goal__Pa"),
        ("espresso_flow_goal", "flow_goal_reported__native"),
        ("espresso_flow_weight", "mass_flow_from_scale__kg_per_s"),
        ("espresso_weight", "weight__kg"), ("espresso_state_change", "state_change"),
    )},
}


def difference_safe(rows):
    return not rows or (len(rows) >= 20 and
                        len({r.get("user_token") for r in rows} - {None, ""}) >= 10)


def difference(first, second):
    excluded = {id(r) for r in second}
    return [r for r in first if id(r) not in excluded]


def suppress(row):
    for key in ("present", "null", "absent_at_current_source",
                "profile_not_returned_or_not_requested", "old_bronze_present",
                "old_normalized_nonnull", "privacy_dropped_now", "historically_confirmed_drop",
                "new_at_source_or_historical_loss_unknown", "example_value_types"):
        if row[key] != "NA":
            row[key] = "SUPPRESSED"


def has(types):
    return bool(set(types) - {"null"})


def releasable(rows, subset):
    """Existing minima, with conservative complementary-user disclosure check."""
    users = {r.get("user_token") for r in rows} - {None, ""}
    chosen = {r.get("user_token") for r in subset} - {None, ""}
    if len(rows) < 20 or len(users) < 10:
        return False
    if len(subset) in (0, len(rows)):
        return True
    return (len(subset) >= 20 and len(chosen) >= 10
            and len(rows) - len(subset) >= 20 and len(users - chosen) >= 10)


def fields(row):
    return row.get("fields", {}) | {
        "PROFILE." + path: types for path, types in row.get("profile_fields", {}).items()
    }


def availability(rows, arm, format_name, machine):
    available = [r for r in rows if r["status"] == "AVAILABLE"]
    paths = REQUIRED_PATHS | {p for r in available for p in fields(r)
                             if p not in {"id", "user_id"}}
    output = []
    memberships = {}
    for path in sorted(paths):
        assessed = [r for r in available if not path.startswith("PROFILE.")
                    or "profile_fields" in r]
        unassessed = difference(available, assessed)
        present = [r for r in assessed if has(fields(r).get(path, []))]
        null = [r for r in assessed if fields(r).get(path) == ["null"]]
        missing = [r for r in assessed if path not in fields(r)]
        types = sorted({t for r in present for t in fields(r)[path]})
        old = [r for r in available if has(r.get("old_fields", {}).get(path, []))]
        normalized = [r for r in available if r.get("old_normalized_nonnull", {}).get(path)]
        dropped_now = [r for r in present if not path.startswith("PROFILE.")
                       and path not in r.get("after_privacy_fields", {})]
        confirmed = [r for r in present if path == "profile_title"
                     and r.get("old_profile_present")]
        new_unknown = [r for r in present if not path.startswith("PROFILE.")
                       and not has(r.get("old_fields", {}).get(path, []))
                       and r not in confirmed]
        cells = [present, null, missing, unassessed, old, normalized,
                 dropped_now, confirmed, new_unknown]
        safe = all(releasable(available, cell) for cell in cells)
        safe = safe and all(difference_safe(difference(first, second))
                            for first in cells for second in cells)
        memberships[path] = present
        count = lambda x: len(x) if safe else "SUPPRESSED"
        if "espresso_flow_weight" in path or "espresso_weight" in path:
            interpretation = "generic channel; measured/estimated origin AMBIGUOUS"
        elif path == "brewdata.parser":
            interpretation = "software-written parser identity; not hardware"
        elif path.startswith("PROFILE."):
            interpretation = "configuration field only; executed stage/control/limiter UNKNOWN"
        elif any(k in path for k in ("machine", "device", "scale", "control", "stage", "state")):
            interpretation = "presence alone does not authenticate hardware/stage/scale"
        else:
            interpretation = "field/type presence only; values not retained"
        output.append(dict(
            arm=arm, upload_format=format_name, machine=machine, selected_records=len(rows),
            available_responses=len(available), native_field=path,
            example_value_types="|".join(types) if safe else "SUPPRESSED",
            present=count(present), null=count(null), absent_at_current_source=count(missing),
            profile_not_returned_or_not_requested=count(unassessed),
            old_bronze_present=count(old) if arm == "A" and not path.startswith("PROFILE.") else "NA",
            normalized_path=".".join(NORMALIZED_PATHS[path]) if path in NORMALIZED_PATHS else "NOT_MAPPED",
            old_normalized_nonnull=count(normalized) if arm == "A" and path in NORMALIZED_PATHS else "NA",
            privacy_dropped_now=count(dropped_now),
            historically_confirmed_drop=count(confirmed) if arm == "A" else "NA",
            new_at_source_or_historical_loss_unknown=count(new_unknown) if arm == "A" else "NA",
            interpretation=interpretation,
            credit="Visualizer; thanks to contributing users collectively.",
        ))
    unsafe_roots = set()
    for parent, parent_rows in memberships.items():
        for child, child_rows in memberships.items():
            if child.startswith((parent + ".", parent + "[]")):
                if not difference_safe(difference(parent_rows, child_rows)):
                    unsafe_roots.add(parent.split(".")[0])
    for row in output:
        if row["native_field"].split(".")[0] in unsafe_roots:
            suppress(row)
    for path in sorted(NOT_CAPTURED_PATHS):
        row = dict(output[0])
        row.update(native_field=path, normalized_path="NOT_MAPPED",
                   interpretation="NOT_CAPTURED: collector omission; no absence-at-source inference")
        for key in ("present", "null", "absent_at_current_source",
                    "profile_not_returned_or_not_requested", "old_bronze_present",
                    "old_normalized_nonnull", "privacy_dropped_now", "historically_confirmed_drop",
                    "new_at_source_or_historical_loss_unknown", "example_value_types"):
            row[key] = "NOT_CAPTURED"
        output.append(row)
    return output


def report(private, root, inventory, output):
    run = json.loads((private / "RUN.json").read_text())
    if run["status"] not in ("COMPLETED", "STOPPED"):
        raise ValueError("Probe has not ended")
    rows_path = private / "FIELDS.jsonl"
    rows = [json.loads(s) for s in rows_path.read_text().splitlines()] if rows_path.exists() else []
    snapshot, receipt = authenticate(root, inventory)
    if receipt != run["snapshot"]:
        raise ValueError("Snapshot changed")
    salt = (root.parent / ".harvest_salt").read_text().strip()
    by_token = {r["shot_token"]: r for r in rows if r["arm"] == "A"}
    for row in snapshot.latest():
        selected = by_token.get(token(salt, row["id"]))
        if selected is not None:
            selected["old_profile_present"] = bool(row.get("context", {}).get("profile_present"))
            selected["old_normalized_nonnull"] = {}
            for source_path, normalized_path in NORMALIZED_PATHS.items():
                value = row
                for key in normalized_path:
                    value = value.get(key) if isinstance(value, dict) else None
                selected["old_normalized_nonnull"][source_path] = value is not None
    public = []
    for arm in ("A", "B"):
        arm_rows = [r for r in rows if r["arm"] == arm]
        groups = sorted({(r.get("format", "UNAVAILABLE"), r.get("machine", "UNKNOWN"))
                         for r in arm_rows})
        split = []
        for format_name, machine in groups:
            group = [r for r in arm_rows if (r.get("format", "UNAVAILABLE"),
                                           r.get("machine", "UNKNOWN")) == (format_name, machine)]
            if releasable(arm_rows, group):
                split.append((format_name, machine, group))
        # Never release a total alongside a partial partition: subtraction could
        # reconstruct the suppressed format or field cell.
        if len(split) == len(groups) and split:
            for format_name, machine, group in split:
                public.extend(availability(group, arm, format_name, machine))
        else:
            public.extend(availability(arm_rows, arm, "ALL", "ALL"))
    # API profile-request totals are necessarily disclosed. Suppress related
    # fields across both arms if a rare cell could be recovered by subtraction.
    profile_paths = lambda p: p == "profile_url" or p.startswith("PROFILE.")
    if any(profile_paths(r["native_field"]) and r["present"] == "SUPPRESSED" for r in public):
        for row in public:
            if profile_paths(row["native_field"]):
                if row["present"] != "NOT_CAPTURED":
                    suppress(row)
    output.mkdir(parents=True, exist_ok=True)
    if public:
        with (output / "FIELD_AVAILABILITY.csv").open("w", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=list(public[0]), lineterminator="\n")
            writer.writeheader()
            writer.writerows(public)
    ledger = [json.loads(s) for s in (private / "REQUESTS.jsonl").read_text().splitlines()]
    starts = [datetime.fromisoformat(r["started_utc"]).timestamp() for r in ledger]
    maximum = lambda seconds: max(sum(0 <= t - s < seconds for s in starts) for t in starts)
    audit = dict(requests=len(ledger), kinds=dict(Counter(r["kind"] for r in ledger)),
                 statuses=dict(Counter(str(r["status"]) for r in ledger)),
                 first_request=ledger[0]["started_utc"], last_response=ledger[-1]["ended_utc"],
                 minimum_request_spacing_seconds=min(b - a for a, b in zip(starts, starts[1:])),
                 maximum_requests_in_60_seconds=maximum(60),
                 maximum_requests_in_600_seconds=maximum(600),
                 available=dict(Counter(r["arm"] for r in rows if r["status"] == "AVAILABLE")),
                 formats={arm: dict(Counter(r.get("format", "UNAVAILABLE") for r in rows
                                           if r["arm"] == arm)) for arm in ("A", "B")},
                 profile_responses=sum("profile_fields" in r for r in rows),
                 published_rows=len(public))
    (private / "REPORT_AUDIT.json").write_text(json.dumps(audit, indent=2) + "\n")
    print("Aggregate export complete; private audit retains request and disclosure details.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("private", "root", "inventory", "output"):
        parser.add_argument("--" + name, type=Path, required=True)
    args = parser.parse_args()
    report(args.private, args.root, args.inventory, args.output)


if __name__ == "__main__":
    main()
