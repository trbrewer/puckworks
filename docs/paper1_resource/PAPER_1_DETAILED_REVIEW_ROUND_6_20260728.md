# Detailed Review of Paper 1 — Round 6

**Repository:** `trbrewer/puckworks`  
**Reviewed branch:** `main`  
**Pinned review commit:** `fc61c4670ec7bf801e40bb391aab16048b8da26b`  
**Commit title:** *Papers 1/2/3: action the round-4 detailed reviews (#190)*  
**Review date:** 28 July 2026  
**Primary manuscript:** `docs/submission/PAPER_A_JFE_MANUSCRIPT.md`  
**Proposed venue:** *Journal of Food Engineering*  
**Recommendation:** **Major revision before submission**

---

## 1. Scope and method

This is a fresh review of the Paper 1 submission package at commit `fc61c467…`, not a reissue of the preceding reviews. I examined the current manuscript, supplementary information, front-matter package, cover letter, figure captions and generators, result records, Pannusch-model implementation, source-data provenance, statistical resampling code, consistency checks, and reproducibility manifest.

The review also included targeted computational audits designed to test particular contracts rather than reproduce the entire slow analysis campaign. Those audits covered:

1. the equation-to-code definition of Reynolds number;
2. the flow-rate and density conversion used by the solver;
3. the numerical state of the clean-inlet boundary;
4. source-campaign reconstruction error under alternative unit conventions; and
5. whether the repository already contains measured complete-cup concentrations that can be compared directly with fraction-resolved observations.

The full slow validation suite and all headline fits were **not** independently rerun. Findings that require a fresh production rerun are identified explicitly. Targeted calculations were conducted only to determine whether a suspected inconsistency is real and whether it is likely to be scientifically material.

### 1.1 Main files reviewed

- `docs/submission/PAPER_A_JFE_MANUSCRIPT.md`
- `docs/submission/PAPER_A_JFE_SUPPLEMENT.md`
- `docs/submission/PAPER_A_JFE_PACKAGE.md`
- `docs/submission/PAPER_A_JFE_COVER_LETTER.md`
- `docs/submission/PAPER_A_SI_PROVENANCE.md`
- `docs/figures/PAPER_A_CAPTIONS.md`
- `docs/paper1_resource/PAPER_A_ENDPOINT_PROPAGATION.json`
- `docs/paper1_resource/PAPER_A_NUMERICAL_CONVERGENCE.json`
- `docs/paper1_resource/PAPER_A_DIFFUSIVITY_CLOSURE_AUDIT.json`
- `docs/paper1_resource/PAPER_1_ROUND_4_ACTION_TRACKER.md`
- `docs/reproducibility/paper_a_manifest.json`
- `puckworks/models/pannusch2024/solver.py`
- `puckworks/models/pannusch2024/closures.py`
- `puckworks/validation/slow/angeloni_bracket.py`
- `puckworks/analysis/identifiability.py`
- `puckworks/figures_paper_a.py`
- the Schmieder/Pannusch experimental-kinetics and cup-mass data and their provenance records
- `tools/paper_a_consistency.py`
- `tools/paper_a_front_matter.py`
- `tools/paper_a_supplement.py`
- the Paper 1 reference-generation tooling and bibliography

---

# 2. Executive assessment

## 2.1 Overall judgment

Paper 1 now has a strong and potentially publishable scientific centre. Its most valuable contribution is not simply that whole-cup measurements contain less temporal information than fractions. It is the more disciplined four-way separation among:

1. **parameter localization** — whether the data distinguish extractable inventory from extraction rate;
2. **absolute prediction error** — whether predictions are numerically close to held-out measurements;
3. **incremental skill** — whether the mechanistic model improves on a simple trained baseline; and
4. **cross-context transfer** — whether a calibrated relationship survives changes in grind, campaign, rig, or observation class.

That distinction is useful beyond espresso. The manuscript also handles several difficult negative or near-null results honestly: the level-only benchmark almost matches the mechanistic transfer; most profiled near-optimal sets reach a tested boundary; and the external dissolved-solids trajectory produces only shallow, loss-dependent rate structure.

The latest revision fixes many of the document-control problems identified previously. In particular, it distinguishes the two endpoint estimands, discloses the source-model Wilke–Chang convention, replaces the internal supplement with a journal-style SI, fixes typed supplementary references, scopes the convergence claim to the one panel actually swept, and aligns Figure 2 with its Arabica-only implementation. These are substantial improvements.

The remaining submission blockers are now more scientific than editorial. The highest-priority issue is that the governing Reynolds-number expression in the manuscript does not match the executable expression. A second unit-contract problem affects the quantity called `flow_mL_s`. A third, newly important finding is that the repository appears to contain measured complete-cup concentrations for the Schmieder source experiments, despite the manuscript saying that an empirical cup comparison is unavailable. Those measurements permit a much more direct and persuasive positive-control analysis than the current sampled-window aggregate and same-model inverse-crime demonstration.

## 2.2 Recommendation

**Major revision before submission.**

The paper should not yet be sent to a journal because the equation/code and flow-unit contracts are load-bearing, and because any correction may require regeneration of the central profiles, benchmark, temporal comparison, figures, and release manifest. The manuscript is nevertheless close enough that the remaining work is finite and well defined. This is not a recommendation to redesign the paper from scratch.

## 2.3 What would change the recommendation to “ready for submission”

The minimum route is:

1. reconcile the Reynolds-number, velocity, and flow-unit definitions with the original source implementation and the manuscript;
2. fix the clean-inlet state and fail-fast solver contracts;
3. rerun all load-bearing analyses after those changes;
4. formally incorporate the measured complete-cup comparison from the source campaign;
5. strengthen the clustered and metric robustness of the near-tied model-versus-null result;
6. generate a clean, commit-pinned reproducibility release; and
7. complete authorship, declarations, novelty-search, and release metadata.

---

# 3. Title review

## 3.1 Current title

> **Separating Extractable Content from Extraction Rate in Espresso Models: Limits of Whole-Cup Measurements and the Value of Time-Resolved Data**

## 3.2 Recommendation

**Retain the current title.**

It resolves the original concern very well:

- it contains **“espresso”**;
- it names the two quantities that the paper is trying to separate;
- it states both the limitation and the constructive experimental lesson;
- it is understandable to an interested non-specialist;
- it does not sound like a social-media slogan; and
- it avoids opaque phrases such as “kinetic parameter localization” in the title itself.

The title is somewhat long, but the length is justified by the two-part scientific contribution. A shorter reserve option, only if the journal requests one, is:

> **What Whole-Cup and Time-Resolved Data Reveal About Extractable Content and Extraction Rate in Espresso**

The current title remains preferable because it is more precise and more conventionally journal-like.

---

# 4. What has improved since the preceding review

The current commit actions a meaningful fraction of the prior major comments. The following should **not** be reopened unless new evidence emerges:

1. **Endpoint propagation is now complete and described with the correct estimand distinction.** The blind endpoint residual and model-minus-null contrast are no longer treated as interchangeable quantities.
2. **The Wilke–Chang source convention is now disclosed.** The manuscript acknowledges that the source implementation supplies solute molecular weight where the standard form uses the solvent molecular weight, and explains why a fitted common rate can absorb much of a pure diffusivity rescaling.
3. **The supplementary-information structure is now journal-facing.** Methods, notes, tables, and figures are typed and sequentially numbered.
4. **The typed-reference checker was fixed.** A reference to “Table S2” can no longer be satisfied by “Note S2.”
5. **The convergence claim is appropriately scoped.** It now refers to the representative Arabica-caffeine panel actually tested, rather than to the paper in general.
6. **Numerical instrumentation was improved.** The archived sweep records solve success, finiteness, monotonicity, and physical interior states over 1,458 solves.
7. **Figure 2’s caption is aligned with the Arabica-only implementation.** The paper no longer implies that both varieties appear in the plotted objective surfaces.
8. **The cover letter no longer asserts declarations that have not yet been supplied.**
9. **The front matter is generated from one source.** The manuscript and package now carry the same title, abstract, and keywords.
10. **The citation/reference pipeline currently resolves the manuscript bibliography cleanly.** The earlier concern about obvious unresolved references is no longer present at this commit.

These improvements move the submission-control system in the right direction. The new review therefore concentrates on unresolved scientific contracts rather than repeating corrected package defects.

---

# 5. Strengths that should be preserved

## 5.1 The central question is important and clearly stated

The paper asks a practical question that modelers often neglect: can a model predict an endpoint while its apparent physical parameters remain weakly separated? That is an important warning for espresso research and for food-process inverse problems more generally.

## 5.2 The exact inventory scaling is separated from approximate rate compensation

The manuscript correctly distinguishes two ideas that are easy to conflate:

- inventory is an **exact multiplicative level** in the linear concentration system; and
- compensation between inventory and rate across multiple conditions is **approximate and design-dependent**.

This is one of the manuscript’s strongest conceptual clarifications and should remain prominent.

## 5.3 The level-only benchmark is excellent

The O-trained level-only comparator is arguably the paper’s most valuable addition. It asks whether the mechanistic model contributes more than a transferred concentration level, rather than merely asking whether its error is tolerable. The 8.23% versus 8.59% result makes the paper more honest and more interesting.

## 5.4 Boundary-censored profiles are reported rather than hidden

The manuscript does not pretend that an interior optimizer automatically establishes a well-localized parameter. Reporting that 16 of 18 10%-near-optimal sets reach a tested boundary is exactly the kind of information many model-validation papers omit.

## 5.5 Objective-family sensitivity is broad

The six solute-by-variety panels and three objective families provide a much stronger basis than a single illustrative SSE surface. The distinction between a profiled objective and a profile likelihood is also handled responsibly.

## 5.6 The endpoint-matching lesson is practical

The paper shows that an unmatched time window can manufacture an apparent transfer failure. This observation is useful independently of the identifiability argument and deserves to remain a clear methodological lesson.

## 5.7 Evidence vocabulary is unusually candid

The labels “target recalibration,” “within-campaign holdout,” “same-model simulation,” and “external objective localization” help prevent overclaiming. The external Waszkiewicz panel is particularly well qualified.

## 5.8 The manuscript distinguishes several meanings of “validation”

The four-property distinction in the Discussion is excellent. It should be retained, simplified slightly, and possibly converted into a compact conceptual figure or boxed summary.

---

# 6. Submission-critical findings

## P0-1. The manuscript and solver use materially different Reynolds-number definitions

### Evidence

The manuscript defines the interstitial liquid velocity as

\[
v_l = \frac{Q}{A\alpha_l},
\]

and then defines

\[
Re = \frac{d_{32}v_l\rho}{\alpha_l\eta}.
\]

The executable solver instead forms a superficial velocity-like quantity `q`, uses `q / ALPHA_L` for advection, and passes `q` to the Sherwood closure. The closure calculates

\[
Re_{\mathrm{code}} = \frac{d_{32}q\rho}{\eta}.
\]

If the manuscript’s `v_l=q/\alpha_l` definition is substituted into its Reynolds number, then

\[
Re_{\mathrm{manuscript}}
 = \frac{d_{32}q\rho}{\alpha_l^2\eta}
 = \frac{Re_{\mathrm{code}}}{\alpha_l^2}.
\]

At the stated porosity \(\alpha_l=0.17\), this is a factor of approximately **34.6**.

A targeted fixed-parameter audit reinforces that this is not a cosmetic difference. Under the current executable expression, the source-campaign reconstruction MAPEs were approximately:

| observable | current implementation MAPE |
|---|---:|
| caffeine | 6.42% |
| trigonelline | 10.18% |
| 5-CQA | 7.22% |
| TDS | 6.72% |

When the closure was forced to use the manuscript Reynolds-number magnitude while leaving the archived source parameters fixed, errors increased to roughly **44–60%**. This is not a production rerun, because the fitted rate parameters were not re-estimated, but it proves that the formula difference materially changes the transfer coefficient.

### Why it matters

Reynolds number enters the Sherwood correlation and therefore the interphase mass-transfer coefficient. The paper’s central object—the common rate multiplier—acts on that same transfer coefficient. A reader cannot reproduce or interpret the rate parameter when the paper and code define the underlying dimensionless group differently.

The latest closure audit explains that a pure diffusivity rescaling can be absorbed by the fitted rate. That argument does **not** automatically resolve the Reynolds mismatch because the two particle classes have separate exponents and because the mismatch changes the Reynolds contribution itself.

### Required action

1. Inspect the original Pannusch/Schmieder MATLAB implementation and article equation together.
2. Determine whether the article contains a notational error, whether the port contains a transcription error, or whether `v_l`, `q`, and \(\alpha_l\) are being named differently from the manuscript.
3. Choose one canonical set of definitions for superficial velocity, interstitial velocity, Reynolds number, and Sherwood number.
4. Make the manuscript, model card, source audit, Python implementation, and unit tests agree exactly.
5. Rerun all Paper 1 analyses whose predictions depend on the solver.

### Acceptance test

A unit test should compute \(q\), \(v_l\), \(Re\), \(Sh\), and \(h\) from a published reference condition independently of the production functions and verify exact agreement with both the documented equation and the executable result.

---

## P0-2. The quantity called `flow_mL_s` is converted as though it were mass flow

### Evidence

The solver input and source-data fields describe flow as mL s⁻¹. The constant-flow path calculates a quantity equivalent to:

```python
q = flow_mL_s / 1000 / RHO / ACS
```

Dividing by density is appropriate when converting a **mass flow** to a volumetric flow. A value already expressed in mL s⁻¹ should instead be converted to m³ s⁻¹ directly before division by area.

With the current \(\rho=980\) kg m⁻³, the implemented velocity and accumulated collection volume are larger than the nominal volumetric interpretation by approximately **2.04%**. For example:

- 0.95 mL s⁻¹ behaves internally like approximately 0.969 mL s⁻¹;
- a nominal 40 mL endpoint corresponds to approximately 40.82 mL under the internal accumulator;
- the 38, 40, and 42 mL sensitivity endpoints correspond to approximately 38.78, 40.82, and 42.86 mL under that convention.

A targeted audit setting density to 1000 kg m⁻³—thereby making the current expression numerically equivalent to direct mL-to-m³ conversion—changed source reconstruction MAPE only modestly:

| observable | current \(\rho=980\) | volume-consistent numerical check |
|---|---:|---:|
| caffeine | 6.42% | 6.46% |
| trigonelline | 10.18% | 10.03% |
| 5-CQA | 7.22% | 7.13% |
| TDS | 6.72% | 6.86% |

The present effect appears modest for this reconstruction, but the contract is still inconsistent.

### Why it matters

The conversion affects advection, Reynolds number, Sherwood number, residence time, and the collection endpoint. It also undermines the manuscript’s careful distinction between a 40 g source endpoint and a 40 mL modeled proxy: the modeled volume is not currently the nominal volume implied by the input label.

### Required action

- Decide whether the source column is volumetric flow in mL s⁻¹ or mass flow in g s⁻¹.
- Rename the variable if it is mass flow.
- Otherwise convert mL s⁻¹ directly to m³ s⁻¹ without dividing by density.
- State the liquid-density assumption used when comparing a 40 g endpoint to a 40 mL proxy.
- Add a collection-volume test showing that 1.00 mL s⁻¹ for 40.00 s accumulates exactly 40.00 mL.
- Rerun all endpoint, transfer, and temporal analyses if the production convention changes.

---

## P0-3. A direct empirical complete-cup comparison appears available and should replace the claim that it is unavailable

### Evidence

Section 5 currently states that the six-window aggregate is not a whole cup and that an empirical whole-cup comparison is unavailable for the Schmieder/Pannusch campaign. The first statement is correct; the second appears incorrect.

The repository contains a `cup_masses.csv` record for the same source experiment identifiers. Its provenance states that it includes per-replicate complete-cup concentrations at brew ratio 1/3 for caffeine, trigonelline, and 5-CQA. The experimental-kinetics table also retains the upper boundary of fraction 10, which provides an experiment-specific complete-shot integration endpoint.

I conducted a targeted review-stage audit using:

- the current solver and current source geometry convention;
- the 15 source experiments;
- nine candidate rate multipliers from 0.25 to 4.0;
- a globally re-estimated multiplicative level at each rate;
- the six retained time windows for fraction scoring; and
- the measured brew-ratio-1/3 cup replicate means for complete-cup scoring, with the fraction-10 upper boundary as the modeled endpoint.

The resulting rate-profile summaries were:

| solute | fraction-scored minimum | fraction range ratio | measured complete-cup minimum | cup range ratio |
|---|---:|---:|---:|---:|
| caffeine | 6.04% at \(k=0.8\) | 4.05× | 5.04% at \(k=1.0\) | 1.29× |
| trigonelline | 9.99% at \(k=0.8\) | 4.41× | 6.25% at \(k=4.0\), boundary | 1.32× |
| 5-CQA | 7.03% at \(k=1.0\) | 4.37× | 6.37% at \(k=3.0\) | 1.39× |

This is precisely the empirical contrast the paper needs: fraction-resolved measurements produce substantially sharper rate profiles than measured complete-cup concentrations from the same experiments.

### Why it matters

The current evidence hierarchy is unnecessarily weak:

1. a sampled-window aggregate that is explicitly not a cup;
2. a same-model exact-cup simulation that is an inverse crime; and
3. an external aggregate-TDS trajectory on a different rig.

The source campaign seems to permit a direct comparison between timed fractions and measured complete cups. That comparison is more intuitive, less vulnerable to the “sampling artefact” objection, and more persuasive to a journal reviewer.

It also corrects an avoidable inconsistency: the manuscript’s dataset table calls the source role “fraction-vs-cup localization,” while the narrative says empirical cups are unavailable.

### Required action

1. Verify the provenance and exact experimental alignment of `cup_masses.csv` against the fraction records.
2. Define the complete-cup endpoint and treatment of source replicates prospectively.
3. Implement the analysis in the repository’s production pipeline.
4. Carry replicate uncertainty or clustered resampling where possible.
5. Rerun it after the Reynolds-number and flow-unit contracts are resolved.
6. Make this measured fraction-versus-cup comparison the primary result of Section 5.
7. Retain the sampled-window aggregate as a diagnostic of incomplete sampling and retain the same-model simulation as a mechanistic information-loss control in the supplement.

### Important caution

The numerical values above are a review-stage audit, not a release result. They inherit the current centre-geometry, Reynolds-number, flow-unit, and concentration-basis conventions and should not be copied into the manuscript until the production implementation is repaired and rerun. The audit establishes feasibility and likely scientific value, not the final numbers.

---

## P0-4. The release manifest is still stale and does not bind all load-bearing artifacts

### Evidence

The current `paper_a_manifest.json` still records:

- an older source commit;
- `git_dirty: true`;
- no generation timestamp;
- a bundle source that does not match the recorded head;
- `bundle_matches_head: false`; and
- `release_fresh: false`.

The numerical claim checker reports no encoded claim failures, but that is not equivalent to a valid submission release. The manifest also does not visibly bind several load-bearing objects, including the production solver and closures, the submitted manuscript, and the submitted supplement.

### Why it matters

The manuscript makes a strong reproducibility promise. A manifest that confirms values inside an outdated or mismatched bundle cannot prove that the paper, code, data, figures, and results all describe the same frozen state.

### Required action

Generate the release only after all scientific corrections are complete. The final manifest should bind, by content hash:

- manuscript, supplement, highlights, cover letter, and front matter;
- solver and closure code;
- all analysis producers;
- source and derived data used by Paper 1;
- numerical result records;
- figure source data and rendered figures;
- environment and lock files;
- test and consistency reports; and
- release DOI/tag/commit.

It should be produced from a clean tree and should fail closed if any required artifact changes.

---

## P0-5. Submission metadata and the novelty record remain incomplete

The manuscript still contains placeholders for:

- author names and order;
- affiliations;
- corresponding author;
- CRediT roles;
- funding;
- competing interests;
- the venue-specific generative-AI declaration;
- release DOI and release commit; and
- the archived novelty-search record.

The front-matter guards correctly block submission. These are administrative rather than scientific defects, but they are absolute submission blockers.

The novelty wording should be finalized only after a documented search covering combinations of espresso extraction, practical identifiability, profile objectives, time-resolved fraction measurements, endpoint aggregation, and mechanistic-versus-null benchmarking.

---

## P0-6. All headline analyses must be regenerated after the solver contract is fixed

The current numerical-convergence record is useful, but it validates the current implementation. It cannot certify results produced under a corrected Reynolds number, flow conversion, or inlet-state representation.

After fixing the model contracts, regenerate at least:

- source-campaign reconstructions;
- six objective-family profile panels;
- endpoint propagation at 38/40/42 mL;
- leave-one-condition-out holdouts;
- O-to-C/F transfer;
- level-only benchmark;
- primary and secondary resampling summaries;
- global-geometry and flow-map sensitivities;
- fraction-versus-measured-cup comparison;
- same-model information control;
- external TDS stress test;
- numerical-convergence sweep; and
- every main and supplementary figure and result table.

This is the key distinction between a documentation repair and a scientific repair. If the canonical equations change, the paper’s numbers must be regarded as provisional until regenerated.

---
# 7. Major scientific and methodological comments

## M1. The clean-inlet boundary is imposed on a copied state, not on the stored BDF state

### Evidence

The governing model specifies a clean Dirichlet inlet, \(c_l(0,t)=0\). In the current right-hand side, the liquid state is copied and the inlet entry in that copy is set to zero before fluxes are evaluated. The derivative of the original inlet state is nevertheless retained in the integrated state vector.

A targeted real-solve check found that the stored inlet state moves from zero to approximately **−0.93** in normalized units by the first reported output and remains negative, even though the interior solution remains positive and the copied inlet value used in the flux calculation is reset to zero.

### Interpretation

The physical flux sees a clean inlet, so this is not evidence that negative inlet concentration directly contaminates the bed. However, the unconstrained state remains inside the BDF error norm and Jacobian system. It can affect time-step selection, conditioning, and diagnostics. The present health checks avoid the defect by excluding the inlet node from positivity checks.

### Required action

Preferably remove the Dirichlet node from the dynamical state. A less elegant alternative is to set its derivative and stored value consistently to zero. Then:

- include the inlet in state-finiteness and boundary checks;
- rerun the representative convergence sweep;
- rerun at least one stiff 5-CQA case and the time-varying-flow solver path; and
- avoid claiming that “all concentrations remained physical” until the full stored state satisfies the contract.

---

## M2. Solver failure is not consistently propagated to the caller

The constant-flow solver records the integrator’s success status but can still return a result after failure. The time-varying path does not consistently expose or check the same status.

For a paper whose conclusions depend on thousands of nonlinear integrations, silent partial returns are unacceptable even if the current archived sweep happened to complete successfully.

The production contract should raise a descriptive exception on:

- unsuccessful integration;
- non-finite state or accumulated mass/volume;
- non-monotone accumulated volume;
- non-positive fraction volume;
- unsorted or invalid time boundaries;
- failure to reach the requested endpoint; or
- physically impossible interior state beyond a declared numerical tolerance.

Both the constant-flow and time-varying-flow paths should return the same structured health metadata.

---

## M3. The `t_bounds` interface can reset the bed at a nonzero time

The solver integrates over `[t_bounds[0], t_bounds[-1]]` and initializes the bed at the first supplied time. It does not require that the first boundary be zero.

A caller that supplies only measured window boundaries beginning after first contact therefore receives a bed freshly initialized at that later time, not a continuation from \(t=0\). In a targeted check beginning at approximately 4.5 s, the initial interior liquid state was close to equilibrium rather than the strongly depleted state reached by a correct solve from zero.

Current Paper 1 producers appear to include zero, so this is a latent contract defect rather than a demonstrated error in the archived headline result. It should still be fixed because the function’s public interface invites misuse.

Required contract:

- either require `t_bounds[0] == 0` within tolerance and fail otherwise;
- or internally prepend zero, integrate the unobserved interval, and return only requested windows;
- require finite, strictly increasing boundaries and at least two values; and
- add tests for both valid and invalid calls.

---

## M4. The concentration basis is not stated consistently

The source fraction data are described as mg per g beverage. The model and parameter table use mg mL⁻¹ and note numerical equivalence to g L⁻¹. The solver applies a scale factor of one while using a liquid density of 980 kg m⁻³ elsewhere.

A constant density conversion can be largely absorbed by the fitted inventory level, so the profile shape may be unaffected. However, the basis matters for:

- physical interpretation of \(c_{s0}\);
- comparisons with roast-and-ground inventory assays;
- any mass balance;
- complete-cup concentration comparison; and
- reproducibility by readers.

The paper should distinguish explicitly among:

1. mass of solute per mass of beverage;
2. mass of solute per volume of beverage;
3. model-state concentration per liquid volume; and
4. solid inventory per chosen solid or bed volume.

Add one conversion table and one mass-balance unit test. Do not describe mg g⁻¹ and mg mL⁻¹ as interchangeable without stating the density approximation.

---

## M5. The model’s source-campaign reconstruction remains weaker than the published source result

The port’s current source-campaign MAPEs are approximately 6.4% caffeine, 10.2% trigonelline, 7.2% 5-CQA, and 6.7% TDS. The source/model card records lower published values of approximately 4.6%, 7.9%, 5.0%, and 6.1%, respectively.

The repository provenance already identifies one likely reason: the experiment-to-grind assignment in the source implementation is opaque, so the port applies the centre-grind geometry to all source experiments. A global sensitivity using the three available geometries is useful but does not reconstruct the experiment-specific mapping.

This does not invalidate Paper 1’s methodological analysis, but it limits language such as “faithfully reproduces” or “source reconstruction” unless the residual discrepancy is explained.

Recommended actions:

- recover `ListOfExperiments` or the equivalent source mapping from the archived MATLAB files;
- document which experiments use which \(d_{s2}\) and \(\psi\);
- repeat the source-reconstruction gate;
- if the mapping cannot be recovered, preserve a transparent uncertainty envelope and say that the port reproduces the model structure but not the published fit to the same error level; and
- ensure the empirical fraction-versus-cup analysis uses the best-supported per-experiment geometry.

---

## M6. The statistical resampling should preserve shared condition structure across solutes

The primary paired clustered bootstrap resamples temperature–pressure conditions independently inside each variety × solute group, while keeping coarse and fine observations from the selected condition together. That respects grind pairing within a group, but it breaks the dependence among solutes measured under the same coffee and operating condition.

The secondary resampling of six whole groups addresses a different and very coarse dependency structure. It does not replace condition-level clustering across solutes.

Recommended additional analysis:

1. within each variety, sample the nine temperature–pressure conditions and carry **all three solutes and both held-out grinds** together;
2. optionally add a conservative global-condition sensitivity that samples common condition labels across varieties where the design permits it;
3. report the model-minus-null difference under this crossed cluster structure; and
4. state whether the conclusion changes.

The code’s field name `ci95_pp` and associated docstrings should also be renamed. The manuscript correctly calls the output a **clustered percentile sensitivity range**, not a calibrated 95% confidence interval.

---

## M7. “Loss robustness” should compare the model-minus-null result, not only the mechanistic error

The central effect is small:

- mechanistic model: 8.23% pooled MAPE;
- level-only comparator: 8.59%;
- paired difference: −0.36 percentage points;
- primary range: −0.73 to +0.03 points.

When the difference is this small, metric choice can matter. The manuscript currently reports an alternative fitting loss that leaves the mechanistic model’s held-out MAPE near 7.0%, but that does not establish that the **incremental advantage over the null** is robust under alternative scoring rules.

Repeat both predictors under at least:

- MAPE;
- MAE on the concentration scale;
- RMSE or a clearly defined normalized RMSE;
- log-relative error; and
- equal weighting of the six variety × solute groups.

Report both pooled and per-group differences. The purpose is not to find a metric that makes the model win; it is to establish whether the “nearly tied” conclusion is itself stable.

---

## M8. The flow-map sensitivity tests magnitude, not functional form

The current ±20% flow-scale sweep is useful, but a common multiplicative scale is especially easy for the fitted rate multiplier to absorb. The manuscript already says that the conclusion remains conditional on the **form** of the inferred pressure–flow map. That caveat is correct and should remain.

A stronger robustness check would vary map shape rather than scale alone—for example:

- the pressure exponent or interpolation rule;
- temperature dependence through viscosity;
- grind ordering and relative spacing; or
- plausible per-condition deviations consistent with reported shot times.

If such a test is not added, narrow the language to “robust to a common ±20% flow-scale perturbation,” not “robust to flow-map uncertainty.”

---

## M9. Fully wetted equilibrium initialization is a load-bearing assumption

The solver initializes the bed as fully wetted and at local equilibrium. Real espresso includes a wetting and filling transient, and the paper’s strongest temporal comparisons rely heavily on early fractions. The assumption is declared, but its consequences deserve more prominence.

At minimum:

- explain that early-time rate information is conditional on starting from the Pannusch model’s wetted equilibrium state;
- avoid implying that the fitted rate is a universal first-contact extraction timescale; and
- consider a limited sensitivity that excludes the first retained fraction or shifts the time origin for the source campaign, analogous to the external-TDS alignment checks.

The external panel already demonstrates how much early-bin weighting can affect an apparent optimum. The same caution should be applied consistently to the in-sample positive control.

---

## M10. The 10%-near-optimal set is a declared tolerance set, not an uncertainty interval

The manuscript generally handles this correctly, but the distinction should be reinforced wherever the profile widths are discussed. A 10% objective increase has no direct probabilistic interpretation without a noise model and likelihood calibration.

Use language such as:

> “The 10%-near-optimal tolerance set was broad and reached the tested boundary.”

Avoid phrases such as “parameter interval,” “confidence region,” or “estimated uncertainty” for these sets.

When the minimum lies at or near a boundary, report the result as censored—e.g. \(k\geq4\) within the tested domain—rather than as a point estimate of 4.

---

## M11. The quantitative Table 7 inventory comparison should remain qualitative

The manuscript has improved its treatment of Angeloni’s roast-and-ground assay, but the temptation to infer a rate by intersecting that assay with the fitted model inventory should be resisted. The fitted \(c_{s0}\) lacks a defensible common volume and solid basis.

The best use of Table 7 is as an experimental-design lesson:

- an orthogonal inventory measurement is potentially powerful;
- it must be expressed on the same physical basis as the model state; and
- the present data do not support that conversion.

Do not restore a numerical implied-rate intersection unless a complete mass/volume mapping and uncertainty propagation are developed.

---

## M12. Numerical convergence is strong for one panel but should be rerun after the model fixes

The current 1,458-solve sweep is a real strength. It establishes local grid and tolerance stability for the representative Arabica-caffeine profile and verifies successful, finite, monotone, and physically acceptable interior solutions under the current code.

The manuscript now scopes the claim appropriately. Two improvements remain desirable:

1. after fixing the inlet state and equation/unit contracts, rerun the sweep; and
2. add a small health-check set for a more numerically demanding 5-CQA panel and the time-varying-flow path.

There is no need to claim universal numerical independence. A representative convergence study plus targeted stress cases is sufficient if the scope is explicit.

---

## M13. The paper needs a dimensional/nondimensional map from equations to code

The manuscript presents dimensional concentrations and governing equations, whereas the solver integrates normalized state variables and accumulators. A reader cannot readily map \(c_l\), \(c_{s1}\), \(c_{s2}\), \(c_{s0}\), bed length, time, and cumulative mass from the paper to the code.

Add a supplementary table with columns:

| manuscript quantity | code variable | stored units/scaling | normalization | boundary/initial value |
|---|---|---|---|---|

This table should include superficial and interstitial velocity, flow, Reynolds number, the Sherwood closure, cup accumulators, and the level parameter. Preparing it will likely expose any remaining unit inconsistencies before peer review does.

---

## M14. The current prose contains one visible sentence-level error

Section 5 ends a paragraph with:

> “This speaks to the open need for multi-class inventory ↔ kinetics).”

