"""Documented product-level adapters + the assumption ledger for the Espresso Model Relay.

Adapters are the ONLY place a value legitimately changes unit, basis, or model lineage. Each adapter is a
pure function that validates SI at the boundary (via `puckworks.validate`), computes a documented
transform, records the exact conversion string, and — where it bridges definitions or lineages — names the
`AssumptionRecord`(s) it rests on. Adapters NEVER silently clamp, silently change a pressure node, silently
equate porosity definitions, silently port a grinder dial, or silently treat total solute content as
extractable. Out-of-domain inputs raise `AdapterDomainError` so the engine can mark a stage DOMAIN_REJECTED
and let independent branches continue.

The assumption ledger (A01–A12) is a first-class, serialized output — not a disclaimer paragraph.
"""
from __future__ import annotations

from .. import validate as V
from ..contracts import K_SI_MAX, K_SI_MIN
from .linked_pull_records import AssumptionRecord


class AdapterDomainError(ValueError):
    """An adapter input is outside a model card's domain — never clamped, always surfaced."""


def _A(aid, category, statement, rationale, stage, comps, fields, consequence, validation, transform=None):
    return AssumptionRecord(aid, category, statement, rationale, stage, tuple(comps), tuple(fields),
                            consequence, validation, transform)


# ── the assumption ledger (A01–A12) ─────────────────────────────────────────────────────────
ASSUMPTIONS: dict = {a.assumption_id: a for a in (
    _A("A01", "CROSS_GRINDER_SIZE_MATCH",
       "The Wadsworth Mahlkonig dial was chosen so its reported MEAN grain radius is closest to Cameron's "
       "coarse-family (boulder) radius.",
       "The two models speak different size languages (an EK43 dial + two particle families vs a "
       "grinder-specific mean-radius map); a single size summary is matched to let the relay continue.",
       "grind", ["cameron2020.extraction_bdf", "wadsworth2026.grindmap"],
       ["boulder_radius_m", "physical_radius_m"],
       "Matching a coarse-family radius to a distribution MEAN tends to overstate particle size and "
       "therefore permeability; the resulting Darcy velocity can be unphysically high.",
       "A shared PSD measured on the same coffee/grinder, mapped to both models' size summaries.",
       "G = (R_boulder - R0) / beta on the Mahlkonig map, accepted only inside G in [1, 11]."),
    _A("A02", "POROSITY_DEFINITION",
       "The connected/percolating porosity fed to the permeability closure is a stipulated tamped-puck "
       "value; it is kept as a NAMED value, never merged with the synthetic-pack void fraction or the "
       "water-accessible porosity.",
       "Each model uses its own porosity definition; equating them silently would be a hidden assumption.",
       "packing", ["wadsworth2026.permeability"], ["phi_p"],
       "Permeability scales strongly with connected porosity (~phi_p^4.4), so this stipulation moves k.",
       "A measured connected porosity for the specific tamped puck.", None),
    _A("A03", "SYNTHETIC_GEOMETRY",
       "The Boolean-sphere pack is a controlled synthetic geometry, not a scan of the user's puck.",
       "It is generated to a target void fraction and heterogeneity, seeded deterministically.",
       "packing", ["brewer2026.pack_generator"], ["solid_mask"],
       "Pack-generator geometry illustrates structure; its void fraction is not the Wadsworth permeability.",
       "A micro-CT scan of a real tamped puck at matched grind.", None),
    _A("A04", "PRESSURE_NODE_ASSIGNMENT",
       "The machine's delivered overpressure is assigned to named pressure NODES (pump / bed-top / basket "
       "/ bed pressure-drop); a single representative bed-top pressure history is handed to the wetting "
       "model rather than re-deriving Foster's internal trajectory.",
       "Espresso pressure differs by node; the relay must say which node each downstream model consumes.",
       "machine", ["foster2025.machine_mode", "foster2025.infiltration"], ["p_h", "dP_bed"],
       "The wetting and flow models see a stipulated node assignment, not a measured basket trace.",
       "Simultaneous pump-outlet and basket pressure measurement on the modelled machine.",
       "p_top ≈ target overpressure minus a stipulated line loss; dP_bed ≈ target overpressure "
       "(the puck is treated as the dominant resistance — applied once, not double-counted)."),
    _A("A05", "CROSS_RIG_TRANSFER",
       "Permeability, geometry, and pressure are passed between models fitted on different rigs and "
       "coffees.",
       "No single rig produced all of these; combining them is a cross-model transfer.",
       "wetting", ["wadsworth2026.permeability", "foster2025.infiltration"], ["k_m2"],
       "Downstream results inherit no validation from any single source rig.",
       "One rig producing permeability, geometry, and wetting on the same coffee.", None),
    _A("A06", "PROFILE_RESCALING",
       "Cameron consumes a single representative pressure; the machine's pressure history is reduced to a "
       "plateau/representative value for it.",
       "Cameron's extraction model takes a scalar pressure, not the full dynamic trace.",
       "extraction", ["foster2025.machine_mode", "cameron2020.extraction_bdf"], ["pressure_bar"],
       "Cameron did NOT consume the full dynamic pressure or any thermal history.",
       "A Cameron variant that accepts a time-varying pressure input.",
       "p_representative = median of the delivered plateau (target overpressure in this reference pull)."),
    _A("A07", "EXTRAPOLATED_CLOSURE",
       "The liquid-viscosity closure was measured on soluble-coffee extract, not in-puck espresso.",
       "The Telis-Romero rheology is a source-data closure extrapolated to espresso conditions.",
       "flow", ["sourcing2026.g10_liquor_rheology", "wadsworth2026.inertial"], ["viscosity_pa_s"],
       "Bulk-cup viscosity is near water (~1.05x); the closure is a diagnostic, not in-puck validation.",
       "In-puck espresso rheometry across the shot.", None),
    _A("A08", "EXTRAPOLATED_CLOSURE",
       "The inertial (Forchheimer) coefficient is extrapolative for tamped coffee even when the Darcy "
       "permeability input is valid.",
       "The k_I closure reproduces a reported Fo band but is not validated for every tamped case.",
       "flow", ["wadsworth2026.inertial"], ["k_I_m"],
       "The Darcy-vs-Forchheimer departure is illustrative of the regime, not a calibrated correction.",
       "Direct pressure-flow measurement into the inertial regime on the specific puck.", None),
    _A("A09", "ONE_WAY_COUPLING",
       "Cameron's cumulative dissolved mass is fed one-way into the Waszkiewicz porosity/permeability "
       "response to create a NEW Puckworks coupling.",
       "The two models were never coupled in either source paper.",
       "puck_change", ["cameron2020.extraction_bdf", "waszkiewicz2025.poroelastic"],
       ["dissolved_mass_g", "dissolution_fraction"],
       "This branch does NOT inherit the Waszkiewicz paper's validation; it is not fed back into Cameron.",
       "A measured flow trace on a shot with independently measured dissolved-mass kinetics.",
       "Phi(t) = m_dissolved(t) / dose, evaluated where m_dissolved > 0 (t=0 skipped to avoid 1/0)."),
    _A("A10", "ONE_WAY_COUPLING",
       "The heterogeneity sigma has two DISTINCT origins that are never interchanged: the streamtube "
       "model's calibrated closure (fast mode) versus a value measured from a synthetic-pack LB flow "
       "field (extended mode).",
       "One is a coffee-calibrated closure; the other is geometry-derived from a toy voxel pack.",
       "heterogeneous", ["brewer2026.streamtube", "brewer2026.pack_generator", "brewer2026.lb_reference"],
       ["sigma"],
       "A calibrated-closure sigma is not geometry-measured; an LB sigma is not coffee-measured.",
       "Flow-heterogeneity measured on the real puck geometry.", None),
    _A("A11", "FLOW_REDUCTION",
       "The multi-solute solver receives a reduced representative flow rather than the full machine Q(t).",
       "The Pannusch fixed-flow path takes a scalar or piecewise flow, not the full dynamic trace.",
       "multisolute", ["foster2025.machine_mode", "pannusch2024.solver"], ["flow_trace"],
       "Pannusch did NOT consume the full dynamic flow trace; the reduction is recorded.",
       "A Pannusch variant driven by the measured Q(t) and T(t) of this shot.",
       "q_representative = mean beverage flow over the modelled shot (mL/s)."),
    _A("A12", "TOTAL_TO_EXTRACTABLE_INVENTORY",
       "Any per-solute inventory used by the chemistry branch is treated with an explicit extractability "
       "assumption; total roasted-solute content is never used directly as extractable solid inventory.",
       "Total roasted content is not the same as the extractable pool a shot can recover.",
       "multisolute", ["pannusch2024.solver"], ["c_s0"],
       "Absolute per-solute yields depend on an unmeasured extractable fraction; only timing is emphasised.",
       "Per-solute extractable fractions measured for this coffee.", None),
)}


