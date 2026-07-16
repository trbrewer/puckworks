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


def paper_b_evidence_matrix():
    """Committed structured evidence matrix for Paper B Figure 2 (review MAJ-09): one
    row per mechanism with a DEFINED status per dimension + the decisive missing
    measurement + a source citation, so the figure is generated from data, not
    hard-coded plotting cells."""
    return _rows(DATA_DIR / "paper_b_evidence_matrix.csv")


def paper_b_evidence_dictionary():
    """Data dictionary for Figure 2 (review MAJ-20/B3-20): one row per (dimension,
    status_token) defining every status word used in the evidence matrix, plus the
    ROADMAP Sec 0 validation rung it maps to. This is the published legend so no matrix
    cell is an undefined token."""
    return _rows(DATA_DIR / "paper_b_evidence_dictionary.csv")


def paper_b_evidence_dictionary_audit():
    """MAJ-20 completeness gate: every status token that appears in the matrix must be
    defined in the dictionary, and every implemented/not-implemented mechanism must carry
    a citation. Returns the set of undefined tokens and uncited mechanisms (both empty on
    a complete dictionary) so a test/gate can assert closure without hard-coding the
    vocabulary."""
    rows = paper_b_evidence_matrix()
    dims = ["implemented", "observable", "params_provenance",
            "generates_interior_max", "evidence_strength"]
    defined = {(r["dimension"], r["status_token"])
               for r in paper_b_evidence_dictionary()}
    undefined = sorted({(dim, r[dim]) for r in rows for dim in dims
                        if (dim, r[dim]) not in defined})
    uncited = sorted(r["mechanism"] for r in rows
                     if not r.get("citation", "").strip())
    return {"undefined_tokens": undefined, "uncited_mechanisms": uncited,
            "complete": (not undefined and not uncited)}


# --- visualizer.coffee two-tier store (ROADMAP 0.13; DATA-ONLY) ----------
# The corpus is gitignored and NOT redistributed (see visualizer/PROVENANCE.md +
# docs/cards/visualizer_coffee.md). These loaders READ the on-disk store at
# runtime and degrade gracefully when it is absent — the corpus is populated by
# `python -m puckworks.lib.visualizer_harvest full`, never by a test.
VIS = DATA_DIR / "visualizer"
VIS_RAW = VIS / "raw"

# stored-unit contract (asserted per CLAUDE.md rule 7). SERIALIZER_REVIEW §8: only the
# scale-derived mass flow is a confirmed kg/s quantity; the reported/ambiguous flow channels
# (flow_reported__native, flow_goal_reported__native) are stored NATIVE with units.si=None
# and are deliberately absent here so visualizer_hydraulic never surfaces them as SI.
_VIS_HYDRAULIC_SI = {
    "time__s": "s", "pressure__Pa": "Pa", "pressure_goal__Pa": "Pa",
    "mass_flow_from_scale__kg_per_s": "kg/s", "weight__kg": "kg",
    "water_dispensed__kg": "kg",
    "temperature_basket__K": "K", "temperature_mix__K": "K",
    "temperature_goal__K": "K",
}
_VIS_OUTCOME_SI = {"tds__fraction": "fraction", "ey__fraction": "fraction"}


def visualizer_index():
    """Return the LATEST-version-per-shot summary (§3) if the corpus is on disk, else
    {'present': False}. `n_shots` counts unique live shot ids (not stored versions);
    `n_versions` is the total append-only row count; `rows` is the latest row per id.
    Never raises on an absent corpus."""
    p = VIS_RAW / "_index.csv"
    if not p.exists():
        return {"present": False}
    from types import SimpleNamespace
    from puckworks.lib import visualizer_harvest as _vh
    shim = SimpleNamespace(out_dir=VIS_RAW)
    latest = _vh.latest_index_rows(shim)
    n_versions = sum(1 for _ in _vh.iter_index_rows(shim))
    return {"present": True, "n_shots": len(latest), "n_versions": n_versions,
            "rows": list(latest.values())}


def _vis_corpus_present():
    return VIS_RAW.exists() and any(VIS_RAW.glob("shard_*.jsonl.gz"))


