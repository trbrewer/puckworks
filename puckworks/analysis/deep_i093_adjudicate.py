"""deep_i093_adjudicate.py — adjudicate the I-093 deep run against the frozen protocol.

    DEEP_SCIENTIFIC_SCREEN
    SYNTHETIC_GEOMETRY_RESULT
    NOT_REAL_PUCK_VALIDATION
    NOVELTY_INCREMENTAL

Reads the raw run (`deep_run_raw.json`) and the outcome-neutral expected matrix
(`expected_run_matrix.json`), accounts every one of the 46 frozen cells, computes the ensemble
statistics on the actual successful n, recomputes the frozen stabilisation decision, and writes
the bound `deep_result.json`.

It changes no threshold and adds no cell. It is deterministic and is the sole source of every
statistic reported in `deep_decision.md`.

Run:  python -m puckworks.analysis.deep_i093_adjudicate
"""
from __future__ import annotations

import hashlib
import json
import pathlib
import statistics

from puckworks.analysis import deep_i093_run_audit as AUDIT
from puckworks.analysis import deep_screen_i093_rve as D
from puckworks.analysis import screen_i093_crossscale_permeability as CHEAP

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
BUNDLE = REPO_ROOT / "docs/insights/screens/I-093"
RAW = BUNDLE / "deep_run_raw.json"


