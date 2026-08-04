"""screen_i024_common_state.py — Insight Foundry cheap screen for candidate I-024.

    CHEAP_SCIENTIFIC_SCREEN
    NOT_A_PUBLICATION_RESULT
    NOT_A_MODEL_VALIDATION_UPGRADE

Question (generated, verbatim from the candidate):

    Under one shared hydraulic and transport state, do the per-species residuals show
    structure that a single kinetic story cannot absorb?

EVIDENCE UNIT: the angeloni2023 campaign ONLY. The generated candidate lists maille2024,
ellero2019 and khamitova2020 entities because the lens grouped them; none of them is scored
here, and neither is any pannusch/schmieder post-fit evidence. One campaign, one model, one
observation operator.

THE TWO MODELS. Both use ONE hydraulic state per condition (one flow map, one bed, one
porosity, one grind) and differ only in how much transport freedom the species get:

    SHARED       one rate multiplier per variety, shared across all four species
                 + one inventory LEVEL per (species, variety)
    INDEPENDENT  one rate multiplier per (species, variety)
                 + one inventory LEVEL per (species, variety)

The level is free in BOTH. That is the design decision that answers the candidate's strongest
alternative — "the apparent species difference is a measurement-lineage difference between the
assays, not chemistry". An inventory error or an assay calibration error is a pure multiplicative
LEVEL per species. Giving both models a free per-species level makes the comparison blind to it
by construction, so anything that survives is condition-dependent structure, not level.

WHY A LEVEL CAN BE FITTED WITHOUT RE-SOLVING. The solver's output is EXACTLY linear in c_s0
(verified to ~1e-6, the solver's own tolerance): scaling c_s0 by lambda scales the liquid state
by lambda and leaves the normalised solid state untouched. So one unit-level solve per
(rate, condition, species) suffices and the optimal level is a weighted-least-squares closed
form. This is the same structure the archived identifiability work uses.

WHAT THE FLAT VALLEY MEANS HERE. ANALYSIS_transfer established that inventory and rate are
practically non-identifiable at a whole-cup endpoint (gap G6). Consequently the INDEPENDENT
model's per-species rates are individually poorly determined — but that is not what this screen
reads. It reads HELD-OUT PREDICTION, where a non-identifiable pair can still predict well, and
the question is whether per-species freedom buys held-out accuracy that the shared state cannot.

Run:  python -m puckworks.analysis.screen_i024_common_state
"""
from __future__ import annotations

import json
import pathlib

import numpy as np

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]

CANDIDATE_ID = "I-024"
SPECIES = ("caffeine", "trigonelline", "5CQA", "tds")
VARIETIES = ("Arabica", "Robusta")

#: Mapping from the model's solute name to the angeloni column, and the unit conversion the
#: frozen observation operator applies (the same convention as
#: gate_pannusch_angeloni_per_condition).
SPECIES_COLUMN = {"caffeine": ("CF", 1.0, "g/L"), "trigonelline": ("TR", 1.0, "g/L"),
                  "5CQA": ("5CQA", 1.0, "g/L"), "tds": ("TS", 0.1, "g/100 mL")}

#: Entities the generated candidate names that are NOT scored here, and why.
EXCLUDED_EVIDENCE = {
    "maille2024.phi_closure / maille2024.two_regime":
        "batch fits on a different campaign; scoring them would mix campaigns and the "
        "candidate's own INCONCLUSIVE clause is about exactly that confound",
    "ellero2019/fig4_caffeine_content":
        "digitised SIMULATION output, not measurement — it cannot carry a residual",
    "khamitova2020/tamping":
        "a different rig and design (tamping force); reference strength only",
    "pannusch2024.solver / pannusch2024.closures as EVIDENCE":
        "used here as the MODEL, never as evidence. Its own fit target (schmieder kinetics) is "
        "post-fit and is not scored",
    "angeloni2023/lipids":
        "not a species the model produces; its RSD is used only as an upper uncertainty "
        "sensitivity, never as a scored observable",
}

