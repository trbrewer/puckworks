# Sanctioned corpus export — contract v1 (WP1.7 / PR3)

The publication pipeline (`corpus_freeze`) requires a **coherent point-in-time export**, not
the moving public-updated window. This spec is defined and exercised BEFORE the real export
exists (via `corpus_export.synthetic_export`), so the schema is not decided under deadline.

Importer: `puckworks.data.corpus_export.import_sanctioned_export(records, export_manifest, dst)`.
It imports into a NEW empty store, writes Bronze lineage, drops post-cutoff records, quarantines
un-normalizable ones, and writes `source_export_manifest.json` — the coherence evidence a
publication freeze checks for a non-null `export_cutoff`.

## Export manifest (required / requested)

| field | req | meaning |
|---|---|---|
| `export_cutoff` | **required** | integer version/time boundary; every record's `updated_at` ≤ this. Its presence is what distinguishes an export from a moving feed. |
| `export_created_at` | requested | when the dump was produced |
| `source` | requested | source identity string |
| `license` | requested | data-use / attribution / redistribution terms |
| `privacy` | requested | PII policy + user-linkage scheme |

## Per-record fields (requested from the maintainer export)

- **stable shot id** (`id`) — required for version identity.
- **`updated_at`** — sufficiently precise integer version key (or an opaque monotone version id).
- **visibility / deletion state** — so tombstoned shots are excluded, not silently kept.
- **canonical telemetry** — `timeframe` + `data.*` channels; **raw telemetry** where permitted (Bronze).
- **machine vs integration/source** kept as DISTINCT fields (do not conflate).
- **channel quantity kinds + units** — especially commanded-vs-achieved identity for pressure/flow.
- **profile / control metadata** — needed for the declared pressure-atlas strata (WP2).
- **privacy-safe user linkage** (a stable opaque per-user token) OR a documented absence.
- **omitted-PII policy** — an explicit statement of what was dropped.

## Adversarial cases the importer + freeze pipeline must survive

Exercised by `synthetic_export()` and `tests/test_corpus_export.py`:
revisions (one id, multiple `updated_at`); equal-timestamp conflicts (same id+`updated_at`,
differing content → deterministic winner, conflict materialized); missing channels
(pressure-only); source-family differences; un-normalizable records (quarantined, not fatal);
records after the cutoff (excluded). All flow through
`import → reconcile → rehearse → materialize → verify → bundle`.

## Status

The synthetic export runs the complete pipeline to a **verified publication snapshot** in CI.
The REAL export (a Miha-side bulk dump/token) is still pending — see WP7 runbook and memory
`harvest-corpus-access-blocker`. When it arrives, follow WP7: import into a new store, pilot,
reconcile, rehearse, materialize, verify, then run the locked corpus products.
