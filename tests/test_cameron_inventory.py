"""One spherical population must set sources and both inventory endpoints."""
import numpy as np
import pytest

from puckworks.models.cameron2020 import extraction_bdf as cam


@pytest.mark.parametrize('gs', np.linspace(1.0, 2.5, 31))
def test_interpolated_geometry_has_one_phase_volume(gs):
    phi1, phi2, a2, b1, b2 = cam.grind_microstructure(gs)
    assert phi1 + phi2 == pytest.approx(cam.PHI_S, abs=1e-15)
    assert b1 * cam.A1 / 3 == pytest.approx(phi1, abs=1e-15)
    assert b2 * a2 / 3 == pytest.approx(phi2, abs=1e-15)


@pytest.mark.parametrize('gs', [1.0, 1.1, 1.5, 1.9, 2.0, 2.1, 2.3, 2.5])
@pytest.mark.parametrize('cs0', [118.0, 118.0 / cam.PHI_S])
def test_complete_inventory_uses_measured_phase_fractions(gs, cs0):
    result = cam.simulate_shot(gs, N=20, M=12, c_s0=cs0)
    phi1, phi2, a2, _, _ = cam.grind_microstructure(gs)
    volume = np.pi * cam.R0 ** 2 * cam.bed_depth(result.m_in)
    final = 0.0
    for phi, radius, concentration in [(phi1, cam.A1, result.cs1_final),
                                       (phi2, a2, result.cs2_final)]:
        # Independent shell-volume reducer; does not use BET or EY_solid.
        nodes = np.linspace(0, radius, concentration.shape[1])
        faces = np.r_[0, (nodes[1:] + nodes[:-1]) / 2, radius]
        weights = np.diff(faces ** 3) / radius ** 3
        final += volume * phi * np.mean(concentration @ weights)
        assert concentration.min() >= -1e-8
    initial = volume * (phi1 + phi2) * cs0
    retained = volume * (1 - cam.PHI_S) * np.mean(result.cl_final)
    assert initial == pytest.approx(final + retained + result.m_cup[-1], abs=2e-11)
    assert result.EY_solid == pytest.approx(result.EY, abs=1e-7)
    assert result.cl_final.min() >= -1e-8


def test_representative_axial_refinement_contracts():
    ey = [cam.simulate_shot(2.1, N=n, M=24).EY for n in (20, 40, 80)]
    assert 0 < ey[2] - ey[1] < ey[1] - ey[0] < 0.3
