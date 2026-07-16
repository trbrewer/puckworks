# Second detailed technical review of the updated `PAPER_A_DRAFT.md`

**Repository:** `trbrewer/puckworks`  
**Repository URL:** <https://github.com/trbrewer/puckworks>  
**Snapshot reviewed:** raw `main` files downloaded on **2026-07-13**  
**Draft revision stated in file:** 2026-07-12  
**Draft SHA-256:** `4b45ad1cab774fda82ee90118fe50ae90f93a521ff7555aef14302c4abcf45ed`  
**Review type:** second-round manuscript, figure, code-path, provenance, and statistical-interpretation review  
**Overall recommendation:** **Major revision before journal submission**

---

## 1. Executive assessment

The updated manuscript is **materially stronger** than the version reviewed previously. It now distinguishes the formal SSE surface from the predictive MAPE metric; replaces the earlier inverse-Hessian “correlation” language with a geometric inverse-curvature coupling; corrects the Schmieder source-design description; separates named solutes from non-equivalent TDS/total-solids proxies; uses matched-beverage-mass endpoints throughout the principal Angeloni analyses; corrects the concentration units in the transfer figures; and gives a much more defensible account of the Waszkiewicz analysis as target-level-profiled external-data objective localization rather than a blind concentration prediction.

The paper’s central qualitative message is plausible and useful:

> A low whole-cup prediction error can coexist with weak practical localization of an inventory–rate decomposition, so endpoint accuracy, parameter identifiability, and predictive performance should be reported separately.

However, the current draft still contains **two validity-critical blockers** and several substantial interpretation and reproducibility problems:

1. **The MAPE cross-check in `identifiability_panel()` is calculated incorrectly.** The code stores `(best level, MAPE)` tuples in a two-column array and then takes minima, thresholds, and means across both columns. Consequently, the manuscript’s numerical statements that the MAPE profile is flat over approximately 33% of the grid and “agrees” with the SSE diagnosis are not presently supported by the implementation.
2. **The manuscript’s principal transfer interpretation is stronger than the analysis performed.** It repeatedly says that predictions are stable “along the compensating manifold,” but the cross-grind routine selects and transfers only **one** O-grind optimum. It never propagates the near-optimal O-grind profile set to C/F predictions. The current evidence supports point-calibration transfer under the assumed maps, not manifold-wide predictive stability.

Additional major concerns are that the O→C/F result is an internal cross-grind holdout within the same Angeloni campaign—not an external prediction; the joint O+C+F fit is an in-sample parameter-sharing compatibility analysis—not predictive transfer; the condition-cluster resampling does not correct all dependence induced by overlapping cross-validation training sets; several headline robustness numbers are calculated after rounding; the matched “40 g” endpoint is implemented as 40 mL under a density approximation; source measurement uncertainty and constructed flow-map uncertainty are not propagated; the exact-cup figure shows one noise realization while the text reports 20; and the paper-build command still does not regenerate every manuscript-facing number.

The appropriate disposition is therefore **major revision**, not rejection. The conceptual arc is substantially improved, and most required work is sharply defined. The revised manuscript should retain its scoped practical-identifiability conclusion, but it should not retain the present MAPE, manifold-stability, dependence-aware interval, or joint-predictive-transfer claims until the analyses below are corrected.

---

## 2. Scope, materials reviewed, and limitations

### 2.1 Files reviewed

I reviewed the current raw-`main` versions of:

- `docs/PAPER_A_DRAFT.md`
- `puckworks/validation/slow/angeloni_bracket.py`
- `puckworks/validation/slow/identifiability.py`
- `puckworks/validation/slow/external_waszkiewicz.py`
- `puckworks/figures_paper_a.py`
- the current six Paper A PNG figures:
  - `fig1_design.png`
  - `fig2_objective_surface.png`
  - `fig3_holdouts.png`
  - `fig4_transfer.png`
  - `fig5_joint_residual.png`
  - `fig6_fraction_vs_endpoint.png`

I also checked the manuscript’s source descriptions against the primary Schmieder, Pannusch, Angeloni, and Waszkiewicz publications and used primary identifiability and cross-validation literature to assess the statistical terminology.

### 2.2 Review method

This was a static and targeted computational audit. I:

- traced each manuscript-facing figure to its plotting function and numerical result object;
- traced major reported values to the slow-analysis routines that generate them;
- inspected objective definitions, nuisance-level profiling, train/test separation, aggregation, rounding, and resampling logic;
- visually reviewed every figure for evidence classification, units, legibility, residual structure, and whether the graphic actually displays the claim made in its title/caption;
- performed direct logic checks on short code paths, including the tuple shape of the MAPE profile and the keys used by the exact-cup report function;
- compared the updated draft with the issues raised in the previous review.

I did **not** rerun the complete approximately 25-minute PDE paper build in a clean, pinned environment. The repository does not yet provide the frozen release/environment that would make such a rerun an auditable submission check. Findings based on direct code inspection are marked as established; requests involving numerical robustness are framed as required reruns rather than asserted outcomes.

### 2.3 Artifact hashes

| Artifact | SHA-256 |
|---|---|
| `PAPER_A_DRAFT.md` | `4b45ad1cab774fda82ee90118fe50ae90f93a521ff7555aef14302c4abcf45ed` |
| `figures_paper_a.py` | `e5617380044d5a8edd927fc7f9c50831d181033476cd9307816562fc19cc8dea` |
| `angeloni_bracket.py` | `253679a5b930bc719167ab7ee3843d920b792fc8f3e0f4d7843d66372170783b` |
| `identifiability.py` | `d6af668ec28253b2c16795c7afef6347b536e8155e0fcc92122a98e3dbd43823` |
| `external_waszkiewicz.py` | `5eef3dd2ee63e743c2319e5e055009faf7f8d2fd957a81475a80ed125701ef85` |
| Figure 1 | `974d245f51604d57f1a38f1912c94e931d89409e97631f8748d104abfb8846bf` |
| Figure 2 | `e989789ca5dca09569654a8d916de882307ea9e611f484bc4b757ced68ac7903` |
| Figure 3 | `a8bb968b3202e79048b803d94181369b7a419b81eaca270b54e969d1ba634479` |
| Figure 4 | `aef8d395259973e0a6edb169abfa62a58aff325cc1eec06b7497724f1c5a83c2` |
| Figure 5 | `af9a46d174c2b3cac59f6e9db97e130bc36fe50424dd65602feac41e0dc368ab` |
| Figure 6 | `da080beb9e063f6aaef57e600d08ac746a2ce3a10a9b9f5eb6ff17a5e0a6b70d` |

These hashes should be superseded by a frozen release tag and archive DOI at submission.

---

## 3. Progress since the previous review

