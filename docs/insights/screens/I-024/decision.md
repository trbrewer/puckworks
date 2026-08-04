# I-024 Cheap Screen Decision

```
CHEAP_SCIENTIFIC_SCREEN
NOT_A_PUBLICATION_RESULT
NOT_A_MODEL_VALIDATION_UPGRADE
```

## Question

Can one shared hydraulic/transport state explain the Angeloni species observations under one
model and one observation operator — or do the per-species held-out residuals carry structure a
single kinetic story cannot absorb?

## Evidence unit

The **angeloni2023 campaign only**: bioactives + total_solids, granulometry O, on-grid, both
varieties. 18 conditions × 4 species; 12 training conditions (6 and 12 bar), 6 held out (9 bar).
MANIFEST-labelled *independent*.

Maille batch fits, Ellero digitised simulations, Khamitova data and Pannusch/Schmieder post-fit
evidence are **excluded from scoring**; `pannusch2024.solver` appears only as the model.
Exclusions and reasons are in `result.json → evidence_unit.excluded_evidence`.

## Method

One hydraulic state per condition in both models; the only difference is whether the transport
rate is shared across species or per-species. A per-species inventory **level is free in both**,
so the comparison is blind to inventory and assay scaling by construction. Levels are fitted in
closed form because the solver is exactly linear in `c_s0` (verified to ~1e-6). Held-out split,
rate domain and materiality criterion were all predeclared. Full method in
[`README.md`](README.md).

## Result

| | RSD 0.3 % | RSD 19.7 % |
|---|---|---|
| `Z_shared` (RMS standardised held-out residual) | 22.15 | 1.38 |
| `Z_independent` | 22.34 | 1.38 |
| **ratio — what C3 reads** | **1.009** | **1.001** |
| between-species spread of mean `z` | 3.90 | 0.60 |
| C1 `Z_shared > 1` | ✔ | ✔ |
| C2 spread > 1 | ✔ | ✘ |
| **C3 `Z_indep ≤ 0.70 × Z_shared`** | **✘** | **✘** |
| survive | **no** | **no** |

**The decision is invariant across the source's entire stated uncertainty band**, so it is
determined by the retained uncertainty and `NEEDS_NEW_DATA` is not triggered.

Giving every species its own transport rate reduces the held-out residual by **0 %** — in fact
the ratio is slightly above 1 at both ends, meaning the extra freedom makes out-of-sample
prediction marginally *worse*. Species by species, the RMS held-out residuals are
indistinguishable between the two models.

**Inventory / assay check.** Fixing the level at pannusch's Table 2 inventory gives `Z = 92.9`;
fitting a per-species level gives `Z = 22.1` — a per-species level absorbs **76.1 %** of the raw
residual. The fitted levels track the campaign's own measured inventory: Robusta caffeine fitted
**21.26** g/L against angeloni Table 7's measured **18.58** and pannusch's **10.80**.

## Primary figure

[`figures/primary.png`](figures/primary.png) — held-out standardised residuals by species and
condition, shared-state and independent-species fits overlaid, at both ends of the RSD band,
with the ±1 σ band drawn. The two marker sets sit on top of one another almost everywhere.

## Adversarial check

The strongest attempt to make this RETIRE go away is that **the screen never gave the
species-specific hypothesis a fair chance**. Four ways that could be true, each tested:

1. **"The rate grid was too narrow to find a per-species optimum."** It was not: two independent
   per-species rates land *on the grid edge* (`rate_at_grid_edge: true`) and the others spread
   across 0.257–6.500 — a 25× range. The per-species fits explored wildly different transport
   rates and still produced the same held-out residuals. That is the finding, not a limitation.
2. **"The held-out split was rigged to be easy."** The interior pressure was held out, which is
   the *easiest* fair split — interpolation, not extrapolation. An easy split biases toward both
   models predicting well, which would depress `Z_shared`. It does not: `Z_shared` exceeds 1 at
   both ends (C1 passes). The shared state is *not* being flattered.
3. **"The missing solute-specific RSD decides it."** It cannot. C3 is a ratio and is scale-free
   in the assumed RSD; it reads 1.009 and 1.001 against a 0.70 threshold at the two extremes of
   a band spanning a factor of 65. No value inside that band changes C3.
4. **"The free level absorbed real species structure."** This is the strongest version, and it
   is why the level is free in *both* models rather than only one. A free level cannot hide
   species-specific *transport* structure, because a level is condition-independent by
   construction and transport structure is not. What it absorbs — 76.1 % of the raw residual —
   is the condition-independent part, which is exactly inventory and assay scaling.

A fifth angle, in the other direction: the fitted rate is **not identified** (the shared rate
moves from 6.5 to 0.440 as the assumed RSD reweights `tds` against the bioactives). Had this
screen scored the fitted *rate*, it would have produced a spurious species story. It scores
held-out prediction, and that is why the flat valley does not contaminate it.

## Strongest alternative explanation

