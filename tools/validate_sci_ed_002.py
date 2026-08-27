"""Fail-closed validator for SCI-ED-002 prospective design capacity (never evidence)."""
from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "docs" / "analysis" / "sci_ed_002"
STATUS = "PROSPECTIVE_DESIGN_CAPACITY_ONLY_NO_MEASUREMENTS"


def load_rows() -> list[dict]:
    with (PACK / "SAMPLING_MATRIX.csv").open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def fail(code: str) -> None:
    raise ValueError(code)


def mutate(rows: list[dict], mutation: str | None, state: dict) -> None:
    if not mutation:
        return
    if mutation == "shared_base_material_across_groups": rows[6]["base_material_id"] = rows[0]["base_material_id"]
    elif mutation == "shared_source_package_across_folds":
        for row in rows[6:12]: row["source_package_id"] = rows[0]["source_package_id"]
    elif mutation == "only_three_laboratories":
        for row in rows:
            if row["laboratory_id"] == "LAB-D": row["laboratory_id"] = "LAB-C"
    elif mutation == "missing_species_roast_cell": rows.pop(0)
    elif mutation == "fewer_than_20_open_base_materials":
        for row in rows:
            if row["validation_group_id"] == "VG05" and row["base_material_id"].endswith("S2"): row["base_material_id"] = row["base_material_id"].replace("S2", "S1")
    elif mutation == "bridge_rows_counted_as_primary_units": rows.append(dict(rows[0], material_roast_unit_id="BR-A-LIGHT", role="BRIDGE"))
    elif mutation == "unpaired_analyte_plan": rows[0]["analyte_plan"] = "caffeine"
    elif mutation == "missing_moisture": rows[0]["moisture_plan"] = ""
    elif mutation == "missing_uncertainty": rows[0]["uncertainty_plan"] = ""
    elif mutation == "vg06_used_by_open_core_reducer": state["vg06_open_access"] = True
    elif mutation == "c_s0_mapping_status_changed": state["c_s0"] = "ESTABLISHED"


def validate(mutation: str | None = None) -> dict:
    rows = load_rows()
    state = {"vg06_open_access": False, "c_s0": "NOT_ESTABLISHED"}
    mutate(rows, mutation, state)
    if any(r["role"] == "BRIDGE" for r in rows): fail("BRIDGE_RECORD_COUNTED_AS_PRIMARY")
    if state["vg06_open_access"]: fail("SEALED_GROUP_ACCESS_BY_OPEN_REDUCER")
    if state["c_s0"] != "NOT_ESTABLISHED": fail("C_S0_MAPPING_MUST_REMAIN_NOT_ESTABLISHED")
    by_group: dict[str, list[dict]] = defaultdict(list)
    for row in rows: by_group[row["validation_group_id"]].append(row)
    if set(by_group) != {f"VG{i:02d}" for i in range(1, 7)}: fail("VALIDATION_GROUP_SET_INVALID")
    expected = {(s, r) for s in ("Arabica", "Robusta") for r in ("light", "medium", "dark")}
    if any({(x["species"], x["roast_stratum"]) for x in group} != expected for group in by_group.values()): fail("GROUP_SPECIES_ROAST_MATRIX_INCOMPLETE")
    owner = {}
    for row in rows:
        base, gid = row["base_material_id"], row["validation_group_id"]
        if base in owner and owner[base] != gid: fail("BASE_MATERIAL_CROSSES_VALIDATION_GROUPS")
        owner[base] = gid
    for field, code in (("source_package_id", "SOURCE_PACKAGE_OVERLAP_ACROSS_GROUPS"), ("data_lineage_id", "DATA_LINEAGE_OVERLAP_ACROSS_GROUPS")):
        owners = {}
        for row in rows:
            value, gid = row[field], row["validation_group_id"]
            if value in owners and owners[value] != gid: fail(code)
            owners[value] = gid
    open_rows = [r for r in rows if r["validation_group_id"] != "VG06"]
    if len(open_rows) != 30 or len(rows) != 36: fail("PRIMARY_UNIT_COUNT_INVALID")
    if len({r["base_material_id"] for r in open_rows}) < 20: fail("OPEN_CORE_REQUIRES_20_BASE_MATERIALS")
    if len({r["base_material_id"] for r in rows}) != 24: fail("TOTAL_REQUIRES_24_BASE_MATERIALS")
    if len({r["laboratory_id"] for r in open_rows}) < 4: fail("OPEN_CORE_REQUIRES_FOUR_LABORATORIES")
    if any(r["analyte_plan"] != "caffeine|trigonelline" for r in rows): fail("PRIMARY_ANALYTE_PLAN_NOT_PAIRED")
    if any(not r["moisture_plan"] for r in rows): fail("PRIMARY_MOISTURE_PLAN_MISSING")
    if any(not r["uncertainty_plan"] for r in rows): fail("PRIMARY_UNCERTAINTY_PLAN_MISSING")
    return {"status": STATUS, "projected_gates": {"open_primary_units": 30, "total_primary_units": 36, "open_base_materials": 20, "total_base_materials": 24, "open_laboratories": 4, "sealed_groups_excluded": 1, "bridge_primary_count": 0}}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fixture")
    parser.add_argument("--output")
    args = parser.parse_args()
    mutation = None
    if args.fixture:
        mutation = json.loads(Path(args.fixture).read_text(encoding="utf-8")).get("mutation")
    try:
        result = validate(mutation)
    except ValueError as exc:
        result = {"status": "FAIL", "failure_reason": str(exc)}
        code = 1
    else: code = 0
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output: Path(args.output).write_text(rendered, encoding="utf-8")
    else: print(rendered, end="")
    return code


if __name__ == "__main__":
    raise SystemExit(main())
