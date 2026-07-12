# Paper A — reproducibility release checklist (handoff §3.3, M10)

**Decision: do NOT tag `paper-a-v1.0.0` now** (`tag_now: false`). Create a release
candidate only after the submission-blocking analyses and manuscript wording are
frozen; create the final tag at submission. Recheck repo state immediately before
release (main moves).

## Versioning (keep package + paper namespaces distinct — do not move/overwrite tags)
```text
v0.1.0                 # package/software version (exists)
paper-a-v1.0.0-rc.1    # manuscript reproducibility candidate
paper-a-v1.0.0         # submitted manuscript snapshot (annotated tag)
paper-a-v1.0.1         # correction / post-submission patch
```

## Release sequence
1. Work on a dedicated `paper-a` branch/PR.
2. Complete the numerical blockers (matched endpoint ✅, exact profiling ✅, uncertainty ✅, boundary flags ✅, TDS separation ✅, external Waszkiewicz TDS test, full-cup handling).
3. Freeze source data + derived outputs; add a one-command build + environment lock.
4. `git tag -a paper-a-v1.0.0-rc.1`; `gh release create --prerelease --generate-notes`.
5. Build from a clean clone **twice**; compare output hashes; fix provenance/build failures.
6. At submission: `git tag -a paper-a-v1.0.0`; GitHub Release; archive on Zenodo; record the **version DOI + tag + full SHA** in the manuscript.
7. Never cite moving `main` as the reproducibility snapshot.

## Release gate — do NOT create the final tag until ALL are true
- [ ] manuscript records the exact tag, full SHA, and archive DOI
- [ ] clean-clone build succeeds twice with identical machine-readable results (or documented deterministic tolerances)
- [ ] source + output hashes saved; package versions + environment recorded
- [ ] solver/grid convergence documented; profile-domain convergence documented
- [ ] bootstrap seeds/resamples saved; all boundary contacts reported
- [ ] every table and figure generated from machine-readable outputs; no manuscript number copied without a source key
- [ ] source licenses + provenance documented
- [ ] matched beverage endpoint used; TDS/TS separated; Waszkiewicz analysis frozen + labelled
- [ ] all tests pass; no stale narrative verdict embedded in analysis code

## Owed release files (create during the RC step, not now)
```text
CITATION.cff                 # ✅ scaffolded (package-level; paper tag added at release)
REPRODUCIBILITY.md
uv.lock (or equivalent pinned environment)
paper_a/{README.md,config/submission.yaml,manifest.json,run_metadata.json,checksums.sha256,results/,figures/,tables/,logs/}
puckworks/paper_a/build.py   # strict one-command build: python -m puckworks.paper_a.build --config ... --strict
```
The one-command build must: validate source hashes; run the analyses; save
machine-readable values; render figures/tables; verify manuscript-linked numbers;
record solver tolerances + parameter bounds; **fail** on unaccepted boundary flags
or missing provenance; emit a release manifest + checksums.

## Status
Deferred by decision. The figure pipeline (`python -m puckworks.figures_paper_a`)
and the slow-analysis modules already regenerate every number from code; the strict
`paper_a/build.py` wrapper + environment lock + hash manifest remain to be built at
the RC step.
