"""PR 2A — the rights-independent normalization boundary (internal; public via ``puckworks.product``).

Turns **caller-owned / synthetic** raw channel data into a validated, contract-typed
:class:`ShotInput` (``puckworks.product``). It is deliberately rights-independent: it accepts no
upstream fixture bytes and ships no data — the real redistributable fixture and its loader remain a
separate, rights-gated effort (PR 1B). This boundary only makes the *shape* explicit:

  * **units are explicit** — every channel declares a unit, validated against the role's allowed set;
  * **time alignment is explicit** — one declared, strictly-increasing time axis; every series is
    aligned to it (equal length);
  * **pressure nodes are explicit** — a pressure channel must name a measurement node + reference;
  * **flow is distinguished from cumulative mass** — separate roles with separate unit sets, so a
    flow rate cannot be silently treated as a cumulative mass (or vice versa);
  * **serialization/provenance stay deterministic** — the output is a normal ``ShotInput`` that
    serializes canonically via the existing serializers.

Malformed input raises :class:`NormalizationError`; nothing is guessed or defaulted silently.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from enum import Enum

from ._enums import AvailabilityStatus, RecordKind, RedistributionStatus, RightsReviewStatus, SeriesKind
from ._records import (
    SHOT_INPUT_SCHEMA_VERSION,
    ChannelSemantics,
    FixtureProvenance,
    ObservedSeries,
    ShotInput,
    TimeAxis,
)


class NormalizationError(ValueError):
    """Raised when caller-supplied raw data cannot be normalized into a valid ShotInput."""


class SeriesRole(str, Enum):
    """What a raw channel represents — the flow/mass distinction is explicit here, not inferred."""

    PRESSURE = "pressure"
    FLOW_RATE = "flow_rate"            # an instantaneous rate (mass/time or volume/time)
    CUMULATIVE_MASS = "cumulative_mass"   # an accumulated mass (monotondically non-decreasing)
    SCALAR = "scalar"                 # any other explicitly-united scalar time series (e.g. temperature)


# Allowed units per role. A flow rate can never carry a mass unit and vice versa — this is the
# structural guard that keeps flow distinct from cumulative mass.
_ROLE_UNITS: dict[SeriesRole, frozenset[str]] = {
    SeriesRole.PRESSURE: frozenset({"bar", "Pa", "kPa", "MPa"}),
    SeriesRole.FLOW_RATE: frozenset({"g/s", "kg/s", "ml/s", "l/s"}),
    SeriesRole.CUMULATIVE_MASS: frozenset({"g", "kg"}),
    SeriesRole.SCALAR: frozenset({"C", "K", "degC", "1", "ratio", "fraction"}),
}


@dataclass(frozen=True)
class RawChannel:
    """One caller-owned raw channel. All fields are explicit; nothing is inferred from a name."""

    channel_id: str
    quantity: str
    unit: str
    role: SeriesRole
    values: tuple[float, ...]
    measurement_node: str | None = None   # required iff role is PRESSURE
    reference: str | None = None          # required iff role is PRESSURE (e.g. "gauge"/"absolute")


def synthetic_provenance(fixture_id: str, *, source_record: str = "caller-owned:synthetic") -> FixtureProvenance:
    """Build a clearly-synthetic, rights-independent provenance record (no upstream data, no
    redistribution rights asserted). Used by callers/tests that own their raw data.

    The sha256 fields are a deterministic digest of the synthetic identity (there are no upstream
    bytes); original and packaged digests are equal because synthetic input is not transformed."""
    import hashlib

    digest = hashlib.sha256(f"puckworks-synthetic:{fixture_id}:{source_record}".encode()).hexdigest()
    return FixtureProvenance(
        fixture_id=fixture_id,
        record_kind=RecordKind.SINGLE_SHOT,
        source_record=source_record,
        source_version="synthetic",
        source_member="synthetic (no upstream data)",
        record_license_expression="CC0-1.0",
        record_license_url="https://creativecommons.org/publicdomain/zero/1.0/",
        attribution="Caller-owned synthetic data; contains no upstream/third-party dataset.",
        original_sha256=digest,
        packaged_sha256=digest,
        rights_basis="caller-owned synthetic object; not a redistributable third-party dataset",
        rights_review_status=RightsReviewStatus.PENDING,
        redistribution_status=RedistributionStatus.PENDING,
        modification_notice="normalized from caller-supplied raw channels; no source data",
        selection_method="synthetic (no selection from an upstream corpus)",
        scientific_caveats=("synthetic normalization input; not an experimental observation",),
    )


def _check_finite(name: str, values) -> tuple[float, ...]:
    out = []
    for i, v in enumerate(values):
        if isinstance(v, bool) or not isinstance(v, (int, float)):
            raise NormalizationError(f"{name}[{i}] must be a real number, got {v!r}")
        f = float(v)
        if not math.isfinite(f):
            raise NormalizationError(f"{name}[{i}] must be finite, got {f!r}")
        out.append(f)
    return tuple(out)


def normalize_shot_input(
    *,
    fixture_id: str,
    provenance: FixtureProvenance,
    time_unit: str,
    time_origin: str,
    time_values,
    channels: list[RawChannel],
    time_axis_id: str = "t",
) -> ShotInput:
    """Normalize caller-owned raw channels into a validated :class:`ShotInput`.

    Raises :class:`NormalizationError` on any malformed input. The result serializes deterministically
    via ``shot_input_to_json``.
    """
    if not isinstance(fixture_id, str) or not fixture_id:
        raise NormalizationError("fixture_id must be a non-empty string")
    if not isinstance(provenance, FixtureProvenance):
        raise NormalizationError("provenance must be a FixtureProvenance")
    if not isinstance(time_unit, str) or not time_unit:
        raise NormalizationError("time_unit must be a non-empty string")

    # ── time alignment: one declared, strictly-increasing axis ──────────────────────
    t = _check_finite("time_values", tuple(time_values))
    if len(t) < 1:
        raise NormalizationError("time_values must be non-empty")
    if any(t[i] >= t[i + 1] for i in range(len(t) - 1)):
        raise NormalizationError("time_values must be strictly increasing (explicit time alignment)")
    axis = TimeAxis(time_axis_id, time_unit, time_origin, t)

    if not channels:
        raise NormalizationError("at least one channel is required")
    seen: set[str] = set()
    series: list[ObservedSeries] = []
    for ch in channels:
        if not isinstance(ch, RawChannel):
            raise NormalizationError("each channel must be a RawChannel")
        if not ch.channel_id:
            raise NormalizationError("channel_id must be non-empty")
        if ch.channel_id in seen:
            raise NormalizationError(f"duplicate channel_id: {ch.channel_id!r}")
        seen.add(ch.channel_id)
        if not isinstance(ch.role, SeriesRole):
            raise NormalizationError(f"{ch.channel_id}: role must be a SeriesRole")
        # explicit units, validated per role (this is the flow-vs-mass structural guard)
        if not ch.unit or ch.unit not in _ROLE_UNITS[ch.role]:
            raise NormalizationError(
                f"{ch.channel_id}: unit {ch.unit!r} is not valid for role {ch.role.value} "
                f"(allowed: {sorted(_ROLE_UNITS[ch.role])})")
        vals = _check_finite(f"{ch.channel_id}.values", ch.values)
        if len(vals) != len(t):
            raise NormalizationError(
                f"{ch.channel_id}: values length {len(vals)} != time length {len(t)} "
                "(series must be aligned to the declared time axis)")
        if ch.role is SeriesRole.CUMULATIVE_MASS and any(vals[i] > vals[i + 1] + 1e-12 for i in range(len(vals) - 1)):
            raise NormalizationError(f"{ch.channel_id}: cumulative_mass must be non-decreasing")

        # pressure requires an explicit node + reference; non-pressure must not fabricate them
        if ch.role is SeriesRole.PRESSURE:
            if not ch.measurement_node or not ch.reference:
                raise NormalizationError(
                    f"{ch.channel_id}: a pressure channel requires measurement_node and reference")
            semantics = ChannelSemantics(ch.measurement_node, ch.reference, "no missing values")
        else:
            if ch.reference in _ROLE_UNITS[SeriesRole.PRESSURE] or ch.reference in ("gauge", "absolute"):
                raise NormalizationError(
                    f"{ch.channel_id}: non-pressure channel must not carry a pressure reference")
            semantics = ChannelSemantics(ch.measurement_node or ch.channel_id, ch.role.value,
                                         "no missing values")

        series.append(ObservedSeries(
            series_id=ch.channel_id, quantity=ch.quantity, unit=ch.unit,
            series_kind=SeriesKind.MEASURED, availability=AvailabilityStatus.AVAILABLE,
            time_axis_id=time_axis_id, channel_semantics=semantics, values=vals,
            provenance="caller-owned:normalized", uncertainty=None))

    return ShotInput(schema_version=SHOT_INPUT_SCHEMA_VERSION, fixture_id=fixture_id,
                     provenance=provenance, time_axis=axis, series=tuple(series))
