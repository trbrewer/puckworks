# Continuous assay-robust stopping enclosures

MODEL-ENG-ROBUST-MASS-STOP-001 — G0 / NO_GOVERNING_PHYSICS_CHANGE / RESEARCH_ONLY.

`solve_robust_stopping_ranges(model, box, query, *, options=...)` encloses **all**
stopping masses for which **every** early-assay input in the supplied closed
Cartesian box satisfies **every** supplied suffix constraint. It returns qualified
feasible, qualified excluded and explicitly unresolved regions over the continuous
requested domain. No preferred mass, arm, recipe or controller is selected.

```python
from puckworks.analysis.conditional_tail_delivery import Model
from puckworks.analysis.conditional_tail_envelope import AssayBox
from puckworks.analysis.conditional_tail_stopping import StoppingQuery
from puckworks.analysis.conditional_tail_robust_stopping import (
    RobustStoppingOptions, solve_robust_stopping_ranges,
)

model = Model.load("docs/analysis/sci_md_mass_delivery_006/models/C2.json")
m1, m2, q1, _ = model.means
box = AssayBox("C2", m1, m2, q1=(q1, q1),
               q2=(0.0931364597, 0.1830244866), input_class="SYNTHETIC")
query = StoppingQuery(box.anchor_kg, model.domain_kg, solute_min_kg=0.001640)
result = solve_robust_stopping_ranges(model, box, query)
```

This is a synthetic possible-input set for the saved model, not an assay-error
calibration or an additional experiment. Source-derived results retain the model's
rights. See [actual verification](VERIFICATION.md).

## Contracts and interpretation

The unchanged public `Model`, `AssayBox` and `StoppingQuery` contracts apply.
Only active assay coordinates vary: none for C0, q1 for C1, q1/q2 for C2.
The early masses are exact as supplied. No coefficient, early-mass, origin,
transform, model-structure or instrument uncertainty is introduced.

With `a = m1_kg + m2_kg`, define

```
F(b,q) = integral_a^b c(u,q) du
solute_min_kg <= F(b,q) <= solute_max_kg
suffix_tds_min_percent <= 100*F(b,q)/(b-a) <= suffix_tds_max_percent
```

Omitted constraints impose no restriction; the inherited query requires at least
one. Limits are inclusive. Beverage/solute are kg, assays kg/kg, TDS mass percent,
basis MASS, coordinates measured from the original collection origin. These are
SUFFIX quantities, including modeled gaps, not measured whole-cup totals.
Require `a <= stop_min_kg <= stop_max_kg <= model.domain_kg`; TDS additionally
requires `stop_min_kg > a`. Anchor-only solute queries and zero-width requested
mass domains are valid. Nonnegative unattainable targets are valid queries.
The inherited input contract requires positive early masses, assay endpoints in
`[0,1]` and TDS limits in `[0,100]`; solute targets need not be attainable within
the suffix domain. Numeric fields require finite real values, not booleans.
Reversed/nonfinite inputs, inactive assay fields, wrong units and domain violations
are rejected. Whole-box marginal extrapolation is reported, never clipped.

The Cartesian set is deterministic: it is neither a probability distribution,
statistical independence assertion, confidence region, instrument specification
nor proof of joint experimental support. The same q applies throughout each
forward integral. Different masses and constraints may have different extrema:
universal quantification distributes across conjunction. Independent witnesses
are never combined into an existential jointly feasible trajectory.

All public records are frozen, with tuples and immutable nested records.
`to_dict()` returns fresh JSON containers; `to_json()` uses strict finite JSON.
Results carry model/box/query/options SHA256 identities, embedded box/query/options,
training identity, anchor/domain, units, rights, claims, allowances and actual
cumulative resource counts. Caller inputs/results should be treated as private.

## Sets, endpoints and resolution

Each `MassRegion` has `lower_kg`, `upper_kg`, `lower_included`, `upper_included`
and a tuple of `reasons`. Inclusion flags describe membership in that **reported
set**, not certainty that an unresolved endpoint is feasible. Feasible, excluded
and unresolved regions form a disjoint complete partition, including endpoint
points. All three sets are normalized; unresolved neighborhoods touching across
a partition boundary are coalesced before measuring their extent.

