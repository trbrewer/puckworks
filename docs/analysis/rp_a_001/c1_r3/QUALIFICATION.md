# C1-R3 qualification

- Focused response-atlas suite: **82 passed**, zero failed, 44.09 s. The added
  route fixture obtains apparatus rule-out from the production evaluator before
  dynamic/spatial decision selection; it does not inject terminal apparatus status.
- Full supported suite on the final execution-code head: **4,267 passed,
  31 skipped, zero failed**, six warnings, 2,776.72 s (wall 2,778.39 s).
- Environment: Python 3.12.3, NumPy 2.2.6, SciPy 1.15.3; editable source
  through `/tmp/rpa001-venv`.
- Ruff: passed.
- Mypy: passed for all 12 response-atlas source modules.
- Registry/cards: 27 components; PASS=65; ACKNOWLEDGED_EXCEPTION=1.
- Generated status: verified.
- Deterministic v5 atlas: `RP_A_001_VERIFY_OK`; byte stable.
- README governance and pulse: passed.
- Insight verification: passed.
- Paper 3 registry/build bundle: passed with zero problems and warnings.
- Local packaging/security executables (`build`, `pip_audit`) were not installed
  in the supported analysis venv; the corresponding corrected-head GitHub
  packaging and security jobs are authoritative and must pass before handoff.

Warnings were the established Matplotlib Axes3D/import and open-figure notices,
three SciPy BDF subtraction warnings, and the development visualizer salt notice.
No numerical producer failure occurred.
