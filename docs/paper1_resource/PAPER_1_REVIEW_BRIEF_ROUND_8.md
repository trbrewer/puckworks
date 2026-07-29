# Paper 1 — reviewer brief, round 8

**Manuscript:** `docs/submission/PAPER_A_JFE_MANUSCRIPT.md` (canonical working draft:
`docs/PAPER_A_DRAFT.md` — the two are held in content agreement by CI).
**Commit:** `21b138a` on `main`. Earlier commits are **not** equivalent: the headline corpus, the
primary resampling unit, the endpoint's *unit*, and the displayed Reynolds number all changed in
PR #198, and PR #199 landed a card batch that corrected two standing cards. Reviewing anything
before `21b138a` will produce findings we have already actioned.

**Supplement:** `docs/submission/PAPER_A_JFE_SUPPLEMENT.md` + `docs/submission/figures/`.

This is a **single-paper review**. Papers B2 and 3 are out of scope; findings about them will not be
actioned in this round.

---

## 1. What changed, and why the previous brief was wrong about what to trust

The round-7 brief told you not to spend effort re-checking arithmetic, on the grounds that
166 of 441 claim-bearing numbers were verified against producers and the correctness-critical
slow-lane subset was 66 of 77 bound. Both figures were accurate. **They were also beside the
point.** Round 7 returned three submission-blocking defects, and the value-level chain passed
every one of them:

| defect | why the chain saw nothing |
|---|---|
| the manuscript's Reynolds number differed from the code's by `α_l⁻² ≈ 34.6` | both equations contain the same constants; only the *use* of porosity differed |
| a 40 **g** endpoint labelled 40 **mL** everywhere, including inside a figure's pixels | the token "40" is byte-identical in either unit |
| 108 scored records described as the complete coarse/fine corpus | 108 is arithmetically correct — for the subset nobody had declared |
| the resampling omitted cross-solute condition dependence | the reported values matched the producer exactly |
| the SI described one optimizer where the code uses three | every reported minimum still resolved against its archive |
| the claim-binding audit was itself stale | the audit sat outside its own binding chain |

Worse, one of round 7's blockers was being **actively enforced in the wrong direction**:
`tools/paper_a_consistency.py` banned the phrase "matched 40 g cups" and required the volume
wording, on a rationale that the solver-contract audit had already overturned. And the previous
brief's own §6 told you the Reynolds equation "has been corrected" — it had been corrected on the
model card and not in the manuscript. **A brief that vouches for something is exactly as fallible
as the thing it vouches for**, which is the disposition we would like you to carry into this round.

### What is new

`tests/test_paper_a_model_contract.py` (19 contracts) binds *meaning* rather than tokens:

- the displayed Reynolds equation against the one `closures.sherwood_h` evaluates (recovered
  numerically from `Sh`, not read from the source);
- the endpoint's printed unit against its stopping rule;
- the declared corpus against the sample-ID manifest the producer emits;
- the resampling cluster key, tested on a construction where the right unit and the wrong one give
  demonstrably different answers;
- the SI optimizer description against `_profile_objectives`;
- the claim-binding audit against a fingerprint of its inputs;
- one interval rendered at one precision across manuscript and supplement.

### Current coverage, stated without spin

- **193 of 477** claim-bearing numerals (40.5 %) resolve against a producer, a committed archive or
  a module constant.
- **89 slow-lane bindings** resolve and match; **11 of 95** slow-lane values remain unbound.
- **0 unaccounted** numerals on the draft and on the conversion.

Those numbers describe *coverage*, not *correctness*, and round 7 is the proof that the two are
different quantities. Please treat them as a map of where the cheap checks already look, not as an
assurance about what they found.

---

## 2. Explicitly out of scope — do not report these

Known, deliberate, deferred:

| | |
|---|---|
| Author list, affiliations, corresponding author, ORCIDs | not yet supplied |
| CRediT roles, funding, competing interests, generative-AI declaration | not yet supplied |
| Licensed indexed novelty search | not yet run |
| Release DOI and archival tag | not yet minted |
| Working-draft date and internal review-history prose | will be stripped at submission |

On novelty, §1 already states the claim is *"the authors' awareness rather than … the result of a
systematic search"* and commits to revising it once the search is archived. Take that at face value.

---

## 3. The chain, and how to test it rather than trust it

```bash
python -m puckworks.paper_a.slow_lane_bindings   # every slow-lane number vs its archived run
python tools/paper_a_consistency.py verify       # submission contract: SI refs, figures, front matter
python tools/claim_binding_audit.py              # fails if the audit's inputs moved under it
python -m pytest tests/test_paper_a_model_contract.py -q   # the semantic contracts
python -m pytest tests/test_cross_paper_number_audit.py -q  # every numeral has a disposition
```

`docs/CLAIM_BINDING_AUDIT.md` is generated and fingerprints the manuscripts and coverage modules it
read, so it cannot again report a state the repository has moved past.

**Adversarial use is the most valuable thing you can do with these.** A manuscript number these
report as verified but which is in fact wrong is the single most useful finding available, because
it means the mechanism is producing false assurance — which is worse than no mechanism.

---

## 4. What we are asking you to look for

### (a) Semantic mismatches the new contracts do *not* cover

