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
