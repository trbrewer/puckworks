# MODEL-PANNUSCH2024-STATE-ENVELOPE-005 handoff

G0 / NO_GOVERNING_PHYSICS_CHANGE / RESEARCH_ONLY.
PHYSICAL_VALIDATION=NOT_ESTABLISHED.

The requested initial-state delivery-envelope and direct shared-state contrast
capability is implemented. All declared numerical checks pass for the stated
contract. The numerical disposition is
`DECLARED_NUMERICAL_VERIFICATION_PASSED_SOFTWARE_AND_HOSTED_CI_SEPARATE`.
Software QA, required hosted CI and ordinary review remain separate evidence;
the draft PR carries the final publication head and current hosted status.
`ENGINEERING_CAPABILITY_VERIFIED` is earned only when all mandatory
implementation/verification and required software/CI checks pass.

Author review after the declared programme identified an extreme-dynamic-range
LP upper-bound scaling underflow when the corresponding lower bound is zero.
A guard/regression correction and the four reserved response executions are
pending. This candidate is not yet a completed engineering qualification.

## Exact authority and changed paths

Actual Puckworks base: `28c32df8ed996043f943b777e9312016e8b5ce05`, tree
`746e4c8970c57720d9c4b1dc51fcf40eee50a55c`, containing merged #318.
Read-only EWP remote main: `73ec476ffe6ac626705ca949e28b32935ddf2992`;
owner checkout: `78cbd59c751393cddfe539e4c69e43a224329bca`.
The sole feature branch is `model/pannusch2024-state-envelope-005`.
The base's quick-pr run was cancelled; the clean local baseline passed before
implementation. Relevant open PRs/branches and accessible worktrees had no
duplicate capability. Unrelated owner worktrees were not repurposed.

The implementation adds `puckworks/models/pannusch2024/state_envelope.py`,
`tests/test_pannusch_state_envelope{,_verification}.py`,
`examples/pannusch_state_envelope.py`, and
`tools/pannusch_state_envelope_verification.py`. Documentation is this bundle,
the model card, ROADMAP, SPRINTS, task ledger and the canonical planning item;
dependent generated status/Insight Foundry files are refreshed by their normal
generators. Existing runtime files and parameter tables remain byte-identical.
No global contracts, registry defaults, scientific gates or workflow selectors
change. Historical 001/002/003/004 evidence remains at its actual producer.

[INTAKE.json](INTAKE.json) records inspected repository context, unchanged
source identities, dataset lineage, the scoped data preflight and clean
baseline. No owner-local originals were freshly inspected or executed for this
task, and no observation values were used to select states, histories, margins
or tolerances. Normal isolated silent integrity QA is separately authorized
under SCI-GOV-001. Missing originals establish no exhaustion.

[PRE_EXECUTION.json](PRE_EXECUTION.json) records exact new source/test/example
and verification-specification hashes before the full comparison. Numerical
execution used that working-tree producer on the exact base above; its source
hashes, not a later report-edit commit, identify the producer. The final PR
contains these unchanged numerical source bytes.

## Public contract and example

`FVChemicalStateSet` intersects explicit liquid/fine/coarse cell concentration
bounds with kg total/optional phase intervals and requires an assumption label.
One species, fixed source configuration/grind/mesh/geometry/absolute start per
query. Concentrations are kg/m^3 on their own source phase bases; fine capacity
has no phi_v2. Equal bounds and exact zero are supported. Invalid, empty and
numerically unresolved inputs/results are distinct; no nominal substitution,
constraint widening, source equilibration or inferred state range occurs.

