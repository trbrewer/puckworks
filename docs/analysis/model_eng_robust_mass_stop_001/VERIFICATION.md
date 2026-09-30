# Numerical verification and repository QA

MODEL-ENG-ROBUST-MASS-STOP-001 — G0 / NO_GOVERNING_PHYSICS_CHANGE / RESEARCH_ONLY.

**ENGINEERING_CAPABILITY_VERIFIED.** Mandatory numerical verification, required
local repository QA and ordinary author review pass. Final focused suite:
**239 passed** (47 new, 192 unchanged predecessors), 106.82 seconds. Maintained
normal suite: **5,300 passed, 64 skipped, 60 deselected**, 1090.85 seconds.
Hosted CI is reported separately on the draft PR. Independent reference mathematics
is not independent reviewer approval. Merge and production adoption are unauthorized.

## Identities and preservation

Fetched defaults exactly match the reviewed identities, with no intervening commits:

| Repository | Commit | Tree |
|---|---|---|
| Puckworks | `8fa96fc3fd993264af1dfadc2942327133fe80db` | `b4bb230e4fc746bbc59299e827bcb0c220887ea1` |
| EWP, read-only | `f15a417cbf3c7528ac734537bb844cab6dc98287` | `a36a006be6d9bb3fb4516ec78ed4299d2e2529b8` |

The bounded drift check inspected recent PRs/issues and every open PR. Puckworks
#257 concerns publication and #264/#129/#128 change Actions dependencies; EWP
#117 is a historical evidence audit and #130 changes Actions. None overlaps this
capability or changes its parent contracts. No broad task-selection or successor
search was performed. The supplied heads for Puckworks #301/#302/#288/#296 and
EWP #194 match their merged publication records. Frozen historical lifecycle
prose is unchanged. Source/test identities for the accepted numerical implementation:

- API SHA256: `0216cc54419e94c1e45d9e851d444fb6650daa574b2c239696f3d9bfc9a985d5`.
- Tests SHA256: `e52f521fcbc0506ad26a6427fd25098e23db1f2953994fae28595bff644c0e75`.

Publication commit/tree and live hosted checks are recorded on the draft PR; this
document does not attempt to contain its own final commit identity. Baseline-wide
byte comparison covers 2,442 existing Puckworks files: only the three authorized
planning files differ, leaving all 2,439 others unchanged. All 1,946 tracked files
in the owner's EWP checkout and all 2,091 in the owner's Puckworks checkout are
unchanged, with both original heads preserved. The imported reviewed EWP tree and
its historical handoff/pins remain unchanged.

The evaluated MASS-DELIVERY-006 producer remains
`0f130d4f2dfca552e56cd7d7e96bb73b8c50f421`, tree
`9f6b5346ea7cfceef4d014c80b235818eee0a23f`. The runtime and all three saved models
are byte-identical to that producer; a publication head is not substituted into
EWP's historical handoff. Work uses isolated branch
`model-eng/robust-mass-stop-001`; owner checkouts and branches are untouched.

## Independent numerical references

The [README](README.md) gives the continuous coverage argument separately from
floating-point qualification. Tests integrate the stated affine-logit model with
independent fsum conditioning, adaptive quadrature and segment refinement. They
never call the production integration kernel to manufacture expected values.
Reference extrema follow convexity or proven assay monotonicity. Scalar residual
roots are bracketed on monotone pieces separated by independently bracketed
derivative roots, retaining knot boundaries. Mass grids and corner-only inverses
are not universal oracles.

The frozen-C2 fixture loads C2.json in place and uses its saved means for m1,
m2 and q1, q2 in `[0.0931364597, 0.1830244866]`, anchor
`0.012921191111111112 kg`, and the unchanged full suffix domain. All knot logits
are negative throughout the assay interval. Hence
`d²F/dq2² = integral beta2²*c*(1-c)*(1-2*c) du > 0` on positive support.
Endpoint derivative checks retain endpoint minima when appropriate; otherwise
independent derivative bracketing locates the unique interior minimum.

Independent recomputation (adaptive refinement, not copied expected numbers):

