# Paper 1 — Detailed Review, Round 7

**Review target:** commit `5db834b12ef25970be9bc27971263fff31b49e51`  
**Primary manuscript:** `docs/submission/PAPER_A_JFE_MANUSCRIPT.md`  
**Supplement:** `docs/submission/PAPER_A_JFE_SUPPLEMENT.md`  
**Figures and captions:** `docs/submission/figures/`, `docs/figures/paper_a/`, and `docs/figures/PAPER_A_CAPTIONS.md`  
**Review brief:** `docs/paper1_resource/PAPER_1_REVIEW_BRIEF_ROUND_7.md`

## Executive verdict

**Not ready for submission.**

The manuscript is substantially stronger than a typical working paper in its explicit separation of parameter localization, absolute prediction error, benchmark skill, and evidence tier. Its central scientific interpretation may survive correction. However, the reviewed commit contains **three submission-blocking defects**:

1. the manuscript still states a Reynolds-number equation that differs from the source MATLAB and the executable port by approximately \( \alpha_l^{-2} \), or about **34.6×** at the stated porosity;
2. the central 38/40/42 endpoint analyses are repeatedly labelled as **mL volume endpoints**, although the producer stops at **mass-equivalent 38/40/42 g endpoints** under the settled source-flow convention; and
3. the headline transfer benchmark silently excludes all coarse- and fine-grind off-grid records while Table 1 says the coarse/fine corpus is held out in its entirety.

The third defect requires either a rerun on the complete coarse/fine corpus or a clearly pre-specified matched-grid estimand plus a separate off-grid sensitivity. The first two appear primarily to require correction of the scientific contract, terminology, generated tables, captions, and figures rather than a slow numerical rerun, provided the executable code is not changed.

I identified **one confirmed stale-number defect**, but it is in the repository’s required claim-binding audit rather than in a scientific result: the audit committed with the review target still reports the earlier `65/436` and `60/77` coverage state from commit `fc61c46`, whereas the Round 7 brief reports `166/441` and `66/77`. I did **not** confirm a stale numerical result in the manuscript itself. Several numerical values are correctly reproduced but attached to the wrong unit, estimand, corpus description, or assurance claim.

### Finding count

| Priority | Count | Submission effect |
|---|---:|---|
| **P0 — submission-blocking** | **3** | Must be resolved before journal submission |
| **P1 — major** | **6** | Must be resolved or explicitly adjudicated before submission |
| **P2 — editorial/scoping** | **4** | Correct during the same revision |
| **Confirmed stale-number findings** | **1** | Supporting audit counts, not a manuscript result |

---

## Scope and method

The review followed the Round 7 brief’s requested emphasis:

- claims whose evidence is weaker than the prose implies;
- corpus descriptions contradicted by the committed corpus;
- estimands named as one quantity but computed as another;
- prose–implementation mismatches;
- adequacy and naming of the level-only comparator;
- identifiability framing;
- endpoint treatment; and
- consistency of the claim-binding assurance layer.

I inspected the exact target manuscript, supplement, figure bundle, captions, solver-contract audit, claim-binding audit, relevant executable model and analysis code, and the Angeloni bioactives corpus. The most important implementation locations were:

- `puckworks/models/pannusch2024/solver.py`
  - `simulate_fractions`
- `puckworks/models/pannusch2024/closures.py`
  - `sherwood_h`
- `puckworks/validation/slow/angeloni_bracket.py`
  - `_matched_bounds`
  - `_profile_objectives`
  - `paired_clustered_bootstrap`
  - `transfer_skill_vs_baselines`
- `puckworks/data/angeloni2023/bioactives.csv`
- `docs/paper1_resource/PAPER_A_SOLVER_CONTRACT_AUDIT.json`
- `docs/CLAIM_BINDING_AUDIT_2026-07-28.md`

A full repository checkout was not available in the execution environment because outbound repository download failed at DNS resolution. I therefore did not claim to have run the three commands listed in the brief. The findings below are based on direct, commit-pinned source inspection. The P0 findings are textual or semantic contradictions visible without recomputation.

---

# P0 — Submission-blocking findings

## P0-1. The manuscript still states the wrong Reynolds-number definition

### Finding

Section 2.1 defines the liquid interstitial velocity as

\[
v_l = \frac{Q}{A_{cs}\alpha_l}
\]

and then gives

\[
Re = \frac{d_{32}v_l\rho}{\alpha_l\eta}.
\]

Together, those equations imply

\[
Re_{\mathrm{manuscript}}
=
\frac{d_{32}Q\rho}{A_{cs}\alpha_l^2\eta}.
\]

The executable source contract is different. In `solver.py`, `q` is the **superficial** velocity and the transport velocity is set to `q / ALPHA_L`. In `closures.py`, `sherwood_h` calculates

\[
Re_{\mathrm{code}}
=
\frac{d_{32}q\rho}{\eta},
\]

