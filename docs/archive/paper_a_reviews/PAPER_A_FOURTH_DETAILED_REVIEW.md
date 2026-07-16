# Fourth detailed technical review of the updated `PAPER_A_DRAFT.md`

**Repository:** `trbrewer/puckworks`  
**Repository URL:** <https://github.com/trbrewer/puckworks>  
**Commit reviewed:** `e297f54169d9b975750b3773d02a639d1e2fbc85`  
**Commit title:** `paper-a: endpoint-mass sensitivity sweep, honest ~5pp caveat (A2-09)`  
**Draft revision stated in file:** 2026-07-12  
**Review date:** 2026-07-13  
**Review type:** fourth-round manuscript, all-figure, analysis-code, result-contract, provenance, and supporting-literature review  
**Overall recommendation:** **Major revision before journal submission**

**Pinned-artifact hashes used in this review**

| Artifact | SHA-256 |
|---|---|
| `docs/PAPER_A_DRAFT.md` | `0b0d05a7d66c1f3f3d606ad8b77fac91a81b2eba2d26ab5f1efab582518224c2` |
| `puckworks/figures_paper_a.py` | `02997f2966693cf9c91b1fbb818cfe64dde93b81e521caa5786582c562e1f770` |
| `puckworks/paper_a/build.py` | `e506f0fa278c10e0df41b9aa247657ec357a5fc55e3a18794ae9c50da624749a` |
| `puckworks/validation/slow/angeloni_bracket.py` | `1bc6581da623982e53108e33d2264e1786025cf2439bf29f1e84a10c39d9cf37` |

---

## 1. Executive assessment

The latest Paper A revision is materially stronger than the version assessed in the third review. It adds rate-grid-density and domain checks, a bounded continuous optimizer, an endpoint-volume sensitivity sweep, a flow-map magnitude sweep, a same-model discrepancy control, additional residual diagnostics, source-data exports, and a nominal paper-build/manifest layer. The manuscript also uses a more careful evidence vocabulary than the earliest drafts: the O-to-C/F comparison is described as a within-campaign holdout, the joint fit as in-sample compatibility, Table 7 as a same-campaign orthogonal measurement, and the Waszkiewicz result as target-level-profiled external-data objective localization rather than a frozen absolute-concentration prediction.

The central qualitative claim remains scientifically plausible: under the tested single-grind, whole-cup observation map, inventory and rate occupy a broad compensating profile, whereas time-resolved observations produce a more localized rate objective. The manuscript is also right to emphasize that parameter localization and prediction quality are different questions.

The current revision nevertheless remains unsuitable for submission for five principal reasons.

1. **The committed provenance package does not certify the current manuscript.** The repository head reviewed here is `e297f541...`, while the committed Paper A manifest records `source_commit = bc8c8733...`, `bundle_source_commit = 838f397f...`, and `git_dirty = true`, yet sets `verified = true`. The verifier checks 18 bundle fields against duplicated hard-coded expected numbers; it does not fail on a dirty tree, source/bundle/head mismatch, manuscript drift, figure drift, incomplete source-data export, or missing environment lock. The “18/18” status therefore cannot be interpreted as a reproducible release certification.

2. **The principal transfer claim still lacks a baseline.** A simple level-only benchmark calculated in the previous round nearly reproduces the reported O-to-C/F error: approximately 8.59% macro-MAPE for an O-trained constant versus approximately 8.23% for the mechanistic transfer, a difference of only 0.36 percentage points using the rounded model scores available. The model was worse than the constant in 5 of 12 variety × solute × held-out-grind cases. No current code path, figure, source-data table, or manuscript paragraph resolves this. Absolute MAPE alone therefore still does not establish useful mechanistic transfer skill.

3. **The new endpoint sensitivity addresses the wrong estimand for the headline transfer claim.** `endpoint_mass_sensitivity()` reruns the blind per-condition O-grind comparison at 38/40/42 mL. It does not refit O and re-predict C/F at each endpoint, does not include the near-optimal profile set, and checks the caffeine/trigonelline sign pattern only in Arabica. It supports a limited caveat about a blind residual, not robustness of the main frozen O-to-C/F transfer result.

4. **The figure package is internally inconsistent and two figures overclaim.** The repository contains and renders eight figures, but the manuscript and figure README declare and describe only six. Source data are missing for Figures 3 and 4 and for several central profile/envelope/external analyses. Figure 4 labels transfer “reasonable” without showing a baseline, profile-wise uncertainty, or endpoint sensitivity. Figure 8 states that group-specific negative offsets are something a pure inventory level rescale cannot remove, but the model fits a separate level for each variety × solute group; such a level can remove a group intercept. What it cannot remove is residual within-group dependence on temperature, pressure, or grind after level fitting. Figure 8 plots only blind pre-level-fit residuals and therefore cannot support its title.

5. **Several numerical summaries still aggregate rounded values.** The blind per-condition mean averages already rounded group MAPEs; the endpoint sweep inherits those rounded means; the refit headline averages rounded per-fit holdout values; the independent-fit comparator in the joint analysis is formed from rounded entries; and the geometry sweep rounds each held-out MAPE to the nearest whole percentage point before computing its spread. The reported approximately 1-point geometry sensitivity, 4.9% independent comparator, endpoint spread, and related derived quantities must be regenerated from full-precision arrays.

The paper’s strongest defensible conclusion at present is narrower than its abstract and Discussion:

> Within the tested model, datasets, assumed flow/geometry maps, endpoint operator, parameter domain, and descriptive objective thresholds, single-grind whole-cup concentration data leave inventory and kinetic rate weakly separated. Time-resolved fraction data produce a more localized rate objective. The selected O-grind calibration yields modest absolute C/F errors, but incremental predictive skill over level-only baselines and robustness of the full profile-wise transfer to endpoint uncertainty have not yet been established.

That is a worthwhile result. The paper should be revised around it rather than preserving the stronger “transfers reasonably along the entire manifold” narrative before the necessary controls are run.

---

## 2. Scope, reviewed materials, and review method

### 2.1 Repository materials reviewed

The review was pinned to commit `e297f54169d9b975750b3773d02a639d1e2fbc85` and covered:

- `docs/PAPER_A_DRAFT.md`;
- all eight committed Paper A figures:
  - `fig1_design.png`;
  - `fig2_objective_surface.png`;
  - `fig3_holdouts.png`;
  - `fig4_transfer.png`;
  - `fig5_joint_residual.png`;
  - `fig6_fraction_vs_endpoint.png`;
  - `fig7_per_group_diagnostics.png`;
  - `fig8_residuals_vs_conditions.png`;
- `puckworks/figures_paper_a.py`;
- `puckworks/paper_a/build.py`;
- `puckworks/validation/slow/angeloni_bracket.py`;
- the identifiability and external-Waszkiewicz slow-analysis paths;
- `tests/test_paper_a.py`;
- the committed `results.json`, Paper A manifest, figure README, and source-data directory;
- the previous detailed Paper A review, to determine which findings were resolved, partially resolved, or unchanged.

### 2.2 Supporting primary references checked

The factual source-study descriptions and methodological interpretation were checked against, among others:

- Schmieder et al. (2023), *Foods* 12, 2871, <https://doi.org/10.3390/foods12152871>;
- Angeloni et al. (2023), *Applied Sciences* 13, 2688, <https://doi.org/10.3390/app13042688>;
- Pannusch et al. (2024), *Journal of Food Engineering* 367, 111887, <https://doi.org/10.1016/j.jfoodeng.2023.111887>;
- Waszkiewicz et al. (2026), *Physics of Fluids* 38, 063113, <https://doi.org/10.1063/5.0319611>;
- Raue et al. (2009), *Bioinformatics* 25, 1923–1929, <https://doi.org/10.1093/bioinformatics/btp358>;
- Wieland et al. (2021), *Current Opinion in Systems Biology* 25, 60–69, <https://doi.org/10.1016/j.coisb.2021.03.005>;
- Simpson and Maclaren (2023), *PLoS Computational Biology* 19, e1011515, <https://doi.org/10.1371/journal.pcbi.1011515>;
- Bengio and Grandvalet (2004), *Journal of Machine Learning Research* 5, 1089–1105, <https://www.jmlr.org/papers/v5/grandvalet04a.html>.

Schmieder reports a 15-setting face-centered design, generally with three repetitions and six at the center, and ten consecutive fractions; the repository’s Pannusch port uses a derived six-window subset. The distinction matters when the paper calls a six-window weighted aggregate a cup. Profile-analysis literature supports distinguishing an interior numerical optimum from a profile region that remains open at a tested boundary, and supports propagating parameter-profile sets into prediction sets. It does not turn an arbitrary 10%-of-minimum objective threshold into a confidence region without a likelihood/noise model. Cross-validation literature likewise supports the manuscript’s decision to call its resampled LOCO intervals descriptive: fold errors from overlapping training sets are dependent.

### 2.3 Review method

The review combined:

1. **Claim-to-code tracing.** Headline statements were traced to functions, fields, aggregation order, rounding, and plotting paths.
2. **Figure inspection.** Every figure was checked for units, plotted evidence, title/caption claims, missing uncertainty, baselines, boundary flags, and consistency with the manuscript.
3. **Reproducibility-contract inspection.** The current head, bundle source commit, manifest source commit, dirty flag, claim verifier, data hashes, and source-data exports were compared.
4. **Targeted numerical diagnostics.** The previously computed level-only benchmark was retained because no current change adds a competing baseline or exports full-precision predictions needed to supersede it.
5. **Literature-grounded interpretation.** Identifiability, profile boundaries, prediction propagation, and cross-validation uncertainty were assessed using primary methodological sources.

### 2.4 Limitations of this review

I did not perform a clean-room rerun of every slow PDE analysis in a newly provisioned, fully pinned environment. The repository does not yet provide a clean, self-consistent release artifact that would make such a rerun auditable. Definite code, manuscript, figure, and manifest inconsistencies are identified directly. Numerical robustness questions are stated as required reruns with acceptance criteria. The constant-baseline comparison uses the committed data and rounded mechanistic scores available in the previous review; exact differences should be regenerated from exported full-precision point predictions.

---

## 3. What has improved since the previous Paper A review

| Previous concern | Current status | Review comment |
|---|---|---|
| Coarse rate-grid and untested profile domain | **Partly improved** | Grid-density/domain checks and a continuous bounded optimizer were added. The tolerance region still reaches the upper boundary, and the Hessian sensitivity to the inventory grid, finite-difference step, and scaling is not shown. |
| Endpoint 40 g versus 40 mL approximation ignored | **Partly improved** | A 38/40/42 mL blind-residual sweep now reports a ~5.3-point spread and a sign flip. It does not rerun the main O-to-C/F transfer estimand and still equates grams with milliliters rather than propagating density. |
| Constructed pressure–flow map had no sensitivity check | **Partly improved** | A ±20% global magnitude sweep was added. It is one Arabica/caffeine representative and does not test map form, condition-specific errors, or measured flow. |
| Same-model exact-cup result had no discrepancy control | **Improved, but not integrated** | Moderate and large synthetic discrepancy controls are in the result bundle and tests. They are not shown in Figure 6 or reported with enough detail in the paper’s core evidence chain. |
| Figure 6 showed one seed | **Partly improved** | An exact-cup ±1 SD band over 20 seeds was added. The fraction-simulation band, discrepancy trajectories, and external Waszkiewicz profile remain absent. |
| Per-group/residual diagnostics absent | **Added, but overinterpreted** | Figures 7 and 8 now exist. They are omitted from the manuscript’s figure list; Figure 7 mislabels cross-condition correlation as trajectory shape; Figure 8’s central causal claim is logically invalid for group-specific fitted levels. |
| Source data absent | **Partly improved** | Seven CSVs are exported for parts of Figures 2, 5, 6, 7, and 8. Figures 3 and 4, profile-wise transfer envelopes, baselines, Waszkiewicz, discrepancy controls, and several surface fields remain unexported. |
| No strict build/manifest | **Added, but currently non-certifying** | A verifier and manifest exist. The current manifest is stale, dirty, and tied to an older bundle, while `verified=true`; the check duplicates selected expected numbers rather than verifying the manuscript/figures/release. |
| No full-precision aggregation | **Not resolved** | Several important paths still round before averaging or before computing ranges. |
| No level-only benchmark | **Not resolved** | The central predictive-transfer conclusion remains unbenchmarked. |
| “Whole manifold” overstatement | **Not resolved** | The transfer set remains a finite subset of a coarse MAPE grid under an arbitrary relative threshold, with aggregate scores only. |
| Submission manuscript conversion | **Not resolved** | Repository notes, review IDs, function names, open-gap ledgers, “owed” actions, and missing conventional declarations remain. |

---

## 4. Independent benchmark diagnostic retained from the previous review

### 4.1 Why the benchmark remains submission-blocking

The model fits a separate multiplicative inventory level for each variety × solute group. A low MAPE can therefore arise mainly from getting the group level approximately right, even if the model contributes little temperature-, pressure-, or grind-dependent predictive structure. Figures 3 and 4 visibly show narrow horizontal prediction bands within several groups. The manuscript needs a baseline that asks whether the mechanistic response improves prediction beyond that level.

No current commit adds such a baseline. The earlier diagnostic therefore remains directly relevant.

### 4.2 Baselines evaluated

- **O-trained MAPE-optimal constant:** one constant per variety × solute fitted on the nine O conditions with the same MAPE logic, then frozen for C and F.
- **Same-(T,p) O lookup:** observed O concentration at the same condition used as a nonmechanistic cross-grind reference.
- **Shared all-grind constant:** one constant per variety × solute fit to O+C+F, compared with the in-sample shared mechanistic fit.
- **Independent per-grind constants:** one constant per variety × solute × grind, compared with independent per-grind mechanistic fits.

### 4.3 Headline diagnostic

| Comparison | Mechanistic MAPE | Simple baseline MAPE | Difference favoring mechanism | Reading |
|---|---:|---:|---:|---|
| O-trained → C/F macro, 12 fit×grind cases | **8.23%** | **8.59%** | **0.36 pp** | Very small incremental skill |
| Held-out C only | **10.30%** | **11.25%** | **0.95 pp** | Modest improvement |
| Held-out F only | **6.16%** | **5.93%** | **−0.23 pp** | Constant slightly better |
| O-trained → C/F macro versus same-(T,p) O lookup | **8.23%** | **10.79%** | **2.57 pp** | Better than this noisier lookup |
| Joint O+C+F, in sample | **6.40%** | **7.11%** | **0.71 pp** | Small in-sample gain |
| Independent per-grind, in sample | **4.90%** | **5.05%** | **0.15 pp** | Essentially tied at displayed precision |

The mechanistic transfer was worse than the O-trained constant in **5 of 12** variety × solute × held-out-grind cases.

### 4.4 Per-case diagnostic

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

Negative differences favor the mechanistic model; positive differences favor the constant. These values are diagnostic because the repository still does not export every full-precision model prediction. They nevertheless establish the required next analysis: report model-versus-baseline paired loss differences and skill, not only absolute MAPE.