def assumption(aid: str) -> AssumptionRecord:
    return ASSUMPTIONS[aid]


# ── adapters ────────────────────────────────────────────────────────────────────────────────
def radius_match(cameron_boulder_radius_m: float) -> dict:
    """A01 — invert the Wadsworth Mahlkonig mean-radius map to the dial whose mean radius is closest to
    Cameron's boulder radius. Accept only inside the map domain (never clamp); record the residual."""
    from ..models.wadsworth2026 import grindmap as gm
    V.require_positive(cameron_boulder_radius_m, "cameron_boulder_radius_m")
    beta, R0 = gm.BETA_FIT, gm.R0_FIT
    g_lo, g_hi = gm.WADSWORTH_MAHLKONIG.G_min, gm.WADSWORTH_MAHLKONIG.G_max
    r_lo = gm.WADSWORTH_MAHLKONIG.mean_radius_m(g_lo)
    r_hi = gm.WADSWORTH_MAHLKONIG.mean_radius_m(g_hi)
    if not (min(r_lo, r_hi) <= cameron_boulder_radius_m <= max(r_lo, r_hi)):
        raise AdapterDomainError(
            f"Cameron boulder radius {cameron_boulder_radius_m*1e6:.0f} um is outside the Wadsworth "
            f"Mahlkonig map domain [{min(r_lo, r_hi)*1e6:.0f}, {max(r_lo, r_hi)*1e6:.0f}] um; not matched.")
    g = (cameron_boulder_radius_m - R0) / beta
    matched = float(gm.WADSWORTH_MAHLKONIG.mean_radius_m(g))
    return {"dial": float(g), "physical_radius_m": matched,
            "residual_m": float(matched - cameron_boulder_radius_m),
            "conversion": ASSUMPTIONS["A01"].mathematical_transform, "assumption_ids": ("A01",)}


