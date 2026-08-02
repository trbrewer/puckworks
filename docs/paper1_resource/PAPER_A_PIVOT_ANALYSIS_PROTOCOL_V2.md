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

`FULL-PUB`, `FULL-WIDE`, `FULL-WIDE-ENDPOINT`, `LOCO-PUB`, `LOCO-WIDE`, `NUM-FULL`. Every reported
number carries exactly one. **No number migrates between tags without a like-for-like re-run.**

| tag | meaning |
|---|---|
| **FULL-WIDE** | full optimal-grind calibration support, widened `κ` domain, **finite-domain results only** — no endpoint statement attaches |
| **FULL-WIDE-ENDPOINT** | full optimal-grind calibration support; threshold referenced to the continuously minimised profile on `D_WIDE = [0.15, 500]`; analytical `κ = ∞` endpoint evaluated separately |

A finite-domain scan keeps `FULL-WIDE`. Only a result whose threshold is referenced to `J_ref` *and*
which compares the separately constructed endpoint against it carries `FULL-WIDE-ENDPOINT`.

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

### 2.2 Reference domain and endpoint

```
D_PUB   = [0.15, 6.5]      published rate domain, retained for reference only
D_WIDE  = [0.15, 500]      the REFERENCE DOMAIN — finite, continuous, and closed
κ = ∞                      ANALYTICAL endpoint via §2.4, evaluated SEPARATELY.
                           NOT approximated by κ = 500 and NOT a member of D_WIDE
```

The previous edition of this section declared the classification domain to be the compactified
interval `[0.15, ∞]` while the only search it specified stopped at `κ = 500`. Those two statements
cannot both be operative, and the difference between them was being closed by narrative rather than
by a procedure. This edition replaces the unresolved global reference with a finite, continuous
reference domain plus a separate analytical endpoint. Each of the two has a procedure that returns
its own quantity, and neither is used to stand in for the other.

The lower bound `κ = 0.15` is **inherited support from the published rate domain, not part of the
inferential claim**; components touching it are reported as lower-censored and no statement is made
about `κ < 0.15`.

**Nothing is claimed about the open interval `(500, ∞)`.** No finite topology is assigned to it, no
connected component is reported inside it, and no finite tail onset is estimated. Those are
architectural facts about this protocol, recorded as `tail_onset_status = unresolved_by_design` and
`intermediate_domain_status = not_characterized_by_design`, and they are not findings. The endpoint
is used only to classify eventual behaviour relative to the WIDE-referenced threshold.

**Right-censoring at the finite domain edge is never called unlimited acceptance.** A component
reaching `κ = 500` is recorded as `upper_truncated_at_domain_edge`, which is a property of the
domain. The only statement that may be made about the upper tail comes from the `κ = ∞` endpoint
via §2.5, and — as §2.5 states — even that statement is conditional on a separate result.

### 2.3 Exact objective definitions

```
J(κ)    = min over I > 0 of MAPE(y, I · f(κ))          — exact weighted median
J_ref   = min over κ ∈ D_WIDE of J(κ)                  — the REFERENCE minimum
J_inf   = min over I > 0 of MAPE(y, I · f_inf)         — exact weighted median at the limit
```

`J_ref` is the **continuously minimised objective on `D_WIDE`, not the minimum of a diagnostic
grid**. §2.7 fixes the procedure that computes it; the minimum of the 40-point grid is never
reported as `J_ref`.

`κ = ∞` is **not** included in `J_ref`. The endpoint is a separate quantity, compared against the
threshold that `J_ref` generates. There is therefore no ordering relation asserted between `J_ref`
and `J_inf`: `J_inf < J_ref` is a legitimate outcome and is exactly what `endpoint_included` means.

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

### 2.5 Verified intervals, thresholds, and endpoint classification

All three quantities are reported as intervals, never as a scalar with an informal tolerance:

```
J_ref ∈ [L_ref, U_ref]
J_inf ∈ [L_inf, U_inf]
T     ∈ [L_T,   U_T]
```

Both threshold families, frozen, and both always applied:

```
relative:  T_rel(q) = (1 + q) · J_ref,   q ∈ {0.05, 0.10, 0.20}
absolute:  T_abs(a) = J_ref + a,         a ∈ {0.10, 0.25} percentage points
```

