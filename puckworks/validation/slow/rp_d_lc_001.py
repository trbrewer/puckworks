"""RP-D-LC-001 heavy driver — deterministic 3D lateral-coupling virtual fixture.

NOT CI. Minutes to hours of D3Q19 TRT lattice-Boltzmann on CPU. Run by hand or in Colab, per
`puckworks/validation/slow/README.md` and CLAUDE.md rule 3.

    python -m puckworks.validation.slow.rp_d_lc_001 --backend reference --mode arm_a    --output RUNDIR
    python -m puckworks.validation.slow.rp_d_lc_001 --backend reference --mode coupons  --output RUNDIR
    # -> freeze the aperture subset (docs/analysis/rp_d_lc_001/APERTURE_FREEZE.md) BEFORE:
    python -m puckworks.validation.slow.rp_d_lc_001 --backend reference --mode primary  --output RUNDIR
    python -m puckworks.validation.slow.rp_d_lc_001 --mode assemble --output RUNDIR

`--output` should be a gitignored directory: raw stage files are compact but the driver keeps no
field arrays. `--mode assemble` folds the stage files into the committed compact record
`docs/analysis/rp_d_lc_001/runs/run_record.json`, from which the analysis module regenerates the
whole bundle deterministically.

The two-step blinded design of PROTOCOL §9 is enforced structurally: `--mode primary` REFUSES to
run until an aperture-freeze file exists, so no full-fixture R, s or Xi-hat can be inspected
before the aperture list is committed.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import pathlib
import platform
import subprocess
import sys
import time

import numpy as np

from puckworks.analysis import rp_d_lc_virtual_fixture as vf
from puckworks.models.brewer2026 import lb_reference as lbref

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
FREEZE_PATH = REPO_ROOT / vf.BUNDLE_REL / "APERTURE_FREEZE.md"
FREEZE_JSON = REPO_ROOT / vf.BUNDLE_REL / "runs" / "aperture_freeze.json"


# ==========================================================================================
# EXECUTION PROVENANCE — the head that produced the NUMBERS is not the head that assembles them
# ==========================================================================================
#: Each heavy stage was launched from the working tree at the time shown, which the next commit
#: captured. Recovered from process start times (`ps -o lstart`) against `git reflog --date=iso`,
#: not from memory: arm_a started 21:13:49 and 9a4b5e8 was committed 21:14:49; the corrected
#: coupon sweep finished 21:34:13 and its code was committed in 1c10c64 at 21:37:01; primary
#: started 21:37:18, seventeen seconds after 1c10c64. Later commits (7403b27, b4a8327, e2719e0)
#: landed WHILE arm_a and primary were already running, so their workers never saw that code.
EXECUTION_AUTHORITIES = {
    "arm_a": {"commit": "9a4b5e8e45c0780221410b78a306e17b32ba3cda",
              "launched_at": "2026-08-09T21:13:49-05:00",
              "note": "launched from the working tree that 9a4b5e8 captured one minute later"},
    "coupons": {"commit": "1c10c64ed76e07c3273820d3f737adf7654b4681",
                "launched_at": "2026-08-09T21:2x-05:00 (finished 21:34:13)",
                "note": "corrected axis-rotated coupon; code captured by 1c10c64"},
    "primary": {"commit": "1c10c64ed76e07c3273820d3f737adf7654b4681",
                "launched_at": "2026-08-09T21:37:18-05:00",
                "note": "launched 17 s after 1c10c64 was committed"},
}
PROTOCOL_FREEZE_COMMIT = "06c1468d47edb1abd0496f1d7354d68f59986007"

#: Symbols whose behaviour determines the NUMBERS a given stage produced. Assembly, reporting and
#: test symbols are deliberately excluded — changing them cannot move a solver output.
_GEOM_SYMS = ("BASE", "S_SMOKE", "S_COARSE", "S_FINE", "SCIENTIFIC_RESOLUTIONS", "PERTURBATIONS",
              "TAU_PLUS", "TAU_CROSS_CHECK", "G_PRIMARY", "G_LINEARITY", "RTOL", "CHECK",
              "MIN_STEPS", "MAX_STEPS", "_base_is_plenum", "_base_lane_height", "_base_aperture_x",
              "base_mask", "scale", "mirror_x", "swap_paths", "_apply_perturbation",
              "build_fixture", "fixture_meta", "mask_hash", "is_mirror_symmetric", "connectivity",
              "plane_flux", "plane_pressure")
_LB_SYMS = ("solve", "EXPORTABLE_FIELDS", "feq_all", "C", "W", "OPP")
_VF_REL = "puckworks/analysis/rp_d_lc_virtual_fixture.py"
_DRV_REL = "puckworks/validation/slow/rp_d_lc_001.py"
_LB_REL = "puckworks/models/brewer2026/lb_reference.py"
STAGE_EXECUTED_SYMBOLS = {
    "arm_a": {_VF_REL: _GEOM_SYMS,
              _DRV_REL: ("solve", "_mach", "_conductance", "_plenum_obstruction", "_job_channel",
                         "_job_return_path", "_job_linearity", "_job_tau", "_job_ladder",
                         "_job_ladder_at", "arm_a"),
              _LB_REL: _LB_SYMS},
    "coupons": {_VF_REL: _GEOM_SYMS + ("build_axial_coupon", "build_bridge_coupon",
                                       "BRIDGE_COUPON", "APERTURE_CANDIDATES"),
                _DRV_REL: ("solve", "_coupon_conductance", "_job_axial_coupon",
                           "_job_bridge_coupon", "arm_b"),
                _LB_REL: _LB_SYMS},
    "primary": {_VF_REL: _GEOM_SYMS + ("boundary_record_from_fields", "field_truth",
                                       "coupon_truth", "infer_from_boundary", "BOUNDARY_KEYS",
                                       "XI_WINDOW_LO", "XI_WINDOW_HI"),
                _DRV_REL: ("solve", "_mach", "_conductance", "_run_case", "_job_case",
                           "_job_blocked", "arm_cdefghi", "SWAP_RESOLUTIONS"),
                _LB_REL: _LB_SYMS},
}


def _blob(commit, rel):
    r = subprocess.run(("git", "show", "%s:%s" % (commit, rel)), cwd=REPO_ROOT,
                       capture_output=True)
    return r.stdout.decode() if r.returncode == 0 else None


def _symbol_digests(src, names):
    """Docstring- and formatting-insensitive digest of each top-level symbol. A prose change
    cannot move a number, so it must not be reported as one."""
    import ast as _ast
    if src is None:
        return {n: "<file-absent>" for n in names}
    tree = _ast.parse(src)
    found = {}
    for node in tree.body:
        if isinstance(node, (_ast.FunctionDef, _ast.AsyncFunctionDef, _ast.ClassDef)):
            found[node.name] = node
        elif isinstance(node, _ast.Assign):
            for t in node.targets:
                if isinstance(t, _ast.Name):
                    found[t.id] = node

    def norm(node):
        n = _ast.parse(_ast.unparse(node))
        for d in _ast.walk(n):
            if isinstance(d, (_ast.FunctionDef, _ast.AsyncFunctionDef, _ast.ClassDef,
                              _ast.Module)):
                if (d.body and isinstance(d.body[0], _ast.Expr)
                        and isinstance(d.body[0].value, _ast.Constant)
                        and isinstance(d.body[0].value.value, str)):
                    d.body = d.body[1:] or [_ast.Pass()]
        return _ast.unparse(n)

    import hashlib as _h
    return {n: (_h.sha256(norm(found[n]).encode()).hexdigest() if n in found else "<absent>")
            for n in names}


def execution_authority_report():
    """VERIFY, at assembly time, that no symbol a stage actually executed changed after it was
    launched. Intervening commits that touched only assembly, reporting or tests leave the stage's
    numbers valid under its own earlier authority; a change to an executed symbol would require a
    rerun of that stage and is reported as such."""
    head = _git("rev-parse", "HEAD")
    shallow = (_git("rev-parse", "--is-shallow-repository") == "true")
    out = {"assembly_commit": head, "assembly_tree": _git("rev-parse", "HEAD^{tree}"),
           "protocol_freeze_commit": PROTOCOL_FREEZE_COMMIT,
           "history_truncated": bool(shallow), "stages": {}}
    for stage, auth in EXECUTION_AUTHORITIES.items():
        commit = auth["commit"]
        tree = _git("rev-parse", "%s^{tree}" % commit)
        # If the historical objects are absent (shallow clone), every symbol would compare as
        # "<file-absent>" and the report would falsely claim that all three stages need
        # rerunning. Absent evidence is NOT evidence of change: say so instead.
        if shallow or tree is None or _blob(commit, _DRV_REL) is None:
            out["stages"][stage] = {
                **auth, "tree": tree,
                "verification_status": "HISTORY_TRUNCATED_NOT_VERIFIABLE",
                "executed_symbols_changed_since_launch": None,
                "intervening_commits_were_assembly_reporting_or_test_only": None,
                "stage_valid_under_its_own_authority": None,
                "rerun_required": None,
                "note": ("the historical objects for this authority are not present in this "
                         "checkout, so the comparison could not be made; this is an environment "
                         "limit, not a finding about the stage"),
            }
            continue
        changed = {}
        for rel, names in STAGE_EXECUTED_SYMBOLS[stage].items():
            a = _symbol_digests(_blob(commit, rel), names)
            b = _symbol_digests(_blob(head, rel), names)
            diff = [n for n in names if a[n] != b[n]]
            if diff:
                changed[rel] = diff
        out["stages"][stage] = {
            **auth,
            "tree": tree,
            "verification_status": "VERIFIED",
            "driver_sha256": hashlib.sha256(
                (_blob(commit, _DRV_REL) or "").encode()).hexdigest(),
            "analysis_sha256": hashlib.sha256(
                (_blob(commit, _VF_REL) or "").encode()).hexdigest(),
            "lb_reference_sha256": hashlib.sha256(
                (_blob(commit, _LB_REL) or "").encode()).hexdigest(),
            "executed_symbols_changed_since_launch": changed,
            "intervening_commits_were_assembly_reporting_or_test_only": not changed,
            "stage_valid_under_its_own_authority": not changed,
            "rerun_required": bool(changed),
        }
    verdicts = [v["stage_valid_under_its_own_authority"] for v in out["stages"].values()]
    out["all_stages_valid"] = (None if any(v is None for v in verdicts) else all(verdicts))
    return out


# ==========================================================================================
# solver adapters
# ==========================================================================================

#: Process-pool width (`--jobs`). Every LB case in this tranche is INDEPENDENT and deterministic,
#: so running several in separate processes changes nothing but wall time: no shared state, no RNG,
#: no cross-case ordering. Each job must return COMPACT SCALARS ONLY — never a field array — both
#: to keep pickling cheap and because `_json_default` refuses to serialise an ndarray.
_JOBS = 1

#: Path-swap control resolutions. Declared BEFORE execution (nothing full-fixture had been
#: inspected) and equal to the full scientific set unless compute forces otherwise.
SWAP_RESOLUTIONS = vf.SCIENTIFIC_RESOLUTIONS


def _pmap(fn, specs):
    """Map a module-level job function over specs, in order, optionally across processes."""
    if _JOBS <= 1 or len(specs) <= 1:
        return [fn(s) for s in specs]
    from concurrent.futures import ProcessPoolExecutor
    with ProcessPoolExecutor(max_workers=min(_JOBS, len(specs))) as ex:
        return list(ex.map(fn, specs))          # ex.map preserves input order


def solve(mask, g, backend="reference", tau=None, fields=("rho", "uy"), steps=None, **kw):
    """Run one LB solve. `steps`, when given, FORCES exactly that many iterations (no early
    break) — used only by the convergence ladder in Arm A."""
    tau = vf.TAU_PLUS if tau is None else tau
    args = dict(g=g, tau_plus=tau, verbose=False, return_fields=tuple(fields))
    if steps is not None:
        args.update(max_steps=steps, check=10 ** 9, rtol=1e-30, min_steps=10 ** 9)
    else:
        args.update(max_steps=vf.MAX_STEPS, check=vf.CHECK, rtol=vf.RTOL, min_steps=vf.MIN_STEPS)
    args.update(kw)
    if backend == "reference":
        return lbref.solve(mask, **args)
    if backend == "taichi":
        from puckworks.models.brewer2026 import lb_taichi as lbti
        if lbti.ti is None:
            raise RuntimeError("taichi backend requested but taichi is not installed")
        raise NotImplementedError(
            "the taichi port asserts cubic domains and exports ux only; it cannot run this "
            "fixture without a port of the additive field instrumentation. Recorded as a "
            "limitation (PROTOCOL §11.8), not silently substituted.")
    raise ValueError("unknown backend %r" % (backend,))


def _mach(res, mask):
    u2 = np.zeros(mask.shape)
    for k in ("ux", "uy", "uz"):
        if k in res:
            u2 = u2 + np.where(mask, 0.0, res[k]) ** 2
    umax = float(np.sqrt(u2).max())
    return umax, umax * 3.0 ** 0.5


def _conductance(res, mask, meta, g):
    pin, pin_sd, _ = vf.plane_pressure(res["rho"], mask, meta["x_node_in"], g)
    pout, pout_sd, _ = vf.plane_pressure(res["rho"], mask, meta["x_node_out"], g)
    q1 = vf.plane_flux(res["ux"], mask, meta["x_meas_a"], meta["lane1_y"])
    q2 = vf.plane_flux(res["ux"], mask, meta["x_meas_a"], meta["lane2_y"])
    dP = pin - pout
    return {"dP": dP, "Q": q1 + q2, "q1": q1, "q2": q2, "C": (q1 + q2) / dP,
            "s": q1 / (q1 + q2), "p_in_sd": pin_sd, "p_out_sd": pout_sd,
            "steps": int(res["steps"]), "converged": bool(res["steps"] < vf.MAX_STEPS)}


# ==========================================================================================
# ARM A — solver, boundary and topology verification
# ==========================================================================================

def _plenum_obstruction(mask, S):
    """Adjudication probe (BOUNDARY_TOPOLOGY_ADJUDICATION.md §3): raise the RETURN PATH's
    resistance without touching a single lane voxel, by plugging the lower half of the common
    plenum's cross-section at the wrap plane x = 0. Preserves both fixture symmetries. If the
    NOTE (erratum E1): the frozen control asked whether Q/dP ITSELF is invariant to this. It is
    NOT — the probe sits ~2 base voxels from the inlet node plane in a 7-base-voxel plenum, so it
    perturbs the lane entrance, which is inside the measured sub-network. What Arm J gates on is
    the COMMON-MODE cancellation in the ratio R (and in the outlet share s), at both scientific
    resolutions and for every frozen aperture."""
    out = mask.copy()
    z0 = vf.BASE["z_lo"] * S
    z1 = (vf.BASE["z_lo"] + vf.BASE["h_low"]) * S
    out[0, :, z0:z1] = True
    return out


# ---- module-level job functions: one LB case each, compact scalars out ----------------------

def _job_channel(spec):
    r = lbref.channel_verification(Nz=spec["Nz"], N=4, g=1e-6, tau_plus=spec["tau_plus"],
                                   max_steps=40000, check=200, rtol=1e-9)
    return {**spec, "err_pct": r["err_pct"], "steps": r["steps"], "converged": r["converged"]}


def _job_return_path(spec):
    S = vf.S_COARSE
    base, meta = vf.build_fixture(S, aperture=spec["aperture"])
    mask = _plenum_obstruction(base, S) if spec["tag"] == "obstructed_return" else base
    r = solve(mask, vf.G_PRIMARY, spec["backend"])
    return {**spec, **_conductance(r, mask, meta, vf.G_PRIMARY)}


def _job_linearity(spec):
    mask, meta = vf.build_fixture(spec["S"], aperture={"kx": 5, "kz": 2})
    g = vf.G_PRIMARY * spec["g_factor"]
    r = solve(mask, g, spec["backend"], fields=("rho", "uy", "uz"))
    c = _conductance(r, mask, meta, g)
    umax, ma = _mach(r, mask)
    out = {**spec, "g": g, "C": c["C"], "s": c["s"], "u_max": umax, "mach": ma,
           "steps": c["steps"], "converged": c["converged"]}
    if spec["g_factor"] == 1.0:
        fl = np.array([vf.plane_flux(r["ux"], mask, x)
                       for x in range(meta["lane_x"][0], meta["lane_x"][1])])
        out["mass"] = {"S": spec["S"], "plane_mean": float(fl.mean()),
                       "plane_ptp_rel": float(np.ptp(fl) / fl.mean()),
                       "inlet_plane": float(fl[0]), "outlet_plane": float(fl[-1]),
                       "inlet_outlet_rel_diff": float(fl[-1] / fl[0] - 1.0)}
    return out


def _job_tau(spec):
    mask, meta = vf.build_fixture(vf.S_COARSE, aperture={"kx": 5, "kz": 2})
    g = vf.G_PRIMARY * ((spec["tau_plus"] - 0.5) / (vf.TAU_PLUS - 0.5))   # hold u ~ g/nu fixed
    r = solve(mask, g, spec["backend"], tau=spec["tau_plus"])
    c = _conductance(r, mask, meta, g)
    return {"tau_plus": spec["tau_plus"], "g": g, "C": c["C"], "s": c["s"], "steps": c["steps"]}


def _job_ladder(spec):
    mask, meta = vf.build_fixture(vf.S_COARSE, aperture={"kx": 5, "kz": 2})
    r = solve(mask, vf.G_PRIMARY, spec["backend"], steps=spec["forced_steps"])
    c = _conductance(r, mask, meta, vf.G_PRIMARY)
    return {"S": vf.S_COARSE, "forced_steps": spec["forced_steps"], "C": c["C"], "s": c["s"]}


def _job_ladder_at(spec):
    """Forced-step run at an arbitrary resolution (the A6b audit); A6's ladder is S_COARSE only."""
    mask, meta = vf.build_fixture(spec["S"], aperture={"kx": 5, "kz": 2})
    r = solve(mask, vf.G_PRIMARY, spec["backend"], steps=spec["forced_steps"])
    c = _conductance(r, mask, meta, vf.G_PRIMARY)
    return {"S": spec["S"], "forced_steps": spec["forced_steps"], "C": c["C"], "s": c["s"]}


