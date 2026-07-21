"""The Espresso Model Relay engine — one illustrative pull, passed from model to model.

`execute_illustrative_linked_pull(request, ...)` runs a directed ACYCLIC, one-way relay across the
registered components: each station calls authoritative model producers (never reimplemented equations),
hands typed `LinkedValue`s forward through documented adapters, records every hand-off as a `LinkRecord`,
and surfaces every assumption. Cameron provides a baseline but not the whole story; the result is a visible
trail from recipe → assumptions → several scientifically distinct readings of the same hypothetical pull.

This is PRODUCT orchestration, not a validated coupled model. The complete-relay hash proves determinism,
NOT scientific certainty. Rights are enforced before every producer (grudeva2025.reduced gets zero calls).

CLI:  python -m puckworks.product.linked_pull --preset illustrative_reference_v1 --mode fast --format json
"""
from __future__ import annotations

import dataclasses

from .. import validate as V
from . import linked_pull_adapters as AD
from . import linked_pull_manifest as MAN
from .linked_pull_records import (EXECUTED_STATUSES, AssumptionRecord, LinkedValue, LinkKind, LinkRecord,
                                   RELAY_SCHEMA_VERSION, ScenarioRelationship as SR, StageResult,
                                   StageStatus as ST, ValueOrigin as VO, artifact_hash, assumption_to_dict,
                                   link_to_dict, model_output_hash, value_to_dict)

REFERENCE_PRESET = "illustrative_reference_v1"

# NOTE: the relay no longer touches Cameron's C_S0 global. brewer2026.streamtube used to mutate it at
# import; that model-level defect is fixed (streamtube now passes its own c_s0 into simulate_shot(c_s0=)),
# so Cameron's baseline uses its own default (118) and streamtube uses its calibrated basis — no import
# order dependence, no global repair needed.

# stipulated defaults surfaced in the report (NOT user inputs, NOT model outputs)
STIPULATED_DEFAULTS = {
    "connected_porosity_phi_p": 0.30,       # A02 — tamped-puck connected porosity for permeability
    "water_accessible_porosity_phi_T": 0.35,  # A02 — wetting porosity (kept separate)
    "line_loss_bar": 0.3,                   # A04 — pump-outlet to bed-top loss
    "basket_area_mm2": 2827.0,              # 60 mm basket
    "random_seed": 42,
    "g10_viscosity_Xw_pct": 90.0,           # nearest in-domain point for the liquor-rheology diagnostic
}


@dataclasses.dataclass(frozen=True)
class RelayRequest:
    dose_g: float = 20.0
    target_beverage_g: float = 40.0
    grind_setting: float = 1.7            # Cameron/EK43 dial
    pressure_bar: float = 9.0             # target overpressure (bar-gauge)
    brew_temperature_c: float = 93.0
    heterogeneity: str = "moderate"       # low | moderate | high
    mode: str = "fast"                    # fast | extended
    seed: int = 42

    def __post_init__(self):
        if self.heterogeneity not in ("low", "moderate", "high"):
            raise ValueError(f"heterogeneity must be low|moderate|high, got {self.heterogeneity!r}")
        if self.mode not in ("fast", "extended"):
            raise ValueError(f"mode must be fast|extended, got {self.mode!r}")
        V.require_positive(self.dose_g, "dose_g")
        V.require_positive(self.target_beverage_g, "target_beverage_g")
        V.require_positive(self.pressure_bar, "pressure_bar")


_HETERO_SIGMA_REF = {"low": 0.35, "moderate": 0.60, "high": 0.90}   # streamtube sigma s_ref by level


class _Ctx:
    """Run accumulator — stages, links, assumptions, a value bus, and warnings."""
    def __init__(self, request: RelayRequest, execution_context: str):
        self.request = request
        self.execution_context = execution_context
        self.mode = request.mode
        self.stages: list[StageResult] = []
        self.links: list[LinkRecord] = []
        self.assumptions: dict[str, AssumptionRecord] = {}
        self.bus: dict = {}          # cross-station values (e.g. cached Cameron shot)
        self.warnings: list[str] = []

    def use_assumption(self, aid: str):
        self.assumptions.setdefault(aid, AD.assumption(aid))

    def add_link(self, edge: MAN.EdgeSpec, *, src_unit, tgt_unit, src_basis, tgt_basis,
                 conversion="", domain_status="IN_DOMAIN"):
        for aid in edge.assumption_ids:
            self.use_assumption(aid)
        self.links.append(LinkRecord(
            edge_id=edge.edge_id, source_component_id=edge.source_component_id,
            source_field=edge.source_field, target_component_id=edge.target_component_id,
            target_field=edge.target_field, kind=edge.kind, source_unit=src_unit, target_unit=tgt_unit,
            source_basis=src_basis, target_basis=tgt_basis, adapter_id=edge.adapter_id,
            assumption_ids=edge.assumption_ids, domain_status=domain_status, conversion=conversion))
        return edge.edge_id


def _rights_ok(cid: str, ctx: _Ctx) -> tuple[bool, str]:
    """Centralized rights preflight — LOCAL_PRIVATE uses may_execute_locally; public also needs batch +
    publish. grudeva2025.reduced is code-rights-blocked so this returns False (zero producer calls)."""
    from .. import rights
    d = rights.may_execute_locally(cid)
    if ctx.execution_context != "LOCAL_PRIVATE":
        pub = rights.may_execute_in_public_batch(cid)
        out = rights.may_publish_outputs(cid)
        allowed = d.allowed and pub.allowed and out.allowed
        return allowed, f"{d.severity}/{pub.severity}/{out.severity}"
    return d.allowed, d.severity


def _disp(cid):
    return MAN.COMPONENT_DISPOSITIONS[cid]


def _stage(cid, status, *, inputs=None, outputs=None, rel=None, rights_decision="clear",
           received=None, emitted=None, assumptions=None, findings=None, warnings=None, message=""):
    d = _disp(cid)
    station = next(s for s in MAN.STATIONS if s[0] == d.station_id)
    return StageResult(
        component_id=cid, station_id=d.station_id, public_heading=station[1], status=status,
        scenario_relationship=rel or d.scenario_relationship, rights_decision=rights_decision,
        inputs=inputs or [], outputs=outputs or [], links_received=received or [],
        links_emitted=emitted or [], assumption_ids=assumptions or [], domain_findings=findings or [],
        warnings=warnings or [], message=message)


def _lv(name, value, unit, basis, origin, **kw):
    return LinkedValue(name=name, value=value, unit=unit, basis=basis, origin=origin, **kw)


# ── the relay ─────────────────────────────────────────────────────────────────────────────
def execute_illustrative_linked_pull(request: RelayRequest, *, manifest_id: str = MAN.MANIFEST_ID,
                                     execution_context: str = "LOCAL_PRIVATE", mode: str | None = None):
    """Run the relay and return a serializable result dict. Deterministic for a fixed request."""
    if manifest_id != MAN.MANIFEST_ID:
        raise ValueError(f"unknown relay manifest {manifest_id!r}")
    if mode:
        request = dataclasses.replace(request, mode=mode)
    ctx = _Ctx(request, execution_context)

    # No global-state management is required: streamtube no longer mutates Cameron's C_S0 at import, so
    # the relay leaves no scientific global modified and does not perturb a later Full Laboratory Tour.
    _cache_cameron(ctx)          # cache the Cameron shot once
    _station_recipe(ctx)
    _station_grind(ctx)
    _station_packing(ctx)
    _station_machine(ctx)
    _station_wetting(ctx)
    _station_flow(ctx)
    _station_pore_scale(ctx)
    _station_extraction(ctx)
    _station_puck_change(ctx)
    _station_heterogeneous(ctx)
    _station_multisolute(ctx)
    _station_other_lenses(ctx)
    # every classified component with no station stage -> record its disposition explicitly
    _fill_unvisited(ctx)
    return _assemble(ctx, manifest_id)


