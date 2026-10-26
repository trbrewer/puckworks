# Verification — SCI-MD-PERTICARINI-PRESSURE-CHEMISTRY-001

G1 / NO_GOVERNING_PHYSICS_CHANGE / RESEARCH_ONLY / RETROSPECTIVE /
TARGET_EXPOSED / SOURCE_INTERNAL / NONSCORING.
**PHYSICAL_VALIDATION=NOT_ESTABLISHED.**

## Intake and pre-result contract

Actual Puckworks base: `b3860d47ae6de6f6592add05cfac78fe9fb00487`, equal to
reviewed main, including merged #367. EWP live main:
`f44c33dbb9b4fb80143e360e6f4a90f8ac0aa516`; read-only. Its reviewed
`dependencies/puckworks.lock.json` still pins
`fc61c4670ec7bf801e40bb391aab16048b8da26b` (GitHub blob
`068a43a393b732eaff414c8d6e1d1a3159fe3f4b`). The local EWP working tree was clean
at intake and preservation check; no EWP file, checkout, pin or default changed.

Isolated branch `analysis/sci-md-perticarini-pressure-chemistry-001` preserves
unrelated work. Applicable root AGENTS/CLAUDE, onboarding, minimum-necessary
governance, espresso data/development guides, relevant cards/registers and the
accepted duration bundle were inspected. Open PRs #337/#336/#333/#321/#264/#257/
#129/#128 covered unrelated work; no overlapping Perticarini task was found.

PLAN.md was recorded at **2026-10-26T14:09:27Z**, before implementation results,
SHA-256 `2ed4517c78dbf4878da06e8288748366eae12fa22104efe3a79c7ec0fc83ab37`.
Prior source and preliminary-arithmetic exposure is declared. This is a
retrospective contract, not preregistration or protected pre-scoring evidence.

## Local verification and reproduction

Source access and chemical operator/formatting checks are recorded in
[SOURCE_NOTES](SOURCE_NOTES.md). Both external PDF hashes match the supplied
identities. Existing complete cell authentication is reused, not re-audited.

A task-local environment `/tmp/pressure-chemistry-venv` uses Python 3.12.3,
NumPy 2.5.4, SciPy 1.18.1, pytest 9.1.1 and Matplotlib 3.11.2. Installed the
repository's existing `[dev,figures]` extras; no dependency definition or lock
changed. Numerical production uses the standard library and committed tables;
the optional figure uses existing Matplotlib. Reproduction after installation
requires no network, PDF or external data mount:

```bash
python -m puckworks.analysis.perticarini2024_pressure_chemistry \
  --output /tmp/pressure-chemistry-reproduction \
  --tds-allowance-pp 0.05 --duration-allowance-s 0.5
# Standard-library numerical-only option: --no-figure
python -m pytest -q tests/test_perticarini2024_pressure_chemistry.py \
  tests/test_perticarini2024_pressure_grind.py
python -m pytest -q -m 'not slow and not live and not gpu and not external_data'
python -m ruff check puckworks/ tests/
python -m mypy
python -m puckworks.insights verify
python -m puckworks.paper3.corpus --verify
python -m puckworks.statusdoc --verify
git diff --check
```

- New + predecessor focused analysis checks: **25 passed**. Independent Decimal
  parsing verifies all 18 pressure differences in duration/TDS/EY and six direct
  four-value interactions. All 18 duration IDs, coefficient maps, nominal values,
  h=0.5 bounds, thresholds and conditional statuses agree with accepted artifacts.
- Tests cover 30 original IDs/publication deduplication, exact native support,
  14+6+4 coverage, 28 primary/30 union accounting, order-invariant full-key joins,
  retained SD zeros, exact coefficient cancellation, structural identity,
  printed ties, strict threshold equality and extremely close rational boundaries,
  separate component/joint statuses and empty strict regions, negative CLI inputs,
  and offline numerical production with socket creation disabled.
- Figure tests bind all 14 points to exact machine-readable nominal/bound values
  and intercept actual plotting calls: centers unchanged, horizontal/vertical
  half-widths exactly 1 s / 0.10 pp at the illustration. Chrome render visually
  inspected outside Git; one reviewer-noted callout/axis overlap was corrected
  by moving only the label. No source artwork or experimental error bars.
