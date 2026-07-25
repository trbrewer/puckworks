# Paper 2 (B2) — review action plan (2026-07-25)

Triages `PAPER_B2_DETAILED_REVIEW_2026-07-25.md` (a detailed external review of
`docs/PAPER_B2_TEMPORAL_DRAFT.md` — "One flow curve, many causes"). Editorial decision:
**major revision**. The review's thrust matches repo discipline: down-scope overclaims, be exact
about what the *preprocessed mean* trace can support. The five headline 9-bar RMSEs
(0.573 / 0.641 / 0.648 / 0.116 / 0.096 g s⁻¹) are **independently reproduced** by the reviewer.

**Legend:** ✅ done in the accuracy PR · ◑ partially done · 🔬 needs new computation (analysis) ·
❓ needs a **Tim decision** · ⏭ deferred (scoped).

---

## What is DONE in the accuracy PR (prose/metadata down-scoping)

The clearly-correct overclaim fixes (review §E1–E13) that are our own manuscript's wording, plus the
one verified metadata error:

| Item | Fix |
|---|---|
| E1 abstract "establishes a need for temporal dynamics" | → "supports temporal flexibility relative to the tested static nulls" |
| E3 "one/measured 9-bar trace" | → "preprocessed across-shot mean 9-bar trajectory" (abstract, §5.2, §5.3, §7); new **observation-operator** paragraph in §2.4 |
| E4 Table 2 / abstract "no coefficients fitted to this flow trace" | added "temporal input partly derived from the same flow (§4.3)" |
| E5 "externally parameterized temporal trajectory" | → "same-campaign, target-informed temporal trajectory" |
| E6 cubic "in-sample flexibility floor/bound" | → "same-trace four-parameter descriptive benchmark (not predictive, not a lower bound)" |
| E7 "moving-block intervals" as CIs | §4.2 heading → "Conditional fixed-loss block-resampling **sensitivity**"; abstract adds "not a between-shot confidence interval" |
| E9 viscosity "implemented branch" vs "outside the ladder" (§5.4 vs §6) | resolved the contradiction — viscosity is a **qualitative sign candidate outside the scored ladder**; "reproduced by"→"compatible with", "corroborated"→"compatible", explicit "compatibility observation, not attribution" |
| E12 "4.9 times lower" | → "a factor of 4.9 smaller" |
| E13 "biological replication" | → "shot-to-shot, coffee-lot, preparation, operator, grinder, or apparatus replication" |
| E10 "nearly reaches an in-sample flexible floor" (§5.2) | added the caveat that the 0.116-vs-0.096 gap should not be over-read (lag-1 ACF ≈ 0.99, DW ≈ 0.01) |
| **§4.2 SEM** (review 4.2) | §2.4 states the `*_std` columns are `pandas.sem()` = **standard errors of the mean, not standard deviations** |
| **Recorded-pressure robustness** (review 4.9/§5.4 audit) | added to §5.2: static 0.647696→0.646846, Φ(t) 0.115769→0.116443 (both < 0.001; ordering unchanged) — a robustness result, not a mechanism claim. |

14 waszkiewicz/paper_b/poroelastic tests pass; the CSV fix breaks no data-integrity test.

## Deferred — needs new COMPUTATION (🔬 the review's "essential before submission" analyses)

These require real analysis on the raw Waszkiewicz shot data and are the substance of the revision;
they are **not** faked:

- **4.1** per-shot ladder: reproduce the ladder on each individual 9-bar shot (five files); report
  per-shot RMSE, shots-won, leave-one-shot-out. *The shot, not the time point, becomes the unit.*
- **4.3 / 4.4** leave-one-shot-out **cross-fitting of Φ(t)** (rebuild mean/TDS/dissolved-mass/params
  without the held-out shot) + shot-level uncertainty **with refitting** (replaces the fixed-loss
  block resampling as the primary uncertainty).
- **4.5** a genuinely **held-out flexible comparator** (penalized spline / GP mean; leave-segment-out CV).
- **4.7** residual diagnostics as a first-class result (residual-vs-time all branches, ACFs, spectra,
  overlaid on shot-level variability).
- **`solids_calibration.csv` sign (review 4.3) — VERIFIED, deferred to the release rebuild.** The CSV `model` column documents `0.5·k·(1 − tanh)` but the implementing code (`waszkiewicz2025/poroelastic.py:77`, Eq. 20) computes `0.5·k·(1 + tanh)` — a documentation-only sign error (the string is not used in computation; `paper_b build verify` passes 18/18 with either). The correct fix is `1 + tanh`, but the CSV's SHA256 is pinned in `paper_b_manifest.json` **and** a PV-04 autopsy snapshot, so it must be corrected together with those frozen hashes in the 4.13 release rebuild rather than as an isolated edit.
- **4.13** a Paper-B2-specific **clean reproducibility release** (strict no-dirty-tree; claim map
  covering *every* number incl. Table 2/3, block endpoints, residual diagnostics, robustness).

## Tim DECISIONS — RESOLVED (2026-07-25)

- ✅ **4.6 viscosity/Gagné — REMOVED (Option A).** Cut the integrated viscosity/Gagné material (§5.4
  rewritten to keep dissolution-opening as the scored sign-carrier + a brief degenerate-second-candidate
  note; Table 4 viscosity row, §6.5 Gagné sentences, and the Limitation-2 second-apparatus sentences
  removed). Full material (closures, Gagné 2.7× dataset, 15%/1.6/1% numbers, degeneracy argument, and
  what a scored version needs) **preserved for the perturbation-program follow-up** in
  `docs/future/PAPER_B2_VISCOSITY_GAGNE_RESERVED.md`.
- ✅ **E16 title — CHANGED** to "One flow curve, many **explanations**".
- ✅ **4.12 keyword — DROPPED** "systems identification" (→ "inverse problems; model discrimination").
  A formal identifiability section is deferred to the shot-level analysis work.

## Deferred — P1/P2 prose (⏭, lower urgency)

- 4.8 LOPO renaming + fold-level reporting; 4.10 richer parameter-provenance table + dependency graph;
  4.11 operationalize the perturbation program (11 items/intervention, "establish"→"support");
  4.12 systematic literature search + missing refs (Gagné, Telis-Romero, Sobolík); figures (P2).

---

Central down-scoped position the revision should adopt (reviewer, verbatim): *the analysis
demonstrates a same-campaign, target-informed temporal construction follows the preprocessed mean
curve better than constant levels; it does not yet establish held-out-shot performance, an
independently measured state trajectory, or a unique poroelastic–dissolution mechanism.*
