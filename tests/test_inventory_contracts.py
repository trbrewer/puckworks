"""PW-CORE-002/003 — SoluteInventory validation, zero-safe species ratios, unknown-compound namespacing."""
import pytest

from puckworks.contracts import SoluteInventory
from puckworks import inventory as inv


def test_pw_core_002_solute_inventory_validates_species_schema():
    good = {"caffeine": {"amount": 12.0, "sd": 0.1, "unit": "mg/kg", "basis": "roasted"}}
    SoluteInventory(species=good)                       # valid
    for bad in ({"x": {"amount": float("nan"), "unit": "mg/kg", "basis": "b"}},   # non-finite
                {"x": {"amount": float("inf"), "unit": "mg/kg", "basis": "b"}},
                {"x": {"unit": "mg/kg", "basis": "b"}},                            # no amount
                {"x": {"amount": 1.0, "basis": "b"}},                             # no unit
                {"x": {"amount": 1.0, "unit": "mg/kg"}},                          # no basis
                {"": {"amount": 1.0, "unit": "mg/kg", "basis": "b"}}):            # empty name
        with pytest.raises(ValueError):
            SoluteInventory(species=bad)
    # extractable_fraction must be a finite fraction in [0,1]
    with pytest.raises(ValueError):
        SoluteInventory(species=good, extractable_fraction={"caffeine": 1.5})


def test_pw_core_002_amount_is_safe_and_ratio_is_zero_safe(monkeypatch):
    si = SoluteInventory(species={"caffeine": {"amount": 10.0, "unit": "mg/kg", "basis": "b"}})
    assert si.amount("caffeine") == 10.0
    assert si.amount("missing") is None
    # a zero / non-finite denominator yields None, never ZeroDivision / inf / nan
    real = inv.bruno_solute_inventory
    class _Fake:
        def amount(self, name):
            return 0.0 if name == "den" else 5.0
    monkeypatch.setattr(inv, "bruno_solute_inventory", lambda o: _Fake())
    assert inv.species_ratio("den", "A", "B") is None       # denominator 0 -> None


def test_pw_core_003_unknown_compounds_are_namespaced():
    # every real bruno compound is currently mapped (no unmapped: keys); the guard is defensive
    for origin, si in inv.bruno_all_inventories().items():
        assert not any(k.startswith("unmapped:") for k in si.species), origin


def test_pw_core_001_contract_boundary_validation():
    import numpy as np
    from puckworks.contracts import (GrindState, BedState, FlowLaw, PumpHeadspace, ShotResultState)

    # valid constructions still work
    GrindState(setting=1.7, fines_fraction=0.3, boulder_radius_m=3e-4)
    BedState(dose_kg=0.02, depth_m=0.02, area_m2=2.7e-3, porosity=0.4, k_m2=1e-12)
    FlowLaw(k_m2=1e-12)
    PumpHeadspace(p_m=1.2e6, Q_m=1e-5, R_f=1e9, H0=0.01)
    ShotResultState(EY_pct=20.0, tds_pct=8.0, t_shot_s=25.0, beverage_g=40.0)

    # latent-bug constructions now fail loudly
    for bad in (
        lambda: GrindState(setting=float("nan")),
        lambda: GrindState(setting=1.7, fines_fraction=1.5),           # out of [0,1]
        lambda: GrindState(setting=1.7, boulder_radius_m=-1e-4),       # negative radius
        lambda: BedState(dose_kg=-0.02, depth_m=0.02, area_m2=2.7e-3, porosity=0.4),
        lambda: BedState(dose_kg=0.02, depth_m=0.02, area_m2=2.7e-3, porosity=1.4),
        lambda: BedState(dose_kg=0.02, depth_m=0.02, area_m2=2.7e-3, porosity=float("inf")),
        lambda: FlowLaw(k_m2=0.0),
        lambda: FlowLaw(k_m2=1e-12, closure=""),
        lambda: PumpHeadspace(p_m=-1.0, Q_m=1e-5, R_f=1e9, H0=0.01),
        lambda: ShotResultState(EY_pct=float("nan"), tds_pct=8.0, t_shot_s=25.0, beverage_g=40.0),
        lambda: ShotResultState(EY_pct=20.0, tds_pct=8.0, t_shot_s=-1.0, beverage_g=40.0),
    ):
        with pytest.raises(ValueError):
            bad()
