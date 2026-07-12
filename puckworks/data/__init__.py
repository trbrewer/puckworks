"""puckworks.data — dataset loaders for intaken (Phase 0) datasets.

Every loader returns plain in-memory structures (dicts of numpy arrays / floats)
read byte-for-byte from files under this package. Datasets live in per-source
subdirectories (e.g. ``waszkiewicz2025/``) with a ``PROVENANCE.md`` and a row in
``MANIFEST.csv``. Loaders do no fitting and no unit conversion beyond what a
column header declares — units are asserted, not trusted (CLAUDE.md rule 7).
"""
import csv
from pathlib import Path

import numpy as np

DATA_DIR = Path(__file__).resolve().parent


def _rows(path):
    with open(path, newline="", encoding="utf-8-sig") as fh:
        return list(csv.DictReader(fh))


def _params(path):
    """Read a `parameter,value,...` calibration file into {name: float}."""
    out = {}
    for r in _rows(path):
        out[r["parameter"]] = float(r["value"])
    return out


def _typed_rows(path):
    """DictReader rows with each cell coerced to float where it parses."""
    def conv(v):
        try:
            return float(v)
        except (ValueError, TypeError):
            return v
    return [{k: conv(v) for k, v in r.items()} for r in _rows(path)]


def _typed_rows_hashskip(path):
    """Like _typed_rows but skips leading `#` comment/provenance lines (the
    romancorrochano2017 drop carries provenance headers on every file)."""
    def conv(v):
        try:
            return float(v)
        except (ValueError, TypeError):
            return v
    with open(path, newline="", encoding="utf-8-sig") as fh:
        body = (ln for ln in fh if not ln.lstrip().startswith("#"))
        rows = list(csv.DictReader(body))
    return [{k: conv(v) for k, v in r.items()} for r in rows]


# --- waszkiewicz2025 (ROADMAP 0.2) ---------------------------------------
WASZ = DATA_DIR / "waszkiewicz2025"

WASZ_PRESSURES_BAR = [1.0, 2.0, 3.5, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 11.0, 13.0]


def waszkiewicz_traces():
    """Q(t) traces at 11 reference pressures.

    Returns {pressure_bar: {col: np.ndarray}} keyed by the rounded reference
    pressure, plus 'columns'. Source: traces_time_dependent.csv (Fig 5/8).
    """
    rows = _rows(WASZ / "traces_time_dependent.csv")
    cols = [c for c in rows[0].keys() if c != "reference_pressure_round__bar"]
    out = {}
    for r in rows:
        p = round(float(r["reference_pressure_round__bar"]), 3)
        d = out.setdefault(p, {c: [] for c in cols})
        for c in cols:
            v = r[c]
            d[c].append(float(v) if v not in ("", None) else np.nan)
    for p in out:
        out[p] = {c: np.asarray(v, float) for c, v in out[p].items()}
    out["columns"] = cols
    return out


def waszkiewicz_tds_fractions():
    """5-s TDS(t) fractions: {'time_s','tds_pct','tds_std_pct'} arrays."""
    rows = _rows(WASZ / "tds_fractions.csv")
    f = lambda k: np.asarray(
        [float(r[k]) if r[k] not in ("", None) else np.nan for r in rows], float
    )
    return {"time_s": f("time__s"), "tds_pct": f("tds__percent"),
            "tds_std_pct": f("tds_std__percent")}


def waszkiewicz_static_calibration():
    """Equilibrium-curve fit: {'P_c_bar','Q_c_g_per_s'} (Fig 6)."""
    p = _params(WASZ / "static_calibration.csv")
    return {"P_c_bar": p["p_ref__bar"], "Q_c_g_per_s": p["q_ref__g_per_s"]}


def waszkiewicz_constants():
    """Rig constants keyed by original parameter name (SI where stated)."""
    return _params(WASZ / "constants.csv")


def waszkiewicz_brewer_quadratic():
    """Brewer pressure-drop quadratic ΔP=aQ²+bQ+c: {'a','b','c'} (Fig 2B)."""
    return _params(WASZ / "brewer_quadratic_params.csv")


