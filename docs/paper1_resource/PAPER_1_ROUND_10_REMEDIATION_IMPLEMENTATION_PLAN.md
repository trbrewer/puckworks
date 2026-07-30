# Paper 1 — Round 10 Remediation Implementation Plan

**Prepared:** 29 July 2026  
**Basis:** `PAPER_1_ROUND_10_DETAILED_REVIEW.md`  
**Reviewed repository snapshot:** `3b7fe7e10ee9989b380c70e40894d74b8ca2d8a5`  
**Target paper:** Paper 1 / Paper A  
**Recommended disposition until completion:** **DO NOT SUBMIT**  
**Recommended scientific route:** **P0-1 Path A — correct the central claim to match the analysis already performed**

---

## 1. Purpose of this plan

This document translates every Round 10 review finding into an implementation-ready remediation program. It specifies:

- the objective of each action;
- the exact method I would use;
- the files and software surfaces likely to be affected;
- the scientific and engineering pitfalls to avoid;
- the tests, mutations, manual reviews, and acceptance evidence required; and
- the order in which the work should be completed so that one correction does not undermine another.

The plan addresses all five active Round 10 findings:

| ID | Severity | Finding | Required outcome |
|---|---|---|---|
| **P0-1** | Submission-blocking | “No resolvable skill” is stronger than the declared uncalibrated sensitivity analysis can determine | Replace the categorical conclusion with an evidence-limited conclusion, or add a separately justified calibrated decision analysis. This plan recommends the former. |
| **P1-1** | Major | Canonical and submission manuscripts are not in material scientific agreement | Establish one authoritative source for the active scientific claim blocks and enforce structural parity. |
| **P1-2** | Major | Estimand direction and resampling-design semantics are duplicated rather than contract-bound | Introduce one typed transfer-analysis contract; derive favourability from it; exact-validate the entire resampling design. |
| **P1-3** | Major | Interval semantic records accept invalid types and contradictory facts | Make interval construction and validation exact, typed, finite, fail-closed, and mutation-tested. |
| **P2-1** | Editorial | Process history and repository/test narration remain in submission-facing material, while the scanner reports a false green | Remove the leakage and replace line-based scanning with paragraph-aware, surface-complete validation. |

The verified numerical results are not themselves under challenge. The implementation should therefore preserve the accepted values unless a deliberately new analysis is undertaken.

---

## 2. Recommended overall remediation strategy

### 2.1 Selected route for the central scientific issue

I would use **P0-1 Path A**: revise the paper so that it says what the present analysis supports.

The core conclusion should become:

> The mechanistic model showed a small observed advantage over the O-trained level-only comparator. The present fixed-predictor clustered sensitivity analyses do not establish whether that advantage is reproducible, statistically distinguishable, or practically useful; acceptable cross-grind endpoint error therefore does not by itself establish mechanistic transfer.

This route is preferable because it:

1. is supported by the existing results;
2. requires no post hoc practical-equivalence threshold;
3. avoids retrofitting a calibrated inferential interpretation onto a sensitivity analysis that was not designed for one;
4. preserves the paper’s principal scientific value: acceptable predictive error is not, by itself, evidence that the mechanistic structure transferred; and
5. can be implemented without changing the accepted numerical values.

### 2.2 Path B should be a separate future analysis, not an in-place wording repair

A claim that the model has **no practically meaningful skill** would require a prospectively justified margin and a calibrated decision procedure. It should not be created by selecting a threshold after seeing the current difference of approximately −0.394 percentage points. If the authors later choose that route, it should be a separately documented analysis with its own protocol, estimand, dependence assumptions, refitting policy, coverage target, and decision rules.

Path B is described in Section 5.13 for completeness, but it is not the recommended Round 10 remediation.

### 2.3 Scope guard

Do not use this remediation to reopen or silently resolve the three items that the Round 10 brief treated as known and outside the active findings: the fraction-versus-measured-cup rate-profile contrast, the 11 unbound slow-lane values, and the approximately 255 hand-sourced design settings. Preserve their existing status and wording unless a separate, explicitly scoped task is authorized. Likewise, do not mix author metadata, funding, competing-interest, novelty-search, DOI/tag, or final-typesetting work into the scientific acceptance evidence for these five findings.

### 2.4 Cross-cutting implementation principles

All work should follow these principles:

1. **Preserve verified science.** Do not change accepted headline values merely to solve a wording or assurance problem.
2. **One source of scientific truth.** Facts, sign conventions, inferential status, and active central claim blocks should have one authoritative representation.
3. **Derive, do not duplicate.** Favourability, interval relation, widths, display strings, cluster counts, and similar facts should be calculated from primitives and exact-checked if serialized.
4. **Fail closed.** Missing, malformed, contradictory, non-finite, or unknown fields must cause a named validation failure.
5. **Keep the oracle genuinely independent.** Source membership and census reconstruction must not call the producer’s grouping implementation.
6. **Generate all reader-facing repetitions.** Abstract, significance statement, Results synthesis, cover letter, package, supplement interpretation, and captions should be rendered from the same accepted claim policy.
7. **Treat green tests as necessary but not sufficient.** The final submission files must also be read continuously as scientific prose and visually inspected.

---

## 3. Baseline, branch, and preservation work before any edits

### Objective

Create a reproducible starting point and a numerical preservation record so that remediation does not accidentally alter accepted results.

### Method

1. Create a dedicated branch from the reviewed commit, for example:

   ```bash
   git switch --detach 3b7fe7e10ee9989b380c70e40894d74b8ca2d8a5
   git switch -c paper1/round10-remediation
   ```

2. Confirm a clean working tree and record:

   - starting commit SHA;
   - tree SHA;
   - Python version;
   - dependency lock or environment identity;
   - relevant random seeds;
   - source CSV hash;
   - current transfer-artifact hashes; and
   - hashes of the current manuscript, supplement, front matter, cover letter, package, highlights, and caption files.

3. Run the complete existing verification chain before editing, where the environment permits:

   ```bash
   python tools/paper_a_transfer_artifacts.py --check
   python tools/paper_a_transfer_text.py --check
   python tools/paper_a_consistency.py verify
   python -m puckworks.paper_a.slow_lane_bindings
   python tools/claim_binding_audit.py
   python -m pytest tests/test_paper_a_transfer_semantics.py \
                    tests/test_paper_a_transfer_contract.py \
                    tests/test_paper_a_model_contract.py \
                    tests/test_paper_a_figure_semantics.py -q
   python -m pytest -q
   ```

4. Create a machine-readable numerical preservation file, for example:

   `docs/paper1_resource/round10_baseline_numerical_invariants.json`

   It should contain at least:

   - model and comparator pooled MAPE at 38, 40, and 42 g;
   - model-minus-comparator differences;
   - full-precision primary range bounds;
   - all secondary range bounds;
   - model-worse counts;
   - source census and scheme census;
   - multi-seed audit standard errors;
   - endpoint-row count and keys; and
   - the exact estimand identifier and sign convention after the new contract is introduced.

5. Add a test that compares regenerated results with this preservation file. The test should allow only changes explicitly approved through a deliberate numerical-baseline update procedure.

### Potential pitfalls, errors, and oversights

- Starting from current `main` rather than the reviewed commit may mix Round 10 remediation with unrelated later changes.
- Recording only rounded values would fail to detect small numerical drift.
- Treating generated-file hashes as scientific invariants can be too brittle; preserve both semantic numerical values and file hashes.
- A producer rerun may change Monte Carlo outputs if seeds or library versions are not fixed. Record the exact seed and environment before comparing.
- Do not update the baseline file merely because a test fails. First determine whether the change is intended, numerical noise, or a defect.

### Required checks

- The pre-edit repository is clean.
- Existing checks are recorded as pass/fail rather than assumed.
- The preservation artifact can be independently read and compared.
- A deliberate one-digit mutation in a preserved full-precision bound causes the preservation test to fail.
- A prose-only edit does not change any numerical invariant.

### Acceptance evidence

- Baseline command transcript.
- Baseline numerical invariant file.
- Starting commit and tree SHAs.
- Environment and seed record.
- Demonstrated failing mutation of one protected number.

---

# 4. Remediation workstream map and dependencies

| Workstream | Finding(s) | Depends on | Principal deliverable |
|---|---|---|---|
| **WS-1** | P1-2, part of P0-1 | Baseline | Typed transfer-analysis and inferential-status contract; no default favourability direction. |
| **WS-2** | P1-3 | Baseline; preferably WS-1 types | Exact interval schema, canonical constructor, strict validator, mutation coverage. |
| **WS-3** | P0-1 | WS-1 | Evidence-limited central claim generated across every publication surface; S3 terminology corrected. |
| **WS-4** | P1-1 | WS-3 | One authoritative claim-block source; canonical/submission structural parity and dual claim coverage. |
| **WS-5** | P2-1 | WS-4 | Clean publication files; split internal/upload captions; paragraph-aware scanner. |
| **WS-6** | All | WS-1 through WS-5 | Regenerated artifacts, full tests, manual prose/figure review, acceptance report. |

The preferred implementation sequence is:

1. freeze the baseline;
2. implement the typed transfer-analysis and interval foundations;
3. implement the corrected claim policy and regenerate all claim surfaces;
4. bind canonical and venue manuscripts to the same generated blocks;
5. remove process leakage and harden the scanner;
6. regenerate, run all tests, inspect rendered outputs, and produce acceptance evidence.

This order prevents the central wording fix from being reintroduced by an older canonical source or rendered through a still-duplicated sign convention.

---

# 5. P0-1 — Correct the central “no resolvable skill” conclusion

## 5.1 Objective

Replace a categorical negative conclusion that the declared analysis cannot determine with a precise statement that:

- reports the observed small advantage;
- does not claim superiority;
- does not claim equivalence, non-distinguishability, absence of skill, or practical negligibility;
- clearly states the limitations of the fixed-predictor sensitivity ranges; and
- preserves the paper’s main methodological lesson: acceptable held-out endpoint error alone does not establish mechanistic transfer.

## 5.2 Method summary

1. Record Path A as the accepted scientific decision.
2. Add a typed inferential-status object that explicitly states the analysis is sensitivity-only and supports no calibrated superiority, equivalence, or absence-of-skill decision.
3. Define one approved evidence-limited core claim.
4. Render every repeated publication statement from that claim policy and the validated numerical artifact.
5. Rename or remove the undefined Supplementary Table S3 `skill` field.
6. Add policy, mutation, cross-surface, and manual continuous-argument checks.
7. Confirm numerical parity with the frozen Round 10 baseline.

## 5.3 Scientific decision to record explicitly

Add an explicit project decision to the remediation record:

```text
Decision: Use P0-1 Path A.
Reason: The existing analysis is descriptive and sensitivity-oriented, without calibrated
coverage or a predeclared practical decision margin. The manuscript will therefore make an
evidence-limited conclusion rather than a categorical absence-of-skill conclusion.
Numerical outputs: unchanged.
```

This prevents later editors from interpreting the wording change as temporary or from reintroducing “no resolvable skill” because it sounds more decisive.

## 5.4 Add a machine-readable inferential-status object

### Method

Extend the transfer-analysis artifact with one typed object that describes what decisions the analysis can and cannot support. A suitable shape is:

```json
{
  "inferential_status": {
    "analysis_kind": "fixed_predictor_clustered_sensitivity",
    "coverage_calibrated": false,
    "confidence_level": null,
    "predictors_refitted_within_draw": false,
    "supports_superiority_decision": false,
    "supports_noninferiority_decision": false,
    "supports_equivalence_decision": false,
    "supports_absence_of_skill_decision": false,
    "practical_margin_pp": null,
    "permitted_claim_class": "descriptive_evidence_limited"
  }
}
```

Use enums or frozen typed structures internally rather than unrestricted strings. The serialized object should be exact-validated against the active analysis method.

The claim generator should consume this object. It must not infer decision authority from whether a range contains zero.

### Required policy rules

At minimum, enforce:

```python
if not status.coverage_calibrated:
    prohibit_claims(
        "statistically significant",
        "statistically indistinguishable",
        "non-distinguishable",
    )

if not status.supports_equivalence_decision:
    prohibit_claims("equivalent", "no meaningful difference")

if not status.supports_absence_of_skill_decision:
    prohibit_claims("no skill", "no resolvable skill", "adding no skill")

if status.practical_margin_pp is None:
    prohibit_claims("practically negligible", "no practically useful improvement")
```

The primary defense should be a controlled claim renderer, not merely a banned-word search. The phrase scan should remain as a secondary defense against manually introduced text.

### Potential pitfalls

- `contains_zero` must not be converted into “no difference.”
- A wholly negative sensitivity range must not be converted into a superiority claim.
- “Not established” must remain attached to the **evidence**, not stated as a property of the model.
- A null practical margin must not silently default to zero.
- An unknown `analysis_kind` must fail rather than fall back to permissive wording.
- Do not use a positive relative-reduction percentage to imply calibrated skill.

### Checks

- Changing `coverage_calibrated` from `false` to `true` without a confidence procedure identifier must fail validation.
- Removing `practical_margin_pp` must make equivalence/absence-of-skill templates unavailable.
- Changing `permitted_claim_class` to an unknown value must fail.
- A mutation inserting “no resolvable skill” into any generated publication block must fail the claim-policy and consistency checks.

## 5.5 Adopt one approved core claim

I would approve the following as the canonical transfer conclusion:

> At the primary 40 g endpoint, the mechanistic model showed a small observed pooled-MAPE advantage over the O-trained level-only comparator: 8.44% versus 8.83%, or −0.394 percentage points for model minus comparator. The reported fixed-predictor clustered ranges are sensitivity analyses without calibrated coverage or a predeclared practical decision margin. They therefore do not establish whether the observed advantage is reproducible, statistically distinguishable, or practically useful. Acceptable cross-grind endpoint error does not by itself establish mechanistic transfer.

The exact wording may be shortened for an abstract, but every version must preserve these propositions:

1. the point estimate is a small observed advantage;
2. the sign convention is model minus comparator, so negative favours the model;
3. the ranges are uncalibrated sensitivity analyses;
4. no superiority, equivalence, absence-of-skill, or practical-usefulness decision is made; and
5. acceptable predictive error alone is insufficient evidence of mechanistic transfer.

## 5.6 Replace the claim on every affected surface

### Affected surfaces

At minimum inspect and regenerate:

- `docs/PAPER_A_DRAFT.md`;
- `docs/submission/PAPER_A_JFE_MANUSCRIPT.md`;
- `docs/submission/PAPER_A_JFE_SUPPLEMENT.md`;
- `docs/submission/paper_a_front_matter.yaml`;
- `docs/submission/PAPER_A_JFE_COVER_LETTER.md`;
- the journal package/combined submission source;
- highlights;
- standalone upload-ready captions;
- figure descriptions and alt text if they restate the conclusion;
- generated transfer text snapshots or golden files; and
- any README or publication summary used as a source for submission text.

### Suggested surface-specific wording

#### Abstract transfer sentence

> On the held-out coarse/fine records, pooled MAPE at 40 g was 8.44% for the mechanistic model and 8.83% for the O-trained level-only comparator, an observed model-minus-comparator difference of −0.394 percentage points. The fixed-predictor clustered sensitivity ranges are not calibrated confidence intervals and do not establish whether this small advantage is reproducible or practically useful. Thus, acceptable cross-grind endpoint error alone does not establish mechanistic transfer.

#### Results heading

> **A small observed advantage over the transferred level does not establish useful mechanistic transfer**

An alternative, if the journal prefers shorter headings:

> **Endpoint accuracy alone does not establish mechanistic transfer**

#### Endpoint synthesis

> The point estimates favour the mechanistic model at all three endpoints, but the differences are small. The primary 40 g and 42 g ranges include zero, the 38 g primary range is wholly negative, and all secondary ranges are wholly negative. Because these are fixed-predictor sensitivity ranges without calibrated coverage or a predeclared practical margin, their positions do not determine superiority, equivalence, absence of skill, or practical usefulness. The present analysis therefore leaves the reproducibility and utility of the incremental advantage unresolved; it does not establish that the advantage is absent.

This deliberately distinguishes “unresolved by this analysis” from the former property-level phrase “unresolved throughout.”

#### Significance statement

> The mechanistic model achieved acceptable held-out endpoint error and a small observed advantage over a transferred level-only comparator. The current dependence-aware sensitivity analysis does not establish whether that increment is reproducible or practically useful. The result shows why endpoint accuracy alone is insufficient evidence that mechanistic structure has transferred across grind conditions.

#### Cover letter

> At the primary 40 g endpoint, the mechanistic model reduced pooled MAPE from 8.83% for the O-trained level-only comparator to 8.44%, an observed difference of −0.394 percentage points for model minus comparator. Because the dependence-aware ranges are fixed-predictor sensitivity analyses without calibrated coverage or a practical decision margin, we do not claim superiority, equivalence, or absence of skill. The contribution is instead to show that acceptable held-out endpoint accuracy does not, by itself, demonstrate transfer of the kinetic mechanism.

#### Figure caption or figure description

> Point estimates show a small observed MAPE advantage for the mechanistic model. The plotted clustered ranges are uncalibrated fixed-predictor sensitivity summaries and do not determine whether the increment is reproducible or practically useful.

#### Conclusion

Retain and elevate the existing defensible formulation:

> Acceptable holdout error does not by itself establish useful mechanistic transfer.

Where helpful, add:

> The present analysis observes a small incremental advantage but does not determine its reproducibility or practical value.

## 5.7 Remove or rename the Supplementary Table S3 `skill` column

### Recommended method

Rename `skill` to:

> **Relative pooled-MAPE reduction (%)**

Define it in the table note as:

\[
100\times\frac{\mathrm{MAPE}_{comparator}-\mathrm{MAPE}_{model}}
{\mathrm{MAPE}_{comparator}}.
\]

State explicitly:

> Positive values favour the mechanistic model. This is a descriptive relative error reduction, not a calibrated inferential measure.

Compute the column from full-precision MAPE values and round only for display. Do not compute it from already rounded table cells.

### Alternative

