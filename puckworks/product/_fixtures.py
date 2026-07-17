"""Bundled fixture loading via ``importlib.resources`` (issue #32, PR 1).

No ``__file__``-relative repository traversal, working-directory assumption, repository-root
discovery, or network access. The manifest is validated as a strict contract (exact key sets, typed
nested channel/transformation objects, duplicate-key rejection, rights consistency) before any value
is read; the CSV header is validated against the manifest's declared columns; and the public loader
only lists or returns a fixture whose redistribution rights are **approved** with an effective member
license. A rights-pending fixture ships in the package (for review) but is not publicly loadable.
"""
from __future__ import annotations

import csv
import hashlib
import importlib.resources as resources
import io
import json
import math

from ._enums import (
    AvailabilityStatus,
    RecordKind,
    RedistributionStatus,
    RightsReviewStatus,
    SeriesKind,
)
from ._records import (
    SHOT_INPUT_SCHEMA_VERSION,
    FixtureProvenance,
    ObservedSeries,
    ShotInput,
    TimeAxis,
    TransformationStep,
)

_DATA_PACKAGE = "puckworks.data.product"
_MANIFEST_SCHEMA_VERSION = 1

_FIXTURES = {
    "waszkiewicz2025_9bar_single_shot": "waszkiewicz2025_9bar_single_shot.manifest.json",
}

_REQUIRED_MANIFEST_KEYS = {
    "schema_version", "fixture_id", "record_kind", "title", "source_authors", "source_title",
    "source_record", "source_version", "source_member", "record_license_expression",
    "record_license_url", "rights_basis", "rights_review_status", "redistribution_status",
    "attribution", "modification_notice", "original_sha256", "normalized_sha256", "packaged_file",
    "time_column", "time_unit", "columns", "channels", "pressure_node", "pressure_reference",
    "time_origin", "missing_value_semantics", "transformations", "selection_method",
    "scientific_caveats",
}
_OPTIONAL_MANIFEST_KEYS = {
    "member_license_expression", "member_license_url", "rights_basis_url", "rights_review_date",
    "debug_source_sha256",
}
_CHANNEL_REQUIRED = {"column", "quantity", "unit", "series_kind"}
_CHANNEL_OPTIONAL = {"pressure_node", "pressure_reference"}
_TRANSFORM_KEYS = {"step_id", "description"}


class FixtureManifestError(ValueError):
    """Raised when a bundled fixture manifest fails validation."""


class FixtureRightsError(RuntimeError):
    """Raised when a fixture's redistribution rights are not approved for public loading."""


def _no_dup(pairs):
    out: dict = {}
    for k, v in pairs:
        if k in out:
            raise FixtureManifestError(f"duplicate manifest key: {k!r}")
        out[k] = v
    return out


def _read_bytes(name: str) -> bytes:
    return resources.files(_DATA_PACKAGE).joinpath(name).read_bytes()


def _load_manifest(fixture_id: str) -> dict:
    try:
        m = json.loads(_read_bytes(_FIXTURES[fixture_id]).decode("utf-8"), object_pairs_hook=_no_dup)
    except json.JSONDecodeError as exc:
        raise FixtureManifestError(f"manifest is not valid JSON: {exc}") from exc
    _validate_manifest(fixture_id, m)
    return m