def waszkiewicz_psd():
    """Mastersizer PSD. Returns {'size_um': (48,), 'volume_pct': (n_rep, 48)}.

    Source file is semicolon-delimited, UTF-8-BOM, transposed: row 1 = bins,
    subsequent rows = replicate volume-% distributions with a leading empty cell.
    """
    raw = (WASZ / "mastersizer_psd.csv").read_text(encoding="utf-8-sig")
    lines = [ln for ln in raw.splitlines() if ln.strip("; \t")]
    size = np.asarray([float(x) for x in lines[0].split(";") if x != ""], float)
    reps = []
    for ln in lines[1:]:
        vals = [float(x) if x != "" else np.nan for x in ln.split(";")]
        reps.append(vals[-len(size):])          # drop leading empty field
    return {"size_um": size, "volume_pct": np.asarray(reps, float)}


# --- schmieder2023 (ROADMAP 0.1, kinetics half) --------------------------
SCHM = DATA_DIR / "schmieder2023"


def schmieder_kinetics_fit_avg():
    """Paper Table A1 — per-experiment AVERAGED c0/lambda fits (authoritative).

    Long form: one row per (exp, component). Returns list of dicts.
    """
    return _typed_rows(SCHM / "kinetics_fit_params_avg.csv")


def schmieder_kinetics_fit_reps():
    """Table S2 — per-replicate c0/lambda fits (15 exp x reps x 4 components)."""
    return _typed_rows(SCHM / "kinetics_fit_params_reps.csv")


def schmieder_cup_masses():
    """Table S3 / paper Table 2 — per-replicate cup mass + concentration by BR."""
    return _typed_rows(SCHM / "cup_masses.csv")


def schmieder_raw_fractions():
    """Table S1 — raw per-fraction outlet concentrations (no TDS column)."""
    return _typed_rows(SCHM / "raw_fractions.csv")


def schmieder_rsm():
    """Paper Table 3 — full-quadratic RSM coefficients beta0..beta9 (data-only)."""
    return _typed_rows(SCHM / "rsm_coefficients.csv")


# --- wadsworth2026 grind map (ROADMAP 0.6 / 1.5) -------------------------
WADS = DATA_DIR / "wadsworth2026"


def wadsworth_grindmap_table1():
    """Full Table 1: per (coffee, G) grind moments <R>,<R2>,<R3>,S plus
    connected/total porosity, connectivity, specific surface, and permeability.
    Two coffees (Guayacan/Colombia, Tumba/Rwanda) x 11 Mahlkonig settings."""
    return _typed_rows(WADS / "wadsworth2026_table1_full.csv")


# --- liang2021 (ROADMAP 0.9 / 1.3), digitized figures --------------------
LIANG = DATA_DIR / "liang2021"


def liang_fig3_tds():
    """Fig 3: equilibrium TDS(%) vs brew ratio, 1-L brews (K*E_max refit)."""
    return _typed_rows(LIANG / "liang_fig3_tds_vs_rbrew.csv")


def liang_fig4_E():
    """Fig 4: E and E_oven (%) vs brew ratio (measurement column selects branch)."""
    return _typed_rows(LIANG / "liang_fig4_E_vs_rbrew.csv")


def liang_fig5_cupping():
    """Fig 5: cupping TDS / E vs brew ratio across roast levels."""
    return _typed_rows(LIANG / "liang_fig5_cupping.csv")


# --- moroney2016 (ROADMAP 0.10 / 1.4) ------------------------------------
MORONEY = DATA_DIR / "moroney2016"


def moroney_fig6():
    """Fig 6: experimental exit concentration c_h (nondim) vs t (nondim)."""
    return _typed_rows(MORONEY / "moroney_fig6_exit_concentration.csv")


def moroney_table1():
    """Table 1: full parameter set + dimensionless groups (transcribed)."""
    return _typed_rows(MORONEY / "moroney2016_table1.csv")


# --- grudeva2025 (ROADMAP 0.7 / 1.7b) ------------------------------------
GRUDEVA = DATA_DIR / "grudeva2025"


def grudeva_params():
    """Both named dimensional configs (thesis_cafe, paper_nominal) + adjudicated
    κ/P_app (transcribed from the card of record)."""
    return _typed_rows(GRUDEVA / "grudeva_params.csv")


