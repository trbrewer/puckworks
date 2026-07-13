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
| A-MAJ13 | Positive-control model-discrepancy variant (altered geometry/flow/IC between data-generation and fitting) | UNBLOCKED-LARGE | multi-seed distribution already delivered; the discrepancy scenario is new analysis |
| A-MAJ17 | Residual-diagnostic faceted figures (residuals vs T/p, normalized within variety×solute series; per-group metrics) | UNBLOCKED-LARGE | new figure + per-group aggregation |
| A-AR13/MAJ19 | Strict one-command `puckworks/paper_a/build.py` (validate source hashes → run analyses → render → verify manuscript numbers → fail on stale/boundary) + env lock | UNBLOCKED-LARGE | `compute_all` completeness done; the strict wrapper + hash manifest remain |
| A-MAJ22 | Recover replicate-level Angeloni/Schmieder uncertainty; uncertainty-weighted objective sensitivity | BLOCKED-EXTERNAL | repo has condition-level means; needs source re-intake |
| A-AR15/MAJ21 | Execute the full Scopus/WoS systematic novelty search; populate the evidence matrix | BLOCKED-EXTERNAL | scaffold exists (`docs/literature_search/`); DB execution is a PI action |
| A-AR14/MAJ20 | Frozen `paper-a-v1.0.0` tag + pinned environment + archival DOI | DEFERRED-DECISION | `tag_now:false` — create at submission RC step |
| A-AR01 | Full conventional manuscript prose (Methods equations, references list, figure captions) | VENUE | manuscript form depends on target journal |
| A2-06/07 | Grid-density/domain convergence for the identifiability panel (18/36/72/144 grids; continuous 1-D optimisation; right-censored boundary labelling) | UNBLOCKED-LARGE | 2nd review; core panel + log-width already done |
| A2-08 | Uncertainty-weighted / heteroscedastic objective sensitivity using source RSD | BLOCKED-EXTERNAL | needs replicate-level RSD (same as A-MAJ22) |
| A2-09 | Density / 40 g-vs-40 mL endpoint sensitivity (38–42 g range) | UNBLOCKED-LARGE | 2nd review; currently 40 g approximated as 40 mL |
| A2-10 | Propagate constructed pressure–flow-map uncertainty (hydraulic coeffs, shot times, viscosity, alignment) | UNBLOCKED-LARGE | 2nd review; transfer currently conditional on the map |
| A2-13b | Waszkiewicz sensitivity matrix (temperature, flow floor, density, alignment) | UNBLOCKED-LARGE | 2nd review; time-origin bug already fixed |
| A2-16 | Further figure redesigns (residual panels, source-data export, seed distributions on Fig 6) | UNBLOCKED-LARGE | 2nd review; Fig 1/2/5 already redesigned |
| A2-17/18 | Convert to conventional journal manuscript + full Methods | VENUE | same as A-AR01 |

## Paper B (`PAPER_B_DETAILED_REVIEW.md`)

| id | task | class | notes |
|---|---|---|---|
| B-AR10/MAJ19-21 | Result-3 robustness study + a **physical lateral-exchange operator** | **PARTLY DONE** | `ntube_robustness_study` (2026-07-13) delivers the N/timestep/grind/pressure/realisation/lateral/control sweeps + conservation + N_eff(t) trajectory, and finds the concentration is robust to numerical/design choices but CONTINGENT on flow-control + low lateral. STILL OWED: a physical transverse-Darcy lateral operator and a formal Jacobian/finite-time-Lyapunov growth analysis; the Fig-5 redesign (trajectories/convergence panels, AR-B2-21/MAJ-21) |
| B-MAJ23/AR15 | Single-source `puckworks/paper_b/build.py` results bundle (raw + display values, provenance, seeds, hashes) with figures consuming the bundle only; headline-value tests | UNBLOCKED-LARGE | mirrors the Paper A build wrapper |
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
