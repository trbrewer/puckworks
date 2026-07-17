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

`puckworks.product` is **unreleased next-minor** additive public API work — the published v0.2.0 wheel
and release assets are unchanged and do **not** contain it.

```python
from puckworks import product

product.available_fixtures()                       # -> tuple[str, ...] (APPROVED fixtures only)
shot = product.load_bundled_shot("<fixture_id>")   # -> ShotInput (raises FixtureRightsError if rights pending)
product.shot_input_to_json(shot)                   # canonical, deterministic JSON (str)
product.bundle_to_json(bundle)                      # -> str; product.bundle_from_json(text) -> ShotExplanationBundle
```

- **Two separately-versioned public top-level schemas**: `ShotInput`
  (`SHOT_INPUT_SCHEMA_VERSION = 1`) and `ShotExplanationBundle`
  (`SHOT_EXPLANATION_BUNDLE_SCHEMA_VERSION = 1`), each carrying its own `schema_version`.
- **Only explicit top-level serializers/readers are supported**: `shot_input_to_dict`/`_to_json`/
  `_from_dict`/`_from_json` and `bundle_to_dict`/`_to_json`/`_from_dict`/`_from_json`. There is **no**
  generic `to_json`/`to_dict`. Readers are strict — they require the schema version, reject
  unsupported versions, unknown top-level fields, and duplicate JSON keys.
- **`NormalizedShot` is deferred** until PR 2 (not public).
- Records are frozen with immutable typed containers (e.g. `normalized_units` is a tuple of
  `UnitBinding`, never a dict).
- **Provenance**: a serialized bundle always carries a **full 40-hex `source_commit`**; there is no
  runtime Git lookup. `build_provenance(source_commit=...)` requires an explicit or packaged commit
  and raises `ProvenanceUnavailableError` otherwise.
- **Rights/attribution** are carried by `FixtureProvenance`; the public loader only lists/returns a
  fixture whose `rights_review_status == approved` and `redistribution_status == redistributable`.
- Every `_`-prefixed submodule is **internal**; no harness, paper, registry, or model object is
  exposed. PR 1 has **no** `analyze_shot`, model orchestration, explanation scoring, or HTML output.

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
  `schema_version`, `product.SHOT_INPUT_SCHEMA_VERSION` and
  `product.SHOT_EXPLANATION_BUNDLE_SCHEMA_VERSION`, the evidence-graph and status-doc schema versions.
  A reader/migration is provided for any already-published schema.
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
