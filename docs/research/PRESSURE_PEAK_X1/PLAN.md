# PRESSURE-PEAK X1: external consistency scoping

**PLAN ONLY. Stop for owner review before implementation or analysis.**
**capability demonstration, not validation; PHYSICAL_VALIDATION=NOT_ESTABLISHED.**
Retrospective, TARGET_EXPOSED, ungraded scoping. G0 documentation now; no new governance layer.

Base main: **45387cf00ff001d656c2e6dc60369c37d5aa948d**, the #407 squash commit.
Branch: **pressure-peak-x1-plan**, in a separate worktree. X1 does not alter the
C3e branch, its accepted artifacts, or any C3e full-stage work. This PR changes
only this plan, remains draft and unmerged, and has auto-merge disabled.

Use existing evidence and Python only. No A/LC fit to external data, new
experiment, new shot acquisition, bootstrap, onset refit, runtime model change
or solver work. The three parts below are separate checks, not pooled evidence
or a score for choosing A versus LC. Interpretation rules are fixed here before
X1 results. Any later implementation needs owner approval of this plan.

## Sources and access checked for planning

Read the espresso data guide, MANIFEST, available-data register, relevant cards
and prior-use limits. The configured local collection is mounted. Planning
inspected repository source transcriptions, prior results, channel-mapping code
and local source locators; it did not open Visualizer shot arrays, select shots,
count eligible sweeps, evaluate viscosity roots or calculate pore volumes.