with no additional porosity divisor. The repository’s own solver-contract audit reaches the same conclusion and records that the original MATLAB uses superficial velocity.

At \(\alpha_l=0.17\),

\[
\frac{Re_{\mathrm{manuscript}}}{Re_{\mathrm{code}}}
=
\alpha_l^{-2}
\approx 34.6.
\]

This is not a harmless notation choice. The governing-equation section currently states a materially different constitutive model from the one that generated the results.

### Evidence relied on

- `docs/submission/PAPER_A_JFE_MANUSCRIPT.md`, §2.1:
  - definition of \(v_l\);
  - displayed Reynolds equation.
- `puckworks/models/pannusch2024/solver.py`, `simulate_fractions`:
  - `q = ...  # superficial velocity`;
  - `v_l = q / ALPHA_L`.
- `puckworks/models/pannusch2024/closures.py`, `sherwood_h`:
  - `Re = d32 * q / kin_vis`.
- `docs/paper1_resource/PAPER_A_SOLVER_CONTRACT_AUDIT.json`:
  - source MATLAB and port both use superficial velocity;
  - the documentation equation was the discrepant item.

### Why this matters

The manuscript’s scientific object is the executable model. A reader attempting to reproduce the paper from the displayed equations would use a Sherwood correlation with a Reynolds number approximately 34.6 times larger than the one used in the archived analyses. Because the rate multiplier acts on the Sherwood prefactors, the numerical fit may partially absorb this scaling, but that does not make the stated model correct.

This defect is especially important because the Round 7 brief says the documentation equation had already been corrected. The correction did not propagate to the reviewed manuscript, and the assurance process did not detect the reappearance.

### Minimum acceptance criterion

1. Replace the Reynolds definition everywhere with the executable/source convention:
   \[
   u_s=Q/A_{cs}, \qquad
   Re=d_{32}u_s\rho/\eta.
   \]
2. If the interstitial velocity is retained in the notation, use the algebraically equivalent form:
   \[
   Re=d_{32}\alpha_l v_l\rho/\eta.
   \]
3. Correct the corresponding model card and any generated equation summaries.
4. Add a contract test or generated model-definition block that binds:
   - superficial velocity;
   - interstitial velocity;
   - Reynolds number; and
   - the porosity factor.
5. Confirm that no executable line was changed. If only documentation is corrected, the slow numerical analyses do not need to be rerun; the paper package still needs a complete consistency regeneration.

### Stale-number status

**No stale scientific result identified.** This is a stale or incompletely propagated **model-contract statement**, not a stale reported result.

---

## P0-2. The central endpoint estimand is mass-based, but the manuscript, supplement, captions, and figures label it as volume-based

### Finding

The manuscript repeatedly describes the Angeloni comparison as a 40 mL matched-volume proxy for a reported 40 g cup and describes the endpoint sweep as 38/40/42 mL. That description conflicts with the settled source-flow contract and the actual producer.

The relevant producer defines `_matched_bounds(flow, target)` as

\[
t_{\mathrm{end}}=\frac{\text{target}}{\text{flow}}.
\]

The source flow column is numerically consumed as **mass flow in g s\(^{-1}\)**, despite its published `mL/s` label. Consequently, passing targets 38, 40, and 42 to `_matched_bounds` stops the simulated shot at **38, 40, and 42 g**, respectively. The solver then uses density when converting that mass flow to superficial volumetric velocity and when forming the liquid-volume accumulator.

The Round 7 brief explicitly states the resulting contract: the modelled endpoint is already mass-based. The figure-bundle README likewise says the transfer figure is rendered at matched 40 g cups. Yet the manuscript, supplementary methods and tables, figure captions, and Figure 3 itself still carry the retired “40 mL matched-volume proxy” narrative.

This is an estimand-label failure of exactly the kind the brief asks the reviewer to find.

### Evidence relied on

- `docs/paper1_resource/PAPER_A_SOLVER_CONTRACT_AUDIT.json`:
  - source and port divide the source flow by density;
  - source consumes the published flow number as mass flow;
  - the collection contract is mass-equivalent.
- `puckworks/validation/slow/angeloni_bracket.py`:
  - `_V_TARGET_ML = 40.0`;
  - `_matched_bounds` returns `target / flow`;
  - the docstring itself calls this a matched-mass cup.
- `puckworks/models/pannusch2024/solver.py`:
  - source flow is converted through density to superficial velocity;
  - concentration averaging uses the liquid-volume accumulator.
- `docs/submission/PAPER_A_JFE_MANUSCRIPT.md`:
  - abstract;
  - Table 2;
  - §§2.3–2.4;
  - §§3–4;
  - Table 4a;
  - limitations.
- `docs/submission/PAPER_A_JFE_SUPPLEMENT.md`:
  - Supplementary Methods S2;
  - Table S3;
  - supplementary figure captions.
