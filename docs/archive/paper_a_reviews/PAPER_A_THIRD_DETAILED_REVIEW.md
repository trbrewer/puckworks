# Third detailed technical review of the updated `PAPER_A_DRAFT.md`

**Repository:** `trbrewer/puckworks`  
**Repository URL:** <https://github.com/trbrewer/puckworks>  
**Commit reviewed:** `41b7d3640bd8ced298652b893da73029e9eebcda`  
**Commit title:** `paper-a: 2nd-review P0 fixes — MAPE bug, manifold test, taxonomy, build, report keys`  
**Draft revision stated in file:** 2026-07-12  
**Review date:** 2026-07-13  
**Review type:** third-round manuscript, figure, code-path, numerical-contract, provenance, and statistical-interpretation review  
**Overall recommendation:** **Major revision before journal submission**

---

## 1. Executive assessment

The updated Paper A is materially stronger than the version assessed in the second review. The revision fixes the definite tuple-indexing error in the MAPE profile, adds an explicit transfer calculation over a near-optimal O-grind parameter set, improves the evidence taxonomy, relabels the leave-one-condition-out resampling summaries as descriptive rather than coverage-calibrated confidence intervals, adds previously omitted analyses to the paper-build result bundle, and repairs the executable report path. The manuscript now makes several important distinctions correctly: target-data refitting is not a blind external prediction; the O→C/F exercise is a within-campaign cross-grind holdout; the joint O+C+F fit is an in-sample parameter-sharing compatibility analysis; Table 7 is a same-campaign orthogonal measurement; and the Waszkiewicz analysis profiles a target-specific level and therefore tests temporal shape rather than frozen absolute concentration.

The central qualitative result remains plausible and potentially useful: **whole-cup observations can leave inventory and kinetic rate weakly separated even when a selected calibration gives modest absolute held-out errors.** The corrected SSE and MAPE profiles both support a broad inventory–rate compensation region under the tested observation map. Time-resolved fraction scoring is more rate-sensitive than the corresponding aggregate in the in-sample and same-model examples. These are worthwhile observations for mechanistic espresso-model evaluation.

However, the current revision still does not justify its headline predictive-transfer language. The most important new finding in this review is that the reported O→C/F model errors are almost reproduced by a trivial level-only benchmark that contains no pressure, temperature, hydraulic, or kinetic response. Using the committed Angeloni on-grid data and the manuscript's reported per-fit model MAPEs, an O-trained MAPE-optimal constant gives a C/F macro-MAPE of approximately **8.59%**, compared with approximately **8.23%** for the mechanistic transfer—an improvement of only **0.36 percentage points** (about 4.2% relative). The mechanistic result is worse than the constant in **5 of 12** variety × solute × held-out-grind comparisons and is slightly worse on grind F in aggregate. Likewise, the in-sample joint shared model reports 6.4% versus approximately 7.11% for a single constant per variety × solute across all three grinds, while the independent per-grind mechanistic fits report 4.9% versus approximately 5.05% for independent per-grind constants. These checks use rounded model scores because full-precision model predictions are not exported, so they are diagnostic rather than final; nevertheless, they show that **low absolute MAPE is not yet evidence of useful mechanistic transfer skill**. A baseline and skill-score analysis is therefore submission-blocking.

The newly added “whole near-optimal set” transfer is also narrower than the prose suggests. It propagates only the 8–15 discrete points, depending on solute/variety, that fall within 10% of the minimum on an 18-point rate grid. It does not establish a continuous manifold, does not demonstrate grid/domain convergence, uses a relative threshold whose meaning depends strongly on the minimum error, and reports only aggregate MAPE summaries rather than condition-wise predictive bands. The formal identifiability panel is based on SSE while the transfer set is defined by MAPE, so the manuscript should not treat the two sets as interchangeable without showing their overlap.

Several previously claimed implementation fixes are also incomplete. `geometry_sensitivity_transfer()` still rounds each held-out MAPE to an integer before calculating the spread, and `joint_multigrind_fit()` stores rounded independent per-grind MAPEs and then uses those rounded values in the headline independent mean. The refit summary similarly aggregates already rounded per-fit values. Consequently, the advertised “≤1 pp geometry sensitivity,” the 4.9% independent-fit comparator, and some cost-of-sharing values must be regenerated from unrounded internal arrays.

The identifiability language remains stronger than the numerical support. The 10%-of-minimum SSE profile reaches the upper rate-domain boundary, so the upper extent is right-censored by the tested domain; `profile_log_width` is therefore not domain-independent. The manuscript's statement that there is “no bounded minimum under either objective” conflicts with the code's interior SSE optimum and should instead say that the **near-optimal region is not closed within the tested domain**. The local Hessian is evaluated by finite differences on a relatively coarse grid and has not been checked against grid density, finite-difference step, parameter scaling, or a continuously optimized profile.

The figures have not caught up with the revised argument. Figure 4 shows only point-optimum predictions and neither the new near-optimal-set envelope nor a null benchmark. Figure 6 plots the seed-0 same-model simulation profile even though the text reports 20-seed means and standard deviations, and it omits the external Waszkiewicz profile despite that analysis carrying substantial weight in the abstract and Section 6. Figure 2 does not show the corrected MAPE profile or indicate that the SSE tolerance set reaches the tested boundary. Figure 3 and Figure 4 display strikingly horizontal prediction clusters, which visually reinforce the need for a level-only comparator.

The appropriate disposition remains **major revision**. The paper should not be rejected on conceptual grounds: the practical-confounding result is credible enough to warrant a properly controlled analysis. But the current manuscript should not claim that the model “transfers reasonably,” that the compensation is prediction-invariant, or that the cup-vs-fractions evidence establishes more than the scoped analyses actually show until the baseline, continuous-profile, numerical-convergence, uncertainty, and figure-synchronization actions below are completed.

---

## 2. Scope, materials reviewed, and limitations

### 2.1 Repository snapshot and files reviewed

I reviewed the raw `main`-branch state represented by commit `41b7d3640bd8ced298652b893da73029e9eebcda`, including:

- `docs/PAPER_A_DRAFT.md`;
- `puckworks/validation/slow/angeloni_bracket.py`;
- `puckworks/validation/slow/identifiability.py`;
- `puckworks/validation/slow/external_waszkiewicz.py`;
- `puckworks/figures_paper_a.py`;
- `puckworks/tests/test_paper_a.py`;
- the committed Angeloni bioactive table used by the analysis;
- the cached Paper A result bundle exposed through the figure build;
- all six current PNG figures:
  - `fig1_design.png`;
  - `fig2_objective_surface.png`;
  - `fig3_holdouts.png`;
  - `fig4_transfer.png`;
  - `fig5_joint_residual.png`;
  - `fig6_fraction_vs_endpoint.png`.

I compared the revision with the previous Paper A review and with the repository commit that explicitly states which second-review actions it intended to resolve. I also checked source-study descriptions and interpretive terminology against the primary Schmieder, Pannusch, Angeloni, Waszkiewicz, identifiability, profile-wise prediction, and cross-validation literature listed in Section 13.

### 2.2 Review method

The review combined:

1. **Static code tracing.** Each major manuscript claim was traced to the analysis function and returned result field that supports it. Particular attention was paid to objective definitions, nuisance-level profiling, parameter grids, boundary handling, train/test separation, aggregation order, rounding, uncertainty labels, and evidence taxonomy.
2. **Figure inspection.** Every figure was assessed for units, evidence classification, whether the plotted quantity matches the prose, whether uncertainty or boundary censoring is visible, and whether the visual display supports the title/caption.
3. **Targeted independent recomputation.** I independently computed simple level-only benchmarks from the committed Angeloni data and compared them with the reported cross-grind and in-sample mechanistic MAPEs. This check is data-only and does not require rerunning the PDE solver.
4. **Change audit.** I compared the current implementation against the previous review's P0/P1 findings and against the current commit message's claims of resolution.
5. **Literature-grounded interpretation.** Profile analysis, prediction propagation, and cross-validation uncertainty were assessed using primary methodological sources rather than treating local objective curvature or resampled fold errors as conventional inferential quantities.

### 2.3 Important limitation of this review

I did **not** perform a clean-room rerun of every slow PDE analysis in a newly provisioned, fully pinned environment. The repository still lacks the frozen `paper-a-v1.0.0` release and environment lock that the manuscript itself says are owed. Findings described as code defects or figure/manuscript mismatches are established directly by inspection. Findings that depend on solver outputs are framed as required reruns unless they are present in the committed result bundle. The independent benchmark comparison uses the manuscript's rounded per-fit model MAPEs, so its exact numerical differences may shift slightly when full-precision model predictions are exported; the qualitative conclusion—that the mechanistic scores are extremely close to a constant-level benchmark—should be tested, not assumed away.

### 2.4 Artifact hashes

| Artifact | SHA-256 |
|---|---|
| `PAPER_A_DRAFT.md` | `52786f670f1e4e899089582f57b6bba8ac2af5a89e94934254ff99a1a8311087` |
| `angeloni_bracket.py` | `6dc590a562059a9788d4a21dcb083fb9ed3f88fb043851aad38aaba87602b046` |
| `identifiability.py` | `69837e516710dfb99d412b1d39061275780fc001a3ce1f0fdab460e588f09ad0` |
| `external_waszkiewicz.py` | `5eef3dd2ee63e743c2319e5e055009faf7f8d2fd957a81475a80ed125701ef85` |
| `figures_paper_a.py` | `4bb44d34f6beb935870da42a896db2e91028b23e061fce4e99b35f3f99ea49be` |
| Figure 1 | `18169a507f30334a051426d46f115132213b82e9f742bb42031562a8f54a75c4` |
| Figure 2 | `5909830e3bb939d72adcf1b7b01fe00d3860ec3995d378d13174fc8f569da759` |
| Figure 3 | `710f7b1feebf61dd2add5d664cbc91bb115cf243eef2a0e04705c16f41c6d4fb` |
| Figure 4 | `aef8d395259973e0a6edb169abfa62a58aff325cc1eec06b7497724f1c5a83c2` |
| Figure 5 | `0d22355e3ebc6661f0116c3aeec5779b96ad6e7b4fc2fac461c93307297954f6` |
| Figure 6 | `da080beb9e063f6aaef57e600d08ac746a2ce3a10a9b9f5eb6ff17a5e0a6b70d` |

These hashes should ultimately be superseded by a tagged release, archived source bundle, environment lock, and persistent DOI.

---

## 3. Progress since the previous Paper A review

| Previous-review issue | Current status | Assessment |
|---|---:|---|
| MAPE profile mixed nuisance levels and MAPEs | **Resolved in code** | `identifiability_panel()` now extracts `_mape_level(...)[1]`, and a structural unit test guards one-dimensional profile construction. Numerical profile claims were regenerated. |
| “Stable along the compensating manifold” was asserted from one point | **Partly resolved** | A near-optimal O-grind set is now transferred to C/F. This is meaningful progress, but the set is a coarse 18-grid-point MAPE threshold subset, not a demonstrated continuous manifold or a profile-wise prediction set with uncertainty. |
| O→C/F, Table 7, and joint fit evidence classes were overstated | **Largely resolved in manuscript and Figure 1** | The manuscript now uses within-campaign holdout, same-campaign orthogonal measurement, and in-sample compatibility terminology. Several code docstrings and `strength` fields remain stale. |
| Condition-cluster bootstrap called dependence-aware CI | **Resolved in wording** | Both resampling summaries are now explicitly descriptive and non-coverage-calibrated. The manuscript still should avoid calling them “interval estimates” without the adjective descriptive. |
| Paper build omitted Result 1 analyses | **Resolved structurally** | `compute_all()` now invokes the refit, bracket, flow-map, geometry, sampled-aggregate, and external analyses. A clean-environment deterministic build and source-data export remain missing. |
| Precision retained only after rounding | **Not fully resolved** | The point-transfer path retains more precision, but geometry sensitivity still rounds to integers before spread calculation, and the joint comparator averages rounded independent values. Refitted headline means also derive from rounded per-fit fields. |
| Exact-cup report keys were broken | **Resolved** | The command-line report path now uses current result keys. Figure 6 still shows only seed 0 while prose reports the 20-seed ensemble. |
| Table 7 called external tie-breaker | **Resolved in manuscript** | It is now correctly called a same-campaign orthogonal measurement. The quantitative constraint it places on the rate profile remains uncomputed. |
| Stale “correlation” and “dependence-aware” language | **Mostly resolved** | Main text uses inverse-curvature coupling and descriptive resampling. Stale transfer/evidence language remains in analysis docstrings and strength tags. |
| Grid/domain convergence, weighted objective, density sensitivity, flow-map uncertainty | **Explicitly deferred** | These are not optional polish: they directly qualify the key identifiability and transfer claims and remain major actions. |
| Figure redesigns | **Not resolved** | Figure 4 and Figure 6 are materially inconsistent with the revised central claims; Figure 2 lacks boundary/MAPE information. |
| Manuscript conversion | **Not resolved** | The draft still reads as an internal repository handoff, with review IDs, code function names, “owed” analyses, change-log language, and an open-gap ledger in the manuscript body. |

---

## 4. Independent benchmark check: does the model add predictive skill beyond a constant level?

### 4.1 Why this check is necessary

The manuscript's transfer argument is based primarily on absolute MAPE. But a low absolute error can arise when concentrations are stable across operating conditions, even if the model contributes little condition-specific signal. Figures 3 and 4 visibly show nearly horizontal prediction bands within each solute/variety group. Therefore, the relevant question is not only “is MAPE below a chosen number?” but also:

> Does the mechanistic model improve held-out prediction over a simple, predeclared baseline fitted only on the same O-grind training data?

A baseline is especially important here because the model profiles a free multiplicative inventory level. A constant predictor is the simplest model that captures only that level and none of the kinetic, temperature, pressure, flow, or grind response.

### 4.2 Baselines evaluated

For each variety × named-solute combination, I calculated:

1. **O-trained MAPE-optimal constant.** A single constant concentration fitted to the nine on-grid O observations by the exact weighted-median solution for MAPE, then applied unchanged to all C and F observations.
2. **O same-condition lookup.** For each held-out C/F point, the observed O concentration at the same temperature and pressure. This uses no mechanistic model and tests whether the same-campaign O response itself transfers across grind.
3. **Shared all-grind constant, in sample.** One MAPE-optimal constant per variety × solute fitted to all O+C+F observations, compared with the joint shared mechanistic fit.
4. **Independent per-grind constants, in sample.** One MAPE-optimal constant per variety × solute × grind, compared with the independent per-grind mechanistic fits.

The model values below are the committed rounded per-fit MAPEs, because the result bundle does not export a full-precision model-prediction table for all comparisons. Final manuscript values must be recomputed from unrounded point predictions.

### 4.3 Headline results

