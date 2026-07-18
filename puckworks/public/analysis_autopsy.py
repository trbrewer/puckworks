"""PV-04 "How We Falsified Our Own Espresso Headline" — the analysis-autopsy public data contract.

A deterministic transform of ONE named producer (`puckworks.harness.result1_magnitude_comparison`)
into a compact public snapshot (`puckworks/public/data/pv04_analysis_autopsy.json`) that the static
interactive and the PV-04 ``PublicClaim`` producer consume. **No headline number is hand-typed** — the
producer is authoritative, and the snapshot records the SHA-256 of the canonical CC-BY Schmieder source
files so ``verify`` fails the moment the underlying data drifts.

The story is a transparent analysis revision (not a humiliation narrative):

    1. an initially attractive interior "fine-grind" bump (a printed RSM central coefficient);
    2. the unit/precision problem that invalidated it (a mixed-unit target; the printed coefficient is
       a rounding artifact of a much smaller refit);
    3. the corrected raw-replicate result — extraction yields ORDERED across dial, the middle BELOW the
       coarse one, with a Welch 95% interval on the contrast that excludes zero: no interior maximum;
    4. the model still has the CAPACITY to draw such a bump, but it is smaller than replicate spread —
       model capacity is not parameter identification.

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
import subprocess
from pathlib import Path

SCHEMA_VERSION = 1
STORY_ID = "PV-04"
TITLE = "How We Falsified Our Own Espresso Headline"
_PKG_DIR = Path(__file__).resolve().parent
_REPO = _PKG_DIR.parents[1]
SNAPSHOT = _PKG_DIR / "data" / "pv04_analysis_autopsy.json"
SITE_DIR = _REPO / "docs" / "public" / "site" / "analysis-autopsy"
GENERATOR = "puckworks.public.analysis_autopsy.build_payload"
PRODUCER = "puckworks.harness.result1_magnitude_comparison"
BADGE = "OBSERVED"                        # a corrected observation of measured replicates
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
               "DOI 10.3390/foods12152871, open access CC-BY. Derived extraction-yield and RSM values "
               "are published with attribution; no raw source file is redistributed.")
SOURCE_IDS = {"schmieder_doe": "Foods 12, 2871 (DOI 10.3390/foods12152871, CC-BY)"}

# public value key -> dotted path into result1_magnitude_comparison()'s return (the no-hand-typed rule)
_VALUE_PATHS = {
    "ey_dial_1p4_pct": "raw_tds_ey.0",
    "ey_dial_1p7_pct": "raw_tds_ey.1",
    "ey_dial_2p0_pct": "raw_tds_ey.2",
    "mid_vs_coarse_contrast_EYpt": "raw_mid_vs_endpoint_contrast_EYpt",
    "welch_ci95_lo_EYpt": "raw_contrast_welch_ci95.0",
    "welch_ci95_hi_EYpt": "raw_contrast_welch_ci95.1",
    "within_cell_std_EYpt": "raw_within_cell_std_EYpt",
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
    "welch_ci95_hi_EYpt": "EY-points", "within_cell_std_EYpt": "EY-points",
    "model_prominence_5bar_EYpt": "EY-points", "model_prominence_9bar_EYpt": "EY-points",
    "model_bump_lt_within_cell_var": "boolean",
    "rsm_refit_central_g": "g", "rsm_printed_central_g": "g", "rsm_raw_central_g": "g",
    "rsm_printed_is_rounding_artifact": "boolean",
}

REVISION_RECORD = [
    "Superseded headline: an interior 'fine-grind' extraction-yield maximum, read from a printed RSM "
    "central coefficient and a target that mixed mg solute masses with g TDS.",
    "Correction 1 — coherent target: rebuild extraction yield from TDS on one consistent basis.",
    "Correction 2 — precision: the printed central coefficient is a rounding artifact of a much smaller "
    "refit (refit vs printed vs raw central mass), not a real 1.7x over-prediction.",
    "Corrected result: raw replicate yields are ORDERED across dial, the middle BELOW the coarse one; "
    "the Welch 95% interval on the middle-vs-coarse contrast excludes zero — no interior maximum.",
    "Standing lesson: a channeling model can still GENERATE a small interior bump (model capacity), but "
    "it is smaller than the shot-to-shot replicate spread — capacity is not identification.",
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

    ey = [values["ey_dial_1p4_pct"], values["ey_dial_1p7_pct"], values["ey_dial_2p0_pct"]]
    series = [
        {"label": "Raw extraction yield by grinder dial", "categories": DIAL_LABELS,
         "values": ey, "error": [values["within_cell_std_EYpt"]] * 3, "unit": "% EY",
         "role": "observed", "component": "schmieder2023 replicate cup masses -> TDS-derived EY",
         "method": "raw per-cell measured yields (error bar = within-cell replicate std)",
         "caveat": "grinder-DIAL positions, non-portable to another grinder without a calibrated "
                   "adapter; ordered (middle below coarse), no interior maximum"},
        {"label": "RSM central coefficient: printed vs refit vs raw", "categories":
            ["printed (rounded)", "refit to data", "raw data mean"],
         "values": [values["rsm_printed_central_g"], values["rsm_refit_central_g"],
                    values["rsm_raw_central_g"]], "unit": "g",
         "role": "derived", "component": "schmieder RSM Eq.4 refit vs the printed coefficient",
         "method": "least-squares refit of the published RSM to the committed cup masses",
         "caveat": "the printed central coefficient is a rounding/precision artifact, not a real "
                   "over-prediction"},
        {"label": "Model interior bump vs replicate spread", "categories":
            ["model bump (5 bar)", "model bump (9 bar)", "replicate spread"],
         "values": [values["model_prominence_5bar_EYpt"], values["model_prominence_9bar_EYpt"],
                    values["within_cell_std_EYpt"]], "unit": "EY-points",
         "role": "simulated", "component": "channeling interior-max sensitivity vs measured spread",
         "method": "model interior prominence at two pressures compared with the within-cell std",
         "caveat": "the model CAN draw a bump (capacity); it is smaller than replicate spread, so the "
                   "data do not identify it"},
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
        "redistribution_class": "CC-BY derived extraction-yield and RSM values, attributed; no raw "
                                "source file redistributed",
        "badge": BADGE,
        "evidence_strength": EVIDENCE_STRENGTH,
        "compares_grinder_dials": True,
        "values": values,
        "units": _UNITS,
        "series": series,
        "revision_record": REVISION_RECORD,
        "scope": "Schmieder E65S grinder DoE at one fixed central flow/temperature condition; "
                 "TDS-derived EY observable; grinder-dial positions (not particle sizes).",
        "caveat": "A dial number is NOT a particle size and is non-portable without a calibrated "
                  "adapter; do not read a universal 'too-fine optimum'. Self-correction here downgrades "
                  "ONE result — it does not prove every current result is correct. Static channeling "
                  "remains a viable GENERATOR (model capacity); the data just do not identify it. The "
                  "1.4-vs-1.7 interval includes zero, so means are 'ordered', not 'statistically "
                  "monotone'. No confidence claim beyond the reported Welch interval.",
        "fidelity_ceiling": "OBSERVED / independent for the raw replicate correction; the model-bump "
                            "comparison is exploratory model-capacity context, never an identification "
                            "claim.",
    }
    return payload


def _canonical_json(payload: dict) -> str:
    return json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False) + "\n"


def _static_summary_text(p: dict) -> str:
    v = p["values"]
    lines = [
        "PV-04 — How We Falsified Our Own Espresso Headline (static text equivalent)",
        f"Generated by {p['generator']} from {p['producer']}, source commit {p['source_commit']}.",
        f"Badge: {p['badge']}. Evidence strength: {p['evidence_strength']}.",
        "",
        "Finding: an apparently dramatic interior 'fine-grind' extraction-yield maximum weakened after "
        "we rebuilt the target on a coherent TDS basis and checked the raw replicates. The raw yields "
        "are ordered across dial with the middle below the coarse one; the model's interior bump is "
        "smaller than the shot-to-shot spread. Model capacity is not parameter identification.",
        "",
        "Key numbers (each produced by result1_magnitude_comparison):",
        f"- raw extraction yield by dial: {v['ey_dial_1p4_pct']} -> {v['ey_dial_1p7_pct']} -> "
        f"{v['ey_dial_2p0_pct']} % EY (middle BELOW coarse)",
        f"- middle-vs-coarse contrast: {v['mid_vs_coarse_contrast_EYpt']} EY-points, Welch 95% CI "
        f"[{v['welch_ci95_lo_EYpt']}, {v['welch_ci95_hi_EYpt']}] (excludes zero)",
        f"- within-cell replicate spread: {v['within_cell_std_EYpt']} EY-points",
        f"- model interior bump: {v['model_prominence_5bar_EYpt']} (5 bar) / "
        f"{v['model_prominence_9bar_EYpt']} (9 bar) EY-points; smaller than replicate spread: "
        f"{v['model_bump_lt_within_cell_var']}",
        f"- RSM central coefficient: printed {v['rsm_printed_central_g']} g is a rounding artifact of "
        f"the refit {v['rsm_refit_central_g']} g (raw {v['rsm_raw_central_g']} g): "
        f"{v['rsm_printed_is_rounding_artifact']}",
        "",
        "What this does NOT claim: that self-correction proves every current result is right; that a "
        "universal 'too-fine optimum' exists; that channeling is ruled out (only that the data do not "
        "identify it); any confidence claim beyond the reported Welch interval.",
        "",
        f"Scope: {p['scope']}",
        f"Caveat: {p['caveat']}",
        "",
        "The documented revision record:",
    ]
    lines += [f"  - {q}" for q in p["revision_record"]]
    lines += ["", "Reproduce: python -m puckworks.public.analysis_autopsy verify", ""]
    return "\n".join(lines)


def export(out_dir: Path | str = SITE_DIR) -> dict:
    payload = build_payload()
    text = _canonical_json(payload)
    SNAPSHOT.parent.mkdir(parents=True, exist_ok=True)
    SNAPSHOT.write_text(text, encoding="utf-8")
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    (out / "data.json").write_text(text, encoding="utf-8")
    (out / "static-summary.txt").write_text(_static_summary_text(payload), encoding="utf-8")
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
              "badge", "evidence_strength", "values", "units", "series", "revision_record", "scope",
              "caveat", "fidelity_ceiling"):
        if f not in stored:
            problems.append(f"snapshot missing required field: {f}")

    for k, val in stored.get("values", {}).items():
        if k not in stored.get("units", {}) or not str(stored["units"][k]).strip():
            problems.append(f"value '{k}' has no unit")
        if not _all_finite(val):
            problems.append(f"value '{k}' is non-finite")

    roles = {"observed", "benchmark", "simulated", "derived"}
    for s in stored.get("series", []):
        for key in ("label", "categories", "values", "unit", "role", "component", "method", "caveat"):
            if key not in s or (isinstance(s.get(key), str) and not s[key].strip()):
                problems.append(f"series '{s.get('label', '?')}' missing '{key}'")
        if s.get("role") not in roles:
            problems.append(f"series '{s.get('label', '?')}' has invalid role {s.get('role')!r}")
        if not _all_finite(s.get("values")):
            problems.append(f"series '{s.get('label', '?')}' has a non-finite value")
        if len(s.get("values", [])) != len(s.get("categories", [1])):
            problems.append(f"series '{s.get('label', '?')}' values/categories length mismatch")

    # the load-bearing corrected-analysis facts (guard a silent producer regression)
    v = stored.get("values", {})
    if not (v.get("ey_dial_1p7_pct", 9) < v.get("ey_dial_2p0_pct", 0)):
        problems.append("raw EY is no longer ordered with the middle dial below the coarse one")
    if not (v.get("welch_ci95_hi_EYpt", 9) < 0):
        problems.append("the middle-vs-coarse Welch 95% interval no longer excludes zero")
    if not v.get("model_bump_lt_within_cell_var"):
        problems.append("the model interior bump is no longer below replicate spread")
    if not v.get("rsm_printed_is_rounding_artifact"):
        problems.append("the printed RSM coefficient is no longer flagged a rounding artifact")

    site_data = Path(out_dir) / "data.json"
    if site_data.exists() and site_data.read_text(encoding="utf-8") != stored_text:
        problems.append("site data.json differs from the packaged snapshot")
    site_summary = Path(out_dir) / "static-summary.txt"
    if not site_summary.exists():
        problems.append("missing static-summary.txt (run export)")
    elif site_summary.read_text(encoding="utf-8") != _static_summary_text(stored):
        problems.append("static-summary.txt is stale vs the snapshot (run export)")

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
        _collect(s.get("error", []))
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
