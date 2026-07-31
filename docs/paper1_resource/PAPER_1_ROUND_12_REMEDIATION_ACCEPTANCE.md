# Paper 1 — Round 12 Remediation Acceptance

**Prepared:** 31 July 2026
**Reviewed commit (input):** `4adbe4af6b6a4faa6b27c38f8aaf3dde01dc8a86`
**Controlling review:** `PAPER_1_ROUND_12_DETAILED_REVIEW.md`
**Probes:** `PAPER_1_ROUND_12_FOCUSED_PROBES.txt`
**Controlling plan:** `PAPER_1_ROUND_12_REMEDIATION_IMPLEMENTATION_PLAN.md`
**Branch:** `paper1/round12-remediation`

This report names each check and its status. It does not claim that all checks pass.

---

## 1. Disposition

All thirteen findings actioned: **1 P0, 8 P1, 4 P2.**

| ID | Finding | Disposition |
|---|---|---|
| P0-1 | Generator emits "the observed advantage is therefore small"; three more live constructions | **Closed** — fixed at source; generated blocks now scanned before insertion |
| P1-1 | Clause governance is not grammatical scope | **Closed** — complement-scoped spans; 9 fail, 15 pass |
| P1-2 | Taxonomy misses ordinary paraphrases and a hyphenated live construction | **Closed** — structural classes, hyphen-aware modifier run |
| P1-3 | Positive coverage is a substring test | **Closed** — affirmative-sentence requirement |
| P1-4 | `VerifiedInferentialStatus` forgeable via the importable sentinel | **Closed** — permission takes an identifier re-verified from production storage |
| P1-5 | Digests bind bytes, not semantics or chronology | **Closed** — interval parsed from the hashed result; predeclaration must be provable |
| P1-6 | Highlights omit the transfer boundary | **Closed** — 62-character bullet; all four propositions required |
| P1-7 | Float coercion destroys the coordinate token upstream | **Closed** — raw tokens preserved through the production loader |
| P1-8 | Three scanner leakage channels | **Closed** — all three |
| P2-1 | Caption validation discards the producer stem | **Closed** — stems retained and validated |
| P2-2 | Figure 3 is a 287-word mini-review | **Closed** — 203 words, no proposition dropped |
| P2-3 | Package contradicts itself about outstanding reruns | **Closed** — see §5 |
| P2-4 | Duplicated comparator-ladder phrase | **Closed** |

**Producer rerun: PERFORMED** (P1-7 changed the production source path). **No protected value moved.**

---

## 2. Protected numerical invariants — frozen before editing, unchanged after

Captured before any change (plan §2.1) and compared after the producer rerun:

| Endpoint | Model | Comparator | Difference | Primary full-precision range | Worse on |
|---|---:|---:|---:|---|---:|
| 38 g | 8.39 % | 8.83 % | −0.447 pp | [−0.8843868833200912, −0.04243254356196476] | 61/132 |
| 40 g | 8.44 % | 8.83 % | −0.394 pp | [−0.8290522506458629, +0.003790518393922992] | 62/132 |
| 42 g | 8.41 % | 8.83 % | −0.425 pp | [−0.8912505494092522, +0.005844468562594105] | 60/132 |

Corpus: 44 records / 3 solutes / 132 observations / 8 off-grid; matched-grid 36 / 108.
`manifest_sha256` and `included_sample_ids_sha256` identical for both corpora.
Cluster census unchanged: 26 / 44 / 78 / 6 clusters, 2 / 4 / 6 / 1 strata.

**Drift: NONE.**

---

## 3. P0-1 — before and after

