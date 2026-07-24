# Detailed Review of Paper 1 / Paper A

**Repository:** `trbrewer/puckworks`  
**Review date:** 24 July 2026  
**Primary manuscript reviewed:** `docs/submission/PAPER_A_JFE_MANUSCRIPT.md`  
**Pinned manuscript revision:** commit `85af247acdf7bdb611d5b5b28b7e09e878ecc3ac`  
**Cross-checked against:** the authoritative working manuscript `docs/PAPER_A_DRAFT.md`, the reviewer brief, figure files and captions, the Angeloni source card, and the key source publications used in the analysis.  
**Line references:** line numbers below refer to the 687-line JFE conversion manuscript at the pinned commit.  
**Review scope:** scientific and editorial desk review. I did not rerun the repository's slow PDE analyses, so numerical values are assessed for interpretation, internal consistency, presentation, and methodological support rather than independently reproduced.

## Overall recommendation

**Major revision before submission.**

The paper has a strong, useful core result: in the tested espresso model and datasets, a whole-cup endpoint can be predicted reasonably well while the model remains unable to cleanly separate the amount of extractable material from the rate at which that material is released. The comparison with a level-only baseline is especially valuable because it demonstrates that acceptable prediction error is not the same as evidence for a transferable kinetic mechanism. The distinction among parameter localization, endpoint accuracy, predictive stability, and incremental skill is worth publishing.

The manuscript is not yet submission-ready, however. The current JFE conversion is partly stale relative to the repository's authoritative working draft; several corrected qualifications have not been propagated. More importantly, the manuscript still depends on an unresolved measurement-uncertainty analysis and an insufficiently documented dimensional conversion for the Angeloni Table 7 inventory constraint. It also relies too heavily on repository language, code-object names, review history, and prior-draft corrections. The scientific story is currently harder to follow than it needs to be.

The paper will be substantially stronger if it is rebuilt around one clear question:

> **What information about espresso extraction rate is retained—or lost—when a time-resolved extraction is reduced to a whole-cup measurement?**

Everything else should serve that question.

---

## 1. Title review

### 1.1 The working title is too metaphorical

The authoritative working draft uses:

> **The cup can hide the clock: practical inventory–kinetics confounding in a cross-dataset espresso extraction case study**

Your concern is justified. “The cup can hide the clock” is memorable, but it leads with a metaphor rather than the scientific subject. It sounds more like a conference talk, magazine headline, or social-media hook than a journal article. The subtitle then swings too far in the other direction: “practical inventory–kinetics confounding” is specialist language and places a comprehension burden on readers before they know what the paper is about.

The metaphor could still be useful as a graphical-abstract caption, section heading, talk title, or outreach phrase. It should not be the manuscript title.

### 1.2 The JFE-conversion title is descriptive but unnecessarily opaque

The submission conversion currently uses:

> **Whole-cup measurements can obscure kinetic parameter localization in espresso extraction models**

This is an improvement because it includes “espresso” and identifies whole-cup measurements as the subject. Its weakness is the phrase **“kinetic parameter localization.”** That phrase is technically defensible, but it is not natural language for most food-engineering readers, coffee researchers, or informed lay readers. It also leaves out the second half of the paper: time-resolved fractions and orthogonal inventory measurements recover information that the cup endpoint loses.

### 1.3 Recommended title

# **Separating Extractable Content from Extraction Rate in Espresso Models: Limits of Whole-Cup Data and the Value of Time-Resolved Measurements**

This title is the best fit for the paper because it:

- contains **espresso**;
- states the two quantities that are being confused in plain language;
- identifies the limitation of whole-cup data;
- signals the positive result about time-resolved measurements;
- avoids both slogan-like metaphor and specialist shorthand; and
- accurately describes a methods/limitations case study rather than implying a fully validated predictive model.

“Extractable content” should be defined in the abstract as the amount of soluble material initially available. The manuscript may then use the shorter technical term **inventory** after that first definition.

### 1.4 Ranked alternatives

| Rank | Proposed title | Comment |
|---:|---|---|
| 1 | **Separating Extractable Content from Extraction Rate in Espresso Models: Limits of Whole-Cup Data and the Value of Time-Resolved Measurements** | Most complete and accessible; my recommendation. |
| 2 | **Limits of Whole-Cup Data for Estimating Espresso Extraction Rates** | Concise and journal-conservative, but it does not mention the inventory/content side of the confounding or the positive value of fractions. |
| 3 | **Estimating Espresso Extraction Rates: Why Whole-Cup Data Need Time-Resolved or Independent Measurements** | Clear and accessible; slightly more prescriptive than the evidence warrants. |
| 4 | **Whole-Cup and Time-Resolved Measurements in Espresso Extraction Models: Separating Extractable Content from Release Rate** | Balanced and neutral, though somewhat long. |
| 5 | **What Whole-Cup Espresso Measurements Can—and Cannot—Reveal About Extraction Rate** | Highly accessible, but the interrogative/rhetorical construction is less conventional and risks retaining some of the tagline quality you want to avoid. |

### 1.5 Running title

**Whole-cup data and espresso extraction rates**

---

## 2. The paper's most defensible central claim

A revised manuscript should repeatedly return to one carefully bounded statement:

> **For the tested model, parameter range, observation operators, and campaigns, whole-cup espresso measurements allowed broad compensation between extractable content and extraction rate. The resulting model could retain acceptable endpoint accuracy while adding little held-out skill over a level-only baseline. Time-resolved fractions and a separately measured inventory supplied stronger information about the rate.**

This wording avoids four common overclaims:

1. It does not say that whole-cup data can never identify a rate.
2. It does not call the target-recalibrated Angeloni analysis a transfer of the original kinetic mechanism.
3. It does not treat a descriptive objective threshold as a confidence interval.
4. It does not equate a shallow, high-error external trajectory profile with independent validation of the absolute model.

---

## 3. Major scientific and editorial comments

## Major Comment 1 — Resolve the version drift before making further revisions

The repository declares `docs/PAPER_A_DRAFT.md` to be the authoritative manuscript, but the JFE conversion contains older, materially less careful language. This is not merely copyediting drift; some differences change the interpretation of the evidence.

Examples:

- **JFE lines 214–223** call the edge-to-minimum objective ratio an “identifiability ratio” and say that a large ratio means the rate “is identified.” The authoritative working draft has already corrected this to **profile range ratio** and explicitly states that it is a domain-dependent localization contrast, not an identification theorem.
- **JFE lines 307–314** say the Table 7 measurement “collapses” the profile to a “narrow band” after propagating ±10% inventory sensitivity. The working draft correctly calls the result a **conditional one-dimensional intersection band**, states that ±10% is an analyst-selected perturbation, and says that the result is not a confidence interval.
- **JFE lines 353 and 370–377** retain the older “frozen-parameter transfer” framing and prior-draft correction narrative. The current working draft has a more defensible heading: cross-grind endpoint prediction versus a level-only baseline.
- **JFE lines 397–403** call the comparator sequence a “nested reduced-model ladder” and conclude that the mechanism explains “essentially nothing.” The models are not nested and have unequal flexibility. The working draft has already corrected this to an **in-sample comparator ladder** with a descriptive interpretation.
- **JFE lines 359–362** still say “matched 40 g cups,” although the analysis uses a 40 mL proxy for a nominal 40 g endpoint. The working draft has corrected this.

**Required action:** choose one canonical manuscript source and regenerate every submission artifact from it. Add an automated check that fails when the authoritative draft and venue conversion disagree on designated load-bearing phrases, result numbers, section titles, or evidence labels. No further scientific edit should be made independently in both files.