def _cache_cameron(ctx: _Ctx):
    from ..models.cameron2020 import extraction_bdf as cam
    r = ctx.request
    ctx.bus["cam_micro"] = cam.grind_microstructure(r.grind_setting)          # (phi1,phi2,a2,bet1,bet2)
    ctx.bus["cam_shot"] = cam.simulate_shot(r.grind_setting, p_bar=r.pressure_bar,
                                            m_in=r.dose_g / 1000.0, m_out=r.target_beverage_g / 1000.0)
    ctx.bus["bed_depth_m"] = float(cam.bed_depth(r.dose_g / 1000.0))


# --- Station 0: recipe ---------------------------------------------------------------------
def _station_recipe(ctx: _Ctx):
    r = ctx.request
    inp = [
        _lv("dose", r.dose_g, "g", "as-entered", VO.USER_INPUT),
        _lv("target_beverage_mass", r.target_beverage_g, "g", "as-entered", VO.USER_INPUT),
        _lv("grind_setting", r.grind_setting, "EK43 dial", "Cameron dial space", VO.USER_INPUT),
        _lv("target_pressure", r.pressure_bar, "bar-gauge", "target overpressure", VO.USER_INPUT),
        _lv("brew_temperature", r.brew_temperature_c, "degC", "as-entered", VO.USER_INPUT),
        _lv("heterogeneity", r.heterogeneity, "", "level", VO.USER_INPUT),
    ]
    out = [_lv(k, v, u, "stipulated", VO.STIPULATED_DEFAULT)
           for k, v, u in (("connected_porosity_phi_p", STIPULATED_DEFAULTS["connected_porosity_phi_p"], ""),
                           ("water_accessible_porosity_phi_T", STIPULATED_DEFAULTS["water_accessible_porosity_phi_T"], ""),
                           ("basket_area", STIPULATED_DEFAULTS["basket_area_mm2"], "mm^2"),
                           ("random_seed", r.seed, ""))]
    ctx.stages.append(StageResult(
        component_id="recipe", station_id="recipe", public_heading="The recipe card", status=ST.EXECUTED,
        scenario_relationship=SR.SAME_SCENARIO, rights_decision="n/a", inputs=inp, outputs=out,
        links_received=[], links_emitted=[], assumption_ids=[], domain_findings=[], warnings=[],
        message="The hypothetical pull every model is asked to examine. Different models were NOT all "
                "developed for this exact coffee, grinder, basket, or machine."))


# --- Station 1: grind ----------------------------------------------------------------------
def _station_grind(ctx: _Ctx):
    cid = "wadsworth2026.grindmap"
    ok, sev = _rights_ok(cid, ctx)
    phi1, phi2, a2, _b1, _b2 = ctx.bus["cam_micro"]
    ins = [_lv("cameron_boulder_radius", a2, "m", "Cameron coarse-family radius", VO.MODEL_OUTPUT,
               source_component_id="cameron2020.extraction_bdf", source_field="boulder_radius_m"),
           _lv("cameron_fines_radius", 12e-6, "m", "Cameron fine-family radius", VO.MODEL_OUTPUT,
               source_component_id="cameron2020.extraction_bdf", source_field="fines_radius_m")]
    if not ok:
        ctx.stages.append(_stage(cid, ST.RIGHTS_BLOCKED, inputs=ins, rights_decision=sev)); return
    try:
        m = AD.radius_match(float(a2))
    except AD.AdapterDomainError as e:
        ctx.stages.append(_stage(cid, ST.DOMAIN_REJECTED, inputs=ins, findings=[str(e)],
                                 rights_decision=sev, message=str(e)))
        return
    edge = next(e for e in MAN.LINK_EDGES if e.edge_id == "cameron_radius_to_grindmap")
    eid = ctx.add_link(edge, src_unit="m", tgt_unit="m", src_basis="Cameron boulder radius",
                       tgt_basis="Wadsworth mean radius", conversion=m["conversion"])
    ctx.bus["physical_radius_m"] = m["physical_radius_m"]
    outs = [_lv("matched_dial", m["dial"], "Mahlkonig dial", "Wadsworth dial space", VO.ASSUMED_BRIDGE,
                assumption_ids=("A01",)),
            _lv("physical_radius", m["physical_radius_m"], "m", "Wadsworth mean radius", VO.ASSUMED_BRIDGE,
                assumption_ids=("A01",)),
            _lv("match_residual", m["residual_m"], "m", "matched - Cameron boulder", VO.DOCUMENTED_DERIVATION)]
    ctx.stages.append(_stage(cid, ST.EXECUTED_WITH_ASSUMPTIONS, inputs=ins, outputs=outs, received=[eid],
                             assumptions=["A01"], rights_decision=sev,
                             findings=[f"Cameron boulder radius {a2*1e6:.0f} um -> Mahlkonig dial "
                                       f"{m['dial']:.2f} (mean radius {m['physical_radius_m']*1e6:.0f} um)."]))


# --- Station 2: packing --------------------------------------------------------------------
def _station_packing(ctx: _Ctx):
    from ..models.wadsworth2026 import permeability as perm
    from ..viz import producers as P
    r = ctx.request
    phi_p = STIPULATED_DEFAULTS["connected_porosity_phi_p"]
    R = ctx.bus.get("physical_radius_m")
    # permeability
    cid = "wadsworth2026.permeability"
    ok, sev = _rights_ok(cid, ctx)
    if ok and R is not None:
        try:
            k = float(perm.k_percolation(R, phi_p))
            guard = AD.si_permeability_guard(k)
            ctx.bus["k_m2"] = k
            e1 = next(e for e in MAN.LINK_EDGES if e.edge_id == "grindmap_to_permeability")
            eid = ctx.add_link(e1, src_unit="m", tgt_unit="m", src_basis="Wadsworth mean radius",
                               tgt_basis="grain radius", conversion="identity")
            outs = [_lv("permeability", k, "m^2", "SI Darcy permeability (guarded)", VO.MODEL_OUTPUT,
                        source_component_id=cid, source_field="k_m2"),
                    _lv("connected_porosity", phi_p, "", "stipulated connected porosity", VO.STIPULATED_DEFAULT,
                        assumption_ids=("A02",))]
            ctx.use_assumption("A02")
            fnd = [f"k = {k:.2e} m^2 at connected porosity {phi_p:g}."]
            if k > 1e-12:
                fnd.append("This permeability is at the HIGH end for espresso — a consequence of matching a "
                           "coarse-family radius to a distribution mean (A01).")
            ctx.stages.append(_stage(cid, ST.EXECUTED_WITH_ASSUMPTIONS, outputs=outs, received=[eid],
                                     assumptions=["A02"], rights_decision=sev, findings=fnd))
        except AD.AdapterDomainError as e:
            ctx.stages.append(_stage(cid, ST.DOMAIN_REJECTED, findings=[str(e)], rights_decision=sev))
    else:
        ctx.stages.append(_stage(cid, ST.NOT_SELECTED, rights_decision=sev,
                                 message="no matched radius available (grind station did not link)"))
    # synthetic pack (deterministic geometry lens)
    cid = "brewer2026.pack_generator"
    ok, sev = _rights_ok(cid, ctx)
    if ok:
        try:
            data = P.pack_porosity_slice(L=24, gs=r.grind_setting, voxel_um=40.0, seed=r.seed)
            ctx.bus["pack_data"] = data
            e2 = next(e for e in MAN.LINK_EDGES if e.edge_id == "grindmap_to_pack")
            eid = ctx.add_link(e2, src_unit="m", tgt_unit="m", src_basis="Wadsworth mean radius",
                               tgt_basis="grain radius (via Cameron gs)", conversion="pack built at gs")
            ctx.use_assumption("A03")
            outs = [_lv("synthetic_void_fraction", data["phi"], "", "synthetic-pack void fraction",
                        VO.MODEL_OUTPUT, source_component_id=cid, source_field="phi", assumption_ids=("A03",)),
                    _lv("solid_fraction", data["phis"], "", "synthetic-pack solid fraction", VO.MODEL_OUTPUT,
                        source_component_id=cid, source_field="phis")]
            ctx.stages.append(_stage(cid, ST.EXECUTED, outputs=outs, received=[eid], assumptions=["A03"],
                                     rights_decision=sev,
                                     findings=[f"Synthetic Boolean-sphere pack, void fraction {data['phi']:.2f} "
                                               f"(SYNTHETIC geometry, not a scan; distinct from the permeability)."]))
        except Exception as e:  # noqa: BLE001 — a producer failure is a structured error, not fake science
            ctx.stages.append(_stage(cid, ST.EXECUTION_ERROR, rights_decision=sev, message=str(e)))
    else:
        ctx.stages.append(_stage(cid, ST.RIGHTS_BLOCKED, rights_decision=sev))


