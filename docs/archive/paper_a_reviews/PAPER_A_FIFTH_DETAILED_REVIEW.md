> **ARCHIVED — already actioned, and partly superseded.** This is the fifth detailed review
> (target `b4de0d9`). Its findings were actioned at the time and are logged in
> `docs/REVIEW_BACKLOG.md` under A-02/A-05/A-07/A-08/A-09/A-14/A-16/A-17/A-23/A-28/A-29/A-32/A-33
> and MC14. Spot-checked on re-upload (2026-07-28): the P0 wordings it targets —
> "transfers reasonably", "transfers across grind", "domain-independent profile width" — appear
> nowhere in the manuscript, the supplement, the figures or the code.
>
> **Two of its positions have since been overturned by later evidence, so do not read it as
> current:** (1) it treats the collection endpoint as a **40 mL volume proxy**; the round-6
> solver-contract audit and round-7 P0-2 established that the stopping rule is a matched
> **mass**, and the endpoints are 38/40/42 **g**. (2) its transfer numbers (8.23 % vs 8.59 %,
> worse on 50 of 108) are for the matched on-grid subset; round-7 P0-3 moved the headline to the
> complete 44-record corpus (8.44 % vs 8.83 %, worse on 62 of 132).
>
> Kept for the record of what was found and when.

# Detailed review of the updated `PAPER_A_DRAFT.md`

## Reviewer-brief-aware assessment of the manuscript, figures, code, data, and reproducibility package

