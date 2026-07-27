# Third Detailed Review of Paper 1 / Paper A

## Manuscript reviewed

**Current title:** *Separating Extractable Content from Extraction Rate in Espresso Models: Limits of Whole-Cup Measurements and the Value of Time-Resolved Data*

**Repository:** `https://github.com/trbrewer/puckworks`

**Review date:** 26 July 2026

**Repository state reviewed:** current `main` as retrieved for this review, including the Paper 1 reference-list commit `a0db098e0e5e99a1275a11f05676d46036a6c438`.

**Primary files reviewed:**

- `docs/submission/PAPER_A_JFE_MANUSCRIPT.md`
- `docs/PAPER_A_DRAFT.md`
- `docs/submission/PAPER_A_JFE_PACKAGE.md`
- `docs/submission/PAPER_A_JFE_HIGHLIGHTS.txt`
- `docs/figures/PAPER_A_CAPTIONS.md`
- the eight rendered Paper A figures and their contact sheet
- `docs/paper1_resource/PAPER_A_P0-5_RESULTS.md`
- `docs/paper1_resource/PAPER_A_OBJECTIVE_FAMILY_PANELS.json`
- `docs/paper1_resource/PAPER_A_TABLE7_UNITS_AUDIT.md`
- `docs/reproducibility/paper_a_manifest.json`
- `docs/literature_search/references.bib`
- `tools/paper_a_consistency.py`
- `tools/paper_a_references.py`

I also checked the current *Journal of Food Engineering* author instructions relevant to the abstract and Highlights. I did **not** independently rerun the full slow PDE campaign. The numerical review below therefore checks the committed methods, source code contracts, machine-readable results, provenance records, internal consistency, and scientific interpretation; it is not a wholly independent numerical replication.

---

# Recommendation

## **Major revision before submission**

Paper 1 is now materially stronger than the version reviewed in the previous round. Its central scientific story is coherent, useful, and likely publishable:

1. a whole-cup endpoint can be fitted while extractable inventory and the mass-transfer-rate multiplier remain weakly separated;
2. a mechanistic cross-grind prediction can have acceptable absolute error while adding almost no resolvable skill over a level-only baseline; and
3. time-resolved measurements retain shape information that is largely removed by integration to a single endpoint.

The present title is excellent and should be retained. The manuscript now contains governing equations, explicit observation operators, dataset roles, parameter units, profile definitions, objective-family robustness, a properly caveated refit bootstrap, and a much more disciplined evidence vocabulary. These are substantial improvements.

The manuscript is nevertheless not submission-ready. The largest remaining risks are no longer a fundamentally weak central result; they are:

- a **stale and contradictory submission package**;
- a **false-pass bibliography generator** that omits cited works while reporting zero unmatched citations;
- an **unbuilt supplement** despite repeated manuscript claims that results are reported there;
- failure to propagate the acknowledged 38/40/42 mL endpoint uncertainty through the paper's headline model-versus-baseline comparison;
- a **dirty, stale reproducibility manifest** that does not represent a clean release candidate;
- figure numbering and content that still reflect internal producer names rather than the proposed four-main/four-supplement journal architecture; and
- a manuscript that remains too repository-facing, too long, and too densely qualified for an external journal reader.

My assessment is therefore:

> **The scientific core is approaching external-review quality, but the submission object is not yet controlled well enough to send.**

---

# Executive assessment

## What the paper now does well

The strongest feature is that the paper no longer relies on a single attractive fit or a single error number. It separates four questions that are often conflated:

- whether the parameters are localized by the observations;
- whether predictions have modest absolute error;
- whether the process model outperforms a trained non-mechanistic benchmark; and
- whether evidence transfers across grinds, campaigns, rigs, and observable classes.

That separation is the paper's real contribution. The quantitative result—8.23% pooled MAPE for the mechanistic cross-grind prediction versus 8.59% for the optimal-grind level-only baseline, with a primary paired clustered percentile range for the difference of −0.73 to +0.03 percentage points—supports a nuanced but valuable conclusion: acceptable endpoint prediction does not establish resolvable mechanistic skill.

The paper also handles several potentially damaging limitations more honestly than before:

- 40 mL is now described as a proxy for a reported 40 ± 2 g beverage, rather than as an exactly matched endpoint;
- the Table 7 assay is demoted to an orthogonal same-campaign measurement with an undefended volume basis;
- the Waszkiewicz panel is described as an external shape stress test, not a blind concentration prediction;
- the single-cup external profile is recognized as flat by construction after one free level is fitted;
- the out-of-bag refit bootstrap is no longer called coverage-calibrated; and
- the same-model exact-cup experiment is explicitly identified as an inverse crime.

These corrections materially improve trustworthiness.

## What still prevents submission

The manuscript currently tells a more mature scientific story than the files surrounding it. The package still uses the retired title and abstract; the bibliography checker misses at least six cited works; the supplement is promised but not present; and the provenance manifest says the bundle is stale, dirty, and not matched to the reviewed head. Those are not cosmetic inconveniences. They make it possible for an editor, reviewer, or future author to receive a contradictory or incomplete version of the paper.

There is also one remaining analysis-level issue that should be treated as a headline sensitivity rather than a minor caveat. The paper's most consequential comparison is only 0.36 percentage points apart, yet the complete O-fit → C/F transfer → baseline comparison has not been rerun at the declared 38 and 42 mL alternatives. The existing 5 percentage-point endpoint effect refers to a different estimand—the blind optimal-grind discrepancy—so it does not prove that the model-versus-null result changes. It does, however, show that endpoint choice can materially affect related outputs. The only defensible way to close this issue is to propagate the endpoint choice through the entire benchmark pipeline.

---

# Status of the principal findings

| Finding | Current support | Review assessment |
|---|---|---|
| Whole-cup data weakly separate inventory and rate | Profiled SSE and MAPE; all six solute × variety panels; three objective families; grid/domain sensitivity | **Strong within the declared model, data, domain, and objectives.** Keep the scoped language. |
| Cross-grind absolute error is modest | O-calibrated predictions on held-out C/F conditions; 8.23% pooled MAPE | **Supported as a within-campaign holdout**, not external transfer. |
| Mechanistic prediction adds little over a level-only null | 8.23% vs 8.59%; −0.36 pp; primary clustered range crosses zero; 50/108 points worse | **A strong and interesting result**, but still conditional on the 40 mL endpoint proxy until the full endpoint sweep is run. |
| Time-resolved source fractions localize the rate more strongly | Empirical in-sample source campaign plus same-model simulation | **Supported as positive-control/information-content evidence**, not independent physical identification. |
| External time-resolved TDS contains some rate-shape information | One rig, one coffee, one grind; high error; MAPE preference weakens under absolute-residual loss | **Useful stress test only.** Figure and abstract must foreground the weaker, loss-dependent reading. |
| A measured inventory can break the compensation | Table 7 comparison | **Design lesson only.** The unit basis is insufficient for a quantitative rate constraint. |

---

# Progress since the previous review

## Resolved or substantially improved

| Previous concern | Current status |
|---|---|
| Title lacked a clear, accessible espresso-specific description | **Resolved.** The new title is the best title used so far. |
| Methods were not standalone | **Largely resolved.** Governing equations, observation operators, fitting equations, objectives, grids, resampling, and parameter units are now present. |
| Only four objective-family panels had been run while the prose implied six | **Resolved analytically.** All six panels and all three objective families are now archived. |
| “Coverage-calibrated” overstated the out-of-bag interval | **Resolved.** The manuscript now calls it an exploratory percentile interval and distinguishes its estimand from LOCO. |
| Table 7 was treated too quantitatively | **Substantially resolved in prose.** The volume-basis problem and qualitative status are now explicit. The figure still risks re-promoting it visually. |
| External TDS preference was shown under only one loss | **Improved analytically.** An absolute-residual shape loss is now reported and gives a weaker, boundary-censored result. The main figure still does not show that weaker loss. |
| Evidence-flow diagram implied that the external rig inherited the Angeloni recalibration | **Resolved conceptually.** The revised Figure 1 separates the branches correctly. |
| Main/supplement architecture was unclear | **Improved on paper.** Four main and four supplementary figures are mapped in the caption file. The actual supplement and final-numbered figures are not yet built. |
| Bibliography was absent | **Partly resolved but currently unsafe.** A generated list exists, but the detector has false negatives and omits cited works. |
| Manuscript drift was uncontrolled | **Partly resolved.** A consistency script exists, but it is intentionally narrow and passes despite major package drift. |

## Still open or newly exposed

