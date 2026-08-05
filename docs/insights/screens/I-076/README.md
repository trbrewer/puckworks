# I-076 — single matched-scenario model disagreement

```
CHEAP_SCIENTIFIC_SCREEN
NOT_A_PUBLICATION_RESULT
NOT_A_MODEL_VALIDATION_UPGRADE
```

> **The protocol was frozen and committed BEFORE this screen ran** —
> [`PROTOCOL.md`](PROTOCOL.md), commit `45f64dd`, which precedes every result-producing commit
> for I-076 in the history. **No model was executed**: the determination is reached at scenario
> construction, upstream of running anything.

## What was run

**Question** (generated, verbatim from the candidate):

> Under one matched scenario, do pannusch2024.solver and cameron2020.extraction_bdf differ in
> sign, ordering, or magnitude on an observable they both produce?

`cameron2020.paper_mode` remains **quarantined** and is never invoked.

## How to re-run

```
python -m puckworks.analysis.screen_i076_matched_models
```

Writes `result.json` and `figures/primary.png`. ~5 s — it solves nothing.

Focused test: `pytest tests/test_screen_i076.py -v`

## Result — **NEEDS_NEW_DATA**

Constructing the matched scenario requires an invented parameter. **Two independent blockers,
each sufficient on its own.**

The striking part is how much *did* line up. The scenario was found, and it is a good one.

## The scenario that was sought and found

**`schmieder2023/cup_masses`, experiment 7 — the source's own DoE Central Point.**

Selected because the source declares it the centre of its design, **not** by inspecting model
output and **not** by taking the midpoint of a range: no model had been run when it was chosen,
and none has been run since.

| | |
|---|---|
| grind level (source dial) | 1.7 |
| measured flow (`scale_flow_ml_s`) | **1.9011 mL s⁻¹** mean over 6 reps (1.850–1.986) |
| measured temperature (`decent_temp_C`) | **88.26 °C** mean (target 89) |
| dose | **20.00 g** (nominal, fixed — `docs/cards/schmieder2023.md`) |
| brew ratio → beverage | 1/2 → **40 g** |
| observable | whole-cup TDS, **9.691 %** mass of beverage |
| replicates | **6**, replicate RSD **0.82 %** (campaign mean 2.5 %, max 8.5 %) |

Everything the authorization asks for is here: an interior source-supported condition, a
**measured** flow as the common intervention, a matched beverage-mass endpoint, a shared
observable, and a real measured-replicate uncertainty. The **observable was never the obstacle.**

The Angeloni route was pursued first and rejected: `angeloni2023` records pressure, temperature
and granulometry but **no measured flow**, and it hits the same grind blocker in a worse form.

## Blocker A — the grind dial spaces are different and non-portable

| component | declared grind input | actual grinder |
|---|---|---|
| `pannusch2024.solver` | registry: "EK43-type grind 1.4–2.0" | **Mahlkönig E65S** — its card places the work on Schmieder's apparatus, and `docs/cards/schmieder2023.md` names the grinder: *"20 g dose, DE1 Pro + IMS basket/screen, Acqua Panna water, Mahlkönig E65S"*, *"GL 1.4–2.0 (only ~7.5 % of the E65S scale)"* |
| `cameron2020.extraction_bdf` | registry: "EK43 dial 1.1–2.3" | **EK43** — *"grind enters via measured microstructure and Darcy-flux tables (EK43 dial 1.1-2.3)"* |

Two grinders, two dial spaces, **no declared adapter**. CLAUDE.md rule 9 / ledger A9, G5 forbids
mapping one grinder's dial onto another's without an explicit refit adapter.

**The numerical coincidence is a trap.** Schmieder GL **1.7** and Cameron dial **1.7** are the
same number and physically unrelated settings. Running Cameron at `gs = 1.7` "because Schmieder
used 1.7" would be the forbidden mapping wearing a disguise — and it is exactly the mistake a
hurried screen would make.

The repository already demonstrates how unsafe the mapping is. Two existing code paths assign
**different, mutually inconsistent** dial values to *one* physical Angeloni grind:

| where | granulometry O → | declared as |
|---|---|---|
| `angeloni_bracket._GRIND_MAP` | **1.9** (for Cameron) | "approximate, **UNCALIBRATED** cross-grinder map" |
| `gate_pannusch_angeloni_per_condition` / `GRIND_17` | **1.7** (for Pannusch) | granulometry O ≈ pannusch centre grind |

