# Detailed technical review of the current `PAPER_B_DRAFT.md`

**Repository:** [`trbrewer/puckworks`](https://github.com/trbrewer/puckworks)  
**Reviewed branch and snapshot:** `main` at commit [`e297f54169d9b975750b3773d02a639d1e2fbc85`](https://github.com/trbrewer/puckworks/commit/e297f54169d9b975750b3773d02a639d1e2fbc85)  
**Manuscript reviewed:** [`docs/PAPER_B_DRAFT.md`](https://github.com/trbrewer/puckworks/blob/e297f54169d9b975750b3773d02a639d1e2fbc85/docs/PAPER_B_DRAFT.md)  
**Figures reviewed:** current Paper B Figures 1–5 and their generating code  
**Prior detailed-review snapshot used for comparison:** `c6fe9b45d4e273fc83c72db4d5e31dcd7d281b5e`  
**Review date:** 2026-07-13  
**Recommendation:** **Major revision before journal submission**

---

## 1. Scope, review basis, and limitations

This review assesses the scientific argument, statistical interpretation, figures, code-to-claim traceability, and reproducibility state of the current Paper B draft. It covers:

- the full Markdown manuscript;
- all five rendered figures;
- `puckworks/harness.py`, especially the Result 1 response-surface analysis, the temporal-model ladder, the cross-pressure calculations, and the N-tube calculations;
- `puckworks/figures.py`;
- `analysis/lopo_cv.py` and `analysis/residual_autocorr.py`;
- `puckworks/paper_b/build.py` and the committed `results.json`/manifest contract;
- the committed Schmieder-derived run table and Waszkiewicz time-series representation;
- the current Paper B evidence matrix; and
- relevant primary literature on the source experiments, espresso infiltration and swelling, structured validation, and heteroskedastic regression bootstrap.

The review combines static code inspection, direct figure inspection, and targeted independent recomputation of the principal Result 1 statistics from the committed run-level table. It does **not** claim a clean-room rerun of every slow poroelastic or N-tube simulation in a newly provisioned, independently pinned environment. Findings established directly from code are distinguished from robustness questions that require rerunning the full pipeline.

### 1.1 Exact reviewed artifact hashes

| Artifact | SHA-256 |
|---|---|
| `docs/PAPER_B_DRAFT.md` | `a3ed7de06f5707a37f24f5e7c166526bb4b5122b8db4112d167582817f5dabe7` |
| `puckworks/harness.py` | `5f51abeb10ae694dc0f12177e3a7cb84a3b8933a94c41f2f6c696c2376ca846c` |
| `puckworks/figures.py` | `7c78cf069927064717eec6d4909b487b7759180c5c1ddff732da1a0705cf2053` |
| `analysis/lopo_cv.py` | `637798a17eafeccfffe889c21df75fd10a192dc1e954517d2463dbd858f3653d` |
| `analysis/residual_autocorr.py` | `c99da7b64d792b9f4ed15db5f76b59dc4d05999bcdc21206f0f02a1ff1048fa0` |
| Figure 1 PNG | `d2c0c894b5b5df71f8acdfe06b4e13507f199a65d67af3475ff97218b1f6f74c` |
| Figure 2 PNG | `68f1f76ec67ad2d625f2f935ff476d0433b4e9b7e1a440b5833752cdd5089792` |
| Figure 3 PNG | `ed38456a43b145fb456dd2b8d5d060a91fd540154c79b1c93d1043fd2f6f5b3a` |
| Figure 4 PNG | `5a8e8c2d1a6158ebfb135cbfd5e1913e84e1909383392d75a03aee06b9f3a340` |
| Figure 5 PNG | `7daa27de8786100a8a1800137ac1ef4c8c1c46c42879d41785616684f4b9fe26` |

The repository head is a later Paper A commit, but the review is pinned to that exact tree because it is the current `main` state presented to a reader.

---

## 2. Executive assessment

The draft has improved substantially since the prior Paper B review. Important corrections now present include:

- the primary response-surface refit uses the source study's achieved flow and temperature predictors and evaluates the cross-section at the actual center setting;
- the descriptive slope interval now uses the correct t critical value;
- the manuscript correctly distinguishes the 15 nominal design settings, 48 complete TDS/BR-1/2 run rows, and the 3/6/3 run counts in the selected central-condition comparison;
- the four cross-pressure summaries are explicitly separated, and the previously conflated shared-calibration and leave-one-pressure-out quantities are labeled more carefully;
- full-precision aggregation is stated for the cross-pressure summaries;
- the temporal branch's donor-parameter provenance is tabulated;
- the swelling/fines conclusion is narrowed to a conditional sign constraint on isolated resistance-only branches under imposed fixed pressure;
- Result 3 is explicitly labeled exploratory, the floor dependence of the closed-form gain is disclosed, and additional numerical/design sweeps have been added; and
- Figures 1, 3, and 5 have been revised to expose several of these qualifications.

These changes materially strengthen the paper. The best defensible central contribution is still valuable:

> Integrated espresso observables can establish model capacity, incompatibility, and a need for temporal flexibility within a tested model set, while remaining insufficient to identify a unique physical mechanism.

The present draft nevertheless remains unsuitable for submission for five principal reasons.

### 2.1 Submission-blocking findings

1. **The committed reproducibility bundle is stale and dirty.** The current manifest identifies source commit `f47fc824...`, not the reviewed `main` commit `e297f541...`, and records `git_dirty: true`. It hashes only four data inputs and checks twelve headline numbers. A zero-failure manifest under those conditions is not evidence that the current manuscript and all figures were regenerated reproducibly.

2. **The Result 1 interval remains conditional on a selected seven-term model and an iid/homoskedastic residual bootstrap.** Independent checks find approximately seventeen-fold variation in within-setting standard deviations. Wild-bootstrap sensitivity preserves the qualitative vertex but widens the interval. The manuscript should report this conditionality and a heteroskedasticity-robust sensitivity explicitly.

3. **Result 2 remains an in-sample time-series reconstruction with extremely structured residuals.** A Durbin–Watson value near 0.01 is not a minor diagnostic; it indicates that pointwise RMSE is aggregating long coherent error runs. The current evidence supports “temporal flexibility greatly improves reconstruction over this window,” not predictive validation or mechanism selection.

4. **The Result 3 conservation claim is not implemented as described.** The code normalizes `s = w / w.sum()`, making `sum(s)=1` tautological, and then stores `share_sum_max_deviation` and `min_flow_share` from the final computed `s`, not the maximum/minimum over all integration substeps. It therefore does not establish that flow-share conservation and non-negativity held “at every step,” nor does it audit mass, age, or raw-flow balance. This is a definite code-to-claim defect.

5. **The manuscript is still an internal project document.** It retains “review-endorsed,” review IDs, function names as Methods, an “Open gaps” section, and a “Status & to-do (NOT for the manuscript body)” section. A conventional Methods, references, data/code availability statement, pinned release, and self-contained captions remain explicitly owed.

### 2.2 Recommended disposition

| Dimension | Assessment |
|---|---|
| Scientific question | Important and suitable for a modeling/methods audience |
| Matched-observable and null-first framing | Strong |
| Result 1 qualitative conclusion | Supported: selected central cells do not show a middle-dial maximum; the fitted conditional surface can |
| Result 1 inference | Promising but conditional; needs heteroskedastic/post-selection sensitivity and clearer outcome provenance |
| Result 2 | Useful in-sample reconstruction audit; not yet predictive mechanism discrimination |
| Result 3 | Interesting exploratory model behavior, but conservation/convergence claims are not yet adequately verified |
| Reproducibility | Improved locally, but the committed paper-wide bundle is stale, dirty, and incomplete |
| Overall recommendation | **Major revision** |

---

## 3. Changes since the previous detailed review

| Previous issue | Current status | Assessment |
|---|---|---|
| Primary RSM predictor mismatch | Achieved flow and temperature are now primary, evaluated at experiment 7 | **Resolved in the main fit** |
| Wrong center-setting mask | Experiment 7 is now used | **Resolved** |
| Normal rather than t slope interval | Correct t-based interval `[1.16, 3.36]` reported | **Resolved** |
| Confusion over design/settings/runs | Main text now states 15 settings and 48 complete run rows, with 3/6/3 runs in selected cells | **Resolved in main text** |
| `cond(X)` versus `cond(XᵀX)` | Both are named correctly; centered/scaled fit is reported | **Resolved** |
| Hard-coded evidence matrix | Figure 2 consumes a committed evidence table | **Improved**, but ontology remains compressed and partly subjective |
| Shared-calibration versus LOPO conflation | Four summaries are now explicitly separated | **Substantially resolved** |
| Early rounding in cross-pressure means | Manuscript says aggregation is from unrounded values | **Resolved for reported summaries**, but should be regression-tested |
| “Parameter-free” temporal branch | Provenance table and qualification added | **Improved**, but “zero-free-parameter” and “0p” remain misleading |
| Swelling/fines overclaim | Narrowed to a conditional isolated-branch sign constraint | **Largely resolved** |
| Result 3 called a stability result | Renamed exploratory finite-time concentration | **Resolved in framing** |
| Floor dependence not tested | Integration is rerun over a floor range | **Improved** |
| N/timestep/pressure/grind sweeps absent | One-factor-at-a-time sweeps added | **Improved**, but called “factorial,” and conservation/convergence acceptance criteria are not met |
| Single-source paper build absent | A Paper B build and manifest exist | **Partial only**; current bundle is stale/dirty and omits major result classes |
| Internal manuscript form | Review-management scaffolding remains | **Not resolved** |

---

## 4. Prioritized required-action matrix

Priority definitions:

- **P0 — validity or reproducibility critical:** resolve before submission.
- **P1 — major interpretation/reporting:** required for a defensible paper.
- **P2 — presentation/editorial:** required for publication quality.

| ID | Priority | Required action | Acceptance criterion |
|---|---:|---|---|
| B3-01 | P0 | Convert the document into a conventional manuscript. | Remove review narration, review IDs, backlog/status sections, and implementation function names from the scientific exposition; add complete Methods, References, Data Availability, Code Availability, and Limitations. |
| B3-02 | P0 | Regenerate a clean Paper B release bundle at the reviewed commit. | Manifest `source_commit == bundle_source_commit == git HEAD`; `git_dirty == false`; release is tagged; environment lock and seeds are included. |
| B3-03 | P0 | Make the bundle complete and make figures consume it. | Bundle includes every manuscript-facing number, all Figure 1–5 source arrays/tables, Result 3 robustness outputs, residual diagnostics, evidence-matrix contents, and figure metadata; plotting does no hidden refitting. |
| B3-04 | P0 | Correct the language for the Schmieder endpoint outcome. | Replace “raw/measured endpoint” with “source-derived run-level endpoint estimate” wherever appropriate; explain first-fraction measurement plus integrated fitted kinetics. |
| B3-05 | P0 | Add heteroskedasticity-robust RSM uncertainty. | Report the existing fixed-design iid residual interval together with a wild-bootstrap or HC-based sensitivity; state that both condition on the selected seven-term model. |
| B3-06 | P0 | Address model-selection uncertainty. | Either rerun the declared backward-elimination rule inside each resample or explicitly label the interval as conditional post-selection inference and provide full-quadratic/model-averaged sensitivity. |
| B3-07 | P0 | Export influence and deletion diagnostics. | Report leave-one-run and leave-one-setting vertex ranges, concavity/domain status, and the result of deleting experiment 10 replicate 1. |
| B3-08 | P0 | Repair the Jensen audit's mean-preservation claim. | After clipping/truncation, calculate and report the evaluated `E[K]`; compare `E[EY(K)]` with `EY(E[K])`, or renormalize/reconstruct a truly unit-mean truncated distribution. |
| B3-09 | P0 | Replace “zero-free-parameter/0p.” | Use “zero additional coefficients fitted to the scored flow trace”; publish parameter counts by fit role and observable. |
| B3-10 | P0 | Make Result 2 dependence-aware. | Use blocked/prequential/whole-pressure validation or a correlated-error likelihood; otherwise confine the claim to in-window in-sample reconstruction and present the cubic strictly as a flexibility bound. |
| B3-11 | P0 | Propagate or disclose source-trajectory uncertainty. | Use replicate/measurement uncertainty supplied by the source where available, or state clearly that analyses use averaged/digitized curves without propagated uncertainty. |
| B3-12 | P0 | Show the actual LOPO evidence. | Add held-out curves or a compact pressure-by-pressure LOPO table/figure; do not rely only on a shared-calibration panel while the prose's robustness argument is LOPO. |
| B3-13 | P0 | Replace the Result 3 conservation audit. | Track raw total flow/control balance, normalized-share sum, minimum conductance/share, and any age/mass balance at every substep; export maxima/minima over the full trajectory and test them. |
| B3-14 | P0 | Investigate and converge the early N-tube switching. | Plot physical time, rerun with smaller steps/integrators and event-time diagnostics, and show trajectory/collapse-time convergence rather than endpoint classification alone. |
| B3-15 | P0 | Stop calling the one-at-a-time sweep factorial. | Relabel it OFAT, or run an actual crossed design over the load-bearing control, lateral, closure, N, timestep, and start-state axes. |
| B3-16 | P0 | Correct Figure 5 and Result 3 summary fields. | Fix the panel-D cross-reference; separate numerical-axis invariance from deliberate physical contingencies; correct the 6–12 versus 6–11-bar text; harmonize N=150 and N=400 reports. |
| B3-17 | P0 | Add horizon and start-state sensitivity. | Vary initial extraction ages/heterogeneity phase and simulation horizon; report whether collapse time and endpoint classification change. |
| B3-18 | P0 | Align tests and code documentation with manuscript claims. | Remove test/docstring statements that the result is “physics, not tuning” or that swelling is “refuted”; add tests for conservation-over-time, current pressure range, figure panel data, and bundle freshness. |
| B3-19 | P1 | Add uncertainty bands to Figure 1's RSM cross-section. | Plot a bootstrap envelope and explicitly label the curve as a conditional shape cross-section, not an absolute reconstruction from rounded source coefficients. |
| B3-20 | P1 | Improve Figure 2's evidence schema. | Publish a data dictionary for every status, parameter role, observable, calibration/evaluation split, and evidence-strength category; include source/rationale fields. |
| B3-21 | P1 | Replace “mechanism discrimination” where only capacity is assessed. | Title and section headings distinguish capacity, incompatibility, reconstruction, and identification. |
| B3-22 | P1 | Reframe pressure “regimes.” | Use continuous pressure-varying error/ranking language unless pressure bins are prespecified and formally tested. |
| B3-23 | P1 | Add residual plots and sensitivity to evaluation window/time grid. | Show residual trace and ACF by branch; vary 15–95 s boundaries and decimation/block length; report whether rankings persist. |
| B3-24 | P1 | Qualify the sign test with control and composition assumptions. | State the fixed-pressure, isolated-resistance assumptions in the heading, figure, and abstract-level discussion; avoid general absence claims. |
| B3-25 | P1 | Treat the composition result as a one-implementation diagnostic. | Add ablations for parameter transfer, initial state, control law, and composition form, or move the figure to a supplement. |
| B3-26 | P1 | Normalize and diversify Result 3 concentration metrics. | Report `N_eff/N`, entropy/Gini/top-k share, collapse time, and uncertainty across substantially more than four stochastic realizations. |
| B3-27 | P1 | Add a physical lateral-exchange closure or demote Result 3. | Until a transverse-Darcy/shared-pressure operator is implemented and validated, retain Result 3 as a clearly separated exploratory supplement. |
| B3-28 | P1 | Complete the data/input hash set. | Hash time-series traces, static calibrations, constants, model code/config, evidence table, all figure source data, and environment files. |
| B3-29 | P1 | Produce vector figures and source-data tables. | Commit PDF/SVG outputs and one machine-readable source table per figure; verify fonts and dimensions at journal size. |
| B3-30 | P1 | Add a source/provenance diagram. | Diagram identifies focal evaluation data, same-campaign calibration, external donor calibration, literature-fixed choices, and fitted-to-scored-trace quantities. |
| B3-31 | P2 | Rewrite the abstract around the scientific contribution. | Replace the internal correction history with the scientific question, matched targets, principal bounded findings, and limitations. |
| B3-32 | P2 | Make captions self-contained. | Define all abbreviations, sample sizes, error bars, fit roles, windows, parameter counts, and validation class without requiring the body text. |
| B3-33 | P2 | Remove implementation labels from figures. | Replace `impl`, `qual-cap`, `0p`, internal registry keys, and review tags with reader-facing scientific terms. |
| B3-34 | P2 | Complete the related-work search before novelty language. | Record databases, dates, queries, screening criteria, and bounded novelty claims. |
| B3-35 | P2 | Harmonize terminology and numeric formatting. | Use one term for run/setting/cell, one CI style, consistent significant figures, and scientific notation such as `10⁻⁶` rather than mixed `1e-6`. |

---

## 5. Independent numerical checks

The following checks were recomputed from the committed TDS, BR 1/2 run table using the retained seven-term achieved-predictor specification. They are intended as targeted verification, not a replacement for a full clean build.

### 5.1 Achieved-predictor response surface

| Quantity | Independent result |
|---|---:|
| Complete run rows | 48 |
| Nominal settings | 15 |
| Center-setting runs (experiment 7) | 6 |
| Mean achieved center flow | 1.90108 mL/s |
| Mean achieved center temperature | 88.2579 °C |
| Conditional grind vertex | 1.743153 |
| Adjusted R² | 0.643401 |
| Residual SD | 0.113739 g |
| Grind-squared coefficient | −1.474505 |

These values agree with the current primary fit and support the corrected center-setting implementation.

### 5.2 Deletion stability

| Diagnostic | Result |
|---|---|
| Leave-one-run vertex range | 1.73611–1.76515 |
| Leave-one-setting vertex range | 1.72018–1.77557 |
| Concave and in-domain leave-one-setting fits | 15/15 |
| Most influential run | experiment 10, replicate 1 |
| Cook's D for that run | 0.441 |
| Standardized residual | −3.66 |
| Leverage | 0.187 |

The conditional vertex is therefore reasonably stable to deletion in this dataset. This is useful evidence and should be exported rather than left as “owed.” It does not resolve post-selection or heteroskedastic uncertainty.

### 5.3 Leave-one-setting-out prediction

Using achieved predictors and holding out complete experiment IDs:

- Q² from averaging held-out run predictions within setting: **0.470105**;
- Q² from predicting at the held-out setting's mean achieved predictors: **0.470088**;
- largest difference between the two aggregation methods: **0.000477 g**.

The manuscript's approximate Q² ≈0.48 is directionally accurate but should be updated to one frozen, full-precision result.

### 5.4 Heteroskedasticity stress check

Within-setting sample SD spans **0.0141 to 0.2418 g**, a roughly **17-fold** range. This makes an iid residual bootstrap a questionable sole uncertainty procedure even though a simple fitted-value versus absolute-residual rank test is not individually significant in this small sample.

A targeted bootstrap sensitivity gave:

| Bootstrap | 2.5%, median, 97.5% vertex | Joint concave and in-domain |
|---|---|---:|
| iid residual | [1.7007, 1.7435, 1.8188] | 99.91% |
| wild Rademacher | [1.6939, 1.7435, 1.8384] | 99.80% |
| wild Mammen | [1.6905, 1.7453, 1.8287] | 99.86% |
| setting-cluster pairs stress test | [1.4908, 1.7522, 2.0857] | 89.68% |

The wild-bootstrap results preserve the qualitative conditional vertex while modestly widening the interval. The setting-cluster pairs result should **not** automatically replace the primary interval because the 15 design settings are fixed design points rather than a random sample of settings; it is useful as a warning about small-design resampling and model fragility, not as a default inferential target.

### 5.5 Model-form sensitivity

| Model | Vertex | Adjusted R² | AICc |
|---|---:|---:|---:|
| Grind only | — | — | −158.09 |
| G + F + T + G² | — | — | −196.27 |
| Retained seven-term model | 1.74315 | 0.64340 | **−199.46** |
| Full quadratic | 1.73727 | 0.63690 | −193.09 |

The full quadratic also gives a concave in-domain vertex close to the retained model. This supports shape stability, while the AICc difference supports—but does not make inferentially costless—the selected specification.

### 5.6 Interpretation of these checks

The current Result 1 conclusion can be strengthened to:

> Conditional on the achieved-predictor quadratic specification and the source-derived run-level endpoints, the fitted grind cross-section has a stable interior vertex near dial 1.74. The three selected nominal central-condition cells themselves do not show a middle-dial maximum. The fitted vertex is robust to single-run and single-setting deletion and to a full-quadratic sensitivity, but its confidence interval remains conditional on model selection and should include heteroskedasticity-robust sensitivity.

That is a stronger and more precise statement than either “the data have no maximum” or “the mechanism is identified.”

---

## 6. Detailed major comments

### 6.1 Manuscript architecture, inferential framing, and reproducibility

#### MAJ-01 — The document remains a revision memo rather than a manuscript

The opening labels the title “review-endorsed,” instructs the reader on verb discipline, points to ROADMAP review history, and says a conventional Methods section is still owed. Sections 7 and 8 then list open gaps and project-management status. This material is useful internally but is unsuitable in a scientific submission.

**Required action:** create a clean manuscript branch or generated manuscript containing only scientific content. Put review history, backlog IDs, and implementation notes in repository documentation. The manuscript should have a conventional sequence: Introduction; Data and observable definitions; Models; Calibration and evaluation design; Statistical analysis; Numerical methods; Results; Discussion; Limitations; Data/Code Availability; References.

#### MAJ-02 — The title still overstates “mechanism discrimination”

Much of the paper establishes model capacity, incompatibility under a specified composition, or in-sample reconstruction—not discrimination among mechanisms in the strong inferential sense. Figure 2 itself says it is not a winner scoreboard, and incomplete wetting is not implemented.

**Required action:** either expand the competing model set and experimental evidence until discrimination is genuinely symmetric, or use a title such as:

> **Limits of mechanism discrimination from integrated espresso measurements: matched observables, temporal nulls, and exploratory streamtube dynamics**

This title better matches the paper's strongest contribution.

#### MAJ-03 — “Two published datasets” understates the dependency graph

The abstract says the paper determines what “two published datasets” can discriminate, while the Methods list five repository dataset keys and the models import same-campaign calibrations and external donor quantities. Two datasets may be the focal evaluation targets, but the conclusions depend on a broader calibration and donor network.

**Required action:** use “two focal evaluation datasets, together with registered same-campaign and external donor/calibration sources.” Add a provenance diagram and parameter table.

#### MAJ-04 — The current manifest cannot certify the current manuscript

The committed Paper B manifest reports:

- `source_commit = f47fc824519d3b5f203c95d6be60cef952b30df3`;
- `bundle_source_commit` equal to that same older commit;
- `git_dirty = true`;
- four data hashes; and
- twelve checked claims with zero failures.

The reviewed tree is `e297f54169d9b975750b3773d02a639d1e2fbc85`. A successful claim check from an older dirty tree does not establish that the current manuscript and images were built from the recorded bundle.

**Required action:** rebuild from a clean checkout at the release commit and fail the build whenever the tree is dirty or the bundle commit differs from `HEAD`. Include the manuscript/figure hashes in the release manifest.

#### MAJ-05 — The build is not yet the single source of truth

`puckworks/paper_b/build.py` assembles selected RSM, Result 1, ladder, cross-pressure, and LOPO outputs, but the paper also relies on Result 3 robustness, the Jensen audit, the channeling closure sweep, the evidence matrix, composition diagnostics, residual diagnostics, figure annotations, and source tables. Several figures still call analysis functions rather than reading a frozen results object.

**Required action:** one build command should produce:

1. a versioned machine-readable results bundle;
2. all figure-source tables/arrays;
3. every manuscript table;
4. all vector figures; and
5. a manifest linking each headline sentence to a bundle path.

Plotting code should be a pure rendering layer over the bundle.

#### MAJ-06 — The input hash set is too narrow

The manifest hashes the Schmieder cup-mass and RSM-coefficient files, one Waszkiewicz TDS file, and the evidence matrix. It does not hash all flow traces, static-calibration inputs, model constants, donor calibration artifacts, configuration files, or the source arrays behind every figure.

**Required action:** hash every input that can change a manuscript number or plotted curve. Include code commit, environment lock, random seeds, numerical tolerances, and platform information.

#### MAJ-07 — Regression tests document stronger claims than the manuscript

Current test/docstring language includes formulations equivalent to “regime structure is physics, not fit tuning” and “swelling refuted as driver,” whereas the manuscript correctly says the physical origin is unresolved and the sign result is conditional on an isolated fixed-pressure branch. Public code documentation is part of the scientific record and should not reintroduce claims the prose has withdrawn.

**Required action:** make test names/docstrings operational rather than interpretive. For example, test that a ranking or sign is reproduced under a declared configuration—not that it proves physics or refutes a mechanism.

#### MAJ-08 — Validation-strength tags are useful internally but should be formalized for readers

The draft uses labels such as “qualitative,” “same-campaign,” “capacity,” and “independent,” but no formal schema defines the criteria or hierarchy. Figure 2 compresses these into short codes.

**Required action:** publish a validation taxonomy with explicit fields: observable match, unit match, calibration source, evaluation source, fitted parameters by role, sample unit, held-out structure, uncertainty treatment, and evidence class. Avoid implying a scalar ordering if the dimensions are not commensurate.

---

### 6.2 Result 1 — corrected empirical target and response-surface analysis

#### MAJ-09 — The endpoint response is source-derived, not a directly measured whole-cup endpoint

Schmieder et al. collected fractions and fitted extraction kinetics. The cup component mass was calculated by combining the measured first-fraction contribution with integration of the fitted kinetic curve to the target beverage mass. Calling the resulting table “raw TDS response,” “measured endpoint,” or “raw cells” obscures this processing step.

This distinction matters because Paper B's methodological theme is matched observables and provenance. The transformed endpoint is a legitimate run-level outcome, but its uncertainty includes fraction measurements, kinetic fit, integration, and endpoint definition.

**Required action:** consistently use “source-derived run-level TDS endpoint estimate” or “TDS-derived extraction-yield estimate.” Describe the calculation and clarify whether the repository reproduces source rounding, fit uncertainty, and replicate handling.

#### MAJ-10 — The selected-cell contrasts are descriptive and heavily conditioned

The 3/6/3 comparison correctly shows that the selected nominal-condition cell means do not have a middle-dial maximum. However, the achieved pressures differ and the comparison is from one machine, one principal coffee, and one campaign. The Welch intervals do not isolate dial causally.

The draft mostly states this correctly. The concern is rhetorical consistency: phrases such as “the raw cells do not support an interior maximum” are safe only if immediately tied to these selected nominal settings and the derived endpoint.

**Required action:** retain “in the three selected nominal settings, the middle mean was below the dial-2.0 mean.” Avoid generalizing to the conditional response surface or to grinder fineness.

#### MAJ-11 — The primary RSM interval is conditional on a post-selected specification

The current interval is produced after retaining a seven-term model. The source used backward elimination. If selection is not repeated inside the bootstrap, the interval describes uncertainty conditional on the selected terms, not the entire analysis procedure.

The draft acknowledges this in one paragraph, but the abstract, figure, and captions should carry the same qualification. A reader should not interpret `[1.70, 1.82]` as an unconditional confidence interval for a physical optimum.

**Required action:** choose one of the following:

- repeat the declared elimination rule in every resample and report selection frequencies; or
- keep the conditional interval but label it “conditional fixed-specification bootstrap interval,” and provide full-quadratic and model-averaged sensitivity.

#### MAJ-12 — Heteroskedasticity should be handled explicitly

The independent check found a setting-level SD range of 0.014–0.242 g. With only three repetitions at most settings, exact variance modeling is difficult, but the scale variation is too large to leave unmentioned when the sole primary interval resamples residuals as exchangeable.

Wild-bootstrap sensitivity produces intervals around `[1.69, 1.83–1.84]`, preserving the conclusion but widening the upper side. This is a favorable result for the authors because it shows that the conditional vertex is not an artifact of the iid residual bootstrap.

**Required action:** add the wild-bootstrap sensitivity to the results bundle and manuscript. A heteroskedasticity-consistent covariance estimate can be reported as an additional local check, with small-sample caveats.

#### MAJ-13 — The deletion analyses are available and should no longer be “owed”

The manuscript identifies experiment 10 replicate 1 as mildly influential and says leave-one-run sensitivity is owed. Independent recomputation shows the vertex remains 1.736–1.765 after deleting any one run and 1.720–1.776 after deleting a full setting; every setting-deletion fit remains concave and in-domain.

**Required action:** implement these diagnostics in the repository build, export the exact ranges, and remove the open-task wording. Show a compact influence plot or supplementary table.

#### MAJ-14 — The leave-one-setting-out result should be frozen at full precision

The current open-gap text reports Q² ≈0.48. Independent achieved-predictor recomputation gives approximately 0.4701. This is not a substantive discrepancy, but it illustrates that the prose and bundle are not yet generated from a single immutable source.

**Required action:** choose and document the precise prediction aggregation. Export per-setting observed and predicted values, PRESS, RMSE, Q², and sample counts. Round only at presentation.

#### MAJ-15 — The RSM curve in Figure 1 is a shape cross-section on an absolute EY axis

Figure 1a labels the curve “RSM fit (achieved predictors; shape only)” but plots it on the same absolute extraction-yield axis as the selected-cell estimates. The note about rounded source coefficients explains why shape rather than absolute reconstruction is used, but the visual still invites absolute comparison.

**Required action:** either:

- plot the full independently refitted absolute prediction with a bootstrap band; or
- center both curve and data and label the panel as a relative-shape comparison.

If the refit itself supplies the absolute intercept from run data, explain why it is called shape-only and which absolute level is being suppressed.

#### MAJ-16 — Figure 1 uncertainty is incomplete

The cell error bars are ±SD, not uncertainty of the mean, and the conditional RSM curve has no uncertainty band. The individual run points are very light and visually subordinate.

**Required action:** make run points clearly visible; define SD versus SE/CI in the caption; add a bootstrap curve envelope and a vertex interval marker. Do not use the vertex band as a substitute for response uncertainty.

#### MAJ-17 — The Jensen “exact gap” audit is not exact after clipping

The untruncated lognormal nodes are constructed to have unit mean in distributional expectation, but the implementation clips the evaluated multipliers to a finite response support. Once clipped, the discrete evaluated `K` values need not retain mean 1. The code then compares `E[EY(K_clipped)]` with `EY(1)` and calls it a direct Jensen gap for a unit-mean distribution.

The reported clipped quadrature mass below 0.2% suggests the numerical effect may be small, but the mathematical statement should still be correct.

**Required action:** report the post-clipping weighted mean and compute `E[EY(K)] − EY(E[K])`, or construct/renormalize a truncated distribution with exact mean one. Add a tolerance check showing that the conclusion is unchanged.

#### MAJ-18 — The closure sweep is descriptive, not a robustness probability

The manuscript correctly says that 10 of 25 fixed combinations is not a probability. The tested rectangle and grid, however, are not scientifically justified, and the median prominence of zero is sensitive to the convention that failed interior peaks receive zero prominence.

**Required action:** justify the parameter rectangle from calibration uncertainty or plausible bounds; show peak location and prominence continuously; demonstrate grid and boundary convergence; report the fraction only as a design-grid summary.

#### MAJ-19 — “Only implemented branch” is a registry statement, not a scientific ranking

The static channeling branch is the only current registry branch producing an interior maximum under its selected calibration, while incomplete wetting is absent and other branches target different observables or use altered parameters. This demonstrates availability/capacity, not superiority.

**Required action:** lead with the asymmetry. Consider renaming Result 1 “capacity audit of currently implemented branches.” Do not allow Figure 2 color or ordering to function as an implicit winner ranking.

#### MAJ-20 — Figure 2 does not contain all metadata claimed in the prose

The manuscript says the matrix covers implementation status, calibration data, evaluation data, observable, free parameters, fitted-versus-predicted status, evidence strength, and decisive missing experiment. The rendered matrix has five compressed columns and a side note. Terms such as `impl`, `proxy`, `same-campaign`, `elevated-pc`, `qual-cap`, and `n/e` are not self-explanatory.

**Required action:** publish the full evidence table in the paper or supplement with human-readable fields and citations. Keep the figure as a simplified map, not the sole audit record.

---

### 6.3 Result 2 — temporal reconstruction and cross-pressure transfer

#### MAJ-21 — “Zero-free-parameter” is internally contradictory and should be removed

The body first calls the empirical trajectory “zero-free-parameter” and later correctly says it has zero additional coefficients fitted to the scored 9-bar flow trace while importing two equilibrium parameters and a three-parameter TDS sigmoid. Figure 3 uses “0p.” A reader will reasonably read that as parameter-free.

**Required action:** use one precise label everywhere: **“0 coefficients fitted to this flow trace.”** In a parameter-provenance table, separately count parameters fit to the scored trace, same-campaign other observables, external donor data, literature values, and fixed numerical choices.

#### MAJ-22 — Result 2 establishes in-window flexibility, not predictive necessity

The constant branches, empirical Φ(t), and flexible cubic are compared on the same 15–95 s trace. The cubic is fitted and scored in-sample. The empirical trajectory uses same-rig TDS and flow-derived quantities. The ranking therefore shows that time variation can reduce reconstruction error relative to constants within that chosen window; it does not establish that a time-varying mechanism is predictively required on new shots.

**Required action:** reserve “needed” for the declared model class/window/metric, or perform blocked/prequential validation. A stronger design would train temporal parameters on one pressure or early interval and predict another pressure or later interval without retuning.

#### MAJ-23 — Durbin–Watson ≈0.01 is a central lack-of-fit result

A mean decimated Durbin–Watson value near 0.01 indicates extremely strong positive residual dependence. Decimation to 1 s makes the diagnostic more interpretable than using the native ≈10 Hz spacing, but it does not make observations independent or validate pointwise RMSE differences.

**Required action:** show residual time series and ACF for each branch; report effective block scales; use block bootstrap, generalized least squares, or whole-pressure/whole-shot replication for uncertainty. Test whether the ranking persists across reasonable evaluation windows and sampling grids.

Structured validation should respect temporal and hierarchical dependence; overlapping held-out calculations do not provide independent errors merely because the scoring units are different time points.

#### MAJ-24 — Source measurement/replicate uncertainty is not propagated

The Waszkiewicz source reports repeated TDS windows and repeated flow measurements/uncertainty. The repository appears to compare models with an averaged or digitized trajectory as if it were exact. This is acceptable for an exploratory reconstruction if disclosed, but not for a strong model-comparison claim.

**Required action:** obtain and use replicate traces/uncertainties where available. Otherwise, show digitization/measurement bands and state that RMSE differences exclude source uncertainty.

#### MAJ-25 — Figure 3a shows a reproduced model curve without the source data

The panel title now honestly says “MODEL curve (reproduction),” which is an improvement. However, the body says the machine-only model reconstructs the digitized source trace. Without the source trace or residuals in the panel, the reader cannot assess that claim.

**Required action:** overlay the digitized source curve with uncertainty and show residual/error, or move the reproduction to a methods-verification supplement and avoid using it as empirical evidence in the main figure.

#### MAJ-26 — Figure 3c is explicitly not LOPO, while the strongest prose argument is LOPO

The panel title correctly says “shared calibration; NOT LOPO,” but the manuscript devotes substantial text to leave-one-pressure-out robustness. A reader sees only the less stringent shared-calibration curves.

**Required action:** show LOPO held-out RMSEs by pressure as points/lines or provide a nearby table. The shared-calibration panel can remain as a separate descriptive result.

#### MAJ-27 — The LOPO analysis validates only part of the temporal pipeline

Leave-one-pressure-out refits the two-parameter equilibrium pair while retaining the 9-bar TDS-derived solids trajectory and donor assumptions. It is a useful check that no single equilibrium point dominates the calibration. It is not an independent transfer test of the temporal mechanism.

**Required action:** state this limitation in the abstract-level summary and figure caption. Consider nested donor sensitivity or leave-one-pressure-out rebuilding of every pressure-dependent quantity that can be rebuilt.

#### MAJ-28 — “Regime-dependent” remains too mechanistic

The abstract now uses “pressure-varying reconstruction error,” but the Result 2 body still says “It is regime-dependent.” The bins were not prespecified, and no change-point or interaction test establishes discrete regimes.

**Required action:** use “the relative reconstruction errors vary with pressure.” Reserve “regime” for a formally defined physical or statistical transition.

#### MAJ-29 — The isolated-branch sign constraint is useful but narrower than the heading can suggest

Under fixed pressure and an isolated branch whose only effect is increasing resistance, decreasing flow has the wrong sign for a rising residual. This is a valid conditional constraint. It does not imply that swelling or fines migration is absent in a coupled machine–bed system. The draft now explains this well; the risk remains in short headings and figure labels.

Mo et al. model swelling as a coupled influence on intra- and inter-grain transport and report effects on extraction rate and beverage strength, not a universal one-variable flow theorem. Likewise, infiltration, saturation, erosion, and machine response can change the net sign.

**Required action:** put “isolated, fixed-pressure resistance-only branch” in the section heading or first sentence of every summary. Avoid “excludes/refutes swelling” in tests, captions, or repository documentation.

#### MAJ-30 — The transferred swelling magnitude is not portable

The ≈4% terminal flow ratio and RMSE ≈1.08 g/s come from one transferred powder parameterization and one imposed composition. They are useful as a stress test but should not be presented as a general magnitude prediction for espresso.

**Required action:** distinguish the sign argument, which follows from the branch assumptions, from the numerical magnitude, which is parameterization-specific. Add parameter sensitivity or omit the magnitude from the main claim.

#### MAJ-31 — Figure 4 rejects one composition implementation, not a mechanism class

The tested shared-porosity composition plus imported swelling flattens the trajectory and performs worse than the constant null. The figure appropriately notes that it cannot separate parameter transfer, initial-state, control-regime, or composition-form error.

**Required action:** either add an ablation matrix—swelling amplitude, initial state, control law, composition operator, parameter source—or move Figure 4 to a diagnostic supplement. The current panel is honest but not a broad mechanism-discrimination result.

#### MAJ-32 — The pressure campaign is still one rig/coffee context

Within-campaign LOPO is valuable, but generalization beyond that apparatus and coffee remains untested. The manuscript acknowledges this in places.

**Required action:** frame the result as internal campaign generalization. A second rig, second coffee, or genuinely preregistered transfer set is needed for external validation.

---

### 6.4 Result 3 — exploratory N-tube concentration

#### MAJ-33 — The advertised conservation audit is not an audit over the trajectory

Inside the integrator, `w` is converted to `s = w / w.sum()`, so `s.sum()` equals one by construction. After the entire loop, the code computes:

```python
share_sum_dev = abs(s.sum() - 1.0)
min_share = s.min()
```

Those are final-step quantities. They are then named `share_sum_max_deviation` and `min_flow_share`, and the robustness wrapper interprets them as conservation/non-negativity “at every step.” This is a definite naming and logic error.

Moreover, normalized-share conservation is not the same as conservation of raw flow, mass, dissolved inventory, or tube age. Under fixed-flow control, mean relative flow is imposed by normalization; under pressure control it is not.

**Required action:** track at every substep:

- raw total/mean conductance and raw total flow implied by the control law;
- normalized share sum before and after any lateral operator;
- minimum raw flow, conductance, share, and age;
- cumulative age/throughput balance;
- any conserved or externally supplied total quantity.

Store true maxima/minima over the full trajectory and add tests that intentionally fail when a violation is injected.

#### MAJ-34 — The current sweep is not factorial

`ntube_robustness_study` varies one axis at a time around a baseline. It does not cross lateral coupling with control law, closure, timestep, N, grind, start state, and pressure. Calling it “factorial” is statistically incorrect and can hide interactions—the most important scientific possibility in this nonlinear model.

**Required action:** relabel as an OFAT sensitivity study, or execute a crossed design over at least control × lateral × closure with selected N/timestep/start-state levels. Report interactions and convergence separately.

#### MAJ-35 — Endpoint saturation is not numerical convergence

Figure 5b shows `N_eff final = 1` for every tested N and substep count. Once the system saturates at the lower bound, identical endpoints do not demonstrate that trajectories, collapse times, or peak/rebound behavior have converged.

**Required action:** report trajectory norms, collapse time, peak time, maximum share, and `N_eff(t)` differences against a finer reference. Show convergence rates or bounded errors. A flat endpoint-at-boundary plot is insufficient.

#### MAJ-36 — The early switching in Figure 5a requires investigation

The baseline trajectory shows abrupt collapse, rebound, and recollapse over the first fraction of normalized shot time, while the maximum single-tube share toggles correspondingly. This may be genuine dynamics, an effect of the near-zero conductance floor and explicit Euler stepping, or an interpolation/event-time artifact. The current normalized time axis conceals the physical timescale.

**Required action:** plot physical seconds; rerun with substantially smaller timesteps and a higher-order/adaptive integrator; inspect conductance and age around switching events; report whether event times converge. Do not describe the trajectory as robust until this is resolved.

#### MAJ-37 — Start-state and horizon dependence are acknowledged but not tested

The abstract says the result remains start-state-dependent; the body says start-time analysis is owed. The implemented sweep does not vary initial tube ages, initial porosity phase, prewetting, or horizon.

**Required action:** define a physically motivated family of initial states and horizons. Report concentration classification, collapse time, and terminal metrics across them. Until then use “start-state sensitivity is untested,” not “dependent” as an established result.

#### MAJ-38 — Four random seeds are inadequate for stochastic robustness

Four finite-network realizations can reveal gross failures but cannot characterize a stochastic distribution, particularly for extreme concentration driven by lognormal tails.

**Required action:** use enough independent realizations to estimate median and interval for `N_eff/N`, maximum share, and collapse time. Check tail-quantile sampling and compare stochastic draws with deterministic quadrature.

#### MAJ-39 — The pressure-range verdict is internally inconsistent

The actual sweep uses 6, 9, and 11 bar; the returned verdict says “6–12 bar.” The manuscript correctly says 6–11 bar. This is a small but definite code/documentation defect.

**Required action:** derive all range strings from the actual configuration and regression-test them.

#### MAJ-40 — The “endpoint_classification_invariant” summary mixes numerical and physical axes

The code aggregates poroelastic rows across N, timestep, grind, pressure, lateral, control, and stochastic realization, then asks whether every row concentrates. Because lateral and pressure-control cases deliberately do not concentrate, the overall flag is false. This is scientifically appropriate contingency, but the field name and surrounding language can be misread as failure of the numerical robustness claim.

**Required action:** export separate summaries:

- numerical convergence axes: N and timestep;
- stochastic realization;
- operating/design axes: grind and pressure;
- physical-model contingencies: control, lateral, closure;
- start state/horizon.

Do not collapse them into one invariance boolean.

#### MAJ-41 — N_eff should be normalized and supplemented

The robustness study uses N=400, while the floor sweep uses N=150. Thus CK values around 83 and 217 refer to different denominators. Absolute `N_eff` is not directly portable across N.

**Required action:** report `N_eff/N` alongside absolute `N_eff`, and add entropy, Gini, top-1/top-10% share, and collapse time. Harmonize N across floor and robustness sweeps or explicitly explain the differing purposes.

#### MAJ-42 — Figure 5d contains a wrong cross-reference

The annotation says measured `N_eff` is floor-independent “(panel c),” but panel c shows control-law/lateral sensitivity. No panel displays `N_eff` versus floor.

**Required action:** either plot the measured floor sweep directly in panel d or point to a supplementary table. Correct the cross-reference before any circulation.

#### MAJ-43 — The closed-form floor line is an imposed diagnostic, not independent validation

The poroelastic gain scales approximately as `1/floor` because the denominator is clipped by construction. Plotting that line usefully exposes singularity but does not validate the N-tube dynamics.

**Required action:** label it as an analytical diagnostic of the regularization, not evidence of physical gain or model stability. Keep numerical endpoint evidence separate.

#### MAJ-44 — The lateral term is a homogenization blend, not a physical exchange operator

The code explicitly describes lateral coupling as `w <- (1−λ)w + λ`, a proxy that blends relative flows toward uniformity. It has no spatial geometry, pressure field, conductance between neighboring tubes, or conservation law for transverse exchange.

**Required action:** avoid interpreting the λ threshold physically. A publishable stability/channel-interaction result needs a specified network or continuum exchange operator with parameters grounded in geometry and permeability.

#### MAJ-45 — The control-law contrast partly encodes the result by construction

Under fixed total flow, `w = g/mean(g)` forces tubes to share a fixed total, so a faster tube necessarily takes relative share from others. Under fixed pressure, `w = g/mean(g0)` allows total flow to change without that same renormalized competition. The contrast is a useful model diagnostic, but it is not experimental evidence that a real espresso machine occupies one idealized boundary condition.

**Required action:** present this as a boundary-condition sensitivity. Couple the bed to an explicit pump/headspace/control model before making practitioner-facing claims about real flow control versus pressure control.

#### MAJ-46 — Result 3 should remain supplementary until the conservation and convergence defects are corrected

The exploratory framing is now much better, but the current main-text prominence is disproportionate to the evidence. A simulated one-channel collapse under an algebraic coupling rule, with a final-step tautological conservation check and unresolved switching, should not carry equal evidentiary weight to the empirical sections.

**Required action:** move Result 3 to an exploratory supplement unless B3-13 through B3-17 are completed. The main text can retain a concise statement that the composition exhibits a potential concentration failure mode under a particular control/regularization choice.

---

## 7. Figure-by-figure review

### Figure 1 — Result 1: target and model capacity

**What works**

- The two grinder axes are explicitly separated, preventing a false direct dial mapping.
- The achieved-predictor vertex and interval are shown.
- Individual runs and cell means are both represented.
- The panel title correctly says “model capacity, not identification.”

**Required revisions**

1. Clarify whether the orange curve is an absolute refit or a shape-only recentering; its current placement on the absolute EY axis is ambiguous.
2. Add a conditional response band.
3. Increase visibility of individual runs and state that error bars are ±SD.
4. State that the endpoint is source-derived from fraction kinetics.
5. Move long interpretive text into the caption.
6. In panel b, disclose calibration and parameter uncertainty and show prominence on a scale that makes the small magnitude legible.
7. Consider a third compact panel showing closure-sensitivity rather than describing 10/25 combinations only in prose.

### Figure 2 — Evidence matrix

**What works**

- The figure is now data-driven rather than manually hard-coded in plotting code.
- The title warns that it is not a winner scoreboard.
- Missing decisive measurements are listed.

**Required revisions**

1. Replace internal abbreviations with reader-facing labels.
2. Add a legend/data dictionary defining every status and color.
3. Separate factual fields from evaluative judgments.
4. Include calibration/evaluation observables, parameter counts, and fit role in the source table even if the figure remains compressed.
5. Add citations or source identifiers per row.
6. Avoid a color progression that can be read as a scalar score.
7. Clarify that “static channeling” parameter provenance is calibrated and same-family rather than an independent unfit prediction.

### Figure 3 — Temporal ladder, cross-pressure comparison, and sign test

**What works**

- Panel a is labeled as a reproduced model curve, not measured data.
- Panel c explicitly says shared calibration and not LOPO.
- Panel d states the isolated fixed-pressure scope.
- The flexible temporal null is shown, limiting mechanism claims.

**Required revisions**

1. Replace all `0p` labels with “0 fit to Q(t).”
2. Overlay the source trace in panel a or remove empirical “reconstructs” language from that panel.
3. Add uncertainty and residual plots for panel b.
4. Show LOPO by pressure in panel c or an adjacent supplementary panel.
5. Remove “regime” language and show continuous error curves with uncertainty.
6. Define RC-3b and Φ(t) in the caption.
7. Reduce dense in-panel prose; it is unreadable at journal column width.
8. Distinguish sign-only inference from the transferred swelling magnitude in panel d.

### Figure 4 — Composition diagnostic

**What works**

- The figure openly reports a failed composition.
- It states that the result does not distinguish parameter-transfer, initial-state, control, or composition-form errors.
- The evaluation window and null are visible.

**Required revisions**

1. Add uncertainty or replicate variability for the observed trace.
2. Show at least one ablation, or move the figure to a supplement.
3. State all imported parameters and their source in the caption.
4. Avoid calling extraction-only equality a validation; it is an implementation identity.
5. Show residuals, because the visually small late differences can still be serially structured.

### Figure 5 — Exploratory N-tube result

**What works**

- The title explicitly says exploratory and contingent.
- The figure separates trajectory, numerical-axis endpoint checks, physical contingencies, and floor dependence.
- The floor-controlled nature of the closed-form gain is disclosed.

**Submission-blocking revisions**

1. Replace normalized shot time with physical time or show both.
2. Resolve the early collapse/rebound switching through timestep/integrator convergence.
3. Replace endpoint-only panel b with trajectory/collapse-time convergence.
4. Label the sweep OFAT, not factorial.
5. Plot `N_eff/N` as well as absolute `N_eff`.
6. Add stochastic uncertainty from substantially more realizations.
7. Plot measured `N_eff` versus floor; fix the incorrect “panel c” cross-reference.
8. Harmonize the N values used in floor and robustness sweeps.
9. Remove or correct any claim that conservation was checked at every step until the code actually tracks it.
10. Distinguish the algebraic lateral proxy from a physical exchange coefficient.

---

## 8. Code and data traceability audit

| Manuscript claim/result | Principal implementation path | Current traceability status |
|---|---|---|
| Selected central-cell means and contrasts | `result1_design_aware_stats` | Recomputable; should be bundled with source-derived outcome metadata |
| Achieved-predictor RSM vertex | `schmieder_rsm_refit(predictors="achieved")` | Numerically verified; interval conditional and bootstrap assumptions incomplete |
| RSM deletion/Q² diagnostics | `lopo_rsm_design_point` plus diagnostics | Partly implemented/reported; deletion ranges not frozen in bundle |
| Jensen deficit | `channeling_concavity_audit` | Implemented; post-clipping mean-preservation statement needs correction |
| Closure sensitivity | channeling sweep functions | Implemented; grid justification and source bundle needed |
| Evidence matrix | committed CSV + Figure 2 renderer | Data-driven; schema insufficiently documented |
| 9-bar temporal ladder | `kappa_t_ladder` | Recomputable; in-sample and strongly autocorrelated |
| Cross-pressure shared calibration | `cross_pressure_discrimination` | Distinct from LOPO; should be exported by pressure with full precision |
| Cross-pressure LOPO | `cross_pressure_loco` | Useful partial calibration test; figure does not show it |
| Residual autocorrelation | `residual_autocorr.summary` | Diagnostic exists; residual series/ACF not shown |
| Composition failure | shared-porosity composition path | One implementation diagnostic; no ablation |
| N-tube floor sweep | `ntube_finite_time_gain` | Reruns floors; N differs from robustness study |
| N-tube OFAT sweep | `ntube_robustness_study` | Axes added; mislabeled factorial; conservation audit defective |
| Figure generation | `puckworks/figures.py` | Figures mix bundled and live-computed analyses |
| Paper-wide reproducibility | `puckworks/paper_b/build.py`, results/manifest | Stale, dirty, incomplete |

### 8.1 Minimum release-manifest fields

The release manifest should contain at least:

- exact commit and clean-tree assertion;
- package/environment lock hash;
- all data and configuration hashes;
- random seeds and number of realizations;
- solver, interpolation, and optimizer tolerances;
- every figure/table output hash;
- a map from manuscript claim to bundle path;
- calibration/evaluation provenance for each parameter;
- runtime and platform information; and
- an explicit “slow analyses completed” flag, not inferred from cached files.

---

## 9. Required numerical reruns and acceptance tests

### 9.1 RSM release analysis

Run the following from a clean release checkout and store all outputs in the Paper B bundle:

1. achieved-predictor retained seven-term fit at experiment-7 achieved conditions;
2. centered/scaled equivalent fit with coefficient back-transformation check;
3. iid residual bootstrap, wild Rademacher bootstrap, and wild Mammen bootstrap;
4. full-quadratic sensitivity;
5. declared backward-elimination repeated inside resampling, if that procedure remains part of the inferential claim;
6. leave-one-run and leave-one-setting fits;
7. held-out experiment-ID predictions and Q²;
8. coefficient covariance/HC sensitivity, leverage, Cook's D, and standardized residuals; and
9. curve-level bootstrap bands.

**Acceptance tests**

- achieved center mask contains exactly experiment 7 and six runs;
- transformed and untransformed fits agree in predicted values and vertex to numerical tolerance;
- deletion results are finite, concave, and explicitly reported;
- bootstrap records the joint event “concave and in-domain,” not separate marginal percentages;
- all reported means/intervals are calculated before display rounding;
- figure and prose read the same bundle fields; and
- the manifest fails if any headline number differs outside a narrow, scientifically justified tolerance.

### 9.2 Jensen/channeling audit

**Required rerun**

For every grind/pressure/closure cell, export:

- untruncated lognormal mean;
- clipped/truncated weighted mean;
- clipped probability/quadrature mass by boundary;
- `EY(E[K_evaluated])`;
- `E[EY(K_evaluated)]`;
- direct gap and sign;
- numerical quadrature convergence; and
- support-boundary sensitivity.

**Acceptance test:** the sign conclusion must remain unchanged after comparing to the actual evaluated mean and after expanding the support/grid.

### 9.3 Temporal ladder and cross-pressure evaluation

**Required rerun**

- retain native and 1-s-decimated residual series;
- compute residual ACFs and block scales;
- vary evaluation windows, for example 10–90, 15–95, and 20–90 s, with a prespecified rationale;
- use blocked or rolling validation where fitting occurs;
- report shared-calibration and LOPO results separately by pressure;
- propagate replicate/measurement uncertainty if source data permit;
- add simple temporal nulls beyond a cubic only if they are evaluated fairly, such as splines with blocked validation or low-order state-space baselines; and
- report uncertainty on RMSE differences using whole-block or whole-pressure resampling rather than treating every time sample as independent.

**Acceptance test:** any claim that temporal flexibility “generalizes” must be supported by scoring data not used to fit that branch or its temporal parameters. Otherwise the manuscript must use “in-sample reconstruction.”

### 9.4 N-tube conservation and convergence rerun

At every substep, record:

- physical time;
- all raw conductances or their extrema and sum;
- raw total relative flow and its control-law target;
- normalized share sum;
- minimum raw and normalized flow;
- minimum conductance;
- age/throughput sum and expected control-law balance;
- `N_eff`, `N_eff/N`, maximum share, top-decile share, entropy, and Gini;
- the identity of the leading tube; and
- any clipping/floor event counts.

Run:

- N = 100, 200, 400, 800 and at least one larger reference;
- multiple timestep/integrator settings, including a higher-order or adaptive method;
- multiple horizons;
- multiple initial age/porosity/prewetting states;
- control × lateral × closure crossed combinations;
- pressure and grind sensitivity inside those crossed combinations; and
- enough stochastic realizations for intervals rather than four-point anecdotal robustness.

**Acceptance tests**

1. conservation metrics are extrema over the entire trajectory, not final values;
2. no negative conductance/flow/age occurs without being detected;
3. collapse time and trajectory norms converge as timestep decreases;
4. conclusions do not rely on a saturated endpoint alone;
5. floor sensitivity is shown for both analytical gain and numerical trajectory;
6. N=150 versus N=400 comparisons are normalized or harmonized;
7. pressure-range labels are generated from the configuration; and
8. the figure is rendered from the frozen robustness output.

### 9.5 Reproducibility release test

A clean CI job should:

```text
checkout release tag
create environment from lock
verify all input hashes
run all fast analyses
run/restore explicitly versioned slow analyses
write results bundle
render tables and vector figures from bundle
verify manuscript-number assertions
verify clean git tree
write release manifest
```

The build should fail on a dirty tree, stale cached bundle, missing slow result, untracked figure source, or mismatch between bundle and manuscript.

---

## 10. Suggested revisions to central claims

### 10.1 Suggested title

> **Limits of mechanism discrimination from integrated espresso measurements: matched observables, temporal nulls, and exploratory streamtube dynamics**

### 10.2 Suggested Result 1 summary

> In three selected nominal central-condition settings, source-derived TDS extraction-yield estimates increased from dial 1.4 to 2.0 and did not exhibit a middle-dial maximum. A response surface fitted across the full 15-setting design using achieved flow and temperature had a conditional concave grind cross-section with a vertex near dial 1.74. This vertex was stable to single-run and single-setting deletion and to a full-quadratic sensitivity, but its interval is conditional on the selected model and should be interpreted with heteroskedasticity-robust sensitivity. A calibrated static-heterogeneity model can generate a small interior maximum for some closure choices; this establishes model capacity, not mechanism identification.

### 10.3 Suggested Result 2 summary

> On the selected 15–95 s interval of the 9-bar campaign trace, all tested constant branches had substantially larger in-sample RMSE than either an empirical dissolution-linked trajectory or a four-coefficient cubic time curve. Because the cubic was fitted and scored on the same trace and residuals remained strongly autocorrelated, the result demonstrates the value of temporal flexibility for reconstruction within this campaign, not predictive validation or identification of a specific bed mechanism. Leave-one-pressure-out refitting shows that the two-parameter equilibrium calibration is not dominated by one pressure point, while the temporal donor trajectory and other assumptions remain fixed.

### 10.4 Suggested sign-constraint wording

> Under an imposed fixed-pressure boundary condition, an isolated branch whose sole effect is to increase hydraulic resistance cannot by itself generate a rising-flow contribution. The tested swelling parameterization and the cited monotone fines-migration branch therefore have the wrong isolated sign for this residual. This does not imply that swelling or fines migration is absent from a coupled machine–bed system.

### 10.5 Suggested Result 3 summary before additional validation

> An exploratory parallel-streamtube construction with extraction-dependent near-choke conductance develops strong concentration under the implemented fixed-total-flow, zero/low-homogenization boundary condition. The behavior is suppressed by pressure-control normalization, stronger algebraic homogenization, or a gentler conductance closure. Because the current lateral term is a proxy, the early trajectory has not yet been shown to converge, and the reported conservation check does not track the full integration, the result is a model failure-mode demonstration rather than evidence of physical instability.

### 10.6 Possible revised abstract

> Integrated espresso measurements can be reproduced by distinct combinations of extraction, hydraulics, and bed evolution. We evaluate what two focal empirical datasets can discriminate when observables, parameter provenance, and null models are made explicit. For a fraction-resolved extraction campaign, three selected nominal settings do not show a middle-dial maximum in source-derived TDS extraction yield, whereas a conditional response surface fitted across the full design has an interior grind vertex near dial 1.74. A calibrated static-heterogeneity model can generate a small peak for some closure choices, demonstrating capacity but not identifying channeling. For a pressure-series flow campaign, temporal trajectories greatly reduce in-window reconstruction error relative to constant baselines, but a flexible non-mechanistic time curve performs similarly and residuals remain strongly structured; the evidence therefore supports temporal flexibility rather than a unique bed mechanism. Under fixed pressure, isolated resistance-increasing swelling or fines branches have the wrong sign for a rising-flow contribution, while their presence in a coupled system is not excluded. An exploratory streamtube composition can concentrate flow under a near-choke, fixed-total-flow, low-homogenization implementation, but this behavior remains a numerical model diagnostic pending full conservation, convergence, and physical lateral-exchange validation. Across the tested data and model set, integrated observables constrain mechanisms without uniquely identifying them and motivate pathway-resolved flow, wetting-front, and independently measured bed-state data.

---

## 11. Section-by-section editorial comments

### Front matter and abstract

1. Remove “draft prose,” revision dates, review history, and “review-endorsed.”
2. Replace “two published datasets” with “two focal evaluation datasets plus donor/calibration sources.”
3. Avoid leading with the repository's prior aggregation error; move that provenance correction to Methods or a data-quality note.
4. Define TDS-derived EY on first use.
5. Replace “zero-free-parameter” with “zero coefficients fitted to the scored flow trace.”
6. Do not call floor independence “completed numerical robustness” until conservation and trajectory convergence are fixed.
7. Keep the final sentence focused on measurements that break the degeneracies.

### Introduction

8. Add a conventional literature review with complete citations rather than model-family shorthand.
9. Distinguish grinder dial, particle-size distribution, permeability, and pressure throughout.
10. State that the paper assesses a specified registry, not the full scientific hypothesis space.
11. Avoid novelty language until the related-work protocol is complete.
12. Explain why Result 1 and Result 2 belong in one paper beyond a general observability theme.

### Methods

13. Add governing equations for every branch used in a main figure.
14. Add a symbols/units table.
15. Add a parameter-provenance table with fit role and data source.
16. Define experimental units and replication separately for each source.
17. Define all evaluation windows and why they were selected.
18. Define the response-surface model, centering/scaling, selection, bootstrap, and deletion analyses.
19. Define the pressure LOPO split and what is held fixed.
20. Define the residual-dependence analysis and the limitations of pointwise RMSE.
21. Define the N-tube ODE, control laws, floors, clipping, interpolation, integrator, and lateral proxy.
22. State numerical tolerances and convergence criteria.
23. State which calculations are confirmatory, descriptive, sensitivity, or exploratory.

### Result 1

24. Use “source-derived run-level endpoint estimates.”
25. Make the selected-cell analysis and the full-design conditional surface visually and verbally distinct.
26. Report the wild-bootstrap sensitivity.
27. Report deletion ranges rather than saying they are owed.
28. Correct stale open-gap numbers to the exact bundle values.
29. Replace “exact Jensen gap” with the corrected evaluated-mean calculation.
30. Explain why the fixed closure grid was selected.
31. Avoid “mechanism discrimination” in the section heading.

### Result 2

32. Replace “zero-free-parameter.”
33. Put “in-sample” before the first RMSE ranking, not only later.
34. Show residual structure rather than only quote Durbin–Watson.
35. Avoid discrete regime language.
36. Show actual LOPO evidence.
37. Clearly separate the sign theorem-like argument from transferred numerical magnitude.
38. Keep composition failure explicitly implementation-specific.

### Result 3

39. Replace “factorial” with “one-factor-at-a-time” unless crossed interactions are run.
40. Remove the claim that conservation was checked at every step until corrected.
41. Resolve the panel-D cross-reference.
42. Replace “robust to every numerical and design choice tested” with a list of exactly tested axes and distinguish saturated endpoint invariance from trajectory convergence.
43. State that start-state/horizon sensitivity is untested.
44. Normalize `N_eff` when N differs.
45. Move to supplement pending conservation and switching analysis.

### Discussion and limitations

46. Make the limits of one-machine/one-coffee evidence prominent.
47. Separate “data cannot identify” from “implemented registry cannot identify.”
48. Do not infer real single-channel formation from simulated tube states.
49. Explicitly discuss donor-model transportability.
50. Discuss how source-derived endpoints and digitized traces affect uncertainty.
51. End with a concrete experimental program: spatial wetting/flow, first-drip timing, independent bed state, pressure/flow reversal, and second-rig transfer.

### Open gaps/status

52. Remove both sections from the submitted manuscript.
53. Preserve them in repository issue tracking or a contributor guide.
54. Correct stale numerical values before retaining them anywhere: current independent values are adjusted R² 0.6434, residual interval about [1.7007, 1.8188], Q² 0.4701, and leverage about 0.187 for the influential run.
55. Remove the statement that floor/N/timestep/pressure/grind sweeps are still owed when some have been run; list only unresolved start/horizon/conservation/physical-lateral issues.

---

## 12. Submission-readiness checklist

### Scientific and statistical

- [ ] Central claims distinguish capacity, reconstruction, transfer, incompatibility, and identification.
- [ ] Source-derived endpoints are described accurately.
- [ ] Achieved-predictor RSM is the single primary contract.
- [ ] RSM interval includes heteroskedasticity sensitivity.
- [ ] Post-selection conditionality is explicit or selection is repeated inside resampling.
- [ ] Deletion and full-quadratic sensitivities are frozen in the bundle.
- [ ] Jensen audit uses the actual evaluated mean after clipping.
- [ ] Temporal comparisons are either validated on held-out blocks/shots or labeled in-sample.
- [ ] Residual dependence is shown and reflected in uncertainty.
- [ ] Cross-pressure shared calibration and LOPO are both shown and correctly labeled.
- [ ] Sign constraints remain conditional on fixed-pressure isolated branches.
- [ ] Result 3 conservation is measured over all substeps.
- [ ] Result 3 trajectories/collapse times converge numerically.
- [ ] Start state and horizon are tested.
- [ ] OFAT versus factorial terminology is corrected.
- [ ] Stochastic uncertainty uses enough realizations.

### Reproducibility

- [ ] Release bundle commit equals release `HEAD`.
- [ ] Git tree is clean.
- [ ] All inputs and figure source data are hashed.
- [ ] Environment is locked.
- [ ] Seeds, tolerances, and solver settings are recorded.
- [ ] All figures consume the frozen bundle.
- [ ] Every manuscript number maps to a bundle path.
- [ ] Slow-analysis completion is explicit.
- [ ] Tests cover conservation-over-time and figure/source consistency.
- [ ] Vector figures and machine-readable source tables are included.

### Manuscript form

- [ ] Internal review narration removed.
- [ ] Full Methods added.
- [ ] Full References added.
- [ ] Captions self-contained.
- [ ] Data and Code Availability added.
- [ ] Limitations section added.
- [ ] Related-work search documented.
- [ ] Title and abstract do not overstate mechanism discrimination.
- [ ] Internal keys/abbreviations replaced or defined.
- [ ] Open-gap and status sections removed from manuscript body.

---

## 13. Supporting reference material

The references below support the review's source-design, mechanism-scope, and statistical-method comments. They should also form part of the manuscript's conventional reference list where relevant.

1. **Schmieder, B. K. L., Pannusch, V. B., Vannieuwenhuyse, L., Briesen, H., & Minceva, M. (2023).** “Influence of Flow Rate, Particle Size, and Temperature on Espresso Extraction Kinetics.” *Foods*, 12(15), 2871. DOI: [10.3390/foods12152871](https://doi.org/10.3390/foods12152871).  
   Relevance: establishes the 15-setting central composite design, three repetitions per setting and six at the center, ten collected fractions, analysis of selected fractions, run-level kinetic integration to cup component masses, and use of achieved flow/temperature in the source response surfaces.

2. **Waszkiewicz, R., Myck, F., Białas, Ł., Puciata-Mroczynska, M., Dzikowski, M., Szymczak, P., & Lisicki, M. (2026).** “Under pressure: Poroelastic regulation of flow in espresso brewing.” *Physics of Fluids*, 38, 063113. DOI: [10.1063/5.0319611](https://doi.org/10.1063/5.0319611).  
   Relevance: principal flow/TDS campaign, poroelastic interpretation, measurement repetition/uncertainty, model limitations at short times and lower pressures, and availability of supporting data/code.

3. **Foster, J., Lee, W., Moroney, K., Prjamkov, D., Salamon, M., Smith, A., Petrassem-de-Sousa, J., & Vynnycky, M. (2025).** “Dynamics of liquid infiltration into an espresso bed using time-resolved micro-computed tomography: Insights from experiment and modeling.” *Physics of Fluids*, 37, 013383. DOI: [10.1063/5.0245167](https://doi.org/10.1063/5.0245167).  
   Relevance: demonstrates time-resolved infiltration/wetting-front structure and supports the review's caution that integrated outlet flow can omit spatial saturation dynamics.

4. **Mo, C., Navarini, L., Suggi Liverani, F., & Ellero, M. (2022).** “Modeling swelling effects during coffee extraction with smoothed particle hydrodynamics.” *Physics of Fluids*, 34, 043104. DOI: [10.1063/5.0086897](https://doi.org/10.1063/5.0086897).  
   Relevance: treats swelling as a coupled intra-/inter-grain transport process and reports effects on extraction rate and beverage strength; it does not justify a general claim that swelling is absent whenever an isolated fixed-pressure resistance branch has the wrong net-flow sign.

5. **Lee, W. T., Smith, A., & Arshad, A. (2023).** “Uneven extraction in coffee brewing.” *Physics of Fluids*, 35, 054110. DOI: [10.1063/5.0138998](https://doi.org/10.1063/5.0138998).  
   Relevance: mechanism/model context for uneven extraction and the distinction between generating a fine-grind response and identifying its physical cause.

6. **Bengio, Y., & Grandvalet, Y. (2004).** “No Unbiased Estimator of the Variance of K-Fold Cross-Validation.” *Journal of Machine Learning Research*, 5, 1089–1105. [JMLR article](https://www.jmlr.org/papers/v5/grandvalet04a.html).  
   Relevance: emphasizes that uncertainty from overlapping cross-validation fits/errors is not obtained by naively treating fold errors as independent.

7. **Roberts, D. R., Bahn, V., Ciuti, S., et al. (2017).** “Cross-validation strategies for data with temporal, spatial, hierarchical, or phylogenetic structure.” *Ecography*, 40, 913–929. DOI: [10.1111/ecog.02881](https://doi.org/10.1111/ecog.02881).  
   Relevance: supports blocked/structured validation when observations have temporal or hierarchical dependence.

8. **Flachaire, E. (2005).** “Bootstrapping heteroskedastic regression models: wild bootstrap vs. pairs bootstrap.” *Computational Statistics & Data Analysis*, 49(2), 361–376. DOI: [10.1016/j.csda.2004.05.018](https://doi.org/10.1016/j.csda.2004.05.018).  
   Relevance: supports wild-bootstrap sensitivity when regression errors may be heteroskedastic.

9. **White, H. (1980).** “A heteroskedasticity-consistent covariance matrix estimator and a direct test for heteroskedasticity.” *Econometrica*, 48(4), 817–838. DOI: [10.2307/1912934](https://doi.org/10.2307/1912934).  
   Relevance: standard basis for heteroskedasticity-consistent regression covariance sensitivity.

10. **Hurvich, C. M., & Tsai, C.-L. (1989).** “Regression and time series model selection in small samples.” *Biometrika*, 76(2), 297–307. DOI: [10.1093/biomet/76.2.297](https://doi.org/10.1093/biomet/76.2.297).  
    Relevance: supports use and interpretation of AICc in small-sample model-form sensitivity, without eliminating post-selection uncertainty.

11. **Durbin, J., & Watson, G. S. (1950, 1951).** “Testing for serial correlation in least squares regression.” *Biometrika*, 37 and 38.  
    Relevance: foundation for the Durbin–Watson statistic; a near-zero value is a diagnostic of strong positive serial correlation, not a validation metric.

12. **Saltelli, A., Ratto, M., Andres, T., et al. (2008).** *Global Sensitivity Analysis: The Primer.* Wiley. DOI: [10.1002/9780470725184](https://doi.org/10.1002/9780470725184).  
    Relevance: supports distinguishing one-factor-at-a-time sensitivity from global/factorial interaction analysis in nonlinear models.

---

## 14. Overall recommendation

**Major revision before submission.**

The updated draft is much more scientifically disciplined than the earlier versions. The achieved-predictor RSM, corrected experimental-unit description, t-based interval, separated cross-pressure summaries, parameter-provenance table, conditional swelling/fines language, and exploratory framing of Result 3 are meaningful advances.

The paper's central methodological thesis is credible and potentially publishable. The remaining problems are not cosmetic, however. The current reproducibility bundle is stale and dirty; RSM uncertainty remains conditional and insufficiently robust to heteroskedasticity; Result 2 is an in-sample, strongly autocorrelated reconstruction; and Result 3's “conservation throughout” assertion is not supported by the implemented audit. The manuscript also remains visibly an internal review document.

A defensible next version should prioritize, in order:

1. a clean, complete, immutable Paper B build at the release commit;
2. heteroskedastic/post-selection sensitivity and frozen deletion diagnostics for Result 1;
3. dependence-aware or explicitly in-sample framing for Result 2, with visible residuals and actual LOPO evidence;
4. a genuine full-trajectory conservation and convergence audit for Result 3, with correction of the OFAT/factorial and Figure 5 issues; and
5. conversion to a conventional manuscript with complete methods, references, captions, and availability statements.

Until those actions are completed, the strongest safe conclusion is:

> The tested integrated observables constrain model capacity and reject some isolated implementations, but they do not uniquely identify an espresso-bed mechanism; the exploratory N-tube behavior motivates spatially resolved measurements and a better-coupled model rather than establishing physical instability.

