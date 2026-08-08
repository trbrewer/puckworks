# I-072 Cheap Screen Decision

```
CHEAP_SCIENTIFIC_SCREEN
NOT_A_PUBLICATION_RESULT
NOT_A_MODEL_VALIDATION_UPGRADE
```

## Question

Under one matched scenario, do `mo2023_2.swelling` and `brewer2026.streamtube` differ in sign,
ordering, or magnitude on an observable they both produce?

Tension row **T-0147** (`model_disagreement` / `declared_competitor`). Note that the row's
`shared_observable` field is **empty**: the generator recorded that `docs/cards/mo2023_2.md`
names the streamtube as a competitor, and asked whether a shared observable exists. It never
asserted one.

## Evidence unit

One component-pair comparison at one matched operating point. No sweep — a response sweep is
RP-A (ROADMAP §9) and is out of scope for the Foundry.

## Method

The protocol ([`PROTOCOL.md`](PROTOCOL.md), frozen and committed before the screen module
existed) puts a **five-part semantic and dimensional compatibility gate** in front of execution:
G1 quantity and definition, G2 index and normalisation, G3 pressure node, G4 intervention and
initial state, G5 validity domains intersect. Execution is conditional on the gate passing.

The gate **fails on all five**, so neither component was run. What the screen produced instead
is (a) the seventeen-row compatibility table the protocol requires, (b) an exact structural
result about each component's output in the other's model, and (c) twelve adversarial checks,
including the two rescues most likely to have produced a false SURVIVE.

## Result

**The two components emit orthogonal moments of the same flow field.**

| | `mo2023_2.swelling` | `brewer2026.streamtube` |
|---|---|---|
| bed-**mean** permeability ratio, indexed by **time** | the model's output (source-data scale 0.048–0.118) | **≡ 1 for every σ** |
| across-**tube** dispersion of permeability at fixed mean | **≡ 0 for every powder** | the model's output (CV = √(e^{σ²}−1)) |

Both degeneracies are exact, not approximate, and both are proved rather than asserted:

- **The streamtube's bed-total flow ratio is identically 1.** Rung A gives tube *i* the velocity
  `q_ref · k_i`, constant in time, so the bed-total flow is `q_ref · Σᵢ wᵢ kᵢ`. Both tube
  constructions normalise that sum to one — the Gauss–Hermite ensemble analytically (the
  `−σ²/2` term is what makes the lognormal unit-mean), the quantile-midpoint ensemble explicitly
  (`k0 *= 1.0 / k0.mean()`). Numerically: max |E[k] − 1| = **3.3 × 10⁻¹⁶** for the
  quantile-midpoint construction across the whole σ grid, and **6.7 × 10⁻¹⁶** for the 15-node
  Gauss–Hermite rule over σ ≤ 1.5.
- **The swelling model's lateral dispersion is identically 0.** `flow_decay` takes no tube
  count and no heterogeneity parameter, and returns one scalar per time sample with no tube
  axis. `docs/cards/mo2023_2.md` states it in terms: *"Mo's 1-D homogeneity is silent on
  channeling."*

So the quantity each component computes is a **structural constant** in the other's model. That
is not a disagreement, and it is equally not an agreement.

The declared validity domains fail to intersect as well: `mo2023_2.swelling` is declared over
powder identities E/H/M/F with **no grinder dial at all**, and `brewer2026.streamtube` over
**EK43 dial 1.1–1.5**. CLAUDE.md rule 9 / ledger A9, G5 forbids mapping one grinder's dial space
onto another's without an explicit refit adapter, and none exists.

**Disclosed limitation of the numerics.** At σ = 2.0 and 3.0 the 15-node Gauss–Hermite rule
itself under-resolves the lognormal tail (worst deviation 1.0 × 10⁻⁷), while the explicitly
renormalised quantile-midpoint construction stays at 1.0 to machine precision at the *same* σ.
The deviation is quadrature resolution, not a mechanism that moves the mean. It is reported
rather than removed by choosing a friendlier σ grid, and the machine-precision claim is scoped
to σ ≤ 1.5 instead of being quietly extended over it.

## Primary figure

[`figures/primary.png`](figures/primary.png) — per the candidate's own instruction for this
branch: *"if no shared definition survives step 1, the two observable definitions side by side
showing why they are not the same quantity."* Panel (a) is the degeneracy matrix; (b) the two
data-flow chains and the two places they fail to meet; (c) and (d) each component's own
observable with the other's structural zero drawn on it — **hatched and labelled
"structurally absent, not a prediction"**, so the flat line is never read as a competing curve.

Panel (c) uses the **digitised source data** (Fig 3a, s_m = 3.6 %) for the magnitude of the
temporal decay. The swelling model was not run to produce it.

## Adversarial check

Twelve checks (A1–A12); **none overturned the finding**. The two that mattered:

- **A10 — the d₃₂ rescue.** The Sauter diameters do overlap numerically: Mo's powders span
  76.0–201.1 µm and the streamtube's dials 1.1/1.3/1.5 span 104.6–124.8 µm, and Mo powder **M**
  (109.0 µm) lands **inside** that span. It rescues nothing. The granulometry behind the
  coincidence differs — for M, the fines radius differs by **26 %** and the boulder radius by
  **37 %** — and d₃₂ is one derived moment, not a grinder dial. Matching a summary statistic is
  not matching a grind.
