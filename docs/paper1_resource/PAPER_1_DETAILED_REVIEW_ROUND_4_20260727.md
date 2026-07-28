# Fourth Detailed Review of Paper 1 / Paper A

## Manuscript reviewed

**Current title:** *Separating Extractable Content from Extraction Rate in Espresso Models: Limits of Whole-Cup Measurements and the Value of Time-Resolved Data*

**Repository:** `trbrewer/puckworks`

**Review date:** 27 July 2026

**Repository state reviewed:** `main` at commit `352dacd51015d95a3b5a5b3e1a8fb331419d78b0`.

**Principal Paper 1 revision reviewed:** commit `085165c27b22404b137eb819095865412623d56d` (*Paper 1: action the third detailed review; endpoint + PDE convergence closed*), together with the subsequent integration/fix commits present at the reviewed head.

**Primary files and artifacts reviewed:**

- `docs/submission/PAPER_A_JFE_MANUSCRIPT.md`
- `docs/PAPER_A_DRAFT.md`
- `docs/submission/PAPER_A_JFE_SUPPLEMENT.md`
- `docs/submission/PAPER_A_JFE_PACKAGE.md`
- `docs/submission/PAPER_A_JFE_HIGHLIGHTS.txt`
- `docs/submission/PAPER_A_JFE_COVER_LETTER.md`
- `docs/submission/paper_a_front_matter.yaml`
- `docs/figures/PAPER_A_CAPTIONS.md`
- the available eight-figure contact sheet
- `docs/paper1_resource/PAPER_A_ENDPOINT_PROPAGATION.json`
- `docs/paper1_resource/PAPER_A_NUMERICAL_CONVERGENCE.json`
- `docs/paper1_resource/PAPER_A_OBJECTIVE_FAMILY_PANELS.json`
- `docs/paper1_resource/PAPER_A_P0-5_RESULTS.md`
- `docs/paper1_resource/PAPER_A_TABLE7_UNITS_AUDIT.md`
- `docs/reproducibility/paper_a_manifest.json`
- `puckworks/figures_paper_a.py`
- the Paper A slow-analysis producers and result contracts relevant to the reported analyses
- `tools/paper_a_front_matter.py`
- `tools/paper_a_references.py`
- `tools/paper_a_consistency.py`
- `tools/paper_a_supplement.py`
- the relevant source-model documentation and the original Wilke–Chang correlation

I did **not** independently rerun the complete slow PDE, bootstrap, endpoint-propagation, and figure-production campaigns. I audited the exact pinned manuscript and package, machine-readable result records, implementation contracts, figure generators, available rendered contact sheet, consistency/release checks, and external constitutive source. Numerical comments below therefore distinguish between: (i) results verified from committed records; (ii) static implementation and provenance findings; and (iii) analyses that should be rerun after a correction.

---

# Recommendation

## **Major revision before submission**

Paper 1 has improved substantially. The central scientific result is now coherent, unusually candid, and plausibly publishable:

1. the whole-cup observation design leaves extractable inventory and the model's mass-transfer-rate multiplier weakly separated;
2. the recalibrated process model predicts held-out coarse/fine conditions with modest absolute error but is nearly matched by a level-only comparator; and
3. time-resolved measurements retain extraction-shape information that is largely removed by aggregation to a single endpoint.

Several important requirements from the previous review have been closed. Front matter is now generated from a single source; all six solute-by-variety objective panels are archived; the complete 38/40/42 mL benchmark propagation has been run; a spatial-grid/tolerance study has been added; a supplement now exists; and the consistency framework has been expanded.

The paper is nevertheless not ready to submit. The present submission object contains **direct internal contradictions, a broken supplementary cross-reference, an unverified constitutive equation, overbroad numerical-convergence wording, stale release provenance, and journal-facing files that still read as repository review records rather than polished scientific material**.

My overall assessment is:

> **The scientific core is now close to external-review quality. The remaining blockers are concentrated and fixable, but several are scientifically load-bearing rather than merely editorial.**

---

# Executive summary of this review

## The strongest advances since the third review

| Previous blocker | Current status | Review assessment |
|---|---|---|
| Front matter drift across manuscript/package/highlights/cover letter | One YAML source now generates the principal front-matter blocks | **Substantially resolved mechanically.** Author, declaration, novelty, and release fields remain unresolved. |
| Missing/incomplete objective-family sweep | Six solute × variety panels and three objectives are archived | **Resolved.** The 16/18 boundary-reaching result is supported. |
| Endpoint uncertainty not propagated through the headline benchmark | Full O-fit → C/F prediction → null comparison run at 38/40/42 mL | **Resolved analytically, but not reconciled everywhere in prose.** |
| PDE discretization convergence absent | 100/200/400 nodes × three tolerances archived for one representative panel | **Useful local evidence added.** The manuscript overgeneralizes it and misdescribes the Jacobian. |
| No supplementary file | A generated supplement now exists | **Mechanically resolved, editorially incomplete.** It is not yet journal-ready and omits promised items. |
| Bibliography coverage defects | Citation extraction expanded and 39 references reportedly resolve | **Substantially improved.** A final typeset-reference audit remains prudent. |
| Narrow consistency check | More checks and a submission mode now exist | **Improved, but still capable of false passes on scientifically meaningful contradictions.** |

## The most important new or remaining blockers

1. **Methods says the full endpoint-propagated transfer estimand was “not evaluated here,” while Results reports that completed analysis.** The package also still lists endpoint propagation as outstanding.
2. **The manuscript promises Supplementary Table S2, but the supplement defines Note S2 and no Table S2.** The checker loses the item type and therefore allows this false pass.
3. **The paper calls its diffusivity equation Wilke–Chang while placing the solute molecular weight in the solvent molecular-weight term.** This must be traced to the original Pannusch implementation and either corrected or explicitly described as a nonstandard source-model closure.
4. **The numerical-convergence record says “analytic Jacobian sparsity pattern,” but the same record says SciPy used a numerical Jacobian with a supplied sparsity pattern.** The convergence conclusion also extends one Arabica-caffeine panel to the whole paper.
5. **The supplement is still an internal audit dossier:** review-ticket language, producer paths, capitalized adjudication prose, non-sequential numbering, a malformed table header, and no embedded supplementary figures.
6. **The reproducibility manifest is stale:** old source commit, dirty tree, null timestamp, bundle/head mismatch, no fresh release, and a retained claim for the retired Table 7 implied-rate intersection.
7. **The main Figure 2 caption claims both coffee varieties, while the figure producer loads Arabica caffeine and Arabica trigonelline only.** The rendered panel and caption therefore do not describe the same data scope.
8. **Novelty search, authorship, declarations, release DOI, and release commit remain unresolved**, while the cover letter already asserts author approval and competing-interest status.

---

# Title assessment

## Recommendation: **retain the current title**

> **Separating Extractable Content from Extraction Rate in Espresso Models: Limits of Whole-Cup Measurements and the Value of Time-Resolved Data**

This remains the best title used for Paper 1. It:

- contains **“espresso”**;
- names the two quantities the paper seeks to separate;
- states both the limitation and the constructive experimental-design lesson;
- is understandable to a broad food-engineering audience;
- avoids the obscurity of “kinetic parameter localization”; and
- avoids the glib, promotional tone of “The cup can hide the clock.”

