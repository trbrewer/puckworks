# PRESSURE-PEAK X1: external consistency scoping

Viscosity washout has enough magnitude in principle at 90 °C, but this check
doesn't establish that it caused R(M). The Visualizer memory-clock comparison
is tighter against time than mass on the primary grid. The falling-pressure
signs are mixed and leave the peak question unresolved. None of these results
fits or tests A/LC parameters.

**capability demonstration, not validation; PHYSICAL_VALIDATION=NOT_ESTABLISHED.**
**TARGET_EXPOSED; ungraded, qualitative scoping.**
Data source: Visualizer; thanks to the contributing users who made their shots public.

## Proposed findings text

The following two sentences are proposed only. FINDINGS.md is unchanged.

> In a separate lab, machine and coffee, the Cibao/93.4 °C conditions show longer reported durations at higher nominal pressure for extra-fine grind (12 minus 9 bar: +7 s; 12 minus 6 bar: +8 s) and shorter durations for extra-coarse grind (-1 s and -7 s, respectively), as recorded in the [Perticarini pressure/grind analysis](../../analysis/sci_md_perticarini_pressure_grind_001/RESULT.md).
> This is sign-level evidence with unknown condition-specific endpoint masses, so the turnover location should be treated as specific to the grind and puck and the fitted Pd/Pstar as non-universal constants, without claiming that these durations locate a flow peak.

The -1 s contrast isn't strictly negative under the source analysis's
illustrative h=0.5 s rounding allowance. No duration was converted to flow.

## Viscosity magnitude bound, plug-in only

