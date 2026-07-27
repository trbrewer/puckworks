"""maille2024 as a REGISTERED component (2026-07-25): the phi closure, the PSD adapter, the
two-regime kinetics, and the A11 `fines_fraction` convention decision the registration forced.

The discriminating computations themselves are covered by tests/test_maille2024.py; this file
covers the component surface and the contract change.
"""
import math

import pytest

import puckworks.models  # noqa: F401  (registers components)
from puckworks import contracts as C
from puckworks import registry as R
from puckworks.models.maille2024 import phi_closure as pc
from puckworks.models.maille2024 import two_regime as tr


# ---- registration ------------------------------------------------------------------------
def test_both_components_registered_as_calibration():
    """Never runtime: no bed, no pressure, no flow to couple through, and the dilute/K=1
    assumption is violated in espresso (card 'Kind justification')."""
    for name, stage in (("maille2024.phi_closure", "grind"),
                        ("maille2024.two_regime", "extraction")):
        c = R.get(name)
        assert c.stage == stage
        assert c.execution_role == "calibration"
        assert c.provenance_class == "published_port"
        assert c.gates, "%s must carry at least one gate wired to real data" % name


def test_evidence_strength_not_upgraded():
    """phi_closure stays at code_verification: the per-bin PSD is unpublished, so Eqs 6.8-6.9
    cannot be run end-to-end from the source and the E1 gate uses a D[4,3] approximation."""
    assert R.get("maille2024.phi_closure").evidence_strength == "code_verification"
    assert R.get("maille2024.two_regime").evidence_strength == "source_curve_reproduction"


# ---- phi closure / PSD adapter ------------------------------------------------------------
def test_e1_two_layer_is_the_registry_convention():
    """The printed Eq 6.9 removes ONE cell layer; the registry adopts TWO (card erratum E1)."""
    assert pc.SHELL_LAYERS == 2
    d43 = 800e-6
    one, two = pc.shell_fraction(d43, 1), pc.shell_fraction(d43, 2)
    assert two > one                       # two layers strictly more shell volume
    assert 0.0 < one < two < 1.0


def test_shell_fraction_consumes_small_particles_whole():
    """A particle thinner than the shell depth is entirely 'fast' -- not a negative volume."""
    assert pc.shell_fraction(2.0 * pc.D_C_M, 2) == 1.0


def test_psd_adapter_reproduces_table_6_3_ordering():
    """The adapter run bin-by-bin on a fines-heavy vs coarse-heavy PSD must order phi correctly,
    and the Eq-6.7 identity phi = fines + coarse must hold exactly."""
    diam = [50.0, 150.0, 400.0, 900.0]
    fine_heavy = pc.phi_from_binned_psd(diam, [40.0, 40.0, 10.0, 10.0])
    coarse_heavy = pc.phi_from_binned_psd(diam, [5.0, 5.0, 20.0, 70.0])
    assert fine_heavy["phi"] > coarse_heavy["phi"]
    for r in (fine_heavy, coarse_heavy):
        assert math.isclose(r["phi"], r["theta_v_fines"] + r["theta_v_coarse"], rel_tol=1e-12)
        assert 0.0 <= r["phi"] <= 1.0


def test_psd_adapter_rejects_malformed_input():
    with pytest.raises(ValueError):
        pc.phi_from_binned_psd([], [])
    with pytest.raises(ValueError):
        pc.phi_from_binned_psd([100.0, 200.0], [1.0])          # length mismatch
    with pytest.raises(ValueError):
        pc.phi_from_binned_psd([100.0, -200.0], [1.0, 1.0])    # non-positive diameter
    with pytest.raises(ValueError):
        pc.phi_from_binned_psd([100.0, 200.0], [0.0, 0.0])     # zero total volume


