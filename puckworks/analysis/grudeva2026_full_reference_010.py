"""Independent analysis-only Grudeva Eqs. 23–29, synthetic case 010.

Grudeva, Moroney & Foster, DOI 10.1017/S095679252500018X (CC-BY-4.0).
No reduced-model dynamics, author code, runtime registration or clipping.
See the scoped 010 contract for geometry, startup and qualification limits.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass

import numpy as np
from scipy.integrate import solve_ivp
from scipy.linalg import eigh
from scipy.sparse import lil_matrix


@dataclass(frozen=True)
class Case:
    identity: str = "SYNTHETIC-GRUDEVA-FINITE-RATE-010-A"
    equation_source: str = "GRUDEVA-EJAM-2026-E23-E29"
    phi_f: float = .64
    phi_b: float = .16
    phi_l: float = .20
    phi_T: float = .20
    varphi_lb: float = 0.
    q: float = 1.
    initial: float = 1.388
    epsilon: float = .01
    D_f: float = 100.
    D_b: float = 1.
    D_l: float = .01
    radius_ratio: float = .1
    b_f: float = 80 / 41
    b_b: float = 2 / 41
    horizon: float = 8.

    @property
    def weights(self):
        return np.array([self.phi_f, self.phi_b]) / self.phi_T

    @property
    def Q(self):
        return 1 / (3 * self.weights)

    @property
    def k(self):
        return np.array([self.b_f, self.b_b]) / self.epsilon

    @property
    def M0(self):
        return float(self.initial * sum(self.weights))

    def check(self):
        """Synthetic identity is deliberately not a general physical case API."""
        if asdict(self) != asdict(Case()):
            raise ValueError("Only the declared synthetic case is supported")
        dimensional_b = 3 * np.array([self.phi_f / self.radius_ratio, self.phi_b])
        np.testing.assert_allclose(dimensional_b / dimensional_b.mean(),
                                   [self.b_f, self.b_b], rtol=1e-14)
        np.testing.assert_allclose(3 * self.Q * self.weights, 1, rtol=1e-14)
        assert self.D_f / self.D_b == 1 / self.radius_ratio**2 or np.isclose(
            self.D_f / self.D_b, 1 / self.radius_ratio**2)


@dataclass(frozen=True)
class Settings:
    axial: int = 128
    fines: int = 16
    boulders: int = 16
    rtol: float = 1e-8
    atol: float = 1e-10
    max_step: float = .02
    startup: float = 1e-6

    def check(self):
        if min(self.axial, self.fines, self.boulders) < 3:
            raise ValueError("At least three cells/shells are required")
        if not 0 < self.startup <= 1e-4:
            raise ValueError("Startup must be explicit and <=1e-4")
        if min(self.rtol, self.atol, self.max_step) <= 0:
            raise ValueError("Positive temporal controls required")


class Sphere:
    """Conservative shell averages and finite surface resistance."""

    def __init__(self, n, diffusivity, Q, k):
        self.faces = 1 - (1 - np.linspace(0, 1, n + 1))**3
        self.r = (self.faces[1:] + self.faces[:-1]) / 2
        self.volume = np.diff(self.faces**3) / 3
        self.D, self.Q, self.k = diffusivity, Q, k
        self.h = diffusivity / (1 - self.r[-1])
        self.conductance = diffusivity * self.faces[1:-1]**2 / np.diff(self.r)
        # Symmetric diffusion generator in sqrt(volume)-weighted coordinates.
        n = len(self.r)
        matrix = np.zeros((n, n))
        for j, g in enumerate(self.conductance):
            matrix[j, j] -= g / self.volume[j]
            matrix[j + 1, j + 1] -= g / self.volume[j + 1]
            matrix[j, j + 1] = matrix[j + 1, j] = g / np.sqrt(
                self.volume[j] * self.volume[j + 1])
        self.eigenvalues, self.eigenvectors = eigh(matrix)
        # The Neumann zero mode is exactly the conserved constant, not a loss rate.
        self.eigenvalues[-1] = 0.

    def transfer(self, grain, liquid):
        last = grain[..., -1]
        saturated_flux = self.Q * self.k * (1 - liquid)
        saturated_surface = last - saturated_flux / self.h
        robin_flux = self.Q * self.k * (last - liquid) / (1 + self.Q * self.k / self.h)
        flux = np.where(saturated_surface >= 1, saturated_flux, robin_flux)
        surface = last - flux / self.h
        return flux / self.Q, surface

    def rhs(self, grain, transfer):
        flux = np.zeros((*grain.shape[:-1], grain.shape[-1] + 1))
        flux[..., 1:-1] = -self.conductance * np.diff(grain, axis=-1)
        flux[..., -1] = self.Q * transfer
        return -np.diff(flux, axis=-1) / self.volume

    def mean(self, grain):
        return 3 * (grain @ self.volume)

    def constant_flux_start(self, age, initial):
        """Exact semi-discrete response; startup control is not a spatial oracle."""
        age = np.asarray(age)
        forcing = np.zeros(len(self.r))
        forcing[-1] = -self.Q * self.k / np.sqrt(self.volume[-1])
        amplitude = self.eigenvectors.T @ forcing
        rate = self.eigenvalues
        integral = np.empty((*age.shape, len(rate)))
        integral[..., :-1] = np.expm1(age[..., None] * rate[:-1]) / rate[:-1]
        integral[..., -1] = age
        return initial + (integral * amplitude) @ self.eigenvectors.T / np.sqrt(self.volume)


def limited_slopes(values):
    """Minmod slopes in cell-index units; no concentration clipping."""
    slopes = np.zeros_like(values)
    left, right = np.diff(values, axis=0)[:-1], np.diff(values, axis=0)[1:]
    slopes[1:-1] = np.where(left * right > 0,
                            np.sign(left) * np.minimum(np.abs(left), np.abs(right)), 0.)
    slopes[0] = values[1] - values[0]
    slopes[-1] = values[-1] - values[-2]
    return slopes


def geometric_amount_rhs(grain, faces, initial):
    """At fixed xi, grain transport representing stationary physical material."""
    n = len(grain)
    slopes = limited_slopes(grain)
    trace = grain[1:] - .5 * slopes[1:]
    flux = np.empty((n + 1, grain.shape[-1]))
    flux[0] = 0
    flux[1:-1] = -faces[1:-1, None] * trace
    flux[-1] = -initial
    return -n * np.diff(flux, axis=0)


def geometric_rhs(grain, t, faces, initial):
    return (geometric_amount_rhs(grain, faces, initial)-grain)/t


def liquid_flux(liquid, s, moving, diffusivity=.01, q=1.):
    """ALE relative face flux; endpoint values have quadratic FV closures."""
    n = len(liquid)
    dz = s / n
    faces = np.linspace(0, 1, n + 1)
    flux = np.empty(n + 1)
    flux[0] = -diffusivity * (7 * liquid[0] - liquid[1]) / (2 * dz)
    flux[1:-1] = ((q - moving * faces[1:-1]) * (liquid[:-1] + liquid[1:]) / 2
                  - diffusivity * np.diff(liquid) / dz)
    outlet = (7 * liquid[-1] - liquid[-2]) / 6
    flux[-1] = (q - moving) * outlet
    return flux, outlet


class Model:
    def __init__(self, settings=Settings(), case=Case()):
        settings.check()
        case.check()
        self.settings, self.case = settings, case
        self.n = settings.axial
        self.width = 1 + settings.fines + settings.boulders
        self.faces = np.linspace(0, 1, self.n + 1)
        self.xi = (self.faces[1:] + self.faces[:-1]) / 2
        self.spheres = [Sphere(settings.fines, case.D_f, case.Q[0], case.k[0]),
                        Sphere(settings.boulders, case.D_b, case.Q[1], case.k[1])]
        self.slices = [slice(1, 1 + settings.fines), slice(1 + settings.fines, self.width)]

    def split(self, y, t):
        return y[:-2].reshape(self.n, self.width)/min(t, 1.)

    def startup(self, t):
        c, n = self.case, self.n
        state = np.empty((n, self.width))
        # Exact axial cell averages of K*(t*z-z*z/2)/D.
        a, b = t * self.faces[:-1], t * self.faces[1:]
        state[:, 0] = sum(c.k) / c.D_l * (t * (a + b) / 2 - (a*a + a*b + b*b) / 6)
        for sphere, sl in zip(self.spheres, self.slices):
            # Integrate cohorts across each wet cell, not just its center age.
            x, w = np.polynomial.legendre.leggauss(8)
            ages = t - ((a + b)[:, None] + (b - a)[:, None] * x) / 2
            states = sphere.constant_flux_start(ages, c.initial)
            state[:, sl] = np.einsum('j,ijk->ik', w / 2, states)
        return np.r_[t*state.ravel(), -sum(c.k) * t*t / 2, 0.]

    def rhs(self, t, y, moving):
        state = self.split(y,t)
        s = t if moving else 1.
        flux, outlet = liquid_flux(state[:, 0], s, int(moving), self.case.D_l)
        rate = np.zeros_like(state)
        rate[:, 0] = -self.n * np.diff(flux)
        for sphere, sl in zip(self.spheres, self.slices):
            transfer, surface = sphere.transfer(state[:, sl], state[:, 0])
            rate[:, 0] += s*transfer
            rate[:, sl] = s*sphere.rhs(state[:, sl], transfer)
            if moving:
                rate[:, sl] += geometric_amount_rhs(state[:, sl], self.faces, self.case.initial)
        return np.r_[rate.ravel(), flux[0], 0. if moving else outlet]

    def sparsity(self):
        nstate = self.n * self.width + 2
        matrix = lil_matrix((nstate, nstate), dtype=int)
        for j in range(self.n):
            base = j * self.width
            matrix[base, base] = 1
            for sl in self.slices:
                matrix[base, base+sl.stop-1] = 1
                for k in range(sl.start, sl.stop):
                    matrix[base+k, base+max(sl.start, k-1):base+min(sl.stop, k+2)] = 1
                matrix[base+sl.stop-1, base] = 1
            for neighbor in range(max(0, j-2), min(self.n, j+3)):
                for k in range(self.width):
                    matrix[base+k, neighbor*self.width+k] = 1
        matrix[-2, :2*self.width:self.width] = 1
        matrix[-1, (self.n-2)*self.width:(self.n)*self.width:self.width] = 1
        return matrix.tocsc()

    def inventories(self, t, y):
        s = min(t, 1.)
        if t==0:
            return np.array([0.,0.,0.,self.case.M0])
        state = self.split(y,t)
        wet = [s * state[:, 0].mean()]
        wet += [s * weight * sphere.mean(state[:, sl]).mean()
                for sphere, sl, weight in zip(self.spheres, self.slices, self.case.weights)]
        return np.r_[wet, (1-s)*self.case.M0]


def integrate(settings=Settings(), case=Case(), capture=True, horizon=None):
    """Two BDF segments, preserving exact transition states; no campaign in CI."""
    model = Model(settings, case)
    final = case.horizon if horizon is None else horizon
    if final <= settings.startup:
        raise ValueError("Horizon must exceed startup")
    state = model.startup(settings.startup)
    segments = []
    jac = model.sparsity()
    for start, stop, moving in [(settings.startup, min(1., final), True), (1., final, False)]:
        if stop <= start:
            continue
        result = solve_ivp(lambda t, y: model.rhs(t, y, moving), (start, stop), state,
                           method="BDF", rtol=settings.rtol, atol=settings.atol,
                           max_step=settings.max_step, jac_sparsity=jac, dense_output=capture)
        segments.append((moving, result))
        state = result.y[:, -1].copy()
        if not result.success:
            break
    return model, segments