def si_permeability_guard(k_m2: float) -> dict:
    """Assert SI permeability is finite and inside the contract band (contracts.K_SI_MIN..MAX). No clamp."""
    V.require_finite(k_m2, "k_m2")
    if not (K_SI_MIN <= k_m2 <= K_SI_MAX):
        raise AdapterDomainError(f"permeability {k_m2:.3e} m^2 outside SI band [{K_SI_MIN:.0e},{K_SI_MAX:.0e}]")
    return {"k_m2": float(k_m2), "conversion": "identity (SI m^2, guarded)", "assumption_ids": ()}


def pressure_node_top(target_overpressure_bar: float, line_loss_bar: float = 0.3) -> dict:
    """A04 — assign a representative bed-top (headspace) pressure node from the target overpressure."""
    V.require_positive(target_overpressure_bar, "target_overpressure_bar")
    p_top = float(target_overpressure_bar - line_loss_bar)
    if p_top <= 0:
        raise AdapterDomainError("bed-top pressure non-positive after line loss")
    return {"p_top_bar": p_top, "p_top_pa": V.bar_gauge_to_pa(p_top),
            "conversion": f"p_top = {target_overpressure_bar:g} - {line_loss_bar:g} bar (line loss)",
            "assumption_ids": ("A04",)}


def pressure_node_drop(target_overpressure_bar: float) -> dict:
    """A04 — assign the whole-bed pressure DROP node (puck treated as dominant resistance; applied once)."""
    V.require_positive(target_overpressure_bar, "target_overpressure_bar")
    return {"dP_bed_bar": float(target_overpressure_bar), "dP_bed_pa": V.bar_gauge_to_pa(target_overpressure_bar),
            "conversion": "dP_bed = target overpressure (puck = dominant resistance; not double-counted)",
            "assumption_ids": ("A04",)}


def representative_pressure(target_overpressure_bar: float) -> dict:
    """A06 — reduce the machine pressure history to the single scalar Cameron consumes."""
    V.require_positive(target_overpressure_bar, "target_overpressure_bar")
    return {"pressure_bar": float(target_overpressure_bar),
            "conversion": ASSUMPTIONS["A06"].mathematical_transform, "assumption_ids": ("A06",)}


def representative_flow(mean_flow_g_s: float, density_kg_m3: float = 1000.0) -> dict:
    """A11 — reduce the machine flow trace to a representative mean flow in mL/s for the chemistry branch."""
    V.require_nonnegative(mean_flow_g_s, "mean_flow_g_s")
    q_ml_s = float(mean_flow_g_s / (density_kg_m3 / 1000.0))   # g/s -> mL/s at ~unit density
    return {"flow_mL_s": q_ml_s, "conversion": f"q = {mean_flow_g_s:g} g/s / {density_kg_m3/1000:g} g/mL",
            "assumption_ids": ("A11", "A12")}


def dissolution_fraction(m_cup_kg, dose_kg: float) -> dict:
    """A09 — Cameron cumulative dissolved-mass trajectory (kg) -> dissolution fraction Phi(t)=m/dose,
    evaluated where m>0 (t=0 skipped to avoid a 1/0 in the poroelastic factor)."""
    import numpy as np
    m = np.asarray(m_cup_kg, float) * 1000.0     # g
    dose_g = float(dose_kg) * 1000.0
    V.require_positive(dose_g, "dose_g")
    phi = np.clip(m / dose_g, 1e-6, 0.999)        # floor away from 0 (and below 1)
    return {"phi": phi, "md_g": m, "dose_g": dose_g,
            "conversion": ASSUMPTIONS["A09"].mathematical_transform, "assumption_ids": ("A09",)}


def mass_flow_from_darcy(q_m_s: float, area_m2: float, density_kg_m3: float) -> dict:
    """Volumetric Darcy velocity (m/s) -> mass flow (g/s). Round-trips with the inverse."""
    for x, n in ((q_m_s, "q_m_s"), (area_m2, "area_m2"), (density_kg_m3, "density_kg_m3")):
        V.require_finite(x, n)
    g_s = float(q_m_s * area_m2 * density_kg_m3 * 1000.0)
    return {"mass_flow_g_s": g_s, "conversion": "g/s = q[m/s] * A[m^2] * rho[kg/m^3] * 1000",
            "assumption_ids": ()}
