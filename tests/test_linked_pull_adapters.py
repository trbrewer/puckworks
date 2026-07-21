"""Adapter + link-record contract tests for the Espresso Model Relay."""
import pytest

from puckworks.product import linked_pull_adapters as AD
from puckworks.product.linked_pull_records import (LinkKind, LinkRecord, LinkedValue, ValueOrigin)


def test_radius_match_stays_in_map_domain_and_records_residual():
    # Cameron gs=1.7 boulder radius ~335 um is inside the Mahlkonig map
    m = AD.radius_match(3.35e-4)
    assert 1.0 <= m["dial"] <= 11.0
    assert "residual_m" in m and m["assumption_ids"] == ("A01",)


def test_out_of_domain_radius_fails_cleanly_not_clamped():
    with pytest.raises(AD.AdapterDomainError):
        AD.radius_match(2.0e-3)          # 2 mm — far outside the map, must raise (never clamp)
    with pytest.raises(AD.AdapterDomainError):
        AD.radius_match(1.0e-5)          # 10 um — below the map


def test_si_permeability_guard_rejects_out_of_band():
    assert AD.si_permeability_guard(3e-11)["k_m2"] == 3e-11
    with pytest.raises(AD.AdapterDomainError):
        AD.si_permeability_guard(1.0)    # 1 m^2 is absurd, outside the SI band


def test_pressure_nodes_are_explicit_and_not_double_counted():
    top = AD.pressure_node_top(9.0, 0.3)
    drop = AD.pressure_node_drop(9.0)
    assert top["p_top_bar"] == pytest.approx(8.7)
    assert drop["dP_bed_bar"] == 9.0           # applied once (not top+drop of the same segment)
    assert top["assumption_ids"] == ("A04",)


def test_representative_reductions_are_recorded():
    assert "conversion" in AD.representative_pressure(9.0)
    rep = AD.representative_flow(2.4)
    assert rep["flow_mL_s"] == pytest.approx(2.4) and rep["assumption_ids"] == ("A11", "A12")


def test_dissolution_fraction_masks_zero_start_without_clamping():
    import numpy as np
    out = AD.dissolution_fraction(np.array([0.0, 0.001, 0.002, 0.0028]), 0.020)
    # the exact-zero start is OMITTED via a recorded mask (not floored to 1e-6)
    assert out["skipped_indices"] == [0] and out["n_skipped_zero"] == 1
    assert np.all(out["phi"] > 0.0)                 # in (0, 1], not clamped to 1e-6/0.999
    assert len(out["phi"]) == 3 and out["md_g_full"].shape == (4,)   # arrays stay length-aware
    assert out["assumption_ids"] == ("A09",)


def test_dissolution_valid_increasing_trajectory():
    import numpy as np
    out = AD.dissolution_fraction(np.array([0.0005, 0.001, 0.002]), 0.020)
    assert out["n_skipped_zero"] == 0 and np.all(np.diff(out["phi"]) > 0)


def test_dissolution_rejects_negative_nan_inf_and_over_dose():
    import numpy as np
    with pytest.raises(AD.AdapterDomainError):
        AD.dissolution_fraction(np.array([0.0, -0.001]), 0.020)          # negative
    with pytest.raises(AD.AdapterDomainError):
        AD.dissolution_fraction(np.array([0.0, np.nan]), 0.020)          # NaN
    with pytest.raises(AD.AdapterDomainError):
        AD.dissolution_fraction(np.array([0.0, np.inf]), 0.020)          # inf
    with pytest.raises(AD.AdapterDomainError):
        AD.dissolution_fraction(np.array([0.0, 0.025]), 0.020)           # 25 g > 20 g dose


def test_dissolution_mass_exactly_at_dose_boundary_is_accepted():
    import numpy as np
    out = AD.dissolution_fraction(np.array([0.0, 0.020]), 0.020)         # exactly the dose
    assert out["phi"][-1] == pytest.approx(1.0)


def test_mass_flow_round_trips_with_darcy_velocity():
    r = AD.mass_flow_from_darcy(1.5e-4, 2.827e-3, 960.0)
    q_back = r["mass_flow_g_s"] / (2.827e-3 * 960.0 * 1000.0)
    assert q_back == pytest.approx(1.5e-4, rel=1e-9)


def test_every_assumption_has_required_fields():
    for aid, a in AD.ASSUMPTIONS.items():
        assert a.assumption_id == aid and a.category and a.statement and a.validation_needed
        assert a.affected_components and a.consequence


# --- LinkRecord invariants ---
def test_direct_link_may_not_change_unit_or_basis():
    with pytest.raises(ValueError):
        LinkRecord("e", "a", "f", "b", "g", LinkKind.DIRECT_MODEL_OUTPUT, "m", "mm", "x", "x")
    with pytest.raises(ValueError):
        LinkRecord("e", "a", "f", "b", "g", LinkKind.DIRECT_MODEL_OUTPUT, "m", "m", "x", "y")


def test_adapter_link_requires_adapter_or_conversion():
    with pytest.raises(ValueError):
        LinkRecord("e", "a", "f", "b", "g", LinkKind.DOCUMENTED_ADAPTER, "m", "mm", "x", "y")
    ok = LinkRecord("e", "a", "f", "b", "g", LinkKind.DOCUMENTED_ADAPTER, "m", "mm", "x", "y",
                    adapter_id="scale")
    assert ok.adapter_id == "scale"


def test_assumed_link_requires_an_assumption_id():
    with pytest.raises(ValueError):
        LinkRecord("e", "a", "f", "b", "g", LinkKind.ILLUSTRATIVE_ASSUMPTION, "m", "m", "x", "x")


def test_assumed_value_requires_an_assumption_id():
    with pytest.raises(ValueError):
        LinkedValue("r", 1.0, "m", "b", ValueOrigin.ASSUMED_BRIDGE)      # no assumption -> error
    ok = LinkedValue("r", 1.0, "m", "b", ValueOrigin.ASSUMED_BRIDGE, assumption_ids=("A01",))
    assert ok.assumption_ids == ("A01",)