- Full 38/40/42 mL endpoint propagation through the headline transfer/null benchmark.
- Synchronization of manuscript, package, Highlights, cover letter, captions, and release records.
- Correct citation extraction and journal-ready reference rendering.
- A complete supplementary manuscript and supplementary figure/table set.
- A clean, fresh provenance manifest and frozen release.
- Spatial-mesh and solver-tolerance convergence for the PDE outputs, distinct from parameter-grid convergence.
- Final figure redesign, final numbering, and vector export.
- Removal of internal code paths, function names, review history, HTML anchors, and repository-development language from the article.

---

# Title review

## Recommendation: **keep the current title**

> **Separating Extractable Content from Extraction Rate in Espresso Models: Limits of Whole-Cup Measurements and the Value of Time-Resolved Data**

This title now satisfies the requirements raised in the first review:

- it contains **“espresso”**;
- it describes the scientific problem rather than advertising a slogan;
- it names the two quantities being separated;
- it explains both the limitation of whole-cup measurements and the positive role of time-resolved data;
- it remains understandable to a broad food-engineering audience; and
- it avoids the obscurity of “kinetic parameter localization” and the glibness of “the cup can hide the clock.”

The running title—*Whole-cup versus time-resolved espresso measurements*—is also clear.

A slightly shorter alternative would be:

> **Separating Extractable Content from Extraction Rate in Espresso: What Whole-Cup and Time-Resolved Data Reveal**

I do **not** think the shorter version is necessary. The current title is more precise and should be treated as fixed unless the target journal imposes a title-length limit.

---

# P0 submission blockers

## P0-1. Synchronize every submission-facing representation

The JFE manuscript and the JFE package currently describe different papers.

| Item | Current manuscript | Current package | Problem |
|---|---|---|---|
| Title | *Separating Extractable Content from Extraction Rate…* | *Whole-cup measurements can obscure kinetic parameter localization…* | Retired title survives in package and cover-letter text. |
| Abstract | approximately 313 words by whitespace count | labelled 237 words and contains an older abstract | The manuscript exceeds the stated 250-word limit, and the package is stale. |
| Keywords | 6 | 7 | Different indexing terms and counts. |
| Highlights | current standalone file has five repository-oriented bullets | package carries an older set | Neither set is fully aligned with the present title and final evidence hierarchy. |
| Analysis status | all six objective panels and the bounded refit bootstrap are complete | says final weighted-uncertainty reruns remain | Obsolete status. |
| Cover letter | no final synchronized version | quotes retired title and older framing | Submission could be made under the wrong title and claims. |

### Required correction

Do not repair these copies manually one at a time. Establish one machine-readable front-matter source—for example `docs/submission/paper_a_front_matter.yaml`—containing:

- final title and running title;
- final abstract;
- keywords;
- Highlights;
- authors, affiliations, ORCIDs, and corresponding author;
- declarations;
- data/release DOI; and
- the editor-facing significance paragraph.

Generate the manuscript title block, package, Highlights file, and cover-letter core from that source. Add a test requiring exact title and abstract equality across all generated files.

### Acceptance criteria

- One title appears everywhere.
- One abstract appears everywhere and is safely below 250 words; target 230–240 to avoid word-counter differences.
- The keyword list is identical everywhere and contains no more than seven terms.
- The Highlights file contains 3–5 bullets, each ≤85 characters, with no unexplained jargon or abbreviations.
- No package status refers to completed analyses as outstanding.
- The cover letter uses the current title and current claims.

---

## P0-2. Fix the reference generator: it currently reports a false clean pass

The new bibliography is a welcome addition, but its coverage checker is not reliable. `tools/paper_a_references.py` reports 33 resolved references and zero unmatched citations. A direct audit of the manuscript shows at least six additional cited works that are present in `references.bib` but omitted from the generated bibliography.

| Work cited in text | Why the current detector misses it |
|---|---|
| Raue et al. (2009) | The citation is split across a line break between “et” and “al.” |
| Transtrum et al. (2015) | It is the second year in the grouped citation “Transtrum et al., 2011, 2015”; the regex captures only the first year. |
| Tönsing et al. (2014) | The surname contains a non-ASCII character outside the detector's `[A-Za-z]` class. |
| Kuhn et al. (2017) | The citation is split across a line break between “et” and “al.” |
| Sánchez-López et al. (2014) | The surname contains accented characters. |
| Sánchez-López et al. (2016) | It combines the accented-surname problem with a second year in a grouped citation. |

The manuscript therefore cites at least **39 distinct works**, not 33. A zero-unmatched report is currently evidence only that the regex recognized 33 patterns; it is not evidence that every citation was checked.

The rendered bibliography also exposes raw BibTeX rather than a journal-ready style. Examples include:

- TeX accent commands such as `K\"unsch`, `Bia\las`, and `\L`;
- the literal placeholder `others` in author lists;
- double-hyphen page ranges such as `1890--1900`; and
- inconsistent punctuation and title capitalization.

### Required correction

Prefer citation keys in the manuscript source and let a standard bibliography processor—BibTeX/Biber, Pandoc citeproc, or a CSL processor—generate in-text citations and references. A custom regex over rendered author-year prose is intrinsically fragile.

If the custom audit is retained, add tests for:

- Unicode surnames;
- TeX-encoded surnames;
- citations split over line breaks;
- multiple years after one author string;
- semicolon-separated grouped citations;
- two-author names and compound surnames;
- narrative and parenthetical citation forms; and
- citations adjacent to punctuation or Markdown emphasis.

Run a DOI and metadata audit independently of citation coverage. The reference list should contain every cited work and no uncited work unless the journal permits a general bibliography.

### Acceptance criteria

- Every in-text citation resolves to exactly one bibliography entry.
- The six works above appear in the final list.
- A test intentionally deleting any one citation entry fails.
- No TeX escape sequences or literal `others` appear in the submitted reference list.
- The reference style is produced by the journal's selected Word/LaTeX/CSL workflow rather than by bespoke Markdown concatenation.

---

## P0-3. Build the supplement that the manuscript already claims exists

The main text repeatedly says that material is “reported in the supplement,” including:

- the extended identifiability discussion;
- the full objective and threshold family;
- off-grid true-rate simulations;
- dense-grid recovery;
- heteroscedastic and correlated noise experiments;
- model-discrepancy dose-response analyses; and
- supplementary Figures S1–S4.

However, the submission directory currently contains only the manuscript, package, and Highlights for Paper A. The P0-5 results record also explicitly says that the six-panel objective-family figure remains to be drawn.

### Required correction

Create a real supplement, not merely a caption map. A defensible minimum would be:

**Supplementary Methods**

1. full PDE discretization and boundary treatment;
2. spatial-mesh and solver-tolerance convergence;
3. pressure-to-flow maps and all assumed hydraulic parameters;
4. objective definitions and closed-form level solutions;
5. detailed resampling algorithms and estimands;
6. external-trajectory alignment, flow-floor, monotonic-mass correction, first-bin handling, and loss definitions; and
7. complete reproducibility instructions tied to a release DOI.

**Supplementary Tables**

- Table S1: all six solute × variety panels under SSE, relative-L2, and Huber, with 2/5/10/20% sets and boundary flags;
- Table S2: exact per-group O→C/F errors, baseline errors, paired differences, and sample counts;
- Table S3: 38/40/42 mL endpoint-propagation results for the full benchmark;
- Table S4: LOCO and out-of-bag results by group and estimand;
- Table S5: external-trajectory results for every alignment, first-bin choice, temperature, flow-floor, and loss; and
- Table S6: numerical convergence results.

**Supplementary Figures**

- the four already mapped S1–S4 figures;
- a six-panel objective-family profile figure;
- endpoint-sensitivity plots for the full transfer/null comparison;
- the off-grid/noise and model-discrepancy simulation panels promised in §5; and
- an external-panel loss comparison showing both MAPE and the absolute-residual shape loss.

### Acceptance criteria

Every “reported in the supplement” statement in the main paper points to an actual numbered supplementary item. The supplement is included in the reproducibility manifest and release archive.

---

## P0-4. Propagate endpoint uncertainty through the headline transfer-versus-null result

The manuscript correctly acknowledges that the source reports 40 ± 2 g while the solver terminates at a volume. It also reports that the blind optimal-grind named-solute residual moves by about 5 percentage points over 38/40/42 mL. The manuscript then explicitly states that this sweep does **not** evaluate the O-refit → C/F transfer and level-only baseline at each endpoint.

That missing propagation matters because the paper's principal benchmark difference is only:

- mechanistic model: 8.23% pooled MAPE;
- level-only baseline: 8.59%;
- difference: −0.36 percentage points.

The 5-point blind-residual sensitivity and the 0.36-point benchmark difference are different estimands and should not be compared as if the former invalidates the latter. Nevertheless, the known sensitivity is large enough that the headline comparison cannot remain conditioned on a single untested proxy without a full pipeline sweep.

### Required analysis

For each endpoint proxy—38, 40, and 42 mL—repeat the complete procedure:

1. fit inventory level and rate on the nine O conditions;
2. freeze the O calibration;
3. predict all held-out C/F observations;
4. refit the O-trained level-only constant at that endpoint;
5. compute pooled and macro MAPE for both predictors;
6. compute paired model-minus-baseline differences;
7. repeat the primary clustered resampling of the paired loss;
8. report the number of held-out points on which the model is worse;
9. report rate and level shifts; and
10. propagate the near-optimal rate set to pointwise prediction envelopes.

### Decision rule

- If the model-minus-null conclusion remains “small and unresolved” at all three endpoints, the result becomes substantially stronger.
- If the sign or interval changes, report the benchmark as endpoint-dependent and make that dependence part of the conclusion.
- If implementing a mass-based collection operator is feasible, add it as a preferred sensitivity; do not conceal an assumed beverage-density model.

---

## P0-5. Regenerate a clean, fresh reproducibility manifest and release

The current manifest reports:

- `source_commit` older than the reviewed Paper 1 state;
- `git_dirty: true`;
- `bundle_matches_head: false`; and
- `release_fresh: false`.

The 63 recorded claim checks pass, which is useful, but the manifest cannot presently serve as release provenance. It proves that a set of expected values matches a stale bundle, not that the submission files, figures, bibliography, supplement, and result bundle all derive from one clean reviewed commit.

### Required correction

After all P0 revisions:

1. run the complete slow analysis from a clean checkout;
2. regenerate `results.json`, source-data tables, all figures, the supplement, and all claim checks;
3. regenerate the manifest with `git_dirty: false`, `bundle_matches_head: true`, and `release_fresh: true`;
4. include hashes for the canonical manuscript, JFE manuscript, package/front matter, Highlights, captions, supplement, reference database, code, data, and figures;
5. include a UTC timestamp and complete environment lock;
6. tag the release candidate; and
7. archive it with a persistent DOI before replacing the data/code placeholders.

The release should be immutable enough that an external reviewer can reconstruct exactly the submitted figures and headline values.

---

## P0-6. Expand the manuscript-consistency gate beyond phrase checking

`tools/paper_a_consistency.py` is a useful beginning, but its own documentation says it is intentionally narrow. It checks five banned phrases and six required phrases between the canonical draft and the JFE conversion. It currently passes while:

- the package uses a different title and abstract;
- the manuscript abstract exceeds the venue limit;
- the package and manuscript have different keyword lists;
- the cover letter uses the retired title;
- supporting results disagree over an 18- versus 29-point formal grid;
- the bibliography omits cited works;
- the supplement is absent; and
- the manifest is stale and dirty.

### Required correction

Turn the current phrase guard into a multi-file submission contract. It should verify at least:

- exact title equality across canonical draft, JFE manuscript, package, cover letter, and front matter;
- exact abstract equality and word count;
- keyword equality and count;
- 3–5 Highlights, each ≤85 characters;
- required author/declaration fields are resolved;
- no bracketed placeholders remain;
- no “owed,” “deferred,” “PI action,” or review-ticket language remains in submission files;
- every in-text citation resolves;
- every table and figure is cited in numerical order;
- final presentation numbers match embedded figure labels or, preferably, figures contain no embedded “Fig N” title;
- every supplementary reference resolves to an existing file/item;
- all headline numbers match machine-readable results;
- rate-grid counts and domains match across manuscript, result notes, and JSON;
- the manifest is clean and fresh; and
- no HTML anchor comments remain in prose.

The best implementation would generate numeric statements and front matter from structured data rather than attempting to detect every possible drift after manual duplication.

---

## P0-7. Complete the actual submission metadata and novelty record

The manuscript still contains placeholders for:

- authors;
- affiliations;
- corresponding author;
- CRediT roles;
- funding;
- competing interests;
- generative-AI declaration; and
- release/data DOI.

The package also says the licensed/indexed novelty search remains a PI action. The prose currently says “To our knowledge, following the documented search,” which sounds final.

### Required correction

Before external submission:

- complete and archive the final Scopus/Web of Science search protocol, date, query, inclusion/exclusion decisions, and results;
- revise the novelty sentence to match what that search actually supports;
- resolve all author metadata and declarations;
- confirm that all authors approve the manuscript and submission;
- insert the release DOI; and
- ensure the AI declaration matches the journal's current Editorial Manager wording and the actual use of tools.

---

# Major scientific and interpretive comments

## MC1. The abstract is too long and slightly overstates the pattern of numerical minima

The current manuscript abstract is approximately 313 words, above the package's stated 250-word limit. It is also too method-dense for an editor-facing abstract.

The sentence beginning “The profile had an interior numerical minimum…” can be read as saying that all six solute × variety panels had interior minima. That is not true of the archived objective-family table. For example:

- Arabica 5-CQA has its minimum at the upper boundary under all three objectives;
- Robusta 5-CQA reaches the lower boundary under SSE and has the entire domain within the 10% set; and
- several other panel/objective combinations are boundary-censored.

The defensible claim is:

- the illustrative Arabica-caffeine profile has an interior minimum but a broad, upper-censored tolerance set; and
- across all six panels and three objectives, broad and usually boundary-reaching near-optimal sets persist.

The abstract should also call the −0.73 to +0.03 range a **clustered percentile sensitivity range** or **resampling range**, not wording that can be mistaken for a calibrated confidence interval.

A replacement abstract is supplied near the end of this review.

---

## MC2. Distinguish exact level factorization from approximate product compensation

The Methods now establishes an important exact result:

\[
\hat y_i(I,k)=I f_i(k),
\]

because the governing system and observation operators are linear in the initial inventory. That is excellent.

Section 3.2 then reverts to:

> “The whole-cup concentration is, to good approximation, `C_cup ≈ c_s0 · φ(...)`…”

This blurs two different statements:

1. **Exact:** inventory is a multiplicative level for every observation in this model.
2. **Approximate and design-dependent:** the rate response changes mainly as a common level across the tested endpoint conditions, so changing inventory can compensate it with little change in the objective.

The flat valley is not created because inventory is only approximately linear. Inventory is exactly linear. The valley arises because the vector of rate sensitivities is nearly collinear with the level sensitivity over the tested design.

### Suggested replacement

> Because the model factorizes exactly as \(\hat y_i=I f_i(k)\), changing inventory scales every predicted observation equally. Under the tested single-grind endpoint design, \(f_i(k)\) changes with rate in nearly the same proportional direction across conditions. Re-optimizing \(I\) therefore compensates much of the rate-induced change, producing an approximately product-like valley in the multi-observation objective.

Use this exact/approximate distinction consistently in the Discussion and Conclusion.

---

## MC3. Correct the 18-versus-29-point objective-family record

The formal Methods correctly states:

- 18 rate points for the ladder/comparator analyses; and
- 29 rate points for the formal objective-family panel.

The machine-readable objective-family JSON also says 29 points. However, `PAPER_A_P0-5_RESULTS.md` says the objective-family result uses an 18-point grid. The reported fractions—such as 0.759—are consistent with a 29-point grid, not an 18-point grid.

This is a supporting-record error, not evidence that the underlying result is wrong. It should nevertheless be fixed because the paper repeatedly emphasizes machine-verifiable claims.

### Required correction

- Change the P0-5 note to 29 points.
- Add a contract test that `n_rate_grid`, domain, threshold, and panel counts agree across JSON, manuscript, supplement, and result notes.
- Avoid rounding grid fractions in prose in a way that hides the denominator; report “22/29 points (75.9%)” in the supplement.

---

## MC4. Complete the model and numerical specification

The governing-equation section is much improved, but several details still prevent independent reconstruction from the paper alone.

### 4.1 Define `d32`

The Sherwood, Reynolds, and transfer equations use \(d_{32}\), while the state equations and parameter table use \(d_{s1}\) and \(d_{s2}\). The manuscript does not define how \(d_{32}\) is calculated or related to the two grain classes.

Add its definition, units, source, and whether it is global, grind-specific, or solute-independent.

### 4.2 State the unit system of the Wilke–Chang relation