The [Waszkiewicz card](../../cards/waszkiewicz2025.md) and
[preprint v2, II.1-II.2 and Appendix A](https://arxiv.org/html/2512.21528v2)
give 18.50 +/- 0.05 g, a Sanremo Zoe Competition, and IMS Competizione
B682TCH26.5E: 58 mm internal diameter, 26.5 mm basket height and 14 mm dry bed
height. Section V.1 discusses 90-96 °C; the checked experimental methods don't
state an exact measured brew temperature. These are conditional window endpoints.
The legacy constants CSV's 28 mm radius differs from the paper's 29 mm radius;
this calculation uses the paper, without changing the legacy file.

Solids needed for viscosity 2.7 times the existing water-viscosity closure:

| Temperature | Eq 10 solids fraction (wt%) | Table 1 solids fraction (wt%) | Domain |
|---|---:|---:|---|
| 90 °C | 0.227327 (22.7327%) | 0.222187 (22.2187%) | Both in domain; table interpolation |
| 96 °C | 0.228494 (22.8494%) | Unavailable | Eq 10 temperature-extrapolated; no Table-1 value |
| 365 K = 91.85 °C, table edge only | 0.227670 (22.7670%) | 0.224749 (22.4749%) | Both in domain; not a 96 °C measurement |

Water viscosities are 0.312674 and 0.291838 mPa s at 90 and 96 °C.
[VISCOSITY_BOUND.csv](VISCOSITY_BOUND.csv) also reports the exact-e target,
viscosities and domain checks. No out-of-domain table call was allowed to clamp
to an endpoint. All 24 committed Table-1 cells match the local source transcription.

The total R rise is e; after one Mc it is only exp(1-exp(-1)) times its initial
value. At fixed bed, temperature and density, the 90 °C result makes viscosity
washout large enough in principle under a final-water-limit assumption. It needs
concentrated in-pore liquor; the existing espresso evidence doesn't establish
that concentration. Industrial extract composition, oils/fines/gas, spatial
concentration and series resistance limit the comparison. Gagne 2021 is the
hypothesis source, not a mechanism test. The extrapolated 96 °C result doesn't
gain measured-table support.

For accessible porosity epsilon, dry bed volume is 36.9891 ml and
**Vp = 36.9891 epsilon ml**, with 0 < epsilon < 1. Using the inherited
Mc = 28.709461834955388 g and water density, **Mc spans 0.808964/epsilon pore
volumes at 90 °C and 0.812531/epsilon at 96 °C**. Accessible porosity isn't
measured here. This water-equivalent scale is conditional on pore accessibility,
swelling and retention; the paper's model-effective Phi isn't a measured void
fraction, and delivered mass isn't in-pore inventory.

## Visualizer funnels and falling-pressure signs

All 465 source files match the owner inventory. The canonical reader gives
23,169 logical records, no revisions or same-timestamp conflicts. The retained
machine label is missing for every record, confirmed against the index.
No label is inferred from a curve or parser. The existing native-provenance
reconciliation authenticates no DE1 record, so that funnel stops there.

| Funnel / reported label | Canonical records | Pressure + scale weight on common time base | Pressure spans 9-5 bar | Strict selected / usable | Secondary selected / usable | Flat selected / usable |
|---|---:|---:|---:|---:|---:|---:|
| Authenticated DE1 | 23,169 examined; 0 authenticated | Not run | Not run | Not run | Not run | Not run |
| DE1/Decent label | 0 | 0 | 0 | 0 / 0 | 0 / 0 | 0 / 0 |
| Meticulous label | 0 | 0 | 0 | 0 / 0 | 0 / 0 | 0 / 0 |
| Gaggiuino/GaggiMate label | 0 | 0 | 0 | 0 / 0 | 0 / 0 | 0 / 0 |
| Other/unknown label | 23,169 | 14,471 | 3,419 | 426 / 426 | 427 / 427 | 92 / 92 |

Resolution is defined for 14,397 common-channel records. All selected windows
are state-unknown, with no authenticated active-brew window. Shutdown/venting
contamination remains unresolved. Multiple candidates occurred in 35 strict,
36 secondary and 3 flat selections; the earliest eligible window was retained.
Labels are user/parser-reported, not verified hardware; the named strata happen
to be empty. Unknown records never enter the authenticated count.

Strict sweep duration is median 2.835 s [IQR 1.724, 4.197], range 0.063-15.000 s;
secondary is 2.849 s [1.728, 4.231], with the same range. Native cadence median
is 0.225 s in both views, range 0.038-1.260 s. The per-sweep largest native gap
has median 0.271 s, range 0.073-1.260 s. Ninety selected sweeps in each view have
negative scale increments. No negative, zero or noisy flow was excluded.

Flow is an estimate from measured scale-weight increments, not a direct flow
sensor. Achieved machine-logged pressure isn't established puck pressure;
pump/model flow is unused. Adjacent interval-flow estimates are assigned their
interval pressure midpoints for secants; plateaus and pairs crossing 6 bar are
unassigned. These are finite-resolution path slopes, without smoothing or lag
correction.
The secondary sign summary retains small upward reversals; X1.3's negative
memory-term argument applies where pressure is falling.

| View | Above 6 bar: positive / negative / zero secants | Below 6 bar: positive / negative / zero secants | Whole-side 9-6 signs (+/-/0) | Whole-side 6-5 signs (+/-/0) |
|---|---:|---:|---:|---:|
| Strict | 1,691 / 1,683 / 331 | 755 / 736 / 125 | 161 / 178 / 87 | 179 / 143 / 104 |
| Secondary | 1,725 / 1,715 / 331 | 764 / 745 / 125 | 162 / 182 / 83 | 179 / 145 / 103 |

These are mixed, noisy or sparse patterns, **unresolved under X1.3**. Positive
path slope below 6 bar is the informative sign consistent with an interior
capacity peak under the stated increasing-memory assumption; positive slope
above 6 bar conflicts with a falling fixed-state capacity there. Negative slope
below 6 bar is unresolved. These sign counts neither locate a peak nor establish
or reject a universal law. Pressure node/calibration, evolving puck properties,
scale lag and differentiation, cup transit, unknown coffee/grind/dose and
public-upload selection remain confounds.

## Memory clock

Amendments 3-5 were committed before corpus collapse calculations. Amendments
3-4 and X1.5 were also in place before any weight values were decoded. Selection
used pressure/time/state plus channel presence only; private IDs/windows were
frozen before weights. Every selected segment with usable scale flow was kept.
The tercile table was written first, then qbar_med and the grids, then metrics.

The 92 other/unknown segments have median duration 15.2 s [IQR 11.7375, 20.7],
range 10.0-65.2 s. Mean-flow tercile boundaries are 0.8924731183 and
1.6661607369 g/s. **qbar_med = 1.2950287243765504 g/s**, giving primary mass
0-12.9502872438 g alongside time 0-10 s, each with 21 points.
This matches the median mean-flow scale; an evolving segment's M(t) needn't
be linear in time.

| Group | Segments | Mean-flow range (g/s) | Median duration (s) | Mass spread | Time spread |
|---|---:|---:|---:|---:|---:|
| Whole other/unknown, primary | 92 | 0-2.913462 | 15.20 | 2.071829 | 0.910644 |
| Slow tercile, descriptive only | 31 | 0-0.875000 | 16.60 | 4.316292 | 0.795107 |
| Middle tercile, descriptive only | 30 | 0.927419-1.654971 | 17.25 | 0.821250 | 0.868129 |
| Fast tercile, descriptive only | 31 | 1.671756-2.913462 | 13.10 | 0.846348 | 0.924599 |

The primary whole-stratum mass-minus-time spread is **+1.161185**. Time is
tighter, a qualitative population pattern favouring a time-based conditioning
state under X1.4. It doesn't identify M2 or exclude R(M)/viscosity washout.
Puck variation, preinfusion history, scale lag and grind/dose differences can
produce either pattern. Under X1.5, only the whole-stratum comparison carries
clock information: with the stratum-wide grid, the slow tercile's mass points
sample later and the fast tercile's earlier, biasing their comparisons in
opposite directions. The middle/fast descriptive mass advantage isn't separate
clock evidence.

The pooled reported-label result is numerically identical because it contains
only other/unknown records. Each named-label stratum has zero segments and an
unavailable clock comparison. No pooled result is authenticated DE1 evidence.

Four segments have an exactly zero final-quarter normalizer and remain in the
selection/bin counts with unavailable normalized-flow diagnostics. Nineteen have
nonmonotone weight; none has a negative normalizer. Paired primary-grid support
ranges from 62 to 88 segments, with a variance at all 21 indices. Ten contributing
segment-grid pairs have repeated upward mass crossings, at most three at one
index; the first was used as declared. These disclosures matter for interpreting
the large normalized spreads. There was no smoothing, outlier removal or flow
selection.

The secondary Mc mass grid gives whole-stratum mass/time spreads
**1.657889 / 0.890900**, still tighter against time. It samples later for slower
shots, nearer the final-quarter normalizer, and is biased toward tighter mass
collapse. Its paired support is 27-88 segments and differs from primary support;
it cannot replace the primary result. Per-tercile secondary results are descriptive
only in the CSV.

## Outputs and checks

Aggregate CSVs contain the viscosity bound, both funnels, quality summaries,
sweep signs, pre-metric flow bins/grids and collapse spreads/per-grid support.
Every Visualizer table carries the required credit. Raw arrays, identifiers and
selected-shot manifests remain outside Git. The staged entry point is
`python -m puckworks.analysis.pressure_peak_x1` with phases `properties`, `select`,
`prepare`, `collapse`, `aggregate`; private source/output paths are CLI arguments.
`prepare` cannot invoke collapse. `collapse` verifies the recorded plan, selection,
bin and grid hashes before reading prepared segments.

Focused tests: 16 passed on Python 3.10 and 3.12. Synthetic checks cover projection
without weight decoding, pressure selection, support intersection, normalization,
negative readings, tercile ties, table domain guards and units. Committed aggregate
arithmetic replays use assert_allclose(rtol=1e-12, atol=0). Ruff passes; statusdoc
verification passes. The full Python 3.12 quick lane completed with **7,854 passed,
69 skipped, 84 deselected in 1,541.99 s**. Two warnings came from unchanged C3d
arithmetic and the Visualizer development salt; there were no failures. A separate
private-data recomputation reproduced both whole-stratum grid results at the
same replay tolerance and verified every frozen pressure window.

Status and C3e artifacts are unchanged. #408 stays draft with auto-merge off.
Owner review is the next step; this scoping result doesn't select a successor.
