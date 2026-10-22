# Source and observation reconciliation

G1 / RESEARCH_ONLY / RETROSPECTIVE / TARGET_EXPOSED / SOURCE_INTERNAL /
NO_GOVERNING_PHYSICS_CHANGE / PHYSICAL_VALIDATION=NOT_ESTABLISHED.

The [Birmingham thesis](https://etheses.bham.ac.uk/7176/2/Roman-Corrochano17EngD.pdf)
was downloaded and its bytes inspected: SHA256
f131d9893e2ac78ce0664d5528beac4be51a02cf1ae684e41920fbc6cadc8818,359 pages.
Printed264/PDF289 is page object3193/content3194. Printed253–255,263–264 were
read textually and visually; apparatus pp62–64,88 and inlet/outlet p274 were read
textually against the existing qualified apparatus reconciliation. Source PDF,
renders, full decoded stream and inspection logs remain external. The live
[landing record](https://etheses.bham.ac.uk/id/eprint/7176/) lists the accepted
thesis PDF and no directly identified supplement. Browser PDF size limits were
bypassed by direct download, not by assuming the content.

Existing inventory/resolver queries opened11 Corrochano CSVs (10 thesis summaries,
one2015 table), including comments/headers/full tables; all matched registered
hashes. One filesystem metadata file was hash-only. Names/hashes are retained in
holdings_checked.json. These are older transport, inventory, fit-error and steady
permeability summaries, not recovered Figure6.22 native records. The Melrose
family query was unavailable in this snapshot; its records were only repository
metadata/context here. Owner-local holdings are not exhausted or nonexistent.
Native Figure6.22 records were **not recovered in this scoped check**. The
published authenticated figure supports this graphical study regardless.

## Observable and conditions

Printed253 defines hydraulic resistance as reported DeltaP_bed/Q. Figure6.22
plots Y=HR/HR_max, preserved without re-normalizing or reconstructing HR.
The caption establishes Psi_E (coarsest grind), initial400kg/m³, three displayed
repetitions per condition and means12.2e-6/2.1e-6m³/s. Preceding prose reports
2.09e-6m³/s instead; the two decimal values are separate interpretations, not
averaged or described as instrument uncertainty. Blue/high and red/low are
explicit in the legend. Conditions do not prove common evolving bed geometry.

HR_max means maximum hydraulic resistance in captions6.18/6.22. Source peaks
near1 and related p257 wording about normalization do **not** authenticate the
algorithm. Per-trace versus per-condition denominators, displayed versus longer
maximum window, handling of near-zero indications and exact maximum records
remain UNKNOWN. The mean-flow averaging interval, weighting, per-repetition
means and rounding algorithm are also UNKNOWN. No flow-error distribution.

The plotted seconds are calibrated from labeled ticks; frameleft is about1s.
Generic p63 describes valve opening as brew start, but Figure6.22's physical
trigger, channel delays and common origin are unauthenticated. Do not zero each
trace at its first vertex. A common physical t0 would change duration scaling to
t_high=t0+r*(t_low-t0); t0 is not fitted here.

Graphical H1–H3/L1–L3 name six source-stream chains, not authenticated instrument
files. Caption repetition count supports represented-condition envelopes; it
does not supply physical identities or matched pairs. p263 links the high-flow
contrast to earlier Figure6.17b and discusses6.18; reuse across related figures
is possible and no new independent campaign is counted. No pointwise cross-figure
join is claimed. The author's gas/capillary/consolidation/swelling discussion
is interpretation; this study identifies no mechanism.

## Applicable apparatus qualifications

Reuse [the existing apparatus reconciliation](../sci_md_corrochano_pressure_flow_001/SOURCE_RECONCILIATION.md):
ultrasonic USC-731 after tank/valve and before heaters; upstream0–6bar transducer;
reported bed pressure subtracts Q-dependent empty-cell/shower/filter/wall losses,
not a direct two-tap differential. Generic simultaneous10Hz LabView acquisition
is not authenticated sampling of these graphical vertices. Figure-specific
sensor response/alignment, meter volume reference and through-bed mapping remain
unqualified. The Figure3.3 positive-intercept polynomial versus displayed curve
discrepancy persists; no second correction or refit is applied. The low mean
falls below the approximate observed empty-cell calibration range, but means do
not certify instantaneous support and no new numerical allowance is imported.

Printed255's typical70–80°C inlet after3s and nominal80°C hydration context do
not provide synchronized Figure6.22 thermal/property bounds. The steady
600s/last30s protocol is not transferred to these transient means or maxima.
The estimated2–4s first-extract arrival and absorption (p255), and explicit
inlet/outlet distinction(p274), prevent equating Q_mean*t with actual cumulative
inlet, through-bed or collected outlet volume. Call it **mean-throughput proxy**.

## Graphical contract and correction record

The frozen PLAN and dataset contract specify full horizontal reading windows,
axis/stroke guards, bounded joins, support and Cartesian outer relaxation.
Raw stream and API independently agree on transformed coordinates and stroke
width; no second graphics transform. The slight anisotropy is enclosed by the
larger scale. Source clipping contains the plotted curves; boundary-centre
discrepancies<0.0002pt are enclosed by the declared0.002pt guard, without adding
endpoint support. Legend strokes are excluded; repeated frame/tick artwork
retains provenance but adds no observation. No identical curve chunks found.

Pre-production source-check correction: initial plan draft used0.04pt as the
interior tick residual check. Independent source audit found the0.4 ordinate
tick residual approximately0.0407pt; the check is corrected to0.05pt before any
formal calculation. The±0.92pt anchor/reading bounds, grids and decision rule
are unchanged. This is exposed retrospective work, not a prospective freeze.

## Rights and interpretation ceiling

Reuse the established Corrochano treatment: factual derived coordinates,
readings, limited provenance and attribution only. Thesis copyright remains
with its rights holders; no open thesis licence is asserted, and the repository
software licence is not assigned to it. Attribute Borja Roman Corrochano,
*Advancing the engineering understanding of coffee extraction*, University of
Birmingham EngD(2017), Figure6.22. Full source artwork/logs stay outside Git.

Different maximum denominators can separate normalized curves even under a
common absolute-HR law. Published-clock separation alone does not exclude an
absolute resistance law versus actual cumulative throughput, statistical
variation, a different authenticated observation mapping or physical origin.
Graphical bounds are not measurement-error bounds or population inference.
PHYSICAL_VALIDATION=NOT_ESTABLISHED in every outcome.
