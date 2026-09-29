# Inverse stopping ranges for frozen conditional delivery

MODEL-ENG-MASS-STOP-001 — G0 / NO_GOVERNING_PHYSICS_CHANGE / RESEARCH_ONLY.

`solve_stopping_ranges(state, query)` enumerates the stopping masses compatible
with inclusive additional-solute and/or suffix-average-TDS bounds. It returns
every numerically qualified component, endpoint enclosures and any unresolved
regions. It selects neither an arm nor a preferred stop. The immutable C0/C1/C2
models, their conditioning contracts, and the forward runtime are unchanged.

```python
from puckworks.analysis.conditional_tail_delivery import EarlyInput, Model
from puckworks.analysis.conditional_tail_stopping import (
    StoppingQuery, solve_stopping_ranges,
)

model = Model.load("docs/analysis/sci_md_mass_delivery_006/models/C2.json")
state = model.condition(EarlyInput("C2", model.means, "SYNTHETIC"))
query = StoppingQuery(
    stop_min_kg=state.b_anchor + 0.001,
    stop_max_kg=model.domain_kg,
    solute_min_kg=0.001,
    suffix_tds_max_percent=8.0,
)
result = solve_stopping_ranges(state, query)
```

This is a synthetic feature-mean example using an existing fitted artifact.
Marginal feature ranges do not establish joint empirical support or accuracy.
The result carries the unchanged feature-extrapolation flags, model and state
identities, arm, input class, original query, units, source rights and claim limits.
`query` and all nested result records are frozen; `to_dict()` returns fresh JSON
containers. Load a saved state with the parent's strict `State.from_dict()`.

## Contract and interpretation

The anchor is `a = m1_kg + m2_kg`. Beverage mass is cumulative kg from the
original collection origin. For a stop `b`, additional solute is
`F(b) = integral_a^b sigmoid(eta(u)) du` in kg, and suffix-average TDS is
`100*F(b)/(b-a)` percent by mass. Early concentrations remain kg/kg. These
are modeled suffix quantities, not measured whole-cup totals, extractable
inventory, extraction yield, flavor or physical stopping accuracy.

Require `anchor <= stop_min_kg <= stop_max_kg <= model.domain_kg`, at least
one delivery constraint, finite real numbers, ordered bounds, nonnegative kg,
TDS between 0 and 100 percent, and the declared mass basis. No clipping is
performed. Booleans, strings as numbers, nonfinite values, and unexpected fields
are rejected. A nonnegative solute target beyond attainable delivery is valid
but unreachable. TDS queries additionally require `stop_min_kg > anchor`.
A single-point allowed range above the anchor is valid for TDS; a zero-width
*suffix* is not. Solute-only queries can include the anchor and zero delivery.

All inequalities are inclusive. Result statuses are:

- `FEASIBLE_RANGES`: topology resolved under the declared numerical allowances.
- `NO_FEASIBLE_RANGE`: all enumerated possibilities excluded; no unresolved region.
- `NUMERICALLY_UNRESOLVED`: ambiguous regions remain, with qualified partial
  components retained. Two partial components may connect through an unresolved
  region; their count is not a claim about the complete true topology.

Each component has `lower` and `upper` endpoint records, each with an enclosure
`[lower_kg, upper_kg]`. A crossing bracket contains the endpoint; its individual
mass values are not asserted to satisfy the constraint. `interior_min_kg` and
`interior_max_kg` delimit the qualified portion. An isolated solution may have
no representable interior witness and instead carry the same root enclosure
at both ends. Exact endpoints are reserved for supplied query coordinates and
algebraically established structural roots. Unresolved adjacency is explicit.

## Complete-set mathematics

In exact arithmetic the following finite enumeration is complete:

1. The existing model has five original knots. On each segment `eta` is affine,
   so `q = sigmoid(eta)` is monotone and, for finite logits, strictly between
   zero and one. Consequently `F` is strictly increasing. A solute threshold
   has at most one crossing, and equality can define an isolated feasible point.
2. For a TDS threshold `t = requested_percent/100`, define
   `h_t(b) = F(b) - t*(b-a)`. Then `h_t'(b) = q(b)-t`. For `0<t<1`, a segment
   has at most one stationary point, found from `eta(b) = logit(t)`.
   Constant segments are considered explicitly. At `t=0` and `t=1`, use the
   strict finite-logit bounds directly, with no infinite-logit arithmetic.
3. Partition at query endpoints, original knots and every threshold's stationary
   point. Each remaining piece is monotone for its threshold residual. Equal
   nonzero endpoint signs exclude a crossing; opposite signs bracket the unique
   crossing. Inspect zero endpoints, constant zero pieces and stationary
   tangencies separately. This includes crossings at knots or query boundaries.
4. Overlay all threshold boundaries. On every open interval between them, each
   inequality has constant truth. Intersect those truths and inspect the boundary
   points themselves. Join touching feasible pieces, preserving disconnected
   intervals and singleton solutions.

The implementation uses this structure, not a grid. It calls the unchanged
`State.remaining_solute()` observer and its stable integration kernel. It does
not reconstruct features, duplicate the fitted predictor, fit parameters or
assume a declining concentration. Equal lower/upper bounds share one boundary
function, allowing qualified singleton root enclosures.

## Floating-point qualification and limits