def test_phi_from_d43_matches_the_e1_gate_route():
    """The single-diameter approximation is the only route reproducible from the thesis (the
    per-bin arrays are unpublished); it must agree with the shell kernel by construction."""
    r = pc.phi_from_d43(800.0, 0.10)
    expected_coarse = 0.90 * pc.shell_fraction(800e-6, pc.SHELL_LAYERS)
    assert math.isclose(r["theta_v_coarse"], expected_coarse, rel_tol=1e-12)
    assert math.isclose(r["phi"], 0.10 + expected_coarse, rel_tol=1e-12)


def test_adapter_flags_extrapolation_beyond_the_source_phi_range():
    """Cameron-fine PSDs push phi to ~0.85-0.94, far above maille's own measured 0.356-0.648.
    The closure must SAY it is being read outside its tested range."""
    fine = pc.phi_from_binned_psd([20.0, 60.0, 120.0], [30.0, 40.0, 30.0])
    assert fine["phi"] > pc.PHI_SOURCE_RANGE[1]
    assert fine["extrapolated_beyond_source_phi_range"] is True


# ---- A11: the fines_fraction convention decision -------------------------------------------
def test_grind_state_from_psd_stamps_the_convention():
    """The card's Interface-mapping complaint made concrete: no bare fines_fraction escapes."""
    gs, r = pc.grind_state_from_psd(1.5, [50.0, 400.0, 900.0], [20.0, 40.0, 40.0])
    assert gs.fines_threshold_um == 186.0
    assert gs.fines_dispersion_method == "hybrid"
    assert gs.fines_basis == "volume"
    # fines_fraction is theta_v,fines (a SIZE class), NOT phi (a fast-EXTRACTION fraction)
    assert gs.fines_fraction == r["theta_v_fines"]
    assert gs.fines_fraction < r["phi"]


def test_undeclared_convention_cannot_be_compared():
    """An undeclared convention is the hazard, not evidence of agreement -- it must raise."""
    bare = C.GrindState(setting=1.5, fines_fraction=0.2)
    declared = C.GrindState(setting=1.5, fines_fraction=0.2, fines_threshold_um=186.0,
                            fines_dispersion_method="hybrid", fines_basis="volume")
    with pytest.raises(ValueError, match="no declared convention"):
        C.assert_fines_fraction_comparable(bare, declared)


def test_different_thresholds_refuse_to_merge():
    """186 um (maille) vs 100 um (smrke2024/khamitova2020) are different quantities, and there is
    deliberately no conversion path (CLAUDE.md rule 6)."""
    maille = C.GrindState(setting=1.5, fines_fraction=0.2, fines_threshold_um=186.0,
                          fines_dispersion_method="hybrid", fines_basis="volume")
    smrke = C.GrindState(setting=1.5, fines_fraction=0.2, fines_threshold_um=100.0,
                         fines_dispersion_method="hybrid", fines_basis="volume")
    with pytest.raises(ValueError, match="thresholds differ"):
        C.assert_fines_fraction_comparable(maille, smrke)


def test_different_dispersion_methods_refuse_to_merge():
    """maille Table 5.2 measures up to ~2x disagreement on the SAME material by method."""
    liquid = C.GrindState(setting=1.5, fines_fraction=0.31, fines_threshold_um=186.0,
                          fines_dispersion_method="liquid", fines_basis="volume")
    air = C.GrindState(setting=1.5, fines_fraction=0.17, fines_threshold_um=186.0,
                       fines_dispersion_method="air", fines_basis="volume")
    with pytest.raises(ValueError, match="dispersion methods differ"):
        C.assert_fines_fraction_comparable(liquid, air)


def test_matching_conventions_compare_cleanly():
    a = C.GrindState(setting=1.1, fines_fraction=0.20, fines_threshold_um=186.0,
                     fines_dispersion_method="hybrid", fines_basis="volume")
    b = C.GrindState(setting=1.5, fines_fraction=0.15, fines_threshold_um=186.0,
                     fines_dispersion_method="hybrid", fines_basis="volume")
    assert C.assert_fines_fraction_comparable(a, b) is True


def test_convention_without_a_value_is_a_construction_error():
    with pytest.raises(ValueError, match="carries no fines_fraction"):
        C.GrindState(setting=1.5, fines_threshold_um=186.0)


