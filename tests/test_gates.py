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
