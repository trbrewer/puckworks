<!-- R5 PR template. Keep PRs narrow and reviewable. -->

## Problem & scope
<!-- What defect/need does this close? Keep the scope tight. -->

## Change
<!-- What you did, at a high level. -->

## Scientific claim / evidence impact
- [ ] No change to any scientific claim or evidence strength, **or** described below.
- [ ] **No evidence-strength upgrade** was made to "repair" an honest limitation (guardrail 2).

## Data / privacy impact
- [ ] No data/privacy path touched, **or** the impact is described and reviewed by a data owner.
- [ ] No private/non-redistributable corpus data added to the repo or any artifact.

## Tests & generated artifacts
- [ ] New/updated tests cover the change; the relevant lane is chosen (quick/slow/...).
- [ ] Generated artifacts regenerated (`paper3.registry_artifacts --write`, etc.) if affected.
- [ ] Quick CI passes on all supported Python versions (link the run).

## Docs / status
- [ ] `STATE_OF_TRUTH.md` / `CURRENT.md` updated if this changes project state.
- [ ] State claims use the vocabulary (implemented / CI-verified / validated / ...), no bare "DONE".

## Public surface (README governance, issue #41)
- [ ] README reviewed/updated where this PR changes a public **capability, model, dataset, paper/card,
      product, runnable environment, release, or project state** — or "not applicable" (internal-only)
      is explained below. `python tools/readme_governance.py verify` passes.
- [ ] Generated README/status artifacts regenerated (`tools/update_readme_pulse.py --write`,
      `python -m puckworks.statusdoc --write`) and evidence/rights language preserved.

## Activation / release completeness (learned from PR #65)
<!-- For an activation/release/state PR, confirm the intended file set actually landed. -->
- [ ] Expected-file checklist written; `git diff --name-only <base>...HEAD` matches it (no intended
      file — e.g. CHANGELOG/current.json — silently omitted from the commit).
- [ ] Regenerated files verified current and the tree is clean after generation.

## Rollback
<!-- How to revert if this regresses. -->
