# Handoff and reproduction

The bounded source investigation is complete: eight originals and their relevant
internal references were inspected; one explicit external workbook reference is
unavailable. Three FIT dilution-entry conflicts were demonstrated, both source
calibration regressions reproduced, and one PRED preparation lacks an aliquot
quantity. Calibration/sample batch applicability, recovery/censoring controls,
standard purity/basis and material identities remain unassessed or unresolved.
Their contribution to predictor bias remains inseparable. The smallest missing
records are listed by explanation in [RESULTS.md](RESULTS.md).

GOVERNANCE_CLASS=G1 · NO_GOVERNING_PHYSICS_CHANGE · RESEARCH_ONLY · RETROSPECTIVE ·
TARGET_EXPOSED · SOURCE_INTERNAL · PHYSICAL_VALIDATION=NOT_ESTABLISHED ·
ANALYTICAL_UNCERTAINTY=NOT_ESTABLISHED.

## Reproduction

Use this branch with Python >=3.10 and repository development/reconstruction
extras (`pip install -e '.[dev,reconstruct]'`). No lock change is needed. Resolve
the originals through the existing `PUCKWORKS_EXTERNAL_DATA_ROOT` or
`$XDG_CONFIG_HOME/puckworks/data_sources.json` (default `~/.config`),
`sources.PANNUSCH2024_MENDELEY_FULL_REPOSITORY.path`. The root has exactly the
source_inputs.csv relative-path semantics; no alternative source substitution.
Private evidence is kept outside Git. Set `PW_PROVENANCE_PRIVATE` to a fresh
authorized external evidence directory, then:

```bash
python tools/five_cqa_observation_provenance.py intake \
  --output "$PW_PROVENANCE_PRIVATE/intake"
python tools/five_cqa_observation_provenance.py reduce \
  --intake "$PW_PROVENANCE_PRIVATE/intake/intake.json" \
  --output "$PW_PROVENANCE_PRIVATE/reduction"
python tools/five_cqa_observation_provenance.py project \
  --intake "$PW_PROVENANCE_PRIVATE/intake/intake.json" \
  --reduction "$PW_PROVENANCE_PRIVATE/reduction/reduction.json" \
  --output "$PW_PROVENANCE_PRIVATE/public"
pytest -q tests/test_five_cqa_observation_provenance.py
```

Intake enumerates all sheets/visibility, names and explicit workbook/chart/link
references and authenticates each source separately. Reduction reads only
source-linked records, reproduces the CGA chart regressions and compares original
preparation quantities. It does not execute MATLAB, evaluate arbitrary formulas,
refresh links, save source workbooks, load any predictor or invoke a historical
prepare/fit/predict/score/verify command. A missing/identity-failed original leaves
independent source results available in the private reduction, with explicit
failures. The public projection is an aggregate publication of this bounded
attempt, not a new source authority.

Retained execution label: `5cqa-observation-provenance-001-private`.
`intake-001` preceded the method audit; `intake-002` adds reproducible chart/link
metadata recording without a new scientific reduction. `reduction-001/002`
retain initial FIT layout parsing diagnostics and usable PRED/calibration results;
`reduction-003` is the complete final frame. Layout fixes excluded out-of-frame
sample identities and stopped requiring an unused nominal header; the actual
IST quantity headers remain required. All originals rehashed unchanged after
execution. `SOURCE_LOCATORS.md` retains exact cells, values and three conditional
source-value diagnostics. The public bindings identify these private artifacts;
actual private paths, individual observations and joins are not in Git.

Scientific output is deterministic given the exact admitted inputs. Private
absolute paths and the intake digest may differ across environments; compare
source hashes, aggregate scientific fields and identity-keyed records, not a
whole-file hash across different roots. The published source/reduction hashes
bind the actual retained execution. The historical authority, models, masks,
thresholds and decisions remain untouched.

## Verification and review

Method audit: **APPROVED** by an independent nonhuman reviewer before any new
reductions or joins, binding the protocol SHA in [METHOD_REVIEW.json](METHOD_REVIEW.json).
Two clarifications were resolved during that single audit: blank water entries
are not measured zero additions, and duplicate chart trendlines are one series.
Final scientific/code review: **APPROVED_FOR_BOUNDED_SCIENTIFIC_RESULT**, no
open material findings. The reviewer independently checked both regressions,
three source conflicts, the missing aliquot, C01 linkage and coverage. See
[INDEPENDENT_REVIEW.md](INDEPENDENT_REVIEW.md) and [FINAL_REVIEW.json](FINAL_REVIEW.json).
No human or hosted PR approval is implied by the independent agent review.

The focused synthetic tests cover hidden/nonnumeric sheets and references,
per-source admission/access/hash failures, wrong analyte/basis and factor-of-1000
errors, exact support boundaries, duplicate/unknown/unmatched keys, dilution
quantities, spill/valid-zero separation and analytical eligibility independent
of predictor mass-domain support. Initial test collection failed because the
standalone tools directory was not importable in isolated pytest; its explicit
file import was corrected, and the failed log is retained privately. This is
software QA, not a scientific result.

Required normal repository selectors/CI remain unchanged. No production behavior,
governing physics, dependency lock, EWP content/native run or PR #333 work changes.
The deliverable is one **draft PR**, unmerged, with auto-merge disabled. This
handoff authorizes no merge, source acquisition, laboratory work, author contact,
new model or correction campaign.

Pannusch/Schmieder source lineage, Mendeley DOI 10.17632/y2tz67f6ry.1 and
CC-BY-NC-3.0 treatment are retained for source-derived outputs; software licensing
is separate.

The final-review receipt binds the scientific files and private evidence. Later
changes to this handoff record QA/lifecycle only; the reviewed scientific files
and private reduction remain byte-identical.

## Completed local QA and publication boundary

| Check | Actual result |
|---|---|
| Unchanged normal offline selector | 6,794 passed; 66 skipped; 63 deselected; one existing development-salt warning; 1,323.48 s |
| New focused synthetic suite | 19 passed, also independently executed by reviewer |
| Scientific-baseline selector | 5 passed; 7 collection skips; 6,930 deselected; 213.82 s |
| Normal lint/registry/generated/status/README checks | All 15 commands passed; registry 66 PASS plus one ACKNOWLEDGED_EXCEPTION |
| Mypy | PASS, 19 core source files |
| Archive deterministic build and self-verification | Two builds, byte comparison and verification passed |
| Source/reuse and review preservation | Eight originals and ten accepted registers unchanged; nine reviewed non-handoff files and all private review bindings unchanged |
| Public boundary / whitespace | PASS; no raw source rows, detailed joins or actual private paths in public payload |

The normal suite was collected before the 19 task-local tests were added; its
existing code/tests are unchanged. The final task-local suite passed separately.
Hosted CI will exercise the combined set on the PR head. The initial focused
collection error and FIT parser diagnostics remain private with their resolutions;
they are not unresolved scientific failures. No QA selector or historical
contract was changed. The scientific-baseline collection skips and registry
acknowledged exception are not promoted to passes.

Hosted CI had not started at this commit. Its live outcomes and the actual draft
PR URL/lifecycle are reported in the final task handoff and PR checks, separately
from this scientific review. The repository reports no required branch-protection
contexts for main (API: branch not protected); normal PR workflows still run.

Private QA receipt: `verification-bindings.json`, SHA-256 `44a66ad2ae1ecdffb8e3e06f802b31a3c29868760df18b8188043eb00279f0cd`.
It binds the normal/focused/scientific-baseline logs, XML reports and other check
receipts. All are retained under the private execution label above.
