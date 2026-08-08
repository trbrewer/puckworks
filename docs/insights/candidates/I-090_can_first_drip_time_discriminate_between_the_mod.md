# I-090 — Can first_drip_time discriminate between the models that predict it?

> Generated from the insight portfolio at commit `56060e5b58`. A card is created when a person decides to work a candidate; everything below the Question is a STARTING POINT, not a result.

## Question

Does first_drip_time, measured by data already in the manifest, separate the models that predict it by more than their within-model uncertainty?

## Insight type

hidden_discriminator, experiment_design

## Target audiences

technical_note, experiment_design, public_story

## Why it may matter

Discrimination without new measurement is the cheapest decisive screen the corpus can offer.

## Why it may be surprising

_not yet written — this is a seed._

## Models, datasets, and other entities

- `model:foster2025.infiltration`
- `model:foster2025.machine_mode`
- `dataset:de1_fixtureA`

## Tension rows

T-0171

## Existing evidence

- foster2025.infiltration=sign_or_compatibility; foster2025.machine_mode=source_curve_reproduction

## Strongest alternative explanation

The observable is defined differently by each model, so the separation is a convention artifact.

## Cheap scientific screen

Signature atlas: predicted first_drip_time per model over a matched domain, against the manifest measurements, with replicate variation drawn.

## Minimum viable figure

Predicted first_drip_time per model versus its controlling input, with the measured points and their spread overlaid.

## Decision rule

- **SURVIVE if** Between-model separation exceeds within-model uncertainty somewhere the data lands.
- **RETIRE if** Model predictions overlap once uncertainty is drawn, or the measurements fall outside every model's validity range.
- **INCONCLUSIVE if** The measurements are single-replicate and no spread can be drawn.

## Stop condition

Predictions overlap after declared uncertainty.

## Possible outputs

- technical_note
- experiment_design
- public_story

## External novelty search terms

- model discrimination observable selection
- espresso extraction mechanism discrimination

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
`python -m puckworks.insights card I-090` at the foundation merge
`56060e5b589132c496c432fa09e61efea305d5cf`, which is what the generated header line stamps.
`python -m puckworks.insights verify` returns `OK` at both, so the snapshot did not drift.

**Shortlist status: `SHORTLISTED`** — recorded here only. The generated portfolio entry for I-090
is still `SEED` and still unscored; this selection is a human decision, not a generator score.

### Human lane

**High-risk — the cheapest decisive screen the corpus could offer if it works, and the most likely
to return `NEEDS_NEW_DATA` if it does not.** Discrimination on an already-measured observable with
no new experiment is the best value in the portfolio; the replicate-spread exposure is real enough
that it is not a Wave-1 bet.

### Strongest alternative explanation (human)

Two, and the second is the one that decides the screen:

1. As generated — *the observable is defined differently by each model, so the separation is a
   convention artifact.* `foster2025.infiltration` and `foster2025.machine_mode` are different
   branches; "first drip" can mean front breakthrough at the bed exit or first mass at the scale,
   and those are not the same instant. A separation between two definitions is not discrimination.
2. **No within-model uncertainty band can be drawn.** `de1_fixtureA` is a single fixture. The
   candidate's own INCONCLUSIVE clause names this exactly: "the measurements are single-replicate
   and no spread can be drawn." Without spread, "separation exceeds within-model uncertainty" is
   not evaluable, and the honest answer is a data request, not a verdict.

### Precise cheap screen

Signature atlas: predicted `first_drip_time` per model over a matched domain, against the manifest
measurements, with replicate variation drawn. Fix the observable definition **first** and record it;
if the two branches define it differently, that is the result and no discrimination claim follows.

### Readiness note (not a hard blocker, but it shapes the answer)

`de1_fixtureA` (MANIFEST row 27) names `source_card` `(registry [RS])`, which is not a card stem —
one of the deferred `MANIFEST_SOURCE_CARD_UNRESOLVED` warnings. `docs/cards/foster2025.md` also
carries a full `TEMPLATE_DEVIATION`. The screen must state which measurement provenance it is
relying on rather than inheriting it silently. A repair here is the same lane's work as I-013.

### Primary figure

Predicted `first_drip_time` per model vs its controlling input, with the measured points and their
spread overlaid — and, if no spread exists, the measured points drawn as single-replicate marks
with the absence of a band made visually explicit rather than implied.

### Decision criteria

