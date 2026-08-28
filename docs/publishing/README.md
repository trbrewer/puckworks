# Puckworks publishing tooling

This directory governs evidence-bound editorial drafting. The source of truth is
[`PUBLISHING_SYSTEM.md`](PUBLISHING_SYSTEM.md); the style and platform checklists are supporting
controls. Nothing here publishes to Substack, Medium, or a community platform.

## Operator flow

1. Add an explicitly activated trigger to `content/triggers/`.
2. Run `python -m tools.publishing.validate_evidence content/triggers/TRIGGER.yml`.
3. Build an evidence ledger and master draft; keep synthetic fixtures under `tests/` only.
4. Run `python -m tools.publishing.validate_draft content/drafts/DATE-slug.md`.
5. After human scientific review, build the Substack variant manually. Existing variants are
   protected; replacement requires an explicit `--force`.
6. After manual Substack publication, record its exact URL as the intended Medium canonical, then
   build Medium. Canonical verification happens after the Medium page exists.
7. Tim Brewer performs the substantive Medium rewrite and all publication actions.

Schedule validation is `python -m tools.publishing.validate_schedule`. Tests are in
`tests/publishing/`. GitHub Actions may create or update editorial reminder issues; it has no
publication credentials or publication code path. Manual workflow dispatch is a dry run unless the
human explicitly selects `apply_changes`. The issue-sync CLI is also dry-run by default; `--apply`
is required for writes. A credential-free plan can use `--issues-json PATH`; without that fixture it
plans from an empty issue list and warns that remote deduplication was not evaluated. Updates preserve
human text outside the exact unkeyed `<!-- publishing-managed:start -->` and
`<!-- publishing-managed:end -->` region, and unchanged issues are not patched.
