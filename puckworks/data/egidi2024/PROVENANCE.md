# egidi2024 — data provenance

Source card: `docs/cards/egidi2024.md` (ROADMAP item 0.3). Data-only (equations
not adopted); the value is the RC-1 EY/TDS bracket.

**Origin:** Egidi, Giacomini, Larsson, Perticarini, *"An improved numerical scheme
for coffee Extraction Yield evaluation,"* **Chaos, Solitons and Fractals 188,
115625 (2024)**, DOI `10.1016/j.chaos.2024.115625`. Table 2 digitized by Tim.

## File
`table2_egidi2024_tds_ey.csv` — 12 conditions (T × p × granulometry): TDS mean,
TDS σ, EY. Dose 20 g, beverage 40 g, VST basket, τ 18–42 s.

## Validation strength / caveats
- **Independent EY/TDS *range bracket* only — NOT a pressure/T response test.**
  In the egidi model, p and T never enter explicitly; they are absorbed into the
  measured flow q and shot time τ, so the 12-condition structure is not actually
  predicted — only the grind-averaged EY. Use as a bracket (EY **19–23 %**,
  TDS ~10 %), not as a response surface. Authors call the validation "preliminary".
- Cameron's EY at a comparable config reads **~15 %** — *below* the egidi bracket
  (Cameron caps EY below its own model curve, per its card). Surfaced in the P1
  harness as a documented discrepancy, not asserted into the bracket.
- Eq. 4 has undefined ρ and φ_s (§5.8 correspondence) — irrelevant here since only
  the tabulated EY/TDS are used, not the equations.

## Verified shared-publication lineage and duration use (2026-10-24)

Egidi Table 2 (article/PDF p.6) and Perticarini's *Predictive Models in Espresso
Coffee Percolation*, Table 4.3 (printed p.91/PDF p.103), present the same Modœtia
observations. All 12 condition labels and all six numeric columns agree with this
canonical CSV; trailing decimal zeroes are harmless display differences. No new
12-row dataset or independent campaign/replicates are created.

The source PDFs actually read have file SHA-256 values
`1aba69278444d107ce5172eb29ba7b37883491fe0b32dfd9bc8898632e203a33` (Egidi) and
`248d480cc2ab3353799fcaa886bb1be3f6cfbe7a9f15e1cdf9d4950827424c7f` (thesis).
[Full source notes](../../../docs/analysis/sci_md_perticarini_pressure_grind_001/SOURCE_NOTES.md)
retain URLs, methods, cell authentication and unresolved fields.

New consumer: `puckworks.analysis.perticarini2024_pressure_grind`, a retrospective,
source-internal, nonscoring analysis of reported condition duration. The duration
statistic/spread/rounding/clock are unspecified; triplicate chemical extractions
and TDS sigma do not establish duration replication or uncertainty. Nominal machine
pressure labels are not measured puck pressure drop; actual condition beverage
masses are unknown. No measured flow or permeability is inferred. The earlier
EY/TDS bracket and p/T-prediction qualification above remain unchanged; no physical
validation upgrade follows. PHYSICAL_VALIDATION=NOT_ESTABLISHED.
