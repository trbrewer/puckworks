# Reproduction and execution boundary

Use a fresh environment and install the repository's existing dev and figures
extras (`python -m pip install -e '.[dev,figures]'`). For the exact reviewed
execution environment, install NumPy 2.5.3 and SciPy 1.18.1 on Python 3.12.3;
the CLI refuses a changed numerical environment after freeze. No dependency
lock changes.
For local PDF inspection only, optional PyMuPDF can be installed separately;
no PDF or copyrighted page image is redistributed here.

```
python -m pytest -q tests/test_moroney_transfer.py tests/test_moroney_transfer_report.py tests/test_moroney2015_batch.py tests/test_moroney2019_ldf.py
python -m puckworks.analysis.moroney_transfer_run qualify
python -m puckworks.analysis.moroney_transfer_run verify --output verification.json
python -m puckworks.analysis.moroney_transfer_run freeze
```

The original PDF has been supplied and audited. `source_objects.json` records
its SHA256, printed/page indices, major-tick anchors, drawing/subpath identities,
all selected row matches and the four confirmed legend rows. The PDF and raster
pages are not redistributed. With PyMuPDF, inspect `document[3].get_drawings()`
for Fig3 and `document[17].get_drawings()` for Fig11; the coordinate convention
and split-subpath method are in the source audit. Source CSV coordinates are
preserved, including signed near-zero values. `qualify` regenerates only the view.

The independent approval is `review/pre-scoring-approval.json` and binds the
source-qualified scientific freeze. To reproduce the bounded comparison, use a
**new empty result path**, keeping the recorded result immutable:

```
python -m puckworks.analysis.moroney_transfer_run predict --review docs/analysis/sci_md_moroney_transfer_001/review/pre-scoring-approval.json --output NEW_RESULT_DIRECTORY
python -m puckworks.analysis.moroney_transfer_report inventory --output NEW_RESULT_DIRECTORY
python -m puckworks.analysis.moroney_transfer_run score --output NEW_RESULT_DIRECTORY
python -m puckworks.analysis.moroney_transfer_report summary --output NEW_RESULT_DIRECTORY
python -m puckworks.analysis.moroney_transfer_report figures --output NEW_RESULT_DIRECTORY
```

The first command fits deep only, preserves starts and alternatives, generates
all shallow trajectories without target columns and hashes the output. The
inventory command audits the separate reservoirs without target concentrations.
The score command verifies hashes and writes scores once, decisions and three
VizSpec-bound figures. Results, costs and environment are emitted as JSON. A genuine independent
reviewer must author the approval; this is not an instruction to manufacture it.
The approved source-qualified freeze has `source_ready: true`; any changed frozen
dependency or numerical environment is rejected.

The top-level `verification*.json` artifacts are synthetic control results,
separate from the executed transfer result under `results/`. `verification.json` and `verification_observed_support.json`
retain the exploratory coarse meshes; `verification_primary.json` uses the
primary declared meshes. The observed-support probe uses mass coordinates only.
Executed fit records, immutable predictions, one-time scores and decisions are
in `results/`. Completed fits checkpoint during prediction; a checkpoint alone
is not a completed prediction freeze and cannot be scored.

The primary observed-support and tightened-tolerance control results are in
`verification_primary_observed_support.json`; they are model-to-model checks.

`moroney_transfer_report` is a reporting and reservoir-audit companion. It never
fits, changes prediction trajectories, or selects parameters from target scores.
The inventory phase repeats only frozen admitted parameter sets and verifies
trajectory identity, retaining separate reservoirs at observation mass support.
Its additional solver cost is recorded. Summary/figures consume the completed
once-only score file. Figure ranges span the declared finite family and numerical
allowances; they are not experimental confidence intervals. The reporter code
hash is recorded separately from the pre-scoring scientific freeze.

`published_control.json` records the separate A reconstruction control at three
meshes with copied Table2 constants, compared only to the Fig7 fitted model line.
It has its own explicit initial soluble mass, is not a predictive calibration,
and was not substituted for any B initialization family. Its command calls
`moroney_transfer.solve(..., amplitude=1, published_control=True)` at the native
Fig7 model-line masses with 480/960/1920 cells; outlet conversion uses rho=965.3.
