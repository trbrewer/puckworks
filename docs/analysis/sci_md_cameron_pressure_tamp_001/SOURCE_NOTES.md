# Source and digitization notes

## Identity and rights

Cameron et al. (2020), *Systematically Improving Espresso: Insights from
Mathematical Modeling and Experiment*, Matter 2, 631–648,
[DOI](https://doi.org/10.1016/j.matt.2019.12.019).

| Source inspected | Identity | Relevant pages |
|---|---|---|
| [Official standalone SI](https://ars.els-cdn.com/content/image/1-s2.0-S2590238519304102-mmc1.pdf) | 8 pages; SHA256 `37530ec8c450c6fe5b231a7d4e3b65347555454b366ed4730ec106a4fb56775f` | Figure S2: PDF 7, printed 6; Tables S1/S3/S5: PDF 4/5/6 |
| [Author-hosted final main paper](https://pages.uoregon.edu/chendon/publications/2020/74.%20Matter%2C%20Espresso%20extraction.pdf) | 19 pages; SHA256 `efd41bb44e2542fcee04498ebc61b5c84e337601a755156e9392d12fcc93d229` | Pressure/tamp discussion: PDF 12, journal 641; methods: PDF 17–18, journal 646–647 |

Downloaded and hashed 2026-10-24. Both match the supplied reference identities;
no version substitution. The [publisher attachment locator](https://www.cell.com/cms/10.1016/j.matt.2019.12.019/attachment/4efc9b80-7dd9-496f-a386-b14828cd9078/mmc1.pdf)
is retained as an alternate locator, not represented as a separately authenticated
download. This is the standalone SI, not the older card's combined mmc2 upload.
The full supplement and relevant main-paper passages were inspected; page images
were checked against native geometry. The source artwork/PDFs remain restricted
and outside Git. Following existing Cameron figure-digitization practice, the
repository holds attributable numerical extraction records and a newly drawn
numerical plot, not publisher artwork or a blanket source redistribution licence.
No source solver code is imported or executed; existing runtime rights are unchanged.

The local Cameron holdings contained the existing Figure 2 PSD and Figure 5
deviation CSVs, not S2. Manifest, capability register, cards, analysis directories,
local/remote branch names and GitHub PR/issue searches found no overlapping S2
identity. This is bounded overlap checking, not an assertion that no unpublished
source data exist. Existing figure IDs and accepted evidence are preserved.

## S2-specific evidence versus general context

S2 directly supplies shot time (s), tamp force (N), the four series labels
{6, 9 bar} × {grind 1.3, 1.5}, four horizontal clusters and displayed vertical bars.
Its caption calls the pressure static water pressure and attributes fine/high-pressure
behaviour to choking. That attribution is the authors' interpretation, not a
mechanism established by these recovered endpoints. The caption does not define
its central statistic, bar statistic, per-point replicate count or shot-clock origin.

The main discussion reports standardizing tamping at 98 N after a range-of-tamp
exploration, with no appreciable variation reported by the authors. That sentence
neither supplies all four S2 settings nor overrides the recovered graphical
contrasts. The general methods identify a San Remo Opera, 20-g ridge-less
baskets, EK43 with coffee burrs, Puqpress accuracy ±3 N, Supreme Roasters coffee,
and an Acaia Lunar balance. They give 20.0(5) g dry coffee / 40.0(5) g beverage,
92 °C, rejection outside ±1 g shot-mass tolerance, exact beverage masses used for
EY, n=20 calibrating measurements and subsequent pentaplicates. These are general
methods context; they do not allocate n=5 or n=20, actual recipe tolerances or
bar semantics to each S2 point. Actual masses and applied forces per extraction
remain unavailable. Tamper accuracy is distinct from x-axis reading uncertainty
and is not added as a graphical tolerance.

Main text uses water-pressure labels while SI S1 uses 5-bar pump overpressure;
S5 scales model fluxes to other overpressures. The current development guide
already records the unresolved node/reference convention. S2 remains native
6/9-bar labels: no −1-bar conversion, MachineState mapping, measured puck pressure
drop or independent S5 flux measurements. Figure 5's SD description is not
borrowed for S2. No individual-shot records, randomization or covariance were recovered.

## Numerical geometry and anchor authentication

`puckworks/data/cameron2020/s2/observations.json` is the qualified data authority.
It includes the exact extracted floating-coordinate readouts, object IDs, candidate
anchors, conservative enclosures, plotted units, calibration, and force joins.
The analysis CSV is a convenient flat projection. Coordinates are PDF page points,
origin top left, y downward. Page content xref 33 places form xref 74 (native name
`Figures/FigureS2_Tamp.pdf`) at
`x=54.141+0.93796*u`, `y=657.721−0.93796*v`.
PyMuPDF's version and paint-sequence IDs are recorded; binary geometry precision
is not experimental measurement precision. Re-extraction requires the same hash;
a different PDF is refused pending version/content comparison.

Direct source labels authenticate dark=grind 1.3, light=grind 1.5, circles=6 bar,
triangles=9 bar. Every marker is associated with its connecting paths and, where
present, its two vertical bar segments. For a connector entering a marker's
horizontal footprint, the endpoint nearest its horizontal symmetry axis is the
anchor candidate. In particular, paths 102/104 are short solid end-dashes: their
interior dash ends are not central anchors. Path103 is the intervening dashed
line, not another observation. The first associated central connector endpoint
in declared series order is the **nominal reference**, not a claim of an exact
experimental or original plotting value. No conflicting candidates are averaged.

Circular symmetry corroborates the circular markers' anchors. For triangles,
the connector/bar junctions lie inside the symbol, away from its tip. Because
marker placement is not perfectly registered, the enclosure also retains the
bounding-box centre and vertex-centroid candidates; neither is imposed as the
true central value. Tip and base vertices are symbol boundaries, inconsistent
with the associated central junctions, and are rejected as anchors. Bar midpoints
are never used as central estimates. Each record retains every admitted candidate.
For example 9-bar/grind 1.3/F1 has connector y 473.9889, bar junctions near 474.106,
triangle bounding centre 472.7084 and centroid 474.4088 pt. The full candidate span
is retained, with padding on both sides. At 6-bar/grind 1.5/F3 the bar junctions
570.2675/570.3483 differ from the circle/connector 570.6529 pt; those too are enclosed.
This is a source-coordinate outer enclosure conditional on the retained candidate
interpretation, not proof of the unknown underlying experimental central statistic.

All S2 strokes are 0.93796003 pt. The recorded plan's common allowance is
0.25 + half-stroke = 0.71898001 pt around candidates, ticks and bar endpoints.
The 0.25-pt floor is a conservative graphical placement/readout allowance,
about one pixel at 300 dpi; no probability or measurement accuracy is implied.
The y frame runs from 55 s at 424.794556 pt to 25 s at 635.835571 pt.
The intermediate 50/45/40/35/30 ticks agree with the affine map to 0.000041 pt,
inside the allowance. The signed scale interval is
[−0.143127684445, −0.141190439702] s/pt. The x ticks 100/200/300 N are
99.565186/184.986420/270.407654 pt, affine to numerical precision.

Four tight clusters around x 97.2, 179.96, 220.83, 261.69 pt recur in all series.
Their padded x intervals have a common intersection at each group and are widely
separated between groups. This authenticates the common nominal design, not exact
round force values or identical actual tamp forces. F1–F4 are the stable identities;
`nominal_force_N` stays null. Actual plotted x and individual force bounds are kept,
including small first-group and connector/marker differences. No positions are
snapped to 98/196/245/294 N or inferred from the standard 98-N recipe.

## Bar and object accounting

Twelve identifiable bars are encoded as 24 vertical path segments. All 24 outer
endpoints are recovered independently; asymmetry and separate segment junctions
are preserved. Paint order and the rendered crop were inspected, including the
crowded F1 light circle/triangle. The9-bar/grind 1.5/F1 upper endpoint is encoded
at y 587.1210 pt, over the neighbouring 6-bar circle (the bar is painted later).
Inner portions pass through or under markers; encoded geometry still supplies
these endpoints. This is not an assumption that an absent path is occluded.

Four marker positions have **no recoverable vertical path**: 6-bar/grind 1.3/F2,
and 9-bar/grind 1.5/F2–F4. They retain null extents and explicit status, not zero
variability, inferred symmetry or marker-size bars. Frame/ticks/connectors/markers
and bar segments account for all 71 paths 84–154. Four additional off-plot curve
paths 155–158 lie left of the S2 frame (x≤77.590 versus frame 79.466 pt), with no
force-group association; they are excluded, not adopted as observations or bars.
Text labels, page decoration and S1 are not numerical S2 observations.

## Interval construction and reproduction

For layer A each signed observation coefficient multiplies its source-y enclosure.
Sum those intervals once; then multiply by the common signed scale interval.
All coefficients sum to zero, so the common affine offset cancels exactly.
A common scale is not independently sampled for each point. I/J start from original
observations and their signed coefficients, not rounded DP/DF bounds. Layer B
instead uses each bar's outer source-y endpoints padded once, without adding the
central uncertainty again. It is a conservative extent sensitivity with unknown
statistical meaning and correlation. It is neither a confidence interval nor a
significance/equivalence test or individual-shot/population range.

Internal contrast arithmetic uses exact rational representations of the stored
coordinate decimals; JSON retains rational bounds and numerical values. Reported
bounds round outward to 0.01 s; signs use unrounded bounds. Cartesian interval
arithmetic can be wider than a dependence-aware reconstruction, and cannot restore
missing experimental covariance or semantics. Individual plotted coordinate
bounds additionally include calibration offset; contrast bounds cancel it.

```bash
# Standard library only; committed qualified observations suffice.
python -m puckworks.analysis.cameron2020_pressure_tamp --output /tmp/cameron-s2
# Optional private-PDF audit: install PyMuPDF in a disposable environment.
PYTHONPATH=. python tools/extract_cameron_s2.py --pdf "$CAMERON_SI_PDF" --output /tmp/cameron-s2-native
cmp puckworks/data/cameron2020/s2/observations.json /tmp/cameron-s2-native/observations.json
```

The new SVG is a numerical redraw governed by bundle-local [VIZ_SPEC.json](VIZ_SPEC.json),
not a mechanism render or an image of the publisher figure. No solver component,
physics, production default, lock, CI policy or acceptance threshold changes.
