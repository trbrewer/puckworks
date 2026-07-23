# Component response & model-disagreement atlas — pre-analysis specification v1

Scheduled backlog specification for research program **RP-A** (ROADMAP §9). This is a
plan, not a result: nothing here is executed, validated, or promoted by its existence.
Committed BEFORE any response sweep is run; its hash (`spec_version` + content) is
intended to ride in every atlas artifact, and a post-hoc change to a summary, taxonomy,
or comparability rule must create a NEW explicitly-versioned spec, not silently edit
this one (mirroring the `PRESSURE_ATLAS_SPEC.md` discipline).

**spec_version: `component-response-atlas/v1`**

Extends the Phase 2 comparison harnesses (ROADMAP §3 items 2.1 extraction, 2.2 κ(t))
by asking a structural question about the whole registry, not one pairwise residual. It
reuses — never redefines — the pressure-node convention (ROADMAP §5.9, ledger A1) and the
observable convention (ROADMAP §5.10, ledger A10). It is distinct from
`PRESSURE_ATLAS_SPEC.md`, which is a machine-command-tracking telemetry study over a
public shot corpus and defines no model/component inventory.

## 1. Question, unit, scope

For each registered executable component: what relationship does it encode between its
inputs, states, and outputs, and where components answer the SAME scientific question,
do they agree — in sign, magnitude, curvature, limiting behaviour, and regime — or not,
and why? Unit of analysis = one (component, relationship) pair for the response half, and
one (comparable-observable group, intervention) tuple for the disagreement half.

Out of scope: any claim that a disagreement is resolved, any evidence-strength promotion,
any pooled cross-model leaderboard, and any implication that every component maps pressure
to TDS (see §3).

## 2. Parameter / observable inventory (machine-readable)

One row per (component, quantity). Required fields, each validated against the live
registry / cards where a registry source exists:

- `component_id` — registered ID (e.g. `cameron2020.extraction_bdf`).
- `stage` — grind / packing / machine / infiltration / flow / bed_dynamics / extraction / observables.
- `quantity_name`.
- `direction` — input / output / state.
- `unit` and `reference_basis` (SI at contract boundaries; node/observable basis per A1/A10).
- `physical_definition` — one sentence.
- `role` — controlled · measured · fitted · fixed · derived · closure · state.
- `provenance` — card/table/equation or registry source.
- `valid_range` — from the card; `NOT_PROVIDED` where the card says so (never invented).
- `evidence_strength` — the §0 label of the component it belongs to; rides along UNCHANGED.
- `independently_variable` — whether the quantity can be varied on its own (y/n/derived).
- `relationship_kind` — direct vs adapter-mediated (name the adapter / ledger item).
- `comparable_observable_group` — the group id used by the disagreement half (§4), or `none`.

## 3. Missing relationships are recorded, never implied

The inventory MUST record absence explicitly. Some components consume pressure
(`cameron2020.extraction_bdf`, `foster2025.infiltration`), some consume flow
(`pannusch2024.solver`, `wadsworth2026.inertial`), and some produce neither whole-cup TDS
nor extraction yield (`wadsworth2026.permeability`, `brewer2026.pack_generator`,
`brewer2026.lb_reference/lb_taichi`). A "no such mapping" cell is a first-class output; the
atlas may not fabricate a pressure→TDS response for a component that has none.

## 4. Comparability levels

Every candidate cross-component comparison is tagged with exactly one level:

1. **directly comparable** — same intervention, same observable, same reference basis.
2. **comparable through a declared adapter** — a named ledger adapter (A1/A3/A5/A10) bridges basis/units.
3. **same intervention, different observable** — comparable input, non-comparable output.
4. **same output label, different physical / reference basis** — e.g. the three `c_sat` conventions, per-bed vs per-grain inventory.
5. **not comparable** — no defensible bridge; recorded and excluded from any residual.

## 5. Response summaries

Per (component, controllable/uncertain quantity), where the response is defined and inside
the valid range:

- local derivative (∂output/∂input at a stated reference condition);
- dimensionless elasticity where mathematically meaningful (never for a quantity spanning zero);
- monotonicity (increasing / decreasing / approximately-flat / non-monotonic / insufficient — reuse `puckworks.viz.relationship.classify_relationship`; a one-grid-point wobble is not a reversal);
- curvature;
- thresholds / saturation points;
- pairwise interactions (a small set of declared pairs, not all pairs);
- dependence on the reference condition (report the reference; do not average across references);
- uncertainty envelope from declared parameter uncertainty (never an invented distribution);
- valid-domain boundary behaviour (what the response does at the edge of the card's range).

## 6. Analytic where available, controlled perturbation otherwise

Where a card / equation provides a closed-form relationship, derive the response analytically.
Only where no closed form exists, use controlled numerical perturbation of the authoritative
producer (no equation reimplemented). Do NOT fit a linear model by default — linearity is a
finding to be tested, not an assumption.

## 7. Disagreement taxonomy

Every recorded disagreement is classified as exactly one of:

- **sign** — the responses point in opposite directions;
- **magnitude** — same sign, materially different size (with a stated practical-difference bound);
- **curvature / regime** — different shape or a different limiting/asymptotic regime;
- **parameter-uncertainty-explained** — the disagreement lies within propagated parameter uncertainty;
- **semantic / non-comparable** — a comparability-level-4/5 artifact (different bookkeeping), not a physical disagreement;
- **unsupported comparison** — the comparison was never defensible (comparability level 5); flagged, not scored.

## 8. Bounded pilot

A small representative pilot over executable components, selected only AFTER inspecting
registry support and the cards. Candidate slots (final selection recorded at run time):

- one extraction component — candidate `cameron2020.extraction_bdf`;
- one hydraulics / permeability component — candidate `wadsworth2026.permeability` or `wadsworth2026.inertial`;
- one machine / wetting / deformation component — candidate `foster2025.infiltration`, `foster2025.machine_mode`, or `waszkiewicz2025.poroelastic`.

The pilot produces one response report per selected component and one matched-comparison
report for the comparable groups those three span; it does not attempt the whole registry.

## 9. Deliverables

- the parameter/observable/comparability schema (§2, §4) as a machine-readable artifact;
- per-component response reports (§5);
- a reproducible response-sweep specification (seeds, reference conditions, perturbation sizes);
- a matched-comparison and disagreement report (§7) with comparability tags;
- evidence-labelled plots or tables (labels ride along unchanged);
- tests for units, valid-range enforcement, deterministic output, and explicit unsupported-relationship cells;
- a **conditional** public-value article, "Where espresso models agree, disagree, and answer different questions" (the public face is PV-08; see §10).

## 10. Publication guardrail

A public article is CONDITIONAL on at least one robust, non-obvious result. A manuscript is
only a *candidate* if the study yields a novel comparison method, a scientifically important
unresolved disagreement, or independently tested model discrimination. No manuscript is
scheduled and no publication claim is made now. Any public output routes through PV-08 and
carries every source component's evidence-strength label unchanged.

## 11. Provenance

Every atlas artifact emits: this spec hash, the code commit, the registry snapshot, the
per-quantity provenance, the reference conditions and perturbation sizes, the comparability
tags, and a frozen-vs-exploratory mark. A partial/unfinished run is stamped
`EXPLORATORY — NOT A PUBLICATION SNAPSHOT`.
