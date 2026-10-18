# Offline reproduction

Use an existing supported Python environment with NumPy and repository dev tools.
No dependency upgrade, source download or model inference is required. Run from
the addendum checkout with the existing owner configuration. The resolver reads
`PANNUSCH2024_MENDELEY_FULL_REPOSITORY`, then `PUCKWORKS_EXTERNAL_DATA_ROOT`,
then `sources.PANNUSCH2024_MENDELEY_FULL_REPOSITORY.path` in
`$XDG_CONFIG_HOME/puckworks/data_sources.json` (default `~/.config`). It reads only
the documented `5cqa-assay-002-evidence-20260929T163451Z/run-001` and named
public authorities. Missing optional records do not prevent core reduction.

```bash
export PYTHONPATH=.
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
python -m pytest -q tests/test_five_cqa_decision_resolution.py
python -m puckworks.analysis.five_cqa_decision_resolution --output "$NEW_PRIVATE_OUTPUT"
cmp "$NEW_PRIVATE_OUTPUT/RESULTS.json" \
  docs/analysis/val_case_5cqa_decision_resolution_001/RESULTS.json
```

`NEW_PRIVATE_OUTPUT` must identify a new directory outside every Git checkout and
the historical input directory. The CLI refuses an existing output directory.
No historical prepare/develop/freeze/score/verify/report command is invoked.
The historical verify command regenerates predictions and is excluded here.

The reducer writes INPUT_LOCATORS.json (actual private paths and hashes),
PRIVATE_RESULTS.json (all paired shots, eighteen deletion vectors, condition
contrasts, exact masks, optional residual and flag checks, full helper scopes),
RESULTS.json (public projection only), and completion.json (output bindings).
All reads are hash-checked before use and rechecked afterward. Historical source
bytes are never changed. The public manifest's explicit fallback filenames are
case-sensitive; a present mismatched file never falls back to a public copy.

Byte-identical public reproduction requires the same input locations, numerical
environment, specification and reducer because private locator/result hashes
are included in the public result. Relocation can change those hashes without
changing science. Compare actual scientific fields separately when appropriate;
never describe relocated output as byte-identical unless it is.

Focused tests use synthetic records exclusively. Full ordinary repository tests,
lint, maintained type checks, generated artifacts and registry gates are separate
software checks recorded in HANDOFF.md. Hosted CI is separately reported at the
draft PR's exact head. These checks do not constitute model validation.

The source-derived aggregates retain Pannusch/Schmieder CC-BY-NC-3.0,
Mendeley DOI 10.17632/y2tz67f6ry.1, separately from first-party software licensing.
The analysis is retrospective, target-exposed and source-internal, conditional
on frozen fits and retained measured inputs. No production adoption or successor.