Remove the column if it is not needed for the argument. This is simpler and eliminates another sign convention. If retained, it must not be called `skill` in code, data, or prose unless the term is carefully defined as a descriptive metric rather than an inferential conclusion.

### Pitfalls

- Using model-minus-comparator in the numerator would make favourable results negative, conflicting with the proposed “reduction” label.
- Computing from rounded 8.44 and 8.83 values can differ from the full-precision result.
- Calling the column “relative skill” would reintroduce the disputed conclusion through terminology.
- A table note must not describe it as statistically significant or resolved.

### Checks

- Unit-test the formula and sign at every endpoint.
- Confirm that a model equal to the comparator gives exactly 0%.
- Confirm that a lower model MAPE gives a positive reduction.
- Search all source and rendered files for a bare `skill` column or undefined use of `skill`.

## 5.8 Add claim-policy tests

Add tests such as:

- `test_sensitivity_only_status_forbids_no_skill_claim()`;
- `test_missing_practical_margin_forbids_equivalence_claim()`;
- `test_uncalibrated_status_forbids_statistical_decision_language()`;
- `test_allowed_evidence_limited_claim_renders_on_all_surfaces()`;
- `test_abstract_and_cover_letter_share_core_claim_assertions()`;
- `test_relative_mape_reduction_is_descriptive_and_correctly_signed()`; and
- `test_point_estimate_and_ranges_remain_numerically_unchanged()`.

Use mutation tests that alter the status object and confirm that the text generator either changes deliberately or fails. It must never continue to emit the same categorical sentence after its decision authority has been removed.

## 5.9 Manual scientific checks

Read, in this order, as a single argument:

1. title;
2. abstract;
3. editor significance paragraph;
4. Methods description of the range;
5. principal Results heading;
6. endpoint table and interpretation;
7. supplement interpretation;
8. figure caption;
9. Discussion;
10. Conclusion; and
11. cover letter.

The reader should never encounter the following contradiction:

- Methods: “not calibrated; no distinguishability or equivalence claim”; then
- Results: “no resolvable skill.”

## 5.10 Search checks

Run exact and case-insensitive searches across all publication and source-template files:

```bash
rg -n -i \
  'no resolvable|no skill|adding no|equivalent|non[- ]?distinguish|unresolved throughout|practically negligible|no meaningful difference' \
  docs puckworks tools tests
```

Every hit must be one of:

- a historical review resource that is explicitly outside publication generation;
- a negative test fixture; or
- a policy rule that forbids the phrase.

There should be no active reader-facing hit.

## 5.11 Acceptance criteria for P0-1

P0-1 is closed only when:

- every editor/reviewer-facing surface uses an evidence-limited conclusion;
- the observed advantage is reported accurately and with the correct sign;
- no surface claims superiority, equivalence, non-distinguishability, absence of skill, or practical negligibility;
- the inferential-status object prevents those claims from being generated under the present analysis;
- Supplementary Table S3 no longer contains an undefined `skill` field;
- the verified numbers are unchanged; and
- a continuous manual read finds no remaining logical contradiction.

## 5.12 Potential hidden regressions

Pay particular attention to:

- captions or alt text generated from older descriptions;
- a package file that embeds an earlier manuscript snapshot;
- front-matter YAML that can overwrite hand-edited Markdown;
- test golden files that preserve the retired phrase;
- a README or figure map used as an upstream source;
- an internal short label such as `no_skill` that later becomes visible;
- negative-language synonyms not covered by exact search patterns; and
- accidental replacement with an equally unsupported positive claim.

## 5.13 Optional Path B requirements, if pursued later

Do not treat this as part of the minimum Round 10 fix. A future calibrated analysis would require:

1. a prospectively justified smallest useful improvement or equivalence margin in percentage points;
2. a clearly identified estimand and direction;
3. a defined dependence unit and resampling design;
4. a decision on whether all fitted predictors are refitted inside each draw;
5. a confidence or coverage target;
6. an appropriate superiority, non-inferiority, or equivalence procedure;
7. multiplicity treatment if several endpoints or schemes are decision-bearing;
8. sensitivity to clustering and endpoint selection;
9. a power/precision assessment; and
10. manuscript wording that distinguishes failure to demonstrate superiority from evidence of equivalence or practical absence.

A post hoc margin chosen because it brackets the observed −0.394 pp result would be scientifically weak and should be avoided.

---

# 6. P1-1 — Establish one authoritative scientific source and enforce manuscript agreement

## 6.1 Objective

Ensure that the canonical draft and the journal manuscript cannot carry different active abstracts, central transfer conclusions, or figure-caption interpretations while CI reports that they are aligned.

## 6.2 Method summary

1. Treat validated scientific facts and claim policy as upstream of both manuscripts.
2. Define named generated blocks for every load-bearing repeated claim.
3. inject those blocks into the canonical and venue manuscripts through explicit markers.
4. Replace curated phrase matching with structural block parity and assertion-level checks.
5. Run claim coverage against both active manuscripts by default.
6. Add drift, missing-block, duplicate-block, polarity, and caveat-loss mutations.
7. Read both rendered manuscripts to confirm that allowed venue shortening has not changed scientific meaning.

## 6.3 Recommended architecture

Use a three-layer design:

1. **Validated scientific facts:** the typed transfer-analysis artifact contains metrics, intervals, estimand, design, and inferential status.
2. **Claim policy and renderer:** one module maps the validated facts and status to approved scientific assertions and prose blocks.
3. **Publication targets:** both the canonical manuscript and venue manuscript receive the same generated scientific blocks, with only explicitly declared venue formatting changes.

Do not use semantic similarity or a short curated phrase list as the primary parity test.

## 6.4 Define named generated blocks

At minimum, create named blocks for:

- `abstract_transfer_claim`;
- `significance_transfer_claim`;
- `results_transfer_heading`;
- `results_endpoint_synthesis`;
- `supplement_transfer_interpretation`;
- `conclusion_transfer_claim`;
- `cover_letter_transfer_claim`;
- `figure_3_caption_claim`; and
- any highlights that state the central result.

Use explicit markers in generated Markdown, for example:

```markdown
<!-- BEGIN GENERATED: abstract_transfer_claim -->
...
<!-- END GENERATED: abstract_transfer_claim -->
```

The generator should fail if:

- a required marker is missing;
- a marker appears more than once;
- begin/end markers are mismatched;
- a generated block has been hand-edited; or
- a target file contains an unknown generated block.

## 6.5 Decide what is authoritative

I would make the renderer, not either Markdown file, authoritative for the shared scientific blocks. The validated artifact and claim policy are upstream; both manuscripts are downstream renderings.

The canonical manuscript may remain longer and include additional exposition, but its active abstract and central transfer synthesis should be generated from the same source as the venue version. Internal review history should be moved to review resources or HTML comments excluded from publication generation.

## 6.6 Structural parity contract

Create a manifest such as:

```yaml
blocks:
  abstract_transfer_claim:
    canonical: docs/PAPER_A_DRAFT.md
    venue: docs/submission/PAPER_A_JFE_MANUSCRIPT.md
    parity: identical_normalized_text
  results_endpoint_synthesis:
    canonical: docs/PAPER_A_DRAFT.md
    venue: docs/submission/PAPER_A_JFE_MANUSCRIPT.md
    parity: identical_normalized_text
  conclusion_transfer_claim:
    canonical: docs/PAPER_A_DRAFT.md
    venue: docs/submission/PAPER_A_JFE_MANUSCRIPT.md
    parity: identical_normalized_text
```

Where venue constraints genuinely require a shorter version, do not use an unbounded “may differ” flag. Use one of these controlled options:

- both versions generated from the same assertion list;
- a specific short-template identifier paired with a long-template identifier; and
- tests that compare required assertion IDs, numerical tokens, polarity, estimand direction, and inferential status.

A permitted difference should be explicit, narrow, and reviewed.

## 6.7 Replace phrase-only agreement with exact block checks

Extend or replace `_phrase_drift()` so that it checks:

1. required generated block presence;
2. exact normalized block equality where required;
3. approved template-pair identity where exact text differs;
4. identical scientific assertion IDs;
5. identical numerical source references;
6. identical sign convention;
7. identical inferential-status class; and
8. absence of retired claim classes.

Whitespace normalization may ignore formatting differences, but it must not remove scientific tokens, punctuation that changes sign, or negation.

## 6.8 Run claim coverage against both manuscripts by default

Change claim coverage so that the default invocation audits all active manuscripts:

```text
canonical: docs/PAPER_A_DRAFT.md
venue:     docs/submission/PAPER_A_JFE_MANUSCRIPT.md
```

The default should fail if:

- one active manuscript was not scanned;
- a load-bearing claim appears in only one manuscript;
- one version exceeds the accepted unbound-claim baseline;
- the two versions bind the same claim to different evidence; or
- a retired claim reappears in either version.

If a `--canonical-only` or `--conversion-only` option remains for diagnostics, it should be explicitly named and not be the CI default.

## 6.9 Correct the current canonical abstract

Replace the active canonical abstract with the same accepted P0-1 abstract block used by the venue manuscript. Move any narration of earlier errors to:

- the Round 9/10 review resources;
- a changelog;
- an HTML comment that is excluded from all reader-facing outputs; or
- Git history.

