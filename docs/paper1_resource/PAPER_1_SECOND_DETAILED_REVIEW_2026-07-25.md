# Second Detailed Review of Paper 1 / Paper A

**Review date:** 25 July 2026  
**Repository:** [`trbrewer/puckworks`](https://github.com/trbrewer/puckworks)  
**Repository state reviewed:** commit [`d9ee264f85b15633f56d540b44066e681979a5fc`](https://github.com/trbrewer/puckworks/tree/d9ee264f85b15633f56d540b44066e681979a5fc)  
**Primary venue manuscript:** [`docs/submission/PAPER_A_JFE_MANUSCRIPT.md`](https://github.com/trbrewer/puckworks/blob/d9ee264f85b15633f56d540b44066e681979a5fc/docs/submission/PAPER_A_JFE_MANUSCRIPT.md)  
**Designated canonical working draft:** [`docs/PAPER_A_DRAFT.md`](https://github.com/trbrewer/puckworks/blob/d9ee264f85b15633f56d540b44066e681979a5fc/docs/PAPER_A_DRAFT.md)  
**Prior external review assessed:** `docs/paper1_resource/PAPER_1_DETAILED_REVIEW-20260724.md` and the resulting action tracker  
**Primary review question:** Is the revised Paper 1 scientifically defensible, internally consistent, readable, and ready for submission as an espresso-modeling case study?

> **Review limitation.** I audited the committed manuscript, canonical draft, action tracker, reviewer brief, uncertainty notes, dimensional audit, analysis code, figure-generation code, cached figures, captions, and literature-search materials. I did not rerun the slow PDE analysis suite. Numerical comments therefore concern the committed result contracts, code paths, and cross-document consistency rather than a clean-room numerical reproduction.

---

## Overall recommendation

# **Major revision before submission**

The paper is substantially stronger than the version assessed in the first review. The central scientific contribution is now clearer and more defensible:

> In the tested espresso extraction model and experimental design, a whole-cup endpoint can be predicted with acceptable error while the extractable-inventory level and kinetic-rate multiplier remain only weakly separated. The mechanistic model's cross-grind endpoint error is also almost matched by a level-only baseline, whereas fraction-resolved measurements move the rate-profile objective more strongly.

That is a worthwhile methods-and-limitations result. It is directly relevant to espresso model development, model validation, and experimental design. The revision has made important progress by adding a level-only null benchmark, dependence-aware bootstrap, objective-family sensitivity analysis, refit-in-bootstrap uncertainty analysis, a dimensional audit of the Table 7 inventory comparison, improved evidence labels, and a clearer distinction between in-sample compatibility, within-campaign holdout, and genuinely external data.

The manuscript should nevertheless **not be submitted in its current form**. The principal blocker is no longer the underlying scientific idea; it is the reliability and coherence of the manuscript as the authoritative statement of the results. The JFE conversion still disagrees with the canonical draft on headline numerical values, contradicts itself on whether analyses are complete, overstates the scope of one uncertainty analysis, and contains unresolved repository/review scaffolding. The current consistency checker only tests a small phrase list and therefore reports success despite these material conflicts.

The most serious current issues are:

1. **Headline numerical drift remains.** The JFE manuscript says the primary observable excludes the aggregate-solids proxy, then reports proxy-inclusive values as the headline. Its 22.6% blind MAPE and 19.9–25.2% endpoint sensitivity conflict with the canonical named-solute values of 26.3% and 23.8–28.8%.
2. **A six-panel robustness claim is supported by only four completed panels.** The manuscript says the objective-family result covers all three solutes and both varieties, while the committed results note explicitly says Robusta trigonelline and Robusta 5-CQA remain owed.
3. **The paper calls an out-of-bag bootstrap interval “coverage-calibrated” without demonstrating coverage calibration.** Repeating the fit is valuable, but it is not the same as establishing frequentist coverage.
4. **The Methods section is still not standalone.** It lacks the governing/observation equations, parameter table, unit bases, dataset-role table, and enough fitting detail for a reader to reconstruct the estimands without the repository.
5. **The Table 7 result has been demoted correctly in prose but is visually re-promoted in Figure 2 as a precise horizontal constraint.** That conflicts with the dimensional audit.
6. **The title remains unsatisfactory.** The working title is a tagline; the JFE title is opaque and does not tell the reader that the paper separates extractable content from extraction rate or compares whole-cup with time-resolved data.
7. **The article still reads partly as a project log.** Review IDs, function names, “delivered/owed/deferred” status language, prior-draft corrections, and placeholders remain throughout.
8. **The section cross-references are systematically wrong** because the JFE conversion and canonical draft have different top-level structures.
9. **Figure 1 contains a scientifically misleading arrow:** it makes the Waszkiewicz external analysis appear downstream of the Angeloni optimal-grind recalibration, although the external shape test freezes Pannusch kinetics and profiles a Waszkiewicz-specific level.

These are all repairable. Once the result contract is made coherent, the missing two robustness panels are either run or the claim is narrowed, the Methods are made self-contained, and the manuscript is rewritten as a journal article rather than a repository status report, Paper 1 should be a credible and useful submission.

---

## 1. Title review

### 1.1 Current working-draft title

> **“The cup can hide the clock: practical inventory–kinetics confounding in a cross-dataset espresso extraction case study.”**

This remains unsuitable for the reasons already identified by the author. “The cup can hide the clock” sounds like a social-media hook or magazine standfirst. It does not tell a literature-search user what quantities are being estimated, what observations are compared, or what the paper actually establishes. The subtitle is more informative, but “inventory–kinetics confounding” is specialist language and the combined title oscillates between glibness and technicality.

### 1.2 Current JFE title

> **“Whole-cup measurements can obscure kinetic parameter localization in espresso extraction models.”**

This version correctly contains **espresso** and is more formal, but it is still not the right title.

- “Kinetic parameter localization” is technically defensible but opaque to many food-science and coffee readers.
- It does not name the paired quantities that are confounded: extractable content/inventory and extraction rate.
- It omits the positive contrast with time-resolved measurements.
- “Can obscure” is vague: the paper makes a more specific design-dependent statement about weak separation under whole-cup endpoint observations.
- The title foregrounds a diagnostic phrase rather than the practical modeling problem.

### 1.3 Recommended title

# **Separating Extractable Content from Extraction Rate in Espresso Models: Limits of Whole-Cup Measurements and the Value of Time-Resolved Data**

This title is the strongest balance of accessibility and precision because it:

- includes **espresso**;
- names the two quantities the paper tries to distinguish;
- states the key comparison between whole-cup and time-resolved data;
- avoids the social-media cadence of “the cup can hide the clock”;
- avoids making “identifiability,” “localization,” “Sherwood multiplier,” or “inverse problem” a barrier at the title level;
- remains appropriately scoped to models rather than claiming a universal property of espresso extraction.

### 1.4 Ranked alternatives

1. **Estimating Extractable Content and Extraction Rate in Espresso Models: Whole-Cup versus Time-Resolved Measurements**
2. **Whole-Cup and Time-Resolved Measurements Provide Different Information About Espresso Extraction Rates**
3. **Weak Separation of Extractable Content and Extraction Rate from Whole-Cup Espresso Measurements**
4. **Practical Identifiability of Extractable Content and Extraction Rate in Espresso Models**
5. **What Whole-Cup Measurements Can—and Cannot—Reveal About Espresso Extraction Rates**

Option 1 is slightly more neutral than the leading recommendation. Option 2 is the most accessible but less explicit about the confounding problem. Option 4 is the most conventional technical title but is less accessible. Option 5 remains somewhat article-like and is not my first choice for a journal paper.

### 1.5 Suggested running title

> **Whole-cup versus time-resolved espresso measurements**

---

## 2. What has improved since the first review

The response to the previous review has been serious and productive. These improvements should be preserved.

| Prior concern | Current status | Assessment |
|---|---|---|
| No declared canonical manuscript | **Addressed in principle** | `docs/PAPER_A_DRAFT.md` is now designated canonical and the JFE file a synced view. The implementation is incomplete because the two still disagree materially. |
| No drift guard | **Partially addressed** | `tools/paper_a_consistency.py` and tests exist, but they check only five retired and six required phrases. They do not check numbers, analysis status, section references, figure labels, or result-bundle provenance. |
| Table 7 treated as a quantitative rate constraint | **Substantially addressed in prose** | The dimensional audit correctly shows the mass-to-volume basis is unresolved and demotes the comparison to qualitative. Figure 2 still visually treats the assay as a precise line. |
| No uncertainty on model-versus-null difference | **Addressed** | The paired clustered bootstrap is a meaningful improvement and the primary interval includes zero. This should be promoted into the abstract. |
| Unweighted-SSE result might be objective-specific | **Partially addressed** | SSE, relative-L2, and Huber sensitivity results support persistence of the valley in four completed panels. The manuscript overextends this to all six panels. |
| Weak two-point holdout | **Addressed materially** | Leave-one-condition-out analysis and a refit-in-bootstrap out-of-bag analysis improve the evidence. Terminology and small-cluster limitations still need correction. |
| Cross-grind result mislabeled as external/mechanistic transfer | **Largely addressed** | It is now described as a within-campaign cross-grind holdout and benchmarked against a level-only constant. Some titles and legacy wording still use “transfer.” |
| Endpoint mismatch | **Addressed** | The 40 mL matched-volume proxy and endpoint sensitivity are now explicit. The numerical headline in the JFE manuscript is stale, and the mass-to-volume approximation still needs a cleaner Methods treatment. |
| Interior optimum versus open profile | **Improved but internally inconsistent** | The formal discussion correctly says the numerical minimum is interior while the tolerance set is right-censored. Elsewhere the manuscript still says the rate is “not a converged interior estimate.” |
| External Waszkiewicz analysis under-scoped | **Improved** | It is now target-level-profiled, high-error, one-coffee/one-grind aggregate-TDS shape evidence, with time-offset and first-bin sensitivity. Additional operator assumptions remain underreported. |
| Literature context missing | **Partially addressed** | A substantial related-work section and bibliography exist. The indexed search remains incomplete, the evidence matrix is unpopulated, and an editorial process note remains in the manuscript. |
| Methods numbering wrong | **Addressed** | Subsections are now correctly numbered 3.1–3.6. In-text section references were deliberately left stale and are now pervasive. |
| Figure evidence categories unclear | **Improved** | Figure 1 is useful in concept and captions are much stronger. Its arrow into the external analysis is wrong, and several figures remain visually crowded. |

The key lesson from this revision cycle is that the paper now has enough analyses. The next step should not be to add another layer of diagnostics indiscriminately. It should be to **freeze a coherent result contract, simplify the article, and make every sentence and figure conform to that contract**.

---

## 3. Submission-critical findings

## Major Comment 1 — The manuscript-consistency system gives false confidence

The action tracker states that the JFE file is a synced view of the canonical draft, and the test asserts that the conversion is “in sync.” That statement is not true in the ordinary scientific sense. The tool is explicit that it is “intentionally narrow”: it checks a curated phrase list, not semantic or numerical equivalence. The current tree demonstrates why that is insufficient.

### 3.1 Material numerical conflicts

| Topic | JFE manuscript | Canonical draft / current declared contract | Required correction |
|---|---|---|---|
| Primary blind per-condition metric | **22.6% including proxy** (L263–L267) | **26.3% named-solute macro-MAPE**, with **22.7% proxy-inclusive** reported separately | Use 26.3% as the primary headline everywhere; report 22.7% only as secondary. |
| Crude versus refined flow map | **23.1% → 22.6%** (L266–L273) | **26.8% → 26.3%** for named solutes | Replace stale values and preserve observable separation. |
| Endpoint sensitivity | **19.9% → 25.2%** (L176–L188) | **23.8% → 28.8%** for named solutes | Correct the numbers and identify whether any proxy-inclusive sensitivity is reported separately. |
| Observable convention | “we never pool the proxy with named molecules” (L250–L255) | Same intended convention | The next table immediately pools it. This is a direct internal contradiction. |
| Rate optimum status | “not a converged interior estimate” (L294–L301) | Interior numerical minimum, broad/right-censored tolerance set | Say the point minimum is interior but weakly localized and not robust as a mechanistic estimate. |
| Refit-in-bootstrap interval | “deferred” (L413–L421) | Delivered and reported later at 7.4%, [4.3, 11.5]% | Delete the deferred statement or move it into historical provenance outside the paper. |
| Residual plots | “still owed” (L640–L650) | Figure 3 already contains signed residuals versus temperature and pressure | Remove the “owed” statement and state exactly what Figure 3 does and does not show. |

These are not stylistic differences. They change the headline error, the endpoint-sensitivity magnitude, and the status of uncertainty analyses. A reviewer who notices the contradiction between L250–L255 and L266 is likely to question the entire result chain.

### 3.2 The supporting result note is itself internally inconsistent

`PAPER_A_P0-5_RESULTS.md` says at its top that sub-analysis C is deferred, repeats that it remains deferred in the model-versus-null section, and then contains a full section titled “Coverage-calibrated LOCO interval that repeats the fit — DELIVERED.” The manuscript inherited both states. This shows that human-readable status notes cannot be treated as an authoritative result database unless they are generated or validated.

### 3.3 The figure code also retains stale scientific language

Figure 5 is still titled around a “reduced-model ladder,” even though the manuscript and consistency tool explicitly retired that phrase in favor of a non-nested **in-sample comparator ladder**. This is another example of a scientifically meaningful label escaping the phrase guard because the guard checks only the two manuscript files.

### 3.4 Required remedy

Do not merely add more phrases to the current list. Replace the present system with a **result-contract workflow**:

1. Create one machine-readable `paper_a_claims.json` or YAML file containing each load-bearing value, observable basis, evidence tier, analysis status, and source function/result-bundle key.
2. Generate or inject tables, abstract numbers, figure annotations, highlights, and venue prose from that contract wherever practicable.
3. Add CI assertions for at least:
   - named-solute versus proxy-inclusive blind MAPE;
   - crude/refined flow-map results;
   - endpoint sensitivity;
   - model-versus-null MAPE and ΔMAPE interval;
   - objective-family panel count and completed groups;
   - LOCO and out-of-bag interval status;
   - figure count and figure labels;
   - Table 7 qualitative-only status.
4. Add a cross-reference linter for every `§` reference in the JFE file.
5. Require cached result-bundle provenance to match the analysis code/content hash used for the paper, not merely a loosely related repository HEAD.
6. Prefer generating the JFE conversion from the canonical source rather than editing both files.

Until this is done, the claim in the JFE highlights that “all headline values are tied to machine-readable result bundles” is aspirational rather than demonstrated by the current manuscript.

---

## Major Comment 2 — The objective-family robustness claim exceeds the completed analysis

At L346–L358 the manuscript states:

> “across caffeine, trigonelline and 5-CQA and both varieties the 10%-near-optimal rate set spans 31–76%...”

The committed `PAPER_A_P0-5_RESULTS.md` reports four panels:

- Arabica caffeine;
- Arabica trigonelline;
- Arabica 5-CQA;
- Robusta caffeine.

It then explicitly says that **Robusta trigonelline and Robusta 5-CQA are owed**. Therefore, the phrase “all three solutes and both varieties” is unsupported in the present result set.

This is a submission-blocking scope error because the robustness analysis is used to rebut a central methodological criticism. Two acceptable resolutions exist:

1. **Run and archive the two missing panels**, regenerate the result bundle, and report all six consistently; or
2. Narrow the manuscript to: “Across the four evaluated panels (all three Arabica solutes and Robusta caffeine)…” and state that the two remaining Robusta panels are not yet evaluated.

The first option is preferable if inexpensive. The second is scientifically honest and sufficient if runtime or data constraints prevent completion.

Also revise the sentence “a well-identified rate would not [move with the loss].” Different loss functions can produce different point estimates under model discrepancy, outliers, or different implicit error models even when a parameter is reasonably estimable. The defensible statement is:

> “The substantial loss-dependent shift in the point minimum, together with the broad boundary-reaching near-optimal sets, provides additional evidence that rate localization is weak under plausible objective choices.”

---

## Major Comment 3 — “Coverage-calibrated” is not justified by the reported bootstrap

The new out-of-bag bootstrap is a useful addition. It resamples condition clusters, refits the level and rate on in-bag conditions, and scores out-of-bag conditions. That is much better than resampling already-computed fold residuals.

However, the manuscript repeatedly calls the resulting percentile interval **coverage-calibrated**. Repeating the fit does not by itself calibrate coverage. Coverage calibration would normally require a simulation study or another procedure showing that the interval attains its nominal coverage under a specified data-generating process. Nothing in the manuscript or result note demonstrates that.

Recommended terminology:

> **condition-cluster out-of-bag refit bootstrap interval**

or

> **refit-in-bootstrap out-of-bag percentile interval**

Additional cautions are needed:

- There are only nine temperature–pressure clusters per group. A percentile bootstrap with so few clusters is an exploratory uncertainty summary, not a high-precision confidence statement.
- The paper should report the 599/600 effective replicates and the reason one draw had no out-of-bag observations.
- The interval estimates a somewhat different prediction setting from single-condition LOCO because each out-of-bag set commonly contains several conditions. The manuscript notes this, but the estimand should be named explicitly in Methods.
- Consider a cluster jackknife or leave-one-cluster sensitivity table as a transparent complement. A BCa interval may be considered, but the main need is honest naming, not more numerical sophistication.

The model-versus-null clustered bootstrap is also best described as a **paired clustered resampling sensitivity analysis** unless a full sampling model is specified. The primary interval [−0.73, +0.03] percentage points is appropriately interpreted as including zero. The coarser six-group interval barely excluding zero should not be used to rescue a significance claim.

---

## Major Comment 4 — The Methods section remains dependent on the repository

The Methods section has improved labels and numbering, but a reader cannot reproduce the analysis from the article. It names the model and gives a verbal description, yet omits the central equations and estimands.

At minimum, add the following.

### 4.1 Governing-model summary

Provide a compact equation set or a clearly cited reduced formulation showing:

- the liquid- and solid-phase state variables;
- advection/dispersion or transport terms retained;
- solid-to-liquid transfer term;
- equilibrium/partition relation;
- the Sherwood correlation and exactly how `rate_scale` multiplies A1/A2;
- initial and boundary conditions;
- spatial and temporal domains;
- whether the two grain classes share or differ in each parameter.

The article need not reproduce every solver implementation detail, but “a two-grain, multi-solute one-dimensional PDE” is not enough for a methods paper whose conclusion depends on parameter roles.

### 4.2 Explicit observation operators

The paper's real organizing concept is the observation map. Write it mathematically. For example:

\[
C_{\mathrm{cup}}(\theta)
= \frac{\int_0^{t_{\mathrm{end}}} Q(t)\,C_{\mathrm{out}}(t;\theta)\,dt}
       {\int_0^{t_{\mathrm{end}}} Q(t)\,dt},
\]

and for fraction \(j\),

\[
C_j(\theta)
= \frac{\int_{t_{j-1}}^{t_j} Q(t)\,C_{\mathrm{out}}(t;\theta)\,dt}
       {\int_{t_{j-1}}^{t_j} Q(t)\,dt}.
\]

Then define the sampled-fraction aggregate separately. This makes the paper's claim transparent: the cup applies one integration operator, while fractions preserve multiple temporal contrasts.

### 4.3 Profile formulation

State the separable form explicitly:

\[
\hat y_i(I,k)=I f_i(k),
\qquad
J_{\mathrm{prof}}(k)=\min_I \sum_i \rho\!\left(I f_i(k)-y_i\right),
\]

where \(I\) is the inventory level, \(k\) the rate multiplier, and \(\rho\) the chosen loss. Give the closed-form least-squares level and the exact weighted-median result for MAPE, with either a short derivation or a supplement reference.

### 4.4 Dataset-role table

Add one table with columns:

- campaign;
- rig/coffee/basket;
- observable;
- number of conditions/replicates;
- role in this paper;
- parameters fitted to it;
- what is held out;
- evidence label;
- key limitation.

This one table could replace much of §3.6 and prevent “external,” “within-campaign,” and “in-sample” from being confused.

### 4.5 Parameter and unit table

List every fitted/frozen parameter used in Paper 1, its unit, physical basis, source, bound/domain, and whether it is estimated globally, per solute, per variety, or per grind. The unresolved physical basis of `c_s0` must be explicit. Do not rely on code identifiers alone.

### 4.6 Numerical and statistical protocol

State:

- all rate grids and domain bounds;
- level bounds, if any;
- Hessian finite-difference step and scaling;
- threshold family (2/5/10/20%);
- which objective is primary for prediction and which is diagnostic;
- how macro-averaging is performed;
- bootstrap cluster units, seed, replicate count, skipped draws, and estimands;
- how missing replicate uncertainty is handled;
- all external-trajectory nuisance assumptions.

The code can remain the executable supplement, but the article must define the scientific analysis without requiring a reader to inspect function names.

---

## Major Comment 5 — Figure 2 contradicts the dimensional audit

The prose now correctly states that the Angeloni Table 7 assay cannot provide a secure quantitative rate constraint because the dry-coffee mass basis is mapped to a volume concentration under an undefended density convention, while the model's `c_s0` basis is itself not independently anchored.

Figure 2 nevertheless draws the Table 7 inventory as a thin, precise horizontal line and labels it simply “Table 7 inventory.” Visually, this line crosses the profile valley at a seemingly definite rate and therefore restores exactly the interpretation the audit withdrew. The caption further calls it “the independent roasted-and-ground inventory assay” without foregrounding the same-campaign and basis-mismatch limitations.

Recommended options, in order:

1. **Remove the Table 7 line from the main Figure 2.** Discuss the qualitative design lesson in text or supplement.
2. If retained, replace it with a broad basis-sensitivity band covering the plausible 4.8–16.3 mg mL⁻¹ range and label it **“illustrative basis range; not a quantitative model constraint.”**
3. If the broad band overwhelms the plot, show a small inset demonstrating why the intersection is basis-dependent rather than presenting an apparent tie-breaker.

Also replace “independent inventory assay” with:

> “orthogonal solid-inventory measurement from the same Angeloni campaign”

The word “independent” is reserved elsewhere for genuinely separate rig/coffee campaigns and should not be used ambiguously here.

---

## Major Comment 6 — Repair the study-design figure and evidence flow

Figure 1 is conceptually useful, but its arrows are not scientifically correct. The arrow into the Waszkiewicz box descends from the Angeloni optimal-grind target-recalibration box. That implies that the external TDS shape test uses or inherits the Angeloni recalibration. The code and prose instead state that Pannusch TDS kinetics are frozen and a Waszkiewicz-specific level is profiled at each candidate rate.

Redraw the flow as follows:

- **Schmieder fractions → Pannusch calibration**
  - branch A: source-campaign fraction-versus-cup localization;
  - branch B: same-model exact-cup simulation;
  - branch C: Angeloni target recalibration → O-condition CV → C/F holdout;
  - branch D: Waszkiewicz target-level-profiled external shape test.
- Table 7 should connect laterally to the Angeloni profile as a same-campaign orthogonal measurement, not as validation after C/F prediction.

“Arrows denote analysis order, not causal validation” in the caption does not solve a wrong data/parameter dependency. The diagram should depict the actual dependency graph.

---

## Major Comment 7 — Complete the literature work and remove the process note

Lines 54–59 are an editorial note about DOI collation, scoping-search status, and a future Scopus/Web of Science query. It should not appear in the manuscript. The current literature directory confirms that the evidence matrix is not populated and that the indexed database search is a submission gate. Therefore:

- retain the qualified novelty wording;
- complete and archive the search before submission;
- remove the process note from the article;
- merge the “Coffee lineage and the gap” and “Novelty statement” paragraphs, which currently repeat one another;
- replace the final reference stub with the complete formatted bibliography;
- audit every in-text citation against the bibliography and every DOI against the cited record.

The novelty claim should remain modest:

> “To our knowledge, following the documented search, prior espresso studies have not combined…”

Do not claim general priority beyond the search actually performed.

---

## Major Comment 8 — Remove project-management prose from the journal manuscript

The JFE manuscript still contains many items that belong in the repository, supplement, or change log rather than the article:

- review IDs such as `A2-09`, `A3-13`, `MC4`, `M4`, `M6`, and `MAJ-05`;
- function names such as `transfer_skill_vs_baselines`, `loco_cv_refit`, and `full_cup_simulation_offgrid_noise` in the main narrative;
- status words such as “delivered,” “owed,” and “deferred”;
- discussion of a “tuple-indexing bug”;
- comparisons with “our pre-correction draft” and prior incorrect interpretations;
- handoff references;
- placeholders for authors, affiliations, CRediT roles, funding, conflicts, AI declaration, and references.

The scientific paper should state the final method, result, limitation, and provenance. It should not narrate how the repository arrived there. A concise reproducibility appendix can map article analyses to code functions without interrupting the main argument.

A useful rule is:

> If a phrase helps a developer understand the revision history but does not help a reader understand the final study, remove it from the manuscript.

---

## Major Comment 9 — Fix every section cross-reference

The JFE conversion retained section references from the working draft even though the structures differ. Examples include:

- L43–L45: “§3–§5” and “§6”;
- L160: positive control “§6”;
- L197–L208: transfer test “§5”;
- L214: positive control “§6”;
- L237: formal panel “§4” without subsection precision;
- L254: Waszkiewicz “§6”;
- L261: LOCO “§5”;
- L370–L375: references to §6 and §4;
- L490: “corrected §5 conclusion”;
- L498 and L555: references to §4 and §6;
- most references in the Discussion, Limitations, and Data/code sections.

In the JFE manuscript, the substantive analyses are all in §4, specifically §§4.1–4.4. These references are mechanically wrong and make the paper difficult to follow. Add a linter or convert to named cross-references in the source (for example, `{#sec:temporal}`) and generate numbers during conversion.

---

## 4. Scientific framing and interpretation

## Major Comment 10 — Standardize “weak localization” versus “non-identifiability”

The reviewer brief correctly states the maximum defensible claim: the profile has an interior numerical minimum, but its 10%-tolerance set is broad and right-censored. This is **weak practical localization**, not the absence of a numerical optimum.

The manuscript currently alternates among:

- “practically confounded”;
- “practically non-identifiable”;
- “not a converged interior estimate”;
- “interior numerical minimum”;
- “weakly localized.”

Use one consistent hierarchy:

1. **Numerical result:** an interior point minimum exists for the profiled objective.
2. **Uncertainty/robustness result:** a broad near-optimal set reaches the domain boundary and the point minimum moves under plausible loss choices.
3. **Interpretation:** inventory and rate are weakly separated / weakly localized under the tested design.
4. **Scoped shorthand:** practical non-identifiability may be used only if immediately qualified by the tested model, design, parameter domain, and objective.

Avoid “the fitted rate is not a converged interior estimate.” It is better to say:

> “The point minimum is interior, but it is not a robust or uniquely localized mechanistic estimate because the profiled near-optimal set is broad and right-censored.”

Also avoid treating condition number 1930 or coupling −0.99 as inferentially precise. These are local, scale- and discretization-dependent diagnostics. Report them to two significant figures and provide finite-difference/grid sensitivity in the supplement.

---

## Major Comment 11 — Make the observation operator the article's organizing principle

The strongest version of Paper 1 is not merely “a parameter profile was flat.” It is:

> Different observation operators retain different information about the same extraction process, and model-validation claims must be calibrated to that information content.

That principle unifies all results:

- the unmatched 25 s window produced a misleading cross-grind conclusion;
- a matched whole-cup endpoint produces a broad inventory–rate compensation profile;
- endpoint predictions remain stable along that profile;
- a level-only baseline nearly matches cross-grind endpoint performance;
- fraction windows provide temporal contrasts that move the rate objective more strongly;
- a single cup plus one free level is algebraically uninformative in the one-shot external construction.

Reorganize the paper around **measurement/observation design**, not around the chronology of repository analyses. This would make the work more accessible and more generalizable without overclaiming.

A simple local sensitivity explanation would help lay readers and technical readers alike. If \(y_i=I f_i(k)\), then the log-sensitivities are approximately \(1\) for inventory and \(s_i=\partial\log f_i/\partial\log k\) for rate. When all endpoint observations have nearly the same \(s_i\), the two sensitivity columns are nearly collinear. Fractions or deliberately varied residence times help because they make \(s_i\) vary. This provides a compact mathematical bridge between the figures and the experimental-design conclusion.

---

## Major Comment 12 — Clarify the cross-grind estimand and avoid “transfer” shorthand

The revised manuscript now mostly handles this well. The relevant result is:

- fit a target-specific level and rate on Angeloni optimal-grind observations;
- freeze them;
- predict coarse/fine conditions within the **same Angeloni campaign** using inferred grind-specific hydraulics;
- compare against an O-trained level-only constant.

This is not external mechanistic transfer. It is a **within-campaign cross-grind prediction test after target-specific calibration**. Use that phrase consistently in section titles, figure titles, captions, and discussion.

The current result is interesting precisely because it separates three properties:

- acceptable absolute error;
- parameter localization;
- incremental skill over a simple baseline.

The paired clustered bootstrap strengthens the finding. Put the primary ΔMAPE result in the abstract:

> model minus constant = −0.36 percentage points; primary clustered 95% interval [−0.73, +0.03].

Then use “no resolvable improvement under the primary clustered resampling scheme,” not “no skill” as an absolute statement.

The shared-parameter compatibility analysis should remain secondary. It is in-sample, and the comparator models are non-nested and have unequal flexibility. It does not demonstrate transfer or select a mechanistic model.

---

## Major Comment 13 — Treat the 40 g to 40 mL conversion as an estimand choice, not a minor density correction

The matched-endpoint correction is one of the most important improvements in the paper. Preserve it. But the current wording still risks making the conversion sound more secure than it is.

Points to address:

- Cite the claimed 0.98–1.00 g mL⁻¹ hot-beverage density range or remove it.
- Espresso beverage mass, liquid volume, dissolved solids, gas/crema, and source collection practice are not necessarily interchangeable under a water-density approximation.
- The source's ±2 g tolerance does not automatically validate a 40 mL operator.
- The endpoint sensitivity demonstrates that the choice matters by about five percentage points in the named-solute blind result; this is not negligible.

If the solver can integrate to collected mass using a declared density model, use a mass endpoint. Otherwise state plainly:

> “Because the source reports beverage mass and the solver terminates on volume, 40 mL is used as a matched-volume proxy for the nominal 40 g endpoint. The resulting estimand is sensitivity-tested at 38, 40, and 42 mL.”

Do not describe the proxy as “the same endpoint as the observations” without the qualification.

---

## Major Comment 14 — The external Waszkiewicz panel is useful only as a carefully bounded stress test

The external panel is much more honestly framed than before. Its defensible contribution is narrow:

- a different rig and coffee;
- optical TDS rather than named solutes;
- one grind and one averaged trajectory;
- measured flow trace;
- target-specific multiplicative level fitted at every rate;
- shallow profile minimum around rate 0.4;
- high minimum MAPE around 27%;
- single-cup profile flat algebraically because one level fits one scalar.

The manuscript should say “the trajectory produces a shallow rate preference under the tested model/operator” rather than “constrains the kinetic rate” without qualification.

Several load-bearing implementation choices appear in code but are not adequately described in Methods:

- 12 public bins versus 14 bins in the article figure;
- time-origin offsets of 0, 2, and 4 s;
- omission/inclusion of the first bin;
- assumed brew temperature;
- pre-drip flow floor;
- isotonic projection of the non-monotone cumulative-mass trace before constructing nonnegative bin masses;
- mass-weighted cup construction;
- sensitivity of the result to temperature and flow-floor choices.

These data-processing steps should be disclosed in a concise external-panel Methods subsection and accompanied by a source-data/processing diagnostic in the supplement.

MAPE also deserves care because early TDS fractions can be small. Report an alternative shape loss—such as concentration-scale SSE after level profiling, or a prespecified weighted/robust loss—to show that the shallow preference is not an early-bin percentage-error artifact.

If article length must be reduced, retain the external result as a short stress-test paragraph and move the full profile, operator sensitivity, and data-processing audit to the supplement. It should not carry the main proof of the paper; the source-campaign fraction comparison and observation-operator mathematics already establish the methodological point more cleanly.

---

## Major Comment 15 — Keep the exact-cup simulation didactic and concise

The exact-integral simulation answers an important objection: the empirical “aggregate” made from six retained windows is not a complete cup. The simulation shows that the fraction-versus-cup contrast persists under the same model with exact integration.

The manuscript appropriately labels this an inverse crime and not empirical validation. Preserve that caveat. However, the current treatment is too long and risks allowing a synthetic best-case result to dominate the article.

Recommended main-text content:

- one short Methods paragraph;
- one result paragraph;
- one panel in the temporal-resolution figure;
- a clear statement that same-model simulation demonstrates information loss **under the assumed model**, not the information content of every real espresso cup.

Move off-grid truth, heteroscedastic noise, correlated shot effects, and model-discrepancy dose-response details to the supplement. Those controls are useful but do not need to interrupt the primary narrative.

---

## Major Comment 16 — Refine the objective and profile reporting

The paper uses several related but distinct diagnostics:

- MAPE for prediction;
- SSE for local curvature/Hessian analysis;
- relative-L2 and Huber sensitivity objectives;
- profile range ratios;
- 10%-near-optimal set widths;
- Jaccard overlap between SSE and MAPE sets.

This is scientifically rich but too complicated in the current narrative. Establish a hierarchy:

1. **Primary localization display:** normalized profiled objective versus rate and the declared near-optimal set.
2. **Primary prediction metric:** named-solute macro-MAPE.
3. **Robustness:** alternative objective family and threshold family in a supplement table.
4. **Local diagnostic:** log-Hessian condition number/coupling, clearly secondary.
5. **Profile range ratio:** descriptive only, because it depends strongly on tested boundaries and on selecting the larger edge value.

The phrase “not a coarse-grid or chosen-domain artefact” at L360–L368 is too strong. The analysis shows persistence across the tested grid densities and alternative domains, but the set remains boundary-censored, so domain dependence is not eliminated. Say:

> “The broad, boundary-reaching profile persists across the tested grid densities and the narrower and wider domains.”

The 10% threshold is declared rather than inferential. Show 2/5/10/20% sensitivity in the supplement and avoid allowing one arbitrary threshold to sound like a confidence region.

---

## 5. Section-by-section review

## 5.1 Title page and abstract — L1–L13

### Strengths

- The abstract now states the central compensation result.
- It separates endpoint accuracy from baseline-relative skill.
- It acknowledges that the shared multigrind fit is in-sample.
- It scopes the external trajectory as shallow and high-error.
- It gives the correct high-level reporting principle.

### Required changes

1. Replace the title as recommended above.
2. Clarify that the Angeloni campaign is used for **target-specific recalibration** and that the C/F test is a within-campaign holdout, not simply “refitted to an independent endpoint campaign.”
3. Include the primary clustered ΔMAPE interval, because it is more informative than 8.2% versus 8.6% alone.
4. State that the broad rate set is right-censored at the upper tested boundary.
5. Avoid implying that the empirical source “whole-cup aggregate” is a true cup; the exact cup result is same-model simulation.
6. Replace “kinetic parameter localization” with plain language on separating extractable content from extraction rate.
7. Consider removing “porous media” from keywords unless the manuscript presents enough porous-media formulation for that keyword to be useful.

A proposed rewrite appears in §9.

---

## 5.2 Introduction — L16–L48

### Strengths

- The inventory-versus-rate problem is explained in relatively accessible terms.
- The scope qualifier at L38–L41 is excellent and should remain.
- The distinction between parameter values and a near-flat valley is clear.

### Required changes

- Support or soften the broad claim that cross-dataset checks are “almost always” whole-cup because “those are what most campaigns report.” A few cited examples or “many available campaigns” would be safer.
- Define “inventory” immediately as **extractable content available in the coffee** and use the accessible phrase before the modeling shorthand.
- Replace “a non-identifiable curve fit masquerading as [a transferred calibration]” with less adversarial language. The paper is strongest when analytical rather than prosecutorial.
- Correct the section references.
- End the Introduction with explicit research questions or hypotheses, for example:
  1. How strongly do whole-cup endpoints separate inventory and rate?
  2. Does acceptable cross-grind endpoint error exceed a level-only baseline?
  3. Do time-resolved observations provide stronger rate information?

---

## 5.3 Literature context — L52–L133

### Strengths

- The distinction between structural and practical identifiability is well made.
- The paper avoids claiming a new general identifiability method.
- Reaction/transport confounding and experimental design provide useful cross-domain context.
- The coffee-model lineage is much more complete than before.

### Required changes

- Delete the italic editorial note at L54–L59.
- Compress the section. It currently reads like a mini-review before a relatively focused case study.
- Merge “Coffee lineage and the gap” with “Novelty statement”; they repeat the same claim.
- Explain “sloppiness,” “profile objective,” and “inverse-curvature coupling” in plain language or reserve them for Methods.
- Complete the indexed search and final bibliography before submission.
- Avoid a novelty claim that depends on four analytical categories being absent in exactly the same combination; describe the applied gap without constructing an overly bespoke novelty test.

---

## 5.4 Methods — L135–L242

### Model, L137–L152

The verbal model description is not sufficient. Add governing equations, initial/boundary conditions, parameter roles, and units. Explain why exact linearity in `c_s0` holds in the final observation. Replace code formatting with mathematical symbols and define repository names only in the reproducibility supplement.

### Data, L154–L172

Add a dataset-role table. Clarify:

- whether the 66 Angeloni records include the full 3×3×3 grid plus off-grid points and how the 33-per-variety count is constructed;
- which values are duplicate means versus individual runs;
- that source-level RSD ranges do not provide condition-specific named-solute weights;
- that Table 7 is an orthogonal measurement from the same campaign;
- that “optimal/coarse/fine” are source granulometry labels rather than universal particle-size classes.

### Endpoint and hydraulics, L174–L200

Separate three issues:

1. mass-to-volume endpoint proxy;
2. pressure-to-flow map used in blind/source comparisons;
3. inferred grind-specific hydraulic map used in O→C/F prediction.

Give equations and parameter values for each. The present paragraph is too dense and mixes assumptions, sensitivity results, and interpretation.

Correct the endpoint numbers to the named-solute contract. Do not report stale proxy-inclusive values as the primary result.

### Fitting protocol, L202–L210

State the full hierarchy clearly: per variety × named solute, O on-grid fit, O off-grid check, LOCO refits, C/F prediction, shared multigrind reconstruction, and external target-level profiling. Define which parameters are global or group-specific. Explain macro-averaging.

### Identifiability metric, L212–L223

This section currently defines only the profile range ratio used in the positive control. It should define the main profiled objective, near-optimal set, right-censoring, local Hessian diagnostic, and objective-family sensitivity. The current title “Identifiability metric” is misleading because there is not one metric.

Suggested title:

> **Profile analysis and localization diagnostics**

### Evidence vocabulary, L225–L242

The discipline is valuable, but a full taxonomy in the Methods reads like internal governance. Replace it with the dataset-role table and one short paragraph defining calibration, within-campaign holdout, and external shape test. Put the longer evidence vocabulary in the supplement.

---

## 5.5 Results 4.1 — L248–L284

This section contains the most obvious numerical error. It declares a named-solute primary convention and immediately reports a proxy-inclusive 22.6% headline. Correct the table to:

- named-solute blind macro-MAPE 26.3%;
- proxy-inclusive value 22.7%, separate;
- named-solute crude/refined values 26.8% and 26.3%;
- named-solute endpoint range 23.8–28.8%.

The “three successively stricter tests” language is useful, but “strictness” mixes different estimands. Consider “three progressively more target-adapted comparisons.”

Remove historical discussion of the earlier draft. State the scientific result directly:

> Matching the collection endpoint materially reduces the blind residual relative to an unmatched fixed-time comparison, while the tested flow-map refinement changes the matched-endpoint error by only about 0.5 percentage points.

Do not imply that the residual is decomposed into inventory and kinetics; the section correctly lists alternative sources and should keep that caution.

---

## 5.6 Results 4.2 — L286–L371

This is the scientific core and should become shorter, cleaner, and more prominent.

### Preserve

- separable level/rate explanation;
- broad right-censored profile;
- interior numerical minimum versus weak localization distinction;
- local condition number/coupling as secondary geometry diagnostics;
- objective-family and grid/domain robustness;
- qualitative-only Table 7 design lesson.

### Correct

- “not a converged interior estimate” contradiction;
- unsupported all-six objective-family claim;
- “a well-identified rate would not move with the loss” overstatement;
- “not a chosen-domain artefact” overstatement;
- review IDs, bug history, and code names;
- Table 7 visual treatment.

### Simplify

A main-text presentation can be reduced to:

1. one equation for level-rate separability;
2. Figure 2 with normalized surface/profile;
3. broad/right-censored set and local condition number;
4. one sentence that the pattern persists across tested objective families and domains;
5. Table 7 only as a qualitative experimental-design example.

Move Jaccard values, detailed grid counts, threshold families, and all solute/variety panels to the supplement.

---

## 5.7 Results 4.3 — L373–L494

This section now contains several valuable analyses, but it is overloaded.

### Recommended hierarchy

1. **Primary:** O-calibrated mechanistic prediction versus O-trained level-only constant on C/F.
2. **Primary uncertainty:** paired clustered ΔMAPE interval.
3. **Secondary:** condition-wise prediction stability across the near-optimal profile set.
4. **Secondary:** LOCO within O and refit-in-bootstrap interval.
5. **Supplementary:** shared-parameter compatibility and non-nested comparator ladder.
6. **Supplementary:** geometry and ±20% flow-map sensitivity.

The result should lead with the sharp finding:

> Absolute cross-grind error is modest, but the mechanistic model's pooled advantage over a level-only constant is only −0.36 percentage points and the primary clustered interval includes zero.

This is clearer than several paragraphs of “transfer” framing.

Replace “coverage-calibrated” throughout. Remove the sentence saying the analysis is deferred. State that the six-group bootstrap and condition-within-group bootstrap differ at the zero boundary, which reinforces the marginal nature of the advantage.

The comparator ladder is not a model-selection analysis. Its unequal flexibility and in-sample scoring must be in the first sentence, not only later. Figure 5 should use “comparator,” not “reduced-model,” and probably move to the supplement.

---

## 5.8 Results 4.4 — L496–L592

This section contains three different evidence tiers:

1. empirical source-campaign fractions versus a sampled-fraction aggregate;
2. same-model exact-cup simulation;
3. external target-level-profiled TDS trajectory.

They should not be narrated as one continuous validation sequence. Use three subheadings and begin each with the evidence type.

### Source fractions

The six-window aggregate is not a whole cup. The manuscript now says this clearly. Consider calling it a **sampled-window aggregate** everywhere to prevent shorthand drift.

### Exact-cup simulation

Retain as a didactic information-content control, shorten in the main text, and move robustness variants to the supplement.

### External TDS

Add the missing operator-processing details and alternative-loss sensitivity. Replace “does constrain the kinetic rate” with “produces a shallow rate-dependent objective preference.” Keep the high 27% minimum error prominent.

The single-cup zero-MAPE line in Figure 6 is potentially misleading. It represents exact fitting by construction, not predictive success. Plot a normalized flat objective at an arbitrary reference level or label the panel “not estimable: one scalar, one fitted level” rather than showing a visually perfect zero-error model.

---

## 5.9 Discussion — L594–L636

The Discussion contains the correct conceptual distinctions. The “four distinct properties” paragraph is strong and should remain central:

- parameter localization;
- endpoint accuracy;
- incremental benchmark skill;
- cross-context prediction.

Required changes:

- correct section references;
- remove review IDs and prior-draft narrative;
- avoid “transferred calibration” shorthand where the calibration was target-specific;
- distinguish prediction stability along a profile from evidence that the model mechanism is correct;
- expand the practical implications for espresso experimentation and model development.

The experimental-design recommendations should be concrete:

- measure early, middle, and late fractions;
- record mass/flow traces synchronized to composition samples;
- measure extractable inventory on the same coffee and physical basis as the model state;
- vary residence time, flow, temperature, and endpoint deliberately to rotate sensitivity directions;
- retain replicate-level uncertainty;
- use multiple coffees, grinders/particle-size distributions, and rigs;
- predeclare simple baselines and held-out contexts.

This is where the paper can connect directly to better espresso modeling and process/equipment optimization without making the manuscript inaccessible.

---

## 5.10 Limitations and future work — L638–L670

This section is written as a project tracker rather than journal prose. It should be replaced with four compact paragraphs:

1. **Data uncertainty and replication:** no condition-specific named-solute replicate weights.
2. **Hydraulics and endpoint:** inferred flow maps and mass-to-volume proxy.
3. **Model and parameterization:** fitted inventory basis, fixed model structure, model discrepancy, limited external TDS evidence.
4. **Generalizability:** one model lineage, limited coffees/rigs/grinds, no independent named-solute multigrind fraction campaign.

Do not list analyses as “delivered” or “owed.” Do not repeat numerical results already in Results. Do not call Figure 3 residual plots owed when they exist.

---

## 5.11 Conclusions — L672–L674

The conclusion is concise and mostly defensible. Improve it by:

- replacing “permits broad compensation” with “provided only weak separation” to avoid implying mathematical permission in all endpoint designs;
- explicitly stating that the cross-grind result is within-campaign after target-specific calibration;
- stating the primary null comparison in words, not adding many numbers;
- distinguishing the external TDS shape test from named-solute validation;
- ending with the observation-design principle.

Suggested final sentence:

> “For espresso inverse problems, the measurement design should therefore be judged not only by how accurately a model predicts the final cup, but by whether it creates distinct information about the physical quantities the model is intended to estimate.”

---

## 5.12 Data/code availability, declarations, figures, and references — L676–L725

### Data and code

The repository mapping is valuable but too function-heavy for the article. Replace the long function list with:

- repository URL;
- archival DOI/tag;
- exact release identifier;
- environment/lock file;
- data provenance and licensing statement;
- figure/source-data archive;
- a supplement table mapping analyses to scripts.

A submission should not point only to a mutable `main` branch. Create a tagged release and archival record with the exact result bundle and figure sources.

### Declarations

All placeholders must be completed before submission: authors, affiliations, corresponding author, CRediT roles, funding, conflicts, and journal-compliant AI declaration.

### Figures

Do not merely say “see another file.” The submission package should include the final numbered captions and figures in the venue format, with consistent main-versus-supplement designation.

### References

The reference section is currently a build instruction, not a bibliography. This is a submission blocker.

---

## 6. Figure-by-figure review

## Figure 1 — Study and evidence design

### What works

- The lane structure makes the evidence hierarchy visible.
- It correctly labels Angeloni C/F as within-campaign and Waszkiewicz as genuinely external.
- The color legend is useful.

### Required changes

- Correct the arrow into Waszkiewicz; it should branch from the Pannusch model/kinetics, not the Angeloni O recalibration.
- Make Table 7 connect to the Angeloni profile/localization analysis rather than appear as the terminal validation step after C/F.
- Replace “campaign-accurate categories” in the title with a reader-facing title such as “Study design and use of each dataset.”
- Increase font size and simplify the legend for print.
- Spell out O/C/F once or avoid abbreviations in the schematic.

## Figure 2 — Inventory–rate objective surface

### What works

- This is the most important scientific figure.
- The normalized SSE surface and profiled curve show the compensation valley clearly.
- Right-censoring is visible.
- Caffeine and trigonelline provide useful contrast.

### Required changes

- Remove or replace the precise Table 7 line with a basis-sensitivity band and explicit qualitative-only label.
- Reduce false precision in condition numbers and coupling values.
- Improve legend contrast; some text is hard to read on the dark contour.
- Explain the y-axis basis. Numerically g L⁻¹ equals mg mL⁻¹, but the physical volume basis of the model inventory is unresolved.
- Put objective-family panels or threshold sensitivity in the supplement rather than further crowding this figure.

## Figure 3 — Leave-one-condition-out holdouts

### What works

- The residual panels answer an earlier review request.
- The figure reveals the Robusta 5-CQA outliers hidden by the pooled mean.
- It is a useful within-campaign diagnostic.

### Required changes

- Shorten the figure title; “not a CI” belongs in the caption.
- Increase text and marker size for journal-column reproduction.
- Clarify whether any plotted interval corresponds to the descriptive fold resampling or the refit-in-bootstrap OOB interval; do not let the caption conflate them.
- Remove the manuscript statement that per-condition residual plots remain owed.

## Figure 4 — Cross-grind prediction versus level-only baseline

### What works

- It places the null benchmark beside the mechanistic model.
- It shows profile-set prediction envelopes rather than only a point estimate.
- It makes the 50/108 worse-than-constant result visible.

### Required changes

- Rename “transfer” to **within-campaign cross-grind prediction**.
- The legends and annotations overlap the data in panels (a) and (b) and are not publication-ready.
- Panel (c) labels are too abbreviated and small; use a table-like dot/bar plot with full or clearly decoded labels.
- Show the pooled model and constant values and clustered ΔMAPE interval explicitly.
- Explain the finite discrete profile set visually without placing dense text over the plotting area.

## Figure 5 — Shared-parameter compatibility and comparator ladder

### What works

- The heatmaps communicate where the cost of sharing occurs.
- The 0/6 comparison against per-grind constants is informative.

### Required changes

- Replace “reduced-model ladder” with **non-nested in-sample comparator ladder**.
- State in the figure—not only the caption—that models have unequal flexibility and are scored on their own fit data.
- The figure is too dense for the main article. Move it to the supplement unless the shared-parameter result becomes a central research question.
- Increase axis/legend text and avoid unexplained abbreviations.

## Figure 6 — Temporal resolution and rate profiles

### What works

- This figure carries the positive message of the paper: temporal resolution changes the objective geometry.
- The source, simulation, and external tiers are visibly distinguished.
- The external high-error minimum is honestly annotated.

### Required changes

- Do not plot the external single-cup line at zero without a dominant “exactly fitted by construction—not validation” label. Zero MAPE visually suggests perfect prediction.
- Consider plotting normalized profile increase in a second row or using a common localization measure. Raw MAPE mixes fit quality and profile sharpness.
- Separate the external panel more strongly; it uses a different observable, campaign, fitting rule, and error level.
- Define the shaded bands exactly in the caption.
- Increase legend size and avoid requiring the first panel's legend to decode all subsequent panels.

## Figure 7 — Per-group diagnostics

### What works

- It shows that inventory matching does not uniformly remove residuals.
- It labels correlations as cross-condition rather than temporal.

### Required changes

- The figure title and panel titles overlap visibly.
- TDS is included beside named solutes despite the primary observable convention; label it as an aggregate proxy and keep it separate.
- With n=9 per group, correlations are highly descriptive. Add uncertainty or avoid emphasizing their magnitudes.
- Keep this as a supplement diagnostic.

## Figure 8 — Blind residuals versus conditions

### What works

- It reveals large pre-fit group offsets.
- It motivates target-level recalibration.

### Required changes

- The current layout is extremely compressed and difficult to read.
- The title contains an internal review ID and an “owed” note.
- It does not show the post-level-fit within-group structure that would address the key question.
- Either regenerate it as a proper supplementary residual diagnostic after level fitting or remove it.

---

## 7. Recommended manuscript architecture

The current JFE manuscript is approximately 7,500 words before a real reference list and contains too many parallel diagnostics. A more direct structure would be:

## 1. Introduction

- practical problem;
- why whole-cup validation can be misleading;
- three research questions;
- scoped contribution.

## 2. Model, datasets, and observation operators

### 2.1 Espresso extraction model and estimated quantities

Define extractable content/inventory and rate multiplier in equations and plain language.

### 2.2 Datasets and their analytical roles

One study-design table.

### 2.3 Whole-cup, fraction, and sampled-window observation operators

Explicit equations.

### 2.4 Profile, prediction, baseline, and uncertainty methods

One coherent statistical protocol.

## 3. Whole-cup endpoints weakly separate extractable content from rate

- matched endpoint;
- blind residual briefly;
- profile valley;
- objective/domain robustness;
- Table 7 qualitative lesson.

**Main figures:** revised Figure 1 and Figure 2.

## 4. Cross-grind endpoint prediction adds little over a level-only baseline

- O→C/F within-campaign holdout;
- primary null comparison and clustered interval;
- prediction stability along profile;
- LOCO/OOB uncertainty in a concise paragraph.

**Main figure:** redesigned Figure 4, optionally with the most useful panel from Figure 3.

## 5. Time-resolved measurements provide stronger rate information

- source fractions versus sampled aggregate;
- concise exact-cup simulation;
- concise external TDS stress test.

**Main figure:** revised Figure 6.

## 6. Discussion

- localization versus prediction versus benchmark skill;
- implications for espresso experiments and model validation;
- limitations/generalizability.

## 7. Conclusions

### Supplement

- full governing equations/numerical details if too long for main Methods;
- all six objective-family panels;
- threshold and grid/domain sensitivity;
- Hessian-step sensitivity;
- full LOCO and OOB tables;
- comparator ladder and shared-parameter heatmaps;
- geometry/flow-map sensitivity;
- external trajectory processing and alternative loss;
- exact-cup simulation variants;
- residual diagnostics and tidy source data.

---

## 8. Recommended core claim set

Freeze the paper around a small number of claims that can be checked automatically.

### Claim 1 — Whole-cup localization

Under the tested single-grind matched-volume endpoint design, the inventory and rate multiplier are weakly separated: the profiled objective has an interior minimum, but the 10%-near-optimal rate set is broad and right-censored.

### Claim 2 — Cross-grind endpoint prediction

After target-specific O-grind calibration, within-campaign C/F absolute errors are modest, but the mechanistic model's pooled advantage over an O-trained level-only constant is only about 0.36 percentage points and is not distinguishable from zero under the primary clustered resampling scheme.

### Claim 3 — Prediction stability does not imply parameter identification

Predictions vary much less than the fitted inventory/rate decomposition across the near-optimal profile set.

### Claim 4 — Temporal resolution

Fraction-resolved observations move the rate-profile objective more strongly than sampled or exact cup aggregates under the tested model and operators.

### Claim 5 — External scope

An external, target-level-profiled TDS trajectory produces only a shallow, high-error rate preference; its single integrated cup is flat algebraically and is not an empirical validation of the kinetic rate.

Every abstract sentence, table, figure, highlight, and conclusion should map to one of these claims or be removed from the main paper.

---

## 9. Proposed abstract rewrite

**Whole-cup espresso measurements can be predicted accurately even when a model's extractable-content and extraction-rate parameters are only weakly separated. We examined this problem in a multi-solute espresso extraction model previously calibrated to fraction-resolved data and then recalibrated to optimal-grind whole-cup observations from a different experimental campaign. Model predictions were mapped to a 40 mL matched-volume proxy for the reported 40 g beverage endpoint. At each candidate mass-transfer-rate multiplier, a multiplicative extractable-inventory level was re-estimated and the resulting objective was profiled. The profile had an interior numerical minimum, but its 10%-near-optimal set extended from approximately 0.4 to the upper tested rate boundary, indicating broad, right-censored inventory–rate compensation. After optimal-grind calibration, coarse- and fine-grind predictions had pooled mean absolute percentage error of 8.2%, compared with 8.6% for an optimal-grind level-only constant. The paired difference was −0.36 percentage points, with a primary clustered 95% resampling interval of −0.73 to +0.03 percentage points, and the mechanistic model was worse on 50 of 108 held-out points. Thus, modest endpoint error provided no resolvable improvement over a transferred concentration level under the primary resampling scheme. Fraction-resolved source-campaign observations produced substantially sharper rate profiles than sampled or simulated whole-cup aggregates. A separate, target-level-profiled dissolved-solids trajectory from an external rig produced only a shallow, high-error rate preference, while its single-cup objective was flat by construction. For espresso inverse problems, matched observation windows are necessary but not sufficient: parameter localization, prediction error, skill over a simple baseline, and cross-context evidence should be evaluated separately.**

This version is deliberately explicit about:

- target-specific recalibration;
- within-campaign held-out prediction;
- right-censoring;
- the clustered null comparison;
- the distinction between empirical fractions, same-model cup simulation, and external target-profiled shape evidence.

---

## 10. Priority action list

## P0 — Submission-blocking

1. **Freeze one quantitative result contract** and regenerate the JFE manuscript, tables, highlights, and figure annotations from it.
2. **Correct the primary blind values** to named-solute 26.3% and the corresponding 26.8→26.3 flow comparison; report the 22.7% proxy-inclusive value separately.
3. **Correct endpoint sensitivity** to the named-solute 23.8→28.8% range or explicitly identify any different estimand.
4. **Resolve all deferred/delivered contradictions**, especially the out-of-bag refit bootstrap and residual plots.
5. **Run the two missing Robusta objective-family panels or narrow the all-six claim.**
6. **Replace “coverage-calibrated”** with a defensible bootstrap description unless an actual coverage study is added.
7. **Adopt the new title** and rewrite the abstract around the primary clustered null comparison.
8. **Add standalone Methods equations, dataset-role table, parameter/unit table, and numerical/statistical protocol.**
9. **Remove or redesign the Table 7 line in Figure 2.**
10. **Correct Figure 1's external-analysis dependency arrow.**
11. **Remove review IDs, code-object names, status language, bug history, and prior-draft narrative from the main paper.**
12. **Repair all in-text section references** with an automated cross-reference system.
13. **Complete authorship, declarations, final captions, and bibliography.**
14. **Complete and archive the indexed novelty search** before making the final novelty statement.

## P1 — Scientific presentation

1. Reorganize around the observation operator and the three research questions.
2. Promote the model-versus-null ΔMAPE interval; demote the non-nested comparator ladder.
3. Reduce the main figure set to four or five figures and move diagnostics to the supplement.
4. Add Hessian finite-difference/scaling sensitivity and all objective/threshold panels to the supplement.
5. Add alternative-loss sensitivity and full processing disclosure for the external TDS trajectory.
6. Clarify the mass-versus-volume endpoint estimand and cite/remove the beverage-density claim.
7. Use “weak localization” consistently and reserve “practical non-identifiability” for explicitly scoped statements.
8. Replace raw zero-MAPE visualization of the algebraically fitted external cup with a non-misleading representation.

## P2 — Reproducibility and editorial finish

1. Produce a clean tagged release and archival DOI with exact figures, source data, result contract, and environment lock.
2. Export tidy source data for every figure.
3. Standardize notation, units, solute names, O/C/F labels, and macro-averaging definitions.
4. Perform a copy edit for sentence length, repetition, and accessibility.
5. Verify every citation and DOI and format the reference list for the target journal.
6. Confirm journal word count, highlight length, figure count, graphical-abstract, and AI-declaration requirements at submission time.

---

## 11. Strengths to preserve

1. **The central problem is real and important.** Espresso modelers need to know whether a good cup-level fit identifies physical mechanisms or merely a compensating parameter combination.
2. **The endpoint correction is exemplary.** The paper demonstrates that mismatched observation windows can manufacture a false validation conclusion.
3. **The level-only baseline is exactly the right comparator.** It converts a vague claim of “reasonable transfer” into a falsifiable skill question.
4. **The paper now separates parameter localization from predictive stability.** This is one of its most valuable conceptual contributions.
5. **The external result is unusually honest.** A shallow, high-error preference is reported as such rather than sold as validation.
6. **The Table 7 dimensional audit is strong scientific hygiene.** It withdraws an attractive but unsupported quantitative tie-breaker.
7. **The repository contains substantial reproducibility infrastructure.** The next step is to make the manuscript draw from it reliably.
8. **The work has practical experimental-design implications.** Fraction timing, synchronized flow, inventory measurements, replicates, and deliberately varied operating conditions are directly actionable for future espresso research.

---

## 12. Bottom line

Paper 1 now contains a credible and potentially publishable scientific story. Its strongest message is not that whole-cup espresso measurements are useless, nor that the model cannot predict across grind. It is more precise and more useful:

> **A whole-cup endpoint may support stable prediction while providing too little independent information to distinguish extractable content from extraction rate, and acceptable endpoint error may add little over a fitted concentration level. Time-resolved measurements and independent physical constraints are therefore needed when the purpose is to learn mechanism rather than only predict the final cup.**

The current obstacle is manuscript control. A journal reviewer should encounter one set of numbers, one evidence hierarchy, one parameter interpretation, and one final article—not a canonical draft, a venue conversion, a result note, and figures that each preserve a different stage of the revision history. Resolve that coherence problem first. Then simplify the paper around the observation operator, null comparison, and fraction-versus-cup contrast.

With those changes, the work should be much clearer to coffee practitioners and general food-engineering readers while remaining technically rigorous enough for specialists.

---

## Sources reviewed

### Manuscripts and review control

- `docs/submission/PAPER_A_JFE_MANUSCRIPT.md`
- `docs/PAPER_A_DRAFT.md`
- `docs/REVIEWER_BRIEF_PAPER_A.md`
- `docs/paper1_resource/PAPER_1_REVIEW_ACTION_PLAN.md`
- prior external detailed review and its action mapping

### Analysis and uncertainty records

- `docs/paper1_resource/PAPER_A_P0-5_RESULTS.md`
- `docs/paper1_resource/PAPER_A_P0-5_UNCERTAINTY_SCOPE.md`
- `docs/paper1_resource/PAPER_A_TABLE7_UNITS_AUDIT.md`
- `docs/figures/paper_a/results.json`
- `puckworks/validation/slow/angeloni_bracket.py`
- `puckworks/validation/slow/identifiability.py`
- `puckworks/validation/slow/external_waszkiewicz.py`

### Consistency and reproducibility infrastructure

- `tools/paper_a_consistency.py`
- `tests/test_paper_a_consistency.py`
- `puckworks/figures_paper_a.py`
- `docs/figures/PAPER_A_CAPTIONS.md`
- `docs/figures/paper_a/README.md`
- Figures 1–8 at the pinned commit

### Literature and submission materials

- `docs/literature_search/README.md`
- `docs/literature_search/SEARCH_PROTOCOL.md`
- `docs/literature_search/NOVELTY_WORDING_PROVISIONAL.md`
- `docs/literature_search/references.bib`
- `docs/submission/PAPER_A_JFE_HIGHLIGHTS.txt`
