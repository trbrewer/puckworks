"""SCI-MD-MAILLE-TRANSFER-001: bounded, non-scoring source-contract audit.

Table 5.10 contains empirical summaries, but the per-experiment maximum
normalization cannot be reconstructed from Table 5.11 marginal summaries.
This module exports inspectable observations; it deliberately supplies no fit
or prediction entry point. Existing registered components remain unchanged.
"""
from __future__ import annotations

import csv
import hashlib
import math
from collections import Counter

from puckworks import data

TASK = "SCI-MD-MAILLE-TRANSFER-001"
STATUS = "BLOCKED_SOURCE_CONTRACT"
MATERIALS = ("Omega_A", "Omega_B", "Omega_C")
ANALYTES = ("Caffeine", "3-CQA", "Citric Acid", "Malic Acid", "Quinic Acid")
TIMES = (10, 15, 20, 25, 30, 60, 180)
CANDIDATES = ("MAILLE_E0", "MAILLE_ES", "MAILLE_DS", "MAILLE_B2", "MAILLE_P2")
# Table 5.11 itself prints 3-CGA; Table 5.10 and methods identify 3-CQA.
# This is an explicit source header discrepancy, never a material alias.
REFERENCE_HEADERS = {a: ("3-CGA" if a == "3-CQA" else a) for a in ANALYTES}
BLOCKERS = (
    "Replicate-specific selected maxima and reference-time identities are missing for B/C.",
    "Table 5.11 marginal means/SD cannot reconstruct mean of per-replicate ratios or maximum-selection error.",
    "Early comparative cells lack exact time/replicate lineage; nominal clocks have a reported 1 s allowance.",
)


class SourceContractError(ValueError):
    """A source identity, schema, domain or scoring requirement is not met."""


def _number(value, label, low=0.0, high=math.inf):
    try:
        result = float(value)
    except (TypeError, ValueError) as exc:
        raise SourceContractError(f"{label}: expected finite number") from exc
    if not math.isfinite(result) or not low <= result <= high:
        raise SourceContractError(f"{label}: impossible/non-finite input")
    return result


def _unique(rows, label):
    result = {}
    for row in rows:
        key = row.get("Sample ID")
        if not isinstance(key, str) or not key.startswith("Omega_"):
            raise SourceContractError(f"{label}: ambiguous material identifier {key!r}")
        if key in result:
            raise SourceContractError(f"{label}: duplicate material identifier {key}")
        result[key] = row
    for key in MATERIALS:
        if key not in result:
            raise SourceContractError(f"{label}: missing material join {key}")
    return result


def _table(prefix, loader):
    """Guard the existing first-match loader against ambiguous files/headers."""
    paths = sorted(data.MAILLE.glob(prefix + " *.csv"))
    if len(paths) != 1:
        raise SourceContractError(f"{prefix}: expected exactly one source file, got {len(paths)}")
    path = paths[0]
    original = path.read_bytes()
    with path.open(newline="", encoding="utf-8-sig") as stream:
        reader = csv.reader(stream)
        header = next(reader)
        if len(set(header)) != len(header):
            raise SourceContractError(f"{prefix}: duplicate column identifier")
        if any(len(row) != len(header) for row in reader):
            raise SourceContractError(f"{prefix}: ragged rows")
    rows = loader()
    if path.read_bytes() != original:
        raise SourceContractError(f"{prefix}: source changed during read")
    identity = {"source_file": "puckworks/data/maille2024/" + path.name,
                "sha256": hashlib.sha256(original).hexdigest(), "rows": len(rows)}
    return rows, identity


