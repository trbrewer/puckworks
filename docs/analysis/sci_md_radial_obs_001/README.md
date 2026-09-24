# Reproduce the Pocket Science assay

Use Python 3.10+ and `pip install -e '.[reconstruct]' pytest`. CI uses a generated
synthetic XLSX, never private source files. The main public interfaces have no
openpyxl dependency until the explicit workbook reader is called.

```bash
python -m pytest -q tests/test_pocketscience2024_assay.py
python tools/reconstruct_pocketscience2024_assay.py --output "$PRIVATE_OUTPUT/replay.json"
```

The reader resolves the existing configured `inventory.root` or
`PUCKWORKS_EXTERNAL_DATA_ROOT`; `--root` takes precedence. It verifies all frozen
source hashes, code and the independent audit before the full replay. Per-cell
primitives, formulas, caches, display formats, dependencies, exclusions and new
condition means stay in the external output. It will not write them inside this
checkout. Preserve the configured private inventory manifest and source exports;
they are lineage evidence, not an alternate formula engine.

[MEASUREMENT_MAP.md](MEASUREMENT_MAP.md) supplies the explicit equations,
identifiability decisions, source anomalies and publication limits.
[CONTRACT.json](CONTRACT.json) is the same logical cross-repository freeze as the
EWP copy; [AUDIT.json](AUDIT.json) is genuine independent agent review, not human
approval. [RESULT.json](RESULT.json) contains bounded public replay dispositions.
The task-local EWP consumer binds the assay code SHA and separately records its
analysis commit. No production lock update is authorized.

Linked retained-field diagnostic: [EWP PR #172](https://github.com/trbrewer/espresso-whole-pull/pull/172).