The threshold interval **propagates the `J_ref` interval**:

```
T_rel(q) ∈ [(1+q)·L_ref, (1+q)·U_ref]
T_abs(a) ∈ [L_ref + a,   U_ref + a]
```

Every objective and threshold interval is intersected with `[0, ∞)`.

**Endpoint classification, per group per convention:**

```
U_inf < L_T   ->  endpoint_included
L_inf > U_T   ->  endpoint_excluded
otherwise     ->  endpoint_indeterminate
```

Interval comparison is used in preference to a single pooled `ε`, because no proof that a pooled
bound is conservative has been produced.

**Near-zero `J_ref`.** If `U_ref < 0.05` pp the relative convention returns
`relative_threshold_not_applicable_near_zero` for that group; this is predeclared because noiseless
synthetic controls can drive `J_ref → 0`, where a ratio carries no tolerance. **The relative
convention is not silently replaced by an absolute one.** The absolute results stand on their own
and are reported as absolute results; the relative slot records that it does not apply.

**Eventual upper behaviour.** Given the separately required fixed-positive-time limit result, the
classification maps to:

```
endpoint_included       ->  wide_referenced_upper_set_unbounded
endpoint_excluded       ->  wide_referenced_eventually_excluded
endpoint_indeterminate  ->  upper_status_indeterminate
```

That mapping is **conditional**. The fixed-positive-time limit is a separate derivation and is not
closed by this protocol, so every archive records
`eventual_upper_precondition = fixed_positive_time_limit` together with its status. Until that
status is `established`, the enumerated value records the endpoint comparison and nothing more, and
no reader-facing text may convert it into a statement about arbitrarily large multipliers.

### 2.6 Quantity-specific error budgets

Every component gets either a verification test or an explicit conservative bound. **Display
precision is never an error estimate.** Components are combined by interval arithmetic (not in
quadrature, which would assume independence that has not been established).

**One pooled error sum is never reused across unrelated quantities.** Three disjoint budgets:

**2.6.1 Reference minimum**

| component | source |
|---|---|
| `E_ref_response` | model-response error at the evaluated `κ` |
| `E_ref_spatial` | mesh refinement 100/200/400 at fixed `κ`; observed max deviation, ×2 safety |
| `E_ref_profile_arithmetic` | floating-point cost of forming the objective at the exact weighted-median level |
| `E_ref_floating` | double precision on the declared operator sizes; 1e-11 relative, from the `NUM-TIME-01` noise-floor measurement |
| `E_ref_search` | the §2.7 deterministic search-convergence envelope |

```
U_ref = best evaluated/refined candidate + applicable evaluation error
L_ref = max(0, best evaluated/refined candidate − applicable evaluation error − E_ref_search)
```

where the *applicable evaluation error* is the sum of the first four components. This is a
**deterministic numerical convergence envelope, not a mathematically certified global interval**:
an evaluated candidate really does bound the minimum from above, while the lower side records how
the refinement sequence settled and is not a proof that no lower basin exists off the sampled set.

`E_ref_profile_arithmetic` is **not** the weighted-median tie width. The objective is exactly
constant across the tie interval, so the tie width is inventory-level identification information in
inventory units and contributes no percentage-point error at all. The previous edition of this
table listed it as one, which was a dimensional error.

**2.6.2 Analytical endpoint**

| component | source |
|---|---|
| `E_endpoint_construction` | null-basis endpoint construction and its projector residuals |
| `E_endpoint_spatial` | mesh refinement at the endpoint |
| `E_endpoint_profile_arithmetic` | floating-point cost of the exact profiling at the limit |
| `E_endpoint_floating` | double precision on the declared operator sizes |

```
J_inf ∈ [ max(0, J_inf_hat − E_inf),  J_inf_hat + E_inf ]
```

Four components and no others. **Do not add to `J_inf`:** a finite-`κ` `C/κ` remainder (at
`κ = ∞` the asymptotic remainder is zero — the remainder localises where a tail begins, which is a
different question and is not asked here); the weighted-median inventory tie width; the
finite-domain search error; or the response-shoulder error.

**2.6.3 Response shoulder**

