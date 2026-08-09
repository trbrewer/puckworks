"""deep_i093_run_audit.py — outcome-neutral execution audit for the I-093 deep screen.

    OUTCOME_NEUTRAL
    NO_PERMEABILITY_VALUES

Built **before** any deep permeability output was inspected. It reconstructs the run matrix that
`docs/insights/screens/I-093/DEEP_SCREEN_PROTOCOL.md` freezes, costs it from single-run timings
measured during the cheap screen, and defines the status vocabulary the later adjudication must
account every cell against.

Nothing here reads a result. `expected_run_matrix()` is a pure function of the frozen protocol
constants, so the audit can be regenerated and tested independently of what the solver produced.

The frozen guard semantics, read from `deep_screen_i093_rve` and NOT changed:

  * the budget is checked **before launching** each cell (`if spent > budget_s: break`);
  * a cell admitted before the cutoff **runs to completion** — no in-flight termination;
  * `spent` accumulates measured wall time, so the cutoff is reached mid-section;
  * in `porosity_dependence`, a porosity is only recorded when **both** its sizes completed
    (`if len(per_L) == 2`), so a half-finished porosity is dropped rather than reported partial;
  * in `trend_on_stabilised_means`, fewer than two completed porosities returns `skipped`.

Run:  python -m puckworks.analysis.deep_i093_run_audit
"""
from __future__ import annotations

import hashlib
import json
import pathlib

from puckworks.analysis import deep_screen_i093_rve as D
from puckworks.analysis import screen_i093_crossscale_permeability as CHEAP

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
BUNDLE = "docs/insights/screens/I-093"

#: Single-run wall-clock seconds measured during the cheap screen at the frozen resolution
#: (grain radius 10 voxels). Used ONLY to cost the matrix; no result depends on them.
MEASURED_COST_S = {32: 18, 48: 55, 64: 183, 80: 403, 100: 726}

#: Every state an expected cell can end in. The adjudication must place all 46 cells.
STATUSES = ("EXPECTED", "LAUNCHED", "CONVERGED", "SCIENTIFIC_NONCONVERGENCE",
            "OPERATIONAL_FAILURE", "EXACT_RETRY", "NOT_LAUNCHED_BUDGET_GUARD",
            "IN_FLIGHT_AT_GUARD")

SEED_SEMANTICS = "RELATED_NON_NESTED"
SEED_SEMANTICS_STATEMENT = (
    "Equal seeds initialize a common pseudorandom stream, but size-dependent coordinate mapping, "
    "placement history, stopping behavior, and draw count produce non-nested geometries. "
    "Equal-seed cases are not interpretable as the same physical realization at increasing size. "
    "No paired finite-size analysis is used. Cross-size statistical independence is not "
    "established.")


def _cost(L):
    return MEASURED_COST_S.get(L, max(MEASURED_COST_S.values()))


def expected_run_matrix():
    """The 46 frozen cells, in the exact order the frozen implementation launches them."""
    cells, order = [], 0

    def add(section, L, phis, seed, cfg, primary, closure, note=""):
        nonlocal order
        order += 1
        cells.append(dict(
            order=order, section=section, L=L,
            L_over_d=L / (2.0 * CHEAP.GRAIN_RADIUS_VOXELS),
            phis_target=phis, seed=seed, solver_config=cfg,
            lattice=[L, L, L], estimated_cost_s=_cost(L),
            required_convergence="lb_reference.solve reaches rtol=%g within max_steps=%d"
                                 % (cfg.get("rtol", CHEAP.LB_KW["rtol"]),
                                    cfg.get("max_steps", CHEAP.LB_KW["max_steps"])),
            needed_for_primary_finite_size=primary,
            needed_for_closure_decision=closure,
            expected_output="deep_result.json -> %s" % section,
            status="EXPECTED", note=note))

    base = dict(CHEAP.LB_KW)
    for L in D.DEEP_SIZES:                                  # §3
        for s in D.DEEP_SEEDS:
            add("S3_multiseed_rve", L, D.DEEP_PHIS, s, base, True, False)
    add("S4.1_tolerance_baseline", 64, D.DEEP_PHIS, 0, base, False, False)   # §4.1
    add("S4.1_tolerance_tightened", 64, D.DEEP_PHIS, 0, dict(base, **D.TOL_SENSITIVITY),
        False, False)
    for p in D.EXTREME_PHIS:                                # §4.2
        for L in D.EXTREME_SIZES:
            for s in D.DEEP_SEEDS:
                add("S4.2_porosity_dependence", L, p, s, base, False, True,
                    note="porosity is recorded only if BOTH sizes complete (len(per_L)==2)")
    for p in CHEAP.PHIS_TARGETS:                            # §4.3
        for s in D.DEEP_SEEDS[:2]:
            add("S4.3_trend_on_means", max(D.DEEP_SIZES), p, s, base, False, True)
    return cells


