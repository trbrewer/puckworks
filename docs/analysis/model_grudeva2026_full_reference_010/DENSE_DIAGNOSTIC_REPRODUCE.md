# Reproduce or inspect the 010 dense-capture diagnostic

Diagnostic scope only. No scientific row or full anchor is authorized.
MATRIX.json and CONTINUATION.json remain immutable; their original campaign hash
checks reject the changed implementation. No ignore-hashes route was added.
PHYSICAL_VALIDATION=NOT_ESTABLISHED.

Resolve external evidence through the retained execution/source configuration.
`DENSE_INPUTS` below is the separately recorded selected-input directory, not a
qualified trajectory. `DENSE_OUTPUT` must be a new exclusive location. Raw arrays,
private locators, execution logs and failure quarantines remain external.

## Recorded diagnostic commands

The two completed replays use the immutable amendment and retained
`frozen-diagnostic-v2` implementation files. For exact historical reproduction,
resolve that external source directory, create a separate temporary copy of this
checkout, and overlay its five files only after checking every SHA256 against
`DENSE_DIAGNOSTIC_AMENDMENT.json["implementation"]`. Run the commands below in
that temporary copy; do not overwrite the working branch or historical evidence.

The delivered command has a later failure-only witness-read correction. Its
identities are in `DENSE_DIAGNOSTIC_DELIVERY.json`, together with the exact old/new
hashes and successful-path reuse proof. It correctly rejects the old amendment
when run without the historical overlay. The delivery binding can verify a
subsequently authorized diagnostic using `--plan DENSE_DIAGNOSTIC_DELIVERY.json`
(with its repository-relative path); no large execution occurred under that
binding, and these instructions authorize no further execution. Ordinary bounded
controls below exercise the delivered failure branch.

Use the original bound Python 3.12.3 / NumPy 2.5.2 / SciPy 1.18.1 environment and
the exact implementation identities in DENSE_DIAGNOSTIC_AMENDMENT.json. The
command checks those identities, the mathematical/solver identities and thread
settings. It disables integrate/solve_ivp in its process. It does not execute
numeric code from an archive, pickle, observation audit or interpolation.

```bash
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONPATH=.
export DENSE_INPUTS DENSE_OUTPUT  # resolved private input; new exclusive output
python - <<'PY'
import hashlib, json, os
from pathlib import Path
plan = json.loads(Path('docs/analysis/model_grudeva2026_full_reference_010/DENSE_DIAGNOSTIC_AMENDMENT.json').read_text())
assert hashlib.sha256((Path(os.environ['DENSE_INPUTS'])/'INPUT.json').read_bytes()).hexdigest() == plan['selected_input_manifest_sha256']
assert not Path(os.environ['DENSE_OUTPUT']).exists()
PY
python tools/diagnose_grudeva2026_dense_capture_010.py replay \
  --plan docs/analysis/model_grudeva2026_full_reference_010/DENSE_DIAGNOSTIC_AMENDMENT.json \
  --input "$DENSE_INPUTS" --output "$DENSE_OUTPUT"
```

The retained supervisor verifies the selected-input manifest, takes an exclusive
execution lock, records the actual child exit status, samples RSS and available
host/cgroup memory/disk, and stops on failure or real critical resource headroom.
The two declared resident executions are distinct fresh processes. No additional
repeat or scientific execution is implied by these reproduction commands.

The first extraction command and its original plan are preserved as failed
evidence. Do not repeat it to recreate a passing copy. The retained original ZIP
segment-1 D member matches its producer digest, while the newly extracted copy
differs at 54 byte positions. The amendment reads that original member directly,
verifies it, constructs owned resident pieces, and releases the extra decoded
array before capture. The mismatching copy is never admitted or repaired. Nine
other individually verified extracted inputs are read-only links, reverified
before use. The original parent archive remains failed/quarantined.

## Ordinary focused controls

```bash
python -m pytest -q tests/test_grudeva2026_full_reference_010.py \
  tests/test_grudeva2026_dense_capture_010.py
python -m ruff check puckworks/ tests/ \
  tools/run_grudeva2026_full_reference_010.py \
  tools/diagnose_grudeva2026_dense_capture_010.py
python -m mypy
python -m pytest -q -m 'not slow and not live and not gpu and not external_data'
```

The existing full-reference test file invokes 17 bounded trajectories / 19
solve_ivp segments; the ordinary quick selector includes 15 / 15. The new dense
diagnostic tests invoke zero integrators: their run_row integration call is a
synthetic stub, explicitly separated from real solver execution. Fault injection
is confined to newly constructed test fixtures. Use a new `--basetemp` if retaining
their small failure artifacts. Fresh child processes exercise capture -> runner
failure -> process exit; another process safely reloads and reproduces witnesses.

## Reading failure evidence

Read `failure.json` first, then `capture-quarantine/FAILURE.json` and
`PRESERVATION.json`. They distinguish prospective source, source-after and
completed-target identities; component/segment/interval; metadata/padding;
source/target layouts and aliasing; exact current-byte differences versus
digest-only discrepancies. Prior bytes are available only through a named
immutable input, not inferred from a previous checksum. Numeric witnesses and
checked snapshots use NPY with `allow_pickle=False` and exact payload checks.
Secondary write failures and missing evidence remain explicit. A quarantine
has no successful `manifest.json` and cannot pass the qualified-reference loader.

`EXTRACTION_COMPARISON.json` retains independent raw ZIP/copy hashes, count 54
and the first 32 exact float-byte witnesses. `extraction-witnesses.npz` is a safe
numeric rendering of those recorded hex bytes/offsets; load with
`np.load(path, allow_pickle=False)`. Both complete original/copy payloads remain
available for further authorized inspection. These are serialized offsets, not
process-memory or hardware addresses, and no common mechanism with either
historical failure has been established.
