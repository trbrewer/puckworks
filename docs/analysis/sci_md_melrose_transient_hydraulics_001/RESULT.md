# SCI-MD-MELROSE-TRANSIENT-HYDRAULICS-001

**Resolved declines in partial Figure 2 readings; physical interpretation remains
conditional.** Eight of twelve temporally informative recovered profiles/fragments
exclude nondecreasing ordinates under the declared reading bounds. Three HF
profiles have a resolved decline followed by recovery through the same observed
trough. These results concern published collected-volume interval averages,
not reconstructed instantaneous flow, physical-brew trends or cross-pressure
reversal. **PHYSICAL_VALIDATION=NOT_ESTABLISHED.**

G1 / NO_GOVERNING_PHYSICS_CHANGE; RESEARCH_ONLY / RETROSPECTIVE /
TARGET_EXPOSED / SOURCE_INTERNAL. Neither a protected holdout nor a predictive
model score. The [plan](PLAN.md) was frozen after source inspection and before
coordinate transcription/new compatibility calculations. The qualitative pattern
was already exposed.

## Coverage and finite results

The intended 16 slots yield 57 retained markers in 14 observed profile fragments:
10 condition-assigned profiles plus 4 LF triangular fragments with unresolved
B400LF/B480LF mapping. At least12 distinct traces are distinguishable (7 HF, 5 LF);
the total number of represented curves and obscured points is unresolved.
The triangular early/late fragments are not joined through hidden crossings or
counted as four independent curves. Ten conditions are confirmed represented by
assigned visible markers; none is claimed completely recovered. B480HF,
D400LF, D480LF and E400LF have no separately identifiable assigned markers in
this recovery; this is not proof of source absence. No sixteenth curve was built.
Physically qualified profiles: **0** under the complete hydraulic/aggregation
contract. This does not erase resolved changes in displayed profiles.

There are 121 supported strict ordered pairs and 162 supported three-point chains.
Two singletons are reported separately. Among 12 informative fragments,
nondecreasing is excluded 8/not-excluded 4; nonincreasing excluded 6/not-excluded 6;
constant excluded 11/not-excluded 1. Including singletons, the corresponding
not-excluded counts are 6/8/3; their vacuous compatibility is not trend evidence.
All feasibility language below means **not excluded by the rectangular outer
relaxation**. Jointly admissible monotone witnesses were not tested.

| Profile (condition where known) | Markers | Up / down / constant | D_up | D_down | δ_up / δ_down / δ_constant |
|---|---:|---|---:|---:|---|
| HF-B400 (B400HF) | 6 | compatible / excluded / excluded | 0 | 1.016327 | 0 / .508163 / .508163 |
| HF-C400 (C400HF) | 7 | excluded / excluded / excluded | 1.016327 | 1.261224 | .508163 / .630612 / .630612 |
| HF-C480 (C480HF) | 7 | excluded / excluded / excluded | .391837 | 1.910204 | .195918 / .955102 / .955102 |
| HF-D400 (D400HF) | 3 | excluded / compatible / excluded | .930612 | 0 | .465306 / 0 / .465306 |
| HF-D480 (D480HF) | 6 | excluded / excluded / excluded | 1.151020 | 1.310204 | .575510 / .655102 / .655102 |
| HF-E400 (E400HF) | 5 | excluded / compatible / excluded | 1.151020 | 0 | .575510 / 0 / .575510 |
| HF-E480 (E480HF) | 6 | excluded / compatible / excluded | 2.302041 | 0 | 1.151020 / 0 / 1.151020 |
| LF-C400 (C400LF) | 1 | singleton: all compatible | 0 | 0 | 0 / 0 / 0 |
| LF-C480 (C480LF) | 3 | compatible / excluded / excluded | 0 | .232653 | 0 / .116327 / .116327 |
| LF-E480 (E480LF) | 6 | excluded / compatible / excluded | .918367 | 0 | .459184 / 0 / .459184 |
| LF-triangle-early-upper | 1 | singleton: all compatible | 0 | 0 | 0 / 0 / 0 |
| LF-triangle-early-lower | 2 | excluded / compatible / excluded | .036735 | 0 | .018367 / 0 / .018367 |
| LF-triangle-late-upper | 2 | compatible / excluded / excluded | 0 | .012245 | 0 / .006122 / .006122 |
| LF-triangle-late-lower | 2 | compatible / compatible / compatible | 0 | 0 | 0 / 0 / 0 |

All magnitudes are mL/s; multiply by 1e-6 for m3/s. Values above are rounded
only for display. Decisions, endpoint witnesses, all attaining point IDs,
expansion witnesses and joint/rectangular distinctions are in [RESULT.json](RESULT.json).
The tiny late-upper triangular increase is one native-pixel residual gap under
this explicit enclosure; it is strongly reading-contract dependent and is not
experimental significance. The early-lower triangular decline is also small.
Neither fragment is assigned a packing density.