The nine contracts above were written to catch the defects round 7 actually found. That is
survivorship bias by construction. The interesting question is what shape of defect they still
cannot see. Candidates we have thought of and not closed:

- an evidence tier asserted above what the design licenses;
- a within-campaign result read as external validation;
- an estimand named as one quantity and computed as another, where both are unitless;
- a figure whose *plotted geometry* disagrees with its caption (we now bind titles and units, not
  what the marks encode);
- a producer whose docstring and behaviour diverge where no manuscript sentence quotes it.

### (b) Statements about the corpus that the corpus contradicts

**Still the class we most need help with.** Round 6 found §5 asserting *"An empirical whole-cup
comparison on this campaign is not available"* two sentences after quoting a MAPE computed against
exactly those measured cups. Round 7 found the transfer benchmark excluding eight records the prose
said were included. Both are the same shape: **a sentence that asserts nothing numeric, and is
therefore invisible to every value-level check.** Only reading the data disproves them.

Worth probing: a described dataset that does not exist or has different coverage; "we do not have X"
where X is present; a method described in prose that differs from the implementation; a limitation
claimed that the data does not impose; a corpus count that is right for a subset nobody declared.

### (c) The knife-edge, specifically

The headline is a paired difference of **−0.394 pp** whose primary clustered percentile range is
**[−0.825, +0.000]** — an upper bound of −0.0004 pp before rounding. At 38 g it clears zero by
0.046 pp; at 42 g it lands on zero again. We have deliberately declined to report any of these as
"excludes zero", on the grounds that the rows differ only in the third decimal place of a resampling
percentile.

**Please attack that decision from either side.** Either we are hiding behind a rounding argument to
avoid conceding a small real effect, or we are reporting a boundary with more precision than the
design supports. We do not think it is the former, but we have an obvious interest in that
conclusion.

### Also welcome, lower priority

Scientific framing; the strength of the identifiability argument; the adequacy of the level-only
comparator; whether demoting the same-(T,p) lookup to a matched-grid secondary is the right call
given it is undefined on 24 of 132 points; and whether §5's evidence hierarchy is persuasive.

---

## 5. Known open items — please do not re-report

Recorded, not overlooked:

1. **The fraction-versus-measured-cup rate-profile contrast has not been run.** Round 6 proposed it
   as §5's primary result. The data supports it; the analysis is owed. §5 now says what is true and
   names the stronger comparison as available.
2. **11 of 95 slow-lane values remain unbound**, enumerated by
   `puckworks.paper_a.claim_coverage.binding_coverage()`.
3. **~255 declared design settings** (thresholds, windows, condition counts) are single-sourced by
   hand rather than spliced. These are choices, not results.

Telling us these are still open is not useful. Telling us one of them is *wrong* is.

---

## 6. Settled against the source — reopen only with new evidence

Both are archived in `docs/paper1_resource/PAPER_A_SOLVER_CONTRACT_AUDIT.json` and were resolved
against the original Pannusch/Schmieder MATLAB, not against our reading of the paper.

- **Reynolds definition.** `SherwoodFunction.m` computes `Re = d32 .* q ./ kin_vis` from the
  **superficial** velocity; our port is identical. The manuscript now displays
  `Re = d32 u_s ρ/η = d32 α_l v_l ρ/η` with `u_s = Q/A_cs`, and a contract test recovers `Re`
  numerically from `Sh` to prove the displayed form is the evaluated one. *Round 7 found this
  correction had reached the model card and not the manuscript — so if you are inclined to check
  whether a "settled" item actually landed everywhere, that instinct has already paid once.*

- **`flow` and density.** `simulation_Fit2.m:3` reads
  `q = flow ./ 1000 ./ paramPh.rho ./ paramPh.Acs` — character-for-character our expression, at all
  seven call sites including the volume accumulator. The source consumes its `flow` column as **mass
  flow in g/s** while labelling it mL/s. Removing the density division would break fidelity to the
  source and invalidate every archived fitted parameter, since `A`, `B`, `K_ref`, `γ` and `c_s0`
  were all estimated under that convention.

  **Consequence, corrected in round 7:** the stopping rule `t_end = M_target / Q` therefore returns
  a collected **mass**, so the endpoints are 38/40/42 **grams** and the sweep spans the campaign's
  own declared ±2 g collection tolerance. The manuscript previously called these mL and framed the
  whole thing as a mass-to-volume proxy. Density still enters the solver — it sets the superficial
  velocity and the concentration averaging — but it does not convert the stopping rule into a volume
  target.

---

## 7. Format

Report findings as **P0 (submission-blocking) / P1 (major) / P2 (editorial)**, each with the
evidence relied on and a minimum acceptance criterion. Where you assert a number is wrong, say what
you compared it against — the last two rounds' audit tables were unusually useful for exactly that
reason.

If a finding is a **stale number**, say so explicitly. Round 7's only confirmed stale numbers were
in the claim-binding audit itself, which is the failure mode we are now generating that document to
prevent. If the category is non-empty again, the bindings are wrong and we need to know.

**If you find nothing in a section, say so.** A round that returns fewer findings is informative
only if we can tell the difference between "checked and clean" and "not reached".
