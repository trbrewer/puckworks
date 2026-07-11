# validation/slow — heavy ladders (NOT in CI)

Anything here is opt-in: run by hand or in `notebooks/espresso_lb_colab.ipynb`.
CI runs **only** the quick gates in `puckworks/validation/gates.py`
(`QUICK`, target < ~30 s total). See CLAUDE.md rule 3 and ROADMAP §0.

## What belongs here (slow)
- GPU / taichi sweeps (the `[lb]` extra); anything needing hardware CI lacks.
- Resolution / convergence studies (sphere-array LB resolution, ε-convergence
  sweeps) that take minutes+.
- Twin-solver cross-checks (`lb_reference` vs `lb_taichi`) and full pack
  cross-validation.
- Full-grid Sweeps A/B (Colab-queued) and any run whose wall time or memory
  makes it unfit for the ~30 s commit gate.

## What does NOT belong here (put in `../gates.py`)
- Fast, deterministic, CPU-only checks that finish well within the ~30 s budget
  and can gate every commit.

## Conventions
- Modules here must **import** cleanly without taichi (per CLAUDE.md); guard the
  optional import at call time, not module top level.
- Do not add anything here to the `QUICK` list or to `tests/`. Nothing in this
  directory may be a CI dependency.
- A slow ladder that later needs to gate status promotions still records its run
  in ROADMAP §7.1 with the dataset + script, same as a quick gate.
