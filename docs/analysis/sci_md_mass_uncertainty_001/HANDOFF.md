# SCI-MD-MASS-UNCERTAINTY-001 handoff

Implementation: **implemented**. Real-data audit: **complete for all three tasks**.
Historical point metrics, primary arm summaries, decision components and retained
shot/pair/row/column results reproduce. Original verdicts remain authoritative.
Independent nonhuman review and hosted CI are separate candidate-bound receipts
in the draft PR conversation; a pending receipt is not a pass. No human approval
is claimed. MERGE_AUTHORIZED=false; PRODUCTION_ADOPTION_AUTHORIZED=false.

## Identities and reproduction

Base: `3cd308ac5bed39acff3d995108b5178a53c982ee`.
Read-only EWP main/reference: `4284e9460c8057053e95de7cfa2fb3590e68e9db`.
Protocol freeze: `14b8ab4d` (before new summaries; prior outcome exposure remains).
Executed implementation: `eedeebd626ea8a8af2b0f4c368a8e05e725720a1`, tree
`090c64399a7499ba0d6dffec5585099e8d3ca36c`.
Publication adds this bundle and minimal navigation/status wording; it does not
change the executed analysis. The PR's candidate head/tree and review are recorded
in its candidate-bound conversation receipt to avoid a self-referential commit.

Use the existing authorized Python environment with NumPy, SciPy and openpyxl;
no install or upgrade is required in the execution environment. Set
`EWP_CHECKOUT` to the existing read-only reference checkout and each output to a
new private directory outside Git and outside the source collection. The existing
resolver honors `PUCKWORKS_EXTERNAL_DATA_ROOT`, XDG configuration and
`~/.config/puckworks/data_sources.json`. No raw inputs are accepted from CI.

```bash
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
python -m puckworks.analysis.mass_uncertainty_audit preflight \
  --ewp-checkout "$EWP_CHECKOUT" --output "$PRIVATE_NEW_PREFLIGHT"
python -m puckworks.analysis.mass_uncertainty_audit audit \
  --ewp-checkout "$EWP_CHECKOUT" --output "$PRIVATE_NEW_AUDIT"
python -m puckworks.analysis.mass_uncertainty_audit report \
  --retained "$PRIVATE_COMPLETED_AUDIT"
python -m pytest -q tests/test_mass_uncertainty_audit.py \
  tests/test_pannusch_conditional_tail_delivery.py \
  tests/test_grudeva_pooled_tail_delivery.py \
  tests/test_grudeva_one_shot_calibration.py \
  tests/test_statusdoc.py tests/test_espresso_data_guide.py
ruff check puckworks/ tests/
python -m puckworks.statusdoc --verify
python -m tools.readme_governance verify
python -m puckworks.paper3.registry_artifacts --verify
python -m puckworks.paper3.build verify
```

`report` only reads the completed retained output and validates its result hash;
it does not reopen sources or calculate science. Audit outputs are exclusive;
existing files/directories cannot be overwritten. The private execution record
contains the exact installed interpreter and filled commands. Public RESULTS.json
is byte-identical to the final retained aggregate. Arithmetic reconciliation uses
at most 512 binary64 ulps at scale max(1,abs(value)); identities, keys, integers
and statuses are exact. This is serialization/reduction precision, not a relaxed
scientific threshold. No historical score/evaluate, fitting, scientific prediction
or solver campaign entrypoint is called.

## Evidence actually available

Configured authorized inventory resolved the three existing task evidence bundles.
All required private predictions, queries, outcome projections, retained detailed
results, original freezes and source/role/model commitments were available.
The audit verified 1,840 files before and after execution. Six Pannusch/Schmieder
originals and nine accepted registers were verified; original measured coordinates
were reconstructed through the qualified adapters. Individual-shot observed
exports matched their retained projection and original MAT assays at the accepted
serialization precision. No normalized mean table was substituted.

For Grudeva, the original CSV, interpretation notebook and thesis match their
commitments. The notebook was not executed. Qualified parser/projections recover
13 original qualified shots, 11 eligible, 55 positive suffix windows and 98 prefix
assays forming 22 summaries. Original exclusions remain. MASS-007 and MASS-008
reuse these physical identities. Pannusch/Schmieder export aliases remain one
lineage; distinct identical-valued shots are not merged.

Every MASS-006/007/008 freeze artifact was rehashed (1,484 / 16 / 271 respectively).
Evaluated producer commits/trees, actual metric/runtime bytes, public model hashes,
008 calibration manifest/artifact-set identity, prediction hashes, original
protocol hashes and outcome-projection identities are in RESULTS.json. EWP's
three retained aggregate results are byte-identical corroborating records.
Original producers remain distinct from current main and the audit implementation.

