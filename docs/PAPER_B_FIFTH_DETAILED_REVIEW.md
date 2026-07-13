# Detailed technical review of the updated `PAPER_B_DRAFT.md`

**Repository:** [`trbrewer/puckworks`](https://github.com/trbrewer/puckworks)  
**Review date:** 2026-07-13  
**Recommendation:** **Major revision before journal submission**  
**Primary review anchor:** raw `docs/PAPER_B_DRAFT.md` retrieved during this review, SHA-256 `f93e3fff4633a7018e69814f2f8eed25575d859756afe944990ec2b35b839c84`  
**Figures reviewed:** all five current Paper B figures and their generating paths  
**Prior review used for comparison:** `PAPER_B_CURRENT_DETAILED_REVIEW.md`, which assessed the earlier `e297f54169d9b975750b3773d02a639d1e2fbc85` tree

---

## 1. Scope, provenance, and review limits

This review covers the scientific argument, statistical interpretation, figures, data contracts, code-to-claim traceability, and reproducibility state of the updated Paper B draft. I inspected:

- the complete current `PAPER_B_DRAFT.md`;
- Figures 1–5 at publication rendering size;
- the principal Paper B routines in `puckworks/harness.py`;
- the Paper B build and result-bundle contract;
- the response-surface, temporal-ladder, cross-pressure, residual, and N-tube analysis paths;
- the committed Schmieder-derived cup-mass table and evidence-matrix files;
- figure-generation logic and data-dictionary claims; and
- relevant primary literature on the source experiments, block and wild bootstrap methods, post-selection uncertainty, swelling, extraction modeling, and spatially uneven extraction.

The review combines static code inspection, direct figure inspection, claim-to-code tracing, and targeted independent calculations from the committed tabular data. It does **not** claim a clean-room rerun of every slow poroelastic or N-tube calculation in a newly provisioned and independently pinned environment. That limitation is important because the repository does not currently provide a clean, commit-coherent Paper B release artifact; this is itself a principal review finding.

### 1.1 Artifact identity and reproducibility warning

The repository state exposed during this review is not a single clean snapshot:

- the branch/commit listing reported `e297f54169d9b975750b3773d02a639d1e2fbc85` as the current `main` head;
- the raw `PAPER_B_DRAFT.md` retrieved during review contains revisions beyond the exact-commit manuscript at that SHA;
- the current committed Paper B results bundle self-reports `source_commit = fa4ec00d743973734a3190007a7437948cf9a405` and `git_dirty = true`; and
- the build can perform a non-strict verification even when the tree or bundle is stale, although its strict release mode is designed to reject that state.

I therefore use the **file hash above**, rather than an assumed branch-to-file mapping, as the authoritative manuscript review anchor. Before submission, the authors should create a clean tagged release in which manuscript, code, data, result bundle, source-data exports, and figures all resolve to one commit.

### 1.2 Reviewed local artifact hashes

| Artifact | SHA-256 |
|---|---|
| Current `PAPER_B_DRAFT.md` | `f93e3fff4633a7018e69814f2f8eed25575d859756afe944990ec2b35b839c84` |
| Current inspected `puckworks/harness.py` | `fb196f77049dffaffc0de1ca8076782cb7a765500dca51e18eee4eee42167330` |
| Current inspected Schmieder-derived CSV | `39b7c16f9d9da614f151f46cb0db1440d43f150fbf49d3d2119f3f2fa1622f43` |
| Figure 1 PNG | `a934dbfa7fe0b952f24c4d38e05703a372ca4ffd66b020ad7b29422aae139cf7` |
| Figure 2 PNG | `68f1f76ec67ad2d625f2f935ff476d0433b4e9b7e1a440b5833752cdd5089792` |
| Figure 3 PNG | `667ac7fc7e0dcb41a9b4a6a98dd2c0e5629b8bd70dcd8865831ed916715bcdec` |
| Figure 4 PNG | `5a8e8c2d1a6158ebfb135cbfd5e1913e84e1909383392d75a03aee06b9f3a340` |
| Figure 5 PNG | `d347cc6f363ada342ced221acca9521d4581c512cb1b8af8baa537145fa31e3d` |

---

## 2. Executive assessment

The updated draft is materially stronger than the version reviewed previously. It now contains a more accurate account of the source endpoint, achieved-predictor response-surface fitting, deletion and heteroskedasticity sensitivities, an explicit flexible temporal null, dependence-aware language, plotted leave-one-pressure-out results, a narrower swelling/fines sign claim, and a substantially expanded exploratory N-tube robustness section. The central organizing idea is both useful and defensible:

> Within the datasets and implemented model set considered, integrated observables can demonstrate model capacity, incompatibility, and a need for temporal flexibility while remaining insufficient to identify a unique physical mechanism.

That thesis could support a strong methods/limitations paper. The current draft, however, is not yet submission-ready. Several new analyses are either described more strongly than implemented or are inconsistent with the current result bundle. The most consequential problems are summarized below.

### 2.1 Submission-blocking findings

1. **The paper is not tied to a clean, coherent release.** The current bundle is marked dirty and points to a different source commit; the build does not establish that the manuscript, figures, code, and exported source data were generated together.

2. **The Jensen calculation is described incorrectly.** The prose defines the direct gap as `E[EY(K)] − EY(1)` and says the evaluated multipliers have mean one. The corrected implementation instead compares against `EY(E[K_evaluated])`, because clipping shifts the numerical mean by as much as approximately 0.0051. The recorded direct gaps span approximately **−4.64 to −1.38 extraction-yield points**; calling approximately −1.4 the “worst” gap reverses the magnitude ordering.

3. **The Result 2 “moving-block bootstrap” does not refit either model.** It resamples contiguous indices from two already-computed squared-error sequences. This is a conditional block resampling of fixed losses, not a bootstrap of the model-fitting and model-comparison procedure. It does not support the draft’s claim that the mechanistic trajectory and cubic are “statistically indistinguishable.”

4. **The cross-pressure prose is stale relative to the current result bundle.** The manuscript gives LOPO/shared/off-9-bar values ending in `0.516/0.510/0.522`; the current bundle gives approximately `0.525/0.519/0.530` for the corresponding RC-3b summaries.

5. **The source-data CSV contains malformed rows that are silently filtered.** Thirty-six rows lack grind, cup mass, and concentration. They occur under experiment 15 across all component × brew-ratio combinations and carry summary-like covariate values. The 576 valid rows are present, but malformed records must be separated or rejected by schema validation rather than disappearing through downstream filtering.

6. **The N-tube switching-convergence claim is not implemented as documented.** The routine’s documentation promises a maximum full-trajectory deviation from the finest solution, but the code stores collapse time, peak time, final effective-channel count, and entropy only. Event times are measured on the outer output grid without interpolation, and only explicit Euler substepping is tested. This cannot justify “not a stepping artefact.”

7. **The N-tube robustness narrative suppresses substantial event variability and misclassifies some states.** Final `N_eff` can saturate while collapse time shifts by roughly 39% across tube count, by more than a second across grind/pressure, and over approximately 1.4–3.5 s across 16 seeds. Some seeds end with two effective channels. The classifier labels a top-decile concentration at lateral coupling 0.1 as “concentrates” despite a maximum single-tube share of only about 0.068 and `N_eff ≈ 19`.

8. **The draft remains an internal review-management document.** It contains review IDs, roadmap references, function names as prose, “still owed” statements, an open-gap ledger, and a status/to-do section. A conventional Methods, Results, Discussion, references, declarations, and clean release are still absent.

### 2.2 Recommended disposition

**Major revision.** The draft should not be submitted until the P0 actions in Section 4 are completed and the numerical claims are regenerated from a clean, versioned result bundle. Result 3 should remain explicitly exploratory unless the authors add a genuine trajectory-convergence and physical-balance analysis; absent that work, it would be safer as a clearly marked simulation appendix or separate methods note.

---

## 3. Material improvements since the preceding review

The revision deserves credit for substantive corrections rather than cosmetic changes.

1. **Source design and endpoint provenance are clearer.** The manuscript now distinguishes 15 settings, 48 complete TDS/BR-1/2 run rows, three extraction repetitions per setting and six at the center, and a source-derived endpoint obtained from a measured first fraction plus integrated fitted kinetics.

2. **The primary RSM contract now uses achieved predictors.** It evaluates the grind cross-section at the achieved conditions of the nominal center point and reports centered/scaled conditioning, deletion ranges, a full-quadratic sensitivity, and wild-bootstrap checks.

3. **The Result 1 claim is narrowed appropriately.** The three selected cell means are described as numerically ordered rather than as proof of a monotone causal grind response.

4. **Figure 2 is data-driven and accompanied by a dictionary.** This is a significant improvement over the earlier hard-coded evidence matrix.

5. **The Result 2 comparator hierarchy is more honest.** The cubic is labeled an in-sample flexibility bound, donor parameter provenance is tabulated, and the paper avoids the phrase “parameter-free.”

6. **Residual dependence is acknowledged.** The draft explicitly reports very strong serial dependence and warns that pointwise RMSEs are reconstruction scores, not held-out predictive validation.

7. **LOPO results are now plotted.** Figure 3 exposes held-out pressure-level values rather than leaving the strongest calibration-stability argument in prose alone.

8. **The swelling/fines conclusion is properly conditional.** The draft restricts the sign test to isolated resistance-increasing branches under imposed fixed pressure and states that coupled beds can contain multiple simultaneous processes.

9. **Result 3 is explicitly exploratory.** The draft no longer calls the N-tube result a linear instability or stability theorem; it discloses floor dependence, control-law dependence, and the proxy nature of lateral homogenization.

10. **The numerical audit has improved.** The current N-tube code tracks full-trajectory extrema for several normalization and non-negativity checks, correcting the earlier final-step-only bookkeeping defect. The remaining issue is that these are numerical invariants enforced largely by construction, not physical conservation laws.

These improvements should be retained. The required revisions below chiefly concern implementation fidelity, evidential calibration, and conversion to a conventional paper.

---

## 4. Prioritized required-action matrix

Priority definitions: **P0** = submission blocker; **P1** = major issue that materially affects interpretation or reproducibility; **P2** = important clarity, presentation, or completeness issue.

| ID | Priority | Required action | Acceptance criterion |
|---|---:|---|---|
| B5-01 | P0 | Create a clean, commit-coherent Paper B release. | A tagged commit with `git_dirty=false`; manuscript, code, input data, result bundle, source-data exports, and all five figures are generated from that commit and cryptographically listed in one manifest. |
| B5-02 | P0 | Make the release build strict by default in CI. | CI fails on a dirty tree, stale source commit, hash mismatch, missing artifact, manuscript/result mismatch, or untracked numerical output. |
| B5-03 | P0 | Correct the Jensen reference and wording. | Use `J = E[EY(K_eval)] − EY(E[K_eval])`, report `E[K_eval]`, and regenerate the range from full precision. Replace “worst ≈−1.4” with the correct largest-magnitude and smallest-magnitude deficits. |
| B5-04 | P0 | Reimplement or relabel the Result 2 block analysis. | Either refit both branches inside each dependence-preserving resample/subsample, or explicitly call the current calculation a conditional block resampling of fixed loss differences. |
| B5-05 | P0 | Remove the “statistically indistinguishable” inference. | Use “the difference is not resolved by this conditional interval,” or conduct a pre-specified equivalence/non-inferiority analysis with a scientifically justified RMSE margin. |
| B5-06 | P0 | Regenerate every cross-pressure number from one result object. | Manuscript, tables, Figure 3, source data, and bundle all report the same full-precision LOPO/shared/off-9-bar summaries. |
| B5-07 | P0 | Repair the malformed Schmieder-derived CSV. | No experimental row may lack the primary predictors/outcome. Summary/design metadata are moved to a separate table or explicitly tagged; schema and uniqueness tests fail on malformed records. |
| B5-08 | P0 | Replace the N-tube convergence claim with a real trajectory-convergence study. | Compare interpolated trajectories on a common physical-time grid; report norms and event-time errors versus spatial and temporal refinement; include at least one higher-order/adaptive solver. |
| B5-09 | P0 | Correct the N-tube state classifier. | Distinguish single-channel, oligarchic/top-decile, distributed, and transient switching using explicit thresholds on top-1 share, `N_eff`, entropy, and persistence. |
| B5-10 | P0 | Reconcile the stochastic sample count. | Table, prose, bundle, and figure all state the same number of realizations; preferably use ≥100 seeds or present exact finite-sample order-statistic intervals without “tight distribution” language. |
| B5-11 | P0 | Convert the draft into a conventional manuscript. | Remove review IDs, roadmap references, implementation function names from the scientific narrative, open-gap/status sections, and correction-history prose; add complete Methods, equations, references, declarations, and data/code availability. |
| B5-12 | P1 | Report the RSM uncertainty as conditional. | State that intervals condition on the selected seven-term model and the source-derived endpoint; show a heteroskedasticity-robust curve band in Figure 1 or supplement. |
| B5-13 | P1 | Add leverage-adjusted wild-bootstrap sensitivity. | Use HC2/HC3 residual scaling before Rademacher/Mammen multiplication and report the resulting vertex/curve interval. |
| B5-14 | P1 | Address post-selection uncertainty. | Re-run model selection within resamples, use a pre-specified full quadratic, or explicitly present the selected-form interval only and add a model-form envelope. |
| B5-15 | P1 | Add design-support sensitivity for the RSM. | Report setting-level cluster/deletion diagnostics and explain that one campaign and 15 design settings limit generalization. |
| B5-16 | P1 | Propagate first-stage endpoint uncertainty or state it is omitted. | Either bootstrap the source’s fraction-to-cup integration stage or explicitly label all RSM uncertainty as conditional on reconstructed cup masses. |
| B5-17 | P1 | Separate conditional RSM cross-section from central-cell means in Figure 1. | The caption and graphics make clear that the fitted curve holds achieved flow/temperature fixed while displayed cell means arise under different achieved conditions. |
| B5-18 | P1 | Add block-length and window sensitivity for Result 2. | Show 4/8/16/24 s blocks or a justified data-driven range, plus all declared time windows, with model refitting where applicable. |
| B5-19 | P1 | Add genuinely prospective temporal validation where feasible. | Use prequential or blocked train/test windows, or relabel the result purely as in-sample reconstruction and avoid predictive language. |
| B5-20 | P1 | Display residual trajectories and uncertainty. | Figure 3 or supplement shows residual-vs-time/ACF by branch and makes the coherent lack of fit visible. |
| B5-21 | P1 | Preserve branch provenance without shorthand claims. | Replace “0 fit Q(t)” with “0 coefficients estimated from this scored flow trace; 2–5 donor/campaign parameters imported,” in caption/table. |
| B5-22 | P1 | Add pressure-level uncertainty to cross-pressure scores. | Use a dependence-aware resampling/unit appropriate to the source traces and distinguish uncertainty in equilibrium refits from fixed donor trajectories. |
| B5-23 | P1 | Scope the LOPO conclusion. | State only that the two-parameter equilibrium calibration is not dominated by one pressure; do not imply physical validation of the residual-vs-pressure pattern. |
| B5-24 | P1 | Relabel “conservation” as a numerical-invariant audit unless physical balances are added. | Separate tautological normalization checks from mass, solute inventory, pressure-work, lateral-flux, and age balances. |
| B5-25 | P1 | Add a finite per-tube solute/inventory balance. | Extraction cannot proceed without bounded inventory; report initial, extracted, and residual inventory and numerical closure error. |
| B5-26 | P1 | Audit donor extrapolation and clipping. | Report the fraction of tube-times outside the donor trajectory range and at the porosity cap; repeat with no extrapolation or a justified terminal law. |
| B5-27 | P1 | Quantify event-time dependence on `N`, grind, pressure, and seed. | Report collapse/switching time distributions and top-1/entropy trajectories, not endpoint `N_eff` alone. |
| B5-28 | P1 | Add start-state and horizon sensitivity. | Test multiple initial heterogeneity amplitudes/distributions and shot horizons; report whether concentration, recovery, and switching persist. |
| B5-29 | P1 | Test a physical lateral-exchange operator or demote the claim. | Replace algebraic blending with a mass-conserving transverse-Darcy/network term, or label lateral results strictly as regularization sensitivity. |
| B5-30 | P1 | Clarify boundary-condition caricatures. | Explain what “fixed flow” and “fixed pressure” omit from a coupled pump–headspace–bed system and avoid mapping them directly onto real machines without analysis. |
| B5-31 | P1 | Make the Figure 2 ontology publication-ready. | Replace internal tokens (`impl`, `qual-cap`, `n/e`) with reader-facing definitions, non-ordinal categorical encoding, and an accessible supplementary table. |
| B5-32 | P1 | Verify every bibliography identifier. | Remove “believed” DOI language; use exact primary-source DOI and bibliographic metadata, including Lee et al. `10.1063/5.0138998`. |
| B5-33 | P1 | Generate text/table values from the frozen result bundle. | No manually duplicated headline constants remain in prose or build expectations; manuscript tables are templated from versioned results. |
| B5-34 | P1 | Make figures consume the frozen result bundle. | Figure generation does not rerun independent fits or embed conclusions; it reads one validated result object plus source data. |
| B5-35 | P1 | Expand the manifest to the full dependency graph. | Hash manuscript, all code modules, environment/lock file, raw/derived data, result bundle, source-data exports, and rendered vector/raster figures. |
| B5-36 | P1 | Replace duplicated “expected” constants with artifact-derived validation. | Checks compare bundle fields to regenerated computations and manuscript-rendered fields, not to manually copied numerical literals. |
| B5-37 | P1 | Reconcile stale RSM values in the open-gap ledger before deleting it. | All reported adjusted R², CI, Q², leverage, and condition numbers match one result bundle. |
| B5-38 | P2 | Rework Figure 3 layout. | LOPO markers remain legible; branch labels are reader-facing; pressure panels have consistent units, scales, and uncertainty. |
| B5-39 | P2 | Rework Figure 5 around diagnostics rather than endpoint saturation. | Main panels show physical-time trajectories, event-time convergence, and seed distributions; floor and broad OFAT sweeps move to supplement. |
| B5-40 | P2 | Make Figure 4 an explicit ablation diagnostic. | Include observed trace, extraction-only, swelling-only where meaningful, and combined branch with residual panel and parameter provenance. |
| B5-41 | P2 | Quantify detectability for the Result 1 bump. | Compare prominence with run-level uncertainty or a pre-specified minimum scientifically meaningful effect; avoid implying robustness from grid fraction alone. |
| B5-42 | P2 | Add a limitations table by evidence class. | For each result, state calibration data, evaluation data, fitted coefficients, held-out unit, omitted uncertainty, and maximum defensible inference. |
| B5-43 | P2 | Tighten related-work and novelty language. | Complete the systematic search before asserting novelty; distinguish contribution in observable matching/evidence discipline from novelty of each component model. |
| B5-44 | P2 | Export complete source data for every figure. | Provide machine-readable coordinates, intervals, classifications, and dictionaries sufficient to regenerate every panel without rerunning slow analyses. |
| B5-45 | P2 | Provide vector figures and accessibility checks. | SVG/PDF versions, color-blind-safe encoding, minimum font size, alt text, and monochrome legibility are documented. |

---

## 5. Targeted independent checks

These checks were performed independently from the manuscript prose using the inspected committed data/code. They are intended as diagnostics, not as a substitute for the clean release rerun required above.

### 5.1 Schmieder-derived data structure

The inspected CSV has **612 rows and 14 columns**. Of these:

- **576 rows** have the expected experimental predictors and outcomes. This count is internally coherent with 4 components × 3 brew ratios × 48 runs.
- **36 rows** have missing grind, cup mass, and concentration.
- All 36 malformed rows are associated with experiment 15, repetitions 1–3, and all 12 component × brew-ratio combinations.
- Those rows carry summary-like values in several covariate fields rather than ordinary experimental records.

The current RSM path happens to exclude them because the required predictor/outcome fields are missing. Silent exclusion is not an acceptable data contract. A future change to filtering or imputation could cause these rows to enter an analysis incorrectly. The correct repair is structural: separate experiment/run observations from design summaries and enforce a schema with a unique primary key.

### 5.2 Primary RSM recomputation

Using the 48 complete TDS, brew-ratio 1/2 run rows and the achieved-predictor seven-term model described in the draft, I obtained:

| Quantity | Independent check |
|---|---:|
| Grind vertex at the center achieved flow/temperature | **1.74315** |
| Adjusted R² | **0.64340** |
| Maximum leverage | **0.2000** |
| Leave-one-run vertex range | approximately **1.736–1.765** |
| Leave-one-setting vertex range | approximately **1.720–1.776** |
| Within-setting SD range | approximately **0.0141–0.2418 g** |
| Ratio of largest to smallest within-setting SD | approximately **17.1×** |

These results support the draft’s claim that the selected quadratic has a stable conditional vertex near 1.74. They do **not** establish that the physical response has an interior maximum, because the conclusion remains conditional on:

- the selected seven-term response form;
- the achieved-predictor support of one campaign;
- reconstructed rather than directly measured cup endpoints;
- the source’s first-stage kinetic fits;
- treatment of run-level heteroskedasticity; and
- no replication across machines, coffees, or campaigns.

### 5.3 RSM interval sensitivities

Approximate delta-method intervals for the vertex illustrate the effect of covariance choice:

| Covariance treatment | Approximate 95% vertex interval |
|---|---|
| Conventional OLS/t | **[1.690, 1.797]** |
| HC3/t | **[1.681, 1.805]** |
| Cluster-robust by 15 setting IDs/t₁₄ | **[1.674, 1.812]** |

A cluster-pairs bootstrap used as a deliberately conservative design-support stress test produced a much broader and asymmetric distribution, with an approximate percentile interval of **[1.52, 2.08]** and about 90% of fits concave with an in-domain vertex. That is not necessarily the preferred primary interval—the design settings are fixed rather than a random cluster sample—but it demonstrates how strongly inference can depend on what is regarded as the resampling unit. The manuscript should explain its estimand and resampling target rather than presenting one interval as unconditional.

### 5.4 Jensen audit

The manuscript says the evaluated lognormal multipliers are unit-mean after clipping and defines the direct comparison against `EY(1)`. The current implementation correctly recognizes that clipping changes the evaluated weighted mean and uses the actual mean-permeability reference.

The current bundle records:

- evaluated multiplier means approximately **0.9949–1.0000**;
- maximum absolute shift from one of approximately **0.0051**; and
- direct Jensen gaps approximately **−4.6355 to −1.3793 extraction-yield points**.

Thus every tested direct gap is negative, which supports the qualitative claim. The required correction is mathematical and rhetorical:

> For each evaluated quadrature cell, compare the ensemble yield with the homogeneous yield at the **evaluated weighted-mean multiplier**, not automatically at one. All tested direct gaps were negative, ranging from approximately −4.64 to −1.38 EY points.

### 5.5 Result 2 temporal-window sensitivity

The current result bundle reports that branch ordering depends materially on the scoring window:

| Window | Empirical Φ(t) RMSE | Cubic RMSE | Ordering |
|---|---:|---:|---|
| 10–90 s | approximately **0.117** | approximately **0.128** | Φ(t) lower |
| 15–95 s | approximately **0.116** | approximately **0.096** | cubic lower |
| 20–90 s | approximately **0.110** | approximately **0.062** | cubic much lower |

This supports the broad conclusion that a time-varying curve is needed relative to constant branches. It does not support a stable Φ-versus-cubic tie. The ordering between mechanistic and flexible temporal branches changes with the evaluation window, which should be shown rather than compressed into “statistically indistinguishable.”

### 5.6 What the current block routine actually computes

The current routine:

1. fits or evaluates the two branches once;
2. stores their pointwise squared-error sequences;
3. samples contiguous blocks of indices from those fixed sequences; and
4. recomputes RMSE differences from the sampled losses.

It does **not** refit the cubic, re-estimate donor-linked trajectories, or propagate uncertainty in the imported parameters. Therefore, its interval is conditional on the already-fitted predictions. This can be useful as a descriptive dependence-aware loss resampling, but it is not a bootstrap confidence interval for the entire model-comparison procedure.

### 5.7 Cross-pressure numerical mismatch

The current manuscript reports:

- LOPO held-out: `0.534 / 0.347 / 0.516`;
- shared all-pressure: `0.524 / 0.335 / 0.510`; and
- shared off-9-bar: `0.512 / 0.356 / 0.522`.

The current result bundle instead records approximately:

- LOPO held-out: **`0.534 / 0.347 / 0.525`**;
- shared all-pressure: **`0.524 / 0.334 / 0.519`**; and
- shared off-9-bar: **`0.512 / 0.356 / 0.530`**.

The first two branches are close, but the RC-3b differences are too large to dismiss as display rounding. This is a direct manuscript–bundle inconsistency. The values should be generated automatically from one frozen result object.

### 5.8 N-tube event sensitivity hidden by endpoint saturation

The final effective-channel count often saturates near its lower bound, but collapse/switching time does not:

| Sensitivity axis | Representative collapse-time change observed in current results |
|---|---|
| Tube count 100 → 800 | approximately **3.10 → 1.90 s** |
| Grind sweep | approximately **2.20 → 3.50 s** |
| Pressure sweep | approximately **1.90 → 2.40 s** |
| 16 stochastic seeds | approximately **1.40–3.50 s** |

Some stochastic runs end with approximately two effective channels rather than one. Endpoint invariance therefore does not imply trajectory or event invariance.

### 5.9 N-tube classification diagnostic

The current binary classifier can label a state “concentrates” when the top decile carries >90% of flow, even if no single tube dominates. In the lateral-regularization 0.1 case, the current result is approximately:

- `N_eff ≈ 19.1`;
- maximum single-tube share ≈ **0.068**; and
- top-decile share high enough to trigger “concentrates.”

That state is oligarchic or top-decile concentrated, not single-channel collapse. The paper’s terminology should follow the metrics it actually reports.

---

## 6. Detailed major comments

### B5-MAJ-01 — The reviewed paper is not represented by a clean released snapshot

The strongest reproducibility statement available to a reader should be: “this exact manuscript and these exact figures were produced from this exact code and data.” The repository cannot currently support that sentence. The raw manuscript, exact-commit snapshot, bundle source commit, and dirty-state metadata do not form one coherent artifact set.

**Why it matters:** A scientifically correct computation can still become unreviewable if values are copied across revisions. The LOPO mismatch documented below is an example of precisely that failure mode.

**Required action:** Make the strict build the only release path. Generate the manuscript tables and figures from a frozen result bundle, then record hashes for the full dependency graph.

### B5-MAJ-02 — Non-strict verification is not release verification

The build now has more checks than before and correctly offers a strict mode. However, a non-strict run can still report success when the bundle is dirty or stale. The claim checks also compare bundle fields with duplicated expected constants, which can agree even when both are detached from the current analysis.

**Required action:** In CI/release mode, prohibit non-strict verification. Check regenerated calculations against the committed bundle, then check manuscript-rendered fields against that bundle. A duplicated literal is not an independent check.

### B5-MAJ-03 — The manifest omits important dependencies and outputs

The expanded input hash list is an improvement, but it still does not fully bind:

- manuscript source;
- all analysis and plotting modules;
- environment/lock file;
- source-data exports;
- evidence dictionaries;
- raster and vector figures; and
- any cached slow-analysis intermediate used by plotting.

**Required action:** Treat the manifest as a directed artifact graph rather than a short input list. Each generated output should name every direct input and the code/environment identity used to create it.

### B5-MAJ-04 — The Jensen reference must use the evaluated mean after clipping

The draft’s formula at lines 204–206 assumes `E[K]=1`, but the evaluated distribution is clipped on a finite numerical support. The code already compensates by using the actual weighted mean. The manuscript is therefore behind the implementation.

**Required action:** Replace `EY(1)` with `EY(E[K_evaluated])`, report the mean shift, and state that clipping is small but not identically zero.

### B5-MAJ-05 — “Worst ≈ −1.4” is numerically reversed

For a deficit, the most negative value is the largest-magnitude deficit. The bundle contains gaps down to approximately −4.64 EY points. Approximately −1.38 is the **smallest-magnitude** deficit, not the worst.

**Required action:** Report the full range and define whether “worst” means most negative, closest to zero, or largest absolute value. Prefer unambiguous wording.

### B5-MAJ-06 — The Jensen argument establishes a numerical property of the implemented response, not channeling in the source experiment

The direct gap supports the statement that averaging the implemented concave response over the tested heterogeneity distribution reduces yield relative to its evaluated-mean reference. It does not show that the real puck has that distribution or that this is the cause of the observed response.

**Required action:** Keep the conclusion at model-capacity level and separate: (i) numerical concavity, (ii) closure calibration, and (iii) empirical evaluation.

### B5-MAJ-07 — The RSM result is reproducible but conditional on a selected model

The independent recomputation supports a conditional vertex near 1.743. The manuscript appropriately discloses model selection, but the abstract and figure can still be read as presenting a physical optimum. The seven-term form was retained after backward elimination, and selection is not repeated within the reported bootstrap.

**Required action:** Label the result “vertex of the selected response-surface approximation” everywhere. Add a model-form envelope or selection-aware sensitivity.

### B5-MAJ-08 — The primary RSM curve band should be heteroskedasticity-robust

A roughly 17-fold span in within-setting SD is not a minor technicality. A conventional residual bootstrap imposes exchangeability/homoskedasticity that the data visibly violate. The manuscript says wild bootstraps were run, but Figure 1 appears to retain the iid residual band.

**Required action:** Use an HC2/HC3-adjusted wild bootstrap for the plotted band, or show both bands with the conventional band explicitly labeled conditional.

### B5-MAJ-09 — The wild bootstrap should account for leverage

Multiplying raw residuals by Rademacher or Mammen variates without leverage adjustment can understate uncertainty in finite samples. Davidson and Flachaire discuss leverage-corrected residual treatments for heteroskedastic regression bootstrap.

**Required action:** Use HC2 or HC3 residual scaling and document the exact bootstrap algorithm, number of draws, invalid-fit handling, seed, and percentile/BCa rule.

### B5-MAJ-10 — The source-derived endpoint adds a first-stage uncertainty layer

The endpoint is not a direct whole-cup mass measurement. It is computed from a measured first fraction plus integration of fitted extraction kinetics to target beverage mass. The downstream RSM treats those values as known observations.

**Required action:** Propagate the first-stage kinetic-fit uncertainty if source-level information permits. Otherwise state prominently that all RSM standard errors and bootstraps are conditional on reconstructed cup masses.

### B5-MAJ-11 — Setting-level support and campaign-level generalization remain limited

Deletion diagnostics are reassuring for numerical stability, but 15 settings on one machine/coffee/campaign do not establish transfer. A cluster-robust sensitivity is wider than the conventional one, and a cluster-pairs stress bootstrap can be much wider.

**Required action:** State that deletion stability is not external validity. Avoid generalizing the vertex to grinders, machines, coffees, or pressure-control conditions not represented in the campaign.

### B5-MAJ-12 — Figure 1 overlays different estimands

The conditional RSM cross-section holds achieved flow and temperature at the center values, whereas the three displayed central-setting cell means arise under materially different achieved pressures and somewhat different flows. A reader may interpret curve and means as one matched conditional response.

**Required action:** Visually separate the conditional response-surface cross-section from the nominal-setting means, or covariate-adjust the displayed points. The caption should state the mismatch in one sentence rather than burying it in prose.

### B5-MAJ-13 — The two grind axes in Figure 1 are not commensurate

The Schmieder dial and Cameron/EK43 dial are grinder-specific, nonportable axes. Aligning vertical markers or similar numeric ranges can imply physical comparability that does not exist.

**Required action:** Use panel-specific axis labeling and explicitly state that dial values are not cross-grinder particle-size coordinates. A particle-size or hydraulic resistance axis would be preferable if available.

### B5-MAJ-14 — The calibrated streamtube comparison remains asymmetric

Static heterogeneity is calibrated to one grind-dependent deviation dataset, incomplete wetting is absent, Lee is tested under a modified ceiling, size exclusion targets inventory rather than the same endpoint response, and the diffusion branch is a null. Figure 2 documents this better than before, but “only implemented mechanism” remains an availability statement rather than comparative evidence.

**Required action:** Use “among the implemented and parameterized branches under these settings” consistently and make the asymmetry central to the Result 1 discussion.

### B5-MAJ-15 — Grid success frequency is not a robustness probability

The 10/25 successful closure combinations depend on a chosen rectangular grid and spacing. The draft does say this is descriptive, but the number is visually salient and can be read probabilistically.

**Required action:** Report the actual parameter ranges and rationale, show a continuous map if possible, and avoid “40% robust” or similar language. Add prominence relative to a pre-specified scientifically meaningful threshold.

### B5-MAJ-16 — The Result 1 bump may be too small to discriminate in available data

The full-grid median prominence is zero, and the successful-cell median is around 0.14 EY points, falling to about 0.03 at 9 bar. These are small relative to run-level variation and likely endpoint reconstruction uncertainty.

**Required action:** Add a detectability calculation or state that model capacity is demonstrated mathematically but the predicted bump is not resolved empirically at the current precision.

### B5-MAJ-17 — Figure 2 is improved but still uses internal ontology

Tokens such as `impl`, `qual-cap`, `n/e`, and validation-rung shorthand are project-management language. The categorical color scale also risks being read as ordinal even when categories are nominal and multidimensional.

**Required action:** Move the full matrix to a supplementary table with complete words, and use the figure only for a small number of reader-facing dimensions. Provide a grayscale-safe encoding and alt text.

### B5-MAJ-18 — Bibliographic certainty must replace “believed” identifiers

A publication figure/data dictionary cannot state that a DOI is “believed.” Lee et al.’s DOI can be verified as `10.1063/5.0138998`.

**Required action:** Validate every reference against the publisher or Crossref metadata and remove all provisional language before release.

### B5-MAJ-19 — Result 2 is an in-sample reconstruction exercise

The cubic is fitted and scored on the same 15–95 s interval. The empirical Φ(t) trajectory imports a TDS-derived donor path from the same rig/campaign and a campaign-calibrated equilibrium pair. Very low Durbin–Watson values reveal structured mismatch rather than independent noise.

**Required action:** Retain “reconstruction” throughout. Remove any suggestion that the 9-bar comparison is predictive validation or mechanism identification.

### B5-MAJ-20 — The current “moving-block bootstrap” is not a bootstrap of the fitted models

The routine resamples blocks of fixed pointwise losses after the predictions have been constructed. It does not account for uncertainty in the cubic coefficients, equilibrium fit, TDS sigmoid, digitization, or donor parameters.

**Required action:** Either refit within each block-resampled or subsampled series, or relabel the calculation precisely. The code, Methods, and caption must agree.

### B5-MAJ-21 — One block length is insufficient

An 8 s block contains about 80 raw samples, while the scored trace spans about 80 s. This leaves only roughly ten non-overlapping block lengths and may not capture slow nonstationary residual structure. With lag-1 correlation around 0.99, conclusions can be block-choice sensitive.

**Required action:** Show a block-length sensitivity (at least 4, 8, 16, and 24 s) and justify stationarity assumptions. A circular/stationary bootstrap is not automatically a cure if residual properties change through the shot.

### B5-MAJ-22 — A confidence interval crossing zero does not establish equivalence

The draft states that Φ(t) and the cubic are “statistically indistinguishable” because the conditional interval includes zero. Failure to reject a zero difference is not evidence that the effects are equivalent.

**Required action:** Say “the difference is not resolved by this analysis.” To claim equivalence, define an RMSE margin that is scientifically negligible and perform an appropriate two-one-sided/equivalence analysis.

### B5-MAJ-23 — The Φ-versus-cubic ordering is window-dependent

The result bundle shows Φ lower at 10–90 s, cubic lower at 15–95 s, and cubic much lower at 20–90 s. This is stronger than a minor sensitivity; it shows that the temporal ranking depends on which transient region is scored.

**Required action:** Display the window table in the manuscript or supplement and state that the flexible-null comparison is not stable to the evaluation window.

### B5-MAJ-24 — The residual structure should be shown, not merely summarized

A mean decimated Durbin–Watson near 0.01 is a load-bearing result. Readers should see whether errors are phase shifts, amplitude drifts, onset errors, or long sign runs.

**Required action:** Add residual-vs-time and ACF panels by branch. Consider integrated absolute error, timing error, and physically meaningful feature errors in addition to pointwise RMSE.

### B5-MAJ-25 — “Zero coefficients fitted to this flow trace” remains easy to misread

The phrase is technically narrower than “parameter-free,” but it can still imply a stronger degree-of-freedom advantage than warranted. The branch imports two equilibrium parameters, three TDS-sigmoid parameters, constitutive choices, initial conditions, and numerical preprocessing.

**Required action:** Use a complete parameter-provenance table in the main text or caption and replace compact labels such as `0 fit Q(t)` with an explicit sentence.

### B5-MAJ-26 — The sign test constrains an isolated branch, not the presence of swelling or fines

The manuscript now says this correctly in several places. Keep that scope. Primary swelling literature treats swelling as coupled to intra-grain and inter-grain transport and reports effects on both rate and beverage strength; a wrong sign for an isolated fixed-pressure resistance branch does not imply physical absence.

**Required action:** Ensure the abstract, captions, and conclusion preserve the same conditional wording as the detailed Result 2 section.

### B5-MAJ-27 — The transferred swelling magnitude is not general evidence

The reported throttling to about 4% and RMSE around 1.08 g/s come from one transferred powder parameterization. The sign may be structural under the branch assumptions; the magnitude is not.

**Required action:** Separate analytic sign conclusions from one-parameterization numerical illustrations in figure labels and prose.

### B5-MAJ-28 — The cross-pressure numbers must be regenerated from one source

The current bundle/manuscript RC-3b mismatch demonstrates that copied values are still being carried across revisions.

**Required action:** Eliminate manual numerical transcription. Figure annotations, prose, and tables should be rendered from the same JSON fields, with unit and rounding format specified once.

### B5-MAJ-29 — LOPO tests calibration influence, not full prediction independence

The held-out pressure is excluded from the two-parameter equilibrium refit, but the 9-bar solids trajectory and donor assumptions remain fixed from the same campaign. It is best described as a leave-one-pressure-out sensitivity of one calibration layer.

**Required action:** Replace “genuinely held-out trace” where it could imply full independence with “held out from the equilibrium-pair calibration.”

### B5-MAJ-30 — Pressure-level uncertainty and trace dependence are not propagated

Pressure-level RMSEs are treated as fixed summaries. Yet each trace contains serial dependence, digitization/measurement uncertainty, and shared donor parameters. The mean across 11 pressures is not accompanied by uncertainty at the pressure unit.

**Required action:** Add an uncertainty analysis whose resampling unit matches the pressure campaign and whose inner step respects within-trace dependence, or keep cross-pressure comparisons descriptive.

### B5-MAJ-31 — The residual-vs-pressure pattern is exploratory

A continuous pattern can arise from omitted machine dynamics, viscosity, sensor behavior, pressure-dependent donor mismatch, an imperfect equilibrium curve, or other bed mechanisms. The current paper appropriately avoids “regimes,” but branch-winner language remains tempting.

**Required action:** Present pressure trends as diagnostics of where each implemented branch fails, not as evidence for distinct physical regimes.

### B5-MAJ-32 — Figure 3 should expose uncertainty and residual dependence

The figure now includes LOPO points, a welcome improvement. It still combines several claims without intervals and does not visualize residual autocorrelation. Dense branch curves and compact labels make it difficult to distinguish calibration, reconstruction, and holdout roles.

**Required action:** Split main and supplementary panels. Keep one clear main result: constants fail to reconstruct the temporal shape, while a flexible temporal null prevents mechanism identification.

### B5-MAJ-33 — Figure 4 is a useful incompatibility diagnostic but not a mechanism test

The shared-porosity composition performs worse than a constant under one imported swelling parameterization. That result can diagnose incompatibility of the chosen composition and parameter transfer. It cannot determine whether the failure is due to control regime, initial state, swelling law, parameter transfer, missing coupling, or the shared-state composition itself.

**Required action:** Label Figure 4 as an ablation/incompatibility result. Add residuals and parameter provenance, and avoid implying a general rejection of swelling.

### B5-MAJ-34 — The N-tube “conservation” wording overstates construction-level checks

Under flow control, relative flows are normalized so their mean or sum meets the imposed control. Shares are normalized by definition. Checking these equalities to floating-point tolerance is useful software verification, but it is not a physical conservation law.

**Required action:** Rename this a “numerical invariant and non-negativity audit.” Add physical inventory and exchange balances before using “conservation” without qualification.

### B5-MAJ-35 — A finite extraction inventory is missing from the N-tube model

Each tube has an extraction-driven conductance clock, but the exploratory model does not close a per-tube solute/material balance that constrains how much extraction can occur.

**Required action:** Define tube inventory, extraction flux, and residual inventory. Report global and tube-wise balance errors and prevent unphysical extraction beyond available material.

### B5-MAJ-36 — The switching-convergence routine does not compute its documented trajectory metric

Its documentation promises the maximum full-trajectory difference in `N_eff(t)` relative to the finest run. The returned object does not contain that metric. It compares event times and final summaries only.

**Required action:** Implement the documented norm on a common interpolated time grid and add a regression test that fails if the field is absent or exceeds tolerance.

### B5-MAJ-37 — Event-time agreement may be output-grid quantization

Identical collapse times around 2.603 s across substep refinements can result from detecting first crossing only at stored outer timesteps. No event interpolation is used.

**Required action:** Locate crossing times by interpolation or solver event functions and refine the output grid independently of the internal step. Report both temporal discretization and event-detection error.

### B5-MAJ-38 — Explicit Euler refinement alone cannot establish solver independence

A stiff, near-choke, thresholded system can exhibit qualitatively similar switching under several Euler substeps while still being integrator-dependent.

**Required action:** Compare at least one higher-order explicit method and one adaptive or implicit method, with tolerances and positivity handling documented.

### B5-MAJ-39 — Spatial convergence is not established

The dedicated convergence routine uses a different tube count from the main Figure 5 baseline, and final-state saturation hides the observed collapse-time shift across `N=100…800`.

**Required action:** Perform a joint `N` and timestep convergence study for physical-time trajectories and event metrics at a common initial random field or convergent stochastic construction.

### B5-MAJ-40 — Endpoint invariance is not trajectory invariance

The draft acknowledges this at one point but then calls the concentration invariant across numerical, stochastic, and operating axes. Collapse time and transient recovery vary substantially.

**Required action:** Replace “invariant” with metric-specific statements: final concentration classification, event time range, peak/recovery behavior, and seed distribution.

### B5-MAJ-41 — The stochastic sample is small and internally inconsistent

The table states four seeds; the prose states 16 realizations. Sixteen runs are still too few to describe a 5–95% interval as a stable distribution without caveat: the nominal tail quantiles are essentially extreme order statistics.

**Required action:** Reconcile counts and increase the ensemble. Report all seed-level values and exact finite-sample quantiles or bootstrap uncertainty on summary statistics.

### B5-MAJ-42 — The binary “concentrates” classifier conflates single-channel and oligarchic states

A top-decile share can exceed 90% while no individual tube carries more than 7%. This is not the same physical state as `N_eff≈1` and top-1 share≈1.

**Required action:** Use a multi-class and persistence-aware classifier. Report top-1, top-5/top-decile, `N_eff`, entropy/Gini, and duration above thresholds.

### B5-MAJ-43 — The model exhibits collapse, rebound, and recollapse

Figure 5a is not a smooth one-way collapse. The trajectories show abrupt switching and recovery. Some runs are explicitly non-monotone in `N_eff`.

**Required action:** Discuss switching/chattering and define “collapse time” carefully. Consider first passage, sustained passage, and final-state metrics separately.

### B5-MAJ-44 — Donor extrapolation and porosity clipping need an audit

The trajectory interpolator permits extrapolation, while porosity is clipped at an upper bound. It is unclear how much of the simulation lies beyond donor support or pinned at the cap.

**Required action:** Export the fraction of tube-time outside donor support and at each clip boundary. Repeat the result with truncated horizon, constant terminal state, and another justified extrapolation law.

### B5-MAJ-45 — Lateral homogenization is a regularization proxy, not transverse physics

The algebraic blending parameter can suppress concentration, but it does not conserve and transport a physically defined lateral flux according to pressure gradients and geometry.

**Required action:** Keep the word “proxy” in every relevant claim. A physical conclusion requires a network/transverse-Darcy operator with its own balance and parameter provenance.

### B5-MAJ-46 — Fixed-flow and fixed-pressure controls are idealized extremes

Real espresso machines couple pump behavior, pressure regulation, headspace, compressibility, and bed resistance. Independent-tube fixed-pressure and globally normalized fixed-flow models bracket behavior but are not direct machine modes.

**Required action:** Present them as boundary-condition thought experiments. Avoid practitioner-facing claims until embedded in a coupled machine–bed model or tested experimentally.

### B5-MAJ-47 — The crossed design is not a comprehensive interaction study

The revised text correctly says OFAT plus a crossed control × lateral × closure design, not “full factorial.” Even so, interactions with timestep, tube count, initial heterogeneity, grind, pressure, and horizon remain untested.

**Required action:** Limit the robustness statement to tested combinations. Add interactions that are mechanistically plausible or state that they remain unknown.

### B5-MAJ-48 — Figure 5 communicates saturation better than convergence

Panel b shows final-state values at a lower bound. Panel a shows abrupt non-monotone switching. Panel d is overloaded with floor and gain information. The current figure makes the endpoint look more robust than the event dynamics are.

**Required action:** Center the main figure on physical-time trajectories, event-time convergence, and seed variation. Move floor sweeps and broad OFAT tables to supplementary material.

### B5-MAJ-49 — The manuscript still mixes scientific claims with project-management history

Lines 1–19, review identifiers throughout, “owed” statements, function names, Section 7, and the status/to-do section are not manuscript prose. They distract from the argument and reveal that Methods and reproducibility remain incomplete.

**Required action:** Remove all review-management scaffolding. Preserve the substance in a conventional Methods/Limitations structure and repository changelog.

### B5-MAJ-50 — The paper needs a sharper distinction among capacity, compatibility, validation, and identification

These concepts are often handled well locally, but the manuscript’s density makes slippage likely:

- **capacity:** a model can generate a qualitative feature;
- **compatibility:** a parameterized composition is not grossly inconsistent with a dataset;
- **validation:** performance on appropriately independent data under a predeclared protocol;
- **identification:** evidence localizes a mechanism/parameter sufficiently to distinguish alternatives.

**Required action:** Define these terms once in Methods and tag each result accordingly. The paper’s main contribution is strongest when it is framed as an evidence-calibration framework rather than a collection of partially comparable mechanisms.

---

## 7. Figure-by-figure review

### Figure 1 — Corrected endpoint target and static-heterogeneity model capacity

#### What works

- The figure now distinguishes raw/setting-level endpoint observations from the response-surface curve and includes uncertainty around the selected RSM.
- It exposes that the three nominal-setting means do not contain a middle-dial maximum.
- It shows that the static-heterogeneity branch can generate a small interior feature under a calibrated closure, which is an appropriate model-capacity result.
- The use of a separate model-capacity panel is preferable to overlaying mechanistic predictions directly on source points as though all axes and observables were identical.

#### Problems

1. **Conditional curve versus nonconditional points.** The achieved-predictor curve is evaluated at one fixed achieved flow/temperature pair. The central-setting means have different achieved pressure and somewhat different flow. Their visual proximity can be mistaken for a fitted conditional comparison.
2. **The plotted uncertainty appears to remain the conventional residual-bootstrap band.** The text emphasizes wild-bootstrap sensitivity, but the main visual should reflect the preferred robust uncertainty treatment.
3. **The source endpoint is reconstructed.** The figure/caption should say “source-derived cup endpoint” rather than allowing the reader to infer direct whole-cup measurement.
4. **The two grinder dials are not portable.** Schmieder and Cameron numeric dial positions should not be visually aligned as if a unit on one grinder corresponds to a unit on the other.
5. **Prominence is not placed on an empirical noise scale.** A bump of 0.03–0.14 EY points is difficult to interpret without run-level variability or a meaningful-effect threshold.
6. **The RSM curve is a selected-model summary.** A smooth band can visually overstate confidence in model form.

#### Required revisions

- Split the source-response and mechanism-capacity panels more clearly.
- Show the HC3-adjusted wild-bootstrap band, with the selected-form conditionality in the caption.
- Add a small inset or annotation showing the achieved covariates for the three nominal settings.
- Replace any shared/dashed vertical dial alignment across grinders with panel-specific markers.
- Report prominence relative to both run-level SD and a declared practically meaningful threshold.
- Export all points, conditional curve coordinates, and bootstrap quantiles as source data.

#### Suggested caption language

> **Figure 1. Source-derived TDS endpoint and model-capacity comparison.** Panel A shows run-level endpoint estimates for three selected nominal settings and the selected seven-term response-surface cross-section evaluated at the achieved flow and temperature of the nominal center setting. Because achieved pressure and flow differ across the displayed settings, the raw means are not observations from that fixed-covariate cross-section. The band is conditional on the selected response form and reconstructed cup endpoints. Panel B shows that the calibrated static-heterogeneity implementation can generate a small interior feature over part of the tested closure grid; this demonstrates capacity of the implementation, not identification of channeling in the source experiment. Grinder dial values are device-specific and are not cross-grinder particle-size coordinates.

### Figure 2 — Evidence and implementation matrix

#### What works

- The matrix is generated from committed data rather than being manually hard-coded.
- It forces the paper to disclose calibration/evaluation data, parameterization, observable, and missing experiment.
- It visually supports the manuscript’s core argument that the comparison is asymmetric.

#### Problems

1. **Too many dimensions are compressed into short tokens.** `impl`, `qual-cap`, `not-impl`, `n/e`, and validation rung labels require project-specific knowledge.
2. **Color suggests a single ordered strength scale.** Implementation status, evidence role, and observable match are not one ordinal variable.
3. **Text is crowded at normal manuscript size.** Several entries are clipped or difficult to scan.
4. **The dictionary contains provisional bibliographic language.** “Believed” DOI wording is unacceptable in a publication artifact.
5. **Parameter counts can be misread.** “Free” must distinguish fitted to the scored trace, fitted to another observable in the same campaign, imported literature parameters, and structural/numerical choices.

#### Required revisions

- Reduce the main figure to four or five reader-facing dimensions.
- Move the complete matrix and dictionary to a supplementary accessible table.
- Use distinct shapes/patterns for nominal categories rather than a sequential color ramp.
- Spell out every token and remove review-rung shorthand.
- Verify all DOI/source metadata.
- Include a column for experimental independence: same trace, same campaign, external campaign, simulated only.

#### Suggested caption language

> **Figure 2. Evidence-role matrix for the implemented comparison set.** Categories describe implementation and evidence roles rather than an ordinal quality score. “External” denotes a different campaign or publication; “same campaign” does not imply independent validation. Parameter counts distinguish coefficients estimated from the scored observable, coefficients estimated from another observable in the same campaign, literature/donor parameters, and fixed structural choices. Full definitions and source records are provided in Supplementary Table S1.

### Figure 3 — Temporal model ladder and cross-pressure reconstruction

#### What works

- Panel A usefully demonstrates that a dip-and-recovery shape is not unique to bed dynamics within the tested machine model.
- Panel B includes a flexible cubic null, preventing the empirical Φ(t) branch from being overinterpreted as uniquely mechanistic.
- Panel C now shows LOPO points in addition to shared-calibration curves.
- Panel D appropriately frames swelling as a sign/magnitude illustration under one transferred parameterization.

#### Problems

1. **Panel A is a model reconstruction, not an observed mechanistic decomposition.** The title/caption should make that explicit.
2. **Panel B omits residuals and the block-resampling interval.** The most important qualification—coherent serial error—is invisible.
3. **The compact label “0 fit Q(t)” is still opaque.** It does not reveal imported donor/campaign parameters.
4. **The manuscript values disagree with the current bundle/figure for RC-3b.** This must be fixed before interpretation.
5. **Panel C is crowded.** Six shared/held-out branch traces or marker sets can obscure pressure-specific differences.
6. **No uncertainty is shown at pressure level.** LOPO point estimates are visually definitive despite shared donor uncertainty and serially dependent traces.
7. **Panel D’s numerical magnitude is parameterization-specific.** The visual can make it look like a general swelling prediction.
8. **The figure does not show the window sensitivity that changes Φ-versus-cubic ordering.**

#### Required revisions

- Add a residual/ACF supplemental panel and refer to it in the main figure.
- Replace compact parameter-count labels with a caption table or full phrase.
- Generate all Figure 3 annotations from the current result bundle.
- Plot pressure-level differences relative to a declared reference, or split shared and LOPO summaries into separate panels.
- Add a small table/inset for 10–90, 15–95, and 20–90 s scores.
- Add uncertainty or state prominently that the pressure-level curves are descriptive point estimates.
- Label the swelling curve “one transferred powder parameterization.”

#### Suggested caption language

> **Figure 3. Null-first temporal reconstruction and pressure-level calibration sensitivity.** Constant branches have substantially larger in-window RMSE than time-varying branches on the selected 9-bar trace. The empirical Φ(t) branch estimates no coefficients from the scored flow trace but imports equilibrium and TDS-trajectory parameters from the same campaign; the cubic is fit and scored on the same window and serves only as an in-sample flexibility bound. Residuals are strongly serially dependent, and branch ordering between Φ(t) and the cubic changes with the scoring window. The pressure panel holds the donor trajectory fixed and leaves each pressure out only from the two-parameter equilibrium calibration; it is not independent validation of the physical pressure pattern.

### Figure 4 — Shared-porosity composition diagnostic

#### What works

- The figure reports a failed composition rather than hiding it.
- It narrows the result to one imported parameterization and one composition rule.
- It supports the paper’s methodological message that individually plausible components need not compose successfully.

#### Problems

1. **The ablation structure is incomplete.** Readers need extraction-only, swelling-only where defined, and combined branches to see which term causes the flattening.
2. **No residual panel or uncertainty is shown.** The quoted RMSE difference is not visually connected to time-local error.
3. **Parameter provenance is not visible.** The viewer cannot distinguish coefficients calibrated to this campaign from imported powder parameters.
4. **The figure cannot identify the source of incompatibility.** Shared porosity, control law, initial condition, swelling magnitude, and donor transfer are confounded.

#### Required revisions

- Add explicit component ablations and residual-vs-time.
- Include a compact parameter-provenance key.
- State in the title/caption that the result is an incompatibility of one parameterized composition, not a test of swelling in general.
- Consider moving this figure to a mechanistic-ablation supplement unless the composition failure is made a central methodological result.

#### Suggested caption language

> **Figure 4. Ablation of one shared-porosity composition.** Under the tested control law, initial condition, and imported swelling parameterization, adding the swelling branch to the extraction-linked porosity trajectory worsens reconstruction relative to extraction-only and to the best constant. This establishes incompatibility of this parameterized composition; it does not determine whether the discrepancy arises from the swelling law, parameter transfer, initial state, boundary condition, or the shared-porosity composition itself.

### Figure 5 — Exploratory N-tube dynamics

#### What works

- The figure clearly labels the result exploratory.
- It discloses the singular/floor-dependent gain and the idealized control/lateral assumptions.
- It includes more numerical and design sensitivities than the preceding version.
- Physical time is preferable to normalized shot time for the switching trajectory.

#### Problems

1. **Panel A shows abrupt collapse, rebound, and recollapse, not a simply converged monotone event.**
2. **Panel B mainly shows endpoint saturation.** It does not establish trajectory, collapse-time, or spatial convergence.
3. **Tube count and timestep are combined despite answering different numerical questions.**
4. **The event time is output-grid quantized and no higher-order solver is shown.**
5. **Panel C’s classification hides the difference between single-channel and top-decile concentration.**
6. **Panel D is overloaded.** Dual axes/log scales and floor-dependent analytic gain are difficult to interpret alongside simulation endpoints.
7. **Seed variability is not visualized adequately.** A median and 5–95% interval from 16 runs can conceal multi-channel endpoints and wide event-time variation.
8. **No physical balance or finite inventory is shown.**
9. **The lateral term is a regularizer, not a physical exchange flux.**
10. **The main configuration (`N=400`) and dedicated convergence configuration (`N=200`) are not fully aligned.**

#### Required revisions

A stronger Figure 5 would contain:

- **Panel A:** `N_eff`, top-1 share, and entropy versus physical time for the reference run, with first-passage and sustained-collapse definitions.
- **Panel B:** temporal-convergence plot of event time and trajectory norm versus timestep for Euler and a higher-order/adaptive solver.
- **Panel C:** spatial convergence/event-time versus `N`, using a controlled initial random field.
- **Panel D:** seed-level distribution of collapse time, final top-1 share, and final `N_eff` over a substantially larger ensemble.

Move the floor sweep, OFAT operating sweeps, and crossed control/lateral/closure table to supplementary figures. Report numerical invariants and physical balances in a separate table.

#### Suggested caption language

> **Figure 5. Exploratory finite-time concentration in an idealized streamtube composition.** The reference configuration uses an imposed total-flow normalization, a near-choke conductance law, no physical transverse exchange, and an extraction-linked donor trajectory. The simulation can exhibit abrupt concentration, recovery, and switching. Final-state concentration is robust over some tested numerical settings, but event timing and transient trajectories vary with tube count, operating inputs, and realization. Numerical normalization checks do not constitute a physical mass or energy conservation law. The result is a model-failure diagnostic and motivation for a physical lateral-network formulation, not evidence that real pucks collapse to one channel.

---

## 8. Section-by-section manuscript review

### Title

The revised title—“Limits of mechanism discrimination from integrated espresso measurements”—is substantially better than a mechanism-forward or stability-forward title. It accurately foregrounds the methodological contribution. The subtitle is still dense. “Matched observables, temporal nulls, and exploratory streamtube dynamics” is defensible, but the paper may read more coherently if the streamtube result is moved to an explicitly exploratory appendix.

**Action:** Retain the emphasis on limits; consider a shorter subtitle such as “Matched observables and null-first model comparison.”

### Front-matter review note (lines 1–19)

This entire block is internal review scaffolding. It includes correction history, roadmap references, verb discipline, and a discussion of unavailable title options.

**Action:** Delete it from the manuscript. Put revision history in the repository changelog and submission cover letter.

### Abstract

The abstract has improved in three important ways: it calls the endpoint source-derived, frames the heterogeneity result as capacity, and explicitly says the N-tube result is exploratory. Remaining issues:

- it states that the floor sweep is “completed” without disclosing that trajectory convergence remains incomplete;
- it compresses multiple kinds of evidence into one dense paragraph;
- it does not disclose that the temporal block interval is conditional on fixed fitted losses;
- it may overstate “flow concentrates strongly” given seed/state and classifier issues; and
- it mentions a “continuous residual-vs-pressure curve” without saying that manuscript and bundle values are currently inconsistent.

**Action:** Rewrite after reruns. A proposed abstract appears in Section 12.

### Introduction

The introduction clearly distinguishes three objects and flags grinder-dial and pressure confounds. The research questions are appropriate. However:

- statements about the homogeneous-model lineage need direct citations;
- the novelty disclaimer is internal project language;
- the paper’s methodological contribution should be stated positively, not only through “what prior discussion conflated”; and
- the relationship between Paper A and Paper B should be described as a conventional companion-methods context, not repository workflow.

**Action:** Add a concise related-work synthesis and define the evidence-calibration framework.

### Methods

The current Methods section is explicitly incomplete. A registry description and data-contract principle are not substitutes for equations, estimands, calibration splits, uncertainty methods, and numerical algorithms.

A submission-ready Methods should include at minimum:

1. **Datasets and provenance:** machine, coffee, experimental unit, sampling, measured versus derived observables, digitization, license.
2. **Observable matching:** units, normalization, endpoint construction, conditioning variables, exclusion criteria.
3. **RSM:** exact design matrix, achieved predictors, retained/full model forms, center cross-section, vertex calculation, covariance and bootstrap algorithms, deletion/CV definitions.
4. **Static heterogeneity:** distribution, quadrature, clipping, homogeneous reference, closure calibration, support grid, prominence definition.
5. **Temporal ladder:** equations for every branch, parameter source, initial state, scoring windows, residual metrics, digitization/preprocessing.
6. **Dependence analysis:** residual sampling rate, decimation, block routine, block lengths, resampling target, interval construction.
7. **Cross-pressure analysis:** exact held-out unit, refitted versus fixed quantities, pressure-level aggregation, uncertainty.
8. **N-tube model:** governing ODE/update equations, control laws, conductance closure, floor, donor interpolation, lateral term, integrator, event definitions, invariants, physical balances, stochastic initialization.
9. **Reproducibility:** software version, environment lock, seeds, hardware if relevant, build command, artifact manifest.

**Action:** Replace function names as Methods with equations and algorithms. Function names may appear in a code-availability appendix.

### Result 1

The empirical-target section is careful and mostly defensible. The strongest claim should remain: the three selected nominal-setting means do not show a middle-dial maximum, while a selected RSM has a conditional vertex near 1.74. These are not contradictory because they condition on different covariates/estimands.

Corrections required before submission:

- fix Jensen mathematics and range;
- make robust RSM uncertainty primary;
- propagate or disclose first-stage endpoint uncertainty;
- sharpen the asymmetry of model capacity comparisons;
- add detectability/effect-size context; and
- remove all review IDs and repository-specific terms.

### Result 2

The null-first logic is the strongest conceptual part of the paper. The data show that constant branches reconstruct the selected trace much worse than time-varying curves. The cubic prevents the empirical Φ(t) branch from being overclaimed as unique. The section becomes unreliable where it converts a conditional block-loss interval into “statistical indistinguishability.”

Corrections required:

- refit in dependence-preserving resamples or relabel the interval;
- add block/window sensitivity;
- show residual structure;
- regenerate cross-pressure numbers;
- state the precise holdout layer;
- keep the swelling/fines sign claim conditional; and
- avoid parameter-count shorthand.

### Result 3

The revised caveats are appropriate, but the section still outruns the implementation. It calls switching converged without computing a trajectory norm or independent solver comparison, calls axes invariant despite large event-time shifts, and conflates top-decile concentration with single-channel collapse.

**Action:** Either complete the numerical/physical validation program or move Result 3 to an exploratory appendix with a narrower conclusion:

> The implemented idealized composition exhibits strong, assumption-dependent concentration and switching, motivating a physical network model; no stability, convergence, or real-puck claim is made.

### Discussion

The discussion’s measurement-design table is valuable. It converts negative identifiability findings into concrete experimental recommendations. It should be retained and expanded to include:

- which parameter/mechanism each proposed measurement would distinguish;
- expected direction/timing of the competing hypotheses;
- required temporal/spatial resolution; and
- whether the proposed observable is technically feasible.

The discussion should also separate three limitations:

1. limitations of the **data** (integrated, same campaign, reconstructed endpoints);
2. limitations of the **implemented model set** (missing wetting/lateral physics, asymmetric calibration); and
3. limitations of the **analysis** (selection, serial dependence, dirty release, numerical convergence).

### Open gaps and status/to-do sections

These sections should not appear in the manuscript body. Their content is useful for project management but currently confirms that critical Methods, novelty, physical lateral exchange, and release work remain undone.

**Action:** Move all unresolved tasks to the repository roadmap. Convert scientifically relevant limitations into a concise Discussion subsection. Do not submit a paper that explicitly says its conventional Methods are “still owed.”

---

## 9. Code, data, and reproducibility audit

### 9.1 Claim-to-code traceability table

| Manuscript claim | Current implementation/evidence | Review finding |
|---|---|---|
| Three selected endpoint means are ordered and do not show a middle-dial maximum | Run-level central-setting extraction-yield calculation | Supported as a descriptive same-campaign comparison; causal grind interpretation remains confounded by achieved conditions. |
| Selected achieved-predictor RSM has a vertex near 1.74 | Seven-term linear model and algebraic vertex | Reproducible; interval is conditional on selected model and reconstructed endpoints. |
| Wild bootstrap shows heteroskedasticity sensitivity | Rademacher/Mammen residual multiplication | Directionally useful, but leverage adjustment and exact plotted-band contract need clarification. |
| Static heterogeneity produces a negative direct Jensen gap | Quadrature over clipped numerical support | Qualitative sign supported; manuscript formula/reference and gap range are wrong. |
| Evidence matrix is data-driven | CSVs plus dictionary to plotting path | Major improvement; ontology and bibliography still need publication cleanup. |
| Φ(t) beats constants under serial dependence | Fixed-loss block resampling | Supports a conditional descriptive loss contrast; not a full model-fitting bootstrap. |
| Φ(t) and cubic are statistically indistinguishable | Conditional interval includes zero | Not established; absence of resolved difference is not equivalence. |
| LOPO held-out summaries | Refit equilibrium pair leaving one pressure out | Appropriate limited calibration-influence check; manuscript RC-3b values stale. |
| Residuals are strongly serially dependent | Decimated residual diagnostics | Supported and important; should be visualized. |
| Isolated swelling/fines resistance branches have wrong sign at fixed pressure | Transferred swelling run plus analytic fines result | Supported only under branch assumptions; magnitude not general. |
| Full-trajectory N-tube numerical audit | Per-substep extrema recorded | Improved; chiefly verifies imposed normalization/non-negativity, not physical conservation. |
| Switching is timestep-converged | Euler substep comparison and output-grid event time | Not established; no trajectory norm, event interpolation, or independent solver. |
| Endpoint invariant across N/timestep/operating axes | Final `N_eff` classification | Final saturation often supported; event time and trajectory are not invariant. |
| 16-realization distribution is tight | Small seed ensemble | Overstated; table says four, event time varies widely, and some endpoints are multi-channel. |
| Lateral regularization suppresses concentration | Algebraic blend sweep | Supported as regularization sensitivity, not physical transverse exchange. |

### 9.2 Data contract defects

The malformed 36 rows in the Schmieder-derived CSV should be treated as a release-blocking data-engineering defect even though current filters omit them. Recommended schema:

**Run-level table**

- `experiment_id`
- `replicate_id`
- `component`
- `brew_ratio`
- `target_grind`
- `target_flow`
- `achieved_flow`
- `target_temperature`
- `achieved_temperature`
- `pressure_summary`
- `cup_mass_derived`
- `cup_concentration_derived`
- units and provenance fields

**Design/summary table**

- one row per setting;
- nominal and achieved-setting summaries;
- replication count;
- source table/figure identifier; and
- any scale/normalization metadata.

Tests should enforce:

- uniqueness of `(experiment_id, replicate_id, component, brew_ratio)` in the run table;
- no null primary predictors/outcomes for `row_type=run`;
- expected unit set by component;
- exactly 48 complete TDS/BR-1/2 run rows for the current extraction;
- exactly 15 setting IDs and the documented center replication;
- no summary record in an experimental table; and
- explicit failure rather than silent filtering.

### 9.3 Result-bundle design

A robust bundle should contain, for every analysis:

- semantic analysis version;
- source commit and dirty flag;
- input hashes;
- code-module hashes;
- environment lock hash;
- random seed(s);
- parameter definitions and units;
- full-precision point estimates;
- uncertainty method and full interval values;
- exclusion/invalid-fit counts;
- diagnostics;
- source-data coordinates for every plotted panel; and
- a claim identifier mapping bundle fields to manuscript sentences/tables.

The manuscript should never contain a number that is not either generated from or checked against a bundle field.

### 9.4 Figure-generation contract

Current plotting paths still risk recomputing fits independently of the frozen bundle. This creates three failure modes:

1. a figure reflects newer code while prose reflects an older bundle;
2. a random bootstrap band changes without a recorded seed/result object; and
3. duplicated calculations drift in centering, filtering, or rounding.

**Required design:**

```text
raw/curated data + pinned code + environment
                    ↓
             compute_results
                    ↓
       immutable versioned results.json
          ↙          ↓           ↘
     figures     source-data     manuscript tables
                    ↓
               strict manifest
```

Plotting should be a pure transformation of frozen numerical/source-data objects.

### 9.5 Precision and rounding

The draft now says several means are computed from unrounded values, which is correct practice. The current manuscript–bundle mismatch shows that precision is not the only problem; revision synchronization is. Recommended policy:

- store full precision in bundle/source data;
- round only at rendering;
- define display precision by metric once;
- generate prose/table strings programmatically;
- prohibit averages of display-rounded values; and
- include regression tests for every headline value and table row.

### 9.6 Statistical terminology tests

Add text-level tests or editorial checks that flag:

- “statistically indistinguishable” without an equivalence margin;
- “parameter-free” or “zero-parameter” when donor parameters exist;
- “validation” for same-campaign reconstruction;
- “conservation” when only normalized shares are checked;
- “converged” without a declared norm/tolerance/reference;
- “invariant” without naming the metric and tested domain;
- “mechanism” where only model capacity is demonstrated; and
- “independent” where a donor trajectory or campaign calibration is shared.

---

## 10. Required numerical reruns and pass/fail criteria

### Rerun 1 — Clean release regeneration

**Procedure:** From a fresh environment, check out the release tag, install from the lock file, regenerate all Paper B results, source data, figures, and manuscript tables, then compare hashes.

**Pass:** zero untracked changes; `git_dirty=false`; all generated hashes match the manifest; the bundle source commit equals the release commit.

### Rerun 2 — RSM robust curve uncertainty

**Procedure:** Recompute the achieved-predictor RSM with conventional, HC2/HC3 wild, and setting-cluster sensitivities. Plot curve-level bands, not only vertex intervals.

**Pass:** the preferred band is identified a priori; algorithms and invalid-fit handling are documented; Figure 1 and prose use the same result object.

### Rerun 3 — RSM model-form/post-selection sensitivity

**Procedure:** Compare the retained seven-term form, a pre-specified full quadratic, and selection repeated within resamples. Record vertex distributions, concavity/in-domain fractions, and prediction bands.

**Pass:** the main claim is stable or narrowed explicitly; no selected-form interval is presented as unconditional.

### Rerun 4 — Two-stage endpoint uncertainty

**Procedure:** Where source information allows, resample or propagate uncertainty from fraction-level kinetic fits into derived cup masses, then refit the RSM.

**Pass:** total uncertainty is reported; if impossible, the manuscript explicitly states that endpoint reconstruction uncertainty is unavailable and omitted.

### Rerun 5 — Source-data schema repair

**Procedure:** Rebuild the Schmieder-derived tables from source with separate run/design schemas and validation.

**Pass:** no malformed run rows; exact expected counts; primary-key and unit tests pass; analysis does not rely on silent NA filtering.

### Rerun 6 — Corrected Jensen audit

**Procedure:** For every grind/pressure cell, report quadrature support, clipping mass, `E[K_eval]`, `E[EY(K_eval)]`, `EY(E[K_eval])`, direct gap, curvature fraction, and grid refinement.

**Pass:** all manuscript numbers and Figure/source data agree; gap range is correctly ordered; conclusions are unchanged under support/grid refinement.

### Rerun 7 — Dependence-preserving Result 2 comparison

**Procedure:** Choose a defensible resampling/validation target. For a bootstrap, reconstruct and refit relevant branches within each block-resampled series; for a predictive analysis, use blocked/prequential holdout. Test multiple block lengths.

**Pass:** Methods state exactly what is resampled and refitted; intervals/holdouts are stable enough for the wording used; no equivalence claim is based solely on a nonsignificant difference.

### Rerun 8 — Temporal-window and metric sensitivity

**Procedure:** Evaluate all branches on 10–90, 15–95, and 20–90 s plus justified alternatives. Report RMSE, MAE, integrated absolute error, onset/timing errors, and residual structure.

**Pass:** the main claim is phrased to hold across declared windows/metrics, or dependence is shown transparently.

### Rerun 9 — Cross-pressure regeneration

**Procedure:** Recompute shared-all, shared-off-9, and LOPO-held-out values from one code path with full precision.

**Pass:** JSON, manuscript, figure, source data, and tests agree exactly before display rounding.

### Rerun 10 — Cross-pressure uncertainty

**Procedure:** Propagate equilibrium-fit uncertainty and within-trace dependence; report pressure-level intervals or maintain descriptive language.

**Pass:** any inferential language has a defined sampling unit and dependence-aware method.

### Rerun 11 — N-tube temporal convergence

**Procedure:** Run multiple output steps and internal steps with explicit Euler, RK4, and an adaptive solver. Interpolate all trajectories to a common physical-time grid. Compute sup and L2 norms for `N_eff`, top-1 share, entropy, total raw flow, and state variables.

**Pass:** declared convergence tolerance is met for trajectories and event times, not just final state; solver/event handling is documented.

### Rerun 12 — N-tube spatial convergence

**Procedure:** Use nested or spectrally consistent initial random fields for increasing `N`; compare aggregate trajectories and event metrics.

**Pass:** spatial error decreases or the result is explicitly described as finite-network behavior; final saturation alone is not accepted as convergence.

### Rerun 13 — N-tube stochastic ensemble

**Procedure:** Run at least 100 independent realizations for the reference and key regularized configurations; report seed-level collapse/sustained-collapse times, final `N_eff`, top-1 share, entropy/Gini, and failure/non-collapse fraction.

**Pass:** manuscript reports distributions with finite-sample uncertainty and does not call a four- or 16-run sample “tight” without qualification.

### Rerun 14 — N-tube start-state and horizon sensitivity

**Procedure:** Vary initial heterogeneity amplitude/distribution, donor start time, and simulation horizon.

**Pass:** the result’s dependence on start state and horizon is quantified; transient collapse/recovery is distinguished from persistent concentration.

### Rerun 15 — Donor-support and clipping audit

**Procedure:** Count tube-time outside donor support and at porosity/conductance floors/caps; repeat with alternative terminal extrapolations.

**Pass:** concentration classification and event metrics are not driven by extrapolation/clipping, or the claim is narrowed accordingly.

### Rerun 16 — Physical balance audit

**Procedure:** Add per-tube and global finite inventory, extraction flux, lateral flux where present, and pressure/flow consistency. Track cumulative balance residuals.

**Pass:** physical balances close within a declared tolerance throughout the trajectory; construction-level share normalization is reported separately.

### Rerun 17 — Physical lateral-network sensitivity

**Procedure:** Replace algebraic homogenization with a mass-conserving pressure-driven exchange network and test grid/network refinement.

**Pass:** any claim about lateral coupling is based on a physical operator with parameter provenance; otherwise the current result remains a regularization study only.

### Rerun 18 — Full paper artifact consistency

**Procedure:** Parse every headline number, table cell, and figure annotation from the rendered manuscript and compare with the bundle/source data.

**Pass:** zero mismatches. The check includes the RC-3b LOPO/shared/off-9 values, RSM diagnostics, seed count, N-tube event metrics, Jensen range, and figure captions.

---

## 11. Suggested replacement wording for high-risk claims

### 11.1 Jensen gap

**Current-risk formulation:**

> The multipliers are unit-mean, so `E[K]=1`, and the worst gap is approximately −1.4 yield-points.

**Suggested replacement:**

> Because quadrature support is clipped, the evaluated weighted-mean multiplier differs slightly from one in some cells. We therefore compare the ensemble yield with the homogeneous yield at the evaluated mean multiplier, `J = E[EY(K_eval)] − EY(E[K_eval])`. Across the tested cells, `E[K_eval]` ranges from approximately 0.995 to 1.000 and every direct gap is negative, approximately −4.64 to −1.38 extraction-yield points. This establishes the sign of the Jensen-type deficit for the implemented numerical response and support; it does not identify heterogeneity as the cause of the source response.

### 11.2 RSM vertex

**Suggested replacement:**

> The selected seven-term achieved-predictor response surface has a conditional grind vertex near dial 1.74. Deletion and heteroskedasticity sensitivities preserve a vertex in this vicinity. The interval conditions on the selected response form, reconstructed cup endpoints, and one campaign; it is not a confidence interval for a universal physical optimum.

### 11.3 Block analysis

**If the current code is retained:**

> We resampled contiguous blocks from the already-computed squared-loss sequences to assess how serial dependence affects the descriptive RMSE difference, conditional on the fitted predictions. This procedure does not refit either model and is not a bootstrap confidence interval for the complete model-fitting process.

**If refitting is implemented:**

> We used a dependence-preserving block resampling procedure in which all coefficients estimated from the scored trace were refit within each resample. Results are reported across a predeclared range of block lengths; imported donor parameters remain fixed, so the interval is conditional on those inputs.

### 11.4 Φ(t) versus cubic

**Current-risk formulation:**

> The two are statistically indistinguishable on this trace.

**Suggested replacement:**

> The conditional RMSE-difference interval includes zero, so this analysis does not resolve a difference between the two branches. This is not evidence of equivalence, and their ordering changes with the scoring window. The flexible null therefore prevents identification of the empirical Φ(t) trajectory as a unique mechanism.

### 11.5 LOPO scope

**Suggested replacement:**

> Leaving one pressure out of the two-parameter equilibrium calibration changes the fitted pair by at most approximately 2.8%, and the pressure-averaged held-out reconstruction scores are close to the shared-calibration scores. This indicates that the equilibrium-pair fit is not dominated by a single pressure. The 9-bar donor trajectory and other campaign assumptions remain fixed, so the analysis is not independent validation of the physical residual-vs-pressure pattern.

### 11.6 Swelling/fines sign claim

**Suggested replacement:**

> Under the imposed fixed-pressure boundary condition and when represented as isolated resistance-increasing branches, the tested swelling parameterization and the cited fines-migration model cannot by themselves supply a rising-flow contribution. This conditional sign constraint does not imply that swelling or fines are absent from a coupled bed in which dissolution, saturation, compaction, viscosity, gas, erosion, and machine response evolve simultaneously.

### 11.7 N-tube result before convergence work

**Suggested replacement:**

> In the implemented finite-network construction, an imposed total-flow normalization, near-choke conductance law, and weak algebraic homogenization can produce strong, non-monotone concentration and switching. Final concentration classifications persist over several tested settings, while event timing varies with tube count, operating inputs, and stochastic realization. Because trajectory convergence, a physical lateral operator, finite material balance, and formal stability analysis are not yet established, this is an exploratory model-failure diagnostic rather than evidence for a real-puck instability.

### 11.8 Numerical audit

**Suggested replacement:**

> At every stored/internal step, the implementation satisfies its imposed share normalization and control-law normalization to numerical tolerance and keeps the audited state variables nonnegative. These are software/numerical invariants. They do not establish physical conservation of solute inventory, pressure work, or transverse flux, which are not closed in the current exploratory model.

---

## 12. Possible revised abstract after the required corrections

> Integrated espresso measurements can be reproduced by distinct combinations of extraction, flow, and bed-state dynamics, limiting mechanism discrimination. We apply matched-observable and null-first comparisons to two published campaigns and an explicitly defined set of model implementations. For a fraction-resolved campaign, three selected nominal-setting, source-derived TDS endpoints are numerically ordered across grinder dial and do not exhibit a middle-dial maximum. A selected achieved-predictor response surface has a conditional interior vertex near dial 1.74, but that result depends on model form, reconstructed endpoints, and one campaign. A calibrated static-heterogeneity implementation can generate a small interior feature over part of its tested closure domain, demonstrating model capacity rather than identifying channeling. For a rising-flow trace, constant branches reconstruct the selected window substantially worse than time-varying branches; however, a flexible non-mechanistic time curve performs comparably to an empirical porosity trajectory and branch ordering depends on the scoring window. Leave-one-pressure-out refits show that a two-parameter equilibrium calibration is not dominated by one pressure, but residuals remain strongly structured and donor assumptions are shared within the campaign. An exploratory streamtube composition can exhibit strong, assumption-dependent concentration and switching under an imposed total-flow normalization and weak regularization, but it is not yet a converged physical stability model. Across the tested datasets and model set, integrated signals constrain model capacity and incompatibility more strongly than they identify mechanism. Measurements of first-drip timing, bed state, and pathway-resolved flow are likely to be more discriminating.

This abstract intentionally avoids numerical confidence claims until the RSM, block, LOPO, and N-tube analyses are regenerated from a clean release.

---

## 13. Editorial, clarity, and consistency comments

These are secondary to the major scientific and reproducibility actions above, but completing them will make the manuscript substantially easier to review.

1. Replace “Paper B — draft prose” with the actual manuscript title and author list.
2. Delete the revision date and “post detailed review” wording from the title line.
3. Remove the front-matter verb-discipline instructions; retain the disciplined verbs in the prose itself.
4. Remove parenthetical explanations of how the title changed during review.
5. Define extraction yield (`EY`) at first use, with units and normalization.
6. Define TDS and explain whether it is mass fraction, percentage, or concentration in every dataset.
7. Distinguish “cup mass,” “solute mass,” “TDS-derived extraction yield,” and “beverage mass” consistently.
8. Replace “source-derived run-level endpoint estimate” with a shorter defined term after its first full explanation.
9. Use “grinder setting” or “dial setting” consistently; avoid alternating among “grind,” “grinder dial,” and `gs` without definition.
10. State explicitly that the Sauter-diameter ordering is nonmonotonic in dial and provide the source/covariance if available.
11. Avoid “fine,” “middle,” and “coarse” where the particle-size ordering is ambiguous; use the actual dial and measured size.
12. Give achieved pressure uncertainty/range, not only means, for the three central settings.
13. Clarify whether Welch intervals use raw run values and whether any source-level repeated structure remains.
14. Report exact sample sizes directly in Figure 1 or its caption.
15. Use consistent typography for `R²`, adjusted `R²`, `Q²`, and condition numbers.
16. Define the exact retained seven RSM terms in the Methods rather than referring to a function.
17. State how the RSM vertex is handled when curvature is nonconcave or the vertex lies outside the design domain.
18. Report bootstrap draw counts, random seeds, interval type, and invalid-fit counts in a table.
19. Replace “99.8% of fits are concave-and-in-domain” with separate percentages for concavity and in-domain status if they differ.
20. Explain why AICc is used and how sample size is counted for the selected versus full quadratic.
21. Avoid presenting the uncentered design condition number as evidence of physical ill-conditioning; it is largely a scaling diagnostic.
22. Define the tested support used for the curvature fraction and clipping audit.
23. State the quadrature order and convergence test for the lognormal expectation.
24. Define “prominence” mathematically, including endpoint and tie handling.
25. State the closure-grid ranges and whether spacing is linear/logarithmic.
26. Avoid “real and grid-converged” for a modeled interior maximum; use “present in the evaluated implementation and numerically stable to the tested grid refinement.”
27. Replace “external target” for Schmieder where the calibration/evaluation relationship is indirect and asymmetric; define the exact independence level.
28. In Figure 2, avoid coloring “not implemented” as though it were low evidence for an implemented branch.
29. Define every validation rung in publication language or remove rung numbers.
30. In Result 2, state the native and decimated sampling rates and the anti-aliasing/aggregation method.
31. Explain why 15–95 s is the primary window and whether it was selected before inspecting branch performance.
32. State whether the cubic uses raw time, centered/scaled time, or an orthogonal polynomial basis.
33. Report cubic coefficient uncertainty only if it serves a scientific purpose; otherwise emphasize its role as a flexibility bound.
34. Distinguish “fit to another observable in the same campaign” from “literature fixed” in all parameter-count tables.
35. Define `P_c` and `Q_c` physically and give their units.
36. Define RC-3b in reader-facing language before using the code label.
37. Avoid “rung 5b” and similar internal labels in the manuscript body.
38. Replace “representative illy powder” with exact source material and parameter provenance.
39. Cite the exact theorem/lemma and assumptions for the fines-migration sign statement in a conventional reference format.
40. State whether pressure traces share preprocessing, digitization, and time alignment.
41. Do not use “genuinely held-out” without specifying “held out from which fitting operation.”
42. Report pressure-level sample count (`n=11`) next to the LOPO average.
43. Clarify whether 9 bar itself is included in each all-pressure average and excluded only in the off-9 summary.
44. Use one display precision for all RMSEs; three decimals is reasonable if supported by measurement precision.
45. Replace “the 14× flow rise the ladder requires” with a defined ratio and time endpoints.
46. Define the porosity trajectory and conductance law symbolically before discussing “near choke.”
47. Define `N_eff`, top-1 share, normalized entropy, and Gini in Methods.
48. Correct the phrase “1/Σsᵢ² → 1.0 of the tubes”; `N_eff` is a count, not “1.0 of the tubes.”
49. State `N` for every N-tube number in the text; `N_eff≈219` is uninterpretable without the total.
50. Replace `1e-6…1e-15` with scientific notation (`10⁻⁶–10⁻¹⁵`) and state units/dimensionlessness.
51. Define the conductance floor relative to what reference conductance.
52. Separate “endpoint classification unchanged” from “gain magnitude floor-dependent.”
53. State how initial tube heterogeneity is generated and whether the same realization is used across parameter sweeps.
54. State how random seeds are fixed and recorded.
55. Avoid “conservation holds” when the quantity is normalized by construction.
56. Use “algebraic homogenization parameter” rather than “lateral coupling” unless a physical flux operator is present.
57. Define the collapse threshold, whether it is first passage or sustained, and how ties/interpolation are handled.
58. Report the outer output timestep separately from internal substeps.
59. Replace “early switching is a real feature” with “the event persists under the tested discretization” until independent solvers agree.
60. Avoid “genuine sweep-and-conservation robustness result”; it is a finite sensitivity and numerical-invariant study.
61. Delete “review MAJ-…” references throughout.
62. Delete all function names from Results; move them to a code mapping appendix.
63. Convert “what would actually discriminate” into a formal experimental-design subsection with citations.
64. Explain whether the companion Paper A is published, submitted, or internal; do not cite an internal analysis filename as literature.
65. Add a conventional limitations subsection instead of the open-gap ledger.
66. Add conflict-of-interest, funding, author contribution, and data/code availability statements.
67. Add a complete reference list and use one citation style.
68. Add supplementary-method identifiers for slow-analysis details rather than repository paths in prose.
69. Provide alt text for each figure.
70. Provide a glossary for recurring terms: matched observable, capacity, compatibility, validation, identification, donor parameter, and numerical invariant.

---

## 14. Proposed submission-ready manuscript structure

1. **Title and abstract**
2. **Introduction**
   - Integrated-observable ambiguity
   - Prior espresso extraction/flow models
   - Contribution: matched-observable, null-first evidence calibration
   - Research questions and scope
3. **Data and Methods**
   - Dataset 1: Schmieder design and reconstructed endpoints
   - Dataset 2: Waszkiewicz pressure/flow/TDS campaign
   - Observable and unit contracts
   - RSM and uncertainty methods
   - Static-heterogeneity model and calibration/evaluation split
   - Temporal branch equations and parameter provenance
   - Dependence-aware comparison and cross-pressure protocol
   - Exploratory N-tube equations, control laws, numerical methods, and diagnostics
   - Reproducibility and artifact release
4. **Results**
   - 4.1 Source endpoint and conditional response surface
   - 4.2 Capacity audit across implemented response generators
   - 4.3 Null-first temporal reconstruction and its limits
   - 4.4 Pressure-level calibration sensitivity
   - 4.5 Composition incompatibility
   - 4.6 Exploratory streamtube concentration, preferably supplemental unless fully validated
5. **Discussion**
   - What the data constrain
   - What they do not identify
   - Model-set and campaign limitations
   - Measurement designs that would discriminate mechanisms
6. **Conclusion**
7. **Data and code availability**
8. **Declarations**
9. **References**
10. **Supplement**
    - Complete evidence matrix and dictionary
    - RSM deletion/model-form/robust covariance results
    - Residual and block/window sensitivities
    - Full cross-pressure tables
    - N-tube numerical, stochastic, floor, and operating sweeps
    - Artifact manifest and source-data dictionary

---

## 15. Submission-readiness checklist

### Scientific/statistical

- [ ] Jensen formula and gap range corrected.
- [ ] Preferred RSM uncertainty is heteroskedasticity-robust and shown in the figure.
- [ ] Model-selection and reconstructed-endpoint conditionality are explicit.
- [ ] Malformed source-data rows are removed or structurally separated.
- [ ] Result 2 block method refits models or is precisely relabeled.
- [ ] No equivalence claim rests on an interval crossing zero.
- [ ] Window/block sensitivity is reported.
- [ ] Residual trajectories and ACF are shown.
- [ ] Cross-pressure values agree across all artifacts.
- [ ] LOPO scope is restricted to the equilibrium calibration layer.
- [ ] Swelling/fines sign claim remains conditional in abstract, results, figures, and conclusion.
- [ ] N-tube trajectory and solver convergence are established or claims are demoted.
- [ ] N-tube classifier distinguishes single-channel from oligarchic concentration.
- [ ] Stochastic count and uncertainty are reconciled.
- [ ] Physical balances are added or “conservation” is replaced by “numerical invariant.”
- [ ] Donor extrapolation, clipping, start state, and horizon are audited.

### Figures and source data

- [ ] All five figures consume the frozen result bundle.
- [ ] Figure 1 distinguishes conditional curve from nominal-setting points.
- [ ] Figure 1 uses the preferred robust band.
- [ ] Figure 2 uses publication-facing terminology and verified sources.
- [ ] Figure 3 shows dependence/window limitations and current values.
- [ ] Figure 4 is clearly an ablation/incompatibility diagnostic.
- [ ] Figure 5 shows trajectory/event convergence rather than endpoint saturation alone.
- [ ] Vector figures, alt text, and color-blind-safe encodings are supplied.
- [ ] Complete source-data files regenerate every panel.

### Reproducibility

- [ ] Clean tagged commit.
- [ ] `git_dirty=false` in release manifest.
- [ ] Bundle source commit equals release commit.
- [ ] Environment/lock file is pinned and hashed.
- [ ] Manuscript, code, data, bundle, source data, and figures are all hashed.
- [ ] One command regenerates all Paper B artifacts.
- [ ] Strict CI fails on any artifact mismatch.
- [ ] Every headline number is generated from or checked against the bundle.
- [ ] Seeds, draw counts, invalid-fit handling, and slow-analysis settings are recorded.

### Manuscript form

- [ ] Review IDs, roadmap references, function names, and status/to-do material removed.
- [ ] Complete Methods with equations and estimands.
- [ ] Complete related-work review and verified references.
- [ ] Conventional limitations section.
- [ ] Data/code availability, funding, conflicts, and author contributions.
- [ ] No unresolved “owed” statements remain in the submission.

---

## 16. Supporting reference material

The references below are the most directly relevant primary or methodological sources used to assess the draft. They should be checked against the journal’s required citation format before submission.

1. **Schmieder, B. K. L., Pannusch, V. B., Vannieuwenhuyse, L., Briesen, H., and Minceva, M. (2023).** “Influence of Flow Rate, Particle Size, and Temperature on Espresso Extraction Kinetics.” *Foods* 12(15), 2871. The source describes 15 experimental settings, generally three extraction repetitions and six at the center, ten consecutive fractions, response-surface modeling with achieved operating values, and reconstruction of cup responses from extraction kinetics. [Publisher article](https://doi.org/10.3390/foods12152871)

2. **Cameron, M. I., et al. (2020).** “Systematically Improving Espresso: Insights from Mathematical Modeling and Experiment.” *Matter* 2, 631–648. Relevant to fine-grind deviations, model calibration, and grinder-specific response. [Publisher article](https://doi.org/10.1016/j.matt.2019.12.019)

3. **Moroney, K. M., Lee, W. T., O’Brien, S. B. G., Suijver, F., and Marra, J. (2016).** “Asymptotic Analysis of the Dominant Mechanisms in the Coffee Extraction Process.” *SIAM Journal on Applied Mathematics* 76(6), 2196–2217. Relevant to the multiscale/double-porosity extraction-model lineage, dominant mechanisms, and the scope of homogeneous packed-bed assumptions. [Publisher article](https://doi.org/10.1137/15M1036658)

4. **Lee, W. T., et al. (2023).** Physics of Fluids article on uneven extraction and flow in espresso. Relevant to spatially uneven extraction and the exact bibliographic identifier that should replace provisional dictionary wording. [Publisher article](https://doi.org/10.1063/5.0138998)

5. **Mo, C., et al. (2022).** “Modeling swelling effects during coffee extraction with smoothed particle hydrodynamics.” *Physics of Fluids* 34, 043104. Relevant to the coupled effects of swelling on intra-grain/inter-grain transport and to scoping the resistance-only sign test. [Publisher article](https://doi.org/10.1063/5.0086897)

6. **Waszkiewicz, R., Myck, F., Białas, Ł., Puciata-Mroczynska, M., Dzikowski, M., Szymczak, P., and Lisicki, M. (2026).** “Under pressure: Poroelastic regulation of flow in espresso brewing.” *Physics of Fluids*. Relevant to source-trace provenance and the distinction between same-campaign calibration and external validation. [Publisher article](https://doi.org/10.1063/5.0319611)

7. **Künsch, H. R. (1989).** “The Jackknife and the Bootstrap for General Stationary Observations.” *The Annals of Statistics* 17(3), 1217–1241. Foundational reference for block bootstrap under dependence; relevant to defining the resampling unit and stationarity assumptions. [Publisher article](https://doi.org/10.1214/aos/1176347265)

8. **Davidson, R., and Flachaire, E. (2008).** “The Wild Bootstrap, Tamed at Last.” *Journal of Econometrics* 146(1), 162–169. Relevant to heteroskedastic regression bootstrap and leverage-adjusted residuals. [Publisher article](https://doi.org/10.1016/j.jeconom.2008.08.003)

9. **Berk, R., Brown, L., Buja, A., Zhang, K., and Zhao, L. (2013).** “Valid Post-Selection Inference.” *The Annals of Statistics* 41(2), 802–837. Relevant to the distinction between conditional selected-model uncertainty and post-selection inference. [Publisher article](https://doi.org/10.1214/12-AOS1077)

10. **Altman, D. G., and Bland, J. M. (1995).** “Absence of evidence is not evidence of absence.” *BMJ* 311, 485. Relevant to the invalid inference from a confidence interval crossing zero to equivalence or “statistical indistinguishability.” [Publisher article](https://doi.org/10.1136/bmj.311.7003.485)

11. **Grandvalet, Y., and Bengio, Y. (2004).** “No Unbiased Estimator of the Variance of K-Fold Cross-Validation.” *Journal of Machine Learning Research* 5, 1089–1105. Relevant to dependence induced by overlapping training sets and cautious interpretation of validation uncertainty. [Journal article](https://www.jmlr.org/papers/v5/grandvalet04a.html)

12. **Roberts, D. R., et al. (2017).** “Cross-validation strategies for data with temporal, spatial, hierarchical, or phylogenetic structure.” *Ecography* 40, 913–929. Relevant to structured holdout design and avoiding random-sample validation for dependent data. [Publisher article](https://doi.org/10.1111/ecog.02881)

### Reference-use notes

- Source-study facts should be taken from the primary publication, not inferred only from repository transformations.
- Statistical method citations do not validate a particular implementation; the code must implement the cited procedure.
- The block-bootstrap reference assumes a clearly defined dependence structure. The espresso trace is strongly autocorrelated and potentially nonstationary, so block resampling should be justified rather than invoked by name alone.
- The wild-bootstrap reference supports heteroskedasticity-robust resampling but does not remove model-selection or first-stage endpoint uncertainty.
- The swelling paper supports a coupled process interpretation; it does not license a universal sign or magnitude outside its assumptions.

---

## 17. Bottom-line review recommendation

The updated Paper B has a promising and increasingly coherent methodological contribution. Its strongest results are:

1. correcting and matching the endpoint observable before mechanism comparison;
2. showing that a selected response surface and selected nominal-setting means answer different conditional questions;
3. demonstrating that model capacity does not equal mechanism identification;
4. using constant and flexible temporal nulls to separate the need for time variation from evidence for a specific bed mechanism; and
5. converting residual ambiguity into concrete recommendations for spatial, first-drip, and bed-state measurements.

The paper should nevertheless remain at **major revision** because its current release is not artifact-coherent, the Jensen prose is mathematically behind the code, the block procedure is mislabeled and overinterpreted, the cross-pressure numbers are inconsistent, malformed source-data rows are silently discarded, and the N-tube convergence/classification claims exceed the implemented diagnostics. These are correctable problems. Addressing them would materially strengthen both the science and the paper’s central message about evidential discipline.

A defensible submission should make Result 1 explicitly conditional, make Result 2 a dependence-aware reconstruction/validation study without equivalence overclaim, and either complete Result 3’s numerical/physical validation or demote it to a narrowly labeled exploratory supplement. The final release must be clean, single-source, and auditable.

