# Paper A — pivot analysis protocol, version 2

**Gate:** P0-G0. **Not yet frozen.** Freezes only at freeze commit F, after the acceptance checklist
in `PAPER_1_P0_G0_PROTOCOL_FREEZE_DECISION_20260802.md` §10 is satisfied.
**Operative plan:** `PAPER_1_PIVOT_AND_REDRAFT_PLAN_V2_2_1.md`
**Manifest:** `PAPER_A_PLAN_MANIFEST_V1.json`
**Supersedes:** `PAPER_A_PIVOT_ANALYSIS_PROTOCOL_V1.md`, retained as a classified historical draft.
**Deviation policy:** append-only. Every later change is dated, justified, and carries an impact
statement. Deviations are never absorbed silently.

---

## 0. The statement that accompanies every result

> **This protocol was frozen after exploratory inspection of the existing campaign.** It limits
> further analytical flexibility and selective reporting. It does **not** provide independent
> confirmation of hypotheses generated from the same data.

Evidential labels, used verbatim in the manuscript:

| label | meaning | applies to |
|---|---|---|
| **post-selection frozen reanalysis** | same campaign, protocol frozen after the hypothesis formed | P0-G4, G5, G6, G8, G9 |
| **prospective model-based study** | synthetic, declared model, no empirical claim | P0-G7 |
| **cross-fitted prospective-protocol emulation** | scored condition excluded from map construction, same campaign | P0-G9 variants |
| **genuinely prospective empirical test** | data collected after this freeze | **none exists** |

---

## 1. Global conventions

### 1.1 Objectives

**Primary:** MAPE, expressed in **percentage points**, with the level minimised exactly:

```
MAPE(I, κ) = (100/n) · Σ_i (f_i(κ)/y_i) · |I − y_i/f_i(κ)|
```

so the minimiser over `I` is any weighted median of `r_i = y_i/f_i(κ)` with weights
`w_i = f_i(κ)/y_i`. Units are percentage points throughout; the factor 100 does not change the
minimiser but fixes the units of every tolerance below.

**Sensitivity family:** relative-L2, SSE, Huber (δ = 1.345·1.4826·MAD at the SSE optimum). These are
**sensitivity objectives, not interchangeable likelihoods.** No probabilistic statement follows from
any of them.

**Positivity precondition.** Both `y_i > 0` and `f_i(κ) > 0` are required. Any violation is a
**hard failure**, recorded and reported; it is never silently dropped.

**Tie handling.** When the weighted-median minimiser is an interval `[I_lo, I_hi]`, the **returned
representative is `I_lo`** (the lower weighted median), and the **entire interval is retained in the
archive**. Objective values are identical across the interval by construction, so the choice cannot
move `J`; it is fixed only so the reported `I` is deterministic.

### 1.2 Determinism

Seeds fixed per analysis and recorded. Environment, package versions, input paths and SHA-256 hashes
recorded in every archive. Failures are logged and retained, never dropped or silently retried.

### 1.3 Estimand tags

`FULL-PUB`, `FULL-WIDE`, `LOCO-PUB`, `LOCO-WIDE`, `NUM-FULL`. Every reported number carries exactly
one. **No number migrates between tags without a like-for-like re-run.**

### 1.4 Aggregation

Macro mean over the six variety–solute groups within a grind. Pooled = equal-weight mean of coarse
and fine **within each fold**. Fold summaries are medians over nine **dependent** folds. **The pooled
median is never reconstructed from component medians** — median is not linear.

---

## 2. P0-G8 — asymptotic classification

This is the first gate to run and the one that can reverse H1. Its contract is therefore complete
here, per the adjudication §7.

### 2.1 Data and evidence unit

| item | frozen value |
|---|---|
| input | `puckworks/data/angeloni2023/bioactives.csv`, SHA-256 recorded in the freeze record |
| rows | the 66 corpus rows; the calibration support is the **on-grid optimal-grind** subset |
| groups | **six**: {Arabica, Robusta} × {caffeine, trigonelline, 5-CQA}. Columns `CF`, `TR`, `5CQA` |
| calibration conditions | the nine on-grid (T, p) optimal-grind conditions per variety |
| unit of analysis | the **variety–solute group**. There is no pooling inside P0-G8 |
| positivity | `y_i > 0` and `f_i(κ) > 0` required; violation is a hard failure |
| missing values | none permitted in the calibration support; a missing cell is a hard failure |
| ties | §1.1 |

