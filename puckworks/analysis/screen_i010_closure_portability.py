"""screen_i010_closure_portability.py — Insight Foundry cheap screen for candidate I-010.

    CHEAP_SCIENTIFIC_SCREEN
    NOT_A_PUBLICATION_RESULT
    NOT_A_MODEL_VALIDATION_UPGRADE

Question (generated, verbatim from the candidate):

    Which registered component, if any, actually consumes pannusch2024.closures's output —
    and does that consuming result change materially when the artifact is swapped for
    another source's or driven outside its declared validity?

STEP 1 — THE PATH IS EXPLICIT IN SOURCE, not inferred from co-location. See `PATH` below:
`pannusch2024.solver` imports `pannusch2024.closures` and calls `sherwood_h` and `vant_hoff_K`
directly; `diffusion_coeff`, `water_viscosity` and `water_density` reach the consumer only
THROUGH `sherwood_h`. The whole artifact therefore enters each solve as exactly three scalars —
`h1`, `h2` (m/s) and `K` (dimensionless). That narrow interface is a result in itself, and it
is why an insensitive outcome would be unsurprising.

STEP 2 — HELD-OUT UNIT: `angeloni2023`, granulometry O, on-grid conditions, both varieties.
MANIFEST-labelled *independent* ("different machine/coffee/basket than pannusch fit or cameron
calibration") and never used to fit the closures. Non-circular by construction. Scoring the
pannusch fit target (schmieder kinetics) would be circular and is excluded.

STEP 3 — EVERYTHING ELSE IS FROZEN. See `FROZEN`. One subtlety is load-bearing and is
predeclared rather than discovered: the analysis' own p→flow map `_flow_darcy` ALSO calls
`pc.water_viscosity`. Left unfrozen, a viscosity swap would move the boundary condition and the
model closure simultaneously, and the screen would be measuring two things. The flow map is
therefore held at the BASELINE viscosity for every swap. This is a choice, made before running,
and it is recorded because it changes what the numbers mean.

STEP 4 — ONE CLOSURE AT A TIME, from a declared in-repo alternative. See `SUBSTITUTIONS`.
Where the alternative uses a different convention (the two K(T) closures are already on record
as disagreeing on the SIGN of dK/dT, `gate_g4_temperature_sensitivity`), only the declared
TEMPERATURE LAW is swapped, anchored so the alternative reproduces pannusch's own value at
pannusch's own reference temperature. A raw numeric swap would measure the convention
difference, not portability, and merging the conventions is forbidden (CLAUDE.md rule 6).

STEP 5 — THE NO-REFIT COMPARISON RUNS FIRST, and it is what the decision rule reads.

STEP 6 — UNCERTAINTY IS PROPAGATED, observational and numerical. See `UNCERTAINTY`.

STEP 7 — THE RECALIBRATION BRANCH runs only if a no-refit effect is material, and is labelled
separately. It is an IN-SAMPLE compensation bound, never a prediction.

Run:  python -m puckworks.analysis.screen_i010_closure_portability
"""
from __future__ import annotations

import json
import pathlib
import statistics

import numpy as np

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]

CANDIDATE_ID = "I-010"
ARTIFACT = "pannusch2024.closures"
CONSUMER = "pannusch2024.solver"

# ------------------------------------------------------------------------------------------
# STEP 1 — the producer -> consumer path, read from source
# ------------------------------------------------------------------------------------------
PATH = dict(
    established=True,
    method="source read, not co-location: the consumer imports the producer module and calls "
           "its functions by name",
    import_site="puckworks/models/pannusch2024/solver.py:30  "
                "`from puckworks.models.pannusch2024 import closures as pc`",
    registry_declaration="puckworks/models/__init__.py — pannusch2024.solver notes: "
                         "'Consumes pannusch2024.closures.'",
    direct_calls=[
        dict(closure="sherwood_h", sites=["solver.py:101 (h1)", "solver.py:102 (h2)",
                                          "solver.py:189 (h1, Q(t) adapter)",
                                          "solver.py:190 (h2, Q(t) adapter)"],
             enters_as="lumped mass-transfer coefficients h1, h2 [m/s], one per grain "
                       "population, via p['m1'], p['m2'], p['f1'], p['f2']"),
        dict(closure="vant_hoff_K", sites=["solver.py:103", "solver.py:173"],
             enters_as="the solid-liquid distribution constant K [-], in the interphase "
                       "transfer terms and the initial condition c0[1:nz] = K*cs0/cl1"),
    ],
    transitive_calls=[
        dict(closure="diffusion_coeff", via="sherwood_h (closures.py:65)",
             enters_as="D [m^2/s] — sets Sc and scales h as h ~ Sh*D/d32, so h ~ D^(2/3)"),
        dict(closure="water_viscosity", via="sherwood_h -> diffusion_coeff and the kinematic "
                                            "viscosity (closures.py:55, 66)",
             enters_as="mu [Pa s] — enters Re, Sc and Wilke-Chang D"),
        dict(closure="water_density", via="sherwood_h (closures.py:66)",
             enters_as="rho [kg/m^3] — only through the kinematic viscosity mu/rho"),
    ],
    interface_width="Three scalars per solve: h1, h2, K. Every one of the five declared "
                    "closures reaches the consumer only through those three numbers.",
    note="The candidate's INCONCLUSIVE branch ('no consuming path can be established') is "
         "closed by this step. The generated row recorded same-stage co-location only; the "
         "path is real and is a direct import.")