def grudeva_vial_stats():
    """Per-vial solubles mean/SD (g) over the 14-shot C1 dataset (derived from
    the reference repo exp13.csv). G3 post-fit reconstruction target."""
    return _typed_rows(GRUDEVA / "exp13_per_vial_stats.csv")


# --- pannusch2024 (ROADMAP 1.8a), Table 2 fitted params ------------------
PANNUSCH = DATA_DIR / "pannusch2024"


def pannusch_table2():
    """Table 2 per-solute fitted params (A1,B1,A2,B2,K_ref,gamma,c_s0)."""
    return _typed_rows(PANNUSCH / "table2_fitted_params.csv")


def pannusch_experimental_kinetics():
    """Schmieder/Pannusch extraction kinetics: per (exp, fraction) T, flow,
    fraction time bounds, and measured caffeine/trigonelline/5CQA/TDS. Derived
    from the reference repo ExperimentalData.mat (15 exp x 6 fractions)."""
    return _typed_rows(PANNUSCH / "experimental_kinetics.csv")


# --- foster2025_2 machine mode (ROADMAP 0.11 / 1.6) ----------------------
FOSTER2 = DATA_DIR / "foster2025_2"


def foster2025_params():
    """Foster Table I/II machine-mode parameters (transcribed from the card)."""
    return _typed_rows(FOSTER2 / "foster2025_params.csv")


def foster_fig15_flow():
    """Fig 15: normalized bed flow Q/Qm + headspace pressure vs experiment time."""
    return _typed_rows(FOSTER2 / "fig15_flow_pressure.csv")


def foster_fig12_14_curves():
    """Figs 12-14: model fitted s/w/H curves + CT data (mm) vs experiment time."""
    return _typed_rows(FOSTER2 / "fig12_14_fitted_curves.csv")


# --- mo2023 (ROADMAP 0.4), microCT Forchheimer pairs ---------------------
MO2023 = DATA_DIR / "mo2023"
# k1 UNITS CAVEAT (§5.3): tables give k1 in 1e-9 m^2 but Forchheimer Eq.2 needs
# [k1]=m; internally inconsistent by ~1e4 vs the Fig 8b annotation. Do NOT use
# k1 quantitatively until resolved (author correspondence pending).


def mo2023_forchheimer():
    """24 microCT samples (types E/H/M/F): location, porosity, tortuosity, Darcy
    kD, Forchheimer kF, inertial k1F. Real-geometry (k, k1) pairs (§5.3 caveat)."""
    out = []
    for tbl, typ in [("table2_typeH", "H"), ("table3_typeE", "E"),
                     ("table4_typeM", "M"), ("table5_typeF", "F")]:
        for r in _typed_rows(MO2023 / f"{tbl}_samples.csv"):
            r["type"] = typ
            out.append(r)
    return out


def mo2023_fig8a():
    """Fig 8a: apparent Darcy permeability kD vs pressure gradient (the canonical
    'why literature k disagrees' Darcy->Forchheimer decline)."""
    return _typed_rows(MO2023 / "fig8a_permeability_vs_pressure_gradient.csv")


def mo2023_psd():
    """Table 1: laser-diffraction PSD (d32, d43, uniformity) per powder type."""
    return _typed_rows(MO2023 / "table1_laser_diffraction.csv")


# --- egidi2024 (ROADMAP 0.3), RC-1 EY/TDS bracket ------------------------
EGIDI = DATA_DIR / "egidi2024"


def egidi_table2():
    """Table 2: 12-condition (T x p x grind) TDS mean/sigma + EY. The independent
    RC-1 EY/TDS *range bracket* (not a pressure/T response test — p,T are
    absorbed into q,tau in the egidi model)."""
    return _typed_rows(EGIDI / "table2_egidi2024_tds_ey.csv")


# --- romancorrochano2017 (ROADMAP 0.5), EngD thesis --------------------------
# Multi-scale extraction (implement-later) + tamped permeability (DATA-ONLY: the
# K-C closures are lower-fidelity than the registered wadsworth2026.inertial, so
# Table 6.1 serves as a permeability validation TARGET / G9, not a component).
RC17 = DATA_DIR / "romancorrochano2017"