| Comparison | Mechanistic MAPE | Simple baseline MAPE | Mechanistic improvement | Reading |
|---|---:|---:|---:|---|
| O-trained → C/F macro, 12 fit×grind cases | **8.23%** | **8.59%** (O-trained constant) | **0.36 pp**; about 4.2% relative | Very small incremental skill |
| Held-out C only | **10.30%** | **11.25%** | **0.95 pp** | Modest improvement |
| Held-out F only | **6.16%** | **5.93%** | **−0.23 pp** | Constant is slightly better |
| O-trained → C/F macro | **8.23%** | **10.79%** (same-T,p O lookup) | **2.57 pp** | Better than this stronger but noisier lookup |
| Joint O+C+F, in sample | **6.40%** | **7.11%** (one all-grind constant) | **0.71 pp**; about 10.0% relative | Small in-sample gain |
| Independent per-grind, in sample | **4.90%** | **5.05%** (per-grind constants) | **0.15 pp**; about 2.9% relative | Essentially tied at reported precision |

The mechanistic transfer is worse than the O-trained constant in **5 of 12** variety × solute × held-out-grind cases. The largest mechanistic improvement occurs for Arabica 5-CQA on C; the model is worse than the constant for Arabica trigonelline on F and Arabica 5-CQA on F, and approximately tied in several Robusta cases.

### 4.4 Per-case diagnostic table

| Variety | Solute | Held-out grind | Model MAPE | O-trained constant MAPE | Model − constant (pp) |
|---|---|---:|---:|---:|---:|
| Arabica | caffeine | C | 8.48 | 9.61 | −1.13 |
| Arabica | caffeine | F | 5.37 | 5.53 | −0.16 |
| Arabica | trigonelline | C | 6.83 | 7.76 | −0.93 |
| Arabica | trigonelline | F | 3.19 | 2.15 | **+1.04** |
| Arabica | 5-CQA | C | 18.21 | 22.09 | −3.88 |
| Arabica | 5-CQA | F | 5.02 | 3.56 | **+1.46** |
| Robusta | caffeine | C | 9.51 | 9.50 | **+0.01** |
| Robusta | caffeine | F | 7.47 | 7.32 | **+0.15** |
| Robusta | trigonelline | C | 8.50 | 8.25 | **+0.25** |
| Robusta | trigonelline | F | 7.14 | 7.67 | −0.53 |
| Robusta | 5-CQA | C | 10.27 | 10.29 | −0.02 |
| Robusta | 5-CQA | F | 8.75 | 9.33 | −0.58 |

Negative differences favor the mechanistic model; positive differences favor the constant.

### 4.5 Consequence for the manuscript

This check does **not** prove that the mechanistic model has no useful predictive content. It demonstrates that the current absolute-error presentation cannot distinguish mechanistic transfer from stable group-level concentration. The analysis must be rerun with full-precision point predictions and predeclared baselines, and should report at least:

- absolute MAPE for each model and baseline;
- a skill score such as `1 − loss_model/loss_baseline`;
- paired point-level or condition-level loss differences;
- uncertainty or a descriptive distribution of those differences;
- results separately for C and F, not only a pooled macro-average;
- whether the model reproduces *changes across temperature and pressure* better than the baseline.

Until then, replace “transfers reasonably” with a neutral statement such as “produced 3–18% absolute MAPE in the held-out grinds, but incremental skill over simple level-only baselines has not yet been established.”

---

## 5. Prioritized required-action matrix

### 5.1 Submission-blocking actions

| ID | Priority | Finding | Required action | Acceptance criterion |
|---|---:|---|---|---|
| **A3-01** | **P0** | Absolute MAPE is almost matched by a constant-level baseline | Add O-trained constant, same-condition O, and other predeclared null/reference models; report skill scores and paired loss differences from full-precision point predictions | The mechanistic model shows a clearly quantified advantage over a declared baseline, or all transfer claims are narrowed to absolute fit quality without mechanistic-skill language |
| **A3-02** | **P0** | “Whole manifold” transfer is a coarse 18-point MAPE-threshold subset | Construct a grid-converged or continuously optimized profile-wise prediction set, state the threshold rationale, propagate it to condition-level C/F predictions, and show the result | Rate/profile bounds and predictive envelopes are stable to grid density/domain; Figure 4 displays point and profile-set predictions; worst/quantile errors are based on unrounded values |
| **A3-03** | **P0** | Round-before-aggregate defects remain in geometry, joint, and refit summaries | Preserve full precision in internal result objects and round only at presentation; rerun all affected manuscript numbers | Code tests fail if rounded values enter any aggregate; geometry spread, independent mean, cost of sharing, and Result 1 means are regenerated |
| **A3-04** | **P0** | Profile set reaches the tested boundary and Hessian robustness is unverified | Perform grid/domain/finite-difference/scaling convergence; report right-censoring; remove “no bounded minimum under either objective” unless demonstrated | Profile limits touching boundaries are labeled open/censored; condition number and coupling are accompanied by sensitivity results; no domain-independent width claim remains |
| **A3-05** | **P0** | Figures do not display the new central evidence | Redesign Figure 4 to show profile-wise envelopes and baselines; Figure 6 to show the 20-seed ensemble and the external Waszkiewicz panel; Figure 2 to show boundary/MAPE information | Every headline quantitative claim is visibly represented in a figure or table generated from one result bundle; captions match the displayed evidence |
| **A3-06** | **P0** | External Waszkiewicz evidence is target-profiled, weakly localized, and partly algebraic | Reframe as external-data shape-objective localization; propagate measurement/alignment/operator assumptions; stop using the single-cup flat profile as empirical evidence | Text and code use one taxonomy; fraction minimum/error and sensitivity are shown; cup flatness is explicitly described as one scalar plus one free level, not a validation result |
| **A3-07** | **P0** | “Matched 40 g” is implemented as 40 mL, with endpoint, flow, and measurement uncertainty unpropagated | Implement mass-consistent termination or state matched-volume approximation; vary density and 38–42 g endpoint; propagate flow-map/geometry/measurement sensitivity | Main conclusions survive a declared uncertainty package, or claims are explicitly conditional; axes and captions use correct endpoint terminology |
| **A3-08** | **P0** | Draft remains an internal project note and lacks a frozen reproducible submission package | Convert to conventional manuscript; add complete Methods, equations, references, data/code availability, environment lock, tagged release, source data, and vector figures | Submitted file contains no review IDs, “owed” ledger, code-function prose, repository note, or change-log instructions; one clean command reproduces all tables/figures |

### 5.2 Major analytical actions

| ID | Priority | Finding | Required action | Acceptance criterion |
|---|---:|---|---|---|
| **A3-09** | P1 | Formal identifiability uses SSE while the transfer set uses MAPE | Show both profiles on a common rate axis, quantify overlap, and state which set underlies each claim | “The valley” is not used as if SSE and MAPE sets were identical; sensitivity to objective is explicit |
| **A3-10** | P1 | The 10%-of-minimum threshold is arbitrary and minimum-dependent | Add absolute-error, measurement-error, or likelihood/noise-model-based thresholds; at minimum provide threshold sensitivity | Conclusions are shown over several declared tolerances, and the chosen primary threshold is justified before interpreting “stable” |
| **A3-11** | P1 | Transfer envelopes are reported only as aggregate MAPEs | Export condition-level predictions for every profile point or representative boundary points | Prediction bands by T, p, grind, solute, and variety are available; failures are not hidden by averaging |
| **A3-12** | P1 | Source measurement uncertainty is disclosed but unused | Fit/score with a justified heteroscedastic error model or perform RSD-weighted sensitivity | Profile and transfer findings are robust to plausible source uncertainty, or uncertainty limits are clearly stated |
| **A3-13** | P1 | Table 7 is shown as a visual line but its rate constraint is not quantified | Intersect the inventory measurement and uncertainty with the profiled path and derive the implied rate range | Manuscript reports the constrained rate/range and explicitly states same-campaign dependence |
| **A3-14** | P1 | “Identifiability ratio” is a range- and grid-dependent sharpness heuristic | Rename it descriptive profile range ratio, show domain/grid/noise sensitivity, and avoid categorical “identified/not identified” thresholds | No universal decision interpretation remains; rates and error profiles are reported directly |
| **A3-15** | P1 | Same-model exact-cup simulation is an inverse crime and uses only one discrepancy-free design | Add model-discrepancy, endpoint, flow, geometry, noise-model, and candidate-grid sensitivities | The contrast survives realistic mismatch scenarios; otherwise it remains a scoped synthetic illustration |
| **A3-16** | P1 | The synthetic truth rate is exactly on the candidate grid | Repeat with off-grid truth and continuous optimization or interpolation | Recovery is not an artifact of including the true rate among nine candidates |
| **A3-17** | P1 | The exact-cup terminal time is the last available fraction bound, not necessarily a documented complete shot endpoint | Verify the physical endpoint or relabel as exact integral over the modeled terminal window | “Whole cup” is used only if the source endpoint is established; otherwise wording is “integrated modeled window” |
| **A3-18** | P1 | Waszkiewicz assumptions are narrow | Vary temperature, density conversion, flow floor, time origin, binning, first-bin treatment, and uncertainty weighting | External profile range and best-rate sensitivity are tabulated; conclusions use the weakest robust wording |
| **A3-19** | P1 | Joint compatibility result has no adequacy criterion | Predefine acceptable error/skill and compare shared model with constants and reduced models | “Shared calibration exists” is based on declared performance and skill, not only a post hoc ≤3 pp rule |
| **A3-20** | P1 | Geometry test sweeps a global geometry rather than a grind-specific mapping | Distinguish global-geometry sensitivity from uncertainty in the O/C/F geometry map; test plausible grind-specific combinations | Claim is limited to the tested global sweep or expanded with a justified cross-grinder uncertainty model |
| **A3-21** | P1 | LOCO uncertainty remains descriptive and folds overlap | Keep it descriptive or implement a resampling design that repeats fitting and matches the inferential target | No conventional 95% CI language is used without a validated scheme; paired baseline differences are included |
| **A3-22** | P1 | Only caffeine and trigonelline receive formal surface panels | Add all solute × variety profiles to supplement and report boundary flags | Headline practical-confounding statement is demonstrably representative rather than selected |

### 5.3 Manuscript, figure, and software-quality actions

| ID | Priority | Finding | Required action | Acceptance criterion |
|---|---:|---|---|---|
| **A3-23** | P1 | Code docstrings and strength tags contradict the manuscript taxonomy | Replace “REAL transfer test,” “external stress test,” “external prediction,” and “negative validation” with current evidence terms | Automated terminology test or review confirms manuscript, code, JSON, and captions use one vocabulary |
| **A3-24** | P1 | Paper-A-specific tests cover only a few structural guards | Add tests for aggregation precision, profile-set construction, boundary censoring, baseline calculation, figure/result synchronization, and deterministic result schema | Regression tests fail on the defects identified in this review |
| **A3-25** | P1 | PNG figures lack machine-readable source tables and vector versions | Export SVG/PDF plus tidy CSV/Parquet source data for every panel | Build emits vector and raster figures and one documented source-data file per figure |
| **A3-26** | P2 | Figure titles embed conclusions and subjective adjectives | Use neutral titles and move interpretation to captions/results | No title says “transfers reasonably,” “robust,” or equivalent without displaying the comparison |
| **A3-27** | P2 | References are prose mentions rather than a finished bibliography | Generate a complete journal-style bibliography and verify metadata | Every in-text citation resolves to a reference; Angeloni is correctly cited as *Applied Sciences* 13(4), 2688 |
| **A3-28** | P2 | “Open gaps” and revision history occupy manuscript space | Move project-management material to repository documentation or supplement | Main manuscript contains scientific limitations and future work, not an implementation ledger |

---
## 6. Detailed major comments

### 6.1 A3-01 — the central transfer claim lacks a null benchmark

**Locations:** Abstract lines 36–46; Result 3; Discussion lines 449–469; Figure 4; `validate_refit_granulometry()`.

The manuscript currently interprets held-out absolute MAPE of approximately 3–18% as “reasonable” cross-grind prediction and uses that result to argue that parameter non-identifiability can coexist with predictive transfer. That conceptual distinction is valid in principle, but the current analysis has not shown that the model's *condition-dependent predictions* add information beyond a fitted level.

The independent check in Section 4 shows why this matters. A constant concentration fitted to O and frozen for C/F achieves approximately 8.59% macro-MAPE, nearly the same as the reported model value of 8.23%. On F, the constant is slightly better in aggregate. The point clouds in Figure 4 are consistent with this: within each species/variety cluster, predictions occupy narrow horizontal bands while observations vary more broadly. A low MAPE in such a design may reflect stable analyte levels rather than successful transport/kinetic extrapolation.

This is not a cosmetic comparison. The main claim is about **predictive transfer despite parameter non-identifiability**. To establish predictive transfer, the analysis should show that the mechanistic model predicts held-out variation better than a reasonable reference available at prediction time. At minimum include:

- a constant fitted to O by the same loss;
- the O concentration at the same T,p condition;
- a variety × solute mean or median;
- a reduced model with level plus simple grind offset, if that offset is estimable without C/F target leakage;
- optionally, an Angeloni-style empirical response surface trained only on O, with limitations stated.

Report `MAPE_model`, `MAPE_baseline`, and a skill score. A useful simple score is

```text
skill = 1 − loss_model / loss_baseline,
```

where positive values favor the model, zero means no improvement, and negative values mean the baseline is better. Because the test set is small and losses are structured by condition, provide paired point-level or condition-level differences rather than relying only on a macro-average.

**Required action:** Make the baseline comparison part of the primary Results and Figure 4. If the model does not materially beat the baseline, the scientifically interesting result may become: *the endpoint design permits both a mechanistic model and a trivial level model to obtain similar held-out error, reinforcing that endpoint MAPE does not diagnose mechanism*. That would remain publishable and may sharpen the paper's argument, but it is different from “the model transfers reasonably.”

---

### 6.2 The joint shared-fit result also needs reduced-model benchmarks

**Locations:** Abstract lines 44–46; Result 3; Figure 5; `joint_multigrind_fit()`.

The shared O+C+F fit is presented as an in-sample compatibility result, which is a welcome correction. But its numerical interpretation still relies on comparison with more flexible per-grind mechanistic fits, not with simpler models. A single constant per variety × solute across all three grinds obtains approximately 7.11% MAPE, versus the reported 6.4% for the shared mechanistic model. Independent per-grind constants obtain approximately 5.05%, versus 4.9% for independent per-grind mechanistic fits. At the current displayed precision, the independent fits are essentially tied with constants.

This implies that the 1.5 pp “cost of sharing” is not necessarily evidence that a shared mechanistic calibration describes the cross-grind structure. It may largely be the cost of forcing one level across grinds that have slightly different mean concentrations. Figure 5 should therefore add at least one reduced-model comparator and distinguish:

1. improvement from allowing a different level per grind;
2. improvement from the mechanistic T/p/flow response within a grind;
3. improvement from a shared kinetic response across grinds.

A nested or hierarchical decomposition would be clearer than comparing only the two mechanistic variants. For example:

- Model 0: one constant per variety × solute;
- Model 1: one constant per variety × solute × grind;
- Model 2: mechanistic model with shared inventory/rate;
- Model 3: mechanistic model with separate inventory/rate per grind.

Report parameter counts, in-sample loss, and a penalized or held-out comparison where possible. This would expose whether mechanistic structure explains variation beyond level shifts.

---

### 6.3 “Reasonably” is a post hoc, undefined performance criterion

**Locations:** Abstract lines 38–44; Result 3 verdict; Figure 4 title; Discussion lines 449–469.

