# MODEL-GRUDEVA2026-BED-ACCURACY-004 owner handoff

**COMPARATOR_NUMERICALLY_QUALIFIED_ON_DECLARED_CASES.**
PHYSICAL_VALIDATION=NOT_ESTABLISHED. The separately identified analysis-only
004 comparator qualifies on the declared canonical cases. Historical 003 remains
unqualified on its original bed refinement; its code and receipts are unchanged.

The demonstrated limitation is linear reconstruction of the short-age diffusion
layer from cell integrals. The correction uses an integral-preserving constant,
linear and square-root basis consistently for transport faces, point liquid
forcing and grain-profile reconstruction. Physical activation, fixed-position
grain memory, continuous admission, radial backend and paired amounts remain.
The completed contract includes the source-to-code map and failed diagnostics.

All four refinements pass all eleven observables. Largest changes across them:
liquid profile 1.80216e-4 / 1e-3; outlet 1.60446e-4 / 1e-3; grain profile
9.18782e-5 / 2.3e-4; grain history 9.82017e-5 / 2.3e-4; cup
1.27890e-5 / 5e-5. Each phase inventory, front/exit/activation, analytical radial,
D=0, conservation, bounds, required-support and deterministic-repeat gate passes.
See [RESULTS.md](RESULTS.md) for every metric and [RESULTS.json](RESULTS.json)
for all counts, exact scientific/configuration/artifact identities and attempts.

Executed scientific core SHA256:
`fcc1daa15df11fa2559deccbd3dd6dd43e8c7debd877275f4da2aa8b924f7db3`.
Frozen matrix SHA256:
`28e43008a3fdd5af6447dbbc08b8b0c72a0731eb4f338eb7f45974f433dcd3c4`.
Total scientific spending: **7 full attempts, 13 short invocations,
1518.092603 seconds**. No full failure, resource termination or unresolved start;
one failed short crossing pilot remains retained. No final correction reserve
was spent. Maximum invocation 578.509216 seconds, maximum measured final RSS
780455936 bytes. No more numerical development is authorized by unused budget.

## Reproduction and acceptance receipts

[CONTRACT.md](CONTRACT.md#execution-and-saved-result-reproduction) gives the
small executable example, bounded seven-row driver, diagnostics and saved-result
reduction commands. The external original archive is named
`model-grudeva2026-bed-accuracy-004`; the separate 003 archive is
`grudeva2026-conservative-003-evidence`. Paths are owner-local, not publication
inputs. Do not distribute PDFs, private correspondence, raw logs or full arrays
in Git. Source snapshots for every executed 004 development hash are retained
externally and verified against the ledger, including the failed pilot version.

```sh
python -m pytest -q tests/test_grudeva2026_bed_accuracy_004.py tests/test_grudeva2026_bed_accuracy_004_report.py tests/test_grudeva2026_conservative_003.py tests/test_grudeva2026_reference_002.py tests/test_grudeva2026.py tests/test_grudeva2026_cli.py -m 'not slow'
python -m pytest -q -m 'not slow and not live and not gpu and not external_data'
python -m pytest -q -m 'scientific_baseline and not live and not gpu and not external_data'
ruff check puckworks/ tests/
mypy
python -m puckworks.insights verify
python -m puckworks.statusdoc --verify
python -m puckworks.paper3.evidence_graph --reconcile --strict --scope paper3
python -m puckworks.paper3.evidence_graph --reconcile --strict --scope all
python -m build --outdir "$EVIDENCE/dist"
python tools/packaging_check.py "$EVIDENCE/dist"
```

The full normal local suite passed 6168 tests; minimum-dependency focused checks
passed 96. Registry, generated/integrity, configured static/type, scientific
baseline and packaging checks pass. No full scientific trajectory is hidden
inside 004's software tests. Existing generators update the affected card/status
snapshots; generated files are not edited by hand. After regeneration, 234
affected checks pass, and the saved-result replay is byte-identical.

Exact final commit/tree, draft PR URL, hosted-check status and the independent
nonhuman exact-head review receipt are supplied in the PR/final handoff outside
this commit's self-hash. At numerical report generation, CI/review are genuinely
pending. Required hosted contexts were read from active ruleset 19053322:
`quick (3.10)`, `quick (3.12)`, `verify-generated`, `paper3-scope-strict`,
`all-scope-strict`. Local tests do not satisfy hosted contexts by implication.

## Owner boundary

There is no remaining numerical gate blocker for this declared comparator.
The unlocked matched solver comparison is **not executed or started**; production
raw-state/observer qualification is still separately required. This result
neither resolves the publication mismatch nor validates coffee physics.
Figures 3/4 remain FAIL/FAIL and Figure 5 incomplete. PR #325's cancelled
post-merge minimum lane is an unchanged infrastructure closeout fact, not a
demonstrated software/numerical failure and not silently repaired here.

Leave this one Puckworks PR draft, auto-merge disabled and issue #67 open.
No merge, EWP edit, OpenFOAM/native integration, parameter fit, dependency/default
change, source acquisition, laboratory work or automatic successor is authorized.
