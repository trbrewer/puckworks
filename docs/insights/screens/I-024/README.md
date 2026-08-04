# I-024 — multi-species common-state consistency

```
CHEAP_SCIENTIFIC_SCREEN
NOT_A_PUBLICATION_RESULT
NOT_A_MODEL_VALIDATION_UPGRADE
```

## What was run

**Question** (generated, verbatim from the candidate):

> Under one shared hydraulic and transport state, do the per-species residuals show structure
> that a single kinetic story cannot absorb?

## How to re-run

```
python -m puckworks.analysis.screen_i024_common_state
```

Writes `result.json` and `figures/primary.png`. ~3 min (15 rates × 18 conditions × 4 species
unit-level solves; the levels are fitted analytically, see below).

Focused test: `pytest tests/test_screen_i024.py -v`

## Evidence unit — the Angeloni campaign only

`angeloni2023` (bioactives + total_solids), granulometry O, on-grid, both varieties.
**18 conditions** (3 T × 3 p × 2 varieties) × **4 species** (caffeine, trigonelline, 5CQA,
total-solids proxy).

MANIFEST `validation_strength`, verbatim: `independent (different machine/coffee/basket than
pannusch fit or cameron calibration)`.

**Explicitly excluded from scoring**, as the authority requires. The generated candidate lists
these entities because the lens grouped them, not because they belong in this screen:

| excluded | why |
|---|---|
| `maille2024.phi_closure`, `maille2024.two_regime` | batch fits on a different campaign; scoring them would mix campaigns, which is the candidate's own INCONCLUSIVE confound |
| `ellero2019/fig4_caffeine_content` | digitised **simulation** output, not measurement — it cannot carry a residual |
| `khamitova2020/tamping` | different rig and design; reference strength only |
| `pannusch2024.solver` / `.closures` **as evidence** | used here as the **model**, never as evidence; its own fit target (Schmieder) is post-fit |
| `angeloni2023/lipids` | not a species the model produces; used only as an upper uncertainty sensitivity |

## The two models

Both carry **one hydraulic state** per condition — one flow map, one bed, one porosity, one
grind, one observation operator (matched 40 g endpoint). They differ only in transport freedom:

| | rate | inventory level |
|---|---|---|
| **SHARED** | one multiplier per **variety**, shared across all four species | one per (species, variety) |
| **INDEPENDENT** | one multiplier per **(species, variety)** | one per (species, variety) |

**The level is free in both.** That is the design decision that answers the candidate's
strongest alternative — *"the apparent species difference is a measurement-lineage difference
between the assays, not chemistry"*. An inventory error or an assay calibration error is a pure
multiplicative level per species. Free levels in both models make the comparison blind to that
by construction, so anything surviving is condition-dependent structure, not level.

**Why the level can be fitted without re-solving.** The solver's output is *exactly* linear in
`c_s0` — verified to ~1e-6, the solver's own tolerance: scaling `c_s0` by λ scales the liquid
state by λ and leaves the normalised solid state untouched. So one unit-level solve per
(rate, condition, species) suffices and the optimal level is a weighted-least-squares closed
form. That is what keeps this inside a cheap-screen budget.

## Predeclared before any fit

- **Held-out split.** Train on **p = 6 and 12 bar**; hold out **p = 9 bar**, at every
  temperature and in both varieties. 12 training / 6 held-out conditions. The *interior*
  pressure is held out, so this is interpolation rather than extrapolation — a fair test rather
  than a hard one — and 9 bar is the reference espresso condition.
- **Rate domain.** `geomspace(0.15, 6.5, 15)` — the same wide log-spaced domain as the archived
  identifiability work, so a boundary optimum is exposed rather than imposed.
- **The materiality criterion**, all three arms in units of retained measurement uncertainty
  (standardised residual `z = (pred − meas)/σ`):

  | arm | test | reads |
  |---|---|---|
  | **C1** exceeds noise | `Z_shared > 1.0` | shared state's RMS standardised held-out residual exceeds one σ |
  | **C2** species-specific | SD across species of per-species mean `z` > 1.0 | separates *a species problem* from *a shared model-form problem* |
  | **C3** reduced by per-species fits | `Z_independent ≤ 0.70 × Z_shared` | per-species transport freedom removes ≥30 % of the RMS held-out residual |

  **SURVIVE iff C1 ∧ C2 ∧ C3.**

## The uncertainty problem, and how it was handled instead of assumed

The campaign retains **per-condition replicate RSD for total solids and lipids only**. For
caffeine / trigonelline / CGA the source gives a *global* range and no per-cell value — MANIFEST
`angeloni2023/bioactives`: `%RSD 0.3-19.7 (in card, not per-cell)`, and
`angeloni2023/total_solids_lipids_rsd`: `caffeine/trigonelline/CGA solute-specific RSD NOT
recovered ... raw replicates still owed`.

