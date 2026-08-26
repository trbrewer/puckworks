# SCI-MD-007-R2-C1 producer qualification

Candidate preparation date: 2026-08-26.

- Focused behavioral suite: `68 passed`.
- Complete repository suite: `4370 passed, 60 skipped, 1 warning` in 2641.86 seconds.
- `ruff check puckworks/ tests/`: PASS.
- R2-touched Python formatting check: PASS, four files already formatted.
- Repository-wide formatting observation: the pre-existing branch contains 400 files that the current Ruff formatter would rewrite; R2 did not modify this unrelated baseline. GitHub CI does not define repository-wide format-check as a gate.
- Mypy: PASS, 19 source files.
- Paper 1, Paper 2, and Paper 3 claim coverage: PASS, zero unaccounted numerals.
- Paper 3 registry, build, availability, corpus, evidence graph, and archive-facing generated checks: PASS.
- Status truth and lateral-coupling generated checks: PASS.
- SCI-MD-007 deterministic double clean generation, source-package manifest, package-authority closure, and drift check: PASS.
- Cross-artifact primitive comparisons: 992/992 PASS.
- Source-package manifest: 22 inputs and 22 outputs, all member hashes PASS.
- Package-authority closure: no missing, unexpected, or wrong-hash members.
- Scientific evidence register hashes: byte-identical to R1.
- Real-data predictor execution: NONE.
- OpenFOAM execution: NONE.

Terminal GitHub check identities and exact P3 Git authority are recorded in the PR and final handoff after the candidate is committed and pushed.
