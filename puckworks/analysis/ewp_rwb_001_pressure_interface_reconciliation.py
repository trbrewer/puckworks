"""Offline C1 pressure-bearing provenance gate for EWP-RWB-001."""
from collections import defaultdict
import math

from puckworks.data.visualizer.integration_contract import recover_integration

MIN_SHOTS = 20
MIN_USERS = 10


def valid_channel(record, name):
    """Use only normalized-store time/channel data; Bronze is never consulted."""
    hydraulic = record.get("hydraulic") or {}
    time = hydraulic.get("time__s")
    values = hydraulic.get(name)
    return (isinstance(time, list) and isinstance(values, list) and len(time) == len(values)
            and bool(time) and any(isinstance(v, (int, float)) and not isinstance(v, bool)
                                   and math.isfinite(v) for v in values))


def aggregate_gate(pairs):
    """Aggregate aligned ``(Bronze wrapper, schema-v6 record)`` pairs without identifiers."""
    groups = defaultdict(lambda: {"records": 0, "users": set(), "command": 0,
                                  "achieved": 0, "both": 0, "explicit": 0,
                                  "structural": 0})
    unresolved = ambiguous = conflicted = 0
    for bronze, normalized in pairs:
        family, _value, provenance, _rule = recover_integration(bronze.get("payload") or {})
        if family == "UNRESOLVED": unresolved += 1; continue
        if family == "AMBIGUOUS": ambiguous += 1; continue
        if family == "CONFLICTED": conflicted += 1; continue
        g = groups[family]; g["records"] += 1
        if bronze.get("hashed_user") is not None: g["users"].add(bronze["hashed_user"])
        kind = "structural" if provenance == "UNIQUE_STRUCTURAL_SIGNATURE" else "explicit"
        g[kind] += 1
        command = valid_channel(normalized, "pressure_goal__Pa")
        achieved = valid_channel(normalized, "pressure__Pa")
        g["command"] += command; g["achieved"] += achieved; g["both"] += command and achieved
    result = {}
    for family, g in sorted(groups.items()):
        users = len(g.pop("users")); disclosure = g["records"] >= MIN_SHOTS and users >= MIN_USERS
        result[family] = {**g, "contributors": users, "disclosure_qualified": disclosure,
                          "pressure_bearing_gate": disclosure and bool(g["command"] or g["achieved"])}
    return {"families": result, "unresolved": unresolved, "ambiguous": ambiguous,
            "conflicted": conflicted}