**Repository:** [`trbrewer/puckworks`](https://github.com/trbrewer/puckworks)  
**Reviewed branch and commit:** `main` at `b4de0d971555dcfcf13b24cab5da6e5b8eab9cf4`  
**Primary manuscript:** `docs/PAPER_A_DRAFT.md`  
**Reviewer brief read before review:** `docs/REVIEWER_BRIEF_PAPER_A.md`  
**Review date:** 2026-07-13  
**Manuscript SHA-256:** `cb8260727e47fda58395429559822d899c6b91319f7fb2667d8542c8c1eaee2`  
**Reviewer-brief SHA-256:** `11b7a34f8621007fd53ee25fa9a554a1c7a978f18319cf4a93464fd83f66de54`

## Recommendation

**Major revision before journal submission.**

The manuscript's central result is credible and potentially publishable: for the tested single-grind, whole-cup observation operator, the profiled inventory–rate objective has an interior numerical optimum but a broad, right-censored near-optimal region, whereas retaining temporal resolution localizes the rate objective more strongly. The revision also makes an important conceptual distinction among parameter localization, endpoint accuracy, cross-design prediction, and incremental skill over a null model.

The present repository state is nevertheless not submission-ready. The principal blocker is not merely editorial. The current manuscript, result bundle, manifest, rendered figures, plotting code, and build contract are not one coherent release. Two committed figures visibly retain interpretations that the current code and reviewer brief say were withdrawn; the current manifest certifies earlier commits rather than the reviewed head; the frozen result text says condition-wise envelopes are still owed even though the current Figure 4 displays them; and the advertised all-analysis build omits a robustness calculation used in the manuscript. In addition, a newly identified observation-operator defect allows a negative five-second collected-mass bin in one declared Waszkiewicz alignment case. That case must be rebuilt from a physically admissible monotone mass or nonnegative-flow reconstruction before the external sensitivity panel is relied upon.

The transfer result also still needs firmer discipline. The model's pooled C/F MAPE is approximately 8.23%, versus approximately 8.59% for the O-trained level-only constant. That is only 0.36 percentage points, and the mechanism is worse on 50 of 108 held-out points. The manuscript handles this appropriately in several places, but its standing conclusion and some code-level verdicts still say that the refit “transfers across grind.” The evidence supports modest absolute endpoint error with little incremental skill beyond a transferred level; it does not support mechanistic transfer.

---

## 1. Scope and review method

I read `docs/REVIEWER_BRIEF_PAPER_A.md` before assessing the manuscript. I treated it as requested: a disclosure register, not a prohibition on discussing known limits. For each disclosed item I asked whether the present manuscript scopes it correctly, whether the limitation remains compatible with the headline claim, and whether the repository artifacts actually implement the correction claimed in the brief.

The review covered:

- the complete current `docs/PAPER_A_DRAFT.md`;
- all eight committed Paper A figures, including their titles, panel contents, legends, axes, and relationship to the prose;
- `puckworks/figures_paper_a.py` and the Paper A build wrapper;
- the principal slow-analysis modules for the Angeloni transfer, identifiability controls, and Waszkiewicz external panel;
- the frozen `docs/figures/paper_a/results.json` and `docs/reproducibility/paper_a_manifest.json` contracts;
- the available tidy source-data exports and selected committed source tables;
- the venue-conversion draft and standalone figure captions where they reveal divergence between manuscript sources;
- targeted, data-only recomputations that do not require rerunning the slow PDE solver; and
- supporting primary literature on the source experiments, practical identifiability/profile analysis, profile-wise prediction, and cross-validation dependence.

This is not a clean-room rerun of every slow PDE calculation in a newly provisioned and pinned environment. Findings described as **definite** are established by manuscript/code/artifact inspection or data-only recomputation. Findings described as **robustness requests** require the authors' full numerical rerun.

---

## 2. Executive assessment

### 2.1 What has improved materially

1. **The scientific scope is much more honest.** The abstract now distinguishes identifiability, absolute endpoint accuracy, baseline-relative skill, and transferability. It also reports the level-only comparator and the 50/108 pointwise losses.
2. **The profile result is described more carefully.** The draft distinguishes an interior optimum from an open/right-censored 10%-tolerance set and correctly states that the objective tolerance is not a confidence region.
3. **The inverse-Hessian quantity is no longer called a statistical correlation.** It is presented as a local-curvature coupling on the SSE surface.
4. **Evidence categories are mostly disciplined.** The Angeloni C/F assessment is called a within-campaign cross-grind holdout; the joint fit is called in-sample compatibility; Table 7 is called a same-campaign orthogonal measurement; and Waszkiewicz is called target-profiled external shape localization.
5. **Figure 4 is substantially stronger.** It now includes the level-only baseline and finite-grid profile-set ranges instead of showing absolute errors alone.
6. **The source-study description is improved.** The Schmieder campaign is described as 15 settings with ten collected fractions, repeated extraction, and a derived six-window subset; the manuscript acknowledges that the empirical sampled aggregate is not a true whole cup.
7. **The LOCO intervals are labelled descriptive.** The text explicitly says they do not repeat the fitting procedure or correct dependence among overlapping folds.
8. **The external panel reports its high error.** A shallow objective minimum around 27% MAPE is not presented as a validated physical rate estimate.

### 2.2 What still blocks submission

1. **No current, clean, internally coherent release exists.** The reviewed head, manifest commit, and bundle source commit differ.
2. **Figures 7 and 8 are stale relative to current code and contradict the reviewer brief's “already corrected” list.**
3. **The Waszkiewicz bin-mass operator can create a negative observed collection mass under a declared alignment case.**
4. **The primary named-solute convention is violated by the 22.6% Result 1 headline, which includes the aggregate-solids proxy.**
5. **Mechanistic transfer is still overstated in the standing conclusion and selected code-level verdicts.**
6. **The 10%-near-optimal “manifold” remains a finite 18-point objective-tolerance set with an arbitrary threshold and no grid-converged prediction-set analysis.**
7. **The Table 7 result is described as a narrow-band collapse although its ±10% inventory sensitivity maps to approximately 0.60–1.76 in rate and is not an uncertainty interval.**
8. **The “nested reduced-model ladder” is not a nested statistical comparison and is scored in-sample without complexity correction.**
9. **The endpoint and flow-map sensitivity analyses do not fully test the headline transfer estimand.**
10. **Figure source data and build verification remain incomplete.**

---

## 3. Audit against `REVIEWER_BRIEF_PAPER_A.md`

The table below distinguishes an adequately handled disclosure from a current contradiction or release regression.

| Brief item | Current assessment | Review finding / required response |
|---|---|---|
| Identifiability maximum claim: interior optimum, broad right-censored 10% set, not CI | **Mostly adequate** | The abstract and Figure 2 discussion are substantially correct. Remove remaining phrases that imply the numerical optimum is absent or non-interior, and replace the binary “identified/not identified” language in the identifiability-ratio definition with “more/less localized over the stated domain.” |
| Transfer maximum claim: modest absolute error but little skill over level-only constant | **Partly adequate** | §5 and much of the abstract comply. The standing position still says the refit “transfers across grind,” and a code docstring still says “transfers REASONABLY.” Harmonize every user-facing and machine-facing verdict with the brief. |
| Joint fit: in-sample compatibility only | **Mostly adequate** | The main text states this correctly. Calling the comparator sequence a “nested reduced-model ladder” and concluding that mechanism explains “essentially nothing” overstates an in-sample, unequal-flexibility comparison. |
| Observation operator: fractions localize more than aggregate under tested operators, in-sample | **Adequate with caveats** | The evidence-tier wording is generally sound. The same-model simulation remains an inverse-crime information demonstration, not empirical validation; keep it explicitly separate from the external panel. |
| Waszkiewicz: shallow, high-error, target-profiled shape localization; cup flat algebraically | **Scope adequate; implementation requires correction** | The prose is appropriately cautious, but the observed-bin construction admits a negative bin under the 4 s alignment. Rebuild the operator before retaining the full alignment-sensitivity claim. |
| Solute-specific uncertainty weighting unavailable | **Disclosure adequate but quantitatively important** | This does not erase the broad profile finding, but it prevents uncertainty-calibrated parameter regions and may alter relative weighting across conditions/solutes. Keep all threshold sets descriptive and run all available RSD/heteroscedastic sensitivity analyses. |
| Continuous/grid-converged prediction envelopes deferred | **Brief is partly stale** | Current Figure 4 and §5 now show condition-wise ranges from a finite 18-point set. What remains deferred is continuous/grid-converged, threshold-sensitive profile-prediction propagation. Correct the brief, abstract, bundle verdict, captions, and backlog to distinguish these two states. |
| Endpoint × density transfer estimand deferred | **Disclosure adequate; headline robustness still untested** | The 38/40/42 mL calculation is for blind O discrepancy, not O-refit→C/F transfer relative to the baseline. Do not describe it as robustness of the transfer result until the full workflow is rerun. |
| Hessian sensitivity table deferred | **Acceptable only because the profile is primary** | Keep the Hessian clearly secondary, local, and scaling/discretization-dependent. Do not use condition number magnitude as a universal classification threshold. |
| Discrepancy/off-grid controls not all plotted | **Disclosure inadequate for a central design argument** | The controls are important enough to the positive-control interpretation that at least one supplementary figure and full source table should be supplied. |
| Fig. 3/4 source data and profile-envelope export deferred | **Submission blocker** | Figure 4 now makes a central claim but its per-condition points, baseline predictions, and profile-set ranges are not exported in the current tidy-data function. Figure 3 fold data are likewise absent. |
| Vector figures done as code, production render owed | **Not complete as a release** | The current raster images include stale Figure 7/8 titles. The vector-capable code is useful, but “done” should mean a clean rerender with hashes and a visual check. |
| Journal conversion in progress | **Still required** | The working draft contains repository notes, review IDs, code function names, a live gap ledger, and an internal change log. The JFE draft also retains many of these. |
| Clean tagged release deferred | **Submission blocker, not merely administrative** | The manifest currently certifies old commits and cannot certify the reviewed manuscript. No acceptance decision should rely on the present bundle until release coherence is established. |
| No measured per-condition flow | **Adequately disclosed, but inference must remain conditional** | The flow-map-form uncertainty is larger in kind than the ±20% magnitude sweep. Avoid wording that generalizes from a representative caffeine/Arabica magnitude test to all model transfer behavior. |
| “Fig. 8 level-rescale title withdrawn” | **Contradicted by current committed image** | The current code contains the corrected title, but the current PNG still says a pure level rescale cannot remove the offsets. Rerender and remove the obsolete explanatory docstring. |
| Figure count synchronized at eight | **Partly corrected** | The manuscript says eight, but `figures_paper_a.py` and the build wrapper still refer to “the six figures” in docstrings/help text. |
| “Matched 40 g” replaced by 40 mL proxy | **Not fully corrected** | §5 still says “matched 40 g cups.” Use “40 mL matched-volume proxy for the nominal 40 g cup” consistently. |
| Interior optimum vs right-censored set harmonized | **Mostly corrected** | §4 still calls the fitted rate “not a converged interior estimate.” The optimum is interior; the near-optimal set is weakly localized and right-censored. Say exactly that. |

---

## 4. Prioritized required-action matrix

### Priority definitions

- **P0 — release/submission blocker:** must be corrected before the work is sent to a journal or relied upon as a reproducible package.
- **P1 — scientific interpretation blocker:** required for defensible claims, figures, or uncertainty statements.
- **P2 — important strengthening/editorial action:** not necessarily fatal to the central result, but needed for a polished journal submission.

| ID | Priority | Required action | Acceptance criterion |
|---|---:|---|---|
| A-01 | P0 | Rebuild Paper A from the reviewed commit or a later clean commit. | `git status --porcelain` empty; `HEAD == results.source_commit == manifest.source_commit == manifest.bundle_source_commit`; strict verification succeeds; release command exits nonzero on any mismatch. |
| A-02 | P0 | Rerender all eight figures from the newly computed bundle. | Figure 7 no longer says “trajectory-shape”; Figure 8 no longer says a level rescale cannot remove group offsets; all raster and vector hashes are recorded. |
| A-03 | P0 | Fix the Waszkiewicz observed-bin mass operator. | Every declared time alignment produces nonnegative bin masses; cumulative reconstructed mass is monotone; integrated mass agrees with the selected flow/mass trace within a declared tolerance; tests fail on a negative bin. |
| A-04 | P0 | Make one release command recompute, render, export, and strictly verify. | A single documented command starts from/validates a clean tree, recomputes all manuscript-facing results, renders eight figures in PNG+SVG/PDF, exports source data, writes hashes, and performs strict freshness checks. |
| A-05 | P0 | Include every manuscript-cited analysis in `compute_all()`. | The result bundle contains `flow_map_sensitivity_transfer` and every other cited robustness/control result; a test maps every manuscript number to a bundle field. |
| A-06 | P0 | Replace hard-coded expected-number verification with artifact-derived checks. | Verification compares manuscript tables/caption metadata or generated claim files against recomputed bundle values, rather than checking bundle fields against separately hard-coded rounded constants. |
| A-07 | P0 | Correct the primary Result 1 observable summary. | The primary blind MAPE is reported for named solutes only (approximately 26.3% from the current exported residuals); the approximately 22.6% value is clearly labelled “including TDS proxy” and is not the headline. |
| A-08 | P0 | Remove all remaining mechanistic-transfer wording. | No manuscript, caption, code docstring, verdict, README, or result bundle says the model “transfers reasonably” or simply “transfers across grind.” The maximum claim matches the reviewer brief. |
| A-09 | P0 | Make the manuscript and frozen bundle agree about prediction envelopes. | The abstract, §5, captions, reviewer brief, result verdict, and figure all state that finite-grid condition-wise ranges are present, while continuous/grid-converged profile-prediction ranges remain deferred. |
| A-10 | P0 | Export complete source data for every data-bearing figure. | Tidy tables reproduce all plotted points, curves, baseline predictions, profile-set ranges, LOCO residuals, ladder values, external sensitivity curves, and simulation bands without rerunning the solver. |
| A-11 | P0 | Choose one canonical manuscript source. | Either `PAPER_A_DRAFT.md` generates the JFE manuscript or vice versa; CI fails when numerical claims, captions, figure count, or references diverge. |
| A-12 | P0 | Hash all manuscript-facing artifacts and transitive inputs. | Manifest includes manuscript(s), captions, result bundle, each figure format, each source-data table, all direct and transitive analysis/model modules, environment/lock file, and source datasets. |
| A-13 | P1 | Rebuild the Waszkiewicz alignment sensitivity after A-03. | Report best rate, minimum MAPE, and range ratio for each physically admissible alignment; document whether conclusions change. |
| A-14 | P1 | Replace “entire manifold” language with finite tolerance-set language. | Text and figure labels say “discrete 10%-relative-MAPE tolerance set on an 18-point rate grid,” unless a continuous profile has actually been computed. |
| A-15 | P1 | Demonstrate grid/domain/threshold convergence of transfer prediction ranges. | Repeat with denser rates and several thresholds or an objective increment justified by a noise model; show convergence of condition-wise ranges and C/F aggregate scores. |
| A-16 | P1 | Reframe the Table 7 intersection. | Describe it as a conditional same-campaign intersection; label ±10% as a sensitivity assumption, not an uncertainty interval; report approximately 0.60–1.76 rather than calling it a narrow collapse. |
| A-17 | P1 | Rename and reinterpret the reduced-model ladder. | Use “in-sample comparator ladder” or similar; state parameter counts and non-nested structure; remove “mechanism explains essentially nothing” unless supported by out-of-sample/penalized comparison. |
| A-18 | P1 | Rerun the actual endpoint×density transfer estimand. | At every endpoint/density scenario, refit O, transfer to C/F, recompute level-only baseline, profile-set ranges, and paired skill. |
| A-19 | P1 | Expand the flow-map magnitude sensitivity beyond one representative fit. | Run all six variety×named-solute groups or label the current result explicitly as Arabica-caffeine only and avoid global robustness wording. |
| A-20 | P1 | Quantify paired uncertainty in mechanism-versus-constant skill. | Report clustered paired differences by condition/grind/group, with a resampling scheme that respects the design; emphasize practical magnitude, not only a pooled mean. |
| A-21 | P1 | Preserve LOCO intervals as descriptive or repeat the fit within resampling. | No “95% confidence interval” language unless the fitting and dependence structure are resampled appropriately; otherwise call them descriptive central ranges. |
| A-22 | P1 | Add fold-level parameter diagnostics to LOCO. | Export and plot selected rates, inventory levels, boundary hits, and fold errors by variety/solute/condition. |
| A-23 | P1 | Replace Figure 7 missing matched values with explicit NA. | No unavailable 5-CQA/TDS matched values are drawn as zero-height bars; use missing glyphs, hatching, or omit bars and label “not available.” |
| A-24 | P1 | Replace or demote Figure 8. | Primary option: plot residuals after fitting the group level and assess remaining T/p structure. Secondary option: retain as supplementary pre-fit discrepancy only, with neutral title and no irreducibility inference. |
| A-25 | P1 | Align Figure 6 central curves and simulation bands. | The line through the same-model simulation is the 20-seed mean if the band is mean±SD, or it is explicitly labelled as seed 0 with the mean shown separately. |
| A-26 | P1 | Plot the key discrepancy/off-grid controls. | Add a supplement showing off-grid recovery, heteroscedastic/correlated noise, and model-discrepancy dose response, with full source tables. |
| A-27 | P1 | Separate named-solute and aggregate-proxy reporting everywhere. | No pooled “overall” metric combines caffeine/trigonelline/5-CQA with source-specific TDS/total solids unless explicitly presented as a secondary sensitivity. |
| A-28 | P1 | Correct the identifiability-ratio interpretation. | Replace “ratio ≫1 means the rate is identified” with “the objective is more strongly localized over this domain”; specify edge and minimum definitions. |
| A-29 | P1 | Harmonize interior-optimum wording. | State: “The numerical optimum is interior, but the near-optimal upper extent is not bounded within the tested domain.” |
| A-30 | P1 | Make the Hessian claim sensitivity-aware. | Supply the deferred finite-difference/grid/scaling table or reduce prominence; never treat κ≈1930 as a calibrated inferential threshold. |
| A-31 | P1 | Add uncertainty/weighting sensitivity using all available source information. | Report unweighted, available-RSD-weighted, and reasonable heteroscedastic sensitivity results; do not call any tolerance set a confidence region absent a likelihood. |
| A-32 | P1 | Correct Figure 4 range semantics. | Legend/caption says “range across declared objective-tolerance set,” not “prediction interval,” “confidence band,” or generic “uncertainty.” |
| A-33 | P1 | Clarify the pressure-to-flow map's epistemic status in every transfer result. | Tables and captions state that per-condition flows were inferred, not measured; distinguish map-form uncertainty from uniform-scale sensitivity. |
| A-34 | P2 | Replace repository-facing prose with conventional Methods. | Equations, parameter units, parameter domains, objective functions, sample sizes, weighting, endpoint operator, solvers, tolerances, and uncertainty procedures appear in the manuscript without function names as substitutes. |
| A-35 | P2 | Remove internal review/roadmap language. | No A2/A3/A4 IDs, “owed,” “review,” backlog, handoff, or repository-note language remains in the submission manuscript. |
| A-36 | P2 | Fix cross-references and section numbering. | Remove the nonexistent “§10.14” reference; automated link/reference checks pass. |
| A-37 | P2 | Standardize endpoint wording. | Every occurrence uses “40 mL matched-volume proxy for the nominal 40 g cup” or an approved shorter equivalent. |
| A-38 | P2 | Use self-contained, neutral figure titles. | Titles state design/quantity rather than conclusions; captions carry interpretation and evidence tier. |
| A-39 | P2 | Improve Figure 2 readability. | Increase legend/color contrast, identify normalized SSE scale and tolerance threshold, show censoring clearly, and either plot the MAPE profile or move MAPE statistics to caption/table. |
| A-40 | P2 | Improve Figure 3 communication. | Reduce title density, distinguish analytes without relying on concentration-scale separation, and provide a fold-level table/parameter panel in the supplement. |
| A-41 | P2 | Improve Figure 5 terminology and grammar. | Replace “in only 0/6” with “in none of six”; mark boundary fits clearly; label the comparator sequence non-nested and in-sample. |
| A-42 | P2 | State the limits of pooled correlations. | Figure 7 correlations use n=9 and are descriptive; add uncertainty/sensitivity or avoid categorical color coding around arbitrary thresholds. |
| A-43 | P2 | Complete references and declarations. | Full bibliographic references with DOI, data/code availability, funding, competing interests, author contributions, and any AI declaration are complete and consistent. |
| A-44 | P2 | Add a concise limitations table. | One journal-facing table maps each result to data source, fitted quantities, held-out unit, comparator, principal uncertainty, and maximum claim. |
| A-45 | P2 | Archive a frozen release. | Tag, DOI/archive, environment lock, source-data license notes, exact command log, and manifest accompany the accepted manuscript. |

---

## 5. Detailed major comments

### 5.1 Release and artifact coherence

#### Major comment 1 — The current manifest does not certify the reviewed manuscript

The reviewed repository head is `b4de0d971555dcfcf13b24cab5da6e5b8eab9cf4`. The committed manifest instead reports `source_commit = 5b53403...` and `bundle_source_commit = 838f397...`, while still recording zero failures and `verified = true`. It also lacks the freshness fields implemented in the current build code. The manifest therefore demonstrates only that an older bundle matched a list of older hard-coded expectations within wide tolerances. It does not establish that the current manuscript, current code, current figures, and current bundle were produced together.

This is a definite release defect. The reviewer brief lists the clean tagged release as deferred, but for a manuscript whose central contribution is methodological discipline and observable-contract traceability, release coherence is part of the evidence. A journal reviewer should not need to infer which combination of manuscript and artifact is authoritative.

**Required action:** perform A-01, A-04, A-06, and A-12 before submission.

#### Major comment 2 — Figures 7 and 8 are visibly stale

The current committed Figure 7 still uses the title “inventory-matching helps caffeine but HURTS trigonelline ...” and labels panel (b) “trajectory-shape agreement.” The current committed Figure 8 still claims that a pure inventory-level rescale cannot remove the negative offsets. Both statements are explicitly listed as corrected in the reviewer brief, and the current plotting code contains more defensible replacement titles. This proves that the committed images were not rendered from the current plotting source.

The issue is not cosmetic. Figure 8's stale title repeats a logically invalid inference: the model fits a separate target level by variety and solute, so a group-level offset can indeed be removed by that level. The present code's corrected title acknowledges this; the current image does not.

**Required action:** rerender from a fresh bundle, inspect every title, and include image hashes in the manifest. Remove obsolete code docstrings that still explain the invalid conclusion.

#### Major comment 3 — The result bundle and manuscript disagree about the finite profile-set envelopes

The current manuscript and Figure 4 state that condition-wise prediction ranges across the finite 10%-near-optimal rate set are now propagated. The frozen bundle's transfer verdict still says those envelopes “remain owed.” The abstract also says they remain owed. This is a three-way inconsistency among displayed figure, manuscript text, and cached machine-readable verdict.

**Required action:** distinguish precisely between (a) the currently displayed finite-grid deterministic ranges and (b) the still-owed continuous/grid-converged profile-prediction analysis. Regenerate all three surfaces from one result object.

#### Major comment 4 — The build's “single source of truth” is actually a duplicated source of truth

`puckworks/paper_a/build.py` checks bundle values against hard-coded rounded expected numbers and broad tolerances. This is useful as a regression smoke test, but it is not a proof that the manuscript text reflects the bundle. The expected values are a second manually maintained numerical source. A manuscript number can drift while both the bundle and hard-coded expectation remain unchanged, and the build will pass.

A stronger contract would generate a machine-readable claims table from the bundle, insert or validate those values in the manuscript, and verify figure/source-data hashes. At minimum, the build should parse a generated table or front matter rather than compare to duplicate constants.

#### Major comment 5 — `compute_all()` does not compute every cited result

The orchestration function claims to run every slow analysis cited by the manuscript. It does not call `flow_map_sensitivity_transfer`, although §5 relies on its ±20% flow-map result. The reproducibility list also omits several current manuscript-facing routines or controls. This means that “full” recomputation cannot reconstruct the entire paper.

**Required action:** create a complete claim-to-function registry and fail the build when a cited bundle path is absent. Include all analyses used in prose, tables, captions, and supplements.

#### Major comment 6 — The release command is not a release build

The current `full` command recomputes and renders, then runs non-strict verification. The `release` command runs strict verification on an existing bundle but does not recompute or render. There is no single command that recomputes, renders, exports, and then verifies freshness. The build help also still refers to six figures.

**Required action:** implement one end-to-end release target with the acceptance criteria in A-04.

### 5.2 Primary observable and Result 1

#### Major comment 7 — The named-solute convention is contradicted by the 22.6% headline

§3 says the primary headline is the macro-average over caffeine, trigonelline, and 5-CQA, and that source-specific TDS/total-solids proxies are never pooled with named molecules. The table immediately reports 22.6% “including proxy” as the blind overall MAPE and repeatedly uses 22.6% in the narrative.

A data-only recomputation from the current exported residual table gives:

- named-solute blind MAPE: **26.329%**;
- named solutes plus aggregate-solids proxy: **22.658%**.

The lower value is driven partly by relatively smaller TDS-proxy errors and cannot be the primary number under the manuscript's declared convention.

**Required action:** make approximately 26.3% the primary blind named-solute summary; place 22.6% in a separately labelled proxy-inclusive sensitivity. Apply the same convention to endpoint sensitivity and every other aggregate.

#### Major comment 8 — “External, per-condition” overstates the Result 1 evidence label

The Angeloni dataset is independent of the Schmieder/Pannusch calibration lineage, so the blind source-model comparison is legitimately cross-dataset. Once target-specific inventory and rate are refit, however, the analysis is a target-data calibration with a very small two-point internal holdout. The table does distinguish these, but its compact “external” labels could be read as external validation after refitting.

**Required action:** use “cross-dataset blind comparison” for the source-model evaluation and “Angeloni-target recalibration with two off-grid O holdouts” for the refit.

#### Major comment 9 — Endpoint sensitivity is currently interpreted too broadly

The 38/40/42 mL sweep quantifies the blind O-grind discrepancy. It does not repeat the actual O-fit→C/F transfer, level-only baseline comparison, or profile-set propagation. The current text says the “qualitative conclusion” is robust and discusses a large structured transfer residual. That wording risks importing robustness from the blind discrepancy to the headline transfer skill.

**Required action:** either run A-18 or limit the conclusion to the blind O comparison. Do not describe the current sweep as cross-grind-transfer robustness.

#### Major comment 10 — The “large, structured residual not removed by inventory alone” is not established by Figure 8

All 72 blind residuals in the current export are negative. Much of the apparent structure is therefore between group means rather than within-group response to temperature or pressure. After demeaning within each variety×observable group, the pooled correlations are only approximately 0.17 with temperature and 0.07 with pressure. These are descriptive calculations, not inferential tests, but they show why the current pre-level plot cannot support an irreducible operating-condition discrepancy.

A group-specific level can remove each group mean. The scientific question is what pattern remains after that level fit. Figure 8 does not show it.

**Required action:** plot post-level residuals and, ideally, account for repeated conditions and measurement variability. Otherwise move Figure 8 to a supplement as a pre-fit discrepancy visualization only.

### 5.3 Practical identifiability and Table 7

#### Major comment 11 — The central profile result is strong, but terminology still mixes an interior optimum with weak localization

The current caffeine profile export has a minimum near rate 0.659 and a 10%-SSE set from approximately 0.385 to the upper grid value 6.5. Thus, the numerical optimum is interior, while the tolerance set's upper extent is right-censored. Statements that the fitted rate is “not a converged interior estimate” conflate these two facts.

**Preferred wording:** “The numerical optimum is interior, but it is weakly localized: the declared near-optimal set remains open at the tested upper boundary and therefore does not support a stable physical rate estimate.”

#### Major comment 12 — “Practical non-identifiability” should be tied to the descriptive objective, not presented as a likelihood result

The manuscript appropriately says that no likelihood is specified and that the 10% set is not a confidence region. Because the analysis uses an arbitrary relative-objective threshold and a finite parameter domain, the strongest precise phrase is “weak practical localization under the tested objective and domain.” “Practical non-identifiability” is reasonable as a qualitative diagnosis, provided it is always anchored to that operational definition.

Profile-likelihood literature distinguishes an interior minimum with a profile that fails to cross a likelihood-based threshold from an identifiable parameter. Here, however, there is no likelihood-based threshold. Keep the analogy, but do not borrow inferential meaning from it.

#### Major comment 13 — The identifiability ratio is too categorical

Methods says a large edge-to-minimum MAPE ratio means the rate “is identified.” The ratio depends on the selected edges, parameter domain, objective, nuisance-level profiling, and dataset. It is a localization contrast, not an identification theorem.

**Required action:** rename it “profile range ratio” or “edge-to-minimum objective ratio,” define the edges, and say larger values indicate stronger localization over that declared range.

#### Major comment 14 — The local Hessian should remain secondary

The condition number and coupling are useful geometry diagnostics, but their magnitudes depend on log parameterization, scaling, finite-difference settings, discretization, and evaluation point. The manuscript acknowledges much of this. Until the promised sensitivity table is supplied, the broad profile should carry the main evidentiary weight.

The code-level convergence verdict also calls a profile width “domain-independent” while the set is boundary-censored. Remove that phrase.

#### Major comment 15 — The Table 7 intersection does not “collapse” the rate to a narrow measured band

Interpolating the committed caffeine profile gives an implied rate of approximately 0.95 at the Table 7 inventory of 12.54 g/L. Applying the manuscript's assumed ±10% inventory perturbation gives approximately 0.60–1.76. This is narrower than the right-censored beverage-only set, but it is not especially narrow and is not a confidence interval. The ±10% value is an analyst-selected sensitivity, not reported uncertainty on the inventory assay.

**Required action:** call it a conditional one-dimensional intersection or sensitivity band. Report its same-campaign status and avoid “collapses” unless accompanied by a justified measurement-uncertainty model.

#### Major comment 16 — The finite profile-set prediction ranges are deterministic tolerance-set ranges

The Figure 4 ranges are generated from rates whose O-fit MAPE lies within 10% of the finite-grid minimum. They are not posterior intervals, confidence intervals, prediction intervals, or measurement-uncertainty intervals. Their width depends on threshold and grid.

The manuscript generally calls them envelopes, which is acceptable, but every caption/legend should add “across the declared objective-tolerance set.” A threshold- and grid-sensitivity plot is needed to show whether the reported median width near 3% is stable.

### 5.4 Cross-grind transfer, null benchmark, and joint fit

#### Major comment 17 — The null benchmark changes the interpretation of the entire transfer section

Figure 4's baseline is now the most important control in §5. The mechanism's pooled MAPE is approximately 8.23%, versus 8.59% for the O-trained constant; it is worse on 50 of 108 points. This supports “no catastrophic deterioration” in absolute endpoint error but very little incremental skill attributable to temperature/pressure/flow/kinetic response.

The manuscript says this clearly in several paragraphs. However, the standing position says the refit “transfers across grind,” and the transfer routine's docstring still says “transfers REASONABLY.” Those phrases will be quoted out of context and should be removed everywhere.

#### Major comment 18 — The 0.36 percentage-point skill difference needs a paired, design-aware uncertainty analysis

A pooled mean alone does not reveal whether the small advantage is systematic, concentrated in a few groups, or within source measurement variability. The 108 points are structured by variety, solute, grind, and repeated T/p combinations; they are not exchangeable independent draws.

**Required action:** export pointwise model-minus-baseline loss differences and summarize them by group and condition. Use a clustered paired resampling or clearly descriptive group-level distribution. The likely conclusion may remain “little incremental skill,” but it should be numerically grounded.

#### Major comment 19 — “Nested reduced-model ladder” is technically incorrect

The one-constant, per-grind constants, shared mechanism, and per-grind mechanism are not all nested models under one common likelihood and parameterization. They also have unequal flexibility and are fitted and scored in-sample. The result that the shared mechanism has lower MAPE than the per-grind constants in none of six fits is useful as a descriptive comparator, but it does not prove that mechanism “explains essentially nothing.”

**Required action:** call this an in-sample model-complexity or comparator ladder. Report parameter counts and avoid inferential language unless using cross-validation, information criteria under a specified likelihood, or another fair predictive comparison.

#### Major comment 20 — The joint fit is compatibility, not transfer

The draft mostly handles this well. Preserve that wording in Figure 5, abstract, conclusion, result bundle, and code. “Shared-parameter compatibility” is the correct concept. A 1.5-point in-sample cost of sharing can be informative, but it does not demonstrate prediction under a new grind, campaign, coffee, or rig.

#### Major comment 21 — The flow-map robustness claim is based on one representative group

`flow_map_sensitivity_transfer` defaults to Arabica caffeine. §5 presents the ≤0.6-point movement as support that the transfer conclusion does not hinge on flow-map magnitude. That may be true for the representative case, but the code does not establish it for all six variety×named-solute fits.

The test also perturbs only a global multiplicative scale. It does not test errors in pressure dependence, temperature dependence, grind dependence, or time-varying flow.

**Required action:** run all six groups or narrow the prose to “representative Arabica-caffeine magnitude sensitivity.” Keep map-form uncertainty prominent.

#### Major comment 22 — The geometry sweep is a global-choice sensitivity, not a grind-map test

The current prose is comparatively careful: one Pannusch geometry is applied globally to all grinds. Maintain this. Do not let “≤1 pp” become a claim that geometry is unimportant across grinders. A grind-specific geometry map remains unvalidated.

### 5.5 Cross-validation and uncertainty

#### Major comment 23 — The LOCO ranges are appropriately descriptive, but “interval” remains easy to overread

The manuscript explicitly states that the two resampling summaries use already-computed fold errors and do not repeat fitting. This is an important correction. Because LOCO training sets overlap, fold errors are dependent; naive resampling can materially understate variance. The current result should remain a descriptive central range, not a confidence interval.

**Required action:** label the ranges “descriptive resampling range” wherever displayed. If inferential coverage is needed, perform a resampling procedure that repeats the fit and respects the condition/group structure.

#### Major comment 24 — LOCO should expose parameter instability, not only prediction error

The paper's thesis concerns parameter localization. LOCO therefore offers a natural diagnostic: how often does the selected rate hit the search boundary, how much does it vary among folds, and how strongly does inventory compensate? Figure 3 currently shows only predictions and residuals.

**Required action:** export fold-specific rates and levels and provide a supplementary parameter-stability panel. This may reinforce the central conclusion even if prediction errors remain modest.

#### Major comment 25 — Source measurement uncertainty is not propagated

Angeloni source records are condition means from duplicate extractions with reported variability, but the repository lacks complete analyte-specific replicate data. The manuscript is transparent about this. The missing uncertainty does not negate the qualitative profile valley, but it prevents claims about calibrated parameter intervals and makes small differences—especially the 0.36-point baseline advantage—hard to interpret.

**Required action:** use all available RSD information in sensitivity analyses, state which analytes lack it, and avoid significance language.

### 5.6 Positive control and external Waszkiewicz panel

#### Major comment 26 — The same-model simulation is an information demonstration, not validation

The exact-cup simulation uses the same model for data generation and recovery. It is valuable because it isolates observation-operator effects, and the off-grid/noise/discrepancy extensions improve it. Still, the central curve is an inverse-crime best case. The text generally acknowledges this. Keep it in a “simulation study” tier and do not call it empirical verification.

#### Major comment 27 — The most important simulation controls are hidden in the bundle

The off-grid recovery, heteroscedastic/correlated noise, and discrepancy-dose results bear directly on whether the sharp fraction minimum is a grid/noise artifact and whether localization implies model correctness. They should not remain only in code/result JSON.

**Required action:** add a concise supplementary figure and source table. At minimum show recovered-versus-true rate under off-grid cases and the discrepancy-induced bias/floor.

#### Major comment 28 — Figure 6 mixes a seed-specific line with a 20-seed ensemble band

The plotted exact-cup center line appears to be a single seed while the fill is mean±SD over 20 seeds. A reader naturally interprets the line as the center of the band. Use the ensemble mean as the line or label the line as seed 0 and display the mean separately.

#### Major comment 29 — The external observation operator admits a physically impossible negative collected-mass bin

The Waszkiewicz routine computes each observed five-second bin mass by differencing interpolated values of the raw cumulative-mass trace. In the committed 9-bar trace, cumulative mass decreases locally 58 times; the minimum one-step decrease is approximately −0.01784 g and the reported flow reaches approximately −0.00946 g/s. With the declared 4 s offset, one five-second bin has mass approximately −0.01816 g.

A negative collection mass can generate a negative weight in the cup-average calculation. Even if the affected bin is small and the broad result is likely unchanged, the current operator is physically invalid and can distort the alignment sensitivity.

**Required action:** construct a monotone cumulative-mass estimate or integrate a nonnegative, smoothed measured-flow trace; define treatment of pre-drip noise; add nonnegativity and mass-balance assertions; then rerun all offsets and first-bin choices.

#### Major comment 30 — The external module still calls the exercise an “external prediction” in its top-level scope

The target concentration level is reprofiled at every rate. This is external-data objective localization, not a frozen absolute prediction. Function-level text mostly says this correctly, but the module header says “external prediction / objective localization.” Remove the former phrase.

#### Major comment 31 — The one-cup flatness is algebraic and should remain a design illustration

The manuscript correctly explains that one integrated scalar paired with one free multiplicative level can be fit exactly at every rate. This is not empirical evidence that all cup-integrated designs carry no rate information. Keep the current qualifier and consider showing a schematic multi-cup counterexample in Discussion: distinct endpoints/flows can create a non-flat profile even with a nuisance level.

### 5.7 Figures and source-data contract

#### Major comment 32 — Figure 7 displays missing matched values as zero-height bars

The plotting code converts `NaN` matched values to zero for 5-CQA and TDS. A zero-height bar visually implies zero error, not “not available.” This is a definite visualization bug.

**Required action:** omit the bar and label NA, use hatching, or show a distinct missing marker. Add a regression test on plotted categories.

#### Major comment 33 — Figure 7's n=9 correlations are exploratory

The revised intended label “cross-condition association” is better than “trajectory-shape agreement.” With only nine points per group and no uncertainty, categorical color rules around zero or 0.4 are too strong. Report the raw values with uncertainty/sensitivity or use neutral colors and descriptive wording.

#### Major comment 34 — Figure 8 is a pre-fit discrepancy plot, not a residual-structure proof

The current manuscript caption is now appropriately cautious, but the raster title is not. Even after rerendering, Figure 8's scientific value is limited unless it shows post-level residuals. The current pre-fit plot primarily visualizes group offsets that the target-specific level is designed to remove.

#### Major comment 35 — Figure 4's envelopes need an explicit legend and complete export

The light vertical ranges in panels (a) and (b) are easy to read as statistical uncertainty. Add a legend stating “min–max prediction across discrete 10%-MAPE rate set; not a confidence/prediction interval.” Export the lower/upper predictions and the O-trained constant for every condition.

#### Major comment 36 — Figure 2 reports a MAPE cross-check without displaying the MAPE profile

The lower panels show SSE profiles; annotations report MAPE fractions/Jaccard. This is acceptable only if the caption and source table make the distinction unambiguous. Better options are a small overlaid normalized MAPE curve, a supplementary MAPE panel, or a table. The current source export includes SSE only.

#### Major comment 37 — Figure 3's observed-versus-predicted panel is dominated by analyte-level separation

Because analytes occupy distinct concentration ranges, the near-diagonal cloud can look stronger than within-group predictive performance. The residual panels help, but a faceted or standardized residual presentation would be more informative. Add fold-selected rate and boundary-hit information in the supplement.

#### Major comment 38 — Figure 5 overstates a non-nested in-sample comparison

The title/panel wording “reduced-model ladder” and “beats per-grind constants in only 0/6” should be revised. Use “shared mechanism has lower in-sample MAPE in none of six group comparisons.” Provide parameter counts in the panel and state that no complexity penalty or independent test is applied.

#### Major comment 39 — The source-data exporter does not meet its own promise

The exporter says it writes the numeric data behind the data-bearing figures from the same bundle. It omits Figure 3, Figure 4, much of Figure 5's ladder, Figure 6's external/sensitivity/control data, and the MAPE profile behind Figure 2 annotations. This is a concrete reproducibility gap.

### 5.8 Manuscript form and literature framing

#### Major comment 40 — The working document is still an internal handoff, not a submission manuscript

The draft contains a repository note, review IDs, function names as methodological shorthand, “owed” analyses, a live gap ledger, and a change-log pointer. These are excellent project-management devices but inappropriate in the submitted manuscript. The JFE conversion draft is a useful start but still retains many internal markers.

**Required action:** make the journal manuscript self-contained and conventional. Move the detailed audit trail to a supplement or repository release notes.

#### Major comment 41 — Two manuscript sources create a new drift risk

`docs/PAPER_A_DRAFT.md` and `docs/submission/PAPER_A_JFE_MANUSCRIPT.md` both contain scientific claims and numbers. Unless one is generated from the other, corrections can land in only one. This is already visible in the repository's artifact drift.

**Required action:** select one canonical source or use a templated build that generates venue variants from a common body and result table.

#### Major comment 42 — The source-study description is largely accurate and should be preserved

The Schmieder paper reports ten consecutive fractions, a 15-setting design, generally three repetitions and six at the center, and cup responses calculated by integrating fitted extraction kinetics. The current draft's distinction between ten collected fractions and the repository's six-window subset is an important correction. Keep it, and state clearly whenever a repository-derived quantity is not the source's direct raw endpoint.

#### Major comment 43 — Novelty wording should remain provisional

The manuscript appropriately calls the literature exercise a documented scoping search and avoids categorical priority. Preserve this until the planned indexed search is complete. The applied contribution is the espresso case study and explicit evidence-tier/profile analysis, not a new identifiability method.

#### Major comment 44 — Profile-analysis literature should be used to motivate prediction propagation, not confer confidence-region status

Profile methods are particularly relevant because they separate an interior optimum from weak or boundary-open localization and encourage examining predictions along the profile. The current Figure 4 step is conceptually aligned with that literature. But without a likelihood/noise model and calibrated threshold, the 10% objective set is a deterministic sensitivity set only.

#### Major comment 45 — Cross-validation dependence is correctly acknowledged and should remain central

The manuscript's caution about overlapping LOCO training sets is statistically justified. Do not let descriptive ranges migrate into a graphical “95% CI” label in a later venue conversion. Any formal comparison of model and baseline should respect clustering and repeated fitted datasets.

---

## 6. Targeted independent checks

These checks use committed tidy data and source tables and do not rerun the PDE solver. They are intended to identify internal inconsistencies and to guide the required full reruns.

### 6.1 Primary blind MAPE convention

From `fig7_8_per_condition_residuals.csv`:

| Summary | Recomputed value |
|---|---:|
| Named solutes only: caffeine, trigonelline, 5-CQA | **26.329%** |
| Named solutes plus TDS/total-solids proxy | **22.658%** |
| Number of blind residual rows | 72 |
| Blind residuals below zero | 72/72 |

The approximately 22.6% result is reproducible only when the proxy is pooled, contradicting the stated primary convention.

### 6.2 Per-group blind error and effect of inventory matching

| Variety | Observable | Blind MAPE (%) | Inventory-matched MAPE (%) | Cross-condition correlation |
|---|---|---:|---:|---:|
| Arabica | caffeine | 12.89 | 3.05 | 0.22 |
| Arabica | trigonelline | 28.64 | 35.74 | 0.04 |
| Arabica | 5-CQA | 47.73 | NA | −0.25 |
| Arabica | TDS proxy | 9.80 | NA | 0.68 |
| Robusta | caffeine | 40.02 | 6.70 | −0.43 |
| Robusta | trigonelline | 11.48 | 25.91 | 0.47 |
| Robusta | 5-CQA | 17.22 | NA | 0.16 |
| Robusta | TDS proxy | 13.49 | NA | 0.43 |

The results support a descriptive observation that inventory matching helps caffeine and worsens trigonelline under the selected mapping. They do not show that an inventory level cannot remove group offsets; they also do not establish a stable temperature/pressure response from n=9 correlations.

After demeaning residuals within each variety×observable group, the pooled correlations are approximately:

- temperature: **0.167**;
- pressure: **0.066**.

These values reinforce the need for a post-level residual analysis before claiming structured operating-condition mismatch.

### 6.3 Caffeine profile

From the current exported SSE profile:

| Quantity | Recomputed value |
|---|---:|
| Number of rate-grid points | 29 |
| Numerical SSE-profile minimum | rate ≈ **0.659** |
| 10%-above-minimum grid set | approximately **0.385–6.5** |
| Fraction of grid within threshold | **0.759** |
| Upper boundary included | **yes** |

This supports the central “interior optimum but right-censored near-optimal set” result.

### 6.4 Table 7 intersection sensitivity

Linear interpolation of the committed caffeine profile gives approximately:

| Assumed inventory | Implied rate |
|---:|---:|
| 12.54 g/L | **0.95** |
| −10%: 11.286 g/L | **1.76** |
| +10%: 13.794 g/L | **0.60** |

The direction is physically consistent with the compensating profile, but the range should be called an assumed sensitivity, not a measured uncertainty interval.

### 6.5 Waszkiewicz mass trace and bin construction

For the committed 9-bar trace:

| Diagnostic | Value |
|---|---:|
| Trace samples | 1000 |
| Local cumulative-mass decreases | **58** |
| Minimum one-step mass increment | **−0.017837 g** |
| Minimum reported mass-flow rate | **−0.009459 g/s** |
| Maximum reported mass-flow rate | 2.019789 g/s |

Five-second bin masses produced by the current differencing operator:

| Declared offset | Negative bins | Minimum bin mass | Sum over 0–60 s bins |
|---:|---:|---:|---:|
| 0 s | 0 | 0.004922 g | 60.4909 g |
| 2 s | 0 | 0.007517 g | 56.5358 g |
| 4 s | **1** | **−0.018164 g** | 52.5630 g |

The negative value is small but physically invalid. It is a definite implementation defect in a declared sensitivity case.

---

## 7. Figure-by-figure review

### Figure 1 — Study and evidence design

**Strengths**

- The three campaign/evidence lanes are much clearer than a generic validation pipeline.
- It correctly distinguishes the Schmieder/Pannusch calibration lineage, the within-Angeloni recalibration/holdouts, and the independent Waszkiewicz panel.
- Table 7 is correctly presented as a same-campaign orthogonal measurement rather than external validation.

**Required revisions**

- Add a prominent note that Angeloni pressure is converted to inferred flow and that C/F are from the same campaign.
- Arrows can imply evidentiary dependence or validation progression; the standalone caption's “analysis order, not causal validation” sentence should appear in the final caption.
- Label the Waszkiewicz box “target-profiled external shape localization,” not simply external localization.
- If Figure 1 remains a main figure, reduce small text and ensure legibility at journal column width.

### Figure 2 — Inventory–rate SSE surface and profile

**Strengths**

- The figure clearly shows compensating inventory and rate.
- The profile panel explicitly marks the domain-edge censoring.
- The local condition number/coupling are labelled as geometry diagnostics.

**Required revisions**

- Clarify that the colored surface is normalized unweighted SSE and that the lower curve is the profiled SSE—not MAPE.
- Either display the MAPE profile/cross-check or move the MAPE overlap statistics to a supplementary table.
- Improve contrast of the legend and the Table 7 line, especially against the dark surface.
- State the threshold and rate domain in the caption.
- The phrase “set open” should be replaced by “right-censored at the tested upper boundary”; the set is finite in the computed grid.
- Export both SSE and MAPE profile data.

### Figure 3 — Leave-one-condition-out holdouts

**Strengths**

- The signed-residual panels are more informative than the observed–predicted panel alone.
- The title correctly labels the resampling as descriptive rather than inferential.

**Required revisions**

- The observed–predicted panel is dominated by between-analyte concentration levels. Consider facets, normalized residuals, or a supplementary per-group panel.
- Add or tabulate fold-selected rates, levels, and boundary hits.
- Reduce title density and avoid embedding too many numerical results in the title.
- Make clear that repeated T/p levels and overlapping fits mean points are not independent.
- Export all 54 fold predictions and fold fit diagnostics.

### Figure 4 — O→C/F holdout versus level-only baseline

**Strengths**

- This is the most important improvement in the revision.
- It places absolute error beside the appropriate trained null rather than implying that a low MAPE alone supports mechanism.
- It shows the finite profile-set prediction ranges condition by condition.

**Required revisions**

- Add a legend for the vertical ranges and label them as deterministic tolerance-set ranges, not uncertainty intervals.
- Report the absolute difference (0.36 percentage points) as well as the approximately 4% relative skill; the latter can sound larger than it is.
- Include group-level paired differences and uncertainty/sensitivity.
- State “model worse on 50/108 points” in the caption or table, not only as a small annotation.
- Export observed values, point predictions, lower/upper ranges, constant predictions, and losses for every held-out condition.
- Use “matched-volume proxy for the nominal 40 g cup,” not “matched-volume proxy for the 40 g endpoint,” if density is not explicitly applied.

### Figure 5 — Shared-parameter compatibility and comparator ladder

**Strengths**

- The figure separates joint and per-grind MAPE and makes the cost of sharing visible.
- Boundary fits are at least noted.

**Required revisions**

- Rename panel (d) as a non-nested in-sample comparator ladder.
- Replace “in only 0/6 fits” with “in none of six fits.”
- Add parameter counts directly to the legend and state that no penalty or held-out evaluation is used.
- Explain boundary markers visually; do not rely on title text alone.
- Consider confidence/sensitivity indicators or keep all comparisons explicitly descriptive.

### Figure 6 — Temporal resolution and aggregate profiles

**Strengths**

- The evidence tiers are explicitly separated.
- The external panel shows the high minimum MAPE and shallow localization rather than hiding them.
- The cup's algebraic flatness is correctly qualified.

**Required revisions**

- Use the ensemble mean as the simulation line if the band is mean±SD.
- Repair the Waszkiewicz mass/bin operator and rerender panel (d).
- Show the off-grid/noise/discrepancy controls in a supplement.
- Label the external profile “target-level-profiled,” and state that it is one optical-TDS trajectory from one coffee/grind.
- Consider plotting actual profile values rather than relying on range-ratio annotations alone.

### Figure 7 — Per-group diagnostics

**Definite current-artifact problems**

- The committed raster is stale and still says “trajectory-shape agreement.”
- Its title is a verdict and contradicts the claimed neutral-title contract.
- Missing matched values are plotted as zero-height bars.

**Required revisions**

- Rerender from current code after fixing missing-value handling.
- Use neutral colors or uncertainty-aware presentation for n=9 correlations.
- Replace categorical “better/worse” annotations with numerical differences and a clear “descriptive” qualifier.
- Consider moving this figure to the supplement because it does not test held-out skill.

### Figure 8 — Blind residuals versus operating conditions

**Definite current-artifact problems**

- The committed raster retains the withdrawn statement that a pure inventory rescale cannot remove the offsets.
- The current plot is pre-target-level and therefore cannot establish irreducible within-group T/p structure.

**Required revisions**

- Rerender with the current neutral title immediately.
- Preferably replace the displayed residuals with post-level residuals and summarize within-group trends.
- If retained as pre-fit context, put it in the supplement and state that group offsets motivate, rather than defeat, target-level fitting.
- Fix the broken manuscript reference to “§10.14.”

---

## 8. Section-by-section manuscript comments

### Title and abstract

- The title is memorable, but the JFE conversion title is more direct and searchable. Consider a hybrid: **“Whole-cup measurements can obscure kinetic-rate localization: an espresso extraction case study.”**
- “Strong practical non-identifiability” is acceptable only when immediately tied to the tested objective/domain. “Weak practical localization” is more precise.
- Replace the contradictory sentence saying condition-wise envelopes remain owed.
- Add the 0.36-percentage-point absolute difference alongside 4% relative skill.
- Avoid saying the rate “is not separately estimable” without “under the tested objective/domain and available measurement uncertainty.”
- The abstract is long and contains implementation detail. Move Hessian coupling, Jaccard overlap, and 18-point-grid detail to Results unless the target journal permits a structured long abstract.

### Methods 2.1 — Model

- Replace package/runtime names with equations and a parameter table.
- Demonstrate or cite the exact linearity in inventory; state numerical conditions under which it holds.
- Define both profiled level estimators: least-squares level for SSE and weighted-median level for MAPE.
- Give units for all concentrations, rate multipliers, flow, endpoints, geometry, and inventory.
- State solver tolerances, spatial/temporal grids, and any positivity/floor handling.

### Methods 2.2 — Data

- Preserve the improved Schmieder description.
- State explicitly that Schmieder's reported cup outcomes were calculated from integrated extraction kinetics, not direct whole-cup measurements.
- Clarify whether Angeloni's 66 records include off-grid conditions and exactly how many enter each analysis.
- Define the analytical distinction among named solutes, gravimetric total solids, modeled pseudo-TDS, and optical TDS.
- Include data licenses and persistent identifiers.

### Methods 2.3 — Pressure-to-flow map and endpoint

- Use 40 mL proxy consistently; §5 still says matched 40 g cups.
- Separate endpoint uncertainty (mass, density, stop tolerance) from flow-map uncertainty.
- State that the p→flow map is constructed and not validated against per-condition measured flow.
- Describe the ±20% scale sweep as magnitude-only and representative if it remains Arabica caffeine only.

### Methods 2.4 — Fitting and evaluation

- Define the exact training/test units and macro-aggregation hierarchy.
- State the rate-domain bounds and grid density for every analysis.
- Identify whether optimization is grid-only or followed by continuous refinement.
- Define how ties and boundary solutions are handled.
- State that the O-trained constant is re-estimated separately for each variety×solute group.

### Methods 2.5 — Identifiability metric

- Rename the edge/min ratio and avoid binary “identified” wording.
- Define threshold sets as deterministic objective-tolerance sets.
- Explain why 10% was selected and show threshold sensitivity.
- Explain that SSE and MAPE use different nuisance-level estimators.

### Result 1

- Correct the 22.6% headline to the named-solute primary result.
- Separate blind cross-dataset discrepancy from target-data recalibration.
- Avoid implying that the flow refinement is generally unimportant; it is small under this matched endpoint and these maps.
- Do not infer a unique cause for the remaining discrepancy.

### Result 2

- Preserve the interior-optimum/right-censored-set distinction.
- Reframe Table 7 as a conditional sensitivity/intersection.
- Keep the Hessian secondary.
- Replace “domain-independent profile width” in generated verdicts.

### Result 3

- Replace “matched 40 g cups.”
- Make baseline-relative interpretation the first conclusion, not an afterthought.
- Rename the model ladder.
- Add design-aware paired skill uncertainty.
- Distinguish finite profile-set stability from mechanistic skill and from statistical prediction uncertainty.
- Limit flow-map robustness to the tested representative case or expand it.

### Section 6 — Observation operator and external test

- Preserve the distinction among empirical sampled aggregate, same-model exact cup, and external target-profiled TDS.
- Repair the Waszkiewicz bin operator.
- Plot the critical simulation controls.
- Avoid general statements that time-resolved data “supply” rate information without “in the tested design/model.”

### Discussion and standing position

- Replace “A refit to Angeloni transfers across grind” with the brief's maximum claim.
- Emphasize that endpoint stability along a compensating set does not imply a mechanistic response is contributing useful skill.
- Add a concise discussion of what new experiment would separate inventory and rate: independent inventory plus multiple resolved fractions or multiple endpoints/flows.
- Explain that a single scalar plus a fitted level is a special algebraic case, not a universal indictment of cup data.

### Open gaps, figures, related work, reproducibility

- Move the gap ledger to supplementary/repository documentation.
- Fix the nonexistent §10.14 cross-reference.
- Remove the claim that every title is neutral until the figures are rerendered.
- Correct the build and figure-code “six figures” text.
- Expand the reproducibility list to every cited routine and one exact release command.
- Keep novelty wording provisional until the indexed search is complete.

---

## 9. Required numerical reruns and tests

### 9.1 Clean release rerun

**Procedure**

1. Start from a clean, pinned checkout.
2. Install from the archival environment lock.
3. Run the single release command.
4. Recompute every analysis, render all figures, export all source tables, and write manifest.
5. Compare generated manuscript claim table and figures with committed outputs.

**Pass criteria**

- exact commit equality across head, bundle, manifest;
- clean tree before computation and documented expected output changes after;
- all source, code, manuscript, result, source-data, and figure hashes present;
- no stale verdict strings;
- all automated tests pass.

### 9.2 Waszkiewicz physical-bin reconstruction

**Candidate methods**

- isotonic regression of cumulative mass, followed by bin differencing;
- monotone spline constrained to nonnegative derivative;
- integration of a smoothed, nonnegative measured-flow trace, with total-mass reconciliation.

**Required diagnostics**

- number/minimum of bin masses;
- mass balance over 0–60 s;
- sensitivity to smoothing/monotonic reconstruction;
- all offset and first-bin cases;
- updated objective curves and conclusions.

**Pass criteria**

- no negative bin mass or negative weighting;
- stated mass-balance tolerance satisfied;
- external conclusions reported only for physically admissible variants.

### 9.3 Full endpoint×density transfer sensitivity

For each endpoint/density combination:

- refit O level and rate;
- transfer to C/F;
- recompute O-trained constant;
- propagate the finite tolerance set;
- report paired model-minus-baseline losses;
- state whether the 0.36-point advantage and 50/108 result are stable.

### 9.4 Continuous/profile prediction-set sensitivity

- use denser rate grids and continuous profile optimization;
- evaluate 2%, 5%, 10%, and 20% relative-objective sets;
- optionally add likelihood-calibrated increments only if a noise model is specified;
- plot condition-wise C/F ranges and convergence;
- report whether the upper set remains boundary-censored.

### 9.5 All-group flow-map magnitude sensitivity

Run ±20% or a justified range for all six variety×named-solute fits and report:

- fitted rate/level shifts;
- C/F MAPE shifts;
- model-minus-constant differences;
- boundary hits;
- group heterogeneity.

### 9.6 Baseline skill uncertainty

Construct pointwise paired loss differences and resample at a defensible unit, for example the shared T/p condition or variety×solute×grind group. Report:

- pooled mean and median difference;
- group distribution;
- proportion of points/groups favoring the mechanism;
- sensitivity to MAPE versus log/relative loss;
- no independence-based p-value unless assumptions are justified.

### 9.7 LOCO refit-resampling or descriptive-only presentation

Either:

- repeat the complete fold fitting inside a hierarchical/clustered resampling design; or
- retain only fold-level empirical distributions and explicitly avoid coverage language.

### 9.8 Post-level residual analysis

For each variety×observable group:

- fit the declared target level using the same objective as the analysis;
- plot signed residuals versus T and p;
- quantify trend with uncertainty appropriate to n=9 and repeated level structure;
- avoid pooling proxies with named solutes.

### 9.9 Figure 6 ensemble consistency

Verify that the plotted center line, band, and exported table all use the same ensemble definition. Add tests comparing plotted values to bundle fields.

### 9.10 Complete source-data reproduction test

For each figure, write a lightweight test that rebuilds all plotted coordinates from the exported CSV alone and compares them with the bundle. The test should fail if a series is omitted or missing values are turned into zero.

---

## 10. Suggested replacement wording

### 10.1 Abstract transfer paragraph

> A calibration fitted on optimal-grind conditions yielded pooled coarse/fine endpoint MAPE of 8.2%, compared with 8.6% for an O-trained level-only constant; the mechanistic model was worse on 50 of 108 held-out points. Thus, the fitted level-plus-rate pair did not deteriorate catastrophically across the held-out grinds, but it added little predictive skill beyond carrying a concentration level. Ranges propagated across the finite 10%-relative-MAPE rate set were narrow for many conditions, indicating prediction stability within that declared tolerance set rather than parameter identification or a confidence interval.

### 10.2 Abstract envelope sentence

> Condition-wise ranges across the finite 18-point 10%-relative-MAPE tolerance set are reported; continuous, grid-converged profile-prediction propagation remains future work.

### 10.3 Result 1 primary summary

> Across the three named solutes, the blind source-model comparison had macro-MAPE of approximately 26.3%. A secondary summary that also includes the non-equivalent aggregate-solids proxy was approximately 22.6% and is reported separately.

### 10.4 Table 7 paragraph

> Intersecting the profiled caffeine inventory–rate curve with the same-campaign roasted-and-ground inventory value gives a conditional implied rate near 0.95. An illustrative ±10% perturbation of that inventory maps to rates of approximately 0.60–1.76. This narrows the beverage-only tolerance set but is not a confidence interval, because the ±10% range is a sensitivity assumption rather than a calibrated measurement-uncertainty model.

### 10.5 Comparator ladder paragraph

> An in-sample comparator ladder places the shared mechanistic fit beside level-only alternatives of different flexibility. The shared two-parameter mechanism had lower in-sample MAPE than the three-parameter per-grind constant in none of six variety–solute comparisons. Because these models are not a single nested likelihood sequence and are scored on their fitting data, the comparison is descriptive; it shows that the mechanistic response did not improve in-sample MAPE over grind-specific levels in this dataset.

### 10.6 Standing position

> `pannusch2024` remains calibrated to the Schmieder fraction campaign, whereas Angeloni is an independent target campaign. After target-specific O-grind recalibration and matched-endpoint mapping, absolute C/F errors were modest, but performance was nearly matched by an O-trained level-only constant. The result therefore supports endpoint prediction stability under the tested within-campaign design, not transfer of an identified kinetic mechanism.

### 10.7 Waszkiewicz paragraph after operator repair

> With a physically admissible nonnegative mass-weighting reconstruction, profiling a target-specific level against the independent five-second optical-TDS trajectory produced a shallow, high-error rate objective. This shows that the resolved trajectory moves the objective more than the corresponding single scalar under the tested alignment and observation operator; it is not an absolute-concentration prediction or a validated kinetic-rate estimate. The single-cup objective is flat algebraically because one scalar level is profiled against one scalar observation.

### 10.8 Figure 8 caption

> **Blind source-model discrepancies before target-level fitting.** The plot displays signed pre-fit discrepancies by operating condition. Between-group offsets motivate target-specific level recalibration; the figure does not determine whether temperature- or pressure-dependent structure remains after that level is fitted.

### 10.9 Reproducibility statement

> All manuscript-facing results, tables, figures, and source-data exports were regenerated from a clean checkout at commit `<SHA>` using `<single command>`. The release manifest records the exact environment, transitive input hashes, result-bundle hash, individual figure/source-data hashes, and strict equality of repository head and bundle source commit.

---

## 11. Submission-readiness checklist

### Scientific claims

- [ ] Primary named-solute result corrected.
- [ ] All mechanistic-transfer wording removed or narrowed.
- [ ] Table 7 result reframed as a conditional sensitivity/intersection.
- [ ] Comparator ladder renamed and interpreted descriptively.
- [ ] Finite tolerance-set ranges clearly distinguished from confidence/prediction intervals.
- [ ] Endpoint and flow-map robustness claims match the actual estimands tested.
- [ ] Waszkiewicz operator repaired and sensitivity rerun.
- [ ] LOCO uncertainty remains descriptive unless fitting is repeated under resampling.

### Figures and tables

- [ ] Eight figures rerendered from current bundle.
- [ ] Figures 7/8 stale titles eliminated.
- [ ] Figure 7 missing values no longer appear as zero.
- [ ] Figure 4 tolerance-set range legend added.
- [ ] Figure 6 line/band ensemble definition aligned.
- [ ] Critical simulation controls plotted in supplement.
- [ ] Every plotted series exported to tidy source data.
- [ ] Vector and raster outputs visually checked and hashed.

### Methods and reporting

- [ ] Conventional equations and parameter table added.
- [ ] Training/test units and aggregation hierarchy defined.
- [ ] Objective/domain/threshold choices specified.
- [ ] Source endpoint and proxy distinctions explicit.
- [ ] Pressure-to-flow assumptions and limitations explicit.
- [ ] Measurement uncertainty and available weighting sensitivities reported.
- [ ] Internal IDs, backlog language, and function-name prose removed.
- [ ] Full references, declarations, and data/code availability completed.

### Reproducibility

- [ ] One canonical manuscript source selected.
- [ ] One release command recomputes, renders, exports, and verifies.
- [ ] `HEAD`, bundle, and manifest commits identical.
- [ ] Clean-tree requirement enforced.
- [ ] All cited analyses included in bundle.
- [ ] Manifest hashes figures, source data, code, manuscript, data, and environment.
- [ ] Release tagged and archived.

---

## 12. Minor and editorial comments

1. Change the header date to the exact revision represented by the release commit.
2. Remove the repository note from the submitted manuscript.
3. Avoid monospace package names in the abstract.
4. Define “O,” “C,” and “F” at first use in abstract/main text.
5. Use one spelling of “nonidentifiability” or “non-identifiability” throughout.
6. Use one spelling of “profiled objective” and reserve “profile likelihood” for likelihood-based work.
7. Replace “independent endpoint dataset” with “independent target campaign” when target parameters are later refit.
8. Replace “matched beverage endpoint” with a concise defined abbreviation only after the full phrase appears.
9. Avoid “strong non-identifiability” without the operational threshold/domain in the same paragraph.
10. Give the full rate domain in Methods, not only in figure annotations.
11. State whether rate multipliers are dimensionless.
12. State whether the same rate multiplier scales both fine and coarse Sherwood prefactors identically.
13. Explain why a per-solute rate is allowed if mechanistic transfer is the scientific target.
14. Give the exact macro-averaging order: condition, grind, solute, variety.
15. Replace “wide envelope external” with “cross-dataset range-bracketing diagnostic.”
16. Correct “Angeloni's” capitalization where it appears lowercase in §2.3.
17. Separate source duplicate-extraction variability from the number of retained repository records.
18. Clarify whether off-grid O points are among the 33 records per variety.
19. State the viscosity correlation and valid temperature range.
20. State whether 40 mL is applied before or after any density conversion.
21. Replace “the rate is identified” in Methods with “the rate objective is localized.”
22. Define Jaccard overlap of the SSE and MAPE grid sets.
23. State that Jaccard depends on the common finite grid and threshold.
24. Avoid “unambiguous” for a scaling-dependent Hessian result.
25. Replace “reliable Hessian” with a specific numerical diagnostic.
26. Remove “if anything, less bounded” and simply state that the upper extent is unresolved within the domain.
27. Replace “matched 40 g cups” in §5.
28. Report pooled model and constant MAPE to consistent precision.
29. Give the 0.36-point difference, not only rounded 0.4.
30. Distinguish “relative improvement” from percentage-point change.
31. Change “in only 0 of 6” to “in none of six.”
32. Avoid using “manifold” for a finite grid set unless defined as an approximation.
33. Use “objective-tolerance set” consistently.
34. Specify the number of accepted grid points per group.
35. Report whether accepted sets hit either domain boundary for every group.
36. Define the condition-wise envelope width denominator and treatment of near-zero observations.
37. State whether 50/108 counts ties and how ties are handled.
38. Give group-level model-versus-constant losses in a table.
39. Replace “confidence” with “descriptive range” wherever LOCO resampling appears.
40. State random seeds and bootstrap replicate counts in Methods.
41. Explain the log/relative-error sensitivity objective.
42. Avoid “robust” when only one representative flow-map fit is tested.
43. Keep “global geometry choice” in every geometry-sensitivity summary.
44. State that the empirical sampled aggregate is duration-weighted over nonconsecutive analyzed windows.
45. Clarify the relationship between ten collected fractions and six analyzed/model-loaded windows.
46. Replace “no real minimum” with “weak variation over the tested range.”
47. Avoid treating edge/min ratios across different objectives as directly commensurate without normalization.
48. State the simulation noise distribution and scale.
49. Put “inverse crime” in plain language for a broad engineering audience.
50. Show the 20-seed mean, not only an annotation.
51. Correct the Waszkiewicz dataset naming mismatch (`waszkiewicz2025` repository path versus 2026 publication) in a data-provenance note.
52. State that optical TDS, gravimetric total solids, and modeled pseudo-TDS are not interchangeable.
53. Remove “the direction is robust” from the external panel until negative-bin repair is complete.
54. Replace “single cup carries no rate information” with the algebraic single-scalar statement every time.
55. Clarify that multiple cup endpoints could localize a rate even without fractions.
56. Move the “Open gaps” section to Limitations/Future Work and remove project-status labels.
57. Fix “§10.14.”
58. Do not say all figure titles are neutral until rerendered images are verified.
59. Correct “six figures” in module/build docstrings.
60. Expand the reproducibility list to every cited function.
61. Add the Waszkiewicz module to build input hashes.
62. Add model solver and parameter files to transitive hashes.
63. Hash `PAPER_A_CAPTIONS.md` and the canonical submission manuscript.
64. Include source-data table hashes.
65. Include figure hashes by format.
66. Record the exact command and wall time for slow reruns.
67. Record hardware only if it can affect floating-point/reproducibility materially.
68. State deterministic versus stochastic tolerance sources separately.
69. Avoid tolerances so wide that substantive drift passes unnoticed.
70. Generate headline tables from the bundle rather than manually transcribing them.
71. Add automated checks for missing/zero-converted values in figures.
72. Add automated checks for nonnegative mass and flow weights.
73. Add automated checks that all declared profile-set ranges use full-precision predictions before aggregation.
74. Add automated checks that proxy-inclusive values cannot populate named-solute headline fields.
75. Use full DOI-form references and consistent journal abbreviations.
76. Define “source model,” “target recalibration,” and “external panel” in a short evidence-tier table.
77. Move review-history discussion to repository release notes.
78. Remove “This corrects an earlier version” from the abstract unless correction history is scientifically necessary; place it in Discussion or a transparent correction note.
79. Keep the unmatched-endpoint lesson, but state it generally after presenting current results.
80. End the conclusion with the experimental-design implication, not the repository state.

---

## 13. Supporting reference material

### Source experiments and model lineage

1. **Schmieder, B., et al. (2023).** “Influence of Flow Rate, Particle Size, and Temperature on Espresso Extraction Kinetics.” *Foods* 12, 2871. [https://doi.org/10.3390/foods12152871](https://doi.org/10.3390/foods12152871)  
   Relevant to the 15-setting design, ten collected fractions, replicate structure, six analyzed fractions, and cup responses calculated from integrated extraction kinetics.

2. **Angeloni, S., et al. (2023).** *Applied Sciences* 13, 2688. [https://doi.org/10.3390/app13042688](https://doi.org/10.3390/app13042688)  
   Relevant to the target campaign, 40±2 g beverage endpoint, chemical concentrations, granulometry/temperature/pressure design, and same-campaign roasted-and-ground inventory measurements.

3. **Pannusch, A., et al. (2024).** *Journal of Food Engineering* 367, 111887. [https://doi.org/10.1016/j.jfoodeng.2023.111887](https://doi.org/10.1016/j.jfoodeng.2023.111887)  
   Relevant to the component-resolved extraction model and source calibration lineage.

4. **Waszkiewicz, M., et al. (2026).** “Under pressure: Poroelastic regulation of flow in espresso brewing.” *Physics of Fluids* 38, 063113. [https://doi.org/10.1063/5.0319611](https://doi.org/10.1063/5.0319611)  
   Relevant to the independent café-grade-rig flow and time-resolved TDS data used for the external objective-localization panel.

### Identifiability and profile-based analysis

5. **Raue, A., et al. (2009).** “Structural and practical identifiability analysis of partially observed dynamical models by exploiting the profile likelihood.” *Bioinformatics* 25, 1923–1929. [https://doi.org/10.1093/bioinformatics/btp358](https://doi.org/10.1093/bioinformatics/btp358)  
   Supports distinguishing an interior optimum from a profile that fails to close within the tested range and emphasizes reoptimization along the profile.

6. **Wieland, F.-G., et al. (2021).** “On structural and practical identifiability.” *Current Opinion in Systems Biology* 25, 60–69. [https://doi.org/10.1016/j.coisb.2021.03.005](https://doi.org/10.1016/j.coisb.2021.03.005)  
   Supports careful distinction between structural and practical identifiability and between parameter estimation and experimental design.

7. **Simpson, M. J., & Maclaren, O. J. (2023).** “Profile-wise analysis: a profile likelihood-based workflow for identifiability analysis, estimation, and prediction for a mathematical model.” *PLOS Computational Biology* 19, e1011515. [https://doi.org/10.1371/journal.pcbi.1011515](https://doi.org/10.1371/journal.pcbi.1011515)  
   Relevant to propagating profile uncertainty into prediction space while keeping parameter and predictive uncertainty conceptually separate.

### Cross-validation dependence

8. **Bengio, Y., & Grandvalet, Y. (2004).** “No unbiased estimator of the variance of K-fold cross-validation.” *Journal of Machine Learning Research* 5, 1089–1105. [https://www.jmlr.org/papers/v5/grandvalet04a.html](https://www.jmlr.org/papers/v5/grandvalet04a.html)  
   Supports the manuscript's caution that errors from overlapping cross-validation fits are dependent and that naive variance estimates can be misleading.

---

## 14. Bottom line

The revised Paper A has a coherent and worthwhile scientific message: an apparently good whole-cup fit can leave an inventory–rate decomposition weakly localized, and a low endpoint error can add little skill beyond a transferred level. The broad, right-censored profile and the distinction between parameter and prediction behavior are the strongest contributions.

The current repository state does not yet provide a trustworthy submission artifact. The highest-priority work is to repair the Waszkiewicz bin operator, correct the primary named-solute headline, remove residual mechanistic-transfer wording, rerender the stale diagnostic figures, complete the figure/source-data contract, and produce a clean commit-coherent release in which manuscript, bundle, figures, code, and manifest all agree. Once those items are resolved, the paper should be reassessed primarily on the clarity of its engineering methods presentation and the strength of its uncertainty/robustness analysis rather than on the existence of the central profile-valley result.

