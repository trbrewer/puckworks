# Part B — do fraction-resolved observations localise the rate better than cup observations?

```
EXPLORATORY_SAME_CAMPAIGN_VIABILITY_SCREEN
NOT_A_FROZEN_P0_GATE_RESULT
```

**gate_binding:** `null` · **date:** 2026-08-03 · **data:**
`PAPER_A_VIABILITY_OBSERVATION_OPERATOR_V1.json` · **manifest:**
`PAPER_A_VIABILITY_MATCHED_DATA_MANIFEST_V1.json` · **producer:**
`tools/paper_a_viability_operator.py` · **figures:** `figures/operator_*.png`

**Same-campaign.** The model parameters were originally fitted in this source lineage. This is an
observation-operator study, not independent physical validation.

---

## The answer

**No.** **0 of 3 solutes** meet the declared material-improvement rule, under every objective, level
policy and shot set tried.

The localisation half of that answer is **convention-dependent and therefore weak evidence in either
direction** — see the correction below. The prediction half is not: fractions cost 4.9–10.0
percentage points of held-out temporal accuracy against an allowance of 0.5 pp, under every
convention, and that is what settles it.

## Matched evidence unit

Built as the exact `experiment × replicate × solute` intersection of `raw_fractions.csv` (Table S1)
and `cup_masses.csv` (Table S3). **45 shots admitted, 3 excluded**, nothing imputed:

| excluded | reason |
|---|---|
| exp 2 rep 3 | fraction set `[1,3,5,7,10]` — fraction 2 concentrations missing |
| exp 5 rep 3 | fraction set `[1,3,5,7,10]` — fraction 2 concentrations missing |
| exp 10 rep 1 | fraction set `[1,3,5,7,10]` — fraction 2 masses missing |

`mass_accumulated_g` is the interval **midpoint** mass (verified: fraction 1 midpoint = mass/2), so
each window is `[mid − mass/2, mid + mass/2]` in cumulative beverage grams, converted to time by the
measured flow. The measured fractions 1,2,3,5,7,10 are **not contiguous**. Cup targets follow the
source's 20 g dose: BR 1/1 = 20 g, 1/2 = 40 g, 1/3 = 60 g.

**Grind.** The port declares grain parameters (`psi`, `d_s2`) for the **centre grind only** — they
are fitted per grind (1.4/1.7/2.0) but the per-experiment assignment is opaque in the source. The
primary analysis therefore uses the **16 GL 1.7 shots across 5 experiments**, where the declared
parameters are the actual grind's. All 45 shots are run as a sensitivity under the port's documented
centre-grind approximation.

## Primary result — GL 1.7, shot-balanced MAPE, exact per-shot level

| solute | arm | `κ*` | `J_min` (pp) | accepted width (decades) | status | held-out MAPE (pp) |
|---|---|---|---|---|---|---|
| caffeine | FRACTION_6 | 1.035 | 4.498 | 0.180 | finite | 6.21 |
| caffeine | **CUP_CURVE_3** | 1.732 | **0.550** | **0.149** | finite | **1.30** |
| trigonelline | FRACTION_6 | 1.035 | 6.865 | 0.088 | finite | 11.53 |
| trigonelline | **CUP_CURVE_3** | 1.177 | **0.533** | **0.057** | finite | **1.58** |
| 5CQA | FRACTION_6 | 1.035 | 4.603 | 0.126 | finite | 7.97 |
| 5CQA | **CUP_CURVE_3** | 1.523 | **0.464** | **0.086** | finite | **1.24** |

Every profile is finite — neither arm is censored at either domain edge, and no fold hit the right
boundary. Leave-one-experiment-out gives 5 folds per arm with 0 failed fits; fold-to-fold `log₁₀κ`
spread is ≤ 0.11 decades for every arm and solute, so both operators pin the rate stably.

### The declared material-improvement rule

| solute | width reduction | ≥ 0.5 decades narrower? | censored → finite? | held-out penalty | **materially more localising?** |
|---|---|---|---|---|---|
| caffeine | −0.031 | no | no | +4.91 pp | **no** |
| trigonelline | −0.031 | no | no | +9.95 pp | **no** |
| 5CQA | −0.040 | no | no | +6.73 pp | **no** |

A negative width reduction means the **cup** set is narrower under the 10 % relative convention.

### Correction — the localisation ordering reverses under the absolute convention

The 10 % relative band scales with each arm's own `J_min`, and the fraction arm's `J_min` is about
nine times larger, so its relative band is about nine times wider in absolute terms. That is a
property of the tolerance convention, not of the operator. Under the **0.25 pp absolute** convention,
which does not scale, the ordering **reverses**:

| solute | FRACTION_6 width (dec) | CUP_CURVE_3 width (dec) | narrower |
|---|---|---|---|
| caffeine | **0.139** | 0.388 | fraction, by 0.249 |
| trigonelline | **0.051** | 0.162 | fraction, by 0.112 |
| 5CQA | **0.087** | 0.229 | fraction, by 0.142 |

