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
