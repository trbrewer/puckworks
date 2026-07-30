# Paper 1 — reviewer brief, round 12

**Manuscript:** `docs/submission/PAPER_A_JFE_MANUSCRIPT.md` (canonical working draft:
`docs/PAPER_A_DRAFT.md`).
**Commit:** `4adbe4a` on `main` — the round-11 remediation (PR #209) **plus the post-merge
self-check** (PR #211), which closed three defects in the new gates themselves. Review this commit,
not the remediation merge: §2 and §5 describe the gates as they stand after #211, and at `fae72c4`
three of the things this brief says are fixed are not.

Earlier commits are **not** equivalent at all: the claim scanner's disclaimer logic was rewritten,
decision permissions moved from a declared flag to a derived one, the source contract gained a
schema module, and the submission scanner now parses Markdown structurally and needs
`markdown-it-py`.

**Supplement:** `docs/submission/PAPER_A_JFE_SUPPLEMENT.md` + `docs/submission/figures/`.
**Upload-ready captions:** `docs/submission/PAPER_A_JFE_FIGURE_CAPTIONS.md` (generated).
**Prior round:** `PAPER_1_ROUND_11_DETAILED_REVIEW.md`, its implementation plan, and our
`PAPER_1_ROUND_11_REMEDIATION_ACCEPTANCE.md`.

This is a **single-paper review**. Papers B2 and 3 are out of scope.

---

## 1. What round 11 found, and why it matters more than its severity count suggests

Round 11 found the stale-number category **empty for the third consecutive round**. The numerical
chain is not where the risk is.

What it found instead was that the round-10 blocker had **come back**. Round 10 retired the
conclusion that cross-grind prediction "adds little", and by round 11 the same *decision* was on five
reader-facing surfaces in different words — "adding little", "incremental skill over a level-only
comparator is small" (three times), "nearly matched" — while the claim scanner built to prevent
exactly that reported **zero problems on both manuscripts**.

Two independent defects produced that false green, and the pair is worth stating plainly because it
generalises:

1. **The rule set had no class for the thing.** The taxonomy was built around absence, equivalence,
   distinguishability and superiority. A *practical-magnitude* verdict — "small", "little",
   "marginal" — was not any of those, so the paraphrase needed no bypass at all. It simply walked
   through a gap.
2. **The disclaimer heuristic rewarded the shape a careful paper produces.** Any of `neither`,
   `without`, `is not`, `are not`, `not a`, `reserve` within the preceding 140 characters suppressed
   a match. So *"We do not claim equivalence; the model is equivalent to the comparator"* — which is
   self-contradictory — returned clean, and so did *"The ranges are not confidence intervals. The
   model outperforms the comparator."* A limitations sentence followed by an overstrong conclusion is
   the most natural paragraph in scientific writing, and it was the one the scanner could not see.

The other six findings share a family resemblance, and it is the same one round 10 and round 9
found: **a mechanism that describes more than it does.** `InferentialStatus` was presented as the
authority that would unlock decision language for a future analysis; it checked only that the
declaration was internally coherent, so a hand-written status naming an *"invented future procedure"*
validated clean and unlocked equivalence prose. `_visible_text` was documented as "what a reader
sees" and was two regular expressions, so `**version**` and `<em>version</em>` were invisible to it.
`validate_interval_record` promised in its own docstring that it never raises, and raised
`OverflowError` on a valid JSON integer. The caption generator's output was certified by comparing it
to the generator.

**The lesson we are carrying into this round:** when this repository claims an assurance property,
test the property, not the intent. That instruction has produced a finding in every round since 8.

---

## 2. What changed since round 11

### The claim (P0-1)

Every property-level magnitude verdict is replaced by the observed contrast plus a **symmetrical**
decision boundary. At 40 g: pooled MAPE 8.44 % against 8.83 %, a model-minus-comparator difference of
−0.394 pp favouring the model, with uncalibrated fixed-predictor ranges and no predeclared practical
margin — so the analysis establishes **neither** a reproducible or practically useful advantage
**nor** its absence.

"Less than half a percentage point" replaces "small" wherever a magnitude is described. The
distinction we are relying on: the first is a measurement anyone can check against Table 4a; the
second is a comparison against a threshold of relevance that nobody declared. Please push on whether
we have actually held that line, or merely relocated the same judgement into a phrase that sounds
more quantitative.

The observed result is **more** prominent than the adjective it replaced, not less. Over-correction
was a real risk here and we would rather you told us we had overshot than that we buried a finding.

### The mechanism (P1-1)

Six rule classes added — `adds_little`, `small_incremental_value`, `nearly_matched`,
`essentially_same`, `within_noise`, `no_practical_advantage` — each scoped to the increment itself,
so "a small positive upper bound", "a small sample", "records were matched by variety" and "no
practical margin was predeclared" stay legal.

Disclaimer suppression is now **clause-scoped**: a non-establishment construction governs from where
it starts to the end of *its* clause, and sentence ends, semicolons, colons, dashes, contrastive
conjunctions (`but`, `however`, `yet`) and a new coordinated subject all end a clause. Fourteen
reproduced false greens fail; nineteen genuine disclaimers still pass. The five retired sentences are
pinned **verbatim** and re-tested by injection into an actual upload file — because the round-11
finding was that they were in the shipped manuscript while `verify` printed clean.

### The other six

| | round-11 defect | now |
|---|---|---|
| **P1-2** | `InferentialStatus` was coherent self-attestation; a fabricated status naming an "invented future procedure" unlocked equivalence prose, and a JSON array in `confidence_procedure` was accepted via `str()` | New `puckworks/paper_a/inferential_evidence.py`. Decisions are **derived** by re-applying a registered procedure's rule to the observed interval, over hash-bound procedure/result/source/estimand/margin-protocol records. `claim_policy.granted()` returns the empty set for a declared status whatever its flags say. The registry ships **empty** |
| **P1-3** | The Highlights file and Figure 3's caption are uploaded separately and were governed only by the *prohibitive* half of the policy, so each could get materially stronger by **omission** | Both are positive-coverage surfaces; both regenerated. The highlight says "Observed pooled error was 0.394 points lower" and a fifth bullet carries the boundary |
| **P1-4** | Production and the oracle share no code and still shared four *premises*: `" Arabica "` silently excluded a record, `on_grid="true"` became False, `T_degC="NaN"` reached cluster ids, `%g` merged 93.40004 with 93.40005 | New `source_schema.py` is one declarative authority. Coordinates are exact `Decimal`s with a lossless canonical form; lookup support is **derived** from usable optimal-grind rows and reconciled against `on_grid` rather than copied from it |
| **P1-5** | `10**400` is valid JSON, is an `int`, and raised `OverflowError` in all six numeric interval fields | Caught at the conversion boundary — not by a blanket `except Exception`, which would hide real coding defects. 91 malformed combinations return named problems; none raise |
| **P1-6** | The scanner could not see through emphasis, inline HTML, entities or split words, and discarded every link **target**; scope covered 2 of 5 upload deliverables | CommonMark parse (`markdown-it-py`) plus a separate destination channel over links, reference definitions, images and HTML attributes, percent-decoded. 18 bypasses × 5 deliverables fail |
| **P2-1** | Figure 4's caption had absorbed `--- ## Supplementary figures`, certified because the upload file exactly equalled its generator's **malformed** output | Extraction stops at any level-1–3 heading or horizontal rule; **validity is a separate gate from freshness** |

### What the new gates caught that round 11 did not list

Four, and we are reporting them rather than absorbing them into the counts, because each was live at
the reviewed commit and each is a data point about coverage:

1. **`editor_significance` said "only a small observed gain"** — rendered into the package, the cover
   letter and the canonical draft. Our *first* draft of the magnitude rule missed it, because
   "observed" sat between the adjective and the noun. The rule now tolerates intervening modifiers.
2. **Manuscript §4: "while its small advantage over a comparator changes sign."**
3. **The canonical draft's figure-mapping table: "a small observed gain".**
4. **The uploaded Highlights file named two repository paths on line 2** — plain text, not even
   inside a comment. Invisible only because `internal_path` was scoped to the manuscript and
   supplement.

Item 1 is the one worth dwelling on: a rule written to catch a defect missed a live instance of that
same defect on its first attempt. Assume the same is true of the rules as they now stand.

### One test we inverted on purpose

`test_an_internal_path_in_a_data_availability_section_is_allowed` asserted a section-scoped path
allowance covering fourteen sections — data availability, reproducibility, figure captions, the
declarations. P1-6 retires it, and it was genuinely too broad: every path in an upload deliverable
was in fact inside an *unsupplied-metadata placeholder*, so a real leak in an availability statement
would have been legal. The exemption is now keyed to the placeholder structurally, and the test
asserts the opposite of what it used to. If you think we removed a legitimate allowance, say so.

### What did not change

**No number moved, no producer was rerun, and no schema or hash migration was required.** The
lossless `Decimal` canonicalisation produces the same strings as `%g` for every coordinate the source
actually contains, so both corpora reproduce byte-identically — 44 records / 132 observations and
36 / 108, identical membership, identical `manifest_sha256`. The difference appears only for
coordinates that *would* previously have collided, of which the source has none.

| endpoint | model / comparator pooled MAPE | paired difference | full-precision primary range | zero relation | model worse on |
|---:|---|---:|---|---|---:|
| 38 g | 8.39 % / 8.83 % | −0.447 pp | `[−0.884387, −0.042433]` | excludes zero, negative side | 61/132 |
| 40 g | 8.44 % / 8.83 % | −0.394 pp | `[−0.829052, +0.003791]` | contains zero | 62/132 |
| 42 g | 8.41 % / 8.83 % | −0.425 pp | `[−0.891251, +0.005844]` | contains zero | 60/132 |

`tools/paper_a_numerical_invariants.py` compares every one of these exactly — no tolerance — on every
run, with mutation tests proving the ratchet bites.

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
pip install -e ".[dev]"                                # markdown-it-py is now required by the scanner

python tools/paper_a_numerical_invariants.py --check   # every protected value, exactly, no tolerance
python tools/paper_a_transfer_artifacts.py --check     # source→artefact
python tools/paper_a_transfer_text.py --check          # artefact→publication
python tools/paper_a_figure_captions.py --check        # structure AND freshness, separately
python tools/paper_a_consistency.py verify             # submission contract, parity, claim policy,
                                                       # structural scanner, endpoint science
python tools/paper_a_migrate_schema4.py                # idempotence of the v3→v4 migration
python -m puckworks.paper_a.claim_coverage             # BOTH manuscripts, by default
python -m puckworks.paper_a.slow_lane_bindings
python tools/claim_binding_audit.py
python -m pytest tests/test_paper_a_claim_policy.py \
                 tests/test_paper_a_inferential_evidence.py \
                 tests/test_paper_a_source_schema.py \
                 tests/test_paper_a_submission_scanner.py \
                 tests/test_paper_a_transfer_semantics.py \
                 tests/test_paper_a_transfer_contract.py \
                 tests/test_paper_a_numerical_invariants.py -q
python -m pytest -q                                    # full suite, ~15 min
```

To regenerate the science (~25 min of PDE solves, hand-run, never in CI):

```bash
python tools/paper_a_transfer_artifacts.py --write
```

Our last full run: **3025 passed, 1 skipped, exit 0.**

---

## 5. What we are asking you to look for

### (a) The corrected claim, read as an argument — highest value

Read title → abstract → significance paragraph → Methods' description of the ranges → Results
headline → Table 4a and its note → endpoint synthesis → Supplementary S3 and its reading → Discussion
→ Conclusions → cover letter → Highlights → Figure 3 caption, as one continuous argument.

- **Is the magnitude language actually fixed, or relocated?** We replaced "small" with "less than
  half a percentage point" and "−0.394 pp". Does *"less than half a percentage point"* still smuggle
  in a relevance judgement, given no margin defines what would count as a lot?
- **Have we overshot?** Three rounds of correction in this area is enough to have flattened the
  result. The point estimate favours the model and we do not want that buried under caveats. Is there
  a surface where a reader now cannot tell what we found?
- Is the distinction between *this analysis does not establish X* and *X is false* held consistently,
  in **both** directions, in every sentence — including ones we composed by hand rather than
  generated?
- Round 10 and round 11 both found the blocker in ungenerated narrative while the generated blocks
  were correct. Which paragraphs are still hand-authored, and does the boundary between generated and
  authored text fall in a sensible place?

### (b) The claim policy, second attempt

It has now failed once in service. The current version is a rewrite, not a patch, but treat it as
unproven.

- **Clause splitting is a deterministic heuristic, not a parser.** Boundaries are sentence
  terminators, `;`, `:`, dashes, contrastive conjunctions and `, and <determiner>`. Can you construct
  a sentence where a disclaimer legitimately governs across one of those, so we now produce a **false
  positive**? Or the reverse — a verdict that stays inside a disclaimer's clause and should not be
  covered by it?
- **The taxonomy is known to be incomplete, and we can tell you by how much.** After the remediation
  merged we tried twenty *fresh* paraphrases against it — none from the review, none from our own
  suite. **Seventeen passed.** We then added six rule classes, which brings it to 19 of 20; the
  twentieth ("the two predictors are much of a muchness") is left failing on purpose, with a test
  pinning that fact, because a keyword list catches what somebody thought of and pretending
  otherwise is how this defect recurred in the first place. Assume the same is true of the list as
  it now stands. The load-bearing defence is meant to be the positive assertion contract and
  generated text; **tell us if the phrase list is doing more work than it should.**
- The safe constructions are a fixed list of verb phrases. Is there an ordinary way to disclaim
  something that is not on it, and would therefore be flagged?
- **Double negation, quotation, and reported speech.** We deliberately do not exempt quotation marks.
  Is that right?
- Does the positive half (four propositions, assigned per surface) now cover the right surfaces, and
  are the assignments right? Figure 3 carries all four; the Highlights file carries three because 85
  characters per bullet is a real constraint. Is dropping the transfer boundary from the Highlights
  defensible, or is that the same omission failure one level down?

### (c) The evidence-bound inferential status

This is the largest new mechanism and the one with the least service history.

- The chain is: registered procedure → evidence record → recompute every digest → **derive** the
  decision → `VerifiedInferentialStatus`. Does that actually remove the trusted boolean, or does it
  move the trust to whoever writes the procedure registration?
- **We already found one instance of it moving rather than going.** As first merged,
  `VerifiedInferentialStatus` was an ordinary dataclass holding a decision map, so hand-building one
  granted all four decisions with no verification having run — the same "typed rather than earned"
  error the finding was about, one type along. It now requires a module-private construction token
  and re-derives its flags from the evidence on every read. Look for the next instance.
- The registry is **empty**, and the positive path is exercised only by a test-only synthetic
  procedure. Is proving the unlock path against a fixture sufficient, or is an empty registry with an
  untested-in-anger unlock mechanism a liability of its own?
- Digests bind an artefact to a claim *within this workflow*. We say so explicitly — it is not
  protection against someone who rewrites code and evidence together. Is that boundary stated where a
  reader would need it?
- The practical margin must be bound to a protocol digest that is not the result. Is that a real
  predeclaration guarantee or a paper one?
- `predictors_refitted_within_draw` is now the registered procedure's requirement rather than a
  universal ban. Is the fixed-predictor rule still enforced where it matters?

### (d) The source contract, third attempt

Round 10's second review found a common mode here; round 11 found four more, one layer up. Assume
there is a fifth.

- The declarative schema is now **shared** between production and the oracle, deliberately — one
  authority for what a row *is*, while membership, analytes, clusters, strata and the census stay
  written twice. Is that the right line, or have we just moved the common mode into the schema?
- We reject leading/trailing whitespace rather than stripping it, on the grounds that a controlled
  transcribed source should not be silently repaired. Defensible or pedantic?
- `lookup_defined` is now derived from actual optimal-grind support and reconciled against `on_grid`,
  with a mismatch raising rather than overwriting either side. Is raising right, or should one side
  win?
- The support set is built from **all** valid optimal-grind rows, while `train_sample_ids` remains the
  18 on-grid ones. Both derivations give the same answer on this source. Is the distinction between
  "an O record exists here" and "this is a calibration-grid condition" drawn correctly?
- We validate structure, tokens, finiteness, parseability and support. We do **not** validate
  transcription, units or plausibility against Angeloni et al. (2023), and the Methods now says so.
  Is that sentence in the right place and strong enough?

### (e) The submission scanner and the caption set

- The scanner now depends on `markdown-it-py`, and **blocks** rather than passing when it is absent.
  Is a hard dependency on a Markdown parser the right call for a repository whose core is
  numpy/scipy, and is the not-run path genuinely blocking everywhere it needs to be?
- Two channels: visible text, and destinations. Can you still get review history, a producer
  identifier or an internal path into an upload deliverable? **Four holes were found by probing this
  after it merged**, all now closed and all worth knowing about because they say what kind of thing
  slips through: a **fenced code block** produced no visible text at all; inside a **raw HTML block**
  the parser does not interpret Markdown, so `<div>An earlier **version** was wrong.</div>` kept its
  asterisks and no rule matched; a **soft hyphen or zero-width space** inside a word defeated every
  phrase rule while being invisible on the page; and **HTML comments** were unscanned even in the two
  files the package manifest uploads verbatim. Closing the second of those introduced a fifth —
  stripping emphasis markers globally ate the underscores out of `paper_a_transfer_text.py` — which
  the existing leakage tests caught. Assume there is a sixth.
- The comment channel is scoped to the two files uploaded **without conversion**; the manuscript,
  package and cover letter are converted to `.docx`/`.tex` with "remove editorial notes" a listed
  step, so their generator stamps never ship. Is that scoping right, or is it convenient?
- The path exemptions are now two files (the package, the canonical draft) plus a structural
  unsupplied-metadata exemption. Read the exemption reasons and say whether either is convenient
  rather than principled.
- Caption **validity** is checked separately from freshness. Are the invariants the right ones, or is
  there a malformed caption set that satisfies all of them?
- Does the standalone caption file read as a caption set to an editor? Figure 3's caption grew
  considerably this round.

### (f) Anything the above does not cover

Round 10's two independent reviews of one commit were **almost disjoint** outside the blocker. One
careful pass finds roughly half of what two find. So the sections above are a starting point, not a
boundary — a finding outside all of them is worth more than a confirmation inside one.

### Also welcome, lower priority

Supplementary Table S7's 44 rows still have not been proofed at journal width.

---

## 6. Known open items — please do not re-report

1. **The fraction-versus-measured-cup rate-profile contrast has not been run.** The data supports it;
   the analysis is owed.
2. **11 of 104 registered slow-lane values remain unbound**, enumerated by
   `puckworks.paper_a.claim_coverage.binding_coverage()` (`still_unbound`). Not to be confused with
   the 99 binding *rules*, all of which resolve and match.
3. **~255 declared design settings** are single-sourced by hand rather than spliced. These are
   choices, not results.
4. **The producer's internal `skill_vs_const` field keeps its name.** It is bound to a registered
   claim and consumed by the public product surface. No *published* surface uses undefined "skill"
   terminology.
5. **`docs/ANALYSIS_transfer.md`, `docs/PUBLIC_VALUE.md` and the public site still say "adds little
   skill over a level-only null."** Same overclaim class, different documents — product and
   repository copy, not Paper 1 submission surfaces, and not governed by the claim policy. Scheduled
   for their own change with the site regenerated through its own gates. Recorded so you can see it
   was a decision rather than an oversight.
6. **`tools/paper_a_transfer_text.py` carries an unused `import re`.** Pre-existing, outside CI's
   lint scope, left alone to keep this branch's diff to the remediation.

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

If a finding is a **stale number**, say so explicitly. Three rounds running that category has been
empty; if it is non-empty again, the binding chain has regressed and we need to know.

**If you find nothing in a section, say so.** A round that returns fewer findings is informative only
if we can tell the difference between "checked and clean" and "not reached".

And if you conclude one of *our* corrections is wrong, say that plainly. It has happened in each of
the last four rounds — round 8's P2-1 was reported backwards, round 9's replacement wording overshot,
round 10 rewrote the central conclusion of the paper on a reviewer's argument, and round 11 found
that rewrite undone by paraphrase. The most useful thing you can tell us is that a fix we are pleased
with does not work.
