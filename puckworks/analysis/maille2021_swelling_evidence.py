"""Small, offline graphical invariant calculation; no physical growth estimator.

Inputs are manually retained poster markers, never raw instrument measurements.
Exact rational arithmetic decides intersections; decimal displays round outward.
"""
from __future__ import annotations

import argparse
import csv
from decimal import Decimal, ROUND_CEILING, ROUND_FLOOR, localcontext
from fractions import Fraction as F
from itertools import product
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
INPUT = ROOT / "puckworks/data/maille2021/swelling_evidence_001"
OUTPUT = ROOT / "docs/analysis/sci_md_maille_swelling_evidence_001"
TASK = "SCI-MD-MAILLE-SWELLING-EVIDENCE-001"
EXCLUDED = "CONDITIONAL_EXCLUSION_ON_RETAINED_SUPPORT"
NOT_EXCLUDED = "NOT_EXCLUDED_BY_OUTER_RELAXATION"
INSUFFICIENT = "INSUFFICIENT_SUPPORTED_OBSERVATIONS"


def linear_bounds(pixel, axis, reading, anchor):
    """Corner enclosure of an affine calibration with ordered, separated anchors.

The denominator has fixed sign. For each coordinate separately this linear-
fractional expression is monotone or constant, so its extrema occur at corners.
Shared anchors are relaxed across readings, not treated as independent errors.
"""
    p, r, e = F(pixel), F(reading), F(anchor)
    a, b = map(F, axis["pixels"])
    va, vb = map(F, axis["values"])
    if r < 0 or e < 0 or abs(b - a) <= 2 * e:
        raise ValueError("Invalid graphical allowance or crossing calibration anchors")
    values = [va + (pp - aa) * (vb - va) / (bb - aa)
              for pp, aa, bb in product((p-r, p+r), (a-e, a+e), (b-e, b+e))]
    return min(values), max(values)


def invariant_bounds(numerator, denominator, power=1):
    """Positive interval quotient; missing/nonpositive inputs do not qualify."""
    if numerator is None or denominator is None:
        return None
    lo, hi = map(F, numerator)
    dl, dh = map(F, denominator)
    if not (0 < lo <= hi and 0 < dl <= dh) or power not in (1, 3):
        return None
    return lo / dh**power, hi / dl**power


def intersection(rows):
    """Necessary constant-invariant intervals, with a two-observation certificate."""
    valid = [(oid, bounds) for oid, bounds in rows if bounds is not None]
    if len(valid) < 2:
        return dict(status=INSUFFICIENT, supported=len(valid), required=len(rows),
                    intersection=None, certificate=None)
    lower_id, lower = max(valid, key=lambda row: row[1][0])
    upper_id, upper = min(valid, key=lambda row: row[1][1])
    excluded = lower[0] > upper[1]
    return dict(status=EXCLUDED if excluded else NOT_EXCLUDED,
                supported=len(valid), required=len(rows),
                intersection=None if excluded else (lower[0], upper[1]),
                limiting_lower_observation=lower_id,
                limiting_upper_observation=upper_id,
                certificate=dict(lower_observation=lower_id, lower_interval=lower,
                                 upper_observation=upper_id, upper_interval=upper,
                                 strict_gap=lower[0]-upper[1]) if excluded else None)


def display(value, upper=False):
    with localcontext() as ctx:
        ctx.prec = 60
        ctx.rounding = ROUND_CEILING if upper else ROUND_FLOOR
        v = Decimal(value.numerator) / Decimal(value.denominator)
        return str(v.quantize(Decimal("0.000001")))


def pack(bounds):
    if bounds is None:
        return None
    return {"exact": [str(x) for x in bounds],
            "outward_decimal": [display(bounds[0]), display(bounds[1], True)]}


def encode(value):
    if isinstance(value, F):
        return str(value)
    if isinstance(value, tuple) and len(value) == 2:
        return pack(value)
    if isinstance(value, dict):
        return {k: encode(v) for k, v in value.items()}
    if isinstance(value, list):
        return [encode(v) for v in value]
    return value