This contains a mismatched parenthesis and is difficult to parse. Replace it with something direct, for example:

> “This points to the need for experiments that combine independently measured inventory with time-resolved extraction data.”

A final whole-manuscript copy edit should search for similar remnants of internal drafting language.

---

# 8. Statistical and inferential assessment

## 8.1 The principal conclusion is appropriately cautious, but should remain descriptive

The manuscript’s statement that the mechanistic model provides “no resolvable skill” beyond a level-only baseline is defensible only when tied to the declared resampling scheme and metric. A safer formulation is:

> “Under the prespecified MAPE comparison and primary condition-clustered sensitivity analysis, the mechanistic model’s 0.36-percentage-point advantage over the level-only baseline was small and the percentile range crossed zero.”

That wording reports the result without implying a formal equivalence test or calibrated null-hypothesis inference.

## 8.2 Endpoint dependence should remain explicit

The model-minus-null effect remains small over 38–42 mL, but whether the declared range excludes zero is endpoint-dependent. The manuscript now acknowledges this and should not collapse the result back into a single endpoint-invariant inferential statement.

The strongest robust conclusion is about **effect size**, not threshold crossing: the advantage remains approximately four-tenths of a percentage point.

## 8.3 “Worse on 50 of 108 points” is descriptive

This count is useful because it shows that the pooled advantage is not a uniform pointwise improvement. It should not be treated as an independent binomial test because observations share conditions, coffee varieties, solutes, and calibration history.

