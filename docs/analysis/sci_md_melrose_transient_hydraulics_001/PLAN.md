# SCI-MD-MELROSE-TRANSIENT-HYDRAULICS-001 plan

Frozen after source inspection, before coordinate transcription or new compatibility
calculations, 2026-10-21 UTC. G1 / NO_GOVERNING_PHYSICS_CHANGE;
RESEARCH_ONLY / RETROSPECTIVE / TARGET_EXPOSED / SOURCE_INTERNAL.
PHYSICAL_VALIDATION=NOT_ESTABLISHED. This is an exposed figure-reading task,
not a prospective experiment, protected holdout or predictive score.

Implementation base: 58075bbbce548e63d94106c96b918c1464221514, current main
at intake; no delta from the owner's reviewed PW revision. Isolated branch.
EWP aace2cc6b6c2a393d2dbfb0274104192ca6c7203 is read-only: accepted
SCI-MD-MO-SPATIAL-PRESSURE-FEASIBILITY-001 RESULT.md retains
UNRESOLVED_BOUNDED_ANALYSIS and line-pressure NOT_ASSESSED.

## Sources and population

Primary: Melrose/Corrochano/Bakalis preprint dated 26 September 2019,
29 PDF pages, SHA256 20b7990af4a9026b44d56a29b559ab0d02f4a094d5a3e171b8d1bb41ae58c6ed;
Figure 2, printed/PDF p.11; native embedded JPEG 957 x 678 (PDF image object 29).
Methods pp.3–5, 10–12 and Figure 1 caption p.10 inspected before this plan.
Supporting thesis: 359 pages, SHA256
f131d9893e2ac78ce0664d5528beac4be51a02cf1ae684e41920fbc6cadc8818;
printed 63–65/90/273–276, PDF 88–90/115/298–301 inspected.
Use the exact owner-held copies verified against these hashes. The public
ResearchGate PDF is browser-readable but direct curl returned 403. The thesis
public download was slow; verified held bytes avoid a version substitution.
Source URLs and reconciliation are retained separately. No manuscript/image
bytes enter Git; only compact factual readings and original analysis.

Primary population is ONLY displayed Figure 2 markers. The thesis authenticates
campaign methods; its curves, tables and fitted functions are not scored.
Configured inventory metadata plus actual relevant held tables were checked:
Corrochano table/fit-summary data are not the Figure 2 ordinate sequences.
No mapped machine-readable original for this figure was found. This is not a
corpus-exhaustion claim. Repository/PR searches for Melrose, the task ID and
fig2_flow_transient found no existing equivalent intake.

## Coverage and identity

Intended slots, not established runs or independent units:
B400LF B480LF C400LF C480LF D400LF D480LF E400LF E480LF;
B400HF B480HF C400HF C480HF D400HF D480HF E400HF E480HF.
Figure 1's convention: B triangle, C square, D diamond, E circle;
open=480, closed=400. Authenticate actual glyphs; do not infer a sixteenth
curve from the grid or infer absence solely from thesis Table 7.1 (15 entries,
no B480HF). Distinguish trace/profile IDs from condition IDs. Retain identity
candidate sets when fill/shape or trace linkage is ambiguous. Never count one
trace for multiple conditions. A visible marker with unresolved identity may
be retained once on an explicitly limited observed profile; disconnected
fragments must not be joined just because a preferred identity fits.

Recover every identifiable displayed marker, not representative envelopes.
Lines are not samples. No smoothing/interpolation, hidden centers, reconstructed
replicates, fitted flow functions or inferred missing samples. List obscured
regions separately with unknown marker counts when counts cannot be resolved.
For overlaps retain a defensible visible-marker enclosure or exclude with
reason. Discrete identity ambiguity is separate from ordinate uncertainty.

## Calibration and reading bounds