def visualizer_iter_shots(filter=None, versions=False):
    """Yield TidyShot dicts from the gitignored shards (generator; never loads all into
    memory). By default yields the LATEST version per shot id (§3); pass ``versions=True``
    for the full append-only history. Optional ``filter`` is a predicate on the shot dict.

    Raises a clear 'run the harvester' RuntimeError when the corpus is absent —
    this is a MISSING-DATA condition, not a test failure (tests use fixtures)."""
    if not _vis_corpus_present():
        raise RuntimeError(
            "visualizer corpus not found under %s — it is gitignored and not "
            "redistributed. Populate it with: pip install -e \".[harvest]\" && "
            "python -m puckworks.lib.visualizer_harvest full "
            "(see puckworks/data/visualizer/PROVENANCE.md)." % VIS_RAW)
    from types import SimpleNamespace
    from puckworks.lib import visualizer_harvest as _vh
    shim = SimpleNamespace(out_dir=VIS_RAW)
    source = _vh.iter_store(shim) if versions else _vh.iter_store_latest(shim)
    for shot in source:
        if filter is None or filter(shot):
            yield shot


def visualizer_hydraulic(shot):
    """Return the hydraulic tier of a TidyShot as SI numpy arrays, asserting the
    per-channel stored unit matches the SI contract (rule 7). Missing channels
    are simply absent from the returned dict (never invented)."""
    hy = shot.get("hydraulic") or {}
    units = (shot.get("units") or {}).get("hydraulic") or {}
    out = {}
    for name, series in hy.items():
        if name == "state_change":
            out[name] = np.asarray(series)  # categorical codes, no unit
            continue
        if (units.get(name) or {}).get("si") is None:
            # §8: an explicitly-native / unit-ambiguous channel (e.g. reported pump flow) is
            # NOT SI mass flow -- excluded here so it can't be mistaken for kg/s. Read it
            # directly from shot["hydraulic"] with its `semantic` tag if you need it.
            continue
        expected = _VIS_HYDRAULIC_SI.get(name)
        if expected is not None:
            got = (units.get(name) or {}).get("si")
            assert got == expected, (
                "visualizer hydraulic channel %r stored as %r, expected SI %r "
                "(rule 7)" % (name, got, expected))
        out[name] = np.asarray([np.nan if v is None else v for v in series],
                               dtype=float)
    return out


def visualizer_outcomes(shot):
    """Return the user-entered outcomes tier (tds/ey fractions + sensory ints),
    asserting the stored unit is a dimensionless fraction where present (rule 7).

    These are NOT groundtruth (see PROVENANCE.md) — the accessor does not upgrade
    them; it only surfaces them with their units checked."""
    oc = shot.get("outcomes") or {}
    units = (shot.get("units") or {}).get("outcomes") or {}
    out = {"sensory": dict(oc.get("sensory") or {})}
    for name, expected in _VIS_OUTCOME_SI.items():
        val = oc.get(name)
        if val is not None:
            got = (units.get(name) or {}).get("si")
            assert got == expected, (
                "visualizer outcome %r stored as %r, expected %r (rule 7)"
                % (name, got, expected))
        out[name] = val
    return out


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