| Part | Existing evidence | Limit carried forward |
|---|---|---|
| Duration signs | `perticarini2024/ey_tds_cibao`; [accepted pressure/grind result](../../analysis/sci_md_perticarini_pressure_grind_001/RESULT.md) and its source notes | Reported condition durations, nominal pressure, unknown condition-specific endpoint masses; no measured flow curve |
| Rheology | `g10_liquor_rheology/telisromero2001_tables` and `g10_liquor_rheology/telisromero2001_closures`; [Telis-Romero card](../../cards/telisromero2001.md), committed Table 1 and Eq-10 coefficients | Industrial soluble-coffee extract, not espresso liquor; temperature/concentration domain matters |
| Waszkiewicz context | [source card](../../cards/waszkiewicz2025.md), [revised preprint v2](https://arxiv.org/html/2512.21528v2#S2), `waszkiewicz2025/constants`, accepted C2/C3e artifacts | One rig/coffee/grind; source geometry and model-effective porosity are different inputs |
| Hypothesis | [Gagne 2021 card](../../cards/gagne2021.md) | Viscosity washout is a hypothesis; endpoint-anchored inverse reconstructions do not identify it |
| Operating histories | `visualizer/hydraulic_timeseries`, logical corpus `VISUALIZER_COFFEE_API_CRAWL_2026_07_15`; [card](../../cards/visualizer_coffee.md), [provenance](../../../puckworks/data/visualizer/PROVENANCE.md), [reconciliation](../../../puckworks/data/visualizer/reconciliation/ewp_rwb_001/RESULT.md) | Public, self-selected records; normalized machine labels and API IDs do not prove device or physical-shot identity |

The newer Telis-Romero card and measured-table manifest entry supersede the old
G10 envelope's claim that the tables are still missing. Use the measured table
and Eq-10 coefficient files, not that older magnitude guess. Source records and
historical cards stay unchanged. Existing raw files remain outside Git.

## 1. Proposed findings note, no new analysis

After approval, the following two sentences are proposed for
[PRESSURE_PEAK_FINDINGS.md](../PRESSURE_PEAK_FINDINGS.md); this PR does not edit it:

> In a separate lab, machine and coffee, the Cibao/93.4 °C conditions show longer reported durations at higher nominal pressure for extra-fine grind (12 minus 9 bar: +7 s; 12 minus 6 bar: +8 s) and shorter durations for extra-coarse grind (-1 s and -7 s, respectively), as recorded in the [Perticarini pressure/grind analysis](../../analysis/sci_md_perticarini_pressure_grind_001/RESULT.md).
> This is sign-level evidence with unknown condition-specific endpoint masses, so the turnover location should be treated as specific to the grind and puck and the fitted Pd/Pstar as non-universal constants, without claiming that these durations locate a flow peak.

When inserting the text into FINDINGS.md, adjust the relative link for that
file's directory. Retain the existing analysis's distinction between nominal
signs and conditional rounding sensitivity: the -1 s extra-coarse 12-minus-9
contrast is not strictly negative at its illustrative h=0.5 s allowance.

**Interpretation rule X1.1:** These reported duration contrasts support a
grind-dependent pressure response at sign level only. Do not convert nominal
40 g divided by duration into measured flow, locate a peak, align grinder
settings across sources, pool temperatures/coffees, or infer a mechanism.
Treating Pd/Pstar as non-universal is the transfer caution, not a measurement
of their values in this other campaign.

## 2. Plug-in viscosity magnitude bound for R(M)

First authenticate apparatus context against the Waszkiewicz card and paper,
recording version/section and distinguishing reported facts from assumptions.
The card gives dose **18.50 +/- 0.05 g**, Sanremo Zoe and a 58 mm basket. The
revised preprint, sections II.1-II.2 and Appendix A, adds **IMS Competizione
B682TCH26.5E**, internal diameter **58 mm**, basket height **26.5 mm**, and dry
coffee height **14 mm**. Use dry coffee height, not basket height, for dry bed
volume. The legacy constants CSV instead encodes radius 28 mm (56 mm diameter);
do not silently mix it with the paper's 58 mm geometry or change that artifact.
Use the explicit v2 apparatus dimensions for this plug-in geometry and disclose
the difference.

The checked card does not give brew water temperature. Section V.1 of
[v2](https://arxiv.org/html/2512.21528v2#S5.SS1) discusses a **90-96 °C** brewing
window, but the checked experimental methods do not identify an exact measured
temperature for these runs. Confirm that distinction before execution. In the
absence of a more specific existing source record, report a conditional
sensitivity at the two published window endpoints, not a claimed measured
setting or an invented midpoint. The schematic boiler temperature is not brew
water temperature. No new source contact or measurement is authorized.

Use the accepted descriptive reference **Mc = 28.709461834955388 g** as a
plug-in scale, not a new fit. For the unchanged memory law,

\[
R(M)=\exp[-\exp(-M/M_c)],\quad
R(\infty)/R(0)=e\simeq2.7,\quad
R(M_c)/R(0)=\exp(1-e^{-1}).
\]

Thus the requested approximately 2.7-fold rise is the total asymptotic rise;
it is not all attained after one Mc. Hold pressure, permeability, geometry and
temperature fixed when using q proportional to 1/mu as a magnitude bound.
This viscosity-only comparison also holds density fixed; changing liquor
density affects mass flow, so a viscosity ratio is not an exact mass-flow ratio.
The water-limit reference gives the most favorable washout comparison:

\[
\mu_{\rm early}/\mu_{\rm water}(T)=2.7,\qquad
\mu_{\rm Eq10}(T,X_w)=1.99\,10^6
 \exp[14514/(8.314T)]X_w^{-6.07},\qquad
w_s=1-X_w/100.
\]

T is kelvin, Xw is percent water by mass, and ws is solids mass fraction.
Use `puckworks.data.telisromero_viscosity_pas` and the existing
`pannusch2024.closures.water_viscosity`; do not refit coefficients or mistake
Eq-10 extrapolation to Xw=100 for measured pure-water viscosity. Invert Eq 10
algebraically for the requested 2.7 ratio, reporting ws as a fraction and wt%,
temperature, viscosities, domain status and the corresponding exact-e target
as a normalization check. This inversion is a plug-in calculation, not a fit
to espresso flow.

Independently compare with piecewise bilinear Table-1 interpolation, in its
actual **295-365 K, 76-90% water** domain. Invert only if the target is bracketed
there; otherwise report the attainable endpoint ratios and an unbracketed root.
The existing `telisromero_eta_measured` clamps out-of-box arguments: guard the
domain before calling it. At the upper published brew-window endpoint, Eq 10
is temperature-extrapolated and no measured-table value exists at that T.
Show the 365 K table edge separately, never relabel it as a measurement at
96 °C. No concentrated-regime substitution or silent clamping to obtain a root.

Estimate pore volume transparently. First compute dry bed volume
`Vbed = pi*(D/2)^2*h0` from the reported apparatus. Then report

\[
V_p(\epsilon)=\epsilon V_{\rm bed},\qquad
N_{\rm pore}(T,\epsilon)=\frac{M_c}{\rho_w(T)V_p(\epsilon)},\quad 0<\epsilon<1.
\]

Use consistent mass/volume units and the existing water-density closure for
this water-equivalent conversion. Distinguish connected flow pores from total
voids, particle-internal porosity, headspace and liquid retained by swelling.
The checked source does not independently measure the relevant accessible
porosity. Do not turn its model-effective Phi=m_d/m0 into a measured pore
fraction, import another coffee's porosity as a fact, or call Vbed pore volume.
Unless an existing same-campaign source establishes epsilon, deliver the
conditional Vp(epsilon) estimate and Mc-in-pore-volumes expression, with the
geometric bound Vp<Vbed, rather than an unsupported scalar. Identify the missing
input plainly. Density, swelling and pore accessibility limit any physical
washout interpretation; hydraulic M is not a measured in-pore liquid inventory.

**Interpretation rule X1.2:** A concentration that can supply the 2.7 ratio
inside the measured rheology domain makes viscosity washout large enough in
principle under the fixed-bed, water-limit assumption. It does not show that
the espresso puck reached that concentration or that viscosity caused R(M).
A ratio unavailable inside that domain leaves the magnitude unsupported by
that table, not physically disproved. Eq-10 extrapolation is labelled separately.
Industrial-extract composition, spatially varying concentration and series
hydraulic resistance prevent equating one local high viscosity with a whole-bed
2.7 ratio. Mc expressed in pore volumes supplies a scale comparison, not a
measured residence time or identified washout law. If porosity or exact brew
temperature remains unknown, keep the result conditional. Gagne 2021 supplies
the hypothesis, not an independent measurement of viscosity in these brews.

## 3. Visualizer scoping, selection fixed before flows are inspected

Use only the mounted public July-15 snapshot resolved through the existing
local inventory and canonical-version reader. No harvest or download of new
shots. Authenticate file identities and preserve the existing latest-version
rule; count each logical API shot once. Duplicate physical uploads or sessions
remain unknown without a source crosswalk. Do not count shards, revisions,
generated PLAY outputs or copies of one snapshot as additional shots.

First inspect native provenance metadata and channel presence only. DE1
eligibility requires retained explicit device/native-export evidence that
identifies a DE1 and the channel mapping; a normalized `machine=decent` guess,
a parser name alone or a familiar pressure curve is insufficient. Reuse the
existing reconciliation evidence, including its unresolved pressure-bearing
provenance, without another structural-signature guessing exercise. Report
unidentified records separately and never relabel them DE1 to enlarge the count.
Zero authenticated DE1 records is a possible scoping outcome; it does not mean
the physical shots were not DE1 or that no pressure sweeps exist.

Channel meanings to report:

| Channel | Role in X1 |
|---|---|
| `espresso_pressure` / `pressure__Pa` | Achieved machine-logged pressure; sensor node and gauge reference require native provenance; not established puck pressure |
| `espresso_pressure_goal` | Commanded pressure, never a substitute for achieved pressure |
| `espresso_weight` / `weight__kg` | Scale mass measurement, subject to calibration, tare and latency |
| `espresso_flow_weight` / `mass_flow_from_scale__kg_per_s` | Scale-derived mass-flow estimate, not an independent direct flow sensor; retain its source filtering and latency caveat |
| `espresso_flow` / `flow_reported__native` | Pump/model estimate with possible volume/mass/proxy ambiguity; excluded from the primary flow view |

### Declared extension: reported labels and the memory clock

Amendment 3 is declared before any Visualizer pressure, flow or weight arrays
are decoded. Only source/index metadata and compressed-file byte hashes have
been inspected in X1. This extension is not POST-HOC EXPLORATORY. Historical
corpus exposure remains TARGET_EXPOSED; no blind-data claim follows.

Keep the authenticated-DE1 funnel above. Add a parallel funnel requiring only
achieved pressure and scale weight on a common native time base. Stratify its
records by the retained reported machine label: **DE1/Decent**, **Meticulous**,
**Gaggiuino/GaggiMate**, and **other/unknown**. Use the existing normalized
`machine` label; case-insensitive DE1/Decent, Meticulous, Gaggiuino and
GaggiMate tokens map to those named strata; absent, conflicting or other labels
go to other/unknown. Labels are user/parser-reported, not verified hardware.
Keep all strata separate from the authenticated count. Apply both the strict
and resolution-tolerant falling-pressure selections and the one-sided X1.3
rule to each funnel. For the reported-label view derive flow from scale-weight
increments over native time intervals; never substitute pump/model flow.

Before opening flow or weight values, also select flat-pressure segments in
each reported-label stratum. A qualifying contiguous segment lasts at least
**10 s**, has median achieved pressure in **[6,10] bar**, and every pressure
sample lies within one per-record channel resolution of that segment's own
median. Resolution is the same smallest positive absolute successive pressure
difference defined above. Undefined resolution cannot qualify a segment.
Missing pressure, duplicate/non-increasing timestamps and acquisition breaks
split support; no smoothing or pressure repair. Search maximal qualifying
native-sample intervals. Retain one per logical record: earliest start, then
longest duration if starts tie; report multiple-candidate counts. Keep known
active-brew and state-unknown status, excluding explicitly non-brewing states.
Do not use duration as a substitute for a mean-flow stratum.

Freeze pressure-selected segment IDs/windows privately before reading weight
values. Then compute each selected segment's mean scale-derived flow as
`(W(end)-W(start))/duration`. Keep every pressure-selected segment with usable
scale flow. Flow values set bins only; they never select or exclude a segment.
For each machine-label stratum, split those segments into mean-flow terciles
using the empirical 1/3 and 2/3 quantiles with linear interpolation, fixed here.
Intervals are `q <= b1`, `b1 < q <= b2`, and `q > b2`; ties stay together, so
counts need not be equal and a bin may be empty. Also form terciles for the
pooled reported-label set and report that set separately, retaining its label
composition and never adding it to authenticated DE1 evidence. Record each
bin's boundaries, segment count, mean-flow range and median segment duration
in an aggregate CSV before any collapse metric is computed or inspected.

For each selected segment use native interval flow `q_i=Delta W/Delta t`.
Normalize by its time-weighted final-quarter mean flow, obtained from the
weight increment over the final quarter divided by that interval's duration.
Use linear interpolation of weight only at the quarter boundary. Retain
negative/noisy readings and disclose them. Missing weight support or an exactly
zero normalization denominator yields an unavailable diagnostic, not a deleted
selection or a substituted channel; disclose negative denominators separately.

Fix physical grids now, without rescaling each shot to its own duration or
delivered mass: **time x_j = 10*j/20 s** and **mass x_j =
28.709461834955388*j/20 g**, for **j=0,...,20**. The time extent is the minimum
eligible plateau duration; the mass extent is the accepted descriptive Mc.
These are distinct physical windows, so the comparison is conditional on this
declared grid, not invariant under arbitrary axis rescaling. No fitted clock
conversion is allowed. Read the interval flow containing each time point.
For each mass level use its first upward crossing by `W(t)-W(start)` and that
native interval's flow; at mass zero use the first interval. Report nonmonotone
scale-weight segments and repeated crossings as measurement limitations; do
not replace mass with a smoothed or monotone-fitted trajectory.

At each grid index use the same segments in the two comparisons: the
intersection with finite normalized-flow support at both corresponding physical
x values. Unsupported values remain missing; no extrapolation. Keep all
selected segments in the count and bin tables, and report contributing counts
at every grid point. With at least two contributors, compute the population
variance of normalized flow about its between-shot mean. The collapse metric
is the square root of the equally weighted mean of those variances over the
common supported grid indices. Report mass spread, time spread and their signed
difference, with the number/range of supported grid indices. No supported
index means unavailable. A smaller spread is tighter; exact equality is a tie;
introduce no numeric superiority band. For the separately reported pooled set,
the same metric includes variation between reported labels, which is a confound.
These are descriptive spreads, not confidence intervals or model grades.

**Interpretation rule X1.4:** "Tighter collapse against delivered mass than
against time is consistent with a throughput-driven memory such as R(M) or
viscosity washout; tighter collapse against time favours a time-based
conditioning state such as M2's clock. Either is a qualitative population
pattern across uncontrolled pucks, not a test of A or LC parameters, and
puck-to-puck variation, preinfusion history, scale lag and grind/dose
differences can produce either."

Freeze the following pressure-only selection before opening flow or weight
values. Channel presence may be inspected; flow magnitude, sign, trend or
agreement with a peak must never select a shot or sweep.

1. Require authenticated DE1 provenance, achieved pressure, scale weight and
   scale-derived flow channels on the same native elapsed-time coordinate.
   Require finite pressure and strictly increasing times; missing points,
   duplicate timestamps and documented acquisition breaks split support.
   Retain an exclusion count for each reason, without inventing repaired data.
2. On the original achieved-pressure samples, find maximal non-increasing
   runs: every pressure increment is <=0; ties are allowed. Require a run to
   cross both **9 bar and 5 bar** downward, in that order. These exact crossings
   operationalize the requested approximately 9-to-5 sweep. In this primary view,
   no pressure smoothing, isotonic fit or jitter tolerance is used. Interpolate crossing times
   linearly within their bracketing native samples; never extrapolate.
3. Exclude a run explicitly identified by native state metadata as pump-off,
   venting or outside brewing. Keep state-unknown candidates in a separate
   count, with shutdown contamination unresolved. For multiple qualifying
   runs, select the earliest within each shot, using pressure/time/state only;
   also report the number with multiple candidates. Do not choose the run whose
   flow looks most favorable. Keep active-brew and state-unknown counts separate.
4. Freeze the private selected IDs/windows. Only then inspect finite aligned
   scale-flow support. Report missing flow, gaps and derivative support rather
   than replacing it with pump-estimated flow. Keep the pressure-selected count
   visible alongside the smaller count with usable flow. Preserve flat, zero,
   negative and noisy scale-flow readings as quality disclosures, not silent
   exclusions based on agreement. No resmoothing, time shift or flow correction
   may be selected by how well it reveals a peak.

Keep that strict non-increasing rule as the primary selection. Add a fixed
secondary view: a run continues through upward pressure reversals no larger
than the channel's resolution, defined as the smallest positive absolute
successive difference in achieved pressure. Compute this resolution per record
from pressure samples only, before any flow or weight value is opened. Use
successive pairs on valid native support; if no positive absolute difference
exists, the resolution is undefined and a 9-to-5 sweep is unsupported. Retain
all other selection and reporting rules. Report both funnels side by side.
The secondary view is a sensitivity check on the selection rule, not a
replacement, and must not be tuned after seeing counts or flows. This empirical
pressure-step definition is not an independent hardware-resolution calibration.

Report a count funnel: canonical local records, authenticated DE1, required
channels, pressure-spanning candidates, monotone runs, active-brew versus
state-unknown sweeps, and usable scale-flow support. Give median [IQR] and range
of 9-to-5 sweep duration, cadence and largest native sampling gap, separately
by those status groups. These are descriptive summaries, not confidence
intervals. Exact monotonicity can exclude physically falling but noisy traces;
report pressure-spanning versus monotone counts, and do not loosen the rule
after seeing the count or flows. A scan that cannot authenticate DE1 stops at
that count and reports provenance unresolved, without promoting unknown-device
records to a DE1 result.

**Interpretation rule X1.3**

X1.3: The path slope on a falling-pressure sweep is
dq/dP = R*C'(P) + C*R'(M)*q/Pdot, and the memory term is negative. The test
is therefore one-sided. Positive path slope below 6 bar (flow falling as
pressure falls) means the capacity term exceeds the memory term there; it is
the informative sign consistent with an interior capacity peak. Positive path
slope above 6 bar conflicts with a falling capacity there under monotone-
increasing memory. Negative path slope below 6 bar is unresolved, because
memory or an evolving puck can produce it; it is not evidence against a
peak. Report mixed, flat, noisy or sparse patterns as unresolved, with no
pass quota or fitted peak location. These are fixed-state-curve statements,
not causal inference from one evolving shot.

Use adjacent native-sample secants `Delta q/Delta P` as finite-resolution
estimates of the instantaneous path slope. Label their support by pressure;
assign an interval above or below 6 bar only when both endpoints lie on that
side. Pressure plateaus have undefined dq/dP, and a single jump spanning both
sides cannot resolve the reversal. Report sign counts and their actual support,
plus whole-side secants across 9-to-6 and 6-to-5 as coarse summaries when
supported. An isolated noisy sign change is not evidence of an interior peak.
This is scoping for a future test, not an A/LC prediction or fit.

The confounds are explicit: machine versus puck pressure, pressure calibration
and control response, scale differentiation/filtering and lag, cup transit and
retention, changing saturation/temperature/permeability, compaction or channeling,
and unknown coffee, grind, dose, basket, preparation, session and upload selection.
Even the unchanged memory model shows the problem:

\[
\left.\frac{dq}{dP}\right|_{\rm path}
=R(M)C'(P)+C(P)R'(M)\frac{q}{\dot P}.
\]

For falling pressure and increasing R, the second term is negative. It can mask
the positive capacity slope below the peak. Neither matching nor conflicting
path signs establish or reject a universal capacity law; no memory correction
or external A/LC parameter estimation is authorized here.

Credit every eventual Visualizer output: **Data source: Visualizer; thanks to
the contributing users who made their shots public.** The permission is to use
the existing public records, not redistribute raw shots. Keep raw arrays,
identifiers, user hashes and private selected-shot manifests outside Git; publish
only permitted aggregate scoping summaries. Do not contact contributors or send
results externally without a separate instruction.

## Delivery and status

This PR contains PLAN.md only. After owner approval, the intended report is one
concise X1 SUMMARY.md, with small aggregate tables as needed for the magnitude
bound and count funnel; no new schema, receipts or governance machinery. Every
numeric output will retain its source/input role and the rules above. Checks
should cover units, domains, unchanged-source reuse and pressure-only selection;
no historical fits are rerun. A blocker stops the affected execution for owner
review rather than changing sources, assumptions or selection rules to obtain
a preferred result. No successor or C3e full-stage work is authorized by X1.

Leave status bookkeeping unchanged: `pressure-peak-flow-turnover` is active,
`verified_commit=null`, and its current next_gate is **C3e screen awaits owner
review**. That gate belongs to the separate C3e/full-stage track; X1 does not
replace or broaden it. No statusdoc regeneration is needed without an input
change. Push the plan without force, open a draft PR with auto-merge off, report
the base/branch/commit/PR and PLAN.md SHA-256, then stop for owner review.
