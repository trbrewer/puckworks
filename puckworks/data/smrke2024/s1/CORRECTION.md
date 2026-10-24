# S1 active-data correction

Parent dataset: `smrke2024/figures`; this is a corrected graphical subset of the
same experiment, not a new physical cohort. Smrke, Eiermann & Yeretzian (2024),
Scientific Reports 14:5612, DOI [10.1038/s41598-024-55831-x](https://doi.org/10.1038/s41598-024-55831-x).
Source and these derivatives: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
Native reconstruction, masks, annotations and conservative allowances were added.

The legacy CSV used a 0–3.5 g/s scale for the published 0–7 g/s axis, included
non-data legend/text ink, and numbered vertical column runs without persistent
trajectory identity. Its 18,001 rows retained only series, run_index, time_s and
flow_rate_g_per_s; no native coordinates. The yellow65.01 s/3.3948 g/s row is a
legend sample, not delivery. Multiplying by two cannot repair these defects.

The retired bytes are retrievable without ambiguity:

```bash
git show 52df324ee809249eacad1233e407434260e22d46:puckworks/data/smrke2024/41598_2024_55831_MOESM1_ESM_FigS1.csv
```

SHA256 `829253aed8e03b93a2b02187184c448b5a5b570ed60aec82c6912e41718bbf33`.
They are removed from the active tree. The corrected source observation file has
14,753 admitted native colour runs, not shots or independent samples. Every row
retains source ID, native column/ordinate extent, provisional colour assignment,
conservative reading bounds or unbounded clipping status, and temporal/membership
qualification. `source_id` resolves to the full native image SHA256 in contract.
There are 5,866 generic one-to-one raster fragments; every branch/merge ends a
generic identity. Their fines/style membership is deliberately ambiguous across
all 12 cells because mixed/antialiased ink is not authenticated trace identity.

`figS1_flow_profiles` remains a compatibility **key** alias of
`figS1_source_observations` in `smrke2024_figures()`. The defective four-column
schema is intentionally not preserved. There is no scalar `flow_rate_g_per_s`
or `run_index` implying a brew. `smrke2024_s1()` adds source contract, original
regions, explicit qualification correction, qualified fragments, raw candidate
reading cells, generic observations/fragments and excluded ink. Candidate cells
include retired regions for audit and carry temporal status; they must not be
used without the returned correction and qualified support.

Figure 3 CSV bytes, key, row ordering and the envelope/transfer consumers remain
unchanged. Accepted endpoint SOURCE/FREEZE/audit/result receipts and historical
verifier remain unchanged; current shared loader/card/notes edits cannot qualify
new current-root endpoint scoring. S-A remains qualitative; S-B remains blocked.

## Disclosed reconstruction corrections

The initial source contract and region hashes remain recorded in the analysis
CONTRACT_FREEZE. Qualification corrections are separately hash-bound in
`qualification_correction.json`; this is retrospective source-exposed work.

- The first producer wrongly retained blue corridor identity across missing
  columns 402–406, exceeding the frozen four-column allowance. That manufactured
  a shifted-lattice rise/constant exclusion. Splitting identity at every
  unbridged gap removes that conclusion. Initial machine result SHA256
  `7d05dafa44be4559a4f71f74c262bd991f889d403bfdfdce3f94177c8bfddf38`, temporal
  comparison SHA256 `feb3d294683e98c8c8ec6a7a1efe45d04788f6706fb78b8e6ac1793d26ce9297`;
  failed attempt payloads/logs are retained externally, not relabelled successful.
- Independent source review found that the candidate corridor first admits a
  second blue branch at x 479 (y 601–695); at x500 it retains neighbour ink y 685–689
  while missing the intended upper ink around y 632–643. The wholex 479–528 region
  loses temporal qualification. Original cells remain explicitly retired audit
  observations. This evidence-driven cutoff was not selected for a contrast.
- Exact y=78 contact detection missed yellow at x189–191,y79–80 because black
  axis ink overprints the edge. A four-pixel boundary neighbourhood (anchor,
  linewidth and footprint allowances rounded outward) now flags censoring and
  removes finite flow bounds. The chart maximum is not a hidden-curve bound.
- Generic colour masks became explicitly provisional, allowing all fines/style
  memberships. Only separately audited regions have definite condition labels.
- The nominal 85 s analysis limit omitted a subpixel native-frame remainder.
  Incomplete remainders now end at124880/1469 s (85.010211 s); the uncertain frame
  neighbourhood remains unsupported. No complete window changes.

After correction, two disconnected blue fragments each have at most one complete
window on a given lattice. The two solid bundles each support [6,9]s only on the
primary lattice. No qualified temporal direction/constant exclusion remains.
See the [result](../../../../docs/analysis/sci_md_smrke_transient_hydraulics_001/RESULT.md).
