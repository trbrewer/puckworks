# Replicate-level measurement uncertainty intake and analysis plan

**Status:** partial TB-2 completion. The repository can now ingest a uniform uncertainty
schema, and the published Angeloni total-solids/lipid RSD tables have been transcribed.
Analyte-specific Angeloni replicate/RSD values and the Schmieder supplementary workbooks
are still required before the manuscript-facing weighted reruns can be completed.

## 1. Source acquisition

### Angeloni et al. 2023

Source: Simone Angeloni et al., “Computer Percolation Models for Espresso Coffee: State
of the Art, Results and Future Perspectives,” *Applied Sciences* 13, 2688 (2023),
DOI `10.3390/app13042688`.

Recovered now:

- Table 1 sample-to-condition map for A1–A33 and R1–R33.
- Table 2 total-solids means and RSDs.
- Table 3 total-lipid means and RSDs.
- A 132-row canonical uncertainty summary validated by `tools/validate_replicate_uncertainty.py`.
- The methods statement that analyses were carried out almost in duplicate (`n=2`).

Not recovered from the article tables:

- per-replicate values;
- sample/analyte-specific RSD for caffeine, trigonelline, 3-CQA, 5-CQA, or 3,5-diCQA.
  Tables 4–5 give central values and only global RSD ranges (Arabica 0.3–19.7%;
  Robusta 0.1–19.2%).

Use `puckworks/data/angeloni2023/replicate_uncertainty_template.csv` for an author or
supplementary-data drop. Do not assign the published global maximum to every analyte or
condition.

### Schmieder et al. 2023

Source: Babette K. L. Schmieder et al., “Influence of Flow Rate, Particle Size, and
Temperature on Espresso Extraction Kinetics,” *Foods* 12, 2871 (2023), DOI
`10.3390/foods12152871`; data DOI `10.17632/y2tz67f6ry.1`.

Acquire and retain the original files, then populate
`puckworks/data/schmieder2023/replicate_measurements_template.csv`:

- Supplementary Table S1: experiment raw data / fraction-level replicate
  concentrations;
- Supplementary Table S2: individual fitted kinetic parameters;
- Supplementary Table S3: single-experiment cup masses;
- Mendeley Data item `Experimental_data`, where available.

Record source filename, source table, file SHA-256, license, download date, and any cell
normalization. Do not average fractions, analytes, brew ratios, or units before the
observable contract is explicit.

## 2. Canonical uncertainty summary

Normalize both campaigns into
`puckworks/data/measurement_uncertainty_summary_template.csv`. The recovered Angeloni total-solids/lipid rows are already available in canonical form as
`puckworks/data/angeloni2023/angeloni2023_uncertainty_summary.csv`. Each row represents one
condition/analyte/observable and should contain either raw-replicate-derived `sd` or a
published `rsd_percent`. Preserve the raw data separately.

When only a mean and RSD are available:

```text
sd = abs(mean) * rsd_percent / 100
se = sd / sqrt(n)                 # only when n and independence are defensible
```

RSD is a coefficient of variation, not a standard error. A reported `0.0%` after rounding
is not evidence of zero variance and must not create infinite weight.

## 3. Predeclared sensitivity analyses

Run all headline results under the same four lenses:

1. existing unweighted objective;
2. variance-weighted least squares with `w_i = 1 / max(sd_i^2, sigma_floor_i^2)`;
3. robust standardized residual loss (Huber or Student-t), using the same scale inputs;
4. cluster/bootstrap resampling at the extraction-run level so derived fractions/cup
   quantities from one run are not treated as independent.

Set `sigma_floor` before seeing the scientific conclusion. A defensible starting rule is
the larger of the assay resolution and a small predeclared fraction of the observable’s
median non-zero SD. Report floor sensitivity. Do not weight by `1/mean^2` when RSD is
missing.

For source-derived cup totals created by integrating fitted fraction kinetics, propagate
the first-stage uncertainty by resampling the complete extraction run (fractions and fit),
not by assuming independently noisy integrated points. Where the source workbook does not
permit this, label the weighted result as assay-only and keep integration uncertainty as
an unresolved limitation.

## 4. Paper A reruns after analyte uncertainty arrives

For each solute and objective:

- recompute the inventory–rate profile and its 10%-near-minimum set;
- compare weighted and unweighted valley width, boundary censoring, and local curvature;
- rerun LOCO and O→C/F transfer with held-out standardized residuals;
- compare the mechanistic model and O-trained constant using paired run/condition
  resampling;
- rerun the joint shared-parameter analysis and report whether the cost-of-sharing exceeds
  measurement variation;
- state whether any conclusion changes sign or evidence tier.

Primary conclusion gate: the model–baseline difference must be reported alongside its
measurement-error distribution; a small MAPE difference alone is not interpreted as
meaningful skill.

## 5. Paper B reruns after Schmieder raw data arrives

- reconstruct source-derived TDS-EY run by run from the same fraction-to-cup procedure;
- refit the RSM using run-level responses and achieved predictors;
- retain fixed-design residual, wild, and case/bootstrap summaries, but add a bootstrap
  that repeats the fraction-to-cup integration;
- compare the middle-vs-fine contrast to the propagated run-level uncertainty;
- ensure the evidence matrix labels the endpoint as source-derived rather than directly
  measured.

## 6. Acceptance checklist

- [ ] raw source files stored with checksums and license/provenance;
- [ ] templates populated without unit or observable merges;
- [ ] raw-replicate, mean, SD, RSD, and `n` semantics validated;
- [ ] weighted, robust, and cluster/bootstrap sensitivity results archived;
- [ ] model–baseline differences compared to measurement variation;
- [ ] profile/skill/LOCO/joint conclusions updated proportionately;
- [ ] manuscript distinguishes assay uncertainty from first-stage integration uncertainty.
