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
    # MAJ-12/13 RSM deletion + wild-bootstrap diagnostics (review §5.2/§5.4 targets)
    ("RSM most-influential Cook's D ~0.44 (exp 10)",
     "rsm_diagnostics.deletion.most_influential_run.cooks_d", 0.441, 0.03),
    ("RSM full-quadratic vertex ~1.737 (§5.5)",
     "rsm_diagnostics.model_form.full_quadratic_vertex", 1.7373, 0.02),
    # MAJ-14 leave-one-setting-out Q^2 frozen at full precision
    ("RSM LOPO Q2 ~0.470", "rsm_lopo.Q2_predictive", 0.470, 0.03),
    # MAJ-17 Jensen audit: max evaluated-mean shift after clipping is tiny
    ("Jensen post-clip mean shift <0.02", "channeling_audit.max_evaluated_mean_shift", 0.005, 0.02),
    # MAJ-38 Result-3 stochastic distribution median N_eff/N (16 realisations)
    ("N-tube stochastic N_eff/N median tiny (concentrated)",
     "ntube_robustness.stochastic_distribution.n_eff_over_N_median", 0.0025, 0.02),
    # MAJ-23 Result-2 block-bootstrap RMSE difference: Phi(t) beats best constant (<0)
    ("Phi(t) block-bootstrap beats best constant ~-0.39 g/s",
     "result2_residuals.rmse_diff_phi_minus_best_const.median", -0.391, 0.08),
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
    # review MAJ-06/B3-28: hash every input that can change a manuscript number or curve
    # -- run-level cup masses, RSM coefficients, the Waszkiewicz TDS fractions + replicate
    # traces + time-dependent flow traces + static/solids calibrations + constants, and
    # the evidence matrix.
    files = ["schmieder2023/cup_masses.csv", "schmieder2023/rsm_coefficients.csv",
             "schmieder2023/kinetics_fit_params_avg.csv",
             "waszkiewicz2025/tds_fractions.csv",
             "waszkiewicz2025/tds_fractions_replicates.csv",
             "waszkiewicz2025/traces_time_dependent.csv",
             "waszkiewicz2025/static_calibration.csv",
             "waszkiewicz2025/solids_calibration.csv",
             "waszkiewicz2025/constants.csv",
             "paper_b_evidence_matrix.csv",
             "paper_b_evidence_dictionary.csv"]
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


def compute(out_path=_BUNDLE, include_slow=True):
    """Run the Result-1/2/3/4 analyses ONCE and cache the bundle. ~2-3 min without the
    Result-3 robustness study, ~6-8 min with it (include_slow=True; review B3-03)."""
    from puckworks import harness as h
    from puckworks.analysis import lopo_cv
    bundle = dict(
        source_commit=_git("rev-parse", "HEAD"),
        git_dirty=bool(_git("status", "--porcelain")),
        rsm=h.schmieder_rsm_refit("tds", "1/2", predictors="achieved"),
        rsm_diagnostics=h.schmieder_rsm_diagnostics("tds", "1/2"),   # MAJ-12/13 + §5.5
        rsm_lopo=lopo_cv.lopo_rsm_design_point("tds", "1/2", predictors="achieved"),  # MAJ-14
        result1=h.result1_design_aware_stats(),
        channeling_audit=h.channeling_concavity_audit(),             # MAJ-17 Jensen
        ladder=h.kappa_t_ladder(),
        result2_residuals=h.result2_residual_diagnostics(),         # MAJ-23 block bootstrap
        cross_pressure=h.cross_pressure_discrimination(),
        loco=h.cross_pressure_loco(),
    )
    if include_slow:
        bundle["ntube_robustness"] = h.ntube_robustness_study()      # Result 3 (MAJ-33..41)
        bundle["ntube_switching_convergence"] = h.ntube_switching_convergence()  # MAJ-36
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(_jsonable(bundle), f)
    return bundle


def verify(bundle_path=_BUNDLE, timestamp=None, write_manifest=True, strict=False):
    """Check the manuscript claims against the bundle. With strict=True (a RELEASE build)
    a STALE or DIRTY tree is ALSO a failure (review MAJ-04/B3-02); with strict=False (the
    routine claim check, which runs on dirty dev trees) the freshness is only recorded as
    manifest fields, not counted as a claim failure."""
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
    # review MAJ-04/B3-02: a passing claim check from a STALE or DIRTY tree cannot certify
    # the current manuscript. Freshness is a first-class manifest field, and a RELEASE
    # build (strict=True) treats a stale/dirty bundle as a failure so a clean release is
    # provable.
    head = _git("rev-parse", "HEAD")
    dirty = bool(_git("status", "--porcelain"))
    bundle_commit = bundle.get("source_commit")
    bundle_matches_head = bool(bundle_commit == head and head != "UNKNOWN")
    fresh = bool(bundle_matches_head and not dirty)
    if strict and not bundle_matches_head:
        failures.append("RELEASE: bundle source_commit %s != git HEAD %s (stale, MAJ-04)"
                        % (str(bundle_commit)[:12], str(head)[:12]))
    if strict and dirty:
        failures.append("RELEASE: git tree is dirty -- bundle cannot certify the current "
                        "manuscript (MAJ-04)")
    manifest = dict(
        paper="B", source_commit=head, git_dirty=dirty, timestamp_utc=timestamp,
        bundle_source_commit=bundle_commit, bundle_matches_head=bundle_matches_head,
        release_fresh=fresh,
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
    p.add_argument("cmd", choices=["compute", "verify", "full", "release"],
                   nargs="?", default="verify")
    p.add_argument("--timestamp", default=None)
    a = p.parse_args(argv)
    if a.cmd in ("compute", "full", "release"):
        print("computing bundle (~6-8 min with Result-3 robustness)...")
        compute()
    if a.cmd in ("verify", "full", "release"):
        strict = (a.cmd == "release")   # a RELEASE build also requires a fresh clean tree
        ok, failures, manifest = verify(timestamp=a.timestamp, strict=strict)
        print(f"manifest -> {os.path.relpath(_MANIFEST, _ROOT)}")
        print(f"commit {manifest['source_commit'][:12]} (dirty={manifest['git_dirty']}, "
              f"fresh={manifest['release_fresh']}); env {manifest['environment']}")
        print(f"claims: {manifest['n_claims'] - manifest['n_failures']}/"
              f"{manifest['n_claims']} pass")
        for fmsg in failures:
            print("  FAIL:", fmsg)
        if not ok:
            sys.exit(1)
        print("VERIFY OK — Paper B headline numbers match the results bundle."
              + (" RELEASE: clean fresh tree." if strict else ""))


if __name__ == "__main__":
    main()
