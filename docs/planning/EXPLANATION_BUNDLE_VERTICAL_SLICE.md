# Evidence-aware explanation-bundle vertical slice — current product implementation plan

> **Authority.** This is the **current scoped product implementation plan**. Project **status**
> remains governed by [`docs/status/current.json`](../status/current.json) and the generated
> [`docs/planning/STATE_OF_TRUTH.md`](STATE_OF_TRUTH.md). The archived
> [`PRODUCT_FIRST_REPRIORITIZATION.md`](archive/PRODUCT_FIRST_REPRIORITIZATION.md) is
> **historical design input, not current authority**. This task selects **only** the first contract /
> golden-result outcome — not the entire archived product backlog.

Decision record: issue **#32**.

## 1. Decision and user outcome
Select one product-facing P0 outcome after the verified v0.2.0 GitHub release: a user can run one
bundled, redistributable espresso shot through a documented product-facing API and receive a
trustworthy explanation result — without reading repository internals or a manuscript. The primary
deliverable is a versioned, deterministic `ShotExplanationBundle` for one redistributable golden
shot, generated from an installed Puckworks wheel.

## 2. Scope
- A typed, versioned product contract (`puckworks/product/`) and its serialization.
- One redistributable golden-shot fixture with recorded provenance + license.
- Deterministic versioned JSON output and a human-readable static export.
- At most three bounded explanation candidates with explicit evidence semantics.
- Installed-wheel golden-path verification.

## 3. Explicit non-goals
Generic CSV upload; DE1 or Visualizer adapters; broad public dashboard; every registered model;
universal channeling score; flavor prediction; recipe optimization; inferred permeability as ground
truth; public data donation; release-workflow automation; PyPI publication; repository-wide harness
refactor; repository-wide strict typing.

## 4. Existing repository capabilities to reuse
- Registry + typed gate evaluation (`puckworks.registry`, `puckworks.gate_runner`) for
  component/claim IDs, gate state, and evidence strength — consumed, not rebuilt.
