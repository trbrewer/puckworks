# Paper 1 — Round 10 remediation: acceptance evidence

**Prepared:** 29 July 2026
**Basis:** [`PAPER_1_ROUND_10_DETAILED_REVIEW.md`](PAPER_1_ROUND_10_DETAILED_REVIEW.md) and
[`PAPER_1_ROUND_10_REMEDIATION_IMPLEMENTATION_PLAN.md`](PAPER_1_ROUND_10_REMEDIATION_IMPLEMENTATION_PLAN.md)
**Reviewed snapshot:** `3b7fe7e` (code identical at `af0f4f0`, which added only the round-10 brief)
**Branch:** `paper1/round10-remediation`
**Scientific route:** **P0-1 Path A** — correct the central claim to match the analysis already performed
**Numerical movement:** **none.** Every protected value is byte-identical to the frozen baseline.

---

## 1. Disposition by finding

| Finding | Resolution | Principal changes | Tests | Mutation evidence | Manual check | Status |
|---|---|---|---|---|---|---|
| **P0-1** central claim | Path A: evidence-limited conclusion on every surface, enforced by a typed inferential-status contract | `puckworks/paper_a/claim_policy.py` (new), `transfer_semantics.InferentialStatus`, `paper_a_front_matter.yaml`, `tools/paper_a_transfer_text.py`, `tools/paper_a_front_matter.py`, `puckworks/figures_paper_a.py` | `tests/test_paper_a_claim_policy.py` (75) | 12 retired verdicts prohibited; 7 disclaimers still permitted; status-driven unlock proven | abstract → significance → Methods → headline → Table 4a → endpoint synthesis → supplement → Discussion → Conclusions → cover letter read as one argument | **PASS** |
| **P1-1** one source of truth | Draft abstract generated from the same front matter as the venue abstract; structural block parity; claim coverage audits both manuscripts by default | `tools/paper_a_front_matter.py`, `tools/paper_a_consistency.py`, `puckworks/paper_a/claim_coverage.py`, `docs/PAPER_A_DRAFT.md` | parity + drift tests in `test_paper_a_claim_policy.py` | 4 drift mutations fail (negation flip, sign flip, missing marker, duplicate marker); a non-source abstract fails | both abstracts diffed; both audits reported | **PASS** |
| **P1-2** estimand + design bound | Typed `EstimandSpec` with derived direction, no renderer default; whole declared design exact-validated; oracle widened to grinds, strata, counts, distribution, hash | `transfer_semantics.py`, `transfer_contract.py`, `source_resampling_oracle.py`, `tools/paper_a_transfer_artifacts.py` | `test_paper_a_transfer_semantics.py` (143) | 28 declared-design mutations fail; 5 renderer blocks change when the estimand reverses | Methods, Table 5, Table S6 and the S3 reading read for sign | **PASS** |
| **P1-3** interval records | Strict finite-number validation, exact zero-contact fields, canonical rebuild and deep compare, no `bool()` coercion | `transfer_contract.interval_record` / `validate_interval_record`, `transfer_semantics.require_finite_number` | `test_paper_a_transfer_contract.py` (98) | all 9 reproduced false greens fail, plus 16 further invalid-primitive and contradictory-field cases | rendered `[−0.829, +0.004]` and the `+0.0038` bound inspected | **PASS** |
| **P2-1** publication hygiene | Draft-history sentence replaced; internal figure map split from generated upload-ready captions; paragraph-aware scanner with rule classes and line mapping | `tools/paper_a_consistency.py`, `tools/paper_a_figure_captions.py` (new), `docs/figures/PAPER_A_FIGURE_MAP_INTERNAL.md` (renamed), `docs/submission/PAPER_A_JFE_FIGURE_CAPTIONS.md` (new) | `test_paper_a_claim_policy.py` §4 | every token-boundary wrap of a prohibited phrase fails (11 splits); 10 leakage classes caught; comment and image-target negatives hold | upload-ready caption file read end to end | **PASS** |

---

## 2. Command chain

Run on the branch head, clean tree:

```
python tools/paper_a_transfer_artifacts.py --check       OK
python tools/paper_a_transfer_text.py --check            OK
python tools/paper_a_figure_captions.py --check           OK
python tools/paper_a_consistency.py verify                OK
python tools/paper_a_numerical_invariants.py --check      OK  (every protected value unchanged)
python tools/paper_a_xref.py                              OK
python tools/paper_a_front_matter.py                      OK  (0 drifted; abstract 240 words)
python tools/paper_a_supplement.py                        OK
python -m puckworks.paper_a.slow_lane_bindings            OK  (99/99 resolve and match)
python -m puckworks.paper_a.claim_coverage                OK  (0 unaccounted, BOTH manuscripts)
python tools/claim_binding_audit.py                       OK
python tools/paper_a_migrate_schema4.py                   OK  (idempotent; no bound moved)
python -m pytest -q                                       OK
```

