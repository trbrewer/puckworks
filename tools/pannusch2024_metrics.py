#!/usr/bin/env python3
"""Compute the four-cell PANNUSCH-RAW-REPRO-001 attribution without fitting."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def legacy_experiments(valid, ledger):
    exps = {e: [dict(r) for r in rows] for e, rows in valid.items()}
    for change in ledger["affected_keys"]:
        bits = dict(part.split("=", 1) for part in change["key"].split(";"))
        row = next(r for r in exps[int(bits["exp"])] if int(r["fraction"]) == int(bits["fraction"]))
        row[bits["field"]] = float(change["old"])
    return exps


def cell(ps, exps, source_grind):
    params = ps._solute_params()
    grinds = ps._source_grinds() if source_grind else {}
    per_experiment = {}
    by_solute = {s: [] for s in ("caffeine", "trigonelline", "5CQA", "tds")}
    warnings = []
    for eid, rows in sorted(exps.items()):
        per_experiment[str(eid)] = {}
        for solute in by_solute:
            value = ps.mape_for_experiment(rows, solute, params[solute], grinds.get(eid))
            per_experiment[str(eid)][solute] = value
            if value is None:
                warnings.append(f"experiment {eid} {solute}: non-positive denominator")
            else:
                by_solute[solute].append(value)
    means = {s: float(np.mean(v)) for s, v in by_solute.items()}
    return {"per_experiment_mape_percent": per_experiment,
            "per_analyte_mape_percent": means,
            "pooled_mape_percent": float(np.mean(list(means.values()))),
            "experiment_analyte_scores": sum(map(len, by_solute.values())),
            "accepted_experiment_fraction_rows": sum(len(v) for v in exps.values()),
            "invalid_physical_fraction_records_excluded": 3,
            "warnings": warnings}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    from puckworks.models.pannusch2024 import solver as ps
    root = Path(__file__).resolve().parents[1]
    data = root / "puckworks/data/pannusch2024"
    valid = ps._exp_kinetics()
    ledger_path = data / "experimental_kinetics_correction_ledger.json"
    ledger = json.loads(ledger_path.read_text())
    legacy = legacy_experiments(valid, ledger)
    result = {
        "task_id": "PANNUSCH-RAW-REPRO-001",
        "metric": "mean absolute percentage error over six fractions; pooled is equal-weight mean of four analyte means",
        "zero_policy": "experiment/analyte score omitted and warned if any measured denominator is non-positive",
        "parameter_refit": False,
        "parameters_sha256": sha(data / "table2_fitted_params.csv"),
        "solver_sha256": sha(root / "puckworks/models/pannusch2024/solver.py"),
        "grind_mapping_sha256": sha(data / "experiment_grind_assignments.csv"),
        "legacy_data_sha256": ledger["base_file_sha256"],
        "valid_only_data_sha256": ledger["candidate_file_sha256"],
        "cells": {
            "A_LEGACY_DATA_CENTER_GRIND": cell(ps, legacy, False),
            "B_VALID_ONLY_DATA_CENTER_GRIND": cell(ps, valid, False),
            "C_LEGACY_DATA_SOURCE_GRIND": cell(ps, legacy, True),
            "D_VALID_ONLY_DATA_SOURCE_GRIND": cell(ps, valid, True),
        },
    }
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
