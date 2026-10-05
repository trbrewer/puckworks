# Common-past paired contrast

007 bounds delivered-solute B_MINUS_A over the original chemical-state set jointly
intersected with every supplied early fraction band. It preserves correlations;
there is no selected best-fit state, schedule optimization or winning-arm premise.

```python
from puckworks.models.pannusch2024 import common_past_contrast as contrast
from puckworks.models.pannusch2024.prefix_conditioned import condition_on_fractions

conditioned = condition_on_fractions(original_U, complete_plan_A, observations)
query = contrast.bound_common_past_contrast(
    conditioned, response_A, response_B,
    branch_time_s=branch_time, epsilon_kg=epsilon, delta_kg=margin,
    comparison_basis="MATCHED_COLLECTED_VOLUME",
)
result = contrast.replay_common_past_extrema(query)
print(result.to_json())
```

Responses come from the unchanged `state_envelope.build_delivery_response`.
Observation objects remain `FVFractionObservation` bound to A. The operation
validates common history functions AND original compiled primary prefixes;
a caller's label or assertion is insufficient. Its immutable receipt binds both
complete plans, original U, observations, model/source identities, branch/window,
settings/margins, mapping and B_MINUS_A orientation. No observation plan changes.
A branch must be an existing primary boundary, strictly inside the common span.
A forcing jump AT branch is allowed. The common chemical state excludes outgoing
instantaneous Q/T, which may change at that instant.

`MATCHED_COLLECTED_VOLUME` refers to the target window, consistently with 005.
`EXPLICIT_UNEQUAL_VOLUME` accepts an explicitly unequal target volume. The receipt
reports target and whole post-branch volumes separately. No beverage-mass or
experimental-flow conversion is inferred.

For explicit equal-child sensitivity, use `pull_back_equal_children(native,U)`
and `bound_mapped_common_past_contrast(U,A,B,observations=...,...)`. Empty mapped
queries have this separately labelled numerical-core path; 006's native-only
empty guard is unchanged. Replays lift each original coarse state, introducing
no independent fine-cell freedom.

Native empty queries call 005 `contrast_deliveries(U,B,A,...)` because its legacy
orientation is first-minus-second. The original optimization and reconstruction
receipt remains in `legacy_b_a`, including its original label meanings and
failure dispositions. 007 rechecks proposed witnesses using 006 exact rows; a
necessary bounded repair preserves the legacy receipt and changes only the 007
witness. Both actual batched forwards use that same state. Their native replay
receipts can qualify the original 005 result only when its witness identities
are unchanged. No extra trajectory is run just to decorate a historical receipt.
007 computes complete replay-inclusive gaps separately; a legacy certificate
never silently certifies the stricter query.

Outputs distinguish compatibility, extremum qualification, decision and
termination. Outer feasibility is insufficient; an empty sufficient-inner search
is not incompatibility. Only a checked outer/original contradiction establishes
incompatibility. Failed arithmetic/replay and null outputs retain reasons.
Supporting marginal intervals are outer-only and are not claimed attained.

An exact-zero contrast requires identical complete plan/operator/window/mapping
identities and separate compatibility evidence. Opposite-sign and material
reversal witnesses are separate facts; an outer interval crossing zero proves
neither. A small sign reversal may coexist with NO_MATERIAL_DIFFERENCE.

## Reproduce

Install the repository's ordinary development dependencies, then:

```bash
python -m pytest -q tests/test_pannusch_common_past_contrast.py tests/test_pannusch_common_past_contrast_verification.py
PYTHONPATH=. python examples/pannusch_common_past_contrast.py
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONPATH=. \
  python tools/pannusch_common_past_contrast_verification.py --output "$EVIDENCE_DIR"
```

The example uses four cells and needs no private files. The last command is the
separate fixed representative campaign, not CI. Its persistent common-Git-directory
budget refuses to reset with a different output directory or worktree. Respect
already consumed work; inspect retained receipts before any bounded correction.
All failed attempts count. A fresh clone can reproduce the public synthetic
inputs independently. No private original data are required.

[Prospective specification/test matrix](CONTRACT.md), [pre-execution identities](PRE_EXECUTION.json)
and [live preflight](LIVE_PREFLIGHT.json) define the bounded query.
Engineering allowances are not rigorous continuum or statistical confidence
certificates. Fixed-operator qualification and mesh/timestep sensitivity are
separate. Preserve 004's incomplete temporal qualification, 005's historical
1 mg decision, and 006's findings. More solute is not better espresso or a taste,
causal experimental, probability, or recipe claim.

G0 / NO_GOVERNING_PHYSICS_CHANGE / RESEARCH_ONLY.
PHYSICAL_VALIDATION=NOT_ESTABLISHED. Pannusch DOI 10.1016/j.jfoodeng.2023.111887;
source-derived CC-BY-NC-3.0 (Mendeley 10.17632/y2tz67f6ry.1) remains separate from
first-party licensing. No EWP/lock/default/forward change, release or successor.