The largest decline witness is HF-E480-x122 → HF-E480-x368 (near 5→35 s):
5.277551020408163 lower minus 2.975510204081633 upper =
**2.3020408163265302 mL/s**. The largest increase witness is
HF-C480-x204 → HF-C480-x368 (near 15→35 s):
4.689795918367347 lower minus 2.779591836734694 upper =
**1.9102040816326529 mL/s**. These are enclosure gaps, not central-value changes.

Qualifying same-trough examples (IDs use native x pixels, not exact times):

| Profile | Earlier → trough → later | Decline / recovery margin (mL/s) | All qualifying triples |
|---|---|---|---:|
| HF-C400 | x122 → x245 → x368 | 1.0163265306122446 / 1.2612244897959184 | 14 |
| HF-C480 | x122 → x204 → x368 | .39183673469387736 / 1.9102040816326529 | 11 |
| HF-D480 | x122 → x204 → x368 | 1.151020408163265 / 1.3102040816326532 | 8 |

The 33 triples reuse observations; they are not 33 independent events. They do
not establish a unique minimum, a globally U-shaped curve, monotonic intervening
segments or a continuous-time turning point. No LF decline-then-recovery triple
survives the current partial recovery/bounds; that does not establish absence.

## Observation and source limits

The [source reconciliation](SOURCE_RECONCILIATION.md) separates the authors'
qualitative description from the recovered inequalities. The native 957×678 JPEG
has no series-name legend. Figure 1 extends its shape/fill convention to later
figures, but Figure 2's two open-looking LF triangle traces do not uniquely
resolve density. Dense LF overlaps and some HF markers remain unresolved;
[the region ledger](../../../puckworks/data/melrose2019bed/ambiguous_regions.csv)
records unknown counts instead of manufacturing points. The thesis's15-condition
table lacks B480HF, which does not prove later-preprint absence.

The preprint directly describes aliquot volume divided by collection duration
and first-drop t=0. Thesis methods support weighed aliquots, approximate water
density and 5/10 s HF/LF durations in this campaign. Exact Figure 2 interval
endpoints and plotted end/midpoint convention are unreported. No cumulative
volume is reconstructed. The reported 1–3% density-approximation error is kept
separate from figure-reading uncertainty.

Figure 1 states 3–4 repetitions and sample SD; thesis general statistical treatment
also refers to repeated samples. Neither establishes Figure 2's pointwise
membership, weights or exact aggregation operation. Thus these are unspecified
published aggregates, not reconstructed individual runs or proven fixed-weight
means. Changing members or weights can decline even if every run increases.

Pressure constancy, numerical pressure value and node identity are separate:
the preprint reports LF/HF applied overpressures1.75/3.75 bar; the thesis selects
tank pressures by grind/density. The regulated tank, pre-cell transducer and
corrected bed drop are different quantities. The conflict is retained and no
numerical pressure adapter is applied. Nominal LF/HF average flow is not imposed
constant flow. Thesis Figure 7.1 is methodological support, not a pointwise join
or second scored dataset.

The maximum-decline witnesses begin near 5 s (HF) or 10 s (LF), touching the
reported early thermal-transient region: outlet~60°C rising to75–80°C after 5–10 s.
Unknown interval endpoints prevent sharper assignment. Later outlet temperature
does not establish constant bed temperature, viscosity or fluid properties.
Thesis p.274 explicitly reports early inlet/outlet disagreement from circuit
filling and absorption. No negligible-storage/collection correction is proved.

## Exact finite mathematics and uncertainty scope

For a finite partial order, a nondecreasing witness is the maximum of lower
bounds over each point's predecessors (including itself). Necessity follows from
l_i≤q_i≤q_j≤u_j for comparable i≤j; sufficiency follows because predecessor sets
are nested under order and their maxima satisfy every upper bound. Reversing the
order gives the successor-lower-maximum nonincreasing witness. A constant exists
exactly when the intersection [max l,min u] is nonempty. Equality is compatible.
The implementation rejects invalid intervals, centers, IDs and cyclic orders.

Expanding each interval symmetrically byδ changes every violating pair gap
l_i−u_j to l_i−u_j−2δ. Thus δ_up=D_up/2 and δ_down=D_down/2 are necessary
and sufficient. The same intersection argument gives
δ_constant=max(0,max l−min u)/2. Witness constructions at these expansions
prove sufficiency, including partial orders. A separately formulated epigraph LP
minimizesδ with q_i bounded by expanded intervals and order constraints; focused
tests agree for synthetic cases and all 14 recovered fragments. The transitive
regression [2,3],[0,3],[0,1] detects the nonadjacent1-before3 contradiction.