| Surface | Before | After |
|---|---|---|
| Generated Results headline (`block_transfer_headline`) | "…**The observed advantage is therefore small**, and this analysis does not establish whether it is reproducible or practically useful" | "…a paired difference of **−0.394 percentage points**, which favours the mechanistic model. … **Because the reported ranges are uncalibrated and no practical margin was predeclared, this analysis does not establish that the observed advantage is reproducible or practically useful, and it does not establish that the advantage is absent**" |
| In-sample bridge paragraph | "…consistent with the **small held-out skill** above (this is a descriptive in-sample comparison…)" | "**This descriptive in-sample comparison is not a held-out test, and it does not adjudicate the magnitude, reproducibility or practical usefulness of the held-out difference** — nor is it proof that mechanism 'explains nothing'." |
| Endpoint propagation | "Because this difference is **only −0.394 percentage points** wide…" | "The model-minus-comparator difference at 40 g is **−0.394 percentage points, favouring the mechanistic model**." |
| Endpoint synthesis | "…the favourable extreme of these ranges lies **well under one percentage point**…" | "…the most favourable bound is **−0.891 pp** and the least favourable is **+0.006 pp**, so the least favourable extreme lies on the other side of zero." |

Two further instances the review did not list, caught by the new rules while implementing them:

* Table 2 row: "closes **only ~0.5 pp** — at matched mass the flow-map choice **barely matters**"
  → "closes **~0.5 pp** — … moves the residual by ~0.5 pp".
* §4: "a median of **only ~3 %** of the observation … grows **only modestly** across declared
  tolerances" → "a median of **~3 %** … grows from ~9.2 % to ~10.5 % for caffeine".

And one the review raised but did not count as the blocker: **"less than half a percentage point"**
is removed from every reader-facing surface. The review's assessment was that it is checkable but
"a rhetorically selected threshold with no declared practical meaning [that] adds little beyond the
exact number". Round 11 introduced it as the replacement for "small"; on reflection the reviewer is
right, and the exact signed value now stands in its place everywhere.

### Why the new wording is descriptive

Each replacement states a measured quantity and then the boundary of what follows from it. The
generator no longer assigns the difference to a relevance category at all: it reports −0.394 pp,
names the direction, and states symmetrically that neither reproducibility/usefulness nor absence is
established. The result is not buried — the signed point estimate remains on every load-bearing
surface, and the manual read in §7 records that.

### The generated/authored boundary

The review found the defect on **both** sides and judged the boundary unreliable. Generated text is
now scanned **before insertion** (`scan_rendered_blocks`), so a prohibited verdict fails where it is
produced, names the block, and never reaches a file. Reverting the generator sentence in a scratch
copy reproduces the block:

```
generated block 'paper-a:transfer-headline' would emit prohibited claim language:
  [magnitude_of_the_contrast] <<advantage is therefore small>> presupposes a predeclared
  practical margin, which this analysis does not support
```

---

## 4. Finding-by-finding evidence

### P1-1 — complement scope

`find_non_establishment_spans` returns `NonEstablishmentSpan(start, end, construction)` covering the
frame's **complement**, ending at a terminator, `;`, `:`, a dash, a contrastive **or causal**
conjunction (`because`, `meaning`, `implying`), an appositive continuation, or a comma opening a new
finite clause. All 9 review false-negatives fail; all 8 review false-positives (plus 7 existing
disclaimer fixtures) pass.

One incidental defect found while doing it: `nonetheless` was in the clause-boundary list, so
"the observed advantage is **nonetheless** small" was split into "…is" and "small" and neither half
matched — a boundary word creating the bypass it was added to close. Conjunctive adverbs are now
boundaries only where they actually join clauses.

### P1-2 — structural classes

`has_no_value`, `no_better_than`, `magnitude_of_the_contrast`, `evaluative_quantity`, plus a bounded
hyphen-aware modifier run (`_MOD`) and a shared adjective set (`_MOD_ADJ`) bound to value nouns. All
9 review paraphrases fail. Controls that must remain legal — `small positive upper bound`, `a small
sample`, `a small held-out sample`, `a tiny numerical tolerance`, `matched records`, `no practical
margin was predeclared`, `the held-out error stays modest` — all pass.

### P1-3 — affirmative propositions

