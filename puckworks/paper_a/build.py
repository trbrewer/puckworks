"""Paper A reproducibility build (review A2-05 / A2-13 / MAJ-19).

One command that (a) records a provenance manifest — commit SHA + dirty flag,
Python/NumPy/SciPy/Matplotlib versions, source-data SHA-256 hashes, the results-bundle
hash, and a UTC timestamp passed in — and (b) VERIFIES that the manuscript-facing
headline numbers equal the values in the machine-readable results bundle
(`docs/figures/paper_a/results.json`), failing loudly on any drift.

    python -m puckworks.paper_a.build verify   # fast: check bundle vs claims + manifest
    python -m puckworks.paper_a.build render    # fast: redraw the six figures from bundle
    python -m puckworks.paper_a.build full       # SLOW (~30 min): recompute bundle, then verify + render

The claims map below is the single source of truth linking every headline manuscript
number to a bundle field; a mismatch beyond tolerance fails the build. This is the strict
wrapper the reviews asked for on top of the existing `figures_paper_a.compute_all`
(which already regenerates every analysis with no hand-typed numbers); it does NOT invent
numbers -- it pins the manuscript to the bundle. Deterministic tolerances are declared
per claim (PDE/bootstrap noise), not hidden.
"""
from __future__ import annotations
import hashlib
import json
import os
import subprocess
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_BUNDLE = os.path.join(_ROOT, "docs/figures/paper_a/results.json")
_MANIFEST = os.path.join(_ROOT, "docs/reproducibility/paper_a_manifest.json")
_DATA = os.path.join(_ROOT, "puckworks/data")

