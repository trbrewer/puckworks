# Paper 1 — Round 12 Remediation Implementation Plan

**Review baseline:** `trbrewer/puckworks` commit `4adbe4af6b6a4faa6b27c38f8aaf3dde01dc8a86` (`4adbe4a`)  
**Source review:** `PAPER_1_ROUND_12_DETAILED_REVIEW.md`  
**Probe record:** `PAPER_1_ROUND_12_FOCUSED_PROBES.txt`  
**Scope:** Paper 1 / Paper A submission surfaces, generators, assurance mechanisms, and directly associated tests  
**Purpose:** implementation instructions only; this document does not assert that any correction has been made or verified

## 1. Required outcome

The remediation must close **1 P0, 8 P1, and 4 P2 findings** without changing the protected Paper A numerical result unless a deliberately rerun scientific producer demonstrates that a change is required.

The required final state is not merely that the current manuscript reads better. It is that:

1. the principal claim reports the observed signed result without assigning it to an undeclared practical-magnitude category;
2. central submission wording is generated from structured evidence and cannot become materially stronger through ordinary copy-editing without a gate failing;
3. positive claim coverage proves that required propositions are actually asserted, rather than merely finding character strings;
4. inferential permission is re-earned from canonical evidence at the point of use rather than trusted because a Python object has a particular type;
5. any future decision interval is derived from the hashed result itself and any practical margin is demonstrably predeclared;
6. source-coordinate identity is fixed before any binary-float coercion;
7. upload-source scanning covers every destination, comment, and exemption channel identified in the review;
8. caption identity, package status, and editorial surfaces are internally consistent; and
9. the exact verification chain, focused adversarial probes, full suite, regeneration, and numerical invariants all pass on the final commit.

## 2. Non-negotiable implementation principles

### 2.1 Freeze the accepted numerical baseline before editing

Before changing code or prose, capture the reviewed endpoint and corpus values in a remediation baseline record. The following values must remain exact unless a consciously rerun producer supplies a different, scientifically adjudicated result:

| Endpoint | Model pooled MAPE | Comparator pooled MAPE | Difference, model − comparator | Primary range | Model worse on |
|---:|---:|---:|---:|---|---:|
| 38 g | 8.39% | 8.83% | −0.447 pp | [−0.8843868833, −0.0424325436] | 61/132 |
| 40 g | 8.44% | 8.83% | −0.394 pp | [−0.8290522506, +0.0037905184] | 62/132 |
| 42 g | 8.41% | 8.83% | −0.425 pp | [−0.8912505494, +0.0058444686] | 60/132 |

The corpus baseline is 44 held-out records, 3 solutes, 132 observations, 8 off-grid records, and a 108-observation matched-grid/lookup-support subset.

### 2.2 Correct authoritative sources, not generated copies

Where text is generated, edit the generator or structured source and regenerate every consumer. Do not hand-edit generated manuscript blocks, the standalone Highlights file, the cover letter, or the upload-ready caption file. A manually corrected generated output that remains inconsistent with its producer is not an acceptable remediation.

### 2.3 Separate three assurance jobs

The current implementation blurs three distinct jobs. They must be separated:

- **Rendering:** produce the exact permitted claim from typed scientific values and declared evidence status.
- **Positive coverage:** prove that a required proposition is affirmatively present on each standalone surface.
- **Prohibitive scanning:** detect dangerous free-text wording as defence-in-depth.

The prohibitive scanner must not remain the load-bearing source of scientific correctness. A finite phrase list cannot prove that prose is safe.

### 2.4 Fail closed at every loss of evidence

The following conditions must block rather than warn or silently coerce:

- structural parser unavailable;
- raw identity token unavailable;
- decisive result field absent or inconsistent with its digest-bound artefact;
- predeclaration chronology unprovable;
- production evidence procedure absent from the production registry;
- required proposition not positively asserted;
- generated artefact stale;
- caption stem unknown, duplicated, or mismatched; or
- package status internally contradictory.

### 2.5 Preserve an auditable acceptance record

The final pull request should retain:

- the pre-change numerical baseline;
- red tests reproducing every focused probe;
- the final passing output of those tests;
- generated-file diffs;
- numerical-invariant output;
- science-regeneration comparison where required;
- full-suite output;
- source manifest/corpus hashes; and
- an explicit finding-by-finding closure table.

## 3. Recommended implementation order

The findings are coupled. Implementing them in the following order avoids repeatedly rewriting the same components:

1. **Freeze baseline and add failing reproductions.** Add every Round 12 probe as a named regression before changing behavior.
2. **P0 wording correction.** Correct the generator and authored bridge text, regenerate both manuscripts, and prove the protected numbers did not move.
3. **Claim-governance redesign.** Address P1-1, P1-2, P1-3, and P1-6 together; do not patch only the adjective regex.
4. **Inferential evidence redesign.** Address P1-4 and P1-5 together because point-of-use verification depends on the canonical result schema and chronology proof.
5. **Source identity correction.** Address P1-7 before rerunning the transfer producer.
6. **Submission scanner and captions.** Address P1-8, P2-1, and P2-2.
7. **Package/editorial cleanup.** Resolve P2-3 and P2-4.
8. **Regenerate and validate.** Regenerate all affected artefacts, rerun the exact chain, run the full suite, rerun the scientific producer because the production source path changed, and compare all protected outputs.
9. **Independent final read.** Read title through caption as one argument and verify that neither the favourable direction nor the evidentiary limits have been buried.

# 4. Finding-by-finding implementation instructions

## P0-1 — Remove unsupported practical-magnitude verdicts from the principal claim

### Objective

Report the observed result prominently and exactly while removing every phrase that decides, without a predeclared margin, that the difference is small, negligible, unimportant, or otherwise practically categorized.

The final argument must preserve all of the following simultaneously:

- the point estimate favours the mechanistic model;
- the difference is −0.394 percentage points at 40 g;
- the model is worse on 62 of 132 held-out observations;
- the reported ranges are fixed-predictor sensitivity ranges, not calibrated confidence intervals;
- no practical margin was predeclared;
- the analysis establishes neither a reproducible/practically useful advantage nor its absence; and
- endpoint accuracy alone does not establish mechanistic transfer.

### Primary files and components

- `tools/paper_a_transfer_text.py`
  - `block_transfer_headline()`
- `docs/submission/PAPER_A_JFE_MANUSCRIPT.md`
- `docs/PAPER_A_DRAFT.md`
- the hand-authored in-sample comparator-ladder paragraph in both manuscripts
- endpoint discussion/synthesis sentences containing `only −0.394` and `well under one percentage point`
- `tests/test_paper_a_claim_policy.py`
- `tests/test_paper_a_transfer_semantics.py`
- `tests/test_paper_a_transfer_contract.py`
- any generated-text snapshot or parity tests that govern the two manuscripts

### Method

1. **Add failing tests first.** Pin the four live constructions exactly:
   - `The observed advantage is therefore small.`
   - `consistent with the small held-out skill above`
   - `only −0.394 percentage points`
   - `well under one percentage point`

   The first two must be prohibited practical-magnitude verdicts. The latter two should be prohibited on central transfer-result surfaces unless a predeclared margin or an explicitly non-evaluative mathematical context is present.

2. **Change the authoritative generator.** In `block_transfer_headline()`, replace the final sentence beginning `The observed advantage is therefore small` at the source. Do not patch the generated manuscript directly.

   A suitable replacement, taking account of the numerical sentence immediately before it, is:

   > The observed difference favours the mechanistic model. Because the reported ranges are uncalibrated and no practical margin was predeclared, this analysis does not establish that the observed advantage is reproducible or practically useful, and it does not establish that the advantage is absent. Acceptable endpoint accuracy does not by itself establish transfer of the kinetic mechanism beyond a transferred concentration level.

   This wording preserves direction, states the basis of the limit, and keeps the decision boundary symmetric.

3. **Correct the hand-authored bridge paragraph.** Replace `consistent with the small held-out skill above` with:

   > This descriptive in-sample comparison is not a held-out test and does not adjudicate the magnitude, reproducibility, or practical usefulness of the held-out difference.

   Confirm whether this paragraph is genuinely required to remain hand-authored. If it carries values or conclusions already available to a generator, move it into a generated block or an approved full-sentence template so the same drift cannot recur there.

