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
