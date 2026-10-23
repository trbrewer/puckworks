# Verification and offline reproduction

SCI-MD-HARGARTEN-SWELLING-KINETICS-001. G1 / SOURCE_INTERNAL / RETROSPECTIVE /
TARGET_EXPOSED / NONSCORING / RESEARCH_ONLY / NO_GOVERNING_PHYSICS_CHANGE.
PHYSICAL_VALIDATION=NOT_ESTABLISHED. Scientific conclusions, independent review,
software checks and hosted CI are separate.

Actual refreshed Puckworks main/base is
`35cc43ae82909b4936e0d15edcc31e541f0c1283`, including merged #355.
Remote EWP main is `f44c33dbb9b4fb80143e360e6f4a90f8ac0aa516`.
Both matched the supplied references; no unexpected remote advance at start.
The existing EWP working checkout was older (`78cbd59c751393cddfe539e4c69e43a224329bca`)
and left untouched. Its object database already contained the refreshed main;
`git show` inspected SCI-MD-002B and instructions at that exact commit. The result
is byte-identical between those EWP commits. No EWP fetch, checkout, write or
working-tree mutation was needed. Local EWP status remained clean.

The task uses a uniquely named branch from actual Puckworks main. PLAN was written
before formal numerical outputs. Source-reading corrections and clarified protocol
wording remained in the same bounded retrospective task; this is not prospective
preregistration or an untouched holdout. No model parameter, scientific threshold,
CI selector or accepted gate was changed to obtain a pass. Final tested head and
live hosted receipts are in the draft PR, avoiding a self-referential commit hash.
Leave OPEN / DRAFT / UNMERGED; auto-merge disabled.

## Scientific verification

One independent AI scientific/source review passed, after six edge-reading fixes
and correction of a relaxed-baseline witness that initially omitted its own lower
constraint. [REVIEW.md](REVIEW.md) and [review_receipt.json](review_receipt.json)
bind scope and scientific bytes. The review directly inspected the authenticated
article artwork, not only hashes or a source card.

[review_check.py](review_check.py) imports no producer. It independently derives
rational pixel mappings, all 17 individual baselines, both graph layers and exact
certificate products; checks 116 primary observations, eight fixed/outer witnesses,
22 conditional Figure7/10 frame comparisons and 34 requested-time summaries;
and calls the frozen production Mo kernel independently for all 17 particles.
It passed with network connections and source-PDF access denied. Six semantic
tamper trials failed as required even after refreshing the producer checksum file:
baseline, shared witness, outer disposition, Mo increment, Mo prediction and
figure-consistency gap. These are mathematical/software checks, not validation.

A separate offline producer replay with sockets disabled and fitz/pymupdf
unavailable regenerated **all 18 derived JSON/CSV/SVG files byte for byte**, including
both comparison plots. The original PDF is needed only for source auditing, not
reproduction from retained authenticated coordinates. The two plots were visually
inspected using native Matplotlib rendering. Full producer regeneration is also
covered by a focused slow test (two independent output directories, no network).

Mo checks retain the raw finite-grid initial-normalization defect and physical
volume-ceiling overshoot; they are not silently repaired. Positive-time radial
and integration-tolerance changes are reported for actual retained support.
Exact rational shared-clock certificates do not inherit floating-point solver
feasibility tolerances. The outer relaxation remains necessary-only.

## Local checks

- Focused new + wet-PSD/Mo predecessor + affected corpus/register tests:
  **74 passed**, 22.54 s, including the complete deterministic regeneration test.
- Repository Ruff plus the independent checker: PASS.
- Project mypy scope: PASS, 19 source files; the existing untyped-body note is not
  a type error. No broader type-check coverage is claimed.
- Registry gates: **66 PASS, 1 ACKNOWLEDGED_EXCEPTION** (pre-existing).
- Generated registry/build/availability/corpus, three manuscript claim audits,
  lateral-coupling verification, both strict evidence scopes, evidence-graph and
  status verification: PASS. Insight Foundry passed after card regeneration.
- Two scientific archive builds compared byte-identical; archive verification
  passed. No production model or EWP content differs from starting authority.
- Ordinary offline suite: initial run **55 failed, 7,064 passed, 32 skipped,
  72 deselected**, 1,499.55 s. Three generated-snapshot failures and 52 LP scheduler
  failures are preserved. **Corrected full run: 7,119 passed, 32 skipped, 73 deselected**,
  1,494.98 s. The extra deselection is the new >2-second deterministic regeneration
  test, run explicitly in the focused suite; the ordinary selector is unchanged.