---
## 5. Prioritized required-action matrix

### 5.1 Submission-blocking actions

| ID | Priority | Finding | Required action | Acceptance criterion |
|---|---:|---|---|---|
| **A4-01** | **P0** | Manifest, bundle, and repository head do not match; tree is dirty but `verified=true` | Recompute on a clean checkout; require `HEAD == manifest.source_commit == bundle.source_commit`; fail on dirty state; stamp non-null UTC time | Clean full build exits zero only when all three commits match, tree is clean, and every output hash is current |
| **A4-02** | **P0** | Build verifies duplicated hard-coded expected values, not the manuscript and figures | Generate a single machine-readable result table and inject/validate manuscript tables, captions, and figure annotations from it; eliminate duplicated expected values or parse the manuscript contract | Editing a manuscript number, figure annotation, bundle value, or result table causes the build to fail |
| **A4-03** | **P0** | Mechanistic transfer is almost matched by a level-only constant | Add predeclared O-trained constant, condition-mean, same-(T,p) O, and reduced-mechanistic baselines; report skill and paired loss differences from full-precision points | The claimed predictive benefit is quantified against baselines with condition-wise uncertainty, or “reasonable transfer” language is removed |
| **A4-04** | **P0** | Endpoint sweep does not test the main O→C/F estimand | For each endpoint/density scenario, refit O, transfer the selected point and profile set to C/F, and compare with baselines | Main transfer MAPE, skill, worst-case profile error, and conclusions are reported over the endpoint uncertainty range |
| **A4-05** | **P0** | Grams are treated as milliliters under an unsupported density range | Implement mass-consistent stopping or propagate measured/justified density and crema/volume uncertainty; rename current operator “40 mL proxy” | Primary labels accurately state mass or volume; density assumptions and uncertainty are traceable and propagated |
| **A4-06** | **P0** | Round-before-aggregate defects affect several headlines | Retain full precision through all fits, means, spreads, and differences; round once in presentation | Regression tests fail if rounded fields enter any aggregate; all affected numbers are regenerated |
| **A4-07** | **P0** | “Entire near-optimal manifold” is a finite coarse MAPE-grid subset | Construct a continuous or demonstrably converged profile-wise prediction set, justify the threshold, and export condition-level envelopes | Prediction envelopes and error summaries are stable to rate grid, domain, interpolation, and threshold; wording reflects a set, not an entire manifold |
| **A4-08** | **P0** | Figure 8’s title makes an invalid inference about fitted levels | Replace blind-only causal interpretation with post-level-fit residual analysis, group-centering, slopes, and uncertainty | Figure shows what remains after each group-specific level fit; title/caption make no claim contradicted by the model parameterization |
| **A4-09** | **P0** | Figure and manuscript packages disagree: eight rendered, six listed | Choose final figure set; synchronize manuscript, README, renderer, build, source data, and captions | One enumerated list matches all committed outputs; no orphaned or undocumented figures remain |
| **A4-10** | **P0** | Figures 3/4 and central analyses lack source data | Export tidy, full-precision data for every panel, including baseline predictions, profile envelopes, external profile, and discrepancy controls | Every plotted mark and band can be regenerated from documented source tables without running the PDE stack |
| **A4-11** | **P0** | Figure 4 does not display the evidence underlying its title | Add baseline, profile-wise bands, point predictions, endpoint sensitivity, and neutral labels | Figure permits visual assessment of incremental skill and profile/endpoint uncertainty; title states quantities rather than verdicts |
| **A4-12** | **P0** | Figure 2 omits the MAPE cross-check and right-censoring | Plot SSE and MAPE profiles or provide a paired supplement; mark open boundary and continuous optimum | Reader can see objective dependence, interior optimum, and open tolerance region directly |
| **A4-13** | **P0** | Abstract and Discussion claim predictive stability before baseline/endpoint/profile controls | Rewrite headline claims provisionally and update only after A4-03/04/07 | Abstract distinguishes absolute error from skill and avoids “entire manifold,” “reasonably,” and “does transfer” unless supported |
| **A4-14** | **P0** | Current document is an internal handoff, not a journal manuscript | Remove repository note, review IDs, backlog/open-gap ledger, function names as prose, and “owed” statements; add conventional sections and declarations | Submission file is self-contained, journal-formatted, and contains no internal project-management language |
| **A4-15** | **P0** | No clean frozen release/environment supports the numerical claims | Tag a release, pin dependencies, record platform/solver settings and random seeds, and archive outputs | A fresh environment reproduces all tables/figures and exact result hashes within declared deterministic tolerances |

### 5.2 Major analytical actions

| ID | Priority | Finding | Required action | Acceptance criterion |
|---|---:|---|---|---|
| **A4-16** | P1 | Interior optimum and open tolerance region are conflated | State: “the numerical optimum is interior; the 10%-tolerance region is right-censored” | No statement says “no bounded minimum” or “not an interior estimate” when the optimizer found an interior minimum |
| **A4-17** | P1 | Hessian robustness is incomplete | Vary inventory grid, rate grid, finite-difference step, log scaling, solver tolerances, and local fit window | Condition number/coupling are reported with sensitivity ranges; no categorical inference rests on one discretization |
| **A4-18** | P1 | MAPE “agreement” criterion only requires two profiles to be broadly flat | Quantify optimum difference, set overlap/Jaccard, profile correlation, and boundary status | “Agrees” has a declared numerical criterion and is shown per solute/variety |
| **A4-19** | P1 | Objective threshold is descriptive but rhetorically resembles uncertainty | Add likelihood/noise-model analysis or explicitly retain multiple descriptive thresholds | No confidence/probability interpretation is implied; conclusions are stable over declared thresholds |
| **A4-20** | P1 | Table 7 line is visual, not a quantitative constraint | Intersect inventory estimate/uncertainty with the profile path and derive implied rate set | Manuscript reports the resulting rate interval/set and same-campaign dependence |
| **A4-21** | P1 | Joint-fit adequacy lacks a null ladder and predeclared criterion | Compare shared mechanistic, shared constant, per-grind constant, and independent mechanistic models | “Compatibility” is tied to predeclared error/skill and complexity, not only a 1.5-point difference |
| **A4-22** | P1 | LOCO intervals resample already-computed dependent fold errors | Keep strictly descriptive or implement repeated-fit bootstrap/hierarchical resampling matching the target | No coverage language unless validated; paired baseline differences are repeated inside each resample |
| **A4-23** | P1 | Flow sensitivity varies only global magnitude for one representative group | Sweep all named solutes/varieties and plausible map forms; include condition-specific or measured-flow alternatives | Robustness conclusion is supported across the full headline population and map-form uncertainty |
| **A4-24** | P1 | Geometry sweep is global, not a grind-specific geometry map | Test plausible O/C/F geometry combinations or narrow wording to global-geometry sensitivity | No inference that cross-grind geometry uncertainty is resolved by a global choice sweep |
| **A4-25** | P1 | Measurement uncertainty is disclosed but not propagated | Use replicate/RSD information where available; perform heteroscedastic or weighted sensitivity | Profile, baseline skill, and transfer conclusions are reported under plausible measurement-error models |
| **A4-26** | P1 | All-solute/all-variety identifiability support is absent | Produce supplementary SSE/MAPE profiles and boundary flags for every named-solute × variety group | Headline practical-confounding claim is representative, not selected from caffeine/trigonelline Arabica |
| **A4-27** | P1 | Same-model simulation uses on-grid truth and a finite candidate set | Repeat with off-grid truths, continuous optimization, multiple noise levels, and solver-resolution checks | Rate recovery and fraction/cup contrast are not candidate-grid artifacts |
| **A4-28** | P1 | Discrepancy controls are not integrated into figures or conclusions | Plot moderate/large discrepancy profiles and report localization bias and irreducible floor | The paper makes clear that a sharp objective can localize the wrong physical rate under misspecification |
| **A4-29** | P1 | Empirical six-window aggregate is called against an “actual cup” with ambiguous provenance | Explain that cup quantities are derived/integrated in the source workflow and document experiment matching | Terminology distinguishes measured fractions, derived six-window aggregate, source cup response, and simulated exact integral |
| **A4-30** | P1 | Waszkiewicz remains one coffee, one grind, target-profiled level, high MAPE | Keep as external shape-objective localization; expand nuisance/operator sensitivity and show the profile | No named-solute or frozen-concentration generalization; figure/table displays minimum, flatness, and sensitivity |
| **A4-31** | P1 | Figure 7 uses “trajectory” for nine operating conditions | Rename as cross-condition response-pattern correlation; add uncertainty and post-level residual metrics | Labels correctly identify the axis of variation and do not imply temporal data |
| **A4-32** | P1 | Aggregate-solids proxies are mixed visually with named solutes | Separate proxy panels or clearly label them as non-equivalent observables | No pooled color/legend treatment implies common analyte identity across campaigns |
| **A4-33** | P1 | Code verdict strings contradict manuscript taxonomy | Replace free-text verdicts with structured evidence metadata and neutral quantities | Automated test rejects stale terms such as “REAL transfer,” “external stress,” “robust,” and “works” in manuscript-facing outputs |
| **A4-34** | P1 | Manifest hashes only six data files | Hash all direct inputs, code modules, manuscript, environment lock, result bundle, source tables, and figures | Manifest provides a complete auditable dependency/output inventory |
| **A4-35** | P1 | Tests accept stale/dirty bundles | Add tests for commit equality, clean tree, figure count, source-data completeness, precision retention, and baseline calculation | Current e297/bc8/838 mismatch would fail automatically |

### 5.3 Presentation and reporting actions

| ID | Priority | Finding | Required action | Acceptance criterion |
|---|---:|---|---|---|
| **A4-36** | P2 | Figure titles embed subjective conclusions | Use neutral titles; move interpretation to Results/Discussion | Titles report design and quantities, not “works,” “reasonable,” “robust,” or “cannot remove” |
| **A4-37** | P2 | Figures are committed only as raster PNGs | Export vector PDF/SVG and publication-resolution PNG | Journal-ready vector outputs reproduce from the same source tables/bundle |
| **A4-38** | P2 | Captions are not self-contained | Add sample sizes, train/test split, objective, fitted parameters, endpoint operator, uncertainty meaning, and evidence tier | Each figure can be understood without code or repository context |
| **A4-39** | P2 | Methods are described mainly by function names | Add equations, parameter tables, numerical solver details, fitting algorithm, domains, tolerances, and aggregation definitions | A reader can reproduce the analysis without reading Python source |
| **A4-40** | P2 | Literature section is a project scoping note | Complete and archive the search; make novelty wording proportionate; provide a full bibliography | No “run at submission” placeholder remains; every citation is in the references list |
| **A4-41** | P2 | No conventional data/code availability or ethics/conflict declarations | Add journal-required declarations | Submission package meets target-journal checklist |
| **A4-42** | P2 | Terminology alternates among matched mass, 40 g, 40 mL, endpoint, and cup | Define one primary operator and use it consistently | Every table, axis, title, and paragraph states the same endpoint quantity and units |

---
## 6. Detailed major comments

### 6.1 The current manifest is self-inconsistent and cannot certify the reviewed state

At the reviewed head, `docs/reproducibility/paper_a_manifest.json` records:

- `source_commit = bc8c87330ab8dea507ecc27dc8935dde4d72bbf9`;
- `bundle_source_commit = 838f397f35b09462372b471432653fd7937200ee`;
- `git_dirty = true`;
- `n_claims = 18`;
- `n_failures = 0`;
- `verified = true`.

The repository head is `e297f54169d9b975750b3773d02a639d1e2fbc85`. These are three different commit identities. A result bundle from one commit, a manifest generated from another, and a manuscript/figure tree at a third cannot be treated as one reproducible artifact. The dirty flag further means the manifest was generated from content that may not correspond to any commit.

This is not a cosmetic provenance issue. The latest commit changes the endpoint analysis, bundle, manifest, manuscript, build claim, and tests. A reader cannot tell which code produced the numbers now displayed in the manuscript and figures.

**Required action:** make commit equality and clean status build invariants. A release build must fail before claim checking when the tree is dirty or when `HEAD`, `bundle_source_commit`, and the manifest source commit differ.

### 6.2 The verifier does not verify the manuscript

`puckworks/paper_a/build.py` defines 18 claim labels, expected numbers, bundle paths, and tolerances in `_CLAIMS`. `verify()` checks the current bundle fields against those hard-coded expected numbers. It does not parse or generate `PAPER_A_DRAFT.md`, tables, figure titles, or captions. Consequently:

- the manuscript can change while the build continues to pass;
- a figure annotation can drift while the build continues to pass;
- an omitted or contradicted claim can pass because only the duplicated Python value is checked;
- stale bundle/source commits can pass;
- a dirty working tree can pass.

The phrase “single source of truth” is therefore not yet accurate. There are at least three sources: bundle values, hard-coded expected values, and prose/figure text.

**Required action:** use one results schema to generate manuscript-facing tables/annotations or validate them mechanically. At minimum, generate an intermediate `paper_a_claims.json` and render both prose tables and figures from it, with hashes checked by the build.

### 6.3 The claimed release check is tolerant enough to hide meaningful drift

Several tolerances are broad relative to the scientific claims: for example, a profile fraction expected at 0.76 is accepted over a ±0.06 interval, the worst transfer error near 21.7 is accepted within ±2 percentage points, and the endpoint spread 5.3 is accepted within ±1.5 points. Tolerances may be appropriate for numerical nondeterminism, but the code does not demonstrate that such nondeterminism exists at those magnitudes or distinguish numerical tolerance from scientific equivalence.

A claim can therefore move materially while the build remains green. Conversely, deterministic cached results should often reproduce exactly under a pinned environment.

**Required action:** empirically characterize rerun variability, use exact checks for deterministic post-processing, and reserve narrow tolerances only for demonstrated solver/platform variation. Report both absolute drift and declared reason.

### 6.4 The figure count and documentation are inconsistent in four places

The renderer returns eight figures. The repository directory contains eight. The manuscript’s Figure section says “Six figures” and lists only Figures 1–6. The figure README likewise says “Six figures,” lists only 1–6, and describes render as drawing the six figures. The build docstring also says it redraws six.

Figures 7 and 8 therefore have no manuscript captions, no placement, no cross-reference, and no explanation of how they alter the evidence chain. This is especially serious because both figures make interpretive claims, not merely supplementary displays.

**Required action:** decide whether Figures 7–8 are main, supplementary, or removed. Synchronize numbering, file names, captions, README, renderer, build documentation, manuscript references, and source-data list in one commit.

### 6.5 The source-data export is incomplete despite a “one CSV per figure series” claim

The committed `source_data/` directory contains seven files:

- two Figure 2 profile tables;
- one Figure 5 table;
- three Figure 6 profile tables;
- one combined Figure 7/8 residual table.

