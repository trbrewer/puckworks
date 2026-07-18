"""PV-05 "More Physics Made It Worse" — the model-composition public data contract.

A deterministic transform of four NAMED producer functions into a compact public snapshot
(``puckworks/public/data/pv05_model_composition.json``) that the static interactive and the PV-05
``PublicClaim`` producer consume. **No headline number is hand-typed** — every value is computed by a
producer, and the snapshot records the SHA-256 of the canonical source-data files (the CC-BY
Waszkiewicz trace + rig inputs) so ``verify`` fails the moment the underlying data drifts.

The story is one TESTED model composition, not a universal claim:

    * a constant baseline (1 free param) is the minimum a mechanism must beat;
    * an extraction-only time-varying branch (0 free params) follows the rising 9-bar flow far better;
    * adding an imported swelling branch through ONE shared porosity state OVER-closes that state, so
      the composite prediction decouples from the rise and scores WORSE than the constant baseline.

It rejects THIS composition — not swelling in general, and not "more physics is worse".

Producers (authoritative for every displayed value):
    puckworks.harness.kappa_t_ladder                       -> constant + extraction-only RMSE, params
    puckworks.models.brewer2026.coupled_kappa_t.degeneracy_rmse   -> extraction-only cross-check
    puckworks.models.brewer2026.coupled_kappa_t.composition_residual -> composite RMSE + closure flags
    puckworks.models.brewer2026.coupled_kappa_t.simulate          -> the presentation trajectories

CLI::

    python -m puckworks.public.model_composition export   # regenerate snapshot + site data.json
    python -m puckworks.public.model_composition verify    # fail on drift / missing fields / non-finite

Runtime: :func:`pv05_values` reads the packaged snapshot (works from an installed wheel) and returns
the headline values; the PV-05 producer maps its numeric keys onto that return.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import subprocess
from pathlib import Path

import numpy as np

SCHEMA_VERSION = 1
STORY_ID = "PV-05"
TITLE = "More Physics Made It Worse"
_PKG_DIR = Path(__file__).resolve().parent
_REPO = _PKG_DIR.parents[1]
SNAPSHOT = _PKG_DIR / "data" / "pv05_model_composition.json"
SITE_DIR = _REPO / "docs" / "public" / "site" / "model-composition"
GENERATOR = "puckworks.public.model_composition.build_payload"
BADGE = "EXPLORATORY_SIMULATION"          # a model-composition experiment, not an observation
EVIDENCE_STRENGTH = "qualitative"         # a diagnosed mis-scale, reported not tuned away

# The canonical CC-BY source data the producers consume (the observed 9-bar trace + rig inputs).
# Their SHA-256 is baked into the snapshot so `verify` fails on any data-file drift.
_WASZ_DIR = _REPO / "puckworks" / "data" / "waszkiewicz2025"
_SOURCE_DATA_FILES = {
    "traces_time_dependent.csv": _WASZ_DIR / "traces_time_dependent.csv",
    "constants.csv": _WASZ_DIR / "constants.csv",
    "static_calibration.csv": _WASZ_DIR / "static_calibration.csv",
    "solids_calibration.csv": _WASZ_DIR / "solids_calibration.csv",
}

# Fixed producer settings (recorded in the snapshot; not free parameters of a public fit).
P_BAR = 9.0
POWDER = "M"
WINDOW = (15.0, 95.0)
EPS0 = 0.17
EPS_MIN, EPS_MAX = 0.02, 0.95
N_PLOT = 64                                # deterministic downsample width for the site series

# Redistribution: the observed trace is CC-BY-4.0 and may be published with attribution; every model
# trace is puckworks-generated derived output; no paywalled (mo2023_2) raw table is redistributed.
DATASET_MANIFEST_IDS = ["waszkiewicz2025/traces_time_dependent", "waszkiewicz2025/constants"]
ATTRIBUTION = ("Observed 9-bar flow trace: Waszkiewicz, Myck, Białas, Puciata-Mroczyńska, Dzikowski, "
               "Szymczak, Lisicki (2025), 'Under pressure: poroelastic regulation of flow in espresso "
               "brewing', Zenodo record 18046315, DOI 10.5281/zenodo.18046315 (arXiv:2512.21528), "
               "CC-BY-4.0. Swelling branch parameters: mo2023_2 (Elsevier, paywalled) — only derived "
               "model output is shown, no source table is redistributed.")
SOURCE_IDS = {
    "observed_trace": "Zenodo 10.5281/zenodo.18046315 (CC-BY-4.0)",
    "poroelastic_model": "waszkiewicz2025.poroelastic",
    "swelling_model": "mo2023_2.swelling (Elsevier 10.1016/j.jfoodeng.2023.111843, paywalled)",
    "synthesis": "brewer2026.coupled_kappa_t (docs/cards/brewer2026_coupled_kappa_t.md)",
}
MODELS = {
    "brewer2026.coupled_kappa_t": "shared-porosity synthesis (framework fidelity = shakiest branch)",
    "waszkiewicz2025.poroelastic": "poroelastic flow closure (drives the extraction-only branch)",
    "mo2023_2.swelling": "fixed-dP swelling branch (imported pre-fitted parameters)",
}

# The compatibility checklist a composition must answer BEFORE combining components (Scene 4).
COMPOSITION_CHECKLIST = [
    "Does each component use the same state definition?",
    "Does the state share one reference volume and the same bounds?",
    "Are the time origins and the pressure/flow nodes compatible?",
    "Does a fitted parameter in one component already absorb what the other adds?",
    "Are mass and energy balances preserved across the composition?",
    "Do both components operate in overlapping evidence domains?",
    "Is the combined observation operator still physically meaningful?",
    "Does the composite beat a simple null benchmark?",
]

_UNITS = {
    "const_baseline_rmse_g_per_s": "g/s",
    "const_baseline_level_g_per_s": "g/s",
    "extraction_only_rmse_g_per_s": "g/s",
    "extraction_only_rmse_degeneracy_g_per_s": "g/s",
    "composite_rmse_g_per_s": "g/s",
    "rmse_ratio_composite_over_constant": "ratio",
    "rmse_ratio_composite_over_extraction": "ratio",
    "extraction_vs_constant_improvement": "ratio",
    "min_shared_porosity": "porosity fraction (dimensionless)",
    "eps0_reference_porosity": "porosity fraction (dimensionless)",
    "swelling_closes_shared_state": "boolean",
    "composite_clamped": "boolean",
    "eval_window_start_s": "s",
    "eval_window_end_s": "s",
    "constant_free_params": "count",
    "extraction_free_params": "count",
    "n_window_points": "count",
    "degeneracy_agreement_g_per_s": "g/s",
}


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
    except Exception:                                   # pragma: no cover - git-less env
        return "UNKNOWN"


def _downsample(a, n=N_PLOT):
    """Deterministically thin an array to n evenly spaced samples (index striding, endpoints kept)."""
    a = np.asarray(a, float)
    if a.size <= n:
        idx = np.arange(a.size)
    else:
        idx = np.unique(np.linspace(0, a.size - 1, n).round().astype(int))
    return [round(float(v), 5) for v in a[idx]], idx


def build_payload(source_commit: str | None = None) -> dict:
    """Deterministically compute the PV-05 snapshot from the named producers. No wall clock.

    ``source_commit`` is stamped informationally (git HEAD at export); ``verify`` passes the stored
    value back so a new commit alone never marks the snapshot stale — only a producer result or a
    source-data hash change does."""
    from puckworks import harness
    from puckworks.models.brewer2026 import coupled_kappa_t as ck
    from puckworks import data as _d

    ladder = harness.kappa_t_ladder(window=WINDOW)
    deg = float(ck.degeneracy_rmse(P_bar=P_BAR, window=WINDOW))
    comp = ck.composition_residual(P_bar=P_BAR, powder=POWDER, window=WINDOW)

    const_rmse = float(ladder["rung1_const_kappa"])
    const_level = float(ladder["rung1_const_level_g_per_s"])
    ext_rmse = float(ladder["rung4_phi_of_t"])            # extraction-only headline (0 free params)
    comp_rmse = round(float(comp["rmse"]), 3)
    eps_min = round(float(comp["eps_min_reached"]), 4)
    fp = ladder["free_params"]

    # degeneracy cross-check: the coupled model's extraction-only reduction MUST match ladder rung 4
    degeneracy_gap = round(abs(round(deg, 3) - ext_rmse), 4)

    values = {
        "const_baseline_rmse_g_per_s": const_rmse,
        "const_baseline_level_g_per_s": const_level,
        "extraction_only_rmse_g_per_s": ext_rmse,
        "extraction_only_rmse_degeneracy_g_per_s": round(deg, 3),
        "composite_rmse_g_per_s": comp_rmse,
        "rmse_ratio_composite_over_constant": round(comp_rmse / const_rmse, 3),
        "rmse_ratio_composite_over_extraction": round(comp_rmse / ext_rmse, 3),
        "extraction_vs_constant_improvement": round(const_rmse / ext_rmse, 3),
        "min_shared_porosity": eps_min,
        "eps0_reference_porosity": EPS0,
        "swelling_closes_shared_state": bool(comp["swelling_closes"]),
        "composite_clamped": bool(comp["clamped"]),
        "eval_window_start_s": WINDOW[0],
        "eval_window_end_s": WINDOW[1],
        "constant_free_params": int(fp["rung1"]),
        "extraction_free_params": int(fp["rung4"]),
        "n_window_points": int(ladder["n_points"]),
        "degeneracy_agreement_g_per_s": degeneracy_gap,
    }

    # ---- presentation trajectories (simulate is authoritative; observed trace is CC-BY) ----
    tr = _d.waszkiewicz_traces()
    t = tr[P_BAR]["time__s"]
    q_obs = tr[P_BAR]["mass_flow_rate__g_per_s"]
    sim_e = ck.simulate(P_bar=P_BAR, t=t, branches=("extraction",))
    sim_c = ck.simulate(P_bar=P_BAR, t=t, branches=("extraction", "swelling"), powder=POWDER)

    t_ds, idx = _downsample(t)
    at = lambda a: [round(float(v), 5) for v in np.asarray(a, float)[idx]]

    series = [
        {"label": "Observed flow (9 bar)", "values": at(q_obs), "unit": "g/s", "role": "observed",
         "component": "waszkiewicz2025 rig measurement",
         "method": "measured Q(t), downsampled from the CC-BY Zenodo trace",
         "caveat": "one rig, one coffee, one pressure; redistributed under CC-BY-4.0 with attribution"},
        {"label": "Extraction-only prediction", "values": at(sim_e["Q"]), "unit": "g/s",
         "role": "simulated", "component": "brewer2026.coupled_kappa_t (extraction branch)",
         "method": "poroelastic closure driven by the 0-free-parameter dissolution Phi(t)",
         "caveat": "a lower residual is not proof the mechanism is uniquely identified or correct"},
        {"label": "Extraction + swelling composite", "values": at(sim_c["Q"]), "unit": "g/s",
         "role": "simulated", "component": "brewer2026.coupled_kappa_t (extraction+swelling)",
         "method": "same shared-porosity state with the imported mo2023_2 swelling branch added",
         "caveat": "over-closes the shared porosity, so the opening driver floors and the prediction "
                   "flattens at the wrong level — a diagnosed mis-scale, not a tuned fit"},
        {"label": "Constant baseline", "values": [const_level] * len(t_ds), "unit": "g/s",
         "role": "benchmark", "component": "least-squares constant (1 free parameter)",
         "method": "the window-optimal constant flow — the minimum a mechanism must beat",
         "caveat": "deliberately simple; a more complex model that loses to this has not earned it"},
        {"label": "Shared porosity — extraction only", "values": at(sim_e["eps"]),
         "unit": "porosity fraction (dimensionless)", "role": "simulated",
         "component": "brewer2026.coupled_kappa_t (extraction branch)",
         "method": "eps(t) = eps0*(1 + Phi_extraction); opens above the eps0 reference",
         "caveat": "extraction opens the pore space, tracking the rising flow"},
        {"label": "Shared porosity — composite", "values": at(sim_c["eps"]),
         "unit": "porosity fraction (dimensionless)", "role": "simulated",
         "component": "brewer2026.coupled_kappa_t (extraction+swelling)",
         "method": "eps(t) = eps0*(1 + Phi_extraction - Phi_swelling); the swelling branch closes it",
         "caveat": "drops below the eps0 reference (over-closure) — the failure mechanism"},
    ]

    model_params = {
        "eps0_reference_porosity": EPS0, "eps_clamp_min": EPS_MIN, "eps_clamp_max": EPS_MAX,
        "pressure_bar": P_BAR, "swelling_powder_class": POWDER,
        "eval_window_s": list(WINDOW), "time_unit": "s", "flow_unit": "g/s",
        "state_variable": "shared porosity eps (dimensionless)",
    }

    payload = {
        "schema_version": SCHEMA_VERSION,
        "story_id": STORY_ID,
        "title": TITLE,
        "generator": GENERATOR,
        "producers": [
            "puckworks.harness.kappa_t_ladder",
            "puckworks.models.brewer2026.coupled_kappa_t.degeneracy_rmse",
            "puckworks.models.brewer2026.coupled_kappa_t.composition_residual",
            "puckworks.models.brewer2026.coupled_kappa_t.simulate",
        ],
        "source_commit": source_commit if source_commit is not None else _source_commit(),
        "source_data_sha256": {name: _sha256_file(p) for name, p in _SOURCE_DATA_FILES.items()},
        "dataset_manifest_ids": DATASET_MANIFEST_IDS,
        "source_ids": SOURCE_IDS,
        "attribution": ATTRIBUTION,
        "redistribution_class": "observed trace CC-BY-4.0 (redistributable, attributed, downsampled); "
                                "model traces puckworks-derived; no paywalled source table redistributed",
        "models": MODELS,
        "model_params": model_params,
        "badge": BADGE,
        "evidence_strength": EVIDENCE_STRENGTH,
        "time_axis_s": t_ds,
        "values": values,
        "units": _UNITS,
        "series": series,
        "composition_checklist": COMPOSITION_CHECKLIST,
        "scope": "One dataset/campaign (waszkiewicz2025 9-bar trace), one observation operator, one "
                 "tested shared-porosity composition, one shared-state definition; the swelling "
                 "parameters are mo2023_2's, applied to a saturated pre-wet rig.",
        "caveat": "This rejects THIS composition, not swelling in general and not a universal rule "
                  "that added physics reduces accuracy. It does NOT prove the extraction-only "
                  "mechanism is correct or uniquely identified. The composition is not coupled into "
                  "the Guided Espresso Pull. Components are fitted/calibrated; a lower residual is "
                  "verification against one trace, not independent validation.",
        "fidelity_ceiling": "coupled kappa(t) FRAMEWORK; branch fidelity inherited from donors "
                            "(mo2023_2 swelling is fixed-dP and unvalidated on a saturated rig). "
                            "Exploratory model-composition evidence, never a validated composition.",
    }
    return payload


def _canonical_json(payload: dict) -> str:
    return json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False) + "\n"


def _static_summary_text(p: dict) -> str:
    """A deterministic, generated static text equivalent (numbers are NOT hand-typed into the HTML)."""
    v = p["values"]
    lines = [
        "PV-05 — More Physics Made It Worse (static text equivalent)",
        f"Generated by {p['generator']} from the named producers, source commit {p['source_commit']}.",
        f"Badge: {p['badge']}. Evidence strength: {p['evidence_strength']}.",
        "",
        "Finding: a time-varying extraction-only model follows the rising 9-bar flow far better than a "
        "constant baseline. But adding an imported swelling branch through ONE shared porosity state "
        "OVER-closes that state, so the composite prediction decouples from the rise and scores worse "
        "than the constant. The result rejects THIS composition, not swelling physics in general.",
        "",
        "Key numbers (each produced by a named function, over the "
        f"{v['eval_window_start_s']:.0f}-{v['eval_window_end_s']:.0f} s window):",
        f"- constant baseline RMSE (1 free param): {v['const_baseline_rmse_g_per_s']} g/s "
        f"at a level of {v['const_baseline_level_g_per_s']} g/s",
        f"- extraction-only RMSE (0 free params): {v['extraction_only_rmse_g_per_s']} g/s "
        f"(cross-checked by degeneracy_rmse = {v['extraction_only_rmse_degeneracy_g_per_s']} g/s; "
        f"agreement {v['degeneracy_agreement_g_per_s']} g/s)",
        f"- extraction beats the constant by {v['extraction_vs_constant_improvement']}x",
        f"- composite (extraction + swelling) RMSE: {v['composite_rmse_g_per_s']} g/s "
        f"= {v['rmse_ratio_composite_over_constant']}x the constant and "
        f"{v['rmse_ratio_composite_over_extraction']}x the extraction-only model",
        f"- shared porosity over-closes to {v['min_shared_porosity']} (below the eps0 reference "
        f"{v['eps0_reference_porosity']}); swelling closes the shared state: "
        f"{v['swelling_closes_shared_state']}; clamp hit: {v['composite_clamped']}",
        "",
        "What this does NOT claim: that physics is universally harmful; that swelling is absent from "
        "real pucks; that the extraction-only mechanism is proven; or any connection to the Guided "
        "Espresso Pull primary chain.",
        "",
        f"Scope: {p['scope']}",
        f"Caveat: {p['caveat']}",
        f"Fidelity ceiling: {p['fidelity_ceiling']}",
        "",
        "Before combining components, a composition must answer:",
    ]
    lines += [f"  - {q}" for q in p["composition_checklist"]]
    lines += ["", "Reproduce: python -m puckworks.public.model_composition verify", ""]
    return "\n".join(lines)


def export(out_dir: Path | str = SITE_DIR) -> dict:
    """Write the packaged snapshot, the site ``data.json`` (identical bytes), and the generated
    static text equivalent."""
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
    """Return a list of problems (empty == clean). Fails on source-hash drift, snapshot drift, a
    changed producer result, missing fields, non-finite values, missing units, or a site number
    absent from the generated data."""
    problems: list[str] = []
    if not SNAPSHOT.exists():
        return [f"missing snapshot {SNAPSHOT}; run `python -m puckworks.public.model_composition export`"]
    stored_text = SNAPSHOT.read_text(encoding="utf-8")
    stored = json.loads(stored_text)

    # rebuild with the STORED source_commit so a new commit alone is not "drift"
    fresh = build_payload(source_commit=stored.get("source_commit"))
    if _canonical_json(fresh) != stored_text:
        problems.append("packaged snapshot is stale vs a fresh run of the producers (run export)")

    # source-data hash binding (fails if the CC-BY trace / rig inputs change)
    for name, p in _SOURCE_DATA_FILES.items():
        live = _sha256_file(p)
        if stored.get("source_data_sha256", {}).get(name) != live:
            problems.append(f"source-data SHA-256 drift on {name}: snapshot "
                            f"{stored.get('source_data_sha256', {}).get(name)} != live {live}")

    # required top-level metadata
    for f in ("schema_version", "story_id", "title", "generator", "producers", "source_commit",
              "source_data_sha256", "dataset_manifest_ids", "source_ids", "attribution",
              "redistribution_class", "models", "model_params", "badge", "evidence_strength",
              "time_axis_s", "values", "units", "series", "composition_checklist", "scope",
              "caveat", "fidelity_ceiling"):
        if f not in stored:
            problems.append(f"snapshot missing required field: {f}")

    # every headline value has a unit and is finite
    for k, val in stored.get("values", {}).items():
        if k not in stored.get("units", {}) or not str(stored["units"][k]).strip():
            problems.append(f"value '{k}' has no unit")
        if not _all_finite(val):
            problems.append(f"value '{k}' is non-finite")

    # every series carries the required evidence metadata and finite values
    roles = {"observed", "benchmark", "simulated", "derived"}
    n_axis = len(stored.get("time_axis_s", []))
    for s in stored.get("series", []):
        for key in ("label", "values", "unit", "role", "component", "method", "caveat"):
            if key not in s or (isinstance(s.get(key), str) and not s[key].strip()):
                problems.append(f"series '{s.get('label', '?')}' missing '{key}'")
        if s.get("role") not in roles:
            problems.append(f"series '{s.get('label', '?')}' has invalid role {s.get('role')!r}")
        if not _all_finite(s.get("values")):
            problems.append(f"series '{s.get('label', '?')}' has a non-finite value")
        if len(s.get("values", [])) != n_axis:
            problems.append(f"series '{s.get('label', '?')}' length != time axis ({n_axis})")

    # the load-bearing comparison facts must hold (guards a silent producer regression)
    v = stored.get("values", {})
    if not (v.get("extraction_only_rmse_g_per_s", 9) < v.get("const_baseline_rmse_g_per_s", 0)):
        problems.append("extraction-only RMSE is not below the constant baseline")
    if not (v.get("composite_rmse_g_per_s", 0) > v.get("extraction_only_rmse_g_per_s", 9)):
        problems.append("composite RMSE is not above extraction-only")
    if not (v.get("composite_rmse_g_per_s", 0) > v.get("const_baseline_rmse_g_per_s", 9)):
        problems.append("composite RMSE is not above the constant baseline")
    if v.get("degeneracy_agreement_g_per_s", 9) > 1e-3:
        problems.append("extraction-only and degeneracy_rmse disagree beyond tolerance")
    if not v.get("swelling_closes_shared_state"):
        problems.append("producer no longer reports the swelling branch closing the shared state")

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

    # no numeric literal in the site HTML/JS that is absent from the generated data
    problems += _site_number_audit(Path(out_dir), stored)
    return problems


def _num_key(x: float) -> str:
    return f"{float(x):.6g}"


def _site_number_audit(site_dir: Path, snapshot: dict) -> list:
    """Every 'science-looking' decimal in app.js/index.html must be present in the generated data.
    Structural integers (indices, sizes) and CSS are exempt via an allowlist."""
    import re
    allowed: set[str] = set()

    def _collect(x):
        if isinstance(x, bool):
            return
        if isinstance(x, (int, float)):
            allowed.add(_num_key(x))
        elif isinstance(x, list):
            for val in x:
                _collect(val)
        elif isinstance(x, dict):
            for val in x.values():
                _collect(val)

    _collect(snapshot.get("values", {}))
    _collect(snapshot.get("time_axis_s", []))
    _collect(snapshot.get("model_params", {}))
    for s in snapshot.get("series", []):
        _collect(s.get("values", []))
    STRUCTURAL = {str(i) for i in range(0, 13)} | {"100", "1000", "16", "18", "20", "24", "40",
                                                   "50", "60", "64", "255", "0.5", "1.5", "2.5"}
    problems = []
    for name in ("app.js", "index.html"):
        f = site_dir / name
        if not f.exists():
            continue
        text = f.read_text(encoding="utf-8")
        text = re.sub(r"//[^\n]*", "", text)                      # strip line comments
        for m in re.findall(r"(?<![\w.])-?\d+\.\d+", text):        # decimal literals only
            if _num_key(float(m)) not in allowed and m not in STRUCTURAL:
                problems.append(f"{name}: numeric literal {m} not present in the generated data")
    return problems


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="puckworks.public.model_composition")
    ap.add_argument("cmd", choices=["export", "verify"])
    ap.add_argument("--out", default=str(SITE_DIR))
    a = ap.parse_args(argv)
    if a.cmd == "export":
        payload = export(a.out)
        digest = next(iter(payload["source_data_sha256"].values()))[:12]
        print(f"wrote {SNAPSHOT} and {Path(a.out) / 'data.json'} (trace sha256 {digest}…)")
        return 0
    problems = verify(a.out)
    if problems:
        print("PV-05 verify FAILED:")
        for p in problems:
            print("  -", p)
        return 1
    print("PV-05 model-composition snapshot OK (producer-bound, finite, unit-carrying, site-consistent)")
    return 0


# ── runtime producer (reads the packaged snapshot; works from an installed wheel) ──
def pv05_values() -> dict:
    """Return the headline PV-05 values from the packaged snapshot (the PV-05 claim producer)."""
    snap = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
    return snap["values"]


if __name__ == "__main__":
    raise SystemExit(main())
