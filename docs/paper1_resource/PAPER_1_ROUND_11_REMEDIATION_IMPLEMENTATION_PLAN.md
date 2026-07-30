# Paper 1 — Round 11 Remediation Implementation Plan

**Prepared:** 30 July 2026  
**Repository:** [`trbrewer/puckworks`](https://github.com/trbrewer/puckworks)  
**Reviewed commit:** [`baf6ef1e794ea2719e9036353d4d0b027a35accb`](https://github.com/trbrewer/puckworks/tree/baf6ef1e794ea2719e9036353d4d0b027a35accb)  
**Controlling brief:** [`PAPER_1_REVIEW_BRIEF_ROUND_11.md`](https://github.com/trbrewer/puckworks/blob/baf6ef1e794ea2719e9036353d4d0b027a35accb/docs/paper1_resource/PAPER_1_REVIEW_BRIEF_ROUND_11.md)  
**Source review:** `PAPER_1_ROUND_11_DETAILED_REVIEW.md`  
**Purpose:** implementation specification for closing every Round 11 finding; this document does **not** assert that any remediation has already been implemented.

---

## 1. Required disposition

The Round 11 review found one P0 submission blocker, six P1 major assurance defects, and one P2 editorial/generation defect. The remediation should not be treated as complete merely because the manuscript wording has been changed. The P0 recurrence occurred while the policy checks were green; therefore, the prose correction and the mechanism that prevents recurrence must land together.

The correct completion standard is:

1. remove the unsupported practical/equivalence-adjacent conclusions from every Paper 1 reader-facing surface;
2. retain the observed model-favouring result prominently and exactly;
3. harden the claim, inferential-status, source, interval, scanner, and caption contracts so the reproduced false greens fail;
4. regenerate affected deliverables from their authoritative sources;
5. run the complete Round 11 assurance chain, with an explicit distinction between **PASS**, **FAIL**, and **NOT RUN**; and
6. record the evidence in a remediation acceptance report tied to an immutable commit.

A check that is skipped, unavailable because of a missing optional dependency, or returns early without performing its intended comparison must **not** be represented as passing.

---

## 2. Protected scientific and numerical invariants

The remediation is primarily a claim-and-assurance correction. These values must remain unchanged unless a separately authorized science change is made:

| Endpoint | Mechanistic-model pooled MAPE | Level-only comparator | Model minus comparator | Primary full-precision range | Model worse on |
|---|---:|---:|---:|---:|---:|
| 38 g | 8.39% | 8.83% | −0.447 pp | [−0.884387, −0.042433] | 61/132 |
| 40 g | 8.44% | 8.83% | −0.394 pp | [−0.829052, +0.003791] | 62/132 |
| 42 g | 8.41% | 8.83% | −0.425 pp | [−0.891251, +0.005844] | 60/132 |

The following interpretive invariants must also be preserved:

- negative model-minus-comparator pooled-MAPE differences favour the mechanistic model;
- the observed 40 g point estimate favours the mechanistic model by 0.394 percentage points;
- the reported ranges are fixed-predictor sensitivity ranges without calibrated coverage;
- no practical margin was predeclared;
- the current analysis establishes neither superiority, non-inferiority, equivalence, practical usefulness, nor absence of incremental value; and
- acceptable endpoint accuracy alone does not establish transfer of the kinetic mechanism.

### Producer-rerun rule

Do **not** rerun `python tools/paper_a_transfer_artifacts.py --write` merely because text, policy, validation, or caption code changed. Run the science producer only if one of the following occurs:

- source-corpus membership changes;
- the normalized partition or design hash changes;
- the estimand changes;
- an archived numerical result artefact changes or becomes invalid;
- a source/design correction alters a downstream calculation; or
- the existing artefacts can no longer be verified against the corrected contracts.

If the strict source parser introduced under P1-4 reproduces the same 44-record/132-observation corpus, identical membership, identical partitions, and identical hashes, use the existing artefacts and document why no producer rerun was required.

---

## 3. Implementation sequence and dependencies

The work should be implemented in the following order.

| Order | Work package | Findings | Dependency/reason |
|---:|---|---|---|
| 1 | Restore the evidence-bounded manuscript claim and add recurrence tests | P0-1, part of P1-1 | Submission blocker; must not be merged as prose-only remediation |
| 2 | Replace disclaimer-window logic and expand decision-language taxonomy | P1-1 | Makes the P0 correction enforceable |
| 3 | Extend positive-claim coverage to highlights and Figure 3 | P1-3 | Standalone surfaces must carry the evidence boundary |
| 4 | Bind inferential authority to verified evidence | P1-2 | Prevents future status objects from licensing unsupported prose |
| 5 | Harden source metadata, coordinate identity, and lookup support | P1-4 | Closes remaining common-mode source assumptions |
| 6 | Make interval/status numeric validation total | P1-5 | Ensures malformed data is rejected rather than crashing the gate |
| 7 | Replace pseudo-rendered scanning with structural Markdown scanning | P1-6 | Closes markup, link-target, and scope bypasses |
| 8 | Parse caption sections structurally and validate output invariants | P2-1 | Uses the same structural parsing direction as P1-6 |
| 9 | Regenerate deliverables, run the complete chain, and issue an acceptance report | All | Final proof that the corrected state is coherent and reproducible |

Recommended commit boundaries are given in §13.

---

# 4. P0-1 — Remove unsupported “adds little / incremental skill is small / nearly matched” conclusions

## 4.1 Objective

Replace every property-level or practical-magnitude verdict with a precise statement of:

1. the observed values and sign;
2. the limited numerical magnitude, stated quantitatively rather than as an inferential adjective;
3. the uncalibrated nature of the ranges and absence of a predeclared practical margin; and
4. symmetrical non-establishment: the analysis establishes neither a reproducible/practically useful advantage nor equivalence/absence of incremental value.

The correction must preserve the real result. It must not respond to the overreach by obscuring the −0.394 pp model-favouring point estimate.

## 4.2 Affected locations and surfaces

At minimum, edit both:

- `docs/submission/PAPER_A_JFE_MANUSCRIPT.md`; and
- `docs/PAPER_A_DRAFT.md`.

Address the occurrences identified in the review:

- Introduction §1.3: “adding little”;
- Results/robustness synthesis: “incremental skill ... is small”;
- Discussion/Conclusions: repeated “incremental skill ... is small” formulations;
- strength-ladder conclusion: “incremental skill ... is small”; and
- standing-position paragraph: “nearly matched”.

Then scan **all actual Paper 1 upload deliverables**, not only those two files, for exact and variant forms.

## 4.3 Method

### Step 1 — Establish canonical evidence-safe language

Use three canonical components. They may be rendered in longer or shorter form, but their meaning must remain unchanged.

**Observed comparison**

> At 40 g, observed pooled MAPE was 8.44% for the mechanistic model and 8.83% for the level-only comparator, a model-minus-comparator difference of −0.394 percentage points.

**Decision boundary**

> The reported fixed-predictor sensitivity ranges are uncalibrated and no practical margin was predeclared; this analysis therefore does not establish superiority, non-inferiority, equivalence, practical usefulness, or absence of incremental value.

**Transfer boundary**

> Acceptable endpoint accuracy alone does not establish transfer of the kinetic mechanism.

Where space is limited, retain the quantitative magnitude and symmetrical non-establishment. Do not shorten the wording to a one-sided statement such as “superiority was not established,” because that still leaves room for an unsupported equivalence or absence conclusion.

### Step 2 — Apply paragraph-level replacements

Do not perform blind phrase substitution if it leaves the surrounding paragraph grammatically or logically inconsistent. Rewrite each affected paragraph around the canonical components.

Recommended paragraph-level formulations are:

**Introduction/positioning formulation**

> The transferred process model produced a model-favouring observed pooled-MAPE difference of less than half a percentage point relative to a level-only comparator. Because the reported ranges are uncalibrated fixed-predictor sensitivities and no practical margin was predeclared, the analysis does not determine whether that observed advantage is reproducible or practically useful, and it does not establish equivalence or absence of incremental value.

**Results/Discussion formulation**

> At 40 g, observed pooled MAPE was 8.44% for the mechanistic model and 8.83% for the level-only comparator, a model-minus-comparator difference of −0.394 percentage points. The reported fixed-predictor sensitivity ranges are uncalibrated and no practical margin was predeclared; this analysis therefore establishes neither a reproducible or practically useful advantage nor equivalence or absence of incremental value.

**Standing-position formulation**

> After target-specific optimal-grind recalibration, the mechanistic model’s observed pooled MAPE was 8.44% versus 8.83% for the level-only comparator. The observed advantage was less than half a percentage point, but the present analysis does not determine whether it is reproducible or practically useful and does not establish equivalence or absence of incremental value.

Prefer “less than half a percentage point” over “small.” The former is a quantitative description; the latter can become a practical-magnitude decision unless a margin defines what “small” means.

### Step 3 — Remove equivalent verdicts, not only the exact words

Search for and adjudicate at least the following classes:

```text
adds little
adding little
offers little
incremental skill is small
small incremental skill
minimal incremental value
marginal benefit
negligible improvement
nearly matched
effectively matched
essentially the same
performs comparably
within noise
no practical advantage
no material advantage
no meaningful gain
only a marginal benefit
```

A phrase may be retained only if it is clearly a quoted historical statement in a non-uploaded review record. It must not remain in a reader-facing Paper 1 surface.

### Step 4 — Preserve manuscript/canonical agreement

Where content is generated, modify the authoritative source and regenerate both manuscripts. Where narrative is authored independently, update both files in the same commit and add an exact or normalized parity assertion for the affected block.

Do not edit only the generated output. Do not edit only the canonical draft and assume conversion will catch up later.

### Step 5 — Add a ratchet test before merging the prose

The exact retired sentences and paraphrases must be added to the claim-policy mutation suite. The P0 text change should not merge until the policy fails those mutations.

## 4.4 Potential pitfalls, errors, and oversights

- **Over-correction:** removing the point estimate or burying it under caveats would misrepresent the result.
- **One-sided caution:** “superiority was not established” is insufficient if the paragraph then implies equivalence or absence.
- **Qualitative magnitude language:** “small,” “minor,” “marginal,” and “negligible” can become practical decisions without a declared margin.
- **Observed versus established:** “the model had lower observed MAPE” is descriptive; “the model performs better” can read as a general/inferential claim.
- **Partial replacement:** an exact phrase can be removed while an equivalent statement survives elsewhere.
- **Generated drift:** editing an output file rather than its source can be reversed by the next regeneration.
- **Context loss:** inserting the full caveat repeatedly can make the paper unreadable; use the canonical meaning at each load-bearing surface, not identical prose everywhere.

## 4.5 Checks

1. Run a case-insensitive repository search across Paper 1 upload surfaces for the phrase classes above.
2. Confirm the 40 g values remain 8.44%, 8.83%, and −0.394 pp everywhere.
3. Confirm every affected paragraph says both:
   - what was observed; and
   - what the analysis does **not establish**, in both directions.
4. Run claim coverage on both manuscripts.
5. Run the exact and paraphrase mutation tests in §5.5.
6. Read title → abstract → significance → Methods range description → Results → Table 4a → endpoint synthesis → S3 → Discussion → Conclusions → cover letter as one continuous argument.
7. Record a reviewer sign-off that no surface says or implies “the advantage is absent/equivalent/negligible.”

## 4.6 Completion evidence

- diff showing removal/replacement of every identified occurrence;
- clean prohibited-language search result;
- passing claim-policy mutation suite;
- passing both-manuscript claim coverage;
- unchanged numerical-invariant output; and
- a short paragraph in the acceptance report explaining why the new wording is descriptive rather than a practical or equivalence decision.

---

# 5. P1-1 — Replace the disclaimer-window heuristic and expand the decision taxonomy

## 5.1 Objective

Ensure a limitations phrase cannot suppress a contradictory verdict merely because it appears within the preceding 140 characters, and ensure the scanner covers practical-negligibility and equivalence-adjacent formulations that caused the P0 recurrence.

The scanner should permit genuine non-establishment statements while failing statements that make a verdict after, before, or beside a disclaimer.

## 5.2 Affected code and tests

Primary code:

- `puckworks/paper_a/claim_policy.py`

Primary tests:

- `tests/test_paper_a_claim_policy.py`

Also update any consistency or text-generation tests that call `claim_policy.scan()` or depend on `SURFACE_ASSERTIONS`.

## 5.3 Method

### Step 1 — Remove broad “preceding window” suppression

Delete the logic that treats generic fragments such as `without`, `neither`, `is not`, `are not`, `not a`, or `rather than` anywhere in a preceding character window as sufficient to suppress a prohibited match.

A disclaimer is valid only when the non-establishment grammar governs the **same decision proposition in the same clause**.

### Step 2 — Split rendered text into decision clauses

Normalize case, Unicode punctuation, and whitespace while preserving sentence and clause boundaries. Treat the following as hard boundaries for claim adjudication:

- `.`, `?`, `!`;
- semicolons;
- em-dash or colon where it begins an independent verdict; and
- contrastive conjunctions such as `but`, `however`, `yet`, and `nevertheless`.

The implementation does not require a general-purpose natural-language parser. A deterministic clause iterator is sufficient if its behavior is explicit and heavily tested.

### Step 3 — Recognize only proposition-scoped safe constructions

Create narrow, explicit patterns for acceptable non-establishment constructions, for example:

```text
this analysis does not establish superiority
we make no claim of equivalence
the ranges cannot determine whether the difference is absent
neither superiority nor equivalence is established
practical usefulness was not established by this analysis
```

The safe span must include the decision term itself. A disclaimer in a prior sentence or prior clause must not suppress a later assertion.

### Step 4 — Evaluate prohibited matches against safe spans

A suitable implementation shape is:

```python
for clause in iter_decision_clauses(normalize_for_claim_scan(text)):
    safe_spans = find_non_establishment_spans(clause)
    for rule in RULES:
        for match in rule.pattern.finditer(clause):
            if status_authorizes(rule.presupposes, verified_status):
                continue
            if match_is_governed_by_safe_span(match, rule, safe_spans):
                continue
            problems.append(...)
```

Do not suppress a match merely because the clause contains the word `not`. The safe construction must identify who/what does not establish which decision.

### Step 5 — Add missing decision-language classes

Add rule IDs and context-specific patterns for at least:

| Rule class | Examples that should fail in the current status | Notes to avoid false positives |
|---|---|---|
| `adds_little` | “the model adds little”; “offers little benefit” | Require model/process/comparator value context; do not match “adds little numerical cost” |
| `small_incremental_value` | “incremental skill is small”; “minimal incremental gain” | Match `small/minimal/marginal/negligible` only when attached to skill/gain/value/benefit/advantage |
| `nearly_matched` | “performance was nearly matched”; “the comparator effectively matched the model” | Do not match data-record matching or matched study design |
| `essentially_same` | “performances were essentially the same” | Require performance/result/model comparison context |
| `comparable_performance` | “the models perform comparably” | Do not match “comparable units” or “comparable datasets” |
| `within_noise` | “the difference is within noise” | Treat as an inferential/practical verdict unless supported by a declared noise model and rule |
| `no_practical_advantage` | “no material/practical advantage”; “only marginal benefit” | Do not match “no practical margin was declared” |
| `no_worse_than` | “no worse than”; “at least as good as” | Non-inferiority decision class |

Retain the existing superiority, non-inferiority, equivalence, absence-of-skill, calibrated-coverage, and practical-margin classes.

### Step 6 — Prefer generated claim components at critical surfaces

Use the central claim renderer for the most important surfaces instead of relying exclusively on open-ended phrase detection. The scanner remains necessary for ungenerated prose and paraphrases, but the abstract, significance paragraph, headline, endpoint synthesis, conclusion, cover letter, highlights, and Figure 3 caption should draw from controlled proposition renderers where practical.

## 5.4 Potential pitfalls, errors, and oversights

- **False positives from generic adjectives:** a rule matching every occurrence of “small” will incorrectly flag “small positive upper bound” or “small sample.”
- **False positives from “matched”:** “matched-grid estimand,” “matched records,” and “matched condition” are design descriptions, not equivalence claims.
- **False negatives through punctuation:** “We make no equivalence claim; the models are equivalent” must fail.
- **False negatives through contrast:** “The range is not calibrated, but the model outperforms the comparator” must fail.
- **Double negation:** “not unable to establish” should not be accepted accidentally.
- **Quoted text:** genuine quotations in reader-facing prose can still convey an unsupported claim; do not automatically exempt quotation marks.
- **Status misuse:** the scanner must consume only the verified status described in §6, not an editable declaration.
- **Rule drift:** a long regex list is not a substitute for positive surface generation and mutation testing.

## 5.5 Required mutation matrix

The current uncalibrated status must produce the following outcomes.

### Must fail

```text
The model outperforms the comparator.
The ranges are not confidence intervals. The model outperforms the comparator.
This is not an inferential result, but the model outperforms the comparator.
Without calibrated coverage, the model outperforms the comparator.
The result is not precise. The model has no incremental skill.
We do not claim equivalence; the model is equivalent to the comparator.
The uncertainty is not small. The model performs comparably.
The model adds little to a baseline that carries no mechanism at all.
Its incremental skill over a level-only comparator is small.
Performance was nearly matched by a level-only constant.
The models are essentially the same.
The mechanistic model offers only marginal benefit.
The comparator is no worse than the mechanistic model.
The difference is within noise.
```

### Must pass

```text
This analysis does not establish superiority.
We make no claim of equivalence.
The ranges cannot determine whether the observed difference is absent.
Neither superiority nor equivalence is established by this analysis.
The observed pooled-MAPE difference was −0.394 percentage points.
The 40 g upper sensitivity bound was a small positive value.
Records were matched by variety, temperature, and pressure.
No practical margin was predeclared.
```

Also test case variation, line wrapping, tabs, emphasis, inline HTML, list items, table cells, and footnotes after the P1-6 structural scanner is implemented.

## 5.6 Checks

1. Every “must fail” mutation returns a named rule ID.
2. Every “must pass” example remains clean.
3. The current manuscript’s retired P0 sentences fail when inserted into every scanned upload surface.
4. The actual corrected upload files return zero claim-policy problems.
5. A test proves a disclaimer in a previous sentence or previous clause cannot suppress a later verdict.
6. A test proves a recognized non-establishment construction is still permitted.
7. The minimum-dependency test lane must execute the scanner; it must not silently return early on import failure.

## 5.7 Completion evidence

- deleted broad-window suppression code;
- new clause-scoped safe-pattern implementation;
- expanded rule table with documented presupposed decision class;
- passing mutation matrix;
- actual-manuscript scan result; and
- coverage output showing the scan executed in every relevant test environment.

---

# 6. P1-2 — Bind `InferentialStatus` to verified procedure/result evidence

## 6.1 Objective

Prevent a fabricated but internally coherent serialized status from licensing superiority, non-inferiority, equivalence, or absence language. Decision permissions must be **derived from verified evidence**, not accepted as editable booleans.

The current all-false status is conservative and should remain effective. The defect is the future unlock path.

## 6.2 Affected code and tests

Primary code:

- `puckworks/paper_a/transfer_semantics.py`
- `puckworks/paper_a/claim_policy.py`
- the transfer-artefact serializer/loader in `tools/paper_a_transfer_artifacts.py` and/or the relevant contract module

Primary tests:

- `tests/test_paper_a_transfer_semantics.py`
- `tests/test_paper_a_claim_policy.py`
- `tests/test_paper_a_transfer_contract.py`

## 6.3 Method

Implement this in two layers: immediate fail-closed hardening and a complete evidence-bound model.

### Layer A — Immediate fail-closed hardening

1. In `status_from_dict`, require `confidence_procedure` to be either `None` or a non-empty string. Reject lists, mappings, numbers, booleans, and other objects. Remove `str(...)` coercion.
2. Apply strict types to all fields. In particular, reject `bool` where a numeric confidence level or margin is expected.
3. Treat `permitted_claim_class` as derived. Do not trust a serialized value that can contradict the analysis kind and verified decision.
4. Until evidence verification is present, reject any serialized status with a true decision flag. The current uncalibrated all-false status remains valid.
5. Do not describe this temporary restriction as automatic future unlocking. It is a deliberate fail-closed state.

### Layer B — Add a registered procedure specification

Introduce an immutable procedure registry or equivalent typed specification. A procedure specification should include at least:

```text
procedure_id
procedure_version
analysis_kind
supported decision types
confidence target semantics
predictor-refit policy
cluster/resampling unit
required estimand form
required practical-margin semantics
implementation identifier/version
```

Use a stable identifier such as `clustered_bootstrap_refit_v1`, not free prose such as “invented future procedure.”

### Layer C — Add a result-evidence record

A verified inferential result record should bind at least:

```text
schema_version
procedure_id
procedure_version
procedure_spec_sha256
analysis_result_sha256
source_manifest_sha256
source_data_sha256 or source provenance digest
estimand_contract_sha256
confidence_level
predictor_refit_policy
practical_margin_pp
practical_margin_protocol_reference
practical_margin_protocol_sha256
observed statistic
interval/test result used by the decision rule
decision rule identifier
derived decision
created_by_tool/version
```

The practical margin must be bound to a protocol or declaration that predates the result. Merely placing a margin in the result record after seeing the result does not make it predeclared.

### Layer D — Canonicalize and verify evidence

1. Serialize evidence deterministically: UTF-8, sorted keys, stable separators, no NaN/Infinity, and explicit schema version.
2. Avoid self-referential hashes. Either hash the canonical payload excluding its own digest field or store the digest in a separate manifest.
3. Verify every referenced artefact exists and matches its digest.
4. Look up the registered procedure and ensure all declared semantics match it.
5. Independently derive the decision from the verified result, estimand direction, confidence target, and practical margin.
6. Reject any stored decision flag that differs from the independently derived result.

For example, an equivalence decision should not be unlocked merely because `supports_equivalence_decision=True`. It should be derived only when the registered equivalence rule is met, such as a verified calibrated interval lying entirely inside a prospectively declared equivalence margin.

### Layer E — Produce a verified status object

Separate types conceptually and, preferably, in code:

```text
DeclaredInferentialMetadata
VerifiedInferentialEvidence
VerifiedInferentialStatus
```

`claim_policy.scan()` should accept only `VerifiedInferentialStatus`. The decision flags and permitted claim class should be read-only derived properties.

A suitable shape is:

```python
verified = verify_inferential_evidence(
    declared_metadata,
    evidence_record,
    procedure_registry,
    artefact_loader,
)
status = derive_verified_status(verified)
problems = claim_policy.scan(text, status)
```

### Layer F — Handle predictor-refit semantics correctly

Do not unconditionally require `predictors_refitted_within_draw=False`. The value must be validated against the registered procedure:

- the present fixed-predictor sensitivity analysis should require `False`;
- a future calibrated clustered bootstrap may require `True`;
- a procedure that does not specify the refit policy must fail registration/verification.

## 6.4 Potential pitfalls, errors, and oversights

- **Moving rather than removing trust:** hashing an artefact does not help if decision flags are still trusted instead of derived.
- **Circular hashes:** an artefact cannot straightforwardly include a digest of itself.
- **Unstable serialization:** timestamps, absolute paths, key ordering, float formatting, or platform-specific line endings can make hashes non-reproducible.
- **Post-hoc margin:** a margin stored with the result is not automatically predeclared.
- **Sign-direction error:** superiority/non-inferiority decisions must use the typed estimand’s metric preference and operand order.
- **Procedure-name spoofing:** free text must not select a procedure.
- **Version drift:** a procedure ID without a version can silently change meaning.
- **Partial evidence:** a missing source/design/result digest must fail closed.
- **Multiple decisions:** a procedure may support one decision class but not another; do not unlock all decision language from a generic “calibrated” flag.
- **Synthetic positive-path test leakage:** the test fixture must not alter the current paper’s status or prose.
- **Security overclaim:** repository hashes provide integrity binding within the workflow, not protection against a malicious actor who can rewrite code and evidence together.

## 6.5 Checks

### Negative tests

1. The reproduced fabricated status with an invented procedure fails.
2. `confidence_procedure: ["fake", "procedure"]` fails type validation.
3. Changing any of the following without corresponding evidence fails:
   - procedure ID/version;
   - confidence level;
   - predictor-refit policy;
   - practical margin;
   - margin protocol hash;
   - source, design, or result hash;
   - observed interval/test result;
   - derived decision; or
   - permitted claim class.
4. A true decision flag without evidence fails.
5. Evidence for equivalence cannot unlock superiority language, and vice versa.

### Positive synthetic test

Create a small, deterministic test-only registered procedure and result fixture with a known decision. Verify that:

- the evidence validates;
- the decision is derived rather than copied;
- only the corresponding claim class unlocks; and
- one-field mutations make verification fail.

### Current-paper test

Verify the present analysis still derives an all-false, descriptive/evidence-limited status and that the corrected paper contains no unlocked decision language.

## 6.6 Completion evidence

- strict `status_from_dict` type behavior;
- registered procedure specification;
- deterministic evidence schema and hash verification;
- independently derived decision permissions;
- negative and positive-path tests; and
- acceptance-report output showing the exact evidence record and procedure ID used for the current all-false status.

---

# 7. P1-3 — Add highlights and Figure 3 to positive claim coverage

## 7.1 Objective

Ensure the two standalone upload-facing surfaces cannot omit the evidence limits while retaining the observed comparison:

- `docs/submission/PAPER_A_JFE_HIGHLIGHTS.txt`; and
- Figure 3 in `docs/submission/PAPER_A_JFE_FIGURE_CAPTIONS.md`.

## 7.2 Method

### Step 1 — Add explicit surface specifications

Extend `SURFACE_ASSERTIONS` or replace it with a structured `SurfaceSpec` registry containing:

```text
surface_id
source/output file
extractor
required proposition IDs
whether text is generated
submission role
```

Add:

- `highlights`; and
- `figure3_caption`.

Do not allow `missing_assertions()` to skip an unknown surface silently. The existing fail-on-unknown behavior should be retained.

### Step 2 — Assign required propositions

Recommended requirements:

| Surface | Required propositions |
|---|---|
| Highlights | observed advantage; ranges uncalibrated; no decision claimed |
| Figure 3 caption | observed advantage; ranges uncalibrated; no decision claimed; endpoint accuracy is insufficient to establish transfer |

Because Figure 3 is meant to stand alone, it should carry all four central propositions.

### Step 3 — Replace the current highlight wording

Replace the current “gain ... was under 0.4 points” wording with wording that identifies the result as observed and states the limit.

Recommended bullets:

```text
Observed pooled MAPE was 0.394 points lower than a level-only comparator.
Uncalibrated ranges support no superiority, equivalence, usefulness, or absence decision.
```

If venue character limits require a different rendering, preserve all four ideas: observed, signed/magnitude, uncalibrated, and no decision in either direction. Validate the final bullets against the venue limit rather than silently dropping the evidence boundary.

### Step 4 — Add the standalone Figure 3 limitation

Append or integrate:

> These fixed-predictor sensitivity ranges are uncalibrated; they support no superiority, non-inferiority, equivalence, practical-usefulness, or absence-of-incremental-value decision. Acceptable endpoint accuracy alone does not establish transfer of the kinetic mechanism.

Retain the existing 44-record/132-observation, 8.44% versus 8.83%, and 62/132 content.

### Step 5 — Generate rather than hand-maintain where possible

Use the same canonical claim renderers as the manuscript for the no-decision and transfer-limit components. The highlight may use a short renderer; the Figure 3 caption may use the full renderer.

The Figure 3 extractor must structurally identify Figure 3 and not accidentally inspect Figure S3 or another paragraph.

## 7.3 Potential pitfalls, errors, and oversights

- **Standalone ambiguity:** “gain” without “observed” reads as an established property.
- **One-sided limit:** saying only “not a confidence interval” does not state that no superiority/equivalence/absence decision is made.
- **Character-limit pressure:** deleting the caveat to fit a venue limit is not acceptable; rewrite compactly instead.
- **Caption duplication:** appending a generated sentence twice can pass simple phrase coverage while creating poor output.
- **Wrong caption extraction:** a regex can match Figure S3 or text elsewhere.
- **Numerical drift:** the short highlight must use 0.394, not a new rounded or relative quantity unless explicitly defined.
- **Missing transfer boundary:** the caption should state that endpoint accuracy alone is insufficient, because it is independently read.

## 7.4 Checks

1. Removing any required proposition from either surface makes claim coverage fail.
2. Changing “observed” to an unqualified “gain” fails the highlight assertion.
3. Deleting the explicit no-decision sentence from Figure 3 fails.
4. Figure 3 retains 44 records, 132 observations, 8.44%, 8.83%, and 62/132.
5. The caption generator and upload file are fresh.
6. A direct visual read confirms both surfaces are intelligible without the manuscript.
7. Venue length/format checks are explicitly recorded rather than assumed.

## 7.5 Completion evidence

- new surface-registry entries;
- generated or synchronized highlight and Figure 3 text;
- deletion mutations for each proposition;
- caption freshness output; and
- standalone editorial sign-off.

---

# 8. P1-4 — Harden the source-to-observation contract

## 8.1 Objective

Close shared, unverified assumptions above the production/oracle split so malformed source metadata, lossy coordinate identity, or false lookup-support declarations cannot pass both implementations.

Retain the independent production and oracle analyte mappings and membership logic. Do not “fix” the issue by making the oracle import the production implementation.

## 8.2 Affected code and documentation

Primary code:

- `puckworks/paper_a/transfer_contract.py`
- `puckworks/paper_a/source_resampling_oracle.py`
- a new or existing declarative source-schema/provenance module/record

Tests:

- `tests/test_paper_a_transfer_contract.py`
- oracle/design mutation tests
- transfer-artifact checker tests

Documentation:

- Paper 1 Methods/data-provenance text describing what the contract verifies and what it does not.

## 8.3 Method

### Step 1 — Define a strict source-row schema

Define required columns, types, controlled vocabularies, units, and null policy for at least:

```text
sample
variety
granulometry
on_grid
T_degC
p_bar
CF/TR/5CQA source analyte columns
```

The schema should be declarative and versioned. It may be stored as typed Python data or a canonical JSON/YAML record, but validation must not depend on informal comments.

### Step 2 — Validate controlled strings before filtering

For `variety` and `granulometry`:

1. require strings;
2. reject leading/trailing whitespace instead of silently stripping it;
3. reject unknown values with a row/sample-specific diagnostic; and
4. filter only after validation.

This ensures `" Arabica "` fails visibly rather than disappearing from the corpus.

### Step 3 — Parse booleans with an explicit token set

Declare the accepted source tokens. If the controlled CSV uses exactly `True` and `False`, accept only those exact tokens. Otherwise declare a narrowly justified set and map each token explicitly.

Unknown tokens such as `true`, `TRUE`, `1`, empty string, or misspellings must fail. Do not convert them to `False` by equality comparison.

### Step 4 — Parse coordinates as finite decimal values

Use a lossless decimal representation for source-condition identity. One suitable approach is:

```python
from decimal import Decimal, InvalidOperation


def parse_coordinate_token(raw: object, field: str, sample_id: str) -> Decimal:
    if not isinstance(raw, str):
        raise SourceSchemaError(...)
    if raw != raw.strip():
        raise SourceSchemaError(...)
    try:
        value = Decimal(raw)
    except InvalidOperation:
        raise SourceSchemaError(...)
    if not value.is_finite():
        raise SourceSchemaError(...)
    return value
```

Define a canonical, non-lossy string form for hashing and IDs. For example, normalize numerically equivalent decimal tokens without rounding, convert `-0` to `0`, and emit a fixed/plain representation. Do **not** use default `%g` or `:g` formatting.

The following must remain distinct:

```text
93.40004
93.40005
```

Numerically equal representations such as `93.4000` and `93.4` may share a condition key only if the schema explicitly treats them as the same measured condition. If textual precision itself is scientifically meaningful, record that precision separately rather than relying on the raw token accidentally.

### Step 5 — Introduce a typed condition key

Use a type such as:

```python
@dataclass(frozen=True, order=True)
class ConditionKey:
    variety: str
    temperature_degC: Decimal
    pressure_bar: Decimal
```

Use this key for support, partition membership, duplicate detection, and deterministic serialization. Convert to float only at a downstream calculation boundary that truly requires float arithmetic, never for identity.

### Step 6 — Derive optimal-grind lookup support from actual source rows

Build a support set from valid, usable optimal-grind rows:

```python
optimal_support = {
    ConditionKey(row.variety, row.temperature_degC, row.pressure_bar)
    for row in parsed_rows
    if row.granulometry == "O" and row.has_required_scored_values
}
```

For every held-out row, derive:

```python
derived_lookup_defined = row.condition_key in optimal_support
```

Then reconcile the source declaration:

```python
if row.on_grid != derived_lookup_defined:
    raise SourceContractError(...)
```

Do not silently overwrite the declaration. A mismatch is evidence requiring investigation.

Derive `train_sample_ids` from the validated usable O rows, not from `on_grid == "True"` alone.

### Step 7 — Check duplicates and ambiguous support

For each optimal-grind condition key:

- if exactly one row is expected, duplicates must fail;
- if replicates are scientifically allowed, the aggregation/selection rule must be explicit and independently tested;
- a row with missing/unusable required analytes must not count as valid lookup support; and
- every `lookup_defined=True` held-out record must resolve to the declared support record(s).

### Step 8 — Add a separate schema/provenance preflight

Before either production construction or oracle comparison:

1. validate the complete source file against the strict schema;
2. emit a deterministic source-schema report with counts and row-specific diagnostics;
3. record declared units and source provenance; and
4. fail the chain if preflight is not clean.

Production and oracle should remain independently implemented for analyte maps, inclusion, membership, and partition derivation. A shared declarative schema is acceptable; a shared production parser that makes the oracle repeat every production mistake is not.

### Step 9 — State the verification boundary in the paper

Add a Methods/data-provenance sentence such as:

> The source contract validates the declared CSV schema, controlled tokens, finite condition coordinates, analyte parseability, corpus membership, and optimal-grind lookup support. It does not independently verify transcription, unit correctness, or measurement accuracy against the source publication.

This prevents structural validation from being described as source-truth validation.

### Step 10 — Rebuild and compare without numerical drift

Run the corrected source preflight, production manifest, and independent oracle on the unchanged source. Require:

- exactly 44 held-out records;
- exactly 132 scored observations;
- identical sample membership;
- identical train/held-out/excluded partitions;
- identical support membership;
- identical normalized partition hash, unless the former hash encoded lossy coordinate strings and a versioned migration is required; and
- unchanged protected numerical results.

If a key/hash representation must change solely to remove `%g` loss, version the schema and prove exact semantic membership equivalence before accepting the migration.

## 8.4 Potential pitfalls, errors, and oversights

- **Common-mode reintroduction:** importing production membership logic into the oracle defeats the independent check.
- **Over-permissive boolean parsing:** accepting every familiar truthy token can hide source corruption.
- **Silent normalization:** stripping whitespace makes a damaged controlled source look valid.
- **Decimal-to-float fallback:** using floats in keys after parsing with `Decimal` reintroduces collisions.
- **Support flag semantics:** if `on_grid` means something other than “an O-grind comparator exists,” rename or separate the fields rather than forcing equivalence.
- **Duplicate support:** multiple O rows at one condition need an explicit rule; arbitrary first-row selection is not acceptable.
- **Unit inference:** field names such as `T_degC` and `p_bar` declare units syntactically but do not independently prove source transcription.
- **Plausibility overreach:** do not reject scientifically unusual but source-valid values using undocumented “reasonable ranges.” Use allowed sets/ranges only when anchored to the source design.
- **Hash migration:** a new canonical key format can change hashes without changing science; document and independently prove equivalence.
- **Unnecessary producer rerun:** do not move Monte Carlo results if the corrected source contract reproduces the same semantic corpus/design.

## 8.5 Required mutation tests

Each mutation must fail with a named diagnostic:

```text
variety=" Arabica "
granulometry="C "
on_grid="true"
on_grid="TRUE"
on_grid="1"
on_grid="Tru"
T_degC="NaN"
T_degC="Infinity"
p_bar="-Infinity"
93.40004 and 93.40005 collapsed to one condition
9.000004 and 9.000005 collapsed to one condition
held-out row on_grid=True with no valid O counterpart
held-out row on_grid=False with a valid O counterpart
duplicate O support with no declared replicate rule
O counterpart present but required analyte unusable
unknown controlled variety/granulometry token
```

Also mutate the production and oracle analyte maps separately to confirm independent disagreement is detected.

## 8.6 Checks

1. Strict source preflight passes the unchanged source.
2. Every mutation above fails.
3. Production and oracle independently reproduce exact membership.
4. The 44-record/132-observation corpus remains exact.
5. `lookup_defined` equals actual support membership for every record.
6. No condition key contains `nan`, `inf`, or rounded `%g` identity.
7. Methods wording accurately states the verification boundary.
8. Numerical invariants remain exact.
9. The acceptance report states whether any schema/hash migration occurred and why.

## 8.7 Completion evidence

- versioned source schema;
- strict row diagnostics;
- typed lossless condition keys;
- independently derived support reconciliation;
- mutation-test output;
- exact corpus/partition comparison; and
- source-boundary Methods text.

---

# 9. P1-5 — Make interval and status numeric validation total

## 9.1 Objective

Honor the validator contract that malformed input returns named problems and never raises due to expected data-conversion errors. Valid JSON integers too large for IEEE float conversion must be rejected deterministically rather than raising `OverflowError`.

## 9.2 Affected code and tests

Primary code:

- numeric helpers in `puckworks/paper_a/transfer_semantics.py`;
- `validate_interval_record` and related reconstruction/comparison paths in `puckworks/paper_a/transfer_contract.py`; and
- confidence-level/practical-margin parsing used by inferential-status validation.

Primary tests:

- `tests/test_paper_a_transfer_semantics.py`
- `tests/test_paper_a_transfer_contract.py`

## 9.3 Method

### Step 1 — Centralize strict finite-number parsing

Use one helper for JSON-number validation. It should:

1. reject `bool` explicitly, because `bool` is a subclass of `int` in Python;
2. require the schema’s accepted numeric types;
3. catch `TypeError`, `ValueError`, and `OverflowError`;
4. reject NaN and ±Infinity; and
5. return a path-specific problem rather than raising.

Illustrative shape:

```python
def require_finite_number(value, path: str, problems: list[str]):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        problems.append(f"{path} must be a finite JSON number")
        return None
    try:
        number = float(value)
    except (TypeError, ValueError, OverflowError):
        problems.append(f"{path} must be a finite JSON number; conversion overflowed or failed")
        return None
    if not math.isfinite(number):
        problems.append(f"{path} must be finite")
        return None
    return number
```

If full-precision bounds are intentionally strings, use a parallel strict decimal-string parser and preserve that schema. Do not make fields accept both numbers and strings merely to simplify the helper.

### Step 2 — Audit every conversion path

Apply the helper or equivalent targeted catches to:

- `full_precision_pp.lower`;
- `full_precision_pp.upper`;
- `signed_nearest_bound_to_zero_pp`;
- `width_pp`;
- `display.lower`;
- `display.upper`;
- display digits if numeric conversion occurs;
- `_same_value` or equivalent comparison helpers;
- canonical interval reconstruction;
- confidence level;
- practical margin; and
- any other serialized numeric field in the inferential status/evidence record.

### Step 3 — Preserve path-specific diagnostics

Do not return a generic “invalid interval.” A multi-field malformed record should report every safely discoverable problem so the user can fix it in one pass.

### Step 4 — Avoid a blanket exception mask

Do not satisfy “never raises” by wrapping the entire validator in `except Exception`. That would hide programming errors. Catch the expected data-domain exceptions at the conversion boundaries and retain ordinary failures for genuine code defects.

### Step 5 — Add totality/property-style tests

Parameterize each numeric field with:

```text
10**400
-(10**400)
True
False
None
"1.0"
NaN
+Infinity
-Infinity
```

Where Python’s JSON decoder can admit non-standard NaN/Infinity, explicitly reject them. Add a test that iterates the entire malformed-input matrix and asserts the validator returns a list without raising.

## 9.4 Potential pitfalls, errors, and oversights

- **Boolean acceptance:** `isinstance(True, int)` is true.
- **Partial audit:** fixing full-precision bounds while display or status fields still overflow leaves the contract false.
- **String coercion:** accepting numeric strings can conceal schema damage.
- **Blanket exception handling:** suppresses real coding defects and can produce false greens.
- **First-error exit:** returning after one failure can hide additional malformed fields; collect problems where safe.
- **Huge finite decimal:** `Decimal` may regard an enormous exponent as finite while later float conversion still fails; reject at the actual representation boundary.
- **Diagnostic instability:** tests should assert stable field paths/rule IDs, not fragile full sentences where wording may legitimately improve.

## 9.5 Checks

1. Large positive and negative integers in every numeric interval field return named problems and never raise.
2. The same totality behavior applies to confidence level and practical margin.
3. `bool`, string, `None`, NaN, and infinities remain rejected.
4. Valid current interval records still reconstruct and exact-compare cleanly.
5. A malformed record reports the correct field path.
6. The top-level checker continues after one malformed artefact sufficiently to report other independent problems where safe.

## 9.6 Completion evidence

- centralized numeric helper or equivalent audited implementation;
- full malformed-input matrix;
- no uncaught expected conversion exceptions;
- unchanged validation of current artefacts; and
- explicit test output demonstrating totality.

---

# 10. P1-6 — Structurally parse Markdown and scan all upload deliverables

## 10.1 Objective

Detect prohibited narration and internal paths despite emphasis, inline HTML, entities, tables, lists, footnotes, inline/reference links, and hidden destinations. Apply the rules to every actual upload deliverable, not only the manuscript and supplement.

## 10.2 Affected code and tests

Primary code:

- `tools/paper_a_consistency.py`
- submission-file/package-manifest definitions used by that checker

Tests should cover the scanner’s block extraction, visible-text normalization, target scanning, file scoping, and allowlists.

## 10.3 Method

### Step 1 — Derive the upload-file set from one authority

Define actual upload deliverables once, preferably from the submission package manifest or a typed `SubmissionFileSpec` registry. The scanner should consume that same registry.

At minimum, scan:

- manuscript;
- supplement;
- cover letter;
- highlights; and
- upload-ready figure captions.

The package/assembly manifest may be exempt from path checks if its purpose requires filenames. The canonical working draft and internal figure map may be exempt from selected upload-leakage rules because they are not uploaded, but their active scientific claim surfaces should remain subject to claim-policy checks where applicable. Every exemption must be explicit, narrow, and tested.

### Step 2 — Parse Markdown into a structural representation

Use an existing pinned CommonMark-compatible parser if the repository already has one; otherwise add a small, pinned dependency such as `markdown-it-py`. Do not extend the current regular-expression pseudo-renderer into a second incomplete Markdown parser.

Extract visible content from:

- headings;
- paragraphs;
- block quotes;
- list items;
- table cells;
- footnotes;
- emphasis/strong text;
- inline code and code blocks where visible in the submission;
- link text and image alt text; and
- raw inline/block HTML after removing tags and decoding entities.

Retain source-line ranges from parser token maps for diagnostics.

### Step 3 — Maintain two scanning channels

**A. Rendered-text/semantic channel**

Scan reader-visible text for:

- claim-policy violations;
- review-history narration;
- process vocabulary; and
- producer/internal narration.

Join adjacent inline text nodes so `ver**sion**` is read as `version`.

**B. Raw-source/metadata leakage channel**

Separately scan:

- inline link destinations;
- reference-style link definitions;
- image destinations;
- HTML `href`/`src` attributes;
- autolinks;
- visible code literals;
- HTML comments if the source file itself is an upload deliverable; and
- raw source for repository path patterns that can survive conversion or metadata inspection.

A link target is not visible prose, but it remains part of the submitted source and must not be discarded for internal-path leakage checks.

### Step 4 — Normalize safely

For scanner comparison only:

- apply Unicode normalization;
- case-fold where the rule is case-insensitive;
- decode HTML entities;
- normalize curly punctuation/dashes where needed;
- collapse internal whitespace; and
- preserve block/clause boundaries used by the claim policy.

Do not alter the submitted file as part of scanning.

### Step 5 — Normalize destinations before path checks

For link/image targets:

- percent-decode;
- normalize backslashes to slashes;
- remove harmless `./` segments;
- identify relative/internal repository paths;
- distinguish public absolute URLs from repository-relative targets; and
- reject traversal forms such as `../docs/...`.

### Step 6 — Replace broad section exemptions with narrow allowlists

Permit only the specific path-bearing content genuinely needed by a submitted file, for example:

- expected submitted figure filenames in caption/source links; and
- approved public DOI/release/deposit URLs in availability statements.

Do not permit every `docs/`, `tools/`, `tests/`, or `puckworks/` path merely because it appears under “reproducibility” or “figure captions.”

### Step 7 — Add rule-specific scope assertions

Tests should assert that each rule class applies to the intended file set. Adding a new upload deliverable must fail until its rule scope is declared, rather than silently leaving it unscanned.

## 10.4 Potential pitfalls, errors, and oversights

- **Parser dependency unavailable:** a missing dependency must yield NOT RUN/FAIL, not a clean result.
- **Visible-text only:** link targets and HTML attributes can still leak internal paths.
- **Raw-source only:** markup can split prohibited prose and cause false negatives unless visible text is reconstructed.
- **Overbroad allowlist:** allowing all paths in availability or caption sections recreates the leak.
- **External URL false positives:** an external public URL may contain `docs` or `review` in its path; distinguish scheme/host and approved public links.
- **Percent-encoding bypass:** `docs%2Finternal%2Freview.md` must not pass.
- **Reference-link bypass:** the destination can be defined far from the visible use.
- **Line mapping:** joining nodes must not destroy useful diagnostics.
- **Tables/footnotes extension support:** some Markdown parsers require plugins; configure and test the dialect actually used by the repository.
- **HTML comments:** comments are invisible, but if Markdown is itself uploaded they are still disclosed in source. Scan them for leakage even if they are excluded from prose semantics.
- **Inline-code exemption:** repository paths in inline code still leak; do not drop them from the path channel.

## 10.5 Required mutation tests

All of these must fail on upload-facing files:

```markdown
An earlier **version** was wrong.
An earlier <em>version</em> was wrong.
The second *review* asked for this.
See [the internal analysis](docs/internal/review.md) for details.
See [the internal analysis][internal].
[internal]: docs/internal/review.md
See <a href="docs/internal/review.md">analysis</a>.
See [analysis](docs%2Finternal%2Freview.md).
| Note | An earlier **version** was wrong |
- The second *review* asked for this.
[^1]: See [analysis](docs/internal/review.md).
An earlier ver**sion** was wrong.
An earlier&nbsp;version was wrong.
`docs/internal/review.md`
```

Repeat representative cases in manuscript, supplement, cover letter, highlights, and standalone captions.

Legitimate expected submitted figure filenames should pass only through an explicit narrow allowlist.

## 10.6 Checks

1. Every reproduced false negative now fails.
2. Link text and destination are scanned through separate channels.
3. Reference-style links and HTML attributes are covered.
4. Every true upload deliverable is within the intended rule scope.
5. Adding a mock upload file without a scope declaration fails a test.
6. Approved public links and expected figure filenames pass only through narrow allowlists.
7. Diagnostics identify file and source line/range.
8. The scanner reports that structural parsing actually ran in the minimum-dependency environment.
9. A final raw-source grep confirms no internal path/review vocabulary remains in upload deliverables.

## 10.7 Completion evidence

- one authoritative upload-file registry;
- structural Markdown parser and configured extensions;
- rendered-text and target/raw-source scan channels;
- narrow allowlists;
- full mutation suite; and
- actual upload-package scan report.

---

# 11. P2-1 — Fix Figure 4 caption extraction and validate generated structure

## 11.1 Objective

Ensure the Figure 4 caption ends at its authored caption text and cannot absorb a horizontal rule or the `## Supplementary figures` heading. Add structural validity checks so reproducible malformed output cannot be certified merely because it matches the generator.

## 11.2 Affected code and files

- `tools/paper_a_figure_captions.py`
- `docs/figures/PAPER_A_FIGURE_MAP_INTERNAL.md`
- generated `docs/submission/PAPER_A_JFE_FIGURE_CAPTIONS.md`
- caption-generator tests

## 11.3 Method

### Step 1 — Replace `_HEADING` regex extraction with structural section parsing

Reuse the Markdown parser introduced under P1-6 where possible. Identify caption sections by level-3 headings matching the exact internal-map form:

```text
### Figure N (`producer_stem`)
### Figure SN (`producer_stem`)
```

Collect the following blocks until the first of:

- any heading at level 1, 2, or 3;
- a horizontal rule; or
- end of document.

A `## Supplementary figures` heading must therefore terminate Figure 4 extraction.

### Step 2 — Validate the source section before rendering

For each figure:

- require exactly one matching heading;
- require non-empty caption content;
- remove approved generator/source-stamp comments only;
- reject embedded headings or horizontal rules in the caption body;
- retain authored inline formatting only if it is valid for the upload caption format; and
- ensure the body begins with the expected `**Figure N.` or `**Figure SN.` label, or add that label in one controlled renderer rather than accepting arbitrary text.

### Step 3 — Validate the complete caption set

For the current package, require:

- main captions exactly `{1, 2, 3, 4}`;
- supplementary captions exactly `{S1, S2, S3, S4}`;
- no duplicates;
- deterministic main-then-supplementary order;
- exactly one `## Main figures` heading;
- exactly one `## Supplementary figures` heading;
- no caption body containing `---` or an embedded heading marker;
- exactly one figure label per caption; and
- no internal producer identifiers, review history, or repository paths in the generated upload file.

If the expected figure set changes later, derive it from a versioned package/figure manifest rather than silently relaxing the count.

### Step 4 — Separate freshness from validity

Keep the existing byte-for-byte freshness comparison, but add a separate structural validator:

```text
source map valid
rendered caption structure valid
current upload file equals valid rendered output
```

All three must pass. Equality to invalid generated output is not acceptance.

### Step 5 — Regenerate

Run:

```bash
python tools/paper_a_figure_captions.py --write
python tools/paper_a_figure_captions.py --check
```

Confirm Figure 4 ends with “equivalent validation.” and is followed by one clean supplementary heading outside the caption.

## 11.4 Potential pitfalls, errors, and oversights

- **Regex patch only:** merely adding `(?=\n## )` can miss horizontal rules, level-1 headings, or future structural changes.
- **Heading-like caption text:** if a caption genuinely needs a heading marker, it must be escaped or represented differently; raw headings should not occur inside a caption.
- **Duplicate labels:** authored text and renderer can each add `Figure 4.`.
- **Stale expected counts:** hard-coded counts must be tied to the current package manifest or updated deliberately.
- **Comment stripping:** remove only recognized assurance comments; do not delete substantive text hidden accidentally in comments without reporting it.
- **Formatting collapse:** joining all whitespace can damage mathematical notation or intended paragraph structure; define the upload-caption format explicitly.
- **Freshness false assurance:** `current == render()` is necessary but not sufficient.

## 11.5 Checks

1. A fixture containing the current Figure 4 delimiter defect fails before the fix and passes after structural parsing.
2. Figure 4 ends at “equivalent validation.”
3. The generated file contains one supplementary heading.
4. The expected 4 main and 4 supplementary captions are present once each and in order.
5. No caption body contains `---`, `##`, or `###` markers.
6. Figure 3 positive-claim coverage from P1-3 still passes after regeneration.
7. The upload file passes the P1-6 scanner.
8. A human directly reads the standalone caption file.

## 11.6 Completion evidence

- structural caption extractor;
- caption-set invariant tests;
- regenerated upload file;
- freshness and validity output; and
- visual sign-off recorded in the acceptance report.

---

# 12. Cross-cutting verification and regression plan

## 12.1 Exact Round 11 command chain

Run every command from the controlling brief against the final candidate commit:

```bash
python tools/paper_a_numerical_invariants.py --check
python tools/paper_a_transfer_artifacts.py --check
python tools/paper_a_transfer_text.py --check
python tools/paper_a_figure_captions.py --check
python tools/paper_a_consistency.py verify
python tools/paper_a_migrate_schema4.py
python -m puckworks.paper_a.claim_coverage
python -m puckworks.paper_a.slow_lane_bindings
python tools/claim_binding_audit.py
python -m pytest tests/test_paper_a_claim_policy.py \
                 tests/test_paper_a_transfer_semantics.py \
                 tests/test_paper_a_transfer_contract.py \
                 tests/test_paper_a_numerical_invariants.py -q
python -m pytest -q
```

Add the new targeted scanner/caption/source-schema test modules to the focused run if they are separate files.

## 12.2 Execution-status requirement

For each command, record:

```text
command
start/end timestamp
exit code
commit SHA
environment/dependency set
PASS / FAIL / NOT RUN
summary count
retained log path or digest
```

A command that cannot exercise a check because a dependency is absent must return a non-passing status or an explicit partial-coverage status that blocks acceptance. It must not print a normal clean result.

## 12.3 Adversarial regression categories

The final focused suite must include:

1. **Claim recurrence:** exact and paraphrased P0 language.
2. **Disclaimer contradiction:** limitations sentence followed by unsupported verdict.
3. **Status fabrication:** internally coherent but unevidenced decision status.
4. **Positive-surface deletion:** remove each required proposition from highlights and Figure 3.
5. **Source corruption:** whitespace, booleans, non-finite coordinates, coordinate collision, support mismatch.
6. **Numeric totality:** oversized integers and non-finite/mistyped fields.
7. **Markdown bypass:** emphasis, HTML, entities, tables, lists, footnotes, reference links, encoded targets.
8. **Caption structure:** section delimiter captured into a caption, duplicates, missing labels/headings.
9. **Numerical ratchet:** one-digit changes to every protected value.
10. **Check-not-run:** simulate missing parser/optional dependency and require a blocking status.

## 12.4 Direct human inspection

Automated checks cannot establish editorial coherence. Perform and record:

- continuous-argument read of all load-bearing Paper 1 surfaces;
- standalone read of highlights;
- standalone read of all figure captions;
- direct view of the generated submission package/file list;
- visual check that Figure 4 and Figure 3 captions are clean;
- check that no review history, internal path, producer identifier, TODO, or placeholder appears; and
- journal-width check of Supplementary Table S7 if it is available in the final package. This was lower priority in the brief but remains a sensible final presentation check.

## 12.5 Numerical and artefact reconciliation

Require all of the following:

- protected numbers exact, no tolerance;
- transfer artefacts pass the corrected source/design/status contracts;
- generated blocks are fresh;
- both manuscripts pass claim coverage;
- the caption file is both structurally valid and fresh;
- source preflight and oracle agree on exact content; and
- no unplanned generated or numerical artefact changes appear in the diff.

---

# 13. Recommended commit/PR structure

Keep commits reviewable and independently green.

## Commit 1 — `paper-a: restore evidence-bounded comparison claim`

Include:

- P0 manuscript/canonical rewrites;
- new practical-negligibility/equivalence-adjacent rules;
- clause-scoped disclaimer handling;
- exact/paraphrase mutation tests; and
- any regenerated text required by those changes.

Do not merge a prose-only P0 fix without the recurrence tests.

## Commit 2 — `paper-a: govern standalone claim surfaces`

Include:

- highlights and Figure 3 surface specifications;
- revised/generated highlight text;
- Figure 3 no-decision/transfer-limit sentence; and
- positive-proposition deletion tests.

## Commit 3 — `paper-a: bind inferential claims to verified evidence`

Include:

- strict status parsing;
- procedure registry/specification;
- evidence record and deterministic verification;
- derived decision permissions;
- fabricated-status and positive-path tests.

## Commit 4 — `paper-a: harden source and numeric contracts`

Include:

- versioned source schema;
- strict controlled tokens and booleans;
- finite lossless condition keys;
- independently derived lookup support;
- source-boundary Methods text;
- overflow/totality fix; and
- source/numeric mutation tests.

If a schema/hash migration is required, keep it explicit and prove semantic membership equivalence in this commit.

## Commit 5 — `paper-a: structurally validate submission markdown and captions`

Include:

- structural Markdown parser;
- visible-text plus destination/raw-source channels;
- complete upload-file scoping;
- narrow allowlists;
- structural caption extractor and invariants;
- regenerated caption file; and
- markup/link/caption mutations.

## Commit 6 — `docs: record Paper 1 Round 11 remediation acceptance`

Include only:

- final acceptance report;
- command results/digests;
- reviewed commit/tree identifiers;
- explicit producer-rerun decision; and
- any retained review artefacts intended for the repository.

---

# 14. Final acceptance checklist

The Round 11 remediation is complete only when every item below is evidenced.

## Scientific claim

- [ ] No Paper 1 reader-facing surface says or implies “adds little,” “incremental skill is small,” “nearly matched,” or an equivalent practical-negligibility/equivalence verdict.
- [ ] The observed −0.394 pp model-favouring 40 g result remains prominent.
- [ ] Uncalibrated-range and no-margin limitations are stated wherever required.
- [ ] Non-establishment is symmetrical: neither advantage/usefulness nor equivalence/absence is established.
- [ ] Endpoint accuracy alone is not presented as establishing mechanism transfer.

## Claim assurance

- [ ] Disclaimer handling is proposition/clause scoped.
- [ ] Every reproduced contradictory disclaimer example fails.
- [ ] New practical-negligibility/equivalence paraphrases fail.
- [ ] Genuine non-establishment statements pass.
- [ ] Highlights and Figure 3 are positive-coverage surfaces.
- [ ] Removing a required proposition makes coverage fail.

## Inferential authority

- [ ] Non-string procedure identifiers fail.
- [ ] Decision permissions are derived from verified evidence.
- [ ] Fabricated coherent statuses cannot unlock prose.
- [ ] Procedure, result, source, design, margin, and decision are cryptographically bound through deterministic records.
- [ ] Predictor-refit semantics are procedure-specific.
- [ ] A synthetic positive path unlocks only the earned decision class.

## Source/design contract

- [ ] Controlled strings and booleans are strict.
- [ ] Coordinates are finite and losslessly canonicalized.
- [ ] No default `%g`/`:g` identity remains.
- [ ] Lookup support is derived from valid O-grind rows and reconciled to the declaration.
- [ ] Source corruption mutations fail with named diagnostics.
- [ ] Production and independent oracle still agree on exact 44-record/132-observation membership.
- [ ] Methods text states the verification boundary.

## Numeric validation

- [ ] Oversized positive/negative integers never raise from validators.
- [ ] Bool, string, `None`, NaN, and infinities fail.
- [ ] Every numeric field path is covered.
- [ ] Current interval/status records still validate exactly.

## Submission scanner and captions

- [ ] Structural Markdown parsing runs in every required environment.
- [ ] Emphasis, HTML, entities, tables, lists, footnotes, and reference links cannot hide prohibited content.
- [ ] Link/image/HTML destinations are scanned for internal paths.
- [ ] Every true upload deliverable is in scope.
- [ ] Allowlisted paths are narrow and explicit.
- [ ] Figure 4 no longer absorbs the supplementary delimiter.
- [ ] Caption-set structure is validated independently of freshness.
- [ ] Standalone captions pass direct human inspection.

## Final chain

- [ ] Every command in §12.1 records PASS, not merely a zero-problem message from a skipped check.
- [ ] Full test suite passes.
- [ ] Both-manuscript claim coverage passes.
- [ ] Numerical invariants remain exact.
- [ ] Generated files are fresh.
- [ ] Working tree contains only intended changes.
- [ ] Science producer rerun decision is explicitly justified.
- [ ] Acceptance report identifies the final commit and tree.

---

# 15. Acceptance-report contents

Create a Round 11 remediation acceptance document beside the review brief and prior reports. It should include:

1. final commit SHA and tree SHA;
2. finding-by-finding disposition, with links to changed files/tests;
3. exact before/after P0 wording;
4. numerical-invariant table and checker output;
5. claim-policy mutation matrix results;
6. inferential-evidence verification summary;
7. source-schema and exact membership reconciliation;
8. interval-validator totality results;
9. Markdown/link/caption adversarial results;
10. complete command table with PASS/FAIL/NOT RUN;
11. generated-file freshness and structural-validity results;
12. human-inspection checklist;
13. producer-rerun decision and rationale; and
14. residual open items, limited to items genuinely outside Round 11 remediation.

The acceptance report should not state “all checks pass” unless it names which checks ran and demonstrates that none silently skipped their intended work.

---

# 16. Final implementation judgment

The most important correction is not merely to replace five sentences. The recurrence demonstrates that the manuscript’s evidentiary boundary and the policy mechanism drifted apart. The appropriate remediation therefore has two inseparable parts:

1. state the observed comparison accurately and without a practical/equivalence verdict; and
2. make the assurance chain fail when that verdict returns by paraphrase, nearby disclaimer, fabricated inferential status, omitted standalone caveat, malformed source metadata, malformed numeric input, Markdown concealment, or malformed generated caption structure.

When the checklist above is satisfied, the Round 11 P0/P1/P2 findings will be addressed without moving the protected science or weakening the paper’s real model-favouring observed result.