The code classifies a shared fit as reasonable when the cost of sharing is ≤3 percentage points, but that threshold appears to be introduced after observing the result. The manuscript also calls 3–18% point-optimum MAPE and a ~22% worst profile-set MAPE “reasonable” without a declared domain-specific acceptance criterion. This makes the interpretation difficult to audit.

The source Angeloni paper's own model errors are not automatically an appropriate threshold because the model, fitting target, predictors, and validation design differ. A defensible criterion could be based on:

- performance relative to null and reduced models;
- source analytical repeatability or RSD;
- an application-relevant concentration tolerance;
- a preregistered absolute threshold;
- or an explicit statement that no pass/fail threshold is claimed and only raw errors are reported.

**Required action:** Remove subjective adjectives from figure titles and primary conclusions unless a threshold is declared before inspection. Prefer neutral statements such as “point-optimum macro-MAPE was X, profile-set worst-case MAPE was Y, and skill relative to the O-trained constant was Z.”

---

### 6.4 A3-02 — the “whole manifold” is a coarse discrete threshold set

**Locations:** Abstract lines 39–44; Result 3; `validate_refit_granulometry()` lines 528–584.

The new analysis is a real improvement: it no longer transfers only one selected optimum. But the implementation evaluates `_RATE_DOMAIN = geomspace(0.15, 6.5, 18)` and defines `near = mpsO <= 1.10 * min(mpsO)`. Depending on fit, only 8–15 of these 18 grid points enter the set. Calling this the “entire near-optimal set,” the “whole valley,” or a “compensating manifold” implies a continuous, grid-converged object that has not been demonstrated.

Three limitations matter:

1. **Discretization.** A narrow excursion between sampled rates or beyond the current boundary could be missed. Percentiles over 8–15 deterministic grid points are not distributional quantiles in the usual statistical sense.
2. **Threshold dependence.** A 10% relative increase can represent a very small absolute loss difference when the minimum MAPE is low, and a much larger difference when it is high.
3. **Domain censoring.** Some profile sets may extend to a tested boundary; the predictive envelope may expand if the domain is widened.

Profile-wise prediction literature treats parameter-profile sets and their propagated predictions as explicit objects whose construction and uncertainty basis must be stated. Here there is no likelihood or confidence set, which is acceptable, but the manuscript should call it a **declared near-optimal grid set**, not a confidence manifold.

**Required analysis:**

- compute a much denser rate profile or use continuous one-dimensional optimization/interpolation;
- show convergence at, for example, 18, 36, 72, and 144 rate points;
- widen the rate domain until the threshold set closes or label it censored;
- repeat for several tolerances, such as 2%, 5%, 10%, 20%, and an absolute MAPE increment;
- export the rate interval, profiled inventory, O loss, and C/F loss at every retained point;
- propagate to each held-out condition, not only an aggregate MAPE;
- report profile-wise minima, maxima, and boundary cases, not p5/p95 of a small deterministic set as if they were uncertainty quantiles.

---

### 6.5 The formal SSE profile and the MAPE transfer set are not the same valley

**Locations:** Methods 2.6; Result 2; Result 3; `identifiability_panel()` and `validate_refit_granulometry()`.

The formal identifiability panel profiles unweighted concentration-scale SSE using a least-squares inventory level. The new transfer set profiles MAPE using a weighted-median inventory level. Both objectives can produce broad compensation regions, but their optima and near-optimal sets need not coincide. The manuscript currently moves between “the SSE valley,” “the MAPE cross-check,” and “the whole compensating manifold” without showing how the sets overlap.

The corrected MAPE profile fraction is useful, but the boolean `mape_cross_check_agrees` is defined as both profile fractions exceeding 0.30. That is an arbitrary flat/not-flat rule, not a quantitative agreement metric.

**Required action:** Plot SSE and MAPE profiles on the same rate axis, with their profiled inventory paths and declared threshold sets. Report:

- rate of the minimum under each objective;
- overlap of the two threshold sets;
- maximum difference in profiled inventory;
- C/F predictions propagated from each set;
- sensitivity of conclusions to objective choice.

Then refer specifically to the “MAPE-defined near-optimal set” or “SSE-defined tolerance set.” Avoid using one generic “manifold” label for both.

---

### 6.6 Aggregate profile-set MAPE does not establish prediction stability at every condition

**Locations:** `validate_refit_granulometry()` lines 548–584; Abstract and Result 3.

The current manifold transfer stores only aggregate MAPE values for each retained parameter pair. A parameter pair could leave the mean MAPE nearly unchanged while substantially changing predictions at a subset of T,p conditions, especially if errors cancel across conditions or if one solute dominates the maximum.

The manuscript's claim that compensation is “approximately prediction-invariant” should be evaluated at the prediction level. For each held-out condition, calculate the range of predicted concentration across the profile set and compare it with:

- observed concentration;
- analytical uncertainty where available;
- point-optimum prediction;
- O-trained constant prediction;
- a declared practical tolerance.

A useful figure would show, for each C/F observation, the point-optimum prediction and a vertical profile-wise prediction interval/envelope. If the profile set is not probabilistic, call it an **envelope**, not a confidence interval. Report the maximum and median envelope width as a fraction of the observation.

This distinction is central to the paper: parameter non-identifiability can coexist with prediction stability only if the predictions themselves are shown to remain stable across the admissible/profile set.

---

### 6.7 A3-03 — geometry sensitivity still rounds before calculating spread

**Location:** `geometry_sensitivity_transfer()` lines 946–963.

The current code calculates each held-out MAPE and immediately applies `round(..., 0)`, then constructs the minimum, maximum, and maximum spread from those integer values. This directly contradicts the commit message and comments claiming full precision through geometry aggregation. A true spread of, for example, 1.8 pp can appear as 1 pp or 2 pp depending on rounding direction; a spread below 1 pp can be rounded to 1 pp; and several different geometries can collapse to identical integers.

The manuscript and Figure 4 advertise “≤1 pp geometry-sensitive,” and the verdict calls the conclusion robust. That number is not presently auditable at sub-percentage-point precision.

**Required correction:** Store raw floats:

```python
held[g] = float(np.mean(np.abs(c * f - m) / m) * 100.0)
```

Compute all spreads from raw floats. Round only when rendering a table or sentence. Add a regression test with synthetic values that differ by less than one percentage point and verify that the returned spread preserves the difference.

Also narrow the interpretation: the current routine tests **one global geometry choice applied to all grinds**. It does not quantify uncertainty in a grind-specific geometry map between the Pannusch and Angeloni grinders. Even after the rounding fix, describe the result as “limited sensitivity to the tested global Pannusch geometry choices,” not broad robustness to geometry.

---

### 6.8 The joint independent-fit comparator still averages rounded values

**Location:** `joint_multigrind_fit()` lines 446–462.

The function computes full-precision independent per-grind minima in `indep`, but stores each value rounded to one decimal in `independent_per_grind_mape`. The headline `indep_mean` is then computed from this rounded dictionary. Therefore, the comment that the pooled values are based on full precision is only partly true: the joint numerator is full precision, while the independent comparator is not.

Because the reported cost of sharing is only ~1.5 pp, tenth-point rounding before aggregation is not negligible. The same issue affects Figure 5 and any baseline comparison.

**Required correction:** Keep separate internal fields, for example:

```python
independent_per_grind_mape_raw = indep
independent_per_grind_mape = {g: round(v, 1) for g, v in indep.items()}
```

and compute `indep_mean` and `cost` from the raw values. Better still, make the result bundle store raw values only and let the rendering layer format them. Add a general test that no field used in a headline aggregate is rounded upstream.

---

### 6.9 Result 1 headline means also derive from rounded per-fit fields

**Location:** `refit_pannusch_angeloni()` around lines 328–347.

Per-solute on-grid and holdout MAPEs are rounded before the macro-average is calculated. The reported 8.4% named-solute holdout and 11.5% aggregate-proxy holdout therefore are averages of displayed values rather than full-precision losses. This is less severe than the conceptual issues above but should be corrected across the paper for consistency.

The paper build should use a single convention:

- internal JSON: full-precision numerical results and explicit units;
- tables/figures: formatting/rounding only at render time;
- manuscript numbers: generated from formatted result fields or a manuscript-value table that records the raw source.

Avoid mixing raw and formatted fields in the same result object.

---

### 6.10 A3-04 — the profiled rate set is right-censored by the tested domain

**Locations:** Result 2 lines 250–267; Figure 2; `identifiability_panel()` lines 723–750.

For caffeine, the manuscript reports an SSE profile within 10% of the minimum over approximately `[0.4, 6.5]`. Because 6.5 is the upper tested rate boundary, the threshold set does not close on that side. The code nevertheless calculates `log_width = log(hi/lo)` and comments that it is “domain-independent.” It is not: widening the domain could increase the width and alter the fraction of grid points within threshold.

The statement “a broad plateau with no bounded minimum under either objective” is also inaccurate. The code reports an interior SSE optimum and a local Hessian it labels reliable. What is unbounded/censored is the **10%-tolerance set**, not the existence of a numerical minimum.

Use language such as:

> “The profiled objective has an interior numerical minimum, but the 10%-above-minimum set reaches the upper edge of the tested rate domain; therefore, its upper extent is right-censored and the data do not establish a closed upper tolerance bound within the tested domain.”

Figure 2 should mark the boundary with an arrow or open interval notation, and the result object should include fields such as `profile_lower_censored` and `profile_upper_censored`. Do not report a finite log width without the qualifier “within the tested domain.”

---
### 6.11 The Hessian diagnostics need numerical convergence and scaling checks

**Locations:** Result 2; `identifiability_panel()` lines 662–722; Figure 2.

The condition numbers of approximately 1930 and 3600 and the inverse-curvature couplings near −1 are plausible signatures of a narrow/flat local objective geometry. But they are computed using central finite differences on a 29 × 41 geometric grid, at the nearest c_s0 grid point to the analytic profile optimum. No sensitivity is shown to:

- rate-grid density;
- inventory-grid density and range;
- finite-difference step size;
- continuous optimization of the two-dimensional minimum;
- alternative parameter scalings;
- objective normalization;
- solver tolerances or numerical noise.

A Hessian condition number is not invariant to reparameterization. The log-parameter basis is defensible, but “standard sloppiness basis” does not make the value universal. Report the basis as part of the result and treat the number as a local numerical diagnostic, not a property of the physical system.

A minimum acceptance package should include a table like:

| rate points | c_s0 points | finite-difference step multiplier | rate domain | condition number | coupling | profile fraction | boundary flag |
|---:|---:|---:|---|---:|---:|---:|---|

Repeat with at least one continuously optimized profile or a local quadratic fit using solver evaluations centered on the optimum. If the condition number varies by orders of magnitude while the profile remains broad, emphasize the profile and demote the exact Hessian number.

---

### 6.12 The `mape_cross_check_agrees` rule is not a principled agreement test

**Location:** `identifiability_panel()` line 733.

The code sets agreement to true when both SSE and MAPE profile fractions exceed 0.30. This is an arbitrary binary threshold. Two profiles could meet that rule while having different minima, different boundaries, and little overlap. Conversely, two similar profiles could fail if both are moderately narrow.

Replace this flag with quantitative fields:

- overlap fraction of threshold sets;
- Jaccard index of grid membership;
- distance between best rates on the log scale;
- maximum relative difference in profiled inventory;
- whether either set is censored.

The manuscript can then say the objectives give the same qualitative conclusion if those quantitative comparisons support it. Avoid embedding an unvalidated 30% cutoff in the result schema.

---

### 6.13 Unweighted concentration-scale SSE is not yet connected to the source error structure

**Locations:** Methods 2.6; Result 2; source-data discussion.

The manuscript correctly states that the SSE profile is not a profile likelihood because no noise model is specified. That honesty is important. But the numerical profile is still treated as the formal identifiability result, even though unweighted concentration-scale SSE gives larger-concentration observations more influence and ignores the source's analyte-specific variability.

Angeloni report duplicate extractions and an analyte RSD range; the repository retains central values only. At minimum, run sensitivity analyses under:

- unweighted SSE;
- relative-error or log-scale SSE;
- MAPE;
- weights based on available analyte-level or condition-level RSD ranges;
- a plausible heteroscedastic model with variance proportional to concentration squared.

Do not infer confidence intervals from these objectives unless a likelihood and uncertainty model are specified. The goal is to determine whether the broad compensation region is robust to reasonable scoring assumptions.

The paper may ultimately retain unweighted SSE for smooth local curvature, but it should explain why and show that the conclusion is not driven by one concentration scale.

---

### 6.14 “Matched beverage mass” remains an approximation to matched volume

**Locations:** Abstract lines 28 and 56–57; Methods 2.3; Results; figure titles; `_V_TARGET_ML` and `_matched_bounds()`.

The implementation terminates at `_V_TARGET_ML = 40.0` and uses `t_end = 40 mL / flow`. The source endpoint is described as 40 ± 2 g beverage. Equating mass and volume by density ≈1 may be reasonable as a first approximation, but the manuscript repeatedly calls the implementation exactly matched mass.

This matters because the central narrative is that endpoint mismatch created a false cross-grind failure. A paper built around endpoint correctness should be exact about its own endpoint operator.

Required options:

1. **Preferred:** use mass-flow traces or a density conversion and terminate when cumulative beverage mass reaches the target mass.
2. **Acceptable sensitivity:** state “matched 40 mL proxy for the 40 g endpoint under ρ≈1 g/mL,” vary density over a physically plausible range, and vary endpoint between 38 and 42 g/mL-equivalent.

Report how point transfer, profile-set worst error, profile width, and flow-map sensitivity change. Figure titles and captions should say “matched-volume proxy” until the mass operator is implemented.

The existing structural test pins 40 mL, not mass consistency. Rename the test accordingly; otherwise it encodes the approximation as a supposed physical truth.

---

### 6.15 Pressure-to-flow and grind-specific flow uncertainty remain conditional assumptions

**Locations:** Methods 2.3; Result 1; Result 3; `_flow_darcy()` and `_flow_gran()` paths.

The manuscript now labels the pressure→flow mappings as assumptions, which is good. But it still treats resulting predictions and profiles as sufficiently definitive to support broad transfer and robustness language. The O profile uses one constructed Darcy map, while the O→C/F transfer uses fitted per-granulometry conductivity polynomials and nominal shot times. These mappings are not measured flow histories for each chemical observation.

Uncertainty sources include:

- 40 g / nominal shot-time anchors;
- viscosity closure and temperature dependence;
- pressure calibration;
- hydraulic polynomial coefficients;
- whether constant-flow integration represents the source extraction;
- time alignment and pre-infusion;
- conversion between mass flow and volume flow;
- grind-specific puck geometry and permeability evolution.

The observation that two tested O flow maps differ by only ~0.5 pp at the matched endpoint does not establish general flow-map robustness. It compares two specific deterministic maps under one endpoint operator.

Required action: sample or sweep plausible hydraulic coefficients, anchors, viscosity/density choices, and shot times. Propagate these through both the O profile and C/F transfer. Report the resulting distribution or range of rate profiles and held-out skill. If a full uncertainty propagation is computationally expensive, a designed sensitivity grid is acceptable, provided the manuscript says results are conditional on the tested map.

