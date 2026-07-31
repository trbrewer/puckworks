# Paper 1 — Round 12 Detailed Review

**Review target:** `trbrewer/puckworks` commit `4adbe4af6b6a4faa6b27c38f8aaf3dde01dc8a86` (`4adbe4a`)  
**Brief:** `docs/paper1_resource/PAPER_1_REVIEW_BRIEF_ROUND_12.md`  
**Paper:** Paper 1 / Paper A only  
**Review date:** 31 July 2026  

## Disposition

**NOT READY FOR SUBMISSION.**

I find **1 P0 submission blocker, 8 P1 major findings, and 4 P2 editorial/packaging findings**. The stale-number category remains **empty**: the protected 38/40/42 g values are internally consistent across the endpoint artefact, the manuscript, Supplementary Table S3, the cover letter, Highlights, and the Figure 3 caption. The blocker is instead the same scientific-claim class that Round 12 says has been eliminated: the principal generated Results paragraph still calls the observed advantage **“small”**, a second manuscript paragraph calls it **“small held-out skill”**, and nearby narrative retains equivalent evaluative framing through **“only”** and **“well under one percentage point.”** The active claim scanner reports zero problems on all six reviewed surfaces.

The larger assurance conclusion is also adverse. This is not one missed adjective behind an otherwise sound gate. Focused probes demonstrate false-green paths in each intended layer of defence:

1. the authoritative generator itself emits the prohibited magnitude verdict;
2. the prohibitive phrase scanner misses the live wording and several ordinary paraphrases;
3. clause-scoped disclaimer suppression both hides explicit verdicts and rejects genuine non-establishment statements;
4. the positive assertion contract accepts negated, quoted, and metalinguistic mentions as if they asserted the required propositions;
5. the future inferential unlock can be fabricated from an importable token, and the evidence verifier hashes an analysis result without deriving the claimed interval from it;
6. the source “lossless identity” contract receives coordinates only after the production loader has irreversibly converted source tokens to binary floats; and
7. the submission scanner still has destination, comment, and exemption bypasses.

The manuscript’s quantitative result is not buried. The exact direction and magnitude—8.44% versus 8.83%, model-minus-comparator difference −0.394 pp, 62/132 observations worse—are prominent on all important surfaces. The required correction is therefore **not** to add caveats or further flatten the result. It is to remove unsupported practical-magnitude decisions while preserving the exact signed contrast and the symmetric evidentiary boundary.

## Review basis and limitations

### Materials reviewed

Reader-facing and package surfaces:

- `docs/submission/PAPER_A_JFE_MANUSCRIPT.md`
- `docs/PAPER_A_DRAFT.md`
- `docs/submission/PAPER_A_JFE_SUPPLEMENT.md`
- `docs/submission/PAPER_A_JFE_COVER_LETTER.md`
- `docs/submission/PAPER_A_JFE_HIGHLIGHTS.txt`
- `docs/submission/PAPER_A_JFE_FIGURE_CAPTIONS.md`
- `docs/submission/PAPER_A_JFE_PACKAGE.md`

Assurance and generation mechanisms:

- `puckworks/paper_a/claim_policy.py`
- `puckworks/paper_a/inferential_evidence.py`
- `puckworks/paper_a/source_schema.py`
- `puckworks/data/__init__.py`
- `tools/paper_a_transfer_text.py`
- `tools/paper_a_consistency.py`
- `tools/paper_a_figure_captions.py`
- the four Round-12-focused test modules named in the brief

Numerical and corpus records:

- `docs/paper1_resource/PAPER_A_ENDPOINT_PROPAGATION.json`
- `docs/paper1_resource/PAPER_A_TRANSFER_CORPUS_CONTRACTS.json`
- Table 4a and its endpoint synthesis
- Supplementary Table S3 and its reading

### Execution performed

I executed focused Python probes against the exact target modules and extracted target surfaces. The probes covered live manuscript wording, fresh claim paraphrases, clause scope, positive assertion polarity, direct construction of `VerifiedInferentialStatus`, semantic and chronological detachment of inferential evidence, coordinate-token collisions through the production float path, raw-HTML destinations, verbatim-upload comments, metadata exemptions, and caption length. The complete output is supplied separately as `PAPER_1_ROUND_12_FOCUSED_PROBES.txt`.

I did **not** independently reproduce the brief’s reported full run of `3025 passed, 1 skipped`, nor did I rerun the approximately 25-minute PDE science regeneration. A complete repository checkout and its full dependency/file tree were not available in the execution environment; attempts to collect the extracted official test modules therefore encountered missing repository fixtures and paths. This review does not certify that reported run. Its findings are based on exact-commit source inspection, publication/artefact cross-checking, and focused executable counterexamples that do not require the PDE regeneration.

## Severity summary