- `docs/figures/PAPER_A_CAPTIONS.md`.
- `docs/figures/paper_a/README.md`:
  - says the corrected figure bundle is matched-mass and Figure 3 is at 40 g.
- `docs/figures/paper_a/fig4_transfer.png`:
  - embedded title still says 40 mL matched-volume proxy.

### Why this matters

The manuscript currently interprets a mass-endpoint sensitivity as a mass-to-volume substitution sensitivity. That changes the meaning of:

- the abstract;
- the endpoint contract;
- the stated limitation;
- the 38/40/42 sweep;
- the claim that the exact residual carries “mass-to-volume” uncertainty;
- all endpoint table headings;
- all endpoint figure labels; and
- the conclusion’s caveat.

The current numerical values appear to be values for the intended mass endpoints. The error is therefore principally semantic and contractual, but it is pervasive and central.

### Minimum acceptance criterion

1. Rename the producer-level target from `_V_TARGET_ML` to a mass-explicit name such as `_M_TARGET_G`.
2. Rename or wrap the source-flow argument so that the implementation makes clear that:
   - the source column is labelled volumetric;
   - the source code consumes it as mass flow;
   - source fidelity is being preserved.
3. Rewrite the endpoint contract in §2.4:
   - Angeloni target: 40 ± 2 g;
   - evaluated targets: 38, 40, and 42 g;
   - density is used to derive liquid velocity and concentration-volume averaging, not to turn the stopping rule into a volume target.
4. Remove the “matched-volume proxy” and “mass-to-volume substitution” narrative from:
   - abstract;
   - Table 2;
   - §§2.3–2.4;
   - §§3–4;
   - Table 4a;
   - limitations and conclusions;
   - Supplementary Methods S2 and Table S3;
   - all captions; and
   - text embedded in figures.
5. Regenerate Figure 3 and any other endpoint-labelled figure from a typed unit/estimand field rather than hand-authored labels.
6. Add a semantic contract test that checks the target’s name, unit, stopping equation, table headings, captions, and figure metadata together.
7. Do not rerun the slow analyses solely to change the label, unless inspection shows that any producer actually used a volumetric target rather than `_matched_bounds(target / source-flow)`.

### Stale-number status

**No stale numerical result confirmed.** The values appear to be current, but their **units and estimand labels are wrong**. The token “40” is numerically unchanged while its scientific meaning changes from mL to g.

---

## P0-3. The headline transfer benchmark excludes eight available coarse/fine records, contrary to the manuscript’s corpus claim

### Finding

The Angeloni file contains 66 condition-level records:

- 22 optimal-grind records;
- 22 coarse-grind records; and
- 22 fine-grind records.

The file explicitly identifies 12 off-grid validation records, four per grind. For the two held-out grinds, the available off-grid records are:

- Arabica coarse: A21, A22;
- Arabica fine: A32, A33;
- Robusta coarse: R21, R22;
- Robusta fine: R32, R33.

The headline transfer function filters **every grind**, including C and F, to `on_grid == "True"`. It therefore evaluates:

\[
2\ \text{varieties}
\times
2\ \text{held-out grinds}
\times
9\ \text{on-grid conditions}
\times
3\ \text{solutes}
=
108
\]

named-solute observations.

The complete coarse/fine corpus contains:

\[
44\ \text{C/F records}
\times
3\ \text{solutes}
=
132
\]

named-solute observations. The benchmark therefore excludes 24 available observations arising from eight C/F records.

Table 1 gives the 108 count but says the coarse/fine corpus is held out as “all of it.” The dataset section also describes the 66-record corpus as a 3×3×3 grid “plus off-grid points” without later disclosing that every off-grid C/F point is omitted from the principal transfer result.

The 108 count is arithmetically correct for the selected subset; the corpus and estimand description are not.

### Evidence relied on

- `puckworks/data/angeloni2023/bioactives.csv`:
  - 66 total records;
  - comment defining 12 off-grid validation points;
  - eight C/F off-grid records listed above.
- `puckworks/validation/slow/angeloni_bracket.py`, `transfer_skill_vs_baselines`:
  - helper `sh(variety, gran)` filters `on_grid == "True"` for O, C, and F.
- `docs/submission/PAPER_A_JFE_MANUSCRIPT.md`:
  - §2.2 describes 66 records and off-grid points;
  - Table 1 gives 108 C/F points and says “all of it”;
  - §4 describes 108 held-out points as the transfer corpus.

### Why this matters

This is not merely a documentation detail. The omitted points are identified in the corpus as validation points and lie away from the 3×3 training grid. They are directly relevant to the paper’s claim about transfer across operating conditions and grind. Their inclusion may change:

- model and comparator MAPE;
- the paired difference;
- the number of points on which the mechanistic model is worse;
- the resampling range;
- per-group conclusions; and
- the relative performance of the same-\((T,p)\) lookup, which cannot be defined for every unmatched off-grid condition.

