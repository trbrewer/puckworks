# Prefix-conditioned finite-fraction delivery

G0 / NO_GOVERNING_PHYSICS_CHANGE / RESEARCH_ONLY.
PHYSICAL_VALIDATION=NOT_ESTABLISHED. This is a checked set-valued inverse query
for depth-resolved initial phase states, not a fitted state or a first
programme early-to-late predictor. All MASS-DELIVERY conclusions and 001–005
historical evidence remain unchanged. See [specification](CONTRACT.md) and
[small-test requirements](TEST_PLAN.md).

## Public operations

Import `puckworks.models.pannusch2024.prefix_conditioned` and reuse 005's
`state_envelope.FVChemicalStateSet` / `build_delivery_response` and 004's
`stateful_fv.FVPlan` / `FVChemicalState`.

```python
observation = FVFractionObservation(
    'first-fraction', early_response, (lower_kg, upper_kg),
    'explicit caller provenance / numerical assumptions')
joint = condition_on_fractions(original_U, immutable_plan, (observation,))
bounds = bound_future_delivery(joint, later_response, epsilon_kg=1e-9)
checked = replay_conditioned_extrema(bounds)
print(checked.to_json())
```

These operations accept existing response objects, so queries reuse propagation.
`condition_on_fractions` performs no propagation or optimization. The observation
binds its response's species, model/source/config, phase bases, mesh, plan and
absolute window. No concentration, density, recovery, percent-TDS, confidence or
precision conversion occurs. Unique nonempty labels and explicit provenance are
required. At most 32 observations; lists/tuples only. Canonical label ordering
makes reordering deterministic; duplicate/overlapping bands with distinct labels
remain separate joint constraints without any independence assumption.

Windows are half-open [start,end) in absolute seconds. Positive duration is
required. Adjacent boundaries may coincide. Every early window ends no later
than the finite target starts. Target observations/values are not accepted.
Malformed, mismatched, stale, nonfinite, boolean and unrepresentable input values
are input errors. Numerical failures remain explicit unresolved results.

An empty native observation list returns 005's `FVEnvelopeResult` directly;
`replay_conditioned_extrema` delegates that result to 005 replay. Bounds,
witnesses, qualifications and failure semantics are retained exactly, with no
new propagation or duplicate optimization.

`pull_back_equal_children(native_fine_response, original_U)` is the explicit
N-to-2N sensitivity mapping. It returns `FVEqualChildPullback`, retaining the
native fine identity, weights P^T*g, allowance |P|^T*a and mapping roundoff.
P splits phase mass equally into children. Replays lift the state exactly and
check representability. Fine-cell freedom is never added. A coarse U/fine plan
requires explicit mapped observations; empty queries use native 005 coordinates.
This is a named mapping, not a general remeshing interface.

## Meaning of results

`FVPrefixBounds` retains original U, all original observations, the immutable
plan/target, the unconditioned result, conservation comparator, outer, actual inner and stricter witness-search
matrices, every LP receipt and all raw/reconstructed/replayed witnesses.
No coordinate-wise box substitutes for the correlated feasible set.

- `compatibility`: ESTABLISHED only after a representable sufficient witness and
  contained forward replay; INCOMPATIBLE_UNDER_DECLARED_CONTRACT only after a
  checked outer contradiction (or exact original-set/zero/singleton contradiction);
  otherwise UNRESOLVED. This rejects the joint model/U/observation/allowance
  combination, not any uniquely identified physical cause.
- `bounds`: QUALIFIED only after both complete extremum brackets fit epsilon
  and both witnesses replay successfully; NUMERICALLY_UNRESOLVED otherwise;
  NOT_APPLICABLE for a checked incompatible set.
- `minimum.interval_kg`: [checked global lower, compatible witness upper].
  `maximum.interval_kg`: [compatible witness lower, checked global upper]. Outer
  optimizer states are never implicitly called compatible extremizing witnesses.
- Widths, absolute reduction and a relative reduction (undefined for zero baseline
  width) report informativeness. `reduction_resolved` additionally requires a
  qualified result and reduction exceeding combined endpoint uncertainty.
- `discretization` explicitly excludes sensitivity from fixed-operator bounds.
  Agreement under refinement is not a continuum certificate.

The coefficient allowances inherited from 005 are engineering estimates, not
rigorous interval-arithmetic guarantees. The binary-rational LP checker is exact
for its supplied floating coefficients, but that does NOT upgrade the inherited
response estimates, model assumptions or physical validity. These are not
statistical confidence intervals or unconditional physical bounds.

The separately stored witness-search set adds an explicit conservative replay
reserve to the actual sufficient inner set. Its empty set
proves no incompatibility. A nonempty outer relaxation alone proves no compatible
exact-model state. Failed conditioning cannot be certified by a fallback.
Every replay batches all early windows and the target through unchanged
`simulate_stateful_fv`, with direct interval-local accounting on the original
primary steps. The entire prediction/replay interval must lie inside each band;
overlap is insufficient. Parent accuracy remains NOT_ASSESSED.

`conservation_bound(Mmax, [(label, window, mass_band), ...])` uses no FV kinetic
responses. It selects a deterministic valid disjoint subset with maximum summed
lower mass and returns [0,Mmax-sum(lower)] with outward arithmetic. It is only a
conservative union bound. A negative remainder is marked a conservation
contradiction, never a valid zero interval.

Strict deterministic JSON includes hashes for arrays by default; use
`include_arrays=True` for actual arrays and `include_timing=True` for timing.
A bounded box projection is only a repair candidate: every original and actual
inner row is rechecked, followed by replay; a failing candidate may use one
bounded all-row LP. No phase/total rebalancing is assumed to preserve observations.
Nested records and arrays are immutable. All work limits, allowances, repairs,
raw residuals and failure reasons remain visible.

Representative synthetic disposition: ENGINEERING_CAPABILITY_VERIFIED. See
[results](RESULTS.md), [QA and review handoff](HANDOFF.md), and retained initial
failures/corrections. Qualification is specific to the declared engineering
allowances; N800 sensitivity exceeds epsilon for the minimum endpoint.

## Commands

Small public example (deliberately broad, potentially uninformative synthetic
mass band; no source observations):

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 \
python -m examples.pannusch_prefix_conditioned
```

Separate authorized full-mesh campaign, outside pytest:

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 \
python -m tools.pannusch_prefix_conditioned_verification --evidence-dir "$EVIDENCE_DIR"
```

The runner is POSIX/Linux, uses one persistent task receipt, and externally
bounds every native call and the whole campaign. These reproduction instructions
do not authorize resetting a consumed budget or running a successor. Full arrays,
trajectories and logs stay outside Git; concise receipts identify them by hash.

Source attribution: Pannusch et al., DOI 10.1016/j.jfoodeng.2023.111887;
Pannusch/Schmieder source-derived outputs retain Mendeley
10.17632/y2tz67f6ry.1 CC-BY-NC-3.0 separately from first-party code licensing.