Do not retain active phrases such as “not identifiable,” “adds little,” or “incremental skill of approximately 4.5%” unless they are separately justified and harmonized with the accepted claim policy. The descriptive relative MAPE reduction can be reported, but it must not be called inferential “skill.”

## 6.10 Mutation and regression tests

Add tests that:

1. change “does not establish” to “establishes no” in the canonical manuscript and require failure;
2. change the venue sign from −0.394 to +0.394 and require failure;
3. delete a generated block from either manuscript and require failure;
4. duplicate a generated block and require failure;
5. change the inferential-status assertion in only one version and require failure;
6. add a venue-only categorical “no skill” sentence and require failure;
7. alter a permitted venue-short template so that it drops the uncalibrated-range caveat and require failure; and
8. run claim coverage with one manuscript omitted and require the CI wrapper itself to fail.

## 6.11 Potential pitfalls, errors, and oversights

- **Fuzzy comparison can hide negation.** “Does not establish skill” and “establishes no skill” are lexically similar but scientifically different.
- **Over-normalization can remove signs.** Never strip `+` or `−` during parity checks.
- **Generated blocks can be overwritten.** The generator should write atomically and `--check` should detect drift without modifying files.
- **Venue shortening can remove caveats.** Approved short templates must retain inferential limitations.
- **Canonical-only tooling can remain the silent default.** Update CI entry points, not just the underlying script.
- **Internal comments can leak into conversion.** Confirm the converter excludes them.
- **A source YAML can become a second manuscript.** Keep structured assertions and limited templates upstream rather than duplicating complete prose in several files.

## 6.12 Required checks

- `paper_a_transfer_text.py --check` verifies both manuscripts and all generated publication surfaces.
- Structural parity reports each block and its status.
- Claim coverage reports both manuscript paths in its transcript.
- A one-word central-claim mutation in either manuscript fails.
- Regeneration produces no diff on a clean tree.
- The canonical and venue abstracts are either identical or are an explicitly approved template pair with the same assertion set.

## 6.13 Acceptance criteria for P1-1

P1-1 is closed only when:

- one upstream scientific claim representation controls both active manuscripts;
- central blocks cannot be independently edited without detection;
- claim coverage audits both manuscripts by default;
- the current active abstracts are materially scientifically aligned;
- mutation tests detect central-claim drift in either direction; and
- CI no longer describes curated phrase matching as whole-document content agreement.

---

# 7. P1-2 — Bind estimand direction and the complete resampling design

## 7.1 Objective

Prevent a reversed loss contrast, incorrect favourable direction, false interval label, or incorrect design metadata from passing the contract/oracle chain and silently producing scientifically inverted or misleading prose.

## 7.2 Method summary

1. Replace the free-text estimand and separate direction default with one typed estimand specification.
2. Derive favourable sign, operand, bound interpretation, labels, and prose from that specification.
3. Require the validated estimand in every publication renderer; remove defaults.
4. Separate declared resampling specifications from independently source-derived realizations.
5. Exact-validate all top-level, scheme, census, membership, grind, count, distribution, and hash fields.
6. Bump the artifact schema and reject legacy objects unless explicitly migrated.
7. Run the complete reproduced mutation set against the full artifact/text chain.

## 7.3 Replace free-text estimand declarations with a typed object

### Recommended type model

Use primitive scientific facts and derive favourability rather than storing unrelated declarations. For example:

```python
from dataclasses import dataclass
from enum import Enum

class MetricPreference(str, Enum):
    LOWER_IS_BETTER = "lower_is_better"
    HIGHER_IS_BETTER = "higher_is_better"

class ContrastOperation(str, Enum):
    LEFT_MINUS_RIGHT = "left_minus_right"
    RIGHT_MINUS_LEFT = "right_minus_left"

@dataclass(frozen=True)
class EstimandSpec:
    id: str
    metric_id: str
    metric_preference: MetricPreference
    left_operand: str
    right_operand: str
    operation: ContrastOperation
    units: str
```

For the current analysis:

```python
POOLED_MAPE_ESTIMAND = EstimandSpec(
    id="pooled_mape_model_minus_level_only_pp",
    metric_id="pooled_mape",
    metric_preference=MetricPreference.LOWER_IS_BETTER,
    left_operand="mechanistic_model",
    right_operand="o_trained_level_only_comparator",
    operation=ContrastOperation.LEFT_MINUS_RIGHT,
    units="percentage_points",
)
```

Derive:

- contrast label;
- zero interpretation;
- favourable sign;
- favourable operand;
- most- and least-favourable interval extremes; and
- publication wording.

The serialized artifact may include derived fields for transparency, but the validator must recompute and exact-compare them.

### Why derivation is preferable

If the metric is a loss, lower is better. For `left − right`, negative values favour the left operand. That relationship is mathematical and should not be separately typed into a prose constant. A change to the operation should deliberately change all favourability prose or fail validation.

## 7.4 Remove publication-facing defaults

Change APIs such as:

```python
favourable_extremes(interval_semantics)
```

so that they require the validated estimand or validated transfer-analysis object:

```python
favourable_extremes(interval_semantics, estimand=validated_analysis.estimand)
```

There should be no module-level default that silently assumes model-minus-comparator.

A missing, unknown, or inconsistent estimand should produce a named failure before rendering.

## 7.5 Replace free-text estimand prose with derived prose

Remove or deprecate `RESAMPLING_ESTIMAND` as a manually maintained sentence. Generate a description such as:

> Pooled MAPE for the mechanistic model minus pooled MAPE for the O-trained level-only comparator, in percentage points; negative values favour the mechanistic model.

The same function should supply:

- Methods text;
- table notes;
- figure captions;
- artifact labels;
- supplemental definitions; and
- test expectations.

## 7.6 Define a complete typed resampling-design contract

Separate each scheme into:

1. **declared scientific specification** — fields that define what the scheme means; and
2. **source-derived realization** — clusters, strata, samples, grinds, observations, counts, distributions, and hashes reconstructed from the CSV.

A scheme specification should include at least:

```text
name
role
label
rationale or rationale_id
strata fields
cluster-key fields
expected observation unit
whether clusters are nested
ordering rule
```

A realized scheme should include at least:

```text
n_clusters
n_strata
cluster_size_distribution
membership records
sample IDs per cluster
grinds per cluster
observation IDs per cluster
per-cluster observation count
stratum ID per cluster
canonical membership hash
n_observations
```

Top-level design fields should include:

```text
schema version
estimand object
interval kind
predictor-refit status
primary scheme
scheme order
complete scheme map
source dataset identity/hash
```

## 7.7 Exact-validate every declared field

The contract validator should exact-compare the artifact with canonical declared specifications for:

- schema version;
- estimand ID and all primitive estimand fields;
- interval kind;
- predictor-refit status;
- primary scheme;
- scheme order;
- scheme names;
- roles;
- labels;
- rationales or rationale IDs;
- strata fields;
- cluster-key fields; and
- any nesting or ordering rules.

Do not accept any declared scheme merely because its name appears in the artifact. Unknown names, extra schemes, missing schemes, duplicate names, and order changes must fail.

## 7.8 Preserve oracle independence while broadening its scope

The independent source oracle should continue to parse `bioactives.csv` directly and implement the four grouping schemes independently. It should not import the producer’s cluster builder.

It should reconstruct and compare:

- exact cluster IDs;
- exact stratum IDs;
- exact observation IDs;
- exact sample IDs;
- exact grinds;
- per-cluster observation counts;
- cluster count;
- stratum count;
- cluster-size distribution;
- total observations; and
- canonical membership hash.

The expected census remains:

| Scheme | Clusters | Strata | Cluster-size distribution | Observations |
|---|---:|---:|---|---:|
| `cond_in_variety` | 26 | 2 | 3×8, 6×18 | 132 |
| `sample_in_variety_grind` | 44 | 4 | 3×44 | 132 |
| `cond_in_group` | 78 | 6 | 1×24, 2×54 | 132 |
| `group` | 6 | 1 | 22×6 | 132 |

The hard-coded census should be a secondary alarm. Exact source-derived membership remains authoritative.

### Layered independence model

Use two complementary checks:

1. **Contract check:** pins non-data declarations such as role, label, rationale, fields, interval kind, and primary status.
2. **Independent oracle check:** reconstructs data-derived membership and census without using producer grouping functions.

This avoids pretending that a CSV can independently determine an authorial rationale while still ensuring that every serialized field is validated.

## 7.9 Canonical serialization and hashing

Use deterministic serialization:

- sort mapping keys;
- sort cluster records by a documented key;
- sort sample, grind, and observation lists deterministically;
- use a fixed JSON separator/encoding;
- reject NaN/Infinity;
- normalize integer keys to strings only at the serialization boundary; and
- include a schema version.

A self-hash is not sufficient. The checker must first reconstruct the expected content independently and then compare both content and hash. Refreshing a hash over false data must not restore a green result.

## 7.10 Schema migration

Increment the transfer artifact’s schema version. Do not silently reinterpret old artifacts under the new validator.

Provide one of:

- a one-time deterministic migration script that reads the old artifact, rebuilds the design from source, and writes the new schema; or
- a clean regeneration path from the source producer.