4. **Remove evaluative adverbs around exact values.** Rewrite the sentence containing `only −0.394 percentage points` so that it reports the signed number directly. For example:

   > At 40 g, the model-minus-comparator difference is −0.394 percentage points, favouring the mechanistic model.

   Rewrite `well under one percentage point` as exact endpoint-specific bounds rather than a comparison to an undeclared relevance threshold. For example:

   > The model-favouring bounds of the primary ranges are −0.884 pp at 38 g, −0.829 pp at 40 g, and −0.891 pp at 42 g.

   Use the exact local context to avoid unnecessary repetition, but retain the same non-evaluative principle.

5. **Regenerate both manuscripts and every derived surface.** Run the text generator in write mode and any front-matter/caption generators whose inputs include the corrected block. Confirm that no generated output was manually edited afterward.

6. **Search all Paper 1 submission surfaces.** Search not only for `small`, but for the exact retired constructions and close evaluative variants. Review each hit manually because `small sample`, `small positive upper bound`, and similar factual uses may be legitimate.

7. **Read the corrected claim continuously.** Review title, abstract, significance paragraph, Methods description of ranges, Results headline, Table 4a and note, endpoint synthesis, Supplementary Table S3 reading, Discussion, Conclusions, cover letter, Highlights, and Figure 3 caption as one argument. Confirm that the favourable point estimate remains obvious and that no surface states or implies absence/equivalence.

### Potential pitfalls, errors, and oversights

- Replacing `small` with `less than half a percentage point` can preserve the same practical judgment through a seemingly quantitative threshold. Prefer the exact signed value.
- Adding more caveats can bury the observed favourable direction. The correction must not become an over-correction.
- Repeating `−0.394 pp` with inconsistent sign conventions can create an apparent contradiction. Always state whether the contrast is model minus comparator and which sign favours the model.
- Calling the ranges `confidence intervals`, `uncertainty intervals`, or `statistical intervals` would overstate their calibration.
- Saying the advantage is `not reproducible` or `not useful` would reverse non-establishment into an absence verdict.
- Correcting the manuscript but leaving the canonical draft or generator unchanged would recreate the defect on the next regeneration.
- A global ban on the word `small` would create false positives for sample size, numerical tolerances, or physically small quantities unrelated to practical value.

### Required checks

- The generator output contains the approved symmetric decision boundary.
- Both manuscripts are byte-consistent with the generator where expected.
- All six active submission surfaces pass the prohibitive scanner.
- Exact regression tests fail if any of the four retired constructions is reintroduced.
- Mutation tests cover `therefore small`, `still small`, `small held-out advantage`, `only <signed value>`, `well under <threshold>`, and equivalent punctuation/hyphenation.
- Numerical invariants remain exact.
- Manual read confirms that the point estimate is prominent and the conclusion remains evidence-limited.

### Acceptance evidence

Retain the generator diff, regenerated manuscript diffs, the exact absence search, targeted test output, numerical-invariant output, and a short manual-reading record identifying every surface reviewed.

---

## P1-1 — Replace whole-clause disclaimer suppression with proposition-linked scope

### Objective

Permit genuine statements of non-establishment while preventing a disclaimer in one grammatical unit from licensing an explicit verdict in another. The scanner must distinguish:

- a decision term that is the object of `does not establish`, `remains unclear whether`, or a comparable epistemic frame; from
- a separate asserted verdict that merely appears later in the same heuristic clause.

### Primary files and components

- `puckworks/paper_a/claim_policy.py`
  - `_SAFE_CONSTRUCTIONS`
  - `_CLAUSE_BOUNDARY`
  - `iter_decision_clauses()`
  - `find_non_establishment_spans()`
  - `_governed()`
  - `scan()`
- `tests/test_paper_a_claim_policy.py`

### Method

1. **Replace the current start-to-end-of-clause span.** `find_non_establishment_spans()` currently gives every recognized construction a span from its start to the end of the heuristic clause. Replace that with a `NonEstablishmentSpan` representation that identifies only the controlled complement of the epistemic construction.

   A suitable internal form is:

   ```python
   @dataclass(frozen=True)
   class NonEstablishmentSpan:
       start: int
       end: int
       construction_id: str
       complement_kind: str
   ```

2. **Recognize a deliberately narrow grammar.** Do not attempt unrestricted English parsing. Define controlled patterns whose capture group is the proposition being disclaimed. At minimum cover:

   - `does/do/did not establish|determine|show|demonstrate|support|resolve [that|whether|if] <proposition>`;
   - `cannot establish|determine|show|support <proposition>`;
   - `<proposition> is/was not established|determined|shown|supported`;
   - `whether|if <proposition> remains unresolved|unclear`;
   - `insufficient to determine whether <proposition>`;
   - `leaves unresolved whether <proposition>`;
   - `does not permit us to conclude that <proposition>`; and
   - the existing generated symmetric formulation.

3. **Capture only the grammatical complement.** A verdict match is safe only if its entire span is inside the captured complement. End the complement at a sentence terminator, semicolon, colon, dash, contrastive conjunction, causal/appositive continuation, or comma that begins a new independent clause.

4. **Handle fronted subordinate clauses explicitly.** In:

   > Although this analysis does not establish superiority, the model outperforms the comparator.

   the safe span must end at the comma closing the subordinate clause. It must not reach the main-clause `outperforms` match.

5. **Handle causal and appositive continuations explicitly.** The following must fail because the verdict is asserted as a reason or restatement, not disclaimed:

   - `This analysis does not establish superiority because the model outperforms the comparator.`
   - `This analysis cannot determine equivalence, meaning the models are essentially the same.`
   - `We do not claim equivalence in formal terms, the models are essentially the same in practice.`

6. **Recognize embedded questions as safe.** The following must pass:

   - `Whether the model outperforms the comparator remains unresolved.`
   - `The data are insufficient to determine whether the model outperforms the comparator.`
   - `It remains unclear whether the model outperforms the comparator.`
   - `The analysis leaves unresolved whether the model outperforms the comparator.`
   - `The data do not permit us to conclude that the model outperforms the comparator.`

7. **Keep the rule explainable.** Document each accepted grammar and its termination rules. The scanner should remain deterministic and reviewable, but its documented claim must be modest: it is a controlled-text backstop, not a general grammatical parser.

8. **Make generated central text the primary defence.** Even after improving scope, do not treat scanner success as proof that arbitrary prose expresses the intended conclusion. Central surfaces should be rendered from approved claim structures as described under P1-3.

### Required regression matrix

| Sentence | Expected result |
|---|---|
| Although this analysis does not establish superiority, the model outperforms the comparator. | fail |
| While this analysis does not establish superiority, the model outperforms the comparator. | fail |
| Whereas this analysis does not establish equivalence, the models are essentially the same. | fail |
| This analysis does not establish superiority because the model outperforms the comparator. | fail |
| This analysis cannot determine equivalence, meaning the models are essentially the same. | fail |
| We do not claim equivalence in formal terms, the models are essentially the same in practice. | fail |
| This analysis does not establish superiority; the model outperforms the comparator. | fail |
| This analysis does not establish superiority, but the model outperforms the comparator. | fail |
| Whether the model outperforms the comparator remains unresolved. | pass |
| The data are insufficient to determine whether the model outperforms the comparator. | pass |
| It remains unclear whether the model outperforms the comparator. | pass |
| The analysis leaves unresolved whether the model outperforms the comparator. | pass |
| The data do not permit us to conclude that the model outperforms the comparator. | pass |

### Potential pitfalls, errors, and oversights

- Adding more words to `_CLAUSE_BOUNDARY` without changing scope will not fix the defect.
- Letting a safe construction govern to sentence end recreates the false negative.
- Treating every occurrence after `whether` as safe could exempt reported or quoted verdicts unrelated to an epistemic frame.
- Overly narrow patterns can force authors into scanner-specific prose and create false positives for ordinary scientific language.
- A dependency parser would add opaque behavior, model/version drift, and a large dependency for a narrow policy. A controlled grammar plus generated central text is more auditable here.
- Offsets must be computed after the same normalization used for rule matching; otherwise punctuation/emphasis normalization can misalign spans.