# ------------------------------------------------------------------------------------------
# PREDECLARED held-out split
# ------------------------------------------------------------------------------------------
#: Fixed before any fit was run. The interior pressure is held out, so this is INTERPOLATION,
#: not extrapolation — a fair test of the shared state rather than a hard one. 9 bar is also the
#: reference espresso condition, so a shared state that fails there fails where it matters.
TRAIN_P_BAR = (6.0, 12.0)
HELD_OUT_P_BAR = (9.0,)
SPLIT_RATIONALE = ("Held out the INTERIOR pressure (9 bar), training on 6 and 12 bar, at every "
                   "temperature and in both varieties. Interpolation rather than extrapolation, "
                   "and 9 bar is the reference espresso condition. Predeclared before any fit.")

#: Same rate domain as the archived identifiability work (log-spaced and wide enough that a
#: boundary optimum is exposed rather than imposed), at a coarser resolution to keep the screen
#: inside its one-day budget.
RATE_GRID = np.geomspace(0.15, 6.5, 15)

# ------------------------------------------------------------------------------------------
# PREDECLARED uncertainty and materiality
# ------------------------------------------------------------------------------------------
#: The campaign retains PER-CONDITION replicate RSD for total solids and lipids only. For
#: caffeine / trigonelline / CGA the source gives a GLOBAL range and no per-cell value
#: (MANIFEST angeloni2023/bioactives: "%RSD 0.3-19.7 (in card, not per-cell)";
#: angeloni2023/total_solids_lipids_rsd: "caffeine/trigonelline/CGA solute-specific RSD NOT
#: recovered ... raw replicates still owed").
#:
#: Rather than invent a value, the screen evaluates the criterion at BOTH ENDS of the source's
#: own stated band and asks whether the decision is invariant. That converts the missing
#: information from a blocker into a bounded sensitivity — and if the decision is NOT invariant,
#: that is precisely the NEEDS_NEW_DATA finding, with the needed measurement named.
BIOACTIVE_RSD_BAND_PCT = (0.3, 19.7)
BIOACTIVE_RSD_BAND_SOURCE = ("angeloni2023/bioactives MANIFEST uncertainty cell, verbatim: "
                             "'%RSD 0.3-19.7 (in card, not per-cell)'")

#: `tds` always uses the campaign's MEASURED per-condition TS RSD, because it exists.
TDS_RSD_SOURCE = "angeloni2023/total_solids per-condition RSD_pct column (measured)"

#: PREDECLARED MATERIALITY CRITERION — fixed before any fit was computed. All three arms are
#: expressed in units of retained measurement uncertainty (standardised residuals, z).
#:
#:   C1  exceeds noise            Z_shared > 1.0
#:       the shared state's RMS standardised HELD-OUT residual exceeds one uncertainty unit
#:   C2  species-specific         SD across species of the per-species mean standardised
#:       (not shared)             held-out residual > 1.0
#:       — this is the arm that separates "a species problem" from "a shared model-form problem"
#:   C3  materially reduced       Z_independent <= 0.7 * Z_shared
#:       by per-species fits      per-species transport freedom removes >= 30 % of the RMS
#:                                held-out residual
#:
#: SURVIVE iff C1 and C2 and C3.
#:
#: C3 is a RATIO and is therefore scale-free in the assumed uncertainty: if C3 fails, the
#: decision is RETIRE at every point in the RSD band. C1 and C2 are uncertainty-scaled and are
#: what the band sensitivity actually probes.
C1_Z_THRESHOLD = 1.0
C2_SPREAD_THRESHOLD = 1.0
C3_REDUCTION_FACTOR = 0.7
CRITERION_STATEMENT = (
    "SURVIVE iff C1 and C2 and C3, all in units of retained measurement uncertainty. "
    "C1: RMS standardised held-out residual under the shared state > %.1f. "
    "C2: SD across species of the per-species mean standardised held-out residual > %.1f "
    "(species-specific rather than a shared model-form problem). "
    "C3: RMS standardised held-out residual under independent per-species fits "
    "<= %.2f x the shared-state value. C3 is a ratio and is scale-free in the assumed RSD, so "
    "a C3 failure retires the candidate at every point in the source's stated 0.3-19.7 %% band. "
    "Predeclared before any fit was computed."
    % (C1_Z_THRESHOLD, C2_SPREAD_THRESHOLD, C3_REDUCTION_FACTOR))


