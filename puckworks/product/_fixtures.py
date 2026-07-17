"""Bundled fixture loading via ``importlib.resources`` (issue #32, PR 1).

No ``__file__``-relative repository traversal, working-directory assumption, repository-root
discovery, or network access. The manifest is validated as a strict contract (exact key sets, typed
scalars, typed nested channel/transformation objects, duplicate-key rejection, pressure-metadata
agreement, and rights consistency) before any value is read; the CSV header is validated against the
declared columns; measurement semantics (node/reference/missing-value) travel into the public
series; and the public loader only lists or returns a fixture whose redistribution rights are
**approved** with an effective member license. A rights-pending fixture ships for review but is not
publicly loadable. Every malformed manifest surfaces as :class:`FixtureManifestError`.
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
    ChannelSemantics,
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

# required scalar string fields (nonempty)
_REQUIRED_STR = {
    "fixture_id", "record_kind", "title", "source_authors", "source_title", "source_record",
    "source_version", "source_member", "record_license_expression", "record_license_url",
    "rights_basis", "rights_review_status", "redistribution_status", "attribution",
    "modification_notice", "packaged_file", "time_column", "time_unit", "pressure_node",
    "pressure_reference", "time_origin", "missing_value_semantics", "selection_method",
}
_REQUIRED_OTHER = {"schema_version", "original_sha256", "normalized_sha256", "columns", "channels",
                   "transformations", "scientific_caveats"}
_REQUIRED_MANIFEST_KEYS = _REQUIRED_STR | _REQUIRED_OTHER
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


def _nonempty_str(m: dict, key: str) -> None:
    v = m.get(key)
    if not isinstance(v, str) or not v.strip():
        raise FixtureManifestError(f"manifest {key} must be a non-empty string; got {v!r}")


def _opt_str_or_none(m: dict, key: str) -> None:
    v = m.get(key)
    if v is not None and (not isinstance(v, str) or not v.strip()):
        raise FixtureManifestError(f"manifest {key} must be a non-empty string or null; got {v!r}")


def _is_sha(v) -> bool:
    return isinstance(v, str) and len(v) == 64 and all(c in "0123456789abcdef" for c in v)


def _load_manifest(fixture_id: str) -> dict:
    try:
        raw = _read_bytes(_FIXTURES[fixture_id]).decode("utf-8")
    except UnicodeDecodeError as exc:
        raise FixtureManifestError(f"manifest is not valid UTF-8: {exc}") from exc
    try:
        m = json.loads(raw, object_pairs_hook=_no_dup)
    except json.JSONDecodeError as exc:
        raise FixtureManifestError(f"manifest is not valid JSON: {exc}") from exc
    _validate_manifest(fixture_id, m)
    return m


def _validate_manifest(fixture_id: str, m: dict) -> None:
    if not isinstance(m, dict):
        raise FixtureManifestError("manifest must be a JSON object")
    if type(m.get("schema_version")) is not int or m.get("schema_version") != _MANIFEST_SCHEMA_VERSION:
        raise FixtureManifestError(f"unsupported manifest schema_version {m.get('schema_version')!r}")
    unknown = set(m) - _REQUIRED_MANIFEST_KEYS - _OPTIONAL_MANIFEST_KEYS
    missing = _REQUIRED_MANIFEST_KEYS - set(m)
    if missing:
        raise FixtureManifestError(f"manifest missing required fields: {sorted(missing)}")
    if unknown:
        raise FixtureManifestError(f"manifest has unknown fields: {sorted(unknown)}")
    for key in _REQUIRED_STR:
        _nonempty_str(m, key)
    for key in ("member_license_expression", "member_license_url", "rights_basis_url"):
        _opt_str_or_none(m, key)
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
        if not _is_sha(m[key]):
            raise FixtureManifestError(f"manifest {key} must be a full lowercase SHA-256")
    if m.get("debug_source_sha256") is not None and not _is_sha(m["debug_source_sha256"]):
        raise FixtureManifestError("debug_source_sha256 must be a full lowercase SHA-256 or null")
    if m["packaged_file"] != f"{fixture_id}.csv":
        raise FixtureManifestError(f"manifest packaged_file {m['packaged_file']!r} unexpected")
    # scientific_caveats: nonempty list of nonempty strings
    if not isinstance(m["scientific_caveats"], list) or not m["scientific_caveats"] or \
            any(not (isinstance(x, str) and x.strip()) for x in m["scientific_caveats"]):
        raise FixtureManifestError("scientific_caveats must be a non-empty list of non-empty strings")
    # columns
    if not isinstance(m["columns"], list) or not m["columns"] or \
            any(not (isinstance(c, str) and c) for c in m["columns"]):
        raise FixtureManifestError("manifest columns must be a non-empty list of strings")
    if len(m["columns"]) != len(set(m["columns"])):
        raise FixtureManifestError("manifest columns contains duplicates")
    if m["time_column"] not in m["columns"]:
        raise FixtureManifestError("manifest time_column not among columns")
    # channels
    if not isinstance(m["channels"], list) or not m["channels"]:
        raise FixtureManifestError("manifest channels must be a non-empty list")
    seen_cols: set = set()
    for ch in m["channels"]:
        if not isinstance(ch, dict):
            raise FixtureManifestError("each channel must be a mapping")
        extra = set(ch) - _CHANNEL_REQUIRED - _CHANNEL_OPTIONAL
        if extra:
            raise FixtureManifestError(f"channel has unknown fields: {sorted(extra)}")
        if _CHANNEL_REQUIRED - set(ch):
            raise FixtureManifestError(f"channel missing fields: {sorted(_CHANNEL_REQUIRED - set(ch))}")
        for f in ("column", "quantity", "unit", "series_kind"):
            if not (isinstance(ch[f], str) and ch[f].strip()):
                raise FixtureManifestError(f"channel {f} must be a non-empty string; got {ch[f]!r}")
        if ch["column"] in seen_cols:
            raise FixtureManifestError(f"duplicate channel column {ch['column']!r}")
        seen_cols.add(ch["column"])
        try:
            SeriesKind(ch["series_kind"])
        except ValueError as exc:
            raise FixtureManifestError(str(exc)) from exc
        is_pressure = "pressure" in ch["quantity"].lower()
        node, ref = ch.get("pressure_node"), ch.get("pressure_reference")
        if is_pressure:
            if not (isinstance(node, str) and node.strip() and isinstance(ref, str) and ref.strip()):
                raise FixtureManifestError(f"pressure channel {ch['column']!r} requires pressure_node + pressure_reference")
            if node != m["pressure_node"] or ref != m["pressure_reference"]:
                raise FixtureManifestError("channel pressure metadata must agree with the manifest top-level values")
        else:
            if node is not None or ref is not None:
                raise FixtureManifestError(f"non-pressure channel {ch['column']!r} must not declare pressure metadata")
    non_time = [c for c in m["columns"] if c != m["time_column"]]
    if seen_cols != set(non_time):
        raise FixtureManifestError("manifest channels must describe exactly the non-time columns")
    # transformations
    if not isinstance(m["transformations"], list) or not m["transformations"]:
        raise FixtureManifestError("manifest transformations must be a non-empty list")
    for t in m["transformations"]:
        if not isinstance(t, dict) or set(t) != _TRANSFORM_KEYS or \
                not all(isinstance(t[k], str) and t[k].strip() for k in _TRANSFORM_KEYS):
            raise FixtureManifestError("each transformation needs exactly non-empty step_id + description")
    # license / rights consistency (defer the full state machine to FixtureProvenance construction)
    if "CC-BY" in m["record_license_expression"].upper() and not m["record_license_url"]:
        raise FixtureManifestError("a CC-BY record_license_expression requires record_license_url")
    try:
        _provenance_from_manifest(m)
    except ValueError as exc:
        raise FixtureManifestError(f"manifest rights/provenance invalid: {exc}") from exc


def _provenance_from_manifest(m: dict) -> FixtureProvenance:
    return FixtureProvenance(
        fixture_id=m["fixture_id"], record_kind=RecordKind(m["record_kind"]),
        source_record=m["source_record"], source_version=m["source_version"],
        source_member=m["source_member"], record_license_expression=m["record_license_expression"],
        record_license_url=m["record_license_url"], attribution=m["attribution"],
        original_sha256=m["original_sha256"], packaged_sha256=m["normalized_sha256"],
        rights_basis=m["rights_basis"], rights_review_status=RightsReviewStatus(m["rights_review_status"]),
        redistribution_status=RedistributionStatus(m["redistribution_status"]),
        modification_notice=m["modification_notice"], selection_method=m["selection_method"],
        scientific_caveats=tuple(m["scientific_caveats"]),
        transformations=tuple(TransformationStep(t["step_id"], t["description"]) for t in m["transformations"]),
        member_license_expression=m.get("member_license_expression"),
        member_license_url=m.get("member_license_url"),
        rights_basis_url=m.get("rights_basis_url"), rights_review_date=m.get("rights_review_date"),
    )


def _parse_csv(fixture_id: str, m: dict, csv_bytes: bytes):
    try:
        text = csv_bytes.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise FixtureManifestError(f"fixture {fixture_id!r} CSV is not valid UTF-8: {exc}") from exc
    rows = list(csv.reader(io.StringIO(text)))
    if len(rows) < 2:
        raise FixtureManifestError(f"fixture {fixture_id!r} CSV must have a header and at least one data row")
    header = rows[0]
    if header != m["columns"]:
        raise FixtureManifestError(f"fixture {fixture_id!r} CSV header {header} != declared columns {m['columns']}")
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
    channels = {ch["column"]: ch for ch in m["channels"]}
    try:
        time_axis = TimeAxis(
            time_axis_id=f"{fixture_id}:time", unit=m["time_unit"], origin=m["time_origin"],
            values=tuple(times),
        )
        series = tuple(
            ObservedSeries(
                series_id=f"{fixture_id}:{col}", quantity=channels[col]["quantity"],
                unit=channels[col]["unit"], series_kind=SeriesKind(channels[col]["series_kind"]),
                availability=AvailabilityStatus.AVAILABLE, time_axis_id=time_axis.time_axis_id,
                channel_semantics=ChannelSemantics(
                    measurement_node=channels[col].get("pressure_node"),
                    reference=channels[col].get("pressure_reference"),
                    missing_value_semantics=m["missing_value_semantics"],
                ),
                values=tuple(cols[col]), provenance=m["source_record"],
            )
            for col in m["columns"] if col != m["time_column"]
        )
        return ShotInput(
            schema_version=SHOT_INPUT_SCHEMA_VERSION, fixture_id=fixture_id, provenance=provenance,
            time_axis=time_axis, series=series,
        )
    except ValueError as exc:
        raise FixtureManifestError(f"fixture {fixture_id!r} could not construct a valid ShotInput: {exc}") from exc


def available_fixtures() -> tuple[str, ...]:
    """Sorted tuple of bundled fixture IDs whose redistribution rights are APPROVED.

    A rights-pending or prohibited fixture is intentionally absent. A **malformed** registered
    manifest raises :class:`FixtureManifestError` — package corruption is visible to the caller, not
    silently swallowed into an empty catalog.
    """
    out = []
    for fid in _FIXTURES:
        prov = _provenance_from_manifest(_load_manifest(fid))  # raises FixtureManifestError if malformed
        if prov.is_redistributable:
            out.append(fid)
    return tuple(sorted(out))


def load_bundled_shot(fixture_id: str) -> ShotInput:
    """Load a bundled measured shot as a :class:`ShotInput`. No analysis is performed.

    Validates the manifest as a strict contract, enforces the redistribution-rights gate (raising
    :class:`FixtureRightsError` for a pending/prohibited fixture), verifies the packaged CSV digest,
    strictly validates the CSV against the declared columns, and carries source units and pressure
    semantics into the public series. Raises ``KeyError`` for an unknown fixture ID.
    """
    return _load(fixture_id, require_rights=True)


def release_ready_fixtures() -> tuple[str, ...]:
    """Fail-closed release gate: every *registered* fixture must be approved-and-redistributable.

    Raises :class:`FixtureRightsError` if any bundled fixture is not releasable, so a package release
    cannot ship a rights-pending candidate. Returns the releasable fixture IDs when all pass.
    """
    for fid in _FIXTURES:
        prov = _provenance_from_manifest(_load_manifest(fid))
        if not prov.is_redistributable:
            raise FixtureRightsError(
                f"fixture {fid!r} is not release-ready "
                f"(review={prov.rights_review_status.value}, redistribution={prov.redistribution_status.value}); "
                f"a package release must not ship it"
            )
    return tuple(sorted(_FIXTURES))


__all__ = ["available_fixtures", "load_bundled_shot", "release_ready_fixtures",
           "FixtureManifestError", "FixtureRightsError"]