def analyze(input_dir=INPUT):
    contract = json.loads((input_dir / "contract.json").read_text())
    with (input_dir / "coordinates.csv").open(newline="") as file:
        coordinates = list(csv.DictReader(file))
    groups = {}
    reading_ids = set()
    for row in coordinates:
        if row["reading_id"] in reading_ids:
            raise ValueError("Duplicate reading ID")
        reading_ids.add(row["reading_id"])
        group = groups.setdefault(row["observation_id"], {})
        if row["series_id"] in group:
            raise ValueError("Duplicate series at observation")
        group[row["series_id"]] = row
    observations = []
    for oid, group in groups.items():
        bounds, times = {}, []
        for series, row in group.items():
            bounds[series] = None
            if row["status"] != "SUPPORTED":
                continue
            axis = contract["axes"][contract["series"][series]["axis"]]
            bounds[series] = linear_bounds(row["y_px"], axis,
                                          contract["reading_allowance_px"],
                                          contract["anchor_allowance_px"])
            times.append(linear_bounds(row["x_px"], contract["axes"]["time_s"],
                                       contract["reading_allowance_px"],
                                       contract["anchor_allowance_px"]))
        # Pairing is declared by source reading, and must admit a common plotted time.
        time = (max(t[0] for t in times), min(t[1] for t in times)) if times else None
        paired = time is not None and time[0] <= time[1]
        x50, x90, conc = [bounds.get(key) for key in ("x50", "x90", "C_V")]
        metres = tuple(x / 10**6 for x in x50) if x50 else None
        fraction = tuple(x / 100 for x in conc) if conc else None
        observations.append(dict(
            observation_id=oid, time_s=time if paired else None,
            x50_um=x50, x90_um=x90, C_vol_percent=conc,
            x50_m=metres, C_volume_fraction=fraction,
            R=invariant_bounds(x90, x50) if paired else None,
            K_m_minus3=invariant_bounds(fraction, metres, 3) if paired else None,
            reading_ids=[row["reading_id"] for row in group.values()],
            reason="GRAPHICAL_TIME_PAIRING" if paired else "TIME_PAIRING_UNRESOLVED"))
    results = {key: intersection([(o["observation_id"], o[key]) for o in observations])
               for key in ("R", "K_m_minus3")}
    statuses = [r["status"] for r in results.values()]
    disposition = (EXCLUDED if EXCLUDED in statuses else
                   NOT_EXCLUDED if all(s == NOT_EXCLUDED for s in statuses) else INSUFFICIENT)
    return {"task": TASK,
            "base_sha": "4f378aa6757e9d61c4231d078aa4e7718736a394",
            "ewp_read_only_sha": "f44c33dbb9b4fb80143e360e6f4a90f8ac0aa516",
            "scope": ["G1", "NO_GOVERNING_PHYSICS_CHANGE", "RESEARCH_ONLY",
                      "RETROSPECTIVE", "TARGET_EXPOSED", "NONSCORING"],
            "source_access": json.loads((input_dir / "sources.json").read_text()),
            "quantitative_coverage": {
                "native_marker_rows": len(coordinates), "time_groups": len(observations),
                "qualified_R": results["R"]["supported"],
                "qualified_K": results["K_m_minus3"]["supported"],
                "coverage_scope": "all interpreted left-panel markers; not a complete raw history",
                "right_panel": "unpooled depiction only; ambiguous cluster retained",
                "original_numerical_records": "NOT_LOCATED_IN_BOUNDED_SEARCH",
                "published_numerical_growth_summaries": "NOT_RECOVERED",
                "quantitative_microscopy": "NOT_ADMITTED_BOUNDARY_AND_MAPPING_UNRESOLVED"},
            "graphical_representation_result": {
                "hypothesis": "H_FIXED_SCALE", "status": disposition,
                "measurement_map_condition": contract["measurement_map_condition"],
                "invariants": results,
                "uncertainty_scope": "graphical outer relaxation only; no experimental-error authority",
                "physical_observation_mapping": "OBSERVATION_MAPPING_UNRESOLVED"},
            "geometric_growth_bound": {
                "value": None, "status": "NOT_IDENTIFIABLE",
                "reason": "LD population/optical mappings unresolved; microscopy coffee edges obscured by bubbles and unbounded projection/focus changes; no calibrated detection limit.",
                "microscopy_baseline_s": 18, "microscopy_last_frame_s": 283,
                "dry_to_wet_bound": None, "equilibrium_bound": None,
                "population_maximum_bound": None},
            "entrainment_attribution": {
                "source_report": "floating large particles enter recirculating flow later",
                "quantitative_fraction": None, "rate": None,
                "status": "QUALITATIVE_SOURCE_EVIDENCE; CONTRIBUTIONS_CONFOUNDED",
                "corrected_trace_recovered": False},
            "hargarten_comparability": {
                "status": "DIFFERING_PUBLISHED_CONCLUSIONS",
                "actual_quantitative_contradiction": "NOT_ESTABLISHED",
                "table": "COMPARISON.md"},
            "mo_parameter_implications": {
                "s_max_percent_equation": "100*((1-C_M)**(-1/3)-1)",
                "s_max_percent_at_C_M_0_1_approx": 3.5744,
                "meaning": "model-implied equilibrium diameter/radius expansion, not empirical estimate",
                "C_M_bound": None, "D_W_bound": None, "kinetic_timescale": None,
                "dry_to_wet_growth": None, "finite_window_projected_growth": None,
                "temperature_or_water_chemistry_dependence": None,
                "observation_mapping": "must allow departures from excluded fixed-population/common-scale conjunction on retained support" if disposition == EXCLUDED else "no identified geometric mapping",
                "parameters_fitted": 0, "Mo_solver_runs": 0},
            "physical_validation": "NOT_ESTABLISHED",
            "observations": observations}