The coefficient \(7.4\times10^{-15}\) is unit-system dependent. Define the units and conventions for:

- molecular weight \(M_i\);
- association factor;
- temperature \(T\);
- viscosity \(\eta\);
- molar volume \(V_i\); and
- resulting diffusivity \(D_i\).

A dimensional or unit test should accompany the implementation.

### 4.3 Reconcile the grain-geometry table

The row for \(d_{s2},\psi\) says “per grind,” but shows only the centre-grind values. Either list the actual values for O/C/F or state explicitly that one global centre-grind geometry is used in the primary analysis and that the alternative global geometries are only a sensitivity.

At present, “per grind” can be read as a calibrated grind-specific geometry map, which the paper later says is unavailable.

### 4.4 Add spatial and tolerance convergence

The manuscript reports convergence of the **rate-parameter grid**, not convergence of the PDE discretization. Because the temporal-information result depends on the shape of the outlet trajectory, numerical convergence of the PDE is load-bearing.

At minimum, report representative convergence at:

- 100, 200, and 400 axial nodes;
- relative/absolute BDF tolerances of \(10^{-5}\), \(10^{-6}\), and \(10^{-7}\); and
- the chosen upwind stencil and boundary treatment.

Compare:

- whole-cup concentration;
- early/middle/late fraction concentrations;
- profile minimum location; and
- profile range ratio or tolerance-set width.

If current tests already cover this, move the results into the supplement and cite them explicitly.

### 4.5 Discuss the fully wetted initial condition in the temporal interpretation

The model starts fully wetted and in local equilibrium, while real espresso includes wetting and preinfusion transients. This is especially relevant to early fraction shape. The paper need not solve unsaturated wetting, but it should state that its positive-control and external shape conclusions are conditional on this initial condition.

### 4.6 Define the external normalized RMSE exactly

The external panel reports “normalised RMSE” values of 57–75%, but the normalization denominator is not given in the main Methods. State the precise formula and level optimization. A result this large can mean very different things if normalized by the mean, RMS, range, or standard deviation of the observations.

---

## MC5. Keep the uncertainty estimands separate in prose, tables, and figures

The revised resampling discussion is scientifically much better, but the presentation still places several different quantities too close together:

1. fixed-predictor paired clustered resampling of **model-minus-null loss**;
2. descriptive resampling of already-computed LOCO errors;
3. condition-cluster out-of-bag resampling that **repeats the fit** and estimates model held-out error at a larger held-out fraction; and
4. the single-condition LOCO point estimate.

These do not estimate the same target. The OOB refit interval is not an uncertainty interval for the −0.36 pp model-minus-null difference. It is an interval for model error under an out-of-bag design that holds out roughly three to four conditions.

### Required correction

Create one compact table with columns:

- analysis;
- resampling unit;
- whether the fit is repeated;
- held-out fraction;
- estimand;
- point estimate;
- percentile range; and
- inferential status.

Use the following terminology consistently:

- **paired clustered resampling sensitivity range** for the fixed-predictor model-minus-null result;
- **descriptive fold-resampling range** for already-computed LOCO errors; and
- **out-of-bag refit percentile interval** for the refitted model-error result.

Do not label the P0-5 table column “95% CI” while the manuscript correctly says no calibrated confidence procedure is specified.

The whole-group paired range barely excludes zero and uses only six groups. It can remain as a sensitivity, but the primary conditions-within-group result should remain dominant.

---

## MC6. The external panel must visually show the weaker loss-dependent result

The manuscript now makes the correct conservative interpretation: MAPE produces a shallow preference near 0.4, but an absolute-residual shape loss is flatter, has high residual error, and places the preferred rate at the lower boundary. The current main Figure 4 external panel appears to show only the MAPE profile.

That is a mismatch between the visual and the conclusion. A reader scanning the figure could see a clear-looking minimum and miss that the rate preference weakens under a less early-bin-dominated loss.

### Required correction

Redesign the external panel to show both losses. Good options include:

- two adjacent normalized-profile panels;
- overlaid objectives after normalization to each minimum, with the actual minimum errors stated separately; or
- a main absolute-residual panel with MAPE shown as a secondary sensitivity.

The figure should explicitly mark:

- the MAPE minimum and its approximately 27% error;
- the absolute-residual minimum at the tested lower boundary;
- the range-ratio ranges under each loss;
- the alignment/first-bin envelope; and
- the algebraically flat single-cup reference as a construction, not an empirical curve.

The caption should use “external shape stress test,” not “external validation.”

---

## MC7. Lead the Table 7 discussion with non-commensurability, not the apparent intersection

The dimensional audit is one of the best improvements in the paper. It shows that plausible conversions of the Table 7 dry-coffee assay span roughly 4.8–16.3 mg mL⁻¹, and that the model's fitted inventory basis is itself not independently anchored.

However, §3.2 still first says that the profiled inventory passes through the measured value and narrows the rate near 1, then spends a long paragraph withdrawing quantitative force from that observation. The figure also retains a visually precise assay line/point.

### Required correction

Reverse the order:

1. state first that the assay and model inventory are not demonstrably commensurate;
2. state that no quantitative rate intersection is claimed;
3. present the broad conversion range; and only then
4. note, as an illustrative design lesson, that an independently anchored inventory measurement of the correct model quantity could rotate or intersect the profile valley.

Consider moving the numerical implied-rate intersection entirely to the supplement. In the main figure, show only the defensible basis range, with no central “measured” line that implies a preferred conversion.

Use **“orthogonal same-campaign inventory assay”** consistently. Avoid “independently measured” where it can be mistaken for an independent campaign.

---

## MC8. The paper still contains too much repository and review scaffolding

The manuscript is approximately 11,500 whitespace-separated words including references. More importantly, a large fraction reads as an internal audit trail rather than a journal article.

Examples include:

- Python function names in parentheses after results;
- repository IDs such as `pannusch2024`, `angeloni2023`, and `waszkiewicz2025`;
- file paths in the Results;
- references to gap “G6”;
- “the repo's internal labels”;
- bracketed editorial notes;
- review-history prose such as “This scoping supersedes…”;
- HTML anchors embedded in section references; and
- a data-availability section that inventories functions rather than giving a stable release citation.

### Required correction

Move the audit trail to the supplement and repository documentation. In the article:

- use author–year dataset names, not registry IDs;
- state methods, not function names;
- cite a versioned release and DOI rather than individual source paths;
- remove every statement about earlier manuscript interpretations;
- remove all review-ticket and roadmap vocabulary;
- replace HTML comments with normal cross-references; and
- use conventional numbered tables and figures.

A 20–30% reduction in the main-text word count is realistic without removing evidence. The paper's logic will become stronger when qualifications are organized once in Methods and Limitations rather than repeated after every number.

---

## MC9. Moderate categorical claims in the Introduction

Several introductory sentences remain broader than the evidence supports.

### “Almost always”

> “In practice this cross-dataset check is almost always performed on whole-cup quantities…”

Unless backed by a systematic review, use “commonly” or “often.”

### “The distinction is decided by…”

> “…the distinction is decided by whether the observable preserves the extraction's temporal shape.”

Time resolution is one route to rotating sensitivity directions, but the paper itself acknowledges that multiple endpoints, flows, temperatures, and pressures can also help. Replace with:

> “…the distinction depends strongly on whether the experimental design preserves or creates contrasts in extraction shape, for example through time-resolved fractions or deliberately varied operating conditions.”

### “Independent coffee dataset”

Be precise about which dataset supports which claim. Angeloni is an independent target campaign for whole-cup recalibration, but the cross-grind prediction is within that same campaign. Waszkiewicz is the independent second-rig time-resolved aggregate-solids panel.

---

## MC10. Use “mass-transfer-rate multiplier” consistently

The parameter \(k\) multiplies both Sherwood prefactors. Calling it simply “the kinetic rate” is accessible, but it can be interpreted as a directly measured first-order rate constant or a unique physical extraction timescale.

Recommended vocabulary:

- first definition: **common mass-transfer-rate multiplier on the two Sherwood prefactors**;
- later shorthand: **rate multiplier**;
- interpretive phrase: **extraction-rate response represented by this multiplier**.

Reserve “physical kinetic rate” for claims the paper does not make. The title's broader phrase “extraction rate” is acceptable for accessibility because the Methods defines the operational parameter.

---

## MC11. Clarify what the primary benchmark does and does not establish

The level-only constant is a defensible null because inventory is an exact multiplicative level. The paper should preserve this comparison. It should also make the benchmark contract maximally explicit:

- the constant is trained only on O conditions;
- it is frozen for C/F;
- it carries no T, p, flow, or kinetic response;
- it is optimized under the same primary loss used for comparison; and
- all model and baseline predictions use the same endpoint proxy.

An optional additional baseline could be a simple empirical response surface trained on O conditions, but this is not necessary for the principal paper. The key is not to imply that beating one constant would prove mechanism; the current result is valuable precisely because the process model barely beats even this minimal comparator.

---

# Section-by-section review

## Front matter

### Strengths

- The current title is strong.
- The running title is concise.
- Six keywords are within the package's stated limit.

### Required changes

- Resolve author, affiliation, corresponding-author, and declaration placeholders.
- Replace the abstract.
- Synchronize the package and cover letter.
- Consider replacing `profile objective` in the keywords with `time-resolved extraction` or `model validation`, terms that may be more discoverable to the intended readership.

A possible final keyword set is:

> espresso; extraction modelling; mass transfer; practical identifiability; time-resolved measurement; experimental design

---

## Abstract

### Strengths

The current abstract contains the three essential results, the baseline, the external limit, and the reporting principle.

### Problems

- Over the journal's stated word limit.
- Too many subordinate clauses and qualifications.
- The “interior minimum” sentence can be misread as universal.
- “Primary clustered 95% resampling interval” sounds more inferential than intended.
- The endpoint-proxy conditionality is stated early but not tied to the cross-grind benchmark.

### Action

Use the replacement abstract supplied below and regenerate every submission-facing copy from it.

---

## 1. Introduction

### What works

- The practical problem is clear.
- The distinction between structural and practical identifiability is now responsible.
- The literature connection to sloppiness, profile methods, reaction–transport confounding, and experimental design gives the espresso case wider relevance.
- The three research questions provide a clean backbone.

### What to change

1. Replace “almost always” with “commonly.”
2. Remove the italic editorial note saying the section is deliberately compact.
3. Remove HTML anchors in section references.
4. Replace categorical “decided by temporal shape” wording with a design-based statement.
5. Shorten the related-work catalogue. The paper needs context, but a long sequence of coffee-model citations can be moved to a concise table or supplement.
6. Do not state “following the documented search” as final until the indexed novelty search is complete.
7. Define the paper's novelty in one sentence:

   > The novelty is not a new identifiability method; it is the first worked espresso case, to our knowledge under the archived search, that combines matched observation operators, profile analysis, a trained null benchmark, within-campaign holdouts, and an independent time-resolved stress test to separate endpoint accuracy from parameter evidence.

8. Avoid introducing too many labels—inventory, kinetic rate, weak separation, weak localization, practical non-identifiability, valley, and sloppiness—in the opening pages. Choose “inventory,” “rate multiplier,” and “weak localization” as the default terms.

---

## 2.1 Espresso extraction model and estimated quantities

### What works

- The equations make the Methods substantially more self-contained.
- The exact multiplicative-level proof is important and should remain.
- The operational definition of the rate multiplier is much clearer.

### What to change

- Define every symbol on first use, especially \(d_{32}\), \(\alpha_{s1}\), \(\alpha_{s2}\), \(A_{cs}\), \(M_i\), and \(V_i\).
- State the units behind the Wilke–Chang coefficient.
- State whether the Sherwood prefactors are dimensionless under the implemented convention.
- State the outlet treatment and numerical implementation of the biased-upwind derivative.
- Explain the effect of the fully wetted initial condition on early fractions.
- Consider presenting the governing equations in a compact model table, with detailed closure coefficients in the supplement.

---

## 2.2 Datasets and analytical roles

### What works

The dataset-role table is one of the manuscript's strongest integrity devices. It prevents in-sample verification, within-campaign holdout, and independent external evidence from being silently upgraded.

### What to change

- The table is too wide for a journal page. Simplify the main version to dataset, observable, fitted quantity, held-out quantity, and evidence tier; move rig details and limitations to Table S1.
- Replace repository IDs with author–year labels.
- Explain “derived six-window subset” without relying on the port name.
- Keep the statement that optimal/coarse/fine are source labels.
- Make the absence of per-condition replicate uncertainty visually obvious in the Angeloni row.
- Do not call the Table 7 assay “independent”; use “orthogonal same-campaign.”

---

## 2.3 Observation operators

### What works

This section now states the paper's conceptual core mathematically. The distinction among a whole cup, a fraction, and a sampled-window aggregate is clear and important.

### What to change

- Add a schematic or small inset illustrating the three operators on one model trajectory. This may communicate the paper faster than several paragraphs.
- State how numerical integration is performed and checked.
- Clarify whether \(Q(t)\) is constant in the source simulations and time-varying only for the external trace.
- Define what happens when the interval boundaries do not coincide with solver time steps.

---

## 2.4 Endpoint and pressure-to-flow assumptions

### What works

The endpoint caveat is now unusually transparent. The external preprocessing choices are also declared rather than hidden in code.

### What to change

- Move most external preprocessing detail to Supplementary Methods and retain a concise main-text summary.
- Remove code-font variable names and function names.
- Remove the shorthand “ρ≈1” from §3.1; it undercuts the careful statement that no validated density conversion is available.
- Provide a small table of assumed flows/shot times by grind, pressure, and temperature.
- Complete the full endpoint propagation requested in P0-4.
- Use consistent capitalization of Angeloni.

---

## 2.5 Profile, prediction, baseline, and uncertainty methods

### What works

- Exact least-squares and weighted-median profiling is a major improvement.
- The sensitivity-column explanation is concise and insightful.
- The reporting hierarchy is responsible.
- The OOB bootstrap estimand is now explained accurately.

### What to change

- State the normalized RMSE formula.
- State precisely how the Huber scale is recomputed or held across candidate rates.
- Number the equations and cite them.
- Add the spatial/tolerance convergence analysis.
- Change “95% interval” language for the fixed-predictor comparison to “95% clustered percentile sensitivity range.”
- Add a table separating all resampling estimands.
- Explain why macro-MAPE rather than pooled point-weighted MAPE is primary, then report both if useful.
- Correct the 18/29 supporting-record inconsistency.

---

## 2.6 Evidence vocabulary

The discipline is valuable, but this section is too repository-aware. Replace the opening sentence with a normal article statement and move internal label mappings to the supplement.

Suggested concise version:

> We distinguish calibration, within-campaign holdout, cross-campaign prediction, in-sample objective localization, and same-model simulation. These labels describe how each result was generated and are not upgraded by subsequent interpretation.

---

## 3.1 Matched endpoint and blind residual

### What works

- Named solutes and aggregate-solids proxies are separated.
- The flow-map effect and endpoint effect are not conflated.
- The refit is explicitly called a new target calibration.

### What to change

- Remove the bracketed editorial note about the weak two-point holdout.
- Remove “ρ≈1.”
- Replace “etc.” after rate examples with either exact values in a table or no examples.
- Avoid saying the per-species rate “flips with endpoint and domain” unless the corresponding result is shown for each species.
- Add exact uncertainty/replicate limitations adjacent to the 26.3% and 8.4% values.
- Number the table and cite it from the text.

---

## 3.2 Inventory–rate profile

### What works

- The profile is the correct primary diagnostic.
- Boundary censoring and lower-bound width are explained well.
- SSE/MAPE set overlap is quantified rather than asserted.
- All six panels and objective families are now available.

### What to change

- Correct the exact-versus-approximate factorization language.
- Lead the Table 7 discussion with non-commensurability.
- Replace “practically non-identifiable” in the first summary sentence with “weakly localized over the tested domain”; retain the formal term only after the scope is explicit.
- Move file paths and producer names to the supplement.
- Move the Hessian condition number/coupling to a secondary paragraph or supplement; the profile should dominate visually and verbally.
- Make clear that some objective-family point minima are on boundaries. Do not allow the representative interior caffeine minimum to become a universal statement.
- Correct the P0-5 grid count.

---

## 4. Cross-grind prediction and null benchmark

### What works

This is now the manuscript's most compelling section. The model's absolute error is respectable, but its advantage over a level-only baseline is small and unresolved. That result is more scientifically informative than a simple “model transfers” or “model fails” claim.

### What to change

