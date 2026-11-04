# Calculation verification and reproduction

The approved plan amendment was committed as `8c48550` before numerical evaluation.
The native-image readings and their graphical perturbation contract were fixed
before fitting. No Waszkiewicz parameters were fitted, no CFD was run, and no
scientific gate or acceptance threshold was added.

- **10 task tests pass.** They check the 100000 Pa/bar conversion, independent
  amplitudes, known affine/threshold/power cases, boundary cases, the Q-space
  exponent reference (including distinction from log–log regression), shared
  panel calibration, fixed central normalizers and serialized paired contrasts.
- `NUMERICAL_CHECK.csv`: separate linear algebra reproduces the one-parameter
  amplitudes; nonlinear least-squares refinement checks the two-parameter central
  solutions. The largest RMSE difference is **1.403e-21 m³/s**. This checks the
  implemented calculations, not physical validity or a new accuracy gate. The
  refinement starts at retained solutions and is not an independent global-search
  proof. The production scalar profiles inspect every detected local bracket and
  the declared domain limits.
- Every draw uses all 12 series and the same central S² values. An independent
  serialized-output audit reproduces the pooled D and its quantiles and checks
  m−m_FA within each realization. No intervals are subtracted after aggregation.
- A full second evaluation of central fits and all 4096 realizations reproduced
  every numerical CSV byte for byte (`DETERMINISM.json`). Both retained result
  bundles render the same final figure. Presentation-only edits strip SVG
  whitespace, name the VizSpec producer module and label counts as **means**;
  input module hashes were refreshed without changing numerical results.
- The native overlay and the final 12-panel figure were visually inspected.
  Source SD caps remain separate from mean-reading uncertainty. No SD enters
  a fitting weight. Unrecoverable SD caps and marker/step coverage remain explicit.
- `REPRODUCTION.json` records Python/NumPy/SciPy versions, source and calculation
  input hashes (including the exact D0 saved-result file), output hashes and the
  separate numerical check. The large paired-realization CSV is derived output,
  not reconstructed bed samples. Original source PDFs/images remain external;
  the attributed source-reading overlay is a CC BY 3.0 adaptation.

Reproduce the complete calculation and report from the repository root:

```sh
python -m puckworks.analysis.cor15_shape_001
python tools/report_cor15_shape_001.py
python tools/verify_cor15_shape_001.py
python -m pytest -q tests/test_cor15_shape_001.py
```

The analysis requires NumPy/SciPy and Matplotlib for the figure. Native-overlay
regeneration additionally requires PyMuPDF/Pillow and the hash-matched local PDF;
its command is in the intake provenance. No PDF is needed to reproduce fits.

`MODELS.csv` uses SI flow for RMSE/residual fields; amplitude units are explicit
per row. `RESIDUALS.csv` retains all signed point residuals. `PAIRED_DIMENSIONAL.csv`
reports paired FA−L0 MSE and RMSE differences; `CONTRASTS.csv` reports normalized
D and matched exponent intervals. All reading intervals condition on the stated
pixel perturbation measure. Neither those intervals nor the much smaller numerical
check quantify source measurement uncertainty.

Repository closeout: the broad offline selection (`not slow and not live and not
release and not gpu and not external_data`) completed with 8008 passed, 33 skipped
and ten stale generated-artifact failures after the manifest addition. The required
data-register/family-index/guide, manuscript-count, claim-audit and insight
projections were regenerated. **All ten failed checks plus the ten task tests
passed on recheck (20 passed)**; the wider affected projection checks also passed
(71 tests). The release-only selector contained no tests. Repository Ruff and
`git diff --check` are clean. These are software checks, not scientific grades.
