"""Data producers for the viz layer — the named functions VizSpecs bind to.

Every function here returns plain JSON-able data (numbers / lists), NO matplotlib,
so the numbers a visual draws recompute from a named function (never hand-typed),
exactly as `public.schema.Producer` requires. Heavy producers (LB, 3D packs) keep
their grids SMALL and are marked slow on their VizSpec; nothing here is a physics
gate.
"""
from __future__ import annotations
import numpy as np

# The honesty policy for the 6+ process stages: each stage's renderable lens, the
# component that sources it, and the badge/evidence that ride along. Component
# keys MUST exist in spec.FIDELITY_CEILINGS (asserted in tests).
STAGE_LENS = [
    ("grind", "cameron2020 microstructure", "waszkiewicz2025",
     "OBSERVED", "reference", "measured PSD / microstructure tables"),
    ("packing", "brewer2026.pack_generator", "brewer2026.pack_generator",
     "EXPLORATORY_SIMULATION", "qualitative", "synthetic Boolean-sphere packing"),
    ("machine", "foster2025.machine_mode", "foster2025.machine_mode",
     "RECONSTRUCTED", "post-fit reconstruction", "pump+headspace P,Q (fitted t_shift)"),
    ("infiltration", "foster2025.infiltration", "foster2025.infiltration",
     "RECONSTRUCTED", "verification", "wetting front (CT-validated model)"),
    ("flow", "brewer2026.lb_reference", "brewer2026.lb_reference",
     "EXPLORATORY_SIMULATION", "verification", "Stokes flow, verification geometry"),
    ("extraction", "cameron2020.extraction_bdf", "waszkiewicz2025",
     "RECONSTRUCTED", "post-fit reconstruction", "dissolution kinetics"),
    ("bed_dynamics", "brewer2026.streamtube / N-tube", "ntube_union",
     "EXPLORATORY_SIMULATION", "qualitative", "channeling (one configuration)"),
    ("observables", "TDS/EY fractions", "waszkiewicz2025",
     "OBSERVED", "reference", "measured cup TDS/EY"),
]


def process_stages():
    """The 6-stage (grind->...->bed_dynamics) labelled map: which registered
    component sources each stage's lens and the badge that rides along. Cross-checks
    each stage name against the live registry so the schematic can't drift from it."""
    from ..registry import STAGES
    live = set(STAGES)
    stages = []
    for stage, comp, source_key, badge, evid, label in STAGE_LENS:
        stages.append(dict(stage=stage, component=comp, source_key=source_key,
                           badge=badge, evidence=evid, label=label,
                           in_registry=(stage in live)))
    return {"stages": stages, "n_registry_stages": len(live)}


def shot_traces(pressure_bar=9.0, stride=4):
    """One OBSERVED pressure-controlled shot: time, basket pressure, mass-flow, mass
    from the Waszkiewicz rig (data-only). Subsampled by `stride` for a light frame."""
    from .. import data as d
    tr = d.waszkiewicz_traces()[float(pressure_bar)]
    def col(name):
        a = tr[name][::stride]
        return [None if not np.isfinite(x) else float(x) for x in a]
    return {
        "t_s": col("time__s"),
        "pressure_bar": col("basket_pressure__bar"),
        "mass_flow_g_s": col("mass_flow_rate__g_per_s"),
        "mass_g": col("mass__g"),
        "source": f"waszkiewicz2025 {pressure_bar:g}-bar trace",
    }


def wetting_front(pressure_bar=9.0, k_SI=2.0e-13, phi_T=0.35, L_mm=12.0,
                  A_mm2=2827.0, stride=3):
    """foster2025.infiltration front s(t) under the recorded pressure history — a
    RECONSTRUCTION of the CT-validated front model (parameters nominal, labelled)."""
    from .. import data as d
    from ..models.foster2025.infiltration import front_from_pressure
    tr = d.waszkiewicz_traces()[float(pressure_bar)]
    t = tr["time__s"]; P = tr["basket_pressure__bar"]
    m = np.isfinite(t) & np.isfinite(P)
    t, P = t[m], np.clip(P[m], 0.0, None)
    out = front_from_pressure(t, P, k_SI=k_SI, phi_T=phi_T, L=L_mm * 1e-3,
                              A=A_mm2 * 1e-6)
    return {
        "t_s": [float(x) for x in t[::stride]],
        "front_mm": [float(x * 1e3) for x in out["s"][::stride]],
        "L_mm": float(L_mm),
        "t_saturate_s": out.get("t_saturate"),
        "params": {"k_SI": k_SI, "phi_T": phi_T, "L_mm": L_mm},
    }