There is no source table for Figure 3’s LOCO points or Figure 4’s O-to-C/F predictions. There is no full Figure 2 objective surface, MAPE profile, Table 7 uncertainty, or boundary flag. There is no profile-wise transfer envelope, no constant baseline, no endpoint-sensitivity table linked to Figure 4, no external Waszkiewicz profile, and no discrepancy-control data linked to Figure 6.

The existing Figure 7/8 table is also limited to the blind and matched residuals surfaced by the per-condition path and does not provide the post-fit diagnostics needed to support Figure 8’s claim.

**Required action:** export full-precision tidy data for every plotted mark and central table, with units, data source, evidence tier, train/test role, endpoint operator, and result-bundle hash in metadata.

### 6.6 The transfer result still lacks incremental-skill evidence

The manuscript repeatedly says the O calibration “predicts the other grinds well,” “transfers reasonably,” and remains “reasonably stable” along the compensating set. These statements are based on absolute error. The retained diagnostic shows that a constant concentration trained on O yields nearly the same C/F macro-MAPE and is slightly better on F in aggregate.

The question is not whether 8% is intuitively “low”; it is whether the model extracts held-out condition/grind signal beyond a level-only reference. The current plots make the concern visible: several prediction clusters are nearly horizontal while observations vary.

**Required action:** add paired point-level comparisons against a predeclared baseline hierarchy. Report:

- model and baseline loss by variety, solute, grind, and condition;
- `skill = 1 - loss_model/loss_baseline` with a clear loss definition;
- distribution of paired absolute-percent-error differences;
- macro and micro averaging separately;
- whether the model predicts temperature/pressure contrasts, not only group levels;
- profile-wise and endpoint-sensitivity skill, not only point-optimum skill.

### 6.7 Figure 4 prejudges the unresolved baseline question

Figure 4’s title says the model “transfers reasonably” and is “≤1 pp geometry-sensitive.” The panels show only observed versus point predictions for C and F. They do not show:

- any baseline;
- the near-optimal-set envelope;
- endpoint uncertainty;
- geometry alternatives;
- flow-map alternatives;
- paired loss differences;
- a declared performance threshold.

The title therefore contains two conclusions not demonstrated in the figure. The geometry value is particularly problematic because the underlying routine rounds each case to an integer before measuring the spread.

**Required action:** use a neutral title such as “Frozen O-calibrated predictions for held-out C and F conditions.” Add baseline symbols/lines, condition-wise profile envelopes, endpoint scenarios, and a small skill panel. Put geometry sensitivity in a separate properly computed panel or table.

### 6.8 The endpoint sensitivity analysis does not test the central transfer result

`endpoint_mass_sensitivity()` calls `gate_pannusch_angeloni_per_condition(v_target=v)` for 38, 40, and 42 mL. That function evaluates the blind Pannusch-to-Angeloni O-grind comparison; it does not refit the Angeloni O calibration and freeze it for C/F. The function then checks two sign booleans only for Arabica caffeine and trigonelline.

The manuscript uses this to support language about the residual and then elsewhere continues to describe matched 40 g cross-grind transfer. But robustness of a blind O residual does not imply robustness of:

- the O-fitted point optimum;
- the O near-optimal set;
- C/F point predictions;
- C/F profile envelopes;
- baseline skill;
- the shared joint fit;
- both varieties and all named solutes.

**Required action:** implement `cross_grind_endpoint_sensitivity()` that repeats the full training/evaluation pipeline for each endpoint/density scenario. The endpoint must be part of the training operator as well as the held-out operator.

### 6.9 The 40 g–40 mL conversion remains an unverified observable mismatch

The source endpoint is described as 40 ± 2 g. The solver is stopped at a target volume divided by flow. The manuscript assumes beverage density 0.98–1.00 g/mL but provides no measurement or source for the relevant espresso liquid/crema state. It then varies 38/40/42 **mL**, not 38/40/42 **g** under a density distribution.

The endpoint error is not necessarily a common multiplicative concentration shift: the time endpoint changes fractional extraction, and that effect can vary by condition and solute. The observed 5.3-point spread confirms that it is not negligible.

**Required action:** either formulate the observation operator in mass coordinates or convert mass to liquid volume using a documented density model and uncertainty. Avoid “matched 40 g” in figures and Results while the implementation is a 40 mL proxy.

### 6.10 Early rounding remains a definite implementation defect

Several code paths round values before downstream aggregation:

- `gate_pannusch_angeloni_per_condition()` rounds each group MAPE to one decimal, then computes `overall_mape_blind` from those rounded values;
- `endpoint_mass_sensitivity()` uses those rounded overall MAPEs and rounds the range;
- `refit_pannusch_angeloni()` stores per-fit holdout MAPEs rounded to one decimal, then averages those fields for named/proxy/all summaries;
- `joint_multigrind_fit()` stores rounded independent-per-grind values before deriving the displayed independent mean/cost;
- `geometry_sensitivity_transfer()` rounds each C/F MAPE to zero decimal places before calculating the maximum spread;
- `flow_map_sensitivity_transfer()` stores rounded perturbation values before ranges/spreads.

The geometry issue is the clearest: a reported maximum spread of 1 percentage point can be created or suppressed by rounding individual values to integers.

**Required action:** preserve raw arrays and full-precision scalar values in the result bundle. Apply formatting only in table/figure rendering. Add tests comparing aggregated values with direct aggregation from raw point losses.

### 6.11 The endpoint sensitivity headline inherits the rounding problem

The reported 19.9→25.2% and 5.3-point spread are calculated from `overall_mape_blind`, which itself is an average of rounded group means. The direction is probably stable, but the values are not “full precision” despite the build’s numerical-contract framing.

**Required action:** return both full-precision point losses and presentation values. Recompute endpoint differences from the point-level losses under one explicitly stated macro/micro averaging rule.

### 6.12 The “entire near-optimal set” remains a coarse finite subset

The transfer routine defines near-optimal O values as grid rates whose O MAPE is no more than 1.10 times the minimum. The primary rate grid has 18 points, and the retained set contains roughly 8–15 values depending on group. This is not an “entire manifold.” It is a finite evaluated subset under one objective, one relative threshold, one domain, and one discretization.

The result reports aggregate held-out MAPEs for those points. It does not export condition-wise predicted ranges or show whether different profile points fail on different conditions.

**Required action:** call it the “evaluated 10%-MAPE near-optimal grid subset” until a continuous/converged profile-wise prediction analysis is performed. Use adaptive/continuous profiling and propagate each accepted parameter pair into condition-level C/F intervals.

### 6.13 SSE and MAPE sets are not interchangeable

The formal identifiability analysis profiles unweighted concentration-scale SSE with a least-squares nuisance level. The transfer set is defined by MAPE with a weighted-median level. The manuscript says the MAPE cross-check “agrees” and then uses “the valley” as if one object underlies both the Hessian and transfer result.

Two objectives can both appear flat while selecting different optima, nuisance paths, boundaries, and prediction sets. The current `mape_cross_check_agrees` logic is not a meaningful equivalence test if it only checks that both flat fractions exceed a threshold.

**Required action:** plot both profiles on the same log-rate axis and report:

- optimum locations;
- overlap of accepted sets;
- boundary status;
- profile correlation after normalization;
- condition-wise predictions from each set;
- sensitivity to absolute versus relative threshold definitions.

### 6.14 The optimum is interior; the tolerance region is open

The manuscript states that the rate is “not a converged interior estimate” and that there is a broad plateau with “no bounded minimum under either objective.” Later it reports a continuous bounded optimizer with an interior optimum near 0.66 and correctly says the 10%-threshold set reaches the upper boundary.

These are different properties:

- the numerical minimum may be interior and reproducible;
- a descriptive near-optimal region may remain open/right-censored;
- parameter uncertainty cannot be inferred without a likelihood/noise model.

Calling the minimum itself unbounded or non-interior is inaccurate.

**Required action:** replace the conflicting text with: “The continuously optimized SSE minimum was interior, but the 10%-of-minimum profiled-objective set remained open at the upper rate boundary; its reported width is therefore a lower bound over the tested domain.”

### 6.15 The Hessian robustness analysis is incomplete

The new convergence routine varies the number/range of rate points and reports stable condition numbers for selected grids. The Hessian still depends on:

- the 41-point inventory grid;
- the local finite-difference or quadratic-fit window;
- parameter scaling/log transform;
- solver tolerances;
- objective normalization;
- the location and spacing of neighboring points;
- whether the local surface is adequately quadratic.

A condition number near 2000 is qualitatively suggestive, but the exact value and inverse-curvature coupling should not carry more precision than the convergence study supports.

**Required action:** provide a sensitivity table over inventory/rate grids, local windows, finite-difference steps, and scaling. Prefer reporting orders of magnitude and eigenvectors with ranges rather than one exact integer.

### 6.16 The profile-width statistic is domain-censored, not domain-independent

The code/commentary describes a log-width quantity as domain-independent, yet every tested configuration reportedly reaches a swept-domain boundary. A width ending at the boundary is a lower bound determined partly by the chosen domain.

**Required action:** rename the field to indicate censoring, e.g. `observed_log_width_lower_bound`, and export explicit left/right open flags. Do not compare widths across domains as if both endpoints were observed.

### 6.17 A 10%-of-minimum objective set is not a confidence region

The manuscript correctly notes that no likelihood is specified, but phrases such as “identifiability” and “whole valley” may still lead readers to interpret the tolerance as statistical uncertainty. A relative 10% criterion depends strongly on the minimum scale and can behave differently across solutes/objectives.

Profile-likelihood methods derive confidence thresholds from a specified likelihood and asymptotic or calibrated reference distribution. This analysis instead uses a descriptive objective profile.

**Required action:** either specify and validate an error model or consistently call the set a descriptive tolerance set. Include threshold sensitivity (for example 5%, 10%, 20%, and a measurement-error-based absolute threshold).

### 6.18 Table 7 is not yet used as a quantitative orthogonal constraint

Figure 2 draws a horizontal Table 7 inventory line and the text says it intersects the profile path. No uncertainty interval for the solid inventory is shown, and no implied rate interval is calculated. A single line crossing a profile is not a quantified tie-breaker.

Because Table 7 is from the same Angeloni campaign, it also cannot be described as independent external confirmation. The manuscript now mostly gets that taxonomy right, but the analytical use remains incomplete.

**Required action:** propagate Table 7 measurement uncertainty and intersect it with the nuisance-level profile. Report the implied rate set and how it changes under endpoint, flow, and objective sensitivity.

### 6.19 The joint shared fit demonstrates compatibility only relative to a flexible comparator

The joint fit is correctly labeled in-sample in much of the text. However, its adequacy is inferred from 6.4% versus 4.9% for separate per-grind mechanistic fits. The constant diagnostic shows a shared level-only model is already near 7.11%, and independent per-grind constants are near 5.05%.

Thus the mechanistic shared fit may add only a small in-sample gain over a much simpler model. Comparing it only with a more flexible mechanistic fit does not establish that its shared dynamics are needed.

**Required action:** add a model ladder with complexity/parameter counts and predeclared adequacy criteria. Information criteria are not automatically valid for the current MAPE setup, so use transparent held-out or paired-loss comparisons where possible.

### 6.20 The manuscript mislabels the joint result in one key sentence

Lines 343–345 describe the strength as “held-out / joint predictive transfer.” The joint result is not predictive transfer: it is fit and scored on pooled O+C+F data. The surrounding paragraphs correctly say this, making the strength line internally contradictory.

**Required action:** use “within-campaign cross-grind holdout at the selected O calibration; separate in-sample shared-parameter compatibility analysis.”

### 6.21 LOCO uncertainty is appropriately called descriptive, but the next step is not optional if intervals remain prominent

The latest text is improved: both the residual-resampling and condition-level resampling summaries are explicitly described as non-coverage-calibrated. That caution is consistent with the dependence created by overlapping LOCO training sets. However, the intervals remain prominent in Figure 3’s title and Results, which can still invite a confidence-interval reading.

The condition-level resampling also resamples nine already-computed condition macro errors. It does not repeat the rate/level fit, preserve all hierarchical dependencies, or include measurement uncertainty. Near agreement between two naive summaries does not validate either one.

**Required action:** either move the intervals to a descriptive supplement or implement repeated-fit resampling at an appropriate experimental unit. Any baseline comparison must be repeated within the same splits/resamples.

### 6.22 Figure 3 hides the condition and error structure behind clustered point clouds

Figure 3 is useful as an observed-versus-predicted display, but it does not show which temperature/pressure condition generated a point, whether errors are systematic by solute or condition, or how the model compares with a constant. Predictions form compact clusters, especially for Robusta, which is exactly why a baseline is needed.

The title includes a descriptive resampling interval but the plot contains no visual uncertainty. The two varieties also use different axis ranges, which makes visual comparison harder.

**Required action:** add equal shared limits/aspect; encode condition or use residual panels; overlay baseline predictions; report paired model-minus-baseline losses. Put descriptive resampling in the caption/table rather than the title unless displayed.

### 6.23 The flow-map magnitude sweep is too narrow for the stated robustness conclusion

`flow_map_sensitivity_transfer()` evaluates one representative combination (Arabica caffeine) under a systematic global ±20% flow multiplier. It refits O and applies the same perturbation to C/F. This is a useful compensation check, but it does not test:

- the other variety or solutes;
- condition-dependent pressure/temperature errors;
- incorrect grind-specific relative flow;
- a different pressure exponent or viscosity law;
- transient/pre-infusion flow;
- measured flow-trace uncertainty.

The rate shifts while held-out MAPE changes little, which is itself consistent with level-rate-flow confounding. It does not establish robustness to the map’s form.

**Required action:** narrow the prose to “limited sensitivity to a common magnitude perturbation for one representative group” until the full map-form sensitivity is run.

### 6.24 The geometry sweep does not resolve grind-specific geometry uncertainty

The geometry analysis applies each of three Pannusch fitted geometries globally to all grinds. This asks whether the complete pipeline changes when one global geometry is chosen. It does not test a mapping in which O, C, and F have different geometries, nor the covariance of geometry with inferred flow and rate.

The code’s verdict says the residual is “not a geometry artefact,” which is stronger than the experiment. A global sweep can miss precisely the cross-grind structural error relevant to transfer.

**Required action:** either build plausible O/C/F geometry scenarios or state that only global-choice sensitivity was examined. Regenerate from unrounded values before quoting a spread.

### 6.25 The current source measurement uncertainty is not propagated

The manuscript notes duplicate extractions and analyte RSD up to approximately 19.7% in the Angeloni source but then uses only reported central values. Some reported transfer errors are of the same order as the source variability. Unweighted MAPE gives equal relative influence to each point regardless of measurement precision, while the formal SSE curvature gives high absolute-weight influence to larger concentrations.

Without replicate-level data, a full observation model may be impossible, but sensitivity to plausible heteroscedastic errors is still possible.

**Required action:** reconstruct available replicate/RSD information by analyte/condition where feasible; otherwise define low/central/high variance scenarios. Show how the profile, baseline skill, LOCO losses, and joint fit change.