def mckeonaloe_baskets():
    """mckeonaloe2022 filter-basket open-area + hole geometry: 2 baskets (Wafo Classic,
    VST) x 2 faces (exit/coffee) with open-area fraction (%) and mean/std hole diameter
    (µm). SINGLE-SPECIMEN hobbyist imaging (n=1 basket each); open-area is direct, mean
    diameters are read off the source bar charts (`mean_hole_diam_approx`=True), no pixel
    calibration or hole count published. Both baskets taper wider on the coffee face
    (top/bottom mean-diameter ratio > 1, so the exit face is flow-limiting). Complements
    the multi-brand `schulman_baskets` table for the G9 exit-boundary gap; measures
    geometry only (no ΔP/resistance) -- a reference/qualitative seed, not a G9 closure."""
    return _typed_rows_hashskip(DATA_DIR / "mckeonaloe2022" / "basket_open_area_geometry.csv")


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
    'quantity' (numeric/form values live in the 'value_or_form' column).
    SUPERSEDED for the numeric estimate by `telisromero_viscosity_pas` (the actual
    transcribed Eq-10 closure, card docs/cards/telisromero2001.md)."""
    return {r["quantity"]: r for r in _rows(G10R / "liquor_rheology.csv")}


def telisromero_rheology_closures():
    """Fitted rheology closures transcribed from docs/cards/telisromero2001.md
    (Eqs 10/12/13), keyed by equation. Coefficients only; NOT the raw Table 1/Table 2
    grids (those remain a digitization target needing the paper)."""
    return {r["equation"]: r for r in _rows(G10R / "telisromero2001_closures.csv")}


def telisromero_rheology_anchors():
    """The two card-quoted MEASURED anchor points (Table 1 eta; Table 2 K) used to gate
    that the Eq-10/13 closures were transcribed faithfully."""
    return _rows(G10R / "telisromero2001_anchors.csv")


_R_GAS = 8.314   # J/(mol K)


def telisromero_viscosity_pas(T_K, Xw_pct):
    """Telis-Romero 2001 Eq. (10) Newtonian viscosity closure [Pa*s].

    eta = 1.99e6 * exp(14514/(R*T)) * Xw^-6.07, with T in KELVIN and Xw in PERCENT water
    (wet basis) -- NOT a fraction (feeding fraction-form Xw is a documented ~10^2.6-10^6
    hazard, card normalization note). Valid box: Xw 76-90 %, T 295-365 K (Newtonian domain).
    At bulk espresso TDS (Xw~90, T~363 K) this gives ~1.06x pure water -- a NEGLIGIBLE
    correction, correcting the paywalled-snippet envelope's ~1.3-2x guess; the 1.3-2x (up to
    ~2-3x) applies to concentrated EARLY IN-PORE liquor (Xw~76). Composition caveat: fit on
    industrial soluble-coffee extract, not fresh espresso liquor."""
    import math
    c = telisromero_rheology_closures()["eq10_newtonian"]
    return (float(c["pre_factor"]) * math.exp(float(c["Ea_or_A"]) / (_R_GAS * T_K))
            * Xw_pct ** float(c["Xw_exponent"]))


def telisromero_table1_eta():
    """Telis-Romero 2001 Table 1 (Newtonian domain) MEASURED viscosity, long format:
    eta [Pa*s] at 4 water fractions (76-90 %w/w) x 6 temperatures (295-365 K). 24 cells.
    Digitized by Tim from the paywalled paper (source md in data/telisromero2001/).
    The transcribed Eq (10) closure reproduces these within the authors' stated ~2.34%
    mean error (gate_g10_telisromero_full_table)."""
    return _rows(G10R / "telisromero2001_table1_eta.csv")


def telisromero_table2_Kn():
    """Telis-Romero 2001 Table 2 (power-law domain) MEASURED consistency index K [Pa*s^n]
    and behavior index n at 3 water fractions (49-64 %w/w) x 9 temperatures (274-353 K).
    27 cells. Concentrated / first-drip regime (>36% solids). n = 0.87-0.97 (near-Newtonian)."""
    return _rows(G10R / "telisromero2001_table2_Kn.csv")


def telisromero_eta_measured(T_K, Xw_pct):
    """Bilinear interpolation of the MEASURED Table-1 eta(Xw, T) grid [Pa*s]. T in KELVIN,
    Xw in PERCENT water. Clamps to the measured box (Xw 76-90 %, T 295-365 K) -- callers
    handle out-of-box extrapolation explicitly (espresso is MORE dilute than 90% Xw, i.e.
    an extrapolation toward pure water; the concentrated <76% regime is Table 2). Prefer
    this over the Eq-10 closure when you want measured data rather than the fit."""
    rows = telisromero_table1_eta()
    xs = sorted({float(r["Xw_pct"]) for r in rows})
    ts = sorted({float(r["T_K"]) for r in rows})
    grid = {(float(r["Xw_pct"]), float(r["T_K"])): float(r["eta_Pas"]) for r in rows}
    x = min(max(Xw_pct, xs[0]), xs[-1])
    t = min(max(T_K, ts[0]), ts[-1])
    x0 = max([v for v in xs if v <= x], default=xs[0])
    x1 = min([v for v in xs if v >= x], default=xs[-1])
    t0 = max([v for v in ts if v <= t], default=ts[0])
    t1 = min([v for v in ts if v >= t], default=ts[-1])
    fx = 0.0 if x1 == x0 else (x - x0) / (x1 - x0)
    ft = 0.0 if t1 == t0 else (t - t0) / (t1 - t0)
    e00, e01 = grid[(x0, t0)], grid[(x0, t1)]
    e10, e11 = grid[(x1, t0)], grid[(x1, t1)]
    return ((1 - fx) * (1 - ft) * e00 + (1 - fx) * ft * e01
            + fx * (1 - ft) * e10 + fx * ft * e11)


def telisromero_thermal_closures():
    """Telis-Romero 2000 thermophysical closures (rho/cp/k/alpha) transcribed from
    docs/cards/telisromero2000.md. Keyed by equation. Companion to the 2001 rheology
    closures -- together a mutually consistent mu/rho/cp/k/alpha(T,X_w) liquor set from
    one material batch family. NOTE the Xw_basis field is 'mass_fraction_0_1' (0-1), NOT
    the PERCENT the 2001 rheology closures use -- see the normalization guard below."""
    return {r["equation"]: r for r in _rows(G10R / "telisromero2000_closures.csv")}


def telisromero_thermal_anchors():
    """Figure-read / water-limit endpoint anchors for the 2000 thermal closures."""
    return _rows(G10R / "telisromero2000_anchors.csv")


def _tr2000_check_frac(Xw_frac):
    # Normalization guard (card hazard): the 2000 closures take X_w as a FRACTION (0-1),
    # while telisromero_viscosity_pas takes PERCENT. A percent value (49-90) slipped in
    # here would silently produce garbage -> fail loud instead (ledger-A7 spirit).
    if not (0.0 < Xw_frac <= 1.0):
        raise ValueError(
            f"telisromero2000 closures take X_w as a FRACTION in (0,1], got {Xw_frac}. "
            "Did you pass PERCENT (the telisromero2001 rheology basis)?")


def telisromero_density_kgm3(T_C, Xw_frac):
    """Telis-Romero 2000 Eq. (1) liquor density [kg/m^3]. T in degC, X_w mass FRACTION.
    rho = 1422.57 - 451.98*Xw - 0.16*T. Espresso edge (Xw~0.90, ~82C) -> ~1003 (<=1% over
    water, negligible for Darcy); first-drip (Xw=0.49) -> ~1196 (20% mass<->volume effect)."""
    _tr2000_check_frac(Xw_frac)
    c = telisromero_thermal_closures()["eq1_density"]
    return (float(c["intercept"]) + float(c["Xw_coeff"]) * Xw_frac
            + float(c["T_coeff"]) * T_C)


def telisromero_thermal_diffusivity_m2s(T_C, Xw_frac):
    """Telis-Romero 2000 Eq. (6) DIRECT thermal diffusivity [m^2/s], TYPO-CORRECTED
    coefficient (2.12e-10, not the printed 0.0212e-10). T in degC, X_w mass FRACTION.
    The direct alpha is convection-biased HIGH vs the self-consistent k/(rho*cp) path
    (authors' mean offset -11.35%); do NOT mix the two paths (card)."""
    _tr2000_check_frac(Xw_frac)
    c = telisromero_thermal_closures()["eq6_alpha_direct"]
    return (float(c["intercept"]) + float(c["Xw_coeff"]) * Xw_frac
            + float(c["T_coeff"]) * T_C)


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


def khomyakov_kinematic_viscosity():
    """khomyakov2020 (DOI 10.1088/1755-1315/548/2/022040, CC BY 3.0) MEASURED
    coffee-extract KINEMATIC viscosity [mm^2/s], Table 1: dry-solids 15-70 wt% x
    T 20-80 C (60 pts). REFERENCE/qualitative for espresso -- DOMAIN GUARD: the
    lowest measured solids is 15 wt%, ABOVE espresso TDS (~4-12 wt%), so espresso
    use is an extrapolation toward the dilute end; do NOT extrapolate below 15 wt%
    silently. Industrial soluble-coffee extract, not a fraction-resolved espresso
    series. NOTE: the source's density + dynamic-viscosity REGRESSIONS are
    QUARANTINED (khomyakov2020_*_QUARANTINED/FLAGGED.csv in this dir; sign/typeset
    conflicts) -- NOT loaded; only this measured kinematic table is usable."""
    return _rows(G10R / "khomyakov2020_kinematic_viscosity.csv")


# --- ellero2019 digitized figures (G2 pointer; SPH SIMULATION, dimensionless) --
# FIGURE-DIGITIZED (pixel extraction), QUALITATIVE strength. These are the SPH
# model's OWN output in simulation units with nominal parameters -- they
# characterize the model, NOT coffee (ellero2019 card VERDICT: skip). The only
# experimental content is the fig2 Ref.[8] transient-discharge markers overlaid on
# the sim. Does NOT close G2: the raw ASIC 1993/1997 discharge series is still owed.
ELLERO = DATA_DIR / "ellero2019"


def _ellero_wide(fname, xcol="t_over_tnu"):
    """Parse a sparse wide digitized CSV (x column + one column per curve, blanks
    where a curve is not sampled) -> {curve_name: {'x': [...], 'y': [...]}}."""
    rows = _rows(ELLERO / fname)
    curves = [c for c in rows[0] if c != xcol]
    out = {c: {"x": [], "y": []} for c in curves}
    for r in rows:
        x = float(r[xcol])
        for c in curves:
            v = r.get(c, "")
            if v not in ("", None):
                out[c]["x"].append(x)
                out[c]["y"].append(float(v))
    return out


def ellero_fig2_forcing():
    """Fig 2 left — inverse-discharge applied forcing F/F0 (step ±1/0), exact
    breakpoints. Rows: t_over_tnu, F_over_F0."""
    return _rows(ELLERO / "fig2_inverse_discharge_applied_forcing.csv")


def ellero_fig2_ref8_markers():
    """Fig 2 right — the overlaid Ref.[8] EXPERIMENTAL transient-discharge markers
    (38 recovered open circles; |Re| vs t/tnu). The only non-simulation content in
    the digitized set; early points (t<~6) carry ~+/-0.3 Re (notes)."""
    return _rows(ELLERO / "fig2_inverse_discharge_reynolds_data_ref8.csv")


def ellero_fig2_reynolds():
    """Fig 2 right — SPH |Re|(t/tnu) per theta (6 curves). Pump-off windows
    (~37.6-52.6, ~75.2-90.2) read as Re~0 (notes)."""
    return _ellero_wide("fig2_inverse_discharge_reynolds_vs_theta.csv")


def ellero_fig3_reynolds():
    """Fig 3 left — direct-discharge SPH |Re|(t/tnu) per theta (4 curves)."""
    return _ellero_wide("fig3_direct_discharge_reynolds_vs_theta.csv")


def ellero_fig3_concentration():
    """Fig 3 right — direct-discharge cumulative output concentration [%] per theta
    (4 curves). Exploratory sweep, no experimental comparison (card)."""
    return _ellero_wide("fig3_direct_discharge_cumulative_output_concentration.csv")


def ellero_fig4_caffeine_Db():
    """Fig 4 left — caffeine content [%] vs t/tnu varying bulk diffusion Db
    (Dr=0.0005, theta=0.0058 fixed; 5 curves). Exploratory sweep (card)."""
    return _ellero_wide("fig4_direct_discharge_caffeine_content_vary_Db.csv")


def ellero_fig4_caffeine_Dr():
    """Fig 4 right — caffeine content [%] vs t/tnu varying release rate Dr
    (Db=0.005, theta=0.0058 fixed; 4 curves). Release rate Dr dominates in-cup
    concentration (card's central claim), not bulk diffusion Db."""
    return _ellero_wide("fig4_direct_discharge_caffeine_content_vary_Dr.csv")


# --- pocketscience2024 (radially sectioned edge/center EY; data-only) ----------
_PSCI = DATA_DIR / "pocketscience2024"


def pocketscience_edge_ey():
    """Pocket Science Coffee 2024 — 12-condition edge/center extraction-yield summary
    (data-only; card `pocketscience2024`). Card-transcribed condition means: per-section
    EY (%), fractional edge yield loss (%), and the outer-section mass fraction of dose
    (label-erratum corrected to outer-to-TOTAL). Rows are (basket, shot_style, grinder,
    puck_screen, dispersion_block). EY units are percent (dimensionless yields; no SI
    conversion). NOT a model; no gate against the source. See PROVENANCE.md."""
    return _rows(_PSCI / "edge_ey_condition_means.csv")


def pocketscience_lrr():
    """Pocket Science Coffee 2024 — grinder-level liquid-retained-ratio (LRR) means
    (g water / g dose), lumped post-flush retention (n=5 each). NOT in-shot dead water
    and NOT a retention curve theta(psi): does not satisfy the G1 search target."""
    return _rows(_PSCI / "lrr_scalars.csv")


# --- canonical visualizer corpus snapshot interface (WP0/PR1) --------------
# Analysis code should consume CorpusSnapshot, never the raw shard iterator.
from puckworks.data.visualizer_store import (   # noqa: E402
    CorpusSnapshot, measurement_dictionary, is_pooling_safe, freeze_snapshot,
)