def analysis_view():
    """Return a long-form view plus source receipt, without inventing missing cells.

    Normalization groups below are unresolved groups of replicate denominators,
    NOT a claim that all seven tabulations used one common denominator.
    """
    specs = (("Table 5.1", data.maille_materials),
             ("Table 5.4", data.maille_psd_hybrid),
             ("Table 6.3", data.maille_phi),
             ("Table 5.10", data.maille_normalized_curves),
             ("Table 5.11", data.maille_equilibrium))
    loaded, sources = {}, {}
    for prefix, loader in specs:
        loaded[prefix], sources[prefix] = _table(prefix, loader)
    mats = _unique(loaded["Table 5.1"], "Table 5.1")
    psd = _unique(loaded["Table 5.4"], "Table 5.4")
    phi = _unique(loaded["Table 6.3"], "Table 6.3")
    refs = _unique(loaded["Table 5.11"], "Table 5.11")
    descriptors = {}
    reference_summaries = []
    for material in MATERIALS:
        for field in ("Roast Degree", "Sieve class (um)"):
            if not mats[material].get(field):
                raise SourceContractError(f"{material}: missing preparation identity {field}")
        descriptors[material] = {
            "phi": _number(phi[material].get("phi"), "phi", high=1),
            "D43_um": _number(psd[material].get("D[4,3] Vol Mean (um)"), "D43_um", low=1e-12),
            "roast": mats[material]["Roast Degree"],
            "sieve_class_um": mats[material]["Sieve class (um)"],
        }
        for analyte in ANALYTES:
            for time in (180, 300, 600):
                base = f"{REFERENCE_HEADERS[analyte]} {time}s"
                reference_summaries.append({
                    "material_id": material, "analyte": analyte, "time_s": time,
                    "mean_mg_L": _number(refs[material].get(base + " avg (mg per L)"), base, low=1e-12),
                    "sd_mg_L": _number(refs[material].get(base + " sd (mg per L)"), base),
                    "source_file": sources["Table 5.11"]["source_file"],
                    "source_locator": f"Table 5.11 / {material} / {base}",
                    "role": "marginal_summary_not_curve_denominator_uncertainty",
                })
    expected = {f"{a} {m}" for a in ANALYTES for m in MATERIALS} | {"Time (s)"}
    output, missing, seen = [], [], set()
    for line, row in enumerate(loaded["Table 5.10"], start=2):
        if set(row) != expected:
            raise SourceContractError("Table 5.10: ambiguous/missing column identifiers")
        time = _number(row["Time (s)"], "time_s")
        if time not in TIMES:
            raise SourceContractError("Table 5.10: unsupported time identity")
        if time in seen:
            raise SourceContractError("Table 5.10: duplicate observation lineage/time")
        seen.add(time)
        for analyte in ANALYTES:
            for material in MATERIALS:
                column = f"{analyte} {material}"
                locator = f"Table 5.10 / CSV L{line} / {column} / t={time:g} s"
                value = row[column]
                if value is None or value in ("", "*"):
                    missing.append(locator)
                    continue
                output.append({
                    "material_id": material, "analyte": analyte, "time_s": time,
                    "observed_normalized_concentration": _number(value, locator, high=1),
                    "normalization_group": f"{material}/{analyte}/replicate_denominators_unresolved",
                    "source_file": sources["Table 5.10"]["source_file"],
                    "source_locator": locator,
                    "observation_kind": ("measured_comparative_value_approximate_time"
                                         if time <= 35 else "mean_of_three_normalized_replicates"),
                    "dependence_group": "MAILLE_WMBR/" + material,
                    "replicate_id": None,
                    "phi": descriptors[material]["phi"],
                    "D43_um": descriptors[material]["D43_um"],
                    "reported_decimal_places": 2,
                    "rounding_half_unit_if_nearest": 0.005,
                    "rounding_rule": "nearest rounding assumption; printed precision is two decimals",
                    "reported_time_allowance_s": 1.0 if time <= 35 else 0.0,
                    "reported_cross_material_time_difference_max_s": 0.5 if time <= 35 else 0.0,
                    "response_sd": None,
                    "denominator_selection_uncertainty": "UNKNOWN",
                    "primary_eligible": False,
                })
    receipt = {"sources": sources, "descriptors": descriptors,
               "reference_summaries": reference_summaries, "missing_cells": missing,
               "missing_times": sorted(set(TIMES) - seen)}
    return output, receipt


def require_scoring_eligible():
    """The inspected source contract has not earned a scoring operator."""
    raise SourceContractError(STATUS + ": " + " ".join(BLOCKERS))


