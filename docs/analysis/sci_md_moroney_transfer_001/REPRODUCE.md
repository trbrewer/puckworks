# Reproduction and execution boundary

Use a fresh environment and install the repository's existing dev and figures
extras (`python -m pip install -e '.[dev,figures]'`). For the exact reviewed
execution environment, install NumPy 2.5.3 and SciPy 1.18.1 on Python 3.12.3;
the CLI refuses a changed numerical environment after freeze. No dependency
lock changes.
For local PDF inspection only, optional PyMuPDF can be installed separately;
no PDF or copyrighted page image is redistributed here.

```
python -m pytest -q tests/test_moroney_transfer.py tests/test_moroney2015_batch.py tests/test_moroney2019_ldf.py
python -m puckworks.analysis.moroney_transfer_run qualify
python -m puckworks.analysis.moroney_transfer_run verify --output verification.json
python -m puckworks.analysis.moroney_transfer_run freeze
```

`qualify` reproduces the task-local mapping without editing source CSVs. Current
four legend exclusions remain pending. When original figure-object evidence is
available, record PDF SHA256, printed/page indices, tick/marker coordinates,
visual inspection outcome and exact confirmed rows in `source_objects.json`.
Do not use concentration residuals for qualification. Review the selected deep
panels for analogous contamination. Freeze the resulting **complete** contract
before the independent pre-scoring audit.

Only after that review, whose JSON contains `decision: APPROVED_FOR_SCORING`,
`reviewer`, `freeze_sha256`, and `thresholds_accepted: true`:

```
python -m puckworks.analysis.moroney_transfer_run predict --review REVIEW.json --output NEW_RESULT_DIRECTORY
python -m puckworks.analysis.moroney_transfer_run score --output NEW_RESULT_DIRECTORY
```

The first command fits deep only, preserves starts and alternatives, generates
all shallow trajectories without target columns and hashes the output. The
second verifies hashes and writes scores once, decisions and three VizSpec-bound
figures. Results, costs and environment are emitted as JSON. A genuine independent
reviewer must author the approval; this is not an instruction to manufacture it.
Current `source_ready: false` refuses prediction even if an approval is supplied.

The current committed numerical artifacts are synthetic control results, not
transfer predictions. `verification.json` and `verification_observed_support.json`
retain the exploratory coarse meshes; `verification_primary.json` uses the
primary declared meshes. The observed-support probe uses mass coordinates only.
No primary scored candidate or fitted-parameter file exists yet.

The primary observed-support and tightened-tolerance control results are in
`verification_primary_observed_support.json`; they are model-to-model checks.