# --- Station 3: machine --------------------------------------------------------------------
def _station_machine(ctx: _Ctx):
    from ..models.foster2025 import machine_mode as mm
    r = ctx.request
    cid = "foster2025.machine_mode"
    ok, sev = _rights_ok(cid, ctx)
    if not ok:
        ctx.stages.append(_stage(cid, ST.RIGHTS_BLOCKED, rights_decision=sev)); return
    try:
        t_p, t_s = mm.reported_times()
        top = AD.pressure_node_top(r.pressure_bar, STIPULATED_DEFAULTS["line_loss_bar"])
        drop = AD.pressure_node_drop(r.pressure_bar)
        ctx.use_assumption("A04")
        shot = ctx.bus["cam_shot"]
        mean_flow = r.target_beverage_g / max(shot.t_shot, 1e-9)      # representative bev flow g/s
        ctx.bus["p_top_bar"] = top["p_top_bar"]
        ctx.bus["dP_bed_pa"] = drop["dP_bed_pa"]
        ctx.bus["mean_flow_g_s"] = mean_flow
        outs = [
            _lv("pump_ponding_time", t_p, "s", "Foster model time", VO.MODEL_OUTPUT, source_field="t_p"),
            _lv("saturation_time", t_s, "s", "Foster model time", VO.MODEL_OUTPUT, source_field="t_s"),
            _lv("bed_top_pressure", top["p_top_bar"], "bar-gauge", "headspace/bed-top node",
                VO.DOCUMENTED_DERIVATION, assumption_ids=("A04",)),
            _lv("bed_pressure_drop", drop["dP_bed_bar"], "bar-gauge", "across-bed node (applied once)",
                VO.DOCUMENTED_DERIVATION, assumption_ids=("A04",)),
            _lv("mean_beverage_flow", mean_flow, "g/s", "target mass / shot time", VO.DOCUMENTED_DERIVATION),
        ]
        ctx.stages.append(_stage(cid, ST.EXECUTED_WITH_ASSUMPTIONS, outputs=outs, assumptions=["A04"],
                                 rights_decision=sev,
                                 findings=[f"Pressure nodes assigned: bed-top {top['p_top_bar']:.1f} bar, "
                                           f"across-bed drop {drop['dP_bed_bar']:.1f} bar (once)."]))
    except Exception as e:  # noqa: BLE001
        ctx.stages.append(_stage(cid, ST.EXECUTION_ERROR, rights_decision=sev, message=str(e)))


# --- Station 4: wetting --------------------------------------------------------------------
def _station_wetting(ctx: _Ctx):
    import numpy as np
    from ..models.foster2025 import infiltration as inf
    cid = "foster2025.infiltration"
    ok, sev = _rights_ok(cid, ctx)
    if not ok:
        ctx.stages.append(_stage(cid, ST.RIGHTS_BLOCKED, rights_decision=sev)); return
    k = ctx.bus.get("k_m2")
    p_top = ctx.bus.get("p_top_bar", ctx.request.pressure_bar)
    L_mm = ctx.bus["bed_depth_m"] * 1000.0
    phi_T = STIPULATED_DEFAULTS["water_accessible_porosity_phi_T"]
    ins = []
    received = []
    if k is not None:
        e1 = next(e for e in MAN.LINK_EDGES if e.edge_id == "permeability_to_infiltration")
        received.append(ctx.add_link(e1, src_unit="m^2", tgt_unit="m^2", src_basis="Darcy permeability",
                                     tgt_basis="Darcy permeability", conversion="SI guarded"))
        ctx.use_assumption("A05")
        ins.append(_lv("permeability", k, "m^2", "from Wadsworth (cross-rig)", VO.MODEL_OUTPUT,
                       source_component_id="wadsworth2026.permeability", source_field="k_m2",
                       assumption_ids=("A05",)))
    e2 = next(e for e in MAN.LINK_EDGES if e.edge_id == "machine_to_infiltration")
    received.append(ctx.add_link(e2, src_unit="bar-gauge", tgt_unit="bar-gauge", src_basis="bed-top node",
                                 tgt_basis="pressure history", conversion="representative bed-top plateau"))
    try:
        L_m = ctx.bus["bed_depth_m"]
        A_m2 = STIPULATED_DEFAULTS["basket_area_mm2"] * 1e-6
        shot_t = ctx.bus["cam_shot"].t_shot
        t = np.linspace(0.0, max(shot_t, 6.0), 300)
        P_bar = np.full_like(t, float(p_top))
        out = inf.front_from_pressure(t, P_bar, k if k else 2.0e-13, phi_T, L_m, A=A_m2)
        ts = out.get("t_saturate")
        data = {"t_s": t.tolist(), "front_mm": (np.asarray(out["s"]) * 1000.0).tolist(),
                "L_mm": L_mm, "t_saturate_s": ts,
                "params": {"L_mm": L_mm, "k_SI": k, "phi_T": phi_T}}
        ctx.bus["saturation_time_s"] = ts
        ctx.bus["wetting_data"] = data
        shot = ctx.bus["cam_shot"]
        frac = (ts / shot.t_shot) if (ts and shot.t_shot) else None
        outs = [_lv("saturation_time", ts, "s", "sharp-front full-depth time", VO.MODEL_OUTPUT,
                    source_component_id=cid, source_field="t_saturate")]
        if frac is not None:
            outs.append(_lv("fraction_of_shot_before_saturation", 100.0 * frac, "%",
                            "modeled saturation / Cameron shot time", VO.DOCUMENTED_DERIVATION))
        ctx.stages.append(_stage(cid, ST.EXECUTED_WITH_ASSUMPTIONS, inputs=ins, outputs=outs,
                                 received=received, assumptions=["A05"], rights_decision=sev,
                                 findings=[f"Sharp front reaches the full {L_mm:.0f} mm bed in ~{ts:.2f} s."
                                           if ts else "no finite saturation time in window"]))
    except Exception as e:  # noqa: BLE001
        ctx.stages.append(_stage(cid, ST.EXECUTION_ERROR, inputs=ins, received=received,
                                 rights_decision=sev, message=str(e)))