---

### 6.16 The geometry sensitivity does not test a cross-grinder geometry map

**Locations:** `geometry_sensitivity_transfer()` and Result 3.

The geometry routine applies each of the three Pannusch fitted geometries globally to O, C, and F. This asks whether the result is sensitive to a single global geometry choice within the observed Pannusch range. It does **not** ask whether Angeloni's O/C/F grinds map to different Pannusch geometry values, nor whether a grind-specific combination changes transfer.

This distinction should be visible in the manuscript and caption. A more relevant sensitivity would evaluate plausible mappings such as:

- O→1.7, C→1.4, F→2.0 or the physically appropriate ordering after checking definitions;
- permutations consistent with particle-size measurements;
- continuous ranges for `psi` and `d_s2` by grind;
- uncertainty in the cross-grinder correspondence.

If such a mapping cannot be justified, retain the current global sweep but call it exactly that. Do not conclude that the residual is “not a geometry artefact.” At most, conclude that it is not highly sensitive to the tested **global** Pannusch geometry setting.

---

### 6.17 Table 7 should be used quantitatively, with uncertainty and dependence stated

**Locations:** Result 2 lines 243–248; Figure 2.

The revised wording correctly demotes Table 7 from “external tie-breaker” to a same-campaign orthogonal measurement. Figure 2 shows a horizontal inventory line crossing the profile path, but the paper does not calculate the corresponding rate or rate range, nor does it propagate uncertainty in the inventory measurement.

To turn this into a scientifically useful result:

1. identify the exact unit conversion between Table 7 and model `c_s0`;
2. report measurement uncertainty or, if unavailable, a justified sensitivity band;
3. solve for the rate values where the profiled inventory intersects that band;
4. report whether the intersection is unique within the tested domain;
5. propagate the constrained set to C/F predictions;
6. state that both inventory and cup measurements arise from the same Angeloni campaign and therefore are not an independent external validation.

This analysis could provide one of the paper's strongest design lessons: an orthogonal inventory measurement can collapse an otherwise broad inventory–rate profile. But the current visual intersection is only suggestive.

---

### 6.18 The LOCO analysis is now honestly descriptive, but its role should be simplified

**Locations:** Result 3; `loco_cv_refit()`; Figure 3.

The revision correctly states that neither resampling summary is coverage-calibrated and that both reuse already computed fold errors from overlapping fits. This addresses the previous overinterpretation and is consistent with the known difficulty of estimating cross-validation variance when training sets overlap.

Two refinements remain:

- Do not describe these as “interval estimates” without “descriptive.” They are percentile ranges of resampled summaries, not confidence intervals for a clearly defined population quantity.
- The condition-level resampling does not become dependence-corrected simply because errors are macro-averaged by T,p. It may still be useful as a compact sensitivity summary, but it should not carry much inferential weight.

Given the paper's main focus, a clearer presentation may be to report the nine condition-level macro errors directly, with median, range, and perhaps a box/violin plot. The stronger action is to compare model and baseline in each held-out condition. A paired distribution of model-minus-baseline loss is more informative than two resampling ranges of model loss alone.

If inferential uncertainty is desired, design a resampling procedure that resamples experimental units/replicates and repeats the entire rate/level fit, with a stated target. The source central values may not support that without replicate-level data, in which case the honest choice is descriptive validation only.

---

### 6.19 The “identifiability ratio” should not be a binary identification criterion

**Locations:** Methods 2.5 lines 158–167; Section 6; `identifiability.py`.

The manuscript defines `max-edge MAPE / min MAPE` and says ratio ≫1 means the rate is identified while ratio ≈1 means it is not. The code comments are more cautious, calling it a descriptive sharpness proxy that is range-dependent. The manuscript should adopt the code's cautious interpretation.

The ratio depends on:

- the chosen rate domain and endpoints;
- grid spacing;
- the minimum error, which can approach zero in a same-model simulation;
- noise level and realization;
- number and timing of observations;
- profiling objective;
- model discrepancy.

It is not an identifiability theorem, confidence measure, or universal threshold. Rename it **profile range ratio** or **relative profile excursion** and show the full profile. Avoid statements such as “ratio ≫1 means identified.” Instead say “larger excursion over the declared domain indicates greater objective sensitivity to rate in this comparison.”

For a more interpretable metric, also report:

- curvature or profile width near the minimum;
- rate interval within an absolute or relative tolerance;
- whether the interval reaches the domain boundary;
- best-rate stability across seeds/conditions;
- profile-wise prediction variation.

---

### 6.20 The exact-cup simulation is a useful illustration, not empirical evidence

**Locations:** Section 6 lines 386–403; `full_cup_simulation_identifiability()`.

The manuscript now explicitly acknowledges the inverse crime and lack of model discrepancy, which is essential. Still, several details make the result more optimistic for fraction-based recovery than the prose may suggest:

- synthetic truth and fitting use the same PDE and parameters;
- the true rate 1.0 is exactly included in the nine-point candidate grid;
- multiplicative Gaussian noise is independent across observations;
- the same geometry, flow, initial condition, and observation operator are used for generation and fitting;
- the terminal time is taken as the latest available fraction upper bound, which may not be the physical full-shot endpoint;
- the free level is fitted separately at each rate;
- no source-like correlated or heteroscedastic error is included.

The 100% recovery of rate=1 is therefore close to a positive-control expectation, not strong evidence that real fraction data identify the physical rate.

Required extensions:

1. off-grid true rates, such as 0.7, 1.15, and 1.8;
2. denser/continuous fitted rates;
3. altered geometry or hydraulic map between generation and fitting;
4. biased endpoint or time origin;
5. correlated and heteroscedastic noise;
6. additive detection-floor effects;
7. solute-parameter mismatch;
8. incomplete/missing fractions.

The result can remain in the paper as a simulation showing *why temporal resolution can help under the model*, but it should not be used to infer a general empirical property of cups.

---

### 6.21 Figure 6 and the text report different stochastic objects

**Locations:** Section 6; `full_cup_simulation_identifiability()` lines 179–199; `fig6_fraction_vs_endpoint()`.

The simulation runs 20 seeds and reports mean ± standard deviation of range ratios and best-rate recovery. But the result object stores only `fraction_mape` and `exact_cup_mape` from seed 0 for plotting. Figure 6 therefore shows one arbitrary realization while the text presents an ensemble result. A reader cannot see the seed variability, and the plotted minimum may not correspond to the reported median/mean behavior.

Required correction:

- store all seed profiles or at least median and 5–95% bands at each rate;
- plot ensemble median with a shaded band;
- state seed count and noise model in the caption;
- show off-grid-truth sensitivity if added;
- avoid mixing a single empirical profile and one synthetic seed without clear visual separation.

This was identified in the previous review and remains unresolved despite the report-key fix.

---

### 6.22 The simulated “whole cup” endpoint requires source verification

**Location:** `full_cup_simulation_identifiability()` lines 150–167.

For each experiment, `t_end` is set to the maximum `t_upper_s` among the available six selected windows. The model then integrates `[0, t_end]` and calls this the exact whole cup. Unless the source documents that the last selected window ends exactly at the complete shot endpoint for every experiment, this is more accurately an exact model integral over the **available terminal window**.

The manuscript itself says the empirical brew-ratio 1/3 cup mass/endpoint is ambiguous. That ambiguity also affects the label attached to the simulation horizon. Verify the source fraction protocol and shot termination. If the latest fraction ends at the full collection endpoint, document it. Otherwise relabel the simulation and vary the terminal time.

The conceptual contrast between resolved and integrated observations remains valid within a declared modeled horizon, but “exact whole cup” should be reserved for an established cup endpoint.

---

### 6.23 The external Waszkiewicz profile provides weak shape localization, not a validated rate estimate

**Locations:** Abstract lines 49–54; Section 6 lines 405–438; `external_waszkiewicz.py`.

The revision substantially improves the prose by stating that the level is profiled and the minimum MAPE is high. The reported best-rate profile has approximately 27% minimum MAPE and only a 1.6–2.1 range ratio over the tested grid depending on offset/bin treatment. This is a shallow objective preference under substantial model–data mismatch, not strong parameter localization.

Use wording such as:

> “The external TDS trajectory produced a shallow, assumption-dependent profiled-MAPE minimum near rate 0.4; the minimum error remained approximately 27%, so the result is evidence only that temporal shape changes the objective more than a single aggregate under the tested operator.”

Avoid “the trajectory constrains the kinetic rate” unless a tolerance interval closes and is stable under uncertainty. The best rate should not be interpreted physically because:

- the TDS pseudo-solute is not a named molecular species;
- absolute level is fitted to the target;
- the coffee, grinder, machine, and likely geometry differ;
- temperature is assumed;
- flow conversion and numerical floor are fixed;
- source uncertainty is not weighted;
- only one averaged trajectory is used.

The external analysis is still valuable as a shape stress test, but it is not an independent confirmation of the Pannusch rate scale.

---

### 6.24 The external single-cup flat profile is algebraic by construction

**Locations:** Abstract lines 51–54; Section 6 lines 416–422; `external_waszkiewicz.py` lines 84–105.

With one cup scalar and one free multiplicative level, the profiled MAPE is exactly zero at every rate. This is a mathematical identity, not a data-driven result. The current manuscript acknowledges this in Section 6, but the abstract's phrase “whose integrated cup carries no rate information at all” can still be read as an empirical finding from the external experiment.

The appropriate interpretation is:

- one scalar observation cannot constrain a shape parameter when an unconstrained scalar level is profiled independently at each rate;
- this says nothing about multiple cups collected at different flow rates, temperatures, or endpoints;
- it also says nothing about a cup design with independently measured inventory or a fixed level.

Keep the algebraic demonstration in Methods or a schematic, but do not count it as an external validation panel. A scientifically informative external cup comparison would require multiple independent cup observations under varied inputs or a fixed/externally constrained level.

---

### 6.25 The Waszkiewicz sensitivity package remains too narrow

**Location:** `external_waszkiewicz.py`.

The code varies only time offset and inclusion of the first bin. Other fixed assumptions may materially affect the shallow rate preference:

- `T_C = 93.0` despite no trace-specific brew temperature;
- `mass_flow_rate_g_per_s ≈ mL/s` under density ≈1;
- `q_floor = 0.05`, which affects pre-drip transport;
- fixed 5 s edges and a 60 s horizon;
- interpolation and extrapolation behavior of the flow trace;
- no uncertainty weighting despite reported replicate information for most bins;
- no alternative optical-TDS observation model;
- rounding each MAPE before calculating range ratios.

Required action: retain full precision, vary these assumptions, and show a compact sensitivity matrix. Because the objective is shallow, even modest shifts in best rate or range ratio may change the interpretation. The analysis code and `strength` field must also stop saying “Frozen external prediction”: it is a target-profiled external shape test.

---
### 6.26 Figure 4 does not show the analysis that now carries the headline claim

**Locations:** Figure 4 and `fig4_transfer()`.

The revised abstract emphasizes transfer across the entire near-optimal set, with a ~22% worst held-out error. Figure 4 still plots only the single point-optimum predictions. There is no indication of:

- the number or rate range of retained profile points;
- the profile-wise prediction envelope at each observation;
- point optimum versus worst profile point;
- O-trained constant baseline;
- geometry sensitivity distribution;
- whether the maximum ~22% comes from one solute/grind or is widespread.

The title embeds two unshown conclusions—“transfers reasonably” and “≤1 pp geometry-sensitive.” Moreover, the geometry number is affected by round-before-aggregate code.

A redesigned Figure 4 should be the paper's central predictive-identifiability figure. Recommended structure:

- panel A: C predictions, observed on x, point prediction on y, vertical profile envelope, constant baseline symbol;
- panel B: F equivalent;
- panel C: model-minus-baseline loss by variety × solute × grind;
- panel D: profile-set held-out MAPE versus O-profile rate, with threshold set highlighted.

Use neutral titles. This would directly connect parameter-profile width to prediction stability and incremental predictive skill.

---

### 6.27 Figure 2 should display censoring and the corrected MAPE cross-check

**Locations:** Figure 2 and `fig2_objective_surface()`.

Figure 2 is visually much improved relative to early drafts: it shows the SSE surface, profiled path, Table 7 line, and normalized profile. But it omits information that the manuscript now treats as central:

- the MAPE profile and its 66% near-optimal fraction;
- the fact that the SSE threshold set reaches the upper domain boundary;
- a clear open/censored interval marker;
- Hessian reliability and sensitivity;
- the rate of the MAPE optimum;
- uncertainty around Table 7.

The lower profile panel currently shades points within 10% and uses a finite horizontal extent without signaling that the set remains open at the boundary. Add a right-facing arrow or “≥6.5” notation. Consider plotting SSE and MAPE profiles in adjacent rows or using a secondary panel with normalized objective increase. Do not imply that the Table 7 horizontal line uniquely selects a point unless the intersection analysis in A3-13 is completed.

The caption should explain that the 10% band is a declared tolerance, not a confidence region, and that the condition number is local and basis-dependent.

---

### 6.28 Figure 3 should show condition structure and baseline comparisons

**Locations:** Figure 3 and `fig3_holdouts()`.

Figure 3 plots observed versus predicted concentrations for all LOCO points. The figure reveals systematic structure that the pooled 6.5% MAPE obscures: predictions within solute/variety groups are compressed into narrow horizontal ranges. This is valuable but not discussed enough.

Recommended changes:

- color or annotate by temperature/pressure, or add residual panels against T and p;
- include the O-trained constant or fit-only-on-training-fold baseline;
- plot model-minus-baseline absolute percentage error by held-out condition;
- label the descriptive resampling range with `%` and explicitly say it is not a CI;
- avoid placing a long statistical conclusion in the title;
- report sample counts and the fitting unit in the caption.

A calibration plot alone can look favorable when between-solute concentration differences dominate. Faceting by solute or plotting normalized residuals would reveal within-group skill more clearly.

---

### 6.29 Figure 5 needs a reduced-model ladder and clearer in-sample framing

**Locations:** Figure 5 and `fig5_joint_residual()`.

The heatmaps clearly show where the joint fit incurs cost, but the figure compares two in-sample mechanistic variants only. Because constant baselines are nearly competitive, add the reduced-model ladder described in Section 6.2. At minimum, include a fourth panel with joint-model improvement over a shared constant and independent-model improvement over per-grind constants.

Other issues:

- the star marking a rate at the domain boundary should explain whether it is the lower or upper boundary;
- the mean cost hides large cell-specific costs, including a ~5.3 pp cell;
- the joint and independent models have different flexibility, so raw in-sample loss is expected to favor the latter;
- rate-boundary fits should not be presented as stable estimates;
- aggregation precision must be corrected before regenerating the heatmap.

Use “in-sample shared-parameter compatibility” in the title/caption. Avoid “shared calibration exists” unless adequacy relative to reduced models and a predeclared criterion is demonstrated.

---

### 6.30 Figure 6 combines unlike evidence classes and omits the external panel

**Locations:** Figure 6 and `fig6_fraction_vs_endpoint()`.

Figure 6 overlays:

- empirical in-sample Schmieder fraction scoring;
- a sampled-fraction aggregate that is not a real whole cup;
- a same-model synthetic exact-integral profile from seed 0.

