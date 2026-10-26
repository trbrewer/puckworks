# Reproduction and artifact guide

Use Python >=3.10 and `pip install -e '.[dev,reconstruct,figures]'` in the
reviewed checkout. Resolve originals using the existing owner data-source
configuration or `PUCKWORKS_EXTERNAL_DATA_ROOT`. Keep the fresh evidence and
output directories outside Git. No EWP checkout or execution is needed.

```bash
python -m pytest -q tests/test_pannusch_fair_tds.py tests/test_pannusch_equilibrium_limit.py
python tools/pannusch_fair_tds.py prepare --private "$EVIDENCE_DIR" --output "$OUTPUT_DIR"
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python tools/pannusch_fair_tds.py fit \
  --private "$EVIDENCE_DIR" --output "$OUTPUT_DIR"
python tools/pannusch_fair_tds.py freeze --private "$EVIDENCE_DIR" --output "$OUTPUT_DIR"
# Independent review records pre_score=APPROVED in OUTPUT_DIR/REVIEW.json.
python tools/pannusch_fair_tds.py score --private "$EVIDENCE_DIR" --output "$OUTPUT_DIR"
```

The initial run uses this directory as output; `--output` preserves it during
reproduction. Existing preparation/fits/freeze/score receipts cannot be silently
replaced. Reproduction creates new execution/timing hashes; the original frozen
scientific result remains historical. No expanded search, repeated target-driven
fit or second empirical comparison is authorized by these commands.

`CONFIG.json` specifies ranges, starts, objective, optimizer budget, reduction
rule, numerical settings, grading and uncertainty rules. No probabilistic priors,
Sobol indices or parameter CIs are estimated. `PARAMETERS.json` retains all starts,
convergence messages, local training sensitivity and fitted parameters. The source
kinetic constants in E's dictionary are ignored by its analytical prediction;
E has three permitted parameters, not seven. F has seven before any declared
training-only reduction. Inventory profiling removes one optimizer dimension,
not one fitted degree of freedom. B has six training-derived fraction means.

`SOURCE.json` identifies originals and accepted exports. Prepared target inputs
contain only conditions, windows and masses. Mixed source files are parsed, but
evaluation chemistry is neither returned to the predictor nor used for fitting,
selection, numerical settings or scoring before freeze. All observed-window gaps
are propagated. Each condition reuses one trajectory over replicate boundaries.

`FREEZE.json` binds code/configuration/source/input/fit/prediction identities before
the first evaluation score. `NUMERICS.json` reports training-only grid, time,
conservation and independent physical-coordinate checks, including admissible
optimizer starts. N200 fits and N800 scored predictions are distinct; fine-grid
training losses are reported without refitting or changing selection. E is an
exact analytical front, including initial liquid inventory and exact overlap.
Its arithmetic allowance and F's engineering allowance are not measurement CIs.

`SCORES.csv` contains balanced R/B/A overall and for every condition; `TRAINING.csv`
contains grouped fitted diagnostics. R is the mean of shot RMSEs, while fitting
minimizes mean shot squared error. A is mean absolute shot bias, not absolute
mean bias. `GAINS.csv`, `THRESHOLDS.csv` and `RESULTS.json` retain all reporting
variants and descriptive spread. Each omission retains complete physical shots,
all fractions and all arms, with equal-condition reweighting and no refitting.
The figure shows three-shot condition means. Lines connect fraction summaries;
they are not continuous-time curves or complete-cup profiles.

Private evidence retains individual shot R/B/A, all 17 paired cohort reductions,
all predictions, actual windows/masses, original joins and detailed logs. Public
projection omits private originals, raw records, detailed predictions and locators.
Pannusch/Schmieder-derived aggregates retain CC-BY-NC-3.0 and attribution to
Pannusch et al., Mendeley DOI 10.17632/y2tz67f6ry.1. First-party software licensing
is separate. Cameron's retained evidence is assessed separately in CAMERON.md.
