# Detailed review of the updated `PAPER_B_DRAFT.md`

**Repository:** `https://github.com/trbrewer/puckworks`  
**Reviewed public `main` commit:** `b4de0d971555dcfcf13b24cab5da6e5b8eab9cf4`  
**Review date:** 13 July 2026  
**Overall recommendation:** **Major revision before journal submission**

## 1. Review scope and traceability

I read `docs/REVIEWER_BRIEF_PAPER_B.md` before assessing the manuscript, as requested. I treated it as a disclosure register rather than a prohibition on criticism: known limitations are evaluated for adequacy and cross-document consistency, while genuinely new defects are identified separately.

The review covers:

- `docs/REVIEWER_BRIEF_PAPER_B.md`;
- `docs/PAPER_B_DRAFT.md`;
- `docs/PAPER_B_CAPTIONS.md`;
- all six rendered Paper B figures—five main figures and one supplementary figure;
- the principal figure-generation code in `puckworks/figures.py`;
- the Paper B analysis/build paths in `puckworks/harness.py`, `puckworks/paper_b/build.py`, and `puckworks/analysis/residual_autocorr.py`;
- the committed `paper_b_results.json` bundle and `paper_b_manifest.json` reproducibility manifest;
- the source-study descriptions and selected statistical claims against primary literature.

### Reviewed artifact hashes

| artifact | SHA-256 |
|---|---|
| `REVIEWER_BRIEF_PAPER_B.md` | `c96af2627636c28f86fc0fa5c584466107750718d366771a881a6009b52b565d` |
| `PAPER_B_DRAFT.md` | `2481035c27f011857af9afb3d9ab99e204e00694af026bdca7b3d7fea2fc1016` |
| `PAPER_B_CAPTIONS.md` | `295446262efe834669d46d6f1c024df6950be7ba352d9d5d67bf5cf30c9f3731` |
| `figures.py` | `4f46fb37a89b39eadd9965009a56c74ecd44d23fea320837f21b1f36c18da110` |
| `harness.py` | `c35618b4aaad4b97e8dab398438adc326a2b2f85cd96a33dc7bfe55de73f091f` |
| `paper_b/build.py` | `49812d8335026e9c51c75ca6fcbcf20477b3726c62ecd4efd7b3fb844b7a74b2` |
| Figure 1 PNG | `a934dbfa7fe0b952f24c4d38e05703a372ca4ffd66b020ad7b29422aae139cf7` |
| Figure 2 PNG | `68f1f76ec67ad2d625f2f935ff476d0433b4e9b7e1a440b5833752cdd5089792` |
| Figure 3 PNG | `667ac7fc7e0dcb41a9b4a6a98dd2c0e5629b8bd70dcd8865831ed916715bcdec` |
| Figure 4 PNG | `5a8e8c2d1a6158ebfb135cbfd5e1913e84e1909383392d75a03aee06b9f3a340` |
| Figure 5 PNG | `d347cc6f363ada342ced221acca9521d4581c512cb1b8af8baa537145fa31e3d` |
| Figure 6 PNG | `777a6fa0b7e822888683ed117445b6924bd6571b1d807b9752d5a1fb7d82142d` |

This was a static code, artifact, and literature audit with targeted internal consistency checks. I did **not** claim a clean-room recomputation of every slow simulation in a newly provisioned environment. The absence of a clean, current, artifact-coherent release is itself one of the central findings.

---

## 2. Executive assessment

The updated manuscript is substantially better than the version reviewed previously. The reviewer brief is useful and mostly honest; the manuscript now makes several important distinctions correctly:

- a conditional response-surface vertex is not a physical optimum;
- a Foster machine/infiltration model curve is a model-capacity example rather than measured data—although one sentence in the manuscript still contradicts this;
- the 9-bar ladder uses in-sample reconstruction errors, not held-out prediction;
- a flexible cubic prevents identifying a particular bed mechanism from the temporal trace;
- leave-one-pressure-out analysis tests calibration stability within one campaign, not independent physical validation;
- the swelling/fines argument is an isolated fixed-pressure sign constraint rather than a general refutation;
- Result 3 is explicitly exploratory and not a stability theorem;
- the Jensen comparison now uses `EY(E[K_evaluated])`, with the corrected deficit range of approximately −4.64 to −1.38 extraction-yield points.

The paper's **central thesis remains defensible**: within the stated datasets and implemented model set, integrated observables can establish model capacity, incompatibility, or the usefulness of temporal flexibility while remaining insufficient to identify a unique physical mechanism.

However, the current package is not ready for submission because several cross-artifact defects remain, including two genuinely new and consequential Result 3 issues:

1. **The frozen result bundle and reproducibility manifest were generated on an older dirty commit and retain pre-correction N-tube classifier behavior.** They are not coherent with the current source, manuscript, figures, or reviewer brief.
2. **The reported “collapse time” is only the first crossing of a 50% single-tube-share threshold.** The same statistic is present in simulations that later finish distributed and are explicitly classified as non-concentrating. It is therefore a transient first-passage time, not necessarily the onset of persistent collapse.

Those defects do not overturn the paper's broad “limits of discrimination” thesis, but they invalidate the present release-integrity claim and weaken the specific Result 3 convergence narrative. Result 3 can remain as exploratory model capacity after the event definition, classifier, and release are corrected.

### Headline-claim status

| claim | assessment | action needed |
|---|---|---|
| Conditional RSM vertex near grind dial 1.74 | **Supported within the declared fixed seven-term achieved-predictor specification.** The deletion, model-form, and wild-bootstrap sensitivities are useful. | Synchronize stale numbers, change the function default to achieved predictors, and keep the post-selection/first-stage limitations explicit. |
| Three selected central-setting endpoint means do not show a middle-dial maximum | **Supported descriptively for this campaign.** The manuscript correctly avoids a clean causal dial interpretation. | Replace “monotonically” in the Figure 1 caption with “numerically ordered”; retain achieved-condition confounding. |
| Static heterogeneity can generate a small interior maximum | **Supported as model capacity, not identification.** The corrected Jensen audit is coherent. | Generate Figure 1 annotations from the result object, not hard-coded prose; retain fragility and small prominence. |
| Time-varying curves reconstruct the 9-bar trace much better than tested constants | **Supported descriptively/in-sample.** | Do not give the fixed-loss block resampling conventional inferential weight; soften “robustly required,” add block-length sensitivity, and specify the stationarity approximation. |
| A specific temporal bed mechanism is not identified | **Supported and well aligned with the cubic comparator and structured residuals.** | Preserve the current cautious conclusion. |
| Equilibrium calibration is not dominated by one pressure | **Supported within the same campaign.** | Preserve the within-rig, donor-conditional scope. |
| The isolated swelling/fines resistance-only branches have the wrong sign at fixed pressure | **Supported as a conditional sign constraint.** | Keep the current coupled-system caveat and distinguish source model curves from empirical validation. |
| The implemented N-tube model can end in strong concentration under near-choke, fixed-flow, low-lateral assumptions | **Plausible exploratory model-capacity result, but the committed bundle is stale.** | Regenerate with the corrected classifier and report exact state classes. |
| The N-tube “collapse-time event” is converged under Euler refinement | **Not established as currently named.** The statistic is a first passage and can occur in trajectories that subsequently deconcentrate. | Rename and add a persistent-event definition; then rerun temporal and spatial refinement. |
| Current bundle/manifest certifies the manuscript and figures | **False for the reviewed head.** | Clean rebuild at the reviewed commit or a later release commit; include all artifacts and semantic invariants. |

---

## 3. How the reviewer brief was handled

The brief correctly asks reviewers not to relabel known, already disclosed limitations as novel findings. I therefore classify findings below as:

- **NEW-DEFECT:** a newly identified error or contradiction;
- **DISCLOSURE-ADEQUACY:** a known limitation whose wording or use is not yet consistently bounded;
- **RELEASE/VENUE:** an acknowledged but submission-blocking packaging or manuscript task;
- **MINOR:** editorial, graphical, or low-risk consistency issue.

### Adequacy of the known disclosures

