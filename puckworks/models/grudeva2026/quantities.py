"""Explicit phase-volume conversions and optional dimensional observation operator."""
from __future__ import annotations

from dataclasses import dataclass
import math
import numpy as np

from .reduced import Parameters, Result


def grain_to_bed(concentration, phase_fraction: float):
    """Same material population only: grain-volume concentration -> bed contribution."""
    if not math.isfinite(phase_fraction) or not 0 < phase_fraction <= 1:
        raise ValueError("phase_fraction must be in (0,1]")
    c = np.asarray(concentration, float)
    if not np.all(np.isfinite(c)) or np.any(c < 0):
        raise ValueError("finite nonnegative concentrations required")
    return c * phase_fraction


def bed_to_grain(contribution, phase_fraction: float):
    """Inverse for the identical population; not a Cameron/scenario adapter."""
    return grain_to_bed(contribution, phase_fraction) / phase_fraction**2


def bed_inventory(external_liquid, fines, boulders_including_pores,
                  parameters: Parameters = Parameters()):
    """Concentration per bed volume; internal pore liquid is already in boulders."""
    p = parameters
    return (grain_to_bed(external_liquid, p.phi_l) + grain_to_bed(fines, p.phi_f)
            + grain_to_bed(boulders_including_pores, p.phi_b))


@dataclass(frozen=True)
class Scaling:
    bed_depth_m: float | None = None
    bed_area_m2: float | None = None
    darcy_flux_m_s: float | None = None
    c_sat_kg_m3: float | None = None
    dry_coffee_mass_kg: float | None = None
    beverage_mass_kg: float | None = None
    beverage_density_kg_m3: float | None = None

    def __post_init__(self):
        for key, value in vars(self).items():
            if value is not None and (not math.isfinite(value) or value < 0):
                raise ValueError(f"{key} must be finite and nonnegative or None")
        if self.beverage_mass_kg is not None and self.beverage_density_kg_m3 is not None:
            raise ValueError("choose measured beverage mass or explicit density approximation")


def dimensional_outputs(result: Result, scaling: Scaling) -> dict:
    """Final integrated cup quantities. None + a reason for missing/zero scales.

    Explicit beverage mass refers to the final observation time. Constant density
    approximates beverage mass from prescribed post-drip liquid volume. A finite
    liquid concentration is kg/m^3, never silently a mass percent.
    Only COMPLETED results qualify, including right-censored observation windows.
    Failed-result arrays remain available on Result for diagnostics, not predictions.
    """
    names = ("time_s", "outlet_concentration_kg_m3", "outlet_volume_flow_m3_s",
             "solute_mass_kg", "beverage_volume_m3", "beverage_mass_kg", "ey_percent",
             "tds_mass_percent")
    out = dict.fromkeys(names)
    reasons = {}
    qualification = {"numerical_status": result.status,
                     "numerical_unavailable_reasons": dict(result.unavailable_reasons),
                     "convergence_status": result.convergence_status,
                     "first_drip_role": "model-derived under prescribed flow",
                     "physical_validation": "NOT_ESTABLISHED"}
    if result.status != "COMPLETED" or not result.time:
        detail = "; ".join(f"{key}: {value}" for key, value in result.unavailable_reasons.items())
        reason = f"Unqualified numerical result ({result.status}): " + (
            detail or "No supported numerical observation samples")
        return {**out, **qualification,
                "beverage_mass_semantics": "Unavailable: numerical result did not qualify",
                "unavailable_reasons": {key: reason for key in names}}
    s = scaling
    p = Parameters(**result.parameters)
    tw = None
    if s.bed_depth_m and s.darcy_flux_m_s:
        tw = p.phi_t*s.bed_depth_m/s.darcy_flux_m_s
        out["time_s"] = (np.asarray(result.time)*tw).tolist()
    else:
        reasons["time_s"] = "Positive bed depth and Darcy flux in m/s required"
    if s.c_sat_kg_m3:
        out["outlet_concentration_kg_m3"] = (np.asarray(result.outlet_concentration)*s.c_sat_kg_m3).tolist()
    else:
        reasons["outlet_concentration_kg_m3"] = "Positive c_sat in kg/m^3 required"
    if s.bed_area_m2 and s.darcy_flux_m_s:
        qv = s.bed_area_m2*s.darcy_flux_m_s
        out["outlet_volume_flow_m3_s"] = [qv if t >= 1 else 0. for t in result.time]
        if tw is not None:
            out["beverage_volume_m3"] = qv*tw*max(result.time[-1]-1, 0.)
            if s.c_sat_kg_m3:
                out["solute_mass_kg"] = qv*tw*s.c_sat_kg_m3*result.cumulative_discharged_solute[-1]
    else:
        reasons["outlet_volume_flow_m3_s"] = "Positive area and Darcy flux required"
    volume, mass = out["beverage_volume_m3"], out["solute_mass_kg"]
    if s.beverage_mass_kg is not None:
        out["beverage_mass_kg"] = s.beverage_mass_kg
        semantics = "explicit final beverage mass supplied by caller"
    elif s.beverage_density_kg_m3 and volume is not None:
        out["beverage_mass_kg"] = volume*s.beverage_density_kg_m3
        semantics = "constant supplied density times prescribed discharged liquid volume (approximation)"
    else:
        semantics = "beverage mass unavailable; no implicit density"
    if mass is not None and s.dry_coffee_mass_kg:
        out["ey_percent"] = 100*mass/s.dry_coffee_mass_kg
    if mass is not None and out["beverage_mass_kg"]:
        out["tds_mass_percent"] = 100*mass/out["beverage_mass_kg"]
    for key, value in out.items():
        if value is None and key not in reasons:
            reasons[key] = ("Positive dry dose and solute mass required" if key == "ey_percent" else
                            "Positive beverage mass with explicit semantics and solute mass required"
                            if key == "tds_mass_percent" else "Missing or zero required dimensional scale")
    return {**out, **qualification, "beverage_mass_semantics": semantics, "unavailable_reasons": reasons}