1. Run the full endpoint sensitivity.
2. Separate the fixed-predictor difference range from the OOB model-error interval.
3. Replace “clustered bootstrap 95% interval” with non-calibrated sensitivity terminology.
4. Add a primary table with exact group-level model, baseline, difference, and sample counts.
5. Put the 8.23/8.59/−0.36 result in the first paragraph and first figure annotation; do not bury it after per-species ranges.
6. Explain once that C/F are within-campaign held-out grinds, then avoid repeating the entire caveat.
7. Keep the comparator ladder explicitly descriptive and in-sample.
8. Correct the missing period in the sentence ending “rather than as a single mean Because…”.
9. Consider moving the joint fit and reduced-model ladder to the supplement. They are useful corroboration but make the main section long.
10. Retain the prediction-stability-across-the-near-optimal-set result; it elegantly distinguishes parameter uncertainty from predictive stability.

---

## 5. Time-resolved measurements

### What works

- The sampled-window aggregate is no longer mislabelled as a whole cup.
- The same-model exact cup addresses the sampling-artifact objection.
- The inverse-crime limitation is explicit.
- The external panel is read conservatively.

### What to change

- Build the promised supplement for all robustness variants.
- Make the fully wetted initial condition part of the temporal limitation.
- Remove “gap G6.”
- Avoid repository IDs in prose.
- Show both losses in the main external panel.
- Define normalized RMSE exactly.
- Call the Waszkiewicz result an “external shape stress test” throughout.
- Do not say the external fractions “always constrain the rate” without immediately adding “weakly and loss-dependently over the tested domain.” Under the absolute-residual loss, the optimum is boundary-censored and the range ratio is only 1.19–1.30.
- Distinguish the publication year 2026 from the repository's `waszkiewicz2025` data ID outside the article.

---

## 6. Discussion

### What works

The four-property distinction is excellent and should remain central:

- parameter localization;
- endpoint accuracy;
- skill over a benchmark; and
- cross-context transferability.

### What to change

- Remove the entire revision-history sentence saying the current scoping supersedes earlier readings. Reviewers do not need the project's internal interpretive history.
- Reduce repetition of numbers already presented in Results.
- Add a concise design implication: time points or operating conditions should be selected to maximize variation in the rate-sensitivity direction relative to the inventory-level direction.
- Avoid “essentially the product” without reminding the reader that exact factorization is in level and approximate compensation is across conditions.
- Distinguish what is specific to this model from the general reporting principle.

---

## 7. Limitations

This section is strong and candid. It should be retained, shortened, and reorganized into four compact paragraphs:

1. measurement uncertainty and small cluster counts;
2. endpoint and hydraulic assumptions;
3. model structure and initial conditions; and
4. generalizability and missing external named-solute fractions.

Add the untested full endpoint propagation until it is completed. Add spatial-discretization uncertainty until convergence is documented. State explicitly that the source model's fully wetted assumption may be most consequential for early fraction shapes.

---

## 8. Conclusions

The conclusion is well scoped. After the endpoint sweep, it should state whether the model-versus-null finding is robust across the endpoint proxy range.

Consider shortening it to four sentences:

1. the whole-cup design permits broad compensation;
2. modest held-out error did not imply resolvable skill over the null;
3. time-resolved observations provided stronger shape information, with external evidence weak and conditional; and
4. the reporting/design principle.

---

## Data and code availability

The current section is a developer inventory of modules and function names. Replace it with a journal-facing statement such as:

> Source datasets are cited in the manuscript. Analysis code, environment specification, machine-readable result bundles, figure source data, supplementary material, and release provenance are archived in the Puckworks Paper 1 release at [DOI], corresponding to commit [SHA]. Third-party data not redistributed are identified by source DOI and acquisition instructions in the archive.

Detailed commands belong in a repository README or reproducibility supplement.

---

## References

Regenerate after fixing the coverage detector. Then verify:

- every cited work appears;
- every DOI resolves;
- author names and accents render correctly;
- titles and journals match authoritative metadata;
- the style follows JFE requirements; and
- recent works are not included merely because they exist in `references.bib`—only because they are relevant and cited.

---

# Figure-by-figure review

The following comments are based on the current eight-figure contact sheet and caption map.

## Cross-cutting figure issue: embedded numbers conflict with final presentation numbers

The caption file proposes:

- Figure 1 = `fig1_design`;
- Figure 2 = `fig2_objective_surface`;
- Figure 3 = `fig4_transfer`;
- Figure 4 = `fig6_fraction_vs_endpoint`;
- Figures S1–S4 = producer figures 3, 5, 7, and 8.

The rendered images still contain internal titles such as “Fig 4,” “Fig 6,” and “Fig 3.” If uploaded under the new presentation numbering, those embedded labels will conflict with the captions.

### Required correction

Remove figure numbers and long titles from inside the images. Use only panel letters and short panel headings. Let the manuscript/caption system supply final numbering. Regenerate all figures after the final main/supplement ordering is frozen.

All figures should be exported as vector PDF/EPS where appropriate, with fonts embedded, and inspected at final journal column width.

---

## Figure 1 — study design

### Strengths

- The evidence branches are now scientifically correct.
- The external branch no longer inherits the Angeloni recalibration.
- Table 7 is shown laterally as an orthogonal same-campaign measurement.

### Changes

- Replace the internal title “Paper A study & evidence design (campaign-accurate categories)” with no embedded title or a neutral panel heading.
- Increase text size and reduce explanatory footnotes inside the image.
- Use author-year campaign names rather than registry language.
- Simplify the evidence-tier legend; several border colors are difficult to distinguish at small size.
- Ensure the palette remains interpretable in grayscale and for common color-vision deficiencies.
- The diagram should communicate three branches in under ten seconds: target calibration/holdout, source positive control, external stress test.

---

## Figure 2 — inventory–rate surface and profile

### Strengths

- The surface-plus-profile design demonstrates compensation better than a point estimate would.
- Boundary censoring is shown.
- The profile—not the Hessian—can carry the primary claim.

### Changes

- The title is too long and review-facing.
- The figure shows only caffeine and trigonelline while the manuscript now relies on all six solute × variety panels. Keep one representative main panel if space requires, but include the complete six-panel figure in the supplement.
- The caption says the Table 7 basis is a shaded band; the current visual appears to retain precise horizontal markers and a central point. Make the graphic match the conservative caption.
- Remove or demote the central “measured” inventory point.
- Increase axis, annotation, and colorbar fonts.
- Use a normalized objective scale and clear contour levels; the dark brown surface currently dominates.
- Mark the 10% set with an actual band rather than tiny “set open” text.
- Move condition number and coupling to the caption or supplement if they make the main panel too dense.

---

## Figure 3 — cross-grind model versus baseline (`fig4_transfer`)

### Strengths

- It combines condition-level predictions with the benchmark.
- The identity line makes absolute errors visible.

### Changes

- This should visually foreground the paper's key result: 8.23% versus 8.59%, difference −0.36 pp, primary range crossing zero, and 50/108 points worse.
- The current grouped bar panel is crowded and the legend/text overlap at contact-sheet size.
- Consider replacing the right panel with a forest plot of per-group paired differences plus a pooled difference and primary sensitivity range.
- Keep the observed-versus-predicted scatter as one or two compact panels, not two nearly redundant dense panels if the journal width is limited.
- State `n=108` and the endpoint proxy in the caption rather than the embedded title.
- Use consistent colors for model and baseline across all figures.
- Add the endpoint-sensitivity result after it is completed, perhaps as a small inset or Supplementary Figure.

---

## Figure 4 — fraction versus endpoint profiles (`fig6_fraction_vs_endpoint`)

### Strengths

- The three evidence tiers are juxtaposed effectively.
- Source fractions and exact-cup simulation make the information-loss argument visually intuitive.

### Changes

- The external panel must show the absolute-residual result as well as MAPE.
- Do not label the single cup in a way that resembles a successful zero-error prediction; label it “one scalar + one fitted level: flat by construction.”
- Separate source-campaign empirical evidence, same-model simulation, and external evidence with more prominent panel subtitles.
- Avoid a long sentence as the embedded figure title.
- State the high external minimum error near the profile, not only in the caption.
- Consider normalizing each objective to its minimum for shape comparison while displaying actual minimum errors in annotations.

---

## Figure S1 — LOCO holdouts (`fig3_holdouts`)

### Strengths

- Shows the distribution hidden by a pooled mean.
- Residuals by temperature and pressure are useful diagnostics.

### Changes

- The current title embeds numbers and “not a CI,” which reads like review commentary.
- The figure appears to emphasize the descriptive [5.1, 8.3] range, while the manuscript now treats the OOB refit interval [4.3, 11.5] as the more complete uncertainty summary. Either add the OOB distribution or keep all uncertainty in a supplementary table and make this figure purely diagnostic.
- Increase legend and point-label readability.
- Correct the grammar/typography of the title and remove internal result-status language.