# Manuscript-facing claims -> (bundle path, expected value, absolute tolerance). The
# bundle path is a dotted/indexed accessor into results.json. Tolerances cover PDE-grid
# + bootstrap-seed determinism, not sloppiness.
_CLAIMS = [
    ("caffeine condition number ~1930",     "panel_caffeine.condition_number", 1927.0, 60.0),
    ("caffeine curvature coupling ~-0.99",  "panel_caffeine.local_curvature_coupling", -0.99, 0.02),
    ("caffeine SSE profile flat ~76%",      "panel_caffeine.profile_fraction_of_log_grid", 0.76, 0.06),
    ("caffeine MAPE cross-check ~66%",      "panel_caffeine.mape_profile_fraction_within10pct", 0.66, 0.06),
    ("trigonelline condition number ~3600", "panel_trigonelline.condition_number", 3619.0, 150.0),
    ("joint pooled MAPE 6.4%",              "joint.mean_joint_pooled_mape", 6.4, 0.4),
    ("joint independent MAPE 4.9%",         "joint.mean_independent_per_grind_mape", 4.9, 0.4),
    ("joint cost-of-sharing 1.5pp",         "joint.cost_of_sharing_pp", 1.5, 0.4),
    ("LOCO pooled mean 6.5%",               "loco.pooled_loco_mean_mape", 6.5, 0.4),
    ("LOCO median 5.2%",                    "loco.pooled_loco_median_mape", 5.2, 0.4),
    ("manifold worst held-out ~22%",        "transfer.manifold_worst_heldout_mape", 21.7, 2.0),
    ("point worst held-out ~18%",           "transfer.point_worst_heldout_mape", 18.2, 2.0),
    ("Result-1 named holdout 8.4%",         "refit_summary.mean_holdout_named", 8.4, 0.5),
    ("Waszkiewicz sensitivity range-ratio floor >1.5",
     "external_waszkiewicz_sensitivity.fraction_range_ratio_min", 1.86, 0.15),
    ("discrepancy control irreducible floor ~4.8% (moderate)",
     "full_cup_discrepancy.mean_irreducible_frac_mape_floor", 4.82, 0.7),
    ("discrepancy large-dose biases located rate (100% of seeds)",
     "full_cup_discrepancy_large.mean_located_rate_biased_fraction", 1.0, 0.05),
    ("continuous-optimiser rate optimum interior ~0.66",
     "identifiability_convergence.continuous_optimiser.continuous_rate_optimum", 0.66, 0.20),
    ("endpoint-mass caveat: MAPE moves ~5pp over 38-42 g",
     "endpoint_mass_sensitivity.overall_mape_spread_pp", 5.3, 1.5),
    # A3-01 null-benchmark skill (submission-blocking finding)
    ("level-only comparator skill ~4.5% (small)",
     "transfer_skill.skill_vs_const", 0.045, 0.04),
    ("model pooled held-out MAPE ~8.4%", "transfer_skill.pooled_model_mape", 8.44, 0.5),
    ("O-trained comparator MAPE ~8.8%",
     "transfer_skill.pooled_const_mape", 8.83, 0.5),
    # A3-03 geometry spread at FULL precision (was rounded to integers)
    ("geometry spread ~0.6pp full precision (A3-03)",
     "geometry_sensitivity.max_geometry_spread_pp", 0.6, 0.5),
    # A3-13 Table 7 orthogonal inventory collapses the caffeine rate to ~0.95
    ("Table 7 inventory implies caffeine rate ~0.95",
     "table7_rate_constraint.caffeine.implied_rate", 0.95, 0.25),
    # A3-11 condition-wise prediction envelope: median width ~3% of obs
    ("condition-envelope median width ~0.03 of obs (A3-11)",
     "transfer.median_condition_envelope_frac_of_obs", 0.029, 0.02),
    # A3-19 in-sample COMPARATOR ladder (non-nested; no likelihood-ratio reading): the shared
    # mechanistic fit beats per-grind constants in 0/6 fits. NOTE the bundle KEY keeps its historical
    # `reduced_model_ladder.` prefix -- it is a frozen result-bundle identifier, not manuscript prose.
    ("in-sample comparator ladder: mech beats per-grind const in 0 fits (A3-19)",
     "reduced_model_ladder.n_fits_mech_beats_pergrind_const", 0.0, 0.5),
    # A3-15/16 off-grid + realistic-noise sim: fraction recovers, cup does not
    ("off-grid+noise sim: fraction recovers off-grid rate <1% (A3-16)",
     "full_cup_offgrid_noise.mean_frac_recovered_err_pct", 0.2, 1.0),
    ("off-grid+noise sim: fraction beats cup in all 9 cases (A3-15)",
     "full_cup_offgrid_noise.n_frac_beats_cup", 9.0, 0.5),

    # ---- review self-audit 2026-07-26: the claim map checked 27 numbers in a manuscript body
    # holding ~530. Every value below was verified against its producer during that audit; they are
    # registered here so a future edit cannot silently invalidate one, which is how Paper 2's
    # Table 3 rc3b column went stale in every row.
    # Section 3.1 — matched endpoint vs blind residual
    ("named-solute macro-MAPE blind ~26.3%", "per_condition.overall_mape_blind", 26.3, 0.05),
    ("proxy-inclusive macro-MAPE ~22.7%",
     "per_condition.overall_mape_blind_proxy_inclusive", 22.7, 0.05),
    ("crude-tau flow map ~26.8%", "flow_map_refinement.overall_mape_crude_tau", 26.8, 0.05),
    ("refined Darcy flow map ~26.3%", "flow_map_refinement.overall_mape_refined_darcy", 26.3, 0.05),
    ("flow-map refinement closes ~0.5 pp", "flow_map_refinement.closed_pp", 0.5, 0.05),
    # Endpoint-mass sensitivity (38 / 40 / 42 mL)
    ("endpoint 38 mL blind MAPE ~23.8%",
     "endpoint_mass_sensitivity.rows.0.overall_mape_blind", 23.8, 0.05),
    ("endpoint 42 mL blind MAPE ~28.8%",
     "endpoint_mass_sensitivity.rows.2.overall_mape_blind", 28.8, 0.05),
    ("endpoint MAPE spread ~5.0 pp",
     "endpoint_mass_sensitivity.overall_mape_spread_pp", 5.0, 0.05),
    # Section 3.2 — identifiability panels
    ("caffeine condition number ~1900", "panel_caffeine.condition_number", 1927.0, 30.0),
    ("caffeine curvature coupling ~-0.99", "panel_caffeine.local_curvature_coupling", -0.994, 0.01),
    ("caffeine profile log-width ~2.8", "panel_caffeine.profile_log_width", 2.827, 0.02),
    ("caffeine near-optimal set covers ~76% of the grid",
     "panel_caffeine.profile_fraction_of_log_grid", 0.76, 0.005),
    ("caffeine MAPE set covers ~66% of the grid",
     "panel_caffeine.mape_profile_fraction_within10pct", 0.66, 0.005),
    ("caffeine SSE/MAPE set Jaccard ~0.86",
     "panel_caffeine.sse_mape_threshold_jaccard", 0.86, 0.005),
    ("trigonelline condition number ~3600", "panel_trigonelline.condition_number", 3619.2, 30.0),
    ("trigonelline curvature coupling ~-0.84",
     "panel_trigonelline.local_curvature_coupling", -0.839, 0.005),
    ("trigonelline SSE profile flat over ~45% of the grid",
     "panel_trigonelline.profile_fraction_of_log_grid", 0.45, 0.005),
    # Section 4 — transfer skill and the reduced-model ladder
    # Round-7 P0-3: the complete 44-record C/F corpus, 132 named-solute observations. The lookup
    # comparator keeps its own support -- it is undefined on the eight off-grid records.
    ("pooled model MAPE ~8.4%", "transfer_skill.pooled_model_mape", 8.44, 0.02),
    ("pooled comparator MAPE ~8.8%", "transfer_skill.pooled_const_mape", 8.83, 0.02),
    ("pooled lookup MAPE ~10.8% (matched-grid support)",
     "transfer_skill.pooled_lookup_mape", 10.79, 0.02),
    ("paired model-minus-comparator ~-0.394 pp",
     "transfer_skill.paired_model_minus_const_mean_pp", -0.394, 0.005),
    ("model worse than the comparator on 62 points",
     "transfer_skill.n_model_worse_than_const", 62, 0.5),
    ("held-out points = 132", "transfer_skill.n_points", 132, 0.5),
    ("held-out records = 44", "transfer_skill.corpus.n_held_out_records", 44, 0.5),
    ("LOCO pooled held-out MAPE ~6.5%", "loco.pooled_loco_mean_mape", 6.5, 0.05),
    ("LOCO median held-out MAPE ~5.2%", "loco.pooled_loco_median_mape", 5.2, 0.05),
    ("ladder one-constant ~7.1%", "reduced_model_ladder.mean_model0_const", 7.12, 0.03),
    ("ladder per-grind constant ~5.1%",
     "reduced_model_ladder.mean_model1_pergrind_const", 5.05, 0.03),
    ("ladder shared mechanistic ~6.4%",
     "reduced_model_ladder.mean_model2_shared_mech", 6.39, 0.03),
    ("ladder per-grind mechanistic ~4.9%",
     "reduced_model_ladder.mean_model3_pergrind_mech", 4.94, 0.03),
    # Section 5 — sampled aggregate vs actual cup, and rate recovery
    ("sampled aggregate vs cup, caffeine ~27.8%",
     "sampled_aggregate_audit.per_solute.caffeine.mape_vs_actual_cup", 27.8, 0.05),
    ("sampled aggregate vs cup, trigonelline ~38.3%",
     "sampled_aggregate_audit.per_solute.trigonelline.mape_vs_actual_cup", 38.3, 0.05),
    ("sampled aggregate vs cup, 5-CQA ~30.7%",
     "sampled_aggregate_audit.per_solute.5CQA.mape_vs_actual_cup", 30.7, 0.05),
    ("fraction range ratio, caffeine ~9.8x",
     "full_cup_sim.per_solute.caffeine.frac_range_ratio", 9.8, 0.05),
    ("fraction range ratio, trigonelline ~20.3x",
     "full_cup_sim.per_solute.trigonelline.frac_range_ratio", 20.27, 0.05),
    ("fraction range ratio, 5-CQA ~13.2x",
     "full_cup_sim.per_solute.5CQA.frac_range_ratio", 13.15, 0.05),
    ("best rate at the true value in 100% of seeds",
     "full_cup_sim.per_solute.caffeine.frac_best_rate_is_1_frac", 1.0, 0.001),
]