Exact-arithmetic completeness is distinct from the floating-point disposition.
Each forward call must meet the parent's existing `1e-9 kg` solute-allowance
ceiling. The observer's quadrature/refinement allowance is propagated, with an
additional arithmetic allowance of
`128*eps*(abs(F)+abs(target_term)+(b-a)*(1+max(abs(logits))))` kg for residual
subtraction, products, interpolation and cut arithmetic. TDS residual allowance
is `100*allowance_kg/(b-a)` percentage points. Computed stationary points receive
small guard intervals accounting for affine inversion arithmetic; within a
guard the `|h'| <= 1` bound also covers its half-width. Degenerate knot geometry,
forward failures, excessive allowances and arithmetic overflow remain unresolved.

Bisection retains confidently signed sides and never discards a midpoint whose
residual overlaps its allowance. Each boundary uses at most 128 refinement
iterations (two searches of at most 64). Uncertainty touching a shared knot or
stationary point is combined before topology decisions. A qualified crossing
needs opposite confident signs, a unique monotone crossing through the enclosure,
and a bracket no wider than `1e-8 kg`. Bracket width contributes a separate
residual effect of at most that width in kg and `100*width/(lower_mass-a)` in
percentage points; these effects are reported alongside residual allowances.

Numerically inseparable crossings, overlapping constraints, tangencies, flat
thresholds without an exact algebraic identity, and unresolved query-endpoint
equalities retain explicit regions. An interval with no representable interior
mass is unresolved, so a rounded midpoint cannot turn a singleton into an interval.
A retained point beside unresolved territory is marked partial, without asserting
isolation. A nonstructural equality at a query boundary
may be unresolved even when a rounded forward value appears exactly equal.
Very small concentrations can make inversion ill-conditioned because the parent
absolute allowance divided by `q` is large. Saturated or underflowed sigmoid
arithmetic is never treated as evidence that finite-logit `q` equals zero or one.
The anchor identity and all-zero-logit prefixes (`F=(b-a)/2`) are checked with
exact rational arithmetic on the stored binary coordinates where applicable.

These are engineering allowances, not rigorous interval-arithmetic certificates,
experimental uncertainties or statistical prediction intervals. The mass
resolution is a numerical target, not a claimed physical stopping precision.
No refinement changes the forward algorithm or the historical adequacy budgets.

## CLI and private saved inputs

The source-free demonstration constructs a first-party synthetic model:

```bash
python -m puckworks.analysis.conditional_tail_stopping --synthetic
```

Saved mode accepts the parent's `state.to_dict()` and `query.to_dict()` JSON:

```bash
python -m puckworks.analysis.conditional_tail_stopping \
  --state "$STATE_JSON" --query "$QUERY_JSON" --output "$OUTPUT_JSON"
```

Saved query JSON requires `stop_min_kg`, `stop_max_kg`, `mass_unit="kg"`,
`solute_unit="kg"`, `tds_unit="percent"` and `basis="MASS"`. The four optional
constraint fields can be omitted or null, provided at least one is supplied.
Duplicate keys, nonfinite JSON, unknown fields, modified model identities and
incorrect derived state fields are rejected. Saved states and results must be
outside Git. Output creation is exclusive; existing files are never overwritten.
Saved mode prints neither states nor results, including on input errors.

## Scope, availability and preserved evidence

The bounded owner task explicitly authorizes G0 implementation, numerical
verification, normal QA, ordinary review and a draft PR. No additional empirical
information enters. Positive engineering evidence retains a usable inverse;
negative or unresolved implementation evidence identifies the unsupported
numerical case. This supports modeled mass-conditioned suffix delivery without
resolving inventory, hydraulics or physical control. It does not revisit a
repeated empirical blocker or authorize a successor search.

Scoped data preflight: `NOT_APPLICABLE_TO_NEW_DATA_G0`. The saved C0/C1/C2
artifacts and parent runtime were inspected and hash-checked against the existing
[006 handoff](https://github.com/trbrewer/espresso-whole-pull/blob/f15a417cbf3c7528ac734537bb844cab6dc98287/docs/analysis/sci_md_mass_delivery_006/HANDOFF.json).
The source guide, card, protocol and prior preflight supply the unchanged context.
No original workbook, source download, private row prediction or outcome join is
needed or accessed by this capability. External corpus availability is not being
reassessed and no exhaustion or measurement recommendation is made.

`pannusch2024/experimental_kinetics` and `schmieder2023/raw_fractions` share one
physical lineage. Synthetic examples are neither experimental replicates nor
holdouts. Retain Pannusch/Schmieder attribution, Mendeley
10.17632/y2tz67f6ry.1, and source-derived **CC-BY-NC-3.0** restrictions separately
from first-party software licensing. Models are reused in place, not copied.
Historical C2 `LEARNED_TWO_ASSAY_MAPPING_EARNED` remains exactly its bounded
conclusion; C0/C1 remain selectable inputs without a new ranking.

RESEARCH_ONLY / SOURCE_INTERNAL / TARGET_EXPOSED /
CONDITIONAL_ON_BEVERAGE_MASS / MODELED_GAPS_NOT_MEASURED_WHOLE_CUP /
NO_REAL_TIME_ASSAY_CLAIM. PHYSICAL_VALIDATION=NOT_ESTABLISHED.
No optimal recipe, flavor objective, mechanism, independent validation, inventory
closure or validated stopping controller is claimed.
PRODUCTION_ADOPTION_AUTHORIZED=false; MERGE_AUTHORIZED=false;
AUTO_MERGE_AUTHORIZED=false; NATIVE_EWP_RUNS=0;
NO_SUCCESSOR_SEARCH_AUTHORIZED. Task fits and outcome joins/scores are zero.

See [verification and reproduction](VERIFICATION.md).