| disclosed item in the brief | adequacy assessment | does it undermine a headline? |
|---|---|---|
| Full trajectory convergence not yet done | The disclosure is honest, but the manuscript and generated verdict still call the first-passage event “collapse” and say it is not a stepping artifact. The event definition creates a new problem beyond the already disclosed missing trajectory norm. | It does **not** undermine the broad exploratory endpoint-capacity claim; it **does** undermine the present collapse-time convergence subclaim. |
| One block length for Result 2 | Disclosed, but the prose still says the 8-second fixed-loss resampling shows time variation is “robustly required.” The resampling does not refit and relies on an unexamined stationarity/local-dependence approximation. | It does not overturn the large descriptive RMSE separation from constants; it limits inferential language. |
| Numerical-invariant rather than physical conservation | The brief states this correctly. The manuscript still calls it a “full-trajectory conservation audit,” which can be read as physical conservation. | No effect on the central thesis; relabeling is required. |
| No physical lateral operator or stability analysis | Adequately disclosed and respected in most prose. | No, provided Result 3 remains exploratory. |
| Conditional RSM uncertainty | Adequately disclosed. The response-surface claim is now one of the stronger parts of the manuscript. | No. |
| Sixteen stochastic seeds | Adequately disclosed in the brief, but the manuscript table and generated verdict still say four seeds. | Does not overturn the endpoint finding, but it shows artifact drift and must be corrected. |
| Figures recompute and bundle is incomplete | Correctly disclosed, but the actual current bundle is stale and semantically inconsistent with current code. This is more serious than an abstract “future improvement.” | It undermines reproducibility certification, not necessarily the scientific thesis. |
| Incomplete panel source data | Adequately disclosed; still a submission requirement. | No. |
| Journal conversion owed | Correctly disclosed and plainly submission-blocking. | No scientific headline impact. |
| Novelty search incomplete | Adequately disclosed. | The manuscript appropriately avoids a novelty claim. |
| Clean tagged release deferred | Correctly disclosed, but the current manifest's passing status can mislead readers because it describes an older dirty generation state. | It undermines any release-certification claim until fixed. |

---

## 4. Prioritized action matrix

### P0 — required before journal submission or external scientific release

| ID | class | issue | required action | acceptance criterion |
|---|---|---|---|---|
| B6-01 | NEW-DEFECT / RELEASE | The current head is `b4de0d9…`, while the committed result bundle and manifest identify `fa4ec00…` and `git_dirty: true`. | Run the entire Paper B build from a clean checkout of the release commit. Regenerate bundle, figures, captions, source data, and manifest together. | Manifest `source_commit`, bundle source commit, Git HEAD, manuscript release commit, and figure provenance all match; tree is clean; strict build passes. |
| B6-02 | NEW-DEFECT | The frozen bundle retains the old N-tube classifier: lateral 0.1 is marked `concentrates: true` despite `N_eff≈19.05` and top-one share ≈0.0676. | Regenerate with current classifier code. Add semantic validation of every classified row. | Every `single_channel`/`concentrates` row satisfies top-one share ≥0.5, `N_eff≤2`, and persistence criteria; lateral 0.1 is not single-channel. |
| B6-03 | NEW-DEFECT | `collapse_time_s` is the first top-one-share crossing of 0.5, even for simulations that later end distributed. | Rename it “first-passage time to top-one share >0.5.” Define a separate persistent-concentration onset with a prespecified persistence/hysteresis rule. | Pressure-control and lateral-0.3 runs no longer report a “collapse” unless they meet the persistent criterion; first-passage and persistent-onset results are both shown. |
| B6-04 | NEW-DEFECT | `ntube_switching_convergence` promises a trajectory-deviation norm but does not compute it, while its verdict says switching is a real feature and not a stepping artifact. | Either implement the documented common-time-grid trajectory norm and event-error analysis or delete the promise and narrow the verdict to first-passage sensitivity under Euler/output-grid refinement. | Function output, docstring, manuscript, caption, and bundle use the same limited claim. |
| B6-05 | NEW-DEFECT | The manuscript says the Foster machine-only model reconstructs a “digitized source trace,” while Figure 3/caption correctly say it is a numerical reproduction of a published **model curve**, not measured data. | Rewrite the Result 2 opening sentence and all related metadata. | No artifact describes the Foster panel as a fit to measured data unless measured data are actually used. |
| B6-06 | DISCLOSURE-ADEQUACY | The 8-second block procedure resamples fixed squared-loss sequences, does not refit either model, uses one trace, and assumes locally stationary dependence; “robustly required” and a conventional “95% interval” are too strong. | Call it a conditional fixed-loss block-resampling distribution/range. Add 4/8/16/24-second block sensitivity and state the stationarity approximation. | Main conclusion is descriptive: tested time-varying curves have much lower in-window RMSE than constants; no coverage-calibrated inference is implied. |
| B6-07 | NEW-DEFECT / CONSISTENCY | The manuscript table says four stochastic seeds although current code uses 16; the generated verdict also says four. | Generate seed count and all sweep ranges directly from the result object. | Manuscript, figure source data, bundle, captions, and code all say 16 for this analysis. |
| B6-08 | RELEASE | The verifier compares cached fields against hard-coded expected constants, not the manuscript prose or plotted arrays. | Build machine-readable claim IDs into manuscript tables/captions or generate prose/tables from the bundle; verify figure source-data hashes and plotted arrays. | A changed bundle value either automatically updates the manuscript/figure or fails the build. |
| B6-09 | RELEASE | The manifest omits manuscript, reviewer brief, captions, figures, source code, and complete environment dependencies. | Expand the dependency manifest to include all scientific inputs and outputs. | Manifest hashes every data input, code module, manuscript/caption source, figure source table, rendered figure, bundle, and lock/environment file. |
| B6-10 | VENUE | The draft remains an internal project document with review IDs, ROADMAP references, function names as prose, an open-gap ledger, and a status/to-do section. | Convert to a conventional manuscript with Methods, equations, estimands, uncertainty methods, references, declarations, data/code availability, and supplementary methods. | A reader can understand and reproduce the analysis without repository project-management documents. |
| B6-11 | VENUE / METHODS | Governing equations, calibration/evaluation splits, numerical solver details, parameter units, tolerances, and uncertainty estimands are not presented conventionally. | Add a complete Methods section and parameter-provenance table. | Every curve and statistic has an equation/model definition, input source, fitted parameter count, fitting target, evaluation target, and uncertainty method. |
| B6-12 | RELEASE | Figures currently recompute live rather than consuming one immutable analysis result. | Make plotting functions consume only frozen, schema-validated result and source-data objects, or rigorously cross-check live output against them. | Clean build is deterministic and produces identical hashes under the pinned environment. |

### P1 — substantial scientific or interpretive revision

