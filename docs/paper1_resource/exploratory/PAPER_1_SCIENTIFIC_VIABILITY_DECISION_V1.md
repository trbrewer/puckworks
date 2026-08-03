# Paper 1 — scientific viability decision

```
EXPLORATORY_SAME_CAMPAIGN_VIABILITY_SCREEN
NOT_A_FROZEN_P0_GATE_RESULT
```

**date:** 2026-08-03 · **branch:** `paper1/scientific-viability-screen` · **gate_binding:** `null`
**inputs:** `PAPER_A_VIABILITY_ENDPOINT_V1.{json,md}`,
`PAPER_A_VIABILITY_OBSERVATION_OPERATOR_V1.{json,md}`,
`PAPER_A_VIABILITY_MATCHED_DATA_MANIFEST_V1.json`, `figures/`

---

## 1. Is there a worthwhile paper?

**Not the paper that was planned, and not on this evidence.** The two analyses that were supposed to
carry Paper 1 both came back negative, and they came back negative in the same direction. Part A: the
large-rate endpoint is *not* uniformly acceptable — four of six variety–solute groups fail the
programme rule, one is clearly excluded, two are so flat that the data cannot distinguish a fast
finite rate from an infinite one, and the whole verdict moves with the tolerance convention. Part B:
the hypothesis that fraction-resolved observations recover rate information that cup measurements
discard is **not supported on this campaign** — six fractions predict held-out extraction 5–10
percentage points *worse* than a three-point cup curve, for all three solutes, under every objective
and level policy tried, while the localisation comparison depends on which tolerance convention is
used and separates nothing. The one genuinely interesting finding is a
by-product: fraction data expose a structured late-time misfit in the declared model that cumulative
averaging hides almost entirely. That is a result about the solver, not about observation design, and
it points at solver development rather than at a Paper 1 headline.

## 2. Part A — endpoint table

| group | `J_ref` | `κ_ref` | `J_inf` | gap | ratio | 10 % rel | 5 % rel | 20 % rel | 0.10 pp | 0.25 pp |
|---|---|---|---|---|---|---|---|---|---|---|
| Arabica:caffeine | 2.8319 | 0.764 | 2.9945 | +0.163 | 1.057 | included | excl | incl | **excl** | incl |
| Arabica:trigonelline | 2.2431 | 1.700 | 2.2771 | +0.034 | 1.015 | included | incl | incl | incl | incl |
| Arabica:5CQA | 4.6056 | 1.025 | 5.0944 | +0.489 | 1.106 | **excluded** | **excl** | incl | **excl** | **excl** |
| Robusta:caffeine | 4.8934 | 6.312 | 4.8998 | +0.006 | 1.001 | included | incl | incl | incl | incl |
| Robusta:trigonelline | *unresolved* | — | 3.8630 | — | — | *indet* | *indet* | *indet* | *indet* | *indet* |
| Robusta:5CQA | *unresolved* | — | 11.7653 | — | — | *indet* | *indet* | *indet* | *indet* | *indet* |

Programme reading under the accepted rule: **`H1_DOES_NOT_LEAD`** (2 successes, 4 failures).

## 3. Part B — observation-operator table

GL 1.7 primary, 16 shots / 5 experiments, shot-balanced MAPE with exact per-shot level profiling:

| solute | arm | `κ*` | `J_min` (pp) | width, 10 % rel | width, 0.25 pp abs | held-out MAPE (pp) | materially better? |
|---|---|---|---|---|---|---|---|
| caffeine | FRACTION_6 | 1.035 | 4.498 | 0.180 | **0.139** | 6.21 | — |
| caffeine | CUP_CURVE_3 | 1.732 | **0.550** | **0.149** | 0.388 | **1.30** | **no** |
| trigonelline | FRACTION_6 | 1.035 | 6.865 | 0.088 | **0.051** | 11.53 | — |
| trigonelline | CUP_CURVE_3 | 1.177 | **0.533** | **0.057** | 0.162 | **1.58** | **no** |
| 5CQA | FRACTION_6 | 1.035 | 4.603 | 0.126 | **0.087** | 7.97 | — |
| 5CQA | CUP_CURVE_3 | 1.523 | **0.464** | **0.086** | 0.229 | **1.24** | **no** |

**The localisation ordering reverses between the two tolerance conventions** — the relative band
scales with each arm's own `J_min`, which is ~9× larger for fractions. Neither margin reaches the
0.5-decade bar (largest 0.249), so localisation separates nothing. Held-out prediction does, and it
is convention-free.

`CUP_FINAL_1` returns `J_min = 0` and a flat profile for all three solutes, exactly as proved.
**0 of 3** solutes materially improved; confirmed by the log-RMSE objective and by the 45-shot
all-grinds sensitivity.

## 4. The decisive plots

| figure | what it settles |
|---|---|
| `figures/endpoint_summary_six_panel.png` | Part A: only Arabica:5CQA is clearly excluded; two Robusta profiles are flat to the domain edge |
| `figures/operator_localisation_vs_heldout.png` | **the decisive one** — the held-out axis separates the arms by 5–10 pp for every solute |
| `figures/operator_accepted_width.png` | 10 %-relative widths; note the ordering reverses under the 0.25 pp absolute convention, so this axis settles nothing |
| `figures/operator_loeo_kappa.png` | both operators pin `κ` stably; the difference is not fold noise |
| `figures/operator_heldout_shape.png` | the fraction-fitted rate predicts the held-out cup curve worse |