Under the numerical allowances:

```
union(feasible_regions) subset true robust set
true robust set subset union(outer_possible_feasible_regions)
union(excluded_regions) intersect true robust set = empty
outer_possible_feasible_regions = union(feasible_regions, unresolved_regions)
```

- `ROBUST_STOPPING_ENCLOSED`: classified regions plus boundary uncertainty whose
  coalesced widths meet the requested resolution; no numerical/resource failure.
- `NO_ROBUST_FEASIBLE_RANGE`: the **complete requested domain** is excluded and
  the outer possible-feasible set is empty.
- `NUMERICALLY_UNRESOLVED`: a numerical/resource/pathological ambiguity remains;
  all earlier qualified pieces and the complete remainder are retained.

`resolution_qualified` and `achieved_unresolved_neighborhood_kg` report the actual
coalesced maximum extent, separately from requested resolution and status.
A narrow unresolved region does not prove the number of components inside it.
Feasible pieces are never joined across an unresolved gap. Separate finite-resolution
answers to nested queries need not have literally nested inner/outer endpoints;
the underlying mathematical robust sets obey box-widening/constraint-tightening
nesting.

C0 and fully collapsed boxes delegate to the unchanged point inverse. The full
immutable `point_result` preserves its isolated roots, crossing brackets,
flat equalities, tangencies, partial components and unresolved reasons. Its
qualified open interiors and exact structural points enter the inner set;
nonzero root enclosures enter the unresolved set, and its remaining possible
support enters the outer set. A root enclosure is not a feasible interval.
Budget interruption of the point inverse retains the entire requested domain
as unresolved, since an interrupted enumeration supplies no complete partition.

## Exact-arithmetic enclosure argument

For a lower constraint use `g(b) = min_q F(b,q) - L`; for an upper constraint
use `g(b) = U - max_q F(b,q)`. For TDS fraction t, replace the target by
`t*(b-a)`. Robust feasibility is exactly `g(b) >= 0` for each supplied constraint.
The existing envelope API supplies enclosures of **both** extrema at a mass node.
Its witness upper bound on a minimum (or lower bound on a maximum) can prove
violation; a witness cannot establish universal satisfaction.

Suppose `c0 <= c(u,q) <= c1` uniformly on a mass cell and assay box. For
`F-t*(b-a)`, derivatives lie in `[c0-t,c1-t]`. For the opposite-sense residual
they lie in `[t-c1,t-c0]`. For node x and any b in `[l,h]`, let D contain all
products of a derivative endpoint with either `l-x` or `h-x`. If `[L,U]`
encloses the minimum constraint residual at x, then

```
L + min(D) <= g(b) <= U + max(D), for every b in [l,h].
```

Uniform derivative transport survives taking the assay minimum: its constants
do not depend on q. Include a cell only if every transported lower bound is
nonnegative. Exclude it only if at least one transported upper bound is strictly
negative. Otherwise subdivide or retain it unresolved. Global `0 <= c <= 1`
gives the 1-Lipschitz solute bound and `max(t,1-t)` TDS-residual bound.

The implementation tightens c0/c1 using the unchanged affine-logit representation.
On each original mass segment, the logit is affine in each assay and mass
separately. Its extrema over the product of a mass interval and assay box occur
at mass endpoints and assay corners. Retain original knots, apply the monotone
sigmoid to the enclosed logits, and take extrema across segments. This proves
**pointwise derivative bounds only**. Integrated extrema always come from the
existing envelope algorithm; corners are not an integral-extremum oracle.

Mass branch-and-bound starts with the whole requested interval, works on the
widest pending cell (lower mass breaks ties), and replaces a parent with two
children atomically. Children are left-closed/right-open, except the original
upper endpoint remains included. A bound over the closed cell also applies to
these half-open pieces. On failure, both the active cell and every pending cell
are retained. No grid, local optimizer or witness collection supplies coverage.

Anchor and finite-logit physical-range identities may classify trivial constraints
using exact rational comparisons of the supplied binary masses. Rounded sigmoid
zeros or ones never establish exact identities. Tiny concentrations, threshold
equalities without an algebraic identity and unresolved tangencies stay explicit.