| ID | Severity | Finding | Submission consequence |
|---|---|---|---|
| P0-1 | P0 | The Round-12 magnitude correction is not present on the principal generated Results surface; “small” and equivalent evaluative framing remain while the scanner returns clean | Blocks submission |
| P1-1 | P1 | Clause-scoped disclaimer governance has false negatives and false positives because “same clause” is not the same as grammatical scope | Gate cannot safely distinguish disclaimer from verdict |
| P1-2 | P1 | The verdict taxonomy misses ordinary absence, equivalence, and magnitude paraphrases, including a live hyphenated construction | Central overclaim can recur by routine copy-editing |
| P1-3 | P1 | Positive assertion coverage is substring presence, not proposition presence | Negation, quotation, or instructions can satisfy the supposed omission guard |
| P1-4 | P1 | `VerifiedInferentialStatus` is forgeable through the importable `_VERIFIED` token | Future decision language can be unlocked without verification |
| P1-5 | P1 | Evidence digests do not bind the claimed interval to the hashed result or prove margin chronology; key procedure semantics may be empty | A formally verified decision can be semantically detached from its evidence |
| P1-6 | P1 | Highlights omit the mechanistic-transfer boundary even though a compliant 62-character bullet fits | Standalone editor-facing surface drops a central proposition |
| P1-7 | P1 | Production float coercion destroys the source coordinate token before the “lossless” schema sees it | Distinct valid source identities can silently collapse |
| P1-8 | P1 | Submission scanner misses unquoted/other HTML destinations, process language in verbatim comments, and unrelated leaks beside metadata placeholders | Upload-source leakage can pass the release gate |
| P2-1 | P2 | Caption validation captures but discards producer stems | A malformed producer-to-presentation mapping can satisfy the stated caption invariants |
| P2-2 | P2 | Figure 3’s standalone caption has grown into a 287-word mini-review | Caption is difficult to scan and duplicates Results/Methods material |
| P2-3 | P2* | Submission package says science reruns are complete while a conversion task still orders replicate/measurement-uncertainty reruns | Status is internally contradictory; severity escalates if the task is real |
| P2-4 | P2 | “in-sample comparator ladder” is duplicated parenthetically | Straight editorial defect |

\* Reclassify P2-3 to P1 or P0 if the named reruns are genuinely outstanding and could change the conclusions.

# Detailed findings

## P0-1 — The Round-12 magnitude correction is false on the principal claim surface

### Finding

The brief says every property-level magnitude verdict was replaced by the observed contrast plus a symmetric decision boundary, and specifically says that “less than half a percentage point” replaced “small.” That correction has not landed. The paper’s **principal generated quantitative Results paragraph** still says:

> “The observed advantage is therefore small …”

A later hand-authored in-sample paragraph says:

> “consistent with the small held-out skill above …”

The endpoint discussion also says:

> “Because this difference is only −0.394 percentage points wide …”

and:

> “the favourable extreme of these ranges lies well under one percentage point …”

The first two are direct practical-magnitude verdicts. The latter two retain the same evaluative function through “only” and “well under,” using undeclared reference points to characterize relevance. The submission manuscript and canonical draft contain the same live wording.

This is a P0 because the brief explicitly states that no science blocker remains and instructs that any discovered science blocker be reported as P0. More substantively, the statement converts an observed numerical contrast into a practical judgment even though the paper repeatedly says no practical margin was predeclared.

### Evidence

1. `tools/paper_a_transfer_text.py`, `block_transfer_headline()`, source lines approximately 528–557: the function docstring says the sentence “now says exactly” that usefulness is unestablished, but the generated string at the end says **“The observed advantage is therefore small.”**
2. `docs/submission/PAPER_A_JFE_MANUSCRIPT.md`:
   - raw line 814: the generated principal Results paragraph contains “advantage is therefore small”;
   - raw line 870: “difference is only −0.394 percentage points”;
   - raw line 903: “favourable extreme … lies well under one percentage point”;
   - raw lines 930–940: the hand-authored comparator-ladder paragraph ends “consistent with the small held-out skill above.”
3. `docs/PAPER_A_DRAFT.md` repeats the same wording at raw lines 829, 885, 918, and 953.
4. Focused execution: `claim_policy.scan(..., TRANSFER_INFERENTIAL_STATUS)` returns `[]` for both live “small” strings and returns zero problems for each of the six active surfaces.
5. The exact mechanism is visible in `claim_policy.py`:
   - the copular pattern allows `advantage is [only/very] small` but not an intervening adverb such as `therefore`;
   - the pre-nominal pattern permits `\w+` modifiers, so the hyphenated modifier in “small held-out skill” does not match;
   - numerical evaluators such as “only −0.394” and “well under one” are outside the keyword grammar.

### Assessment of the brief’s specific questions

**Has magnitude language been fixed or relocated?** Not fixed. It remains explicitly as “small” and is also relocated into “only” and “well under.”

**Does “less than half a percentage point” itself smuggle in relevance?** It is a checkable inequality, unlike “small,” and when immediately accompanied by the exact −0.394 pp value and the symmetric boundary it is not independently a false scientific claim. It is nevertheless a rhetorically selected threshold with no declared practical meaning and adds little beyond the exact number. I would remove it from the highest-stakes claim surfaces rather than rely on a distinction readers may not preserve. It is not the main blocker; the live “small” wording is.

**Has the result been buried by caveats?** No. The signed point estimate is prominent in the abstract, significance statement, headline Results paragraph, endpoint table, cover letter, Highlights, and Figure 3 caption. The correction should preserve that prominence.