`E_shoulder_step`, `E_shoulder_spatial`, `E_shoulder_floating`. This budget enters **no** objective
and **no** threshold. It is descriptive model sensitivity, per §2.8.

### 2.7 Finite WIDE minimisation and topology contract

No assumption of a single minimum or monotone tails. One deterministic, fail-closed numerical
procedure, frozen here, on `log κ` over `D_WIDE`.

**Nested grids, exactly:**

```
40, 80, 160, 320 log-spaced points on [0.15, 500]
```

**2.7.1 Reference-minimum search.** At every refinement:

1. evaluate both domain endpoints;
2. identify every sampled local basin;
3. run bounded scalar minimisation in every basin;
4. retain tied or near-tied basins;
5. compare the best value and the minimiser locations across refinements;
6. calculate the predeclared search-convergence envelope;
7. return `reference_minimum_status = unresolved` if the frozen stability criteria are not met.

**The minimum of the 40-point grid is never reported as `J_ref`.** It is retained beside the result
as a diagnostic and is labelled as one.

**2.7.2 Threshold topology.** For every threshold:

1. detect every sign change on each nested grid;
2. refine every detected root;
3. run explicit tangency checks;
4. compare roots and components across refinements;
5. retain lower-boundary censoring;
6. report components only within `[0.15, 500]`;
7. return `finite_wide_topology_status = unresolved` if the frozen stability criteria fail.

A **tangency** is a local minimum of `J − T` that stays positive but within the frozen relative band
of zero: no root is bracketed, yet the component structure is not decided. It is returned unresolved
rather than merged away or discarded. A refined local minimum that turns out to be *below* the
threshold where the grid showed no sign change is also unresolved — that is a statement about the
grid, not about the profile.

**No component adjoining the endpoint exists.** The previous edition admitted an explicit
`[κ_c, ∞]` component whenever the endpoint was included. Under the WIDE reference no finite topology
is claimed for `(500, ∞)`, so that object is not constructible and must not be serialised. A
component reaching the upper edge is recorded as `upper_truncated_at_domain_edge` with a finite
bound of 500.

**An unresolved `J_ref` blocks endpoint classification**, because it changes the threshold.
**Unresolved secondary finite topology does not erase an otherwise resolved endpoint
classification**, but it is reported prominently and prevents any claim of complete finite-domain
topology.

**2.7.3 Frozen numerical stability tolerances.** Assigned here, before the freeze, and tested only
on synthetic objective functions. The coordinate is natural `log κ`; objective tolerances are in
percentage points. All are fail-closed: violating one returns `unresolved`, never a best guess.

| tolerance | value | applies to |
|---|---|---|
| `MIN_XATOL_LOGKAPPA` | `1e-8` | bounded scalar minimisation inside a basin |
| `BASIN_TIE_RTOL` / `BASIN_TIE_ATOL` | `1e-3` / `1e-12` | retention of a tied or near-tied basin |
| `BASIN_MERGE_DLOG` | `1e-6` | two minimisers closer than this are the same basin |
| `REF_VALUE_RTOL` / `REF_VALUE_ATOL` | `1e-4` / `1e-9` | best-value stability, each of the final two transitions |
| `REF_LOCATION_DLOG` | `1e-3` | stability of the retained minimiser **set**, final transition |
| `E_REF_SEARCH_FLOOR` | `1e-12` | floor of the search-convergence envelope |
| `ROOT_XTOL_LOGKAPPA` | `1e-8` | bisection tolerance for a threshold root |
| `TANGENCY_RTOL` | `1e-3` | relative band defining a tangency |
| `ROOT_MATCH_DLOG` | `1e-3` | matching roots across refinements |

The whole retained set is compared across refinements, not only the argmin, so a genuine tie that
swaps which basin holds the argmin does not read as instability.

Implementation and synthetic architecture tests: `puckworks/paper_a/wide_reference.py` and
`tests/test_paper_a_wide_reference.py`.

### 2.8 Response shoulder

The shoulder is **descriptive model sensitivity and is not the objective-profile boundary.** The two
are reported separately and never conflated.

