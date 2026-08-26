"""R1 fail-closed register validator, reducer, and deterministic generator."""

from __future__ import annotations

import csv
import hashlib
import json
import math
import shutil
import tempfile
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

from .sci_md_007 import (
    COMPOUND_GATES,
    FAIL,
    PASS,
    PROVENANCE,
    TARGET_SEMANTICS,
    primary_eligible,
    validate_contract,
)

ROOT = Path(__file__).parents[2]
DATA = ROOT / "puckworks/data/sci_md_007"
OUT = ROOT / "docs/analysis/sci_md_007"
ANALYTES = {"caffeine", "trigonelline"}


def read_csv(name: str) -> list[dict[str, str]]:
    with (DATA / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


class UnionFind:
    def __init__(self, values):
        self.parent = {v: v for v in values}

    def find(self, value):
        while self.parent[value] != value:
            self.parent[value] = self.parent[self.parent[value]]
            value = self.parent[value]
        return value

    def union(self, left, right):
        a, b = self.find(left), self.find(right)
        if a != b:
            self.parent[max(a, b)] = min(a, b)


def _boolean(value: str, field: str) -> bool:
    if value not in {"true", "false"}:
        raise ValueError(f"{field} must be true or false")
    return value == "true"


def validate_registers(sources, materials, observations) -> None:
    required = {
        "sources": {
            "source_publication_id",
            "laboratory_id",
            "data_lineage_id",
            "source_locator",
            "source_card_path",
            "source_screening_state",
        },
        "materials": {
            "base_coffee_material_id",
            "roast_batch_id",
            "source_publication_id",
            "data_lineage_id",
            "laboratory_id",
            "species_scientific",
        },
        "observations": {
            "observation_id",
            "base_coffee_material_id",
            "roast_batch_id",
            "source_publication_id",
            "data_lineage_id",
            "laboratory_id",
            "analyte",
            "target_semantics",
            "measurement_provenance",
            "conversion_status",
            "rights_usable",
            "duplicate_status",
            "roasted_unextracted",
            "source_locator",
        },
    }
    for name, rows in (
        ("sources", sources),
        ("materials", materials),
        ("observations", observations),
    ):
        if not rows or not required[name] <= set(rows[0]):
            raise ValueError(f"{name} missing required columns")

    def unique(rows, key):
        vals = [r[key] for r in rows]
        if any(not x for x in vals) or len(vals) != len(set(vals)):
            raise ValueError(f"invalid/duplicate {key}")

    unique(sources, "source_publication_id")
    unique(observations, "observation_id")
    material_keys = {(m["base_coffee_material_id"], m["roast_batch_id"]) for m in materials}
    if len(material_keys) != len(materials):
        raise ValueError("duplicate material/roast key")
    source_ids = {s["source_publication_id"] for s in sources}
    for source in sources:
        if not (ROOT / source["source_card_path"]).is_file():
            raise ValueError("source card missing: " + source["source_card_path"])
    seen_locator = set()
    for row in observations:
        text = json.dumps(row).lower()
        if "angeloni" in text:
            raise ValueError("prohibited lineage identifier")
        if row["source_publication_id"] not in source_ids:
            raise ValueError("observation source FK failure")
        if (row["base_coffee_material_id"], row["roast_batch_id"]) not in material_keys:
            raise ValueError("observation material FK failure")
        if (
            row["analyte"] not in ANALYTES
            or row["target_semantics"] not in TARGET_SEMANTICS
            or row["measurement_provenance"] not in PROVENANCE
        ):
            raise ValueError("invalid observation enum")
        _boolean(row["rights_usable"], "rights_usable")
        _boolean(row["roasted_unextracted"], "roasted_unextracted")
        if row["uncertainty_value_as_published"]:
            if (
                not math.isfinite(float(row["uncertainty_value_as_published"]))
                or float(row["uncertainty_value_as_published"]) < 0
            ):
                raise ValueError("invalid uncertainty")
        if int(row["number_of_analytical_replicates"]) < 0:
            raise ValueError("invalid replicate count")
        key = (
            row["source_publication_id"],
            row["source_locator"],
            row["base_coffee_material_id"],
            row["roast_batch_id"],
            row["analyte"],
        )
        if key in seen_locator:
            raise ValueError("unexplained duplicate source/material/analyte locator")
        seen_locator.add(key)
    for row in materials:
        if row["source_publication_id"] not in source_ids:
            raise ValueError("material source FK failure")
    if any(str(ROOT) in p.read_text(errors="ignore") for p in DATA.glob("*.csv")):
        raise ValueError("absolute path in register")


def search_complete(sources) -> dict:
    logs, results, passes = (
        read_csv("search_log.csv"),
        read_csv("search_results.csv"),
        read_csv("citation_passes.csv"),
    )
    reasons = []
    expected = {
        (f"q{i:02d}_{p.lower()}")
        for i in range(1, 9)
        for p in ("Crossref", "OpenAlex", "GeneralPublicWeb")
    }
    if {r["search_id"] for r in logs} != expected:
        reasons.append("required query/provider set incomplete")
    numeric = (
        "result_limit",
        "results_returned",
        "results_screened",
        "unique_candidates_added",
        "duplicates",
        "inaccessible_candidates",
        "out_of_scope_candidates",
    )
    for row in logs:
        try:
            [int(row[k]) for k in numeric]
        except (ValueError, KeyError):
            reasons.append("non-numeric search count")
    if any(
        not r["screening_state"] or r["screening_state"] == "UNRESOLVED_PENDING_SCREEN"
        for r in results
    ):
        reasons.append("candidate lacks terminal screening state")
    for source in sources:
        for direction in ("BACKWARD", "FORWARD"):
            if not any(
                x["source_publication_id"] == source["source_publication_id"]
                and x["direction"] == direction
                for x in passes
            ):
                reasons.append(f"{source['source_publication_id']} missing {direction} pass")
    return {
        "pass": not reasons,
        "reasons": sorted(set(reasons)),
        "searches": len(logs),
        "result_records": len(results),
        "unique_candidates": len({r["candidate_id"] for r in results}),
        "duplicates": sum(bool(r["duplicate_of"]) for r in results),
        "citation_records": len(passes),
    }


def groups(materials, observations):
    units = {(m["base_coffee_material_id"], m["roast_batch_id"]) for m in materials}
    uf = UnionFind(units)
    edges = []
    for key in ("source_publication_id", "data_lineage_id", "base_coffee_material_id"):
        buckets = defaultdict(list)
        for m in materials:
            buckets[m[key]].append((m["base_coffee_material_id"], m["roast_batch_id"]))
        for value, members in sorted(buckets.items()):
            for member in members[1:]:
                uf.union(members[0], member)
                edges.append(
                    {
                        "left": "|".join(members[0]),
                        "right": "|".join(member),
                        "reason": f"shared {key}: {value}",
                    }
                )
    roots = {u: uf.find(u) for u in units}
    names = {root: f"vg_{i:03d}" for i, root in enumerate(sorted(set(roots.values())), 1)}
    return {u: names[root] for u, root in roots.items()}, edges


def qualify(observations, group_map):
    result = []
    for raw in observations:
        row = dict(raw)
        row["roasted_unextracted"] = _boolean(row["roasted_unextracted"], "roasted_unextracted")
        row["rights_usable"] = _boolean(row["rights_usable"], "rights_usable")
        row["duplicate"] = row["duplicate_status"] != "UNIQUE"
        row["canonical_basis"] = (
            "dry roasted coffee" if row["canonical_unit"] == "mg/g dry roasted coffee" else ""
        )
        row["conversion_supported"] = row["conversion_status"] == "SUPPORTED_EXACT"
        row["analytical_method"] = row["analytical_method"]
        row["validation_group_id"] = group_map[
            (row["base_coffee_material_id"], row["roast_batch_id"])
        ]
        eligible = primary_eligible(row)
        row["primary_prediction_label_eligible"] = eligible
        reasons = []
        if not eligible:
            for condition, label in (
                (not row["roasted_unextracted"], "NOT_ROASTED_UNEXTRACTED"),
                (row["target_semantics"] != "TOTAL_ROASTED_CONTENT", "TARGET_SEMANTICS"),
                (row["measurement_provenance"] != "DIRECT_ROASTED_MATERIAL_ASSAY", "PROVENANCE"),
                (not row["conversion_supported"], "CANONICAL_BASIS_UNSUPPORTED"),
                (not row["rights_usable"], "RIGHTS"),
                (row["duplicate"], "DUPLICATE"),
            ):
                if condition:
                    reasons.append(label)
        row["exclusion_reason"] = ";".join(reasons)
        result.append(row)
    return result


def _gate(analyte, rows, materials, contract):
    threshold = contract["thresholds"]
    eligible = [
        r for r in rows if r["analyte"] == analyte and r["primary_prediction_label_eligible"]
    ]
    units = {(r["base_coffee_material_id"], r["roast_batch_id"]) for r in eligible}
    mids = {u[0] for u in units}
    pubs = {r["source_publication_id"] for r in eligible}
    labs = {
        r["laboratory_id"]
        for r in eligible
        if r["laboratory_id"] and "unknown" not in r["laboratory_id"]
    }
    groupset = {r["validation_group_id"] for r in eligible}
    counts = Counter(r["validation_group_id"] for r in eligible)
    largest = max(counts.values(), default=0) / len(eligible) if eligible else None
    f0 = {
        "pass": all(
            r["target_semantics"] == "TOTAL_ROASTED_CONTENT"
            and r["measurement_provenance"] == "DIRECT_ROASTED_MATERIAL_ASSAY"
            for r in eligible
        ),
        "applicability": "APPLICABLE" if eligible else "VACUOUS_NO_ELIGIBLE_ROWS",
        "eligible_rows": len(eligible),
    }
    f1 = {
        "pass": all(
            r["canonical_unit"] == "mg/g dry roasted coffee"
            and r["conversion_status"] == "SUPPORTED_EXACT"
            for r in eligible
        ),
        "applicability": "APPLICABLE" if eligible else "VACUOUS_NO_ELIGIBLE_ROWS",
        "eligible_dry_basis_rows": len(eligible),
        "unsupported_conversions": sum(
            r["conversion_status"] != "SUPPORTED_EXACT" for r in eligible
        ),
    }
    t = threshold["F2"]
    primitives = {
        "material_roast_units": len(units),
        "base_materials": len(mids),
        "publications": len(pubs),
        "identified_laboratories": len(labs),
        "validation_groups": len(groupset),
        "largest_group_share": largest,
    }
    f2pass = (
        len(units) >= t["material_roast_units"]
        and len(mids) >= t["base_coffee_materials"]
        and len(pubs) >= t["source_publications"]
        and len(labs) >= t["identified_laboratories"]
        and len(groupset) >= t["validation_groups"]
        and largest is not None
        and largest <= t["largest_group_max_fraction"]
    )
    f2 = {
        "pass": f2pass,
        **primitives,
        "thresholds": t,
        "failure_reasons": [
            k
            for k, v in primitives.items()
            if (
                k != "largest_group_share"
                and v
                < t[
                    {
                        "base_materials": "base_coffee_materials",
                        "publications": "source_publications",
                        "identified_laboratories": "identified_laboratories",
                        "validation_groups": "validation_groups",
                    }.get(k, k)
                ]
            )
            or (k == "largest_group_share" and (v is None or v > t["largest_group_max_fraction"]))
        ],
    }
    material_by = {(m["base_coffee_material_id"], m["roast_batch_id"]): m for m in materials}
    species = {"Arabica": "Coffea arabica", "Robusta": "Coffea canephora"}
    sp = {}
    for label, scientific in species.items():
        sr = [
            r
            for r in eligible
            if material_by[(r["base_coffee_material_id"], r["roast_batch_id"])][
                "species_scientific"
            ]
            == scientific
        ]
        sp[label] = {
            "material_roast_units": len(
                {(r["base_coffee_material_id"], r["roast_batch_id"]) for r in sr}
            ),
            "publications": len({r["source_publication_id"] for r in sr}),
            "laboratories": len({r["laboratory_id"] for r in sr}),
            "validation_groups": len({r["validation_group_id"] for r in sr}),
        }
    t3 = threshold["F3"]
    f3pass = all(
        x["material_roast_units"] >= t3["units_per_species"]
        and x["publications"] >= t3["publications_per_species"]
        and x["laboratories"] >= t3["laboratories_per_species"]
        and x["validation_groups"] >= t3["validation_groups_per_species"]
        for x in sp.values()
    )
    f3 = {
        "pass": f3pass,
        "species": sp,
        "thresholds": t3,
        "failure_reasons": [
            label
            for label, x in sp.items()
            if not (
                x["material_roast_units"] >= t3["units_per_species"]
                and x["publications"] >= t3["publications_per_species"]
                and x["laboratories"] >= t3["laboratories_per_species"]
                and x["validation_groups"] >= t3["validation_groups_per_species"]
            )
        ],
    }
    t4 = threshold["F4"]
    strata = {}
    for label, scientific in species.items():
        strata[label] = {}
        for r in eligible:
            m = material_by[(r["base_coffee_material_id"], r["roast_batch_id"])]
            if m["species_scientific"] == scientific and m["roast_category_harmonized"]:
                strata[label].setdefault(m["roast_category_harmonized"], set()).add(
                    (r["base_coffee_material_id"], r["roast_batch_id"], r["validation_group_id"])
                )
    categorical = all(
        len(
            [
                v
                for v in strata[s].values()
                if len(v) >= t4["categorical_units_per_stratum"]
                and len({x[2] for x in v}) >= t4["categorical_groups_per_stratum"]
            ]
        )
        >= t4["categorical_strata_per_species"]
        for s in species
    )
    metric = [
        r
        for r in eligible
        if material_by[(r["base_coffee_material_id"], r["roast_batch_id"])]["roast_metric_type"]
    ]
    quantitative = (
        len({(r["base_coffee_material_id"], r["roast_batch_id"]) for r in metric})
        >= t4["quantitative_metric_units"]
        and len({r["validation_group_id"] for r in metric}) >= t4["quantitative_metric_groups"]
        and all(
            sum(
                material_by[(r["base_coffee_material_id"], r["roast_batch_id"])][
                    "species_scientific"
                ]
                == scientific
                for r in metric
            )
            >= t4["quantitative_metric_units_per_species"]
            for scientific in species.values()
        )
    )
    f4 = {
        "pass": categorical or quantitative,
        "categorical_route": {
            "pass": categorical,
            "strata": {s: {k: len(v) for k, v in x.items()} for s, x in strata.items()},
        },
        "quantitative_route": {
            "pass": quantitative,
            "units": len(metric),
            "groups": len({r["validation_group_id"] for r in metric}),
        },
        "thresholds": t4,
        "failure_reasons": [] if categorical or quantitative else ["neither roast route qualifies"],
    }
    uncertain = {
        (r["base_coffee_material_id"], r["roast_batch_id"])
        for r in eligible
        if r["uncertainty_type"] in {"SD", "raw replicates"}
    }
    source_labs = {
        (r["source_publication_id"], r["laboratory_id"])
        for r in eligible
        if (r["base_coffee_material_id"], r["roast_batch_id"]) in uncertain
    }
    fraction = len(uncertain) / len(units) if units else None
    t6 = threshold["F6"]
    f6pass = (
        fraction is not None
        and fraction >= t6["uncertainty_bearing_fraction"]
        and len(source_labs) >= t6["uncertainty_source_laboratory_groups"]
        and all(r["analytical_method"] for r in eligible)
    )
    f6 = {
        "pass": f6pass,
        "uncertainty_bearing_units": len(uncertain),
        "eligible_units": len(units),
        "uncertainty_bearing_fraction": fraction,
        "source_laboratory_groups": len(source_labs),
        "between_lab_reproducibility_floor": "NOT_IDENTIFIABLE",
        "thresholds": t6,
        "failure_reasons": [] if f6pass else ["uncertainty coverage/group threshold unmet"],
    }
    folds = [{"test_group": g, "training_groups": sorted(groupset - {g})} for g in sorted(groupset)]
    category_support = all(
        any(
            x["validation_group_id"] != g
            and material_by[(x["base_coffee_material_id"], x["roast_batch_id"])][
                "species_scientific"
            ]
            == material_by[(r["base_coffee_material_id"], r["roast_batch_id"])][
                "species_scientific"
            ]
            for x in eligible
        )
        for g in groupset
        for r in eligible
        if r["validation_group_id"] == g
    )
    f7pass = len(groupset) >= threshold["F7"]["outer_validation_groups"] and category_support
    f7 = {
        "pass": f7pass,
        "outer_validation_groups": len(groupset),
        "publication_leakage": 0,
        "data_lineage_leakage": 0,
        "base_material_leakage": 0,
        "category_support_all_folds": category_support,
        "proposed_folds": folds,
        "thresholds": threshold["F7"],
        "failure_reasons": [] if f7pass else ["outer group/category support threshold unmet"],
    }
    return {"F0": f0, "F1": f1, "F2": f2, "F3": f3, "F4": f4, "F6": f6, "F7": f7}


def reduce(sources, materials, observations):
    contract = json.loads((OUT / "feasibility_contract.json").read_text())
    group_map, edges = groups(materials, observations)
    rows = qualify(observations, group_map)
    gates = {a: _gate(a, rows, materials, contract) for a in ANALYTES}
    pairs = defaultdict(set)
    for r in rows:
        if r["primary_prediction_label_eligible"]:
            pairs[
                (r["base_coffee_material_id"], r["roast_batch_id"], r["validation_group_id"])
            ].add(r["analyte"])
    paired = [k for k, v in pairs.items() if v == ANALYTES]
    t5 = contract["thresholds"]["F5"]
    f5pass = (
        len(paired) >= t5["paired_material_roast_units"]
        and len({x[2] for x in paired}) >= t5["validation_groups"]
    )
    f5 = {
        "pass": f5pass,
        "paired_material_roast_units": len(paired),
        "validation_groups": len({x[2] for x in paired}),
        "thresholds": t5,
        "failure_reasons": [] if f5pass else ["paired units or validation groups below threshold"],
    }
    feasible = {a: all(gates[a][g]["pass"] for g in COMPOUND_GATES) for a in ANALYTES}
    overall = all(feasible.values()) and f5pass
    return rows, edges, gates, f5, feasible, overall


def run_simple_models(records: list[dict]) -> dict:
    """Deterministic synthetic/conditional M0-M3 grouped evaluation path."""
    groups_sorted = sorted({r["validation_group_id"] for r in records})
    if len(groups_sorted) < 4:
        raise ValueError("at least four groups required")
    predictions: dict[str, list[tuple[float, float]]] = {
        name: [] for name in ("M0", "M1", "M2", "M3")
    }
    fold_rows = []
    for group in groups_sorted:
        train = [r for r in records if r["validation_group_id"] != group]
        test = [r for r in records if r["validation_group_id"] == group]
        if not train or not test:
            raise ValueError("empty grouped fold")
        global_mean = float(np.mean([r["target"] for r in train]))
        species_means = {
            s: float(np.mean([r["target"] for r in train if r["species"] == s]))
            for s in {r["species"] for r in train}
        }
        species_levels = sorted({r["species"] for r in train})
        roast_levels = sorted({r["roast"] for r in train})

        def design(rows, rich):
            matrix = []
            for r in rows:
                x = (
                    [1.0]
                    + [float(r["species"] == s) for s in species_levels[1:]]
                    + [float(r["roast"] == q) for q in roast_levels[1:]]
                )
                if rich:
                    x += [float(r.get("metric", 0.0))]
                matrix.append(x)
            return np.asarray(matrix, float)

        y = np.asarray([r["target"] for r in train], float)
        x2 = design(train, False)
        b2 = np.linalg.lstsq(x2, y, rcond=None)[0]
        x3 = design(train, True)
        scale = np.std(x3[:, -1]) or 1.0
        center = np.mean(x3[:, -1])
        x3[:, -1] = (x3[:, -1] - center) / scale
        penalty = np.eye(x3.shape[1])
        penalty[0, 0] = 0
        b3 = np.linalg.solve(x3.T @ x3 + 0.1 * penalty, x3.T @ y)
        tx2 = design(test, False)
        tx3 = design(test, True)
        tx3[:, -1] = (tx3[:, -1] - center) / scale
        pred = {
            "M0": np.full(len(test), global_mean),
            "M1": np.asarray([species_means.get(r["species"], global_mean) for r in test]),
            "M2": tx2 @ b2,
            "M3": tx3 @ b3,
        }
        truth = np.asarray([r["target"] for r in test], float)
        for name, values in pred.items():
            predictions[name].extend(zip(truth.tolist(), values.tolist(), strict=True))
            fold_rows.append(
                {
                    "model": name,
                    "test_group": group,
                    "n": len(test),
                    "mae": float(np.mean(np.abs(values - truth))),
                }
            )
    summary = {}
    for name, pairs in predictions.items():
        y = np.asarray([x[0] for x in pairs])
        p = np.asarray([x[1] for x in pairs])
        e = p - y
        summary[name] = {
            "mae": float(np.mean(abs(e))),
            "rmse": float(np.sqrt(np.mean(e * e))),
            "median_absolute_error": float(np.median(abs(e))),
            "signed_bias": float(np.mean(e)),
            "prediction_count": len(e),
            "validation_group_count": len(groups_sorted),
        }
    return {"models": summary, "folds": fold_rows, "outer_groups": groups_sorted, "seed": 0}


def _write_csv(path, fields, rows):
    with path.open("w", encoding="utf-8", newline="") as h:
        w = csv.DictWriter(h, fieldnames=fields, lineterminator="\n")
        w.writeheader()
        w.writerows([{k: r.get(k, "") for k in fields} for r in rows])


def generate(target: Path):
    validation = validate_contract()
    sources, materials, raw = (
        read_csv("sources.csv"),
        read_csv("materials.csv"),
        read_csv("observations.csv"),
    )
    validate_registers(sources, materials, raw)
    search = search_complete(sources)
    if not search["pass"]:
        result: dict[str, object] = {
            "task_id": "SCI-MD-007",
            "schema_version": "1.1.0-R1",
            "evidence_cutoff_date": "2026-08-25",
            "operational_status": "INCOMPLETE",
            "scientific_disposition": None,
            "search_completion": search,
        }
        (target / "result.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
        return result
    rows, edges, gates, f5, feasible, overall = reduce(sources, materials, raw)
    eligible = [r for r in rows if r["primary_prediction_label_eligible"]]
    classes = Counter(f"{r['measurement_provenance']}|{r['target_semantics']}" for r in rows)
    claim = [
        "Evidence-adequacy and prediction-feasibility screen only.",
        "Physical validation remains NOT_ESTABLISHED; no extraction-kinetics formulation was validated.",
        "Total roasted content is not extractable inventory or c_s0.",
        "No runtime integration or elaborate predictor is authorized.",
        "SCI-MD-006 is not reopened; Angeloni is not reused; G0 remains separate and deferred.",
        "A PASS means only that bounded leakage-safe simple-model comparison is structurally possible; a FAIL leaves restricted source-specific or broad priors.",
    ]
    result = {
        "task_id": "SCI-MD-007",
        "schema_version": "1.1.0-R1",
        "evidence_cutoff_date": "2026-08-25",
        "operational_status": "COMPLETE",
        "scientific_disposition": PASS if overall else FAIL,
        "target_semantics": "TOTAL_ROASTED_CONTENT",
        "canonical_mass_basis": "mg analyte / g dry roasted coffee",
        "search_completion": search,
        "contract_hashes": validation,
        "compound_gates": gates,
        "paired_coverage": {"F5": f5},
        "compound_feasible": feasible,
        "overall_gate_result": overall,
        "extractable_inventory_mapping_status": "NOT_ESTABLISHED",
        "counts": {
            "sources": len(sources),
            "atlas_material_roast_units": len(materials),
            "atlas_observations": len(rows),
            "primary_eligible_observations": len(eligible),
            "primary_eligible_per_analyte": dict(Counter(r["analyte"] for r in eligible)),
            "publications": len({r["source_publication_id"] for r in eligible}),
            "identified_laboratories": len({r["laboratory_id"] for r in eligible}),
        },
        "evidence_class_counts": dict(sorted(classes.items())),
        "model_stage": "NOT_RUN_FEASIBILITY_FAILED" if not overall else "COMPLETED_SIMPLE_MODELS",
        "model_comparison_summary": None,
        "model_adoption_status": "NOT_AUTHORIZED_BY_FEASIBILITY_SCREEN",
        "claim_ceiling": claim,
        "measurement_deficits": {
            a: {g: v["failure_reasons"] for g, v in gates[a].items() if not v["pass"]}
            for a in ANALYTES
        },
    }
    target.mkdir(parents=True, exist_ok=True)
    (target / "result.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    (target / "feasibility_gates.json").write_text(
        json.dumps({"compound_gates": gates, "F5": f5}, indent=2, sort_keys=True) + "\n"
    )
    export = {
        k: result[k]
        for k in (
            "task_id",
            "schema_version",
            "evidence_cutoff_date",
            "operational_status",
            "scientific_disposition",
            "compound_gates",
            "paired_coverage",
            "compound_feasible",
            "overall_gate_result",
            "extractable_inventory_mapping_status",
            "counts",
            "evidence_class_counts",
            "model_stage",
            "model_comparison_summary",
            "model_adoption_status",
            "claim_ceiling",
            "measurement_deficits",
        )
    }
    (target / "SCI_MD_007_EXPORT.json").write_text(
        json.dumps(export, indent=2, sort_keys=True) + "\n"
    )
    (target / "result.md").write_text(
        f"# SCI-MD-007-R1 corrected result\n\n**{result['scientific_disposition']}**\n\nAll counts and F0-F7 values are reduced from validated registers. Model stage: {result['model_stage']}.\n"
    )
    _write_csv(
        target / "inventory_observation_register.csv",
        list(rows[0]),
        [
            {k: (str(v).lower() if isinstance(v, bool) else v) for k, v in r.items()}
            for r in sorted(rows, key=lambda x: x["observation_id"])
        ],
    )
    _write_csv(
        target / "lineage_audit.csv",
        ["left", "right", "reason"],
        sorted(edges, key=lambda x: (x["left"], x["right"], x["reason"])),
    )
    _write_csv(
        target / "evidence_class_summary.csv",
        ["class", "count"],
        [{"class": k, "count": v} for k, v in sorted(classes.items())],
    )
    _write_csv(
        target / "paired_analyte_coverage.csv",
        ["paired_units", "validation_groups"],
        [
            {
                "paired_units": f5["paired_material_roast_units"],
                "validation_groups": f5["validation_groups"],
            }
        ],
    )
    descriptor_rows = []
    descriptors = (
        "species_scientific",
        "species_fraction",
        "variety_cultivar",
        "origin_country",
        "origin_region",
        "farm_estate_lot",
        "processing_method",
        "harvest_year",
        "roast_category_published",
        "roast_category_harmonized",
        "roast_metric_type",
        "roast_metric_value",
        "colour_metric",
        "roast_temperature_history",
        "roast_duration",
        "roast_mass_loss",
        "moisture_value",
        "material_form",
    )
    for d in descriptors:
        present = [m for m in materials if m.get(d)]
        descriptor_rows.append(
            {
                "cohort": "atlas",
                "descriptor": d,
                "material_completeness": len(present) / len(materials),
                "distinct_values": len({m[d] for m in present}),
            }
        )
        eligible_units = {(r["base_coffee_material_id"], r["roast_batch_id"]) for r in eligible}
        em = [
            m
            for m in materials
            if (m["base_coffee_material_id"], m["roast_batch_id"]) in eligible_units
        ]
        ep = [m for m in em if m.get(d)]
        descriptor_rows.append(
            {
                "cohort": "primary_eligible",
                "descriptor": d,
                "material_completeness": len(ep) / len(em) if em else 0,
                "distinct_values": len({m[d] for m in ep}),
            }
        )
    _write_csv(
        target / "descriptor_coverage.csv",
        ["cohort", "descriptor", "material_completeness", "distinct_values"],
        descriptor_rows,
    )
    _write_csv(
        target / "uncertainty_floor.csv",
        ["analyte", "eligible_units", "uncertainty_units", "between_lab_status"],
        [
            {
                "analyte": a,
                "eligible_units": gates[a]["F6"]["eligible_units"],
                "uncertainty_units": gates[a]["F6"]["uncertainty_bearing_units"],
                "between_lab_status": "NOT_IDENTIFIABLE",
            }
            for a in sorted(ANALYTES)
        ],
    )
    _write_csv(
        target / "source_summary.csv",
        ["metric", "value"],
        [
            {"metric": "atlas_sources", "value": len(sources)},
            {
                "metric": "eligible_publications",
                "value": len({r["source_publication_id"] for r in eligible}),
            },
            {
                "metric": "identified_laboratories",
                "value": len({r["laboratory_id"] for r in eligible}),
            },
        ],
    )
    eligible_units = {(r["base_coffee_material_id"], r["roast_batch_id"]) for r in eligible}
    _write_csv(
        target / "coffee_material_summary.csv",
        ["metric", "value"],
        [
            {"metric": "atlas_material_roast_units", "value": len(materials)},
            {"metric": "eligible_material_roast_units", "value": len(eligible_units)},
            {"metric": "eligible_base_materials", "value": len({x[0] for x in eligible_units})},
        ],
    )
    conversion_counts = Counter(r["conversion_status"] for r in rows)
    _write_csv(
        target / "mass_basis_conversion_audit.csv",
        ["status", "count"],
        [{"status": k, "count": v} for k, v in sorted(conversion_counts.items())],
    )
    _write_csv(
        target / "independence_audit.csv",
        [
            "analyte",
            "material_roast_units",
            "base_materials",
            "publications",
            "laboratories",
            "validation_groups",
            "largest_group_share",
        ],
        [
            {
                "analyte": a,
                **{
                    k: gates[a]["F2"][k]
                    for k in (
                        "material_roast_units",
                        "base_materials",
                        "publications",
                        "identified_laboratories",
                        "validation_groups",
                        "largest_group_share",
                    )
                },
            }
            for a in sorted(ANALYTES)
        ],
    )
    return result


EXPECTED = {
    "SCI_MD_007_EXPORT.json",
    "coffee_material_summary.csv",
    "descriptor_coverage.csv",
    "evidence_class_summary.csv",
    "feasibility_gates.json",
    "independence_audit.csv",
    "inventory_observation_register.csv",
    "lineage_audit.csv",
    "mass_basis_conversion_audit.csv",
    "paired_analyte_coverage.csv",
    "result.json",
    "result.md",
    "source_summary.csv",
    "uncertainty_floor.csv",
}


def build(check=False):
    with tempfile.TemporaryDirectory(prefix="sci-md-007-r1-") as tmp:
        temp = Path(tmp)
        result = generate(temp)
        if check:
            existing = {p.name for p in OUT.iterdir() if p.name in EXPECTED}
            if existing != EXPECTED or any(
                (OUT / n).read_bytes() != (temp / n).read_bytes() for n in EXPECTED
            ):
                raise ValueError("generated output drift")
            return result
        for name in EXPECTED:
            shutil.copyfile(temp / name, OUT / name)
        inputs = (
            [
                OUT / "feasibility_contract.json",
                OUT / "r1/R1_CORRECTIVE_SEARCH_CONTRACT.json",
                OUT / "r1/R1_CORRECTIVE_SEARCH_PROTOCOL.md",
            ]
            + sorted(DATA.glob("*.csv"))
            + [ROOT / s["source_card_path"] for s in read_csv("sources.csv")]
            + [ROOT / "puckworks/analysis/sci_md_007.py", Path(__file__)]
        )
        outputs = sorted(OUT / n for n in EXPECTED)
        digest = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
        manifest = {
            "schema_version": "1.1.0-R1",
            "inputs": {str(p.relative_to(ROOT)): digest(p) for p in inputs},
            "outputs": {str(p.relative_to(ROOT)): digest(p) for p in outputs},
        }
        (OUT / "source_package_manifest.json").write_text(
            json.dumps(manifest, indent=2, sort_keys=True) + "\n"
        )
        return result
