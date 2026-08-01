# Paper 1 — Domain Referee Review

**Manuscript:** *Separating Extractable Content from Extraction Rate in Espresso Models: Limits of Whole-Cup Measurements and the Value of Time-Resolved Data*  
**Target journal:** *Journal of Food Engineering*  
**Repository state reviewed:** `trbrewer/puckworks`, commit `4ab18ad3e6fa8b7185a20b6a10d6de86507be805`  
**Submission surfaces reviewed:**

- `docs/submission/PAPER_A_JFE_MANUSCRIPT.md`
- `docs/submission/PAPER_A_JFE_SUPPLEMENT.md`
- `docs/submission/PAPER_A_JFE_FIGURE_CAPTIONS.md`
- the four image files present in `docs/submission/figures/`
- the Angeloni bioactive-concentration table and the archived transfer-corpus result contract needed to interrogate the headline comparison

**Review posture:** food-engineering and inverse-problem referee review, not repository-assurance review. I have not repeated the known open items excluded by the brief. I did not execute the complete producer/test suite; I read the current manuscript, supplement, captions, figures and result/data artifacts, and I performed one independent, reviewer-side empirical-baseline calculation described in Appendix A.

---

## Recommendation

# **Major revision**

The manuscript is scientifically valuable, unusually candid about what its analyses do and do not establish, and substantially closer to publishable than the length of the findings below may suggest. I do **not** recommend rejection. The corpus is defensible, the observation-operator analysis is strong, the inventory–rate compensation result is credible within the declared model, and the temporal-information section is appropriately tiered and limited.

The paper is nevertheless not ready for *Journal of Food Engineering* in its current form because the principal benchmark does not give the mechanistic predictor and a non-mechanistic predictor equivalent information or flexibility. The reported difference—8.44% versus 8.83% MAPE—is therefore a valid comparison with a deliberately minimal level-only ablation, but not yet an adequate estimate of incremental mechanistic prediction skill. The central comparison also omits calibration/refit variability, and the pooled result hides a decisive grind asymmetry: the model improves on the constant for the coarse grind but is worse for the fine grind.

The paper has reached the point where further claim-policing or assurance infrastructure would add little value. The next revision should add science, not gates.

## Single change that would most improve the paper

Replace the single-constant headline with an **equal-information, optimal-grind-only benchmark panel**, selected and tuned without using coarse/fine outcomes, and propagate the complete calibration-and-comparison procedure through a refit-aware uncertainty analysis. At minimum, the panel should contain:

1. the current level-only constant;
2. the current same-(temperature, pressure) lookup on its valid support;
3. a low-degree empirical response model trained only on the nine optimal-grind conditions, using the same exogenous condition and hydraulic information available to the mechanistic predictor; and
4. the mechanistic predictor.

The revised result should be shown by target grind and by variety–solute group as well as pooled. That single integrated change would resolve the paper's most important scientific ambiguity.

---

## Overall scientific assessment

The strongest contribution is not a claim that this particular reduced model has transferred an espresso extraction mechanism. It is a carefully worked case showing that four commonly conflated diagnostics must be separated: the localization of fitted parameters, the stability of predictions along a compensation set, absolute endpoint error, and performance relative to a non-mechanistic benchmark. The manuscript demonstrates particularly well that weak parameter localization can coexist with stable aggregate predictions. It also demonstrates that mismatching the model and experimental observation windows can manufacture a large apparent transfer failure.

The manuscript is weaker when it elevates those observations into a four-way “dissociation” and a general reporting principle. In this case, endpoint accuracy and the reported cross-grind transfer score are not operationally independent: transferability is assessed through held-out endpoint error, after target-specific calibration and with target-grind hydraulic information. Incremental benchmark skill is not yet decisively evaluated because the primary comparator carries no condition or hydraulic response. A single worked case can **demonstrate and motivate** a reporting framework; it cannot by itself validate that framework as generally sufficient.

The reduced physics is acceptable for the paper's inverse-problem question provided the cross-grind result remains explicitly conditional. It is not a complete espresso model: the calculation begins fully wetted and saturated, omits axial dispersion, does not represent radial heterogeneity or channeling, and holds bed structure fixed rather than allowing wetting, swelling, compaction, erosion or permeability evolution. Those omissions do not nullify the exact multiplicative inventory result or the observed profile compensation within this model. They do prevent the fitted rate multiplier, or its transfer, from being interpreted as a validated physical extraction-rate parameter.

---

# Major findings

## Major finding 1 — The level-only constant is a valid minimal ablation, but it is not a sufficient headline benchmark of mechanistic skill

### Judgment

The current comparator is **not too strong**. It is intentionally weak. It carries one fitted concentration level per variety–solute group and no temperature, pressure, flow or kinetic response. That makes it a useful diagnostic of whether the process model improves on transferring only a level, especially because inventory is exactly multiplicative in the model.

It is not, however, the right **sole** benchmark for the broader question “does the mechanistic model add predictive information?” The mechanistic arm receives temperature, pressure and a target-grind hydraulic map; the constant receives none of those response variables. The comparison therefore confounds the value of the mechanistic structure with the value of having any condition-dependent response at all.

### Evidence relied on

