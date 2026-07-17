# visualizer.coffee sanctioned-export readiness packet

A packet the maintainer can share with the visualizer.coffee data steward. It states exactly what
Puckworks requests, how the transfer is accepted, and what Puckworks will and will not publish. It is
**not sent automatically**; the maintainer decides when/whether to share it. Tracking issue: the
sanctioned-corpus-export issue in this repository.

## 1. Purpose

The ordinary public API exposes a **moving recent-updated window**, not the historical corpus. A
coherent, citable dataset requires a **point-in-time sanctioned export** with a governance record.
Puckworks publishes only privacy-safe **aggregate/derived** products from a verified frozen corpus —
never raw user records.

## 2. Exact requested files

- one immutable export archive (or corpus-scoped transfer) covering the agreed scope;
- one `source_export_manifest.json` (schema below);
- an archive checksum (SHA-256) computed by the source.

## 3. Manifest schema (publication profile)

Validated by `puckworks.data.corpus_export.validate_export_manifest(manifest, profile="publication")`,
which **fails closed** on any missing/invalid field:

| field | meaning |
|---|---|
| `export_spec_version` | export contract version |
| `source_name` / `source_authority` | source identity + authorising party |
| `export_created_at` | when the dump was produced |
| `export_cutoff` | integer version/time boundary; every record's version ≤ this |
| `source_schema_version` | source record schema version |
| `record_count` | total records in the export |
| `archive_or_export_sha256` | full lowercase SHA-256 of the archive/export |
| `stable_record_id_semantics` | how record IDs are stable |
| `record_version_semantics` | the monotone per-record version key |
| `user_linkage_semantics` | privacy-safe per-user token semantics (or documented absence) |
| `privacy_transform` | PII policy applied at/for export |
| `rights_basis` | rights basis for research use |
| `raw_redistribution_status` | `prohibited` or `permitted` |
| `aggregate_publication_status` | `permitted` or `prohibited` |
| `retention_policy` | how long Puckworks may retain the data |
| `deletion_or_correction_policy` | how deletions/corrections are handled |
| `contact_record` | authorising contact/authority |

## 4. Example manifest

See the synthetic-but-complete example produced by `corpus_export.synthetic_export()` (used only in
tests). A real export replaces the synthetic placeholders (notably `archive_or_export_sha256`,
`rights_basis`, and `contact_record`) with real values.

## 5. Checksum instructions

`sha256sum <export-archive>` (or `shasum -a 256`), recorded in `archive_or_export_sha256`. Puckworks
re-verifies the archive digest before import and refuses a mismatch.

## 6. Privacy and user-linkage requirements

- no reversible user identity; a salted one-way per-user token (or a documented absence);
- free-text/PII dropped at import;
- one-shot-per-user sensitivity applied to any public aggregate;
- small-cell suppression (or an equivalent disclosure rule) before public aggregate release.

## 7. Transfer acceptance (commands)

```
python -c "from puckworks.data.corpus_export import validate_export_manifest, import_sanctioned_export; \
  import json; m=json.load(open('source_export_manifest.json')); \
  validate_export_manifest(m, profile='publication')"
# import into a NEW empty store, then rehearse -> materialize -> verify -> bundle (WP7 runbook)
```

Acceptance requires: publication-profile manifest validates; import into a new empty store; clean
reconcile; a materialized publication freeze; an independently verified receipt.

## 8. What Puckworks will / will not publish

**Will**: privacy-safe aggregate/derived products (channel-availability denominators, operating-envelope
coverage, command-vs-achieved diagnostics, contributor-concentration diagnostics) with denominators and
snapshot hashes. **Will not**: raw or user-level records; user TDS/yield/sensory as ground truth; any
causal, channeling, permeability, machine-ranking, flavor, or recipe-optimality claim from the corpus
alone.

## 9. Failure and re-export handling

A failed import (bad checksum, non-empty destination, un-normalizable records beyond quarantine
tolerance, missing governance field) is reported and **not** materialized as publication. Corrections
are handled by a fresh source-side re-export, not by editing Puckworks-side data.

## 10. Attribution / share-back

Public products credit visualizer.coffee and the collective contributors per the agreed terms. Puckworks
shares back aggregate results and this methodology with the source.
