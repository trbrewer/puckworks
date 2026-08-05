# I-076 Cheap Screen Decision

```
CHEAP_SCIENTIFIC_SCREEN
NOT_A_PUBLICATION_RESULT
NOT_A_MODEL_VALIDATION_UPGRADE
```

> Protocol frozen and committed before execution: [`PROTOCOL.md`](PROTOCOL.md), commit `45f64dd`.
> **No model was executed.**
>
> **Corrected 2026-08-05 after exact-head review — disposition UNCHANGED (NEEDS_NEW_DATA), but the
> blocker set is reduced from two to one.** Review rejected the absence of a temperature
> *argument* in Cameron's signature as an independent blocker: Cameron carries a fixed
> water-property basis documented at ~90 °C, and a fixed or implicit basis is not automatically a
> different intervention. **The grind basis alone is decisive.** The protocol's original
> two-blocker record is preserved verbatim, with a dated erratum appended.

## Question

Under one physically coherent, predeclared matched scenario, do `pannusch2024.solver` and
`cameron2020.extraction_bdf` differ materially in the sign, ordering or magnitude of a genuinely
shared observable after conventions and bases are made explicit?

`cameron2020.paper_mode` is quarantined and was not invoked.

## Evidence unit

`schmieder2023/cup_masses` experiment 7 — the source's own **DoE Central Point** — together with
`docs/cards/{schmieder2023, schmieder2023_AUDIT, pannusch2024, cameron2020}.md`, the registry
entries for both components, and the components' own call signatures.

## Method

The protocol's sixteen items were frozen first (with a dated erratum recording the withdrawn
second blocker). This screen executes it: an **admissibility analysis** over cards, registry,
manifest and signatures. The blocker is established programmatically, not asserted. Full method in [`README.md`](README.md).

## Result

### The scenario exists, and it is good

| | |
|---|---|
| grind level (source dial) | 1.7 |
| measured flow | **1.9011 mL s⁻¹** (6 reps, 1.850–1.986) |
| measured temperature | **88.26 °C** |
| dose / beverage | 20.00 g / 40 g (brew ratio 1/2) |
| observable | whole-cup TDS **9.691 %** mass of beverage |
| replicate RSD | **0.82 %** (campaign mean 2.5 %) |

Interior source-supported condition; measured flow as the common intervention; matched
beverage-mass endpoint; shared observable; real measured uncertainty. **The observable was never
the obstacle.**

### One decisive blocker

**Cross-grinder microstructure mapping.** No declared, source-grounded mapping exists between the
selected Schmieder/E65S grind condition and Cameron's **EK43-derived grind-microstructure**
convention. Cameron resolves its dial through *measured microstructure* tables
(`grind_microstructure(gs)` → `phi1, phi2, a2, bet1, bet2`), so the dial is load-bearing physics
rather than a flux prefactor — supplying `q` explicitly does not avoid it. Rule 9 / ledger A9, G5
forbids the mapping without an explicit refit adapter, and none exists.

The numerical coincidence — Schmieder GL **1.7** and Cameron dial **1.7** — is a trap, not a
bridge. The repository already shows how unsafe the mapping is: for **one** physical Angeloni
grind (O), one code path uses 1.7 (Pannusch) and another uses 1.9 (Cameron), the latter declared
"approximate, **UNCALIBRATED**".

### Temperature is NOT a blocker

`simulate_shot` exposes no temperature argument, but Cameron is not temperature-free: its
implementation carries a fixed water-property basis documented in source —

```
MU = 3.15e-4          # viscosity of water at ~90 C, Pa s
```

— and ~90 °C sits **inside** Pannusch's declared 80–98 °C window, within 2 °C of this scenario's
measured 88.26 °C. **A fixed or implicit temperature basis is not automatically a different
intervention.** Inferring one from a missing argument over-claimed what a signature can show.

What remains is narrower and does not block: the full temperature provenance of Cameron's fitted
kinetic parameters is not documented per-temperature. That is a **non-blocking metadata caveat** —
it would matter for *interpreting* a comparison, not for deciding whether one can be constructed.

### The Pannusch metadata conflict — internal, and unresolved

