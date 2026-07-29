# Paper 1 — reviewer brief, round 10

**Manuscript:** `docs/submission/PAPER_A_JFE_MANUSCRIPT.md` (canonical working draft:
`docs/PAPER_A_DRAFT.md` — the two are held in content agreement by CI).
**Commit:** `3b7fe7e10ee9989b380c70e40894d74b8ca2d8a5` on `main`. Earlier commits are **not** equivalent: the transfer
artefact schema, the interval-semantics layer, the endpoint row contract and the resampling
provenance check all changed in PR #203.

**Supplement:** `docs/submission/PAPER_A_JFE_SUPPLEMENT.md` + `docs/submission/figures/`.
**Prior round:** `PAPER_1_ROUND_9_DETAILED_REVIEW.md`, with its remediation plan beside it.

This is a **single-paper review**. Papers B2 and 3 are out of scope.

---

## 1. What round 9 found, and why it matters more than the numbers

Round 9 found **no stale number anywhere** — the first round in five where that category was empty.
What it found instead was worse: **current, correct numbers rendered into false sentences.** Seven
findings, and every one of them was introduced by the round-8 remediation that was supposed to make
the paper more trustworthy.

The two that should shape how you read this round:

**A boolean was doing the work of four different facts.** The generator computed

```python
same_side = (base["interval"]["contains_zero_full_precision"]
             == alt["interval"]["contains_zero_full_precision"])
```

and rendered `True == True` as *"both lie on the same side of zero"* — of two intervals that both
**contain** zero. The same code would have said it of one wholly negative and one wholly positive
interval, since both give `False == False`. Downstream, the conclusion and cover letter described a
`+0.0038 pp` upper bound as *"reaching zero at its upper bound"*, and Supplementary S3 attributed
the *"largest advantage"* to an **upper** bound although the estimand is model-minus-comparator loss,
so negative favours the model and the **lower** bound is the favourable extreme.

**Two named assurance layers returned false greens.** The endpoint contract was guarded by
`if isinstance(rows, list) and rows and KEY in rows[0]`, so deleting `rows`, emptying it, or removing
the key from every row all returned a clean bill of health. And the artefact checker carried a
comment claiming resampling membership was rebuilt from the source — while comparing only cluster
counts and a self-hash. Swapping one solute between two sample records passed everything.

Round 9 reproduced both before reporting them. So did we, before fixing them.

---

## 2. What changed since round 9

### The two blockers

| | round-9 defect | now |
|---|---|---|
| **P0-1** | interval geometry and bound favourability misrendered across Results, conclusion, supplement and cover letter | new `puckworks/paper_a/transfer_semantics.py` types the four facts separately: trinary `ZeroRelation`, exact-contact flags, favourability from a declared `EstimandDirection`, and audit scope |
| **P0-2** | the abstract called the 40 g bound's side "unresolved at the precision this resampling attains" while the Results and the archived audit put it ~8.1 Monte Carlo SE above zero | the abstract now separates **numerical sign stability**, **endpoint sensitivity of the zero relation**, and **absence of calibrated coverage**; `paper_a_consistency` fails if prose and the archived flag disagree **in either direction** |

The zero relation is now trinary because a boolean cannot distinguish "wholly below" from "wholly
above". `describe_shared_relation` names the relation rather than asserting a shared side, and it is
parameterised in tests over both-contain, both-below, both-above and mixed geometries — so a
renderer cannot be correct at 40 g and false at 38 g.

### The three majors

**P1-1** Schema **v3** replaces the single top-level `stability_audit` scalar with a
`stability_audits` list keyed by exact target. `find_exact_audit` fails on zero matches, fails on
multiple matches, and never falls back. Both bound standard errors are now reported separately
(0.000520 and 0.000466 pp) rather than as one symmetric ±0.0005, and Table 4a carries a dagger
scoping them to the single audited row. The 38 g and 42 g bounds, the three secondary schemes and
the alternative fitting loss are stated as **not separately audited**.

**P1-2** Endpoint rows fail closed. Fourteen mutations — missing, empty, non-list, keyless in first
/ middle / last row, duplicate, extra, non-dict, non-finite, non-numeric, retired key in any row —
all produce named failures. Malformed input is *reported*, never raised.

