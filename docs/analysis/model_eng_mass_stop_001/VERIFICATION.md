# Numerical verification and repository QA

MODEL-ENG-MASS-STOP-001 — G0 / NO_GOVERNING_PHYSICS_CHANGE / RESEARCH_ONLY.
**ENGINEERING_CAPABILITY_VERIFIED.** Local numerical/software QA and author
review pass. Hosted CI and external review are reported separately in the draft
PR; no external reviewer approval is claimed here. No merge or production adoption
is authorized. Numerical qualification does not establish physical validation.

## Baselines and short drift check

Both fetched default branches equal the reviewed selection identities:

| Repository | Commit | Tree |
|---|---|---|
| Puckworks | `d9924186a0daceacd083e1d3f2edcc9749d85d2d` | `c46e59f2c4cbedf772196cd4d43bcc4445815b61` |
| EWP, read-only | `f15a417cbf3c7528ac734537bb844cab6dc98287` | `a36a006be6d9bb3fb4516ec78ed4299d2e2529b8` |

No intervening default-branch commits exist. Recent, open and related PRs/issues
were inspected in both repositories, together with current source paths. Recent
Puckworks #292/#294/#297–#300 and EWP #198/#200 provide forward delivery,
adaptation or species work, not the complete inverse API. Open publication,
dependency and unrelated science items do not supersede this capability.
The legacy mass-delivery stopping methods evaluate a supplied stop mass.

