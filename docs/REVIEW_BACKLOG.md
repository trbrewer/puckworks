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
| A-MAJ04 | Grid-density / domain robustness appendix for the identifiability panel (18/36/72/144 rate grids; ≥2 domains; continuous 1-D optimisation; boundary reporting) | UNBLOCKED-LARGE | core rename + log-width + MAPE cross-check already done; the convergence *appendix* (multi-grid reruns) remains |
| A-MAJ13 | Positive-control model-discrepancy variant (altered geometry/flow/IC between data-generation and fitting) | **DONE** (2026-07-12) | `full_cup_simulation_discrepancy`: truth generated at T+ΔC (Arrhenius-nonlinear) × flow-scale, fit at nominal, sweeping rate only. DOSE-RESPONSE: moderate (T+4, ×1.10) leaves an irreducible MAPE floor ~4.8% (>> 3% noise) while the located rate stays ROBUST at 1.0; larger (T+8, ×1.25) raises the floor AND biases the located rate to 1.4 in 100% of seeds → a sharp minimum is necessary-not-sufficient. Both doses in the bundle + 2 build claims + `test_discrepancy_control_dose_response` |
| A-MAJ17 | Residual-diagnostic faceted figures (residuals vs T/p, normalized within variety×solute series; per-group metrics) | **PARTLY DONE** (2026-07-12) | Fig 7 (`fig7_per_group_diagnostics`) delivers the per-GROUP metrics — variety×solute blind vs inventory-matched MAPE + trajectory-shape correlation (n=9/group), making visible that inventory-matching helps caffeine but HURTS trigonelline. STILL OWED: the residual-vs-(T,p) SCATTER needs the per-condition residual VECTORS surfaced through the harness (only per-group summaries are currently in the bundle) |
| A-AR13/MAJ19 | Strict one-command `puckworks/paper_a/build.py` | **DONE** (2026-07-13) | `verify` (fast) checks 13 manuscript claims vs the bundle + writes a provenance manifest (commit, env versions, 6 data-file SHA-256, bundle hash); `full` recomputes+renders+verifies. Guarded by `test_paper_a_build_verifies_manuscript_claims`. Owed: an env lockfile (uv/poetry) + the release tag |
| A-MAJ22 | Recover replicate-level Angeloni/Schmieder uncertainty; uncertainty-weighted objective sensitivity | BLOCKED-EXTERNAL | repo has condition-level means; needs source re-intake |
| A-AR15/MAJ21 | Execute the full Scopus/WoS systematic novelty search; populate the evidence matrix | BLOCKED-EXTERNAL | scaffold exists (`docs/literature_search/`); DB execution is a PI action |
| A-AR14/MAJ20 | Frozen `paper-a-v1.0.0` tag + pinned environment + archival DOI | DEFERRED-DECISION | `tag_now:false` — create at submission RC step |
| A-AR01 | Full conventional manuscript prose (Methods equations, references list, figure captions) | VENUE | manuscript form depends on target journal |
| A2-06/07 | Grid-density/domain convergence for the identifiability panel | **DONE** (2026-07-13) | `identifiability_panel_convergence`: κ 1924/2069/2067 across 18/36/72 grids, flat valley on [0.3,3]+[0.1,10], threshold right-censored. Still owed: 144-pt grid + continuous 1-D optimiser (marginal) |
| A2-08 | Uncertainty-weighted / heteroscedastic objective sensitivity using source RSD | BLOCKED-EXTERNAL | needs replicate-level RSD (same as A-MAJ22) |
| A2-09 | Density / 40 g-vs-40 mL endpoint sensitivity (38–42 g range) | **DOCUMENTED** (2026-07-13) | Methods now state the 40 g≈40 mL approximation (~0–2 % density + ±5 % tolerance), level-robust MAPE absorbs a common shift; the per-endpoint sweep remains a bounded owed check |
| A2-10 | Propagate constructed pressure–flow-map uncertainty | **DONE** (2026-07-13) | `flow_map_sensitivity_transfer`: a systematic ±20% flow-scale perturbation (refit O, transfer C/F) moves held-out MAPE ≤0.6 pp; transfer robust to flow-map MAGNITUDE, still conditional on the inferred-map FORM. Owed: a per-shot measured flow trace |
| A2-13b | Waszkiewicz sensitivity matrix (temperature, flow floor, density, alignment) | **DONE** (2026-07-12) | `waszkiewicz_sensitivity` sweeps temperature 89-95 C × flow floor 0.02-0.10 (12 cells): the localization conclusion is INVARIANT — every cell keeps the 12-fraction range ratio 1.9-2.0× while the single cup NEVER discriminates; best-rate point shifts only 0.4→0.6 (temperature rescales the level, not the cup-vs-fraction contrast). In the bundle + guarded by `test_waszkiewicz_sensitivity_localization_invariant` + a build claim. Time-alignment already swept (offset 0/2/4 s); density (40 g≈40 mL) documented in A2-09 |
| A2-16 | Further figure redesigns (residual panels, source-data export, seed distributions on Fig 6) | **PARTLY DONE** (2026-07-12) | Fig 7 per-group residual-diagnostic panel added (see A-MAJ17). STILL OWED: source-data CSV export alongside each figure + seed-distribution bands on Fig 6 |
| A2-17/18 | Convert to conventional journal manuscript + full Methods | VENUE | same as A-AR01 |

## Paper B (`PAPER_B_DETAILED_REVIEW.md`)

| id | task | class | notes |
|---|---|---|---|
| B-AR10/MAJ19-21 | Result-3 robustness study + a **physical lateral-exchange operator** | **PARTLY DONE** | `ntube_robustness_study` (sweeps+conservation+trajectory) + **Fig 5 redesigned** (2026-07-13: trajectory / N-timestep convergence / lateral×control contingency / supp. floor audit, AR-B2-21). STILL OWED: a physical transverse-Darcy lateral operator + a formal Jacobian/finite-time-Lyapunov growth analysis (deep modeling; Result 3 stays exploratory until then) |
| B-MAJ23/AR15 | Single-source `puckworks/paper_b/build.py` results bundle | **DONE** (2026-07-12) | `compute` runs Result-1/2/4 (RSM, Result-1 trend, κ(t) ladder, cross-pressure, LOPO) ONCE into `docs/figures/paper_b_results.json` (provenance-stamped); `verify` (fast) checks 12 manuscript numbers vs the bundle + writes a manifest (commit, env, 4 data SHA-256). Guarded by `test_paper_b_build_verifies_manuscript_claims`. Owed: migrate the live figures to consume the bundle (currently recompute); Result-3 sweep stays out (slow); env lockfile + tag |
| B-AR01/MAJ01 | Full conventional manuscript (Introduction/Data-and-observation-operators/Methods/Results/Discussion/Data-availability/References); remove project-management prose + status section | VENUE | large writing; venue-dependent; §9 of the review proposes an architecture |
| B-AR16/MAJ23 | Execute the systematic related-work/novelty search | BLOCKED-EXTERNAL | scaffold exists (`docs/PAPER_B_RELATED_WORK.md`); DB execution is a PI action |
| B-release | Frozen Paper B tag + pinned environment + archival DOI | DEFERRED-DECISION | at submission |
| B-MAJ07-partial | Fig 1 run-level jittered extraction-run points (vs cell means) | UNBLOCKED-LARGE | needs run-level points surfaced through the harness; cell means + achieved-predictor curve + ddof wording already fixed |

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
