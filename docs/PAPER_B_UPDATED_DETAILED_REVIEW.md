# Detailed technical review of the updated `PAPER_B_DRAFT.md`

**Repository:** [`trbrewer/puckworks`](https://github.com/trbrewer/puckworks)  
**Review snapshot:** commit [`c6fe9b45d4e273fc83c72db4d5e31dcd7d281b5e`](https://github.com/trbrewer/puckworks/commit/c6fe9b45d4e273fc83c72db4d5e31dcd7d281b5e)  
**Commit subject:** “2.x: Paper B MAJ-04 (achieved-predictor RSM) + MAJ-09 (data-driven Figure 2)”  
**Manuscript reviewed:** [`docs/PAPER_B_DRAFT.md`](https://github.com/trbrewer/puckworks/blob/c6fe9b45d4e273fc83c72db4d5e31dcd7d281b5e/docs/PAPER_B_DRAFT.md)  
**Figures reviewed:** Paper B Figures 1–5 and their plotting code  
**Previous review snapshot:** [`8ca073fdda68a2032d321abe5401eb5d531d6e88`](https://github.com/trbrewer/puckworks/commit/8ca073fdda68a2032d321abe5401eb5d531d6e88)  
**Review date:** 2026-07-13  
**Recommendation:** **Major revision before journal submission**

---

## 1. Scope, review basis, and limitations

This is a second detailed technical review of Paper B. It focuses both on the scientific manuscript and on whether the revised prose, figures, data representations, and analysis code now implement the same inferential contracts.

The review covers:

- the exact updated [`PAPER_B_DRAFT.md`](https://github.com/trbrewer/puckworks/blob/c6fe9b45d4e273fc83c72db4d5e31dcd7d281b5e/docs/PAPER_B_DRAFT.md);
- all five rendered Paper B figures;
- [`puckworks/harness.py`](https://github.com/trbrewer/puckworks/blob/c6fe9b45d4e273fc83c72db4d5e31dcd7d281b5e/puckworks/harness.py), especially the Result 1 statistics/RSM, cross-pressure analyses, and N-tube analysis;
- [`puckworks/figures.py`](https://github.com/trbrewer/puckworks/blob/c6fe9b45d4e273fc83c72db4d5e31dcd7d281b5e/puckworks/figures.py);
- [`analysis/lopo_cv.py`](https://github.com/trbrewer/puckworks/blob/c6fe9b45d4e273fc83c72db4d5e31dcd7d281b5e/analysis/lopo_cv.py) and [`analysis/residual_autocorr.py`](https://github.com/trbrewer/puckworks/blob/c6fe9b45d4e273fc83c72db4d5e31dcd7d281b5e/analysis/residual_autocorr.py);
- the committed [`paper_b_evidence_matrix.csv`](https://github.com/trbrewer/puckworks/blob/c6fe9b45d4e273fc83c72db4d5e31dcd7d281b5e/puckworks/data/paper_b_evidence_matrix.csv);
- the committed Schmieder-derived run-level cup-mass table used by the analysis; and
- primary supporting literature on the source experiments, espresso-bed infiltration/swelling/erosion, cross-validation dependence, regression bootstrap, and post-model-selection inference.

I performed a static traceability audit and targeted independent recomputations from the committed Schmieder table. Those recomputations use the manuscript’s retained seven-term TDS/BR 1/2 response-surface specification and are reported in Section 9. I did not claim a clean-room rerun of every slow simulation, every model component, or the complete repository test suite in a newly provisioned, environment-locked installation. The repository still lacks a single frozen Paper B build that emits one immutable numerical-results bundle and then renders every table and figure from that bundle. Comments below distinguish definite implementation/reporting defects from analyses that require additional numerical work.

### Exact reviewed artifacts

| Artifact | SHA-256 |
|---|---|
| `PAPER_B_DRAFT.md` | `033d8b2a304cbbc7d69608905dcf82d4546c02eef8d7ef8c48f4a0872bab71ea` |
| `puckworks/harness.py` | `21490be63f29fd20e74d6f2fb8b07aec57e3948bae882d8073042eb5f3929e8f` |
| `puckworks/figures.py` | `b5ce2fca054f95bd6d5bc901d2b5134f3e72767e654019651d81adbfc83f409b` |
| `analysis/lopo_cv.py` | `1cbacc9325c51b2ffbd50cd7e306e6980ffa88741a8ee71aad3a9f55795c9010` |
| `analysis/residual_autocorr.py` | `c99da7b64d792b9f4ed15db5f76b59dc4d05999bcdc21206f0f02a1ff1048fa0` |
| `paper_b_evidence_matrix.csv` | `c1e6aae3e2b43bfed2c3224c22edd4233d9e94d29a189a3e92d5ff8634faa6be` |
| committed Schmieder cup-mass table | `39b7c16f9d9da614f151f46cb0db1440d43f150fbf49d3d2119f3f2fa1622f43` |
| Figure 1 PNG | `26cecac1f88341936e73eb30025d3b0c3ccb1d8406b0f99d391c0caf647140c2` |
| Figure 2 PNG | `68f1f76ec67ad2d625f2f935ff476d0433b4e9b7e1a440b5833752cdd5089792` |
| Figure 3 PNG | `3af0b0c53db6c8aa0223567e41a43a48774595f417f5a5e5b2a5fd736ac7b716` |
| Figure 4 PNG | `5a8e8c2d1a6158ebfb135cbfd5e1913e84e1909383392d75a03aee06b9f3a340` |
| Figure 5 PNG | `2ae261bf752e8a192eb77df3db661630cdc809de028ba9f3e1e0833c00df9240` |

---

## 2. Executive assessment

The updated draft is **materially better** than the version reviewed previously. The authors have corrected the most serious source-design wording in the main Result 1 narrative, added an achieved-predictor RSM path, replaced the hard-coded Figure 2 grid with a committed evidence table, corrected the distinction between `cond(X)` and `cond(XᵀX)`, added a fixed-design residual bootstrap, added leave-one-pressure-out calibration checks, narrowed the swelling/fines conclusion to an isolated fixed-pressure resistance branch, labeled the Foster curve as a model reproduction, and explicitly downgraded Result 3 from a stability theorem to an exploratory finite-time concentration calculation. These are substantial and welcome changes.

The paper’s strongest publishable thesis remains:

> **Matched integrated observables can establish model capacity, incompatibility, and the need for temporal structure, while still being insufficient to identify a unique espresso-bed mechanism.**

That thesis is plausible and useful. The current draft, however, is still not submission-ready because several newly revised quantitative contracts are internally inconsistent. The most important findings are:

1. **The primary RSM result in the prose is not the result shown in Figure 1.** The text reports the nominal-target-predictor, case-bootstrap result—vertex 1.73 with interval [1.68, 1.81]—whereas Figure 1 uses achieved predictors and the fixed-design residual bootstrap—vertex about 1.74 with interval about [1.70, 1.82]. The revised code has both analyses, but the manuscript has not selected and consistently reported one primary estimand.

2. **The achieved-predictor RSM evaluates “central” flow and temperature using the wrong mask.** The code averages every TDS/BR 1/2 row with grind 1.7, spanning several flow and temperature settings, instead of the actual central design setting, experiment 7. The numerical effect on the vertex is small, but the method contract is wrong and the figure annotation is therefore misleading.

3. **The descriptive linear-trend interval has a definite calculation error.** `result1_design_aware_stats` uses `1.96 × SE` while reporting a 95% interval. With 12 runs and 10 residual degrees of freedom, the classical t-based interval is approximately **[1.16, 3.36]**, not **[1.29, 3.23]**.

4. **The RSM cross-validation remains inconsistent with the revised source contract.** `lopo_rsm_design_point` still uses nominal target flow and target temperature, while the source RSM used achieved flow and temperature. Its module header also says “18 design points,” although the source and committed data contain **15 settings** and 48 complete TDS/BR 1/2 run rows.

5. **The cross-pressure section mixes four different summaries.** The values 0.512/0.356/0.522 g/s described as “full-precision held-out means” are produced by the campaign-wide shared calibration over the ten off-9-bar pressures, not by leave-one-pressure-out refits. The manuscript first reports LOPO all-pressure means and then labels a different, shared-calibration summary as held out.

6. **The new LOPO function still averages rounded values.** `cross_pressure_loco` rounds every pressure-level RMSE before computing the mean, reproducing in that function the precision practice that was fixed in `cross_pressure_discrimination`.

7. **“Zero-parameter” remains an inaccurate complexity label.** The Φ(t) branch has zero *additional coefficients fitted to the scored flow trace*, but it imports the shared two-parameter equilibrium calibration and donor quantities from other observables. Figure 3’s “0p” labels and the prose’s “zero-parameter poroelastic Φ(t)” invite the wrong interpretation.

8. **Result 2 remains an in-sample reconstruction comparison with strongly structured residuals.** The cubic is fitted and scored on the same time series, and the mean decimated Durbin–Watson value near 0.01 shows severe residual structure. The conclusion should be about reconstruction within a defined window and tested model set, not a validated requirement or mechanism.

9. **The N-tube floor sweep is useful but does not establish general robustness.** It establishes that one endpoint classification is unchanged over selected floors at one grind, pressure, horizon, initialization, tube count, control law, and zero-lateral setting. It does not establish robustness to timestep, horizon, N, start state, pressure, grind, stochastic realization, or a physical exchange closure. The code/figure sweep includes `10⁻⁶`, while the prose states `10⁻⁹…10⁻¹⁵`.

10. **The document is still an internal project draft.** It retains “review-endorsed,” ROADMAP instructions, function names as methods, an “Open gaps” section, and a “Status & to-do (NOT for the manuscript body)” section. A conventional Methods section, references, captions, data/code statement, and pinned release remain explicitly “owed.”

### Recommended editorial disposition

| Dimension | Assessment |
|---|---|
| Scientific question | Important; suitable for a methodological/mechanistic modeling audience |
| Central conceptual contribution | Strong matched-observable and null-first framing |
| Improvement since previous review | Substantial; several major overclaims and implementation defects were corrected |
| Current statistical support | Directionally informative, but internally inconsistent in the RSM and cross-pressure sections |
| Current mechanistic support | Supports capacity and conditional incompatibility; not unique identification |
| Current numerical support for Result 3 | Exploratory endpoint demonstration only |
| Current manuscript form | Internal revision document, not a submission manuscript |
| Recommendation | **Major revision** |

---

## 3. What has improved since the previous review

The revision should receive explicit credit for the following changes. They should be preserved while the remaining issues are repaired.

| Previous concern | Current status | Review assessment |
|---|---|---|
| Experimental-unit wording | Main Result 1 now states three independent extraction repetitions per setting and six at the center | **Substantially improved**, but stale contradictory text remains in a returned code note and §7 |
| RSM predictor contract | `schmieder_rsm_refit` now supports achieved predictors and Figure 1 uses them | **Partially resolved**; prose, figure, bootstrap, central mask, and LOPO are not harmonized |
| RSM bootstrap | Fixed-design residual bootstrap added; case bootstrap retained for comparison | **Improved**, but primary method remains inconsistent in prose and model-selection uncertainty is excluded |
| Condition number | `κ₂(X)` and `κ₂(XᵀX)` are now named correctly | **Resolved in labeling**, but predictors are still fit on an avoidably ill-conditioned raw scale |
| Figure 1 “raw monotone” wording | Replaced by “observed cell means increase” | **Improved**, though raw run points are still hidden |
| Figure 2 hard-coding | Replaced by a committed CSV consumed by the plotting function | **Substantially resolved**, but status ontology and one provenance classification remain problematic |
| Cross-pressure precision bug | Shared-calibration summaries now retain raw values until display | **Resolved in one function**; the new LOPO function still averages rounded values |
| Leave-one-pressure-out analysis | Added and interpreted mainly as calibration stability | **Improved**, but manuscript mixes LOPO and shared-calibration summaries |
| Pressure “regimes” | Bins explicitly called descriptive/not preregistered | **Improved**, although the abstract still says transfer is “regime-dependent” |
| Swelling/fines overclaim | Narrowed to isolated resistance-only branches under fixed pressure | **Largely resolved**; the section heading still says “excludes” |
| Foster panel | Explicitly labeled a reproduced model curve, not measured data | **Resolved** |
| Coupled composition | Extraction-only equality labeled an implementation identity | **Resolved conceptually**; figure remains redundant and in-sample |
| N-tube “stability” claim | Renamed finite-time concentration; floor dependence exposed; integration rerun at each floor | **Meaningful improvement**, but broad robustness language still exceeds the tested sweep |
| Single-source build | Figure 1 now consumes one RSM result rather than refitting inside plotting | **Local improvement only**; there is still no frozen paper-wide results bundle/build |
| Source-year terminology | Internal identifiers unchanged | **Not resolved**; `waszkiewicz2025` and `mo2023_2` no longer match publication years |

---

## 4. Prioritized required-action matrix

Priority definitions:

- **P0 — validity-critical:** resolve before submission because it changes a central number, estimand, interpretation, or reproducibility claim.
- **P1 — major reporting/reproducibility:** required for a defensible paper, but unlikely by itself to reverse the central qualitative thesis.
- **P2 — editorial/presentation:** required for publication quality and reader comprehension.

| ID | Priority | Required action | Acceptance criterion |
|---|---:|---|---|
| AR-B2-01 | P0 | Convert the internal revision document into a conventional manuscript. | Remove review instructions, “review-endorsed,” ROADMAP narration, function-name methods, open-task scaffolding, and the status/to-do section; add full Methods, references, captions, Data/Code Availability, and limitations. |
| AR-B2-02 | P0 | Select one primary RSM estimand and use it consistently. | Main text, abstract, Figure 1, caption, tables, and results bundle all report the achieved-predictor, fixed-design analysis—or a clearly justified alternative—with one vertex, one interval, and one fit statistic. |
| AR-B2-03 | P0 | Correct the achieved-predictor central-setting mask. | Evaluate the RSM cross-section at the achieved flow/temperature of experiment 7, or explicitly define and justify another reference point; do not call the average of every grind-1.7 condition “central.” |
| AR-B2-04 | P0 | Correct the Result 1 trend interval and statistical hierarchy. | Use the appropriate t critical value or a justified alternative; identify the 15 settings, 48 complete run rows, and 12 central-cell runs correctly; remove stale “single-experiment-per-cell/no between-experiment replication” language. |
| AR-B2-05 | P0 | Make RSM uncertainty conditionality explicit and address model selection. | State that the current bootstrap conditions on the retained seven-term model; either repeat backward elimination inside resampling or label the interval as conditional post-selection inference. Report the joint concave-and-in-domain fraction, not two separate fractions as if jointly 100%. |
| AR-B2-06 | P0 | Center/scale the RSM computation and perform influence sensitivity. | Fit on centered/scaled achieved predictors, back-transform the vertex, and show that fitted values/vertex are invariant; report leave-one-run/robust sensitivity for the influential observation. |
| AR-B2-07 | P0 | Repair RSM leave-one-setting-out validation. | Hold out each of the 15 experiment IDs with all repetitions together, fit using achieved flow/temperature, and report n=15, PRESS/Q²/RMSE and per-setting residuals; remove the “18 design points” statement. |
| AR-B2-08 | P0 | Separate all cross-pressure estimands. | Report and label separately: shared calibration/all 11; shared calibration/off-9 ten; LOPO/all 11; LOPO/off-9 ten. Do not call shared-calibration values “held out.” |
| AR-B2-09 | P0 | Preserve full precision in `cross_pressure_loco`. | Store raw pressure-level RMSE values, aggregate raw values, and round only for display; add a regression test analogous to the one for `cross_pressure_discrimination`. |
| AR-B2-10 | P0 | Correct parameter-count labels. | Replace “0p/zero-parameter” with “0 additional coefficients fitted to this flow trace,” and give a complete table of flow-fitted, same-campaign donor-fitted, external-dataset fitted, literature-fixed, and chosen numerical quantities. |
| AR-B2-11 | P0 | Make the Result 2 comparison dependence-aware or explicitly in-sample. | Either use blocked/rolling/whole-pressure validation with a correlated-error model, or label the cubic strictly as an in-sample flexibility bound and narrow “time variation is required” to an in-window reconstruction statement. |
| AR-B2-12 | P0 | Reframe Result 3 or perform a genuine robustness study. | Either move it to an exploratory supplement, or provide trajectories, timestep/N/horizon/start/pressure/grind/realization sweeps, conservation checks, a physical lateral operator, and a stability/finite-time-growth analysis. |
| AR-B2-13 | P0 | Build the paper from one immutable results bundle. | One command writes versioned machine-readable results, tables, and vector figures; figures consume that bundle only; bundle includes commit, data hashes, environment, seeds, parameter provenance, and numerical tolerances. |
| AR-B2-14 | P1 | Show raw Result 1 run data and label derived outcomes correctly. | Figure 1a shows all 12 run-level points; caption states that TDS cup mass/EY was derived by integrating each run’s fitted fraction kinetics; error bars are defined. |
| AR-B2-15 | P1 | Add uncertainty to the RSM curve, not only the vertex. | Plot a pointwise or simultaneous bootstrap envelope for the achieved-condition cross-section, with the conditional nature stated. |
| AR-B2-16 | P1 | Formalize the Figure 2 evidence ontology. | Publish a schema/data dictionary defining each dimension and status, with source/rationale fields and auditable criteria; correct static-channeling parameter provenance. |
| AR-B2-17 | P1 | Quantify uncertainty and residual structure in Result 2. | Show residual traces and ACF; test decimation/block-length sensitivity; use source measurement SD/replicate information where available; report uncertainty on RMSE differences. |
| AR-B2-18 | P1 | Show LOPO evidence in Figure 3 or label the panel unambiguously. | Figure 3c either displays LOPO results or explicitly states “shared campaign-wide calibration; not LOPO,” with LOPO shown elsewhere. |
| AR-B2-19 | P1 | Narrow pressure-regime wording. | Remove “regime-dependent” from the abstract unless regimes are prespecified and tested; describe pressure-varying relative reconstruction error instead. |
| AR-B2-20 | P1 | Keep the swelling/fines result as a conditional sign constraint. | Replace the heading’s “excludes” with “constrains”; supply complete primary citations and define the fixed-pressure/control assumptions. |
| AR-B2-21 | P1 | Document static-channeling calibration and uncertainty. | Give the calibration dataset, observable, grinder mapping, fitted closure, uncertainty, parameter portability limits, and sensitivity of prominence/peak location to calibration and grid resolution. |
| AR-B2-22 | P1 | Update publication metadata and references. | Cite Waszkiewicz et al. as 2026 and Mo et al. swelling as 2022; distinguish internal dataset keys from article years; supply full references for every model and lemma. |
| AR-B2-23 | P1 | Produce journal-quality figure files. | Provide PDF/SVG or journal-compliant 300–600 dpi raster outputs; current manuscript figures are 150 dpi PNGs. |
| AR-B2-24 | P2 | Rewrite the abstract around the scientific result rather than repository history. | Remove the internal pipeline-correction narrative and clarify “two focal empirical datasets” versus the larger set of calibration/supporting sources. |
| AR-B2-25 | P2 | Reduce figure rhetoric and annotation density. | Move long interpretive paragraphs from plots into captions; increase legibility and avoid claims such as “robust result” inside figures. |
| AR-B2-26 | P2 | Complete and document the related-work search. | Record databases, dates, queries, screening criteria, included studies, and bounded novelty claims. |

---

## 5. Detailed major comments

### MAJ-01 — The document is still an internal review artifact, not a submission manuscript

The draft opens with internal revision history, verb instructions, figure paths, and a “review-endorsed” title ([lines 1–17](https://github.com/trbrewer/puckworks/blob/c6fe9b45d4e273fc83c72db4d5e31dcd7d281b5e/docs/PAPER_B_DRAFT.md#L1-L17)). The Methods section explicitly says a conventional Methods section is “still owed” ([lines 112–116](https://github.com/trbrewer/puckworks/blob/c6fe9b45d4e273fc83c72db4d5e31dcd7d281b5e/docs/PAPER_B_DRAFT.md#L112-L116)). The paper then contains “Open gaps” and “Status & to-do (NOT for the manuscript body)” sections ([lines 393–463](https://github.com/trbrewer/puckworks/blob/c6fe9b45d4e273fc83c72db4d5e31dcd7d281b5e/docs/PAPER_B_DRAFT.md#L393-L463)).

This is not a cosmetic problem. The missing material includes equations, parameter definitions, calibration/evaluation splits, uncertainty methods, numerical tolerances, source-data transformations, references, and release information needed to assess the work independently.

**Required action:** Create a clean manuscript with conventional sections and move all review history, code-function narration, action tracking, and verb rules to a response-to-review or project document. Function names may appear in a reproducibility appendix, but not as substitutes for a statistical or physical method.

---

### MAJ-02 — State one inferential thesis and clarify what “two datasets” means

The abstract says the work determines what “two published datasets” can discriminate ([lines 23–26](https://github.com/trbrewer/puckworks/blob/c6fe9b45d4e273fc83c72db4d5e31dcd7d281b5e/docs/PAPER_B_DRAFT.md#L23-L26)), while the Methods list includes Schmieder, Waszkiewicz, Cameron, Román-Corrochano, and Lee, and other sections rely on Foster, Mo, and Fasano models. The intended meaning appears to be **two focal empirical evaluation datasets**, with other sources supplying calibration, comparison models, or mechanistic priors.

The paper will be easier to evaluate if it states one thesis and one evidence hierarchy. A defensible version is:

> Under explicitly matched observation operators, the available whole-cup and whole-trace data can reject some model instances and establish capacity or temporal structure, but they do not uniquely identify a bed mechanism.

**Required action:** Define “focal evaluation dataset,” “calibration source,” “donor observable,” “literature-fixed model,” and “exploratory synthetic model.” Use those categories consistently in the abstract, Methods, evidence matrix, and Discussion.

---

### MAJ-03 — The source design is improved in the prose, but the hierarchy and derived response still need exact treatment

The revised main text correctly says each Schmieder setting had three independently prepared extraction repetitions and the center had six ([lines 131–138](https://github.com/trbrewer/puckworks/blob/c6fe9b45d4e273fc83c72db4d5e31dcd7d281b5e/docs/PAPER_B_DRAFT.md#L131-L138)). That matches the source’s face-centered design of 15 settings with three repetitions, six at the center.

Two corrections remain necessary:

1. The returned `experimental_unit_note` still says “ONE experiment per dial … NO between-experiment replication; the within-cell spread is a within-experiment variance” ([`harness.py` lines 634–640](https://github.com/trbrewer/puckworks/blob/c6fe9b45d4e273fc83c72db4d5e31dcd7d281b5e/puckworks/harness.py#L634-L640)). Section 7 repeats “single-experiment-per-cell structure” ([draft lines 414–419](https://github.com/trbrewer/puckworks/blob/c6fe9b45d4e273fc83c72db4d5e31dcd7d281b5e/docs/PAPER_B_DRAFT.md#L414-L419)). This contradicts both the source and the revised main text.

2. The “mass in cup” outcome is **derived**, not directly measured at the endpoint. Schmieder et al. fitted extraction kinetics to six analyzed fractions for each run, then integrated the individual run’s fitted kinetics to 20, 40, and 60 g beverage endpoints. Figure 1’s label “measured TDS-EY” is therefore too simple.

**Required action:** Use a hierarchy such as:

- 15 nominal settings/experiment IDs;
- 48 complete extraction runs for TDS/BR 1/2;
- ten collected fractions, six chemically analyzed fractions per run;
- run-specific fitted concentration kinetics;
- derived run-level 40 g cup TDS mass and EY;
- one campaign, one principal coffee, one machine.

Call Figure 1 data “source-derived run-level TDS-EY” or “TDS-EY derived from integrated run-specific fraction kinetics.”

---

### MAJ-04 — The raw central-cell comparison is descriptive and post hoc; preserve that scope

The central cell means and Welch contrasts are correctly reported numerically. Independent recomputation gives:

- dial 1.4: 18.267%, n=3, SD 0.552;
- dial 1.7: 19.381%, n=6, SD 0.159;
- dial 2.0: 19.622%, n=3, SD 0.071;
- 1.4−1.7: −1.114 EY-points, Welch 95% CI [−2.414, 0.187], p=0.0675;
- 1.7−2.0: −0.241 EY-points, Welch 95% CI [−0.422, −0.060], p=0.0161.

The manuscript appropriately notes that achieved flow and pressure differ across the three nominal conditions. It should go one step further and identify the contrast analysis as a **secondary descriptive reanalysis of selected axis/center settings**, not the source’s primary factorial inference. With only three dial levels, post hoc selection of adjacent contrasts, and confounding by achieved conditions, the p-values should not carry more weight than the effect estimates and intervals.

**Required action:** Predeclare one primary contrast or label both contrasts exploratory. Consider a multiplicity-adjusted presentation, but do not let multiplicity mechanics obscure the larger issue: these are nominal-setting contrasts, not causal dial effects.

---

### MAJ-05 — The reported trend interval uses the wrong critical value

The code computes the slope interval as `slope ± 1.96 × SE` ([`harness.py` lines 616–622](https://github.com/trbrewer/puckworks/blob/c6fe9b45d4e273fc83c72db4d5e31dcd7d281b5e/puckworks/harness.py#L616-L622)) and the manuscript reports [1.29, 3.23] ([draft lines 129–130](https://github.com/trbrewer/puckworks/blob/c6fe9b45d4e273fc83c72db4d5e31dcd7d281b5e/docs/PAPER_B_DRAFT.md#L129-L130)). For a classical OLS interval with n=12 and two estimated coefficients, the residual degrees of freedom are 10 and the t critical value is about 2.228.

Independent recomputation gives:

- slope = 2.258 EY-points per dial;
- SE = 0.4937;
- t-based 95% CI = **[1.158, 3.358]**;
- p = 0.00102.

This numerical correction does not change the sign, but it is a definite reporting error.

**Required action:** Use a t interval, or state and justify a robust/clustered alternative. Because the predictor has only three unique levels and achieved conditions are confounded, keep this as a descriptive trend rather than a causal estimate.

---

### MAJ-06 — The revised RSM has two incompatible “primary” analyses

The source RSM used set grind plus experimentally achieved flow and temperature. The updated code now supports that contract and Figure 1 consumes `schmieder_rsm_refit(predictors="achieved")` ([`figures.py` lines 67–78](https://github.com/trbrewer/puckworks/blob/c6fe9b45d4e273fc83c72db4d5e31dcd7d281b5e/puckworks/figures.py#L67-L78)). Figure 1 therefore reports approximately:

- achieved-predictor vertex 1.744;
- fixed-design residual-bootstrap 95% interval about [1.700, 1.819];
- adjusted R² about 0.643.

The manuscript’s main Result 1 paragraph instead reports:

- target-predictor vertex 1.73;
- 2000 **case** bootstrap interval [1.68, 1.81];
- adjusted R² 0.65 ([draft lines 149–160](https://github.com/trbrewer/puckworks/blob/c6fe9b45d4e273fc83c72db4d5e31dcd7d281b5e/docs/PAPER_B_DRAFT.md#L149-L160)).

Section 7 then mentions the residual interval [1.69, 1.80] and the achieved-predictor sensitivity ([lines 395–411](https://github.com/trbrewer/puckworks/blob/c6fe9b45d4e273fc83c72db4d5e31dcd7d281b5e/docs/PAPER_B_DRAFT.md#L395-L411)). A reader encounters three related but nonidentical reporting contracts.

**Required action:** Make the achieved-predictor, fixed-design residual-bootstrap result the primary analysis because it matches the source predictor contract and the intended fixed-design interpretation. Put the nominal-predictor and case-bootstrap values in a sensitivity table. Use the same values in the abstract, Results, figure, caption, and supplementary results bundle.

---

### MAJ-07 — The achieved-predictor “central” cross-section is evaluated at the wrong reference condition

For achieved predictors, the code defines the center as every row with `G == 1.7` and averages their achieved flow and temperature ([`harness.py` lines 982–990](https://github.com/trbrewer/puckworks/blob/c6fe9b45d4e273fc83c72db4d5e31dcd7d281b5e/puckworks/harness.py#L982-L990)). This includes multiple design settings at grind 1.7—flow-axis, temperature-axis, and center—not only the central setting.

Independent recomputation shows:

| Reference | Mean achieved flow | Mean achieved temperature | Vertex | Cross-section prediction at dial 1.7 |
|---|---:|---:|---:|---:|
| Current all-`G=1.7` mask | 1.9108 mL/s | 87.9907 °C | 1.74384 | 3.92174 g |
| True center, experiment 7 | 1.9011 mL/s | 88.2579 °C | 1.74315 | 3.92706 g |

The numerical difference is small, which is reassuring, but the annotation “mean achieved central flow/temp” in the figure code is factually wrong.

**Required action:** Mask experiment 7 or the nominal triplet `(target F=2, G=1.7, target T=89)`. Return the exact reference definition in the results bundle. Add a unit test that confirms the center mask contains six runs from experiment 7 only.

---

### MAJ-08 — The RSM interval is conditional on both the retained model and the response-surface form

The source used backward elimination at α=0.05 from a full quadratic model. The repository refit fixes the retained seven-term TDS/BR 1/2 specification and resamples residuals without repeating selection ([`harness.py` lines 1007–1043](https://github.com/trbrewer/puckworks/blob/c6fe9b45d4e273fc83c72db4d5e31dcd7d281b5e/puckworks/harness.py#L1007-L1043)). The resulting interval is therefore conditional on:

- the seven retained terms;
- the quadratic functional form;
- fixed achieved predictors;
- the residual-resampling assumptions; and
- the selected 40 g TDS response.

That is a legitimate conditional sensitivity analysis, but it does not “confirm[] the interior maximum is a real … feature” in the broad sense claimed at [lines 151–154](https://github.com/trbrewer/puckworks/blob/c6fe9b45d4e273fc83c72db4d5e31dcd7d281b5e/docs/PAPER_B_DRAFT.md#L151-L154). It confirms that the **fitted selected quadratic** has a well-localized in-domain vertex under the conditional resampling scheme. The source itself cautioned that its response surfaces only partly explained the variation and should be interpreted quantitatively with care.

The code also reports concavity and in-domain fractions separately. For the achieved analysis, the independent check found a joint concave-and-in-domain fraction of about 0.9985, not literally 100%.

**Required action:** Use wording such as “the selected quadratic surface has a conditional vertex near 1.74.” Either repeat term selection within each resample, use a method designed for post-selection inference, or clearly state that selection uncertainty is excluded. Report the joint validity fraction and the tested domain.

---

### MAJ-09 — Raw-scale numerical conditioning is avoidable, and influence deserves a sensitivity analysis

The revision correctly labels `κ₂(X) ≈ 1.66×10⁶` and `κ₂(XᵀX) ≈ 2.74×10¹²`. It then says the vertex and predictive Q² “are not” numerically unstable ([draft lines 403–405](https://github.com/trbrewer/puckworks/blob/c6fe9b45d4e273fc83c72db4d5e31dcd7d281b5e/docs/PAPER_B_DRAFT.md#L403-L405)). That categorical statement is stronger than the checks shown.

Independent reparameterization on centered/scaled predictors reduces `κ₂(X)` to approximately **3.89** while reproducing fitted values to about `1.6×10⁻¹²`. There is no reason to retain the ill-conditioned raw-scale fit as the computational implementation. Back-transform only the quantities needed for interpretation.

The achieved-predictor fit also has:

- maximum absolute standardized residual ≈ 3.66;
- maximum leverage ≈ 0.20;
- maximum Cook’s distance ≈ 0.44;
- most influential row: experiment 10, repetition 1.

These diagnostics do not prove that the row is erroneous, but they justify a leave-one-run and robust-regression sensitivity for the vertex and curve.

**Required action:** Center and scale predictors in the fit, demonstrate invariance after back-transformation, and report influence sensitivity. Replace “are not numerically unstable” with a measured statement about invariance across parameterization, solver, and leave-one-run analyses.

---

### MAJ-10 — RSM leave-one-setting-out validation still violates the source predictor contract and misstates n

The RSM LOPO module says there are “18 design points” ([`lopo_cv.py` lines 14–17](https://github.com/trbrewer/puckworks/blob/c6fe9b45d4e273fc83c72db4d5e31dcd7d281b5e/analysis/lopo_cv.py#L14-L17)), but the source and committed data contain **15 nominal settings**. The function constructs target `F,G,T` rows ([lines 38–54](https://github.com/trbrewer/puckworks/blob/c6fe9b45d4e273fc83c72db4d5e31dcd7d281b5e/analysis/lopo_cv.py#L38-L54)) and groups by nominal target triples ([lines 68–96](https://github.com/trbrewer/puckworks/blob/c6fe9b45d4e273fc83c72db4d5e31dcd7d281b5e/analysis/lopo_cv.py#L68-L96)). That is inconsistent with the newly adopted achieved-predictor RSM.

Independent experiment-ID LOPO gives:

| Predictor contract | Held-out settings | Q² | RMSE |
|---|---:|---:|---:|
| Nominal target flow/temp | 15 | 0.47885 | 0.12744 g |
| Achieved flow/temp | 15 | 0.47011 | 0.12850 g |

The result is qualitatively similar, but the implementation and reporting contract must match the primary model.

**Required action:** Hold out `exp` rather than grouping floating-point triples, use achieved flow/temperature, retain all repetitions of the held-out setting together, and report n=15. Include per-setting observed means, predictions, residuals, leverage/extrapolation flags, and a plot. Do not imply a precision estimate from 15 highly overlapping refits without appropriate caution.

---

### MAJ-11 — Figure 1 still hides the most important data and overstates the RSM evidence

Figure 1 has improved substantially: it distinguishes the observed cell means from the response-surface curve, labels the second panel’s grinder axis as nonportable, and no longer calls the raw response monotone in a statistical sense.

Remaining problems:

1. Panel a shows only three means ± SD, hiding the 3/6/3 run values and the very unequal cell dispersions.
2. The label “measured TDS-EY” should be “source-derived TDS-EY from integrated run-specific kinetics.”
3. The RSM curve is achieved-predictor/residual-bootstrap while the text is target-predictor/case-bootstrap.
4. The vertical band is a vertex interval, not a confidence band for the curve; readers may misread it as general RSM uncertainty.
5. The vertex annotation overlaps the curve/data near the upper-right portion of panel a.
6. Juxtaposing the Schmieder E65S dial and Cameron model grind axes can still suggest a quantitative overlay even though the axes are explicitly nonportable.

**Required action:** Show all run points with a small horizontal jitter, overlay means and clearly defined SD/CI, add a bootstrap curve envelope, and place the conditional vertex estimate in the caption or an uncluttered inset. Consider moving the model-capacity panel to a separate figure or using normalized axes with a prominent “different grinder/calibration axis” banner.

---

### MAJ-12 — Static channeling remains a capacity demonstration with unpropagated calibration uncertainty

The manuscript now appropriately calls the result model capacity rather than identification. The closure sensitivity—10 of 25 grid combinations produce an interior maximum, with full-grid median prominence near zero—makes fragility visible.

However, the analysis still treats the calibrated σ(grind) closure and supporting pressure/geometry choices as fixed. The evidence chain crosses datasets and grinder axes: Cameron supplies the calibration deviation; Schmieder supplies a weak smooth/target; the model’s own grind coordinate is nonportable. The prominence distribution over an arbitrarily selected `(s_ref,m)` rectangle is not a probability of robustness.

**Required action:** Add a parameter-provenance/calibration table and propagate plausible closure uncertainty to peak location and prominence. Show grid-resolution convergence of peak location/prominence, not only whether a coarse grid argmax is interior. Keep the conclusion at “this model class can generate a small interior response under some calibrated closure settings.”

---

### MAJ-13 — Figure 2 is now data-driven, but its ontology is not yet an evidence framework

Replacing the plotting-layer hard coding with a committed CSV is a major improvement. The current table, however, mixes fundamentally different kinds of status:

- implementation state (`implemented`);
- observable comparability (`matched`, `mismatch`, `proxy`);
- parameter source (`literature`, `target-fit`, `same-campaign`);
- simulated outcome (`capacity`, `no`, `elevated-ρc`); and
- evidence strength (`qual-cap`, `qual-null`, `reference`).

The abbreviations are not defined in the figure or caption. More importantly, the static-channeling row records `params_provenance = same-campaign-transfer`, while the prose says the closure is calibrated to Cameron and checked against Schmieder. That appears to be cross-dataset calibration/proxy transfer, not same-campaign transfer.

A committed CSV is auditable only if each judgment has a definition and source. At present, the statuses remain expert-curated assertions without a rationale field.

**Required action:** Publish a schema with allowed values and criteria. Add columns for calibration dataset, evaluation dataset, observation operator, fitted quantities, source citation, rationale, and reviewer-verifiable evidence path. Correct the channeling provenance classification. Define all abbreviations or avoid abbreviations entirely.

---

### MAJ-14 — “Zero-parameter” and “0p” still misstate model complexity

The prose calls the empirical Φ(t) branch “zero-free-parameter” and later a “zero-parameter poroelastic Φ(t)” ([draft lines 226–237](https://github.com/trbrewer/puckworks/blob/c6fe9b45d4e273fc83c72db4d5e31dcd7d281b5e/docs/PAPER_B_DRAFT.md#L226-L237)). Figure 3 labels static κ(P) and Φ(t) as “0p” ([`figures.py` lines 205–221](https://github.com/trbrewer/puckworks/blob/c6fe9b45d4e273fc83c72db4d5e31dcd7d281b5e/puckworks/figures.py#L205-L221)).

The code itself contains the more accurate accounting: all three pressure branches share two flow-fitted equilibrium parameters; Φ(t) adds three donor sigmoid parameters from another observable; RC-3b imports Cameron calibration. “Zero” means only zero additional coefficients optimized against the particular scored flow trace after those choices are fixed.

**Required action:** Replace parameter counts with a provenance-aware table:

| Model | Fitted to scored 9-bar flow trace | Fitted to same campaign, other observable | Fitted to other dataset | Literature fixed | Analyst chosen/numerical |
|---|---:|---:|---:|---:|---:|

In the plot use “0 added flow-trace coefficients,” not “0p.” This distinction is central to the paper’s argument about fair nulls.

---

### MAJ-15 — The temporal ladder is an in-sample reconstruction ladder, not predictive model comparison

The three constants, Φ(t), and cubic are all scored on one 15–95 s trace. The cubic is fitted and evaluated on the same window, so its RMSE is an **in-sample flexibility bound**. That is useful: it shows that a nonmechanistic smooth trajectory can match or exceed the mechanistic reconstruction. It is not a predictive benchmark unless fitted and evaluated on separated blocks or traces.

The phrase “time variation is required” ([draft lines 231–233](https://github.com/trbrewer/puckworks/blob/c6fe9b45d4e273fc83c72db4d5e31dcd7d281b5e/docs/PAPER_B_DRAFT.md#L231-L233)) is too categorical. The data show that, among the tested mean-trajectory forms and scoring window, nonconstant trajectories reduce RMSE relative to the tested constants. They do not establish a universal physical requirement, nor do they identify whether the time variation arises in the bed, machine, saturation, viscosity, sensor response, or observation model.

**Required action:** Either use a dependence-aware predictive design—such as contiguous-block/rolling-origin evaluation, fitting on one pressure and evaluating another under a prespecified transfer rule, or a correlated-error likelihood/information criterion—or explicitly call the cubic an in-sample flexibility bound and narrow the claim.

---

### MAJ-16 — The Durbin–Watson result is a major lack-of-fit finding, but its sensitivity and visual evidence are missing

The manuscript reports a mean Durbin–Watson value near 0.01 after decimation to 1 s ([lines 306–311](https://github.com/trbrewer/puckworks/blob/c6fe9b45d4e273fc83c72db4d5e31dcd7d281b5e/docs/PAPER_B_DRAFT.md#L306-L311)). This is not a minor diagnostic: it means the residuals remain highly structured, so the RMSE rankings are dominated by systematic trajectory mismatch rather than approximately independent noise.

The decimation step is sensible as a first attempt to avoid reporting the native ~10 Hz sampling autocorrelation, but 1 s is discretionary. The paper does not show sensitivity at 0.5, 1, 2, or 5 s, does not show residual ACFs, and does not estimate an effective number of independent temporal units or a correlated-error model.

**Required action:** Plot residuals and ACFs for all ladder models; repeat diagnostics over prespecified decimation/block scales; report RMSE-difference uncertainty using block/bootstrap or an explicit time-series error model. Treat the structured residual as an outcome of the study, not a footnote.

---

### MAJ-17 — The cross-pressure section conflates shared calibration, conditional transfer, and LOPO

Four summaries must be kept distinct:

1. **Shared calibration, all 11 pressures:** the campaign-wide `(P_c,Q_c)` fit is used for every trace.
2. **Shared calibration, ten off-9-bar pressures:** same fit, omitting 9 bar only from the summary.
3. **LOPO, all 11 pressures:** each pressure is excluded when refitting `(P_c,Q_c)`.
4. **LOPO, ten off-9-bar pressures:** LOPO summary with the donor 9-bar pressure omitted from evaluation.

The manuscript reports LOPO all-11 means of 0.534/0.347/0.516 and shared all-11 means of 0.524/0.335/0.510 ([lines 284–300](https://github.com/trbrewer/puckworks/blob/c6fe9b45d4e273fc83c72db4d5e31dcd7d281b5e/docs/PAPER_B_DRAFT.md#L284-L300)). It then states that the “full-precision (unrounded) held-out means” are 0.512/0.356/0.522 over the ten off-9-bar pressures ([lines 301–306](https://github.com/trbrewer/puckworks/blob/c6fe9b45d4e273fc83c72db4d5e31dcd7d281b5e/docs/PAPER_B_DRAFT.md#L301-L306)). Those latter values come from `cross_pressure_discrimination`, which uses the shared campaign-wide calibration; they are not LOPO-held-out values.

Figure 3c likewise uses `cross_pressure_discrimination()` ([`figures.py` lines 224–231](https://github.com/trbrewer/puckworks/blob/c6fe9b45d4e273fc83c72db4d5e31dcd7d281b5e/puckworks/figures.py#L224-L231)), not `cross_pressure_loco()`.

**Required action:** Rename every quantity with an explicit calibration/evaluation tag. Put the four summaries in one table. Either plot both shared and LOPO curves or make Figure 3c’s shared-calibration status unmistakable. Do not use “held out” for any pressure whose equilibrium point contributed to the fitted calibration.

---

### MAJ-18 — The new LOPO function still computes means from rounded pressure-level values

`cross_pressure_loco` rounds each pressure’s RMSE to three decimals before storing it ([`harness.py` lines 1346–1348](https://github.com/trbrewer/puckworks/blob/c6fe9b45d4e273fc83c72db4d5e31dcd7d281b5e/puckworks/harness.py#L1346-L1348)) and then averages those rounded values ([lines 1349–1354](https://github.com/trbrewer/puckworks/blob/c6fe9b45d4e273fc83c72db4d5e31dcd7d281b5e/puckworks/harness.py#L1349-L1354)). This is the same class of issue that the revision correctly fixed in `cross_pressure_discrimination`.

The numerical effect may be small, but the paper explicitly emphasizes full-precision aggregation, so the implementation must be consistent.

**Required action:** Store a raw dictionary, aggregate raw values, and round only in a presentation layer. Add a unit test that recomputes the mean directly from raw pressure-level outputs.

---

### MAJ-19 — Pressure-varying relative error should not be elevated to “regimes” without prespecification and uncertainty

The revision now says the pressure bins are descriptive, which is appropriate. The abstract nevertheless calls conditional transfer “regime-dependent” ([draft lines 43–45](https://github.com/trbrewer/puckworks/blob/c6fe9b45d4e273fc83c72db4d5e31dcd7d281b5e/docs/PAPER_B_DRAFT.md#L43-L45)), and the main text refers to one model doing better at low pressure and another at mid-range.

The curves are based on one campaign and do not display uncertainty. Adjacent pressure-level errors are not independent experimental replications, and the bins were chosen after viewing the curves. LOPO refits overlap heavily; naïve fold-to-fold variance is not a conventional confidence interval.

**Required action:** Describe “pressure-varying relative reconstruction error” unless a regime hypothesis is prespecified. Show uncertainty or replicate variation where available. Treat LOPO as a calibration-sensitivity diagnostic and cite the dependence of errors from overlapping training sets when discussing aggregate uncertainty.

---

### MAJ-20 — Source trace uncertainty is not propagated into Result 2

The analysis scores mean/digitized traces with unweighted RMSE. The source representation appears to include flow-rate standard-deviation fields, but Figure 3 and the ladder do not display or use them. Without uncertainty, an RMSE difference such as 0.116 versus 0.096 g/s is not interpretable as a statistically meaningful difference; it only ranks two deterministic reconstructions under one loss.

**Required action:** Document whether the trace is a mean, a single run, or digitized from a source figure; show source uncertainty; use a weighted or hierarchical model if replicate-level information exists; and report sensitivity to the evaluation window. At minimum, state that RMSE differences are descriptive and not inferential.

---

### MAJ-21 — The fixed-pressure sign constraint is much better, but the heading and bibliography still overstate it

The body now carefully limits the conclusion to isolated resistance-increasing branches under imposed fixed pressure and acknowledges coupled processes ([draft lines 239–271](https://github.com/trbrewer/puckworks/blob/c6fe9b45d4e273fc83c72db4d5e31dcd7d281b5e/docs/PAPER_B_DRAFT.md#L239-L271)). This is scientifically defensible and should be retained.

The heading still says the sign test “excludes the matrix-resistance mechanisms,” which is broader than the body. “Constrains isolated resistance-only branches” is the accurate formulation. Complete primary citations are also required for the claimed Fasano lemma and Part III result. The internal module name `mo2023_2` does not match the swelling article’s 2022 publication year.

**Required action:** Change the heading, define the control boundary precisely, and provide full source citations. Keep any magnitude from the transferred “representative illy powder” parameterization separate from the analytic sign statement.

---

### MAJ-22 — The composition failure is useful but supports only one implementation/parameter-transfer statement

Figure 4 shows that adding the imported swelling branch to the shared-porosity composition worsens the 9-bar reconstruction relative to the extraction-only identity and best constant. The manuscript appropriately says this does not distinguish parameter-transfer, initial-state, control-regime, or composition-form error ([lines 313–324](https://github.com/trbrewer/puckworks/blob/c6fe9b45d4e273fc83c72db4d5e31dcd7d281b5e/docs/PAPER_B_DRAFT.md#L313-L324)).

That scoped negative result is useful. It is not independent evidence against swelling, nor does the exact extraction-only reduction validate the composition—it is an implementation identity. Because Figure 4 largely repeats the observed and Φ(t) trajectories from Figure 3, it may be better suited to a supplement unless the main text makes composition failure a major methodological contribution.

**Required action:** Present a parameter/provenance table for the composed branches, show residuals, and label the result “this transferred parameterization under this composition rule worsens reconstruction.” Consider moving the full trace plot to supplementary material and retaining a compact residual or RMSE-difference panel in the main paper.

---

### MAJ-23 — Result 3’s floor sweep establishes only endpoint invariance over a selected numerical range

The revised code genuinely reruns the N-tube integration for each conductance floor, which fixes an important weakness. The result is nevertheless narrower than the prose and Figure 5 annotation suggest.

At present the sweep tests whether the **final effective channel count and Boolean concentration classification** change over selected floors at:

- grind `gs=1.1`;
- pressure 9 bar;
- N=150 in the floor analysis;
- deterministic quantile initialization;
- a fixed horizon and timestep/substep scheme;
- fixed-total-flow normalization;
- zero lateral homogenization; and
- one poroelastic trajectory/closure realization.

The figure code sweeps `10⁻⁶, 10⁻⁹, 10⁻¹², 10⁻¹⁵` ([`figures.py` lines 337–344](https://github.com/trbrewer/puckworks/blob/c6fe9b45d4e273fc83c72db4d5e31dcd7d281b5e/puckworks/figures.py#L337-L344)), while the manuscript says `10⁻⁹…10⁻¹⁵` ([draft lines 346–350](https://github.com/trbrewer/puckworks/blob/c6fe9b45d4e273fc83c72db4d5e31dcd7d281b5e/docs/PAPER_B_DRAFT.md#L346-L350)).

“Genuinely floor-independent” should therefore be replaced by “the final classification is invariant over the selected floor values in this tested configuration.” Two simulations can have the same final N_eff but very different collapse times and transient dynamics.

**Required action:** Reconcile the floor range and plot N_eff(t), maximum share(t), total flow/pressure, and time-to-threshold for every floor. Report convergence of those trajectories, not only the endpoint.

---

### MAJ-24 — Result 3 still needs numerical convergence, initial-condition sensitivity, and a physical exchange/control formulation

The N-tube model contains a positive feedback by construction: each tube’s extraction clock advances in proportion to its current conductance share, and under fixed total flow a faster tube takes a larger share of a fixed total. The “lateral” term is an algebraic blend of weights toward one, not a mass-conserving transverse exchange operator ([`harness.py` lines 1450–1469](https://github.com/trbrewer/puckworks/blob/c6fe9b45d4e273fc83c72db4d5e31dcd7d281b5e/puckworks/harness.py#L1450-L1469)). The pressure-control comparison uses a different normalization, so it is not simply a matched physical boundary-condition experiment.

No evidence is shown for:

- timestep/substep convergence;
- tube-number convergence;
- horizon sensitivity;
- start-time/initial-state sensitivity;
- random perturbation or realization sensitivity;
- pressure and grind sweeps;
- conservation/error balances;
- a physical machine–bed feedback law;
- a physical transverse-Darcy or network exchange closure; or
- Jacobian/finite-time-Lyapunov growth along the evolving trajectory.

The code also assigns `n_eff_final_numeric` from the second floor in the supplied sequence, an arbitrary representative choice, and `concentrates_numeric` from the first floor. Those convenience fields should not substitute for reporting the full vector.

**Required action:** Either keep Result 3 as an explicitly constructed numerical counterexample in the supplement, or complete a robustness and physical-closure program. A main-text physical claim requires at least trajectories, numerical convergence, broad parameter/initialization sweeps, and a control/exchange law derived from the same hydraulic system.

---

### MAJ-25 — Figures 3–5 remain annotation-heavy and do not show the diagnostics needed for their claims

The revised captions/titles are more cautious, but the plots still carry long argumentative text in small type.

- **Figure 3b:** bar heights alone conceal the trajectory, residual structure, and uncertainty. “0p” is misleading.
- **Figure 3c:** shows shared-calibration results while adjacent prose foregrounds LOPO.
- **Figure 3d:** the annotation is dense and partly competes with the data.
- **Figure 4:** a large text block overlays the plot and repeats information that belongs in the caption; residuals are absent.
- **Figure 5:** panel b visually emphasizes a floor-singular closed-form gain that the paper says is not meaningful, while the claimed robust quantity appears only in a small text annotation. No time trajectory or convergence result is plotted.

**Required action:** Move interpretive paragraphs to captions. Use separate residual/ACF plots and uncertainty bands. For Figure 5, replace or supplement the singular gain panel with N_eff(t), time-to-collapse, and numerical-refinement sensitivity.

---

### MAJ-26 — The paper build remains only partially single-source and the figure files are not publication grade

Figure 1 now consumes one RSM result, and Figure 2 consumes a committed table—both good changes. But `render_all()` still invokes analysis/simulation functions separately in the plotting process, and there is no immutable Paper B result bundle against which manuscript values, tables, and figures can be checked. A change in a model function can alter a figure without updating the prose or recording a result-schema change.

The plotting module sets both figure and save resolution to 150 dpi and writes PNG only ([`figures.py` lines 26–52](https://github.com/trbrewer/puckworks/blob/c6fe9b45d4e273fc83c72db4d5e31dcd7d281b5e/puckworks/figures.py#L26-L52)). The reviewed PNGs are indeed 150 dpi. This is insufficient for many journal workflows and makes small annotations difficult to read.

**Required action:** Implement:

1. `compute_paper_b_results` → immutable JSON/Parquet/CSV bundle;
2. `render_paper_b` → figures and tables from that bundle only;
3. a manuscript-value check that fails when numbers diverge;
4. commit/data/environment/seeds/tolerances in metadata;
5. vector PDF/SVG output and, where required, 300–600 dpi raster export;
6. a tagged archival release with DOI.

---

### MAJ-27 — Publication metadata and primary references need correction and completion

The manuscript has no conventional reference section and uses internal keys as if they were citations. Two are now bibliographically stale:

- the repository key `waszkiewicz2025` corresponds to the published 2026 article *Under pressure: Poroelastic regulation of flow in espresso brewing*, Physics of Fluids 38, 063113, DOI `10.1063/5.0319611`;
- the repository key `mo2023_2` corresponds to the 2022 swelling article, Physics of Fluids 34, 043104, DOI `10.1063/5.0086897`.

Foster et al. 2025 directly support the importance of infiltration and partial wetting; the paper reports that infiltration can occupy a substantial fraction of brewing time and uses time-resolved micro-CT. That strengthens the manuscript’s own conclusion that incomplete wetting is a serious unimplemented competitor rather than a peripheral omission.

**Required action:** Add complete primary citations for every dataset, model, equation, and lemma. Internal keys may be documented in the reproducibility appendix, but the manuscript must use publication metadata.

---

### MAJ-28 — The Discussion is directionally correct but still overgeneralizes from two focal campaigns and one exploratory model

The Discussion now limits the integrated-observable statement to the two datasets examined and explicitly says the Result 3 channels are simulated ([draft lines 364–376](https://github.com/trbrewer/puckworks/blob/c6fe9b45d4e273fc83c72db4d5e31dcd7d281b5e/docs/PAPER_B_DRAFT.md#L364-L376)). This is good.

The phrase “integrated observables can erase the structure needed to discriminate mechanisms” should nevertheless be tied to the exact observation operators and candidate model set. Integrated observables are not inherently nondiscriminating; discrimination depends on experimental excitation, controls, noise, replication, and whether candidate predictions differ after applying the observation operator.

**Required action:** Frame the conclusion as an observability result for the tested endpoints/traces and model classes. Distinguish:

- failure to discriminate because predictions are similar after integration;
- failure because a competitor is unimplemented;
- failure because parameters are fitted to the same target;
- failure because uncertainty/replication is inadequate; and
- true incompatibility of a model instance under defined boundary conditions.

---

## 6. Figure-by-figure review

### Figure 1 — TDS-EY target and static-channeling capacity

**What works**

- The two grinder axes are explicitly distinguished.
- The raw-cell statement is now “no middle-cell maximum,” not “statistically monotone.”
- Figure generation consumes the achieved-predictor RSM result rather than refitting in the plotting layer.
- The model-capacity conclusion is appropriately separated from identification.

**Required corrections**

1. Harmonize the figure with the main-text RSM estimand and bootstrap.
2. Correct the achieved central-condition mask.
3. Show all 12 central-cell run values.
4. Relabel “measured TDS-EY” as a source-derived run-level endpoint from integrated kinetics.
5. Add an RSM curve uncertainty envelope; clarify that the vertical band is a vertex interval.
6. Move the overlapping vertex annotation.
7. Consider separating panel b or visually emphasizing that the axes and calibrations are not commensurate.
8. State n and error-bar definition in the caption.

**Current image properties:** 1078×554 px, 150 dpi.

---

### Figure 2 — Mechanism evidence matrix

**What works**

- It is now generated from a committed structured file.
- Color is accompanied by text.
- A decisive-missing-measurement column is a useful design feature.
- The title says it is not a winner scoreboard.

**Required corrections**

1. Define every dimension and status in the caption or supplement.
2. Replace abbreviations such as `impl`, `qual-cap`, `elevated-ρc`, and `n/e` with readable text.
3. Correct the static-channeling parameter provenance classification.
4. Add calibration/evaluation dataset and source/rationale fields to the underlying table.
5. Distinguish “not implemented” from “not testable with this observable.”
6. Consider separating implementation readiness from evidential strength into two panels/tables.
7. Ensure the missing-measurement text remains readable at journal column width.

**Current image properties:** 1524×522 px, 150 dpi.

---

### Figure 3 — Machine null, temporal ladder, cross-pressure comparison, and sign constraint

**What works**

- Foster is now explicitly a model-curve reproduction.
- The evaluation window is stated in panel b.
- The swelling panel is scoped to an isolated fixed-pressure resistance branch.
- The cross-pressure curves make the absence of a universal winner visible.

**Required corrections**

1. Replace “0p” with complete provenance-aware complexity labels.
2. Add trajectories/residuals or a companion residual figure; RMSE bars are insufficient.
3. Make clear that the cubic is fitted and scored in-sample.
4. State in panel c whether calibration is shared or LOPO; current code is shared calibration.
5. Show uncertainty or source trace variation.
6. Reduce annotation density in panels a, b, and d.
7. Replace “time variation needed” with a narrower in-window reconstruction statement.
8. Use the corrected cross-pressure summary table as the numerical source.

**Current image properties:** 1502×1004 px, 150 dpi.

---

### Figure 4 — Shared-porosity composition diagnostic

**What works**

- The 15–95 s window is visibly shaded.
- The title is neutral compared with the prior “failed/over-closes” framing.
- The extraction-only reduction is identified as an implementation identity.
- The best-constant comparator is computed on the same window.

**Required corrections**

1. Add a residual panel or show residuals below the trace.
2. Move the long explanatory block to the caption.
3. State all transferred parameters and their sources.
4. Clarify that the result tests one composition rule and one imported parameterization.
5. Consider moving the full plot to the supplement because the observed and Φ(t) curves repeat Figure 3.

**Current image properties:** 942×580 px, 150 dpi.

---

### Figure 5 — Exploratory finite-time concentration

**What works**

- It no longer claims a formal instability theorem.
- It exposes the floor singularity of the closed-form gain.
- It compares flow and pressure control and shows the effect of the homogenizing proxy.
- The numerical integration is rerun at each floor.

**Required corrections**

1. Reconcile the floor range in code/figure and prose.
2. Replace “robust concentration result is floor-independent” with tested-configuration endpoint language.
3. Show N_eff(t), maximum share(t), total-flow/pressure behavior, and time-to-threshold.
4. Add N, timestep, substep, horizon, initialization, pressure, and grind sensitivity.
5. Add stochastic/perturbation realizations or explain deterministic initialization.
6. Replace the algebraic lateral proxy with a physical exchange operator before making physical claims.
7. De-emphasize the closed-form gain magnitude, which the paper itself says is not meaningful.
8. Move the small text annotation into the caption.

**Current image properties:** 1212×590 px, 150 dpi.

---

## 7. Section-by-section manuscript comments

### Abstract

- Remove the history of an earlier repository aggregation error. It is useful audit history but not the scientific result.
- Clarify “two focal empirical datasets” and identify supporting calibration/model sources separately.
- Replace “time variation is required” with “nonconstant trajectories reduce in-window reconstruction error relative to the tested constants.”
- Replace “regime-dependent” with “pressure-varying within the campaign” unless regimes are prespecified.
- Replace broad floor-independence language with tested-configuration endpoint invariance.
- State that Result 3 is simulated and exploratory in a single concise clause.

### Introduction

- Add a conventional literature synthesis with complete citations.
- Define “mechanism discrimination,” “capacity,” “incompatibility,” and “identification.”
- Avoid an unverified claim that mechanisms have not been compared head-to-head; complete the related-work search first.
- Separate the Cameron calibration phenomenon from the Schmieder dial response more strongly; they are not the same grinder/observable.

### Methods

- Replace registry/project language with equations and experiment/analysis contracts.
- Give all observation operators and units.
- Describe source-data derivation, exclusions, and missing rows.
- Define calibration/evaluation partitions.
- Give parameter provenance and any optimization bounds.
- Specify numerical solvers, grids, tolerances, seeds, and convergence tests.
- Give statistical models, bootstrap type, model-selection treatment, CV unit, and uncertainty procedures.
- Explain how densely sampled traces are treated as dependent observations.

### Result 1

- Correct the t interval.
- Reconcile RSM estimand/bootstrap and central mask.
- Replace “confirming the maximum is real” with conditional fitted-surface language.
- Add the achieved-predictor LOPO result.
- Show run points and influence sensitivity.
- Keep the channeling result explicitly at capacity level.

### Result 2

- Replace zero-parameter labels.
- Call the cubic an in-sample flexibility bound unless validated separately.
- Separate shared and LOPO transfer summaries.
- Add residual/ACF evidence and uncertainty.
- Change “excludes” to “constrains” in the sign-test heading.
- Keep composition conclusions conditional on the imported parameterization and composition form.

### Result 3

- Narrow “robust” to the exact floor/end-state test.
- Reconcile the floor range.
- Add trajectories and convergence or move the result to the supplement.
- Do not infer physical channel formation from an uncoupled algebraic positive-feedback construction.

### Discussion

- Organize around observation operators and evidence strength, not around a mechanism winner.
- Distinguish unavailable competitors from tested failures.
- Treat incomplete wetting as a major open competitor, supported by time-resolved infiltration literature.
- Separate within-campaign transfer, cross-dataset proxy comparison, and independent validation.
- State the external-validity limits: one principal coffee/machine campaign for each focal dataset.

---

## 8. Code and result traceability findings

| Manuscript claim | Code/data path | Current status | Required correction |
|---|---|---|---|
| Central-cell Welch contrasts | `result1_design_aware_stats` | Values correct | Fix stale experimental-unit note; clarify exploratory hierarchy |
| Linear trend CI | `result1_design_aware_stats` | **Definite error:** uses 1.96 | Use t critical or justified alternative |
| Primary RSM vertex | `schmieder_rsm_refit` | Both target/achieved available | Select one primary achieved-predictor analysis |
| Achieved central reference | `schmieder_rsm_refit` | **Wrong mask:** all G=1.7 | Use experiment 7 only |
| RSM bootstrap | `schmieder_rsm_refit` | Residual and case both available | Use residual primary; state fixed-term conditionality; report joint valid fraction |
| RSM conditioning | `schmieder_rsm_refit.diagnostics` | Names corrected | Center/scale computational fit; add influence sensitivity |
| RSM predictive Q² | `analysis/lopo_cv.py` | Target predictors; doc says 18 points | Use achieved predictors and 15 experiment IDs |
| Figure 1 RSM | `figures.fig1_result1` | Uses achieved/residual result | Reconcile with prose and correct center mask |
| Figure 2 evidence | CSV + `figures.fig2_evidence_matrix` | Data-driven | Define ontology; correct provenance; add rationale/source fields |
| 9-bar temporal ladder | `kappa_t_ladder` | Deterministic in-window RMSE | Correct complexity labels; dependence-aware validation or in-sample label |
| Cross-pressure shared calibration | `cross_pressure_discrimination` | Raw aggregation fixed | Do not call values held out |
| Cross-pressure LOPO | `cross_pressure_loco` | Added, but averages rounded values | Preserve raw values; add off-9 LOPO summary |
| Figure 3c | `figures.fig3_ladder` | Uses shared calibration | Label clearly or plot LOPO |
| Residual autocorrelation | `analysis/residual_autocorr.py` | 1 s decimated DW reported | Add ACF/residual plots and scale sensitivity |
| Composition | coupled κ(t) path + Figure 4 | Scoped identity/failure language improved | Add parameter provenance and residuals |
| N-tube floor test | `ntube_finite_time_gain` | Reruns each floor | Limit claim to endpoint/configuration; add trajectories/convergence |
| Figure generation | `figures.render_all` | Reruns analyses; PNG only | Consume frozen results bundle; vector output |

---

## 9. Independent numerical checks

These checks were performed directly from the committed Schmieder cup-mass table using the seven-term TDS/BR 1/2 specification implemented in the repository:

`1, F, G, T, G², T², F×G`.

They are intended as targeted verification, not as a substitute for a frozen package-wide reproduction.

### 9.1 Central-setting run-level results

| Dial | n | Mean EY (%) | Sample SD | Mean achieved flow (mL/s) | Mean achieved temperature (°C) | Mean max pressure (bar) |
|---:|---:|---:|---:|---:|---:|---:|
| 1.4 | 3 | 18.267 | 0.552 | 1.921 | 88.495 | 3.907 |
| 1.7 | 6 | 19.381 | 0.159 | 1.901 | 88.258 | 3.408 |
| 2.0 | 3 | 19.622 | 0.071 | 1.996 | 88.618 | 3.333 |

### 9.2 Pairwise Welch contrasts

| Contrast | Difference (EY-points) | Welch df | 95% CI | p |
|---|---:|---:|---:|---:|
| 1.4 − 1.7 | −1.114 | 2.167 | [−2.414, 0.187] | 0.0675 |
| 1.7 − 2.0 | −0.241 | 7.000 | [−0.422, −0.060] | 0.0161 |

These match the manuscript’s pairwise values after rounding.

### 9.3 Linear trend

| Quantity | Value |
|---|---:|
| n | 12 |
| residual df | 10 |
| slope | 2.258 EY-points/dial |
| SE | 0.4937 |
| manuscript/code normal-critical interval | [1.290, 3.226] |
| classical t₁₀ interval | **[1.158, 3.358]** |
| p | 0.00102 |

### 9.4 RSM fit comparison

| Analysis | Vertex | Residual-bootstrap 95% interval | Case-bootstrap 95% interval | Adjusted R² | Joint concave + in-domain fraction |
|---|---:|---:|---:|---:|---:|
| Nominal target F/T | 1.73324 | [1.69114, 1.79892] | [1.67701, 1.80554] | 0.64938 | 0.9990 |
| Achieved F/T, current all-G=1.7 reference | 1.74384 | [1.69988, 1.81878] | [1.69013, 1.81682] | 0.64340 | 0.9985 |
| Achieved F/T, true center exp. 7 reference | 1.74315 | [1.69921, 1.81738] | [1.68905, 1.81661] | 0.64340 | 0.9985 |

The predictor/reference differences are small, but the achieved/true-center result is the methodologically correct primary cross-section.

### 9.5 Conditioning and influence

| Diagnostic | Target fit | Achieved fit |
|---|---:|---:|
| `κ₂(X)` raw scale | 1.6555×10⁶ | 1.6557×10⁶ |
| `κ₂(XᵀX)` raw scale | 2.7407×10¹² | 2.7414×10¹² |
| `κ₂(X)` centered/scaled | 3.878 | 3.890 |
| maximum fitted-value difference after reparameterization | 5.7×10⁻¹³ | 1.6×10⁻¹² |
| max absolute standardized residual | 3.704 | 3.660 |
| max leverage | 0.180 | 0.200 |
| max Cook’s distance | 0.429 | 0.441 |

The most influential row in both fits is experiment 10, repetition 1. This warrants a sensitivity analysis, not automatic exclusion.

### 9.6 Leave-one-setting-out RSM prediction

| Predictor contract | Held-out units | Complete run rows | Q² | RMSE (g) | Worst residual (g) |
|---|---:|---:|---:|---:|---:|
| Nominal target F/T | 15 experiment IDs | 48 | 0.47885 | 0.12744 | −0.21895 |
| Achieved F/T | 15 experiment IDs | 48 | 0.47011 | 0.12850 | −0.21808 |

This check confirms that the qualitative predictive score is not sensitive to target versus achieved predictors, but the production analysis should still implement the source contract.

---

## 10. Required analyses and suggested acceptance criteria

### 10.1 Result 1 central-cell analysis

**Required analysis**

- Freeze the 12 run-level TDS-EY values and their source/provenance.
- Correct the trend CI.
- State whether adjacent pairwise contrasts were prespecified.
- Report effect estimates and intervals, not only p-values.
- Show achieved flow, temperature, and pressure beside each dial cell.

**Acceptance criteria**

- No statement implies a causal dial effect.
- The experimental hierarchy is consistent across prose, code, figure, and supplement.
- Figure 1 shows all runs and defines error bars.

### 10.2 RSM reanalysis

**Required analysis**

1. Use achieved flow and temperature and experiment 7 as the central reference.
2. Fit on centered/scaled predictors.
3. Verify retained terms against the source supplementary OriginPro object or label the fit an independent retained-term reanalysis.
4. Use fixed-design residual bootstrap as primary.
5. Either repeat model selection per bootstrap or state conditionality.
6. Report joint concave-and-in-domain fraction.
7. Add leave-one-run and robust-regression sensitivity.
8. Add achieved-predictor leave-one-experiment-out prediction.
9. Plot a curve envelope and setting-level observed/predicted values.

**Acceptance criteria**

- One primary vertex and interval appear everywhere.
- Centered/scaled and raw parameterizations agree to a prespecified tolerance.
- Influence sensitivity does not materially change the qualitative statement, or the change is reported.
- “Real maximum” language is removed unless independent data support it.

### 10.3 Static-channeling capacity

**Required analysis**

- Publish calibration/evaluation data map.
- Quantify closure uncertainty and grinder-axis nonportability.
- Test grid/quadrature resolution for peak location and prominence.
- Show sensitivity to pressure, geometry, and clipping bounds.
- Keep incomplete wetting as an explicit unimplemented competitor.

**Acceptance criteria**

- Conclusion remains at model capacity.
- No grid fraction is interpreted probabilistically.
- The evidence matrix classification matches the documented provenance.

### 10.4 Temporal ladder

**Required analysis**

- Complete parameter-provenance count.
- Show observed and predicted trajectories, residuals, and ACFs.
- Evaluate decimation/block-length sensitivity.
- Treat cubic as in-sample flexibility bound or validate it on held-out contiguous blocks/pressures.
- Incorporate source uncertainty where available.
- Perform evaluation-window sensitivity.

**Acceptance criteria**

- “0p” labels are gone.
- The conclusion is explicitly conditional on window/model set.
- RMSE differences are not presented as inferential without dependence-aware uncertainty.

### 10.5 Cross-pressure analysis

**Required analysis**

- Produce a table with the four calibration/evaluation summaries defined in MAJ-17.
- Preserve raw values through aggregation.
- Add LOPO off-9-bar means.
- Plot shared and LOPO curves or their differences.
- Report per-pressure calibration drift and trace errors.
- Avoid post hoc regime claims.

**Acceptance criteria**

- “Held out” is used only for LOPO predictions.
- Figure 3c and prose identify the same estimand.
- All means are reproducible from raw pressure-level values.

### 10.6 Exploratory N-tube result

**Required analysis for main-text retention**

- N_eff(t), maximum share(t), total flow/pressure, and time-to-threshold trajectories.
- Floor, N, timestep/substep, horizon, start-state, pressure, grind, and stochastic perturbation sweeps.
- Conservation and solver-error checks.
- A physical lateral exchange operator.
- A consistent machine/bed control law for flow versus pressure comparisons.
- Jacobian or finite-time growth analysis if using stability language.

**Acceptance criteria**

- Numerical refinement changes reported outcomes below a prespecified tolerance.
- Classification is reported across the full sensitivity design, not one configuration.
- No “robust physical channeling” claim is made from an algebraic uncoupled proxy.

**Alternative acceptance path:** Move Result 3 to an exploratory supplement and present it as a constructed counterexample showing that a non-exchanging positive-feedback composition can collapse under one control law.

### 10.7 Reproducibility build

**Required build outputs**

- `paper_b_results.json` with schema version;
- tidy CSV/Parquet tables for all plotted data;
- vector figures and high-resolution raster derivatives;
- manuscript-number consistency test;
- environment lock file;
- source-data and output hashes;
- commit SHA, random seeds, tolerances, and timing metadata;
- tagged archival release.

**Acceptance criterion:** A new environment can execute one documented command and reproduce all manuscript-facing numbers and figures without reading values from the prose.

---

## 11. Suggested replacement wording for load-bearing claims

### Abstract, opening and scope

**Current problem:** repository correction history dominates the scientific opening, and “two datasets” is ambiguous.

**Suggested wording:**

> Whole-cup and whole-trace espresso measurements apply strong observation operators to coupled extraction, flow, wetting, and bed evolution. We evaluate how much two focal experimental campaigns can discriminate among specified machine, static-bed, time-varying-bed, and exploratory streamtube models when observables, units, and calibration roles are explicitly matched.

### RSM result

**Suggested wording:**

> Using set grind with achieved flow and temperature, and conditioning on the retained seven-term quadratic model, the refitted TDS/BR 1/2 surface has a grind vertex near 1.74 (fixed-design residual-bootstrap 95% interval approximately 1.70–1.82; adjusted R²≈0.64). This localizes the vertex of the selected fitted surface; it does not independently establish a physical optimum, and the raw central-setting means contain no middle-dial maximum.

### Central-cell trend

**Suggested wording:**

> Across the 12 runs in the three selected nominal central-condition cells, a descriptive OLS trend is +2.26 EY-points per dial (t-based 95% CI approximately 1.16–3.36). Because achieved pressure and flow differ by cell and the dial-to-particle-size map is nonmonotonic, this is not a causal dial effect.

### Result 2 complexity

**Suggested wording:**

> The Φ(t) branch adds no coefficients fitted to the scored 9-bar flow trace, but it imports the campaign-wide equilibrium calibration and donor trajectory parameters estimated from other observables. It should therefore be described as zero-added-flow-trace-coefficient, not parameter-free.

### Result 2 conclusion

**Suggested wording:**

> Within the 15–95 s window and tested model set, nonconstant mean trajectories reduce in-sample RMSE relative to the three constant baselines. A flexible cubic performs at least as well as the physical Φ(t) reconstruction, so the trace supports temporal structure but does not identify its mechanism.

### Cross-pressure result

**Suggested wording:**

> Figure 3c reports conditional transfer using an equilibrium calibration fitted to all 11 pressures. Separate leave-one-pressure-out refits show that this two-parameter calibration is not dominated by a single equilibrium point. These are different estimands and neither is an independent second-rig validation.

### Sign constraint

**Suggested wording:**

> Under the imposed fixed-pressure boundary condition, an isolated branch that only increases hydraulic resistance cannot by itself generate a positive flow contribution. This constrains the tested isolated swelling/fines branches; it does not establish that swelling or fines are absent from a coupled machine–bed system.

### N-tube result

**Suggested wording:**

> At `gs=1.1`, 9 bar, N=150, fixed-total-flow normalization, zero lateral proxy, and the chosen initialization/horizon, the final N_eff≈1 classification is unchanged over the selected conductance floors. Broader robustness to numerical resolution, time horizon, initialization, pressure, grind, realization, and physical exchange closure has not been established.

---

## 12. Proposed manuscript architecture

### Proposed title

**Limits of mechanism discrimination from integrated espresso flow and extraction observables**

The current title is also defensible once “review-endorsed” is removed, but a title emphasizing limits of discrimination better matches the evidence.

### Proposed section flow

1. **Introduction**
   - mechanistic hypotheses;
   - observation-operator problem;
   - focal questions and evidence hierarchy.

2. **Data and observation operators**
   - Schmieder design/run/fraction/derived cup outcome;
   - Waszkiewicz traces/equilibrium data;
   - calibration and donor sources;
   - units, transformations, and exclusions.

3. **Candidate models and parameter provenance**
   - machine-only null;
   - constant/static bed models;
   - dynamic Φ(t) and donor variants;
   - static heterogeneity;
   - swelling/fines sign models;
   - exploratory N-tube composition.

4. **Statistical and numerical methods**
   - central-cell contrasts;
   - achieved-predictor RSM and bootstrap;
   - setting-level CV;
   - temporal scoring and correlated residuals;
   - shared versus LOPO cross-pressure calibration;
   - numerical sensitivity and reproducibility.

5. **Results**
   - Result 1: raw endpoint, conditional surface, model capacity;
   - Result 2: null ladder, sign constraints, conditional pressure transfer;
   - Result 3: exploratory composition counterexample, preferably supplementary unless expanded.

6. **Discussion**
   - what is discriminated;
   - what remains observationally equivalent;
   - decisive experiments;
   - external-validity limits.

7. **Data and code availability**

8. **References**

9. **Supplementary material**
   - diagnostics, sensitivity, full evidence matrix, provenance tables, and exploratory N-tube analysis.

---

## 13. Submission-readiness checklist

### Scientific/statistical

- [ ] One primary achieved-predictor RSM result is used consistently.
- [ ] Achieved central mask is experiment 7 only.
- [ ] Trend CI is corrected.
- [ ] RSM selection conditionality is stated or selection is repeated in resampling.
- [ ] RSM computation is centered/scaled and influence sensitivity reported.
- [ ] RSM LOPO uses achieved predictors and 15 experiment IDs.
- [ ] Shared and LOPO cross-pressure summaries are separated.
- [ ] LOPO aggregation uses raw values.
- [ ] Result 2 parameter accounting is complete.
- [ ] Cubic comparison is labeled in-sample or validated predictively.
- [ ] Residual dependence and uncertainty are shown.
- [ ] Sign constraint is scoped to the imposed boundary/model class.
- [ ] Result 3 is expanded or demoted to exploratory supplement.

### Figures

- [ ] Figure 1 shows raw run points and a curve uncertainty band.
- [ ] Figure 2 has defined statuses and corrected provenance.
- [ ] Figure 3c’s calibration contract matches its label.
- [ ] Residual/ACF diagnostics are visible.
- [ ] Figure 4 annotation is moved to caption or supplement.
- [ ] Figure 5 shows trajectories and convergence, not only endpoints/gain.
- [ ] Vector and high-resolution outputs are released.

### Manuscript/reproducibility

- [ ] Internal review/status prose is removed.
- [ ] Full Methods and equations are present.
- [ ] Complete primary references are present.
- [ ] Waszkiewicz and Mo publication years are corrected.
- [ ] Related-work search is documented.
- [ ] Data/code availability and licenses are stated.
- [ ] One frozen build produces all results/tables/figures.
- [ ] Environment, seeds, tolerances, hashes, and commit are recorded.
- [ ] Tagged archival release/DOI is available.

---

## 14. Minor and editorial comments

1. The draft header says revision 2026-07-12, while the reviewed commit and key changes are dated 2026-07-13. Update or remove the revision banner in the submission manuscript.
2. Define every acronym at first use: EY, TDS, RSM, LOPO, RMSE, Q², DW, CK, RC-3b, N_eff.
3. Use one notation for grind/dial across source and model axes; avoid `gs`, `GL`, and “dial” without a mapping table.
4. State whether pressures are gauge or absolute wherever physically relevant.
5. Replace code-style scientific prose such as “rung 5b,” “RC-3b,” and function names in the main manuscript with descriptive model names.
6. Define whether all RMSEs are equally weighted in time and how missing/NaN samples are treated.
7. State the number of samples in every scoring window after decimation/masking.
8. Report units consistently as `g s⁻¹`, `mL s⁻¹`, and °C.
9. Avoid “real” for model-derived features; use “present in the fitted surface” or “reproducible under the stated resampling scheme.”
10. Avoid “fails” for a model outside its calibrated control regime; use “is incompatible with this trace under the tested parameterization.”
11. Explain why 15–95 s was selected before showing model rankings, or present window sensitivity.
12. Explain why the long-run constant uses a 10 s late interval and test plausible alternatives.
13. State polynomial basis/scaling and fitting method for the cubic.
14. Define the effective-channel metric and its bounds in the Methods, not only the Results.
15. In Figure 5, use `M_0` consistently and distinguish a numerical floor from a physically measured baseline conductance.
16. Avoid calling the evidence matrix “evidence strength” without a rubric.
17. Cite the source of the nonmonotonic dial-to-Sauter-diameter mapping and its uncertainty.
18. State whether beverage density is assumed when moving between mass and volume in any model path.
19. Include source-data licenses and digitization uncertainty.
20. Ensure figure captions are self-contained and do not require access to repository function names.

---

## 15. Supporting primary references

The following references directly support the review’s source-design, physical-model, and statistical comments.

1. **Schmieder BKL, et al. (2023).** “Influence of Flow Rate, Particle Size, and Temperature on Espresso Extraction Kinetics.” *Foods* 12(15):2871. DOI: [10.3390/foods12152871](https://doi.org/10.3390/foods12152871).  
   Relevance: 15-setting face-centered design; three repetitions per setting and six at center; achieved flow/temperature used in RSM; backward elimination; six analyzed fractions; run-specific kinetics integrated to derived cup masses; caution on quantitative response-surface interpretation.

2. **Waszkiewicz R, Myck F, Białas Ł, et al. (2026).** “Under pressure: Poroelastic regulation of flow in espresso brewing.” *Physics of Fluids* 38:063113. DOI: [10.1063/5.0319611](https://doi.org/10.1063/5.0319611).  
   Relevance: current publication metadata for the principal pressure/flow/poroelastic source; the internal repository key `waszkiewicz2025` should not be used as the article year.

3. **Foster J, Lee W, Moroney K, et al. (2025).** “Dynamics of liquid infiltration into an espresso bed using time-resolved micro-computed tomography: Insights from experiment and modeling.” *Physics of Fluids* 37:013383. DOI: [10.1063/5.0245167](https://doi.org/10.1063/5.0245167).  
   Relevance: infiltration and partial wetting can occupy a substantial part of the brew and require spatial/time-resolved observation; supports treating incomplete wetting as a major unimplemented competitor.

4. **Mo C, Navarini L, Suggi Liverani F, Ellero M. (2022).** “Modeling swelling effects during coffee extraction with smoothed particle hydrodynamics.” *Physics of Fluids* 34:043104. DOI: [10.1063/5.0086897](https://doi.org/10.1063/5.0086897).  
   Relevance: swelling is a coupled dynamic transport/bed process; current repository key `mo2023_2` is bibliographically stale.

5. **Mo C, Johnston R, Navarini L, Ellero M. (2021).** “Modeling the effect of flow-induced mechanical erosion during coffee filtration.” *Physics of Fluids* 33:093101. DOI: [10.1063/5.0059707](https://doi.org/10.1063/5.0059707).  
   Relevance: erosion can create evolving axial/transverse heterogeneity; supports caution against reducing all bed evolution to an isolated one-sign resistance branch.

6. **Bengio Y, Grandvalet Y. (2004).** “No Unbiased Estimator of the Variance of K-Fold Cross-Validation.” *Journal of Machine Learning Research* 5:1089–1105. [Article](https://www.jmlr.org/papers/v5/grandvalet04a.html).  
   Relevance: errors from overlapping cross-validation training sets are dependent; naïve fold variance can underestimate uncertainty.

7. **Roberts DR, Bahn V, Ciuti S, et al. (2017).** “Cross-validation strategies for data with temporal, spatial, hierarchical, or phylogenetic structure.” *Ecography* 40:913–929. DOI: [10.1111/ecog.02881](https://doi.org/10.1111/ecog.02881).  
   Relevance: validation splits should respect temporal/hierarchical dependence; supports contiguous/block evaluation for dense flow traces.

8. **Freedman DA. (1981).** “Bootstrapping Regression Models.” *The Annals of Statistics* 9(6):1218–1228. DOI: [10.1214/aos/1176345638](https://doi.org/10.1214/aos/1176345638).  
   Relevance: foundational distinction between regression bootstrap designs and assumptions; supports explicit fixed-design residual-bootstrap justification.

9. **Leeb H, Pötscher BM. (2005).** “Model Selection and Inference: Facts and Fiction.” *Econometric Theory* 21(1):21–59. DOI: [10.1017/S0266466605050036](https://doi.org/10.1017/S0266466605050036).  
   Relevance: inference conditional on a data-selected model does not automatically include model-selection uncertainty.

10. **Crameri F, Shephard GE, Heron PJ. (2020).** “The misuse of colour in science communication.” *Nature Communications* 11:5444. DOI: [10.1038/s41467-020-19160-7](https://doi.org/10.1038/s41467-020-19160-7).  
    Relevance: supports color-accessible figure design, although text labels and a defined evidence ontology remain necessary.

---

## 16. Bottom-line recommendation

**Major revision before journal submission.**

The revision has made genuine progress and has repaired several prior overclaims. The null-first, matched-observable framing is strong enough to support a useful paper. The main qualitative conclusion—that the tested integrated endpoints and traces provide limited unique mechanism discrimination—remains credible.

Before submission, the authors should treat the following as non-negotiable:

1. harmonize and correct the achieved-predictor RSM analysis, central mask, bootstrap, and LOPO;
2. correct the linear-trend interval and stale experimental-unit language;
3. separate shared-calibration and LOPO cross-pressure quantities and preserve full precision;
4. replace zero-parameter labels with complete parameter provenance;
5. make Result 2 explicitly in-sample or dependence-aware;
6. substantially narrow or expand the N-tube robustness claim;
7. complete a conventional manuscript with full references and Methods; and
8. create one frozen, auditable paper build with vector figures.

Once those actions are completed, Paper B can make a clear contribution: not a declaration of a winning espresso mechanism, but a rigorous demonstration of what matched integrated observations can and cannot discriminate, together with concrete experimental measurements that would break the remaining degeneracies.