| item | frozen value |
|---|---|
| derivative | `s(κ) = ∂ log ŷ / ∂ log κ`, central difference, step 0.08 in `log κ`, with half/double step-convergence |
| inventory | held **fixed** at the group's `J_ref` level (not re-profiled), so the quantity is a pure model-response sensitivity |
| aggregation | **maximum absolute** `s` over the declared outputs at that condition — identifies where **all** outputs are weakly sensitive |
| primary threshold | **0.05** |
| sensitivity family | {0.10, 0.05, 0.01} |
| crossing rule | smallest `κ` above which `max_out |s| < threshold` for all larger grid points; located by bisection to `|Δ log κ| < 1e-3` |
| no crossing | `shoulder_not_reached` within the WIDE grid — reported, not extrapolated |
| multiple crossings | all reported; the **largest** is the shoulder, and the multiplicity is flagged |

The threshold family is declared here so that a member cannot be chosen afterwards for agreement
with `J_inf`. The shoulder error budget (§2.6.3) enters neither `J_ref`, nor `J_inf`, nor any
threshold.

### 2.9 Group and programme-level decision rules

Per group, per convention, the endpoint classification is one of `endpoint_included`,
`endpoint_excluded`, `endpoint_indeterminate`, `limit_construction_failed`, or — for a relative
convention under the §2.5 near-zero rule — `relative_threshold_not_applicable_near_zero`.

**Group-level success.** A group succeeds when:

- `J_ref` is resolved;
- the endpoint construction succeeds;
- it is `endpoint_included` under the 10 % relative convention;
- it is `endpoint_included` under at least one absolute convention; and
- it is not `endpoint_excluded` under either absolute convention.

**Group-level exception.** A group is an exception when:

- `J_ref` is resolved;
- the endpoint construction succeeds;
- it is not excluded under the 10 % relative or either absolute convention; but
- it fails the success rule because one required convention is indeterminate, or the relative
  convention is `relative_threshold_not_applicable_near_zero`.

**Group-level failure.** A group fails when:

- `J_ref` is unresolved;
- endpoint construction fails;
- the 10 % relative convention is `endpoint_excluded`; or
- either absolute convention is `endpoint_excluded`.

Success is tested before exception. That order decides the one case the wording leaves open: a group
included under one absolute convention and indeterminate under the other **succeeds**, because the
success rule asks for inclusion under *at least one* absolute convention and exclusion under
neither.

**Programme result, frozen:**

```
H1_STRONG:          6/6 group-level successes.

H1_QUALIFIED:       exactly 5/6 group-level successes and exactly one group-level exception.
                    The exception is named in the same headline sentence.

H1_DOES_NOT_LEAD:   any group-level failure; two or more exceptions; any unresolved J_ref;
                    or any endpoint-construction failure.
```

**Every threshold-family result remains displayed**, even when it does not determine the programme
label.

`finite_wide_topology_status` does not enter this rule. Unresolved secondary finite topology is
reported prominently and prevents any claim of complete finite-domain topology (§2.7.2), but it does
not erase an otherwise resolved endpoint classification.

### 2.10 Archive and reproducibility contract

`PAPER_A_ASYMPTOTIC_PROFILE_LIMITS.json` records: protocol version; frozen-content commit; producer
path and SHA-256; exact command; environment and package versions; every input path and SHA-256;
group definitions; the estimand tag `FULL-WIDE-ENDPOINT`; the reference domain, the nested grid
sizes and both threshold families; the full objective and tolerance specification; the three
quantity-specific error-budget identifiers of §2.6; `J_ref`, `J_inf`, thresholds and all intervals;
every connected component, within `[0.15, 500]` only; shoulder results including the family;
per-group classification under **every** convention; all failures and warnings; the programme result
from §2.9; the archive's own hash; and a **substantive** verification command.

Six status fields are recorded **separately**, because they answer six different questions and a
single pooled status is how they were conflated before:

```
reference_minimum_status:      resolved | unresolved
finite_wide_topology_status:   resolved | unresolved
endpoint_classification:       endpoint_included | endpoint_excluded |
                               endpoint_indeterminate | limit_construction_failed
eventual_upper_status:         wide_referenced_upper_set_unbounded |
                               wide_referenced_eventually_excluded |
                               upper_status_indeterminate
tail_onset_status:             unresolved_by_design | certified_in_separate_analysis |
                               not_applicable
intermediate_domain_status:    not_characterized_by_design
```

For the current protocol:

```
tail_onset_status          = unresolved_by_design
intermediate_domain_status = not_characterized_by_design
```

The archive also records `eventual_upper_precondition = fixed_positive_time_limit` and its status
(§2.5). **An invented component such as `[κ_c, ∞]` is never serialised**; finite connected components
are reported only within `D_WIDE`. The structural contract is
`puckworks.paper_a.wide_reference.validate_archive`.

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
| `κ` locations | `κ = 1` (nominal); each group's `J_ref` minimiser (group-specific; every retained tied minimiser is used); and the §2.8 shoulder |
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

**H4 wording is generated from the P0-G8 outcome**, not chosen: if P0-G8 returns `H1_STRONG` or
`H1_QUALIFIED`, H4's antecedent is satisfied and the localisation clause applies; otherwise only the
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
| P0-G8 returns `H1_DOES_NOT_LEAD` | H1's broad headline is removed; the response limit and threshold dependence lead |
| P0-G8 returns `H1_QUALIFIED` | H1 may lead, and the single exception is named in the same headline sentence |
| any group returns `limit_construction_failed` or an unresolved `J_ref` | that group is a failure, so the programme result is `H1_DOES_NOT_LEAD` until it is resolved or explicitly scoped |
| any group returns `finite_wide_topology_status = unresolved` | the programme label is unchanged, but no claim of complete finite-domain topology is made and the unresolved status is reported prominently |
| `eventual_upper_precondition_status` is not `established` | no reader-facing text converts an eventual-upper enumerated value into a statement about arbitrarily large multipliers |
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

---

## 10. Deviation record

Append-only, per the deviation policy in the header. Every entry is dated, justified, and carries an
impact statement. This protocol is **not yet frozen**, so an entry here records a pre-freeze change
to a candidate document; it is not a post-freeze deviation.

### D-01 — 2026-08-02 — WIDE-referenced estimand replaces the unresolved global reference

**Changed.** §1.3 (added `FULL-WIDE-ENDPOINT`), §2.2, §2.3, §2.5, §2.6, §2.7, §2.9, §2.10, and the
dependent vocabulary in §3, §5 and §8.

**Why.** §2.2 declared the classification domain to be `[0.15, ∞]` and §2.3 defined `J_min` as an
infimum over it, while the only search the protocol specified ended at `κ = 500`. No procedure
computed the declared quantity. The reference is now `J_ref`, the continuously minimised objective on
the finite `D_WIDE = [0.15, 500]`, with `κ = ∞` evaluated separately as an analytical endpoint and
compared against the resulting threshold.

Three further defects were corrected in the same pass:

- §2.6 pooled one error sum across the reference minimum, the endpoint and the shoulder, and listed
  the weighted-median tie width as a percentage-point error. The tie width is in inventory units and
  the objective is exactly constant across it, so it was dimensionally wrong. The budgets are now
  three disjoint sets of named components.
- §2.7 admitted an explicit `[κ_c, ∞]` connected component. No finite topology is claimed for
  `(500, ∞)`, so that object is not constructible and is now rejected by the archive contract.
- §2.9 stated the programme rule as a single sentence with no group-level definitions, leaving the
  five-of-six case and the near-zero relative case undecided. Group-level success, exception and
  failure are now defined, and the programme label is one of three enumerated results.

**Impact.** No result changes, because no P0-G8 result exists: the gate has not run and its archive
does not exist in the tree. What changes is which quantity the gate will compute and which
statements the archive can carry. `J_min` over a compactified domain is withdrawn and does not
appear in any active surface. `FULL-WIDE` is retained for finite-domain results, which are
unaffected; the finite-domain scan in `PAPER_A_RATE_DOMAIN_CHECK.json` keeps that tag and remains
superseded by P0-G8, as it already was. The displaced wording in the immutable initial claim ledger
is recorded in `PAPER_A_CLAIM_RESOLUTION_DELTA_PRE_FREEZE.json`; the ledger itself is not rewritten.

**Not included, and still owed before P0-G0 can freeze.** The fixed-positive-time limit result that
the eventual-upper vocabulary is conditional on; the PR-03a verdict-field split; the production
`_mape_profile_level`; PR-07 staging; PR-09; premise gating; commit-bound closures; and the
freeze/activation Git-history controls.