No group may be added, removed, merged or reweighted after any output is inspected, without a dated
deviation record.

### 2.2 Parameter domain and endpoint

```
classification domain:  κ ∈ [0.15, ∞]        (compactified; ∞ is an included endpoint)
PUB grid:               geomspace(0.15, 6.5, 18)     — finite diagnostic grid only
WIDE grid:              geomspace(0.15, 500, 40)     — finite diagnostic grid only
κ = ∞:                  ANALYTICAL endpoint via §2.4. NOT approximated by κ = 500
```

The lower bound `κ = 0.15` is **inherited support from the published rate domain, not part of the
inferential claim**; components touching it are reported as lower-censored and no statement is made
about `κ < 0.15`.

**Right-censoring at a finite cap is never called unboundedness.** The only statement that may be
made about the upper tail comes from the `κ = ∞` endpoint via §2.5.

### 2.3 Exact objective definitions

```
J(κ)    = min over I > 0 of MAPE(y, I · f(κ))          — exact weighted median
J_min   = inf over κ ∈ [0.15, ∞] of J(κ)               — includes the endpoint
J_inf   = min over I > 0 of MAPE(y, I · f_inf)         — exact weighted median at the limit
```

`J_min` is taken over the **compactified domain including `κ = ∞`**, so `J_min ≤ J_inf` always. A
`J_min` attained only at the endpoint is recorded as such.

### 2.4 Limit construction — primary method fixed now

**Primary: analytical operator limit with a derived remainder bound.**

For fixed condition, the semi-discrete system is linear: `dz/dt = A(κ) z` with
`A(κ) = A₀ + κ·A₁`, where `A₁` carries the interphase-transfer terms (they scale linearly in the
multiplier through the Sherwood prefactors) and `A₀` carries advection and the accumulation rows.
The limit `f_inf` is obtained from the singularly-perturbed limit of that pencil: as `κ → ∞` the
fast subspace is driven to the local-equilibrium manifold `ker(A₁)` and the reduced dynamics act on
the slow complement. `f_inf` is computed by projecting onto `ker(A₁)` and integrating the reduced
operator, with a remainder bound derived from the spectral gap of `A₁` restricted to the fast
subspace.

**Verification control (not an alternative):** a high-`κ` numerical sequence
`κ ∈ {10², 10³, 10⁴, 10⁵, 10⁶}` evaluated by the exact-in-time matrix exponential. It must converge
to the analytical `f_inf` within the remainder bound. **If the analytical route cannot be completed,
the gate returns `limit_construction_failed`; the numerical sequence must not be promoted to primary
after the fact.**

**Coverage.** The construction is applied and verified at **every declared calibration condition and
every group** — nine conditions × two varieties × three solutes. The existing `NUM-TIME-01`
centre-condition, three-solute time-integrator check is **supporting control evidence only** and is
explicitly not a substitute.

### 2.5 Verified intervals and classification

All three quantities are reported as intervals, never as a scalar with an informal tolerance:

```
J_min ∈ [L_min, U_min]
J_inf ∈ [L_inf, U_inf]
T     ∈ [L_T,   U_T]
```

Tolerance families, both applied:

```
relative:  T_rel(q) = (1 + q) · J_min,   q ∈ {0.05, 0.10, 0.20}
absolute:  T_abs(a) = J_min + a,         a ∈ {0.10, 0.25} percentage points
```

The threshold interval **propagates the `J_min` interval**: `T_rel(q) ∈ [(1+q)L_min, (1+q)U_min]`,
`T_abs(a) ∈ [L_min + a, U_min + a]`.

**Classification, per group per convention:**

```
U_inf < L_T   ->  tail_included
L_inf > U_T   ->  tail_excluded
otherwise     ->  boundary_indeterminate
```

Interval comparison is used in preference to a single pooled `ε`, because no proof that a pooled
bound is conservative has been produced.

**Near-zero `J_min`.** If `U_min < 0.05` pp the relative convention is declared unstable for that
group and **only the absolute convention is used**; this is predeclared because noiseless synthetic
controls can drive `J_min → 0`.

### 2.6 Error budget

Every component gets either a verification test or an explicit conservative bound. **Display
precision is never an error estimate.** Components combined by interval arithmetic (not in
quadrature, which would assume independence that has not been established):

