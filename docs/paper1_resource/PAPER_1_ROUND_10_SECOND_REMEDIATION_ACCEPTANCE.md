# Paper 1 — Round 10 second review: acceptance evidence

**Prepared:** 30 July 2026
**Basis:** [`PAPER_1_ROUND_10_SECOND_DETAILED_REVIEW.md`](PAPER_1_ROUND_10_SECOND_DETAILED_REVIEW.md)
and its [implementation plan](PAPER_1_ROUND_10_SECOND_REMEDIATION_IMPLEMENTATION_PLAN.md)
**Reviewed snapshot:** `3b7fe7e` — the same pre-remediation commit the first round-10 review examined
**Branch:** `paper1/round10b-remediation`, on top of the first remediation (`6cf5e96`, PR #205)
**Numerical movement:** **none.** Every protected value is byte-identical to the frozen baseline.

---

## 1. Two independent reviews of one commit

This is a *second* review of `3b7fe7e`, by a reviewer working independently of the first. The two
agree exactly on the submission blocker and diverge usefully everywhere else:

| | first review | second review |
|---|---|---|
| **P0** | "no resolvable skill" is not licensed | **the same finding**, reached from the missing definition of *resolvable* rather than from the missing decision object |
| **P1** | estimand declared twice; interval validator checks 4 of 9 fields | **renderer bypasses the typed semantics layer**; **the oracle does not establish the observation universe** |
| **P2** | line-based publication scanner; mis-titled caption file | **Table S6 claims membership it does not show**; **ambiguous audited-bound referent**; **validators raise where they should report** |

Only the P0 overlapped. Of the second review's five other findings, the first remediation had closed
two by side effect (the oracle's `grinds`/census comparison, and non-finite interval bounds) and left
four open. Those four are actioned here.

That is worth recording on its own: two competent reviews of the same commit produced almost disjoint
non-blocking finding sets.

---

## 2. Disposition by finding

| Finding | State after PR #205 | Action here | Evidence |
|---|---|---|---|
| **P0-1** central verdict | Actioned (Path A) | Residue closed: the endpoint synthesis no longer opens "Two things follow, and they agree" or reads a zero-containing range as conceding no advantage; six close variants added to the claim policy | `test_paper_a_claim_policy.py` (84) |
| **P1-1** geometry authority | **Open** | `block_endpoint_reading` derives endpoint groupings from typed `ZeroRelation` via a new `group_by_relation`; AST guard over four renderer modules; contradictory-cache and all-relation tests | `test_paper_a_source_observations.py` (69) |
| **P1-2** observation universe | Partly closed (grinds, census) | Independent analyte→column map in the oracle; each retained cell required present/numeric/finite; observation ids built from validated cells; production admission rule reads the same columns through its own helper; manifest validator compares exact canonical labels; checker converts source-contract failures into named problems | 10 source mutations + 9 manifest mutations |
| **P2-1** Table S6 caption | **Open** | Caption now says cluster keys, strata, census, ranges and widths, and states where exact per-scheme membership lives | supplement assertions |
| **P2-2** audited bound | **Open** | "The **upper** bound's sign is stable across seeds", tied to `upper_bound_sign_is_stable`, plus an explicit note that no lower-bound flag is archived | supplement assertions |
| **P2-3** total validators | Partly closed (intervals) | `validate_endpoint_contract` returns named per-index problems instead of raising `ValueError`; `find_exact_audit` raises a contextual `KeyError` instead of `AttributeError` | 9 target + 6 audit parameterisations |

---

## 3. The finding that mattered most

The second review's P1-2 is the most valuable result of either round-10 review, because it is a
**common-mode** defect between two components built specifically to be independent.

`source_resampling_oracle` shares no grouping code with production — that was verified on the AST and
remains verified. But both it and `build_transfer_corpus_manifest` treated "every retained sample
record contributes three named-solute observations" as an axiom. Neither read `CF`, `TR` or `5CQA`.
The reviewer deleted all three scored columns from a copy of `bioactives.csv` and the oracle still
returned 44 records and 132 observations without raising.

The current committed source is complete — 44 held-out rows, all three analytes present, numeric and
finite in every one — so no published number was ever wrong. What was wrong was the assurance claim:
the chain could not have detected a missing analyte column, a blank cell, or a renamed analyte.

Both sides now read the columns, through **separately written** helpers (`ORACLE._scored_value` and
`TC._scored_solute_value`). A test asserts the two maps agree while a second asserts the oracle still
imports nothing from the contract — agreement is the check, independence is the mechanism.

Ten mutations, each naming the sample, the solute and the source column:

```
remove CF column        -> source CSV lacks required columns ['CF']
remove TR column        -> source CSV lacks required columns ['TR']
remove 5CQA column      -> source CSV lacks required columns ['5CQA']
blank CF cell           -> source observation A12|caffeine: column 'CF' is blank
blank TR cell           -> source observation A12|trigonelline: column 'TR' is blank
text in TR cell         -> source observation A12|trigonelline: column 'TR' is non-numeric ('n/a')
text in 5CQA cell       -> source observation A12|5CQA: column '5CQA' is non-numeric ('below LOD')
NaN in analyte cell     -> source observation A12|caffeine: column 'CF' is non-finite ('NaN')
+inf in analyte cell    -> source observation A12|caffeine: column 'CF' is non-finite ('inf')
-inf in analyte cell    -> source observation A12|5CQA: column '5CQA' is non-finite ('-inf')
```

And nine on the manifest side, where the validator previously compared only the *length* of each
record's solute list: a renamed label, a duplicated label, a reordering, a wrong `n_solutes`, a
per-record rename, a per-record duplicate, a per-record reorder, a non-list `records`, and a
non-mapping record. A relabelled record with a **refreshed hash** also fails, because a self-hash
proves only that someone remembered to rehash.

---

## 4. P1-1, and why one line mattered

`block_endpoint_reading` built its endpoint lists straight from the archived boolean:

```python
contains = [m for m, r in rows if interval(r)["contains_zero_full_precision"]]
excludes = [m for m, r in rows if not interval(r)["contains_zero_full_precision"]]
```

Two defects in three lines. The cached flag is a **second authority** for a fact the full-precision
bounds already determine, so a renderer invoked on an unvalidated or mutated record can publish
geometry the bounds contradict. And `not contains` collapses BELOW and ABOVE into one bucket — the
exact conflation round-9 P0-1 was about — which reads correctly today only because no Paper A range is
wholly positive.

Both are closed. `TS.group_by_relation` returns every relation key including empty ones, so a caller
cannot mistake "nothing above zero" for "I never handled above zero"; the AST guard covers four
renderer modules and is proven non-vacuous by a companion test asserting the contract may still read
the flags; and the contradiction mutation demonstrates the renderer following the bounds
(`excludes zero on the negative side at 38 g, 40 g and 42 g`) while the cache claims containment,
with the validator refusing the record outright.

The rendered sweep is unchanged for the real data: *excludes zero on the negative side at 38 g, and
contains zero at 40 g and 42 g.*

---

## 5. Command chain

```
python tools/paper_a_transfer_artifacts.py --check       OK
python tools/paper_a_transfer_text.py --check            OK
python tools/paper_a_figure_captions.py --check          OK
python tools/paper_a_consistency.py verify               OK
python tools/paper_a_numerical_invariants.py --check     OK  (every protected value unchanged)
python tools/paper_a_xref.py                             OK
python tools/paper_a_front_matter.py                     OK
python tools/paper_a_supplement.py                       OK
python -m puckworks.paper_a.slow_lane_bindings           OK  (99/99)
python -m puckworks.paper_a.claim_coverage               OK  (0 unaccounted, both manuscripts)
python tools/claim_binding_audit.py                      OK
python tools/paper_a_migrate_schema4.py                  OK  (idempotent)
python -m pytest -q                                      OK
```

Schema stays at **4**. The second review's plan asked for no bump unless persisted field meaning
changes, and nothing here changes a persisted field: the manifest's admission rule is stricter, its
output identical.

---

## 6. Where I did not follow the plan

**The plan asked for `SCHEMA_VERSION = 3`.** It was written against `3b7fe7e`, before the first
remediation bumped the schema to 4 for the typed estimand and inferential status. Schema 4 is
therefore the correct baseline here, and this change adds no persisted field at all.

**The plan's suggested abstract and endpoint wording differs from what is committed.** The first
remediation had already rewritten those surfaces from the other review's Path A. Both wordings satisfy
both reviews' acceptance criteria — observed advantage with its sign, uncalibrated ranges, no
decision, accuracy insufficient — so the committed text was kept and only the residue the second
review names specifically was changed. The `claim_policy` propositions are what enforce this, not the
sentences.

**Table S6's caption points at "the machine-readable endpoint-propagation record" rather than the
filename.** The plan suggested naming `PAPER_A_ENDPOINT_PROPAGATION.json`. That is an internal
repository path, and the publication scanner rejects those in submission-facing prose for the reasons
round-10 P2-1 established. The availability statement is where the deposit is named.

---

## 7. Out of scope, unchanged

The fraction-versus-measured-cup contrast, the 11 unbound slow-lane values, the ~255 hand-declared
design settings, author metadata and declarations, the novelty search, the release DOI, and final
typesetting including Table S7 at journal width. The second review also declines to re-report these.

Both reviews flag Table S7 and Figure 1 as needing a final-width proof. That is a production step at
release, not a content defect, and neither review counts it as a finding.
