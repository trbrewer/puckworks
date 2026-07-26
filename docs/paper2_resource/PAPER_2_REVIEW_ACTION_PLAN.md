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

- ✅ **4.1 per-shot ladder — DONE (2026-07-25).** The blocker was an *intake* gap, not missing
  data: the 57 raw per-brew traces were on Zenodo (CC-BY) but only the per-pressure means had been
  ingested. They are now `waszkiewicz2025/traces_per_brew` (9 bar has **five** shots), and
  re-aggregating them reproduces the published means on all 11 000 rows to 5e-7. Producer:
  `analysis.waszkiewicz_shot_level` (`per_shot_ladder`, `shot_level_noise_floor`); 8 tests.

  **Results, with the shot as the unit (window 15–95 s, n=5):**

  | rung | mean RMSE g/s | SD | range |
  |---|---|---|---|
  | rung1 best-in-window constant (1 param, re-fit per shot) | 0.580 | 0.054 | 0.532–0.666 |
  | rung3 published static κ(P) (0 free params) | 0.661 | 0.100 | 0.566–0.773 |
  | **rung4 poroelastic Φ(t)** (0 free params) | **0.189** | 0.061 | 0.115–0.241 |
  | flexible cubic (4 params, re-fit per shot) | 0.107 | 0.016 | 0.081–0.124 |

  **Shot-to-shot noise floor: 0.149 g/s** (a single shot's RMSE from the mean curve the manuscript
  scores; range 0.073–0.212; pointwise between-shot SD mean 0.154, max 0.359).

  **What this CONFIRMS (the primary claim, now stronger).** Φ(t) beats the best-in-window constant
  on **5 of 5 individual shots**, with a mean margin of 0.39 g/s ≈ **2.6× the noise floor**. The
  headline ordering is not an artifact of averaging — it survives the unit change. Same for static
  κ(P) (0.189 vs 0.661).

  **What this REFUTES (the secondary claim).** On the averaged curve the manuscript reports Φ(t)
  0.116 vs cubic 0.096 — a 0.020 gap supporting "Φ(t) nearly reaches the flexible floor". Per shot
  the cubic wins clearly and the gap widens to **0.083 ± 0.050 g/s**, which is *inside* the 0.149
  noise floor. With five shots that comparison is **not resolvable**, and the "nearly reaches the
  flexible floor" framing cannot be asserted.

  **Also: the absolute RMSEs are not shot-prediction accuracy.** Φ(t) scores 0.116 against the mean
  but 0.189 against real shots — because averaging five brews removes noise the model never had to
  predict. Any absolute RMSE quoted from the mean trace should be labelled as fit to a preprocessed
  average, with 0.149 g/s given as the scale on which differences are read.

  ⏭ *Manuscript edits deliberately NOT made here* — the numbers are landed and producer-backed
  first; changing §5.2/Table 2 and the abstract is a separate scoped pass.
- ◑ **4.2 / P0.2 — PARTIALLY DONE (2026-07-25); my earlier "fully blocked" call was too strong.**
  Φ(t) reuses the target through **two** channels and they are not equally blocked:
  **(a) the equilibrium calibration** $(P_c, Q_c)$ is fitted across pressures with the 9-bar point
  being the mean of the five 9-bar shots — so it *does* contain the held-out shot, and it **is**
  cross-fittable. Now done (`leave_one_shot_out_phi`): per held-out shot the 9-bar point is rebuilt
  from the other four, $(P_c,Q_c)$ refitted, Φ(t) recomputed, and only the held-out shot scored.
  **Finding: this channel is negligible** — held-out mean RMSE 0.1897 vs in-sample 0.1886 g/s, an
  optimism of **0.0011 g/s ≈ 1 % of the 0.149 g/s shot noise floor** ($P_c$ is unmoved at 12.394;
  $Q_c$ spans 1.903–1.913). So target reuse through the equilibrium fit is *bounded and immaterial*.
  **(b) the dissolved-mass sigmoid** $(k,l,m)$ is fitted from TDS(t)×Q(t) and **remains blocked** —
  the deposit's TDS is three replicates that are not shot-matched to the flow traces. Reported, not
  hidden (`remaining_target_reuse`), and a test forbids describing this as a full cross-fit.
- ✅ **P0.3 shot-level paired uncertainty — DONE (2026-07-25).** The block-resampling interval is
  demoted to a secondary within-curve sensitivity; the primary statement is now at the shot.
  Producer `paired_shot_uncertainty`. With five paired units the exact two-sided randomization
  p-value is enumerated over all 2⁵ = 32 sign assignments, and the **structural floor is 0.0625** —
  no paired randomization test on this design can reach 0.05, which the manuscript now states
  before reporting any result. Φ(t) beats the best constant on **5/5** shots by **−0.390 g/s**
  (2.6× the 0.149 g/s shot noise floor) and the static branch on **5/5** by **−0.472 g/s**; the
  Φ(t)-vs-cubic gap of **+0.083 g/s** is *below* the noise floor and therefore unresolvable.