| component | source | bound |
|---|---|---|
| asymptotic remainder | §2.4 spectral-gap bound | derived, per condition |
| spatial discretisation | mesh refinement 100/200/400 at fixed `κ` | observed max deviation, ×2 safety |
| exact-profile arithmetic | weighted-median tie width | interval width, exact |
| global minimum isolation | §2.7 bracketing tolerance | algorithmic, declared below |
| floating point | double precision on the declared operator sizes | 1e-11 relative, from the `NUM-TIME-01` noise-floor measurement |
| shoulder derivative | central difference, step-convergence | max step-to-step change |

`L_min = J_min_hat − Σ bounds`, `U_min = J_min_hat + Σ bounds`, and likewise for `J_inf`.

### 2.7 Global profile topology

No assumption of a single minimum or monotone tails. Frozen algorithm, on `log κ` over the finite
portion:

1. evaluate `J` on the WIDE grid;
2. bracket every sign change of `J(κ) − T` between adjacent grid points;
3. refine each bracket by bisection to `|Δ log κ| < 1e-4`;
4. detect **tangencies** — a local minimum of `J − T` within `1e-3·T` of zero without a sign change —
   and mark the interval `unresolved` rather than merging or discarding it;
5. report **every** connected component of `{κ : J(κ) ≤ T}`;
6. flag components touching `κ = 0.15` as **lower-censored**;
7. represent a component adjoining `κ = ∞` **explicitly** as `[κ_c, ∞]`, admitted only when the §2.5
   endpoint classification is `tail_included`;
8. if any bracket fails to refine, or a tangency remains unresolved, the group returns
   **`topology_unresolved`** — never a single interval by default.

### 2.8 Response shoulder

The shoulder is **descriptive model sensitivity and is not the objective-profile boundary.** The two
are reported separately and never conflated.

| item | frozen value |
|---|---|
| derivative | `s(κ) = ∂ log ŷ / ∂ log κ`, central difference, step 0.08 in `log κ`, with half/double step-convergence |
| inventory | held **fixed** at the group's `J_min` level (not re-profiled), so the quantity is a pure model-response sensitivity |
| aggregation | **maximum absolute** `s` over the declared outputs at that condition — identifies where **all** outputs are weakly sensitive |
| primary threshold | **0.05** |
| sensitivity family | {0.10, 0.05, 0.01} |
| crossing rule | smallest `κ` above which `max_out |s| < threshold` for all larger grid points; located by bisection to `|Δ log κ| < 1e-3` |
| no crossing | `shoulder_not_reached` within the WIDE grid — reported, not extrapolated |
| multiple crossings | all reported; the **largest** is the shoulder, and the multiplicity is flagged |

The threshold family is declared here so that a member cannot be chosen afterwards for agreement
with `J_inf`.

### 2.9 Group and programme-level decision rules

Per group, per convention, the outcome is one of: `tail_included`, `tail_excluded`,
`boundary_indeterminate`, `topology_unresolved`, `limit_construction_failed`.

**Programme-level rule, frozen:**

> **H1 may lead the paper only if the classification is `tail_included` for at least five of six
> groups under the 10 % relative rule AND under at least one absolute rule, with no group classified
> `tail_excluded` and no group in `topology_unresolved` or `limit_construction_failed`.**
>
> Otherwise the paper reports group-specific and threshold-dependent results and H1 does not lead.

Enumerated consequences:

| outcome | consequence |
|---|---|
| all six included, both conventions | H1 leads; state the operational scope explicitly |
| five of six included, no exclusions | H1 leads; the exception is reported by name in the same sentence |
| any group excluded | H1 does not lead; the response limit and threshold dependence lead instead |
| any boundary-indeterminate | H1 does not lead; the indeterminacy is reported as a result |
| classification changes across conventions | reported as **threshold-dependent**; H1 does not lead |
| any numerical failure | H1 does not lead until the failure is resolved or explicitly scoped |

### 2.10 Archive and reproducibility contract

`PAPER_A_ASYMPTOTIC_PROFILE_LIMITS.json` records: protocol version; frozen-content commit; producer
path and SHA-256; exact command; environment and package versions; every input path and SHA-256;
group definitions; the full objective and tolerance specification; method and error-budget
identifiers; `J_min`, `J_inf`, thresholds and all intervals; every connected component; shoulder
results including the family; per-group classification under **every** convention; all failures and
warnings; the branch consequence from §2.9; the archive's own hash; and a **substantive**
verification command.

**A file-existence check is not reproduction.** The producer exposes `--verify`, which recomputes
the group-level classification from archived inputs and compares semantically, and `--exists`, which
does not.

