# maille2024 — data provenance

**Source:** Maille, M. J. "Measuring Coffee Extraction Kinetics at Early Time Scales." PhD thesis,
Dept. of Chemical and Biological Engineering, University of Sheffield, May 2024 (adv. J. D. Litster;
sponsor Keurig Dr Pepper). Card: `docs/cards/maille2024.md`.
**Tables digitized (Tim drop 2026-07-25).** The card was written from the **redacted** release; this
drop includes tables that were blanked there (Table 5.6 SSA-all-materials, Table 5.9 porosity), so
the source here is the **unredacted** thesis for those. The time-resolved extraction **figures**
(Figs 4.6–4.10) are a separate digitization that will follow.

**Material:** single 70 kg lot, washed, Antioquia Colombia; two roast levels (light/dark); coarse
sieved fractions + full-PSD materials. Batch **well-mixed reactor** (WMBR) — no bed, no pressure,
no flow, no EY/TDS. Coefficients are per-material curve fits.

## Files (all table transcriptions from the thesis)

| file | source | content |
|---|---|---|
| `Table 5.1 …` | Table 5.1 | material legend: Sample ID (ΩA…) → roast degree, sieve class (µm) |
| `Table 6.3 …` | Table 6.3 | the φ closure: θ_v,fines, θ_v,coarse, φ (17 materials) |
| `Table 5.4 …` | Table 5.4 | hybrid PSD: D[4,3], D[3,2], vol fraction < 186 µm (21) |
| `Table 5.2 …` | Table 5.2 | PSD by **liquid vs air** dispersion — Dx50/D[4,3]/D[3,2]/vol<186µm (24) |
| `Table 6.4 …` | Table 6.4 | caffeine + 3-CQA kinetics: λ_fast, λ_slow (±95% CI), R², MPE (17) |
| `Table 6.5 …` | Table 6.5 | citric/malic/quinic kinetics, same fields (16) |
| `Table 5.11 …` | Table 5.11 | equilibrium conc. [mg L⁻¹] mean±SD at 180/300/600 s, 5 compounds (21) |
| `Table 5.10 …` | Table 5.10 | normalized extraction conc. vs time (10–180 s), ΩA–ΩC × 5 compounds |
| `Table 5.6 …` | Table 5.6 | SSA (Kr adsorption) all materials [cm² g⁻¹] (unredacted) |
| `Table 5.7 …` | Table 5.7 | measured vs calculated SSA (Eq 5.4) (5) |
| `Table 5.9 …` | Table 5.9 | particle porosity ε_p / ε_open / ε_closed + densities (unredacted) (5) |
| `Table 6.1 …` | Table 6.1 | hydration-time (Eq 6.3) inputs |
| `Table 6.2 …` | Table 6.2 | Bi_m / Fo_m estimate inputs (186 µm threshold) |
| `Table 3.2 …` | Table 3.2 | 35 roast batches (mass, time, end T, % loss, Agtron) |

## Errata / caveats (carried from the card — transcribed as printed, flagged in analysis)

- **E1 (shell depth, RESOLVED here).** Eq 6.9 as printed subtracts one cell layer (2·d_c off the
  diameter); the text intent + Table 6.3 require **two** layers (4·d_c). Recomputing θ_v,coarse
  (D[4,3] single-diameter approximation, d_c = 45 µm) reproduces Table 6.3 to mean |err| **0.018 at
  two layers vs 0.207 at one** — the registry adopts the **two-layer** convention
  (`analysis.maille2024`). This roughly doubles φ vs the printed one-layer form.
- **E5 (impossible CIs).** Table 6.4 ΩT / 3-CQA λ_fast upper CI (11.9) is below the estimate (12.2);
  Table 6.5 ΩL / quinic λ_slow CI (44, lower 65, upper 54) is internally impossible. Transcribed as
  printed; treat those CIs as **unusable**.
- **Instrument-specific φ.** Eqs 6.8–6.9 assume the Malvern 100-bin scale, bin 75 ≈ 186 µm; the
  **per-bin PSD arrays are not published**, so φ cannot be recomputed end-to-end from these tables —
  the E1 gate uses the D[4,3] single-diameter approximation the thesis itself used.
- **Batch, bed-free, coarse-grind, dilute (K≈1), single origin, one temperature (91.5 °C).** No EY,
  no TDS, no bed/flow/pressure. Espresso-grind use is extrapolation (materials are 2–4× coarser).

## License / access

University of Sheffield / White Rose eTheses. Values transcribed from the thesis tables; the PDF is
not redistributed. No raw data or code was published with the thesis.