## 8.4 Group heterogeneity should be more visible

The pooled mean is nearly tied, but readers also need to see whether the model helps particular solutes or varieties and hurts others. A compact per-group table of:

- mechanistic MAPE;
- null MAPE;
- paired difference;
- number of conditions improved; and
- boundary status of the O-fit rate

would make the result more informative and discourage overinterpretation of the pooled average.

## 8.5 The out-of-bag refit interval estimates a different target

The manuscript now distinguishes the out-of-bag refit interval from the frozen model-minus-null difference. Preserve this distinction. The former includes recalibration variability under a particular resampling design; it should not be presented as uncertainty on the −0.36-point paired contrast.

## 8.6 A practical equivalence margin would improve interpretation

If the authors want to say the model adds too little skill to matter practically, define that threshold before looking at the result. For example, a one-percentage-point MAPE improvement might be chosen as an engineering relevance margin, but the choice must be justified, not reverse-engineered from the observed 0.36.

Without such a margin, say “small” and report the absolute difference rather than “negligible” or “practically equivalent.”

---

# 9. Section-by-section manuscript review

## 9.1 Abstract

### Strengths

- States the exact scientific problem immediately.
- Includes the model-versus-null comparison and the paired difference.
- Reports boundary-reaching profile sets rather than only the illustrative interior minimum.
- Separates matched endpoints from parameter localization.
- Qualifies the external trajectory and endpoint dependence.

