# I-040 Cheap Screen Decision

```
CHEAP_SCIENTIFIC_SCREEN
NOT_A_PUBLICATION_RESULT
NOT_A_MODEL_VALIDATION_UPGRADE
```

## Question

For the dataset whose `validation_strength` names both an independent and a post-fit strength,
which of those strengths does each consuming gate actually rely on?

Dataset: `waszkiewicz2025/traces_time_dependent`. The cell, verbatim:

```
independent within-rig (equilibrium) / post-fit (9-bar Q(t) reproduction)
```

## Evidence unit

The repository's own source: MANIFEST row 2, `puckworks/data/__init__.py`,
`puckworks/validation/gates.py`, `puckworks/harness.py`, `puckworks/public/claims.py`, the
`brewer2026.coupled_kappa_t` and `waszkiewicz2025.poroelastic` modules, the analyses, the viz
producers and the paper builds. No experimental datum is scored; the unit of evidence is the
consumer's own text and the columns it reads.

## Method

Four separable layers — static AST enumeration (over-approximating), dynamic tracing of every
flagged gate, an adversarial docstring strength scan, and a hand-read attribution table.
Reconciled: an uncovered consumer forces `NEEDS_NEW_DATA` rather than a verdict. Full method in
[`README.md`](README.md).

## Result

**27 consumers attributed. 0 promotions.**

| | count |
|---|---|
| loader call sites (static) | 21 |
| gates flagged by static reachability (over-approximating) | 12 |
| gates confirmed by dynamic tracing | **7** |
| static false positives resolved by tracing | 5 |
| public claims | 2 |
| producers / analyses / renderers (assert nothing, inherit) | 18 |
| **consumers stating a strength stronger than their half** | **0** |

### Attribution by half

**Half A — "independent within-rig (equilibrium)"** — the 11-point long-run curve
(`basket_pressure__bar[-1]`, `mass_flow_rate__g_per_s[-1]`), basket node.

| consumer | states | vs its half |
|---|---|---|
| `gate_waszkiewicz_static_refit` | independent | matches |
| `poroelastic.steady_state_curve` (producer) | — | n/a |

**Half B — "post-fit (9-bar Q(t) reproduction)"** — the time-resolved trajectory, basket node.

| consumer | states | vs its half |
|---|---|---|
| `gate_waszkiewicz_dynamic_9bar` | post-fit reconstruction | matches |
| `gate_p2_cross_pressure` | post-fit reconstruction | matches |
| `gate_kappa_t_degeneracy` | verification | weaker (conservative) |
| `gate_p2_kappa_ladder` | *none stated* | label carried downstream by PV-02 |
| `gate_kappa_t_composition_diagnostic` | *none stated* | label carried downstream by PV-05 |
| **PV-02** | post-fit reconstruction | matches |
| **PV-05** | qualitative | weaker (conservative) |

plus 16 producers / analyses / renderers that assert nothing and inherit.

**Neither half — the category the cell does not anticipate.**

| consumer | reads | states |
|---|---|---|
| `gate_ntube_kappa_t_union` | `time__s` only | qualitative |
| `coupled_kappa_t.simulate` (producer) | `time__s` only | — |

The dataset supplies a **clock**. No measured column is scored against it; the assertion
(single-channel collapse, `N_eff → ~1`) is carried by the streamtube/porosity machinery. Its
`(P_c, Q_c)` come from `published_calibration()` — a different manifest row,
`waszkiewicz2025/static_calibration`.

**Both halves — one consumer, because the split IS its subject.**
`analysis.waszkiewicz_shot_level.recorded_pressure_robustness` compares the recorded-pressure
convention against the reference-pressure label, touching the endpoint and the trajectory. It
leans on neither half as evidence *for a model*.

## Primary figure

[`figures/primary.png`](figures/primary.png) — asserting consumers grouped by the half they
lean on, with columns read, strength stated, and the comparison.

## Adversarial check

The strongest available attempt to make the RETIRE go away, run mechanically so it could not be
skipped by inattention:

1. **Two independent enumerations, and the human table must cover the union.** Had the table
   been built only from the six obvious consumers, `gate_ntube_kappa_t_union` would have been
   missed silently. The static layer flagged 12 gates; the dynamic layer confirmed 7; the table
   covers all 7 and all 21 call sites. Coverage is `complete = true`. This is the check that
   actually bit.
2. **Token scan for a promotion.** Every real consumer's docstring was scanned for the ROADMAP
   §0 vocabulary. **One candidate promotion was flagged**: `gate_p2_cross_pressure` rests on
   the post-fit half and its docstring contains "independent". Cleared by reading — the word
   appears **negated**: *"within-campaign CONDITIONAL transfer, NOT independent out-of-sample
   validation"*. That is an explicit refusal of the independent half, i.e. the opposite of a
   promotion. No unresolved candidate promotion remains.

Both checks were run before the decision rule was applied, and the rule was not modified after
seeing them.

## Strongest alternative explanation

*"The cell is mixed only in wording; both halves support the same gate assertion equally."*

