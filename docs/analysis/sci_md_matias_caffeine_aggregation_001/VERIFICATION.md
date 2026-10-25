# Verification and handoff

Actual base: `91a8d92a027ffde1c15a841d694b2c8a51f2e637` (live main).
PR #364 is merged, accepted head `a777ce74573c2f0a302f310b79d3b0966f76b249`.
Git history and GitHub PR search found no existing aggregation result. Isolated
worktree/branch `research/sci-md-matias-caffeine-aggregation-001` preserves
existing checkouts/local work. EWP live main remains
`f44c33dbb9b4fb80143e360e6f4a90f8ac0aa516`; its local checkout was inspected
read-only, at `78cbd59c751393cddfe539e4c69e43a224329bca`. Its Puckworks lock
checkout_commit remains `fc61c4670ec7bf801e40bb391aab16048b8da26b`.

[Source identities](SOURCE_NOTES.md) and [artifact_sha256.json](artifact_sha256.json)
bind scientific bytes, without requiring a commit to contain its own hash.
All 25 files in the predecessor artifact manifest were checked byte-for-byte
against accepted hashes; none changed. The new [review receipt](review.json)
binds source CSV/geometry, exact producer, independent checker, tests, unchanged
transform helper and results. The final submitted/tested head is recorded in
the PR and handoff after commit creation. Unchanged science is not re-audited
solely because operational documentation changes a commit hash.

## Reproduction

```bash
python -m puckworks.analysis.matias2023_caffeine_aggregation \
  --output /tmp/matias-caffeine-aggregation --plot
python -m puckworks.analysis.matias2023_aggregation_check \
  --results /tmp/matias-caffeine-aggregation/results.json \
  --output /tmp/matias-aggregation-review.json --lp
python -m pytest -q tests/test_matias_caffeine_aggregation.py
```

The exact calculation is offline and reads the accepted CSV directly. It needs
no PDF recovery, network, private mount or optimizer; matplotlib is optional
through --plot. SciPy is an existing dependency used only by the independent
numerical LP check. No dependency or CI policy changes.

Seven generated files replay byte-identically in this environment: results.json,
support.csv, witness_residuals.csv, local_curvatures.csv, prefix_hull.csv,
certificates.csv and comparison.png. No cross-version Matplotlib byte guarantee.
Source/method/plan/review/verification/VizSpec are authored accompanying records.
The optional plot emits a pre-existing system Axes3D-import warning; the 2D
figure renders correctly and was visually inspected.

## Exact and focused checks

All four source layers are COMPLETE, with ten intervals and witness values,
nine monotonicity constraints, eight secant-convexity constraints and one exact
attaining lower certificate each. The independent checker verifies original
constraints and the equality of primal cost/certified lower bound without
calling the hull producer. All four numerical LP objectives agree within
1.95e−16 dex; every y variable is unbounded in sign. This floating agreement is
QA, not exact authority. Local exclusion counts are N/G/P_outer/P_inner=5/5/0/1
out of eight; all 32 diagnostics and 40 witness/support slots are retained.

The initial focused run passed 70 tests (39 new plus 31 predecessor) in 1.37 s.
The new tests cover geometric/constant/k=0 limits, genuine positive mixtures
using justified enclosing log intervals, positive excursions, shift/widening,
nonuniform/gapped support, repeated prefix sources, collinearity/ties/anchor
controls, invalid inputs, empty inner/absent support, P quantifiers,
local-versus-global infeasibility and necessary-only compatibility. Mutated
witnesses/certificates/source hashes are rejected by the independent checker.

Registry gates: 66 PASS / one pre-existing ACKNOWLEDGED_EXCEPTION. Ruff on
puckworks/tests and the affected metadata producer passes. Configured mypy:
19 modules, no issues. No production models/validation files changed.

The first expanded affected-test command used nonexistent tests/test_insights.py
and ran no tests. The corrected path ran 144 checks: 142 passed, two failed
because LOCAL_CORPUS_FAMILY_INDEX still held the old available-register hash.
The existing family-index producer then refreshed that binding, followed by the
guide producer. This is an affected projection repair, not a corpus scan/count
refresh. These original attempts are not relabelled as passes. The final corrected affected suite passed **144/144** in 3.78 s. The full
quick-lane outcome is recorded below after completion.

## Generated projections and scope

Existing producers used:

```bash
python tools/build_available_data_register.py
python tools/build_local_corpus_family_index.py
python tools/build_espresso_data_guide.py
python -m puckworks.insights write
```

Only the MATIAS2023 authority block, current Matias card/capability note and
ordinary roadmap/sprint pointers change. MANIFEST, source geometry, accepted
results/code, observation count and four-extraction grouping remain unchanged.
The Insight authority input (card) changed, so its existing producer ran; the
larger generated diff refreshes source-commit provenance to the actual base.
After normalizing producer-stamped commit provenance, the Insight delta is
limited to the Matias card hash, status text and capability-section hash, plus
the snapshot hash. Candidate IDs, corpus counts and evidence labels are unchanged. No unrelated
corpus-count refresh. README's existing Matias citation/card link still routes
to the current capability; no product/runtime/environment/registry change.
STATE_OF_TRUTH/CURRENT have no lifecycle promotion to project.

## Local and hosted completion

Generated registry/build/availability/corpus checks, all three manuscript claim
coverage checks, lateral-coupling artifacts, evidence graph reconciliation/verify,
status truth, Insight verify and local-corpus coverage all pass. README governance
passes. GitHub reports no classic branch protection, but its active ruleset
requires quick (3.10), quick (3.12), verify-generated, paper3-scope-strict and
all-scope-strict, with strict latest-base checking. All triggered repository
workflows will still be run and reported. No CI rules are changed.

The full local quick lane passed: **7,321 passed, 36 skipped, 73 deselected**,
10 warnings, in **1,529.63 s**. It used the unchanged repository selector
`not slow and not live and not gpu and not external_data`, with JUnit output.
No failed full-suite test or unresolved local blocker. The earlier affected-run
failures remain SOFTWARE_OR_QA_FAILURE records, corrected as described above.

Local environment: Python 3.12.3, NumPy 2.5.4, SciPy 1.18.1, pytest 9.1.1,
Matplotlib 3.11.2, using the existing task environment; no dependency update.
README pulse, radar configuration and committed research-intake validation pass.
EWP's lock was also fetched read-only at its live main identity and matches the
recorded pin; neither local nor remote EWP content was written.
Required hosted CI is NOT_YET_RUN_AT_PACKET_CREATION. The final observed
workflow outcomes are recorded on the draft PR; the live branch runs are at
[GitHub Actions](https://github.com/trbrewer/puckworks/actions?query=branch%3Aresearch%2Fsci-md-matias-caffeine-aggregation-001).
This operational record precedes submission and does not assert future success. Actual results and final
submitted/tested head will be recorded in the draft PR and final handoff.
A pending, cancelled or failed workflow is never inferred to pass.

Leave OPEN / DRAFT / UNMERGED, auto-merge disabled. No production change,
EWP write or successor. Physical validation remains NOT_ESTABLISHED.