The current CLI conservatively requires complete original frozen bundles. A
missing optional reference or unrelated historical fit-log member can mark that
task unavailable, even where a narrower primary reduction might be possible;
other available tasks continue. This portability limitation did not affect this
execution: every member was available. Identity mismatches always stop execution;
there is no fallback to replacement bytes or aggregate reconstruction.

## Findings and limitations

- MASS-006: C2 primary R=0.480034 pp, mean absolute shot bias=0.395567 pp;
  original A/B/C/D PASS. Primary C2 gain over C1 (R_C1 − R_C2) sensitivity is 0.093939–0.135358 pp.
  Full flow scope remains incomplete. Source-observed replicate spread is
  explicitly separated from each arm's actual score-supported replicate spread.
- MASS-007: C2 R=0.599149 pp, mean absolute shot bias=0.532635 pp; adequacy FAIL,
  I0/I1 PASS. Gains remain above 0.10 pp and 15% in every physical-shot deletion.
  Mean absolute bias spans 0.481706–0.573421 pp. Original 7/11 adequate shots
  remain two short of the required nine.
- MASS-008: A2 R=0.483158 pp, mean absolute pair bias=0.346410 pp; adequacy PASS,
  all increments FAIL. Every identity deletion leaves 90 off-diagonal pairs.
  A2's gains remain positive, but each comparison crosses the 0.10 pp component;
  versus M the range is 0.005877–0.149255 pp. Adverse calibration-choice bias
  remains visible despite favorable overall means.

All-arm, all-panel distributions, support/extrapolation, signed threshold headroom
and count surplus/shortfall are retained. These are conditional variability and
sensitivity summaries, not confidence intervals or replacement decisions.
Within-shot analytical repeatability, calibration/systematic uncertainty,
early-input propagation, model-training uncertainty, cross-source uncertainty
and prospective coverage remain unestablished. No noise-floor, equivalence,
perfect-model failure-probability or physical-validation claim follows.

## Execution, checks and preserved corrections

Final retained execution: `audit-003`, Python 3.12.3, existing NumPy 2.5.3 /
SciPy 1.18.1 / openpyxl 3.1.5, one worker and one BLAS thread. Reduction wall time
6.20 s, maximum process RSS 1,051,424 KiB. Inputs totaled about 14.2 MB in the
independent preservation check; outputs remain private except permitted aggregates.
No paid compute, dependency upgrade or system-wide change.

Preserved attempts and corrections:

1. `preflight-001`: selected old environment lacked openpyxl. No input mismatch;
   existing reader-capable environment used for successful `preflight-002`.
2. `audit-001` at `a2976e51`: stopped at missing calibration key in the new
   MASS-008 status-vector reduction. Historical wrapper adds that field after
   pure metrics. Independent review confirmed an implementation omission, not
   changed evidence or a numeric disagreement. `454372fc` adds exact calibration
   membership/status reduction; `audit-002` completes.
3. Independent review requested explicit actual-scored replicate variability
   alongside available source-observed variability. `eedeebd6` adds support counts
   and spreads per arm; `audit-003` completes. Point metrics and physical-shot
   sensitivities are unchanged. Earlier analysis versions remain private.
4. README check initially used a direct script invocation from an uninstalled
   environment, causing import failure; the documented module invocation passed.

Focused maintained tests: **74 passed**, including 18 rights-independent new
synthetic tests. Full repository Ruff passed; generated status, README governance,
Paper 3 registry artifacts and build verification passed. Unchanged baseline
quick/generated/scientific-baseline evidence is reusable at the exact base:
[quick](https://github.com/trbrewer/puckworks/actions/runs/37994127568),
[generated](https://github.com/trbrewer/puckworks/actions/runs/37994127440),
[scientific baseline](https://github.com/trbrewer/puckworks/actions/runs/37994127536).
This baseline evidence is not candidate-specific CI. Hosted candidate checks and
final independent review must be read separately in the PR; no CI selector changed
and no private evidence was uploaded to CI.

Independent nonhuman review checked original-source matching, independent weighted
arithmetic, condition/shot/pair weighting, joint-role deletion, missing uncertainty,
claim limits and privacy; material findings above were corrected. It independently
rehashed all 1,840 original inputs after the analysis. Its final receipt binds the
actual publication candidate, not an invented human approval.

Expected changed paths are the two new Python files, this four-file bundle,
CURRENT.md, current.json and generated STATE_OF_TRUTH.md. Status changes only
reconcile the stale Grudeva next action against merged 008/009 and open #333.
The active queue remains capped at five; unrelated owner work is not reprioritized.
PR #333 stays at its original reviewed head and qualification-incomplete state.

Historical sources, models, predictions, scores and receipts remain unchanged.
EWP remains read-only (fetch only), native runs=0. Production defaults, dependency
locks and adoption settings remain unchanged. No merge, release, issue closure,
new acquisition, laboratory work or automatic successor. This audit supplies no
certificate that the host involved in prior integrity failures is reliable.
