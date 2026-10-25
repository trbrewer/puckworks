# Verification and handoff

SCI-MD-KHAMITOVA-TAMPING-CHEMISTRY-001; G1 / NO_GOVERNING_PHYSICS_CHANGE /
RESEARCH_ONLY / RETROSPECTIVE / TARGET_EXPOSED / SOURCE_INTERNAL / NONSCORING.
PHYSICAL_VALIDATION=NOT_ESTABLISHED.

## Repository state and scope

Actual base: `0547471e85c62f662a15c0df120f6a7d7a65b85c` (current Puckworks main,
PR #362 merged). Remote main was rechecked during implementation and still
matched; no intervening changes. Git grep at that base and remote PR search found
no landed implementation of this task. Work is isolated on
`research/sci-md-khamitova-tamping-chemistry-001`; unrelated user work is preserved.
The submitted head and live hosted statuses are recorded in the draft PR and
final handoff, avoiding a self-referential commit hash in this document.

EWP remote main remains `f44c33dbb9b4fb80143e360e6f4a90f8ac0aa516`. Its lock was
read at that exact remote revision and locally: the adopted Puckworks checkout
is `fc61c4670ec7bf801e40bb391aab16048b8da26b`, distinct from research main.
Lock SHA256 remains
`52b15ceef87d503a3e77c6e3c1cbed785185d2dde0b79647e5fbe309395d2f10`.
EWP's local status remains clean; no EWP writes, dependency adoption or solver run.

[Preserved-evidence receipt](preserved_evidence.json) compares every tracked byte
in the original Khamitova dataset, model and validation directories, historical
I-024, accepted Foster, Mo, Cameron, Corrochano bundles and Waszkiewicz data against
the base. All are unchanged. The five original CSVs are neither corrected nor
reformatted. No new component, gate, equation, schema, governance or visualization
registry infrastructure, calibration/validation edge, fit or cross-source score.
One branch and one draft PR; OPEN / DRAFT / UNMERGED, auto-merge disabled; no
production adoption or automatic successor.

## Source and output identities

The authenticated 189-page, 5,146,825-byte official PDF has SHA256
`59065ee31eb23c694c53dd1c7702c141d5c29bdd79413933e1b62e2fc70aa229`.
HTTP completeness checks, official DOI/date, labels, page mappings and rights
are in [source_metadata.json](source_metadata.json) and [SOURCE_NOTES](SOURCE_NOTES.md).
All 432 chemistry entries and eight ground entries agree with the unchanged
CSVs; the one related-unit source inconsistency is retained. No PDF/page images
are committed. Configuration inspection was limited to the registered Khamitova
subset; the five external CSV copies match the originals, not a new campaign.

[artifact_sha256.json](artifact_sha256.json) binds the plan, source/audit, methods,
review, software/tests and scientific outputs. The canonical results SHA256 is
`46992ed2326b8139173bd4717a7605aa5cbeadd35cf83226efb46de80b1c569e`.
`results.json` itself records all original CSV and audit-metadata SHA256 values.
Input identities and scientific files contain no run timestamps or environment
paths. Review/CI and software versions are kept here instead.

[One substantive independent-method review](REVIEW.md) passed. The separate
[check](independent_check.py) uses PyMuPDF positioned words instead of Poppler
layout text and direct-CSV exact arithmetic without importing the producer.
It rechecks 440 strings/144 keys and all 36 block calculations and attaining
pairs, with selected hand calculations in the review. This is a same-session
independent-method audit; no separate human reviewer is claimed. Synthetic tests
verify implementation and do not authenticate the source.

## Reproduction and checks

From a source checkout, ordinary reproduction needs only committed CSVs/audit
metadata. `--plot` uses the existing optional `figures` extra; omit it for standard
library-only numeric analysis. No PDF parser, PDF download or network is needed.

```bash
python -m puckworks.analysis.khamitova2020_tamping_chemistry \
  --output /tmp/khamitova-report --plot
python -m pytest -q tests/test_khamitova_tamping_chemistry.py \
  tests/test_available_data_register.py tests/test_espresso_data_guide.py \
  tests/test_local_corpus_family_index.py \
  tests/test_data_loaders.py::test_khamitova2020_tamping_intake \
  tests/insights/test_foundry.py tests/test_paper3_corpus.py \
  tests/test_paper_a_model_contract.py
python tools/build_available_data_register.py
python tools/build_local_corpus_family_index.py
python tools/build_espresso_data_guide.py
python -m puckworks.insights verify
```

Fresh processes reproduce JSON, three CSV views and PNG byte-for-byte in the
recorded environment. Cross-version Matplotlib image-byte identity is not claimed.
All 144 records, 36 endpoint requests and 36 complete four-level requests have
support; RSD and each rounding/normalization feature independently have full
support. Missing-mean, missing-precision, invalid/nonpositive denominator,
missing/negative/nonfinite/zero RSD, finite nominal/unbounded rounding, interior
excursion, extrema/ties, exact sign and outward-serialization fixtures pass.
The unequal-width [0,100]/50/50/50 fixture gives maximum range 50; the four
unit-scale RSD fixture gives lambda=0.5 and is invariant under units rescaling.
No JSON NaN/Infinity or finite unbounded sentinel is emitted.

Affected combined checks: **158 passed in 28.67 s** (37 task + 121 existing
checks). A subsequent test-only cleanup removed an inconsistent synthetic
precision subcase; the final task module still has **37 passed**. The final
submitted-head affected rerun is recorded below.

Loaded registry: **28 components, 66 PASS, one pre-existing ACKNOWLEDGED_EXCEPTION**.
An earlier empty-registry invocation is not counted. These baseline gate results
are reused with the unchanged model/validation tree proof. Configured Ruff scope
`puckworks/ tests/` plus `tools/` and this bundle's review scripts passes; mypy
passes its 19 configured modules. A broader `ruff check .` also visited unrelated
historical research scripts and found four existing unused imports; those files
are unchanged and this is not reported as a clean whole-tree lint pass.

Registry artifacts, Paper 3 build/availability/corpus, Paper A/B2/3 claim coverage,
lateral-coupling generated artifacts, evidence graph reconciliation/verification,
Insight verification, status truth and local corpus coverage (39 mapped/registered)
pass. Two Paper 3 archives are byte-identical and self-verification passes.
Existing producers regenerated the affected data register, family index, guide
and Insight snapshots. The broad Insight diff is principally provenance commit
refresh plus the Khamitova metadata; no ID registry change or new candidate work.
An initial metadata draft omitted analyte/temperature discovery words; it was
repaired and the unsubmitted regeneration discarded before regeneration with the
complete source description. No generator/schema infrastructure was changed.

One early affected run checked the guide before RESULT existed: **1 link failure,
70 passed**, then intentionally interrupted during an unnecessary historical
I-024 solver check. The completed guide passes fresh. I-024's unchanged evidence
is reused instead of completing that redundant solver exercise. The broad local
suite began during implementation and is not represented as an exact submitted-
head run; its final disposition and the fresh affected-head check follow below.
No assertion, selector, coverage floor or CI timeout was weakened.

Environment: Python 3.12.3, NumPy 2.5.4, SciPy 1.18.1, pytest 9.1.1,
Matplotlib 3.11.2; optional independent-source check PyMuPDF 2.0, Poppler tools
from the host. These optional tools are not core project dependencies.

## Submitted-head and hosted CI disposition

Pending submission at this document's preparation. The PR will remain draft and
unmerged with auto-merge disabled. Scientific qualification and software checks
above do not imply completed hosted CI. Final submitted/tested head, hosted pass/
pending/failure status and any infrastructure-only dispositions are recorded in
the final handoff and PR; this section is updated at submission. No protected
merge or production adoption is requested.
