# Reproducing and reading 010

This analysis is not registered as a runtime component. It changes no production
physics, defaults or dependency locks. PHYSICAL_VALIDATION=NOT_ESTABLISHED.

Use the exact candidate commit identified in the handoff/PR receipt, or the
external `frozen-source-v1` snapshot. MATRIX.json records the source hashes,
NumPy/SciPy installation identities, BDF implementation, Python/platform and
single-thread environment. It contains the complete synthetic case, all 14 rows,
physical observation coordinates, event conventions and numerical limits.
Source material and old 004–009 trajectories are not inputs to this campaign.
The full-equation operators and observer are independent of the reduced solver:
no reduced dynamics are imported. Existing 004–009 contracts/archive interfaces
were consulted for reporting and evidence conventions. NumPy, SciPy BDF, JSON,
SHA256 and numeric NPZ are reused generic facilities, not correctness oracles.

Set `ARCHIVE_ROOT` to a **new** external directory. The runner uses exclusive
row directories and a serial lock. Never overwrite a retained row. Retained
failures are evidence; a rerun needs an explicitly identified correction/reuse
record. No expensive campaign is launched by ordinary quick CI.

```bash
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
export PYTHONPATH=.
python -m pytest -q tests/test_grudeva2026_full_reference_010.py

# Reproduce the one actually attempted row in a new external directory:
python tools/run_grudeva2026_full_reference_010.py run \
  --archive-root "$ARCHIVE_ROOT" --row anchor
# The original run stopped at its archive-integrity exception.
python tools/run_grudeva2026_full_reference_010.py report \
  --archive-root "$ARCHIVE_ROOT"
```

Only `anchor` was attempted; the other 13 rows in MATRIX.json are **NOT_RUN**.
No automatic continuation or speculative rerun was launched. A fresh execution
has its own identities and cannot retroactively repair the retained failed run.
The original anchor archive occupies 27,685,312,970 bytes. Highest observed RSS
in the one-second external monitor was 91,653,436 KiB; this is a sampled value,
not a measured continuous peak or a new resource quota.

`freeze` is the producer's prospective operation, not a reproduction step: do
not regenerate or weaken the committed matrix after viewing results. Execution
checks its source/environment identities and independent pre-campaign review.
A changed environment requires an explicit new reproduction identity; it is not
silently accepted as exact repeat evidence. No resources were purchased and no
OS/hosting limits were increased for 010.

Archive inspection does not execute a solver. The retained anchor intentionally
fails strict loading with `ValueError("Archive state identity mismatch")`:

```python
from pathlib import Path
import json
from puckworks.analysis.grudeva2026_full_reference_010_io import load_archive

directory = Path(ARCHIVE_ROOT) / 'anchor' / 'trajectory'
manifest = json.loads((directory / 'manifest.json').read_text())
trajectory, manifest = load_archive(directory)  # Expected rejection for retained v1.
```

The failed candidate is quarantined. No qualified observation NPZ or numerical
audit was produced. The matching arrays and failure diagnostics are retained for
inspection, not promoted to a usable full-reference archive. Read RESULTS before
any reuse. No full-case output passed a precision requirement. Neither
refinement differences nor conditional Richardson estimates are rigorous
continuum-error certificates. New arbitrary queries are not automatically
qualified by storing an interpolant.

Raw solver state is cell-major **U=s*C**, followed by signed J_in and J_out.
The archive separately retains physical concentration arrays, physical axial
coordinates at accepted times, and radial shell faces/representative centers.
Grain states are spherical shell-volume averages. Radial means are computed
from those states, not from a mass complement. For t<=startup, requested
observations use the explicit startup approximation in CONTRACT; t=0 has no
liquid support. For dry grains and the exact newly wetted trace, concentration
is the declared initial value. Every positive wetting age uses the numerical
state and its frozen reconstruction.

`boundary_flux` columns are signed inlet, cup discharge, physical moving-front
or outlet, and relative ALE front/outlet flux. A zero relative moving-front flux
does not mean zero physical solute flux. Negative J_in is inlet loss. Cup
inventory is exactly zero through t=1; outlet concentration at t=1 denotes its
right-hand discharge limit. Before t=1 beverage concentration is unavailable.
Dry liquid values are NaN with an explicit wet-domain mask, not fabricated zeros.

`load_archive` verifies SHA256 file/array identities and uses only JSON and
numeric NPZ with `allow_pickle=False`. Accepted raw states are preserved exactly;
interpolant evaluation is tested separately with a scale-aware floating-point
allowance. No saved Python object, source file or pickle is executed on loading.
Full arrays/logs and private source locators stay outside Git.

The original source equation, synthetic parameter selection, mathematical
controls, numerical qualification and software QA have separate identities.
Preserved historical dispositions are CORROBORATED_PUBLICATION_DISCREPANCY and
FIG5_REFERENCE_INCOMPLETE. This archive supplies no reduced-model error estimate,
epsilon-validity range, publication discrepancy cause, physical validation,
production adoption or automatic successor.