`python tools/paper_a_consistency.py submission` still fails, as it must: the author metadata,
competing-interest statement, generative-AI declaration, novelty-search record and release DOI are
unresolved. That is the release gate doing its job, and none of it is in round-10 scope.

---

## 3. Numerical preservation

`docs/paper1_resource/PAPER_A_ROUND10_NUMERICAL_INVARIANTS.json` was written from the committed
artefacts **before** any remediation edit and is compared field by field on every run. The comparison
is exact — no tolerance — because a wording and validator remediation moves nothing.

Preserved and re-verified: 8.39/8.44/8.41 % model pooled MAPE, 8.83 % comparator, −0.447/−0.394/−0.425 pp
paired differences, 61/62/60 of 132 model-worse counts, all twelve full-precision scheme range bounds,
the 0.000520/0.000466 pp Monte Carlo standard errors, the corpus manifest and included-ID hashes, and
all four schemes' cluster counts, stratum counts, size distributions and membership hashes.

One field changed deliberately and is recorded as such: the estimand identity moved from the
pre-migration shim value `pre_schema4_free_text` to `pooled_mape_model_minus_level_only_pp`. That is
the typing of a sentence, not the movement of a number, and the migration tool reports it explicitly
rather than tolerating it silently.

Two values now **appear** in the supplement that did not before, and neither is a new result: the
relative pooled-MAPE reduction column (4.98 / 4.42 / 4.76 %) is computed from the already-archived
full-precision pooled MAPEs, replacing the undefined `skill` column of 0.051 / 0.045 / 0.048.

---

## 4. Schema 4 and how the artefacts were migrated

The three transfer artefacts moved from schema 3 to schema 4 **without re-running any producer**, via
`tools/paper_a_migrate_schema4.py`:

* every interval record was rebuilt by the canonical constructor **from its own archived
  full-precision bounds**, so no bound moved and every derived field is what those bounds imply;
* the resampling design was rebuilt from the source CSV through the contract's grouping functions,
  and the migration aborts unless the rebuilt membership is identical, cluster for cluster, to the
  committed one;
* the ambiguous `display.touches_zero` became `display.contains_zero_rounded`, with the flat aliases
  renamed to match, and exact `touches_zero_at_lower` / `touches_zero_at_upper` fields added.

The tool is idempotent and was verified byte-identical on a second run, which is what makes its
"no number moved" claim re-checkable rather than a one-time assertion.

A `--write` producer rerun (~25 min of PDE solves) was deliberately **not** performed. It would move
Monte Carlo bounds in their last displayed digit for reasons unrelated to this remediation, against a
review that found the numerical work clean.

---

## 5. What the paper now says

The accepted core claim, and the propositions every surface must carry, are data in
`puckworks.paper_a.claim_policy.ASSERTIONS` / `SURFACE_ASSERTIONS`:

1. the observed pooled difference, with its sign (−0.394 pp, favouring the mechanistic model);
2. the reported ranges are uncalibrated sensitivity ranges, not confidence intervals;
3. no superiority, equivalence or absence-of-skill decision is made;
4. acceptable endpoint accuracy alone does not establish mechanistic transfer.

Retired from every reader-facing surface: "no resolvable skill", "adding no resolvable skill", "did
not supply resolvable skill", "no resolvable gain", "unresolved throughout the declared tolerance",
"barely outperformed", "barely beats even this", "the model beats it", and §4's heading claim that
cross-grind prediction "adds little". Each is now prohibited by a rule keyed to the decision it
presupposes, so it cannot return while the declared status supports no decision — and would unlock
automatically if a future calibrated analysis declared one.

Explicit disclaimers are deliberately still permitted. The paper must be able to say "we make no
claim of statistical distinguishability, non-distinguishability or equivalence", and the scanner
recognises that sentence rather than pushing the authors toward silence about their own limits.

---

## 6. Round-10 items checked clean, and preserved

Regression-tested, not assumed: the trinary zero relation with separate exact-contact flags; the
lower bound as the favourable extreme under model-minus-comparator loss; the 40 g upper bound as
small and positive rather than in contact with zero; the multi-seed audit scoped to 40 g /
`cond_in_variety` / primary loss with separate lower and upper standard errors; endpoint rows failing
closed across 14 mutations; exact source membership for all four schemes; Figure 1's colour/style
encodings and Figure S3 panel (b)'s neutral bars.