### Required revisions

1. **“Predicted accurately” is stronger than necessary.** Use “with modest error” or “reasonably closely,” because 8.2% may or may not be judged accurate across applications.
2. **The temporal-evidence sentence is not yet precise enough.** “Aggregated or simulated whole-cup ones” combines a sampled-window aggregate that is not a cup with a same-model exact cup. After the empirical cup analysis is formalized, say “measured complete-cup concentrations.”
3. **The abstract is numerically dense.** It contains the profile result, benchmark, range, pointwise count, temporal control, external test, single-cup algebra, and endpoint propagation. Retain the benchmark numbers but simplify the final three sentences.
4. **“No resolvable skill” should be tied to the primary analysis.** Avoid a universal conclusion.
5. **The last endpoint sentence is awkwardly detached.** Integrate it into the benchmark sentence or move the detailed endpoint range to the Results.

A replacement abstract is provided in §13.

## 9.2 Introduction

### Strengths

The opening is accessible and the inventory-versus-rate explanation is unusually clear for a technical inverse-problem paper. The decision to define “weakly separated” before introducing “practical non-identifiability” is excellent and aligns with the original accessibility objective.

### Revisions

- Shorten the vocabulary paragraph. It currently defines the numerical, robustness, and interpretive levels at great length before the reader has seen the experiment.
- Move some of the exact qualifications about parameter domain and objectives to Methods or Discussion.
- State the null-benchmark question explicitly among the research questions: “Does the mechanistic transfer outperform a level-only predictor trained at the same grind?”
- Add the direct source-campaign measured-cup comparison to the contribution statement after it is formalized.
- Replace “close the loop with a positive control” with a more neutral sentence; “positive control” is acceptable but slightly promotional in the current context.

