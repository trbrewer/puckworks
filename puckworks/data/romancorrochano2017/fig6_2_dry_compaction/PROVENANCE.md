# Figure 6.2 dry mechanical loading

Borja Roman Corrochano, *Advancing the engineering understanding of coffee
extraction*, University of Birmingham EngD (2017), Figure6.2 printed223 /
PDF248 / index247; methods Section3.3.15 printed85 / PDF110 / index109.
[Original source](https://etheses.bham.ac.uk/7176/2/Roman-Corrochano17EngD.pdf).
PDF SHA256 f131d9893e2ac78ce0664d5528beac4be51a02cf1ae684e41920fbc6cadc8818.

Compact factual source-derived coordinates and provenance only. Source copyright
remains with its rights holders; no thesis reuse licence or repository MIT grant
is asserted for source material. PDF, source artwork, screenshots and full decoded
streams remain external, consistent with the existing Corrochano intake policy.
The original analysis figure is a Puckworks reconstruction with attribution.

- coordinates.csv: every original vertex once, including four separately named
  legend strokes (empty trace). Raw decimal operands and exact page-point coordinates
  are retained. Top-left origin, y downward; no density/force smoothing.
- paths.json: transforms, widths/caps/joins/dashes, axis geometry and tick checks,
 152 curve paintings mapped to76 unique chunks,64 bounded joins,12 graphical
  identities, clip/support provenance and four legends. Painting numbers are not
  independent observations; source-stream draw order is retained. No unassigned
  coloured marks. API folding of collinear lines into quads does not remove raw vertices.
- contract.json: fixed two-axis bounds, requested levels and limited-null rule.
- holdings_checked.json: the single bounded native-record check; no external-corpus
  exhaustion claim. Native mechanical records: Not recovered in the scoped check.

B/C/D/E mean thesis Psi_B/Psi_C/Psi_D/Psi_E (journal A/B/C/D). Within grind,
1=solid,2=dashed,3=dash-dot. These identify source graphical chains, not authenticated
physical specimens or instrument files. Twelve curves represent the caption's
three sample measurements per grind; no new independent campaign is created.

Original units: force N; dry bulk density kg/m³; page coordinates PDF points.
Graphical bounds, between-curve variation, unknown physical variability and
unquantified mechanical-instrument uncertainty are distinct. No confidence limits,
constitutive law, stress/porosity/strain transformation or wet-bed extrapolation.
PHYSICAL_VALIDATION=NOT_ESTABLISHED.

Offline analysis:

```sh
python -m puckworks.analysis.corrochano2017_dry_compaction --output /tmp/dry-compaction --plot
```

Optional source audit (PyMuPDF2.0, exact authenticated PDF; never part of routine reproduction):

```sh
python tools/extract_corrochano2017_dry_compaction.py SOURCE.pdf --output /tmp/fig6-2-audit
```

This deterministically re-extracts coordinates.csv and paths.json. The source is
not downloaded by either command. Detailed interpretation is in the task's
PLAN.md and SOURCE_RECONCILIATION.md under docs/analysis.
