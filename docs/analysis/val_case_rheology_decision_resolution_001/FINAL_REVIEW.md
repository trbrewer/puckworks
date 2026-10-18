# Independent final scientific and implementation review

**Disposition: PASS. No material finding remains in the reviewed scope.**
Completed 2026-10-15, 15:21 UTC, by separate nonhuman Codex agent
`/root/final_scientific_review`. This reviewer did not author the implementation,
specification, manifest, synthetic expectations or scientific results. This is
agent review, not human scientific peer review, protected GitHub approval,
owner acceptance, merge permission or production authorization.

The review binds the direct file identities below. Puckworks base is
`882584d110e1356091435ab8b002fb9abdd35ad6`; the final candidate commit/tree and
hosted CI are recorded separately in the candidate-bound PR receipt. At this
review's completion the candidate commit and hosted CI had not yet completed;
this review makes no claim that ordinary full-suite QA or hosted CI passed.

## Materials and exact identities

| Reviewed file | SHA-256 |
|---|---|
| [Case implementation](../../../puckworks/analysis/rheology_decision_resolution.py) | `5e31f28cc4fed539e42cfe96b5566e1a4b2dba14adc115e76f5312b274dcd224` |
| [Focused tests](../../../tests/test_rheology_decision_resolution.py) | `2aed44ee343e89e54052d33a88eed4e00ed5611fe5ce390401d0cf38b9fd14cd` |
| [Independent synthetic fixtures](../../../tests/fixtures/rheology_decision_resolution_boundaries.json) | `2ec4c1adefd1b5e5793b4184d583483d4cdc037ee523e4e11234afb1dfbad014` |
| [PROTOCOL.md](PROTOCOL.md) | `12bc2a1352e97926fab9300496491ce92c2eb50c71a8cc4afc2d99704ed254a3` |
| [INPUT_MANIFEST.json](INPUT_MANIFEST.json) | `6284263ca767eb08c9bc24b22894f113543c365bb4e1e7b2e15a443322c32750` |
| [PRE_ANALYSIS_REVIEW.md](PRE_ANALYSIS_REVIEW.md) | `8a991dc2a0de9129dff56e5c8572c216573b4cdf01b2ca99b4101e6f719710ec` |
| [RESULTS.json](RESULTS.json) | `665cc4f0d905726a6e3ff55d60d20a3de82dde25aa73933ffa455a0907e4ccc1` |
| [RESULTS.md](RESULTS.md) | `456acb30e83f8cad0354251c17b9ea1ae320b3a303b188f1fb4890c2c9d07e0e` |
| [HANDOFF.md](HANDOFF.md) | `61728096eddf194b6273f72023ab0f131994dfc5001dbb1cc8c20a7517e74f45` |
| [CURRENT discovery link](../../CURRENT.md) | `e521347a9e9ce60c3d65c4a217378fc94aa17d06f3451163f282a44b49cb4d95` |

EWP read-only source was verified at
`4284e9460c8057053e95de7cfa2fb3590e68e9db`. Every one of the manifest's
25 EWP file hashes and five Puckworks policy/governance file hashes matched.
The accepted policy/helper remain byte-identical to their pinned source:

- Policy: `db16e68aa0e7fbdb37bfb455c39455928115af65c207fc43ec133424cd72a552`.
- Helper: `d9c3d2a6e949e1f617e813dab12680dff58acdd1e4904178910739d4876e7d90`.

The accepted policy head/tree are
`8cd54290f4a927b046f2da43447c1d864e95b2dd` /
`7741920d87c813658941ebc26869c2af19807fad`. The manifest and protocol preserve
the historical v1-proposed wording and cite later owner acceptance, actual
merge and post-merge verification as the authority. PR #335 infrastructure
qualification was not repeated.

## Independent source/result cross-check

The reviewer read historical analysis and observer modules as text, without
importing or executing EWP modules. A separate standard-library-only Python
3.12.3 check loaded the retained JSON directly, constructed the required
Cartesian population independently, and compared it with the result bundle.
It did not import the case adapter or use its outputs as expected arithmetic.
The original CPython 3.12.3 built-in `sum` supplied the historical compensated
summation independently of the adapter's explicit compatibility implementation.

All checks passed exactly, with no tolerance, rounding, padding or RSS:

1. Exactly 24 primary and eight secondary identities, each once; sorted result
   order; no missing, extra, duplicate or undisclosed adverse row. All 840
   declared source locators resolve to the corresponding retained values.
2. All 32 retained magnitudes equal their base variants. All 160 allowance
   components reproduce from the 144 required variant/arithmetic pairs:
   absolute temporal, axial, radial and SW property changes from base; zero
   TR property term; maximum retained independent arithmetic discrepancy.
   Ordered built-in `sum` exactly equals every retained and reported total.
3. All units, budgets, original evidence-completeness fields, original labels
   and reproduced labels agree. Every L, U, precision ceiling, precision
   headroom and both directional budget headrooms agrees at binary64 precision.
   Historical equality stays unresolved; eligibility uses inclusive
   `u <= 0.20*b`. The historical source gives a valid primary FAIL precedence
   over unresolved siblings and requires all 24 PASS for aggregate sufficiency.
4. Source pairing confirms primary radial refinement changes C while E2 stays
   at base; secondary refinement changes both C configurations. Secondary
   renames Cradial after the original sum. Neither JSON key sorting nor the
   new term label changes the arithmetic order or provenance.
