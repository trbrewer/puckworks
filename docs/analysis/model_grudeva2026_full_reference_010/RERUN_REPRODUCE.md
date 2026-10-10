# Controlled scientific rerun — 010

This owner-authorized continuation uses the original `MATRIX.json` unchanged.
`RERUN.json` binds the actual executable/environment and three affected files,
reused reviews/controls, fresh external evidence directory, and the order
**anchor, repeat, twelve remaining rows in their original relative order**.
There are fourteen distinct authorized new executions. No automatic retry is
allowed. Historical accounting remains two full trajectories / four BDF segments.
PHYSICAL_VALIDATION=NOT_ESTABLISHED.

The unchanged source contract and mathematical reviews are reused. The external
evidence configuration identifies the fresh campaign path; its absolute-path
SHA256 is bound without publishing a private locator. Use the existing bound
Python executable with `OPENBLAS_NUM_THREADS=1`, `OMP_NUM_THREADS=1`, and
`MKL_NUM_THREADS=1` in the isolated checkout. No dependency installation or
resource-limit changes are part of reproduction.

The retained external `execute.py` adapts the prior serial supervisor, holds its
execution lock, checks actual headroom and accessible new kernel error evidence,
and launches each row once in a fresh process. The runner verifies the specific
binding and exact source/environment identities. `--rerun` is not an integrity
bypass. Do not regenerate the original matrix or point a new execution at an
existing row directory. The binding is for this specific bounded attempt;
commands below describe its predeclared conditional sequence, not authorization to repeat it. Only the anchor executed; repeat and repeat-check were NOT_RUN after the archive-writer stop.

```bash
"$FULL010_PYTHON" tools/run_grudeva2026_full_reference_010.py run \
  --archive-root "$FULL010_ARCHIVE_ROOT" --row anchor --rerun
"$FULL010_PYTHON" tools/run_grudeva2026_full_reference_010.py run \
  --archive-root "$FULL010_ARCHIVE_ROOT" --row repeat --rerun
"$FULL010_PYTHON" tools/run_grudeva2026_full_reference_010.py repeat-check \
  --archive-root "$FULL010_ARCHIVE_ROOT" --rerun
```

The supervisor advances only after successful integrity, integration and required
support. It revalidates both full archives for the repeat comparison and compares
scientific arrays/observations, excluding timestamps. Finite numerical gate
failures remain failures and may be characterized by the remaining declared
refinements. Unexplained integrity mismatches, integration/nonfinite-state failure,
missing required support, repeatability failure, active system/I/O errors and
unsafe resources stop the attempt without another trajectory.

Immediately after the solver returns, `solver-end.json` records segment/time
counts. `checkpoints/SOURCE_COMMITMENT.json` precedes accepted t/y writes;
`checkpoint.json` identifies exact payloads. A fresh process safely reloads and
verifies them and writes `PROVISIONAL.json`, labelled
**PROVISIONAL — NOT FULL_REFERENCE_QUALIFICATION**. Its accepted-state balance
uses model phase inventories and evolved accumulators. Its sampled evolution and
all-native extrema are diagnostic summaries, not the independent final flux audit.
Dense capture failures preserve these files and the existing structured witnesses.

On the successful archive path, verified accepted files are hardlinked into the final archive. All source-before,
source-after, exact saved bytes, redundant states and interpolant checks remain.
The runner uses a fresh process to revalidate the full archive before observations/audits; final
bundles also receive fresh-process validation. Recomputed provisional summaries
use the original scale-aware arithmetic allowance; their underlying accepted
state bytes must match exactly. Final observations and independent inventory/
Gauss boundary-quadrature audits consume validated archive contents.

```bash
"$FULL010_PYTHON" tools/run_grudeva2026_full_reference_010.py report \
  --archive-root "$FULL010_ARCHIVE_ROOT" --rerun
"$FULL010_PYTHON" -m pytest -q tests/test_grudeva2026_full_reference_010.py
```

Reporting writes exclusively. Inspect existing JSON receipts rather than running
write commands again. The focused file includes the existing paired t=1.01
fixture demonstrating unchanged accepted times/states with checkpoint capture,
plus solver-free payload/source/failure controls. The unchanged large diagnostic
is reused, not rerun. Historical reproduction instructions and bindings remain
unchanged in `REPRODUCE.md` and `CONTINUATION_REPRODUCE.md`; quarantined historical
arrays are never new scientific inputs or reference data.

Matching readback and repeatability provide evidence for this execution contract,
not universal hardware reliability. Historical mechanisms and environment health
remain unresolved. PR #333 stays draft/unmerged, auto-merge disabled; #67 stays open.
