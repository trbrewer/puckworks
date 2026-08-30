# pannusch2024 — source-faithful reconstructed authority

Source card: `docs/cards/pannusch2024.md` (ROADMAP item 0.1, the Mendeley half).

**Origin:** Mendeley Data *"Data Repository for … Model-Based Kinetic Espresso
Brewing Control Chart for Representative Taste Components,"* DOI
`10.17632/y2tz67f6ry.1`, **CC-BY-NC-3.0**. Supplied by Tim 2026-07-10 (the
Mendeley public API exposes only the root file, not the `Experimental_data/`
subfolder). The full repository is on disk under this directory but is
**gitignored** (large + mixed binaries: a Windows `.exe` installer, MATLAB
`.mlapp`/`.mat`, ~350 per-experiment `.xls`/`.txt`/`.mat` traces).

## Landed (1.8a, 2026-07-11)
- `table2_fitted_params.csv` — Table 2 per-solute fits (A1,B1,A2,B2,K_ref,γ,c_s0),
  transcribed from the card. Consumed by `pannusch2024.closures` + `.solver`.
- `table2_grind_psi_ds2.csv` — per-grind (1.4/1.7/2.0) ψ, d_s2.
- `experimental_kinetics.csv` — the Schmieder/Pannusch extraction kinetics
  (15 exp × 6 fractions: T, flow, fraction time bounds, measured
  caffeine/trigonelline/5CQA/TDS), **derived** from the reference repo
  `ExperimentalData.mat` (averaged over the 3 runs; CC-BY-NC-3.0).
- (These three are git-tracked exceptions to the ignored raw drop.)
- **FULL SOLVER LANDED** (`puckworks/models/pannusch2024/solver.py`): the 1D
  two-grain multi-solute PDE (method of lines, 5-pt biased upwind + BDF), ported
  faithfully from the released MATLAB. Reproduces the fit MAPEs — TDS 6.7 /
  caffeine 6.4 / trigonelline 10.2 / CGA 7.2 % (published 6.07/4.59/7.85/4.98;
  post-fit reconstruction). **Creates RC-4a.**

## PANNUSCH-RAW-REPRO-001 correction (2026-08-30)

The hash-bound generator reconstructs 15 fit experiments (45 shots), eight March
prediction conditions (24 shots), and experiment 46. Three source-declared spilled
HPLC samples (experiments 3, 11, 14; fraction 2) remain visible but no longer enter
accepted means. Benchmark scoring consumes explicit source grind assignments.

Committed normalized products remain **CC-BY-NC-3.0 third-party data**, not MIT; raw
MAT/workbook/telemetry files remain external. `c_s0` is fitted, not inventory.
Experiment 46 is n=1 operational recovered mass, not total content, production M0,
analytical exhaustion, or a c_s0 bridge. March targets are exposed, source-internal,
campaign-separated source-prediction observations, not independent validation.

## Status: kinetics covered via schmieder2023; Pannusch-specific data deferred
The extraction **kinetics** this repo fits are the Schmieder-2023 measurements,
already curated in `../schmieder2023/` (Tables A1/2/3 + S1/S2). So the item-0.1
gate dataset (RC-4) is in hand.

**Deferred to item 1.8a** (pannusch2024 solver intake), not done here:
- **Table 2 fitted parameters** (A1,B1,A2,B2,K_ref,γ,c_s0 per solute; ψ,d_s2 per
  grind) → `pannusch2024_table2.csv`. The repo stores these as MATLAB **`table`
  objects** inside `.mat` files, which `scipy.io.loadmat` cannot parse cleanly;
  transcribe from the paper Table 2 (values are on the card) or re-export at 1.8a.
- **Dry PSD** (`Experimental_data/Particle size distribution/
  particle_size_distribution_dry.xlsx`) — multi-sheet HELOS/RODOS export, one
  sheet per grind level; grind-stage data for 1.8a / pack_generator.
- Raw pump/mass/HPLC traces (`Experimental_data/`, `data/01…45`), control-chart
  values (`Data_BrewingControl.mat`), validation set (`Experimental_data_validation`).

Everything needed for 1.8a is present on disk; see the card for the Table-2
values and the file map above.
