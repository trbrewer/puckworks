# Bounded-assay delivery envelopes

MODEL-ENG-ASSAY-ENVELOPE-001 — G0 / NO_GOVERNING_PHYSICS_CHANGE / RESEARCH_ONLY.

This API bounds the minimum and maximum interval solute over a caller-supplied
closed assay box for one unchanged C0, C1 or C2 model. It optimizes the query
inputs, never fits a model. The forward and stopping APIs, model coefficients,
feature transforms, knots, domains and historical evidence remain unchanged.

```python
from puckworks.analysis.conditional_tail_delivery import Model
from puckworks.analysis.conditional_tail_envelope import (
    AssayBox, EnvelopeQuery, bound_interval_delivery, bound_remaining_solute,
)

model = Model.load("docs/analysis/sci_md_mass_delivery_006/models/C2.json")
m1, m2, q1, q2 = model.means
box = AssayBox("C2", m1, m2, q1=(q1, q1),
               q2=(0.0931364597, 0.1830244866), input_class="SYNTHETIC")
result = bound_remaining_solute(model, box, 0.04104270828628944)
partial = bound_interval_delivery(model, box, EnvelopeQuery(0.02, 0.03))
payload = result.to_json()
```

These are synthetic queries of a saved model, not observed shots or inferred
instrument tolerances. Different queries can have different extremizing inputs;
their separate extrema need not be jointly attainable by one shot.

## Input and result contract

Masses and solute are kg. Assays `q1` and `q2` are kg solute/kg beverage.
Average TDS is explicitly `100 * solute_kg / interval_width_kg`, mass percent.
The cumulative beverage coordinate retains its original collection origin.
Exact positive finite early masses define `anchor = m1_kg + m2_kg`; require
`anchor <= start_kg <= end_kg <= model.domain_kg`. Remaining solute uses the
same calculation with `start_kg = anchor`. No future chemistry is accepted.

C0 accepts no assays; C1 requires only q1; C2 requires q1 and q2. Each interval
is finite, ordered, closed and contained in [0,1]. Collapsed intervals are valid.
No input is clipped or widened. Booleans, strings as numbers, unknown fields,
duplicate JSON keys, wrong units/basis and invalid domains are rejected.
JSON input requires explicit units, basis and input classification.

The Cartesian product describes possible deterministic inputs. It is neither
a probability distribution nor an assertion of statistical independence.
Correlated or nonrectangular sets and uncertainties in masses, coordinates,
coefficients or model identity are outside this interface.

Immutable results report separate intervals for the minimum and maximum,
feasible common-input witnesses with unchanged parent predictions, the overall
delivery interval and positive-width TDS equivalents. They retain identities,
input classification, units, rights, limitations, whole-box marginal feature
extrapolation, numerical allowances, both optimization gaps, resource counts
and termination reason. Being inside every marginal training range does not
establish joint experimental support.

The overall delivery interval is `[minimum.lower_kg, maximum.upper_kg]`.
An extremum gap includes its numerical allowances; it is not just a distance
between approximate optimizer values. `ENVELOPE_QUALIFIED` requires both gaps
to meet the requested absolute resolution and every load-bearing numerical
check to pass. Otherwise the result is `NUMERICALLY_UNRESOLVED`, even if its
outer interval is finite. Failed evaluations cannot establish qualification.

Zero-width delivery is exactly zero with null TDS. C0 and fully collapsed
boxes reduce to one parent prediction and its unchanged allowance, without
additional modeled variability. The default gap resolution is `1e-7 kg`
(0.1 mg); it is not assay accuracy, predictive accuracy or an espresso-quality
threshold. Tighter requested resolution does not change the hard ceilings of
4096 subdivisions and 16384 parent point evaluations per query. Smaller
explicit resource limits are supported. Budgets never expand automatically.

For a lower delivery requirement `S >= T`, a qualified minimum lower bound at
least T establishes satisfaction throughout the supplied set, conditional on
the model. A feasible witness whose prediction plus allowance is below T
contradicts it. Otherwise it remains unresolved at this resolution. Reverse
the inequalities and use the maximum for `S <= T`. Pointwise envelope curves
are bounding constructions, not attainable trajectories.

## Exact-arithmetic construction

With the unchanged hats H_k, feature means mu and scales s,

```
alpha(b) = sum_k H_k(b) * (theta[k,0]
           + theta[k,1]*(m1-mu1)/s1 + theta[k,2]*(m2-mu2)/s2
           - sum_j theta[k,j+3]*mu[j+2]/s[j+2])
beta_j(b) = sum_k H_k(b) * theta[k,j+3]/s[j+2]
eta(b,q) = alpha(b) + sum_j beta_j(b)*q_j
S(q;u,v) = integral_u^v sigmoid(eta(b,q)) db
```

Equivalently, center the affine assay dependence at a parent-conditioned state.
The implementation reuses the parent's immutable model/input/state objects,
authoritative point observer and stable scalar sigmoid-affine integration
kernel. It does not implement another forward predictor.

For a sub-box Q, minimize and maximize each affine assay term at its permitted
endpoint. Monotonicity of sigmoid then encloses every concentration, and
integration encloses every common-input S(q). Split at original knots, query
endpoints and coefficient-sign crossings. These integrated pointwise envelopes
are outer bounds, not necessarily achieved by any one q.

There is also a useful protection against rounded sign-crossing coordinates:
within an original mass segment, the minimum of affine functions is concave,
so its endpoint chord lies below it; the maximum is convex and its chord lies
above it. Integrating those chords through monotone sigmoid stays conservative
even if a sign crossing is rounded or omitted. Original knots must still be
retained. Independent quadrature/refinement qualifies the added breakpoints
and arithmetic rather than inheriting the parent's five-knot allowance.

