# Validation report — TB / PI / VENUE handoff outputs

**Date:** 2026-07-13
**Baseline:** `b4de0d971555dcfcf13b24cab5da6e5b8eab9cf4`

## Automated checks

Executed from the modified source tree:

```bash
python -m py_compile \
  tools/check_release_environment.py \
  tools/prepare_paper_release.py \
  tools/validate_replicate_uncertainty.py \
  tools/validate_submission_limits.py \
  puckworks/figures.py \
  puckworks/figures_paper_a.py

PYTHONPATH=. pytest -q \
  tests/test_figure_exports.py \
  tests/test_release_helpers.py \
  tests/test_uncertainty_intake.py \
  tests/test_submission_limits.py
```

Result:

```text
10 passed
```

## Submission-limit validator

```json
{
  "ok": true,
  "counts": {
    "jfe": {
      "abstract_words": 237,
      "keywords": 7,
      "highlight_count": 5,
      "highlight_characters": [68, 72, 70, 73, 63]
    },
    "aps_dfd_2026": {
      "title_characters": 112,
      "abstract_body_characters": 1874,
      "funding_characters": 70,
      "body_plus_funding_characters": 1944
    }
  },
  "failures": []
}
```

## Release-environment gate

The negative gate test failed as intended because the runner did not match the recorded manifest stack:

```text
python: expected 3.13.13, observed 3.13.5
numpy: expected 2.5.1, observed 2.3.5
scipy: expected 1.18.0, observed 1.17.0
matplotlib: expected 3.11.0, observed 3.10.8
```

A production release was therefore not attempted in this runner.

## Synthetic release integration

A temporary Git repository with stub Paper A/Paper B compute, render, and strict-verify interfaces was used to exercise `tools/prepare_paper_release.py` end to end. It verified:

- clean checkout enforcement;
- detached worktree creation/removal;
- external bundle/figure/manifest staging;
- strict manifest assertions;
- source-archive overlay;
- deterministic tar creation;
- SHA-256 sidecar verification;
- expected generated files after archive extraction.

The first integration run found that imported Python modules could create `__pycache__` in the detached worktree. `PYTHONDONTWRITEBYTECODE=1` was added to the release subprocess environment, and the full synthetic run then passed for both papers.

## Data transcription validation

The Angeloni PDF was extracted with `pdftotext -layout`. A parser compared all fields in Tables 1–3 to the delivered CSV:

```text
66 condition mappings checked
66 total-solids mean/RSD pairs checked
66 total-lipid mean/RSD pairs checked
132 reconstructed SDs checked
0 mismatches
```

The source PDF SHA-256 recorded in the audit memo is:

```text
2600ef731c37d088838eaabb3d88e8b9ad09a7ff7b7d63d566b6a13329fc6ea7
```

## Patch validation

The final patch is checked with:

```bash
git diff --cached --check
git apply --check puckworks_handoff_2026-07-13.patch
```

A fresh application tree is then compared to the modified selected-source tree. Because the baseline was reconstructed from public raw files rather than a full clone, the check proves internal patch consistency for touched/new files, not compatibility with arbitrary future commits.

## Manual checks still required in the repository

- full repository test suite;
- exact-stack Paper A and Paper B recompute;
- visual inspection of every vector figure for clipping, font substitution, alpha/rasterization, and colour/greyscale legibility;
- manuscript cross-reference and bibliography audit;
- source-data/license review before public redistribution;
- release archive and DOI review by the repository owner.