### Required checks

- All sentences in the regression matrix produce the expected outcome.
- Existing genuine-disclaimer fixtures continue to pass.
- Existing explicit-verdict fixtures continue to fail.
- Random punctuation and conjunction mutations do not change the intended classification.
- A review comment in the code accurately states the scanner’s limits and does not call it a parser if it is not one.

### Acceptance evidence

Retain the red/green regression matrix, coverage of every controlled grammar, mutation-test output, and a manual review of all generated non-establishment sentences.

---

## P1-2 — Expand verdict coverage without making the phrase list load-bearing

### Objective

Close the ordinary paraphrase gaps demonstrated in Round 12 while explicitly treating the phrase taxonomy as defence-in-depth. Routine copy-editing must not convert the central claim into an absence, equivalence, superiority, or practical-negligibility verdict.

### Primary files and components

- `puckworks/paper_a/claim_policy.py`
  - `RULES`
- `tests/test_paper_a_claim_policy.py`
- generated central-claim renderers and positive-coverage machinery addressed under P1-3

### Method

1. **Add exact failing probes before modifying rules.** Pin all of the following:

   - `The model has no advantage.`
   - `There is no advantage.`
   - `The model shows no advantage.`
   - `The model is no better than the comparator.`
   - `The comparator is just as accurate.`
   - `The observed gain is minuscule.`
   - `The difference is negligible.`
   - `The model has a tiny held-out advantage.`
   - `consistent with the small held-out skill above`

2. **Add structural rule classes rather than isolated sentences.** Cover at least:

   - subject + `has|shows|provides|offers` + `no` + value noun;
   - existential `there is/was no` + value noun;
   - `no better than` and `just as accurate|precise|effective` equivalence formulations;
   - copular magnitude judgments on `difference`, `effect`, `increment`, `contrast`, `gain`, `advantage`, and `improvement`;
   - adjectives including `minuscule`, `negligible`, `tiny`, `trivial`, `marginal`, `slight`, and existing variants; and
   - hyphenated and multiword modifiers such as `held-out`, `cross-grind`, and `incremental predictive` between adjective and head noun.

3. **Use bounded, head-noun-aware patterns.** Permit `small held-out sample` and `tiny numerical tolerance` while prohibiting `small held-out advantage`. The rule should bind the practical-magnitude adjective to a declared value noun, not simply search for the adjective.

4. **Preserve non-establishment exceptions through P1-1 scope.** `This analysis establishes no advantage` is a verdict and should fail; `This analysis does not establish an advantage` is a non-establishment statement and should pass because the verdict phrase lies inside the controlled complement.

5. **Add realistic mutation tests.** Starting from a prohibited sentence, mutate:

   - adverb insertion (`therefore`, `still`, `only`, `very`);
   - hyphenation (`held-out`, `cross-context`);
   - active/passive voice;
   - singular/plural head nouns;
   - subject substitution (`model`, `predictor`, `mechanistic formulation`);
   - copular verb substitution (`is`, `remains`, `appears` where asserted); and
   - head-noun substitution (`gain`, `difference`, `advantage`, `effect`, `increment`).

6. **Document residual incompleteness.** The test suite may pin deliberately unsupported idioms, but the production documentation must not describe the taxonomy as exhaustive. The central claim must remain protected by approved rendering and proposition-level coverage.

### Potential pitfalls, errors, and oversights

- Broad patterns for `no advantage` may flag unrelated methodological statements. Limit scanning to Paper A claim surfaces and use contextual head nouns.
- Adding `appears small` may raise questions about hedged subjective statements; without a practical margin it remains a practical-magnitude judgment and should normally fail on central result surfaces.
- Allowing arbitrary intervening `\w+` tokens misses hyphenated words and can overrun into unrelated phrases. Use a bounded token pattern that explicitly includes hyphens.
- A growing synonym list can create false assurance. The implementation and documentation must continue to state that this is a backstop.
- Rule error messages should not themselves repeat unsupported wording such as `the observed advantage is small`.

### Required checks

- Every Round 12 paraphrase fails under the current evidence status.
- Legitimate controls such as `small sample`, `small positive upper bound`, `matched records`, and `no practical margin was predeclared` remain legal.
- Mutation tests demonstrate stable classification under ordinary copy-edits.
- Central generated surfaces do not depend on a particular adjective being listed to remain scientifically compliant.

### Acceptance evidence

Retain the rule-by-rule test matrix, false-positive controls, mutation results, and a code comment stating the taxonomy’s limited role.

---

## P1-3 — Replace substring assertion coverage with affirmative proposition verification

### Objective

Prove that each required proposition is affirmatively communicated on each required surface. Negated, quoted, hypothetical, conditional, reported, instructional, or metalinguistic mentions must not satisfy positive coverage.

### Primary files and components

- `puckworks/paper_a/claim_policy.py`
  - `Assertion`
  - `ASSERTIONS`
  - `SURFACE_ASSERTIONS`
  - `missing_assertions()`
- central claim generators in `tools/paper_a_transfer_text.py`
- front-matter/Highlights generation
- figure-caption generation
- `tests/test_paper_a_claim_policy.py`
- `tests/test_paper_a_transfer_contract.py`
- any surface-parity tests

### Preferred implementation model

Use a hybrid of **typed generated claims** and **approved complete-sentence variants**.

1. Define a proposition enum or immutable IDs:

   ```python
   class ClaimProposition(Enum):
       OBSERVED_ADVANTAGE = "observed_advantage"
       RANGES_UNCALIBRATED = "ranges_uncalibrated"
       NO_DECISION_CLAIMED = "no_decision_claimed"
       ACCURACY_INSUFFICIENT = "accuracy_is_insufficient"
   ```

2. Have each authoritative renderer return a structured object:

   ```python
   @dataclass(frozen=True)
   class RenderedClaim:
       text: str
       propositions: frozenset[ClaimProposition]
       source_values_sha256: str
       renderer_id: str
   ```

   The renderer, not a caller-provided tag, determines which propositions its exact template carries.

3. During final assembly, verify that the exact rendered text appears in the designated generated block and that the block digest matches the renderer output. Collect proposition IDs only from verified generated blocks.

4. For unavoidable hand-authored standalone sentences, use approved **whole-sentence** variants with declared polarity and role. Do not accept arbitrary fragments. For example:

   ```python
   AssertionVariant(
       proposition=ClaimProposition.ACCURACY_INSUFFICIENT,
       exact_sentence="Endpoint accuracy alone did not establish mechanistic transfer.",
       polarity="affirmative_non_establishment",
   )
   ```

5. Parse visible prose into sentence/node spans and exclude:

   - quoted strings;
   - code spans/fences;
   - HTML comments;
   - headings that merely instruct an editor;
   - conditional antecedents;
   - reported speech; and
   - sentences carrying a local negation that reverses the approved proposition.

6. Retain a separate prohibitive scan over quotations if the policy intentionally forbids dangerous wording from shipping even as a quotation. Positive and negative checks have different semantics and should not share the same exemption behavior.

7. Make `missing_assertions()` consume verified proposition evidence, not `any phrase is a substring`. If a surface contains both an approved sentence and a contradictory sentence, fail on contradiction rather than declaring coverage satisfied.

### Required negative fixtures

The following must **not** satisfy positive coverage:

- `Observed pooled error was not 0.394 points lower.`
- `These are not uncalibrated ranges.`
- `The phrase “support no superiority” is not this paper’s conclusion.`
- `The caption must include “−0.394 pp”.`
- `If the difference were −0.394 pp, the model would be favoured.`
- `The reviewer called the difference −0.394 pp.`
- a block quote containing an otherwise approved sentence;
- an HTML comment containing an approved sentence; and
- an instruction that names every required phrase without asserting any of them.

### Required positive fixtures

Each required surface should have a fixture containing the exact approved generated block or approved full-sentence variant and must report the intended proposition set. At minimum test:

- abstract;
- editor significance paragraph;
- cover letter;
- Results headline;
- endpoint synthesis;
- supplement reading;
- conclusion;
- Highlights; and
- Figure 3 caption.

### Potential pitfalls, errors, and oversights