def write(result, output):
    output.mkdir(parents=True, exist_ok=True)
    encoded = encode(result)
    (output / "RESULT.json").write_text(json.dumps(encoded, indent=2) + "\n")
    rows = []
    for observation in result["observations"]:
        row = {"observation_id": observation["observation_id"]}
        for key in ("time_s", "x50_um", "x90_um", "C_vol_percent", "R", "K_m_minus3"):
            bounds = observation[key]
            row[key + "_low"] = display(bounds[0]) if bounds else ""
            row[key + "_high"] = display(bounds[1], True) if bounds else ""
        rows.append(row)
    with (output / "intervals.csv").open("w", newline="") as file:
        writer = csv.DictWriter(file, rows[0], lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def plot(result, output):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from puckworks.public.schema import Producer
    from puckworks.viz.spec import VizSpec
    spec = VizSpec(id="maille_swelling_evidence_001", title="Maille graphical invariants",
                   class_=1, producer=Producer(module=__name__, function="analyze",
                                              result_map={"observations": "observations"}),
                   badge="OBSERVED", evidence_strength="reference", components=[],
                   fidelity_ceiling="Conditional graphical outer enclosures; no physical growth bound.",
                   render_fn=__name__ + ":plot", outputs=["comparison.svg"], used_in=TASK,
                   caption="Sala, Maille, Scott, Zukswert, ASIC2021 S8-PO-01 Fig4. Factual readings; source artwork external. Allowances are not experimental error bars.")
    if spec.validate():
        raise ValueError(spec.validate())
    with matplotlib.rc_context({"svg.hashsalt": TASK, "font.size": 10}):
        fig, axes = plt.subplots(1, 2, figsize=(10, 5), sharey=True)
        for ax, key, label, factor in zip(
                axes, ("R", "K_m_minus3"), ("x90 / x50", "C_V / x50³ (10⁶ m⁻³)"), (1, 1e6)):
            for i, row in enumerate(result["observations"]):
                bounds = row[key]
                if bounds:
                    ax.plot([float(v) / factor for v in bounds], [i, i], "o-", color="#285f82")
            intersection_ = result["graphical_representation_result"]["invariants"][key]
            if intersection_["intersection"]:
                lo, hi = intersection_["intersection"]
                ax.axvspan(float(lo)/factor, float(hi)/factor, color="#b5c7ae", alpha=.5)
            ax.set_xlabel(label)
            ax.set_title("Necessary-only overlap" if intersection_["status"] == NOT_EXCLUDED
                         else "Empty common intersection")
            ax.grid(axis="x", alpha=.2)
        labels = [f"O{i+1:02} (~{sum(map(float,r['time_s']))/2:.0f} s)"
                  for i, r in enumerate(result["observations"])]
        axes[0].set(yticks=range(len(labels)), yticklabels=labels)
        axes[0].invert_yaxis()
        fig.suptitle("Maille: fixed-population/common-scaling necessary invariants")
        fig.text(.5, .02, "Graphical outer bounds only • no laboratory uncertainty or physical growth bound",
                 ha="center", fontsize=9)
        fig.tight_layout(rect=(0, .05, 1, .94))
        fig.savefig(output / "comparison.svg", metadata={"Date": None, "Creator": TASK})
        plt.close(fig)
        svg = output / "comparison.svg"
        svg.write_text("\n".join(line.rstrip() for line in svg.read_text().splitlines()) + "\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--plot", action="store_true")
    args = parser.parse_args()
    result = analyze()
    write(result, args.output)
    if args.plot:
        plot(result, args.output)
    print(result["graphical_representation_result"]["status"])


if __name__ == "__main__":
    main()
