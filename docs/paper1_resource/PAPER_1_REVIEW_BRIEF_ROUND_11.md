# Paper 1 — reviewer brief, round 11

**Manuscript:** `docs/submission/PAPER_A_JFE_MANUSCRIPT.md` (canonical working draft:
`docs/PAPER_A_DRAFT.md` — see §2 for what "held in agreement" now actually means, because last round
it did not mean what this brief said it did).
**Commit:** `6cf5e9638709831b76aefb583d711bf7161eeb7b` on `main` — the round-10 remediation merge
(PR #205). Earlier commits are **not** equivalent: the transfer artefact schema moved v3 → v4, the estimand became a typed object,
the interval validator was rewritten, and the caption deliverable was split in two.

**Supplement:** `docs/submission/PAPER_A_JFE_SUPPLEMENT.md` + `docs/submission/figures/`.
**Upload-ready captions:** `docs/submission/PAPER_A_JFE_FIGURE_CAPTIONS.md` (generated).
**Prior round:** `PAPER_1_ROUND_10_DETAILED_REVIEW.md`, its remediation plan, and our
`PAPER_1_ROUND_10_REMEDIATION_ACCEPTANCE.md` beside them.

This is a **single-paper review**. Papers B2 and 3 are out of scope.

---

## 1. What round 10 found, and the shape of the mistake

Round 10 found the stale-number category **empty for the second consecutive round**. What it found
instead was one submission blocker that had been sitting in the abstract of every version for
months, and which four rounds of review had read straight past — including, we suspect, because it
sounded like the opposite of overclaiming.

The paper said, correctly and prominently, that its ranges are fixed-predictor clustered percentile
**sensitivity** ranges with no calibrated coverage, and that it makes *"no claim of statistical
distinguishability, non-distinguishability or equivalence"* from them. It then concluded — in the
abstract, the editor significance paragraph, the principal Results headline, the endpoint synthesis,
the cover letter and the caption map — that the mechanistic model supplied **"no resolvable skill"**.

Absence of skill is a *decision*. The declared analysis makes no decision, in either direction. And
the point estimate actually favours the model: −0.394 pp at 40 g, every secondary scheme's range
wholly negative at all three endpoints, and the 38 g primary range excluding zero on the *favourable*
side. An uncalibrated range cannot establish that the model has reproducible incremental skill; the
same range cannot establish that it has none.

The lesson we take from it, and the one worth carrying into this round: **a cautious-sounding claim
is still a claim.** Our own assurance layers were built to catch overclaiming in the direction of
"the mechanism transfers". Nothing in them noticed a categorical verdict pointing the other way.

The three majors were all of one kind too — assurance code that described more than it did:

* the canonical draft and the venue manuscript carried **materially different active abstracts**
  ("not identifiable" vs "weakly separated"; "an incremental skill of only ≈4.5 % relative"; the
  kinetic structure "adds little beyond the transferred level") while CI called them content-aligned
  on the strength of a curated phrase list none of those differences touched — and claim coverage
  audited only the draft by default, so a green audit could certify an abstract no editor would see;
* favourability was declared **twice** — a free-text estimand sentence in the artefact and a
  module-level direction default in the renderer — so a reversed estimand left every favourability
  sentence unchanged with the validator and the oracle green;
* `validate_interval_record` checked four of nine stored fields, under `bool(...)` coercion. Because
  `bool(None)` is falsey and `bool("false")` is **true**, a deleted boolean field and the string
  `"false"` each coerced to whatever value the record needed to look consistent. Nine mutations were
  reproduced; all nine returned an empty problem list.

And the editorial finding was a false green in the scanner itself: the manuscript's *"An earlier
version of this paragraph… that was wrong"* survived because the scanner read **physical lines** and
the phrase was wrapped across three.

---

## 2. What changed since round 10

### The blocker

We took **Path A**: the paper now says what the analysis supports. The observed advantage is
reported with its sign, and the limit of the evidence is stated in the same breath.

The mechanism, not just the wording: a typed `InferentialStatus` object in the artefact declares
which decisions the analysis can make — for this analysis, **none**, with `practical_margin_pp: null`
— and `puckworks/paper_a/claim_policy.py` derives the prohibited phrase classes *from that object*.
So "no resolvable skill", "adds no skill", "unresolved throughout", "statistically indistinguishable",
"outperforms", "practically negligible" and their relatives cannot be reintroduced on any
reader-facing surface while no decision is declared — and would unlock automatically if a future
calibrated analysis declared one. Explicit disclaimers are recognised and permitted: the paper must
be able to say what it is *not* claiming.

The positive half is checked too. Four propositions make up the accepted claim, and each surface must
carry the ones assigned to it:

1. the observed pooled difference, with its sign;
2. the ranges are uncalibrated sensitivity ranges, not confidence intervals;
3. no superiority, equivalence or absence-of-skill decision is made;
4. acceptable endpoint accuracy alone does not establish mechanistic transfer.

Supplementary Table S3's undefined `skill` column became **relative pooled-MAPE reduction (%)**, with
its formula and its descriptive status in the table note, computed from full-precision pooled values
(4.98 / 4.42 / 4.76 %). Figure 3's panel (c) title — `pooled skill 4%`, an undefined quantity rounded
to zero decimals — became `relative pooled-MAPE reduction 4.4%`.

### The three majors

| | round-10 defect | now |
|---|---|---|
| **P1-1** | two active abstracts with different central claims, "held in agreement" by a phrase list | both render the **same abstract** from `paper_a_front_matter.yaml`; eight generated blocks are checked for exact normalised parity between the two files; claim coverage audits **both** manuscripts by default (0 unaccounted in each) |
| **P1-2** | estimand direction declared twice, renderer defaulted | one typed `EstimandSpec`; direction **derived** from metric preference × operand order; no renderer default (a missing estimand is a `TypeError`, not an assumption); the whole declared design exact-pinned; the source oracle widened to grinds, stratum counts, size distributions and a normalised-partition hash |
| **P1-3** | four of nine interval fields validated, under `bool()` coercion | every field required and exact-compared against a canonical record rebuilt from the bounds; bounds validated as finite JSON numbers (bool, str, `None`, NaN, ±inf rejected **before** classification); `bool(...)` coercion gone; malformed records return named problems and never raise |

Twenty-eight declared-design mutations now fail the checker, including every one round 10 reproduced.
Reversing the estimand in the artefact changes **five** generated blocks; before, it changed none.

### The editorial finding

The scanner reads **normalised visible paragraphs** with a map back to the first source line. HTML
comments are blanked while preserving line positions; Markdown link and image targets are reduced to
their visible text; internal runs of whitespace are collapsed. Every token-boundary wrap of a
prohibited phrase is tested, plus three-line splits, case and tab variation.

The file titled *"submission-ready figure captions"* — whose first three paragraphs were review
history, producer identifiers and a test path — is now two files. `docs/figures/PAPER_A_FIGURE_MAP_INTERNAL.md`
is repository bookkeeping and is **never uploaded** (and is deliberately excluded from the scanner:
it is *allowed* to hold what the scanner keeps out of the paper).
`docs/submission/PAPER_A_JFE_FIGURE_CAPTIONS.md` is **generated** from it, captions only, and is what
the package manifest lists.

### Schema 4, and why no producer was rerun

The artefacts moved v3 → v4 through `tools/paper_a_migrate_schema4.py`, which does **no** numerical
work: intervals are rebuilt by the canonical constructor from their own archived full-precision
bounds, and the resampling design is rebuilt from the source CSV with the migration aborting unless
the rebuilt membership is identical cluster-for-cluster to the committed one. It is idempotent, and
we verified it byte-identical on a second run — which is what makes "no number moved" re-checkable
rather than a claim you have to take from us.

A `--write` producer rerun would move Monte Carlo bounds in their last displayed digit for reasons
unrelated to this remediation, against a review that found the numerical work clean. We judged that a
worse trade. Argue with that if you disagree.

### One false green we shipped and CI caught

Worth telling you, because it is the third round running that our own new assurance layer has
returned one. The first version of the abstract-parity check called `paper_a_front_matter.load()` and
returned early on `ImportError`. pyyaml is a dev/radar extra, so on the minimum-dependency lane the
check did not run — and a canonical abstract mutated to say *"an incremental skill of ≈4.5 %
relative"*, the retired round-10 wording itself, passed there. The mutation test asserting that
failure is what surfaced it, on the one lane lacking the dependency.

The comparison is now two steps: the three rendered abstracts against each other (no parser needed),
then against the source where the environment allows, with the partial coverage RECORDED rather than
silently passing. Assume there are more of these. The pattern — a check that cannot run looking
identical to a check that ran and found nothing — has produced a finding in rounds 8, 9 and 10.

### What did not change

**No headline value moved**, and this time it is pinned rather than asserted:
`tools/paper_a_numerical_invariants.py` extracted every protected value from the artefacts *before*
any remediation edit and compares them exactly — no tolerance — on every run, with seven one-digit
mutation tests proving the ratchet bites.

| endpoint | model / comparator pooled MAPE | paired difference | full-precision primary range | zero relation | model worse on |
|---:|---|---:|---|---|---:|
| 38 g | 8.39 % / 8.83 % | −0.447 pp | `[−0.884387, −0.042433]` | excludes zero, negative side | 61/132 |
| 40 g | 8.44 % / 8.83 % | −0.394 pp | `[−0.829052, +0.003791]` | contains zero | 62/132 |
| 42 g | 8.41 % / 8.83 % | −0.425 pp | `[−0.891251, +0.005844]` | contains zero | 60/132 |

---

## 3. Explicitly out of scope — do not report these

| | |
|---|---|
| Author list, affiliations, corresponding author, ORCIDs | not yet supplied |
| CRediT roles, funding, competing interests, generative-AI declaration | not yet supplied |
| Licensed indexed novelty search | not yet run |
| Release DOI and archival tag | not yet minted |
| Working-draft repository note and the internal figure map | stripped at submission / never submitted |

`paper_a_consistency.py submission` reports blockers; all of them are the metadata above. No science
blocker remains. If you find one, that is a P0.

---

## 4. The chain, and how to test it rather than trust it

```bash
python tools/paper_a_numerical_invariants.py --check   # every protected value, exactly, no tolerance
python tools/paper_a_transfer_artifacts.py --check     # source→artefact: corpus manifest AND the full
                                                       # design, plus the typed estimand and status
python tools/paper_a_transfer_text.py --check          # artefact→publication: every generated block
python tools/paper_a_figure_captions.py --check        # internal map→upload-ready captions
python tools/paper_a_consistency.py verify             # submission contract, block parity, claim
                                                       # policy, paragraph scanner, endpoint science
python tools/paper_a_migrate_schema4.py                # idempotence of the v3→v4 migration
python -m puckworks.paper_a.claim_coverage             # BOTH manuscripts, by default
python -m puckworks.paper_a.slow_lane_bindings         # 99 bindings vs their archived runs
python tools/claim_binding_audit.py
python -m pytest tests/test_paper_a_claim_policy.py \
                 tests/test_paper_a_transfer_semantics.py \
                 tests/test_paper_a_transfer_contract.py \
                 tests/test_paper_a_numerical_invariants.py -q
python -m pytest -q                                    # full suite, ~15 min
```

To regenerate the science (~25 min of PDE solves, hand-run, never in CI):

```bash
python tools/paper_a_transfer_artifacts.py --write
```

---

## 5. What we are asking you to look for

### (a) The corrected claim, read as an argument

This is the highest-value target. Read title → abstract → significance paragraph → Methods'
description of the range → Results headline → Table 4a and its note → endpoint synthesis →
Supplementary S3 and its reading → Discussion → Conclusions → cover letter, as one continuous
argument, and ask:

- does any surface still make a decision the analysis cannot make — in **either** direction? We were
  looking for overclaiming toward "the mechanism transfers" and missed a categorical verdict pointing
  the other way, so please assume our blind spot is still there somewhere;
- have we now overshot the other way? Is there a place where the hedging has become so heavy that a
  reader cannot tell what we actually found? "The point estimate favours the model" is a real result
  and we do not want to bury it;
- is the distinction between *this analysis does not establish X* and *X is false* held consistently,
  or does it slip in a sentence we composed carelessly?
- is the relative pooled-MAPE reduction column now unambiguous, or does a defined descriptive ratio
  still read as an inferential quantity beside four percentile ranges?

### (b) The claim policy as a mechanism

It is new, and it is now the thing standing between us and a repeat.

- the prohibition is derived from a declared `InferentialStatus`. Is that the right locus, or does it
  just move the problem — a false status object would license false prose. What checks the status?
- disclaimers are permitted by looking back ~140 characters for a disclaiming phrase. That is a
  heuristic. Can you construct a sentence that asserts a verdict while carrying a disclaimer marker
  nearby, and get it past the scan?
- the four required propositions are assigned per surface. Are the assignments right — in particular,
  should the figure caption and the highlights carry more than they do?
- is there a decision class we have not enumerated at all? (Superiority, non-inferiority, equivalence
  and absence of skill are the four; "no worse than", "at least as good as", "comparable" are the
  kind of thing we may have missed.)

### (c) The estimand and design contract

- direction is now derived from `(metric_preference, operation)`. Is the derivation right in all four
  combinations, and is the *metric preference* itself stated anywhere a reader can check?
- the division of labour is deliberate: the contract pins authorial declarations (role, label,
  rationale), the independent oracle owns everything the source data determines. Is that boundary in
  the right place, or is there a field that belongs on the other side?
- the oracle now also compares a normalised-partition hash as a second signal after comparing
  content. Is that redundant, or does it earn its place?
- can you still get a scientifically wrong design through the full chain?

### (d) Interval records

- every stored field is now rebuilt and exact-compared, and unexpected fields fail. Is there a field
  we should have **removed** instead of validated?
- `display.touches_zero` split into exact `touches_zero_at_lower` / `touches_zero_at_upper` and
  `display.contains_zero_rounded`. Are those names now unambiguous to a reader of the JSON?
- we reject bool, str, `None`, NaN and ±inf before classification. Is there an input class still
  getting through?

### (e) The scanner, and the caption split

- the internal figure map is excluded from scanning by design. Is that exclusion safe, or have we
  just moved the upload risk somewhere a check no longer looks?
- the upload-ready caption file is generated. Does it read as a standalone caption set to an editor,
  or has generation stripped something a reader needed?
- can you get review history, a producer identifier or an internal path into a submission-facing file
  in a way the paragraph scanner misses? Table cells, list items and footnotes are the shapes we are
  least confident about.
- the internal-path rule applies only to the manuscript and the supplement, with the package and the
  canonical draft exempt because both are repository-facing by construction. Is that scoping
  defensible or convenient?

### Also welcome, lower priority

Supplementary Table S7's 44 rows still have not been proofed at journal width. `fig4_transfer.png`
was re-rendered for its panel-(c) title only.

---

## 6. Known open items — please do not re-report

1. **The fraction-versus-measured-cup rate-profile contrast has not been run.** The data supports
   it; the analysis is owed.
2. **11 of 104 registered slow-lane values remain unbound**, enumerated by
   `puckworks.paper_a.claim_coverage.binding_coverage()` (`still_unbound`). Not to be confused with
   the 99 binding *rules*, all of which resolve and match.
3. **~255 declared design settings** are single-sourced by hand rather than spliced. These are
   choices, not results.
4. **The producer's internal `skill_vs_const` field keeps its name.** It is bound to a registered
   claim and consumed by the public product surface; renaming it would ripple well outside Paper 1.
   No *published* surface uses undefined "skill" terminology any more. See §7 of the acceptance
   report.
5. **`docs/ANALYSIS_transfer.md`, `docs/PUBLIC_VALUE.md` and the public site still say "adds little
   skill over a level-only null."** Same overclaim class, different documents — product and
   repository copy, not Paper 1 submission surfaces. Scheduled for their own change with the site
   regenerated through its own gates. Recorded so you can see it was a decision.

Telling us these are still open is not useful. Telling us one of them is *wrong* is.

---

## 7. Settled against the source — reopen only with new evidence

Both archived in `PAPER_A_SOLVER_CONTRACT_AUDIT.json`:

- **Reynolds definition** — computed from the **superficial** velocity; a contract test recovers `Re`
  numerically from `Sh` to prove the displayed form is the evaluated one.
- **`flow` and density** — the source consumes its `flow` column as **mass flow in g/s** while
  labelling it mL/s, so the stopping rule returns a collected **mass** and the endpoints are
  38/40/42 **grams**.

Round 8 found the second correction had reached the science and not the release gate. If you are
inclined to check whether a "settled" item actually landed *everywhere*, that instinct has now paid
three times.

---

## 8. Format

Report findings as **P0 (submission-blocking) / P1 (major) / P2 (editorial)**, each with the evidence
relied on and a minimum acceptance criterion. Where you assert a number is wrong, say what you
compared it against.

If a finding is a **stale number**, say so explicitly. Two rounds running that category has been
empty; if it is non-empty again, the binding chain has regressed and we need to know.

**If you find nothing in a section, say so.** A round that returns fewer findings is informative only
if we can tell the difference between "checked and clean" and "not reached".

And if you conclude one of *our* corrections is wrong, say that plainly. It has happened in each of
the last three rounds — round 8's P2-1 was reported backwards, round 9's replacement wording
overshot, and this round we have rewritten the central conclusion of the paper on a reviewer's
argument. We would rather be told than have it stand.