- Merely changing from phrase substring to sentence substring still accepts negated or quoted exact sentences if context is ignored.
- Allowing the caller to supply proposition IDs recreates the trusted-boolean problem in a different type.
- Exact-sentence matching can be brittle if whitespace or typography changes. Normalize only typography and whitespace that cannot change meaning; do not normalize away negation or punctuation boundaries.
- Generated blocks may be duplicated in a surface. Require the expected count and location.
- A surface can assert both the permitted proposition and a contradictory verdict. Coverage must be combined with contradiction scanning.
- A semantic NLP classifier would introduce opaque false positives/negatives. For high-stakes central prose, controlled templates are preferable.

### Required checks

- All negation/quotation/metalinguistic probes fail positive coverage.
- Every designated surface carries its required proposition IDs through verified generated text or approved full sentences.
- Contradictory surfaces fail even when they include all required sentences.
- Generated-block hashes and expected counts are checked.
- Existing surface-parity checks continue to pass after regeneration.

### Acceptance evidence

Retain the structured-renderer design, exact approved sentence inventory, negative fixture output, surface proposition matrix, and final generated-block hashes.

---

## P1-4 — Make inferential permission reverified at the point of use

### Objective

Ensure that no directly constructed Python object, imported sentinel, test fixture, or caller-selected registry can unlock superiority, equivalence, non-inferiority, absence, calibrated-coverage, or margin-dependent prose in production.

### Primary files and components

- `puckworks/paper_a/inferential_evidence.py`
  - `_VERIFIED`
  - `VerifiedInferentialStatus`
  - `verify_inferential_evidence()`
  - `PROCEDURE_REGISTRY`
- `puckworks/paper_a/claim_policy.py`
  - `granted()`
- `tests/test_paper_a_inferential_evidence.py`
- `tests/test_paper_a_claim_policy.py`

### Method

1. **Stop treating type identity as provenance.** Remove the claim that `VerifiedInferentialStatus` is unforgeable. In-process Python code that can import a module can inspect module attributes and construct ordinary classes.

2. **Change the production permission API.** `claim_policy.granted()` should not accept a pre-verified object as sufficient evidence. It should accept either:

   - the current descriptive `InferentialStatus`, which grants nothing; or
   - an immutable evidence reference/ID that is reverified against canonical production artefacts and the production registry at the point of use.

   A suitable shape is:

   ```python
   @dataclass(frozen=True)
   class InferentialEvidenceReference:
       evidence_id: str

   def granted(status_or_reference) -> set[str]:
       if isinstance(status_or_reference, TS.InferentialStatus):
           return set()
       if not isinstance(status_or_reference, InferentialEvidenceReference):
           raise TypeError(...)
       receipt = verify_registered_production_evidence(status_or_reference.evidence_id)
       return receipt.permissions
   ```

3. **Reverify from canonical storage.** `verify_registered_production_evidence()` must load the evidence record, result, protocol, estimand contract, source manifest, and procedure from fixed production locations/registries. It must not trust decisive fields carried in the caller’s object.

4. **Separate production and test seams.** Keep synthetic procedures and arbitrary registries available only through an explicitly named test helper, such as `verify_inferential_evidence_for_test()`. Production rendering and `claim_policy.granted()` must have no parameter through which a caller can inject a registry.

5. **Make any verification receipt informational, not authoritative by itself.** A receipt may record result/protocol hashes, verifier version, registry hash, and derived permissions for audit, but production permission should either revalidate the receipt against canonical artefacts or regenerate it. Possession of a receipt object alone must not be sufficient.

6. **Retire the sentinel as a security claim.** `_VERIFIED` may remain as an internal construction convenience, but a directly constructed object using it must still grant nothing because `granted()` no longer trusts that object.

7. **Keep the current Paper A behavior unchanged.** The production registry is empty and the present analysis requests no inferential decision. The refactor should therefore leave current publication prose in the descriptive, evidence-limited state.

### Potential pitfalls, errors, and oversights

- Making the class name private or using name-mangling does not create a security boundary.
- Signing a receipt with a key stored in the same repository/process would merely move the token.
- Caching permissions can become stale if an artefact changes. Cache only against complete content hashes and invalidate on any hash mismatch.
- Allowing a registry argument in a broadly used production function makes test injection available in production.
- Reverification must not mutate the evidence or silently repair inconsistent fields.
- The production registry’s emptiness must remain fail-closed, not trigger a fallback to declared flags.

### Required checks

- Import `_VERIFIED`, directly construct `VerifiedInferentialStatus`, and prove that `granted()` raises or returns the empty set.
- Supply a synthetic registry through the test seam and prove it cannot reach production rendering.
- Change one canonical artefact after producing a receipt and prove permission is denied.
- Verify that a plain `InferentialStatus` grants nothing regardless of its declared flags.
- Confirm current Paper A generated text remains unchanged except for the intended P0 wording correction.

### Acceptance evidence

Retain the forged-object regression, production/test API boundary tests, stale-receipt test, and output showing the current production registry grants no decision language.

---

## P1-5 — Bind inferential decisions to parsed result semantics and demonstrable chronology

### Objective

Make a decision reproducible from the contents of the digest-bound result, a validated procedure implementation, a matching estimand, and a practical-margin protocol that demonstrably existed before the result. A matching opaque hash must no longer be enough.

### Primary files and components

- `puckworks/paper_a/inferential_evidence.py`
  - `ProcedureSpec`
  - `EvidenceRecord`
  - `evidence_from_dict()`
  - `verify_inferential_evidence()` or its production replacement
- new canonical result/protocol schemas, preferably under `puckworks/paper_a/`
- the production procedure registry
- `tests/test_paper_a_inferential_evidence.py`
- migration/idempotence tests if the evidence schema version changes

### Method

1. **Define a canonical analysis-result schema.** The digest-bound result must contain, at minimum:

   - schema version;
   - analysis/result ID;
   - estimand ID and sign convention;
   - procedure ID and version;
   - implementation ID;
   - confidence/coverage level;
   - cluster unit;
   - predictor-refit policy;
   - point estimate;
   - lower and upper interval bounds;
   - decision-relevant sample/cluster counts;
   - source manifest hash;
   - estimand contract hash;
   - code commit/tree or implementation digest; and
   - generation metadata sufficient to reproduce the result.

2. **Hash bytes, then parse those same bytes.** The verifier must:

   - read the canonical result artefact bytes;
   - compute and compare the SHA-256 digest;
   - parse the verified bytes against the schema; and
   - derive the observed interval and every decision-relevant semantic value from that parsed object.

   It must never accept `observed_interval_pp` as an independent caller-authored decisive field.

3. **Remove duplicated decisive fields from `EvidenceRecord`.** Prefer an evidence record that contains references and hashes only. If backward compatibility requires retaining an interval, require exact equality to the parsed result and mark the duplicate as transitional.

4. **Validate `ProcedureSpec` strictly.** Reject empty or whitespace-only:

   - `cluster_unit`;
   - `required_estimand_id`;
   - `implementation_id`;
   - procedure ID/version; and
   - every declared decision-rule ID.

5. **Bind `implementation_id` to code.** Use an immutable identity such as:

   - repository commit/tree;
   - module and callable identifier; and
   - SHA-256 of the source file or packaged implementation artefact.

   The verifier must compare the registered implementation identity with the identity recorded in the result.

6. **Make predeclaration chronological.** A different protocol hash is not proof of predeclaration. The recommended repository-native proof is:

   - a `protocol_commit` containing the exact protocol blob;
   - a `result_commit` or generation commit;
   - verification that `protocol_commit` is a strict ancestor of `result_commit`; and
   - verification that the protocol blob/hash at the ancestor is the one referenced by the result.

   Configure the relevant CI job with sufficient Git history to verify ancestry. For release archives without Git history, include a frozen chronology proof generated by release CI and fail closed if it cannot be validated.

7. **Validate protocol semantics.** The protocol must identify the same estimand, metric, direction, decision class, and units as the result. A margin for another estimand or sign convention must not unlock prose.

8. **Use only the authoritative production registry.** Production verification must not accept arbitrary caller-supplied registries. Synthetic registries belong only in the explicit test seam from P1-4.

9. **Bump the evidence schema version.** Add a migration only if historical evidence must remain readable. The migration must be idempotent and must not invent chronology or result semantics that the old record never contained. Old records lacking sufficient proof should remain non-authoritative.