| Quantity | Reference |
|---|---:|
| Full-box lower crossing, kg | 0.04184117210147098 |
| Interior minimizing q2 there, kg/kg | 0.14327933303178286 |
| Corner-only lower crossing, kg | 0.040487607611635994 |
| Corner-only upper crossing, kg | 0.041142221852795195 |
| Lower-q2 endpoint delivery at robust crossing, kg | 0.0017015031334205206 |
| Independent delivery reference allowance, kg | 3.8890479551953114e-17 |

At the full-box lower crossing for 0.001640 kg, the lower-q2 endpoint delivers
more than 0.001670 kg. Monotonic delivery proves the combined band empty: below
that crossing the minimum misses the lower limit, and at or above it this endpoint
violates the upper limit. These are recomputed regression fixtures, not a new
scientific finding. The nominal and corner-only point inverses intentionally give
nonempty alternatives and are retained solely as insufficient comparators.

The default lower-crossing result has unresolved neighborhood
`[0.041841078552873404, 0.041841295205586757)` kg, width
`2.1665271335291614e-7 kg`, with useful feasible and excluded neighbors. It uses
30 mass subdivisions, 76 envelope calls (15 tighter repeats), 8,566 parent
deliveries and 4,169 cumulative assay subdivisions. The latter are across calls;
the per-call 4,096 cap remains unchanged. The full combined band is excluded using
8 mass subdivisions, 17 envelope calls and 1,297 parent deliveries.

The genuinely two-dimensional fixture has beta columns `(1,2,.5,3,1)` and
`(2,1,3,.5,2)` on the five knots, independent rank two and strictly positive
throughout the domain. Both coordinates vary and affect the result. Monotonicity
therefore proves integrated extrema at the corresponding lower/upper corners for
this fixture only. Its independent combined solute/TDS reference qualifies to
`1.3542175292952097e-7 kg`, with 35 mass subdivisions, 80 envelope calls and
400 parent deliveries. Widening the box and tightening constraints are checked
against the independently nested reference sets, rather than requiring independently
terminated numerical endpoints to be literally nested.

Its independently bracketed feasible interval is `[0.04630304546350704, 0.08]` kg.

A manufactured C1 family with knot intercepts `(-5,-1,-4,0,-5)` and positive
constant assay beta 0.2 proves assay monotonicity while producing nonmonotone
suffix TDS. Its 12-percent upper constraint has two disconnected robust components.
Independent intervals are `[0.009,0.019934693321819547]` and
`[0.03627222420185975,0.05787028027342643]` kg.
The result retains both, with maximum coalesced boundary extent
`1.3542175292952097e-7 kg`, 59 mass subdivisions, 137 envelope calls and
411 parent deliveries. A separate noncollapsed analytical constant family recovers
a three-milligram-wide mass component `[0.035,0.035003]` kg without bridging its
two unresolved boundary neighborhoods.

Additional tests cover C0 and collapsed C1/C2 exact-parent reductions; analytical
constant full/empty/interval sets; combined and conflicting constraints;
anchor-only solute, domain endpoints, knot roots, zero-width positive-suffix TDS
queries, equalities, exact flat prefixes, tangencies, narrow components,
unrepresentable interiors, near-equal logits, saturation and underflow. Rounded
numerical zeros never establish exact identities. Parent results preserve isolated
root and partial-component semantics.

Expected unresolved cases include forced global/nested budget limits, tangency,
nonstructural nearly flat equality, underflow-scale targets and unrepresentable
interiors. Injected parent exceptions, quadrature warnings, excessive/nonfinite
allowances, envelope-bound quadrature failure and early/late envelope API exceptions
retain every unclassified mass. Earlier classifications survive a later failure.
Every actual delegated delivery is counted even when an envelope discards its
return via an injected exception; unavailable nested audit totals are explicitly
flagged incomplete. Remaining global budget is asserted at each envelope call,
including tighter repeats; point dispatch is stopped before an excess delivery.
Collapsed delegation also reserves its complete worst-case refinement budget before
starting, declining unsafe dispatch without a delivery. The reservation is separately
labeled, because the unchanged parent reports maximum rather than cumulative
iterations. It totals 12,160 across the focused run, at most 1,152 per query;
new mass splits plus the reservation never exceed the per-query 2,048 cap.

Contract checks cover immutable records, identities, rights, units, inactive
fields, strict JSON, deterministic independent queries, no file/fitting access,
exclusive private output, malformed and symlink-loop inputs, and sanitized CLI
argument errors. Numerical reference mathematics is not independent reviewer approval.