Because the headline advantage is only about 0.36 percentage points and the primary range touches zero, an undisclosed corpus change of 24 observations cannot be assumed immaterial.

### Minimum acceptance criterion

Choose and pre-specify one of the following defensible contracts.

**Option A — complete-corpus headline**

1. Fit on the declared optimal-grind training set.
2. Evaluate the mechanistic model and level-only comparator on all 44 C/F records, giving 132 named-solute observations.
3. Redesign the cluster resampling for the actual condition structure.
4. Treat the same-\((T,p)\) lookup as a secondary comparator limited to the matched-grid subset.
5. Regenerate all result tables, captions, figures, binding records, and prose.

**Option B — matched-grid headline plus mandatory off-grid sensitivity**

1. Rename the primary estimand explicitly as the “matched 3×3 on-grid C/F transfer benchmark.”
2. Replace “all of it” with “all on-grid C/F records.”
3. Add a record-level inclusion/exclusion manifest.
4. Report the eight C/F off-grid records as a separate extrapolation/validation sensitivity using the mechanistic model and level-only comparator.
5. State why a matched-grid estimand is primary and how the off-grid result affects the conclusion.

Under either option, the analysis artifact should emit the exact included sample IDs so that corpus membership is bound, not inferred from prose.

### Stale-number status

**No.** The value 108 is correct for the currently implemented subset. The defect is an undisclosed exclusion and a false corpus-coverage claim.

---

# P1 — Major findings

## P1-1. The primary resampling does not preserve the shared condition structure across solutes

### Finding

The manuscript correctly recognises that the 108 observations are dependent because C and F are paired and multiple solutes are observed under shared temperature–pressure conditions. However, the primary resampling implementation clusters by `group = variety:solute` and then independently resamples \((T,p)\) conditions inside each group.

This keeps C and F together for a given solute, but it can select different conditions for caffeine, trigonelline, and 5-CQA within the same variety in a bootstrap draw. It therefore breaks the condition-level dependence among solutes recorded under the same variety and operating condition.

The secondary six-group resampling is not a substitute. It resamples entire variety×solute groups and answers a much coarser question.

### Evidence relied on

- `docs/submission/PAPER_A_JFE_MANUSCRIPT.md`, §4:
  - describes shared \((T,p)\) conditions and dependence;
  - calls conditions-within-group the primary unit.
- `puckworks/validation/slow/angeloni_bracket.py`, `paired_clustered_bootstrap`:
  - groups records by `variety:solute`;
  - resamples condition lists independently for each group;
  - keeps only C and F paired within a solute.
- `puckworks/data/angeloni2023/bioactives.csv`:
  - all three named solutes occur on each condition-level record.

### Why this matters

The central model-minus-comparator difference is small and the primary range lies near zero. Its uncertainty or sensitivity summary is therefore particularly sensitive to the resampling unit. The manuscript’s phrase “once the dependence is respected” is stronger than the implementation licenses.

### Minimum acceptance criterion

1. For the on-grid analysis, make the primary cluster:
   \[
   (\text{variety}, T, p),
   \]
   carrying all three named solutes and both held-out grinds together.
2. If the off-grid records are included, define clusters from the actual sample/condition design rather than forcing a balanced-grid assumption.
3. Rerun the paired model-minus-comparator sensitivity under this crossed condition structure.
4. Retain the existing within-solute and six-group variants only as secondary sensitivities.
5. Replace the output field `ci95_pp` and docstring “95% CI” language with terminology consistent with the manuscript’s “clustered percentile sensitivity range,” unless a calibrated interval is introduced.
6. Update the conclusion if the sign, zero-crossing, or practical interpretation changes.

### Stale-number status

**No.** The reported range appears current for the implemented resampling scheme; the problem is that the scheme does not preserve all declared dependence.

---

## P1-2. The claimed loss robustness does not test the paper’s central model-versus-comparator estimand

### Finding

Section 4 says the verdict is robust to the loss function because a log/relative-error level fit gives a pooled mechanistic-model error of 7.0%. That analysis tests whether the mechanistic predictor’s **absolute held-out error** remains modest under a different fitting choice.

The paper’s principal quantitative result is different: the **paired difference between the mechanistic model and the level-only comparator**. The alternative-loss check does not refit and rescore both predictors under a common alternative loss and does not report the paired difference or its resampling range.

The paper later distinguishes absolute error from incremental skill, but the phrase “the verdict is robust to the loss function” conflates them.

### Evidence relied on

- `docs/submission/PAPER_A_JFE_MANUSCRIPT.md`, §4:
  - principal result is model MAPE minus level-only comparator MAPE;
  - later loss-robustness sentence reports only the mechanistic pooled mean of 7.0%.