- The manuscript defines the mechanistic endpoint prediction and its target-grind, study-derived hydraulic information at `PAPER_A_JFE_MANUSCRIPT.md:779–813`.
- The headline constant is defined as carrying no temperature, pressure, flow or kinetic response at `PAPER_A_JFE_MANUSCRIPT.md:814–852`.
- The model's canonical cross-grind result uses frozen centre-grind geometry and grind-specific hydraulics; the relevant qualification is at `PAPER_A_JFE_MANUSCRIPT.md:948–956` and the flow/geometry sensitivities at `PAPER_A_JFE_MANUSCRIPT.md:999–1012`.
- The complete-corpus headline is 8.44% versus 8.83% MAPE, a difference of −0.394 percentage points, with the model worse on 62 of 132 observations (`PAPER_A_JFE_MANUSCRIPT.md:814`; `PAPER_A_JFE_SUPPLEMENT.md:312–333`).
- The archived transfer contract shows a material grind asymmetry:
  - coarse: model 10.17%, constant 11.19%;
  - fine: model 6.71%, constant 6.48%.
  Thus, the full pooled improvement comes from the coarse grind; the process model is worse than the constant on the fine grind.
- The per-group table shows that the pooled gain is concentrated mainly in Arabica 5-CQA (−1.48 pp) and Arabica caffeine (−0.61 pp). At 40 g, Arabica trigonelline and Robusta caffeine are slightly worse than the constant, Robusta trigonelline is nearly tied, and Robusta 5-CQA improves by only 0.34 pp (`PAPER_A_JFE_SUPPLEMENT.md:296–317`).
- The current in-sample ladder is correctly labeled as in-sample and non-nested. It shows that the two-parameter shared mechanistic model beats the three-parameter per-grind constants in none of six groups (`PAPER_A_JFE_MANUSCRIPT.md:929–941`; Supplementary Figure S2). This is informative about compatibility, but it is not a fair zero-shot coarse/fine benchmark because the per-grind constants consume coarse/fine outcomes.
- The same-(temperature, pressure) optimal-grind lookup is a fair held-out comparator on the 108 observations for which it exists, and the model performs better there (8.23% versus 10.79%). Its support restriction is handled correctly (`PAPER_A_JFE_MANUSCRIPT.md:843–852`). It is nevertheless a noisy, unsmoothed one-record lookup rather than the strongest plausible empirical response baseline.

### Reviewer-side diagnostic

I fitted an exploratory family of no-mechanism empirical predictors using **only** each group's nine on-grid optimal-grind observations. Candidate families were constant, temperature only, pressure only, additive temperature plus pressure, and temperature-by-pressure interaction. Each family was fitted under MAPE, selected separately within each variety–solute group by leave-one-optimal-condition-out cross-validation, then frozen and evaluated on the complete coarse/fine corpus.

The resulting empirical macro-MAPE was approximately **8.691%**, compared with **8.832%** for the exact level-only constant. The mechanistic model's reported 8.44% therefore still performs better, but its apparent margin falls from about 0.394 pp to about **0.25 pp**. This check did not use the target-grind hydraulic quantity available to the process model; a genuinely equal-information baseline could narrow the margin further. Full details are in Appendix A.

This calculation is deliberately described as a reviewer-side sensitivity probe, not a new confirmatory result. The candidate family was not prospectively registered, and nine training conditions provide little room for model selection. Its value is to show that the headline gap is benchmark-sensitive even before hydraulic information is equalized.

### What should be done instead

Construct a predeclared benchmark panel with the following contract:

- **Training support:** only the nine on-grid optimal-grind records within each variety–solute group.
- **No coarse/fine leakage:** neither candidate-family selection nor coefficient fitting may inspect any coarse/fine concentration.
- **Equal information:** empirical candidates may use the same measured or inferred exogenous inputs provided to the mechanistic arm—at least temperature and pressure, and preferably the derived flow/shot-time variable used by the process calculation.
- **Controlled flexibility:** restrict candidates to low-degree, physically sensible forms. With nine points, examples could include constant; linear temperature; linear pressure; additive temperature and pressure; and one low-degree flow-based response. Do not search a large function library.
- **Nested selection:** choose form and any regularization using optimal-grind-only cross-validation. Refit the selected family on all nine optimal-grind conditions and freeze it before coarse/fine scoring.
- **Common scoring:** use the same endpoint, loss, macro-averaging and corpus as the mechanistic predictor.
- **Transparent support:** retain the same-(temperature, pressure) lookup on its 108-observation support and do not mix its score with complete-corpus scores.
- **Mechanistic ablations:** strongly consider adding a “source-rate fixed, target level fitted” process ablation and a “common hydraulic map across grinds” ablation. These would separate the value of target-rate recalibration and target-grind hydraulics from the rest of the process structure.

### Pitfalls to avoid

- Selecting empirical forms by their coarse/fine performance would invalidate the holdout.
- Including too many temperature–pressure interaction or polynomial terms will overfit nine points.
- Treating the same-condition lookup as a complete-corpus comparator would silently change the estimand.
- Giving the process model target-grind hydraulic data while withholding the same derived input from every empirical baseline would preserve the current information asymmetry.
- A post hoc benchmark revision cannot be made fully prospective. The manuscript should call the revised panel a locked, transparent sensitivity analysis rather than imply that it was the original confirmatory plan.