### 6.26 Macro-averaging choices need a formal definition and sensitivity table

The paper alternates among named-solute macro averages, proxy-separated averages, pooled point errors, per-grind means, and means over rounded per-fit values. The central 8.4%, 6.4%, 4.9%, and 6.5% figures do not all share the same unit of aggregation.

**Required action:** add a Methods subsection defining:

- point-level percentage error;
- group MAPE;
- macro averaging across variety/solute/grind;
- micro averaging across points;
- whether each experimental setting or reported central value is the statistical unit;
- treatment of TDS/total-solids proxies.

Report macro and micro results side by side as a sensitivity.

### 6.27 Figure 7’s “trajectory-shape” label is incorrect

The correlation in Figure 7 is computed across the nine O-grind temperature/pressure conditions. It is not a temporal extraction trajectory. Calling it “trajectory-shape agreement” conflates operating-condition response with time-course shape, the paper’s main conceptual distinction.

With only nine points, the correlation is also unstable and can be driven by narrow ranges or one condition. No interval is shown. The sign and magnitude should not be read as mechanistic agreement.

**Required action:** rename it “cross-condition response-pattern correlation,” report `n=9`, confidence/bootstrapped descriptive ranges, and preferably compare post-level-fit residual slopes rather than raw correlation alone.

### 6.28 Figure 7’s title overgeneralizes an endpoint-specific sign result

The title says inventory matching “helps caffeine but HURTS trigonelline.” The new endpoint sensitivity explicitly says the trigonelline sign flips near the +5% endpoint. Figure 7 is tied to the 40 mL proxy, but its title reads as a general finding.

**Required action:** state “at the 40 mL proxy endpoint” in the caption and avoid capitalization/causal language. Display endpoint sensitivity or move the sign result to a table.

### 6.29 Figure 7 mixes named solutes with non-equivalent TDS proxies

The paper correctly says Pannusch pseudo-TDS, Angeloni gravimetric total solids, and Waszkiewicz optical TDS are not one analyte. Figure 7 nevertheless puts TDS bars/correlations beside named solutes under a common diagnostic title. This can visually imply equivalence even if the manuscript says otherwise.

**Required action:** separate the aggregate proxy into a distinct panel with a prominent observation-operator note, or omit it from the named-solute diagnostic.

### 6.30 Figure 8’s central inference is logically false for the fitted model

Figure 8 states that solute- and variety-specific negative offsets are something “a pure inventory (level) rescale cannot remove.” Yet the target refit estimates a separate `c_s0` level for every variety × solute. A separate level can shift each group independently and can remove a group-specific mean/intercept offset.

What it cannot remove is condition-dependent structure within a group: residual trends with temperature or pressure, nonparallel response patterns, heteroscedasticity, or grind-specific changes after fitting the level. Figure 8 does not test those because it plots blind residuals before the group-specific target level is fitted.

**Required action:** remove the current title/conclusion. Plot blind and post-level-fit residuals, center within group, and estimate residual trends versus temperature and pressure with uncertainty.

### 6.31 Figure 8 uses a residual population that is not the paper’s central fitted-transfer population

The plot consumes `per_condition`, the blind Pannusch-to-Angeloni O-grind path, including TDS. The core manuscript claim concerns an Angeloni O target recalibration frozen for C/F. Figure 8 is therefore about the pre-refit external mismatch, not residuals from the calibrated transfer model.

This distinction is not apparent from the title “signed transfer residuals.”

**Required action:** label the current data “blind source-model residuals on Angeloni O,” or replace the figure with residuals from O training/LOCO and C/F prediction, clearly separated by evidence tier.

### 6.32 Figure 8 cannot support a temperature or pressure pattern from the current rendering

The x-axis has only three levels, and many group/solute points overlap at each level. There are no within-group fitted slopes, means, intervals, or jitter. The dominant visual feature is vertical group separation, which is exactly the level effect a group-specific scale can address.

**Required action:** facet by variety × solute or plot centered group residual means and uncertainty at each condition. Add interaction tests or descriptive slope ranges. Avoid causal language about unmodeled physics from blind residuals alone.

### 6.33 Figure 2 does not display the MAPE cross-check that carries a headline claim

The abstract and Result 2 say the MAPE cross-check agrees and quote an approximately 66% flat fraction. Figure 2 shows only the SSE surface/profile. Readers cannot assess whether MAPE has the same optimum, boundary behavior, or profile shape.

**Required action:** add MAPE profile panels, or a supplemental figure/table with the same axis and threshold. Include the exact weighted-median nuisance path and compare accepted sets.

### 6.34 Figure 2 conceals right-censoring

The lower caffeine/trigonelline panels shade the within-10% region but do not mark that the region reaches the upper domain boundary. The legend reports a percentage of grid, which can look like a bounded interval. The continuous optimum and wider-domain result are not indicated.

**Required action:** add an open arrow/hatched continuation at the censored side, show tested domain boundaries, and state “lower-bound width; threshold set open at upper boundary” in the caption.

### 6.35 Figure 2’s title turns a descriptive analysis into a verdict

“Flat valley (practical non-identifiability)” is a reasonable interpretation, but the title should not substitute for the statistical assumptions needed to define practical identifiability. The analysis uses a descriptive SSE objective, selected parameterization/domain, local Hessian, and arbitrary tolerance.

**Required action:** use a neutral title such as “Inventory–rate objective surface and profiled objective under the tested O-grind design.” State the interpretation in the caption with scope and caveats.

### 6.36 Figure 5 needs a reduced/null model ladder

Figure 5 compares joint and independent mechanistic MAPE and their difference. It visually emphasizes the cost of parameter sharing but not whether either mechanistic model improves on simple levels. Given the baseline diagnostic, this is a major omission.

**Required action:** add panels or a companion table for shared constant and independent per-grind constants, and plot mechanistic skill relative to each. Include parameter counts and clarify in-sample status.

### 6.37 Figure 6 omits the external result central to the abstract

The abstract cites an independent second-rig TDS trajectory as a culminating result. Figure 6 shows empirical Schmieder fraction/aggregate profiles and same-model exact-cup simulation only. The Waszkiewicz external profile is neither plotted nor supplied in source data.

**Required action:** add a separate external panel showing fraction and cup profiles, target-level profiling, time-offset/first-bin sensitivity, and the high minimum MAPE. Alternatively, demote the external claim from the abstract.

### 6.38 Figure 6 omits the model-discrepancy finding that qualifies the simulation

The result bundle includes moderate and larger discrepancy controls, and tests explicitly recognize that a sharp fraction objective can retain discrimination while localizing a biased rate and leaving an irreducible floor. This is a scientifically important qualification of the “time resolution identifies rate” story, but it is absent from the figure and main narrative.

**Required action:** plot same-model and discrepancy profile results together or add a dedicated figure. Rewrite the conclusion to say temporal resolution can sharpen the objective but does not guarantee physical parameter correctness under misspecification.

### 6.39 Figure 6’s uncertainty display is asymmetric across simulated observables

The plot includes an exact-cup ±1 SD band but not the fraction-simulation seed band, although the result object contains both. The empirical fraction curve is correctly seed-free, but the simulated fraction curve/summary underlying the 9.8–20.3× ratios should be displayed if ensemble claims are made.

**Required action:** distinguish empirical fraction, simulated fraction mean/band, and exact-cup mean/band. Avoid plotting a seed-0 line as if it were the ensemble result.

### 6.40 The exact-cup simulation remains an inverse-crime illustration

The paper now acknowledges this, which is good. Truth and fit use the same solver and a finite candidate rate grid containing the true value. The 100% recovery of rate=1 is therefore a best-case grid result, not evidence of estimator calibration.

**Required action:** add off-grid truth values, continuous optimization, multiple noise levels, solver discretization perturbations, and misspecification. Report bias, dispersion, and objective curvature rather than only fraction of seeds selecting a grid point.

### 6.41 The “identifiability ratio” is a domain-dependent sharpness statistic, not a standard identification metric

The ratio `max-edge MAPE / min MAPE` changes with the chosen rate range, edge location, noise level, and minimum floor. A ratio of 2 does not have an inferential interpretation and can be inflated when the minimum is small.

**Required action:** call it a descriptive profile-range ratio, report the full profile and domain, and supplement with accepted-set width/curvature or a likelihood-based interval when a noise model is available.

### 6.42 The external Waszkiewicz cup profile is flat by construction

With one integrated scalar and one free multiplicative target level, every rate can match the scalar exactly. The manuscript now states this clearly. The abstract’s phrase that the integrated cup “carries no rate information at all,” however, risks sounding empirical/general rather than algebraic for this one-observation/one-level design.

**Required action:** qualify in the abstract: “the one-scalar cup profile was flat by construction after profiling one multiplicative level.” Emphasize that multiple cups at distinct conditions/endpoints could constrain rate.

### 6.43 The external Waszkiewicz profile is weak and high-error and should remain a shape diagnostic

The reported best rate is around 0.4, minimum MAPE around 27%, and profile range ratio around 2. The level is fitted to the external trajectory. This is evidence that temporal bins contain more rate-sensitive shape information under the tested operator, but not that the transferred kinetics accurately predict the external coffee or identify a physical rate.

**Required action:** retain “external-data objective localization” and report the full nuisance sensitivity. Do not use “independent identification,” “validation,” or “prediction” for the absolute concentration.

### 6.44 The source-study description should distinguish measured and derived cup responses

Schmieder’s study collected ten fractions under 15 settings and used fitted extraction kinetics to calculate cup response variables at selected brew ratios. The repository uses a derived six-window subset and compares its weighted aggregate with a source cup response. Calling the latter simply the “actual cup” can imply a directly measured complete-shot cup paired exactly with the six retained windows.

**Required action:** document the source calculation, replicate aggregation, experiment matching, and any mismatch between fraction-shot and cup-response records. Use “source-derived BR 1/3 cup response” where appropriate.

### 6.45 The paper’s evidence taxonomy is not consistently implemented in code

The manuscript has improved labels, but analysis docstrings and verdict strings still include phrases such as “REAL transfer test,” “external stress test,” “non-transferability,” “robust,” “works,” or “residual is not a geometry artefact.” These strings are serialized into `results.json` and can flow into reports.

**Required action:** define structured fields such as `campaign_relation`, `fit_use`, `holdout_unit`, `observable`, `nuisance_fitted`, and `inference_scope`. Generate prose from those fields or keep prose out of machine-readable results.

### 6.46 The figure README itself overstates the current evidence

The README says predictive transfer “works at matched mass” and that the cup “loses the rate.” It also declares six figures while the directory contains eight. Documentation should not be a second, stronger manuscript.

**Required action:** make the README procedural and neutral: describe files, inputs, build commands, and evidence classes without scientific verdicts.

### 6.47 The input hash list is incomplete

The manifest hashes six data files, but the analyses depend on code modules, model parameters/closures, possible additional fraction and hydraulic inputs, manuscript text, plotting code, source-data exports, and environment state. It does not hash rendered figures or the environment lock.

**Required action:** include all direct inputs and outputs or generate a dependency manifest during execution. At minimum hash:

- manuscript;
- all model/analysis/plot/build modules;
- every data file opened;
- result bundle;
- source-data CSVs;
- all figures;
- lockfile/container definition;
- test suite and build command.

### 6.48 Fast tests validate cached fields, not scientific recomputation

`tests/test_paper_a.py` reads the committed bundle for most guards. Tests skip if blocks are absent and do not run PDE analyses. This is acceptable for fast CI, but passing tests only confirm the cached bundle contains expected patterns, not that current code reproduces it.

The build test also accepts a stale dirty manifest because `verify()` does.

**Required action:** retain fast structural tests but add a scheduled/release clean full build, commit/hash checks, small numerical smoke cases, and a failure when required bundle blocks are missing rather than skipping in release mode.

### 6.49 The manuscript remains an internal project document

Examples include:

- the repository note at the top;
- review identifiers such as A2-09, B1, M4, MAJ-05;
- function names embedded in Results;
- “owed” checks and “data-blocked” backlog items;
- a section titled “Open gaps this paper defines” that doubles as a project ledger;
- a change-log pointer;
- references to cards, handoffs, and repo rules;
- no conventional full reference list or journal declarations.

**Required action:** create a submission branch/document that presents methods, results, limitations, and future work scientifically, while moving implementation/backlog detail to a supplement or repository documentation.

### 6.50 The novelty statement remains conditional on an unfinished search

The manuscript is appropriately cautious (“to our knowledge, following a documented scoping search”) but says the full Scopus/Web of Science query will be run at submission. A novelty statement should be based on the completed search used for the submitted version.

**Required action:** complete, date, archive, and report the search strategy before submission. Keep novelty framed as an applied espresso case study, not a new identifiability method.

---
## 7. Section-by-section manuscript review

### 7.1 Repository note and title

The working-draft note is useful for project governance but should not appear in a submitted manuscript. It tells the reader which verbs are “allowed,” references review cards and ROADMAP sections, and states that a release remains “owed.” Those are process controls, not scientific content. Their presence also creates an avoidable ambiguity: some of the manuscript’s restraint may look editorially imposed rather than arising from the evidence.

The title is memorable and broadly consistent with the strongest finding. “The cup can hide the clock” should nevertheless be treated as a case-study result, not a universal theorem. The subtitle appropriately names “practical inventory–kinetics confounding” and “cross-dataset espresso extraction case study”; retain that qualification.

**Required actions**

1. Remove the repository note from the submission file.
2. Move the verb/evidence taxonomy to an internal style guide or a short supplementary provenance note.
3. Retain “case study” in the title or subtitle.
4. Do not use “the cup” generically in the abstract without adding “under the tested model, design, and endpoint operator.”

### 7.2 Abstract

The abstract is much clearer than early versions about the SSE surface, the local inverse-curvature coupling, and the in-sample nature of the joint fit. It still contains three claims that outrun the analysis.

First, “predicts the held-out coarse/fine grinds reasonably” is a value judgement unsupported by a baseline or predeclared tolerance. An 8.23% macro-MAPE can be low in absolute terms while adding almost no information beyond a group-level constant; the retained diagnostic finds only a 0.36-point advantage over the O-trained constant and no advantage on grind F at the displayed precision.

Second, “the entire near-optimal O-grind set” is not what was propagated. The code evaluates a finite accepted subset of an 18-point MAPE grid under a 10%-relative objective rule. It does not trace a continuous profile set, show grid/domain convergence for the prediction envelope, or establish that the selected set corresponds to uncertainty with stated coverage.

Third, “the integrated cup carries no rate information at all” needs the algebraic qualifier. In the one-external-shot calculation, one multiplicative level is profiled against one integrated scalar; the flat profile is therefore constructed by the observation/nuisance-parameter count. This does not imply that a set of cups at multiple endpoints or operating conditions would carry no kinetic information.

**Required actions**