A shorter acceptable alternative is:

> **Separating Extractable Content from Extraction Rate in Espresso: What Whole-Cup and Time-Resolved Measurements Reveal**

The shorter alternative is not necessary unless the editor requests compression. I recommend treating the present title as fixed and preventing further drift through the existing front-matter generator.

---

# Assessment of the central evidence

## 1. Weak inventory–rate localization

The strongest support comes from the exact multiplicative factorization of inventory, followed by profiled objectives across the rate domain. The paper is right to distinguish:

- an interior numerical minimum;
- the breadth and boundary-censoring of a declared near-optimal set; and
- the scoped interpretation of weak practical localization.

Across six solute-by-variety panels and three objective families, 16 of 18 10%-near-optimal sets reach a tested rate boundary. This is persuasive evidence that the point optimum is not a robust mechanistic estimate under the tested single-grind endpoint design. The manuscript is also right not to call the profiled objective a likelihood when no noise model is specified.

The term **“practical non-identifiability”** should remain carefully scoped. The evidence supports “weak localization under this model, observation operator, parameter domain, objective, and experimental design.” It does not establish structural non-identifiability or a universal inability of endpoint data to constrain rate.

## 2. Cross-grind prediction versus the level-only comparator

The committed endpoint-propagation record gives:

| endpoint proxy | mechanistic pooled MAPE | level-only MAPE | model − null | primary clustered sensitivity range | model worse on |
|---:|---:|---:|---:|---:|---:|
| 38 mL | 8.17% | 8.59% | −0.421 pp | [−0.791, −0.028] pp | 51/108 |
| 40 mL | 8.23% | 8.59% | −0.361 pp | [−0.725, +0.027] pp | 50/108 |
| 42 mL | 8.20% | 8.59% | −0.392 pp | [−0.778, +0.010] pp | 49/108 |

Two readings must be kept together:

- **Practical effect size:** the difference is tiny and stable, only about 0.36–0.42 percentage points.
- **Threshold/inferential reading:** the declared primary range narrowly excludes zero at 38 mL but includes zero at 40 and 42 mL.

The paper should therefore avoid an unqualified statement that the model provides “no resolvable skill” across the whole endpoint range. The defensible statement is:

> At the nominal 40 mL proxy, the gain over the level-only comparator was 0.36 percentage points and the declared primary clustered sensitivity range included zero. Across 38–42 mL, the effect remained practically small, although whether the range crossed zero depended on the endpoint proxy.

This is stronger scientifically than forcing a binary “significant/not significant” verdict. It shows that the practical conclusion is stable while the boundary-crossing classification is not.

## 3. Time-resolved versus integrated observations

The source-campaign fraction analysis and same-model exact-cup simulation both support the information-content contrast. The empirical sampled-window aggregate is not a complete cup, but the same-model exact-integral experiment addresses that concern under the assumed model.

This remains a **positive control**, not independent validation:

- the source fraction data are the model's own calibration data;
- the same-model simulation is an inverse crime;
- the external dissolved-solids trajectory is an aggregate proxy with one rig, coffee, grind, and averaged trace; and
- the external preference is shallow, high-error, and loss-dependent.

The paper's best conclusion is therefore “time-resolved observations carried more rate information in the tested model and designs,” not “time-resolved data identify the physical extraction rate.”

---

# P0 submission blockers

## P0-1. Reconcile the completed endpoint analysis everywhere

### Direct contradiction

Methods §2.4 says:

> “This sweep quantifies the blind O-grind discrepancy only; it is not the O-refit→C/F transfer estimand … [that is] a separate estimand, not evaluated here.”

Results §4 then reports the complete O-refit → C/F transfer → level-only-null analysis at 38, 40, and 42 mL. The package also lists “the 38/40/42 mL endpoint propagation” among work that remains before submission.

This is not a harmless history note. It causes the paper to make three incompatible statements about whether a headline sensitivity analysis exists.

### Required correction

Rewrite §2.4 so it distinguishes the two completed endpoint analyses:

1. **blind optimal-grind residual sensitivity**, which moves by about five percentage points; and
2. **full transfer-versus-null benchmark propagation**, whose paired difference stays between −0.36 and −0.42 percentage points but whose primary range crosses zero at two of three proxies.

A concise replacement would be:

> We evaluated endpoint-proxy sensitivity for two distinct estimands. First, the blind optimal-grind discrepancy was recalculated at 38, 40, and 42 mL. Second, the complete optimal-grind fit, frozen coarse/fine prediction, level-only comparison, and paired clustered resampling were repeated at each endpoint. These analyses are reported separately because a common endpoint-induced shift can cancel in the model-minus-null contrast even when it materially changes the blind residual.

Remove endpoint propagation from the package's outstanding list. Add a consistency test requiring the endpoint result record, Methods status, Results table, abstract, package, and supplement to agree that the analysis is complete.

### Acceptance test

A repository-wide search for `not evaluated here`, `endpoint propagation`, and `outstanding` should return no contradictory status statement.

---

## P0-2. Audit the Wilke–Chang diffusivity closure against the original source

### The issue

The manuscript writes:

\[
D_i(T)=7.4\times10^{-15}\frac{(2.6M_i)^{1/2}T}{\eta(T)V_i^{0.6}}
\]

and defines \(M_i\) as the **solute molecular weight**, calling the expression “the Wilke–Chang relation.”

In the standard Wilke–Chang correlation, the numerator contains \((\phi_B M_B)^{1/2}\), where \(\phi_B\) is the **solvent association factor** and \(M_B\) is the **solvent molecular weight**. The molar-volume term belongs to the solute. For water, \(\phi_B\) is commonly taken as 2.6 and \(M_B\) is the molecular weight of water, not caffeine, trigonelline, or 5-CQA.

The current equation mixes a water-specific association factor with a solute-specific molecular weight. A unit test that reproduces the implemented expression proves implementation consistency, but it does not prove that the physical correlation has been transcribed correctly.

### Why this matters

This may be one of three things:

1. **A manuscript notation error:** the code uses solvent molecular weight but the text says solute.
2. **A faithful reproduction of a nonstandard source implementation:** Pannusch's model/code may itself substitute solute molecular weight.
3. **A port or source error:** both the code and manuscript may have inherited the wrong variable.

The scientific consequences differ. Because the Sherwood prefactors are solute-specific and were fitted in the source model, a constant solute-specific rescaling of diffusivity may be partly or even largely absorbed by those fitted prefactors. That possibility does **not** make the issue ignorable: it affects physical interpretation, comparability of the parameters, and whether the paper may call the closure Wilke–Chang without qualification.

### Required correction

1. Inspect the original Pannusch article, supplement, and source MATLAB/code, not only the puckworks card.
2. Record exactly which molecular weight the published implementation uses.
3. If the original source uses solvent molecular weight, correct the port and rerun all dependent calibrations/results.
4. If the original source deliberately uses solute molecular weight, describe it as the **Pannusch source-model diffusion closure** and state explicitly that it differs from standard Wilke–Chang notation.
5. Run a reparameterization/sensitivity test showing whether replacing the term with standard \(M_B\) changes:
   - fitted Sherwood prefactors or their transformed equivalents;
   - the rate-profile geometry;
   - the 8.23% versus 8.59% benchmark;
   - the fraction-versus-cup localization contrast; and
   - the external trajectory result.