| ID | class | issue | required action | acceptance criterion |
|---|---|---|---|---|
| B6-13 | NEW-DEFECT | The Figure 5 “timestep-converged” annotation is attached to a first-passage statistic and the early trajectory visibly collapses, rebounds, and recollapses. | Add a 0–10 s inset and mark first passage, recovery, and persistent onset separately. | Figure makes transient switching visible and does not imply first crossing equals persistent collapse. |
| B6-14 | NEW-DEFECT | Non-concentrating pressure-control and high-lateral runs have non-null `collapse_time_s` values. | Add regression tests using these counterexamples. | Nonpersistent runs cannot be reported as collapsed by the persistent-event field. |
| B6-15 | DISCLOSURE-ADEQUACY | “Full-trajectory conservation audit” conflates definitional share normalization and imposed flow control with physical conservation. | Rename to “full-trajectory numerical-invariant audit.” State what is definitional, imposed, and untested. | No claim of solute, mass, pressure-work, lateral-flux, or age conservation is made without an explicit balance equation. |
| B6-16 | NEW-DEFECT | Figure 5d and its caption call computed N-tube `N_eff` “MEASURED.” | Replace “measured” with “simulated” or “computed.” | Figure, caption, and prose consistently distinguish numerical from empirical quantities. |
| B6-17 | CONSISTENCY | Result 3 mixes `N=400` baseline, `N=200` convergence, and `N=150` floor audit; the brief describes “one configuration (N=200).” | Add a configuration table and state N for each panel/analysis. Update the reviewer brief. | Each numerical result is tied to one explicit configuration; no implication that all panels use the same N. |
| B6-18 | DISCLOSURE-ADEQUACY | “Invariant” is used for endpoint class despite meaningful event-time and some final-state variability. | Use “endpoint class unchanged in the tested cases” and report quantitative ranges. | Narrative separates categorical stability from numerical invariance. |
| B6-19 | NEW-DEFECT | Seed 8/9 outcomes lie almost exactly on the `top1=0.5`, `N_eff=2` classifier boundary. | Perform threshold sensitivity and report all state counts. | Main qualitative conclusion is unchanged across reasonable prespecified thresholds, or the fragility is disclosed. |
| B6-20 | CONSISTENCY | `schmieder_rsm_refit` defaults to nominal target predictors even though the primary analysis and source contract use achieved predictors. | Change default to `predictors="achieved"` or require an explicit keyword. | Accidental calls cannot silently use the secondary sensitivity specification. |
| B6-21 | CONSISTENCY | Section 7 retains stale RSM values: adjusted R² 0.65, CI [1.69,1.80], Q² 0.48, and leverage 0.18 differ from the current bundle. | Generate or remove these numbers. | Values match the frozen bundle at full precision and are not duplicated manually. |
| B6-22 | CONSISTENCY | Figure 1 caption calls cell means “monotonically” increasing while the text deliberately says “numerically ordered, not statistically monotone.” | Use the same language as the manuscript. | Caption says “numerically ordered” and retains the unresolved 1.4–1.7 contrast. |
| B6-23 | RELEASE | Figure 1b annotations “10/25” and “full-grid median prominence ≈0” are hard-coded in plotting code. | Pull them from a frozen closure-sensitivity result. | A unit test fails if annotation and analysis object differ. |
| B6-24 | FIGURE | Figure 2 uses internal tokens such as `impl`, `same-campaign`, `qual-cap`, and `elevated-pc` that are not self-explanatory in the figure. | Use publication-facing terms or include a compact in-figure legend/dictionary. | Figure is interpretable without opening a repository dictionary. |
| B6-25 | FIGURE | Figure 3 labels Φ(t) as “0 params,” contradicting the careful provenance table. | Replace with “0 coefficients fitted to displayed Q(t); donor/campaign parameters imported.” | Figure and caption convey the complete parameter provenance. |
| B6-26 | FIGURE | Figure 6 plots only best constant, cubic, and Φ(t) ACFs but the caption says “every branch.” | Add static κ(P), or say “the three plotted branches.” | Caption exactly matches plotted series. |
| B6-27 | FIGURE | Figure 6 says ACF remains “near unity for several seconds in every branch”; the cubic drops materially by 2.5 s. | Say “strongly positive across the displayed lags.” | Description is visually accurate. |
| B6-28 | FIGURE / METHODS | Figure 6 juxtaposes raw-sample lag-1 ACF with a Durbin–Watson statistic computed after 1-second decimation. | State both sampling intervals in the caption and Methods. | Reader can reproduce both diagnostics and understand why they differ. |
| B6-29 | DISCLOSURE-ADEQUACY | The abstract says N-tube “concentration is floor-independent,” which can be read as a broad model property. | Say “the endpoint class was unchanged over the tested conductance floors in the specified configuration.” | Scope is explicit in the abstract. |
| B6-30 | CONSISTENCY | The manuscript header lists `fig{1..5}` although a supplementary Figure 6 exists and `render_all` emits it. | List five main figures plus Figure S1/6 consistently. | Header, captions, manuscript calls, source data, and build inventory agree. |
| B6-31 | METHODS | “Two published datasets” is ambiguous because the analysis also imports Cameron, Foster, Mo, Fasano, Lee, and other sources. | Define the two primary empirical evaluation campaigns and separately list calibration/donor/model-source evidence. | Dataset roles are unambiguous in abstract and Methods. |
| B6-32 | METHODS | The dataset manifest paragraph does not fully enumerate model-curve and donor-source roles. | Add a provenance matrix. | Every imported model, parameter, trace, and target is linked to a citation and repository object. |
| B6-33 | RESULT 2 | The pointwise and conditional block intervals are presented alongside very strong residual structure but without model-error interpretation. | Treat residual structure as evidence of misspecification; report phase-specific residual summaries or a smooth residual model. | Discussion does not imply low RMSE equals adequate stochastic fit. |
| B6-34 | RESULT 1 | The plotted RSM band is the iid residual-bootstrap band while wild-bootstrap sensitivity is emphasized in prose. | Show the preferred robust band, show both, or clearly label the plotted band as conditional iid-residual. | Figure and inferential narrative use the same uncertainty contract. |
| B6-35 | RESULT 1 | The retained model was selected by backward elimination, but the manuscript's intervals are conditional on that choice. | Keep this caveat prominent and avoid calling the interval a general physical optimum interval. | Abstract, Results, caption, and conclusion all say “conditional vertex.” |
| B6-36 | RESULT 3 | The current convergence acceptance criterion allows a 0.5 s change without scaling to event time or output resolution. | Prespecify absolute and relative tolerances and show convergence order/sensitivity. | Criterion is justified and not chosen after viewing results. |
| B6-37 | RESULT 3 | The output-grid first-passage time is quantized; identical values across substeps can reflect output sampling rather than solver convergence. | Interpolate the crossing or refine output times independently of internal substeps. | Event-time convergence is not limited by the fixed recording grid. |
| B6-38 | RELEASE | Generated narrative strings in the bundle are stronger or stale: “ZERO-param,” “time variation is NEEDED,” “only TIES,” “real feature,” “not a stepping artefact,” and “4 stochastic realisations.” | Remove narrative verdicts from machine results or generate them from a centrally tested claim dictionary. | No machine-generated prose exceeds the manuscript's approved claim scope. |

### P2 — editorial, graphical, and completeness improvements

| ID | class | issue | required action |
|---|---|---|---|
| B6-39 | FIGURE | Figure 5a compresses the scientifically important first 10 seconds into a 100-second axis. | Add an inset or split view. |
| B6-40 | FIGURE | Figure 5d is crowded by two log axes, two closures, gains, and computed endpoint counts. | Split into two panels or move the closed-form diagnostic to supplementary material. |
| B6-41 | FIGURE | Figure 3c has six overlapping series and a small legend. | Use separate shared/LOPO panels, direct labels, or a difference plot. |
| B6-42 | FIGURE | Several annotations are too small for journal reproduction. | Test at final column width and minimum journal font size. |
| B6-43 | EDITORIAL | Replace internal identifiers such as MAJ-xx, B5-xx, ROADMAP §x, and function names in scientific prose. | Move traceability to a supplementary reproducibility table. |
| B6-44 | EDITORIAL | Replace all “review-endorsed,” “owed,” “still owed,” and project-status language. | Use ordinary limitations and future-work prose. |
| B6-45 | REFERENCES | Add a complete, checked bibliography and cite every source model at first use. | DOI and year must match the final published item; distinguish the `waszkiewicz2025` repository key from the 2026 paper. |
| B6-46 | DATA | Export complete per-panel source data, including every plotted line, band, bar, marker, and annotation statistic. | Source-data package can regenerate all panels without running the scientific analysis. |
| B6-47 | ACCESSIBILITY | Retain color-independent symbols and test grayscale/colour-vision accessibility. | All distinctions remain visible without color. |
| B6-48 | ABSTRACT | Reduce implementation detail and state the empirical unit and validation scope more directly. | Abstract reads as a paper rather than a repository audit. |

---

## 5. Detailed review comments

## 5.1 Title, abstract, and central positioning

### 5.1.1 The revised title is appropriate

“Limits of mechanism discrimination from integrated espresso measurements” accurately reflects the strongest contribution. It avoids claiming that a specific mechanism has been identified and avoids the unsupported language of linear stability. This title should be retained unless the final journal requires a shorter form.

### 5.1.2 The abstract's central conclusion is supportable

The sentence that integrated measurements do not uniquely identify a mechanism is consistent with the analyses, provided the scope remains “within the datasets and implemented model classes.” The manuscript should preserve that qualifier everywhere, including the title page, conclusion, graphical abstract, and highlights.

### 5.1.3 “Two published datasets” needs definition

The abstract appears to mean two principal empirical evaluation campaigns: Schmieder for the endpoint/RSM analysis and Waszkiewicz for the temporal/cross-pressure analysis. Yet the paper also uses Cameron as a calibration source, Foster as a model-curve source, Mo and Fasano as mechanistic branches, and Lee as a competing model. Replace “two published datasets” with “two principal empirical campaigns, supplemented by donor calibrations and published model curves,” or provide equivalent wording.

### 5.1.4 The Result 2 abstract wording remains slightly too inferential

“Establishes a need for time variation” is defensible as a constrained descriptive statement about the tested curves and scoring windows. It should not be read as a population-level statistical requirement. A safer abstract formulation is:

> “Time-varying curves reduced in-window reconstruction error substantially relative to the tested constant nulls, while a flexible cubic performed similarly to the mechanistic trajectory; the trace therefore supports temporal flexibility but not a unique mechanism.”

### 5.1.5 The Result 3 floor claim should be narrowed