def _validate_manifest(fixture_id: str, m: dict) -> None:
    if not isinstance(m, dict):
        raise FixtureManifestError("manifest must be a JSON object")
    if m.get("schema_version") != _MANIFEST_SCHEMA_VERSION:
        raise FixtureManifestError(f"unsupported manifest schema_version {m.get('schema_version')!r}")
    unknown = set(m) - _REQUIRED_MANIFEST_KEYS - _OPTIONAL_MANIFEST_KEYS
    missing = _REQUIRED_MANIFEST_KEYS - set(m)
    if missing:
        raise FixtureManifestError(f"manifest missing required fields: {sorted(missing)}")
    if unknown:
        raise FixtureManifestError(f"manifest has unknown fields: {sorted(unknown)}")
    if m["fixture_id"] != fixture_id:
        raise FixtureManifestError(f"manifest fixture_id {m['fixture_id']!r} != requested {fixture_id!r}")
    try:
        RecordKind(m["record_kind"])
        review = RightsReviewStatus(m["rights_review_status"])
        redist = RedistributionStatus(m["redistribution_status"])
    except ValueError as exc:
        raise FixtureManifestError(str(exc)) from exc
    if m["record_kind"] != RecordKind.SINGLE_SHOT.value:
        raise FixtureManifestError(f"this fixture must be a single_shot; got {m['record_kind']!r}")
    for key in ("original_sha256", "normalized_sha256"):
        val = m[key]
        if not (isinstance(val, str) and len(val) == 64 and all(c in "0123456789abcdef" for c in val)):
            raise FixtureManifestError(f"manifest {key} must be a full lowercase SHA-256")
    if m["packaged_file"] != f"{fixture_id}.csv":
        raise FixtureManifestError(f"manifest packaged_file {m['packaged_file']!r} unexpected")
    # columns / channels
    if not isinstance(m["columns"], list) or not m["columns"]:
        raise FixtureManifestError("manifest columns must be a non-empty list")
    if len(m["columns"]) != len(set(m["columns"])):
        raise FixtureManifestError("manifest columns contains duplicates")
    if m["time_column"] not in m["columns"]:
        raise FixtureManifestError("manifest time_column not among columns")
    if not isinstance(m["channels"], list) or not m["channels"]:
        raise FixtureManifestError("manifest channels must be a non-empty list")
    seen_cols: set = set()
    for ch in m["channels"]:
        if not isinstance(ch, dict):
            raise FixtureManifestError("each channel must be a mapping")
        if set(ch) - _CHANNEL_REQUIRED - _CHANNEL_OPTIONAL:
            raise FixtureManifestError(f"channel has unknown fields: {sorted(set(ch) - _CHANNEL_REQUIRED - _CHANNEL_OPTIONAL)}")
        if _CHANNEL_REQUIRED - set(ch):
            raise FixtureManifestError(f"channel missing fields: {sorted(_CHANNEL_REQUIRED - set(ch))}")
        if ch["column"] in seen_cols:
            raise FixtureManifestError(f"duplicate channel column {ch['column']!r}")
        seen_cols.add(ch["column"])
        try:
            SeriesKind(ch["series_kind"])
        except ValueError as exc:
            raise FixtureManifestError(str(exc)) from exc
    non_time = [c for c in m["columns"] if c != m["time_column"]]
    if seen_cols != set(non_time):
        raise FixtureManifestError("manifest channels must describe exactly the non-time columns")
    # transformations
    if not isinstance(m["transformations"], list) or not m["transformations"]:
        raise FixtureManifestError("manifest transformations must be a non-empty list")
    for t in m["transformations"]:
        if not isinstance(t, dict) or set(t) != _TRANSFORM_KEYS or not (t["step_id"] and t["description"]):
            raise FixtureManifestError("each transformation needs exactly step_id + description")
    # license / rights
    if "CC-BY" in m["record_license_expression"].upper() and not m["record_license_url"]:
        raise FixtureManifestError("a CC-BY record_license_expression requires record_license_url")
    member_expr = m.get("member_license_expression")
    member_url = m.get("member_license_url")
    approved = (review is RightsReviewStatus.APPROVED or redist is RedistributionStatus.REDISTRIBUTABLE)
    if approved and (not member_expr or not member_url):
        raise FixtureManifestError(
            "an approved/redistributable fixture requires member_license_expression + member_license_url"
        )
    if not approved and (member_expr or member_url):
        raise FixtureManifestError(
            "a pending fixture must not assert a member license until approved"
        )


def _provenance_from_manifest(m: dict) -> FixtureProvenance:
    return FixtureProvenance(
        fixture_id=m["fixture_id"], record_kind=RecordKind(m["record_kind"]),
        source_record=m["source_record"], source_version=m["source_version"],
        source_member=m["source_member"], record_license_expression=m["record_license_expression"],
        record_license_url=m["record_license_url"], attribution=m["attribution"],
        original_sha256=m["original_sha256"], packaged_sha256=m["normalized_sha256"],
        rights_basis=m["rights_basis"], rights_review_status=RightsReviewStatus(m["rights_review_status"]),
        redistribution_status=RedistributionStatus(m["redistribution_status"]),
        modification_notice=m["modification_notice"],
        transformations=tuple(TransformationStep(t["step_id"], t["description"]) for t in m["transformations"]),
        member_license_expression=m.get("member_license_expression"),
        member_license_url=m.get("member_license_url"),
        rights_basis_url=m.get("rights_basis_url"), rights_review_date=m.get("rights_review_date"),
    )


