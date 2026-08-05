# I-076 — matched-scenario protocol (FROZEN BEFORE EXECUTION)

```
CHEAP_SCIENTIFIC_SCREEN
NOT_A_PUBLICATION_RESULT
NOT_A_MODEL_VALIDATION_UPGRADE
```

**This document is committed before any model execution**, and it is what the screen is bound
to. It freezes the sixteen items the authorization requires. Where an item **cannot** be frozen
from existing sources without inventing a value, it says so and names the exact missing evidence
— which is itself a protocol outcome, not a failure to write one.

Candidates under comparison:

```
pannusch2024.solver
cameron2020.extraction_bdf          (cameron2020.paper_mode remains QUARANTINED and is not invoked)
```

---

## Determination reached at protocol time

**No admissible matched scenario exists in the repository.** Two independent blockers, each
sufficient on its own, and neither removable without inventing a parameter:

1. **The two components' grind inputs live in different, non-portable dial spaces.**
2. **`cameron2020.extraction_bdf` has no temperature input at all**, while `pannusch2024.solver`
   is declared over a temperature range and its closures are temperature-dependent by
   construction.

The protocol therefore freezes the *attempted* scenario in full — so the attempt is auditable and
so a future session with the missing evidence can execute it unchanged — and records the screen's
disposition as **NEEDS_NEW_DATA**. No model is executed.

---

## 1. The exact scenario that was sought, and the best candidate found

The authorization prefers an interior Angeloni condition, or another source-supported scenario.
Both were pursued. The **strongest** candidate found anywhere in the repository is:

> **`schmieder2023/cup_masses`, experiment 7 — the source's own DoE Central Point.**
> Grind level 1.7, target flow 2.0 mL s⁻¹, target temperature 89 °C, brew ratio 1/2,
> **six replicates** of the TDS observable.

It was selected because it is the **source's declared centre point**, not because of anything
about model output — no model had been run when it was chosen, and no range midpoint was
inspected and then adopted.

Measured values, verbatim from the loader:

| rep | `scale_flow_ml_s` | `decent_temp_C` | `pressure_max_bar` | TDS mass in cup (g) | `conc_in_cup` |
|---|---|---|---|---|---|
| 1 | 1.986 | 87.86 | 3.25 | 3.8961 | 0.0974 |
| 2 | 1.850 | 87.60 | 3.20 | 3.8877 | 0.0972 |
| 3 | 1.885 | 88.22 | 3.05 | 3.9125 | 0.0978 |
| 4 | 1.914 | 88.48 | 3.27 | 3.8568 | 0.0964 |
| 5 | 1.909 | 88.63 | 4.48 | 3.8807 | 0.0970 |
| 6 | 1.862 | 88.75 | 3.20 | 3.8234 | 0.0956 |

Dose is **20.00 g, nominal and fixed** (`docs/cards/schmieder2023.md`, Parameters); brew ratio
1/2 ⟹ beverage **40 g**.

The Angeloni route was considered first and rejected earlier: `angeloni2023` records pressure,
temperature and granulometry but **no measured flow**, so using it would require the existing
pressure→flow map — and, more decisively, it hits the same grind blocker (below) in a worse form.

## 2. Why the point does *not* lie inside the declared range of both components

This is the item that fails, and it fails twice.

### Blocker A — the grind dial spaces are different and non-portable

| component | declared grind input | grinder |
|---|---|---|
| `pannusch2024.solver` | "EK43-type grind 1.4–2.0; centre-grind (1.7)" *(registry)* | **Mahlkönig E65S** — `docs/cards/schmieder2023.md`: "20 g dose, DE1 Pro + IMS basket/screen, Acqua Panna water, **Mahlkönig E65S**"; "GL 1.4–2.0 (only ~7.5 % of the E65S scale)" |
| `cameron2020.extraction_bdf` | "EK43 dial 1.1–2.3" | **EK43** — grind enters "via measured microstructure and Darcy-flux tables (EK43 dial 1.1–2.3)" |