## 5. Selected branch

```
STOP_PAPER_1_AND_REPURPOSE
```

Applying the declared branch rules in order:

- **`PROCEED_STRONG_PAPER`** requires Part A to give `H1_STRONG` or `H1_QUALIFIED` **and** ≥2/3
  solutes materially improved. Part A gives `H1_DOES_NOT_LEAD`; 0/3 improved. **Fails both limbs.**
- **`PROCEED_NARROW_OBSERVATION_DESIGN_PAPER`** requires ≥2/3 solutes materially improved even
  though Part A does not lead. **0/3 improved. Fails.**
- **`INCONCLUSIVE_REQUIRES_NEW_DATA`** applies only when the source mapping or a model discrepancy
  *prevents* a defensible comparison. The comparison ran cleanly: a complete 48-shot intersection,
  3 documented exclusions, both arms finite and uncensored, 0 failed fits, and agreement across two
  objectives, two level policies and two shot sets. **The comparison is defensible; the answer is
  simply negative.**
- **`STOP_PAPER_1_AND_REPURPOSE`** is what remains. Its stated condition is Part A mostly
  endpoint-excluded or indeterminate **and** fractions not materially improving ≥2 solutes. The
  second limb holds outright. On the first, I should be precise rather than generous: at the 10 %
  relative convention 3 of 6 groups are excluded-or-indeterminate — exactly half, not a majority —
  while 4 of 6 fail the programme rule. **This is the branch the rules select, and the first limb is
  satisfied on the programme rule rather than on a strict majority of 10 %-relative classifications.**

## 6. The strongest defensible thesis that survives

Not a Paper 1 headline, but real and worth writing down:

> On this campaign and within this declared model, six-fraction time-resolved measurements do not
> determine the mass-transfer-rate multiplier better than a three-point cumulative cup curve — the
> comparison depends on which tolerance convention is used and neither margin is material — and they
> predict held-out extraction 5–10 percentage points worse. The fraction-resolved data are not less
> informative in principle: they expose a structured late-time misfit (the model under-predicts by up
> to 9 % at fractions 7 and 10) that cumulative averaging conceals to within ±0.5 %.

The intuition that motivated Paper 1 — that aggregate cup measurements discard kinetic information
that time-resolved sampling would recover — is **contradicted by the only matched dataset available
to test it**, and the reason is that the model cannot reproduce the temporal shape it would need to
exploit.

## 7. Claims that must be abandoned

1. **That time-resolved observations recover rate information whole-cup measurements discard.**
   Measured, on matched shots, same model: no material improvement for any solute, and worse held-out
   prediction. This was H1's motivating intuition.
2. **That the large-rate endpoint is broadly operationally acceptable.** Four of six groups fail;
   Arabica:5CQA is excluded under four of five conventions.
3. **Any universal weak-localisation headline.** Both operators localise `κ` to within 0.06–0.18
   decades here — sharply. Weak localisation is a property of the *Angeloni* nine-condition
   whole-cup design, not of espresso extraction or of cup measurement as such.
4. **That the observation-design contribution can lead a paper.** The negative control is the only
   arm that behaves as the design narrative predicted, and it does so by construction.
5. **Any threshold-based endpoint claim at the current precision.** The decisive margins are
   0.02–0.06 pp against campaign repeatability published only as 0.3–19.7 % ranges at `n ≈ 2`. The
   verdicts are numerically resolved and empirically arbitrary.

## 8. Minimum next scientific work

In priority order, and all of it solver-side rather than governance-side:

1. **Diagnose the late-time misfit.** The residual is structured, one-signed and up to 9 %. Candidate
   causes worth separating: an over-fast decay in the two-grain closure, an inadequate fines/PSD
   representation, and evolving permeability. This is the only lead in the whole screen that points
   at a model improvement with a measurable target.
2. **Recover per-solute replicate uncertainty** for Angeloni (author contact; the template already
   exists at `puckworks/data/angeloni2023/replicate_uncertainty_template.csv`). Without it no
   endpoint threshold verdict at 0.02–0.06 pp margins can be defended.
3. **Estimate the within-shot fraction correlation** from Schmieder Supplementary S1
   (DOI `10.17632/y2tz67f6ry.1`). Protocol V2 §6 declares `ρ = 0.6` with no measurement behind it,
   and it drives the resource-equated budget comparison as much as the cost vector does.
4. **Recover per-grind `psi`/`d_s2`** so GL 1.4 and 2.0 stop running on centre-grind parameters.
5. Only after 1–4: revisit whether an observation-design question is worth asking again, with a model
   that can reproduce the shape.

## 9. No further governance work should begin

**No further governance, assurance, protocol, ledger, freeze, activation, novelty or manuscript work
should begin until the user has reviewed this scientific result.** The formal machinery is in good
order and is not the bottleneck: P0-G0, P0-G8, P0-G7 and P0-G9 all remain open, the plan remains a
candidate, and `PAPER_A_ASYMPTOTIC_PROFILE_LIMITS.json` was never created. What has changed is that
the scientific case those gates were built to protect has not survived contact with the data, and
continuing to harden the machinery around it would be the most expensive possible way to avoid that
conclusion.