def _job_axial_coupon(spec):
    mask, meta = vf.build_axial_coupon(spec["S"], spec["level"], spec["orientation"])
    c = _coupon_conductance(mask, meta, vf.G_PRIMARY, spec["backend"])
    return {**{k: spec[k] for k in ("S", "level", "orientation")},
            "mask_sha256": meta["mask_sha256"], **c}


def _job_bridge_coupon(spec):
    mask, meta = vf.build_bridge_coupon(spec["S"], spec["kx"], spec["kz"])
    c = _coupon_conductance(mask, meta, vf.G_PRIMARY, spec["backend"],
                            node_in=meta["x_node_in"], node_out=meta["x_node_out"])
    return {"S": spec["S"], "kx": spec["kx"], "kz": spec["kz"],
            "mask_sha256": meta["mask_sha256"], **c}


def _job_blocked(spec):
    S, backend = spec["S"], spec["backend"]
    mb, meta = vf.build_fixture(S, aperture=None)
    r = solve(mb, vf.G_PRIMARY, backend, fields=("rho", "uy", "uz"))
    c = _conductance(r, mb, meta, vf.G_PRIMARY)
    pin, pin_sd, _ = vf.plane_pressure(r["rho"], mb, meta["x_node_in"], vf.G_PRIMARY)
    pout, pout_sd, _ = vf.plane_pressure(r["rho"], mb, meta["x_node_out"], vf.G_PRIMARY)
    offs = {}
    for d in meta["node_offsets"]:
        pi, _, _ = vf.plane_pressure(r["rho"], mb, meta["x_node_in"] - d, vf.G_PRIMARY)
        po, _, _ = vf.plane_pressure(r["rho"], mb, meta["x_node_out"] + d, vf.G_PRIMARY)
        offs["offset_%d" % d] = {"dP": pi - po, "C": c["Q"] / (pi - po),
                                 "C_rel_change": (c["Q"] / (pi - po)) / c["C"] - 1.0}
    return {"S": S, "mask_sha256": meta["mask_sha256"], **c, "blocked_share": c["s"],
            "node_in_sd_over_dP": pin_sd / (pin - pout),
            "node_out_sd_over_dP": pout_sd / (pin - pout),
            "node_surface_sensitivity": offs}


def _job_case(spec):
    return _run_case(spec["S"], spec["aperture"], spec["backend"],
                     variant=spec.get("variant", "mirror"), swapped=spec.get("swapped", False),
                     perturbation=spec.get("perturbation"), g=spec.get("g"),
                     label=spec.get("label", "primary"))


def arm_a(backend, out_dir, log):
    rec = {}
    # --- A1 canonical plane channel + tau independence + the discretisation law -------------
    ch = _pmap(_job_channel, [{"Nz": 33, "tau_plus": t}
                              for t in (vf.TAU_CROSS_CHECK, vf.TAU_PLUS, 3.0)])
    for c in ch:
        log("A1 channel tau=%.1f err=%+.5f%% steps=%d" % (c["tau_plus"], c["err_pct"], c["steps"]))
    lad_raw = _pmap(_job_channel, [{"Nz": n, "tau_plus": vf.TAU_PLUS}
                                   for n in (5, 7, 9, 13, 17, 25, 33)])
    ladder = []
    for c in lad_raw:
        h = c["Nz"] - 2
        ladder.append({"h_lu": h, "err_pct": c["err_pct"], "law_50_over_h2_pct": 50.0 / h ** 2})
        log("A1 ladder h=%2d err=%+.4f%%" % (h, c["err_pct"]))
    rec["channel"] = {"tau_independence": ch, "resolution_ladder": ladder,
                      "err_law_pct": vf.CHANNEL_ERR_LAW_PCT}
    rec["tau_independence_max_spread_pct"] = max(c["err_pct"] for c in ch) - min(
        c["err_pct"] for c in ch)

    # --- A2 topology: connectivity, mirror exactness, no periodic lateral bypass ------------
    topo = []
    for S in vf.SCIENTIFIC_RESOLUTIONS:
        for ap in (None, {"kx": 5, "kz": 2}):
            m, meta = vf.build_fixture(S, aperture=ap)
            conn = vf.connectivity(m, meta)
            topo.append({"S": S, "aperture": ap, "mask_sha256": meta["mask_sha256"],
                         "mirror_exact": vf.is_mirror_symmetric(m, S), **conn})
    rec["topology"] = topo
    log("A2 topology: %d configurations checked" % len(topo))

    # --- A3 return-path invariance: the decisive Route-A demonstration ----------------------
    specs = [{"aperture": ap, "tag": t, "backend": backend}
             for ap in (None, {"kx": 5, "kz": 2})
             for t in ("nominal", "obstructed_return")]
    got = _pmap(_job_return_path, specs)
    ret = []
    for ap in (None, {"kx": 5, "kz": 2}):
        row = {"aperture": ap}
        for t in ("nominal", "obstructed_return"):
            c = next(x for x in got if x["aperture"] == ap and x["tag"] == t)
            row[t] = {k: c[k] for k in ("dP", "Q", "q1", "q2", "C", "s", "steps", "converged")}
            log("A3 %-18s ap=%s dP=%.6e C=%.9f steps=%d" % (t, ap, c["dP"], c["C"], c["steps"]))
        row["dP_change_rel"] = row["obstructed_return"]["dP"] / row["nominal"]["dP"] - 1.0
        row["C_change_rel"] = row["obstructed_return"]["C"] / row["nominal"]["C"] - 1.0
        row["s_change_abs"] = row["obstructed_return"]["s"] - row["nominal"]["s"]
        ret.append(row)
    rec["return_path_invariance"] = ret

    # --- A4 low-Mach linearity, mass conservation, plane invariance -------------------------
    got = _pmap(_job_linearity, [{"S": S, "g_factor": f, "backend": backend}
                                 for S in vf.SCIENTIFIC_RESOLUTIONS
                                 for f in (vf.G_LINEARITY[0], 1.0, vf.G_LINEARITY[1])])
    lin, mass = [], []
    for r in got:
        mass_row = r.pop("mass", None)
        r.pop("backend", None)
        lin.append(r)
        if mass_row:
            mass.append(mass_row)
        log("A4 S=%d g x%.1f C=%.9f Ma=%.2e steps=%d"
            % (r["S"], r["g_factor"], r["C"], r["mach"], r["steps"]))
    rec["linearity"] = lin
    rec["mass_conservation"] = mass

    # --- A5 tau independence on the ASSEMBLED fixture ---------------------------------------
    tau_rows = _pmap(_job_tau, [{"tau_plus": t, "backend": backend}
                                for t in (vf.TAU_PLUS, vf.TAU_CROSS_CHECK)])
    for r in tau_rows:
        log("A5 fixture tau=%.1f C=%.9f s=%.9f steps=%d"
            % (r["tau_plus"], r["C"], r["s"], r["steps"]))
    rec["tau_independence_fixture"] = {
        "rows": tau_rows,
        "C_rel_spread": abs(tau_rows[1]["C"] / tau_rows[0]["C"] - 1.0),
        "s_abs_spread": abs(tau_rows[1]["s"] - tau_rows[0]["s"])}

    # --- A6 convergence ladder (forced step counts) -----------------------------------------
    lad = _pmap(_job_ladder, [{"forced_steps": n, "backend": backend}
                              for n in (1000, 2000, 4000, 8000)])
    for r in lad:
        log("A6 forced steps=%d C=%.9f s=%.9f" % (r["forced_steps"], r["C"], r["s"]))
    rec["convergence_ladder"] = lad

    # --- A6b forced-step convergence audit: does stopping at rtol actually stop late enough? ---
    audit = []
    for S in vf.SCIENTIFIC_RESOLUTIONS:
        conv = _job_linearity({"S": S, "g_factor": 1.0, "backend": backend})
        n = int(conv["steps"])
        longer = _job_ladder_at({"S": S, "forced_steps": int(n * vf.CONVERGENCE_AUDIT_FACTOR),
                                 "backend": backend})
        audit.append({"S": S, "converged_steps": n,
                      "audit_steps": longer["forced_steps"],
                      "C_converged": conv["C"], "C_audit": longer["C"],
                      "s_converged": conv["s"], "s_audit": longer["s"],
                      "C_rel_change": longer["C"] / conv["C"] - 1.0,
                      "s_abs_change": longer["s"] - conv["s"],
                      "within_tolerance": bool(
                          abs(longer["C"] / conv["C"] - 1.0) <= vf.TOL_CONVERGENCE_REL
                          and abs(longer["s"] - conv["s"]) <= vf.TOL_CONVERGENCE_REL)})
        log("A6b audit S=%d converged@%d vs forced@%d  dC=%.2e ds=%.2e  %s"
            % (S, n, longer["forced_steps"], audit[-1]["C_rel_change"],
               audit[-1]["s_abs_change"], "OK" if audit[-1]["within_tolerance"] else "FAIL"))
    rec["convergence_audit"] = audit

    # --- A7 backend cross-check ---------------------------------------------------------
    try:
        from puckworks.models.brewer2026 import lb_taichi as lbti
        available = lbti.ti is not None
    except Exception:
        available = False
    rec["backend_cross_check"] = {
        "taichi_available": bool(available),
        "status": "SKIPPED_TAICHI_UNAVAILABLE" if not available else "SKIPPED_CUBIC_ONLY_PORT",
        "limitation": ("The taichi port asserts cubic domains and exports ux only; this fixture "
                       "is non-cubic and needs rho/uy. The NumPy reference result is retained "
                       "and the cross-check is recorded as NOT PERFORMED, never as passed."),
    }
    _dump(out_dir / "arm_a.json", rec)
    return rec