The checker should reject the previous schema version with a clear message such as:

```text
resampling_design.schema_version: expected 4, found 3; regenerate the Paper A transfer artifact
```

Use the actual next version in the repository; `4` is illustrative if that is indeed the next version.

## 7.11 Required mutation tests

Each of the following mutations must fail the **full** `paper_a_transfer_artifacts.py --check` chain with a specific diagnostic:

| Mutation | Expected failure |
|---|---|
| Reverse estimand operation | `estimand.operation mismatch` or equivalent |
| Change interval kind to calibrated 95% CI | `interval_kind mismatch` |
| Change nested schema version | `schema_version mismatch` |
| Reverse scheme order | `scheme_order mismatch` |
| Change scheme role | `scheme.role mismatch` |
| Change scheme label | `scheme.label mismatch` |
| Change declared strata | `scheme.strata mismatch` |
| Change cluster key | `scheme.cluster_key mismatch` |
| Change `n_strata` | source-oracle census mismatch |
| Change size distribution | source-oracle distribution mismatch |
| Change rationale | `scheme.rationale mismatch` |
| Change grinds and refresh self-hash | source-oracle membership mismatch |
| Delete a sample ID from one cluster | source-oracle membership mismatch |
| Duplicate an observation ID | duplicate/coverage failure |
| Add an unknown scheme | unexpected-scheme failure |
| Remove a required scheme | missing-scheme failure |
| Change predictor-refit status | predictor-refit contract failure |
| Change primary scheme | primary-scheme contract failure |

## 7.12 Renderer-direction test

Add a dedicated end-to-end test:

1. build a valid artifact with model-minus-comparator;
2. confirm that negative favours the model and the lower bound is the more favourable extreme;
3. construct a separately valid comparator-minus-model estimand;
4. confirm that the rendered sign explanation and favourable extreme deliberately reverse; and
5. confirm that changing only serialized prose while leaving the typed operation unchanged fails validation.

The renderer must never retain “negative values favour the mechanistic model” after the operation has been reversed.

## 7.13 Potential pitfalls, errors, and oversights

- **Circular oracle:** importing the producer’s grouping function into the oracle would make both fail identically.
- **Self-hash false assurance:** a refreshed hash over false membership is still false membership.
- **Non-deterministic ordering:** sets or dictionary insertion order can create unstable hashes.
- **Alias drift:** sample IDs, grind labels, and solute names must be normalized by explicit rules, not ad hoc string cleanup.
- **Free-text rationale:** compare it to one canonical value or use a stable rationale ID plus generated prose.
- **Metric-direction assumptions:** not every future metric will be lower-is-better; keep this explicit in the type.
- **Unknown enums:** reject, do not fall back.
- **Legacy artifact acceptance:** do not let optional defaults make an old schema appear valid.
- **Renderer bypass:** all publication helpers must require the validated analysis object; direct imports of a default sign convention should be prohibited by test or static check.

## 7.14 Required checks

- Source census independently reproduces all four scheme counts and distributions.
- Exact membership comparison includes samples, grinds, and observations.
- Every Round 10 reproduced mutation fails the full checker.
- The artifact cannot claim a calibrated CI while the analysis status remains sensitivity-only.
- The renderer has no default estimand direction.
- Generated Methods, table notes, and captions use the same derived estimand wording.
- Artifact regeneration is deterministic under a fixed source and environment.

## 7.15 Acceptance criteria for P1-2

P1-2 is closed only when:

- one structured estimand object controls calculation, validation, and prose;
- favourable direction is derived, not independently hard-coded;
- the full declared design is exact-pinned;
- the independent oracle compares all source-derived membership facts, including grinds;
- refreshing a hash over false data cannot pass;
- every reproduced mutation fails the full chain; and
- changing the estimand operation cannot leave favourability prose unchanged.

---

# 8. P1-3 — Make interval semantics and records exact, typed, and fail-closed

## 8.1 Objective

Ensure that an interval record cannot:

- accept booleans, numeric strings, NaN, or infinity as bounds;
- omit required fields;
- carry contradictory width, zero relation, contact, or display data;
- falsely label a sensitivity range as a calibrated confidence interval; or
- cause uncaught exceptions instead of a named validation problem.

## 8.2 Method summary

1. Define an exact versioned interval schema and one canonical constructor.
2. Reject booleans, strings, missing values, NaN, and infinities before classification.
3. Derive full-precision zero geometry, contact, width, nearest bound, and display fields from validated primitives.
4. Rebuild a canonical record during validation and deep-compare every stored field.
5. Remove boolean coercion and silent defaults; return named problems for malformed records.
6. Require validated typed records in all consumers.
7. Cover valid geometry, invalid primitives, every reproduced false green, and randomized property cases.

## 8.3 Define one canonical interval type

Use a frozen type for validated interval primitives and derived semantics. For example:

```python
@dataclass(frozen=True)
class IntervalSemantics:
    lower: float
    upper: float
    relation_to_zero: ZeroRelation
    touches_zero_at_lower: bool
    touches_zero_at_upper: bool
    signed_nearest_bound_to_zero: float
    width: float
```

Keep the interval kind separate but typed:

```python
class IntervalKind(str, Enum):
    FIXED_PREDICTOR_CLUSTERED_SENSITIVITY = (
        "fixed_predictor_clustered_sensitivity_range"
    )
```

The artifact record should be created only through a canonical constructor.

## 8.4 Strict numeric validation

Implement a helper along these lines:

```python
def require_finite_json_number(value: object, path: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValidationError(f"{path}: expected finite JSON number, got {type(value).__name__}")
    result = float(value)
    if not math.isfinite(result):
        raise ValidationError(f"{path}: expected finite number, got {result!r}")
    return result
```

This deliberately rejects:

- `True` and `False`, despite `bool` being an `int` subclass in Python;
- strings such as `"0.1"`;
- `None`;
- lists or mappings;
- `NaN`;
- `+Infinity`; and
- `−Infinity`.

Also configure JSON handling strictly:

- serialize with `allow_nan=False`;
- reject non-standard constants during parsing; and
- never rely on Python’s permissive default JSON treatment of NaN/Infinity.

## 8.5 Validate bounds and exact zero geometry

After type validation:

1. require `lower <= upper`;
2. classify the closed interval as exactly one of:
   - `below_zero` when `upper < 0`;
   - `contains_zero` when `lower <= 0 <= upper`;
   - `above_zero` when `lower > 0`;
3. separately derive exact contact:
   - `touches_zero_at_lower = (lower == 0.0)`;
   - `touches_zero_at_upper = (upper == 0.0)`;
4. derive width as `upper - lower`;
5. derive the signed nearest bound to zero; and
6. preserve full-precision geometry independently of rounded display text.

Treat `−0.0` consistently. Canonicalize it to `0.0` for display and contact fields, while preserving the correct containing relation.

## 8.6 Canonical record construction

The only supported construction path should resemble:

```python
record = interval_record(
    lower=validated_lower,
    upper=validated_upper,
    display_digits=3,
    kind=IntervalKind.FIXED_PREDICTOR_CLUSTERED_SENSITIVITY,
)
```

The constructor should derive:

- kind identifier;
- full-precision bounds;
- contains/excludes-zero booleans;
- exact lower/upper zero contact;
- signed nearest bound;
- width;
- display digits;
- rounded display lower/upper;
- display text; and
- any display-specific zero-rounding indicator.

If a display field means “rounds to zero” rather than “exactly touches zero,” rename it accordingly in the next schema. Avoid using one `touches_zero` name for two different concepts.

## 8.7 Exact schema validation

Define the required key set. Reject missing and unexpected keys unless a documented schema-version migration explicitly allows them.

Validation should:

1. validate primitive fields and exact types;
2. construct a canonical record from full-precision bounds, display precision, and expected interval kind;
3. deep-compare every stored derived field with the canonical record; and
4. return a validated typed object or a list of named problems.

Fields to compare include at least:

- `kind`;
- lower and upper bounds;
- `contains_zero_full_precision`;
- `excludes_zero_full_precision`;
- exact lower/upper contact fields;
- `signed_nearest_bound_to_zero_pp`;
- `width_pp`;
- display digits;
- display lower;
- display upper;
- display text; and
- display zero-contact/rounding status.

Do not use `bool(value)`. Require `type(value) is bool` and exact equality.

## 8.8 Named errors instead of uncaught exceptions

Wrap parsing, formatting, decimal conversion, and deep comparison so that malformed records produce diagnostics such as:

```text
intervals[40g].display.lower: expected -0.829, found 999.0
intervals[40g].contains_zero_full_precision: required boolean field missing
intervals[40g].lower_pp: numeric strings are not accepted
intervals[40g].upper_pp: non-finite value Infinity
intervals[40g].kind: expected fixed_predictor_clustered_sensitivity_range,
                      found calibrated_95_percent_confidence_interval
```

The artifact checker should report all independent interval problems in one run where practical, rather than stopping at the first malformed field.

## 8.9 Reduce unnecessary duplication

Review every stored interval field and ask whether any consumer genuinely requires it.