def roman_tamped_kappa():
    """Table 6.1: steady-state Darcy permeability kappa [m^2] on fully-extracted,
    tamped/consolidated espresso beds -- 4 grinds (PsiB-PsiE) x 3 initial bed
    densities (360/400/480 kg/m^3), with +/-1 SD and ANOVA/Tukey sig letters.
    G9 permeability target + §5.5. NOT a K-C validation (permeability card)."""
    return _typed_rows_hashskip(RC17 / "table6_1_tamped_kappa.csv")


def roman_deff():
    """Table 4.9: microstructural (non-fitted) effective diffusion coefficients
    Deff [x1e-11 m^2/s, 80 C] per grind x 4 MW classes (low/med/high/vhigh)."""
    return _typed_rows_hashskip(RC17 / "table4_9_deff.csv")


def roman_partition_K():
    """Table 4.10: solid-liquid partition K vs T (Arrhenius ln K = -657/T + 1.4,
    R^2=0.91); swelling factor S=1 (none observed)."""
    return _typed_rows_hashskip(RC17 / "table4_10_partition_K.csv")


def roman_hindrance():
    """Tables 4.8/4.7/4.6 joined: microstructural hindrance Hm, particle
    tortuosity (CPSM), and particle porosity (open/closed/total) per blend."""
    return _typed_rows_hashskip(RC17 / "table4_8_hindrance.csv")


def roman_Db():
    """Table 3.4: bulk diffusion coefficient Db [m^2/s, 80 C] per MW category
    (Stokes-Einstein)."""
    return _typed_rows_hashskip(RC17 / "table3_4_Db.csv")


def roman_mpe_table53():
    """Table 5.3: stirred-vessel MPE per grind (single Deff fitted to all grinds
    jointly vs each grind individually; NOT the 1-Deff-vs-4-Deff comparison --
    that is Figs 5.11/5.13)."""
    return _typed_rows_hashskip(RC17 / "table5_3_mpe.csv")


def roman_fig511_mpe():
    """Fig 5.11 (digitized): stirred-vessel MPE using a SINGLE Deff per MW class,
    per grind. ~+/-0.5 pp raster fidelity."""
    return _typed_rows_hashskip(RC17 / "fig5_11_mpe_single_deff.csv")


def roman_fig513_mpe():
    """Fig 5.13 (digitized): stirred-vessel MPE for best-single vs two 4-Deff
    ensemble weightings -- the ~5-8% multiple-Deff numbers. ~+/-0.5 pp."""
    return _typed_rows_hashskip(RC17 / "fig5_13_mpe_scenarios.csv")


def _mo2():
    return DATA_DIR / "mo2023_2"


def mo2_granulometry():
    """mo2023_2 Table 1: bimodal granulometry per powder (E/H/M/F) -- fine/coarse
    volume fractions theta_f/theta_c, representative diameters 2R_f/2R_c (um),
    Sauter d_[3,2] (um). Feeds the Carman-Kozeny k0 closure."""
    return _typed_rows(_mo2() / "table1_granulometry.csv")


def mo2_k0():
    """mo2023_2 Table 2: derived Carman-Kozeny k0 [m^2] per powder (t=0 flow
    closure sanity check; the k0 verification target)."""
    return _typed_rows(_mo2() / "table2_k0.csv")


def mo2_yield_strength():
    """mo2023_2 Figs 6-9 (digitized): fixed-flow-rate experimental yield & strength
    [%] vs beverage mass M_c [g], powders {E,M,F} x q {2,3,4 mL/s}, with 3-replicate
    error bars. Rare fixed-flow espresso validation data (the paper's main value)."""
    return _typed_rows(_mo2() / "figs6_9_yield_strength.csv")


def mo2_fig3a_qdecay():
    """mo2023_2 Fig 3(a) (digitized): simulated superficial velocity q(t) [mm/s]
    under swelling at fixed dP, per powder, at swelling s_m in {0, 3.6}%. Model
    output (verification twin target), not experimental data."""
    return _typed_rows(_mo2() / "fig3a_qdecay.csv")