def _parse_csv(fixture_id: str, m: dict, csv_bytes: bytes):
    rows = list(csv.reader(io.StringIO(csv_bytes.decode("utf-8"))))
    if not rows:
        raise FixtureManifestError(f"fixture {fixture_id!r} CSV is empty")
    header = rows[0]
    if header != m["columns"]:
        raise FixtureManifestError(
            f"fixture {fixture_id!r} CSV header {header} != declared columns {m['columns']}"
        )
    time_idx = header.index(m["time_column"])
    n = len(header)
    times: list[float] = []
    cols: dict[str, list[float]] = {c: [] for c in header if c != m["time_column"]}
    for r, row in enumerate(rows[1:], start=2):
        if len(row) != n:
            raise FixtureManifestError(f"CSV row {r} has {len(row)} fields, expected {n}")
        vals = []
        for x in row:
            try:
                v = float(x)
            except ValueError as exc:
                raise FixtureManifestError(f"CSV row {r}: non-numeric value {x!r}") from exc
            if math.isnan(v) or math.isinf(v):
                raise FixtureManifestError(f"CSV row {r}: NaN/infinity not allowed")
            vals.append(v)
        times.append(vals[time_idx])
        for i, c in enumerate(header):
            if c != m["time_column"]:
                cols[c].append(vals[i])
    if any(b <= a for a, b in zip(times, times[1:])):
        raise FixtureManifestError("CSV time column must be strictly increasing")
    return times, cols


def _load(fixture_id: str, *, require_rights: bool) -> ShotInput:
    if fixture_id not in _FIXTURES:
        raise KeyError(f"unknown fixture {fixture_id!r}; available: {', '.join(sorted(_FIXTURES))}")
    m = _load_manifest(fixture_id)
    provenance = _provenance_from_manifest(m)
    if require_rights and not provenance.is_redistributable:
        raise FixtureRightsError(
            f"fixture {fixture_id!r} rights not approved "
            f"(review={provenance.rights_review_status.value}, "
            f"redistribution={provenance.redistribution_status.value}); not publicly loadable"
        )
    csv_bytes = _read_bytes(m["packaged_file"])
    digest = hashlib.sha256(csv_bytes).hexdigest()
    if digest != m["normalized_sha256"]:
        raise FixtureManifestError(
            f"fixture {fixture_id!r} CSV digest {digest} != manifest normalized_sha256"
        )
    times, cols = _parse_csv(fixture_id, m, csv_bytes)
    time_axis = TimeAxis(
        time_axis_id=f"{fixture_id}:time", unit=m["time_unit"], origin=m["time_origin"],
        values=tuple(times),
    )
    channels = {ch["column"]: ch for ch in m["channels"]}
    series = tuple(
        ObservedSeries(
            series_id=f"{fixture_id}:{col}", quantity=channels[col]["quantity"],
            unit=channels[col]["unit"], series_kind=SeriesKind(channels[col]["series_kind"]),
            availability=AvailabilityStatus.AVAILABLE, time_axis_id=time_axis.time_axis_id,
            values=tuple(cols[col]), provenance=m["source_record"],
        )
        for col in m["columns"] if col != m["time_column"]
    )
    return ShotInput(
        schema_version=SHOT_INPUT_SCHEMA_VERSION, fixture_id=fixture_id, provenance=provenance,
        time_axis=time_axis, series=series,
    )


def available_fixtures() -> tuple:
    """Sorted tuple of bundled fixture IDs whose redistribution rights are APPROVED.

    A rights-pending or prohibited fixture is intentionally absent — it ships for review but is not
    part of the public surface until approved.
    """
    out = []
    for fid in _FIXTURES:
        try:
            prov = _provenance_from_manifest(_load_manifest(fid))
            if prov.is_redistributable:
                out.append(fid)
        except (FixtureManifestError, KeyError, ValueError):
            continue
    return tuple(sorted(out))


def load_bundled_shot(fixture_id: str) -> ShotInput:
    """Load a bundled measured shot as a :class:`ShotInput`. No analysis is performed.

    Validates the manifest as a strict contract, enforces the redistribution-rights gate (raising
    :class:`FixtureRightsError` for a pending/prohibited fixture), verifies the packaged CSV digest,
    strictly validates the CSV against the declared columns, and preserves source units and
    pressure-node semantics. Raises ``KeyError`` for an unknown fixture ID.
    """
    return _load(fixture_id, require_rights=True)


__all__ = ["available_fixtures", "load_bundled_shot", "FixtureManifestError", "FixtureRightsError"]