### Required negative tests

- Actual result interval `[-2.0, 2.0]`, evidence record interval `[-0.3, 0.2]`: verification must fail before decision derivation.
- Protocol created after result: verification must fail.
- Empty `cluster_unit`: registration must fail.
- Empty `implementation_id`: registration must fail.
- Result estimand differs from registered estimand: fail.
- Result procedure version differs from registry: fail.
- Implementation digest differs: fail.
- Protocol margin units or sign convention differ: fail.
- Result bytes change without digest update: fail.
- Evidence digest changes but referenced result path remains the same: fail unless the new canonical result is explicitly registered and reverified.

### Potential pitfalls, errors, and oversights

- Canonical JSON serialization and raw file hashing are different concepts. Hash the actual archived bytes and parse those bytes; do not reserialize and hash a Python object unless the archive contract explicitly defines canonical serialization.
- Git commit timestamps are not reliable chronology proof by themselves. Use ancestry and blob identity, not only dates.
- A shallow CI checkout can make ancestry unverifiable. That must block or the job must fetch sufficient history.
- Floating-point parsing can alter decisive bounds. Preserve decimal tokens or use a declared numeric canonicalization for decision fields.
- A procedure implementation can change while keeping the same module/function name. Include a source or package digest.
- Migration code must not fill missing old fields with plausible defaults and then call the old evidence verified.

### Required checks

- The exact detached-result and post-result-protocol probes fail.
- Positive synthetic evidence passes only through the test seam and only when all result/protocol/implementation semantics agree.
- Current production Paper A remains descriptive because no authoritative procedure is registered.
- Schema migration, if present, is idempotent and refuses to manufacture missing proof.
- Verification output records every artefact hash and the derived decision inputs.

### Acceptance evidence

Retain example canonical result/protocol fixtures, schema validation output, chronology proof output, implementation digest comparison, and negative-test results.

---

## P1-6 — Add the mechanistic-transfer boundary to Highlights

### Objective

Ensure the standalone Highlights file carries all four central propositions within the journal’s 85-character-per-bullet limit.

### Primary files and components

- the authoritative Highlights source, likely `paper_a_front_matter.yaml` or its generator input
- `docs/submission/PAPER_A_JFE_HIGHLIGHTS.txt`
- `puckworks/paper_a/claim_policy.py`
  - `SURFACE_ASSERTIONS["highlights"]`
- `tests/test_paper_a_front_matter.py`
- `tests/test_paper_a_claim_policy.py`

### Method

1. Add `accuracy_is_insufficient` to the Highlights requirement:

   ```python
   "highlights": (
       "observed_advantage",
       "ranges_uncalibrated",
       "no_decision_claimed",
       "accuracy_is_insufficient",
   )
   ```

2. Replace the current redundant fifth bullet with:

   > Endpoint accuracy alone did not establish mechanistic transfer

   This is 62 characters excluding any file-format bullet marker and remains below the 85-character limit even when normal spacing is included.

3. Make the generator, not the output file, authoritative. Regenerate the standalone Highlights file.

4. Count characters exactly as the venue does. Define whether the bullet symbol, leading space, Unicode dash, and trailing whitespace count; apply the stricter interpretation in tests.

5. Verify the file as a whole carries all four propositions and that no individual bullet contains prohibited magnitude/equivalence language.

### Potential pitfalls, errors, and oversights

- Editing `PAPER_A_JFE_HIGHLIGHTS.txt` directly will be overwritten.
- Character counts can differ between Python code points and rendered glyphs; the venue limit is ordinarily character-based, so test code points after normalizing line endings and excluding only the file’s structural bullet marker if the journal does not receive it.
- The new bullet should not say endpoint accuracy proves no mechanism transfer. `Did not establish` is the required evidentiary formulation.
- Replacing a bullet can reduce coverage of another proposition. Re-run the complete Highlights proposition matrix.

### Required checks

- 3–5 bullets remain present.
- Every bullet is ≤85 characters under the documented counting rule.
- Highlights positive coverage includes all four propositions.
- The standalone file passes leakage and prohibited-language scans.
- Front-matter parity tests pass.

### Acceptance evidence

Retain the generated file diff, per-bullet character counts, and the four-proposition coverage output.

---

## P1-7 — Preserve raw coordinate identity before float conversion

### Objective

Ensure that distinct valid decimal source coordinates cannot collapse before source validation, condition-key construction, support reconciliation, clustering, census, or lookup membership.

### Primary files and components

- `puckworks/data/__init__.py`
  - `_typed_rows()`
  - `_typed_rows_hashskip()`
  - Angeloni-specific loader(s)
- `puckworks/paper_a/source_schema.py`
  - `parse_coordinate()`
  - `read_rows()` / `parse_rows()`
- production transfer-corpus construction
- independent source oracle
- `tests/test_paper_a_source_schema.py`
- `tests/test_paper_a_transfer_contract.py`
- numerical/manifest invariant tests

### Method

1. **Route identity-bearing source rows through raw parsing first.** For `angeloni2023/bioactives.csv`, use raw `csv.DictReader` tokens or `source_schema.read_rows()` as the authoritative input. Call `source_schema.parse_rows()` before any generic typed loader converts cells.

2. **Separate identity from computation.** Keep exact `Decimal` values in `SourceRow`/`ConditionKey` for:

   - temperature and pressure identity;
   - duplicate detection;
   - support membership;
   - cluster IDs;
   - on-grid reconciliation; and
   - manifest/census construction.

   Convert `Decimal` to `float` only at a downstream arithmetic boundary that does not determine identity.

3. **Make loss of the raw token visible.** Change `parse_coordinate()` so a float is rejected by default for source-identity parsing. If a legacy/test-only float path must remain, require an explicit `allow_lossy_float=True` argument that production never uses and document that it cannot recover the source token.

4. **Correct the docstring.** State that `repr(float)` recovers a round-trippable representation of the binary float, not the original decimal token.

5. **Avoid a risky global loader change where possible.** The generic `_typed_rows()` functions are used by many datasets. Prefer an Angeloni/source-schema-specific raw path or add an explicit `preserve_raw_fields` schema hook rather than changing every dataset’s return types silently.

   A safe generic extension would be:

   ```python
   def _typed_rows(path, *, preserve_raw_fields=frozenset()):
       ...
       return [
           {k: v if k in preserve_raw_fields else conv(v) for k, v in row.items()}
           for row in _rows(path)
       ]
   ```

   Production must then pass all identity/control fields explicitly. A dedicated schema-first loader is preferable because it makes omission harder.

6. **Detect collisions and duplicate conditions explicitly.** If two distinct raw decimal values ever canonicalize to the same identity unexpectedly, raise an error naming both sample IDs, raw tokens, and source lines. Numerically equal forms such as `9`, `9.0`, and `9.00` may intentionally share an identity; numerically distinct decimals must not.

7. **Add end-to-end temporary-CSV tests through the production path.** Include:

   - `93.4000400000000001` and `93.4000400000000002`;
   - `10.0000000000000001` and `10.0000000000000002`;
   - equivalent forms `9`, `9.0`, `9.00`;
   - `-0` and `0`;
   - scientific notation if the schema permits it;
   - non-finite values;
   - leading/trailing whitespace; and
   - duplicate sample IDs.

8. **Regenerate the transfer artefacts.** Because this changes the production source path, rerun the full source-to-artefact producer. The current corpus should reproduce byte-identically or with an explicitly explained serialization-only change. Any membership, manifest, cluster, result, or protected-number change is a stop condition requiring scientific adjudication.

### Potential pitfalls, errors, and oversights

- Preserving raw tokens for only one coordinate but not the other leaves a partial collision path.
- Converting `Decimal` back to float before constructing `ConditionKey` recreates the defect.
- Different textual forms of the same exact number should not become false distinct conditions unless the scientific contract defines token identity rather than numerical identity.
- A generic loader signature change may break unrelated datasets. Add focused compatibility tests.
- Decimal context precision should not round parsed source tokens. Construct `Decimal` directly from strings and avoid arithmetic before canonicalization.
- Sorting/serialization of `Decimal` keys must remain deterministic.

### Required checks