## 9.3 Related work

The section is strong and appropriately distinguishes structural identifiability, practical identifiability, profile analysis, sloppiness, and experimental design. It is, however, long relative to the paper’s empirical contribution.

Recommended compression:

- retain one paragraph on structural versus practical identifiability;
- retain one on profiles and parameter compensation;
- retain one on reaction/transport confounding and experimental design;
- shorten the coffee-model lineage to the models directly needed to position Pannusch and the measurement gap; and
- move the extended methodological comparison to Supplementary Methods S1, as the manuscript already proposes.

The final novelty statement must be updated after the documented search is complete. Avoid “first” claims unless the search supports them.

## 9.4 Methods §2.1 — model and parameters

This section cannot be considered submission-ready until P0-1 and P0-2 are resolved.

After reconciliation, the section should:

- define \(Q\) unambiguously as volumetric or mass flow;
- define superficial and interstitial velocity once;
- give a single Reynolds-number expression matching the code;
- state the Wilke–Chang expression as the **source-model convention**, not as the unmodified standard correlation;
- provide a paper-to-code scaling table;
- explain whether concentrations are per mass or per volume of liquid;
- state how the Dirichlet inlet is enforced numerically; and
- separate fixed source parameters from parameters estimated in this study.

The exact inventory scaling argument is excellent and should stay.

## 9.5 Methods §2.2 — datasets

Table 1 is useful and unusually transparent. Revise the Schmieder row once the measured cup analysis is added. It should distinguish:

- six retained fraction windows;
- complete-cup concentrations from `cup_masses.csv`;
- source model calibration status;
- replicate structure; and
- any incomplete mapping between experiment and geometry.

The phrase “fraction-vs-cup localization” currently anticipates an analysis that the prose says is unavailable. The revised row should make the direct empirical comparison explicit.

For Angeloni, make clear which 66 records enter which analyses and how the 108 held-out C/F points are formed. For Waszkiewicz, retain the strong warning that optical TDS is an aggregate proxy, not named-solute evidence.

## 9.6 Methods §2.3 — observation operators

This is one of the manuscript’s strongest sections. The cup, fraction, and sampled-window aggregate operators are clearly distinguished.

Add two details:

1. define the measured source complete-cup operator and endpoint used in the new empirical analysis; and
2. state whether cup observations are replicate-level or replicate means and how the objective weights them.

The statement that the sampled-window aggregate is not a whole cup should remain emphatic.

## 9.7 Methods §2.4 — endpoint and flow assumptions

The latest revision correctly separates:

- the blind fixed-parameter endpoint sensitivity; and
- the fully propagated O-refit-to-C/F benchmark sensitivity.

Preserve that distinction. After fixing the flow contract:

- state the exact density used to relate 40 g to 40 mL;
- report whether endpoint accumulation is based on the prescribed volume flow or a density-derived mass flow;
- narrow the ±20% robustness language to common scale; and
- consider one shape sensitivity or leave the limitation explicit.

## 9.8 Methods §2.5 — profiles, benchmark, and resampling

The analytic re-estimation of the multiplicative level is a strong methodological feature. Keep the derivation concise in the main paper and place implementation details in the SI.

Revise the uncertainty subsection to:

- add the crossed condition-within-variety cluster scheme;
- rename `ci95` quantities consistently as sensitivity ranges;
- distinguish frozen-prediction resampling from refit/OOB resampling;
- add metric robustness for both the model and null; and
- explain why the 10% profile set is a tolerance set rather than a confidence set.

## 9.9 Results §3 — matched endpoint and profile breadth

The matched-endpoint result is clear and valuable. The result that an apparent large residual partly disappears when observation windows are matched should remain early in the paper.

For the profile results:

- lead with the six-panel summary rather than the illustrative caffeine surface;
- report boundary-censored sets using inequality language;
- keep the objective-family sensitivity near the main result; and
- make the status of off-grid points and leave-one-condition-out folds explicit.

The prose is currently more repetitive than necessary. The same distinction between an interior point minimum and a broad boundary-reaching near-optimal set appears several times.

## 9.10 Results §4 — cross-grind transfer and null benchmark

This is the paper’s strongest results section.

Recommended changes:

- lead with absolute errors and paired difference, not relative “skill” percentage;
- add the compact per-group delta table requested above;
- report crossed-cluster and metric sensitivities;
- keep endpoint-specific ranges visible;
- retain “worse on 50 of 108” as a descriptive counterweight; and
- trim the long concluding robustness paragraph, moving detailed geometry and flow variants to SI.

The statement that the result excludes both “the model identifies the rate” and “the model simply fails across grind” is an excellent balanced interpretation.

## 9.11 Results §5 — time-resolved information

This section requires the largest conceptual revision.

### Current problem

The manuscript proves that the six-window aggregate is not a cup, then says empirical cups are unavailable and relies on an inverse-crime exact cup. The repository appears to contain measured source cups after all.

### Recommended architecture

