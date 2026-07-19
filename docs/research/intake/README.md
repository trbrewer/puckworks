# Controlled research intake (issue #46, channel B)

This directory is the **controlled research-intake** channel: papers, datasets, reports, and notes
**deliberately supplied** to the project — including material privately uploaded to the maintainer that
GitHub Actions cannot see. Automation discovers external *metadata* (issue #42, `tools/research_radar.py`);
this channel captures **deliberate intake** as **metadata-only** records so a private upload becomes
visible to the deterministic registry-impact review without leaking its contents.

## What is here

- `schema.json` — JSON Schema (draft-07) for an intake record.
- `<stable-id>.yml` — one **metadata-only** record per source.
- (report) `tools/research_impact.py` computes deterministic JSON + Markdown deltas from these records,
  the model cards (`docs/cards/`), and the live registry.

## Hard rules (never store)

- **No copyrighted full text**, figures, tables, charts, images, or dataset rows.
- **No tokens, secret/tokenised URLs, private share links, email bodies, or uploaded file contents.**
- Only official public identifiers (DOI / arXiv id / official URL) and metadata the source *explicitly*
  states. A likely-useful variable is recorded only when the source describes it.

## Access / redistribution vocabulary

`access_state`: `metadata_only` · `open_access` · `project_private_review` · `rights_pending` ·
`redistribution_prohibited` · `redistribution_permitted`.

`redistribution_state`: `rights_pending` · `redistribution_prohibited` · `redistribution_permitted` ·
`not_applicable`.

## Dispositions (a disposition is NOT an implementation authorization)

`metadata_only` · `data-access-and-license-review` · `full-text-review` · `rights-review` ·
`already-carded` · `duplicate` · `superseded` · `implement-candidate` · `no-action`.

Implementation is **always** a separate, human-authorized scoped issue, card-first. The goal is better
**validated coverage**, not a larger registry.

## Identity and deduplication

Records are identified by **DOI → arXiv id → normalized title** (first available). Duplicates are
reported (never silently dropped); all provenance is preserved.

## Add a record

1. Copy the schema fields into `docs/research/intake/<stable-id>.yml` (metadata only).
2. Set honest `access_state` / `redistribution_state` / `disposition`.
3. Run `python tools/research_impact.py report` and review the deltas.
4. Any implementation is a separate authorized issue.

## Regenerate the impact report

```bash
python tools/research_impact.py report --format md      # human report
python tools/research_impact.py report --format json    # deterministic machine report
```

The report **cannot** modify a card, registry entry, model, claim, or evidence label, and performs no
network access.