6. Add a source-trace test that checks the equation against the archived source expression, not merely against itself.

### Recommended manuscript wording if the source is nonstandard

> Diffusivity follows the closure implemented in the Pannusch source model. Its numerator uses the analyte molecular weight together with the water association factor; this differs from the conventional Wilke–Chang form, which uses the solvent molecular weight. We retain the source closure for faithful reproduction and assess the standard-form substitution in sensitivity analysis.

Do not submit the paper with the current unqualified statement until this audit is complete.

---

## P0-3. Remove or correctly supply the nonexistent Supplementary Table S2

### The contradiction

The manuscript first says that the Table 7 assay and fitted inventory are not demonstrably commensurate and that **no quantitative rate intersection is claimed**. It then says:

> “The numerical implied-rate intersection is reported in Supplementary Table S2…”

The supplement defines:

- Supplementary Note S1;
- Supplementary Note S2;
- Supplementary Table S1;
- Supplementary Table S3;
- Supplementary Table S5; and
- Supplementary Table S6.

There is no Supplementary Table S2. The reproducibility manifest still verifies a retired claim, “Table 7 inventory implies caffeine rate ~0.95.”

### Why the checker passes

`_supplementary_targets()` extracts only the token `S2`, not the pair `(Table, S2)`. The presence of **Note S2** can therefore satisfy a promise for **Table S2**. This is a classic false-pass caused by discarding semantic type information.

### Recommended scientific resolution

The cleanest solution is **not** to create a rate-intersection table. The paper has correctly concluded that the mass-to-volume basis is undefended and the two inventory quantities are not demonstrably commensurate. A numerical intersection under an arbitrary basis invites exactly the interpretation the prose rejects.

I recommend:

- delete the sentence promising Supplementary Table S2;
- remove the retired implied-rate claim from the manifest and result bundle;
- retain Supplementary Note S2 as a dimensional audit; and
- state only the design lesson: an independently anchored inventory measurement could add a sensitivity direction that helps intersect the profile valley.

If the authors insist on retaining a numerical illustration, it must be explicitly labelled **noninferential and basis-conditional**, show the whole plausible basis range, and never be reported as an implied physical rate.

### Checker correction

Compare typed identifiers:

```text
(Table, S2), (Figure, S3), (Note, S2), ...
```

not only `S2`. Require sequential numbering or an explicit, justified skip. Also verify that every promised supplementary figure exists in the supplement package.

---

## P0-4. Correct the Jacobian description and narrow the numerical-convergence claim

### Internal inconsistency

The manuscript and Supplementary Table S6 say the BDF integration uses “an analytic Jacobian sparsity pattern.” The machine-readable convergence record says SciPy emitted warnings in `num_jac`, and clarifies:

> “The solver supplies a Jacobian SPARSITY pattern but not an analytic Jacobian, so scipy estimates entries by finite differences.”

A sparsity pattern is not an analytic Jacobian. The accurate wording is:

> “stiff BDF integration with a supplied Jacobian sparsity pattern and a numerically estimated Jacobian.”

### Scope problem

The convergence campaign covers one panel:

- Arabica;
- caffeine;
- optimal grind;
- nine conditions;
- 100/200/400 axial nodes; and
- tolerances 10⁻⁵/10⁻⁶/10⁻⁷.

The resulting agreement is excellent for that representative calculation: whole-cup, late-fraction, and range-ratio variations are tiny, and the profiled minimum is invariant. It supports **local numerical stability for the tested panel**.

It does not, by itself, establish that:

- all solutes are converged;
- the 5-CQA or highest-rate stiffness is covered;
- the external time-varying-flow trajectory is converged;
- every positive-control fraction profile is converged; or
- “the weak-localization result” across all panels cannot be numerical.

### Required correction

Change the conclusion to:

> For the representative Arabica-caffeine optimal-grind panel, the reported observables and profile summary were insensitive to the tested axial resolutions and BDF tolerances. This supports numerical stability of that panel; it is not a global convergence proof for every solute and trajectory used in the paper.

Then either:

- add a small worst-case panel set (e.g., 5-CQA, a high-rate cell, and the external time-varying-flow trajectory); or
- explicitly retain the representative-panel limitation.

The six RuntimeWarnings should remain disclosed, but the claim that they “do not affect” results should be based on successful solver status, finite states, mass-balance/positivity checks, and agreement—not only on agreement with another configuration that may exercise the same numerical path.

Also specify the exact objective and observable used for the convergence profile. The archived convergence minimum should be directly reconcilable with the formal objective-family panel or clearly identified as a different profile construction.

---

## P0-5. Rebuild the supplement as a journal supplement, not a review ledger

The existence of `PAPER_A_JFE_SUPPLEMENT.md` is progress, but its current form is not suitable for an editor or reviewer.

### Current problems

- Heading: “Paper A — Table 7 inventory-constraint dimensional audit (review MC5 / P0-4).”
- Subheadings: “Question (review MC5),” “Recommendation (implemented in this PR),” and “To make it quantitative later (owed; out of scope here).”
- Producer paths and Python function names appear in the scientific supplement.
- Adjudication prose uses capitalized terms such as “HOWEVER,” “EXCLUDES,” “CONVERGED,” and “IDENTICAL.”
- Numbering jumps S1 → S3 → S5 → S6.
- Supplementary Table S3 has an empty header cell between the primary interval and the secondary range.
- The manuscript/caption package promises supplementary figures, but the supplement contains no figure objects or figure-placement references.
- Table S6 says “analytic Jacobian sparsity pattern,” contradicting its own warning paragraph.
- The Table 7 audit mixes scientific explanation with repository history and future-work bookkeeping.

### Required structure

Create a clean journal supplement such as:

1. **Supplementary Methods S1:** extended identifiability definitions and objective construction.
2. **Supplementary Methods S2:** endpoint-proxy and external-trajectory processing.
3. **Supplementary Table S1:** all fitted parameters and boundary flags.
4. **Supplementary Table S2:** objective-family and threshold robustness—if retained under that number.
5. **Supplementary Table S3:** endpoint propagation.
6. **Supplementary Table S4:** external-trajectory loss/alignment sensitivity.
7. **Supplementary Table S5:** numerical convergence.
8. **Supplementary Figures S1–S4:** the actual rendered figures with captions.

Keep repository producer names, hashes, and review-ticket history in a separate **reproducibility audit document**, not in the submitted SI.

### Acceptance criteria

- Sequential item numbering.
- Every main-text SI reference resolves by both type and number.
- Every supplementary figure is physically included in the submission bundle.
- No `review`, `PR`, `owed`, `producer`, internal path, or implementation-status prose remains in the journal SI unless scientifically necessary.
- Tables render correctly in Word/PDF with no empty or shifted columns.

---

## P0-6. Regenerate the reproducibility manifest from the exact release candidate

The manifest reports 63 claims with zero numerical failures, which is useful, but the provenance state is explicitly non-release:

- `source_commit`: `7ec68b4...`, not the reviewed head;
- `git_dirty`: `true`;
- `timestamp_utc`: `null`;
- `bundle_source_commit`: `5bcc71...`;
- `bundle_matches_head`: `false`; and
- `release_fresh`: `false`.

It also retains the scientifically retired Table 7 implied-rate claim and appears not to cover all newly added endpoint-propagation and numerical-convergence claims.

### Required correction

After all scientific edits:

1. create a clean worktree at the final Paper 1 commit;
2. rebuild every slow result bundle and figure from that exact commit, or document which frozen records are intentionally reused and why;
3. regenerate the manifest with a non-null UTC timestamp;
4. include hashes for manuscript, supplement, front matter, data, code, figures, and result records;
5. assert `git_dirty=false`, `bundle_matches_head=true`, and `release_fresh=true`;
6. add claims for the endpoint-propagation table and convergence record;
7. remove retired claims that the manuscript no longer makes;
8. archive the environment lock and solver/library versions; and
9. mint the archival DOI only after this state is frozen.

A numerical claim checker should also verify claim **coverage**, not just correctness of the claims it happens to contain. Otherwise, new headline numbers can enter the manuscript without entering the manifest.

---

## P0-7. Resolve novelty, authorship, declarations, and cover-letter assertions

The front-matter YAML correctly turns unresolved fields into explicit nulls:

- authors;
- affiliations;
- corresponding author;
- ORCIDs;
- CRediT roles;
- funding;
- competing interests;
- generative-AI declaration;
- release DOI;
- release commit; and
- indexed novelty-search metadata.

The manuscript also says the licensed/indexed novelty search has not yet been run and that the novelty sentence will be revised afterward.

These are genuine submission blockers. More importantly, the current cover letter already says:

> “all authors have approved the submission”

and

> “We declare no competing interests beyond those stated in the manuscript.”

Those statements cannot be made safely while the author list and competing-interest field are null.

### Required correction

- Complete the Scopus/Web of Science—or equivalent licensed—search and archive database, exact query, date, screening criteria, and inclusion decisions.
- Revise the priority claim to match the archived search.
- Obtain explicit author approval, CRediT roles, funding, and conflict declarations.
- Generate the cover letter only after those fields are resolved.
- Replace the release placeholders after the clean release exists.

The front-matter gate should prevent cover-letter generation in “submission-ready” mode while these fields remain null.

---

## P0-8. Correct Figure 2's data scope and the caption package

The Figure 2 producer loads:

- `identifiability_panel("Arabica", "caffeine")`; and
- `identifiability_panel("Arabica", "trigonelline")`.

The caption says the model is evaluated at nine optimal-grind conditions **for each coffee variety**, giving 18 condition means per solute. Unless the producer has been changed elsewhere, that caption is incorrect: the plotted surfaces are Arabica-only panels.

### Required correction

Choose one of two options:

1. **Keep the existing plot:** label both panels explicitly “Arabica,” and say nine condition means per solute.
2. **Expand the figure:** add Robusta surfaces/profiles or redesign the figure to summarize all six panels without excessive density.

Do not leave a main figure whose caption doubles the apparent sample scope.

Figure S3's caption also calls the inventory assay “independent,” despite the manuscript's deliberate term “orthogonal same-campaign inventory assay.” Use the same evidence terminology everywhere.

Finally, the available contact sheet still shows embedded “Fig 1,” “Fig 2,” etc. titles and producer-oriented long headings, although the current caption contract says embedded figure numbers were removed. Regenerate the final figures from the pinned release commit and visually verify the actual exported files rather than relying only on a test or caption declaration.

---

# Major scientific and methodological comments

## MC1. Reframe the abstract's benchmark claim

The current abstract says:

> “Acceptable endpoint prediction therefore gave no resolvable skill beyond a transferred concentration level.”

This is defensible at the nominal 40 mL proxy under the declared primary clustered range. It is too categorical as a general endpoint statement because the 38 mL range narrowly excludes zero. The effect is still practically tiny, so the paper does not need an absolute negative claim to remain interesting.

Recommended wording:

> At the nominal 40 mL proxy, the gain over the level-only comparator was 0.36 percentage points and the declared clustered sensitivity range included zero. Across 38–42 mL, the effect remained small, although whether the range crossed zero depended on the endpoint proxy.

This is more precise and harder for a reviewer to attack.

The abstract is approximately 245 words by a simple whitespace count, close to the declared 250-word limit despite the YAML comment targeting 230–240. Reduce it to about 220–235 words to avoid submission-system counting differences.

## MC2. The level-only comparator is useful but should not be treated as the only possible null

The optimal-grind-trained constant is an elegant null because the model inventory is an exact multiplicative level. It asks whether the mechanistic response across temperature/pressure/grind adds useful predictive structure beyond a transferred concentration level.

However, it is not a general nonmechanistic benchmark. It ignores even a simple empirical response to temperature and pressure. The paper should either:

- explicitly call it the **level-only null tailored to the inventory factorization**; or
- add a small empirical comparator, such as a regularized linear/quadratic response surface in temperature, pressure, and grind, fitted only on the same training data.

A second comparator would reveal whether the process model beats a modest data-driven trend model, not merely a constant. This is especially relevant because the manuscript's broader language sometimes sounds like a verdict on “mechanistic skill” in general.

## MC3. Keep “sensitivity range,” not confidence-interval language

The fixed-predictor paired clustered percentile ranges condition on the fitted predictors and do not propagate training uncertainty. The whole-group variant has only six clusters. The out-of-bag refit analysis uses nine condition clusters and a larger held-out fraction than leave-one-condition-out. These are useful robustness exercises, but they estimate different things.

The paper is right to separate them in Table 5. Continue to avoid:

- “95% confidence interval”;
- “coverage-calibrated”; and
- a binary hypothesis-test interpretation.

Also state why conditions-within-group was selected as primary **before** looking at which range crossed zero. A reviewer may otherwise suspect that the primary choice was result-dependent.

## MC4. The 10% near-optimal threshold is declared, not inferential

The 10% threshold is a practical profile-width diagnostic. It is not tied to a likelihood-ratio cutoff or a noise model. That is acceptable, but the main text should not let the terminology drift into “confidence region” or “identified/nonidentified” language.

Keep the multi-threshold sensitivity in the supplement and describe the main result as:

> broad, boundary-reaching near-optimal sets under the declared threshold family.

## MC5. Clarify the endpoint proxy as a volume-proxy analysis, not propagation of measured mass uncertainty

The source reports a 40 ± 2 g beverage; the solver uses 38/40/42 mL. The present manuscript is commendably explicit that this is not a validated density conversion. Some later wording nevertheless says “across the ±2 g window,” which subtly treats one gram as one millilitre.

Use consistently:

- “38–42 mL volume-proxy sensitivity inspired by the reported 40 ± 2 g endpoint”; or
- “volume-proxy bracket.”

Do not call it propagation of measured mass uncertainty. A true mass-endpoint analysis would require a declared relationship among liquid volume, dissolved-solids mass, gas/crema, density, and collection practice.

## MC6. The external trajectory is a weak shape stress test, not rate validation