These curves arise from different observation sets, noise structures, and evidence classes. Overlaying them on one axis encourages direct magnitude comparisons that are not well controlled. The figure also omits the Waszkiewicz external profile even though the abstract uses it to support the time-resolution conclusion.

Recommended redesign:

- **Panel group A:** in-sample Schmieder empirical fraction and sampled aggregate, clearly labeled as model-calibration lineage and incomplete aggregate;
- **Panel group B:** same-model simulation with median and 5–95% bands over seeds, plus off-grid truth/discrepancy sensitivity;
- **Panel group C:** external Waszkiewicz fraction profile across declared alignment assumptions, with minimum MAPE and no-rate-information algebraic cup schematic separated from empirical curves.

Do not put the exact-cup seed-0 line beside empirical data as if it had the same evidentiary status. Show raw/normalized profiles and tolerance widths, not only range ratios.

---

### 6.31 Figure 1 is improved but can be simplified and should include the benchmark logic

**Locations:** Figure 1 and `fig1_design()`.

Figure 1 now uses campaign-accurate categories and correctly separates source calibration, in-sample localization, same-model simulation, target recalibration, within-campaign holdout, same-campaign orthogonal measurement, and independent external data. This is a strong improvement.

Remaining suggestions:

- add a simple baseline/reference-model box or annotation in the Angeloni holdout lane;
- reduce text density and font size pressure;
- avoid using a red border for independent external evidence if red elsewhere implies failure;
- make arrows reflect data use precisely—e.g., Table 7 constrains the profile rather than following from C/F holdout;
- state in the caption that Angeloni O is used for target recalibration and therefore subsequent C/F predictions are internal to that campaign.

This figure can become a useful evidence map if the manuscript uses the same terms everywhere.

---

### 6.32 Code and manuscript evidence taxonomy are still inconsistent

**Locations:** `angeloni_bracket.py` module/function docstrings, `external_waszkiewicz.py`, Reproducibility lines 635–637.

Examples of stale wording include:

- `joint_multigrind_fit()` calls itself “The REAL transfer test” and “external stress test,” even though it fits all O+C+F data jointly and is in sample;
- its verdict says the shared pair “transfers reasonably” despite no holdout;
- `external_waszkiewicz.py` calls the target-profiled analysis a “Frozen external prediction” and uses a strength tag combining prediction and objective localization;
- the manuscript Reproducibility section says “granulometry validation = negative (held-out grind),” which contradicts the revised positive/qualified finding;
- old comments speak of a “correlation” in places where the manuscript correctly says coupling.

These are not harmless developer comments because `results.json` carries verdict and strength strings that can flow into reports and figures. Implement a single evidence taxonomy as constants or structured metadata rather than free-text labels. Add a test that forbidden/stale phrases do not appear in manuscript-facing result fields.

---

### 6.33 The Paper-A-specific tests do not guard the remaining high-risk contracts

**Location:** `puckworks/tests/test_paper_a.py`.

The current file contains useful guards for:

- the 40 mL endpoint convention;
- the one-dimensional MAPE profile extraction;
- removal of a fixed-time parameter from the species bracket.

It does not test:

- full-precision aggregation;
- geometry spread before rounding;
- joint comparator precision;
- profile boundary censoring;
- manifold/grid-set rate bounds;
- overlap of SSE and MAPE sets;
- baseline calculations;
- figure-title/result consistency;
- seed-ensemble storage;
- source-commit/result-schema synchronization;
- deterministic build output.

Add small synthetic tests that do not require PDE solves. For example, refactor aggregation helpers into pure functions and test them with values that would be altered by early rounding. Store profile-set construction in a helper and test threshold/boundary cases. Add a fixture result bundle and assert that Figure 4 consumes the manifold envelope and baseline fields. The current “88 tests green” repository statement does not substitute for contract-specific regression tests.

---

### 6.34 The result bundle is broader but not yet a submission-grade single source of truth

**Locations:** `figures_paper_a.compute_all()` and Reproducibility section.

`compute_all()` now includes the major analyses cited by the manuscript, resolving a previous omission. Still, a submission-grade build needs more than invoking functions:

- a pinned source commit and dirty-tree check;
- package and operating-system versions;
- random seeds and deterministic behavior;
- solver tolerances;
- input-data checksums;
- raw, unrounded result values;
- schema validation;
- source-data tables for every figure;
- generated manuscript-value table;
- vector figures;
- a clean-environment build log;
- failure if the manuscript references a value absent from the bundle.

The schema comment still refers to a “cluster CI” even though the manuscript correctly rejects that interpretation. This illustrates why result metadata must be updated together with analysis semantics.

Recommended output layout:

```text
paper_a_release/
  manifest.json
  environment.lock
  results_raw.json
  manuscript_values.csv
  figure_source_data/
  figures/png/
  figures/pdf/
  figures/svg/
  build.log
  checksums.sha256
```

The build should fail if `git diff --quiet` is false unless a development override is explicitly supplied.

---

### 6.35 The manuscript remains an internal handoff rather than a journal submission

**Locations:** repository note, Methods, Open gaps, Figures, Reproducibility, change log.

The first 14 lines instruct collaborators to strip repository notes later and discuss review provenance, verb discipline, function names, and an owed tag. The body repeatedly includes review IDs (`A2-02`, `M4`, `B5`), code function names as prose, “owed” analyses, “the card marks it skip,” handoff references, and a project-status section. These are useful engineering records but inappropriate in a submitted manuscript.

The submission version should contain:

- conventional title page and author information;
- structured or journal-compliant abstract;
- mathematical model and observation equations;
- data sources and experimental units;
- fitting objectives and optimization details;
- uncertainty and validation methods;
- results with tables/figures;
- limitations and future work in scientific prose;
- complete references;
- data/code availability statements;
- conflicts/funding/author contributions as required.

Move all review provenance and implementation backlog to `REVIEW_BACKLOG.md`, issues, or a supplement. A reader should not need Python function names to understand how the analysis was conducted.

---

### 6.36 The Methods remain insufficient for independent reconstruction

**Locations:** Methods 2.1–2.6.

The Methods describe the conceptual structure but omit several details needed to reproduce the analysis without reading source code:

- governing PDEs, boundary/initial conditions, and numerical scheme;
- exact cup/fraction observation operators;
- units and conversion of `c_s0`;
- how `rate_scale` modifies A1/A2;
- all fixed solute parameters and their provenance;
- rate/inventory domains and grid sizes for each analysis;
- exact SSE, MAPE, log-loss, and profile-threshold formulas;
- analytic weighted-median and least-squares level solutions;
- optimizer/tie-breaking behavior;
- treatment of off-grid points;
- definition of macro-averaging;
- baseline models;
- handling of duplicates/replicates;
- flow and geometry equations with coefficient tables;
- numerical tolerances and runtime environment;
- random-noise model and seed handling;
- criteria for boundary flags and “reliability.”

Add a self-contained Methods section or a detailed supplement. Code availability is not a substitute for a scientific method description.

---

### 6.37 The title and abstract still overstate the empirical “cup hides the clock” claim

The title is memorable, but the evidence consists of:

- a broad endpoint objective profile in one model–dataset configuration;
- an in-sample fraction comparison on the model's calibration lineage;
- a same-model inverse-crime simulation;
- an external single-shot cup profile that is flat algebraically because one free level fits one scalar.

This supports a scoped claim that **a cup endpoint can hide kinetic timing under a free inventory level in the tested design**, not that cups generally lack kinetic information. The introduction and related-work section acknowledge this, but the title/abstract can still be read categorically.

Possible title alternatives:

- “When a cup endpoint weakly constrains kinetics: inventory–rate confounding in an espresso extraction case study”;
- “Endpoint accuracy without kinetic identification in a multi-solute espresso model”;
- “Inventory–kinetics confounding under cup-integrated espresso observations.”

If retaining the current title, add “in a single-grind endpoint design” or equivalent qualification in the subtitle/abstract.

---

### 6.38 The claim that “matching the beverage endpoint is a prerequisite for any of them” should be narrowed

**Locations:** Abstract lines 54–57; Discussion lines 460–469.

It is correct that comparing mismatched observation windows can create spurious validation failures. But “matching the beverage endpoint is a prerequisite for identifiability, transfer, and endpoint accuracy” is too broad. Identifiability can be studied under any explicitly defined observation operator; the issue is that the model and data operators must correspond. A fixed-time endpoint could be valid if the experiment reported a fixed-time sample. Likewise, different endpoints can be compared through a calibrated observation model.

Prefer:

> “A validation score is interpretable only when the model output is mapped to the same observation window and endpoint as the data.”

This states the general principle without privileging one endpoint type.

---

### 6.39 The related-work section is extensive but not yet integrated into the paper's actual inferential choices

The draft correctly distinguishes structural and practical identifiability and cites profile analysis and sloppiness literature. Yet the actual analysis does not use a likelihood, profile confidence set, or profile-wise prediction interval. The related-work discussion should clearly separate:

- established likelihood-based profile methods;
- the paper's descriptive objective profiles and tolerance sets;
- local curvature diagnostics;
- profile-set prediction propagation without statistical coverage.

Simpson and Maclaren's profile-wise prediction framework is especially relevant to the paper's stated parameter-vs-prediction distinction, but the manuscript currently implements only a coarse deterministic MAPE set. Cite that work as motivation while making clear that the paper does not construct likelihood-based prediction intervals.

The novelty claim should remain modest: this is an applied espresso case study using established inverse-problem ideas. Complete and archive the documented search before asserting priority.

---

### 6.40 The source citations and metadata need final verification

The main source citations should be standardized and complete. In particular:

- Angeloni et al. is *Computer Percolation Models for Espresso Coffee: State of the Art, Results and Future Perspectives*, *Applied Sciences* **13**(4), 2688 (2023), DOI `10.3390/app13042688`;
- Schmieder et al. is *Influence of Flow Rate, Particle Size, and Temperature on Espresso Extraction Kinetics*, *Foods* **12**(15), 2871 (2023), DOI `10.3390/foods12152871`;
- Pannusch et al. is *Model-based kinetic espresso brewing control chart for representative taste components*, *Journal of Food Engineering* **367**, 111887 (2024), DOI `10.1016/j.jfoodeng.2023.111887`;
- Waszkiewicz et al. is *Under pressure: Poroelastic regulation of flow in espresso brewing*, *Physics of Fluids* **38**, 063113 (2026), DOI `10.1063/5.0319611`.

Ensure the data-release year/name (`waszkiewicz2025`) is explained only in repository documentation, not used as an ambiguous manuscript citation.

---
## 7. Section-by-section manuscript comments

### 7.1 Title

**Current:** “The cup can hide the clock: practical inventory–kinetics confounding in a cross-dataset espresso extraction case study.”

The title is engaging and reflects the central metaphor, but it risks sounding universal. The actual result is conditional on a free inventory level, a single-grind endpoint design, the tested model, parameter domain, flow maps, and objectives. Consider adding a qualifier such as “under a single-grind endpoint design” or using one of the alternatives in Section 6.37.

“Cross-dataset” is accurate in the broad sense that the Pannusch/Schmieder model is refitted to Angeloni, but the main transfer test is within the Angeloni campaign after target recalibration. A title emphasizing “target recalibration plus internal cross-grind holdout” would be more precise than implying a fully frozen cross-dataset prediction.

### 7.2 Repository note

Delete lines 3–14 from any submission. They are internal governance instructions, not manuscript content. Move verb-discipline notes, review provenance, code targets, and the owed release tag to repository documentation.

### 7.3 Abstract

The abstract is much improved in its evidence labels, but it remains overpacked and contains several unsupported or overly strong phrases.

Specific issues:

- “matched-beverage-mass” should be “matched-volume proxy for the 40 g endpoint” until mass-consistent integration or density sensitivity is implemented.
- “strong practical non-identifiability” is supportable as a scoped conclusion, but the exact Hessian numbers should not lead the abstract until numerical convergence is shown.
- “MAPE cross-check that agrees” should be replaced by the actual profile fractions and a statement that the two objectives both yield broad sets, without the arbitrary agreement flag.
- “predicts the held-out coarse/fine grinds reasonably” lacks a null benchmark. State absolute errors and, after rerun, skill relative to baseline.
- “entire near-optimal O-grind set” should be “the discrete 10%-near-optimal MAPE grid set” until continuous/grid-converged propagation is performed.
- “stable along the compensating manifold” is too strong because profile-set aggregate MAPE is shown, not condition-wise prediction invariance.
- “the independent second-rig TDS trajectory consistently constrains the rate” should be “produces a shallow profiled-objective minimum under declared assumptions”; minimum MAPE is ~27%.
- “the integrated cup carries no rate information at all” should disclose in the same sentence that this is algebraic because one scalar is paired with one profiled level.
- “even when it does transfer” is not established relative to a level-only baseline.

The abstract should be shortened and organized around three findings:

1. broad endpoint objective profile;
2. absolute held-out error plus incremental skill over baseline;
3. stronger objective sensitivity with temporal observations in scoped in-sample/synthetic/external-shape analyses.

### 7.4 Introduction

The opening claim that cross-dataset checks are “almost always” performed on whole-cup quantities is broad and should be supported or softened. “Frequently” is safer unless the literature search quantifies prevalence.

The introduction appropriately explains inventory–rate compensation. Add a paragraph distinguishing:

- parameter identifiability;
- prediction identifiability/profile-wise prediction stability;
- predictive skill relative to a benchmark;
- cross-dataset generalization versus within-campaign holdout.

This distinction will prevent the manuscript from treating low absolute error as transfer skill—the same interpretive problem it criticizes in mechanism identification.

The phrase “non-identifiable curve fit masquerading as a transferred calibration” is rhetorically forceful and may sound accusatory. Prefer neutral scientific language: “a low-error fit whose parameter decomposition is weakly localized.”

### 7.5 Methods 2.1 — Model

Replace code identifiers with mathematical notation and equations. Include:

- governing balances and relevant constitutive relations;
- definition and units of `c_s0`;
- definition of `rate_scale` and exactly which coefficients it multiplies;
- proof or derivation of linearity in inventory under the normalized solver;
- observation operator for a time window and for a matched endpoint;
- fixed parameters and their source/fitted status;
- solver discretization and convergence settings.

The statement that the whole-cup concentration is “exactly linear” in `c_s0` should be accompanied by either an equation or a formal test/reference. Clarify whether this remains exact for all solver features, boundary conditions, and nonlinear closures used in the analyses.

### 7.6 Methods 2.2 — Data

The source-study description is now substantially more accurate. Retain the distinction between ten collected fractions and the repository's six-window subset. State the experimental unit and replicate handling explicitly:

- Angeloni table rows are condition-level central values based on duplicate extractions;
- replicate-level values are not available in the repository analysis;
- Schmieder center-point repetition and selected-window structure;
- Waszkiewicz trajectory is an average over shots, with bin-specific uncertainty treatment.

Correctly distinguish named solutes from TDS/total-solids proxies. Consider moving the detailed TDS non-equivalence explanation to a short table of observables and units.

### 7.7 Methods 2.3 — Pressure→flow map

The section should include the actual coefficients and units, not only prose. Separate the O profile map from the O/C/F transfer map. Explain whether flow is constant within a simulated cup and how pre-infusion/transient flow are treated. Use “assumed mapping” consistently.