- Both distinct-token collision probes remain distinct through the production loader and manifest path, or the loader fails explicitly before coercion.
- Equivalent numerical tokens canonicalize as intended.
- Current Angeloni corpus membership, counts, support, cluster IDs, and manifest hash are unchanged unless a serialization migration is deliberately declared.
- Production and independent oracle still derive membership separately but consume the same validated raw schema.
- Full scientific regeneration and exact numerical invariants pass.

### Acceptance evidence

Retain temporary CSV fixtures, production-path outputs, before/after manifest hashes, corpus comparison, regeneration logs, and exact endpoint invariant results.

---

## P1-8 — Close raw-HTML, comment, and metadata-exemption leakage channels

### Objective

Ensure no internal path, review history, producer identifier, or repository-process narration can enter any uploaded Paper A deliverable through Markdown destinations, raw HTML, comments, percent encoding, or overbroad metadata exemptions.

### Primary files and components

- `tools/paper_a_consistency.py`
  - destination extraction and `_HTML_TARGET`
  - `_normalise_target()`
  - HTML comment handling
  - `_UNSUPPLIED_METADATA`
  - upload-file scope and exemptions
- `tests/test_paper_a_submission_scanner.py`
- all five upload deliverables governed by the package

### Method

#### A. Parse raw HTML structurally

1. Replace `_HTML_TARGET` regex extraction with an HTML tokenizer/parser. Python’s standard `html.parser.HTMLParser` is sufficient for quoted and unquoted attributes if the accepted HTML subset is narrow and tested.

2. Extract every permitted URL-bearing attribute, at minimum:

   - `href`;
   - `src`;
   - `srcset` candidates;
   - `poster`;
   - `cite`;
   - `action`;
   - `formaction`; and
   - `data` if the accepted submission syntax permits it.

3. Parse `srcset` as multiple URL candidates and scan each. Do not treat the whole attribute as one target.

4. Decode HTML entities, then percent-decode and normalize slashes/dot segments before applying path rules. Define bounded repeated decoding or reject multiply encoded targets so double encoding cannot bypass the rule.

5. Preserve source-line information for actionable diagnostics.

#### B. Scan comments in verbatim uploads with the full policy

6. For `PAPER_A_JFE_HIGHLIGHTS.txt` and `PAPER_A_JFE_FIGURE_CAPTIONS.md`, apply review-history, producer-identifier, internal-narration, and internal-path rules to HTML comments, not only `_INTERNAL_PATH_RX`.

7. Exempt only exact per-file generation stamps. Prefer a literal expected stamp generated by the authoritative tool rather than a broad regex such as `contains GENERATED`. Any additional comment must fail.

8. Add a rendered-file invariant requiring exactly the expected comment count and exact comment text.

#### C. Narrow the metadata exemption to an exact placeholder node

9. Replace paragraph-/line-wide exemption with an exact approved placeholder grammar. The simplest safe policy for upload surfaces is:

   - the normalized paragraph must consist solely of an approved unsupplied-metadata placeholder; and
   - it must contain no link/image/raw-HTML destination or unrelated prose.

10. If one tracking reference is genuinely necessary, approve one exact reference pattern and target. Do not exempt every target on the same line.

11. A paragraph such as `Funding is not yet supplied. See docs/internal/review.md for the scientific analysis.` must fail both visible-text and destination checks.

#### D. Apply the tests to every applicable upload file

12. Parameterize bypass fixtures across manuscript, supplement, cover letter, Highlights, and standalone captions according to their actual upload/conversion path. Comments must be tested on the two verbatim files specifically.

13. Retain the hard dependency on `markdown-it-py` and the blocking not-run path. If structural parsing is unavailable, submission verification must fail.

### Exact bypass fixtures that must fail

- `<a href=docs/internal/review.md>the analysis</a>`
- `<img src=docs/internal/figure.png alt="figure">`
- `<a href=docs%2Finternal%2Freview.md>the analysis</a>`
- `<img srcset="docs/internal/figure.png 1x" alt="figure">`
- `<video poster="docs/internal/review.png"></video>`
- `<!-- The second review retained a producer identifier. -->`
- `<!-- generated from a private producer identifier -->`
- `Funding is not yet supplied. See docs/internal/review.md for the scientific analysis.`
- `Funding is not yet supplied. See [the scientific analysis](docs/internal/review.md).`

### Potential pitfalls, errors, and oversights

- `HTMLParser` lowercases attribute names but does not validate URL schemes; normalize consistently.
- `srcset` parsing is subtle because commas can appear in data URLs. Either use a tested parser or disallow data URLs in submission HTML.
- Repeated percent decoding can be abused; establish and test a deterministic normalization policy.
- Stripping comments before scanning them recreates the verbatim-upload gap.
- A broad generator-stamp exemption can hide process language placed beside the word `GENERATED`.
- Path normalization must handle backslashes, `./`, `../`, percent-encoded separators, and HTML entities.
- Conversion assumptions must remain documented. If the actual submission workflow changes and comments start shipping from another file, scope must be updated.

### Required checks

- Every exact bypass fixture fails with the correct file and source line.
- Quoted and unquoted HTML attributes are both detected.
- Every `srcset` candidate is scanned.
- Only the exact approved generator stamp passes in verbatim files.
- Exact standalone metadata placeholders pass; placeholders with extra prose or any target fail.
- Missing `markdown-it-py` blocks verification.
- Existing legitimate figure targets and public DOI/Zenodo targets remain allowed.

### Acceptance evidence

Retain the parser tests, target-normalization table, comment-policy tests, exact placeholder tests, and full submission-scanner output for all upload deliverables.

---

## P2-1 — Preserve and validate producer stems in the caption mapping

### Objective

Prove a one-to-one mapping between presentation figure number and producer stem, independently of caption freshness and body validity.

### Primary files and components

- `tools/paper_a_figure_captions.py`
  - `_HEADING`
  - `captions()`
  - `caption_set_problems()`
- `docs/figures/PAPER_A_FIGURE_MAP_INTERNAL.md`
- preferably a single authoritative figure manifest
- caption tests

### Method

1. Replace tuple extraction with a structured record:

   ```python
   @dataclass(frozen=True)
   class CaptionEntry:
       number: str
       producer_stem: str
       caption: str
       source_line: int
   ```

2. Preserve `match.group(2)` from `_HEADING` and pass it through all validation and rendering stages.

3. Establish one authoritative expected mapping. Prefer a machine-readable manifest consumed by the internal map generator, caption generator, package manifest, and tests. Avoid maintaining the same mapping independently in several Python constants and Markdown tables.

4. Validate:

   - every expected figure number appears exactly once;
   - every expected producer stem appears exactly once;
   - no unknown number or stem appears;
   - each number maps to the expected stem;
   - main/supplementary sets are complete; and
   - the caption’s visible `Figure N` label agrees with the entry number.

5. Keep mapping validity separate from:

   - caption-body structural validity; and
   - generated upload-file freshness.

   All three gates must pass independently.

6. Add mutation tests for duplicate stem, swapped stems, missing stem, unknown stem, duplicated number, missing number, and stale output.

### Potential pitfalls, errors, and oversights

- An expected mapping duplicated in a test constant can drift with the production constant. Use one declarative manifest and test its consumers.
- Renumbering a presentation figure is not necessarily a producer rename. The mapping must make that distinction explicit.
- Producer stems may contain hyphens or underscores; preserve them exactly rather than normalizing them into possible collisions.
- Sorting by presentation number must not erase the source mapping before validation.

### Required checks

- All mapping mutations fail for the intended reason.
- Current figure map passes unchanged if it is correct.
- Upload caption freshness and body-structure checks remain independent.
- The package figure inventory consumes or cross-checks the same manifest.

### Acceptance evidence

Retain the figure manifest, mapping validation output, and mutation-test results.

---

## P2-2 — Reduce Figure 3 to an editor-usable standalone caption

### Objective

Reduce Figure 3 from approximately 287 words to roughly 150–200 words while retaining everything necessary to interpret the figure and the central evidence boundary.

### Primary files and components

- the authoritative generated Figure 3 caption source in `tools/paper_a_transfer_text.py` or its upstream template
- `docs/figures/PAPER_A_FIGURE_MAP_INTERNAL.md`
- `docs/submission/PAPER_A_JFE_FIGURE_CAPTIONS.md`
- caption-generation and claim-coverage tests