- ✅ **P0.4 held-out flexible comparator — DONE (2026-07-25), and it downgrades the paper.**
  Producer `held_out_flexible_comparator`: a prespecified penalized cubic B-spline (12 interior
  knots, second-difference penalty, GCV on training data only) under two protocols that withhold
  the scored points. **Leave-one-shot-out:** spline **0.186 g/s** vs Φ(t) **0.189** (Φ(t) under its
  own equilibrium cross-fit, **0.190**) — a gap ~40× smaller than the noise floor, against a
  held-out constant of 0.600 and static 0.661. *A generic prespecified smoother trained only on
  other brews predicts a held-out brew as well as the dissolution-linked trajectory does.*
  **Leave-segment-out (interior):** Φ(t) **0.158** vs spline **0.233** vs constant **0.419** —
  filling a temporal gap does need the trajectory's shape. Both are written into the abstract,
  §5.2a and the Discussion; the ontology gains `shot_held_out_null` / `segment_held_out_null` so
  the retired "genuinely held-out" phrase cannot leak back onto a mechanistic branch.

- ✅ **P0.7 residual diagnostics at one resolution — DONE (2026-07-25).** Producer
  `residual_diagnostics`: ACF, Durbin–Watson, residual-vs-time and residual/between-shot-SD for
  **every** branch on the **same** decimated grid (1 s primary, 5 s sensitivity). The statistics
  are demonstrably resolution-dependent (Φ(t) ACF 0.969→0.533, DW 0.047→0.823 from 1 s to 5 s),
  which is why the resolution is declared. Every branch, including the flexible cubic, leaves
  strongly autocorrelated residuals; Φ(t) and the cubic sit at 0.76× and 0.65× the between-shot SD
  while the constant and static branches sit at 3.8× and 4.3×.

  Archive: `PAPER_B2_SHOT_LEVEL_RESULTS.json`. 8 new tests, including one that proves the
  leave-one-shot-out loop actually excludes the scored shot (fitting on all five scores better),
  and one that fails if the mechanistic advantage over the withheld spline ever exceeds the noise
  floor without new evidence.

- ✅ **P1.4 block-resampling Methods corrected — DONE (2026-07-25).** The description was wrong
  about what the code does, in the direction that matters: the producer resamples **common block
  indices into the two paired squared-error sequences** and recomputes each branch's RMSE, whereas
  the Methods said it sampled blocks of the *difference* sequence `d_i`. Resampling `d_i` alone
  would break the pairing and would not reproduce an RMSE difference (which is not the mean of
  `d_i`). Now stated with the block construction, the **non-circular** boundary convention (starts
  drawn from 0..n−b, so end points are slightly under-represented), 1,000 resamples at seed 0, and
  the per-block-length deterministic streams.

- ✅ **P1.5 complementary metrics — DONE (2026-07-25).** RMSE, MAE, mean bias and standardized
  residual scale per branch. They **change one ordering**: on MAE the static κ(P) branch (0.370)
  beats the best constant (0.478), the reverse of their RMSE ranking (0.661 vs 0.583), because the
  static branch carries a −0.312 g/s mean bias that RMSE penalizes more. Verified to hold at both
  the 1 s and 5 s diagnostic resolutions. No conclusion rests on that pair, but it is recorded as
  the demonstration that one scalar is not complete evidence.

- ✅ **P1.1 cross-pressure heterogeneity — DONE (2026-07-26), and it qualifies the paper.** The
  macro mean says Φ(t) is best; the per-pressure table says the **best branch changes three times**
  (RC-3b at 1–2 bar, static at 3.5–6, Φ(t) at 7–11, RC-3b at 13). Φ(t) wins **4 of 11** pressures —
  and that band contains the primary 9-bar analysis, so the headline sits inside the only region
  where the temporal branch is preferred. Shot counts per pressure range 3–10, so the averaging
  scheme matters: equal-pressure gives phi < rc3b < static, shot-weighted gives phi < static < rc3b.
  Both reported; abstract and §5.3a updated.

- ✅ **P1.2 pressure domains — DONE (2026-07-26).** §5.3b separates the four pressures that were
  being conflated: nominal setting, recorded basket pressure (**below nominal at every setting**, by
  up to 0.61 bar; nominal 9 bar delivered **8.71 bar**), the fitted P_c = **12.39 bar** (a parameter,
  not a setting, reached by only **1 of 11** pressures), and the tested range 1–13 bar.

- ✅ **P1.3 provenance dependency graph — DONE (2026-07-26).** §5.3c replaces the flat
  "target-informed" label with per-input access levels. The point it makes concrete: Φ(t) has
  **zero** free parameters fitted to the scored trace and is still **not held out**, because its
  sigmoid channel is derived from TDS(t)×Q(t) and Q(t) is the scored observable. Only the penalized
  spline is held out, and it is a null.

