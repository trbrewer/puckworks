"""Authoritative R2 evidence-package validator, reducer, and generator."""

from __future__ import annotations

import csv
import hashlib
import json
import math
import re
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
REQUIRED_SPECIES = {"Arabica": "Coffea arabica", "Robusta": "Coffea canephora"}
UNKNOWN_LABS = {"", "unknown", "unspecified", "not_reported", "not reported"}


def identified_laboratory(value: str) -> bool:
    return value.strip().lower() not in UNKNOWN_LABS and "unknown" not in value.lower()


def normalize_doi(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"^https?://(?:dx\.)?doi\.org/", "", value)
    value = re.sub(r"^doi:\s*", "", value)
    return value.strip().rstrip(".,") if value.startswith("10.") else ""


def normalize_text(value: str) -> str:
    return " ".join(re.sub(r"[^a-z0-9]+", " ", value.lower()).split())


def bibliographic_identity(row: dict[str, str]) -> tuple[str, ...]:
    doi = normalize_doi(row.get("doi_or_stable_id", ""))
    if doi:
        return ("doi", doi)
    stable = row.get("doi_or_stable_id", "").strip().lower()
    if stable:
        return ("stable", stable)
    first_author = normalize_text(row.get("authors", "").split(";")[0])
    return (
        "fallback",
        normalize_text(row.get("title", "")),
        row.get("year", "").strip(),
        first_author,
    )


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


def expected_search_plan(contract: dict) -> dict[str, tuple[str, str]]:
    return {
        f"q{i:02d}_{provider.lower()}": (provider, query)
        for i, query in enumerate(contract["queries"], 1)
        for provider in contract["providers"]
    }


def _integer(value: str, field: str) -> int:
    if not re.fullmatch(r"0|[1-9][0-9]*", value or ""):
        raise ValueError(f"{field} must be a nonnegative integer")
    return int(value)


def resolve_candidate_roots(rows: list[dict[str, str]]) -> dict[str, str]:
    by_candidate: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        if not row["candidate_id"]:
            raise ValueError("blank candidate_id")
        by_candidate[row["candidate_id"]].append(row)
    roots: dict[str, str] = {}
    for candidate, occurrences in by_candidate.items():
        canonical = [r for r in occurrences if not r["duplicate_of"]]
        if len(canonical) != 1:
            raise ValueError(f"candidate lineage {candidate} has {len(canonical)} introductions")
        identities = {bibliographic_identity(r) for r in occurrences}
        identities.discard(("fallback", "", "", ""))
        if len(identities) > 1:
            raise ValueError(f"candidate lineage {candidate} joins different identities")
        roots[candidate] = candidate
    for row in rows:
        duplicate = row["duplicate_of"]
        if duplicate and duplicate not in by_candidate:
            raise ValueError(f"dangling duplicate_of: {duplicate}")
        if duplicate and duplicate != row["candidate_id"]:
            raise ValueError("duplicate occurrence does not resolve to its canonical lineage")
    identity_roots: dict[tuple[str, ...], str] = {}
    for candidate, occurrences in by_candidate.items():
        identity = bibliographic_identity(occurrences[0])
        if identity != ("fallback", "", "", ""):
            prior = identity_roots.setdefault(identity, candidate)
            if prior != candidate:
                raise ValueError("same normalized identity has multiple canonical roots")
    return roots


