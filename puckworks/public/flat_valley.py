"""PV-03 "The Cup Hides the Clock" — the flat-valley public data contract (issue #54).

A deterministic, hash-bound transform of the committed Paper A result bundle
(``docs/figures/paper_a/results.json``) into a compact public snapshot
(``puckworks/public/data/pv03_flat_valley.json``) that the static interactive and the PV-03
``PublicClaim`` producer consume. **No headline number is hand-typed** — every value is copied from a
named bundle field, and the snapshot records the SHA-256 of the source bundle so ``verify`` fails the
moment the science drifts.

CLI::

    python -m puckworks.public.flat_valley export   # regenerate the snapshot + the site data.json
    python -m puckworks.public.flat_valley verify    # fail on drift / missing fields / non-finite

Runtime: :func:`pv03_values` reads the packaged snapshot (works from an installed wheel) and returns
the headline values; the PV-03 producer maps its numeric keys onto that return.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

SCHEMA_VERSION = 1
STORY_ID = "PV-03"
_PKG_DIR = Path(__file__).resolve().parent
_REPO = _PKG_DIR.parents[1]
SOURCE_BUNDLE = _REPO / "docs" / "figures" / "paper_a" / "results.json"
SNAPSHOT = _PKG_DIR / "data" / "pv03_flat_valley.json"
SITE_DIR = _REPO / "docs" / "public" / "site" / "flat-valley"
GENERATOR = "puckworks.public.flat_valley.build_payload"
BADGE = "RECONSTRUCTED"                 # a post-fit refit to measured data; not a raw observation
EVIDENCE_STRENGTH = "negative validation"   # the mechanistic model barely beats a level-only null

# Headline numeric fields: public key -> dotted path in the Paper A bundle. This table IS the
# no-hand-typed-numbers contract; the exporter digs each path, verify re-digs and compares.
_VALUE_PATHS = {
    "condition_number": "panel_caffeine.condition_number",
    "inverse_curvature_coupling": "panel_caffeine.local_curvature_coupling",
    "rate_star": "panel_caffeine.rate_star",
    "c_s0_star": "panel_caffeine.c_s0_star",
    "profile_fraction_of_log_grid": "panel_caffeine.profile_fraction_of_log_grid",
    "profile_upper_censored": "panel_caffeine.profile_upper_censored",
    "profile_log_width": "panel_caffeine.profile_log_width",
    "mape_profile_fraction_within10pct": "panel_caffeine.mape_profile_fraction_within10pct",
    "sse_mape_threshold_jaccard": "panel_caffeine.sse_mape_threshold_jaccard",
    "held_out_model_mape": "transfer_skill.pooled_model_mape",
    "held_out_const_mape": "transfer_skill.pooled_const_mape",
    "n_model_worse_than_const": "transfer_skill.n_model_worse_than_const",
    "n_points": "transfer_skill.n_points",
    "skill_vs_const": "transfer_skill.skill_vs_const",
    "table7_implied_rate": "table7_rate_constraint.caffeine.implied_rate",
    "table7_inventory_g_L": "table7_rate_constraint.caffeine.inventory_g_L",
    "trigonelline_condition_number": "panel_trigonelline.condition_number",
    "trigonelline_coupling": "panel_trigonelline.local_curvature_coupling",
}

_UNITS = {
    "condition_number": "ratio", "inverse_curvature_coupling": "ratio (geometric, not statistical)",
    "rate_star": "rate scale (dimensionless)", "c_s0_star": "g/L",
    "profile_fraction_of_log_grid": "fraction of tested log-rate grid",
    "profile_upper_censored": "boolean", "profile_log_width": "log-rate units",
    "mape_profile_fraction_within10pct": "fraction of tested log-rate grid",
    "sse_mape_threshold_jaccard": "Jaccard overlap (0-1)",
    "held_out_model_mape": "% MAPE", "held_out_const_mape": "% MAPE",
    "n_model_worse_than_const": "count", "n_points": "count", "skill_vs_const": "fraction",
    "table7_implied_rate": "rate scale (dimensionless)", "table7_inventory_g_L": "g/L",
    "trigonelline_condition_number": "ratio", "trigonelline_coupling": "ratio (geometric)",
}

# Axis/curve arrays for the interactive (kept compact). key -> dotted bundle path.
_AXIS_PATHS = {
    "profile_rates": "panel_caffeine.profile.rates",
    "profile_c_star": "panel_caffeine.profile.c_star",
    "profile_sse": "panel_caffeine.profile.sse",
    "profile_sse_min": "panel_caffeine.profile.sse_min",
    "surface_rates": "panel_caffeine.surface.rates",
    "surface_cs0": "panel_caffeine.surface.cs0",
    "surface_sse": "panel_caffeine.surface.sse",
    "near_optimal_rate_interval": "panel_caffeine.profile_rate_within10pct",
    "pc_caffeine_rates": "positive_control.per_solute.caffeine.rates",
    "pc_caffeine_fraction_mape": "positive_control.per_solute.caffeine.fraction_mape",
    "pc_caffeine_cup_mape": "positive_control.per_solute.caffeine.sampled_agg_mape",
    "pc_caffeine_fraction_range_ratio": "positive_control.per_solute.caffeine.frac_range_ratio",
    "pc_caffeine_cup_range_ratio": "positive_control.per_solute.caffeine.sampled_agg_range_ratio",
    "table7_implied_rate_band": "table7_rate_constraint.caffeine.implied_rate_band",
}

DATASET_MANIFEST_IDS = ["angeloni2023/bioactives", "angeloni2023/total_solids",
                        "angeloni2023/inventories", "pannusch2024/table2_params"]


def _dig(obj, path):
    cur = obj
    for seg in path.split("."):
        cur = cur[int(seg)] if isinstance(cur, (list, tuple)) else cur[seg]
    return cur


def _all_finite(x) -> bool:
    if isinstance(x, bool):
        return True
    if isinstance(x, (int, float)):
        return math.isfinite(x)
    if isinstance(x, list):
        return all(_all_finite(v) for v in x)
    return True


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def build_payload(source_path: Path | str = SOURCE_BUNDLE) -> dict:
    """Deterministically transform the Paper A bundle into the compact PV-03 snapshot. No wall clock."""
    source_path = Path(source_path)
    bundle = json.loads(source_path.read_text(encoding="utf-8"))
    values = {k: _dig(bundle, p) for k, p in _VALUE_PATHS.items()}
    axes = {k: _dig(bundle, p) for k, p in _AXIS_PATHS.items()}
    return {
        "schema_version": SCHEMA_VERSION,
        "story_id": STORY_ID,
        "source_commit": bundle["source_commit"],
        "source_bundle": "docs/figures/paper_a/results.json",
        "source_bundle_sha256": _sha256_file(source_path),
        "generator": GENERATOR,
        "badge": BADGE,
        "evidence_strength": EVIDENCE_STRENGTH,
        "objective": "unweighted concentration-scale SSE with a least-squares nuisance level, on "
                     "matched-mass 40 g whole-cup endpoints (log-parameter basis u=ln rate, v=ln c_s0)",
        "near_optimal_sse_tol": 0.1,     # the documented 10% objective threshold (transform parameter)
        "threshold_definitions": {
            "near_optimal": "profiled SSE (minimised over inventory at each rate) within 10% of the "
                            "global minimum",
            "jaccard": "overlap of the SSE-near-optimal and MAPE-near-optimal rate sets"},
        "right_censoring": {"profile_upper_censored": bool(values["profile_upper_censored"]),
                            "meaning": "the near-optimal rate set runs to the upper edge of the tested "
                                       "log-rate grid; the true extent is not bounded by the data"},
        "null_benchmark": "an O-trained level-only constant: carry the fitted concentration level "
                          "across grinds with no kinetic mechanism",
        "values": values,
        "units": _UNITS,
        "axes": axes,
        "dataset_manifest_ids": DATASET_MANIFEST_IDS,
        "scope": "One model (pannusch2024) refit to one independent campaign (angeloni2023); "
                 "conditional on the tested model, observation operator, data, objective, and domain. "
                 "Practical (not structural) identifiability; no likelihood/noise model.",
        "caveat": "Endpoint prediction stability is not parameter identification and not mechanistic "
                  "validation. The inverse-curvature coupling is objective-surface geometry, NOT a "
                  "statistical parameter correlation. The 10% set is a tested-domain threshold set, "
                  "NOT a confidence interval. Fraction agreement is in-sample verification, not "
                  "independent validation. The tested rate range is right-censored.",
    }


def _canonical_json(payload: dict) -> str:
    return json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False) + "\n"


def _static_summary_text(p: dict) -> str:
    """A deterministic, generated static text equivalent (numbers are NOT hand-typed into the HTML)."""
    v = p["values"]
    return (
        "PV-03 — The Cup Hides the Clock (static text equivalent)\n"
        f"Generated from {p['source_bundle']} (SHA-256 {p['source_bundle_sha256']}), "
        f"source commit {p['source_commit']}.\n"
        f"Badge: {p['badge']}. Evidence strength: {p['evidence_strength']}.\n\n"
        "Finding: whole-cup endpoints leave the extraction model's inventory and rate practically "
        "non-identifiable, yet the endpoint still predicts reasonably — and barely beats a level-only "
        "null. Endpoint accuracy is not mechanistic validation.\n\n"
        "Key numbers (each a field of the committed Paper A result bundle):\n"
        f"- caffeine SSE-Hessian condition number: {v['condition_number']} (ratio)\n"
        f"- local inverse-curvature coupling: {v['inverse_curvature_coupling']} "
        "(geometric objective-surface diagnostic, NOT a statistical parameter correlation)\n"
        f"- near-optimal (SSE within 10% of min) rate set covers {v['profile_fraction_of_log_grid']} "
        "of the tested log-rate grid; the upper extent is RIGHT-CENSORED\n"
        f"- SSE vs MAPE near-optimal set overlap (Jaccard): {v['sse_mape_threshold_jaccard']}\n"
        f"- held-out mechanistic MAPE: {v['held_out_model_mape']}% vs level-only constant "
        f"{v['held_out_const_mape']}% (a tested-domain threshold set, NOT a confidence interval)\n"
        f"- mechanistic model worse than the constant on {v['n_model_worse_than_const']} of "
        f"{v['n_points']} held-out points (skill vs const {v['skill_vs_const']})\n"
        f"- trigonelline condition number: {v['trigonelline_condition_number']} "
        "(a tighter but still ill-conditioned valley)\n"
        f"- with an independently measured inventory (~{v['table7_inventory_g_L']} g/L) the valley "
        f"collapses to an implied rate ~{v['table7_implied_rate']}\n\n"
        "What this does NOT prove: that the mechanism transferred; structural identifiability; a "
        "statistical confidence interval; or that timed fractions uniquely identify the true "
        "mechanism (fraction agreement here is in-sample verification, not independent validation).\n\n"
        f"Scope: {p['scope']}\nCaveat: {p['caveat']}\n"
        "Reproduce: python -m puckworks.public.flat_valley verify\n"
    )


def export(source_path: Path | str = SOURCE_BUNDLE, out_dir: Path | str = SITE_DIR) -> dict:
    """Write the packaged snapshot, the site ``data.json`` (identical bytes), and the generated
    static text equivalent."""
    payload = build_payload(source_path)
    text = _canonical_json(payload)
    SNAPSHOT.parent.mkdir(parents=True, exist_ok=True)
    SNAPSHOT.write_text(text, encoding="utf-8")
    out = Path(out_dir); out.mkdir(parents=True, exist_ok=True)
    (out / "data.json").write_text(text, encoding="utf-8")
    (out / "static-summary.txt").write_text(_static_summary_text(payload), encoding="utf-8")
    return payload


def verify(source_path: Path | str = SOURCE_BUNDLE, out_dir: Path | str = SITE_DIR) -> list:
    """Return a list of problems (empty == clean). Fails on source-hash drift, snapshot drift,
    missing fields, non-finite values, missing units, or a site number absent from the data."""
    problems: list[str] = []
    fresh = build_payload(source_path)
    fresh_text = _canonical_json(fresh)

    if not SNAPSHOT.exists():
        return [f"missing snapshot {SNAPSHOT}; run `python -m puckworks.public.flat_valley export`"]
    stored_text = SNAPSHOT.read_text(encoding="utf-8")
    if stored_text != fresh_text:
        problems.append("packaged snapshot is stale vs a fresh transform of the Paper A bundle "
                        "(run export)")
    stored = json.loads(stored_text)

    # source-bundle hash binding
    live_sha = _sha256_file(Path(source_path))
    if stored.get("source_bundle_sha256") != live_sha:
        problems.append(f"source-bundle SHA-256 drift: snapshot {stored.get('source_bundle_sha256')} "
                        f"!= live {live_sha}")

    # required top-level metadata
    for f in ("schema_version", "story_id", "source_commit", "source_bundle_sha256", "generator",
              "badge", "evidence_strength", "objective", "null_benchmark", "values", "units", "axes",
              "dataset_manifest_ids", "scope", "caveat", "right_censoring", "threshold_definitions"):
        if f not in stored:
            problems.append(f"snapshot missing required field: {f}")

    # every value has a unit and is finite
    for k, v in stored.get("values", {}).items():
        if k not in stored.get("units", {}) or not str(stored["units"][k]).strip():
            problems.append(f"value '{k}' has no unit")
        if not _all_finite(v):
            problems.append(f"value '{k}' is non-finite")
    for k, v in stored.get("axes", {}).items():
        if not _all_finite(v):
            problems.append(f"axis '{k}' has a non-finite value")

    # site data.json matches the packaged snapshot
    site_data = Path(out_dir) / "data.json"
    if site_data.exists() and site_data.read_text(encoding="utf-8") != stored_text:
        problems.append("site data.json differs from the packaged snapshot")

    # generated static text equivalent is current
    site_summary = Path(out_dir) / "static-summary.txt"
    if not site_summary.exists():
        problems.append("missing static-summary.txt (run export)")
    elif site_summary.read_text(encoding="utf-8") != _static_summary_text(stored):
        problems.append("static-summary.txt is stale vs the snapshot (run export)")

    # no numeric literal in the site HTML/JS that is absent from the data (guards hand-typed numbers)
    problems += _site_number_audit(Path(out_dir), stored)
    return problems


def _site_number_audit(site_dir: Path, snapshot: dict) -> list:
    """Every 'science-looking' number in app.js/index.html must be present in the snapshot values or
    axes. Small structural integers (indices, sizes) and CSS are exempt via an allowlist."""
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
    _collect(snapshot.get("axes", {}))
    _collect(snapshot.get("right_censoring", {}))
    _collect(snapshot.get("near_optimal_sse_tol"))
    # structural integers the UI may use literally without being a science claim
    STRUCTURAL = {str(i) for i in range(0, 13)} | {"100", "1000", "16", "18", "24", "29", "41",
                                                   "10", "20", "40", "50", "60", "255"}
    problems = []
    for name in ("app.js", "index.html"):
        f = site_dir / name
        if not f.exists():
            continue
        text = f.read_text(encoding="utf-8")
        # strip line comments to avoid flagging documentation numbers
        text = re.sub(r"//[^\n]*", "", text)
        for m in re.findall(r"(?<![\w.])-?\d+\.\d+", text):        # decimal literals only
            if _num_key(float(m)) not in allowed and m not in STRUCTURAL:
                problems.append(f"{name}: numeric literal {m} not present in the generated data")
    return problems


def _num_key(x: float) -> str:
    return f"{float(x):.6g}"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="puckworks.public.flat_valley")
    ap.add_argument("cmd", choices=["export", "verify"])
    ap.add_argument("--source", default=str(SOURCE_BUNDLE))
    ap.add_argument("--out", default=str(SITE_DIR))
    a = ap.parse_args(argv)
    if a.cmd == "export":
        payload = export(a.source, a.out)
        print(f"wrote {SNAPSHOT} and {Path(a.out) / 'data.json'} "
              f"(source sha256 {payload['source_bundle_sha256'][:12]}…)")
        return 0
    problems = verify(a.source, a.out)
    if problems:
        print("PV-03 verify FAILED:")
        for p in problems:
            print("  -", p)
        return 1
    print("PV-03 flat-valley snapshot OK (hash-bound, finite, unit-carrying, site-consistent)")
    return 0


# ── runtime producer (reads the packaged snapshot; works from an installed wheel) ──
def pv03_values() -> dict:
    """Return the headline PV-03 values from the packaged snapshot (the PV-03 claim producer)."""
    snap = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
    return snap["values"]


if __name__ == "__main__":
    raise SystemExit(main())