“Concentration is floor-independent” is too broad because only a specified finite-time endpoint classification was unchanged over a tested floor range. Use “the endpoint class was unchanged over the tested conductance-floor sweep in the specified configuration.”

### 5.1.6 The broad thesis survives the disclosed limitations

The open issues around full trajectory convergence, physical lateral exchange, post-selection RSM inference, and second-rig transfer do not invalidate the limits-of-discrimination thesis. They constrain individual subclaims. This distinction should be made explicit in the Discussion: the paper is strongest as an observability/claim-discipline study, not as a validated new model of puck instability.

---

## 5.2 Methods, data provenance, and scientific units

### 5.2.1 The Schmieder source description is now largely accurate

The manuscript correctly identifies the extraction run—not the fraction or sensor sample—as the experimental unit, describes 15 design settings with three repetitions and six at the centre, and explains that cup outcomes were reconstructed from the measured first fraction plus integration of fitted extraction kinetics. This matches the source study. The paper should retain this exact distinction.

### 5.2.2 The paper must distinguish reconstructed endpoint uncertainty from direct endpoint measurement

The RSM and selected cell analyses use source-derived cup outcomes. Their uncertainty includes at least run-to-run variation and first-stage extraction-kinetics reconstruction, but the current conditional bootstrap treats the outcomes as observed responses. The brief discloses that first-stage propagation is open. That is acceptable for the conditional claim, but the Methods must state explicitly that the intervals do not propagate kinetic-fit uncertainty.

### 5.2.3 The source's achieved-predictor contract is correctly used in the primary build

The source used set grinding level with experimentally achieved flow and temperature. The current primary build calls `schmieder_rsm_refit(... predictors="achieved")`, which is correct. However, the function default remains `predictors="target"`. This is a latent reproducibility hazard. Defaults should encode the primary scientific contract, or the argument should be mandatory.

### 5.2.4 The registry concept is useful internally but is not a substitute for Methods

A typed component registry, evidence matrix, and validation gates can support reproducibility. A journal reader still needs equations, boundary conditions, parameter definitions, calibration targets, numerical solvers, and uncertainty estimands. The current section reads as software architecture rather than scientific Methods.

### 5.2.5 Add a calibration/evaluation provenance table

For every branch, list:

- governing equation or algorithm;
- empirical source;
- parameter source;
- parameters fitted to the displayed target;
- parameters fitted elsewhere in the same campaign;
- literature-fixed or constructed quantities;
- evaluation window and metric;
- validation strength.

The existing Result 2 parameter table is a good seed but should cover all results.

### 5.2.6 Dataset keys must not substitute for citations

The paragraph explaining that repository key `waszkiewicz2025` maps to a 2026 paper is helpful internally. In the manuscript, cite the final publication normally and relegate repository keys to Data Availability or supplementary provenance.

### 5.2.7 Model-source roles are incomplete in the dataset list

Foster, Mo, Fasano, and related imported branches are scientifically important even where no raw dataset is loaded. Include them in a model-source/provenance table rather than leaving the impression that only the listed dataset keys define the evidence base.

---

## 5.3 Result 1 — endpoint and response-surface analysis

### 5.3.1 The observed three-cell conclusion is correctly narrow

The selected source-derived TDS extraction-yield means are numerically ordered, and the middle dial lies below dial 2.0 in this campaign. The manuscript appropriately notes that the 1.4–1.7 contrast includes zero and that achieved conditions differ. This supports “the selected cell means do not show a middle-dial maximum,” not “the physical grind response is monotone.”

### 5.3.2 Do not use “monotonically” in the Figure 1 caption

The caption currently says the three means increase monotonically. The manuscript itself carefully says “numerically ordered, not statistically monotone.” Use the same wording in both places.

### 5.3.3 The achieved-condition confounding is load-bearing

Pressure differs substantially across the three nominal dial settings. The manuscript correctly treats the selected-cell contrast as descriptive. The final paper should not place a p-value beside a causal dial statement. A full design-aware model with achieved covariates would be valuable but is not necessary for the current descriptive conclusion if the limitation remains explicit.

### 5.3.4 The conditional RSM vertex is reproducible and reasonably stress-tested

The current result object reports approximately:

- vertex 1.743;
- adjusted R² 0.643;
- iid residual-bootstrap interval about [1.699, 1.817];
- wild Rademacher interval about [1.700, 1.829];
- wild Mammen interval about [1.693, 1.818];
- leave-one-run range 1.736–1.765;
- leave-one-setting range 1.720–1.776;
- full-quadratic vertex about 1.737.

Those checks support the limited statement that a retained achieved-predictor quadratic surface has a stable conditional interior vertex within this design.

### 5.3.5 The interval must remain conditional

The source model involved backward elimination, and the endpoint itself is reconstructed. Neither model-selection uncertainty nor first-stage endpoint uncertainty is propagated. The word “conditional” should precede “vertex” at each load-bearing occurrence, including Figure 1, the abstract, and the conclusion.

### 5.3.6 The RSM figure should use the preferred uncertainty contract

Figure 1 uses an iid residual-bootstrap band while the prose highlights wild-bootstrap sensitivity because the within-setting SD varies greatly. Either plot the preferred heteroskedasticity-aware band, overlay both, or explicitly label the band as the conditional iid-residual result and place wild-bootstrap intervals in a table.

### 5.3.7 Section 7 contains stale RSM numbers

The open-gap summary reports values that differ from the current result object, including adjusted R² 0.65 rather than 0.643, interval [1.69,1.80] rather than approximately [1.699,1.817], Q² 0.48 rather than 0.470, and leverage 0.18 rather than 0.20. This is precisely the sort of drift a single-source build should prevent. Remove the duplicate summary from the manuscript or generate it.

### 5.3.8 The Jensen correction is now scientifically coherent

The manuscript correctly compares `E[EY(K)]` with `EY(E[K_evaluated])`, not automatically `EY(1)`, after finite-support clipping. It reports the full negative range and correctly identifies −4.64 as the largest-magnitude loss. This prior issue is adequately corrected.

### 5.3.9 The frozen bundle still contains stale Jensen prose

The bundle verdict calls approximately −1.379 the “worst” gap, even though it is the smallest-magnitude deficit. Machine-readable numerical fields are correct; generated prose is not. Avoid storing scientific narrative in result JSON unless it is generated from tested semantic rules.

### 5.3.10 The static-heterogeneity result remains capacity, not identification

The closure is calibrated to Cameron, the interior maximum is present in only 10 of 25 tested closure combinations, and full-grid median prominence is approximately zero. The manuscript is right to describe the effect as fragile and small. This is useful negative/limiting evidence, not a mechanism winner.

### 5.3.11 Hard-coded Figure 1 annotations should be eliminated

The plotting code inserts “10/25” and “full-grid median prominence ≈0” as literal strings. These should come from a frozen closure-sensitivity result with a test that checks the displayed annotation.

---

## 5.4 Result 2 — temporal ladder, residuals, and cross-pressure analysis

### 5.4.1 Correct the Foster model-versus-data statement

The manuscript says the machine-only model “reconstructs a mid-shot flow minimum on the digitized source trace.” Figure 3a and its caption correctly call it a numerical reproduction of the published Foster **model curve**, not measured data. The model-capacity inference remains useful:

> a dip-and-recovery shape is available in a machine/infiltration model without evolving bed resistance.

It should not be described as a fit to a measured trace unless the empirical trace and fitting procedure are provided.

### 5.4.2 The null-first ladder is conceptually strong

The progression from three constant/static baselines to Φ(t) and a flexible cubic is one of the paper's strongest design choices. It shows that low error from a mechanistic-looking curve is insufficient when a generic temporal curve does at least as well.

### 5.4.3 Replace “0 params” in Figure 3

The axis label “0 fit Q(t)” is reasonably scoped, but the panel annotation says Φ(t) has “0 params.” It has zero additional coefficients fitted to the displayed Q(t) trace, not zero parameters. It imports equilibrium and TDS-sigmoid quantities. Use the longer but accurate label.

### 5.4.4 “Time variation is required” should be read as a model-set statement

The observed RMSE separation is large and persists over three windows. That supports saying the tested constant curves cannot reconstruct the observed shape nearly as well as the tested time-varying curves. It does not prove that any arbitrary time-varying physical state is required in a broader data-generating sense, especially because machine/headspace dynamics can also create temporal structure.

### 5.4.5 The block procedure is not a full bootstrap

Code inspection confirms that the procedure resamples blocks from two already-computed squared-error sequences. It does not refit the cubic, recompute donor calibration, refit Φ(t), or propagate measurement/model uncertainty. The manuscript discloses this, which is good. The remaining problem is the inferential language placed on the output.