def mo2_fig6_ksweep():
    """mo2023_2 Fig 6 (digitized): type-M yield/strength vs M_c under a sweep of
    the partition coefficient K (note: captions mislabel K as 'hindrance')."""
    return _typed_rows(_mo2() / "fig6_Ksweep_typeM.csv")


def mo2_sim_lines():
    """mo2023_2 Figs 7-9 (digitized): the MODEL yield/strength curves overlaid on
    the experimental points, powders {E,M,F} x q {2,3,4}. Simulation lines."""
    return _typed_rows(_mo2() / "figs7_9_simulation_lines.csv")


def schulman_baskets():
    """schulman2011 filter-basket geometry: 14 baskets x (base diameter, mean hole
    diameter, hole sigma, total open area A_h, grid). Enables an orifice/Poiseuille
    screen-resistance CONSTRUCTION for G9 -- the source measured NO ΔP/resistance."""
    return _typed_rows_hashskip(DATA_DIR / "schulman2011" / "basket_geometry.csv")


def angeloni_inventories():
    """angeloni2023 Table 7: measured R&G solid inventory C0_s [mg/L] per species
    (CF/CQA/TR/CA/AA/TA/FA/LP) per variety (Arabica/Robusta). Extraction-inventory
    priors + an INDEPENDENT multi-species target (different machine/coffee/basket
    than pannusch's fit)."""
    return _typed_rows_hashskip(DATA_DIR / "angeloni2023" / "inventories.csv")


def angeloni_bioactives():
    """angeloni2023 Tables 4+5: per-species bioactives [g/L] for all 66 shots
    (33 Arabica + 33 Robusta), joined to the Table 1 condition matrix. Species:
    TR TA AA CA 3CQA 5CQA CF FA 3_5diCQA totCQA totOA. on_grid ('True'/'False')
    flags the 54 calibration vs 12 off-grid validation points."""
    return _typed_rows_hashskip(DATA_DIR / "angeloni2023" / "bioactives.csv")


def angeloni_total_solids():
    """angeloni2023 Table 2: total solids TS [g/100 mL] + %RSD, 66 shots, joined
    to conditions. (TS g/100 mL ~ TDS %.)"""
    return _typed_rows_hashskip(DATA_DIR / "angeloni2023" / "total_solids.csv")


def angeloni_lipids():
    """angeloni2023 Table 3: total lipids [g/100 mL] + %RSD, 66 shots, joined to
    conditions."""
    return _typed_rows_hashskip(DATA_DIR / "angeloni2023" / "lipids.csv")


def _fasano1():
    return DATA_DIR / "fasano2000_partI"


def fasano_fig8_1():
    """Fig 8.1 (digitized, schematic): EXPERIMENTAL discharge q(t) [mL/s] during
    percolation at 3/5/7 bar (illycaffe) -- transient peak then decay to a
    nonmonotone-in-pressure asymptote. Low fidelity, qualitative only."""
    return _typed_rows(_fasano1() / "fig8_1_discharge_vs_pressure.csv")


def fasano_fig8_4():
    """Fig 8.4 (digitized): direct/inverse chamber discharge in 3 segments --
    (1) direct percolation decay, (2) pressure off/on resumes at the low plateau
    (ordinary porous medium), (3) chamber INVERTED replays the full peak+decay
    (the fines counter-migration reversal signature)."""
    return _typed_rows(_fasano1() / "fig8_4_direct_inverse.csv")


def fasano_fig8_6():
    """Fig 8.6 (digitized): MODEL asymptotic discharge q_inf vs applied pressure
    p0 for threshold functions beta1, beta2 (mu=0.5; Suski free-boundary
    simulation). The nonmonotone q_inf(p0) result. Verification of a digitized
    model output -- NOT reproducible from scratch (closures K,M,gamma unpublished)."""
    return _typed_rows(_fasano1() / "fig8_6_asymptotic_q_vs_p0.csv")


def fasano_fig8_7():
    """Fig 8.7 (digitized): the detachment-threshold shapes beta1(q), beta2(q)
    fed to the Fig 8.6 simulation -- monotone-decreasing with a steep drop (the
    threshold the flow must cross for nonmonotone q_inf, per Cor. 8.2)."""
    return _typed_rows(_fasano1() / "fig8_7_thresholds.csv")