Grind is **load-bearing physics** for Cameron, not a flux prefactor: it sets the measured
microstructure via `grind_microstructure(gs) → phi1, phi2, a2, bet1, bet2`. Supplying `q`
explicitly removes the flux dependence but **not** the microstructure dependence.

**Recorded, not corrected:** the registry's `EK43-type` wording on the Pannusch side is not
supported by that component's own card. A screen may not edit a registry field, so it is filed as
a discrepancy for a human.

## Blocker B — Cameron has no temperature input

`cameron2020.extraction_bdf.simulate_shot` accepts exactly:

```
gs, p_bar, m_in, m_out, N, M, q, t_shot, n_save, rtol, atol, c_s0
```

**No temperature parameter** — the component is isothermal. `pannusch2024.solver` is declared over
**T 80–98 °C** and its closures (van 't Hoff `K(T)`, Wilke–Chang `D(T)`) are temperature-dependent
by construction.

So the two cannot receive the *same intervention* on an axis only one of them has. Fixing Pannusch
at the measured 88.26 °C while Cameron receives nothing is two experiments printed side by side,
not a matched scenario.

Both blockers are checked **programmatically** — signatures and card text — rather than asserted
in prose.

## Comparability classification

Using the RP-A concepts as vocabulary only; no RP-A machinery is implemented.

| axis | level | rationale |
|---|---|---|
| **intervention** (primary) | **(5) non-comparable** | no matched scenario can be constructed: no grind adapter, and a temperature axis for only one component |
| observable | (2) comparable through an existing declared adapter | whole-cup TDS mass % at a matched 40 g endpoint, after Pannusch's own declared mg mL⁻¹ ↔ mass % convention |
| inventory | (4) same label, different basis | per-solute pseudo-molecule vs per-bed-volume pool with a 29.6 % EY ceiling |

## Uncertainty authorities — enumerated, never pooled

| authority | value | applies to |
|---|---|---|
| measured replicate | 0.82 % RSD at this scenario; campaign mean 2.5 %, max 8.5 % | the measured observable |
| fitted-source residual | Pannusch reproduced fit MAPE, TDS 6.7 % | Pannusch vs **its own fit target** — **never** Cameron's predictive uncertainty |
| numerical convergence | Cameron ≈ 0.15 pt default-grid bias; Pannusch grid/tolerance | discretisation only — **never** experimental or model-form |
| parameter | not quantified | — |
| model-form | not quantified | — |

Not combined into one threshold. A SURVIVE on magnitude would need a commensurate, source-grounded
authority spanning both components; none exists.

## Inventory bases — kept native

Pannusch: per-solute `c_s0` (Table 2), TDS as a caffeine-like pseudo-molecule, mg mL⁻¹.
Cameron: per-bed-volume `c_s0 = 118/φ_s`, EY ceiling 29.6 %, `c_sat` 212.4 kg m⁻³.

No rescaling, no forced equality, no refit, no new physics.

## Figure

`figures/primary.png` — **A**: every scenario axis, showing which ones reach both components and
exactly where the two that block it fail. **B**: the shared observable and its six measured
replicates — **no model prediction is drawn, because none was computed**. **C**: the named missing
evidence.

The figure deliberately does not place any native model quantity on a common axis, because they
are not comparable at the intervention.

Bundle-local screen evidence. **Not** registered in `puckworks/viz/registry.py` or the generated
gallery.

## What would unblock this screen

1. **A grind calibration linking the two dial spaces** — a measured PSD (or equivalent
   microstructure) for Schmieder's Mahlkönig E65S at GL 1.4/1.7/2.0, on the same basis as the
   existing `cameron2020/psd_figure2` (Cameron's measured EK43 PSD at four dial settings).
   Equivalently for Angeloni's Mythos O/C/F. This is the explicit refit adapter rule 9 requires.
2. **A temperature basis for `cameron2020.extraction_bdf`** — either a declared temperature
   closure, or a source-backed statement of the temperature its fixed parameters correspond to.

**Neither alone is sufficient. Both are required.**

## Scope — what this screen did NOT do

- **No model execution.** A test asserts neither solver is invoked.
- No refit, no new physics, no new pressure→flow model.
- No sweep, adapter registry, comparability schema or response atlas. No RP-A machinery.
- No use of `cameron2020.paper_mode`.
- No evidence label, badge, validation rung or model verdict changed. The registry `EK43-type`
  discrepancy is recorded, not corrected.
