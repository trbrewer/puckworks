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

## ⚠ 1.5 grind-map data gap (discovered building Sprint 1)
`wadsworth2026_table1.csv` contains only the **permeability** columns
(`R_m` = the k-relevant Sauter/volume radius, `phi_p`, `s_p`, `k_m2`). Fitting
`R_m = βG + R₀` gives β≈5.8e-5 / R₀≈1.4e-4 — **not** the paper's 4.3505e-5 /
1.0160e-4, because `R_m` is ~1.3–1.45× the grind-map **area-equivalent mean
⟨R⟩** on both coffees. So the card's statement that ⟨R⟩, ⟨R²⟩, ⟨R³⟩, S "are
already in `data/wadsworth2026_table1.csv`" is **incorrect** — those grind-map
columns were never transcribed.
- **Need for 1.5:** the grind-map columns of the paper's Table 1 — ⟨R⟩
  (area-equivalent-circle mean), ⟨R²⟩, ⟨R³⟩, S per G per coffee — OR the 0.6
  22-sample PSD zip (compute the moments directly).
- **Drop:** add them as columns to `wadsworth2026_table1.csv` (or a new
  `wadsworth2026_grindmap.csv`). Then the β,R₀ refit and S(G) monotonicity gates
  can run. 1.2 already landed; 1.5 waits on this.

## ✅ Card provenance confirmed (Tim, 2026-07-10)
`wadsworth2026_grindmap.md` and the permeability paper share DOI
`10.1098/rsos.252031` because **one paper covers both** the grind map and the
permeability model. No card error. (Was flagged during D1; now resolved.)
