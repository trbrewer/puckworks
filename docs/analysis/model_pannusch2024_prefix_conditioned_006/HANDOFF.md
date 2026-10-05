# Prefix-conditioned 006 handoff

**ENGINEERING_CAPABILITY_VERIFIED** on the mandatory small analytical/manufactured
and fixed-model tests plus the representative synthetic fixed-operator query.
G0 / NO_GOVERNING_PHYSICS_CHANGE / RESEARCH_ONLY.
PHYSICAL_VALIDATION=NOT_ESTABLISHED. No empirical predictive advantage is established.

The deliverable is [draft Puckworks PR #320](https://github.com/trbrewer/puckworks/pull/320) from
`model/pannusch2024-prefix-conditioned-006`, unmerged with auto-merge disabled.
Exact publication head/tree and final hosted check states belong to the PR and
final delivery receipt; they are not self-referential claims inside their own
commit. The source candidate verified locally is
`5fb7b83e2585556f910a2754225b5f8cdbcf55a7`; the publication follow-up changes only lifecycle documentation.
Base is `4f652dee3a43e9e97dc555173cb469d424cdc69a`, tree
`c17082884871e0a37dced8598560b191c8425da1`. EWP remote remains the reviewed
`73ec476ffe6ac626705ca949e28b32935ddf2992`, tree
`8ced37ad5b294616b8935d92a57e3845321d5eed`.

## Capability and files

The additive `prefix_conditioned.py` exposes `FVFractionObservation`,
`FVPrefixConditionedSet`, `condition_on_fractions`, `bound_future_delivery`,
`replay_conditioned_extrema`, and a named equal-child sensitivity pullback.
See [API and explicit commands](README.md), [numerical specification](CONTRACT.md),
[two small test suites and their requirements](TEST_PLAN.md), the public example
`examples/pannusch_prefix_conditioned.py`, and the separate runner
`tools/pannusch_prefix_conditioned_verification.py`.

The model card, ROADMAP, SPRINTS, task ledger and live status receive additive
006 entries. Status reconciles 005's already-merged #319 without restamping its
historical evidence. Status and insight surfaces are regenerated through their
existing generators. No forward model, state_envelope.py, parameter table,
default, dependency, registry or workflow changes are included.

## Numerical outcome

At N400/h=.02, the unconditioned interval is
[1.2056084186673772e-5, 2.708487175825335e-5] kg; conditioned interval
[1.5496913443458448e-5, 2.4013808699025333e-5] kg. Complete minimum/maximum
gaps are 1.0982634987804617e-12 / 1.5832919861519332e-12 kg, both below
1e-9. Compatibility is ESTABLISHED; bounds QUALIFIED. Absolute width reduction
is 6.511892316012693e-6 kg (relative 0.43329458780341723), exceeding the
combined endpoint uncertainty. Conservation-only gives
[0, 9.067447797340304e-5] kg using both disjoint lower bands and no kinetics.

All four fixed operators qualify; eight reconstructed witnesses satisfy every
original U row and observation, and all batched replays pass complete-interval
containment. Fine responses use P^T*g and |P|^T*a on original coarse coordinates,
with exact equal-child state replay. N800's minimum endpoint changes about
-7.13e-9 kg, beyond epsilon. Both temporal maximum-change signs are unresolved.
[Results](RESULTS.md) report every interval, bracket, sensitivity and limitation;
[compact strict JSON](RESULTS.json) contains the detailed evidence.

Engineering response allowances remain estimates, not rigorous interval,
continuum, statistical-confidence or physical bounds. No unique-state recovery,
changed-future comparison, ranking, real-data scoring or reversal of MASS-DELIVERY.
Historical 004 remains IMPLEMENTED_QUALIFICATION_INCOMPLETE with
resolved_temporal_decrease=FAIL; 005's 1 mg decision is unchanged.

## Resources, preservation, QA and review

Campaign: 34/64 propagation executions, 64/160 LP invocations, 144860 exponential
actions, 170.267721461 s aggregate campaign wall / 1800 s. Measured maximum child
RSS 355324 KiB; simultaneous parent/child peak was not measured. Thread settings
are all 1. Initial PLANNED_STOP harness rejection, eight failed repair LPs and
all four initial unresolved witness results remain visible. The correction
reuses unchanged native responses and frozen bands; no response repeat or
recentered observation. See [resources](RESOURCES.json), [initial results](INITIAL_RESULTS.json),
and both correction receipts. No unused budget authorizes further exploration.

[PRESERVATION_CHECK.json](PRESERVATION_CHECK.json) verifies every protected source,
parameter/default and 001–005 evidence hash in [PRESERVATION.json](PRESERVATION.json).
The EWP lock remains SHA-256
`52b15ceef87d503a3e77c6e3c1cbed785185d2dde0b79647e5fbe309395d2f10`;
EWP's owner worktree remains clean and its code was not executed.

Local QA: clean baseline 5939 passed; final normal selection 5982 passed,
65 skipped, 63 deselected, with one unchanged DEV salt warning. Focused and
minimum-dependency tests each pass all 43 cases; historical integrity passes
5 with 7 skips. Ruff, mypy, generated checks, source/hash/path checks and clean
installed-wheel/sdist verification pass.

[QA.json](QA.json) separates the clean baseline, final focused/full QA,
minimum dependencies, packaging and generated-document verification. The base
hosted quick-pr coverage job was cancelled, including its single retry; Python
3.10–3.13, min-deps and mypy passed. Cancellation is not a scientific failure.
Final exact-head hosted states are reported as observed; pending, cancelled or
unavailable is never PASS. Supported CI interpreters/selection/coverage are unchanged.

[Code review](REVIEW.md) is explicitly nonhuman author review. Ordinary human/
independent owner review remains pending on the draft; no approval is invented.
The review addresses inner/outer signs, positive contradiction evidence, repair
against every observation, and hidden tolerance risks. This is separate from
software QA and numerical qualification.

Full arrays, raw optimizer states, complete logs and detailed environment/worktree
receipts stay in the owner-retained external task evidence directory, with file
hashes in [EXTERNAL_EVIDENCE_INDEX.json](EXTERNAL_EVIDENCE_INDEX.json). Concise
committed receipts contain no local absolute paths or original observations.
Original-observation access is NOT_NEEDED_FOR_SYNTHETIC_G0; eventual Pannusch and
Schmieder corpora retain shared lineage and prior exposure. Absence in a checkout
is not corpus exhaustion. Source-derived CC-BY-NC-3.0 rights/attribution remain
separate from first-party code licensing. No EWP write/run, acquisition, release,
laboratory operation, merge or successor is authorized or performed.