| Previous-review issue | Current status | Assessment |
|---|---:|---|
| Fixed-time integration did not match the target beverage endpoint | **Resolved in the principal analyses** | The Angeloni routines now use a matched endpoint and explicitly retract the earlier cross-grind failure conclusion. A density/mass-volume sensitivity is still needed. |
| Formal analysis was described as MAPE although code used SSE | **Resolved in prose** | The draft now clearly identifies unweighted concentration-scale SSE as the formal curvature objective and MAPE as a secondary predictive cross-check. The MAPE implementation itself has a new/remaining bug; see A2-01. |
| Inverse-Hessian quantity called a statistical correlation | **Largely resolved** | The main Methods/Results correctly call it a geometric inverse-curvature coupling. One stale “correlation” remains in the open-gaps section. |
| Schmieder experimental design misdescribed | **Resolved** | The draft now states ten source fractions, 15 settings, three repetitions and six at the centre, and identifies the repository’s six-window subset. |
| Angeloni rows/replicates and uncertainty insufficiently described | **Improved, not resolved analytically** | Duplicate extractions and the reported RSD range are disclosed, but the fit still uses central values without uncertainty weighting or propagation. |
| Figures 3–4 used `mg/g` instead of concentration units | **Resolved** | Axes now use `g L⁻¹`. |
| Fixed-time species-envelope artifact | **Resolved in description and implementation** | The current bracket is described as matched-mass. |
| Waszkiewicz called a frozen external prediction | **Substantially resolved in manuscript** | The manuscript correctly says target-specific level is profiled. Module docstrings and strength tags still use “prediction.” |
| Same-model exact-cup simulation presented too strongly | **Improved** | The draft acknowledges inverse crime and absent model discrepancy. Figure 6 still shows only one seed and not the reported distribution. |
| Cross-validation interval treated as a conventional CI | **Partly improved** | The simple residual interval is now explicitly descriptive. The condition-cluster interval is still called dependence-aware and its near-equivalence is overinterpreted. |
| End-to-end paper build incomplete | **Improved but still false as written** | More analyses were added to `compute_all()`, but `refit_pannusch_angeloni()`—the source of the 8.4%/11.5% Result 1 values—is still omitted. |
| Manuscript looked like an internal analysis note | **Still unresolved** | Repository notes, review IDs, “owed” items, function names, handoff language, and open-gap bookkeeping remain in the manuscript body. |

---

## 4. Prioritized required-action matrix

### 4.1 Submission-blocking actions

| ID | Priority | Finding | Required action | Acceptance criterion |
|---|---:|---|---|---|
| **A2-01** | **P0** | MAPE profile mixes nuisance-level and MAPE columns | Fix `mape_prof` extraction, rerun both panels, regenerate Figure 2 and every related sentence | MAPE array is one-dimensional and independently unit-tested; all MAPE-flatness values are regenerated from the corrected array |
| **A2-02** | **P0** | “Stable along the compensating manifold” is not tested | Propagate an explicitly defined near-optimal O-grind profile set to C/F predictions, or delete the manifold-wide claim | Predictive distribution/envelope over the profile set is shown; tolerance and objective are stated; median, range, and worst-case transfer error are reported |
| **A2-03** | **P0** | Evidence classes are overstated | Reclassify O→C/F as internal cross-grind holdout, Table 7 as same-campaign independent-measurement constraint, and joint O+C+F as in-sample shared-parameter compatibility | Abstract, §2.6, §5, Fig. 1, Fig. 5, captions, result bundle, and code docstrings all use the same taxonomy |
| **A2-04** | **P0** | Condition-cluster bootstrap does not establish dependence-corrected coverage | Relabel it as a descriptive condition-level resampling summary, or implement a resampling scheme that repeats model selection/fitting and justifies its inferential target | No “dependence-aware CI” or “fold dependence does not widen” claim remains without a validated procedure |
| **A2-05** | **P0** | Paper build does not regenerate every manuscript-facing result | Add the omitted Result 1 refit and create one deterministic build that emits numbers, tables, source data, and figures from one result bundle | A clean-environment command reproduces all reported values and figure files; no manuscript value comes from a separate hand-run path |

### 4.2 Major analytical actions

| ID | Priority | Finding | Required action | Acceptance criterion |
|---|---:|---|---|---|
| **A2-06** | P1 | Local Hessian claims exceed numerical support | Repeat with continuous or substantially denser optimization, multiple finite-difference steps, parameter scalings, and rate domains | Condition number/coupling are reported as scale- and local-method-dependent diagnostics; convergence/sensitivity table supplied |
| **A2-07** | P1 | Profile width is censored by tested domain | Label intervals that touch a sweep boundary as open/right-censored and report width “within the tested domain” | No “bounded minimum” or “domain-independent” wording when the threshold set reaches a boundary |
| **A2-08** | P1 | Global/profile metrics ignore measurement uncertainty | Add weighted/heteroscedastic sensitivity using source RSD information or a justified error model | Main conclusion survives a declared weighting/noise sensitivity, or is narrowed accordingly |
| **A2-09** | P1 | Matched 40 g is implemented as 40 mL | State and test density/endpoint assumptions, including the source’s endpoint tolerance | Sensitivity covers plausible density and 38–42 g endpoint range; units in code/results are explicit |
| **A2-10** | P1 | Constructed pressure–flow maps are treated too deterministically | Propagate uncertainty/sensitivity in hydraulic coefficients, nominal shot times, viscosity, density, and time alignment | Transfer results include a flow-map uncertainty range or are explicitly conditional without robustness language |
| **A2-11** | P1 | Geometry spread is calculated after integer rounding | Retain full precision through all aggregation and round only display output | Reported maximum geometry spread is based on unrounded values and has a reproducible precision policy |
| **A2-12** | P1 | Joint independent-fit aggregate partly reuses rounded values | Preserve an unrounded internal results object for independent-fit MAPEs | Pooled and cost-of-sharing values are calculated from unrounded values; display rounding occurs last |
| **A2-13** | P1 | Exact-cup text reports 20 seeds, figure shows seed 0 only | Store and plot seed distributions/quantiles; fix broken report keys; add model-discrepancy scenarios | Figure and text display the same simulation ensemble; `python -m ...identifiability` completes without error |
| **A2-14** | P1 | Waszkiewicz robustness is incomplete | Retain full precision and vary temperature, flow floor, density conversion, and reasonable alignment/operator choices | External panel includes a compact sensitivity table and consistently uses “objective localization” |
| **A2-15** | P1 | Table 7 is called an external tie-breaker | Quantify how the measured inventory intersects/constrains the profile and label it as an orthogonal measurement from the same campaign | Profile-constrained rate estimate/range is shown with measurement uncertainty if available; same-campaign status explicit |
| **A2-16** | P1 | Figures do not display several headline claims | Redesign Figures 1–6 as detailed in §7 | Every figure has neutral titles, complete units, source-data export, and visually exposes rather than merely asserts the key comparison |

### 4.3 Manuscript and software-quality actions

| ID | Priority | Finding | Required action | Acceptance criterion |
|---|---:|---|---|---|
| **A2-17** | P1 | Manuscript remains an internal working document | Convert to a conventional journal manuscript and move review/change-log material to repository documentation | No review IDs, handoff notes, “owed,” code-function prose, or repository banner in submitted manuscript |
| **A2-18** | P1 | Methods are not yet sufficient for independent reproduction | Add equations, endpoint operator, objectives, weighting, parameter domains, optimization, CV, resampling, software/environment, and data exclusions | A reader can reconstruct every analysis without reading Python source |
| **A2-19** | P2 | Stale contradictions remain | Complete a terminology/consistency sweep | “Correlation,” “single measurements,” “negative validation,” “external prediction,” and outdated docstrings are removed or corrected |
| **A2-20** | P2 | Source-data and figure deliverables are incomplete | Export vector figures and tidy source-data tables | SVG/PDF/EPS plus machine-readable source data are produced by the paper build |

---

## 5. Detailed major comments

## 5.1 A2-01 — the MAPE profile cross-check is invalid as currently computed