This is a submission-blocking issue because reviewers could receive claims that the repository itself has already judged too strong.

---

## Major Comment 2 — Make the observation operator the paper's organizing idea

The paper's most general contribution is not the particular optimum or profile width. It is the demonstration that **the observation operator determines which parameter combinations can be learned**.

At present, this point is explained verbally but not developed into a compact analytical principle. A simple local sensitivity argument would turn the paper from a long audit of one transfer attempt into a more general and reusable food-engineering result.

For observations of the form

\[
y_i = I\,f_i(k),
\]

where \(I\) is extractable content and \(k\) is a rate multiplier, define the local log-sensitivity

\[
s_i(k)=\frac{\partial \log f_i(k)}{\partial \log k}.
\]

For log-scale observations, the local sensitivity vector for condition \(i\) is

\[
\left[1,\ s_i(k)\right].
\]

With weights \(w_i\), the local information/Gram matrix is

\[
G=\sum_i w_i
\begin{bmatrix}
1\\ s_i
\end{bmatrix}
\begin{bmatrix}
1 & s_i
\end{bmatrix}.
\]

Its determinant is

\[
\det(G)=\left(\sum_i w_i\right)^2\operatorname{Var}_w(s_i).
\]

The practical implication is straightforward:

- when the rate sensitivities \(s_i\) are nearly the same across observations, the two sensitivity columns are nearly collinear and extractable content can compensate for rate;
- when sampling times or operating conditions create a broad spread in \(s_i\), the two parameters become more separable;
- time-resolved fractions are useful because early, middle, and late measurements generally rotate the rate-sensitivity direction more than one integrated endpoint does.

This should be presented as a **local design diagnostic**, not a structural-identifiability theorem. It would nevertheless provide the analytical backbone currently missing from the paper and would explain why the fraction result matters beyond espresso.

**Recommended placement:** one short subsection near the end of Methods, followed by a plot or small table showing the distribution of \(s_i\) for whole-cup conditions versus fraction times. That plot could be more informative than several current diagnostic panels.

---

## Major Comment 3 — The Methods section is not yet standalone

A journal manuscript cannot depend on repository object names and a citation to `pannusch2024` in place of a reproducible model description. Lines 139–154 provide only a short verbal description of a one-dimensional PDE and a Sherwood correlation. A reader cannot reconstruct the analysis from the paper.

At minimum, the manuscript needs:

1. **The governing balances or a clearly defined reduced model.** The full PDE may be placed in an appendix, but the state variables, boundary conditions, initial conditions, and outlet definition must be stated.
2. **The observation operators**, explicitly written. For example:

   \[
   C_{\mathrm{cup}}=
   \frac{\int_0^{t_{\mathrm{end}}}Q(t)C_{\mathrm{out}}(t)\,dt}
        {\int_0^{t_{\mathrm{end}}}Q(t)\,dt},
   \]

   and, for fraction \(j\),

   \[
   C_j=
   \frac{\int_{t_j}^{t_{j+1}}Q(t)C_{\mathrm{out}}(t)\,dt}
        {\int_{t_j}^{t_{j+1}}Q(t)\,dt}.
   \]

3. **A precise definition of `c_s0`.** Is it mass per dry-coffee mass, mass per solid-phase volume, mass per bulk bed volume, or a normalized solver concentration? This definition is essential to the Table 7 comparison.
4. **A precise definition of `rate_scale`.** State which Sherwood coefficients it multiplies, whether it acts identically on the internal fine/coarse particle classes, whether the baseline value is one, and what physical interpretation—if any—survives after target recalibration.
5. **The exact fitting groups.** Lines 206–210 say parameters are fitted per solute per variety. The text, figures, and captions must consistently state whether each profile uses one variety, both varieties, or shared parameters.
6. **The objective functions and averaging order.** Define unweighted SSE, pooled MAPE, macro-MAPE, and the exact group hierarchy used in each result.
7. **The analytical MAPE level solution.** If the optimal level is a weighted median, provide the derivation and weights in an appendix.
8. **Parameter domains and boundary handling.** List the rate grid, inventory domain if applicable, interpolation procedure, and criterion for declaring a boundary-censored set.
9. **A compact dataset-and-role table.** Readers should not have to infer which campaign supplies source calibration, target recalibration, internal holdout, same-campaign orthogonal information, simulation truth, and independent shape testing.

A two-page self-contained methods description would improve both rigor and accessibility.

---

## Major Comment 4 — Measurement uncertainty is a submission gate, not a routine limitation

The manuscript acknowledges that Angeloni reports analyte relative standard deviations spanning approximately 0.3–19.7%, while the repository retains central values and the principal profile uses unweighted concentration-scale SSE. It also states that weighted reruns remain outstanding.

This matters directly to the central result. A broad profile under unweighted SSE could become narrower or broader when high-variance observations are downweighted. Likewise, the relative ranking of rate values and the curvature near the optimum can change. It is not enough to mention this in an editorial note or limitations register.

**Required analyses:**

- Reconstruct per-observation uncertainty wherever the source supports it. If replicate-level named-solute uncertainty is unavailable, document exactly what is and is not available.
- Repeat the principal profile under at least:
  - uncertainty-weighted SSE;
  - a relative or log-scale objective;
  - a robust objective that limits leverage from individual conditions.
- Show the normalized profiles together rather than reporting only one optimum.
- Repeat the model-versus-null comparison with a **paired, clustered uncertainty analysis**. The 108 held-out observations are not 108 independent experimental units: they share conditions, coffee varieties, solutes, and fitted groups. A cluster bootstrap or hierarchical resampling over condition and group is preferable to treating points independently.
- For leave-one-condition-out evaluation, any interval intended to describe refitting uncertainty should repeat the fit inside the resampling loop. The current intervals resample already-computed fold errors and are correctly described as descriptive; they should not be given inferential prominence.

If a defensible uncertainty model cannot be reconstructed from the source data, the paper should make the profile primarily a **sensitivity analysis across plausible weighting schemes** and avoid inferential language altogether.

---

## Major Comment 5 — The Table 7 inventory constraint needs a dimensional audit

The manuscript treats the Angeloni Table 7 caffeine value as 12.54 g L⁻¹ and intersects it with the profiled `c_s0(rate)` curve. The repository's Angeloni source card records that the source concentration was reported on a mass basis and was mapped to mg L⁻¹ using an assumption equivalent to **1 kg = 1 L**.

That conversion is not a minor detail. A dry-coffee assay in mg kg⁻¹ cannot be equated directly to a model concentration in mg L⁻¹ without specifying the relevant volume basis. Depending on the model definition, a valid mapping may require some combination of:

- dry dose;
- bulk bed volume;
- solid-phase volume or skeletal density;
- bed porosity;
- moisture basis;
- extractable versus total assayed fraction; and
- any normalization used by the solver.

Until this mapping is written dimensionally from first principles, the claim that Table 7 gives a quantitative rate intersection is not secure. The ±10% perturbation does not address a possible basis mismatch, which could be much larger than 10%.

**Required action:** add a units table and a complete conversion equation. Propagate uncertainty in every conversion factor. If the model and assay bases cannot be reconciled, retain Table 7 only as qualitative evidence that an orthogonal inventory measurement could break the compensation—not as a numerical tie-breaker producing a rate of approximately 0.95.

This issue does **not** undermine the main observation that the beverage-only profile is broad. It does undermine the current quantitative strength assigned to the Table 7 intersection.

---

## Major Comment 6 — Clarify what is actually held out in the cross-grind analysis

