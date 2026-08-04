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
# STEP 6 + the PREDECLARED materiality criterion
# ------------------------------------------------------------------------------------------
#: Retained observational uncertainty. The campaign's ONLY per-condition replicate information
#: is the TS and lipid RSD columns; the named bioactives carry a global 0.3-19.7 % range with
#: no per-cell value (MANIFEST angeloni2023/bioactives, and
#: angeloni2023/total_solids_lipids_rsd: "caffeine/trigonelline/CGA solute-specific RSD NOT
#: recovered"). TS is used because it IS one of the four scored observables, is measured on the
#: same 66 shots, and its median sits well inside the source's stated global band for the
#: others. Lipids are NOT a scored observable and are carried only as an upper sensitivity.
OBS_RSD_SOURCE = "median measured per-condition RSD of angeloni2023/total_solids (n=66)"
OBS_RSD_PCT = 4.70
OBS_RSD_UPPER_SENSITIVITY_PCT = 12.55        # angeloni2023/lipids median, not scored

#: Retained numerical uncertainty: the MAXIMUM relative change in the predicted held-out
#: concentration between the frozen configuration (NZ=200, rtol=atol=1e-6) and a refined one
#: (NZ=400, rtol=atol=1e-8), over all 72 held-out points. Computed from the baseline alone,
#: before any substitution was run. It is negligible: the budget is entirely observational.
NUM_REL_PCT = 0.0001

#: PREDECLARED MATERIALITY CRITERION — fixed before any swap result was computed, and derived
#: from retained uncertainty rather than from a round percentage.
#:
#:     U = sqrt(OBS_RSD_PCT^2 + NUM_REL_PCT^2)  ~= 4.70 %
#:
#: A substitution is MATERIAL iff the MEDIAN absolute relative change in the held-out predicted
#: concentration, over all held-out conditions x scored species, EXCEEDS U.
#:
#: The median (not the mean, not the max) because a single domain-edge condition must not
#: decide the screen. The fraction of points exceeding U and the per-species breakdown are
#: reported, and are informative, but they are NOT the criterion.
MATERIALITY_U_PCT = float(np.hypot(OBS_RSD_PCT, NUM_REL_PCT))
MATERIALITY_STATEMENT = (
    "A substitution is MATERIAL iff the median absolute relative change in the held-out "
    "predicted concentration across all held-out (condition x species) points exceeds "
    "U = sqrt(obs^2 + num^2) = %.3f %%, where obs = %.2f %% (%s) and num = %.4f %% (max "
    "relative change between NZ=200/1e-6 and NZ=400/1e-8 on the same points). Predeclared "
    "before any substitution was computed." % (MATERIALITY_U_PCT, OBS_RSD_PCT, OBS_RSD_SOURCE,
                                               NUM_REL_PCT))

