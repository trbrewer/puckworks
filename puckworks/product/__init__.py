"""``puckworks.product`` — the supported product-facing contract (issue #32).

A stable boundary between the scientific internals and any consumer of a shot-explanation result.
Everything named in :data:`__all__` follows the repository stability policy (``docs/API.md``);
``_``-prefixed submodules (``_records``, ``_serialize``, ``_provenance``, ``_enums``) are internal
implementation and may change without notice. There is **no fixture loader in PR 1A** (fixture
discovery/loading is deferred to PR 1B). No harness, paper, registry, or model implementation object
is exposed here.

This is **unreleased next-minor** API work: the published v0.2.0 wheel does **not** contain
``puckworks.product``. PR 1A scope is the **rights-independent** contract only — the versioned
records, canonical serialization, Git-free build provenance, and strict validation. There is
deliberately **no** bundled runtime fixture, fixture discovery/loader, ``analyze_shot`` / model
orchestration / explanation scoring / HTML output, and no public ``NormalizedShot``. The real
redistributable fixture, its manifest/loader/distribution, arrive in a separate **PR 1B** after its
license is approved; ``FixtureProvenance`` remains here because it is part of the record semantics.
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
from ._normalize import (
    NormalizationError,
    RawChannel,
    SeriesRole,
    normalize_shot_input,
    synthetic_provenance,
)
from ._pull import (
    PULL_RUN_SCHEMA_VERSION,
    SERIES_ROLES,
    ComponentCoverage,
    ComponentDisposition,
    DomainFinding,
    DomainStatus,
    PullConfig,
    PullDomainError,
    PullEvent,
    PullRecipe,
    PullReportArtifacts,
    PullRun,
    PullSeries,
    PullTrace,
    StageResult,
    available_pull_presets,
    evaluate_domain,
    load_pull_preset,
    pull_run_to_dict,
    pull_run_to_json,
    pull_run_to_markdown,
    pull_run_summary,
    render_pull_report,
    simulate_pull,
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
    # provenance (fixture discovery/loading is deferred to PR 1B, after an approved fixture)
    "build_provenance",
    "dev_build_identifier",
    # PR 2A — rights-independent normalization boundary (caller-owned/synthetic input only)
    "normalize_shot_input",
    "RawChannel",
    "SeriesRole",
    "synthetic_provenance",
    # Guided Espresso Pull (issue #48) — rights-independent guided mechanism explorer
    "PULL_RUN_SCHEMA_VERSION",
    "SERIES_ROLES",
    "PullRecipe",
    "PullConfig",
    "PullRun",
    "PullSeries",
    "PullTrace",
    "PullReportArtifacts",
    "StageResult",
    "ComponentCoverage",
    "DomainFinding",
    "DomainStatus",
    "ComponentDisposition",
    "PullEvent",
    "simulate_pull",
    "evaluate_domain",
    "available_pull_presets",
    "load_pull_preset",
    "pull_run_to_dict",
    "pull_run_to_json",
    "pull_run_to_markdown",
    "pull_run_summary",
    "render_pull_report",
    # exceptions
    "SchemaError",
    "ProvenanceUnavailableError",
    "NormalizationError",
    "PullDomainError",
]
