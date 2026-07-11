"""Unit tests for the Pannusch PDE solver's constituent parts."""
import numpy as np

from puckworks.models.pannusch2024 import solver as ps
from puckworks.models.pannusch2024 import closures as pc


def test_upwind_exact_for_polynomials():
    """5-point biased-upwind first-derivative matrix is exact to degree 4."""
    n = 200
    z = np.linspace(0, 1, n)
    D = ps.five_point_biased_upwind(n, z[1] - z[0], 1.0)
    for k in range(1, 5):
        got = D @ (z ** k)
        assert np.max(np.abs(got - k * z ** (k - 1))) < 1e-10


def test_jac_sparsity_structure():
    """Jacobian pattern: banded liquid + grain coupling + mcum<-outlet."""
    nz = 20
    S = ps._jac_sparsity(nz).toarray()
    assert S.shape == (3 * nz + 2, 3 * nz + 2)
    assert S[5, 5] and S[5, nz + 5] and S[5, 2 * nz + 5]   # liquid <- self + grains
    assert S[nz + 5, 5] and S[2 * nz + 5, 5]                # grains <- liquid
    assert S[3 * nz + 1, nz - 1]                            # mcum <- outlet liquid
    assert not S[5, 10]                                     # outside advection band


def test_closures_physical_anchors():
    """Water viscosity/density at 90 C; van't Hoff identity at Tref."""
    assert abs(float(pc.water_viscosity(363.15)) - 3.15e-4) / 3.15e-4 < 0.02
    assert abs(float(pc.water_density(363.15)) - 962) < 12
    assert abs(float(pc.vant_hoff_K(pc.TREF_K, 0.81, -371)) - 0.81) < 1e-9


def test_single_experiment_reproduces_kinetics():
    """One experiment/solute forward solve tracks the measured decay."""
    exps = ps._exp_kinetics()
    params = ps._solute_params()
    mape = ps.mape_for_experiment(exps[7], "caffeine", params["caffeine"])
    assert mape is not None and mape < 8.0        # exp7 caffeine ~3.9%