A centered Taylor bound tightens boxes near interior extrema. With center c,
radii r_j and `g_j = integral sigmoid'(eta(b,c))*beta_j(b) db`, use

```
D = sum_j abs(g_j)*r_j
B = sum_j max_b(abs(beta_j(b)))*r_j
R = (v-u)*B**2/8
S(c)-D-R <= S(q) <= S(c)+D+R
```

Taylor's theorem and `abs(sigmoid''(eta)) <= 1/4` prove the remainder bound
uniformly along every segment from c to q. Intersect this bound with the
integrated pointwise bound. The center prediction comes from the parent;
gradient integration has its own adaptive/refinement allowance. This is still
optimization over a fixed model and a deterministic possible-input set.

Branch-and-bound keeps a complete partition of the original box. For each
leaf i let `[L_i,U_i]` enclose every delivery there. Feasible witnesses give
the minimum an upper bound and the maximum a lower bound. Thus

```
min_i L_i <= min_Q S <= min_w (S(w)+allowance(w))
max_w (S(w)-allowance(w)) <= max_Q S <= max_i U_i
```

Subdivision prioritizes the largest unresolved contribution to either gap,
breaking ties by creation order. Within that box it bisects the coordinate
with largest width times maximum absolute beta (q1 first on ties). Splitting
never removes an unresolved region. Children inherit their parent's bounds;
partition replacement occurs only after both children succeed. Attempted
subdivisions count even when a child hits a limit or fails. Root
corners and subsequent sub-box centers are feasible witnesses only; neither
corners, a grid nor local optimization supplies the global guarantee.

## Floating-point qualification

The argument above is exact-arithmetic mathematics. Computed enclosures are
engineering enclosures under explicitly reported numerical allowances, not
certificates from a rigorous interval-arithmetic library. Independent adaptive
quadrature is a numerical reference, not proof of rigorous rounding control.

Every witness retains the parent's `1e-9 kg` allowance ceiling. Envelope
integration compares the stable kernel with adaptive quadrature and a second
run bisecting each piece, retaining discrepancies and quadrature error estimates.
Gradient references are likewise refined. Additional arithmetic allowances
cover feature conditioning, affine interpolation, signs/cuts, products,
summation and bound comparisons; sigmoid's `1/4` Lipschitz constant converts
logit uncertainty to solute uncertainty. Specifically, let epsilon be machine
epsilon, W the query width and
`M = max_k(abs(theta[k,0]) + sum_r abs(theta[k,r+1]) *
(max(abs(input_lower_r),abs(input_upper_r))+abs(mu_r))/s_r)`.
The arithmetic allowance is
`512*epsilon*(abs(u)+abs(v)+W*(1+M))`; Taylor arithmetic additionally allows
`512*epsilon*(D+R)`. Each gradient integral's quadrature/refinement allowance
is augmented by `512*epsilon*W*max(abs(beta_j))*(1+M)` and multiplied by r_j
before entering the Taylor bounds. Result fields report maxima over attempted
successful evaluations, separately for parent, envelope integration, arithmetic
(including Taylor arithmetic) and weighted gradient effects. These conservative
engineering allowances are not inferred measurement errors. Bounds and gap calculations round
outward, and the physical range `[0, v-u]` is available as a conservative
fallback. Numerical failures retain this fallback and qualified witnesses,
record failure counts, and return unresolved.

Resource exhaustion, unrepresentable assay splits and requests below the
numerical allowance floor remain unresolved. No convenient box is discarded
and no requested tolerance is silently relaxed. See [verification](VERIFICATION.md)
for analytical proofs, independently recomputed references and actual limits.

## Reproduction and privacy

The source-free demonstration requires no saved model or private data:

```bash
python -m puckworks.analysis.conditional_tail_envelope --synthetic
```

Saved mode accepts a strict model JSON, box JSON and coordinate query JSON:

```bash
python -m puckworks.analysis.conditional_tail_envelope \
  --model docs/analysis/sci_md_mass_delivery_006/models/C2.json \
  --box /private/box.json --query /private/query.json --output /private/result.json
```

Use caller-controlled paths outside Git for the box, query and output. Saved
mode is quiet, sanitizes errors and creates output exclusively. It never prints
private values, overwrites an existing result or commits input/output archives.
`box.to_dict()` and `query.to_dict()` provide the complete serialized schemas.

## Scope and rights

No new fits, empirical outcome joins/scores or native EWP runs occur. No source
acquisition, assay validation, calibrated uncertainty model, model ranking,
robust inverse stopping search, production adoption or successor is authorized.
Pannusch `experimental_kinetics` and Schmieder `raw_fractions` share one physical
lineage; these synthetic queries add no experimental samples or independent
evidence. Their frozen source-derived models and results retain CC-BY-NC-3.0
attribution: Pannusch/Schmieder, Mendeley 10.17632/y2tz67f6ry.1. That restriction
is separate from first-party code licensing.

G0 data-availability preflight: NOT_APPLICABLE to original observations; public
saved models and manufactured inputs supply all references. Corpus guide
metadata were inspected; original/private observations were not inspected for
this task. No absence, exhaustion or laboratory recommendation is made.

The new information is a previously unavailable numerical query. Qualified
output supports bounded model-conditional threshold decisions; mandatory
failure retains a partial capability without weakened criteria. This advances
conditional delivered-solute use without revisiting empirical adequacy or the
programme's missing-measurement blockers. The lower-cost route is the existing
small Python model; no physics, CFD or new experiment is involved.

PHYSICAL_VALIDATION = NOT_ESTABLISHED. RESEARCH_ONLY.
CONDITIONAL_ON_THE_UNCHANGED_MODEL_AND_CALLER_SUPPLIED_ASSAY_SET.
