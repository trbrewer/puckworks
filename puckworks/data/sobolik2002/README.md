# Sobolík et al. (2002) — digitized figures and tables

Source: Sobolík V., Žitný R., Tovcigrecko V., Delgado M., Allaf K. (2002),
"Viscosity and electrical conductivity of concentrated solutions of soluble coffee",
*Journal of Food Engineering* **51**, 93–98. PII S0260-8774(01)00042-5.

Coffee studied: freeze-dried 65% arabica (Colombia) / 35% robusta (Brazil),
"Café filtré" (Carrefour, France). ω = kg dry coffee / kg solution.

---

## Evidence strength labels

Every data file carries an `evidence_strength` column or is exact by construction.

| Label | Meaning |
|---|---|
| `EXACT_TRANSCRIPTION` | Read from the PDF text layer (embedded fonts, not OCR) and cross-checked against the rendered page. No extraction error. |
| `COMPUTED_FROM_PUBLISHED_EQUATION` | Evaluated from the paper's own equation and published parameters. Reproduces the fitted lines exactly; carries the model's fit error, not a digitization error. |
| `DIGITIZED_HIGH` | Marker centroid extracted from a 300 DPI raster; agrees with the paper's own correlation within ~5–10%. |
| `DIGITIZED_MEDIUM` | Extracted but degraded — marker clipped by the plot frame, or merged with a neighbour. |
| `DIGITIZED_LOW` | Detected but series/temperature assignment not possible (overlapping markers). Value reported, label withheld. |

---

## Files

### Exact transcriptions

| File | Content |
|---|---|
| `table1_kappa_quadratic_coefficients.csv` | Table 1 — quadratic coefficients p₀ᵢ, p₁ᵢ, p₂ᵢ of Eq. (11) for 11 mass fractions, 25–72 °C. **Includes a validation flag — see Anomaly 1.** |
| `table2_model_parameters.csv` | Table 2 — parameters and confidence intervals for model (9) and the modified Casteel–Amis model (10), plus σ and R. |

### Computed from published equations (exact reproduction of the fitted lines)

| File | Equation | Content |
|---|---|---|
| `eq11_kappa_computed_from_table1.csv` | Eq. (11) | κ(ω,T) = p₀ᵢ + p₁ᵢT + p₂ᵢT², 11 ω values × 25–72 °C. These are the full lines in Fig. 5 and the marker values in Fig. 6. |
| `eq9_eq10_conductivity_models_computed.csv` | Eqs. (9), (10) | Seven-parameter model and modified Casteel–Amis model on an ω × T grid. Eq. (9) gives the full lines in Fig. 6. |
| `eq4_viscosity_concentrated_computed.csv` | Eq. (4) | μ(ω,T) for ω = 0.5–0.8, 25–95 °C (the fitted lines in Fig. 2). |
| `eq5_viscosity_dilute_computed.csv` | Eq. (5) | μ(ω,T) for ω = 0–0.5, 0–80 °C (the fitted lines in Fig. 3). |
| `eq1_eq2_eq3_physical_properties_computed.csv` | Eqs. (1), (2), (3) | Refractive index, density and thermal conductivity, reviewed from Weisser (1972). Eq-3 verified 2026-07-23 against a clean copy: `λ = 10⁻³(565.1 + 1.8T − 0.0058T²)(1 − 0.54ω)` W m⁻¹ K⁻¹ — an **adopted Riedel sucrose-analog** (base = pure-water k(T); the (1 − 0.54ω) factor is the sucrose-solution relation the authors adopted after measuring coffee ≈ sucrose, not a coffee-specific fit). The `thermal_conductivity_W_m-1_degC-1` column reproduces this to 5×10⁻⁶ W m⁻¹ K⁻¹. Reproduced by `gate_g10_sobolik_density`. |

### Digitized from figures

| File | Figure | Points | Validation |
|---|---|---|---|
| `fig1_flow_curves_digitized.csv` | Fig. 1 — τ vs γ̇, ω = 0.7, 40 °C, log-log | 17 | No published equation; see Anomaly 2 |
| `fig2_viscosity_concentrated_digitized.csv` | Fig. 2 — μ vs T, ω = 0.5–0.8, semi-log | 48 | vs Eq. (4): geometric-mean ratio **0.968**, log₁₀ RMS **0.064 decades (~16%)** |
| `fig3_viscosity_dilute_weisser_digitized.csv` | Fig. 3 — μ vs T, ω = 0–0.5 (Weisser 1972 data), semi-log | 24 | vs Eq. (5): geometric-mean ratio **0.977**, log₁₀ RMS **0.031 decades (~7%)** |
| `fig6_conductivity_vs_massfraction_digitized.csv` | Fig. 6 — κ vs ω at 30/40/50/60/70 °C, linear | 34 (25 fully resolved) | vs Eq. (11): mean absolute deviation **1.67%**, max **5.3%** |

