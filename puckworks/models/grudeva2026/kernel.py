"""Independent spherical diffusion response derived from EJAM Eqs.68–70.

No upstream solver code is used. See the task contract for the correction to
printed Eq.71. The finite positive tail mode preserves inventory exactly.
"""
from __future__ import annotations

import numpy as np
from scipy.special import polygamma


def modal_spectrum(diffusivity: float, modes: int) -> tuple[np.ndarray, np.ndarray]:
    if not np.isfinite(diffusivity) or diffusivity <= 0:
        raise ValueError("diffusivity must be finite and positive")
    if isinstance(modes, bool) or not isinstance(modes, int) or modes < 2:
        raise ValueError("modes must be an integer >=2")
    n = np.arange(1, modes + 1, dtype=float)
    weights = 6 / (np.pi * n) ** 2
    rates = (np.pi * n) ** 2 * diffusivity
    tail_weight = 6 / np.pi**2 * polygamma(1, modes + 1)
    tail_integral = polygamma(3, modes + 1) / (np.pi**4 * diffusivity)
    return np.r_[weights, tail_weight], np.r_[rates, tail_weight / tail_integral]


def spherical_history(times, boundary, initial: float, *, diffusivity=1.0,
                      q_b=1.0, modes=128) -> dict:
    """Exact decaying recurrence for a piecewise-linear Eulerian boundary.

    ``times[0]`` is the desaturation clock t0, which may be nonzero. The initial
    surface jump has an integrable infinite flux; its instantaneous flux is None.
    Flux can be negative when the boundary drives uptake. No state is clipped.
    """
    t, c = np.asarray(times, float), np.asarray(boundary, float)
    if t.ndim != 1 or t.size < 2 or c.shape != t.shape:
        raise ValueError("times/boundary must be matching one-dimensional arrays")
    if not np.all(np.isfinite(t)) or not np.all(np.isfinite(c)) or np.any(np.diff(t) <= 0):
        raise ValueError("finite boundary and strictly increasing times required")
    if not np.isfinite(initial) or initial < 0 or np.any(c < 0):
        raise ValueError("nonnegative finite concentrations required")
    if not np.isfinite(q_b) or q_b <= 0:
        raise ValueError("q_b must be finite and positive")
    w, lam = modal_spectrum(diffusivity, modes)
    h = np.full(w.size, initial - c[0])
    mean = [float(initial)]
    flux = [0.0 if initial == c[0] else None]
    for dt, old, new in zip(np.diff(t), c[:-1], c[1:]):
        decay = np.exp(-lam * dt)
        h = h * decay + (new - old) / dt * np.expm1(-lam * dt) / lam
        mean.append(float(new + w @ h))
        flux.append(float((w * lam) @ h / (3 * q_b)))
    return {"times": t.tolist(), "mean": mean, "flux": flux,
            "transferred_per_grain_volume": [float(initial - b) for b in mean],
            "initial_flux_reason": None if flux[0] is not None else
            "Integrable short-age singularity; instantaneous flux at activation is unavailable.",
            "modes": modes, "tail": "positive inventory-and-integrated-relaxation matched mode"}