### 5.4.6 “Preserves serial dependence” is too absolute

A moving-block scheme approximates local dependence under assumptions such as stationarity and suitable block length. The loss-difference sequence here is visibly phase-varying across a single shot. Say that the scheme retains local ordering within sampled 8-second blocks under a working stationarity approximation, not that it simply “preserves” the full dependence structure.

### 5.4.7 Report a resampling range, not an unqualified confidence interval

Because the procedure conditions on fitted curves and uses one unvalidated block length, label [−0.60,−0.23] as a central 95% conditional block-resampling range for fixed losses. Do not imply nominal frequentist coverage for the full fit-and-compare procedure.

### 5.4.8 Add the disclosed block-length sensitivity

The brief correctly lists 4/8/16/24 seconds as an open task. This is a modest and high-value rerun. Report median and 2.5/97.5% quantiles for Φ-minus-constant and Φ-minus-cubic at each block length. If the sign against constants remains stable, it strengthens the descriptive conclusion without overclaiming formal inference.

### 5.4.9 Residual structure is evidence of model inadequacy, not merely uncertainty inflation

Lag-one autocorrelation near 0.99 and Durbin–Watson near 0.01 show coherent lack of fit. The manuscript should say explicitly that even the low-RMSE branches leave systematic temporal structure, which may reflect missing machine dynamics, phase transitions, donor mismatch, or other omitted state variables.

### 5.4.10 Figure 6 does not show every branch

The ACF panel contains best constant, cubic, and Φ(t), but not static κ(P). Change “every branch” to “each plotted branch” or add the missing series.

### 5.4.11 Figure 6's temporal resolutions need clarification

The lag-one ACF is computed at the raw sample interval, while the stated Durbin–Watson summary is computed after decimation to 1 second. Put both intervals in the caption. Otherwise, readers may assume they are equivalent diagnostics at the same sampling scale.

### 5.4.12 “Near unity for several seconds” is visually inaccurate for the cubic

The cubic residual ACF remains strongly positive but declines to roughly 0.7–0.8 by the end of the displayed 2.5-second lag range. Use “strongly positive across the displayed lags.”

### 5.4.13 The swelling/fines sign argument is appropriately bounded

The manuscript now says an isolated resistance-increasing branch at fixed pressure cannot by itself generate a rising-flow contribution. That is the correct scope. Swelling can affect inter- and intra-grain transport in coupled models, and fines can alter permeability and flow, so the paper should retain its current statement that those processes may still be present while another mechanism controls the net sign.

### 5.4.14 Cross-pressure LOPO is now displayed and well scoped

Figure 3c now includes held-out markers, and the text clearly separates held-out all-pressure, shared-calibration all-pressure, shared-calibration off-9-bar, and equilibrium-curve Q² summaries. This corrects an important previous weakness.

### 5.4.15 The cross-pressure maximum claim is appropriate

“The two-parameter equilibrium fit is not dominated by any single pressure” is supported by the reported calibration drift and similar held-out/shared mean errors. The manuscript correctly avoids claiming that the residual-vs-pressure pattern is physically validated.

### 5.4.16 Figure 3c remains visually dense

Six series are difficult to distinguish. A useful alternative is a two-panel display: shared RMSE by pressure and held-out-minus-shared RMSE, or direct labels at the line endpoints. This is a readability issue rather than a scientific defect.

### 5.4.17 Figure 4 is an honest negative result

The shared-porosity composition worsens the reconstruction, and the manuscript correctly avoids deciding whether the failure is due to transfer, initial conditions, control, or composition form. Preserve this negative result; it materially supports the paper's limits theme.

---

## 5.5 Result 3 — exploratory N-tube composition

### 5.5.1 The exploratory classification is appropriate

The manuscript consistently says Result 3 is exploratory and not a stability theorem. That disclosure is adequate for a model-capacity result. A physical lateral operator, balance laws, and formal stability analysis are not prerequisites for retaining the result as an exploratory demonstration, provided the numerical event and endpoint claims are correct.

### 5.5.2 The current frozen bundle is incompatible with current classifier code

Current code defines `concentrates` only when the state is `single_channel`, requiring final top-one share ≥0.5 and `N_eff≤2` unless the trajectory is classified as transient. The committed bundle nevertheless marks the lateral-0.1 run as concentrating even though final top-one share is approximately 0.0676 and `N_eff≈19.05`. This is a decisive release-integrity failure and evidence that the bundle was generated with older code.

### 5.5.3 The classifier correction described in the brief has not reached the frozen artifacts

The reviewer brief says the old top-decile classifier was fixed. That appears true in source code, but not in the committed result bundle. The correct response is not to re-raise the old conceptual issue; it is to require an artifact-coherent clean rebuild and semantic tests.

### 5.5.4 “Collapse time” is a first-passage statistic

The code records the first time at which the largest single-tube share exceeds 0.5. This is not the same as the onset of persistent concentration. It can be triggered by a transient excursion.

### 5.5.5 Counterexamples occur inside the current bundle

The pressure-control run ends distributed (`N_eff≈218.8`, top-one share ≈0.02) but has `collapse_time_s≈4.104`. The lateral-0.3 run ends distributed (`N_eff≈307.4`, top-one share ≈0.0072) but has `collapse_time_s≈3.003`. These are direct counterexamples to interpreting the field as persistent collapse.

### 5.5.6 Rename and split the event metrics

At minimum report:

1. first-passage time to top-one share >0.5;
2. duration above threshold;
3. number of threshold crossings;
4. persistent-onset time, defined prospectively—for example, the first time top-one share remains >0.5 and `N_eff≤2` for at least 5 seconds or through the remainder of the shot;
5. final state class.

The exact persistence rule should be justified and sensitivity-tested, not chosen post hoc to produce convergence.

### 5.5.7 Figure 5a visually demonstrates rebound

The early trajectory collapses, recovers, and collapses again before settling. The current 0–100 second scale compresses this behavior. Add a 0–10 second inset and label first passage and persistent onset separately.

### 5.5.8 The convergence function does not implement its documented trajectory norm

The docstring promises maximum `|N_eff(t)|` trajectory deviation against the finest reference. The returned object contains only event times and final `N_eff`. This is an implementation-contract defect. Either compute the norm on a common physical-time grid or delete the promise.

### 5.5.9 The generated convergence verdict is too strong

The bundle says the switching is a “real feature” and “not a stepping artefact.” Euler substep stability of a quantized first-passage event does not establish that. A more accurate statement is:

> “The first recorded crossing of the 0.5 top-one-share threshold was unchanged under the tested Euler substep refinement at fixed spatial discretization and output grid.”

### 5.5.10 Output-grid quantization can mask event-time changes

The identical 2.603-second values across substeps may reflect the fixed output times at which the event is observed. Interpolate the crossing or independently refine the output grid. Report error relative to the finest temporal/spatial solution.

### 5.5.11 Separate spatial and temporal refinement

The N sweep changes the finite-network realization and event time substantially. Temporal convergence at fixed N does not imply convergence as N changes. Report first-passage and persistent-onset times against both N and timestep.

### 5.5.12 The paper still has a stale four-seed statement

The robustness table says “4 seeds,” whereas code and the result object use 16 realizations. The generated verdict also says four. This must be generated from one source.

### 5.5.13 The 16-seed result is categorical, not numerically invariant

Most runs end near one effective channel, but some end at approximately 2.0 or 1.71, and first-passage times span approximately 1.4–3.5 seconds. Say the endpoint class was unchanged under the current threshold for the 16 tested seeds, not that the result is invariant.

### 5.5.14 Threshold sensitivity is required

Two seeds are just above top-one share 0.5 and at `N_eff≈2`. Small numerical or definitional changes can move them between classes. Report state counts under reasonable threshold alternatives or define an uncertainty band around the classifier.

### 5.5.15 “Conservation” should be relabeled

Normalized shares sum to one because `s=w/w.sum()`. Under flow control, mean relative flow is imposed near one by construction. The current audit is useful as a numerical-invariant and non-negativity check, but it is not a physical conservation law. Use that exact label.

### 5.5.16 Physical balances remain a known, appropriately deferred task

The brief correctly states that solute inventory, pressure work, lateral flux, and age balance are not audited. This does not preclude an exploratory model-capacity result, but the manuscript should not use “conservation” without the “numerical-invariant” qualifier.

### 5.5.17 Figure 5d uses the wrong epistemic label

`N_eff` is simulated/computed, not measured. Replace “MEASURED” in title, axis label, annotation, and caption.

