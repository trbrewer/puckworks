# Paper 1 — Detailed Review, Round 11

**Review date:** 30 July 2026  
**Repository:** `trbrewer/puckworks`  
**Reviewed commit:** `baf6ef1e794ea2719e9036353d4d0b027a35accb`  
**Controlling brief:** [`PAPER_1_REVIEW_BRIEF_ROUND_11.md`](https://github.com/trbrewer/puckworks/blob/baf6ef1e794ea2719e9036353d4d0b027a35accb/docs/paper1_resource/PAPER_1_REVIEW_BRIEF_ROUND_11.md)  
**Primary manuscript:** [`docs/submission/PAPER_A_JFE_MANUSCRIPT.md`](https://github.com/trbrewer/puckworks/blob/baf6ef1e794ea2719e9036353d4d0b027a35accb/docs/submission/PAPER_A_JFE_MANUSCRIPT.md)  
**Canonical draft:** [`docs/PAPER_A_DRAFT.md`](https://github.com/trbrewer/puckworks/blob/baf6ef1e794ea2719e9036353d4d0b027a35accb/docs/PAPER_A_DRAFT.md)

---

## 1. Disposition

**NOT SUBMISSION-READY at the reviewed commit.**

I find:

- **1 P0 submission blocker**;
- **6 P1 major findings**; and
- **1 P2 editorial finding**.

The central numerical chain is internally consistent. **There is no stale-number finding.** The blocker is instead a recurrence of the exact scientific-claim class that Round 10 was intended to remove: reader-facing manuscript prose again states, as a property of the model or comparison, that the mechanism is “adding little,” that its “incremental skill … is small,” and that comparator performance “nearly matched” it. Those statements go beyond the declared analysis, which has no calibrated coverage and no predeclared practical margin.

The strongest assurance finding is that the current claim scanner returns a clean result on both manuscripts despite those sentences. It also admits direct contradictory verdicts whenever a generic disclaimer token appears within the preceding 140 characters. The new assurance architecture is materially better than the prior one, but several components still certify their own assumptions or their own generated defects.

### Finding matrix

| ID | Severity | Finding | Immediate consequence |
|---|---|---|---|
| P0-1 | P0 | Unsupported “adds little / incremental skill is small / nearly matched” conclusions remain in both manuscripts | The submitted argument still makes a practical/absence/equivalence-adjacent decision the declared analysis cannot make |
| P1-1 | P1 | Claim-policy disclaimer suppression and decision taxonomy produce reproducible false greens | Contradictory verdicts and the current P0 language pass the policy scan |
| P1-2 | P1 | `InferentialStatus` is internally coherent self-attestation, not independently verified inferential evidence | A fabricated status can unlock equivalence or other decision prose without proof that the procedure ran or earned the decision |
| P1-3 | P1 | Positive claim coverage omits the highlights and Figure 3 caption | Two upload-facing, standalone surfaces can lose the evidence limits without failing coverage |
| P1-4 | P1 | Source-to-observation independence stops above several shared, unverified premises | Malformed or scientifically wrong condition/support metadata can pass both sides of the chain |
| P1-5 | P1 | Interval validation raises on very large valid JSON integers despite its “never raises” contract | A malformed artefact can crash the gate instead of being rejected with a named problem |
| P1-6 | P1 | The publication scanner does not actually normalize rendered Markdown/HTML, discards link targets, and under-scopes internal-path checks | Review history and internal paths can be inserted into upload-facing files without detection |
| P2-1 | P2 | Figure 4’s generated caption absorbs the supplementary-section delimiter | The current upload-ready caption file is malformed while all freshness/parity checks remain green |

---

## 2. Scope, method, and limitations

### 2.1 Scope followed

This review is confined to Paper 1 and the exact Round 11 commit. I reviewed the manuscript, canonical draft, supplement, cover letter, highlights, upload-ready captions, internal caption map, claim policy, inferential-status and interval semantics, source/corpus contract, independent source oracle, estimand/design contract, consistency scanner, and caption generator.

I did **not** re-report the brief’s known open items: the unrun fraction-versus-measured-cup contrast, the 11 unbound slow-lane values, the hand-sourced design settings, the producer-internal `skill_vs_const` name, or repository/product copy outside the Paper 1 submission surfaces. I also treated unsupplied authorship/front-matter metadata, the novelty search, DOI/tag, and the deliberately internal figure map as out of scope in accordance with the brief.

### 2.2 Review method

I used four complementary checks:

1. **Continuous-argument reading.** I read the title, abstract, principal significance/result surfaces, Methods description of the ranges, Table 4a, endpoint synthesis, Supplementary Table S3 and its reading, Discussion, Conclusions, cover letter, highlights, and captions as one argument.
2. **Exact numerical reconciliation.** I compared the protected 38/40/42 g values in the Round 11 brief against the manuscript, supplement, Figure 3 caption, abstract, and cover letter.
3. **Contract/code inspection.** I traced the inferential status, prohibited-claim rules, positive surface assertions, source-to-corpus construction, estimand direction derivation, interval reconstruction, paragraph scanner, and caption generator.
4. **Targeted adversarial mutations.** I executed module-level mutations against the exact-commit code to test the specific bypasses invited by the brief: nearby disclaimers, missing decision-language classes, fabricated statuses, Markdown/HTML splitting, hidden link targets, malformed source metadata, default-`g` coordinate collisions, and oversized integers.

### 2.3 Limitations

I did not rerun the repository’s complete approximately 15-minute test suite or the approximately 25-minute PDE/science producer. I treated the repository’s recorded green baseline as the starting state and tested whether targeted mutations could remain green. The findings below therefore do **not** claim that the full suite currently reports failures; several findings are precisely that the current suite or checker can report success for a scientifically or editorially wrong state.

---

## 3. Detailed findings

## P0-1 — The manuscript still concludes that the model adds little, has small incremental skill, or is nearly matched

### Finding

The Round 10 accepted claim explicitly requires the paper to report the observed difference and its sign, describe the ranges as uncalibrated sensitivity ranges, make no superiority/equivalence/absence decision, and state that endpoint accuracy alone is insufficient to establish mechanism transfer. The same acceptance report says the claim that cross-grind prediction “adds little” was retired from every reader-facing surface.

Nevertheless, the exact Round 11 submission manuscript contains all of the following:

- §1.3: “**while adding little to a baseline that carries no mechanism at all**” ([manuscript line 165](https://github.com/trbrewer/puckworks/blob/baf6ef1e794ea2719e9036353d4d0b027a35accb/docs/submission/PAPER_A_JFE_MANUSCRIPT.md#L165));
- §4 robustness synthesis: “**its incremental skill over a level-only comparator is small**” ([line 1005](https://github.com/trbrewer/puckworks/blob/baf6ef1e794ea2719e9036353d4d0b027a35accb/docs/submission/PAPER_A_JFE_MANUSCRIPT.md#L1005));
- §6: “**incremental skill over a level-only comparator is small**” ([line 1147](https://github.com/trbrewer/puckworks/blob/baf6ef1e794ea2719e9036353d4d0b027a35accb/docs/submission/PAPER_A_JFE_MANUSCRIPT.md#L1147));
- §6 strength-ladder conclusion: “**incremental skill over a level-only baseline is small**” ([line 1167](https://github.com/trbrewer/puckworks/blob/baf6ef1e794ea2719e9036353d4d0b027a35accb/docs/submission/PAPER_A_JFE_MANUSCRIPT.md#L1167)); and
- §6 standing position: “**performance was nearly matched by an O-trained level-only constant**” ([line 1173](https://github.com/trbrewer/puckworks/blob/baf6ef1e794ea2719e9036353d4d0b027a35accb/docs/submission/PAPER_A_JFE_MANUSCRIPT.md#L1173)).

The canonical draft repeats the same wording, including “adding little” ([canonical line 181](https://github.com/trbrewer/puckworks/blob/baf6ef1e794ea2719e9036353d4d0b027a35accb/docs/PAPER_A_DRAFT.md#L181)), “incremental skill … is small” ([lines 1018, 1155 and 1175](https://github.com/trbrewer/puckworks/blob/baf6ef1e794ea2719e9036353d4d0b027a35accb/docs/PAPER_A_DRAFT.md#L1018-L1181)), and “nearly matched” ([line 1181](https://github.com/trbrewer/puckworks/blob/baf6ef1e794ea2719e9036353d4d0b027a35accb/docs/PAPER_A_DRAFT.md#L1181)).

This directly contradicts the Round 10 acceptance record, which states that §4’s “adds little” conclusion was retired and that no reader-facing surface should make an absence/equivalence/practical-negligibility decision ([Round 10 acceptance lines 95–114](https://github.com/trbrewer/puckworks/blob/baf6ef1e794ea2719e9036353d4d0b027a35accb/docs/paper1_resource/PAPER_1_ROUND_10_REMEDIATION_ACCEPTANCE.md#L95-L114)).

### Why this is submission-blocking

The observed difference is real and should remain prominent: at 40 g, model-minus-comparator pooled MAPE is −0.394 percentage points, favouring the mechanistic model. But “adding little,” “incremental skill is small,” and “nearly matched” do more than state the number. They assign a practical magnitude or equivalence-adjacent property to the comparison.

No practical margin was declared. The ranges have no calibrated coverage. The analysis therefore cannot decide that the incremental value is negligible, small in the practical sense, equivalent, absent, or nearly the same. It also cannot decide superiority. The defensible conclusion is symmetrical non-establishment: the observed point estimate favours the model, while the procedure does not establish whether that advantage is reproducible or practically useful and does not establish that it is absent.

The principal generated Results block uses “the **observed** advantage is therefore small” and immediately states that reproducibility and practical usefulness are not established. I do not elevate that isolated, numerically tethered formulation as a separate blocker. The P0 is the repeated property-level conclusion that the model **adds little**, its **skill is small**, or the comparator **nearly matched** it—especially because one of those exact claims was expressly retired in Round 10.

### Required correction

Replace every property-level “skill/little/nearly matched” formulation in both manuscripts with a neutral statement of the observed contrast and the decision boundary. For example:

> At 40 g, observed pooled MAPE was 8.44% for the mechanistic model and 8.83% for the level-only comparator, a model-minus-comparator difference of −0.394 percentage points. The reported fixed-predictor sensitivity ranges are uncalibrated and no practical margin was predeclared; this analysis therefore establishes neither superiority, non-inferiority, equivalence, practical usefulness, nor absence of incremental value.

For the standing-position paragraph, a shorter acceptable form is:

> After target-specific optimal-grind recalibration, the mechanistic model’s observed pooled MAPE was 8.44% versus 8.83% for the level-only comparator. That observed advantage is less than half a percentage point, but the present analysis does not determine whether it is reproducible or practically useful and does not establish equivalence or absence of incremental value.

### Minimum acceptance criterion

1. No reader-facing Paper 1 surface contains “adds little,” “incremental skill is small,” “mechanistic skill is small,” “nearly matched,” or an equivalent practical-negligibility/equivalence verdict.
2. The manuscript and canonical draft retain the observed −0.394 pp direction prominently.
3. Every replacement explicitly distinguishes “not established” from “false/absent.”
4. Exact and variant mutation tests demonstrate that the claim-policy gate catches the retired phrases before merge.
5. `claim_coverage` and the consistency checks pass on both manuscripts after the rewritten prose is regenerated or synchronized.

---

## P1-1 — The claim-policy disclaimer heuristic and phrase taxonomy permit contradictory verdicts

### Finding

The claim policy suppresses a prohibited match whenever **any** item in a broad disclaimer list appears within the preceding 140 normalized characters. The list includes generic fragments such as `neither`, `without`, `is not`, `are not`, `not a`, `rather than`, and `reserve` ([`claim_policy.py` lines 181–198](https://github.com/trbrewer/puckworks/blob/baf6ef1e794ea2719e9036353d4d0b027a35accb/puckworks/paper_a/claim_policy.py#L181-L198)). The scanner does not determine whether that disclaimer negates the matched proposition, whether it belongs to another sentence, or whether a contrastive conjunction reverses it; it simply searches the preceding window ([lines 227–240](https://github.com/trbrewer/puckworks/blob/baf6ef1e794ea2719e9036353d4d0b027a35accb/puckworks/paper_a/claim_policy.py#L227-L240)).

The rule taxonomy also does not include the practical-negligibility and equivalence-adjacent language now present in the manuscript: “adds little,” “incremental skill … is small,” “nearly matched,” “marginal benefit,” or “essentially no practical advantage.”

### Reproduced false greens

Against the exact-commit `TRANSFER_INFERENTIAL_STATUS`, the scanner behaved as follows:

```text
The model outperforms the comparator.
  -> caught as superiority

The ranges are not confidence intervals. The model outperforms the comparator.
  -> []

This is not an inferential result, but the model outperforms the comparator.
  -> []

Without calibrated coverage, the model outperforms the comparator.
  -> []

The result is not precise. The model has no incremental skill.
  -> []

We do not claim equivalence; the model is equivalent to the comparator.
  -> []

The uncertainty is not small. The model performs comparably.
  -> []

The model adds little to a baseline that carries no mechanism at all.
  -> []

Its incremental skill over a level-only comparator is small.
  -> []

Performance was nearly matched by a level-only constant.
  -> []
```

Most importantly, scanning the **actual** exact-commit files returned:

```text
docs/submission/PAPER_A_JFE_MANUSCRIPT.md: 0 problems
docs/PAPER_A_DRAFT.md:                    0 problems
```

Thus the policy’s green result does not cover the claim class it was introduced to prevent.

### Why this matters

A nearby disclaimer is not a grammatical negation. “We do not claim equivalence; the model is equivalent” is internally contradictory and should fail, not pass. Similarly, “the ranges are not confidence intervals” cannot license a later superiority verdict. The current heuristic rewards exactly the prose shape most likely to appear in a careful scientific paragraph: a limitations sentence followed by an overstrong conclusion.

The missing rule classes also mean an author can reintroduce the retired conclusion through natural paraphrase without needing any disclaimer bypass at all.

### Required correction

1. Replace broad preceding-window suppression with proposition-scoped handling. A disclaimer should be accepted only when the negation or non-establishment construction is syntactically attached to the same decision term, for example:
   - “we make no claim of equivalence”;
   - “the analysis does not establish superiority”; or
   - “the ranges cannot determine whether the difference is absent.”
2. Remove generic tokens such as `without`, `neither`, `is not`, `are not`, and `not a` as standalone suppressors.
3. Treat sentence boundaries, semicolons, and contrastive conjunctions (`but`, `however`, `yet`) as hard barriers unless a narrowly specified grammar shows the disclaimer continues to govern the matched term.
4. Add practical-negligibility/equivalence-adjacent classes, including at least:
   - `adds? little` / `offers? little`;
   - `small|minimal|marginal|negligible incremental (skill|gain|value|benefit)`;
   - `nearly|essentially|effectively matched`;
   - `essentially the same` / `within noise`;
   - `no material/practical advantage`; and
   - “only marginal benefit.”
5. Prefer structured generated central-claim text over relying on an open-ended keyword list for the most important surfaces.

### Minimum acceptance criterion

A mutation suite must fail every contradictory or paraphrased example above while continuing to permit genuine disclaimers. It must also fail the present exact P0 sentences when inserted into any scanned reader-facing surface, and the current manuscripts must no longer return a false clean result.

---

## P1-2 — `InferentialStatus` is self-attested rather than evidence-bound

### Finding

The current `TRANSFER_INFERENTIAL_STATUS` is scientifically conservative and correct: all decision flags are false, coverage is uncalibrated, and no practical margin is declared ([`transfer_semantics.py` lines 503–517](https://github.com/trbrewer/puckworks/blob/baf6ef1e794ea2719e9036353d4d0b027a35accb/puckworks/paper_a/transfer_semantics.py#L503-L517)).

The problem is the **future unlock mechanism**. `status_from_dict` accepts a serialized object, checks field types and enum membership, and converts any non-null `confidence_procedure` with `str(...)` ([lines 520–561](https://github.com/trbrewer/puckworks/blob/baf6ef1e794ea2719e9036353d4d0b027a35accb/puckworks/paper_a/transfer_semantics.py#L520-L561)). `validate_inferential_status` then checks only internal coherence: whether a procedure name, confidence level, decision flag, and practical margin are mutually present ([lines 564–623](https://github.com/trbrewer/puckworks/blob/baf6ef1e794ea2719e9036353d4d0b027a35accb/puckworks/paper_a/transfer_semantics.py#L564-L623)). It does not verify that the named procedure exists, ran, achieved calibrated coverage, used the declared margin prospectively, or produced the declared decision.

A second inconsistency is that `predictors_refitted_within_draw=True` is rejected unconditionally—even for the enum value intended to represent a future calibrated confidence procedure—while a fabricated calibrated status with that flag set to `False` can pass.

### Reproduction

The following fabricated object passed status validation and unlocked equivalence prose:

```text
analysis_kind: calibrated_clustered_confidence
coverage_calibrated: true
confidence_level: 0.95
confidence_procedure: "invented future procedure"
predictors_refitted_within_draw: false
supports_equivalence_decision: true
practical_margin_pp: 0.5
permitted_claim_class: calibrated_decision

validate_inferential_status(...) -> []
scan("The model is equivalent to the comparator.", fabricated_status) -> []
```

Replacing the procedure string with a JSON array also passed because the parser coerced it to a string:

```text
confidence_procedure: ["fake", "procedure"]
parsed as: "['fake', 'procedure']"
validate_inferential_status(...) -> []
```

### Why this matters

The status object is the authority that disables prohibited-language rules. If it is an editable declaration rather than a derived, independently checked result, the mechanism moves the overclaiming risk instead of eliminating it. A future author can make the object internally coherent and thereby license a decision the analytical evidence never earned.

This is not a criticism of the current all-false status; it is a finding that the purported automatic future unlocking is not evidence-safe.

### Required correction

Separate **declared status** from **verified status**. Decision flags should be derived from an immutable procedure/result record rather than accepted as primary booleans. At minimum, the verified record should bind:

- a registered procedure identifier and version;
- the analysis/result artefact hash and source-data hash;
- confidence target and decision rule;
- predictor-refit semantics;
- the predeclared practical margin and protocol reference;
- the observed interval/test result; and
- the decision produced by applying that rule.

The claim policy should grant decision language only from the verified/derived status. `confidence_procedure` must be either `null` or a non-empty string matching a registered procedure; lists, mappings, and other objects must be rejected rather than stringified. Validation of `predictors_refitted_within_draw` must depend on the analysis kind and registered procedure instead of universally requiring `False`.

### Minimum acceptance criterion

1. A fabricated but internally coherent status object cannot unlock decision language without a matching verified procedure/result artefact.
2. Non-string `confidence_procedure` values fail closed.
3. Changing any decision flag, confidence target, margin, procedure ID, result hash, or refit declaration without the corresponding evidence fails validation.
4. A positive-path test demonstrates that a genuinely registered future procedure can unlock only the exact decision it produced.

---

## P1-3 — Highlights and the Figure 3 caption are not governed as positive claim surfaces

### Finding

`SURFACE_ASSERTIONS` assigns the four accepted propositions to the abstract, significance paragraph, cover letter, Results headline, endpoint synthesis, supplement reading, and conclusion, but it has no `highlights` or `figure3_caption` surface ([`claim_policy.py` lines 295–312](https://github.com/trbrewer/puckworks/blob/baf6ef1e794ea2719e9036353d4d0b027a35accb/puckworks/paper_a/claim_policy.py#L295-L312)).

The current highlight says:

> “A process model’s gain over a concentration-only baseline was under 0.4 points”

([`PAPER_A_JFE_HIGHLIGHTS.txt` line 6](https://github.com/trbrewer/puckworks/blob/baf6ef1e794ea2719e9036353d4d0b027a35accb/docs/submission/PAPER_A_JFE_HIGHLIGHTS.txt#L6)).

It omits “observed,” the uncalibrated-range limitation, and the no-decision proposition. Read alone, “gain” is easy to interpret as an established model property.

The Figure 3 caption correctly reports 44 records, 132 observations, 8.44% versus 8.83%, 62 of 132, and states that any clustered intervals are fixed-predictor sensitivities rather than calibrated confidence intervals ([caption line 13](https://github.com/trbrewer/puckworks/blob/baf6ef1e794ea2719e9036353d4d0b027a35accb/docs/submission/PAPER_A_JFE_FIGURE_CAPTIONS.md#L13)). It does **not** say that no superiority, non-inferiority, equivalence, practical-usefulness, or absence decision is made, nor that acceptable endpoint accuracy alone does not establish mechanism transfer.

### Why this matters

Both files are independently uploaded and may be read without the manuscript paragraphs that supply the limitations. The caption file explicitly claims that its captions stand alone. A positive-coverage mechanism that ignores these surfaces permits the central claim to become materially stronger by omission while every prohibited-phrase check remains green.

### Required correction

Add named `highlights` and `figure3_caption` entries to the positive surface contract and bind them to their actual generated text.

Recommended minimum propositions:

- **Highlights:** observed direction/magnitude plus explicit non-establishment. Two venue-length bullets could be:
  - “Observed pooled MAPE was 0.394 points lower than a level-only comparator.”
  - “Uncalibrated ranges did not determine superiority or practical usefulness.”
- **Figure 3 caption:** all four central propositions, because the caption is intended to stand alone. A compact addition would be:
  - “These fixed-predictor sensitivity ranges are uncalibrated and support no superiority, non-inferiority, equivalence, practical-usefulness, or absence decision; acceptable endpoint accuracy alone does not establish kinetic-mechanism transfer.”

### Minimum acceptance criterion

1. Both surfaces are named in `SURFACE_ASSERTIONS` or an equivalent structured contract.
2. Deleting any required proposition from either generated file makes the check fail.
3. The generated Figure 3 caption includes an explicit no-decision statement, not only “not a confidence interval.”
4. The highlight identifies the comparison as **observed** and supplies a second compact bullet stating the inferential/practical limit.

---

## P1-4 — The source-to-observation contract shares unverified condition and support assumptions

### Finding

The independent source oracle and production manifest are usefully separate. They declare their analyte maps independently, parse scored cells through separate helpers, and compare exact partition membership rather than trusting an artefact’s self-hash. That architecture should be retained.

However, independence stops above several premises that both implementations accept without validation:

1. **Inclusion is tested before normalization.** The oracle checks raw `variety` and `granulometry` values before stripping them ([`source_resampling_oracle.py` lines 101–112](https://github.com/trbrewer/puckworks/blob/baf6ef1e794ea2719e9036353d4d0b027a35accb/puckworks/paper_a/source_resampling_oracle.py#L101-L112)); production does not strip those fields at all before filtering ([`transfer_contract.py` lines 587–599](https://github.com/trbrewer/puckworks/blob/baf6ef1e794ea2719e9036353d4d0b027a35accb/puckworks/paper_a/transfer_contract.py#L587-L599)). A stray space silently excludes a record rather than failing the source contract.
2. **`on_grid` is parsed as exact string equality to `"True"`.** Unknown tokens such as `true`, `TRUE`, `1`, or a misspelling become `False` rather than being rejected.
3. **Condition coordinates are not required to be finite.** Production calls `float(T)` and `float(p)` directly and will admit `NaN` or infinities into the manifest and cluster identifiers. The scored analyte values are finite-checked, but the design coordinates are not.
4. **Both sides canonicalize coordinates with default `g` formatting.** The oracle uses `"%g" % float(text)` ([oracle lines 83–85](https://github.com/trbrewer/puckworks/blob/baf6ef1e794ea2719e9036353d4d0b027a35accb/puckworks/paper_a/source_resampling_oracle.py#L83-L85)); production uses `f"{float(value):g}"` ([contract lines 525–538](https://github.com/trbrewer/puckworks/blob/baf6ef1e794ea2719e9036353d4d0b027a35accb/puckworks/paper_a/transfer_contract.py#L525-L538)). Default `g` formatting retains only six significant digits, so distinct coordinates can collapse into one cluster unless that quantization is explicitly part of the scientific design.
5. **Lookup support is copied from `on_grid`, not derived from actual optimal-grind support.** Production sets `lookup_defined = bool(on_grid)` ([contract lines 587–605](https://github.com/trbrewer/puckworks/blob/baf6ef1e794ea2719e9036353d4d0b027a35accb/puckworks/paper_a/transfer_contract.py#L587-L605)). It does not verify that an O-grind row actually exists at the same `(variety, T, p)`.
6. **The paper/contract boundary remains under-described.** The current checks establish presence, numeric parseability, finiteness of scored cells, membership, and grouping. They do not validate transcription correctness, analyte units, coordinate units, or physical plausibility against the source publication.

### Reproduced consequences

Synthetic rows passed as follows:

```text
C row marked on_grid=True, with no O-grind counterpart
  -> admitted; lookup_defined=True; train_sample_ids=[]

on_grid="true"
  -> admitted as on_grid=False rather than rejected

T_degC="NaN"
  -> admitted; temperature_degC=nan; cluster id contains "nan"

variety=" Arabica "
  -> silently excluded; zero retained records
```

Default-`g` canonicalization also produced collisions:

```text
93.40004 -> "93.4"
93.40005 -> "93.4"
9.000004 -> "9"
9.000005 -> "9"
```

The current source file does not contain these malformed values; this is a fail-closed/common-mode finding, not a claim that the present 44-record corpus is wrong.

### Why this matters

The Round 10 common-mode omission involved both implementations agreeing on an unverified premise. The same pattern remains possible one layer higher. A wrong `on_grid` flag, a missing O counterpart, a malformed coordinate, or a six-significant-digit collision can alter support and cluster membership while both implementations agree.

### Required correction

1. Define and enforce a strict source schema for `variety`, `granulometry`, `on_grid`, `T_degC`, `p_bar`, and scored analytes.
2. Normalize only under an explicit rule, or preferably reject leading/trailing whitespace in controlled source data so corruption is visible.
3. Parse booleans with an explicit accepted-token set and reject every unknown token.
4. Require finite coordinates and declared units; add plausible-range checks if they can be justified from the source design without converting provenance validation into model judgment.
5. Replace default-`g` canonicalization with a lossless decimal representation or an explicitly declared, tested quantization tied to measurement resolution. Distinct source values must not merge merely because Python’s default formatter rounds them.
6. Build an actual optimal-grind support set from source rows, for example `{(variety, canonical_T, canonical_p)}`, derive `lookup_defined` from membership, and fail if the source `on_grid` declaration disagrees.
7. Add a sentence to the Methods/data-provenance description stating exactly what the contract does and does not verify: it checks source structure, membership, parseability, finiteness, and support; it does not independently validate transcription, units, or measurement correctness against the article.
8. Keep the two analyte maps independently implemented; do not make one import the other. Instead, validate both against an external source-schema/provenance record and preserve mutation tests that change one side at a time.

### Minimum acceptance criterion

Mutations involving whitespace, unknown boolean tokens, `NaN`/±infinity coordinates, near-equal but distinct coordinates, absent O support with `on_grid=True`, and present O support with `on_grid=False` must all fail with named diagnostics. The unchanged source must continue to reproduce the exact 44-record/132-observation corpus and partition membership.

---

## P1-5 — The interval validator can raise `OverflowError` instead of rejecting malformed input

### Finding

`validate_interval_record` explicitly promises that malformed input returns named problems and “never raises” ([`transfer_contract.py` lines 364–385](https://github.com/trbrewer/puckworks/blob/baf6ef1e794ea2719e9036353d4d0b027a35accb/puckworks/paper_a/transfer_contract.py#L364-L385)). It catches `ValueError` around full-precision bound parsing ([lines 405–410](https://github.com/trbrewer/puckworks/blob/baf6ef1e794ea2719e9036353d4d0b027a35accb/puckworks/paper_a/transfer_contract.py#L405-L410)).

The central numeric helper calls `float(value)` without catching `OverflowError` ([`transfer_semantics.py` lines 93–111](https://github.com/trbrewer/puckworks/blob/baf6ef1e794ea2719e9036353d4d0b027a35accb/puckworks/paper_a/transfer_semantics.py#L93-L111)). A sufficiently large integer is valid JSON and is an `int`, but cannot be converted to a finite IEEE float.

### Reproduction

Replacing each numeric field in a valid interval record with `10**400` produced:

```text
full_precision_pp.lower           -> OverflowError: int too large to convert to float
full_precision_pp.upper           -> OverflowError: int too large to convert to float
signed_nearest_bound_to_zero_pp   -> OverflowError
width_pp                           -> OverflowError
display.lower                     -> OverflowError
display.upper                     -> OverflowError
```

### Why this matters

A validator used as a release gate must reject malformed artefacts deterministically. Crashing is not equivalent to a named validation failure: it can terminate a multi-artefact check early, hide additional problems, or be caught at a higher layer and misclassified as infrastructure failure.

### Required correction

- Catch `(TypeError, ValueError, OverflowError)` around every numeric conversion, preferably centrally in `require_finite_number`.
- Audit `_same_value`, canonical-record reconstruction, display-field comparison, confidence-level parsing, and practical-margin parsing for the same class.
- Return a path-specific diagnostic such as `interval.display.lower must be a finite JSON number; conversion overflowed`.

### Minimum acceptance criterion

A mutation test must place a large positive and negative integer in every numeric interval field and confirm that `validate_interval_record` returns one or more named problems without raising. The same totality test should cover status confidence levels and margins if those fields share float conversion paths.

---

## P1-6 — The scanner does not normalize rendered text, discards internal link targets, and under-scopes internal-path rules

### Finding

The consistency scanner describes `_visible_text` as what a reader sees, but it only replaces Markdown links with their visible labels and collapses whitespace ([`paper_a_consistency.py` lines 542–556](https://github.com/trbrewer/puckworks/blob/baf6ef1e794ea2719e9036353d4d0b027a35accb/tools/paper_a_consistency.py#L542-L556)). It does not remove emphasis markers, inline HTML tags, or entities. Link targets are discarded entirely.

The rule scope also applies `internal_path` and `internal_narration` only to the manuscript and supplement, even though the highlights, cover letter, and upload-ready captions are actual submission files ([lines 237–261](https://github.com/trbrewer/puckworks/blob/baf6ef1e794ea2719e9036353d4d0b027a35accb/tools/paper_a_consistency.py#L237-L261)).

### Reproduced false negatives

```text
"An earlier version was wrong."
  -> caught
"An earlier **version** was wrong."
  -> not caught
"An earlier <em>version</em> was wrong."
  -> not caught

"The second review asked for this."
  -> caught
"The second *review* asked for this."
  -> not caught

"See docs/internal/review.md for details."
  -> caught
"See [the internal analysis](docs/internal/review.md) for details."
  -> not caught
```

The same bypass persisted inside the shapes the brief highlighted:

```text
| Note | An earlier **version** was wrong |     -> not caught
- The second *review* asked for this.           -> not caught
[^1]: See [analysis](docs/internal/review.md).  -> not caught
```

Plain table cells, list items, and footnotes are not inherently invisible to the paragraph iterator. The demonstrated weakness is that inline markup or link syntax inside those structures splits or hides the prohibited phrase.

### Why this matters

The scanner exists to prevent review history, producer identifiers, and repository paths from reaching an editor. Those strings can now be hidden with ordinary Markdown emphasis or a hyperlink. Discarding a link target may make sense for prose semantics, but it is unsafe for an **internal-path leakage** rule: the target remains embedded in the submitted source and can surface in conversion, accessibility metadata, or editor inspection.

Scoping internal paths to only the manuscript and supplement is also too narrow. The cover letter and standalone captions are sent to the journal; an internal path in either is still a leak. The package may reasonably be exempt because it is an assembly manifest, and the canonical draft may be exempt from path checks because it is repository-facing, but the actual upload deliverables should not be.

### Required correction

1. Parse Markdown into an abstract syntax tree or otherwise normalize rendered text robustly:
   - remove emphasis markers and inline-code delimiters;
   - strip or decode inline HTML and entities;
   - preserve block boundaries and source-line mapping;
   - normalize Unicode punctuation and whitespace where relevant.
2. Scan visible link text for prose rules **and** scan link/reference destinations separately for internal-path patterns. Apply a narrow allowlist for legitimate submitted figure filenames and public release URLs rather than discarding all targets.
3. Apply `internal_path` and `internal_narration` to every true upload deliverable: manuscript, supplement, cover letter, highlights, and standalone captions. Exempt only files whose submission role genuinely requires repository paths, and document each exemption.
4. Add mutation tests for paragraphs, headings, list items, table cells, footnotes, reference-style links, emphasis, inline code, HTML tags, entities, and combinations of these.

### Minimum acceptance criterion

Every reproduced false negative above must fail. An internal path hidden in either inline or reference-style link syntax must fail on every upload-facing file. Legitimate submitted figure paths should pass only through an explicit, narrow allowlist.

---

## P2-1 — Figure 4’s generated upload caption includes the supplementary-section delimiter

### Finding

The current upload-ready caption file ends Figure 4 with the literal text:

> `... they should not be pooled as equivalent validation. --- ## Supplementary figures`

and then emits a second standalone `## Supplementary figures` heading on the next block ([`PAPER_A_JFE_FIGURE_CAPTIONS.md` lines 15–17](https://github.com/trbrewer/puckworks/blob/baf6ef1e794ea2719e9036353d4d0b027a35accb/docs/submission/PAPER_A_JFE_FIGURE_CAPTIONS.md#L15-L17)).

The generator’s regular expression captures from a `### Figure N` heading until the next `###` heading or end-of-file. It does not stop at a horizontal rule or a `##` section heading ([`paper_a_figure_captions.py`, `_HEADING`](https://github.com/trbrewer/puckworks/blob/baf6ef1e794ea2719e9036353d4d0b027a35accb/tools/paper_a_figure_captions.py#L37-L59)). The renderer then adds its own supplementary heading. Because the checked upload file exactly equals the generator’s malformed output, freshness and parity remain green.

### Why this matters

The deliverable is no longer a clean standalone caption set. This is editorial rather than scientific—the caption’s scientific content remains understandable—but it demonstrates that equality to a generator does not establish validity of the generated structure.

### Required correction

Parse the internal map structurally, or terminate caption extraction at any heading of level 1–3 and at horizontal rules. Add output invariants:

- exactly four main captions and four supplementary captions for the current package;
- exactly one `## Supplementary figures` heading;
- no caption body contains a horizontal-rule token or embedded heading marker; and
- each caption begins with exactly one `**Figure N.` label.

### Minimum acceptance criterion

Regenerate the caption file, confirm the Figure 4 caption ends at “equivalent validation,” and verify the structural invariants above in an automated test plus a direct visual read of the standalone file.

---

## 4. Brief section-by-section conclusions

## 4.1 (a) Corrected claim, read as an argument

**Finding present:** P0-1.

### Checked and sound

- The title is specific, includes “espresso,” and accurately frames the measurement/identifiability problem.
- The abstract clearly reports the observed model-favouring difference, the 62/132 count, the zero-containing primary range, the lack of calibrated coverage/margin, and the non-establishment of reproducibility/usefulness.
- The principal Results block, Table 4a, endpoint synthesis, Supplementary Table S3 reading, and cover letter preserve the sign convention and distinguish numerical resolution from inferential resolution.
- The paper has not overshot so far into hedging that the result disappears: the −0.394 pp observed advantage is prominent.
- The relative pooled-MAPE reduction column is now clearly defined as `100 × (comparator − model) / comparator` and expressly described as descriptive rather than inferential. I found no ambiguity requiring a new finding.

### Not sound

The Introduction and Discussion reintroduce an unsupported practical/property verdict through “adding little,” “incremental skill is small,” and “nearly matched.” The generated core blocks are not enough if ungenerated narrative reverses their evidentiary boundary.

## 4.2 (b) Claim policy as a mechanism

**Findings present:** P1-1, P1-2, and P1-3.

### Checked and sound

- The current all-false `InferentialStatus` accurately describes the fixed-predictor sensitivity analysis.
- Encoding the accepted central claim as positive propositions is the right design direction; a purely prohibitive scanner would permit omission.
- Where a surface is actually assigned propositions, the current generated text generally carries them correctly.

### Not sound

- Generic nearby disclaimers can suppress unrelated or contradictory verdicts.
- Important practical-negligibility/equivalence paraphrases are absent from the rule set.
- The status is not evidence-bound.
- The highlights and Figure 3 caption are not positive-coverage surfaces.

## 4.3 (c) Source-to-observation contract

**Finding present:** P1-4.

### Checked and sound

- The independent oracle should remain independently implemented; making it import the production analyte map would recreate the common mode it was designed to break.
- Both implementations now require each scored `CF`/`TR`/`5CQA` cell to exist, parse numerically, and be finite.
- Exact membership comparison is the correct authority; counts and self-hashes alone are insufficient.
- The current source file is consistent with the 44-record/132-observation result. I found no current-corpus or stale-number discrepancy.

### Boundary requiring clarification

The contract validates structural and computational admissibility, not measurement truth. The paper should state explicitly that it does not independently verify transcription, units, or plausibility against the source publication.

## 4.4 (d) Estimand and design contract

**No separate finding. Checked and clean, subject to the source-support defect in P1-4.**

The direction derivation is correct in all four combinations:

| Metric preference | Operation | Negative values favour |
|---|---|---|
| lower is better | left − right | left |
| lower is better | right − left | right |
| higher is better | left − right | right |
| higher is better | right − left | left |

The manuscript states the actual metric/order/sign wherever it is load-bearing: pooled MAPE for the mechanistic model minus pooled MAPE for the level-only comparator, with negative values favouring the mechanistic model.

The division between authorial declarations and source-derived facts is reasonable. Role, human-readable label, and scientific rationale are authorial; membership, support, and partition content should remain source-derived. I found no additional field that clearly belongs on the opposite side.

The normalized-partition hash earns its place as a **secondary integrity signal after exact content comparison**. It would be redundant or dangerous if treated as proof of correctness, but it is useful for deterministic serialization/provenance once content has been independently verified.

## 4.5 (e) Interval records

**Finding present:** P1-5.

### Checked and sound

- The exact full-precision zero relation is reconstructed rather than trusted.
- `touches_zero_at_lower`, `touches_zero_at_upper`, and `display.contains_zero_rounded` are materially clearer than the prior ambiguous `touches_zero` field.
- Unexpected fields fail, and the stored redundancy is defensible because every field is exact-compared to a canonical reconstruction.
- I found no stored field that obviously should be removed rather than validated.

### Not sound

The totality contract is incomplete because oversized integer conversion can raise `OverflowError`.

## 4.6 (f) Scanner and caption split

**Findings present:** P1-6 and P2-1.

### Checked and sound

- Splitting the internal figure map from the upload-ready caption file is the correct architecture.
- Excluding the internal map itself from submission-language scanning is defensible **only** because it is never uploaded and because the generated upload file is separately validated.
- The scientific content of Figures 1, 2, S1–S4 generally reads as standalone caption text.

### Not sound

- The upload-side scanner is vulnerable to ordinary Markdown/HTML and hidden link targets.
- Internal path/narration scoping omits several true upload files.
- The caption generator currently reproduces a malformed Figure 4 boundary and the parity check certifies it.
- Figure 3 lacks an explicit no-decision/transfer-limit sentence, addressed in P1-3.

### Lower-priority items from the brief

I found no new text-level defect in Supplementary Table S7 or the re-rendered Figure 4 panel-(c) title. I did not independently perform a journal-width typesetting proof of S7 or a pixel-level image-difference audit; those remain the brief’s acknowledged presentation checks and are not re-reported as findings here.

---

## 5. Numerical reconciliation — no stale-number finding

The protected values in the Round 11 brief agree with the current submission surfaces.

| Endpoint | Protected model MAPE | Protected comparator | Protected difference | Protected primary full-precision range | Protected worse-on count | Submission display checked |
|---|---:|---:|---:|---:|---:|---|
| 38 g | 8.39% | 8.83% | −0.447 pp | [−0.884387, −0.042433] | 61/132 | Table 4a and Supplement S3 show 8.39, 8.83, −0.447, [−0.884, −0.042], 61/132 |
| 40 g | 8.44% | 8.83% | −0.394 pp | [−0.829052, +0.003791] | 62/132 | Abstract, Results, Table 4a, Supplement S3, Figure 3 caption, and cover letter agree after declared rounding |
| 42 g | 8.41% | 8.83% | −0.425 pp | [−0.891251, +0.005844] | 60/132 | Table 4a and Supplement S3 show 8.41, 8.83, −0.425, [−0.891, +0.006], 60/132 |

The relative pooled-MAPE reductions in Supplementary Table S3—4.98%, 4.42%, and 4.76%—are consistent with the stated descriptive formula and the archived pooled values. The 40 g primary range is correctly described as containing zero; the 38 g range excludes zero on the negative/model-favouring side; the 42 g range contains zero. The 40 g upper bound is small and positive rather than “touching” zero.

**Conclusion: the stale-number category remains empty.**

---

## 6. Prioritized remediation sequence

1. **Remove the P0 language first.** Rewrite every “adds little,” “incremental skill is small,” and “nearly matched” sentence in the manuscript and canonical draft, preserving the observed −0.394 pp result and the symmetrical non-establishment conclusion.
2. **Make the claim-policy gate capable of preventing the exact recurrence.** Scope disclaimers to the same proposition and add practical-negligibility/equivalence paraphrases, with adversarial tests.
3. **Bind inferential authority to evidence.** Derive decision grants from a verified procedure/result record and reject non-string procedure identifiers.
4. **Extend positive surface coverage.** Add highlights and Figure 3 caption to the assertion contract; regenerate both.
5. **Close source common modes.** Strictly validate condition metadata, derive lookup support, and replace lossy default-`g` canonicalization.
6. **Restore validator totality.** Catch overflow in all numeric paths and add oversized-number mutations.
7. **Use rendered-text/AST scanning and scan link targets.** Expand internal-path scope to all actual upload files.
8. **Fix the caption parser and regenerate.** Add structural output invariants so malformed generated text cannot be certified merely because it is reproducible.
9. **Rerun the complete assurance chain.** At minimum, run every command in §4 of the Round 11 brief, including both-manuscript claim coverage, targeted tests, the full test suite, and a direct visual inspection of the final upload package. A science-producer rerun is not necessary solely for these text/contract corrections unless source/design changes alter the archived result artefacts.

---

## 7. Final review conclusion

The numerical work and the central generated claim surfaces are substantially more coherent than in prior rounds. The manuscript correctly reports a model-favouring observed difference, correctly distinguishes sensitivity ranges from confidence intervals, and correctly avoids turning a zero relation into an inferential verdict in its principal generated blocks.

However, the submission is not ready because the ungenerated Introduction and Discussion still make the practical/property conclusion that Round 10 explicitly retired. The claim-policy scan’s clean result is therefore a false assurance, not merely incomplete coverage. The additional P1 findings show how the same class of error can recur through nearby disclaimers, fabricated inferential status, omitted standalone surfaces, shared source assumptions, malformed numeric input, and Markdown/link bypasses.

The appropriate Round 11 disposition is:

> **P0 REMEDIATION REQUIRED BEFORE SUBMISSION; CLAIM AND ASSURANCE HARDENING REQUIRED BEFORE ACCEPTANCE.**

