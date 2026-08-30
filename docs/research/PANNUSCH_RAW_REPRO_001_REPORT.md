# PANNUSCH-RAW-REPRO-001 scientific report

## Disposition

`PANNUSCH_RAW_REPRO_001_COMPLETE_TRANSFER_SUBSET_ELIGIBLE` (G1). This task changes
accepted source data and mappings only: no governing physics, fitted parameters, EWP,
or target scores changed.

## Authority, method, and rights

Thirteen hash-bound source inputs beneath the external recovered store reconstruct the
authority deterministically through `tools/pannusch2024_reconstruct.py`. They include
the source MAT workspaces, preprocessing MATLAB, experiment-design and analytical
workbooks, PSD provenance, and prediction mass-fit metadata. The products retain
CC-BY-NC-3.0 status and attribution; raw workbooks, MAT files, telemetry, apps, binaries,
and archives remain external. The accepted independent review freeze is the scientific
starting authority.

## Reconstructed campaigns and corrections

The fit campaign contains 15 experiments, 45 physical shots, and six accepted fractions
per experiment. Three source-declared spilled HPLC samples—experiment/run/fraction
3/1/2, 11/3/2, and 14/3/2—remain visible as invalid records and no longer enter means.
Nine analyte cells across the three accepted rows rise from two-thirds of the valid-only
mean to that mean; TDS is unchanged. `experimental_kinetics_correction_ledger.json`
records the exact before/after values and hashes.

All fit experiments now use explicit source grind assignments: experiments 1,2,5,6,12
at 1.4; 9,10,11,14,15 at 1.7; and 3,4,7,8,13 at 2.0. The benchmark fails closed instead
of silently falling back to center grind. Table 2 fitted psi, d_s2, and solute parameters
are unchanged.

## Experiment 46 and March prediction campaign

Experiment 46 reconstructs 12 fractions from 819.70 g liquid and 20 g coffee: caffeine
251.598442 mg, trigonelline 168.643265 mg, 5-CQA 144.520754 mg, workbook CQA sum
280.257266 mg, and TDS 5241.913218 mg (26.2096% of dose). Tails after 212.68 g are
0.212%, 0.106%, 0.061%, and 0.068%, respectively. These are `DIRECT_RECOVERED_MASS`,
an `N1_OPERATIONAL_REFERENCE_ESTIMATE`, and an
`EMPIRICALLY_RESOLVED_MEASURED_TAIL`. They do not establish total roasted content,
analytical exhaustion, production M0, replacement of fitted c_s0, same lot/roast,
or repeatability.

March 2022 contains eight conditions, 24 physical shots, six fractions per shot, and
five chemistry observables. Temperature and flow trajectories are programmed. It is
`SOURCE_DESIGNATED_PREDICTION`, `CAMPAIGN_SEPARATED`, `TARGET_EXPOSED`, and
`SOURCE_INTERNAL`, not target-blind or independent validation.

## Metric attribution (MAPE %)

| data / grind | caffeine | trigonelline | 5-CQA | TDS | pooled |
|---|---:|---:|---:|---:|---:|
| legacy / center | 6.4150 | 10.1802 | 7.2232 | 6.7249 | 7.6358 |
| valid-only / center | 4.9140 | 8.7190 | 5.7716 | 6.7249 | 6.5324 |
| legacy / source | 6.6034 | 9.8569 | 6.9128 | 6.5179 | 7.4728 |
| valid-only / source | 5.1082 | 8.3977 | 5.4655 | 6.5179 | 6.3723 |

The spill correction reduces pooled MAPE by about 1.10 percentage points at center
grind. Source grind changes it independently by about -0.16 points on either data
version. No optimizer or parameter fit ran. Source-published metrics remain separately
labelled.

## Eligibility, blockers, and claim ceiling

Normalized fraction-shape transfer is conditionally eligible for constant-temperature
C01, C02, C05–C08. Absolute mass remains blocked by inventory mapping; C03–C04 are
blocked by EWP temperature physics; prescribed flow cannot validate hydraulics. Source
baseline fitting privileges prohibit automatic treatment as a fair no-retuning baseline.
The later ceiling is `CAMPAIGN_SEPARATED_TARGET_EXPOSED_FIXED_PARAMETER_COMPARISON`.

`c_s0` remains a `FITTED_MODEL_PARAMETER`; no common volume/phase/porosity/density/
moisture basis maps it to experiment-46 recovered mass. The recovered corpus improves
source reconstruction but does not establish external physical validation.

## Home laboratory and confirmation

Disposition remains `HOME_LAB_REDESIGN`. Source-laboratory fraction feasibility and
variance do not qualify Tim's apparatus or close initial/cup/retained/residual mass.
Tier 1 still needs 3–5 reference replicates, paired caffeine/trigonelline fractions,
spent puck, retained liquid, moisture basis, blanks, recovery spikes, LOD/LOQ, and
durable joins. No purchase or commissioning occurred.