**Location:** `angeloni_bracket.py`, approximately lines 633–690; manuscript abstract lines 29–35 and §4 lines 244–262.

`_mape_level(f, m)` explicitly returns a two-element tuple:

```python
return c, float(np.mean(np.abs(c * f - m) / m) * 100.0)
```

but `identifiability_panel()` constructs:

```python
mape_prof = np.array([_mape_level(F[i], m) for i in range(n_rate)])
```

This yields an array of shape `(n_rate, 2)`, whose first column is the best inventory level and whose second column is MAPE. The subsequent operations:

```python
mape_min = float(np.min(mape_prof))
within_mape = mape_prof <= mape_min * 1.10
frac_within_mape = float(np.mean(within_mape))
```

therefore compare and average **inventory values and MAPE values together**. The returned `mape_profile_fraction_within10pct` and `mape_cross_check_agrees` are not meaningful MAPE-profile statistics.

**Required correction:**

```python
mape_prof = np.array([_mape_level(F[i], m)[1] for i in range(n_rate)], dtype=float)
```

Preferably also retain the MAPE-optimal nuisance level separately:

```python
mape_pairs = [_mape_level(F[i], m) for i in range(n_rate)]
mape_c_star = np.array([x[0] for x in mape_pairs])
mape_prof = np.array([x[1] for x in mape_pairs])
```

Then add a unit test with synthetic arrays for which the weighted-median MAPE profile is calculable by hand. The test should verify array shape, minimum, threshold membership, and boundary handling.

**Manuscript consequence:** Until the corrected run is complete, remove:

- “and a MAPE cross-check that agrees” from the abstract;
- “flat over ~33% of the grid”; and
- “consistent across the SSE and MAPE objectives.”

The SSE profile and surface are not invalidated by this specific bug, so the paper may continue to present the SSE-based practical-confounding result after the numerical robustness work in A2-06/A2-07.

---

## 5.2 A2-02 — manifold-wide predictive stability is asserted but never evaluated

**Location:** abstract lines 36–42; §5 lines 269–302; Discussion lines 428–437; `validate_refit_granulometry()` approximately lines 490–574.

The paper’s most important interpretive sentence is that predictions are “stable along the compensating manifold.” That claim would be valuable because it would directly demonstrate the distinction between parameter identifiability and prediction identifiability. The current code, however, does not perform that experiment.

For each variety/solute, `validate_refit_granulometry()`:

1. evaluates O-grind MAPE over the finite rate grid;
2. selects one discrete optimum `(rsO, cs0O)`;
3. freezes that one pair; and
4. predicts C and F.

No alternative near-optimal O-grind pairs are transferred. The code’s docstring says that “predictions along that compensating manifold stay stable across grind,” but the implementation supplies no such distribution or envelope.

**Required analysis:**

1. Choose and justify a near-optimal set, for example:
   - O-grind predictive MAPE ≤ 1.10 × minimum;
   - or an absolute ΔMAPE threshold declared in advance;
   - and, separately, the SSE threshold used in the identifiability panel.
2. At every rate in the set, use the objective-appropriate profiled inventory.
3. Freeze each resulting pair and predict all C/F observations.
4. Report for each variety × solute × grind:
   - point-optimum MAPE;
   - median MAPE across the set;
   - 5th–95th percentile or full range;
   - worst-case MAPE;
   - pointwise predictive bands;
   - whether ranking and systematic residual direction change along the set.
5. Repeat with Table 7 inventory fixed or constrained, so the effect of the orthogonal measurement is visible.

A profile can be flat for the fitting observable while predictions at a new design vary strongly. Conversely, predictions may be stable. That is an empirical question, not a consequence of the existence of a compensation valley.

**Interim replacement wording:**

> One selected O-grind calibration predicts the held-out C/F conditions with approximately 3–18% MAPE under the assumed endpoint and flow maps. Stability of those predictions over the full near-optimal O-grind profile has not yet been evaluated; the current evidence therefore supports point-calibration transfer, not manifold-wide predictive stability.

---

## 5.3 A2-03 — evidence taxonomy must be corrected consistently

The manuscript commendably introduces an evidence vocabulary, but applies it inconsistently.

### O→C/F transfer

C and F are held-out granulometries from the **same Angeloni campaign**, with the same varieties, experimental platform, assay framework, and source study. This is a meaningful internal design extrapolation or cross-grind holdout. It is not an “external prediction” in the manuscript’s own definition of a genuinely different rig/coffee.

Figure 1 currently labels the O→C/F arrow **external prediction**. Replace it with **internal cross-grind holdout** or **within-campaign design extrapolation**.

### Table 7 inventory

Table 7 is an orthogonal measurement from the Angeloni study, which is useful because it measures a different quantity than the beverage concentrations. It is not external to the transfer campaign. Call it a **same-campaign independent-measurement constraint** or **orthogonal inventory measurement**.

The arrow in Figure 1 should point from Table 7 toward the profile/calibration, because the measurement constrains or selects among parameter pairs. The present arrow from C/F transfer to Table 7 suggests that the transfer generates the constraint.

### Joint O+C+F fit

`joint_multigrind_fit()` fits the shared pair using O, C, and F and then scores those same pooled observations. It is an **in-sample shared-parameter reconstruction/compatibility analysis**. It can answer whether forcing one pair causes a large in-sample cost relative to separate fits. It cannot “confirm” held-out transfer and should not be called “joint predictive transfer.”

The manuscript’s statement that the joint fit “confirms” cross-grind transfer should become:

> A shared pair fitted to all three grinds reconstructs the pooled data with 6.4% macro-average MAPE, compared with 4.9% for separate per-grind fits. This indicates a modest in-sample cost of parameter sharing under the assumed maps; it is a compatibility analysis, not a held-out prediction.

### Original Pannusch→Angeloni comparison

The blind evaluation of the unrefitted Pannusch calibration against Angeloni is the true cross-dataset external prediction. Figure 1 would be clearer if it included this path explicitly. The current diagram visually centers the within-Angeloni refit and omits the genuinely external Waszkiewicz panel.

---

## 5.4 A2-04 — the condition-cluster bootstrap is descriptive, not a demonstrated dependence correction

**Location:** §5 lines 304–325; open gaps lines 459–468; `loco_cv_refit()` approximately lines 737–840; Figure 3 title.

The draft correctly notes that the 54 held-out errors are dependent. It then constructs nine macro-errors—one per `(T,p)` condition, averaged across variety and solute—and resamples those nine values. This is a useful **condition-level descriptive resampling summary**, but it does not by itself resolve the full dependence structure because:

- all leave-one-condition-out fits have highly overlapping training sets;
- the bootstrap resamples already-computed final errors rather than resampling the original experimental units and repeating parameter selection/fitting;
- the six outputs attached to a condition share design and model structure;
- source duplicate extractions are unavailable at replicate level in the repository representation;
- there are only nine condition clusters.

Bengio and Grandvalet show that K-fold/leave-one-out errors are dependent and that no universal unbiased variance estimator exists from the fold errors alone. Nadeau and Bengio likewise emphasize variability induced by training-set choice. These papers do not forbid all useful resampling, but they make “dependence-aware confidence interval” too strong for the present algorithm.

The near-coincidence of `[5.0, 8.2]` and `[5.1, 8.3]` also does **not** demonstrate that fold dependence is immaterial. It may simply reflect two summaries of the same limited set of errors.

**Required wording now:**