1. **Primary empirical comparison:** fractions versus measured complete cups on the same source experiments.
2. **Sampling diagnostic:** six-window aggregate versus measured cup, showing that the aggregate is not a cup.
3. **Same-model control:** exact integrated cup versus fine temporal curve under synthetic truth, explicitly an inverse crime.
4. **External stress test:** Waszkiewicz TDS trajectory, retained as weak external aggregate-proxy evidence.

This ordering gives the section a clean evidence ladder from measured same-campaign data, through a mechanistic control, to a weak external stress test.

The sentence with “multi-class inventory ↔ kinetics)” must be rewritten.

## 9.12 Discussion

The Discussion’s four-property distinction is excellent. It should become the organizing structure of the section:

1. what the endpoint identifies;
2. what the model predicts;
3. what it adds over a simple baseline; and
4. what transfers across context.

Then add a practical experimental-design subsection explaining how to create rate-sensitive information:

- timed fractions or continuous concentration traces;
- multiple endpoints/residence times;
- measured flow histories;
- independent inventory assays on a compatible basis;
- deliberate variation in temperature and flow; and
- replicate-level uncertainty.

Remove repository-development history and reduce repeated restatement of evidence labels.

## 9.13 Limitations

Add explicit limitations for:

- unresolved Reynolds/velocity source convention until repaired;
- flow-unit and concentration-basis assumptions;
- centre geometry used across source experiments;
- source reconstruction not yet matching published MAPE;
- dependence among solutes measured under common conditions;
- fully wetted equilibrium initialization; and
- the measured complete-cup comparison’s endpoint and replicate assumptions.

After adding the empirical cup analysis, remove the claim that complete source cups are unavailable. Continue to state that the same-model exact-cup simulation demonstrates information loss only under the assumed model.

## 9.14 Conclusions

The conclusion is strong but slightly overpacked. A cleaner version would state:

- whole-cup endpoint calibration weakly separated inventory and rate in this model/design;
- held-out error was modest but nearly matched by a level-only comparator;
- measured fractions carried substantially more rate-shape information than measured cups in the source campaign, if confirmed by the production analysis; and
- the general lesson is to report localization, error, benchmark skill, and transfer separately.

Avoid implying that a single integrated cup is universally uninformative. The algebraic flatness applies when one scalar cup is paired with one free scalar level; multi-cup designs at different conditions can identify rate information.

---
# 10. Figures and tables

I reviewed the current Paper 1 contact sheet and the figure-generation code in addition to the captions.

## 10.1 Figure 1 — evidence and study design

The figure is conceptually useful and provides a clear map through a complicated evidence structure. The current design, however, gives substantial visual weight to the same-model exact-cup simulation because the manuscript assumes that no measured source cup exists.

After the source cup analysis is formalized, revise the figure so that the main temporal branch reads:

**measured timed fractions → measured complete cups → same-model exact-cup control → external TDS stress test**.

This will make the evidence hierarchy immediately understandable. The sampled-window aggregate can appear as a cautionary side branch labeled “incomplete subset of collection windows; not a cup.”

## 10.2 Figure 2 — objective surfaces and profile valleys

The corrected Arabica-only scope now matches the implementation. Scientifically, the figure demonstrates the distinction between a point minimum and a broad valley well.

Presentation issues remain:

- text and boundary annotations are too small at journal column width;
- the heatmap palette has limited print contrast and may be difficult for some color-vision deficiencies;
- the two-dimensional surfaces invite readers to focus on an attractive optimum despite the paper’s stronger six-panel boundary summary; and
- the evidence badges compete with the data.

Consider keeping one simplified illustrative profile in the main paper and moving the dense two-dimensional surfaces to SI. The main figure should emphasize the profile width and censoring rather than the color surface.

## 10.3 Figure 3 — within-campaign holdouts

The observed-versus-predicted panel is useful, but the residual-condition diagnostics and legends are small. A cleaner main figure would show:

- observed versus predicted with identity line;
- residual distribution or per-group error; and
- a concise evidence label in the caption rather than inside each panel.

Temperature- and pressure-residual panels can remain supplementary unless they reveal a specific systematic pattern discussed in the text.

## 10.4 Figure 4 — cross-grind transfer versus null

Panels showing mechanistic and null predictions are informative, but the current “pooled skill 4%” headline should be removed. A relative reduction of approximately 4% sounds more impressive than the actual **0.36-percentage-point** difference and distracts from the range crossing zero.

Recommended title:

> **Mechanistic and level-only cross-grind errors are nearly tied**

Recommended annotation:

> Model 8.23%; null 8.59%; paired difference −0.36 pp; primary range −0.73 to +0.03 pp.

The 12 small group labels in the comparison panel are difficult to read. A dot-and-line plot of per-group paired differences would communicate heterogeneity more effectively.

## 10.5 Figure 5 — shared cross-grind fit

This figure is a useful in-sample compatibility diagnostic but is secondary to the held-out benchmark. The four-panel layout is dense and the text is small. It belongs in the supplement unless the journal permits a generous figure allowance.

The caption must continue to say that a shared in-sample fit is not evidence of held-out transfer.

## 10.6 Figure 6 — temporal information

This is potentially the manuscript’s most intuitive figure. It should be rebuilt around the measured complete-cup analysis.

Suggested layout for each solute:

- fraction-scored objective profile;
- measured complete-cup objective profile;
- sampled-window aggregate as a dashed diagnostic; and
- same-model exact-cup profile as a lighter secondary control.

Use a common normalized objective axis or clearly explain absolute-error differences. Mark boundary-censored minima with arrows rather than plotting them as ordinary point estimates.

The external TDS panel should remain visually separated because it differs in coffee, rig, observable, and evidence tier.

## 10.7 Supplementary Figures S1–S4

These are now properly typed and cited. They are useful diagnostics. Figure S3’s inventory-matched residuals need especially careful labeling so readers do not interpret the orthogonal assay as a validated physical inventory conversion.

Figures S1 and S4 could use larger fonts and simpler legends. Figure S2 should preserve the wording “in-sample parameter-sharing penalty.”

## 10.8 Table 1 — dataset roles

Excellent in concept. Update the Schmieder row to separate fraction windows and measured complete cups, and add the unresolved experiment-to-geometry mapping to its limitation column.

## 10.9 Table 2 — parameters and units

This table is essential but cannot be finalized until the unit contracts are reconciled. Add rows for:

- superficial velocity;
- interstitial velocity;
- Reynolds number;
- liquid density used in the flow conversion;
- concentration measurement basis; and
- code normalization.

The current statement that mg mL⁻¹ is “numerically g L⁻¹” is mathematically true, but it does not resolve the difference from mg g⁻¹ beverage.

## 10.10 Table 3 — matched-endpoint tests

The evidence-strength column is useful. Ensure that each row distinguishes whether parameters are frozen, the level is re-fitted, or both level and rate are re-fitted. The latest commit improved this distinction; preserve it.

## 10.11 Tables 4 and 4a — transfer and endpoint propagation

These are central. Consider merging them into one main table with an endpoint subsection or moving per-species detail to SI. Keep the 38/40/42 mL model and null errors together so readers can see that the effect size is stable even when range crossing is not.

## 10.12 Table 5 — resampling estimands

This is unusually valuable and should remain. Add the new crossed condition-within-variety scheme and ensure machine-readable field names match the table’s vocabulary.

## 10.13 Table 6 — rate information by scoring target

Replace the current two-column comparison between fractions and sampled-window aggregate with a three- or four-target table:

| solute | timed fractions | measured complete cup | sampled-window aggregate | same-model exact cup |
|---|---|---|---|---|

The measured cup should be the principal comparator. The other two are diagnostics with different evidence status.

---

# 11. Submission package, supplement, and repository controls

## 11.1 Front matter and package

The current package is synchronized with the manuscript title, abstract, keywords, and analysis status. This is a resolved strength, not a current defect.

The generated-front-matter approach should be retained. Extend its contract so that a final package build also verifies:

- author and affiliation completeness;
- matching abstract and highlights;
- exact figure/table counts;
- complete declarations;
- release DOI/tag/commit;
- manuscript and supplement hashes in the release manifest; and
- absence of placeholders or internal status language.

## 11.2 Supplementary information

The SI is much improved and now resembles journal supplementary material. It remains long and somewhat repository-facing. Remove or relocate:

- producer names and internal commands not needed for scientific reproduction;
- “delivered,” “owed,” “gate,” and adjudication language;
- development-history explanations; and
- detailed provenance mechanics better suited to `PAPER_A_SI_PROVENANCE.md`.

The submitted SI should contain methods, results, robustness analyses, figures, tables, and enough reproducibility detail to identify the archive—not the project’s internal review history.

Add the paper-to-code dimensional map and the production measured-cup analysis to the SI.

## 11.3 Consistency checker

The checker is materially stronger after the typed-reference and bidirectional SI fixes. The next high-value extensions are semantic and numerical:

- equations and unit definitions hashed or parsed from one canonical specification;
- manuscript/code agreement for `Q`, `q`, \(v_l\), \(Re\), and endpoint accumulation;
- result-table numbers generated from machine-readable records;
- figure captions generated from the same records as annotations;
- evidence-label consistency across manuscript, SI, figures, and manifest;
- no `ci95` field exposed as a confidence interval when the paper calls it a sensitivity range; and
- required citation of every submitted SI object and prohibition of uncited submitted objects.

A phrase checker cannot catch a scientifically wrong equation if every document repeats it consistently. The scientific specification needs executable tests.

## 11.4 Reference system

The current manuscript’s in-text citations and generated bibliography appear aligned. Preserve the current reference tooling and add regression cases for:

- Unicode surnames;
- grouped citations containing multiple years;
- multiline citations;
- organization authors; and
- duplicate year suffixes.

This is a robustness improvement rather than a present bibliography blocker.

## 11.5 Release provenance

The release manifest should be regenerated last, never used to bless an intermediate working tree. It should record:

- clean commit SHA;
- UTC generation time;
- Python and dependency lock hashes;
- deterministic seeds;
- hardware/runtime information where relevant;
- every producer command;
- artifact hashes;
- test summary; and
- an explicit statement that the bundle source equals the reviewed head.

---

# 12. Accessibility, style, and manuscript architecture

## 12.1 Accessibility

The manuscript is substantially more accessible than many identifiability papers. The core terms “extractable content,” “extraction rate,” “whole cup,” and “timed fractions” are understandable to a broad reader. Preserve that language.

The density of specialist terms nevertheless increases after the Introduction. Prefer plain-language terms in the main text and retain the formal term in parentheses:

- “weakly separated (practically non-identifiable under this design)”;
- “broad objective valley” rather than repeated “profile manifold” language;
- “declared near-optimal tolerance” rather than “profile interval”;
- “same-model control” with “inverse crime” defined once; and
- “quantity being estimated” before “estimand” where possible.

## 12.2 Length

The current manuscript is approximately 13,000 words before references by a simple Markdown count, with roughly another 5,500 words in the SI. The Methods alone approach 4,700 words. Even without relying on a specific journal word limit, the main paper is longer than necessary for its core contribution.

A reasonable editorial target would be approximately 9,000–10,500 words for the main article, subject to the current journal instructions. The reduction should come from:

- repeated qualification, not scientific content;
- moving implementation detail to SI;
- shortening related work;
- consolidating robustness prose into tables;
- removing repository status language; and
- stating evidence labels once per analysis rather than repeatedly.

## 12.3 Recommended main-paper architecture

1. **Introduction:** problem, gap, research questions, contribution.
2. **Model and observation operators:** only equations and assumptions needed to understand the study.
3. **Data and analysis design:** source fractions/cups, Angeloni transfer, external TDS, profiles, null, uncertainty.
4. **Results I — endpoint calibration:** matched windows and broad inventory–rate profiles.
5. **Results II — prediction versus benchmark:** cross-grind model and level-only comparator.
6. **Results III — information content:** measured fractions versus measured cups, then controls and external stress test.
7. **Discussion:** four distinct properties and experimental-design implications.
8. **Limitations and conclusions.**

Detailed code mapping, convergence, full panels, alternative objectives, OOB refits, geometry/flow sensitivities, and same-model variants belong in SI.

---

# 13. Suggested abstract revisions

Because the measured complete-cup result is not yet a production repository result, two versions are provided.

## 13.1 Conservative abstract using only currently released analyses

> Whole-cup espresso measurements may be predicted with modest error even when extractable content and extraction rate remain weakly separated. We examined a multi-solute extraction model calibrated to fraction-resolved source data and recalibrated it to whole-cup observations at one grind. A 40 mL model endpoint was used as a proxy for the reported 40 g beverage. At each candidate mass-transfer-rate multiplier, the multiplicative inventory level was re-estimated and the objective was profiled. Across six solute-by-variety panels and three objective families, 16 of 18 declared near-optimal sets reached a tested boundary, indicating broad compensation between content and rate. After optimal-grind calibration, frozen coarse- and fine-grind predictions gave 8.23% pooled MAPE, compared with 8.59% for an optimal-grind level-only baseline. The paired difference was −0.36 percentage points; its primary condition-clustered percentile range (−0.73 to +0.03) crossed zero, and the mechanistic model was worse on 50 of 108 held-out observations. Matched endpoints therefore removed a spurious transfer failure but did not establish incremental mechanistic skill. Fraction-resolved source observations produced sharper rate profiles than an incomplete sampled-window aggregate and a same-model integrated-cup control. An independent dissolved-solids trajectory retained only weak, loss-dependent rate structure. These results are specific to the tested model, endpoints, parameter domain, and campaigns. They support a general reporting principle: parameter localization, absolute prediction error, skill over a simple benchmark, and cross-context transfer should be evaluated separately.

## 13.2 Preferred abstract after production integration of measured source cups

> Whole-cup espresso measurements may be predicted with modest error even when extractable content and extraction rate remain weakly separated. We examined a multi-solute extraction model calibrated to time-resolved source data and recalibrated it to whole-cup observations at one grind. At each candidate mass-transfer-rate multiplier, the multiplicative inventory level was re-estimated and the objective was profiled. Across six solute-by-variety panels and three objective families, 16 of 18 declared near-optimal sets reached a tested boundary, indicating broad compensation between content and rate. After optimal-grind calibration, frozen coarse- and fine-grind predictions gave 8.23% pooled MAPE, compared with 8.59% for an optimal-grind level-only baseline. The paired difference was −0.36 percentage points; its primary condition-clustered percentile range (−0.73 to +0.03) crossed zero, and the mechanistic model was worse on 50 of 108 held-out observations. Matched endpoints therefore removed a spurious transfer failure but did not establish incremental mechanistic skill. In the source campaign, timed fractions localized the rate substantially more sharply than measured complete-cup concentrations after re-estimating the inventory level. A same-model control reproduced the contrast, while an independent dissolved-solids trajectory retained only weak, loss-dependent rate structure. These results are specific to the tested model, endpoints, parameter domain, and campaigns. They show why parameter localization, prediction error, skill over a simple benchmark, and cross-context transfer should be evaluated separately.

The second version is preferable only after the empirical cup analysis is implemented, reviewed, and rerun under the corrected solver contract.

---

# 14. Suggested journal Highlights

Each proposed highlight is within 85 characters, including spaces:

- **Whole-cup espresso data weakly separated extractable content from extraction rate.**
- **The model reached 8.2% MAPE versus 8.6% for a level-only baseline.**
- **Measured cups carried much less rate information than timed fractions.**
- **Endpoint matching fixed comparability, not mechanistic identification.**

The third highlight should be used only after the measured source-cup analysis is productionized. Until then, replace it with:

- **Timed fractions constrained the rate more strongly than integrated observations.**

---

# 15. Prioritized revision plan

## 15.1 P0 — blockers before external submission

| ID | Action | Deliverable | Acceptance condition |
|---|---|---|---|
| P0-1 | Reconcile superficial velocity, interstitial velocity, Reynolds number, and Sherwood closure with the original source | source-model fidelity audit; corrected code/manuscript/card | one independently computed reference condition agrees across equation, code, and test |
| P0-2 | Resolve the `flow_mL_s`/density conversion | canonical unit contract and collection-volume tests | 1 mL s⁻¹ for 40 s accumulates exactly 40 mL under the declared convention |
| P0-3 | Fix the stored clean-inlet state and solver fail-fast behavior | solver patch and health tests | full state satisfies boundary/finiteness/monotonicity contracts; failures raise |
| P0-4 | Productionize measured fraction-versus-complete-cup analysis | result JSON/CSV, table, figure, methods, provenance | experiment IDs and endpoints verified; analysis rerun after model fixes |
| P0-5 | Regenerate every load-bearing Paper 1 result | clean result bundle and figures | all claim checks, scientific gates, and consistency checks pass |
| P0-6 | Add crossed condition-level clustering and model-versus-null metric sensitivity | revised uncertainty record | conclusion reported under all declared schemes without selective emphasis |
| P0-7 | Complete authorship, declarations, novelty search, and release fields | final front matter and search record | submission-ready guard passes with no placeholders |
| P0-8 | Build a clean frozen release | DOI/tag/commit and complete manifest | clean tree, bundle matches head, all required artifact hashes present |