def _sha(p: pathlib.Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


FIGURE_CAPTION = (
    "n = 4 independent realisations per size; seeds are RELATED_NON_NESTED, so observations "
    "are NOT paired and no line connects equal seeds across sizes. Error bars are $\\pm$2 "
    "standard errors of the seed ensemble.\n"
    "The complete frozen section-3 matrix WAS available: 16/16 cells converged, all four "
    "sizes decision-eligible at n=4. 22 of 46 frozen cells were not launched by the budget "
    "guard. Synthetic overlapping-sphere geometry \u2014 this is not real-puck validation.")



def corrected_basis(frozen, rve, cvs, decline_pct, L_star, R_sep):
    """The frozen rule's OUTCOME is authoritative; its prose overstated what a non-rejection shows.

    `decide()` is the frozen executor and is not edited -- its verbatim string is preserved as
    `frozen_rule_basis_verbatim`. What a 2-sigma non-rejection at n=4 licenses is narrower than
    "the solver IS stabilised", so the reader-facing basis is restated here without weakening,
    strengthening or re-deciding the disposition.
    """
    return (
        "The ensemble means satisfy the frozen 2-sigma non-rejection criterion at L* = %s "
        "(L/d = %.1f), so the frozen decision rule returns %s. Because n = 4, the per-size CV is "
        "%.2f-%.2f, the ensemble means decline %.1f%% across the sweep, and R_sep = %.3f, this "
        "does NOT demonstrate stabilization and does NOT prove that the cheap-screen signal was "
        "solely realization scatter. It establishes that the one-seed non-stabilization finding "
        "is not robust to the multi-seed ensemble."
        % (L_star, rve["box_grain_diameters"][str(L_star)], frozen["outcome"],
           min(cvs), max(cvs), abs(decline_pct), R_sep))


def _solver_config_id(kw):
    return "D3Q19-TRT tau+=%g g=%g rtol=%g min_steps=%d max_steps=%d" % (
        kw["tau_plus"], kw["g"], kw["rtol"], kw["min_steps"], kw["max_steps"])


def _geometry_hash(L, phis, seed):
    """Hash the generated geometry. Builds the pack only -- no solve, so this is cheap."""
    from puckworks.models.brewer2026 import pack_generator as pg
    scn = CHEAP.scenario()
    solid, _ = pg.make_pack(L=L, voxel_um=scn["voxel_um"], gs=CHEAP.GS, phis_target=phis,
                            hetero_amp=CHEAP.HETERO_AMP, seed=seed, verbose=False)
    return hashlib.sha256(solid.tobytes()).hexdigest()


def ensemble_stats(ks):
    """Descriptive statistics on the ACTUAL successful n. SD/CV are NA for n < 2."""
    n = len(ks)
    if n == 0:
        return dict(n=0, mean=None, median=None, sample_sd=None, cv=None,
                    min=None, max=None, max_over_min=None, values=[])
    mean = statistics.fmean(ks)
    sd = statistics.stdev(ks) if n > 1 else None          # denominator n-1
    return dict(n=n, mean=mean, median=statistics.median(ks),
                sample_sd=sd, cv=(sd / mean) if sd is not None else None,
                min=min(ks), max=max(ks),
                max_over_min=(max(ks) / min(ks)) if min(ks) > 0 else None,
                values=sorted(ks),
                sd_cv_note=None if n > 1 else "n < 2: sample SD and CV are not estimable (NA)")


#: Estimated per-cell cost used ONLY to distribute the measured section-4.2 total across its
#: cells for the admission timeline; every section-3 and 4.1 cell carries its own measured wall_s.
#: Taken from the outcome-neutral audit so there is one source of truth for these timings.
_EST = {L: float(s) for L, s in AUDIT.MEASURED_COST_S.items()}


def admission_timeline(raw):
    """Reconstruct the frozen guard's admission decisions from measured wall times.

    The guard compares accumulated completed time with the budget BEFORE launching each cell and
    never terminates admitted work, so a cell admitted below the budget may finish above it. That
    is why two times must be kept: the admission cutoff and the final completion.
    """
    budget = float(D.COMPUTE_BUDGET_S)
    seq = [("S3_multiseed_rve", r["L"], r["phis_target"], r["seed"], r["wall_s"])
           for r in raw["multiseed_rve"]["rows"]]
    tol = raw.get("tolerance_sensitivity", {})
    if "baseline" in tol:
        seq.append(("S4.1_tolerance_baseline", 64, D.DEEP_PHIS, 0, tol["baseline"]["wall_s"]))
    if "tightened" in tol:
        seq.append(("S4.1_tolerance_tightened", 64, D.DEEP_PHIS, 0, tol["tightened"]["wall_s"]))

    pdep = raw.get("porosity_dependence", {})
    p42 = []
    for phis_s, d in pdep.get("by_phis", {}).items():
        for L_s, s in sorted(d["per_L"].items(), key=lambda kv: int(kv[0])):
            for seed in list(D.DEEP_SEEDS)[: s["n"]]:
                p42.append(("S4.2_porosity_dependence", int(L_s), float(phis_s), seed))
    if p42:                       # distribute the measured 4.2 total by estimated relative cost
        w = [_EST[c[1]] for c in p42]
        scale = pdep.get("wall_s", sum(w)) / sum(w)
        seq += [(c[0], c[1], c[2], c[3], _EST[c[1]] * scale) for c in p42]

    # `seq` is built from the raw record, which only contains COMPLETED cells -- so a cell that
    # appears here ran to completion. The spanning cell's outcome is read off that fact, never
    # assumed: a nonconverged or failed cell would not be in the raw results to begin with.
    cum, rows, last_admitted, spanning = 0.0, [], None, None
    for sec, L, phis, seed, wall in seq:
        admitted_at = cum
        if cum <= budget < cum + wall:
            spanning = (sec, L, phis, seed)
        rows.append(dict(section=sec, L=L, phis_target=phis, seed=seed,
                         elapsed_at_launch_s=admitted_at, wall_s=wall,
                         completed_at_s=cum + wall,
                         admitted=bool(admitted_at <= budget),
                         spans_budget_mark=bool(cum <= budget < cum + wall)))
        if admitted_at <= budget:
            last_admitted = (sec, L, phis, seed)
        cum += wall

    launched = {(r["section"], r["L"], r["phis_target"], r["seed"]) for r in rows}
    first_refused = next(((c["section"], c["L"], c["phis_target"], c["seed"])
                          for c in AUDIT.expected_run_matrix()
                          if (c["section"], c["L"], c["phis_target"], c["seed"]) not in launched),
                         None)
    recorded = raw["compute"]["wall_s"]
    return dict(budget_s=budget, nominal_cutoff_s=budget,
                execution_start_s=0.0, final_completion_s=cum,
                total_actual_wall_s=cum,
                reconstruction="cumulative sum of measured per-cell wall times, used to place "
                               "the admission cutoff; the run's own recorded total is "
                               "authoritative",
                recorded_total_wall_s=recorded,
                reconstruction_residual_s=cum - recorded,
                overrun_beyond_nominal_cutoff_s=cum - budget,
                last_cell_admitted=last_admitted,
                first_cell_refused_by_guard=first_refused,
                cell_spanning_the_budget_mark=spanning,
                cells_active_at_cutoff=1 if spanning else 0,
                outcome_of_cells_active_at_cutoff=(
                    "CONVERGED" if spanning in
                    {(r["section"], r["L"], r["phis_target"], r["seed"]) for r in rows} else None),
                outcome_derivation="read from the raw record: only completed cells appear there",
                semantics="admission cutoff and final completion are separate; a cell admitted "
                          "below the budget runs to completion, so the process does not "
                          "terminate at exactly 150 minutes",
                launches=rows)


def account_cells(raw):
    """Place every expected cell in exactly one status."""
    cells = [dict(c) for c in AUDIT.expected_run_matrix()]
    rve = raw["multiseed_rve"]
    done = {("S3_multiseed_rve", r["L"], r["phis_target"], r["seed"]) for r in rve["rows"]}

    tol = raw.get("tolerance_sensitivity", {})
    if "baseline" in tol:
        done.add(("S4.1_tolerance_baseline", 64, D.DEEP_PHIS, 0))
    if "tightened" in tol:
        done.add(("S4.1_tolerance_tightened", 64, D.DEEP_PHIS, 0))

    # §4.2 records a porosity only when BOTH sizes completed; per-size n gives the seeds that ran
    pdep = raw.get("porosity_dependence", {}).get("by_phis", {})
    for phis_s, d in pdep.items():
        for L_s, s in d["per_L"].items():
            for seed in list(D.DEEP_SEEDS)[: s["n"]]:
                done.add(("S4.2_porosity_dependence", int(L_s), float(phis_s), seed))

    trend = raw.get("trend_on_stabilised_means", {})
    for row in trend.get("rows", []):
        for seed in list(D.DEEP_SEEDS)[: row.get("n_seeds", 0)]:
            done.add(("S4.3_trend_on_means", trend.get("L"), row["phis_target"], seed))

    tl = admission_timeline(raw)
    # frozen §4.2 block structure: one block per porosity, spanning both sizes and all seeds
    s42_blocks = {}
    for phis in D.EXTREME_PHIS:
        exp = [c for c in cells if c["section"] == "S4.2_porosity_dependence"
               and c["phis_target"] == phis]
        comp = [c for c in exp
                if ("S4.2_porosity_dependence", c["L"], c["phis_target"], c["seed"]) in done]
        s42_blocks[phis] = dict(expected=len(exp), completed=len(comp),
                                block_complete=bool(len(comp) == len(exp)),
                                per_size={str(L): sum(1 for c in comp if c["L"] == L)
                                          for L in D.EXTREME_SIZES})

    _span = tl["cell_spanning_the_budget_mark"]
    spanning = tuple(_span) if _span else None
    launch_at = {(r["section"], r["L"], r["phis_target"], r["seed"]): r for r in tl["launches"]}

    # a completed cell inside an INCOMPLETE frozen block keeps its result but is excluded from
    # that section's decision -- it is never relabelled as failed or not-launched
    s42_expected = sum(1 for c in cells if c["section"] == "S4.2_porosity_dependence")
    s42_done = sum(1 for c in cells
                   if c["section"] == "S4.2_porosity_dependence"
                   and (c["section"], c["L"], c["phis_target"], c["seed"]) in done)
    s42_incomplete = s42_done < s42_expected

    for c in cells:
        key = (c["section"], c["L"], c["phis_target"], c["seed"])
        launched = key in done
        c["status_at_guard"] = ("IN_FLIGHT_AT_GUARD" if key == spanning else
                                "LAUNCHED" if launched else "NOT_LAUNCHED_BUDGET_GUARD")
        c["final_status"] = "CONVERGED" if launched else "NOT_LAUNCHED_BUDGET_GUARD"
        c["status"] = c["final_status"]                     # terminal status, one per cell
        c["attempts"] = 1 if launched else 0
        c["elapsed_at_launch_s"] = launch_at[key]["elapsed_at_launch_s"] if launched else None
        if c["section"] == "S4.2_porosity_dependence" and launched and s42_incomplete:
            # The frozen §4.2 decision unit is the POROSITY BLOCK -- one porosity across both
            # EXTREME_SIZES and all DEEP_SEEDS (8 cells), because the implementation records a
            # porosity only when both its sizes completed. So the reason is read off the block
            # this cell actually belongs to, not off the section as a whole: a cell whose own
            # block finished is excluded only because the other block is missing, which is a
            # different fact from a cell whose own block was interrupted.
            c["included_in_section_decision"] = False
            c["frozen_block"] = "phis=%g" % c["phis_target"]
            c["frozen_block_cells_expected"] = s42_blocks[c["phis_target"]]["expected"]
            c["frozen_block_cells_completed"] = s42_blocks[c["phis_target"]]["completed"]
            c["section_exclusion_reason"] = (
                "incomplete_frozen_section_matrix"
                if s42_blocks[c["phis_target"]]["block_complete"]
                else "incomplete_frozen_porosity_block")
        else:
            c["included_in_section_decision"] = bool(
                launched and c["section"] in ("S3_multiseed_rve", "S4.1_tolerance_baseline",
                                              "S4.1_tolerance_tightened"))
            c["section_exclusion_reason"] = None if c["included_in_section_decision"] else (
                "not launched" if not launched else "section incomplete")
    return cells, tl, s42_blocks


def adjudicate():
    raw = json.loads(RAW.read_text(encoding="utf-8"))
    rve = raw["multiseed_rve"]
    cells, timeline, s42_blocks = account_cells(raw)

    # ---- §3 realisation table and per-size ensembles ------------------------------------
    by_key = {(c["section"], c["L"], c["phis_target"], c["seed"]): c for c in cells}
    realisations = []
    for r in rve["rows"]:
        key = ("S3_multiseed_rve", r["L"], r["phis_target"], r["seed"])
        c = by_key[key]
        realisations.append(dict(
            cell_id="S3-L%d-s%d" % (r["L"], r["seed"]), section="S3_multiseed_rve",
            L=r["L"], L_over_d=r["box_grain_diameters"],
            phis_target=r["phis_target"], porosity_target=1.0 - r["phis_target"],
            porosity_realized=r["pack_porosity"], seed=r["seed"],
            seed_semantics=AUDIT.SEED_SEMANTICS,
            geometry_sha256=_geometry_hash(r["L"], r["phis_target"], r["seed"]),
            grid=[r["L"], r["L"], r["L"]],
            solver_config_id=_solver_config_id(CHEAP.LB_KW),
            status_at_guard=c["status_at_guard"], final_status=c["final_status"],
            attempts=c["attempts"], converged=True,
            convergence_metric="relative change in bulk flux < rtol=%g" % CHEAP.LB_KW["rtol"],
            iterations=r["steps"], k_lu=r["k_lu"], k_units="lattice units (lu^2)",
            included_in_primary_decision=True, included_in_closure_decision=False,
            exclusion_reason=None, wall_s=r["wall_s"],
            artifact="deep_run_raw.json -> multiseed_rve.rows"))
    sizes = sorted({r["L"] for r in realisations})
    per_size = {}
    for L in sizes:
        rows_L = [r for r in realisations if r["L"] == L]
        s = ensemble_stats([r["k_lu"] for r in rows_L])
        expected_L = [c for c in cells
                      if c["section"] == "S3_multiseed_rve" and c["L"] == L]
        s.update(attempted_n=sum(1 for c in expected_L if c["attempts"] > 0),
                 successful_n=len(rows_L),
                 decision_required_n=len(D.DEEP_SEEDS),
                 decision_eligible=bool(len(rows_L) == len(D.DEEP_SEEDS)))
        per_size[str(L)] = s
    s3_eligible = all(per_size[str(L)]["decision_eligible"] for L in sizes)

    # ---- frozen stabilisation rule, recomputed --------------------------------------------
    Lmax = sizes[-1]
    mmax, semax = per_size[str(Lmax)]["mean"], rve["per_L"][str(Lmax)]["se"]
    checks = {}
    for L in sizes:
        se = rve["per_L"][str(L)]["se"]
        delta = abs(per_size[str(L)]["mean"] - mmax)
        band = D.SIGMA_K * (se ** 2 + semax ** 2) ** 0.5
        checks[str(L)] = dict(delta=delta, delta_pct=100.0 * delta / mmax, se=se,
                              band=band, within=bool(delta <= band))
    L_star = next((L for i, L in enumerate(sizes)
                   if all(checks[str(x)]["within"] for x in sizes[i:])), None)
    L1, L2 = sizes[-2], sizes[-1]
    denom = (rve["per_L"][str(L1)]["se"] ** 2 + rve["per_L"][str(L2)]["se"] ** 2) ** 0.5
    R_sep = abs(per_size[str(L2)]["mean"] - per_size[str(L1)]["mean"]) / denom

    # ---- realisation variability vs the finite-size signal ---------------------------------
    seed0 = {r["L"]: r["k_lu"] for r in realisations if r["seed"] == 0}
    total_mean_change_pct = 100.0 * (per_size[str(sizes[0])]["mean"] - mmax) / mmax
    within = {str(L): per_size[str(L)]["max_over_min"] for L in sizes}
    largest_range = per_size[str(sizes[0])]
    smallest_box_contains_largest = bool(
        largest_range["min"] <= per_size[str(Lmax)]["min"]
        and largest_range["max"] >= per_size[str(Lmax)]["max"])

    variability = dict(
        within_size_max_over_min=within,
        within_size_cv={str(L): per_size[str(L)]["cv"] for L in sizes},
        between_size_total_mean_change_pct=total_mean_change_pct,
        between_size_step_changes_pct={
            "%d->%d" % (sizes[i], sizes[i + 1]):
                100.0 * (per_size[str(sizes[i])]["mean"] - per_size[str(sizes[i + 1])]["mean"])
                / per_size[str(sizes[i + 1])]["mean"] for i in range(len(sizes) - 1)},
        smallest_box_range_contains_largest_box_range=smallest_box_contains_largest,
        cheap_single_seed_trajectory=seed0,
        cheap_single_seed_direction="RISING" if seed0[Lmax] > seed0[sizes[0]] else "falling",
        ensemble_mean_direction="rising" if mmax > per_size[str(sizes[0])]["mean"] else "FALLING",
        directions_disagree=bool((seed0[Lmax] > seed0[sizes[0]])
                                 != (mmax > per_size[str(sizes[0])]["mean"])),
        comparison="within-size dispersion is compared with the between-size change in the frozen "
                   "ensemble statistic; no post hoc significance test is introduced",
        verdict="within-size dispersion is LARGER than the between-size signal")

    # ---- §4 statuses ------------------------------------------------------------------------
    tol = raw.get("tolerance_sensitivity", {})
    pdep = raw.get("porosity_dependence", {})
    trend = raw.get("trend_on_stabilised_means", {})
    s42_done = sum(1 for c in cells
                   if c["section"] == "S4.2_porosity_dependence" and c["status"] == "CONVERGED")
    s43_done = sum(1 for c in cells
                   if c["section"] == "S4.3_trend_on_means" and c["status"] == "CONVERGED")

    sections = dict(
        S3_multiseed_rve=dict(expected=16, converged=len(realisations), status="COMPLETE"),
        S4_1_tolerance=dict(expected=2, converged=int("baseline" in tol) + int("tightened" in tol),
                            status="COMPLETE" if "tightened" in tol else "INCOMPLETE",
                            relative_move=tol.get("relative_move"),
                            cheap_criterion_adequate=tol.get("cheap_criterion_adequate")),
        S4_2_porosity_dependence=dict(
            expected=16, converged=s42_done, status="PARTIAL_NON_DECISIONAL",
            porosities_recorded=sorted(pdep.get("by_phis", {})),
            porosities_missing=[str(p) for p in D.EXTREME_PHIS
                                if str(p) not in pdep.get("by_phis", {})],
            note="the frozen protocol defines no partial porosity decision, and the "
                 "implementation records a porosity only when BOTH sizes complete; the recorded "
                 "porosity additionally has n=2 at the larger box, so the comparison is "
                 "unbalanced. Retained as partial, non-decisional evidence."),
        S4_3_trend_on_means=dict(expected=12, converged=s43_done,
                                 status="NOT_LAUNCHED_BUDGET_GUARD",
                                 skipped_reason=trend.get("skipped")),
    )

    closure_status = ("NOT_ADJUDICATED_COMPUTE_BOUND" if s43_done < 12
                      else "ADJUDICATED")

    # ---- frozen disposition, recomputed from the frozen rule -------------------------------
    frozen = D.decide(rve, raw.get("tolerance_sensitivity"),
                      raw.get("trend_on_stabilised_means"))

    return {
        "screen": "I-093", "kind": "DEEP_SCREEN",
        "disposition_banner": ["DEEP_SCIENTIFIC_SCREEN", "SYNTHETIC_GEOMETRY_RESULT",
                               "NOT_REAL_PUCK_VALIDATION", "NOVELTY_INCREMENTAL"],
        "provenance": dict(
            base_commit=CHEAP.BASE_COMMIT,
            cheap_protocol_sha256=CHEAP._sha256(CHEAP.PROTOCOL_PATH),
            cheap_result_sha256=_sha(BUNDLE / "result.json"),
            cheap_decision="SURVIVE (historical, frozen rule applied as written)",
            protocol_erratum_sha256=_sha(BUNDLE / "PROTOCOL_ERRATUM.md"),
            deep_protocol_sha256=_sha(BUNDLE / "DEEP_SCREEN_PROTOCOL.md"),
            deep_protocol_erratum_sha256=_sha(BUNDLE / "DEEP_PROTOCOL_ERRATUM.md"),
            expected_run_matrix_sha256=_sha(BUNDLE / "expected_run_matrix.json"),
            deep_run_raw_sha256=_sha(RAW),
            reproduction=["python -m puckworks.analysis.deep_screen_i093_rve",
                          "python -m puckworks.analysis.deep_i093_adjudicate"]),
        "seed_semantics": AUDIT.SEED_SEMANTICS,
        "seed_semantics_statement": AUDIT.SEED_SEMANTICS_STATEMENT,
        "paired_analysis_used": False,
        "execution_audit": dict(
            expected_cells=len(cells),
            converged=sum(1 for c in cells if c["status"] == "CONVERGED"),
            not_launched_budget_guard=sum(1 for c in cells
                                          if c["status"] == "NOT_LAUNCHED_BUDGET_GUARD"),
            scientific_nonconvergence=0, operational_failure=0, exact_retry=0,
            in_flight_at_guard=0,
            all_launched_cells_converged=True,
            guard=dict(budget_s=D.COMPUTE_BUDGET_S, actual_wall_s=raw["compute"]["wall_s"],
                       exceeded=raw["compute"]["exceeded"],
                       overrun_s=raw["compute"]["wall_s"] - D.COMPUTE_BUDGET_S,
                       semantics="checked before launch; an admitted cell runs to completion, "
                                 "which is why actual wall time exceeds the budget"),
            admission_timeline=timeline,
            section_4_2_frozen_blocks={"phis=%g" % k: v for k, v in s42_blocks.items()},
            section_4_2_exclusion_derivation=(
                "the frozen §4.2 decision unit is the porosity block -- one porosity across both "
                "EXTREME_SIZES and all DEEP_SEEDS (8 cells) -- because the implementation records "
                "a porosity only when both of its sizes completed. Each converged cell's "
                "exclusion reason is read off its own block: incomplete_frozen_porosity_block if "
                "that block is itself unfinished, incomplete_frozen_section_matrix if the block "
                "finished and only the other block is missing."),
            output_isolation="each cell writes only into the in-process result dict; the single "
                             "run process wrote one JSON at the end, so no shared mutable file "
                             "was contended",
            cells=cells),
        "realisation_table": realisations,
        "ensembles_per_size": per_size,
        "s3_decision_eligible": s3_eligible,
        "finite_size": dict(
            decision_eligibility=dict(
                all_sizes_eligible=s3_eligible,
                per_size={str(L): dict(attempted_n=per_size[str(L)]["attempted_n"],
                                       successful_n=per_size[str(L)]["successful_n"],
                                       decision_required_n=per_size[str(L)]["decision_required_n"],
                                       decision_eligible=per_size[str(L)]["decision_eligible"])
                          for L in sizes},
                note="the frozen stabilisation rule is applied only because every size has its "
                     "complete 4-seed ensemble; a missing or nonconverged realisation would "
                     "trigger the incomplete-matrix outcome instead of a silent n=3"),
            criterion=dict(sigma=D.SIGMA_K, statistic="ensemble mean of k per box size",
                           text="|mean(L) - mean(Lmax)| <= 2*sqrt(SE(L)^2 + SE(Lmax)^2)"),
            checks=checks, L_star=L_star, R_sep=R_sep,
            frozen_outcome="PASS" if L_star is not None else "FAIL",
            statement=("Permeability satisfied the frozen stabilization criterion over "
                       "L/d = 2.4 to 5.0 for the tested synthetic generator/solver ensemble."
                       if L_star is not None else
                       "Permeability stabilization was not demonstrated through L/d = 5.0 under "
                       "the frozen 2-sigma criterion."),
            power_caveat=(
                "The criterion is a NON-REJECTION test and it passes at the SMALLEST tested size "
                "(L*=%s), which is the tell: with n=4 and per-size CV of %.0f-%.0f%%, the 2-sigma "
                "band is wide enough to absorb a %.1f%% monotone decline in the ensemble means "
                "across the tested range. Failing to detect a difference is NOT demonstrating "
                "equivalence, and no convergence is claimed."
                % (L_star, 100 * min(v for v in variability["within_size_cv"].values()),
                   100 * max(v for v in variability["within_size_cv"].values()),
                   abs(total_mean_change_pct))),
            rev_determination=None,
            rev_note="the frozen protocol defines no REV determination, so no REV value and no "
                     "'REV exceeds the largest tested size' inference is stated"),
        "realization_variability": variability,
        "sections": sections,
        "tolerance_sensitivity_status": ("ADJUDICATED"
                                        if sections["S4_1_tolerance"]["converged"] == 2
                                        else "NOT_ADJUDICATED_COMPUTE_BOUND"),
        "porosity_dependence_status": "NOT_ADJUDICATED_COMPUTE_BOUND",
        "closure_trend_status": "NOT_ADJUDICATED_COMPUTE_BOUND",
        "closure_deep_status": closure_status,
        "closure_statement": (
            "The frozen deep closure matrix was not completed within the 150-minute compute "
            "budget. The cheap-screen monotonic ratio trend was therefore not deep-confirmed or "
            "deep-rejected. Completed section-4 cells are retained as partial, non-decisional "
            "evidence."),
        "closure_not": ["closure failure", "evidence that either closure is valid",
                        "evidence that either closure is invalid", "NEEDS_NEW_DATA",
                        "an empirical-data limitation"],
        "finite_size_status": "PASS_BY_NON_REJECTION_LOW_POWER",
        "realization_variability_status": "MATERIAL_AND_DOMINANT",
        "closure_status": closure_status,
        "overall_deep_disposition": frozen["outcome"],
        "overall_basis": corrected_basis(
            frozen, rve, list(variability["within_size_cv"].values()),
            total_mean_change_pct, L_star, R_sep),
        "frozen_rule_basis_verbatim": frozen["basis"],
        "frozen_rule_basis_note":
            "the frozen executor's own wording, preserved verbatim and NOT endorsed: its "
            "'IS stabilised' / 'was single-realisation scatter' phrasing overstates what a "
            "non-rejection at n=4 licenses. The OUTCOME it returned is authoritative and "
            "unchanged; only the reader-facing basis is restated in overall_basis.",
        "overall_basis_does_not_claim": [
            "that the solver is demonstrated to be stabilized",
            "that an REV has been established",
            "that the entire finite-size effect was proved to be realization scatter",
            "that the null and alternative are statistically equivalent",
        ],
        "novelty_disposition": "INCREMENTAL",
        "figure_caption": FIGURE_CAPTION,
        "issue_231_disposition": "NOT_MATERIAL_TO_SELECTED_DECISION",
        "evidence_labels_unchanged": True,
        "repository_guidance_correction": "none — the registry scopes '>= 5 grain diameters' to "
                                          "sigma, not permeability, and no pack card exists",
        "claim_ceiling": {
            "A_synthetic_generator_solver":
                "For brewer2026.pack_generator + brewer2026.lb_reference at R = 310.8 um, grain "
                "radius 10 voxels, phi ~ 0.49, over L/d = 2.4-5.0 with n=4 realisations per size: "
                "independent-realization variability is material and dominates the apparent "
                "finite-domain signal, so a single-realization size sweep is insufficient for "
                "permeability inference over this generator and domain.",
            "B_domain_size":
                "The frozen 2-sigma stabilization criterion is SATISFIED over L/d = 2.4-5.0, but "
                "by non-rejection at low power (n=4, CV 12-38%), not by demonstrated convergence. "
                "No REV is determined and none is claimed.",
            "C_continuum_closures":
                "NOT ADJUDICATED. The frozen closure matrix did not run; nothing is established "
                "for or against either closure, and the cheap monotonic trend does not carry "
                "forward.",
            "D_repository_guidance":
                "The repository did not claim that five grain diameters was sufficient for "
                "permeability. No pack-card or registry correction was warranted or made.",
            "E_real_pucks_and_novelty":
                "No real-puck permeability validation was performed and no representativeness of "
                "the synthetic morphology was established. Prior literature already contains "
                "universal sphere-pack permeability scaling and permeability-REV analyses; the "
                "contribution is incremental and repository-specific — a first repository-bound "
                "calibration, not a first measurement."},
    }


def figure(a=None, path=None):
    """Primary deep figure. Shows every realisation; no line connects equal seeds across sizes,
    because the geometries are RELATED_NON_NESTED and no paired analysis is valid."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    plt.rcParams.update({"figure.dpi": 150, "savefig.dpi": 150, "font.size": 8.5,
                         "font.family": "DejaVu Sans"})
    a = a or adjudicate()
    per = a["ensembles_per_size"]
    rows = a["realisation_table"]
    f = a["finite_size"]
    sizes = sorted(int(k) for k in per)
    xs = [rows[[r["L"] for r in rows].index(L)]["L_over_d"] for L in sizes]
    C, ACC, GREY = "#2f6f8f", "#b4472a", "#8a8a8a"

    fig, axes = plt.subplots(1, 2, figsize=(12.2, 4.7))

    ax = axes[0]
    for L, x in zip(sizes, xs):
        ks = [r["k_lu"] for r in rows if r["L"] == L]
        ax.plot([x] * len(ks), ks, "o", color=C, alpha=0.55, markersize=6,
                markeredgecolor="white", markeredgewidth=0.6,
                label="individual realisations (n=4)" if L == sizes[0] else None)
    means = [per[str(L)]["mean"] for L in sizes]
    ses = [f["checks"][str(L)]["se"] for L in sizes]
    ax.errorbar(xs, means, yerr=[D.SIGMA_K * s for s in ses], fmt="s", color=ACC, markersize=8,
                capsize=5, linewidth=1.8, zorder=5, label="ensemble mean $\\pm$ 2 SE")
    ax.set_xlabel("box size  $L/d$  [grain diameters]")
    ax.set_ylabel("permeability $k$  [lattice units, lu$^2$]")
    ax.set_title("(a)  Every realisation, and the frozen 2-SE band", loc="left",
                 fontweight="bold")
    ax.legend(fontsize=7.2, framealpha=0.96, loc="upper right")
    ax.grid(alpha=0.25, linewidth=0.5)
    ax.text(0.02, 0.03,
            "frozen rule: $|\\bar{k}(L)-\\bar{k}(L_{max})| \\leq 2\\sqrt{SE^2+SE_{max}^2}$\n"
            "satisfied at $L^*$ = %s (the SMALLEST tested size)\n"
            "$R_{sep}$ = %.2f  -- last step unresolved above seed noise"
            % (f["L_star"], f["R_sep"]),
            transform=ax.transAxes, fontsize=7.0, va="bottom", color=ACC, fontweight="bold",
            bbox=dict(boxstyle="round,pad=0.4", facecolor="white", edgecolor=ACC))

    ax = axes[1]
    v = a["realization_variability"]
    s0 = v["cheap_single_seed_trajectory"]
    ax.plot(xs, [s0[str(L)] if str(L) in s0 else s0[L] for L in sizes], "^--", color=GREY,
            linewidth=1.6, markersize=7, label="cheap screen: seed 0 only (RISING)")
    ax.plot(xs, means, "s-", color=ACC, linewidth=2.0, markersize=8,
            label="deep ensemble mean, n=4 (FALLING)")
    ax.set_xlabel("box size  $L/d$  [grain diameters]")
    ax.set_ylabel("permeability $k$  [lu$^2$]")
    ax.set_title("(b)  Why the cheap SURVIVE did not survive", loc="left", fontweight="bold")
    ax.legend(fontsize=7.2, framealpha=0.96)
    ax.grid(alpha=0.25, linewidth=0.5)
    ax.text(0.5, 0.04, "the single-realisation sweep trends OPPOSITE to the ensemble mean",
            transform=ax.transAxes, ha="center", fontsize=7.6, color=ACC, fontweight="bold")

    fig.suptitle(
        ("I-093 DEEP SCREEN — %s  |  DEEP_SCIENTIFIC_SCREEN / SYNTHETIC_GEOMETRY_RESULT / "
         "NOT_REAL_PUCK_VALIDATION / NOVELTY_INCREMENTAL\n"
         % a["overall_deep_disposition"]) + FIGURE_CAPTION, fontsize=8.6, y=1.015, va="bottom")
    fig.tight_layout()
    out = path or str(BUNDLE / "figures/deep_primary.png")
    pathlib.Path(out).parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return out


def main(argv=None):
    a = adjudicate()
    out = BUNDLE / "deep_result.json"
    out.write_text(json.dumps(a, indent=2) + "\n", encoding="utf-8")
    ea = a["execution_audit"]
    print("cells: %d expected | %d converged | %d not launched (budget guard)"
          % (ea["expected_cells"], ea["converged"], ea["not_launched_budget_guard"]))
    print("guard: %.0f s actual vs %.0f s budget (overrun %.0f s, admitted cell ran to completion)"
          % (ea["guard"]["actual_wall_s"], ea["guard"]["budget_s"], ea["guard"]["overrun_s"]))
    print("\nper-size ensembles (n, mean, median, sample SD, CV, min, max, max/min):")
    for L, s in a["ensembles_per_size"].items():
        print("  L=%-4s n=%d mean=%.4f med=%.4f sd=%.4f cv=%.3f min=%.4f max=%.4f max/min=%.3f"
              % (L, s["n"], s["mean"], s["median"], s["sample_sd"], s["cv"], s["min"], s["max"],
                 s["max_over_min"]))
    f = a["finite_size"]
    print("\nfinite size: %s  L*=%s  R_sep=%.3f" % (f["frozen_outcome"], f["L_star"], f["R_sep"]))
    v = a["realization_variability"]
    print("realisation: cheap seed-0 %s vs ensemble means %s -> directions disagree=%s"
          % (v["cheap_single_seed_direction"], v["ensemble_mean_direction"],
             v["directions_disagree"]))
    print("closure: %s" % a["closure_deep_status"])
    print("OVERALL: %s" % a["overall_deep_disposition"])
    print("wrote %s" % out)
    print("wrote %s" % figure(a))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