## Floating-point qualification and accounting

The argument above is exact-arithmetic mathematics. Computed sets are engineering
enclosures under numerical allowances: **ALLOWANCE_BASED_NOT_INTERVAL_CERTIFIED**.
Independent adaptive quadrature is a verification reference, not a rigorous
interval-arithmetic library or an empirical uncertainty estimate.

Every load-bearing envelope must return `ENVELOPE_QUALIFIED`, with no failed
parent/bound evaluations. Its integration, feature/arithmetic and gradient
allowances are inherited and reported as cumulative maxima; the unchanged parent
forward ceiling is 1e-9 kg. Node extrema already include the envelope allowances.

Let epsilon be machine epsilon, and M the maximum over knot rows of
`abs(theta0) + sum(abs(theta_j)*(max(abs(input_lower_j),abs(input_upper_j))
+ abs(mean_j))/scale_j)`. The pointwise logit allowance is
`512*epsilon*(1+M)`; sigmoid endpoint evaluation adds `128*epsilon` in concentration
units. Residual transport additionally allows
`512*epsilon*(abs(x)+abs(a)+abs(target)+abs(extremum_lower)
+abs(extremum_upper)+(h-l)*(1+abs(t)))` kg, followed by outward `nextafter`.
Reported maxima distinguish these allowances. Point dispatch retains the parent's
own residual/bracket allowances in `point_result`.

The immutable options schema is exactly:

```json
{
  "mass_resolution_kg": 0.000001,
  "envelope_absolute_gap_kg": 0.0000001,
  "tighter_envelope_absolute_gap_kg": 0.000000001,
  "max_mass_subdivisions": 2048,
  "max_envelope_calls": 512,
  "max_parent_evaluations": 65536,
  "max_assay_subdivisions_per_call": 4096,
  "max_parent_evaluations_per_envelope": 16384
}
```

All resolutions must be finite/positive; tighter gap <= initial gap <= 1e-7 kg.
Integer budgets may be reduced to zero but not enlarged beyond these hard caps.
Collapsed-box delegation reserves a conservative bound on parent mass refinements
before calling the point inverse. For each distinct boundary function, there are
at most `1 + interior_knots` original pieces. Each intersecting segment whose
logits straddle the TDS target level can add at most one non-guard piece; solute
boundaries add none. Each piece permits at most `MAX_REFINEMENTS=128` frontier
steps. The sum must fit `max_mass_subdivisions`; otherwise the whole domain is
unresolved with `POINT_INVERSE_MASS_BUDGET_RESERVATION_UNAVAILABLE`, without a
delegated calculation. Zero-width queries need no refinement reservation.
The result reports `point_inverse_mass_refinements_reserved` separately from
actual new `mass_subdivisions`: the unchanged parent exposes its maximum
iterations, not the cumulative refinement count. Their sum stays within the cap.
This conservative dispatch can decline a complex collapsed query even if a
less conservative bound might fit; there is no automatic cap escalation.
The numerical mass convention of 1e-6 kg does **not** imply experimental,
assay or machine milligram accuracy. Ambiguous cells within eight requested mass
resolutions may repeat the envelope at the explicitly preauthorized tighter gap.
Subdivision stops at one quarter of the requested mass resolution, then coalesced
neighborhoods determine qualification; larger neighborhoods are never relabeled
qualified. Tolerances and caps never escalate automatically.

Per-query adapters subclass the public immutable Model/State contracts and delegate
all delivery calculations unchanged. An accounting guard runs **before** each
delivery, including point-inverse calls, attempted failures and tighter repeats.
Envelope calls receive `min(remaining_global_budget, per_call_cap)`; counts never
reset per cell. Repeated identical envelope queries are cached within one solve.
No global monkeypatch, shared query cache or fitting is used. If an unexpected
envelope API exception prevents return of its nested audit, parent delivery use
is still measured by the adapter, while `nested_accounting_complete=false`
explicitly marks unavailable subdivision/quadrature totals (reported totals then
cover completed audits only). Such a result cannot qualify. Normal parent failures
return complete nested accounting through the existing envelope result.

