# waszkiewicz2025 — data provenance

Source card: `docs/cards/waszkiewicz2025.md` (ROADMAP item 0.2).

**Origin:** Zenodo deposit *"Under pressure: Poroelastic regulation of flow in
espresso brewing"*, record 18046315, version v1.0.1,
DOI `10.5281/zenodo.18046315` (arXiv:2512.21528).
Retrieved 2026-07-10 via the Zenodo public API (file
`RadostW/espresso-v1.0.1.zip`, git tag `fbc33d3`).

**License (read carefully — split):** the Zenodo *data deposit* is **CC-BY-4.0**;
the accompanying analysis *code* (the `.py` fitting scripts) is **GPLv3** per the
repo README. Only DATA files (measurements + published fitted-parameter tables)
are ingested here — no code is copied into puckworks. Attribution: Waszkiewicz,
Myck, Białas, Puciata-Mroczyńska, Dzikowski, Szymczak, Lisicki (2025).

**Rig context (per card):** Sanremo Zoe, 56 mm bed / 58 mm basket, Fiorenzato F64
at 1.9, single Brazilian light-medium roast, 20 kg tamp, WDT. All calibration
constants are per-rig / per-coffee / per-grind and NOT transferable.

## File map (local name ← source path in the zip), byte-exact copies
| local file | source path | content |
|---|---|---|
| `traces_time_dependent.csv` | `formatted_measurements/time_dependent.csv` | Q(t) traces at **11 reference pressures** {1,2,3.5,4,5,6,7,8,9,11,13} bar, 1000 t-points each; columns incl. `pressure__bar`, `basket_pressure__bar`, `mass__g`, `mass_flow_rate__g_per_s` with per-column std. Gate data for RC-3 / item 1.2 (9-bar Q(t)) and P2 harness. |
| `tds_fractions.csv` | `formatted_measurements/tds.csv` | 5-s-interval TDS(t) mean+std (12 fractions, 2.5–57.5 s). |
| `tds_fractions_replicates.csv` | `measurements_tds_calibration/tds.csv` | raw 3-replicate TDS fractions. |
| `brewer_quadratic_points.csv` | `formatted_measurements/brewer_calibration.csv` | ΔP vs flow-rate points (Fig 2B), 4 measurement series — pump→basket pressure-drop adapter (ledger A1). |
| `mastersizer_psd.csv` | `measurements_mastersizer/mastersizer.csv` | Mastersizer volume-density PSD; **semicolon-delimited, UTF-8 BOM, transposed**: row 1 = 48 size bins (µm), rows 2–4 = 3 replicate volume-% distributions (leading empty field per data row). |
| `constants.csv` | `constant_parameters/constants.csv` | rig constants: r_basket 0.028 m, μ 3.15e-4 Pa·s (water@90°C), h₀ 0.01 m, dose 18.5 g. |
| `static_calibration.csv` | `fit_parameters/static_model_calibration.csv` | equilibrium-curve fit (Fig 6): **P_c = 12.39 ± 2.98 bar, Q_c = 1.897 ± 0.147 g/s** (matches card). |
| `tds_calibration.csv` | `fit_parameters/tds_calibration.csv` | TDS sigmoid (Eq 19): k 25.62 %, ℓ 20.86 s, m 8.87 s. |
| `solids_calibration.csv` | `fit_parameters/solids_calibration.csv` | dissolved-mass sigmoid (Eq 20): k 2.257 g, ℓ 19.83 s, m 9.34 s, **first_drop_offset 8.0 s**. |
| `brewer_quadratic_params.csv` | `fit_parameters/brewer_calibration.csv` | ΔP = aQ²+bQ+c: a 0.01718, b 0.03671, c 0.28316 (bar, g/s). |

## Not ingested (available in the source zip if needed later)
- `measurements_time_dependent/*.txt` (58 raw per-brew JSON-lines traces; the
  formatted per-pressure means are the ingested product).
- `formatted_measurements/debug_time_dependent.csv` (3.6 MB intermediate).
- Figures (PDF), MATLAB/Python fitting code (GPLv3), `brew_restarting.txt`
  (Fig 10 delamination experiment — qualitative).

## Caveats carried to MANIFEST
- Time-dependent Q(t) validation has **soft circularity**: m_d(t) derives from
  TDS(t)×Q(t) on the same rig (card §"Calibration"). Validation strength =
  *independent within-rig* for the equilibrium curve; *post-fit/semi-quantitative*
  for the 9-bar Q(t) reproduction.
- Highest pressures (11–13 bar) dip below the monotone model (card).
