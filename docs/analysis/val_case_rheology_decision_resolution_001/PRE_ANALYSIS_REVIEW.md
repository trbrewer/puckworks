# Independent pre-analysis review

**Disposition: PASS for the frozen mapping and synthetic expectations.**
No material finding remains in this review scope. Review completed on
2026-10-15 at 15:08 UTC, before `RESULTS.json` existed and before this reviewer
executed any retained-case decision or allowance arithmetic.

Reviewer: separate nonhuman Codex agent `pre_analysis_review`, assigned only
review of the prospective mapping, source manifest and independently specified
fixtures. The reviewer did not author the implementation, protocol, manifest or
fixtures. This is independent nonhuman review, not owner acceptance, protected
GitHub approval or human scientific peer review.

## Frozen materials

Direct SHA-256 identities checked from file bytes:

| Material | SHA-256 |
|---|---|
| [PROTOCOL.md](PROTOCOL.md) | `12bc2a1352e97926fab9300496491ce92c2eb50c71a8cc4afc2d99704ed254a3` |
| [INPUT_MANIFEST.json](INPUT_MANIFEST.json) | `6284263ca767eb08c9bc24b22894f113543c365bb4e1e7b2e15a443322c32750` |
| [Synthetic fixtures](../../../tests/fixtures/rheology_decision_resolution_boundaries.json) | `2ec4c1adefd1b5e5793b4184d583483d4cdc037ee523e4e11234afb1dfbad014` |

Puckworks base: `882584d110e1356091435ab8b002fb9abdd35ad6`.
EWP source: `4284e9460c8057053e95de7cfa2fb3590e68e9db`.
All 25 manifest-listed EWP files and all five policy/governance files matched
their manifest hashes. The accepted PR #335 head
`8cd54290f4a927b046f2da43447c1d864e95b2dd` has byte-identical policy/helper
files to the pinned Puckworks base. Their direct identities are:

- Policy: `db16e68aa0e7fbdb37bfb455c39455928115af65c207fc43ec133424cd72a552`.
- Helper: `d9c3d2a6e949e1f617e813dab12680dff58acdd1e4904178910739d4876e7d90`.

The protocol preserves the historical `v1-proposed` text and identifies later
owner acceptance, actual merge and the final receipt as authority for this
separately authorized application. This review does not rewrite those records
or repeat PR #335 infrastructure qualification.

## Review evidence

Read the controlling policy/helper, SCI-GOV-001, Validation Operating Standard,
the relevant October 9 review sections, historical 010 protocol and static
analysis source, the inherited observer decision functions, and separate 007/011
result context. Source modules were read as text only, never imported or run.
Public metadata and aggregate receipts were available; no restricted source
property tables, native traces, external archive or physical measurements were
inspected or newly verified.

The following checks passed:

1. **Population and source crosswalk.** Independently constructed the required
   Cartesian population from the two laws, two histories and six primary/two
   secondary metrics: exactly 24 primary and eight secondary identities, all
   unique, no missing or extra identity. Checked all 840 declared source
   locators resolve. Unit labels and required variant families match their
   source fields. Coverage locator sets independently match the exact primary
   C/E2 and secondary new-C/old-C constructions. These were structural checks,
   not numerical classification of the retained rows.
2. **Historical mapping.** `010/common.py::decision` delegates to
   `008/observer.py::qualify_metric`, which delegates to
   `007/observer.py::decide`. The frozen primary adapter preserves strict
   `M+u<b` satisfaction and strict `M-u>b` failure; both equalities remain
   unresolved. Secondary label remapping preserves the same two strict
   boundaries. Complete valid compatible evidence and inclusive `u<=0.20*b`
   remain mandatory. `010/common.py::overall` gives any qualified FAIL
   precedence, requires all 24 PASS for sufficiency and retains unresolved
   siblings. Separate secondary accounting is correct.
3. **Representation and sum convention.** The historical README specifies
   Python 3.12.3. The observer constructs terms in time, axial, Cradial,
   property, arithmetic order and calls built-in `sum`; 010 renames the
   secondary radial key only afterward. The frozen specification correctly
   requires this original order and CPython 3.12 compensated float summation,
   rather than sorted JSON order, naive summation on an older interpreter,
   decimal reinterpretation, RSS or a new tolerance. The referenced
   [CPython 3.12.3 implementation](https://github.com/python/cpython/blob/v3.12.3/Python/bltinmodule.c#L2444)
   confirms the compensation convention. Exact reconciliation must still be
   demonstrated by the eventual implementation and final retained-data review.
4. **Synthetic expectations.** Reviewed all 16 boundary/precision fixtures,
   16 invalid-input fixtures and six aggregate fixtures independently by the
   written inequalities, without calling an implementation under test. With
   `b=10,u=2`, `M=7` gives `[5,9]`, `M=13` gives `[11,15]`, `M=8` or `12`
   touches the relevant boundary and `M=10` overlaps. All expected labels are
   correct. The supplied hexadecimal float immediately above 2 fails the
   inclusive precision ceiling even where the envelope remains entirely above
   or below. Invalid evidence, units, terms and shortened support cannot give
   supported success. Failure precedence, missing decisions and unresolved
   siblings are explicitly represented. Structural expectations cover exact
   membership, no source writes/imports/native calls and deterministic output;
   their executable verification remains an implementation responsibility.
5. **Helper separation.** The generic strict comparator may label equality a
   mathematical violation; the local historical adapter must still return
   UNRESOLVED. A `sensitivity` evidence/basis pair with an explicitly separate
   bound-based diagnostic can report informative interval relations while its
   bound resolution remains UNRESOLVED and contractual bound assessment
   UNAVAILABLE. The planned outputs do not promote empirical sensitivity to a
   certified bound or replace the historical decisions.
6. **Construction and support.** Primary radial refinement holds E2 fixed and
   changes C; secondary changes both C configurations. Original arithmetic
   discrepancies span every required variant, and TR property contribution
   remains zero. Full-time hydraulic/allocation support remains distinct from
   the fixed delivery supports. The support declaration uses all 18 C
   terminals per history, retains UP `0.015983191` kg and DOWN `0.016114389` kg,
   all 50 coverage rows and unscored terminal tails. Missing delivery support
   cannot be repaired by cropping and does not alone invalidate hydraulics.
7. **Scientific ceilings.** The protocol explicitly discloses target exposure
   and the known unresolved outcomes; expected counts are verification
   expectations, not tuning targets. It separates approximation from secondary
   modeled contrast, C from measured truth and two radial cells per axial
   station from two lumped states. It preserves 007's failure/unresolved
   context and 011's separate distribution-preserving null without a new E2
   run. Weighted permeability/residence-time changes prevent unique lateral
   mechanism attribution. Engineering thresholds, finite support and unknown
   uncertainty components are appropriately limited.

## Remaining execution responsibilities

This PASS permits the bounded retained-results evaluation under the hashed
specification; it is not a favorable scientific result. The final independent
review must check actual source/result values, arithmetic, decisions, helper
outputs, support and reader-facing claims, after the implementation and focused
tests exist. Any material source mismatch must remain visible rather than be
adjusted to match expected counts. The final bundle should explicitly report
`SCIENTIFIC_RESULT_DISPOSITION`, `VALIDATION_FRAMEWORK_DISPOSITION` and
`CLAIM_CEILING` separately as required by the operating standard.

EWP had no tracked or untracked changes at the review check. This reviewer wrote
only this review file. No original scoring/preparation/report entry point or
native execution was invoked; no real 32-row numerical evaluation was performed
by this reviewer during pre-analysis review.