`build_delivery_response` produces reusable sparse transpose responses on
`FVPlan.primary_steps`; partial windows retain original frozen T/Q and local
accumulator rewards. `bound_delivery` optimizes both extrema with checked
primal/dual evidence. `contrast_deliveries` directly optimizes g_A-g_B over the
same U and requires epsilon_kg, delta_kg and a comparison basis.
`replay_extrema` explicitly replays primary witnesses through unchanged
`simulate_stateful_fv`; contrast witnesses replay both plans from the same state.
Per-witness replay/qualification operations also support explicit accounting.

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 \
python examples/pannusch_state_envelope.py
```

The [API/mathematical contract](README.md) gives decision precedence, immutable
results, optimization gaps and failure semantics. The example uses only public
state/envelope operations. It supplies synthetic assumptions, not observations.

## Declared result and numerical limits

At N400/h=.02, the outer individual delivery intervals are
A `[2.67072164263e-5,7.34019863370e-5]` kg and
B `[2.63995614636e-5,7.29711439721e-5]` kg. The direct shared-state contrast is
`[-9.53471518632e-8,8.57447041541e-7]` kg. Both prescribed collection volumes
are 2.16e-5 m^3. With epsilon=1e-9 kg and delta=1e-6 kg, the numerical quality
is `NUMERICALLY_QUALIFIED` and the decision is
`NO_MATERIAL_DIFFERENCE_THROUGHOUT_SET`. Feasible replayed witnesses support
an opposite-sign reversal below the material margin, not a material reversal.

Both extremum gaps are <=9.077e-14 kg. All six primary states satisfy original
constraints after explicit recorded roundoff repairs. Eight fresh trajectories
check them, including both histories for each contrast witness. Response,
optimization, summation/conversion and replay allowances are separate. The
largest absolute forward/response discrepancy is 3.118e-19 kg. Witness state
identities, phase inventories, original/repaired residuals and replay facts
are retained in [RESULTS.json](RESULTS.json); bulky arrays stay outside Git.

Whole-U temporal contrast sensitivity upper bounds are 6.500e-12 kg for
.02/.01 s and 1.732e-12 kg for .01/.005 s. The inventory-preserving N400/N800
contrast sensitivity upper bound is 1.361e-9 kg. Every temporal level and each
individual response are reported in [RESULTS.md](RESULTS.md). These do not
become rigorous continuum-error allowances or universal coverage of arbitrary
states/windows. The old 004 allowance is not inherited. Its temporal-decrease
failure and `IMPLEMENTED_QUALIFICATION_INCOMPLETE` remain unchanged.

## Resource and acceptance receipts

The predeclared 28 large executions completed: 18 response passes, eight
primary witness trajectories and two unchanged forward timings. Four correction
slots are unused (hard total 32). 101728 exponential actions; 38 LP calls;
100.913519/1800 s aggregate numerical wall; 172368 KiB peak RSS. All numerical
thread settings were 1. Per-call forward settings retain the 120 s ceiling.
No dense full-mesh transitions or coordinate-wise forward sweep occurred.
Baseline/final timing includes correctness checks and earns no speedup claim.
See [RESOURCES.json](RESOURCES.json).

The separately invoked runner is:

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 \
python -m tools.pannusch_state_envelope_verification baseline --evidence-dir "$EVIDENCE_DIR"
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 \
python -m tools.pannusch_state_envelope_verification execute --evidence-dir "$EVIDENCE_DIR"
```

The Git-common-directory receipt prevents resetting this task by changing
output/worktree directories; the existing campaign refuses an unaccounted
repeat. An independent parent enforces the remaining aggregate deadline.
These reproduction commands are not authorization for another campaign.
Ordinary CI tests are small meshes; no full programme is hidden in optimizers
or tests. Fine-level sensitivity and timing-repeat candidates are not primary replay witnesses.

[QA.json](QA.json) records actual baseline/final checks, skips, warnings and
any incomplete check separately from numerical results. Review performed by
the implementation agent is nonhuman author review, not independent review.
No human or independent scientific review is implied. Required hosted CI and
ordinary owner review are reported on the draft PR; auto-merge is disabled.

No numerical mandatory check failed or was skipped in the declared programme.
The full-mesh programme used no correction execution. External-data/live/GPU
software lanes remain outside the normal selected QA, and Python versions not
installed locally are covered only by the actual hosted matrix, not by an
invented local result. Source-derived outputs retain Pannusch/Schmieder
CC-BY-NC-3.0 attribution separately from first-party software licensing.

No merge, release, publication deployment, EWP write/run or lock change,
protected-target scientific scoring, laboratory operation, author contact,
physical-validation claim, measured-state recovery, universal profile ordering,
taste claim, corpus-exhaustion conclusion, whole-shot coupling or successor.