UNCERTAINTY = dict(observational_rsd_pct=OBS_RSD_PCT, observational_source=OBS_RSD_SOURCE,
                   observational_upper_sensitivity_pct=OBS_RSD_UPPER_SENSITIVITY_PCT,
                   numerical_max_rel_pct=NUM_REL_PCT,
                   numerical_source="NZ 200/rtol 1e-6 vs NZ 400/rtol 1e-8 over the 72 "
                                    "held-out points (angeloni_bracket._numerics)",
                   combined_U_pct=MATERIALITY_U_PCT,
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


def no_refit(shots=None):
    shots = shots or _held_out_shots()
    base = _predict(shots)
    out = []
    for sub in substitutions():
        if sub["patch"] is None:
            out.append(dict(sub, ran=False, median_rel_change_pct=None, material=None))
            continue
        alt = _predict(shots, sub["patch"])
        rel = _rel_change(base, alt)
        vals = sorted(rel.values())
        by_species = {}
        for sol in FROZEN["species"]:
            v = [rel[k] for k in rel if k[3] == sol]
            by_species[sol] = dict(median=round(statistics.median(v), 4),
                                   max=round(max(v), 4))
        med = statistics.median(vals)
        rec = dict(sub)
        rec.pop("patch", None)
        rec.update(ran=True, n_points=len(vals),
                   median_rel_change_pct=round(med, 4),
                   p90_rel_change_pct=round(vals[int(0.9 * len(vals))], 4),
                   max_rel_change_pct=round(max(vals), 4),
                   frac_points_above_U=round(
                       sum(1 for v in vals if v > MATERIALITY_U_PCT) / len(vals), 4),
                   by_species=by_species,
                   material=bool(med > MATERIALITY_U_PCT),
                   counts_toward_decision=bool(sub["admissible"]))
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
def screen():
    shots = _held_out_shots()
    vr = validity_range_check(shots)
    base, subs = no_refit(shots)

    admissible = [s for s in subs if s.get("counts_toward_decision") and s.get("ran")]
    material = [s for s in admissible if s["material"]]

    recal = None
    if material:
        patches = {s["closure"]: s for s in substitutions()}
        recal = {s["closure"]: recalibration_branch(shots, patches[s["closure"]]["patch"])
                 for s in material}

    if material or vr["consumed_outside_declared_range"]:
        decision = "SURVIVE"
        why = ("A confirmed closure swap changes the held-out output by more than the retained "
               "uncertainty over the common validity range." if material else
               "The artifact is already consumed outside its declared validity range.")
    else:
        decision = "RETIRE"
        why = ("A consuming path exists and the held-out output is insensitive to every "
               "admissible one-closure swap: no substitution moved the median held-out "
               "prediction by more than the predeclared uncertainty U, and the artifact is "
               "driven strictly inside its declared range.")

    return dict(
        screen=CANDIDATE_ID, artifact=ARTIFACT, consumer=CONSUMER,
        disposition=["CHEAP_SCIENTIFIC_SCREEN", "NOT_A_PUBLICATION_RESULT",
                     "NOT_A_MODEL_VALIDATION_UPGRADE"],
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
        validity_range=vr, uncertainty=UNCERTAINTY,
        substitutions=subs,
        n_admissible=len(admissible), n_material=len(material),
        recalibration=recal,
        decision=decision, decision_reasoning=why)


# ------------------------------------------------------------------------------------------
# Primary figure
# ------------------------------------------------------------------------------------------
_INK, _MUTED, _GRID = "#1a1a1a", "#5a5a5a", "#d9d9d9"
_C_BASE, _C_K, _C_D, _C_RHO, _C_MU = "#1a1a1a", "#0072b2", "#e69f00", "#cc79a7", "#6b6b6b"


def figure(path=None):
    """Held-out species concentration under each closure, over the common validity range."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    plt.rcParams.update({"figure.dpi": 150, "savefig.dpi": 150, "font.size": 8.5,
                         "font.family": "DejaVu Sans"})

    shots = _held_out_shots()
    meas = _measured(shots)
    base = _predict(shots)
    subs = {s["closure"]: s for s in substitutions()}
    alts = {name: _predict(shots, subs[name]["patch"])
            for name in ("vant_hoff_K", "diffusion_coeff", "water_density", "water_viscosity")}
    r = screen()

    variety = "Arabica"
    rows = [s for s in shots if s["variety"] == variety]
    order = sorted({(s["T_degC"], s["p_bar"]) for s in rows})
    xs = np.arange(len(order))
    labels = ["%.0f°C\n%.0f bar" % (t, p) for t, p in order]

    style = [("baseline (VDI μ, Rackett ρ, Wilke-Chang D, van't Hoff K)", base, _C_BASE, "-",
              2.0, 1.0),
             ("swap K(T) → Arrhenius T-law", alts["vant_hoff_K"], _C_K, "-", 1.6, 1.0),
             ("swap D(T) → Stokes-Einstein T-law", alts["diffusion_coeff"], _C_D, "-", 1.6,
              1.0),
             ("swap ρ(T) → telisromero2001", alts["water_density"], _C_RHO, "-", 1.6, 1.0),
             ("swap μ(T) → TR2001 @ X_w=100 % (OUT OF ITS OWN RANGE — bound only)",
              alts["water_viscosity"], _C_MU, ":", 1.5, 1.0)]

    fig, axes = plt.subplots(1, 4, figsize=(13.4, 4.6))
    for ax, sol in zip(axes, FROZEN["species"]):
        for i, (lab, pred, col, ls, lw, a) in enumerate(style):
            y = [pred[(variety, t, p, sol)] for t, p in order]
            # the baseline is drawn as a WIDE pale line so the swap curves sit on top of it:
            # where they coincide, that coincidence is the result and must be visible.
            if i == 0:
                ax.plot(xs, y, "-", color=col, lw=5.0, alpha=0.28, solid_capstyle="round",
                        label=lab if sol == "caffeine" else None, zorder=2)
            else:
                ax.plot(xs, y, ls, color=col, lw=lw, alpha=a, marker="o", ms=3.4,
                        label=lab if sol == "caffeine" else None, zorder=3)
        ym = [meas[(variety, t, p, sol)] for t, p in order]
        ax.errorbar(xs, ym, yerr=[v * OBS_RSD_PCT / 100.0 for v in ym], fmt="s", ms=4.2,
                    color="#d55e00", ecolor="#d55e00", elinewidth=1.0, capsize=2.5,
                    label="measured (angeloni, ±%.1f %% replicate RSD)" % OBS_RSD_PCT
                    if sol == "caffeine" else None, zorder=4)
        ax.set_title(sol, fontsize=9.5, color=_INK)
        ax.set_ylabel(SPECIES_UNITS[sol], fontsize=7.6, color=_MUTED)
        ax.grid(True, color=_GRID, lw=0.5, alpha=0.8)
        ax.set_axisbelow(True)
        ax.set_xticks(xs)
        ax.set_xticklabels(labels, fontsize=6.6)
        ax.tick_params(labelsize=7)

    fig.suptitle("I-010 — held-out (angeloni) prediction under a one-at-a-time closure swap; "
                 "every curve is inside the artifact's declared range (T 80–98 °C, Q 1–3 mL/s)",
                 fontsize=11, y=1.005, x=0.005, ha="left", weight="bold")
    fig.text(0.005, 0.955,
             "CHEAP_SCIENTIFIC_SCREEN · NOT_A_PUBLICATION_RESULT · "
             "NOT_A_MODEL_VALIDATION_UPGRADE     Arabica shown; Robusta identical in shape — "
             "all 18 conditions × 4 species in result.json.     NO REFIT: nothing is fitted to "
             "these points.",
             fontsize=7.2, color=_MUTED, style="italic", ha="left")

    fig.tight_layout()
    handles, labs = axes[0].get_legend_handles_labels()
    fig.legend(handles, labs, loc="upper left", ncol=3, fontsize=7.4, frameon=False,
               bbox_to_anchor=(0.0, -0.035))

    med = {s["closure"]: s["median_rel_change_pct"] for s in r["substitutions"] if s["ran"]}
    fig.text(0.005, -0.20, va="top", s=
             "Median |Δ| in the held-out prediction over all 72 points, vs the predeclared "
             "uncertainty U = %.2f %% (√(obs² + num²); obs = %.2f %% measured replicate RSD, "
             "num = %.4f %%):\n"
             "    K(T) %.3f %%     D(T) %.3f %%     ρ(T) %.3f %%   — all three admissible "
             "swaps are far below U.        μ(T) %.2f %% — EXCLUDED from the decision: TR2001 "
             "is being driven outside its own 76–90 %% X_w range.\n"
             "    Sh = A Re^B Sc^(1/3): UNSUBSTITUTABLE — the corpus holds no second Sherwood "
             "correlation, and moving one solute's fitted (A, B) onto another is a misuse, not "
             "a source swap.\n"
             "DECISION  RETIRE — the path is real, but the held-out output is insensitive to "
             "every admissible one-closure swap, and the artifact is driven strictly inside "
             "its declared range."
             % (MATERIALITY_U_PCT, OBS_RSD_PCT, NUM_REL_PCT, med["vant_hoff_K"],
                med["diffusion_coeff"], med["water_density"], med["water_viscosity"]),
             fontsize=7.2, color=_MUTED, ha="left", linespacing=1.6)

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
    print("path established: %s (%s)" % (r["path"]["established"], r["path"]["import_site"]))
    print("held-out points : %d" % r["held_out_unit"]["n_points"])
    print("U (predeclared) : %.3f %%" % MATERIALITY_U_PCT)
    for s in r["substitutions"]:
        if not s["ran"]:
            print("  %-16s NOT RUN — %s" % (s["closure"], "unsubstitutable"))
            continue
        print("  %-16s median |d| = %7.4f %%   material=%-5s  counts=%s"
              % (s["closure"], s["median_rel_change_pct"], s["material"],
                 s["counts_toward_decision"]))
    print("outside declared range: %s" % r["validity_range"]["consumed_outside_declared_range"])
    print("DECISION: %s" % r["decision"])
    fig_path = figure()
    print("wrote %s" % out.relative_to(REPO_ROOT))
    print("wrote %s" % fig_path.relative_to(REPO_ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