Execution uses one numerical worker. Set BLAS threads to one as below; the library
does not mutate process-wide thread settings. Parent delivery counts and envelope
adaptive-quadrature counts are distinct; parent-internal quadrature is already
part of each counted delivery and is not exposed as a separate parent API counter.

## CLI and exact saved schemas

```bash
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
python -m puckworks.analysis.conditional_tail_robust_stopping --synthetic
python -m puckworks.analysis.conditional_tail_robust_stopping \
  --model docs/analysis/sci_md_mass_delivery_006/models/C2.json \
  --box "$PRIVATE_BOX_JSON" --query "$PRIVATE_QUERY_JSON" \
  --output "$PRIVATE_OUTPUT_JSON"
```

Optional `--options "$PRIVATE_OPTIONS_JSON"` accepts **all and only** the option
fields shown above. Without it the explicit defaults apply. Saved model JSON is
the unchanged `Model.to_dict()` schema. Box JSON requires `arm`, `m1_kg`, `m2_kg`,
`input_class`, `mass_unit="kg"`, `concentration_unit="kg/kg"`, `basis="MASS"`
plus only the active `q1`/`q2` two-element closed intervals. `input_class` is
`SYNTHETIC`, `SUPPLIED_EARLY_ASSAYS` or `SOURCE_EARLY_INPUT`.

Query JSON requires `stop_min_kg`, `stop_max_kg`, `mass_unit="kg"`,
`solute_unit="kg"`, `tds_unit="percent"`, `basis="MASS"`; optional fields are
`solute_min_kg`, `solute_max_kg`, `suffix_tds_min_percent`,
`suffix_tds_max_percent`. Omitted or null constraints are inactive, with at least
one active. Unknown/duplicate keys and nonfinite values fail. `to_dict()` on the
corresponding records supplies complete schemas without manual transcription.

Caller boxes, queries, options and results must stay outside Git. Saved mode
prints neither supplied inputs nor results, sanitizes errors and creates output
exclusively with mode 0600; it never overwrites an existing path. The synthetic
stdout demonstration uses manufactured inputs and identifies them as SYNTHETIC.

## Scope, availability and rights

The already completed selection gate identified implementation category A: the
missing usable quantified inverse. Verified output enables bounded model-conditional
threshold decisions; failed soundness or unresolved mandatory numerics limit the
capability honestly. This advances mass-conditioned suffix model use without
reopening empirical adequacy or the programme's repeated missing-measurement blockers.
The lower-cost parent Python APIs are reused. No new selection/successor search
or laboratory recommendation is made.

Scoped data preflight: **NOT_APPLICABLE_TO_NEW_DATA_G0**. The source guide,
MANIFEST entries `pannusch2024/experimental_kinetics` and `schmieder2023/raw_fractions`,
available-data policies, existing leverage ledger and frozen parent card/models
were inspected. Raw workbooks/observations were not accessed for this task.
External unmounted evidence is not declared absent or exhausted. Fits=0, new
empirical joins/scores=0, native EWP runs=0; no new train/evaluation split.

Pannusch/Schmieder remain one physical lineage. Synthetic boxes are not additional
experiments or independent holdouts. Source-derived model/results retain
CC-BY-NC-3.0, Pannusch/Schmieder attribution, Mendeley 10.17632/y2tz67f6ry.1,
separately from first-party code licensing. Every predecessor scientific disposition
is preserved. Numerical robustness over a supplied box is not empirical predictive
robustness or physical validation.

RESEARCH_ONLY; SOURCE_INTERNAL / TARGET_EXPOSED where inherited;
CONDITIONAL_ON_THE_UNCHANGED_MODEL_AND_CALLER_SUPPLIED_ASSAY_SET;
DETERMINISTIC_SET_NOT_PROBABILITY_MODEL;
MARGINAL_RANGES_NOT_JOINT_EXPERIMENTAL_SUPPORT;
MODELED_GAPS_NOT_MEASURED_WHOLE_CUP; NO_REAL_TIME_ASSAY_CLAIM;
ALLOWANCE_BASED_NOT_INTERVAL_CERTIFIED; PHYSICAL_VALIDATION=NOT_ESTABLISHED.
Production adoption, merging, auto-merge, release, activation, default/lock changes,
EWP integration and successors are not authorized.
