# Figure 12: historical raw file and qualified view

`fig12_pressure_comparison.csv` is preserved byte-for-byte (SHA256
`03716bc0938fabd5bdb58069d4445fc8702da9581ff1715625c14cde044562fa`).
`README_manifest.csv` and all other historical Moroney source files are unchanged.
The legacy `moroney2015_data()['fig12_pressure']` still returns all **94 raw rows**.
Its historical MEASURED tag means plotted-coordinate extraction, not authenticated
experimental identity or zero reading error.

[SCI-MD-MORONEY-FIXED-FLOW-PRESSURE-001](../../../docs/analysis/sci_md_moroney_fixed_flow_pressure_001/RESULT.md)
authenticates four legend samples (one-based data rows 7/32/54/79) and 90 data
markers. New scientific use should load the
[qualified sidecar](../../../docs/analysis/sci_md_moroney_fixed_flow_pressure_001/qualified_observations.csv)
with `puckworks.analysis.moroney2015_fixed_flow_pressure.load_qualified()` in a
repository checkout. It uses Figure 12 native centers, retains raw differences,
reading allowances and all 44 Figure 3 reuse links. See the source-object accounting
and observation/pressure limits in that bundle. Do not treat legend deletion alone
as qualification, reuse as independent extractions, or graphical sensitivity as
experimental uncertainty. Other family subsets gain no new qualification here.

PHYSICAL_VALIDATION=NOT_ESTABLISHED.
