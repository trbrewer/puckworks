# Angeloni 2023 Tables 1–3 transcription audit

**Audit date:** 2026-07-13
**Result:** pass — 66 condition mappings and 132 mean/RSD pairs matched exactly.

## Source checked

Angeloni et al., “Computer Percolation Models for Espresso Coffee: State of the
Art, Results and Future Perspectives,” *Applied Sciences* 13, 2688 (2023), DOI
`10.3390/app13042688`.

The audit used the author-deposited article PDF at the Università di Camerino
repository:

`https://pubblicazioni.unicam.it/retrieve/d8b5f72e-eff9-4d85-b92d-7df02046c4a7/2023ComPerMod.pdf`

Downloaded-file SHA-256:

```text
2600ef731c37d088838eaabb3d88e8b9ad09a7ff7b7d63d566b6a13329fc6ea7
```

## Checks performed

1. Extracted layout-preserving text with `pdftotext -layout`.
2. Parsed all 66 sample-to-temperature/pressure/grind mappings from Table 1.
3. Parsed all 66 total-solids mean/RSD pairs from Table 2.
4. Parsed all 66 total-lipid mean/RSD pairs from Table 3.
5. Compared every parsed field to
   `puckworks/data/angeloni2023/angeloni2023_total_solids_lipids_rsd.csv`.
6. Recomputed every `sd_reconstructed` as `abs(mean) * RSD / 100`.

No mismatch was found.

## Qualification that remains

The reconstructed SDs are not raw replicates and are not standard errors. Table 3
contains one lipid RSD printed as `0.0%` (A21). That rounded value must not create
an infinite statistical weight; a predeclared analytical-resolution or variance
floor is required. Tables 4–5 give only global analyte RSD ranges rather than
sample/analyte-specific uncertainty, so they cannot support the requested
solute-specific weighted Paper A refit without an additional source-data drop.
