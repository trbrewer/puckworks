# VAL-CASE-RHEOLOGY-DECISION-RESOLUTION-001 handoff

Completed bounded retained-aggregate evaluation: 32/32 historical labels reproduced,
zero discrepancies. Primary 24 PASS, 24 precision eligible, 24 envelopes entirely
below budget. Secondary six MATERIAL_MODELED_DELIVERY_CONTRAST and two UNRESOLVED,
six precision eligible/two ineligible, all eight envelopes entirely above threshold.
SW_UP/TR_UP fraction-TDS remain UNRESOLVED; their above-threshold sensitivity
relations do not satisfy the failed precision rule. [Scientific addendum](RESULTS.md).

G1 / NO_GOVERNING_PHYSICS_CHANGE / RESEARCH_ONLY / RETROSPECTIVE /
TARGET_EXPOSED / EXPLORATORY. This is aggregate arithmetic reproduction, not native
or independent 50-digit campaign re-verification, physical validation or production
adoption. No private corpus or external native archive is required.

## Identities and authority

- Puckworks base: `882584d110e1356091435ab8b002fb9abdd35ad6`.
- Isolated branch: `val-case/rheology-decision-resolution-001`.
- EWP read-only source: `4284e9460c8057053e95de7cfa2fb3590e68e9db`, tree
  `d9d9faaa56f22ab0bd7f47c43174024d15ada192`.
- Accepted policy/helper commit: Puckworks base above; accepted head
  `8cd54290f4a927b046f2da43447c1d864e95b2dd`, tree
  `7741920d87c813658941ebc26869c2af19807fad`.
- Policy SHA-256: `db16e68aa0e7fbdb37bfb455c39455928115af65c207fc43ec133424cd72a552`.
- Helper SHA-256: `d9c3d2a6e949e1f617e813dab12680dff58acdd1e4904178910739d4876e7d90`.

Owner acceptance, actual merge and post-merge verification of #335 are linked and
body-hash pinned in INPUT_MANIFEST.json. Its historical v1-proposed wording remains
unchanged. Reviewed main identities matched live main at intake; no reset or
unmerged #321/#333 changes. Task/purpose PR searches found no duplicate.
The final candidate head/tree and candidate-specific CI receipt belong in the
PR description, avoiding a self-referential committed hash. PR remains draft,
auto-merge disabled and unmerged; protected approval is distinct from agent review.

## Reproduction

From a checkout of this PR's exact candidate head, with Python 3.10–3.13 and the
repository's ordinary dev dependencies installed. Preparation of the two checkouts
may use network; the evaluation itself requires no network. Point EWP_READONLY at
an existing clean checkout of the exact source commit above. No setup, imports or
execution from EWP are needed. Use a new output pathname each time.

```bash
export EWP_READONLY=/path/to/espresso-whole-pull
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONPATH=.
git -C "$EWP_READONLY" rev-parse HEAD
git -C "$EWP_READONLY" status --porcelain
python -m pytest -q tests/test_rheology_decision_resolution.py
python -B -m puckworks.analysis.rheology_decision_resolution \
  --evidence-checkout "$EWP_READONLY" --output /tmp/rheology-decision-results.json
cmp /tmp/rheology-decision-results.json \
  docs/analysis/val_case_rheology_decision_resolution_001/RESULTS.json
git -C "$EWP_READONLY" diff --exit-code
git -C "$EWP_READONLY" status --porcelain
```

The CLI requires the exact EWP revision and all manifest file hashes, detects
missing/duplicate decisions, checks retained component construction and original
summation, and emits deterministic sorted JSON. It refuses an existing output
or an output within EWP. The only subprocess is read-only local `git rev-parse`,
with optional Git locks disabled. No source writes, legacy scoring imports,
network/native execution or original entry points occur. Puckworks' existing
package initialization still registers its built-in components, unchanged.

Ordinary QA commands (no CI selector, threshold, timeout or protection changes):

```bash
python -m ruff check puckworks/ tests/
python -m mypy
python -m mypy puckworks/analysis/rheology_decision_resolution.py
python -m pytest -q -m 'not slow and not live and not gpu and not external_data'
python -c 'from puckworks.registry import run_all_gates; run_all_gates()'
python -m puckworks.statusdoc --verify
python -m tools.readme_governance verify
python -m puckworks.paper3.registry_artifacts --verify
python -m puckworks.paper3.build verify
git diff --check
```

## Review and execution evidence

Independent boundary-fixture author: `/root/boundary_expectations`; hand-derived
expectations without retained-case evaluation or imports from the implementation.
Independent pre-analysis reviewer: `/root/pre_analysis_review`; PASS, no material
findings. PRE_ANALYSIS_REVIEW.md binds exact protocol, manifest and fixture hashes;
840 locators and all 32 identities checked before RESULTS.json existed.

Initial focused synthetic run: 63 passed. Initial focused mypy reported two
optional-value typing findings; explicit type annotations fixed them without
arithmetic changes, then mypy passed. The required three result dispositions were
added as metadata; all 32 case records and summary counts were verified unchanged.
No scientific input, rule or evidence changed after freeze. Maintained ruff,
19-module mypy, case-specific mypy, statusdoc, README governance, generated
artifacts and Paper 3 verification passed; registry gates report 66 PASS plus
one ACKNOWLEDGED_EXCEPTION. The full ordinary suite is reported separately.

The [final independent scientific review](FINAL_REVIEW.md) records the 32-row
source/result crosswalk and direct reviewed-file hashes. Ordinary QA totals and
hosted CI are recorded at delivery in the candidate-bound PR receipt. They are separate from the scientific results
above. No private/native input is missing for this bounded evaluation; unrepresented
uncertainty and physical claims remain limited as documented in RESULTS.md.

Expected change set is the one case-local module, focused synthetic tests/fixture,
this enduring bundle, and a narrow CURRENT discovery link. No historical source,
helper/policy, scorer, gate vocabulary, dependency, production/default or CI changes.
Rollback is removal/revert of this opt-in case bundle; no production activation.

`PHYSICAL_VALIDATION=NOT_ESTABLISHED`; `MERGE_AUTHORIZED=false`;
`PRODUCTION_ADOPTION_AUTHORIZED=false`; `NEW_NATIVE_SIMULATIONS=0`;
`NATIVE_EWP_RUNS=0`; `NO_AUTOMATIC_SUCCESSOR`.