- 🔧 **DEFECT FOUND AND FIXED while doing P1.1: Table 3's rc3b column was stale in all three rows**
  (0.525/0.519/0.530 against the producers' 0.516/0.510/0.522). `static` and `phi` matched exactly
  in every row — a one-column transcription that survived because nothing checked it. Table 3 is now
  bound to `cross_pressure_loco` / `cross_pressure_discrimination` by a test, proven non-vacuous by
  restoring the stale value and confirming the failure.

  Archive: `PAPER_B2_CROSS_PRESSURE_RESULTS.json`. Producer
  `puckworks/analysis/waszkiewicz_cross_pressure.py`; 11 tests.

- 🔴 **4.3 / 4.4** full leave-one-shot-out **cross-fitting of Φ(t)** — **BLOCKED ON DATA, not effort.**
  Φ(t) = m_d(t)/m0 is built from TDS(t)×Q(t), and the deposit's TDS is 3 replicates that are **not
  shot-matched** to the 5 flow traces, so a held-out shot cannot have its own Φ(t) rebuilt. The
  per-shot ladder above therefore evaluates Φ(t) as a **zero-free-parameter prediction** and does
  **not** claim a cross-fit (`per_shot_ladder()["note"]` says so, and a test pins it). Unblocking
  needs shot-matched TDS from the authors — a correspondence item, not an analysis one.
- **4.5** a genuinely **held-out flexible comparator** (penalized spline / GP mean; leave-segment-out CV).
- ✅ **4.7 residual diagnostics — ANALYSIS DONE (2026-07-26), figure still owed.** New §5.2b.
  `residual_diagnostics()` now emits the **ACF across 20 lags** and a **periodogram** per branch
  alongside the scalars, because lag-1 alone cannot separate a slow drift from a fast oscillation —
  and they mean different things about adequacy. The finding: **>95 % of residual power sits in the
  lowest-frequency quarter for every branch** (0.957 constant / 0.957 static / 0.990 Φ(t) / 0.954
  cubic), so the residuals are slow drift over the 80 s window, not noise a smoother missed. The
  dominant period separates the branches where the scalars do not: the static branches peak at
  **80 s** (one unreversed drift, exactly what a constant leaves against a rising trace) and both
  temporal branches at **40 s** — the temporal construction sheds the slowest component and leaves
  one that *reverses within the shot*, so no further level or slope term would absorb it. Six
  claims bound; 7 tests, including a non-vacuity check that a pure 4 s oscillation lands with
  <0.1 power in the slowest quarter, so "drift" is not an artefact of the estimator.
  **Still owed:** the overlay figure (residual-vs-time for all branches on the pointwise
  between-shot band). It belongs to the Paper 2 figure set, which does not exist yet — there is no
  `figures_paper_b` module and the manuscript still carries "Figure N near here" placeholders. The
  series are in the bundle (`shot_level.residuals_1s`) so the panels can be drawn without re-running
  anything.
- **`solids_calibration.csv` sign (review 4.3) — VERIFIED, deferred to the release rebuild.** The CSV `model` column documents `0.5·k·(1 − tanh)` but the implementing code (`waszkiewicz2025/poroelastic.py:77`, Eq. 20) computes `0.5·k·(1 + tanh)` — a documentation-only sign error (the string is not used in computation; `paper_b build verify` passes 18/18 with either). The correct fix is `1 + tanh`, but the CSV's SHA256 is pinned in `paper_b_manifest.json` **and** a PV-04 autopsy snapshot, so it must be corrected together with those frozen hashes in the 4.13 release rebuild rather than as an isolated edit.
- ✅ **4.13 clean reproducibility release — DONE (2026-07-26).** The strict `release` verb already
  existed (no-dirty-tree + freshness); the gap was the claim map. New
  `puckworks/paper_b/claim_coverage.py` audits **every numeral in the manuscript body** and forces
  each into a disposition. **Claims 18 → 118; unaccounted 150 → 0** (producer 137 / config 159 /
  dataset 17 / derived 5, each recomputed rather than waved through / structural 74). Tables 2 and
  3, the block endpoints, the residual diagnostics and the robustness study are all bound; the
  33-cell per-pressure table is **expanded from the producer**, not transcribed. **Three unbacked
  numbers found:** the six recorded-pressure values were transcribed from a reviewer's table with
  no producer of ours (now reproduced exactly by `recorded_pressure_robustness()`); "up to 0.61
  bar" and "a mean 8.71 bar" are **not reproducible under any natural definition** and were
  replaced with producer-backed values under a declared one; and a macro mean printed as 0.335
  contradicted Table 3's 0.334. Also fixed `_get`, which split dotted paths naively and reported
  every per-pressure cell MISSING. CI enforces a zero-unaccounted ratchet. 12 tests.

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