- `puckworks/validation/slow/angeloni_bracket.py`:
  - `_log_level_mape` returns the mechanistic prediction’s MAPE under a log-level fit;
  - the associated producer verdict describes absolute held-out error;
  - no corresponding alternative-loss paired comparator result is produced there.

### Why this matters

A model can have similar absolute error under two losses while its small advantage over a comparator changes sign. Because the central difference is only a few tenths of a percentage point, robustness of the mechanistic MAPE alone cannot establish robustness of the central conclusion.

### Minimum acceptance criterion

Either:

1. narrow the claim to “the mechanistic model’s absolute held-out error remains modest under the tested alternative level fit”; or
2. perform a proper comparator-robustness analysis in which:
   - model and comparator are trained under the same declared loss;
   - both are evaluated under the same scoring rule;
   - paired condition-level differences are reported;
   - the crossed cluster sensitivity from P1-1 is repeated; and
   - pooled and per-group effects are shown.

At minimum, include MAPE and one concentration-scale loss. Additional log-relative or normalized-RMSE analyses may remain supplementary.

### Stale-number status

**No.** The 7.0% value is not shown to be stale; it is attached to a broader robustness claim than it supports.

---

## P1-3. Supplementary Methods S1 misdescribes the objective-specific nuisance optimization

### Finding

Supplementary Methods S1 says that at every rate-grid point the inventory level is “the exact least-squares minimizer” and then lists SSE, relative-L2, and Huber objectives.

The implementation does not use one ordinary least-squares minimizer for all three objectives:

- SSE uses ordinary least squares;
- relative-L2 uses weighted least squares with weights \(1/y_i^2\); and
- Huber uses an objective-specific iteratively reweighted solution.

The main manuscript describes this correctly, making the supplement internally inconsistent with both the manuscript and the executable producer.

### Evidence relied on

- `docs/submission/PAPER_A_JFE_SUPPLEMENT.md`, Supplementary Methods S1.
- `docs/submission/PAPER_A_JFE_MANUSCRIPT.md`, §2.5:
  - correctly distinguishes ordinary, weighted, and Huber optimizers.
- `puckworks/validation/slow/angeloni_bracket.py`, `_profile_objectives`:
  - `_ls_level`;
  - `_rel_level`;
  - `_huber_level`;
  - objective-specific profile construction.

### Why this matters

The objective family is central to the paper’s robustness argument. The supplement’s current wording could lead a reader to believe that all profiles use the SSE nuisance solution and only change the outer scoring function, which would be a different analysis.

### Minimum acceptance criterion

Replace the passage with an objective-specific statement, for example:

> At each candidate rate, the inventory level is optimized for the objective being profiled: ordinary least squares for SSE, weighted least squares for relative-L2, and IRLS for Huber. Each curve is therefore an objective-specific profile.

Add the explicit formulas or a compact table and generate this description from the same metadata used by the producer where practical.

### Stale-number status

**No.** This is a method-description mismatch.

---

## P1-4. Supplementary Table S5 generalises a one-panel convergence check beyond the evidence shown

### Finding

Supplementary Table S5 clearly states that the convergence panel is Arabica caffeine at the optimal grind. Its reading then says that “the identifiability conclusion” and the broad boundary-reaching set are properties of “the design and the data,” rather than numerical artifacts.

The table demonstrates excellent numerical stability for the listed outputs in one panel. It does not show:

- all six variety×solute panels;
- all three objective families;
- the endpoint-propagation benchmark;
- the off-grid transfer result;
- the crossed resampling; or
- the near-optimal-set boundary flag itself as a convergence output.

The main text is more carefully scoped than this supplementary reading.

### Evidence relied on

- `docs/submission/PAPER_A_JFE_SUPPLEMENT.md`, Table S5 and its reading:
  - panel explicitly identified as Arabica caffeine;
  - global-sounding identifiability conclusion.
- `docs/submission/PAPER_A_JFE_MANUSCRIPT.md`, numerical-method discussion:
  - describes the representative panel more cautiously.

### Why this matters

The convergence numbers are persuasive, but the assurance tier should match the design. A representative-panel check can support that panel and provide evidence that the scheme is stable; it cannot, without targeted stress cases, certify every load-bearing conclusion in the paper.

### Minimum acceptance criterion

Choose one:

1. narrow the reading to:
   - the Arabica-caffeine panel;
   - the listed whole-cup/fraction/profile outputs; and
   - the tested node/tolerance domain; or
2. add targeted convergence checks for the load-bearing extremes, such as:
   - a boundary-minimum panel;
   - a panel with the broadest near-optimal set;
   - one coarse/fine transfer case;
   - an early-fraction external-trajectory stress case.

If the “boundary-reaching set is not numerical” claim remains, include the boundary and set-width diagnostics directly in the convergence artifact.

### Stale-number status

**No.** The numerical values appear internally consistent; the scope of the conclusion is too broad.

---

## P1-5. The required claim-binding audit contains stale coverage counts and stale provenance

### Finding

