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
- The public API surface (`puckworks.__all__`) as the only supported dependency for the product layer.

## 5. Golden-shot data/provenance selection gate
Before any bundle work: select **one** fixture with a known source, **recorded redistribution/license
status**, explicit units, documented timing channels, small enough to ship and test, and supporting
at least two materially different explanations. If no redistributable fixture qualifies, STOP and
report — do not synthesize a shot presented as real, and do not use non-redistributable corpus data.

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

## 8. Explanation and evidence semantics
Every displayed series is classified **measured / derived / fitted / predicted / simulated /
unsupported-or-unavailable**. Each explanation candidate states: compatible observations; incompatible
observations; missing evidence; evidence strength; supporting component and claim IDs; caveats; one
discriminating next measurement. Compatibility outcomes: `compatible`, `partly compatible`,
`contradicted`, `insufficient evidence`, `outside current model scope`. **No single overall winner
score.** No evidence-strength upgrade by inference; no unsupported causal diagnosis.

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
Deterministic versioned JSON (stable key order; no wall-clock in the payload — provenance timestamps
are inputs). A human-readable static report (self-contained HTML or equivalent) that preserves the
measured/modelled distinction without relying on color alone. A golden JSON fixture pins the contract.

## 11. Test and verification matrix
Unit + schema validation; golden regression fixture (byte-stable JSON); serialization round-trip;
installed-wheel clean-room golden path; partial-result behavior when one explanation is unavailable;
negative tests (unsupported diagnosis, evidence upgrade, unit confusion must fail); measured-vs-modelled
distinction preserved in export.

## 12. Ordered implementation PRs
- **PR 1** — typed/versioned product contract, serialization, fixture manifest.
- **PR 2** — normalization + analysis orchestration, deterministic golden bundle.
- **PR 3** — human-readable static result/export + installed-wheel golden-path smoke.
- **PR 4** — evidence-comprehension review + wording corrections.

Generic import begins only after the bundled result is understandable and scientifically modest.

## 13. Risks and stop conditions
- No redistributable golden fixture qualifies → STOP at §5.
- A product producer would need a harness/paper internal → redesign the boundary, do not import it.
- Any wording implies channeling/flavor/recipe/permeability not supported by evidence → block.
- Determinism cannot be achieved without wall-clock in the payload → move the timestamp to provenance inputs.

## 14. Definition of done
One bundled shot produces deterministic versioned JSON **and** a human-readable result from an
installed wheel; every series is classified; ≤3 explanations state supporting/contradicting/missing
evidence, caveats, and one discriminating next measurement; units, provenance, component/claim IDs,
schema/package/source versions, serialization round-trip, golden regression, and clean-room smoke are
verified; no unsupported diagnosis, flavor prediction, or recipe optimization is emitted.

## 15. Deferred follow-ups
Generic CSV import (only after the bundled result is understood); a next-measurement recommender;
release-workflow automation (a later P1); PyPI publication (separate, unapproved). None are in scope here.
