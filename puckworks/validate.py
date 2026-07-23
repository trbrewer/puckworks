"""Public-boundary units, array, and trace validation (P1.1).

ADDITIVE, opt-in helpers — importing this module changes NO numerical behaviour. It gives callers
explicit unit conversions at boundaries, early-failing array checks (finite / positive / fraction
/ monotonic time / aligned lengths / dimensionality), a controlled closure vocabulary, and a
versioned `Trace` structure to replace free-form trace dicts where a caller chooses to.

Units policy (see docs/UNITS_POLICY.md): SI internally — Pa, m, s, kg, K, dimensionless. Machine-
facing bar-gauge appears ONLY at input/output boundaries; convert with `bar_gauge_to_pa` /
`pa_to_bar_gauge`. The `is_plausible_pressure_pa` guard catches the common factor-of-100000
bar-vs-pascal error.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

import numpy as np

BAR_PA = 1.0e5   # 1 bar = 100000 Pa

# a shot pressure in Pa is O(1e5..1.2e6); a value below this floor is almost certainly bar (or a
# unit slip), above the ceiling is almost certainly a factor error.
_PRESSURE_PA_FLOOR = 1.0e4     # 0.1 bar
_PRESSURE_PA_CEIL = 5.0e6      # 50 bar

# controlled finite vocabularies (Literal-style); additive — validators are opt-in
CLOSURES = ("poroelastic", "ck")


class Closure(str, Enum):
    POROELASTIC = "poroelastic"
    CK = "ck"


# ---- units -------------------------------------------------------------------------------
def bar_gauge_to_pa(p_bar_gauge):
    """Machine bar-gauge overpressure -> Pa (gauge). Boundary conversion only."""
    return np.asarray(p_bar_gauge, float) * BAR_PA if np.ndim(p_bar_gauge) else float(p_bar_gauge) * BAR_PA


def pa_to_bar_gauge(p_pa):
    return np.asarray(p_pa, float) / BAR_PA if np.ndim(p_pa) else float(p_pa) / BAR_PA


def is_plausible_pressure_pa(p):
    """True iff `p` is in the plausible SI espresso range. Catches a bar value (~9) mistakenly
    passed where Pa (~9e5) is expected — the classic factor-of-100000 error."""
    try:
        arr = np.asarray(p, float)
    except (TypeError, ValueError):
        return False
    return bool(np.all(np.isfinite(arr)) and np.all(arr >= _PRESSURE_PA_FLOOR)
               and np.all(arr <= _PRESSURE_PA_CEIL))


def assert_pressure_pa(p, name="pressure"):
    if not is_plausible_pressure_pa(p):
        raise ValueError("%s = %r is not a plausible SI pressure [%g..%g Pa] — is it bar-gauge "
                         "(off by ~1e5)?" % (name, p, _PRESSURE_PA_FLOOR, _PRESSURE_PA_CEIL))
    return p


# ---- array validators (raise ValueError early with actionable messages) ------------------
def require_finite(a, name="array"):
    arr = np.asarray(a, float)
    if not np.all(np.isfinite(arr)):
        raise ValueError("%s contains non-finite values (nan/inf)" % name)
    return arr


def require_positive(a, name="array"):
    arr = require_finite(a, name)
    if np.any(arr <= 0):
        raise ValueError("%s must be strictly positive" % name)
    return arr


def require_nonnegative(a, name="array"):
    arr = require_finite(a, name)
    if np.any(arr < 0):
        raise ValueError("%s must be nonnegative" % name)
    return arr


def require_fraction(a, name="fraction"):
    """0 <= x <= 1 (porosity, share, extraction fraction, ...)."""
    arr = require_finite(a, name)
    if np.any(arr < 0) or np.any(arr > 1):
        raise ValueError("%s must lie in [0, 1]" % name)
    return arr


def require_monotonic_increasing(t, name="time", strict=True):
    arr = np.asarray(t, float)
    if arr.ndim != 1:                      # scalar/2-D would make np.diff raise a raw NumPy error
        raise ValueError("%s must be 1-D, got %d-D" % (name, arr.ndim))
    if arr.size < 1:
        raise ValueError("%s must be nonempty" % name)
    if not np.all(np.isfinite(arr)):
        raise ValueError("%s contains non-finite values (nan/inf)" % name)
    d = np.diff(arr)
    if strict and np.any(d <= 0):
        raise ValueError("%s must be strictly increasing (found a non-increasing step)" % name)
    if not strict and np.any(d < 0):
        raise ValueError("%s must be non-decreasing" % name)
    return arr


def require_aligned(name_to_array):
    """All arrays share one length (each must be 1-D). Returns that length."""
    lengths = {}
    for k, v in name_to_array.items():
        arr = np.asarray(v)
        if arr.ndim != 1:
            raise ValueError("%s must be 1-D for alignment, got %d-D" % (k, arr.ndim))
        lengths[k] = arr.shape[0]
    if len(set(lengths.values())) > 1:
        raise ValueError("misaligned array lengths: %r" % lengths)
    return next(iter(lengths.values())) if lengths else 0


def require_ndim(a, ndim, name="array"):
    arr = np.asarray(a)
    if arr.ndim != ndim:
        raise ValueError("%s must be %d-D, got %d-D" % (name, ndim, arr.ndim))
    return arr


def require_closure(name):
    if name not in CLOSURES:
        raise ValueError("unknown closure %r (allowed: %s)" % (name, ", ".join(CLOSURES)))
    return name


# ---- versioned trace structure (additive; replaces a free-form dict where a caller opts in) ---
TRACE_SCHEMA_VERSION = 1


@dataclass
class Trace:
    """A validated multi-channel time trace. `time` is seconds (monotonic); `channels` maps a
    channel name to a same-length array; `units` maps the channel name to its unit string; missing
    samples are represented as nan (never silently dropped)."""
    time: np.ndarray
    channels: dict                      # name -> np.ndarray (aligned with time)
    units: dict                         # name -> unit str
    source: str = ""
    schema_version: int = TRACE_SCHEMA_VERSION
    _validated: bool = field(default=False, repr=False)

    def validate(self):
        t = require_monotonic_increasing(self.time, "time", strict=True)
        if not isinstance(self.channels, dict) or not isinstance(self.units, dict):
            raise ValueError("channels and units must both be mappings")
        if set(self.units) != set(self.channels):     # exact coverage: no missing/extra unit keys
            raise ValueError("units keys %r must exactly match channel keys %r"
                             % (sorted(self.units), sorted(self.channels)))
        if not isinstance(self.source, str):
            raise ValueError("source must be a string")
        if self.schema_version != TRACE_SCHEMA_VERSION:
            raise ValueError("unsupported trace schema_version %r (expected %d)"
                             % (self.schema_version, TRACE_SCHEMA_VERSION))
        for name, arr in self.channels.items():
            a = np.asarray(arr, float)
            if a.ndim != 1:
                raise ValueError("channel %r must be 1-D, got %d-D" % (name, a.ndim))
            if a.shape[0] != t.shape[0]:
                raise ValueError("channel %r length %d != time length %d"
                                 % (name, a.shape[0], t.shape[0]))
            # NaN is the explicit missing-sample marker; +/-inf is never allowed (would break JSON)
            if np.any(np.isinf(a)):
                raise ValueError("channel %r contains infinite values "
                                 "(only finite values or nan-missing are allowed)" % name)
            unit = self.units[name]
            if not isinstance(unit, str) or not unit.strip():
                raise ValueError("channel %r has an empty or non-string unit" % name)
        object.__setattr__(self, "_validated", True)
        return self

    def to_dict(self):
        if not self._validated:            # never serialize an unvalidated trace
            self.validate()
        return {"schema_version": self.schema_version, "source": self.source,
                "time": [float(v) for v in np.asarray(self.time, float)],
                "units": dict(self.units),
                "channels": {k: [None if np.isnan(v) else float(v) for v in np.asarray(arr, float)]
                             for k, arr in self.channels.items()}}

    def to_json(self, **kwargs):
        """Canonical strict JSON (allow_nan=False). Safe because validate() rejects +/-inf and
        to_dict() maps nan-missing to null."""
        import json
        return json.dumps(self.to_dict(), allow_nan=False, **kwargs)