**P1-3** New `puckworks/paper_a/source_resampling_oracle.py` parses `bioactives.csv` with
`csv.DictReader` and reconstructs all four partitions from the scheme definitions. It is
**deliberately a second implementation**: it does not import `transfer_contract` and does not call
`cluster_key_of`, `stratum_key_of`, `cluster_membership`, `scheme_design` or `resampling_design` —
asserted on the parsed AST, because the module docstring names those functions in order to explain
why it avoids them. Comparison is exact, cluster by cluster, stratum by stratum.

### The editorial pair

**P2-1** Draft-history narration, internal `docs/` paths in the Results narrative, "already in the
repo", a review-ticket identifier and a generator self-description are gone from reader-facing
prose. The process scan now covers the **supplement and the standalone captions** — it described
itself as covering "every file a reviewer or editor could receive" while omitting both — strips HTML
comments before scanning, and has patterns for `earlier draft`, `round-\d+`, `already in repo` and
backticked `docs/` paths, with an allowlist for the availability and metadata sections where naming
a file *is* the content.

**P2-2** Figure 1's seven evidence categories now carry unique `(colour, line style)` pairs, with
patch legend handles so the style is visible in the key and survives grayscale — `insample` and
`within` were both plain blue, two legend entries with one encoding. Figure S3 panel (b)'s
undocumented `r > 0.4` / `r < 0` colour rule is replaced by a single neutral colour plus the zero
line, since signed bar length already carries the information and the thresholds implied
significance classes that were never computed.

### One thing the oracle caught that nobody had reported

Building the independent oracle surfaced a real inconsistency we had shipped: a late round-8 refactor
changed the `cond_in_group`/`group` cluster-id delimiter *after* the artefacts were written, so the
committed ids and the current production code disagreed. Membership sets were identical; only the id
spelling differed. Normalised to the pipe form and regenerated.

### What did not change

**No headline value moved.** 8.44 % / 8.83 %, −0.394 pp, worse on 62 of 132, and all three
full-precision primary ranges reproduce round 9's independently computed values to six decimals:

| endpoint | full-precision primary range | zero relation |
|---:|---|---|
| 38 g | `[−0.884387, −0.042433]` | excludes zero on the negative side |
| 40 g | `[−0.829052, +0.003791]` | contains zero |
| 42 g | `[−0.891251, +0.005844]` | contains zero |

---

## 3. Explicitly out of scope — do not report these

| | |
|---|---|
| Author list, affiliations, corresponding author, ORCIDs | not yet supplied |
| CRediT roles, funding, competing interests, generative-AI declaration | not yet supplied |
| Licensed indexed novelty search | not yet run |
| Release DOI and archival tag | not yet minted |
| Working-draft date and internal review-history prose | stripped at submission |

`paper_a_consistency.py submission` reports blockers; all of them are the metadata above. No science
blocker remains. If you find one, that is a P0.

---

## 4. The chain, and how to test it rather than trust it

```bash
python tools/paper_a_transfer_artifacts.py --check   # source→artefact: rebuilds the corpus manifest
                                                     # AND the full resampling partition from the CSV
python tools/paper_a_transfer_text.py --check        # artefact→publication: every generated block
python tools/paper_a_consistency.py verify           # submission contract, endpoint science,
                                                     # process language, prose-vs-audit agreement
python -m puckworks.paper_a.slow_lane_bindings       # 99 bindings vs their archived runs
python tools/claim_binding_audit.py                  # fails if its own inputs moved under it
python -m pytest tests/test_paper_a_transfer_semantics.py \
                 tests/test_paper_a_transfer_contract.py \
                 tests/test_paper_a_model_contract.py \
                 tests/test_paper_a_figure_semantics.py -q
python -m pytest -q                                  # full suite, ~15 min
```

To regenerate the science (~25 min of PDE solves, hand-run, never in CI):

```bash
python tools/paper_a_transfer_artifacts.py --write
```

`tests/test_paper_a_transfer_semantics.py` holds 49 contracts including the 14 endpoint-row
mutations and 5 membership mutations. Each one corresponds to a defect that shipped.

---

## 5. What we are asking you to look for

### (a) The semantics layer itself

It is new, and it is now the single point of failure for every claim about interval geometry. Attack
it directly:

- is the trinary relation the *right* decomposition, or is there a fifth fact still being inferred?
- `contains_zero` uses a closed-interval convention, so a bound of exactly 0.0 counts as containment
  with a separate `touches_zero_at_*` flag. Is that the right convention to publish, and is it
  applied consistently?
