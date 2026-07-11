# wadsworth2026 (grind map) — data provenance

Source card: `docs/cards/wadsworth2026_grindmap.md` (ROADMAP items 0.6 / 1.5).

**Origin:** Wadsworth et al., *"A model for the permeability of coffee pucks
validated using X-ray computed micro-tomography,"* **R. Soc. Open Sci. 13,
252031 (2026)**, DOI `10.1098/rsos.252031`, **open access CC-BY-4.0**. Confirmed
(Tim, 2026-07-10) that this ONE paper covers both the grind map and the
permeability model. `wadsworth2026_table1_full.csv` supplied by Tim 2026-07-10.

## File
`wadsworth2026_table1_full.csv` — the complete Table 1, 22 rows = two coffees
(Guayacan/Colombia, Tumba/Rwanda) × 11 Mahlkonig settings G 1–11. Columns:
`R_mean_m` ⟨R⟩, `R2_mean_m2` ⟨R²⟩, `R3_mean_m3` ⟨R³⟩, `S_polydispersivity` S,
`phi_T_total`, `phi_p_connected`, `C_connectivity`, `s_total_per_m`,
`s_p_connected_per_m`, `k_m2`, `k_err_m2`.

This **supersedes** the partial `../wadsworth2026_table1.csv` (permeability
columns only: `R_m`=⟨R⟩, `phi_p`, `s_p`, `k`). The old file is still wired to the
`wadsworth2026.permeability` gate and is left untouched (no refactor of a gated
component); the grind-map component consumes this full file.

## ⚠ Card-vs-data discrepancy (flagged, for card reconciliation)
The card prints the grind-map fit as β=4.3505e-5 m/setting, R₀=1.0160e-4 m. A
plain OLS refit of this file's ⟨R⟩ column gives **β=5.805e-5, R₀=1.380e-4
(R²=0.994)** — the card's slope is ~1.33× too shallow to span the measured
192–818 µm range. The moment columns are internally consistent (S=⟨R⟩⟨R²⟩/⟨R³⟩
reconstructs the reported S to <5e-3). The component therefore uses the
**data-refit** constants; the card's printed β/R₀ are recorded but **not
treated as validated**. Needs card reconciliation (INTAKE) — possible causes:
a different ⟨R⟩ weighting in the paper's fit, or a card transcription error.

## Still pending (0.6)
The **22-sample raw PSD zip** (full R, R_min, R_max distributions) that feeds
`brewer2026.pack_generator` is separate from this table and remains requested
from the authors (see `../BLOCKED_INTAKE.md`). This Table 1 unblocks 1.5; the
raw PSDs are only needed for pack_generator inputs.
