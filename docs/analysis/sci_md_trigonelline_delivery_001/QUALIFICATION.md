# Qualification and completion record

Local qualification: **PASS**. Scientific comparison: **TRIGONELLINE_MASS_SHAPE_EARNED**.
The comparison completed with a qualified portable research predictor; task
outcome is SUCCESS. This statement is separate from physical validation,
which remains NOT_ESTABLISHED. RESEARCH_ONLY; NO_GOVERNING_PHYSICS_CHANGE.

| Check | Baseline | Candidate |
| --- | --- | --- |
| Puckworks full routine suite | 5033 passed, 34 skipped, 0 xfailed | 5058 passed, 34 skipped, 0 xfailed |
| EWP full routine suite | 1635 tests, 20 skipped, no failures/errors | 1635 tests, 20 skipped, no failures/errors |
| New focused suite | Not present | 25 passed, no skips/xfails |
| New plus unchanged caffeine focused suites | Not applicable | 61 passed, no skips/xfails |
| Clean-checkout focused suite | Not applicable | 25 passed, no skips/xfails |
| Scientific-baseline workflow selector | Preserved | 5 passed, 5087 deselected |
| Critical-module coverage floor | 70% required | 80% |
| Saved-model reproduction | Not applicable | 192 slots exactly equal; maximum difference 0 |
| Retained report reproduction | Not applicable | Exact retained score equality; no rescore |

The Puckworks full suite ran at reviewed scientific head
`de31200f272711ca6b2e9fc5dc7c4881c406ab56`. Clean-checkout reproduction ran at result
publication head `0e8e4a527fabd0d92199da376490f6a47f123f1a`.
All 53 frozen code/protocol hashes and 646 pre-score artifacts remain unchanged
in the later G0 reporting commits. All 653 private run files were unchanged
by reproduction against read-only evidence. No permitted floating-point
variation was needed: predictions and states reproduced exactly.

Both full Puckworks runs had the same two existing warnings. Every Puckworks
skip path, line and reason matches BASELINE.json exactly. EWP skip prerequisites,
source files and pinned environment are unchanged; its 20 reasons remain those
listed in BASELINE.json. No test was weakened, newly skipped or xfailed.
The independent reviewer separately ran 23 tests and deliberately deselected
two fitting tests; these are deselections, not skips or a full-suite claim.

Registry gates, ruff, the current mypy scope, generated status/registry/paper
artifacts, all three claim-coverage commands, evidence reconciliation in both
strict scopes and deterministic archive creation/verification pass. EWP source,
static, historical-baseline, active-change, release and task-applicable boundary
checks pass, as do shell/JSON syntax and secret/path/generated-product checks.
Exact commands, identities, durations and log hashes are in QUALIFICATION.json.

The protected-file comparison preserves all 2241 original Puckworks files
other than the expressly allowed one-line CHANGELOG addition. This includes
all accepted MASS/CAFFEINE code, fitted coefficients, predictions, scores,
protocols, source reconstructions, original tests and CI workflows. All 2438
EWP tracked files match their baseline hashes. The user's original EWP
checkout remains at its unchanged head. Dependency locks, release/archive
identities and reference cases are untouched; NATIVE_EWP_RUNS=0.

Hosted interpreter/minimum-dependency, packaging, notebook, cross-platform and
supply-chain checks are **UNVERIFIED at this pre-push record**. The draft PR's
Checks tab and final PR report retain their actual outcomes for the exact
publication head. The existing supported local environments were preserved;
no dependency was upgraded as a repair. A hosted QA/infrastructure outcome
is reported separately from this completed scientific decision.

All real fits used one worker and one BLAS thread. The complete retained
account is 183 starts, 16 analytic fits, 25,875 actual residual calls (24,240
numerical-Jacobian calls), maximum 178 calls/start, zero failed/boundary starts,
5.2541000079363585 s optimizer wall time and 56.57155203819275 s fitting-clock
span. Peak recorded RSS was 84,592 KiB. Private evidence remains below 5 GiB.
Exactly one independently approved outcome join and score occurred. No rescue
fit, scientific protocol change, post-score repair or rescore occurred.

Retained failed attempts are bounded tooling/reference failures: the private
source helper's optional-key assumption, a pre-execution HPLC-helper syntax
error, an unused-import lint finding, a path-sanitizer rejection before public
writing, and the independent reviewer's own antiderivative-reference precision
correction. Private final-report helper attempts also stopped before writing
because they parsed incomplete wrapped pytest skip reasons. Exact complete
raw skip-section comparison establishes byte-identical baseline equality.
None changed source observations, eligibility, scientific code
after freezing, thresholds or predictions. The full routine suites necessarily
include their existing historical reproduction tests; no historical scientific
CLI workflow was independently replayed.

Source originals and row-level evidence stay private. Public source-derived
models and aggregates retain CC-BY-NC-3.0 restrictions. SOURCE_INTERNAL,
TARGET_EXPOSED and RETROSPECTIVE labels remain; analytical uncertainty is
NOT_ESTABLISHED. Flow m2 extrapolation and the unsupported secondary window
remain explicit in RESULT.md and RESULTS.json.

MERGE_AUTHORIZED=false; PRODUCTION_ADOPTION_AUTHORIZED=false;
NATIVE_EWP_RUNS=0; NO_SUCCESSOR_AUTHORIZED.