The registry's `EK43-type` wording on the pannusch side is not supported by its own card, which
places the campaign on an **E65S**. The two dial numbers therefore denote settings on **two
different grinders**.

**The numerical coincidence is a trap.** Schmieder GL **1.7** and Cameron dial **1.7** are the
same number and physically unrelated settings. Running Cameron at `gs = 1.7` "because Schmieder
used 1.7" would be the forbidden mapping wearing a disguise.

CLAUDE.md rule 9 / ledger A9, G5: *dial spaces are grinder-specific and non-portable; never map
one grinder's dial to another's without an explicit refit adapter.* **No such adapter exists**
between E65S and EK43, and none exists between Angeloni's Mythos granulometry (O/C/F) and EK43.

The repository already contains evidence of how unsafe the mapping is: the two existing
Mythos→dial assignments **disagree for the same physical grind** — `gate_pannusch_angeloni_
per_condition` treats granulometry O as ≈ pannusch's centre grind 1.7, while
`angeloni_bracket._GRIND_MAP` (declared "approximate, **UNCALIBRATED**") sends O → 1.9 for
Cameron. One physical grind, two incompatible uncalibrated dial values.

This blocker is not cosmetic for Cameron: grind sets the **measured microstructure** (`phi1`,
`phi2`, `a2`, `bet1`, `bet2` via `grind_microstructure(gs)`), so it is load-bearing physics, not
merely a flux prefactor. Supplying `q` explicitly removes the flux dependence but **not** the
microstructure dependence.

### Blocker B — Cameron has no temperature input

`cameron2020.extraction_bdf.simulate_shot` accepts exactly:

```
gs, p_bar, m_in, m_out, N, M, q, t_shot, n_save, rtol, atol, c_s0
```

There is **no temperature parameter**; the component is isothermal. `pannusch2024.solver` is
declared over **T 80–98 °C** and its closures — van 't Hoff `K(T)`, Wilke–Chang `D(T)` — are
temperature-dependent by construction.

So the two components cannot be given the *same intervention*: one has a temperature axis and the
other has none. Fixing Pannusch at 88.6 °C while Cameron receives nothing is not a matched
scenario; it is two different experiments reported side by side.

## 3. The intervention that would have been supplied to each model

Frozen for a future session, with the conversion each component's interface requires:

| | `pannusch2024.solver` | `cameron2020.extraction_bdf` |
|---|---|---|
| flow | `flow_mL_s` argument, consumed as a **mass** flow in **g s⁻¹** (`angeloni_bracket._SOURCE_FLOW_UNITS`; internally `q = flow/1000/ρ/A_cs` with ρ = 980 kg m⁻³) | `q`, a **superficial Darcy flux in m s⁻¹**: `q = Q_vol / (π R0²)`, `R0 = 29.2 mm` |
| temperature | `T_C` | **none — no such input** |
| grind | `GRIND_17 = {psi: 0.23, d_s2: 330 µm}` (Table 2 centre grind) | `gs` dial → `grind_microstructure(gs)` |

The common intervention would have been the **measured** `scale_flow_ml_s`, mean **1.901 mL s⁻¹**
over the six replicates — satisfying the authorization's preference for measured flow. Each side
needs a different declared conversion of it, and each conversion carries its own density.

## 4. Pressure-node convention

Schmieder's `pressure_max_bar` is a **per-shot maximum**, not a steady node value
(`schmieder2023_AUDIT.md` D2: "Read as per-shot maxima. **Do not use as a Darcy ΔP(Q) point.**").
Both components would have been driven by **flow**, not pressure, so no pressure node is on the
critical path — but recorded because Cameron's `p_bar` defaults to 5 bar and must be bypassed by
supplying `q` explicitly, not left at its default.

## 5. Flow convention and units