Add a sensitivity-design subsection and state which map is primary. The current text says the refined map comes from the study's “own hydraulics,” but the 40 g / 24 s anchor is still an imposed physical point. Avoid wording that could imply measured per-condition flow.

### 7.8 Methods 2.4 — Fitting and evaluation protocol

Add a diagram/table that lists, for each result:

| Analysis | Training data | Test data | Parameters fitted | Objective | Endpoint/operator | Evidence class |
|---|---|---|---|---|---|---|

This is clearer than relying on prose and Figure 1 alone. Include the null models and ensure that every holdout excludes the held-out condition from all fitting steps, including level selection and any hyperparameter/threshold choice.

Clarify whether rate-grid choice was made before seeing test performance. If the 10% profile threshold or ≤3 pp compatibility rule was selected post hoc, say so and treat it as descriptive.

### 7.9 Methods 2.5 — Identifiability metric

Rename the “identifiability ratio.” State the full profile and tolerance width as primary. The current binary interpretation should be removed. Add domain, grid, and noise sensitivity. Separate:

- in-sample empirical profile;
- same-model simulation profile;
- external target-profiled shape profile.

They should not share one unqualified metric interpretation.

### 7.10 Methods 2.6 — Evidence vocabulary

This section is useful but should be shortened and integrated with the analysis table. “JFE-standard terms” should be removed unless the journal explicitly defines them. The evidence labels are generally standard scientific language, but not necessarily a named journal standard.

The external Waszkiewicz case is not an “external prediction” of absolute concentration because level is fitted. Add “external-data shape fit/objective localization” as a distinct row. Likewise, the pooled envelope bracket is not the same evidentiary strength as a condition-level external prediction.

### 7.11 Result 1

The corrected endpoint analysis is important and should be retained. However:

- replace matched mass with matched-volume approximation until corrected;
- report blind named-solute results separately from aggregate proxy, not only a combined 22.6%;
- show full condition-level errors and a null baseline;
- quantify whether the 0.5 pp flow-map difference is small relative to source variability and numerical precision;
- avoid reading specific fitted rates mechanistically before the profile analysis;
- calculate headline means from full precision.

A table should include model, constant baseline, and source/repeatability context.

### 7.12 Result 2

This remains the strongest section conceptually. Improve it by:

- replacing the approximate product equation with the exact model relation or carefully labeled approximation;
- reporting all boundary/censor flags;
- removing “no bounded minimum under either objective”;
- presenting grid/domain convergence;
- showing SSE and MAPE profiles together;
- quantifying Table 7 intersection;
- demoting exact Hessian values if sensitivity is poor;
- adding all solutes/varieties to supplement.

The phrase “unambiguous” is too strong before numerical convergence and uncertainty sensitivity. “Both objectives show a broad compensation region under the tested grid” is sufficient.

### 7.13 Result 3

This section needs the largest revision because it connects the identifiability result to prediction.

Required narrative order:

1. define baseline models and acceptance criterion;
2. report point-optimum model versus baseline on C and F;
3. propagate the profile set and compare condition-wise envelopes with baseline;
4. report geometry/flow/endpoint sensitivity;
5. present joint in-sample compatibility separately, with constant/reduced-model comparators;
6. present LOCO model-minus-baseline paired errors and descriptive distributions.

Do not use the joint fit to confirm held-out transfer. Do not call a coarse deterministic set a whole manifold. Report the 5-CQA Arabica C/F behavior explicitly because it drives the worst errors and profile-set maximum.

### 7.14 Section 6 — temporal information

Split this section into three evidence tiers:

1. **In-sample empirical localization:** useful positive control but on calibration lineage and using a sampled aggregate that is not a cup.
2. **Same-model simulation:** exact operator comparison under an inverse crime; show ensemble and discrepancy sensitivity.
3. **External target-profiled shape analysis:** one aggregate TDS trajectory with high residual error and shallow profile; cup flatness algebraic.

The current section carefully qualifies many points, but the opening and closing synthesis still makes them sound mutually confirming. They all point in the same qualitative direction, but they do not have equal evidentiary strength.

### 7.15 Discussion

The discussion's distinction between parameter identifiability and predictive transfer is theoretically sound. The empirical claim should be revised to include a third axis: **predictive skill relative to a null model**. A model can have stable predictions across a parameter profile and low absolute MAPE while contributing little beyond a constant level.

A stronger discussion sentence would be:

> “The endpoint data weakly localize the inventory–rate decomposition. Predictions generated across the near-optimal set also vary less than the parameters, but their incremental skill over level-only baselines is small and must be reported separately from absolute error.”

This would make the paper more original and methodologically coherent: endpoint accuracy, prediction stability, parameter identifiability, and incremental skill are four distinct properties.

### 7.16 Open gaps

Delete this implementation ledger from the submission. Convert scientifically relevant items into a conventional Limitations and Future Work section. Do not label analyses “delivered,” reference review IDs, or list function names.

A concise limitations section should cover:

- target-data refitting and within-campaign holdouts;
- uncertain pressure→flow and cross-grinder geometry maps;
- central-value rather than replicate-level analysis;
- mass–volume endpoint approximation;
- grid/domain dependence of profiles;
- same-model simulation;
- one external TDS trajectory and no named-solute external fractions;
- absence of full likelihood-based uncertainty.

### 7.17 Figures section

A manuscript normally introduces figures in the relevant Results sections rather than including an internal inventory of what each figure is intended to show. Remove or convert this section into figure captions in the submission.

The sentence “every value regenerates” should be backed by the frozen build and source-data outputs. At present, Figure 4 does not show the new manifold result and Figure 6 does not show the reported ensemble or external result.

### 7.18 Related work

The section is comprehensive but long relative to the applied analysis. Condense by focusing on:

- practical identifiability/profile methods;
- profile-wise prediction and parameter-vs-prediction uncertainty;
- experimental design for transport/kinetic separation;
- espresso model/data lineage.

Do not imply that a literature gap establishes novelty without the archived search. Ensure every cited 2025/2026 source is finalized and bibliographically verified.

### 7.19 Reproducibility

Replace implementation-oriented lists with a concise Data and Code Availability section in the paper, and place command details in a repository README/supplement. Correct stale evidence tags. Add release DOI, commit, environment, input checksums, build command, expected runtime, and output checksums.

The analysis may remain outside routine CI because of runtime, but a scheduled or release workflow should execute it in a controlled environment. Fast unit tests should cover pure numerical contracts, while a slow tagged build verifies the complete result bundle.

---
## 8. Figure-by-figure review

### Figure 1 — Paper A study and evidence design

**What works**

- The evidence categories are now substantially more accurate.
- Angeloni O recalibration, within-campaign LOCO, within-campaign C/F holdout, Table 7 orthogonal measurement, in-sample Schmieder localization, same-model simulation, and independent Waszkiewicz data are visually separated.
- The legend makes clear that “external” means a different rig/coffee not used for target fitting.

**Remaining issues**

- The figure is text-dense, with small type likely to be difficult at journal column width.
- The target-recalibration lane does not show the null/reduced models that are essential to interpreting transfer skill.
- The Table 7 box appears after the C/F holdout in a linear flow, but it constrains the O profile rather than being a downstream result of the holdout.
- Red is used for independent external evidence, which may be misread as failure or danger.
- The same-model simulation box is visually parallel to empirical analyses but should be more clearly distinguished as synthetic.

**Required actions**

1. Add a “level-only reference model” node to the Angeloni holdout lane.
2. Reposition Table 7 as an orthogonal arrow into the profile/inventory–rate node.
3. Reduce box text and use a caption for definitions.
4. Confirm legibility at final print dimensions.
5. Use evidence-type shapes or line styles in addition to color for accessibility.

### Figure 2 — Inventory–rate SSE surface and profile

**What works**

- The valley and compensating inventory path are visually clear.
- Caffeine and trigonelline are shown side by side.
- The normalized profile makes the broad tolerance region easier to interpret than a raw surface alone.
- Table 7 inventory is included as an orthogonal constraint.

**Remaining issues**

- The 10% profile set reaches the upper rate boundary, but the graphic does not show right-censoring.
- The MAPE profile, now a corrected and cited result, is absent.
- The local Hessian condition number is printed without numerical-sensitivity context.
- The Table 7 line has no uncertainty band and no quantified intersection rate.
- The lower y-axis truncation and shading may make the profile appear closed when it is not.
- “Practical non-identifiability” in the title embeds the conclusion rather than neutrally naming the plotted object.

**Required actions**

1. Add a right-open arrow/`≥6.5` marker where the threshold set reaches the domain edge.
2. Add the MAPE profile or a companion panel.
3. Show SSE and MAPE minima and threshold-set overlap.
4. Include Table 7 uncertainty/sensitivity band and intersection range.
5. Put the condition number, basis, and grid in the caption rather than as an unqualified figure fact.
6. Export the full surface/profile source data.

### Figure 3 — Leave-one-condition-out holdouts

**What works**

- It shows individual held-out observations rather than only pooled summary statistics.
- Named solutes and varieties are separated.
- Units are now correct.

**Remaining issues**

- Between-solute concentration differences dominate the visual, so a near-diagonal cloud can obscure weak within-solute condition response.
- Predictions form compressed horizontal bands; this should be analyzed rather than left implicit.
- Temperature and pressure are not visible.
- There is no baseline prediction or model-minus-baseline error.
- The title contains a long resampling statistic and the displayed bracket lacks an explicit `%` sign.
- The descriptive interval can be mistaken for a confidence interval.

**Required actions**

1. Facet or normalize within solute/variety.
2. Add residual-vs-T and residual-vs-p panels or encode condition.
3. Add fold-specific constant/reduced-model predictions.
4. Plot paired model-minus-baseline absolute percentage error.
5. Move resampling details to the caption and label them non-coverage-calibrated.

### Figure 4 — Frozen O→C/F cross-grind holdout

**What works**

- C and F are separated.
- Variety and solute encoding is clear.
- The matched-endpoint correction is reflected in the plotted point predictions.

**Critical deficiencies**

- It shows only one point optimum, not the near-optimal-set transfer that now anchors the abstract.
- It does not show the ~22% worst profile-set error.
- It does not show a constant/reduced-model benchmark, despite the mechanistic result being nearly tied with the O-trained constant.
- The title claims “transfers reasonably” and “≤1 pp geometry-sensitive”; neither claim is directly displayed, and the latter is based on rounded geometry values.
- It labels 40 g although the operator uses 40 mL.
- Horizontal prediction bands suggest low condition-specific signal, which the current caption does not discuss.

**Required redesign**

- Draw the point prediction and profile-set envelope for every held-out observation.
- Add the O-trained constant as a comparison marker/line.
- Include a panel of model skill by fit and grind.
- Include the profile-set held-out MAPE as a function of rate.
- Use “matched 40 mL proxy” until mass-corrected.
- Replace the title with a neutral description.

### Figure 5 — Joint shared fit versus independent per-grind fits

**What works**

- The heatmaps expose heterogeneous cost-of-sharing by variety, solute, and grind.
- Boundary-fit flags are visible.
- The figure now correctly reads as an in-sample comparison in the manuscript.

**Remaining issues**

- There is no constant/reduced-model comparator.
- The independent comparator is aggregated from rounded values in the current code.
- A shared-model mean cost of 1.5 pp hides cells with much larger costs.
- The two mechanistic models have different flexibility, so lower independent in-sample error is expected.
- The star does not specify lower versus upper boundary.
- The title still foregrounds the mean as if it were a validation statistic.

**Required actions**

1. Correct precision and regenerate.
2. Add shared and per-grind constant baselines.
3. Report parameter counts and/or a held-out comparison.
4. Mark boundary direction.
5. Discuss cell-level heterogeneity rather than only the mean.
6. Use a neutral “in-sample compatibility” title.

### Figure 6 — Fraction-resolved versus aggregated scoring

**What works**

- The qualitative difference in profile shape is easy to see.
- The caption/title acknowledges empirical plus same-model evidence.
- The true synthetic rate is marked.

**Critical deficiencies**

- The synthetic profiles are seed 0 only, while the text reports 20-seed ensemble summaries.
- The empirical sampled aggregate is not a whole cup, whereas the synthetic line is an exact modeled integral; overlaying them invites an apples-to-oranges comparison.
- The external Waszkiewicz profile is absent despite its prominence in the abstract and Section 6.
- No uncertainty bands are shown.
- Range/domain dependence is not visible.
- The same-model truth rate lies exactly on the candidate grid.
- The figure does not show the high external minimum error or shallow external profile.

**Required redesign**

Create three clearly labeled evidence tiers:

1. in-sample Schmieder empirical fraction versus sampled aggregate;
2. same-model simulation median and seed bands, including off-grid truth/model discrepancy;
3. external Waszkiewicz shape profile with alignment/assumption bands.

Treat the one-scalar cup flatness as an algebraic schematic or note, not a plotted empirical validation curve.

### Cross-figure production requirements

All six figures should:

- be generated from the same raw, unrounded, versioned result bundle;
- have tidy machine-readable source-data files;
- be exported as PDF/SVG and high-resolution PNG;
- use consistent evidence terminology, units, and endpoint labels;
- include sample counts and evidence class in captions;
- avoid subjective/conclusion-bearing titles;
- be checked at final journal dimensions and for color-vision accessibility;
- have automated tests that confirm key plotted fields correspond to manuscript values.

---

## 9. Required numerical reruns and acceptance tests

### 9.1 Predictive-skill benchmark package

**Purpose:** determine whether the mechanistic model adds predictive skill beyond level-only or simple empirical references.

Required outputs:

1. Full-precision point predictions for all O training/LOCO and C/F holdout observations.
2. O-trained MAPE-optimal constant, mean, median, and same-T,p O lookup baselines.
3. Optional reduced models with clearly controlled parameter fitting.
4. Per-observation and per-condition losses.
5. Macro and micro summaries by grind, variety, and solute.
6. Skill scores and paired differences.
7. Descriptive uncertainty obtained by resampling the appropriate experimental unit and repeating fitting where feasible.
8. A baseline panel in Figures 3–5.

**Acceptance criterion:** Any statement that the model transfers must report incremental skill. If skill is negligible or negative, reframe the result as endpoint-error non-specificity rather than successful mechanistic transfer.

### 9.2 Profile and Hessian convergence package

Run at least:

- rate grids of 18, 36, 72, and 144 points;
- c_s0 grids of 41, 81, and 161 points for the surface/Hessian;
- multiple rate domains, e.g. `[0.05, 10]`, `[0.1, 20]`, subject to physical/numerical justification;
- finite-difference step multipliers around the chosen local point;
- continuous one-dimensional profile optimization/interpolation;
- alternative parameter bases/scalings;
- SSE, log-SSE/relative SSE, and MAPE profiles.

Required table fields:

- optimum rate/inventory;
- boundary flags;
- tolerance-set interval with open/closed endpoints;
- profile fraction and width within tested domain;
- condition number and coupling;
- threshold-set overlap between objectives;
- solver convergence/failure counts.

**Acceptance criterion:** The qualitative broad-profile conclusion is stable, and exact local diagnostics are reported only to the precision supported by convergence.

