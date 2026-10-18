# Caffeine addendum handoff

Scientific reduction complete for all five declared evidence components. Original
and reproduced decisions agree exactly: D0/S0/S1/S2 primary adequacy all PASS;
S2 A/B/C/D PASS/FAIL/FAIL/FAIL; original simpler-predictor disposition unchanged.
This completes one T04 case and caffeine-specific T02 interpretation, not those
entire queues. The [results](RESULTS.md) retain adverse and conditional findings.

## Identities and authority

- Base/main: `79852f11073ef92041edff5ae0e951603084c706` (actual PR #338 merge).
- Read-only EWP: `4284e9460c8057053e95de7cfa2fb3590e68e9db`, clean before/after.
- Protocol/input/synthetic specification freeze: `8fd04834` before new deletion
  calculations. Historical result exposure is disclosed, never a blind test.
- Policy acceptance: [PR #335](https://github.com/trbrewer/puckworks/pull/335),
  merge `882584d110e1356091435ab8b002fb9abdd35ad6`. Its preserved `v1-proposed`
  wording does not require reactivation. Policy SHA-256:
  `db16e68aa0e7fbdb37bfb455c39455928115af65c207fc43ec133424cd72a552`;
  unchanged helper SHA-256:
  `d9c3d2a6e949e1f617e813dab12680dff58acdd1e4904178910739d4876e7d90`.
- Validation Operating Standard v1 at the EWP reference: SHA-256
  `1655e033a29570f71412ea065298f18c6227c40d7567c682ee6340ae6cf3bcc0`.
- Historical scorer SHA-256:
  `9e660b7c2ff6d65d2770a0caa2195ee084e768c5195fc42ffa01f081b851f989`.
  Historical evaluated producer `3389f8f4d41cfcbb965e38e9ceaed0840f9a41ea`,
  tree `10be5a877c75a6476ad32c610a7ac4fc8f71deb3` remains distinct from this addendum.
- Executed addendum module SHA-256:
  `366a40ac8be28a34b294adfd696dabf0fab364f01c47bea9ccefd24c926e7f2d`.
- Public RESULTS.json SHA-256:
  `b76b428448f3b1bf8cd3eae78b647dca88e856a6ea6d0aa8be74f61460d80cb2`.

[INPUT_MANIFEST.json](INPUT_MANIFEST.json) records exact repository and admitted
artifact byte identities, the four model-file hashes separately from embedded
model-content hashes, immutable parent identity, source IDs, and result binding.
Historical Puckworks #290 and EWP #196 were verified MERGED; stale historical
'draft' wording creates no EWP cleanup or remerge prerequisite. Open/recent task
and purpose searches found no equivalent completed/active caffeine addendum.

The final delivery receipt in this PR records exact candidate head/tree and
hosted check URLs at that head, avoiding a self-referential commit hash inside
its own tree. Direct file hashes above bind the actual executed science.

## Inputs, reproduction depth and private audit evidence

The configured collection resolves only `caffeine-delivery-001-evidence/run-001`
and its named records. All required and optional inputs were available and
admitted. Thirty-three input/authority/model files were verified before and after
reduction. Core bindings:

- shot_results.json:
  `01bd61d6af8403219071b80d094967211a06e196a8ed57dc1fb71fda9d2bb756`.
- scores.json/public historical RESULTS.json:
  `f42708bb45acbdd3b637fc6db28c5236ff7e973c02dd5c489ea9f9c2569e7c06`.
- Freeze: `de43273e864a6c3f25778d2f08672e943141100aa360650e48ef97d7309e03bc`.

The completion/receipt chain, retained observations, predictions, queries and
source-coordinate crosswalk were verified. The core uses admitted shot sufficient
statistics. The fraction route independently recomputes every arm/shot with
retained caffeine_mg_g and total allowance_kg, without altering coordinates or
counting coordinate allowance twice. Both reproductions have zero nonzero
arithmetic discrepancies in the execution environment; all labels are identical.
The independent reviewer used a different arithmetic ordering and found maximum
absolute difference 8.88e-16, with no decision differences. Reconciliation's
512-ulp arithmetic check is never used for threshold decisions or identities.

All 96 source observations are valid, versus 95/96 prediction support per arm.
The exact unsupported shot/fraction is retained, with its original reason.
No original source workbook cells were necessary or reopened; original-source
identities/qualification are reused from the bound historical records. This is
retained-source evidence, not new source qualification or independent replication.

External evidence bundle label: **caffeine-decision-resolution-001-private**,
final execution **analysis-004**.
**analysis-002/003** are byte-identical repeats before the receipt-filename
correction; all four executions have identical scientific and private results. Its private `INPUT_LOCATORS.json` contains the exact local input locators;
its `PRIVATE_RESULTS.json` contains every paired shot comparison, all baselines,
all 12 primary and six temperature deletion records, actual changed membership,
scenario-specific allowances, condition contrasts, helper scopes, reconstructed
shot results and complete crosswalks. No unfavorable result is withheld from
review. Access remains through the owner's external workspace; local paths are
not published. Cryptographic bindings:

- PRIVATE_RESULTS.json:
  `72fbb6c969052b80d03595c552ab73ec79c8306de29c316e816e41ee00946dce`.
- INPUT_LOCATORS.json:
  `9d46a9b5504c251e06f8d2c73b9c611ed6eacadde840a327b1d69058765069ac`.

RESULTS.json and each private completion record bind these outputs. Public
results contain only permitted baseline/condition summaries and exhaustive
aggregate ranges/counts; no individual shot metrics or keyed deletion means.
Pannusch/Schmieder and Mendeley 10.17632/y2tz67f6ry.1 attribution and source-derived
CC-BY-NC-3.0 treatment remain separate from first-party software licensing.

## Reproduction and checks

Use an existing Python environment with NumPy, SciPy and the repository's dev
checks. No dependency upgrade or production dependency is added. The CLI reads
only explicitly configured retained evidence and writes to a new private directory
outside Git/source inputs. It refuses an existing output directory. Use either
`--retained "$CAFFEINE_RETAINED_RUN"` or existing resolver configuration
(`PUCKWORKS_EXTERNAL_DATA_ROOT`, XDG/user data_sources.json); no archive scan.

```bash
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONPATH=.
python -m puckworks.analysis.caffeine_decision_resolution \
  --retained "$CAFFEINE_RETAINED_RUN" --output "$PRIVATE_NEW_OUTPUT"
cmp "$PRIVATE_NEW_OUTPUT/RESULTS.json" \
  docs/analysis/val_case_caffeine_decision_resolution_001/RESULTS.json
python -m pytest -q tests/test_caffeine_decision_resolution.py \
  tests/test_decision_resolution.py tests/test_mass_uncertainty_audit.py \
  tests/test_statusdoc.py tests/test_espresso_data_guide.py
python -m ruff check puckworks/ tests/
python -m mypy
python -m pytest -q -m 'not slow and not live and not gpu and not external_data'
python -m puckworks.statusdoc --verify
python -m tools.readme_governance verify
python -m puckworks.paper3.registry_artifacts --verify
python -m puckworks.paper3.build verify
git diff --check
```

Byte-identical public reproduction requires the same admitted input locators,
code/specification and numerical environment, because private locator and result
hashes are part of the public binding. Relocation may change those hashes without
changing scientific values; it must not be disguised as byte-identical evidence.
No historical prepare/develop/fit/predict/freeze/score entry point is invoked.
The original caffeine panel reducer and decision policy/helper bytes are unchanged.

Independent pre-analysis review: [receipt](PRE_ANALYSIS_REVIEW.json), PASS.
It checked mapping, hierarchy, support, design and independently derived every
synthetic expectation. One manifest classification error (registry __init__
mislisted as model artifact) was corrected before the protocol commit and analysis.
Independent final nonhuman review: [receipt](FINAL_REVIEW.json), PASS, no
unresolved material findings. It independently checked 15,110 numerical values
and 1,566 exact comparisons, all 96 arm/shot fraction reconstructions, 72 paired
shot contrasts, 21 scenarios and 32 variability cells; reviewer tests: 32 passed.
The [bounded correction addendum](FINAL_REVIEW_ADDENDUM.json) binds the final
code/tests/RESULTS.json after a public-receipt filename correction; no scientific
value changed. Reviewer final focused suite: 33 passed. The public receipt redacts only the local interpreter path and binds its retained
private original. All private outcomes were reviewed. This is not human approval
or scientific validation.

Executed focused checks: 150 baseline tests passed, then 32 new synthetic tests plus one public-receipt fallback check;
183 affected tests passed together. Repository Ruff, maintained mypy (19 modules),
status, README governance, generated registry artifacts and Paper 3 build checks
passed. Analysis-001 completed; analysis-002 adds explicit canonical coordinate
crosswalk checks and exact unsupported-shot identity without changing scientific
values; analysis-003 is byte-identical to analysis-002. Analysis-004 fixes fallback
lookup of public SCORE_COMPLETION.json/SCORE_RECEIPT.json when private receipts
are absent; the previous uppercase .JSON suffix was wrong. This never affected
the admitted private run. Only the implementation hash changes in public JSON;
all scientific and private results remain identical. The added regression check
and independent bounded review pass. All prior outputs are preserved. Full ordinary QA and candidate-specific hosted CI outcomes are recorded
in the final candidate-bound PR receipt; a running check is not reported as PASS.
No selector, threshold, coverage floor, timeout or protection rule was changed.

The initial broad instruction-filename discovery returned unrelated paths but
read no unrelated scientific files; subsequent evidence reads used only the
configured named run and its references. A first shell redirection failed before
baseline tests started because the new output directory did not yet exist; the
successful run is separately recorded. These operational events did not alter
scientific evidence. No host requalification or archive census was performed.

## Stop state

One draft Puckworks PR, unmerged, auto-merge disabled. EWP stays unchanged; no EWP
PR, model adoption, release, issue closure or automatic successor. Historical
scientific artifacts, thresholds, masks, models, predictions and receipts remain
unchanged. Physical validation and practical incremental value remain unestablished.

PHYSICAL_VALIDATION=NOT_ESTABLISHED
MERGE_AUTHORIZED=false
PRODUCTION_ADOPTION_AUTHORIZED=false
NEW_MODEL_FITS=0
NEW_PREDICTIONS=0
NEW_NATIVE_SIMULATIONS=0
NATIVE_EWP_RUNS=0
HISTORICAL_SCORE_LIFECYCLE_INVOCATIONS=0
HISTORICAL_RESULTS_UNCHANGED
NO_AUTOMATIC_SUCCESSOR