### 5.5.18 Result 3 uses multiple baseline sizes

The main trajectory is N=400, the switching-convergence routine defaults to N=200, and the floor audit uses N=150. The reviewer brief's “one configuration (N=200)” is therefore incomplete. Add a configuration table and update the brief.

### 5.5.19 The floor result is valid only as an endpoint-class check

The closed-form gain is explicitly floor-dependent, while final `N_eff` is reported as insensitive over the tested floors. That distinction is valuable. Keep the claim at the level of endpoint class/metric in the tested finite-time configuration.

### 5.5.20 “Low lateral” needs a quantitative definition

At lateral 0.1, the old bundle gives an oligarchic state (`N_eff≈19`), not single-channel concentration; at 0.3 it is distributed. Define whether “concentrate” means any low-dimensional oligarchy or specifically single-channel collapse. Use the explicit state labels in prose and figures.

### 5.5.21 Figure 5b demonstrates endpoint saturation, not convergence

The manuscript already says this, which is good. Keep the word “saturation.” A line at exactly one across N and substeps contains no information about trajectory error.

### 5.5.22 Result 3 can remain after correction

The exploratory conclusion that the implemented positive-feedback composition can produce strong final concentration under fixed-flow, near-choke, low-lateral assumptions remains plausible. The required revision is to cleanly separate:

- transient first passage;
- persistent final state;
- numerical endpoint saturation;
- solver convergence;
- physical stability.

---

## 5.6 Discussion and conclusion

### 5.6.1 The Discussion's observability framing is the manuscript's strongest contribution

The comparison of what whole-cup, whole-bed, and single-outlet measurements hide is useful. The table proposing first-drip, bed-state, and spatial/pathway-resolved measurements should be retained and strengthened with explicit hypotheses each measurement would separate.

### 5.6.2 Do not imply that Result 3 supplies evidence about real pucks

The manuscript correctly says the per-tube observations are simulated. Preserve this. Result 3 motivates an experiment; it does not provide experimental evidence for one-channel real-puck evolution.

### 5.6.3 The “two datasets examined” sentence should be clarified

Use “two primary empirical evaluation campaigns” and then distinguish calibration and model-source literature. This prevents a reader from wondering why numerous other studies appear in the analysis.

### 5.6.4 Remove the open-gap ledger and project status from the manuscript body

A journal Discussion may state limitations and future work. It should not contain internal task status, review IDs, exact backlog links, or notes such as “still owed.” Move traceability to a repository document or supplementary reproducibility appendix.

### 5.6.5 The conclusion should distinguish what survives from what does not

A suitable structure is:

1. endpoint cell means do not show the fitted middle-dial maximum;
2. a conditional RSM vertex exists but is model-conditional;
3. static heterogeneity can generate a small, fragile maximum;
4. time-varying curves outperform constants on one trace, but a flexible null prevents mechanism identification;
5. pressure LOPO supports calibration stability, not physical validation;
6. an exploratory N-tube construction can end concentrated under specific assumptions, but no instability is proven;
7. better observables are needed.

---

## 6. Figure-by-figure review

## Figure 1 — matched target and static-heterogeneity capacity

**Strengths**

- Clearly juxtaposes raw/source-derived cell observations with the conditional RSM curve.
- Shows the model's own non-portable dial axis and labels capacity rather than identification.
- Includes the RSM vertex and uncertainty.

**Required revisions**

1. Replace “monotonically” with “numerically ordered.”
2. State explicitly in the legend or caption that the plotted band is the iid residual-bootstrap band if that remains true.
3. Generate “10/25” and median prominence from the result object.
4. Enlarge annotation fonts and reduce overlapping explanatory text.
5. Consider showing achieved pressure values in panel a or in a compact inset because confounding is central.

## Figure 2 — evidence matrix

**Strengths**

- It is data-driven rather than manually colored.
- It explicitly avoids a winner-scoreboard interpretation.
- It names a decisive missing measurement for each mechanism.

**Required revisions**

1. Replace repository tokens with publication-facing labels.
2. Define parameter provenance and evidence-strength categories inside the figure or immediate caption.
3. Replace internal row labels such as `sigma(phi1)` and `y0` with mathematical notation or descriptive names.
4. Ensure all text is legible at final journal width.
5. Provide the matrix and dictionary as supplementary source data.

## Figure 3 — temporal ladder and cross-pressure evaluation

**Strengths**

- Panel a now clearly says “MODEL curve.”
- Panel c includes actual LOPO held-out markers.
- Panel d properly scopes swelling as an isolated resistance-only branch.

**Required revisions**

1. Correct the contradictory manuscript sentence about a digitized source trace.
2. Change “0 params” to “0 coefficients fitted to displayed Q(t).”
3. Reduce panel c clutter; consider shared and held-out difference views.
4. State that the cubic is in-sample and the block range is conditional fixed-loss resampling.
5. Add the exact evaluation-window shading/definition consistently across related figures.

## Figure 4 — shared-porosity composition diagnostic

**Strengths**

- Presents a negative result directly.
- Clearly labels the common evaluation window.
- Avoids claiming independent validation.

**Required revisions**

1. State the parameter provenance more compactly in the caption rather than dense plot text.
2. Consider adding a residual panel or integrated error table so the worsening is not communicated only through overlaid curves.
3. Keep the conclusion limited to the tested composition and imported parameterization.

## Figure 5 — exploratory N-tube result

**Strengths**

- Uses physical time.
- Separates endpoint saturation from physical contingencies.
- Labels Result 3 exploratory and does not call it a stability theorem.

**Submission-blocking revisions**

1. Rename the vertical event marker as first passage unless a persistent event is implemented.
2. Add an early-time inset showing rebound and recollapse.
3. Do not label the first passage “timestep-converged” without the exact configuration and event definition.
4. Replace every “MEASURED N_eff” with “computed/simulated N_eff.”
5. State N separately for trajectory, convergence, and floor audit.
6. Regenerate from current classifier code.
7. Replace “endpoint invariant” with “endpoint class unchanged in tested cases” where appropriate.
8. Consider splitting panel d into a supplementary figure because the dual-axis display is crowded.

## Figure 6 — residual diagnostics

**Strengths**

- Makes the strongly structured lack of fit visible rather than hiding it behind RMSE.
- Reinforces that these are reconstruction scores, not validation.

**Required revisions**

1. Add static κ(P) or change “every branch” to “the plotted branches.”
2. Replace “near unity for several seconds” with “strongly positive across displayed lags.”
3. State the raw sampling interval for lag-one ACF and 1-second decimation for Durbin–Watson.
4. Consider displaying the loss-difference series used by the block resampling; this would make the stationarity concern visible.

---

## 7. Reproducibility and build audit

### 7.1 The current bundle does not describe the current head

The public head reviewed here is `b4de0d971555…`. The committed bundle reports `source_commit = fa4ec00d7439…` and `git_dirty = true`. The manifest repeats that older source commit, marks the generation tree dirty, and reports `release_fresh = false`. This is not a release artifact for the current manuscript.

### 7.2 `bundle_matches_head=true` is stale metadata

The manifest's `bundle_matches_head=true` reflects the repository state when the manifest was generated, not the currently reviewed head. A committed static boolean cannot certify a later checkout. Verification must recompute this comparison at review/build time.

### 7.3 Non-strict verification can print success on a stale/dirty package

The code intentionally records freshness but does not treat it as failure unless `strict=True`. That is acceptable for development, but the generated “VERIFY OK” message is too reassuring when invoked on a non-release build. Use “numerical claim check passed; release freshness not certified” for non-strict mode.

### 7.4 The claim table is not a manuscript verifier

The build checks 18 numeric paths against authored expected values and tolerances. It does not parse the manuscript, compare captions, verify figure annotations, or confirm plotted arrays. Several defects identified here—four versus 16 seeds, hard-coded 10/25, old classifier state, Foster data/model wording—can pass the current verifier.

### 7.5 Result 3 build documentation contradicts implementation

The module header says slow Result 3 is referenced but not bundled. `compute(include_slow=True)` does bundle it, and `main()` uses that default for full/release builds. Update the documentation and runtime estimates.

### 7.6 Add semantic invariants, not only numeric tolerances

Examples:

- `concentrates` implies final state `single_channel`;
- `single_channel` implies top-one share ≥0.5 and `N_eff≤2`;
- “n_realisations” equals the number of seed rows and all generated text;
- each figure annotation equals its source-data field;
- each manuscript claim ID resolves to a current bundle field;
- current head equals source commit and tree is clean for release;
- no result marked “held-out” uses the held-out target in fitting;
- model/data provenance labels are enum-validated.

