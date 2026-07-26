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

    # ---- review 4.13: every number in Tables 2/3, the shot-level results, the held-out
    # comparator and the residual diagnostics is bound to a producer. Before this, 18 claims
    # covered a manuscript containing far more results, and an unregistered number was an
    # unchecked number that looked exactly like a checked one.
    # Table 2 — the remaining ladder rows and the two ratios stated in the prose
    ("Table 2 late-window constant ~0.641",  "ladder.rung1b_longrun_const", 0.641, 0.01),
    ("Table 2 static kappa(P) ~0.648",       "ladder.rung3_static_kappaP", 0.648, 0.01),
    ("Table 2 improvement vs best constant ~4.9x", "ladder.improvement_factor", 4.9, 0.1),
    ("Table 2 improvement vs static ~5.6x",  "ladder.improvement_vs_static", 5.6, 0.1),
    # Table 3 — all nine cells
    ("Table 3 LOPO-EC static ~0.534",        "loco.heldout_mean.static", 0.534, 0.01),
    ("Table 3 LOPO-EC Phi(t) ~0.347",        "loco.heldout_mean.phi", 0.347, 0.01),
    ("Table 3 LOPO-EC rc3b ~0.516",          "loco.heldout_mean.rc3b", 0.516, 0.01),
    ("Table 3 shared static ~0.524",         "loco.shared_calibration_mean.static", 0.524, 0.01),
    ("Table 3 shared Phi(t) ~0.334",         "loco.shared_calibration_mean.phi", 0.334, 0.01),
    ("Table 3 shared rc3b ~0.510",           "loco.shared_calibration_mean.rc3b", 0.510, 0.01),
    ("Table 3 off-9-bar static ~0.512",
     "cross_pressure.conditional_transfer_mean_full_precision.static", 0.512, 0.01),
    ("Table 3 off-9-bar rc3b ~0.522",
     "cross_pressure.conditional_transfer_mean_full_precision.rc3b", 0.522, 0.01),
    # Shot-level results (§5.2a) — the exact randomization test and the noise floor
    ("shot noise floor ~0.149 g/s",
     "shot_level.noise_floor.noise_floor_rmse_g_per_s", 0.1492, 0.005),
    ("Phi(t) minus constant, per-shot mean ~-0.390 g/s",
     "shot_level.paired.comparisons.phi_vs_const.mean_difference_g_per_s", -0.3904, 0.005),
    ("Phi(t) minus static, per-shot mean ~-0.472 g/s",
     "shot_level.paired.comparisons.phi_vs_static.mean_difference_g_per_s", -0.4717, 0.005),
    ("exact randomization p = 2/32 (design floor)",
     "shot_level.paired.comparisons.phi_vs_const.exact_randomization_p", 0.0625, 0.0001),
    # Held-out flexible comparator (§5.2a) — the result that DOWN-scoped the temporal claim
    ("leave-one-shot-out spline ~0.186", "shot_level.heldout.leave_one_shot_out_mean.spline", 0.1861, 0.003),
    ("leave-one-shot-out Phi(t) ~0.189", "shot_level.heldout.leave_one_shot_out_mean.phi", 0.1894, 0.003),
    ("leave-one-shot-out Phi(t) cross-fit ~0.190",
     "shot_level.heldout.leave_one_shot_out_mean.phi_equilibrium_crossfit", 0.1897, 0.003),
    ("leave-one-shot-out constant ~0.600", "shot_level.heldout.leave_one_shot_out_mean.const", 0.5995, 0.005),
    ("leave-one-shot-out static ~0.661", "shot_level.heldout.leave_one_shot_out_mean.static", 0.6611, 0.005),
    ("Phi(t) minus held-out spline ~0.003 (below the noise floor)",
     "shot_level.heldout.phi_minus_spline_heldout_g_per_s", 0.0033, 0.002),
    ("leave-segment-out interior Phi(t) ~0.158",
     "shot_level.heldout.leave_segment_out_interior_mean.phi", 0.1579, 0.003),
    ("leave-segment-out interior spline ~0.233",
     "shot_level.heldout.leave_segment_out_interior_mean.spline", 0.233, 0.003),
    ("leave-segment-out interior constant ~0.419",
     "shot_level.heldout.leave_segment_out_interior_mean.const", 0.4193, 0.003),
    # Residual diagnostics at the DECLARED 1 s resolution (§5.2a). The between-shot sd here
    # (0.1529) is the decimated-series quantity and is NOT the same as the full-resolution
    # 0.154 in shot_level.noise_floor -- two nearly-equal numbers that must not be swapped.
    ("residual diagnostics between-shot sd ~0.153 (1 s series)",
     "shot_level.residuals_1s.between_shot_sd_mean_g_per_s", 0.1529, 0.002),
    ("residual lag-1 ACF, constant ~0.958",
     "shot_level.residuals_1s.branches.rung1_const.lag1_autocorrelation", 0.9579, 0.002),
    ("residual lag-1 ACF, Phi(t) ~0.969",
     "shot_level.residuals_1s.branches.rung4_phi_of_t.lag1_autocorrelation", 0.9687, 0.002),
    ("residual lag-1 ACF, cubic ~0.904",
     "shot_level.residuals_1s.branches.flexible_cubic.lag1_autocorrelation", 0.9041, 0.002),
    ("static MAE ~0.370 beats constant MAE ~0.478 (ordering reversal)",
     "shot_level.residuals_1s.branches.rung3_static.mae_g_per_s", 0.3695, 0.003),
    ("constant MAE ~0.478", "shot_level.residuals_1s.branches.rung1_const.mae_g_per_s", 0.478, 0.003),
    ("static mean bias ~-0.312 (why MAE and RMSE disagree)",
     "shot_level.residuals_1s.branches.rung3_static.mean_bias_g_per_s", -0.3121, 0.003),
    ("residual/between-shot ratio, constant ~3.8",
     "shot_level.residuals_1s.branches.rung1_const.residual_over_between_shot_sd", 3.81, 0.05),
    ("residual/between-shot ratio, static ~4.3",
     "shot_level.residuals_1s.branches.rung3_static.residual_over_between_shot_sd", 4.323, 0.05),
    ("residual/between-shot ratio, Phi(t) ~0.76",
     "shot_level.residuals_1s.branches.rung4_phi_of_t.residual_over_between_shot_sd", 0.756, 0.02),
    ("residual/between-shot ratio, cubic ~0.65",
     "shot_level.residuals_1s.branches.flexible_cubic.residual_over_between_shot_sd", 0.648, 0.02),
    # The 5 s check that shows the structure is resolution-dependent
    ("residual lag-1 ACF at 5 s, Phi(t) ~0.533",
     "shot_level.residuals_5s.branches.rung4_phi_of_t.lag1_autocorrelation", 0.533, 0.005),
    ("residual lag-1 ACF at 5 s, constant ~0.786",
     "shot_level.residuals_5s.branches.rung1_const.lag1_autocorrelation", 0.786, 0.005),
    ("residual lag-1 ACF at 5 s, cubic ~0.471",
     "shot_level.residuals_5s.branches.flexible_cubic.lag1_autocorrelation", 0.471, 0.005),
    ("residual DW at 1 s, Phi(t) ~0.047",
     "shot_level.residuals_1s.branches.rung4_phi_of_t.durbin_watson", 0.0468, 0.002),
    ("residual DW at 1 s, constant ~0.005",
     "shot_level.residuals_1s.branches.rung1_const.durbin_watson", 0.0049, 0.002),
    ("residual DW at 1 s, static ~0.004",
     "shot_level.residuals_1s.branches.rung3_static.durbin_watson", 0.0038, 0.002),
    ("residual DW at 1 s, cubic ~0.067",
     "shot_level.residuals_1s.branches.flexible_cubic.durbin_watson", 0.0667, 0.002),
    ("Phi(t) minus cubic, per-shot mean ~+0.083 g/s (below the noise floor)",
     "shot_level.paired.comparisons.phi_vs_cubic.mean_difference_g_per_s", 0.0826, 0.003),
    # Recorded-pressure robustness (§5.2). These six values were TRANSCRIBED from a reviewer's
    # independent table until review 4.13's coverage audit found they had no producer here.
    ("recorded-pressure static nominal 0.647696",
     "shot_level.recorded_pressure.static_nominal_rmse_g_per_s", 0.647696, 1e-5),
    ("recorded-pressure static recorded 0.646846",
     "shot_level.recorded_pressure.static_recorded_rmse_g_per_s", 0.646846, 1e-5),
    ("recorded-pressure static delta -0.00085",
     "shot_level.recorded_pressure.static_delta_g_per_s", -0.00085, 1e-5),
    ("recorded-pressure Phi(t) nominal 0.115769",
     "shot_level.recorded_pressure.phi_nominal_rmse_g_per_s", 0.115769, 1e-5),
    ("recorded-pressure Phi(t) recorded 0.116443",
     "shot_level.recorded_pressure.phi_recorded_rmse_g_per_s", 0.116443, 1e-5),
    ("recorded-pressure Phi(t) delta +0.000673",
     "shot_level.recorded_pressure.phi_delta_g_per_s", 0.000673, 1e-5),
    # Equilibrium-window sensitivity (§2) — the values quoted when justifying the observable
    ("window sensitivity 90-100 s P_c ~12.391",
     "shot_level.window_sensitivity.windows.mean_90_100s.P_c_bar", 12.391, 0.002),
    ("window sensitivity 90-100 s Q_c ~1.914",
     "shot_level.window_sensitivity.windows.mean_90_100s.Q_c_g_per_s", 1.914, 0.002),
    ("window sensitivity 110-120 s (excl. contaminated) P_c ~11.935",
     "shot_level.window_sensitivity.windows.mean_110_120s_excl_contaminated.P_c_bar", 11.935, 0.002),
    ("window sensitivity 110-120 s (excl. contaminated) Q_c ~1.861",
     "shot_level.window_sensitivity.windows.mean_110_120s_excl_contaminated.Q_c_g_per_s", 1.861, 0.002),
    # §5.3b — replaced two numbers the audit could not reproduce (0.61 bar, 8.71 bar)
    ("max mean pressure deficit 0.508 bar",
     "shot_level.nominal_vs_recorded.max_mean_deficit_bar", 0.5076, 0.001),
    ("max saturated-interval mean deficit 0.540 bar",
     "shot_level.nominal_vs_recorded.max_mean_deficit_saturated_bar", 0.5395, 0.001),
    ("max pointwise deficit 0.673 bar",
     "shot_level.nominal_vs_recorded.max_pointwise_deficit_saturated_bar", 0.6726, 0.001),
    ("9-bar delivered mean 8.768 bar",
     "shot_level.nominal_vs_recorded.nine_bar_mean_recorded_bar", 8.7679, 0.001),
    # decimated-resolution RMSEs quoted in the MAE/RMSE ordering-reversal paragraph
    ("decimated RMSE, constant ~0.583",
     "shot_level.residuals_1s.branches.rung1_const.rmse_g_per_s", 0.5826, 0.002),
    ("decimated RMSE, static ~0.661",
     "shot_level.residuals_1s.branches.rung3_static.rmse_g_per_s", 0.661, 0.002),
    # swelling branch scale (§5.4)
    ("swelling branch RMSE with a free level ~1.08",
     "ladder.rung5b_swelling_mo2", 1.082, 0.005),
    ("swelling correlation with the measured trace ~-0.951",
     "ladder.rung5b_swelling_corr_with_trace", -0.951, 0.005),
    # Block-bootstrap intervals quoted in §5.2 / §5.2a. The 24 s row is the one that excludes
    # zero; the 16 s row does not, and the manuscript distinguishes them.
    ("Phi(t) minus cubic median ~+0.02",
     "result2_residuals.rmse_diff_phi_minus_cubic.median", 0.022, 0.003),
    ("Phi(t) minus cubic 95% lower ~-0.01",
     "result2_residuals.rmse_diff_phi_minus_cubic.ci95.0", -0.008, 0.003),
    ("Phi(t) minus cubic 95% upper ~+0.05",
     "result2_residuals.rmse_diff_phi_minus_cubic.ci95.1", 0.053, 0.003),
    ("24 s block Phi(t) minus cubic lower ~+0.001",
     "result2_residuals.block_length_sensitivity.3.phi_minus_cubic.ci95.0", 0.001, 0.0005),
    ("24 s block Phi(t) minus cubic upper ~+0.04",
     "result2_residuals.block_length_sensitivity.3.phi_minus_cubic.ci95.1", 0.04, 0.002),
]


