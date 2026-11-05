"""Metadata-only Step 0 audit; deliberately contains no turnover evaluator.

Private output only. Channel presence is not measurement lineage or control mode.
Source authentication and canonical version semantics are inherited from X1.
"""

from __future__ import annotations

import argparse
from collections import defaultdict
import csv
import hashlib
import json
from pathlib import Path
from types import SimpleNamespace

from puckworks.analysis.pressure_peak_x1 import authenticate
from puckworks.data.visualizer.integration_contract import parser_family
from puckworks.lib.visualizer_harvest import iter_bronze


# Known explicit authority from EWP-RWB-001 C1, never a machine label.
FAMILIES = ("VISUALIZER_BEANCONQUEROR", "UNRESOLVED")
FIELDS = {
    "reported_machine": ("normalized", ("machine",)),
    "context_machine": ("normalized", ("context", "machine")),
    "native_machine": ("payload", ("brewdata", "machine")),
    "native_parser": ("payload", ("brewdata", "parser")),
    "native_profile": ("payload", ("brewdata", "profile")),
    "native_frames": ("payload", ("brewdata", "frames")),
    "native_stage": ("payload", ("brewdata", "stage")),
    "native_control_mode": ("payload", ("brewdata", "control_mode")),
    "native_scale": ("payload", ("brewdata", "scale")),
    "pressure_channel": ("normalized", ("hydraulic", "pressure__Pa")),
    "pressure_goal_channel": ("normalized", ("hydraulic", "pressure_goal__Pa")),
    "flow_goal_channel": ("normalized", ("hydraulic", "flow_goal_reported__native")),
    "flow_weight_channel": ("normalized", ("hydraulic", "mass_flow_from_scale__kg_per_s")),
    "weight_channel": ("normalized", ("hydraulic", "weight__kg")),
    "generic_state_channel": ("normalized", ("hydraulic", "state_change")),
    "salted_user": ("normalized", ("hashed_user",)),
    "dose": ("normalized", ("context", "dose__kg")),
    "grinder_model": ("normalized", ("context", "grinder_model")),
    "grinder_setting": ("normalized", ("context", "grinder_setting")),
    "coffee_brand": ("payload", ("bean_brand",)),
    "coffee_type": ("payload", ("bean_type",)),
    "roast_date": ("payload", ("roast_date",)),
    "roast_level": ("normalized", ("context", "roast_level")),
}


def at(record, path):
    for key in path:
        if not isinstance(record, dict):
            return None
        record = record.get(key)
    return record


def present(value):
    """Container presence only: zero/-1 are present; neither means qualified."""
    if value is None:
        return False
    if isinstance(value, (str, list, dict)):
        return bool(value)
    return True


def format_family(payload):
    parser = at(payload, ("brewdata", "parser"))
    if parser is None:
        return "UNRESOLVED"
    if parser_family(parser) == "VISUALIZER_BEANCONQUEROR":
        return "VISUALIZER_BEANCONQUEROR"
    raise ValueError("Explicit parser differs from retained C1 authority; inspect before reuse")


def field_presence(normalized, payload):
    sources = {"normalized": normalized, "payload": payload}
    return {key: present(at(sources[source], path))
            for key, (source, path) in FIELDS.items()}


def publishable_count(count, users, total, all_users):
    """Existing 20-shot/10-user rule, including the complementary cell.

    Corpus/format-wide zero or complete coverage reveals no small subgroup.
    Missing-linkage records cannot count toward the distinct-user threshold.
    """
    if total < 20 or len(all_users) < 10:
        return False
    if count == 0 or count == total:
        return True
    return (count >= 20 and len(users) >= 10
            and total - count >= 20 and len(all_users - users) >= 10)


