from puckworks.validation.gates import QUICK

def test_quick_gates():
    for g in QUICK:
        r = g()
        assert r["passed"], (g.__name__, r)


def test_g1_glassbead_closure_sane():
    from puckworks.validation.gates import gate_g1_glassbead_closure_sane
    assert gate_g1_glassbead_closure_sane()["passed"]


def test_g3_pump_envelope_bounds_quadratic():
    from puckworks.validation.gates import gate_g3_pump_envelope_bounds_quadratic
    assert gate_g3_pump_envelope_bounds_quadratic()["passed"]


def test_g10_reference_mu_above_water():
    from puckworks.validation.gates import gate_g10_reference_mu_above_water
    assert gate_g10_reference_mu_above_water()["passed"]


def test_g10_mu_bias_directional():
    from puckworks.validation.gates import gate_g10_mu_bias_directional
    assert gate_g10_mu_bias_directional()["passed"]


def test_g10_telisromero_closure():
    from puckworks.validation.gates import gate_g10_telisromero_closure
    r = gate_g10_telisromero_closure()
    assert r["passed"], r
    # closures reproduce the authors' own Table anchors within stated fit error
    assert r["eta_err_pct"] <= 2.34   # authors' Eq (10) mean relative error
    assert r["K_err_pct"] <= 10.0     # Eq (13) mean 6.77%, well within
    # bulk shot-TDS liquor is negligibly above water -- NOT the 1.3-2x envelope guess
    assert 1.0 < r["shot_tds_mu_ratio_to_water"] < 1.2


def test_g10_telisromero_full_table():
    from puckworks.validation.gates import gate_g10_telisromero_full_table
    r = gate_g10_telisromero_full_table()
    assert r["passed"], r
    assert r["n_eta_cells"] == 24 and r["n_K_cells"] == 27
    # closures reproduce the measured grid at ~the authors' own fit quality
    assert r["eta_mean_err_pct"] <= 3.5
    assert r["K_mean_err_pct"] <= 8.0


def test_g10_viscosity_bulk_negligible():
    from puckworks.validation.gates import gate_g10_viscosity_bulk_negligible
    r = gate_g10_viscosity_bulk_negligible()
    assert r["passed"], r
    assert r["mu_peak_ratio_to_water"] < 1.15          # in-pore liquor never strongly viscous
    assert r["depthavg_end_flow_factor"] > 0.95        # constant-water-mu safe


def test_g10_viscosity_sensitivity_verdict():
    from puckworks.analysis import g10_viscosity_sensitivity as vs
    r = vs.run_sensitivity(n_snap=4)
    # G10 closes as negligible across the espresso envelope
    assert r["any_powerlaw_regime"] is False
    assert r["worst_shot_integrated_deficit_pct"] < 5.0
    assert r["worst_mu_ratio_to_water"] < 1.15
    # dilute-water fix: mid/late dilute liquor is ~water, not the 1.07x box edge
    from puckworks import data as d
    muw = 3.15e-4
    assert d.telisromero_eta_measured(363.0, 90.0) / muw < 1.10   # box edge ~1.07x


def test_g10_intersource_spread():
    from puckworks.validation.gates import gate_g10_intersource_spread
    r = gate_g10_intersource_spread()
    assert r["passed"], r
    assert r["khomyakov_above_tr"] is True          # consistent sign
    assert 25 <= r["offset_pct_median"] <= 50       # bounded systematic offset (~+37%)


def test_g10_closure_robust_to_intersource_spread():
    # even conservatively DOUBLING the coffee-viscosity excess (covers khomyakov's +37%
    # vs TR2001), the G10 'no runtime hook' verdict survives.
    from puckworks.analysis import g10_viscosity_sensitivity as vs
    r = vs.run_sensitivity(n_snap=4, excess_scale=2.0)
    assert r["any_powerlaw_regime"] is False
    assert r["worst_shot_integrated_deficit_pct"] < 8.0    # baseline ~2.75%, robust ~5.3%
    assert r["worst_mu_ratio_to_water"] < 1.15


def test_g10_telisromero2000_thermal():
    from puckworks.validation.gates import gate_g10_telisromero2000_thermal
    r = gate_g10_telisromero2000_thermal()
    assert r["passed"], r
    assert r["max_anchor_err_pct"] <= 1.5        # closures reproduce Fig endpoints
    assert r["printed_eq6_err_pct"] > 8.0        # printed coeff mispredicts -> typo documented
    assert -20.0 < r["alpha_krocp_offset_pct"] < -5.0   # authors' convection offset (~-11%)
    assert r["normalization_guard_fires"] is True


def test_telisromero2000_normalization_guard():
    import pytest
    from puckworks import data as d
    # fraction basis: legal
    assert 990 < d.telisromero_density_kgm3(82.0, 0.90) < 1010
    # percent basis (the 2001 rheology basis) must be REJECTED, not silently mis-evaluated
    with pytest.raises(ValueError):
        d.telisromero_density_kgm3(82.0, 90.0)


def test_telisromero_loader_and_anchors():
    from puckworks import data as d
    # Eq (10) reproduces the Table-1 eta anchor (X_w=90, T=295 K -> 1.00e-3 Pa*s)
    assert abs(d.telisromero_viscosity_pas(295.0, 90.0) - 1.00e-3) / 1.00e-3 < 0.03
    anchors = {a["quantity"]: a for a in d.telisromero_rheology_anchors()}
    assert set(anchors) == {"eta", "K"}
    closures = d.telisromero_rheology_closures()
    assert set(closures) == {"eq10_newtonian", "eq12_powerlaw_n", "eq13_powerlaw_K"}


def test_a4_solute_inventory_contract():
    from puckworks import contracts, inventory
    assert contracts.SCHEMA_VERSION == "0.6"      # A4 additive bump
    si = inventory.bruno_solute_inventory("Nicaragua")
    assert isinstance(si, contracts.SoluteInventory)
    # linkable species present; content positive; NOT c_s0 (extractable unknown)
    for s in inventory.PANNUSCH_LINKABLE:
        assert si.amount(s) > 0
    assert si.extractable_fraction is None
    assert si.strength.startswith("reference")


def test_bruno_solute_inventory_prior_gate():
    from puckworks.validation.gates import gate_bruno_solute_inventory_prior
    assert gate_bruno_solute_inventory_prior()["passed"]