---

## 3. P0-G6 — RSI admission

| item | frozen value |
|---|---|
| RSI formula | `RSI = sqrt(Var_w(s))` with `s_i = ∂ log f_i/∂ log κ`; companion `RSI_total = sqrt(Σ w_i (s_i − s̄_w)²)` reported always |
| primary quantity | **`RSI`** (per-observation). `RSI_total` is reported but is not the ranking statistic |
| weights | **uniform `w_i = 1`**, declared fixed; a relative-scale weighting is reported as a sensitivity only |
| designs | `full_grid_9`, `isothermal_T88/T93.4/T98`, `isobaric_p6/p9/p12`, `corners_2`, `diagonal_3`, `single_condition` (must score 0) |
| `κ` locations | `κ = 1` (nominal); each group's `J_min` argmin (group-specific); and the §2.8 shoulder |
| derivative | central difference, step 0.08 in `log κ`, half/double convergence; unresolved if the change exceeds 5 % of the spread |
| profile width | log-width of the 10 %-relative near-optimal set of the **exact MAPE** profile |
| censoring | right-, left- and doubly-censored profiles are **excluded from the ranking** and reported separately; a group with fewer than **five** evaluable designs is `insufficient_designs` |
| statistic | **Kendall `τ_b`** between RSI and inverse profile width, ties handled by `τ_b` |
| admission | `τ_b ≥ 0.40` with at least **eight** evaluable pairs, in **≥ 5 of 6** groups, at **both** `κ = 1` and the group optimum |
| positive control | a synthetic family with `f_i(κ) = κ^{p_i}` and prescribed spread, where the surrogate must rank correctly |
| negative control | a family constructed so the weighted median switches across `κ`, where the smooth surrogate is expected to fail |

Every group and design is reported regardless of admission. A "positive but negligible" association
does not admit RSI: the `τ_b ≥ 0.40` floor is the point.

---

## 4. P0-G9 — target-map protocol

| item | frozen value |
|---|---|
| map families | (a) current campaign-conditioned; (b) common O-grind; (c) **scored-condition-excluded (cross-fitted)**; (d) limited-adaptation at *n* target measurements; (e) physics-only Darcy form |
| exclusion unit | the **scored condition and every upstream quantity fitted using it** — including the per-granulometry conductivity polynomial and the nominal shot time. Removing only the final row while retaining a polynomial fitted with it **leaks** and is prohibited |
| raw-support sufficiency | a cross-fitted map is constructible when ≥ 3 hydraulic observations remain at the target granulometry after exclusion; otherwise the variant is `not_constructible` |
| adaptation counts | `n ∈ {0, 1, 2, 3, all}` |
| placements | frozen: extremes-first by pressure, then temperature — **never selected using any chemical outcome** |
| selection | nested entirely within hydraulic/calibration support |
| uncertainty | conductivity-polynomial coefficient covariance propagated by linearisation; shot-time uncertainty ±10 % as a declared sensitivity |
| extrapolation leverage | fraction of target residence times outside calibration support, and the largest gap in calibration spans |
| impossibility criterion | if (c) is `not_constructible` for any variety, **H3 remains retrospective**, is removed from title and contribution list, and no prospective language is used |

Same-campaign cross-fitting is labelled **cross-fitted prospective-protocol emulation** even if the
result survives. It is not independent prospective validation.

---

## 5. P0-G5 — estimation policy and propagation

**Axis A — point estimation.** Free-WIDE fit; fixed anchors `κ ∈ {0.5, 1, 2}`; regularised fit.

| item | frozen value |
|---|---|
| regularisation coordinate | **`log κ`** — dimensionless, so a single `λ` grid is meaningful |
| penalty | `J(κ) + λ · (log κ)²`, with `J` in percentage points |
| `λ` grid | `{0.01, 0.1, 1, 10}` |
| tuning branch | **frozen no-tuning grid.** Every candidate is reported; no post hoc winner is selected. Nested selection is *not* used, because with nine conditions it is unstable and that instability would itself require adjudication |
| level | re-profiled exactly under **every** policy |

**Axis B — propagation.** Point only; operational-profile envelope; objective-family envelope.
Envelopes are constructed by evaluating predictions at every `κ` in the near-optimal set — **all
connected components, and the full weighted-median interval at each** — and reporting the min–max
span. **No coverage or confidence interpretation attaches.**