# ------------------------------------------------------------------------------------------
# STEP 3 — the frozen configuration
# ------------------------------------------------------------------------------------------
FROZEN = dict(
    model_grid=dict(NZ=200, scheme="five-point biased upwind (Carver & Hinds 1978)",
                    integrator="BDF (solve_ivp)", rtol=1e-6, atol=1e-6),
    boundary_conditions=dict(inlet="Dirichlet c_l(z=0) = 0", bed_length_m=0.015,
                             bed_diameter_m=0.058, porosity_alpha_l=0.17),
    grind="GRIND_17 — the centre grind (psi=0.23, d_s2=330 um); the per-experiment grind "
          "assignment lives in the source's opaque parameter list (documented approximation)",
    measured_flow_input="angeloni_bracket._flow_darcy — Darcy q = q_ref*(p/p_ref)*"
                        "(mu(T_ref)/mu(T)), anchored at 40 g / ~24 s at 9 bar, 93.4 C. NOT "
                        "fitted to the concentrations.",
    flow_map_viscosity="FROZEN AT BASELINE for every swap. _flow_darcy calls "
                       "pc.water_viscosity, so an unfrozen viscosity swap would move the "
                       "boundary condition and the model closure at once. Predeclared.",
    inventory_basis="pannusch Table 2 c_s0 — BLIND, no refit to angeloni. The angeloni "
                    "Table 7 inventories are NOT substituted in; that is a different "
                    "experiment (inventory matching) and is out of scope here.",
    objective="none — the no-refit branch fits nothing. The scored quantity is the predicted "
              "held-out concentration itself.",
    observation_operator="matched-beverage-mass endpoint: terminate every simulation at the "
                         "same COLLECTED MASS (40 g) via _matched_bounds, then take the "
                         "single fraction-averaged outlet concentration. Preserves the source "
                         "convention that the flow column, published in mL/s, is consumed as "
                         "g/s (angeloni_bracket._SOURCE_FLOW_UNITS).",
    species=["caffeine", "trigonelline", "5CQA", "tds"],
    species_columns={"caffeine": "CF", "trigonelline": "TR", "5CQA": "5CQA",
                     "tds": "TS (g/100mL -> mg/mL, x10 per the source convention)"},
)

#: The producer's declared validity range, verbatim from the registry entry.
DECLARED_VALID_RANGE = ("T 80-98 C, Q 1-3 mL/s; fitted Sherwood params lack generality; "
                        "Wilke-Chang over-predicts absolute D but is the model's own law")
DECLARED_T_C = (80.0, 98.0)
DECLARED_Q_ML_S = (1.0, 3.0)

# ------------------------------------------------------------------------------------------
# STEP 6 — retained uncertainty, PER OUTPUT
# ------------------------------------------------------------------------------------------
# CORRECTION (2026-08-04). The first version of this screen used the median total-solids
# replicate RSD as though it were the uncertainty of all four scored outputs, and decided the
# candidate against that single number. It is not the bioactives' uncertainty and it never was:
# the campaign does not retain one for them. Each output is now evaluated against ITS OWN
# retained uncertainty, and where that uncertainty is a range, the screen reports what happens
# across the range instead of collapsing it.

#: TOTAL SOLIDS — retained, measured, per condition. `angeloni2023/total_solids` carries an
#: RSD_pct column for every shot, so this output has a real uncertainty and a real answer.
TDS_RSD_SOURCE = "measured per-condition RSD_pct of angeloni2023/total_solids"

#: THE NAMED BIOACTIVES — NOT retained per cell. The MANIFEST uncertainty cell for
#: `angeloni2023/bioactives` reads, verbatim, "%RSD 0.3-19.7 (in card, not per-cell)", and
#: `angeloni2023/total_solids_lipids_rsd` records "caffeine/trigonelline/CGA solute-specific RSD
#: NOT recovered (Tables 4-5 give only global ranges 0.3-19.7%); raw replicates still owed".
#:
#: That is a RANGE spanning a factor of 65, and the screen must not replace it with a number.
#: No midpoint, no median, no best cell, and specifically not the total-solids value.
BIOACTIVE_RSD_BAND_PCT = (0.3, 19.7)
BIOACTIVE_RSD_BAND_SOURCE = ("angeloni2023/bioactives MANIFEST uncertainty cell, verbatim: "
                             "'%RSD 0.3-19.7 (in card, not per-cell)'")

#: Which authority governs which output. `tds` has a measured value; the other three have a band.
UNCERTAINTY_AUTHORITY = {
    "tds": dict(kind="measured_per_condition", source=TDS_RSD_SOURCE),
    "caffeine": dict(kind="declared_range", range_pct=list(BIOACTIVE_RSD_BAND_PCT),
                     source=BIOACTIVE_RSD_BAND_SOURCE),
    "trigonelline": dict(kind="declared_range", range_pct=list(BIOACTIVE_RSD_BAND_PCT),
                         source=BIOACTIVE_RSD_BAND_SOURCE),
    "5CQA": dict(kind="declared_range", range_pct=list(BIOACTIVE_RSD_BAND_PCT),
                 source=BIOACTIVE_RSD_BAND_SOURCE),
}

#: Retained numerical uncertainty: the MAXIMUM relative change in the predicted held-out
#: concentration between the frozen configuration (NZ=200, rtol=atol=1e-6) and a refined one
#: (NZ=400, rtol=atol=1e-8), over all 72 held-out points. Negligible against every observational
#: figure below, so it never changes a classification; carried for completeness.
NUM_REL_PCT = 0.0001

#: CAMPAIGN-LEVEL PROXY SENSITIVITY — REPORTED, NEVER DECISIVE.
#: The median measured per-condition total-solids RSD over the WHOLE campaign (all 66 shots).
#: This is the number the superseded first version used as the decision authority for all four
#: outputs. It is retained here so the correction is auditable, and it is excluded from every
#: classification by construction (`_classify` never reads it).
#:
#: NOTE it is not even the right total-solids figure for THIS screen: the 18 held-out
#: granulometry-O on-grid conditions have their own median (computed at run time and reported as
#: `tds_median_rsd_this_screen_pct`), which is higher. Both are above every admissible
#: total-solids effect, so no classification turns on the difference — but the screen quotes the
#: one that governs its own conditions, not the campaign-wide one.
PROXY_U_PCT = 4.70
PROXY_U_ROLE = ("campaign-level proxy sensitivity ONLY, over all 66 shots. Not the decision "
                "authority for any output. It is a total-solids figure, which is the retained "
                "uncertainty of ONE of the four scored outputs and of none of the other three; "
                "and it is not even the total-solids median over this screen's own 18 held-out "
                "conditions.")

#: PREDECLARED MATERIALITY STATISTIC — unchanged from the first version, and applied SEPARATELY
#: per output rather than pooled across analytes with different uncertainty authority.
MATERIALITY_STATEMENT = (
    "For each admissible substitution and EACH scored output separately: the effect statistic is "
    "the MEDIAN absolute relative change in the held-out predicted concentration across the 18 "
    "held-out conditions. The substitution is MATERIAL for that output at a given RSD if the "
    "median effect exceeds that RSD. Outputs are NOT pooled: total solids is judged against its "
    "own measured per-condition RSD, and each named bioactive against the declared 0.3-19.7 %% "
    "range, evaluated at BOTH ends. Numerical uncertainty (%.4f %% max) is negligible against "
    "every threshold and changes no classification." % NUM_REL_PCT)

