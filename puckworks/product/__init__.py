"""``puckworks.product`` — the supported product-facing contract (issue #32).

A stable boundary between the scientific internals and any consumer of a shot-explanation result.
Everything named in :data:`__all__` follows the repository stability policy (``docs/API.md``);
``_``-prefixed submodules (``_records``, ``_serialize``, ``_provenance``, ``_fixtures``, ``_enums``)
are internal implementation and may change without notice. No harness, paper, registry, or model
implementation object is exposed here.

This is **unreleased next-minor** API work: the published v0.2.0 wheel does **not** contain
``puckworks.product``. PR 1 scope is the versioned records, canonical serialization, build/fixture
provenance, and one (rights-gated) single-shot fixture — there is deliberately **no** ``analyze_shot``
/ model orchestration / explanation scoring / HTML output, and no public ``NormalizedShot`` yet.
"""
from __future__ import annotations

from ._enums import (
    AvailabilityStatus,
    CompatibilityStatus,
    ProvenanceSource,
    RecordKind,
    RedistributionStatus,
    RightsReviewStatus,
    SeriesKind,
)
from ._fixtures import (
    FixtureManifestError,
    FixtureRightsError,
    available_fixtures,
    load_bundled_shot,
    release_ready_fixtures,
)
from ._provenance import ProvenanceUnavailableError, build_provenance, dev_build_identifier
from ._records import (
    MAX_EXPLANATION_CANDIDATES,
    SHOT_EXPLANATION_BUNDLE_SCHEMA_VERSION,
    SHOT_INPUT_SCHEMA_VERSION,
    BuildProvenance,
    Caveat,
    ChannelSemantics,
    DetectedEvent,
    EvidenceReference,
    ExplanationCandidate,
    FixtureProvenance,
    NextMeasurement,
    ObservedSeries,
    ShotExplanationBundle,
    ShotInput,
    TimeAxis,
    TransformationStep,
    UnitBinding,
)
from ._serialize import (
    SchemaError,
    bundle_from_dict,
    bundle_from_json,
    bundle_to_dict,
    bundle_to_json,
    shot_input_from_dict,
    shot_input_from_json,
    shot_input_to_dict,
    shot_input_to_json,
)

__all__ = [
    # schema versions
    "SHOT_INPUT_SCHEMA_VERSION",
    "SHOT_EXPLANATION_BUNDLE_SCHEMA_VERSION",
    "MAX_EXPLANATION_CANDIDATES",
    # enums (four orthogonal dimensions + provenance/rights vocabularies)
    "SeriesKind",
    "AvailabilityStatus",
    "CompatibilityStatus",
    "RecordKind",
    "ProvenanceSource",
    "RightsReviewStatus",
    "RedistributionStatus",
    # records
    "ChannelSemantics",
    "UnitBinding",
    "TransformationStep",
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
    "ShotExplanationBundle",
    # explicit top-level serialization
    "shot_input_to_dict",
    "shot_input_to_json",
    "shot_input_from_dict",
    "shot_input_from_json",
    "bundle_to_dict",
    "bundle_to_json",
    "bundle_from_dict",
    "bundle_from_json",
    # provenance + fixtures
    "build_provenance",
    "dev_build_identifier",
    "available_fixtures",
    "load_bundled_shot",
    "release_ready_fixtures",
    # exceptions
    "SchemaError",
    "ProvenanceUnavailableError",
    "FixtureManifestError",
    "FixtureRightsError",
]
