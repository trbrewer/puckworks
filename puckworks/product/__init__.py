"""``puckworks.product`` — the supported product-facing contract (issue #32).

A stable boundary between the scientific internals and any consumer of a shot-explanation result.
Everything named in :data:`__all__` follows the repository stability policy (``docs/API.md``);
``_``-prefixed submodules (``_records``, ``_serialize``, ``_provenance``, ``_fixtures``, ``_enums``)
are internal implementation and may change without notice. No harness, paper, registry, or model
implementation object is exposed here.

PR 1 scope: the versioned records, canonical serialization, build/fixture provenance, and one
redistributable single-shot fixture. There is deliberately **no** ``analyze_shot`` / model
orchestration / explanation scoring / HTML output — those arrive in later PRs.
"""
from __future__ import annotations

from ._enums import AvailabilityStatus, CompatibilityStatus, RecordKind, SeriesKind
from ._fixtures import available_fixtures, load_bundled_shot
from ._provenance import build_provenance
from ._records import (
    SCHEMA_VERSION,
    BuildProvenance,
    Caveat,
    DetectedEvent,
    EvidenceReference,
    ExplanationCandidate,
    FixtureProvenance,
    NextMeasurement,
    NormalizedShot,
    ObservedSeries,
    ShotExplanationBundle,
    ShotInput,
    TimeAxis,
)
from ._serialize import (
    bundle_from_dict,
    bundle_from_json,
    shot_input_from_dict,
    shot_input_from_json,
    to_dict,
    to_json,
)

__all__ = [
    # schema
    "SCHEMA_VERSION",
    # enums (four orthogonal dimensions)
    "SeriesKind",
    "AvailabilityStatus",
    "CompatibilityStatus",
    "RecordKind",
    # records
    "EvidenceReference",
    "BuildProvenance",
    "FixtureProvenance",
    "TimeAxis",
    "ObservedSeries",
    "DetectedEvent",
    "Caveat",
    "NextMeasurement",
    "ExplanationCandidate",
    "ShotInput",
    "NormalizedShot",
    "ShotExplanationBundle",
    # serialization
    "to_dict",
    "to_json",
    "bundle_from_dict",
    "bundle_from_json",
    "shot_input_from_dict",
    "shot_input_from_json",
    # provenance + fixtures
    "build_provenance",
    "available_fixtures",
    "load_bundled_shot",
]