def _per_pressure_claims():
    """Expand the §5.3 per-pressure table into one claim per printed cell.

    Generated rather than hand-written: the table has 11 pressures x 3 branches, and transcribing
    33 claims by hand is precisely how Table 3's `rc3b` column went stale in every row. The claims
    are derived from the SAME producer the manuscript's table is printed from, so a cell that
    changes upstream either updates the table or fails the check.
    """
    import json as _json
    import os as _os
    if not _os.path.exists(_BUNDLE):
        return []
    try:
        with open(_BUNDLE) as fh:
            per_pressure = _json.load(fh)["cross_pressure"]["per_pressure"]
    except (KeyError, ValueError, OSError):
        return []
    out = []
    for pressure in sorted(per_pressure, key=float):
        for branch, value in sorted(per_pressure[pressure].items()):
            out.append((f"per-pressure {pressure} bar {branch} ~{value}",
                        f"cross_pressure.per_pressure.{pressure}.{branch}",
                        float(value), 0.0005))
    return out


#: The per-pressure cells are appended at import time so `verify` and the coverage audit see one
#: claim list. They are read from the committed bundle, so this cannot invent a claim that no
#: producer supports -- if the bundle is missing the table, zero claims are added and the coverage
#: audit reports the cells as UNACCOUNTED rather than silently passing.
_CLAIMS = _CLAIMS + _per_pressure_claims()


