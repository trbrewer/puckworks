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
>
> **Corrected 2026-08-05 after exact-head review — disposition UNCHANGED (NEEDS_NEW_DATA), one
> decisive blocker instead of two.** The absence of a temperature *argument* is not an
> independent blocker: Cameron carries a fixed ~90 °C water-property basis. The grind basis alone
> is decisive. The protocol's original record is preserved, with a dated erratum appended.

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

Constructing the matched scenario requires an invented parameter: a **cross-grinder microstructure
mapping**. That is **one decisive blocker**, and it is sufficient on its own.

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

## The decisive blocker — the grind dial spaces are different and non-portable

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

### The Pannusch metadata conflict is INTERNAL — recorded, not resolved

Not a card-versus-registry error. **`docs/cards/pannusch2024.md` itself** carries both statements:
that the validation campaign is the **Schmieder-2023 apparatus** — whose card names a **Mahlkönig
E65S** — *and* that the fitted range is an **"EK43-type grind 1.4–2.0"**. The card is internally
inconsistent about the grinder family; the registry merely repeats one side of it.

The screen records the conflict and **does not resolve it**. Picking a winner would be inventing
the very cross-grinder mapping the screen is blocked on, and a screen may not edit a source card
or a registry field. The blocker holds under **either** reading: if the campaign is E65S, no
mapping to Cameron's EK43 microstructure exists; if the fitted range really is EK43-type, that
claim is unsupported by the campaign the card itself names, so the grind basis is still
unestablished.

## Temperature is a caveat, NOT a blocker

`cameron2020.extraction_bdf.simulate_shot` accepts exactly:

```
gs, p_bar, m_in, m_out, N, M, q, t_shot, n_save, rtol, atol, c_s0
```

There is no temperature argument. **An earlier version of this screen read that as a second,
independently sufficient blocker. That was withdrawn on review**: a missing *argument* is not
evidence of a different *intervention*. Cameron is not temperature-free — it carries a fixed
water-property basis documented in its own source:

```python
MU = 3.15e-4          # viscosity of water at ~90 C, Pa s
```

~90 °C lies **inside** Pannusch's declared 80–98 °C window and within about 2 °C of this
scenario's measured 88.26 °C. A fixed or implicit basis is a *narrow* validity range, not an
incompatible one.

What remains is a **non-blocking metadata caveat**: the temperature provenance of Cameron's fitted
kinetic parameters is not documented per-temperature, so a comparison run at 88.26 °C would carry
an unquantified basis mismatch. That affects how a comparison is *interpreted*, not whether it can
be *constructed*.

The decisive blocker is checked **programmatically** — signatures, card text and the manifest —
rather than asserted in prose, and so is the temperature basis.

## Comparability classification

Using the RP-A concepts as vocabulary only; no RP-A machinery is implemented.

| axis | level | rationale |
|---|---|---|
| **intervention** (primary) | **(5) non-comparable** | no matched scenario can be constructed: no grind adapter between the two dial spaces. Temperature is **NOT** part of this classification — Cameron's fixed ~90 °C basis sits inside Pannusch's declared window |
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
exactly where the one that blocks it fails; temperature is drawn as a non-blocking caveat. **B**: the shared observable and its six measured
replicates — **no model prediction is drawn, because none was computed**. **C**: the named missing
evidence.

The figure deliberately does not place any native model quantity on a common axis, because they
are not comparable at the intervention.

Bundle-local screen evidence. **Not** registered in `puckworks/viz/registry.py` or the generated
gallery.

## What would unblock this screen

**One item.** A grind calibration linking the two dial spaces — a measured PSD (or equivalent
microstructure) for Schmieder's Mahlkönig E65S at GL 1.4/1.7/2.0, on the same basis as the
existing `cameron2020/psd_figure2` (Cameron's measured EK43 PSD at four dial settings).
Equivalently for Angeloni's Mythos O/C/F. This is the explicit refit adapter rule 9 requires.

**It is sufficient on its own.** With that calibration in hand the matched scenario becomes
constructible and the screen can be executed; the temperature caveat would then be recorded
alongside the result rather than preventing it.

## Scope — what this screen did NOT do

- **No model execution.** A test asserts neither solver is invoked.
- No refit, no new physics, no new pressure→flow model.
- No sweep, adapter registry, comparability schema or response atlas. No RP-A machinery.
- No use of `cameron2020.paper_mode`.
- No evidence label, badge, validation rung or model verdict changed. The `EK43-type` /
  E65S conflict inside `docs/cards/pannusch2024.md` is recorded, not corrected — neither the
  card nor the registry entry is touched.