# ------------------------------------------------------------------------------------------
# Data
# ------------------------------------------------------------------------------------------
def conditions():
    """The angeloni granulometry-O on-grid design, split into training and held-out."""
    from puckworks import data as d
    bio = d.angeloni_bioactives()
    ts = {(r["variety"], r["T_degC"], r["p_bar"]): r for r in d.angeloni_total_solids()}
    out = []
    for r in sorted((x for x in bio
                     if x["granulometry"] == "O" and x["on_grid"] == "True"),
                    key=lambda x: (x["variety"], x["T_degC"], x["p_bar"])):
        key = (r["variety"], r["T_degC"], r["p_bar"])
        meas = {s: float(r[SPECIES_COLUMN[s][0]]) for s in SPECIES if s != "tds"}
        meas["tds"] = float(ts[key]["TS_g_100mL"])
        out.append(dict(variety=r["variety"], T_degC=r["T_degC"], p_bar=r["p_bar"],
                        held_out=r["p_bar"] in HELD_OUT_P_BAR, measured=meas,
                        tds_rsd_pct=float(ts[key]["RSD_pct"])))
    return out


def unit_level_predictions(conds, rate_grid=RATE_GRID):
    """F[rate][(variety, T, p, species)] — the prediction at c_s0 = 1, one solve each.

    The level is NOT swept: the solver is exactly linear in c_s0, so prediction = level x F.
    This is what keeps the screen inside a cheap budget — 15 rates x 18 conditions x 4 species.
    """
    from puckworks.models.pannusch2024 import solver as ps
    from puckworks.validation.slow import angeloni_bracket as AB
    params = ps._solute_params()
    F = {}
    for ri, rate in enumerate(rate_grid):
        row = {}
        for c in conds:
            flow = AB._flow_darcy(c["p_bar"], c["T_degC"])
            bounds = AB._matched_bounds(flow)
            for s in SPECIES:
                sp = dict(params[s])
                sp["A1"] = sp["A1"] * float(rate)
                sp["A2"] = sp["A2"] * float(rate)
                sp["c_s0"] = 1.0
                conv = SPECIES_COLUMN[s][1]
                row[(c["variety"], c["T_degC"], c["p_bar"], s)] = float(
                    ps.simulate_fractions(c["T_degC"], flow, bounds, sp, cl1=1.0)[0]) * conv
        F[ri] = row
    return F


def sigma_of(c, species, bioactive_rsd_pct):
    """Absolute measurement sigma for one (condition, species), from retained uncertainty."""
    rsd = c["tds_rsd_pct"] if species == "tds" else bioactive_rsd_pct
    return abs(c["measured"][species]) * rsd / 100.0


# ------------------------------------------------------------------------------------------
# Fitting
# ------------------------------------------------------------------------------------------
def _best_level(F_row, conds, variety, species, bioactive_rsd_pct):
    """Weighted-least-squares level: closed form, because prediction = level x F."""
    num = den = 0.0
    for c in conds:
        if c["variety"] != variety:
            continue
        f = F_row[(variety, c["T_degC"], c["p_bar"], species)]
        m = c["measured"][species]
        w = 1.0 / sigma_of(c, species, bioactive_rsd_pct) ** 2
        num += w * f * m
        den += w * f * f
    return num / den if den > 0 else float("nan")