def audit():
    cells = expected_run_matrix()
    by_section = {}
    for c in cells:
        e = by_section.setdefault(c["section"], dict(cells=0, est_s=0))
        e["cells"] += 1
        e["est_s"] += c["estimated_cost_s"]
    total = sum(c["estimated_cost_s"] for c in cells)
    return dict(
        kind="OUTCOME_NEUTRAL_EXECUTION_AUDIT",
        note="constructed from the frozen protocol before any permeability output was inspected",
        base_commit=CHEAP.BASE_COMMIT,
        deep_protocol_sha256=hashlib.sha256(
            (REPO_ROOT / BUNDLE / "DEEP_SCREEN_PROTOCOL.md").read_bytes()).hexdigest(),
        cheap_protocol_sha256=CHEAP._sha256(CHEAP.PROTOCOL_PATH),
        seed_semantics=SEED_SEMANTICS,
        seed_semantics_statement=SEED_SEMANTICS_STATEMENT,
        seed_semantics_evidence=dict(
            source="puckworks/models/brewer2026/pack_generator.py::make_pack",
            same_seed_same_L_reproducible=True,
            different_seed_same_L_differs=True,
            smaller_is_spatial_subset_of_larger=False,
            size_changes_coordinate_mapping="rng.integers(0, L, batch) bounds depend on L",
            size_changes_draw_count="placement loops until solid.mean() >= phis_target",
            voxel_agreement_L32_vs_L64_corner=0.5057,
            chance_level_expectation=0.5001,
            caveat="weak spatial correspondence for the tested case is supporting evidence only; "
                   "it does NOT establish cross-size statistical independence, which was not "
                   "quantified"),
        statistical_consequences=[
            "no paired size differences are computed",
            "no lines connect equal seeds across sizes in any figure",
            "each box size is summarised as its own ensemble",
            "no independent-groups inferential test is introduced post hoc",
            "cross-size covariance induced by common seed labels was not quantified",
        ],
        guard_semantics=dict(
            checks_before_launch=True,
            terminates_in_flight_cell=False,
            admitted_cell_runs_to_completion=True,
            budget_s=D.COMPUTE_BUDGET_S,
            source="deep_screen_i093_rve: `if spent > budget_s: break` precedes each _run call",
            partial_porosity_dropped="porosity_dependence records a porosity only when both "
                                     "sizes completed (len(per_L) == 2)",
            trend_skipped_when="trend_on_stabilised_means returns skipped when fewer than two "
                               "porosities completed"),
        measured_single_run_cost_s=dict(MEASURED_COST_S),
        expected_cells=len(cells),
        by_section={k: dict(v, est_min=round(v["est_s"] / 60, 1)) for k, v in by_section.items()},
        estimated_total_s=total, estimated_total_min=round(total / 60, 1),
        frozen_budget_s=D.COMPUTE_BUDGET_S, frozen_budget_min=D.COMPUTE_BUDGET_S / 60,
        budget_sufficient=bool(total <= D.COMPUTE_BUDGET_S),
        shortfall_min=round((total - D.COMPUTE_BUDGET_S) / 60, 1),
        status_vocabulary=list(STATUSES),
        cells=cells,
    )


def main(argv=None):
    a = audit()
    out = REPO_ROOT / BUNDLE / "expected_run_matrix.json"
    out.write_text(json.dumps(a, indent=2) + "\n", encoding="utf-8")
    print("expected cells: %d" % a["expected_cells"])
    for k, v in sorted(a["by_section"].items()):
        print("  %-28s %2d cells  est %6.0f s (%.1f min)" % (k, v["cells"], v["est_s"], v["est_min"]))
    print("estimated total %.0f s (%.1f min) vs frozen budget %.0f min -> sufficient=%s (short by %.1f min)"
          % (a["estimated_total_s"], a["estimated_total_min"], a["frozen_budget_min"],
             a["budget_sufficient"], a["shortfall_min"]))
    print("seed semantics: %s" % a["seed_semantics"])
    print("wrote %s" % out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