### Acceptance check

The benchmark section is acceptable when a reader can answer, without consulting code: what each comparator saw; where it was trained; how its complexity was selected; which support it was scored on; whether target-grind hydraulic information was available to it; and how results differ by coarse versus fine grind and by variety–solute group.

---

## Major finding 2 — The current resampling is valid as fixed-predictor sensitivity, but it does not quantify uncertainty in the comparison procedure

### Judgment

The manuscript is technically correct to call its clustered percentile ranges **fixed-predictor sensitivity ranges**, not confidence intervals. Its symmetric reading—that a zero-containing uncalibrated range does not establish absence of skill, while a wholly negative one does not establish a reproducible or useful advantage—is sound.

The limitation is that the principal ranges condition on the fitted mechanistic predictor and the fitted constant. They do not propagate the instability of fitting the rate and inventory from only nine optimal-grind conditions, nor the instability of selecting or fitting a stronger empirical comparator. Consequently, the paper has a detailed distribution for held-out losses conditional on one calibration, but not for the full scientific procedure that generated the two predictors being compared.

### Evidence relied on

- The resampling method explicitly fixes both predictors before resampling (`PAPER_A_JFE_MANUSCRIPT.md:572–588`).
- The four cluster schemes cover the same 132 observations and give the same point estimate, with materially different ranges (`PAPER_A_JFE_MANUSCRIPT.md:855–906`). This is a useful dependence sensitivity analysis.
- Table 5 explicitly states that the out-of-bag refit interval is not an uncertainty interval for the −0.394 pp model-minus-comparator difference (`PAPER_A_JFE_MANUSCRIPT.md:909–925`). This distinction is clean and correct.
- The model-only optimal-grind refit bootstrap gives 7.4% with a wide 4.3–11.5% percentile interval, illustrating the size of calibration variability when fitting is repeated (`PAPER_A_JFE_MANUSCRIPT.md:958–986`).
- The headline is heterogeneous by grind and group, while the pooled macro-MAPE compresses that structure (`PAPER_A_JFE_SUPPLEMENT.md:296–317`; transfer contract `pooled_by_grind`).

### What should be done instead

Add a **refit-aware paired procedure analysis**. A defensible exploratory implementation with the available data would be:

1. Resample optimal-grind temperature–pressure conditions within each variety, preserving the three co-measured solutes at each sampled coffee record or declaring clearly why a group-specific resample is used.
2. Refit the mechanistic model and every benchmark within each resample, including empirical-family selection where applicable.
3. Score the refitted predictors on coarse/fine records under a second resampling level that preserves the three solutes measured from the same sample record. A sample-record cluster is the clearest source-established dependence unit; the current condition-coupled C/F scheme may remain as a conservative sensitivity.
4. Record the pooled difference, coarse and fine differences, and the six group differences.
5. Report the result as an exploratory refit-aware distribution unless a simulation study establishes coverage. Do not relabel it as a calibrated confidence interval.

A simpler companion analysis would repeatedly omit one optimal-grind condition, refit both arms, and examine the resulting coarse/fine score difference. The folds are dependent, so this remains descriptive, but it directly reveals whether the headline depends on a particular calibration condition.

### Scientific interpretation that is available now

The current result supports a stronger descriptive statement than the manuscript allows itself to make, without pretending to formal inference:

> The observed pooled gain is small (about 0.4 percentage points, or 4.4% relative reduction in pooled MAPE), heterogeneous, absent in the fine-grind aggregate, and concentrated in a minority of variety–solute groups. Under the present benchmark and design, the data do not provide compelling evidence of a practically important incremental gain.

That statement is not an equivalence claim and does not assert that incremental value is absent. It is a proportionate reading of the observed effect.

### Practical margin

A practical margin should be justified before any superiority, non-inferiority or equivalence language is introduced. It could be based on an engineering use case, assay repeatability, recipe-control relevance or the accuracy needed for design optimization. The source does not provide condition-specific replicate uncertainty for a calibrated named-solute test, so the paper should not manufacture a formal margin from the global RSD range. It can nevertheless discuss whether a 0.25–0.4 pp change in MAPE would alter an engineering decision.

### Acceptance check

The revised paper should make the distinction among three quantities unmistakable:

- conditional sampling sensitivity of fixed predictions;
- calibration/refit variability of absolute prediction error; and
- calibration/refit variability of the **model-minus-benchmark difference**.

Only the third directly addresses the headline skill comparison.

---

## Major finding 3 — The “cross-grind” test is conditional outcome transfer, not a validation of grind physics

### Judgment

The manuscript is commendably cautious in several places, but the engineering design of the test deserves greater prominence. The canonical calculation holds the centre-grind particle geometry fixed across all target grinds. The target grind enters through a study-derived hydraulic conductivity/shot-time map rather than through a calibrated mapping of target particle-size distribution, fines fraction, porosity or permeability evolution.

This is a legitimate test of whether a target-calibrated reduced predictor remains useful on records labeled coarse and fine, conditional on the supplied hydraulic map. It is not a direct validation that the two-grain model captures how changing grind changes extraction physics.

### Evidence relied on

