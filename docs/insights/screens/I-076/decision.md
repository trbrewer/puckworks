# I-076 Cheap Screen Decision

```
CHEAP_SCIENTIFIC_SCREEN
NOT_A_PUBLICATION_RESULT
NOT_A_MODEL_VALIDATION_UPGRADE
```

> Protocol frozen and committed before execution: [`PROTOCOL.md`](PROTOCOL.md), commit `45f64dd`.
> **No model was executed.**

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

The protocol's sixteen items were frozen first. This screen executes it: an **admissibility
analysis** over cards, registry, manifest and signatures. Both blockers are established
programmatically, not asserted. Full method in [`README.md`](README.md).

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

### Two independent blockers, each sufficient alone

**A — grind dial spaces.** Pannusch's campaign is on a **Mahlkönig E65S** (GL 1.4–2.0, "only
~7.5 % of the E65S scale"); Cameron's grind enters through **measured microstructure and
Darcy-flux tables keyed to an EK43 dial** (1.1–2.3). Two grinders, two dial spaces, **no declared
adapter**. Rule 9 / ledger A9, G5 forbids the mapping.

The numerical coincidence — E65S GL **1.7** and EK43 dial **1.7** — is a trap, not a bridge. The
repository already shows how unsafe the mapping is: for **one** physical Angeloni grind (O), one
code path uses 1.7 (Pannusch) and another uses 1.9 (Cameron), the latter declared "approximate,
**UNCALIBRATED**".

Grind is load-bearing physics for Cameron (`grind_microstructure(gs)` → `phi1, phi2, a2, bet1,
bet2`), so supplying `q` explicitly does not avoid it.

**B — temperature axis.** `simulate_shot` takes `gs, p_bar, m_in, m_out, N, M, q, t_shot,
n_save, rtol, atol, c_s0` and **no temperature**. Cameron is isothermal. Pannusch is declared over
T 80–98 °C with temperature-dependent `K(T)` and `D(T)`. One component has the axis; the other
does not.

### Comparability

**Primary: (5) non-comparable at the intervention.** Secondary: **(2)** on the observable alone
(via Pannusch's own declared mg mL⁻¹ ↔ mass % convention) and **(4)** on inventory (per-solute
pseudo-molecule vs per-bed-volume pool with a 29.6 % EY ceiling).

## Primary figure

[`figures/primary.png`](figures/primary.png) — every scenario axis with the two that block it
marked; the shared observable with its six measured replicates and **no model prediction drawn**,
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
4. **"Cameron is isothermal, so just don't match temperature."** Then the two models are not
   receiving the same intervention, and any difference is unattributable — precisely the
   condition the decision rule routes to NEEDS_NEW_DATA rather than to a verdict.

A fifth, in the opposite direction: **"declare RETIRE — the ranges don't intersect."** The
protocol froze this distinction *before* the result, so it cannot be chosen now: disjoint declared
ranges retire, because no data would change them; a **missing measurable calibration** needs data.
An E65S↔EK43 PSD comparison is a thing that can be measured and simply has not been. Blocker A is
the second kind, and Blocker B is resolved by evidence (a temperature closure or a declared
isothermal-equivalence statement) rather than by re-reading the cards.

## Strongest alternative explanation

*"The two components are not answering the same question — the observable is named the same but
defined differently (pressure-node or observable-convention mismatch)."*

**Partly right, and it is not what blocks the screen.** The observable *is* differently defined —
Pannusch reports mg mL⁻¹ against Cameron's mass %, with different beverage densities (1000 vs
997 kg m⁻³) — but that gap is bridgeable by Pannusch's own declared conversion, which is why the
observable axis classifies as **(2)**, comparable through an existing declared adapter. The
inventory bases are genuinely non-commensurable, which is **(4)**.

Neither is the blocker. The blocker is upstream of the observable entirely: the two components
cannot be given the same **intervention**.

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
   dose, flow, units, uncertainty — lines up. Two upstream axes do not.
2. **Both blockers are about missing *evidence*, not missing *analysis*.** A grind calibration is
   measurable and has not been measured; a temperature basis for Cameron is a statement its source
   could make and has not. Neither is resolved by thinking harder.
3. **The trap was real and was avoided by construction.** The two dials carry the same number.
   Freezing the protocol before touching a model is what made the coincidence visible as a
   coincidence rather than as a convenience.

## Claim ceiling

**The strongest thing this result licenses anyone to say:**

> As of `14c3753`, no scenario in this repository allows `pannusch2024.solver` and
> `cameron2020.extraction_bdf` to be given the same intervention: their grind inputs are settings
> on two different grinders with no declared calibration between them, and only one of the two
> components has a temperature input at all. Their whole-cup TDS outputs could be placed on a
> common observable basis; their inputs cannot.

It licenses **nothing** beyond that. In particular it does **not** say:

- that the two components agree, or disagree. **No comparison was made**, and no model was run;
- that either component is right, wrong, validated or invalidated. Both registry evidence
  strengths are untouched (`post_fit_reconstruction`, `code_verification`);
- that the components are non-comparable *in principle*. They are non-comparable **on the evidence
  this repository currently holds**, and the two measurements that would change that are named;
- anything about `cameron2020.paper_mode`, which stays quarantined and unexamined.

The ceiling may not exceed the weakest evidence consumed. The weakest input is card and registry
metadata, so this is a **statement about admissibility**, carrying no physical content.

## Named missing evidence

1. **A grind calibration linking the two dial spaces** — a measured PSD (or equivalent
   microstructure) for Schmieder's Mahlkönig E65S at GL 1.4/1.7/2.0, on the same basis as the
   existing `cameron2020/psd_figure2` (Cameron's measured EK43 PSD at four dial settings).
   Equivalently for Angeloni's Mythos O/C/F. *Resolves blocker A. Not sufficient alone.*
2. **A temperature basis for `cameron2020.extraction_bdf`** — a declared temperature closure, or a
   source-backed statement of the temperature its fixed parameters correspond to, so a Pannusch
   run can be placed at a temperature Cameron can represent. *Resolves blocker B. Not sufficient
   alone.*

**Both are required.**

## Next action

**No retirement is recorded.** I-076 is not entered in `RETIRED_CANDIDATES.md`; the screen ran and
returned `NEEDS_NEW_DATA`, and this bundle is the record. It does **not** enter the IF-7 queue
either — that is for survivors.

One item is filed for a human and is deliberately not acted on here: the registry `valid_range`
for `pannusch2024.solver` says "EK43-type grind 1.4–2.0", which its own card does not support —
the campaign is on a Mahlkönig E65S. A screen may not edit a registry field, and correcting it
would touch a component's declared validity, so it is recorded and left.

No deep screen. No novelty research. Triage rule 1.

## Reproduction

```
python -m puckworks.analysis.screen_i076_matched_models
pytest tests/test_screen_i076.py -v
```

## Source commit

- Corpus snapshot the candidate was generated at: `c1b7d79e8f6800df16ad4fc195d45bf156e4ec8b`
- Branch base (Wave-1 merge): `14c3753c6e8dab2995332dbe1c3d1e04c4348051`
- Protocol commit (precedes this result): `45f64dd`
- Branch: `insights/if6b-wave2-cheap-screens`
