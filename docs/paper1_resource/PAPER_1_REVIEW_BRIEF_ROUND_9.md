# Paper 1 — reviewer brief, round 9

**Manuscript:** `docs/submission/PAPER_A_JFE_MANUSCRIPT.md` (canonical working draft:
`docs/PAPER_A_DRAFT.md` — the two are held in content agreement by CI).
**Commit:** `45e753a5f37ede66cd99a016a6b8902fdbadebdf` on `main`. Earlier commits are **not** equivalent: the primary
clustered interval, the canonical bootstrap draft count, one robustness *claim* and the entire
manuscript-generation mechanism all changed in PR #201. Reviewing anything before that commit will
produce findings we have already actioned.

**Supplement:** `docs/submission/PAPER_A_JFE_SUPPLEMENT.md` + `docs/submission/figures/`.
**Prior round:** `PAPER_1_ROUND_8_DETAILED_REVIEW.md`, with the remediation plan beside it.

This is a **single-paper review**. Papers B2 and 3 are out of scope.

---

## 1. Read this first: last round, the brief and the audit were both wrong, in opposite directions

Round 8 asked us to reconcile this brief's *"11 of 95 slow-lane values remain unbound"* **down to
6**, on the authority of `docs/CLAIM_BINDING_AUDIT.md`.

We did not make that change, because the reviewer had it backwards. The audit was computing

```
unbound = 95 registered slow-lane RESULTS  −  89 binding RULES
```

across two different populations. Five of those 89 rules bind values that are not registered
slow-lane results at all, so subtracting credited them against results they do not cover. **11 was
correct; the audit's 6 was the arithmetic error.** The generator now reports the two populations
separately, and asserts that its categories reconcile.

We are opening with this because it is the most useful thing we can tell you about how to read the
rest of this document:

- the **brief** was wrong in round 7 (it vouched for a Reynolds correction that had reached the
  model card and not the manuscript);
- the **generated audit** was wrong in round 8 (the arithmetic above);
- and the round-8 **review** was wrong about which of those two to trust.

Three rounds, three different assurance artefacts producing confident false statements. Treat
everything below as a map of where we have looked, never as evidence of what we found.

---

## 2. What changed since round 8

### The three submission blockers are closed

| | round-8 defect | now |
|---|---|---|
| **P0-1** | the *separately supplied* Figure 3 caption still quoted the superseded 108-point tuple (8.2 %/8.6 %/50-of-108) | generated from the complete-corpus artefact; 108 survives only as an explicitly labelled matched-grid secondary |
| **P0-2** | general Methods declared **two** schemes and named the superseded one primary | generated from the archived design object; **four** schemes, `cond_in_variety` primary |
| **P0-3** | package and release gate still encoded the retired **mL** endpoint; `_release_state()` sought a `v_targets` key the artefact had not carried since round 7 | typed collected-mass schema; **the endpoint contract now runs in `verify`**, not `submission` only |

On P0-3 specifically: the reason a broken release gate and a green development lane coexisted for a
whole review round is that the science check lived in the mode nobody runs until the end. **No
scientific contract now lives only in `submission`**; that mode adds metadata and freshness on top.

### The science moved, and this is the part that most needs your scrutiny

Round 8 asked us to adjudicate a knife-edge: the 40 g primary upper bound sat at `−0.0004 pp`, and
the paper leaned on the sign of its fourth decimal. We raised the canonical draw count from
**B = 8000 to B = 1,000,000** and ran a 20-seed stability audit.

The knife-edge was Monte Carlo noise. At adequate resolution:

- the 40 g primary upper bound is **+0.004 pp** (Monte Carlo SE ±0.0005), so the primary range
  **contains** zero at 40 g and 42 g and excludes it at 38 g;
- the round-7 claim that **the zero crossing changes under an alternative fitting loss is
  withdrawn** — at B = 1,000,000 both losses put the range on the same side of zero;
- **the abstract's headline sentence changed** as a consequence: the range now *contains* zero
  rather than *reaching* it.

Everything that did **not** depend on the draw count reproduced exactly before we changed anything:
pooled MAPE 8.44 % / 8.83 %, paired difference −0.394 pp, worse on 62 of 132, at all three
endpoints and under both losses. That reproduction is in the PR history and is the reason we are
confident the movement is numerical, not substantive — but it is exactly the kind of claim that
deserves an independent check rather than our assurance.

