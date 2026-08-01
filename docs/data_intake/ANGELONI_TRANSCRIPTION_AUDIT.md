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

---

# Addendum, 31 July 2026 — Tables 4–5 (the headline corpus)

**Result: pass — 66 samples, 726 analyte cells and 66 condition rows matched the article exactly.**

## Why this addendum exists

The audit above covered Tables 1–3 and compared them with
`angeloni2023_total_solids_lipids_rsd.csv` — total solids and lipids. Neither is a Paper A scored
analyte.

The file that carries Paper A's entire headline result is `bioactives.csv`, transcribed from
**Tables 4–5**. The 132 scored observations behind pooled MAPE 8.44 % versus 8.83 % come from its
`CF`, `TR` and `5CQA` columns, and its `T_degC`/`p_bar`/`granulometry` columns decide which records
are training and which are held out. **That file had never been machine-compared with the source.**

Twelve review rounds reported the stale-number category empty, and each was right — but that check
is *internal consistency*: the same value copied correctly from artefact to manuscript to caption.
It cannot detect a value that was wrong when it was typed in. The source contract says so directly:
it validates structure, tokens, coordinates, parseability and support, and explicitly **not**
transcription against the publication.

## What was checked

Same source document as the original audit, digest re-confirmed:

```text
https://pubblicazioni.unicam.it/retrieve/d8b5f72e-eff9-4d85-b92d-7df02046c4a7/2023ComPerMod.pdf
sha256 2600ef731c37d088838eaabb3d88e8b9ad09a7ff7b7d63d566b6a13329fc6ea7
```

| Compared | Count | Mismatches |
|---|---:|---:|
| Samples present in both article and CSV | 66 | 0 missing, 0 extra |
| Analyte cells (11 species × 66 samples) | 726 | **0** |
| Condition rows — `T_degC`, `p_bar`, `granulometry` | 66 | **0** |
| `on_grid`, **re-derived** from the article's own 3×3 grid | 66 | **0** |

All 44 held-out coarse/fine records, all 132 scored observations, and all 18 optimal-grind training
records are inside that comparison.

`on_grid` is not read back from the file being audited; it is recomputed from the article's stated
temperature and pressure against the declared calibration grid (T ∈ {88, 93.4, 98} °C, p ∈ {6, 9,
12} bar), so a mis-set flag would fail even though the flag is derived rather than transcribed.

## Reproducing it

```bash
python tools/audit_angeloni_bioactives.py             # fetches and pins the source digest
python tools/audit_angeloni_bioactives.py --pdf FILE  # against a local copy
```

Network-dependent, so **not a CI gate** — it is an intake/release audit run deliberately. Offline it
fails with a stated reason rather than passing quietly.

Non-vacuity was checked by perturbation: changing one caffeine cell (A12 `CF` 4.76 → 4.77) and one
condition (A12 9 → 12 bar) each fail with the sample, field, article value and CSV value named.

## What this does and does not establish

It establishes that the committed corpus **is** the article's Tables 1, 4 and 5.

It does not establish that the article's own measurements are correct, that the units are what the
column headers say, or that the HPLC-DAD determinations behind them are sound. Those are properties
of the source campaign and cannot be checked from the repository.

The qualification in the original audit still stands: Tables 4–5 publish only global analyte RSD
ranges, so a solute-specific weighted refit remains blocked pending a replicate drop from the
authors.
