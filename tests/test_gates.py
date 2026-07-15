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