**Is the generated/authored boundary sensible?** No. The principal generated block itself is wrong, and a nearby hand-authored paragraph reintroduces the same verdict. Generation has not made the claim safe, and the policy has not governed the ungenerated bridge paragraph.

### Minimum acceptance criterion

All of the following are required:

1. Replace the generated headline sentence in `block_transfer_headline()` and regenerate **both** manuscripts. A defensible formulation is:

   > “The observed difference is −0.394 percentage points, favouring the mechanistic model. Because the reported ranges are uncalibrated and no practical margin was predeclared, this analysis does not establish that the observed advantage is reproducible or practically useful, and it does not establish that the advantage is absent. Acceptable endpoint accuracy does not by itself establish transfer of the kinetic mechanism beyond a transferred concentration level.”

2. Replace “consistent with the small held-out skill above” with a non-decisional link, for example:

   > “This descriptive in-sample comparison is not a held-out test and does not adjudicate the magnitude, reproducibility, or practical usefulness of the held-out difference.”

3. Remove the evaluative adverbs in “only −0.394” and “well under one percentage point.” State the exact values and their direction without assigning them to an undeclared relevance bin.
4. Add verbatim regression tests for the four live constructions above, including `therefore`, a hyphenated modifier, `only <number>`, and `well under <threshold>`.
5. Run the prohibitive scanner against generated block output **before** insertion, and against the fully rendered manuscript after insertion. A generator is a source of text, not evidence that the text is scientifically permissible.
6. Add a release assertion that the exact sentences removed by this finding are absent from every Paper 1 submission surface.

---

## P1-1 — Clause governance does not model grammatical scope

### Finding

The rewritten disclaimer governor suppresses any prohibited match that occurs after a safe construction within the same heuristic clause. That is not sufficient to determine whether the safe construction actually governs the verdict. Opening concessive clauses, causal continuations, result/appositive continuations, and comma splices all allow an explicit verdict to inherit a disclaimer it does not grammatically belong to. Conversely, ordinary embedded-question disclaimers are rejected because their wording is not in the fixed safe-construction list.

### Evidence

The following explicit verdicts return no problems:

- “Although this analysis does not establish superiority, the model outperforms the comparator.”
- “While this analysis does not establish superiority, the model outperforms the comparator.”
- “Whereas this analysis does not establish equivalence, the models are essentially the same.”
- “This analysis does not establish superiority because the model outperforms the comparator.”
- “This analysis cannot determine equivalence, meaning the models are essentially the same.”
- “We do not claim equivalence in formal terms, the models are essentially the same in practice.”

The following genuine non-establishment statements are incorrectly flagged:

- “Whether the model outperforms the comparator remains unresolved.”
- “The data are insufficient to determine whether the model outperforms the comparator.”
- “It remains unclear whether the model outperforms the comparator.”
- “The analysis leaves unresolved whether the model outperforms the comparator.”
- “The data do not permit us to conclude that the model outperforms the comparator.”

In `claim_policy.py`, `_CLAUSE_BOUNDARY` is a deterministic delimiter expression, and `find_non_establishment_spans()` gives every recognized safe construction scope from its start to the **end of the whole heuristic clause**. That is precisely why a fronted disclaimer reaches through a comma to a later main-clause verdict.

### Impact

Routine scientific prose can either evade the gate or be rejected despite saying exactly what the policy requires. This encourages authors to write to the scanner rather than to meaning and leaves explicit overclaim one copy-edit away from release.

### Minimum acceptance criterion

1. Replace whole-clause suppression with proposition-linked suppression: a match is safe only when it is inside the grammatical/controlled complement of a recognized non-establishment construction, not merely later in the same clause string.
2. At minimum, recognize embedded `whether`/`if` questions and ordinary epistemic frames such as “remains unclear,” “insufficient to determine,” “leaves unresolved,” and “does not permit us to conclude.”
3. Opening concessive/subordinate clauses must not license a later independent-clause verdict.
4. The exact examples above must be pinned with expected outcomes.
5. Do not resolve this solely by adding more boundary words. The defect is scope, not delimiter coverage.

---

## P1-2 — The verdict taxonomy misses ordinary paraphrases and a live hyphenated construction

### Finding

The brief correctly acknowledges that a finite phrase list is incomplete, but the remaining misses are not confined to an obscure idiom. Ordinary scientific/editorial paraphrases of absence, equivalence, and practical insignificance pass clean. One miss is already live in the manuscript: “small held-out skill.”

### Evidence

The focused scanner returns no problem for:

- “The model has no advantage.”
- “There is no advantage.”
- “The model shows no advantage.”
- “The model is no better than the comparator.”
- “The comparator is just as accurate.”
- “The observed gain is minuscule.”
- “The difference is negligible.”
- “The model has a tiny held-out advantage.”
- “consistent with the small held-out skill above.”

These are not exotic edge cases. They are natural editorial substitutions for the exact claim classes the policy exists to control.

### Impact

The phrase list is still doing more load-bearing work than the brief says it should. That would be tolerable only if the positive assertion contract and generated text were semantically strong. P1-3 and P0-1 show that neither fallback currently provides that protection.

