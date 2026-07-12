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