### 7.7 Freeze complete panel source data

For each panel, export a tidy table containing all x/y data, uncertainty limits, category labels, annotations, and provenance. Plot only from these tables for the release. This allows reviewers to inspect figures without rerunning slow analyses.

### 7.8 Pin the exact environment

The manifest records package versions, but a release should include a lock file or container image digest and a deterministic command. Random seeds, BLAS/solver details where relevant, and rendering backend should be included.

---

## 8. Required numerical and artifact reruns

These are the minimum reruns I would require before submission.

### Rerun 1 — clean production build

**Procedure:** clean checkout; pinned environment; strict build; regenerate bundle, all figures, captions, source data, and manifest.  
**Pass:** no dirty tree; all commits/hashes aligned; no authored output drift; deterministic rerun within documented tolerance.

### Rerun 2 — classifier semantic audit

**Procedure:** rerun every N-tube OFAT and crossed case using current classifier.  
**Pass:** lateral 0.1 is not single-channel; all state invariants hold; state counts are reported; no stale verdict text.

### Rerun 3 — first passage versus persistent concentration

**Procedure:** compute first crossing, total time above threshold, crossing count, persistent onset, and final class for every configuration.  
**Pass:** nonpersistent pressure-control/high-lateral runs are not called collapsed; Figure 5 distinguishes transient and persistent events.

### Rerun 4 — temporal and spatial event sensitivity

**Procedure:** vary internal timestep, output timestep, N, and at least one higher-order/adaptive integrator for representative cases; interpolate events on a common physical-time grid.  
**Pass for current limited claim:** first-passage and persistent-onset times stabilize under stated tolerances; trajectory errors are reported.  
**Alternative:** omit any convergence claim and retain only endpoint model capacity.

### Rerun 5 — classifier-threshold sensitivity

**Procedure:** vary top-one threshold, `N_eff` threshold, and persistence duration over prespecified ranges.  
**Pass:** qualitative endpoint conclusion is stable or fragility is prominently disclosed.

### Rerun 6 — Result 2 block-length sensitivity

**Procedure:** repeat fixed-loss block resampling at 4, 8, 16, and 24 seconds; report distributions for Φ−constant and Φ−cubic.  
**Pass:** wording reflects actual sensitivity; no nominal coverage claim.

### Rerun 7 — Result 2 loss-series diagnostics

**Procedure:** plot fixed loss differences and assess phase/nonstationarity; optionally use phase-stratified or stationary-bootstrap sensitivity.  
**Pass:** method assumptions and limitations are explicit; conclusion remains descriptive.

### Rerun 8 — RSM single-contract build

**Procedure:** make achieved predictors mandatory/default; regenerate curve, iid band, wild intervals, deletion, Q², and all manuscript numbers from one result object.  
**Pass:** no stale values in §7, captions, or figures.

### Rerun 9 — Figure 1 closure-sweep source data

**Procedure:** export all 25 cells, peak classification, prominence, and pressure sweep.  
**Pass:** plotted annotations are generated; full-grid and successful-cell summaries are clearly separated.

### Rerun 10 — complete figure source-data build

**Procedure:** export all six figures' data and metadata.  
**Pass:** independent plot-only script reproduces all figures without invoking scientific solvers.

---

## 9. Suggested replacement wording

### 9.1 Foster panel

**Replace:**

> “A machine-only model reconstructs a mid-shot flow minimum on the digitized source trace.”

**With:**

> “A numerical reproduction of the published Foster machine/infiltration model curve exhibits a dip-and-recovery without evolving bed resistance. This is a model-capacity example, not a fit to measured data.”

### 9.2 Result 2 fixed-loss resampling

**Replace the inferential portion with:**

> “To assess sensitivity to local serial dependence, we resampled contiguous 8 s blocks of the already-computed squared-loss-difference sequence. This conditional procedure does not refit either curve and assumes that local dependence in the observed sequence is representative. Its central 95% resampling range remains below zero for Φ(t) minus the best constant, while the Φ(t)-minus-cubic range spans zero. Together with the raw RMSE separation across three windows, this supports a descriptive need for temporal flexibility among the tested reconstructions, but it is not a coverage-calibrated bootstrap of the full fitting procedure and does not identify a mechanism.”

### 9.3 Result 3 event

**Replace:**

> “collapse time”

**With:**

> “first-passage time at which one tube first exceeds 50% of the total flow”

until a persistent event is implemented.

After implementation, use:

> “Persistent-concentration onset was defined prospectively as the first time at which top-one share exceeded 0.5 and `N_eff≤2` for at least [duration] s. First-passage and persistent-onset times are reported separately because some trajectories cross the threshold transiently and later redistribute.”

### 9.4 Numerical invariant audit

**Replace:**

> “full-trajectory conservation audit”

**With:**

> “full-trajectory numerical-invariant audit of normalized share sums, non-negativity, and the imposed control-law flow condition; this is not a physical solute, energy, pressure-work, lateral-flux, or age balance.”

### 9.5 Result 3 floor claim

**Use:**

> “The final state classification was unchanged over the tested conductance-floor range in the specified finite-time configuration, although the closed-form conductance gain scales with the imposed floor.”

### 9.6 Seed statement

**Use:**

> “Across 16 tested finite-network realizations, the endpoint class was unchanged under the prespecified classifier, while first-passage times ranged from approximately 1.4 to 3.5 s and several realizations finished near the class boundary.”

### 9.7 Central conclusion

A defensible final conclusion is:

> “Within two primary empirical campaigns and the implemented model set, whole-cup and single-outlet measurements constrain model compatibility but do not uniquely identify a physical mechanism. A conditional RSM vertex, a small static-heterogeneity capacity effect, and lower in-window error from time-varying curves are all compatible with multiple explanations. Within-campaign pressure holdouts support calibration stability rather than physical validation, and an exploratory N-tube construction demonstrates a possible numerical concentration mode only under specified near-choke, fixed-flow, low-lateral assumptions. Discrimination therefore requires additional first-drip, bed-state, pressure-step, spatial, or pathway-resolved measurements.”

---

## 10. Minor and editorial comments

1. Change the manuscript header from `fig{1..5}` to “Figures 1–5 and Supplementary Figure S1/6.”
2. Remove “Two rounds of detailed review adopted” from the paper.
3. Remove “reviewers please read…” from the submission manuscript; retain it in repository review materials.
4. Remove ROADMAP references from title notes and Results.
5. Remove parenthetical review IDs such as MAJ-02/B3-21.
6. Replace repository function names with method names; place function mapping in reproducibility supplement.
7. Define every symbol at first use, including κ, Φ, `N_eff`, λ, and conductance floor.
8. Use one notation for grind dial versus model grind coordinate and emphasize non-portability.
9. Define extraction yield before first use and give its units.
10. State whether error bars in Figure 1 are SD, SE, or confidence intervals directly in the panel label.
11. Ensure the RSM outcome is described as cup TDS mass or TDS-derived EY consistently; Figure 1 combines both and needs a transparent conversion description.
12. Use “grinder dial” rather than “grind” when referring to Schmieder's non-monotone particle-size axis.
13. Avoid “real” as a synonym for “numerically present”; use “present in the numerical sweep.”
14. Replace all-caps emphasis such as `MEASURED`, `CONTINGENT`, and `NOT` with typographic hierarchy suitable for a paper.
15. Use standard mathematical typography for `N_eff` and Φ(t) in captions.
16. State the number of bootstrap replicates in the RSM caption/table.
17. State random seeds or RNG policy in Methods.
18. Define the exact pressure set in the cross-pressure analysis.
19. State whether RMSE weights each timestamp equally and whether the sample spacing is uniform.
20. Explain decimation before Durbin–Watson and whether anti-alias filtering was used.
21. Report measurement units consistently as g s⁻¹ rather than mixed `g/s` and `g s−1` styles.
22. Avoid “ties” in machine-generated prose; use “difference not resolved by this conditional range.”
23. Replace “ZERO-param” everywhere.
24. Distinguish fitted parameters from fixed hyperparameters and numerical regularization.
25. Explain the physical or computational meaning of the conductance floor.
26. State the simulation horizon in Figure 5 caption.
27. State the exact start-state distribution and its parameterization.
28. State whether the seed sweep changes only network heterogeneity or other inputs.
29. Report the final state for each seed in supplementary source data.
30. Define the lateral homogenization proxy equation and its units/dimensionlessness.
31. Explain why lateral 0.1, 0.2, and 0.3 were selected.
32. Define flow-control and pressure-control boundary conditions mathematically.
33. Explain how total flow is normalized under flow control.
34. Do not describe normalized share-sum unity as an empirical conservation result.
35. Distinguish first threshold crossing from peak-share time.
36. Use “conditional on donor trajectories” consistently for cross-pressure Φ and RC-3b.
37. State that the 9-bar TDS trajectory remains fixed in LOPO.
38. Add a table mapping empirical observations, reconstructions, published model curves, and simulations.
39. In Figure 3d, call the measured line “observed 9-bar flow” and the other “transferred isolated swelling branch.”
40. In Figure 4, state whether the observed trace has replicate uncertainty.
41. Use a complete bibliography rather than repository dataset keys in prose.
42. Check the final publication year and DOI for Waszkiewicz and avoid citing the preprint year as the article year.
43. Add data-license and derivative-data provenance in Data Availability.
44. Add software license and exact release DOI/tag in Code Availability.
45. State whether the source CSV's 36 design-summary rows are excluded by schema before all analyses.
46. Add fail-fast tests for missing/extra experimental rows and unexpected units.
47. Add an explicit statement that the evidence matrix is not a meta-analysis.
48. Avoid describing the fixed 5×5 closure rectangle as a probability distribution over plausible closures.
49. Explain how “prominence” is defined mathematically.
50. Report the pressure-specific prominence values in supplementary data.
51. Explain why 9 bar is a particularly weak interior maximum in the model.
52. Use “same-campaign” consistently rather than alternating with “internal.”
53. Separate independent validation, within-campaign holdout, post-fit reconstruction, and model capacity in a formal legend.
54. Add model and data uncertainty separately where both exist.
55. Avoid “best” without specifying metric and window.
56. State that the cubic degree was chosen as a flexibility benchmark, not selected by cross-validation.
57. Add a sensitivity to a lower-complexity temporal null, such as linear/quadratic or spline with effective degrees of freedom, if space permits.
58. Explain whether the cubic extrapolates outside the scoring window; do not show extrapolation as prediction.
59. Put Figure 6 in the main paper if Result 2 is a headline; structured residuals are not merely supplementary detail.
60. Remove the status/to-do section entirely from the submitted manuscript.