def test_registry_conventions_record_the_known_hazard():
    """wadsworth2026.grindmap carries radius MOMENTS -- not expressible as a fines_fraction at
    all -- and is recorded as None rather than given a fabricated threshold."""
    assert C.FINES_CONVENTIONS["maille2024"]["threshold_um"] == 186.0
    assert C.FINES_CONVENTIONS["khamitova2020"]["threshold_um"] == 100.0
    # recorded as None rather than rounded to one number: wadsworth carries radius MOMENTS (no
    # threshold exists), and smrke2024 uses TWO cuts in one paper (<120 um sieve, 100 um quantile).
    assert C.FINES_CONVENTIONS["wadsworth2026.grindmap"] is None
    assert C.FINES_CONVENTIONS["smrke2024"] is None
    # 0.7 introduced these fines-provenance fields; 0.8 added PressureNode/PressureTrace (third
    # Paper 3 review P0-8). Both additive, so the conventions asserted above are unchanged.
    assert C.SCHEMA_VERSION == "0.8"


# ---- two-regime kinetics --------------------------------------------------------------------
def test_eq_6_2_is_zero_before_the_delay_and_monotone_after():
    f = tr.fraction_extracted
    assert f(2.0, 0.5, 5.0, 50.0, tau_s=4.0) == 0.0        # hard shift, no early extraction
    ys = [f(t, 0.5, 5.0, 50.0, tau_s=4.0) for t in (5.0, 20.0, 60.0, 600.0)]
    assert all(b > a for a, b in zip(ys, ys[1:]))
    assert ys[-1] < 1.0 and ys[-1] > 0.99                   # approaches, never reaches, C_inf


def test_eq_6_2_reduces_to_eq_6_1_at_zero_delay():
    assert tr.fraction_extracted(10.0, 0.4, 5.0, 50.0, 0.0) == pytest.approx(
        0.4 * (1 - math.exp(-2.0)) + 0.6 * (1 - math.exp(-0.2)))


def test_two_regime_rejects_invalid_parameters():
    with pytest.raises(ValueError):
        tr.fraction_extracted(10.0, 1.4, 5.0, 50.0)         # phi outside [0,1]
    with pytest.raises(ValueError):
        tr.fraction_extracted(10.0, 0.5, 0.0, 50.0)         # non-positive time constant


def test_tau_is_carried_as_the_cards_visual_values_not_fitted():
    """tau is NOT tabulated anywhere in the thesis; the acids get 0 by the source's own reading."""
    assert tr.TAU_S["Caffeine"] == 4.0 and tr.TAU_S["3-CQA"] == 3.0
    assert all(tr.TAU_S[a] == 0.0 for a in ("Citric acid", "Malic acid", "Quinic acid"))


def test_kinetics_lookup_omits_unreported_fits():
    """Omega_C/M/O quinic are '*' in the source: omitted, never defaulted."""
    assert "Quinic" not in tr.kinetics("Omega_C")
    omega_a = tr.kinetics("Omega_A")
    assert {"Caffeine", "3-CQA", "Citric", "Malic"} <= set(omega_a)
    for lf, ls in omega_a.values():
        assert 0 < lf < ls                                  # fast is faster than slow, always


def test_e5_impossible_cis_stay_flagged_never_repaired():
    flagged = tr.ci_flags()["flagged"]
    keys = sorted((f["sample"], f["compound"], f["regime"]) for f in flagged)
    assert keys == [("Omega_L", "Quinic", "lambda_slow"), ("Omega_T", "3-CQA", "lambda_fast")]


def test_source_bands_are_the_gate_4_question():
    assert tr.in_source_bands(5.0, 40.0) == {
        "fast_in_band": True, "slow_in_band": True,
        "fast_range_s": [2.2, 19.1], "slow_range_s": [13.0, 158.0]}
    # roman's fine-class sub-second constants miss both bands (gate 4, roman half)
    miss = tr.in_source_bands(0.04, 0.5)
    assert not miss["fast_in_band"] and not miss["slow_in_band"]
