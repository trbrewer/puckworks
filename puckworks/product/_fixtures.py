"""Bundled fixture loading via ``importlib.resources`` (issue #32, PR 1).

No ``__file__``-relative repository traversal, working-directory assumption, repository-root
discovery, or network access. Fixtures ship inside the installed package.
"""
from __future__ import annotations

import csv
import hashlib
import importlib.resources as resources
import io
import json

from ._enums import AvailabilityStatus, RecordKind, SeriesKind
from ._records import FixtureProvenance, ObservedSeries, ShotInput, TimeAxis

_DATA_PACKAGE = "puckworks.data.product"

# fixture_id -> (manifest resource, csv resource)
_FIXTURES = {
    "waszkiewicz2025_9bar_single_shot": (
        "waszkiewicz2025_9bar_single_shot.manifest.json",
        "waszkiewicz2025_9bar_single_shot.csv",
    ),
}

# measured input channels a fixture CSV may declare (product-side series metadata)
_SERIES_META = {
    "line_pressure_bar": ("line_pressure", "bar"),
    "mass_g": ("mass", "g"),
}


def available_fixtures() -> tuple:
    """Sorted tuple of bundled fixture IDs."""
    return tuple(sorted(_FIXTURES))


def _read_resource_bytes(name: str) -> bytes:
    return resources.files(_DATA_PACKAGE).joinpath(name).read_bytes()


def load_bundled_shot(fixture_id: str) -> ShotInput:
    """Load a bundled measured shot as a :class:`ShotInput`. No analysis is performed.

    Verifies the packaged CSV digest against the fixture manifest, preserves the source units and
    pressure-node semantics, and returns typed measured series. Raises ``KeyError`` for an unknown
    fixture ID.
    """
    if fixture_id not in _FIXTURES:
        raise KeyError(
            f"unknown fixture {fixture_id!r}; available: {', '.join(available_fixtures())}"
        )
    manifest_name, csv_name = _FIXTURES[fixture_id]
    manifest = json.loads(_read_resource_bytes(manifest_name).decode("utf-8"))
    csv_bytes = _read_resource_bytes(csv_name)

    digest = hashlib.sha256(csv_bytes).hexdigest()
    if digest != manifest["normalized_sha256"]:
        raise ValueError(
            f"fixture {fixture_id!r} CSV digest {digest} != manifest normalized_sha256 "
            f"{manifest['normalized_sha256']}"
        )

    reader = csv.DictReader(io.StringIO(csv_bytes.decode("utf-8")))
    columns = reader.fieldnames or []
    if "time_s" not in columns:
        raise ValueError(f"fixture {fixture_id!r} CSV is missing the time_s column")
    channels = [c for c in columns if c != "time_s"]

    times: list[float] = []
    channel_values: dict[str, list[float]] = {c: [] for c in channels}
    for row in reader:
        times.append(float(row["time_s"]))
        for c in channels:
            channel_values[c].append(float(row[c]))

    provenance = FixtureProvenance(
        fixture_id=manifest["fixture_id"],
        record_kind=RecordKind(manifest["record_kind"]),
        source_record=manifest["source_record"],
        source_version=manifest["source_version"],
        source_member=manifest["source_member"],
        license=manifest["source_license"],
        attribution=manifest["attribution"],
        original_sha256=manifest["original_sha256"],
        packaged_sha256=manifest["normalized_sha256"],
        redistribution_status=manifest["redistribution_status"],
        transformations=tuple(manifest.get("transformations", ())),
    )

    time_axis = TimeAxis(
        time_axis_id=f"{fixture_id}:time",
        unit=manifest["units"]["time_s"],
        origin=manifest["time_origin"],
        values=tuple(times),
    )

    series = []
    for c in channels:
        quantity, default_unit = _SERIES_META.get(c, (c, ""))
        unit = manifest["units"].get(c, default_unit)
        series.append(
            ObservedSeries(
                series_id=f"{fixture_id}:{c}",
                quantity=quantity,
                unit=unit,
                series_kind=SeriesKind.MEASURED,
                availability=AvailabilityStatus.AVAILABLE,
                time_axis_id=time_axis.time_axis_id,
                values=tuple(channel_values[c]),
                provenance=provenance.source_record,
            )
        )

    return ShotInput(
        fixture_id=fixture_id,
        provenance=provenance,
        time_axis=time_axis,
        series=tuple(series),
    )


__all__ = ["available_fixtures", "load_bundled_shot"]