The external comparison has useful honesty but remains limited:

- one averaged trajectory;
- one coffee and grind;
- 12 public bins versus 14 shown in the article;
- assumed 93 °C;
- ambiguous time zero;
- flow flooring before first drip;
- missing standard deviation for the first bin;
- target-specific level refitted at every rate;
- high absolute errors; and
- different preferred rates under MAPE and nRMSE, with nRMSE often at the tested lower boundary.

The main text and figure should foreground both loss functions. Showing only the more visually distinct MAPE trough risks overstating rate localization. The correct conclusion is:

> The independent trajectory contains limited rate-shape information under the tested preprocessing and model, but the preference is shallow, high-error, and loss-dependent.

## MC7. The source fraction analysis and same-model simulation are positive controls

The source-campaign fraction result is in-sample and the exact-cup simulation is generated and fitted by the same model. They are valuable because they show that the observation operator can remove information even when the model is exactly correct.

Keep “positive control,” “information-content demonstration,” and “inverse crime” prominent. Avoid calling the fraction result independent confirmation of the physical rate.

## MC8. Early-time assumptions are load-bearing for the time-resolved conclusion

The model assumes:

- a fully wetted bed at \(t=0\);
- local equilibrium in the initial condition;
- a clean inlet;
- no axial dispersion;
- fixed structure and porosity; and
- imposed flow.

These assumptions can materially sharpen early-time and fraction-to-fraction contrasts. Real espresso includes wetting fronts, dead volume, preinfusion, compressibility, gas, dispersion, and evolving permeability. The temporal-information result is therefore conditional on the assumed start-up and transport representation.

Add a dedicated paragraph in Limitations:

> The model's fraction-level information contrast is conditional on an idealized fully wetted initial state, clean inlet, negligible axial dispersion, and imposed flow. Unmodelled wetting, machine dead volume, dispersion, and evolving puck structure could broaden or shift early-time profiles and therefore change the apparent rate information in fractions.

## MC9. The pressure-to-flow map remains an inferred hydraulic surrogate

The flow-map comparison shows that two tested maps have little effect at the matched endpoint. That does not validate the hydraulic map. Pressure, temperature, flow, compaction, and permeability may be correlated; coarse/fine conditions may alter structure in ways not represented by the inferred map.

The best experimental addition would be per-shot measured flow or mass trajectories. The paper should say that directly and avoid implying that the small difference between two assumed maps establishes hydraulic robustness.

## MC10. Explain macro-MAPE versus point-weighted paired loss more clearly

The paper reports macro-averaged group MAPE for headline model performance and uses paired point-level/group-clustered losses for the model-minus-null range. This is legitimate, but readers can easily assume the same aggregation in both places.

Add a compact notation table or equation showing:

- per-point percentage error;
- per-group MAPE;
- macro-average across six groups;
- the 108-point paired difference; and
- the clustering hierarchy.

MAPE's sensitivity to small observations is especially visible in the external early bins. Consider reporting MAE or nRMSE alongside MAPE for the main transfer benchmark as a robustness check, not only for the external trajectory.

## MC11. “Model worse on 50 of 108 points” is descriptive, not a sign test

This is a useful intuitive statistic. Do not imply formal evidence from the near-even count without accounting for clustered dependence and error magnitude. Keep it descriptive and subordinate to the paired effect and clustered sensitivity range.

## MC12. Distinguish within-campaign holdout from external transfer

The coarse/fine evaluation is held out from the optimal-grind fit, but shares campaign, machine, coffee, basket, analytical methods, and many experimental conventions. “Cross-grind prediction” and “within-campaign holdout” are accurate. “External validation” or broad “transferability” would overstate it.

The Waszkiewicz trajectory is genuinely external but does not test the same named-solute observable or concentration calibration. The evidence ladder should continue to keep these separate.

## MC13. The shared-parameter compatibility result is in-sample

The shared two-parameter mechanistic fit versus per-grind fits is a compatibility diagnostic, not predictive evidence. Its comparison to a three-parameter per-grind constant is descriptive because the models are non-nested, unequally flexible, and fitted/scored on the same observations.

The manuscript now says this, but Figure S2/producer headings remain dense and can be misread. Consider moving the full comparator ladder entirely to SI and summarizing only the qualitative result in the main Discussion.

## MC14. The novelty statement must be evidence-based and modest

The paper's novelty is not a new identifiability method. It is the application and integration of mature inverse-problem tools in a multi-solute espresso model with matched observation operators, a comparator, and time-resolved controls.

After the indexed search, a strong but modest statement would be:

> We found no prior espresso study that combined matched-observable cross-condition evaluation with profiled inventory–rate compensation, an explicit level-only benchmark, and time-resolved information controls in a multi-solute mechanistic model.

Avoid claiming first use of identifiability methods in coffee unless the archived search genuinely supports that broader claim.

---

# Section-by-section review

## Abstract

### Strengths

- Gives the problem, design, profile result, comparator, fraction result, external caveat, and endpoint sensitivity.
- Uses the current title's accessible vocabulary.
- Reports the 50/108 statistic and the primary range rather than only MAPE.
- Distinguishes whole-cup accuracy from parameter localization.

### Required edits

- Replace the categorical “no resolvable skill” sentence with nominal-endpoint wording.
- Reduce the abstract to approximately 220–235 words.
- Avoid “the paired difference” without naming model minus null.
- State that the 38–42 analysis is a **volume-proxy sensitivity**, not mass-uncertainty propagation.
- Consider removing the illustrative-panel interior-minimum detail; the cross-panel 16/18 result is more important and saves words.

## Introduction

### Strengths

- The paper's central distinction is now clear early.
- The three-level vocabulary—numerical minimum, robustness result, scoped interpretation—is excellent.
- The literature section connects espresso modelling with practical identifiability and experimental design.
- The contribution is framed as applied methodology, not a new theorem.

### Required edits

- Complete the indexed novelty search and remove the explicit “will be revised” process sentence from the submitted manuscript.
- Shorten the related-work discussion. Much of the structural/practical identifiability overview can remain in Supplementary Note S1.
- Avoid broad statements that “a good held-out whole-cup error is then read as evidence…” unless supported by examples or softened to “may be read.”
- Keep the three research questions; they provide a strong organizing spine.

## §2.1 Model and constitutive closures

### Strengths

- Governing equations, initial/boundary conditions, grain classes, and the exact inventory factorization are finally explicit.
- The rate multiplier is correctly distinguished from a physical first-order rate constant.
- The parameter table improves reproducibility.

### Required edits

- Resolve the Wilke–Chang molecular-weight issue before submission.
- Replace “analytic Jacobian sparsity pattern.”
- Give the numerical method enough detail to reproduce the biased-upwind stencil and boundary treatment, preferably in SI.
- State whether concentrations are mass per liquid volume, bed volume, or another internal basis consistently throughout.
- Explain how the source fitted solute-specific Sherwood coefficients interact with the common rate multiplier.
- Use standard SI typography and avoid code-style parameter names in the journal prose where a mathematical symbol exists.

## §2.2 Datasets and roles

### Strengths

Table 1 is one of the manuscript's best additions. It prevents the reader from confusing:

- source calibration data;
- same-model simulation;
- target-specific recalibration;
- within-campaign holdout;
- orthogonal same-campaign assay; and
- independent external stress test.

### Required edits

- Make the “duplicate extractions” limitation more visible: the repository retains condition means without per-condition named-solute replicate uncertainty.
- Verify all sample counts against source tables and explain off-grid points in one sentence.
- Avoid “independent, whole-cup” as a standalone heading for Angeloni if the same campaign is then used for fitting and within-campaign holdout. “Independent target campaign relative to the source calibration” is clearer.

## §2.3 Observation operators

This is scientifically central and should remain. The exact distinction among:

- complete cup integral;
- fraction vector; and
- sampled-window aggregate

is essential. Consider adding a small schematic or compact equation box rather than carrying all explanatory prose in the body.

## §2.4 Endpoint and flow assumptions

### Strengths

The discussion of mass versus volume is unusually transparent and should be preserved.

### Required edits

- Remove the obsolete “not evaluated here” statement.
- Stop calling 38/40/42 mL the ±2 g window without qualification.
- Split the long subsection into:
  1. endpoint proxy;
  2. pressure-to-flow map; and
  3. external-trajectory preprocessing.
- Move many external preprocessing details to SI while retaining the load-bearing assumptions in the main text.

## §2.5 Fitting, profiles, and resampling

### Strengths

- The analytic nuisance-level solution is a strong methodological feature.
- The objective families and threshold sets are explicit.
- Resampling estimands are more carefully separated than in earlier drafts.

### Required edits

- State the primary clustering choice and rationale before Results.
- Clarify whether the same rate grid is used for all panels and where interpolation, if any, occurs.
- Distinguish rate-grid convergence from PDE convergence consistently.
- Correct the Jacobian language and narrow convergence scope.
- Consider moving local Hessian details to SI; the profile is the load-bearing result.

## §3 Whole-cup profile analysis

### Strengths

- Exact inventory linearity and approximate cross-condition compensation are now correctly separated.
- Boundary censoring and threshold breadth are reported.
- Objective-family robustness extends the claim beyond one illustrative panel.
- Table 7 has been appropriately demoted in prose.

### Required edits

- Delete the nonexistent Table S2 reference and the implied-rate claim.
- Replace “caffeine matched-mass SSE” with “caffeine 40 mL volume-proxy SSE” or equivalent.
- Replace the undefined `c_s0·φ = const` with a defined expression, for example \(I f(k)\approx\mathrm{const}\), or define \(\phi\).
- Remove duplicated wording: “A numerical identifiability panel (numerical identifiability panel).”
- Do not let the bright Table 7 band visually dominate Figure 2 if the comparison is qualitative only.

## §4 Cross-grind prediction and comparator

### Strengths

This is now the paper's most compelling results section. It gives absolute error, a relevant comparator, pointwise wins/losses, clustered ranges, endpoint propagation, LOCO, out-of-bag refit, and compatibility analyses.

### Required edits

- Renumber Table 4a as a normal sequential table. “4a” is revision residue.
- Frame the 38 mL result as practically small but threshold-sensitive, not as proof of robust superiority.
- Add a simple empirical trend comparator or explicitly narrow the claim to the level-only null.
- Remove duplicated wording: “An in-sample comparator ladder (in-sample comparator ladder).”
- Reduce detail in the main text. The full resampling taxonomy and comparator ladder can partly move to SI.
- Figure 3 should show the absolute model-minus-null difference and primary range, not a rounded “pooled skill 4%” headline.

## §5 Time-resolved information

### Strengths

- Correctly distinguishes sampled aggregate from an actual cup.
- Adds a same-model exact-cup control.
- Declares the inverse crime.
- Includes an independent external trajectory with multiple processing/loss sensitivities.

### Required edits

- Replace “no real minimum” in Table 6 prose with “no well-localized minimum” or “a shallow minimum,” since a numerical minimum exists.
- Repair the malformed sentence “This speaks to the open need for multi-class inventory ↔ kinetics).”
- Clarify that the six-window empirical aggregate and the exact simulated cup answer related but different questions.
- Show both MAPE and nRMSE external profiles in the figure or move the external panel to SI.
- Add the start-up/wetting/dispersion limitation.

## Discussion

### Strengths

The four-way distinction among parameter localization, absolute error, benchmark skill, and cross-context transfer is the paper's most generalizable contribution. Preserve it.

### Required edits

- Reduce repetition: the same distinction is stated in the Introduction, Results, Discussion, Standing Position, and Conclusion.
- Correct lowercase “angeloni.”
- Avoid saying the endpoint artefact “disappears” if it is reduced rather than eliminated.
- Separate what the data show from what would be a future experimental design recommendation.
- Discuss the possibility that source-fitted Sherwood coefficients absorb constitutive scaling, especially after the Wilke–Chang audit.

## Limitations

The limitations are extensive and honest, but they should be reorganized by consequence:

1. **Observation mismatch:** mass endpoint versus volume proxy.
2. **Uncertainty:** no per-condition replicate uncertainty for named solutes.
3. **Hydraulics:** inferred flow and fixed structure.
4. **Transport assumptions:** fully wetted, no axial dispersion, clean inlet.
5. **Evidence scope:** within-campaign holdout, in-sample positive control, one external trajectory.
6. **Inference:** declared objective thresholds and conditional resampling ranges.
7. **Constitutive source:** Wilke–Chang/source-closure audit.

Avoid using the Limitations section as a second Methods section; move operational detail to SI.

## Conclusion

The conclusion should be shorter and centered on one sentence:

> For the tested espresso extraction model, whole-cup prediction accuracy did not reliably determine the split between extractable inventory and mass-transfer rate, and the process model's held-out advantage over a level-only comparator was practically small; time-resolved observations retained substantially more rate-shape information.

Then add one experimental-design sentence and one scope sentence. Do not repeat every evidence tier.

---

# Figure-by-figure review

## Figure 1 — study and evidence design

### What works

- The dependency graph now correctly branches the external trajectory from the source calibration rather than from Angeloni recalibration.
- Table 7 is shown as a lateral same-campaign comparison.
- Evidence categories are explicit.

### Required changes

- The available contact sheet remains too text-heavy for normal journal width.
- Remove repository/audit phrasing and reduce box text.
- Ensure “independent” appears only for the external campaign.
- Regenerate from the final commit and verify that embedded producer figure numbers are absent.

A simplified four-branch diagram with a short legend would be clearer than a prose-rich workflow chart.

## Figure 2 — inventory–rate objective surfaces

### Scientific issue

The producer uses Arabica-only caffeine and trigonelline panels, while the caption claims both varieties and 18 means per solute. Correct this before submission.

### Presentation issues

- The bright cyan Table 7 range attracts attention disproportionate to its evidentiary status.
- The local condition number/coupling annotations compete with the profiles.
- Legends and small text are crowded.
- “SSE optimum,” profile tolerance, assay range, and local diagnostics attempt to carry too many messages in one figure.

### Recommended redesign

Use a two-column figure with:

- top: normalized profile curves for all six panels, or two illustrative surfaces with explicit “Arabica” labels;
- bottom: objective-family/threshold breadth summary across all six panels.