- Replace evaluative transfer wording with baseline-relative results.
- Call the propagated set a “finite objective-tolerance grid subset” until a continuous profile-prediction calculation is supplied.
- State that the one-scalar external cup profile is flat “by construction after profiling one multiplicative level.”
- Add the endpoint-density caveat to the abstract if “matched-beverage-mass” remains load-bearing.
- Do not state that identifiability and transfer “diverge” until incremental transfer skill is shown; presently the evidence establishes weak parameter localization plus modest absolute holdout error.

### 7.3 Introduction

The conceptual distinction among endpoint fit, parameter localization, and predictive transfer is valuable and should remain the organizing theme. The Introduction currently says that a held-out whole-cup error is “almost always” read as mechanistic evidence and that the paper provides a protocol distinguishing a transferred calibration from a “non-identifiable curve fit masquerading as one.” Both formulations are rhetorically stronger than necessary and are not supported by a systematic review of field practice.

The Introduction should also distinguish two mechanisms of weak localization:

- exact linearity in inventory under this solver and normalization;
- approximate compensation between inventory and rate over the finite operating design and endpoint map.

The former is structural within the implementation; the latter is empirical and domain-dependent. Combining them into a generic statement that both knobs “act as a level” can obscure the fact that rate can alter condition dependence as well as level.

**Required actions**

- Replace “almost always” with a sourced and bounded statement such as “whole-cup endpoints are common in the campaigns considered here.”
- Remove “masquerading,” which imputes intent and is unnecessary.
- State explicitly that inventory is exactly multiplicative in this implementation, whereas the rate direction is only approximately collinear with it over the tested design.
- Introduce the baseline question here: useful transfer requires improvement over a level-only predictor, not merely a small absolute error.

### 7.4 Methods — model and parameterization

Section 2.1 gives a useful high-level description but is not yet sufficient for independent reproduction. The paper needs the governing equations, boundary/initial conditions, dependent variables, geometry, hydraulic closure, temperature dependence, species parameters, numerical method, convergence tolerances, and the exact parameter transformation used for profiling and Hessian calculations. A function name and lineage citation cannot substitute for Methods.

The sentence that whole-cup concentration is “exactly linear in `c_s0`” should be accompanied by a short derivation or numerical invariance test. The weighted-median result for MAPE also requires the exact loss definition, weights, handling of zeros, and proof/reference. Readers need to know whether macro-MAPE is obtained by pooling observations, averaging group MAPEs, or averaging condition-level percentages with equal weights.

**Required actions**

- Add the equations and complete parameter table.
- Define the dimensionless/physical units of the rate multiplier and inventory.
- State which parameters are inherited unchanged from Pannusch, which are recalibrated, and which are assumed for Angeloni.
- Define all objective functions mathematically before presenting values.
- State the optimizer bounds, grid values, tie-breaking rule, and boundary policy.
- Include a solver-resolution and numerical-error subsection.

### 7.5 Methods — data provenance and statistical unit

The revised description of Schmieder’s 15 settings, repetitions, ten fractions, and the derived six-window Pannusch subset is much improved. The Angeloni description also correctly notes that the repository retains central values rather than replicate-level uncertainty.

Two provenance issues remain. First, the manuscript alternates among “cup,” “whole-cup,” “source cup,” and weighted fraction aggregate without always distinguishing a directly measured beverage sample from a response reconstructed or calculated from fraction data. Second, 66 retained sample records do not automatically imply 66 independent experimental units: duplicates, shared condition settings, variety strata, and source-level preprocessing matter for uncertainty.

**Required actions**

- Add a data dictionary with source table/figure, unit, replicate handling, transformation, inclusion/exclusion, and repository row count for every outcome.
- Identify the experimental unit for each analysis and the level at which resampling is performed.
- Distinguish direct cup measurements, source-derived cup responses, sampled aggregates, and exact simulated integrals throughout.
- Propagate or bracket source measurement variability rather than treating central values as error-free.

### 7.6 Methods — beverage endpoint and density

The new 38/40/42 mL sensitivity statement is an improvement because it makes the mass/volume approximation visible. It does not make “matched 40 g cups” exact. At 40 g and density 0.98–1.00 g/mL, the corresponding volume is roughly 40.0–40.8 mL before considering crema, dissolved-solids concentration, temperature, or how the source defined beverage mass. The source’s ±2 g tolerance also creates a range that is not identical to 38–42 mL.

More importantly, the current sensitivity sweep is applied to the blind O-grind residual rather than the O-refit-to-C/F transfer estimand. The manuscript currently uses that sweep to support a broader matched-endpoint narrative than it tests.

**Required actions**

- Refer to the implementation as a “40 mL volume approximation to a 40 ± 2 g endpoint.”
- Propagate a defensible density distribution or report a two-dimensional mass × density sensitivity.
- Rerun the complete O calibration, profile set, C/F transfer, and baselines at each endpoint scenario.
- Show whether the headline ranking and skill—not only the sign of two blind residuals—are stable.

### 7.7 Methods — pressure-to-flow map

The manuscript properly labels the pressure-to-flow relation as an assumption rather than a fit. The ±20% magnitude sweep is useful but narrow. A global scalar perturbation preserves every condition’s ordering and the entire map shape. It does not test whether the chosen shape, pressure dependence, grind dependence, or machine-control behavior is correct.

The transfer result is particularly sensitive to this distinction because flow determines both advection and endpoint time. Cross-grind flow is not measured condition by condition in Angeloni and is inferred from a constructed map. A global “geometry sensitivity” similarly tests a common geometry choice, not whether coarse and fine beds have different effective geometry.

**Required actions**

- Publish the exact map equation, parameter values, source, and resulting condition table.
- Separate sensitivity to map magnitude from sensitivity to map form.
- Explore at least one alternative physically plausible pressure–flow/grind map and report condition-wise effects.
- State clearly that the C/F transfer is conditional on inferred rather than measured flows.
- Avoid saying residuals are “not a flow-map artefact” on the basis of one ±20% representative sweep.

### 7.8 Methods — fitting, aggregation, and uncertainty

The evidence vocabulary is a strong addition. The statistical contract remains fragmented across prose and functions. The paper uses SSE for the formal local surface/Hessian, MAPE for point selection and transfer, macro-averages across groups, a descriptive resampling of LOCO errors, and local curvature diagnostics without a likelihood. These are all defensible as descriptive analyses, but they must be specified in one table and kept distinct.

The current implementation still rounds before several downstream aggregates. That is a numerical-method error, not a presentation preference. Rounding should occur only at the final display layer.

**Required actions**

- Add an estimand table: analysis, data unit, fit set, holdout set, nuisance parameters, loss, aggregation, uncertainty, and interpretation.
- Preserve full precision throughout and round only in tables/captions.
- Report paired condition-level loss differences for model-versus-baseline comparisons.
- For LOCO, either rerun a hierarchical/cluster bootstrap that repeats fitting or retain strictly descriptive quantiles without a “95%” coverage implication.
- Distinguish optimizer uncertainty, data uncertainty, model discrepancy, and numerical uncertainty.

### 7.9 Result 1 — blind comparison and source-data bracket

The correction from a fixed-time integration window to a matched endpoint is important and should be documented transparently. The result is currently hard to interpret because the paper combines a wide species-envelope check, per-condition blind residuals, a Pannusch–Angeloni refit, an endpoint-volume sweep, and flow-map sensitivity under one “apparent success” heading.

The endpoint sweep reveals that the blind residual conclusion can change materially over 38–42 mL, with a reported approximately 5.3-point span and a sign change for one analyte. This is not a minor caveat; it demonstrates that endpoint definition is an influential component of the observable contract.

**Required actions**

- Separate the blind model-data comparison from the target recalibration analysis.
- Report every group, not only selected Arabica analytes, in endpoint and flow sensitivities.
- Define a priori what would count as agreement or failure.
- Include source-measurement uncertainty and avoid interpreting overlapping broad envelopes as validation.
- Rephrase the result as an observable-contract diagnostic unless baseline-relative predictive skill is shown.

### 7.10 Result 2 — objective surface and practical identifiability

This remains the paper’s strongest section. The distinction between inverse-curvature coupling and statistical correlation is correct. The new bounded optimizer and grid/domain checks improve transparency.

The wording still conflicts internally. An interior numerical minimizer near rate 0.66 is reported, while nearby text says the rate “does not converge to an interior value” and that there is “no bounded minimum.” The proper conclusion is that the point minimum is interior under the chosen objective and bounds, but the descriptive near-optimal/tolerance set is broad and right-censored at the upper tested boundary. That is practical weak localization, not absence of a numerical minimum.

The 10%-of-minimum rule is descriptive. It is not a confidence threshold. Its width depends on loss scaling, noise level, objective floor, and the tested domain. The Hessian condition number likewise depends on parameter scaling, local finite differences, and where it is evaluated.

**Required actions**

- Harmonize all statements around “interior point optimum; right-censored broad tolerance set.”
- Show SSE and MAPE profiles together or in a supplement.
- Mark the tested upper boundary and censoring explicitly in Figure 2.
- Report sensitivity to inventory grid, finite-difference step, parameter scaling, and optimum location.
- Do not interpret the inverse Hessian as covariance or the 10% set as an interval with coverage.
- Propagate the profile set to condition-wise predictions rather than only aggregate errors.

### 7.11 Result 2 — Table 7 orthogonal inventory measurement

Using Angeloni’s Table 7 as a same-campaign orthogonal measurement is potentially valuable. The current presentation mainly draws a vertical line through the objective surface. A line crossing a broad valley does not by itself establish that the external inventory measurement resolves the rate: the measurement has uncertainty, unit conversions and dry-mass basis must match, and the intersection with the profile should be quantified.

**Required actions**

- Document the exact conversion from Table 7 to model inventory, including moisture/dry-mass and species naming.
- Include measurement uncertainty as a band, not a line.
- Compute the induced rate profile/interval conditional on that inventory band.
- State whether the orthogonal inventory is truly excluded from all target fitting and tuning.
- Avoid “independent confirmation”; it is an orthogonal same-campaign constraint.

### 7.12 Result 3 — point transfer across grind

The manuscript correctly calls C/F a within-campaign holdout. That is an improvement over earlier “external transfer” language. The unresolved issue is whether the model does more than carry an O-fitted concentration level into C and F. The level-only benchmark nearly matches the reported macro-MAPE and beats the mechanism for five of twelve cases.

A claim that the point optimum “transfers reasonably” therefore has no objective basis until a baseline, tolerance, and uncertainty are supplied. Figure 4’s visual compression can make a narrow level predictor look strong when the between-group range dominates the axes.

**Required actions**

- Add full-precision level-only, same-condition O, and reduced-mechanistic baselines.
- Report skill `1 − L_model/L_baseline`, paired loss differences, and uncertainty by group and grind.
- Plot residuals or within-group centered predictions in addition to pooled observed-vs-predicted axes.
- Predeclare an acceptable-error criterion tied to measurement repeatability or application need.
- Remove “reasonable” if the model does not show material baseline-relative skill.

### 7.13 Result 3 — transfer along the profile set

The new calculation is directionally appropriate: identifiability conclusions should be propagated into predictions. The manuscript overstates its completeness. The “entire near-optimal set” comprises 8–15 accepted points selected from an 18-point MAPE rate grid. The formal identifiability panel is SSE-based, while this accepted set is MAPE-based. Only aggregate held-out errors are summarized, so a stable average can hide unstable conditions or sign reversals.

**Required actions**

- Define separately the SSE profile set and the MAPE objective-tolerance set.
- Trace the accepted set continuously or demonstrate grid/domain convergence of its prediction envelope.
- Plot condition-wise C/F prediction bands and baseline-relative skill along the profile.
- Report the rate/inventory endpoints, number of accepted points, boundary censoring, and sensitivity to 5%, 10%, and 20% thresholds.
- Replace “whole manifold” and “entire set” with “tested objective-tolerance subset” until the continuous calculation is complete.

### 7.14 Result 3 — leave-one-condition-out analysis

The LOCO exercise is useful for showing that selected point estimates are not driven by a single O condition. The folds share eight of nine training conditions, so their errors and fitted parameters are strongly dependent. Resampling the nine already-computed fold errors is not a conventional confidence interval for future prediction and does not reproduce the fit-selection process.

**Required actions**

- Keep the current interval labeled “descriptive fold-error resampling range,” not a 95% CI.
- Prefer a cluster/bootstrap procedure that resamples experimental units and reruns profiling, with a clearly stated target population.
- Report fold-specific fitted rates/inventories and whether optima hit boundaries.
- Add baseline LOCO under the identical folds.
- Do not use the LOCO range as evidence of cross-grind generalization.

### 7.15 Result 3 — joint multigrind fit

The joint shared-parameter fit is a useful compatibility diagnostic. It is entirely in sample and should not be called predictive transfer. The reported 6.4% versus 4.9% comparison is also based on rounded intermediate independent-fit values in the current path.

The scientific interpretation depends on a null/reduced comparator. A shared level-only model gives approximately 7.11% in the retained diagnostic, leaving a small in-sample gain. Without a penalty for flexibility, measurement uncertainty, or an out-of-sample criterion, a 1.5-point cost of sharing is not inherently “modest.”

**Required actions**

- Regenerate all values from unrounded condition-level predictions.
- Add shared and per-grind level-only baselines.
- Report degrees of freedom and an information/validation criterion if comparing model flexibility.
- Present the result as “shared-parameter in-sample compatibility,” not transfer.
- Show condition-wise residuals and boundary flags, not only heatmap averages.

### 7.16 Result 6 — empirical fraction positive control

The positive-control concept is sound: under the model’s own calibration campaign, fraction-resolved scoring should localize rate more strongly than an aggregate. The evidence is in sample and partly constructed from the same model lineage, so it verifies sensitivity of the observation operator rather than external mechanistic truth.

The “sampled aggregate” is not equivalent to an exact cup and may retain or discard information depending on window selection and weighting. The paper should make the six-window derivation and all weights explicit.

**Required actions**

- Call this an in-sample observation-operator sensitivity check.
- Provide the six windows, times, weights, normalization, and mapping to source fractions.
- Show all species and operating conditions or justify the representative subset.
- Include uncertainty or replicate variability from the source campaign.

### 7.17 Result 6 — same-model exact-cup simulation

The exact-cup simulation is an “inverse crime” in the conventional sense: data are generated and fitted with the same model, discretization family, and parameterization. It is useful for demonstrating that integration can erase rate sensitivity even without external discrepancy, but it cannot establish that the real espresso system behaves that way.

The newly added discrepancy controls are important and should be visible, not hidden in the bundle/tests. Figure 6 currently shows only the no-discrepancy exact-cup band.

**Required actions**

- Label the panel “same-model synthetic illustration.”
- Plot moderate and large discrepancy controls and quantify how often they create false localization or bias.
- Vary noise, operating design, endpoints, seed count, and mismatch type.
- Report numerical resolution and stochastic convergence.
- Avoid using synthetic exact-cup flatness as independent support for the empirical claim.

### 7.18 Result 6 — independent Waszkiewicz trajectory

