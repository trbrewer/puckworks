"""Research-only parameter injection and reductions for absolute fraction TDS.

Pannusch et al., Mendeley 10.17632/y2tz67f6ry.1; derived data CC-BY-NC-3.0.
Uses the existing conservative constant-input engine; no production changes.
"""
from __future__ import annotations

from dataclasses import dataclass
import numpy as np

from puckworks.analysis import pannusch_equilibrium_limit as eq
from puckworks.models.pannusch2024 import solver as ps
from puckworks.models.pannusch2024 import temperature_history_fv as fv

TRAIN = tuple(f'FIT-C{i:02}' for i in (9, 10, 11, 14, 15))
TEST = eq.CONDITIONS
FRACTIONS = eq.FRACTIONS


@dataclass(frozen=True)
class Scenario:
    temperature_C: float
    flow_label: float
    parameters: dict
    start_s: float = 0.
    grind: float = 1.7

    @property
    def Q(self):
        return self.flow_label / 1000 / eq.RHO_COMMON

    @property
    def T(self):
        return self.temperature_C + 273.15

    def system(self, cells):
        system = fv._System('tds', self.grind, self.Q, cells)
        system.sp.update(self.parameters)
        system.Cstar = self.parameters['c_s0']
        return system

    def constants(self):
        s = self.system(1)
        K = s.coefficients(self.T)[0]
        H = ps.ALPHA_L + (s.as1 + ps.PHI_V2*s.as2)/K
        return dict(K=K, c_s0=s.Cstar, front_s=self.start_s+ps.ACS*ps.L*H/self.Q)


def predict(arm, parameters, shots, cells=200, halves=False):
    """One trajectory per shared condition, on the union of replicate boundaries."""
    output, diagnostics = {}, []
    for condition in sorted({p['condition'] for p in shots}):
        group = [p for p in shots if p['condition'] == condition]
        p = group[0]
        if any((q['temperature_C'], q['flow_label'], q['start_s'], q['grind']) !=
               (p['temperature_C'], p['flow_label'], p['start_s'], p['grind']) for q in group):
            raise ValueError('condition does not have shared programmed inputs')
        s = Scenario(p['temperature_C'], p['flow_label'], parameters, p['start_s'], p['grind'])
        boundaries = np.unique(np.concatenate([np.ravel(q['windows']) for q in group]))
        union = np.column_stack([boundaries[:-1], boundaries[1:]])
        if arm == 'F':
            c, diag = eq.finite_averages(s, union, cells=cells, halves=halves)
            diagnostics.append(dict(condition=condition, **diag))
        elif arm == 'E':
            c = eq.equilibrium_averages(s, union)
        else:
            raise ValueError('unknown mechanistic arm')
        for q in group:
            values = []
            for lo, hi in q['windows']:
                mask = (union[:, 0] >= lo) & (union[:, 1] <= hi)
                values.append(100*np.dot(c[mask], np.diff(union[mask], axis=1).ravel()) /
                              (eq.RHO_COMMON*(hi-lo)))
            output[q['shot']] = values
    return np.array([output[p['shot']] for p in shots]), diagnostics


def weights(shots):
    counts = {c: sum(p['condition'] == c for p in shots) for c in {p['condition'] for p in shots}}
    return np.array([np.asarray(p['masses_g'])/sum(p['masses_g']) /
                     counts[p['condition']]/len(counts) for p in shots])


def amplitude(unit_prediction, observed, weight, bounds):
    denominator = np.sum(weight*unit_prediction**2)
    if denominator <= 0:
        raise ValueError('unresolved amplitude')
    return float(np.clip(np.sum(weight*unit_prediction*observed)/denominator, *bounds))


def shot_metrics(prediction, observed, masses):
    w = np.asarray(masses)/np.sum(masses)
    residual = np.asarray(prediction)-observed
    b = float(np.dot(w, residual))
    return dict(R=float(np.sqrt(np.dot(w, residual**2))), B=b, A=abs(b))


def aggregate(rows):
    return {k: float(np.mean([np.mean([r[k] for r in rows if r['condition'] == c])
                             for c in sorted({r['condition'] for r in rows})]))
            for k in ('R', 'B', 'A')}


def band(gain, low=.10, high=.25):
    return 'worse' if gain < 0 else 'small' if gain < low else 'moderate' if gain < high else 'large'


def interval_bands(a, b, low=.10, high=.25):
    """All bands attained on a closed sensitivity interval, including interiors."""
    return sorted({band(x, low, high) for x in [a, b, 0., low, high] if a <= x <= b})
