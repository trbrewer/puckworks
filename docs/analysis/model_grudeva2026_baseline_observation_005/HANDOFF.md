# 005 owner handoff after persistence correction

**OBSERVER_QUALIFICATION_INCOMPLETE / OBSERVER_DIAGNOSTIC_INLET_BLOCKED.**
G1 / NO_GOVERNING_PHYSICS_CHANGE; the owner-authorized persistence correction is
G0 within this task. PHYSICAL_VALIDATION=NOT_ESTABLISHED.

One new complete combined observation was obtained. All three segments pass file
identity, exact returned-array fidelity and unchanged live/offline replay; all
22 combined individual gates pass. Its complete public Result exactly matches
the historical failed probe in the same environment. That repeat-consistency
check does not replace real normal/control neutrality.

The subsequent normal observation fails its unchanged diagnostic inlet gate:
2.046100506994386e-5 > 2e-5 at t=.2,z=0. Normal/combined grain profile and history
refinement errors are 6.000191780015651e-4 and 4.323872501288406e-4 against
2.3e-4. Observer qualification remains unresolved; do not attribute the errors
to a governing-physics defect. Execution stopped before the unobserved control,
repeat or other three refinements. No scientific correction or further trajectory
is authorized by unused resources. Every gate/count/location is in RESULTS.

## Preservation and evidence

Use the existing configured `grudeva2026-baseline-observation-005` evidence
archive. Its original append-only `invocations.jsonl` remains authoritative.
The original 2 GiB failure, 8 GiB short pilot and failed combined capture retain
all metadata, numerical files, logs, allocations and identities. The failed third
file has a CRC failure in D_97.npy. Its original expected hash and live reference
are absent: recovery is ineligible and historical root cause is UNRESOLVED.
Current stable file hashes cannot repair that missing capture binding.

New originals are `combined-persistence.json` / its three NPZ and receipt files,
public checkpoint, execution receipt and full observations; the equivalent
`normal-persistence*` files; `persistence-diagnosis.json`; source-delta evidence;
fixtures and both charged offline-report attempts. Current MATRIX names exact
raw, source, request, controller and allocation bindings. Captured MATRIX receipts
retain their original identities across subsequent administrative planning updates.
No segments from different executions are combined.

The changed observer module is explicitly bound by old/new SHA256 and exact
source delta in PERSISTENCE_SOURCE_DELTA.json. Its scientific definitions,
dependencies, production-call structure and array extraction remain unchanged;
the whole module is not byte-identical. All 50 protected production/001–004
paths and the EWP lock retain their original hashes. No PDF/private path/full
array/log or executable pickle is committed.

## Reproduce the saved-evidence conclusion

Use the current checked-out source and safe JSON/NPZ files from the configured
archive. No archived Python or pickle needs execution. This command performs
numerical offline replay, not a solver invocation; account for it if conducting
a new authorized task execution rather than inspecting the retained receipt.

```sh
python -m puckworks.analysis.grudeva2026_baseline_observation_005_report \
  --runs-directory "$EVIDENCE" \
  --matrix docs/analysis/model_grudeva2026_baseline_observation_005/MATRIX.json \
  --output "$EVIDENCE/reproduced-persistence-results.json"
# Expected exit 2: observer incomplete; diagnostic inlet block; missing rows/neutrality.
cmp "$EVIDENCE/reproduced-persistence-results.json" \
  docs/analysis/model_grudeva2026_baseline_observation_005/RESULTS.json
```

The charged report worker recomputed available observations from raw NPZ files.
Its own ledger start was pending during execution; after successful completion,
only resource accounting and that temporary own-start reason/block were refreshed.
The preliminary worker, original end record and accounting-closure receipt are
preserved. Scientific fields were unchanged. The ordinary reporter using the now
closed ledger has no pending-start exception or disabled identity check.

## Resource amendment and actual use

The owner-authorized address-space ceiling remains exactly 8589934592 bytes.
The new controller only permits the exact `combined-persistence-recapture`
correction identity; no force/retry flag. The original 2 GiB and prior 8 GiB
controllers and ledger prefixes remain bound separately. Installation used the
same original lock and retained an explicit `persistence-amendment.json` old/new
binding; no replacement ledger or external host/container restriction change.

The replacement full run took 142.27878846699605 seconds; peak RSS 3765407744
bytes, peak virtual 4082462720 bytes. Normal took 30.401547679997748 seconds.
The complete-panel allocation was conditionally resource-feasible after the
combined measurement; the later observer gate stopped execution.

Cumulative totals: **3 full, 19 short, 551.7639391399425 numerical seconds**.
All attempts are closed. One correction full slot and 142.27878846699605 seconds
were consumed by recapture; total correction time including the earlier fixture
is 145.90051950799534 seconds. Five mandatory runs remain unexecuted. The ledger
retains failed diagnosis/fixture/auxiliary-report attempts as well as successful
runs. No attempts or time were reset or borrowed from historical tasks.

## QA and decision boundary

Use the final exact-head receipt on draft PR #327 for normal QA, minimum
dependencies, static/type, integrity/packaging, hosted CI and the same independent
nonhuman review's persistence/new-evidence addendum. Earlier review of the blocked
candidate does not approve these new observations. Pending checks stay pending.

EWP remains clean/read-only. Its dependency-lock SHA256 is
`52b15ceef87d503a3e77c6e3c1cbed785185d2dde0b79647e5fbe309395d2f10`.
Leave #327 draft, auto-merge disabled, and #67 open. This task does not establish
readiness for a matched comparison. No 006, production repair, publication
rescore, adoption, merge, matched comparison or automatic successor is authorized.