The Angeloni campaign is independent of the source calibration campaign, but the reported cross-grind result is not a blind transfer of the source model:

- the model is recalibrated on Angeloni optimal-grind data;
- a target-specific level and rate multiplier are fitted for each solute/variety group;
- coarse and fine chemical concentrations are held out;
- the hydraulic mapping uses Angeloni-derived, grind-specific conductivity and nominal shot-time information.

The final point is important. Even though the flow map is not fitted to the target chemical concentrations, the mechanistic prediction receives target-campaign and target-grind hydraulic information. The evidence is therefore best described as:

> **a within-campaign cross-grind concentration holdout under target-derived hydraulic inputs and a matched-volume endpoint proxy.**

That is still a legitimate test. In fact, the finding that the mechanism barely improves on a constant despite receiving structured target-derived hydraulic information is scientifically interesting. But it should not be called mechanistic transfer without qualification.

In the abstract, replace language like “refitted to an independent endpoint campaign” followed by “transfer” with something explicit:

> “The model was recalibrated on one grind of a separate espresso campaign and evaluated on held-out conditions and grinds within that campaign.”

For the Waszkiewicz analysis, say:

> “The source kinetics were frozen while a target-specific concentration level was fitted to the independent trajectory; the test therefore evaluates temporal shape, not absolute concentration transfer.”

---

## Major Comment 7 — Promote the null comparison, but quantify its uncertainty correctly

The 8.2% versus 8.6% held-out MAPE comparison is one of the paper's strongest results. It turns an abstract identifiability concern into a practical model-evaluation lesson: a mechanistic model can appear adequate in absolute terms while contributing little beyond a learned level.

This result should appear earlier and more prominently. However, the manuscript currently alternates between a **0.4 percentage-point** difference and a **4% relative skill** statement. The latter sounds more impressive and is less intuitive. Use the absolute difference as the primary description:

> “The mechanistic model reduced pooled MAPE by 0.4 percentage points relative to the level-only baseline.”

Then report a paired uncertainty interval on the difference. Also show the group-level distribution of

\[
\Delta \mathrm{MAPE}=\mathrm{MAPE}_{\mathrm{mechanistic}}-\mathrm{MAPE}_{\mathrm{constant}}.
\]

A paired dot or interval plot by solute × variety × target grind would communicate the result more clearly than the current bar chart. The “worse on 50 of 108 points” count can remain descriptive, but it should not be treated as a sign test because the observations are dependent.

The in-sample comparator ladder should not be used to make model-selection claims unless it is evaluated with a penalty or out-of-sample procedure. The clean statement is:

> “In these six groups, the two-parameter shared mechanistic reconstruction did not outperform the three-level per-grind constant on the data used for fitting.”

That is already consequential; “explains essentially nothing” is unnecessary and stronger than the design supports.

---

## Major Comment 8 — Use profile terminology that matches the evidence

The paper is commendably careful in several places about the lack of a likelihood, but the JFE conversion still contains language that implies formal identification.

Recommended terminology:

- **profiled objective**, not profile likelihood;
- **near-optimal objective set** or **declared tolerance set**, not confidence region;
- **profile range ratio** or **edge-to-minimum objective ratio**, not identifiability ratio;
- **more/less strongly localized over the tested domain**, not identified/not identified based on one ratio;
- **local objective coupling**, not parameter correlation;
- **right-censored at the tested boundary**, retained prominently.

The 10%-above-minimum set is arbitrary. It is useful as a visual and descriptive threshold, but it should not be the sole measure of the valley. Show several normalized objective levels—such as 2%, 5%, 10%, and 20%—or the full profile on a log-rate axis. If a measurement-error model becomes available, add likelihood-based or bootstrap uncertainty separately.

The Hessian condition number is highly dependent on parameterization and local scaling even in log coordinates. It can remain as supporting geometry, but the paper should lead with the global profile and sensitivity-direction argument, which are easier to interpret and less fragile.

---

## Major Comment 9 — Rework the Waszkiewicz external trajectory analysis

The independent time-resolved TDS trajectory is useful because it moves the argument beyond the source model's own calibration campaign. It is also the part most vulnerable to accidental overinterpretation.

Several issues need attention:

1. **Twelve versus fourteen fractions.** The source publication describes an espresso divided into fourteen 5-second fractions, with the first collection interval empty. The manuscript reports a twelve-fraction trajectory. State exactly which bins were retained, excluded, merged, or unavailable and why.
2. **Replicate handling.** The source reports that the time-resolved TDS experiment was repeated three times and averaged. The manuscript mentions a single-replicate first bin with missing standard deviation. Reconcile these descriptions and show the data-preprocessing table.
3. **MAPE near zero.** The source trajectory approaches very low TDS at late times. MAPE can become unstable and heavily weight bins with small denominators. Repeat the profile with an absolute-error, log-error with an explicit floor, or uncertainty-weighted score. Show whether the best rate and profile contrast persist when near-zero bins are handled differently.
4. **Time alignment.** The 0/2/4 s offset sensitivity is helpful, but the observation operator should be written explicitly and aligned to measured bin masses or first-drip timing wherever possible.
5. **High minimum error.** A minimum MAPE around 27% means the frozen source kinetics do not reconstruct the external shape particularly well. Treat the result as a weak consistency check: the trajectory contains some rate-sensitive shape information under the model, not evidence that the model's rate is correct.
6. **The cup result is algebraic.** With one integrated scalar and one free multiplicative level, exact matching at every rate follows by construction. This should be one sentence or a schematic, not a headline empirical result.
7. **TDS comparability.** Optical refractometer TDS, gravimetric total solids, and the source model's pseudo-component are not equivalent analytes. The manuscript already recognizes this, but the visual design should make the distinction unavoidable.

The best external conclusion is:

> “Under a target-profiled level and the tested time-alignment assumptions, the independent TDS trajectory produced a shallow rate-dependent objective, whereas a single integrated scalar could not constrain the rate because its level was freely fitted.”

---

## Major Comment 10 — Keep the simulation as a didactic control, not as empirical evidence

The exact-integral simulation is useful because it separates the effect of temporal aggregation from the incomplete six-window sampling. It is also an inverse-crime design: the model generates the data and then fits itself. The manuscript acknowledges this, but the simulation occupies too much narrative space and accumulates many variants—on-grid truth, off-grid truth, heterogeneous noise, correlated noise, and model-discrepancy dose response.

Move most of these variants to the supplement. In the main text, retain one compact result:

- fraction-resolved synthetic observations produce a sharply rate-dependent objective;
- the exact whole-cup integral produces a much flatter objective after profiling the level;
- this is an information-content demonstration under correct model specification, not validation of a physical kinetic rate.

The empirical source-campaign fractions and the external Waszkiewicz trajectory should carry more narrative weight than the simulation.

---

## Major Comment 11 — Simplify the evidence hierarchy

The manuscript's evidence-tier discipline is a genuine strength, but the current prose turns it into a taxonomy that readers must continually decode. Lines 225–242 define many categories, and nearly every result ends with a “Strength:” label. This reads like repository governance rather than a journal article.

Use a single study-design table with columns such as:

