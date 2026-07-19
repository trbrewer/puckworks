# Guided Pull Laboratory (PV-19B)

**Development work (`0.4.0.dev0`) — not part of the released v0.3.0.**

The Guided Pull Laboratory exposes the *full* component registry while running only the *compatible*
subset as **independent model lenses**. It never sums or averages competing mechanisms, never presents
model agreement as validation, and is **not** a digital twin.

```bash
python -m puckworks.product.lab matrix   --format md      # all-component coverage matrix
python -m puckworks.product.lab compare  --format md      # common-scenario comparison + reference suite
python -m puckworks.product.lab compare  --format json    # deterministic machine report (schema v5)
python -m puckworks.product.lab compare  --domain-policy strict --references none   # request controls
```

## Two modes

1. **Common-scenario model lenses.** One bounded espresso scenario (the `pv19_named` fixed reference
   recipe) is mapped into the *compatible* models. Each model runs independently through its existing
   authoritative producer. Today `cameron2020.extraction_bdf` is the single executed common-scenario
   lens (via `puckworks.product.simulate_pull` — no equation is re-implemented). Results are overlaid
   only when observable definition, units, reference volume, and axis are compatible.
2. **Component reference suite.** Executable components' native reference cases demonstrate that the
   registry works. Each is labelled *"the component's own native reference case, not the common Guided
   Pull scenario."* **Four** genuinely-executed native reference runners ship today (`puckworks.product.
   lab_runners`), each reusing the same authoritative callables the validation gates use — no equation
   duplication:
   - `waszkiewicz2025.poroelastic` — refit the published equilibrium curve; recover `(P_c, Q_c)` vs the
     published calibration; `interactive-fast`;
   - `wadsworth2026.permeability` — collapse Table 1 onto the percolation permeability form (geometric-
     mean ratio); `interactive-fast`;
   - `foster2025.infiltration` — parameter-free first-drip bracket vs the DE1 fixture observation;
     `interactive-fast`;
   - `brewer2026.lb_reference` — solve the component's canonical **synthetic plane channel** and compare
     the lattice permeability to the **exact plane-Poiseuille** `k = h²/12`; `batch-only`. Its verification
     input is generated in code and its reference is the analytic channel solution — this is **numerical
     code verification, not experimental evidence** and not coffee/espresso validation (fidelity ceiling:
     *"does not validate porous coffee-bed physics, predict espresso extraction, establish experimental
     accuracy, or provide a directly comparable beverage metric"*). A genuine multi-second LB solve, it is
     honestly classified `batch-only` — outside the interactive-fast budget, selectable explicitly, and
     not in the default fast sweep (the three source-data runners above stay `interactive-fast`).

   Runner failures are isolated (one erroring never erases the others; `FAILED` is a per-request
   *execution* state, never a static capability). A component's native runner *capability* is `AVAILABLE`
   / `NOT_IMPLEMENTED` / `OPTIONAL_DEPENDENCY_UNAVAILABLE` / `RIGHTS_BLOCKED` / `NOT_APPLICABLE`;
   `grudeva2025.reduced` is `RIGHTS_BLOCKED` (issue #73). A future integrated chain may pick one compatible
   component per physical stage; competing models remain branches.

## Coverage vocabulary

Every registered component (enumerated from `puckworks.components()`, never a hard-coded count) gets
exactly one disposition: `COMMON_SCENARIO_READY`, `COMMON_SCENARIO_WITH_VERIFIED_ADAPTER`,
`NATIVE_REFERENCE_ONLY`, `SUPPORTING_STAGE_LENS`, `CALIBRATION_OR_CLOSURE`, `ADAPTER_REQUIRED`,
`OUTSIDE_SCENARIO_DOMAIN`, `RIGHTS_BLOCKED`, `NOT_EXECUTABLE`, `SKIPPED_OPTIONAL_DEPENDENCY`, `FAILED`,
or `METADATA_INCOMPLETE` (an honest fallback when a component's registry metadata is missing — never an
invented capability).

## Contract (schema v5)

Scenario identity is exact: a `pv19_named` run is `pv19_named`, a `guided_v1` run is `guided_v1`, and a
custom `guided_v1` run records its base preset plus every applied override (`base` → `effective`). The
entry point is typed — `execute_scenario(ScenarioRequest) → ScenarioExecution` then
`build_comparison(execution) → ComparisonRun` — so a bare `PullRun` dict can no longer be mislabelled.
`run_scenario()` remains only as a documented compatibility wrapper returning the raw run.

### Request semantics (explicit and validated)

- **`domain_policy`** (`warn` | `strict`) is *operational*: the effective config carries the request's
  policy and the domain is evaluated **once, up front**, through the authoritative product domain. A
  `REJECTED` input blocks under any policy; an evidence-range `WARNING` blocks under `strict`. When
  blocked the scientific producer is **not** called (`domain.producer_executed == false`), and the
  requested lens is surfaced as `REQUESTED_BUT_NOT_EXECUTABLE` — never silently produced as zero.
- **`lens_selection_policy`** (`primary` | `all_ready` | `selected` | `none`) chooses which
  common-scenario lenses run. Execution is **adapter-driven**: `prepare_scenario()` builds a
  model-independent scenario (no producer call), then only the selected, ready, in-domain lenses execute
  through their `LensAdapterSpec` (the first adapter wraps Cameron and calls the existing `simulate_pull`).
  The producer is invoked **only** for a selected+ready+in-domain lens — selecting `none`, a
  registered-but-non-ready component, a rights-blocked lens, or a domain-blocked Cameron runs **no**
  producer, and `counts.common_scenario_producer_invocations == counts.executed_common_scenario_lenses`.
  `requested_lens_ids` requires `selected`; duplicates canonicalize; adding a future adapter never changes
  `primary`. Each lens keeps its OWN domain findings (Cameron's evidence domain is not applied globally).
- **`reference_selection_policy`** (`none` | `interactive_fast` | `selected`) resolves **components**: a
  registered component with no runner is `RUNNER_NOT_IMPLEMENTED`, a rights-blocked one is `RIGHTS_BLOCKED`
  (never executed); only a non-registered id is "unknown" and raises. Ids are meaningful only under
  `selected`.

**Capability is never conflated with execution.** The `capability_snapshot.component_matrix` records the
*static* `native_runner_capability` / `common_scenario_adapter_capability`; the *per-request*
`reference_selection[].native_runner_execution_state` records what actually ran for this request.

### Three integrity layers (each recomputed, never trusted from the field)

- **scientific payload** (`scientific_payload_sha256`) — the science, free of build provenance **and** of
  the environment-dependent capability snapshot; stable across build identity, Python version, and
  optional-dependency installation (installing Taichi does not change it for a Cameron-only request);
- **capability snapshot** (`capability_snapshot_sha256`) — the env-dependent capability/rights matrix,
  optional-dependency availability, and interpreter fingerprint;
- **full artifact** (`artifact_sha256`) — the complete downloadable JSON *including* build provenance
  (`package_version`, `source_commit`, `workflow_run_id`, `wheel_sha256`) and the other two hashes,
  excluding only its own field. Provenance is supplied **explicitly** by the caller (the batch workflow
  passes `GITHUB_SHA` / `GITHUB_RUN_ID` / the wheel SHA); the scientific producer runs no git subprocess.

`verify_integrity(report)` recomputes all three from the report's own content and reports any mismatch
(a tampered `dose_g` trips the scientific + artifact hashes; a tampered capability field trips the
capability + artifact hashes but leaves the scientific hash intact). Canonical JSON is **finite** —
`NaN`/`Infinity` are rejected, never serialized.

Observable roles trace the producer: pressure and target beverage are **prescribed**; mean flow is
**derived**; extracted mass / extraction yield / TDS / shot duration are **simulated**; first drip is
**unsupported** (saturated bed); first modeled solute arrival is a **derived diagnostic**, explicitly
`is_physical_first_drip: false`.

The component capability matrix is explicit (not a substring heuristic): the common-scenario
**disposition** and **adapter capability** for every registered component are stated in the committed
`puckworks.product.lab_catalog` (validated against the registry — gate ids resolve, runner/adapter ids
resolve, rights match `puckworks.rights`, a rights-blocked component is dispositioned `RIGHTS_BLOCKED`),
and `_lab_spec` consumes that catalog rather than a `stage`/`kind` heuristic. Every registered component has
one validated `ComponentLabSpec` with callable/runtime/calibration flags, `native_runner_capability`,
`common_scenario_adapter_capability`, and concentration reference basis. **Rights truth is centralized in
`puckworks.rights`** (one record per component with distinct `code_rights_state` / `data_rights_state` /
`output_redistribution_state`; an unreviewed component is `NOT_REVIEWED`, never a silent `CLEAR`). Rights
are **use-specific** — `rights.may_execute_locally` / `may_execute_in_public_batch` /
`may_publish_outputs` / `may_include_code_in_release` / `may_include_data_in_release` each consult the
relevant field with the strictness that use demands: `RIGHTS_BLOCKED` is refused everywhere;
`NOT_REVIEWED` stays inspectable **locally** but is a visible gap for public execution / output
redistribution / release (never "clear"); only an affirmative clearance permits an outward or release
use. `grudeva2025.reduced` is `code RIGHTS_BLOCKED` (#73) and can never be a lens, native runner, or
adapter; the release guard hard-blocks only on code not cleared for release inclusion (no
`--allow-rights-blocked` bypass — an authorized removal makes it pass) and reports `NOT_REVIEWED` gaps.
`rights.review_backlog()` surfaces the reviews still owed (Cameron code + outputs first).
`capability_snapshot.reference_suite_coverage` lists runner *capabilities* honestly; only
actually-executed references appear in `executed_reference_results`.

### Selected-references-only public artifact (per-component, affirmative-only)

Public execution is enabled **one component at a time, only after an affirmative outward rights review** —
never a blanket switch. `brewer2026.lb_reference` is the **first** component with such a clearance (code
`CLEAR`, data `NOT_APPLICABLE`, output `CLEAR`; bounded to its synthetic LB channel code-verification path,
issue #70 — see `docs/rights_review_notes.md`). A request that selects **exactly** that runner
(`lens_selection_policy=none`, `reference_selection_policy=selected`,
`requested_reference_runner_ids=("brewer2026.lb_reference",)`) passes the `PUBLIC_ARTIFACT` preflight and
runs precisely one native producer; the published artifact carries the cleared preflight record and the
execution context alongside the scientific result. A references-only artifact has no common-scenario trace,
so the batch's required-figure gate applies only when a lens executed; the absence of a trace panel is
recorded, never silently skipped.

This is **not** a generic public-execution bypass. The **default / broad** public Laboratory batch remains
**gated**: it selects the Cameron primary lens (still `NOT_REVIEWED`), so a default `PUBLIC_BATCH` /
`PUBLIC_ARTIFACT` run blocks before any producer and emits only the rights preflight. A mixed request
pairing the cleared LB runner with any `NOT_REVIEWED` runner blocks as a whole (one blocked selection blocks
the request); the LB clearance never propagates to Cameron, Roman, Waszkiewicz, Wadsworth, Foster, or any
other component, and `grudeva2025.reduced` stays hard-blocked in every context (#73).

## Reference-basis groundwork (a possible second lens)

A second common-scenario lens would overlay another model's EY/TDS on Cameron's — meaningful only on the
same quantity basis or through a **tested, inventory-conserving** conversion. `reference_basis` makes the
basis a typed value (`QUANTITY_BASES`: `bed_volume` / `grain_volume` / `per_bed_cell` / `per_species` /
`liquid_phase_profile` / `flow_trend` / …) and provides **fail-closed** conversion primitives: the only
registered rule is the identity, so every cross-basis request raises `UnsupportedConversion` (no invented
scale factor), and `assert_inventory_conserved` rejects any transform that does not conserve total solute
inventory. Admissibility is therefore mechanical — `mo2023_2.coupled_bed` (per-bed-cell) and
`pannusch2024.solver` (per-species) have no validated conversion, `romancorrochano2017.extraction` is a
flow trend, and `grudeva2025.reduced` is rights-blocked (#73). **No candidate is admissible, so no second
lens is added**; the ontology, validators, and audit are the deliverable. `python -m
puckworks.product.reference_basis --format md` prints the readiness report.

## Native reference runner authority

Each native reference runner reuses the component's authoritative producer callables **and** delegates its
pass/band verdict to that component's quick gate — the gate is the single source of every threshold. The
wadsworth `0.7 < ratio < 1.2` collapse band, the foster `> 0.5 g` first-drip threshold, and the
waszkiewicz refit tolerances live only in `gate_wadsworth_collapse` / `gate_infiltration_triangle` /
`gate_waszkiewicz_static_refit`; the runner surfaces that verdict verbatim (a `gate_authority` block) and
never re-derives the literal. The foster first-drip crossing is explicit: no crossing → `unavailable`
(never a false `argmax` sample at t[0]). `RunnerSpec` and the registry are validated
(`validate_runners()`), results are schema-sanitized and finite, and selection raises on an unknown id
(`run_selected(..., strict=True)` by default; `available_runners()` lists the selectable set).

## Unit-safe figures

`lab.render_data(report)` is the single shared plotting layer for the Streamlit UI and the Actions batch,
and it is **unit-safe by construction**: every source trace is split into one panel *per unit*, so a
single ordinary y-axis never overlays incompatible units (bar / g/s / g / % / kg/m³). `assert_unit_safe`
rejects a mixed-unit panel; both renderers call it, so neither can draw one. The batch writes one figure
**and** one CSV (the text-alternative) per panel, records a `panel_inventory` in the manifest, and keeps
the required-figure gate — if nothing is plottable the job fails, never a silent skip. The Streamlit UI
adds a per-unit panel selector, a per-panel data table + CSV download, an axis unit label, and a
`domain_policy` control that surfaces the strict block path.

## Honesty boundaries (enforced by tests)

- **No incompatible units on one ordinary y-axis** (bar / g/s / g / % / kg/m³ are never overlaid); the
  plotting layer splits by unit and a validator rejects a mixed-unit panel.
- No summing/averaging of competing mechanisms; no ensemble without a defensible statistical model.
- Competing extraction models (`grudeva2025.reduced`, `pannusch2024.solver`,
  `romancorrochano2017.extraction`, `mo2023_2.coupled_bed`) are `ADAPTER_REQUIRED`: their concentration
  reference volumes / observables differ (e.g. Cameron bed-volume vs Grudeva grain-volume), so they are
  **not** overlaid until an inventory-conserving conversion is tested.
- No grinder dial is treated as a universal particle size; no dial→size conversion is applied.
- Evidence labels ride through from the producer unchanged; no comparison result upgrades evidence.
- Optional accelerator/GPU components (`brewer2026.lb_taichi`) are `OPTIONAL_DEPENDENCY_UNAVAILABLE` when
  absent and never enter the base install; a skip is never counted as a pass.
- Serialization is deterministic (schema v5, distinct from `PullRun` v1) with no wall-clock in the
  canonical content, and rejects non-finite floats.

## How a lens/adapter enters later

A lens adapter must: declare the wrapped component, check domain, map scenario fields to native inputs,
record every mapping/assumption, reject missing inputs, never silently clamp, execute the existing
authoritative producer, translate only known-semantics outputs, keep the native outputs, attach
evidence/scope, and fail safely (a failed lens never erases other lenses). No adapter may duplicate a
model equation already in the repo. `grudeva2026` (issue #67) could enter as a lens only after its
separate implementation and a demonstrated reference-volume adapter.

## What this does not prove

Model agreement is not validation. The common scenario is not a best recipe and predicts no flavor.
Native reference results are not predictions of one common shot. See the report's own
"what this does not prove" section, always emitted.
