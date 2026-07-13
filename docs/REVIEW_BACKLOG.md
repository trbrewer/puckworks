# Review backlog — open / larger / blocked tasks (deferred, to conduct later)

Durable record of the Paper A + Paper B review actions **not yet done** (as of
2026-07-13), so they can be picked up later. The validity-critical **P0** items of both
detailed reviews are already actioned and committed (see ROADMAP §7.1). What remains is
larger-effort, venue-dependent, or externally blocked.

Status key: **UNBLOCKED-LARGE** (can be done now but substantial) · **VENUE** (depends on
target journal; risk of rework if done speculatively) · **BLOCKED-EXTERNAL** (needs data,
author response, or infrastructure not available here) · **DEFERRED-DECISION** (a decision
already made to defer, e.g. release tag).

## Paper A (`PAPER_A_DETAILED_REVIEW.md`)

| id | task | class | notes |
|---|---|---|---|
| A-MAJ04 | Grid-density / domain robustness appendix for the identifiability panel (18/36/72/144 rate grids; ≥2 domains; continuous 1-D optimisation; boundary reporting) | **DONE** (2026-07-12) | `identifiability_panel_convergence` now spans 18/36/72/**144** grids (κ 1924/2070/2067/2022, log-width stable) + narrow[0.3,3]/wide[0.1,10] domains, and adds a GRID-FREE continuous Brent optimiser on the profiled SSE: optimum 0.66 (interior), 10%-band valley [0.37, 6.5] (right-censored) → the flat valley is not a coarse-grid, domain, or discretisation artefact. In the bundle + a build claim + `test_identifiability_convergence_144_and_continuous` |
| A-MAJ13 | Positive-control model-discrepancy variant (altered geometry/flow/IC between data-generation and fitting) | **DONE** (2026-07-12) | `full_cup_simulation_discrepancy`: truth generated at T+ΔC (Arrhenius-nonlinear) × flow-scale, fit at nominal, sweeping rate only. DOSE-RESPONSE: moderate (T+4, ×1.10) leaves an irreducible MAPE floor ~4.8% (>> 3% noise) while the located rate stays ROBUST at 1.0; larger (T+8, ×1.25) raises the floor AND biases the located rate to 1.4 in 100% of seeds → a sharp minimum is necessary-not-sufficient. Both doses in the bundle + 2 build claims + `test_discrepancy_control_dose_response` |
| A-MAJ17 | Residual-diagnostic faceted figures (residuals vs T/p, normalized within variety×solute series; per-group metrics) | **DONE** (2026-07-12) | Fig 7 (`fig7_per_group_diagnostics`) = per-GROUP metrics (variety×solute blind vs inventory-matched MAPE + shape correlation). Fig 8 (`fig8_residuals_vs_conditions`) = the residual-vs-(T,p) SCATTER: `gate_pannusch_angeloni_per_condition` now surfaces per-shot signed residual vectors, showing a solute- and variety-consistent negative offset (all conditions under-predict) that a pure inventory/level rescale cannot remove |
| A-AR13/MAJ19 | Strict one-command `puckworks/paper_a/build.py` | **DONE** (2026-07-13) | `verify` (fast) checks 13 manuscript claims vs the bundle + writes a provenance manifest (commit, env versions, 6 data-file SHA-256, bundle hash); `full` recomputes+renders+verifies. Guarded by `test_paper_a_build_verifies_manuscript_claims`. Owed: an env lockfile (uv/poetry) + the release tag |
| A-MAJ22 | Recover replicate-level Angeloni/Schmieder uncertainty; uncertainty-weighted objective sensitivity | BLOCKED-EXTERNAL | repo has condition-level means; needs source re-intake |
| A-AR15/MAJ21 | Execute the full Scopus/WoS systematic novelty search; populate the evidence matrix | BLOCKED-EXTERNAL | scaffold exists (`docs/literature_search/`); DB execution is a PI action |
| A-AR14/MAJ20 | Frozen `paper-a-v1.0.0` tag + pinned environment + archival DOI | DEFERRED-DECISION | `tag_now:false` — create at submission RC step |
| A-AR01 | Full conventional manuscript prose (Methods equations, references list, figure captions) | VENUE | manuscript form depends on target journal |
| A2-06/07 | Grid-density/domain convergence for the identifiability panel | **DONE** (2026-07-13) | `identifiability_panel_convergence`: κ 1924/2069/2067 across 18/36/72 grids, flat valley on [0.3,3]+[0.1,10], threshold right-censored. Still owed: 144-pt grid + continuous 1-D optimiser (marginal) |
| A2-08 | Uncertainty-weighted / heteroscedastic objective sensitivity using source RSD | BLOCKED-EXTERNAL | needs replicate-level RSD (same as A-MAJ22) |
| A2-09 | Density / 40 g-vs-40 mL endpoint sensitivity (38–42 g range) | **DONE** (2026-07-12) | `endpoint_mass_sensitivity` re-runs the per-condition transfer at 38/40/42 mL. HONEST finding (not the optimistic prior framing): the overall blind MAPE is MODERATELY endpoint-sensitive — it moves ~5.3 pp (19.9→25.2%) — and the trigonelline-hurts detail FLIPS near +5%. ROBUST across endpoints: the large per-condition residual itself + the caffeine inventory-match improvement. So the headline holds but the exact magnitude + trigonelline detail carry a ~5 pp endpoint uncertainty the manuscript must STATE. In the bundle + build claim + test |
| A2-10 | Propagate constructed pressure–flow-map uncertainty | **DONE** (2026-07-13) | `flow_map_sensitivity_transfer`: a systematic ±20% flow-scale perturbation (refit O, transfer C/F) moves held-out MAPE ≤0.6 pp; transfer robust to flow-map MAGNITUDE, still conditional on the inferred-map FORM. Owed: a per-shot measured flow trace |
| A2-13b | Waszkiewicz sensitivity matrix (temperature, flow floor, density, alignment) | **DONE** (2026-07-12) | `waszkiewicz_sensitivity` sweeps temperature 89-95 C × flow floor 0.02-0.10 (12 cells): the localization conclusion is INVARIANT — every cell keeps the 12-fraction range ratio 1.9-2.0× while the single cup NEVER discriminates; best-rate point shifts only 0.4→0.6 (temperature rescales the level, not the cup-vs-fraction contrast). In the bundle + guarded by `test_waszkiewicz_sensitivity_localization_invariant` + a build claim. Time-alignment already swept (offset 0/2/4 s); density (40 g≈40 mL) documented in A2-09 |
| A2-16 | Further figure redesigns (residual panels, source-data export, seed distributions on Fig 6) | **DONE** (2026-07-12) | Fig 7 + Fig 8 residual panels (A-MAJ17); `export_source_data` writes 7 tidy per-figure CSVs (Fig 2/5/6/7/8) from the bundle into `docs/figures/paper_a/source_data/` (wired into render); Fig 6 now shows the exact-cup ±1σ seed band over 20 noise realizations (`full_cup_simulation_identifiability` surfaces per-rate seed mean/std) |
| A2-17/18 | Convert to conventional journal manuscript + full Methods | VENUE | same as A-AR01 |

## Paper B (`PAPER_B_DETAILED_REVIEW.md`)

| id | task | class | notes |
|---|---|---|---|
| B-AR10/MAJ19-21 | Result-3 robustness study + a **physical lateral-exchange operator** | **PARTLY DONE** | `ntube_robustness_study` (sweeps+conservation+trajectory) + **Fig 5 redesigned** (2026-07-13: trajectory / N-timestep convergence / lateral×control contingency / supp. floor audit, AR-B2-21). STILL OWED: a physical transverse-Darcy lateral operator + a formal Jacobian/finite-time-Lyapunov growth analysis (deep modeling; Result 3 stays exploratory until then) |
| B-MAJ23/AR15 | Single-source `puckworks/paper_b/build.py` results bundle | **DONE** (2026-07-12) | `compute` runs Result-1/2/4 (RSM, Result-1 trend, κ(t) ladder, cross-pressure, LOPO) ONCE into `docs/figures/paper_b_results.json` (provenance-stamped); `verify` (fast) checks 12 manuscript numbers vs the bundle + writes a manifest (commit, env, 4 data SHA-256). Guarded by `test_paper_b_build_verifies_manuscript_claims`. Owed: migrate the live figures to consume the bundle (currently recompute); Result-3 sweep stays out (slow); env lockfile + tag |
| B-AR01/MAJ01 | Full conventional manuscript (Introduction/Data-and-observation-operators/Methods/Results/Discussion/Data-availability/References); remove project-management prose + status section | VENUE | large writing; venue-dependent; §9 of the review proposes an architecture |
| B-AR16/MAJ23 | Execute the systematic related-work/novelty search | BLOCKED-EXTERNAL | scaffold exists (`docs/PAPER_B_RELATED_WORK.md`); DB execution is a PI action |
| B-release | Frozen Paper B tag + pinned environment + archival DOI | DEFERRED-DECISION | at submission |
| B-MAJ07-partial | Fig 1 run-level jittered extraction-run points (vs cell means) | **DONE** (2026-07-12) | `schmieder_tds_ey` already surfaces `ey_replicates`; Fig 1(a) now overlays the individual per-run EY points (deterministic jitter) behind the cell means, making the run-to-run spread and small n (3; 6 at centre) visible -- the wide 1.4-dial cell is now honest |

## What is already DONE (do not redo)
- **Paper A P0 (all):** SSE/MAPE objective consistency, curvature-coupling rename, LOCO
  dependence-aware bootstrap, joint-fit full precision, matched-endpoint bracket + guard
  test, Waszkiewicz time-origin bug, same-model-simulation rescope, g/L units, honest
  `compute_all`. **Paper A P1:** Fig 1 taxonomy, Fig 2 normalized surface + profile row +
  colorbar, Fig 5 comparator, interval-operator weighting fix.
- **Paper B P0:** cross-pressure full-precision bug, κ(X) vs κ(XᵀX) relabel, fixed-design
  residual bootstrap + vertex-validity fractions, sign/LOPO/regime narrowing, Foster
  panel relabel, Fig 4 neutralisation, experimental-unit hierarchy correction, **MAJ-04**
  achieved-predictor RSM refit, **MAJ-09** data-driven Figure 2.
- See ROADMAP §7.1 (2026-07-12/13 entries) for the full changelog and commit trail.

## Paper A (`PAPER_A_THIRD_DETAILED_REVIEW.md`, 2026-07-13)

### DONE this round (code + manuscript + figures, committed)
| id | task | notes |
|---|---|---|
| A3-01 | Null-benchmark skill package | `transfer_skill_vs_baselines`: O-trained MAPE-optimal constant + same-(T,p) O lookup vs the mechanistic O→C/F transfer, full precision. Finding CONFIRMS the review: pooled model **8.2 %** vs constant **8.6 %** → skill **≈4 %**, model worse than the constant on **50/108** held-out points. In the bundle + 3 build claims + test + Fig 4 panel (c). Abstract/Result 3/Discussion rewritten around it |
| A3-03 | Round-before-aggregate defects | `geometry_sensitivity_transfer` (was integer-rounded → **0.6 pp** at full precision), `joint_multigrind_fit` (`independent_mean_raw`; indep mean from raw), `refit_pannusch_angeloni` (`mape_holdout_raw`). Regression tests added |
| A3-04 | Boundary censoring + language | panel now returns `profile_lower/upper_censored`, `profile_log_width_censored`; "no bounded minimum" removed from abstract/Result 2 ("interior minimum, but the 10 % set is right-censored"); Fig 2 shows a right-open arrow |
| A3-09/A3-12 | SSE↔MAPE overlap replaces binary flag | panel returns `sse_mape_threshold_jaccard` (0.86 caffeine) + `sse_mape_best_rate_log_distance`; `mape_cross_check_agrees` now derived from Jaccard≥0.5 |
| A3-06/A3-23/A3-32 | Evidence-taxonomy sync | `joint_multigrind_fit` → in-sample compatibility (not "REAL transfer test"/"transfers reasonably"); `validate_refit_granulometry` verdict → null-benchmark caveat; `external_waszkiewicz` → "target-profiled external shape test" (not "Frozen external prediction"), cup flatness labelled algebraic. Terminology guard test added |
| A3-05 (part) | Figures | Fig 4 redesigned with the null-baseline skill panel + neutral title + matched-volume label; Fig 2 censoring arrow + MAPE-fraction/Jaccard annotation + neutral title |
| A3-07 (part) | Matched-volume terminology | abstract/Result 1/Fig 4 now say "matched beverage endpoint (40 mL matched-volume proxy)" (endpoint-mass sensitivity already run last round, A2-09) |
| A3-14 (part) | Ratio wording | manuscript uses profile fraction/width directly; identifiability.py already labels the ratio a descriptive range-dependent proxy |

### UNBLOCKED-LARGE remaining (deferred; can be done later)
| id | task | notes |
|---|---|---|
| A3-02 | Grid-converged / continuous profile-wise PREDICTION set; threshold sensitivity | **DONE** (2026-07-13) | `validate_refit_granulometry.threshold_sensitivity` sweeps the near-optimal set at 2/5/10/20 % (set size + worst held-out MAPE; caffeine ~8.5→9.7 %); the SSE-profile grid/continuous convergence was already done (A2-06/MAJ-04) |
| A3-11 | Condition-wise prediction envelopes across the profile set | **DONE** (2026-07-13) | `condition_envelopes`: per-(T,p) pred min/max/median across the 10 % set + envelope width as a fraction of obs (median ~3 %, worst ~16 %). Fig 4 (a,b) draw the vertical envelopes; build claim + test + Result 3 sentence |
| A3-05 (rest) | Fig 6 external tier; Fig 3 residual-vs-(T,p); Fig 5 reduced-model ladder | **DONE** (2026-07-13) | Fig 6 → 3 tiers with the external Waszkiewicz shape-test panel; Fig 3 → obs-vs-pred + signed-residual-vs-(T,p) panels; Fig 4 → null-baseline skill panel + condition envelopes; Fig 5 → reduced-model ladder panel (d). Remaining figure nicety: vector (PDF/SVG) export (part of A3-08 release, DEFERRED) |
| A3-15/A3-16 | Same-model simulation off-grid truth + realistic noise + continuous fit | **DONE** (2026-07-13) | `full_cup_simulation_offgrid_noise`: truth at off-grid rates 0.7/1.15/1.8, dense 41-pt grid + parabolic (continuous) recovery, under iid/heteroscedastic/correlated per-shot noise. Fraction recovers to mean **0.2%** vs cup **15.1%**; fraction beats cup in **9/9** cases → the contrast is not an artefact of an on-grid true rate or iid noise. Bundle + 2 build claims + test + §6 sentence (model discrepancy was already A-MAJ13) |
| A3-13 | Table 7 quantitative intersection (inventory band → implied rate range) | **DONE** (2026-07-13) | `table7_rate_constraint`: PDE-free intersection of the profiled valley c*(rate) with the Table 7 inventory. Caffeine 12.54 g/L → implied rate ≈**0.95**, ±10% inventory band **≈0.6–1.75** (interior, unique) → an orthogonal same-campaign inventory COLLAPSES the broad rate profile. In the bundle + build claim + test + Result 2 sentence |
| A3-19 | Reduced-model ladder for the joint fit (Model 0–3, parameter counts) | **DONE** (2026-07-13) | `reduced_model_ladder`: means 7.1→5.1→6.4→4.9 % (1/3/2/6 params); the 2-param shared mechanistic model beats the 3-param per-grind constant in **0/6** fits. Fig 5 panel (d) + build claim + test + Result 3 sentence |
| A3-24 (rest) | More contract tests (figure/result sync) | **MOSTLY DONE** (2026-07-13) | Added tests for precision (geometry/joint), null-benchmark skill, censoring+Jaccard, condition envelopes+threshold, reduced-model ladder, Table 7 intersection, off-grid+noise sim, and a stale-taxonomy guard. Remaining: an explicit figure-renders-from-bundle smoke test (minor) |

### BLOCKED-EXTERNAL / VENUE / DEFERRED (not actionable here)
- **A3-12/6.13, A3-21** replicate-level RSD / heteroscedastic weighting — needs source re-intake (same as A-MAJ22).
- **A3-08, A3-27(bib), 6.35–6.40, §7** full manuscript conversion (equations, Methods, bibliography, remove review IDs/ledger) — VENUE; large writing.
- **A3-08(release)** frozen `paper-a-v1.0.0` tag + env lock + DOI + vector figures — DEFERRED to submission RC.
- **A3-06(likelihood)** likelihood-based profile confidence/prediction intervals — needs a specified noise model (out of scope by design).

## Paper B (`PAPER_B_CURRENT_DETAILED_REVIEW.md`, 2026-07-13)

### DONE this round (code + manuscript + figures, committed)
| id | task | notes |
|---|---|---|
| MAJ-33/B3-13 | Result-3 conservation audit was final-step-only, mislabeled "max"/"every step" | `ntube_kappa_t_union` now has a FULL-TRAJECTORY `conservation_audit`: running extrema over every substep of raw conductance/relative-flow/age + share-sum max deviation; honest control-law fact (raw total flow conserved under FLOW control, FREE under PRESSURE). Test + build claim |
| MAJ-34/39/40/41/B3-15/16 | "factorial" mislabel; 6-12 vs 6-11; mixed axes; N_eff not normalized | `ntube_robustness_study` → OFAT + a crossed control×lateral×closure design (design_type="NOT a full factorial"); pressure range from config [6,11]; invariance SEPARATED per axis type (numerical/stochastic/operating vs physical contingencies); `n_eff_over_N` added |
| MAJ-17/B3-08 | Jensen "exact gap" used EY(1) after clipping shifts E[K]≠1 | now uses the actual post-clip evaluated mean E[K] (shift ≤0.005); sign conclusion unchanged; build claim |
| MAJ-12/13/§5.5/B3-05/07 | Deletion + wild-bootstrap + model-form "owed" | new `schmieder_rsm_diagnostics` reproduces the review's leave-one-run (1.736-1.765), leave-one-setting (1.720-1.777, 15/15), exp-10 Cook's D 0.441/leverage 0.187, wild Rademacher+Mammen, AICc (full-quad vertex 1.737). In bundle + 2 claims + test + Result-1 prose |
| MAJ-14/B3-03 | Q² not frozen | `rsm_lopo` (Q²≈0.470) frozen in the bundle + claim |
| MAJ-04/05/06/B3-02/03/28 | Stale/dirty bundle; narrow hashes; incomplete | bundle now includes rsm_diagnostics/rsm_lopo/channeling_audit/ntube_robustness; 10 input hashes; `release` mode / strict verify FAILS on stale/dirty tree (`release_fresh`); routine claim check unaffected. 16/16 claims |
| MAJ-42/MAJ-35/B3-16 | Fig 5d wrong "(panel c)" cross-ref; endpoint saturation ≠ convergence | Fig 5d now plots MEASURED N_eff (floor-indep) beside the closed-form gain; panel b relabeled endpoint saturation |
| MAJ-26/B3-12 | Prose relies on LOPO but Fig 3c showed only shared calibration | Fig 3c now overlays the LOPO held-out RMSE by pressure (open markers) for all three branches + manuscript ref |
| MAJ-21/28/09/30/02/07 | wording | "0p"→"0 fit Q(t)"; "regime-dependent"→"errors vary continuously with pressure"; "raw cells"→"source-derived run-level endpoint estimate"; swelling sign-vs-magnitude; title→"Limits of mechanism discrimination…"; test docstring made operational |

### UNBLOCKED-LARGE — now DONE
| id | task | resolution |
|---|---|---|
| MAJ-36/B3-14 | N-tube early-switching: physical-time axis + smaller-timestep + event-time convergence | `ntube_switching_convergence` reruns the baseline at 4/8/16/32/64 substeps and reports collapse-time convergence (~2.9 s, spread ≲0.1 s → a CONVERGED physical event, not a stepping artefact); trajectory now carries `time_s_trajectory`/`collapse_time_s`; Fig 5a on a physical-time axis. In bundle + claim + test + manuscript |
| MAJ-38/B3-26 | >4 stochastic realisations + normalized concentration metrics (entropy/Gini/top-k) | 16 seeds; `concentration_metrics` (N_eff/N, normalized entropy, Gini, top-1/top-decile share, collapse time); `stochastic_distribution` (N_eff/N median+p5/p95, entropy, collapse range). In bundle + claim + test + manuscript |
| MAJ-23/B3-23 | Result-2 residual ACF plots + block/prequential bootstrap uncertainty | `result2_residual_diagnostics`: per-branch residual ACF (lag-1≈0.99), moving-block bootstrap (8 s blocks): Φ(t) beats best constant by −0.39 g/s CI [−0.60,−0.23] (excludes 0) but TIES the flexible cubic (+0.02, [−0.01,+0.05], straddles 0); ranking persists across 3 windows. In bundle + claim + test + manuscript |
| MAJ-16/B3-19 | Fig 1 RSM bootstrap band + run-point visibility | `schmieder_rsm_diagnostics().curve_band` iid-residual bootstrap envelope drawn on Fig 1 (done earlier, commit 23eb396) |
| MAJ-20/B3-20 | Fig 2 full evidence data dictionary (per-status fields + citations) | added `citation` column to `paper_b_evidence_matrix.csv`; new `paper_b_evidence_dictionary.csv` defines every status token + its ROADMAP §0 rung; `fig2_evidence_dictionary_md` exports the published legend; `paper_b_evidence_dictionary_audit` gate asserts no undefined token / uncited mechanism. In data hashes + test + manuscript |

### BLOCKED-EXTERNAL / VENUE / DEFERRED
- **MAJ-01/B3-01, §11 editorial, B3-31/32/33** full manuscript conversion (remove open-gaps/status, add Methods/References/Data-availability, self-contained captions) — VENUE.
- **MAJ-24/B3-11** source replicate-trajectory uncertainty — partly BLOCKED-EXTERNAL (a `tds_fractions_replicates.csv` exists but full propagation is a re-intake).
- **MAJ-27/32** second-rig / second-coffee external transfer — BLOCKED (no second rig).
- **MAJ-44/B3-27** physical transverse-Darcy lateral operator + Jacobian/Lyapunov — BLOCKED deep research (shared with B-AR10).
- **B3-29** vector (PDF/SVG) figures; **B3-02** frozen release tag — DEFERRED to submission RC.
- **B3-34** systematic related-work/novelty search — BLOCKED-EXTERNAL (PI/DB action).

---

## Visualizer.coffee intake (0.13 / Sprint D5, 2026-07-13)

Phase-0 data intake + ingestion tool (NO registry component, NO physics gate). The
tool + two-tier store + card + manifest rows landed and are committed (ROADMAP §7.1,
SPRINTS D5); what remains is external/local, not actionable in-repo.

### DONE this round (committed)
- Harvester `puckworks/lib/visualizer_harvest.py` (`[harvest]` extra; lazy `requests`);
  two-tier `normalize_shot` (hydraulic vs outcomes SEPARATE; SI at boundary + rule-7
  flags; privacy drop + salted user-id hash); rate-limited resumable crawl.
- Loaders (`visualizer_index` / `visualizer_iter_shots` / `visualizer_hydraulic` /
  `visualizer_outcomes`), PROVENANCE, gitignore, 2 MANIFEST rows, data-only card
  `visualizer_coffee`, DERIVED `aggregate_stats.csv` (zero-state), 14 offline tests.
- Miha Rekar corpus-use request email DRAFTED (`docs/sourcing/VISUALIZER_MIHA_CORPUS_REQUEST_EMAIL.md`).

### BLOCKED-EXTERNAL / TB / DEFERRED (not actionable here)
- **Miha Rekar reply** — sanctioned bulk/research use of the corpus (**SENT 2026-07-13 by Tim, awaiting reply**). BLOCKED-EXTERNAL: gates **redistribution / publication** use only; the public-API harvest works without it. If a sanctioned bulk export is offered, prefer it over API paging. §5.8.
- **Populate the corpus (TB, local)** — the corpus is gitignored / not redistributed, so it is NOT populated in-repo. Tim runs `python -m puckworks.lib.visualizer_harvest full` locally, then `stats --write-aggregate` to replace the zero-state `aggregate_stats.csv`. Until then all coverage numbers are 0 by construction.
- **G3/P2/P6 ecological consumers** — UNBLOCKED-LARGE but downstream: build the population pump/flow (P–Q) envelope, the Fo_F population, and the PV-06/PV-17 at-scale companion ON the harvested corpus. Deferred until the corpus is on disk (and, for any published use, until the Miha reply lands). Reference-strength / selection-biased — the label rides along, never upgrades a controlled result.

---

## Paper A (`PAPER_A_FOURTH_DETAILED_REVIEW.md`, 2026-07-13)

Many 4th-review findings were already resolved by prior rounds (A3-03/MAJ-12 added
`_raw` fields to refit/joint/geometry/flow; Fig 4 already carries a level-only
baseline; "matched 40 g" already softened). The still-present DEFINITE defects are
DONE below; the large additions + conversion are deferred.

### DONE this round (committed)
- **A4-06** precision: `gate_pannusch_angeloni_per_condition` / `endpoint_mass_sensitivity`
  now aggregate overall MAPE + spread + helps/hurts sign from RAW values (`_raw` fields).
- **A4-33** verdict strings neutralised (per-condition note, endpoint verdict).
- **A4-08** Fig 8 title withdrew the logically-false "a level rescale cannot remove"
  claim; **A4-31** Fig 7 "trajectory" → "cross-condition correlation (n=9)".
- **A4-09** figure-count drift fixed (manuscript/docstring/README declare 8; new test).
- **A4-01/34/35** build strict release (fails dirty/stale) + `release_fresh`/
  `bundle_matches_head` + code+manuscript hashes + freshness/figure-count tests.
- **A4-05** "40 mL proxy" labelling; **A4-16/42** wording already correct.

### UNBLOCKED-LARGE (deferred; computable now but substantial)
- **A4-03 / §4 / §10.1 — baseline-relative transfer skill (the central finding).** A
  full-precision O-trained constant / same-(T,p) O lookup / shared+per-grind constant
  baseline module reporting skill = 1−L_model/L_baseline, paired loss diffs, and win
  counts; then rewrite Result 3 + abstract baseline-relative (remove "reasonable"). The
  review's own diagnostic: model ≈ level-only (8.23 vs 8.59; worse in 5/12). **Top item.**
- **A4-04 / §6.8** `cross_grind_endpoint_sensitivity` — refit O + transfer C/F per
  endpoint×density (the current sweep tests only the blind residual).
- **A4-07 / §6.12** continuous/converged profile-set → condition-wise C/F envelopes.
- **A4-10/11/12** Fig 3/4 source-data export + Fig 4 baseline/envelope redesign + Fig 2
  MAPE panel & censoring marks. **A4-17** Hessian sensitivity table. **A4-21** joint null
  ladder. **A4-27/28** off-grid sim + discrepancy in figures. **A4-37** vector figures.

### BLOCKED-VENUE / EXTERNAL
- **A4-14/49, §7.1/7.20/7.22/7.23, A4-40/41/50** full journal manuscript conversion,
  references, declarations, completed novelty search — VENUE/PI.
- **A4-15** clean tagged release + pinned env/container — TB/infra (build strictness done).
- **A4-25 / §10.11** replicate/RSD propagation — BLOCKED-EXTERNAL (source re-intake; = A-MAJ22).

## Paper B (`PAPER_B_FIFTH_DETAILED_REVIEW.md`, 2026-07-13)

### DONE this round (committed)
- **B5-03** Jensen formula + range + mean-shift corrected (code + prose; added
  `min_jensen_gap_EYpt`; worst = most negative, −4.64..−1.38).
- **B5-04/05** Result-2 block step relabelled a conditional block resampling of fixed
  losses; "statistically indistinguishable" → "not resolved by this conditional interval".
- **B5-06** stale RC-3b/phi cross-pressure numbers regenerated from the bundle.
- **B5-07** Schmieder CSV schema-contract test (36 exp-15 corner-point design rows pinned
  separate from 576 valid runs; no silent filtering).
- **B5-08/10** N-tube switching-convergence scoped to collapse-time-under-Euler; dropped
  "tight distribution"; reported event-time variability + two-channel seeds.
- **B5-02** (Paper B strict release already exists from the MAJ-04 work).

### UNBLOCKED-LARGE (deferred)
- **B5-08-full** real trajectory-convergence study (interpolated common grid, norms,
  event-time error vs spatial+temporal refinement, higher-order/adaptive solver).
- **B5-09** N-tube state classifier redesign (explicit single/oligarchic/distributed/
  transient thresholds on top-1 share, N_eff, entropy, persistence).
- **B5-24/25/26/27/28** N-tube physical balances (solute inventory, pressure-work,
  lateral-flux, age), donor-extrapolation audit, event-time + start-state sensitivity.
- **B5-13/14/15/16** RSM leverage-adjusted wild bootstrap, post-selection uncertainty,
  design-support, first-stage endpoint propagation.
- **B5-18/20** block-length sensitivity + residual-ACF figure. **B5-31** Fig 2 ontology.
- **B5-33/34/35/36** template prose/figures from the frozen bundle + full dependency manifest.
- **B5-39/40/44/45** figure reworks + complete source data + vector figures.

### BLOCKED-VENUE / CARD
- **B5-01** clean tagged release — TB. **B5-11** manuscript conversion — VENUE.
- **B5-29** physical transverse-Darcy lateral operator — CARD-BLOCKED (rule 1; = G-lat/PV-14).
- **B5-43** systematic novelty search — PI. **B5-32** DOI verification — needs source check.