| Dataset | Machine/coffee relation | Observable | Parameters fitted on that dataset | Held-out quantity | Role in paper |
|---|---|---|---|---|---|
| Schmieder/Pannusch | source calibration | fractions | original model calibration | none in this paper | in-sample information control |
| Angeloni O | independent campaign, target calibration | whole-cup named solutes | target level + rate | LOCO condition or off-grid O | target recalibration/internal holdout |
| Angeloni C/F | same campaign as target calibration | whole-cup named solutes | none after O fit | C/F concentrations | within-campaign cross-grind holdout |
| Angeloni Table 7 | same campaign, different measurement | dry-coffee assay | none | n/a | orthogonal inventory constraint, conditional on units |
| Waszkiewicz | independent rig and coffee | 5 s TDS trajectory | target level only | trajectory shape | external objective-localization check |
| Synthetic exact cup | same model | simulated fractions/cup | profiled level | known generating rate | didactic simulation |

Then use conventional phrases in the prose. The paper does not need both an internal evidence vocabulary and journal-facing prose.

---

## Major Comment 12 — Complete and tighten the literature/novelty analysis

The literature section is unusually long for an applied JFE paper and begins with generic identifiability theory before establishing the espresso problem. This contributes to the inaccessible tone you want to avoid.

Recommended sequence:

1. Whole-cup endpoints are common and convenient in espresso studies.
2. Extraction models contain parameters that can produce similar endpoint changes.
3. Practical-identifiability and profile methods provide established tools for testing this.
4. Prior coffee work has time-resolved fractions and mechanistic models, but the specific combination of whole-cup profile analysis, null benchmarking, and temporal-observation comparison appears to be missing.

The current novelty statement remains conditional on a documented scoping search, while the full indexed search is explicitly outstanding. Complete the Scopus/Web of Science or equivalent search before submission and archive:

- databases and dates;
- exact queries;
- inclusion/exclusion criteria;
- screening decisions for the closest studies; and
- a short table explaining how the present paper differs.

Avoid “we did not find” as the sole foundation of novelty. The contribution can be framed positively even if related work exists:

> “This study applies established practical-identifiability tools to quantify inventory–rate compensation in a multi-solute espresso model, combines that analysis with a trained null benchmark, and tests how temporal aggregation changes the rate profile.”

That is specific and defensible.

---

## Major Comment 13 — Remove revision history and repository scaffolding from the paper

The JFE manuscript still contains:

- the editorial conversion note at line 9;
- review IDs such as A2-09, A3-01, B1/B5, M4, and M6;
- code-function names in the main narrative;
- statements about bugs and unit tests;
- “delivered,” “owed,” “data-blocked,” and handoff language;
- references to earlier draft claims being overturned;
- a roadmap change log;
- author, declaration, caption, and reference placeholders.

This material is valuable provenance, but it belongs in repository documentation, a reproducibility supplement, or the response-to-reviewers file—not the article.

The final paper should report the corrected design directly. For example, replace:

> “That failure was mostly an artefact of the unmatched 25 s endpoint…”

with:

> “Predictions were evaluated at the same beverage endpoint as the observations; using a fixed 25 s integration window increased the apparent error and was therefore rejected as an unmatched observation operator.”

This preserves the methodological lesson without narrating the draft's history.

Tone also needs moderation. Phrases such as “this paper argues that reading is unsafe,” “curve fit masquerading as one,” “the decisive comparison,” and “the result is unambiguous” are rhetorically forceful but not necessary. Neutral alternatives will make the paper sound more authoritative, not less.

---

## Major Comment 14 — Reduce the main figure set and improve legibility

The current package contains eight figures, several of which are dense diagnostic composites. The core paper can be told with four or five main figures:

1. **Study design and observation operators.** Simplified version of current Figure 1.
2. **Whole-cup inventory–rate profile.** Current Figure 2, revised and paired with the local sensitivity-direction explanation.
3. **Held-out model versus level-only baseline.** A paired error-difference figure combining the strongest parts of Figures 3 and 4.
4. **Fraction-resolved versus aggregated rate profiles.** Simplified current Figure 6 for the source data and exact-cup simulation.
5. **Independent trajectory check.** Waszkiewicz profile, separated from the source/simulation panels if it remains in the main paper.

Move current Figures 5, 7, and 8 to supplementary material. They are useful diagnostics but interrupt the central argument.

Add three concise tables:

- dataset/evidence-role table;
- observation-adapter and structural-assumption table;
- summary of principal numerical results with the appropriate evidence label.

Detailed figure comments appear in Section 6 below.

---

## Major Comment 15 — Make the paper's scope accessible without diluting the science

The paper can be understandable to a non-specialist food engineer without abandoning rigor. Introduce each technical term only after a plain-language statement:

- **Extractable content (inventory):** how much of a compound is available to be released.
- **Extraction rate:** how quickly that available material enters the beverage.
- **Practical identifiability/localization:** whether the available measurements narrow a parameter to a useful range.
- **Observation operator:** how the model's time-dependent output is converted into the quantity actually measured.
- **Level-only baseline:** a model that predicts one learned concentration and contains no kinetic response.

Use “percentage points” at first occurrence instead of “pp.” Explain O, C, and F immediately as source labels for optimal, coarse, and fine granulometries. Define macro-MAPE and pooled MAPE in words.

The lay-accessible idea is simple and should appear in the first paragraph:

> A final cup records both how much soluble material was available and how much time the process had to release it. Different combinations of amount and rate can therefore produce nearly the same final concentration.

That statement invites the reader into the technical analysis rather than asking the reader to decode “kinetic parameter localization” first.

---

## 4. Section-by-section review

## 4.1 Title page and abstract — lines 1–15

### Strengths

- The abstract contains the key numerical comparison with the level-only baseline.
- It distinguishes the source fraction campaign from the target endpoint campaign.
- The final sentence correctly separates localization, accuracy, prediction, and null-model skill.

### Required changes

- Replace the title as recommended above.
- Delete the editorial note at line 9.
- The abstract is 237 words and contains too many technical diagnostics: Sherwood multiplier, ill-conditioning, 10% profile, multiple holdouts, shared-fit penalty, independent trajectory, and algebraic flatness. It is accurate but cognitively overloaded.
- Begin with the intuitive amount-versus-rate problem.
- State clearly that Angeloni is used for **target recalibration**, not blind external prediction.
- Use the 0.4-percentage-point model-versus-null difference as the principal held-out result.
- Mention the Waszkiewicz result as shallow and high-error in the same sentence that mentions its rate minimum.
- Remove “model transfer” from the keywords unless the title/text consistently qualify what is transferred. Better keywords include `whole-cup measurement`, `time-resolved extraction`, `parameter estimation`, `inverse problem`, and `model evaluation`.

A proposed abstract appears in Section 8.

---

## 4.2 Introduction — lines 18–50

### Strengths

- Lines 29–43 give a clear qualitative account of amount–rate compensation.
- The paragraph correctly limits the claim to the tested design and does not assert exact invariance.

### Required changes

- Lines 20–27 say cross-dataset checks are “almost always” performed on whole-cup quantities and that a good whole-cup error is read as evidence of physics. Cite this claim or soften it.
- Replace “This paper argues that reading is unsafe” with “That inference is not generally warranted.”
- Replace “two knobs” with “two fitted quantities” after the first accessible explanation.
- Replace “curve fit masquerading as one” at lines 45–50 with neutral language.
- Repair the stale section references (§3–§5 and §6). The current manuscript has Methods in Section 3, Results in Section 4, Discussion in Section 5, and Limitations in Section 6.
- End the introduction with three explicit research questions or hypotheses, for example:
  1. Do whole-cup endpoints localize extractable content and rate separately?
  2. Does the mechanistic model add held-out skill over a level-only baseline?
  3. Do time-resolved observations produce stronger rate-dependent objectives than integrated endpoints?

These questions would make the later results feel planned rather than accumulated.

---

## 4.3 Literature context — lines 54–135

### Strengths