def audit(root, inventory):
    snapshot, receipt = authenticate(root, inventory)
    integrity = receipt["integrity"]
    if integrity["n_revisions"] or integrity["n_same_timestamp_conflicts"]:
        raise ValueError("Snapshot no longer matches the unrevised C1 join contract")
    bronze = {}
    for row in iter_bronze(SimpleNamespace(out_dir=Path(root))):
        key = (row["id"], row["updated_at"])
        if key in bronze:
            raise ValueError("Duplicate Bronze join key")
        payload = row["payload"]
        # Retain only required metadata, never traces or outcomes, for the join.
        bronze[key] = (format_family(payload), {
            field: present(at(payload, path))
            for field, (source, path) in FIELDS.items() if source == "payload"
        })
    counts = defaultdict(lambda: defaultdict(int))
    users = defaultdict(lambda: defaultdict(set))
    for row in snapshot.latest():
        family, native = bronze.pop((row["id"], row["updated_at"]))
        flags = field_presence(row, {}) | native
        for field, yes in {"records": True, **flags}.items():
            if yes:
                counts[family][field] += 1
                if row.get("hashed_user"):
                    users[family][field].add(row["hashed_user"])
    if bronze:
        raise ValueError("Unmatched Bronze keys")
    if sum(c["records"] for c in counts.values()) != integrity["n_logical_records"]:
        raise ValueError("Canonical record count mismatch")
    coverage = []
    for family in FAMILIES:
        total = counts[family]["records"]
        all_users = users[family]["records"]
        for field in FIELDS:
            count, field_users = counts[family][field], users[family][field]
            coverage.append({
                "upload_format": family, "field": field, "records": total,
                "present_records": count, "distinct_users": len(field_users),
                "publishable": publishable_count(count, field_users, total, all_users),
            })
    return {"authentication": receipt, "coverage": coverage,
            "counts_are": "nonempty containers/scalars, not validity or lineage",
            "turnover_calculated": False}


def accompanying_metadata(collection, inventory):
    """Hash existing non-array metadata; detect additions without decoding shots."""
    manifest = json.loads(Path(inventory).read_text())
    known = {r["relative_path"] for r in manifest["entries"]
             if r["relative_path"].startswith("visualizer/")}
    rows = [r for r in manifest["entries"] if r["relative_path"] in known
            and r.get("sha256") and not r["relative_path"].endswith(".gz")
            and not r["relative_path"].endswith(".harvest_salt")]
    differences = [r["relative_path"] for r in rows if
                   hashlib.sha256((collection / r["relative_path"]).read_bytes()).hexdigest()
                   != r["sha256"]]
    added = [str(p.relative_to(collection)) for p in (collection / "visualizer").rglob("*")
             if p.is_file() and str(p.relative_to(collection)) not in known]
    return {"compared_metadata_files": len(rows), "all_match": not differences,
            "differences": differences, "unregistered_files": sorted(added)}


def write_qualification(result, destination):
    """Export only field availability; never treat generic names as lineage."""
    units = {"pressure_channel": "Pa (native bar)",
             "pressure_goal_channel": "Pa (native bar)",
             "flow_weight_channel": "kg/s (native g/s)",
             "weight_channel": "kg (native g)", "dose": "kg",
             "flow_goal_channel": "native units UNKNOWN"}
    with Path(destination).open("w", newline="") as stream:
        writer = csv.DictWriter(stream, lineterminator="\n", fieldnames=[
            "upload_format", "records", "field", "field_path", "units",
            "present_records", "lineage_or_interpretation", "credit",
        ])
        writer.writeheader()
        for row in result["coverage"]:
            field = row["field"]
            source, path = FIELDS[field]
            if field == "native_parser":
                interpretation = "explicit parser only; hardware and sensors UNKNOWN"
            elif field.endswith("channel"):
                interpretation = "container presence only; source semantics UNKNOWN"
            elif field.startswith("native_") or "machine" in field:
                interpretation = "named path coverage only; no qualifying authority"
            else:
                interpretation = "context presence only; no matching performed"
            writer.writerow({
                "upload_format": row["upload_format"], "records": row["records"],
                "field": field, "field_path": source + "." + ".".join(path),
                "units": units.get(field, "not assigned"),
                "present_records": row["present_records"] if row["publishable"] else "SUPPRESSED",
                "lineage_or_interpretation": interpretation,
                "credit": "Data source: Visualizer; thanks to contributing users.",
            })


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--inventory", type=Path, required=True)
    parser.add_argument("--private", type=Path, required=True)
    args = parser.parse_args()
    repo = Path(__file__).resolve().parents[2]
    if args.private.resolve().is_relative_to(repo):
        parser.error("Private output must be outside the repository")
    args.private.mkdir(parents=True, exist_ok=True)
    result = audit(args.root, args.inventory)
    result["accompanying_metadata"] = accompanying_metadata(args.root.parent.parent, args.inventory)
    (args.private / "metadata_audit.json").write_text(json.dumps(result, indent=2) + "\n")
    write_qualification(result, args.private / "QUALIFICATION.csv")
    print("Metadata audit retained privately; no pressure-flow outcomes calculated.")


if __name__ == "__main__":
    main()