- **SURVIVE** — between-model separation exceeds within-model uncertainty somewhere the data lands,
  under one fixed observable definition.
- **RETIRE** — model predictions overlap once declared uncertainty is drawn, the measurements fall
  outside every model's validity range, or the apparent separation is an observable-convention
  artifact.
- **NEEDS_NEW_DATA** — the measurements are single-replicate and no spread can be drawn. Expected;
  the deliverable is then a specific, costed replicate-measurement request (the observable, the
  number of replicates a design calculation supports, and the rig), not a verdict.

### Likely output class

`experiment_design` most likely (a targeted first-drip replicate campaign), `technical_note` if
discrimination is actually achieved, `public_story` only downstream of one of those.

### Screen outcome (appended after the Wave-3 cheap screen ran, 2026-08-07)

**RETIRE** — `docs/insights/screens/I-090/`. Recorded in
[`../RETIRED_CANDIDATES.md`](../RETIRED_CANDIDATES.md) with a reopen condition.

**This card expected `NEEDS_NEW_DATA` plus a costed replicate request, and that is not what the
evidence supports.** The card's second alternative was confirmed factually — `de1_fixtureA` is
one physically independent extraction, 100 samples *of it*, median cadence 0.270 s (event
*resolution*, not population variance), no replicate spread, no declared within-model band for
either component, grind setting **assumed** and κ **fitted to this same shot**. But it is not the
binding obstacle. The comparison is ill-posed **upstream** of the uncertainty question.

**The two components are not rivals.** They are sequential stages of one pipeline —
`foster2025.machine_mode` (stage `machine`) *generates* the pressure history that
`foster2025.infiltration` (stage `infiltration`) *consumes*. Both bind to the **same card**,
`docs/cards/foster2025.md`, whose Interface mapping states: *"one card serves
`foster2025.infiltration` and `foster2025.machine_mode`, so anything listed above is attributed
to both."* So T-0171's *"2 registered models name first_drip_time among their interface outputs"*
is **one Outputs clause counted twice** — co-location, not a relationship.

**They are one front law, demonstrated.** Fed `machine_mode`'s own implied bed-top pressure,
`infiltration`'s public closed form reproduces `machine_mode`'s front to RMSE **7.0 × 10⁻⁸ mm** on
a 9.975 mm bed, with the residual falling under grid refinement (1.7e-5 → 1.1e-6 → 7.0e-8), which
is what identifies it as quadrature error rather than a physical difference. Any first-drip
difference between them is therefore a difference in the **pressure history supplied** — a
boundary condition, not a mechanism.

**The convention artifact the first alternative predicted is real, and quantified.** The measured
event moves with the detection threshold across 6.793 s (0.05–0.2 g) to 8.775 s (2.0 g) — a
**1.982 s** span, wider than the **1.4 s** model bracket (6.4–7.8 s) the existing gate compares
against. And `de1_fixtureA` lies outside `machine_mode`'s declared configuration (DeLonghi EC685,
59 mm basket, 10 g fine grind), which cannot consume a recorded trace at all.

**A replicate campaign would NOT have rescued it**, and the screen says so explicitly so that the
experiment this card anticipated is not commissioned for an ill-posed comparison.

**The readiness note held and was acted on.** The screen states which measurement provenance it
relies on rather than inheriting it, and it surfaced a further finding: MANIFEST row 27 declares
`validation_strength = independent (parameter-free triangle)`, contradicting ROADMAP §7.1's own
2026-07-16 entry. That target is **named and deliberately not edited** — the Foundry is not an
authority over an evidence label, and I-045 set the precedent.

**Claim ceiling.** Under the current repository implementations and controlling card semantics,
`foster2025.machine_mode` and `foster2025.infiltration` are producer/consumer views of one front
evolution, not rival first-drip models. First-drip data therefore cannot discriminate between them
as presently defined. This does **not** independently validate the shared front law, prove
machine-mode accuracy, or generalise beyond the declared configuration, and it changes no
validation rung — `foster2025.infiltration` remains `sign_or_compatibility`,
`foster2025.machine_mode` remains `source_curve_reproduction`.

**Reopen condition.** Reopen only if future repository authorities establish two genuinely
distinct front dynamics, two independently parameterised rival hypotheses, or two different
model-to-observable mappings that predict the same fixed first-drip event. **Additional replicates
under the current shared law do not reopen it.**

**No follow-on work.** No deep screen, novelty search or manuscript task follows from this
retirement, and none was started.