The external trajectory is the paper’s most genuinely independent evidence class. The manuscript now appropriately says the target level is profiled and the result is objective localization. The minimum temporal MAPE is still high (approximately 27%) and the profile only about twofold above its minimum across the tested rate range, so the result is weak rather than decisive.

The integrated-cup comparison is flat because a single level parameter is fitted to a single scalar. That algebraic construction should not be presented as an empirical discovery. The temporal result is also sensitive to time offset, first-bin treatment, flow weighting, and concentration/TDS operator choices.

**Required actions**

- Add the observed and predicted time-series/profile panel to a main or supplementary figure.
- Plot the full profile under every nuisance specification and report the shift in the optimum.
- Separate flow measurement uncertainty, timing alignment, first-bin handling, and TDS conversion.
- State that the fitted level prevents an absolute-concentration prediction claim.
- Characterize the result as “external temporal-shape objective localization with substantial residual error.”

### 7.19 Discussion

The Discussion is strongest when it separates parameter localization from predictive performance and emphasizes observable matching. It is weakest where it treats the current absolute C/F errors as evidence that non-identifiability can coexist with successful transfer. The baseline diagnostic means that this illustrative contrast is not yet established.

The practical recommendation should also be more nuanced. Time-resolved fractions are one way to improve design; independent inventory measurements, multiple endpoint masses, richer input trajectories, measured flow, or orthogonal solute information may also rotate sensitivity directions. Conversely, time resolution does not guarantee identifiability if noise, nuisance levels, and model discrepancy dominate.

**Required actions**

- Reframe the central message as a testable separation, not a demonstrated divergence, until baseline skill is quantified.
- Distinguish design recommendations supported directly by this case from broader hypotheses.
- Add a limitations paragraph covering density, inferred flow, geometry, source central values, model discrepancy, objective thresholds, and same-model simulation.
- Avoid universal language about cups or clocks.

### 7.20 “Open gaps this paper defines”

This section functions as a development backlog rather than a manuscript section. Some items are genuine scientific limitations; others are code tasks, review identifiers, or future project cards. A journal reader needs a concise Limitations and Future Work section, not a live handoff ledger.

**Required actions**

- Convert unresolved scientific limitations into prose in the Discussion.
- Move engineering tasks and review IDs to the repository issue tracker.
- Remove claims that a gap is “defined” by the paper unless the literature review substantiates that priority.

### 7.21 Figures section

The manuscript says “Six figures” and lists Figures 1–6. The rendering code and current directory contain Figures 1–8. Figures 7 and 8 are therefore orphaned: they have no manuscript captions, no placement, and no explicit interpretation in the main text. The figure module and README also still say six figures.

**Required actions**

- Decide whether the paper has six or eight main figures.
- If Figures 7–8 are retained, cite them in Results, provide complete captions, and update the README/build contract.
- If supplementary, rename and number them accordingly.
- Generate vector versions and source-data tables for every plotted element.

### 7.22 Related work and novelty

The related-work section is broad and appropriately states that the contribution is an applied case study rather than a new identifiability method. It is still a scoping-search narrative with the full indexed search deferred to submission. The novelty claim should not precede the completed search.

The bibliography is not rendered in the draft itself; readers are sent to a repository `.bib`. A submitted paper needs a complete reference list and journal-standard citations.

**Required actions**

- Complete and archive the search before finalizing novelty language.
- Report databases, dates, exact queries, screening method, and inclusion logic.
- Add the complete bibliography to the manuscript.
- Distinguish coffee-process modelling, inverse-problem methods, and this paper’s specific applied gap.

### 7.23 Reproducibility section

The current section is a code map, not a reproducibility statement. It lists function names and calls slow analyses “not in CI,” but does not identify a clean release, environment, hardware, random seeds, run time, software versions, input/output hashes, licenses, or an executable end-to-end command. Some strength tags are also stale: the granulometry line still says “negative (held-out grind)” despite the revised narrative.

**Required actions**

- Replace the section with Data Availability, Code Availability, Computational Reproducibility, and Ethics/Competing Interests/Funding declarations as required by the journal.
- Pin a release and environment; provide one command that regenerates results, all eight—or declared six—figures, source data, and the manuscript number table.
- Make release verification fail on a dirty tree, mismatched commit, missing output, absent hash, or stale manuscript value.
- Preserve the implementation map in a supplementary README.

---

## 8. Figure-by-figure review

### 8.1 Figure 1 — study and evidence design

**What works**

- The campaign lanes help distinguish source calibration, target recalibration, within-campaign holdout, same-campaign orthogonal measurement, synthetic illustration, and independent external data.
- The explicit definition of “external” is valuable and corrects earlier overclassification.
- The visual hierarchy is readable and the palette is restrained.

**Problems**

- Arrows can be read as a single chronological validation chain even though Table 7 is not downstream evidence generated by the C/F holdout and the Schmieder/Pannusch lane is not experimentally connected to Angeloni by a shared coffee or rig.
- “Held-out O conditions” may imply a conventional independent test set; LOCO folds share most training data and are an internal sensitivity exercise.
- The “same-model exact-cup simulation” is shown on the same evidentiary plane as empirical datasets without an explicit “synthetic/inverse-crime” warning.
- The figure contains no direct indication that Angeloni flow is inferred rather than measured.
- The legend and fine text may be illegible at single-column print size.

**Required revision**

- Use non-directional grouping or annotate arrows as “analysis relation,” not evidence accumulation.
- Rename LOCO to “internal leave-one-condition-out refitting.”
- Add “synthetic; same generator and fitter” to the simulation box.
- Add “flow inferred from assumed map” to the Angeloni lane.
- Supply a self-contained caption defining every category.

### 8.2 Figure 2 — objective surface and profiles

**What works**

- The figure makes the compensating valley visually clear.
- Plotting the profiled path and Table 7 inventory reference is useful.
- Log-rate display is appropriate.

**Problems**

- Only the SSE profile is visible even though the manuscript repeatedly invokes a MAPE cross-check and uses MAPE for transfer-set selection.
- The accepted/tolerance region reaches the upper plotted boundary, but the title and annotations do not prominently say “right-censored by tested domain.”
- Contour values and objective normalization are difficult to interpret; a reader cannot tell whether color differences are practically large.
- A vertical Table 7 line without an uncertainty band overstates precision.
- The local condition number/coupling annotation can be mistaken for a global property of the whole valley.
- The figure does not show grid points, continuous-optimum location, or sensitivity to scaling/finite differences.

**Required revision**

- Add a companion MAPE profile or a clearly linked supplementary panel.
- Shade and label the accepted region, with an arrow/open endpoint at the domain-censored upper edge.
- Show the continuous point optimum and sampled rate grid.
- Replace the Table 7 line with a converted uncertainty band.
- State in the caption that the Hessian metrics are local, scale-dependent diagnostics.
- Export the full surface matrices, profile arrays, accepted-set flags, optimum, and Table 7 band.

### 8.3 Figure 3 — O-grind leave-one-condition-out predictions

**What works**

- Showing every held-out point is preferable to reporting only a pooled score.
- Separating varieties reveals group structure that a single pooled panel would hide.
- The identity line is useful.

**Problems**

- The pooled observed-versus-predicted range is dominated by between-solute and between-variety levels; within-group predictive structure is visually compressed.
- No level-only LOCO baseline is shown.
- Conditions, temperatures, pressures, and fold identities are not encoded, so structured residuals cannot be diagnosed.
- The title foregrounds pooled MAPE and a descriptive interval without clearly stating the dependence among folds.
- Measurement uncertainty is absent.
- Source data for this figure are not exported.

**Required revision**

- Add residual or within-group-centered panels and a matched baseline.
- Encode condition or provide a companion table with T, p, observed, predicted, baseline, and fold-fitted parameters.
- Label the interval “descriptive resampling of dependent fold errors.”
- Include measurement-error bars where available.
- Export all point-level source data at full precision.

### 8.4 Figure 4 — frozen O-to-C/F transfer

**What works**

- C and F are separated, and all condition-level points are shown.
- The figure directly visualizes the internal cross-grind holdout rather than only a summary statistic.

**Problems**

- The title says transfer is “reasonable,” an evaluative conclusion not defined in advance and not supported against a baseline.
- The title also advertises “≤1 pp geometry-sensitive,” but the panel contains no geometry sweep and the number is calculated after rounding each geometry-specific error to a whole percentage point.
- No O-trained constant, same-(T,p) O lookup, or reduced model is shown.
- No near-optimal-set prediction envelope is shown despite the abstract’s emphasis on stability along the valley.
- No endpoint-mass/density sensitivity appears.
- Pooled axes again privilege between-group level agreement over within-group condition response.
- Source data for the figure are absent from the export package.

**Required revision**

A defensible redesign would use three aligned views:

1. observed versus predicted for the selected mechanistic point and O-trained constant;
2. paired condition-level loss difference or residual by group and grind;
3. condition-wise prediction envelope over the converged profile set, with endpoint/density scenarios as bands or facets.

The title should be descriptive, for example: **“Frozen O-grind calibration applied to C and F: absolute errors and comparison with level-only baselines.”** Geometry sensitivity should move to a dedicated panel/table and be recomputed without intermediate rounding.

### 8.5 Figure 5 — joint shared versus independent fits

**What works**

- The heatmap format makes group/grind heterogeneity visible.
- Showing both joint and independent scores is better than a single pooled average.
- Boundary flags are relevant to interpretation.

**Problems**

- Both columns are in-sample fits with different flexibility; the visual may be read as a validation comparison.
- No shared/per-grind level-only null is shown.
- The independent 4.9% summary is contaminated by early rounding.
- A heatmap of MAPE alone hides residual sign and condition structure.
- The “cost of sharing” has no uncertainty or benchmark against measurement repeatability.
- The exported CSV contains only per-grind MAPEs, not point predictions, parameter values, or boundary flags.

**Required revision**

- Add null-model columns and state parameter counts.
- Regenerate from full-precision point losses.
- Provide condition-level residual distributions and fitted parameter/boundary tables.
- Relabel the figure as an “in-sample shared-parameter compatibility diagnostic.”
- Export all underlying predictions and fit metadata.

### 8.6 Figure 6 — fraction versus aggregate rate profiles

**What works**

- The central visual comparison—sharp fraction profile versus flat aggregate profiles—is conceptually effective.
- Showing all three solutes is useful.
- The 20-seed exact-cup band improves on the earlier single-seed figure.

**Problems**

- The panel conflates three evidence types: empirical in-sample fractions, a sampled aggregate from those fractions, and same-model synthetic exact-cup simulations.
- The exact-cup band alone is shown; uncertainty for empirical fractions and sampled aggregates is absent.
- The moderate and large discrepancy controls are not plotted.
- The independent Waszkiewicz temporal profile, which the prose treats as key corroboration, is absent.
- The seed band may convey data uncertainty even though it is stochastic-simulation variability under one generator.
- The title/caption needs to state which profile is SSE or MAPE and whether levels are profiled.
- Source-data CSVs omit seed-level curves, discrepancy controls, accepted sets, and external profiles.

**Required revision**

- Separate empirical, synthetic, and external panels or use clearly differentiated rows.
- Plot discrepancy controls and seed-level/quantile summaries.
- Add the external Waszkiewicz objective profile and observed trajectory in a distinct panel.
- Define every loss, normalization, nuisance fit, and endpoint operator in the caption.
- Export all curves and seeds at full precision.

### 8.7 Figure 7 — per-group refit diagnostics

**What works**

- Group-specific blind versus inventory-matched errors expose heterogeneity hidden by pooled summaries.
- Marking cases in which inventory matching worsens error is informative.
- Correlations provide a first look at whether the model captures cross-condition variation.

**Problems**

- Panel (b) labels a correlation across nine operating conditions as “trajectory-shape agreement.” These are not temporal trajectories; they are condition-response patterns.
- Correlation with only nine points is highly uncertain, can be driven by one condition, and is insensitive to calibration/scale. No confidence interval or rank-correlation sensitivity is shown.
- The title generalizes that matching “helps caffeine but HURTS trigonelline”; this is endpoint-, variety-, and model-specific and may not hold uniformly.
- TDS is included alongside species-specific outcomes although its inventory interpretation differs.
- The bar comparison is still based on the blind source-model residual, not necessarily the fitted O-to-C/F transfer question.
- The figure is not listed or captioned in the manuscript.

**Required revision**

- Rename panel (b) “cross-condition association between model and data.”
- Show scatterplots or condition labels, Pearson and Spearman estimates, uncertainty, and leave-one-condition sensitivity.
- Avoid a universal analyte verdict in the title.
- Separate TDS or explain its level parameter and comparability.
- Connect the diagnostic explicitly to the estimand it addresses.

### 8.8 Figure 8 — residuals versus operating conditions

**What works**

- Plotting signed residuals against temperature and pressure is the right general diagnostic.
- Variety color and solute marker encodings expose systematic grouping.

**Critical logical problem**

The title says the solute- and variety-consistent negative offset is something a pure inventory level rescale “cannot remove.” The model fits a separate inventory level for each variety × solute. A group-specific multiplicative level can remove a group-specific intercept/offset in log or relative-error space. What a single level cannot remove is **within-group residual dependence on temperature, pressure, grind, or another condition variable after the level is fitted**.

The plotted residuals are explicitly `signed_resid_blind_pct` from the blind source-model prediction, before the target group level is fitted. They therefore cannot establish that the residual is irreducible by inventory recalibration. The visual clustering by group is exactly the pattern most compatible with a missing group-level adjustment.

**Required revision**

- Withdraw the current title and interpretation.
- Replot residuals after fitting the group-specific O inventory level, and separately after full selected-point fitting.
- Within each group, estimate residual trends versus centered temperature and pressure, with uncertainty and interaction checks.
- Distinguish source-model blind residuals, O-calibration residuals, and C/F transfer residuals.
- Do not infer a mechanism from pooled colored clusters.
- A suitable title is: **“Blind source-model residuals by operating condition; group offsets motivate target-level recalibration.”**

### 8.9 Cross-figure design and publication quality

Across all figures:

- Titles often contain conclusions (“reasonable,” “works,” “cannot remove”) rather than describing the plotted estimand.
- Full self-contained captions are missing from the manuscript.
- Raster PNGs should be supplemented with PDF/SVG vector outputs and accessible color/marker choices.
- Units, sample sizes, fit/holdout status, objective, nuisance fitting, and uncertainty meaning should appear in every caption.
- The same evidence categories and terminology should be used in text, code, result bundle, README, and captions.
- All source-data tables should include full precision, metadata, and a data dictionary.

---

## 9. Code, data, and reproducibility audit

### 9.1 Current build architecture

The current architecture has a sensible intended separation:

1. slow analyses produce `results.json`;
2. figures render from that bundle;
3. source-data CSVs export from the same bundle;
4. a paper build writes a manifest and verifies selected claims.

That is a good foundation. The implementation does not yet provide a single source of truth because scientific numbers are duplicated in the manuscript, verifier expectations, plot annotations, README, and cached bundle, and the manifest does not prove these are synchronized.

