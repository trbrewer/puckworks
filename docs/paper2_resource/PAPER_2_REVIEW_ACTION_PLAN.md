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
- 🔴 **4.3 / 4.4** full leave-one-shot-out **cross-fitting of Φ(t)** — **BLOCKED ON DATA, not effort.**
  Φ(t) = m_d(t)/m0 is built from TDS(t)×Q(t), and the deposit's TDS is 3 replicates that are **not
  shot-matched** to the 5 flow traces, so a held-out shot cannot have its own Φ(t) rebuilt. The
  per-shot ladder above therefore evaluates Φ(t) as a **zero-free-parameter prediction** and does
  **not** claim a cross-fit (`per_shot_ladder()["note"]` says so, and a test pins it). Unblocking
  needs shot-matched TDS from the authors — a correspondence item, not an analysis one.
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
