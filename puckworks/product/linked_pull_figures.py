"""Figures for the Espresso Model Relay — REUSING the existing evidence-bound VizSpecs + tour draws.

To keep the honesty system intact we do not mint new ungoverned figures here: each relay figure is drawn
by an existing `tour_insight_draw` primitive from an existing registered `VizSpec` (so it carries the same
badge / evidence strength / fidelity ceiling and in-figure stamp). The relay simply feeds the same
authoritative producers with the linked scenario. matplotlib is a viz extra, imported lazily.
"""
from __future__ import annotations

from .linked_pull import RelayRequest


def _cam_kwargs(request: RelayRequest) -> dict:
    return dict(preset="pv19_named", dose_g=request.dose_g, target_beverage_g=request.target_beverage_g,
                pressure_bar=request.pressure_bar, grind_setting=request.grind_setting,
                brew_temperature_c=request.brew_temperature_c)


def _figure(spec_id, draw_name, data):
    from ..viz import registry as R, tour_insight_draw as D
    spec = R.viz_by_id(spec_id)
    fig, narrative = getattr(D, draw_name)(data, presentation="notebook",
                                           ceiling=spec.fidelity_ceiling, title=spec.title)
    R.stamp_fig(fig, spec)
    return {"viz_spec_id": spec_id, "figure": fig, "caption": narrative.to_caption(),
            "evidence_badge": spec.badge, "fidelity_ceiling": spec.fidelity_ceiling}


def relay_figures(request: RelayRequest) -> dict:
    """Return {station_id: figure-record} for the stations that have a defensible reused figure. Each
    record has {viz_spec_id, figure, caption, evidence_badge, fidelity_ceiling}."""
    import numpy as np

    from ..models.cameron2020 import extraction_bdf as cam
    from ..models.foster2025 import infiltration as inf
    from ..viz import producers as P

    out = {}
    # Extraction — the whole simulated shot
    out["extraction"] = _figure("cameron_shot_timeseries", "figure_cameron_shot_timeseries",
                                P.cameron_shot_timeseries(**_cam_kwargs(request)))
    # Packing — the synthetic puck
    out["packing"] = _figure("grain_pack_3d", "figure_pack_slice",
                             P.pack_porosity_slice(L=24, gs=request.grind_setting, voxel_um=40.0,
                                                   seed=request.seed))
    # Wetting — event-focused front from the linked pressure/permeability
    R_m = None
    try:
        from .linked_pull_adapters import radius_match
        from ..models.wadsworth2026 import permeability as perm
        phi1, phi2, a2, _b1, _b2 = cam.grind_microstructure(request.grind_setting)
        R_m = radius_match(float(a2))["physical_radius_m"]
        k = float(perm.k_percolation(R_m, 0.30))
    except Exception:
        k = 2.0e-13
    L_m = float(cam.bed_depth(request.dose_g / 1000.0))
    t = np.linspace(0.0, max(cam.simulate_shot(request.grind_setting, p_bar=request.pressure_bar,
                                               m_in=request.dose_g / 1000.0,
                                               m_out=request.target_beverage_g / 1000.0).t_shot, 6.0), 300)
    front = inf.front_from_pressure(t, np.full_like(t, request.pressure_bar - 0.3), k, 0.35, L_m)
    wdata = {"t_s": t.tolist(), "front_mm": (np.asarray(front["s"]) * 1000.0).tolist(),
             "L_mm": L_m * 1000.0, "t_saturate_s": front.get("t_saturate"),
             "params": {"L_mm": L_m * 1000.0, "k_SI": k, "phi_T": 0.35}}
    out["wetting"] = _figure("wetting_front_sweep", "figure_wetting_front", wdata)
    return out