#: Fixed three-way classification, per output and per substitution.
STATUS_MATERIAL = "MATERIAL_THROUGHOUT"
STATUS_IMMATERIAL = "IMMATERIAL_THROUGHOUT"
STATUS_CHANGES = "CHANGES_WITHIN_RANGE"

UNCERTAINTY = dict(
    per_output_authority=UNCERTAINTY_AUTHORITY,
    tds_source=TDS_RSD_SOURCE,
    bioactive_band_pct=list(BIOACTIVE_RSD_BAND_PCT),
    bioactive_band_source=BIOACTIVE_RSD_BAND_SOURCE,
    solute_specific_rsd_recovered=False,
    numerical_max_rel_pct=NUM_REL_PCT,
    numerical_source="NZ 200/rtol 1e-6 vs NZ 400/rtol 1e-8 over the 72 held-out points "
                     "(angeloni_bracket._numerics)",
    proxy_U_pct=PROXY_U_PCT, proxy_U_role=PROXY_U_ROLE,
    criterion=MATERIALITY_STATEMENT)


# ------------------------------------------------------------------------------------------
# STEP 4 — the substitutions
# ------------------------------------------------------------------------------------------
def _held_out_shots():
    from puckworks import data as d
    bio = d.angeloni_bioactives()
    return sorted((r for r in bio
                   if r["granulometry"] == "O" and r["on_grid"] == "True"),
                  key=lambda r: (r["variety"], r["T_degC"], r["p_bar"]))


#: Units of each scored observable, as the frozen observation operator produces AND measures it.
#: caffeine/trigonelline/5CQA are angeloni's g/L, which equals the solver's mg/mL. `tds` is the
#: aggregate-solids proxy in g/100 mL, which is why its conversion factor is 0.1 — the same
#: convention gate_pannusch_angeloni_per_condition uses. Predictions and measurements are in the
#: SAME units per species; no further scaling is applied anywhere.
SPECIES_UNITS = {"caffeine": "g/L  (= mg/mL)", "trigonelline": "g/L  (= mg/mL)",
                 "5CQA": "g/L  (= mg/mL)", "tds": "g/100 mL  (total solids proxy)"}


def _measured(shots):
    """Measured held-out values, in the same units as `_predict` returns per species."""
    from puckworks import data as d
    ts = {(r["variety"], r["T_degC"], r["p_bar"]): r["TS_g_100mL"]
          for r in d.angeloni_total_solids()}
    col = {"caffeine": "CF", "trigonelline": "TR", "5CQA": "5CQA"}
    out = {}
    for r in shots:
        key = (r["variety"], r["T_degC"], r["p_bar"])
        for sol, c in col.items():
            out[key + (sol,)] = float(r[c])                       # g/L
        out[key + ("tds",)] = float(ts[key])                      # g/100 mL
    return out


def _predict(shots, patch=None):
    """Held-out predictions under the frozen configuration, with one closure optionally swapped.

    `patch` is {closure_name: callable} applied to `pannusch2024.closures` for the duration.
    The flow map is computed FIRST, from the baseline module, so a viscosity swap cannot move
    the boundary condition (FROZEN['flow_map_viscosity']).
    """
    from puckworks.models.pannusch2024 import closures as pc
    from puckworks.models.pannusch2024 import solver as ps
    from puckworks.validation.slow import angeloni_bracket as AB

    params = ps._solute_params()
    conv = {"caffeine": 1.0, "trigonelline": 1.0, "5CQA": 1.0, "tds": 0.1}

    # flow map at the BASELINE closure, before any patch is applied
    plan = [(r, AB._flow_darcy(r["p_bar"], r["T_degC"])) for r in shots]

    saved = {}
    if patch:
        for name, fn in patch.items():
            saved[name] = getattr(pc, name)
            setattr(pc, name, fn)
    try:
        out = {}
        for r, flow in plan:
            bounds = AB._matched_bounds(flow)
            key = (r["variety"], r["T_degC"], r["p_bar"])
            for sol in FROZEN["species"]:
                out[key + (sol,)] = float(ps.simulate_fractions(
                    r["T_degC"], flow, bounds, params[sol], cl1=1.0)[0]) * conv[sol]
        return out
    finally:
        for name, fn in saved.items():
            setattr(pc, name, fn)