Not a card-versus-registry error. The **same card** states both that validation is against the
Schmieder-2023 apparatus (whose card names a **Mahlkönig E65S**) *and* that the fitted range is an
**"EK43-type grind 1.4–2.0"**. The two cannot both be right about the grinder family.

Recorded, **not resolved** — a screen may not edit a registry field or a source card, and picking
a winner would be inventing the very mapping this screen is blocked on. Either reading leaves the
grind basis unestablished as EK43-derived microstructure, so the decisive blocker stands under
both.

### Comparability

**Primary: (5) non-comparable at the intervention — on the grind axis alone.** Secondary:
**(2)** on the observable (via Pannusch's own declared mg mL⁻¹ ↔ mass % convention) and **(4)** on
inventory (per-solute pseudo-molecule vs per-bed-volume pool with a 29.6 % EY ceiling).

## Primary figure

[`figures/primary.png`](figures/primary.png) — every scenario axis with the one that blocks it
marked and temperature drawn as a non-blocking caveat; the shared observable with its six measured replicates and **no model prediction drawn**,
because none was computed; and the named missing evidence.

## Adversarial check

The strongest attempt to overturn NEEDS_NEW_DATA is: **"you could have run it — just pick a
dial."** Four ways that fails:

1. **"Use 1.7 for both; the numbers match."** That is the whole trap. The numbers match because
   two manufacturers happen to print similar scales, not because the grinds match. Rule 9 exists
   for exactly this, and it is a rule about physical non-portability, not about tidiness.
2. **"Use the existing `_GRIND_MAP`; it is already in the repository."** It is declared
   "approximate, **UNCALIBRATED**", and it *contradicts* the other in-repo assignment for the same
   physical grind (O → 1.9 for Cameron vs O ≈ 1.7 for Pannusch). Adopting either would be
   inventing a parameter, and adopting both would be inventing two mutually inconsistent ones.
3. **"Supply `q` explicitly and the grind stops mattering."** It does not. `q` removes the
   Darcy-flux dependence; `gs` still sets the measured microstructure that the extraction physics
   runs on.
4. **"Cameron's card names an EK43, so a 1.7 dial IS an EK43 1.7."** That reading depends on
   resolving the conflict *inside* Pannusch's own card in one particular direction. The screen
   may not resolve it — and doing so would be inventing the mapping, not discovering it.

An attack that **succeeded**, and is the reason for this revision: **"the absence of a temperature
argument does not establish a different intervention."** Correct. Cameron carries a fixed ~90 °C
water-property basis inside Pannusch's declared window; the second blocker was withdrawn and
downgraded to a non-blocking caveat. The disposition is unchanged because the grind blocker never
depended on it.

One in the opposite direction: **"declare RETIRE — the ranges don't intersect."** The protocol
froze this distinction *before* the result, so it cannot be chosen now: disjoint declared ranges
retire, because no data would change them; a **missing measurable calibration** needs data. An
E65S↔EK43 PSD comparison is a thing that can be measured and simply has not been.

## Strongest alternative explanation

*"The two components are not answering the same question — the observable is named the same but
defined differently (pressure-node or observable-convention mismatch)."*

**Partly right, and it is not what blocks the screen.** The observable *is* differently defined —
Pannusch reports mg mL⁻¹ against Cameron's mass %, with different beverage densities (1000 vs
997 kg m⁻³) — but that gap is bridgeable by Pannusch's own declared conversion, which is why the
observable axis classifies as **(2)**, comparable through an existing declared adapter. The
inventory bases are genuinely non-commensurable, which is **(4)**.

Neither is the blocker. The blocker is upstream of the observable entirely: the two components
cannot be given the same **grind intervention**.

## Decision

**NEEDS_NEW_DATA.**

The frozen rule applied without revision: *"NEEDS_NEW_DATA if constructing the matched scenario
requires an invented parameter."* It does — an E65S↔EK43 dial calibration that no source supplies.

- **SURVIVE** would require a directly comparable or existing-adapter comparison showing a
  difference beyond declared uncertainty. No comparison exists to show one.
- **RETIRE** would require overlapping results, non-intersecting declared ranges, or a
  disagreement fully explained by convention. The first needs a comparison; the second is false
  (the ranges are not disjoint — they are *incommensurable*, which is different); the third
  presupposes a measured disagreement.