A fourth, design-aligned scheme was added: `sample_in_variety_grind`, one cluster per coffee sample
record carrying its three co-measured solutes, 44 clusters within variety × grind. It is a
prominent **secondary**; `cond_in_variety` was deliberately **not** re-selected as primary, to avoid
choosing a unit after seeing where its range falls.

### The other majors

**P1-1** the primary cluster is no longer described as the design's "actual dependence structure";
the census is stated as it is (**18 clusters of six observations, 8 off-grid clusters of three**),
and the false claim that both secondary ranges are narrower is corrected — the whole-group range is
**wider**. **P1-2** analytical flags now derive from signed full-precision bounds, with display
rounding kept strictly separate. **P1-3** the interval contract is artefact-driven and
block-scoped. **P1-4** the corpus is bound to a hashed, source-derived manifest, published as
Supplementary Table S7. **P1-5** Figure 1 draws LOCO and C/F as parallel branches with explicit
calibration scopes. **P2-2** Supplementary S3's titles no longer collide.

### The structural change you should attack hardest

Every data-bearing value in the transfer analysis is now **generated**, not typed:

```
bioactives.csv
  └─ puckworks/paper_a/transfer_contract.py     endpoint schema · corpus manifest + hashes ·
  │                                             resampling design · ONE display formatter
  └─ tools/paper_a_transfer_artifacts.py        --check (cheap) / --write (slow) / --recompute
  └─ tools/paper_a_transfer_text.py             marked blocks in manuscript, draft, captions
  └─ tools/paper_a_supplement.py                supplement (delegates transfer blocks)
```

This is new and unproven. It removes one failure mode (a value retyped in five places, corrected in
four) and introduces another: **a generator that renders a defensible number into an indefensible
sentence.** We already caught three such defects in our own generated prose during review —
a malformed clause ("contains zero *at its upper bound*"), a claim that a bound was "far below what
this resampling resolves" when it was in fact ~8 standard errors from zero, and a sentence about
"the largest advantage the upper bounds allow" that was backwards once those bounds turned positive.
We fixed those three. **We do not believe we found them all.**

---

## 3. Explicitly out of scope — do not report these

| | |
|---|---|
| Author list, affiliations, corresponding author, ORCIDs | not yet supplied |
| CRediT roles, funding, competing interests, generative-AI declaration | not yet supplied |
| Licensed indexed novelty search | not yet run |
| Release DOI and archival tag | not yet minted |
| Working-draft date and internal review-history prose | will be stripped at submission |

`paper_a_consistency.py submission` reports 15 blockers. All 15 are the metadata above. No science
blocker remains; if you find one, that is a P0.

---

## 4. The chain, and how to test it rather than trust it

```bash
python tools/paper_a_transfer_artifacts.py --check   # source→artefact: rebuilds the manifest from
                                                     # the CSV and compares hashes (seconds)
python tools/paper_a_transfer_text.py --check        # artefact→publication: every generated block
python tools/paper_a_consistency.py verify           # submission contract, incl. endpoint science
python -m puckworks.paper_a.slow_lane_bindings       # 98 bindings vs their archived runs
python tools/claim_binding_audit.py                  # fails if its own inputs moved under it
python -m pytest tests/test_paper_a_transfer_contract.py tests/test_paper_a_model_contract.py \
                 tests/test_paper_a_figure_semantics.py -q
python -m pytest -q                                  # full suite, ~15 min
```

To regenerate the science itself (~25 min of PDE solves, hand-run, not CI):

```bash
python tools/paper_a_transfer_artifacts.py --write
```

**`--check` deliberately does not re-solve the PDEs.** It rebuilds the corpus manifest from
`bioactives.csv` and compares it to what each artefact declares, so membership and schema drift are
caught every commit for free. The expensive numerical reproduction is `--recompute`.

**The two contract layers are deliberately independent.** Source→artefact tests reconstruct counts,
IDs, cluster membership and hashes from the CSV; artefact→publication tests compare the marked
blocks with the artefact. Deriving both sides from the same JSON would prove only internal
consistency and could certify a wrong artefact. If you find a place where we have in fact closed
that loop, it is a P1.

