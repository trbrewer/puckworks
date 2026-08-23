# C1 qualification record

Environment: Python 3.12.3, NumPy 2.2.6, SciPy 1.15.3, Matplotlib 3.11.1,
pytest 9.1.1; repository installed with `python -m pip install -e .`.

- `python -m pytest tests/test_response_atlas.py tests/test_response_atlas_c1.py -q`:
  34 passed in 24.20 s.
- focused producer/registry regression selection (`test_gates`, Fo_F contract,
  global-state, Lab runner contract and authority): 51 passed in 224.76 s.
- first full-suite attempt before editable installation: 4,218 passed, 31
  skipped, 1 failed in 2,697.84 s. The sole failure was
  `test_generated_pulse_block_is_current`: a subprocess launched from `tools/`
  could not import the checkout because the venv lacked the editable install.
  This was an environment setup failure, not a source/scientific failure.
- isolated gate after `python -m pip install -e .`: 1 passed in 39.00 s.
- authoritative complete rerun, `python -m pytest -q`: 4,219 passed, 31
  skipped, 0 failed, 6 warnings in 2,743.87 s.
- `ruff check .`: passed.
- `python -c "from puckworks.registry import components,run_all_gates; ..."`:
  27 components; PASS=65, ACKNOWLEDGED_EXCEPTION=1.
- `python -m puckworks.statusdoc --verify`: passed.
- `python -m puckworks.analysis.response_atlas verify`: passed.
- `python -m puckworks.insights verify`: passed.
- `python tools/update_readme_pulse.py --verify`: passed.

Warnings were existing/declared: unavailable Matplotlib Axes3D from multiple
install locations, more than 20 Paper-B figures open, three SciPy BDF invalid
subtract warnings in release tests, and the development visualizer salt warning.
No warning was promoted to a pass or suppressed.