`Assertion.present_in` now requires the phrase to occur in an **asserting sentence**. Quotations,
code spans and HTML comments are removed; sentences carrying local negation, wording instructions,
conditional antecedents or reported speech are excluded. The review's three counterexamples plus a
reported-speech variant all now report the propositions missing; the real Highlights and Figure 3
caption still report none missing.

The prohibitive scanner deliberately keeps the **opposite** policy on quotation: a dangerous verdict
inside quotation marks still ships to a reader.

### P1-4 / P1-5 — permission and evidence

* `claim_policy.granted()` takes an `InferentialStatus` (grants nothing) or an
  `InferentialEvidenceReference`, re-verified from `PRODUCTION_EVIDENCE` at the point of use. A
  `VerifiedInferentialStatus` — however constructed — now raises.
* The decisive interval is parsed from the hashed result (`_result_problems`); the evidence record's
  copy must equal it exactly. The reviewer's detached-result probe fails.
* Predeclaration requires `predates_result: true` plus named protocol/result commits
  (`_chronology_problems`). The post-result-protocol probe fails.
* Empty `cluster_unit`, `required_estimand_id`, `implementation_id`, procedure id/version and rule
  ids no longer register.
* `verify_inferential_evidence_for_test` is the only path taking a caller-supplied registry.
* "Unforgeable" is retired from the documentation.

`PRODUCTION_EVIDENCE` and `PROCEDURE_REGISTRY` both ship **empty**, which is Paper A's actual state.

### P1-6 — Highlights

Bullet 5 replaced with "Endpoint accuracy alone did not establish mechanistic transfer" (62 chars,
shorter than the 70-char partly-redundant bullet it replaces). `SURFACE_ASSERTIONS["highlights"]`
now requires all four propositions. Bullet lengths: 68 / 73 / 75 / 63 / 62, all ≤ 85.

### P1-7 — raw coordinate identity

`puckworks.data` rows are now `TypedRow`, a dict subclass carrying `raw_tokens` as an **attribute**
— invisible to `keys()`, `items()` and iteration, so every existing consumer is unaffected.
`source_schema.parse_row` parses identity columns from the token, but **only while token and typed
value agree**: a disagreement means one of the two was rewritten, and preferring the stale half
would be a fresh way for a value and its description to drift apart.

End-to-end through the production loader, `93.4000400000000001` and `93.4000400000000002` now
produce distinct cluster ids; so do `10.0000000000000001` and `...02`.

### P1-8 — three channels

* **Raw HTML:** quoted *and* unquoted attributes, plus `srcset` (candidate-list aware), `poster`,
  `data`, `cite`, `action`, `longdesc`, `background`, `xlink:href`. All six review examples extract.
* **Verbatim comments:** every leakage class, not only the path rule, with an exact generator-stamp
  grammar (`_is_generator_stamp`) as the sole exemption.