### Proposed replacement caption

The following is approximately 150 words and carries the required content:

> **Figure 3. Within-campaign cross-grind prediction after target-specific calibration.** For each variety–solute group, inventory and rate were fitted to nine optimal-grind conditions and frozen for coarse/fine prediction at 40 g. Panels show the complete held-out corpus (44 records × 3 solutes = 132 observations, including 8 off-grid records) and summarize error by target grind. The comparator is an optimal-grind-trained level-only constant with no process or kinetic response. Pooled MAPE was 8.44% for the mechanistic model and 8.83% for the constant, a model-minus-comparator difference of −0.394 percentage points favouring the mechanistic model; the model had the larger absolute error on 62 of 132 observations. The 108-observation matched-grid subset is secondary and supplies the lookup comparator. Clustered ranges are fixed-predictor sensitivity ranges, not calibrated confidence intervals; without a predeclared practical margin they establish neither a comparator decision nor its absence. Endpoint accuracy alone does not establish mechanistic transfer. Evidence tier: within-campaign cross-grind holdout.

### Method

1. Edit the authoritative generator/template, not the upload caption file.
2. Retain panel-reading instructions, corpus scope, comparator definition, headline numbers, sensitivity-range status, symmetric non-decision, and transfer boundary.
3. Move detailed near-optimal-rate-envelope mechanics, lookup-support detail beyond what is needed to identify the secondary subset, and extended method interpretation to the main text or supplement.
4. Regenerate the internal map and upload caption file.
5. Run positive coverage for all four Figure 3 propositions.
6. Add a non-blocking or blocking caption-length policy. A sensible gate is a warning above 200 words and a hard failure above an explicitly justified ceiling, with Figure 3 held to the approved target in a focused test.

### Potential pitfalls, errors, and oversights

- Over-shortening can remove the complete-corpus/off-grid distinction or make the lookup comparator appear part of the headline corpus.
- Calling ranges confidence intervals or implying a decision would recreate the central claim defect.
- Removing `62/132 worse` would make the favourable pooled difference appear more uniformly favourable than observed.
- A hand edit to the upload file will be overwritten.
- Caption word counts should ignore Markdown emphasis markers but include visible labels and numbers consistently.

### Required checks

- Caption is within the approved word target.
- It carries all four required propositions.
- All protected numbers and corpus counts match the artefact.
- No prohibited practical-magnitude wording appears.
- Internal map and upload file are fresh and structurally valid.

### Acceptance evidence

Retain before/after word counts, generated diffs, claim-coverage output, and numerical-parity output.

---

## P2-3 — Resolve the contradictory package status for outstanding reruns

### Objective

Make one authoritative source state whether replicate/measurement-uncertainty sensitivity reruns are complete, outstanding, or not part of the submission requirement. The package must not say both that science reruns are complete and that a potentially conclusion-changing rerun remains.

### Primary files and components

- `docs/submission/PAPER_A_JFE_PACKAGE.md`
- `tools/paper_a_front_matter.py --check-submission-ready`
- relevant analysis artefacts and gates for the objective-family sweep, bounded refit bootstrap, and replicate/measurement-uncertainty sensitivity
- package/readiness tests

### Method

1. **Identify the exact analysis named by item 2.** Determine whether `replicate/measurement-uncertainty sensitivity reruns` is:

   - the already completed objective-family sweep/bounded refit bootstrap described at the top of the package;
   - a distinct completed analysis with a different artefact;
   - a distinct outstanding analysis; or
   - stale wording for work no longer required.

2. **Bind status to evidence.** Create or extend a machine-readable submission-readiness manifest with fields such as:

   - requirement ID;
   - description;
   - state (`complete`, `outstanding`, `not_required`);
   - governing artefact path and SHA-256;
   - completion gate/test;
   - conclusion-change potential; and
   - last adjudicated commit.

3. **Generate or validate package prose from the manifest.** The top status paragraph and conversion checklist must consume the same authoritative state or be cross-checked against it.

4. **Apply the correct branch:**

   - **If already complete:** remove conversion item 2 and cite the completion artefact/gate in the readiness manifest.
   - **If distinct and outstanding:** add it to the authoritative outstanding list, execute it, update affected artefacts and prose if required, and block submission until complete.
   - **If not required:** remove it and record the scientific/governance reason so it does not reappear.

5. **Reclassify severity if necessary.** If the rerun can change figures, abstract, discussion, or conclusion, treat it as at least P1. If it can change the central conclusion, treat it as P0 and repeat the scientific review after completion.

### Potential pitfalls, errors, and oversights

- Similar analysis names may refer to different uncertainty treatments. Confirm producer, inputs, estimand, and output, not only wording.
- Deleting the task without locating completion evidence can hide genuinely outstanding work.
- Marking an item `complete` because a file exists is insufficient; bind it to a passing gate and current inputs.
- A rerun that changes values requires regeneration of every dependent surface and a fresh numerical/claim review.
- Hand-maintained status prose will drift again unless tied to one manifest.

### Required checks

- No contradictory readiness statements remain.
- The readiness checker reports the same state as the package prose.
- Every completed science item names a current artefact and gate.
- Every outstanding conclusion-relevant item blocks submission.
- If the rerun is executed, numerical invariants and all dependent generated surfaces are reviewed again.

### Acceptance evidence

Retain the readiness-manifest diff, artefact hashes, gate output, and the explicit decision on whether item 2 was stale, complete, or outstanding.

---

## P2-4 — Remove the duplicated comparator-ladder phrase

### Objective

Correct the duplicated phrase in both manuscript sources and make the comparator ladder understandable to a reader.

### Primary files and components

- `docs/submission/PAPER_A_JFE_MANUSCRIPT.md`
- `docs/PAPER_A_DRAFT.md`
- the authoritative generator/template if the paragraph is generated
- text parity/editorial tests

### Method

1. Locate every occurrence of:

   > An in-sample comparator ladder (in-sample comparator ladder) makes its adequacy auditable.

2. Prefer an informative replacement:

   > An in-sample comparator ladder (one constant, per-grind constants, a shared mechanistic fit, and per-grind mechanistic fits) makes its adequacy auditable.

   Confirm the four labels exactly match the actual ladder before using this wording. If the surrounding text already defines the ladder, simply delete the parenthetical.

3. Correct the authoritative source and regenerate both manuscripts if applicable.

4. Search the repository for the duplicated phrase and confirm no generated copy remains.

### Potential pitfalls, errors, and oversights

- The proposed expansion must match the actual comparator set; do not introduce a more detailed but inaccurate definition.
- Directly editing only one manuscript creates parity drift.
- The phrase may appear in generated snapshots or package excerpts that also need regeneration.

### Required checks

- Exact duplicate phrase absent repository-wide within Paper 1 surfaces.
- Manuscript and canonical draft agree.
- Comparator labels match the underlying analysis and table.
- Text-generation/parity checks pass.

### Acceptance evidence

Retain the exact search output and corrected paragraph diff.

# 5. Cross-cutting test and validation plan

## 5.1 Add Round 12 probes as permanent regression tests

Convert the focused probe file into named tests rather than keeping it only as an external review artefact. Each test name should identify the assurance property, for example:

- `test_magnitude_verdict_with_intervening_adverb_is_rejected`
- `test_hyphenated_value_modifier_is_rejected`
- `test_fronted_disclaimer_does_not_govern_main_clause`
- `test_embedded_whether_question_is_recognised_as_non_establishment`
- `test_negated_phrase_does_not_satisfy_positive_assertion`
- `test_directly_constructed_verified_status_grants_nothing`
- `test_result_interval_is_derived_from_hashed_result`
- `test_post_result_margin_protocol_is_rejected`
- `test_production_loader_preserves_distinct_decimal_identities`
- `test_unquoted_html_destination_is_scanned`
- `test_verbatim_comment_receives_full_leakage_policy`
- `test_metadata_placeholder_does_not_exempt_adjacent_path`
- `test_caption_mapping_rejects_swapped_producer_stems`

## 5.2 Run generators in the correct development sequence

For each generator affected:

1. run its `--check` and confirm the expected stale/failing state after source edits;
2. run `--write` once the authoritative source is correct;
3. inspect the generated diff;
4. rerun `--check`; and
5. prohibit subsequent manual changes to generated files.

## 5.3 Exact repository verification chain

After all corrections and regeneration, run:

```bash
pip install -e ".[dev]"

python tools/paper_a_numerical_invariants.py --check
python tools/paper_a_transfer_artifacts.py --check
python tools/paper_a_transfer_text.py --check
python tools/paper_a_figure_captions.py --check
python tools/paper_a_consistency.py verify
python tools/paper_a_migrate_schema4.py
python -m puckworks.paper_a.claim_coverage
python -m puckworks.paper_a.slow_lane_bindings
python tools/claim_binding_audit.py

python -m pytest \
  tests/test_paper_a_claim_policy.py \
  tests/test_paper_a_inferential_evidence.py \
  tests/test_paper_a_source_schema.py \
  tests/test_paper_a_submission_scanner.py \
  tests/test_paper_a_transfer_semantics.py \
  tests/test_paper_a_transfer_contract.py \
  tests/test_paper_a_numerical_invariants.py -q

python -m pytest -q
```

Run the migration command in a way that proves idempotence, including a second invocation or its existing idempotence test.

## 5.4 Scientific regeneration requirement

Because P1-7 changes the production source-loading path, run the full transfer artefact producer in write mode:

```bash
python tools/paper_a_transfer_artifacts.py --write
```

Then rerun the entire verification chain. Compare:

- source manifest hash;
- 44/132 and 36/108 corpus membership;
- off-grid count;
- cluster IDs and cluster count;
- all protected endpoint values;
- generated figures/source data;
- manuscript numbers; and
- release bundle hashes where applicable.

An unexpected scientific or corpus change is not an editorial correction. Stop, isolate the cause, and adjudicate it before continuing.

## 5.5 Manual submission-surface read

Automated checks cannot replace the final argument-level read. Review in this order:

1. title;
2. abstract;
3. editor significance paragraph;
4. Methods description of ranges;
5. Results headline;
6. Table 4a and note;
7. endpoint synthesis;
8. Supplementary Table S3 and reading;
9. Discussion;
10. Conclusions;
11. cover letter;
12. Highlights; and
13. Figure 3 caption.

For each surface, record:

- exact observed result and direction;
- range type;
- decision boundary;
- mechanistic-transfer boundary;
- absence of practical-magnitude verdicts; and
- consistency with surrounding surfaces.

## 5.6 Proof Supplementary Table S7 at journal width

This was not a counted Round 12 finding because no final journal-width rendering was available, but it remains a useful lower-priority completion check. Render the supplement using the intended journal page width, font size, margins, and table orientation. Check all 44 rows for clipping, illegible type, wrapped identifiers that become ambiguous, repeated-header behavior, page breaks, unit visibility, and alignment of values with row labels. If the table is not legible at the journal width, prefer a landscape page, continued-table structure, or machine-readable supplement rather than reducing the font below a defensible size. Retain a PDF proof and a row-by-row visual sign-off. This check must not alter scientific values; any value discrepancy should be traced back to the authoritative table source rather than corrected only in the typeset output.

# 6. Stop conditions

Stop the remediation and reopen scientific adjudication if any of the following occurs:

- a protected endpoint number or range changes unexpectedly;
- corpus membership, off-grid count, support, or cluster identity changes;
- a rerun named in P2-3 is genuinely outstanding and can affect the central conclusion;
- chronology of a practical-margin protocol cannot be proven;
- a production inferential procedure remains unlockable through caller-supplied objects or registries;
- any Round 12 adversarial probe still returns a false green;
- a required proposition can be satisfied through negation, quotation, or instruction;
- structural scanning is unavailable or skips a deliverable;
- generated files are manually edited after regeneration;
- figure producer mapping is ambiguous; or
- the full suite or exact verification chain fails.

# 7. Suggested commit structure

Keep the remediation reviewable in logically separate commits:

1. **tests: pin Round 12 false-green reproductions**
2. **paper-a: correct magnitude wording and regenerate publication text**
3. **paper-a: make claim scope and positive coverage proposition-linked**
4. **paper-a: reverify inferential permissions from canonical evidence**
5. **paper-a: preserve raw source-coordinate identity**
6. **submission: close scanner channels and validate caption stems**
7. **submission: shorten Figure 3 and resolve package/editorial defects**
8. **verification: regenerate science and record Round 12 acceptance**

Do not combine all changes into one opaque commit. Each commit should have passing tests relevant to its scope, with the final commit carrying the complete chain.

# 8. Final closure checklist

## P0 and manuscript claim

- [ ] `advantage is therefore small` removed from the generator and all generated surfaces.
- [ ] `small held-out skill`, evaluative `only`, and `well under one percentage point` removed or rewritten non-evaluatively.
- [ ] −0.394 pp and its favourable direction remain prominent.
- [ ] Symmetric non-establishment language remains explicit.
- [ ] Mechanistic-transfer boundary remains explicit.

## Claim governance

- [ ] Disclaimer scope is linked to the controlled proposition, not the rest of a heuristic clause.
- [ ] All false-negative and false-positive sentence probes classify correctly.
- [ ] Ordinary absence/equivalence/magnitude paraphrases are covered.
- [ ] Positive coverage rejects negated, quoted, conditional, reported, and metalinguistic mentions.
- [ ] Highlights carry all four required propositions.

## Inferential evidence

- [ ] Direct construction with `_VERIFIED` cannot grant permissions.
- [ ] Production permissions are reverified from canonical evidence at point of use.
- [ ] Result interval is parsed from the digest-bound result.
- [ ] Procedure semantics and implementation identity are verified.
- [ ] Empty required procedure fields are rejected.
- [ ] Practical-margin chronology is demonstrably pre-result.
- [ ] Test registries cannot reach production rendering.

## Source contract

- [ ] Raw coordinate tokens survive until exact `Decimal` identity is fixed.
- [ ] Production-path collision tests pass.
- [ ] Current source census, support, cluster IDs, manifest, and numerical results reproduce.
- [ ] `repr(float)` is no longer described as recovering the original token.

## Submission scanner and captions

- [ ] Unquoted HTML attributes, `srcset`, and `poster` are scanned.
- [ ] Percent/entity/path normalization closes encoded variants.
- [ ] Full leakage policy applies to comments in verbatim uploads.
- [ ] Only exact generator stamps are exempt.
- [ ] Metadata exemption applies only to the exact placeholder node.
- [ ] Producer stems are preserved and validated one-to-one.
- [ ] Figure 3 is within the approved caption length and carries all required facts/propositions.

## Package/editorial and final verification

- [ ] Replicate/measurement-uncertainty rerun status is resolved and evidence-bound.
- [ ] Duplicated comparator-ladder phrase is corrected in all authoritative and generated surfaces.
- [ ] Exact verification chain passes.
- [ ] Full test suite passes.
- [ ] Scientific regeneration completes and protected values remain exact or any change is separately adjudicated.
- [ ] Final continuous-argument read is recorded.

# 9. Required final acceptance record

The remediation should conclude with a Markdown acceptance report containing:

1. final commit, tree, and working-tree state;
2. finding-by-finding disposition (`closed`, `not closed`, or `reclassified`);
3. files changed for each finding;
4. exact replacement wording for P0-1;
5. adversarial probe results;
6. targeted and full test counts;
7. numerical invariant output;
8. source/corpus/manifest comparisons;
9. regeneration result and any byte/hash differences;
10. submission-scanner and caption validation output;
11. P2-3 rerun-status decision and evidence;
12. manual surface-reading conclusion; and
13. final disposition:

```text
ROUND_12_REMEDIATION_ACCEPTED__PAPER_1_SCIENCE_AND_ASSURANCE_BLOCKERS_CLOSED
```

That disposition should be used only if every P0/P1 item is closed, every applicable P2 item is resolved, all required tests and regeneration checks pass, and no outstanding conclusion-relevant analysis remains. It does **not** certify completion of the brief's explicitly out-of-scope author metadata, licensed novelty search, archival DOI/tag, or final typesetting. Overall submission readiness should be declared separately after those package items are complete.
