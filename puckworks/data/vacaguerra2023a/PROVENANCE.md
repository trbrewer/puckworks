# vacaguerra2023a — data provenance

**Source:** Vaca Guerra, M., Harshe, Y.M., Fries, L., Rothberg, S., Palzer, S., Heinrich, S.
"Influence of particle size distribution on espresso extraction via packed bed compression."
*Journal of Food Engineering* **340** (2023) 111301. DOI 10.1016/j.jfoodeng.2022.111301.
**Version digitized: the revised preprint dated 2022-09-27** (Tim drop, 2026-07-25) — equation
and table/figure numbering may differ trivially from the version of record. Card: `docs/cards/vacaguerra2023a.md`.

**Material:** a single dark-roast 100 % arabica; the fitted coefficients are material-scoped.

## Files (as digitized)

| file | source | method | units (as published) |
|---|---|---|---|
| `Table_C1_Extraction_conditions_from_permeability_experiments.csv` | Table C.1 | table transcription | Dosage g; ε₀ –; ΔP bar; Q mL s⁻¹; δL mm |
| `Table_1_Particle_size_distributions_used_in_extraction_experiments.csv` | Table 1 | table transcription | α µm; β –; d[3,2] µm; fines %; ψ – |
| `Table_2_Empirical_coefficients_compression_factor_phi_Equation_9.csv` | Table 2 | table transcription | k₁ Pa; k₂ Pa m⁻¹; k₃ Pa; k₄ Pa m⁻¹; k₅ Pa m⁻² |
| `Table_3_Empirical_coefficients_compression_factor_omega_Equation_10.csv` | Table 3 | table transcription | x₁ –; x₂ m⁻¹; x₃ –; x₄ m⁻¹ |
| `Figure_12_Calculated_versus_experimental_dry_bed_porosity_validation_experiments.csv` | Fig. 12 | figure digitization | measured / calculated dry-bed porosity, both – |

## Load-bearing caveats (carried from the card, and now resolved / quantified)

- **Eq-9/Eq-10 β-sign error (RESOLVED here).** The printed Table-2/Table-3 coefficients k₃, x₃ are
  **positive**, but the `+k₃β`/`+x₃β` forms give unphysical repose porosity ω ≈ 0.48–0.62 (above the
  loosest *measured* bed, ε₀ = 0.36) and φ 2–4× too low. The `−k₃β`/`−x₃β` forms give ω ≈ 0.31–0.37
  (matching Table C.1's ε₀ range and the card's Fig-9 per-PSD fits within ≤0.04) and φ of the right
  magnitude. **Adopt the negated-β convention** (`puckworks.analysis.vacaguerra2023a`).
- **Viscosity convention (G10).** The authors compute K with µ = 3.5 mPa·s (their own unpublished
  measurement at 65 °C). Since K ∝ µ, cross-source K comparisons (Wadsworth band, Corrochano) must
  renormalize µ first; the analysis module reports both the as-published and a G10-renormalized variant.
- **Permeability Eq-11 is post-fit** (λ = 7.5, exponents 4.3/0.43 fitted to these same 9 points) — a
  reconstruction, never blind-tested. K here is the DRY-bed porosity closure; not consolidation-corrected.
- **Numeric flag not propagated:** the card notes the paper misquotes the Corrochano permeability range
  (3×10⁻¹⁴–8×10⁻¹³); the registry keeps the primary `romancorrochano2015` value.

## License / access

JFE (Elsevier). The preprint is the digitized copy; values are transcribed/digitized, not redistributed
as the publisher PDF. No raw data or code was published with the paper.