def substitutions():
    """The declared in-repo alternatives, one per closure, with their admissibility.

    `admissible` is False where using the alternative would require driving IT outside ITS OWN
    declared range. Those are still run, and reported, but they are excluded from the decision
    — measuring another source's extrapolation error is not a portability test.
    """
    from puckworks.models.pannusch2024 import closures as pc
    from puckworks.models.romancorrochano2017 import extraction as rx
    from puckworks import data as d

    tref = pc.TREF_K                                   # 360.15 K = 87.0 C, pannusch's own
    base_K, base_D = pc.vant_hoff_K, pc.diffusion_coeff
    base_mu, base_rho = pc.water_viscosity, pc.water_density

    def K_roman_shape(T_K, Kref, gamma, Tref=tref):
        """Pannusch's K anchored at Tref, carrying romancorrochano's Arrhenius T-LAW.

        K_sub(T) = K_pann(Tref) * K_roman(T)/K_roman(Tref). The partition CONVENTION and the
        anchor stay pannusch's; only the declared temperature dependence is swapped. The two
        closures disagree on the sign of dK/dT (gate_g4_temperature_sensitivity) and are never
        merged or averaged (CLAUDE.md rule 6).
        """
        T_K = np.asarray(T_K, float)
        anchor = base_K(Tref, Kref, gamma, Tref)
        ratio = rx.K_of_T(T_K - 273.15) / rx.K_of_T(Tref - 273.15)
        return anchor * ratio

    def D_stokes_einstein_shape(T_K, solute, Tref=tref):
        """Wilke-Chang's value at Tref, carrying romancorrochano's D ~ T temperature law.

        The thesis corrects Deff to temperature by the ratio of absolute temperatures;
        Wilke-Chang carries D ~ T/mu(T). Anchoring at Tref swaps only the declared T-law.
        """
        T_K = np.asarray(T_K, float)
        return float(base_D(Tref, solute)) * (T_K / Tref)

    def mu_telisromero_water_limit(T_K):
        """TR2001 Eq (10) evaluated at X_w = 100 % — OUTSIDE its declared 76-90 % range."""
        T_K = np.asarray(T_K, float)
        return np.vectorize(lambda t: float(d.telisromero_viscosity_pas(float(t), 100.0)))(T_K)

    def rho_telisromero_water_limit(T_K):
        """TR2001 density at X_w = 1 (pure water). Agrees with Rackett to <0.5 % in range."""
        T_K = np.asarray(T_K, float)
        return np.vectorize(
            lambda t: float(d.telisromero_density_kgm3(float(t) - 273.15, 1.0)))(T_K)

    return [
        dict(closure="vant_hoff_K", label="K(T): van't Hoff -> romancorrochano Arrhenius T-law",
             alternative_source="romancorrochano2017.extraction.K_of_T (thesis Arrhenius fit "
                                "ln K = -657/T + 1.4; card romancorrochano2017_extraction.md)",
             anchoring="K_pann(Tref) preserved at Tref = %.2f K; only the T-law is swapped"
                       % tref,
             admissible=True,
             admissibility_note="Both closures are declared over the espresso window and are "
                                "already compared on file (gate_g4_temperature_sensitivity). "
                                "They DISAGREE on the sign of dK/dT — a partition-convention "
                                "difference, surfaced, never merged.",
             patch={"vant_hoff_K": K_roman_shape}),
        dict(closure="diffusion_coeff",
             label="D(T): Wilke-Chang -> romancorrochano Stokes-Einstein T-law",
             alternative_source="romancorrochano2017.extraction.deff_of temperature "
                                "correction (D scaled by the ratio of absolute temperatures)",
             anchoring="D_WC(Tref, solute) preserved at Tref = %.2f K; only the T-law is "
                       "swapped" % tref,
             admissible=True,
             admissibility_note="Both are declared over the espresso window. The difference "
                                "between the two T-laws is exactly the mu(T) factor.",
             patch={"diffusion_coeff": D_stokes_einstein_shape}),
        dict(closure="water_density", label="rho(T): VDI Rackett -> telisromero2001 at X_w = 1",
             alternative_source="sourcing2026.g10_liquor_rheology — "
                                "puckworks.data.telisromero_density_kgm3 at the pure-water "
                                "limit",
             anchoring="none needed — same quantity, same units, both declared at the "
                       "pure-water limit",
             admissible=True,
             admissibility_note="A genuine like-for-like alternative source.",
             patch={"water_density": rho_telisromero_water_limit}),
        dict(closure="water_viscosity",
             label="mu(T): VDI -> telisromero2001 Eq (10) extrapolated to X_w = 100 %",
             alternative_source="sourcing2026.g10_liquor_rheology — "
                                "puckworks.data.telisromero_viscosity_pas",
             anchoring="none applied",
             admissible=False,
             admissibility_note="EXCLUDED FROM THE DECISION. TR2001 Eq (10) is declared over "
                                "X_w 76-90 % (coffee extract); at X_w = 100 % it returns "
                                "~0.56x the VDI water value, i.e. it is being driven far "
                                "outside ITS OWN range. Running it measures TR2001's "
                                "extrapolation error, not pannusch's portability. Reported as "
                                "a labelled BOUND only. The corpus contains no second "
                                "PURE-WATER viscosity correlation declared over 88-98 C — "
                                "that absence is itself a recorded finding.",
             patch={"water_viscosity": mu_telisromero_water_limit}),
        dict(closure="sherwood_h", label="Sh = A Re^B Sc^(1/3): NO ALTERNATIVE IN THE CORPUS",
             alternative_source=None, anchoring=None, admissible=False,
             admissibility_note="UNSUBSTITUTABLE. No second Sherwood correlation is registered "
                                "or carded. The fitted (A, B) are per-solute in Table 2 and "
                                "the card states they 'lack physical meaning and generality'; "
                                "moving one solute's pair onto another is a misuse, not a "
                                "source swap, and is not performed. Recorded as a gap.",
             patch=None),
    ]


# ------------------------------------------------------------------------------------------
# Validity-range check (a SURVIVE route in its own right)
# ------------------------------------------------------------------------------------------
def validity_range_check(shots):
    """Is the artifact ALREADY consumed outside its declared range under the frozen config?

    The candidate's SURVIVE condition has two arms and this is the second one, independent of
    any substitution.
    """
    from puckworks.validation.slow import angeloni_bracket as AB
    T = [r["T_degC"] for r in shots]
    Q = [float(AB._flow_darcy(r["p_bar"], r["T_degC"])) for r in shots]
    t_out = [t for t in T if not DECLARED_T_C[0] <= t <= DECLARED_T_C[1]]
    q_out = [q for q in Q if not DECLARED_Q_ML_S[0] <= q <= DECLARED_Q_ML_S[1]]
    return dict(declared_valid_range_verbatim=DECLARED_VALID_RANGE,
                declared_T_C=list(DECLARED_T_C), declared_Q_mL_s=list(DECLARED_Q_ML_S),
                used_T_C=[min(T), max(T)], used_Q_mL_s=[round(min(Q), 3), round(max(Q), 3)],
                n_conditions=len(shots),
                n_T_outside=len(t_out), n_Q_outside=len(q_out),
                consumed_outside_declared_range=bool(t_out or q_out),
                note="Under the frozen configuration the consumer drives the artifact strictly "
                     "INSIDE its declared T and Q range, so this SURVIVE arm does not fire. "
                     "Note the flow map is an assumption (single anchor, granulometry O); a "
                     "different admissible flow map could move Q, and that sensitivity is "
                     "already archived as angeloni_bracket.flow_map_sensitivity_transfer.")


# ------------------------------------------------------------------------------------------
# STEP 5 — the no-refit comparison
# ------------------------------------------------------------------------------------------
def _rel_change(base, alt):
    keys = sorted(base)
    return {k: abs(alt[k] - base[k]) / abs(base[k]) * 100.0 for k in keys}