- The manuscript calls the result a within-campaign cross-grind prediction after target-specific calibration and says it is conditional on an inferred flow map (`PAPER_A_JFE_MANUSCRIPT.md:779–813`).
- It later states that the test is conditioned on frozen centre-grind geometry (`PAPER_A_JFE_MANUSCRIPT.md:948–956`).
- The geometry sensitivity applies each of three source geometries **globally** to every grind and explicitly does not validate a grind-specific geometry map (`PAPER_A_JFE_MANUSCRIPT.md:999–1005`).
- In contrast, Table 2 currently says that `d_s2` and `psi` are estimated “per grind, from the source's fitted table” (`PAPER_A_JFE_MANUSCRIPT.md:326–339`). That row is inconsistent with the canonical analysis and should be corrected.
- The per-granulometry flow treatment uses fitted hydraulic conductivity and nominal shot times of 20/13/35 s (`PAPER_A_JFE_MANUSCRIPT.md:441–449`). This is exogenous process information rather than concentration fitting, but it gives the mechanistic arm information about the target grind that the level-only constant does not receive.
- Recent espresso flow experiments describe nonlinear, time-evolving pressure–flow behavior associated with brewer losses, wetting, swelling, compaction, erosion and poroelastic changes. The manuscript's cited Waszkiewicz campaign is therefore itself evidence that a fixed Darcy-form map is a reduced assumption, not a generally validated law.

### What should be done instead

Two scientifically acceptable paths are available.

**Path A — retain the present analysis and narrow the interpretation.**

- Call it “within-campaign coarse/fine endpoint prediction conditional on target-grind hydraulics and global geometry.”
- Remove or qualify any wording that a reader could interpret as transfer of a physical grind mechanism.
- Correct Table 2 so the canonical and sensitivity geometries are described accurately.
- Add a table listing every input that changes with grind and every input held fixed.
- Make the equal-information hydraulic baseline in Major finding 1 part of the main result.

**Path B — strengthen the grind-physics test.**

- Use measured or independently mapped particle-size/fines information for O, C and F where available.
- Propagate those grind-specific geometries without fitting to held-out concentrations.
- Include porosity/permeability sensitivity or a calibrated physical mapping if the source supports one.
- Compare the resulting model with the same equal-information empirical benchmarks.

Path A is sufficient for this paper's stated case-study purpose. Path B would support a materially stronger food-engineering claim.

### Flow-map sensitivity

The reported ±20% flow-scale perturbation is useful and shows that the **magnitude** of the inferred map is not load-bearing for pooled endpoint error. It does not test map form, pressure nonlinearity, time variation, or interactions between hydraulic and structural assumptions. Add at least a small form family, for example:

- the current Darcy proportionality;
- a nonlinear pressure exponent or pressure-offset form constrained by plausible espresso hydraulics;
- a nominal-shot-time-only map; and
- where possible, a representative time-varying flow profile.

The purpose is not to identify the true map from these data. It is to determine whether the benchmark verdict survives plausible map forms, rather than only a uniform scale change.

### Acceptance check

A reader should be able to identify exactly which physical attributes of grind are actually transferred. Under the present canonical setup the answer is primarily target-grind hydraulics, not target-grind particle geometry. The title and conclusions need not change if that distinction remains explicit.

---

## Major finding 4 — The numerical convergence evidence is excellent for one panel but insufficient for all load-bearing results

### Judgment

The existing 100/200/400-node by 10⁻⁵/10⁻⁶/10⁻⁷ tolerance study is well designed and reports inference-relevant outputs rather than only state-vector differences. For the Arabica-caffeine optimal-grind panel it is convincing.

It is not a paper-wide convergence demonstration. The manuscript itself correctly states that it does not certify 5-CQA, highest-rate cells, the external time-varying-flow trajectory or the positive-control fraction profiles. This matters because Arabica 5-CQA supplies the largest part of the model's apparent advantage over the constant, and the temporal-profile results are central to the paper's main message.

### Evidence relied on

- Numerical method and representative convergence study: `PAPER_A_JFE_MANUSCRIPT.md:506–536`.
- The manuscript's own explicit exclusions: `PAPER_A_JFE_MANUSCRIPT.md:523–530`.
- Solver-warning and physical-state checks across 1,458 solves: `PAPER_A_JFE_MANUSCRIPT.md:538–544`; `PAPER_A_JFE_SUPPLEMENT.md:392–436`.
- The representative panel is Arabica caffeine, optimal grind, nine conditions (`PAPER_A_JFE_SUPPLEMENT.md:392–436`).
- Arabica 5-CQA produces the largest per-group model-versus-constant improvement (`PAPER_A_JFE_SUPPLEMENT.md:296–317`).

### What should be done instead

Run a compact **numerical envelope suite**, not an exhaustive repeat of every cell. It should include:

1. 5-CQA at the highest-stiffness or highest-rate boundary conditions;
2. the lowest and highest temperature, pressure and flow combinations relevant to O, C and F;
3. at least one coarse and one fine target case;
4. the external time-varying-flow TDS trajectory;
5. the source fraction-profile positive control;
6. one rate-profile case whose minimum or near-optimal set touches a domain boundary.

For each case compare:

- whole-cup and fraction concentrations;
- profile minimum and range ratio;
- any boundary classification;
- the resulting held-out MAPE and, where relevant, the model-minus-comparator difference;
- positivity and monotonic cumulative mass; and
- a global solute mass-balance residual or equivalent conservation check.

Numerical variation should be reported relative to the scale of the claimed effect. Because the headline difference is only about 0.394 pp, showing that discretization/tolerance changes move the paired difference by much less than that is more informative than showing only sub-percent concentration agreement in one panel.

An analytic Jacobian is not required for publication, but the six numerical-Jacobian overflow/invalid warnings should be absent or explicitly demonstrated harmless in the newly selected worst-case cells. The present instrumentation is a strong basis for that check.

### Acceptance check

The paper need not claim universal convergence. It should establish that each class of load-bearing observable—named-solute transfer, stiffest solute, temporal profile, and external variable-flow trajectory—has at least one conservative convergence representative.

---

## Major finding 5 — The strongest dissociation is demonstrated, but the four-way and protocol claims should be narrowed

### Judgment

The paper convincingly demonstrates one important dissociation:

- parameter localization is weak;
- endpoint predictions remain comparatively stable along the declared near-optimal set.

That result is directly tested and is the manuscript's strongest inverse-problem contribution.

The paper also convincingly shows that endpoint matching and flow correction are different issues: a fixed-time mismatch can produce an apparent transfer failure that largely disappears at a matched collected-mass endpoint.

The evidence does **not** yet establish a full four-way empirical dissociation among identifiability, endpoint accuracy, benchmark skill and cross-grind transferability:

- benchmark skill is benchmark-dependent and currently tested against a minimal comparator;
- cross-grind transferability is measured through the same held-out endpoint errors used to describe endpoint accuracy;
- the target-grind calculation is conditional on target hydraulics and global geometry; and
- one case cannot establish that the proposed four-part reporting protocol is generally sufficient.

### Evidence relied on

- Near-optimal-set prediction envelopes remain comparatively stable despite parameter instability (`PAPER_A_JFE_MANUSCRIPT.md:942–956`).
- The endpoint-artifact result is reported at `PAPER_A_JFE_MANUSCRIPT.md:788–813`.
- The discussion states that endpoint accuracy, parameter identification, cross-grind transferability and incremental skill are distinct and must be reported separately (`PAPER_A_JFE_MANUSCRIPT.md:1157–1184`).
- The conclusion says the results establish a practical reporting principle (`PAPER_A_JFE_MANUSCRIPT.md:1239–1242`).

### What should be done instead

Recast the contribution hierarchy approximately as follows:

1. **Demonstrated in this case:** exact inventory scaling creates a broad practical compensation profile under the tested whole-cup design; parameter localization can be weak while endpoint predictions remain stable.
2. **Demonstrated in this case:** observation-window mismatch can dominate apparent cross-context error.
3. **Observed but not decisively adjudicated:** the process predictor has a small, heterogeneous advantage over a minimal level-only comparator.
4. **Proposed reporting framework:** localization, absolute prediction, equal-information benchmark skill and cross-context evidence should be reported separately.

A suitable conclusion would be:

> In this reduced-model case study, weak localization of the inventory–rate split coexisted with stable endpoint predictions. Matched-endpoint coarse/fine predictions were modest in absolute error, but incremental skill and transfer of a physical grind mechanism were not established. The case therefore motivates, rather than universally validates, separate reporting of parameter localization, absolute prediction, equal-information benchmark performance and cross-context evidence.

Retaining a stronger universal protocol claim would require at least one further model lineage or dataset in which the same reporting framework changes the scientific conclusion. That expansion is not necessary if the paper is presented plainly as an applied case study and methodological demonstration.

### Acceptance check

The abstract, discussion and conclusion should distinguish “demonstrates in this case,” “observes,” “does not adjudicate,” and “proposes.” This is not another request for defensive wording; it is a request to align the claimed contribution with the actual experimental and benchmark design.

---

# Minor findings

## Minor finding 1 — The three-solute selection is defensible, but the eligibility rule must be explicit

### Judgment

Using caffeine, trigonelline and 5-CQA is scientifically defensible if—and apparently because—they are the named species shared between the source mechanistic parameterization and the Angeloni campaign. It is not defensible to leave the reader with the impression that Angeloni measured only those three named solutes.

The controlled CSV contains eleven measured species/aggregates beyond the condition fields. The manuscript currently says Angeloni “reports measured beverage concentrations” for caffeine, trigonelline, 5-CQA and total solids (`PAPER_A_JFE_MANUSCRIPT.md:283–303`) without explaining that the chemical campaign is broader and that model support, not observed performance, determines eligibility.

### Required correction

Add a short eligibility statement and, preferably, a compact supplement table:

- Angeloni measured eleven reported analyte/aggregate columns in the controlled table.
- The analysis includes the three named solutes for which the source extraction model supplies the required species-specific parameterization.
- The inclusion rule was common model–data support and was not chosen from coarse/fine performance.
- TDS remains separate because it is an aggregate optical/solids observable, not a fourth named solute.

This removes a plausible outcome-selection concern without expanding the model to unsupported species.

---