def _get(obj, path):
    """Dotted path, tolerating list indices ("rows.0") and keys containing dots.

    The naive split broke on both. Paper 2 hit the same thing with a per-pressure table keyed
    "11.0", where every cell reported MISSING; one implementation, one behaviour.
    """
    from puckworks.review.number_audit import _get as _shared
    return _shared(obj, path)


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
    """SHA-256 of every direct input the Paper A analyses consume (A4-34/§6.47): the
    source data AND the analysis/plot/build modules + the manuscript, so a changed
    input is detectable."""
    data_files = ["angeloni2023/bioactives.csv", "angeloni2023/inventories.csv",
                  "angeloni2023/total_solids.csv", "schmieder2023/cup_masses.csv",
                  "schmieder2023/rsm_coefficients.csv", "waszkiewicz2025/tds_fractions.csv",
                  "waszkiewicz2025/traces_time_dependent.csv"]
    out = {}
    for rel in data_files:
        p = os.path.join(_DATA, rel)
        out[rel] = _sha256(p) if os.path.exists(p) else "MISSING"
    # code + manuscript inputs (A4-34): the analyses depend on these, not just data
    for rel in ["puckworks/validation/slow/angeloni_bracket.py",
                "puckworks/validation/slow/identifiability.py",
                "puckworks/figures_paper_a.py", "puckworks/paper_a/build.py",
                "docs/PAPER_A_DRAFT.md"]:
        p = os.path.join(_ROOT, rel)
        out[rel] = _sha256(p) if os.path.exists(p) else "MISSING"
    return out


