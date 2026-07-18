"""PV-04 "How We Falsified Our Own Espresso Headline" — the analysis-autopsy public data contract.

A deterministic transform of ONE named producer (`puckworks.harness.result1_magnitude_comparison`)
into a compact public snapshot (`puckworks/public/data/pv04_analysis_autopsy.json`) that the static
interactive and the PV-04 ``PublicClaim`` producer consume. **No headline number is hand-typed** — the
producer is authoritative, and the snapshot records the SHA-256 of the canonical CC-BY Schmieder source
files so ``verify`` fails the moment the underlying data drifts.

The story is the project correcting its OWN aggregation and interpretation (not a humiliation
narrative; the source authors are not blamed):

    1. a superseded internal headline: an interior "fine-grind" extraction-yield maximum, read from a
       literal evaluation of the rounded published RSM coefficients at the central condition (~6.723 g,
       treated as if it were the real level) and a target that mixed mg solute masses with g TDS;
    2. the unit/aggregation problem — mg-scale solute masses and g-scale TDS/cup-mass quantities were
       aggregated before conversion to one coherent TDS-derived EY target;
    3. the printed-precision problem — limited printed coefficient precision makes the literal absolute
       reconstruction unreliable; the project's refit central-condition prediction (~3.918 g) is near
       the observed central mean (~3.876 g);
    4. the corrected raw-replicate result — extraction-yield CELL MEANS ordered across dial with the
       middle BELOW the coarse one, and a Welch 95% interval on the middle-minus-coarse (dial 1.7 −
       dial 2.0) contrast that excludes zero: no observed interior maximum in these cells;
    5. the model still has the CAPACITY to draw such an interior feature, but the tested feature is
       smaller than the descriptive replicate spread — model capacity is not mechanism identification.

Self-correction here does NOT prove every current result is right; it documents one downgrade.

CLI::

    python -m puckworks.public.analysis_autopsy export
    python -m puckworks.public.analysis_autopsy verify

Runtime: :func:`pv04_values` reads the packaged snapshot (works from an installed wheel).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import struct
import subprocess
import zlib
from pathlib import Path

SCHEMA_VERSION = 2                        # v2: additive replicate-level + evidence-partition contract
STORY_ID = "PV-04"
TITLE = "How We Falsified Our Own Espresso Headline"
_PKG_DIR = Path(__file__).resolve().parent
_REPO = _PKG_DIR.parents[1]
SNAPSHOT = _PKG_DIR / "data" / "pv04_analysis_autopsy.json"
SITE_DIR = _REPO / "docs" / "public" / "site" / "analysis-autopsy"
GENERATOR = "puckworks.public.analysis_autopsy.build_payload"
PRODUCER = "puckworks.harness.result1_magnitude_comparison"
BADGE = "OBSERVED"                        # global badge: the corrected observation of measured replicates
EVIDENCE_STRENGTH = "independent"         # raw replicates, independent of the fit (UNCHANGED)

_SCHM_DIR = _REPO / "puckworks" / "data" / "schmieder2023"
_SOURCE_DATA_FILES = {
    "cup_masses.csv": _SCHM_DIR / "cup_masses.csv",
    "rsm_coefficients.csv": _SCHM_DIR / "rsm_coefficients.csv",
}

DIAL_LABELS = ["dial 1.4 (finer)", "dial 1.7 (middle)", "dial 2.0 (coarser)"]

DATASET_MANIFEST_IDS = ["schmieder2023/cup_masses", "schmieder2023/rsm_coefficients"]
ATTRIBUTION = ("Schmieder, Pannusch, Vannieuwenhuyse, Briesen, Minceva (2023), 'Influence of flow "
               "rate, particle size, and temperature on espresso extraction kinetics', Foods 12, 2871, "
               "DOI 10.3390/foods12152871, open access CC-BY. DERIVED replicate-level extraction-yield "
               "values and RSM predictions are published with attribution; no raw source CSV is "
               "redistributed.")
SOURCE_IDS = {"schmieder_doe": "Foods 12, 2871 (DOI 10.3390/foods12152871, CC-BY)"}

# public value key -> dotted path into result1_magnitude_comparison()'s return (the no-hand-typed rule)
_VALUE_PATHS = {
    "ey_dial_1p4_pct": "raw_tds_ey.0",
    "ey_dial_1p7_pct": "raw_tds_ey.1",
    "ey_dial_2p0_pct": "raw_tds_ey.2",
    "mid_vs_coarse_contrast_EYpt": "raw_mid_vs_coarse_contrast_EYpt",
    "welch_ci95_lo_EYpt": "raw_contrast_welch_ci95.0",
    "welch_ci95_hi_EYpt": "raw_contrast_welch_ci95.1",
    "mean_within_cell_std_EYpt": "raw_mean_within_cell_std_EYpt",
    "within_cell_std_EYpt": "raw_within_cell_std_EYpt",   # compat alias == mean within-cell SD
    "model_prominence_5bar_EYpt": "model_prominence_5bar_EYpt",
    "model_prominence_9bar_EYpt": "model_prominence_9bar_EYpt",
    "model_bump_lt_within_cell_var": "model_bump_lt_within_cell_var",
    "rsm_refit_central_g": "rsm_refit_central_g",
    "rsm_printed_central_g": "rsm_printed_central_g",
    "rsm_raw_central_g": "rsm_raw_central_g",
    "rsm_printed_is_rounding_artifact": "rsm_printed_is_rounding_artifact",
}

_UNITS = {
    "ey_dial_1p4_pct": "% EY", "ey_dial_1p7_pct": "% EY", "ey_dial_2p0_pct": "% EY",
    "mid_vs_coarse_contrast_EYpt": "EY-points", "welch_ci95_lo_EYpt": "EY-points",
    "welch_ci95_hi_EYpt": "EY-points",
    "mean_within_cell_std_EYpt": "EY-points", "within_cell_std_EYpt": "EY-points",
    "model_prominence_5bar_EYpt": "EY-points", "model_prominence_9bar_EYpt": "EY-points",
    "model_bump_lt_within_cell_var": "boolean",
    "rsm_refit_central_g": "g", "rsm_printed_central_g": "g", "rsm_raw_central_g": "g",
    "rsm_printed_is_rounding_artifact": "boolean",
}

# The ordered record of the revision (Scene 1). Every internal number cited here is reproducible from
# the producer (the ~6.723 g literal rounded-coefficient central value is `rsm_printed_central_g`); no
# historical number or curve is invented to dramatise the story.
REVISION_RECORD = [
    "Superseded internal headline: an interior 'fine-grind' extraction-yield maximum, read from a "
    "literal evaluation of the rounded published RSM coefficients at the central condition (~6.723 g, "
    "treated as if it were the real absolute level) and a target that mixed mg solute masses with g "
    "TDS.",
    "Problem 1 — unit/aggregation: mg-scale solute masses and g-scale TDS/cup-mass quantities were "
    "aggregated before conversion to one coherent observable; the target must first be rebuilt as a "
    "single-basis TDS-derived extraction yield.",
    "Problem 2 — printed precision: limited printed coefficient precision makes the literal absolute "
    "reconstruction unreliable; the project's least-squares refit central-condition prediction "
    "(~3.918 g) is near the observed central mean (~3.876 g). The 6.723 g figure is a literal "
    "evaluation of rounded coefficients, NOT itself a coefficient and NOT a real 1.7x over-prediction.",
    "Correction — coherent target: extraction yield rebuilt from TDS on one consistent basis, so the "
    "three dial cells can be compared as one observable.",
    "Corrected replicate-level finding: the raw cell means are ordered across dial with the middle "
    "below the coarse one (18.27 -> 19.38 -> 19.62 % EY); the Welch 95% interval on the middle-minus-"
    "coarse (dial 1.7 - dial 2.0) contrast excludes zero -> no observed interior maximum in these "
    "cells.",
    "Remaining model-capacity statement: a channeling model can still GENERATE a small interior "
    "feature, but the tested feature is smaller than the descriptive within-cell replicate spread -- "
    "model capacity, not identification of channeling as the cause.",
    "Resulting downgrade: the interior 'fine-grind maximum' interpretation is superseded and revised "
    "down to a model-capacity statement; self-correction here downgrades ONE result and does not prove "
    "every current result is correct.",
]

# The explicit evidence partitions (Phase 2): the site must not imply that all panels share the global
# OBSERVED / independent class. Each partition names its own role, badge, strength, and scope.
EVIDENCE_PARTITIONS = [
    {"partition": "corrected_replicate_data", "role": "observed", "badge": "OBSERVED",
     "strength": "independent",
     "scope": "One machine, one coffee, one campaign, and one fixed nominal central condition; the "
              "within-cell spread is run-to-run variance at a fixed NOMINAL dial (the experimental "
              "unit), with no replication across machines/coffees/campaigns. A grinder dial is not a "
              "particle size and is non-portable to another grinder without a calibrated adapter."},
    {"partition": "rounded_coefficient_and_refit_audit", "role": "derived", "badge": "RECONSTRUCTED",
     "strength": "verification",
     "scope": "A computational audit: the literal rounded-coefficient central value vs a least-squares "
              "refit vs the observed central mean. Verification against the committed data, NOT "
              "independent experimental validation."},
    {"partition": "model_interior_feature", "role": "simulated", "badge": "EXPLORATORY_SIMULATION",
     "strength": "qualitative",
     "scope": "Model capacity to draw an interior feature at two pressures, compared with the "
              "descriptive replicate spread. This is capacity, NOT identification of channeling as the "
              "cause; 0.218 EY-points is a descriptive reference, not a formal minimum-detectable-"
              "effect or noise floor."},
    {"partition": "superseded_headline", "role": "superseded", "status": "superseded/revised",
     "badge": None,
     "scope": "The interior 'fine-grind maximum' headline read from the literal rounded-coefficient "
              "central value and the mixed-unit target. Retained visibly as a revised record; it "
              "carries NO current evidence badge."},
]


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _all_finite(x) -> bool:
    if isinstance(x, bool):
        return True
    if isinstance(x, (int, float)):
        return math.isfinite(x)
    if isinstance(x, list):
        return all(_all_finite(v) for v in x)
    return True


def _source_commit() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"],
                                       stderr=subprocess.DEVNULL, cwd=str(_REPO)).decode().strip()
    except Exception:                                   # pragma: no cover
        return "UNKNOWN"


def _dig(obj, path):
    cur = obj
    for seg in path.split("."):
        cur = cur[int(seg)] if isinstance(cur, (list, tuple)) else cur[seg]
    return cur


def _r(x, n=4):
    return round(float(x), n) if isinstance(x, (int, float)) and not isinstance(x, bool) else x


def build_payload(source_commit: str | None = None) -> dict:
    """Deterministically compute the PV-04 snapshot from the named producer. No wall clock."""
    from puckworks import harness
    res = harness.result1_magnitude_comparison()

    raw = {k: _dig(res, p) for k, p in _VALUE_PATHS.items()}
    values = {k: (_r(v, 3) if not isinstance(v, bool) else v) for k, v in raw.items()}

    # replicate-level structure (grouped by dial) — the corrected observed series carries actual
    # replicate arrays, per-cell sample SDs, and n per cell, not three repeated descriptive bars.
    reps = [[_r(x, 3) for x in cell] for cell in res["raw_tds_ey_replicates"]]
    cell_stds = [_r(s, 3) for s in res["raw_tds_ey_cell_stds"]]
    ns = [int(n) for n in res["raw_tds_ey_ns"]]
    ey_means = [values["ey_dial_1p4_pct"], values["ey_dial_1p7_pct"], values["ey_dial_2p0_pct"]]

    series = [
        {"label": "Observed extraction yield by grinder dial (replicate points)",
         "categories": DIAL_LABELS, "values": ey_means, "unit": "% EY",
         "replicates": reps, "cell_stds": cell_stds, "ns": ns,
         "role": "observed", "badge": "OBSERVED", "strength": "independent",
         "component": "schmieder2023 replicate cup masses -> TDS-derived EY",
         "method": "individual measured replicate yields per dial cell; the overlays are each cell's "
                   "mean and each cell's OWN within-cell standard deviation (uncorrected, ddof=0 — a "
                   "descriptive reference, not a Bessel-corrected estimator), with n per cell (3/6/3)",
         "scope": "one machine, one coffee, one campaign, one fixed nominal central condition; "
                  "grinder-DIAL positions, non-portable without a calibrated adapter",
         "caveat": "grinder-DIAL positions, non-portable to another grinder without a calibrated "
                   "adapter; the cell means are ordered with the middle below the coarse cell, so there "
                   "is no observed interior maximum here (the 1.4-vs-1.7 interval includes zero, so the "
                   "means are ORDERED, not statistically monotone)"},
        {"label": "Central-condition cup-mass value: rounded published coefficients vs project refit "
                  "vs observed mean",
         "categories": ["rounded published coefficients", "project refit", "observed central mean"],
         "values": [values["rsm_printed_central_g"], values["rsm_refit_central_g"],
                    values["rsm_raw_central_g"]], "unit": "g",
         "role": "derived", "badge": "RECONSTRUCTED", "strength": "verification",
         "component": "schmieder RSM Eq.4 evaluated/refit at the central condition",
         "method": "central-condition cup-mass prediction three ways: a literal evaluation of the "
                   "rounded published coefficients (~6.723 g), the project's least-squares refit to the "
                   "committed cup masses (~3.918 g), and the observed central-condition mean (~3.876 g)",
         "scope": "a computational audit against the committed data — verification, not independent "
                  "experimental validation",
         "caveat": "limited printed coefficient precision prevents reconstructing the absolute level "
                   "from the printed values; the refit is near the observed mean. The 6.723 g figure is "
                   "a literal evaluation of rounded coefficients, not itself a coefficient"},
        {"label": "Model interior prominence vs descriptive replicate spread",
         "categories": ["model interior prominence (5 bar)", "model interior prominence (9 bar)",
                        "mean within-cell SD (descriptive, ddof=0)"],
         "values": [values["model_prominence_5bar_EYpt"], values["model_prominence_9bar_EYpt"],
                    values["mean_within_cell_std_EYpt"]], "unit": "EY-points",
         "role": "simulated", "badge": "EXPLORATORY_SIMULATION", "strength": "qualitative",
         "component": "channeling interior-max sensitivity vs the descriptive replicate spread",
         "method": "model interior prominence at two pressures compared with the mean within-cell "
                   "sample SD across the three dial cells",
         "scope": "model-capacity context on the tested closure grid; not a mechanism-identification "
                  "claim",
         "caveat": "the model CAN draw an interior feature (capacity); the tested feature is smaller "
                   "than the descriptive replicate spread, so the data do not identify it, and this is "
                   "not identification of channeling as the cause. The 0.218 EY-point spread is a "
                   "descriptive reference, not a formal minimum-detectable-effect or noise floor"},
    ]

    payload = {
        "schema_version": SCHEMA_VERSION,
        "story_id": STORY_ID,
        "title": TITLE,
        "generator": GENERATOR,
        "producer": PRODUCER,
        "source_commit": source_commit if source_commit is not None else _source_commit(),
        "source_data_sha256": {name: _sha256_file(p) for name, p in _SOURCE_DATA_FILES.items()},
        "dataset_manifest_ids": DATASET_MANIFEST_IDS,
        "source_ids": SOURCE_IDS,
        "attribution": ATTRIBUTION,
        "redistribution_class": "CC-BY DERIVED replicate-level extraction-yield values and RSM "
                                "predictions, attributed; no raw Schmieder source CSV is redistributed",
        "badge": BADGE,
        "evidence_strength": EVIDENCE_STRENGTH,
        "compares_grinder_dials": True,
        "values": values,
        "units": _UNITS,
        "series": series,
        "evidence_partitions": EVIDENCE_PARTITIONS,
        "revision_record": REVISION_RECORD,
        "scope": "Schmieder E65S grinder DoE at one fixed central flow/temperature condition; "
                 "TDS-derived EY observable; grinder-dial positions (not particle sizes).",
        "caveat": "A dial number is NOT a particle size and is non-portable without a calibrated "
                  "adapter; do not read a universal 'too-fine optimum'. Self-correction here downgrades "
                  "ONE result — it does not prove every current result is correct. Static channeling "
                  "remains a viable GENERATOR (model capacity); the data just do not identify it. The "
                  "1.4-vs-1.7 interval includes zero, so means are 'ordered', not 'statistically "
                  "monotone'. No confidence claim beyond the reported Welch interval.",
        "fidelity_ceiling": "Per-partition, NOT one global class: the corrected replicate correction is "
                            "OBSERVED / independent; the rounded-coefficient/refit audit is "
                            "RECONSTRUCTED / verification (a computational audit, not independent "
                            "experimental validation); the model interior feature is "
                            "EXPLORATORY_SIMULATION / qualitative and is model capacity, never mechanism "
                            "identification; the superseded interior-maximum headline carries no current "
                            "evidence badge.",
    }
    return payload


def _canonical_json(payload: dict) -> str:
    return json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False) + "\n"


def _static_summary_text(p: dict) -> str:
    v = p["values"]
    obs = next(s for s in p["series"] if s["role"] == "observed")
    lines = [
        "PV-04 — How We Falsified Our Own Espresso Headline (static text equivalent)",
        f"Generated by {p['generator']} from {p['producer']}, source commit {p['source_commit']}.",
        f"Global badge: {p['badge']}. Evidence strength: {p['evidence_strength']} "
        "(this refers to the corrected observed replicate result only; see the per-panel partitions).",
        "",
        "Finding: an apparently dramatic interior 'fine-grind' extraction-yield maximum was superseded "
        "after the project rebuilt the target on a coherent TDS basis and checked the raw replicates. "
        "The raw cell means are ordered across dial with the middle below the coarse one; the model's "
        "interior feature is smaller than the shot-to-shot spread. Model capacity is not parameter "
        "identification.",
        "",
        "Key numbers (each produced by result1_magnitude_comparison):",
        f"- observed extraction-yield CELL MEANS by dial: {v['ey_dial_1p4_pct']} -> "
        f"{v['ey_dial_1p7_pct']} -> {v['ey_dial_2p0_pct']} % EY (middle BELOW coarse)",
        "- observed replicate points per dial cell (n = "
        f"{obs['ns'][0]} / {obs['ns'][1]} / {obs['ns'][2]}):",
        f"    dial 1.4 (finer):   {obs['replicates'][0]} % EY (cell SD {obs['cell_stds'][0]})",
        f"    dial 1.7 (middle):  {obs['replicates'][1]} % EY (cell SD {obs['cell_stds'][1]})",
        f"    dial 2.0 (coarser): {obs['replicates'][2]} % EY (cell SD {obs['cell_stds'][2]})",
        f"- middle-minus-coarse (dial 1.7 - dial 2.0) contrast: {v['mid_vs_coarse_contrast_EYpt']} "
        f"EY-points, Welch 95% CI [{v['welch_ci95_lo_EYpt']}, {v['welch_ci95_hi_EYpt']}] "
        "(excludes zero)",
        f"- mean within-cell sample SD across the three dial cells (uncorrected, ddof=0): "
        f"{v['mean_within_cell_std_EYpt']} EY-points — a DESCRIPTIVE reference only, not each cell's "
        "error bar, not a noise floor, not a minimum-detectable-effect",
        f"- model interior prominence: {v['model_prominence_5bar_EYpt']} (5 bar) / "
        f"{v['model_prominence_9bar_EYpt']} (9 bar) EY-points; smaller than the descriptive spread: "
        f"{v['model_bump_lt_within_cell_var']}",
        f"- central-condition cup-mass value: a literal evaluation of the rounded published "
        f"coefficients gives {v['rsm_printed_central_g']} g, the project refit gives "
        f"{v['rsm_refit_central_g']} g, and the observed central mean is {v['rsm_raw_central_g']} g; "
        "limited printed precision prevents reconstructing the absolute level "
        f"(rounding-limited: {v['rsm_printed_is_rounding_artifact']})",
        "",
        "Evidence partitions (the panels do NOT share one global class):",
    ]
    for ep in p["evidence_partitions"]:
        badge = ep.get("badge") or "(no current badge)"
        strength = ep.get("strength") or ep.get("status", "")
        lines.append(f"  - {ep['partition']}: {ep['role']} / {badge} / {strength} — {ep['scope']}")
    lines += [
        "",
        "What this does NOT claim: that self-correction proves every current result is right; that a "
        "universal 'too-fine optimum' exists; that channeling is disproved or was identified as the "
        "cause (only that the data do not identify it); that the fine-grind reversal is 'fake'; any "
        "confidence claim beyond the reported Welch interval; that a grinder dial is a portable "
        "particle-size scale.",
        "",
        f"Scope: {p['scope']}",
        f"Caveat: {p['caveat']}",
        f"Fidelity ceiling: {p['fidelity_ceiling']}",
        "",
        "The documented revision record:",
    ]
    lines += [f"  - {q}" for q in p["revision_record"]]
    lines += ["", "Reproduce: python -m puckworks.public.analysis_autopsy verify", ""]
    return "\n".join(lines)


# ── deterministic PNG static equivalent (pure stdlib; no wall clock, no fonts, byte-reproducible) ──
_FONT3x5 = {
    "0": ["111", "101", "101", "101", "111"], "1": ["010", "110", "010", "010", "111"],
    "2": ["111", "001", "111", "100", "111"], "3": ["111", "001", "111", "001", "111"],
    "4": ["101", "101", "111", "001", "001"], "5": ["111", "100", "111", "001", "111"],
    "6": ["111", "100", "111", "101", "111"], "7": ["111", "001", "010", "010", "010"],
    "8": ["111", "101", "111", "101", "111"], "9": ["111", "101", "111", "001", "111"],
    ".": ["000", "000", "000", "000", "010"], "-": ["000", "000", "111", "000", "000"],
    "%": ["101", "001", "010", "100", "101"], " ": ["000", "000", "000", "000", "000"],
}


class _Canvas:
    def __init__(self, w, h, bg=(255, 255, 255)):
        self.w, self.h = w, h
        self.buf = bytearray(bg * (w * h))

    def px(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.buf[i:i + 3] = bytes(c)

    def rect(self, x, y, w, h, c):
        for yy in range(int(y), int(y + h)):
            for xx in range(int(x), int(x + w)):
                self.px(xx, yy, c)

    def hline(self, x0, x1, y, c, t=1):
        for dy in range(t):
            for x in range(int(x0), int(x1)):
                self.px(x, int(y) + dy, c)

    def vline(self, x, y0, y1, c, t=1):
        for dx in range(t):
            for y in range(int(y0), int(y1)):
                self.px(int(x) + dx, y, c)

    def text(self, x, y, s, c, scale=2):
        cx = int(x)
        for ch in s:
            glyph = _FONT3x5.get(ch, _FONT3x5[" "])
            for r in range(5):
                for col in range(3):
                    if glyph[r][col] == "1":
                        self.rect(cx + col * scale, int(y) + r * scale, scale, scale, c)
            cx += 4 * scale

    def png(self):
        def chunk(typ, data):
            return (struct.pack(">I", len(data)) + typ + data
                    + struct.pack(">I", zlib.crc32(typ + data) & 0xffffffff))
        raw = bytearray()
        stride = self.w * 3
        for y in range(self.h):
            raw.append(0)
            raw.extend(self.buf[y * stride:(y + 1) * stride])
        ihdr = struct.pack(">IIBBBBB", self.w, self.h, 8, 2, 0, 0, 0)
        return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
                + chunk(b"IDAT", zlib.compress(bytes(raw), 9)) + chunk(b"IEND", b""))


def _static_summary_png(p: dict) -> bytes:
    """Deterministic Scene-3 chart (observed replicate dots + cell means) built from the payload.

    Byte-reproducible: no timestamps, no system fonts (an embedded 3x5 bitmap font), fixed geometry,
    fixed zlib level. Regenerating from the committed snapshot yields identical bytes."""
    obs = next(s for s in p["series"] if s["role"] == "observed")
    ink, muted, line_c, teal, mean_c = (20, 24, 28), (90, 100, 110), (207, 212, 206), \
        (14, 116, 144), (176, 106, 44)
    W, H = 720, 420
    ML, MR, MT, MB = 70, 24, 60, 60
    cv = _Canvas(W, H)
    # y-axis range covering all replicate points, padded to whole %EY
    allv = [x for cell in obs["replicates"] for x in cell]
    ylo, yhi = math.floor(min(allv)), math.ceil(max(allv))
    if yhi - ylo < 2:
        yhi = ylo + 2

    def sy(v):
        return MT + (yhi - v) / (yhi - ylo) * (H - MT - MB)
    # axes
    cv.vline(ML, MT, H - MB, muted, 2)
    cv.hline(ML, W - MR, H - MB, muted, 2)
    # y gridlines + labels (integer %EY)
    for yv in range(ylo, yhi + 1):
        py = sy(yv)
        cv.hline(ML, W - MR, py, line_c, 1)
        cv.text(8, py - 5, f"{yv}", muted, 2)
    cv.text(8, MT - 22, "EY %", muted, 2)
    # three dial columns
    ncell = len(obs["replicates"])
    colw = (W - MR - ML) / ncell
    dials = ["1.4", "1.7", "2.0"]
    for i, cell in enumerate(obs["replicates"]):
        cx = ML + colw * (i + 0.5)
        # replicate dots with deterministic horizontal offsets
        m = len(cell)
        for j, val in enumerate(cell):
            ox = (j - (m - 1) / 2.0) * 14
            px, py = int(cx + ox), int(sy(val))
            cv.rect(px - 3, py - 3, 6, 6, teal)
        # cell mean line (thicker, amber)
        mean_y = sy(obs["values"][i])
        cv.hline(cx - colw * 0.32, cx + colw * 0.32, mean_y, mean_c, 3)
        # dial label on the x-axis
        cv.text(cx - 12, H - MB + 12, dials[i], muted, 2)
    cv.text(W // 2 - 40, H - 26, "dial", muted, 2)
    # contrast readout (middle-minus-coarse) as text, from the payload
    c = p["values"]["mid_vs_coarse_contrast_EYpt"]
    cv.text(ML, MT - 44, f"1.7-2.0 {c}", ink, 2)
    return cv.png()


def export(out_dir: Path | str = SITE_DIR) -> dict:
    payload = build_payload()
    text = _canonical_json(payload)
    SNAPSHOT.parent.mkdir(parents=True, exist_ok=True)
    SNAPSHOT.write_text(text, encoding="utf-8")
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    (out / "data.json").write_text(text, encoding="utf-8")
    (out / "static-summary.txt").write_text(_static_summary_text(payload), encoding="utf-8")
    (out / "static-summary.png").write_bytes(_static_summary_png(payload))
    return payload


def verify(out_dir: Path | str = SITE_DIR) -> list:
    problems: list[str] = []
    if not SNAPSHOT.exists():
        return [f"missing snapshot {SNAPSHOT}; run `python -m puckworks.public.analysis_autopsy export`"]
    stored_text = SNAPSHOT.read_text(encoding="utf-8")
    stored = json.loads(stored_text)

    fresh = build_payload(source_commit=stored.get("source_commit"))
    if _canonical_json(fresh) != stored_text:
        problems.append("packaged snapshot is stale vs a fresh run of the producer (run export)")

    for name, p in _SOURCE_DATA_FILES.items():
        live = _sha256_file(p)
        if stored.get("source_data_sha256", {}).get(name) != live:
            problems.append(f"source-data SHA-256 drift on {name}")

    for f in ("schema_version", "story_id", "title", "generator", "producer", "source_commit",
              "source_data_sha256", "dataset_manifest_ids", "attribution", "redistribution_class",
              "badge", "evidence_strength", "values", "units", "series", "evidence_partitions",
              "revision_record", "scope", "caveat", "fidelity_ceiling"):
        if f not in stored:
            problems.append(f"snapshot missing required field: {f}")

    if stored.get("schema_version") != SCHEMA_VERSION:
        problems.append(f"schema_version is {stored.get('schema_version')}, expected {SCHEMA_VERSION}")

    for k, val in stored.get("values", {}).items():
        if k not in stored.get("units", {}) or not str(stored["units"][k]).strip():
            problems.append(f"value '{k}' has no unit")
        if not _all_finite(val):
            problems.append(f"value '{k}' is non-finite")

    roles = {"observed", "benchmark", "simulated", "derived"}
    for s in stored.get("series", []):
        for key in ("label", "categories", "values", "unit", "role", "component", "method", "caveat",
                    "badge", "strength", "scope"):
            if key not in s or (isinstance(s.get(key), str) and not s[key].strip()):
                problems.append(f"series '{s.get('label', '?')}' missing '{key}'")
        if s.get("role") not in roles:
            problems.append(f"series '{s.get('label', '?')}' has invalid role {s.get('role')!r}")
        if not _all_finite(s.get("values")):
            problems.append(f"series '{s.get('label', '?')}' has a non-finite value")
        if len(s.get("values", [])) != len(s.get("categories", [1])):
            problems.append(f"series '{s.get('label', '?')}' values/categories length mismatch")

    # the corrected observed series must carry actual replicate arrays, cell SDs and n
    obs = [s for s in stored.get("series", []) if s.get("role") == "observed"]
    if not obs:
        problems.append("no observed series in the snapshot")
    else:
        o = obs[0]
        if not (isinstance(o.get("replicates"), list) and len(o["replicates"]) == 3
                and all(isinstance(c, list) and c for c in o["replicates"])):
            problems.append("observed series has no per-dial replicate arrays")
        if not (isinstance(o.get("cell_stds"), list) and len(o.get("cell_stds", [])) == 3):
            problems.append("observed series has no per-cell sample SDs")
        if not (isinstance(o.get("ns"), list) and len(o.get("ns", [])) == 3):
            problems.append("observed series has no per-cell n")

    # the four evidence partitions are present and named honestly
    parts = {ep.get("partition") for ep in stored.get("evidence_partitions", [])}
    for need in ("corrected_replicate_data", "rounded_coefficient_and_refit_audit",
                 "model_interior_feature", "superseded_headline"):
        if need not in parts:
            problems.append(f"evidence partition missing: {need}")

    # the load-bearing corrected-analysis facts (guard a silent producer regression)
    v = stored.get("values", {})
    if not (v.get("ey_dial_1p7_pct", 9) < v.get("ey_dial_2p0_pct", 0)):
        problems.append("raw EY is no longer ordered with the middle dial below the coarse one")
    if not (v.get("welch_ci95_hi_EYpt", 9) < 0):
        problems.append("the middle-minus-coarse Welch 95% interval no longer excludes zero")
    if not v.get("model_bump_lt_within_cell_var"):
        problems.append("the model interior feature is no longer below the descriptive replicate spread")
    if not v.get("rsm_printed_is_rounding_artifact"):
        problems.append("the printed RSM central value is no longer flagged rounding-limited")

    site_data = Path(out_dir) / "data.json"
    if site_data.exists() and site_data.read_text(encoding="utf-8") != stored_text:
        problems.append("site data.json differs from the packaged snapshot")
    site_summary = Path(out_dir) / "static-summary.txt"
    if not site_summary.exists():
        problems.append("missing static-summary.txt (run export)")
    elif site_summary.read_text(encoding="utf-8") != _static_summary_text(stored):
        problems.append("static-summary.txt is stale vs the snapshot (run export)")
    site_png = Path(out_dir) / "static-summary.png"
    if not site_png.exists():
        problems.append("missing static-summary.png (run export)")
    elif site_png.read_bytes() != _static_summary_png(stored):
        problems.append("static-summary.png is stale vs the snapshot (run export)")

    problems += _site_number_audit(Path(out_dir), stored)
    return problems


def _num_key(x: float) -> str:
    return f"{float(x):.6g}"


def _site_number_audit(site_dir: Path, snapshot: dict) -> list:
    import re
    allowed: set[str] = set()

    def _collect(x):
        if isinstance(x, bool):
            return
        if isinstance(x, (int, float)):
            allowed.add(_num_key(x))
        elif isinstance(x, list):
            for v in x:
                _collect(v)
        elif isinstance(x, dict):
            for v in x.values():
                _collect(v)

    _collect(snapshot.get("values", {}))
    for s in snapshot.get("series", []):
        _collect(s.get("values", []))
        _collect(s.get("replicates", []))
        _collect(s.get("cell_stds", []))
        _collect(s.get("ns", []))
    STRUCTURAL = {str(i) for i in range(0, 13)} | {"100", "1000", "16", "18", "20", "24", "40",
                                                   "50", "60", "64", "255", "1.4", "1.7", "2.0",
                                                   "0.5", "1.5", "2.5"}
    problems = []
    for name in ("app.js", "index.html"):
        f = site_dir / name
        if not f.exists():
            continue
        text = re.sub(r"//[^\n]*", "", f.read_text(encoding="utf-8"))
        for m in re.findall(r"(?<![\w.])-?\d+\.\d+", text):
            if _num_key(float(m)) not in allowed and m not in STRUCTURAL:
                problems.append(f"{name}: numeric literal {m} not present in the generated data")
    return problems


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="puckworks.public.analysis_autopsy")
    ap.add_argument("cmd", choices=["export", "verify"])
    ap.add_argument("--out", default=str(SITE_DIR))
    a = ap.parse_args(argv)
    if a.cmd == "export":
        payload = export(a.out)
        digest = next(iter(payload["source_data_sha256"].values()))[:12]
        print(f"wrote {SNAPSHOT} and {Path(a.out) / 'data.json'} (source sha256 {digest}…)")
        return 0
    problems = verify(a.out)
    if problems:
        print("PV-04 verify FAILED:")
        for p in problems:
            print("  -", p)
        return 1
    print("PV-04 analysis-autopsy snapshot OK (producer-bound, finite, unit-carrying, site-consistent)")
    return 0


def pv04_values() -> dict:
    """Return the headline PV-04 values from the packaged snapshot (the PV-04 claim producer)."""
    snap = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
    return snap["values"]


if __name__ == "__main__":
    raise SystemExit(main())