- If not needed, remove it in the new schema.
- If retained for transparency or convenient rendering, exact-validate it.
- Require publication consumers to accept only the validated typed record, not an unchecked dictionary.

The goal is not to maximize fields. It is to ensure that every retained field is trustworthy.

## 8.10 Unit and mutation test matrix

### Valid geometry cases

- wholly negative interval;
- wholly positive interval;
- interval crossing zero;
- exact zero at lower bound;
- exact zero at upper bound;
- degenerate `[0, 0]` interval;
- degenerate non-zero interval;
- values that round to zero but do not exactly touch zero; and
- negative zero inputs.

### Invalid primitive cases

- lower is `True`;
- upper is `False`;
- numeric strings;
- `None`;
- lists/mappings;
- NaN;
- positive infinity;
- negative infinity;
- lower greater than upper; and
- display digits that are boolean, non-integer, negative, or above the supported maximum.

### Contradictory record mutations

Every reproduced Round 10 false green must fail:

- wrong `kind`;
- wrong width;
- wrong signed nearest bound;
- wrong display lower;
- wrong display upper;
- wrong display zero-contact status;
- missing `excludes_zero_full_precision`;
- missing `contains_zero_full_precision`;
- string `"false"` in a boolean field;
- unexpected extra field;
- wrong exact-contact flag;
- wrong display text; and
- changed display precision without updating the display fields.

### Property tests

Where the project permits, add randomized tests over finite ordered bounds. For each generated pair:

- construction followed by validation must pass;
- any single derived-field mutation must fail;
- relation categories must be mutually exclusive and exhaustive; and
- width must be non-negative and exactly derived.

## 8.11 Integration tests

- The recursive artifact checker must validate every interval record, including endpoint and fitting-loss alternatives.
- A malformed interval should produce a non-zero check exit status.
- The text renderer must refuse an unvalidated interval object.
- Display rounding must never change the full-precision relation used for scientific prose.
- Regeneration followed by `--check` must be idempotent.

## 8.12 Potential pitfalls, errors, and oversights

- **Python boolean coercion:** `bool("false")` is `True`; never coerce.
- **NaN comparison behavior:** NaN can bypass ordinary equality logic; reject before comparison.
- **JSON permissiveness:** Python may serialize or parse non-standard NaN/Infinity unless explicitly prohibited.
- **Rounded zero:** `+0.0038` displayed to two decimals becomes `0.00` but does not exactly touch zero.
- **Negative zero:** normalize display without losing geometric meaning.
- **Floating-width equality:** build the canonical record from the same validated primitives and compare deterministic serialized values.
- **Legacy fields:** optional defaults can recreate false greens; migrate or reject old schemas explicitly.
- **Broad exception handling:** do not convert programmer errors into silent validation success.
- **Kind labels:** never allow free text such as “95% CI” where the method is a sensitivity range.

## 8.13 Acceptance criteria for P1-3

P1-3 is closed only when:

- invalid primitive inputs are rejected before classification;
- every required field and exact type is enforced;
- every derived field is reconstructed and exact-compared;
- no `bool(...)` coercion remains in interval validation;
- malformed records return named failures;
- all reproduced false greens are covered by tests and fail;
- all interval consumers require validated records; and
- current correct intervals still render exactly as intended.

---

# 9. P2-1 — Remove process leakage and make the scanner robust to line wrapping

## 9.1 Objective

Ensure that no submission-ready file contains review history, correction narration, producer/test identifiers, or internal repository paths that an editor should not receive, and ensure that the automated gate catches such text even when it is split across physical lines.

## 9.2 Method summary

1. Replace active review-history narration with the current scientific fact only.
2. Separate internal figure-production mapping from the file that is actually uploaded.
3. Define one complete manifest of publication-facing files and source templates.
4. Strip hidden comments while preserving line positions, then scan normalized visible Markdown blocks rather than physical lines.
5. Use precise rule classes for review history, internal implementation narration, and internal paths.
6. Test every prohibited phrase at every token-boundary line wrap and on every publication surface.
7. Scan and manually inspect the built upload package, not only the source tree.

## 9.3 Correct the active manuscript sentence

Replace the current review-history narration with the current scientific fact only. Recommended text:

> Measured complete-cup concentrations are available across all 15 experiments and are the reference for the 27.8/38.3/30.7% sampled-aggregate audit. The full fraction-versus-measured-cup rate-profile contrast has not yet been run.

This preserves the useful correction without telling the reader that an earlier draft was wrong.

## 9.4 Split internal figure mapping from upload-ready captions

Create two clearly named files:

1. **Internal repository mapping**, for example:
   - `docs/figures/PAPER_A_FIGURE_MAP_INTERNAL.md`

   This may contain:
   - producer identifiers;
   - module paths;
   - test paths;
   - prior numbering notes;
   - review history; and
   - links between generated images and manuscript figure numbers.

2. **Upload-ready caption file**, for example:
   - `docs/submission/PAPER_A_JFE_FIGURE_CAPTIONS.md`

   This should contain only:
   - final figure numbers;
   - final captions;
   - panel definitions;
   - symbol/line/color definitions needed by readers; and
   - no repository/test/review preamble.

Update package manifests and submission assembly to include only the upload-ready file.

Do not merely rename the existing file while leaving it in the package. Verify the package input list.

## 9.5 Define the complete publication-surface set

The scanner should explicitly cover every source or output capable of reaching a reader, including at least:

- canonical manuscript;
- venue manuscript;
- supplement;
- cover letter;
- highlights;
- front-matter YAML or other templates;
- significance statement;
- package/combined manuscript source;
- upload-ready captions;
- figure descriptions/alt text;
- generated claim-block sources; and
- any journal response or summary included in the submission package.

Maintain this list in one manifest. A test should fail if a new file is added to the submission package but not to the scan manifest.

## 9.6 Replace physical-line scanning with visible-block scanning

### Recommended algorithm

1. Read the file while preserving line endings and source line numbers.
2. Remove HTML comments by replacing comment characters with spaces but preserving newline positions.
3. Parse visible Markdown into blocks:
   - headings;
   - paragraphs;
   - list items;
   - block quotes;
   - table cells or rows where practical;
   - captions; and
   - optionally code blocks as a distinct block type.
4. Join wrapped continuation lines inside each visible block with a single space.
5. Normalize Unicode whitespace and case for matching, but preserve a character-to-source-line map.
6. Apply phrase and path rules to the normalized block.
7. Report file, start line, end line, matched phrase, and rule ID.

The key requirement is that:

```text
An\nearlier version
```

is scanned as the visible phrase `an earlier version`.

### Diagnostic example

```text
PAPER_A_JFE_MANUSCRIPT.md:1025-1027 [PROCESS_HISTORY_EARLIER_VERSION]
visible paragraph contains prohibited phrase: "an earlier version"
```

## 9.7 Separate rule classes

Use at least three rule classes:

### A. Review/process-history language

Examples:

- `an earlier version`;
- `the second review`;
- `the third review`;
- `reviewer asked`;
- `previously carried`;
- `that was wrong`;
- `we corrected` when referring to draft history rather than scientific correction; and
- similar explicit production-history language.

### B. Internal implementation narration

Examples:

- `producer identifier`;
- `generated by tools/...`;
- test-module names;
- artifact-builder names;
- internal fixture names; and
- repository-only figure-number mapping prose.

### C. Internal paths

Detect visible paths beginning with:

- `docs/`;
- `tools/`;
- `tests/`;
- `puckworks/`;
- `.github/`.

Apply narrow, section-aware allowances only where a genuine data/code availability statement is intended for readers. An allowance should be tied to a specific section and rule, not a broad file-level exemption.

## 9.8 Handle comments, code, references, and legitimate uses carefully

### HTML comments

Exclude them from reader-visible phrase checks, but preserve line mapping. Confirm that the journal conversion also removes them.

### Code blocks and inline code

- Process-history language in a code block is normally not submission prose, but an upload-ready caption file should contain no such block anyway.
- Internal paths in a data/code availability section may be legitimate, but should preferably be public repository URLs or archive identifiers rather than local paths.

### References

Avoid over-broad patterns such as the single word `previously`, which would create false positives in ordinary scientific prose. Use precise phrases and rule IDs.

### Hyphenation and punctuation

Normalize repeated whitespace and Unicode dashes. Consider token matching that tolerates punctuation between terms without matching unrelated sentences.

## 9.9 Required scanner tests

For every prohibited multi-token phrase:

1. inject it on one line and require failure;
2. split it at every token boundary and require failure;
3. split it across three lines and require failure;
4. vary capitalization and require failure;
5. use multiple spaces/tabs and require failure;
6. place it inside an HTML comment and confirm the visible-prose rule does not fire;
7. place it in the upload-ready captions and require failure;
8. place it in the internal mapping file and confirm that file is not treated as an upload surface; and
9. place an internal path in an allowed data/code availability block and confirm only the narrow allowlist applies.

Add tests for each publication surface, not just the manuscript and supplement.

## 9.10 Package-level checks

After building the submission package:

- list every included file;
- run the visible-block scanner over the built package contents;
- search the package recursively for internal paths and review phrases;
- confirm that the internal figure map is absent; and
- inspect the first page/section of the upload-ready caption file.

