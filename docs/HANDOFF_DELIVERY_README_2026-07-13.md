# Delivery README — TB / PI / VENUE handoff

This delivery contains a unified patch and a repo-shaped copy of every proposed file. Start with `docs/HANDOFF_EXECUTION_SUMMARY_2026-07-13.md`.

## Apply the patch

From the `puckworks` repository root:

```bash
git switch -c handoff-tb-pi-venue-2026-07-13
git apply --check puckworks_handoff_2026-07-13.patch
git apply puckworks_handoff_2026-07-13.patch
```

The patch was based on public `main` at:

```text
b4de0d971555dcfcf13b24cab5da6e5b8eab9cf4
```

If `main` has moved, review normal context conflicts; the accompanying `repo_files/` directory provides exact proposed file contents.

## Review order

1. Read the execution summary and validation report.
2. Review `puckworks/figures.py` and `puckworks/figures_paper_a.py` plus their tests.
3. Review the Angeloni CSV and transcription audit before any inferential use.
4. Review the DOI/bibliography changes and retain the provisional novelty wording until PI-1 is archived.
5. Review the APS abstract and JFE package; do not treat the Paper A body as upload-ready.
6. Review the release runbook/tool, then run it only from the exact recorded environment on a clean committed tree.

## Focused checks

```bash
PYTHONPATH=. pytest -q \
  tests/test_figure_exports.py \
  tests/test_release_helpers.py \
  tests/test_uncertainty_intake.py \
  tests/test_submission_limits.py

python tools/validate_submission_limits.py
python tools/check_release_environment.py
```

The last command should fail unless the active interpreter and direct numerical stack exactly match the recorded release versions.

## Production release

After the full repository tests pass and the complete environment has been archived:

```bash
python tools/prepare_paper_release.py \
  --paper all \
  --timestamp 2026-07-13T00:00:00Z \
  --output-dir dist
```

Inspect the manifests, provenance JSON, figure/source-data files, tar contents, and SHA-256 sidecars before creating tags or depositing a DOI.