## Minor finding 2 — Distinguish mass flow and volumetric flow with separate symbols

The source convention is handled thoughtfully: a column labeled mL s⁻¹ is consumed by the source calculation as mass flow, the stopping rule uses collected mass, and density is used when deriving velocity. Preserving that convention is reasonable because the inherited fitted parameters were obtained under it, and the 38/40/42 g sweep bounds the practical endpoint ambiguity (`PAPER_A_JFE_MANUSCRIPT.md:377–421`).

The notation still uses `Q` both as volumetric flow in the observation-operator discussion and as a mass-flow quantity in the endpoint/table discussion (`PAPER_A_JFE_MANUSCRIPT.md:341–381`; Table 2 at 326–339). Use distinct symbols, for example:

- `m_dot` for collected mass flow and the stopping rule `t_end = M_target/m_dot`;
- `Q_v = m_dot/rho` for volumetric flow entering superficial velocity and volume-weighted integration.

This is a dimensional clarity correction, not a request to alter the source arithmetic.

---

## Minor finding 3 — Expand the physical-scope limitation by naming the omitted espresso processes

The limitations section says the model structure is fixed and model discrepancy is not represented, but it does not clearly name the major physical omissions. Add one concise paragraph stating that the canonical model:

- starts from a fully wetted, locally equilibrated bed;
- omits the initial unsaturated infiltration, air and residual CO₂ displacement;
- omits axial dispersion, radial nonuniformity and channeling;
- holds porosity and permeability fixed; and
- does not model swelling, compaction, erosion, fines migration or dissolution-driven hydraulic evolution.

These are well-established features of real espresso flow and are especially relevant to a paper discussing cross-grind transfer. The result should remain framed as a reduced-model inverse problem. No new multiphysics model is required for this manuscript.

### Point found clean

Using superficial velocity to form the packed-bed Reynolds number while using interstitial velocity in the advection term is internally consistent and explicitly documented (`PAPER_A_JFE_MANUSCRIPT.md:190–215`). I do not recommend changing that convention.

---

## Minor finding 4 — The geometry entry in Table 2 conflicts with the actual canonical transfer calculation

Table 2 says `d_s2` and `psi` are “per grind, from the source's fitted table” (`PAPER_A_JFE_MANUSCRIPT.md:326–339`), whereas the results section says the canonical transfer uses frozen centre-grind geometry and the sensitivity applies each candidate geometry globally (`PAPER_A_JFE_MANUSCRIPT.md:948–956`, `999–1005`).

Correct the table to describe:

- the canonical global centre-grind geometry;
- the three global geometry sensitivity cases; and
- the absence of a calibrated target-specific grind-geometry map.

This is methodologically important because it determines what “cross-grind” means.

---

## Minor finding 5 — Add a direct engineering-scale interpretation of the effect size

The paper reports the relative pooled-MAPE reduction of about 4.4%, but it does not tell a food-engineering reader whether a 0.394 pp absolute MAPE change would affect process design, recipe control, equipment optimization or analyte prediction. Add a short interpretation tied to a plausible use case. Where no decision threshold is available, say that the observed difference is unlikely to change an engineering decision at the present residual and uncertainty scale.

Do not translate the result into formal equivalence or non-inferiority without a justified margin.

---

## Minor finding 6 — Clarify the structural-identifiability definition in Supplementary Note S1

Structural identifiability is not a property of the model and observation map “alone”; it also depends on the declared inputs/excitation, initial and boundary conditions, parameterization and idealized observation protocol. Amend the definition accordingly. The main manuscript already behaves as though these qualifications matter, so this is a conceptual precision fix rather than a change to the result.

---

# Editorial and figure findings

1. `PAPER_A_JFE_MANUSCRIPT.md:814`: “**The Because** the reported ranges…” should be “Because the reported ranges…”
2. `PAPER_A_JFE_MANUSCRIPT.md:937–938`: replace the comma after “in this dataset” with a period before “This descriptive…”
3. `PAPER_A_JFE_MANUSCRIPT.md:441`: “Angeloni report pressure” should be “Angeloni reports pressure.”
4. Supplementary Figure S2 is scientifically useful and correctly labels the comparison as in-sample and non-nested, but the heatmap annotations, diagonal group labels and long all-caps header are difficult to read at likely journal width. Increase text size and simplify the header. Do not remove the unequal-flexibility warning.
5. Supplementary Figure S1 is valuable because it exposes the severe Robusta 5-CQA folds that the pooled 6.5% LOCO MAPE can obscure. Keep it.
6. Supplementary Figures S3 and S4 are clean. S4's explicit note that group-level recalibration removes offsets and that within-group response is not shown is scientifically important and should remain.
7. The standalone captions are generally excellent: they state calibration/holdout dependencies, evidence tiers and inferential limitations rather than merely describing graphical elements.

---

# Sections checked and found scientifically sound

## Study architecture and corpus construction — clean

The dataset-role table clearly separates source calibration, target recalibration, within-campaign holdout, same-model simulation and external aggregate-proxy evidence. The complete 44-record/132-observation coarse/fine corpus is the correct primary support for predictors that are defined everywhere. Including the eight off-grid records does not make the comparison inhomogeneous; excluding them would weaken the transfer test. The on-grid and off-grid slices are appropriately reported, and the 108-observation lookup comparison remains on its own support.