# ==========================================================================================
# ARM B — component calibration (coupons). Runs BEFORE the aperture freeze.
# ==========================================================================================

def _coupon_conductance(mask, meta, g, backend, node_in=None, node_out=None):
    r = solve(mask, g, backend, fields=("rho",))
    axis_len = mask.shape[0]
    if node_in is None:
        # A uniform periodic duct is FULLY DEVELOPED everywhere: mu*lap(u) = -g pointwise, so the
        # periodic part of the pressure is constant and dP = g*L exactly. That makes this coupon
        # the falsification test of the frozen pressure definition p = rho/3 - g*x promised in
        # BOUNDARY_TOPOLOGY_ADJUDICATION.md section 2 — if the density is NOT uniform here, the
        # definition is not physically coherent and the tranche stops as INVALID_EXECUTION.
        q = vf.plane_flux(r["ux"], mask, axis_len // 2)
        dP = g * axis_len
        pin = pout = float("nan")
        rho_f = r["rho"][~mask]
        planes = np.array([vf.plane_pressure(r["rho"], mask, x, g)[0] for x in range(axis_len)])
        return {"Q": q, "dP": dP, "G": q / dP, "steps": int(r["steps"]),
                "converged": bool(r["steps"] < vf.MAX_STEPS),
                "rho_fluid_mean": float(rho_f.mean()),
                "rho_fluid_ptp_rel": float(np.ptp(rho_f) / rho_f.mean()),
                # the periodic pressure part must be flat along the duct; report it, do not assume
                "periodic_pressure_ptp_over_dP": float(np.ptp(planes + g * np.arange(axis_len))
                                                       / dP)}
    else:
        q = vf.plane_flux(r["ux"], mask, (node_in + node_out) // 2)
        pin, _, _ = vf.plane_pressure(r["rho"], mask, node_in, g)
        pout, _, _ = vf.plane_pressure(r["rho"], mask, node_out, g)
        dP = pin - pout
    return {"Q": q, "dP": dP, "G": q / dP, "steps": int(r["steps"]),
            "converged": bool(r["steps"] < vf.MAX_STEPS)}


def arm_b(backend, out_dir, log):
    rec = {"axial": [], "bridge": []}
    rec["axial"] = _pmap(_job_axial_coupon,
                         [{"S": S, "level": lv, "orientation": o, "backend": backend}
                          for S in vf.SCIENTIFIC_RESOLUTIONS
                          for lv in ("high", "low") for o in ("x", "y")])
    for c in rec["axial"]:
        log("B axial S=%d %-4s orient=%s G=%.6f steps=%d rho_ptp=%.2e"
            % (c["S"], c["level"], c["orientation"], c["G"], c["steps"],
               c.get("rho_fluid_ptp_rel", float("nan"))))
    rec["bridge"] = _pmap(_job_bridge_coupon,
                          [{"S": S, "backend": backend, **cand}
                           for S in vf.SCIENTIFIC_RESOLUTIONS
                           for cand in vf.APERTURE_CANDIDATES])
    for c in rec["bridge"]:
        log("B bridge S=%d kx=%d kz=%d G=%.6f steps=%d"
            % (c["S"], c["kx"], c["kz"], c["G"], c["steps"]))
    # coupon-predicted Xi for every candidate, at the coarse resolution (selection basis)
    pred = {}
    for S in vf.SCIENTIFIC_RESOLUTIONS:
        a = next(r["G"] for r in rec["axial"] if r["S"] == S and r["level"] == "high"
                 and r["orientation"] == "x")
        b = next(r["G"] for r in rec["axial"] if r["S"] == S and r["level"] == "low"
                 and r["orientation"] == "x")
        pred[str(S)] = {"a_coupon": a, "b_coupon": b,
                        "c_coupon": (a - b) / (a + b),
                        "rows": [{**{k: r[k] for k in ("kx", "kz")},
                                  "G_bridge": r["G"],
                                  "Xi_coupon": r["G"] * (2.0 / (a + b))}
                                 for r in rec["bridge"] if r["S"] == S]}
    rec["coupon_prediction"] = pred
    _dump(out_dir / "arm_b.json", rec)
    return rec


# ==========================================================================================
# ARMS C..I — full fixture. Requires the committed aperture freeze.
# ==========================================================================================

def _run_case(S, aperture, backend, variant="mirror", swapped=False, perturbation=None,
              g=None, label=""):
    """One (blocked, open) fixture pair -> boundary record, blind inference, then field truth.

    ORDER IS LOAD-BEARING (PROTOCOL §6): the boundary record is built and the inverse is called
    and recorded BEFORE `field_truth` is evaluated. The inverse never sees a truth quantity."""
    g = vf.G_PRIMARY if g is None else g
    mo, meta_o = vf.build_fixture(S, aperture=aperture, variant=variant, swapped=swapped,
                                  perturbation=perturbation)
    mb, meta_b = vf.build_fixture(S, aperture=None, variant=variant, swapped=swapped,
                                  perturbation=perturbation)
    t0 = time.time()
    ro = solve(mo, g, backend, fields=("rho", "uy", "uz"))
    rb = solve(mb, g, backend, fields=("rho", "uy", "uz"))
    bnd = vf.boundary_record_from_fields(ro, rb, mo, mb, meta_o, g)

    # ---- BLIND INFERENCE FIRST -----------------------------------------------------------
    inf = vf.infer_from_boundary({
        "Q0": bnd["blocked"]["Q"], "dP0": bnd["blocked"]["dP"],
        "q1": bnd["open"]["q1"], "q2": bnd["open"]["q2"], "dP": bnd["open"]["dP"],
        "orientation": "swapped" if swapped else "nominal",
        "converged": bnd["open"]["converged"] and bnd["blocked"]["converged"]})

    # ---- ONLY NOW the independent truth --------------------------------------------------
    truth = vf.field_truth(ro, rb, mo, mb, meta_o, g)
    umax_o, ma_o = _mach(ro, mo)
    umax_b, ma_b = _mach(rb, mb)
    fl_o = np.array([vf.plane_flux(ro["ux"], mo, x)
                     for x in range(meta_o["lane_x"][0], meta_o["lane_x"][1])])
    s_b = (bnd["open"]["q1_plane_b"] / (bnd["open"]["q1_plane_b"] + bnd["open"]["q2_plane_b"]))
    row = {
        "role": label or "primary", "S": S, "aperture": aperture, "variant": variant,
        "swapped": bool(swapped), "perturbation": perturbation, "g": g,
        "mask_sha256_open": meta_o["mask_sha256"], "mask_sha256_blocked": meta_b["mask_sha256"],
        "mirror_exact_open": vf.is_mirror_symmetric(mo, S),
        "boundary": {"R": inf["R"], "s": inf["s"],
                     "dP_ratio_open_over_blocked": inf["dP_ratio_open_over_blocked"],
                     **{k: bnd["open"][k] for k in ("Q", "q1", "q2", "dP", "steps", "converged")},
                     "Q0": bnd["blocked"]["Q"], "dP0": bnd["blocked"]["dP"],
                     "q1_0": bnd["blocked"]["q1"], "q2_0": bnd["blocked"]["q2"],
                     "blocked_share": bnd["blocked"]["q1"] / bnd["blocked"]["Q"],
                     "steps_blocked": bnd["blocked"]["steps"],
                     "converged_blocked": bnd["blocked"]["converged"],
                     "s_plane_b": s_b, "s_plane_delta": s_b - inf["s"]},
        "inference": {k: inf[k] for k in ("status", "c_hat", "t_hat", "Xi_hat")},
        "truth": truth,
        "numerics": {"u_max_open": umax_o, "mach_open": ma_o, "u_max_blocked": umax_b,
                     "mach_blocked": ma_b,
                     "plane_flux_ptp_rel": float(np.ptp(fl_o) / fl_o.mean()),
                     "seconds": round(time.time() - t0, 1)},
    }
    return row


def _case_line(row):
    inf, truth = row["inference"], row["truth"]
    return ("  %-14s S=%d ap=%s%s%s R=%.6f s=%.6f Xi_field=%.4f Xi_hat=%s [%s] %.0fs"
            % (row["role"], row["S"], row["aperture"],
               " swapped" if row["swapped"] else "",
               (" " + row["perturbation"]) if row["perturbation"] else "",
               row["boundary"]["R"], row["boundary"]["s"], truth["Xi_field"],
               ("%.4f" % inf["Xi_hat"]) if inf["Xi_hat"] else "-",
               inf["status"], row["numerics"]["seconds"]))


#: PROTOCOL §9 step 1, made ALGORITHMIC so the selection is not a judgement call. Declared before
#: the coupon sweep was run, and it reads coupon output ONLY — never a full-fixture observable.
FREEZE_RULE = (
    "From the coupon-predicted Xi at S_COARSE, over candidates with kz >= 2 (kz = 1 is a "
    "2-lattice-unit feature at S_COARSE, ~12 % element error under the measured 50/h^2 law): "
    "take the candidate with the LARGEST Xi_coupon strictly below XI_WINDOW_LO; the candidate "
    "with the SMALLEST Xi_coupon strictly above XI_WINDOW_HI; and, inside the window, the "
    "candidates nearest to three log-spaced targets between XI_WINDOW_LO and XI_WINDOW_HI "
    "(geometric quartiles), deduplicated. Ties break on smaller kx then smaller kz. Selection is "
    "sorted by Xi_coupon ascending."
)


def freeze_apertures(out_dir, log):
    """Apply FREEZE_RULE to the coupon output and write the aperture freeze. Refuses to overwrite
    an existing freeze, so a second pass cannot quietly re-select after seeing anything."""
    if FREEZE_JSON.exists():
        raise SystemExit("aperture freeze already exists at %s — refusing to re-select"
                         % FREEZE_JSON)
    b = json.loads((out_dir / "arm_b.json").read_text())
    pred = b["coupon_prediction"][str(vf.S_COARSE)]
    rows = [r for r in pred["rows"] if r["kz"] >= 2]
    rows.sort(key=lambda r: (r["Xi_coupon"], r["kx"], r["kz"]))
    lo, hi = vf.XI_WINDOW_LO, vf.XI_WINDOW_HI

    below = [r for r in rows if r["Xi_coupon"] < lo]
    above = [r for r in rows if r["Xi_coupon"] > hi]
    inside = [r for r in rows if lo <= r["Xi_coupon"] <= hi]
    picked, reasons = [], {}

    def take(r, why):
        key = (r["kx"], r["kz"])
        if r is not None and key not in reasons:
            reasons[key] = why
            picked.append(r)

    if below:
        take(below[-1], "largest coupon-predicted Xi strictly BELOW the window")
    targets = [lo * (hi / lo) ** f for f in (0.25, 0.5, 0.75)]
    for i, t in enumerate(targets):
        if inside:
            r = min(inside, key=lambda r: (abs(math.log(r["Xi_coupon"] / t)), r["kx"], r["kz"]))
            take(r, "nearest coupon-predicted Xi to log-target %d (%.4f) INSIDE the window"
                 % (i + 1, t))
    if above:
        take(above[0], "smallest coupon-predicted Xi strictly ABOVE the window")
    picked.sort(key=lambda r: r["Xi_coupon"])

    doc = {
        "rule": FREEZE_RULE,
        "selected_from": "coupon output only (arm_b.json); NO full-fixture observable was read",
        "window": {"lo": lo, "hi": hi, "provenance": vf.XI_WINDOW_PROVENANCE},
        "excluded_kz1": True,
        "n_candidates_considered": len(rows),
        "selected": [{"kx": r["kx"], "kz": r["kz"]} for r in picked],
        "coupon_predicted": [{"kx": r["kx"], "kz": r["kz"], "Xi_coupon": r["Xi_coupon"],
                              "G_bridge": r["G_bridge"],
                              "reason": reasons[(r["kx"], r["kz"])]} for r in picked],
        "a_coupon": pred["a_coupon"], "b_coupon": pred["b_coupon"],
        "c_coupon": pred["c_coupon"],
        "n_predicted_in_window": sum(1 for r in picked if lo <= r["Xi_coupon"] <= hi),
        "all_candidate_predictions": [
            {"kx": r["kx"], "kz": r["kz"], "Xi_coupon": r["Xi_coupon"]} for r in rows],
    }
    _dump(FREEZE_JSON, doc)
    lines = [
        "# RP-D-LC-001 — APERTURE FREEZE (step 2 of the blinded design)", "",
        "```", "SELECTED FROM COUPON OUTPUT ONLY",
        "NO FULL-FIXTURE R, s OR Xi-hat WAS INSPECTED BEFORE THIS FILE WAS COMMITTED", "```", "",
        "The rule below was declared in the driver before the coupon sweep ran and is applied",
        "mechanically; the driver refuses to re-select once this file exists, and refuses to run",
        "`--mode primary` until it does.", "",
        "## Rule", "", "> " + FREEZE_RULE, "",
        "## Coupon calibration (S = %d)" % vf.S_COARSE, "",
        "| quantity | value |", "|---|---|",
        "| `a_coupon` (high segment) | %.6f |" % pred["a_coupon"],
        "| `b_coupon` (low segment) | %.6f |" % pred["b_coupon"],
        "| `c_coupon` | %.6f |" % pred["c_coupon"],
        "| window | %.6f … %.6f |" % (lo, hi), "",
        "## Selected apertures", "",
        "| kx | kz | `G_bridge_coupon` | `Xi_coupon` | in window | why |",
        "|---|---|---|---|---|---|",
    ]
    for r in picked:
        lines.append("| %d | %d | %.6f | %.6f | %s | %s |"
                     % (r["kx"], r["kz"], r["G_bridge"], r["Xi_coupon"],
                        "yes" if lo <= r["Xi_coupon"] <= hi else "no",
                        reasons[(r["kx"], r["kz"])]))
    lines += ["", "Coupon-predicted cases inside the window: **%d**."
              % doc["n_predicted_in_window"], "",
              "If the assembled fixture then misses the target, the disposition is",
              "`DESIGN_MISSED_TARGET` — a second post-hoc aperture set is **not** selected in",
              "this frozen execution.", "",
              "## All candidates considered (kz >= 2)", "",
              "| kx | kz | `Xi_coupon` |", "|---|---|---|"]
    for r in rows:
        lines.append("| %d | %d | %.6f |" % (r["kx"], r["kz"], r["Xi_coupon"]))
    FREEZE_PATH.write_text("\n".join(lines) + "\n")
    log("froze %d apertures (%d coupon-predicted inside the window) -> %s"
        % (len(picked), doc["n_predicted_in_window"], FREEZE_PATH))
    return doc


def load_freeze():
    if not FREEZE_JSON.exists():
        raise SystemExit(
            "REFUSING to run the full fixture: no aperture freeze at %s.\n"
            "PROTOCOL §9 requires the aperture subset to be selected from COUPON output only "
            "and committed BEFORE any open-fixture R, s or Xi-hat is inspected.\n"
            "Run `--mode coupons`, write the freeze, commit it, then re-run." % FREEZE_JSON)
    return json.loads(FREEZE_JSON.read_text())


def arm_cdefghi(backend, out_dir, log):
    freeze = load_freeze()
    selected = [dict(a) for a in freeze["selected"]]
    rec = {"aperture_freeze": freeze, "cases": [], "path_swap": [], "blocked": [],
           "identical_path_control": None, "asymmetry": [], "grid_refinement": {}}

    # --- ARM C: blocked full fixture (also recorded standalone) -----------------------------
    rec["blocked"] = _pmap(_job_blocked, [{"S": S, "backend": backend}
                                          for S in vf.SCIENTIFIC_RESOLUTIONS])
    for c in rec["blocked"]:
        log("C blocked S=%d C=%.9f share=%.9f dP=%.6e steps=%d"
            % (c["S"], c["C"], c["s"], c["dP"], c["steps"]))

    # --- ARMS D+E (open + blind inversion), G (path swap), H (identical path) and I
    #     (adversarial asymmetry) are all INDEPENDENT deterministic cases, so they are
    #     dispatched as ONE batch to maximise pool occupancy. Ordering of the output list is
    #     preserved by _pmap, so the record is identical to a serial run.
    ap_mid = selected[len(selected) // 2]
    specs = []
    for S in vf.SCIENTIFIC_RESOLUTIONS:
        for ap in selected:
            specs.append({"S": S, "aperture": ap, "backend": backend, "label": "primary"})
    for S in SWAP_RESOLUTIONS:
        for ap in selected:
            specs.append({"S": S, "aperture": ap, "backend": backend, "swapped": True,
                          "label": "path_swap"})
    specs.append({"S": vf.S_COARSE, "aperture": ap_mid, "backend": backend,
                  "variant": "identical", "label": "identical_path"})
    # R-linearity: Arm A measures the forcing dependence of the CONDUCTANCE C, but the tranche's
    # observable is the RATIO R, in which a common-mode O(Re) drift cancels. Added here BEFORE the
    # primary arm runs (the freeze is committed; this reuses a frozen aperture and invents nothing)
    # so the linearity control can be evaluated on the quantity the decision actually uses.
    for S in vf.SCIENTIFIC_RESOLUTIONS:
        for f in vf.G_LINEARITY:
            specs.append({"S": S, "aperture": ap_mid, "backend": backend,
                          "g": vf.G_PRIMARY * f, "label": "linearity_R"})
    for name in vf.PERTURBATIONS:
        specs.append({"S": vf.S_FINE, "aperture": ap_mid, "backend": backend,
                      "perturbation": name, "label": "asymmetry"})
        specs.append({"S": vf.S_FINE, "aperture": ap_mid, "backend": backend,
                      "perturbation": name, "swapped": True, "label": "asymmetry_swap"})
    log("dispatching %d full-fixture cases across %d worker(s)" % (len(specs), _JOBS))
    rows = _pmap(_job_case, specs)
    for r in rows:
        log(_case_line(r))
    rec["cases"] = list(rows)

    def _find(label, S, ap, swapped=False, perturbation=None):
        return next(r for r in rows if r["role"] == label and r["S"] == S
                    and r["aperture"] == ap and r["swapped"] == swapped
                    and r["perturbation"] == perturbation)

    # --- ARM G: exact path-swap control ----------------------------------------------------
    for S in SWAP_RESOLUTIONS:
        for ap in selected:
            base = _find("primary", S, ap)
            sw = _find("path_swap", S, ap, swapped=True)
            row = {
                "S": S, "aperture": ap,
                "R": base["boundary"]["R"], "R_swap": sw["boundary"]["R"],
                "s": base["boundary"]["s"], "s_swap": sw["boundary"]["s"],
                "c_field": base["truth"]["c_field"], "c_field_swap": sw["truth"]["c_field"],
                "c_hat": base["inference"]["c_hat"], "c_hat_swap": sw["inference"]["c_hat"],
                "Xi_field": base["truth"]["Xi_field"], "Xi_field_swap": sw["truth"]["Xi_field"],
                "Xi_hat": base["inference"]["Xi_hat"], "Xi_hat_swap": sw["inference"]["Xi_hat"],
            }
            row["share_sign_reversed"] = bool(
                (row["s"] - 0.5) * (row["s_swap"] - 0.5) < 0
                and abs(abs(row["s"] - 0.5) - abs(row["s_swap"] - 0.5))
                <= vf.TOL_SWAP_R_REL * abs(row["s"] - 0.5) + 1e-12)
            row["c_sign_reversed"] = bool(
                row["c_hat"] is not None and row["c_hat_swap"] is not None
                and row["c_hat"] * row["c_hat_swap"] < 0
                and row["c_field"] * row["c_field_swap"] < 0)
            row["R_preserved"] = bool(abs(row["R_swap"] / row["R"] - 1.0) <= vf.TOL_SWAP_R_REL)
            row["Xi_field_preserved"] = bool(
                abs(row["Xi_field_swap"] / row["Xi_field"] - 1.0) <= vf.TOL_SWAP_XI_REL)
            row["Xi_hat_preserved"] = bool(
                row["Xi_hat"] and row["Xi_hat_swap"]
                and abs(row["Xi_hat_swap"] / row["Xi_hat"] - 1.0) <= vf.TOL_SWAP_XI_REL)
            row["signature_ok"] = bool(row["share_sign_reversed"] and row["c_sign_reversed"]
                                       and row["R_preserved"] and row["Xi_field_preserved"]
                                       and row["Xi_hat_preserved"])
            rec["path_swap"].append(row)

    # --- ARM H: identical-path negative control --------------------------------------------
    ctrl = _find("identical_path", vf.S_COARSE, ap_mid)
    rec["identical_path_control"] = {
        "S": ctrl["S"], "aperture": ap_mid,
        "R": ctrl["boundary"]["R"], "s": ctrl["boundary"]["s"],
        "R_minus_1": ctrl["boundary"]["R"] - 1.0, "s_minus_half": ctrl["boundary"]["s"] - 0.5,
        "q_lat": ctrl["truth"]["q_lat"], "p_face_gap_open": ctrl["truth"]["p_face_gap_open"],
        "X_cross_product": ctrl["truth"]["X_cross_product"],
        "X_normalised": ctrl["truth"]["X_normalised"],
        "inverse_status": ctrl["inference"]["status"],
        "Xi_hat": ctrl["inference"]["Xi_hat"], "c_hat": ctrl["inference"]["c_hat"],
        "degenerate_atol_used_by_inverse": wp6_degenerate_atol(),
    }

    # --- ARM I: one-voxel adversarial asymmetry, at the finest scientific resolution --------
    for name in vf.PERTURBATIONS:
        row = _find("asymmetry", vf.S_FINE, ap_mid, perturbation=name)
        base = _find("primary", vf.S_FINE, ap_mid)
        sw = _find("asymmetry_swap", vf.S_FINE, ap_mid, swapped=True, perturbation=name)
        rec["asymmetry"].append({
            "perturbation": name, "S": vf.S_FINE, "aperture": ap_mid,
            "blocked_share": row["boundary"]["blocked_share"],
            "blocked_share_departure": row["boundary"]["blocked_share"] - 0.5,
            "blocked_share_unperturbed": base["boundary"]["blocked_share"],
            "Xi_hat": row["inference"]["Xi_hat"], "Xi_hat_unperturbed": base["inference"]["Xi_hat"],
            "Xi_hat_bias_factor": (row["inference"]["Xi_hat"] / base["inference"]["Xi_hat"])
            if (row["inference"]["Xi_hat"] and base["inference"]["Xi_hat"]) else None,
            "Xi_field": row["truth"]["Xi_field"], "Xi_field_unperturbed": base["truth"]["Xi_field"],
            "inverse_status": row["inference"]["status"],
            "inverse_returned_physical": row["inference"]["status"] == "ok",
            "Xi_hat_swap": sw["inference"]["Xi_hat"],
            "swap_exposes": (
                None if not (row["inference"]["Xi_hat"] and sw["inference"]["Xi_hat"])
                else abs(sw["inference"]["Xi_hat"] / row["inference"]["Xi_hat"] - 1.0)
                > vf.TOL_SWAP_XI_REL),
        })

    # --- grid refinement -------------------------------------------------------------------
    cls = {}
    for S in vf.SCIENTIFIC_RESOLUTIONS:
        w = [r for r in rec["cases"] if r["role"] == "primary" and r["S"] == S
             and vf.XI_WINDOW_LO <= r["truth"]["Xi_field"] <= vf.XI_WINDOW_HI]
        ok = bool(w) and all(
            r["inference"]["status"] == "ok" and r["inference"]["Xi_hat"]
            and 0.5 <= r["inference"]["Xi_hat"] / r["truth"]["Xi_field"] <= 2.0 for r in w)
        cls[str(S)] = "factor_two_recovered" if ok else "not_recovered"
    pairs = []
    for ap in selected:
        a = next((r for r in rec["cases"] if r["role"] == "primary" and r["S"] == vf.S_COARSE
                  and r["aperture"] == ap), None)
        b = next((r for r in rec["cases"] if r["role"] == "primary" and r["S"] == vf.S_FINE
                  and r["aperture"] == ap), None)
        if a and b:
            pairs.append({
                "aperture": ap,
                "R_coarse": a["boundary"]["R"], "R_fine": b["boundary"]["R"],
                "R_rel_change": b["boundary"]["R"] / a["boundary"]["R"] - 1.0,
                "s_coarse": a["boundary"]["s"], "s_fine": b["boundary"]["s"],
                "c_field_coarse": a["truth"]["c_field"], "c_field_fine": b["truth"]["c_field"],
                "Xi_field_coarse": a["truth"]["Xi_field"], "Xi_field_fine": b["truth"]["Xi_field"],
                "Xi_field_rel_change": b["truth"]["Xi_field"] / a["truth"]["Xi_field"] - 1.0,
                "Xi_hat_coarse": a["inference"]["Xi_hat"], "Xi_hat_fine": b["inference"]["Xi_hat"],
            })
    rec["grid_refinement"] = {"classification_by_resolution": cls, "pairs": pairs}
    _dump(out_dir / "arm_cdefghi.json", rec)
    return rec


# ==========================================================================================
# ARM J — Route-A isolation gate (erratum E1) + node-surface sensitivity, at BOTH scientific
# resolutions, for the blocked fixture and every frozen aperture that carries a decision clause.
# ==========================================================================================

def _node_block(r, mask, meta, g, d):
    """Boundary observables measured with the node surfaces moved `d` voxels further into the
    common plenum. d = 0 is the frozen surface pair."""
    xin, xout = meta["x_node_in"] - d, meta["x_node_out"] + d
    pin, pin_sd, _ = vf.plane_pressure(r["rho"], mask, xin, g)
    pout, pout_sd, _ = vf.plane_pressure(r["rho"], mask, xout, g)
    q1 = vf.plane_flux(r["ux"], mask, meta["x_meas_a"], meta["lane1_y"])
    q2 = vf.plane_flux(r["ux"], mask, meta["x_meas_a"], meta["lane2_y"])
    dP = pin - pout
    return {"offset": d, "x_node_in": xin, "x_node_out": xout, "dP": dP, "Q": q1 + q2,
            "q1": q1, "q2": q2, "C": (q1 + q2) / dP, "s": q1 / (q1 + q2),
            "p_node_in": pin, "p_node_out": pout,
            "p_in_sd_over_dP": pin_sd / dP, "p_out_sd_over_dP": pout_sd / dP}


def _face_pressure(r, mask, y, ax, az, g):
    vals = []
    for x in range(ax[0], ax[1]):
        fl = ~mask[x, y, az[0]:az[1]]
        if fl.any():
            vals.append(r["rho"][x, y, az[0]:az[1]][fl] / 3.0 - g * x)
    if not vals:
        return float("nan"), float("nan")
    v = np.concatenate(vals)
    return float(v.mean()), float(v.std())


def _job_route_a(spec):
    """One LB solve for Arm J. `aperture=None` is the blocked fixture (whose face pressures are
    reported for EVERY frozen aperture footprint, since one blocked run serves them all)."""
    S, g = spec["S"], vf.G_PRIMARY
    mask, meta = vf.build_fixture(S, aperture=spec["aperture"])
    if spec["obstructed"]:
        mask = _plenum_obstruction(mask, S)
    r = solve(mask, g, spec["backend"], fields=("rho", "uy", "uz"))
    out = {"S": S, "aperture": spec["aperture"], "obstructed": spec["obstructed"],
           "steps": int(r["steps"]), "converged": bool(r["steps"] < vf.MAX_STEPS),
           "nodes": [_node_block(r, mask, meta, g, d) for d in (0,) + meta["node_offsets"]]}
    if spec["aperture"] is None:
        faces = {}
        for ap in spec["selected"]:
            m2 = vf.fixture_meta(S, aperture=ap)
            ax, az = m2["aperture_x"], m2["aperture_z"]
            p1, p1sd = _face_pressure(r, mask, meta["y_face1"], ax, az, g)
            p2, p2sd = _face_pressure(r, mask, meta["y_face2"], ax, az, g)
            faces["%d,%d" % (ap["kx"], ap["kz"])] = {"p1_0": p1, "p2_0": p2,
                                                     "p1_0_sd": p1sd, "p2_0_sd": p2sd}
        out["blocked_faces"] = faces
    else:
        ax, az = meta["aperture_x"], meta["aperture_z"]
        p1, p1sd = _face_pressure(r, mask, meta["y_face1"], ax, az, g)
        p2, p2sd = _face_pressure(r, mask, meta["y_face2"], ax, az, g)
        yb = meta["y_bridge"]
        q_lat = float(np.where(mask[:, yb, :], 0.0, r["uy"][:, yb, :])[ax[0]:ax[1],
                                                                      az[0]:az[1]].sum())
        out.update({"p1": p1, "p2": p2, "p1_sd": p1sd, "p2_sd": p2sd, "q_lat": q_lat})
    return out


def _derive(blk, opn, i_node):
    """Truth + boundary + blind inference for one (S, aperture) at one node-surface choice."""
    b, o = blk["nodes"][i_node], opn["nodes"][i_node]
    key = "%d,%d" % (opn["aperture"]["kx"], opn["aperture"]["kz"])
    p1_0, p2_0 = blk["blocked_faces"][key]["p1_0"], blk["blocked_faces"][key]["p2_0"]
    g1t = b["q1"] / (b["p_node_in"] - p1_0)
    g1b = b["q1"] / (p1_0 - b["p_node_out"])
    g2t = b["q2"] / (b["p_node_in"] - p2_0)
    g2b = b["q2"] / (p2_0 - b["p_node_out"])
    A1, A2 = g1t + g1b, g2t + g2b
    gap = opn["p1"] - opn["p2"]
    ok = bool(np.isfinite(gap) and gap != 0 and np.sign(gap) == np.sign(opn["q_lat"]))
    G_lat = opn["q_lat"] / gap if ok else float("nan")
    inf = vf.infer_from_boundary({
        "Q0": b["Q"], "dP0": b["dP"], "q1": o["q1"], "q2": o["q2"], "dP": o["dP"],
        "orientation": "nominal", "converged": blk["converged"] and opn["converged"]})
    return {"offset": b["offset"], "R": inf["R"], "s": inf["s"],
            "c_hat": inf["c_hat"], "Xi_hat": inf["Xi_hat"], "status": inf["status"],
            "c_field": (g1t - g1b) / A1, "A1_field": A1, "A2_field": A2,
            "G_lat_field": G_lat,
            "Xi_field": G_lat * (1.0 / A1 + 1.0 / A2) if ok else float("nan"),
            "node_in_sd_over_dP": b["p_in_sd_over_dP"],
            "node_out_sd_over_dP": b["p_out_sd_over_dP"]}


def arm_j(backend, out_dir, log):
    freeze = load_freeze()
    selected = [dict(a) for a in freeze["selected"]]
    specs = []
    for S in vf.SCIENTIFIC_RESOLUTIONS:
        for obs in (False, True):
            specs.append({"S": S, "aperture": None, "obstructed": obs, "backend": backend,
                          "selected": selected})
            for ap in selected:
                specs.append({"S": S, "aperture": ap, "obstructed": obs, "backend": backend,
                              "selected": selected})
    log("ARM J: %d solves (return-path gate + node-surface sensitivity)" % len(specs))
    rows = _pmap(_job_route_a, specs)

    def find(S, ap, obs):
        return next(r for r in rows if r["S"] == S and r["aperture"] == ap
                    and r["obstructed"] == obs)

    gate, node_sens = [], []
    for S in vf.SCIENTIFIC_RESOLUTIONS:
        for ap in selected:
            nom = _derive(find(S, None, False), find(S, ap, False), 0)
            obs = _derive(find(S, None, True), find(S, ap, True), 0)
            row = {
                "S": S, "aperture": ap,
                "R_nominal": nom["R"], "R_obstructed": obs["R"],
                "R_rel_change": obs["R"] / nom["R"] - 1.0,
                "s_nominal": nom["s"], "s_obstructed": obs["s"],
                "s_abs_change": obs["s"] - nom["s"],
                "c_hat_nominal": nom["c_hat"], "c_hat_obstructed": obs["c_hat"],
                "Xi_hat_nominal": nom["Xi_hat"], "Xi_hat_obstructed": obs["Xi_hat"],
                "Xi_hat_rel_change": (obs["Xi_hat"] / nom["Xi_hat"] - 1.0)
                if (nom["Xi_hat"] and obs["Xi_hat"]) else None,
                "sign_s_minus_half_nominal": int(np.sign(nom["s"] - 0.5)),
                "sign_s_minus_half_obstructed": int(np.sign(obs["s"] - 0.5)),
                "sign_preserved": bool(np.sign(nom["s"] - 0.5) == np.sign(obs["s"] - 0.5)),
                "dP_rel_change": obs["R"] and (
                    find(S, None, True)["nodes"][0]["dP"]
                    / find(S, None, False)["nodes"][0]["dP"] - 1.0),
            }
            row["R_within_bound"] = bool(abs(row["R_rel_change"]) <= vf.TOL_RETURN_PATH_R_REL)
            row["s_within_bound"] = bool(abs(row["s_abs_change"]) <= vf.TOL_RETURN_PATH_S_ABS)
            row["pass"] = bool(row["R_within_bound"] and row["s_within_bound"]
                               and row["sign_preserved"])
            gate.append(row)
            log("  J gate S=%d ap=%s dR=%+.3e ds=%+.3e dXi_hat=%s %s"
                % (S, ap, row["R_rel_change"], row["s_abs_change"],
                   ("%+.3e" % row["Xi_hat_rel_change"]) if row["Xi_hat_rel_change"] is not None
                   else "n/a", "OK" if row["pass"] else "FAIL"))

            offs = [_derive(find(S, None, False), find(S, ap, False), i) for i in range(3)]
            base = offs[0]
            node_sens.append({
                "S": S, "aperture": ap, "surfaces": offs,
                "R_rel_change_by_offset": [o["R"] / base["R"] - 1.0 for o in offs],
                "c_field_abs_change_by_offset": [o["c_field"] - base["c_field"] for o in offs],
                "Xi_field_rel_change_by_offset": [o["Xi_field"] / base["Xi_field"] - 1.0
                                                  for o in offs],
                "Xi_hat_rel_change_by_offset": [
                    (o["Xi_hat"] / base["Xi_hat"] - 1.0)
                    if (o["Xi_hat"] and base["Xi_hat"]) else None for o in offs],
                "in_window_by_offset": [
                    bool(np.isfinite(o["Xi_field"])
                         and vf.XI_WINDOW_LO <= o["Xi_field"] <= vf.XI_WINDOW_HI) for o in offs],
                "factor_two_by_offset": [
                    bool(o["Xi_hat"] and np.isfinite(o["Xi_field"])
                         and 0.5 <= o["Xi_hat"] / o["Xi_field"] <= 2.0) for o in offs],
            })
    rec = {"gate": gate, "node_surface_sensitivity": node_sens, "raw": rows,
           "tolerances": {"R_rel": vf.TOL_RETURN_PATH_R_REL, "s_abs": vf.TOL_RETURN_PATH_S_ABS,
                          "node_offset_R_rel": vf.TOL_NODE_OFFSET_R_REL},
           "coverage": {"resolutions": list(vf.SCIENTIFIC_RESOLUTIONS),
                        "apertures": selected,
                        "note": ("Every decision-carrying configuration was tested: the blocked "
                                 "fixture and all frozen apertures at both scientific "
                                 "resolutions. The bound is therefore not generalised from one "
                                 "probe.")}}
    _dump(out_dir / "arm_j.json", rec)
    return rec


def wp6_degenerate_atol():
    from puckworks.analysis import screen_wp6_lateral_identifiability as wp6
    return wp6.DEGENERATE_ATOL


# ==========================================================================================
# assembly
# ==========================================================================================

def _git(*args):
    try:
        return subprocess.check_output(("git",) + args, cwd=REPO_ROOT).decode().strip()
    except Exception:
        return None


def _dump(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=1, sort_keys=True, default=_json_default) + "\n")


def _json_default(o):
    if isinstance(o, (np.floating, np.integer)):
        return o.item()
    if isinstance(o, np.ndarray):
        raise TypeError("field arrays are never written to the run record")
    raise TypeError(repr(o))


def environment():
    import scipy
    try:
        import taichi
        tv = taichi.__version__
    except Exception:
        tv = None
    return {"python": sys.version.split()[0], "numpy": np.__version__,
            "scipy": scipy.__version__, "taichi": tv,
            "platform": platform.platform(), "machine": platform.machine()}


def assemble(out_dir):
    a = json.loads((out_dir / "arm_a.json").read_text())
    b = json.loads((out_dir / "arm_b.json").read_text())
    c = json.loads((out_dir / "arm_cdefghi.json").read_text())
    jp = out_dir / "arm_j.json"
    # Arm J may be DELIBERATELY NOT RUN when execution validity has already failed on a control
    # its 24 solves cannot repair (e.g. the componentwise creeping-flow control). In that case its
    # controls are recorded NOT_EVALUATED and FAIL-closed — never silently treated as passed, and
    # never omitted so that a missing control reads as an absent objection.
    j = json.loads(jp.read_text()) if jp.exists() else None

    conv_ok = all(r["boundary"]["converged"] and r["boundary"]["converged_blocked"]
                  for r in c["cases"]) and all(r["converged"] for r in c["blocked"])
    # C-linearity (frozen control) and R-linearity (what the decision's observable needs).
    lin_C = {}
    for S in vf.SCIENTIFIC_RESOLUTIONS:
        cs = [r["C"] for r in a["linearity"] if r["S"] == S]
        lin_C[str(S)] = max(cs) / min(cs) - 1.0
    lin_C_ok = all(v <= vf.TOL_LINEARITY_REL for v in lin_C.values())
    lin_R = {}
    for S in vf.SCIENTIFIC_RESOLUTIONS:
        rs = [r["boundary"]["R"] for r in c["cases"]
              if r["S"] == S and r["role"] in ("primary", "linearity_R")
              and r["aperture"] == c["aperture_freeze"]["selected"][
                  len(c["aperture_freeze"]["selected"]) // 2]]
        lin_R[str(S)] = (max(rs) / min(rs) - 1.0) if len(rs) > 1 else None
    # lin_R is reported inside boundary_inference_forcing_stability, whose numerical gate now
    # binds it (and the other five spreads) to TOL_LINEARITY_REL. It is NOT a separate verdict.
    lin_R_ok = all(v is not None and v <= vf.TOL_LINEARITY_REL for v in lin_R.values())
    mach_ok = all(r["mach"] <= vf.TOL_MACH for r in a["linearity"])
    mass_ok = all(r["plane_ptp_rel"] <= vf.TOL_MASS_REL for r in a["mass_conservation"]) and all(
        r["numerics"]["plane_flux_ptp_rel"] <= vf.TOL_MASS_REL for r in c["cases"])
    topo_ok = all(t["mirror_exact"] and t["single_connected"] and t["no_lateral_bypass"]
                  for t in a["topology"])
    plane_ok = all(abs(r["boundary"]["s_plane_delta"]) <= vf.TOL_PLANE_REL for r in c["cases"])
    # NOTE: a paired-row COUNT is not a convergence criterion; see grid_refinement.
    # ---- return-path probe: BOTH the frozen control and the quantity the adjudication claims --
    # The frozen control demanded that the two-terminal conductance C = Q/dP itself be invariant
    # to obstructing the return path. That is STRONGER than the adjudication's claim and it is
    # measurably false: the obstruction sits ~2 base voxels from the inlet node plane in a
    # 7-base-voxel plenum, so it perturbs the lane ENTRANCE profile, which is genuinely inside the
    # measured sub-network. What the adjudication actually claims is that the return path divides
    # out of the RATIO R = C_open / C_blocked. Both numbers are recorded; neither is hidden, and
    # the frozen control's verdict is reported as it stands (see PROTOCOL.md erratum).
    ret_C_worst = max(abs(r["C_change_rel"]) for r in a["return_path_invariance"])
    ret_ok_frozen = ret_C_worst <= vf.TOL_LINEARITY_REL
    _rp = {r["aperture"] is None: r for r in a["return_path_invariance"]}
    R_nom = _rp[False]["nominal"]["C"] / _rp[True]["nominal"]["C"]
    R_obs = _rp[False]["obstructed_return"]["C"] / _rp[True]["obstructed_return"]["C"]
    ret_R = {
        "R_nominal": R_nom, "R_obstructed_return": R_obs,
        "R_rel_change": R_obs / R_nom - 1.0,
        "signal_R_minus_1_nominal": R_nom - 1.0,
        "fraction_of_coupling_signal": abs(R_obs - R_nom) / abs(R_nom - 1.0),
        "dP_rel_change": _rp[True]["dP_change_rel"],
        "C_rel_change_blocked": _rp[True]["C_change_rel"],
        "C_rel_change_open": _rp[False]["C_change_rel"],
        "tol_swap_r_rel": vf.TOL_SWAP_R_REL,
        "passes_on_R": bool(abs(R_obs / R_nom - 1.0) <= vf.TOL_SWAP_R_REL),
    }
    # The single smoke-scale probe above is superseded as a GATE by Arm J, which repeats the
    # obstruction at both scientific resolutions for the blocked fixture and every frozen
    # aperture, against the predeclared 0.1 % bound on R and 5e-4 on the outlet share.
    ret_R["superseded_as_gate_by"] = "arm_j.gate"
    gate_rows = j["gate"] if j else []
    ret_ok = bool(gate_rows) and all(r["pass"] for r in gate_rows)

    prim = [r for r in c["cases"] if r["role"] == "primary"]
    mech = {
        "bridge_flux_consistent": all(
            r["truth"]["gap_sign_consistent"] and r["truth"]["q_lat"] > 0 for r in prim),
        "R_direction_consistent": all(r["boundary"]["R"] >= 1.0 - 1e-9 for r in prim),
        "share_direction_consistent": all(r["boundary"]["s"] < 0.5 for r in prim),
        "G_lat_monotone_in_aperture": _monotone_by_aperture(prim),
    }
    controls = {
        "convergence": {
            # every scientific run must meet the criterion before max_steps AND the criterion
            # itself must stop late enough — the forced-step audit is what establishes the latter,
            # so a failed audit fails the control even if every run "converged".
            "pass": bool(conv_ok and all(r["within_tolerance"] for r in a["convergence_audit"])),
            "all_runs_converged": conv_ok,
            "rtol": vf.RTOL, "max_steps": vf.MAX_STEPS,
            "worst_steps": max(r["boundary"]["steps"] for r in c["cases"]),
            "forced_step_audit": a["convergence_audit"],
            "audit_factor": vf.CONVERGENCE_AUDIT_FACTOR,
            "audit_tol_rel": vf.TOL_CONVERGENCE_REL},
        # --- E2 is split into THREE records that are never allowed to substitute for one
        # another. R-stability certifies the boundary observables; it does NOT certify the
        # internal field truth, which is built from Q, dP, q_lat and (p1-p2) individually.
        "low_mach_linearity": {
            # Mach REGIME only. This control can no longer be marked green from R + Mach.
            "pass": bool(mach_ok),
            "max_mach": max(r["mach"] for r in a["linearity"]),
            "tol_mach": vf.TOL_MACH,
            "scope": ("Mach/compressibility regime ONLY. Linearity adequacy is decided by "
                      "componentwise_creeping_flow_control; boundary-observable stability by "
                      "boundary_inference_forcing_stability."),
        },
        "frozen_C_linearity_control": {
            "pass": lin_C_ok,
            "verdict": "FAIL" if not lin_C_ok else "PASS",
            "conductance_spread_by_resolution": lin_C,
            "tol_linearity_rel": vf.TOL_LINEARITY_REL,
            "note": ("HISTORICAL FROZEN REQUIREMENT, PRESERVED — not relabelled. The frozen "
                     "exact-linearity criterion FAILED, revealing a small finite-Reynolds-number "
                     "dependence of the absolute conductance (Re ~ 1e-2). That is NOT the same "
                     "kind of defect as E1: here the failure is informative about the REGIME, and "
                     "whether the dependence is bounded enough for the internal field quantities "
                     "to serve as numerical truth is decided separately by "
                     "componentwise_creeping_flow_control. See PROTOCOL.md erratum E2."),
        },
        "componentwise_creeping_flow_control": _componentwise_creeping_flow(
            c, c["aperture_freeze"]["selected"][len(c["aperture_freeze"]["selected"]) // 2]),
        "boundary_inference_forcing_stability": {
            **_inference_forcing_stability(
                c, c["aperture_freeze"]["selected"][len(c["aperture_freeze"]["selected"]) // 2]),
            "R_spread_by_resolution": lin_R,
            "R_spread_within_tolerance": lin_R_ok,
            "tol_numerical_rel": vf.TOL_LINEARITY_REL,
            "scope": ("Confirms R, s, c_field, c_hat, Xi_field and Xi_hat are NUMERICALLY stable "
                      "under forcing (each spread bound to TOL_LINEARITY_REL) AND that the "
                      "inverse status, the sign of s - 1/2 and the classification do not move. "
                      "Does NOT by itself validate the internal field truth — that is "
                      "componentwise_creeping_flow_control."),
        },
        "coarse_graining_surface_stability": _node_sensitivity_summary(j),
        "frozen_volume_flux_uniformity_control": {
            "pass": mass_ok, "status": "EVALUATED",
            "verdict": "FAIL" if not mass_ok else "PASS",
            "measured_quantity": "sum(u_x) over the fluid nodes of each plane",
            "note": ("HISTORICAL FROZEN PROXY, PRESERVED EXACTLY. This is a volume-flux "
                     "uniformity check, not a mass-conservation check. Its verdict stands as "
                     "measured and is not relabelled."),
            "tol_rel": vf.TOL_MASS_REL,
            "worst_plane_ptp_rel": max(
                [r["plane_ptp_rel"] for r in a["mass_conservation"]]
                + [r["numerics"]["plane_flux_ptp_rel"] for r in c["cases"]]),
            "arm_a_by_resolution": {str(r["S"]): r["plane_ptp_rel"]
                                    for r in a["mass_conservation"]},
            "specification_note": (
                "REPORTED, NOT USED TO SOFTEN THE VERDICT. The frozen control measures the VOLUME "
                "flux integral of u_x. In a weakly compressible solver the conserved quantity is "
                "the MASS flux integral of rho*u_x, so a residual of order the fractional density "
                "variation along the fixture is expected and is NOT a violation of the solver's "
                "own conservation. The observed magnitude is consistent with that: the density "
                "drop implied by the measured node pressures is ~5e-4 at S=2 and larger at S=3, "
                "where the domain and hence the total pressure drop are larger. The stored records "
                "contain only u_x sums, so rho*u_x cannot be recomputed from them; measuring the "
                "mass flux is a change for the NEXT protocol, not a repair applicable here. The "
                "frozen verdict stands as measured. See PROTOCOL.md erratum E4."),
            "expected_effect_of_lower_forcing": (
                "Lower forcing is EXPECTED to reduce the volume-versus-mass-flux proxy "
                "discrepancy, because a smaller total pressure drop means a smaller density "
                "variation. It does not evaluate mass conservation. Actual mass flux must be "
                "MEASURED in the next execution."),
        },
        "mass_conservation": {
            # The conserved quantity in a weakly compressible solver is sum(rho*u_x). The rho
            # fields needed to form it at the required planes were not retained in the compact
            # stage record, so this control CANNOT be evaluated from what exists. Fail-closed,
            # and explicitly NOT a claim that solver mass conservation failed.
            "pass": False, "status": "NOT_EVALUATED",
            "not_evaluated_because": "MASS_FLUX_RHO_U_NOT_RETAINED_AT_REQUIRED_PLANES",
            "measured_quantity": "sum(rho * u_x) — NOT AVAILABLE in the retained record",
            "statement": ("The frozen volume-flux proxy FAILED at S=3; actual mass conservation "
                          "was NOT EVALUATED in this execution."),
            "see": "frozen_volume_flux_uniformity_control",
        },
        "topology": {
            # Topology answers whether the intended fluid connections exist. Whether the
            # resolved solution can be reduced to the proposed two-node representation is a
            # SEPARATE control, coarse_graining_surface_stability; both roll up into clause 1.
            "pass": bool(topo_ok and ret_ok),
            # Connectivity evidence and the Route-A isolation portion are distinct. If the masks
            # pass but Arm J was deliberately omitted, this control is fail-closed but NOT an
            # evidence-based failure, and the causal record must not report it as one.
            "status": "EVALUATED" if (not topo_ok or j is not None) else "NOT_EVALUATED",
            "not_evaluated_because": (None if (not topo_ok or j is not None)
                                      else "NOT_RUN_UPSTREAM_EXECUTION_INVALID"),
            "masks_and_connectivity": topo_ok,
            "return_path_common_mode_bound_holds": ret_ok,
            "route_a_isolation_gate": {
                "pass": ret_ok,
                "tol_R_rel": vf.TOL_RETURN_PATH_R_REL,
                "tol_s_abs": vf.TOL_RETURN_PATH_S_ABS,
                "status": "EVALUATED" if j else "NOT_EVALUATED",
                "not_evaluated_because": None if j else "NOT_RUN_UPSTREAM_EXECUTION_INVALID",
                "worst_R_rel_change": max((abs(r["R_rel_change"]) for r in gate_rows),
                                          default=None),
                "worst_s_abs_change": max((abs(r["s_abs_change"]) for r in gate_rows),
                                          default=None),
                "all_signs_preserved": all(r["sign_preserved"] for r in gate_rows)
                if gate_rows else None,
                "rows": gate_rows,
                "coverage": j["coverage"] if j else {
                    "note": ("Arm J was deliberately NOT RUN: execution validity had already "
                             "failed on a control its 24 solves cannot repair. Recorded as "
                             "NOT_EVALUATED and fail-closed, so the Route-A isolation bound is "
                             "NOT claimed by this execution.")},
                "statement": (
                    "The return path does NOT cancel exactly at the level of either absolute "
                    "conductance, because it influences the entrance region near the measurement "
                    "planes. Its effects on the open and blocked conductances are strongly "
                    "common-mode, so the pressure-normalised ratio R is insensitive to the tested "
                    "return-path perturbation to bounded numerical accuracy.")},
            "return_path_R_probe_smoke": ret_R,
            "frozen_C_invariance_control": {
                "pass": ret_ok_frozen,
                "worst_C_change_under_return_obstruction": ret_C_worst,
                "tol": vf.TOL_LINEARITY_REL,
                "note": ("MIS-SPECIFIED AND FAILED AS WRITTEN — recorded, not hidden. It required "
                         "C = Q/dP itself to be invariant to the return-path obstruction, which is "
                         "stronger than the adjudication's claim and is false because the probe "
                         "perturbs the lane entrance profile inside a short plenum. The decision "
                         "uses the R-ratio probe above, which is what the adjudication claims. "
                         "See the post-execution erratum in PROTOCOL.md.")},
        },
        "plane_invariance": {"pass": plane_ok, "tol_rel": vf.TOL_PLANE_REL,
                             "worst_share_delta": max(
                                 abs(r["boundary"]["s_plane_delta"]) for r in c["cases"])},
        "fixed_lattice_forcing_resolution_comparison": {
            "status": "EVALUATED_DIAGNOSTIC", "pass": None,
            "resolutions": list(vf.SCIENTIFIC_RESOLUTIONS),
            "n_pairs": len(c["grid_refinement"]["pairs"]),
            "pairs": c["grid_refinement"]["pairs"],
            "classification_by_resolution":
                c["grid_refinement"]["classification_by_resolution"],
            "note": ("S=2 and S=3 were run at the SAME lattice g and nu with all lengths "
                     "proportional to S, so they are NOT the same dimensionless problem: "
                     "u ~ g L^2 / nu and Re ~ g L^3 / nu^2, giving Re(S=3)/Re(S=2) = (3/2)^3 = "
                     "3.375. These rows compare two different Reynolds numbers and are a "
                     "DIAGNOSTIC, not a grid-convergence result. See PROTOCOL.md erratum E5."),
        },
        "grid_refinement": {
            "pass": False, "status": "NOT_EVALUATED",
            "not_evaluated_because":
                "DYNAMIC_SIMILARITY_NOT_HELD_AND_NO_FROZEN_CONVERGENCE_TOLERANCE",
            "resolutions": list(vf.SCIENTIFIC_RESOLUTIONS),
            "statement": ("Grid refinement was NOT evaluated: dynamic similarity was not held "
                          "across the two resolutions, and no convergence tolerance was frozen "
                          "for it. The existing paired rows are retained as "
                          "fixed_lattice_forcing_resolution_comparison."),
            "see": "fixed_lattice_forcing_resolution_comparison",
        },
        "backend_cross_check": {
            # Reported, never required. Taichi is absent and its port is cubic-only, so
            # this is NOT_EVALUATED — recorded as not performed, never as passed.
            **a["backend_cross_check"],
            "pass": bool(a["backend_cross_check"].get("taichi_available")),
            "status": ("EVALUATED" if a["backend_cross_check"].get("taichi_available")
                       else "NOT_EVALUATED"),
            "not_evaluated_because": (None if a["backend_cross_check"].get("taichi_available")
                                      else "TAICHI_UNAVAILABLE_AND_PORT_IS_CUBIC_ONLY"),
        },
        "axis_rotation_anisotropy": _anisotropy(b),
        "tau_independence_fixture": _tau_independence(a),
        "determinism": {"note": "the kernel and every derived quantity are deterministic float "
                                "operations with no RNG; re-running an identical configuration "
                                "on identical hardware reproduces the record bit-for-bit."},
    }

    # attach the coupon prediction to every case
    for r in c["cases"]:
        S = str(r["S"])
        if r["aperture"] and S in b["coupon_prediction"]:
            p = b["coupon_prediction"][S]
            hit = next((x for x in p["rows"] if x["kx"] == r["aperture"]["kx"]
                        and x["kz"] == r["aperture"]["kz"]), None)
            if hit:
                r["truth"]["Xi_coupon"] = hit["Xi_coupon"]
                r["truth"]["c_coupon"] = p["c_coupon"]
                r["truth"]["G_bridge_coupon"] = hit["G_bridge"]
                r["truth"]["a_coupon"] = p["a_coupon"]
                r["truth"]["b_coupon"] = p["b_coupon"]
        # ASSEMBLY-ONLY normalisation, then ARM F with the case's ACTUAL network geometry
        t, i = _normalise_truth(r["truth"]), r["inference"]
        r["comparison"] = _arm_f(t, i, r["boundary"], variant=r.get("variant", "mirror"),
                                 swapped=bool(r.get("swapped")))

    rec = {
        # The head that produced the NUMBERS is not necessarily the head that assembles them.
        # Never conflate them: `provenance` records each stage's own launch authority, verified.
        "provenance": execution_authority_report(),
        "git_status_clean_at_assembly": (_git("status", "--porcelain") == ""),
        "environment": environment(),
        "solver": {"backend": "reference", "kernel": "brewer2026.lb_reference (D3Q19 TRT, "
                                                     "magic Lambda=3/16, full-way bounce-back)",
                   "dtype": "float64", "tau_plus": vf.TAU_PLUS, "nu": (vf.TAU_PLUS - 0.5) / 3.0,
                   "g": vf.G_PRIMARY, "rtol": vf.RTOL, "check": vf.CHECK,
                   "min_steps": vf.MIN_STEPS, "max_steps": vf.MAX_STEPS},
        "boundary_mode": {
            "route": "A",
            "name": "periodic body force with a resolved common plenum (ROUTE A)",
            "pressure_definition": "p = rho/3 - g*x  (physical field; the lattice density carries "
                                   "only the periodic part)",
            "why_valid": (
                "R is a ratio of two independently MEASURED two-terminal conductances Q/dP of the "
                "same lane sub-network, formed from an open and a blocked run that differ ONLY in "
                "the aperture voxels. The return-path contribution was strongly COMMON-MODE in "
                "the tested perturbation and its residual effect on R is BOUNDED by Arm J; exact "
                "cancellation is neither assumed nor claimed."),
            "how_far_that_is_demonstrated": (
                "BOUNDED, NOT ELIMINATED — see PROTOCOL.md erratum E1. The obstruction probe "
                "changed the return path by 22.5 % in dP; the two conductances moved by -1.84 % "
                "(blocked) and -1.88 % (open), i.e. nearly common-mode, and R moved by 3.7e-4, "
                "about 1 % of the coupling signal R-1. That is an UPPER BOUND from a deliberately "
                "extreme perturbation, not a calibration of the nominal fixture, and it is not "
                "negligible against a factor-of-two recovery criterion. The stronger claim that C "
                "itself is invariant to the return path was the frozen control's form and it is "
                "measurably FALSE: the probe perturbs the lane entrance, which is genuinely "
                "inside the measured sub-network. See controls.topology.frozen_C_invariance_"
                "control for that verdict, preserved."),
        },
        "geometry": {"base_template": vf.BASE, "topology": a["topology"],
                     "min_feature_vox": vf.MIN_FEATURE_VOX,
                     "regeneration": "puckworks.analysis.rp_d_lc_virtual_fixture.build_fixture("
                                     "S, aperture={'kx':..,'kz':..}, variant=..., swapped=...)"},
        "coupons": b,
        "aperture_freeze": c["aperture_freeze"],
        "blocked": c["blocked"],
        "cases": c["cases"],
        "path_swap": c["path_swap"],
        "identical_path_control": c["identical_path_control"],
        "asymmetry": c["asymmetry"],
        "grid_refinement": c["grid_refinement"],
        "controls": controls,
        "mechanism": mech,
        "arm_a": a,
        "arm_j": j if j else {
            "status": "NOT_RUN_UPSTREAM_EXECUTION_INVALID",
            "gate": "NOT_EVALUATED",
            "node_surface_sensitivity": "NOT_EVALUATED",
            "causal_sequence": [
                "forcing-independence of the internal field truth FAILED",
                "execution validity therefore FAILED",
                "the costly downstream nuisance-isolation arm was no longer scientifically necessary"],
        },
    }
    dest = REPO_ROOT / vf.RUNS_REL / "run_record.json"
    _dump(dest, rec)
    print("wrote %s" % dest)
    return rec


def _monotone_by_aperture(prim):
    out = {}
    for S in vf.SCIENTIFIC_RESOLUTIONS:
        pts = sorted(((r["aperture"]["kx"] * r["aperture"]["kz"], r["truth"]["G_lat_field"])
                      for r in prim if r["S"] == S), key=lambda t: t[0])
        out[str(S)] = all(b[1] >= a[1] for a, b in zip(pts, pts[1:])) if len(pts) > 1 else None
    return out


# ==========================================================================================
# ASSEMBLY-ONLY SEMANTIC NORMALISATION
# ==========================================================================================
# Everything below runs at ASSEMBLY time and touches no symbol in STAGE_EXECUTED_SYMBOLS. The
# retained numerical rows are re-interpreted, never recomputed: changing field_truth(),
# _run_case() or any solver/geometry symbol would correctly invalidate the execution-authority
# record for rows that have already been produced.

def _classify_truth(t):
    """Is the in-situ field truth quantitatively usable for this case?

    STRUCTURALLY_DEGENERATE_NO_INFORMATION is decided on X == 0 EXACTLY, never on a tolerance:
    a small nonzero X is a different thing (the map is still one-to-one, merely ill-conditioned)
    and conflating them would assert exact equality of two provably unequal mid-node pressures.
    """
    X = t.get("X_cross_product")
    if X == 0.0:
        return "STRUCTURALLY_DEGENERATE_NO_INFORMATION"
    gap = t.get("p_face_gap_open")
    if not t.get("gap_sign_consistent") or gap in (0.0, None) or not np.isfinite(gap or 0.0):
        return "NUMERICALLY_UNRESOLVED"
    return "QUANTITATIVE"


def _normalise_truth(t):
    """Move a non-quantitative case's round-off-amplified quotient out of the scientific fields
    and into a clearly separated diagnostic. Nothing is deleted."""
    status = _classify_truth(t)
    t["truth_status"] = status
    t["quantitative_truth_available"] = (status == "QUANTITATIVE")
    if status == "QUANTITATIVE":
        return t
    t["raw_roundoff_amplified_quotient"] = {
        "p_face_gap_open": t.get("p_face_gap_open"),
        "q_lat": t.get("q_lat"),
        "G_lat_field_raw": t.get("G_lat_field"),
        "Xi_field_raw": t.get("Xi_field"),
        "evidence_use": "NUMERICAL_DIAGNOSTIC_NOT_PHYSICAL_TRUTH",
        "why": ("X = 0 exactly, so no uncoupled mid-node pressure gap drives the bridge; the "
                "measured gap and lateral flux are at round-off/residual scale and their quotient "
                "is meaningless as a conductance."
                if status == "STRUCTURALLY_DEGENERATE_NO_INFORMATION" else
                "X is nonzero but the bridge pressure gap was not resolved with a consistent "
                "sign, so the quotient is not a dependable conductance."),
    }
    t["G_lat_field"] = None
    t["Xi_field"] = None
    return t


def coupon_network_conductances(a, b, variant, swapped):
    """The four axial conductances the coupon-calibrated network must be evaluated with, for the
    ACTUAL geometry of the case. Getting this wrong silently compares the wrong network."""
    if variant == "identical":
        return (a, b, a, b)                 # both lanes ordered alike -> X = 0 identically
    return (b, a, a, b) if swapped else (a, b, b, a)


def _tau_independence(a):
    """Compare tau_plus = 2.0 against 1.2 on the fixture in DIMENSIONLESS terms.

    A Darcy conductance is inversely proportional to the dynamic viscosity, so the raw C = Q/dP
    MUST change by exactly nu(2.0)/nu(1.2) = 2.143 between the two relaxation times — that is the
    definition of viscosity, not a discretisation error. The quantity that has to be invariant is
    the REDUCED conductance nu*C (a pure geometry number) and the outlet share s (dimensionless).
    Arm A recorded the raw ratio; this recomputes the meaningful one.
    """
    rows = []
    for r in a["tau_independence_fixture"]["rows"]:
        nu = (r["tau_plus"] - 0.5) / 3.0
        rows.append({**r, "nu": nu, "reduced_C_nu_times_C": nu * r["C"]})
    hi, lo = rows[0], rows[1]
    return {
        "rows": rows,
        "raw_C_ratio": lo["C"] / hi["C"],
        "expected_raw_C_ratio_nu_hi_over_nu_lo": hi["nu"] / lo["nu"],
        "reduced_C_rel_spread": abs(lo["reduced_C_nu_times_C"] / hi["reduced_C_nu_times_C"] - 1.0),
        "s_abs_spread": abs(lo["s"] - hi["s"]),
        "tol_rel": vf.TOL_LINEARITY_REL,
        "pass": bool(abs(lo["reduced_C_nu_times_C"] / hi["reduced_C_nu_times_C"] - 1.0)
                     <= vf.TOL_LINEARITY_REL and abs(lo["s"] - hi["s"]) <= vf.TOL_LINEARITY_REL),
        "interpretation": (
            "TRT with magic Lambda = 3/16 makes the bounce-back wall position viscosity-"
            "independent. Arm A1 showed that on the analytic plane channel; this shows it holds "
            "for the ASSEMBLED 3D fixture, which is the claim that licenses running the tranche "
            "at tau_plus = 2.0 for time-step economy."),
    }


def _forcing_rows(c, ap_mid, S):
    rows = [r for r in c["cases"] if r["S"] == S and r["aperture"] == ap_mid
            and r["role"] in ("primary", "linearity_R")]
    return sorted(rows, key=lambda r: r["g"])


def _reduced_spread(vals):
    """Relative spread of a quantity that must be EXACTLY proportional to the forcing."""
    a = [abs(v) for v in vals if v is not None and np.isfinite(v)]
    if len(a) < 2 or min(a) == 0.0:
        return float("nan")
    return max(a) / min(a) - 1.0


def _componentwise_creeping_flow(c, ap_mid):
    """E2 — is the simulation close enough to LINEAR creeping flow that its INTERNAL pressure and
    flux fields can serve as independent truth?

    Stability of the derived ratio R is NOT sufficient and must never stand in for this. Open and
    blocked runs can acquire nearly identical finite-Reynolds-number errors, leaving R unchanged
    while biasing the four axial conductances, the bridge conductance, c_field and Xi_field — all
    of which are built from Q, dP, q_lat and (p1 - p2) INDIVIDUALLY, not from their ratio.

    Every component below must be exactly proportional to the forcing in Stokes flow, so each is
    divided by g and its relative spread across x0.5 / x1 / x2 is taken against the protocol's
    componentwise tolerance (1e-4) — NOT the observed conductance drift, and NOT Arm J's 1e-3
    return-path bound.
    """
    comps = (("Q", "boundary"), ("Q0", "boundary"), ("dP", "boundary"), ("dP0", "boundary"),
             ("q_lat", "truth"), ("p_face_gap_open", "truth"))
    out = {"tol_rel": vf.TOL_LINEARITY_REL, "aperture": ap_mid, "by_resolution": {},
           "components": [k for k, _ in comps],
           "why": ("the internal field truth is built from these components individually; a "
                   "stable R does not certify any of them")}
    ok = True
    for S in vf.SCIENTIFIC_RESOLUTIONS:
        rows = _forcing_rows(c, ap_mid, S)
        rec = {"n_forcings": len(rows), "g_values": [r["g"] for r in rows], "reduced_spread": {}}
        for key, src in comps:
            sp = _reduced_spread([r[src][key] / r["g"] for r in rows])
            rec["reduced_spread"][key] = sp
            if not (np.isfinite(sp) and sp <= vf.TOL_LINEARITY_REL):
                ok = False
        rec["worst"] = max((v for v in rec["reduced_spread"].values() if np.isfinite(v)),
                           default=float("nan"))
        rec["pass"] = bool(np.isfinite(rec["worst"]) and rec["worst"] <= vf.TOL_LINEARITY_REL
                           and len(rows) >= 3)
        if len(rows) < 3:
            ok = False
        out["by_resolution"][str(S)] = rec
    out["pass"] = bool(ok)
    return out


def _inference_forcing_stability(c, ap_mid):
    """Confirms R, s, c_field, Xi_field, c_hat and Xi_hat are stable under forcing, and that the
    inverse status, sign of s - 1/2, window membership, factor-of-two membership and the resulting
    classification do not move. This does NOT by itself validate the field truth — that is the
    componentwise control's job — and it is reported without any fitting or correction."""
    out = {"aperture": ap_mid, "tol_rel": vf.TOL_LINEARITY_REL, "by_resolution": {}}
    ok = True
    for S in vf.SCIENTIFIC_RESOLUTIONS:
        rows = _forcing_rows(c, ap_mid, S)
        if len(rows) < 3:
            out["by_resolution"][str(S)] = {"pass": False, "n_forcings": len(rows)}
            ok = False
            continue

        def series(src, key):
            return [r[src][key] for r in rows]

        xi_f = series("truth", "Xi_field")
        xi_h = series("inference", "Xi_hat")
        win = [bool(np.isfinite(x) and vf.XI_WINDOW_LO <= x <= vf.XI_WINDOW_HI) for x in xi_f]
        f2 = [bool(h and np.isfinite(x) and 0.5 <= h / x <= 2.0) for h, x in zip(xi_h, xi_f)]
        rec = {
            "n_forcings": len(rows), "g_values": [r["g"] for r in rows],
            "R": series("boundary", "R"), "s": series("boundary", "s"),
            "c_field": series("truth", "c_field"), "Xi_field": xi_f,
            "c_hat": series("inference", "c_hat"), "Xi_hat": xi_h,
            "inverse_status": series("inference", "status"),
            "R_rel_spread": _reduced_spread(series("boundary", "R")),
            "s_abs_spread": max(series("boundary", "s")) - min(series("boundary", "s")),
            "c_field_abs_spread": max(series("truth", "c_field")) - min(series("truth", "c_field")),
            "Xi_field_rel_spread": _reduced_spread(xi_f),
            "Xi_hat_rel_spread": _reduced_spread(xi_h),
            "sign_s_minus_half": sorted({int(np.sign(v - 0.5)) for v in series("boundary", "s")}),
            "window_membership": win, "factor_two_membership": f2,
        }
        ch = [v for v in rec["c_hat"] if v is not None]
        rec["c_hat_abs_spread"] = (max(ch) - min(ch)) if len(ch) == len(rows) else float("nan")
        rec["status_constant"] = len(set(rec["inverse_status"])) == 1
        rec["sign_constant"] = len(rec["sign_s_minus_half"]) == 1
        rec["classification_constant"] = len(set(win)) == 1 and len(set(f2)) == 1
        # NUMERICAL gate. Classification constancy alone is not stability: a 10 % move in R,
        # Xi_field or Xi_hat that never crosses a window or factor-of-two boundary would pass a
        # classification-only test. Every spread this function already computes is bound to the
        # tolerance already stored in this record (TOL_LINEARITY_REL = 1e-4, the frozen
        # forcing-linearity tolerance) — not a new threshold.
        _tol = vf.TOL_LINEARITY_REL
        _spreads = {k: rec[k] for k in ("R_rel_spread", "s_abs_spread", "c_field_abs_spread",
                                        "c_hat_abs_spread", "Xi_field_rel_spread",
                                        "Xi_hat_rel_spread")}
        rec["numerical_spreads"] = _spreads
        rec["numerical_stability_pass"] = bool(
            all(v is not None and np.isfinite(v) and abs(v) <= _tol for v in _spreads.values()))
        rec["pass"] = bool(
            rec["numerical_stability_pass"] and rec["status_constant"]
            and rec["sign_constant"] and rec["classification_constant"])
        ok = ok and rec["pass"]
        out["by_resolution"][str(S)] = rec
    out["pass"] = bool(ok)
    return out


def _node_sensitivity_summary(j):
    if j is None:
        return {"pass": False, "status": "NOT_EVALUATED",
                "not_evaluated_because": "NOT_RUN_UPSTREAM_EXECUTION_INVALID",
                "reason": ("Arm J was not run because execution validity had already failed "
                           "upstream on a control its solves cannot repair. NOT_EVALUATED is "
                           "neither a pass nor a failure OF THIS CONTROL; it is fail-closed so an "
                           "unevaluated control can never read as passed, and the disposition is "
                           "driven by the failed upstream control."),
                "classification_stable_under_node_offset": None}
    """Moving the frozen node surfaces is LOAD-BEARING, not decorative: the return-path result
    shows the nominal ports are not perfect equipotentials, so the two-node reduction is only
    defensible if the decision quantities and the CLASSIFICATION survive a frozen surface shift.
    No surface is ever chosen because it improves agreement with Xi_hat — the frozen pair is
    always offset 0, and these are reported around it."""
    rows = j["node_surface_sensitivity"]
    worst_R = max(max(abs(v) for v in r["R_rel_change_by_offset"]) for r in rows)
    worst_c = max(max(abs(v) for v in r["c_field_abs_change_by_offset"]) for r in rows)
    worst_xi = max(max(abs(v) for v in r["Xi_field_rel_change_by_offset"]) for r in rows)
    stable = all(len(set(r["in_window_by_offset"])) == 1
                 and len(set(r["factor_two_by_offset"])) == 1 for r in rows)
    return {
        "pass": bool(stable and worst_R <= vf.TOL_NODE_OFFSET_R_REL),
        "classification_stable_under_node_offset": stable,
        "worst_R_rel_change": worst_R,
        "worst_c_field_abs_change": worst_c,
        "worst_Xi_field_rel_change": worst_xi,
        "tol_R_rel": vf.TOL_NODE_OFFSET_R_REL,
        "frozen_surface_is_offset_0": True,
        "rows": rows,
    }


def _anisotropy(b):
    rows = []
    for S in vf.SCIENTIFIC_RESOLUTIONS:
        for level in ("high", "low"):
            gx = next(r["G"] for r in b["axial"] if r["S"] == S and r["level"] == level
                      and r["orientation"] == "x")
            gy = next(r["G"] for r in b["axial"] if r["S"] == S and r["level"] == level
                      and r["orientation"] == "y")
            rows.append({"S": S, "level": level, "G_x": gx, "G_y": gy,
                         "rel_difference": gy / gx - 1.0})
    return {
        "rows": rows,
        "worst_rel_difference": max(abs(r["rel_difference"]) for r in rows),
        "interpretation": (
            "WEAK BY CONSTRUCTION — read this before quoting it as an anisotropy result. The two "
            "orientations differ by transposing the duct's cross-section (y <-> z) while the "
            "forcing stays on +x. Exchanging y and z is an EXACT symmetry of the D3Q19 lattice, "
            "its weights and the TRT operator under x-forcing, so an exactly-zero difference is "
            "the expected outcome and confirms the implementation is consistent; it is NOT "
            "evidence that the lattice is isotropic in a direction the fixture actually probes. "
            "A genuinely informative rotation would drive the duct along a different lattice axis "
            "or a diagonal, which this kernel (body force in +x only) cannot do. Recorded as a "
            "consistency check, never as a passed anisotropy test."),
        "test_strength": "IMPLEMENTATION_CONSISTENCY_NOT_ANISOTROPY",
    }


def _arm_f(t, i, bnd, variant="mirror", swapped=False):
    out = {"truth_status": t.get("truth_status"),
           "inference_status": i.get("status")}
    quantitative = bool(t.get("quantitative_truth_available")) and i.get("status") == "ok"
    out["quantitative_comparison_emitted"] = quantitative
    if not quantitative:
        out["not_emitted_because"] = (
            "truth_status=%s, inference.status=%s — quantitative c/Xi comparisons are suppressed "
            "so a round-off-amplified or nonphysical value cannot enter an error statistic."
            % (t.get("truth_status"), i.get("status")))
        for k in ("c_hat_minus_c_field", "c_hat_minus_c_coupon", "Xi_hat_over_Xi_field",
                  "Xi_hat_over_Xi_coupon", "log2_factor_error_field", "Xi_coupon_over_Xi_field"):
            out[k] = None
        return _arm_f_network(out, t, bnd, variant, swapped)
    xf, xc, xh = t.get("Xi_field"), t.get("Xi_coupon"), i.get("Xi_hat")
    ch, cf, cc = i.get("c_hat"), t.get("c_field"), t.get("c_coupon")
    out["c_hat_minus_c_field"] = (ch - cf) if (ch is not None and cf is not None) else None
    out["c_hat_minus_c_coupon"] = (ch - cc) if (ch is not None and cc is not None) else None
    out["Xi_hat_over_Xi_field"] = (xh / xf) if (xh and xf) else None
    out["Xi_hat_over_Xi_coupon"] = (xh / xc) if (xh and xc) else None
    out["log2_factor_error_field"] = (
        abs(np.log2(xh / xf)) if (xh and xf and xh > 0 and xf > 0) else None)
    out["Xi_coupon_over_Xi_field"] = (xc / xf) if (xc and xf) else None
    return _arm_f_network(out, t, bnd, variant, swapped)


def _arm_f_network(out, t, bnd, variant, swapped):
    """Forward network predictions. Always emitted — for a structurally degenerate fixture the
    network's own answer (R = 1, s = 1/2 for ANY G_lat) is exactly what makes the observed
    residual scientifically useful."""
    if all(t.get(k) for k in ("g1_top", "g1_bot", "g2_top", "g2_bot")) and t.get("G_lat_field"):
        p = vf.network_prediction(t["g1_top"], t["g1_bot"], t["g2_top"], t["g2_bot"],
                                  t["G_lat_field"])
        out["network_field_R"] = p["R"]
        out["network_field_s"] = p["s"]
        out["network_field_R_residual"] = bnd["R"] - p["R"]
        out["network_field_s_residual"] = bnd["s"] - p["s"]
    a, bq = t.get("a_coupon"), t.get("b_coupon")
    if t.get("G_bridge_coupon") and a and bq:
        g4 = coupon_network_conductances(a, bq, variant, swapped)
        p = vf.network_prediction(*g4, t["G_bridge_coupon"])
        out["coupon_network_geometry"] = {"variant": variant, "swapped": bool(swapped),
                                          "conductance_order": list(g4)}
        out["network_coupon_R"] = p["R"]
        out["network_coupon_s"] = p["s"]
        out["network_coupon_R_residual"] = bnd["R"] - p["R"]
        out["network_coupon_s_residual"] = bnd["s"] - p["s"]
        if variant == "identical":
            out["identical_path_network_predicts_R_one"] = abs(p["R"] - 1.0) < 1e-12
            out["identical_path_network_predicts_s_half"] = abs(p["s"] - 0.5) < 1e-12
            out["axial_widening_artifact_R_minus_1"] = bnd["R"] - p["R"]
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(prog="puckworks.validation.slow.rp_d_lc_001")
    ap.add_argument("--backend", default="reference", choices=("reference", "taichi"))
    ap.add_argument("--arch", default="cpu")
    ap.add_argument("--dtype", default="f64")
    ap.add_argument("--mode", required=True,
                    choices=("arm_a", "coupons", "freeze", "primary", "arm_j", "assemble", "all"))
    ap.add_argument("--output", required=True)
    ap.add_argument("--jobs", type=int, default=1,
                    help="independent LB cases to run concurrently (processes)")
    a = ap.parse_args(argv)
    global _JOBS
    _JOBS = max(1, int(a.jobs))
    out = pathlib.Path(a.output)
    out.mkdir(parents=True, exist_ok=True)
    if a.dtype != "f64":
        raise SystemExit("PROTOCOL §5 freezes dtype=f64 for the reference backend")
    t0 = time.time()

    def log(msg):
        print("[%7.1fs] %s" % (time.time() - t0, msg), flush=True)

    if a.mode in ("arm_a", "all"):
        arm_a(a.backend, out, log)
    if a.mode in ("coupons", "all"):
        arm_b(a.backend, out, log)
    if a.mode == "all" and not FREEZE_JSON.exists():
        raise SystemExit("--mode all stops here: run `--mode freeze`, review and "
                         "COMMIT the aperture freeze, then `--mode primary`.")
    if a.mode == "freeze":
        freeze_apertures(out, log)
    if a.mode in ("primary", "all"):
        arm_cdefghi(a.backend, out, log)
    if a.mode in ("arm_j", "all"):
        arm_j(a.backend, out, log)
    if a.mode in ("assemble", "all"):
        assemble(out)
    log("done")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