A clean source tree is not sufficient if the package assembly includes a stale generated file.

## 9.11 Potential pitfalls, errors, and oversights

- **Line mapping loss:** naïvely collapsing the whole file makes diagnostics unusable.
- **False positives:** patterns such as `previously` are too broad without context.
- **False negatives at Markdown boundaries:** list items, table cells, and wrapped captions need block-aware handling.
- **Comment leakage:** a converter may retain comments even if the scanner ignores them; test the rendered output.
- **Allowlist creep:** broad exemptions for code/data availability can hide internal paths elsewhere.
- **Package drift:** a clean source file may not be the file actually uploaded.
- **Misnamed file:** a document called “submission-ready” may still contain an internal preamble; inspect contents, not titles.
- **Hidden source templates:** scanning only rendered files permits an old template to regenerate prohibited prose later.

## 9.12 Acceptance criteria for P2-1

P2-1 is closed only when:

- the active manuscript contains current science rather than draft-history narration;
- internal figure mapping and upload-ready captions are separate;
- the submission package includes only the upload-ready caption file;
- the scanner operates on normalized visible blocks rather than isolated lines;
- canonical and all reader-facing source templates are scanned;
- internal paths across all required prefixes are detected with narrow allowances;
- line-wrap mutations fail at every token boundary; and
- a package-level manual inspection finds no review, producer, fixture, test, or repository narration.

---

# 10. Preserve the Round 10 items already checked clean

The remediation must not regress the following accepted corrections.

## 10.1 Interval geometry and favourable-bound interpretation

Preserve:

- closed-interval zero relation;
- separate exact-contact flags;
- negative values favouring the model for model-minus-comparator loss;
- the lower bound as the more favourable extreme under that estimand; and
- the 40 g upper bound as small and positive, not exact zero contact.

Add regression tests so that these remain true after the estimand/interval refactor.

## 10.2 Audit-scope discipline

Preserve the statement that the multi-seed audit applies only to:

- 40 g;
- `cond_in_variety`; and
- primary fitting loss.

Continue to report lower and upper standard errors separately. Do not let other endpoints, secondary schemes, or alternative loss inherit that audit.

## 10.3 Endpoint-row fail-closed behavior

Retain the tests for:

- missing rows;
- empty collections;
- malformed records;
- missing keys;
- duplicate endpoints;
- extra endpoints;
- non-finite values;
- non-numeric values; and
- retired keys.

The interval validator refactor must not weaken this collection-level validation.

## 10.4 Independent source membership

Preserve the corrected exact source membership and the closure of the solute-swap/wrong-condition-cluster defects. Broaden the oracle; do not replace it with producer self-validation.

## 10.5 Figure semantics

Preserve:

- Figure 1’s distinct colour/style encodings that remain distinguishable in grayscale; and
- Figure S3 panel (b)’s neutral bars and zero line without undocumented significance-like threshold colours.

No visual change is required merely because the captions are being cleaned.

## 10.6 Stale-number status

The Round 10 stale-number category was empty. Add a cross-surface numerical consistency test so that the remediation retains:

- 8.44% model pooled MAPE at 40 g;
- 8.83% comparator pooled MAPE;
- −0.394 pp model-minus-comparator difference;
- 62/132 model-worse count at 40 g;
- the accepted endpoint values and ranges; and
- the accepted audit standard errors.

---

# 11. File-by-file implementation map

This table identifies the likely change surfaces. Exact paths should be confirmed against the branch before editing.

| File or module | Planned change | Finding(s) |
|---|---|---|
| `puckworks/paper_a/transfer_contract.py` | Add typed estimand/inferential-status serialization; complete resampling validation; strict interval record validation; schema bump | P0-1, P1-2, P1-3 |
| `puckworks/paper_a/transfer_semantics.py` | Reject invalid bounds; derive favourability from required estimand; remove publication default | P1-2, P1-3 |
| `puckworks/paper_a/source_resampling_oracle.py` | Compare grinds, samples, per-cluster counts, strata counts, distributions, hashes, and complete source-derived realization | P1-2 |
| `tools/paper_a_transfer_artifacts.py` | Require complete validated transfer-analysis object; report named failures; strict JSON; full mutations | P0-1, P1-2, P1-3 |
| `tools/paper_a_transfer_text.py` | Render evidence-limited claim blocks from validated facts/status; no direction default | P0-1, P1-1, P1-2 |
| `tools/paper_a_consistency.py` | Structural block parity; both manuscripts; visible-block scanner; expanded path/process rules | P0-1, P1-1, P2-1 |
| `puckworks/paper_a/claim_coverage.py` | Audit canonical and venue manuscripts by default | P1-1 |
| `docs/PAPER_A_DRAFT.md` | Replace active abstract/transfer blocks with generated accepted wording; remove active review history | P0-1, P1-1, P2-1 |
| `docs/submission/PAPER_A_JFE_MANUSCRIPT.md` | Replace categorical claim and process-history sentence; generated blocks | P0-1, P1-1, P2-1 |
| `docs/submission/PAPER_A_JFE_SUPPLEMENT.md` | Correct interpretation and rename/remove `skill` column | P0-1 |
| `docs/submission/paper_a_front_matter.yaml` | Correct abstract/significance source; bind to generated claim policy | P0-1, P1-1 |
| `docs/submission/PAPER_A_JFE_COVER_LETTER.md` | Correct central claim | P0-1 |
| package/highlight sources | Correct central claim and enforce generation | P0-1, P1-1 |
| `docs/figures/PAPER_A_CAPTIONS.md` | Retire or convert to internal map | P2-1 |
| new upload-ready caption file | Reader-only captions; package input | P0-1, P2-1 |
| transfer semantics/contract tests | Strict type, mutation, direction, and design coverage | P1-2, P1-3 |
| consistency/generated-text tests | Claim policy, block parity, line-wrap, complete surface coverage | P0-1, P1-1, P2-1 |
| new acceptance report | Record evidence against each Round 10 finding | All |

---

# 12. Detailed test and mutation matrix

## 12.1 Scientific-claim tests

| Test | Expected result |
|---|---|
| Current sensitivity-only status + “no resolvable skill” | Fail |
| Current status + “equivalent” | Fail |
| Current status + “statistically indistinguishable” | Fail |
| Current status + approved evidence-limited claim | Pass |
| Observed difference sign changed in one surface | Fail cross-surface consistency |
| 38 g negative range converted to superiority claim | Fail claim policy/manual review |
| `skill` column retained without formula | Fail supplement check |
| Relative MAPE reduction computed from rounded cells | Fail full-precision formula test |

## 12.2 Manuscript-parity tests

| Test | Expected result |
|---|---|
| Canonical abstract changes but venue does not | Fail |
| Venue endpoint synthesis changes but canonical does not | Fail |
| Required block missing | Fail |
| Duplicate generated marker | Fail |
| Approved venue-short template retains all assertion IDs | Pass |
| Venue-short template drops uncalibrated caveat | Fail |
| Claim coverage audits only one active manuscript | CI wrapper fails |

## 12.3 Estimand/design tests

Use every reproduced Round 10 mutation plus unknown/missing/extra scheme cases. Every mutation must fail the full checker, not merely a helper test.

## 12.4 Interval tests

Use every reproduced Round 10 false green plus exact-contact, rounded-zero, NaN, infinity, negative-zero, extra-field, and malformed-display cases.

## 12.5 Process scanner tests

For each prohibited phrase, generate all token-boundary wraps. Test all publication surfaces and package outputs. Include positive tests for narrow legitimate data/code availability text.

## 12.6 Numerical preservation tests

Compare regenerated full-precision results with the baseline invariant file. A wording-only remediation should produce zero numerical differences.

---

# 13. Implementation pitfalls that span more than one finding

## 13.1 Solving prose without solving its source

Hand-editing the manuscript can appear to close P0-1 while an older YAML/front-matter/template regenerates the retired sentence. Always identify the upstream source before editing a generated file.

## 13.2 Solving the contract with duplicated “expected” data

A producer and checker that import the same mutable dictionary can agree on the same error. Use:

- typed canonical declarations for authorial design facts;
- an independently coded source oracle for data-derived membership; and
- mutation tests against the complete executable chain.

## 13.3 Treating hashes as truth

Hashes establish identity, not correctness. Compare reconstructed content first; use hashes as a secondary integrity signal.

## 13.4 Replacing one overclaim with another

The correction must not become:

- “the model has skill” because point estimates are negative; or
- “the models are equivalent” because a sensitivity range contains zero.

The correct conclusion is about what the present analysis **does not establish**.

## 13.5 Breaking the accepted display convention

Do not reduce all intervals to two decimals merely to avoid explaining small endpoint values. That can make a small positive bound appear to be exact zero. Preserve full-precision semantics and the current careful three-decimal display caveat.

## 13.6 Allowing validators to mutate input

Validation should be pure. It should not silently insert defaults, normalize contradictory fields in place, or rewrite malformed records into passing form. Construction and validation should be separate operations.

## 13.7 Leaving bypass APIs

After introducing typed validated objects, remove or deprecate functions that accept unchecked dictionaries or use default estimands. Search the repository for all callers.