## Reproduction and QA

Existing Python 3.12.3 / NumPy 2.5.3 / SciPy 1.18.1 / pytest 9.1.1 environment;
No project dependency or lock changes. Packaging used an existing build frontend
and its ordinary isolated setuptools backend; initial unavailable-frontend/backend
probes are retained in the logs and did not modify the test environment. One numerical worker and one BLAS thread. The clean
local normal baseline passed **5,253 tests, 64 skipped, 60 deselected** in
1037.60 seconds. The baseline emits only the existing synthetic Visualizer
fixture's development-salt warning. Hosted baseline checks on the exact reviewed
main were also green. No unrelated baseline repair was made.

```bash
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
export PYTHONPATH=.
python -m pytest -q \
  tests/test_conditional_tail_robust_stopping.py \
  tests/test_conditional_tail_envelope.py \
  tests/test_conditional_tail_stopping.py \
  tests/test_conditional_tail_delivery.py \
  tests/test_conditional_tail_training.py \
  tests/test_pannusch_conditional_tail_delivery.py
python -m pytest -q -m "not slow and not live and not gpu and not external_data"
ruff check puckworks/ tests/
mypy
mypy --check-untyped-defs puckworks/analysis/conditional_tail_robust_stopping.py
python -c "from puckworks.registry import run_all_gates; run_all_gates()"
python -m pytest -q -m "scientific_baseline and not live and not gpu and not external_data"
python -m puckworks.analysis.conditional_tail_robust_stopping --synthetic
```

The remaining maintained checks use these unchanged entry points:

```bash
python -m puckworks.paper3.registry_artifacts --verify
python -m puckworks.paper3.build verify
python -m puckworks.paper3.availability --verify
python -m puckworks.paper3.corpus --verify
python -m puckworks.paper_a.claim_coverage
python -m puckworks.paper_b2.claim_coverage
python -m puckworks.paper3.claim_coverage
python -m puckworks.analysis.lateral_coupling_discrimination --verify
python -m puckworks.paper3.evidence_graph --reconcile
python -m puckworks.paper3.evidence_graph --verify
python -m puckworks.paper3.evidence_graph --reconcile --strict --scope paper3
python -m puckworks.paper3.evidence_graph --reconcile --strict --scope all
python -m puckworks.statusdoc --verify
python -m puckworks.paper3.archive create-archive --out "$PRIVATE_ARCHIVE_A"
python -m puckworks.paper3.archive create-archive --out "$PRIVATE_ARCHIVE_B"
cmp "$PRIVATE_ARCHIVE_A" "$PRIVATE_ARCHIVE_B"
python -m puckworks.paper3.archive verify-archive "$PRIVATE_ARCHIVE_A"
python tools/readme_governance.py verify
python tools/update_readme_pulse.py --verify
```

Packaging builds wheel/sdist from a tracked-only export outside the checkout,
checks both with `python tools/packaging_check.py "$PRIVATE_DIST"`, rebuilds the
wheel from the sdist and installs the wheel outside the checkout with existing
numerical dependencies. Its public registry gates and synthetic CLI are checked
from that installation. The required saved-mode C2 combined-band CLI is quiet,
uses private JSON files and creates an exclusive mode-0600 result. No native CFD
packaging demonstration or historical scientific workflow is replayed.

Full routine logs, case accounting and generated products stay outside Git.
No historical prepare/develop/fit/predict/freeze/score workflow is replayed.
Fits=0, new empirical outcome joins/scores=0, native EWP runs=0. Normal repository
QA is separate from the bounded new model-query characterization.

## Actual local QA results

