# Verification — SCI-MD-PERTICARINI-PRESSURE-GRIND-001

G1 / NO_GOVERNING_PHYSICS_CHANGE / RESEARCH_ONLY / RETROSPECTIVE /
TARGET_EXPOSED / SOURCE_INTERNAL / NONSCORING.
**PHYSICAL_VALIDATION=NOT_ESTABLISHED.**

## State and freeze receipt

Both live mains matched the reviewed heads on 2026-10-24:
Puckworks actual base `1398d38ff1986aa85150d55ad9f797bc1aaff1eb`, including merged
#359; EWP `f44c33dbb9b4fb80143e360e6f4a90f8ac0aa516`. There were no intervening
commits; GitHub search found no existing Perticarini analysis PR. The base checkout
was clean. A new isolated worktree/branch preserves unrelated work. EWP received
no writes or scientific runs. Final submitted/tested head is recorded in the PR
closeout (avoiding a self-referential hash).

The complete PLAN.md was frozen at **2026-10-24T21:16:39Z**, before the analysis
module or numerical/figure outputs were produced. File SHA-256:
`d576f613f92debc405063e5b501b0577702f3345fa31e9ffc08ed3b421339a47`.
This is a retrospective plan freeze after declared source/arithmetic exposure,
not preregistration or a protected pre-scoring freeze. No scoring/fitting occurs.

## Local evidence

- Direct source inspection: both official PDF hashes matched reviewed identities;
  all 18+12 thesis rows and the same 12 Egidi rows matched condition labels and
  all six numeric columns exactly as decimals. Full table renders/headers/units/
  captions and relevant methods were inspected. An independent scratch parser
  of PDF text confirmed the cell comparison. See SOURCE_NOTES.md.
- The new focused tests cover both schemas, complete unique support, four strata,
  exact key joins and row-order invariance, 14/19/4/2 contrasts, all 21 diagnostics,
  ordinal orientation, independent Decimal reduction directly from canonical CSVs,
  adverse Cibao interactions, all box vertices, critical/zero-touch boundaries,
  reversal boundaries, shared-cell cancellation and structural identities.
- Numerical/CSV/JSON/Markdown/SVG output comparison is byte-for-byte deterministic;
  new CSVs use LF. SVG values are bound to all 39 computed contrast IDs. Its full
  browser-rendered figure was visually checked outside Git. An initial ImageMagick
  renderer could not interpret the SVG; Chrome rendered the same valid SVG without
  altering it. This was rendering-tool infrastructure, not a numerical defect.
- Base registry gates: **66 PASS, 1 ACKNOWLEDGED_EXCEPTION**. The full offline
  quick suite and final focused checks are recorded below when complete. Local
  broad execution excludes slow/live/gpu/external_data as in current quick CI;
  it does not rerun unrelated scientific campaigns.

Supported local interpreter: `/tmp/pw-cameron-venv/bin/python` (existing environment,
no dependency edits). Reproduction itself uses only Python's standard library.

```bash
python -m puckworks.analysis.perticarini2024_pressure_grind --output /tmp/perticarini-pressure-grind
python -m pytest -q tests/test_perticarini2024_pressure_grind.py \
  tests/test_available_data_register.py tests/test_local_corpus_family_index.py \
  tests/test_espresso_data_guide.py tests/test_data_loaders.py \
  tests/test_paper3_corpus.py tests/insights/test_foundry.py
python -m pytest -v -m 'not slow and not live and not gpu and not external_data'
python -c 'from puckworks.registry import run_all_gates; run_all_gates()'
python -m ruff check puckworks/ tests/
python -m puckworks.paper3.corpus --verify
python -m puckworks.insights verify
git diff --check
```

## Discovery dependencies and bounded corrections

The available-data-register, local-corpus-family-index and espresso-data-guide
producers ran. Manifest dataset count stays **127**; identities and both canonical
input files are unchanged. Only the two relevant manifest records changed; all
other rows and source strengths remain. Producer dataset scopes preserve native
nominal machine pressure and unknown duration/endpoint semantics. No new physical
validation, measured-flow or calibration capability is added.

Corpus denominator verification passed without regeneration. The existing Insight
verification found actual stale card/manifest fingerprints, so its existing
producer also ran. No new corpus scan, corpus regeneration, claim-binding producer
or new visualization registry was needed.