**Dominance.** Policy *A* dominates *B* only if `A` is better on **coarse and fine and pooled**, in
**≥ 7 of 9** folds. Otherwise the result is **no winner**, which is a legitimate and reportable
outcome.

Axis A and Axis B are never ranked against each other.

**H4 wording is generated from the P0-G8 outcome**, not chosen: if P0-G8 returns `tail_included` for
the programme, H4's antecedent is satisfied and the localisation clause applies; otherwise only the
physical-interpretation clause applies. Both branches are written now, in the plan, and neither is
edited after the result.

---

## 6. P0-G7 — observation-operator study

| item | frozen value |
|---|---|
| generator | the declared model at fixed parameters for stages 1–3; a **perturbed generator** for stage 4 (mismatch), so the fitted model is not the data-generating model |
| true `κ` | `{0.5, 1, 2, 6.5, 50}` — below, at, and beyond the shoulder |
| true `I` | `{0.5, 1, 2}` × the group level |
| operators | (a) one whole cup per condition; (b) multiple endpoints 20/40/60 g from matched shots; (c) fractionated at the Schmieder windows; (d) combined (b)+(c) — **included, not optional** |
| noise | shot-to-shot lognormal σ = 0.03; within-shot fraction correlation ρ = 0.6; assay lognormal σ = 0.02; flow/endpoint σ = 0.02; map coefficient covariance from §4 |
| mismatch | separate coarse/fine multipliers (ratio 1.3); time-varying flow (±15 % linear ramp); wrong map (O-grind map applied to target); each at a declared magnitude |
| resources | cost vector: 1 shot = 1.0; 1 assay = 0.4; 1 fraction sample = 0.15. Budget levels `{10, 20, 40}` units |
| replicates | 200 per cell; seeds `0…199` |
| metrics | `κ` bias and RMSE; profile width; boundary/censoring rate; prediction error; optimisation failure rate |
| positive control | noiseless, rich design must recover `κ` to within 2 % and `I` to within 1 % — failure is a **pipeline defect**, not a finding |
| success | an operator "improves recovery" if median `κ` RMSE is lower at **equal budget** in ≥ 4 of 5 true-`κ` values |
| inconclusive | if no operator meets that bar, the study returns `inconclusive` and the observation-compression narrative is not asserted |

---

## 7. P0-G4 — LOCO-WIDE factorial

```
arms (4: M0, M1, M2, empirical)
  × map protocols (2: campaign-conditioned, cross-fitted)
  × objectives (2: MAPE primary, relative-L2 sensitivity)
  × folds (9 leave-one-optimal-condition-out)
  × policy branches (3: free-WIDE, fixed κ=1, regularised λ=1)
  = 4 × 2 × 2 × 9 × 3 = 432 cells
```

Expected run count **432**. Allowed failure states: `optimiser_boundary`, `positivity_violation`,
`map_not_constructible`. Retry policy: **none** — a failed cell is retained and reported. Failure
retention is mandatory; the archive row count must equal 432 including failures.

---

## 8. Withdrawal rules

| if | then |
|---|---|
| P0-G8 excludes the tail, or classification is threshold-dependent | H1's broad headline is removed; the response limit and threshold dependence lead |
| P0-G8 returns any `topology_unresolved` or `limit_construction_failed` | H1 does not lead until resolved or explicitly scoped |
| RSI fails `τ_b ≥ 0.40` in ≥ 5/6 groups | design-ranking claims removed; algebra and exact profiling retained |
| the cross-fitted map is `not_constructible`, or the coarse benefit collapses | H3 demoted to retrospective case study; removed from title and contributions |
| no policy dominates | H4 reports "no winner"; no recommendation is made |
| the observation-operator study returns `inconclusive` | the compression narrative is not forced; branch to structural compensation or design adequacy |
| P0-G10 finds the contribution too narrow | narrow, split, or terminate; a positive novelty finding is not required |

---

## 9. Reporting rules

- Every pooled figure appears with its coarse/fine components and weighting rule **on the same page**.
- No adjective without a declared comparator. "Competitive", "useful", "large", "strong" are banned
  unqualified. Report the number.
- No causal "because" linking the map to predictive stability until a mechanism is tested.
- Dependent folds are described as such; no binomial probability, standard error on `n = 9`, or
  significance language attaches to sign counts.
- The operational near-optimal set is never called a confidence set, credible interval, or
  coverage-calibrated statement.
- Every archive records its estimand tag, evidence type, seeds, hashes and failure counts.