### 9.3 Profile-wise prediction package

For each variety × solute:

1. Define the primary profile set and several sensitivity sets.
2. Propagate every retained rate/inventory pair to each C/F observation.
3. Export per-observation min, max, median, and point-optimum prediction.
4. Report envelope widths and model-vs-baseline skill across the set.
5. Identify the parameter pair and observation producing the worst error.
6. Repeat under endpoint, flow, and geometry sensitivity.

**Acceptance criterion:** The phrase “prediction-stable along the profile” is used only if profile-wise envelopes are narrow relative to a declared practical scale and model skill remains positive relative to baseline across the relevant set.

### 9.4 Endpoint, flow, geometry, and measurement sensitivity package

At minimum vary:

- beverage endpoint 38, 40, and 42 g;
- density conversion over a justified range;
- primary and alternative pressure→flow maps;
- hydraulic-anchor and shot-time uncertainty;
- global and plausible grind-specific geometry choices;
- source RSD/heteroscedastic weighting;
- solver tolerances.

Report effects on:

- profile width and censoring;
- point and profile-set C/F skill;
- joint compatibility;
- Table 7 constrained rate;
- geometry-spread headline.

**Acceptance criterion:** Claims are either robust across this package or explicitly conditional on the primary assumptions.

### 9.5 Table 7 constraint package

Required outputs:

- unit conversion audit;
- measurement uncertainty/sensitivity band;
- profile intersection rate/range for each relevant solute/variety;
- whether the intersection is unique and interior;
- C/F predictions after applying the orthogonal constraint;
- comparison with unconstrained profile-set predictions.

**Acceptance criterion:** Figure 2 and text quantify rather than merely display the constraint.

### 9.6 Exact-cup simulation package

Run:

- at least 100 seeds or justify 20 with Monte Carlo error;
- off-grid truth rates;
- multiple noise levels and correlated/heteroscedastic errors;
- model-discrepancy variants;
- endpoint/time-origin perturbations;
- continuous fitted rate or dense interpolation;
- multiple observation schedules/number of fractions.

Store median and quantile profiles, not only seed 0.

**Acceptance criterion:** Figure 6 displays the ensemble, and the manuscript calls the result a same-model/sensitivity simulation with no empirical generalization beyond tested mismatch cases.

### 9.7 External Waszkiewicz package

Required outputs:

- raw observed trajectory with uncertainty;
- best-profiled prediction and residuals;
- full-precision rate profiles;
- offset, first-bin, temperature, flow-floor, density, binning, and horizon sensitivity;
- uncertainty-weighted and unweighted objectives;
- profile interval/tolerance set with boundary flags;
- explicit comparison to a simple shape baseline;
- no empirical interpretation of the one-scalar flat cup.

**Acceptance criterion:** The external conclusion is framed as shallow shape-objective localization under mismatch, and its sensitivity is visible in Figure 6 or supplement.

### 9.8 Reproducibility package

One release command should:

1. verify the source tree is clean and record the commit;
2. verify input checksums;
3. create/activate a pinned environment;
4. run fast tests;
5. execute slow analyses once;
6. validate a versioned result schema;
7. generate manuscript values, source data, and vector/raster figures;
8. write logs and checksums;
9. compare outputs against release expectations within declared numerical tolerances.

**Acceptance criterion:** An independent user can reproduce all reported values and figures from the archived release without manual edits or hidden files.

---
## 10. Suggested replacement wording for key passages

These are examples, not mandatory prose. Numerical placeholders should be populated only after the full-precision reruns.

### 10.1 Abstract — identifiability sentence

**Current issue:** exact local Hessian numbers and “no bounded minimum” are stated more strongly than the domain-censored profile supports.

**Suggested wording:**

> “For the single-grind Angeloni endpoint fit, profiling inventory at each kinetic-rate scale produced a broad near-optimal region under both unweighted SSE and MAPE. The 10%-above-minimum SSE set extended from approximately 0.4 to the upper tested rate boundary of 6.5, so its upper extent was not closed within the evaluated domain. A local log-parameter Hessian was highly ill-conditioned, consistent with strong inventory–rate compensation, although its numerical value is basis- and discretization-dependent.”

### 10.2 Abstract — transfer sentence before the benchmark rerun

> “At the selected O-grind optimum, held-out C/F absolute MAPEs ranged from approximately 3% to 18%; across the discrete O-grind MAPE set within 10% of its minimum, the largest aggregate held-out MAPE was approximately 22%. These errors describe within-campaign prediction after target recalibration. Incremental skill over simple level-only baselines remains to be established.”

### 10.3 Abstract — transfer sentence after a successful benchmark rerun

> “At the selected O-grind optimum, the model achieved a C/F macro-MAPE of X% versus Y% for an O-trained level-only baseline (skill Z%). Propagating the grid-converged near-optimal O profile produced condition-wise prediction envelopes of [summary], with worst held-out skill [summary]. Thus parameter uncertainty was larger than prediction variation under the tested profile set, although stability was incomplete.”

### 10.4 Abstract — external temporal-shape sentence

> “On a separate-rig TDS trajectory, profiling a target-specific level produced a shallow rate-dependent MAPE minimum (minimum approximately 27% under the primary alignment), whereas one integrated scalar was flat by construction because one free level can match one scalar at every rate. This external panel therefore tests temporal-shape sensitivity, not frozen absolute concentration or named-solute identification.”

### 10.5 Methods — endpoint wording

> “Angeloni report a 40 ± 2 g beverage endpoint. The primary implementation approximated this as a 40 mL terminal volume under ρ=1 g mL⁻¹ and constant flow; sensitivity analyses varied density and terminal mass/volume over the declared range. We therefore refer to the primary operator as a matched-volume proxy unless otherwise stated.”

### 10.6 Result 2 — boundary-censored profile

> “The SSE profile had an interior numerical minimum, but the 10%-above-minimum set reached the upper edge of the tested rate domain. The data therefore did not establish a closed upper tolerance bound within the tested domain; the reported width is a lower bound on the full near-optimal extent.”

### 10.7 Result 3 — profile-set terminology

> “We propagated a declared near-optimal MAPE set—rates whose O-grind MAPE was within 10% of the minimum—to the held-out C/F observations. This set is descriptive rather than probabilistic. After grid/domain convergence, we report the resulting condition-wise prediction envelope and its skill relative to an O-trained constant.”

### 10.8 Joint-fit interpretation

> “Fitting one shared inventory/rate pair to all O+C+F observations yielded X% in-sample macro-MAPE, compared with Y% for separate per-grind mechanistic fits and B% for a shared level-only baseline. This is an in-sample compatibility comparison, not a held-out transfer test.”

### 10.9 LOCO uncertainty sentence

> “The nine condition-level macro errors had mean X%, median Y%, and range [A,B]%. Percentile ranges obtained by resampling the already-computed errors are reported only as descriptive summaries; because the LOCO training sets overlap and the fits were not repeated under resampling, these ranges do not have nominal confidence-interval coverage.”

### 10.10 Same-model simulation sentence

> “In a discrepancy-free same-model simulation, temporally resolved observations produced a sharper rate objective than a single integrated observation. Because truth and fitting used the same solver and the primary true rate lay on the candidate grid, this is a best-case information-design illustration rather than evidence that real cups generally lack kinetic information.”

### 10.11 Main conclusion

> “For the tested single-grind endpoint design, inventory and rate were weakly separated by the objective. Prediction variation across the near-optimal set was smaller than parameter variation, but absolute held-out error, profile-wise prediction stability, and incremental skill over simple baselines must be reported separately. Time-resolved observations generated stronger rate sensitivity in the tested in-sample, synthetic, and external-shape analyses, with evidence strength and model mismatch stated for each.”

### 10.12 Possible revised concise abstract

> **Background:** Whole-cup validation can yield low prediction error while leaving a mechanistic parameter decomposition weakly localized. **Methods:** We refitted a multi-solute espresso extraction model, originally calibrated on fraction-resolved Schmieder data, to Angeloni whole-cup concentrations. Inventory was profiled analytically at each kinetic-rate scale, and selected/near-optimal calibrations were evaluated on held-out conditions and grinds. We separately compared fraction-resolved and aggregated objectives in calibration-lineage data, same-model simulation, and a target-profiled external TDS trajectory. **Results:** Under the single-grind endpoint design, SSE and MAPE both produced broad inventory–rate compensation regions; the SSE 10%-tolerance set reached the upper tested rate boundary. Point-optimum C/F errors were approximately 3–18%, and the discrete near-optimal-set worst error was approximately 22%, but preliminary level-only benchmarks achieved similar macro error, so incremental mechanistic skill requires explicit reporting. Fraction-resolved objectives were more rate-sensitive than aggregates in the tested designs; the external TDS minimum remained shallow and high-error, and its one-cup flat profile was algebraic under a free level. **Conclusion:** Endpoint error, parameter localization, prediction stability, and skill over a null model are distinct. Mechanistic validation should match the observation operator, propagate profile uncertainty to predictions, and include simple reference models and temporal observations where kinetic interpretation is sought.

---

## 11. Minor, editorial, and consistency comments

1. Replace code-style dataset names such as `` `pannusch2024` `` and `` `angeloni2023` `` in prose with author–year citations; reserve identifiers for Data/Code Availability.
2. Standardize “5-CQA” versus “5CQA” and define once.
3. Standardize `c_s0`, `c_{s,0}`, “inventory,” and units.
4. Define O, C, and F at first use and provide their physical granulometry meaning if available.
5. Avoid uppercase emphasis such as “REAL,” “WHOLE,” “INDEPENDENT,” and “ROBUST” in code-generated verdicts and manuscript prose.
6. Replace “positive control” with “in-sample information-design check” where that is more precise.
7. “Post-fit” is sometimes used as a dataset category and sometimes as an action; use “target-data recalibration” and “in-sample reconstruction.”
8. Do not call the six-window aggregate an endpoint without the qualifier sampled-fraction aggregate.
9. Add units to every parameter-domain statement.
10. Explain whether `rate_scale` is dimensionless and whether multiplying both A1 and A2 preserves any fitted physical relationship.
11. State how ties in weighted medians are handled; the current implementation selects the first crossing.
12. Explain how zero or near-zero concentrations are handled in MAPE; current data appear positive, but the method should state its domain.
13. Report the number of observations contributing to every macro-MAPE.
14. Distinguish macro-average over fits from micro-average over points in table headings.
15. Report exact rate grids and threshold membership counts in supplement.
16. Avoid “model-free evidence” for the profile: the profile is conditional on the mechanistic model and observation operator, even though the broadness is seen directly from the objective.
17. Replace “standard sloppiness basis” with “a declared log-parameter basis commonly used for relative parameter changes.”
18. Clarify whether Figure 2's inventory axis is mg/L, g/L equivalent, or another solid-phase unit; current label `g L⁻¹` may be easy to confuse with beverage concentration.
19. Use an en dash consistently for ranges and a true minus sign in figures where possible.
20. Ensure the 10% symbols in figure legends are rendered correctly; source strings contain doubled `%` for formatting.
21. Add `n` and evidence class to every figure caption.
22. Add panel labels at consistent positions and font sizes.
23. Use one convention for “rate scale” versus “Sherwood rate scale.”
24. Avoid “at the domain edge” unless the direction and exact boundary are stated.
25. Replace “flips across flow-map/domain” with quantified sensitivity.
26. Explain why total-solids/TDS are retained in some preliminary analyses but excluded from primary named-solute transfer.
27. Keep the distinction between optical TDS, gravimetric total solids, and the Pannusch pseudo-solute in a dedicated observable table.
28. Check the phrase “source's reported central values, not the replicate-level RSD”: RSD is a summary, not replicate-level values. Say “the repository lacks replicate-level measurements and uses reported central values; source RSD summaries are not propagated.”
29. Remove “the card marks it skip” and other internal data-card language.
30. Remove “handoff §2.6,” review IDs, and repository path references from scientific prose.
31. Explain the off-grid O points and why they form an appropriate holdout.
32. State whether the two off-grid points were used in any model or threshold development.
33. Ensure the source says 66 records/33 per variety and clarify how on-grid/off-grid counts sum across O/C/F.
34. Do not use “independent target” as a synonym for “independent validation”; the target is independent of original calibration but is then used for refitting.
35. Verify whether “different coffee” means different blend/origin/roast and state only what the source establishes.
36. Report whether T/p condition ordering or file row order affects any deterministic tie breaking.
37. Store random generator algorithm/version or use a reproducible NumPy environment lock.
38. Do not round rates to one decimal in degeneracy tables if the grid is irregular and nearby values matter.
39. Define “profile fraction of log grid” and distinguish it from continuous interval measure.
40. Avoid comparing profile fractions across different grid densities without weighting or continuous measure.
41. A log-width can be reported as `ln(r_hi/r_lo)` but should be marked censored when a boundary is reached.
42. In Figure 2, clarify whether contours are normalized independently by solute; direct color comparison may otherwise be misleading.
43. In Figure 5, use a diverging scale centered exactly at zero and state the common/independent color limits.
44. Avoid using p5–p95 on small deterministic sets; use min–max or explicitly call them grid quantiles.
45. Provide the actual number of points in each near-optimal set; the result object has it but the manuscript does not.
46. Explain why 10% relative loss was chosen and whether it was selected before inspecting the transfer envelope.
47. Separate numerical solver failures from poor model fit in any widened-domain profile.
48. Include a table of boundary flags for every fit.
49. Confirm the exact DOI and Zenodo record number for Waszkiewicz; the code mentions one record while search results may expose a concept/version DOI.
50. Cite the software packages and versions used for numerical integration and plotting.

---

## 12. Submission-readiness checklist

### 12.1 Scientific validity

- [ ] Full-precision transfer predictions exported.
- [ ] O-trained constant and other predeclared baselines evaluated.
- [ ] Model skill reported by grind, variety, solute, and condition.
- [ ] Near-optimal profile set grid/domain converged.
- [ ] SSE and MAPE profile overlap quantified.
- [ ] Profile boundary censoring explicitly reported.
- [ ] Hessian/condition-number sensitivity completed.
- [ ] Endpoint mass/volume sensitivity completed.
- [ ] Flow-map and geometry uncertainty propagated or claims narrowed.
- [ ] Measurement/RSD sensitivity completed.
- [ ] Table 7 profile intersection quantified.
- [ ] LOCO ranges kept descriptive or fit-repeating uncertainty implemented.
- [ ] Same-model simulation includes off-grid truth and model discrepancy.
- [ ] Waszkiewicz analysis retains full precision and broader sensitivity.
- [ ] All solute × variety profile panels supplied in supplement.

### 12.2 Figures and tables

- [ ] Figure 1 includes reference-model logic and remains legible at print size.
- [ ] Figure 2 shows censoring and SSE/MAPE profiles.
- [ ] Figure 3 shows condition structure and baseline comparison.
- [ ] Figure 4 shows profile-wise envelopes and null-model skill.
- [ ] Figure 5 includes reduced-model baselines and corrected precision.
- [ ] Figure 6 shows simulation ensemble and external profile as separate evidence tiers.
- [ ] All figures use correct endpoint terminology and units.
- [ ] Neutral titles replace subjective conclusions.
- [ ] Vector figures generated.
- [ ] Machine-readable source data generated for every panel.
- [ ] Figure captions state evidence class, sample count, objective, and uncertainty meaning.