> Resampling the nine condition-level macro-errors yielded a descriptive [5.1, 8.3]% interval. Because the cross-validation fits share training observations and the resampling did not repeat fitting, this interval is not coverage-calibrated and does not correct all dependence among fold errors.

**Stronger future options:**

- obtain replicate-level source data and bootstrap experimental conditions/replicates while rerunning the complete nested fit;
- use repeated grouped splits designed around the inferential target;
- report the nine condition macro-errors directly without attaching frequentist coverage language;
- use a hierarchical observation model if the measurement structure can be reconstructed.

Figure 3 should not place “condition-cluster bootstrap [5.1, 8.3]” in its title unless the caption clearly says descriptive and non-coverage-calibrated.

---

## 5.5 A2-05 — the paper build still omits manuscript-facing analyses

`figures_paper_a.compute_all()` says that every slow analysis cited by the manuscript is regenerated. It calls the bracket, per-condition evaluation, flow-map refinement, identifiability panels, transfer, joint fit, LOCO, geometry sensitivity, positive control, exact-cup simulation, aggregate audit, and Waszkiewicz analysis.

It does **not** call `refit_pannusch_angeloni()`, even though Result 1 reports the refit’s named-solute holdout of approximately 8.4% and TDS proxy result of approximately 11.5%. Therefore the manuscript statement that “every value regenerates … none hand-typed” is false as written.

A defensible paper build should:

1. run every numerical analysis once;
2. write a versioned, schema-validated result bundle containing full-precision values;
3. generate all manuscript tables from that bundle;
4. generate figures from the same bundle without refitting inside plotting code;
5. export figure source-data tables;
6. record repository commit, dirty status, Python version, package lock, OS/platform, random seeds, solver tolerances, and data checksums;
7. produce vector figures in addition to PNG previews;
8. fail if a manuscript table/figure requests a missing key;
9. be exercised in a clean environment before release.

The build should also validate semantic invariants, such as MAPE profile dimensionality, no aggregation after display rounding, endpoint units, and the train/test membership of every score.

---

## 5.6 A2-06/A2-07 — local Hessian and profile claims need numerical qualification

The log-parameter Hessian is a useful local geometric diagnostic, but the current wording is too definitive.

### Nearest-grid-point curvature is not a verified continuous optimum

The code chooses the best point on an 18-value rate grid and the nearest point on a 2D inventory grid, then applies central finite differences. “Interior optimum” means only that the selected grid point is not an endpoint. It does not establish that the continuous gradient is zero, that the Hessian is converged, or that the reported condition number is stable.

### Condition number depends on parameter scaling

Using log parameters is reasonable, but it is not uniquely “the standard sloppiness basis.” Condition numbers are parameterization- and scaling-dependent. The manuscript should state that the value describes the local SSE geometry **in the declared log-coordinate system**.

### Reliability flag is heuristic

`hessian_reliable` checks boundary status, a numerical flatness rule, and whether the inverse-derived coupling is finite/in range. It does not test finite-difference convergence, grid convergence, local positive definiteness under alternative steps, or continuous stationarity.

### Profile set reaches a tested-domain boundary

For caffeine, the within-10% interval `[0.4, 6.5]` reaches the upper sweep limit. The upper endpoint is therefore censored by the tested domain. `profile_log_width` is not “domain-independent,” as a code comment states; it is the width observed **within the selected domain** and can increase if the sweep is extended.

### Required numerical appendix

For each formal panel, report:

- continuous one-dimensional optimization of the profiled objective or a much denser grid;
- at least three rate-grid densities and expanded domains;
- at least three finite-difference step sizes in log coordinates;
- local gradient norm at the reported point;
- Hessian eigenvalues and sign;
- condition number under declared coordinate scalings;
- profile threshold intervals with open/closed boundary notation;
- MAPE-profile results after A2-01;
- all solutes and both varieties in supplement, not only two Arabica panels.

The practical-confounding conclusion should rely primarily on the profile, while the Hessian is presented as a local corroborating geometric diagnostic. This aligns with the identifiability literature’s caution that local curvature/Fisher approximations can miss nonlinear, asymmetric, or unbounded profiles.

---

## 5.7 The “identifiability ratio” is descriptive, not a universal identification rule

Methods §2.5 says that a max-edge/minimum MAPE ratio much greater than one means the rate “is identified,” whereas a ratio near one means it is not. This ratio depends on:

- the arbitrary sweep endpoints;
- grid density;
- noise realization;
- selected loss;
- nuisance-level treatment;
- number and weighting of observations;
- the minimum’s absolute error.

There is no universal threshold at which such a range ratio establishes identifiability. Rename it **objective-profile contrast over the stated rate domain**. Use it to compare observation operators under a shared design, but avoid categorical “identified/not identified” decisions based only on that ratio.

Suggested Methods wording:

> We report the ratio of the maximum to minimum profiled MAPE over the declared sweep as a descriptive profile-contrast statistic. Its magnitude is domain- and loss-dependent and is not treated as a confidence bound or universal identifiability threshold.

---

## 5.8 A2-09 — “matched 40 g” is implemented as 40 mL

The Angeloni code sets a 40.0 mL target and computes `t_end = 40 mL / Q`, effectively using beverage density ≈1 g/mL. The source endpoint is expressed as beverage mass, approximately 40 ± 2 g. The Waszkiewicz module similarly treats `g/s ≈ mL/s` under `ρ≈1`.

This may be a small approximation, but it is load-bearing because the paper’s corrected conclusion hinges on endpoint matching. The manuscript should not silently equate mass and volume.

**Required actions:**

- define whether model flow is volumetric or mass flow at every interface;
- state the density approximation explicitly;
- test density over a defensible espresso range or use measured/temperature-dependent density where available;
- test the source endpoint tolerance, at minimum 38, 40, and 42 g;
- report how transfer, profile width, and point optimum change;
- use variable names such as `target_beverage_mass_g` and `target_beverage_volume_mL` rather than one representing the other.

---

## 5.9 A2-10 — uncertainty in the constructed flow maps is not propagated

The cross-grind flow is inferred from fitted hydraulic-conductivity polynomials, nominal grind-specific shot times, a viscosity correction, and density equivalence. No condition-specific measured flow trace is used. The draft discloses this, which is good, but then describes transfer as robust based mainly on switching the global grain geometry.

A geometry sweep does not cover uncertainty in:

- polynomial coefficients;
- nominal O/C/F shot times;
- pressure calibration;
- viscosity closure;
- beverage density;
- whether the hydraulic relation transfers across all `(T,p)` points;
- possible pressure/flow transients.

The current transfer result should be described as conditional on the constructed map. A useful uncertainty analysis would sample plausible hydraulic coefficients and shot times, recompute the profile/fit, and propagate them to held-out predictions. Where coefficient covariance is unavailable, report a structured scenario analysis rather than an unjustified probability interval.

The claim that the two tested O-grind flow maps differ by only ~0.5 percentage points is informative only within those two choices; it is not a general flow-map uncertainty bound.

---

## 5.10 A2-08 — unweighted SSE and central-value MAPE do not use the source uncertainty structure

The formal SSE panel gives high-concentration species/conditions greater absolute influence, while MAPE gives approximately relative influence. Neither reflects the source’s reported, uneven analytical variability. The manuscript notes RSD values of approximately 0.3–19.7% but uses only central values.

The main conclusion need not depend on a fully specified likelihood, but a serious practical-identifiability study should test whether the valley and transfer metrics survive plausible observation models. At minimum:

- show residuals versus fitted concentration, solute, variety, temperature, pressure, and grind;
- compare unweighted SSE, relative SSE/log error, and uncertainty-weighted SSE where source RSDs can be mapped;
- explain how duplicate extractions were summarized;
- distinguish assay uncertainty from model discrepancy;
- avoid calling tolerance sets confidence intervals.

If condition-level uncertainty cannot be recovered, say so and use a sensitivity range based on the published RSD envelope rather than ignoring it.

---

## 5.11 Table 7 is valuable but not an external validation dataset

The measured solid inventories are orthogonal to the beverage outputs and can reduce the inventory–rate ambiguity. That is a strong design point. But Table 7 comes from the same Angeloni study/campaign family and should not be labeled “external” relative to the Angeloni concentration fit.

The present text mainly notes that the profile crosses the reported inventory. That is qualitative. The revision should quantify:

- the rate(s) at which the profiled inventory equals the Table 7 value;
- the rate interval induced by any reported inventory uncertainty;
- the beverage-fit penalty at the constrained inventory;
- whether the constrained rate is interior and stable to objective, flow map, and domain;
- whether the result differs by variety and solute.

This would convert “one available tie-breaker” into a reproducible constrained-estimation result.

---

## 5.12 A2-11/A2-12 — retain full precision until presentation

### Geometry sensitivity

`geometry_sensitivity_transfer()` rounds each held-out C/F MAPE to a whole percentage point before computing the range and maximum spread. A reported “≤1 pp” spread can therefore be created or suppressed by display rounding.

Store full-precision MAPEs, compute all spreads from them, and round only the final displayed fields. Include enough decimal places to show whether the practical conclusion depends on rounding.

### Joint-fit comparator

`joint_multigrind_fit()` computes independent per-grind values at full precision but stores them rounded to 0.1 before the final global independent mean is calculated from the stored dictionary. The distortion is likely small, but the comments claim full-precision aggregation. Maintain a private/full-precision object and derive display dictionaries afterward.

### Grid-interior language

“All rates interior” means the selected members of an 18-point grid were not the first/last entries. Call them “non-boundary grid selections,” not converged continuous interior optima, unless continuous optimization is performed.

---

## 5.13 A2-13 — exact-cup simulation reporting and executable path are inconsistent

The manuscript reports means and standard deviations across 20 noise seeds and 100% recovery of the calibrated rate. Figure 6, however, plots only the first noise realization (`seed 0`) because `full_cup_simulation_identifiability()` stores only `fm0` and `cm0` for the curve data.

Twenty random-noise realizations of one simulated design are not “20 independent seeds” in an experimental sense; call them **20 random-noise realizations**.

The figure should display either:

- all profiles faintly plus a median; or
- median profiles with quantile ribbons; or
- a distribution of best-rate and profile-contrast statistics.

The exact-cup and fraction curves should use comparable visual scaling or report normalized objective increase so that different y-axis ranges do not visually manufacture “sharp” versus “flat.”

The command-line report also appears broken. It requests `frac_best_rate` and `cup_best_rate`, whereas the returned simulation dictionary contains `frac_best_rate_median` and no `cup_best_rate`. The advertised module command should be executed in the release test.

Finally, add at least one model-discrepancy scenario—e.g., synthetic data generated with perturbed equilibrium, a different mass-transfer law, or misspecified flow—because the current inverse-crime result only establishes information behavior when truth and fitting model are identical.

---

## 5.14 A2-14 — Waszkiewicz wording is much improved, but the sensitivity set remains narrow

The manuscript now correctly says that a target-specific multiplicative level is fitted at each rate and that the one-cup profile is flat algebraically. This is a major improvement.

Remaining issues:

- the module’s top-level and function docstrings still say “predict”/“frozen external prediction”;
- the returned strength tag still says “external prediction / objective localization”;
- MAPE values are rounded before minima and range ratios are computed;
- brew temperature is fixed at 93 °C;
- the pre-drip flow floor is fixed at 0.05;
- mass flow is converted to volumetric flow using density ≈1;
- only three time offsets and one first-bin inclusion choice are examined.

Use **external-data objective localization** consistently. Retain full precision. Add a compact sensitivity over temperature, flow floor, density, and plausible time-alignment/operator choices. Because the minimum MAPE is approximately 27%, emphasize that the frozen kinetic shape is only moderately compatible with the external TDS trajectory.

The abstract phrase “the integrated cup carries no rate information at all” should read:

> for this one-shot, one-free-level construction, the integrated scalar is algebraically uninformative about rate.

---

## 5.15 The manuscript still reads as a repository handoff rather than a submission

The opening repository note, change-log references, review IDs, code-function names, “owed” statements, “handoff §2.6,” ROADMAP references, open-gap bookkeeping, and internal strength tags should not appear in the journal manuscript.

A submission-ready paper needs conventional sections and declarations, including:

- title page, authors, affiliations, corresponding author;
- highlights if required by the target journal;
- abstract and keywords;
- nomenclature or parameter table;
- governing equations and observation operators;
- complete Methods independent of code;
- Results without repository review commentary;
- Discussion and limitations;
- Conclusions;
- data availability;
- code availability and frozen release/DOI;
- funding, conflicts of interest, author contributions, acknowledgements;
- complete formatted references;
- supplementary-information map.

The Journal of Food Engineering guide asks for editable source files, including editable figures/tables/text graphics. The build should therefore produce suitable vector/editable outputs rather than only PNGs.

---

## 5.16 Internal contradictions and stale language need a final sweep

Examples include:

- **Open gaps:** “rate↔inventory correlation −0.99” reintroduces the statistical-correlation wording corrected elsewhere.
- **Replicates:** Methods says Angeloni records are based on duplicate extractions, while open gaps says named-solute rows are “single measurements.” Clarify that the repository holds one reported central value per condition, derived from duplicate source extractions.
- **Grid robustness:** §4 says the result is “not an artefact of a coarse grid,” then immediately says grid-density/domain robustness remains owed. The stronger statement should wait for the appendix.
- **Evidence:** §5 says “held-out / joint predictive transfer,” although the joint fit is in-sample.
- **Strength tags:** Reproducibility still calls granulometry validation “negative (held-out grind),” which contradicts the current “reasonable transfer” conclusion.
- **Code docstrings:** `joint_multigrind_fit()` still predicts failure, calls the test external, and says each grind has measured flow. `validate_refit_granulometry()` claims manifold stability not calculated. Earlier functions contain stale fixed-time and inventory/kinetics interpretations.
- **Terminology:** Figure 1 footer uses “identification” rather than “identifiability.”

Add an automated search for retired phrases and a human consistency pass across manuscript, captions, result JSON, docstrings, and README/reproducibility notes.

---

## 5.17 The source-data description is now substantially better, but the statistical unit must remain explicit

The updated Schmieder description now matches the source study: ten consecutive fractions under 15 settings, generally three repetitions and six at the central point; the repository uses a derived six-window subset. Retain this distinction everywhere, including Figure 1 and supplementary data-flow diagrams.

For Angeloni, distinguish four levels:

1. experimental condition;
2. duplicate extraction replicate in the source;
3. reported condition-level central value retained by the repository;
4. multiple analytes measured on that condition.

The 54 LOCO errors are not 54 independent shots. They are six modeled outputs for each of nine shared conditions. The manuscript’s statistical-unit language should be based on that hierarchy.

