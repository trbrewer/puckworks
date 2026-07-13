# Provenance — pocketscience2024 (radially sectioned edge/center extraction yield)

**Card:** `docs/cards/pocketscience2024.md` (verdict: data-only; no model, no gate
against the source itself).

**Source.** Pocket Science Coffee (pseudonymous author), "Espresso Water Flow Part 1:
Dispersion, Puck Screens and Baskets," blog post, 27 Feb 2024. Plots and Monte-Carlo
error analysis by Jonathan Gagné. **No DOI; not peer-reviewed.** A destructive-sectioning
experiment on a Decent DE1 measuring edge vs. center extraction yield across dispersion
block (brass/teflon), puck screen (Y/N), basket (VST18 / Sworks High Flow), and shot
style confounded with grinder (Niche↔traditional, Superjolly MP64↔turbo).

## What is tracked here (derived, card-faithful)
- `edge_ey_condition_means.csv` — the 12-condition summary table transcribed **from the
  card** (§Parameters). Columns: basket, shot_style, grinder, puck_screen,
  dispersion_block, ey_center_pct, ey_edge_pct, edge_yield_loss_pct (fractional edge loss
  ×100, negative = edge under-extracted), shot_ey_filtered_pct, outer_mass_frac_of_dose,
  n_shots (`4-5`; 5 nominal, 3 rejects across the 60-shot campaign, excluded), provenance.
  Units: percent throughout (registry EY %); no SI conversion (dimensionless yields).
- `lrr_scalars.csv` — grinder-level liquid-retained-ratio means (Niche 3.38, Superjolly
  MP64 3.30; n=5 each), lumped post-flush retention. **NOT** an in-shot dead-water figure
  and **NOT** a retention curve θ(ψ): does not satisfy the G1 search target.

## What is NOT tracked (raw workbook)
The raw `Espresso water flow experiment.xlsx` (3 sheets, 60 shots × ~47 columns), the
per-sheet CSVs, and the source PDF are held locally under this directory but are
**gitignored, not redistributed** — the workbook is a pseudonymous hobbyist artifact with
**no explicit data-use license** (public blog download ≠ redistribution grant). This
mirrors the `pannusch2024` / `visualizer` precedent. If a per-shot transcription check or
finer analysis is needed, the raw sheets are available locally for that work.

## Carried corrections / caveats (from the card)
- **Column-label erratum:** the VST18 raw sheet labels its 0.31 as "outer to inner section
  ratio by mass," but the values (outer 5.56 g / dose 17.9 g = 0.31) show it is
  outer-to-**total** — the same quantity as the Sworks sheet's correctly labeled 0.34. The
  derived CSV carries the corrected meaning (`outer_mass_frac_of_dose`).
- Raw-mean edge losses here differ from Gagné's Monte-Carlo figures (e.g. worst −32% here
  vs. ~−37% combined in his Fig. 3): two readings of the same raw data (different
  resampling + scaling). The tracked table is the raw condition means.
- Section EYs are anchored to shot EY **by construction** (not independent of the beverage
  measurement); two-zone radial resolution only (no depth); single DE1; shot style
  confounded with grinder; VST18×brass cells absent (12 of 16).

## Registry use (offline only)
Validation target for any future radially resolved bed_dynamics/extraction variant
(reproduce the sign structure: large negative edge loss only for traditional basket ×
traditional shot × no screen; near-zero for modern basket + screen) and a prior-shaping
caution for `brewer2026.streamtube` σ (a grind-driven lognormal σ silently absorbs this
boundary-condition heterogeneity when calibrated on shot-level data). No contract consumes
it under v0.1 (no radial coordinate / inlet-uniformity field). **Does not close G1 or G9.**