def _get(obj, path):
    """Resolve a dotted path, tolerating keys that themselves contain dots.

    The per-pressure table is keyed by pressure ("11.0"), so a naive split on "." turns
    `cross_pressure.per_pressure.11.0.phi` into a lookup for "11" then "0" and every cell reports
    MISSING. At each step, prefer the longest key that actually exists in the mapping.
    """
    cur = obj
    parts = path.split(".")
    i = 0
    while i < len(parts):
        if isinstance(cur, dict):
            for take in range(len(parts) - i, 0, -1):     # longest match first
                key = ".".join(parts[i:i + take])
                if key in cur:
                    cur = cur[key]
                    i += take
                    break
            else:
                raise KeyError(parts[i])
        elif isinstance(cur, (list, tuple)):
            cur = cur[int(parts[i])]        # ci95.0 / block_length_sensitivity.3
            i += 1
        else:
            cur = cur[parts[i]]
            i += 1
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
    # review 4.13: the shot-level layer is a first-class part of the results, so its producers
    # belong in the bundle rather than being recomputed ad hoc. Without this, Tables 2/3 aside,
    # every number in §5.2a was unregistered -- and an unregistered number is an unchecked one.
    from puckworks.analysis import waszkiewicz_shot_level as wsl
    bundle["shot_level"] = dict(
        ladder=wsl.per_shot_ladder(),
        noise_floor=wsl.shot_level_noise_floor(),
        paired=wsl.paired_shot_uncertainty(),
        loso_phi=wsl.leave_one_shot_out_phi(),
        heldout=wsl.held_out_flexible_comparator(),
        window_sensitivity=wsl.equilibrium_window_sensitivity(),
        residuals_1s=wsl.residual_diagnostics(resolution_s=1.0),
        residuals_5s=wsl.residual_diagnostics(resolution_s=5.0),
        # review 4.13 found the six recorded-pressure values in §5.2 had been transcribed from a
        # reviewer's independent table with no producer of ours behind them. This is that producer;
        # it reproduces the reviewer's numbers exactly.
        recorded_pressure=wsl.recorded_pressure_robustness(),
        # §5.3b nominal-vs-recorded: the audit could not reproduce the stated 0.61 bar / 8.71 bar
        # under any natural definition, so both are now computed here under a declared one.
        nominal_vs_recorded=wsl.nominal_vs_recorded_pressure(),
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
