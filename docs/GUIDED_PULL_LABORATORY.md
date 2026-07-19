# Guided Pull Laboratory (PV-19B)

**Development work (`0.4.0.dev0`) — not part of the released v0.3.0.**

The Guided Pull Laboratory exposes the *full* component registry while running only the *compatible*
subset as **independent model lenses**. It never sums or averages competing mechanisms, never presents
model agreement as validation, and is **not** a digital twin.

```bash
python -m puckworks.product.lab matrix   --format md      # all-component coverage matrix
python -m puckworks.product.lab compare  --format md      # common-scenario comparison + reference suite
python -m puckworks.product.lab compare  --format json    # deterministic machine report (schema v2)
```

## Two modes

1. **Common-scenario model lenses.** One bounded espresso scenario (the `pv19_named` fixed reference
   recipe) is mapped into the *compatible* models. Each model runs independently through its existing
   authoritative producer. Today `cameron2020.extraction_bdf` is the single executed common-scenario
   lens (via `puckworks.product.simulate_pull` — no equation is re-implemented). Results are overlaid
   only when observable definition, units, reference volume, and axis are compatible.
2. **Component reference suite.** Executable components' native reference cases demonstrate that the
   registry works. Each is labelled *"the component's own native reference case, not the common Guided
   Pull scenario."* A future integrated chain may pick one compatible component per physical stage;
   competing models remain branches.

## Coverage vocabulary

Every registered component (enumerated from `puckworks.components()`, never a hard-coded count) gets
exactly one disposition: `COMMON_SCENARIO_READY`, `COMMON_SCENARIO_WITH_VERIFIED_ADAPTER`,
`NATIVE_REFERENCE_ONLY`, `SUPPORTING_STAGE_LENS`, `CALIBRATION_OR_CLOSURE`, `ADAPTER_REQUIRED`,
`OUTSIDE_SCENARIO_DOMAIN`, `RIGHTS_BLOCKED`, `NOT_EXECUTABLE`, `SKIPPED_OPTIONAL_DEPENDENCY`, or `FAILED`
(reserved for an execution that errored — never for an unsupported component).

## Honesty boundaries (enforced by tests)

- No summing/averaging of competing mechanisms; no ensemble without a defensible statistical model.
- Competing extraction models (`grudeva2025.reduced`, `pannusch2024.solver`,
  `romancorrochano2017.extraction`, `mo2023_2.coupled_bed`) are `ADAPTER_REQUIRED`: their concentration
  reference volumes / observables differ (e.g. Cameron bed-volume vs Grudeva grain-volume), so they are
  **not** overlaid until an inventory-conserving conversion is tested.
- No grinder dial is treated as a universal particle size; no dial→size conversion is applied.
- Evidence labels ride through from the producer unchanged; no comparison result upgrades evidence.
- Optional accelerator/GPU components (`brewer2026.lb_taichi`) are `SKIPPED_OPTIONAL_DEPENDENCY` and
  never enter the base install; a skip is never counted as a pass.
- Serialization is deterministic (schema v2, distinct from `PullRun` v1) with no wall-clock in the
  canonical content.

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