## Observation operators and endpoint matching — clean and a major strength

The whole-cup, fraction and sampled-window operators are distinguished carefully. The paper correctly shows that a fixed-time model output and a fixed-mass experimental cup are different estimands. Repeating the transfer benchmark at 38, 40 and 42 g, rather than using the blind-residual endpoint sensitivity to infer comparator sensitivity, is methodologically sound.

## Exact multiplicative inventory factorization — clean

The analytical profiling of the inventory level is a strong feature. It makes the compensation geometry transparent and avoids unnecessary numerical optimization. The manuscript also correctly separates a declared near-optimal tolerance set from a likelihood-based confidence region.

## Treatment of the nonstandard diffusivity closure — clean

The manuscript identifies that the inherited relation pairs the solvent association factor with solute rather than solvent molecular weight, reproduces the source convention, and demonstrates why the change is absorbed by the profiled common rate multiplier. It correctly concludes that the absolute fitted rate is not diffusivity-anchored or physically interpretable while the profile geometry and benchmark results are essentially unchanged (`PAPER_A_JFE_MANUSCRIPT.md:208–238`). No further scientific correction is required unless the source authors provide a definitive erratum.

## Section 3, inventory–rate localization — clean within its declared scope

The broad/right-censored profile result is supported across six panels and three objective families. Boundary flags, grid-density checks, domain sweeps and objective robustness are presented honestly. The conclusion is practical localization failure under the tested design, not a general structural-identifiability theorem.

## Same-(temperature, pressure) lookup handling — clean

The lookup is evaluated only where it exists and is not pooled with complete-corpus comparator scores. That is the correct treatment of unequal support.

## In-sample comparator ladder — clean as a diagnostic

The manuscript explicitly states that the models are non-nested, of unequal flexibility and evaluated on their own fitting data. It does not misuse the ladder as a held-out test. The ladder should be retained, but it cannot substitute for the equal-information held-out benchmark requested above.

## Section 5, temporal-information evidence — clean and appropriately tiered

The source fraction analysis, same-model exact-cup control and independent external TDS trajectory are clearly separated. The inverse-crime status of the synthetic control is disclosed. The external trajectory is read at the weaker of the percentage and absolute-residual losses, and its high residual, shallow preference, boundary censoring and one-coffee/one-grind scope are acknowledged. The claim is correctly limited to objective localization under the tested model and observation operator.

## Figures and captions — scientifically clean overall

The four available submission figures faithfully expose residual structure and model limitations rather than hiding them behind pooled scores. Captions are unusually complete and stand alone. The only material figure action is readability improvement for Supplementary Figure S2.

---

# Direct answers to the referee brief

## (a) Is the comparator fair?

**As a minimal transferred-level ablation: yes. As the sole headline benchmark of mechanistic skill: no.** It is deliberately easier to beat than a low-degree empirical condition/hydraulic-response model. The per-grind constants are not fair zero-shot comparators because they use target outcomes; the manuscript correctly treats them as in-sample. The same-(temperature, pressure) lookup is fair on its restricted support and deserves co-prominence, but an optimal-grind-only empirical response baseline using equal exogenous information is still needed.

## (b) Is the corpus the right one?

**Yes.** The complete 132 observations are the correct primary corpus for the model and level-only/empirical predictors. The 108-observation matched-grid subset is appropriately secondary. The three-solute restriction is defensible as common model–data support, but the eligibility rule must be explicit because Angeloni measured a broader analyte panel. Forty-four sample records are small; clustered fixed-predictor ranges are reasonable descriptive sensitivities, but they do not replace refit-aware uncertainty for the full comparison procedure.

## (c) Does the conclusion follow?

**Partly.** Weak parameter localization coexisting with stable predictions is demonstrated. Endpoint mismatch manufacturing apparent failure is demonstrated. The full four-way dissociation and general reporting-principle language are stronger than one benchmark-sensitive, within-campaign case supports. The formal reading of the uncalibrated ranges is correct, but the authors may still state descriptively that the observed gain is small, heterogeneous and not compelling evidence of practical improvement.

## (d) Are the physics and numerics defensible?

**Conditionally.** The one-dimensional saturated two-grain model is defensible as a deliberately reduced inverse-problem vehicle, not as a complete espresso model. The superficial/interstitial velocity pairing is physically and mathematically coherent. Preserving the source's mass-flow convention is reasonable, although notation should distinguish mass and volume flow. The Darcy/hydraulic treatment is a pragmatic mapping whose magnitude sensitivity is useful, but its functional form and time dependence remain unresolved. Numerical convergence is convincing for one representative panel and insufficient for the complete set of load-bearing solutes and trajectories.

## (e) Would I accept it at JFE?

**Major revision.** The topic and approach fit a food-engineering journal that publishes validated mathematical modeling. The paper should become publishable without new wet-laboratory experiments if it adds the equal-information benchmark, refit-aware comparison analysis, numerical envelope checks and narrower transfer/protocol interpretation.

---

# Prioritized revision plan

## Priority 1 — Rebuild the headline benchmark

**Objective:** determine whether the process structure adds prediction skill beyond a fair non-mechanistic response model.