### Minimum acceptance criterion

1. Add coverage for the ordinary structures above, including:
   - `no + value noun` and `has/shows/provides no + value noun`;
   - `no better than` / `just as accurate` equivalence formulations;
   - copular magnitude judgments on `difference`, `effect`, `increment`, and `contrast`, not only `skill/gain/benefit/advantage/improvement`;
   - hyphenated modifiers between adjective and head noun.
2. Add morphology/synonym cases such as `minuscule` rather than assuming the current adjective list is representative.
3. Treat the prohibitive scanner as defence-in-depth. For central surfaces, render from a typed claim object or tightly controlled templates and verify the rendered propositions, rather than relying on a negative keyword census.
4. Add mutation tests that perform realistic copy-edits—adverb insertion, hyphenation, head-noun substitution, active/passive voice—and require the policy outcome to remain stable.

---

## P1-3 — Positive assertion coverage tests strings, not propositions

### Finding

`Assertion.present_in()` flattens and lowercases text, then asks whether any accepted phrase is a substring. It does not inspect polarity, quotation, reported speech, or whether the phrase is merely an instruction about what should later be written. Consequently, a surface can explicitly deny the required result, quote the required wording as rejected language, or mention it metalinguistically and still be certified as carrying every required proposition.

### Evidence

`claim_policy.py`, raw lines 486–580:

```python
def present_in(self, text: str) -> bool:
    flat = _flatten(text).lower()
    return any(_flatten(p).lower() in flat for p in self.any_of)
```

Focused counterexamples:

- A Highlights file saying “Observed pooled error was **not** 0.394 points lower,” “These are **not** uncalibrated ranges,” and “The phrase ‘support no superiority’ is **not** this paper’s conclusion” returns `missing=[]` and `scan=[]`.
- A Figure 3 caption saying it **must include** the quoted strings “−0.394 pp,” “uncalibrated ranges,” “does not establish whether,” and “alone does not establish” returns `missing=[]` and `scan=[]`.
- An abstract that negates the observed point estimate, negates the range characterization, and mentions the decision/transfer phrases only inside negative/metalinguistic constructions also returns `missing=[]` and `scan=[]`.

### Impact

The positive half of the claim policy cannot establish that a required scientific proposition is present. It establishes only that selected character sequences occur. This is the same class of false assurance the brief asks reviewers to test: a mechanism describes more than it does.

### Minimum acceptance criterion

1. Replace free-substring proposition detection on central surfaces with one of these defensible models:
   - render each surface from structured claim data and compare the rendered typed fields to the artefact; or
   - parse a narrow, controlled template grammar that records assertion polarity and role.
2. Quoted, negated, hypothetical, conditional, reported, and metalinguistic mentions must not satisfy a positive proposition.
3. Keep quotation non-exempt for the **prohibitive** scanner if the repository wishes to prevent dangerous wording from reaching readers, but make the **positive** checker quotation- and polarity-aware. The two jobs have opposite requirements.
4. Add the three exact counterexamples above, plus conditional forms (“if the difference were −0.394 pp”) and reported speech (“the reviewer called it −0.394 pp”), as failing positive-coverage fixtures.

---

## P1-4 — `VerifiedInferentialStatus` is still typed rather than earned

### Finding

The new type is described as unforgeable because it requires a module-private token. In Python, the token is an ordinary module attribute. Importing `puckworks.paper_a.inferential_evidence` exposes `inferential_evidence._VERIFIED`, which can be passed directly to the public dataclass constructor. `claim_policy.granted()` then trusts the resulting object solely because it is an instance of `VerifiedInferentialStatus`.

### Evidence

`inferential_evidence.py` states that only `verify_inferential_evidence()` has the token and that direct construction is impossible. The actual constructor checks identity against `_VERIFIED`; it does not prevent callers from importing that object. `claim_policy.granted()` performs an `isinstance` test and reads the forged object’s derived flags.

The focused probe directly constructs a synthetic equivalence status with `_token=IE._VERIFIED`. The result:

- is a `VerifiedInferentialStatus`;
- derives `equivalence=True`;
- causes `granted()` to return `equivalence`, `calibrated coverage`, and `a predeclared practical margin`; and
- allows “The model is equivalent to the comparator” to pass the claim scanner.

No verification function ran.

### Impact

The trusted boolean has moved again: from a stored decision flag to possession of an importable sentinel plus caller-selected evidence/procedure objects. The current Paper A registry is empty and the current analysis requests no decision, so this does not alter today’s manuscript. It does make the advertised future unlock unsafe and invalidates the “unforgeable” assurance claim.

### Minimum acceptance criterion

1. A directly constructed object, including one supplied with the module sentinel, must never unlock decision language.
2. `claim_policy.granted()` should consume an authoritative verification result whose evidence is reverified against canonical artefacts and the production registry at the point of use; it must not trust Python type identity as proof of provenance.
3. Remove or narrow the word “unforgeable.” In-process Python objects cannot provide a security boundary against code that can import the module.
4. Separate test injection from production: synthetic registries and caller-supplied verification inputs must be available only through an explicit test seam that production rendering cannot invoke.
5. Add an acceptance test that imports `_VERIFIED`, constructs the dataclass directly, and proves `granted()` returns the empty set or raises a verification error.