- `EstimandDirection` is a declaration, not something derived. If it were wrong, every favourability
  statement would invert silently. Is it stated where a reader can check it?
- does any renderer still infer geometry or favourability locally instead of asking the module?

### (b) The audit-scope discipline

We chose the review's **Path A** — scope the existing audit rather than run new ones. So the paper
now says the 38 g, 42 g, secondary-scheme and alternative-loss Monte Carlo precisions are unknown.

- Is that honest, or does it leave a reader unable to judge the endpoint sensitivity at all?
- We retained three decimals with an explicit resolution caveat, following round 9's own argument
  against coarsening to two. Argue us down if the caveat does not carry that weight.
- Does any sentence still imply the audit covers more than one target?

### (c) The oracle's independence

Two implementations of the same partition is deliberate duplication. That has a cost:

- could the oracle and production drift such that the *oracle* is the wrong one?
- the oracle hard-codes an `EXPECTED_CENSUS` as a documented cross-check while treating exact
  membership as the authority. Is that hierarchy right, or does the hard-coded census risk becoming
  the thing that gets "fixed" when the data legitimately changes?
- is there a partition error both implementations would make?

### (d) Generated prose, read as prose — again

This was the highest-value target last round and remains so. The numbers are bound; the sentences
around them are built by string concatenation that no test evaluates for meaning. Round 9 found six
such defects. **We found and fixed three more during our own review pass this round** — a
"both … both" duplication from composing relation prose, a `±0.0005` that survived the split into two
standard errors, and an "advantage is −0.394 pp" that paired a favourable word with a negative number
without stating the convention.

We also caught something worth telling you plainly: **one of our P0-1 fixes silently did not
apply.** The patch script aborted on an assertion before writing, and our own phrase sweep passed
because we ran it before regenerating. We found it only by reading the rendered output against an
audit sheet. Assume, therefore, that a phrase we claim to have retired may still be present, and
check the rendered files rather than our description of them.

### Also welcome, lower priority

Supplementary Table S7 now contains 44 rows with pipe-delimited cluster ids escaped for Markdown;
it parses as a clean 8-column table but has not been proofed at journal width. Figure 1 and Figure
S3 were re-rendered.

---

## 6. Known open items — please do not re-report

1. **The fraction-versus-measured-cup rate-profile contrast has not been run.** The data supports
   it; the analysis is owed.
2. **11 of 104 registered slow-lane values remain unbound**, enumerated by
   `puckworks.paper_a.claim_coverage.binding_coverage()` (`still_unbound`). Not to be confused with
   the 99 binding *rules*, all of which resolve and match.
3. **~255 declared design settings** are single-sourced by hand rather than spliced. These are
   choices, not results.

Telling us these are still open is not useful. Telling us one of them is *wrong* is.

---

## 7. Settled against the source — reopen only with new evidence

Both archived in `PAPER_A_SOLVER_CONTRACT_AUDIT.json`:

- **Reynolds definition** — computed from the **superficial** velocity; a contract test recovers
  `Re` numerically from `Sh` to prove the displayed form is the evaluated one.
- **`flow` and density** — the source consumes its `flow` column as **mass flow in g/s** while
  labelling it mL/s, so the stopping rule returns a collected **mass** and the endpoints are
  38/40/42 **grams**.

Round 8 found the second correction had reached the science and not the release gate. If you are
inclined to check whether a "settled" item actually landed *everywhere*, that instinct has now paid
twice.

---

## 8. Format

Report findings as **P0 (submission-blocking) / P1 (major) / P2 (editorial)**, each with the
evidence relied on and a minimum acceptance criterion. Where you assert a number is wrong, say what
you compared it against.

If a finding is a **stale number**, say so explicitly. Round 9's stale-number category was empty;
if it is non-empty again, the binding chain has regressed and we need to know.

**If you find nothing in a section, say so.** A round that returns fewer findings is informative
only if we can tell the difference between "checked and clean" and "not reached".

And if you conclude one of *our* corrections is wrong — as round 8's P2-1 was, and as round 9's
"same side of zero" replacement wording was — say that plainly. Two rounds running, the remediation
has overshot in at least one place. We would rather be told than have it stand.
