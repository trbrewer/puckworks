# Melrose2019bed Figure 2 transient flow

Dataset `melrose2019bed/fig2_flow_transient`: partial visible-marker recovery
from the 26 September2019 packed-bed preprint, printed/PDFp.11. Primary PDF
SHA256 `20b7990af4a9026b44d56a29b559ab0d02f4a094d5a3e171b8d1bb41ae58c6ed`.
Native Figure2 JPEG957×678; actual image hash and source URLs in `contract.json`.
Supporting thesis identity, method reconciliation, rights and limitations:
[observer/source record](../../../docs/analysis/sci_md_melrose_transient_hydraulics_001/SOURCE_RECONCILIATION.md).

`source_coordinates.csv` is the retained factual native-coordinate transcription;
`observations.csv` is its deterministic normalized projection in seconds, mL/s
and m^3/s (1mL/s=1e-6m^3/s). Full marker footprints,1px raster guard and shared
±1px calibration anchors give reading bounds only. Blank ordinate centers are
intentional; no hidden center was inferred. `profiles.json` separates profile
fragments from condition IDs. `ambiguous_regions.csv` accounts for unresolved
overlap, with unknown counts left blank. `contract.json` preserves shared
calibration, preparation, observer, pressure and aggregation facts/limitations.

The16-condition grid is planned coverage, not16 runs. Recoverable profile
fragments/points are not independent experimental units. Repetition count,
pointwise members, weights, exact collection endpoints and experimental error
bars for Figure2 are not established. Same Corrochano campaign as the thesis;
no independent replication or additional scored thesis dataset. Flow is an
interval-average collected-volume rate, not intrinsic permeability.

Source rights: author-uploaded publicly readable preprint; no manuscript/data
reuse license identified. Thesis is university-hosted research material with
its own rights. This compact factual derived transcription follows the existing
source-specific factual-table/figure-reading treatment; no manuscript, extracted
image or overlay is redistributed, and the Puckworks software MIT license is
not applied to either source. Source citation/rights qualification travels with
these readings. Original analysis code is Puckworks-authored.

Research only, retrospective, target exposed, source internal; physical
validation NOT_ESTABLISHED. No runtime component, production gate or raw-data
gap closure. Yield/fitted-parameter/PSD/Ymax work remains outside this intake.

Regenerate retained data and analysis from committed coordinates (no network):

```bash
python -m puckworks.analysis.melrose2019bed_transient
pytest -q tests/test_melrose2019bed_transient.py
```

The default command writes this normalized CSV and the task's CSV/JSON results.
Use `--output /tmp/melrose-reproduction` for a separate complete output directory.
Data access: `puckworks.data.melrose2019bed_fig2_flow_transient()`.