- Integration regression after matching the new oracle LP to the repository's
  one-thread HiGHS setting: **222 passed**, 30.98 s.

The new manifest row increases retained dataset records from 124 to 125. Existing
owner tools regenerated the available-data register, local family projection,
data guide, corpus counts, claim-binding audit and Insight Foundry projections.
The empirical campaign count remains 46. Historical scalar data, wet-PSD intake
and predecessor results are preserved; no new independent campaign is claimed.

## Preserved failures and corrections

1. Web-reader refresh of the TUM PDF returned HTTP429. Existing authenticated local
   article bytes were available and matched the exact predecessor SHA256; no source
   substitution or claim of unavailable evidence followed.
2. Initial source intake incorrectly assigned some frame-edge identities/times and
   double represented one triangle. The independent review's six corrections are
   preserved in source_corrections.json, with explicit unsupported overlap records.
   Three separately visible clipped circles were recovered. These corrections were
   made before the first formal group outputs; no discrepancy allowance changed.
3. The first relaxed-baseline witness omitted each point's own lower bound when its
   time interval had positive width. The independent checker rejected it. Adding
   that lower constraint corrected the witness; the computed baselines and group
   brackets were unchanged. Outer witnesses are explicitly necessary-only.
4. Initial Ruff found one unused test import; removing it restored PASS.
5. One generated verification reported stale card fingerprints after warranted card
   edits. Running the existing Insight Foundry writer restored verification. The
   failed result is retained rather than relabelled PASS.
6. Initial focused tests reported 17 passed / 1 skipped because the independent checker
   and formal bundle did not yet exist. Final focused execution contains the actual
   checker and deterministic regeneration test: 74 passed across the named files.
7. EWP's local checkout was older than its remote main. Reading the already-present
   refreshed commit object confirmed the same SCI-MD-002B result; EWP was not changed.

8. The new baseline verification LP initially used HiGHS default threads, which
   initialized a process-wide scheduler inconsistent with existing one-thread LP
   solvers. This caused later ordinary-suite LP failures despite isolated passes.
   A five-case reproduction gave 1 passed / 4 failed with HiGHS status4. Matching
   `threads=1` in this test fixed the same-order regression: 222 passed. No producer
   algorithm, physical parameter, solver tolerance or CI selector changed. The
   entire ordinary suite was restarted in a fresh process after correction.

9. Git whitespace checking flagged Matplotlib-generated SVG line-end spaces.
   The producer now strips them deterministically. Independent XML token/geometry
   equivalence passed, numeric artifacts were unchanged, and the 18-file offline
   replay remains byte-identical. Review bindings were refreshed for formatting.

These are access, reading, implementation or verification incidents, not physical
hypothesis outcomes. No timeout, cancellation or incomplete hosted check is PASS.

## Commands

Use Python ≥3.10 with the existing repository dependencies. Local environment:
Python 3.12; NumPy/SciPy/Matplotlib/pytest exact versions and retained log SHA256s
are in verification_record.json. No new runtime dependency. Source extraction only
used PyMuPDF/Pillow; the offline producer/checker do not need them.

```sh
python -m pip install -e '.[dev,figures]'
python -m puckworks.analysis.hargarten2020_swelling_kinetics --output /tmp/hargarten-kinetics-replay --plot
python docs/analysis/sci_md_hargarten_swelling_kinetics_001/review_check.py --output /tmp/hargarten-kinetics-replay
python -m pytest -q tests/test_hargarten2020_swelling_kinetics.py tests/test_hargarten2020_wet_psd.py tests/test_mo_transfer.py tests/test_available_data_register.py tests/test_local_corpus_family_index.py tests/test_espresso_data_guide.py tests/test_paper3_corpus.py
python -m pytest -q -m 'not slow and not live and not gpu and not external_data'
python -m ruff check puckworks/ tests/ docs/analysis/sci_md_hargarten_swelling_kinetics_001/review_check.py
python -m mypy
python -c 'from puckworks.registry import run_all_gates; run_all_gates()'
```

Affected owner regeneration:

```sh
python tools/build_available_data_register.py
python tools/build_local_corpus_family_index.py
python tools/build_espresso_data_guide.py
python -m puckworks.paper3.corpus --splice
python tools/claim_binding_audit.py --write
python -m puckworks.insights write
```

The required protected hosted checks were refreshed using
`python -m puckworks.statusdoc --audit-ruleset`:
`quick (3.10)`, `quick (3.12)`, `verify-generated`, `paper3-scope-strict`,
`all-scope-strict`. Local PASS does not imply hosted PASS. Final exact-head check
conclusions and links are recorded in the PR description after observation.