---

## P1-5 — The evidence chain hashes artefacts without binding the claimed semantics or chronology

### Finding

The verifier checks that a caller-supplied digest for `analysis_result` matches the digest recorded in `EvidenceRecord`, but it never parses the hashed result and never derives `observed_interval_pp` from it. The interval used to make the decision is a separate, caller-written field in the evidence record. Likewise, a practical-margin protocol is proven only to be a different hashed artefact; no mechanism proves it existed before the result. Registration also accepts an empty `cluster_unit` and empty `implementation_id`.

### Evidence

A focused synthetic procedure was registered with `cluster_unit=''` and `implementation_id=''`; `ProcedureSpec.problems()` returned no problems.

The probe then supplied:

- an actual hashed analysis result whose interval was `[-2.0, 2.0]`, which does **not** support equivalence under the synthetic margin;
- a separately written evidence interval of `(-0.30, 0.20)`, which does support equivalence;
- a practical-margin protocol object explicitly marked `created_after_result=True`; and
- matching hashes for both artefacts.

`verify_inferential_evidence()` returned no problems and produced a verified equivalence decision. This is possible because:

- `analysis_result_sha256` is compared only as an opaque digest;
- `observed_interval_pp` is trusted from the evidence record;
- the protocol digest proves identity, not temporal ordering; and
- `implementation_id` is recorded but not validated or tied to executable code.

### Impact

The chain can truthfully say “this decision references this result hash” while deriving the decision from a different interval. It can truthfully say “the margin references a separate protocol hash” while the protocol was written after the result. Those are the exact semantic properties the mechanism claims to provide.

### Minimum acceptance criterion

1. Define a canonical result schema and derive `observed_interval_pp`, confidence level, estimand ID, procedure ID/version, and relevant fitting/refit metadata directly from the parsed **hashed analysis result**. Remove duplicated decisive values from `EvidenceRecord`, or require exact equality to values parsed from the result.
2. Bind `implementation_id` to an immutable code identity—at minimum a commit/tree plus callable/module identifier or a digest of the registered implementation—and verify it.
3. Reject empty `cluster_unit`, `required_estimand_id`, and `implementation_id` at registration.
4. Make predeclaration an actual ordering property. Acceptable evidence could be commit ancestry, a signed/archived timestamp, or an immutable protocol artefact demonstrably preceding the result commit. Merely being a different file/hash is insufficient.
5. The production verifier must use the authoritative production registry; arbitrary caller-supplied registries must not be able to unlock production prose.
6. Add the exact detached-result and post-result-protocol probes as negative tests.

---

## P1-6 — The Highlights omission is not forced by the 85-character limit

### Finding

The Highlights surface is required to carry only three of the four central propositions. `accuracy_is_insufficient`—the boundary that endpoint accuracy alone does not establish mechanistic transfer—is intentionally omitted on the stated ground that an 85-character bullet cannot fit it. That premise is false.

### Evidence

Current fifth Highlight:

> “Accurate prediction did not guarantee well-determined model parameters” — 70 characters.

A direct replacement:

> “Endpoint accuracy alone did not establish mechanistic transfer” — 62 characters.

An alternative:

> “Accurate endpoint prediction did not establish mechanistic transfer” — 67 characters.

Both fit comfortably. The current fifth bullet is also partially redundant with the first and fourth bullets, which already communicate weak parameter separation and stronger rate constraint from time-resolved samples.

### Impact

Highlights are uploaded and read independently. Bullet 2 reports the favourable −0.394-point contrast and bullet 3 supplies the inferential non-decision, but the paper’s central distinction between endpoint prediction and mechanistic transfer is absent. That is the same omission class the positive contract was introduced to prevent.

### Minimum acceptance criterion

1. Add `accuracy_is_insufficient` to the `highlights` assignment in `SURFACE_ASSERTIONS`.
2. Replace the current fifth bullet with one of the compliant 62/67-character formulations above, or supply another formulation under the venue limit.
3. Add a per-bullet character-count test and a positive-coverage test proving all four propositions are carried by the standalone file as a whole.

---

## P1-7 — “Lossless” coordinate identity is impossible after the production loader’s float conversion

### Finding

`source_schema.py` correctly states that coordinates are identities and that binary floating point is the wrong representation. It then says production’s already-coerced float can be converted through `repr()` “to recover [the source token] exactly.” That is impossible once two distinct decimal source tokens map to the same binary float.

### Evidence

Production’s `_typed_rows()` and `_typed_rows_hashskip()` call `float(v)` on every parseable cell before `source_schema.parse_coordinate()` sees it. The focused probe shows:

- `93.4000400000000001` and `93.4000400000000002` are distinct source tokens but become the same float, both `repr` as `93.40004`, and produce the same canonical coordinate;
- `10.0000000000000001` and `10.0000000000000002` are distinct tokens but become the same float, both `repr` as `10.0`, and produce the same canonical coordinate `10`.

