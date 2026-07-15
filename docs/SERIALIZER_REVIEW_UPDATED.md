# Updated review of the Visualizer serializer and Puckworks corpus harvester

**Review date:** July 15, 2026  
**Requested artifact:** `SERIALIZER_REVIEW_UPDATED.md`

## Executive verdict

The updated implementation is a **substantial improvement** over the version reviewed previously. It correctly handles Visualizer's top-level `timeframe`, preserves valid 0–100 enjoyment scores, stops labeling ambiguous reported flow as SI mass flow, parses malformed trace samples without losing alignment, creates fresh output directories before checking disk space, writes compressed shards atomically, retains a privacy-filtered Bronze representation, records run manifests, provides an offline re-normalization path, and defaults aggregate analysis to a one-record-per-shot view.

Those changes make the code suitable for:

- a bounded engineering pilot;
- normalizer and quality-control development;
- exploratory analysis of the recent public cohort exposed by the ordinary Visualizer API;
- testing an eventual static corpus export.

It is **not yet safe for a canonical full-corpus harvest or a paper-grade snapshot**. Four issues are blocking:

1. The ordinary Visualizer API still does not enumerate the full historical public corpus. A Premium account does not change the authenticated API listing into a corpus-wide listing.
2. An interrupted incremental run can advance its durable timestamp cursor past records that were never stored, permanently omitting them.
3. Record identity and the “latest” view are based only on `(shot_id, updated_at)`. Two changed versions sharing the same integer-second timestamp can be conflated, and the reader can return the earlier payload.
4. Visualizer can serialize either canonical chart data (`timeframe` plus `data`) or `brewdata`; the Puckworks normalizer extracts traces only from `data`. A corpus containing substantial `brewdata`-only populations may therefore yield normalized records with little or no usable telemetry.

There are also high-priority issues in reconciliation, Bronze recoverability and privacy, scalar validation, source provenance, chronology, record lifecycle handling, manifests, and million-record scalability.

### Readiness assessment

| Intended use | Readiness | Assessment |
|---|---:|---|
| Bounded engineering pilot | **Yes** | Good enough to exercise acquisition, normalization, QC, sharding, and exploratory summaries. |
| Recent-public exploratory dataset | **Yes, with caveats** | Must be labeled as a recent public API cohort, not the Visualizer corpus. |
| Import of a maintainer-provided static export | **Conditional** | Add an export adapter and fix version identity, failed-record retention, reconciliation, and provenance first. |
| Full historical corpus through the ordinary API | **No** | The current API scope does not expose it, and request-by-request crawling is impractical at corpus scale. |
| Canonical, reproducible research snapshot | **No** | Cursor loss, timestamp ties, incomplete provenance, and cross-file consistency remain blockers. |
| Paper-grade normalized modeling data | **No** | Source coverage, eligibility rules, units, chronology, and lifecycle semantics need stronger contracts. |

---

## Scope and reviewed revisions

This review covers both sides of the serialization boundary:

1. **Visualizer source serializer and API contract**
   - [`app/models/shot/jsonable.rb`](https://github.com/miharekar/visualizer/blob/ffe899b1a8849b7604905f4c5db7066bf09f76ab/app/models/shot/jsonable.rb)
   - [`app/controllers/api/shots_controller.rb`](https://github.com/miharekar/visualizer/blob/ffe899b1a8849b7604905f4c5db7066bf09f76ab/app/controllers/api/shots_controller.rb)
   - [`openapi.yaml`](https://github.com/miharekar/visualizer/blob/ffe899b1a8849b7604905f4c5db7066bf09f76ab/openapi.yaml)
   - Visualizer revision reviewed: `ffe899b1a8849b7604905f4c5db7066bf09f76ab`

2. **Puckworks acquisition, normalization, storage, and reading code**
   - [`puckworks/lib/visualizer_harvest.py`](https://github.com/trbrewer/puckworks/blob/adbac42e573de3ee7131b956dffb775562a1eb4f/puckworks/lib/visualizer_harvest.py)
   - [`tests/test_visualizer_harvest.py`](https://github.com/trbrewer/puckworks/blob/adbac42e573de3ee7131b956dffb775562a1eb4f/tests/test_visualizer_harvest.py)
   - [`puckworks/data/__init__.py`](https://github.com/trbrewer/puckworks/blob/adbac42e573de3ee7131b956dffb775562a1eb4f/puckworks/data/__init__.py)
   - Puckworks revision reviewed: `adbac42e573de3ee7131b956dffb775562a1eb4f`

I independently executed targeted local checks against the exact `visualizer_harvest.py` file at that Puckworks revision. I did **not** rerun the repository's entire test and gate suite in this review environment. The reviewed commit reports that its full suite passed, but the reproduced edge cases below are not covered by the current tests and still fail.

---

## Status of the earlier findings

| Earlier finding | Updated status | Notes |
|---|---:|---|
| Top-level `timeframe` was not read | **Resolved** | The normalizer reads the response root first and retains a nested fallback. |
| Fresh output directory could fail before first write | **Resolved** | `_crawl` now creates `out_dir` before the disk-space check. |
| Enjoyment values above 15 were discarded | **Resolved** | `espresso_enjoyment` is now validated on 0–100; other tasting dimensions remain 0–15. |
| Reported flow was mislabeled as SI mass flow | **Largely resolved** | Ambiguous reported flow stays native; only the scale-derived channel is converted. Source-side quantity and unit metadata would still be better. |
| Trace parsing could fail on booleans, strings, `NaN`, or infinity | **Mostly resolved** | Trace elements are parsed to finite floats or aligned `null`; scalar user/context fields remain less robust. |
| Normalized-only storage prevented offline repair | **Partly resolved** | A privacy-filtered Bronze payload and re-normalizer exist, but failed records are not written to Bronze and the privacy transform is shallow. |
| Incremental runs could accumulate duplicate observations | **Improved but not resolved** | There is a latest view and version-aware skipping, but timestamp-only identity fails on ties and interrupted cursors can omit records. |
| Atomic shard writes and reconciliation were absent | **Partly resolved** | Shard writes are atomic and a reconciler exists; index/cursor/manifest consistency and exact version reconciliation remain incomplete. |
| No stable integration/parser provenance | **Partly resolved** | Puckworks has an `integration_source` field, but Visualizer does not emit a stable source enum in the reviewed serializer, so values are often inferred or unknown. |
| Important chronology was discarded | **Unresolved** | `updated_at` is retained, but `start_time` is not present in the normalized record. |
| Full historical corpus access | **Unresolved outside the serializer** | The ordinary endpoint still exposes recent public records when unauthenticated and the authenticated user's own records when authenticated. |

---

# What the update now does well

## 1. Correct Visualizer trace layout

The Puckworks normalizer now reads `timeframe` from the top level of the detail response and falls back to `data.timeframe` for legacy fixtures. This matches the current Visualizer serializer, which emits chart records as:

```json
{
  "timeframe": [...],
  "data": {
    "espresso_pressure": [...],
    "espresso_flow": [...]
  }
}
```

This resolves the original failure in which valid channel arrays were retained without a time base and then classified as having zero samples. See [`normalize_shot`, lines 447–465](https://github.com/trbrewer/puckworks/blob/adbac42e573de3ee7131b956dffb775562a1eb4f/puckworks/lib/visualizer_harvest.py#L447-L465) and the Visualizer branch between chart-data and `brewdata` serialization in [`jsonable.rb`](https://github.com/miharekar/visualizer/blob/ffe899b1a8849b7604905f4c5db7066bf09f76ab/app/models/shot/jsonable.rb).

## 2. Correct outcome-scale separation

The code now distinguishes:

- `espresso_enjoyment`: 0–100;
- other sensory dimensions: 0–15;
- TDS and extraction yield: percentages converted to dimensionless fractions.

The update also preserves an actual score of zero instead of treating it as missing. This is important for unbiased outcome distributions and repeated-user preference analysis. See [`_SENSORY_MAX`, lines 108–117](https://github.com/trbrewer/puckworks/blob/adbac42e573de3ee7131b956dffb775562a1eb4f/puckworks/lib/visualizer_harvest.py#L108-L117) and [`normalize_shot`, lines 504–533](https://github.com/trbrewer/puckworks/blob/adbac42e573de3ee7131b956dffb775562a1eb4f/puckworks/lib/visualizer_harvest.py#L504-L533).

## 3. Safer flow semantics

The implementation no longer labels the ambiguous `espresso_flow` series as `kg/s`. It stores that channel as `flow_reported__native`, marks its SI unit as `null`, records a semantic description, and adds an ambiguity flag. The separate `espresso_flow_weight` channel is treated as scale-derived mass flow and converted from g/s to kg/s.

This is a major scientific improvement because downstream code can no longer accidentally treat a machine estimate or volumetric proxy as measured mass flow merely because of the column name. See [`_FLOW_CHANNELS` and `_AMBIGUOUS_FLOW_CHANNELS`, lines 77–90](https://github.com/trbrewer/puckworks/blob/adbac42e573de3ee7131b956dffb775562a1eb4f/puckworks/lib/visualizer_harvest.py#L77-L90) and [`normalize_shot`, lines 482–496](https://github.com/trbrewer/puckworks/blob/adbac42e573de3ee7131b956dffb775562a1eb4f/puckworks/lib/visualizer_harvest.py#L482-L496).

The remaining caution is that this is still a Puckworks-side interpretation. A source contract from Visualizer identifying the quantity kind, native unit, derivation method, and integration source for each channel would be stronger than a global name-based assumption.

## 4. Trace parsing preserves alignment

`_finite_float` rejects booleans, nonnumeric strings, `NaN`, and infinity. `_parse_series` inserts `null` in the original position instead of deleting the sample or failing the whole record. This is exactly the right default for time-aligned telemetry.

The QC block now records:

- sample count;
- valid timestamp count;
- nonincreasing and duplicate timestamp counts;
- median, minimum, maximum, and IQR of sampling intervals;
- channel length;
- valid and missing counts;
- whether each channel length matches the time vector;
- a simple flatline indicator.

See [`_finite_float` and `_parse_series`, lines 295–326](https://github.com/trbrewer/puckworks/blob/adbac42e573de3ee7131b956dffb775562a1eb4f/puckworks/lib/visualizer_harvest.py#L295-L326) and [`_timeseries_qc`, lines 329–363](https://github.com/trbrewer/puckworks/blob/adbac42e573de3ee7131b956dffb775562a1eb4f/puckworks/lib/visualizer_harvest.py#L329-L363).

## 5. Better recoverability and provenance foundations

The update adds several good operational foundations:

- destination creation before the first disk-space check;
- deterministic gzip output with `mtime=0`;
- temporary-file, `fsync`, and atomic rename for normalized and Bronze shards;
- an append-only version store plus a default latest-record reader;
- a rebuildable CSV index;
- a quarantine ledger;
- run manifests with source-code commit, schema versions, timestamps, configuration, and salt fingerprint;
- a privacy-filtered Bronze payload and offline re-normalizer.

These are meaningful improvements, not cosmetic changes. They reduce the chance that a long acquisition becomes unusable because of one parser defect or a torn compressed file.

## 6. Better test coverage

The current tests cover several previously missing cases, including:

- top-level `timeframe`;
- 0–100 enjoyment;
- fresh destination creation;
- Bronze storage and offline re-normalization;
- version-aware latest views;
- malformed trace parsing and quarantine behavior;
- manifests;
- integration-source fields;
- atomic writes and basic reconciliation;
- first-class QC output.

The remaining problems are primarily adversarial boundary cases: interrupted high-water marks, identical timestamp versions, exact index/shard reconciliation, nested free text, failed-record Bronze retention, source-shape coverage, and lifecycle changes.

---

# Blocking findings

## P0-1. The current API still cannot supply the full historical public corpus

This is not fixed by serializer work.

The reviewed Visualizer API controller begins its shot listing from:

```ruby
Current.user.present? ? Current.user.shots : Shot.visible
```

It then applies the non-Premium time restriction unless the authenticated user is Premium. The documented `updated_after` filter is applied only for an authenticated user. The practical result is:

| Request context | Listing scope |
|---|---|
| Unauthenticated | Recent public/visible records, subject to the non-Premium window |
| Authenticated free account | Recent records belonging to that account |
| Authenticated Premium account | Historical records belonging to that account |
| Full historical public corpus | Not exposed by the ordinary documented listing |

See the reviewed [`Api::ShotsController`](https://github.com/miharekar/visualizer/blob/ffe899b1a8849b7604905f4c5db7066bf09f76ab/app/controllers/api/shots_controller.rb) and [`openapi.yaml`](https://github.com/miharekar/visualizer/blob/ffe899b1a8849b7604905f4c5db7066bf09f76ab/openapi.yaml).

The current Puckworks client also has no authentication or bulk-export adapter. Its `list_public_shot_ids` calls the ordinary public endpoint. Therefore, even a technically flawless run would produce a recent-public cohort rather than the full authorized corpus.

### Required resolution

The maintainer should provide one of these:

1. **A consistent static snapshot**, preferably compressed NDJSON or Parquet, with a manifest and checksums; or
2. **A corpus-scoped endpoint and token** that enumerate the permitted population with deterministic keyset pagination; or
3. **A database/export artifact** produced under the explicit permission grant.

A static snapshot is preferable. At the current request-per-record design and a conservative sustained rate, a million-record transfer would require many weeks before retries, listing calls, and reconciliation. A multi-million-record corpus is not appropriately transferred through ordinary detail requests.

### Puckworks change needed

Add a separate import command rather than forcing a static export through the online crawler, for example:

```text
python -m puckworks.lib.visualizer_harvest import-snapshot \
    --input visualizer_snapshot_2026-07-15.ndjson.zst \
    --manifest visualizer_snapshot_2026-07-15.manifest.json
```

The importer should validate the source manifest and hashes, retain the source payload, normalize offline, write exact version identities, and produce an import reconciliation report.

---

## P0-2. An interrupted incremental run can permanently skip records

The incremental listing is ordered newest-first by `updated_at`. During `_crawl`, Puckworks tracks the maximum update timestamp encountered. In the `finally` block it saves that maximum cursor even when the run stopped before all eligible records were fetched.

See:

- [`list_public_shot_ids`, lines 232–256](https://github.com/trbrewer/puckworks/blob/adbac42e573de3ee7131b956dffb775562a1eb4f/puckworks/lib/visualizer_harvest.py#L232-L256)
- [`_crawl`, lines 935–1007](https://github.com/trbrewer/puckworks/blob/adbac42e573de3ee7131b956dffb775562a1eb4f/puckworks/lib/visualizer_harvest.py#L935-L1007)

I reproduced this exact failure:

```text
Committed cursor before run: 100
Eligible source records, descending: A@200, B@199
Run limit: fetch one detail record
```

Observed behavior:

1. `A@200` was stored.
2. The run stopped incomplete.
3. The durable cursor was advanced to `200` in `finally`.
4. The next strict `updated_after=200` query returned neither `A@200` nor `B@199`.
5. `B@199` was permanently omitted.

This is a canonical high-water-mark error. The fact that the source is descending makes `max(updated_at seen)` unsafe until the whole eligible range has been drained.

### Preferred fix

Use an opaque server cursor based on deterministic ascending keyset order:

```sql
ORDER BY updated_at ASC, id ASC
```

with cursor state equivalent to:

```text
(updated_at, id)
```

Advance the committed cursor only after the corresponding detail payload and acquisition ledger entry are durable.

### Temporary client-side fix

Until the source supports a compound cursor:

- never advance the committed incremental cursor when `completed == false`;
- keep a separate provisional run checkpoint;
- overlap the next query by at least one timestamp bucket;
- deduplicate by a content-aware version identity;
- fully consume all records sharing a timestamp before advancing beyond it.

At minimum, change the `finally` behavior so an incomplete run retains the prior committed cursor. Reprocessing already stored versions is safe; silently missing an unseen version is not.

### Required regression test

Create records `A@200` and `B@199`, stop after `A`, rerun from the persisted cursor, and assert that the final latest store includes both records.

---

## P0-3. Timestamp-only version identity can return the wrong payload

The current index columns do not include a content hash, ingest sequence, shard, or line offset. The latest index chooses the last-written row when `updated_at` ties, but `iter_store_latest` subsequently selects a winner using only:

```text
shot_id + updated_at
```

and yields the **first** physical record that matches that pair.

See:

- [`latest_index_rows`, lines 624–637](https://github.com/trbrewer/puckworks/blob/adbac42e573de3ee7131b956dffb775562a1eb4f/puckworks/lib/visualizer_harvest.py#L624-L637)
- [`iter_store_latest`, lines 647–659](https://github.com/trbrewer/puckworks/blob/adbac42e573de3ee7131b956dffb775562a1eb4f/puckworks/lib/visualizer_harvest.py#L647-L659)
- [`_INDEX_COLUMNS`, lines 129–132](https://github.com/trbrewer/puckworks/blob/adbac42e573de3ee7131b956dffb775562a1eb4f/puckworks/lib/visualizer_harvest.py#L129-L132)

I reproduced this with two versions of one shot:

```text
shot A, updated_at=100, pressure=1 bar
shot A, updated_at=100, pressure=9 bar
```

The index's tie policy treated the second row as the winner, but the latest-store iterator returned the first payload: 1 bar rather than 9 bar.

A related acquisition defect appears in `_crawl`:

```python
if have is not None and upd_i is not None and upd_i <= have:
    continue
```

A changed source payload with the same integer-second `updated_at` is never fetched once that timestamp is present locally. Visualizer's API representation uses integer timestamps, so a tie is not merely theoretical.

### Required identity model

A stored version needs at least:

```text
shot_id
updated_at
content_sha256
ingest_sequence or harvested_at_ns
source_snapshot_id or run_id
shard_path
record_offset or record_number
```

A defensible unique version key is:

```text
(shot_id, updated_at, content_sha256)
```

The latest-selection rule should use an explicit deterministic ordering, such as:

```text
(updated_at, source_sequence, ingest_sequence)
```

For a static snapshot, source sequence may be unnecessary if each shot occurs once and the manifest guarantees uniqueness. For a moving API, the exact stored version must be addressable rather than rediscovered by timestamp matching.

### Recommended storage index

A small SQLite or DuckDB catalog would be safer than append-only CSV:

```sql
CREATE TABLE versions (
    shot_id TEXT NOT NULL,
    updated_at INTEGER,
    content_sha256 TEXT NOT NULL,
    ingest_seq INTEGER NOT NULL,
    run_id TEXT NOT NULL,
    shard TEXT NOT NULL,
    record_number INTEGER NOT NULL,
    is_latest BOOLEAN NOT NULL,
    PRIMARY KEY (shot_id, updated_at, content_sha256)
);
```

### Required regression tests

- Same ID and same timestamp, different payload hashes: the designated later version must be returned.
- Same ID, timestamp, and hash: the second retrieval must be idempotently skipped.
- Same ID, older timestamp, different hash: policy must be explicit rather than silently replacing the latest state.

---

## P0-4. `brewdata`-only records may normalize to little or no telemetry

The current Visualizer serializer has two shapes:

```ruby
if information.chart_data?
  # top-level timeframe + data
else
  # brewdata
end
```

Puckworks uses `brewdata` for best-effort machine/source inference, but all hydraulic trace extraction is from `raw["data"]`. If a record contains only `brewdata`, the normalizer generally reports missing `timeframe` and missing channels rather than converting the source-specific payload into a canonical trace.

This can create a subtle corpus-selection problem: the resulting dataset may appear large while useful telemetry is concentrated in only those integrations that Visualizer has already transformed into chart data. Different machines or source applications could be systematically excluded from model-ready subsets.

### Required next step

Before a full acquisition, estimate record counts by serialization shape:

```text
chart_data: top-level timeframe + data
brewdata_only
authored metadata only
malformed/other
```

Then create a real-response fixture matrix covering at least the major Visualizer integrations present in the authorized corpus. For every source, determine whether:

- Visualizer returns canonical chart data;
- Puckworks needs a source-specific `brewdata` adapter;
- units and quantity kinds are documented;
- sampling cadence and channel semantics differ;
- machine and parser provenance are available.

If Visualizer can supply the static corpus export, the best design is for the export to include both the original permitted payload and a source-side canonical chart representation for every supported integration.

---

# High-priority findings

## P1-1. Reconciliation can report `ok` while an exact version is missing from the index

`reconcile_store` compares sets of shot IDs between shards and the index. It does not compare the exact multiset of version keys or row counts by version.

I reproduced this store:

```text
Shard: A@100, A@101
Index: A@101 only
```

The reconciler returned `ok: true` because both sides contained the shot ID `A`. One stored version had no index row, but no problem was reported.

See [`reconcile_store`, lines 1090–1140](https://github.com/trbrewer/puckworks/blob/adbac42e573de3ee7131b956dffb775562a1eb4f/puckworks/lib/visualizer_harvest.py#L1090-L1140).

### Fix

Reconciliation should compare exact records, not only ID sets:

- normalized version key multiset versus index version key multiset;
- normalized version key multiset versus Bronze version key multiset;
- per-shard record counts versus manifest counts;
- source payload hash versus recorded hash;
- all index pointers versus readable shard records;
- no orphan normalized record, Bronze record, index row, or quarantine reference;
- exactly one latest pointer per live shot;
- file checksums against the run manifest.

`_sha256_file` already exists but is not incorporated into run manifests or reconciliation. It should be used for every committed shard and index snapshot.

---

## P1-2. Bronze does not retain the records that most need future repair

Bronze is created only after normalization and strict serialization of the tidy record succeed:

```text
fetch raw
normalize
validate tidy JSON
append tidy
append Bronze
```

If `normalize_shot` fails because of an unanticipated response shape, the code writes only a quarantine entry containing a hash and error text. It does not store the payload or a pointer to a stored acquisition record.

I reproduced this with a malformed detail object whose `data` field was a string. The run reported one quarantined record and zero Bronze records. The quarantine row contained only:

```text
run_id
id
updated_at
failure_stage
exception_type
reason
content_sha256
```

That record cannot be re-normalized offline because the exact source payload was discarded. This undercuts the main purpose of Bronze precisely for new parser failures.

### Fix

Write the acquisition record **before** normalization, then reference it from normalized and quarantine records:

```text
1. Fetch response.
2. Validate only enough to build an acquisition envelope.
3. Apply the approved privacy transform.
4. Store acquisition payload durably with a hash.
5. Attempt normalization.
6. Store either a normalized pointer or a quarantine pointer to the same acquisition key.
```

Suggested acquisition key:

```text
(run_id, source_sequence, shot_id, source_updated_at, content_sha256)
```

The quarantine ledger should include:

```text
bronze_shard
bronze_record_number
content_sha256
http_status
endpoint
retry_count
```

---

## P1-3. The Bronze privacy transform is shallow and context retains free text

`_strip_pii` drops a short list of top-level keys only:

```python
return {k: v for k, v in raw.items() if k not in _PRIVACY_DROP}
```

I confirmed that nested values such as these survive:

```json
{
  "metadata": {
    "user_name": "nested",
    "email": "x@example.com",
    "notes": "nested note"
  },
  "tags": ["person-name"],
  "profile_title": "John home profile"
}
```

The normalized `context` also retains `profile_title`, `tags`, `grinder_model`, and `grinder_setting`. Some are analytically useful, but `profile_title` and tags are free text and can contain names, locations, equipment serials, or other identifying details. This conflicts with the module-level statement that all free text is dropped.

### Recommended privacy architecture

Use an explicit, recursive allowlist rather than a denylist. Separate three release levels:

1. **Restricted acquisition layer**: exact permitted source payload, encrypted/access-controlled, never public.
2. **Internal research layer**: approved structured fields, pseudonymous link key, free-text either removed or processed under a documented review policy.
3. **Public derivative layer**: aggregates or disclosure-reviewed rows with no stable user link key and no free text.

If the permission agreement prohibits retaining the raw payload, then define a schema-aware recursive transform and test it against nested metadata. Do not describe the result as fully raw or immutable; call it a **privacy-filtered acquisition payload**.

The current `hash_user` also uses a concatenated salt and a 64-bit truncated digest. For internal longitudinal linkage, prefer keyed HMAC-SHA-256 and retain at least 128 bits. Use a release-specific key or omit the link key entirely from public artifacts.

---

## P1-4. Scalar parsing accepts booleans and non-finite values

Trace parsing is robust, but `_num` is not equivalent. I confirmed:

```text
_num(True)  -> 1.0, clean
_num(NaN)   -> NaN, clean
_num(Inf)   -> Inf, clean
_num("nan") -> NaN, clean
_num("inf") -> Inf, clean
```

Consequences include:

- a boolean can become a dose, duration, TDS, EY, or drink weight;
- `NaN` or infinity can enter the tidy object and cause the entire shot to be quarantined later by `json.dumps(..., allow_nan=False)`;
- the error is attributed to serialization rather than the field that was invalid;
- numeric user entries outside plausible physical ranges are accepted;
- sensory floats are silently truncated with `int(v)` rather than rejected or explicitly rounded;
- `duration` ignores the `dirty` flag returned by `_num`.

See [`_num`, lines 399–421](https://github.com/trbrewer/puckworks/blob/adbac42e573de3ee7131b956dffb775562a1eb4f/puckworks/lib/visualizer_harvest.py#L399-L421).

### Fix

Create one finite scalar parser with field-specific policies:

```python
def parse_finite_scalar(value, *, minimum=None, maximum=None,
                        allow_suffix=False, integer=False):
    ...
```

For each field, preserve:

```text
raw value or raw-class summary
parsed value
parse status
range status
source unit
conversion performed
```

Reasonable validation should flag, rather than necessarily delete, implausible values. Examples include negative duration, dose, drink weight, TDS, or extraction yield; extraction yield far above a declared research ceiling; and TDS outside a physically plausible range. Exact thresholds should be documented and source-aware rather than silently embedded.

---

## P1-5. Brew chronology is missing from the normalized layer

The Visualizer detail representation includes `start_time`, but the normalized Puckworks record retains only `updated_at`. Update time is an edit/upload timestamp, not the brew event time.

Without `start_time`, later work cannot reliably perform:

- chronological train/validation/test splits;
- firmware- or parser-era analyses;
- seasonality checks;
- detection of retrospective uploads;
- leakage audits across a user's successive shots;
- longitudinal behavior analysis;
- calibration-drift studies.

### Fix

Retain chronology at two levels:

- protected exact `start_time` and `updated_at` in the restricted acquisition/internal layer;
- privacy-reviewed date bucket, such as month or week, in general research extracts.

Also retain provenance for whether the timestamp is source-recorded, upload-derived, or inferred. A static corpus snapshot should have its own `snapshot_at`, distinct from both shot timestamps.

---

## P1-6. Integration source remains inferred, unknown, or conflated with machine

Puckworks now has separate fields for machine and `integration_source`, which is a good schema decision. The source value, however, is usually not available explicitly from the reviewed Visualizer serializer. `_integration_source` falls back to `_infer_machine`, even though its docstring says source is never guessed from machine.

As a result:

- a machine label can be recorded as an integration source;
- chart-data records without `brewdata`, `source`, or `machine` can remain unknown;
- parser/firmware versions are unavailable;
- source-dependent units, smoothing, sensor placement, and derived-flow methods cannot be stratified reliably.

See [`_infer_machine` and `_integration_source`, lines 366–396](https://github.com/trbrewer/puckworks/blob/adbac42e573de3ee7131b956dffb775562a1eb4f/puckworks/lib/visualizer_harvest.py#L366-L396).

### Visualizer-side recommendation

Add controlled, documented fields to the authorized export or serializer:

```json
{
  "integration_source": "gaggiuino",
  "integration_schema_version": 3,
  "parser_name": "...",
  "parser_version": "...",
  "machine_make": "Gaggia",
  "machine_model": "Classic Pro",
  "channel_contract": {
    "espresso_flow": {
      "quantity_kind": "volumetric_flow",
      "unit": "mL/s",
      "derivation": "machine_estimate"
    }
  }
}
```

Until this exists, source-stratified modeling should either exclude unknown records or treat source as an explicit missing/confounded variable. It should not infer scientific equivalence from a common channel name.

---

## P1-7. Record identity, listing/detail consistency, and lifecycle are not validated

The crawler assumes that the detail response belongs to the listed ID and version. It does not validate:

- `raw.id == listed sid`;
- detail `updated_at` is consistent with the list row;
- the response schema is the expected endpoint shape;
- a record that changes between list and detail retrieval;
- a shot that becomes private or is deleted after listing.

A persistent fetch error currently stops the whole crawl. A 404 or 403 caused by a normal visibility race should instead become a classified per-record event and allow the run to continue.

There is also no tombstone or withdrawal policy. Once stored, a shot can remain in the latest analytic view even if it is later deleted or made private.

### Fix

Add an acquisition status ledger with classifications such as:

```text
fetched
unchanged
changed_during_fetch
not_found
became_private
rate_limited
transient_server_error
permanent_schema_error
quarantined
tombstoned
```

Define whether the authorized snapshot is historical and immutable or whether later source withdrawals must remove records from future research datasets. This is a governance decision that should be encoded in manifests and loaders, not improvised later.

---

## P1-8. Run manifests are useful but insufficient, and run IDs can collide

The current run ID is:

```python
run_%d_%d % (int(started_at), os.getpid())
```

I observed two runs started in the same second under the same process receiving the same run ID. Their manifest path is therefore identical and can be overwritten.

Manifest write failures are also swallowed, so an otherwise completed run may have no provenance record without surfacing a failure. The manifest currently lacks several items needed for a reproducible corpus statement:

- Visualizer source revision or API schema version;
- access scope and authorization mechanism;
- source snapshot ID or starting/ending source cursor;
- expected/listed ID count;
- detail success and failure counts by class;
- normalized, Bronze, index, quarantine, and tombstone counts;
- shard filenames, byte sizes, record counts, and hashes;
- index hash;
- source payload hash totals or Merkle/root digest;
- prior and committed cursor values;
- an explicit statement that the run completed coherently.

### Fix

Use `uuid4`, ULID, or `time_ns` plus randomness for run identity. Write an atomic **started** manifest before acquisition, update through a journal or temporary file, and atomically finalize it after reconciliation. A missing or unwritable final manifest should make the run incomplete, not disappear silently.

---

## P1-9. Atomic individual files do not provide atomic multi-file commits

A flush currently performs:

1. normalized shard write;
2. optional Bronze shard write;
3. CSV index append.

Each shard write is atomic, but the bundle is not. A crash between steps can leave:

- a normalized shard without Bronze;
- normalized and Bronze shards without index rows;
- a partially appended index;
- a cursor advanced beyond the fully reconciled bundle.

The index append is not `fsync`ed or atomically replaced. Cursor and page-checkpoint files are also written directly rather than by temporary-file rename.

### Fix

Treat each shard bundle as a transaction:

```text
write normalized temp
write Bronze temp
write bundle manifest temp
fsync all
rename data files
rename bundle commit marker last
rebuild/update catalog from committed bundle
advance cursor only after bundle reconciliation
```

Alternatively, use SQLite/DuckDB for the catalog and transactions, while retaining immutable compressed payload shards. On startup, recover or remove uncommitted temporary bundles before resuming.

---

# Additional scientific and engineering findings

## 1. Quality metrics do not yet implement model eligibility

The QC block is useful, but the code comment says the metrics “feed declared eligibility rules downstream.” No concrete eligibility functions or named cohorts are implemented in the reviewed file.

Create explicit, versioned tiers, for example:

```text
trace_present_v1
hydraulic_basic_v1
mass_flow_validated_v1
pressure_flow_model_v1
outcome_tds_v1
outcome_sensory_v1
longitudinal_user_v1
```

Each tier should emit pass/fail plus reason codes. This prevents each paper or notebook from inventing a different undocumented filter.

## 2. Timestamp QC can hide gaps

`_timeseries_qc` removes `None` timestamps before calculating intervals. If the raw series is:

```text
0.0, null, 2.0
```

it calculates a single 2-second step between nonadjacent positions, losing the fact that one timestamp was missing. An all-null or one-valid-value vector can also be marked monotonic because there are no nonpositive steps.

Add:

- missing timestamp count and fraction;
- adjacency-aware interval calculations;
- longest run of missing timestamps;
- explicit `insufficient_time_for_monotonicity` status;
- start/end/duration consistency;
- comparison of declared duration with final time value.

## 3. Channel QC needs physical and cross-channel checks

Useful additions include:

- finite min/max and quantiles;
- out-of-plausible-range count;
- longest flatline duration, not only “all values equal”;
- derivative spikes;
- cumulative weight monotonicity and negative-step counts;
- pressure/flow/weight onset alignment;
- scale-flow integral versus observed weight change;
- declared duration versus trace duration;
- source-specific expected-channel matrix;
- source-specific sampling-cadence expectations.

Global `missing:<channel>` flags should not automatically imply bad quality. A channel can be legitimately unavailable for one integration and required for another.

## 4. Useful context is underrepresented in Silver

Visualizer's serializer can expose structured fields such as bean brand/type, roast date, roaster or coffee-bag identifiers, dose, beverage weight, grinder details, and roast level. Puckworks retains only a subset in normalized context.

For many Puckworks questions, these fields can support:

- repeated-coffee controls;
- roast-age analysis;
- dose/yield-ratio features;
- grinder-stratified validation;
- profile transfer across coffee contexts;
- user and coffee fixed effects;
- domain-shift assessment.

Add useful structured fields with explicit missingness and privacy review. Do not import unrestricted notes into general research tables.

## 5. The re-normalizer needs its own failure and provenance contract

`renormalize_from_bronze` can abort on one malformed Bronze payload. It does not verify the stored content hash before use, produce a run manifest, quarantine bad Bronze records, or protect against writing into a nonempty destination with conflicting shard names.

A re-normalization run should be treated like a first-class transformation job:

- validate every Bronze hash;
- record source Bronze manifest and normalizer commit/version;
- quarantine per record rather than aborting all work;
- produce exact input/output counts;
- write to a new immutable destination;
- reconcile before publishing a “complete” marker.

## 6. Million-record scalability needs redesign

With `shard_size=100`, one million records produce roughly:

- 10,000 normalized gzip files;
- 10,000 Bronze gzip files;
- one very large append-only CSV index.

Every run reads the whole index into a dictionary, and `rebuild_index` loads all generated rows into memory before writing. The online path also performs approximately one detail request per shot.

For a full corpus, prefer:

- a server-generated bulk export;
- larger byte-targeted shards, not 100-record shards;
- Parquet for normalized tables and feature tables;
- compressed NDJSON or source-native export for restricted acquisition payloads;
- SQLite or DuckDB for version/catalog state;
- partitioning by snapshot/run/source or hashed shot prefix;
- streaming index rebuilds;
- explicit storage estimates before acquisition.

## 7. Concurrency and checkpoint safety are not defined

Two harvest processes targeting the same directory can choose the same next shard index and temporary filename. There is no directory lock or writer identity. Cursor and page-checkpoint JSON files are non-atomic and can become corrupt during interruption.

Use a process/file lock for the store, atomic checkpoint writes, and a recovery rule for malformed checkpoints. A static snapshot importer should support parallel parsing only through controlled partitions with disjoint output paths.

## 8. `max_requests` is not the total HTTP request cap

The variable `n_fetched` counts detail records fetched, while list-page requests also consume API quota. Therefore `--max-requests N` does not bound total HTTP requests to `N`. This is mainly a naming/documentation issue but matters for a “respectful harvester.” Rename it to `--max-detail-fetches` or account for all HTTP calls in a shared request counter.

---

# Independently reproduced failure cases

These checks were run against the exact Puckworks harvester file at revision `adbac42e573de3ee7131b956dffb775562a1eb4f`.

## Reproduction A: interrupted cursor skips an eligible record

**Setup**

```text
Existing cursor: 100
Source order: A@200, B@199
Stop after one detail fetch
```

**Observed**

```text
Stored after first run: A
Persisted cursor: 200
Second strict query: no rows
Final stored IDs: A only
Missing permanently: B
```

**Severity:** P0 data loss.

## Reproduction B: equal-timestamp latest view returns earlier content

**Setup**

```text
A@100 payload 1: pressure = 1 bar
A@100 payload 2: pressure = 9 bar
```

**Observed**

The index's tie rule selected the later index row, but the store iterator yielded the first shard record matching `A@100`. The returned normalized pressure was 100,000 Pa rather than 900,000 Pa.

**Severity:** P0 silent wrong-data selection.

## Reproduction C: reconciliation false positive

**Setup**

```text
Shard versions: A@100, A@101
Index versions: A@101
```

**Observed**

```json
{
  "ok": true,
  "n_shard_records": 2,
  "n_index_rows": 1,
  "problems": []
}
```

**Severity:** P1; integrity checks can certify an inconsistent store.

## Reproduction D: malformed source payload is not recoverable offline

**Setup**

A fetched record caused normalization to raise because `data` was not a dictionary.

**Observed**

```text
Quarantined: 1
Bronze records: 0
Quarantine contains: hash + reason, no payload or Bronze pointer
```

**Severity:** P1; future normalizer repair is impossible for the records most likely to need it.

## Reproduction E: nested PII/free text survives `_strip_pii`

**Setup**

Nested `metadata.user_name`, `metadata.email`, `metadata.notes`, free-text tags, and a personalized profile title.

**Observed**

All nested and non-denylisted free text survived the Bronze transform.

**Severity:** P1 privacy/governance mismatch.

## Reproduction F: scalar booleans and non-finite values are accepted

**Observed**

```text
True -> 1.0
NaN -> NaN
Inf -> Inf
"nan" -> NaN
"inf" -> Inf
```

**Severity:** P1 field-quality and avoidable-quarantine risk.

## Reproduction G: run manifest ID collision

Two runs started within the same integer second under the same process generated the same `run_<seconds>_<pid>` identifier and therefore the same manifest path.

**Severity:** P1 provenance overwrite risk.

---

# Recommended implementation sequence

## Phase 1: secure the acquisition contract

1. Obtain a static corpus export or corpus-scoped API endpoint/token.
2. Define the exact permitted population: public-only, deleted-history policy, private records excluded or included, and user-linkage terms.
3. Require a source manifest containing snapshot time, record count, schema/source revision, and checksums.
4. Add a Puckworks static-export importer.

## Phase 2: fix identity and commit semantics

1. Replace timestamp-only identity with `(id, updated_at, content_sha256)`.
2. Record exact shard and record location in a transactional catalog.
3. Fix incomplete incremental cursor advancement.
4. Use deterministic compound source cursors when online incremental acquisition is required.
5. Introduce unique run IDs and atomic started/final manifests.
6. Make normalized, acquisition, index, and cursor updates a recoverable bundle transaction.

## Phase 3: make acquisition lossless within the approved privacy contract

1. Persist the privacy-approved acquisition record before normalization.
2. Reference acquisition records from both normalized and quarantine rows.
3. Replace shallow denylisting with a schema-aware allowlist or retain exact payload only in a restricted layer.
4. Verify content hashes before re-normalization.
5. Add tombstone and lifecycle semantics.

## Phase 4: strengthen scientific semantics

1. Retain `start_time` and approved chronology buckets.
2. Obtain explicit integration/parser, machine, units, quantity-kind, and derivation metadata.
3. Audit `brewdata`-only coverage by integration.
4. Add source-specific adapters or source-side canonical chart serialization.
5. Harden scalar parsing and field-specific validation.
6. Add structured coffee, roast, grinder, dose, and beverage context.
7. Define versioned model-eligibility cohorts and reason codes.

## Phase 5: pilot and reconcile

Run a bounded pilot from the actual authorized transfer path—not merely the recent public endpoint. Produce:

- source expected count versus imported count;
- exact payload-hash reconciliation;
- normalized, Bronze, quarantine, and tombstone counts;
- serialization-shape distribution;
- integration-source distribution and unknown rate;
- trace-channel coverage by integration;
- timestamp and cadence QC;
- scalar parse/range failure rates;
- outcome availability and value distributions;
- random and source-stratified raw-to-normalized manual audits;
- file/catalog checksums;
- deterministic re-import result.

Only after those checks should the canonical import begin.

---

# Acceptance tests to add before the canonical harvest

## Acquisition and cursor tests

1. Interrupted descending incremental run with `A@200` and `B@199`; both must eventually be stored.
2. Same-second timestamp cohort spanning multiple pages; no omission or duplication after resume.
3. Cursor is unchanged after incomplete runs unless the server cursor contract explicitly guarantees safety.
4. List/detail ID mismatch is quarantined and does not enter the store under the wrong ID.
5. List/detail version mismatch receives an explicit policy and status.
6. 404/403 visibility race is recorded and the crawl continues.
7. Persistent 429/5xx behavior preserves committed work and a resumable source position.
8. `max_requests` or its replacement accurately reflects all HTTP calls.

## Version and latest-view tests

1. Same ID, same timestamp, changed content hash.
2. Same ID, same timestamp, identical content hash.
3. Same ID, newer timestamp.
4. Same ID, older timestamp arriving later.
5. Latest pointer resolves the exact physical record, not any record sharing its timestamp.
6. Deleted/private record tombstone behavior.
7. Record becomes visible again after a tombstone.

## Reconciliation tests

1. Shard version missing from index must fail.
2. Index version missing from shard must fail.
3. Normalized version missing from Bronze must fail when Bronze is required.
4. Bronze record missing from normalized and quarantine outputs must fail.
5. Duplicate exact version key must fail or be explicitly idempotent.
6. Corrupted gzip, JSON line, content hash, index pointer, and manifest checksum must fail.
7. Reconciliation must be deterministic and produce a machine-readable report.

## Privacy and recoverability tests

1. Nested names, emails, notes, locations, URLs, and arbitrary metadata.
2. Free-text profile titles and tags.
3. Failed normalization still leaves a recoverable acquisition payload or approved reference.
4. Public-export builder removes stable user link keys and free text.
5. Hash-linkage implementation uses a secret key and sufficient output length.

## Scalar tests

1. `null`, empty string, zero, numeric string, numeric suffix, boolean, `NaN`, infinity, and malformed text.
2. Negative and implausibly high TDS, EY, dose, beverage weight, and duration.
3. Sensory float policy: reject, preserve decimal, or explicitly round—never silently truncate without a flag.
4. Dirty duration and unit suffix flags are retained.

## Source-shape fixture matrix

Use actual permission-approved responses for the major corpus integrations, including at least those represented materially in the export. For each source, test:

- canonical chart-data shape;
- `brewdata`-only shape;
- integration and parser identity;
- machine make/model;
- channel quantity kinds and units;
- optional outcomes and context;
- nulls and malformed samples;
- expected channel availability;
- cadence and timestamp behavior.

Candidate integrations named in the current project context include Decent, Meticulous, Beanconqueror, Gaggiuino, GaggiMate, Smart Espresso Profiler, and Pressensor. The actual matrix should be based on corpus counts rather than assumptions.

## Chronology and QC tests

1. `start_time` retained at the approved precision.
2. Missing timestamp inside a series does not disappear from cadence QC.
3. All-null and one-valid timestamp vectors are “insufficient,” not automatically valid.
4. Duplicate, decreasing, and large-gap timestamps.
5. Channel length mismatch and state-channel QC.
6. Weight monotonicity and flow-integral consistency where applicable.
7. Source-specific expected-channel and range rules.
8. Named eligibility tiers produce stable reason codes.

---

# Suggested target data architecture

## Restricted acquisition layer

One envelope per fetched/exported source record:

```json
{
  "acquisition_schema_version": 1,
  "run_id": "01J...",
  "source_snapshot_id": "visualizer-2026-07-15",
  "source_sequence": 123456,
  "endpoint_or_export": "snapshot.ndjson.zst",
  "http_status": 200,
  "harvested_at": "2026-07-15T...Z",
  "shot_id": "...",
  "source_updated_at": 1784...,
  "content_sha256": "...",
  "privacy_transform_version": "restricted-exact-or-allowlist-v1",
  "payload": {}
}
```

## Normalized version table

```text
shot_id
source_updated_at
content_sha256
source_snapshot_id
ingest_sequence
normalizer_schema_version
normalized_payload_location
acquisition_payload_location
status
```

## Latest-state table

Exactly one explicit pointer per live shot:

```text
shot_id
latest_version_key
latest_reason
is_tombstoned
tombstone_reason
```

## Research tables

Separate by evidence tier:

- hydraulic traces;
- trace QC and eligibility;
- structured shot context;
- user-entered analytical outcomes;
- source/integration provenance;
- derived trace features;
- privacy-reviewed aggregate/public products.

This keeps machine telemetry, user-entered measurements, and sensory preference from being silently merged into one undifferentiated “ground truth” row.

---

# Recommended pilot decision gates

Proceed from pilot to canonical acquisition only when all of these are true:

1. **Scope gate:** the source manifest or endpoint demonstrably includes historical public shots outside the ordinary recent window and records from users other than the authenticated research account.
2. **Count gate:** expected source count reconciles exactly to acquisition records, classified exclusions, and documented tombstones.
3. **Identity gate:** equal timestamps and changed content cannot be conflated.
4. **Resume gate:** every forced interruption point resumes without omitted eligible records.
5. **Recoverability gate:** every fetched/exported record is either normalized or recoverably quarantined.
6. **Privacy gate:** storage layers and release layers pass a documented nested-field review.
7. **Source gate:** integration provenance and serialization shape coverage are quantified; unsupported sources are explicit.
8. **Unit gate:** every model-used channel has documented quantity kind, unit, derivation, and source scope.
9. **Chronology gate:** brew and update timestamps support leakage-safe splits and snapshot claims.
10. **Integrity gate:** exact cross-layer reconciliation and file hashes pass.
11. **Determinism gate:** importing and normalizing the same snapshot twice produces the same version set and research tables.
12. **Scale gate:** projected storage, file count, memory, and run time are acceptable for the full corpus.

---

# Final assessment

The update successfully resolves many of the original serializer defects and shows good engineering direction. In particular, the top-level `timeframe` correction, enjoyment-scale fix, conservative flow naming, aligned finite trace parsing, QC block, atomic shard writes, latest-view concept, Bronze concept, and run manifests materially improve the usefulness of harvested data.

The remaining risk has moved from basic parsing to **corpus correctness**:

- Are all authorized records actually reachable?
- Can an interruption omit unseen records?
- Can two source versions be distinguished unambiguously?
- Can every failed record be repaired offline?
- Does the normalized population represent every integration rather than only chart-data sources?
- Can the exact snapshot used by a model or paper be reconstructed and verified?

At present, the answers are not yet strong enough for a canonical corpus claim.

**Recommendation:** use the updated code for a bounded pilot and continue development, but do not start the definitive full-corpus acquisition until the P0 issues are fixed. The best path is a maintainer-generated, versioned static export, imported through a content-addressed acquisition layer with exact reconciliation. That approach bypasses the ordinary API's scope and moving-pagination limitations while preserving the strong normalization improvements already made.