# --- Station 5: flow -----------------------------------------------------------------------
def _station_flow(ctx: _Ctx):
    from ..models.wadsworth2026 import inertial as inrt
    from ..data import telisromero_viscosity_pas
    r = ctx.request
    # liquor-rheology diagnostic (reference constraint)
    cid = "sourcing2026.g10_liquor_rheology"
    ok, sev = _rights_ok(cid, ctx)
    mu = inrt.MU_92C
    if ok:
        try:
            T_K = r.brew_temperature_c + 273.15
            mu_liquor = float(telisromero_viscosity_pas(T_K, STIPULATED_DEFAULTS["g10_viscosity_Xw_pct"]))
            ctx.use_assumption("A07")
            outs = [_lv("liquor_viscosity", mu_liquor, "Pa*s", "Telis-Romero extract closure (diagnostic)",
                        VO.FITTED_REFERENCE, source_component_id=cid, source_field="viscosity_pa_s",
                        assumption_ids=("A07",)),
                    _lv("bulk_vs_water_ratio", mu_liquor / mu, "", "liquor / water viscosity", VO.DOCUMENTED_DERIVATION)]
            ctx.stages.append(_stage(cid, ST.EXECUTED, outputs=outs, assumptions=["A07"], rights_decision=sev,
                                     findings=[f"Bulk liquor viscosity ~{mu_liquor/mu:.2f}x water at the "
                                               f"dilute end (near-negligible for flow)."]))
        except Exception as e:  # noqa: BLE001
            ctx.stages.append(_stage(cid, ST.EXECUTION_ERROR, rights_decision=sev, message=str(e)))
    else:
        ctx.stages.append(_stage(cid, ST.RIGHTS_BLOCKED, rights_decision=sev))
    # inertial flow diagnostic
    cid = "wadsworth2026.inertial"
    ok, sev = _rights_ok(cid, ctx)
    k = ctx.bus.get("k_m2")
    if not ok:
        ctx.stages.append(_stage(cid, ST.RIGHTS_BLOCKED, rights_decision=sev)); return
    if k is None:
        ctx.stages.append(_stage(cid, ST.NOT_SELECTED, rights_decision=sev,
                                 message="no linked permeability")); return
    try:
        dP = ctx.bus.get("dP_bed_pa", V.bar_gauge_to_pa(r.pressure_bar))
        L = ctx.bus["bed_depth_m"]
        grad_p = dP / L
        kI = float(inrt.k_I(k, "zhou"))
        q_darcy = k * grad_p / mu
        q_forch = float(inrt.solve_q(k, kI, grad_p, mu=mu))
        Fo = float(inrt.forchheimer_number(k, q_forch, kI, mu=mu))
        ctx.use_assumption("A08")
        received = []
        e1 = next(e for e in MAN.LINK_EDGES if e.edge_id == "permeability_to_inertial")
        received.append(ctx.add_link(e1, src_unit="m^2", tgt_unit="m^2", src_basis="Darcy permeability",
                                     tgt_basis="Darcy permeability"))
        e2 = next(e for e in MAN.LINK_EDGES if e.edge_id == "machine_to_inertial")
        received.append(ctx.add_link(e2, src_unit="bar-gauge", tgt_unit="Pa", src_basis="across-bed node",
                                     tgt_basis="pressure gradient", conversion="grad_p = dP_bed / bed_depth"))
        e3 = next(e for e in MAN.LINK_EDGES if e.edge_id == "rheology_to_inertial")
        received.append(ctx.add_link(e3, src_unit="Pa*s", tgt_unit="Pa*s", src_basis="closure",
                                     tgt_basis="fluid viscosity", conversion="water viscosity used (bulk)"))
        regime = "inertial (Fo_F >> 1)" if Fo > 1 else ("transitional" if Fo > 0.1 else "Darcy-like")
        outs = [
            _lv("darcy_velocity", q_darcy, "m/s", "linear Darcy (naive)", VO.DOCUMENTED_DERIVATION),
            _lv("forchheimer_velocity", q_forch, "m/s", "inertial-corrected", VO.MODEL_OUTPUT,
                source_component_id=cid, source_field="q"),
            _lv("forchheimer_number", Fo, "", "Fo_F", VO.MODEL_OUTPUT, source_component_id=cid,
                source_field="Fo_F", assumption_ids=("A08",)),
            _lv("inertial_flow_ratio", q_forch / q_darcy if q_darcy else 0.0, "", "Forchheimer / Darcy",
                VO.DOCUMENTED_DERIVATION),
        ]
        fnd = [f"Fo_F = {Fo:.2g} ({regime}); inertial flow is {100*(1-q_forch/q_darcy):.0f}% below the "
               f"naive Darcy value."]
        if q_darcy > 0.1:
            fnd.append("The Darcy velocity is unphysically high here — a downstream signal that the A01 "
                       "radius match overstated permeability. Fo_F >> 1 flags exactly this.")
        ctx.stages.append(_stage(cid, ST.EXECUTED_WITH_ASSUMPTIONS, outputs=outs, received=received,
                                 assumptions=["A08"], rights_decision=sev, findings=fnd))
    except Exception as e:  # noqa: BLE001
        ctx.stages.append(_stage(cid, ST.EXECUTION_ERROR, rights_decision=sev, message=str(e)))


# --- Station 6: optional pore-scale --------------------------------------------------------
def _station_pore_scale(ctx: _Ctx):
    for cid in ("brewer2026.lb_reference", "brewer2026.lb_taichi"):
        ok, sev = _rights_ok(cid, ctx)
        if not ok:
            ctx.stages.append(_stage(cid, ST.RIGHTS_BLOCKED, rights_decision=sev)); continue
        if ctx.mode != "extended":
            ctx.stages.append(_stage(cid, ST.OPTIONAL_DEPENDENCY_UNAVAILABLE, rights_decision=sev,
                                     message="pore-scale relay runs only in extended mode"))
            continue
        if cid == "brewer2026.lb_taichi":
            try:
                import taichi  # noqa: F401
            except Exception:
                ctx.stages.append(_stage(cid, ST.OPTIONAL_DEPENDENCY_UNAVAILABLE, rights_decision=sev,
                                         message="taichi not installed"))
                continue
        try:
            from ..models.brewer2026 import lb_reference as lb, pack_generator as pg
            solid, meta = pg.make_pack(L=28, voxel_um=40.0, gs=ctx.request.grind_setting, seed=ctx.request.seed,
                                       verbose=False)
            res = lb.solve(solid, verbose=False, max_steps=6000)
            sig = pg.sigma_micro(res["ux"], solid)
            ctx.bus["lb_sigma"] = float(sig["sigma"])
            ctx.use_assumption("A03"); ctx.use_assumption("A10")
            e1 = next(e for e in MAN.LINK_EDGES if e.edge_id == "pack_to_lb")
            eid = ctx.add_link(e1, src_unit="bool voxels", tgt_unit="bool voxels", src_basis="synthetic pack",
                               tgt_basis="LB domain", conversion="deterministic solid mask")
            outs = [_lv("lb_permeability", res["k"], "lattice units", "LB (lattice-scale)", VO.MODEL_OUTPUT,
                        source_component_id=cid, source_field="k"),
                    _lv("lb_sigma", float(sig["sigma"]), "", "flow-heterogeneity from LB field",
                        VO.MODEL_OUTPUT, source_component_id=cid, source_field="sigma_micro",
                        assumption_ids=("A10",))]
            ctx.stages.append(_stage(cid, ST.EXECUTED_WITH_ASSUMPTIONS, outputs=outs, received=[eid],
                                     assumptions=["A03", "A10"], rights_decision=sev,
                                     findings=[f"LB flow through the synthetic pack: sigma = {sig['sigma']:.2f} "
                                               f"(lattice-scale, NOT the user's permeability)."]))
        except Exception as e:  # noqa: BLE001
            ctx.stages.append(_stage(cid, ST.EXECUTION_ERROR, rights_decision=sev, message=str(e)))