def verify(bundle_path=_BUNDLE, timestamp=None, write_manifest=True, strict=False):
    """Check the manuscript claims against the bundle and write a provenance manifest.
    Returns (ok, failures, manifest). With strict=True (a RELEASE build) a STALE or DIRTY
    tree is ALSO a failure (A4-01/§6.1): a bundle from one commit, a manifest from
    another, and a dirty tree cannot certify the manuscript. `timestamp` is passed in
    (scripts cannot call the clock deterministically)."""
    with open(bundle_path) as f:
        bundle = json.load(f)
    failures = []
    checked = []
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
                            f"(|Δ| {abs(actual - expected):.3f} > tol {tol})")
    # A4-01/§6.1: freshness is a first-class field; a RELEASE build fails on a
    # stale/dirty tree so HEAD == manifest.source_commit == bundle.source_commit.
    head = _git("rev-parse", "HEAD")
    dirty = bool(_git("status", "--porcelain"))
    bundle_commit = bundle.get("source_commit")
    bundle_matches_head = bool(bundle_commit == head and head != "UNKNOWN")
    release_fresh = bool(bundle_matches_head and not dirty)
    if strict and not bundle_matches_head:
        failures.append("RELEASE: bundle source_commit %s != git HEAD %s (stale, A4-01)"
                        % (str(bundle_commit)[:12], str(head)[:12]))
    if strict and dirty:
        failures.append("RELEASE: git tree is dirty -- bundle cannot certify the current "
                        "manuscript (A4-01)")
    manifest = dict(
        paper="A", source_commit=head, git_dirty=dirty, timestamp_utc=timestamp,
        bundle_source_commit=bundle_commit, bundle_matches_head=bundle_matches_head,
        release_fresh=release_fresh,
        bundle_schema_version=bundle.get("schema_version"),
        bundle_sha256=_sha256(bundle_path),
        environment=_env(), data_sha256=_data_hashes(),
        n_claims=len(_CLAIMS), n_failures=len(failures),
        claims=checked, verified=(len(failures) == 0))
    if write_manifest:
        os.makedirs(os.path.dirname(_MANIFEST), exist_ok=True)
        with open(_MANIFEST, "w") as f:
            json.dump(manifest, f, indent=2)
    return (len(failures) == 0), failures, manifest


def main(argv=None):
    import argparse
    p = argparse.ArgumentParser(prog="puckworks.paper_a.build")
    p.add_argument("cmd", choices=["verify", "render", "full", "release"],
                   nargs="?", default="verify")
    p.add_argument("--timestamp", default=None, help="UTC timestamp to stamp the manifest")
    a = p.parse_args(argv)
    if a.cmd == "full":
        from puckworks.figures_paper_a import compute_all
        print("recomputing bundle (slow ~30 min)...")
        compute_all()
    if a.cmd in ("render", "full"):
        from puckworks.figures_paper_a import render_all
        print("rendered:", render_all())
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
        print("VERIFY OK — manuscript headline numbers match the results bundle.")


if __name__ == "__main__":
    main()
