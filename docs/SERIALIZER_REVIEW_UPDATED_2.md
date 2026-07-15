# SERIALIZER_REVIEW_UPDATED_2

**Updated Visualizer serializer / Puckworks corpus-harvester review — round 2**  
**Review date:** 2026-07-15  
**Repositories reviewed:**

- [miharekar/visualizer](https://github.com/miharekar/visualizer), especially:
  - [`app/models/shot/jsonable.rb`](https://github.com/miharekar/visualizer/blob/main/app/models/shot/jsonable.rb)
  - [`app/controllers/api/shots_controller.rb`](https://github.com/miharekar/visualizer/blob/main/app/controllers/api/shots_controller.rb)
  - [`app/models/shot.rb`](https://github.com/miharekar/visualizer/blob/main/app/models/shot.rb)
  - [`openapi.yaml`](https://github.com/miharekar/visualizer/blob/main/openapi.yaml)
- [trbrewer/puckworks](https://github.com/trbrewer/puckworks), especially:
  - [`puckworks/lib/visualizer_harvest.py`](https://github.com/trbrewer/puckworks/blob/main/puckworks/lib/visualizer_harvest.py)
  - [`tests/test_visualizer_harvest.py`](https://github.com/trbrewer/puckworks/blob/main/tests/test_visualizer_harvest.py)
  - [`puckworks/data/visualizer/PROVENANCE.md`](https://github.com/trbrewer/puckworks/blob/main/puckworks/data/visualizer/PROVENANCE.md)
  - [`docs/cards/visualizer_coffee.md`](https://github.com/trbrewer/puckworks/blob/main/docs/cards/visualizer_coffee.md)

---

## Executive verdict

The revised Puckworks serializer/harvester is **materially better than the versions reviewed previously**. The current code correctly handles Visualizer's top-level `timeframe`, validates the separate 0–100 enjoyment scale, keeps ambiguous reported flow out of SI mass-flow fields, parses malformed numeric trace samples without destroying alignment, writes individual gzip shards atomically, retains a privacy-filtered Bronze layer, records quarantined payloads, preserves version history, exposes a latest-version view, and avoids committing an incremental high-water mark when a run stops early.

The repository's current offline test suite passed in full:

```text
41 passed, 1 warning in 0.49s
```

I also ran additional adversarial tests against the exact reviewed source. Those tests reproduced several integrity and governance failures that are not covered by the repository suite.

### Overall readiness

| Intended use | Assessment |
|---|---|
| Normalizer development with synthetic fixtures | **Ready** |
| Small, recent-public-shot engineering pilot | **Ready with safeguards** |
| Ingest of a maintainer-provided, immutable corpus snapshot | **Conditionally ready after the P0/P1 fixes below** |
| Full historical corpus via the ordinary documented API | **Not possible with the reviewed API path** |
| Long-running moving API crawl claimed as a complete snapshot | **Not ready** |
| Defensible model-development or publication dataset | **Not yet** |
| Public redistribution of per-shot data | **Not authorized by the reviewed provenance posture** |

### Most important conclusion

The principal risk is no longer the original `timeframe` serializer mismatch. It is now the **acquisition contract around the serializer**:

1. The ordinary API still does not enumerate the full historical public corpus.
2. Offset pagination over a changing collection does not produce a provably complete snapshot.
3. Same-second edits can still be skipped before their content hash is observed.
4. normalized shards, Bronze shards, and the CSV index do not commit as one transaction.
5. deleted, privatized, unavailable, or list/detail-inconsistent records are not modeled safely.
6. `brewdata`-only records still produce no normalized telemetry.
7. the privacy-filtered Bronze contract is implemented with a narrow denylist rather than an enforceable allowlist.
8. the offline re-normalizer is not idempotent when pointed at an existing destination.

**Recommendation:** do not start a canonical full-corpus run through the current ordinary API crawler. Obtain a maintainer-generated snapshot or a dedicated corpus endpoint, apply the acquisition-integrity fixes in this review, complete a bounded pilot, and then create the canonical Bronze/Silver/Gold datasets from a fixed source snapshot.

---

## 1. Scope and review method

This review covered both sides of the data boundary:

1. **Visualizer source behavior**
   - Which records `/api/shots` can enumerate.
   - How Premium and authentication affect that enumeration.
   - How shot details are serialized.
   - The two possible information shapes: top-level `timeframe` + `data`, or `brewdata`.
   - Timestamp precision, ordering, and API rate limits.

2. **Puckworks acquisition and normalization**
   - Listing, detail fetching, resume behavior, incremental behavior, and rate limiting.
   - Trace parsing, unit conversion, outcomes, context, and QC.
   - Bronze, normalized shards, index, quarantine, run manifests, and reconciliation.
   - version selection, offline re-normalization, and analytic loaders.
   - privacy transformations and provenance claims.

3. **Executable verification**
   - The exact reviewed Puckworks harvester was downloaded from `main`.
   - SHA-256 of `visualizer_harvest.py`:

     ```text
     13746fb1a1fc0a83a2c4df7100b2401adf01ff3a31a1bf0ce02cb215225ba5a0
     ```

   - SHA-256 of `tests/test_visualizer_harvest.py`:

     ```text
     544d532b3984ae6835ffbbc3f970844e2196c2c92cc45b1241b13a427c5b785c
     ```

   - The repository test module and its three synthetic Visualizer fixtures were run offline.
   - Additional synthetic adversarial tests exercised gaps not represented in the repository suite.

No live corpus was downloaded for this review. Findings about corpus composition must therefore be validated quantitatively during the proposed pilot.

---

## 2. Improvements confirmed since the preceding review

The current revision resolves or substantially improves many earlier findings.

### 2.1 Top-level `timeframe` is handled correctly

Visualizer's native serializer emits chart records as:

```json
{
  "timeframe": [...],
  "data": {
    "espresso_pressure": [...]
  }
}
```

The normalizer now reads top-level `timeframe` first and falls back to legacy `data.timeframe`. This prevents valid live traces from being converted into zero-sample records merely because the time base was sought in the wrong object.

**Status:** resolved and regression-tested.

### 2.2 Fresh output directories are created before disk checks

The crawler now creates `out_dir` before calling `shutil.disk_usage`, eliminating the fresh-run `FileNotFoundError` identified earlier.

**Status:** resolved and regression-tested.

### 2.3 Enjoyment and tasting scales are separated

The code now distinguishes:

- tasting dimensions: `0..15`;
- `espresso_enjoyment`: `0..100`.

A valid enjoyment value such as 82 is retained instead of being nulled as out of range.

**Status:** resolved and regression-tested.

### 2.4 Ambiguous flow is no longer mislabeled as SI mass flow

`espresso_flow` and `espresso_flow_goal` are preserved as native reported/estimated values with explicit ambiguity semantics. Only `espresso_flow_weight` is converted to `mass_flow_from_scale__kg_per_s`.

This is a substantial scientific improvement because downstream code can no longer mistake an integration-specific flow proxy for a confirmed mass-flow measurement simply because the column name says `kg_per_s`.

**Status:** resolved for the normalized field names. Source-side unit provenance is still needed; see P1-06.

### 2.5 Trace parsing preserves alignment

Numeric strings are parsed where possible. Nulls remain null. Booleans, nonnumeric strings, NaN, and infinity become `None` in place rather than becoming false measurements or dropping the whole shot. Channel QC now records validity, missingness, length agreement, and flatline status. Time QC records missing timestamps, monotonicity, duplicates, and sample-interval summaries.

**Status:** substantially improved. Physical and cross-channel QC remain incomplete; see P1-07.

### 2.6 Individual gzip shard writes are atomic

A shard is written to a temporary file, flushed, `fsync`ed, and then moved into place with `os.replace`. This prevents a process interruption during gzip creation from leaving a torn file under the final shard name.

**Status:** resolved at the individual-file level. The normalized/Bronze/index set is not transactional; see P0-04.

### 2.7 Version history and latest-version selection are explicit

The normalized record receives a content hash. The append-only index includes `(id, updated_at, content_sha256)`, and the latest reader collapses version history to one row per shot. Reconciliation now compares content-addressed version multisets rather than only ID sets.

**Status:** substantially improved. Acquisition can still skip a changed same-second version before computing its hash; see P0-03.

### 2.8 Interrupted incremental runs do not advance the durable cursor

The durable cursor advances only when the listing loop exhausts normally. This fixes the previously reproduced newest-first high-water-mark omission in which a run stored update 200, stopped before update 199, then permanently advanced past 199.

**Status:** resolved for that specific failure. The ordinary public API ignores `updated_after`, timestamps are second-resolution, and the listing is not a deterministic snapshot; see P0-01 through P0-03.

### 2.9 Bronze and quarantine payloads are retained

The harvester now stores a privacy-filtered source payload in Bronze and includes a filtered payload in quarantine records. This allows many normalizer defects to be corrected offline after a shot leaves the public listing window.

**Status:** strong improvement. Bronze completeness, privacy, transactionality, and re-normalization safety remain incomplete; see P0-04, P1-01, P1-02, and P1-03.

### 2.10 Exact brew time, run IDs, and manifests were added

`start_time` is retained separately from `updated_at`, run IDs use nanoseconds plus random bytes, and a per-run JSON manifest is written.

**Status:** strong improvement. The manifest currently lacks several elements needed for publication-grade provenance, and its Git commit may be taken from the caller's working directory; see P1-04.

---

## 3. Readiness matrix by subsystem

| Subsystem | Current status | Corpus implication |
|---|---|---|
| Visualizer chart serialization | Good | `timeframe` + `data` can be normalized |
| Visualizer non-chart serialization | Unsupported by current normalizer | `brewdata`-only records lose normalized telemetry |
| Full-corpus enumeration | Blocked | ordinary API cannot discover the historical public corpus |
| Moving-feed pagination | Non-deterministic | completion does not prove snapshot completeness |
| Detail normalization | Much improved | good foundation for chart-data records |
| Source/integration provenance | Partial/inferred | cross-integration heterogeneity remains confounded |
| Same-second version detection | Incomplete | changed content can be silently skipped |
| Individual shard durability | Good | final shard files are not torn |
| Multi-artifact commit | Incomplete | shard/Bronze/index can disagree after a crash |
| Bronze recoverability | Partial | filtered source payload retained, but not fully governed or reconciled |
| Privacy filtering | Partial | known exact keys removed recursively; unknown free text and URLs remain |
| Offline re-normalization | Unsafe on existing destination | repeated invocation can corrupt index/store consistency |
| Quarantine | Partial | normalization failures retained; detail-fetch failures stop the crawl and are not quarantined |
| Lifecycle/deletions | Missing | stale records remain “live” forever |
| Reconciliation | Partial | normalized shards/index checked, but Bronze and manifests are not verified |
| Analytic scalability | Not demonstrated | current latest/rebuild/reconcile paths use O(N) in-memory structures |
| Documentation | Stale in material places | current operational claims overstate scope, speed, and guarantees |

---

# 4. Blocking findings for a canonical corpus

## P0-01 — The ordinary API still cannot enumerate the full historical public corpus

**Evidence:** source review.

The current Visualizer API controller starts a shot listing from one of two relations:

```ruby
Current.user.present? ? Current.user.shots : Shot.visible
```

It then applies the `non_premium` scope unless the authenticated user is Premium. In the shot model, `non_premium` means records created within the last month. `updated_after` is applied only when a user is authenticated. The OpenAPI description says the same thing at a higher level:

- unauthenticated listing: public shots;
- authenticated listing: the authenticated user's shots;
- `updated_after`: authenticated requests only.

Therefore the reviewed possibilities are:

| Request mode | Enumerated records |
|---|---|
| unauthenticated | recent public window only |
| authenticated free | recent history of that account's own shots |
| authenticated Premium | all history of that account's own shots |
| corpus-wide historical public records | not exposed by the documented listing |

The Puckworks harvester does not implement authentication anyway, but adding a Premium token would not solve the corpus-listing issue: it would switch the listing to the token owner's shots.

### Consequence

A run can naturally exhaust the ordinary listing and set `completed=True` while having acquired only the current recent-public window. Calling that result the “full Visualizer corpus” would be materially false.

### Required resolution

Use one of these maintainer-provided mechanisms:

1. **Preferred: fixed bulk snapshot export**
   - compressed NDJSON or Parquet;
   - all records within the permission scope;
   - stable snapshot ID and generation timestamp;
   - expected record count;
   - source commit/schema version;
   - integration/parser source;
   - per-shard checksums;
   - persistent approved user pseudonym;
   - explicit visibility scope.

2. **Dedicated corpus API**
   - separate `corpus_read` authorization;
   - selects `Shot.visible` or the specifically approved scope;
   - no one-month restriction;
   - deterministic keyset cursor;
   - batch detail payloads;
   - record version/digest;
   - lifecycle/tombstone feed.

3. **Research-specific server-side export task**
   - functionally equivalent to option 1 but produced directly from the application/database.

### Additional operational reason

At the Puckworks default 18 detail requests per minute, one million details plus about 10,000 listing calls require roughly **39 continuous days** before retries or interruptions. Two million would require roughly **78 days**. The current provenance statement that the “full corpus is a multi-hour uninterrupted run” must be removed.

**Disposition:** hard blocker unless an unreviewed private snapshot/endpoint has already been supplied.

---

## P0-02 — Offset pagination over a moving collection cannot establish a complete snapshot

**Evidence:** source review and pagination reasoning.

The Puckworks full run uses page numbers and resumes near the prior page, rewinding three pages to absorb some movement. Visualizer orders the full listing by `start_time DESC`; the incremental listing uses `updated_at DESC`. Neither reviewed ordering has a documented secondary `id` key. The underlying population can receive new records and edits while a crawl runs.

Three problems follow.

### 1. Ties are not deterministically ordered

Many records can share the same integer-second `start_time` or `updated_at`. Without a secondary key, rows at a page boundary may move between requests.

### 2. Inserts, edits, deletions, and visibility changes shift offsets

A fixed three-page rewind only absorbs a bounded amount of movement. It is not a proof that no unharvested row moved before the resume page. A sufficiently large shift, or a long enough interruption, can create omissions.

### 3. “Listing exhausted” is not “snapshot complete”

A crawl can reach an empty last page while the collection has changed at earlier pages. The current summary calls this `completed=True`, but it only means the client exhausted the page sequence it observed.

### Required design

The source should provide one of:

#### Immutable snapshot

```text
snapshot_id = visualizer-public-2026-07-15T...
all exported rows are selected from one consistent snapshot
```

#### Deterministic keyset traversal

```sql
ORDER BY updated_at ASC, id ASC
```

with a cursor containing both values:

```json
{"updated_at_usec": 178..., "id": "..."}
```

The cursor must advance only after the corresponding record has been durably committed.

#### Watermarked crawl

Freeze a source watermark at crawl start, traverse only records at or below it, reconcile against an expected count, then run a separate catch-up pass.

### Client-side recommendation

Rename the current `completed` concept to `listing_exhausted` unless a source snapshot/count proves completeness. Record:

- access scope;
- snapshot/watermark;
- expected count;
- listed count;
- unique listed IDs;
- successfully committed IDs;
- unresolved IDs;
- lifecycle changes.

**Disposition:** hard blocker for any “complete corpus” or fixed-snapshot claim.

---

## P0-03 — Changed content with the same second-resolution `updated_at` is skipped before hashing

**Evidence:** reproduced offline.

The current code loads the latest stored timestamp per ID and performs this prefetch check:

```python
if have is not None and upd_i is not None and upd_i <= have:
    continue
```

Visualizer serializes `updated_at` to integer Unix seconds in both list and detail responses. The normalized content hash is computed only **after** a detail response is fetched and normalized. Therefore the hash cannot detect a change that the timestamp check prevents from being fetched.

### Reproduction

1. Harvest shot `A` with `updated_at=100` and pressure `[1, 1]`.
2. Change the source payload to pressure `[9, 9]` while retaining `updated_at=100`.
3. Run the full harvester again.

Observed result:

```json
{
  "run2_n_fetched": 0,
  "stored_versions": 1,
  "latest_pressure_Pa": 100000.0
}
```

The repository test that manually stores two same-timestamp versions confirms the latest reader can choose the last version **after both exist**. It does not test whether the crawler can discover the second version. It currently cannot.

### Why this also affects incremental cursors

A strict source filter equivalent to `updated_at > cursor` cannot discover a later edit whose serialized timestamp equals the cursor second. A content hash in the detail response does not repair a list filter that never returns the record.

### Required resolution

The best source contract is one of:

- `updated_at` with microsecond precision;
- a monotonic `record_version` or database `lock_version`;
- a source-generated content digest in the list response;
- immutable event/version IDs.

Then use:

```text
version identity = (shot_id, source_record_version)
```

or:

```text
version identity = (shot_id, updated_at_usec, source_payload_sha256)
```

A temporary client workaround could force re-fetching records in an overlapping time band, including equal timestamps, but it cannot prove complete same-second change detection for the whole historical corpus.

**Disposition:** hard blocker for exact version history and incremental correctness.

---

## P0-04 — Normalized shard, Bronze shard, and index do not commit as one transaction

**Evidence:** source review.

Each gzip shard is written atomically, but `flush()` performs three separate operations:

1. write normalized shard;
2. write Bronze shard;
3. append rows to `_index.csv`.

A crash can occur between any pair:

| Crash point | Possible state |
|---|---|
| after normalized shard | normalized exists; Bronze and index absent |
| after Bronze shard | normalized and Bronze exist; index absent |
| during index append | shards committed; index partial or missing rows |
| after index, before checkpoint | data committed; page/cursor state stale |

The CSV append is not `fsync`ed and is not atomically replaced in the normal append path. Reconciliation can detect some shard/index disagreements, but it does not make the multi-file commit atomic, does not validate Bronze parity, and does not automatically recover.

### Required design

Use a committed-shard manifest pattern:

1. Write normalized shard to a temporary path.
2. Write Bronze shard to a temporary path.
3. Write an index fragment to a temporary path.
4. Flush and `fsync` all three.
5. Calculate checksums and record counts.
6. Rename each into a versioned immutable path.
7. Atomically write a small **commit marker/manifest** naming the three files and checksums.
8. Readers consume only shard sets referenced by committed manifests.
9. Treat the global index as rebuildable from committed manifests.

A transactional store such as SQLite for metadata plus immutable compressed objects, or DuckDB/Parquet with committed manifests, would be safer at corpus scale.

### Required reconciliation extension

For every committed shard set verify:

```text
normalized count == Bronze count == index-fragment count
normalized IDs/versions match Bronze wrapper IDs/versions
all checksums match
all files named by the commit manifest exist
no uncommitted orphan is treated as live
```

**Disposition:** hard blocker for a long one-time acquisition that must survive abrupt interruption without manual forensic repair.

---

## P0-05 — Detail lifecycle failures stop the crawl and are not represented as tombstones or retries

**Evidence:** reproduced offline.

The crawler treats any exception during `fetch_shot` as a reason to stop the whole run. The failing ID is not added to quarantine because quarantine begins only after a detail payload has been received.

### Reproduction

The listing contained `A` and `B`. Fetching `A` raised a simulated `404 Not Found`; `B` was otherwise valid.

Observed result:

```json
{
  "completed": false,
  "n_fetched": 0,
  "stored_ids": [],
  "quarantine_count": 0,
  "stopped_early": "RuntimeError: 404 Not Found"
}
```

A real record can disappear between list and detail retrieval because it was deleted, made private, or otherwise became unavailable. That event should not prevent unrelated records from being acquired.

### Required behavior by status

| Status/condition | Recommended action |
|---|---|
| 404 / 410 after listing | record lifecycle event, continue, reconcile later |
| 403 | record authorization/visibility event, continue, flag scope issue |
| 429 | honor `Retry-After`, retry, then place in retry queue if unresolved |
| 5xx / network error | bounded retries, durable retry queue, do not mark snapshot complete while unresolved |
| malformed JSON | quarantine response metadata, continue |
| list/detail ID mismatch | quarantine integrity failure, continue without committing record |

### Tombstones and latest view

The current latest view treats every previously acquired shot as live forever. A canonical evolving corpus needs:

```text
tombstones/
    shot_id
    observed_at
    prior_version
    reason: deleted | private | unavailable | out_of_scope
```

For a fixed snapshot, lifecycle is simpler: record the snapshot scope once and do not pretend later API state changes alter that snapshot. For an evolving corpus, a complete re-list/reconciliation mechanism is required.

**Disposition:** hard blocker for unattended corpus acquisition and for an accurate current/latest view.

---

## P0-06 — `brewdata`-only responses still normalize to zero telemetry

**Evidence:** source review and reproduced offline.

Visualizer's serializer intentionally emits one of two information shapes:

```ruby
if information.chart_data?
  json[:timeframe] = information.timeframe
  json[:data] = information.data
else
  json[:brewdata] = information.brewdata
end
```

Puckworks reads telemetry only from `raw["data"]` plus top-level or nested `timeframe`. `brewdata` is consulted only for best-effort machine/source inference.

### Reproduction

A synthetic record containing only:

```json
{
  "brewdata": {
    "decent": {
      "timeframe": [0, 1],
      "pressure": [1, 9]
    }
  }
}
```

produced:

```json
{
  "n_samples": 0,
  "hydraulic": {},
  "flags": ["missing:timeframe"]
}
```

The exact content and usability of each `brewdata` integration will vary, so the fix should not assume the synthetic shape above. The key point is that the source serializer explicitly emits non-chart records while the current normalized telemetry path has no adapter for them.

### Required resolution

1. Add an explicit source-shape field:

   ```text
   information_shape = chart_data | brewdata_only | no_information
   ```

2. Preserve `brewdata` in the restricted Bronze layer.
3. Create source-specific adapters only where semantics are documented and tested.
4. Never silently classify `brewdata`-only as an ordinary empty hydraulic trace.
5. During the pilot, quantify:
   - percentage chart-data;
   - percentage brewdata-only;
   - integration mix within each;
   - recoverable channels by adapter;
   - records that are context-only.
6. Add real, permission-approved fixtures for every materially represented integration.

**Disposition:** hard blocker if the corpus is intended to cover all integrations rather than only chart-data records.

---

# 5. High-priority findings

## P1-01 — The offline Bronze re-normalizer is not idempotent and can corrupt an existing destination

**Evidence:** reproduced offline.

`renormalize_from_bronze` always begins at normalized `shard_idx=0`. It does not require an empty destination and appends to any existing `_index.csv`.

### Reproduction

A two-record Bronze source was re-normalized twice into the same destination.

After the second run:

```json
{
  "shard_records": 2,
  "index_rows": 4,
  "reconcile": {
    "ok": false,
    "problems": ["index_versions_not_in_shards:2"]
  }
}
```

The second run overwrote `shard_00000.jsonl.gz` but appended duplicate index rows.

### Required fix

Default behavior should require an empty, nonexistent destination:

```python
if dst.exists() and any(dst.iterdir()):
    raise RuntimeError("destination must be empty; use --replace or a new version directory")
```

Prefer a versioned output:

```text
silver/schema_v006/<source_snapshot_id>/
```

Write to a temporary directory, reconcile fully, then atomically publish the directory or its manifest.

Also:

- catch and quarantine failures per Bronze record instead of aborting the whole job;
- validate/inject wrapper `id` and `updated_at` rather than relying solely on payload copies;
- record source Bronze shard checksums;
- record normalizer source hash/schema version;
- write a re-normalization manifest;
- verify normalized count and version keys against Bronze before publishing.

---

## P1-02 — List/detail identity and version agreement are not validated

**Evidence:** reproduced offline.

The crawler uses the listing ID for dedup state but normalizes whatever ID appears in the detail payload. It does not require:

```text
detail.id == listed.id
```

nor does it validate that the detail `updated_at` agrees with the listing version.

### Reproduction

The list returned ID `A`; the detail response returned ID `B`. Two repeated runs produced index IDs:

```json
["B", "B"]
```

The second run fetched the same source again because dedup looked for `A` while the index contained `B`. Reconciliation correctly detected a duplicate version key, but only after invalid data had been committed.

### Required fix

Before normalization or storage:

```python
canonical_detail_id = raw.get("id")
if canonical_detail_id != sid:
    quarantine(reason="list_detail_id_mismatch")
    continue
```

Also validate:

- ID present and correctly typed;
- detail `updated_at` present;
- list and detail timestamps agree or have an explicitly documented race policy;
- response schema/format is the one requested;
- source version is not older than the version advertised by the list.

Keep both list and detail observations in an acquisition envelope for audit:

```json
{
  "listed_id": "...",
  "listed_updated_at": 123,
  "detail_id": "...",
  "detail_updated_at": 123,
  "fetched_at": "...",
  "payload": {}
}
```

---

## P1-03 — Bronze privacy filtering is recursive but not an enforceable “drop all free text” policy

**Evidence:** reproduced offline.

The update recursively removes exact keys in `_PRIVACY_DROP`, which is better than the previous top-level-only implementation. However, it remains a case-sensitive denylist. Unknown fields and differently named free-text fields survive.

### Reproduction

The following values remained after `_strip_pii`:

```json
{
  "emailAddress": "alice@example.test",
  "profile_url": "https://visualizer.coffee/api/shots/x/profile",
  "image_url": "https://example.test/users/alice/shot.jpg",
  "metadata": {
    "Owner": "Alice",
    "comment": "Alice home machine",
    "location": "123 Home St"
  }
}
```

Visualizer's serializer can expose `metadata`, `profile_url`, `image_url`, and other optional fields. A corpus with multiple integrations may contain additional arbitrary keys not anticipated in the denylist.

The normalized Silver record also retains string fields such as `grinder_model`, `grinder_setting`, and `roast_level`. These are scientifically useful, but the current provenance claim that all free text is dropped is too broad.

### Required privacy architecture

Choose one explicit model with the maintainer/data grant.

#### Model A — restricted exact Bronze plus privacy-reviewed research layers

```text
Bronze-0: exact authorized payload, encrypted and access-controlled
Bronze-R: allowlisted/pseudonymized research payload
Silver: normalized typed fields
Gold: approved aggregates/features
```

This is the strongest scientific design because the exact source can be reprocessed, while only approved layers are exposed to ordinary research workflows.

#### Model B — no exact raw retention, strict allowlisted Bronze

If exact raw retention is not permitted, define a recursive allowlist of accepted paths and types. Unknown keys are excluded and counted, not automatically retained.

Example:

```text
allowed scalar fields:
  id, updated_at, start_time, duration, bean_weight, drink_weight, ...
allowed trace fields:
  timeframe, data.espresso_pressure, ...
allowed structured fields:
  selected documented brewdata subtrees
```

### Additional recommendations

- Drop or tokenize relinking URLs such as `profile_url` and `image_url`.
- Case-fold keys for privacy matching only if using a denylist fallback.
- Treat arbitrary `metadata` as restricted by default.
- Use a keyed HMAC rather than plain `SHA256(salt | user_id)`.
- Increase the persistent user pseudonym from 64 bits (16 hex chars) to at least 128 bits to make collision risk negligible for user-level longitudinal work.
- Keep exact `start_time` restricted; bucket it for derived/public products.
- Add automated privacy tests with unknown nested keys, capitalization variants, URLs, arrays, and integration-specific payloads.

---

## P1-04 — Run manifests are useful but not yet publication-grade, and the Git commit can be wrong

**Evidence:** source review and reproduced offline.

`_git_commit()` executes:

```python
subprocess.run(["git", "rev-parse", "HEAD"])
```

without setting `cwd`. It therefore reports the Git repository of the process's current working directory, not necessarily the Puckworks repository containing the harvester.

### Reproduction

The harvester was called while the process was inside an unrelated temporary Git repository. `_git_commit()` returned that unrelated repository's HEAD exactly.

### Fix

Resolve the repository root from the module path:

```python
repo_root = Path(__file__).resolve().parents[2]
subprocess.run(
    ["git", "rev-parse", "HEAD"],
    cwd=repo_root,
    ...
)
```

Also record a SHA-256 of the exact normalizer source file. A content hash is more reliable than Git state when local changes are present.

### Manifest fields still needed

```yaml
run_id:
mode:
access_scope:
authentication_mode:
source_snapshot_id:
source_watermark:
source_expected_count:
source_api_version:
visualizer_source_commit:
puckworks_commit:
normalizer_source_sha256:
normalizer_schema_version:
bronze_schema_version:
started_at:
completed_at:
listing_exhausted:
snapshot_complete:
cursor_in:
cursor_candidate:
cursor_committed:
list_pages_requested:
list_rows_seen:
unique_list_ids:
detail_requests:
detail_successes:
status_counts:
retry_counts:
new_versions:
unchanged_versions:
quarantine_counts_by_reason:
lifecycle_counts:
normalized_shards:
  - name:
    records:
    sha256:
bronze_shards:
  - name:
    records:
    sha256:
index_fragments:
  - name:
    rows:
    sha256:
salt_key_id_or_fingerprint:
reconciliation_report_sha256:
```

The current manifest write failure is silently swallowed. Acquisition may continue, but the resulting run should be marked **not publishable** until a manifest is reconstructed and verified. At minimum, emit a durable error outside the failed manifest path.

---

## P1-05 — Reconciliation does not validate Bronze parity or acquisition manifests

**Evidence:** reproduced offline.

A normalized shard and matching index were created with zero Bronze records, while `store_bronze=True` was conceptually expected. `reconcile_store` returned:

```json
{
  "ok": true,
  "n_shard_records": 1,
  "n_index_rows": 1,
  "n_bronze": 0,
  "problems": []
}
```

The function reports `n_bronze` but does not make a mismatch a failure.

### Required extension

When Bronze is required, reconciliation must verify:

- one Bronze wrapper for every normalized stored version;
- same canonical ID and source version;
- source payload hash present and valid;
- Bronze wrapper/payload identity agrees;
- no Bronze-only orphan;
- no normalized-only orphan;
- committed shard manifests/checksums agree;
- no unresolved retry/quarantine entry prevents snapshot completeness;
- run manifest counts reconcile with physical files.

Keep a separate mode for intentionally Bronze-free derived stores, but make that mode explicit in the store manifest rather than inferred.

---

## P1-06 — Integration/source provenance remains inferred and conflated with machine identity

**Evidence:** source review.

Puckworks checks for explicit fields such as `integration_source`, `integration`, or `parser`, but the reviewed Visualizer native serializer and OpenAPI schema do not expose a stable integration/parser enum. The fallback derives a source from a small set of `brewdata` keys or machine fields.

That fallback conflates distinct concepts:

- source application/import adapter;
- machine manufacturer/model;
- profile ecosystem;
- telemetry semantics;
- parser version.

This matters because integrations can differ in channel definitions, sensor placement, sample cadence, filtering, flow estimation, units, and firmware-era behavior.

### Required source fields

A corpus export should emit explicit controlled fields such as:

```json
{
  "integration_source": "gaggiuino",
  "integration_schema_version": 3,
  "parser_name": "Parsers::Gaggiuino",
  "parser_version": "...",
  "machine_make": "Gaggia",
  "machine_model": "Classic Pro",
  "telemetry_unit_profile": "visualizer_chart_v2"
}
```

The parser/integration source should be authoritative source metadata, not guessed from user text or machine labels.

### Puckworks action

- retain explicit source verbatim;
- retain source-version fields;
- mark inferred source as low confidence;
- never use inferred source for hard unit conversion unless the source contract validates it;
- stratify all pilot QC by integration source.

---

## P1-07 — Physical-domain and cross-channel QC are still missing

**Evidence:** reproduced offline.

The parser validates finite numeric representation but does not validate physical plausibility. A synthetic record containing impossible values normalized without any range or physical flags:

```json
{
  "dose_kg": -0.018,
  "duration_s": -30.0,
  "tds_fraction": 2.5,
  "ey_fraction": -0.05,
  "pressure_Pa": [-500000.0, 100000000.0],
  "temperature_K": [-26.85, 1273.15],
  "flags": []
}
```

These records should generally be retained in Bronze, but they should not silently enter modeling cohorts.

### Add two levels of validation

#### Hard representation/physical impossibility checks

Examples, with thresholds agreed from source contracts rather than copied blindly:

- fractions outside `0..1`;
- nonpositive dose or duration;
- impossible absolute temperature;
- extreme/negative pressure where not supported by sensor semantics;
- impossible flow/weight magnitudes;
- start/end time contradiction.

#### Soft domain/plausibility checks

Use broad source-specific ranges and retain flagged values for review. Do not delete data merely because it is unusual.

### Add cross-channel QC

- cumulative weight monotonicity and downward jumps;
- integral of scale-derived mass flow versus weight change;
- scalar drink weight versus terminal trace weight;
- scalar duration versus final time sample;
- pressure/flow goal versus achieved availability;
- time gaps and longest missing interval;
- excessive sampling jitter;
- temperature rate-of-change;
- duplicate or reset segments;
- source-specific channel combinations.

### Create declared analytic eligibility

Rather than requiring every downstream analyst to interpret dozens of flags, derive explicit, versioned fields:

```text
eligible_trace_basic
eligible_pressure_analysis
eligible_pressure_mass_flow_analysis
eligible_weight_analysis
eligible_outcome_linkage
eligibility_reason_codes
qc_policy_version
```

The original values and detailed flags should remain available.

---

## P1-08 — Current latest/rebuild/reconcile paths are not corpus-scale streaming paths

**Evidence:** source review.

Some APIs are generators, but several important functions still retain O(N) or worse in-memory state:

- `latest_index_rows()` creates a dict for every unique shot;
- `iter_store_latest()` creates a winners dict and then a `chosen` dict holding the full latest trace record for every shot before yielding;
- `rebuild_index()` builds all rows in one Python list;
- `reconcile_store()` builds Counters containing every version key;
- `compute_stats()` relies on the non-streaming latest reader.

For millions of shots, storing every full trace in `chosen` can require very large memory even if each shard is read sequentially.

### Recommended storage/analysis split

Use JSONL/gzip only as an immutable acquisition interchange if desired. Build a scalable Silver layer:

```text
shots.parquet
  one row per source version; scalar/context/outcome/QC fields

traces.parquet or partitioned Arrow datasets
  shot_id, version, channel, samples/list array or long-form points

latest_versions.parquet / DuckDB view
  one source version per shot

tombstones.parquet
run_manifests/
```

DuckDB or SQLite can maintain version/latest indexes without loading them into Python memory. Parquet allows column pruning and predicate pushdown for analysis.

### Required scale test

Before the full corpus, synthesize or sample at least the expected order of magnitude and measure:

- peak RAM;
- disk amplification Bronze → Silver;
- records/second normalization;
- re-normalization throughput;
- reconciliation time;
- latest-view query time;
- random record audit time;
- shard/partition counts.

---

# 6. Additional correctness findings

## P2-01 — The state channel bypasses parsing, alignment checks, and QC

**Evidence:** reproduced offline.

`espresso_state_change` is copied as-is. A sequence containing:

```json
[0, true, "manual-note"]
```

was retained unchanged, with no state-specific flags and no state entry in channel QC.

### Recommendation

Define the source contract for state values. Then:

- preserve alignment with the time vector;
- validate allowed types/codes;
- reject or quarantine arbitrary free text;
- record missing/invalid count;
- check length agreement;
- expose state-code vocabulary/source version;
- include it in QC without treating it as a continuous numeric channel.

---

## P2-02 — Non-integer sensory values are silently truncated

**Evidence:** reproduced offline.

A `flavor` value of `7.9` is accepted and stored as integer `7` because the code calls `int(v)` after range checking. That hides malformed or off-contract data.

### Recommendation

Require an exact integer:

```python
if isinstance(v, int) and not isinstance(v, bool):
    ...
elif isinstance(v, float) and math.isfinite(v) and v.is_integer():
    ...
else:
    flag("noninteger_sensory")
```

Do not round or truncate without an explicit source rule.

---

## P2-03 — Generic numeric parsing conflates zero, missing, and invalid

`_num` treats numeric zero as missing for every scalar field:

```python
if v in (None, "", 0):
    return (None, False)
```

This may reflect the source's zero-as-unentered convention for TDS/EY, but it is not appropriate as a universal rule.

Examples:

- TDS/EY zero may be a source sentinel and should be labeled as such.
- dose zero is invalid, not merely missing.
- duration zero is invalid or a special record, not necessarily missing.
- drink weight zero may indicate an aborted shot and can be scientifically informative.

### Recommendation

Make parsing field-specific:

```text
raw parse result
source sentinel interpretation
domain validation
normalized value
flags
```

Preserve a reason code such as:

```text
missing_blank
missing_source_zero_sentinel
invalid_nonpositive
unparseable_suffix
out_of_range
```

---

## P2-04 — Empty series and absent series are collapsed

`_series` returns `None` for both a missing key and an empty list. These cases may mean different things:

- key absent because integration does not provide the channel;
- key present but the source emitted an empty array;
- parsing/import failure;
- legitimately empty/aborted record.

### Recommendation

Represent source presence separately:

```text
channel_present_in_payload
raw_length
valid_length
```

This will improve integration coverage studies and help distinguish structural missingness from bad data.

---

## P2-05 — Source unit assumptions are stronger than the reviewed API schema

The OpenAPI shot detail is intentionally flexible, and the reviewed schema does not enumerate every chart-data channel with a source-specific unit contract. Puckworks assumes common Visualizer conventions for bar, °C, grams, and grams/second.

These assumptions may be correct for normalized chart data, but the canonical corpus should not rely only on convention—especially across multiple parser ecosystems.

### Recommendation

Ask Visualizer to include either:

```json
"channel_units": {
  "espresso_pressure": "bar",
  "espresso_temperature_basket": "degC",
  "espresso_flow_weight": "g/s"
}
```

or a stable `telemetry_unit_profile` whose versioned schema documents all channels. Puckworks should store the source unit declaration and reject/flag mismatches with the expected profile.

---

## P2-06 — Detail endpoint scope should be made explicit in the research export

The reviewed `show` path looks up `Shot.find_by(id:)` inside `with_shot`; it is not visibly scoped to `Shot.visible` in that controller path. The OpenAPI describes `/shots/{id}` as a public read endpoint. This may be an intentional UUID-by-ID sharing model, but the research pipeline should not rely on ambiguity.

### Recommendation

- Enumerate only IDs supplied by the authorized corpus snapshot/list.
- Never probe or guess IDs.
- Make the custom corpus export explicitly select the permission scope, normally `Shot.visible`.
- Include `scope` and visibility policy in the export manifest.
- Ask the maintainer to confirm whether any non-public records are included under the permission grant.

---

## P2-07 — Several state files and ledgers are themselves non-atomic

The following ordinary writes are not temp-file + `fsync` + replace operations:

- `_cursor.json`;
- `_list_page.json`;
- run manifest JSON;
- quarantine JSONL append;
- normal index append.

A crash can truncate one of these files or leave a valid-looking but incomplete final line.

### Recommendation

- Atomic-replace small JSON state files.
- Use an append log with checksummed records or SQLite for quarantine/retries.
- `fsync` file and parent directory where durability matters.
- Treat corrupt state as recoverable from committed shard manifests.

---

## P2-08 — `Retry-After` and request accounting are limited

The retry code parses `Retry-After` only when it consists solely of digits. HTTP-date values are not handled. `--max-requests` counts successful detail fetches, not list requests, failed attempts, or retries. The CLI now documents that distinction, which is good, but an operator may still need a total-request or wall-clock cap.

### Recommendation

Record and expose:

```text
total_http_attempts
list_attempts
detail_attempts
retry_attempts
status_counts
bytes_received
```

Support both delta-seconds and HTTP-date `Retry-After`. Add an identifying User-Agent/contact string agreed with Visualizer.

---

## P2-09 — The same `content_sha256` name refers to different content layers

The normalized record's `content_sha256` hashes normalized content. The Bronze wrapper's `content_sha256` hashes the filtered source payload. These are both useful but semantically different.

### Recommendation

Rename explicitly:

```text
source_payload_sha256
normalized_record_sha256
```

Also include the unambiguous hash algorithm and canonicalization version.

---

# 7. Documentation corrections required before a production run

The current `PROVENANCE.md` materially overstates or misstates several behaviors.

## 7.1 Full-corpus scope

Current language says the public documented API is sufficient and no bulk export is needed. The reviewed controller and OpenAPI do not support that claim. Replace it with the actual authorized transfer mechanism and scope.

## 7.2 Timeframe location

The field map says the shared vector is `data.timeframe`. Current native serialization puts it at top level for chart-data records. Document top-level `timeframe`, with legacy nested fallback only as an implementation compatibility note.

## 7.3 Store layout

The layout omits:

- `bronze_*.jsonl.gz`;
- `_quarantine.jsonl`;
- `_runs/*.json`;
- version history semantics;
- reconciliation and rebuild commands;
- committed shard/checksum manifests once added.

## 7.4 Privacy description

The document says all free text is dropped. Current behavior drops selected exact keys but retains several string context fields and unknown Bronze fields. State the actual tiered policy precisely.

## 7.5 Incremental behavior

The document says incremental mode retrieves only new/updated records. On the ordinary unauthenticated public endpoint, Visualizer ignores `updated_after`; Puckworks therefore rescans the public window and locally skips known timestamps. That is not a source-side incremental feed and cannot detect all same-second changes.

## 7.6 Runtime

Replace “multi-hour” with a calculation based on expected corpus size and actual transfer mechanism. Ordinary per-record API retrieval at 18/min is measured in many weeks per million records.

## 7.7 Resume guarantees

Replace “fully resumable” and “no data loss” with narrower guarantees until snapshot pagination, lifecycle, same-second versions, and multi-artifact transactions are fixed.

Suggested language:

> Individual normalized and Bronze shard files are written atomically, and interrupted runs preserve committed shards. The current ordinary API crawler is suitable for engineering pilots but does not yet guarantee complete snapshot enumeration or exact change capture across a moving corpus.

---

# 8. Recommended target data architecture

## 8.1 Acquisition manifest

A maintainer-generated export should include:

```json
{
  "snapshot_id": "visualizer-public-2026-07-15T00:00:00Z",
  "generated_at": "2026-07-15T...Z",
  "scope": "public_shots",
  "visualizer_commit": "...",
  "export_schema_version": 1,
  "record_count": 1234567,
  "user_identifier_policy": "server_pseudonym_v1",
  "files": [
    {
      "name": "shots-00000.ndjson.zst",
      "records": 100000,
      "bytes": 123,
      "sha256": "..."
    }
  ]
}
```

## 8.2 Acquisition envelope per record

```json
{
  "snapshot_id": "...",
  "shot_id": "...",
  "source_record_version": "...",
  "start_time": "...",
  "created_at": "...",
  "updated_at": "...with subsecond precision...",
  "visibility_scope": "public",
  "integration_source": "...",
  "parser_version": "...",
  "machine_make": "...",
  "machine_model": "...",
  "telemetry_unit_profile": "...",
  "user_pseudonym": "...",
  "payload_sha256": "...",
  "payload": {}
}
```

## 8.3 Bronze layers

### Bronze-0 — restricted exact authorized snapshot

- immutable;
- encrypted/access-controlled;
- exact payload and export envelope;
- source checksums verified;
- not exposed to routine notebooks;
- retention and deletion policy documented.

### Bronze-R — research-safe source representation

- recursive allowlist;
- approved pseudonyms;
- URLs and arbitrary free text removed or separately governed;
- unknown-field counts retained;
- source payload hash links back to Bronze-0.

## 8.4 Silver — normalized scientific representation

At minimum:

```text
source identity and source version
integration/parser/unit profile
machine and profile metadata with provenance
hydraulic channels and source units
outcomes as a separate evidence tier
context and brew event time
trace QC and physical QC
eligibility policies and reason codes
normalizer schema/source hash
source_payload_sha256
normalized_record_sha256
```

## 8.5 Gold — analysis-specific products

Examples:

- one latest source version per shot;
- source-stratified trace features;
- profile-shape clusters;
- pressure/flow envelopes;
- repeated-user longitudinal cohorts;
- outcome-ready subsets;
- machine/integration coverage tables;
- privacy-reviewed aggregates for public communication.

Every Gold product should name:

```text
source snapshot
Silver schema/version
cohort/eligibility policy version
feature code commit/hash
row/shot/user counts
exclusion reasons
```

---

# 9. Acceptance gates before the canonical harvest

## Gate A — Access and scope

Pass only when:

- a known public shot older than one month is present;
- records from multiple users are present under the authorized corpus mechanism;
- the permission scope is explicit;
- the expected source record count is supplied;
- the transfer mechanism is practical for corpus size;
- no ordinary account/Premium ambiguity remains.

## Gate B — Snapshot completeness

Pass only when:

- snapshot ID or watermark is fixed;
- ordering/cursor is deterministic;
- same-key ties are deterministic;
- expected count reconciles;
- all unresolved fetch/retry records are zero or explicitly accounted for;
- a repeat import of the same snapshot produces the same source hashes and counts.

## Gate C — Identity and version correctness

Pass only when:

- list/export ID equals payload ID;
- source version has subsecond precision or a monotonic token;
- same-second/source-version tests capture changed content;
- unchanged records do not generate duplicate versions;
- missing/mismatched identity is quarantined before storage;
- exact normalized latest version is reproducible.

## Gate D — Transactional durability

Pass only when:

- normalized/Bronze/index shard sets have commit manifests;
- crash injection at every write boundary leaves either a committed set or an ignored orphan;
- index rebuild from committed shards reproduces the same latest view;
- cursor/checkpoint never advances beyond committed data;
- all file checksums verify.

## Gate E — Bronze and privacy

Pass only when:

- exact-vs-filtered retention policy is approved;
- unknown fields cannot bypass privacy controls;
- relinking URLs and arbitrary metadata are governed;
- user pseudonym method and collision/security properties are documented;
- exact timestamps are restricted or bucketed for derived/public products;
- Bronze-normalized one-to-one reconciliation passes.

## Gate F — Source shape and integration coverage

Pass only when real, approved fixtures cover materially represented sources, including at least:

- Decent;
- Meticulous;
- Beanconqueror;
- Gaggiuino;
- GaggiMate;
- Smart Espresso Profiler;
- Pressensor;
- any additional integration above a defined prevalence threshold.

For each fixture verify:

- chart-data or brewdata-only shape;
- time base;
- channel names;
- units;
- parser/integration source;
- optional outcomes;
- nulls and malformed values;
- source-specific machine/context fields.

## Gate G — QC and scientific eligibility

Pass only when:

- representation QC, physical QC, and cross-channel QC are versioned;
- invalid values are flagged without silently becoming valid measurements;
- eligibility cohorts are explicit;
- all exclusion reasons are countable;
- integration-stratified QC reports are produced.

## Gate H — Offline re-normalization

Pass only when:

- destination must be empty or explicitly replaced;
- repeated run into the same logical version is deterministic and idempotent;
- per-record failures quarantine rather than abort;
- wrapper identity/version is validated;
- source Bronze checksums are recorded;
- output reconciliation passes before publication.

## Gate I — Scale

Pass only when a representative large pilot demonstrates bounded memory and acceptable throughput for:

- import;
- latest selection;
- reconciliation;
- re-normalization;
- feature extraction;
- aggregate generation.

## Gate J — Documentation

Pass only when `PROVENANCE.md`, the data card, CLI help, and runbook all describe the actual mechanism and no longer claim:

- ordinary API full-corpus access;
- source-side unauthenticated incremental filtering;
- multi-hour runtime for millions of detail requests;
- blanket free-text removal under the current denylist;
- unconditional no-data-loss resume guarantees.

---

# 10. Recommended implementation order

## Immediate — before any canonical acquisition

1. Obtain the fixed snapshot or dedicated corpus endpoint.
2. Define the exact permission scope and raw-retention/privacy policy.
3. Require deterministic source versioning and snapshot identity.
4. Add list/export-to-detail ID/version validation.
5. Replace page-offset completeness assumptions with snapshot/keyset semantics.
6. Add committed shard-set manifests and Bronze parity checks.
7. Model lifecycle/tombstones and continue past record-specific failures.
8. Fix the offline re-normalizer's destination behavior and provenance.
9. Replace Bronze denylist behavior with a governed restricted/allowlisted design.
10. Update `PROVENANCE.md` before operators follow it.

## Next — bounded pilot

1. Import 1,000–10,000 records or a source-defined stratified slice.
2. Include every major integration and both serializer shapes.
3. Produce source counts, shape counts, channel coverage, QC, privacy audit, and storage metrics.
4. Manually compare at least dozens of source payloads and normalized records, stratified by integration.
5. Re-run the entire normalization from Bronze and require identical results.
6. Inject failures at write boundaries and verify commit/recovery behavior.
7. Reconcile against source manifest counts and checksums.

## Then — canonical snapshot

1. Verify all source checksums.
2. Preserve immutable restricted Bronze.
3. Generate privacy-reviewed Bronze-R.
4. Normalize to versioned Silver.
5. Reconcile and sign/hash the dataset manifest.
6. Freeze eligibility and feature-policy versions for each analysis.
7. Build Gold products from Silver, never directly from a moving API.

---

# 11. Suggested focused code changes

## 11.1 Validate acquisition identity

```python
def validate_detail_envelope(sid, listed_updated_at, raw):
    detail_id = raw.get("id")
    if not detail_id or detail_id != sid:
        raise IntegrityError(
            f"list/detail id mismatch: listed={sid!r}, detail={detail_id!r}"
        )

    detail_updated_at = raw.get("updated_at")
    if detail_updated_at is None:
        raise IntegrityError("detail missing updated_at/source version")

    return detail_updated_at
```

## 11.2 Do not use integer timestamp alone as the prefetch version key

```text
preferred list tuple:
    id, source_record_version, source_payload_sha256
```

Then:

```python
if stored_source_version == listed_source_version \
        and stored_source_payload_sha256 == listed_source_payload_sha256:
    skip
else:
    fetch
```

## 11.3 Make state files atomic

```python
def atomic_json(path, obj):
    tmp = path.with_suffix(path.suffix + ".tmp")
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(obj, fh, sort_keys=True)
        fh.flush()
        os.fsync(fh.fileno())
    os.replace(tmp, path)
```

## 11.4 Fix Git provenance

```python
def _git_commit():
    repo_root = Path(__file__).resolve().parents[2]
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=repo_root,
        capture_output=True,
        text=True,
        timeout=5,
    )
    return result.stdout.strip() if result.returncode == 0 else None
```

Also compute:

```python
normalizer_source_sha256 = sha256(Path(__file__).read_bytes()).hexdigest()
```

## 11.5 Require an empty re-normalization destination

```python
dst = Path(dst_dir)
if dst.exists() and any(dst.iterdir()):
    raise RuntimeError(
        "re-normalization destination must be empty; choose a new schema-version directory"
    )
```

## 11.6 Use HMAC for persistent user pseudonyms

```python
hmac.new(secret_key, b"visualizer-user-v1\x00" + user_id_bytes, hashlib.sha256)
```

Store at least 128 bits in the research pseudonym.

---

# 12. Detailed adversarial test results

These tests used synthetic data and monkeypatched transport only. They did not query or expose real Visualizer users.

| Test | Observed result | Interpretation |
|---|---|---|
| same-second changed payload | second run fetched 0 records; old pressure remained | content hash cannot help when timestamp prefilter skips fetch |
| list ID `A`, detail ID `B` | `B` stored twice across two runs; duplicate version detected later | acquisition identity must be validated before commit |
| detail fetch raises 404 | crawl stops before later IDs; no quarantine entry | record lifecycle failure is treated as run failure |
| re-normalizer run twice into same destination | 2 shard records, 4 index rows; reconciliation fails | output is not idempotent/safe on existing destination |
| normalized+index with no Bronze | reconciliation reports `ok=true` | Bronze parity is not an integrity requirement today |
| unknown nested free text and URLs | values survive recursive exact-key filter | denylist does not enforce all-free-text removal |
| malformed state values | boolean/string retained, no QC | state channel bypasses parser/QC |
| brewdata-only record | `n_samples=0`, empty hydraulic | non-chart serializer shape unsupported |
| impossible physical values | retained without range flags | representation validation is not physical validation |
| caller in unrelated Git repo | manifest helper reports unrelated HEAD | provenance commit is working-directory dependent |

---

# 13. Final assessment

The current revision is a strong engineering step and should be kept. Its normalized schema is now credible enough to support a **bounded, instrumented pilot of chart-data records**, and its repository tests cover many of the defects found in earlier reviews.

It is not yet a safe mechanism for a canonical corpus acquisition, primarily because the ordinary API does not provide the corpus, the listing is not a snapshot, version discovery depends on second-resolution timestamps, and the store lacks a transactional commit boundary across its three essential artifacts. The remaining issues are fixable; most do not require abandoning the current normalizer. They require wrapping it in a stronger source/export contract and a transactional, privacy-governed data architecture.

### Go/no-go summary

- **Go:** continue serializer/normalizer development and a small recent-public engineering pilot.
- **Conditional go:** import a maintainer-provided fixed snapshot after identity, transaction, privacy, re-normalization, and reconciliation fixes.
- **No-go:** label an ordinary API run as the complete historical Visualizer corpus.
- **No-go:** use current output as publication-grade population evidence without source-stratified QC, exact snapshot provenance, and declared analytic eligibility.

The best next milestone is not another long production crawl. It is a **snapshot-contract test**: obtain a small maintainer-generated export with a manifest, ingest it end-to-end, prove exact counts/checksums and offline reproducibility, and then scale that same mechanism to the full authorized corpus.

---

## Source index

### Visualizer

- [Shot API controller](https://github.com/miharekar/visualizer/blob/main/app/controllers/api/shots_controller.rb)
- [Shot serializer](https://github.com/miharekar/visualizer/blob/main/app/models/shot/jsonable.rb)
- [Shot model/scopes](https://github.com/miharekar/visualizer/blob/main/app/models/shot.rb)
- [OpenAPI specification](https://github.com/miharekar/visualizer/blob/main/openapi.yaml)
- [Repository README / supported integrations](https://github.com/miharekar/visualizer)

### Puckworks

- [Visualizer harvester/normalizer](https://github.com/trbrewer/puckworks/blob/main/puckworks/lib/visualizer_harvest.py)
- [Harvester tests](https://github.com/trbrewer/puckworks/blob/main/tests/test_visualizer_harvest.py)
- [Visualizer provenance](https://github.com/trbrewer/puckworks/blob/main/puckworks/data/visualizer/PROVENANCE.md)
- [Visualizer data card](https://github.com/trbrewer/puckworks/blob/main/docs/cards/visualizer_coffee.md)
- [Harvester commit history](https://github.com/trbrewer/puckworks/commits/main/puckworks/lib/visualizer_harvest.py)