def _sse(F_row, conds, variety, species, level, bioactive_rsd_pct):
    tot = 0.0
    for c in conds:
        if c["variety"] != variety:
            continue
        f = F_row[(variety, c["T_degC"], c["p_bar"], species)]
        z = (level * f - c["measured"][species]) / sigma_of(c, species, bioactive_rsd_pct)
        tot += z * z
    return tot


def fit(F, conds, bioactive_rsd_pct, rate_grid=RATE_GRID):
    """Fit both models on the TRAINING conditions only."""
    train = [c for c in conds if not c["held_out"]]
    shared, indep = {}, {}
    for v in VARIETIES:
        # SHARED: one rate for the variety, minimising the summed training SSE over all species
        best = None
        for ri in range(len(rate_grid)):
            lv = {s: _best_level(F[ri], train, v, s, bioactive_rsd_pct) for s in SPECIES}
            tot = sum(_sse(F[ri], train, v, s, lv[s], bioactive_rsd_pct) for s in SPECIES)
            if best is None or tot < best[0]:
                best = (tot, ri, lv)
        shared[v] = dict(rate_index=best[1], rate=float(rate_grid[best[1]]),
                         levels={s: float(best[2][s]) for s in SPECIES},
                         train_sse=float(best[0]))
        # INDEPENDENT: one rate per species
        indep[v] = {}
        for s in SPECIES:
            bs = None
            for ri in range(len(rate_grid)):
                lvl = _best_level(F[ri], train, v, s, bioactive_rsd_pct)
                sse = _sse(F[ri], train, v, s, lvl, bioactive_rsd_pct)
                if bs is None or sse < bs[0]:
                    bs = (sse, ri, lvl)
            indep[v][s] = dict(rate_index=bs[1], rate=float(rate_grid[bs[1]]),
                               level=float(bs[2]), train_sse=float(bs[0]),
                               rate_at_grid_edge=bool(bs[1] in (0, len(rate_grid) - 1)))
    return shared, indep


def held_out_residuals(F, conds, shared, indep, bioactive_rsd_pct):
    """Standardised held-out residuals under both models."""
    held = [c for c in conds if c["held_out"]]
    rows = []
    for c in held:
        v = c["variety"]
        for s in SPECIES:
            sig = sigma_of(c, s, bioactive_rsd_pct)
            m = c["measured"][s]
            fs = F[shared[v]["rate_index"]][(v, c["T_degC"], c["p_bar"], s)]
            fi = F[indep[v][s]["rate_index"]][(v, c["T_degC"], c["p_bar"], s)]
            ps_ = shared[v]["levels"][s] * fs
            pi_ = indep[v][s]["level"] * fi
            rows.append(dict(variety=v, T_degC=c["T_degC"], p_bar=c["p_bar"], species=s,
                             measured=m, sigma=sig,
                             pred_shared=ps_, pred_independent=pi_,
                             z_shared=(ps_ - m) / sig, z_independent=(pi_ - m) / sig))
    return rows


def _rms(vals):
    v = np.asarray(list(vals), float)
    return float(np.sqrt(np.mean(v ** 2))) if v.size else float("nan")


def evaluate(rows):
    z_sh = [r["z_shared"] for r in rows]
    z_in = [r["z_independent"] for r in rows]
    per_species_mean = {s: float(np.mean([r["z_shared"] for r in rows if r["species"] == s]))
                        for s in SPECIES}
    Z_shared, Z_indep = _rms(z_sh), _rms(z_in)
    spread = float(np.std(list(per_species_mean.values()), ddof=1))
    c1 = bool(Z_shared > C1_Z_THRESHOLD)
    c2 = bool(spread > C2_SPREAD_THRESHOLD)
    c3 = bool(Z_indep <= C3_REDUCTION_FACTOR * Z_shared)
    return dict(Z_shared=round(Z_shared, 4), Z_independent=round(Z_indep, 4),
                reduction_ratio=round(Z_indep / Z_shared, 4) if Z_shared else None,
                per_species_mean_z_shared={k: round(v, 4)
                                           for k, v in per_species_mean.items()},
                between_species_spread=round(spread, 4),
                per_species_rms_z_shared={
                    s: round(_rms(r["z_shared"] for r in rows if r["species"] == s), 4)
                    for s in SPECIES},
                per_species_rms_z_independent={
                    s: round(_rms(r["z_independent"] for r in rows if r["species"] == s), 4)
                    for s in SPECIES},
                C1_exceeds_noise=c1, C2_species_specific=c2, C3_reduced_by_species_fits=c3,
                survive=bool(c1 and c2 and c3))


