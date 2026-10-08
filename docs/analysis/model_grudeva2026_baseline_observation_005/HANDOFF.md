# 005 owner handoff after resource amendment

**OBSERVER_QUALIFICATION_INCOMPLETE / OBSERVER_CAPTURE_IDENTITY_BLOCKED.**
Complete-panel resource feasibility remains NOT_ESTABLISHED.
G1 / NO_GOVERNING_PHYSICS_CHANGE; G0 resource engineering within the task.
PHYSICAL_VALIDATION=NOT_ESTABLISHED.

The owner-authorized 8 GiB replacement pilot passed its applicable .4-horizon
checks. The one full combined probe returned a COMPLETED public Result at t=8
and all three original solver objects, then failed the unchanged observer's
third-segment persistence/replay identity check. Full observation and neutrality
remain unqualified. Stop: no remaining matrix, repair, recapture, comparison,
publication score, merge or automatic successor is authorized.

## Evidence and reproduction

Use the existing external `grudeva2026-baseline-observation-005` archive. Its
original `invocations.jsonl` contains every historical and new attempt; never
initialize a replacement ledger. Preserved originals include `invoke-2gib.py`,
`controller-binding-2gib.json`, `invocations-before-8gib.jsonl`,
`MATRIX-2gib-reviewed.json` and `RESULTS-2gib-reviewed.json`. Their exact hashes,
new controller and amendment are bound in current MATRIX. The old result remains
OBSERVER_QUALIFICATION_INCOMPLETE / RESOURCE_FEASIBILITY_BLOCKED.

New safe evidence includes `pilot-8gib.json`, its NPZ/observation files and
`pilot-8gib-evaluation.json`; `combined-8gib.json`, three segment NPZ files,
`combined-8gib-execution.json` and `combined-8gib-failure-audit.json`. The third
NPZ survives without its original expected hash/live replay metadata. Its
post-failure inventory hash must not be substituted to force successful replay.
No numerical pickle or archived executable is needed to inspect these arrays.

```sh
python -m puckworks.analysis.grudeva2026_baseline_observation_005_report \
  --runs-directory "$EVIDENCE" \
  --matrix docs/analysis/model_grudeva2026_baseline_observation_005/MATRIX.json \
  --output "$EVIDENCE/replayed-amended-results.json"
# Expected exit 2: observer incomplete, capture identity and panel-feasibility blocks.
cmp "$EVIDENCE/replayed-amended-results.json" \
  docs/analysis/model_grudeva2026_baseline_observation_005/RESULTS.json
```

The failure-first reducer rejects incomplete segment evidence before launching
full offline reconstruction. Its accounting checks both exact resource policies
and preserves all individual unavailable reasons. It never launches a solver.
The full raw Result remains COMPLETED but EXECUTED_UNQUALIFIED, not a qualified
baseline or evidence of a governing-physics defect.

## Original continuation commands: historical, not rerun instructions

```sh
python tools/run_grudeva2026_baseline_observation_005.py amend-resources "$EVIDENCE"
python "$EVIDENCE/invoke.py" pilot-combined-8gib short development \
  python tools/run_grudeva2026_baseline_observation_005.py run --row combined --pilot \
    --output "$EVIDENCE/pilot-8gib.json" \
    --matrix "$EVIDENCE/MATRIX-8gib-pilot-frozen.json" \
    --allocation "$EVIDENCE/allocation-pilot-8gib.json"
python "$EVIDENCE/invoke.py" combined-feasibility-8gib full development \
  python tools/run_grudeva2026_baseline_observation_005.py run --row combined \
    --output "$EVIDENCE/combined-8gib.json" \
    --matrix "$EVIDENCE/MATRIX-combined-probe-frozen.json" \
    --allocation "$EVIDENCE/allocation-combined-probe-8gib.json"
```

The installer refuses a second installation. It preserves the old controller and
ledger before installing the exact task-local 8 GiB controller. Neither the
protected 004 controller nor the scientific 005 observer changes. Both numerical
starts checked real host/cgroup/limit/storage headroom. Resource tests use
separate temporary software ledgers and a nonnumerical child; they do not run a
production trajectory or require a CI host to allocate 8 GiB.

The probe retains its original matrix identity. Current MATRIX binds that
receipt and checks identical scientific fields; changes to planning/status do
not restamp the raw evidence. A successful complete probe would have been reused
as the combined row. This probe is currently blocked and cannot qualify that row.

## QA, review and boundaries

Run focused affected resource/reporter tests and inherited observer tests with
the unchanged selectors. Existing analytical fixtures and unaffected normal QA
retain their actual identities. Final current-head hosted checks, static/type,
minimum dependencies, packaging/integrity and the same independent review's
resource/new-evidence addendum are recorded on draft PR #327. Do not present the
prior review as approval of newly executed results.

Current totals: 1 full, 9 short, 298.9300972319761 numerical seconds. Original
2 GiB failure remains counted. No unresolved starts or raised time/count limits.
The consumed observer-only correction remains consumed; this G0 amendment does
not authorize repairing the newly exposed scientific observation failure.

All 50 protected 001–004/production paths and the scientific observer remain
byte-identical. EWP is read-only; lock SHA256 remains
`52b15ceef87d503a3e77c6e3c1cbed785185d2dde0b79647e5fbe309395d2f10`.
Leave #327 draft, auto-merge disabled, and #67 open. Any resolution of the
unresolved observer identity failure requires a separate owner decision; unused
budget alone does not authorize it. No matched comparison is ready or executed.