`fig4_apparatus_dimensions.csv` holds the labelled dimensions of the conductivity cell (Fig. 4), which is a schematic, not plotted data.

**Fig. 5 was deliberately not digitized as scatter.** It carries ~25 plotted points per series across 11 overlapping ω series on a log axis; automated series assignment there would manufacture false precision. Its content is fully and exactly available as `eq11_kappa_computed_from_table1.csv`, which is what the figure's full lines represent.

---

## Method

1. Pages rasterized from the source PDF at 300 DPI (`pdftoppm`).
2. Plot frames located programmatically as long continuous dark runs; axis ranges confirmed by tick-spacing arithmetic (each detected tick interval extrapolates to the frame edges within 1–2 px).
3. Markers extracted by binary closing (to fill halftone grey fills) → hole filling (so open ring markers survive) → morphological opening with a disk (to sever the ~3 px connecting curves) → connected-component centroids.
4. Series assigned by monotonic ordering, which is physically guaranteed within each figure (μ increases with ω; κ increases with T). Assignments were then checked against the published legends and agree.
5. Fig. 1 filled/open markers separated objectively by mean interior grey level (filled ≈ 165, open ≈ 255).

Calibration was validated **numerically, not by eye**: digitized values are compared against the paper's own correlations in each file's `ratio_` or `deviation_` column. Digitized temperatures recover the nominal values (25, 30, 40 … 95 °C) to within 0.15 °C, and Fig. 6 recovers Table 1 to within 1.67% mean — independent confirmation that both axis scales are correct.

---

## Anomalies flagged (transcribed as printed, NOT corrected)

**Anomaly 1 — Table 1, rows 1 and 11.** As printed, row 1 (ω = 0) and row 11 (ω = 0.8) yield κ ≈ 0 S m⁻¹ from Eq. (11):

- ω = 0, T = 50 °C → Eq. (11) gives 5.1×10⁻⁵ S m⁻¹, but this is pure tap water, and Table 2 gives κ_w = 0.0503 S m⁻¹, with the text citing ~0.043 S m⁻¹ at 50 °C. Fig. 6 shows ≈0.049.
- ω = 0.8, T = 70 °C → Eq. (11) gives 8.3×10⁻⁵ S m⁻¹, but Fig. 6 shows ≈0.064 and Eq. (9) gives 0.14.

Both rows are self-consistent with a **three-decade exponent shift** in the printed table (e.g. row 1 as 1.48E-2 / 7.20E-4 / 1.70E-7 reproduces 0.051 S m⁻¹ at 50 °C). This is recorded as `SUSPECT_SOURCE_TYPO` in the `validation_flag` column. The values in the CSV are the printed ones. The other nine rows reproduce Fig. 6 to within a few percent and are unaffected.

**Anomaly 2 — Fig. 1 vs Fig. 2 at ω = 0.7, 40 °C.** The two flow curves in Fig. 1 give apparent viscosities of ≈5.9→5.1 Pa·s (filled markers, shear-thinning) and ≈3.5 Pa·s (open markers, Newtonian). The paper states its reported data correspond to the second phase, after passing 95 °C — i.e. the open, Newtonian branch. But Eq. (4) predicts 5.32 Pa·s at ω = 0.7, 40 °C, and the digitized Fig. 2 point is 5.24 Pa·s. Those match the *filled* branch, not the open one. Either the symbol assignment or the phase attributed to the correlation is worth checking against the original before Fig. 1 is used quantitatively. Both series are supplied with their caption labels as printed.

---

## Known limitations

- Fig. 3 markers at T = 0 and 80 °C sit on the plot frame and are partially clipped (`DIGITIZED_MEDIUM`); the T = 80 column resolved only 1 of 6 series.
- Fig. 6 columns at ω = 0, 0.02, 0.05, 0.4, 0.7, 0.8 have overlapping markers; 25 of 55 points resolved to a specific temperature, the rest reported as `DIGITIZED_LOW` without a temperature label. Use `eq11_kappa_computed_from_table1.csv` for these instead.
- The small open rectangles in Fig. 6 (temperatures differing by 1–2 °C from the rated values) were not separated from the main markers.
- The Weisser (1972) diamond overlay in Fig. 2 (ω = 0.5) was not separated from the main ω = 0.5 series.
- Digitized values carry the paper's own measurement error on top of extraction error: the authors state viscosity is accurate to about 15%.
