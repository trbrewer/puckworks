# Inspect/reproduce the finite 010 transfer experiment

This command copies and hashes opaque bytes. It never imports Puckworks, NumPy
or SciPy, evaluates an interpolant, invokes a solver, or admits a scientific
archive. The diagnostic does not change the frozen campaign hash guards.
PHYSICAL_VALIDATION=NOT_ESTABLISHED.

The recorded plan is `TRANSFER_ISOLATION_PLAN.json`. Its SHA256 binds the
standalone command, focused tests, exact interpreter/runtime files, system tools,
source metadata and private `INPUTS.json`. Resolve private paths through the
existing retained execution/source configuration. Never infer them from public
descriptions. The input JSON has `source` (original segment ZIP) and
`opaque_bad_fixture` (complete quarantined NPY). The latter is compared only to
its own bad-copy identity. The original failed archive and bad extraction remain
quarantined; a new matching copy cannot repair their historical outcomes.

## Recorded commands

The finite supervisor takes an exclusive execution lock and runs A, B, C once,
recording real process exits and per-second process-tree RSS, available memory
and disk. It is retained externally with the plan-bound SHA. The interpreter is
the original bound Python 3.12.3; no dependencies are installed or upgraded.
The following are the recorded invocations, not authorization for additional
large executions. `TRANSFER_OUTPUT` is an exclusive new parent directory; A, B,
and C are sibling directories so C can reverify A's retained spool.

```bash
python tools/diagnose_grudeva2026_transfer_010.py A \
  --plan docs/analysis/model_grudeva2026_full_reference_010/TRANSFER_ISOLATION_PLAN.json \
  --inputs "$TRANSFER_INPUTS" --output "$TRANSFER_OUTPUT/A"
python tools/diagnose_grudeva2026_transfer_010.py B \
  --plan docs/analysis/model_grudeva2026_full_reference_010/TRANSFER_ISOLATION_PLAN.json \
  --inputs "$TRANSFER_INPUTS" --output "$TRANSFER_OUTPUT/B"
python tools/diagnose_grudeva2026_transfer_010.py C \
  --plan docs/analysis/model_grudeva2026_full_reference_010/TRANSFER_ISOLATION_PLAN.json \
  --inputs "$TRANSFER_INPUTS" --output "$TRANSFER_OUTPUT/C"
```

Each command verifies its implementation/environment/input binding and creates
exclusive records. A future explicitly authorized environment contrast would
need a separately identified plan with actual transferred-input verification,
environment/filesystem identities and software differences. The present binding
must not be edited to relabel such a run as the same execution. No ignore-hashes
or reference-loader bypass exists.

## Small independent checks

```bash
python -m pytest -q tests/test_grudeva2026_transfer_010.py
python -m ruff check tools/diagnose_grudeva2026_transfer_010.py tests/
```

These use deterministic opaque byte fixtures, including signed-zero bytes. They
invoke zero solvers and no retained scientific inputs. Negative controls cover
known differences, truncation/short reads and writes, stale expectations, changed
source buffers and destinations, secondary evidence failures, and fresh-process
witness reproduction. Small A/B/C subprocess controls require the bound system
tools; unavailable platforms report skips explicitly. GNU/Python hash agreement
is not an independent cryptographic-library implementation: both use libcrypto.

Ordinary packaging QA is separate. The frozen virtual environment lacks a
setuptools backend, so its initial `build --no-isolation` fails before creating
a distribution. The retained successful packaging check exposes the already
installed system setuptools 68.1.2 / wheel 0.42.0 only to the build process:

```bash
PYTHONPATH=/usr/lib/python3/dist-packages:. python -m build --no-isolation --outdir "$QA_DIST" .
python tools/packaging_check.py "$QA_DIST"
```

This installs/upgrades nothing and is not an environment used for a diagnostic
row or scientific run. Other platforms need their own identified available
build backend; this command does not relax the frozen transfer environment.

Read `FIRST_FAILURE.json` first when present, followed by `witness-N.json`, raw
`prior/current.bin` blocks, complete differing-offset TSV, and `RESULT.json`.
Essential failure records precede fallible enrichment. A missing prior block
is explicit; a digest does not supply prior bytes. `events.jsonl` identifies
stage/time/count/offset/digest comparisons; `prospective.jsonl` preserves the
ordered source commitments. A's complete `decoded-member.bin` retains the actual
decoded chunks for later inspection. Read new diagnostic outputs as ordinary
bytes, never through the qualified-reference loader.

For a small saved diagnostic, `check --target ... --spool ... --records ...
--output NEW_DIRECTORY` invokes the same fresh-process reader used by A.
`pair --target ... --spool ... --output NEW_DIRECTORY` compares ordinary NPY
byte fixtures without numerical conversion. Large checks remain bounded by
the declared plan; these interfaces do not authorize unplanned rereads.

Full NPY/member, payload, compressed member and whole ZIP are different domains.
The payload starts at member offset 128. A returned fsync and a matching fresh
process read do not prove a physical-media read or universal hardware health.
The archived machine visibility record explicitly preserves inaccessible SMART
and absent EDAC visibility. No administrative system change is part of this work.