# --- Station 7: extraction baseline --------------------------------------------------------
def _station_extraction(ctx: _Ctx):
    cid = "cameron2020.extraction_bdf"
    ok, sev = _rights_ok(cid, ctx)
    if not ok:
        ctx.stages.append(_stage(cid, ST.RIGHTS_BLOCKED, rights_decision=sev)); return
    r = ctx.request
    shot = ctx.bus["cam_shot"]
    rep = AD.representative_pressure(r.pressure_bar)
    ctx.use_assumption("A06")
    e1 = next(e for e in MAN.LINK_EDGES if e.edge_id == "machine_to_extraction")
    eid = ctx.add_link(e1, src_unit="bar-gauge", tgt_unit="bar-gauge", src_basis="dynamic P(t)",
                       tgt_basis="scalar representative", conversion=rep["conversion"])
    outs = [
        _lv("extraction_yield", shot.EY, "%", "cup EY (Cameron)", VO.MODEL_OUTPUT, source_component_id=cid,
            source_field="EY"),
        _lv("strength_tds", shot.tds, "%", "TDS (Cameron)", VO.MODEL_OUTPUT, source_component_id=cid,
            source_field="tds"),
        _lv("shot_time", shot.t_shot, "s", "modeled shot time", VO.MODEL_OUTPUT, source_component_id=cid,
            source_field="t_shot"),
        _lv("dissolved_mass", float(shot.m_cup[-1] * 1000.0), "g", "cumulative dissolved (cup)",
            VO.MODEL_OUTPUT, source_component_id=cid, source_field="m_cup"),
    ]
    ctx.bus["ey_pct"] = shot.EY; ctx.bus["tds_pct"] = shot.tds; ctx.bus["shot_time_s"] = shot.t_shot
    ctx.stages.append(_stage(cid, ST.EXECUTED_WITH_ASSUMPTIONS, outputs=outs, received=[eid],
                             assumptions=["A06"], rights_decision=sev,
                             findings=[f"Baseline: EY {shot.EY:.1f}%, TDS {shot.tds:.1f}%, shot "
                                       f"{shot.t_shot:.0f} s. EY/TDS are not flavour."]))


# --- Station 8: puck change ----------------------------------------------------------------
def _station_puck_change(ctx: _Ctx):
    import numpy as np
    shot = ctx.bus["cam_shot"]
    r = ctx.request
    # waszkiewicz one-way branch
    cid = "waszkiewicz2025.poroelastic"
    ok, sev = _rights_ok(cid, ctx)
    if ok:
        try:
            from ..models.waszkiewicz2025 import poroelastic as wz
            Pc, Qc = wz.published_calibration()
            frac = AD.dissolution_fraction(shot.m_cup, r.dose_g / 1000.0)
            ctx.use_assumption("A09")
            Q = wz.q_dynamic_from_md(r.pressure_bar, Pc, Qc, frac["md_g"], frac["dose_g"])
            Q = np.asarray(Q, float)
            Q = Q[np.isfinite(Q)]
            e1 = next(e for e in MAN.LINK_EDGES if e.edge_id == "cameron_to_waszkiewicz")
            eid = ctx.add_link(e1, src_unit="g", tgt_unit="", src_basis="cumulative dissolved mass",
                               tgt_basis="dissolution fraction", conversion=frac["conversion"])
            trend = 100.0 * (Q[-1] - Q[0]) / Q[0] if len(Q) > 1 and Q[0] else 0.0
            outs = [_lv("bed_flow_start", float(Q[0]), "g/s", "one-way coupled flow", VO.MODEL_OUTPUT,
                        source_component_id=cid, source_field="q_dynamic_from_md", assumption_ids=("A09",)),
                    _lv("bed_flow_end", float(Q[-1]), "g/s", "one-way coupled flow", VO.MODEL_OUTPUT,
                        source_component_id=cid, source_field="q_dynamic_from_md", assumption_ids=("A09",)),
                    _lv("flow_trend_pct", trend, "%", "end vs start", VO.DOCUMENTED_DERIVATION)]
            ctx.stages.append(_stage(cid, ST.EXECUTED_WITH_ASSUMPTIONS, outputs=outs, received=[eid],
                                     assumptions=["A09"], rights_decision=sev,
                                     message="NEW one-way Puckworks coupling; NOT validated by the "
                                             "Waszkiewicz paper; not fed back into Cameron.",
                                     findings=[f"Coupled bed flow trends {trend:+.0f}% over the shot."]))
        except Exception as e:  # noqa: BLE001
            ctx.stages.append(_stage(cid, ST.EXECUTION_ERROR, rights_decision=sev, message=str(e)))
    else:
        ctx.stages.append(_stage(cid, ST.RIGHTS_BLOCKED, rights_decision=sev))
    # coupled_kappa_t stress test
    cid = "brewer2026.coupled_kappa_t"
    ok, sev = _rights_ok(cid, ctx)
    if ok:
        try:
            from ..models.brewer2026 import coupled_kappa_t as ck
            res = ck.simulate(P_bar=r.pressure_bar, branches=("extraction", "swelling", "compaction"))
            outs = [_lv("kappa_over_kappa0_end", float(res["kappa_ck"][-1]), "", "combined resistance factor",
                        VO.MODEL_OUTPUT, source_component_id=cid, source_field="kappa_ck"),
                    _lv("pore_space_clamped", bool(res["clamped"]), "", "over-closure flag", VO.MODEL_OUTPUT,
                        source_component_id=cid, source_field="clamped")]
            msg = ("Stress-test composition. Pore space CLAMPED (over-closure shown, not tuned away)."
                   if res["clamped"] else "Stress-test composition branch.")
            ctx.stages.append(_stage(cid, ST.EXECUTED_WITH_ASSUMPTIONS, outputs=outs, rights_decision=sev,
                                     message=msg, findings=[f"Combined kappa/kappa0 -> {res['kappa_ck'][-1]:.2f}."]))
        except Exception as e:  # noqa: BLE001
            ctx.stages.append(_stage(cid, ST.EXECUTION_ERROR, rights_decision=sev, message=str(e)))
    else:
        ctx.stages.append(_stage(cid, ST.RIGHTS_BLOCKED, rights_decision=sev))
    # mo swelling
    cid = "mo2023_2.swelling"
    ok, sev = _rights_ok(cid, ctx)
    if ok:
        try:
            from ..models.mo2023_2 import swelling as sw
            d = sw.flow_decay("M", np.linspace(0.0, max(shot.t_shot, 20.0), 24))
            outs = [_lv("flow_decay_ratio", float(d["q_rel"][-1]), "", "q(end)/q(0)", VO.MODEL_OUTPUT,
                        source_component_id=cid, source_field="q_rel")]
            ctx.stages.append(_stage(cid, ST.EXECUTED_WITH_ASSUMPTIONS, outputs=outs, rights_decision=sev,
                                     findings=[f"Swelling alone lowers flow to {100*d['q_rel'][-1]:.0f}% of "
                                               f"its start over the shot."]))
        except Exception as e:  # noqa: BLE001
            ctx.stages.append(_stage(cid, ST.EXECUTION_ERROR, rights_decision=sev, message=str(e)))
    else:
        ctx.stages.append(_stage(cid, ST.RIGHTS_BLOCKED, rights_decision=sev))
    # fasano fines migration
    cid = "fasano2000_partI.fines_migration"
    ok, sev = _rights_ok(cid, ctx)
    if ok:
        try:
            from ..viz import producers as P
            d = P.fines_migration()
            outs = [_lv("mass_balance", d["mass_balance"], "", "fines mass balance", VO.MODEL_OUTPUT,
                        source_component_id=cid, source_field="mass_balance")]
            ctx.stages.append(_stage(cid, ST.EXECUTED, outputs=outs, rel=SR.NATIVE_REFERENCE,
                                     rights_decision=sev,
                                     message="Alternative resistance mechanism (fines migration); closures "
                                             "are ours, not the paper's.",
                                     findings=["Another mechanism that could produce changing flow."]))
        except Exception as e:  # noqa: BLE001
            ctx.stages.append(_stage(cid, ST.EXECUTION_ERROR, rights_decision=sev, message=str(e)))
    else:
        ctx.stages.append(_stage(cid, ST.RIGHTS_BLOCKED, rights_decision=sev))
    # lee guarded (reference only)
    cid = "lee2023.feedback"
    ok, sev = _rights_ok(cid, ctx)
    if ok:
        try:
            from ..models.lee2023 import feedback as lee
            lr = lee.simulate(r.grind_setting)
            ctx.stages.append(_stage(cid, ST.REFERENCE_ONLY, rel=SR.NATIVE_REFERENCE, rights_decision=sev,
                                     outputs=[_lv("ey_total", lr["EY_tot_pct"], "%", "imposed-density case",
                                                  VO.FITTED_REFERENCE, source_component_id=cid,
                                                  source_field="EY_tot_pct")],
                                     message="Guarded: its headline fine-grind decline needs an unphysical "
                                             "imposed density; shown as a hypothesis, not validated."))
        except Exception as e:  # noqa: BLE001
            ctx.stages.append(_stage(cid, ST.EXECUTION_ERROR, rights_decision=sev, message=str(e)))
    else:
        ctx.stages.append(_stage(cid, ST.RIGHTS_BLOCKED, rights_decision=sev))


