# Prospective rights-review protocol

## Question and use profile

For each selected component, determine whether Puckworks may execute the exact current implementation
locally and publish bounded, reduced response-atlas outputs in its public repository under
`RP_A_001_LOCAL_DERIVED_OUTPUT_PROFILE_V1`.

The proposed outputs are input identifiers and bounded values, model-generated response values,
derivatives, elasticities, monotonicity and curvature classes, prospectively defined events, compact
interactions, numerical-refinement summaries, bounded tables/plots, comparability records, citations,
and unchanged evidence labels. Public hosted execution and a public API are not part of this profile.

Excluded from public output are articles, screenshots, source figures or substitutes, supplements, raw
XCT, uncleared pressure traces or datasets, publisher PDFs, private correspondence or identifiers,
copied unlicensed code, and extensive reproductions of source tables.

## Evidence and decision rules

Controlling evidence is, in order: exact licence text, official publisher/article/supplement pages,
official data or code repository licences at the relevant version, written rights-holder permission,
repository authorship history, and the actual artifact. Crossref and institutional or author records are
corroborating only. Search snippets, mirrors, social media, blogs, and AI summaries are discovery only.

Article, code, data, and generated-output rights are reviewed independently. Readability, a DOI, or
silence is not permission. No SPDX identifier is inferred. Each load-bearing source is hashed and dated.

Only the repository states `CLEAR`, `PERMISSION_DOCUMENTED`, `INDEPENDENT_REIMPLEMENTATION`,
`RIGHTS_REVIEW_REQUIRED`, `RIGHTS_BLOCKED`, `NOT_REVIEWED`, and `NOT_APPLICABLE` may be used. A completed
but unresolved field becomes `RIGHTS_REVIEW_REQUIRED`; affirmative states require primary evidence.

`INDEPENDENT_REIMPLEMENTATION` requires first-party history, no identified direct copying, derivation
from lawfully usable equations/descriptions/factual inputs, independent software structure, and no
unlicensed upstream code. It never clears copied data or fixtures.

The global `RightsRecord` must not over-clear a narrow input or output profile. If a bounded affirmative
finding cannot be represented faithfully, the global field remains `RIGHTS_REVIEW_REQUIRED`, the RP-A
gate remains closed, and the disposition is `RGT_RP_A_001_POLICY_REPRESENTATION_INSUFFICIENT`.

## Component review

For every component, inspect its card, implementation, registry record, gates, tests, product callers,
data dependencies, full introducing history and blame, upstream code candidates, official article,
supplement, data/code repositories, embedded constants/tables, and generated-output chain. Foster paths
are separated into synthetic pressure, cleared source pressure, private recorded pressure, and
Cameron-derived permeability. Wadsworth raw XCT is outside the RP-A profile. Cameron source tables may
be consumed only as specifically determined and are not republished.

## Gate and dispositions

The RP-A resume gate requires all three components to have affirmative support for local execution and
publication of the exact derived outputs from identified permitted inputs, implementable attribution,
no private/unredistributable committed data, no unresolved dependency, and faithful policy
representation. No substitution or two-component downgrade is permitted.

Permitted dispositions are the exact `RGT_RP_A_001_*` taxonomy in the owner authorization. The review
stops for duplicate ownership, collision, baseline failure, inaccessible/ambiguous controlling evidence,
unresolved provenance or permission, policy-representation insufficiency, scientific changes, source
drift, or any need to execute RP-A. Partial and negative determinations are valid.

## Private evidence and change control

Working evidence lives in a new immutable attempt outside every worktree. Public records contain only
source metadata, hashes, bounded permission summaries, and determinations. No correspondence is searched
unless an owner-maintained location is explicitly identified. No author or publisher is contacted.

Commit A freezes this protocol and contains no affirmative determination. Commit B records evidence and
supported rights/notices changes. Commit C reconciles use gates and the RP-A resume decision. Commit A
will not be rewritten after adjudication starts. Every source hash is rechecked before adjudication and
push. The draft PR remains unmerged and not ready.
