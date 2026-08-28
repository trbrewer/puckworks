# Puckworks publishing tooling

This directory governs evidence-bound editorial drafting. The source of truth is
[`PUBLISHING_SYSTEM.md`](PUBLISHING_SYSTEM.md); the style and platform checklists are supporting
controls. Nothing here publishes to Substack, Medium, or a community platform.

## Operator flow

1. Add an explicitly activated trigger to `content/triggers/`.
2. Run `python -m tools.publishing.validate_evidence content/triggers/TRIGGER.yml`.
3. Build an evidence ledger and master draft; keep synthetic fixtures under `tests/` only.
4. Run `python -m tools.publishing.validate_draft content/drafts/DATE-slug.md`.
5. After human scientific review, build the Substack variant manually.
6. After manual Substack publication, record and verify its exact URL before building Medium.
7. Tim Brewer performs the substantive Medium rewrite and all publication actions.

Schedule validation is `python -m tools.publishing.validate_schedule`. Tests are in
`tests/publishing/`. GitHub Actions may create or update editorial reminder issues; it has no
publication credentials or publication code path.