The current Angeloni coordinate values are simple enough that the committed corpus is unchanged; this is not a stale-number finding. It is a false assurance property and a latent identity/census defect.

### Impact

A future source row can be structurally valid yet silently merge with a different condition before cluster IDs, support, census, or lookup reconciliation are computed. The shared schema cannot repair information already destroyed by the shared loader.

### Minimum acceptance criterion

1. Preserve raw CSV tokens for identity columns through production. A suitable interface is `(raw_token, typed_value)` or a loader mode/schema hook that leaves declared identity fields as strings/`Decimal`.
2. Derive canonical identity only from the raw token. Numeric arrays for computation may be derived separately after identity is fixed.
3. Add an end-to-end temporary-CSV test through the **production loader**, not merely a direct call to `parse_coordinate()`, containing two distinct high-precision tokens. It must either preserve distinct identities or fail explicitly before coercion.
4. Correct the docstring: `repr(float)` recovers the round-trippable float value, not the original decimal token.

### Clean judgments on the rest of the source-contract questions

- Rejecting leading/trailing whitespace is defensible for a controlled transcription and correctly fails closed.
- Raising when derived lookup support and declared `on_grid` disagree is preferable to silently choosing one side.
- Distinguishing “an optimal-grind record exists here” from “this row is in the 18-condition calibration grid” is coherent and useful.
- The Methods limitation—that structure/tokens/support are checked but transcription, units, and plausibility against the source article are not—is appropriately candid.

---

## P1-8 — The structural submission scanner still has three independent leakage channels

### Finding

The scanner’s move to CommonMark parsing is sound, and failing closed when `markdown-it-py` is absent is the right choice. Three bypass classes remain.

### A. Raw HTML destinations

`_HTML_TARGET` recognizes only **quoted** `href` and `src`. It misses unquoted attributes and other URL-bearing attributes. Focused examples that yield no target include:

- `<a href=docs/internal/review.md>…</a>`
- `<img src=docs/internal/figure.png alt="figure">`
- `<a href=docs%2Finternal%2Freview.md>…</a>`
- `<img srcset="docs/internal/figure.png 1x" …>`
- `<video poster="docs/internal/review.png"></video>`

The same path in a quoted `href` is found, confirming this is an extraction gap rather than a path-rule gap.

### B. Process language in comments of verbatim uploads

The comment channel for the Highlights and standalone captions applies **only** the internal-path regular expression. It does not apply review-history, internal-narration, or producer-identifier rules. These comments therefore pass:

- `<!-- The second review retained a producer identifier. -->`
- `<!-- generated from a private producer identifier -->`

Those files are explicitly uploaded as-is, so the source reaches the editor even though the text is not rendered.

### C. Metadata exemption is wider than the placeholder

Visible-text exemption is assigned to the entire parsed paragraph whenever it contains “not yet supplied” or a related phrase. Destination exemption is assigned to every target on the same source line. Therefore these pass:

- `Funding is not yet supplied. See docs/internal/review.md for the scientific analysis.`
- `Funding is not yet supplied. See [the scientific analysis](docs/internal/review.md).`

The implementation is paragraph-/line-scoped even though the comments describe a structural exemption keyed narrowly to the placeholder.

### Impact

All three channels can place repository process material or internal paths in an upload deliverable while `paper_a_consistency.py` reports clean. They are independent enough that fixing one will not close the others.

### Minimum acceptance criterion

1. Parse raw HTML with an HTML tokenizer/parser and extract quoted and unquoted URL attributes. Scan at least `href`, `src`, all candidates in `srcset`, and `poster`; include any other URL-bearing attributes permitted in the accepted submission syntax.
2. Apply all leakage classes to comments in files uploaded verbatim. Exempt only an exact, machine-validated generator-stamp grammar—not an entire rule class.
3. Scope unsupplied-metadata exemption to the precise placeholder node/span and, if needed, one exact approved tracking reference. Unrelated prose or link targets in the same paragraph/line must still be scanned.
4. Add the exact bypasses above as tests on every applicable upload file.
5. Retain the hard dependency/fail-closed behavior for structural parsing. A scanner that cannot parse must remain a blocker, not a skip.

---

## P2-1 — Caption validation discards the producer stem it claims to map

### Finding

The caption heading regex captures both the presentation number and the producer stem—`### Figure N (`stem`)`—but `captions()` retains only `(number, caption_text)`. `caption_set_problems()` then validates number completeness, duplication, labels, and structural delimiters. It cannot detect a duplicated, swapped, missing, or unexpected producer stem.

### Evidence

- `_HEADING` captures groups `(number, stem)`.
- `captions()` reads `match.group(1)` only and appends `(number, paragraph)`.
- `caption_set_problems()` receives no stem and therefore cannot validate the one-to-one producer-to-presentation mapping.

The Round-12 delimiter correction is otherwise sound: validity is now separate from freshness, and a caption body containing a heading/horizontal-rule delimiter is rejected.

### Impact

The upload caption text can remain fresh and structurally valid while the repository’s bookkeeping points the presentation figure to the wrong producer. No current mismatch was found; this is a gap in the claimed mapping invariant.

### Minimum acceptance criterion

