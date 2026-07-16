# Detailed technical review of `PAPER_A_DRAFT.md`

**Review date:** 12 July 2026  
**Repository:** [`trbrewer/puckworks`](https://github.com/trbrewer/puckworks)  
**Manuscript reviewed:** [`docs/PAPER_A_DRAFT.md`](https://github.com/trbrewer/puckworks/blob/main/docs/PAPER_A_DRAFT.md)  
**Recommendation:** **Major revision; not ready for submission in its current form**

---

## 1. Executive assessment

The manuscript has a strong and useful methodological question: **does a good endpoint fit demonstrate that an extraction model has learned transferable kinetics, or can inventory and rate compensate?** The repository's emphasis on matched observables, held-out tests, explicit evidence-strength labels, and visible negative results is an unusually good foundation for answering that question.

The central qualitative idea is credible and worth developing. In the tested model, the initial soluble inventory is a level parameter, and a kinetic-rate multiplier can produce a broad compensating valley when the scoring observable does not retain enough temporal information. The paper also correctly recognizes that a refit on a new coffee is not the same thing as a frozen-parameter transfer.

However, the present quantitative story is not yet reliable enough for publication. Two implementation issues affect the observables at the heart of the manuscript:

1. **The cross-grind calculations use grind-specific flows but integrate every condition for a fixed 25 seconds.** At the reference condition this represents approximately 50 mL for O, 77 mL for C, and 29 mL for F, although the Angeloni experiments target approximately 40 g of beverage. The resulting concentrations are therefore not matched to the same cup endpoint. This can materially create or amplify the reported coarse/fine residual pattern.
2. **The positive-control “whole cup” is not a whole cup.** It is a duration-weighted average of six selected fraction windows numbered 1, 2, 3, 5, 7, and 10; the unmeasured intervals are omitted. The repository contains actual brew-ratio 1/3 cup-concentration observations for those experimental conditions. A targeted data audit shows that the current sampled-window aggregate differs from the actual cup concentration by roughly 28–38% MAPE, depending on solute.

A third implementation mismatch is also important: the manuscript repeatedly says that the inventory is optimized analytically and the profile is mapped exactly, but the code uses finite grids for both the level and rate. Several headline conclusions are then based on coarse, boundary-limited sweeps without uncertainty or range-convergence checks.

These are correctable problems. The paper should be rebuilt around a stricter sequence:

> **match the beverage endpoint → profile the level exactly → quantify practical identifiability with uncertainty → test frozen-parameter transfer separately → compare fractions with an actual full-cup observable.**

Until that sequence is completed, all numerical claims in the Abstract and Results—especially the 25–49% cross-grind errors, the ~30% joint-fit error, the 1.2–1.3× “whole-cup” ratios, and the categorical statements that the rate is or is not identified—should be treated as provisional.

---

## 2. Review basis and limits

### Repository materials inspected

The review compared the manuscript against the following repository materials:

- [`docs/PAPER_A_DRAFT.md`](https://github.com/trbrewer/puckworks/blob/main/docs/PAPER_A_DRAFT.md)
- [`docs/ANALYSIS_transfer.md`](https://github.com/trbrewer/puckworks/blob/main/docs/ANALYSIS_transfer.md)
- [`puckworks/validation/slow/angeloni_bracket.py`](https://github.com/trbrewer/puckworks/blob/main/puckworks/validation/slow/angeloni_bracket.py)
- [`puckworks/validation/slow/identifiability.py`](https://github.com/trbrewer/puckworks/blob/main/puckworks/validation/slow/identifiability.py)
- [`puckworks/models/pannusch2024/solver.py`](https://github.com/trbrewer/puckworks/blob/main/puckworks/models/pannusch2024/solver.py)
- [`docs/cards/angeloni2023.md`](https://github.com/trbrewer/puckworks/blob/main/docs/cards/angeloni2023.md)
- [`docs/cards/pannusch2024.md`](https://github.com/trbrewer/puckworks/blob/main/docs/cards/pannusch2024.md)
- [`puckworks/data/angeloni2023/bioactives.csv`](https://github.com/trbrewer/puckworks/blob/main/puckworks/data/angeloni2023/bioactives.csv)
- [`puckworks/data/angeloni2023/total_solids.csv`](https://github.com/trbrewer/puckworks/blob/main/puckworks/data/angeloni2023/total_solids.csv)
- [`puckworks/data/angeloni2023/inventories.csv`](https://github.com/trbrewer/puckworks/blob/main/puckworks/data/angeloni2023/inventories.csv)
- [`puckworks/data/pannusch2024/experimental_kinetics.csv`](https://github.com/trbrewer/puckworks/blob/main/puckworks/data/pannusch2024/experimental_kinetics.csv)
- [`puckworks/data/schmieder2023/cup_masses.csv`](https://github.com/trbrewer/puckworks/blob/main/puckworks/data/schmieder2023/cup_masses.csv)
- [`puckworks/data/schmieder2023/raw_fractions.csv`](https://github.com/trbrewer/puckworks/blob/main/puckworks/data/schmieder2023/raw_fractions.csv)

### Snapshot record

Because the manuscript and code point to a moving `main` branch rather than a manuscript-specific commit, the exact files fetched for this review were recorded by SHA-256:

| File | SHA-256 |
|---|---|
| `docs/PAPER_A_DRAFT.md` | `147227ce6c9dd3a8ac9b48329cb1bfd1adc02689ff8c5ae70c7d744dfcd36919` |
| `puckworks/validation/slow/angeloni_bracket.py` | `1a24a7cae11a4f6182389f2c153f96df5c8ee793247c02e0faefddf2bd5bdd47` |
| `puckworks/validation/slow/identifiability.py` | `c24001a72c89090445f0f410c8c018a59b45e44927c862d576d6a7608c401d42` |
| `puckworks/models/pannusch2024/solver.py` | `9e640e09cbf417289f20d377c1ade4d4cd9e9371dad9a9fe0bcbf813dba134a4` |
| `puckworks/data/pannusch2024/experimental_kinetics.csv` | `735c8aa86e06ff1c46f13335924d91636e77da161962a1b7e9394421dbdd28ca` |
| `puckworks/data/schmieder2023/cup_masses.csv` | `39b7c16f9d9da614f151f46cb0db1440d43f150fbf49d3d2119f3f2fa1622f43` |
| `docs/cards/angeloni2023.md` | `a5234e6d18d1db295f64163e3646199c604b5682ae587909a3961f3d84bd50b2` |
| `docs/cards/pannusch2024.md` | `4d5bea52ae76e2e227ed6568fad8edf719b3bb849c488faa76e8f652983a5632` |

### What was and was not independently reproduced

This review included static code inspection, data-structure checks, shot-volume arithmetic, and a targeted comparison between the sampled-fraction aggregate and the actual brew-ratio 1/3 cup data. The full slow PDE suites were **not** treated as independently reproduced here. The manuscript's printed output values were audited against their code paths, but an end-to-end rerun and numerical convergence study remains a required manuscript action.

---

## 3. Summary of findings and required actions

| ID | Severity | Finding | Required action |
|---|---|---|---|
| B1 | **Blocker** | Cross-grind predictions use a fixed 25 s interval despite grind-specific 40 g shot times | End each simulation at the matched beverage mass/volume and rerun every cross-grind and joint-fit result |
| B2 | **Blocker** | The positive-control “whole cup” omits unmeasured intervals and is not the actual cup observable | Use actual BR 1/3 cup observations or reconstruct the complete shot; relabel the present quantity if retained |
| B3 | **Blocker** | Manuscript says analytic/exact profiling; code uses coarse finite grids | Implement the exact MAPE level profile or validated continuous optimization; expose the complete profile in code |
| B4 | **Blocker** | “Identifiability ratio” is range-dependent, lacks uncertainty, and code computes max/min rather than explicitly edge/min | Replace or supplement with profile-likelihood/error regions, shot-level bootstrap, parameter correlation, and sweep-range convergence |
| B5 | **Blocker** | Cross-grind failure conflates endpoint mismatch, frozen grain geometry, flow assumptions, and parameter confounding | Correct endpoint first, run geometry/flow sensitivities, and narrow the causal claim |
| B6 | **Blocker** | All joint optima hit the rate boundary, yet the manuscript says no shared calibration exists | Extend and justify the parameter domain until the optimum is interior or a stable asymptote is demonstrated |
| M1 | Major | Non-identifiability does not logically imply non-transferability | Present practical non-identifiability and empirical transfer failure as separate findings |
| M2 | Major | Residual is declared “not a flow error” after testing only two assumed maps | Say “not removed by the two tested maps”; propagate flow and endpoint uncertainty |
| M3 | Major | Positive control is in-sample verification, not independent physical identification | Use “objective localization on calibration data”; reserve identification claims for uncertainty-qualified or independent evidence |
| M4 | Major | The ~7% holdout is an average of very small two-point checks | Report every fit and prediction, uncertainty, and blocked/leave-one-condition-out validation |
| M5 | Major | TDS and gravimetric total solids are treated as interchangeable despite different model semantics | Separate or exclude TDS from headline averages; document the proxy and sensitivity |
| M6 | Major | MAPE ignores replicate uncertainty and creates a particular weighting | Justify the error model; add uncertainty-weighted and alternative-loss sensitivity analyses |
| M7 | Major | Structural and practical identifiability language is blurred | Use “practically non-identifiable over the tested domain under this design and objective” |
| M8 | Major | Code docstrings and returned verdicts contain retracted or stale interpretations | Remove narrative verdicts from code or synchronize them with the manuscript and structured evidence |
| M9 | Major | Related work is explicitly incomplete | Complete a systematic identifiability and inverse-problem review before asserting novelty |
| M10 | Major | “Every number regenerates” is not presently true for all tables and prose | Add one paper-build command, captured outputs, tests, environment lock, and a pinned commit |
| E1 | Editorial | Internal project instructions are still in the manuscript | Remove ROADMAP/G6/verb-discipline/change-log prose from the submitted manuscript |
| E2 | Editorial | Several phrases are categorical or rhetorical beyond the evidence | Replace “It is wrong,” “as it must,” and “no shared calibration exists” with evidence-bounded wording |
| E3 | Editorial | Figures needed to evaluate the claims are missing | Add profiles, actual-vs-predicted panels, residual structure, and uncertainty graphics |

---

# 4. Submission-blocking technical findings

## B1. The cross-grind calculations do not compare matched 40 g cups

### Manuscript claim

The Methods say the per-granulometry test uses Angeloni's fitted hydraulic conductivity and shot times `τ_{O,C,F} = 20/13/35 s`, and the Results describe C and F as predictions “each with its own measured flow” ([draft lines 113–123](https://github.com/trbrewer/puckworks/blob/main/docs/PAPER_A_DRAFT.md#L113-L123), [215–231](https://github.com/trbrewer/puckworks/blob/main/docs/PAPER_A_DRAFT.md#L215-L231)). The joint fit likewise says each grind uses its own measured flow ([233–245](https://github.com/trbrewer/puckworks/blob/main/docs/PAPER_A_DRAFT.md#L233-L245)).

The target study, as summarized by the repository card, used a 20 g dose and **40 ± 2 g beverage** at a 1:2 ratio; the card also records the O/C/F shot times as 20/13/35 s ([Angeloni card lines 62–76](https://github.com/trbrewer/puckworks/blob/main/docs/cards/angeloni2023.md#L62-L76)).

### What the code does

The flow adapter defines

```python
flow = (40 / tau_gran) * k_r(p) / k_r(9) * mu_ref / mu(T)
```

([`angeloni_bracket.py` lines 284–297](https://github.com/trbrewer/puckworks/blob/main/puckworks/validation/slow/angeloni_bracket.py#L284-L297)).

However, both the joint fit and held-out-grind validation evaluate every condition over `[0.0, 25.0]` seconds ([lines 332–335](https://github.com/trbrewer/puckworks/blob/main/puckworks/validation/slow/angeloni_bracket.py#L332-L335), [426–429](https://github.com/trbrewer/puckworks/blob/main/puckworks/validation/slow/angeloni_bracket.py#L426-L429)).

At 9 bar and the reference temperature, the implied beverage amounts are approximately:

| Grind | `τ` used to define flow | Reference flow | Beverage represented by 25 s | Difference from 40 mL |
|---|---:|---:|---:|---:|
| O | 20 s | 2.000 mL/s | 50.0 mL | +25% |
| C | 13 s | 3.077 mL/s | 76.9 mL | +92% |
| F | 35 s | 1.143 mL/s | 28.6 mL | −29% |

Pressure and temperature scaling change these amounts further. Thus, the comparison does not merely vary flow while holding the measured cup endpoint fixed; it also varies the simulated beverage amount substantially and in a grind-dependent direction.

### Why this matters

Cup concentration depends on both extraction history and the interval over which mass is collected. Integrating coarse-grind flow for 25 s can represent nearly twice the target beverage volume, while fine-grind integration can stop well before the target. This is capable of producing a structured O/C/F residual even if the model's true matched-cup transfer were better.

The manuscript currently interprets the extreme-grind residual as evidence that a single inventory/rate cannot serve all grinds. That interpretation cannot be separated from this endpoint mismatch until the simulations are rerun at the target beverage mass.

### Required action

1. For every condition, compute a terminal time that yields the same target beverage amount as the observation. For constant flow, use approximately `t_end = V_target / Q`; for time-varying flow, integrate until cumulative beverage reaches the target.
2. Match the source protocol's 40 ± 2 g endpoint, with a documented density convention.
3. Rerun:
   - the blind per-condition comparison;
   - the O fit and two O holdouts;
   - O→C/F frozen-parameter transfer;
   - per-grind refits;
   - the joint shared-inventory fit;
   - all residual and identifiability summaries that depend on these predictions.
4. Add a sensitivity at 38, 40, and 42 g.
5. Do not retain the 25–49%, ~30%, or “extreme-grind residual” headline values unless they survive this correction.

### Suggested replacement wording before rerun

> “The current cross-grind calculation is a preliminary fixed-time stress test. A matched-beverage-mass rerun is required before interpreting its coarse/fine residuals as transfer failure.”

---

## B2. The positive-control “whole cup” is a sampled-window aggregate, not a whole cup

### Manuscript claim

The Methods state that the same fraction shots are “collapsed to one volume-weighted whole-cup value” ([draft lines 135–144](https://github.com/trbrewer/puckworks/blob/main/docs/PAPER_A_DRAFT.md#L135-L144)). Result 4 repeatedly calls the resulting quantity a whole cup and concludes that the cup integrates the kinetic rate away ([247–272](https://github.com/trbrewer/puckworks/blob/main/docs/PAPER_A_DRAFT.md#L247-L272)).

### What the data and code show

The Pannusch experimental-kinetics file contains six selected windows per experiment, with fraction numbers:

```text
1, 2, 3, 5, 7, 10
```

For example, experiment 1 covers:

```text
0.000–4.496 s
4.496–11.469 s
11.469–17.755 s
23.789–29.778 s
35.450–41.071 s
52.866–58.490 s
```

The windows between fractions 3 and 5, 5 and 7, and 7 and 10 are not included in the measured aggregate.

The code forms `cpred` and `cmeas` by weighting only these six selected windows by their durations ([`identifiability.py` lines 45–61](https://github.com/trbrewer/puckworks/blob/main/puckworks/validation/slow/identifiability.py#L45-L61)). It does not integrate the full 0-to-end shot and does not use the actual cup observations in `cup_masses.csv`.

The repository does contain actual cup concentrations at brew ratio 1/3 for the same experimental-condition identifiers. A targeted audit compared:

- the code's duration-weighted mean of the six selected fraction observations; and
- the replicate-mean `conc_in_cup` at brew ratio 1/3.

Across the 15 experimental conditions:

| Solute | Mean sampled-window aggregate | Mean actual BR 1/3 cup | Mean aggregate/cup ratio | MAPE across experiments |
|---|---:|---:|---:|---:|
| caffeine | 4.340 mg/g | 3.400 mg/g | 1.278 | 27.8% |
| trigonelline | 2.391 mg/g | 1.733 mg/g | 1.383 | 38.3% |
| 5-CQA | 2.825 mg/g | 2.168 mg/g | 1.307 | 30.7% |

The discrepancy is not a single constant scaling factor: the sampled-window/actual-cup ratio ranges approximately 1.05–1.53 across solutes and experiments. A global level re-optimization therefore does not automatically remove the shape difference.

### Why this matters

The paper's positive control is intended to establish the key contrast “fractions retain rate information; the same shots' endpoint does not.” That comparison is only compelling if the endpoint is a valid full-shot observable. The present code instead compares all measured windows with a non-contiguous subset average. This can make the aggregate appear flatter for reasons that are partly an artifact of sampling.

### Required action

Use one of the following defensible designs:

1. **Preferred empirical comparison:** score the fraction curves against the fraction data and score full-shot model predictions against the actual BR 1/3 cup observations at the same experimental conditions. Account for the fact that cup and fraction measurements may be separate replicates rather than literally the same shot.
2. **Complete reconstruction:** if all ten fraction masses and concentrations can be obtained, integrate every interval over the complete shot and verify that the reconstructed cup agrees with `cup_masses.csv`.
3. **Simulation-only information comparison:** generate synthetic complete fraction curves from the calibrated model, add a stated noise model, and compare identifiability when those curves are retained versus exactly integrated. Label this a simulation study rather than an empirical positive control.

If the present six-window statistic is retained for a secondary sensitivity, call it a **“sampled-fraction aggregate”**, not a whole cup.

All claims and ratios in Result 4 must be regenerated after this correction.

---

## B3. The manuscript's “analytic” and “exact” profile is implemented as a coarse grid search

### Manuscript claim

The Methods state that exact linearity in `c_s0` makes the best-fit inventory available analytically and allows the objective valley to be mapped “exactly rather than by noisy re-optimisation” ([draft lines 83–96](https://github.com/trbrewer/puckworks/blob/main/docs/PAPER_A_DRAFT.md#L83-L96)). The fitting protocol repeats that inventory is “obtained analytically” ([125–133](https://github.com/trbrewer/puckworks/blob/main/docs/PAPER_A_DRAFT.md#L125-L133)).

### What the code does

In `refit_pannusch_angeloni`, `_best_cs0` evaluates 50 candidate levels over a finite interval and takes the grid argmin ([`angeloni_bracket.py` lines 241–244](https://github.com/trbrewer/puckworks/blob/main/puckworks/validation/slow/angeloni_bracket.py#L241-L244)). The joint and per-grind fits similarly use 60- or 50-point level grids ([lines 349–374](https://github.com/trbrewer/puckworks/blob/main/puckworks/validation/slow/angeloni_bracket.py#L349-L374), [431–444](https://github.com/trbrewer/puckworks/blob/main/puckworks/validation/slow/angeloni_bracket.py#L431-L444)). The positive-control level fit uses a 160-point grid ([`identifiability.py` lines 31–35](https://github.com/trbrewer/puckworks/blob/main/puckworks/validation/slow/identifiability.py#L31-L35)).

The rate grids are also sparse:

- default transfer/joint/degeneracy grid: eight linearly spaced values from 0.4 to 2.5;
- positive-control grid: nine hand-selected values from 0.25 to 4.0.

### The correct analytic profile for MAPE

At fixed rate, let `f_i` be the predicted concentration per unit inventory, `m_i` the measured concentration, and `c` the level. The MAPE objective is

\[
J(c)=\frac{1}{n}\sum_i \frac{|c f_i-m_i|}{m_i}
=\frac{1}{n}\sum_i \frac{f_i}{m_i}\left|c-\frac{m_i}{f_i}\right|.
\]

For positive `f_i` and `m_i`, an exact minimizer is a **weighted median** of `m_i/f_i` with weights `f_i/m_i`. It is not generally the ordinary median and is not merely an unspecified “rescale.” If a different loss is chosen, it has a different analytic optimum.

### Why this matters

A coarse level grid can quantize both the minimum and the fitted inventory, while a sparse rate grid can create apparent boundary optima or miss curvature. This is particularly problematic when the scientific claim concerns a difference of less than one percentage point across the profile.

The manuscript's rate-profile table is also not directly returned by the named function: `refit_pannusch_angeloni` returns only the best rate for each fit. The complete table therefore does not presently have a single structured, paper-facing output path.

### Required action

1. Implement an exact weighted-median solution for MAPE, with tests against dense brute-force optimization.
2. Alternatively, use a continuous scalar optimizer with a convergence test and stop calling the result analytic.
3. Add a dedicated function such as `profile_inventory_rate(...)` that returns, for every rate:
   - exact profiled inventory;
   - objective value;
   - predictions and residuals;
   - boundary/convergence flags.
4. Use a log-rate grid dense enough to resolve the profile and then refine locally with continuous optimization.
5. Regenerate every table and figure from the structured profile output.
6. Add unit tests for linearity in `c_s0`, exact level optimization, and profile reproducibility.

---

## B4. The “identifiability ratio” is not a sufficient identification analysis

### Current definition

The manuscript defines

\[
R = \frac{\text{max-edge MAPE}}{\text{minimum MAPE}}
\]

and treats `R ≫ 1` as identified and `R ≈ 1` as not identified ([draft lines 135–144](https://github.com/trbrewer/puckworks/blob/main/docs/PAPER_A_DRAFT.md#L135-L144)).

### Code/manuscript mismatch

The implementation uses `max(profile)/min(profile)` rather than explicitly evaluating the two sweep edges ([`identifiability.py` lines 65–79](https://github.com/trbrewer/puckworks/blob/main/puckworks/validation/slow/identifiability.py#L65-L79)). It may happen that the maximum lies at an edge for the current grid, but that is not guaranteed by the code.

### Statistical limitations

The ratio is not a standard identifiability diagnostic and has several problems:

- It increases or decreases when the arbitrary sweep endpoints change.
- It has no defined threshold for “≫1.”
- It ignores replicate or assay uncertainty.
- It does not provide a confidence interval for the rate.
- It does not describe inventory–rate covariance.
- It can call a profile “sharp” even when its minimum is biased or the model is misspecified.
- It cannot distinguish structural identifiability from practical estimability under noise.
- It is calculated after another coarse level optimization.

The manuscript itself lists profile likelihood, condition number, and bootstrap work as still owed ([draft lines 305–319](https://github.com/trbrewer/puckworks/blob/main/docs/PAPER_A_DRAFT.md#L305-L319)). Those are not optional embellishments; they are necessary to support the title and main claim.

### Required action

At minimum:

1. Plot the full profiled objective over a justified log-rate domain.
2. Report the set of rates within a prespecified tolerance of the optimum, with the tolerance connected to measurement uncertainty or a bootstrap distribution.
3. Bootstrap at the experimental-shot level, preserving all fractions within a shot.
4. Report inventory–rate correlation and profile-derived uncertainty.
5. Repeat over alternative rate ranges and grid densities.
6. Compare MAPE with at least one uncertainty-aware or likelihood-based objective.
7. If a likelihood can be specified, use profile-likelihood confidence intervals; otherwise explicitly call the result an error-profile sensitivity rather than formal identification.
8. Retain the edge/min ratio, if desired, only as a descriptive visualization and not as the decision rule.

### Recommended terminology

Use:

> “The rate profile is sharply localized relative to the tested range under fraction scoring.”

and

> “The endpoint profile remains broad over the tested range.”

Do not write “the rate is identified” without a defined uncertainty criterion.

---

## B5. The cross-grind result does not isolate inventory–kinetics confounding

### Frozen geometry

The Pannusch solver states that the source's per-experiment grind assignment is opaque, so the implementation uses the center-grind geometry for every experiment ([`solver.py` lines 20–23](https://github.com/trbrewer/puckworks/blob/main/puckworks/models/pannusch2024/solver.py#L20-L23)). `simulate_fractions` defaults to `GRIND_17` ([lines 94–120](https://github.com/trbrewer/puckworks/blob/main/puckworks/models/pannusch2024/solver.py#L94-L120)). The cross-grind code changes flow by Angeloni granulometry but does not pass a different Pannusch grain geometry.

The repository card records fitted Pannusch `ψ` and `d_s2` values for grind 1.4/1.7/2.0 ([Pannusch card lines 63–86](https://github.com/trbrewer/puckworks/blob/main/docs/cards/pannusch2024.md#L63-L86)). Although no defensible cross-grinder mapping is yet established, the fact that geometry is frozen is a model-specification choice, not evidence about inventory/rate alone.

### Multiple simultaneous differences

The O→C/F result currently changes or assumes all of the following:

- flow through a fitted hydraulic map;
- a fixed 25 s endpoint rather than matched beverage mass;
- viscosity correction;
- frozen Pannusch grain geometry;
- a cross-machine and cross-coffee comparison;
- a fixed rate/inventory pair fitted at O.

A failure under this bundle does not uniquely diagnose inventory–kinetics confounding. It shows that the **tested transfer configuration** does not reproduce the targets.

### Required action

After correcting the beverage endpoint:

1. Define a hierarchy of cross-grind tests:
   - fixed geometry, matched beverage mass;
   - plausible geometry mapping using the Pannusch 1.4/1.7/2.0 table;
   - geometry sensitivity over a physically justified range;
   - optional fitted geometry only if clearly labelled as a new calibration.
2. Present the cross-grinder mapping uncertainty explicitly.
3. Report which components of failure are robust to geometry and flow assumptions.
4. Narrow the manuscript claim to the tested configuration unless the result is robust across that hierarchy.

A defensible statement would be:

> “A frozen-geometry, frozen-parameter transfer from O to C/F did not reproduce the matched-cup targets under the tested flow maps.”

---

## B6. A boundary optimum cannot support “no shared calibration exists”

### Current result

The manuscript says that every solute is pushed to the upper rate boundary of 2.5 and concludes that “no shared calibration exists” ([draft lines 233–245](https://github.com/trbrewer/puckworks/blob/main/docs/PAPER_A_DRAFT.md#L233-L245)). The code searches only eight rates from 0.4 to 2.5 ([`angeloni_bracket.py` lines 337–379](https://github.com/trbrewer/puckworks/blob/main/puckworks/validation/slow/angeloni_bracket.py#L337-L379)).

### Why this matters

An optimum at the boundary means the search domain is censoring the estimate. It does not establish that no better shared calibration lies beyond the boundary. It may also indicate a monotone objective, a missing mechanism, or the beverage-endpoint error discussed above.

### Required action

1. Correct the endpoint and level optimization first.
2. Extend the rate domain logarithmically in both directions.
3. Continue until one of the following is documented:
   - an interior minimum;
   - a stable asymptote with no scientifically meaningful improvement;
   - a physically justified parameter bound that the optimum violates.
4. Report profile curves, not only the selected boundary value.
5. Replace “no shared calibration exists” with:

> “No adequate shared calibration was found within the tested model and justified parameter domain.”

unless an actual non-existence result is proved.

---

# 5. Major interpretation and statistical issues

## M1. Practical non-identifiability and predictive transfer are separate questions

The manuscript opens Result 3 with: “Because the single-grind fit is non-identifiable, it is also non-transferable” ([draft lines 213–218](https://github.com/trbrewer/puckworks/blob/main/docs/PAPER_A_DRAFT.md#L213-L218)). This implication is not generally valid. Parameters can be individually non-identifiable while predictions remain stable along the compensating manifold. Conversely, well-estimated parameters can still transfer poorly under model misspecification.

The paper has two distinct findings to test:

1. **Estimation finding:** inventory and rate are practically confounded under a particular endpoint design and objective.
2. **Prediction finding:** a frozen calibration performs poorly on specified held-out conditions.

### Required action

Remove the causal connector. Use:

> “The single-grind fit is practically non-identifiable under the tested objective. Separately, its frozen predictions perform poorly on held-out C/F conditions.”

Then discuss whether the profile predicts transfer sensitivity, rather than assuming it.

---

## M2. “The residual is not a flow error” is unsupported

The manuscript says the residual after the Darcy refinement “is not a flow error” and “no flow map can close” it ([draft lines 175–179](https://github.com/trbrewer/puckworks/blob/main/docs/PAPER_A_DRAFT.md#L175-L179)). The code makes the same categorical assertion in docstrings and returned notes ([`angeloni_bracket.py` lines 190–204](https://github.com/trbrewer/puckworks/blob/main/puckworks/validation/slow/angeloni_bracket.py#L190-L204)).

Only two assumed mappings are compared:

- a crude pressure-to-shot-time interpolation;
- a single-anchor Darcy scaling.

Neither is measured per shot, and the current calculations also hold an unmatched 25 s interval. Therefore the analysis supports only:

> “The residual was not removed by the two tested flow mappings.”

### Required action

- Propagate uncertainty in the flow anchor and viscosity model.
- Include a matched-beverage endpoint.
- Where possible, compare against measured per-condition shot times or flows.
- Remove unique attribution to inventory plus kinetics unless competing sources have been quantitatively bounded.

---

## M3. The positive control is in-sample verification, not independent identification

The manuscript correctly labels Result 4 as verification on the model's own fit data, but its prose then says “the rate is identified” and “the two are separable only with time-resolved data” ([draft lines 247–272](https://github.com/trbrewer/puckworks/blob/main/docs/PAPER_A_DRAFT.md#L247-L272)).

The Pannusch model was fitted to these fraction data. Its source workflow used sequential estimation specifically to address parameter correlation, and the repository card warns that fitted parameters lack physical meaning and generality ([Pannusch card lines 85–106](https://github.com/trbrewer/puckworks/blob/main/docs/cards/pannusch2024.md#L85-L106)). A sharp in-sample profile shows that the implemented model and chosen objective are sensitive to rate near their calibration. It does not establish that the physical Sherwood rate is uniquely or accurately learned from independent data.

### Required action

Use language such as:

> “On the model's calibration data, fraction scoring localizes the rate profile more sharply than endpoint scoring.”

Reserve stronger identification language for:

- uncertainty-qualified estimation under an explicit error model; and preferably
- an independent fraction-resolved dataset.

Also change “only with time-resolved data” to “time-resolved data can supply the missing information in this model and design.” Other independent constraints or multi-condition designs can also break the degeneracy.

---

## M4. The ~7% holdout needs complete reporting and uncertainty

The refit is performed separately for each solute and variety, using nine O-grid points and only two off-grid O points per fit. The headline “mean holdout ≈7%” averages eight small checks when TDS is included: four modeled observables × two varieties. It is not a single robust validation sample.

The manuscript does acknowledge a “weak 2-pt holdout,” but the Abstract calls the error “excellent,” and the result is central to the narrative.

### Required action

Report:

- the prediction and observation for every held-out point;
- MAPE for every solute × variety fit;
- pooled error with a clearly stated weighting;
- median and range, not only the mean;
- uncertainty from a blocked bootstrap or leave-one-condition-out procedure;
- performance under alternative flow and endpoint assumptions.

A better validation design would hold out entire `(T,p)` conditions across both varieties or use nested leave-one-condition-out profiling, rather than relying on two points per fitted model.

Replace “excellent held-out error” with “a low mean error on two off-grid O points per solute/variety” until uncertainty is shown.

---

## M5. TDS and Angeloni total solids are not the same modeled observable

The code maps Pannusch `tds` to Angeloni `TS_g_100mL` with a unit conversion and an approximate `TS ≈ TDS` assumption ([`angeloni_bracket.py` lines 63–100](https://github.com/trbrewer/puckworks/blob/main/puckworks/validation/slow/angeloni_bracket.py#L63-L100)). The Pannusch card states that TDS is represented as a caffeine-like pseudo-molecule and that the fitted parameters lack generality ([Pannusch card lines 74–86](https://github.com/trbrewer/puckworks/blob/main/docs/cards/pannusch2024.md#L74-L86)).

The cross-grind function then drops TDS as a “unit-aggregate artifact” ([`angeloni_bracket.py` lines 397–414](https://github.com/trbrewer/puckworks/blob/main/puckworks/validation/slow/angeloni_bracket.py#L397-L414)), while the same-grind ~7% headline includes it.

### Required action

- Separate the chemically named solutes from the TDS/TS proxy throughout.
- Report headline results both with and without TDS.
- Explain the analytical definition of Angeloni total solids and why it is or is not commensurate with Pannusch's pseudo-solute.
- Do not average TDS with named bioactives unless the observable contract is defended.
- Apply one consistent inclusion rule across fit, holdout, and cross-grind tests.

---

## M6. MAPE is not a complete measurement-error model

MAPE gives each residual a weight proportional to `1/measured concentration`. That may be a reasonable descriptive score, but it is not automatically the appropriate fitting likelihood. The Angeloni total-solids table includes RSD values, and the source campaign used replicate measurements. The current fitting code does not use those uncertainties.

### Required action

1. State why MAPE is used for estimation rather than only evaluation.
2. Clarify whether the CSV rows are replicate means and how replicate variability enters the analysis.
3. Add at least two sensitivity fits:
   - uncertainty-weighted residuals using available RSD/SD information;
   - a log-concentration or relative-error model.
4. Use a shot-level bootstrap to preserve multisolute and within-condition dependence.
5. Report whether the inventory–rate valley and transfer verdict are robust to the loss function.

---

## M7. Distinguish structural from practical identifiability

The manuscript sometimes makes universal statements:

- “a single-grind whole-cup fit therefore constrains only their product”;
- “the whole cup integrates [the rate] away”;
- “only the product `c_s0 · φ`” is identified.

Yet the model response `φ(rate, flow, T)` can vary across multiple endpoint conditions. In principle, sufficiently informative endpoint measurements at different residence times, flows, or temperatures can contain some rate information. The current data show a **nearly flat practical profile over a tested domain**, not an exact theorem that all endpoint designs identify only a product.

### Required action

Use consistently:

> “Inventory and rate are practically non-identifiable over the tested rate domain under this single-grind endpoint design, flow assumptions, and objective.”

If the authors want a structural-identifiability theorem, it should be derived for a clearly simplified observation model with explicit conditions.

---

## M8. Code documentation contradicts the manuscript's current interpretation

Several code comments and returned notes preserve earlier conclusions that the manuscript now calls wrong. For example, `refit_pannusch_angeloni` still says caffeine kinetics transfer and the trigonelline difference is genuinely kinetic ([`angeloni_bracket.py` lines 207–223](https://github.com/trbrewer/puckworks/blob/main/puckworks/validation/slow/angeloni_bracket.py#L207-L223), [273–281](https://github.com/trbrewer/puckworks/blob/main/puckworks/validation/slow/angeloni_bracket.py#L273-L281)). The flow refinement declares the residual uniquely non-flow. `identifiability.py` returns a hard-coded narrative verdict with rounded values that no longer match the manuscript exactly ([`identifiability.py` lines 80–87](https://github.com/trbrewer/puckworks/blob/main/puckworks/validation/slow/identifiability.py#L80-L87)).

### Required action

- Remove scientific conclusions from stale docstrings and hard-coded verdict strings.
- Return structured numbers, assumptions, and evidence labels.
- Generate manuscript prose from versioned output artifacts rather than embedding conclusions in code.
- Add tests that manuscript tables agree with serialized outputs.

A person running the advertised scripts should not receive an interpretation the paper has retracted.

---

## M9. Related work is a declared submission blocker

The Related Work section explicitly says the systematic identifiability search is still owed and novelty should not yet be asserted ([draft lines 321–352](https://github.com/trbrewer/puckworks/blob/main/docs/PAPER_A_DRAFT.md#L321-L352)). This is correctly candid, but it means the manuscript is not yet review-ready.

### Required action

Complete and document a systematic search covering:

- structural versus practical identifiability;
- profile likelihood and likelihood-based confidence regions;
- sloppiness and compensating parameter manifolds;
- parameter confounding in reaction/transport and dissolution models;
- experimental design for kinetic identification;
- integral/endpoint observations versus time-resolved observations;
- prior coffee-extraction work using fractions, inventories, or multi-grind fits.

The paper should state what is new only after distinguishing among:

1. a new espresso case study;
2. a new observation about this specific model/data pair;
3. a new general method or theorem.

Also replace the ellipsis in the Pannusch title with the full verified title already present in the repository card: **“Model-based kinetic espresso brewing control chart for representative taste components.”**

---

## M10. The reproducibility claim is stronger than the current paper pipeline

The manuscript says every number regenerates from two slow modules ([draft lines 1–11](https://github.com/trbrewer/puckworks/blob/main/docs/PAPER_A_DRAFT.md#L1-L11)), but:

- the rate-profile table is not directly returned as a complete structured artifact;
- level profiles are grid approximations despite being called analytic;
- scripts contain stale narrative conclusions;
- the slow analyses are not in CI;
- the manuscript does not pin a commit, environment, output archive, or numerical tolerances;
- no single paper-build command generates tables and figures;
- there are no visible convergence checks for the solver, rate grid, or level optimization in this paper path.

### Required action

Create a reproducibility package containing:

1. a pinned repository commit and environment lock;
2. one command such as `python -m puckworks.paper_a.build`;
3. machine-readable outputs for every table and figure;
4. solver and optimizer tolerances;
5. runtime and hardware notes;
6. random seeds for bootstraps;
7. hashes of input data and generated artifacts;
8. tests for matched beverage volume, exact level profiling, rate-boundary flags, and full-cup aggregation;
9. a lightweight CI smoke test plus archived full slow-run outputs.

The repository's own provenance discipline says results should be reportable with component versions and gate status. Paper A should meet that standard.

---

# 6. Section-by-section manuscript comments

## Title

Current:

> “The cup hides the clock: an inventory–kinetics identifiability limit in cross-dataset espresso extraction modelling.”

The title is memorable, but “identifiability limit” sounds more general and formal than the present evidence. Until the statistical and observable corrections are complete, use a case-study formulation.

### Suggested title

> **The cup can hide the clock: practical inventory–kinetics confounding in a cross-dataset espresso extraction case study**

After a formal analysis and corrected actual-cup comparison, a stronger title may be justified.

---

## Abstract

The Abstract is clear and narratively strong, but nearly every numerical clause depends on analyses that require rerunning. Specific problems:

- “predict an independent 66-shot campaign” blurs blind prediction with subsequent fitting;
- “excellent held-out error” overstates a mean from two holdout points per fit;
- “does not transfer across grind” currently depends on unmatched beverage endpoints and frozen geometry;
- “collapsing the identical shots to a whole-cup value” is factually inaccurate for the implemented statistic;
- “the whole cup integrates it away” is too universal;
- no uncertainty is reported.

### Required action

Rewrite the Abstract only after corrected results exist. Until then, use no specific error ranges. A safe provisional version is:

> “We examine whether a multi-solute extraction model calibrated on fraction-resolved data retains a unique kinetic interpretation when refitted to an independent endpoint dataset. Profiling inventory and a Sherwood-rate multiplier reveals a broad compensating region under the tested single-grind endpoint design. In a separate verification on the model's calibration data, fraction-resolved scoring produces a more localized rate profile than an aggregated endpoint score. Frozen-parameter cross-grind predictions are also evaluated, with transfer conclusions conditioned on matched beverage volume, flow mapping, and grain-geometry assumptions. The results motivate reporting parameter profiles and collecting temporal or independent-inventory information rather than treating a low endpoint error as mechanistic validation.”

---

## Introduction

### Strengths

- The problem is accessible beyond coffee science.
- The distinction between endpoint fit and mechanism is valuable.
- The manuscript foregrounds a negative result rather than hiding it.

### Required revisions

- Replace “almost always” with evidence from a literature review or a narrower statement.
- Do not say a single-grind endpoint “therefore constrains only their product” as a universal theorem.
- Define “transfer” operationally near first use: frozen parameters, specified observable, specified domain.
- Distinguish parameter transfer, predictive transfer, and model-class validity.
- State early that the case study contains both cross-coffee and cross-machine changes, not only a dataset change.

---

## Methods

### Model description

The model summary is concise, but the paper must state all transfer-relevant approximations:

- center-grind geometry used by the port;
- constant porosity and complete wetting;
- imposed flow rather than predicted flow;
- TDS pseudo-molecule treatment;
- fitted nature of `A`, `B`, `K`, and `c_s0`;
- original source's warning that parameters lack generality.

### Data description

Clarify:

- whether Angeloni rows are replicate means;
- how duplicate measurements and RSD are handled;
- how the 66 rows divide into on-grid/off-grid and O/C/F subsets;
- that there are two O off-grid points per variety, not a large holdout set;
- whether Schmieder cup and fraction measurements are from identical shots or matched conditions.

### Flow mapping

Calling the refined map “from the study's own hydraulics” is too strong for the O single-anchor map. It combines a generic anchor with repository closures. Call it a **single-anchor Darcy-inspired assumption**. The per-grind map does use Angeloni's fitted `k_r(p)` and recorded characteristic times, but must still terminate at target beverage mass.

### Fitting protocol

State the total model-flexibility count. Separate fits across four observables and two varieties imply up to 16 fitted quantities (`c_s0` and `rate_scale` for each observable × variety), although each individual fit has two. The reader needs this context when interpreting the mean holdout.

### Identifiability metric

Move the edge/min ratio to a descriptive secondary metric. The primary method should be a profile with uncertainty and domain-convergence diagnostics.

### Validation vocabulary

The evidence-label system is useful internally, but manuscript readers need standard terminology. “Negative validation” is not universally understood and can sound self-contradictory. Prefer:

- calibration/reconstruction;
- internal holdout;
- external prediction;
- failed external prediction;
- in-sample verification.

The repository labels can remain in a supplement.

---

## Result 1

The sequence from broad envelope to per-condition testing is good. Retain it, but:

- show predictions and observations, not only MAPE;
- separate named solutes from TDS/TS;
- state the exact number of fitted and held-out points;
- add uncertainty;
- replace “It is wrong” with “That mechanistic decomposition is not supported by the profile analysis.”

The flow attribution at lines 175–179 should be removed or qualified as discussed above.

---

## Result 2

This is the strongest conceptual section. It should become the paper's statistical center.

### Add

- a two-dimensional inventory × rate objective surface;
- exact profiled inventory versus rate;
- uncertainty band or bootstrap profiles;
- profile sensitivity to flow map, endpoint, loss, and rate domain;
- all solutes and varieties, not one representative table only;
- the independent Table 7 inventory as a vertical or transformed constraint band with its uncertainty.

### Change

- “rate is not identifiable” → “rate is practically non-identifiable over the tested profile/domain.”
- “only tie-breaker” → “one available external tie-breaker.”
- Do not call a boundary result an optimizer “flip” without demonstrating numerical convergence.

---

## Result 3

This section must be fully regenerated after B1–B6. The corrected sequence should be:

1. O calibration profile;
2. frozen O parameters predicting matched 40 g C/F cups;
3. geometry sensitivity;
4. flow-map sensitivity;
5. joint shared-parameter fit with extended rate domain;
6. residual plots by `(T,p,grind,variety,solute)`;
7. comparison with per-grind fits using the same objective and endpoint.

Do not use the same-grind ~7% off-grid holdout as a direct comparator to the on-grid O-fit MAPE unless the difference in evaluation sets is made explicit.

---

## Result 4

The fraction-versus-endpoint concept is potentially the most broadly useful result, but the current endpoint is invalidly named. Rebuild it using actual full-cup data or a complete synthetic integration.

Show:

- profiles on a common log-rate axis;
- bootstrap envelopes;
- full-cup and sampled-window aggregate as separate curves if useful;
- exact number of experiments and replicate handling;
- whether minima remain near rate 1 across solutes;
- whether the conclusion survives alternative loss functions.

Replace “as it must” with “consistent with use of these data in calibration.” A calibration optimum need not land exactly at 1 after changing the objective, level treatment, or subset.

---

## Discussion

The practical message is good but overgeneralized. The Discussion should distinguish:

- what this case study directly shows;
- what is a model-based inference;
- what is a general experimental-design principle;
- what remains untested.

A more defensible central conclusion is:

> “In this case study, a low endpoint error did not uniquely determine the inventory/rate decomposition, and frozen-parameter transfer should be assessed separately. Temporal measurements and independent inventory information are promising ways to reduce that ambiguity.”

Avoid saying Angeloni's endpoint dataset makes the degeneracy “unbreakable.” Multiple endpoint conditions, independent priors, or a different model structure could still carry information.

---

## Open gaps

The manuscript is commendably transparent, but several listed “open gaps” are actually preconditions for the central claim. Move the following from future work into the current paper:

- profile uncertainty;
- condition-number or covariance analysis;
- measurement-uncertainty propagation;
- full-cup observable correction;
- matched-beverage-volume correction;
- rate-domain convergence;
- geometry sensitivity.

Independent fraction data can remain future work, provided the current result is labelled verification.

---

## Related work

Complete before submission. The current placeholder should not appear in a submitted draft.

---

## Reproducibility

Expand from a list of modules into a complete computational protocol. Include exact commands, commit, environment, input hashes, output paths, expected runtimes, and tolerances. Create a table mapping every manuscript number to a function and serialized output key.

---

# 7. Figures and tables required for a convincing revision

## Figure 1 — study and evidence design

A compact schematic showing:

- Pannusch/Schmieder fraction calibration;
- Angeloni O fit and O holdout;
- frozen O→C/F transfer;
- independent inventory constraint;
- fraction versus actual-cup comparison.

Label each arrow as calibration, internal holdout, external prediction, or in-sample verification.

## Figure 2 — inventory–rate objective surface

For at least caffeine and trigonelline:

- two-dimensional error contours;
- exact profiled minimum path;
- Table 7 inventory and uncertainty;
- bootstrap cloud or confidence region;
- sensitivity panels for flow/endpoint assumptions.

## Figure 3 — all O holdouts

Plot every observed and predicted off-grid O point, separated by solute and variety. Include uncertainty and show the distribution hidden by the ~7% mean.

## Figure 4 — matched-cup O→C/F transfer

For each solute:

- observed versus predicted concentrations by condition;
- residuals by grind;
- fixed-geometry and geometry-sensitivity versions;
- explicit 40 g termination.

## Figure 5 — joint-fit residual structure

A heat map by variety × solute × grind × condition, with:

- joint shared fit;
- per-grind fit;
- difference;
- rate-boundary flags.

## Figure 6 — fraction versus endpoint rate profiles

Use:

- fraction observations;
- actual BR 1/3 cup observations;
- optional sampled-window aggregate as a diagnostic;
- uncertainty envelopes and a common normalized objective scale.

## Table 1 — observable contract

| Quantity | Dataset | Analytical definition | Unit | Used for | Caveat |
|---|---|---|---|---|---|
| Fraction concentration | Schmieder/Pannusch | interval mass / interval beverage | mg/g | calibration/verification | selected windows |
| Full BR 1/3 cup | Schmieder | total component mass / cup mass | mg/g | endpoint comparison | separate replicates may apply |
| Bioactive cup concentration | Angeloni | reported beverage concentration | g/L | transfer target | duplicates/uncertainty |
| Total solids | Angeloni | source-specific gravimetric quantity | g/100 mL | proxy comparison | not identical to modeled pseudo-TDS |

## Table 2 — fit and validation accounting

For every solute × variety, report:

- number fitted;
- number held out;
- parameters fitted;
- loss;
- best rate and whether boundary-limited;
- fitted inventory;
- training error;
- each holdout error;
- bootstrap interval.

---

# 8. Required action plan

## Priority 0 — complete before interpreting the headline results

- [ ] Pin a commit and create a manuscript-specific reproducibility snapshot.
- [ ] Replace fixed 25 s cross-grind simulations with matched 40 ± 2 g beverage termination.
- [ ] Replace the six-window “whole cup” with actual BR 1/3 cup observations or a complete-shot reconstruction.
- [ ] Implement exact MAPE level profiling or validated continuous optimization.
- [ ] Add a structured rate-profile function and regenerate the Result 2 table.
- [ ] Extend the rate domain and resolve every boundary optimum.
- [ ] Rerun all headline numbers and rewrite the Abstract from the corrected outputs.

## Priority 1 — complete before journal submission

- [ ] Add shot-level bootstrap/profile uncertainty and parameter-correlation diagnostics.
- [ ] Separate practical non-identifiability from predictive transfer failure.
- [ ] Run flow-map and grain-geometry sensitivity analyses.
- [ ] Report all O holdouts rather than only the mean.
- [ ] Separate named solutes from TDS/total-solids proxy results.
- [ ] Test robustness to alternative objectives and measurement weighting.
- [ ] Synchronize code docstrings, output verdicts, analysis document, and manuscript.
- [ ] Complete the identifiability/inverse-problem related-work review.
- [ ] Add the figures and tables listed above.

## Priority 2 — manuscript and release polish

- [ ] Remove internal project instructions, ROADMAP references, G6 labels, and change-log prose from the paper body.
- [ ] Replace categorical rhetoric with evidence-bounded wording.
- [ ] Add standard Data Availability, Code Availability, Author Contributions, Competing Interests, and Funding sections as applicable.
- [ ] Verify all bibliographic details and complete the references.
- [ ] Archive generated data, figures, and logs with checksums.

---

# 9. Suggested claim hierarchy after correction

The revised paper should use a tiered claim structure.

## Claim supported now at a conceptual level

> Inventory and kinetic-rate parameters can compensate strongly in endpoint fits, so a low endpoint error need not uniquely determine a mechanism.

## Claim supportable after corrected profiling

> Under the tested single-grind endpoint design and objective, the inventory/rate profile is broad relative to measurement uncertainty.

## Claim supportable after corrected cross-grind rerun

> A frozen O calibration did or did not reproduce matched 40 g C/F targets under specified flow and geometry assumptions.

## Claim supportable by the current calibration-data comparison only after fixing the cup observable

> Fraction-resolved scoring localizes the rate profile more sharply than full-cup scoring on the model's calibration campaign.

## Claim not yet supported

> Whole-cup data generally identify only the inventory–rate product, or time-resolved data are the only possible way to separate them.

---

# 10. Example revised core wording

## Methods wording

> “At each kinetic-rate value, predictions are linear in the inventory level. For the MAPE objective, we profile the level using its exact weighted-median solution. We then evaluate the rate profile over a predeclared log-scale domain and quantify practical identifiability using shot-level bootstrap profiles. All cup predictions terminate at the observed target beverage mass.”

## Result 2 wording

> “The profiled endpoint objective remained broad across the tested rate domain, with compensating changes in inventory. We therefore regard rate and inventory as practically non-identifiable under this single-grind endpoint design, rather than interpreting the numerical optimum as a unique mechanistic estimate.”

## Transfer wording

> “Practical non-identifiability and predictive transfer were assessed separately. Parameters profiled on O were frozen and evaluated on matched-mass C/F cups. Performance is reported for fixed geometry and for a prespecified geometry-sensitivity range.”

## Positive-control wording

> “On the Schmieder calibration campaign, fraction-resolved scoring produced a more localized rate profile than scoring the corresponding full-cup observations. Because the model was calibrated on these fractions, this is an in-sample verification of information content, not an independent identification of the physical rate.”

## Discussion wording

> “The case study shows why endpoint accuracy, parameter identification, and frozen-parameter transfer should be reported as distinct properties. Independent inventory measurements, multi-condition designs, and temporal sampling can each reduce the ambiguity.”

---

# 11. Strengths to preserve

Despite the major revisions required, several aspects should be retained:

1. **The central question is important and generalizable.** Endpoint fit versus mechanistic identification is relevant well beyond espresso.
2. **The manuscript is unusually transparent about evidence strength.** The distinction among post-fit reconstruction, held-out checks, and verification is a strong foundation.
3. **Negative results remain visible.** The paper does not hide the failed cross-grind attempt.
4. **The independent inventory measurement is valuable.** It offers a concrete external constraint rather than an abstract identifiability discussion.
5. **The repository has strong provenance instincts.** Cards, data manifests, and explicit assumptions make the analysis auditable.
6. **The narrative hook is effective.** “The cup hides the clock” can remain, provided the empirical full-cup comparison is corrected and the claim is scoped.

---

# 12. Final recommendation

**Decision: major revision.**

The manuscript should not be submitted with the current numerical results or categorical identification/transfer language. The matched-beverage-mass error in the cross-grind calculation and the incomplete sampled-window “whole cup” directly affect the two main empirical pillars of the paper. The finite-grid implementation also contradicts the stated analytic profile and leaves boundary conclusions unresolved.

The paper is nevertheless promising. A corrected version could make a useful contribution if it centers on **practical parameter confounding, matched-observable validation, and the separation of fit, identification, and transfer**. The highest-value next step is not prose editing; it is to repair the observable contracts and regenerate the complete analysis with exact profiling and uncertainty.