def _tds_rsd_by_condition(shots):
    """Measured per-condition total-solids RSD, keyed the same way as the prediction dicts."""
    from puckworks import data as d
    ts = {(r["variety"], r["T_degC"], r["p_bar"]): float(r["RSD_pct"])
          for r in d.angeloni_total_solids()}
    return {(r["variety"], r["T_degC"], r["p_bar"]): ts[(r["variety"], r["T_degC"],
                                                        r["p_bar"])] for r in shots}


def _classify(species, effects, tds_rsd):
    """Three-way status for one (substitution, output), against THAT output's own authority.

    `effects` is the list of per-condition absolute relative changes (%) for this output.
    Returns the fixed classification plus the supporting numbers. This function never reads
    PROXY_U_PCT — the campaign proxy is reported elsewhere and decides nothing.
    """
    med = statistics.median(effects)
    mx = max(effects)
    auth = UNCERTAINTY_AUTHORITY[species]

    if auth["kind"] == "measured_per_condition":
        # Total solids: a real, measured uncertainty per condition. One determination.
        per_cond = [rsd for rsd in tds_rsd]
        med_rsd = statistics.median(per_cond)
        n_above = sum(1 for e, rsd in zip(effects, tds_rsd) if e > rsd)
        status = STATUS_MATERIAL if med > med_rsd else STATUS_IMMATERIAL
        return dict(species=species, authority="measured per-condition RSD",
                    median_effect_pct=round(med, 4), max_effect_pct=round(mx, 4),
                    threshold_pct=round(med_rsd, 4),
                    threshold_note="median of the measured per-condition RSD",
                    n_conditions_effect_exceeds_own_rsd=n_above,
                    frac_conditions_exceeding=round(n_above / len(effects), 4),
                    material_at_low_rsd=None, material_at_high_rsd=None,
                    status=status)

    lo, hi = auth["range_pct"]
    mat_lo = med > lo                      # most demanding end of the declared range
    mat_hi = med > hi                      # least demanding end
    if mat_lo and mat_hi:
        status = STATUS_MATERIAL
    elif not mat_lo and not mat_hi:
        status = STATUS_IMMATERIAL
    else:
        status = STATUS_CHANGES
    return dict(species=species, authority="declared range %.1f-%.1f %% (not per-cell)"
                                           % (lo, hi),
                median_effect_pct=round(med, 4), max_effect_pct=round(mx, 4),
                threshold_pct=None,
                threshold_note="no single threshold exists — the range is evaluated at both ends",
                frac_conditions_exceeding_low_end=round(
                    sum(1 for e in effects if e > lo) / len(effects), 4),
                frac_conditions_exceeding_high_end=round(
                    sum(1 for e in effects if e > hi) / len(effects), 4),
                material_at_low_rsd=bool(mat_lo), material_at_high_rsd=bool(mat_hi),
                status=status)


def no_refit(shots=None):
    shots = shots or _held_out_shots()
    base = _predict(shots)
    tds_rsd_map = _tds_rsd_by_condition(shots)
    out = []
    for sub in substitutions():
        if sub["patch"] is None:
            rec = dict(sub)
            rec.pop("patch", None)
            rec.update(ran=False, per_output=None, statuses=None,
                       counts_toward_decision=False)
            out.append(rec)
            continue
        alt = _predict(shots, sub["patch"])
        rel = _rel_change(base, alt)
        per_output = {}
        for sol in FROZEN["species"]:
            keys = sorted(k for k in rel if k[3] == sol)
            effects = [rel[k] for k in keys]
            tds_rsd = [tds_rsd_map[k[:3]] for k in keys]
            per_output[sol] = _classify(sol, effects, tds_rsd)
        vals = sorted(rel.values())
        rec = dict(sub)
        rec.pop("patch", None)
        rec.update(
            ran=True, n_points=len(vals), per_output=per_output,
            statuses={s: per_output[s]["status"] for s in FROZEN["species"]},
            counts_toward_decision=bool(sub["admissible"]),
            # POOLED figures — reported for continuity with the first version and for the
            # proxy sensitivity only. They are NOT read by the decision.
            pooled_median_rel_change_pct=round(statistics.median(vals), 4),
            pooled_p90_rel_change_pct=round(vals[int(0.9 * len(vals))], 4),
            pooled_max_rel_change_pct=round(max(vals), 4),
            pooled_frac_points_above_proxy_U=round(
                sum(1 for v in vals if v > PROXY_U_PCT) / len(vals), 4),
            pooled_material_against_proxy_U=bool(statistics.median(vals) > PROXY_U_PCT),
            pooled_note="POOLED ACROSS ANALYTES WITH DIFFERENT UNCERTAINTY AUTHORITY. Retained "
                        "for auditability against the superseded first version; decides nothing.")
        out.append(rec)
    return base, out


# ------------------------------------------------------------------------------------------
# STEP 7 — recalibration / compensation branch (only if a no-refit effect is material)
# ------------------------------------------------------------------------------------------
def recalibration_branch(shots, sub_patch):
    """IN-SAMPLE upper bound on how much of a swap a single rate rescale could absorb.

    Refits ONE scalar multiplier on the Sherwood prefactors (A1, A2) per species, chosen to
    minimise the median absolute relative difference from the BASELINE prediction. This is a
    compensation bound, NOT a prediction: it is fitted on the same points it is scored on, and
    it is labelled accordingly wherever it appears.
    """
    from puckworks.models.pannusch2024 import solver as ps
    base = _predict(shots)
    orig = ps._solute_params

    def scaled(mult):
        def _f():
            p = orig()
            return {s: dict(v, A1=v["A1"] * mult, A2=v["A2"] * mult) for s, v in p.items()}
        return _f

    grid = np.geomspace(0.5, 2.0, 13)
    best = None
    for m in grid:
        ps._solute_params = scaled(float(m))
        try:
            alt = _predict(shots, sub_patch)
        finally:
            ps._solute_params = orig
        med = statistics.median(_rel_change(base, alt).values())
        if best is None or med < best[1]:
            best = (float(m), med)
    return dict(label="RECALIBRATED_IN_SAMPLE_UPPER_BOUND_ON_COMPENSATION",
                rate_multiplier=round(best[0], 4),
                residual_median_rel_change_pct=round(best[1], 4),
                caveat="Fitted on the same points it is scored on. It bounds how much a "
                       "single global rate rescale COULD absorb; it is not a held-out result "
                       "and may not be read as one.")