- The paper correctly distinguishes structural from practical identifiability.
- It acknowledges that sloppiness and identifiability are not synonyms.
- It avoids claiming a new general identifiability method.

### Required changes

- Delete the repository-facing note at lines 56–61 from the manuscript.
- Reduce the generic identifiability review by at least one third.
- Move detailed methodological literature to a compact paragraph or supplement.
- Establish the espresso literature gap before the broader reaction–transport analogies.
- Complete the indexed novelty search before submission.
- Use a reproducible supplementary search protocol rather than describing an unfinished gate in the paper.
- Check all 2025–2026 references for final bibliographic status and consistency.
- Avoid a novelty claim that depends on four simultaneous distinctions being absent from every prior paper. Focus on the specific combined contribution you actually demonstrate.

---

## 4.4 Methods — lines 137–242

### Immediate defects

- The subsections under Section 3 are numbered **2.1–2.6**. Renumber them 3.1–3.6.
- Several cross-references still point to the working draft's old section numbers.

### Model — lines 139–154

- Add governing equations, outlet definition, and parameter table.
- Clarify the relationship between the model's internal fine/coarse particle classes and Angeloni's O/C/F granulometry categories.
- Explain whether the same rate multiplier is applied to both internal particle classes.
- State exactly why `c_s0` enters linearly and whether that linearity holds for every observation operator used.
- Distinguish the exact linearity in `c_s0` from the approximate compensation between `c_s0` and rate.

### Data — lines 156–174

- Add the dataset-role table.
- State the exact experimental unit and replicate handling for every campaign.
- Explain why six of ten Schmieder fractions are used and whether the omitted windows bias the sampled aggregate.
- Do not call the Angeloni campaign a “transfer target” without immediately explaining that it is recalibrated.
- Make clear that Table 7 is a same-campaign, different-measurement constraint.

### Endpoint and pressure-to-flow map — lines 176–202

- Delete “review A2-09.”
- The 40 g-to-40 mL approximation is material: the stated endpoint sensitivity is about 5.3 percentage points for the blind comparison. Put the adapter in a table and keep the conclusion conditional.
- Use “40 mL proxy for the nominal 40 ± 2 g endpoint” consistently.
- Explain whether crema, dissolved solids, and temperature affect the mass-to-volume conversion.
- The closeness of two tested flow maps at the endpoint does not validate the map form.
- State explicitly which hydraulic quantities come from Angeloni and therefore constitute target-derived inputs.
- Provide the map equations, units, and per-grind values in a table or supplement.

### Fitting protocol — lines 204–212

- Define the six solute × variety groups explicitly.
- State whether all groups use the same rate grid and bounds.
- Explain how target O off-grid points, LOCO folds, and C/F conditions are separated.
- Distinguish hyperparameter/model-selection decisions made before versus after inspecting target outcomes.

### Profile metric and evidence vocabulary — lines 214–242

- Replace the stale identifiability-ratio wording with the current working-draft language.
- Move the evidence taxonomy to the study-design table.
- Retain the statement that no likelihood is specified and that the threshold is not a confidence interval.
- Add the local sensitivity-direction criterion proposed in Major Comment 2.

---

## 4.5 Results 4.1 — lines 248–284

The heading “an apparent success” is rhetorical and does not tell the reader what was tested. A better heading is:

> **4.1 Matching the beverage endpoint changes the apparent cross-dataset error**

Specific comments:

- The bracketed note at lines 259–261 must be removed or converted into ordinary prose.
- The “strength” column in the table mixes design category and interpretation. Replace it with `Fit/test role` and use standard labels.
- Comparing the blind model with Angeloni's own ~9–13% model is not necessarily apples-to-apples unless the objective, analytes, and evaluation set are identical. Explain or remove.
- Remove the narrative about what changed from “our earlier draft.” Report the matched-endpoint result directly.
- The endpoint correction is a valuable methodological result but should not dominate the paper's opening result section. Consider moving the full sensitivity to the supplement and retaining one concise statement in Methods/Results.

---

## 4.6 Results 4.2 — lines 286–351

This is the core result and should be the first major scientific result after the study design.

### Strengths

- The manuscript correctly explains that exact inventory linearity plus weak variation in fractional extraction creates a compensation valley.
- It clearly labels the upper extent of the 10% set as right-censored.
- It distinguishes objective coupling from statistical correlation.
- It checks grid density and domain range.

### Required changes

- Add the sensitivity-direction derivation and a direct design interpretation.
- Correct the Table 7 unit issue before retaining the rate intersection.
- Port the current working-draft wording on the conditional intersection band.
- Remove code-function names and review IDs.
- Delete the bug-history sentence at lines 331–334.
- Do not say “the result is unambiguous” or “stronger than before.”
- Show profiles across all solute × variety groups in the supplement, not only selected examples.
- Explain why Figure 2 appears to use Arabica Table 7 values while its caption describes both varieties.
- Report a threshold-sensitivity family rather than relying only on 10%.

---

## 4.7 Results 4.3 — lines 353–453

A better heading is:

> **4.3 Cross-grind endpoint predictions add little skill over a level-only baseline**

### Strengths

- The section makes the essential distinction between parameter uncertainty and prediction stability.
- The level-only baseline is appropriately simple and relevant.
- The manuscript is candid that C/F are from the same campaign.
- Geometry, flow-scale, and loss-function sensitivities are useful.

### Required changes

- Use “40 mL matched-volume proxies” instead of “matched 40 g cups.”
- Remove all earlier-draft and review-ID discussion.
- Lead with the null result, not the absolute error table.
- Report uncertainty on the paired model-minus-null difference.
- Replace the “nested reduced-model ladder” with the current working-draft comparator language.
- Avoid the conclusion that the mechanism explains “essentially nothing.”
- Explain the target-derived hydraulic information used for C/F.
- The 10%-near-optimal set is a discrete grid subset, not a manifold. The manuscript acknowledges this, but the terminology should be consistent everywhere, including figures and code-facing captions.
- Move most of the LOCO resampling caveat and geometry/flow details to a robustness subsection or supplement. The main result currently becomes buried under methodological bookkeeping.

---

## 4.8 Results 4.4 — lines 455–551

A better structure would separate this into two subsections:

> **4.4 Time-resolved source data provide stronger rate information**  
> **4.5 Independent TDS trajectory: external shape check**

### Source fractions

- The empirical six-window aggregate is not a true cup and differs substantially from the actual brew-ratio cup. That limitation should appear before any fraction-versus-aggregate conclusion.
- Consider moving the sampled aggregate to the supplement and using the exact-cup simulation as the clean didactic comparison.
- Keep the source-data result explicitly in-sample.

### Simulation

- Condense substantially in the main text.
- Retain one statement about off-grid truth/noise robustness in the supplement.
- Avoid giving the simulation equal evidentiary weight to empirical data.

### External TDS

- Resolve the fraction-count and replicate inconsistencies.
- Test alternatives to MAPE for late, near-zero TDS bins.
- Show the exact flow-weighted interval operator.
- Keep the 27% minimum error next to the reported profile ratio.
- State that the target-specific level eliminates absolute concentration information.
- Move the algebraically flat one-cup curve to an inset or explanatory sentence.

---

## 4.9 Discussion — lines 553–595

### Strengths

- The “four distinct properties” framing is the manuscript's clearest conceptual contribution.
- The paper correctly says that prediction stability does not imply parameter estimability or mechanistic skill.
- The matched-observation-window lesson is valuable and broadly applicable.

### Required changes