def marginal_summary_counterexample():
    """Synthetic algebra check; not measured uncertainty or a proposed treatment.

    Both reference columns have identical mean/SD in both worlds. Changing only
    their replicate pairing changes the mean of normalization by selected maxima.
    """
    left = (0.9, 1.0, 1.1)
    aligned = sum(0.5 / max(a, b) for a, b in zip(left, left)) / 3
    reversed_pairing = sum(0.5 / max(a, b) for a, b in zip(left, reversed(left))) / 3
    return {"kind": "synthetic_nonidentifiability_example_not_empirical_bound",
            "aligned": aligned, "reversed_pairing": reversed_pairing,
            "difference": aligned - reversed_pairing}


def audit():
    rows, receipt = analysis_view()
    curves, diagnostics = [], []
    for material in MATERIALS:
        for analyte in ANALYTES:
            curve = [r for r in rows if r["material_id"] == material and r["analyte"] == analyte]
            early = sum(r["time_s"] <= 35 for r in curve)
            refs = [r for r in receipt["reference_summaries"]
                    if r["material_id"] == material and r["analyte"] == analyte]
            late = next((r for r in curve if r["time_s"] == 180), None)
            if late is not None:
                pooled = next(r["mean_mg_L"] for r in refs if r["time_s"] == 180) / max(
                    r["mean_mg_L"] for r in refs)
                diagnostics.append({"material_id": material, "analyte": analyte,
                                    "table510_minus_ratio_of_pooled_means":
                                        late["observed_normalized_concentration"] - pooled})
            curves.append({"material_id": material, "analyte": analyte,
                           "early_n": early, "late_n": len(curve) - early,
                           "both_windows_present": 0 < early < len(curve),
                           "qualified_for_scoring": False})
    result = {
        "task": TASK, "governance": "G1", "declaration": "NO_GOVERNING_PHYSICS_CHANGE",
        "scientific_verdict": STATUS, "failure_category": "Data, rights, or provenance failure",
        "blockers": list(BLOCKERS), "sources": receipt["sources"],
        "descriptors": receipt["descriptors"], "observed_cells": len(rows),
        "missing_cells": receipt["missing_cells"], "missing_times": receipt["missing_times"],
        "observation_kinds": dict(Counter(r["observation_kind"] for r in rows)),
        "curves": curves, "planned_material_folds": [
            {"held": m, "train": [t for t in MATERIALS if t != m]} for m in MATERIALS],
        "executed_folds": 0, "optimizer_attempts": 0, "predictions": 0,
        "primary_eligible_cells": 0, "fitted_parameters": 0,
        "candidate_status": {c: "NOT_IMPLEMENTED_SOURCE_GATE_STOP" for c in CANDIDATES},
        "analyte_decisions": {a: {"adequacy": "NOT_ADJUDICATED", "two_rate_gain": "NOT_ADJUDICATED",
                                  "source_phi_increment": "NOT_ADJUDICATED"} for a in ANALYTES},
        "observer": "per_experiment_maximum_then_late_replicate_average; early_selection_lineage_unknown",
        "normalization_operator_qualified": False,
        "pooled_denominator_diagnostic": diagnostics,
        "diagnostic_role": "source_operator_check_only; not prediction errors or model scores",
        "synthetic_counterexample": marginal_summary_counterexample(),
        "pre_scoring_freeze": "NOT_REACHED_SOURCE_GATE_STOP",
        "independent_pre_scoring_review": "NOT_PERFORMED_NO_SCORING",
        "tighter_numerical_repeat": "NOT_APPLICABLE_NO_FITS_OR_PREDICTIONS",
        "source_treatments": "NOT_FROZEN_NO_QUALIFIED_OBSERVER",
        "new_native_builds": 0, "new_native_integrations": 0,
        "production_defaults_and_runtime_lock": "UNCHANGED",
        "next_action": "OWNER_DISPOSITION; NO_SUCCESSOR_EXECUTION_AUTHORIZED",
    }
    return result
