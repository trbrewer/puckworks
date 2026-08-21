# C1-R2 qualification

The v4 result was executed from commit
`a8f2679985948bf82443aee30f35ff4e504fc74a` (tree
`0707f3b3a1bfa5b4f2887c46d40bdbf5402e101e`) and retained by commit
`326662eb6af2dc74ccfd9a795cb1ce1863cc8450` (tree
`4cffbade03ee1bb6096465faaa8fbac01993319b`).

Environment: CPython 3.12.3, NumPy 2.2.6, SciPy 1.15.3, editable checkout in
`/tmp/rpa001-venv`.

- Focused atlas suite: 62 passed in 33.66 s.
- Full suite: 4,247 passed, 31 skipped, 6 warnings, zero failed in 2,757.82 s
  (wall 2,759.51 s).
- Ruff: passed.
- Mypy: passed for 19 source files.
- Registry/card gates: 65 PASS, 1 ACKNOWLEDGED_EXCEPTION; 27 components.
- Generated status verification: passed.
- Deterministic v4 verification: `RP_A_001_VERIFY_OK`.
- README governance and pulse: passed.
- Insights verification: passed.
- Paper bundle verification: passed with no problems or warnings.

The six pytest warnings are the existing Matplotlib Axes3D/import and open-figure
warnings, three SciPy BDF runtime warnings in release tests, and the expected
development-salt warning. No unrelated bulk formatting was performed.

Corrected-head GitHub results are retained on PR #244 and issue #243 after they
reach terminal state; committing those operational results would create another
head and retrigger CI. This record does not self-approve the head, authorize EWP
mutation, or authorize merge. Physical validation remains `NOT_ESTABLISHED`.