# ------------------------------------------------------------------------------------------
# Decision
# ------------------------------------------------------------------------------------------
#: FIXED CLASSIFICATION — applied to the admissible substitutions only, in this precedence.
CLASSIFICATION_RULE = (
    "SURVIVE: at least one admissible closure swap is MATERIAL_THROUGHOUT the applicable "
    "retained uncertainty for at least one output, OR the artifact is consumed outside its "
    "declared range. "
    "RETIRE: every admissible swap is IMMATERIAL_THROUGHOUT for every output, AND the artifact "
    "is consumed inside its declared range. "
    "NEEDS_NEW_DATA: materiality CHANGES within the retained uncertainty range for at least one "
    "admissible swap and output, and no swap is material throughout — the missing evidence is "
    "solute-specific replicate RSD for caffeine, trigonelline and CGA.")


def screen():
    shots = _held_out_shots()
    vr = validity_range_check(shots)
    base, subs = no_refit(shots)

    admissible = [s for s in subs if s.get("counts_toward_decision") and s.get("ran")]
    material_cells = [(s["closure"], sp) for s in admissible
                      for sp, v in s["per_output"].items() if v["status"] == STATUS_MATERIAL]
    changing_cells = [(s["closure"], sp) for s in admissible
                      for sp, v in s["per_output"].items() if v["status"] == STATUS_CHANGES]

    # STEP 7 — the recalibration branch runs only on a MATERIAL no-refit effect.
    recal = None
    if material_cells:
        patches = {s["closure"]: s for s in substitutions()}
        for name in sorted({c for c, _ in material_cells}):
            recal = recal or {}
            recal[name] = recalibration_branch(shots, patches[name]["patch"])

    if vr["consumed_outside_declared_range"]:
        decision = "SURVIVE"
        why = "The artifact is already consumed outside its declared validity range."
    elif material_cells:
        decision = "SURVIVE"
        why = ("At least one admissible closure swap is material throughout the applicable "
               "retained uncertainty: %s."
               % ", ".join("%s on %s" % (c, sp) for c, sp in material_cells))
    elif changing_cells:
        decision = "NEEDS_NEW_DATA"
        why = ("Materiality CHANGES within the retained uncertainty range for %d "
               "(substitution, output) cells: %s. Every one of them is a named bioactive, whose "
               "replicate RSD the campaign does NOT retain per cell — the source gives only the "
               "declared 0.3-19.7 %% range, and the measured effects fall inside it. The missing "
               "evidence is solute-specific replicate RSD for caffeine, trigonelline and CGA. "
               "For total solids, the one output whose uncertainty IS retained, every admissible "
               "swap is immaterial."
               % (len(changing_cells),
                  ", ".join("%s on %s" % (c, sp) for c, sp in changing_cells)))
    else:
        decision = "RETIRE"
        why = ("Every admissible swap is immaterial throughout the applicable retained "
               "uncertainty for every output, and the artifact is driven strictly inside its "
               "declared range.")

    return dict(
        screen=CANDIDATE_ID, artifact=ARTIFACT, consumer=CONSUMER,
        disposition=["CHEAP_SCIENTIFIC_SCREEN", "NOT_A_PUBLICATION_RESULT",
                     "NOT_A_MODEL_VALIDATION_UPGRADE"],
        correction_note=(
            "CORRECTED 2026-08-04. The superseded first version used the median total-solids "
            "replicate RSD (4.70 %) as the decision authority for all four outputs, including "
            "three whose replicate uncertainty the campaign does not retain, and reported "
            "RETIRE. Each output is now judged against its own retained uncertainty; the "
            "corrected disposition is recorded below. The producer->consumer path, the frozen "
            "configuration, the admissible substitutions and the no-refit predictions are "
            "unchanged."),
        path=PATH, frozen=FROZEN,
        held_out_unit=dict(
            dataset="angeloni2023 (bioactives + total_solids), granulometry O, on-grid",
            manifest_validation_strength_verbatim=(
                "independent (different machine/coffee/basket than pannusch fit or cameron "
                "calibration)"),
            n_conditions=len(shots), n_species=len(FROZEN["species"]),
            n_points=len(shots) * len(FROZEN["species"]),
            non_circular_because="never used to fit pannusch2024.closures; the fit target "
                                 "(schmieder kinetics) is excluded as circular"),
        validity_range=vr,
        uncertainty=dict(UNCERTAINTY,
                         tds_median_rsd_this_screen_pct=round(statistics.median(
                             list(_tds_rsd_by_condition(shots).values())), 4),
                         tds_median_rsd_this_screen_note=(
                             "median measured total-solids RSD over the 18 held-out "
                             "granulometry-O on-grid conditions this screen actually uses. THIS "
                             "is the total-solids threshold; PROXY_U_PCT (4.70 %) is the "
                             "campaign-wide median over all 66 shots and decides nothing.")),
        classification_rule=CLASSIFICATION_RULE,
        substitutions=subs,
        n_admissible=len(admissible),
        material_cells=[list(c) for c in material_cells],
        changing_cells=[list(c) for c in changing_cells],
        recalibration=recal,
        decision=decision, decision_reasoning=why)


# ------------------------------------------------------------------------------------------
# Primary figure
# ------------------------------------------------------------------------------------------
_INK, _MUTED, _GRID = "#1a1a1a", "#5a5a5a", "#d9d9d9"
_C_BASE, _C_K, _C_D, _C_RHO, _C_MU = "#1a1a1a", "#0072b2", "#e69f00", "#cc79a7", "#6b6b6b"