The Round 7 brief reports:

- 166 of 441 Paper 1 claims verified; and
- 66 of 77 slow-lane values bound, with zero declared unbindable.

The committed `docs/CLAIM_BINDING_AUDIT_2026-07-28.md` at the review target says it was generated at commit `fc61c46` and still reports:

- 65 of 436 Paper 1 claims producer-bound;
- 60 of 77 slow-lane values checked;
- six declared unbindable; and
- 11 still unbound.

This is a confirmed stale-number defect in a document that the review brief expressly directs the reviewer to use.

### Evidence relied on

- `docs/paper1_resource/PAPER_1_REVIEW_BRIEF_ROUND_7.md`, §§1 and 3.
- `docs/CLAIM_BINDING_AUDIT_2026-07-28.md`, headline and progress table.

### Why this matters

The binding initiative is intended to prevent stale numbers and false assurance. Its own required audit is not bound to the reviewed state. A reviewer cannot determine from the repository artifact whether the brief, the audit, or the command output is authoritative.

This does not show that the manuscript’s scientific numbers are stale. It shows that the governance document summarising their coverage is stale.

### Minimum acceptance criterion

1. Regenerate the audit at the exact manuscript/release commit.
2. Include:
   - source commit;
   - generation command;
   - total claim count;
   - bound count;
   - slow-lane bound count;
   - unbindable count; and
   - remaining unbound IDs.
3. Make CI fail if:
   - the audit’s embedded commit is not the current target;
   - the brief’s headline counts disagree with generated output; or
   - a hand-authored audit table differs from the machine-readable coverage record.
4. Prefer generating the Round 7 brief’s coverage paragraph from the same artifact rather than duplicating the numbers manually.

### Stale-number status

**Yes — confirmed stale numbers.** They are coverage/governance numbers, not scientific result numbers.

---

## P1-6. The audit claims universal three-significant-figure consistency that the supplement contradicts

### Finding

The claim-binding audit says every appearance of the disputed interval now uses three significant figures. Supplementary Table S3 and its reading still display, for example:

- \([-0.72,+0.03]\);
- \([-0.75,-0.03]\); and
- other two-decimal endpoint intervals.

The main text uses \([-0.725,+0.027]\) for the 40 g primary range. The underlying values appear to be the same, but the committed package does not satisfy the assurance statement.

The audit also retains a later paragraph describing two committed records as different runs after an earlier paragraph says the discrepancy was only a rounding artifact. The audit is internally unreconciled.

### Evidence relied on

- `docs/CLAIM_BINDING_AUDIT_2026-07-28.md`:
  - assertion that every appearance now uses three significant figures;
  - later legacy discrepancy paragraph.
- `docs/submission/PAPER_A_JFE_SUPPLEMENT.md`, Table S3 and reading.
- `docs/submission/PAPER_A_JFE_MANUSCRIPT.md`, Table 4a and §4.

### Why this matters

This is precisely the sort of false assurance the brief identifies as worse than no mechanism. A value-level binding can pass while presentation precision and stale explanatory prose drift.

### Minimum acceptance criterion

1. Select one canonical archive for each interval.
2. Define an explicit rendering policy:
   - preferably three decimal places for the small pp ranges; or
   - a documented significant-figure rule applied uniformly.
3. Generate the main table, SI table, readings, and captions from the same canonical record.
4. Remove the superseded “two runs” paragraph if the adjudicated conclusion is one run plus rounding.
5. Add a semantic occurrence test that verifies both value and intended precision across manuscript and supplement.

### Stale-number status

**No stale result value confirmed.** This is a precision/rendering drift and a false assurance statement.

---

# P2 — Editorial and scoping findings

## P2-1. Supplementary Methods S1 inadvertently asserts structural identifiability

### Finding

Supplementary Methods S1 first says structural identifiability is not what the paper measures, but then says a model may be structurally identifiable and practically non-identifiable, “which is the situation studied here.”

No structural-identifiability analysis is presented for the full model and observation map. The second sentence therefore goes beyond the paper’s evidence and contradicts the otherwise careful framing in the main text.

### Minimum acceptance criterion

Replace it with language such as:

> This paper evaluates practical localization only. Structural identifiability of the full model under the relevant observation maps is not assessed.

### Stale-number status

**No.**

---

## P2-2. “Null” should be replaced by “comparator” or formally defined

### Finding

The level-only constant is a useful, deliberately weak benchmark. Its training and freezing contract is unusually well explained. However, the manuscript repeatedly calls it a “natural null,” “null model,” or “null benchmark.”

No statistical null hypothesis, null distribution, calibrated test, or nested-model relation is defined. The word “null” therefore risks implying an inferential status the analysis explicitly disclaims.

### Minimum acceptance criterion

Use **level-only comparator** or **level-only benchmark** throughout the manuscript, supplement, captions, and figures. Retain “null” only if the authors add a precise model-comparison definition and explain that it is not a hypothesis-testing null.

