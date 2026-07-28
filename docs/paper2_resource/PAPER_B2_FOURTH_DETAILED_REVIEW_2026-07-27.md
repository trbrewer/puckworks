# Fourth Detailed Review of PAPER B2

## Manuscript reviewed

**File:** `docs/PAPER_B2_TEMPORAL_DRAFT.md`  
**Current title:** *One flow curve, many explanations: null-first inference for machine and porous-bed dynamics in espresso*  
**Repository:** <https://github.com/trbrewer/puckworks>  
**Pinned repository snapshot:** [`352dacd51015d95a3b5a5b3e1a8fb331419d78b0`](https://github.com/trbrewer/puckworks/tree/352dacd51015d95a3b5a5b3e1a8fb331419d78b0)  
**Review date:** 27 July 2026  
**Recommendation:** **Major revision before external journal submission**

Line references refer to the manuscript at the pinned snapshot unless otherwise stated.

---

## 1. Editorial decision and overall assessment

Paper B2 has improved substantially again. The current draft now deals responsibly with several of the most important concerns raised in the previous review. In particular, it:

- distinguishes the leave-in shot-to-full-mean dispersion from the honest other-four template error and explicitly says that neither is a noise floor;
- reports the five individual 9-bar shots as the experimental units and gives the exact attainable two-sided sign-flip result;
- distinguishes the fully held-out other-shot empirical template from the partly target-informed `Φ(t)` trajectory;
- withdraws the earlier interval-holdout headline after showing that it is comparator- and gap-dependent;
- separates nominal, recorded-basket, and fitted characteristic pressures;
- shows the strong pressure dependence concealed by an aggregate error;
- computes the genuine individual-shot cross-pressure estimands in the analysis layer; and
- retracts the earlier physical interpretation of 80 s and 40 s Fourier bins in the Results text.

The central descriptive result remains persuasive and reproducible: on the declared, preprocessed 9-bar mean trajectory, the tested time-varying branches reconstruct the flow much more closely than the tested time-invariant constant and static poroelastic branches. The manuscript also remains appropriately cautious that reconstruction quality does not identify a unique physical mechanism.

The paper is nevertheless **not yet submission-ready**. This fourth review found seven submission-blocking issues, three of which are new data- or code-integrity findings rather than merely uncompleted editorial work:

1. **Two nominally separate shots are exactly identical after preprocessing.** `12-8-6` and `12-8-6_alt` have identical values in every numeric field at all 1,000 time rows, yet are counted as two independent shots in the 57-shot summaries.
2. **The Foster branch is still misclassified as “machine-only” and as operating “without an evolving bed.”** Its sharp wetting front is an evolving bed saturation state. What is absent is extraction-driven or damage-driven evolution of saturated-bed constitutive properties, not bed evolution in every sense.
3. **The manuscript still describes a shot-count-weighted mean of pressure-level mean-curve RMSEs as answering what happens to a randomly drawn shot.** The analysis code correctly says this is mathematically false and already computes the proper individual-shot estimand, but the prose has not been synchronized.
4. **Figure 4 contradicts the corrected Results text.** The manuscript caption still says “Residual structure is slow drift” and reports “dominant residual periods,” while the revised analysis correctly says the values are merely the first two available Fourier bins of the 80 s window.
5. **The evidence release remains dirty, stale, and tied to an earlier commit.** The current manifest reports `git_dirty=true`, `release_fresh=false`, a null timestamp, and source commit `99ea79f…`, not the reviewed manuscript commit `352dacd…`.
6. **The cross-pressure producer contains a rank-transition counting bug.** It returns `len(set(winners)) - 1`, which counts distinct winner labels minus one, not adjacent changes. The observed winner sequence changes three times, while that expression returns two.
7. **The manuscript overstates what numerical verification guarantees.** Verified plotted values can still be assigned the wrong estimand, caption, access class, or physical interpretation; the present Figure 4 and cross-pressure wording are concrete examples.

These problems do not overturn the paper’s main 9-bar reconstruction result. They do affect the claimed experimental-unit count, pressure-domain inference, conceptual framing of the first null, figure semantics, and reproducibility status. They therefore require correction before peer review.

My recommendation remains **major revision**, but the manuscript is now closer to a defensible submission than in the first three rounds. The next revision should be a focused integration and integrity pass rather than another wholesale conceptual rewrite.

---

## 2. Scope and method of this review

I reviewed the following at the pinned repository snapshot:

- [`docs/PAPER_B2_TEMPORAL_DRAFT.md`](https://github.com/trbrewer/puckworks/blob/352dacd51015d95a3b5a5b3e1a8fb331419d78b0/docs/PAPER_B2_TEMPORAL_DRAFT.md)
- [`puckworks/analysis/waszkiewicz_shot_level.py`](https://github.com/trbrewer/puckworks/blob/352dacd51015d95a3b5a5b3e1a8fb331419d78b0/puckworks/analysis/waszkiewicz_shot_level.py)
- [`puckworks/analysis/waszkiewicz_cross_pressure.py`](https://github.com/trbrewer/puckworks/blob/352dacd51015d95a3b5a5b3e1a8fb331419d78b0/puckworks/analysis/waszkiewicz_cross_pressure.py)
- [`puckworks/figures_paper_b2.py`](https://github.com/trbrewer/puckworks/blob/352dacd51015d95a3b5a5b3e1a8fb331419d78b0/puckworks/figures_paper_b2.py)
- [`docs/figures/paper_b_results.json`](https://github.com/trbrewer/puckworks/blob/352dacd51015d95a3b5a5b3e1a8fb331419d78b0/docs/figures/paper_b_results.json)
- [`docs/reproducibility/paper_b_manifest.json`](https://github.com/trbrewer/puckworks/blob/352dacd51015d95a3b5a5b3e1a8fb331419d78b0/docs/reproducibility/paper_b_manifest.json)
- [`docs/figures/paper_b2/ALT_TEXT.md`](https://github.com/trbrewer/puckworks/blob/352dacd51015d95a3b5a5b3e1a8fb331419d78b0/docs/figures/paper_b2/ALT_TEXT.md)
- [`docs/paper2_resource/PAPER_B2_ROUND_3_ACTION_TRACKER.md`](https://github.com/trbrewer/puckworks/blob/352dacd51015d95a3b5a5b3e1a8fb331419d78b0/docs/paper2_resource/PAPER_B2_ROUND_3_ACTION_TRACKER.md)
- the committed 57,000-row processed per-brew trace deposit; and
- the previous three detailed reviews and their numerical audits.

I directly checked the processed shot table by grouping all rows by `shot_id`, excluding the identifier itself, and hashing the complete numeric arrays. That audit found one exact duplicate pair. I also inspected the current cross-pressure and figure producers line by line and checked the manuscript against the generated bundle, manifest, alt text, and action tracker.

The core 9-bar numerical ladder was independently reproduced in the preceding review and is unchanged in the current bundle. In this round I did **not** rerun the entire repository CI suite, rebuild every model result from raw upstream source files, or regenerate every figure asset. The current action tracker itself states that rendered PNG/PDF/SVG outputs were not regenerated after the latest figure-code changes. The conclusions below distinguish direct checks from repository-reported checks accordingly.

The exact duplicate finding concerns the **processed repository trajectories**. It does not, by itself, prove that the source campaign did not conduct two physical brews. It does establish that the repository currently supplies no statistically independent information with which to treat those two records as separate experimental units.

---

## 3. Resolution audit against the third review

| Third-review issue | Current status | Fourth-review assessment |
|---|---|---|
| 0.149 g s⁻¹ called a “noise floor” | Manuscript now calls it leave-in dispersion and explicitly rejects floor/threshold interpretations | **Resolved in main prose** |
| Fully held-out spline and partly target-informed `Φ(t)` treated as like-for-like | The asymmetry is now prominent in Abstract, Methods, Results, and Discussion | **Substantially resolved** |
| Interval-holdout result overpromoted | Removed from Abstract/Conclusion and explicitly withdrawn after comparator/gap sensitivity | **Resolved** |
| Genuine individual-shot cross-pressure estimand absent | Producer and bundle now compute mean individual-shot and pooled shot×time RMSEs | **Analysis resolved; manuscript not synchronized** |
| 80 s/40 s interpreted as physical drift timescales | Results text now correctly says they are window bins | **Resolved in Results, regressed in figure caption and stale render surfaces** |
| Dirty and mismatched reproducibility release | Manifest still dirty, stale, untimestamped, and on an older commit | **Unresolved** |
| Repository-wide stale terminology | Mutation-tested semantic audit was strengthened | **Improved, but visible stale labels remain** |
| Cubic described as a floor/bound | Table calls it a comparator, but Methods and residual discussion still use “bound”/“floor” | **Partly unresolved** |
| Cross-pressure pressure-specific ranking hidden | Table 3a and narrative now show all pressure winners | **Strongly improved** |
| Source campaign 60 versus deposit 57 not fully explained | Prose/code now acknowledge three unidentified exclusions | **Improved, but exact duplicate creates a new 57-versus-56 issue** |
| Figures not regenerated after semantic fixes | Action tracker explicitly says they remain unregenerated | **Unresolved** |

The revision has therefore resolved most of the inferential problems identified in round three, but it has also exposed a deeper integration problem: the code, manuscript, figure descriptions, rendered assets, and release manifest are not all describing the same final evidentiary object.

---

## 4. Priority revision matrix

### 4.1 P0 — submission blockers

| ID | Required action | Why it is blocking | Minimum acceptance criterion |
|---|---|---|---|
| **P0.1** | Resolve the exact duplicate `12-8-6` / `12-8-6_alt` | The paper counts 57 shots, but only 56 distinct processed trajectories are present | Provenance establishes whether these are one or two physical brews; statistical treatment is corrected; every affected summary is regenerated; a duplicate-trace gate is added |
| **P0.2** | Replace “machine-only/no evolving bed” with a technically accurate Foster null | A sharp wetting front is an evolving bed saturation state | All prose, headings, captions, alt text, code labels, and matrix entries distinguish evolving wetting from extraction-/damage-driven constitutive evolution |
| **P0.3** | Put the four cross-pressure estimands into the manuscript and correct the “randomly drawn shot” statement | The present weighting interpretation is mathematically wrong | Table and prose report equal-pressure mean-curve, shot-weighted mean-curve, mean individual-shot, and pooled shot×time RMSEs by exact name |
| **P0.4** | Synchronize Figure 4 with the corrected spectral interpretation and regenerate assets | Current caption makes a withdrawn physical claim | No “slow drift,” “dominant period,” or physical-timescale wording remains; panel shows bin index/frequency; PNG/PDF/SVG/source data/alt text all match |
| **P0.5** | Freeze a clean, commit-matched Paper B2 evidence release | Current evidence bundle is not a submission artifact for the reviewed manuscript | `git_dirty=false`; source/bundle/manuscript commits match; timestamp and hashes present; `release_fresh=true`; figures regenerated; tagged archive/DOI |
| **P0.6** | Correct and test `n_rank_changes` | Current producer implements the wrong quantity | Use adjacent-transition count; add a regression test with a re-entrant winner sequence; regenerate bundle and claims |
| **P0.7** | Narrow the artifact-verification guarantee | Numerical equality cannot guarantee semantic correctness | Manuscript states that values are verified separately from estimand labels, captions, access classifications, and render freshness |

### 4.2 P1 — major scientific and methodological revisions

| ID | Revision | Expected result |
|---|---|---|
| **P1.1** | Replace every remaining “cubic bound/floor” formulation with “same-trace descriptive comparator” | Removes a mathematically unsupported benchmark interpretation |
| **P1.2** | Make RC-3b self-contained | Reader can reproduce donor trajectory, equations, units, parameter choices, and pressure dependence without source-code archaeology |
| **P1.3** | Add observation-operator sensitivity | Establishes whether the temporal advantage and residual structure survive reasonable derivative/smoothing/alignment choices |
| **P1.4** | Tighten statistical terminology and branch-specific refitting description | Avoids implying experimental randomization and clarifies what is or is not re-estimated per shot |
| **P1.5** | Complete 60/57/56 provenance accounting | Defines source brews, deposited records, exclusions, aliases, and independent experimental units |
| **P1.6** | Keep spectral claims strictly descriptive unless a fuller analysis is added | Prevents low-frequency bins from being interpreted as physical processes |
| **P1.7** | Expand semantic checks to rendered and reader-visible surfaces | Prevents prose corrections from leaving contradictory captions, alt text, labels, or exports |
| **P1.8** | Correct all figure terminology and regenerate all exports | Makes the evidence package internally coherent |
| **P1.9** | Add methodological references and a real supplement | Makes a methods/inference paper scholarly and reproducible rather than repository-dependent |
| **P1.10** | Moderate “time-varying predictions are required” where necessary | Keeps the claim explicitly relative to tested branches and the chosen observation operator |

### 4.3 P2 — editorial and presentation revisions

- Reduce the approximately 365-word abstract to roughly 220–250 words.
- Correct the malformed equation token `Q_{	ext{cub}}` at manuscript line 111; the current source contains a tab character inside `\text`.
- Replace the nonstandard heading sequence `4.2a`, `4.2b`, `5.3a`, `5.3b`, and `5.3c` with conventional numbering.
- Update the working-draft date from 15 July 2026.
- Complete author names, affiliations, contribution statement, corresponding-author details, funding, competing interests, and acknowledgements.
- Move the extended 110–120 s source-observable autopsy to a supplement after retaining a concise main-text statement.
- Remove internal workflow commentary and function names from the submitted article or move them to the reproducibility supplement.
- Decide whether Figure 5 and Table 4 duplicate one another; retain one in the main text and move the other to supplementary material.
- Expand the bibliography beyond seven references, especially for Savitzky–Golay processing, penalized splines/GCV, exact paired sign-flip inference, grouped validation, inverse problems, identifiability, and model discrimination.

---

## 5. Independent data-integrity and numerical audit

### 5.1 Core 9-bar reconstruction ladder remains sound

The independently reproduced values from the prior round remain the values registered in the current evidence bundle:

| Branch | RMSE (g s⁻¹) | Interpretation |
|---|---:|---|
| Best in-window constant | 0.5728555 | Strongest one-level static null fitted on the scored mean trace |
| Late-window constant | 0.6405890 | Physically motivated static sensitivity |
| Static poroelastic branch | 0.6476960 | Pressure-dependent but time-invariant at fixed pressure |
| Empirical `Φ(t)` trajectory | 0.1157694 | Time-varying, transferred from same-campaign information, partly target-informed |
| Degree-three cubic | 0.0963965 | Four-parameter same-trace descriptive comparator |

This supports the narrow statement that temporal flexibility sharply reduces reconstruction error relative to the tested time-invariant branches on this processed trajectory. It does not establish that `Φ(t)` is the causal bed state or that the cubic is an attainable lower bound.

### 5.2 Current cross-pressure estimands

The revised analysis code correctly distinguishes four estimands. The manuscript currently reports only the first two and still misinterprets the second.

| Estimand | Static | `Φ(t)` | RC-3b | What it means |
|---|---:|---:|---:|---|
| Equal-pressure macro mean of **pressure-level mean-curve** RMSE | 0.5239 | 0.3345 | 0.5098 | Each pressure gets equal weight; response is the pressure-level mean curve |
| Shot-count-weighted macro mean of **pressure-level mean-curve** RMSE | 0.5094 | 0.3431 | 0.5300 | Mean-curve errors weighted by record count; still not a random-shot expectation |
| Mean of 57 individual-record RMSEs | 0.5271 | 0.3632 | 0.5400 | Expected RMSE under uniform sampling of the 57 deposited records, subject to duplicate dependence |
| Pooled shot × time RMSE | 0.5567 | 0.3927 | 0.6143 | Root mean square over all included record-time observations |

All four preserve the aggregate ordering `Φ(t) < static < RC-3b` except the equal-pressure mean-curve summary, where RC-3b is second. The absolute values differ materially because pressure-level averaging removes shot variability that the branches were never asked to predict.

The third row should not yet be called an expectation over 57 independent shots because two records are exact duplicates. After provenance resolution, the estimand should be defined over independent brews or over explicitly clustered source units.

### 5.3 Exact duplicate processed trajectories

The committed processed table contains:

- 57,000 rows;
- 57 nominal `shot_id` values;
- 1,000 rows per nominal shot; and
- pressure-level record counts of 5, 4, 3, 10, 5, 6, 4, 4, 5, 4, and 7.

After excluding `shot_id` and hashing the complete arrays of:

- `reference_pressure_round__bar`,
- `time_index`,
- `pressure__bar`,
- `basket_pressure__bar`,
- `mass__g`, and
- `mass_flow_rate__g_per_s`,

one exact duplicate pair was found:

```text
12-8-6      SHA-256 2430b8a677bf9912e1e6b98d28fcf009aa2bce04f4c963a3bb4610b46dc3a380
12-8-6_alt  SHA-256 2430b8a677bf9912e1e6b98d28fcf009aa2bce04f4c963a3bb4610b46dc3a380
```

Every numeric value is exactly equal, with maximum absolute difference zero in every field. The generated bundle consequently assigns the pair identical per-record RMSEs:

| Record | Static | `Φ(t)` | RC-3b |
|---|---:|---:|---:|
| `12-8-6` | 0.7680 | 0.3162 | 0.1657 |
| `12-8-6_alt` | 0.7680 | 0.3162 | 0.1657 |

The `_alt` suffix suggests an alternate representation or source path, but that is an inference from naming and must not substitute for provenance. There are three possible cases:

1. **Same physical brew, alternate file/format.** Then only one experimental unit should be retained.
2. **Two physical brews accidentally collapsed during preprocessing.** Then the ingestion/processing pipeline has overwritten one trace and the original independent record must be restored.
3. **Two genuinely distinct brews that happen to have identical processed arrays.** At the stored precision and over six complete 1,000-row numeric columns, this requires an explicit provenance explanation; treating them as independent without one is not defensible.

Using the current rounded result bundle and removing one copy gives the following approximate sensitivity values:

| Summary after one duplicate removal | Static | `Φ(t)` | RC-3b |
|---|---:|---:|---:|
| Mean of 56 distinct processed-trajectory RMSEs | 0.5228 | 0.3640 | 0.5467 |
| Pooled trajectory × time RMSE | 0.5522 | 0.3939 | 0.6194 |
| 13-bar mean individual-trajectory RMSE | 0.8218 | 0.3723 | 0.2058 |

These are approximate because they are reconstructed from values rounded to four decimals in the current bundle. The aggregate ordering does not change, but the record count, weighting, 13-bar means, pooled metrics, uncertainty interpretation, and “random shot” language do change. The issue is therefore not ignorable merely because the headline order is robust.

### 5.4 Rank-transition producer bug

The observed pressure-wise winner sequence is:

```text
RC-3b, RC-3b, static, static, static, static, Φ, Φ, Φ, Φ, RC-3b
```

It contains three adjacent transitions:

1. `RC-3b → static`,
2. `static → Φ`, and
3. `Φ → RC-3b`.

The figure code correctly computes adjacent transitions. The cross-pressure analysis producer, however, returns:

```python
n_rank_changes = len(set(winners)) - 1
```

That expression yields `3 unique winners - 1 = 2`; it does not count transitions and fails whenever a winner reappears later. The correct implementation is, for example:

```python
n_rank_changes = sum(a != b for a, b in zip(winners, winners[1:]))
```

A regression test should use a re-entrant sequence such as `A, A, B, B, A`, for which `len(set)-1` gives one but the correct number of transitions is two.

This is a small numerical field but an important quality-control example: a verification manifest can confirm a number against a bundle while both preserve the same incorrect definition. Semantic and algorithmic tests are necessary in addition to claim-value matching.

---

## 6. Detailed major comments

### 6.1 P0 — Resolve the exact duplicate before treating the cross-pressure records as experimental units

**Evidence.** The repository deposit includes `12-8-6` and `12-8-6_alt` as separate IDs, but their complete processed numeric trajectories are byte-for-byte identical. They are each included in the seven-record 13-bar group and in all 57-record aggregate calculations.

**Why it matters.** The manuscript correctly insists that the shot, rather than the time sample, is the experimental unit at 9 bar. The same principle must apply cross-pressure. Two aliases or duplicated records cannot contribute two independent units. Duplication gives the 13-bar condition excess weight, understates uncertainty if record-level resampling is later used, and makes the “57 included shots” statement factually ambiguous.

**Required revision.** Trace the pair back through the source archive, ingestion manifest, raw filenames, and formatter. Record a stable source-unit identifier separate from a display `shot_id`. Then:

- deduplicate or restore the missing independent trace as appropriate;
- regenerate pressure-level means, per-record scores, macro summaries, pooled summaries, Figure 3, table values, manifest claims, and any uncertainty calculations;
- replace “57 included shots” with an accurate statement during the interim, such as “57 processed trace records, containing 56 distinct numeric trajectories pending provenance resolution”; and
- add a permanent ingestion test that hashes canonical processed arrays and fails on undeclared duplicates.

**Acceptance criterion.** A machine-readable provenance table maps every processed trace to a unique source brew/file, declares aliases explicitly, identifies the three source-reported but absent brews, and leaves no undeclared exact duplicate. All affected results are regenerated from the resolved experimental-unit table.

### 6.2 P0 — The Foster null is not “machine-only” and does not operate with “no evolving bed”

**Evidence.** The manuscript itself states that the Foster model contains ponding and a sharp wetting front advancing through an initially dry porous bed. That front changes the saturated fraction and hydraulic state of the bed over time. Yet the Abstract, Introduction, contribution statement, Results heading, Conclusions, Figure 1 caption, and alt text repeatedly call it “machine-only” or say it has “no evolving bed mechanism at all.”

**Why it matters.** The present wording collapses two distinct claims:

1. a dip-and-recovery can arise without extraction-driven changes such as swelling, fines migration, particle rearrangement, or evolving intrinsic permeability; and
2. a dip-and-recovery can arise without any evolving bed state.

The model supports the first, not the second. Wetting and infiltration are bed dynamics. Because the paper’s central theme is mechanism non-identifiability, its null taxonomy must be especially exact.

**Recommended terminology.** Use one of:

- **pump–headspace–sharp-front-infiltration null**;
- **machine–wetting null**; or
- **boundary-and-infiltration null**.

Describe its scope as:

> The model allows the wetted fraction and hydraulic path length to evolve through sharp-front infiltration, while holding the saturated-bed constitutive law free of extraction-driven swelling, fines migration, particle rearrangement, and damage-induced permeability evolution.

**Acceptance criterion.** No reader-visible or machine-generated artifact says “machine-only,” “no evolving bed,” or equivalent without immediately and accurately qualifying the evolving wetting front. Table 4 and Figure 5 distinguish saturation-front evolution from structural/constitutive evolution.

### 6.3 P0 — Correct the cross-pressure estimand in the manuscript, not only in code

**Evidence.** Manuscript lines 367–371 state that weighting pressure-level errors by shot count answers “what happens to a randomly drawn shot.” The revised code explicitly says this is wrong because:

\[
\operatorname{RMSE}(\bar Q) \ne \operatorname{mean}_i\{\operatorname{RMSE}(Q_i)\}.
\]

The same code already computes all four properly named estimands, including mean individual-record RMSE and pooled record×time RMSE.

**Why it matters.** This is not a minor wording distinction. A pressure-level mean curve has shot variability averaged out, so model errors against it are systematically optimistic relative to errors on actual shots. The Abstract says that scoring all 57 shots individually raises every branch’s error, but the body never gives the values that substantiate that statement.

**Required revision.** Replace the current two-summary paragraph with a table containing all four estimands. Title Table 3a explicitly as **pressure-level mean-curve reconstruction error**, not simply per-pressure error. State that the individual-shot values are within-campaign descriptive scores and currently depend on resolution of the duplicate pair.

**Acceptance criterion.** The main text reports 0.5271/0.3632/0.5400 as the current mean individual-record RMSEs and 0.5567/0.3927/0.6143 as pooled record×time RMSEs, or the regenerated deduplicated values. Nowhere is a weighted average of mean-curve RMSEs called a random-shot expectation.

### 6.4 P0 — Figure 4 currently reasserts the interpretation that the Results withdraw

**Evidence.** The corrected Results now say that 80 s and 40 s are the first two nonzero Fourier periods available in an 80-point series and do not establish physical timescales or distinguish drift from oscillation. The manuscript’s Figure 4 caption nevertheless reads:

> “Residual structure is slow drift … Dominant residual period: 80 s … 40 s …”

The figure code has been partly corrected, but still plots a horizontal bar labelled in seconds rather than plotting bin index or frequency. Its docstring still says the residuals “drift.” The action tracker states that the rendered figure assets have not been regenerated.

**Why it matters.** This is a direct contradiction between two reader-visible parts of the same manuscript. A peer reviewer may reasonably conclude that the authors have not decided which interpretation they endorse.

**Required revision.** Plot the actual spectral index or frequency:

- `k = 1` and `k = 2`, with the frequency resolution stated; or
- frequency in Hz, with an explicit note that resolution is `1/80 Hz`.

A period label may be included only as a parenthetical property of the analysis window, not as a measured system timescale. Remove “slow drift,” “dominant period,” and “branches differ in period.”

**Acceptance criterion.** The Results, caption, figure title, panel labels, source-data column names, SVG/PDF text, PNG, alt text, and analysis-code strings all say only that residual power is concentrated in the lowest resolvable frequency bins of the chosen window.

### 6.5 P0 — The reproducibility record is still not tied to the reviewed manuscript

**Evidence.** At snapshot `352dacd…`, the committed Paper B manifest records:

```text
source_commit:        99ea79f97894c68d53a779ab892ce7801aa7042b
git_dirty:            true
timestamp_utc:        null
bundle_source_commit: 99ea79f97894c68d53a779ab892ce7801aa7042b
release_fresh:        false
```

The action tracker says the manifest was regenerated and all claims verify, but verification against a dirty worktree and older commit is not a frozen release for the current manuscript. It also says the rendered figures were not re-emitted.

**Why it matters.** The manuscript’s numerical claims have continued to change after the recorded bundle commit. A reviewer cannot reconstruct which exact code, data, prose, and figures constitute the submitted evidence object.

**Required revision.** Build a Paper B2-specific release from a clean checkout at the final manuscript commit. Include:

- clean git status;
- exact manuscript, code, data, result-bundle, and figure hashes;
- UTC timestamp;
- environment lock or package versions;
- source and bundle commit equality;
- regenerated PNG, PDF, SVG, alt text, and source-data exports;
- full claim verification;
- a duplicate-data audit result;
- semantic/render audits; and
- tagged archival release with DOI.

**Acceptance criterion.** A reviewer can clone or download one versioned artifact, run one documented command, and reproduce the manuscript tables and figures without relying on a dirty worktree or uncommitted state.

### 6.6 P0 — Fix the rank-change field and add a definition-level test

**Evidence.** `cross_pressure_heterogeneity()` computes `n_rank_changes=len(set(winners))-1`. The figure code separately computes adjacent changes and obtains the manuscript’s stated value of three.

**Why it matters.** The bundle can contain internally inconsistent fields depending on which producer a consumer reads. The bug also reveals a gap in the test strategy: value-registration tests do not establish that a field computes the quantity named by the field.

**Required revision.** Implement adjacent-transition counting, define the quantity in a docstring, add a re-entrant-sequence unit test, and register the corrected field in the manifest.

**Acceptance criterion.** Producer, result bundle, manuscript, figure, and test all derive “three changes” from the same function and definition.

### 6.7 P0 — Narrow the statement that a figure “cannot disagree” with a verified number

**Evidence.** Manuscript lines 537–541 say that because figures are generated from the verified bundle, “a figure cannot disagree with a verified number.” The statement is too broad. A figure can reproduce a numeric value exactly while:

- calling a mean-curve RMSE an individual-shot RMSE;
- calling equilibrium-calibration withholding fully held-out temporal validation;
- plotting a Fourier-bin period as a physical timescale;
- using a stale render generated before code corrections; or
- assigning an incorrect mechanistic label.

The current paper contains examples of each class of risk.

**Required revision.** Replace the guarantee with:

> Data-bearing figure values are sourced from the verified result bundle. Estimand names, access classifications, captions, units, and rendered-asset freshness are audited separately because numeric equality alone does not establish semantic correctness.

**Acceptance criterion.** The manuscript and repository documentation clearly separate numerical claim verification, semantic-label verification, and render-freshness verification.

### 6.8 P1 — The cubic is a comparator, not a bound or floor

**Evidence.** Section 3.4 says the cubic’s purpose is “to bound what smooth temporal flexibility can achieve,” then says it is not a lower bound, and finally calls it “this floor.” Later text says it “bounds what any smooth same-trace fit can be expected to fix.” These statements are mutually inconsistent.

A degree-three polynomial is one particular four-parameter smooth function class. Higher-degree polynomials, splines, Gaussian processes, state-space smoothers, or basis expansions can fit differently. There is no theorem making this cubic a lower error bound or a universal flexibility bound.

**Required revision.** Use only:

- “same-trace four-parameter descriptive comparator”; or
- “same-trace cubic reference fit.”

State that it asks whether a low-dimensional generic time function can match or exceed the imported mechanistic trajectory on the same trace. Do not infer what “any smooth fit” could achieve.

**Acceptance criterion.** `bound`, `floor`, and `lower bound` no longer describe the cubic in the manuscript, figures, alt text, manifest, or code-generated labels.

### 6.9 P1 — RC-3b needs a reproducible methods description

**Evidence.** The manuscript says RC-3b combines the equilibrium relation with a “donor extraction trajectory,” but does not provide the donor model, equations, initialization, parameter values, unit conversions, or pressure dependence. The code calls the Cameron extraction model with fixed settings, interpolates cup mass, and passes that trajectory into `q_dynamic_from_md`.

**Why it matters.** RC-3b is a major comparator in the cross-pressure conclusions and wins at 1, 2, and 13 bar. A reader cannot currently understand why its pressure response takes that shape or reproduce it from the paper.

**Required revision.** Add a compact Methods subsection or Supplement table giving:

- donor model and citation;
- equation mapping from donor state to dissolved mass;
- dose, input mass, output mass, simulation duration, save grid, and units;
- all parameters varied with pressure and all held fixed;
- justification for transferring this donor trajectory to the Waszkiewicz campaign; and
- sensitivity to the most influential donor assumptions.

**Acceptance criterion.** A reader can reproduce RC-3b without inspecting Python source and can distinguish source-model content from Puckworks synthesis.

### 6.10 P1 — Test the observation operator, not only the scoring window

**Evidence.** The primary observable is not raw flow. It results from numerical differentiation of mass, approximately 3 s Savitzky–Golay smoothing, temporal alignment, interpolation, truncation, and pressure-level averaging. The manuscript carefully discloses this operator, which is a major improvement, but its sensitivity analyses vary the scoring window and resampling blocks rather than the operator that creates the trajectory and its residual spectrum.

**Why it matters.** Differentiation amplifies noise; smoothing imposes serial correlation and suppresses high-frequency structure; alignment and averaging strengthen a common curve. These choices can alter RMSE, residual autocorrelation, spectral power, and the apparent advantage of a smooth temporal candidate.

**Required revision.** At minimum, report a sensitivity grid for:

- Savitzky–Golay windows such as 21, 31, and 51 source samples;
- polynomial orders 1, 2, and 3 where numerically valid;
- differentiating before versus within a smoothing derivative operator;
- alternative alignment anchors;
- interpolation/grid choices; and
- individual-shot analyses before pressure-level averaging.

The purpose is not to choose the setting that makes one model win, but to show which conclusions survive a defensible preprocessing range.

**Acceptance criterion.** The static-versus-temporal separation and the low-frequency residual statement are reported across the operator sensitivity grid, with any reversals disclosed.

### 6.11 P1 — Refine statistical language and branch-specific fitting statements

**Evidence.** Section 4.2a says each branch is rescored per shot while “re-optimizing each branch’s own free parameters within each unit.” In practice, the constant and cubic are refitted; the static and `Φ(t)` branches retain upstream/campaign calibration. The term “exact randomization test” may also be read as design-based randomization even though no treatment was randomized.

**Required revision.** State the branch-specific operation explicitly:

- best constant: refitted to each shot;
- cubic: refitted to each shot;
- static poroelastic: no shot-specific refit; imported equilibrium calibration;
- empirical `Φ(t)`: no shot-specific flow-trace fit; imported equilibrium and dissolved-mass trajectory, with partial target access;
- other-four spline: trained only on the other four shots.

Call the test an **exact two-sided sign-flip enumeration under a conditional sign-symmetry null**. Keep the five-unit percentile bootstrap supplementary or remove it; it should not share equal inferential prominence with the exact enumeration.

**Acceptance criterion.** A reader can identify, for every score, which data were used to fit, tune, select, or construct every branch.

### 6.12 P1 — Complete the campaign provenance accounting

The current paper has three counts:

- 60 brews reported for the source campaign;
- 57 processed trace records in the repository deposit; and
- 56 distinct processed numeric trajectories after exact-hash deduplication.

The code says the three source-side exclusions are not identified. This is transparent but incomplete. The paper should not use “57 shots” without qualification until source-unit provenance is resolved.

**Required revision.** Add a supplementary inventory with one row per source brew and fields for source identifier, nominal pressure, source file, processing outcome, inclusion/exclusion reason, processed ID, alias/duplicate relationship, and final analysis-unit ID.

**Acceptance criterion.** All source-reported brews are accounted for, and the analysis-unit count follows from the inventory rather than from counting filenames or IDs.

### 6.13 P1 — Keep the spectral analysis descriptive unless it is redesigned

The corrected Results language is much better, but two claims still go beyond the diagnostic:

- “power in the lowest-frequency quarter” depends on an arbitrary division of a short spectrum; and
- saying low-frequency structure “bounds what any smooth same-trace fit can be expected to fix” is unsupported.

A more complete spectral analysis would need clear detrending, tapering/window choice, leakage assessment, null simulations accounting for the smoothing operator, and raw-shot replication. Even then, the result would describe a residual timescale distribution, not identify its physical source.

**Recommended wording.** “All tested branches leave serially dependent residuals, and most residual spectral power lies in the lowest available frequency bins on this processed 80 s window.”

**Acceptance criterion.** No physical process, drift timescale, periodicity, or universal fitting limit is inferred from the current spectrum.

### 6.14 P1 — The semantic audit should cover the actual submitted artifacts

The action tracker deserves credit for mutation-testing and strengthening the semantic audit after finding that its earlier green result was vacuous. However, visible stale phrases remain in:

- manuscript Figure 4 caption;
- Figure 1 caption;
- figure-code docstrings and labels;
- Figure 3 “held out” legend;
- alt text (“in-sample flexibility bound,” “leave-one-pressure-out held-out errors,” “no evolving bed mechanism”); and
- unregenerated rendered figure assets.

This suggests that the audit’s scope is still not identical to the reader’s submission surface.

**Required revision.** Test exact assertion classes rather than broad banned words. Include:

- manuscript body and figure-caption section;
- alt text;
- code string literals that become titles, labels, legends, or notes;
- exported SVG/PDF text extraction;
- source-data headers;
- result-bundle field descriptions; and
- render hashes tied to the final source and bundle.

**Acceptance criterion.** Deliberately reintroducing each withdrawn claim into any reader-visible surface causes the audit to fail, and the final render is generated after the last semantic change.

### 6.15 P1/P2 — Streamline the manuscript into a journal article rather than a repository audit log

The paper’s unusual transparency is a strength, but the current draft is approximately 11,000 words and sometimes reads as a response-to-review ledger. The long source-observable autopsy, detailed repository internals, repeated caveats, producer names, and manifest mechanics obscure the scientific narrative.

A stronger main article would preserve the core inferential hierarchy:

1. one integrated curve can have multiple explanations;
2. the Foster infiltration model demonstrates shape non-uniqueness;
3. the 9-bar static-to-temporal ladder establishes a large model-relative reconstruction gap;
4. shot-level and other-shot analyses limit predictive/mechanistic interpretation;
5. pressure dependence further prevents a universal branch claim; and
6. interventions are required for identification.

Move audit mechanics, full per-shot tables, preprocessing sensitivities, release metadata, and detailed provenance to a reproducibility supplement.

---

## 7. Figure-by-figure review

### Figure 1 — Machine-side non-uniqueness

**Keep:** The separation between the Foster published-model object and the Waszkiewicz measured object is excellent and prevents accidental cross-calibration claims.

**Revise:**

- Change “machine-side” to “machine–wetting” or “pump–headspace–infiltration.”
- Replace “no evolving bed mechanism” with “without extraction-driven evolution of saturated-bed constitutive properties.”
- State explicitly that the wetted length/front evolves.
- Ensure the schematic visually marks the porous bed and wetting front as part of the dynamic subsystem rather than as a static appendage.

### Figure 2 — Null-first temporal ladder

**Keep:** Showing coefficients fitted to the scored trace is useful.

**Revise:**

- Remove “flexibility bound” from alt text and any render; use “same-trace cubic comparator.”
- Make access class as visible as free-parameter count. “Zero coefficients fitted to this trace” is not equivalent to held-out.
- Clarify in panel (c) whether the band is pointwise between-shot SD, SEM, or another dispersion object.
- State that moving-block intervals in panel (d) condition on fixed predictions and are secondary within-curve sensitivities.

### Figure 3 — Cross-pressure assessment

**Keep:** Per-pressure ranks are much more informative than the aggregate alone.

**Revise:**

- Title panel (a) “pressure-level mean-curve RMSE,” not generic per-pressure RMSE.
- Resolve the duplicate before reporting 13-bar `n=7`.
- Generate “three changes” from the corrected shared producer rather than a separate figure-only calculation.
- Replace panel (b) legend “leave-one-pressure-out (held out)” with “equilibrium-calibration point omitted (LOPO-EC).”
- Add, either in Figure 3 or a companion table, mean individual-shot and pooled shot×time RMSEs.
- Consider removing the shaded 7–11 bar band, which visually suggests a prespecified regime even though the prose says no regime is inferred.

### Figure 4 — Residual structure

**Blocking revision required.** The current caption contradicts the Results. Use bin index or frequency, not a bar chart of “periods.” A suitable title is:

> **Low-frequency residual structure on the 80 s analysis window.**

Panel (c) could simply display `peak bin k` with values 1 or 2, accompanied by the window’s frequency resolution. Do not call the result drift or assign physical timescales.

### Figure 5 — Mechanism-by-perturbation matrix

**Keep:** The move from curve fitting to discriminating intervention is the paper’s most useful practical contribution.

**Revise:**

- Label every cell as a hypothesis conditional on apparatus, control mode, and model assumptions.
- Correct the machine/wetting row to acknowledge an evolving wetting front.
- Avoid “the one column where candidates differ in sign” unless every sign follows analytically under clearly stated shared conditions.
- Consider moving the full matrix to the supplement and retaining a smaller decision tree in the main text.

---

## 8. Section-by-section comments

### Title

The title is thoughtful and accurately signals non-identifiability. It also includes “espresso,” which is important for discoverability. No title change is required. A slightly more explicit alternative would be:

> **One espresso flow curve, many explanations: null-first tests of machine, wetting, and porous-bed dynamics**

### Abstract, line 11

The abstract is scientifically rich but too long and carries too many numerical and access-provenance qualifications for most journals. Correct the Foster claim, retain the core ladder, retain the shot-level/other-shot limitation, and report the real individual-shot cross-pressure result only after duplicate resolution.

### Introduction, lines 21–25

Replace “machine-only” throughout. “Null-first” remains a strong organizing idea, but the “simplest model class” should be defined relative to the observable and question; the Foster branch is not the simplest purely machine model because it includes porous-bed infiltration.

### Data, line 41

This paragraph is close to correct already because it acknowledges the moving sharp wetting front and fixed permeability. The final question should ask whether a **machine–infiltration subsystem** can generate a dip without extraction-driven constitutive evolution, not whether a machine alone can.

### Methods §3.4, lines 108–115

Correct the malformed LaTeX. Remove all bound/floor language. The paragraph should explain that the cubic is intentionally same-trace and non-predictive, used only to show that low RMSE does not confer mechanistic identification.

### Methods §3.5, lines 116–118

Expand RC-3b. “Project synthesis” is candid but insufficient for a scientific Methods section. Add the donor model and parameterization explicitly.

### Statistical analysis §4.2a, lines 161–169

This is now one of the strongest sections. Amend “re-optimizing each branch” to a branch-specific statement. Consider replacing “randomization” with “sign-flip enumeration.” Keep the exact attainable p-value explanation.

### Cross-pressure §5.3a, lines 330–371

The pressure-specific table is useful. Correct three points:

1. label every score as pressure-level mean-curve RMSE;
2. resolve the duplicated 13-bar trace; and
3. replace the false random-shot interpretation with all four estimands.

The prose at lines 357–365 appropriately avoids inferring regimes. The shaded band in Figure 3 should follow that same restraint.

### Pressure domains §5.3b

This section is valuable. Check whether statements about how many conditions reach `P_c` use nominal settings or recorded basket pressure. Since the constitutive equation consumes a specific pressure variable, the domain count should use that same variable or state both counts.

### Results residual-spectrum section

The retraction of physical 80 s/40 s interpretations is correct and should be retained. Remove remaining claims that the spectrum “bounds” smooth fitting. Describe the analysis as a processed-window residual diagnostic.

### Discussion §7.1

“Temporal flexibility is required relative to those nulls” is defensible. Keep “relative to those nulls” in the same sentence every time. Add “under the declared observation operator” at least once.

### Discussion §7.2

This is now appropriately skeptical of `Φ(t)` as a predictive closure. Replace any residual “cubic bound” wording. The claim that the repeatable common shape explains reconstruction quality is plausible but should be described as an inference supported by the other-four template, not as uniquely established.

### Limitations §8

Add two new limitations:

- cross-pressure record provenance is incomplete and presently contains one exact duplicate processed trajectory; and
- the primary observable and residual spectrum depend on a derivative/smoothing/alignment operator whose sensitivity has not yet been fully quantified.

### Conclusions §9

Correct “without bed evolution.” A defensible replacement is “with evolving wetting but without extraction-driven evolution of saturated-bed constitutive properties.” Avoid implying that all temporal explanations are internal bed mechanisms.

### Data and code availability

Once the release is frozen, replace future-tense instructions with an exact version, tag, DOI, commit, environment, and one-command reproduction entry point.

### Figures preamble, lines 537–541

Narrow the verification guarantee as specified in §6.7. A claim-verified number and a semantically correct figure are related but separate quality gates.

---

## 9. Suggested replacement text

### 9.1 Replacement Foster sentence for the Abstract

> A published pump–headspace–sharp-front-infiltration model first shows that a mid-shot flow minimum can arise with an evolving wetting front but without extraction-driven swelling, fines migration, particle rearrangement, or evolving saturated-bed permeability.

### 9.2 Replacement null-first paragraph for the Introduction

> The present study adopts a null-first strategy. A candidate bed mechanism should first be compared with the least elaborate coupled system capable of expressing the observable. If pump, headspace, pressure-boundary, and wetting-front dynamics can generate the shape without extraction-driven evolution of saturated-bed constitutive properties, the shape is not uniquely attributable to swelling, fines migration, rearrangement, or dissolution. If tested time-invariant branches leave a large coherent residual but time-varying branches reduce it, the evidence supports temporal flexibility relative to those branches. If a generic same-trace function performs as well as a named trajectory, reconstruction quality alone does not identify that trajectory’s mechanism.

### 9.3 Replacement §3.4 cubic paragraph

> A degree-three polynomial in time, `Q_cub(t)=a0+a1t+a2t²+a3t³`, is fitted and scored on the same interval. It has no bed-mechanism interpretation and no held-out status. It is used as a four-parameter same-trace descriptive comparator: if a generic low-dimensional time function reconstructs the trajectory as well as the imported mechanistic candidate, low in-sample RMSE cannot identify the named mechanism. The cubic is neither a predictive challenger nor a mathematical lower bound on the error attainable by other smooth functions.

### 9.4 Replacement cross-pressure estimand paragraph

> Cross-pressure performance depends on both the response object and the weighting scheme. Equal weighting of the eleven pressure-level mean curves gives mean RMSEs of 0.5239, 0.3345, and 0.5098 g s⁻¹ for the static, `Φ(t)`, and RC-3b branches. Weighting those same mean-curve RMSEs by the number of deposited records gives 0.5094, 0.3431, and 0.5300 g s⁻¹; this remains an average of mean-curve errors and is not the expected error for a randomly selected shot. Scoring the 57 deposited records individually gives current mean RMSEs of 0.5271, 0.3632, and 0.5400 g s⁻¹, while pooling all record–time residuals gives 0.5567, 0.3927, and 0.6143 g s⁻¹. These record-level values will be regenerated after resolution of one exact duplicate processed trajectory in the 13-bar group.

### 9.5 Interim duplicate/provenance disclosure

> The source campaign is described as 60 brews. The repository currently contains 57 processed trace records, but canonical hashing identifies `12-8-6` and `12-8-6_alt` as exactly identical across all stored numeric fields and time rows. Pending source-provenance resolution, the deposit therefore contains at most 56 distinct processed trajectories. Cross-pressure record-level summaries are reported as provisional and will be regenerated after the pair is classified as a source alias, processing collision, or documented pair of distinct physical brews.

### 9.6 Replacement Figure 4 caption

> **Figure 4. Low-frequency residual structure on the 80 s analysis window.** (a) Residual autocorrelation across twenty one-second lags. (b) Fraction of spectral power in the lowest-frequency quarter of the available discrete Fourier bins. (c) Index of the largest nonzero-frequency bin. The static branches peak at the first nonzero bin and the temporal branches at the second. Because an 80-point one-second series has frequency resolution 1/80 Hz, these correspond mechanically to 80 s and 40 s window periods; they are not measured physical timescales and do not distinguish drift from oscillation. The result shows coherent low-frequency lack of fit only.

### 9.7 Replacement figure-verification statement

> Data-bearing figure values are read from the same result bundle used by the numerical claim verifier. Numeric agreement does not by itself guarantee that an estimand, access class, unit, caption, or physical interpretation is correct, so semantic labels and rendered-asset freshness are audited separately. Final raster and vector figures, source-data tables, and text alternatives are regenerated and hashed in the release manifest.

### 9.8 Suggested shorter Abstract

> Time-resolved espresso outlet flow integrates machine response, pressure boundaries, wetting, porous-bed resistance, extraction, and measurement processing; similar curve shapes therefore need not imply the same mechanism. We apply a null-first comparison to ask whether specified time-invariant branches can reconstruct a published flow trajectory and whether improved temporal reconstruction identifies a bed process. A pump–headspace–sharp-front-infiltration model shows that a mid-shot minimum can arise with evolving wetting but without extraction-driven swelling, fines migration, rearrangement, or changing saturated-bed permeability. For the differentiated, approximately 3 s-smoothed mean of five nominal 9-bar brews over 15–95 s, the best constant and static poroelastic branches have RMSEs of 0.573 and 0.648 g s⁻¹. A partly target-informed dissolution-linked `Φ(t)` trajectory gives 0.116 g s⁻¹, while a four-parameter cubic fitted and scored on the same trace gives 0.096 g s⁻¹. Across the five individual brews, `Φ(t)` improves on both time-invariant branches, but a fully held-out empirical template learned from the other four brews predicts the omitted brew as well as `Φ(t)`. Branch ranking also varies across pressure. The data therefore support time-varying prediction relative to the tested time-invariant branches, but do not identify the responsible mechanism. Pressure steps, reversal, spent-puck rebrewing, and spatial state measurements offer more discriminating tests than further flexible fits to the same outlet curve.

---

## 10. Recommended revised manuscript structure

A more concise submission could use the following structure:

1. **Introduction**
   - Integrated observables and mechanism non-identifiability
   - Null-first inference
   - Scoped questions and claims
2. **Evidence objects and observation operator**
   - Foster model output
   - Waszkiewicz source campaign and processed trace records
   - Explicit 60/57/56 provenance accounting
   - Differentiation, smoothing, alignment, interpolation, and averaging
3. **Models and access classes**
   - Pump–headspace–infiltration null
   - Best constant and static poroelastic nulls
   - Empirical `Φ(t)` candidate
   - Same-trace cubic comparator
   - RC-3b donor branch
   - Dependency/access graph
4. **Analysis design**
   - Primary 9-bar mean-curve ladder
   - Five-shot paired analysis
   - Fully held-out other-shot empirical template
   - Cross-pressure estimands
   - Residual diagnostics
   - Preprocessing sensitivity
5. **Results**
   - Shape non-uniqueness
   - Static-to-temporal gap
   - Shot-level effect sizes and attainable inference
   - No predictive advantage over other-shot template
   - Pressure-specific rank variation
   - Descriptive low-frequency residual structure
6. **Discriminating experiments**
7. **Discussion and limitations**
8. **Conclusions**

Move the following to a supplement:

- detailed source-observable autopsy;
- full per-shot and per-pressure tables;
- all preprocessing and scoring-window sensitivity;
- block-resampling details;
- RC-3b parameter inventory;
- spectral implementation details;
- duplicate/provenance inventory;
- evidence-manifest schema and claim registry; and
- complete perturbation matrix.

---

## 11. Reproducibility and release checklist

The final Paper B2 release should not be approved until all items below pass.

### Source and provenance

- [ ] Final manuscript commit identified.
- [ ] Clean worktree: `git_dirty=false`.
- [ ] Source commit, result-bundle commit, and manuscript commit match.
- [ ] UTC build timestamp recorded.
- [ ] Environment locked or fully enumerated.
- [ ] Every source brew is represented in a provenance inventory.
- [ ] The three source-reported but absent brews are identified or explicitly documented as unknowable from the released source.
- [ ] Exact and near-duplicate trace audit passes or all declared aliases are documented.

### Analysis

- [ ] Correct adjacent rank-transition count.
- [ ] Four cross-pressure estimands generated at full internal precision.
- [ ] No averaging of already rounded per-record RMSEs.
- [ ] Duplicate-resolved pressure-level and record-level summaries regenerated.
- [ ] RC-3b equations and parameters documented.
- [ ] Observation-operator sensitivity completed.
- [ ] Spectral analysis labelled as descriptive window-bin evidence.
- [ ] Branch-specific fitting/access path recorded for every result.

### Manuscript semantics

- [ ] No unqualified “machine-only” or “no evolving bed” Foster claim.
- [ ] No cubic “bound” or “floor.”
- [ ] No weighted mean-curve statistic called a random-shot expectation.
- [ ] No LOPO-EC result called fully held-out temporal validation.
- [ ] No 80 s/40 s value called a physical period or drift timescale.
- [ ] “Time-varying required” always remains relative to tested branches and the declared observable.

### Figures and artifacts

- [ ] All figures regenerated after final code and wording changes.
- [ ] PNG, PDF, and SVG hashes recorded.
- [ ] Extracted SVG/PDF text passes semantic audit.
- [ ] Source-data headers use correct estimand names.
- [ ] Alt text matches the final caption and render.
- [ ] No stale cached figure remains in the submission package.

### Verification and archive

- [ ] All registered numerical claims pass.
- [ ] Definition-level unit tests pass, including re-entrant rank transitions.
- [ ] Semantic audit is mutation-tested against every withdrawn claim class.
- [ ] Render-freshness check passes.
- [ ] Release manifest reports `release_fresh=true`.
- [ ] Tagged archive and DOI created.
- [ ] One-command reproduction instructions tested from a clean environment.

---

## 12. Recommended order of work

1. **Resolve the duplicate provenance first.** Every cross-pressure record count and aggregate should be treated as provisional until this is settled.
2. **Correct the Foster taxonomy and cubic terminology repository-wide.** These are conceptual definitions that should propagate into all surfaces before figures are regenerated.
3. **Synchronize the cross-pressure manuscript with the already-corrected analysis estimands.** Fix the rank-transition producer at the same time.
4. **Redesign and regenerate Figure 4.** Then regenerate all five figures and exports from the corrected final bundle.
5. **Add the observation-operator sensitivity and RC-3b documentation.** Decide whether either changes the main claims.
6. **Shorten and reorganize the manuscript.** Move audit mechanics to a supplement and add methodological citations.
7. **Create the clean, commit-matched release last.** Do not regenerate the final manifest before all prose, code, data, and figures are frozen.

---

## 13. Final verdict

The manuscript’s central scientific contribution is now clear and worthwhile: **a large reduction in espresso-flow reconstruction error can establish the need for temporal flexibility relative to specified time-invariant branches without identifying a unique porous-bed mechanism.** The current 9-bar numerical ladder supports that conclusion, and the addition of shot-level, other-shot, cross-pressure, and parameter-access analyses has made the paper much more rigorous.

The remaining blockers are concrete rather than philosophical. The authors must resolve one exact duplicate experimental record, classify the Foster model as a machine–wetting/infiltration null rather than a no-bed-evolution model, report the correct cross-pressure estimands, remove the residual-period contradiction, fix the rank-transition producer, narrow the artifact-verification claim, and freeze a clean release. These changes are necessary for the paper’s methods and reproducibility message to be credible on its own terms.

After those corrections—and after a concise journal-editing pass—the paper should be suitable for serious external review. I would encourage revision rather than abandonment: the core result is reproducible, the null-first framework is useful well beyond espresso, and the manuscript is now close enough that a disciplined final integration pass should yield a defensible submission.