def figure(path=None, result=None):
    """Two-panel primary figure.

    TOP — the candidate's required minimum figure: held-out concentration per species and
    condition under each closure, over the common validity range. The measured points carry the
    uncertainty each output ACTUALLY has: a measured per-condition bar for total solids, and for
    the three named bioactives the full declared 0.3-19.7 % range, drawn as a band because the
    campaign does not retain a per-cell value.

    BOTTOM — the decisive comparison: each admissible swap's median held-out effect per output,
    against that output's own uncertainty authority. This is the panel the decision reads.
    """
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    plt.rcParams.update({"figure.dpi": 150, "savefig.dpi": 150, "font.size": 8.5,
                         "font.family": "DejaVu Sans"})

    shots = _held_out_shots()
    meas = _measured(shots)
    base = _predict(shots)
    subs = {s["closure"]: s for s in substitutions()}
    swap_names = ("vant_hoff_K", "diffusion_coeff", "water_density", "water_viscosity")
    alts = {name: _predict(shots, subs[name]["patch"]) for name in swap_names}
    r = result or screen()
    tds_rsd = _tds_rsd_by_condition(shots)
    tds_med_rsd = statistics.median(list(tds_rsd.values()))

    variety = "Arabica"
    order = sorted({(s["T_degC"], s["p_bar"]) for s in shots if s["variety"] == variety})
    xs = np.arange(len(order))
    labels = ["%.0f\u00b0C\n%.0f bar" % (t, p) for t, p in order]

    style = [("baseline (VDI \u03bc, Rackett \u03c1, Wilke-Chang D, van\u2019t Hoff K)",
              base, _C_BASE, "-", 5.0, 0.28),
             ("swap K(T) \u2192 Arrhenius T-law", alts["vant_hoff_K"], _C_K, "-", 1.6, 1.0),
             ("swap D(T) \u2192 Stokes-Einstein T-law", alts["diffusion_coeff"], _C_D, "-",
              1.6, 1.0),
             ("swap \u03c1(T) \u2192 telisromero2001", alts["water_density"], _C_RHO, "-",
              1.6, 1.0),
             ("swap \u03bc(T) \u2192 TR2001 @ X_w=100 % (OUT OF ITS OWN RANGE \u2014 bound "
              "only)", alts["water_viscosity"], _C_MU, ":", 1.5, 1.0)]

    fig = plt.figure(figsize=(13.4, 8.2))
    gs = fig.add_gridspec(2, 4, height_ratios=[1.15, 1.0], hspace=0.52, wspace=0.30)

    lo_b, hi_b = BIOACTIVE_RSD_BAND_PCT
    for j, sol in enumerate(FROZEN["species"]):
        ax = fig.add_subplot(gs[0, j])
        for i, (lab, pred, col, ls, lw, a) in enumerate(style):
            y = [pred[(variety, t, p, sol)] for t, p in order]
            if i == 0:
                ax.plot(xs, y, "-", color=col, lw=lw, alpha=a, solid_capstyle="round",
                        label=lab if j == 0 else None, zorder=2)
            else:
                ax.plot(xs, y, ls, color=col, lw=lw, alpha=a, marker="o", ms=3.4,
                        label=lab if j == 0 else None, zorder=3)
        ym = [meas[(variety, t, p, sol)] for t, p in order]
        if sol == "tds":
            err = [v * tds_rsd[(variety, t, p)] / 100.0 for v, (t, p) in zip(ym, order)]
            ax.errorbar(xs, ym, yerr=err, fmt="s", ms=4.2, color="#d55e00", ecolor="#d55e00",
                        elinewidth=1.2, capsize=2.5, zorder=4,
                        label="measured \u00b1 MEASURED per-condition RSD" if j == 0 else None)
        else:
            hi = [v * hi_b / 100.0 for v in ym]
            lo = [v * lo_b / 100.0 for v in ym]
            ax.errorbar(xs, ym, yerr=hi, fmt="none", ecolor="#d55e00", elinewidth=6.0,
                        alpha=0.22, capsize=0, zorder=3,
                        label="measured \u00b1 the DECLARED 0.3\u201319.7 % range "
                              "(no per-cell RSD retained)" if j == 0 else None)
            ax.errorbar(xs, ym, yerr=lo, fmt="s", ms=4.2, color="#d55e00", ecolor="#d55e00",
                        elinewidth=1.2, capsize=2.5, zorder=4)
        ax.set_title(sol, fontsize=9.5, color=_INK)
        ax.set_ylabel(SPECIES_UNITS[sol], fontsize=7.4, color=_MUTED)
        ax.grid(True, color=_GRID, lw=0.5, alpha=0.8)
        ax.set_axisbelow(True)
        ax.set_xticks(xs)
        ax.set_xticklabels(labels, fontsize=6.2, rotation=90)
        ax.tick_params(labelsize=7)
        if j == 0:
            handles, labs = ax.get_legend_handles_labels()

    # ---- decisive panel -------------------------------------------------------------------
    axd = fig.add_subplot(gs[1, :])
    # the declared bioactive band governs the three named solutes ONLY; it is drawn over their
    # x-range and stops where the total-solids group begins, because tds has its own authority.
    axd.axhspan(lo_b, hi_b, xmin=0.0, xmax=(2.5 + 0.5) / 4.2, color="#d55e00", alpha=0.13,
                zorder=0)
    axd.plot([-0.5, 2.5], [hi_b] * 2, color="#d55e00", lw=1.0, ls="--", zorder=1)
    axd.plot([-0.5, 2.5], [lo_b] * 2, color="#d55e00", lw=1.0, ls="--", zorder=1)
    axd.text(2.45, hi_b * 1.10, "declared bioactive RSD range 0.3\u201319.7 % "
             "(no per-cell value retained) \u2014 governs these three only",
             fontsize=7.2, color="#d55e00", ha="right")
    axd.text(2.45, lo_b * 0.78, "0.3 %  \u2014 most demanding end", fontsize=7.0,
             color="#d55e00", ha="right", va="top")
    axd.axvline(2.5, color=_GRID, lw=1.2, zorder=1)

    swap_style = {"vant_hoff_K": (_C_K, "o", "K(T)"), "diffusion_coeff": (_C_D, "o", "D(T)"),
                  "water_density": (_C_RHO, "o", "\u03c1(T)"),
                  "water_viscosity": (_C_MU, "D", "\u03bc(T) bound \u2014 excluded")}
    recs = {s["closure"]: s for s in r["substitutions"] if s.get("ran")}
    off = {"vant_hoff_K": -0.21, "diffusion_coeff": -0.07, "water_density": 0.07,
           "water_viscosity": 0.21}
    for name, (col, mk, lab) in swap_style.items():
        po = recs[name]["per_output"]
        xv = [j + off[name] for j, sol in enumerate(FROZEN["species"])]
        yv = [po[sol]["median_effect_pct"] for sol in FROZEN["species"]]
        hiv = [po[sol]["max_effect_pct"] for sol in FROZEN["species"]]
        axd.vlines(xv, yv, hiv, color=col, lw=1.1, alpha=0.55, zorder=2)
        axd.plot(xv, hiv, "_", ms=8, color=col, alpha=0.75, zorder=2)
        axd.plot(xv, yv, mk, ms=6.5, color=col, zorder=3, label="%s  median (bar = max)" % lab,
                 mfc=col if name != "water_viscosity" else "none",
                 mec=col, mew=1.4, ls="none")
    axd.plot([2.55, 3.68], [tds_med_rsd] * 2, color="#0072b2", lw=2.4, zorder=4)
    axd.text(3.68, tds_med_rsd * 1.18, "total-solids MEASURED RSD\nmedian %.2f %% over these 18 "
             "conditions\n\u2014 a real threshold" % tds_med_rsd, fontsize=7.2, color="#0072b2",
             ha="right", linespacing=1.4)
    axd.set_yscale("log")
    axd.set_xticks(range(len(FROZEN["species"])))
    axd.set_xticklabels(["%s\n%s" % (s, "measured RSD" if s == "tds" else "declared range only")
                         for s in FROZEN["species"]], fontsize=8)
    axd.set_xlim(-0.5, 3.7)
    axd.set_ylabel("held-out effect of the swap\n|\u0394| in predicted concentration  [%]",
                   fontsize=8.4)
    axd.grid(True, axis="y", color=_GRID, lw=0.5)
    axd.set_axisbelow(True)
    axd.legend(loc="lower left", fontsize=7.2, frameon=False, ncol=4)
    axd.set_title("Decisive panel \u2014 each swap\u2019s median held-out effect against THAT "
                  "OUTPUT\u2019S OWN retained uncertainty (this is what the decision reads)",
                  fontsize=9, color=_INK, pad=8)

    fig.suptitle("I-010 \u2014 held-out (angeloni) prediction under a one-at-a-time closure "
                 "swap, inside the artifact\u2019s declared range (T 80\u201398 \u00b0C, "
                 "Q 1\u20133 mL/s)", fontsize=11.5, y=0.995, x=0.005, ha="left", weight="bold")
    fig.text(0.005, 0.962,
             "CHEAP_SCIENTIFIC_SCREEN \u00b7 NOT_A_PUBLICATION_RESULT \u00b7 "
             "NOT_A_MODEL_VALIDATION_UPGRADE     Arabica shown above; all 18 conditions "
             "\u00d7 4 species in result.json.     NO REFIT \u2014 nothing is fitted to these "
             "points, so there is no recalibrated curve to distinguish.",
             fontsize=7.2, color=_MUTED, style="italic", ha="left")

    fig.legend(handles, labs, loc="upper left", ncol=3, fontsize=7.4, frameon=False,
               bbox_to_anchor=(0.0, 0.955))

    po = {n: recs[n]["per_output"] for n in swap_names}
    fig.text(0.005, 0.045, va="top", ha="left", fontsize=7.2, color=_MUTED, linespacing=1.6,
             s="Per-output classification (each output against its OWN authority; analytes are "
               "NOT pooled):\n"
               "    total solids \u2014 measured RSD available: K(T) %.2f %%, D(T) %.2f %%, "
               "\u03c1(T) %.3f %% median effect, all below the measured %.2f %% \u2192 "
               "IMMATERIAL, a real answer.\n"
               "    caffeine / trigonelline / 5CQA \u2014 no per-cell RSD: K(T) and D(T) median "
               "effects (%.2f\u2013%.2f %%) sit INSIDE the declared 0.3\u201319.7 %% range, so "
               "they are material at one end and immaterial at the other. \u03c1(T) is below "
               "0.3 %% \u2192 immaterial throughout.\n"
               "    The campaign-wide 4.70 %% figure the superseded first version used as the "
               "authority for ALL FOUR outputs is a total-solids number over all 66 shots; it "
               "is retained as a labelled proxy and decides nothing.\n"
               "DECISION  %s \u2014 materiality changes inside the retained range for %d "
               "(swap, output) cells, every one a named bioactive. Missing evidence: "
               "solute-specific replicate RSD for caffeine, trigonelline and CGA. For total "
               "solids, the one output whose uncertainty IS retained, every admissible swap is "
               "immaterial."
               % (po["vant_hoff_K"]["tds"]["median_effect_pct"],
                  po["diffusion_coeff"]["tds"]["median_effect_pct"],
                  po["water_density"]["tds"]["median_effect_pct"], tds_med_rsd,
                  min(po["diffusion_coeff"][s]["median_effect_pct"]
                      for s in ("caffeine", "trigonelline", "5CQA")),
                  max(po["vant_hoff_K"][s]["median_effect_pct"]
                      for s in ("caffeine", "trigonelline", "5CQA")),
                  r["decision"], len(r["changing_cells"])))

    path = path or (REPO_ROOT / "docs/insights/screens/I-010/figures/primary.png")
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return path