---

## 5.18 “Reasonable transfer” needs a declared benchmark rather than post hoc interpretation

The held-out range of approximately 3–18% spans very different levels of agreement. The paper should define what “reasonable” means before using it as a conclusion. Possible benchmarks include:

- source analytical variability;
- Angeloni’s own reported model error, carefully matched by observable and aggregation;
- a pre-specified practical threshold;
- comparison with a simple empirical baseline;
- relative improvement over the unrefitted Pannusch prediction.

Report per-condition, per-solute, and per-variety results rather than relying on a broad range and macro-average. The systematic horizontal bands visible in Figures 3 and 4 suggest that condition sensitivity may be compressed even where average level is acceptable. A model can obtain moderate MAPE by fitting group levels while failing to reproduce within-group slopes across process settings.

---

## 6. Section-by-section manuscript comments

### Title and abstract

The title is engaging and appropriately signals a case study. “The cup can hide the clock” is defensible only with the scoped qualifiers now present in much of the text. Avoid implying a universal endpoint impossibility.

The abstract should be revised after A2-01/A2-02. It currently contains too many implementation-specific numerical diagnostics and three distinct evidence arcs. A clearer structure would be:

1. problem and datasets;
2. formal single-grind practical-confounding result;
3. internal holdout point-calibration performance;
4. time-resolved versus integrated observation comparison;
5. scoped implication.

Delete “predictions are stable along the compensating manifold” until tested. Qualify the one-shot Waszkiewicz cup result. Avoid presenting the joint in-sample fit as predictive evidence.

### Introduction

The introduction is clear but sometimes shifts from the tested case to broad claims that endpoint validation is “almost always” used and interpreted mechanistically. Either support those field-wide claims with a systematic literature sample or narrow them to a recognized risk in the literature.

The contribution is not a new held-out protocol in a formal methodological sense unless the protocol is specified generically and evaluated beyond this case. Present the contribution as an applied demonstration and reproducible case-study workflow.

### Methods

This section needs equations and enough detail to reproduce the analysis without reading code. Add:

- PDE summary and exact parameter definitions/units;
- proof or derivation of linearity in `c_s0` under the implemented normalization;
- SSE and MAPE equations;
- weighted-median nuisance-level derivation;
- endpoint operator and mass/volume conversion;
- rate grids/domains and why chosen;
- all fixed parameters and source mappings;
- flow-map equations and coefficients;
- train/test partitions;
- joint-fit macro-averaging definition;
- LOCO fitting sequence and error aggregation;
- resampling target and algorithm;
- simulation truth, noise model, number of conditions, and seeds;
- software versions/tolerances.

### Result 1

Separate the blind external Pannusch→Angeloni evaluation from the within-Angeloni refit. Do not place TDS proxy and named-solute metrics in the same “overall” number unless the composition is unmistakable. The claim that the fixed-time error was “mostly” an endpoint artifact should be backed by a decomposition table showing old versus corrected endpoint under otherwise identical code.

### Result 2

This is the paper’s strongest section after correction. Keep the scoped practical-confounding language. Replace “unambiguous,” “reliable Hessian,” and “not a coarse-grid artifact” with language proportionate to the numerical checks actually completed. Correct the MAPE result before publication.

### Result 3

Rename the section **Internal cross-grind holdout and shared-parameter compatibility**. Separate:

- one O optimum frozen to C/F: internal prediction;
- near-optimal profile propagated to C/F: prediction-identifiability analysis, currently missing;
- one pair fitted jointly to O+C+F: in-sample compatibility;
- global geometry scenarios: limited structural sensitivity;
- LOCO within O: internal condition holdout.

These answer different questions and should not be pooled into one “confirmation.”

### Section 6

The three observation comparisons are useful but have different evidence levels:

- Schmieder fractions versus sampled aggregate: in-sample empirical verification on calibration-lineage data;
- exact whole-cup simulation: same-model information experiment;
- Waszkiewicz trajectory versus one integrated scalar: external-data objective localization with an algebraically flat one-point comparator.

Keep them visibly separate in text and figures. Avoid averaging their evidential force into “consistently constrains” without the design qualifiers.

### Discussion and conclusions

Retain the distinction between parameter and prediction identifiability, but only claim the latter after A2-02. Discuss other ways endpoint designs can identify rate: multiple endpoints, varying residence times, independent inventory, informative priors, and joint multi-condition designs. The final conclusion should emphasize that the problem is design- and observation-operator-specific, not a theorem about cups.

---

## 7. Figure-by-figure review

## Figure 1 — study and evidence design

**What works:** The flow diagram is clean, legible, and valuable for separating calibration, holdout, and verification.

**Problems:**

- O→C/F is mislabeled “external prediction.”
- Table 7 is mislabeled “external constraint.”
- The Table 7 arrow direction is conceptually reversed.
- The genuinely external Waszkiewicz analysis is absent.
- The blind original Pannusch→Angeloni comparison is not distinguished from the within-Angeloni refit.
- The footer says “identification” rather than “identifiability.”

**Required redesign:** Use lanes for **data source** and **evidence use**. Show Pannusch/Schmieder calibration lineage, blind Angeloni external evaluation, Angeloni O refit, O-condition CV, C/F internal holdout, same-campaign Table 7 constraint, joint in-sample fit, same-model simulation, and external Waszkiewicz localization. Use a legend with unambiguous evidence classes.

---

## Figure 2 — inventory–rate objective surface

**What works:** The valley is visually obvious, the profiled path is useful, and the Table 7 line makes the independent-measurement idea concrete.

**Problems:**

- no colorbar or objective units;
- the filled surface uses raw SSE over a limited range without showing normalized objective increase;
- only one 1.1× contour is shown;
- `c_s0` lacks units and physical definition;
- condition numbers dominate panel titles without their coordinate/local-method qualification;
- no profile-objective panel shows the threshold set or boundary censoring;
- the plotted result bundle inherits the invalid MAPE cross-check, though the surface itself is SSE;
- the trigonelline Table 7 line sits far above much of the profile, which deserves direct quantitative interpretation.

**Required redesign:** Add a colorbar for `ΔSSE/SSE_min` or `SSE/SSE_min`; show multiple contours; label inventory units; add a lower profile strip with SSE and corrected MAPE; shade the declared near-optimal set; mark open/censored boundaries; report coupling/condition number in caption or inset with coordinate and finite-difference method.

---

## Figure 3 — leave-one-condition-out holdouts

**What works:** It exposes every held-out point and separates varieties.

**Problems:**

- the title promotes a condition-cluster “bootstrap” interval without its descriptive limitation;
- pooled concentration scatter is dominated by between-analyte and between-variety level differences;
- horizontal point bands suggest limited sensitivity to `(T,p)` within each group, but the figure does not display residuals or condition labels;
- axes do not use equal limits/aspect, weakening visual error comparison;
- no uncertainty bars are shown;
- the worst Robusta 5-CQA fold cannot be identified from the graphic.

**Required redesign:** Use equal aspect and matched limits. Add signed relative-residual panels or facet by solute with color/shape for temperature and pressure. Label or highlight the worst folds. Put the descriptive interval in the caption, not the title. Export the point table with fit membership and condition identifiers.

---

## Figure 4 — frozen O→C/F prediction

**What works:** Units are corrected, C and F are separated, and variety markers are distinguishable.

**Problems:**