### 12.3 Code and reproducibility

- [ ] Early-rounding defects removed.
- [ ] Raw and display values separated in result schema.
- [ ] Evidence taxonomy synchronized across manuscript, code, JSON, and captions.
- [ ] Profile/baseline/aggregation regression tests added.
- [ ] Seed ensemble stored, not only seed 0.
- [ ] Clean-tree, commit, input checksum, and environment metadata recorded.
- [ ] One command reproduces all values, tables, source data, and figures.
- [ ] Frozen release tag and archive DOI created.
- [ ] Slow release build rerun in a clean environment.
- [ ] Output checksums published.

### 12.4 Manuscript package

- [ ] Repository note removed.
- [ ] Review IDs, “owed” items, function-name prose, and change log removed.
- [ ] Complete equations and numerical methods added.
- [ ] Experimental/statistical units and replicate handling stated.
- [ ] Baseline methods and skill scores added.
- [ ] Limitations written as scientific limitations, not backlog items.
- [ ] Complete bibliography generated and verified.
- [ ] Data and Code Availability statements added.
- [ ] Funding, conflicts, author contributions, and acknowledgments added as required.
- [ ] Abstract and conclusion narrowed to evidence-supported claims.

---
## 13. Supporting reference material

The following sources are the most directly relevant references for interpreting the
source campaigns, the model lineage, the identifiability terminology, profile-wise
prediction, validation uncertainty, and computational reproducibility. They should be
converted to the target journal's reference style and cross-checked against the final
bibliography generated from `docs/literature_search/references.bib`.

### 13.1 Primary espresso data and model sources

1. **Schmieder, B. K. L., Pannusch, V. B., Vannieuwenhuyse, L., Briesen, H., &
   Minceva, M. (2023). “Influence of Flow Rate, Particle Size, and Temperature on
   Espresso Extraction Kinetics.” *Foods*, 12(15), 2871.**
   <https://doi.org/10.3390/foods12152871>

   **Relevance to this review:** This is the fraction-resolved source campaign used by
   the Pannusch calibration lineage. It documents the 15-setting face-centred central
   composite design, three repetitions for most settings, six at the centre, and the
   time-resolved extraction of caffeine, trigonelline, 5-CQA, and TDS. The manuscript
   should distinguish the source's ten collected fractions from the repository's
   derived six-window subset and should state that only reported/derived central values,
   not replicate-level measurements, enter the present analysis.

2. **Pannusch, V. B., Schmieder, B. K. L., Vannieuwenhuyse, L., Briesen, H., &
   Minceva, M. (2024). “Model-based kinetic espresso brewing control chart for
   representative taste components.” *Journal of Food Engineering*, 367, 111887.**
   <https://doi.org/10.1016/j.jfoodeng.2023.111887>

   **Relevance to this review:** This is the mechanistic multi-solute model being
   refitted and profiled. It is the appropriate source for the PDE structure,
   temperature/flow correlations, Sherwood coefficients, per-solute parameters, and the
   original calibration claim. Paper A should clearly separate parameters inherited
   from this source from the two target-data-adjusted quantities (`c_s0` and
   `rate_scale`).

3. **Angeloni, S., Giacomini, J., Maponi, P., Perticarini, A., Vittori, S.,
   Cognigni, L., & Fioretti, L. (2023). “Computer Percolation Models for Espresso
   Coffee: State of the Art, Results and Future Perspectives.” *Applied Sciences*,
   13(4), 2688.**
   <https://doi.org/10.3390/app13042688>

   **Relevance to this review:** This is the whole-cup target campaign. It supports the
   manuscript's use of temperature, pressure, granulometry, beverage concentrations,
   total solids, and the same-campaign roast-and-ground inventory measurements. It is
   also the source against which endpoint matching, duplicate-extraction handling,
   concentration units, and the pressure-to-flow approximation must be described. The
   O-to-C/F test is internal to this campaign even though the campaign is independent of
   the original Pannusch calibration data.

4. **Waszkiewicz, R., Myck, F., Białas, Ł., Puciata-Mroczynska, M., Dzikowski,
   M., Szymczak, P., & Lisicki, M. (2026). “Under pressure: Poroelastic regulation
   of flow in espresso brewing.” *Physics of Fluids*, 38(6), 063113.**
   <https://doi.org/10.1063/5.0319611>

   **Relevance to this review:** This is the independent second-rig trajectory used in
   the external-data objective-localization panel. Its value is the simultaneous
   time-resolved flow/TDS information, not a blind test of an absolutely calibrated
   concentration level: Paper A profiles a target-specific level against this shot.
   The manuscript should therefore report the large residual error and the shallow rate
   objective, and use “external-data objective localization” or “target-profiled shape
   comparison,” not “frozen external prediction.” The associated archived data/code
   record should be cited by a version-specific DOI in Data Availability.

### 13.2 Identifiability, profiling, and prediction from weakly identified models

5. **Raue, A., Kreutz, C., Maiwald, T., Bachmann, J., Schilling, M., Klingmüller,
   U., & Timmer, J. (2009). “Structural and practical identifiability analysis of
   partially observed dynamical models by exploiting the profile likelihood.”
   *Bioinformatics*, 25(15), 1923–1929.**
   <https://doi.org/10.1093/bioinformatics/btp358>

   **Relevance to this review:** This is a foundational reference for distinguishing
   structural from practical identifiability and for using profiles to expose
   compensation and unbounded/asymmetric parameter uncertainty. Paper A does not specify
   a likelihood, so its quantities should remain “profiled objective” and
   “objective-tolerance set,” not “profile likelihood” or “confidence interval.”

6. **Wieland, F.-G., Hauber, A. L., Rosenblatt, M., Tönsing, C., & Timmer, J.
   (2021). “On structural and practical identifiability.” *Current Opinion in
   Systems Biology*, 25, 60–69.**
   <https://doi.org/10.1016/j.coisb.2021.03.005>

   **Relevance to this review:** This review stresses the conceptual difference between
   structural and practical identifiability and cautions against relying only on local
   Fisher/Hessian approximations. It supports treating the local condition number and
   inverse-curvature coupling as secondary diagnostics, with the boundary-censored
   nonlinear profile carrying more of the interpretation.

7. **Simpson, M. J., & Maclaren, O. J. (2023). “Profile-Wise Analysis: A profile
   likelihood-based workflow for identifiability analysis, estimation, and
   prediction with mechanistic mathematical models.” *PLOS Computational Biology*,
   19(9), e1011515.**
   <https://doi.org/10.1371/journal.pcbi.1011515>

   **Relevance to this review:** This work explicitly links parameter profiles to
   prediction intervals/sets. It is directly relevant to Paper A's central separation
   of parameter localization and predictive stability. It also illustrates why
   propagating an objective/profile set to pointwise predictions is more informative
   than reporting only the selected optimum and a single worst aggregate MAPE.

8. **Simpson, M. J., & Maclaren, O. J. (2024). “Making Predictions Using Poorly
   Identified Mathematical Models.” *Bulletin of Mathematical Biology*, 86, 80.**
   <https://doi.org/10.1007/s11538-024-01294-0>

   **Relevance to this review:** This paper demonstrates that weak parameter
   identifiability need not imply weak prediction, provided the parameter uncertainty is
   propagated to predictions. It is the closest methodological support for Paper A's
   intended claim. The present manuscript should match that logic by showing
   profile-wise prediction envelopes and reference-model skill, not by equating modest
   aggregate error with mechanistic predictive value.

9. **Gutenkunst, R. N., Waterfall, J. J., Casey, F. P., Brown, K. S., Myers,
   C. R., & Sethna, J. P. (2007). “Universally sloppy parameter sensitivities in
   systems biology models.” *PLOS Computational Biology*, 3(10), e189.**
   <https://doi.org/10.1371/journal.pcbi.0030189>

   **Relevance to this review:** This is a core reference for broad sensitivity spectra
   and model-manifold geometry. It supports using geometric language carefully, but it
   does not make a scale-dependent Hessian condition number a universal or
   likelihood-calibrated measure of identifiability. The manuscript's restrained term
   “inventory–rate profile valley” is preferable unless a full scaled sensitivity
   analysis is provided.

### 13.3 Cross-validation and dependence

10. **Bengio, Y., & Grandvalet, Y. (2004). “No Unbiased Estimator of the Variance
    of K-Fold Cross-Validation.” *Journal of Machine Learning Research*, 5,
    1089–1105.**
    <https://www.jmlr.org/papers/v5/grandvalet04a.html>

    **Relevance to this review:** Cross-validation test errors are dependent because
    training sets overlap. This supports the revision's decision to call the two LOCO
    intervals descriptive, but also shows why resampling already-computed fold errors—at
    either the residual or condition level—does not establish nominal confidence
    coverage or prove that fold dependence is negligible.

11. **Roberts, D. R., Bahn, V., Ciuti, S., Boyce, M. S., Elith, J.,
    Guillera-Arroita, G., Hauenstein, S., Lahoz-Monfort, J. J., Schröder, B.,
    Thuiller, W., Warton, D. I., Wintle, B. A., Hartig, F., & Dormann, C. F.
    (2017). “Cross-validation strategies for data with temporal, spatial,
    hierarchical, or phylogenetic structure.” *Ecography*, 40(8), 913–929.**
    <https://doi.org/10.1111/ecog.02881>

    **Relevance to this review:** Although developed in ecology, the paper is a useful
    general reference for aligning holdout blocks with the intended extrapolation and
    dependence structure. Paper A should state separately what its condition LOCO test,
    off-grid O holdout, and O-to-C/F grind holdout estimate; these are different target
    tasks, not interchangeable replications of one generalization error.

### 13.4 Computational reproducibility and archival practice

12. **Sandve, G. K., Nekrutenko, A., Taylor, J., & Hovig, E. (2013). “Ten Simple
    Rules for Reproducible Computational Research.” *PLOS Computational Biology*,
    9(10), e1003285.**
    <https://doi.org/10.1371/journal.pcbi.1003285>

    **Relevance to this review:** The recommendations to track how every result was
    produced, avoid manual data manipulation, archive exact software versions, and
    retain intermediate/source data align directly with the requested single-source
    Paper A build and machine-readable figure-data package.

13. **Peng, R. D. (2011). “Reproducible Research in Computational Science.”
    *Science*, 334(6060), 1226–1227.**
    <https://doi.org/10.1126/science.1213847>

    **Relevance to this review:** This article frames computational reproducibility as a
    minimum standard when full independent replication is difficult. That is especially
    pertinent here because the primary results depend on slow PDE solves, constructed
    observation maps, and multiple post-processing stages.

14. **Wilkinson, M. D., Dumontier, M., Aalbersberg, I. J., et al. (2016). “The
    FAIR Guiding Principles for scientific data management and stewardship.”
    *Scientific Data*, 3, 160018.**
    <https://doi.org/10.1038/sdata.2016.18>

    **Relevance to this review:** FAIR principles support publishing versioned,
    machine-readable source data and sufficiently rich metadata for every figure and
    table. A Git repository is valuable but is not, by itself, a permanent scholarly
    archive; the release should be deposited with a persistent DOI.

### 13.5 Reference-use cautions specific to Paper A

- **Do not cite profile-likelihood work as though the present SSE/MAPE tolerance sets
  were likelihood confidence regions.** The literature is methodological support for
  profiling and prediction propagation; statistical coverage requires an observation
  model and calibrated threshold.
- **Do not use the independent Waszkiewicz paper to imply independent concentration-level
  prediction.** The analysis fits a target-specific nuisance level and therefore tests
  temporal shape/rate localization conditional on that level.
- **Do not treat same-campaign Angeloni Table 7 measurements as an external dataset.**
  They are orthogonal measurements within the target campaign and can constrain the
  profile if their uncertainty and unit mapping are made explicit.
- **Do not cite generic identifiability literature in place of reporting numerical
  convergence.** The rate grid, threshold, domain, finite-difference step, parameter
  scaling, endpoint operator, and weighting must all be documented and tested in this
  application.

---

## 14. Bottom-line decision and minimum conditions for reconsideration

**Recommendation: Major revision before journal submission.**

The updated Paper A has made real and technically important progress. The corrected
MAPE profile, explicit near-optimal-set transfer, improved evidence taxonomy,
descriptive treatment of LOCO resampling, and expanded build orchestration directly
resolve several prior-review blockers. The broad inventory–rate compensation under the
tested single-grind matched-endpoint design remains a credible central finding. The
paper also has a potentially useful methodological message: parameter localization,
predictive stability, endpoint accuracy, and transportability are different empirical
properties.

The present draft is not yet submission-ready because its strongest positive transfer
claim lacks a meaningful null-model comparison. In the independent data-only check
performed for this review, an O-trained constant concentration is within approximately
0.36 percentage points of the reported mechanistic C/F macro-MAPE and is better for
some fit/grind combinations. This does not invalidate the confounding result. It does,
however, mean that low C/F MAPE and a relatively narrow profile-set MAPE envelope do not
yet demonstrate that the transferred kinetic structure adds substantial predictive
information beyond a level carried from O. The manuscript must either establish such
incremental skill from full-precision condition-level predictions or explicitly narrow
its claim to “the fitted level-plus-rate pair does not catastrophically deteriorate
across these grinds.”

At minimum, a revision suitable for another scientific review should:

1. **Add and report predeclared reference models.** Export full-precision condition-level
   predictions and compare the mechanistic transfer with O-trained constant, pooled-
   mean, simple T/p trend, and—where justified—a low-dimensional empirical baseline.
   Report paired error differences, distributions, and cases where the mechanistic model
   is worse.
2. **Propagate the profile set to the observable, not only to aggregate MAPE.** Show
   pointwise C/F prediction envelopes, threshold membership, domain/grid convergence,
   SSE–MAPE set overlap, and results under at least one measurement-error weighting.
3. **Correct numerical and inferential precision.** Remove early rounding from geometry,
   joint-fit, and summary aggregation; mark boundary-censored profiles; test Hessian
   scaling and finite differences; and avoid confidence language for descriptive
   resampling.
4. **Test the observation and transport assumptions.** Quantify sensitivity to the
   40 g-versus-40 mL approximation, endpoint tolerance, pressure-to-flow map, grind
   geometry, source RSD information, and target-specific nuisance-level profiling.
5. **Redesign the evidence package.** Figures 2 and 4 should expose profile censoring,
   profile-wise predictions, and baseline skill; Figure 6 should separate in-sample,
   same-model, and independent-rig evidence and display ensembles rather than seed 0.
6. **Convert the repository draft into a conventional manuscript.** Add complete
   equations and methods, a verified bibliography, Data/Code Availability, a frozen
   environment and release DOI, vector figures, and machine-readable source data; remove
   review IDs, backlog language, function-name prose, and internal repository notes.

A well-executed revision could still produce a strong case study. Indeed, the null-model
comparison may sharpen rather than weaken the central lesson: endpoint validation can
look successful while carrying little information about kinetic mechanism. That is a
more discriminating and scientifically valuable conclusion than treating a low MAPE,
by itself, as evidence of mechanistic transfer.

---

*End of review.*
