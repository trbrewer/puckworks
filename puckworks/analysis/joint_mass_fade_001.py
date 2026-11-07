"""One mass-driven hydraulic fade of J1; research only, fixed R0 chemistry.

Specification: docs/research/JOINT_MASS_FADE_001/PLAN.md. gamma has units 1/g;
the inherited theta[4] remains fixed Mc, never gamma. tau0 stays last.
"""
import math

import numpy as np

from . import joint_clock_001 as J
from . import joint_clock_001_run as R

ORDER = ("a", "Pstar", "n", "Pd", "gamma", "tau0")


def coordinates(parameters):
    p = np.asarray(parameters, dtype=float)
    if p.shape != (6,):
        raise ValueError("Expected (a,Pstar,n,Pd,gamma,tau0)")
    z = J.coordinates(p[[0, 1, 2, 3, 5]], "J1")
    return np.r_[z[:4], p[4], z[-1]]


def physical(z):
    z = np.asarray(z, dtype=float)
    if z.shape != (6,):
        raise ValueError("Expected six coordinates with tau0 last")
    p = J.physical(z[[0, 1, 2, 3, 5]], "J1")
    return np.r_[p[:4], z[4], p[-1]]


def bounds():
    return (coordinates([.001, .5, 1., .1, 0., 0.]),
            coordinates([20., 100., np.inf, 100., .2, 100.]))


def prepare(source, parameters, mc, dt=.02, cells=256):
    p = np.asarray(parameters, dtype=float)
    if p.shape != (6,) or not np.isfinite(p).all() or not (0 <= p[4] <= .2):
        raise ValueError("Invalid fade parameters")
    if not math.isfinite(mc) or mc <= 0:
        raise ValueError("Invalid fixed Mc")
    return J.Prepared(source["predict_times_s"], source["predict_pressure_bar"],
                      np.r_[p[:4], mc], "W1", [p[-1]], dt, cells,
                      source["predict_horizon_s"], gamma=float(p[4]))


def regime(gamma, mc):
    product = gamma*mc
    if gamma == 0:
        return dict(gamma_Mc=product, regime="rises_to_limit", Mstar_g=None,
                    liquid_maximum="no interior peak")
    if product < 1:
        return dict(gamma_Mc=product, regime="rises_then_falls",
                    Mstar_g=mc*math.log(1/product), liquid_maximum="interior if mass reaches Mstar")
    return dict(gamma_Mc=product, regime="declines_from_breakthrough", Mstar_g=None,
                liquid_maximum="breakthrough boundary")


def objective(data, parameters, held, dt=.02, accelerate=True):
    sources = [s for s in data["sources"] if held is None or s["nominal_pressure_bar"] != held]
    mc = data["bank"][R.label(held)][4]
    parts, detectors = [], []
    for source in sources:
        pred = prepare(source, parameters, mc, dt)
        obs = pred.observer(source["observer_times_s"], accelerate=accelerate)
        parts.append(J.loss_components(pred.scored_flow(source["fit_times_s"]),
            source["fit_flow_g_s"], obs, source["observed_onset_for_scoring_only_s"]))
        detectors.append(obs["detected"])
    conditions = sorted({s["nominal_pressure_bar"] for s in sources})
    groups = [np.array([i for i,s in enumerate(sources) if s["nominal_pressure_bar"] == p]) for p in conditions]
    means = np.array([np.asarray(parts)[g].mean(axis=0) for g in groups])
    flow, onset = means.mean(axis=0)
    if not np.isfinite(flow+onset):
        raise ValueError("Nonfinite objective is unavailable")
    return dict(parameters=list(map(float, parameters)), objective=float(flow+onset),
        flow_component=float(flow), onset_component=float(onset), detected=sum(detectors),
        intended=len(sources), available=len(sources),
        condition_components=[dict(pressure_bar=p, flow=float(v[0]), onset=float(v[1]),
            detected=int(np.sum(np.asarray(detectors)[g])), brews=len(g)) for p,v,g in zip(conditions,means,groups)])