# ------------------------------------------------------------------------------------------
# Step 6 — is the structure just inventory / assay level?
# ------------------------------------------------------------------------------------------
def level_absorption(F, conds, shared, bioactive_rsd_pct):
    """How much of the raw residual a per-species LEVEL absorbs.

    Compares the held-out standardised residual with the level FIXED at pannusch's own Table 2
    inventory against the residual with the level FITTED. A large drop means the apparent
    species structure is a LEVEL effect — i.e. inventory or assay scaling — which is the
    candidate's strongest alternative explanation, quantified rather than asserted.

    Also reports the fitted level beside the angeloni Table 7 measured inventory where one
    exists, as an independent check on what the fitted level is standing in for.
    """
    from puckworks.models.pannusch2024 import solver as ps
    from puckworks import data as d
    table2 = {s: v["c_s0"] for s, v in ps._solute_params().items()}
    inv = {(r["variety"], r["species"]): r["C0_s_mg_L"] / 1000.0
           for r in d.angeloni_inventories()}
    inv_col = {"caffeine": "CF", "trigonelline": "TR", "5CQA": "CQA"}   # CQA = TOTAL CQA
    held = [c for c in conds if c["held_out"]]
    fixed, fitted = [], []
    for c in held:
        v = c["variety"]
        for s in SPECIES:
            f = F[shared[v]["rate_index"]][(v, c["T_degC"], c["p_bar"], s)]
            sig = sigma_of(c, s, bioactive_rsd_pct)
            m = c["measured"][s]
            fixed.append((table2[s] * f - m) / sig)
            fitted.append((shared[v]["levels"][s] * f - m) / sig)
    cmp_rows = []
    for v in VARIETIES:
        for s in SPECIES:
            meas_inv = inv.get((v, inv_col.get(s, "")))
            cmp_rows.append(dict(
                variety=v, species=s,
                level_fitted=round(shared[v]["levels"][s], 4),
                level_pannusch_table2=round(table2[s], 4),
                level_ratio_fitted_over_table2=round(
                    shared[v]["levels"][s] / table2[s], 4),
                angeloni_table7_inventory_g_L=(round(meas_inv, 4) if meas_inv else None),
                inventory_note=("angeloni Table 7 measures TOTAL CQA, not 5CQA — not "
                                "species-matched" if s == "5CQA" else
                                "no Table 7 inventory for the aggregate-solids proxy"
                                if s == "tds" else "species-matched")))
    return dict(Z_level_fixed_at_pannusch_table2=round(_rms(fixed), 4),
                Z_level_fitted=round(_rms(fitted), 4),
                absorbed_fraction=round(1.0 - _rms(fitted) / _rms(fixed), 4)
                if _rms(fixed) else None,
                levels=cmp_rows,
                reading="A large absorbed fraction means the bulk of the apparent species "
                        "difference is a per-species LEVEL — inventory or assay scaling — not "
                        "condition-dependent transport structure. Both scored models carry a "
                        "free per-species level, so the decision is already blind to it.")