Move the Table 7 basis illustration and Hessian diagnostics to SI. The main figure should state the core finding: broad, boundary-reaching profile sets.

## Figure 3 — cross-grind prediction versus null

The present plot gives observed-versus-predicted panels and a bar chart titled approximately “pooled skill 4%.” Relative skill sounds more impressive than the underlying absolute difference of 0.36 percentage points.

Recommended changes:

- title the comparator panel “Model − level-only MAPE: −0.36 pp at 40 mL”;
- add the primary range [−0.73, +0.03] visibly;
- retain “50/108 points worse” as a secondary annotation;
- simplify the per-fit labels; and
- consider showing endpoint-proxy sensitivity as three points with ranges.

The deterministic near-optimal prediction bars must not resemble confidence/prediction intervals. The current annotation helps, but the figure remains dense.

## Figure 4 — temporal information

The main message is valuable but the figure combines three evidence tiers:

- in-sample source fractions;
- same-model simulation; and
- independent external stress test.

Use visual separation and explicit tier labels. For the external panel, display both MAPE and nRMSE or move the panel to SI; otherwise the figure privileges the stronger-looking loss. A single-cup flat profile is mathematically expected after fitting a free level and does not need much main-figure space.

## Supplementary figures / contact sheet

The caption map proposes four main and four supplementary figures, but the generated supplement does not include them. The supplied contact sheet still shows embedded `Fig N` headings and long producer-style titles. Treat it as an internal diagnostic, not final artwork.

Final artwork should have:

- consistent typography and panel lettering;
- no embedded presentation number in the image;
- captions separate from the graphics;
- legible text at intended column width;
- color-vision-safe differentiation and non-color encodings;
- vector PDF/EPS for line art; and
- identical terminology to the manuscript.

---

# Table and supplementary-material review

## Main tables

The manuscript currently uses Table 1, 2, 3, 4, 4a, 5, and 6. Renumber sequentially. “Table 4a” signals an inserted revision and is unsuitable for final submission unless paired with a deliberate 4b.

Table 1 is valuable but wide; it may need landscape or SI placement. Table 2 should define every symbol used in the governing equations. Table 5's resampling taxonomy is scientifically useful but could move to SI with a shorter main-text summary.

## Supplementary Table S1

Useful comprehensive parameter/objective table. Ensure units and boundary flags are intelligible without producer context.

## Missing Supplementary Table S2

Remove the main-text promise or create a scientifically justified, correctly numbered item. My recommendation is to remove the implied-rate intersection rather than revive it.

## Supplementary Table S3

The endpoint table is useful. Fix the empty header cell and rewrite the all-caps audit prose into neutral scientific language.

## Supplementary Table S5

The external sensitivity matrix is appropriate for SI. Rename it sequentially and remove the producer line from the journal version.

## Supplementary Table S6

Correct “analytic Jacobian,” narrow the conclusion to the representative panel, and explain solver warnings neutrally. Consider adding solver success/status and conservation/positivity diagnostics.

---

# Editorial and terminology corrections

The following should be fixed in the next manuscript pass:

| Current wording/problem | Recommended correction |
|---|---|
| “not evaluated here” for completed endpoint propagation | Replace with a two-estimand description of both completed analyses |
| “matched-mass SSE” | “40 mL volume-proxy SSE” or “matched-volume-proxy SSE” |
| “c_s0·φ = const” with undefined \(\phi\) | Define \(\phi\), or use \(I f(k)\approx\mathrm{const}\) |
| “A numerical identifiability panel (numerical identifiability panel)” | Delete duplicated parenthesis |
| “An in-sample comparator ladder (in-sample comparator ladder)” | Delete duplicated parenthesis |
| “Table 4a” | Renumber sequentially |
| “no real minimum” | “no well-localized minimum” or “a shallow minimum” |
| “This speaks to the open need for multi-class inventory ↔ kinetics).” | Rewrite or delete; sentence is grammatically incomplete |
| lowercase “angeloni” | “Angeloni” |
| “analytic Jacobian sparsity pattern” | “supplied Jacobian sparsity pattern with numerical finite-difference Jacobian” |
| “independent inventory assay” in Figure S3 caption | “orthogonal same-campaign inventory assay” |
| “across the ±2 g window” for 38–42 mL | “across the 38–42 mL volume-proxy bracket” |
| “no resolvable skill” without endpoint qualifier | Scope to the nominal 40 mL proxy and declared primary range |
| “pooled skill 4%” figure title | Report absolute ΔMAPE and range |
| producer paths and review IDs in SI | Move to reproducibility audit, remove from submitted SI |

Also standardize:

- modelling/modeling according to journal style;
- “near-optimal” and percentage-spacing conventions;
- `5-CQA` versus `5CQA`;
- “level-only baseline” versus “concentration-only baseline”;
- “rate multiplier” versus “rate scale”; and
- “volume-proxy endpoint” versus “matched endpoint.”

---

# Suggested revised abstract

> Whole-cup espresso measurements may be predicted accurately while leaving extractable content and mass-transfer rate weakly separated. We evaluated a multi-solute extraction model first calibrated to fraction-resolved data and then recalibrated to optimal-grind whole-cup concentrations. For each candidate rate multiplier, a multiplicative inventory level was profiled analytically. Across six solute–variety panels and three loss functions, 16 of 18 declared 10%-near-optimal sets reached a tested rate boundary, indicating weak localization under the single-grind endpoint design. After optimal-grind calibration, held-out coarse- and fine-grind predictions had 8.23% pooled MAPE, compared with 8.59% for an optimal-grind-trained level-only baseline. At the nominal 40 mL proxy, the difference was −0.36 percentage points and the declared clustered sensitivity range included zero; the model was worse on 50 of 108 observations. A 38–42 mL volume-proxy sensitivity analysis kept the effect small (−0.36 to −0.42 points), although whether the range crossed zero depended on the endpoint. Fraction-resolved source data produced substantially sharper rate profiles than their sampled aggregate, while same-model simulations showed a similar contrast against an exact whole-cup integral. An independent dissolved-solids trajectory gave only a shallow, high-error, loss-dependent rate preference. These results separate four questions that are often conflated: parameter localization, absolute prediction error, improvement over a benchmark, and cross-context transfer. For this model, matched endpoints were necessary for fair prediction assessment but insufficient for identifying the inventory–rate split.

This version is about 221 words by whitespace counting and retains the principal quantitative results without making the nominal-endpoint benchmark conclusion universal.

---

# Suggested Highlights

Each proposed bullet is within the stated 85-character limit:

- Whole-cup espresso data weakly separate content from mass-transfer rate
- The process model performed similarly to a concentration-only baseline
- Time-resolved data carried more rate information in the tested model
- Prediction accuracy did not guarantee well-localized parameters

The current bullet “A process model barely outperformed…” should be replaced. “Barely outperformed” implies an established ordering, whereas the nominal primary range includes zero and endpoint classification changes at 38 mL.

---

# Recommended final manuscript architecture

The current manuscript is approximately 13,650 words including references and remains dense. A clearer journal version would move roughly 20–30% of the technical audit detail into SI.

## Main paper

1. **Introduction**
   - espresso problem and inventory–rate compensation;
   - three research questions;
   - concise related work and scoped novelty.

