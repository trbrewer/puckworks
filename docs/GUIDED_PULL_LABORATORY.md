# Guided Pull Laboratory (PV-19B)

**Development work (`0.4.0.dev0`) — not part of the released v0.3.0.**

The Guided Pull Laboratory exposes the *full* component registry while running only the *compatible*
subset as **independent model lenses**. It never sums or averages competing mechanisms, never presents
model agreement as validation, and is **not** a digital twin.

```bash
python -m puckworks.product.lab matrix   --format md      # all-component coverage matrix
python -m puckworks.product.lab compare  --format md      # common-scenario comparison + reference suite
python -m puckworks.product.lab compare  --format json    # deterministic machine report (schema v4)
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
   Pull scenario."* Three genuinely-executed native reference runners ship today (`puckworks.product.
   lab_runners`), each reusing the same authoritative callables the validation gates use — no equation
   duplication:
   - `waszkiewicz2025.poroelastic` — refit the published equilibrium curve; recover `(P_c, Q_c)` vs the
     published calibration;
   - `wadsworth2026.permeability` — collapse Table 1 onto the percolation permeability form (geometric-
     mean ratio);
   - `foster2025.infiltration` — parameter-free first-drip bracket vs the DE1 fixture observation.

   All three are `interactive-fast`. Runner failures are isolated (one erroring never erases the
   others; `FAILED` is a per-request *execution* state, never a static capability). A component's native
   runner *capability* is `AVAILABLE` / `NOT_IMPLEMENTED` / `OPTIONAL_DEPENDENCY_UNAVAILABLE` /
   `RIGHTS_BLOCKED` / `NOT_APPLICABLE`; `grudeva2025.reduced` is `RIGHTS_BLOCKED` (issue #73). A future
   integrated chain may pick one compatible component per physical stage; competing models remain
   branches.

## Coverage vocabulary

Every registered component (enumerated from `puckworks.components()`, never a hard-coded count) gets
exactly one disposition: `COMMON_SCENARIO_READY`, `COMMON_SCENARIO_WITH_VERIFIED_ADAPTER`,
`NATIVE_REFERENCE_ONLY`, `SUPPORTING_STAGE_LENS`, `CALIBRATION_OR_CLOSURE`, `ADAPTER_REQUIRED`,
`OUTSIDE_SCENARIO_DOMAIN`, `RIGHTS_BLOCKED`, `NOT_EXECUTABLE`, `SKIPPED_OPTIONAL_DEPENDENCY`, `FAILED`,
or `METADATA_INCOMPLETE` (an honest fallback when a component's registry metadata is missing — never an
invented capability).

## Contract (schema v4)

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
- **`requested_lens_ids`** actually selects the common-scenario lenses (default: every executable common
  lens — today just Cameron). An unknown id raises; a registered-but-non-executable id is surfaced as
  `REQUESTED_BUT_NOT_EXECUTABLE`. `counts.executed_common_scenario_lenses` is **derived** from what ran.
- **`reference_selection_policy`** (`none` | `interactive_fast` | `selected`) is unambiguous. Under
  `selected`, `requested_reference_runner_ids` are validated (an unknown id raises; ids are meaningless
  under any other policy, so that combination is rejected rather than silently ignored).

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

The component capability matrix is explicit (not a substring heuristic): every registered component has
one validated `ComponentLabSpec` with callable/runtime/calibration flags, `native_runner_capability`,
`common_scenario_adapter_capability`, and concentration reference basis. **Rights truth is centralized in
`puckworks.rights`** (one record per component with distinct `code_rights_state` / `data_rights_state` /
`output_redistribution_state`; an unreviewed component is `NOT_REVIEWED`, never a silent `CLEAR`). The
Lab consumes it: `grudeva2025.reduced` is `code RIGHTS_BLOCKED` (#73) and can never be a lens, native
runner, or adapter; a release-readiness guard fails if a rights-blocked component would enter a new
artifact. `capability_snapshot.reference_suite_coverage` lists runner *capabilities* honestly; only
actually-executed references appear in `executed_reference_results`.

## Honesty boundaries (enforced by tests)

- No summing/averaging of competing mechanisms; no ensemble without a defensible statistical model.
- Competing extraction models (`grudeva2025.reduced`, `pannusch2024.solver`,
  `romancorrochano2017.extraction`, `mo2023_2.coupled_bed`) are `ADAPTER_REQUIRED`: their concentration
  reference volumes / observables differ (e.g. Cameron bed-volume vs Grudeva grain-volume), so they are
  **not** overlaid until an inventory-conserving conversion is tested.
- No grinder dial is treated as a universal particle size; no dial→size conversion is applied.
- Evidence labels ride through from the producer unchanged; no comparison result upgrades evidence.
- Optional accelerator/GPU components (`brewer2026.lb_taichi`) are `OPTIONAL_DEPENDENCY_UNAVAILABLE` when
  absent and never enter the base install; a skip is never counted as a pass.
- Serialization is deterministic (schema v4, distinct from `PullRun` v1) with no wall-clock in the
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