### 9.2 Manifest defects

At the reviewed head, the committed manifest records:

- a source commit older than the reviewed repository head;
- a bundle source commit older still;
- `git_dirty = true`;
- a verification time that is absent or not release-grade;
- 18 checked claims and zero failures;
- `verified = true` despite the above mismatches.

This is a category error: the verifier answers “do selected cached fields equal duplicated expected constants?” rather than “does this clean commit regenerate the submitted manuscript and all its artifacts?”

**Required release semantics**

A release verifier should fail unless all of the following are true:

```text
working_tree_clean
HEAD == manifest.source_commit
HEAD == results.source_commit
all declared inputs exist and match hashes
all declared outputs exist and match hashes
all manuscript numeric placeholders resolve from the result table
all figure/source-data values originate from the same bundle
all required tests pass
software environment is pinned
random seeds and stochastic summaries are recorded
```

### 9.3 Hard-coded claim duplication

The `_CLAIMS` table in the build layer duplicates expected numerical values. Such checks can catch accidental bundle changes, but they cannot establish correctness and create maintenance risk. A scientifically corrected result would fail until a developer manually changes the expected constant, while a stale manuscript could pass indefinitely.

**Required action:** generate a canonical results table with named fields, units, precision, and provenance. Use it to populate manuscript tables/captions or compare parsed placeholders. Keep regression tolerances only for numerical stability tests, not as the primary scientific verification contract.

### 9.4 Incomplete dependency hashing

The manifest hashes only a subset of data inputs. The computation also depends on analysis code, solver code, constitutive parameters, plotting code, manuscript text, source-data export logic, environment, and possibly files opened indirectly by loaders. Rendered figures and source-data outputs are not comprehensively hashed.

**Required action:** instrument file access or maintain an explicit dependency graph. Hash all direct inputs and outputs, including the environment lock/container digest. Record file sizes, MIME types, and generation commands.

### 9.5 Eight-figure/six-figure contract drift

`render_all()` returns eight figures, while the module docstring says six, the manuscript says six, and the figure README says six. This is a straightforward build-contract defect that should be automatically detectable.

**Required action:** define an expected figure registry once and use it to generate the manuscript figure list, README, render loop, output manifest, and source-data checks. The build must fail when counts or names differ.

### 9.6 Source-data export gaps

The exporter currently writes:

- two Figure 2 profile CSVs;
- one Figure 5 MAPE CSV;
- three Figure 6 profile CSVs;
- one combined Figure 7/8 residual CSV.

It omits Figure 3 and Figure 4 point data entirely, and omits central information for the other figures: surface matrices, MAPE profiles, accepted-set flags, Table 7 uncertainty, joint point predictions, exact-cup seed curves, discrepancy controls, Waszkiewicz profiles, baselines, geometry/flow/endpoint sensitivities, and build metadata.

**Required action:** export one tidy table per panel/series plus a machine-readable data dictionary. Add a test that every plotted artist derives from an exported field or a documented non-data annotation.

### 9.7 Precision defects

The current code has several round-then-aggregate paths. These should be treated as defects because derived values can change with the arbitrary display precision.

**Required action:** maintain raw floating-point arrays and derive every mean, quantile, range, comparison, and verdict from them. Add regression tests that recompute displayed summaries from exported point data and confirm agreement after final formatting only.

### 9.8 Missing baseline layer

No canonical baseline module exists for Paper A. This encourages post hoc comparisons and makes it hard to guarantee identical folds, weights, endpoints, and group definitions.

**Required action:** add a baseline registry with explicit fit/predict interfaces and include at least:

- O-trained MAPE-optimal constant by variety × solute;
- O-trained mean/median concentration;
- same-(T,p) O lookup;
- reduced mechanistic models with fixed rate or fixed inventory;
- shared and per-grind constants for in-sample compatibility analyses.

All baselines must consume the same train/test split and scoring function as the mechanistic model.

### 9.9 Test-suite interpretation

Fast tests that inspect cached fields are valuable for schema and regression checks. They do not reproduce the slow science. Skipping absent blocks can also turn an incomplete bundle into a passing test run.

**Required action:** use two modes:

- **fast CI:** schema, import, unit, analytic-profile, precision, and small-grid smoke tests;
- **release CI:** clean full slow build, no skips, deterministic seeds, output hash checks, manuscript/figure/source-data synchronization, and environment capture.

### 9.10 Provenance language embedded in result strings

Several analysis functions serialize verdict prose. This couples scientific interpretation to implementation and can preserve outdated claims after numbers change.

**Required action:** serialize facts, not verdicts. Recommended fields include:

```yaml
dataset_id:
campaign_relation:
observable:
fit_groups:
holdout_groups:
nuisance_parameters_fitted:
objective:
aggregation:
point_estimate:
profile_domain:
boundary_status:
baseline_id:
uncertainty_type:
```

Generate prose only in the manuscript layer.

---

## 10. Required numerical reruns and explicit acceptance tests

The following analyses are required before the current central claims can be retained. “Acceptance” here means that the analysis is complete and interpretable, not that it must favor the model.

### 10.1 Full-precision baseline-relative cross-grind transfer

**Rerun**

- Fit the O-grind mechanistic model and every predeclared baseline using identical groups, endpoints, losses, and weights.
- Freeze each fit and predict every C/F condition.
- Export condition-level observed values, predictions, percent/absolute/log errors, group identifiers, and fit metadata.

**Report**

- macro- and micro-averaged losses;
- paired condition-level loss differences;
- group/grind skill relative to each baseline;
- cluster-aware uncertainty;
- number of cases in which each model wins.

**Acceptance test**

- Every displayed score recomputes from exported full-precision point data.
- “Reasonable/useful transfer” is retained only with a predeclared practical threshold or material baseline-relative skill; otherwise use neutral absolute-error wording.

### 10.2 Endpoint mass × density transfer sensitivity

**Rerun**

- Use beverage masses spanning the source tolerance and a documented density range/distribution.
- For every scenario, rerun O fitting, point transfer, continuous profile-set transfer, and baselines.

**Report**

- endpoint volume/time by condition;
- selected parameters and boundary status;
- C/F loss and skill;
- worst-case condition and profile envelope;
- sign/ranking changes.

**Acceptance test**

- The manuscript uses “matched mass” only if mass is explicitly converted and propagated; otherwise it says “volume approximation.”
- Endpoint robustness claims refer to the main transfer estimand, not the blind residual.

### 10.3 Precision audit

**Rerun**

- Remove all intermediate `round()` calls from scientific calculations.
- Recompute blind, refit, joint, independent, geometry, flow, endpoint, LOCO, and profile summaries.

**Acceptance test**

- A unit test verifies that changing display precision does not alter any derived statistic or conclusion.
- Exported raw values reproduce all tables and captions.

### 10.4 Continuous profile-set and prediction-envelope convergence

**Rerun**

- Trace the profiled optimum continuously in log rate over expanded domains.
- Evaluate multiple grid densities only as verification.
- Define separate SSE and MAPE objective-tolerance sets.
- Propagate every accepted parameter pair to every C/F condition and baseline-relative loss.

**Report**

- boundary censoring;
- accepted-set endpoints;
- envelope convergence with grid/domain;
- threshold sensitivity (for example 5%, 10%, 20% descriptive rules);
- condition-wise and aggregate envelopes.

**Acceptance test**

- Doubling grid density and expanding the domain changes reported prediction-envelope limits by less than a predeclared numerical tolerance, or the result is explicitly reported as unresolved/domain-censored.

### 10.5 Objective and species sensitivity

**Rerun**

- Produce profiles for all species/varieties, not only representative Arabica caffeine/trigonelline.
- Compare SSE, MAPE, log-error, and a measurement-error-weighted likelihood where source uncertainty permits.

**Acceptance test**

- The central identifiability statement is scoped to the groups/objectives that actually show the broad profile.
- Any likelihood interval is based on an explicit observation model; descriptive sets remain labeled descriptive.

### 10.6 Hessian and local-curvature sensitivity

**Rerun**

- Vary finite-difference step, inventory grid, parameter scaling, and evaluation point.
- Compare numerical Hessian with automatic/analytic derivatives if feasible.

**Report**

- eigenvalues/eigenvectors with units/scaling;
- condition number sensitivity;
- coupling sensitivity;
- whether the Hessian is positive definite and numerically stable.

**Acceptance test**

- “Order 10³” and “near −1” are retained only if stable across a defensible range; otherwise report a qualitative flat direction and relegate local numbers to supplement.

### 10.7 Table 7 inventory-constrained profile

**Rerun**

- Convert Table 7 inventory with full unit/basis provenance and uncertainty.
- Intersect or combine that information with the O-grind objective under a stated statistical or descriptive rule.

**Acceptance test**

- Report the resulting rate range/profile and whether it remains boundary-censored.
- Show an uncertainty band, not a single vertical line.

### 10.8 Repeated-fit resampling for O-grind internal validation

**Rerun**

- Resample at the defensible experimental-unit level and repeat profiling/selection in each sample.
- Apply identical resamples to baselines.

**Acceptance test**

- Intervals are named for the estimand and resampling design.
- No nominal coverage claim is made from resampling dependent fold errors alone.

### 10.9 Pressure-to-flow map-form sensitivity

**Rerun**

- Compare the current map with at least one alternative plausible map/form and parameter uncertainty.
- Include condition-specific perturbations consistent with machine variability where justified.

**Acceptance test**

- Report effects on selected parameters, point transfer, profile envelopes, and baseline skill.
- Scope conclusions to assumed maps if measured flow is unavailable.

### 10.10 Grind-specific geometry sensitivity

**Rerun**

- Test plausible O/C/F-specific geometry or particle-size mappings, not only one global geometry perturbation.
- Avoid whole-percentage-point rounding.

**Acceptance test**

- The geometry conclusion is based on full-precision condition-level outputs and explicitly distinguishes global from grind-specific uncertainty.

### 10.11 Source measurement uncertainty

**Rerun**

- Propagate Angeloni replicate/RSD information where recoverable.
- Conduct a defensible sensitivity when replicate-level data are unavailable.

**Acceptance test**

- Report whether model-baseline differences are large relative to measurement variation.
- Avoid ranking differences smaller than data precision as substantive.

### 10.12 Same-model simulation with discrepancy and off-grid design

**Rerun**

- Vary generator/fitter mismatch, noise, seed, rate, inventory, endpoints, and operating conditions.
- Include off-grid input combinations and multiple endpoint masses.

**Acceptance test**

- Figure 6 shows no-discrepancy and discrepancy cases.
- Claims are limited to observation-operator behavior demonstrated across the tested design.

### 10.13 External Waszkiewicz temporal-shape analysis

**Rerun**

- Export observed bins, measured flow, predicted bins at each rate, fitted target level, and every nuisance sensitivity.
- Compare against simple temporal baselines, such as a scaled mean shape or low-order monotone curve.

**Acceptance test**

- The external mechanistic profile is interpreted relative to baseline shape fit and residual magnitude.
- Integrated-cup flatness is labeled algebraic under one scalar/one level.

### 10.14 Residual structure after target-level fitting

**Rerun**

- Replace Figure 8’s blind pooled residuals with within-group post-level-fit residuals.
- Test centered temperature, pressure, interaction, and grind effects with uncertainty.

**Acceptance test**

- Any claim that inventory cannot remove a pattern is based on residuals after inventory fitting.
- Group offsets are not confused with within-group condition structure.

### 10.15 Clean end-to-end release build

**Rerun**

- Start from a clean checkout of a tagged commit in a pinned environment.
- Run one command to compute all analyses, render the declared figure set, export all source data, build the manuscript numeric table, run release tests, and write a manifest.

**Acceptance test**

- clean tree before and after except declared outputs;
- exact commit equality across head/bundle/manifest;
- non-null timestamp and environment identifier;
- zero skipped required release tests;
- all input/output hashes present;
- manuscript, figure, README, source-data, and registry counts agree;
- rerunning produces numerically identical outputs within documented deterministic tolerances.

---

## 11. Suggested replacement wording for high-risk claims

### 11.1 Abstract — identifiability

**Current implication:** there is no interior/bounded rate solution.

**Suggested wording**

> The profiled objective had an interior numerical minimum within the tested bounds, but the descriptive near-optimal region was broad and remained open at the upper rate boundary. Thus, under the tested single-grind whole-cup design and objective, inventory and rate were weakly separated; the data localized a compensating profile more strongly than a unique rate.

### 11.2 Abstract — transfer

**Suggested wording before baseline analysis is completed**

> Freezing the selected O-grind calibration and applying it to C and F produced absolute group-level MAPEs of approximately 3–18%. These are internal, within-campaign holdout errors. Because a level-only O-trained benchmark nearly matches the current macro-MAPE, the incremental predictive contribution of the mechanistic condition response remains to be established.

**Suggested wording if a future baseline analysis shows material skill**

> Relative to a predeclared O-trained level-only baseline evaluated on identical C/F conditions, the frozen mechanistic calibration reduced [loss] by [estimate and interval], with gains concentrated in [groups].

### 11.3 Profile-set transfer

**Suggested wording**

> Across the finite O-grind MAPE objective-tolerance subset sampled on the current rate grid, aggregate C/F MAPE ranged from [x] to [y]. This is a descriptive grid-based sensitivity, not a confidence set; condition-wise envelopes and grid/domain convergence are reported in [figure/table].

### 11.4 Endpoint contract

**Suggested wording**

> Angeloni reports a 40 ± 2 g beverage endpoint, whereas the solver terminates at volume. The primary implementation uses 40 mL as an approximation and therefore does not exactly match beverage mass. We propagate source mass tolerance and a stated beverage-density range through the full calibration and transfer analysis.

Until that propagation is complete, replace “matched 40 g cups” with **“40 mL endpoint approximation to the reported 40 ± 2 g beverage.”**

### 11.5 Joint fit

**Suggested wording**

> A single shared inventory–rate pair fitted to O, C, and F reconstructed the same data at [full-precision score], compared with [score] for separate per-grind fits and [score] for a shared level-only model. This is an in-sample compatibility/flexibility comparison, not held-out evidence.

### 11.6 External Waszkiewicz analysis

**Suggested wording**

> On the independent Waszkiewicz shot, the target-level-profiled temporal objective had a shallow minimum near [rate], with a minimum MAPE of approximately [value] and material sensitivity to [nuisance choices]. The result indicates that the time bins contain rate-dependent shape information under the tested operator, but the high residual error and fitted target level preclude an absolute-concentration validation claim. The one-scalar integrated-cup profile is flat by construction when one multiplicative level is profiled.

### 11.7 Figure 4 title

> **Frozen O-grind calibration applied to C and F: absolute errors, level-only baselines, and profile-wise prediction envelopes**

### 11.8 Figure 7 title

> **Per-group blind and inventory-matched errors, with cross-condition model–data association**

### 11.9 Figure 8 title