- Repair all stale section references.
- Replace the internal “standing position” language with an ordinary synthesis paragraph.
- Remove references to superseding earlier readings.
- Discuss the target-derived hydraulic input, Table 7 dimensional issue, and uncertainty-model dependence as substantive limitations.
- Add the local sensitivity-design interpretation: informative experiments should create variation in the rate-sensitivity direction.
- Avoid saying independent inventory “would identify” the rate unless its measurement and mapping uncertainty are quantified. Say it can improve separation.

---

## 4.10 Limitations — lines 597–625

The current section is a project status register, not a journal limitations section. Rewrite it into four concise paragraphs:

1. **Source-data uncertainty and experimental dependence.** Central values, duplicates, unavailable replicate-level uncertainty, and non-independent CV folds.
2. **Observation adapters.** 40 g-to-40 mL proxy, inferred pressure-to-flow map, frozen geometry, and target-derived hydraulics.
3. **Parameter interpretation.** Rate multiplier is a model-specific scale, not a directly measured physical coefficient; Table 7 mapping is conditional.
4. **External scope.** One external TDS trajectory, one coffee/grind, target-profiled level, shallow/high-error fit, and lack of independent named-solute temporal data.

Remove “delivered,” “owed,” review IDs, and code names. Future work can then be stated briefly.

---

## 4.11 Conclusions — lines 627–629

The conclusion is disciplined overall, but one sentence is too broad:

> “an independent time-resolved dissolved-solids trajectory supplied shape information that a single integrated cup could not.”

For the external panel, the cup could not constrain the rate **by construction** because there was one scalar endpoint and one freely fitted scalar level. Revise to:

> “Under the tested target-profiled observation operator, the independent time-resolved dissolved-solids trajectory produced a shallow rate-dependent objective, whereas a single integrated scalar could not localize the rate after its level was freely fitted.”

The final reporting principle is strong and should remain.

---

## 4.12 Data/code, declarations, figures, and references — lines 631–687

- Replace the function inventory with a conventional data-and-code availability statement.
- Provide a permanent release, DOI, tagged commit, environment lockfile, and one documented command that reproduces each manuscript figure/table.
- Move function-level provenance to the supplement or repository README.
- Delete “Strength tags,” “not in CI,” and the change log from the article.
- Complete authorship, affiliations, CRediT, funding, competing-interest, and AI-use declarations.
- Include the final captions in the submission package.
- Generate and audit the complete reference list. A manuscript with a placeholder reference section is not ready for external review.

---

## 5. Detailed line-level editorial comments

| Lines | Comment | Recommended action |
|---:|---|---|
| 1 | Current title uses opaque “kinetic parameter localization.” | Use the recommended title in Section 1.3. |
| 9 | Editorial instruction is visible in manuscript. | Delete before any circulation outside the project. |
| 13 | Abstract contains too many metrics and evidence qualifications in one paragraph. | Rewrite around problem, design, profile result, null result, and temporal result. |
| 20–27 | “Almost always” and implied community practice are broad claims. | Cite or soften. |
| 29 | “This paper argues that reading is unsafe” is rhetorical. | Use “That inference is not generally warranted.” |
| 31–40 | “Two knobs” and “near-flat valley” are accessible, but parameter meaning should be defined more precisely. | Introduce plain-language terms, then technical notation. |
| 45–50 | Stale section references and “masquerading” language. | Correct references and neutralize tone. |
| 56–61 | Internal novelty-search note. | Move protocol details to supplement; complete search. |
| 85–90 | Careful distinction among profile objective, likelihood, and correlation. | Preserve, but shorten. |
| 115–119 | “Did not find” claim relies on unfinished search. | Complete indexed search and use a reproducible protocol. |
| 121–135 | Novelty paragraph repeats previous paragraph and is heavily qualified. | Merge into one concise contribution paragraph. |
| 139, 156, 176, 204, 214, 225 | Subsections numbered 2.x under Section 3. | Renumber 3.1–3.6. |
| 141–154 | Model cannot be reconstructed from this description. | Add equations, parameters, boundaries, and observation operator. |
| 148–153 | Exact linearity and weighted-median solution are important. | Derive explicitly in appendix and distinguish from approximate rate compensation. |
| 158–174 | Data roles are dense and mixed with evidence labels. | Add a dataset-role table. |
| 164–174 | Angeloni called independent target, but later fitted. | Use “separate target campaign used for recalibration.” |
| 178 | Review ID in heading. | Delete. |
| 179–192 | Mass-to-volume proxy and 5.3-point sensitivity are material. | Put in adapter table and maintain conditional language. |
| 194–202 | Multiple flow maps and target-derived hydraulics are hard to follow. | Add equations/table; distinguish inputs from fitted chemical parameters. |
| 206–210 | Per-solute/per-variety fitting groups need explicit enumeration. | Add a fitting-design table or schematic. |
| 216–223 | Stale “identifiability ratio” language overclaims. | Port the corrected profile-range-ratio wording. |
| 227–242 | Evidence taxonomy reads as repository governance. | Replace with one study-design table and ordinary terminology. |
| 250–255 | TDS/total-solids distinctions are important. | Preserve, perhaps in a boxed observation-compatibility note. |
| 259–261 | Bracketed editorial note remains. | Delete or rewrite as prose. |
| 263–268 | Table combines metrics with subjective “strength” labels. | Use fit/test role and dataset relation instead. |
| 270–278 | Prior-draft correction narrative. | Report final matched-endpoint result directly. |
| 288–291 | Product-like compensation is stated as “to good approximation.” | Quantify or link to sensitivity variation across conditions. |
| 299–301 | Says optimum is not a converged interior estimate, while later text says interior numerical minimum. | Port the corrected “interior but weakly localized” wording. |
| 302–314 | Table 7 rate constraint overstates precision and omits dimensional conversion. | Complete dimensional audit; use conditional language. |
| 316–338 | Dense numerical diagnostics obscure the profile. | Lead with profile; move condition number/Jaccard details to supplement. |
| 331–334 | Bug and unit-test history. | Remove from manuscript. |
| 340–348 | Domain checks are useful, but threshold remains arbitrary. | Keep concise; show multiple thresholds. |
| 350–351 | “Strength” label. | Integrate into normal prose. |
| 353 | “Frozen-parameter transfer” is too broad. | Use cross-grind endpoint prediction versus baseline. |
| 359–362 | “Matched 40 g cups” contradicts the 40 mL proxy. | Correct everywhere. |
| 370–377 | Earlier-draft and review IDs. | Remove. |
| 379–390 | Excellent null comparison. | Promote, report paired clustered uncertainty, use 0.4 percentage points primarily. |
| 392–403 | “Nested” is incorrect; “essentially nothing” overstates. | Port corrected comparator language. |
| 405–419 | Prediction stability across declared grid set is useful. | Keep but avoid “manifold”; move detailed tolerance ladder to supplement. |
| 421–453 | Robustness section is too long and uses project-status language. | Condense main text; provide full supplement. |
| 455–486 | Sampled aggregate is not a whole cup. | Reframe as incomplete-window aggregate and reduce prominence. |
| 488–516 | Simulation is detailed beyond its evidentiary role. | Move variants to supplement. |
| 518–551 | External test is valuable but has fraction-count, metric, and absolute-fit concerns. | Rework as in Major Comment 9. |
| 553–595 | Good conceptual synthesis mixed with stale references and revision history. | Retain conceptual distinction, rewrite completely. |
| 597–625 | Project checklist rather than limitations prose. | Replace with four concise limitations paragraphs. |
| 629 | “A single integrated cup could not” is too broad. | State the one-scalar/one-level construction explicitly. |
| 631–661 | Function inventory and strength tags are not a journal availability statement. | Replace with release/DOI/commit and supplement. |
| 663–687 | Submission placeholders remain. | Complete all fields and reference list. |