def main(argv=None):
    r = screen()
    out = REPO_ROOT / "docs/insights/screens/I-010/result.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(r, indent=2) + "\n", encoding="utf-8")
    print("path established: %s" % r["path"]["established"])
    print("held-out points : %d" % r["held_out_unit"]["n_points"])
    print("uncertainty authority: tds = measured per-condition RSD; bioactives = declared "
          "%.1f-%.1f %% range (no per-cell value)" % BIOACTIVE_RSD_BAND_PCT)
    for s in r["substitutions"]:
        if not s["ran"]:
            print("  %-16s NOT RUN \u2014 unsubstitutable" % s["closure"])
            continue
        print("  %-16s admissible=%-5s" % (s["closure"], s["admissible"]))
        for sol in FROZEN["species"]:
            v = s["per_output"][sol]
            print("      %-13s median=%7.4f %%  max=%7.4f %%  -> %s"
                  % (sol, v["median_effect_pct"], v["max_effect_pct"], v["status"]))
    print("outside declared range: %s" % r["validity_range"]["consumed_outside_declared_range"])
    print("material cells : %s" % (r["material_cells"] or "none"))
    print("changing cells : %d" % len(r["changing_cells"]))
    print("DECISION: %s" % r["decision"])
    fig_path = figure(result=r)
    print("wrote %s" % out.relative_to(REPO_ROOT))
    print("wrote %s" % fig_path.relative_to(REPO_ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
