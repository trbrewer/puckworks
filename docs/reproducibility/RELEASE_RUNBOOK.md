# Paper A / Paper B frozen-release runbook

## Purpose

The result bundles record `source_commit`. Recomputing a tracked bundle at commit
`H`, committing that bundle, and then running the current strict release command is
self-referential: the commit becomes `H+1`, while the bundle still records `H`.
No ordering of an ordinary in-tree recompute and commit can make a generated file
contain the hash of the commit that already contains that exact file.

`tools/prepare_paper_release.py` avoids the cycle. It treats the Git tag as the
immutable **source commit** and the attached archive as the immutable **generated
submission object**:

1. require a clean checkout and record `HEAD`;
2. create a detached worktree at that commit;
3. compute bundles, figures, source-data exports, and manifests into an external
   staging directory, so the source worktree remains clean;
4. run the existing strict verifiers against the staged bundles;
5. overlay the verified generated files onto `git archive HEAD`;
6. write deterministic `tar.gz` archives and SHA-256 sidecars.

This gives the required equality inside each release archive:

```text
source tag commit == manifest.source_commit == bundle.source_commit
```

It also preserves `git_dirty == false`, `bundle_matches_head == true`, and
`release_fresh == true` in the paper manifest because no generated file is written
inside the detached source worktree.

## Recorded environment

The direct numerical stack is frozen in:

- `docs/reproducibility/paper_release_environment.json`
- `requirements-paper-release.lock`

Required versions:

```text
Python      3.13.13
NumPy       2.5.1
SciPy       1.18.0
Matplotlib  3.11.0
```

Before the expensive builds, the release tool invokes:

```bash
python tools/check_release_environment.py
```

The command fails on any mismatch. The direct-version file is not a complete
transitive package lock. For archival-grade recreation, create the environment,
record `python -m pip freeze --all`, and save either that complete resolution or an
immutable container image digest with the release metadata.

## Prepare a candidate release

From the clean source commit intended for both tags:

```bash
python -m venv .venv-release
. .venv-release/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements-paper-release.lock
python -m pip install -e .
python tools/check_release_environment.py
```

Use an explicit timestamp so manifests can be regenerated intentionally:

```bash
python tools/prepare_paper_release.py \
  --paper all \
  --timestamp 2026-07-13T00:00:00Z \
  --output-dir dist
```

Expected outputs are two independent archives and sidecars:

```text
dist/puckworks-paper-a-<12-char-sha>.tar.gz
dist/puckworks-paper-a-<12-char-sha>.tar.gz.sha256
dist/puckworks-paper-b-<12-char-sha>.tar.gz
dist/puckworks-paper-b-<12-char-sha>.tar.gz.sha256
```

Paper A performs the slow full recompute, figure render, and source-data export.
Paper B performs the full recompute and figure render. Each archive contains a
paper-specific release provenance file under `docs/reproducibility/` with the
source commit, observed environment, and hashes of every staged generated file.

## Verify the candidate archives

```bash
sha256sum --check dist/puckworks-paper-a-*.tar.gz.sha256
sha256sum --check dist/puckworks-paper-b-*.tar.gz.sha256
```

Extract each archive in a temporary directory and inspect:

```text
docs/reproducibility/paper_a_manifest.json
docs/reproducibility/paper_a_release_provenance.json
docs/reproducibility/paper_b_manifest.json
docs/reproducibility/paper_b_release_provenance.json
```

For each paper, confirm:

```text
verified             true
release_fresh        true
git_dirty            false
bundle_matches_head  true
source_commit        <tag target SHA>
bundle_source_commit <tag target SHA>
```

Also confirm that each figure has `.png`, `.svg`, and `.pdf` forms and that all
source-data CSV exports expected by the paper are present.

## Tag only after scientific review of the candidate

The tool deliberately does not create tags or publish releases. After both candidate
archives have been inspected and the scientific claims approved:

```bash
git status --short                    # must be empty
git rev-parse HEAD                    # record full SHA
git tag -a paper-a-v1.0.0 -m "Paper A v1.0.0 frozen source"
git tag -a paper-b-v1.0.0 -m "Paper B v1.0.0 frozen source"
git push origin paper-a-v1.0.0 paper-b-v1.0.0
```

Attach the corresponding archive and `.sha256` file to each GitHub release. Deposit
those same bytes in Zenodo or the selected repository, record the assigned DOI in the
release notes, and do not rebuild the archive after DOI registration. A rebuild is a
new release candidate and must receive a new checksum; a scientific change should
receive a new semantic version tag.

## Failure interpretation

- **Environment mismatch:** recreate the exact locked interpreter/package stack;
  do not weaken the checker during a release cut.
- **Dirty source checkout:** commit or discard source changes before running.
- **Strict verification failure:** the bundle no longer supports a manuscript-facing
  claim within its declared tolerance; review the numerical result before tagging.
- **Detached worktree becomes dirty:** a build path wrote into source instead of the
  external staging directory. Treat this as a release-tool defect.
- **Archive checksum differs between identical runs:** inspect generated file metadata
  and nondeterministic numerical paths before proceeding.

## Scope not automated

Tag creation, GitHub release publication, Zenodo deposition, DOI registration,
author approval, and journal submission remain explicit human actions.
