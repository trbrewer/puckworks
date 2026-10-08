# 005 owner handoff

**RESOURCE_FEASIBILITY_BLOCKED; OBSERVER_QUALIFICATION_INCOMPLETE.**
PHYSICAL_VALIDATION=NOT_ESTABLISHED. G1 / NO_GOVERNING_PHYSICS_CHANGE.
The .4-horizon combined-row pilot failed in unchanged production solve_ivp's
accepted-state allocation under 2 GiB, before a solver object returned. No
full-horizon attempt, neutrality pair, matched comparison or production repair
was executed. Historical 001 and qualified 004 retain their original authority.

Implementation:

- `puckworks/analysis/grudeva2026_baseline_observation_005.py`: return capture,
  numeric BDF persistence/replay, actual modal/state mapping, cell-average
  reconstruction, activation, independent phase and cup observations.
- `puckworks/analysis/grudeva2026_baseline_observation_005_report.py`: offline
  failure-first reducer, inherited masks/gates plus maximum locations and counts.
- `tools/run_grudeva2026_baseline_observation_005.py`: scoped adapter to the
  unchanged 004 external controller, one-run execution and fixture evidence.
- `tests/test_grudeva2026_baseline_observation_005*.py`: independent numerical
  and software/negative-path checks.
- `examples/grudeva2026_baseline_observation_005.py`: small manufactured
  cell-average reconstruction example; explicitly not a production trajectory.

## Reproduce saved evidence without a solver or pickle

Use the external archive named `grudeva2026-baseline-observation-005`, with its
original `invocations.jsonl`, `invoke.py`, logs, `pilot.json` and
`fixtures-retention.json`. The arrays in these JSON fixtures are synthetic; the
failed pilot contains no returned production arrays. All original attempt
records and pre-freeze source identities remain retained. Do not reset its ledger.

```sh
python -m puckworks.analysis.grudeva2026_baseline_observation_005_report \
  --runs-directory "$EVIDENCE" \
  --matrix docs/analysis/model_grudeva2026_baseline_observation_005/MATRIX.json \
  --output "$EVIDENCE/replayed-results.json"
# Expected exit 2 and OBSERVER_QUALIFICATION_INCOMPLETE, with RESOURCE_FEASIBILITY_BLOCKED.
cmp "$EVIDENCE/replayed-results.json" \
  docs/analysis/model_grudeva2026_baseline_observation_005/RESULTS.json
python examples/grudeva2026_baseline_observation_005.py
```

For a future separately authorized complete capture, `Trajectory(path)` loads
only safe NPZ arrays; `evaluate(t, side='left'|'right')` retains segment provenance;
`state_fields` exposes actual liquid/modal averages; physical faces are returned
s times recorded xi faces. `profiles` returns liquid, weighted grain-volume mean
and every mode at requested physical positions; `inventory` performs the separate
spatial sums. `observe_saved` emits the full profiles, modal contributions,
seven histories, activation, accepted/event audits and cup quadrature externally.
None of these offline calls starts a solver. The diagnostic quadratic and public
center-linear/end-extension reconstructions have distinct definitions. Public
Results are never replaced by a diagnostic reconstruction.

## Execution commands and bound

The exact original commands were serial, with controlled library threading and
external start/end/resource logging:

```sh
python tools/run_grudeva2026_baseline_observation_005.py init "$EVIDENCE"
python "$EVIDENCE/invoke.py" fixtures-initial short development \
  python -m pytest -q tests/test_grudeva2026_baseline_observation_005.py
python "$EVIDENCE/invoke.py" pilot-combined short development \
  python tools/run_grudeva2026_baseline_observation_005.py run --row combined \
    --pilot --output "$EVIDENCE/pilot.json"
python "$EVIDENCE/invoke.py" fixtures-retention short development \
  python tools/run_grudeva2026_baseline_observation_005.py fixtures \
    --output "$EVIDENCE/fixtures-retention.json"
```

The initial fixture/pilot source snapshot is historical and hash-bound; the
current implementation does not restamp it. The three intermediate fixture
emissions (`fixtures-final`, `fixtures-bound`, `fixtures-freeze`) and manufactured `example` invocation
remain counted. Reproducing numerical invocations consumes a separately
allocated budget, not a fresh ledger used to evade this task's limits. The full
runner requires an exact frozen matrix with established feasibility and refuses
this blocked matrix before calling production. No full execution command is a
continuation instruction for the present task.

## QA and review

```sh
python -m pytest -q tests/test_grudeva2026_baseline_observation_005*.py \
  tests/test_grudeva2026_bed_accuracy_004*.py tests/test_grudeva2026_conservative_003.py \
  tests/test_grudeva2026_reference_002.py tests/test_grudeva2026.py \
  tests/test_grudeva2026_cli.py -m 'not slow'
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

Current generated/integrity and registry checks are ordinary QA. No generator
or historical receipt is edited to suppress a failure. The full normal selector
and supported dependency floors remain intact. The final head/tree, PR URL,
actual candidate QA, hosted checks and the single independent nonhuman exact-head
review receipt are supplied in the PR/final response after those identities exist.
This avoids a circular self-hash and does not imply pending checks passed.

## Remaining owner decision

The bounded task cannot qualify actual full production observation or neutrality
within the measured memory limit. Code/tests and a reproducible blocked report
are delivered; no numerical disagreement is attributed to production. Resolving
execution feasibility would require a separate owner decision. It does not
follow from the unused attempt/time reserve. EWP remains untouched at its older
local head and current remote authority; its lock SHA256 remains
`52b15ceef87d503a3e77c6e3c1cbed785185d2dde0b79647e5fbe309395d2f10`.
Leave #67 open and this one PR draft, auto-merge disabled. No comparison, repair,
production adoption, merge or successor is performed or authorized here.