Figure 3's panel (c) title changed — `pooled skill 4%` (an undefined quantity, rounded to zero
decimals) became `relative pooled-MAPE reduction 4.4%` — and `fig4_transfer.png` was re-rendered.
The render is byte-reproducible in this environment, verified by re-rendering the unmodified figure
first, so the image diff is confined to that title.

---

## 7. Deliberately out of scope

Unchanged, and not reopened: the fraction-versus-measured-cup rate-profile contrast, the 11 unbound
slow-lane values, the ~255 hand-sourced design settings, author metadata, funding, competing
interests, the generative-AI declaration, the novelty search, the release DOI/tag, and final
typesetting including Table S7's journal-width layout.

Two scoping decisions worth stating plainly, because both could otherwise look like omissions:

* **The producer's `skill_vs_const` field keeps its name.** It is an internal identifier bound to a
  registered claim and consumed by the public product surface (`puckworks/public/claims.py`,
  `flat_valley.py`, `paper_a/build.py`, the PV-03 data file). Renaming it would ripple well outside
  Paper 1 for no reader-facing gain. What the review asked for — that no *published* surface use
  undefined "skill" terminology — is done: the Supplementary Table S3 column, its table note and the
  Figure 3 panel title are all corrected.
* **`docs/ANALYSIS_transfer.md`, `docs/PUBLIC_VALUE.md` and the public site still say "adds little
  skill over a level-only null".** These are product and repository documents, not Paper 1
  submission surfaces, and the round-10 scope is explicitly single-paper. They carry the same
  overclaim class and should be corrected in their own change, with the public site regenerated
  through its own gates. Recorded here so the next round can see it was a decision, not an oversight.

---

## 8. One defect this remediation introduced, and where it was caught

The first version of the abstract-parity check called `paper_a_front_matter.load()` and returned
early on `ImportError`. pyyaml is a radar/dev extra, so on the minimum-dependency CI lane the check
did not run — and a canonical abstract mutated to say *"an incremental skill of ≈4.5 % relative"*,
which is the retired round-10 wording itself, passed there. The mutation test asserting that failure
is what surfaced it, on the one lane that lacks the dependency.

This is the same shape as the defects round 10 reported: a check that cannot run looking exactly like
a check that ran and found nothing. The comparison is now two steps — the three rendered abstracts
against each other (no parser needed), then against the source where the environment allows — and the
partial coverage is recorded in `abstract_source_unavailable` rather than passing silently. The test
now stubs `__import__` for `yaml`, so the minimum-dependency behaviour is exercised on every lane.

Recorded here rather than quietly fixed, because "our own new assurance layer returned a false green"
has now been a finding in three consecutive rounds and the pattern is worth naming.

---

## 9. Commits

| # | commit | purpose |
|---|---|---|
| 1 | `5a04f08` | Freeze the accepted numbers: invariants tool, artefact, 7 one-digit mutation tests |
| 2 | `61cc30c` | All five findings: schema 4 with the typed estimand and inferential status, full design binding, strict interval records, the migration, the Path A claim policy and prose, one abstract source with block parity, and the paragraph-aware scanner with the caption split |
| 3 | `73652bc` | The abstract-parity check no longer goes silent without pyyaml (see §8) |

The plan asked for six separable commits. Commit 2 is not separable in the way the plan assumed: the
generated files — manuscript, draft, supplement, package, cover letter, captions — each carry both a
schema-4 stamp and corrected claim prose, so any split leaves an intermediate tree where
`--check` fails. Given the repository's rule that gates stay green between commits, one complete
commit with a message covering all five findings was the honest option.

---

## 10. The five questions the review said a re-review should ask

1. **Does every central surface use the analysis-limited conclusion?** Yes, and a status-derived
   policy blocks the alternative on the manuscript, draft, supplement, package, cover letter,
   highlights, upload-ready captions and the front-matter source.
2. **Are canonical and venue manuscripts materially aligned?** Yes. One abstract source, structural
   parity over eight generated blocks, dual claim coverage by default, four drift mutations failing.
3. **Can a reversed estimand or false design metadata still pass the full chain?** No. 28 declared-design
   mutations fail, and reversing the estimand changes five renderer blocks rather than none.
4. **Can a contradictory interval field or invalid bound still pass validation?** No. All nine
   reproduced false greens fail, along with booleans, numeric strings, NaN, infinities, missing and
   extra fields.
5. **Does the scan catch line-wrapped history and internal paths in every upload-facing file?** Yes,
   at every token boundary, in normalised visible paragraphs, with the internal map explicitly
   excluded because it is allowed to hold what the scanner keeps out of the paper.