### Stale-number status

**No.**

---

## P2-3. Section 5 reintroduces ambiguity about the available empirical whole-cup data

### Finding

Section 5 correctly states that measured complete-cup concentrations are available and that the stronger fraction-versus-measured-cup profile analysis has not yet been executed. A few sentences later, it says that no “empirical complete-shot reconstruction” is available and therefore uses a same-model simulation.

That wording can be read as a renewed absence claim about the complete-cup data immediately after the text establishes that the data exists. The intended distinction appears to be between:

- measured complete-cup scalars, which are available; and
- a completed empirical rate-profile comparison or full time-resolved reconstruction, which is not.

The same paragraph also ends with an unmatched parenthesis in the sentence about “multi-class inventory ↔ kinetics).”

### Minimum acceptance criterion

1. Replace the absence wording with a direct statement:
   > The measured complete cups are available, but the fraction-versus-measured-cup rate-profile analysis has not yet been run; the same-model exact-cup calculation is therefore retained as an interim control.
2. Reserve “complete-shot reconstruction” for a clearly defined time-resolved quantity if that is what is intended.
3. Correct the unmatched parenthesis and rewrite the final sentence for clarity.

This finding is about contradictory wording, not a request to re-report the known open analysis item.

### Stale-number status

**No.**

---

## P2-4. Figure 3 requires publication-layout correction in addition to the endpoint relabelling

### Finding

The current transfer figure contains a long, incorrect 40 mL title and visible legend/annotation collisions in the upper portion of panel (a). Several labels compete with the plotted data, and the key “not shown”/envelope explanation is difficult to parse at normal manuscript scale.

The figure contains valuable information, but it is not yet journal-ready in its current rendered form.

### Minimum acceptance criterion

When regenerating the figure for P0-2:

1. use a short title or move the full contract to the caption;
2. replace 40 mL with the correct 40 g endpoint;
3. move legends outside the data area or split them by panel;
4. remove overlapping annotations;
5. verify legibility at the journal’s expected single- or double-column width; and
6. ensure all labels use the final “comparator,” endpoint, and corpus terminology.

### Stale-number status

**No.**

---

# Cross-cutting assessment of the claim-binding work

The binding work is valuable and should be retained. It appears to have reduced ordinary arithmetic drift and made the provenance of many slow results inspectable. The Round 7 defects show the remaining boundary of a numeral-centric system:

| Defect found | Why a value binding can miss it | Required stronger control |
|---|---|---|
| Wrong Reynolds equation | The equation may contain the same constants while the semantic use of porosity is wrong | Executable model-contract tests or generated equations |
| 40 g result labelled 40 mL | The numeric token is identical | Typed units and estimand metadata propagated to text and figures |
| 108 selected records described as all C/F data | The count is correct for the hidden subset | Record-ID inclusion manifests and corpus assertions |
| Bootstrap omits cross-solute clustering | The output values match the producer | Design-semantic tests on the resampling unit |
| SI says ordinary least squares for all objectives | All reported minima can still bind | Method-description metadata generated from code |
| One-panel convergence read globally | The numbers are correct | Evidence-tier and scope assertions |
| Audit itself stale | The audit is outside its own binding chain | Self-provenancing generated audit and CI consistency |

The next assurance increment should therefore be **semantic binding**, not simply a higher proportion of numeric tokens bound.

Recommended machine-readable contracts:

1. **Model contract:** velocity definitions, Reynolds formula, porosity use, initial/boundary conditions.
2. **Observation contract:** endpoint quantity, unit, source-flow interpretation, stop equation, averaging quantity.
3. **Corpus contract:** included sample IDs, excluded sample IDs, rationale, observation count by variety/grind/solute/grid status.
4. **Resampling contract:** cluster keys and which observations must move together.
5. **Evidence contract:** in-sample, within-campaign holdout, external proxy, or independent named-solute evidence.
6. **Presentation contract:** canonical value plus unit, precision, caption text, and figure metadata.

---

# Recommended correction sequence

## Gate 1 — Correct the scientific contract before touching prose selectively

1. Fix Reynolds-number documentation everywhere.
2. Rename the endpoint and source-flow variables/metadata to reflect the settled mass contract.
3. Decide the corpus estimand:
   - complete C/F corpus; or
   - matched-grid primary plus off-grid sensitivity.
4. Define the correct crossed resampling unit.
5. Record those decisions in machine-readable contracts.

## Gate 2 — Run only the analyses genuinely affected

A slow rerun is **not evidently required** for the Reynolds documentation correction if code remains unchanged.

The endpoint numerical results also appear to be the existing mass-endpoint results, so relabelling and regeneration may suffice.

A rerun **is required** for:

- complete-corpus or off-grid transfer evaluation;
- corrected crossed-cluster resampling;
- any alternative-loss model-versus-comparator analysis retained as robustness evidence.