> **Blind source-model residuals by operating condition; group offsets motivate target-level recalibration**

### 11.10 Discussion conclusion

> This case study shows that a low integrated-endpoint objective can coexist with weak parameter localization. Whether it also coexists with useful predictive transfer must be assessed against simple baselines under the identical holdout contract. Time-resolved observations, orthogonal inventory measurements, multiple endpoints, and measured hydraulic inputs are candidate ways to improve separation, but their value is design- and discrepancy-dependent.

---

## 12. Possible revised abstract

> **Background.** Whole-cup measurements are common targets for mechanistic coffee-extraction models, but integrated endpoints may weakly separate extractable inventory from release kinetics. We examined this issue in a multi-solute espresso model calibrated on fraction-resolved Schmieder/Pannusch data and recalibrated to the independent Angeloni chemical campaign.
>
> **Methods.** For each species, we profiled a multiplicative solid-inventory level and a Sherwood mass-transfer-rate multiplier against Angeloni O-grind concentrations using a 40 mL volume approximation to the reported 40 ± 2 g beverage endpoint. We examined SSE and MAPE profiles, local curvature, internal leave-one-condition-out refitting, frozen O-to-C/F within-campaign holdouts, shared multigrind fits, fraction-versus-aggregate observation operators, same-model simulations, and a target-level-profiled external Waszkiewicz TDS trajectory.
>
> **Results.** The O-grind objective contained a broad inventory–rate compensation valley. Its numerical point minimum was interior, but the descriptive near-optimal profile remained right-censored at the upper tested rate boundary; local curvature was correspondingly ill-conditioned. The selected O calibration produced C/F absolute MAPEs of approximately 3–18%, but a level-only O-trained benchmark nearly reproduced the current macro-average, so incremental mechanistic transfer skill remains unresolved. A shared multigrind fit was compatible with the pooled data in sample, with a small advantage over a shared level-only comparator at the displayed precision. Fraction-resolved scoring localized rate more strongly than sampled or exact integrated aggregates under the tested operators. On the independent Waszkiewicz trajectory, temporal bins produced a shallow target-level-profiled rate minimum with substantial residual error; the single integrated scalar was flat by construction after profiling one level.
>
> **Conclusions.** Under this model, design, endpoint approximation, parameter domain, and objective, whole-cup concentration weakly separates inventory from kinetics. Parameter localization, absolute holdout error, and baseline-relative predictive skill are distinct quantities and should be reported separately. Richer temporal observations, orthogonal inventory information, multiple endpoints, and measured flow are promising design additions, but require explicit uncertainty and discrepancy analysis.

This abstract intentionally avoids claiming successful transfer until the full-precision baseline analysis and endpoint propagation are complete.

---

## 13. Editorial and consistency comments

1. Replace code-style dataset labels such as ``pannusch2024`` and ``angeloni2023`` with normal citations in prose.
2. Use one notation for inventory (`c_s0`, `C0`, or a typeset symbol) and define its units once.
3. Use one notation for rate scale and state whether 1 is the source-calibrated value.
4. Define “macro-MAPE” mathematically and state group weights.
5. Avoid “point optimum” without specifying objective and data subset.
6. Replace “rate is not separately estimable” with “weakly localized over the tested domain” unless a statistical model supports estimability language.
7. Replace “whole valley” and “entire manifold” with the exact computed set.
8. Do not use “confidence interval” for the descriptive LOCO resampling output.
9. State every parameter bound wherever boundary behavior is discussed.
10. Report rates/inventories with units or explicitly as dimensionless multipliers.
11. Use “condition” consistently; do not alternate with “run,” “sample,” and “record” without defining levels.
12. State whether duplicate source extractions were averaged before repository entry.
13. Give the exact Angeloni off-grid points and whether they enter each analysis.
14. Clarify why TDS is absent from some species-specific analyses and present in Figures 7–8.
15. Define 5-CQA at first use and use one spelling (`5-CQA`, not a mix with `5CQA`).
16. Explain whether “solid inventory” is extractable mass concentration, dry-bean concentration, or a model-normalized state.
17. Avoid “exact cup” without adding “exact model-integrated cup.”
18. Avoid “actual cup” for source-derived or reconstructed responses.
19. Replace “positive control recovers the lost information” with “shows greater rate sensitivity under the fraction scoring operator.”
20. State whether profile objectives are normalized before the 10% rule.
21. Report absolute objective values as well as relative profiles.
22. Clarify whether the MAPE weighted median uses observation-specific denominators and how zero/near-zero values are handled.
23. State how ties in the weighted median and rate grid are resolved.
24. Report optimizer convergence flags and function evaluations.
25. Distinguish right-censoring of a descriptive set from an optimizer hitting a bound.
26. State whether Hessian derivatives use natural-log or base-10-log parameters.
27. Give the finite-difference step and inventory/rate scaling.
28. Replace “correlation” with “coupling diagnostic” consistently in figures and tables.
29. Put the Table 7 conversion formula in Methods or supplement.
30. Define “geometry sensitivity” precisely; identify every altered parameter.
31. Define the ±20% flow perturbation relative to what quantity and whether endpoint time is recomputed.
32. Do not round to whole percentage points in intermediate geometry outputs.
33. Use “percentage points” for differences between percentages.
34. Provide denominators and sample sizes next to all pooled metrics.
35. State whether MAPE values are means across conditions or means of group means.
36. Report medians/IQRs alongside means where distributions are skewed.
37. Avoid all-caps interpretive words in figure titles (`WORKS`, `STRUCTURED`, `CANNOT`).
38. Use sentence-case descriptive figure titles.
39. Ensure colors remain distinguishable in grayscale and for color-vision deficiencies.
40. Increase small legend/annotation text for journal reproduction size.
41. Add panel labels in consistent positions and type size.
42. Include exact units on every axis, including inventory surface axes.
43. State whether error bars are SD, SE, quantiles, or intervals and what they vary over.
44. Give random seed policy and number of stochastic realizations in the caption, not only text.
45. Add figure callouts for Figures 7 and 8 or remove/renumber them.
46. Update the figure-module docstring from six to the declared count.
47. Update the figure README and reproducibility section to match the declared count.
48. Add source-data files for Figures 3 and 4.
49. Include a source-data README with field definitions and hashes.
50. Generate vector figures in addition to PNG.
51. Remove review IDs (A2-09, M4, M6, B2, B5, MAJ-19) from submission prose and captions.
52. Remove statements that checks are “owed” or “data-blocked” from the manuscript.
53. Convert “Open gaps this paper defines” to conventional Limitations/Future Work.
54. Add author contributions, funding, conflicts, data availability, code availability, and AI-use declarations as required.
55. Include the full reference list in the manuscript.
56. Complete the literature search before stating novelty.
57. Replace “independent endpoint dataset” in the abstract with “independent campaign used for target recalibration”; within-campaign C/F is not a second independent dataset.
58. Clarify that Table 7 is from the same Angeloni campaign.
59. Clarify that Waszkiewicz is independent but its target level is fitted.
60. Report manuscript and artifact version/commit in a reproducibility footnote, not in scientific prose.

---

## 14. Submission-readiness checklist

### Scientific analysis

- [ ] Full-precision O→C/F model-versus-baseline analysis completed.
- [ ] Endpoint mass and density propagated through the main transfer estimand.
- [ ] Continuous profile-prediction envelopes shown and grid/domain convergence established.
- [ ] SSE and MAPE profile roles separated.
- [ ] All species/varieties checked or scope narrowed.
- [ ] Table 7 uncertainty converted and propagated.
- [ ] LOCO uncertainty relabeled or recomputed with repeated fitting.
- [ ] Flow-map form and grind-specific geometry sensitivities completed.
- [ ] Source measurement uncertainty assessed.
- [ ] External Waszkiewicz analysis benchmarked and plotted.
- [ ] Same-model discrepancy controls integrated into the evidence chain.
- [ ] Figure 8 reanalyzed after inventory fitting.

### Figures and source data

- [ ] Declared figure count agrees across manuscript, code, README, and manifest.
- [ ] Every figure is cited and has a self-contained caption.
- [ ] Figure 2 marks boundary censoring and includes/links the MAPE profile.
- [ ] Figure 3 includes a matched baseline and residual view.
- [ ] Figure 4 includes baselines and profile-wise envelopes.
- [ ] Figure 5 includes null comparators and full-precision outputs.
- [ ] Figure 6 separates empirical, synthetic, and external evidence.
- [ ] Figure 7 terminology and uncertainty corrected.
- [ ] Figure 8 title/inference corrected.
- [ ] Vector outputs generated.
- [ ] Full-precision source data and data dictionary supplied for every panel.

### Reproducibility

- [ ] Clean tagged release created.
- [ ] Pinned environment/container provided.
- [ ] One command regenerates analyses, figures, source data, and manuscript numbers.
- [ ] `HEAD == results.source_commit == manifest.source_commit` enforced.
- [ ] Dirty builds fail release verification.
- [ ] All direct inputs and outputs are hashed.
- [ ] Required release tests cannot skip missing blocks.
- [ ] Random seeds, hardware, software versions, and runtimes recorded.
- [ ] Manifest verifies manuscript/figure synchronization, not only cached constants.

### Manuscript conversion

- [ ] Repository note and review-management language removed.
- [ ] Full Methods with equations, parameters, solver, objectives, and uncertainty added.
- [ ] Results use evidence-neutral terminology.
- [ ] Limitations consolidated in Discussion.
- [ ] Full references included.
- [ ] Novelty search completed and archived.
- [ ] Data/code/declaration sections added.
- [ ] Abstract revised after the baseline and endpoint analyses.

---

## 15. Supporting references

1. **Schmieder, B. K. L., et al.** “Influence of Flow Rate, Particle Size, and Temperature on Espresso Extraction Kinetics.” *Foods* 12 (2023): 2871. <https://doi.org/10.3390/foods12152871>. Primary source for the 15-setting, repeated, ten-fraction campaign used in the Schmieder/Pannusch lineage.
2. **Angeloni, S., et al.** “Computer Percolation Models for Espresso Coffee: State of the Art, Results and Future Perspectives.” *Applied Sciences* 13 (2023): 2688. <https://doi.org/10.3390/app13042688>. Primary source for the target chemical campaign, beverage endpoint, and Table 7 inventory measurements.
3. **Pannusch, V. B., et al.** “Model-Based Kinetic Espresso Brewing Control Chart for Representative Taste Components.” *Journal of Food Engineering* 367 (2024): 111887. <https://doi.org/10.1016/j.jfoodeng.2023.111887>. Source model/calibration lineage.
4. **Waszkiewicz, R., et al.** “Under Pressure: Poroelastic Regulation of Flow in Espresso Brewing.” *Physics of Fluids* 38 (2026): 063113. <https://doi.org/10.1063/5.0319611>. Independent flow/TDS trajectory used for target-level-profiled temporal objective localization.
5. **Raue, A., et al.** “Structural and Practical Identifiability Analysis of Partially Observed Dynamical Models by Exploiting the Profile Likelihood.” *Bioinformatics* 25 (2009): 1923–1929. <https://doi.org/10.1093/bioinformatics/btp358>. Foundational reference for profile-based practical-identifiability analysis and unbounded/asymmetric profiles.
6. **Wieland, F.-G., et al.** “On Structural and Practical Identifiability.” *Current Opinion in Systems Biology* 25 (2021): 60–69. <https://doi.org/10.1016/j.coisb.2021.03.005>. Clarifies structural versus practical identifiability and limitations of local uncertainty summaries.
7. **Simpson, M. J., and O. J. Maclaren.** “Profile-Wise Analysis: A Profile Likelihood-Based Workflow for Identifiability Analysis, Estimation, and Prediction with Mechanistic Mathematical Models.” *PLoS Computational Biology* 19 (2023): e1011515. <https://doi.org/10.1371/journal.pcbi.1011515>. Supports propagating profile sets into prediction sets and distinguishing parameter and prediction uncertainty.
8. **Bengio, Y., and Y. Grandvalet.** “No Unbiased Estimator of the Variance of K-Fold Cross-Validation.” *Journal of Machine Learning Research* 5 (2004): 1089–1105. <https://www.jmlr.org/papers/v5/grandvalet04a.html>. Relevant to dependence among overlapping cross-validation folds and cautious interpretation of fold-error variance.
9. **Gutenkunst, R. N., et al.** “Universally Sloppy Parameter Sensitivities in Systems Biology Models.” *PLoS Computational Biology* 3 (2007): e189. <https://doi.org/10.1371/journal.pcbi.0030189>. Background on broad sensitivity spectra and model-manifold geometry.
10. **Transtrum, M. K., Machta, B. B., and Sethna, J. P.** “Geometry of Nonlinear Least Squares with Applications to Sloppy Models and Optimization.” *Physical Review E* 83 (2011): 036701. <https://doi.org/10.1103/PhysRevE.83.036701>. Background for local curvature and manifold interpretations.
11. **Tönsing, C., Timmer, J., and Kreutz, C.** “Cause and Cure of Sloppiness in Ordinary Differential Equation Models.” *Physical Review E* 90 (2014): 023303. <https://doi.org/10.1103/PhysRevE.90.023303>. Relevant to distinguishing sloppiness, scaling, design, and identifiability.
12. **Roberts, D. R., et al.** “Cross-Validation Strategies for Data with Temporal, Spatial, Hierarchical, or Phylogenetic Structure.” *Ecography* 40 (2017): 913–929. <https://doi.org/10.1111/ecog.02881>. General guidance for matching validation splits to dependence and intended generalization.

The final manuscript should cite the source papers directly and should not rely on this review’s summaries as substitutes for the original methods and data descriptions.

---

## 16. Overall recommendation

**Major revision before journal submission.**

The revision has made real progress. It now acknowledges the 40 g/40 mL issue, tests rate-domain/grid sensitivity, adds same-model discrepancy controls and residual diagnostics, expands the slow build, and uses a much more disciplined evidence taxonomy. The broad inventory–rate profile under the tested whole-cup O-grind observation map remains a credible and potentially publishable case-study result.

The paper’s current second pillar—successful predictive transfer despite non-identifiability—is not yet demonstrated. Its absolute C/F error is almost matched by a level-only baseline; the endpoint sweep does not evaluate the headline transfer estimand; the profile-set propagation is a coarse descriptive grid subset; several summaries still round before aggregation; and Figure 8 makes an inference contradicted by the group-specific level parameter. The stale, dirty, cross-commit manifest and six-versus-eight figure drift further prevent the present artifact from functioning as a submission-grade reproducible record.

A strong revision should make the baseline-relative question explicit and allow the answer to be negative or heterogeneous. Even if the mechanistic transfer proves no better than a constant, the paper can make an important contribution: it would show concretely that a visually good, low-error, cross-grind endpoint reconstruction may be generated largely by level calibration while leaving mechanism and condition response weakly supported. That conclusion would be sharper, more surprising, and better aligned with the paper’s methodological motivation than an unsupported “reasonable transfer” label.

