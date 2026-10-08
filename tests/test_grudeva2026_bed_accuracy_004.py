"""Independent integral oracles; no full canonical trajectory in software QA."""
import numpy as np
import pytest
from scipy.linalg import expm

from puckworks.analysis import grudeva2026_bed_accuracy_004 as ref
from puckworks.analysis import grudeva2026_conservative_003 as old


@pytest.mark.parametrize('fraction', [.2, .5, .8, 1.])
def test_old_trace_fails_exact_curved_integrals_and_004_reproduces(fraction):
    n = 64
    s = (32+fraction)/n
    faces = np.r_[np.arange(33)/n, s]
    primitive = lambda z: .3*(z+2*(s-z)**1.5/(3*np.sqrt(s)))
    means = np.diff(primitive(faces))/np.diff(faces)
    assert abs(old.face_values(means, faces)[-1]-.3) > .01
    assert ref.face_values(means, faces)[-1] == pytest.approx(.3, abs=2e-12)
    for point in (s-.003, s-.008, s):
        expected = .3*(1-np.sqrt((s-point)/s))
        assert ref.point_liquid(point, faces, means) == pytest.approx(expected, abs=2e-12)


@pytest.mark.parametrize('offset', [0., .001, .03, .2])
def test_reconstruction_integrates_stored_means_before_and_after_exit(offset):
    faces = np.r_[np.linspace(0., .4, 18), .403]
    anchor = faces[-1]+offset
    center = (faces[:-1]+faces[1:])/2
    means = .2*center+.1*(ref.root_means(faces, anchor)-np.sqrt(anchor))
    points, weights = np.polynomial.legendre.leggauss(160)
    for i, (left, right) in enumerate(zip(faces[:-1], faces[1:])):
        # Quadratic coordinate change resolves the root at the right endpoint.
        u = (points+1)/2
        z = right-(right-left)*u*u
        vals = np.array([ref.point_liquid(p, faces, means, anchor) for p in z])
        actual = weights @ (u*vals)
        assert actual == pytest.approx(means[i], abs=2e-12)


def test_constant_linear_and_one_cell_scalar_compatibility():
    for faces in (np.array([0., .003]), np.array([0., .03, .09, .2])):
        for speed in (0., .08):
            h, slope = .003, .2
            new = faces.copy()
            new[-1] += speed*h
            c0 = slope*(faces[:-1]+faces[1:])/2
            source = h*slope*(np.diff(faces)+np.diff(new))/2
            c1, _, _, residual = ref.transport_solve(c0, faces, new, h, source,
                                                     np.zeros(len(c0)))
            assert c1 == pytest.approx(slope*(new[:-1]+new[1:])/2, abs=2e-15)
            assert residual < 1e-16
            c1, _, _, _ = ref.transport_solve(np.full(len(c0), .3), faces, new,
                                              h, np.zeros(len(c0)),
                                              np.zeros(len(c0)), inlet=.3)
            assert c1 == pytest.approx(.3, abs=2e-15)
    radial = ref.Radial(8, 0.)
    c, j, f, audit = ref.step(radial, np.zeros(1), np.zeros((8, 1)),
                             np.zeros(2), .01)
    assert f[-1] == pytest.approx(.01/5.4416, rel=1e-12)
    assert c == pytest.approx(0., abs=1e-15)
    assert j == pytest.approx(ref.INITIAL*f[-1], abs=1e-17)
    assert abs(audit['front_residual']) < 1e-17


@pytest.mark.parametrize('initial,boundary', [(1.388, .2), (.1, .8), (.7, .7)])
def test_paired_signed_exchange_and_fixed_memory(initial, boundary):
    radial = ref.Radial(24)
    faces = np.array([0., .02, .07, .095])
    c0 = np.full(3, boundary)
    j0 = np.full((24, 3), initial)*np.diff(faces)
    c1, j1, new, audit = ref.step(radial, c0, j0, faces, .001, fixed=True,
                                 offset=.02, exit_speed=.1)
    # Independent physical-shell exponential with a linear time boundary.
    w, lower, diagonal, upper, forcing, _ = radial.op
    matrix = np.zeros((26, 26))
    matrix[:24, :24] = np.diag(diagonal)+np.diag(lower, -1)+np.diag(upper, 1)
    matrix[:24, 24] = forcing
    matrix[24, 25] = 1.
    for k in range(3):
        state = np.r_[np.full(24, initial), c0[k], (c1[k]-c0[k])/.001]
        expected = (expm(.001*matrix)@state)[:24]*np.diff(faces)[k]
        actual = radial.shells(j1)[:, k]
        # The inherited similarity transform amplifies shell-center roundoff
        # by 1/sqrt(shell volume). Test actual physical amounts under the
        # declared 256-epsilon rule, using L1 so cancellation cannot pass.
        error = float(w @ abs(actual-expected))
        participating = float(w @ (abs(actual)+abs(expected)))
        assert error <= old.ALGEBRA_RTOL*participating
    balance = (ref.CAPACITY*np.diff(new)@(c1-c0)
               +ref.DELTA*sum(radial.means(j1-j0))+sum(np.diff(audit['face_amount'])))
    assert abs(balance) <= old.ALGEBRA_RTOL*audit['algebra_scale']+audit['linear_residual']
    assert np.array_equal(faces, new)


def test_unchanged_support_and_helper_lineage():
    assert ref.Radial is old.Radial
    assert ref.phase_integrals is old.phase_integrals
    assert ref.transfer_amounts is old.transfer_amounts
    t, z = ref.observation_support(8.)
    assert len(t) == 395 and len(z) == 220 and t[-1] == 8 and z[-1] == 1
    with pytest.raises(ValueError):
        ref.point_liquid(1.1, np.array([0., 1.]), np.array([.2]))


def test_zero_volume_cell_crossing_bracket_uses_positive_support():
    radial=ref.Radial(32)
    faces=np.array([0., .01, .01])
    c=np.array([.1,.2])
    j=np.c_[np.full(32,.01*ref.INITIAL),np.zeros(32)]
    c1,j1,f,audit=ref.step(radial,c,j,faces,.001)
    assert f[-1]>.01 and np.all(np.isfinite(c1))
    assert audit['transfer_residual']<=old.ALGEBRA_RTOL*audit['algebra_scale']+audit['linear_residual']
