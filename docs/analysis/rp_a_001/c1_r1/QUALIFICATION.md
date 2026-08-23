# C1-R1 qualification

This record qualifies the retained C1-R1 v3 result generated from execution commit
`a6e6cd1c46121a9338e4e8358bc68b9ad56d8e55` (tree
`c454deefc1a603ea4484b35a8ab3e455af1f66f6`). The result commit is
`a655c1d967cc7e51a376e0f3f76ffb6750800da2` (tree
`44d38385d371b5e3353826bea74c1afa690c66c0`).

Environment: CPython 3.12.3, NumPy 2.2.6, SciPy 1.15.3, editable checkout in
`/tmp/rpa001-venv`.

Local qualification completed on 2026-08-21:

- `pytest -q tests/test_response_atlas.py tests/test_response_atlas_c1.py tests/test_response_atlas_c1_r1.py`: 57 passed in 31.90 s.
- `pytest -q`: 4,242 passed, 31 skipped, 6 warnings, 0 failed in 2,753.12 s (wall 2,754.81 s).
- `ruff check .`: passed.
- `mypy`: passed, 19 source files.
- registry/card gates: passed (65 PASS, 1 ACKNOWLEDGED_EXCEPTION; 27 components).
- `python -m puckworks.statusdoc --verify`: passed.
- `python -m puckworks.analysis.response_atlas verify`: `RP_A_001_VERIFY_OK`.
- README governance and pulse verification: passed.
- `python -m puckworks.insights verify`: passed.
- `python -m puckworks.paper3.build verify`: passed with no problems or warnings.

The six pytest warnings are the existing Matplotlib Axes3D/import and open-figure
warnings, three SciPy BDF runtime warnings in release tests, and the expected
development-salt warning in the visualizer-harvest test. A repository-wide
`ruff format --check .` is not a clean-tree gate: it reports 455 pre-existing
files outside this correction as requiring formatting. The enforced Ruff lint
gate passed and no unrelated formatting rewrite was made.

GitHub corrected-head checks are recorded in PR #244 and issue #243 after they
reach terminal state; adding those operational results here would itself create
a new head and retrigger the checks.

Physical validation remains `NOT_ESTABLISHED`. This qualification does not
self-approve the head, authorize EWP mutation, or authorize merge.