Coordinates are native JPEG pixels, x right, y down, origin top left (zero-based).
Linear axes: x=80 at 0 s, x=900 at 100 s; y=548 at 0 mL/s,
y=58 at 6 mL/s. Each shared anchor ranges +/-1 native pixel, covering
axis stroke/raster placement. Internal ticks check affine calibration.
For each retained glyph record a source rectangle containing its visible full
extent; expand by 1 native pixel for JPEG/raster boundary identification.
This deliberately uses the full glyph footprint, not subpixel center precision.
A central coordinate is recorded only if the center is identifiable; otherwise
retain bounds with null central values. Overlap bounds may use an explicit
cluster extent only where an actual marker's presence and profile are supported;
no hidden marker may be manufactured by extrapolating a line.

Transform rectangle endpoints at all shared calibration corners to get outer
pointwise time/flow enclosures. The shared affine parameters and native rectangles
remain available; the rectangular analysis relaxes their coupling. No arbitrary
percentage tolerance or experimental error is added. Thesis density approximation
(~water; reported 1–3% error depending on concentration) is recorded separately,
not converted to independent symmetric pointwise errors. Units: mL/s and
m^3/s (x1e-6); seconds; pressure only where qualified, bar x1e5 Pa.

## Order and observation contract

Analyze plotted interval-average ordinates, never instantaneous flow.
Display order is supported between separated x enclosures within a trace.
Methods also establish successive collected aliquots and volume/duration rates:
retain this support separately from exact time endpoints (not reported).
Do not label abscissae interval ends or midpoints solely from their values.
Thesis reports 5 s HF / 10 s LF; same-campaign linkage supports methods,
not exact profile-specific collection endpoints or pointwise replicate joins.
Use only supported directed order relations and their transitive closure;
uncertain x sorting does not create order, independently known collection order
is not erased by overlapping time bounds.

Aggregation categories: single run; fixed-weight mean; ratio of summed volumes
and durations; other specified operation; unspecified published aggregate.
Preprint Figure 1 mentions 3–4 repetitions and sample SD; thesis general
statistical conventions do not prove Figure 2 membership/weights. Unresolved
aggregation blocks an unconditional run-level hydraulic implication.

## Finite calculations and claims

Reject nonfinite/malformed intervals and centers outside bounds. For all
reflexive comparable pairs: nondecreasing iff l_i<=u_j, nonincreasing iff
l_j<=u_i. Constant iff max(l)<=min(u), without order. Construct witnesses
from predecessor lower maxima, successor lower maxima, and constant intersection.
Use strict supported pairs for D_up=max(0,l_i-u_j), D_down=max(0,l_j-u_i).
Report attaining endpoints/IDs/order support with deterministic ties.
Uniform symmetric rectangular expansion is exactly D/2; constant expansion
is max(0,max(l)-min(u))/2. Retain witnesses at expansion and independently
check representative identities by a separately formulated LP.

For decline followed by recovery require the SAME trough j in a supported
chain i<j<k with l_i>u_j and l_k>u_j. Report triples and both margins;
rejection of two global monotone hypotheses alone is insufficient.
Distinguish no-data/single-point/order-free from informative temporal results;
report actual comparable pairs/triples. Use unrounded values for decisions.
Rectangular infeasibility excludes every contained joint reading; feasibility
means only not excluded by this relaxation unless joint constraints are checked.
Delta is a mathematical discrepancy, not a sensor error, probability or CI.

Report authors' description, recovered profiles, observation/aggregation support,
conditional hydraulic implication, and physical validation separately. Prove
fixed-topology quasi-static positive linear network monotonicity under increasing
conductance; fixed bed pressure or the separately conditional constant applied
head plus time-invariant memoryless nondecreasing loss. Fixed constitutive
factors, negligible storage/inertia, collection mapping and fixed eligible
replicate weights are explicit premises, not consequences of nominal pressure.
A decline contradicts their conjunction only; no alternative mechanism selected.
No cross-pressure reversal, Waszkiewicz explanation, intrinsic permeability,
rejection of all erosion/opening models, independent replication, runtime port,
yield/parameter fitting, physical-validation upgrade or automatic successor.

One independent scientific reviewer will inspect the full candidate and every
load-bearing witness against source images; resolve material findings in this
same task and record actual timing/identity. Focused offline tests, ordinary
repository checks and active-ruleset CI follow. One draft PR, unmerged,
auto-merge disabled. Any necessary transcription correction gets a source-based
reason and effect; no outcome-driven bounds/inclusion changes.
