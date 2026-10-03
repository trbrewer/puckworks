# Puckworks publishing tooling

This directory supports reader-first science-of-espresso articles with a closed internal evidence package. [`PUBLISHING_SYSTEM.md`](PUBLISHING_SYSTEM.md) is authoritative. Nothing here publishes to Substack, Medium, or a community platform.

## Operator flow

1. Close the internal trigger, source-artifact, evidence-ledger, and claim package.
2. Draft a reader-first public narrative from that package.
3. Run the evidence, draft, schedule, and mechanical style checks.
4. Tim Brewer separately performs scientific review and editorial review.
5. Only after both reviews may an operator prepare platform variants for Tim's manual publication.

Do not paste frontmatter, evidence ledgers, claims tables, validation output, or agent self-review into Substack or Medium.

The core commands are `python -m tools.publishing.validate_evidence`, `python -m tools.publishing.validate_draft`, and `python -m tools.publishing.validate_schedule`. Tests live in `tests/publishing/`. Reminder automation has no publication credentials or publication path. Its command and manual workflow are dry-run by default; issue writes require explicit human activation and preserve human text outside the managed region.
