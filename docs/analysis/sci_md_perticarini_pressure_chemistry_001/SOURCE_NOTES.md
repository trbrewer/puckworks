# Targeted chemical source qualification

G1 / NO_GOVERNING_PHYSICS_CHANGE / RESEARCH_ONLY / RETROSPECTIVE /
TARGET_EXPOSED / SOURCE_INTERNAL / NONSCORING.
**PHYSICAL_VALIDATION=NOT_ESTABLISHED.**

Reuse the predecessor's [complete authentication and duration contract](../sci_md_perticarini_pressure_grind_001/SOURCE_NOTES.md),
[accepted result](../sci_md_perticarini_pressure_grind_001/RESULT.md), condition
IDs and canonical bytes. Its audit compared all 18 Cibao rows / 108 numerical
cells, all 12 Modœtia rows / 72 cells, and the same Modœtia rows in Egidi. That
complete intake audit is not repeated. This task inspects only the chemical
operator, methods/averaging passages and native table formatting needed anew.
No canonical numerical discrepancy or correction was found.

## Actual source access and lineage

On 2026-10-26 the implementation agent opened the official PDFs and reused the
predecessor's externally cached, hash-verified originals and page renders:

| Source | Original and inspected locations | SHA-256 |
|---|---|---|
| A. Perticarini, *Predictive Models in Espresso Coffee Percolation*, University of Camerino doctoral thesis, 2024 | [Official PDF](https://pubblicazioni.unicam.it/retrieve/cf1d5052-f17f-4c11-96e2-07533acdbb41/02_28_24%20-%20Perticarini%20Alessia.pdf); methods/recipe PDF97–98, chemical measurement/averaging PDF99–101; Table 4.2 PDF102 / printed90 and Table 4.3 PDF103 / printed91 | `248d480cc2ab3353799fcaa886bb1be3f6cfbe7a9f15e1cdf9d4950827424c7f` |
| N. Egidi, J. Giacomini, E. Larsson and A. Perticarini, *An improved numerical scheme for coffee Extraction Yield evaluation*, Chaos, Solitons and Fractals 188 (2024) 115625 | [Official PDF](https://pubblicazioni.unicam.it/bitstream/11581/485884/1/2024AnImpNumSchEYEval.pdf), [DOI](https://doi.org/10.1016/j.chaos.2024.115625); methods and Table 2 on PDF/article page 6 | `1aba69278444d107ce5172eb29ba7b37883491fe0b32dfd9bc8898632e203a33` |

PDF page numbers are one-based. Text-layer passages and full native table renders
were actually inspected; the table formatting claim does not rely on normalized
CSV decimal spellings. Cached locations are `/tmp/perticarini-pressure-source/`
and `/tmp/perticarini-pressure-egidi/`. These originals/renders remain outside Git.
The review record separately documents the independent reviewer's actual access.

**Thesis Table 4.3 and Egidi Table 2 contain the same Modœtia observations.**
Their sole canonical identity remains `egidi2024/table2`: no second campaign,
independent replication or extra conditions. `perticarini2024/ey_tds_cibao`
contains 18 Cibao Altura conditions. The new condition view contains those same
30 IDs; 28 enter primary pairs, with the two 12-bar conditions only in the
secondary family. Full coffee/temperature/pressure/grind keys join chemistry
to duration; row order and inferred shot membership are not join keys.

| Canonical file | SHA-256 of raw bytes |
|---|---|
| `puckworks/data/perticarini2024/ey_tds_cibao.csv` | `2c5fae8319d41c690b7e23ea00ddfc722e08c01ebcd8f012dafb1820a8fc6703` |
| `puckworks/data/egidi2024/table2_egidi2024_tds_ey.csv` | `1b5cd8891472d2d432fcb96a59e167d8fcca8b8e70a0a75187d810bf8a8e4419` |

Canonical raw bytes, including line endings and decimal spellings, stay intact.
JSON also retains Git blob identities and hashes of the reused predecessor files.
All numerical regeneration is offline from these committed tables. Original PDFs,
facsimiles and page renders are unnecessary for numerical reproduction and are
not redistributed. Existing factual numerical-table attribution/rights apply;
public access is not a blanket redistribution license. The figure is newly
computed, not source artwork.

## Chemical operator and corrected formatting

The beverage is stirred/cooled and a small prepared aliquot is measured with a
digital refractometer (VST in the thesis). There are **three chemical extraction
samples per configuration**. The thesis explicitly averages both TDS and EY over
those three extractions, after calculating EY for each sample. With the source's
brew-ratio convention, for sample j:

```
r_j = dry dose_j / beverage mass_j
E_j = C_j / r_j
C_bar = (C_1 + C_2 + C_3) / 3
E_bar = (E_1 + E_2 + E_3) / 3
```

This documents the source operator; it does not reconstruct unavailable sample
values. Nominal dry dose 20±0.1 g and beverage 40±2 g do not establish
`E_bar = 2*C_bar`. A ratio of published means does not identify individual brew
masses or an arithmetic mean brew ratio. TDS and EY are chemically related
outputs, not independent confirmation. EY remains the published central endpoint,
with uncertainty unqualified here; no SD or h_C propagation through a fixed ratio.

**All three native tables display TDS means to ONE decimal place and EY means
to TWO.** The earlier brief's claim of two-decimal thesis TDS means was incorrect.
For example, native Cibao TDS is `10.3 (0.00)` and Modœtia Fine/90.4/9 is
`11.0 (0.3)`; Modœtia Coarse/93.4/9 is `9.6 (0.50)`. Thus SD formatting is
not uniform. Canonical trailing-zero normalization changes no numerical value.
Printed decimals authenticate neither a rounding rule nor measurement accuracy.
The `h_C=0.05 pp` illustration is a total declared perturbation, not an
inferred nearest-decimal measurement bound or extra rounding term.

Sigma is the reported **TDS standard deviation**, whose estimator is unspecified.
Keep all reported SDs, including printed zeros, as descriptive metadata. A printed
zero SD does not establish an exact mean. It supplies neither a mean standard
error nor a duration error; no significance, p-value or confidence interval is
computed. `observations.csv`, `primary.csv` and `secondary.csv` retain these SDs
separately from conditional perturbation ranges.

## Remaining unknowns and inherited limits

Raw chemical replicate values, EY SDs, relevant covariance, actual condition-specific
dose/beverage masses and an authenticated joint timing/chemistry replicate model
are unavailable in the inspected passages/tables. Three chemical samples do not
authenticate three timed-shot values. Per-condition duration statistic, spread,
clock convention and rounding remain unspecified: **reported condition duration**
is the retained meaning. The ±0.5 s illustration is not authenticated timing error.
A condition-level join establishes no shot-level covariance or causal link.

Native pressures are nominal machine settings, not measured puck pressure drop;
exact temperature settings are not measured puck histories. Grind labels remain
native and ordinal within coffee. No physical cross-coffee particle-size scale,
measured flow from 40 g/duration, instantaneous flow or residence time is inferred.
The predecessor's excluded pooled Table 4.1 times and model/fitted fluxes remain
excluded. Its separate pooled-time discrepancy is unaffected. The historical
EY/TDS range-bracket qualification and all physical-validation labels stay intact.

## Narrow discovery-metadata correction

The existing Cibao manifest caveat described EY as a TDS × brew-ratio product
and called the ratio of published means an implied beverage/dose ratio. With
the source's dose/beverage convention the sample operator is division, followed
by averaging. This task replaces only that chemical-description sentence with
the samplewise operator and the non-identifiability of masses from mean ratios.
The source values, accepted predecessor artifacts and validation-strength fields
are unchanged; no table discrepancy or new intake correction is implied.