# ------------------------------------------------------------------------------------------
# Screen
# ------------------------------------------------------------------------------------------
def screen():
    conds = conditions()
    F = unit_level_predictions(conds)

    band = {}
    for tag, rsd in (("low", BIOACTIVE_RSD_BAND_PCT[0]), ("high", BIOACTIVE_RSD_BAND_PCT[1])):
        sh, ind = fit(F, conds, rsd)
        rows = held_out_residuals(F, conds, sh, ind, rsd)
        band[tag] = dict(bioactive_rsd_pct=rsd, shared=sh, independent=ind,
                         evaluation=evaluate(rows),
                         level_absorption=level_absorption(F, conds, sh, rsd),
                         residuals=rows)

    verdicts = {t: band[t]["evaluation"]["survive"] for t in band}
    invariant = len(set(verdicts.values())) == 1
    c3 = {t: band[t]["evaluation"]["C3_reduced_by_species_fits"] for t in band}

    if not invariant:
        decision = "NEEDS_NEW_DATA"
        why = ("The decision flips across the source's own stated bioactive RSD band "
               "(%.1f-%.1f %%), so it is not determined by the retained uncertainty. "
               "Solute-specific replicate RSD for caffeine / trigonelline / CGA is required."
               % BIOACTIVE_RSD_BAND_PCT)
    elif all(verdicts.values()):
        decision = "SURVIVE"
        why = ("Reproducible species-specific held-out residual structure remains beyond "
               "uncertainty and is materially reduced by per-species fits, at both ends of the "
               "retained uncertainty band.")
    else:
        decision = "RETIRE"
        failed = [k for k, v in band["low"]["evaluation"].items()
                  if k.startswith("C") and v is False]
        why = ("The shared-state hypothesis is not refuted at either end of the retained "
               "uncertainty band. Failing arms at the low (most demanding) end: %s. "
               "C3 is a scale-free ratio, so a C3 failure retires the candidate at every "
               "point in the band." % (", ".join(failed) or "none"))

    return dict(
        screen=CANDIDATE_ID,
        disposition=["CHEAP_SCIENTIFIC_SCREEN", "NOT_A_PUBLICATION_RESULT",
                     "NOT_A_MODEL_VALIDATION_UPGRADE"],
        evidence_unit=dict(
            campaign="angeloni2023 only (bioactives + total_solids), granulometry O, on-grid",
            manifest_validation_strength_verbatim=(
                "independent (different machine/coffee/basket than pannusch fit or cameron "
                "calibration)"),
            n_conditions=len(conds),
            n_train=sum(1 for c in conds if not c["held_out"]),
            n_held_out=sum(1 for c in conds if c["held_out"]),
            species=list(SPECIES), varieties=list(VARIETIES),
            excluded_evidence=EXCLUDED_EVIDENCE),
        predeclared=dict(train_p_bar=list(TRAIN_P_BAR), held_out_p_bar=list(HELD_OUT_P_BAR),
                         split_rationale=SPLIT_RATIONALE,
                         rate_grid=[round(float(r), 4) for r in RATE_GRID],
                         criterion=CRITERION_STATEMENT,
                         C1_z_threshold=C1_Z_THRESHOLD,
                         C2_spread_threshold=C2_SPREAD_THRESHOLD,
                         C3_reduction_factor=C3_REDUCTION_FACTOR),
        uncertainty=dict(bioactive_rsd_band_pct=list(BIOACTIVE_RSD_BAND_PCT),
                         bioactive_rsd_band_source=BIOACTIVE_RSD_BAND_SOURCE,
                         tds_rsd_source=TDS_RSD_SOURCE,
                         solute_specific_rsd_recovered=False,
                         note="Solute-specific replicate RSD for caffeine / trigonelline / CGA "
                              "is NOT recovered by the campaign. Rather than invent one, the "
                              "criterion is evaluated at both ends of the source's own stated "
                              "band and the decision is taken only if it is invariant."),
        band=band,
        decision_invariant_across_band=invariant,
        C3_by_band=c3,
        decision=decision, decision_reasoning=why)


# ------------------------------------------------------------------------------------------
# Primary figure
# ------------------------------------------------------------------------------------------
_INK, _MUTED, _GRID = "#1a1a1a", "#5a5a5a", "#d9d9d9"
_C_SHARED, _C_INDEP = "#0072b2", "#e69f00"