Measured volumetric flow, mL s⁻¹, from a scale-derived rate. Pannusch consumes its flow argument
as g s⁻¹; Cameron consumes a superficial velocity in m s⁻¹. Both conversions require a beverage
density and **the two components use different ones** (Pannusch ρ = 980 kg m⁻³ internally;
Cameron `RHO_OUT` = 997 kg m⁻³). Recorded, not merged.

## 6. Temperature basis

Measured `decent_temp_C`, mean **88.26 °C** over the six replicates (target 89 °C). **Applicable
to Pannusch only** — see Blocker B.

## 7. Grind convention

Schmieder GL 1.7 on a **Mahlkönig E65S**. **Not translatable** to Cameron's EK43 dial. See
Blocker A.

## 8. Dose and geometry basis

Dose 20.00 g (nominal, fixed). Cameron basket radius `R0` = 29.2 mm; Pannusch bed diameter
58 mm, bed height 15 mm, porosity 0.17. The geometries are close but not identical and are kept
native, not reconciled.

## 9. Stopping rule

Terminate at a **matched collected beverage mass of 40 g** (brew ratio 1/2 at a 20.00 g dose).
Cameron reaches it through its own Eq. 26, `t_shot = m_out / (π R0² ρ_out q)`; Pannusch through
`t_end = m_target / flow` on its g s⁻¹ convention. Both are declared rules of their own
components; neither is invented here.

## 10. Endpoint

**Beverage mass**, 40 g. Not a time endpoint and not a volume endpoint.

## 11. The shared observable and its units

**Whole-cup total dissolved solids as a mass percentage of the beverage**, cumulative, at the
40 g endpoint.

- Cameron reports it natively: `ShotResult.tds = 100 · M_cup / m_out` — a true mass ratio.
- Pannusch reports a fraction-averaged outlet concentration in **mg mL⁻¹**; its own port converts
  measured `TDS_pct` by a factor of 10 (`solver._MEAS`), i.e. it assumes a beverage density of
  1000 kg m⁻³ to move between mass % and mg mL⁻¹.
- Schmieder's `conc_in_cup` for TDS is a **mass fraction** (≈ 0.097 ⟹ 9.7 % TDS), gravimetrically
  anchored per DIN 10775 on a **centrifuged supernatant with fines excluded**
  (`schmieder2023_AUDIT.md` D8 — a declared normalization hazard for any cross-source TDS
  comparison).

## 12. Each model's inventory basis — kept native, never equalized

| | inventory convention |
|---|---|
| Pannusch | **per-solute** `c_s0` (Table 2), with TDS modelled as a *caffeine-like pseudo-molecule* |
| Cameron | **per-bed-volume** soluble inventory `c_s0 = 118/φ_s`, EY ceiling **29.6 %**, `c_sat` 212.4 kg m⁻³ |

No rescaling, no refit, no forced equality. Per the authorization: a difference caused solely by
incompatible inventory bases is a **semantic/convention** difference, not a kinetic disagreement.

## 13. Declared adapters

**None exists** for the grind axis (E65S ↔ EK43, or Mythos ↔ EK43) and **none exists** for the
temperature axis (Cameron has no temperature). The only adapter in play would have been
Pannusch's own declared mass %↔mg mL⁻¹ TDS convention, which is a unit conversion within one
component, not a bridge between the two.

## 14. Uncertainty authorities — kept separate, never pooled

| authority | value | applies to |
|---|---|---|
| **measured replicate** | Schmieder TDS, 6 reps at exp 7; campaign mean RSD **2.5 %**, max 8.5 % (`schmieder2023/cup_masses` manifest caveat) | the measured observable |
| **fitted-source residual** | Pannusch's reproduced fit MAPEs (TDS 6.7 %) | Pannusch's agreement with **its own fit target** — *not* Cameron's predictive uncertainty |
| **numerical convergence** | Cameron ≈ 0.15 pt default-grid bias (paper SI); Pannusch grid/tolerance | discretisation only |
| **parameter** | not quantified in either card for this scenario | — |
| **model-form** | not quantified | — |

