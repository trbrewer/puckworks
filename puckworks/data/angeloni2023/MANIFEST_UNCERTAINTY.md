# Angeloni 2023 uncertainty intake manifest

## Recovered file

`angeloni2023_total_solids_lipids_rsd.csv` transcribes and has been independently checked against Tables 1–3 of Angeloni et al.,
*Applied Sciences* 13, 2688 (2023), DOI `10.3390/app13042688`. It contains all 66
Arabica/Robusta conditions for total solids and total lipids, including the published
condition-level RSD and a mechanically reconstructed standard deviation
`sd = abs(mean) * RSD / 100`.

`angeloni2023_uncertainty_summary.csv` contains the same 132 observations in the
canonical schema accepted by `tools/validate_replicate_uncertainty.py`; it is the
analysis-facing file. The source-shaped transcription is retained separately so the
published table layout and condition metadata remain auditable.

The article says analyses were carried out “almost in duplicate (n=2).” The table records
`n_reported=2` with an explicit qualification because individual-sample exceptions are not
enumerated. The full 66-condition mapping and all 132 mean/RSD pairs were checked programmatically on 2026-07-13 against the Università di Camerino author-deposited PDF; see `docs/data_intake/ANGELONI_TRANSCRIPTION_AUDIT.md`. A21 total-lipid RSD is printed as 0.0%; treat it as rounded and apply a predeclared variance floor rather than infinite weight. The file does **not** recover replicate values and does **not** recover sample/analyte-
specific RSDs for caffeine, trigonelline, or chlorogenic acids; Tables 4–5 report only that
the Arabica RSD range was 0.3–19.7% and the Robusta range was 0.1–19.2%.

## Still required

Populate `replicate_uncertainty_template.csv` from the authors’ underlying laboratory
records or a supplementary workbook. Preserve the raw source file, checksum it, and add a
row to the project’s canonical data manifest before weighted Paper A analyses are claimed.
