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

## Paper B (`PAPER_B_DETAILED_REVIEW.md`)

| id | task | class | notes |
|---|---|---|---|
| B-AR10/MAJ19-21 | Result-3 robustness study + a **physical lateral-exchange operator**: convergence in N/timestep/solver/horizon; multiple network realisations; pressure×grind×closure sensitivity; feedback-link ablations; N_eff(t)/max-share/total-flow/mass-balance trajectories; consistent flow- vs pressure-control machine model | UNBLOCKED-LARGE | the most substantial remaining unblocked scientific item; until done, keep Result 3 explicitly exploratory |
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
