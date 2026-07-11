# liang2021 — data provenance

Source card: `docs/cards/liang2021.md` (ROADMAP items 0.9 / 1.3).

**Origin:** Liang, Chan & Ristenpart, *"An equilibrium desorption model for the
strength and extraction yield of full immersion brewed coffee,"* **Sci. Rep. 11,
6904 (2021)**, DOI `10.1038/s41598-021-85787-1` (open access). The paper
publishes **no data repository** — everything is digitized from plots. Figure
CSVs supplied by Tim 2026-07-11 (digitized; carry reading noise).

## Files (digitized from figures)
| file | figure | content |
|---|---|---|
| `liang_fig3_tds_vs_rbrew.csv` | Fig 3 | equilibrium TDS(%) vs brew ratio, 1-L brews, by temperature. K*E_max refit target (Eq 11). |
| `liang_fig4_E_vs_rbrew.csv` | Fig 4 | E and E_oven (%) vs brew ratio (`measurement` = equilibrium / oven_drying). Retention-kernel (Eq 22) validation. |
| `liang_fig5_cupping.csv` | Fig 5 | cupping TDS / E vs brew ratio across roast levels (5A/5B panels). Secondary. |

## Validation strength / caveats
- **Digitization** (not a repository pull): points carry plot-reading noise.
  Refit K*E_max = 0.2186 vs the paper's in-text 0.215 ± 0.002 — consistent
  within digitization error (gate tolerance 0.01).
- Fig 3 here has ~42 points (subset of the paper's 99); still recovers the fit.
- `R_brew_digitized` is the read value; `R_brew_nominal` the intended setpoint.
- Validity R_brew >= 3 (the paper excludes R_brew = 2, "moist sludge").