* **Metadata exemption:** scoped to the placeholder **sentence** (bounded by `.` + whitespace, so a
  path's dots do not truncate it) plus one exact approved tracking reference. Both review bypasses
  fail; the genuine declarations blocks still pass.

### P2-1 / P2-2 / P2-4

Producer stems retained through extraction and validated against `EXPECTED_STEMS`, with duplicate,
unknown, missing and mismatched-stem detection. Figure 3 reduced 290 → **203 words** using a
generated `limits_sentence_short` renderer — a renderer, not a paraphrase, so a future analysis that
earns a decision cannot keep emitting either form. Required content retained: 44, 132, 8.44 %,
8.83 %, −0.394, 62 of 132, all four propositions. The duplicated parenthetical now names the ladder's
members.

---

## 5. P2-3 — the package contradiction, resolved on the evidence

The review asked us to decide whether conversion item 2 named completed work or an outstanding
analysis, and to escalate if the latter could change the conclusions.

**It is neither, and that is why it read as a contradiction.** Per
`PAPER_A_P0-5_UNCERTAINTY_SCOPE.md` and `MANIFEST_UNCERTAINTY.md`: the three named solutes carry
**no per-cell RSD** in the Angeloni source — only global ranges — so a solute-specific weighted
refit is **blocked pending a replicate drop from the Angeloni authors**. The adopted fallback,
recorded at the time, is a descriptive sensitivity analysis across plausible weighting schemes, with
the calibrated named-solute interval left explicitly owed.

So the work is complete *as scoped*, and the calibrated version is *not performable*. Item 2 now says
that, cites the scope document, and explains what it previously said and why that was ambiguous.
**No escalation:** the blocked analysis cannot change the figures or the conclusion, because the
conclusion is already stated as descriptive and evidence-limited.

---

## 6. Producer rerun — required, performed, and what it moved

P1-7 changed the production source-loading path, so the plan (§5.4) requires the science producer to
run rather than reasoning that it need not.

```
python tools/paper_a_transfer_artifacts.py --write
start 2026-07-31T21:47:38Z   end 2026-07-31T22:13:37Z   exit 0   (25 m 59 s)
```

Compared against the pre-rerun snapshot and the frozen baseline:

| Compared | Result |
|---|---|
| Source manifest hash | unchanged |
| 44/132 and 36/108 membership | unchanged |
| Off-grid count (8) and lookup observations (108) | unchanged |
| Cluster ids, counts (26/44/78/6) and strata (2/4/6/1) | unchanged |
| All protected endpoint values and full-precision ranges | unchanged |
| Manuscript numbers | unchanged |

**The only diff in three artefacts was `"schema_version": 3 → 4`** — a stale stamp predating the
round-10 migration, refreshed by the rerun. It is excluded from `manifest_sha256`, which is computed
over the records. Regenerating the text blocks propagated the same stamp into the two manuscripts;
no rendered number changed.

That is the outcome the change predicted: preserving a token that was previously discarded cannot
alter a corpus whose tokens never needed it.

---

## 7. Manual submission-surface read (plan §5.5)

Read in the prescribed order. For each surface: observed result and direction, range type, decision
boundary, transfer boundary, absence of magnitude verdicts.

| # | Surface | −0.394 & direction | Range type | Decision boundary | Transfer boundary | Magnitude verdict |
|---|---|---|---|---|---|---|
| 1 | Title | n/a | n/a | n/a | frames measurement limits | none |
| 2 | Abstract | ✔ signed, favouring model | uncalibrated sensitivity | ✔ symmetric | ✔ | none |
| 3 | Editor significance | ✔ 0.394 pp | uncalibrated, no margin | ✔ | ✔ | none (round-11 "small observed gain" already removed) |
| 4 | Methods, ranges | n/a | ✔ named, not CI | ✔ | n/a | none |
| 5 | Results headline | ✔ signed + 62/132 | ✔ not a CI | ✔ symmetric | ✔ | **removed this round** |
| 6 | Table 4a + note | ✔ all three endpoints | ✔ | ✔ descriptive column | n/a | none |
| 7 | Endpoint synthesis | ✔ bounds by endpoint | ✔ | ✔ symmetric | ✔ | **removed this round** |
| 8 | Supplementary S3 + reading | ✔ | ✔ | ✔ | n/a | none |
| 9 | Discussion (four properties) | ✔ signed | ✔ | ✔ symmetric | ✔ | none |
| 10 | Conclusions / strength ladder | ✔ signed | ✔ | ✔ | ✔ | none |
| 11 | Cover letter | ✔ | ✔ | ✔ | ✔ | none |
| 12 | Highlights | ✔ 0.394 lower | ✔ uncalibrated | ✔ | ✔ **added this round** | none |
| 13 | Figure 3 caption | ✔ signed + 62/132 | ✔ | ✔ | ✔ | none; 203 words |

Three editorial defects introduced by my own P0 edits were found by this read and corrected before
commit: the headline restated "favours the mechanistic model" twice, the endpoint synthesis restated
−0.891 pp twice, and the standing position still carried "less than half a percentage point".

Read as one argument, the paper reports a model-favouring observed difference prominently and
states, at every load-bearing surface, that the analysis decides nothing in either direction. The
result is not buried.

---

## 8. Command table

Run at the final commit, macOS / Python 3.13, `.[dev]` with `pyyaml` and `markdown-it-py`.

| Command | Exit | Status | Result |
|---|---:|---|---|
| `tools/paper_a_numerical_invariants.py --check` | 0 | **PASS** | every protected value unchanged |
| `tools/paper_a_transfer_artifacts.py --write` | 0 | **PASS** | 25 m 59 s; only `schema_version` moved |
| `tools/paper_a_transfer_artifacts.py --check` | 0 | **PASS** | |
| `tools/paper_a_transfer_text.py --check` | 0 | **PASS** | incl. pre-insertion claim scan |
| `tools/paper_a_figure_captions.py --check` | 0 | **PASS** | 8 captions, stems validated |
| `tools/paper_a_consistency.py verify` | 0 | **PASS** | |
| `tools/paper_a_migrate_schema4.py` | 0 | **PASS** | no bound moved |
| `python -m puckworks.paper_a.claim_coverage` | 0 | **PASS** | 0 unaccounted, both manuscripts |
| `python -m puckworks.paper_a.slow_lane_bindings` | 0 | **PASS** | 99/99 |
| `tools/claim_binding_audit.py` | 0 | **PASS** | |
| `pytest tests/test_paper_a_round12_probes.py` | 0 | **PASS** | 77 probes |
| `pytest -k paper_a` | 0 | **PASS** | 1179 tests |
| `python -m pytest -q` (full) | 0 | **PASS** | **3157 passed, 1 skipped** in 14 m 45 s |

The full-suite run started at 22:15:32Z and finished at 22:30:18Z with exit code 0, at the
regenerated state. The single skip is a pre-existing environment-gated case, not a check this
work disabled.

**Explicitly NOT RUN:**

* Supplementary Table S7 at journal width (plan §5.6) — no journal-width rendering exists; carried
  forward, as in round 11.
* Slow/GPU/live/external-data lanes (marker-excluded, unaffected).
* CI (branch unmerged at the time of writing).

---

## 9. Round-12 probes as permanent regressions

`tests/test_paper_a_round12_probes.py` — 77 tests, one per reviewer counterexample, added **before**
any behaviour changed. Sections map to the probe file: live wording, copy-edit mutations, ordinary
paraphrases, clause governance both directions, active-surface cleanliness, positive-coverage
polarity, the importable sentinel, empty procedure semantics, detached result, post-result protocol,
production-loader coordinate identity, six HTML destinations, verbatim comments, metadata exemption,
caption length, producer stems, duplicated phrase.

---

## 10. Residual open items

Carried forward from round 11 and not re-reported by round 12:

1. The unrun fraction-versus-measured-cup contrast.
2. 11 of 104 registered slow-lane values unbound.
3. ~255 hand-sourced design settings.
4. The producer-internal `skill_vs_const` name.
5. `docs/ANALYSIS_transfer.md`, `docs/PUBLIC_VALUE.md` and the public site still say "adds little
   skill" — product and repository copy, not Paper 1 submission surfaces, not governed by the claim
   policy.
6. The unused `import re` in `tools/paper_a_transfer_text.py`.

New, and stated rather than hidden:

7. **The calibrated named-solute uncertainty interval remains blocked** on a replicate drop from the
   Angeloni authors (§5). This is a data-availability constraint, not an analysis debt.
8. **The prohibitive taxonomy remains incomplete by construction.** Round 11 measured it at 19/20 on
   fresh paraphrases; round 12 found nine more it missed. The structural classes added this round
   cover the classes rather than the sentences, but a finite phrase list cannot prove prose is safe
   — which is why the load-bearing defences are now generated central text, pre-insertion scanning,
   and proposition-level positive coverage.
