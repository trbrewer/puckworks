# Supported public API & stability policy (P1.5)

Puckworks is a scientific package with a **small, explicit supported surface**. Only the symbols
in `puckworks.__all__` are the public API; everything else is internal research tooling that may
change without notice.

## The supported API

```python
import puckworks

puckworks.__version__                 # str

# registry query
puckworks.load_builtin_components()   # -> int (idempotent; registers the built-ins)
puckworks.components(stage=None)      # -> list[Component]  (read-only snapshots)
puckworks.get("cameron2020.extraction_bdf")   # -> Component (read-only snapshot)
puckworks.Component                   # the component metadata dataclass

# gate evaluation (typed; runs every gate, no short-circuit)
puckworks.evaluate_all_gates()        # -> GateSuiteResult (.passed, .to_dict(), .summary_text())
puckworks.GateStatus                  # PASS / FAIL / SKIP / ERROR / ACKNOWLEDGED_EXCEPTION
puckworks.GateResult, puckworks.GateSuiteResult

# public namespaces
puckworks.contracts                   # typed physics state dataclasses (SCHEMA_VERSION)
puckworks.validate                    # boundary units + validators + versioned Trace
puckworks.product                     # product-facing contract (see below)
```

### `puckworks.product` — product contract (issue #32)

```python
from puckworks import product

product.available_fixtures()                       # -> tuple[str, ...]
shot = product.load_bundled_shot("waszkiewicz2025_9bar_single_shot")   # -> ShotInput
product.to_json(shot)                              # canonical, deterministic JSON (str)
product.bundle_from_json(text)                     # -> ShotExplanationBundle
```

`puckworks.product` is a **supported, additive** namespace with its own `product.__all__`: the
orthogonal enums (`SeriesKind`, `AvailabilityStatus`, `CompatibilityStatus`, `RecordKind`), the
typed records (`ShotInput`, `ObservedSeries`, `TimeAxis`, `EvidenceReference`, `BuildProvenance`,
`FixtureProvenance`, `DetectedEvent`, `Caveat`, `NextMeasurement`, `ExplanationCandidate`,
`NormalizedShot`, `ShotExplanationBundle`), canonical serialization (`to_dict`/`to_json`/
`bundle_from_*`/`shot_input_from_*`), and `build_provenance` / `load_bundled_shot`. Its records and
serialized schemas (`SCHEMA_VERSION = 1`) follow the stability policy below. Every `_`-prefixed
submodule (`_records`, `_serialize`, `_provenance`, `_fixtures`, `_enums`) is **internal**; no
harness, paper, registry, or model implementation object is exposed. (PR 1 ships the contract,
serialization, and one fixture only — no `analyze_shot`/model orchestration/HTML output.)

## What is NOT public (internal research tooling)

`harness`, `analysis`, `paper3`, `paper_a`, `paper_b`, `figures`, `figures_paper_a`, `lib`, `viz`,
`inventory`, `release`, `statusdoc`, and every `_`-prefixed name. These support the science and the
release/publication machinery; they are importable but **not** covered by the stability policy, and
should not be depended on by external code. The product-facing API is `puckworks.product` (above) —
a distinct supported surface built on narrow `_`-prefixed adapters, **not** these internals.

## Stability policy

- **Semantic versioning** covers the names in `puckworks.__all__` and the serialized schemas listed
  below. A breaking change to any of them bumps the MAJOR version.
- **Additive is safe**: new components, new gates, new fields on a versioned schema, new public
  functions — these are MINOR.
- **Deprecation**: a public symbol slated for removal keeps working for **at least one MINOR
  release** with a `DeprecationWarning` and a documented replacement, before removal in a MAJOR.
- **Serialization compatibility**: every serialized public schema carries a `schema_version` and is
  extended additively (fields are added, never repurposed) — `contracts.SCHEMA_VERSION`,
  `registry.SCHEMA_VERSION`, `gate_runner`/`GateResult` `schema_version`, `validate.Trace`
  `schema_version`, `product.SCHEMA_VERSION` (`ShotExplanationBundle`), the evidence-graph and
  status-doc schema versions. A reader/migration is provided for any already-published schema.
- **Internal churn is free**: harness/analysis/paper* internals may change in any release.

## Reader paths

| you are… | start here |
|---|---|
| **a new user** | README quick start → `puckworks.evaluate_all_gates()` and `puckworks.components()` on an installed wheel |
| **a scientific user** | `docs/cards/` (physics per model), `docs/paper3_resource/EVIDENCE_GRAPH.md` (per-claim evidence), `docs/UNITS_POLICY.md` |
| **a contributor** | `CONTRIBUTING.md`, `docs/CI_LANES.md`, `docs/paper3_resource/EVIDENCE_GRAPH.md` (adding a gate/component), this file |
| **a release manager** | `docs/reproducibility/RELEASE_RUNBOOK.md` (v0.2.0 rehearsal), `docs/status/current.json` → `STATE_OF_TRUTH.md` |

Current project status is generated at `docs/planning/STATE_OF_TRUTH.md` from
`docs/status/current.json` — do not depend on commit-specific planning prose.