**Addressed, and it is substantially correct — with one qualification that strengthens rather
than weakens the retirement.** The two halves are not separate artifacts but two *readings of
one file*: half A is the last time point of each of 11 traces, half B is the full trajectory.
So "touches the file" carries no information at all, and attribution had to be made by what
each assertion depends on. It was, per consumer, and the halves turn out to be cleanly
separated in practice — `steady_state_curve()` is the only route to half A, and it is consumed
by exactly one gate.

The qualification: the alternative predicts the halves are *interchangeable*. They are not.
PV-02's evidence selection actively distinguishes them, refusing the half-A gate as evidence
for a half-B claim on the ground that it "concerns … a different observable". The halves
support **different** assertions, and the repository already knows it.

## Decision

**RETIRE.**

The candidate's rule, applied without revision: *"RETIRE if every consuming gate already reads
the correct half."* Every one does. Of the nine asserting consumers, four state a strength that
matches their half exactly, three state a strictly weaker one, and two state none at all and
inherit a matching-or-weaker label downstream. No consumer states a strength stronger than the
half its assertion rests on.

`NEEDS_NEW_DATA` was available and was **not** triggered: the source metadata was sufficient to
attribute every consumer, and coverage reconciliation passed.

## Why

Three findings, in descending order of how much they carried the decision:

1. **The claim layer enforces the split at the strongest possible point.** PV-02 selects only
   `gate_waszkiewicz_dynamic_9bar` and records `"EXCLUDED: gate_waszkiewicz_static_refit, which
   concerns the steady-state pressure-flow curve and the recovered P_c/Q_c -- a different
   observable."` A reader-facing claim resting on the post-fit half explicitly declines to cite
   the independent-half gate. That is the exact failure mode the candidate was looking for,
   already prevented by construction.
2. **The one gate on half A does not reach the trajectory at all.** It touches the dataset only
   through `steady_state_curve()`, which takes `[-1]` of each trace. There is no code path by
   which the 9-bar reconstruction could contribute to its assertion.
3. **Conservatism runs in the safe direction throughout.** `gate_kappa_t_degeneracy` states
   `verification` (a model-vs-model reduction) on a half labelled `post-fit reconstruction`;
   PV-05 states `qualitative`. Both under-claim relative to their half.

### Two observations recorded, neither a finding

- **Two gates state no strength in their own docstring** (`gate_p2_kappa_ladder`,
  `gate_kappa_t_composition_diagnostic`). Their labels exist — PV-02 "post-fit reconstruction",
  PV-05 "qualitative" — but downstream. A reader of the gate alone gets no rung. Per the
  candidate's own criteria this is a coarse assertion, which the card's decision block routes
  to RETIRE-with-the-coarseness-recorded, **not** to `NEEDS_NEW_DATA`. Recording it here is the
  whole of the action it warrants.
- **The screen did not adjudicate half A's own label.** `gate_waszkiewicz_static_refit`
  reproduces the source's own published static fit from the source's own equilibrium data, and
  the gate discloses this ("same method + data"). Whether "independent within-rig" is the right
  manifest label for that is a question about the **cell**, not about which half a consumer
  leans on — outside this candidate's decision rule, and deliberately left with no verdict. It
  is noted for whoever works I-045, which audits a second mixed cell by the same method.

## Claim ceiling

**The strongest thing this result licenses anyone to say:**

> As of commit `c1b7d79`, an enumeration of every in-repository consumer of
> `waszkiewicz2025/traces_time_dependent` found no consumer stating a validation strength
> stronger than the half of its mixed manifest cell that its assertion rests on.

It licenses **nothing** beyond that. In particular it does **not** say:

- that any evidence label is correct — only that consumers read the half they cite;
- that the manifest's own half-A label is right (explicitly not adjudicated);
- anything about any other dataset, including the other mixed cells in the manifest;
- that the post-fit half has become stronger evidence. It has not. Every "post-fit
  reconstruction" label consumed here remains post-fit reconstruction, with the manifest's own
  soft-circularity caveat intact.

The ceiling may not exceed the weakest evidence the screen consumed. The screen consumed
provenance metadata and source text — so the ceiling is a **statement about bookkeeping**, and
it carries no physical content whatsoever.

## Next action

Record the retirement in [`../../RETIRED_CANDIDATES.md`](../../RETIRED_CANDIDATES.md) with its
reopen condition. Carry the two recorded observations into **I-045** (Wave 2), which audits
`foster2025_2/fig12_14_curves` by this same method and can reuse this module's four-layer
structure directly.

No deep screen. No novelty research. Triage rule 1: only survivors get either.

## Reproduction

```
python -m puckworks.analysis.screen_i040_evidence_halves
pytest tests/test_screen_i040.py -v
```

## Source commit

- Corpus snapshot the candidate was generated at: `c1b7d79e8f6800df16ad4fc195d45bf156e4ec8b`
- Foundation merge / branch base: `56060e5b589132c496c432fa09e61efea305d5cf`
- Branch: `insights/if5-wave1-cheap-screens`