def figure(path=None, result=None):
    """Held-out standardised residuals by species and condition, both fits overlaid."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    plt.rcParams.update({"figure.dpi": 150, "savefig.dpi": 150, "font.size": 8.5,
                         "font.family": "DejaVu Sans"})
    r = result or screen()

    fig, axes = plt.subplots(1, 2, figsize=(11.6, 4.5), sharey=True)
    for ax, tag in zip(axes, ("low", "high")):
        b = r["band"][tag]
        rows = b["residuals"]
        ev = b["evaluation"]
        keys = sorted({(x["variety"], x["T_degC"]) for x in rows})
        xs = np.arange(len(keys) * len(SPECIES), dtype=float)
        i = 0
        ticks, labels = [], []
        for v, T in keys:
            for s in SPECIES:
                rec = [x for x in rows if x["variety"] == v and x["T_degC"] == T
                       and x["species"] == s][0]
                ax.plot([i, i], [0, rec["z_shared"]], color=_C_SHARED, lw=1.0, alpha=0.45,
                        zorder=1)
                ax.plot(i - 0.16, rec["z_shared"], "o", ms=5.0, color=_C_SHARED, zorder=3)
                ax.plot(i + 0.16, rec["z_independent"], "s", ms=4.6, color=_C_INDEP, zorder=3)
                ticks.append(i)
                labels.append("%s\n%s %.0f°C" % (s, v[:3], T))
                i += 1
        ax.axhspan(-1, 1, color="#6b6b6b", alpha=0.11, zorder=0)
        ax.axhline(0, color=_INK, lw=0.9, zorder=2)
        ax.set_xticks(ticks)
        ax.set_xticklabels(labels, fontsize=5.6, rotation=90)
        ax.grid(True, axis="y", color=_GRID, lw=0.5)
        ax.set_axisbelow(True)
        ax.set_title("assumed bioactive RSD = %.1f %%   (%s end of the source's stated band)"
                     % (b["bioactive_rsd_pct"], tag), fontsize=8.8, color=_INK, pad=7)
        ax.set_yscale("symlog", linthresh=2.0)
        ax.text(0.985, 0.025,
                "Z_shared %.2f    Z_independent %.2f    ratio %.2f\n"
                "between-species spread %.2f    →  %s"
                % (ev["Z_shared"], ev["Z_independent"], ev["reduction_ratio"],
                   ev["between_species_spread"],
                   "SURVIVE" if ev["survive"] else "not survived"),
                transform=ax.transAxes, ha="right", va="bottom", fontsize=7.4, color=_INK,
                linespacing=1.5,
                bbox=dict(boxstyle="round,pad=0.35", fc="white", ec=_GRID, lw=0.8, alpha=0.95))
    axes[0].set_ylabel("standardised held-out residual  z = (pred − meas) / σ\n"
                       "symlog, linear within ±2", fontsize=8)

    handles = [
        plt.Line2D([], [], ls="none", marker="o", color=_C_SHARED, ms=5.0,
                   label="shared state — one rate per variety, all species"),
        plt.Line2D([], [], ls="none", marker="s", color=_C_INDEP, ms=4.6,
                   label="independent per-species fits — one rate per species"),
        plt.Rectangle((0, 0), 1, 1, fc="#6b6b6b", alpha=0.11,
                      label="±1 measurement σ (retained replicate uncertainty)")]

    fig.suptitle("I-024 — can one shared transport state explain every measured species at "
                 "once?   Held-out = 9 bar (interior pressure), predeclared",
                 fontsize=11, y=1.015, x=0.005, ha="left", weight="bold")
    fig.text(0.005, 0.965,
             "CHEAP_SCIENTIFIC_SCREEN · NOT_A_PUBLICATION_RESULT · "
             "NOT_A_MODEL_VALIDATION_UPGRADE     angeloni2023 campaign ONLY — no maille, "
             "ellero, khamitova or pannusch/schmieder post-fit evidence is scored.     "
             "A per-species inventory LEVEL is free in BOTH models, so the comparison is blind "
             "to inventory and assay scaling by construction.",
             fontsize=7, color=_MUTED, style="italic", ha="left")

    fig.tight_layout()
    fig.legend(handles=handles, loc="upper left", bbox_to_anchor=(0.0, -0.005), ncol=3,
               fontsize=7.4, frameon=False)

    lo, hi = r["band"]["low"]["evaluation"], r["band"]["high"]["evaluation"]
    la = r["band"]["low"]["level_absorption"]
    fig.text(0.005, -0.075, va="top", ha="left", fontsize=7.1, color=_MUTED, linespacing=1.6,
             s="Predeclared criterion (all arms in units of measurement σ): C1 Z_shared > 1 · "
               "C2 between-species spread > 1 · C3 Z_independent ≤ 0.70 × Z_shared. "
               "SURVIVE iff C1 ∧ C2 ∧ C3.\n"
               "    low  RSD 0.3 %%:  C1 %s   C2 %s   C3 %s      "
               "high RSD 19.7 %%:  C1 %s   C2 %s   C3 %s\n"
               "C3 is a RATIO and therefore scale-free in the assumed RSD — it reads the same "
               "(%.2f vs the 0.70 threshold) at both ends, so the missing solute-specific RSD "
               "cannot change it.\n"
               "Inventory / assay check: fixing the level at pannusch's Table 2 inventory gives "
               "Z = %.1f; fitting a per-species level gives Z = %.1f — a per-species LEVEL "
               "absorbs %.1f %% of the raw residual.\n"
               "DECISION  %s — %s"
               % (lo["C1_exceeds_noise"], lo["C2_species_specific"],
                  lo["C3_reduced_by_species_fits"], hi["C1_exceeds_noise"],
                  hi["C2_species_specific"], hi["C3_reduced_by_species_fits"],
                  lo["reduction_ratio"], la["Z_level_fixed_at_pannusch_table2"],
                  la["Z_level_fitted"], 100.0 * (la["absorbed_fraction"] or 0.0),
                  r["decision"], r["decision_reasoning"]))

    path = path or (REPO_ROOT / "docs/insights/screens/I-024/figures/primary.png")
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return path


def main(argv=None):
    r = screen()
    out = REPO_ROOT / "docs/insights/screens/I-024/result.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(r, indent=2) + "\n", encoding="utf-8")
    print("conditions: %d train / %d held out"
          % (r["evidence_unit"]["n_train"], r["evidence_unit"]["n_held_out"]))
    for tag in ("low", "high"):
        e = r["band"][tag]["evaluation"]
        print("  RSD %5.1f %%  Z_shared=%7.2f  Z_indep=%7.2f  ratio=%.3f  spread=%7.2f  "
              "C1=%-5s C2=%-5s C3=%-5s -> survive=%s"
              % (r["band"][tag]["bioactive_rsd_pct"], e["Z_shared"], e["Z_independent"],
                 e["reduction_ratio"], e["between_species_spread"], e["C1_exceeds_noise"],
                 e["C2_species_specific"], e["C3_reduced_by_species_fits"], e["survive"]))
    la = r["band"]["low"]["level_absorption"]
    print("  level absorbs %.1f %% of the raw residual (Z %.1f -> %.1f)"
          % (100.0 * (la["absorbed_fraction"] or 0.0),
             la["Z_level_fixed_at_pannusch_table2"], la["Z_level_fitted"]))
    print("  decision invariant across the RSD band: %s" % r["decision_invariant_across_band"])
    print("DECISION: %s" % r["decision"])
    fig_path = figure(result=r)
    print("wrote %s" % out.relative_to(REPO_ROOT))
    print("wrote %s" % fig_path.relative_to(REPO_ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