## Gate 3 — Regenerate the whole submission package

Regenerate rather than hand-edit:

- abstract;
- Tables 1, 2, 4a, and 5 where affected;
- Supplementary Methods S1–S2;
- Supplementary Table S3;
- all endpoint and comparator captions;
- Figure 3 and any other endpoint-labelled figure;
- result bindings;
- claim-binding audit; and
- the reviewer brief’s coverage counts.

## Gate 4 — Add adversarial semantic tests

At minimum, CI should fail when:

- the manuscript Reynolds expression differs from `closures.sherwood_h`;
- a mass endpoint is printed with mL;
- the declared record count does not equal the emitted sample-ID manifest;
- any available record is called “held out all” while excluded;
- the resampling cluster key separates solutes from the same condition;
- the SI optimizer description differs from `_profile_objectives`;
- an audit’s embedded commit is not the target commit; or
- the main and SI render the same interval at inconsistent precision.

---

# Strengths that should be preserved

The paper has several unusually strong features that should not be lost during correction.

1. **Clear separation of scientific questions.** Parameter localization, absolute prediction, incremental benchmark skill, and cross-context transfer are treated as distinct quantities.
2. **Appropriate evidence vocabulary.** The manuscript generally distinguishes in-sample verification, within-campaign holdout, and external aggregate-proxy evidence.
3. **Honest handling of a weak external panel.** The Waszkiewicz analysis is not oversold; loss dependence, boundary censoring, high residuals, and the aggregate-TDS limitation are explicit.
4. **Strong explanation of exact inventory scaling.** The linearity argument is one of the clearest parts of the paper.
5. **Useful comparator design.** The level-only comparator is trained only on the optimal grind and frozen, making it a meaningful check against confusing low absolute error with mechanistic value.
6. **Good distinction between threshold sets and confidence regions.** The paper avoids calibrated-CI language for quantities that are only descriptive sensitivity ranges.
7. **Transparent limitations.** Inferred flow, frozen geometry, model lineage, unavailable replicate-level uncertainty, and in-sample temporal evidence are discussed directly.
8. **Promising assurance architecture.** The claim-binding machinery is worth extending; the Round 7 defects identify its semantic frontier rather than negating its value.
9. **Title and overall framing.** The title is descriptive, includes “espresso,” and accurately foregrounds the paper’s central inventory-versus-rate question once the endpoint terminology is corrected.

---

# Final recommendation

The manuscript should return for one focused technical revision before any submission-format polishing.

The correction should be considered successful only when:

- the displayed model matches the executable model;
- 38/40/42 are consistently treated as mass endpoints;
- the headline corpus is explicitly and reproducibly defined;
- the off-grid observations are analysed or transparently separated;
- the primary resampling preserves condition dependence across solutes;
- the central comparator conclusion is tested under any loss-robustness claim retained;
- the supplement accurately describes the objective-specific optimizer;
- the convergence claim is scoped to the evidence shown;
- the claim-binding audit is regenerated at the target commit; and
- all prose, tables, SI, captions, and figure text are regenerated from those corrected contracts.

The likely scientific endpoint remains plausible: acceptable whole-cup prediction can coexist with weak parameter localization and little incremental skill over a level-only benchmark. The current submission package does not yet establish that result under a fully correct and transparent model, endpoint, corpus, and resampling contract.

---

## Concise disposition table

| ID | Priority | Finding | Rerun required? | Stale number? |
|---|---|---|---|---|
| P0-1 | P0 | Manuscript Reynolds definition differs from source and code by ~34.6× | No, if code unchanged | No |
| P0-2 | P0 | 38/40/42 g analyses labelled as mL volume proxies | Probably not; regenerate package | No — unit/estimand error |
| P0-3 | P0 | Eight C/F off-grid records omitted while corpus described as complete | Yes, at least as sensitivity | No |
| P1-1 | P1 | Bootstrap breaks cross-solute condition dependence | Yes | No |
| P1-2 | P1 | Loss robustness tests mechanistic error, not model-minus-comparator skill | Yes, or narrow claim | No |
| P1-3 | P1 | SI misstates objective-specific nuisance optimization | No | No |
| P1-4 | P1 | One-panel convergence read as global identifiability assurance | Possibly, or narrow claim | No |
| P1-5 | P1 | Claim-binding audit reports old counts and old commit | Regenerate audit | **Yes** |
| P1-6 | P1 | Audit’s precision assurance contradicted by SI | Regenerate text/tables | No |
| P2-1 | P2 | SI inadvertently asserts structural identifiability | No | No |
| P2-2 | P2 | Trained comparator is called a statistical “null” | No | No |
| P2-3 | P2 | §5 availability wording is contradictory; syntax defect remains | No | No |
| P2-4 | P2 | Figure 3 legend/title layout is not publication-ready | Regenerate figure | No |