def channeling_concentration(gs=1.1, N=200, P_bar=9.0):
    """N-tube channeling concentration — EXPLORATORY, ONE configuration. Returns the
    per-tube share trajectory + N_eff collapse (not a general instability)."""
    from ..harness import ntube_kappa_t_union
    r = ntube_kappa_t_union(gs=gs, N=N, P_bar=P_bar)
    cm = r.get("concentration_metrics", {})
    return {
        "time_s": [float(x) for x in r.get("time_s_trajectory", [])],
        "max_share": [float(x) for x in r.get("max_share_trajectory",
                                              r.get("max_share_traj", []))],
        "n_eff_over_N": cm.get("n_eff_over_N"),
        "collapse_time_s": r.get("collapse_time_s"),
        "config": {"gs": gs, "N": N, "P_bar": P_bar},
    }


def fines_migration(p0=5.0, p0_curve=(3.0, 4.0, 5.0, 6.0, 7.0, 8.0), t_end=300.0):
    """fasano2000_partI.fines_migration MECHANISM ILLUSTRATION: the compact-layer
    front s(t) at one pressure + the nonmonotone q_inf(p0) SHAPE. fasano-STRUCTURED —
    closures are OURS, zero identified params, NOT a coffee fit."""
    from ..models.fasano2000_partI.fines_migration import (
        simulate, q_infinity_curve, beta_from_fig87)
    beta = beta_from_fig87("beta1")
    sim = simulate(p0, beta, t_end=t_end)
    p0a = np.asarray(p0_curve, float)
    qinf = q_infinity_curve(p0a, beta)
    return {
        "t_s": [float(x) for x in sim["t"]],
        "q": [float(x) for x in sim["q"]],
        "compact_front_s": [float(x) for x in sim["s"]],
        "mass_balance": float(np.max(np.abs(sim["mass_balance"]))),
        "p0_bar": [float(x) for x in p0a],
        "q_inf": [float(x) for x in qinf],
        "note": "mechanism illustration; closures are ours, not the paper's; no coffee fit",
    }


def pack_porosity_slice(L=24, gs=1.3, voxel_um=40.0, seed=0):
    """A single mid-plane slice of a brewer2026.pack_generator Boolean-sphere pack,
    plus the sub-voxel heterogeneity field. SMALL grid; grains are synthetic, fines
    are a HETEROGENEITY FIELD (not resolved particles)."""
    from ..models.brewer2026.pack_generator import make_pack, hetero_field
    solid, meta = make_pack(L=L, voxel_um=voxel_um, gs=gs, seed=seed)
    z = L // 2
    het = hetero_field(L, corr_len=max(2, L // 8), seed=seed)   # (L,L) columnar field
    return {
        "solid_slice": solid[:, :, z].astype(int).tolist(),
        "hetero_slice": het.astype(float).tolist(),
        "phi": meta["phi"], "phis": meta["phis"], "gs": gs, "L": L,
    }


def stokes_channel_field(Nz=25, N=3, tau_plus=1.2, g=1.0e-6):
    """The Stokes channel VERIFICATION field: the analytic Poiseuille profile the
    brewer2026.lb_reference twin reproduces, plus that LB twin's measured agreement
    (err_pct). This is 'computed Stokes flow, verification geometry' — NOT the flow
    in a real puck. Fast."""
    from ..models.brewer2026.lb_reference import channel_case
    ver = channel_case(Nz=Nz, N=N)                 # LB-vs-analytic verification
    nu = (tau_plus - 0.5) / 3.0
    h = float(Nz - 2)                              # channel width between walls
    z = np.arange(Nz, dtype=float)
    zc = np.clip(z - 0.5, 0.0, h)                  # walls at 0.5 and Nz-1.5
    u = (g / (2.0 * nu)) * zc * (h - zc)           # analytic Stokes (parabolic) profile
    field = np.tile(u, (max(3, N), 1))             # (width, Nz) velocity slice
    return {"u_profile": u.tolist(), "u_field": field.tolist(), "z": z.tolist(),
            "u_max": float(u.max()),
            "lb_err_pct_vs_analytic": float(ver["err_pct"]),
            "Nz": Nz, "N": N,
            "note": "analytic Stokes channel; the LB twin verifies it (err_pct)"}