def roman_y0_extractable():
    """Section 4.4.1 + Fig 4.19: long-time-limit extractable soluble solids y0
    [kg SS/100 kg RGC = %] per grind, 80 C dilute. PsiA (finest) exact from text
    (31.7 dilute / 32.15 equilibrium); other grinds derived from the normalized
    Fig 4.19 (~+/-0.5 pp). Feeds §5.5 nested-ceiling cross-check + P3 hypothesis
    #4 (size-exclusion: y0 decreases monotonically with coarsening grind)."""
    return _typed_rows_hashskip(RC17 / "y0_extractable.csv")


def roman_fig74_espresso():
    """Fig 7.4 (digitized MPE) joined with Tables 7.1/7.2 (exact conditions): the
    15 espresso flow/density conditions with Deff/K metadata and the
    PARAMETER-FREE bed-scale MPE. MPE_med_MW_pct is the headline non-fitted
    result (8.6-14.3% across all 15) -> the thesis '9-14%' / <=14% bed gate."""
    return _typed_rows_hashskip(RC17 / "fig7_4_mpe_espresso.csv")


# --- G1/G3/G10 reference-strength sourcing (2026-07-12) ---
# REFERENCE/qualitative priors, not independent measurements. The strength tag
# lives in MANIFEST.csv; loaders do no fitting.
from pathlib import Path as _Path
_SRC0712 = _Path(__file__).parent
G1GB = _SRC0712 / "g1_glassbead_analog"
G3PC = _SRC0712 / "g3_pump_characteristic"
G10R = _SRC0712 / "g10_liquor_rheology"


def glassbead_retention_kr():
    """Glass-bead retention/K_r closure (ANALOG shape prior, arXiv:2501.13361).
    REFERENCE-STRENGTH: spherical glass beads, NOT coffee. Transfers K_r(S)
    shape + S_r + linearized-VG slope, NOT magnitude. Coffee retention search
    target STAYS OPEN. Rows keyed by 'quantity' (the CSV also carries a separate
    'parameter' symbol column; the duplicate 'capillary_pressure_slope' rows
    collapse to the last, which the closure gate does not consume)."""
    return {r["quantity"]: r for r in _rows(G1GB / "glassbead_retention_kr.csv")}


def pump_characteristic_ulka():
    """Ulka vibe-pump P-Q envelope + DE1-shape context (reference/qualitative).
    Manufacturer ENDPOINTS only measured (+/-15%); interior curve is a CONCAVE
    DROOP, not a quadratic. True DE1 Q(P) is closed firmware. Rows keyed by
    'quantity'."""
    return {r["quantity"]: r for r in _rows(G3PC / "pump_characteristic_ulka.csv")}


def liquor_rheology():
    """Coffee-extract mu(T,c)/rho(T,c) envelope (Telis-Romero; reference).
    Espresso TDS sits BELOW the sources' dilute end -> mu_espresso is an
    EXTRAPOLATION toward pure water. Espresso IS Newtonian. Rows keyed by
    'quantity' (numeric/form values live in the 'value_or_form' column)."""
    return {r["quantity"]: r for r in _rows(G10R / "liquor_rheology.csv")}


# --- bruno2026 roasted chemistry (item 0.8; Sci. Rep. 16, 15857, CC BY 4.0) ---
BRUNO = DATA_DIR / "bruno2026"


def bruno_roasted_composition():
    """Bruno 2026 Table 2 — four roasted single origins x ten compounds (mean, SD),
    long format. DATA-ONLY (roasting is upstream of the registry; the ODE model is
    NOT implemented, per the card). Serves the G6 / ledger-A4 SoluteInventory prior:
    an INDEPENDENT measured roasted-chemistry reference set (mg/kg roasted powder;
    lipids % w/w dry basis). n=3 per cell."""
    return _rows(BRUNO / "bruno2026_roasted_composition.csv")


def bruno_roasted_composition_wide():
    """Bruno 2026 Table 2 in wide format (one row per compound; origin columns).
    Same data as `bruno_roasted_composition`, convenience layout."""
    return _rows(BRUNO / "bruno2026_roasted_composition_wide.csv")