---

## Figure S2 — joint fit and reduced-model ladder (`fig5_joint_residual`)

### Strengths

- Useful support for the claim that parameter sharing has a modest in-sample cost.
- The reduced-model ladder prevents the shared fit from being misread as predictive transfer.

### Changes

- Very dense; suitable only for the supplement.
- Separate the heatmaps and comparator ladder if they are unreadable at page width.
- State clearly that every model is scored on its own fitting data and that parameter counts differ.
- Remove “rate at domain boundary” from the main title and use a compact flag in the table/heatmap.

---

## Figure S3 — per-group diagnostics (`fig7_per_group_diagnostics`)

### Changes

- Replace “independent inventory” with “orthogonal same-campaign inventory assay.”
- Clarify that the correlations are across operating conditions, not over time and not held-out skill.
- The first panel risks implying that inventory matching is a valid physical correction despite the unit-basis problem. Add a prominent qualitative-only label or move this panel behind the Table 7 audit.
- Increase label sizes and reduce unused space.

---

## Figure S4 — residuals versus conditions (`fig8_residuals_vs_conditions`)

### Assessment

This is currently the least informative figure. It has substantial whitespace and small points, and it does not directly support one of the three principal findings.

Options:

- replace it with a compact residual heatmap;
- combine it with Figure S3;
- retain it only as source-data diagnostics; or
- replace it with the missing endpoint-sensitivity or objective-family figure, which would be more valuable to reviewers.

---

# Table review

## Dataset-role table

Scientifically excellent, visually too wide. Simplify in the main paper and move detailed limitations to the supplement.

## Parameter-and-units table

Keep, but add `d32`, unit conventions for Wilke–Chang, and actual grind geometry use. Separate measured, source-fitted, target-fitted, and assumed quantities with an explicit status column.

## Result 1 table

Number it and avoid mixing the three named solutes with the aggregate proxy in the first row. The “strength” column is useful but could use standard labels: descriptive bracket, blind external comparison, target recalibration, internal holdout.

## Cross-grind summary table

Replace broad error ranges with exact group-level values in the supplement. In the main table, show pooled model, baseline, difference, primary range, and count worse.

## Objective-family table

Place the full table in the supplement. Include numerator/denominator for grid fractions and boundary flags.

---

# Detailed editorial and line-level comments

The line numbers below refer to the reviewed current JFE manuscript snapshot and may shift after edits.

| Approx. line/section | Comment | Recommended change |
|---|---|---|
| Title | Strong and appropriately descriptive. | Keep. |
| Authors/affiliations | Placeholders remain. | Complete before external circulation. |
| Abstract, opening | Good problem statement but long. | Use replacement abstract. |
| Abstract, “The profile had an interior…” | Can imply all panels have interior minima. | Restrict the interior statement to the illustrative panel; summarize broad/boundary-reaching sets across all panels. |
| Abstract, “95% resampling interval” | Sounds like a calibrated CI. | Use “clustered percentile sensitivity range.” |
| §1.1 “almost always” | Unsupported categorical claim. | Use “commonly.” |
| §1.1 “kinetic rate” | May imply a measured physical rate constant. | Define and then use “mass-transfer-rate multiplier” / “rate multiplier.” |
| §1.1 cross-references | HTML comments remain in the text. | Replace with final numbered cross-references. |
| §1.1 final contribution sentence | Says temporal preservation decides the distinction. | Broaden to experimental designs that generate distinct sensitivities. |
| §1.2 italic opening note | Internal editorial note. | Delete. |
| §1.2 novelty sentence | Search appears provisional. | Finalize indexed search or soften until complete. |
| Governing equations | `d32` undefined. | Define and add to parameter table. |
| Wilke–Chang equation | Unit convention not stated. | State all units and resulting diffusivity unit. |
| Initial condition | Fully wetted local equilibrium may affect early fractions. | Add limitation and, ideally, sensitivity/discussion. |
| Dataset table | Very wide. | Condense main table; move details to supplement. |
| Parameter table | `d_s2, ψ` says per grind but displays centre values. | Reconcile primary geometry and sensitivity geometries. |
| Endpoint Methods | Excellent caveat but overly long. | Keep core in main; move preprocessing detail to supplement. |
| External preprocessing | Load-bearing but dense. | Add a supplementary flowchart/table. |
| Profile equations | Strong. | Number equations and cite them. |
| Solver | Only parameter-grid convergence is reported. | Add spatial/tolerance convergence. |
| Resampling | Multiple estimands are close together. | Add an estimand table and standardized terminology. |
| Evidence vocabulary | Mentions repo labels. | Remove repo-facing sentence. |
| §3.1 “ρ≈1” | Contradicts careful endpoint caveat. | Delete. |
| §3.1 bracketed note | Reads as reviewer annotation. | Remove or integrate into Methods. |
| §3.1 “caffeine ~2.2, trigonelline at edge, etc.” | Informal and selective. | Give a complete table or delete examples. |
| §3.2 “to good approximation” | Confuses exact level factorization and approximate compensation. | Use the replacement explanation in MC2. |
| §3.2 “independently measured Table 7” | May imply independent campaign. | Use “orthogonal same-campaign assay.” |
| §3.2 Table 7 file path | Repository-facing. | Cite Supplementary Note/Table. |
| §3.2 Hessian | Useful but secondary. | Keep profile primary; move detailed Hessian diagnostics to supplement if needed. |
| Objective family | Supporting note says 18 points, JSON says 29. | Correct note and test. |
| §4 opening | Strong distinction between identification and prediction. | Retain, but reduce italics and repeated caveats. |
| §4 benchmark | Key result appears after a long setup. | Move 8.23 vs 8.59 and −0.36 pp earlier. |
| §4 clustered result | Uses “95% interval.” | Use non-calibrated sensitivity terminology. |
| §4 OOB interval | Can be mistaken for null-difference uncertainty. | Separate paragraph/table by estimand. |
| §4 shared fit/ladder | Useful but long. | Move most detail to supplement. |
| §4 line near “single mean Because” | Missing period. | Correct sentence break. |
| §5 source campaign | Uses registry IDs and gap G6. | Replace with author–year terms; remove gap ID. |
| §5 simulation | Promises supplement variants. | Build and cite actual items. |
| §5 external loss | nRMSE undefined. | State formula. |
| §5 external claim | “always constrains” can overstate a 1.19–1.30 boundary result. | Say “retains weak, loss-dependent rate structure.” |
| Discussion “supersedes…” | Internal revision history. | Delete. |
| Data availability | Function inventory, not journal statement. | Replace with release DOI statement. |
| Declarations | Placeholders. | Complete. |
| Figure captions section | Refers reader to repository path. | In final source, insert/cross-reference captions as required by submission workflow. |
| Bibliography | Missing cited works and raw TeX. | Regenerate with robust citation system. |

---

# Proposed replacement abstract

The following is approximately 242 words by whitespace count and is designed to remain below 250 under common counters. Confirm the final count in the actual Word or LaTeX submission file.

> Whole-cup espresso measurements can be predicted accurately even when extractable content and extraction rate are weakly separated. We examined this problem in a multi-solute extraction model calibrated previously to fraction-resolved data and recalibrated to optimal-grind whole-cup observations from another campaign. Predictions used a 40 mL proxy for the reported 40 g beverage endpoint. At each mass-transfer-rate multiplier, a multiplicative inventory level was re-estimated and the objective profiled. In the illustrative caffeine panel, the numerical minimum was interior, but its 10%-near-optimal set extended from about 0.4 to the upper tested boundary. Across six solute-by-variety panels and three objective families, near-optimal sets were broad and reached a boundary in 16 of 18 cases. After optimal-grind calibration, coarse- and fine-grind predictions had 8.2% pooled MAPE, versus 8.6% for a concentration-only baseline. The paired difference was −0.36 percentage points; the primary clustered percentile range (−0.73 to +0.03) crossed zero, and the mechanistic model was worse on 50 of 108 held-out points. Thus, acceptable endpoint prediction did not provide resolvable skill beyond a transferred concentration level. Fraction-resolved source-campaign observations produced sharper rate profiles than aggregated or simulated whole-cup observations. An external dissolved-solids trajectory retained only a shallow, high-error, loss-dependent preference, while a single cup was uninformative by construction after fitting one level. For the tested espresso model and datasets, matched endpoints are necessary but insufficient: parameter localization, prediction error, benchmark skill, and cross-context evidence should be reported separately. The cross-grind benchmark remains conditional on the endpoint proxy.