Inventing a value would have made the verdict an artifact of that invention. Instead the
criterion is **evaluated at both ends of the source's own stated band** (0.3 % and 19.7 %), with
`tds` always using its measured per-condition RSD, and the decision is taken **only if it is
invariant**. If it were not invariant, that would itself be the `NEEDS_NEW_DATA` finding, with
the required measurement named.

Note the structural property that makes this work: **C3 is a ratio, and therefore scale-free in
the assumed RSD.** A C3 failure retires the candidate at every point in the band, regardless of
what the missing solute-specific RSD turns out to be.

## Result

| | RSD 0.3 % (low end) | RSD 19.7 % (high end) |
|---|---|---|
| `Z_shared` | 22.15 | 1.38 |
| `Z_independent` | 22.34 | 1.38 |
| **ratio** (C3 reads this) | **1.009** | **1.001** |
| between-species spread | 3.90 | 0.60 |
| C1 exceeds noise | ✔ | ✔ |
| C2 species-specific | ✔ | ✘ |
| **C3 reduced by per-species fits** | **✘** | **✘** |
| survive | no | no |

**Decision invariant across the band → decide. RETIRE.**

Per-species freedom buys **nothing** held-out — the ratio is ≥1 at both ends, i.e. the
independent fits are very slightly *worse* out of sample. The per-species RMS values show the
same thing species by species (`result.json → band.*.evaluation.per_species_rms_z_*`).

### Inventory / assay check (step 6)

Fixing the level at pannusch's Table 2 inventory gives `Z = 92.9`; fitting a per-species level
gives `Z = 22.1`. **A per-species level absorbs 76.1 % of the raw residual.** The bulk of the
apparent species difference is inventory or assay scaling, exactly as the candidate's strongest
alternative predicted — and both scored models already carry a free level, so the decision is
blind to it.

The fitted levels track the campaign's own measured inventory rather than pannusch's. Robusta
caffeine: fitted **21.26**, angeloni Table 7 measured **18.58**, pannusch Table 2 **10.80** g/L.
That is independent evidence that the fitted level is standing in for real inventory.

*Caveat carried, not resolved:* angeloni Table 7 measures **total CQA**, not 5CQA, so the 5CQA
inventory comparison is not species-matched; and there is no Table 7 inventory for the
aggregate-solids proxy. Both are recorded on the level rows in `result.json`.

### The flat valley is visible, and it is why the screen reads held-out prediction

The fitted **rate is not identified**: the shared rate lands at 6.5 for Arabica at the low RSD
end and 0.440 at the high end (the weighting between `tds` and the bioactives changes with the
assumed RSD, and the objective is nearly flat in rate), and two independent per-species rates
sit **on the grid edge** (`rate_at_grid_edge: true`). That is the inventory↔rate flat valley
`ANALYSIS_transfer` established (gap **G6**), reproduced here.

This is precisely why the screen scores **held-out prediction** and not the fitted rate: a
non-identifiable pair can still predict, and the question asked is whether per-species freedom
buys held-out accuracy. It does not.

## Figure

`figures/primary.png` — held-out standardised residuals by species and condition, shared-state
and independent-species fits overlaid, at both ends of the RSD band, with the ±1 σ band drawn.
The two marker sets sit on top of each other almost everywhere; **that coincidence is the
result**.

Not registered in the viz layer, for the same reason as I-040 and I-010: a screen artifact, not
a mechanism render bound to a VizSpec fidelity ceiling, and the IF-5 decision forbids extending
a governed registry before Wave 1 reports.

## Corpus warnings

**None of the 32 build warnings is load-bearing for this screen**, and none was repaired.
`docs/cards/angeloni2023.md` resolves with no `TEMPLATE_DEVIATION`, as does
`docs/cards/pannusch2024.md`. All 32 deferred — see
[`../../IF5_HUMAN_TRIAGE_DECISION.md`](../../IF5_HUMAN_TRIAGE_DECISION.md) §7.

## Scope — what this screen did NOT do

- It did **not** score any campaign other than angeloni2023.
- It did **not** upgrade any evidence label. `pannusch2024.solver` remains
  `post_fit_reconstruction`; angeloni2023 remains a data-only intake.
- It did **not** claim the model predicts angeloni. It does not; the blind gap is `ANALYSIS_
  transfer`'s standing result. This screen compares two *fits* on the same held-out points.
- It did **not** attempt to resolve the inventory↔rate non-identifiability. That is gap G6 and
  needs time-resolved data or an independent inventory measurement.
- It did **not** run any candidate outside Wave 1, and did no novelty research.
