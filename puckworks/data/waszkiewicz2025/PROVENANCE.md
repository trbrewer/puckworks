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

## Raw per-brew traces (ingested 2026-07-25) -> `traces_per_brew.csv`

`measurements_time_dependent/*.txt` (57 raw per-brew JSON-lines traces) are now ingested as
**per-shot** time series, because the published `traces_time_dependent.csv` is a per-pressure MEAN
whose `*_std` columns are standard **ERRORS** (`sem`) -- so shot-to-shot variability is not
recoverable from it, and any analysis on it has the time point, not the shot, as its unit.

**Reduction.** Re-implemented from the method documented in the deposit's
`format_measurements_time_dependent.py`; **that script is GPLv3 and is NOT ingested or copied** (the
standing convention for this source: CC-BY-4.0 data, code not ingested). Steps: reference pressure =
median `p2`, rounded to the nearest 0.5 bar, with the source's two manual corrections (`1-2.txt` ->
1.0 bar; 1.5 -> 2.0); t=0 = the sample after the last out-of-tolerance `p2` within the first 500
samples; truncate at 100 s; `p2` kPa -> bar; flow = Savitzky-Golay(gradient(mass, t), window 31,
polyorder 1); basket pressure = p - (a q^2 + b q + c) from `brewer_quadratic_params.csv`; interpolate
each shot onto a common 0-100 s, 1000-point grid.

**Verification.** Re-aggregating these 57 shots by (pressure, time) with mean/`sem` reproduces the
published `traces_time_dependent.csv` on **all 11 000 rows to max |delta| = 5e-7** -- i.e. exactly,
within that file's own 1e-6 write precision. Guarded by
`tests/test_waszkiewicz_per_brew.py::test_reaggregation_reproduces_the_published_means`.

**Shots per reference pressure:** 1.0:5, 2.0:4, 3.5:3, 4.0:10, 5.0:5, 6.0:6, 7.0:4, 8.0:4,
**9.0:5**, 11.0:4, 13.0:7 (57 total).

**Caveats.** The source's reduction is baked in (alignment, ~3 s Savitzky-Golay smoothing, brewer
subtraction), so these are processed, not raw instrument output. Filename prefixes are NOT the
reference pressure (`10-2` is 11 bar, `12-8-2` is 13 bar). The source's `excluded/` brews are NOT
included -- their exclusion is the authors' judgement and is not re-litigated here. Time is stored
as `time_index` on the exact grid rather than a float, so joins cannot drift.

## Not ingested (available in the source zip if needed later)
- `measurements_time_dependent/excluded/*` (brews the authors excluded).
- `formatted_measurements/debug_time_dependent.csv` (3.6 MB intermediate).
- Figures (PDF), MATLAB/Python fitting code (GPLv3), `brew_restarting.txt`
  (Fig 10 delamination experiment — qualitative).

## Caveats carried to MANIFEST
- Time-dependent Q(t) validation has **soft circularity**: m_d(t) derives from
  TDS(t)×Q(t) on the same rig (card §"Calibration"). Validation strength =
  *independent within-rig* for the equilibrium curve; *post-fit/semi-quantitative*
  for the 9-bar Q(t) reproduction.
- Highest pressures (11–13 bar) dip below the monotone model (card).