---

## 6. Figure-by-figure comments

## Figure 1 — Study design and evidence tiers

**What works:** The figure makes the campaign hierarchy visible and correctly distinguishes source calibration, target recalibration, internal holdouts, orthogonal measurement, simulation, and external shape testing.

**Problems:**

- Text is too small at normal journal width.
- The legend requires readers to decode several evidence categories before understanding the experiment.
- The note defining “external” is essential but visually subordinate.
- Arrows can still be interpreted as a validation ladder even though the caption says they show analysis order.

**Revision:** Use three horizontal rows—source campaign, Angeloni campaign, external campaign—with explicit boxes labeled `fit`, `held out`, and `level fitted only`. Put the observation operator under each dataset. Reduce the color taxonomy.

---

## Figure 2 — Inventory–rate objective surface

**What works:** This is the central figure. The compensation valley, profile curve, right-censored threshold set, Table 7 line, and local coupling are all visible.

**Problems:**

- The title is very long and embeds the conclusion.
- The dark brown/orange palette provides limited perceptual contrast and may not reproduce well.
- The legend sits over the data.
- The bottom panels truncate the normalized objective near 0.6, hiding the full edge behavior.
- The 10% threshold dominates even though it is analyst-selected.
- The figure shows Table 7 lines of approximately 12.54 and 7.97 g L⁻¹, which correspond to the Arabica values, while the standalone caption says the analysis includes nine conditions for each variety, 18 means per solute. Verify whether the plotted profiles are Arabica-only and correct the caption/methods accordingly.
- The condition number and coupling annotation looks like a statistical result without enough visual explanation.

**Revision:** Use a simpler sequential palette, place the legend outside, show the full normalized profile, overlay several objective thresholds, label the dataset/variety in each panel, and add a small sensitivity-direction inset or companion panel. Do not retain the Table 7 line until the units mapping is defended.

---

## Figure 3 — Leave-one-condition-out evaluation

**What works:** It shows predictions and signed residuals rather than only one pooled score.

**Problems:**

- The title contains too many numbers and caveats.
- Group encoding by both color and marker is difficult to decode.
- Temperature and pressure take only a few discrete values, so points overlap heavily.
- Fonts and legends are too small.
- The residual panels do not show uncertainty or the repeated/clustered nature of conditions.

**Revision:** Either facet by solute/variety or move the detailed residual panels to the supplement. In the main text, show a paired observed–predicted panel plus a distribution of held-out errors by group.

---

## Figure 4 — Cross-grind prediction and null benchmark

**What works:** This figure contains the strongest applied comparison and shows both prediction scatter and group-level errors.

**Problems:**

- The title's “pooled skill 4%” emphasizes the relative percentage; the clearer result is a 0.4-percentage-point difference.
- Legends overlap the scatter panels.
- The right-hand bar chart is crowded with abbreviations.
- A bar chart does not make paired model-minus-null differences easy to see.
- The phrase “model worse than constant on 50/108 points” is visually prominent without showing dependence or uncertainty.

**Revision:** Replace the bar chart with paired group-level differences and a clustered bootstrap interval for the pooled difference. Label groups in plain language or use a two-level facet. Keep absolute MAPE in a small table or caption.

---

## Figure 5 — Shared-parameter compatibility and comparator ladder

**What works:** It documents where the shared fit succeeds or fails and makes the in-sample comparator transparent.

**Problems:**

- The figure is too dense for a central narrative.
- Heatmaps, rate shifts, and the comparator ladder compete for attention.
- The title makes a strong claim about “0/6 fits” before explaining that models are non-nested, unequal in flexibility, and scored in-sample.
- Small labels will be unreadable after journal reduction.

**Revision:** Move the full figure to the supplement. Retain one compact main-text panel showing shared-fit versus per-grind-level error, clearly labeled as in-sample and descriptive.

---

## Figure 6 — Temporal resolution and rate profile

**What works:** This is conceptually central and visually demonstrates the difference between fraction-resolved and integrated observations.

**Problems:**

- It combines three evidence tiers—in-sample empirical data, same-model simulation, and independent external data—in one visual, encouraging readers to compare them as if equivalent.
- The external panel has a different error range and a much higher minimum, but visual adjacency can make the profiles look comparably successful.
- The algebraically flat single-cup external curve is a constructed consequence of one free level and one scalar observation.
- Legends and annotations are dense.

**Revision:** Split the external Waszkiewicz test into its own figure or supplementary figure. Use the main figure for source fractions versus sampled/exact cup only, with unmistakable labels `empirical in-sample` and `simulation`. Report the external 27% minimum directly in its panel title/caption.

---

## Figure 7 — Per-group blind and inventory-matched diagnostics

**What works:** It shows that inventory matching does not uniformly solve the residual and therefore discourages a simplistic inventory-only explanation.

**Problems:**

- The figure mixes MAPE bars and cross-condition correlations, which answer different questions.
- The correlation panel can be misread as predictive skill.
- Several labels and annotations overlap or are too small.
- The Table 7 unit-mapping concern affects the interpretation of the inventory-matched bars.

**Revision:** Move to the supplement. Retain only after the inventory conversion is resolved. Describe correlations explicitly as descriptive response-shape associations.

---

## Figure 8 — Residuals versus operating conditions

**What works:** It checks for structure that a pooled error can hide.

**Problems:**

- The figure contains large unused space and tiny panels.
- It shows pre-fit source-to-target residuals, not the residuals after target-level calibration that are more relevant to the paper's central claims.
- Discrete temperature/pressure values create overlapping points.

**Revision:** Replace with post-level-fit residual diagnostics or move to the supplement. Use jitter/faceting and include uncertainty where available.

---

## 7. Recommended manuscript structure

The current paper reads partly as a chronological record of corrections. A question-driven structure would be clearer.

## 1. Introduction

- Whole-cup espresso endpoints combine amount and rate information.
- Why endpoint accuracy may not imply a learned kinetic mechanism.
- Three research questions.
- Concise contribution statement.

## 2. Data, model, and observation operators

### 2.1 Datasets and experimental roles

One table covering Schmieder/Pannusch, Angeloni, Waszkiewicz, and simulation.

### 2.2 Extraction model and fitted quantities

Governing equations, inventory, rate multiplier, group structure, parameter domains.

### 2.3 Observation operators

Cup, fractions, target endpoint, time alignment, pressure-to-flow adapter.

### 2.4 Profile and evaluation methods

Objectives, analytical level fit, profile definition, local sensitivity-direction criterion, null baseline, holdout design, and uncertainty methods.

## 3. Whole-cup endpoints weakly separate content from rate

- Core profile surface.
- Global profile and right-censoring.
- Weighting/objective sensitivity.
- Conditional orthogonal-inventory result only if units are resolved.

## 4. Endpoint prediction is stable but adds little over a level-only baseline

- O-to-C/F held-out predictions.
- Paired model-minus-null comparison with clustered uncertainty.
- Near-optimal-set prediction stability.
- Brief robustness summary.

## 5. Time resolution supplies stronger rate information

- Source fraction comparison.
- Compact exact-cup simulation as didactic control.
- Independent Waszkiewicz shape check, clearly separated and qualified.

## 6. Discussion

- Observation design and sensitivity-direction variation.
- Distinction among localization, accuracy, prediction stability, and mechanistic skill.
- Implications for espresso experiments and food-process inverse problems.
- Limitations.