The pointwise rectangles contain all readings allowed by the retained glyphs and
shared affine calibration. Rectangular infeasibility therefore excludes every
contained joint reading. Feasibility only says this relaxation did not exclude
the hypothesis; the reported witness may use mutually inconsistent calibration
extremes. Delta is exact for uniform independent rectangular expansion, not
necessarily for a shared calibration adjustment or physical error model. It is
not a sensor-error estimate, confidence interval, probability or error budget.

## Conditional hydraulic implication

Reuse only EWP #213's within-trajectory theorem: fixed topology, quasi-static
positive **linear** resistive edges with every g_e nondecreasing. For fixed
constitutive factors, slit g_e=w_e a_e³/(12μl_e) increases with aperture.
At unit terminal pressure difference,
K(g)=min_v Σ_e g_e(Δv_e)². Increasing every coefficient increases the energy
at every admissible trial potential, hence cannot decrease its minimum.
At fixed positive bed pressure P, Q=KP is nondecreasing. Passivity by itself
does not establish this result. Fixed geometry factors/fluid properties and
negligible storage/inertial transients are required. Opening may change pore
volume; equality of inlet, outlet and collected flow requires an observer
mapping or the appropriate negligible-storage limit. No general nonlinear or
dynamic network claim is made.

A separate constant-applied-head extension is conditional: with a common
pressure reference/outlet, fixed L, K>0, Q≥0 and a time-invariant, memoryless,
nondecreasing loss h, Q/K+h(Q)=L. For K2≥K1, the left side at a fixed Q falls
or stays equal. It is strictly increasing in Q because Q/K is strictly increasing;
therefore, when the stated solutions exist, Q2≥Q1. This does not establish that
the experimental apparatus obeyed this mapping throughout these intervals.
EWP's numerical adapter and mass-flow units were not imported. EWP #213 remains
**UNRESOLVED_BOUNDED_ANALYSIS**, line-pressure applicability **NOT_ASSESSED**.

For integrable nondecreasing Q and successive positive-duration nonoverlapping
intervals I before J, Q(s)≤Q(t) for every s∈I,t∈J (up to irrelevant endpoint
conventions). Integrating over I×J and dividing by |I||J| gives mean_I Q≤mean_J Q,
even for unequal durations. Fixed nonnegative replicate weights preserve this
inequality term by term; for a mean their sum is one. The same replicate members
and weights must apply at every compared position. A ratio of summed volumes
to summed durations instead weights each rate by its duration share; changing
shares need an additional applicability check.

Supported premises: interval-rate quantity, chronological displayed order,
campaign aliquot method and regulated applied-head description. Unqualified
premises: exact aggregation, per-profile pressure mapping, fixed constitutive
factors, time-invariant apparatus losses and negligible storage/inertia/collection
effects. A blanket early inlet=outlet assertion is contradicted by the thesis;
a blanket whole-run isothermal assertion is contradicted by the reported thermal
transient. These are not blanket disproofs of later, appropriately scoped limits.

A resolved decline contradicts the **conjunction** of the scoped hydraulic and
eligible-observer/aggregation assumptions. It does not identify which fails or
select compaction, fines, gas, viscosity, storage or collection effects as a cause.
Future models intended to reproduce these published profiles must accommodate
the resolved declines/recoveries through their hydraulics **or** a supported
observation/aggregation mapping. Failure to exclude monotonicity does not validate
opening-only physics. No intrinsic permeability, cross-pressure reversal,
Waszkiewicz high-pressure explanation, rejection of all opening/erosion models,
independent campaign replication or runtime adoption follows.

## Reproduction and evidence identities

```bash
python -m puckworks.analysis.melrose2019bed_transient --output /tmp/melrose-reproduction
pytest -q tests/test_melrose2019bed_transient.py
```

Compare the four generated files with this directory's RESULT.json,
profile_results.csv, condition_results.csv and
`puckworks/data/melrose2019bed/observations.csv`. All tests use committed data;
source downloads are unnecessary. Source coordinates, calibration/observer
contract, profile mapping and ambiguity ledger live in that dataset directory.
Source PDFs, extracted images, overlays and full logs remain external to Git.

Implementation base: `58075bbbce548e63d94106c96b918c1464221514`, identical to
reviewed main at intake. Source hashes and input hashes are in RESULT.json.
[Independent scientific review](REVIEW.md) binds the reviewed scientific candidate;
[verification](VERIFICATION.md) records software QA separately. Hosted required
CI and final checked head are reported on the single draft PR. No merge,
auto-merge, EWP edit, production change or automatic successor is authorized.
