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

## Rollback
<!-- How to revert if this regresses. -->