# --- Station 9: heterogeneous extraction ---------------------------------------------------
def _station_heterogeneous(ctx: _Ctx):
    cid = "brewer2026.streamtube"
    ok, sev = _rights_ok(cid, ctx)
    if not ok:
        ctx.stages.append(_stage(cid, ST.RIGHTS_BLOCKED, rights_decision=sev)); return
    try:
        from ..models.brewer2026 import streamtube as st
        r = ctx.request
        resp = st.EYResponse(gs=r.grind_setting, p_bar=r.pressure_bar, m_in=r.dose_g / 1000.0,
                             m_out=r.target_beverage_g / 1000.0)
        if ctx.mode == "extended" and "lb_sigma" in ctx.bus:
            sigma = ctx.bus["lb_sigma"]; origin = "LB-derived (synthetic pack)"; oid = "lb_sigma"
            ctx.use_assumption("A10")
            e1 = next(e for e in MAN.LINK_EDGES if e.edge_id == "lb_to_streamtube")
            received = [ctx.add_link(e1, src_unit="", tgt_unit="", src_basis="LB flow field",
                                     tgt_basis="ensemble sigma", conversion="sigma_micro")]
        else:
            sigma = st.sigma_closure_power(r.grind_setting, _HETERO_SIGMA_REF[r.heterogeneity], 1.0)
            origin = "streamtube calibrated closure"; oid = "sigma_closure"; received = []
        e2 = next(e for e in MAN.LINK_EDGES if e.edge_id == "cameron_to_streamtube")
        received.append(ctx.add_link(e2, src_unit="EY response", tgt_unit="EY response",
                                     src_basis="Cameron response", tgt_basis="Cameron response"))
        ey_h = float(resp.ey_of_k(1.0)); ey_e = float(resp.ey_ensemble(sigma)); dfc = float(resp.deficit(sigma))
        outs = [_lv("homogeneous_ey", ey_h, "%", "Cameron-response EY", VO.MODEL_OUTPUT,
                    source_component_id=cid, source_field="ey_of_k"),
                _lv("heterogeneous_ey", ey_e, "%", "ensemble EY", VO.MODEL_OUTPUT, source_component_id=cid,
                    source_field="ey_ensemble"),
                _lv("ey_deficit_pct", 100.0 * dfc, "%", "relative EY deficit", VO.DOCUMENTED_DERIVATION),
                _lv("sigma", sigma, "", origin, VO.MODEL_OUTPUT, source_component_id=cid, source_field=oid,
                    assumption_ids=("A10",) if oid == "lb_sigma" else ())]
        ctx.stages.append(_stage(cid, ST.EXECUTED, rel=SR.SAME_SCENARIO, outputs=outs, received=received,
                                 rights_decision=sev,
                                 findings=[f"Uneven paths (sigma {sigma:.2f}, {origin}) drop EY from "
                                           f"{ey_h:.1f}% to {ey_e:.1f}% ({100*dfc:.0f}% deficit)."]))
    except Exception as e:  # noqa: BLE001
        ctx.stages.append(_stage(cid, ST.EXECUTION_ERROR, rights_decision=sev, message=str(e)))


