# Paper 1 — Round 11 Remediation Acceptance

**Prepared:** 30 July 2026
**Reviewed commit (input):** `baf6ef1e794ea2719e9036353d4d0b027a35accb`
**Controlling review:** `PAPER_1_ROUND_11_DETAILED_REVIEW.md`
**Controlling plan:** `PAPER_1_ROUND_11_REMEDIATION_IMPLEMENTATION_PLAN.md`
**Branch:** `paper1/round11-remediation`
**Final code commit:** `7767a7b1bc9e` · **tree:** `17ad8b73d184db4a99c32ac02936d769cfa7702b`
**Full-suite run commit:** `df1406f` (this report's own commit re-runs nothing but itself)

This report records what was changed, what was run, and what was **not** run. It does not claim
that all checks pass; it names each check and its status.

---

## 1. Disposition

All eight Round 11 findings are actioned: **1 P0, 6 P1, 1 P2.**

Three defects of the same class that the review did not list were found by the new gates while
implementing them, and are corrected here as well — they are itemised in §4 rather than folded
silently into the counts.

| ID | Severity | Finding | Disposition |
|---|---|---|---|
| P0-1 | P0 | "adds little / incremental skill is small / nearly matched" in both manuscripts | **Closed** — all five occurrences rewritten; recurrence tests land in the same commit |
| P1-1 | P1 | Disclaimer suppression and decision taxonomy produce false greens | **Closed** — clause-scoped safe spans; six new rule classes |
| P1-2 | P1 | `InferentialStatus` is self-attestation, not evidence | **Closed** — decisions derived from a verified procedure/result record |
| P1-3 | P1 | Highlights and Figure 3 not governed as positive surfaces | **Closed** — both registered; both regenerated |
| P1-4 | P1 | Shared unverified source premises | **Closed** — versioned schema, lossless keys, derived support |
| P1-5 | P1 | Interval validator raises `OverflowError` | **Closed** — totality restored at every conversion boundary |
| P1-6 | P1 | Scanner does not normalise rendered text; under-scoped | **Closed** — CommonMark parse, two channels, all upload files |
| P2-1 | P2 | Figure 4 caption absorbs the section delimiter | **Closed** — structural extraction plus output invariants |

**Producer rerun: NOT REQUIRED, and not performed.** Justified in §6.

---

## 2. Protected numerical invariants — unchanged

| Endpoint | Model pooled MAPE | Comparator | Model − comparator | Primary full-precision range | Model worse on |
|---|---:|---:|---:|---:|---:|
| 38 g | 8.39 % | 8.83 % | −0.447 pp | [−0.884387, −0.042433] | 61/132 |
| 40 g | 8.44 % | 8.83 % | −0.394 pp | [−0.829052, +0.003791] | 62/132 |
| 42 g | 8.41 % | 8.83 % | −0.425 pp | [−0.891251, +0.005844] | 60/132 |

`tools/paper_a_numerical_invariants.py --check` → *every protected value unchanged*.
Corpus membership, partitions and hashes are also unmoved (§6).

---

## 3. P0-1 — exact before/after

The Round 10 acceptance retired the conclusion that cross-grind prediction "adds little". Round 11
found the same **decision** back on five reader-facing surfaces in different words, with the claim
scanner reporting zero problems on both manuscripts.

| Surface | Before | After (abridged) |
|---|---|---|
| §1.3 | "…while **adding little** to a baseline that carries no mechanism at all." | "…while its observed pooled-MAPE advantage over a baseline that carries no mechanism at all **is less than half a percentage point**. Because the reported ranges are uncalibrated fixed-predictor sensitivities and no practical margin was predeclared, this analysis **does not determine** whether that observed advantage is reproducible or practically useful, and it **does not establish that the advantage is absent**." |
| §4 synthesis | "(while its **incremental skill over a level-only comparator is small**, per the benchmark above)" | "(while its observed pooled-MAPE difference from a level-only comparator is **−0.394 pp at 40 g, favouring the model**, which the uncalibrated ranges **establish neither as reproducible and practically useful nor as absent**…)" |
| §6 four properties | "but its **incremental skill over a level-only comparator is small**" | "but its **observed incremental skill over a level-only comparator is −0.394 pp of pooled MAPE, which this analysis establishes neither as reproducible and practically useful nor as absent**" |
| §6 strength ladder | "…whose **incremental skill over a level-only baseline is small**, and which does not…" | "…whose observed incremental skill over a level-only baseline is **−0.394 pp of pooled MAPE with uncalibrated ranges that establish neither its reproducibility nor its absence**, and which does not…" |
| §6 standing position | "…but performance was **nearly matched by** an O-trained level-only constant (pooled 8.44 % vs 8.83 %…)" | "…and the model's observed pooled MAPE was **8.44 % against 8.83 %** — a **model-minus-comparator difference of −0.394 pp, favouring the model**, with the model worse on 62 of 132 held-out points. That observed advantage is less than half a percentage point; because the ranges are uncalibrated and no margin was predeclared, the present analysis **does not determine** whether it is reproducible or practically useful, and **does not establish equivalence or absence of incremental value**." |

Identical edits landed in `docs/PAPER_A_DRAFT.md` in the same commit.

### Why the new wording is descriptive rather than a decision

Each replacement states a **measured quantity** and then the **boundary of what follows from it**.
"Less than half a percentage point" and "−0.394 pp" are properties of the observed data: anyone can
check them against Table 4a. "Small" is not — it is a comparison against a threshold of relevance,
and no such threshold was predeclared, so the word imports a decision the procedure never made.
The same applies to "nearly matched", which asserts the two arms are close enough to be treated as
the same; that is an equivalence judgement requiring both a margin and calibrated coverage.

Non-establishment is **symmetrical** everywhere. One-sided caution ("superiority was not
established") is insufficient, because it leaves an absence or equivalence reading standing —
which is precisely the reading the retired wording invited. Every corrected paragraph therefore
denies both directions, and the result the paper actually has (−0.394 pp, favouring the model) is
now **more** prominent than the adjective it replaced, not less.

---

## 4. Findings the new gates caught that the review did not list

Reported explicitly rather than absorbed, because each is the P0 class and each was live at the
reviewed commit:

1. **`editor_significance`: "only a **small observed gain** over a trained level-only baseline."**
   Rendered into the package, the cover letter and the canonical draft. Missed by the first draft of
   the magnitude rule because "observed" sat between the adjective and the noun; the rule now
   tolerates up to two intervening modifiers. Now: "its observed gain … is 0.394 percentage points
   of pooled error".
2. **Manuscript §4: "while its **small advantage** over a comparator changes sign."** A generic
   statement about predictors, but an unqualified magnitude verdict all the same. Now "observed
   advantage".
3. **Canonical draft figure-map table: "a **small observed gain** over the level-only comparator."**
   Now "an observed −0.394 pp gain".

A fourth, of the P1-6 class:

4. **The uploaded Highlights file named two repository paths on line 2** —
   `tools/paper_a_front_matter.py` and `docs/submission/paper_a_front_matter.yaml`, in plain text,
   not inside a comment. Invisible because `internal_path` was scoped to the manuscript and
   supplement. Widening the scope found it immediately. The "do not edit by hand" warning the
   header exists for survives; the paths do not.

---

## 5. Finding-by-finding evidence

### P1-1 — clause-scoped disclaimers and the missing taxonomy

Two independent defects produced one false green.

*Taxonomy.* Six classes added — `adds_little`, `small_incremental_value`, `nearly_matched`,
`essentially_same`, `within_noise`, `no_practical_advantage` — each scoped to the increment itself,
so "a small positive upper bound", "a small sample", "records were matched by variety" and "no
practical margin was predeclared" remain legal.

*Suppression.* The 140-character preceding-window search is deleted, along with the generic tokens
`neither`, `without`, `is not`, `are not`, `not a`, `reserve`, `rather than`. A non-establishment
construction now governs from where it starts to the end of **its** clause; sentence ends,
semicolons, colons, dashes, contrastive conjunctions and a new coordinated subject all end a clause.

| Mutation | Before | After |
|---|---|---|
| `The ranges are not confidence intervals. The model outperforms the comparator.` | clean | `[outperforms]` |
| `We do not claim equivalence; the model is equivalent to the comparator.` | clean | `[is_equivalent]` |
| `Without calibrated coverage, the model outperforms the comparator.` | clean | `[outperforms]` |
| `This is not an inferential result, but the model outperforms the comparator.` | clean | `[outperforms]` |
| `The result is not precise. The model has no incremental skill.` | clean | `[no_incremental_skill]` |
| `The uncertainty is not small. The model performs comparably.` | clean | `[comparable_performance]` |
| `The model adds little to a baseline that carries no mechanism at all.` | clean | `[adds_little]` |
| `Its incremental skill over a level-only comparator is small.` | clean | `[small_incremental_value]` |
| `Performance was nearly matched by a level-only constant.` | clean | `[nearly_matched]` |
| `The models are essentially the same.` | clean | `[essentially_same]` |
| `The mechanistic model offers only marginal benefit.` | clean | `[small_incremental_value]` |
| `The difference is within noise.` | clean | `[within_noise]` |
| `The comparator is no worse than the mechanistic model.` | caught | `[at_least_as_good]` |
| `This analysis does not establish superiority, and the model outperforms the comparator.` | clean | `[outperforms]` |

Genuine disclaimers still pass (19 examples, including every sentence Round 10 praised). The five
retired sentences are pinned **verbatim** and re-tested by injection into an actual upload file,
because the finding was that they were in the shipped manuscript while `verify` printed clean.

A second, independent authority pins the same strings in the submission contract's phrase table,
which also holds the two manuscripts together on the authored paragraphs that have no
generated-block parity.

### P1-2 — inferential authority bound to evidence

New `puckworks/paper_a/inferential_evidence.py`:

```
registered procedure + evidence record + the artefacts it names
    -> verify (every digest recomputed, every semantic re-checked)
    -> DERIVE each decision from the observed interval and the registered rule
    -> VerifiedInferentialStatus, whose flags are computed properties
```

* `claim_policy.granted()` returns the empty set for a declared `InferentialStatus` whatever its
  flags read, and raises on a duck-typed stand-in.
* The reviewer's fabricated status now unlocks nothing and cannot be verified: no such procedure is
  registered, and free text cannot select one.
* `confidence_procedure: ["fake", "procedure"]` fails type validation; the `str()` coercion is gone.
* `predictors_refitted_within_draw` is the registered procedure's requirement, not a universal ban;
  the fixed-predictor rule is scoped to the analysis kind it is about.
* The artefact boundary fails closed: a status granting a decision with no evidence record raises
  in `validated_analysis` rather than rendering prose from it.
* **Registry ships empty**, which is the honest state — Paper A performs no inferential procedure.
  The positive path is exercised by a test-only synthetic procedure, because a fix that merely bans
  the language is one a future author will delete rather than satisfy.

**Current status for the record:** `fixed_predictor_clustered_sensitivity`, coverage uncalibrated,
`confidence_procedure=None`, all four decision flags false, no margin, claim class
`descriptive_evidence_limited`. No evidence record and no procedure id, because none is claimed.

71 tests: both reproductions verbatim; every evidence field and every declared field mutated one at
a time; each artefact digest broken **and** each omitted (partial evidence fails closed); the
decision proved recomputed rather than copied; the paper proved unaffected.

### P1-3 — the two standalone surfaces

`SURFACE_ASSERTIONS` gains `highlights` (observed advantage · ranges uncalibrated · no decision) and
`figure3_caption` (all four, because its own file header claims the captions stand alone).

Highlights, regenerated from the one front-matter source — 5 bullets, 68/73/75/63/70 characters
against the venue's 85, no unexpanded acronyms:

```
• Whole-cup espresso data weakly separate content from extraction rate
• Observed pooled error was 0.394 points lower than a level-only comparator
• Uncalibrated ranges support no superiority, equivalence or absence decision
• Time-resolved samples constrained extraction rate more strongly
• Accurate prediction did not guarantee well-determined model parameters
```

The character limit was answered by compact rewriting, never by dropping the caveat.

Figure 3's caption now carries the signed point estimate (−0.394 pp, from the archived value and the
typed estimand), the generated limits sentence, and the transfer boundary — the decision and
transfer components come from the same renderers the manuscript uses, and the sentence they
replaced was deleted rather than left to duplicate them. The extractor addresses Figure 3 by its
exact `**Figure 3.` label, so `Figure S3` cannot be audited in its place.

Deletion mutations are **proposition-level**: a proposition may be carried by several phrasings, so
each test strips every accepted carrier. Removing one rendering while a synonym survives is not a
loss of the claim.

### P1-4 — the shared source premises

New `puckworks/paper_a/source_schema.py`: one declarative authority for what a source row is.

| Reproduced | Before | After |
|---|---|---|
| `variety=" Arabica "` | silently excluded; zero retained records | `SourceSchemaError` naming the sample and the whitespace |
| `granulometry="C "` | silently excluded | rejected |
| `on_grid="true"` / `"TRUE"` / `"1"` / `"Tru"` | admitted as `False` | rejected against the two declared tokens |
| `T_degC="NaN"` / `"Infinity"` / `"-Infinity"` | admitted; cluster id contained `nan` | rejected as non-finite |
| `93.40004` vs `93.40005` | one condition (`%g`) | two conditions |
| `9.000004` vs `9.000005` | one condition | two conditions |
| held-out `on_grid=True`, no O counterpart | admitted, `lookup_defined=True` | `SourceContractError` |
| held-out `on_grid=False`, O counterpart present | admitted | rejected |
| duplicate O support | first row silently wins | rejected for want of a declared replicate rule |
| O counterpart present, analyte unusable | counted as support | not support |

Identity goes through `Decimal`; `float` appears only at the arithmetic boundary. `9` and `9.0`
still share one key — the behaviour `%g` was for, and got right.

Independence is preserved and now enforced: an AST check fails if the oracle ever calls the
production builder, the two analyte maps remain separately declared, and a mutation of one side
alone is still detected.

**Methods text added** to both manuscripts stating exactly what the contract does and does not
verify — "it does not independently verify transcription, unit correctness, or measurement accuracy
against the source publication" — because structural validation reads like source validation unless
the difference is written down.

### P1-5 — validator totality

`10**400` is valid JSON, is an `int`, passes every isinstance test, and raised `OverflowError` in
all six numeric interval fields, in both signs. Caught at the conversion boundary — in
`require_finite_number`, `_same_value`, and the status level/margin paths — never by wrapping a
caller in `except Exception`, which would hide real coding defects behind the same green result.

Matrix: 7 field paths × 13 malformed values (`10**400`, `-(10**400)`, `10**309`, `True`, `False`,
`None`, `"1.0"`, `""`, NaN, ±Inf, list, mapping) → **91 combinations, all returning named problems,
none raising.** Valid records still validate exactly.

### P1-6 — structural scanning

Replaced the two-regex pseudo-renderer with a CommonMark parse (`markdown-it-py`, declared as a
`submission` extra and added to the min-deps lane) and two channels: reader-visible text with
adjacent inline nodes joined, and a separate destination channel over inline links, reference
definitions, images, autolinks and raw `href`/`src` attributes, percent-decoded before path rules
see them.

All 18 reproduced bypasses now fail, on each of 5 upload deliverables (90 cases): `**version**`,
`<em>version</em>`, `ver**sion**`, `<b>ver</b>sion`, `&nbsp;`, `_version_`, table cells, list items,
block quotes, headings, inline and reference links, HTML `href`, percent-encoded targets,
footnotes, inline code, image destinations.

Scope now covers manuscript, supplement, cover letter, Highlights and standalone captions. Two file
exemptions remain, each with a written reason: the package (an assembly manifest whose file table is
its content) and the canonical draft (repository-facing, not uploaded). The fourteen-section path
allowance is **retired** and replaced by a structural exemption keyed to the unsupplied-metadata
placeholder itself, plus narrow allowlists for submitted figure filenames and public DOI links.

A missing parser **blocks** rather than returning clean, and that behaviour is itself tested.

### P2-1 — caption structure

Extraction now terminates at any level-1–3 heading or horizontal rule. Figure 4 ends at "…they
should not be pooled as equivalent validation." and the file carries exactly one
`## Supplementary figures` heading.

Validity is a **separate gate** from freshness: 4 main + 4 supplementary captions, one of each
section heading, one label per caption, no rule or heading marker in any body. `current ==
render()` proves the file was generated; it does not prove what was generated is well formed, which
is how the malformed caption passed for a whole round.

---

## 6. Producer-rerun decision — NOT REQUIRED

Per the plan's producer-rerun rule, `tools/paper_a_transfer_artifacts.py --write` was **not** run.
None of its triggers fired:

| Trigger | Status |
|---|---|
| source-corpus membership changed | **No** — 44 records / 132 observations; identical `held_out_sample_ids` and `train_sample_ids` |
| normalized partition or design hash changed | **No** — `manifest_sha256` and `included_sample_ids_sha256` byte-identical for both corpora; oracle census unchanged (26/44/78/6 clusters) |
| estimand changed | **No** |
| an archived result artefact changed or became invalid | **No** — `paper_a_transfer_artifacts.py --check` passes against the corrected contracts |
| a source/design correction altered a downstream calculation | **No** — the strict parser reproduces the same semantic corpus |
| artefacts unverifiable against corrected contracts | **No** |

**No schema or hash migration was required.** The lossless `Decimal` canonicalisation produces the
same strings as `%g` for every coordinate actually present (`88`, `93.4`, `98`, `6`, `9`, `12`), so
the partition keys and hashes are unchanged; the difference appears only for coordinates that would
previously have collided, of which the source contains none. `tools/paper_a_migrate_schema4.py`
reports *3 artefacts, no bound moved.*

---

## 7. Command table

Run against `7767a7b1bc9e` on 2026-07-30 (UTC), macOS / Python 3.13, `.[dev]` environment with
`pyyaml` and `markdown-it-py` present.

| Command | Exit | Status | Result |
|---|---:|---|---|
| `tools/paper_a_numerical_invariants.py --check` | 0 | **PASS** | every protected value unchanged |
| `tools/paper_a_transfer_artifacts.py --check` | 0 | **PASS** | artefacts OK |
| `tools/paper_a_transfer_text.py --check` | 0 | **PASS** | generated blocks fresh |
| `tools/paper_a_figure_captions.py --check` | 0 | **PASS** | 8 captions, structure valid and fresh |
| `tools/paper_a_consistency.py verify` | 0 | **PASS** | submission contract OK |
| `tools/paper_a_migrate_schema4.py` | 0 | **PASS** | 3 artefacts, no bound moved |
| `python -m puckworks.paper_a.claim_coverage` | 0 | **PASS** | 0 unaccounted numerals in **both** manuscripts |
| `python -m puckworks.paper_a.slow_lane_bindings` | 0 | **PASS** | 99/99 resolve and match |
| `tools/claim_binding_audit.py` | 0 | **PASS** | current at the final commit |
| focused suite (7 modules) | 0 | **PASS** | 764 passed |
| `python -m pytest -q` (full) | 0 | **PASS** | **3025 passed, 1 skipped** in 14 m 37 s |

The full-suite run was started at commit `df1406f` (17:46:38Z) and finished at 18:01:16Z with exit
code 0. The single skip is a pre-existing environment-gated case, not a check disabled by this work.

**Explicitly NOT RUN:**

* the ~25-minute PDE/science producer — deliberately, per §6;
* slow/GPU/live/external-data lanes, which are excluded from the default suite by marker and are
  unaffected by text and contract changes;
* a journal-width typesetting proof of Supplementary Table S7 and a pixel-level image diff of
  Figure 4 — the review's acknowledged presentation checks, carried forward unchanged;
* CI itself (this branch is unmerged).

No check in this table returned early or was skipped for a missing dependency. The one check that
*can* be environment-limited — the abstract-versus-YAML comparison without `pyyaml` — ran fully
here, and the structural scanner's not-run path is tested rather than assumed.

---

## 8. Human inspection

| Item | Status |
|---|---|
| Continuous-argument read: title → abstract → significance → Methods ranges → Table 4a → endpoint synthesis → S3 → Discussion → Conclusions → cover letter | Done — the five corrected paragraphs read as one argument; the observed result is prominent and every claim about it is two-sided |
| Standalone read of the Highlights file | Done — intelligible alone; states the observed direction and the limit |
| Standalone read of all eight captions | Done — Figure 4 ends at "equivalent validation."; one supplementary heading; Figure 3 stands alone with all four propositions |
| No review history, internal path, producer identifier, TODO or placeholder in upload deliverables | Done — scanner clean under the widened scope; raw grep clean |
| Reviewer sign-off that no surface says or implies "absent / equivalent / negligible" | Done — see §3 |
| Journal-width check of Supplementary Table S7 | **Not done** — carried forward (§7) |

---

## 9. Residual open items

Genuinely outside Round 11 remediation, carried forward:

1. The unrun fraction-versus-measured-cup contrast, the 11 unbound slow-lane values, the
   hand-sourced design settings, and the producer-internal `skill_vs_const` name — all explicitly
   out of scope for Round 11.
2. Unsupplied authorship/front-matter metadata, the novelty search, and the release DOI/tag —
   author and external actions, blocked by `--check-submission-ready` until resolved.
3. `docs/ANALYSIS_transfer.md`, `docs/PUBLIC_VALUE.md` and the public site carry the retired
   "adds little skill" phrasing. These are repository and product copy, outside the Paper 1
   submission surfaces the review scoped, and are **not** governed by the claim policy. They should
   be brought into line separately.

---

## 10. Commit map

| Commit | Findings |
|---|---|
| `341dbff` restore the evidence-bounded comparison claim | P0-1, P1-1 |
| `8938052` govern the standalone claim surfaces | P1-3 |
| `4a17e0c` bind inferential claims to verified evidence | P1-2 |
| `d22f73d` harden the source and numeric contracts | P1-4, P1-5 |
| `7767a7b` structurally validate submission markdown and captions | P1-6, P2-1 |

---

## 11. Post-merge self-check (30 July 2026)

After the remediation merged as `fae72c4`, the new gates were probed adversarially rather than
re-run. **Three found defects in the gates themselves.** None affected the paper's text — the phrase
sweep, `verify` and the numerical invariants were all clean throughout — but each was a live hole in
a check, which is the class of thing round 11 was about.

| # | Found | Why it matters | Fixed |
|---|---|---|---|
| 1 | **`VerifiedInferentialStatus` was forgeable.** An ordinary dataclass holding a decision map: hand-building one granted all four decisions with no verification having run | The same "typed rather than earned" error P1-2 identified, one type along. Only one call site constructing it correctly was a *convention* — the guarantee P1-2 rejected | Module-private construction token; `decision_flags` re-derives from the evidence on every read, so there is no stored verdict to tamper with |
| 2 | **Four scanner bypasses.** Fenced code blocks produced no visible text; raw HTML blocks kept their Markdown markers uninterpreted; soft hyphens and zero-width characters split a phrase invisibly; HTML comments were unscanned even in files uploaded verbatim | Each is a way to put review history or a repository path into a deliverable unseen | Fence and code-block tokens extracted; emphasis stripped after HTML-block tag removal; six invisible characters removed before matching; comment path-channel added for the two files the package uploads without conversion |
| 3 | **The magnitude taxonomy was thin.** Twenty *fresh* paraphrases — none from the review, none from the suite — were tried; **17 passed** | A keyword list catches what somebody thought of. This is exactly how the round-10 verdict returned | Six rule classes added, bringing it to **19 of 20**. The twentieth is left failing with a test pinning the fact, because the honest statement is the measurement, not a claim of completeness |

Closing (2) introduced a fifth defect — stripping emphasis markers globally removed the underscores
from `tools/paper_a_transfer_text.py`, so the internal-path rule stopped recognising its own target.
The existing leakage tests caught it before commit. It is recorded because "a fix opening another
hole" is the failure mode of the last four rounds, and it happened again inside one session.

One consequential editorial change: the upload-ready caption file's generation stamp named
`tools/paper_a_figure_captions.py`. That file is uploaded **exactly as it stands** — unlike the
manuscript, which is converted to `.docx` with "remove editorial notes" a listed step — so the
comment shipped. Same class as the two paths found on line 2 of the Highlights file, and fixed the
same way.

Re-verified after all of it: full chain PASS, 1100 Paper 1 tests pass, protected values unchanged,
0 unaccounted numerals in both manuscripts.
