# schmieder2023 — data provenance

Source card: `docs/cards/schmieder2023.md` (ROADMAP item 0.1, the kinetics half).

**Origin:** Schmieder, Pannusch, Vannieuwenhuyse, Briesen, Minceva, *"Influence of
Flow Rate, Particle Size, and Temperature on Espresso Extraction Kinetics,"*
**Foods 12, 2871 (2023)**, DOI `10.3390/foods12152871`, **open access CC-BY**.
Files supplied by Tim 2026-07-10 (MDPI is Cloudflare-blocked from CC); the
machine-readable supplementary + full-text JATS XML were parsed here — **no
numeric table was hand-keyed**.

System (per card): Colombia Suprema Huila washed Arabica, one roast, 20 g dose,
DE1 Pro + IMS basket, Acqua Panna water, Mahlkönig E65S, flow-controlled
(0.96/1.9/2.8 mL/s), GL 1.4–2.0, T 80–98 °C. Coefficients are box-specific.

## Curated CSVs (parsed from `source/`, exact values)
| file | source | rows | content |
|---|---|---|---|
| `kinetics_fit_params_avg.csv` | paper **Table A1** (JATS XML) | 60 | per-experiment **averaged** c₀, λ (+SE, red-χ², adj-R²) for trigonelline / caffeine / 5-CQA / TDS. **Authoritative** — Exp 7 caffeine c₀=9.70981, λ=23.09434 matches card (9.71 / 23.09). TDS c₀ in g/g, others mg/g. |
| `kinetics_fit_params_reps.csv` | **Table S2** (xlsx) | 192 | same fit params **per replicate** (15 exp × 3 reps; Exp 7 center point ×6) × 4 components. |
| `cup_masses.csv` | **Table S3** (xlsx) = paper Table 2 | 612 | per-replicate component **mass in cup** + **concentration in cup** at BR 1/1, 1/2, 1/3, with DoE run conditions (flow, GL, temp, max pressure). mg for solutes, g for TDS. |
| `raw_fractions.csv` | **Table S1** (xlsx) | 288 | raw per-fraction data: fraction & accumulated mass (g), outlet concentration (mg/g) of trigonelline / caffeine / 5-CQA per fraction (S1 has no TDS column — TDS is gravimetric). |
| `rsm_coefficients.csv` | paper **Table 3** (JATS XML) | 12 | full-quadratic RSM coefficients β₀–β₉ + adj-R² per component × BR (Eq. 4). Machine/grinder-specific regression — **data-only / qualitative** (adj-R² 0.41–0.75). |

`source/` keeps the three supplementary xlsx + the full-text XML (small, CC-BY)
so the parse is reproducible. Extraction scripts were one-shot (OOXML parsed via
`zipfile`+`xml`; JATS via ElementTree, handling merged headers, rowspan, and
`a × 10⁻ᵇ` notation).

## Not tracked in git (on disk, gitignored — see repo `.gitignore`)
Bulky MDPI artifacts: `foods-12-02871-s001.zip` (17 MB), `.epub` (9 MB),
`foods-12-02871-v5.pdf` (6 MB), `S4.1_OriginPro_*.opju` (37 MB), the extracted
`foods-12-02871-s001/` dirs, `.DS_Store`.

## Caveats (→ MANIFEST)
- RSM adj-R² low (0.41 caffeine … 0.75 TDS); authors restrict to **qualitative**
  trends. Cup-mass reproducibility mean RSD 2.5 % (max 8.5 %).
- Single bean / machine / grinder — non-transferable. x_grind is a dial number,
  not a PSD. Earliest brew (< fraction-1 mass) known to misfit the exponential.