def search_complete(sources, *, data: Path = DATA) -> dict:
    def load(name):
        with (data / name).open(encoding="utf-8", newline="") as handle:
            return list(csv.DictReader(handle))

    logs, results, passes = (
        load("search_log.csv"),
        load("search_results.csv"),
        load("citation_passes.csv"),
    )
    r1 = json.loads((OUT / "r1/R1_CORRECTIVE_SEARCH_CONTRACT.json").read_text())
    plan = expected_search_plan(r1)
    cutoff = r1["evidence_cutoff_date"]
    allowed = set(r1["source_screening_states"])
    reasons: list[str] = []
    log_by: dict[str, dict[str, str]] = {}
    for row in logs:
        sid = row.get("search_id", "")
        if sid in log_by:
            reasons.append(f"duplicate search log: {sid}")
        log_by[sid] = row
    if set(log_by) != set(plan):
        reasons.append("contract-derived search plan mismatch")
    result_by: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in results:
        result_by[row.get("search_id", "")].append(row)
    numeric = (
        "result_limit",
        "results_returned",
        "results_screened",
        "unique_candidates_added",
        "duplicates",
        "inaccessible_candidates",
        "out_of_scope_candidates",
    )
    query_audit = []
    for sid, expected in sorted(plan.items()):
        row = log_by.get(sid)
        if not row:
            continue
        provider, query = expected
        if (row.get("provider"), row.get("query")) != expected:
            reasons.append(f"{sid}: provider/query mismatch")
        if not row.get("execution_date") or row["execution_date"] > cutoff:
            reasons.append(f"{sid}: invalid execution date")
        try:
            values = {key: _integer(row.get(key, ""), f"{sid}.{key}") for key in numeric}
        except ValueError as exc:
            reasons.append(str(exc))
            continue
        if values["result_limit"] != r1["result_limit_per_query_per_provider"]:
            reasons.append(f"{sid}: result limit mismatch")
        if values["results_returned"] > values["result_limit"]:
            reasons.append(f"{sid}: returned above limit")
        if values["results_screened"] != values["results_returned"]:
            reasons.append(f"{sid}: screened/returned mismatch")
        observed = result_by.get(sid, [])
        if len(observed) != values["results_returned"]:
            reasons.append(f"{sid}: result row count mismatch")
        ranks = []
        for item in observed:
            if (item.get("provider"), item.get("query")) != expected:
                reasons.append(f"{sid}: result provider/query mismatch")
            try:
                ranks.append(_integer(item.get("result_rank", ""), f"{sid}.result_rank"))
            except ValueError as exc:
                reasons.append(str(exc))
            if not item.get("retrieval_date") or item["retrieval_date"] > cutoff:
                reasons.append(f"{sid}: invalid retrieval date")
            if (
                item.get("screening_state") not in allowed
                or item.get("screening_state") == "UNRESOLVED_PENDING_SCREEN"
            ):
                reasons.append(f"{sid}: nonterminal screening state")
        if sorted(ranks) != list(range(1, len(observed) + 1)):
            reasons.append(f"{sid}: ranks not unique contiguous")
        derived = {
            "unique_candidates_added": sum(not x["duplicate_of"] for x in observed),
            "duplicates": sum(bool(x["duplicate_of"]) for x in observed),
            "inaccessible_candidates": sum(
                x["screening_state"] == "RIGHTS_OR_ACCESS_BLOCKED" for x in observed
            ),
            "out_of_scope_candidates": sum(
                x["screening_state"].startswith("OUT_OF_SCOPE_") for x in observed
            ),
        }
        if derived["unique_candidates_added"] + derived["duplicates"] != len(observed):
            reasons.append(f"{sid}: unique plus duplicate mismatch")
        for field, value in derived.items():
            if value != values[field]:
                reasons.append(f"{sid}: {field} mismatch")
        query_audit.append(
            {"search_id": sid, "provider": provider, "query": query, **values, **derived}
        )
    for sid in set(result_by) - set(plan):
        reasons.append(f"unexpected result search_id: {sid}")
    roots = {}
    try:
        roots = resolve_candidate_roots(results)
    except ValueError as exc:
        reasons.append(str(exc))
    citation_audit = []
    for source in sources:
        for direction in ("BACKWARD", "FORWARD"):
            selected = [
                row
                for row in passes
                if row.get("source_publication_id") == source["source_publication_id"]
                and row.get("direction") == direction
            ]
            ranks = []
            stable = []
            if not selected:
                reasons.append(f"{source['source_publication_id']} missing {direction} pass")
            zero_result = (
                len(selected) == 1
                and selected[0].get("rank") == "0"
                and selected[0].get("stable_id") == "NO_RESULTS_RETURNED"
                and selected[0].get("screening_state") == "SCREENED_NO_RESULTS"
            )
            for row in selected:
                try:
                    rank = _integer(row.get("rank", ""), "citation rank")
                    if rank == 0 and not zero_result:
                        raise ValueError("citation rank must be positive")
                    ranks.append(rank)
                except ValueError as exc:
                    reasons.append(str(exc))
                if not row.get("stable_id"):
                    reasons.append("blank citation stable ID")
                stable.append(row.get("stable_id", ""))
                if row.get("screening_state") not in {"SCREENED", "SCREENED_NO_RESULTS"}:
                    reasons.append("unterminated citation row")
                if not row.get("retrieval_date") or row["retrieval_date"] > cutoff:
                    reasons.append("invalid citation retrieval date")
            if len(selected) > 20 or any(rank > 20 for rank in ranks):
                reasons.append("citation pass exceeds frozen limit")
            if ranks and not zero_result and sorted(ranks) != list(range(1, len(selected) + 1)):
                reasons.append("citation ranks not unique contiguous")
            if len(stable) != len(set(stable)):
                reasons.append("duplicate citation stable ID")
            citation_audit.append(
                {
                    "source_publication_id": source["source_publication_id"],
                    "direction": direction,
                    "result_count": 0 if zero_result else len(selected),
                    "zero_result_sentinel": zero_result,
                    "complete": bool(selected) and not any(rank > 20 for rank in ranks),
                }
            )
    duplicate_count = sum(bool(r["duplicate_of"]) for r in results)
    unresolved = sum(
        not r["screening_state"] or r["screening_state"] == "UNRESOLVED_PENDING_SCREEN"
        for r in results
    )
    return {
        "pass": not reasons,
        "reasons": sorted(set(reasons)),
        "searches": len(logs),
        "result_records": len(results),
        "unique_candidates": len(roots),
        "duplicates": duplicate_count,
        "unresolved_candidates": unresolved,
        "inaccessible_candidates": sum(
            r["screening_state"] == "RIGHTS_OR_ACCESS_BLOCKED" for r in results
        ),
        "out_of_scope_candidates": sum(
            r["screening_state"].startswith("OUT_OF_SCOPE_") for r in results
        ),
        "citation_records": len(passes),
        "query_provider_audit": query_audit,
        "citation_pass_audit": citation_audit,
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
    unit_rows = {(r["base_coffee_material_id"], r["roast_batch_id"]): r for r in eligible}
    units = set(unit_rows)
    mids = {u[0] for u in units}
    pubs = {r["source_publication_id"] for r in eligible}
    labs = {r["laboratory_id"] for r in eligible if identified_laboratory(r["laboratory_id"])}
    groupset = {r["validation_group_id"] for r in eligible}
    counts = Counter(r["validation_group_id"] for r in unit_rows.values())
    largest = max(counts.values(), default=0) / len(units) if units else None
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
            "laboratories": len(
                {r["laboratory_id"] for r in sr if identified_laboratory(r["laboratory_id"])}
            ),
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
    strata = {label: defaultdict(set) for label in species}
    stratum_groups = {label: defaultdict(set) for label in species}
    for unit, row in unit_rows.items():
        material = material_by[unit]
        for label, scientific in species.items():
            category = material["roast_category_harmonized"]
            if material["species_scientific"] == scientific and category:
                strata[label][category].add(unit)
                stratum_groups[label][category].add(row["validation_group_id"])
    categorical_details, categorical_failures = {}, []
    for label in species:
        categories, qualifying = {}, []
        for category in sorted(strata[label]):
            unit_count = len(strata[label][category])
            group_count = len(stratum_groups[label][category])
            failures = []
            if unit_count < t4["categorical_units_per_stratum"]:
                failures.append("units_below_threshold")
            if group_count < t4["categorical_groups_per_stratum"]:
                failures.append("validation_groups_below_threshold")
            categories[category] = {
                "material_roast_units": unit_count,
                "validation_groups": group_count,
                "qualifies": not failures,
                "failure_reasons": failures,
            }
            if not failures:
                qualifying.append(category)
        passed = len(qualifying) >= t4["categorical_strata_per_species"]
        if not passed:
            categorical_failures.append(f"categorical_{label}_qualifying_strata_below_threshold")
        categorical_details[label] = {
            "categories": categories,
            "qualifying_strata": qualifying,
            "qualifying_strata_count": len(qualifying),
            "pass": passed,
        }
    categorical = all(item["pass"] for item in categorical_details.values())

    metric_units, invalid_metric_units = {}, []
    for unit, row in unit_rows.items():
        material = material_by[unit]
        metric_type = material["roast_metric_type"].strip()
        if not metric_type:
            continue
        try:
            value = float(material["roast_metric_value"])
        except ValueError:
            invalid_metric_units.append("|".join(unit))
            continue
        if not math.isfinite(value) or not material["roast_metric_units"].strip():
            invalid_metric_units.append("|".join(unit))
            continue
        metric_units[unit] = {
            "value": value,
            "metric_type": metric_type,
            "metric_units": material["roast_metric_units"],
            "species_scientific": material["species_scientific"],
            "validation_group_id": row["validation_group_id"],
        }
    metric_groups = {item["validation_group_id"] for item in metric_units.values()}
    per_species_units = {
        label: sum(item["species_scientific"] == scientific for item in metric_units.values())
        for label, scientific in species.items()
    }
    variation = {}
    for label, scientific in species.items():
        qualifying_ids, qualifying_details = [], []
        for group in sorted(metric_groups):
            by_type = defaultdict(dict)
            for unit, item in metric_units.items():
                if (
                    item["species_scientific"] == scientific
                    and item["validation_group_id"] == group
                ):
                    by_type[item["metric_type"]][unit] = item["value"]
            qualifying_types = []
            for metric_type, values in sorted(by_type.items()):
                if len(values) >= 2 and len(set(values.values())) >= 2:
                    qualifying_types.append(
                        {
                            "metric_type": metric_type,
                            "unit_ids": ["|".join(unit) for unit in sorted(values)],
                            "distinct_values": sorted(set(values.values())),
                        }
                    )
            if qualifying_types:
                qualifying_ids.append(group)
                qualifying_details.append(
                    {"validation_group_id": group, "qualifying_metric_types": qualifying_types}
                )
        variation[label] = {
            "qualifying_validation_group_ids": qualifying_ids,
            "qualifying_groups": qualifying_details,
            "count": len(qualifying_ids),
            "threshold": t4["within_species_varying_groups"],
            "pass": len(qualifying_ids) >= t4["within_species_varying_groups"],
        }
    quantitative_checks = {
        "total_units": len(metric_units) >= t4["quantitative_metric_units"],
        "validation_groups": len(metric_groups) >= t4["quantitative_metric_groups"],
        "units_per_species": all(
            count >= t4["quantitative_metric_units_per_species"]
            for count in per_species_units.values()
        ),
        "within_species_varying_groups": all(item["pass"] for item in variation.values()),
    }
    quantitative = all(quantitative_checks.values())
    quantitative_failures = [
        f"quantitative_{key}_failed" for key, passed in quantitative_checks.items() if not passed
    ]
    f4 = {
        "pass": categorical or quantitative,
        "categorical_route": {
            "pass": categorical,
            "species": categorical_details,
            "failure_reasons": categorical_failures,
        },
        "quantitative_route": {
            "pass": quantitative,
            "material_roast_units": len(metric_units),
            "validation_groups": len(metric_groups),
            "units_per_species": per_species_units,
            "within_species_varying_groups": variation,
            "minimum_within_species_varying_groups": min(
                (item["count"] for item in variation.values()), default=0
            ),
            "invalid_metric_unit_ids": invalid_metric_units,
            "primitive_pass": quantitative_checks,
            "failure_reasons": quantitative_failures,
        },
        "thresholds": t4,
        "failure_reasons": (
            []
            if categorical or quantitative
            else ["neither_roast_route_qualifies", *categorical_failures, *quantitative_failures]
        ),
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
    folds, transport_rows = [], []
    leakage_ids = {"publication": set(), "data_lineage": set(), "base_material": set()}
    species_all = category_all = metric_all = True
    for group in sorted(groupset):
        test = [row for row in unit_rows.values() if row["validation_group_id"] == group]
        train = [row for row in unit_rows.values() if row["validation_group_id"] != group]
        intersections = {
            "publication": sorted(
                {row["source_publication_id"] for row in test}
                & {row["source_publication_id"] for row in train}
            ),
            "data_lineage": sorted(
                {row["data_lineage_id"] for row in test} & {row["data_lineage_id"] for row in train}
            ),
            "base_material": sorted(
                {row["base_coffee_material_id"] for row in test}
                & {row["base_coffee_material_id"] for row in train}
            ),
        }
        for key, values in intersections.items():
            leakage_ids[key].update(values)
        train_species = {
            material_by[(row["base_coffee_material_id"], row["roast_batch_id"])][
                "species_scientific"
            ]
            for row in train
        }
        test_species = {
            material_by[(row["base_coffee_material_id"], row["roast_batch_id"])][
                "species_scientific"
            ]
            for row in test
        }
        unsupported_species = sorted(test_species - train_species)
        species_all &= not unsupported_species
        for row in test:
            unit = (row["base_coffee_material_id"], row["roast_batch_id"])
            material = material_by[unit]
            species_name = material["species_scientific"]
            category = material["roast_category_harmonized"]
            metric_type = material["roast_metric_type"]
            category_supported = not category or any(
                material_by[(candidate["base_coffee_material_id"], candidate["roast_batch_id"])][
                    "species_scientific"
                ]
                == species_name
                and material_by[
                    (candidate["base_coffee_material_id"], candidate["roast_batch_id"])
                ]["roast_category_harmonized"]
                == category
                for candidate in train
            )
            metric_supported = not metric_type or any(
                material_by[(candidate["base_coffee_material_id"], candidate["roast_batch_id"])][
                    "species_scientific"
                ]
                == species_name
                and material_by[
                    (candidate["base_coffee_material_id"], candidate["roast_batch_id"])
                ]["roast_metric_type"]
                == metric_type
                for candidate in train
            )
            category_all &= category_supported
            metric_all &= metric_supported
            transport_rows.append(
                {
                    "analyte": analyte,
                    "test_group": group,
                    "base_coffee_material_id": unit[0],
                    "roast_batch_id": unit[1],
                    "species": species_name,
                    "species_supported": species_name in train_species,
                    "harmonized_roast_category": category,
                    "harmonized_roast_category_supported": category_supported,
                    "roast_metric_type": metric_type,
                    "quantitative_metric_type_supported": metric_supported,
                }
            )
        folds.append(
            {
                "test_group": group,
                "training_groups": sorted(groupset - {group}),
                "test_species": sorted(test_species),
                "training_species": sorted(train_species),
                "unsupported_test_species": unsupported_species,
                "publication_intersection_ids": intersections["publication"],
                "data_lineage_intersection_ids": intersections["data_lineage"],
                "base_material_intersection_ids": intersections["base_material"],
            }
        )
    leakage_counts = {key: len(values) for key, values in leakage_ids.items()}
    f7pass = len(groupset) >= threshold["F7"]["outer_validation_groups"] and not any(
        leakage_counts.values()
    )
    f7_failures = []
    if len(groupset) < threshold["F7"]["outer_validation_groups"]:
        f7_failures.append("outer_validation_groups_below_threshold")
    for key, count in leakage_counts.items():
        if count:
            f7_failures.append(f"{key}_leakage_detected")
    f7 = {
        "pass": f7pass,
        "outer_validation_groups": len(groupset),
        "publication_leakage": leakage_counts["publication"],
        "data_lineage_leakage": leakage_counts["data_lineage"],
        "base_material_leakage": leakage_counts["base_material"],
        "publication_leakage_ids": sorted(leakage_ids["publication"]),
        "data_lineage_leakage_ids": sorted(leakage_ids["data_lineage"]),
        "base_material_leakage_ids": sorted(leakage_ids["base_material"]),
        "species_support_all_folds": species_all,
        "harmonized_roast_category_support_all_folds": category_all,
        "quantitative_metric_type_support_all_folds": metric_all,
        "proposed_folds": folds,
        "transportability_rows": transport_rows,
        "thresholds": threshold["F7"],
        "failure_reasons": f7_failures,
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
            "schema_version": "1.2.0-R2",
            "evidence_cutoff_date": "2026-08-25",
            "operational_status": "INCOMPLETE",
            "scientific_disposition": None,
            "search_completion": search,
        }
        (target / "result.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
        return result
    rows, edges, gates, f5, feasible, overall = reduce(sources, materials, raw)
    transport_rows = [
        row
        for analyte in sorted(ANALYTES)
        for row in gates[analyte]["F7"].pop("transportability_rows")
    ]
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
        "schema_version": "1.2.0-R2",
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
            "identified_laboratories": len(
                {r["laboratory_id"] for r in eligible if identified_laboratory(r["laboratory_id"])}
            ),
        },
        "evidence_class_counts": dict(sorted(classes.items())),
        "model_stage": (
            "NOT_RUN_FEASIBILITY_FAILED"
            if not overall
            else "NOT_RUN_R2_CORRECTION_SCOPE_PENDING_OWNER_AUTHORIZATION"
        ),
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
        f"# SCI-MD-007-R2 corrected result\n\n**{result['scientific_disposition']}**\n\nAll counts and F0-F7 values are reduced from validated registers. Model stage: {result['model_stage']}.\n"
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
                "value": len(
                    {
                        r["laboratory_id"]
                        for r in eligible
                        if identified_laboratory(r["laboratory_id"])
                    }
                ),
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
                "material_roast_units": gates[a]["F2"]["material_roast_units"],
                "base_materials": gates[a]["F2"]["base_materials"],
                "publications": gates[a]["F2"]["publications"],
                "laboratories": gates[a]["F2"]["identified_laboratories"],
                "validation_groups": gates[a]["F2"]["validation_groups"],
                "largest_group_share": gates[a]["F2"]["largest_group_share"],
            }
            for a in sorted(ANALYTES)
        ],
    )
    r2 = target / "r2"
    r2.mkdir(parents=True, exist_ok=True)
    (r2 / "search_closure_audit.json").write_text(
        json.dumps(search, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    _write_csv(
        r2 / "citation_pass_summary.csv",
        [
            "source_publication_id",
            "direction",
            "result_count",
            "zero_result_sentinel",
            "complete",
        ],
        search["citation_pass_audit"],
    )
    _write_csv(
        r2 / "fold_transportability_audit.csv",
        [
            "analyte",
            "test_group",
            "base_coffee_material_id",
            "roast_batch_id",
            "species",
            "species_supported",
            "harmonized_roast_category",
            "harmonized_roast_category_supported",
            "roast_metric_type",
            "quantitative_metric_type_supported",
        ],
        transport_rows,
    )
    _write_csv(
        r2 / "R2_REGISTER_CORRECTIONS.csv",
        [
            "path",
            "row_identity",
            "field",
            "previous_value",
            "corrected_value",
            "deterministic_derivation",
            "reason",
            "scientific_content_impact",
            "authorizing_contract_field",
        ],
        [
            {
                "path": "NO_REGISTER_CORRECTIONS_REQUIRED",
                "row_identity": "NOT_APPLICABLE",
                "field": "NOT_APPLICABLE",
                "previous_value": "NOT_APPLICABLE",
                "corrected_value": "NOT_APPLICABLE",
                "deterministic_derivation": "Strengthened reducer closes existing rows without edits",
                "reason": "Existing zero-result citation sentinels are schema-valid",
                "scientific_content_impact": "NONE",
                "authorizing_contract_field": "input_mutation.allowed",
            }
        ],
    )
    source_summary = {
        row["metric"]: str(row["value"])
        for row in csv.DictReader((target / "source_summary.csv").open(newline=""))
    }
    independence = list(csv.DictReader((target / "independence_audit.csv").open(newline="")))
    comparisons = {
        "result_export_disposition": export["scientific_disposition"]
        == result["scientific_disposition"],
        "result_export_overall": export["overall_gate_result"] == result["overall_gate_result"],
        "evidence_classes_sum": sum(classes.values()) == len(rows),
        "eligible_observations": len(eligible)
        == sum(result["counts"]["primary_eligible_per_analyte"].values()),
        "paired_units": f5["paired_material_roast_units"]
        == int(
            next(csv.DictReader((target / "paired_analyte_coverage.csv").open()))["paired_units"]
        ),
        "search_totals": search["searches"] == 24
        and search["result_records"] == 400
        and search["unique_candidates"] == 269
        and search["duplicates"] == 131,
    }
    for row in independence:
        analyte = row["analyte"]
        comparisons[f"{analyte}_independence_laboratory_nonblank"] = bool(row["laboratories"])
        comparisons[f"{analyte}_independence_laboratory_equals_f2"] = (
            int(row["laboratories"]) == gates[analyte]["F2"]["identified_laboratories"]
        )
        comparisons[f"{analyte}_source_summary_laboratory_equals_f2"] = (
            int(source_summary["identified_laboratories"])
            == gates[analyte]["F2"]["identified_laboratories"]
        )
        comparisons[f"{analyte}_f4_export_result"] = (
            export["compound_gates"][analyte]["F4"] == result["compound_gates"][analyte]["F4"]
        )
        comparisons[f"{analyte}_f7_export_result"] = (
            export["compound_gates"][analyte]["F7"] == result["compound_gates"][analyte]["F7"]
        )
    required_csvs = [
        "independence_audit.csv",
        "source_summary.csv",
        "coffee_material_summary.csv",
        "paired_analyte_coverage.csv",
        "uncertainty_floor.csv",
        "evidence_class_summary.csv",
        "inventory_observation_register.csv",
    ]
    blank_violations = []
    for name in required_csvs:
        for index, row in enumerate(csv.DictReader((target / name).open(newline="")), 2):
            for field, value in row.items():
                if value == "" and name not in {"inventory_observation_register.csv"}:
                    blank_violations.append(f"{name}:{index}:{field}")
    comparisons["no_blank_required_summary_fields"] = not blank_violations
    if not all(comparisons.values()):
        raise ValueError("R2 cross-artifact semantic mismatch")
    cross_audit = {
        "schema_version": "1.2.0-R2",
        "status": "PASS",
        "comparisons": comparisons,
        "blank_violations": blank_violations,
        "manifest_closure": "VERIFIED_BY_BUILD_AFTER_MANIFEST_SERIALIZATION",
    }
    (r2 / "R2_CROSS_ARTIFACT_AUDIT.json").write_text(
        json.dumps(cross_audit, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (r2 / "R2_CORRECTION_REPORT.md").write_text(
        "# SCI-MD-007-R2 correction report\n\n"
        f"Search relational closure: {'PASS' if search['pass'] else 'FAIL'}. "
        f"Scientific disposition: `{result['scientific_disposition']}`. "
        "Laboratory identity is counted for F2/F3 independence but is not a validation-group edge. "
        "EWP verifies exact producer/package bytes and independently reduces exported Boolean gates; "
        "Puckworks remains authoritative for raw-register primitives.\n",
        encoding="utf-8",
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
    "r2/R2_CROSS_ARTIFACT_AUDIT.json",
    "r2/R2_CORRECTION_REPORT.md",
    "r2/R2_REGISTER_CORRECTIONS.csv",
    "r2/citation_pass_summary.csv",
    "r2/fold_transportability_audit.csv",
    "r2/search_closure_audit.json",
}


def build(check=False):
    with tempfile.TemporaryDirectory(prefix="sci-md-007-r2-") as tmp:
        temp = Path(tmp)
        result = generate(temp)
        if check:
            existing = {name for name in EXPECTED if (OUT / name).is_file()}
            if existing != EXPECTED or any(
                (OUT / n).read_bytes() != (temp / n).read_bytes() for n in EXPECTED
            ):
                raise ValueError("generated output drift")
            return result
        for name in EXPECTED:
            (OUT / name).parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(temp / name, OUT / name)
        inputs = (
            [
                OUT / "feasibility_contract.json",
                OUT / "r1/R1_CORRECTIVE_SEARCH_CONTRACT.json",
                OUT / "r1/R1_CORRECTIVE_SEARCH_PROTOCOL.md",
                OUT / "r2/R2_EVIDENCE_PACKAGE_CORRECTION_CONTRACT.json",
                OUT / "r2/R2_EVIDENCE_PACKAGE_CORRECTION_CONTRACT.md",
            ]
            + sorted(DATA.glob("*.csv"))
            + [ROOT / s["source_card_path"] for s in read_csv("sources.csv")]
            + [ROOT / "puckworks/analysis/sci_md_007.py", Path(__file__)]
        )
        outputs = sorted(OUT / n for n in EXPECTED)
        digest = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
        manifest = {
            "schema_version": "1.2.0-R2",
            "reducer_path": str(Path(__file__).relative_to(ROOT)),
            "reducer_sha256": digest(Path(__file__)),
            "r2_contract_sha256": digest(OUT / "r2/R2_EVIDENCE_PACKAGE_CORRECTION_CONTRACT.json"),
            "inputs": {str(p.relative_to(ROOT)): digest(p) for p in inputs},
            "outputs": {str(p.relative_to(ROOT)): digest(p) for p in outputs},
        }
        (OUT / "source_package_manifest.json").write_text(
            json.dumps(manifest, indent=2, sort_keys=True) + "\n"
        )
        return result
