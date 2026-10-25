# Substantive independent-method review

Disposition: **PASS for the bounded descriptive result**. This is a same-session
review using independent source extraction and direct-CSV arithmetic, not a claim
of a separate human reviewer or protected scoring. It imports neither the analysis
producer nor its audit script. One review engagement is retained; no review ladder
or successor is created. [Machine receipt](independent_check.json) binds the
reviewed source, implementation, audit, results and figure by SHA256.

## Independent checks

- **Source mapping:** PyMuPDF positioned-word extraction, separate from the
  producer audit's Poppler layout text, reproduces all 432 chemistry strings and
  eight ground strings. Baseline row coordinates, source pressure/temperature
  labels, page breaks and horizontal order independently establish 144 keys.
  Every row maps to the original CSV; page/row/source strings agree with the
  companion audit. Visual review of PDF 115–118 confirms table labels, repeated
  digits, trailing zeros and the continued Table 5.4 boundary. The complete PDF
  identity is checked before parsing.
- **Calculations:** the independent script directly reads unchanged CSVs and
  derives the block diameter from six pairwise distances. For all 36 blocks it
  verifies R, E, c_star, Δ, percentage change, reference-normalized E, missed
  range and all extrema/ties. It computes RSD scales/pair multipliers separately
  and verifies that the constructed lower/upper interval intersection meets at
  the resulting multiplier. It verifies all nominal attaining pairs.
- **Conditional bounds:** all actual primary strings have ±0.005 half-place
  intervals and all source diameters exceed 0.01. Hence E±0.005 and Δ±0.01 are
  independently checked for all 36 blocks. Formula review confirms the distinct
  observation requirement in the sharp range upper bound, the positive reference
  denominator, strict sign decisions, and conservative relaxation in normalized
  E and RSD ratio enclosures. The test with one [0,100] interval and three point
  intervals at 50 verifies the generic upper-bound hazard. No sampled grid is
  used as a certificate.
- **Conversion audit:** direct rational interval checks find exactly the one
  retained Table 5.2 mismatch. No concentration fusion or extra observations.
- **Claims and figure:** every pressure/temperature/analyte block is retained;
  colors/force ticks and separate analyte scales agree with the table. Rounding
  caps are distinguished from nominal means; no RSD bars are plotted. The report
  separates endpoint direction from interior extrema and reports actual blocks
  for minima/maxima. Its observation basis retains source tuning/fixed-settings,
  count, units and assay ambiguities. It supplies no adequacy budget or inference
  beyond the reported cells.

Selected hand checks (native units mg per reference 40 mL):

| Block | Four means at 10/15/20/30 kgF | R; E; midpoint | Δ; missed range |
|---|---|---|---|
| total CQA, 88°C/7 bar | 131.84, 144.31, 140.67, 138.49 | 12.47; 6.235; 138.075 | 6.65; 5.82 |
| caffeine, 93°C/7 bar | 236.49, 248.11, 235.41, 248.08 | 12.70; 6.35; 241.76 | 11.59; 1.11 |
| trigonelline, 88°C/7 bar | 120.95, 130.30, 126.96, 127.76 | 9.35; 4.675; 125.625 | 6.81; 2.54 |
| nicotinic acid, 93°C/7 bar | 5.24, 6.41, 4.65, 5.21 | 1.76; 0.88; 5.53 | −0.03; 1.73 |

For the first row, E bounds are [6.23,6.24], Δ bounds [6.64,6.66], and the
attaining RSD pair is 10/15 kgF with exact multiplier
`12.47 / (131.84×0.029 + 144.31×0.019)`.
For caffeine 93°C/7 bar, the largest RSD ratio is the 20/30 kgF pair, although
the full range involves 20/15 kgF. This checks that the diagnostic does not simply
reuse the minimum/maximum amount pair.

## Findings and disposition

The source's already exposed related-unit inconsistency was reconfirmed, not
repaired. Review identified that support summaries must honor explicit audit
support and missing precision separately: the loader now derives feature-level
rounding support and the complete precision status; coverage separately counts
mean/RSD and their rounding metadata. Synthetic missing/invalid fixtures exercise
those paths while all actual 144 records remain supported. An in-progress guide
check initially encountered the not-yet-written RESULT link; the completed bundle
passes that check. A single changed MANIFEST row's CRLF triggered whitespace QA;
only that row's terminator was normalized and existing producers rerun. Neither
correction alters the 440 source strings or scientific calculations. The endpoint CSV also carries the same source-qualification tokens as the representation CSV; numerical JSON is unchanged.

Scientific limits remain qualified limitations, not failed arithmetic. There is
no independent laboratory/population validation, calibrated RSD uncertainty,
practical-adequacy decision or isolated causal tamping result. Hosted CI is
reported separately in [VERIFICATION](VERIFICATION.md).

```bash
# Optional review path; PDF and PyMuPDF remain external to ordinary reproduction.
python docs/analysis/sci_md_khamitova_tamping_chemistry_001/independent_check.py \
  --pdf /path/to/authenticated-complete.pdf --output /tmp/khamitova-independent.json
```
