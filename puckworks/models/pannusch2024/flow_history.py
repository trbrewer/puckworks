"""Immutable, strictly SI positive prescribed flow; no experimental clock mapping."""
from __future__ import annotations

from dataclasses import dataclass
import math
import numbers

import numpy as np

from . import temperature_history as th

InvalidFlowHistoryInput = th.InvalidTemperatureHistoryInput


def _real(value, name):
    if isinstance(value, (bool, np.bool_)) or not isinstance(value, numbers.Real):
        th._reject(f"{name} must be a finite real number")
    value = float(value)
    if not math.isfinite(value):
        th._reject(f"{name} must be a finite real number")
    return value


def _reals(values, name, minimum):
    try:
        a = np.asarray(values, dtype=object)
    except (TypeError, ValueError):
        th._reject(f"{name} must be a one-dimensional real sequence")
    if a.ndim != 1 or len(a) < minimum:
        th._reject(f"{name} has invalid shape or length")
    return tuple(_real(v, name) for v in a)


@dataclass(frozen=True)
class _FlowSegment:
    start_s: float
    end_s: float
    start_m3_s: float
    end_m3_s: float

    def value_m3_s(self, t_s):
        if not self.start_s <= t_s <= self.end_s:
            th._reject("segment flow query outside support")
        if self.end_s-self.start_s < 1e-300:
            return self.start_m3_s + (self.end_m3_s-self.start_m3_s)*((t_s-self.start_s)/(self.end_s-self.start_s))
        return self.start_m3_s + (self.end_m3_s-self.start_m3_s)*(t_s-self.start_s)/(self.end_s-self.start_s)


@dataclass(frozen=True)
class FlowHistory:
    """Constant interval edges or linear knots, with no extrapolation/endpoint holds.

    Constant intervals are left-closed/right-open, final endpoint included in the
    last interval. Duplicate times cannot represent jumps. Values are m^3/s.
    """
    times_s: tuple[float, ...]
    flows_m3_s: tuple[float, ...]
    kind: str
    units: str = "m^3/s"

    def __post_init__(self):
        t = _reals(self.times_s, "flow times", 2)
        q = _reals(self.flows_m3_s, "flows_m3_s", 1)
        if any(b <= a or not math.isfinite(b-a) for a, b in zip(t, t[1:])):
            th._reject("flow times must increase strictly with finite differences")
        if not isinstance(self.kind, str) or self.kind not in ("constant", "linear"):
            th._reject("flow kind must be constant or linear")
        if self.units != "m^3/s":
            th._reject("flow units must be m^3/s; no implicit conversion")
        if len(q) != len(t)-(self.kind == "constant") or any(not 1e-6 <= v <= 3e-6 for v in q):
            th._reject("flow count or 1e-6..3e-6 m^3/s domain violated")
        object.__setattr__(self, "times_s", t)
        object.__setattr__(self, "flows_m3_s", q)

    def _time(self, value):
        t = _real(value, "flow query time")
        if not self.times_s[0] <= t <= self.times_s[-1]:
            th._reject("flow query outside supplied history support")
        return t

    def _index(self, t):
        return min(int(np.searchsorted(self.times_s, t, side="right"))-1, len(self.times_s)-2)

    def value_m3_s(self, t_s):
        t = self._time(t_s)
        i = self._index(t)
        if self.kind == "constant":
            return self.flows_m3_s[i]
        a, b = self.times_s[i:i+2]
        if b-a < 1e-300:
            return self.flows_m3_s[i]+(self.flows_m3_s[i+1]-self.flows_m3_s[i])*((t-a)/(b-a))
        return self.flows_m3_s[i]+(self.flows_m3_s[i+1]-self.flows_m3_s[i])*(t-a)/(b-a)

    def integral(self, a, b):
        """Local analytic panel integrals; no subtraction of cumulative volumes."""
        a, b = self._time(a), self._time(b)
        if b < a:
            th._reject("flow integration bounds reversed")
        if a == b:
            return 0.
        parts = []
        for i in range(self._index(a), self._index(b)+1):
            left, right = self.times_s[i:i+2]
            lo, hi = max(a, left), min(b, right)
            if hi <= lo:
                continue
            q = self.flows_m3_s[i]
            if self.kind == "linear":
                if right-left < 1e-300 or not math.isfinite((lo-left)+(hi-left)):
                    # Exceptional clock scales: normalize before arithmetic that
                    # could overflow/underflow. Normal campaign arithmetic stays unchanged.
                    midpoint_fraction = ((lo-left)/(right-left)+(hi-left)/(right-left))/2
                    q += (self.flows_m3_s[i+1]-q)*midpoint_fraction
                else:
                    slope = (self.flows_m3_s[i+1]-q)/(right-left)
                    # Endpoint-local trapezoid, stable even for tiny delayed windows.
                    q += slope*((lo-left)+(hi-left))/2
            parts.append((hi-lo)*q)
        return math.fsum(parts)

    def integration_segments(self, start_s, end_s):
        start_s, end_s = self._time(start_s), self._time(end_s)
        if start_s >= end_s:
            th._reject("flow history must cover a nonempty model interval")
        segments = []
        for i, (left, right) in enumerate(zip(self.times_s, self.times_s[1:])):
            a, b = max(left, start_s), min(right, end_s)
            if a >= b:
                continue
            qa = qb = self.flows_m3_s[i]
            if self.kind == "linear":
                if right-left < 1e-300:
                    delta = self.flows_m3_s[i+1]-qa
                    qa, qb = qa+delta*((a-left)/(right-left)), qa+delta*((b-left)/(right-left))
                else:
                    slope = (self.flows_m3_s[i+1]-qa)/(right-left)
                    qa, qb = qa+slope*(a-left), qa+slope*(b-left)
            segments.append(_FlowSegment(a, b, qa, qb))
        return tuple(segments)
