# Repository review: corpus-harvest readiness

## Verdict

**The serializer correction is successful, but I would not begin the canonical full-corpus harvest with the current `main` branches.**

The revised Puckworks normalizer now reads Visualizer’s top-level `timeframe` correctly, retains backward compatibility with the earlier nested representation, and handles the current response shape. I also exercised that path locally with a live-style response, and the trace timestamps were normalized correctly. ([Puckworks harvester source](https://github.com/trbrewer/puckworks/raw/refs/heads/main/puckworks/lib/visualizer_harvest.py))

However, the current system has several blockers that could make a completed harvest:

- historically incomplete;
- non-idempotent after incremental updates;
- vulnerable to permanent omissions after an interrupted run;
- unable to repair future normalization mistakes because the original API payloads are discarded;
- incorrect for some important outcome and flow fields.

**Readiness assessment:**

- **Bounded engineering pilot:** Yes, after the first-run directory fix.
- **Recent-public-shot exploratory dataset:** Yes, with prominent limitations.
- **Canonical historical corpus:** No.
- **Dataset suitable for defensible modeling, validation, or papers:** Not yet.

---

## What is now working well

The top-level serializer mismatch identified previously has been corrected. The current code reads `timeframe` from the response root and falls back to `data.timeframe`, so both the current Visualizer response and older fixtures can be processed. The regression test is a meaningful improvement rather than merely a fixture update. ([Puckworks harvester source](https://github.com/trbrewer/puckworks/raw/refs/heads/main/puckworks/lib/visualizer_harvest.py))

Several other design choices remain strong foundations:

- Hydraulic traces and user-entered outcome fields remain distinguishable rather than being presented as equally controlled measurements.
- Units and ambiguity flags are represented explicitly.
- User IDs are transformed with a salted hash, permitting repeated-user analyses without retaining direct account identifiers.
- Gzip JSONL sharding and generator-based readers avoid loading the complete corpus into memory.
- The crawler includes rate limiting, retry behavior, checkpoint concepts, and a testable transport layer.
- Raw corpus files are excluded from the public repository, consistent with the stated redistribution posture.

Those are good building blocks. The problems below are concentrated in access scope, incremental correctness, fidelity, and scientific semantics.

---

# Blocking findings

## 1. The current API path cannot enumerate the historical public corpus

This is the most important finding.

For an unauthenticated request, Visualizer begins with visible/public shots, but then applies its `non_premium` scope. That scope is defined as shots created within the past month. For an authenticated request, the API selects `Current.user.shots`, meaning the caller’s own shots rather than every visible shot. The `updated_after` filter is also only applied when there is a current authenticated user. ([Visualizer shots controller](https://github.com/miharekar/visualizer/blob/main/app/controllers/api/shots_controller.rb))

Consequently:

- an unauthenticated Puckworks harvest sees only the recent public window;
- a normal authenticated harvest sees the authenticated account’s shots;
- premium authentication may expand the account’s own history, but it does not convert the API into a corpus-wide public listing;
- the permission grant alone does not alter these controller queries.

Unless the permission includes a separate endpoint, token scope, database export, or server-side dump that is not present on the reviewed `main` branch, the current harvester cannot discover all historical IDs.

### Required resolution

The Visualizer side needs one of these:

1. **A server-generated bulk export**, preferably compressed NDJSON or Parquet; or
2. **A corpus-scoped API endpoint**, such as:

```text
GET /api/corpus/shots?cursor=<opaque_cursor>&items=1000
Authorization: Bearer <corpus-read-token>
```

That endpoint should explicitly select all permitted `Shot.visible` records, bypass the one-month scope under the special authorization, and not substitute `Current.user.shots`.

A server-side export is preferable. Visualizer describes its collection as containing millions of shots, while the Puckworks crawler currently makes approximately one detail request per shot plus one listing request per 100 shots. At the default 18 requests per minute, one million records would take about 39 continuous days before accounting for retries, interruptions, reconciliation, or service-side load. Multiple millions would take months. ([Puckworks harvester source](https://github.com/trbrewer/puckworks/raw/refs/heads/main/puckworks/lib/visualizer_harvest.py))

The permission should therefore be implemented as a **bulk-transfer mechanism**, not merely permission to exercise the ordinary public API for a very long time.

---

## 2. A fresh harvest can fail before writing its first record

At the start of `_crawl`, the harvester calls:

```python
shutil.disk_usage(cfg.out_dir)
```

before ensuring that `cfg.out_dir` exists. On a fresh clone or a new destination, this raises `FileNotFoundError`.

I reproduced this locally using a nonexistent output path.

### Fix

Create the destination before the first disk-space check:

```python
cfg.out_dir.mkdir(parents=True, exist_ok=True)
usage = shutil.disk_usage(cfg.out_dir)
```

Alternatively, check the nearest existing parent, but creating the intended directory is simpler and makes the later write path deterministic.

Add a regression test that runs a one-record crawl with an entirely nonexistent temporary output directory. The current tests exercise crawl and resume behavior but do not cover this first-run condition. ([Puckworks harvester source](https://github.com/trbrewer/puckworks/raw/refs/heads/main/puckworks/lib/visualizer_harvest.py))

---

## 3. Current “incremental” mode is not corpus-wide incremental mode

Puckworks supplies `updated_after` during incremental listing. Visualizer explicitly ignores that parameter for unauthenticated requests, and ordinary authenticated requests cover only the authenticated user’s records. ([Visualizer OpenAPI schema](https://github.com/miharekar/visualizer/raw/refs/heads/main/openapi.yaml))

Therefore, against the ordinary public API, an incremental run will continue paging through the recent public feed rather than requesting only corpus records changed since the checkpoint.

This becomes a data-integrity problem because the current harvester can append records whose IDs are already present. The standard Puckworks iterator then yields every stored record, and `visualizer_index()` uses index rows as its shot count. There is no canonical “latest version per shot” layer in the loader. ([Puckworks harvester source](https://github.com/trbrewer/puckworks/raw/refs/heads/main/puckworks/lib/visualizer_harvest.py))

I reproduced this locally:

1. A simulated full run stored one shot.
2. A simulated incremental run returned the same shot.
3. The incremental run reported no newly discovered ID but appended the record.
4. The store and index then contained two records for the same shot.
5. Existing readers treated both as observations.

This would bias:

- shot counts;
- device and profile distributions;
- train/test datasets;
- aggregate trace statistics;
- outcome analyses;
- any model that does not explicitly deduplicate first.

### Required design

Separate these concepts:

```text
versions/
    append-only record versions

latest/
    exactly one current record per shot ID

tombstones/
    records known to have been deleted, privatized, or made unavailable
```

Use a version identity such as:

```text
(shot_id, visualizer_updated_at, content_hash)
```

The analytic loader should default to `latest`, not to every historical version. Version-history analysis should require an explicit separate loader.

---

## 4. An interrupted incremental run can permanently skip unseen updates

The current listing is sorted newest-first by `updated_at`. During an incremental run, the harvester tracks the maximum update timestamp encountered and may save that maximum even when the run is incomplete.

That creates a classic high-water-mark error.

For example:

```text
previous cursor: 100
eligible records, descending: 200, 199
```

Suppose the harvester durably stores record `200` and is interrupted before storing `199`. If it saves `200` as the new cursor, the next strict `updated_after=200` request will never return `199`.

I reproduced the equivalent condition locally using the current interruption/request-limit path.

The API also reports update timestamps at integer-second precision and orders only by `updated_at`, without a documented secondary ordering key. Several records can therefore share the same timestamp. A strict timestamp-only cursor cannot safely distinguish how much of that timestamp group has been consumed. ([Visualizer shots controller](https://github.com/miharekar/visualizer/blob/main/app/controllers/api/shots_controller.rb))

### Preferred fix

Use an opaque server cursor backed by deterministic keyset ordering:

```sql
ORDER BY updated_at ASC, id ASC
```

The cursor should encode both:

```text
(updated_at, id)
```

The client advances it only after the corresponding detail record has been written durably.

### Acceptable temporary fix

Until the endpoint supports that:

- never advance the durable high-water mark when `completed == false`;
- retain a separate provisional run checkpoint;
- overlap the next query by several seconds;
- deduplicate by `(id, updated_at, content_hash)`;
- process every same-second timestamp group completely before advancing.

The overlap approach reduces risk but is not as reliable as a deterministic compound cursor.

---

## 5. The directory called `raw` does not contain raw Visualizer records

The Puckworks crawler fetches a Visualizer detail response, immediately normalizes it into `TidyShot`, and stores only that normalized representation. The original JSON response is discarded. ([Puckworks harvester source](https://github.com/trbrewer/puckworks/raw/refs/heads/main/puckworks/lib/visualizer_harvest.py))

That is too risky for a one-time authorized corpus acquisition.

The raw response is needed because:

- the normalizer will continue to evolve;
- source-specific field semantics may later be clarified;
- valid fields are currently being lost or misinterpreted;
- records may later be deleted, privatized, or changed;
- new research questions may require context not selected by the current normalizer;
- auditability requires demonstrating what Visualizer actually returned.

The enjoyment-scale error described below is already a concrete example. A normalized-only corpus cannot be repaired after the fact without retrieving every affected record again.

### Recommended storage architecture

#### Bronze: protected immutable acquisition layer

Store the API result essentially as received:

```json
{
  "harvest_schema_version": 1,
  "run_id": "...",
  "harvested_at": "...",
  "endpoint": "...",
  "list_summary": { "...": "..." },
  "http_status": 200,
  "visualizer_updated_at": 1234567890,
  "content_sha256": "...",
  "payload": { "...original Visualizer detail response..." }
}
```

Bronze should be encrypted or access-controlled and should not be committed publicly.

#### Silver: normalized research layer

Include:

- stable shot ID;
- version identity;
- hashed user ID;
- integration/parser source;
- start time or an approved time bucket;
- normalized traces;
- original/native trace names and units;
- user-entered outcomes;
- context fields;
- QC flags;
- normalizer version.

#### Gold: analysis products

Include:

- latest-shot table;
- trace feature table;
- source-specific calibration subsets;
- validation cohorts;
- outcome-ready subsets;
- coverage and missingness summaries;
- privacy-reviewed public aggregates.

The existing `raw/` directory should either become genuinely raw or be renamed `normalized/`.

---

## 6. Valid enjoyment values are currently discarded

Visualizer treats the individual tasting-assessment dimensions as values from 0 through 15. `espresso_enjoyment`, however, is entered on a 0-through-100 scale. ([Visualizer shot model](https://github.com/miharekar/visualizer/blob/main/app/models/shot.rb))

The Puckworks normalizer currently includes `espresso_enjoyment` in the collection of sensory integers validated against 0 through 15. A valid value such as `82` is therefore replaced with `None` and marked out of range. The repository’s fuller fixture itself contains an enjoyment value of 82, illustrating the expected scale. ([Puckworks harvester source](https://github.com/trbrewer/puckworks/raw/refs/heads/main/puckworks/lib/visualizer_harvest.py))

I confirmed this behavior locally.

### Fix

Use separate definitions:

```python
TASTING_FIELDS_0_15 = {
    "espresso_acidity",
    "espresso_bitterness",
    "espresso_sweetness",
    "espresso_body",
    "espresso_aftertaste",
    # other Visualizer tasting dimensions
}

OUTCOME_FIELDS_0_100 = {
    "espresso_enjoyment",
}
```

Give the normalized columns scale-explicit names:

```text
espresso_enjoyment__score_0_100
espresso_acidity__score_0_15
espresso_bitterness__score_0_15
```

Add tests for:

- enjoyment: `0`, `15`, `16`, `82`, `100`, `101`;
- tasting dimensions: `0`, `15`, `16`;
- numeric strings as well as numeric values.

This correction is essential before using the corpus for sensory, preference, or extraction-outcome work.

---

## 7. Integration source and machine identity will be missing for many records

Visualizer supports data originating from several ecosystems, including Decent, Meticulous, Beanconqueror, Gaggiuino, GaggiMate, Smart Espresso Profiler, Pressensor, and others. ([Visualizer repository](https://github.com/miharekar/visualizer))

The Visualizer model knows the parser/integration source internally, but the current detail serializer does not reliably expose it as a stable documented field. For chart-data records, the response is principally top-level `timeframe` plus `data`; it is not necessarily accompanied by the nested `brewdata` structure from which Puckworks attempts to infer the source or machine. ([Visualizer JSON serializer](https://github.com/miharekar/visualizer/blob/main/app/models/shot/jsonable.rb))

This matters scientifically, not just descriptively. Different integrations may differ in:

- channel definitions;
- nominal units;
- sampling cadence;
- filtering and smoothing;
- flow estimation;
- pressure and temperature sensor placement;
- profile naming;
- availability of weight-derived flow;
- firmware-era behavior.

Without a source field, these differences become unexplained heterogeneity inside the modeling data.

### Visualizer-side fix

Emit a stable field such as:

```json
{
  "integration_source": "decent_tcl",
  "integration_schema_version": 1
}
```

The value should be a controlled enum based on the actual parser or import adapter, not a title guessed from free text.

Machine model can remain a separate, optional field:

```json
{
  "integration_source": "gaggiuino",
  "machine_make": "Gaggia",
  "machine_model": "Classic Pro"
}
```

Puckworks should preserve `integration_source` exactly and use inference only as a clearly marked fallback.

---

## 8. `espresso_flow` is represented as mass flow despite acknowledged ambiguity

The normalizer stores Visualizer’s `espresso_flow` in a field named like `flow__kg_per_s`, while also setting a flag indicating that the channel may represent volumetric rather than mass flow. ([Puckworks harvester source](https://github.com/trbrewer/puckworks/raw/refs/heads/main/puckworks/lib/visualizer_harvest.py))

A warning flag does not make the column name scientifically safe. Downstream code will naturally interpret a `kg_per_s` field as SI mass flow, and the ambiguity can silently enter feature engineering, conservation calculations, and model validation.

### Fix

Preserve the native channel separately:

```text
flow_reported__native
flow_reported__source_unit
flow_reported__semantic
```

Only populate:

```text
mass_flow__kg_per_s
```

when the source contract confirms that the channel is mass flow and the conversion is known.

Similarly, a separately supplied weight-derived flow channel should have its own explicit provenance:

```text
mass_flow_from_scale__kg_per_s
```

Do not combine pump/model-estimated flow and scale-derived flow into the same variable without recording the method.

---

## 9. Trace parsing is not robust enough for corpus-scale heterogeneity

The Visualizer API schema permits series elements that may be numbers, strings, booleans, or null values. The current Puckworks path applies direct numeric conversion to trace elements. ([Visualizer OpenAPI schema](https://github.com/miharekar/visualizer/raw/refs/heads/main/openapi.yaml))

At corpus scale, this can produce several undesirable outcomes:

- `null` or malformed values can cause an entire shot to be skipped;
- Python booleans can become `1.0` or `0.0`, creating false measurements;
- `NaN` and infinity can enter output unless explicitly rejected;
- array-length mismatches can destroy time/channel alignment;
- nonmonotonic timestamps can pass through;
- implausible channel values are not systematically quarantined;
- a skipped shot is counted but its ID and rejection reason are not preserved in a durable failure ledger.

### Required behavior

Use a per-element parser that distinguishes:

```text
valid finite numeric
missing
boolean
non-numeric string
non-finite numeric
```

Preserve array alignment with null values rather than deleting bad positions. Then calculate channel-level QC:

- original length;
- valid count;
- missing fraction;
- non-finite count;
- minimum and maximum;
- timestamp monotonicity;
- median and dispersion of sample interval;
- duplicate timestamps;
- fraction outside plausible source-specific ranges;
- length difference relative to `timeframe`.

Serialize with:

```python
json.dumps(record, allow_nan=False)
```

A malformed record should enter a quarantine ledger containing:

```text
shot_id
updated_at
run_id
failure_stage
exception_type
reason
retry_count
raw content hash
```

A single malformed record, 404, or disappearing public shot should not terminate the complete crawl.

---

## 10. Important temporal and provenance information is being discarded

Visualizer exposes shot timing information in its list/detail representations, but Puckworks does not retain enough of it in the normalized record. ([Visualizer shots controller](https://github.com/miharekar/visualizer/blob/main/app/controllers/api/shots_controller.rb))

Start time is valuable for:

- chronological train/test splits;
- detecting firmware or parser-era changes;
- measuring corpus growth and selection effects;
- avoiding leakage from repeated users;
- evaluating seasonality and behavior changes;
- distinguishing retrospective edits from newly uploaded shots.

For privacy, a protected Bronze layer can keep the full timestamp while Silver exposes only an approved day, week, or month bucket.

Every completed run should also write a manifest with:

```yaml
run_id:
started_at:
completed_at:
completed:
visualizer_commit:
puckworks_commit:
api_schema_version:
normalizer_version:
access_scope:
snapshot_or_watermark:
cursor_in:
cursor_out:
configuration:
listed_records:
unique_ids_listed:
details_requested:
details_received:
versions_written:
latest_records:
unchanged_records:
quarantined_records:
tombstoned_records:
retry_counts:
shard_checksums:
index_checksum:
user_hash_salt_fingerprint:
```

Without this, it will be difficult to state precisely which corpus state underlies a paper or model.

---

# Pagination and snapshot consistency

The current API uses offset-style pages over a collection that can change while a harvest runs. Sorting by `updated_at` without a secondary key permits records to shift between pages while new records or edits are occurring. Rewinding a few pages on resume reduces the probability of omissions but does not establish completeness.

For a crawl that could last days or weeks, “everything observed during the crawl” is not the same as a coherent snapshot.

A corpus endpoint or export should provide one of:

### Snapshot export

```text
snapshot_at = 2026-07-15T...
all rows selected consistently as of snapshot_at
```

### Watermarked traversal

```text
crawl records with updated_at <= crawl_start_watermark
then execute a catch-up pass for later updates
```

### Database/export transaction

Generate the complete export against a consistent database snapshot and attach the snapshot timestamp and source commit/schema version.

For research use, this is far better than treating a long-running moving crawl as though it were a single frozen population.

---

# Atomicity and recoverability

The current shard and index operations should also be hardened before a long harvest.

Recommended write sequence:

1. Write a shard to a temporary file.
2. Flush and `fsync`.
3. Calculate and store its checksum.
4. Rename atomically to the final shard path.
5. Update or rebuild the index from committed shards.
6. Commit the crawl checkpoint only after those operations succeed.

The index should be treated as rebuildable metadata, not the sole source of record identity. A reconciliation command should verify:

```text
shard files readable
checksums valid
record counts match manifests
every index row points to a real record
every real record appears in the index
no duplicate version keys
exactly one latest record per live shot
quarantine and tombstone counts reconcile
```

This matters for a harvest that may run for a substantial period and accumulate many shards.

---

# What a harvest run today would actually produce

Assuming the output-directory issue is fixed, the ordinary public endpoint would produce a useful but sharply bounded dataset.

### It would be useful for

- testing the Puckworks ingestion pipeline;
- inspecting current Visualizer response shapes;
- developing trace QC;
- exploring a recent public-shot cohort;
- testing feature extraction;
- estimating missingness and channel coverage;
- building preliminary visualizations;
- selecting source-specific examples for manual review.

### It would not yet support defensible claims about

- the complete historical Visualizer corpus;
- long-term trends;
- historical profile adoption;
- population-level machine comparisons;
- complete user-level longitudinal behavior;
- source-stratified models, while source identity is missing;
- sensory preference, while valid enjoyment values are discarded;
- hydraulic models that treat ambiguous flow as mass flow;
- reproducible corpus statistics after incremental duplicate accumulation;
- a fixed corpus snapshot suitable for a publication.

So the current output would be **engineering-useful**, but it should not be labeled the Visualizer corpus.

---

# Minimum acceptance gates before a canonical harvest

## Gate 1: corpus access

Pass only when:

- a known public shot older than one month appears in the corpus listing;
- authentication returns corpus-visible shots from users other than the authenticated account;
- the authorization scope is explicitly documented;
- a server-provided count or export manifest gives an expected record total;
- the transfer mechanism is practical for the expected corpus size.

## Gate 2: fresh-run reliability

Pass only when:

- a crawl succeeds with no pre-created directories;
- empty, partial, and existing destinations are all tested;
- disk-space checks occur against an existing path;
- interrupted writes leave no valid-looking partial shard.

## Gate 3: deterministic enumeration

Pass only when:

- ordering is deterministic using at least `(updated_at, id)`;
- same-second timestamp ties are tested;
- an interrupted run resumes without omissions;
- cursor advancement follows durable writes;
- a completed rerun against an unchanged source yields no new versions.

## Gate 4: raw fidelity

Pass only when:

- the original permitted detail payload is retained in protected Bronze storage;
- every raw record has a content hash;
- the raw response can be re-normalized without network access;
- schema and source versions are recorded;
- storage and publication policies are documented separately.

## Gate 5: semantic correctness

Pass only when:

- enjoyment accepts 0–100;
- tasting dimensions accept 0–15;
- flow channels are not labeled mass flow without confirmed semantics;
- source/parser is present or explicitly missing;
- time units and channel units are source-tested;
- start time and update time are retained at an approved privacy level.

## Gate 6: source fixture matrix

Create fixtures from actual, permission-approved responses for at least:

- Decent;
- Meticulous;
- Beanconqueror;
- Gaggiuino;
- GaggiMate;
- Smart Espresso Profiler;
- Pressensor;
- any additional parser with meaningful corpus representation.

Each fixture should test trace extraction, source identity, units, optional outcomes, nulls, and expected metadata. Visualizer’s current integrations are heterogeneous enough that a generic Decent-shaped fixture is not sufficient coverage. ([Visualizer repository](https://github.com/miharekar/visualizer))

## Gate 7: malformed-data matrix

Tests should include:

- number and numeric-string values;
- nulls;
- booleans;
- empty strings;
- `NaN` and infinity;
- unequal channel lengths;
- empty timeframe;
- nonmonotonic timeframe;
- duplicated timestamps;
- one malformed channel among otherwise valid channels;
- 404 between list and detail retrieval;
- 429 and temporary 5xx responses.

The result should be either a valid normalized record with QC flags or an identifiable quarantine record—never a silent skip.

## Gate 8: version and deletion behavior

Test:

1. Initial shot version.
2. Edited shot with the same ID.
3. Repeated unchanged retrieval.
4. Shot becoming private or returning 404.
5. Shot becoming visible again.
6. Same `updated_at` but changed content.
7. Duplicate detail response within one run.

The latest view must contain one record per live shot, while version history remains auditable.

## Gate 9: bounded pilot

Before the full acquisition, run a pilot of approximately 1,000–10,000 records or a server-defined bounded slice.

The pilot report should include:

- listed IDs versus fetched IDs;
- unique records versus versions;
- success, retry, quarantine, and disappearance rates;
- source distribution;
- source missingness;
- trace-channel coverage;
- sample-count and duration distributions;
- timestamp quality;
- missingness by field;
- outcome value distributions;
- invalid and out-of-range values;
- raw-to-normalized spot checks for a random sample;
- shard and manifest reconciliation.

Manually compare at least several dozen Bronze records against Silver records, stratified by source rather than drawing only a simple random sample dominated by the largest integration.

---

# Recommended implementation sequence

1. **Establish an actual corpus-wide export or corpus-scoped endpoint.**
2. **Fix fresh-directory creation.**
3. **Add immutable Bronze storage and run manifests.**
4. **Replace timestamp-only/descending resume logic with deterministic keyset or snapshot semantics.**
5. **Separate version history from the latest analytic view.**
6. **Correct enjoyment scaling and flow semantics.**
7. **Expose and preserve integration/parser source.**
8. **Add robust trace parsing, QC, and a quarantine ledger.**
9. **Retain approved temporal and contextual fields.**
10. **Run the bounded pilot and reconcile counts.**
11. **Only then begin the canonical acquisition.**
12. **Generate Silver and Gold datasets from the preserved Bronze snapshot rather than during network retrieval.**

---

## Bottom line

The serializer update resolved the original `timeframe` defect, and the Puckworks harvester remains a promising foundation. The current code will now parse more real Visualizer traces than before.

But the **largest problem is no longer serialization**. It is that the reviewed API route does not expose the historical public corpus, ordinary incremental filtering is not available for that corpus, and the client’s current version/cursor behavior can duplicate or omit records. The normalized-only storage would then make those defects difficult or impossible to repair after acquisition.

I would treat the present implementation as ready for a **small recent-data engineering pilot**, not for the authorized canonical harvest. The canonical run should begin only after corpus-wide access, immutable raw retention, deterministic resume semantics, outcome/unit corrections, and latest-version reconciliation all pass the gates above.
