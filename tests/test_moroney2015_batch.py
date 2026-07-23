"""moroney2015 well-mixed batch two-population solver + Fig-6 reproduction gate.

source_curve_reproduction: reproduces the paper's own Fig-6 batch plateau from Table 1 + the
DERIVED (exact) immersion volume bookkeeping. Not an independent validation; drip-filter, not espresso.
"""
from puckworks.analysis import moroney2015_batch as mb
from puckworks.validation.gates import gate_moroney2015_batch_ode


def test_derived_volumes_reconstruct_table1_phi_h():
    v = mb.derived_volumes()
    # V_h/V_T reconstructs Table 1's phi_h = 0.8272 to four decimals (confirms the authors' construction)
    assert abs(v["phi_h_reconstructed"] - 0.8272) < 1e-4
    assert abs(v["V_T_m3"] * 1e6 - 541.1) < 0.1        # V_T = 541.1 cm^3
    assert abs(v["V_h_m3"] * 1e6 - 447.6) < 0.1        # V_h = 447.6 cm^3
    assert abs(v["V_T_over_V_water"] - 1.0823) < 1e-3  # bed-volume -> water-charge factor


def test_batch_reproduces_fig6_plateau_and_cross_checks():
    for grind, want in (("JK_drip_filter", 36.6), ("Cimbali_20", 30.4)):
        s = mb.solve(grind)
        # equilibrium brew concentration reproduces the digitized Fig-6 model plateau within ~5%
        assert abs(s["ch_equilibrium"] - want) / want < 0.05, (grind, s["ch_equilibrium"])
        # c_v0 initial condition derives from Table 1 (phi_s,b0 * c_s / phi_v0)
        assert abs(s["c_v0_derived"] - s["c_v0_table"]) < 0.5
        # soluble mass budget is in the stated 26-33% extractable range
        assert 26.0 <= s["extractable_pct_dose"] <= 33.0
    # fine grind plateaus higher than coarse
    assert mb.solve("JK_drip_filter")["ch_equilibrium"] > mb.solve("Cimbali_20")["ch_equilibrium"]


def test_gate_passes():
    assert gate_moroney2015_batch_ode()["passed"]
