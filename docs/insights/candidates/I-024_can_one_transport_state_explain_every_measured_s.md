# I-024 — Can one transport state explain every measured species at once?

> Generated from the insight portfolio at commit `56060e5b58`. A card is created when a person decides to work a candidate; everything below the Question is a STARTING POINT, not a result.

## Question

Under one shared hydraulic and transport state, do the per-species residuals show structure that a single kinetic story cannot absorb?

## Insight type

cross_species, identifiability

## Target audiences

domain_paper, technical_note

## Why it may matter

It separates species-specific diffusion from inventory mis-specification — two very different corrections.

## Why it may be surprising

_not yet written — this is a seed._

## Models, datasets, and other entities

- `model:maille2024.phi_closure`
- `dataset:angeloni2023/bioactives`
- `dataset:angeloni2023/inventories`
- `dataset:angeloni2023/lipids`
- `dataset:angeloni2023/total_solids`
- `dataset:ellero2019/fig4_caffeine_content`
- `dataset:khamitova2020/tamping`
- `model:maille2024.two_regime`
- `model:pannusch2024.closures`
- `model:pannusch2024.solver`

## Tension rows

T-0037, T-0038, T-0039, T-0040

## Existing evidence

- card interface outputs + manifest rows, verbatim labels retained

## Strongest alternative explanation

The apparent species difference is a measurement-lineage difference between the assays, not chemistry.

## Cheap scientific screen

Fit one shared state across species and inspect the per-species residual structure; compare against per-species independent fits.

## Minimum viable figure

Per-species residuals versus time under the shared fit, with the independent-fit residuals overlaid.

## Decision rule

- **SURVIVE if** Residual structure is species-specific and survives the independent-fit comparison.
- **RETIRE if** Residuals are unstructured, or the structure is common to all species (a shared model-form problem, not a species one).
- **INCONCLUSIVE if** Species measurements come from too few campaigns to separate species effects from campaign effects.

## Stop condition

Per-species residual structure is within measurement uncertainty.

## Possible outputs

- domain_paper
- technical_note

## External novelty search terms

- multi-solute extraction kinetics coffee
- species-specific diffusion coffee
- trigonelline caffeine chlorogenic extraction

_Run only after the candidate survives its cheap screen (blueprint §13.4)._

## Status

SEED

Transitions require a one-line reason appended here.

---

## Human triage (IF-5)

*Hand-written on 2026-08-04, after the generated body above. Everything above this line is generator
output at the `c1b7d79e…` corpus snapshot and is preserved byte-identical — question, stable ID,
entity relations, tension rows and provenance included. The decision record is
[`../IF5_HUMAN_TRIAGE_DECISION.md`](../IF5_HUMAN_TRIAGE_DECISION.md).*

**Provenance of this card.** Content derives from corpus snapshot
`c1b7d79e8f6800df16ad4fc195d45bf156e4ec8b`; the card file was materialised by
`python -m puckworks.insights card I-024` at the foundation merge
`56060e5b589132c496c432fa09e61efea305d5cf`, which is what the generated header line stamps.
`python -m puckworks.insights verify` returns `OK` at both, so the snapshot did not drift.

**Shortlist status: `SHORTLISTED`** — recorded here only. The generated portfolio entry for I-024
is still `SEED` and still unscored; this selection is a human decision, not a generator score.

### Human lane

**Wave 1 — executing now.** The portfolio's only `cross_species_inconsistency` candidate: there is
no second attempt if it is skipped. It reuses an observation operator Paper A already froze, and it
can return a *useful* `NEEDS_NEW_DATA` on a well-understood axis rather than stalling.

### Strongest alternative explanation (human)

The generated alternative is the right one and is elevated to a **test**, not a caveat: *the
apparent species difference is a measurement-lineage difference between the assays, not chemistry.*
Made precise for this campaign — the species are measured by different assays (HPLC for the
bioactives, gravimetric total solids for TS) and their solid inventories come from a separate
Table 7 R&G assay. Either a per-species **inventory** error or a per-species **assay scale** error
produces a *level* offset per species that is constant across conditions, which is exactly what a
naive residual plot would show as "species structure".

The screen must therefore separate **level** structure (absorbable by inventory/assay scaling, and
therefore not evidence against a shared transport state) from **condition-dependent** structure
(not absorbable, and the only thing that can survive).

A second alternative, from the standing record: `ANALYSIS_transfer` established that inventory and
rate are practically non-identifiable at a whole-cup endpoint (the flat valley, gap G6). Per-species
independent fits will therefore *always* fit training better; only their **held-out** improvement
counts.

### Precise cheap screen

Evidence unit: **the Angeloni campaign only.** Maille batch fits, Ellero digitised simulations,
Khamitova data and Pannusch/Schmieder post-fit evidence are **excluded** from scoring — they appear
in the generated entity list because the lens grouped them, not because they belong in this screen.

1. Predeclare held-out conditions before fitting.
2. Fit one shared hydraulic/transport state (one shared rate scale, one model, one observation
   operator) on the training conditions.
3. Compute held-out per-species residuals.
4. Normalise by retained inventory and measurement uncertainty where available.
5. Compare the shared-state result against independent per-species fits.
6. Test explicitly whether any apparent species structure is absorbed by an inventory or assay
   **level** rescaling.
7. Apply one predeclared quantitative materiality criterion tied to measurement uncertainty.

### Primary figure

Held-out standardised residuals by species and condition, shared-state and independent-species fits
overlaid. `docs/insights/screens/I-024/figures/primary.png`.

### Decision criteria

- **SURVIVE** — reproducible species-specific held-out residual **structure** remains beyond
  uncertainty *and* is materially reduced by per-species fits.
- **RETIRE** — residuals are unstructured, or the structure is shared across species (a model-form
  problem, not a species one), or it is absorbed by inventory/assay level scaling.
- **NEEDS_NEW_DATA** — the retained uncertainty or inventory information is inadequate to make the
  comparison. The known exposure: solute-specific replicate RSD is **not** recovered for
  caffeine/trigonelline/CGA (the source gives only a global 0.3–19.7 % range); only TS and lipids
  carry per-condition RSD.

### Likely output class

`domain_paper` if it survives (species-resolved transport structure is a physical result);
`technical_note` on multi-species identifiability if it retires on the inventory/assay explanation.