## 15.2 P1 — major quality improvements

| ID | Action | Purpose |
|---|---|---|
| P1-1 | Recover source experiment-to-geometry mapping or bound it transparently | improve source fidelity and temporal positive control |
| P1-2 | Add dimensional/nondimensional paper-to-code map | make the model reproducible and expose unit assumptions |
| P1-3 | Reconcile mg g⁻¹, mg mL⁻¹, and g L⁻¹ bases | protect physical interpretation and mass balance |
| P1-4 | Add a flow-map shape sensitivity or narrow robustness language | prevent scale-only testing from being overgeneralized |
| P1-5 | Add one stiff-solute and time-varying-flow numerical health check | broaden numerical assurance without overclaiming |
| P1-6 | Add per-group model-versus-null deltas | reveal heterogeneity hidden by pooled MAPE |
| P1-7 | Rebuild Figures 1, 4, and 6 around the evidence hierarchy | improve scientific communication |
| P1-8 | Shorten main manuscript and move implementation detail to SI | improve journal readability |

## 15.3 P2 — editorial and presentation improvements

- Copy-edit for residual drafting errors and mismatched punctuation.
- Standardize rounding: two decimals for MAPE where differences are discussed, one decimal for broad descriptive summaries.
- Replace relative “pooled skill” headlines with absolute paired differences.
- Increase figure fonts and reduce internal evidence badges.
- Use boundary arrows and inequality notation for censored optima.
- Define “inverse crime,” “estimand,” and “profile objective” once in accessible language.
- Consolidate repeated caveats into one evidence-ladder table.
- Verify the current *Journal of Food Engineering* author instructions immediately before submission.

---

# 16. Proposed automated acceptance gates

## 16.1 Scientific specification gates

- [ ] A canonical test independently calculates \(Q\), \(q\), \(v_l\), \(Re\), \(Sh\), and \(h\).
- [ ] Manuscript equations and code definitions match that canonical test.
- [ ] Flow-unit test accumulates the prescribed volume exactly.
- [ ] Clean inlet remains zero in the stored state, not merely in a copied flux state.
- [ ] Constant and time-varying solvers fail closed on unsuccessful integration.
- [ ] `t_bounds` are finite, strictly increasing, and begin at zero or are internally extended to zero.
- [ ] Concentration-basis conversions are tested against a hand calculation.
- [ ] Source reconstruction is compared with the published source values and any gap is explained.
- [ ] Empirical source-cup rows map one-to-one to the intended source experiments and endpoint definitions.

## 16.2 Analysis gates

- [ ] All six profile panels and three objective families regenerate.
- [ ] Boundary-censoring status is machine-readable.
- [ ] Endpoint propagation regenerates at 38, 40, and 42 mL.
- [ ] Model and null are compared under all declared metrics.
- [ ] Condition-within-variety clustering carries all solutes and both grinds together.
- [ ] Resampling fields use “range,” not “CI,” unless a calibrated interval is actually justified.
- [ ] Fraction-versus-measured-cup profiles regenerate from committed data.
- [ ] Same-model and external-TDS controls remain clearly separated by evidence tier.
- [ ] Numerical convergence reruns after solver changes and includes targeted stress cases.

## 16.3 Document gates

- [ ] Title, abstract, keywords, highlights, package, and cover letter derive from one source.
- [ ] Every table and figure exists, is sequentially numbered, and is cited in both directions.
- [ ] Every numerical headline is generated from a result record.
- [ ] No internal status terms or unresolved placeholders remain.
- [ ] Evidence labels agree across manuscript, SI, figures, captions, and result records.
- [ ] The manuscript contains no claim that empirical source cups are unavailable if `cup_masses.csv` is used.
- [ ] The paper-to-code variable map is included in SI.

## 16.4 Release gates

- [ ] Git tree is clean.
- [ ] Manifest commit equals bundle head.
- [ ] Bundle is generated after the final code/manuscript change.
- [ ] All load-bearing code, data, results, figures, and documents are hashed.
- [ ] Environment and deterministic seeds are recorded.
- [ ] Full test and consistency summaries are archived.
- [ ] DOI/tag/commit fields resolve to the released artifact.

---

# 17. Targeted review-stage audit details

This appendix records the calculations conducted specifically for this review. They are diagnostic and are **not** substitutes for the repository’s production analysis.

## 17.1 Reynolds-number audit

Using the manuscript definitions and \(\alpha_l=0.17\):

\[
\frac{Re_{\mathrm{manuscript}}}{Re_{\mathrm{code}}}
= \frac{1}{\alpha_l^2}
= 34.6021.
\]

At fixed archived source parameters, changing only the closure to the manuscript-scale Reynolds number increased source reconstruction errors from approximately 6–10% to approximately 45–60%, demonstrating material sensitivity. Because the source rate parameters were not refitted, these values should not be interpreted as corrected production performance.

## 17.2 Flow conversion audit

The current code’s density division creates a factor of:

\[
\frac{1000}{980}=1.020408
\]

relative to a direct volumetric conversion. Re-evaluating source reconstruction under a numerical density of 1000 kg m⁻³ produced only small MAPE changes, but the collection endpoint and physical units remain inconsistent under the current naming.

## 17.3 Clean-inlet state audit

A production-like solve was inspected at reported output times. The stored inlet state became substantially negative while the copied value used for flux evaluation was zeroed. Interior values remained positive in the checked case. This confirms a state-representation defect even though the physical boundary flux is enforced indirectly.

## 17.4 Measured source-cup feasibility audit

The audit joined source experiment identifiers across the retained fraction records and `cup_masses.csv`, used brew-ratio-1/3 replicate means, and integrated the model to each experiment’s fraction-10 upper boundary. A common multiplicative level was re-estimated at each candidate rate separately for the fraction and cup objectives.

The fraction objectives varied by factors of approximately 4.05–4.41 across the tested rate range. The measured complete-cup objectives varied only by factors of approximately 1.29–1.39. Trigonelline and 5-CQA cup minima were high-rate or boundary-adjacent, while their fraction minima remained near the source rate.

This supports the manuscript’s intended information-content argument with actual measured cups, subject to production validation and rerun after the solver contracts are fixed.

---

# 18. Review limitations

- I did not rerun the entire slow Paper 1 campaign.
- The targeted empirical cup analysis is not yet a committed repository result.
- The review-stage calculations inherit the current solver’s unresolved Reynolds-number, flow, geometry, and concentration-basis conventions.
- I did not independently inspect the original proprietary or archived MATLAB implementation beyond the repository’s current provenance descriptions; source fidelity must be resolved from the underlying source files.
- I did not conduct the final venue-specific novelty search or verify the journal’s current administrative requirements; those should be checked at submission time.
- Visual comments are based on the current rendered contact sheet and figure code, not final typeset proofs.

These limitations do not weaken the static findings that the manuscript and solver currently define Reynolds number differently, that the `flow_mL_s` conversion is dimensionally ambiguous, that the stored inlet state drifts, that the manifest is stale, or that measured complete-cup records appear to exist in the repository.

---

# 19. Final verdict

Paper 1 has matured into a serious and potentially valuable study. The title is now excellent. The conceptual argument is clear, the benchmark is unusually honest, and the paper’s distinction among localization, prediction error, incremental skill, and transfer deserves publication.

The submission is not yet ready because the model specification is not fully faithful to the executable solver, and because the current temporal-evidence section overlooks a stronger empirical comparison already present in the repository. These are not cosmetic issues. The Reynolds/velocity and flow-unit contracts must be settled first, followed by a clean regeneration of the analysis.

The most important opportunity is constructive: the measured source cups can turn Section 5 from a partly synthetic information-content demonstration into a direct empirical comparison. If that result survives the corrected solver and a formal production analysis, the paper will be both simpler and stronger.

**Recommendation: major revision before submission, with a clear path to readiness once the P0 actions are closed.**