1. Preserve `(number, stem, caption)` through extraction.
2. Compare against an authoritative expected mapping and require stems to be unique, complete, and known.
3. Add duplicate-stem, swapped-stem, missing-stem, and unknown-stem mutations that fail independently of upload-file freshness.

---

## P2-2 — Figure 3’s caption is a 287-word mini-review

### Finding

The standalone Figure 3 caption is 2,092 characters, approximately 287 words, and 12 sentence-ending units. For comparison, Figure 4 is approximately 155 words. Figure 3 currently carries calibration design, panel semantics, comparator definition, full corpus census, off-grid status, point estimate, win/loss count, matched-grid subset, lookup support, near-optimal-rate propagation, interval semantics, all four decision classes, the symmetric boundary, the transfer lesson, and evidence tier.

### Impact

The caption is accurate and self-contained, but it is no longer functioning primarily as a caption. It duplicates Results and Methods material, obscures the panel-reading instructions, and will be difficult to typeset and scan.

### Minimum acceptance criterion

Reduce Figure 3 to roughly 150–200 words while retaining:

- what was fitted and held out;
- what the panels show;
- the level-only comparator definition;
- complete corpus size and off-grid inclusion;
- 8.44% versus 8.83%, −0.394 pp favouring the model, and 62/132 worse;
- the fact that ranges are uncalibrated sensitivities and make no decision; and
- the mechanistic-transfer boundary.

Move detailed matched-grid/lookup support and near-optimal-rate-envelope mechanics to the main text or supplement unless visually necessary for interpreting the figure.

A workable condensed direction is:

> **Figure 3. Within-campaign cross-grind prediction after target-specific calibration.** For each variety–solute group, inventory and rate were fitted to nine optimal-grind conditions and frozen for coarse/fine prediction at 40 g. Panels show the complete held-out corpus (44 records × 3 solutes = 132 observations, including 8 off-grid records) and summarize error by target grind. The comparator is an optimal-grind-trained level-only constant with no process or kinetic response. Pooled MAPE was 8.44% for the mechanistic model and 8.83% for the constant, a model-minus-comparator difference of −0.394 pp favouring the mechanistic model; it had the larger absolute error on 62/132 observations. The 108-observation matched-grid subset is secondary and supplies the lookup comparator. Clustered ranges are fixed-predictor sensitivities, not calibrated confidence intervals; with no predeclared practical margin, they establish neither a comparator decision nor its absence. Endpoint accuracy alone does not establish mechanistic transfer.

---

## P2-3 — The package contradicts itself about outstanding science reruns

### Finding

At the top, `PAPER_A_JFE_PACKAGE.md` says the objective-family sweep and bounded refit bootstrap are complete, says previous weighted-uncertainty rerun wording was obsolete, and states that what “genuinely remains” is metadata, novelty search, DOI, and typesetting. Under “Conversion edits before upload,” item 2 still says:

> “Complete replicate/measurement-uncertainty sensitivity reruns; update figures, bundle values, abstract, and discussion only if conclusions change.”

### Impact

A packager cannot tell whether this is stale process language or an unperformed analysis that can alter the figures and conclusion. The top-level declaration and task list cannot both be authoritative.

### Minimum acceptance criterion

1. Decide whether item 2 names work already completed or a distinct outstanding analysis.
2. If complete, remove the task and bind the completion claim to the relevant artefact/gate.
3. If distinct and outstanding, add it to the authoritative submission-readiness list and complete it before submission.
4. If its result could change the abstract/discussion, reclassify this finding to at least P1; if it can change the central conclusion, treat it as P0.

---

## P2-4 — Duplicated comparator-ladder phrase

### Finding

The manuscript says:

> “An **in-sample comparator ladder** (in-sample comparator ladder) makes its adequacy auditable.”

The parenthetical repeats the immediately preceding phrase and provides no definition.

### Minimum acceptance criterion

Delete the parenthetical, or replace it with an informative explanation such as “(one-constant, per-grind constant, shared mechanistic, and per-grind mechanistic).” Apply the same correction to the canonical draft.

# Numerical cross-check — stale-number category empty

I compared the manuscript’s Table 4a and narrative against `PAPER_A_ENDPOINT_PROPAGATION.json` at the reviewed commit, including the full-precision primary `cond_in_variety` ranges. No stale numerical publication value was found.

| Endpoint | Model pooled MAPE | Comparator pooled MAPE | Difference, model − comparator | Full-precision primary range | Published rounded range | Zero relation | Model worse on |
|---:|---:|---:|---:|---|---|---|---:|
| 38 g | 8.39% | 8.83% | −0.447 pp | [−0.8843868833, −0.0424325436] | [−0.884, −0.042] | excludes zero, negative side | 61/132 |
| 40 g | 8.44% | 8.83% | −0.394 pp | [−0.8290522506, +0.0037905184] | [−0.829, +0.004] | contains zero | 62/132 |
| 42 g | 8.41% | 8.83% | −0.425 pp | [−0.8912505494, +0.0058444686] | [−0.891, +0.006] | contains zero | 60/132 |