- Contract types + unit discipline (`puckworks.contracts`, bar-gauge vs pascal, versioned trace
  schema/validators from #25).
- Paper 3 per-claim evidence graph (schema v2) for claim/evidence references.
- Internal numerical, registry, gate, data, and evidence providers — invoked **only** through narrow
  private adapters (see the Product API boundary below), never re-exposed publicly.

### Product API boundary
`puckworks.product` will be an additive public namespace.

External consumers use only:

    import puckworks
    puckworks.product

The implementation PR will:

- add `product` to top-level `puckworks.__all__`;
- define a separate `puckworks.product.__all__`;
- document the new namespace in `docs/API.md`;
- expose product records and supported product functions only through that namespace;
- avoid adding every product record directly to the top-level namespace.

The product implementation may invoke internal numerical, registry, gate, data, and evidence
providers only through narrow private adapters located under `puckworks.product` and prefixed with `_`.

No public signature, dataclass field, exception payload, serialized field, or return value may expose:
harness objects; paper/manuscript objects; registry implementation objects; internal model result
objects; NumPy-specific implementation details; repository-relative filesystem paths.

Private adapters require characterization tests. External callers never import those adapters.

## 5. Golden-shot data/provenance selection gate
Before any bundle work: select **one** fixture with a known source, **recorded redistribution/license
status**, explicit units, documented timing channels, small enough to ship and test, and supporting
at least two materially different explanations. If no redistributable fixture qualifies, STOP and
report — do not synthesize a shot presented as real, and do not use non-redistributable corpus data.

### Fixture record kind
The fixture manifest must declare `record_kind`: `single_shot` | `aggregate_reference_case`.

Requirements for `single_shot`: one identifiable experimental run; source record or source member is
individually addressable; timing and channels belong to that one run; it is **not** a mean, median,
ensemble, or fitted reconstruction.

Requirements for `aggregate_reference_case`: aggregation procedure is documented; replicate count and
uncertainty channels are retained where available; product language never calls it a shot or an
observed individual event.

**The active outcome currently requires `single_shot`.** If only an aggregate qualifies: stop before
product implementation; update issue #32, `current.json`, and this plan through a separate reviewed
planning correction; do not silently relabel the aggregate as a shot.

### Explanation selection
Explanation candidates are selected **only after** fixture qualification. A model must have the
required observable inputs and a documented comparison interpretation. Do not treat a mechanism
validated for a distinct time regime or phenomenon as a competing fit merely to fill three slots.
Fewer than three candidates is valid. A single overall winner remains prohibited.

## 6. `ShotInput` and normalized-input contract
- `ShotInput`: raw user/fixture input — time series (pressure, flow or cumulative mass), optional
  command/setpoint, temperature; declared units; declared time origin; fixture ID.
- `normalize_and_validate(shot_input) -> NormalizedShot`: explicit unit conversion at the boundary
  (SI internally), monotonic-time and missing-value checks, no silent inference of ambiguous units,
  pressure reference, or flow-vs-cumulative-mass.

## 7. `ShotExplanationBundle` v1 contract
`ShotExplanationBundle` must contain: `schema_version`; `package_version`; `source_commit`; input
fixture ID + digest; generation provenance; normalized units; observations and events; explanation
candidates; evidence references; warnings; caveats; next measurement; deterministic serialization.

**Build and source provenance.** `source_commit` and package build identity must come from an explicit
deterministic build-provenance provider or serialized package resource. Public bundle generation must
NOT: call `git rev-parse`; assume a repository checkout; inspect `.git`; derive identity from the
current working directory; or insert the current wall clock implicitly. The installed-wheel golden
path must produce the full source commit without a Git checkout. Timestamps, when included, are
explicit inputs; they are excluded from byte-stable golden output unless a fixed value is supplied.

## 8. Result semantics — four orthogonal dimensions
The contract has separate fields/enums for series origin, availability, compatibility, and evidence.

- **`SeriesKind`** (origin of an available numerical series): `measured`, `derived`, `fitted`,
  `predicted`, `simulated`.
- **`AvailabilityStatus`** (recorded independently): `available`, `unavailable`, `unsupported`, `failed`.
- **`CompatibilityStatus`** (per explanation): `compatible`, `partly_compatible`, `contradicted`,
  `insufficient_evidence`, `outside_model_scope`.
- **`EvidenceReference`**: source scheme; source identifier; source evidence-strength value; source
  gate status; provenance.

Invariants:
- availability is not a series origin;
- compatibility is not evidence strength;
- numerical fit is not evidence strength;
- an unavailable result has no invented numerical series;
- missing numerical values use explicit validity/availability semantics;
- NaN and infinity are never emitted in public JSON;
- source evidence labels are preserved rather than translated upward.

Each explanation candidate states: compatible observations; incompatible observations; missing
evidence; evidence references; supporting component/claim IDs; caveats; one discriminating next
measurement. **No single overall winner score.** No unsupported causal diagnosis.

## 9. Orchestration boundary
```
normalized = normalize_and_validate(shot_input)
bundle      = analyze_shot(normalized)
```
`analyze_shot` coordinates internal producers, normalizes their result semantics, attaches evidence,
returns partial results when one explanation is unavailable, and reports insufficiency without
fabricating a winner. The consumer must **not** import `harness`, `paper*`, manuscript, or `registry`
internals directly — only the product package's public surface.

## 10. Deterministic serialization and export
Deterministic versioned JSON: UTF-8; sorted keys; `allow_nan=False`; stable sequence ordering; no
implicit wall-clock value; **no runtime Git lookup**; identical bytes across supported Python
3.10–3.13 for the golden object. Timestamps are explicit inputs, excluded from byte-stable golden
output unless a fixed value is supplied. A human-readable static report (self-contained HTML or
equivalent) that preserves the measured/modelled distinction without relying on color alone (a later
PR). A golden JSON fixture pins the contract.

## 11. Test and verification matrix
Unit + schema validation; golden regression fixture (byte-stable JSON); serialization round-trip;
installed-wheel clean-room golden path; partial-result behavior when one explanation is unavailable;
negative tests (unsupported diagnosis, evidence upgrade, unit confusion must fail); measured-vs-modelled
distinction preserved in export.

## 12. Ordered implementation PRs
PR 1 was **split** so a rights-blocked fixture cannot block the rights-independent contract:

- **PR 1A — public product contract** (PR #34): public namespace; typed/versioned records; canonical
  serialization; Git-free provenance; strict validation; a **test-only synthetic** golden; **no runtime
  fixture**. No `analyze_shot`, model execution, explanation conclusions, or HTML.
- **PR 1B — approved real fixture** (separate, after rights approval): one formally redistributable
  individual shot; source and transformed hashes; manifest; attribution; public loader; wheel/sdist
  inclusion; installed-wheel golden path. Blocked on the Waszkiewicz member-license clarification
  (RadostW/espresso#1) or another explicitly-licensed single shot.
- **PR 2A — normalization boundary**: explicit-unit validation; time alignment; pressure-node/reference
  handling; flow-versus-mass semantics; **no model conclusions**.
- **PR 2B — analysis orchestration**: fixture-supported explanation candidates; evidence/caveats; no
  overall winner; next-measurement logic.
- **PR 3 — human-readable static result/export.**
- **PR 4 — evidence-comprehension review + wording corrections.**

Issue #32 remains open until the complete outcome is delivered. Generic import begins only after the
bundled result is understandable and scientifically modest.

## 13. Risks and stop conditions
- No redistributable golden fixture qualifies → STOP at §5.
- Only an aggregate qualifies but is labelled a shot → STOP; propose a reference-case planning correction.
- A public product type or consumer would need to import an internal object → redesign the boundary.
  Private characterized adapters may invoke internal providers, but no internal type may escape the
  product namespace.
- Any wording implies channeling/flavor/recipe/permeability not supported by evidence → block.
- Installed-wheel source provenance would require a Git checkout, or canonical JSON differs across
  supported Python versions → STOP and redesign the provenance/serialization boundary.

## 14. Definition of done
One bundled shot produces deterministic versioned JSON **and** a human-readable result from an
installed wheel; every series is classified; ≤3 explanations state supporting/contradicting/missing
evidence, caveats, and one discriminating next measurement; units, provenance, component/claim IDs,
schema/package/source versions, serialization round-trip, golden regression, and clean-room smoke are
verified; no unsupported diagnosis, flavor prediction, or recipe optimization is emitted.

## 15. Deferred follow-ups
Generic CSV import (only after the bundled result is understood); a next-measurement recommender;
release-workflow automation (a later P1); PyPI publication (separate, unapproved). None are in scope here.
