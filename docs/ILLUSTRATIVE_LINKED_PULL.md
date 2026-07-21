# The Espresso Model Relay (`illustrative_linked_pull_v1`)

*An illustrative, assumption-rich linked pull across separate models. **This is not a validated coupled
simulation.***

## Purpose

One hypothetical espresso pull, passed from model to model. At each station the relay shows what the model
calculates, what is handed forward, what had to be assumed, and what the result might mean for the liquid
that reaches the cup. The goal is **not** to pretend Puckworks has a validated whole-shot mega-model; it is
to show, as honestly and concretely as possible, how model outputs *could* be handed from one component to
another in an illustrative computational relay — with every assumption explicit, named, visible, attached
to the precise hand-off, serialized, and never confused with validation inherited from an individual
component.

## Why it exists separately from the Full Laboratory Tour

The **Full Laboratory Tour** (`full_laboratory_tour_v1`) visits every model *independently* — each answers
its own question on its own terms, and results are never averaged or ranked. That product is unchanged: the
relay does not modify its manifest, routes, ordering, hashes, rights, figures, or notebook, and a
regression test pins its scientific hash (`tests/test_linked_pull_tour_regression.py`).

The **Espresso Model Relay** does the opposite thing on purpose: it *links* selected outputs across models
to demonstrate platform capability. Because that linking requires cross-rig transfers and assumed bridges,
it is a distinct, clearly-labelled experience — not a replacement for the tour.

## Positioning (public wording)

Use "model relay", "illustrative linked pull", "assumption-rich chain". Never "digital twin", "validated
coupled model", "universal simulator", "recipe optimizer", "mechanism oracle", "taste predictor", or "a
prediction of your exact puck". The permanent warning is displayed near the top of the notebook and again
at the end (`linked_pull_display.PERMANENT_WARNING`).

## Architecture (product orchestration, not a new component)

The complete relay is **not** registered in `puckworks.registry`. It is a product-level orchestration
artifact:

| module | role |
|---|---|
| `puckworks/product/linked_pull_records.py` | typed records + finite enums (`LinkKind`, `ValueOrigin`, `ScenarioRelationship`, `StageStatus`), `LinkedValue`, `LinkRecord`, `AssumptionRecord`, `StageResult`, deterministic hashing |
| `puckworks/product/linked_pull_manifest.py` | the frozen link graph — every registered component classified exactly once, the station list, the edges; `verify_linked_pull_manifest()` |
| `puckworks/product/linked_pull_adapters.py` | documented adapters + the A01–A12 assumption ledger (unit/basis-checked, never clamped) |
| `puckworks/product/linked_pull.py` | the acyclic, one-way engine + CLI (`python -m puckworks.product.linked_pull`) |
| `puckworks/product/linked_pull_narrative.py` | structured novice narrative built from computed results |
| `puckworks/product/linked_pull_display.py` | Markdown report + notebook blocks + chain map (from the serialized links) |
| `puckworks/product/linked_pull_figures.py` | figures REUSING the existing evidence-bound VizSpecs + tour draws |

## Reference pull

```
dose_g = 20.0 · target_beverage_g = 40.0 · grind_setting (EK43) = 1.7 · target_pressure_bar = 9.0
brew_temperature_c = 93.0 · heterogeneity = moderate · mode = fast · seed = 42
```

Reproduce:

```bash
python -m puckworks.product.linked_pull --preset illustrative_reference_v1 --mode fast --format json \
  --output relay.json
```

The `model_output_hash` (model outputs + link topology) and `artifact_hash` (whole record, timestamps
excluded) are deterministic — run it twice and compare. **Neither is a validation or scientific-certainty
hash.**

## Link kinds

`DIRECT_MODEL_OUTPUT` (solid) · `DOCUMENTED_ADAPTER` (dashed) · `ILLUSTRATIVE_ASSUMPTION` (dotted) ·
`SHARED_INPUT_ONLY` / `DIAGNOSTIC_ONLY` (thin grey) · `ALTERNATIVE_BRANCH` (branch) ·
`REFERENCE_CONSTRAINT` · `OPTIONAL_SLOW_PATH` (extended mode) · `RIGHTS_BLOCKED` (no execution).

## Assumption ledger (A01–A12)

A01 cross-grinder size match · A02 distinct porosity definitions · A03 synthetic geometry · A04
pressure-node assignment · A05 cross-rig transfer · A06 dynamic-profile → representative pressure · A07
liquor rheology closure · A08 inertial closure extrapolation · A09 Cameron→Waszkiewicz one-way coupling ·
A10 two distinct sigma origins · A11 flow reduction for the chemistry branch · A12 total→extractable
inventory. Each is a serialized `AssumptionRecord` with a `validation_needed` field.

## v1 component dispositions (all 25, exactly once)

The fast reference run **authoritatively executes 18 components with 10 serialized cross-component
hand-offs** (2 direct, 6 documented adapters, 2 illustrative assumptions) and 9 named assumptions. These
counts are derived from the audited reference result and frozen in
`tests/test_linked_pull_execution_accounting.py` so they cannot drift.