**Method:** lock a small optimal-grind-only candidate family; select by nested optimal-grind CV; include temperature, pressure and the same hydraulic information; freeze and score on complete C/F; retain constant and lookup.

**Primary risks:** C/F leakage, overfitting nine conditions, unequal input information, mixing comparator supports.

**Checks:** exact training IDs; no C/F access in selection; common endpoint/loss; by-grind and by-group reporting; benchmark stability across a predeclared small family.

## Priority 2 — Propagate refitting through the comparison

**Objective:** quantify how calibration instability affects the model-minus-benchmark result.

**Method:** resample O conditions, refit both arms, resample/score C/F sample records, preserve co-measured solutes, report pooled/grind/group distributions.

**Primary risks:** claiming calibrated coverage; too few clusters; conflating different held-out fractions.

**Checks:** label estimand; effective draws; failure/boundary rates; sensitivity to sample-record versus condition clustering; separate fixed-predictor and refit-aware results.

## Priority 3 — Run a load-bearing numerical envelope

**Objective:** show that the conclusion is not numerically specific to Arabica caffeine O.

**Method:** convergence cells for stiffest 5-CQA, high-rate boundary, C/F extrema, external flow trajectory and temporal positive control.

**Primary risks:** checking only state outputs rather than conclusion-bearing observables; reusing one numerical path without conservation evidence.

**Checks:** profile minimum/range, MAPE and ΔMAPE stability, mass balance, positivity, warnings, solver success.

## Priority 4 — Align the engineering interpretation

**Objective:** make clear what physical information actually transfers.

**Method:** correct geometry provenance; list grind-varying inputs; test flow-map form; relabel as conditional outcome transfer unless grind-specific geometry is added.

**Primary risks:** allowing “cross-grind” to imply particle-physics validation; withholding target hydraulics from baselines.

**Checks:** a one-page dependency diagram or table showing fitted, frozen, inferred and held-out quantities.

## Priority 5 — Tighten the contribution claim

**Objective:** preserve the strong case-study result without universalizing it.

**Method:** distinguish demonstrated dissociation, observed benchmark result and proposed protocol in the abstract, discussion and conclusion.

**Primary risks:** replacing overclaim with vacuous language.

**Checks:** retain the positive scientific statement that weak localization coexists with stable endpoint predictions and that matched observation operators are essential.

---

# Appendix A — Independent reviewer-side empirical-baseline check

## Purpose

To determine whether a slightly stronger, still non-mechanistic optimal-grind-only predictor materially changes the 8.83% level-only benchmark.

## Data and support

- Controlled Angeloni bioactive table at reviewed commit.
- Training: nine on-grid O-grind conditions per variety.
- Test: all C and F records, including off-grid records.
- Solutes: caffeine (`CF`), trigonelline (`TR`) and 5-CQA.
- Grouping: model fitted and selected separately for each variety–solute group, matching the current comparator/model grouping.

## Candidate family

1. constant;
2. linear temperature response;
3. linear pressure response;
4. additive temperature plus pressure;
5. temperature, pressure and their interaction.

For each candidate, coefficients minimize training MAPE through linear programming. Candidate choice uses leave-one-O-condition-out cross-validation within the group. The selected family is refitted to all nine O conditions and frozen before C/F evaluation.

## Results

| group | selected family | complete C/F MAPE (%) |
|---|---:|---:|
| Arabica caffeine | pressure | 8.744 |
| Arabica trigonelline | constant | 6.454 |
| Arabica 5-CQA | pressure | 13.216 |
| Robusta caffeine | constant | 7.483 |
| Robusta trigonelline | temperature | 7.302 |
| Robusta 5-CQA | constant | 8.946 |
| **Macro average** | — | **8.691** |

By target grind, the empirical macro-MAPE is approximately 11.012% for C and 6.370% for F. Recomputing the current MAPE-optimal constants from the same raw table gives 8.832% overall, 11.187% for C and 6.478% for F, reproducing the reported comparator after rounding.

## Interpretation

- A low-degree empirical response selected without C/F outcomes improves the constant from about 8.832% to 8.691%.
- The mechanistic model's reported 8.44% remains lower, but the margin narrows from about 0.394 pp to roughly 0.25 pp.
- The empirical baseline improves both grinds, while the mechanistic model's pooled improvement over the constant is confined to the coarse grind.
- This empirical check still does not use the target-grind hydraulic information available to the mechanistic calculation; it therefore does not resolve the equal-information question.

## Limitations

- The candidate family was chosen by this reviewer after reading the manuscript and is not prospectively registered.
- Nine O conditions make model-family selection unstable.
- No hydraulic predictor was available in the raw concentration table used for this calculation.
- The exercise is a benchmark-sensitivity diagnostic, not a replacement for the authors' locked analysis.

---

# Final referee statement

This manuscript is not suffering from a lack of caveats. It is suffering from one remaining scientific mismatch between the question and the analysis: the paper asks whether a mechanistic response adds predictive information, but its primary comparator has no response structure and does not receive the same hydraulic information. The authors have already built most of the machinery needed to fix that mismatch. Once the benchmark, refit-aware comparison and numerical envelope are added, the paper should present a strong and useful food-engineering case study.