GitHub verifies predecessor Puckworks [#288](https://github.com/trbrewer/puckworks/pull/288)
and EWP [#194](https://github.com/trbrewer/espresso-whole-pull/pull/194) as merged.
Their publication heads are respectively
`c5f0df7490ab92c2c0868ea2b0d8e05fced68e94` and
`9ec7267bb297dfb8c1ccec611cc40ca79aae9ff2`. The evaluated producer remains
`0f130d4f2dfca552e56cd7d7e96bb73b8c50f421`, tree
`9f6b5346ea7cfceef4d014c80b235818eee0a23f`; later publication heads do not replace it.
Frozen historical OPEN/UNMERGED prose was not edited or used as live lifecycle authority.

Implementation uses an isolated `engineering/model-eng-mass-stop-001` worktree.
The implementation commit is `4dfb1c865f00f45dba2c62804791d9f270d33f5b`, tree
`659e95c450816a5fe51c1b921ea16aac1502cd77`. The full normal suite ran against
that exact tree before committing it. The subsequent closeout changes only
planning and this verification report; the publication head/tree and hosted CI
are recorded in the draft PR body, without pretending a document can contain
its own final commit hash. Implementation/test content identities are:

- API SHA256: `6c8d25a062fd8175d8697cc9dd5e04b32840f90dce116a3c708a5f3d4a85f96a`.
- Tests SHA256: `c590fae7670995303a0e0905ebf46f7e06449b6589641e48c20fc7d19531116d`.

The owner's existing checkouts and EWP files are unchanged. Parent runtime SHA256
is `4fb20dd42e0ed7d5a758f549d616131988a1dab05ddc49b9253441606f155e33`.
The C0/C1/C2 canonical model identities remain:

| Arm | Canonical model SHA256 |
|---|---|
| C0 | `d486067fc8e8c381860f2473bfe0d14176f0a5abc3f8fed7cd75525923d82d86` |
| C1 | `43b08545dd7adc0a63d2dba696b4e29864385d3e25cb9676989d1c2374ff1145` |
| C2 | `960e0c7dd37d3ba876f95a44c00c69f222e53c022a641e4b092a2af686fb9516` |

## Numerical comparators and coverage

The focused tests use analytical constant concentrations, independent adaptive
quadrature of the stated affine-logit sigmoid with segment refinement, and
round trips through the unchanged parent observer. The reference enumerator
finds derivative roots by numerical bracketing rather than the implementation's
analytic logit inversion. A grid is not used as the completeness oracle.

All 31 synthetic feature-mean/marginal-corner states across C0/C1/C2 are exercised
with three queries each (93 frozen-model state/query cases). These are numerical
references, not calibration, model ranking, experimental replicates or holdouts.
Manufactured cases cover constant, rising, falling and rise/fall profiles;
simultaneous constraints; empty/full/point ranges; anchor zero delivery; roots at
knots and query endpoints; singleton equality solutions; flat prefixes;
tangencies; narrow components; near-equal logits; saturation and underflow;
unresolved overlapping constraints; and parent numerical failures.

Contract tests cover units/basis, finite numbers, booleans, invalid domains,
zero-width TDS suffix rejection, unexpected and duplicate fields, immutability,
serialization, identity/rights/flag propagation, deterministic independent
queries, constraint intersection, quiet saved-state CLI, exclusive creation and
operation with file/fitting access blocked. Repository test fixtures block network
connections in the offline lane. No protected source access is needed.

Fewer than 200 distinct deterministic state/query cases are used; there is no
standalone exploratory sweep. Execution uses one worker and one BLAS thread,
at most 128 refinement iterations per boundary. Focused characterization is in
seconds, below the 30-minute/512-case bounds, and adds no state archives or bulk
characterization artifacts. Normal repository QA is separate. Task fits=0,
outcome joins/scores=0, native EWP runs=0; no dependency changes.

## Frozen C2 disconnected-range regression

Synthetic early values:
`(0.0030670000000000003, 0.0032029999999999997, 0.2974564005, 0.0931364597)`;
allowed stops `[0.007, 0.06971540000000001]` kg; suffix TDS <= 4.9 percent.
This lies within marginal feature bounds and asserts no joint experimental support.

Independent quadrature/bracketing recomputes crossings near
`0.04618171404338526` and `0.06408384803290236` kg. The API returns **two**
components: the lower query endpoint to the first crossing, and the second
crossing to the upper query endpoint. Initial measured bracket widths are
approximately `2.10e-12` and `2.00e-12 kg`, both below `1e-8 kg`.
Copied expected numbers are only secondary regression checks; the numerical
reference is recomputed from the unchanged artifact.

At a numerically constructed TDS tangency, uncertainty remains explicit. A
distinguishable narrow island near that extremum is recovered. At constant logit
`-20`, the inherited absolute allowance divided by very small concentration
prevents a `1e-8 kg` boundary qualification; the query returns unresolved and
retains its qualified portion. Neither case changes the forward model.

## Reproduction and recorded QA

Existing environment: Python 3.12.3, NumPy 2.5.2, SciPy 1.18.1, pytest 9.1.1.
No packages were installed or upgraded. From the candidate checkout:

```bash
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
export PYTHONPATH=.
python -m pytest -q \
  tests/test_conditional_tail_stopping.py \
  tests/test_conditional_tail_delivery.py \
  tests/test_conditional_tail_training.py \
  tests/test_pannusch_conditional_tail_delivery.py
python -m pytest -q -m "not slow and not live and not gpu and not external_data"
ruff check puckworks/ tests/
mypy
python -c "from puckworks.registry import run_all_gates; run_all_gates()"
python -m pytest -q -m "scientific_baseline and not live and not gpu and not external_data"
python -m puckworks.analysis.conditional_tail_stopping --synthetic
```

The maintained generated/claim commands are those in
`.github/workflows/generated-artifacts.yml`; strict evidence-graph commands are
in `.github/workflows/paper3-evidence.yml`. Archive creation/verification runs
outside Git. No historical prepare/develop/fit/predict/freeze/score command runs.

Before any implementation, the clean baseline passed:

| Check | Result |
|---|---|
| Maintained normal suite | 5108 passed, 65 skipped, 60 deselected; 1005.53 s |
| Predecessor focused tests | 48 passed |
| Registry | PASS=65, ACKNOWLEDGED_EXCEPTION=1 |
| Ruff / maintained mypy | PASS / 19 source files pass |
| Frozen scientific-baseline selection | 5 passed, 7 skipped, 5221 deselected |
| Generated artifacts, claim coverage, status truth | PASS |
| Strict evidence graphs, both scopes | PASS |
| Deterministic archives and member hashes | PASS |

The baseline normal suite emits one existing development-salt warning from a
synthetic Visualizer fixture. It does not run a production harvest.

Current focused candidate verification: **119 passed in 13.54 s**. Ruff and
additional direct typing of the new module pass. The first test run exposed an
independent-reference bug: exact zeros at knot endpoints were omitted by a
strict sign-product crossing test. The reference was corrected to retain exact
zero endpoints; analytical expected roots and the production enumerator already
agreed. Failed development logs remain outside Git.

Author review found and corrected an adjacent-float edge case: a rounded
midpoint could equal a root endpoint and incorrectly classify an open interval.
The explicit `NO_REPRESENTABLE_INTERIOR_MASS` regression now passes; retained
points beside unresolved territory are partial rather than asserted isolated.
The superseded candidate normal-suite run was interrupted for this correction
after 1240 passes and 32 skips, with no test failure; its full log is retained.
This is not the accepted candidate normal-suite result.

Accepted local candidate QA:

| Check | Result |
|---|---|
| Required focused reproduction | 119 passed; 13.54 s |
| Maintained normal suite | 5179 passed, 65 skipped, 60 deselected; 1003.70 s |
| Registry | PASS=65, ACKNOWLEDGED_EXCEPTION=1 |
| Ruff / maintained mypy / direct module typing | PASS / 19 files pass / 1 file passes |
| Frozen scientific-baseline selection | 5 passed, 7 skipped |
| Generated artifacts, claim coverage, status truth | PASS |
| Strict evidence graphs, both scopes | PASS |
| Deterministic archives and member hashes | PASS |
| Source syntax, Markdown links, changed-path and secret/private-path checks | PASS |
| Frozen predecessor preservation | 25 checked runtime/test/evidence files byte-identical |
| EWP | Clean original checkout/head preserved; no file edits or native runs |

The normal suite has the same single development-salt warning as baseline.
Registry and scientific-baseline evidence is reused after the isolated inverse
correction because their protected producers and artifacts are unchanged. The
new inverse's focused tests, full normal suite, lint and typing were rerun after
that correction. No failures were suppressed and no unrelated repair was made.
There are no shell or JSON source-file changes; strict runtime JSON behavior is
covered by the focused tests. All full logs and routine archive products remain
outside Git; new public capability/test/documentation files total under 100 KiB.

Author review covered enumeration, anchor/units, allowance propagation, clipping,
equality/tangency/flat/adjacent-float behavior, source privacy, and preservation.
This is ordinary G0 code review, not independent scientific review. The current
repository rules require `quick (3.10)`, `quick (3.12)`, `verify-generated`,
`paper3-scope-strict`, and `all-scope-strict`; the draft PR's live checks and
closeout body record their actual publication-head results. Human review remains
available through the ordinary draft PR. No separate scientific stage or
independent-evidence framework applies.

Handoff: retain the reusable inverse API with all resolved components and explicit
unresolved regions. Ordinary analytical/reference topology, including the frozen
C2 two-component case, qualifies. Near tangencies, overlapping boundaries, flat
threshold equalities without an algebraic identity, very small concentrations,
and unrepresentable interiors can remain unresolved. These numerical limits do
not change historical predictive adequacy or authorize physical control.

PHYSICAL_VALIDATION=NOT_ESTABLISHED; RESEARCH_ONLY; SOURCE_INTERNAL;
TARGET_EXPOSED. First-party tests/code and source-derived CC-BY-NC-3.0 rights
remain distinct. No merge, auto-merge, production adoption or successor is authorized.