- **Authoritative executions (18):** `wadsworth2026.grindmap`, `wadsworth2026.permeability`,
  `brewer2026.pack_generator`, `foster2025.machine_mode`, `foster2025.infiltration`,
  `wadsworth2026.inertial`, `sourcing2026.g10_liquor_rheology`, `cameron2020.extraction_bdf`,
  `waszkiewicz2025.poroelastic`, `brewer2026.coupled_kappa_t`, `mo2023_2.swelling`,
  `fasano2000_partI.fines_migration`, `brewer2026.streamtube`, `pannusch2024.closures`,
  `romancorrochano2017.extraction`, `moroney2016.surrogate`, `mo2023_2.coupled_bed`,
  `liang2021.desorption`.
- **Not selected (3):** `pannusch2024.solver` (the registered multi-solute *solver* is NOT run — the
  release-clock diagnostic is derived from `pannusch2024.closures`; the solver needs an authoritative
  linked Q(t)/T/inventory adapter), `brewer2026.lb_reference` and `brewer2026.lb_taichi` (slow optional
  pore-scale path, run only in extended mode — *not* a missing dependency).
- **Reference-only (3):** `sourcing2026.g3_pump_characteristic`, `sourcing2026.g1_glassbead_analog`,
  `lee2023.feedback` (guarded — its headline decline needs an unphysical density).
- **Rights-blocked (#73):** `grudeva2025.reduced` — shown in the chain map, **zero** model and adapter
  calls, no inputs, no outputs, no edges.

In **extended** mode the pore-scale relay adds `brewer2026.lb_reference` (the reference LB solve, run
once). `brewer2026.lb_taichi` is counted only if the actual Taichi-backed backend runs; the reference solve
is never relabelled as Taichi (Taichi absent → optional-dependency-unavailable).

## Direct vs adapted vs assumed hand-offs

Direct (unit + basis unchanged): permeability → inertial; Cameron response → streamtube. Documented
adapters (unit/basis converted, formula recorded): grindmap → permeability / pack; permeability →
infiltration; machine nodes → infiltration / inertial; representative pressure → Cameron. Illustrative
assumptions (dotted): Cameron boulder radius → grindmap dial (A01); Cameron dissolved mass → Waszkiewicz
porosity response (A09); LB sigma → streamtube (A10, extended). (The machine-flow → Pannusch *solver*
hand-off is not a runtime link in v1: the solver is not-selected, so no hand-off is fabricated.)

## Fast vs extended mode

**Fast** (default, ~4 s after install on an ordinary CPU): all lightweight primary stages, synthetic pack,
machine, wetting, Darcy/inertial, Cameron baseline, Waszkiewicz one-way branch, streamtube
calibrated-closure branch, reduced multi-solute branch, alternative lenses, dashboard. **Extended** adds
the pore-scale relay (pack → LB velocity field → `sigma_micro` → LB-derived streamtube branch); the two
sigma origins are always displayed separately (A10). Taichi is optional; its absence never fails the fast
path.

## Rights behavior

Every producer call passes a centralized preflight (`rights.may_execute_locally` for `LOCAL_PRIVATE`;
public contexts additionally require batch + publish clearance and are fail-closed in v1).
`grudeva2025.reduced` receives zero calls. There is no public-hosted execution mode in v1.

## Output schema

`schema_version`, `contract_schema_version`, `manifest_id`, `source_commit`, `execution_context`, `mode`,
`request`, `stipulated_defaults`, `stages` (each with typed inputs/outputs, links, assumptions, domain
findings, narrative, content hash), `links`, `assumptions`, `counts`, `component_dispositions`,
`model_output_hash`, `artifact_hash`. Timestamps are excluded from the canonical hashes.

## Scientific limitations

The relay is illustrative and assumption-rich by design. Notable integration findings: matching Cameron's
coarse-family boulder radius to the Wadsworth **mean**-radius map (A01) overstates permeability, so the
naive Darcy velocity is unphysically high — the Forchheimer `Fo_F ≫ 1` correctly flags this. The
Cameron→Waszkiewicz branch (A09) is a **new** coupling with no inherited validation. The multi-solute
branch is a **reduced** representation (release-clock ordering from the pannusch closures, not absolute
per-solute cup yields, because per-solute extractable fractions are unmeasured — A12).

## Highest-value measurements to strengthen the weakest assumptions

1. A shared PSD measured on the same coffee/grinder, mapped to both Cameron's families and the Wadsworth
   size map (turns A01 from an assumed match into a calibrated adapter).
2. Simultaneous pump-outlet and basket pressure on the modelled machine (A04 pressure nodes).
3. A single rig producing permeability, geometry, and wetting on one coffee (A05 cross-rig transfer).
4. Independent dissolved-mass kinetics alongside a measured flow trace (A09 one-way coupling).
5. Per-solute extractable fractions for the coffee (A12), to move the chemistry branch from timing-only to
   absolute yields.
