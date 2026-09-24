# Source-conditioned fines-intervention endpoint transfer

Use Python 3.12 with the repository's NumPy/SciPy dependencies and `dev,figures`
extras. The exact executed versions are retained in SYNTHETIC_QA.json and the
prediction receipt. Run from the Puckworks checkout:

```bash
python -m venv .venv
.venv/bin/pip install -e '.[dev,figures]'
.venv/bin/python -m pytest -q tests/test_smrke2024_transfer.py
.venv/bin/python -m puckworks.analysis.smrke2024_transfer prepare --output /tmp/smrke-transfer-reproduction
# Requires the genuine independently authored AUDIT.json covering FREEZE.json.
.venv/bin/python -m puckworks.analysis.smrke2024_transfer fit-predict --output /tmp/smrke-transfer-reproduction
# Predictions and PREDICTION_RECEIPT.json now exist; inspect/hash before scoring.
.venv/bin/python -m puckworks.analysis.smrke2024_transfer score --output /tmp/smrke-transfer-reproduction
.venv/bin/python -c 'from pathlib import Path; from tools.plot_smrke2024_transfer import render; render(Path("/tmp/smrke-transfer-reproduction"))'
```

The output directory must be new; scientific artifacts are exclusive writes.
No live-source download or native build/run is part of reproduction. Reproduction
is an explicitly labeled rerun of public comparisons, not fresh validation.
Prepare uses the existing loader but only Figure 3 markers enter the models.

[Contract](CONTRACT.md), [source preflight](SOURCE_USE.md),
[source identities](SOURCE.json), [all observations](observations.json), and
[pre-fit support masks](support.json) define the bounded analysis.
Results are recorded in RESULT.md after the audited computation.

The `Fitted.parameters` tuple is (E_inf, A, tau[, beta]) for M0/M1 and
(b0, b1, b2[, gamma]) for B0/B1, in the displayed unscaled equations. The typed
Covariate/Observation/Fitted API rejects incompatible units/source labels.
Fitted predictions carry separate time/intervention support and fitted-source
identity; support flags never turn source conditioning into universal validity.

Figures are analysis comparisons, not mechanism renders: `endpoints.png` shows
across-shot endpoint curves trained only at 0 g, with unambiguous circles and
ambiguous crosses. `residuals.png` distinguishes time extrapolation.
`errors.png` shows central errors and the finite tested digitization sensitivity
range, not confidence intervals. `source_overlay.png` labels unchanged source
pixels and historical CSV lines; the original digitizer's overlay was unavailable.
No full-data fit is presented as validation.
