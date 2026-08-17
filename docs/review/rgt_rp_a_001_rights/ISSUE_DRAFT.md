# RGT-RP-A-001: use-specific rights review for the RP-A pilot trio

## Authorization and exact use profile

This issue governs `RGT-RP-A-001`, a use-specific rights and provenance review for:

- `cameron2020.extraction_bdf`
- `wadsworth2026.permeability`
- `foster2025.infiltration`

Downstream profile: `RP_A_001_LOCAL_DERIVED_OUTPUT_PROFILE_V1`.

The question is whether Puckworks may execute each exact current implementation locally in a private,
commit-pinned environment and publish bounded reduced response-atlas outputs: input identifiers and
values, generated responses, derivatives, elasticities, monotonicity and curvature classifications,
predeclared threshold/saturation and interaction metrics, numerical-refinement summaries, bounded
tables/plots, comparability records, citations, and unchanged evidence labels.

## Required separation and evidence standard

The review separately determines code, source data/transcribed numerical material, generated-output
redistribution, local execution, public batch execution, code inclusion in a release, and data inclusion
in a release. Controlling conclusions require primary official evidence. Public availability, a DOI,
open access, or silence is not permission. Article, supplement, code, and dataset terms do not propagate
without evidence.

## Boundaries

- Rights and provenance review only: no RP-A scientific execution, response curves, tuning, component
  substitution, or inspection of prospective RP-A results.
- No model, card, scientific data value, evidence label, component status/kind/range, registry science,
  RP-A implementation, Insight Foundry, EWP, or SCI-LC-001A change.
- Public artifacts exclude articles, screenshots, source figures or substitutes, full supplements, raw
  XCT, uncleared pressure traces/datasets, publisher PDFs, private correspondence or identifiers, copied
  unlicensed code, and extensive source-table reproduction.
- Private evidence stays outside Git in `RGT_RP_A_001_PRIVATE_EVIDENCE_BUNDLE`.
- No author, publisher, or institution will be contacted by this task.

## Ownership

Owned paths are limited to `docs/review/rgt_rp_a_001_rights/**`, the three named permission-summary
paths if evidence requires them, `puckworks/rights.py`, directly required rights tests,
`THIRD_PARTY_NOTICES.md`, and narrowly supported rights-only MANIFEST corrections. All scientific,
shared-status, product implementation, CI, release, RP-A analysis, Insight Foundry, and EWP paths are
forbidden except exact reader-facing rights corrections expressly authorized by the owner.

## Decisions, stops, and commits

Use only `CLEAR`, `PERMISSION_DOCUMENTED`, `INDEPENDENT_REIMPLEMENTATION`, `RIGHTS_REVIEW_REQUIRED`,
`RIGHTS_BLOCKED`, `NOT_REVIEWED`, and `NOT_APPLICABLE`. No state may be more permissive than its evidence,
and narrow findings must not over-clear unrelated uses. Stop for inaccessible or ambiguous controlling
evidence, unresolved provenance or permission, policy-representation insufficiency, collision, source
drift, any scientific change, or any need to execute RP-A.

The three principal commits prospectively freeze the protocol, record evidence-backed determinations,
then issue the deterministic RP-A resume gate. The pull request remains draft and unmerged. A separate
governed issue is required before it may be marked ready or merged.

Rights conclusions do not alter scientific evidence, credibility, validation, comparability, validity,
or model status. This is a repository-use recommendation, not general legal advice.