After the 38/40/42 mL propagation is complete, replace the final sentence with a direct robustness result if justified.

---

# Proposed JFE Highlights

Each proposed bullet is below 85 characters including spaces and avoids acronyms and specialist shorthand.

- **Whole-cup espresso data weakly separate content from extraction rate** — 68 characters
- **A process model barely outperformed a concentration-only baseline** — 65 characters
- **Time-resolved samples constrained extraction rate more strongly** — 63 characters
- **Accurate prediction did not guarantee well-determined model parameters** — 70 characters

These are preferable to bullets containing “inventory–kinetics compensation profile,” “localize,” “benchmark skill,” or “machine-readable result bundles,” which are less accessible to the general audience Elsevier asks authors to target in Highlights.

---

# Suggested main-manuscript architecture

A tighter journal version could use the following structure.

## 1. Introduction

- Why whole-cup model checks are attractive.
- Inventory–rate compensation problem.
- Literature and precise gap.
- Three research questions and contribution.

## 2. Methods

### 2.1 Model and parameters

Equations, rate multiplier, exact level factorization, assumptions.

### 2.2 Datasets and evidence design

Compact role table; detailed campaign information in supplement.

### 2.3 Observation operators

Cup, fraction, sampled-window aggregate.

### 2.4 Calibration, profiles, prediction, and benchmarks

Objectives, grids, threshold sets, null baseline, resampling estimands.

### 2.5 Endpoint, hydraulics, and numerical verification

40 mL proxy, 38/40/42 propagation, flow maps, mesh/tolerance convergence.

## 3. Results

### 3.1 Whole-cup profiles weakly localize inventory and rate

Representative main profile; six-panel robustness in supplement.

### 3.2 Cross-grind prediction adds no resolvable skill over the level-only null

Put the 8.23/8.59/−0.36 result first.

### 3.3 Time-resolved measurements retain stronger rate-shape information

Source positive control, same-model exact-cup experiment, external stress test.

## 4. Discussion

- Four properties do not coincide.
- Experimental-design implications.
- Model-specific versus general reporting principle.

## 5. Limitations

Short, organized, explicit.

## 6. Conclusions

Four concise sentences.

This structure would remove the current internal “result arc” narration while keeping the scientific progression.

---

# Prioritized action plan

## P0 — required before submission or formal external review

1. **Run the full 38/40/42 mL O-fit → C/F → null benchmark sensitivity.**
2. **Freeze the current title and generate all front matter from one source.**
3. **Reduce and correct the abstract; synchronize package and cover letter.**
4. **Fix citation extraction and regenerate a complete journal-ready bibliography.**
5. **Create the full supplement and every item promised by the main text.**
6. **Regenerate all figures with final numbering removed from the image interiors.**
7. **Show both external losses in the main temporal figure.**
8. **Correct the 18/29-point supporting-record inconsistency.**
9. **Generate a clean, fresh result bundle and reproducibility manifest.**
10. **Complete author metadata, declarations, novelty search, and release DOI.**
11. **Expand the consistency gate to cover all submission files and claims.**

## P1 — required for a strong journal manuscript

12. Add spatial-mesh and solver-tolerance convergence.
13. Define `d32`, Wilke–Chang units, and normalized RMSE.
14. Reconcile the geometry table and primary grind assumptions.
15. Reorder the Table 7 discussion and demote the numerical intersection.
16. Separate all resampling estimands in one table.
17. Cut 20–30% from the main text by moving audit detail to the supplement.
18. Remove repository IDs, paths, functions, review history, HTML anchors, and roadmap language.
19. Redesign the four main figures for final journal size and accessibility.
20. Number and cite every table and figure in order.
21. Replace the developer-facing data-availability section with a release statement.

## P2 — valuable enhancements, not prerequisites for the current paper

22. Add a simple empirical response-surface baseline as a secondary comparator.
23. Implement a mass-based endpoint operator under a declared beverage-density model.
24. Quantify prospective experimental designs that rotate inventory and rate sensitivities.
25. Acquire or design an independent named-solute, multi-grind, fraction-resolved campaign.
26. Test sensitivity to wetting/preinfusion initial conditions in a future model extension.

---

# Proposed automated acceptance gates

A final Paper 1 submission check should fail unless all of the following are true:

## Front matter

- [ ] Title identical in manuscript, package, cover letter, Highlights metadata, and release record.
- [ ] Abstract identical everywhere and ≤250 words; preferably ≤240.
- [ ] Keywords identical everywhere and within venue count.
- [ ] 3–5 Highlights, every bullet ≤85 characters.
- [ ] No author/declaration/DOI placeholders.

## Scientific claims

- [ ] Full 38/40/42 mL transfer/null sensitivity archived.
- [ ] All headline numbers generated from the result bundle.
- [ ] Objective-family grid consistently recorded as 29 points.
- [ ] No statement implies all panel minima are interior.
- [ ] Fixed-predictor ranges are not called calibrated confidence intervals.
- [ ] External rate preference is described as shallow, high-error, loss-dependent, and boundary-censored under the weaker loss.
- [ ] Table 7 is never presented as a quantitative rate constraint.

## Reproducibility

- [ ] Clean checkout; `git_dirty=false`.
- [ ] Bundle commit equals release commit.
- [ ] Figures, source data, manuscript, supplement, and references hashed.
- [ ] Release archive and DOI inserted.
- [ ] Spatial and tolerance convergence documented.

## References

- [ ] Every in-text citation resolves.
- [ ] Raue 2009, Transtrum 2015, Tönsing 2014, Kuhn 2017, and Sánchez-López 2014/2016 are included.
- [ ] No raw TeX accents, `others`, or double-hyphen pages in final output.
- [ ] DOI and bibliographic metadata audit passes.

## Figures and supplement

- [ ] Four main figures and all supplementary figures exist.
- [ ] No embedded figure number conflicts with presentation numbering.
- [ ] External figure shows both loss functions.
- [ ] Six-panel objective-family figure exists.
- [ ] Every “Supplementary” citation points to an actual numbered item.
- [ ] Vector files and readable final-size fonts pass inspection.

## Manuscript hygiene

- [ ] No internal function names or file paths in Results/Discussion.
- [ ] No review-ticket, “owed,” “deferred,” or revision-history language.
- [ ] No HTML anchor comments.
- [ ] Every table and figure cited in order.
- [ ] Data availability cites a stable release rather than a developer command list.

---

# Strengths that should be preserved during revision

1. **The current title.** It solves the original title problem.
2. **The four-property distinction.** This is the conceptual heart of the paper.
3. **The level-only null benchmark.** It converts a modest error into an interpretable skill question.
4. **The exact level profiling.** It is mathematically clean and computationally efficient.
5. **Boundary-censoring language.** It prevents finite-domain profile widths from being overread.
6. **Objective-family robustness across all six panels.** This is much stronger than a single illustrative fit.
7. **The separation of named solutes from aggregate-solids proxies.** Do not allow these to be pooled again.
8. **The explicit evidence tiers.** Keep them, but present them in normal journal language.
9. **The honest external failure/weakness.** High external error and loss dependence improve rather than diminish the paper's credibility.
10. **The dimensional audit of Table 7.** Preserve the caution and use it as an experimental-design lesson.
11. **The inverse-crime declaration.** Same-model simulations should remain clearly scoped.
12. **The distinction between parameter instability and prediction stability.** This is subtle and valuable.

---

# Final verdict

Paper 1 has progressed from an interesting but internally inconsistent research narrative into a serious manuscript with a defensible central contribution. The new title is appropriate, the analytical framing is much more mature, and the principal result is valuable precisely because it avoids a simplistic success/failure conclusion.

I would support submission after a further major revision focused on two layers:

1. **one remaining scientific closure:** propagate the endpoint proxy through the complete model-versus-null benchmark and document numerical convergence; and
2. **submission-object control:** synchronize front matter, repair references, build the supplement, regenerate final figures, and freeze a clean reproducible release.

Until those steps are complete, the paper should not be submitted. The current package can present the wrong title and abstract, the reference audit can falsely pass while omitting cited works, and the manifest itself says the release is stale and dirty. Those defects would distract reviewers from what is now a genuinely strong scientific message.

After they are corrected, the paper should be positioned around this concise claim:

> **In the tested espresso model and datasets, matching whole-cup observations was compatible with weak inventory–rate localization and supplied no resolvable cross-grind skill beyond a transferred concentration level, whereas time-resolved observations retained substantially stronger rate-shape information.**

That is specific, interesting, accessible, and well aligned with *Journal of Food Engineering*.
