"""Paper 1 numeral audit — every number in the manuscript body must be accounted for.

`paper_a.build.verify` checks 27 registered claims. The manuscript body contains roughly 560
numerals. That gap is invisible by construction: a number nobody registered is a number nobody
checks, and on the page it is indistinguishable from one that passed.

The same audit on Paper 2 took it from 150 unaccounted to zero and found three unbacked values on
the way, two of which had been transcribed from a reviewer's table with no producer here behind
them. This is that audit, pointed at Paper 1, sharing the engine in `puckworks.review.number_audit`
so the three papers cannot drift apart in what "accounted for" means.

Paper 1 has a wrinkle Paper 2 does not: several results come from the SLOW lane
(`validation/slow/angeloni_bracket.py`, `identifiability.py`) and are not in the fast bundle at
all. Those are registered in `SLOW_LANE_RESULTS` with the producer that computes them and the
committed archive that records the value, so the manuscript's number is at least traceable to a
recorded run rather than to prose. That is weaker than a bundle-backed claim and is labelled as
such rather than being quietly counted as producer-backed.

CLI::

    python -m puckworks.paper_a.claim_coverage           # report; exit 1 above the baseline
    python -m puckworks.paper_a.claim_coverage --json
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from puckworks.review import number_audit as NA

REPO_ROOT = Path(__file__).resolve().parents[2]
MANUSCRIPT = REPO_ROOT / "docs" / "PAPER_A_DRAFT.md"
CONVERSION = REPO_ROOT / "docs" / "submission" / "PAPER_A_JFE_MANUSCRIPT.md"
BUNDLE = REPO_ROOT / "docs" / "figures" / "paper_a" / "results.json"

#: Sections that are not results prose: the figure list, the reproducibility appendix (a pointer
#: list of module paths and commands), and the reference list.
SKIP_SECTIONS = (
    "## References",
    "## Reproducibility",
    "## Data and code availability",
    "## Figures",
)

#: Declared protocol / configuration constants — inputs to the analysis, not results. Each needs a
#: stated source rather than a producer.
CONFIG_CONSTANTS: dict[str, str] = {
    "8000": "bootstrap replicates B for the paired model-minus-null resampling, seed 0",
    "600": "replicate cap for the out-of-bag coverage bootstrap",
    "599": "effective replicates (one draw left no condition out of bag)",
    "0": "bootstrap seed",
    "10": "percent-above-minimum threshold defining the near-optimal set",
    "95": "interval coverage (%)",
    "9": "(T,p) condition clusters in the Angeloni design",
    "108": "held-out points in the O->C/F transfer",
    "54": "held-out errors in the leave-one-condition-out evaluation",
    "3": "solutes (caffeine, trigonelline, 5-CQA); also polynomial degree where stated",
    "2": "varieties (Arabica, Robusta)",
    "6": "objective-family panels (3 solutes x 2 varieties)",
    "0.05": "significance threshold where stated",
    "1.345": "Huber tuning constant (standard)",
    "1.4826": "MAD-to-sigma consistency constant (standard)",
    "0.25": "lower boundary of the swept rate set",
    "6.5": "upper boundary of the tested rate domain",
    "0.1": "lower edge of the wider sensitivity domain",
    "0.3": "lower edge of the narrower sensitivity domain",
    "20": "diffusion times integrated; also a declared tolerance (%)",
    "5": "declared tolerance (%)",
    "4": "declared tolerance (%)",
    "40": "brew-ratio / sampling window parameter as declared in §2",
    "27": "sampling window parameter as declared in §2",
    "32": "Sauter mean diameter subscript d_32 in the Sherwood correlation",
    "15": "diffusivity exponent (Wilke-Chang, 1e-15) and the 15 collected fractions",
    "1": "fraction indices of the retained six-window subset",
    "7": "fraction index in the retained subset",
    "18": "grid points for the ladder and comparator analyses",
    "29": "grid points for the formal panel",
    "36": "grid points in the convergence sweep",
    "41": "inventory-axis grid points",
    "72": "grid points in the convergence sweep",
    "144": "grid points in the convergence sweep",
    "0.15": "lower edge of the swept rate domain",
    "0.55": "lower edge of the inventory grid",
    "200": "axial nodes in the PDE discretisation",
    "1/3": "brew-ratio denominator",
    "38": "endpoint-mass sensitivity target (mL)",
    "42": "endpoint-mass sensitivity target (mL)",
    "25": "unmatched fixed observation window (s) used only as a contrast",
    "16": "rate-sweep span factor",
    "0.8": "swept rate at which the fraction minimum occurs",
    "1.0": "swept rate at which the fraction minimum occurs",
}

#: Facts about the SOURCE DATASETS rather than results computed here.
DATASET_FACTS: dict[str, str] = {
    "1.4": "Pannusch fitted geometry (one of three)",
    "1.7": "Pannusch fitted geometry (one of three)",
    "2.0": "Pannusch fitted geometry (one of three)",
    "10.80": "pannusch2024 fitted c_s0 for caffeine (mg/mL), volume basis not independently anchored",
    "12.5": "independently measured Table 7 inventory (mg/mL)",
    "4.8": "lower end of the inventory basis span (mg/mL)",
    "16.3": "upper end of the inventory basis span (mg/mL)",
    "2871": "Foods 12, 2871 (2023) — Schmieder DoE article number",
    "2688": "Appl. Sci. 13, 2688 (2023) — Angeloni article number",
    "367": "J. Food Eng. 367 — Pannusch volume",
    "111887": "J. Food Eng. 367, 111887 — Pannusch article number",
    "063113": "Phys. Fluids 38, 063113 — Waszkiewicz article number",
    "66": "condition-level sample records in the Angeloni set (33 per variety)",
    "33": "condition-level sample records per variety",
    "19.7": "upper end of the source-reported analyte RSD range (%)",
    "0.3": "lower end of the source-reported analyte RSD range (%)",
    "24": "fine representative particle size (um), measured PSD peak; also ~24 s espresso anchor",
    "330": "coarse representative particle size (um)",
    "0.23": "fines volume fraction at the centre grind",
    "84": "d32 Sauter mean diameter at the centre grind (um), reported as measured on the "
          "pannusch2024 source card; the manuscript now defines d32 (third review MC4.1)",
    "0.015": "bed height L (m)",
    "0.058": "bed diameter D_bed (m)",
    "60": "dissolved-solids bins span 0-60 s in the released trace",
    "12": "five-second dissolved-solids bins; also journal volume",
    "93": "assumed brew temperature (degC), swept separately",
    "89": "lower edge of the swept assumed-temperature range (degC)",
    "93.4": "physical espresso anchor temperature (degC)",
    "40": "physical espresso anchor beverage mass (g)",
    "10": "consecutive fractions collected by the source study",
    "6": "retained collection windows per solute",
    "13": "Appl. Sci. volume; also the measured Table 7 caffeine inventory (mg/mL)",
    "9": "on-grid (T,p) conditions; also 9 bar anchor pressure",
    "2": "off-grid conditions; also varieties",
}

CITED_VALUES: dict[str, str] = {}

#: Results produced by the SLOW lane, which the fast bundle does not carry. Each entry names the
#: producer AND the committed archive recording the value, so the manuscript number is traceable to
#: a recorded run. Weaker than a bundle-backed claim; counted separately, never as `producer`.
SLOW_LANE_RESULTS: dict[str, str] = {
    "7.4": "loco_coverage_interval pooled held-out MAPE; docs/paper1_resource/PAPER_A_P0-5_RESULTS.md",
    "4.3": "loco_coverage_interval 95% lower; PAPER_A_P0-5_RESULTS.md",
    "11.5": "loco_coverage_interval 95% upper; PAPER_A_P0-5_RESULTS.md",
    "0.66": "objective-family: Arabica caffeine SSE rate_at_min 0.659; PAPER_A_OBJECTIVE_FAMILY_PANELS.json",
    "0.58": "objective-family: relative-L2 rate_at_min 0.576 (both panels)",
    "0.86": "objective-family: Arabica caffeine Huber rate_at_min 0.863",
    "0.44": "objective-family: Robusta trigonelline SSE rate_at_min 0.440",
    "0.50": "objective-family: Robusta trigonelline Huber rate_at_min 0.504",
    "31": "objective-family: smallest 10%-set fraction across panels x objectives (0.310)",
    "100": "objective-family: largest 10%-set fraction across panels x objectives (1.000)",
    "1.19": "external panel: smallest RMSE-after-level range ratio; PAPER_A_EXTERNAL_PANEL_LOSSES.json",
    "1.30": "external panel: largest RMSE-after-level range ratio",
    "1.64": "external panel: smallest MAPE range ratio",
    "2.07": "external panel: largest MAPE range ratio",
    "57": "external panel: smallest minimum residual (%)",
    "75": "external panel: largest minimum residual (%)",
    "2.6": "improvement of the model over the same-(T,p) lookup (pp), 8.23 vs 10.79",
    "0.725": "endpoint propagation: 40 mL within-group clustered lower bound (pp); quoted at 3 sf because 0.725 sits exactly on a 2 dp rounding boundary",
    "0.751": "endpoint propagation: 40 mL whole-group clustered lower bound (pp)",
    "0.027": "endpoint propagation: 40 mL within-group clustered UPPER bound (pp)",
    "0.032": "endpoint propagation: 40 mL whole-group clustered UPPER bound (pp)",
    "0.03": "paired bootstrap 95% bound (pp)",
    "8.5": "tolerance sweep: worst-case held-out MAPE at the 2% tolerance (%)",
    "9.7": "tolerance sweep: worst-case held-out MAPE at the 20% tolerance (%)",
    "2.8": "per solute x variety held-out median, lowest (%)",
    "8.8": "per solute x variety held-out median, highest (%)",
    "32.7": "worst individual LOCO fold, Robusta 5-CQA (%)",
    "5.1": "condition-cluster resampling 95% lower bound (%)",
    "8.3": "condition-cluster resampling 95% upper bound (%)",
    "7.0": "pooled mean under a log/relative-error level fit (%)",
    "0.71": "fitted rate before the flow-map perturbation",
    "0.88": "fitted rate after the flow-map perturbation",
    "0.6": "max held-out MAPE shift under geometry/flow-map perturbation (pp)",
    "2.2": "per-species refit rate for caffeine",
    "3.4": "inventory-basis span ratio (16.3/4.8)",
    "3.3": "profile log-width on the wider [0.1,10] domain (3.289)",
    "2.0": "profile log-width on the narrower [0.3,3] domain (2.039)",
    "89": "fraction of grid within 10% on the narrower domain (%)",
    "1900": "identifiability convergence: condition number at 18 rate points (1924)",
    "2100": "identifiability convergence: condition number at 36/72 rate points (2069.5/2067.0)",
    "2000": "identifiability convergence: condition number at 144 rate points (2021.8)",
    "0.99": "curvature coupling across the convergence sweep (-0.993/-0.994)",
    "1.8": "inventory grid upper edge, times the profiled optimum",
    "0.17": "bulk bed porosity, source physical parameter",
    "6.0": "positive control: caffeine minimum fraction MAPE (6.04 %)",
    "1.4": "positive control: caffeine sampled-aggregate range ratio (1.43)",
    "4.1": "positive control: caffeine fraction range ratio (4.05); also 5-CQA minimum sampled-aggregate MAPE (4.13 %)",
    "4.4": "positive control: trigonelline (4.41) / 5-CQA (4.37) fraction range ratio",
    "1.2": "positive control: trigonelline sampled-aggregate range ratio (1.22)",
    "3.6": "positive control: trigonelline minimum sampled-aggregate MAPE (3.62 %)",
    "10.0": "positive control: trigonelline minimum fraction MAPE (9.99 %)",
    "1.6": "independent-trace check: lower fraction-scoring range ratio",
    "2.1": "independent-trace check: upper fraction-scoring range ratio",
    # --- endpoint propagation through the full transfer-versus-null benchmark (P0-4) ----------
    # Producer: validation.slow.angeloni_bracket.endpoint_propagation_benchmark; archive:
    # docs/paper1_resource/PAPER_A_ENDPOINT_PROPAGATION.json. ~2-3 min of PDE solves per endpoint.
    "8.17": "endpoint propagation: model pooled held-out MAPE at 38 mL (%)",
    "8.20": "endpoint propagation: model pooled held-out MAPE at 42 mL (%)",
    "0.421": "endpoint propagation: paired model-minus-null difference at 38 mL (pp)",
    "0.361": "endpoint propagation: paired model-minus-null difference at 40 mL (pp)",
    "0.392": "endpoint propagation: paired model-minus-null difference at 42 mL (pp)",
    "0.79": "endpoint propagation: 38 mL clustered percentile range, lower bound (pp)",
    "0.72": "endpoint propagation: 40 mL clustered percentile range, lower bound (pp)",
    "0.78": "endpoint propagation: 42 mL clustered percentile range, lower bound (pp)",
    "0.01": "endpoint propagation: 42 mL clustered percentile range, upper bound (pp)",
    "51": "endpoint propagation: held-out points where the model is worse, at 38 mL",
    "49": "endpoint propagation: held-out points where the model is worse, at 42 mL; "
          "also the unmatched fixed-window comparison upper end (%)",
    "0.06": "endpoint propagation: spread of the paired difference across 38/40/42 mL (pp)",
    "0.42": "endpoint propagation: the paired difference rounded to 2 dp at 38 mL (-0.421), quoted as the range endpoint in prose",
    # --- PDE discretisation / solver-tolerance convergence (MC4.4) ------------------------------
    # Producer: validation.slow.angeloni_bracket.numerical_convergence; archive:
    # docs/paper1_resource/PAPER_A_NUMERICAL_CONVERGENCE.json.
    "400": "PDE convergence: finest axial resolution swept (nodes)",
    "0.0004": "PDE convergence: worst-case relative deviation of the whole-cup concentration (%)",
    "0.0013": "PDE convergence: worst-case relative deviation of the late fraction (%)",
    "0.0204": "PDE convergence: worst-case relative deviation of the profile range ratio (%)",
    # Solver-health instrumentation (fourth review P0-4): 9 cells x 18 rate points x 9 conditions.
    # NOTE the 18: the convergence profile is swept on the LADDER grid, not the 29-point formal
    # panel grid, which is part of why its minimum is not expected to coincide with the panels'.
    "1458": "PDE convergence: profiled solves checked for termination status, finiteness, "
            "positivity and volume/mass monotonicity (9 cells x 18 rates x 9 conditions)",
    # --- diffusivity-closure audit (fourth review P0-2) -----------------------------------------
    # Archive: docs/paper1_resource/PAPER_A_DIFFUSIVITY_CLOSURE_AUDIT.json. The molecular weights
    # are the solute MWs the implementation supplies to the Wilke-Chang association factor; the
    # rest are the numerical degeneracy check that shows the closure choice is absorbed by the
    # fitted rate.
    "194.19": "diffusivity closure: caffeine molecular weight (g/mol)",
    "137.14": "diffusivity closure: trigonelline molecular weight (g/mol)",
    "354.31": "diffusivity closure: 5-CQA molecular weight (g/mol)",
    "2.84": "diffusivity closure: Arabica-caffeine minimum MAPE under either closure (%), "
            "2.8375 vs 2.8328 to 3 sf",
    "1.43": "diffusivity closure: Arabica-caffeine profile range ratio, source closure (1.4268)",
    "1.45": "diffusivity closure: Arabica-caffeine profile range ratio, solvent-MW variant (1.4486)",
}

DERIVED_QUANTITIES: dict[str, tuple[str, str, str]] = {}


def _claims():
    from puckworks.paper_a.build import _CLAIMS
    return list(_CLAIMS)


def _bundle():
    with open(BUNDLE, encoding="utf-8") as fh:
        return json.load(fh)


#: Ratchet. CI enforces that this never grows; lowering it is the work.
BASELINE_UNACCOUNTED = 0


def binding_coverage() -> dict:
    """How many slow-lane results are CHECKED against their archive, versus merely described.

    This is the number that says whether the review process is converging. Before the binding
    sweep it was 0 of 75.
    """
    from puckworks.paper_a import slow_lane_bindings as SLB

    bound = sorted(set(SLOW_LANE_RESULTS)
                   & (set(SLB.BINDINGS) | set(SLB.DERIVED) | set(SLB.CODE_CONSTANTS)))
    declared = sorted(set(SLOW_LANE_RESULTS) & set(SLB.UNBINDABLE))
    unbound = sorted(set(SLOW_LANE_RESULTS) - set(bound) - set(declared))
    return dict(n_slow_lane=len(SLOW_LANE_RESULTS), n_archive_bound=len(bound),
                n_declared_unbindable=len(declared), n_still_unbound=len(unbound),
                archive_bound=bound, declared_unbindable=declared, still_unbound=unbound)


def _spec(manuscript=None):
    cfg = dict(CONFIG_CONSTANTS)
    # Slow-lane values are labelled by whether they are actually CHECKED against the archived run
    # or merely described by a sentence. Before the 2026-07-28 binding sweep every one of them read
    # "SLOW LANE: ..." regardless, so a verified number and an unverifiable one were indis-
    # tinguishable in the audit -- which is how stale numbers survived five review rounds.
    from puckworks.paper_a import slow_lane_bindings as SLB
    for k, v in SLOW_LANE_RESULTS.items():
        if k in SLB.CODE_CONSTANTS:
            m, a, _k, _ = SLB.CODE_CONSTANTS[k]
            cfg[k] = f"CODE-BOUND ({m}.{a}): {v}"
        elif k in SLB.DERIVED:
            cfg[k] = f"ARCHIVE-BOUND (derived over {SLB.DERIVED[k][0]}): {v}"
        elif k in SLB.BINDINGS:
            archive, path = SLB.BINDINGS[k][0], SLB.BINDINGS[k][1]
            cfg[k] = f"ARCHIVE-BOUND ({archive}:{path}): {v}"
        elif k in SLB.UNBINDABLE:
            cfg[k] = f"SLOW LANE (UNBINDABLE -- {SLB.UNBINDABLE[k]}): {v}"
        else:
            cfg[k] = "SLOW LANE (UNBOUND): " + v
    return NA.PaperSpec(
        name="Paper 1 claim coverage",
        manuscript=manuscript or MANUSCRIPT,
        claims=_claims,
        skip_sections=SKIP_SECTIONS,
        config_constants=cfg,
        dataset_facts=DATASET_FACTS,
        cited_values=CITED_VALUES,
        derived=DERIVED_QUANTITIES,
        bundle=_bundle,
        baseline=BASELINE_UNACCOUNTED,
    )


def audit(path=None):
    return NA.audit(_spec(path), path)


def render(report):
    return NA.render(report)


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else list(argv)
    which = CONVERSION if "--conversion" in argv else MANUSCRIPT
    report = NA.audit(_spec(which), which)
    if "--json" in argv:
        print(json.dumps(report, indent=2))
    else:
        print(render(report))
    n = len(report["unaccounted"])
    if n > BASELINE_UNACCOUNTED:
        print(f"\nFAIL: {n} unaccounted exceeds the baseline of {BASELINE_UNACCOUNTED}.",
              file=sys.stderr)
        return 1
    if n < BASELINE_UNACCOUNTED:
        print(f"\nNOTE: {n} unaccounted, below the baseline of {BASELINE_UNACCOUNTED} — "
              f"lower BASELINE_UNACCOUNTED to {n} so the ratchet holds.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