## 13.8 Updating tests to match a defect

When an existing golden file fails, determine whether the new output is scientifically correct. Do not automatically regenerate expected files and thereby bless an unintended change.

---

# 14. Recommended commit structure

Use reviewable commits with one scientific purpose each.

## Commit 1 — Baseline and numerical invariants

- add baseline invariant artifact;
- add preservation tests;
- no scientific or prose changes.

## Commit 2 — Typed transfer-analysis and estimand contract

- add estimand and inferential-status types;
- remove renderer direction defaults;
- complete design validation and oracle comparison;
- add design mutation tests;
- schema migration/regeneration.

## Commit 3 — Strict interval construction and validation

- reject invalid numeric inputs;
- canonicalize records;
- deep-compare all fields;
- add interval mutation/property tests.

## Commit 4 — Evidence-limited claim and shared generated blocks

- implement claim policy;
- revise abstract, Results, supplement, cover letter, highlights, captions;
- rename/remove S3 `skill`;
- generate canonical and venue blocks from one source;
- add parity and claim-policy tests.

## Commit 5 — Publication hygiene and scanner hardening

- replace active draft-history sentence;
- split internal and upload-ready caption files;
- add visible-block scanning, expanded path rules, and token-wrap tests;
- update package manifest.

## Commit 6 — Regenerated artifacts and final acceptance evidence

- regenerate all derived files;
- run full suite;
- add acceptance report and command transcripts;
- verify clean tree after `--check` commands.

This structure makes it possible to review scientific wording separately from validator internals while preserving dependency order.

---

# 15. Final verification procedure

## 15.1 Regeneration

Run the canonical producers/generators required by the repository. Then immediately run their `--check` modes and confirm no diff remains.

## 15.2 Required command chain

At minimum:

```bash
python tools/paper_a_transfer_artifacts.py --check
python tools/paper_a_transfer_text.py --check
python tools/paper_a_consistency.py verify
python -m puckworks.paper_a.slow_lane_bindings
python tools/claim_binding_audit.py
python -m pytest tests/test_paper_a_transfer_semantics.py \
                 tests/test_paper_a_transfer_contract.py \
                 tests/test_paper_a_model_contract.py \
                 tests/test_paper_a_figure_semantics.py -q
python -m pytest -q
```

Add the new focused tests to the explicit fast gate so that the most important Round 10 regressions are visible even before the full suite completes.

## 15.3 Clean-tree check

After regeneration and checks:

```bash
git status --short
git diff --check
```

A clean generation check should not modify tracked files.

## 15.4 Numerical parity report

Generate a before/after report with:

- every protected full-precision number;
- before value;
- after value;
- absolute difference;
- allowed difference; and
- pass/fail.

For a Path A wording/assurance remediation, the expected allowed difference is zero for deterministic values. Seed-audited stochastic outputs should be compared under the exact frozen seed/environment policy.

## 15.5 Cross-surface claim report

Generate a table that lists, for every publication surface:

- file;
- block ID;
- rendered central claim;
- estimand direction;
- point difference;
- interval kind;
- inferential-status class;
- banned-language scan result; and
- parity status.

This makes it easy to see whether one cover-letter or caption source escaped regeneration.

## 15.6 Mutation audit

Run all required mutations against the complete chain and retain the transcript. The transcript should show a named failure for every mutation; a generic crash is not sufficient unless the mutation is deliberately testing malformed file syntax.

## 15.7 Manual rendered review

Inspect the final rendered manuscript, supplement, and figures rather than only Markdown:

- abstract and headings;
- tables and notes;
- line wrapping around signs and units;
- caption package;
- Figure 1 and Figure S3 visual semantics;
- the 40 g small positive upper bound;
- any converted mathematical symbols;
- absence of internal comments or paths; and
- continuity of the scientific argument.

## 15.8 Submission-package audit

Build the actual upload package and verify:

- expected files only;
- upload-ready captions only;
- no internal figure map;
- no review-history language;
- no local paths or test names;
- no stale manuscript copy; and
- package hashes recorded.

---

# 16. Acceptance report structure

Create:

`docs/paper1_resource/PAPER_1_ROUND_10_REMEDIATION_ACCEPTANCE.md`

It should contain:

| Finding | Resolution | Code/doc changes | Tests | Mutation evidence | Manual check | Status |
|---|---|---|---|---|---|---|
| P0-1 | Path A evidence-limited claim | links/SHAs | test names | transcript section | continuous argument read | PASS/FAIL |
| P1-1 | shared generated blocks and dual coverage | links/SHAs | test names | drift mutations | abstract/block parity | PASS/FAIL |
| P1-2 | typed estimand/full design binding | links/SHAs | test names | all design mutations | Methods/table/caption sign read | PASS/FAIL |
| P1-3 | strict interval schema | links/SHAs | test names | all interval mutations | rendered range inspection | PASS/FAIL |
| P2-1 | clean prose and robust scanner | links/SHAs | test names | token-wrap mutations | package inspection | PASS/FAIL |

Also record:

- branch and head commit;
- tree SHA;
- source hash;
- artifact schema version;
- all command outcomes;
- total test counts;
- numerical parity result;
- generated file hashes; and
- known-open items that remain explicitly outside Round 10.

Do not mark a finding closed based solely on code review. Each row needs executable and manual evidence.

---

# 17. Definition of done

The Round 10 remediation is complete only when all of the following are true.

## Scientific claim

- [ ] Path A is recorded as the accepted decision.
- [ ] The observed small advantage is reported accurately.
- [ ] No active surface says “no resolvable skill,” “no skill,” “equivalent,” “non-distinguishable,” or a synonym unsupported by the analysis.
- [ ] The text does not claim superiority.
- [ ] The inferential-status contract prevents unsupported decision language.
- [ ] Supplementary Table S3 no longer uses undefined `skill` terminology.

## Source-of-truth alignment

- [ ] Canonical and venue manuscripts receive central claims from one upstream renderer.
- [ ] Structural parity covers the abstract, transfer Results, conclusion, and captions.
- [ ] Claim coverage audits both manuscripts by default.
- [ ] A one-word claim mutation in either manuscript fails CI.

## Estimand and design contract

- [ ] One typed estimand controls sign, favourability, labels, and prose.
- [ ] Publication renderers have no default direction.
- [ ] All top-level and per-scheme declarations are exact-validated.
- [ ] The independent oracle compares samples, grinds, observations, strata, counts, distributions, and hashes.
- [ ] Every Round 10 design mutation fails the full checker.

## Interval contract

- [ ] Booleans, strings, NaN, and infinities are rejected.
- [ ] Missing and unexpected fields fail.
- [ ] Every derived field is canonicalized and exact-compared.
- [ ] No boolean coercion remains.
- [ ] Every Round 10 interval mutation fails.
- [ ] Full-precision geometry remains separate from display rounding.

## Publication hygiene

- [ ] The manuscript states current facts without draft-history narration.
- [ ] Internal mapping and upload-ready captions are separate.
- [ ] Visible-block scanning catches line-wrapped phrases.
- [ ] All publication surfaces and templates are scanned.
- [ ] Internal paths are detected with narrow, explicit allowances.
- [ ] The built package contains no review, producer, test, fixture, or repository narration.

## Preservation and final validation

- [ ] Accepted numerical values are unchanged.
- [ ] Previously closed Round 9/10 geometry, audit-scope, endpoint-row, source-membership, and figure issues remain closed.
- [ ] All focused and full tests pass.
- [ ] Regeneration is deterministic and leaves a clean tree.
- [ ] The final rendered manuscript and package pass manual review.
- [ ] The Round 10 remediation acceptance report is complete and evidence-backed.

---

# 18. Recommended final reviewer recheck

After implementation, the next review should be deliberately narrow. It should answer only these questions:

1. **Claim:** Does every active surface say that the present analysis does not establish useful mechanistic transfer, rather than claiming that skill is absent?
2. **Alignment:** Are the canonical and venue manuscripts generated from the same scientific claim source?
3. **Estimand/design:** Can any reversed estimand, false interval label, altered role/strata/key metadata, or changed grind membership pass the full artifact chain?
4. **Intervals:** Can any invalid bound, missing field, wrong type, false width/contact/display field, NaN, or infinity pass validation?
5. **Publication hygiene:** Can line-wrapped review history or internal paths survive in any built submission file?
6. **Preservation:** Are all accepted numerical and visual results unchanged?

A pass on those six questions, supported by the acceptance evidence described above, would close the Round 10 submission blocker and major assurance findings without reopening the numerical work already checked clean.

---

## Final recommendation

Implement Path A and the assurance repairs in one controlled remediation branch, but keep the commits separable. Do not submit after a prose-only edit. The central wording, manuscript source architecture, estimand/design contract, interval validator, and publication scanner are coupled: leaving any one of them unchanged creates a plausible route for the retired claim or an inverted semantic interpretation to return under a green test chain.

The intended end state is not a weaker paper. It is a more defensible one: the mechanistic model has a small observed advantage, the current sensitivity analysis does not determine whether that increment is reproducible or practically useful, and the paper demonstrates why acceptable endpoint prediction alone is insufficient evidence of mechanistic transfer.
