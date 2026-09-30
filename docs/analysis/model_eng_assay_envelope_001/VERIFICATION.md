# Numerical verification and ordinary repository QA

MODEL-ENG-ASSAY-ENVELOPE-001 — G0 / NO_GOVERNING_PHYSICS_CHANGE / RESEARCH_ONLY.

**ENGINEERING_CAPABILITY_VERIFIED.** Mandatory numerical cases, local repository
QA and ordinary author review pass, including the unchanged frozen-C2 interior
minimum and a genuinely two-dimensional assay box. Hosted CI is reported
separately on the draft PR. Independent reference mathematics is not independent
reviewer approval. Merge and production adoption are not authorized.

## Identities, drift and preservation

Fetched mains equal the reviewed identities; no subsequent main commits exist:

| Repository | Commit | Tree |
|---|---|---|
| Puckworks | `e33153b22036e2900bfd35873bba0808b245cb2e` | `e0fd76fca849a4996cab0806ec68ae1a8aae061a` |
| EWP, read-only | `f15a417cbf3c7528ac734537bb844cab6dc98287` | `a36a006be6d9bb3fb4516ec78ed4299d2e2529b8` |

The short check inspected recent/related PRs and issues and every open PR.
Puckworks #257 concerns publishing; #264/#129/#128 change Actions dependencies.
EWP #117 is a historical laboratory evidence audit and #130 changes Actions.
None implements or supersedes this capability. No broader novelty or successor
search was performed. Puckworks #301, #288, #296 and EWP #194 are merged;
their supplied publication heads were verified. Frozen OPEN/UNMERGED prose is
historical and unchanged.

The evaluated MASS-DELIVERY-006 producer remains
`0f130d4f2dfca552e56cd7d7e96bb73b8c50f421`, tree
`9f6b5346ea7cfceef4d014c80b235818eee0a23f`. Publication heads do not replace it.
EWP's historical handoff and consumer pin are unchanged. Work uses the isolated
branch `model-eng/assay-envelope-001`, preserving both owner checkouts.

Hash comparison checks all 2,438 baseline Puckworks tracked files: only the
three authorized planning documents differ. All 2,435 others, including the
forward/stopping runtime, existing tests, frozen models and historical science,
are byte-identical. All 1,946 files in the owner's EWP checkout, 2,438 files in
the reviewed EWP checkout, and 2,091 files in the owner's Puckworks checkout
are unchanged. Source/test content identities for the tested implementation:

- Envelope API SHA256: `98845895cb4fd032690d5b1c457e719d68b14768b9da68b6501a20bdd32e8b3a`.
- Envelope tests SHA256: `5ec232c9a85a7b0dfeda65370cfd87a32ffae88259155cff8f655cc4d54f8cad`.

The publication commit/tree and its hosted checks are recorded in the draft PR,
without pretending this document can contain its own final commit identity.

## Numerical references and actual results

The tests independently integrate the stated affine-logit model with fsum
conditioning, adaptive quadrature and segment bisection/refinement, without
calling the parent's integration kernel. Analytical solutions and convexity
arguments establish extrema; corner probes and grids are not global oracles.
Runtime mathematical and floating-point arguments are in the [README](README.md).

At the mandatory C2 query, m1, m2 and q1 are the saved means,
q2 is `[0.0931364597, 0.1830244866]`, the anchor is
`0.012921191111111112 kg` and the stop is `0.04104270828628944 kg`.
Independent recomputation gives:

| Input | Solute kg | Reference allowance kg |
|---|---:|---:|
| Lower q2 endpoint | 0.0016654705046629595 | 3.85e-17 |
| Interior q2 = 0.1381981039733334 | 0.0016180687390461369 | 3.80e-17 |
| Upper q2 endpoint | 0.0016610729567656775 | 3.85e-17 |

At both assay endpoints every knot logit is negative, hence the logit remains
negative over their Cartesian interval and all queried mass segments. Therefore
`S''(q2) = integral beta_2^2*c*(1-c)*(1-2*c) db > 0`: beta is nonzero on positive
mass support. Endpoint derivatives are -0.0021570853815816985 and
0.0018835027232413722 kg per kg/kg. Independent derivative bracketing finds the
unique minimum; its derivative residual is 1.73e-18. Both endpoints exceed
0.001640 kg and the feasible interior witness does not. Rounded historical
numbers are secondary regression checks, not the oracle.

At the default tolerance the API returns:

| Extremum | Lower kg | Upper kg | Gap kg |
|---|---:|---:|---:|
| Minimum | 0.0016179778034867635 | 0.0016180688137890403 | 9.101030227685014e-8 |
| Maximum | 0.0016654705046620756 | 0.0016655137491818298 | 4.324451975418892e-8 |