# --- Station 10: multi-solute --------------------------------------------------------------
def _station_multisolute(ctx: _Ctx):
    from ..models.pannusch2024 import closures as pc
    r = ctx.request
    T_K = r.brew_temperature_c + 273.15
    # closures (executed): per-solute diffusion coefficients -> release-clock ordering
    cid = "pannusch2024.closures"
    ok, sev = _rights_ok(cid, ctx)
    diffs = {}
    if ok:
        try:
            for s in ("caffeine", "trigonelline", "5CQA"):
                diffs[s] = float(pc.diffusion_coeff(T_K, s))
            outs = [_lv(f"Deff_{s}", diffs[s], "m^2/s", "diffusion coefficient", VO.MODEL_OUTPUT,
                        source_component_id=cid, source_field="diffusion_coeff") for s in diffs]
            ctx.stages.append(_stage(cid, ST.EXECUTED, rel=SR.NATIVE_REFERENCE, outputs=outs,
                                     rights_decision=sev,
                                     findings=["Per-solute diffusion coefficients set different release "
                                               "clocks at the same temperature."]))
        except Exception as e:  # noqa: BLE001
            ctx.stages.append(_stage(cid, ST.EXECUTION_ERROR, rights_decision=sev, message=str(e)))
    else:
        ctx.stages.append(_stage(cid, ST.RIGHTS_BLOCKED, rights_decision=sev))
    # solver (reduced, adapted): representative-flow-driven release timing (A11/A12)
    cid = "pannusch2024.solver"
    ok, sev = _rights_ok(cid, ctx)
    if not ok:
        ctx.stages.append(_stage(cid, ST.RIGHTS_BLOCKED, rights_decision=sev)); return
    mean_flow = ctx.bus.get("mean_flow_g_s", r.target_beverage_g / max(ctx.bus["shot_time_s"], 1e-9))
    rep = AD.representative_flow(mean_flow)
    ctx.use_assumption("A11"); ctx.use_assumption("A12")
    e1 = next(e for e in MAN.LINK_EDGES if e.edge_id == "machine_to_pannusch")
    eid = ctx.add_link(e1, src_unit="g/s", tgt_unit="mL/s", src_basis="machine flow trace",
                       tgt_basis="representative flow", conversion=rep["conversion"])
    # normalized release-clock proxy from diffusion timescale tau ~ d^2/Deff (documented reduction)
    d32 = 330e-6
    clocks = {s: (d32 * d32) / (6.0 * diffs[s]) for s in diffs} if diffs else {}
    order = sorted(clocks, key=clocks.get)
    outs = [_lv("representative_flow", rep["flow_mL_s"], "mL/s", "reduced machine flow",
                VO.DOCUMENTED_DERIVATION, assumption_ids=("A11",))]
    outs += [_lv(f"release_timescale_{s}", clocks[s], "s", "tau ~ d^2/(6 Deff)", VO.DOCUMENTED_DERIVATION)
             for s in clocks]
    ctx.stages.append(_stage(cid, ST.EXECUTED_WITH_ASSUMPTIONS, rel=SR.ADAPTED_SCENARIO, outputs=outs,
                             received=[eid], assumptions=["A11", "A12"], rights_decision=sev,
                             message="Reduced multi-solute branch: release-clock ordering from the "
                                     "pannusch closures, not absolute per-solute cup yields (extractable "
                                     "fractions unmeasured).",
                             findings=[f"Release order (fastest first): {', '.join(order)}."
                                       if order else "closures unavailable"]))


# --- Station 11: other lenses --------------------------------------------------------------
def _station_other_lenses(ctx: _Ctx):
    import numpy as np
    r = ctx.request
    shot_t = ctx.bus.get("shot_time_s", 25.0)
    # romancorrochano normalized release by MW class
    cid = "romancorrochano2017.extraction"
    ok, sev = _rights_ok(cid, ctx)
    if ok:
        try:
            from ..models.romancorrochano2017 import extraction as rc
            grind_key = "PsiC"
            t = np.linspace(0.5, max(shot_t, 10.0), 30)
            rel = {mw: float(rc.sphere_release(rc.deff_of(grind_key, mw, r.brew_temperature_c),
                                               3.0e-4, t)[-1]) for mw in ("low", "high")}
            outs = [_lv(f"released_frac_{mw}", rel[mw], "fraction", "normalized release by MW", VO.MODEL_OUTPUT,
                        source_component_id=cid, source_field="sphere_release") for mw in rel]
            ctx.stages.append(_stage(cid, ST.EXECUTED_WITH_ASSUMPTIONS, rel=SR.NEAREST_VALID_CASE, outputs=outs,
                                     rights_decision=sev,
                                     message="Nearest valid grind case; normalized release, NOT absolute EY.",
                                     findings=[f"Small molecules release faster than large "
                                               f"({rel['low']:.2f} vs {rel['high']:.2f} at shot end)."]))
        except Exception as e:  # noqa: BLE001
            ctx.stages.append(_stage(cid, ST.EXECUTION_ERROR, rights_decision=sev, message=str(e)))
    else:
        ctx.stages.append(_stage(cid, ST.RIGHTS_BLOCKED, rights_decision=sev))
    # moroney early/plateau/washthrough
    cid = "moroney2016.surrogate"
    ok, sev = _rights_ok(cid, ctx)
    if ok:
        try:
            from ..models.moroney2016 import surrogate as mo
            half = float(mo.washthrough_halfmax_time())
            ctx.stages.append(_stage(cid, ST.EXECUTED_WITH_ASSUMPTIONS, rel=SR.ADAPTED_SCENARIO,
                                     outputs=[_lv("washthrough_halfmax_tau", half, "dimensionless",
                                                  "nondimensional wash-through time", VO.MODEL_OUTPUT,
                                                  source_component_id=cid, source_field="washthrough_halfmax_time")],
                                     rights_decision=sev,
                                     message="Qualitative extraction-clock lens (early release, plateau, "
                                             "wash-through).",
                                     findings=[f"Wash-through half-max at tau ~ {half:.2f} (nondimensional)."]))
        except Exception as e:  # noqa: BLE001
            ctx.stages.append(_stage(cid, ST.EXECUTION_ERROR, rights_decision=sev, message=str(e)))
    else:
        ctx.stages.append(_stage(cid, ST.RIGHTS_BLOCKED, rights_decision=sev))
    # mo coupled_bed depth-resolved
    cid = "mo2023_2.coupled_bed"
    ok, sev = _rights_ok(cid, ctx)
    if ok:
        try:
            from ..models.mo2023_2 import coupled_bed as cb
            q_ml = ctx.bus.get("mean_flow_g_s", 1.5)
            bd = cb.simulate_bed("M", q_mL_s=max(q_ml, 0.5), dose_g=r.dose_g, t_end=min(max(shot_t, 10.0), 40.0))
            ctx.stages.append(_stage(cid, ST.EXECUTED_WITH_ASSUMPTIONS, rel=SR.ADAPTED_SCENARIO,
                                     outputs=[_lv("yield_frac_end", float(bd["yield_frac"][-1]), "fraction",
                                                  "eluted / extractable inventory", VO.MODEL_OUTPUT,
                                                  source_component_id=cid, source_field="yield_frac")],
                                     rights_decision=sev,
                                     message="Depth-resolved extraction lens (normalized; cup-mass/inventory "
                                             "limits apply).",
                                     findings=[f"Depth-resolved normalized yield reaches "
                                               f"{100*bd['yield_frac'][-1]:.0f}% of the extractable pool."]))
        except Exception as e:  # noqa: BLE001
            ctx.stages.append(_stage(cid, ST.EXECUTION_ERROR, rights_decision=sev, message=str(e)))
    else:
        ctx.stages.append(_stage(cid, ST.RIGHTS_BLOCKED, rights_decision=sev))
    # liang equilibrium ceiling / retained-liquid
    cid = "liang2021.desorption"
    ok, sev = _rights_ok(cid, ctx)
    if ok:
        try:
            from ..models.liang2021 import desorption as lg
            e_eq = float(lg.E_equilibrium())
            ctx.stages.append(_stage(cid, ST.EXECUTED, rel=SR.NATIVE_REFERENCE,
                                     outputs=[_lv("equilibrium_ey_ceiling", 100.0 * e_eq, "%",
                                                  "equilibrium EY ceiling (oven-dry basis)", VO.FITTED_REFERENCE,
                                                  source_component_id=cid, source_field="E_equilibrium")],
                                     rights_decision=sev,
                                     message="Equilibrium ceiling / retained-liquid bookkeeping — a DIFFERENT "
                                             "concept from Cameron's soluble-inventory ceiling (not a swap-in).",
                                     findings=[f"Immersion-equilibrium EY ceiling ~{100*e_eq:.0f}% "
                                               f"(different bookkeeping from the cup EY above)."]))
        except Exception as e:  # noqa: BLE001
            ctx.stages.append(_stage(cid, ST.EXECUTION_ERROR, rights_decision=sev, message=str(e)))
    else:
        ctx.stages.append(_stage(cid, ST.RIGHTS_BLOCKED, rights_decision=sev))
    # grudeva — rights-blocked, ZERO calls
    cid = "grudeva2025.reduced"
    ok, sev = _rights_ok(cid, ctx)
    ctx.stages.append(_stage(cid, ST.RIGHTS_BLOCKED, rel=SR.NOT_EXECUTED, rights_decision=sev,
                             message="Rights-blocked (#73): shown in the chain map, receives ZERO model and "
                                     "adapter calls. It could have been a reduced whole-shot extraction lens."))


