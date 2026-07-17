"""Product enums — four orthogonal result dimensions (issue #32).

Series origin, availability, and explanation compatibility are SEPARATE concepts. Evidence strength
is a fourth dimension carried by :class:`~puckworks.product._records.EvidenceReference` and preserves
the source vocabulary — it is never derived from compatibility or fit quality.
"""
from __future__ import annotations

from enum import Enum


class SeriesKind(str, Enum):
    """Origin of an *available* numerical series. Not an availability flag."""

    MEASURED = "measured"
    DERIVED = "derived"
    FITTED = "fitted"
    PREDICTED = "predicted"
    SIMULATED = "simulated"


class AvailabilityStatus(str, Enum):
    """Whether a result exists, recorded independently of its origin."""

    AVAILABLE = "available"
    UNAVAILABLE = "unavailable"
    UNSUPPORTED = "unsupported"
    FAILED = "failed"


class CompatibilityStatus(str, Enum):
    """How an explanation candidate relates to the observations. Never evidence strength."""

    COMPATIBLE = "compatible"
    PARTLY_COMPATIBLE = "partly_compatible"
    CONTRADICTED = "contradicted"
    INSUFFICIENT_EVIDENCE = "insufficient_evidence"
    OUTSIDE_MODEL_SCOPE = "outside_model_scope"


class RecordKind(str, Enum):
    """Whether the bundled input is one run or an aggregate."""

    SINGLE_SHOT = "single_shot"
    AGGREGATE_REFERENCE_CASE = "aggregate_reference_case"


__all__ = [
    "SeriesKind",
    "AvailabilityStatus",
    "CompatibilityStatus",
    "RecordKind",
]