The complete-corpus record also consistently declares 44 held-out records, 3 solutes, 132 observations, 8 off-grid records, and a 108-observation matched-grid/lookup-support subset. The distinction between the complete headline corpus and the matched-grid secondary support is consistently represented on the reviewed surfaces.

# Brief-by-brief audit

## (a) Corrected claim as one continuous argument

**Not clean.** P0-1 applies.

- The point estimate and its favourable sign are not buried; no over-correction finding.
- The symmetric “does not establish advantage / does not establish absence” boundary is generally strong in the abstract, cover letter, Table 4a reading, supplement, conclusion, and Figure 3 caption.
- The principal generated Results paragraph and one hand-authored bridge paragraph break that boundary by assigning practical magnitude.
- “Less than half a percentage point” is checkable but rhetorically unnecessary; “small,” “only,” and “well under” are clearer violations.
- The generated/authored boundary is not reliable because both sides contain the defect.

## (b) Claim policy

**Not clean.** P1-1, P1-2, P1-3, and P1-6 apply.

- Clause splitting is not a safe substitute for grammatical scope.
- The taxonomy misses routine paraphrases, not only the intentionally documented idiom.
- The fixed safe-construction list creates false positives for ordinary non-establishment prose.
- Keeping quotations non-exempt in the prohibitive scanner is defensible; treating quoted phrases as positive assertions is not.
- The positive assertion assignments are incomplete for Highlights, and their implementation is lexical rather than propositional.

## (c) Evidence-bound inferential status

**Not clean.** P1-4 and P1-5 apply.

- The current empty production registry is honest and fail-closed for Paper A; I do not treat emptiness alone as a defect.
- The unlock mechanism is nevertheless not earned: the construction token is importable, the decisive interval is not derived from the hashed result, and predeclaration chronology is not proven.
- The current fixed-predictor Paper A status remains descriptive; I found no evidence that the present manuscript is actually being unlocked as calibrated inferential prose.

## (d) Source contract

**Not clean because of P1-7; otherwise the requested design choices are defensible.**

- One shared declarative schema for row meaning is reasonable while census/membership calculations remain independently implemented.
- Whitespace rejection is appropriately fail-closed.
- Raising on `lookup_defined`/`on_grid` mismatch is preferable to overwriting.
- The all-valid-O-support versus 18-on-grid-training distinction is correctly drawn.
- The stated limitation on transcription/units/plausibility verification is clear.
- The fifth common mode is upstream loss of the raw coordinate token in production.

## (e) Submission scanner and caption set

**Not clean.** P1-8, P2-1, and P2-2 apply.

- A hard parser dependency with a blocking not-run path is the right design.
- Raw HTML targets, verbatim comments, and metadata exemptions still provide leakage paths.
- Package/canonical-draft file exemptions are principled because those files are not upload science surfaces; the implemented metadata exemption is broader than its stated rationale.
- Caption validity is now genuinely separate from freshness, which is a meaningful correction.
- Producer-stem identity is not part of the retained caption representation.
- Figure 3 is accurate but too long for an effective standalone caption.

## (f) Other findings

P2-3 and P2-4 apply. No additional stale-number, reference-number, corpus-census, endpoint-unit, or figure-count defect was found in the inspected material.

Supplementary Table S7’s appearance at final journal width was **not assessed**, because no final typeset/journal-width rendering was available in the reviewed artefacts.

# Recommended remediation order

1. **Correct P0-1 first** in the generator, both manuscripts, and all derived surfaces; add exact live-sentence tests.
2. Redesign claim-policy scope and positive coverage together. Patching the adjective regex alone will reproduce the prior cycle.
3. Make inferential verification derive semantics from canonical hashed artefacts and remove Python type identity as the trust boundary.
4. Preserve raw source identity before any float coercion.
5. Close the three scanner channels with structural parsing and exact-span exemptions.
6. Add the missing Highlights proposition and producer-stem mapping checks.
7. Resolve package status, shorten Figure 3, and clean the duplicated phrase.
8. Only after those changes, run the exact chain in the brief, the full suite, and the PDE regeneration/check as applicable. The acceptance record should include the focused adversarial probes from this review, not only the repository’s existing fixtures.

# Explicit exclusions respected

I did not re-report the six known open items listed in §6 of the brief: the unrun fraction-versus-measured-cup contrast, the 11/104 unbound slow-lane values, the approximately 255 hand-sourced design settings, the internal `skill_vs_const` name, the separate repository/site “adds little skill” copy, or the unused `re` import. I also did not report missing author/declaration metadata, licensed search, DOI/tag, working-draft repository note, or internal figure-map content as submission findings.

# Acceptance disposition

**ROUND_12_REVIEW_COMPLETE__PAPER_1_NOT_SUBMISSION_READY**

A defensible acceptance state requires, at minimum:

- P0-1 removed from generator, manuscript, and canonical draft;
- no live or fresh paraphrase counterexample in the supplied probe set returns a false green;
- positive assertion coverage rejects negated/quoted/metalinguistic mentions;
- inferential decisions are derived from the contents of the hashed result and a demonstrably pre-result protocol;
- raw coordinate identity survives the production loader;
- the three submission-scanner bypass classes are closed; and
- the exact-commit full verification chain passes after regeneration.