- **A11 — the Rung-B rescue.** Rung B (`simulate_ensemble_dynamic`) *does* emit a time-indexed
  bed-total flow, which is the index and normalisation G1–G2 need. It is still inadmissible:
  running it requires `lam_e`, `a_open` and `a_clog`, whose module defaults are `0.0` (no
  dynamics) and for which the repository declares no calibrated values; supplying them is
  inventing parameters. Rung B also carries **no gate**, and the registry declares it
  *"hypothesis-generating"*.

**A9** is recorded specifically to prevent a known artifact being sold as a discovery:
`gate_kappa_t_composition_diagnostic` already records mo2023_2's fixed-Δp swelling branch
over-closing a saturated pre-wet bed, *"reported not tuned away"*. This screen reports **no**
numerical disagreement at all, so it cannot be mistaking that mis-scale for a new result.

## Strongest alternative explanation

The candidate's own generated alternative — *"the two components are not answering the same
question; the observable is named the same but defined differently"* — is not merely the
strongest alternative here. **It is the finding.** The human triage predicted it (*"it will
probably retire on 'they answer different questions'"*), and the screen's contribution is to
convert that expectation into an exact, checkable structural statement rather than leaving it as
a judgement call.

The remaining alternative — that the incompatibility is a convention artifact removable by a
transformation — is what A1–A8 test one at a time. None succeeds, and the reason is stable: no
transformation converts a time-indexed bed-mean into a tube-indexed dispersion, because the
target index does not exist in the source model.

## Decision

**RETIRE**

## Why

The components answer different physical questions. `mo2023_2.swelling` computes the bed-**mean**
permeability as a function of **time** under fixed Δp, from a dry bed. `brewer2026.streamtube`
computes the across-**tube dispersion** of permeability at a **fixed mean**, with no time index,
on a saturated bed, under fixed pressure and a fixed delivered-mass endpoint. Each output is
identically constant in the other's model, and their declared validity domains do not intersect
in any descriptor both components accept.

The protocol's frozen ordering rule maps this to RETIRE rather than NEEDS_NEW_DATA: the failures
are on G1–G4, and **no amount of new data changes what a component computes**. NEEDS_NEW_DATA is
reserved for a missing declared value where G1–G4 pass.

Two secondary findings, each of which would have blocked a comparison on its own:

1. **No admissible uncertainty exists for a shared observable.** The only numerical quantity the
   repository declares for `brewer2026.streamtube` is `gate_streamtube_heldout`'s held-out error
   on the **EY relative deviation** (< 0.02, LOO over three grinds). Wrong observable. The
   evidence label `within_campaign_held_out` is a label, not a band, and the protocol froze that
   distinction before any result. On the mo2023_2 side, *"E/H/M within ~5 %, F within ~13 %"* and
   the `max_rel_err < 0.20` gate threshold are model-vs-source **agreement tolerances**, not
   measurement uncertainties, and the source campaign retains no replicate spread on q(t)/q(0).
2. **`brewer2026.streamtube` has no card.** Its validity range and uncertainty are
   registry-sourced, and this result says so rather than inheriting card provenance it does not
   have.

## Claim ceiling

A **registry finding about one declared-competitor row**, and nothing more.

- It does **not** establish that the two components agree. Two components that answer different
  questions neither agree nor disagree.
- It does **not** establish that a real bed lacks either mechanism. `docs/cards/mo2023_2.md`
  says *"a bed can have both"*, and this result is consistent with that.
- It does **not** upgrade, downgrade or restate any validation rung or evidence class.
  `mo2023_2.swelling` remains `source_curve_reproduction`; `brewer2026.streamtube` remains
  `within_campaign_held_out`.
- It licenses **no** statement about espresso.
- The strongest admissible output class is `technical_note`, per the candidate card — and only
  as a registry/provenance note about how declared-competitor rows should be read.

## Next action

None in this branch. The retirement is recorded in
[`../../RETIRED_CANDIDATES.md`](../../RETIRED_CANDIDATES.md) with its reopen condition. The
candidate and this bundle are preserved.

**Reopen condition.** `brewer2026.streamtube` Rung B acquires declared, calibrated values for
`lam_e`, `a_open` and `a_clog` together with a gate, so that it predicts a time-varying
bed-**total** flow ratio — and that prediction is made on a granulometry inside `mo2023_2`'s
declared powder set, or on a grind descriptor both components declare they accept. Then, and only
then, G1–G5 can be re-evaluated on q_total(t)/q_total(0). **Not** reopened by a response sweep
(that is RP-A, ROADMAP §9). **Not** reopened by a d₃₂ coincidence.

## Reproduction

```
python -m puckworks.analysis.screen_i072_matched_observable
python -m pytest tests/test_screen_i072.py -q
```

## Source commit

Base `85f65c0d4b836990152fa4e9bf91c6d292a9e257` (tree `f44eb36c27145e6068009e89fca982138a7401d1`).
`result.json` binds the SHA-256 of `PROTOCOL.md` and of every input file it read.