Inspection also exposed **two pre-existing false measured-pressure edges** for
these nominal-label tables. A dataset-specific exception removes only those two
MEASURES edges and retains every other relation. This corrects the initial
working impression that the new consumer name alone caused them: both edges
already existed at the base. No flow-calibration edge is created. The correction
changes membership fingerprints of the two directly affected pressure discovery
families; historical I-032/I-084 and T-0047/T-0165 remain reserved in the append-only
registry, while corrected memberships get I-103/I-104 and T-0186/T-0187. The
remaining active candidate identities/memberships are unchanged; no candidate is
scored or executed and these generated metadata authorize no successor work.

Focused runs before regeneration exposed three stale-Insight checks; after
regeneration the historical seeded-ID survival check also identified those two
legitimate membership replacements. Its existing survival budget is preserved,
with explicit assertions for the old reserved IDs and corrected pressure-family
membership, rather than keeping false source semantics. These bounded software/
discovery corrections change no duration input, contrast, threshold or claim.

## Independent review and hosted checks

One substantive independent nonhuman review is recorded in REVIEW.md. Source
semantics, exact arithmetic/dependence, sensitivity/reversal, adverse outcomes and
the separate Cameron uncertainty layers are its scientific scope. Local tests,
independent review and hosted CI are distinct dispositions.

Current hosted protection is inspected from the live GitHub ruleset; observed
required contexts and exact-head results are recorded in the completion receipt
below and PR closeout. No pending or unobserved check is described as passing.
No .github policy, CI timeout, governing physics, production defaults, dependency
lock or unrelated scientific bundle changed. The PR remains OPEN / DRAFT /
UNMERGED with auto-merge disabled.

## Completed focused verification and independent review

- Focused material-risk and integration selection above: **144 passed in 8.88 s**.
  After the figure footer was changed to derive its reversal counts/thresholds
  from computed records, its complete 12-test analysis selection passed again
  (**12 passed in 0.63 s**); all numerical JSON/CSV and RESULT.md hashes remained
  unchanged. All seven generated files reproduced byte-for-byte offline.
- Full repository Ruff: PASS. `git diff --check`: PASS. Corpus denominator
  verification and Insight verification: PASS. The existing claim-binding
  staleness check also passed in the broad run; no claim-binding regeneration.
- Python 3.12.3; NumPy 2.5.4; SciPy 1.18.1; pytest 9.1.1. No dependency files changed.
- Independent reviewer `/root/independent_review`: **PASS, no material finding or
  correction requested**. Its separate source transcriptions and arithmetic checks
  confirm all 39 contrasts/21 diagnostics, source semantics and Cameron comparison.
  Its separate focused run passed **13 tests in 0.82 s**. REVIEW.md discloses the
  nonhuman independent-agent role and exact reviewed file SHA-256 values. Only
  completion receipts/status text may be appended after that receipt; unchanged
  science reuses that review without another review stage.
- Discovery preservation: relation multiset **635→633**, removing exactly the two
  false pressure edges (unique keys **580→578**); no other additions or changes
  apart from regeneration commit metadata. **88/90** active candidate memberships
  and **169/171** active tension memberships remain unchanged. All **102** prior
  candidate and **185** prior tension fingerprint→ID mappings remain reserved,
  with two additions in each registry bucket for the corrected memberships.
- Live GitHub **Protect main** ruleset **19053322**, read 2026-10-24, requires
  `quick (3.10)`, `quick (3.12)`, `verify-generated`, `paper3-scope-strict`, and
  `all-scope-strict`, with strict required-status-check policy. These are the
  observed current requirements, not an inherited historical pass count.

The broad local run began before edits and loaded the old family-index producer
at collection. It later found a cached-producer/generated-output mismatch after
the requested regeneration. A fresh final-file run of the affected family-index
and analysis checks passed **15/15 in 0.68 s**, agreeing with the earlier 144-test
selection. This mixed-worktree broad run is not claimed as standalone final-head
qualification; its eventual count and final-head hosted results are recorded in
the PR closeout. No unaffected campaign is replayed to resolve this cache-timing
issue. The final submitted head is tested separately by the focused selection
and required hosted checks, with actual observed status reported at closeout.