*"The apparent species difference is a measurement-lineage difference between the assays, not
chemistry."*

**Addressed, and substantially confirmed.** Quantified rather than asserted: 76.1 % of the raw
held-out residual is absorbed by a per-species multiplicative level, and the fitted levels
recover the campaign's own measured inventory more closely than pannusch's does. The species
differ mostly in **how much of them is in the coffee**, not in how they move through it.

The second standing alternative, from the repository's own record: `ANALYSIS_transfer`
established that inventory and rate are practically non-identifiable at a whole-cup endpoint
(gap **G6**). That predicts per-species fits will fit *training* better while buying nothing
held-out. That is exactly what happened, and it is reproduced here on a second split.

## Decision

**RETIRE.**

The candidate's rule, applied without revision: *"RETIRE if residuals are unstructured, or the
structure is common to all species (a shared model-form problem, not a species one)"* — and, per
the human card, *"or it is absorbed by inventory/assay level scaling"*. Two of those three fire:

- **C3 fails at both ends of the uncertainty band.** Per-species transport freedom does not
  materially reduce the held-out residual. This is the scale-free arm and it is decisive.
- **The residual is dominated by level, not by transport.** 76.1 % of it is inventory/assay
  scaling.
- At the high end of the band, **C2 also fails** — the between-species spread (0.60) is below one
  σ, so the remaining structure is not even species-specific.

`NEEDS_NEW_DATA` was live and was genuinely at risk: the campaign does not retain
solute-specific replicate RSD for caffeine, trigonelline or CGA. It was **not** triggered
because the verdict is invariant across the source's own stated 0.3–19.7 % band. Had it flipped,
the finding would have been a named measurement request.

## Why

1. **The observation operator integrates transport differences away.** A cup-integrated endpoint
   at a matched 40 g is a near-exhausted bed. Rate changes shift *when* solute leaves the grain,
   not how much is available to leave, so by the endpoint the species look alike whatever rate
   they are given. A 25× spread in fitted rate produces no held-out separation.
2. **What differs between species is the level.** Inventory and assay scale are
   condition-independent, and they account for three quarters of the raw residual. A "species
   effect" read off an uncorrected residual plot would have been an inventory effect.
3. **The remaining residual is shared, not species-specific.** At the conservative end of the
   uncertainty band the between-species spread falls below one σ, which is the candidate's own
   "shared model-form problem, not a species one" branch.

## Claim ceiling

**The strongest thing this result licenses anyone to say:**

> On the angeloni2023 campaign, scored at held-out 9-bar conditions under one model
> (`pannusch2024.solver`) and one observation operator (matched 40 g endpoint), giving each
> measured species its own transport rate does not improve held-out prediction over a single
> shared rate, and a per-species inventory level accounts for ~76 % of the residual.

It licenses **nothing** beyond that. In particular it does **not** say:

- that species-specific extraction kinetics do not exist. It says this campaign, at this
  observable, cannot see them — and identifies why (the endpoint integrates them away);
- that the shared transport state is *correct*. `Z_shared > 1` at both ends: the shared state
  does not fit within measurement uncertainty either. Neither model is validated here; they are
  compared to each other;
- that the fitted rates mean anything. They are not identified — two sit on the grid edge and
  the shared rate moves 15× with the assumed RSD. Quoting any of them as a transport rate would
  be a misreading of the flat valley;
- that any evidence label has changed. `pannusch2024.solver` remains `post_fit_reconstruction`,
  angeloni2023 remains a data-only intake, and gap G6 remains open.

The ceiling may not exceed the weakest evidence consumed. The weakest input is the assumed
bioactive replicate RSD — which is not measured per cell at all — so the ceiling is a
**comparative statement between two fits under a bounded uncertainty assumption**, not a
statement about coffee chemistry.

## Next action

Record the retirement in [`../../RETIRED_CANDIDATES.md`](../../RETIRED_CANDIDATES.md) with its
reopen condition.

Two things route onward, and neither is part of this screen's output:

- **The measurement that would reopen this is specific and nameable**: solute-specific replicate
  RSD for caffeine / trigonelline / CGA, which `angeloni2023/MANIFEST_UNCERTAINTY.md` already
  records as owed. It would not change C3, but it would let C1 and C2 be evaluated rather than
  bracketed.
- **The observable that would change the answer is fraction-resolved, not whole-cup.**
  `ANALYSIS_transfer` already shows fraction-resolved objectives retain rate information the cup
  discards. A species screen on timed fractions is a *different* candidate and would need data
  this campaign does not have.

No deep screen. No novelty research. Triage rule 1.

## Reproduction

```
python -m puckworks.analysis.screen_i024_common_state
pytest tests/test_screen_i024.py -v
```

## Source commit

- Corpus snapshot the candidate was generated at: `c1b7d79e8f6800df16ad4fc195d45bf156e4ec8b`
- Foundation merge / branch base: `56060e5b589132c496c432fa09e61efea305d5cf`
- Branch: `insights/if5-wave1-cheap-screens`
