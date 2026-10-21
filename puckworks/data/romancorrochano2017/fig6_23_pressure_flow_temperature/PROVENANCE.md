# Figure 6.23 pressure-flow temperature intake

Dataset `romancorrochano2017/fig6_23_pressure_flow_temperature`; source card
[romancorrochano2017_permeability](../../../../docs/cards/romancorrochano2017_permeability.md).
G1 / NO_GOVERNING_PHYSICS_CHANGE / RESEARCH_ONLY / RETROSPECTIVE /
TARGET_EXPOSED / SOURCE_INTERNAL / PHYSICAL_VALIDATION=NOT_ESTABLISHED.

[Thesis](https://etheses.bham.ac.uk/7176/2/Roman-Corrochano17EngD.pdf), printed266 /
PDF291. `contract.json` binds the exact PDF, native JPEGs, plan and calibration.
`source_coordinates.csv` is the offline input. Coordinates refer to the native
512×384 images, not page-render pixels. `coverage.csv` retains missing and
ambiguous support. `readings.csv` is the generated SI projection, loaded with
`puckworks.data.rc17_fig6_23_pressure_flow()`; blank fields mean missing.

Coordinate transcription used colour-excess masks as an inspection aid (channel
excess35/255 and primary channel>90), followed by native-image and enlarged-image
inspection. All-colour extrema include stroke/raster noise and grid intersections;
no smoothing, curve fit or pixel-as-sample analysis. The fixed two-pixel ordinate
guard is additional. Late upper hot-flow bounds were separately inspected and
rounded outwards; early merges are not joined to that fragment. Axis anchors are
shared ±1px enclosures; x bands are inverse-affine unions plus2px, rounded
outwards to integer pixels. Exact fractions preserve every conversion and strict
decision. The producer's float bound fields are rounded outwards where necessary.

Complete envelopes mean every represented coloured stroke over the retained full
band is enclosed. Coalesced strokes lie inside the envelope; this does not count
hidden trajectories or authenticate physical repetitions. No visible trajectory
leaves the plotted ordinate range at retained5–55s bands. Near-axis hot strokes
remain floor-indication limited. The60s bands extend beyond endpoints around
native x407; all four panel/condition slots are explicitly unsupported, although
part of each band contains ink. They are not silently clipped or extrapolated.

No raw samples, individual pressure identities or authenticated cross-panel pairs
were recovered. The late hot-flow fragment is not a paired physical run. Its ratio
uses all hot pressure ordinates, so a resolved comparison survives any fixed
pressure partner contained in those envelopes. Full hot-condition trends require
more and are reported separately. No independent campaign is added to the shared
Corrochano/Melrose lineage.

Pressure is already corrected by the source, not a direct two-tap differential.
The Figure3.3 coefficient/curve inconsistency and calibration applicability remain
unresolved. Readings are plotted inlet-meter indications at unknown volume
reference conditions; floor readings are not exact physical zero. Reading bounds
exclude experimental/calibration uncertainty. See the full
[source reconciliation](../../../../docs/analysis/sci_md_corrochano_pressure_flow_001/SOURCE_RECONCILIATION.md)
and [results](../../../../docs/analysis/sci_md_corrochano_pressure_flow_001/RESULT.md).

Rights: compact derived factual coordinates and readings only. No permission to
redistribute the thesis or source artwork is inferred from access. PDF, extracted
JPEGs, rendered pages and source overlays remain outside Git; the original
reconstruction SVG contains only retained derived enclosures. This intake does
not relabel the source material under the repository software licence.

Rebuild offline, from repository root:

```bash
python -m puckworks.analysis.corrochano2017_pressure_flow --output /tmp/corrochano-reproduction --plot
cmp /tmp/corrochano-reproduction/RESULT.json docs/analysis/sci_md_corrochano_pressure_flow_001/RESULT.json
cmp /tmp/corrochano-reproduction/readings.csv puckworks/data/romancorrochano2017/fig6_23_pressure_flow_temperature/readings.csv
```

`--plot` uses the existing optional `figures` extra. Without that flag the
producer needs no plotting dependencies or thesis download. Copy generated
`readings.csv` into this directory when intentionally regenerating the intake;
compare `conductances.csv` and `reconstruction.svg` with the result directory.
