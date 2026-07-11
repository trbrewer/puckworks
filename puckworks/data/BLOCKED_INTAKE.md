# Phase 0 intake — blocked / pending items

CC environment reaches Zenodo + the Mendeley public API, but **MDPI** and
**Royal Society** are Cloudflare-403, and the Mendeley *bulk* download / any
subfolder is not exposed by the public API. Per SPRINTS.md D1 note, those need
Tim to download and drop files. Running status:

## 0.1 — Schmieder / Pannusch — ✅ RESOLVED (Tim drop 2026-07-10)
- **Schmieder kinetics: DONE.** Tim dropped the *Foods* 12, 2871 supplementary
  + full-text XML → parsed to `schmieder2023/` (Tables A1/2/3 + S1/S2, exact).
- **Pannusch Mendeley repo: on disk, gitignored.** Table 2 fitted params, dry
  PSD, and control-chart values are **deferred to item 1.8a** (the `.mat` files
  hold MATLAB `table` objects scipy can't parse). See
  `pannusch2024/PROVENANCE.md`. Not needed for any Sprint-1 gate.

## 0.6 — Wadsworth 22-sample PSD zip — ⏳ PENDING AUTHORS
- Table 1 moments already in `wadsworth2026_table1.csv` (+ 8.1e17→8.1e-17 m²
  erratum recorded). The full **22-sample PSD zip (R, R_min, R_max)** does **not
  appear to be published** with the paper (R. Soc. Open Sci. 13, 252031); RS is
  Cloudflare-403 here and it is not on figshare/Dryad. **Tim has requested it
  from the authors** (2026-07; log under ROADMAP §5.8 correspondence).
- **Drop when received** → `puckworks/data/wadsworth2026_psd/`. Not hard-blocking
  1.5 (its gate uses Table 1, in repo); it feeds pack_generator PSD inputs.

## ✅ 1.5 grind-map data — RESOLVED (Tim drop 2026-07-10)
Tim supplied the full Table 1 → `wadsworth2026/wadsworth2026_table1_full.csv`
(22 rows, ⟨R⟩/⟨R²⟩/⟨R³⟩/S + porosity/connectivity/surface/k). `wadsworth2026.
grindmap` landed & gated. NOTE: the earlier `wadsworth2026_table1.csv` held only
the permeability columns (its `R_m` is the k-relevant radius, ~1.3× the grind-map
⟨R⟩) — the card's claim that ⟨R⟩/S were in that file was wrong; the full file
fixes it.

### ✅ Card β,R₀ typo corrected (2026-07-11)
An OLS refit of the full Table 1 ⟨R⟩ column gives **β=5.805e-5, R₀=1.380e-4
(R²=0.994)**, not the previously-printed **4.3505e-5 / 1.0160e-4** (~1.33×
shallower). Confirmed by Tim as a typo; the card of record now carries the
corrected values and the component's `BETA_CARD/R0_CARD` match the refit
(`gate_grindmap_refit` reports `card_reproduces=True`).

### Still pending: raw 22-sample PSD zip (feeds pack_generator, not 1.5)
The full R/R_min/R_max distributions remain requested from the authors.

## ✅ Card provenance confirmed (Tim, 2026-07-10)
`wadsworth2026_grindmap.md` and the permeability paper share DOI
`10.1098/rsos.252031` because **one paper covers both** the grind map and the
permeability model. No card error. (Was flagged during D1; now resolved.)