## 7. Conclusions

One paragraph with the bounded result and practical reporting recommendations.

### Supplement

- Full PDE and numerical implementation.
- All solute/variety profiles.
- Grid/domain/threshold sensitivity.
- Complete uncertainty and objective sensitivity.
- Flow/geometry/end-point robustness.
- Comparator ladder.
- Simulation variants.
- Residual diagnostics.
- Literature search protocol.
- Reproducibility manifest.

---

## 8. Proposed abstract rewrite

Whole-cup espresso measurements summarize an entire extraction in one endpoint. That endpoint may be predicted accurately even when a model cannot distinguish how much soluble material was available from how quickly it was released. We examined this issue with a multi-solute espresso extraction model previously calibrated to fraction-resolved data and recalibrated on one grind of a separate whole-cup campaign. At a matched beverage endpoint, profiles of extractable content and mass-transfer rate formed a broad compensating valley: many parameter pairs gave similar error, and the near-optimal rate range reached the upper search boundary. When the recalibrated model was evaluated on coarse and fine grinds within the same campaign, its pooled mean absolute percentage error was 8.2%, only 0.4 percentage points lower than that of an optimal-grind level-only baseline, and it was worse on 50 of 108 observations. Fraction-resolved source data produced substantially stronger rate-dependent objectives than aggregated endpoints. An independent second-rig dissolved-solids trajectory showed the same qualitative direction, although its minimum was shallow and high-error. Endpoint accuracy, parameter localization, and predictive skill over a simple baseline are therefore distinct properties. Espresso-model validation should match the measurement window, include null-model comparisons, and use time-resolved fractions or independently measured extractable content when kinetic interpretation is required.

**Suggested keywords:** espresso; whole-cup measurement; extraction rate; parameter estimation; practical identifiability; time-resolved extraction; model evaluation; experimental design

---

## 9. Priority action list

## P0 — Submission-blocking

- [ ] Select one canonical manuscript source and regenerate the JFE version from it.
- [ ] Port all corrected evidence language from the authoritative draft.
- [ ] Complete uncertainty-weighted and alternative-objective profile analyses.
- [ ] Quantify paired uncertainty for the model-versus-level-only comparison.
- [ ] Resolve the Table 7 dimensional conversion or remove the numerical rate intersection.
- [ ] Add standalone model and observation-operator equations.
- [ ] Complete the indexed novelty search and final reference list.
- [ ] Remove all review IDs, prior-draft history, bug notes, “delivered/owed” language, and placeholders.
- [ ] Repair section numbering and every cross-reference.

## P1 — Scientific presentation

- [ ] Adopt a descriptive espresso title.
- [ ] Rewrite the abstract around amount versus rate, not diagnostics.
- [ ] Reorganize the paper around the observation operator.
- [ ] Add the local rate-sensitivity variation criterion.
- [ ] Reframe Angeloni C/F as a within-campaign chemical holdout under target-derived hydraulics.
- [ ] Rework the Waszkiewicz analysis for fraction count, replicate handling, near-zero MAPE sensitivity, and time alignment.
- [ ] Reduce the main figure set to four or five figures.
- [ ] Add dataset-role, adapter/assumption, and principal-results tables.

## P2 — Editorial polish and reproducibility

- [ ] Standardize `extractable content/inventory`, `rate multiplier`, and `extraction rate` terminology.
- [ ] Define O/C/F, macro-MAPE, pooled MAPE, and percentage points at first use.
- [ ] Use one spelling convention consistently.
- [ ] Create a permanent tagged release with DOI and pinned environment.
- [ ] Supply a concise journal-style data/code availability statement and a detailed reproducibility supplement.
- [ ] Complete title-page and declaration material.

---

## 10. Strengths that should be preserved

1. **The level-only baseline.** This is the analysis that makes the paper practically important rather than merely diagnostic.
2. **The distinction among four properties:** parameter localization, endpoint accuracy, prediction stability, and incremental skill.
3. **The matched-observation-window lesson.** Correctly mapping model output to the measured endpoint is essential and broadly applicable.
4. **The right-censoring disclosure.** The manuscript does not pretend that the upper profile bound is closed.
5. **The separation of named solutes from incompatible TDS/total-solids proxies.** This is careful and should remain explicit.
6. **The candid treatment of the external trajectory.** Keeping the shallow minimum and high error visible is scientifically honest.
7. **The repository's provenance and regeneration discipline.** This should support the paper through a supplement and permanent release, even though the internal governance language should be removed from the article.
8. **The negative result.** Showing that a mechanistic model can be nearly matched by a simple baseline is valuable knowledge and should not be softened into a conventional success narrative.

---

## 11. Bottom line

Paper 1 contains a publishable and potentially influential message for espresso modelling and food-process inverse problems: **a good final-cup prediction can coexist with poor information about the process rate, and mechanistic complexity must earn its place against a simple baseline.**

The title should state that message directly rather than relying on “the cup hides the clock.” The recommended title is:

# **Separating Extractable Content from Extraction Rate in Espresso Models: Limits of Whole-Cup Data and the Value of Time-Resolved Measurements**

The paper should be considered ready for submission only after the uncertainty analysis, Table 7 dimensional mapping, version synchronization, standalone Methods, and full editorial cleanup are complete. Those changes would not alter the core contribution; they would make it easier to understand, harder to misinterpret, and substantially more credible.

---

## Sources reviewed

### Repository sources

- [JFE conversion manuscript at the reviewed commit](https://github.com/trbrewer/puckworks/blob/85af247acdf7bdb611d5b5b28b7e09e878ecc3ac/docs/submission/PAPER_A_JFE_MANUSCRIPT.md)
- [Authoritative Paper A working draft at the reviewed commit](https://github.com/trbrewer/puckworks/blob/85af247acdf7bdb611d5b5b28b7e09e878ecc3ac/docs/PAPER_A_DRAFT.md)
- [Current-document index](https://github.com/trbrewer/puckworks/blob/main/docs/CURRENT.md)
- [Paper A reviewer brief](https://github.com/trbrewer/puckworks/blob/85af247acdf7bdb611d5b5b28b7e09e878ecc3ac/docs/REVIEWER_BRIEF_PAPER_A.md)
- [Paper A figure captions](https://github.com/trbrewer/puckworks/blob/85af247acdf7bdb611d5b5b28b7e09e878ecc3ac/docs/figures/PAPER_A_CAPTIONS.md)
- [Paper A figures](https://github.com/trbrewer/puckworks/tree/main/docs/figures/paper_a)
- [Angeloni source/model card](https://github.com/trbrewer/puckworks/blob/85af247acdf7bdb611d5b5b28b7e09e878ecc3ac/docs/cards/angeloni2023.md)
- [Publication strategy review identifying Paper 1's central contribution](https://github.com/trbrewer/puckworks/blob/main/docs/PUBLICATION_STRATEGY_REVIEW.md)

### Key primary publications cross-checked

- Angeloni et al. (2023), *Computer Percolation Models for Espresso Coffee: State of the Art, Results and Future Perspectives*, *Applied Sciences* 13, 2688.
- Schmieder et al. (2023), *Influence of Flow Rate, Particle Size, and Temperature on Espresso Extraction Kinetics*, *Foods* 12, 2871.
- Pannusch et al. (2024), *Model-based kinetic espresso brewing control chart for representative taste components*, *Journal of Food Engineering* 367, 111887.
- Waszkiewicz et al. (2026), *Under pressure: Poroelastic regulation of flow in espresso brewing*, *Physics of Fluids* 38, 063113.
