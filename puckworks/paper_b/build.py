"""Paper B reproducibility build (review AR-B2-13).

Paper B's figures currently recompute their analyses live; this wrapper adds the
single immutable results bundle the review asks for. `compute` runs the Result-1/2/4
analyses ONCE into `docs/figures/paper_b_results.json` (provenance-stamped, no
hand-typed numbers); `verify` checks the manuscript-facing headline numbers against
that bundle and writes a provenance manifest (commit, env, data hashes). The slow
Result-3 robustness sweep (`ntube_robustness_study`) is referenced, not bundled here.

    python -m puckworks.paper_b.build compute   # ~2-3 min: build the results bundle
    python -m puckworks.paper_b.build verify     # fast: check bundle vs claims + manifest
    python -m puckworks.paper_b.build full        # compute then verify

Mirrors puckworks/paper_a/build.py: the _CLAIMS table is the single source of truth
linking each manuscript number to a bundle field with a declared tolerance.
"""
from __future__ import annotations
import hashlib
import json
import os
import subprocess
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_BUNDLE = os.path.join(_ROOT, "docs/figures/paper_b_results.json")
_MANIFEST = os.path.join(_ROOT, "docs/reproducibility/paper_b_manifest.json")
_DATA = os.path.join(_ROOT, "puckworks/data")

_CLAIMS = [
    ("RSM achieved-predictor vertex ~1.74", "rsm.vertex_g", 1.744, 0.02),
    ("RSM achieved adj-R2 ~0.64",           "rsm.adj_r2", 0.643, 0.02),
    ("RSM joint concave+in-domain ~0.998",  "rsm.bootstrap_concave_AND_in_domain_fraction", 0.9985, 0.01),
    ("RSM centered kappa2(X) ~3.9",         "rsm.diagnostics.centered_scaled_condition_number_kappa2_X", 3.89, 0.3),
    ("RSM n_center_runs = 6 (exp 7)",       "rsm.n_center_runs", 6, 0.5),
    ("Result-1 trend slope ~2.26",          "result1.trend.slope_EYpt_per_dial", 2.258, 0.05),
    ("ladder rung4 Phi(t) RMSE ~0.116",     "ladder.rung4_phi_of_t", 0.116, 0.02),
    ("ladder best-const null ~0.573",       "ladder.rung1_const_kappa", 0.573, 0.02),
    ("ladder flexible cubic ~0.096",        "ladder.flexible_cubic_null", 0.096, 0.02),
    ("cross-pressure Phi transfer ~0.356",  "cross_pressure.conditional_transfer_mean_full_precision.phi", 0.356, 0.02),
    ("LOPO held-out Phi ~0.347",            "loco.heldout_mean.phi", 0.347, 0.02),
    ("LOPO max calibration drift ~2.8%",    "loco.max_calibration_drift", 0.0283, 0.01),
]


def _get(obj, path):
    cur = obj
    for key in path.split("."):
        cur = cur[key]
    return cur


def _sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _git(*args):
    try:
        return subprocess.check_output(["git", *args], cwd=_ROOT,
                                       stderr=subprocess.DEVNULL).decode().strip()
    except Exception:
        return "UNKNOWN"


def _env():
    import numpy, scipy
    v = {"python": sys.version.split()[0], "numpy": numpy.__version__,
         "scipy": scipy.__version__}
    try:
        import matplotlib
        v["matplotlib"] = matplotlib.__version__
    except Exception:
        v["matplotlib"] = "ABSENT"
    return v


def _data_hashes():
    files = ["schmieder2023/cup_masses.csv", "schmieder2023/rsm_coefficients.csv",
             "waszkiewicz2025/tds_fractions.csv", "paper_b_evidence_matrix.csv"]
    out = {}
    for rel in files:
        p = os.path.join(_DATA, rel)
        out[rel] = _sha256(p) if os.path.exists(p) else "MISSING"
    return out


def _jsonable(o):
    if isinstance(o, dict):
        return {(k if isinstance(k, (str, int, float, bool)) or k is None else str(k)):
                _jsonable(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [_jsonable(x) for x in o]
    return o


def compute(out_path=_BUNDLE):
    """Run the Result-1/2/4 analyses ONCE and cache the bundle (~2-3 min)."""
    from puckworks import harness as h
    bundle = dict(
        source_commit=_git("rev-parse", "HEAD"),
        rsm=h.schmieder_rsm_refit("tds", "1/2", predictors="achieved"),
        result1=h.result1_design_aware_stats(),
        ladder=h.kappa_t_ladder(),
        cross_pressure=h.cross_pressure_discrimination(),
        loco=h.cross_pressure_loco(),
    )
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(_jsonable(bundle), f)
    return bundle


def verify(bundle_path=_BUNDLE, timestamp=None, write_manifest=True):
    with open(bundle_path) as f:
        bundle = json.load(f)
    failures, checked = [], []
    for label, path, expected, tol in _CLAIMS:
        try:
            actual = float(_get(bundle, path))
        except (KeyError, TypeError):
            failures.append(f"{label}: bundle field '{path}' MISSING")
            continue
        ok = abs(actual - expected) <= tol
        checked.append(dict(claim=label, path=path, expected=expected, actual=actual,
                            tol=tol, ok=ok))
        if not ok:
            failures.append(f"{label}: bundle {actual} vs manuscript {expected} "
                            f"(|Δ| {abs(actual - expected):.4f} > tol {tol})")
    manifest = dict(
        paper="B", source_commit=_git("rev-parse", "HEAD"),
        git_dirty=bool(_git("status", "--porcelain")), timestamp_utc=timestamp,
        bundle_source_commit=bundle.get("source_commit"),
        bundle_sha256=_sha256(bundle_path), environment=_env(),
        data_sha256=_data_hashes(), n_claims=len(_CLAIMS), n_failures=len(failures),
        claims=checked, verified=(len(failures) == 0))
    if write_manifest:
        os.makedirs(os.path.dirname(_MANIFEST), exist_ok=True)
        with open(_MANIFEST, "w") as f:
            json.dump(manifest, f, indent=2)
    return (len(failures) == 0), failures, manifest


def main(argv=None):
    import argparse
    p = argparse.ArgumentParser(prog="puckworks.paper_b.build")
    p.add_argument("cmd", choices=["compute", "verify", "full"], nargs="?", default="verify")
    p.add_argument("--timestamp", default=None)
    a = p.parse_args(argv)
    if a.cmd in ("compute", "full"):
        print("computing bundle (~2-3 min)...")
        compute()
    if a.cmd in ("verify", "full"):
        ok, failures, manifest = verify(timestamp=a.timestamp)
        print(f"manifest -> {os.path.relpath(_MANIFEST, _ROOT)}")
        print(f"commit {manifest['source_commit'][:12]} (dirty={manifest['git_dirty']}); "
              f"env {manifest['environment']}")
        print(f"claims: {manifest['n_claims'] - manifest['n_failures']}/"
              f"{manifest['n_claims']} pass")
        for fmsg in failures:
            print("  FAIL:", fmsg)
        if not ok:
            sys.exit(1)
        print("VERIFY OK — Paper B headline numbers match the results bundle.")


if __name__ == "__main__":
    main()