The minimizing witness has q2=0.13825603570253905 and parent prediction
0.0016180688137881589 kg (allowance 8.811782166088303e-16 kg). The maximizing
witness is the lower q2 endpoint, with parent prediction
0.0016654705046629597 kg (allowance 8.837948231001882e-16 kg).
Both are common inputs throughout the complete query. There are **52
subdivisions, 107 parent evaluations, 105 bound evaluations, 53 retained
partition boxes and zero failed evaluations**. The overall outer delivery
interval is the minimum lower bound to the maximum upper bound.

An explicitly tighter `1e-9 kg` request also qualifies, with minimum gap
8.818019931865901e-10 kg and maximum gap 6.757415313071725e-10 kg, using
84 subdivisions and 171 parent evaluations. No budget or tolerance changed
automatically.

Manufactured interior tests have constant center logit -2. On the two mass
segments `[.02,.04]` and `[.04,.06]`, beta knot vectors are `(-1,1,-1)` for q1
and `(-1,-1,3)` for q2, with mean assays (.5,.5) and intervals [.4,.6]. Their
weighted integrals vanish and their functions span two dimensions. All logits
remain negative, so the integrated Hessian is positive definite: the center is
the unique global minimum, and convexity places a maximum at a corner. The
one-dimensional restriction supplies the 1D proof; changing the intercept to
+2 supplies a strict interior maximum. These are manufactured model coefficients,
not transcriptions of fitted model artifacts.

| Manufactured query | Minimum enclosure kg | Maximum enclosure kg | Splits / parent calls |
|---|---|---|---:|
| C1 interior minimum | [0.004768062846840939, 0.004768116880886081] | [0.004773447020639743, 0.004773490646806904] | 19 / 41 |
| C2 interior minimum | [0.004768020258249906, 0.004768116880886081] | [0.004811716498081039, 0.0048117883638327036] | 428 / 861 |
| C2 interior maximum | [0.03518821163616755, 0.035188283501920506] | [0.035231883119112364, 0.03523197974175289] | 428 / 861 |

Every listed case qualifies at the default gap. The wider manufactured
two-dimensional [.3,.7] box also qualifies (557 subdivisions, 1119 parent calls).
Input widening is checked through valid extremum-enclosure relations; separately
terminated finite-gap outer intervals need not be strictly nested.

Other coverage includes C0 and collapsed-box exact-parent reductions; C1/C2
constant profiles; provably monotone corner extrema; mixed coefficient signs
and within-segment sign crossings; knot/partial/domain-boundary/zero-width
queries; near-equal logits, saturation, underflow and adjacent floats; strict
JSON, units, basis, fields, immutability and privacy; witness feasibility and
independent recomputation; deterministic repeatability and independent queries.

Explicit unresolved cases use zero/small subdivision or point budgets, a
below-allowance resolution request and an adjacent-float assay interval without
a representable split. A limit during the second child retains its complete
parent box and counts the attempted subdivision. Injected parent exceptions,
warnings, nonfinite/excessive allowances and failed added quadrature retain
unresolved status and failure counts. The universal delivery enclosure remains
available on numerical failure; failed evaluations never qualify a result.

Exact unresolved stress scope (all use the manufactured C2 interior fixture
and mass window `[0.02,0.06] kg`, except for the stated assay-box changes):

| Assay set / controls | Termination |
|---|---|
| `[.4,.6]^2`; zero subdivisions | `SUBDIVISION_LIMIT` |
| `[.4,.6]^2`; 0, 4 or 6 parent calls | `PARENT_POINT_EVALUATION_LIMIT` |
| `[.4,.6]^2`; `1e-16 kg` gap, three subdivisions | `SUBDIVISION_LIMIT` |
| `[.5,nextafter(.5,1)]^2`; `1e-25 kg` gap | `NO_REPRESENTABLE_OR_INFLUENTIAL_ASSAY_SPLIT` |
| Collapsed (.5,.5); `1e-25 kg` gap | `PARENT_ALLOWANCE_RESOLUTION_LIMIT` |
| `[.4,.6]^2`; injected parent exception/warning or invalid allowance | Parent numerical failure / unqualified point |
| `[.4,.6]^2`; injected nonfinite new quadrature | `ENVELOPE_NUMERICAL_FAILURE` |

## Reproduction, execution budget and QA

Existing Python 3.12.3 / NumPy 2.5.2 / SciPy 1.18.1 / pytest 9.1.1 environment;
no dependency installation or upgrade. One worker, one BLAS thread. Full logs,
temporary numerical accounting and routine build/archive products remain outside
Git. No bulk atlas or new evidence framework is added.

The final focused accounting records **40 distinct API model/box/query cases**
and 50 API invocations: 2,559 attempted subdivisions and 5,286 parent point
evaluations. Four parent failures and one bound failure are deliberately
injected, counted and asserted unresolved. The direct envelope-integration
test adds one case and the synthetic/private CLI paths add two, for **43
distinct numerical cases**, below 256. Maximum observed per-query use is
557 subdivisions and 1,119 parent calls, below the unchanged hard caps.
The three focused executions total 116.42 s, conservatively including their
predecessor regression time; reference recomputation and the additional CLI
smoke add under one second. New characterization is below two minutes and the
30-minute limit. Full repository baseline/regression QA is separate.

