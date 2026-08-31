#!/usr/bin/env python3
"""Validate reviewed local-corpus family coverage and authority invariants."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "puckworks/data/LOCAL_CORPUS_FAMILY_INDEX.json"
PERMISSION = ROOT / "puckworks/data/VISUALIZER_API_PERMISSION_STATUS.json"


def validate() -> list[str]:
    problems: list[str] = []
    index = json.loads(INDEX.read_text(encoding="utf-8"))
    records = index["families"]
    ids = [item["family_id"] for item in records]
    aliases = [alias.lower() for item in records for alias in item["aliases"]]
    if len(records) != 39 or len(set(ids)) != 39:
        problems.append("family census is not 39 unique families")
    if index["mapped_or_registered_family_count"] != 39 or index["unregistered_material_family_count"]:
        problems.append("coverage counts are not 39 mapped / 0 unregistered")
    if len(aliases) != len(set(aliases)):
        problems.append("family aliases do not resolve uniquely")
    for item in records:
        if not item["manifest_dataset_ids"] or not item["source_registration"]:
            problems.append(f"{item['family_id']}: no manifest/source registration")
        if not item["rights_access_status"] or not item["raw_access_status"]:
            problems.append(f"{item['family_id']}: rights/access absent")
        if not item["model_chain_stages"] or "UNKNOWN" in item["model_chain_stages"]:
            problems.append(f"{item['family_id']}: model-chain stage absent or unknown")
    encoded = INDEX.read_text(encoding="utf-8")
    if re.search(r"/(?:home|Users)/", encoded):
        problems.append("local absolute path in family index")
    permission = json.loads(PERMISSION.read_text(encoding="utf-8"))
    snapshot = permission["corpus_records"][0]
    if snapshot["access_status"] != "PERMISSIONED_LOCAL_API_SNAPSHOT_READY_FOR_INTERNAL_ANALYSIS":
        problems.append("Visualizer local snapshot is not permissioned-ready")
    if permission["raw_redistribution"] or permission["private_record_use"]:
        problems.append("Visualizer redistribution/private-use authority is too broad")
    if permission["tds_ey"]["population_chemistry_ready"]:
        problems.append("Visualizer population chemistry is overstated")
    return problems


if __name__ == "__main__":
    failures = validate()
    if failures:
        raise SystemExit("\n".join(failures))
    print("local corpus coverage valid: 39 mapped/registered, 0 unregistered")