These are **not** combined into a pooled threshold, and one component's fit residual is never used
as the other's predictive uncertainty.

## 15. Decision rule (frozen, applied without revision)

- **SURVIVE** — a directly comparable or existing-adapter comparison shows a difference beyond the
  applicable declared uncertainty at the frozen interior scenario, and the difference is *not*
  explained by unit, endpoint, pressure-node, inventory or stopping-rule convention.
- **RETIRE** — results overlap within applicable uncertainty; **or** the declared validity ranges
  provide no common admissible scenario; **or** the apparent disagreement is fully explained by a
  documented convention or basis difference.
- **NEEDS_NEW_DATA** — constructing the matched scenario requires an invented parameter; **or**
  the outputs appear different but no defensible common uncertainty authority exists; **or**
  source metadata cannot establish a common observable and endpoint.

Note the RETIRE arm's second clause and the NEEDS_NEW_DATA arm's first clause both look at
scenario construction. They are distinguished as follows, and this distinction is frozen here:

> If the declared ranges simply **do not intersect** on a shared axis, that is RETIRE — the
> components answer questions in different regions and no data would change it. If a common
> scenario **could** exist but stating it requires **inventing a value the sources do not
> supply**, that is NEEDS_NEW_DATA — naming the measurement that would supply it.

Blocker A is the second kind: an E65S↔EK43 grind calibration is a measurable thing that simply
has not been measured. Blocker B is closer to the first, but it is a *missing model input* rather
than a disjoint range, and it too would be resolved by evidence (a Cameron temperature closure or
a declared isothermal-equivalence adapter) rather than by re-reading the cards.

## 16. Comparability classification (frozen from the cards, before execution)

Using the RP-A concepts, without implementing any RP-A machinery:

**Primary: (5) non-comparable** — at the level of the *intervention*. A matched scenario cannot be
constructed: the grind axis has no declared adapter between the two dial spaces, and the
temperature axis exists for only one of the two components.

**Secondary, recorded for completeness:**

- on the **observable** axis alone, the two would be **(2) comparable through an existing declared
  adapter** — whole-cup TDS mass % at a matched 40 g beverage endpoint, after Pannusch's own
  declared mg mL⁻¹↔mass % convention;
- on the **inventory** axis, they are **(4) same label, different basis** — "soluble inventory"
  names a per-solute pseudo-molecule quantity in one component and a per-bed-volume pool with a
  29.6 % EY ceiling in the other.

So the observable was never the obstacle. The **intervention** is.

---

## What would unblock this screen

Named precisely, because "more data" is not a request:

1. **A grind calibration linking the two dial spaces** — a measured PSD (or equivalent
   microstructure) for Schmieder's Mahlkönig E65S at GL 1.4/1.7/2.0, on the same basis as
   `cameron2020/psd_figure2` (Cameron's measured EK43 PSD at four dial settings). That is the
   explicit refit adapter rule 9 requires. Equivalently for Angeloni's Mythos O/C/F.
2. **A temperature basis for Cameron** — either a declared temperature closure, or a source-backed
   statement of which temperature its fixed parameters correspond to, so a Pannusch run can be
   placed at that temperature rather than at one Cameron cannot represent.

Item 1 alone does not unblock the screen; both are required. Item 2 alone does not either.

## What this protocol does NOT authorize

No refit of either component. No new physics. No new pressure→flow model. No generalized sweep,
adapter registry, comparability schema or response atlas. No use of `cameron2020.paper_mode`. No
execution of either model under this screen, since the determination above is reached before
execution.

## Source commit

- Branch base: `14c3753c6e8dab2995332dbe1c3d1e04c4348051`
- Branch: `insights/if6b-wave2-cheap-screens`