- All **seven generated outputs** (condition/primary/secondary/interaction CSV,
  JSON, RESULT and SVG) regenerate byte-for-byte into a separate temporary
  directory. Same-environment repeated figure generation also matches exactly;
  cross-Matplotlib-version SVG byte identity is not asserted.
- Full repository Ruff: **PASS**. Configured mypy: **PASS, 19 files**.
  Packaging: **15 passed**. Status documentation, corpus denominator,
  registry-artifact and Paper 3 build verification: **PASS**.
- Base registry gates: **66 PASS, 1 ACKNOWLEDGED_EXCEPTION**. No registered
  component/gate or physics changed; this evidence is reused.

## Generated discovery views and preservation

Only the two relevant manifest rows changed, and only `gate_use` / `caveat`:
**130 dataset IDs and all validation-strength fields remain unchanged**.
The narrow Cibao brew-ratio description correction was documented in SOURCE_NOTES
before editing. Card updates add this condition-level consumer; existing model
verdicts and historical EY/TDS bracket qualification remain unchanged.

Ran the existing available-data-register, local-corpus-family-index and
espresso-data-guide producers. The initial integration selection reported
**154 passed / 3 failed**, with all three failures caused by stale Insight
card/manifest fingerprints. This is generated-document QA drift, not numerical
failure. The existing Insight writer refreshed affected views; verification and
the affected 87-test analysis/discovery selection then **passed**. No generator
framework, new corpus census, scientific campaign or review stage was added.

The Insight relation list remains exactly **639 entries**, counts unchanged;
all **104 reserved candidate** and **187 reserved tension** fingerprint/ID
mappings remain identical. Active portfolio content is unchanged except source
commit metadata. Only two card entities and two dataset entities change beyond
that metadata; no new measured-pressure/flow/calibration edge is introduced.
The apparently large generated diff is mainly source-commit provenance refresh.

All **16** canonical/predecessor files (two canonical inputs, predecessor module
and complete predecessor bundle) compare byte-for-byte to actual base. The new
JSON records input SHA-256/Git blob IDs and reused predecessor hashes. No source
PDF/facsimile/render is staged. No production defaults, dependencies, pins,
accepted physical models or other analysis bundles changed.

## Review and hosted checks

One substantive independent nonhuman review is recorded in [REVIEW](REVIEW.md).
Source qualification, software correctness, conditional arithmetic and physical
validation are separate dispositions. No human review is invented.

Live GitHub Protect main ruleset **19053322**, read 2026-10-26, requires
`quick (3.10)`, `quick (3.12)`, `verify-generated`, `paper3-scope-strict`,
and `all-scope-strict`, with strict status-check policy. No CI policy or time
budget changed. Full local quick-suite completion and final submitted/tested
head, PR URL and hosted check states are recorded below / in the PR closeout;
pending checks are not a pass. The PR must remain OPEN / DRAFT / UNMERGED,
with auto-merge disabled.

Independent review completion: **PASS**, no material finding remains. Separate
reviewer runs: **25 analysis tests / 9 discovery tests passed**, independent
Decimal reduction and all-seven-output byte reproduction passed. The single
minor callout overlap was resolved and visually rechecked in the same review.
The verbatim receipt is REVIEW.md (SHA-256
`cf904764b59ceef8ca25c53a47db516b33bdc782e098a5b38602b905c24785a8`);
its file-hash table binds the scientific content. No further scientific edits
followed that receipt. Final completion text may be appended without changing
the reviewed computation or claim surface.

## Completed local gate and publication handoff

Full repository quick suite on the reviewed final scientific files:
**7,402 passed, 36 skipped, 74 deselected, 8 warnings in 1,526.20 s**
(25 min 26 s). Selector exactly matches the normal offline quick CI lane:
`not slow and not live and not gpu and not external_data`.
No failures, selector changes, timeout extensions or unrelated scientific reruns.
The eight warnings are from existing tests; the retained full log is external at
`/tmp/pressure-chemistry-quick.log`.

All 20 file hashes in REVIEW.md were checked after review and still match.
Completion records are the only subsequent additions. Final staged diff check
passed. The final commit is created from this tested tree; its exact submitted /
tested head and live hosted CI state are recorded in the draft PR description
and final task handoff, avoiding a self-referential commit hash here. Hosted
checks are a distinct disposition and are not implied by this local pass.