def _fill_unvisited(ctx: _Ctx):
    """Any classified component with no stage yet (reference-only sources) gets an explicit disposition."""
    seen = {s.component_id for s in ctx.stages}
    for cid, d in MAN.COMPONENT_DISPOSITIONS.items():
        if cid in seen:
            continue
        ctx.stages.append(_stage(cid, d.intended_status, rel=d.scenario_relationship,
                                 message=d.role))


# ── assembly + serialization ────────────────────────────────────────────────────────────────
def _assemble(ctx: _Ctx, manifest_id: str) -> dict:
    from ..viz.registry import source_commit
    from . import linked_pull_narrative as NAR
    for s in ctx.stages:
        s.narrative = NAR.stage_narrative(s)
    executed = [s for s in ctx.stages if s.status in EXECUTED_STATUSES]
    counts = _counts(ctx)
    stages_d = [_stage_to_dict(s) for s in ctx.stages]
    result = {
        "report": "puckworks-espresso-model-relay",
        "schema_version": RELAY_SCHEMA_VERSION,
        "contract_schema_version": _contract_version(),
        "manifest_id": manifest_id,
        "source_commit": source_commit(),
        "execution_context": ctx.execution_context,
        "mode": ctx.mode,
        "positioning": ("An illustrative, assumption-rich linked pull across separate models. This is NOT "
                        "a validated coupled simulation, digital twin, or taste predictor."),
        "request": dataclasses.asdict(ctx.request),
        "stipulated_defaults": STIPULATED_DEFAULTS,
        "stages": stages_d,
        "links": [link_to_dict(link) for link in ctx.links],
        "assumptions": [assumption_to_dict(a) for a in _sorted_assumptions(ctx)],
        "counts": counts,
        "component_dispositions": {cid: d.role for cid, d in MAN.COMPONENT_DISPOSITIONS.items()},
        "warnings": ctx.warnings,
        "hash_note": ("model_output_hash proves the numbers are deterministic; artifact_hash covers the "
                      "whole record. NEITHER is a validation or scientific-certainty hash."),
    }
    result["model_output_hash"] = model_output_hash(ctx.stages)
    result["artifact_hash"] = artifact_hash(result)
    return result


def _counts(ctx: _Ctx) -> dict:
    from collections import Counter
    c = Counter(s.status.value for s in ctx.stages if s.component_id != "recipe")
    link_kinds = Counter(link.kind.value for link in ctx.links)
    executed = [s for s in ctx.stages if s.status in EXECUTED_STATUSES and s.component_id != "recipe"]
    handoffs = [link for link in ctx.links if link.kind in (
        LinkKind.DIRECT_MODEL_OUTPUT, LinkKind.DOCUMENTED_ADAPTER, LinkKind.ILLUSTRATIVE_ASSUMPTION,
        LinkKind.OPTIONAL_SLOW_PATH)]
    return {
        "components_executed": len(executed),
        "cross_component_handoffs": len(handoffs),
        "direct_handoffs": link_kinds.get("DIRECT_MODEL_OUTPUT", 0),
        "documented_adapters": link_kinds.get("DOCUMENTED_ADAPTER", 0),
        "illustrative_assumptions": link_kinds.get("ILLUSTRATIVE_ASSUMPTION", 0),
        "shared_input_or_diagnostic": link_kinds.get("SHARED_INPUT_ONLY", 0) + link_kinds.get("DIAGNOSTIC_ONLY", 0),
        "assumptions_introduced": len(ctx.assumptions),
        "by_status": dict(c),
    }


def _sorted_assumptions(ctx: _Ctx) -> list:
    return [ctx.assumptions[k] for k in sorted(ctx.assumptions)]


def _stage_to_dict(s: StageResult) -> dict:
    nar = s.narrative
    return {
        "component_id": s.component_id, "station_id": s.station_id, "public_heading": s.public_heading,
        "status": s.status.value, "scenario_relationship": s.scenario_relationship.value,
        "rights_decision": s.rights_decision,
        "inputs": [value_to_dict(v) for v in s.inputs], "outputs": [value_to_dict(v) for v in s.outputs],
        "links_received": s.links_received, "links_emitted": s.links_emitted,
        "assumption_ids": s.assumption_ids, "domain_findings": s.domain_findings, "warnings": s.warnings,
        "message": s.message, "content_hash": s.content_hash(),
        "narrative": dataclasses.asdict(nar) if nar else None,
    }


def _contract_version():
    from .. import contracts
    return contracts.SCHEMA_VERSION


# ── CLI ──────────────────────────────────────────────────────────────────────────────────────
def _main(argv=None):
    import argparse
    import json
    ap = argparse.ArgumentParser(description="Espresso Model Relay (illustrative_linked_pull_v1)")
    ap.add_argument("--preset", default=REFERENCE_PRESET)
    ap.add_argument("--mode", default="fast", choices=("fast", "extended"))
    ap.add_argument("--format", default="json", choices=("json", "md"))
    ap.add_argument("--output", default=None)
    ap.add_argument("--dose-g", type=float, default=20.0)
    ap.add_argument("--beverage-g", type=float, default=40.0)
    ap.add_argument("--grind", type=float, default=1.7)
    ap.add_argument("--pressure-bar", type=float, default=9.0)
    ap.add_argument("--temperature-c", type=float, default=93.0)
    ap.add_argument("--heterogeneity", default="moderate", choices=("low", "moderate", "high"))
    args = ap.parse_args(argv)
    if args.preset != REFERENCE_PRESET:
        raise SystemExit(f"unknown preset {args.preset!r} (only {REFERENCE_PRESET})")
    req = RelayRequest(dose_g=args.dose_g, target_beverage_g=args.beverage_g, grind_setting=args.grind,
                       pressure_bar=args.pressure_bar, brew_temperature_c=args.temperature_c,
                       heterogeneity=args.heterogeneity, mode=args.mode)
    result = execute_illustrative_linked_pull(req, mode=args.mode)
    if args.format == "md":
        from . import linked_pull_display as D
        text = D.relay_markdown(result)
    else:
        text = json.dumps(result, indent=2, sort_keys=True, default=str)
    if args.output:
        with open(args.output, "w") as f:
            f.write(text)
        print(f"wrote {args.output} · components_executed={result['counts']['components_executed']} · "
              f"model_output_hash={result['model_output_hash'][:12]}")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(_main())
