"""sobolik2002 Eq-1/Eq-2 density + refractive-index reproduction gate (G10 third channel).

source_curve_reproduction: recomputes the authors' own closed forms and confirms the tabulated
columns; concentrated soluble-coffee extract, reference-strength for espresso. Eq-3 excluded (illegible).
"""
from puckworks.validation.gates import gate_g10_sobolik_density


def test_density_gate_reproduces_eq1_eq2():
    r = gate_g10_sobolik_density()
    assert r["passed"]
    assert r["n_D_max_abs_err"] < 5e-4        # Eq 1 refractive index recomputes to the table
    assert r["rho_max_rel_err"] < 1e-3        # Eq 2 volume-additive density recomputes
    assert r["water_limit_exact"]             # w=0 recovers pure water exactly (card's key claim)
    assert r["drho_dT_negative"]              # drho/dT < 0 throughout
    assert r["n_rows"] > 100


def test_density_gate_declares_reproduction_only():
    r = gate_g10_sobolik_density()
    # must not overclaim: source_curve_reproduction, explicitly reference for espresso
    assert "source_curve_reproduction" in r["strength"]
    assert "reference" in r["strength"]
