# Fifth Detailed Review of PAPER B2

## Manuscript reviewed

**File:** `docs/PAPER_B2_TEMPORAL_DRAFT.md`  
**Current title:** *One flow curve, many explanations: null-first inference for machine and porous-bed dynamics in espresso*  
**Repository:** <https://github.com/trbrewer/puckworks>  
**Pinned merged snapshot:** [`fc61c4670ec7bf801e40bb391aab16048b8da26b`](https://github.com/trbrewer/puckworks/tree/fc61c4670ec7bf801e40bb391aab16048b8da26b)  
**Paper B2 content commit within the merged PR:** [`f0d836c5b237adac9733d0e39bff69b532fdfcef`](https://github.com/trbrewer/puckworks/commit/f0d836c5b237adac9733d0e39bff69b532fdfcef)  
**Merged revision:** [PR #190](https://github.com/trbrewer/puckworks/pull/190)  
**Review date:** 28 July 2026  
**Recommendation:** **Major revision before external journal submission**

Line references in this report refer to the manuscript at the pinned merged snapshot. Numerical checks were performed against the committed processed per-brew deposit and the code at the same Paper B2 content revision.

---

## 1. Editorial decision and overall assessment

Paper B2 is now substantially stronger than the manuscript reviewed in rounds one through four. The revision has correctly resolved several material problems:

- the exact `12-8-6` / `12-8-6_alt` duplicate is now traced to the source archive and excluded from shot-level inference;
- the pressure-wise branch-change count is correctly defined as three adjacent transitions rather than `number of distinct winners minus one`;
- the main Methods and Results text now recognizes that the Foster model contains an advancing wetting front and therefore does include evolving bed saturation/path-length state;
- the 0.149 g s⁻¹ quantity is no longer presented as a noise floor;
- the fully held-out other-shot template is distinguished from the partly target-informed empirical `Φ(t)` branch;
- the comparator-sensitive interval-holdout result has been withdrawn from the paper’s headline claims;
- genuine individual-shot cross-pressure scores are now reported; and
- Figure 4’s spectral abscissa has been changed from an apparent physical period to Fourier-bin index, with an explicit warning that 80 s and 40 s are properties of the finite analysis window.

The manuscript’s central descriptive result remains numerically sound. On the declared, preprocessed nominal 9-bar mean trajectory over 15–95 s, the tested time-varying branches reconstruct the curve much more closely than the tested time-invariant branches. The independently checked RMSE ladder remains:

| Branch | RMSE (g s⁻¹) | Appropriate evidentiary reading |
|---|---:|---|
| Best in-window constant | 0.572856 | Strongest one-level in-sample static null |
| “Late-window” constant | 0.640589 | One-level in-sample subset fit; currently misclassified in the manuscript |
| Static poroelastic branch | 0.647696 | Same-campaign pressure-dependent but time-invariant reconstruction |
| Empirical `Φ(t)` | 0.115769 | Partly target-informed within-campaign temporal reconstruction |
| Same-trace cubic | 0.096396 | Four-parameter in-sample descriptive comparator |

That ladder supports a useful, publishable, but narrow conclusion: **time-varying predictions are needed relative to the specified time-invariant branches to reconstruct this processed mean trajectory; the trajectory alone does not identify which physical mechanism supplies the time dependence.**

The remaining work is no longer a fundamental conceptual rewrite. It is, however, still **major revision** because several current statements misclassify data access, experimental units, pressure quantities, or physical state. Those are not merely stylistic defects. They determine what kind of evidence the reader believes is being presented.

The most important outstanding findings are:

1. **The Foster correction has regressed on reader-visible surfaces.** The main Methods text is careful, but Table 4, the conclusion, and Figure 5 still say “without bed evolution,” “without bed,” and “no bed-state signature.” Sharp-front infiltration through an initially dry porous bed is evolving bed saturation and hydraulic-path state.
2. **The “late-window constant” is not fitted outside the scoring interval.** The producer uses 85–95 s because it defines the late interval as `hi - 10` to `hi`, while the scored interval is 15–95 s. Table 1’s “0 on scoring interval” and the provenance graph’s “tail of the same shot, outside the scored window” are therefore false.
3. **The cross-pressure mean-curve summaries still mix 57 source records with 56 physical brews.** The manuscript says all four rows of Table 3c are over 56 shots, but the first two rows retain the source’s seven-record 13-bar mean and the second row weights that pressure by seven. It is a source-record-count-weighted summary, not a physical-shot-count-weighted summary.
4. **LOPO-EC terminology remains inconsistent outside the main prose.** Figure 3’s legend, alt text, the result-builder claim label, and supporting code continue to call an equilibrium-calibration deletion “held out,” despite retaining temporal inputs.
5. **The committed reproducibility record is still stale and dirty.** At the reviewed merge commit, the manifest and result bundle still identify `352dacd…`, record `git_dirty=true`, have no timestamp, and set `release_fresh=false`.
6. **The manuscript overstates what value verification guarantees.** A value-matching bundle cannot ensure that a figure uses the correct estimand, access class, pressure node, physical label, or current render. The unresolved Figure 5 and late-window labels demonstrate the limitation directly.
7. **The manuscript structure is internally broken.** Section 5.4 appears before 5.3a–5.3c; Table 3c precedes Table 3b; Figure 4 points to the wrong section; and the text refers to a nonexistent “reserved-material note.”

Several further scientific issues should also be addressed: the cubic is still described as a “bound” and “floor”; the exact sign-flip language is broader than the actual test; the residual-spectrum analysis remains more prominent than its untapered 80-point design supports; the pressure-domain panel calls a 100-second endpoint pressure a general delivered mean; uncertainty in the equilibrium calibration is not reported alongside deletion stability; and the RC-3b donor branch is under-specified relative to the importance assigned to its pressure-wise wins.

**Bottom line:** the paper has a defensible core and is closer to submission than at any earlier review. A focused integration, estimand, and frozen-release pass should make it substantially more robust. It is not yet ready to send to a journal in its present form.

---

## 2. Scope and method of this review

I reviewed the following repository objects at the pinned merged snapshot:

- [current Paper B2 manuscript](https://github.com/trbrewer/puckworks/blob/fc61c4670ec7bf801e40bb391aab16048b8da26b/docs/PAPER_B2_TEMPORAL_DRAFT.md);
- [temporal-ladder producer in `harness.py`](https://github.com/trbrewer/puckworks/blob/fc61c4670ec7bf801e40bb391aab16048b8da26b/puckworks/harness.py);
- [`waszkiewicz_shot_level.py`](https://github.com/trbrewer/puckworks/blob/fc61c4670ec7bf801e40bb391aab16048b8da26b/puckworks/analysis/waszkiewicz_shot_level.py);
- [`waszkiewicz_cross_pressure.py`](https://github.com/trbrewer/puckworks/blob/fc61c4670ec7bf801e40bb391aab16048b8da26b/puckworks/analysis/waszkiewicz_cross_pressure.py);
- [`figures_paper_b2.py`](https://github.com/trbrewer/puckworks/blob/fc61c4670ec7bf801e40bb391aab16048b8da26b/puckworks/figures_paper_b2.py);
- [Paper B2 build/claim verifier](https://github.com/trbrewer/puckworks/blob/fc61c4670ec7bf801e40bb391aab16048b8da26b/puckworks/paper_b2/build.py);
- [semantic audit](https://github.com/trbrewer/puckworks/blob/fc61c4670ec7bf801e40bb391aab16048b8da26b/tests/test_paper_b2_semantic_audit.py);
- [result bundle](https://github.com/trbrewer/puckworks/blob/fc61c4670ec7bf801e40bb391aab16048b8da26b/docs/figures/paper_b_results.json);
- [reproducibility manifest](https://github.com/trbrewer/puckworks/blob/fc61c4670ec7bf801e40bb391aab16048b8da26b/docs/reproducibility/paper_b_manifest.json);
- [figure alt text](https://github.com/trbrewer/puckworks/blob/fc61c4670ec7bf801e40bb391aab16048b8da26b/docs/figures/paper_b2/ALT_TEXT.md);
- [Waszkiewicz data provenance](https://github.com/trbrewer/puckworks/blob/fc61c4670ec7bf801e40bb391aab16048b8da26b/puckworks/data/waszkiewicz2025/PROVENANCE.md);
- the committed 57,000-row processed per-brew trace deposit; and
- the four earlier detailed Paper B2 reviews and their numerical audits.

I independently checked:

- record and distinct-trajectory counts by nominal pressure;
- exact equality of the duplicate processed trajectories;
- the 15–95 s scoring mask and 85–95 s “late” mask;
- the best-constant and late-constant levels and RMSEs;
- the 90–100 s alternative late-level sensitivity;
- leave-in and leave-one-shot-out other-four distances;
- full-resolution and 1 s-grid between-shot standard-deviation summaries;
- nominal-9-bar basket-pressure means over the full record, scored interval, and final sample;
- the effect of using six rather than seven 13-bar units in the pressure-level weighting; and
- source-manifest, result-bundle, manuscript, figure, and code terminology consistency.

I did not independently rerun all 2,117 repository tests, reproduce the entire multi-minute Paper B result bundle from a clean checkout, or re-fit every source model from its original archive. PR #190 reports that the full suite passed and that 156 Paper B2 claims verified, but that report is treated here as repository-reported evidence rather than as an independently rerun result. This distinction matters because the current bundle and manifest are explicitly not release-fresh.

---

## 3. Resolution audit against the fourth review

| Fourth-review issue | Current status | Fifth-review assessment |
|---|---|---|
| Exact duplicate treated as two shots | Source archive traced; alias declared; shot-level functions exclude it | **Resolved for shot-level scoring**; mean-curve weighting remains hybrid and mislabeled |
| Rank-transition count used `len(set)-1` | Corrected to adjacent changes | **Resolved** |
| Foster described as machine-only / no evolving bed | Main Methods and main Result corrected | **Partly resolved; regressed in Table 4, Figure 5, and conclusion** |
| Figure 4 used physical-period language | Panel now uses Fourier-bin index; caveat added | **Substantially resolved**, though still over-prominent and cross-reference is wrong |
| Cross-pressure random-shot estimand absent | Genuine 56-shot and pooled estimands added | **Resolved numerically; population wording and hybrid table statement still need correction** |
| Dirty/stale release | PR explicitly leaves frozen-release manifest open | **Unresolved** |
| Verification claimed semantic certainty | Main figure preamble still says a figure “cannot disagree” with a verified number | **Unresolved** |
| Inconsistent stale terminology | Semantic audit strengthened and mutation-tested | **Improved, but still has false negatives and omits `harness.py`** |
| Cubic described as bound/floor | Main table calls it comparator | **Unresolved in Methods and Results prose** |
| Pressure-specific ranking hidden | Full pressure table and rank transitions now shown | **Resolved descriptively**; uncertainty remains absent |
| 57 source records versus 56 brews | Provenance now explains duplicate | **Resolved in provenance; not consistently reflected in weighted mean-curve estimand** |
| Source campaign says 60 brews but deposit has fewer | Provenance says source-excluded brews are not included | **Improved**, but manuscript should state the exclusion path and unknown selection implications more clearly |

The revision therefore closes the two most concrete round-four code/data defects. The principal remaining problem is synchronization: the main explanatory prose, tables, figure code, figure alt text, producer metadata, and frozen evidence package still do not all describe the same access classes and physical meanings.

---

## 4. Priority revision matrix

### 4.1 P0 — submission blockers

| ID | Required action | Why it is blocking | Minimum acceptance criterion |
|---|---|---|---|
| **P0.1** | Correct Foster/machine–wetting language on every surface | Current Table 4, conclusion, and Figure 5 deny bed evolution although wetting state and path length evolve | Repository-wide search finds no unqualified “without bed evolution,” “without bed,” “no bed-state signature,” or machine-only label for this branch |
| **P0.2** | Reclassify the 85–95 s late constant as an in-sample subset fit | Its fitted interval is wholly inside the scored 15–95 s interval; Table 1 and access graph are factually wrong | Manuscript, producer metadata, dependency graph, result bundle, and captions state the exact 85–95 s access and one target-fitted level |
| **P0.3** | Separate record-weighted mean-curve and physical-shot summaries | Table 3c says all rows use 56 shots, but the first two preserve a seven-record 13-bar source mean and one weights by seven | Either recompute mean curves/weights from six physical brews or rename the summary “source-record-count-weighted” and state its 57-record hybrid construction numerically |
| **P0.4** | Enforce LOPO-EC terminology repository-wide | Figure legend, alt text, build labels, and supporting comments still say “held out” despite retained temporal inputs | Every reader-visible and machine-readable label says “equilibrium-calibration point omitted” or “LOPO-EC”; bare “held-out pressure” is absent except in explicit retractions |
| **P0.5** | Produce a clean, commit-matched Paper B2 release | Current bundle/manifest identify `352dacd…`, dirty tree, null timestamp, and `release_fresh=false` | Clean checkout; bundle commit equals manuscript commit; `git_dirty=false`; timestamp and hashes present; strict release verification passes; archive DOI/tag recorded |
| **P0.6** | Narrow the artifact-verification claim and correct the command | Numeric claim matching cannot certify estimand, semantics, units, node identity, or freshness; `paper_b.build.verify` is the wrong module name | Manuscript says verification reduces numeric transcription error and separately requires semantic/freshness checks; command is `python -m puckworks.paper_b2.build verify` or `release` |
| **P0.7** | Repair section/table order and cross-references | The present 5.4 → 5.3a → 5.3b → 5.3c order is not submission-quality and produces wrong references | Conventional sequential numbering; Tables 3a/3b/3c appear in order; Figure 4 points to the actual spectral-caveat section; nonexistent reserved note removed or supplied |

### 4.2 P1 — major scientific and methodological revisions

| ID | Required action | Purpose |
|---|---|---|
| **P1.1** | Remove “bound” and “floor” language from the cubic | A single degree-three polynomial does not bound smooth temporal flexibility or attainable reconstruction error |
| **P1.2** | State the exact assumptions and scope of the sign-flip test | “No paired randomization test can reach 0.05” is broader than the enumerated two-sided sign-flip test under sign symmetry |
| **P1.3** | Demote or strengthen the residual-spectrum result | An untapered 80-point periodogram after alignment/smoothing is a descriptive low-bin concentration diagnostic, not a robust physical timescale result |
| **P1.4** | Relabel the 8.71 bar quantity as an endpoint mean | The producer uses the final 100 s point, not the mean basket pressure over the scored interval or full shot |
| **P1.5** | Report calibration uncertainty alongside deletion stability | Source calibration reports large `std` fields; small leave-one-pressure deletion drift is not parameter precision |
| **P1.6** | Fully specify RC-3b and its pressure-node mapping | RC-3b materially determines low- and high-pressure “wins” but is described only as a donor extraction trajectory |
| **P1.7** | Add pressure-wise shot-level uncertainty or explicitly keep ranks descriptive | Some pressure-wise margins are small and sample sizes range from three to ten brews |
| **P1.8** | Scope the other-shot template conclusion to this five-shot, same-condition design | “No new-shot predictive advantage” is too universal for one rig, one pressure, five shots, and asymmetric access |
| **P1.9** | Make the raw other-four mean the primary held-out empirical template | It is simpler, fully empirical, and differs negligibly from the fitted spline; the spline can remain a sensitivity |
| **P1.10** | Tighten the proposed experimental decision logic | Reversal asymmetry or an outlet deposit does not by itself uniquely establish fines migration without apparatus and inert-bed controls |
| **P1.11** | Clarify the source campaign/exclusion accounting | Readers need a one-row-per-brew inclusion/exclusion/alias inventory and an explicit selection-bias limitation |
| **P1.12** | Label the two between-shot SD values by grid | 0.154 is full-resolution; approximately 0.153 is the 1 s diagnostic grid |
| **P1.13** | Replace population-style “randomly drawn shot” language | The data describe a finite observed campaign, not a probability sample from a defined shot population |
| **P1.14** | Reduce the manuscript’s ledger-like length and move implementation detail to SI | The current draft is approximately 12,159 words with a 437-word abstract and approximately 4,386-word Results section |

### 4.3 P2 — editorial and presentation corrections

- Update the working-draft date from 15 July 2026.
- Complete author names, affiliations, corresponding author, CRediT roles, funding, competing interests, and acknowledgments.
- Correct the malformed cubic equation token currently rendered as `Q_{ ext{cub}}` with a tab/missing backslash; it should be `Q_{\text{cub}}`.
- Use one consistent name for the first branch: preferably **machine–wetting / pump–headspace–sharp-front infiltration**.
- Change “model-valid pressure range” to **evaluated pressure range** or **data-support range** unless formal model validity has actually been established.
- Correct Figure 3’s legend and alt text.
- Reorder Tables 3a, 3b, and 3c.
- Remove internal review-history prose from the journal article where it no longer helps the scientific argument; retain it in a provenance record.
- Expand methodological references for smoothing, penalized splines/GCV, exact paired sign tests, model discrimination, and inverse-problem identifiability.
- Convert the supplementary-material “plan” into an actual supplement before submission.

---

## 5. Independent numerical and data audit

### 5.1 Primary 9-bar ladder

The central values reproduce to full practical precision from the committed preprocessed mean trace and declared window:

| Quantity | Independently checked value |
|---|---:|
| Number of scored points | 800 |
| Actual scored grid | 15.015–94.995 s |
| Best-constant level | 1.58411054 g s⁻¹ |
| Best-constant RMSE | 0.57285551 g s⁻¹ |
| 85–95 s level used by `rung1b_longrun_const` | 1.87079986 g s⁻¹ |
| 85–95 s late-constant RMSE | 0.64058895 g s⁻¹ |
| Static poroelastic RMSE | 0.64769605 g s⁻¹ |
| Empirical `Φ(t)` RMSE | 0.11576939 g s⁻¹ |
| Same-trace cubic RMSE | 0.09639640 g s⁻¹ |

The main error separation is real for this observation operator. The new access-class finding changes the interpretation of the late constant, not the ordering or the paper’s central conclusion.

### 5.2 The “late-window” branch is in-sample

The producer defines:

```python
lo, hi = window                 # default (15.0, 95.0)
sel = (t >= lo) & (t <= hi)     # scored interval
late = (t >= hi - 10.0) & (t <= hi)
```

Thus the calibration interval is 85–95 s, entirely contained inside the 15–95 s scoring interval. Consequences:

- it has **one coefficient fitted to the scored target**, not zero;
- its access level is **direct target**, not “same shot outside the scored window”;
- it is not a held-out long-run level; and
- “near the end of the source trace” is imprecise because the source trace continues to 100 s.

For context, an actual 90–100 s source-tail mean is 1.86335582 g s⁻¹ and gives a 15–95 s RMSE of 0.63729221 g s⁻¹. This small sensitivity does not affect the scientific conclusion. The required correction is semantic and evidentiary, not numerical.

### 5.3 Shot-level repeatability quantities

For the five nominal-9-bar brews:

| Quantity | Value (g s⁻¹) | Meaning |
|---|---:|---|
| Mean shot-to-full-mean RMSE | 0.14915119 | Leave-in descriptive dispersion; optimistic by construction |
| Mean shot-to-other-four-mean RMSE | 0.18643899 | Honest other-shot empirical-template error |
| Ratio | 1.25 exactly | Algebraic result for five shots |
| Mean pointwise sample SD, full scored grid | 0.15395022 | Full approximately 10 Hz processed grid |
| Mean pointwise sample SD, 1 s decimated grid | 0.15290766 | Grid used for the residual diagnostics |

The revised manuscript correctly rejects a noise-floor interpretation. It should now label the 0.154 and 0.153 versions explicitly by grid wherever each appears.

### 5.4 Duplicate resolution and the remaining hybrid estimand

The deposit contains 57 processed trace records but 56 physical brews. The provenance record now establishes that `12-8-6.txt` is an exact prefix of `12-8-6_alt.txt`, whose extra samples are scale-clearing data after the truncation point. The decision to preserve both records when reproducing the source’s published 13-bar aggregate, while excluding the alias when the shot is the experimental unit, is transparent and defensible.

It creates two different data objects:

1. **Source-reproduced pressure-level mean curves:** 57 record contributions, including seven 13-bar records representing six brews.
2. **Shot-level estimands:** 56 physical brews, with six 13-bar units.

Table 3c currently says “All values … over 56 distinct shots,” which is false for the first two rows. The equal-pressure mean uses a source-published 13-bar mean that includes the alias, and the “shot-count-weighted” row weights that mean by seven.

Using the manuscript’s pressure-level RMSEs gives:

| Mean-curve weighting | Static | `Φ(t)` | RC-3b |
|---|---:|---:|---:|
| Current 57-record weights | 0.5094 | 0.3431 | 0.5300 |
| Six-brew weight at 13 bar | 0.5041 | 0.3429 | 0.5365 |

The ordering remains unchanged, but the label and estimand do. The paper should either:

- retain the exact source-reproduction object and call row 2 **source-record-count-weighted mean of source mean-curve RMSEs**, or
- construct a six-brew 13-bar mean and use physical-shot weights, reporting the source-reproduction version as a sensitivity.

### 5.5 Cross-pressure scores and rank changes

The current pressure-level mean-curve table is internally consistent:

| Nominal pressure (bar) | Static | `Φ(t)` | RC-3b | Lowest |
|---:|---:|---:|---:|---|
| 1.0 | 0.431 | 0.374 | 0.159 | RC-3b |
| 2.0 | 0.649 | 0.573 | 0.303 | RC-3b |
| 3.5 | 0.306 | 0.418 | 0.692 | Static |
| 4.0 | 0.246 | 0.374 | 0.785 | Static |
| 5.0 | 0.402 | 0.456 | 0.879 | Static |
| 6.0 | 0.453 | 0.502 | 0.912 | Static |
| 7.0 | 0.551 | 0.222 | 0.628 | `Φ(t)` |
| 8.0 | 0.575 | 0.118 | 0.448 | `Φ(t)` |
| 9.0 | 0.648 | 0.116 | 0.392 | `Φ(t)` |
| 11.0 | 0.693 | 0.173 | 0.241 | `Φ(t)` |
| 13.0 | 0.809 | 0.354 | 0.169 | RC-3b |

The winner sequence changes three times, and the revised code now counts those adjacent transitions correctly. These are descriptive rankings. At 5 and 6 bar, the margins between static and `Φ(t)` are only about 0.054 and 0.049 g s⁻¹, while pressure-specific sample sizes are small. A journal reader should not interpret the visual sequence as evidence for sharp pressure regimes without paired shot-level uncertainty or a prespecified pressure-interaction model.

### 5.6 Basket-pressure quantity at nominal 9 bar

The current pressure-domain producer uses one row per pressure from the `endpoint_100s` equilibrium window. It therefore reports the mean of the five **final basket-pressure samples**, not a time average over the scored interval.

For nominal 9 bar:

| Basket-pressure summary | Mean (bar) |
|---|---:|
| Full 0–100 s processed records | 8.76791 |
| Primary 15–95 s scored interval | 8.73697 |
| 85–95 s interval | 8.70976 |
| Final sample at approximately 100 s | 8.71692 |

The manuscript’s 8.71 bar number is therefore reasonable as a rounded endpoint mean, but the sentence “the nominal 9 bar condition delivered a mean 8.71 bar” is ambiguous and usually reads as a time- or shot-average. Replace it with **“the mean endpoint basket pressure at approximately 100 s was 8.717 bar.”** If the intended comparison is the scored temporal analysis, use the 15–95 s average or, better, the full recorded pressure history already used in the robustness check.

### 5.7 Calibration uncertainty versus deletion stability

The committed static calibration table reports:

| Parameter | Estimate | Repository `std` field |
|---|---:|---:|
| `P_c` | 12.39155 bar | 2.97582 bar |
| `Q_c` | 1.89699 g s⁻¹ | 0.14713 g s⁻¹ |

The paper emphasizes that omitting one pressure calibration point at a time changes the fitted quantities by no more than approximately 2.8%. That is a useful deletion-stability result, but it is not equivalent to parameter precision. The reported `P_c` spread is large relative to the tested range, and only one nominal pressure reaches/exceeds the point estimate. The manuscript should report both types of information and avoid allowing a narrow deletion range to imply that `P_c` is precisely known.

### 5.8 Reproducibility-state audit

At the reviewed merged snapshot, the committed manifest records:

```text
source_commit:        352dacd51015d95a3b5a5b3e1a8fb331419d78b0
git_dirty:            true
timestamp_utc:        null
bundle_source_commit: 352dacd51015d95a3b5a5b3e1a8fb331419d78b0
release_fresh:        false
```

The result bundle also identifies `352dacd…` and `git_dirty=true`. The paper itself correctly says a clean release is required before submission, and PR #190 explicitly lists the frozen Paper B2 manifest as still open. Therefore the current package is suitable for development review but not for archival citation or journal submission.

---
## 6. Detailed major comments

### 6.1 The Foster branch is still described inconsistently as having no bed evolution

**Finding.** Section 2.1 and the abstract now make the correct distinction: the Foster branch includes an advancing wetting front, changing wetted fraction, and changing hydraulic path length, while excluding extraction-driven changes in the saturated-bed constitutive law. That correction has not propagated to all reader-visible surfaces. Table 4 says the branch can generate dip/recovery “without bed evolution” and predicts “No bed-state signature”; the conclusion again says “without bed evolution”; and the Figure 5 producer uses shortened labels such as “without bed” and “no signature.”

**Why it matters.** Wetting and saturation are internal porous-bed state variables. An advancing front in an initially dry bed is a genuine form of bed-state evolution even if intrinsic permeability, particle size, fines distribution, and solid skeleton are held fixed. Calling the branch “machine-only” or “without bed evolution” would invite a reviewer to reject the physical taxonomy, and it obscures the paper’s strongest point: the same observable can be generated by *machine–wetting dynamics* without the extraction-driven material changes often inferred from it.

**Required revision.** Use one precise formulation throughout:

> The pump–headspace–sharp-front-infiltration branch generates a dip-and-recovery trajectory without extraction-driven evolution of saturated-bed constitutive properties. Its wetting front, saturated path length, and phase occupancy still evolve.

Rename the Table 4 row **“Machine–wetting / pump–headspace–infiltration”**. Replace its depth-resolved prediction with something such as **“No extraction-driven solid-state signature is required; a wetting/saturation profile may remain.”** In Figure 5, avoid compressed labels that drop the qualification.

**Acceptance criterion.** A repository-wide search across manuscript, generated captions, alt text, figure source, result metadata, and tests finds no unqualified `without bed evolution`, `without bed`, `no bed-state signature`, or `machine-only` description of this branch. Expand the semantic guard so these exact regressions fail a test.

---

### 6.2 The late-window constant is an in-sample branch, not a zero-access sensitivity

**Finding.** The primary score uses 15–95 s. The producer constructs the late interval as the final ten seconds ending at the scoring upper bound, i.e. 85–95 s. The fitted level therefore uses direct target values entirely inside the interval on which RMSE is calculated. Table 1 nevertheless says “0 on scoring interval,” and the provenance graph describes the level as drawn from the tail of the same shot “outside the scored window.”

**Why it matters.** This changes the branch’s access class and effective fitted parameter count. It is not merely a constant imported from an independent late-time equilibrium measurement. It is a one-parameter, in-sample subset fit. The current label makes the ladder appear more cleanly separated by target access than it is.

**Required revision.** Choose one of two defensible options:

1. **Retain the current calculation and relabel it.** State explicitly that one constant level is estimated from target observations at 85–95 s and scored over 15–95 s. In Table 1, use `1 level fitted on an in-window subset`; in the dependency graph, classify it as `direct_target`; and in captions call it an **85–95 s subset-fit constant**.
2. **Redesign it as an out-of-score sensitivity.** Fit the level on 95–100 s and score only 15–95 s. This would make access outside the scored interval true, although it would still be same-shot information and the available tail is only about five seconds, not ten. If 90–100 s is used, the scored interval must end before 90 s to avoid overlap.

The first option is cleaner because it preserves the published numerical ladder and makes its meaning honest.

**Acceptance criterion.** The code, result bundle, Table 1, access hierarchy, figure annotations, caption, and methods all state the exact fitting interval. No artifact claims zero target access or an interval outside 15–95 s for the existing 85–95 s calculation.

---

### 6.3 Table 3c mixes a 57-record mean-curve object with 56 physical brews

**Finding.** The duplicate alias is now excluded from the genuine individual-shot summaries, giving 56 physical brews. However, the committed pressure-level mean curve at 13 bar was originally formed from seven source records, two of which are identical aliases of one brew. The first Table 3c row averages those already-deposited pressure-level means, while the second weights pressure-level scores by the source record counts, including a weight of seven at 13 bar. The table introduction says that all four rows summarize 56 shots.

The numerical sensitivity is small but nonzero. Using the current 57-record weights gives approximately 0.5094, 0.3431, and 0.5300 g s⁻¹ for static, `Φ(t)`, and RC-3b. Treating 13 bar as six physical brews changes these to approximately 0.5041, 0.3429, and 0.5365 g s⁻¹.

**Why it matters.** The problem is not the size of the numerical change; it is the estimand. A pressure-level curve formed from seven source records is not the mean of six independent physical brews, and a seven-unit weight is not a physical-shot weight. The paper’s emphasis on experimental units makes this inconsistency especially visible.

**Required revision.** Preferably regenerate every pressure-level mean from the six unique 13-bar brews, regenerate the pressure-level scores, and then use 56 physical-shot counts consistently. If preserving the deposited source mean is important for exact source fidelity, label the first two rows explicitly as:

- **equal-pressure mean of deposited source mean-curves**; and
- **source-record-count-weighted mean of deposited mean-curve RMSEs (57 records; 56 physical brews)**.

Do not call either the expected error for a randomly selected shot. Retain the genuine mean individual-shot and pooled pointwise rows as the two shot-level estimands.

**Acceptance criterion.** Table 3c, its producer metadata, and the prose agree on 56 versus 57, on whether the duplicate is present in each row, and on whether the unit is a pressure, source record, physical brew, or record×time observation.

---

### 6.4 LOPO-EC is an equilibrium-calibration deletion, not a held-out temporal prediction

**Finding.** The main prose has improved by using **LOPO-EC** and explaining that only one equilibrium pressure–flow calibration point is omitted. Elsewhere, Figure 3’s generated legend and alt text still say “leave-one-pressure-out (held out)” or “held-out errors,” the claim builder uses a label equivalent to “LOPO held-out `Φ`,” and supporting comments continue to imply that a pressure condition has been withheld from the whole dynamic branch.

**Why it matters.** At an omitted pressure, the analysis retains the same campaign, rig, temporal closure, 9-bar dissolved-mass trajectory, donor assumptions, and—depending on the branch—other target-proximal inputs. The exercise measures sensitivity to deletion from the *equilibrium calibration*. It is useful, but it is not a fully held-out pressure prediction of the temporal model.

**Required revision.** Adopt a single term everywhere: **equilibrium-calibration leave-one-pressure-out (LOPO-EC)**. In compact legends use **“equilibrium point omitted”**. Replace “held-out errors” with **“errors after omitting that pressure from the equilibrium fit.”** Reserve “held out” without a qualifier for the other-four-shot empirical template, where the scored shot is excluded from the template.

**Acceptance criterion.** Figure 3 legend, alt text, captions, result keys or display names, claim registry, comments used to generate documentation, and manuscript all use the same restricted meaning. A semantic test should reject bare `held-out pressure` and `LOPO held-out` labels unless the surrounding text explicitly says only the equilibrium calibration point was omitted.

---

### 6.5 A clean, Paper-B2-specific evidence release remains a prerequisite

**Finding.** The manuscript is now merged at `fc61c467…`, but the committed manifest and result bundle still identify `352dacd…`, record a dirty tree, omit a UTC timestamp, and set `release_fresh=false`. PR #190 itself correctly leaves the frozen release as an open action.

**Why it matters.** A paper that makes artifact-backed claims should permit a reviewer to identify the exact manuscript, code, data, generated figures, and numerical claims that belong together. Passing claim checks against a stale, dirty bundle is a development-state property, not an archival release.

**Required revision.** From a clean checkout of the final manuscript commit:

1. regenerate the full Paper B2 bundle and all figures;
2. run strict verification and semantic tests;
3. record the source commit, clean-tree state, timestamp, Python/package environment, data hashes, figure hashes, source-data CSV hashes, and command line;
4. ensure the manifest’s manuscript and bundle commit identifiers match;
5. archive the release using a stable tag and preferably a DOI-bearing service; and
6. cite that immutable release from the paper.

A Paper-B2-specific manifest is preferable to a broad Paper B manifest that includes unrelated analyses, because it makes the article’s evidence surface auditable without ambiguity.

**Acceptance criterion.** `git_dirty=false`; `release_fresh=true`; bundle commit equals manuscript commit; all hashes resolve; no untracked generated artifacts are needed; strict `python -m puckworks.paper_b2.build release` succeeds from a clean checkout; and the tagged archive reproduces the submitted figures and tables.

---

### 6.6 Value verification cannot guarantee semantic agreement

**Finding.** The Figures preamble says that every figure is generated from the same verified bundle “so a figure cannot disagree with a verified number.” It also names `paper_b.build.verify`, whereas the implemented command surface is under `puckworks.paper_b2.build`.

**Why it matters.** Numeric verification can catch transcription or stale-value mismatches for registered fields. It cannot prove that a panel uses the right estimand, that “held out” is an accurate access label, that the plotted pressure is at the intended node or time summary, that a physical category is correct, or that the render reflects current source. The current Foster, late-window, LOPO, and endpoint-pressure issues are concrete examples of semantically wrong labels coexisting with numerically correct values.

**Required revision.** Replace the absolute claim with:

> Figures are generated from the registered result bundle, and automated checks verify selected numeric values against that bundle. Separate semantic, provenance, access-class, unit, and release-freshness audits are required because numeric agreement alone does not establish that a quantity is correctly interpreted.

Correct the documented commands to `python -m puckworks.paper_b2.build verify` and, for the frozen package, `python -m puckworks.paper_b2.build release`.

**Acceptance criterion.** No text says a verified number makes semantic disagreement impossible. The documented command runs from a clean checkout and matches the package/module actually shipped.

---

### 6.7 Section, table, and figure cross-references need a complete structural pass

**Finding.** The Results sequence currently places §5.4 before §§5.3a–5.3c. Table 3c precedes Table 3b. Figure 4’s caption points to §5.4 for the withdrawn period interpretation, although the relevant residual discussion is elsewhere. The text also sends the reader to a “reserved-material note” that does not exist as a named note or cross-reference.

**Why it matters.** Broken numbering is an editorial defect, but here it also obscures the evidence hierarchy. The reader encounters diagnostics, cross-pressure estimands, pressure nodes, and access provenance in a non-logical order.

**Required revision.** Rebuild the Results in a conventional sequence, for example:

- 5.1 Primary 9-bar reconstruction ladder;
- 5.2 Residual structure and fixed-loss sensitivity;
- 5.3 Shot-level paired results and held-out other-shot template;
- 5.4 Cross-pressure heterogeneity and estimands;
- 5.5 Pressure nodes and calibration domain;
- 5.6 Access/provenance hierarchy; and
- 5.7 Mechanistic sign constraints and withdrawn analyses.

Number Tables 3a–3c in order or replace the lettered sequence with Tables 3–5. Update all internal references automatically if the target journal format permits.

**Acceptance criterion.** Every section and table appears in numeric order; every `§`, figure, table, supplement, and note reference resolves to an existing object; and an automated link/cross-reference check returns no orphaned target.

---

### 6.8 The cubic is a comparator, not a bound, floor, or envelope of temporal flexibility

**Finding.** The manuscript correctly says the cubic is not a lower bound, but in the same paragraph says its purpose is “to bound what smooth temporal flexibility can achieve” and asks whether the mechanistic branch improves on “this floor.” Similar language survives elsewhere.

**Why it matters.** A degree-three polynomial is one four-parameter function class. It does not bound the performance of splines, Gaussian processes, monotone functions, state-space models, higher-order polynomials, or even a differently scaled cubic. Its in-sample error is neither a universal attainable minimum nor a principled flexibility ceiling.

**Required revision.** Describe it only as a **four-parameter same-trace cubic comparator**. Its valid role is to demonstrate that a simple non-mechanistic time function can achieve similar in-sample reconstruction. Delete `bound`, `floor`, `ceiling`, `lower bound`, and any statement that it represents what “any smooth function” can achieve.

A suitable replacement is:

> The cubic is included as one low-dimensional, non-mechanistic temporal comparator. Its similar same-trace RMSE shows that reconstruction quality is not unique to the named closure; it does not bound the performance of other temporal function classes.

**Acceptance criterion.** The manuscript, figures, result labels, and code comments consistently use `comparator` and make no extremal claim for the cubic.

---

### 6.9 The exact sign-flip statement is broader than the implemented test

**Finding.** The paper correctly enumerates all 32 sign assignments for five nonzero paired differences and obtains a two-sided value of 0.0625. It then says that “no paired randomization test on this design” can reach 0.05, however large the effect.

**Why it matters.** The minimum 2/32 result applies to the specific two-sided sign-flip test under the sign-symmetry null and the adopted treatment of the observed statistic. It is not a theorem covering every conceivable paired randomization, permutation, rank, parametric, Bayesian, or one-sided procedure. The current wording overgeneralizes a valuable but specific discreteness result.

**Required revision.** State:

> For the exact two-sided sign-flip test used here, with five nonzero paired differences and a sign-symmetry null, the smallest attainable p-value is 2/32 = 0.0625.

Also state the chosen statistic and treatment of ties/zero differences in Methods or supplement. Continue emphasizing effect sizes and directional consistency.

**Acceptance criterion.** The scope is tied explicitly to the implemented two-sided sign-flip test and its assumptions; no universal claim is made about all paired randomization tests.

---

### 6.10 The residual-spectrum panel remains a weak basis for physical interpretation

**Finding.** The revision commendably changes the horizontal axis to Fourier-bin index and explicitly says that 80 s and 40 s are properties of the 80-point window. Nevertheless, Figure 4 remains a full headline figure, and the text interprets more than 95% of power in the slowest quarter as coherent low-frequency lack of fit.

**Why it matters.** The diagnostic uses a short, approximately 80-point, 1 s-decimated, aligned, differentiated, and approximately 3 s-smoothed mean trajectory. An untapered periodogram of a residual with trend or endpoint mismatch naturally concentrates energy in the first bins because of spectral leakage. The first two nonzero bins are not independently replicated frequencies, and preprocessing shapes the spectrum. The panel supports a descriptive statement that residuals vary slowly over this finite window, but not a robust physical timescale or a model-independent “slow process” conclusion.

**Required revision.** Either move the spectrum to the supplement and retain autocorrelation/residual-time plots in the main paper, or strengthen it using prespecified detrending, a taper, sensitivity across sampling grids and windows, and preferably shot-level spectra or a multitaper/low-frequency surrogate analysis. Explicitly report whether the power fraction is computed after mean removal only, after linear detrending, or otherwise.

**Acceptance criterion.** Main-text language is limited to the finite-window diagnostic actually supported. No physical period, drift mechanism, or independent timescale is inferred. The Figure 4 cross-reference points to the correct caveat.

---

### 6.11 The held-out other-shot result should be scoped and simplified

**Finding.** The fully held-out other-four-shot template achieves mean RMSE about 0.186 g s⁻¹, versus about 0.189 g s⁻¹ for the partly target-informed `Φ(t)` trajectory, with the five paired differences split two to three. The conclusion says the template “predicts a new brew as well as” the named trajectory and that the named closure shows “no new-shot predictive advantage.”

**Why it matters.** This is a strong and useful result, but it is based on five nominal-9-bar brews from one rig/campaign, with asymmetric access: the empirical template uses other flow traces, while `Φ(t)` reuses campaign-derived dissolved-mass information that is partly based on flow. It does not establish equivalence in a population or across apparatus, coffee, recipes, or pressures.

The raw other-four mean is also the most transparent fully empirical predictor. Its RMSE is about 0.18644 g s⁻¹, and the penalized-spline variant is effectively the same at the reported precision. Making the spline the primary comparator adds architecture and smoothing choices without adding material performance.

**Required revision.** Make the raw mean of the other four aligned traces the primary held-out template. Present the fixed-architecture spline as a sensitivity check. Replace the broad conclusion with:

> In this five-shot, same-condition comparison, the partly target-informed `Φ(t)` reconstruction did not outperform a fully held-out template formed from the other four observed traces.

Do not use `equivalent` unless an equivalence margin and test are prespecified.

**Acceptance criterion.** The conclusion names the five-shot, one-condition scope and asymmetric access. The raw other-four template is primary or the choice of spline is explicitly justified before inspecting results.

---

### 6.12 The 8.71 bar value is an endpoint summary, not the delivered mean pressure

**Finding.** The pressure-domain producer takes one `endpoint_100s` row per nominal pressure. At nominal 9 bar, the five final basket-pressure values average approximately 8.7169 bar. The corresponding mean over the primary 15–95 s scored interval is approximately 8.7370 bar, and the full processed 0–100 s mean is approximately 8.7679 bar. The manuscript currently says the condition “delivered a mean 8.71 bar at the basket.”

**Why it matters.** “Mean delivered pressure” normally implies a temporal mean, not a mean across shots of one final sample. This distinction matters because the paper emphasizes precise pressure nodes and uses the recorded pressure history in a robustness check.

**Required revision.** Rename the plotted/data quantity **mean endpoint basket pressure at approximately 100 s**. If the scientific question concerns the temporal scoring interval, plot the 15–95 s time-and-shot mean or, preferably, summarize the pressure history with mean, range, and temporal variation. Retain nominal and recorded quantities as separate variables.

Also replace **model-valid pressure range** with **evaluated pressure range (1–13 bar)** unless the authors have performed a separate formal validity assessment.

**Acceptance criterion.** The producer key, axis label, caption, Results, and supplement name the endpoint. No general delivered-mean statement is attached to 8.7169 bar.

---

### 6.13 Calibration deletion stability should not substitute for parameter uncertainty

**Finding.** The equilibrium calibration table gives `P_c = 12.39155` bar with a repository `std` field of about 2.97582 bar and `Q_c = 1.89699` g s⁻¹ with `std` about 0.14713 g s⁻¹. The paper emphasizes that deleting one pressure calibration point changes the fitted quantities by at most about 2.8%, but does not place those source uncertainty fields alongside that result.

**Why it matters.** Leave-one-point deletion stability and parameter uncertainty answer different questions. A fit can be stable to deletion while a parameter remains weakly identified or strongly correlated with another parameter. The large relative `P_c` spread is particularly relevant because only the highest nominal pressure lies at or above the point estimate.

**Required revision.** Define exactly what each repository `std` field represents—standard error, covariance-based standard deviation, bootstrap spread, or another quantity—before using it. Report it next to the estimate, provide the covariance or confidence region if available, and propagate calibration uncertainty into the static and temporal predictions. At minimum, add a sensitivity envelope across plausible `P_c` and `Q_c` values. Frame LOPO-EC drift strictly as influence/deletion stability.

**Acceptance criterion.** The manuscript separates influence, precision, and predictive uncertainty; the source of each uncertainty quantity is documented; and cross-pressure conclusions are shown not to depend on an unreported single best-fit calibration.

---

### 6.14 RC-3b is under-specified relative to its role in the results

**Finding.** RC-3b is described as combining the equilibrium relation with a donor extraction trajectory. The implementation fixes a particular donor simulation/configuration and maps it into the pressure-wise comparison. Yet the paper does not provide the defining equations, donor parameter values, normalization, pressure-node assumptions, time alignment, or a sensitivity analysis. RC-3b wins at several pressure settings and therefore materially affects the claimed rank transitions and domain heterogeneity.

**Why it matters.** A branch cannot function as a substantive comparator if a reader cannot reconstruct it from the paper and supplement. “Donor trajectory” also raises transfer questions: whether pressure in the donor model is pump, basket, or puck pressure; whether output mass or time truncation is held fixed; and whether recipe differences are rescaled physically or empirically.

**Required revision.** Add a complete RC-3b specification in Methods or Supplement S9:

- equation and normalization;
- donor model/version and citation;
- every fixed recipe and extraction parameter;
- mapping from donor time/state to Waszkiewicz time/state;
- pressure-node definition;
- handling of shot duration and output target;
- whether any parameter was selected after inspecting cross-pressure results; and
- sensitivity to plausible donor settings.

If this cannot be done compactly and reproducibly, remove RC-3b from headline rank claims and retain it as an exploratory supplement.

**Acceptance criterion.** An independent reader can reproduce the RC-3b vector at every pressure from the archived release without reading undocumented source internals, and the ranking conclusion is robust to a declared sensitivity range.

---

### 6.15 Pressure-wise winners require uncertainty or deliberately descriptive language

**Finding.** The manuscript reports that the best branch changes three times across eleven nominal pressure settings and identifies which branch has the lowest mean-curve RMSE at each pressure. Per-pressure brew counts range from three to ten, and some branch margins—especially around 5 and 6 bar—are modest.

**Why it matters.** A minimum of three correlated point estimates is unstable when the underlying mean curve is estimated from few shots. A rank map without uncertainty can make exploratory differences look like mechanistic regimes or boundaries.

**Required revision.** Preferably bootstrap at the physical-brew level within each pressure, rebuilding the mean curve and rescoring each branch, then report the probability each branch is lowest and intervals for pairwise differences. With very small `n`, use this descriptively and show all shot-level scores. If the resampling is not defensible at `n=3`, state that the winner map is a point-estimate visualization only and remove any regime/boundary implication.

**Acceptance criterion.** Every pressure-wise winner is accompanied by uncertainty or the figure/caption explicitly says the ranks are descriptive point estimates and cannot establish pressure domains or transition thresholds.

---

### 6.16 The source-campaign inventory and exclusions should be visible in the paper

**Finding.** The source campaign is described as containing 60 brews, while the deposited table has 57 source records and 56 distinct physical brews after alias resolution. The provenance file now explains that three source-excluded brews are not in the deposit and identifies the duplicate alias, but the manuscript does not give readers a compact inclusion/exclusion flow.

**Why it matters.** The paper uses shot as the experimental unit and makes cross-pressure statements. Missing or excluded brews may affect balance and selection, even when exclusions were made upstream. Readers need to know whether exclusion was prespecified, caused by sensor failure, or related to the response.

**Required revision.** Include a supplementary inventory with one row per source brew: source ID, nominal pressure, inclusion status, reason for exclusion, alias relationship, and whether it contributes to the deposited mean, shot-level analysis, and weighted summaries. Add a one-sentence limitation that the present study inherits upstream exclusions and cannot fully assess their selection effect unless raw excluded traces and reasons are available.

**Acceptance criterion.** Counts reconcile exactly: 60 source brews → three excluded upstream → 57 deposited identifiers → one alias pair → 56 distinct physical brews. Every table states which level it uses.

---

### 6.17 The proposed perturbation matrix sometimes treats suggestive signatures as identifying evidence

**Finding.** Table 4 and the experiment sections are valuable, but some cells imply that flow-reversal asymmetry, re-clogging, or an outlet-side deposit would establish fines migration, while a flat rebrew would support dissolution-linked opening.

**Why it matters.** These signatures are not unique. Plumbing asymmetry, residual gas, preferential wetting, basket geometry, filter-paper deformation, asymmetric compaction, particle release unrelated to migration, and hysteretic machine control can mimic them. Conversely, a fines layer may not remobilize under the chosen reversal amplitude. An intervention is discriminating only when apparatus and alternative-bed controls are specified.

**Required revision.** Recast Table 4 as **expected directional tendencies under stated idealizations**, not outcome-to-mechanism assignments. Add:

- an inert porous-load control for machine/plumbing asymmetry;
- a no-fines or controlled-fines preparation;
- matched pressure-node measurements on both sides of the puck;
- imaging or collected-particle mass to corroborate migration;
- repeat randomized orientation/reversal order;
- sham pressure steps; and
- independently measured extraction/TDS and saturation state.

Use phrases such as “would increase support for” rather than “would establish.”

**Acceptance criterion.** No single proposed observable is presented as uniquely identifying fines migration, swelling, or dissolution. Each high-value experiment includes at least one machine control and one independent state measurement.

---

### 6.18 Population language exceeds the finite-campaign design

**Finding.** Table 3c labels the mean individual-shot RMSE as “the expected error of a randomly drawn shot,” and nearby prose asks what happens to a randomly drawn shot.

**Why it matters.** The 56 brews are a finite, structured campaign, not documented as a probability sample from a defined population of espresso shots. Their pressure distribution is design-dependent and unequal. Averaging them estimates the arithmetic mean over the observed records; it does not, without a sampling model, estimate population expectation.

**Required revision.** Use:

> mean RMSE over the 56 observed physical brews, giving each observed brew equal weight.

For the pooled score use:

> RMSE over all retained record×time observations, which weights longer/equally sampled records and pressure settings in proportion to their observations.

If a target population is desired, define the pressure/recipe distribution and use design or post-stratification weights.

**Acceptance criterion.** `expected`, `randomly drawn`, and population-general language are removed unless a sampling distribution is explicitly defined.

---

### 6.19 The manuscript is too long and ledger-like for its central contribution

**Finding.** The draft is approximately 12,000 words, with a roughly 437-word abstract and a Results section of more than 4,000 words. Much of the prose documents prior-review corrections, withdrawn claims, implementation details, and governance history.

**Why it matters.** The evidentiary caution is a strength, but the article’s scientific argument is harder to see than necessary. Journal reviewers may interpret the length as uncertainty about the main contribution. Recounting earlier versions (“an earlier version said…”) belongs in a changelog, response letter, or provenance supplement, not usually in the final narrative.

**Required revision.** Reduce the main paper to its central chain:

1. non-uniqueness demonstrated by the machine–wetting branch;
2. declared 9-bar temporal ladder;
3. shot-level and other-shot evidence;
4. cross-pressure heterogeneity with honest estimands;
5. residual/identifiability limitations; and
6. discriminating experimental program.

Move exact resampling implementation, access graph internals, full pressure tables, review history, withdrawn interval-holdout analysis, model-card details, and reproducibility ledgers to a supplement. Target a 250–300-word abstract and a materially shorter Results section.

**Acceptance criterion.** The abstract states design, principal values, access limitations, and conclusion without implementation digressions; the main paper can be read continuously without repository-internal terminology; and all moved material remains archived and citable.

---

### 6.20 The front matter and equation rendering are not yet submission-ready

**Finding.** The draft still contains placeholder author/affiliation, funding, competing-interest, and acknowledgment sections. The working date is stale. The cubic equation currently contains a tab/missing backslash in `Q_{\text{cub}}`, causing malformed rendering in some views.

**Why it matters.** These are simple editorial defects but will undermine confidence in a technically meticulous paper if left to the submission stage.

**Required revision.** Complete all front matter, select the target journal’s reference and equation style, repair the cubic token, run a Markdown/LaTeX render, and inspect every equation, table, and figure caption in the exact submission output.

**Acceptance criterion.** No placeholders remain; equations render correctly in HTML and the submission PDF; author contributions and disclosures are complete; and the manuscript date/version matches the frozen release.

---
## 7. Section-by-section review

### Title and abstract

The current title is memorable and accurately signals non-identifiability, but it reads slightly like an essay title. A more conventional scientific title would make the observable, comparison, and espresso context explicit. Possible alternatives are:

1. **Temporal espresso flow requires dynamic predictions but does not identify bed mechanism**
2. **Null-first inference from time-resolved espresso flow: dynamic reconstruction without mechanism identification**
3. **Machine–wetting and porous-bed dynamics are non-identifiable from a single espresso flow curve**
4. **Time-resolved espresso flow rejects tested static nulls but not competing dynamic mechanisms**

The abstract contains the right safeguards but is too long and contains too many subsidiary results. Retain the Foster non-uniqueness example, the principal 9-bar ladder, the five-shot held-out-template result, the cross-pressure heterogeneity result, and the model-relative conclusion. Remove secondary pressure-domain detail, the full significance-discreteness explanation, and most proposed-experiment enumeration from the abstract.

Specific corrections:

- Replace the universal “no new-shot predictive advantage” formulation with the five-shot, same-condition wording proposed in §6.11.
- Clarify that 0.335–0.343 g s⁻¹ refers to two different mean-curve averaging schemes, while 0.364 g s⁻¹ is the mean individual-brew score.
- Avoid describing pressure-wise minima as regimes.
- Keep “residual power concentrated at low frequencies” descriptive and finite-window qualified.
- State that `Φ(t)` is partly target-informed before reporting its apparently strong RMSE.

### 1. Introduction

The Introduction now has a clear inferential thesis: similar integrated trajectories can be generated by different state/boundary combinations. The discussion of model lineages is useful, and the null-first sequence is a strong organizing device.

Required improvements:

- Use **machine–wetting** rather than alternating between machine, boundary-condition, and no-bed language.
- Define “mechanism identification” more explicitly: identification of a unique latent process or parameterization from the available observable under the candidate model set.
- Distinguish structural non-identifiability from practical weak discrimination due to noise, preprocessing, and finite replication.
- State early that the measured object is a processed campaign mean, not a raw shot trace, and that shot-level checks are secondary re-scorings of the deposited per-brew records.
- Reduce repeated declarations that fit is not mechanism; one clear statement in the Introduction and one in the Discussion are sufficient.

### 2. Data and evidence objects

This section is much improved by the observation-operator description and alias provenance. It should now become the definitive place for all counts and exclusions.

Add a compact flow statement:

> The source campaign reports 60 brews. Three were excluded upstream and are absent from the deposited processed table. The deposit contains 57 identifiers; two are aliases of the same processed physical brew, leaving 56 distinct brews for shot-level inference.

Also:

- State whether the five 9-bar records are all source brews at that condition or a subset.
- Name the exact differentiated-mass smoothing method, window implementation, edge handling, interpolation grid, alignment event, and whether any negative flow values were clipped.
- Clarify that the pointwise fields named `*_std` in the source workflow are standard errors if that remains true in the deposited mean object.
- Distinguish full-resolution values from 1 s-decimated diagnostic values.
- Add an explicit table of pressure nodes and units rather than relying only on prose.

### 3. Model ladder

This section should be the most compact and reproducible part of the manuscript.

- **Static branches:** give the exact pressure input used—nominal 9 bar or recorded basket pressure—and place the alternative in a robustness subsection.
- **Late constant:** correct the access interval and parameter count as in §6.2.
- **Empirical `Φ(t)`:** retain the excellent target-access caveat, but add the exact sigmoid formula and numerical parameters in the supplement.
- **Cubic:** remove bound/floor language and fix the equation rendering.
- **RC-3b:** supply complete equations and donor settings or move it out of the main paper.
- **Provenance table:** classify access using a small controlled vocabulary and make it machine-readable. `same_shot` is not enough for the late constant; the relevant class is direct target use on a subset of the scored interval.

### 4. Statistical and diagnostic analysis

The strongest methodological improvement is treating the shot as the experimental unit. Preserve that emphasis.

For the fixed-loss block sensitivity:

- It is correctly described as conditional on already-computed predictions.
- Consider moving the implementation paragraph to the supplement and retaining only the estimand, pairing, block lengths, and caveat in the main paper.
- The phrase “interval resolves the sign” is preferable to confidence-interval terminology, given the conditional construction.

For the shot-level analysis:

- Scope the exact sign-flip test as in §6.9.
- Report all five paired differences in a small table or dot plot, not only their mean and sign count.
- Make the leave-one-shot-out other-four mean primary.
- Define whether each branch’s free parameters are re-estimated per shot. In particular, the best constant must be fit separately to each scored shot, while same-campaign parameters remain fixed.
- Avoid a five-unit percentile bootstrap in the main text; it adds little beyond the exact sign result and visible paired data.

For residual diagnostics:

- Keep residual-versus-time and common-grid autocorrelation.
- Move the periodogram to the supplement unless strengthened.
- Report residual scale relative to both pointwise shot SD and shot-level predictive error without implying either is an irreducible noise floor.

### 5. Results

The Results contain the necessary evidence but should be reordered and shortened.

- Start with the numerical ladder and access classes.
- Follow immediately with the five individual-shot paired results and the other-four template.
- Present residual diagnostics after these primary experimental-unit results.
- Then give cross-pressure heterogeneity, with shot-level estimands before mean-curve summaries.
- Present pressure nodes and calibration domain before interpreting pressure-wise ranks.
- Move the access dependency graph to Methods or supplement; it is not a result.
- Remove narration about earlier versions and withdrawn claims. State the current result only, with the sensitivity evidence that supports it.

For Table 3c, rename the rows exactly by unit and weighting. A defensible ordering is:

1. mean RMSE over 56 observed physical brews;
2. pooled RMSE over retained brew×time observations;
3. equal mean across 11 pressure-level mean curves; and
4. source-record-count-weighted mean of pressure-level mean-curve RMSEs, only if this hybrid is retained.

For the pressure-domain paragraph, use **endpoint basket pressure** and **evaluated pressure range**.

### 6. Proposed experiments

This section is a valuable contribution and should remain, but it needs a clearer distinction between predictions, controls, and identifying observations.

For each proposed experiment, state:

- manipulated boundary condition;
- independently measured input and pressure node;
- primary observable;
- independent latent-state measurement;
- apparatus-only/inert-bed control;
- expected sign under each candidate branch;
- falsification criterion; and
- known confounders.

The highest-value near-term experiment is likely a pressure-step or controlled flow/pressure intervention with simultaneous upstream/downstream pressure and time-resolved outlet mass/TDS. Flow reversal is potentially discriminating but experimentally difficult and especially vulnerable to plumbing asymmetry; it should not be presented as uniquely decisive without an inert-load reversal control.

### 7. Discussion

The Discussion is scientifically mature and appropriately cautious. It can be shorter.

Retain:

- model-relative rejection of specified time-invariant branches;
- inability of one integrated curve to identify latent mechanism;
- asymmetric access of `Φ(t)` and the held-out template;
- pressure-wise heterogeneity; and
- the need for interventions and independent state measurements.

Correct:

- the Foster “without bed evolution” regression;
- the LOPO phrasing;
- broad new-shot/population claims; and
- any implication that the cubic provides a flexibility bound.

Add one explicit distinction:

> The present result is evidence against the tested time-invariant *predictions*, not proof that every admissible static spatial field or unmeasured time-varying boundary condition is absent.

### Limitations

The limitations are already unusually strong. Add or sharpen:

- inherited upstream exclusions and unknown selection implications;
- partial target access in the dissolved-mass trajectory;
- processed/aligned/smoothed observation rather than raw sensor data;
- only five shots at the principal 9-bar condition;
- unequal counts and no population sampling design across pressure;
- weakly constrained equilibrium characteristic pressure;
- under-specified RC-3b transfer assumptions;
- no independent measurement of saturation, fines, swelling, porosity, or internal pressure; and
- no external apparatus/coffee/recipe validation.

### Conclusion

The conclusion should be reduced to three claims:

1. a pump–headspace–sharp-front-infiltration branch demonstrates curve-shape non-uniqueness without extraction-driven evolution of saturated-bed constitutive properties;
2. the processed 9-bar mean trajectory needs time-varying predictions relative to the tested time-invariant branches; and
3. fit quality and the present held-out evidence do not identify the responsible physical closure.

Avoid a long list of caveats here; those belong in Limitations.

### Figures, supplement, and declarations

The declaration sections must be completed. The supplementary-material “plan” must become a real archived supplement, with stable filenames and cross-references. Internal repository function names can remain in a reproducibility appendix but should not interrupt the main journal narrative.

---

## 8. Figure-by-figure review

### Figure 1 — machine-side/non-unique flow minimum

**Strengths:** The pressure-node diagram and explicit separation between the Foster evidence object and the Waszkiewicz measured trace are excellent. The caption correctly notes that the wetting front advances.

**Required changes:**

- Rename the figure concept from “machine-side” to **machine–wetting** non-uniqueness.
- Ensure the plotted/reconstructed Foster curve is identified as normalized and not quantitatively fitted to the Waszkiewicz trace.
- Put the pressure-node definition directly on the panel or legend.
- State which quantities are digitized versus recomputed.

### Figure 2 — primary temporal ladder

**Strengths:** This is the principal figure and now communicates target access better than earlier versions.

**Required changes:**

- Relabel the late branch **85–95 s subset-fit constant** and visually mark its fitting interval.
- Replace parameter-count-only annotations with short access labels: direct target, same-campaign indirect target, or literature/donor.
- State whether the between-shot band uses full-resolution or 1 s-grid SD and whether it is SD or SEM.
- Keep the fixed-loss interval panel explicitly secondary.
- Consider adding the five shot-level paired differences as an inset or a separate main panel, because they are more important than the conditional block intervals.

### Figure 3 — cross-pressure assessment

**Strengths:** Showing every pressure and the three adjacent branch changes is much better than an aggregate-only score.

**Required changes:**

- Change all “held-out” labels to **equilibrium point omitted / LOPO-EC**.
- Add per-pressure physical-brew counts and uncertainty or label winners as descriptive point estimates.
- Rename panel (d) **nominal setting versus mean endpoint basket pressure at approximately 100 s**.
- Show calibration uncertainty, not only ±2.8% deletion drift.
- Clarify whether the 13-bar mean curve contains the duplicate alias or regenerate it from six physical brews.

### Figure 4 — residual diagnostics

**Strengths:** The new Fourier-bin framing and warning against interpreting 80/40 s as measured periods are major improvements.

**Required changes:**

- Correct the section cross-reference.
- Prefer moving the spectral panels to the supplement.
- If retained, add the detrending/taper specification and a sensitivity panel or source-data field.
- Avoid “Every branch leaves coherent low-frequency lack of fit” as an absolute title; use **“Residuals retain slow finite-window structure on the declared diagnostic grid.”**
- Explain why constant and static branches coincide after centering without implying that the underlying predictions are identical.

### Figure 5 — mechanism-by-perturbation matrix

**Strengths:** The matrix turns non-identifiability into a constructive experimental program.

**Required changes:**

- Replace machine/headspace with **machine–wetting / infiltration**.
- Remove “without bed,” “no signature,” and categorical mechanism assignments.
- Add a visible legend: **predicted tendency, not observed result**.
- Add controls or a parallel small panel listing required apparatus-only and independent-state measurements.
- Do not single out reversal as uniquely discriminating in sign unless every candidate’s prediction and confounder has been formally derived.

### Alt text and source-data exports

Alt text must communicate the same access qualifications as the captions. Figure 3 currently overstates holding out, and Figure 5 inherits the no-bed shorthand. Regenerate all PNG/PDF/SVG and source-data CSV assets after the final semantic pass; do not assume updated Python source means committed renders are current.

---

## 9. Suggested replacement wording

### 9.1 Foster branch in Table 4 and conclusion

**Replace:**

> Can generate dip/recovery without bed evolution.

**With:**

> Can generate dip/recovery without extraction-driven change in saturated-bed constitutive properties; wetting front, phase occupancy, and saturated path length still evolve.

**Replace the conclusion’s first sentence with:**

> A flow curve can reject specified time-invariant predictions without identifying a physical mechanism. A published pump–headspace–sharp-front-infiltration model generates a dip-and-recovery trajectory without extraction, swelling, fines transport, particle rearrangement, or damage-driven permeability evolution, although its wetting and saturated-path state evolve.

### 9.2 Late-window constant Methods/Table 1

> The 85–95 s subset-fit constant estimates one level directly from the final ten seconds of the 15–95 s scoring interval and applies that level across the full interval. It is therefore an in-sample, one-parameter sensitivity branch, not an out-of-window or held-out estimate.

Suggested Table 1 row:

| Branch | Coefficients fitted using this target | Other parameters | Access | Intended role |
|---|---:|---|---|---|
| 85–95 s subset-fit constant | 1 level from an in-window target subset | none | direct target | interpretable in-sample static sensitivity |

### 9.3 Cubic comparator

> A degree-three polynomial with four coefficients is fitted and scored on the same 15–95 s mean trajectory. It is one low-dimensional, non-mechanistic temporal comparator. Its purpose is to test whether a simple time function can match the reconstruction quality of the named temporal closure; it does not bound the performance of other temporal model classes and is not a predictive benchmark.

### 9.4 Exact sign-flip test

> Under the sign-symmetry null, we enumerated all 32 sign assignments of the five nonzero paired differences using the mean paired difference as the statistic. For this exact two-sided sign-flip test, the smallest attainable p-value is 2/32 = 0.0625. We therefore emphasize the five visible paired effects and directional consistency rather than a conventional significance threshold.

### 9.5 Held-out other-shot conclusion

> In the five nominal-9-bar brews from this campaign, a fully held-out template formed from the other four observed traces achieved mean RMSE 0.186 g s⁻¹, compared with 0.189 g s⁻¹ for the partly target-informed empirical `Φ(t)` trajectory; the paired differences favoured the two branches in two and three shots, respectively. Thus, in this same-condition comparison, the named closure did not outperform a simple other-shot template for prediction of the omitted brew.

### 9.6 Cross-pressure estimands

> The mean individual-brew RMSE gives each of the 56 observed physical brews equal weight. It is a finite-campaign descriptive average, not a population expectation. The pooled RMSE instead combines all retained brew×time observations. Pressure-level mean-curve summaries answer different questions and are reported separately; they should not be interpreted as shot-level predictive error.

If the source duplicate remains in the mean-curve object:

> The deposited 13-bar mean curve averages seven source records representing six physical brews because one alias is duplicated. Mean-curve summaries that retain this object are labeled source-record based and are not described as 56-brew summaries.

### 9.7 Pressure-domain wording

> The nominal 9-bar condition had a mean endpoint basket pressure of 8.717 bar across its five processed records at approximately 100 s. Over the primary 15–95 s scoring interval, the time-and-shot mean basket pressure was approximately 8.737 bar. Nominal setting, recorded basket history, and fitted characteristic pressure are distinct quantities.

### 9.8 Calibration stability and uncertainty

> Omitting one pressure point from the equilibrium calibration changed the fitted point estimates by no more than approximately 2.8%, indicating limited single-point influence within this campaign. This deletion stability is not a confidence interval. The full fit reports `P_c = 12.39` bar and `Q_c = 1.897` g s⁻¹, with repository uncertainty fields of 2.98 bar and 0.147 g s⁻¹, respectively; their statistical meaning and propagation are reported in the supplement.

### 9.9 Artifact verification

> Figures and registered manuscript values are generated from a common result bundle, and automated checks reduce numeric transcription error. Numeric agreement does not by itself validate estimand choice, target-access classification, pressure-node identity, physical interpretation, or release freshness, which are checked separately through semantic tests and a clean-release manifest.

### 9.10 Figure 4 caption

> **Figure 4. Residual dependence on the declared finite diagnostic grid.** Residual autocorrelation and spectral-bin summaries are computed on the same approximately 1 s, 80-point window. Power concentrated in the first Fourier bins indicates slow variation relative to this window, but the corresponding 80 s and 40 s periods are grid properties rather than independently identified physical timescales. Results are descriptive and sensitive to detrending, tapering, preprocessing, and window choice.

### 9.11 Proposed-experiment decision logic

> Perturbation outcomes are treated as shifts in relative support rather than unique mechanism identifiers. A reversal asymmetry, for example, would increase support for directional deposition only if it exceeds the response of an inert hydraulic load and is corroborated by independent particle or spatial-state measurements.

---

## 10. Suggested shorter abstract

Time-resolved espresso outlet flow combines pump and headspace response, wetting, pressure boundary conditions, evolving hydraulic resistance, extraction, and measurement processing. Similar trajectories may therefore arise from different mechanisms. We apply a null-first comparison to ask whether a measured flow curve requires time-varying predictions relative to specified time-invariant branches, and whether improved reconstruction identifies a porous-bed process. A published pump–headspace–sharp-front-infiltration model first shows that a dip-and-recovery curve can arise without extraction-driven change in saturated-bed constitutive properties, although wetting state and hydraulic path length evolve. We then analyze the differentiated, approximately 3 s-smoothed, aligned mean of five nominal-9-bar brews over 15–95 s. The best constant and static poroelastic branches have RMSEs of 0.573 and 0.648 g s⁻¹. A partly target-informed, dissolution-linked empirical `Φ(t)` trajectory has RMSE 0.116 g s⁻¹, while a four-parameter cubic fitted and scored on the same trace has RMSE 0.096 g s⁻¹. Across the five individual brews, `Φ(t)` improves on the constant and static branches, but a fully held-out template formed from the other four brews predicts the omitted brew with mean RMSE 0.186 g s⁻¹, compared with 0.189 g s⁻¹ for `Φ(t)`. Across eleven nominal pressure settings, the lowest-error branch varies and individual-brew errors exceed pressure-level mean-curve errors. These results support time-varying predictions relative to the tested time-invariant branches, but neither same-trace fit nor the present held-out comparison identifies the responsible closure. Mechanistic discrimination requires interventions and independent state measurements, including controlled pressure or flow steps, reversal with apparatus controls, rebrewing, and spatial measurements of saturation, solids, deformation, or fines.

This version is approximately 250 words and preserves the core claims without the current abstract’s secondary detail.

---

## 11. Recommended final manuscript architecture

1. **Introduction**
   - Integrated-observable inverse problem
   - Espresso model lineages
   - Null-first questions and claim scope

2. **Evidence objects and observation operator**
   - Foster machine–wetting object
   - Waszkiewicz campaign, counts, exclusions, alias
   - Differentiation, smoothing, alignment, interpolation
   - Pressure nodes and analysis windows

3. **Candidate branches and access classes**
   - Constants and equilibrium poroelastic branch
   - Empirical `Φ(t)`
   - Four-parameter cubic comparator
   - RC-3b, if fully specified
   - Access/provenance table

4. **Evaluation design**
   - Primary 9-bar mean-trajectory reconstruction
   - Shot-level paired analysis
   - Fully held-out other-four template
   - Cross-pressure shot-level and mean-curve estimands
   - Residual and sensitivity diagnostics

5. **Results**
   - Main ladder
   - Five-shot evidence and other-shot prediction
   - Cross-pressure heterogeneity and uncertainty
   - Pressure/calibration sensitivity
   - Residual lack of fit

6. **Discriminating experiments**
   - Controlled pressure/flow steps
   - Reversal plus inert-load control
   - Rebrew and first-drop tests
   - Spatial and chemical state measurements

7. **Discussion**
   - What is rejected
   - What is not identified
   - External-validity and access limitations
   - Implications for espresso modeling

8. **Conclusion**

9. **Supplement**
   - complete equations/parameters;
   - brew inventory and exclusion table;
   - full precision scores and paired differences;
   - residual/spectral sensitivity;
   - block-resampling implementation;
   - RC-3b specification;
   - figure source data;
   - reproducibility manifest and semantic checks.

---

## 12. Pre-submission acceptance checklist

### Scientific meaning and access

- [ ] Foster branch is named machine–wetting/infiltration and never described as having no bed evolution.
- [ ] The late constant is classified as a one-parameter 85–95 s in-window subset fit.
- [ ] `Φ(t)` is consistently described as partly target-informed and within-campaign.
- [ ] The other-four template is the only fully held-out shot comparator.
- [ ] LOPO-EC is never presented as fully held-out temporal validation.
- [ ] The cubic is called a comparator, not a bound or floor.
- [ ] RC-3b is fully specified or demoted to exploratory supplement.

### Experimental units and estimands

- [ ] The 60 → 57 identifiers → 56 physical brews accounting is explicit.
- [ ] Every table identifies pressure-, record-, brew-, or brew×time-level units.
- [ ] The 13-bar alias is either removed from reconstructed means or clearly retained as a source-record object.
- [ ] Mean individual-brew and pooled errors are not called population expectations.
- [ ] Pressure-wise rank claims include uncertainty or are explicitly descriptive.
- [ ] Five paired differences are visible and the exact sign-flip assumptions are stated.

### Pressure and calibration

- [ ] Nominal, pump, basket, puck, endpoint, interval-mean, and characteristic pressure are not conflated.
- [ ] 8.717 bar is labeled mean endpoint basket pressure at approximately 100 s.
- [ ] “Model-valid range” is replaced by evaluated/data-support range.
- [ ] Calibration uncertainty is reported and distinguished from deletion stability.
- [ ] Static and temporal conclusions are robust to plausible calibration uncertainty.

### Manuscript and figures

- [ ] Sections, tables, figures, supplements, and notes are in order and cross-references resolve.
- [ ] Figure 3 and alt text use LOPO-EC language.
- [ ] Figure 4 has the correct caveat/reference or is moved to the supplement.
- [ ] Figure 5 removes no-bed shorthand and includes control-dependent interpretation.
- [ ] All figure formats and source-data CSVs are regenerated from final source.
- [ ] The cubic equation renders correctly.
- [ ] Abstract is shortened and conclusion is model-relative.
- [ ] Review-history and internal governance prose is moved out of the main article.
- [ ] Author, affiliation, contribution, funding, competing-interest, and acknowledgment fields are complete.

### Reproducibility release

- [ ] Final build starts from a clean checkout.
- [ ] Bundle and manuscript commit hashes match.
- [ ] Manifest records `git_dirty=false`, UTC timestamp, environment, data hashes, and figure hashes.
- [ ] `release_fresh=true` under strict verification.
- [ ] Numeric, semantic, unit, access-class, and cross-reference tests all pass.
- [ ] The semantic audit includes manuscript, figure source, captions, alt text, claim registry, result labels, and relevant harness code.
- [ ] Correct commands are documented under `python -m puckworks.paper_b2.build`.
- [ ] The exact release is tagged and archived at a stable citation/DOI.
- [ ] A reviewer can reproduce every main table and figure without an uncommitted local file.

---

## 13. Final recommendation

**Major revision before external journal submission.**

Paper B2 now has a credible and potentially valuable contribution. Its central numerical result is reproducible: the declared processed nominal-9-bar mean trajectory is reconstructed far better by the tested time-varying branches than by the tested time-invariant branches. The manuscript also now does something unusually useful: it separates reconstruction, target access, prediction, and mechanism identification, and it converts residual ambiguity into a proposed experimental program.

The fifth-round blockers are narrower than those in earlier reviews, but they are not cosmetic. The current draft still misclassifies the late-window constant’s target access, mixes 57 source records with 56 physical brews in one cross-pressure summary, allows “held-out” language to drift back into LOPO-EC artifacts, and reintroduces the physically incorrect “without bed evolution” shorthand on prominent surfaces. Its pressure-domain label refers to an endpoint rather than a temporal mean, calibration precision is not presented alongside deletion stability, and its reproducibility package remains tied to an earlier dirty snapshot. These issues affect what a reader would infer from the evidence.

Once those points are corrected, the cubic is consistently demoted from a supposed bound to a comparator, the residual-spectrum claim is appropriately scoped, RC-3b is specified or demoted, the paper is shortened, and a clean commit-matched release is frozen, the manuscript should be ready for a final technical proofread and target-journal formatting pass. I would then expect the appropriate recommendation to move from **major revision** toward **minor revision / submission-ready**, assuming the regenerated evidence bundle confirms the present numerical results.