- the title states the conclusion (“transfers reasonably”) rather than describing the data;
- “≤1 pp geometry-sensitive” is not visible and is computed after rounding;
- no profile-wide predictive envelope is displayed;
- no flow-map uncertainty is shown;
- horizontal bands reveal systematic compression of condition response;
- one-to-one scatter again emphasizes group level more than within-group process sensitivity.

**Required redesign:** Use a neutral title. Add pointwise prediction bands generated from the near-optimal O profile and separate scenario bands for flow/geometry. Include signed percent residual by `(T,p)` and per-group metrics. Show the geometry/flow sensitivity in a separate panel or supplementary figure rather than in the title.

---

## Figure 5 — joint shared-fit residual by grind

**What works:** The heatmap quickly locates groups carrying larger joint-fit errors.

**Problems:**

- it shows only joint-fit MAPE, not the independent-fit reference or the difference that defines cost-of-sharing;
- integer annotations hide small but relevant differences;
- it can be mistaken for a predictive test;
- no signed residual pattern is shown;
- the title reports rounded macro metrics and “rate at boundary,” but boundary refers only to the grid.

**Required redesign:** Use paired panels for joint MAPE, independent MAPE, and `joint − independent`; or display the cost-of-sharing directly. Add signed residual summaries. Label it “in-sample shared-parameter compatibility.” Retain at least one decimal place and calculate from full precision.

---

## Figure 6 — fractions versus aggregated endpoints

**What works:** The key qualitative contrast is immediately visible, and the figure distinguishes empirical sampled aggregation from same-model exact-cup simulation.

**Problems:**

- exact-cup curves are seed 0 only, while the text reports 20-realization statistics;
- there are no uncertainty ribbons or best-rate distributions;
- three panels have different y-axis scales, exaggerating visual sharpness differences;
- “empirical + same-model simulation” in one plot can blur evidence levels;
- the external Waszkiewicz profile is absent despite being a prominent manuscript result;
- range ratios are domain-dependent and not shown with the rate-domain caveat.

**Required redesign:** Plot normalized objective increase or otherwise make scales comparable. Show median/quantile profiles over simulation noise realizations. Visually separate empirical in-sample and same-model simulation panels. Add the Waszkiewicz external-data profile as a separate figure/panel, with the one-cup flatness labeled algebraic for one scalar and one profiled level.

---

## 8. Required reruns and suggested acceptance tests

### 8.1 Corrected formal profile package

For every solute × variety at O grind:

- corrected one-dimensional MAPE profile;
- SSE profile;
- nuisance-level profiles for both objectives;
- dense/continuous optimization;
- multiple domains and grid densities;
- boundary-censored threshold intervals;
- Hessian sensitivity to step/coordinate scaling;
- source-data table.

**Pass condition:** The conclusion is based on profiles that remain broad under reasonable objective/domain/grid choices, not on a single condition number.

### 8.2 Prediction-identifiability package

For each near-optimal O-grind profile set:

- propagate all parameter pairs to C/F;
- plot pointwise and metric distributions;
- compare unconstrained profile, Table 7-constrained profile, and selected optimum;
- repeat under hydraulic/geometry scenarios.

**Pass condition:** Any claim of “stable along the manifold” is backed by an explicit envelope. If predictions vary substantially, revise the paper to distinguish point-transfer from prediction identifiability.

### 8.3 Observation/noise sensitivity package

- unweighted SSE;
- relative/log loss;
- uncertainty-weighted scenario(s);
- residual diagnostics;
- endpoint mass/density sensitivity;
- hydraulic-map scenarios.

**Pass condition:** Main qualitative conclusions survive, or the text states which assumptions control them.

### 8.4 Cross-validation uncertainty package

- direct table of nine condition macro-errors;
- transparent descriptive summaries;
- no coverage claim unless full resampling/refitting is justified;
- replicate-level analysis if data become available.

**Pass condition:** Figure, Methods, Results, and code use the same inferential label and target.

### 8.5 Exact-cup and external-trajectory package

- all noise-realization summaries and quantiles;
- model-discrepancy simulation;
- fixed report function;
- Waszkiewicz temperature/flow-floor/density/time sensitivity;
- full-precision metric calculations.

**Pass condition:** Figure 6 and the text refer to the same ensembles and evidence classes.

### 8.6 Reproducibility package

One command should produce:

- frozen full-precision result JSON/Parquet;
- manuscript tables;
- figure source-data CSV/Parquet;
- SVG/PDF plus PNG figures;
- environment and data manifest;
- checksums and commit/tag;
- a machine-readable claim-to-result map.

**Pass condition:** Clean-environment rerun and numeric regression test succeed before release.

---

## 9. Suggested replacement wording for key passages

### Abstract — transfer sentence

> Although the single-grind inventory and rate are weakly localized, one selected O-grind calibration predicts the held-out C/F observations with approximately 3–18% MAPE under the assumed endpoint and pressure–flow maps. Whether this predictive performance remains stable over the full near-optimal O-grind profile is evaluated separately [after A2-02] and should not be inferred from the parameter valley alone.

### Joint-fit sentence

> A shared pair fitted to all three grinds reconstructs the pooled observations with 6.4% macro-average MAPE, compared with 4.9% for separate per-grind fits. The approximately 1.5-percentage-point in-sample cost indicates compatibility with parameter sharing under the assumed maps; it is not a held-out prediction.

### Cross-validation uncertainty sentence

> Leave-one-condition-out prediction yielded a 6.5% pooled mean absolute percentage error across the nine O-grind conditions. Resampling the 54 final errors and, separately, the nine condition-level macro-errors gave descriptive intervals of [5.0, 8.2]% and [5.1, 8.3]%, respectively. Because the fitted folds share training data and fitting was not repeated inside the resampling, these intervals are not coverage-calibrated estimates of cross-validation uncertainty.

### Waszkiewicz sentence

> On the independent TDS trajectory, a target-level-profiled fraction objective showed a rate-dependent trough, whereas the corresponding single integrated scalar was exactly matchable at every rate by its one free level. The flat cup profile is therefore algebraic for this one-shot construction and does not imply that multi-cup endpoint designs are generally uninformative.

### Practical-confounding conclusion

> Under the tested model, log-rate domain, endpoint operator, flow assumptions, and error criteria, the single-grind cup data produce a broad inventory–rate profile. The data therefore do not support a unique mechanistic interpretation of the fitted pair without additional information such as an independent inventory measurement or time-resolved observations.

---

## 10. Minor and editorial comments

1. Use `5-CQA` consistently; Figure legends currently show `5CQA`.
2. Define O, C, and F at first use and give the physical grind/granulometry mapping.
3. Define `c_s0` units in the Methods, every table, and Figure 2.
4. Define whether MAPE macro-averages weight varieties, solutes, grinds, and conditions equally.
5. Replace “exact analytical” with “closed-form weighted-median solution” for the MAPE level and provide the derivation.
6. Avoid “model-free evidence” for a profile generated from model predictions; the profile is model- and observation-operator-dependent.
7. Replace “stronger than before” and revision-history commentary with direct scientific statements.
8. Avoid “textbook distinction” unless a suitable reference is cited; simply state the distinction.
9. Report absolute errors alongside MAPE where concentrations vary substantially.
10. Give the number of observations contributing to every table cell and metric.
11. Clarify whether the 66 Angeloni records include off-grid and all granulometries exactly as counted in each analysis subset.
12. State how missing/nonpositive analyte values are handled; MAPE requires positive observations.
13. Report solver convergence/tolerance and whether the linearity in inventory is numerically verified.
14. Document random seeds once in Methods and include them in result metadata.
15. Use “random-noise realizations” instead of “independent seeds.”
16. Move the literature-search protocol and novelty qualification to supplementary material, while retaining a concise Methods statement.
17. Replace code identifiers in prose with scientific descriptions; place function names in Code Availability or supplement.
18. Add a limitations paragraph distinguishing measurement uncertainty, model discrepancy, hydraulic mapping, geometry, and dataset shift.
19. Add a simple empirical baseline for cross-grind prediction to contextualize 3–18% MAPE.
20. Use neutral figure titles; conclusions belong in captions/text.