## Why

1. **The obstacle is the intervention, not the observable.** Everything downstream — endpoint,
   dose, flow, units, uncertainty — lines up. One upstream axis does not.
2. **The blocker is missing *evidence*, not missing *analysis*.** A grind calibration is
   measurable and has not been measured. It is not resolved by thinking harder, and it is not
   resolved by reading the cards more carefully — which is precisely what distinguishes it from
   the temperature question, where closer reading *did* resolve the matter and removed a blocker.
3. **The trap was real and was avoided by construction.** The two dials carry the same number.
   Freezing the protocol before touching a model is what made the coincidence visible as a
   coincidence rather than as a convenience.

## Claim ceiling

**The strongest thing this result licenses anyone to say:**

> As of `14c3753`, no scenario in this repository allows `pannusch2024.solver` and
> `cameron2020.extraction_bdf` to be given the same **grind** intervention: their grind inputs are
> settings on two different grinders with no declared calibration between them, and the card that
> would settle which grinder Pannusch was fitted on contradicts itself. Their whole-cup TDS
> outputs could be placed on a common observable basis; their grind inputs cannot.

It licenses **nothing** beyond that. In particular it does **not** say:

- that the two components agree, or disagree. **No comparison was made**, and no model was run;
- that either component is right, wrong, validated or invalidated. Both registry evidence
  strengths are untouched (`post_fit_reconstruction`, `code_verification`);
- that the components are non-comparable *in principle*. They are non-comparable **on the evidence
  this repository currently holds**, and the one measurement that would change that is named;
- **that the two components are thermally incompatible.** They are not shown to be. Cameron
  carries a fixed ~90 °C water-property basis inside Pannusch's declared 80–98 °C window; the
  open question is the undocumented temperature provenance of Cameron's fitted parameters, which
  is a caveat on interpreting a comparison, not a barrier to constructing one;
- anything about `cameron2020.paper_mode`, which stays quarantined and unexamined.

The ceiling may not exceed the weakest evidence consumed. The weakest input is card and registry
metadata, so this is a **statement about admissibility**, carrying no physical content.

## Named missing evidence

**One item.**

1. **A grind calibration linking the two dial spaces** — a measured PSD (or equivalent
   microstructure) for Schmieder's Mahlkönig E65S at GL 1.4/1.7/2.0, on the same basis as the
   existing `cameron2020/psd_figure2` (Cameron's measured EK43 PSD at four dial settings).
   Equivalently for Angeloni's Mythos O/C/F. *Resolves the decisive blocker. **Sufficient
   alone**.*

A temperature basis for `cameron2020.extraction_bdf` — a declared closure, or a source-backed
statement of the temperature its fitted kinetic parameters correspond to — would **improve** a
future comparison but is **not** required to construct one, and is therefore deliberately not on
this list.

## Next action

**No retirement is recorded.** I-076 is not entered in `RETIRED_CANDIDATES.md`; the screen ran and
returned `NEEDS_NEW_DATA`, and this bundle is the record. It does **not** enter the IF-7 queue
either — that is for survivors.

One item is filed for a human and is deliberately not acted on here: **`docs/cards/pannusch2024.md`
contradicts itself about the grinder.** The same card states that validation is against the
Schmieder-2023 apparatus — a **Mahlkönig E65S** — and that the fitted range is an **"EK43-type
grind 1.4–2.0"** (the wording the registry repeats). This is an *internal* conflict, not a
card-versus-registry error, and the screen does not say which side is right: a screen may not edit
a source card or a registry field, and resolving it would amount to inventing the cross-grinder
mapping this screen is blocked on.

No deep screen. No novelty research. Triage rule 1.

## Reproduction

```
python -m puckworks.analysis.screen_i076_matched_models
pytest tests/test_screen_i076.py -v
```

## Source commit

- Corpus snapshot the candidate was generated at: `c1b7d79e8f6800df16ad4fc195d45bf156e4ec8b`
- Branch base (Wave-1 merge): `14c3753c6e8dab2995332dbe1c3d1e04c4348051`
- Protocol commit (precedes this result): `45f64dd`; erratum appended 2026-08-05 after review
- Branch: `insights/if6b-wave2-cheap-screens`