So the honest statement is: **under a relative tolerance the cup curve localises better; under an
absolute tolerance the fraction curve does; neither margin reaches the declared 0.5-decade bar**
(the largest is 0.249). Localisation alone does not separate these operators.

What does separate them is held-out prediction, and it is convention-free: fractions are worse by
4.9–10.0 pp against a 0.5 pp allowance. **Fractions therefore fail the rule on the second limb
regardless of which tolerance convention is used**, and the material-improvement verdict is 0/3
either way.

## The negative control behaves exactly as proved

`CUP_FINAL_1` returns `J_min = 0.0` exactly and a flat profile for all three solutes. With one
observation and one free level the exact MAPE minimiser is `I* = y/f(κ)`, so `|I*f(κ) − y| = 0`
identically at every `κ`. The profile carries no rate information **by construction**, and it is not
counted as evidence that any arm "won".

## Sensitivities all agree on the verdict

| sensitivity | result |
|---|---|
| **log-RMSE objective** | cup narrower for all three solutes under its relative band (0.146 vs 0.156; 0.063 vs 0.097; 0.087 vs 0.105) — same ordering as the primary relative convention |
| **all 45 shots, 15 experiments** (centre-grind approximation) | 0/3 materially improved; held-out penalty 5.9–10.1 pp |
| **common level per solute** | labelled assumption sensitivity; widens every set, does not reverse the ordering for trigonelline or 5CQA |

## Positivity — recorded, not clipped

At high `κ` the bed is exhausted before the late fractions, so late interval-average predictions
reach zero and then go slightly negative. That is a hard failure of the positivity precondition. Those
`κ` are **excluded and recorded**, never clipped:

| solute | FRACTION_6 valid grid | valid `κ` range | first violation | accepted set inside valid range? |
|---|---|---|---|---|
| caffeine | 46/64 | [0.15, 56] | 49.3 | yes — minimiser 1.68 decades below |
| trigonelline | 36/64 | [0.15, 13.6] | 15.5 | yes — minimiser 1.17 decades below |
| 5CQA | 43/64 | [0.15, 33.5] | 38.1 | yes — minimiser 1.57 decades below |

`CUP_CURVE_3` has no violations anywhere on the grid. Every accepted set lies strictly inside the
valid range, so the headline comparison is unaffected. **This defect was found by a `NaN` in the
log-RMSE sensitivity, not by design** — the primary MAPE path had been silently averaging over
negative predictions before positivity was enforced.

## Why fractions lose — it is misfit, not information

The mean signed relative residual at each arm's own best `κ` shows the mechanism:

| solute | f1 | f2 | f3 | f5 | f7 | f10 |
|---|---|---|---|---|---|---|
| caffeine | −2.5 | −0.0 | −0.1 | −2.3 | −4.6 | +0.2 |
| trigonelline | −2.5 | +0.1 | −1.8 | −0.8 | −6.3 | −9.3 |
| 5CQA | −3.1 | −0.9 | −1.8 | +0.2 | −4.6 | −2.0 |

against the cup curve:

| solute | BR 1/1 | BR 1/2 | BR 1/3 |
|---|---|---|---|
| caffeine | +0.21 | −0.17 | +0.28 |
| trigonelline | +0.17 | −0.06 | +0.50 |
| 5CQA | +0.24 | −0.06 | +0.34 |

The fraction residuals are **structured and concentrated in the late fractions**, where the model
under-predicts by up to 9 %: the observed extraction has a heavier tail than the model produces. The
misfit is *not* confined to the earliest brew that the source itself flags. Cumulative averaging
hides this almost completely — cup residuals are within ±0.5 %.

So the extra fraction observations do not buy rate information; they mostly buy **model misfit**. The
model fits cumulative cup concentrations about ten times better than it fits the fraction-resolved
time series, and the rate estimate that best reproduces the shape is not better determined for it.

**This is a finding about the declared model, not an information-theoretic statement about
observation operators.** A model that reproduced the temporal shape could still make fractions the
more informative operator; this campaign cannot tell us, because this model does not.

## Figures

| file | content |
|---|---|
| `figures/operator_profiles_by_solute.png` | rate profiles, three arms per solute |
| `figures/operator_accepted_width.png` | accepted-set widths — narrower is better localised |
| `figures/operator_loeo_kappa.png` | fold-to-fold `log₁₀κ` stability |
| `figures/operator_heldout_shape.png` | held-out cup curves, level anchored on the first observation only |
| `figures/operator_localisation_vs_heldout.png` | the decisive plot: cup is down-left of fractions on both axes for every solute |

## Caveats

- Single bean, machine and grinder; grind dial is not a PSD; coefficients are box-specific.
- Model parameters were fitted in this source lineage — same-campaign, not independent validation.
- 16 shots / 5 experiments in the primary set; 45 / 15 in the sensitivity.
- The GL 1.4 and GL 2.0 shots run on centre-grind parameters, a documented approximation of the port.