2. **Methods**
   - governing model and exact inventory factorization;
   - datasets/evidence roles;
   - observation operators;
   - fitting/profile/comparator design;
   - endpoint proxy and primary uncertainty strategy.

3. **Results**
   - whole-cup profile localization;
   - cross-grind model versus level-only comparator;
   - time-resolved information controls.

4. **Discussion**
   - four distinct properties;
   - experimental-design implications;
   - evidence scope and limitations.

5. **Conclusion**
   - three short paragraphs at most.

## Supplement

- extended identifiability review;
- complete objective/threshold tables;
- all fit parameters and boundary flags;
- endpoint-proxy details;
- resampling taxonomy;
- external preprocessing and loss sensitivity;
- numerical convergence;
- full comparator ladder;
- supplementary figures; and
- detailed dimensional audit.

## Separate reproducibility audit

Keep hashes, producer names, internal function paths, ticket history, release gates, and claim manifests in a repository-facing audit document, not in the journal SI.

---

# Prioritized action plan

## P0 — required before submission

1. **Reconcile endpoint status** in Methods, Results, package, abstract, and supplement.
2. **Audit the Wilke–Chang/source-model diffusivity closure**; correct or qualify it and rerun dependent outputs if necessary.
3. **Delete or correctly supply Supplementary Table S2**; make SI reference checking type-aware.
4. **Correct Jacobian wording** and narrow/expand the numerical-convergence claim.
5. **Rebuild the supplement** with sequential numbering, correct tables, actual supplementary figures, and no review/process language.
6. **Correct Figure 2 scope** or regenerate it for both varieties; align all captions with actual data.
7. **Regenerate the reproducibility manifest** at a clean final commit; remove retired Table 7 claims and add new endpoint/convergence claims.
8. **Complete and archive the indexed novelty search.**
9. **Resolve authors, affiliations, ORCIDs, CRediT, funding, conflicts, AI declaration, release DOI, and release commit.**
10. **Prevent the cover letter from asserting approval/conflict status while metadata remains null.**

## P1 — strongly recommended for scientific clarity

11. Add a modest temperature/pressure empirical comparator or narrowly label the current comparator as a factorization-specific level-only null.
12. Reframe the benchmark conclusion around practical effect size and endpoint-dependent range crossing.
13. Show both external loss functions or move the external panel to SI.
14. Add at least one worst-case convergence panel, or explicitly retain the representative-panel limitation.
15. Add the early-time wetting/dead-volume/dispersion limitation.
16. Explain the metric and clustering hierarchy with equations or a compact table.
17. Redesign Figures 2–4 around the three central findings and reduce annotation density.
18. Reduce the main manuscript by about 20–30% and remove repository-facing prose.

## P2 — editorial completion

19. Renumber tables sequentially.
20. Repair duplicated phrases, undefined symbols, malformed sentences, capitalization, and terminology drift.
21. Regenerate and visually inspect all final vector artwork at journal column width.
22. Run a final citation/reference/typesetting audit.
23. Build a clean Word or LaTeX submission source and verify all cross-references after conversion.

---

# Proposed automated acceptance gates

The repository's release-gate concept is excellent. I recommend declaring Paper 1 submission-ready only when all of the following pass.

## Scientific contract

- [ ] Every headline value is present in a machine-readable result record.
- [ ] The manifest covers all headline claims, not only a legacy subset.
- [ ] Endpoint propagation is marked complete everywhere.
- [ ] The Wilke–Chang/source-closure audit is resolved and recorded.
- [ ] No retired Table 7 implied-rate claim remains.
- [ ] Numerical-convergence wording matches the actual solver and tested scope.

## Manuscript/package contract

- [ ] Exact title, abstract, keywords, and Highlights equality across generated files.
- [ ] Abstract below a safe buffer, preferably ≤235 words.
- [ ] Every SI reference resolves by `(type, number)`.
- [ ] Every cited figure/table appears and is cited in order.
- [ ] Table numbering is sequential.
- [ ] No review-ticket, PR, producer, or unresolved-process language in submission files.

## Figure contract

- [ ] Figure 2 caption scope equals the data actually plotted.
- [ ] No embedded presentation number in exported artwork.
- [ ] Main comparator figure shows absolute ΔMAPE and primary range.
- [ ] External figure represents both declared loss readings or is moved to SI.
- [ ] All supplementary figures are included in the SI bundle.

## Release contract

- [ ] Clean repository state.
- [ ] Manifest source commit equals release commit.
- [ ] Bundle commit equals release commit.
- [ ] Non-null generation timestamp.
- [ ] Environment and data/code/figure hashes archived.
- [ ] Release DOI minted and inserted.
- [ ] All author/declaration fields resolved.
- [ ] Indexed novelty search archived.

---

# Final verdict

Paper 1 is much stronger than it was at the first and second review stages. The present title should be retained. The central result—**whole-cup prediction can remain acceptable while inventory and rate are weakly localized, and while a mechanistic cross-grind prediction is nearly matched by a level-only comparator**—is useful, honest, and relevant beyond espresso.

The new endpoint-propagation and convergence work materially improve the paper. They also expose why a final independent consistency pass remains essential: the Methods and package still describe endpoint propagation as absent, the SI checker confuses a Note with a Table, the numerical record contradicts the manuscript's Jacobian wording, and the release manifest still verifies a claim the prose has rejected.

The most consequential scientific question is the Wilke–Chang/source-model closure. It may ultimately prove to be a source-faithful reparameterization with little effect on the qualitative result, but that must be demonstrated rather than assumed. Once that audit, the direct contradictions, the SI package, the figure-scope error, and release provenance are corrected, the paper should be close to a credible *Journal of Food Engineering* submission.

## Recommended editorial decision at this stage

> **Major revision, with encouragement to resubmit after the P0 items are closed.**

---

# Source map for this review

All repository observations above refer to commit:

`352dacd51015d95a3b5a5b3e1a8fb331419d78b0`

Key paths:

- Manuscript: `docs/submission/PAPER_A_JFE_MANUSCRIPT.md`
- Supplement: `docs/submission/PAPER_A_JFE_SUPPLEMENT.md`
- Package: `docs/submission/PAPER_A_JFE_PACKAGE.md`
- Front matter: `docs/submission/paper_a_front_matter.yaml`
- Captions: `docs/figures/PAPER_A_CAPTIONS.md`
- Endpoint propagation: `docs/paper1_resource/PAPER_A_ENDPOINT_PROPAGATION.json`
- Numerical convergence: `docs/paper1_resource/PAPER_A_NUMERICAL_CONVERGENCE.json`
- Objective-family panels: `docs/paper1_resource/PAPER_A_OBJECTIVE_FAMILY_PANELS.json`
- Reproducibility manifest: `docs/reproducibility/paper_a_manifest.json`
- Figure producer: `puckworks/figures_paper_a.py`
- Consistency checker: `tools/paper_a_consistency.py`

External constitutive reference checked:

- Wilke, C. R. & Chang, P. (1955), “Correlation of diffusion coefficients in dilute solutions,” *AIChE Journal* 1, 264–270, DOI `10.1002/aic.690010222`.