```bash
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
export PYTHONPATH=.
python -m pytest -q \
  tests/test_conditional_tail_envelope.py \
  tests/test_conditional_tail_delivery.py \
  tests/test_conditional_tail_stopping.py \
  tests/test_conditional_tail_training.py \
  tests/test_pannusch_conditional_tail_delivery.py
python -m pytest -q -m "not slow and not live and not gpu and not external_data"
ruff check puckworks/ tests/
mypy
mypy puckworks/analysis/conditional_tail_envelope.py
python -c "from puckworks.registry import run_all_gates; run_all_gates()"
python -m pytest -q -m "scientific_baseline and not live and not gpu and not external_data"
python -m puckworks.analysis.conditional_tail_envelope --synthetic
```

The maintained generated-artifact commands from `.github/workflows/generated-artifacts.yml`
and strict evidence-graph commands from `.github/workflows/paper3-evidence.yml`
are used unchanged. Archive creation/verification writes outside Git. No historical
prepare, develop, fit, predict, freeze or score command is rerun.

Maintained generated/claim/evidence commands actually executed:

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
python tools/readme_governance.py verify
python tools/update_readme_pulse.py --verify
python -m puckworks.paper3.archive create-archive --out /tmp/envelope-a.tar.gz
python -m puckworks.paper3.archive create-archive --out /tmp/envelope-b.tar.gz
cmp /tmp/envelope-a.tar.gz /tmp/envelope-b.tar.gz
python -m puckworks.paper3.archive verify-archive /tmp/envelope-a.tar.gz
```

Use fresh caller-controlled archive names outside Git; the two archives match
byte-for-byte and member verification passes. No generated content delta is
needed. There are no shell or JSON source-file changes; runtime JSON rejection
is tested. Python syntax, Markdown links, changed-path scope and private-path/
secret-signature checks pass.

| Check | Clean baseline before code changes | Candidate |
|---|---|---|
| Maintained normal suite | 5179 passed, 65 skipped, 60 deselected; 1013.21 s | 5252 passed, 65 skipped, 60 deselected; 1030.07 s |
| Focused reproduction | 119 predecessor tests passed; 13.30 s | 192 passed; 42.88 s |
| Ruff / maintained mypy | PASS / 19 files pass | PASS; new module also passes direct mypy |
| Registry | 65 PASS, 1 ACKNOWLEDGED_EXCEPTION | Same |
| Scientific baseline | 5 passed, 7 skipped; 175.70 s | 5 passed, 7 skipped; 175.62 s |
| Generated/claim/status and strict evidence graphs | PASS | PASS |
| Deterministic archives/member verification | PASS | PASS |
| README governance and generated pulse | PASS | PASS |

The baseline emits one existing development-salt warning from a synthetic
Visualizer fixture. The candidate also emitted a SciPy BDF `invalid value
encountered in subtract` warning in the unchanged
`test_smrke2024_envelope.py::test_shape_morphology_is_fast_rise_then_plateau`:
its assertions passed. That warning is retained, not suppressed or repaired in
this scope. The new envelope tests emitted no warning. No production harvest
occurred. The first 72-test new
numerical run passed in 30.64 s; the first full focused run passed 191 tests in
42.90 s. Author review then added directed rounding at both TDS-conversion
operations, reported Taylor arithmetic in the allowance maximum, sanitized
symlink-loop path failures, and tested a budget stop during the second child.
The final focused suite has 73 new tests plus 119 unchanged predecessor tests.
An initial static typing check required two list annotations; that check and
all execution logs are retained. No numerical failure was suppressed or
acceptance criterion changed; no unrelated baseline repair was made.

## Claim and authorization boundaries

Task model fits = 0; new empirical outcome joins/scores = 0; native EWP runs = 0.
Query optimization counts above are numerical work, not model fitting.
Ordinary author code/numerical review is separate from hosted CI and any external
review. The draft PR reports its live publication-head checks; no external
reviewer approval is claimed. The five required repository contexts are
`quick (3.10)`, `quick (3.12)`, `verify-generated`, `paper3-scope-strict` and
`all-scope-strict`. No extra scientific pre-score gate applies to this G0 query.

No predecessor adequacy claim is upgraded. Source-derived results retain
Pannusch/Schmieder attribution and CC-BY-NC-3.0 separately from first-party code.
These synthetic cases add no observed shots or independent validation panel.
No calibrated assay-error model, real-coffee guarantee, production integration,
merge, auto-merge, release, laboratory operation or successor is authorized.

PHYSICAL_VALIDATION = NOT_ESTABLISHED. RESEARCH_ONLY.
CONDITIONAL_ON_THE_UNCHANGED_MODEL_AND_CALLER_SUPPLIED_ASSAY_SET.
