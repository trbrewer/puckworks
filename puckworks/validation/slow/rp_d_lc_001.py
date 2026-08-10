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
    j = json.loads((out_dir / "arm_j.json").read_text())

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
    lin_ok = all(v is not None and v <= vf.TOL_LINEARITY_REL for v in lin_R.values())
    mach_ok = all(r["mach"] <= vf.TOL_MACH for r in a["linearity"])
    mass_ok = all(r["plane_ptp_rel"] <= vf.TOL_MASS_REL for r in a["mass_conservation"]) and all(
        r["numerics"]["plane_flux_ptp_rel"] <= vf.TOL_MASS_REL for r in c["cases"])
    topo_ok = all(t["mirror_exact"] and t["single_connected"] and t["no_lateral_bypass"]
                  for t in a["topology"])
    plane_ok = all(abs(r["boundary"]["s_plane_delta"]) <= vf.TOL_PLANE_REL for r in c["cases"])
    grid_ok = len(c["grid_refinement"]["pairs"]) >= 3
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
    gate_rows = j["gate"]
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
        "low_mach_linearity": {
            "pass": bool(lin_ok and mach_ok),
            "max_mach": max(r["mach"] for r in a["linearity"]),
            "tol_mach": vf.TOL_MACH, "tol_linearity_rel": vf.TOL_LINEARITY_REL,
            "R_spread_by_resolution": lin_R,
            "conductance_spread_by_resolution": lin_C,
            "frozen_C_linearity_control": {
                "pass": lin_C_ok,
                "note": ("MIS-SPECIFIED AND FAILED AS WRITTEN — recorded, not hidden. The frozen "
                         "tolerance was placed on the CONDUCTANCE C across x0.5/x1/x2 forcing. "
                         "The measured drift is a genuine O(Re) inertial correction (Re ~ 1e-2), "
                         "not a defect: C rises monotonically and near-linearly with g. The "
                         "tranche's observable is the RATIO R, formed from an open and a blocked "
                         "run at the SAME g, in which that common-mode drift cancels; the "
                         "decision therefore uses R_spread_by_resolution. See PROTOCOL.md "
                         "erratum E2.")},
        },
        "mass_conservation": {"pass": mass_ok, "tol_rel": vf.TOL_MASS_REL,
                              "worst_plane_ptp_rel": max(
                                  [r["plane_ptp_rel"] for r in a["mass_conservation"]]
                                  + [r["numerics"]["plane_flux_ptp_rel"] for r in c["cases"]])},
        "topology": {
            "pass": bool(topo_ok and ret_ok and _node_sensitivity_summary(j)["pass"]),
            "masks_and_connectivity": topo_ok,
            "return_path_common_mode_bound_holds": ret_ok,
            "route_a_isolation_gate": {
                "pass": ret_ok,
                "tol_R_rel": vf.TOL_RETURN_PATH_R_REL,
                "tol_s_abs": vf.TOL_RETURN_PATH_S_ABS,
                "worst_R_rel_change": max(abs(r["R_rel_change"]) for r in gate_rows),
                "worst_s_abs_change": max(abs(r["s_abs_change"]) for r in gate_rows),
                "all_signs_preserved": all(r["sign_preserved"] for r in gate_rows),
                "rows": gate_rows,
                "coverage": j["coverage"],
                "statement": (
                    "The return path does NOT cancel exactly at the level of either absolute "
                    "conductance, because it influences the entrance region near the measurement "
                    "planes. Its effects on the open and blocked conductances are strongly "
                    "common-mode, so the pressure-normalised ratio R is insensitive to the tested "
                    "return-path perturbation to bounded numerical accuracy.")},
            "node_surface_sensitivity": _node_sensitivity_summary(j),
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
        "grid_refinement": {"pass": grid_ok,
                            "resolutions": list(vf.SCIENTIFIC_RESOLUTIONS)},
        "backend_cross_check": a["backend_cross_check"],
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
        # ARM F cross-model comparison
        t, i = r["truth"], r["inference"]
        r["comparison"] = _arm_f(t, i, r["boundary"])

    rec = {
        "source_commit": _git("rev-parse", "HEAD"),
        "source_tree": _git("rev-parse", "HEAD^{tree}"),
        "git_status_clean": (_git("status", "--porcelain") == ""),
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
                "the aperture voxels, so a common-mode return-path contribution cancels."),
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
        "arm_j": j,
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


def _node_sensitivity_summary(j):
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


def _arm_f(t, i, bnd):
    out = {}
    xf, xc, xh = t.get("Xi_field"), t.get("Xi_coupon"), i.get("Xi_hat")
    ch, cf, cc = i.get("c_hat"), t.get("c_field"), t.get("c_coupon")
    out["c_hat_minus_c_field"] = (ch - cf) if (ch is not None and cf is not None) else None
    out["c_hat_minus_c_coupon"] = (ch - cc) if (ch is not None and cc is not None) else None
    out["Xi_hat_over_Xi_field"] = (xh / xf) if (xh and xf) else None
    out["Xi_hat_over_Xi_coupon"] = (xh / xc) if (xh and xc) else None
    out["log2_factor_error_field"] = (
        abs(np.log2(xh / xf)) if (xh and xf and xh > 0 and xf > 0) else None)
    out["Xi_coupon_over_Xi_field"] = (xc / xf) if (xc and xf) else None
    if all(t.get(k) for k in ("g1_top", "g1_bot", "g2_top", "g2_bot")) and t.get("G_lat_field"):
        p = vf.network_prediction(t["g1_top"], t["g1_bot"], t["g2_top"], t["g2_bot"],
                                  t["G_lat_field"])
        out["network_field_R"] = p["R"]
        out["network_field_s"] = p["s"]
        out["network_field_R_residual"] = bnd["R"] - p["R"]
        out["network_field_s_residual"] = bnd["s"] - p["s"]
    if t.get("G_bridge_coupon") and t.get("c_coupon") is not None:
        a, bq = t.get("a_coupon"), t.get("b_coupon")
        if a and bq:
            p = vf.network_prediction(a, bq, bq, a, t["G_bridge_coupon"])
            out["network_coupon_R"] = p["R"]
            out["network_coupon_s"] = p["s"]
            out["network_coupon_R_residual"] = bnd["R"] - p["R"]
            out["network_coupon_s_residual"] = bnd["s"] - p["s"]
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