5. All 50 coverage records are retained unchanged apart from explicitly
   derived tail fields. All traces reach support; all coverage ratios and
   terminal tails reproduce. All 36 C terminal masses match support and
   coverage. The original Decimal floor calculation from 18 terminals per
   history gives UP `0.015983191` kg and DOWN `0.016114389` kg exactly; the
   support receipt matches. Per-row coverage sets match the relevant C/E2 or
   OLD-C/NEW-C constructions. No support shortening or tail deletion occurs.
6. All helper records use sensitivity evidence and basis; their directed
   range relation is `satisfies`, but bound resolution remains `UNRESOLVED`
   and bound-based contractual assessment `UNAVAILABLE` for all 32 rows.
   Unknown uncertainty components remain explicit. The helper never replaces
   a historical label or certifies an empirical envelope.

| Question | Original and reproduced | Precision eligible / ineligible | Envelope below / above / overlap |
|---|---|---|---|
| Primary, 24 | 24 PASS; zero FAIL/UNRESOLVED | 24 / 0 | 24 / 0 / 0 |
| Secondary, 8 | Six MATERIAL_MODELED_DELIVERY_CONTRAST; two UNRESOLVED | 6 / 2 | 0 / 8 / 0 |

Original-label, component, total, unit, budget, support and aggregate
discrepancies: **zero**. The primary aggregate remains
`E2_CONDUCTANCE_MATCHED_REVERSAL_SUFFICIENT_FOR_TESTED_OUTPUTS`.

For SW_UP fraction-TDS, `[L,U]` is
`[4.709125247311057, 4.749202516699462]` pp, precision headroom is
`-3.863469420252452e-05` pp, and above-budget headroom is
`4.6091252473110575` pp. For TR_UP fraction-TDS, `[L,U]` is
`[4.142920962062328, 4.192195935234582]` pp, precision headroom is
`-0.004637486586127185` pp, and above-budget headroom is
`4.042920962062328` pp. Each original decision correctly remains UNRESOLVED
through failed precision eligibility, while its retained sensitivity envelope
lies entirely above the original 0.10 pp materiality threshold.

## Implementation, tests and scientific claims

The 400-line opt-in case implementation is focused on this frozen population.
No helper, scorer, public vocabulary, threshold, dependency, default execution
or production path changes. Its only subprocess is local read-only Git revision
lookup; source loading authenticates pinned files and never imports EWP. The
CLI rejects output inside EWP and existing output files. Missing decisions are
retained; component, unit, support and evidence defects cannot become a
successful interpretation. The synthetic tests exercise the actual adapter
as well as the independently specified strict-boundary expectations, immediate
precision-ceiling successor, overlap, failure precedence, missing/duplicate
accounting, provenance distinctions and serialization.

Reviewer-run focused tests: **63 passed in 0.45 s**, using Python 3.12.3 and
the ordinary Puckworks development environment, with one BLAS thread. The
reviewer also ran the new read-only CLI to a fresh external temporary path;
`cmp` against committed RESULTS.json passed byte-for-byte. Bare `python` was
initially unavailable in this shell; selecting the existing development
interpreter resolved that environment-only command failure. No test failed.

The readable matrices and scientific conclusions agree with the checked JSON.
RHEOLOGY-007 retains 22 PASS, the genuine TR/9-bar fraction-TDS FAIL and
SW/9-bar UNRESOLVED, alongside useful hydraulic/allocation/path results. Its
non-exchanging P construction remains distinct from E2's two radial cells at
each axial station. RHEOLOGY-011 retains its eight below-budget arrangement
contrasts and `NO_MATERIAL_ARRANGEMENT_CONTRAST_FOR_TESTED_DELIVERY`; full
conditional E2 was not triggered. These are historical context, not new scores.

The report correctly separates E2 approximation from secondary modeled
contrast, C from experimental truth, and matched conductance from unique
lateral-position attribution. The 010 reversal changes the area-weighted
permeability distribution and associated residence-time behavior; 011 supplies
a separate distribution-preserving null. Finite support, deliberately unscored
tails, source-conditioned property assumptions, engineering threshold status
and unknown measurement/training/source-model/parameter/continuum uncertainty
are explicit. No physical-validation, certified-bound, whole-shot, arbitrary
transfer, taste-tolerance or production-adoption claim is supported or made.

## Review limits and delivery status

This verifies retained aggregate arithmetic and decisions, not original native
computation, the 50-digit campaign, external archives or physical measurements.
Restricted property tables were not accessed. The data guide and source-use
receipts were inspected as metadata/context; public retained aggregate JSON
was inspected directly. The pre-analysis review's exact protocol, manifest and
fixture identities still match. Its chronology is recorded in that independent
review; this final review does not claim to recreate the earlier session.

EWP had no tracked or untracked changes both before and after review execution.
Historical Puckworks policy/helper files remained unchanged. This reviewer
authored only this review file in the repository; separate ordinary QA and
hosted CI must be reported by their actual candidate-bound receipts. No input
is missing for this bounded aggregate evaluation. Unrepresented uncertainty
and the two failed historical precision requirements remain unresolved as
scientifically documented; there is no material review blocker.

`PHYSICAL_VALIDATION=NOT_ESTABLISHED`; `MERGE_AUTHORIZED=false`;
`PRODUCTION_ADOPTION_AUTHORIZED=false`; `NEW_NATIVE_SIMULATIONS=0`;
`NATIVE_EWP_RUNS=0`; `NO_AUTOMATIC_SUCCESSOR`.