---

## 11. Submission-readiness checklist

### Scientific claims

- [ ] All headline statements use the maximum defensible scope in the reviewer brief.
- [ ] Foster panel is correctly described as a published model-curve reproduction.
- [ ] Result 2 block output is labeled conditional fixed-loss resampling, not a full bootstrap.
- [ ] Block-length sensitivity is reported or inferential language is removed.
- [ ] Result 3 first passage and persistent endpoint are distinguished.
- [ ] Current classifier is used in every artifact.
- [ ] Numerical-invariant audit is not called physical conservation.
- [ ] “0 parameters” is removed.
- [ ] “Measured N_eff” is removed.
- [ ] All RSM intervals remain explicitly conditional.

### Reproducibility

- [ ] Clean tagged release.
- [ ] Bundle source commit equals release commit.
- [ ] `git_dirty=false`.
- [ ] Strict verification passes.
- [ ] All scientific data/code/manuscript/figure artifacts are hashed.
- [ ] All figures consume frozen source data or are cross-verified against it.
- [ ] No hard-coded manuscript-facing annotation remains.
- [ ] Semantic classifier and provenance tests pass.
- [ ] Exact environment is pinned.
- [ ] Complete per-panel source data are included.

### Manuscript form

- [ ] Conventional Methods with equations and numerical details.
- [ ] Complete references and related work.
- [ ] Data and code availability statements.
- [ ] Author contributions, conflicts, funding, and acknowledgments.
- [ ] Internal review IDs and project-management language removed.
- [ ] Five main figures plus supplementary figure enumerated consistently.
- [ ] Captions stand alone and match plotted content.
- [ ] Figures are rendered in required vector formats and checked at final size.

---

## 12. Supporting primary references

The following sources are especially relevant to the review and should be represented accurately in the manuscript's final bibliography.

1. **Schmieder, B. K. L., Pannusch, V. B., Vannieuwenhuyse, L., Briesen, H., & Minceva, M.** “Influence of Flow Rate, Particle Size, and Temperature on Espresso Extraction Kinetics.” *Foods* 12, 2871 (2023). https://doi.org/10.3390/foods12152871  
   Relevance: 15-setting face-centered design; three repetitions and six at the centre; ten consecutive fractions; cup masses calculated from measured first fractions plus integrated fitted kinetics; achieved flow and temperature used in response-surface analysis; source cautions against strong quantitative interpretation.

2. **Cameron, M. I., et al.** “Systematically Improving Espresso: Insights from Mathematical Modeling and Experiment.” *Matter* 2 (2020). https://doi.org/10.1016/j.matt.2019.12.019  
   Relevance: fine-grind extraction response and homogeneous-model context; calibration/provenance source rather than independent validation of the present static-heterogeneity closure.

3. **Foster, J. A., et al.** “Dynamics of Liquid Infiltration into an Espresso Bed Using Time-Resolved X-Ray Tomography.” *Physics of Fluids* 37, 013383 (2025).  
   Relevance: machine/infiltration model capacity and the distinction between a reproduced model curve and measured data.

4. **Waszkiewicz, R., et al.** “Under Pressure: Poroelastic Regulation of Flow in Espresso Brewing.” *Physics of Fluids* 38, 063113 (2026). https://doi.org/10.1063/5.0319611  
   Relevance: equilibrium pressure-flow behavior, temporal flow/TDS analysis, poroelastic interpretation, and same-campaign calibration limitations.

5. **Lee, W. T., Smith, A., & Arshad, A.** “Uneven Extraction in Coffee Brewing.” *Physics of Fluids* 35, 054110 (2023). https://doi.org/10.1063/5.0138998  
   Relevance: low-dimensional pathway model that can generate decreasing extraction at fine grind; useful competitor but not directly matched to the constant-pressure temporal flow observable.

6. **Mo, C., Navarini, L., Suggi Liverani, F., & Ellero, M.** “Modeling Swelling Effects during Coffee Extraction with Smoothed Particle Hydrodynamics.” *Physics of Fluids* 34, 043104 (2022). https://doi.org/10.1063/5.0086897  
   Relevance: swelling affects coupled intra- and inter-grain transport; supports limiting the manuscript's sign conclusion to an isolated transferred resistance-only branch.

7. **Smrke, S., et al.** “The Role of Fines in Espresso Extraction Dynamics.” *Scientific Reports* 14 (2024). https://doi.org/10.1038/s41598-024-55831-x  
   Relevance: fines fraction affects permeability and flow in empirical espresso measurements; reinforces the need not to generalize an isolated fixed-pressure branch to coupled real-puck dynamics.

8. **Künsch, H. R.** “The Jackknife and the Bootstrap for General Stationary Observations.” *Annals of Statistics* 17, 1217–1241 (1989). https://doi.org/10.1214/aos/1176347265  
   Relevance: block-resampling methods are developed for dependent stationary sequences; the manuscript should state the working dependence/stationarity assumptions and block-length sensitivity.

9. **Mammen, E.** “Bootstrap and Wild Bootstrap for High Dimensional Linear Models.” *Annals of Statistics* 21, 255–285 (1993). https://doi.org/10.1214/aos/1176349025  
   Relevance: rationale for wild-bootstrap sensitivity under heteroskedastic regression; does not remove post-selection or first-stage endpoint uncertainty.

---

## 13. Final recommendation

**Major revision.**

The central limits-of-discrimination argument is scientifically worthwhile and substantially better scoped than in earlier drafts. Result 1's conditional RSM analysis is now credible at its stated level, the corrected Jensen calculation is coherent, the null-first temporal ladder is conceptually strong, the pressure holdout is properly described as within-campaign calibration stability, and the manuscript is admirably explicit that Result 3 is exploratory.

The paper should not yet be submitted because the current release is not artifact-coherent and the N-tube event definition creates a new substantive inconsistency. The frozen bundle is from an older dirty commit and preserves pre-correction classifier behavior; “collapse time” is a transient first-passage statistic that also occurs in runs ending distributed; generated verdicts and manuscript tables retain stale claims; and the paper still lacks conventional Methods and a clean release package.

After a clean rebuild, persistent-event correction, Result 2 wording calibration, and journal-format conversion, the manuscript could make a useful contribution centered on **what integrated espresso measurements can and cannot discriminate**, rather than on identifying a particular physical mechanism.
