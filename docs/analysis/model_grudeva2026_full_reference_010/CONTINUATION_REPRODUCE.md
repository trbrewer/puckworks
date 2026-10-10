# Reproduce the 010 continuation

This continues draft PR #333 and the original G2 task. The original
[MATRIX.json](MATRIX.json) remains byte-for-byte unchanged (SHA256
`092269b20b88d413abbfb1350240d32ab869e985cf1825ef1f28f73462e667d3`).
[CONTINUATION.json](CONTINUATION.json) prospectively binds the three permitted
implementation changes, unchanged environment, original failure, controls and
execution order. It is not a new scientific matrix. No physics, solver setting,
observation support, limit or error-budget definition changes.
PHYSICAL_VALIDATION=NOT_ESTABLISHED.

Use the existing source/evidence configuration and retained execution records to
resolve external evidence. Private mounted paths are intentionally absent here.
Set `FULL010_ARCHIVE_ROOT` to the identified continuation campaign directory for
inspection, or to a **new, exclusive** directory for an authorized reproduction.
Never point a new run at the original failed archive or an existing row directory.

## Inspect retained evidence without integrating

The original archive, diagnostic records, frozen source and closeout remain
unchanged. The current v1 reader still rejects its stale accepted-state identity.
A new v2 archive is successful only when `manifest.json` exists and every source,
file, raw numeric payload, loaded array, layout and redundant-state check passes.
`WRITE_START.json`, `SOURCE_COMMITMENT.json`, or directory presence alone are not
completion evidence. `INCOMPLETE_MANIFEST.json` retains partial returned solver
states and is deliberately not accepted as a completed trajectory.

```bash
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONPATH=.
python - <<'PY'
import os
from pathlib import Path
from puckworks.analysis.grudeva2026_full_reference_010_io import load_archive
root = Path(os.environ['FULL010_ARCHIVE_ROOT'])
trajectory, manifest = load_archive(root/'anchor/trajectory')
print(manifest['schema'], manifest['metadata'])
print([(len(s['t']), float(s['t'][0]), float(s['t'][-1]))
       for s in trajectory.segments])
PY
```

The independent raw NPY reader hashes the canonical C-order numeric payload;
the safe NumPy loader uses `allow_pickle=False`. Stored bytes have **zero allowed
change**, including signed zero. Dense-interpolant evaluations are separately
checked against the original scale-aware allowance. Neither NaN availability in
observation bundles nor their boolean masks permits an unexplained byte change.
Observation/diagnostic NPZ bundles have prospective `.source.json` commitments
and independently checked raw ZIP-member and loaded numeric identities.

## Ordinary controls and software QA

```bash
python -m pytest -q tests/test_grudeva2026_full_reference_010.py
python -m ruff check puckworks/ tests/
python -m ruff check tools/run_grudeva2026_full_reference_010.py
python -m mypy
python -m pytest -q -m 'not slow and not live and not gpu and not external_data'
```

The focused command executes 17 bounded trajectories / 19 `solve_ivp` segments,
including a fixed-settings paired capture/no-capture fixture through t=1.01.
The ordinary quick selector excludes that slow pair and executes 15 bounded 010
trajectories / 15 segments. These are software/control executions, not scientific
matrix rows. The large serialization diagnostic is solver-free and separate:
one representative (24834,18003) float64 payload and one 2**32+257-byte uint8
payload. Its retained script/plan/results and scoped reuse proof are recorded in
[CONTINUATION_CONTROLS.json](CONTINUATION_CONTROLS.json) and
[CONTINUATION_LARGE_TEST_REUSE.json](CONTINUATION_LARGE_TEST_REUSE.json).
Do not repeat that multi-gigabyte diagnostic just to reproduce an established
finding.

## Explicit scientific execution

Use the environment exactly bound in the original matrix and continuation.
The runner checks Python, NumPy/SciPy distribution records, BDF source, thread
settings, original matrix and current implementation hashes, and both required
independent pre-execution review receipts. There is no ignore-hashes option.
Do not run `freeze` over the original matrix.

The authorized sequence is one separately identified replacement anchor, then
thirteen outstanding rows in `row_order`; repeat is a separate integration.
The retained external supervisor runs these commands serially with actual
memory/disk monitoring and no automatic retry. Each runner also checks current
host/cgroup limits and conservative buffer/archive admission estimates.

```bash
python tools/run_grudeva2026_full_reference_010.py run \
  --archive-root "$FULL010_ARCHIVE_ROOT" --row anchor --continuation
```

After the anchor's complete integrity and audit path succeeds, execute only the
remaining rows in the immutable order. A numerical gate failure is recorded in
`results.json` and does not suppress computable observations or independent rows.
A nonzero process exit is a pipeline/integrity/integrator failure: retain it and
stop; do not blindly retry or skip to another row.

```bash
python - <<'PY'
import json, os, subprocess, sys
from pathlib import Path
matrix = json.loads(Path('docs/analysis/model_grudeva2026_full_reference_010/MATRIX.json').read_text())
for row in matrix['row_order'][1:]:
    subprocess.run([sys.executable, 'tools/run_grudeva2026_full_reference_010.py',
                    'run', '--archive-root', os.environ['FULL010_ARCHIVE_ROOT'],
                    '--row', row, '--continuation'], check=True)
PY
python tools/run_grudeva2026_full_reference_010.py report \
  --archive-root "$FULL010_ARCHIVE_ROOT" --continuation
```

Reporting revalidates saved results, prospective observation identities and full
trajectory archives before reference comparisons. Its output is written
exclusively as `RESULTS.json`; do not invoke it again over an existing report.
Solver-start, solver-end, archive, observation and numerical-gate statuses must
be counted separately.

For the **original exact-freeze path**, use the retained `frozen-source-v1` or an
isolated extraction of commit `9b5ef8db725afaad3238494abcb43f2dd6c3e1f5`, and the
original [REPRODUCE.md](REPRODUCE.md). Omit `--continuation` there: its original
implementation/environment checks remain mandatory. Inspection of the old
failure is authorized; these instructions do not authorize another historical
scientific rerun or repair its outcome.