---

## 5. What we are asking you to look for

### (a) The generated prose, read as prose

This is the highest-value target this round. The numbers are bound; the **sentences around them**
are generated by string-building code that no test evaluates for meaning. Specifically:

- a sentence whose *arithmetic* is right and whose *claim* is wrong, especially anywhere a bound's
  sign, direction or favourability is described;
- text that reads correctly at 40 g and becomes false at 38 g or 42 g, where the bound changes sign;
- comparative language ("narrower", "wider", "largest", "at most") that would invert if the
  underlying values moved;
- any place the manuscript narrates the repository's own history rather than the analysis. We
  removed several such passages; we may have missed one, and a journal reader should not be reading
  our changelog.

### (b) The B = 1,000,000 result

- Is the multi-seed audit design sound, and is the Monte Carlo SE we quote (±0.0005 pp, audited at
  the 40 g primary bound) legitimately applied where we apply it?
- Does the third displayed decimal survive that SE? We assert it is resolved to about ±0.001 pp and
  quote three decimals anyway, with the SE stated. Argue us down if that is not defensible.
- Is withdrawing the fitting-loss zero-crossing claim correct, or have we replaced one
  over-read of a boundary with a differently-shaped over-read?

### (c) The primary scheme, still `cond_in_variety`

We retained it deliberately and say so. But retaining a conservative unit is still a choice, and
the paper now reports four schemes whose ranges differ. Is the framing honest, or does reporting
four sensitivities while designating one primary smuggle back the selection we claim to avoid?

### (d) Anything the new contracts still do not cover

Round 8's most valuable finding was that a test named for the primary interval could not match it.
The equivalent question now: which of our new assertions would pass unchanged if the thing it names
were deleted? We have added mutation tests for the failure modes we could imagine. Yours will be
different.

### Also welcome, lower priority

Supplementary Tables **S6** (resampling design) and **S7** (44-record corpus membership) are new —
check numbering, citation and whether S7 is legible at journal width. Figure 1 was redrawn and
Figure S3 relaid out; both are asserted by tests on node/edge data and rendered bounding boxes
rather than on pixels, so a semantic error would survive.

---

## 6. Known open items — please do not re-report

1. **The fraction-versus-measured-cup rate-profile contrast has not been run.** Round 6 proposed it
   as §5's primary result. The data supports it; the analysis is owed.
2. **11 of 103 registered slow-lane values remain unbound**, enumerated by
   `puckworks.paper_a.claim_coverage.binding_coverage()` (`still_unbound`). Not to be confused with
   the 98 binding *rules*, all of which resolve and match. (The registered total rose from 95
   because the four-scheme design and the Monte Carlo audit added quoted values; the unbound set is
   unchanged.)
3. **~255 declared design settings** are single-sourced by hand rather than spliced. These are
   choices, not results.

Telling us these are still open is not useful. Telling us one of them is *wrong* is.

---

## 7. Settled against the source — reopen only with new evidence

Unchanged from round 8, and both archived in `PAPER_A_SOLVER_CONTRACT_AUDIT.json`:

- **Reynolds definition** — `SherwoodFunction.m` computes `Re` from the **superficial** velocity;
  a contract test recovers `Re` numerically from `Sh` to prove the displayed form is the evaluated
  one.
- **`flow` and density** — the source consumes its `flow` column as **mass flow in g/s** while
  labelling it mL/s, so the stopping rule returns a collected **mass** and the endpoints are
  38/40/42 **grams**. Round 8 found this correction had reached the science and not the release
  gate. If you are inclined to check whether a "settled" item actually landed *everywhere*, that
  instinct has now paid twice.

---

## 8. Format

Report findings as **P0 (submission-blocking) / P1 (major) / P2 (editorial)**, each with the
evidence relied on and a minimum acceptance criterion. Where you assert a number is wrong, say what
you compared it against.

If a finding is a **stale number**, say so explicitly.

**If you find nothing in a section, say so.** A round that returns fewer findings is informative
only if we can tell the difference between "checked and clean" and "not reached".

And if you conclude one of *our* corrections is wrong — as round 8's P2-1 was — say that plainly.
We would rather be told the remediation overshot than have it stand.