| Check | Result |
|---|---|
| Required focused suite | 239 passed; 106.82 s |
| Maintained normal selection | 5,300 passed, 64 skipped, 60 deselected; 1090.85 s |
| Ruff; maintained mypy; direct new-module mypy | PASS; 19 maintained files and the new module checked |
| Registry gates | PASS: 65 passes, 1 existing acknowledged exception |
| Scientific-baseline selection | 5 passed, 7 skipped, 5,412 deselected; 175.34 s |
| Registry artifacts, paper build, availability, corpus, claim coverage A/B2/3, lateral artifacts | PASS; no stale or unaccounted artifacts |
| Evidence reconcile/verify and both strict scopes | PASS |
| Status, README governance and generated pulse | PASS; unchanged generated status current |
| Existing paper archive reproducibility and member verification | PASS; two identical 159-member archives |
| Wheel/sdist inventory and sdist-to-wheel rebuild | PASS; no private/untracked material; API bytes match tested source |
| Installed-wheel public registry gates and synthetic CLI | PASS; synthetic result matches checkout |
| Required synthetic CLI and private saved-C2 CLI | PASS; quiet saved mode, exclusive mode-0600 output |
| Python 3.10 syntax, whitespace, Markdown links, secret/path and exact-scope checks | PASS |
| Frozen parent/model/history bytes, owner checkouts, EWP identity/pins | PASS |

All 25 sequential remaining-QA commands returned zero. The normal selection's
single development-salt warning matches the clean baseline; the scientific skips
and existing registry exception do not represent new evidence or changed gates.
No shell or JSON source is added or changed; strict JSON, units and boundary
behavior are tested through the API/CLI contracts. Paper archive verification
concerns unchanged historical evidence, not a new scientific publication bundle.
Final closeout changes only this report, schema wording and the three planning
entries; the tested API/test hashes above are unchanged.

## Author review and bounded correction

Review covered quantified constraint conjunction, complete continuous mass coverage,
point-root versus feasible-interval semantics, normalization/coalescing, derivative
and residual allowances, global/nested guards, rights, preservation and privacy.
The argument parser was made quiet even for malformed arguments that argparse
would otherwise echo. Result serialization includes internal numerical conventions
as well as all caller options.

Author review found a real strict-serialization defect for a finite manufactured
model with extreme mass scales: derivative-bound arithmetic overflow correctly
retained the whole domain as unresolved, but stored an infinite diagnostic allowance.
A regression reproduced the JSON failure; the correction records an allowance only
after its finiteness check. The regression now returns a finite, strictly serialized
unresolved result without a parent delivery. The interrupted full-suite attempt had
1,323 passes and 32 skips with no assertion failure; it is retained as superseded,
not reported as accepted QA. The corrected 238-test focused run passes. No threshold,
cap, model, parent source or difficult acceptance case was weakened.

The final budget review added the conservative point-refinement reservation and
verified rejection before dispatch plus unchanged point results when the reservation
fits. A second full-suite attempt was superseded after 1,508 passes and 43 skips
without assertion failures, so the maintained suite is rerun on the final source.
The final focused suite passes 239 tests in 106.82 seconds.

The task's final focused accounting has 63 API invocations over 43 distinct
model/box/query cases, plus three explicit nominal/corner point comparators and
one additional synthetic CLI case: **47 distinct characterization cases**, below
128. Repeats and option/failure variants are counted as invocations, not new
empirical observations. Across those 63 API invocations: 517 mass splits, 1,134
envelope calls (125 tighter repeats) and 15,180 actual parent deliveries. Maximum
per-query use is 59 mass splits, 137 envelope calls and 8,566 deliveries, below
all hard limits. Completed nested audits report 4,936 assay subdivisions; the two
injected lost envelope returns explicitly mark that nested total incomplete.
Every delivery remains accounted for even in those injections. Five injected
parent failures and one saturated-profile numerical rejection account for the six
failed parent evaluations; all are explicit unresolved outcomes. The saturated
positive-logit case retains its previously qualified region. No ordinary mandatory
case has an unexpected unresolved neighborhood or misses its requested resolution.

The first 42-test run passed in 61.88 seconds. Review coverage/metadata/privacy
additions produced 237-test focused passes in 106.69 and 107.60 seconds before the
final overflow regression and correction. New characterization remains bounded;
normal repository QA and inherited regression cases are separate. All failed and
superseded routine logs remain outside Git.

## Handoff boundary

The capability is research-only and conditional on the unchanged model and
caller-supplied assay set. Numerical resolution is not machine stopping accuracy
or empirical predictive robustness. Source-derived outputs retain Pannusch/Schmieder
CC-BY-NC-3.0 attribution separately from first-party code licensing. All predecessor
scientific dispositions remain unchanged. No production adoption, merging,
auto-merge, release, activation, default/lock change, EWP implementation or successor
is authorized. PHYSICAL_VALIDATION=NOT_ESTABLISHED.