---

## 11. Submission-readiness checklist

### Scientific validity

- [ ] MAPE profile bug fixed and all dependent claims regenerated.
- [ ] Near-optimal profile propagated to held-out C/F or manifold-stability claim removed.
- [ ] Evidence taxonomy corrected.
- [ ] Joint fit described as in-sample compatibility.
- [ ] Cross-validation intervals relabeled or reimplemented.
- [ ] Grid/domain/finite-difference sensitivity completed.
- [ ] Boundary-censored profile intervals reported.
- [ ] Endpoint density/tolerance sensitivity completed.
- [ ] Flow-map uncertainty evaluated.
- [ ] Measurement/noise weighting sensitivity completed.
- [ ] Table 7 constraint quantified.
- [ ] Full precision retained before rounding.
- [ ] Exact-cup simulation ensemble shown and report command fixed.
- [ ] Waszkiewicz sensitivity expanded.

### Figures and tables

- [ ] Figure 1 evidence classes corrected and external panel added.
- [ ] Figure 2 colorbar, units, normalized objective, and profile panel added.
- [ ] Figure 3 residual/condition structure displayed.
- [ ] Figure 4 manifold and structural-uncertainty bands displayed.
- [ ] Figure 5 independent comparator/difference displayed.
- [ ] Figure 6 simulation uncertainty displayed; evidence classes separated.
- [ ] Vector/editable figure files produced.
- [ ] Figure source-data tables exported.
- [ ] Captions are self-contained and state sample sizes/objectives.

### Manuscript package

- [ ] Internal repository note and change-log prose removed.
- [ ] Complete equations and analysis methods added.
- [ ] Full reference list added and verified.
- [ ] Title page, keywords, highlights, declarations, and contributions added.
- [ ] Data and code availability statements added.
- [ ] Frozen release tag/archive DOI created.
- [ ] Supplement maps every robustness analysis and source-data file.
- [ ] One clean paper-build command reproduces all values.

---

## 12. Supporting reference material

The references below support the review’s source-design checks, terminology, profile-analysis recommendations, cross-validation caution, and submission/reproducibility recommendations.

### Espresso data and model lineage

1. **Schmieder, B. K. L., Pannusch, V. B., Vannieuwenhuyse, L., Briesen, H., & Minceva, M. (2023).** Influence of flow rate, particle size, and temperature on espresso extraction kinetics. *Foods, 12*(15), 2871. <https://doi.org/10.3390/foods12152871>  
   Relevance: primary source for ten consecutive fractions, the 15-setting central-composite design, three repetitions per setting and six at the center, and the use of achieved flow/temperature values in source response-surface analysis.

2. **Pannusch, V. B., et al. (2024).** Model-based kinetic espresso brewing control chart for representative taste components. *Journal of Food Engineering, 367*, 111887. <https://doi.org/10.1016/j.jfoodeng.2023.111887>  
   Relevance: model under review and its component-resolved extraction/calibration lineage.

3. **Angeloni, S., Giacomini, M., Maponi, P., Perticarini, A., Vittori, S., Cognigni, L., & Fioretti, L. (2023).** Computer percolation models for espresso coffee: state of the art, results and future perspectives. *Applied Sciences, 13*(4), 2688. <https://doi.org/10.3390/app13042688>  
   Relevance: transfer campaign, duplicate extractions, analyte variability, granulometry/pressure/temperature design, concentration outputs, hydraulic fits, and solid-inventory measurements.

4. **Waszkiewicz, M., et al. (2026).** Under pressure: poroelastic regulation of flow in espresso brewing. *Physics of Fluids, 38*, 063113. <https://doi.org/10.1063/5.0319611>  
   Relevance: independent time-resolved TDS/flow observation class used for external-data objective localization.

### Identifiability and profile analysis

5. **Raue, A., Kreutz, C., Maiwald, T., Bachmann, J., Schilling, M., Klingmüller, U., & Timmer, J. (2009).** Structural and practical identifiability analysis of partially observed dynamical models by exploiting the profile likelihood. *Bioinformatics, 25*(15), 1923–1929. <https://doi.org/10.1093/bioinformatics/btp358>  
   Relevance: profile-based diagnosis of practical non-identifiability and limitations of relying only on local covariance/curvature.

6. **Wieland, F.-G., Hauber, A. L., Rosenblatt, M., Tönsing, C., & Timmer, J. (2021).** On structural and practical identifiability. *Current Opinion in Systems Biology, 25*, 60–69. <https://doi.org/10.1016/j.coisb.2021.03.005>  
   Relevance: distinction between structural and practical identifiability and caution regarding local Fisher-information approaches.

7. **Gutenkunst, R. N., et al. (2007).** Universally sloppy parameter sensitivities in systems biology models. *PLoS Computational Biology, 3*(10), e189. <https://doi.org/10.1371/journal.pcbi.0030189>  
   Relevance: local sensitivity spectra/model-manifold context; also reinforces that “sloppiness,” scaling, and identifiability should not be conflated.

### Cross-validation uncertainty

8. **Bengio, Y., & Grandvalet, Y. (2004).** No unbiased estimator of the variance of K-fold cross-validation. *Journal of Machine Learning Research, 5*, 1089–1105. <https://www.jmlr.org/papers/v5/grandvalet04a.html>  
   Relevance: dependence among fold errors and the impossibility of a universal unbiased variance estimate based only on standard K-fold results.

9. **Nadeau, C., & Bengio, Y. (2003).** Inference for the generalization error. *Machine Learning, 52*, 239–281. <https://doi.org/10.1023/A:1024068626366>  
   Relevance: variability due to training-set choice and the danger of treating resampled errors as independent.

### Submission and reproducibility

10. **Journal of Food Engineering — Guide for Authors.** <https://www.sciencedirect.com/journal/journal-of-food-engineering/publish/guide-for-authors>  
    Relevance: current requirement for editable source files and conventional submission components; supports producing editable/vector figure assets and a complete manuscript package.

---

## 13. Bottom-line decision

**Major revision before submission.**

The updated draft has corrected many of the previous review’s most serious conceptual and provenance problems, and its scoped single-grind practical-confounding result is now a credible basis for a publishable case study. The manuscript is not yet submission-ready because one advertised objective cross-check is numerically malformed, the central manifold-wide prediction claim has not been tested, evidence classes remain conflated, uncertainty language exceeds the resampling procedure, and the build/figures do not yet support all headline statements.

The recommended revision should preserve the paper’s central distinction among endpoint fit, parameter identifiability, and predictive performance, while replacing unsupported generalizations with directly computed profile-wide prediction results. Completing actions A2-01 through A2-05 is essential; the P1 actions are needed for a rigorous Journal of Food Engineering submission.
