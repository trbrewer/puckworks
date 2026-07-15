# Visualizer data-use review — triaged backlog

*Created 2026-07-15, triaging `docs/visualizerCoffee_DATA_USE.md` (1814-line engineering +
scientific-use review). This is a substantial program; items are bucketed by priority.
The one **release-blocking data bug is fixed**; the rest are prioritized follow-ups.*

---

## SERIALIZER_REVIEW triage (2026-07-15) — a SECOND independent review

*Triaging `docs/SERIALIZER_REVIEW.md`. Confirms the timeframe fix worked, then finds the
**real** blocker is no longer serialization: the public API route does not expose the
historical corpus, and normalized-only storage makes any later fix un-repairable.*

### DECISIVE FINDING — harvest scope (review §1), empirically confirmed → **harvest PAUSED**
The unauthenticated API paginates the recently-**updated** public feed, not the historical
corpus. **Verified against our own run:** all 3,400 harvested shots have `updated_at`
inside a **4-day window** (2026-07-11 → 07-15); **zero** older than 30 days. So the crawl
cannot acquire "the Visualizer corpus" — it is a recent-activity cohort over a live-moving
feed. The standing "run until complete" premise is void. **The detached crawl was stopped
gracefully at 3,400 shots (throwaway: recent-window only + the §6/§8 bugs + normalized-only).**
- **NEEDS TIM → MIHA (blocking):** the grant must be implemented as a **bulk transfer**, not
  permission to exercise the public API for weeks. Ask Miha for either (a) a server-side
  bulk export (compressed NDJSON/Parquet, consistent DB snapshot), or (b) a corpus-scoped
  endpoint/token that selects all `Shot.visible` and bypasses the ~1-month `non_premium`
  scope (and does NOT substitute `Current.user.shots`). At 18 req/min, 1 M shots ≈ 39 days;
  millions ≈ months — the ordinary API is not a viable acquisition path.

### DONE (committed) — safe code fixes that don't need the Visualizer side
- **§6 enjoyment scale (data-corruption bug).** `espresso_enjoyment` is a **0..100**
  preference score, but it was validated against **0..15** with the tasting dimensions, so
  every real value >15 (e.g. 82) became `None`. Fixed: per-field ceilings (`_SENSORY_MAX`,
  enjoyment→100, tasting dims→15); regression test (`test_enjoyment_uses_0_100_scale_not_0_15`).
- **§2 fresh-run FileNotFoundError.** `_crawl` now `mkdir`s `out_dir` before the first
  per-100 disk-space check (which fires on iteration 0); regression test
  (`test_crawl_creates_missing_output_dir`).
- **§5 immutable Bronze layer — DONE (why the periodic model is now safe).** The harvester
  writes a **PII-stripped raw payload** (`bronze_NNNNN.jsonl.gz`, 1:1 with each normalized
  shard) carrying `{id, updated_at, hashed_user, content_sha256, payload}` — the raw trace
  is kept, all `_PRIVACY_DROP` fields incl. `user_id` are gone, only the salted hash remains.
  `renormalize_from_bronze(cfg, dst)` re-runs the CURRENT normalizer **offline** over stored
  Bronze, reproducing the normalized store (identities preserved via the stored hash). This
  is the lever for the ephemeral recent-updated window: a normalizer fix (e.g. the pending
  §8 flow-semantics rename) now re-applies to shots already harvested, even after they age
  out of the API. Config flag `store_bronze` (default on); Bronze is gitignored with the
  store. Tests: `test_bronze_stores_pii_stripped_raw_with_content_hash`,
  `test_renormalize_from_bronze_reproduces_records_offline`. *(Legacy caveat: the ~3.4k shots
  harvested before this land have no Bronze and cannot be re-normalized — a known one-time loss.)*
  Deferred sub-item: rename the `raw/` dir (holds Bronze **and** normalized) to a clearer
  `bronze/`+`normalized/` split — cosmetic, do with the §3 latest-version refactor.

### DONE (committed) — §3 latest-version store + §4 version-aware dedup
- **§3 latest-version-wins view.** Shards + `_index.csv` stay append-only (the version log);
  reading now DEFAULTS to latest-per-id. Lib: `latest_index_rows`/`latest_index_map`
  (collapse index to newest `updated_at` per id, tie→last-written), `iter_store_latest`
  (one record per id). Data layer: `visualizer_index()` reports `n_shots` (unique live ids)
  vs `n_versions` (total rows); `visualizer_iter_shots()` defaults to latest, `versions=True`
  for history; `compute_stats` uses the latest view so re-lists aren't double-counted.
- **§4 version-aware dedup / no duplicate accumulation.** `_crawl` keys on
  `id → latest updated_at`: a listed shot is fetched only when new OR its `updated_at` is
  newer (an edit, stored as a new version); an already-held version is skipped WITHOUT a
  fetch. Fixes the old "skip if id seen" that missed every edit and the append-dup on
  re-list. `harvest_incremental` is now a safe periodic top-up; summary adds `n_updated`.
  Also fixed a truthiness bug: `updated_at`/`duration` of `0` were collapsed to `""` (read
  back as missing, defeating dedup) — now explicit None checks.
  Tests: `test_version_dedup_reruns_add_nothing_and_capture_edits` (+ realistic
  listing/detail `updated_at` agreement in the resume test).
  *(Note: this is the client-side "acceptable temporary fix" from review §4. A true opaque
  keyset `(updated_at,id)` server cursor still needs the Visualizer side; not required while
  we re-list the small recent window and dedup client-side.)*
- **§8 flow semantics — DONE (committed).** `espresso_flow`/`espresso_flow_goal` (pump/model
  estimates, possibly volumetric) are no longer labelled kg/s: kept NATIVE under
  `flow_reported__native`/`flow_goal_reported__native` with `units.si=None` + a `semantic`
  tag, flagged `unit_ambiguous:*`, and EXCLUDED from the SI accessor `visualizer_hydraulic`.
  Only the scale-derived `espresso_flow_weight` (confirmed mass) becomes SI
  `mass_flow_from_scale__kg_per_s`; `compute_stats` peak-flow uses only that. Data-layer
  `_VIS_HYDRAULIC_SI` + `visualizer_hydraulic` (skip `si=None`) + `PROVENANCE.md` updated;
  normalizer schema v2→v3. Test: `test_ambiguous_flow_kept_native_not_labelled_kg_per_s`.
  Re-applies to already-harvested shots via `renormalize_from_bronze`.
- **§7 integration/parser source — PARTIAL DONE (committed).** `_integration_source(raw)`
  records the origin app/parser SEPARATELY from `machine`, with provenance: `explicit`
  (a stable Visualizer field, if present) > `inferred` (brewdata) > `unknown` (flagged
  `missing:integration_source`, never guessed). Stored as
  `context.integration_source` + `context.integration_source_provenance`; normalizer schema
  bumped v1→v2. Test: `test_integration_source_explicit_inferred_unknown`.
  *(Still needs the Visualizer side to emit a controlled `integration_source` enum so most
  records are `explicit` rather than `inferred`/`unknown` — not in our control.)*

### DONE (committed) — §9 robust trace parsing + quarantine ledger
- **Per-element trace parsing.** `_finite_float`/`_parse_series`: booleans (would fake a
  1.0/0.0 sample), non-numeric strings, and NaN/Inf become `None` **in place** (array
  alignment preserved) and are flagged `bad_samples:<channel>=N`; a single bad sample no
  longer raises and drops the whole shot. `json.dumps(allow_nan=False)` guard so NaN/Inf
  can never enter a shard.
- **Quarantine ledger (never a silent skip).** A shot the normalizer/serializer cannot
  handle is appended to `_quarantine.jsonl` with `{run_id, id, updated_at, failure_stage,
  exception_type, reason, content_sha256}` and the crawl continues; `iter_quarantine()`
  reader; summary reports `n_quarantined` (replaces the old silent `n_skipped`) + a `run_id`.
  Tests: `test_trace_parsing_tolerates_bad_samples_without_dropping_shot`,
  `test_malformed_record_is_quarantined_not_silently_skipped`.

### DONE (committed) — atomicity + reconciliation
- **Atomic shard/bronze writes.** `_atomic_write_jsonl_gz`: temp → fsync → `os.replace`
  (`mtime=0` for reproducible gzip / stable checksums), so a crash/reap mid-write never
  leaves a torn shard that reads as valid. `_write_shard`/`_write_bronze_shard` route through it.
- **Reconciliation + rebuildable index.** `reconcile_store(cfg)` (non-destructive) verifies
  every shard readable, index↔shards id agreement, no duplicate `(id, updated_at)` version
  keys, latest-view one-per-id, and reports shard/index/bronze/quarantine counts.
  `rebuild_index(cfg)` regenerates `_index.csv` from the shards (index = derived metadata),
  atomically. CLI: `reconcile`, `rebuild-index`. `_sha256_file` helper. Tests:
  `test_shard_writes_are_atomic_no_tmp_leftover`, `test_reconcile_and_rebuild_index`.

### DONE (committed) — first-class channel QC metrics
- `_timeseries_qc` adds a per-shot `qc` block: timestamp monotonicity, non-increasing-step
  count, duplicate-stamp count, sampling-interval median + min/max + **IQR (jitter)**, and
  per-channel `valid`/`missing`/`flatline`/`len_matches_time`. High-level flags
  `qc:time_not_monotonic` / `qc:duplicate_timestamps` feed declared eligibility rules
  (beyond the raw `bad_samples`/`length_mismatch`/`missing:*` flags). Normalizer schema
  v3→v4; re-applies to harvested shots via `renormalize_from_bronze`. Test:
  `test_timeseries_qc_metrics`.

### ALL SERIALIZER_REVIEW ITEMS ACTIONED except §1 corpus access (blocked on Miha)
Every code-side review item (§2, §3, §4, §5, §6, §7*, §8, §9, §10, atomicity, QC) is
committed and tested. §1 (historical-corpus access) and the fully-`explicit` §7 source enum
require the Visualizer side and are out of our control.

### DONE (committed) — §10 per-run manifest
- Every crawl writes `_runs/<run_id>.json` with mode, counts (`n_new/n_updated/n_quarantined`),
  cursor, `started_at/completed_at`, `harvest_version`, `normalizer_schema_version`,
  `bronze_schema_version`, `puckworks_commit` (best-effort), config, and a **salt
  fingerprint** (12-hex of `sha256(salt)`, never the salt). `iter_run_manifests()` reader.
  So a paper can name the exact corpus state it was built on. Test:
  `test_run_manifest_written_with_provenance_and_salt_fingerprint`.
  *(Remaining §10 piece: shard/index checksums in the manifest — pairs with the atomicity
  item below.)*

### Acceptance gates before a canonical harvest (review Gates 1–9)
corpus access · fresh-run reliability · deterministic enumeration · raw fidelity · semantic
correctness · source fixture matrix · malformed-data matrix · version/deletion behavior ·
bounded 1k–10k pilot with a reconciliation report. Gate 1 (access) is the current blocker
and is **not in our control** — it needs the Visualizer-side export/token above.

---

## DONE (committed)
- **§8.1 (P0) timeframe location** — the live API puts `timeframe` at the **top level**,
  not `data.timeframe`; the old normalizer produced `n_samples=0` / `missing:timeframe`
  on **every** live trace (values present, no time base). Fixed (top-level read + legacy
  fallback), verified on a live shot (0→98 samples), contract test added. **The ~11.5k
  shots harvested before the fix were unusable and were cleared; a fresh crawl is running
  with the fix.** (commit `09cbb19`).
- **§8.6 (P1) valid zero sensory** — a real `0` was erased by truthiness; now kept,
  booleans excluded, out-of-range flagged.

## HIGH — decide before *paper-grade* corpus statistics
- **§9.1 store a PII-stripped raw payload (bronze-ish layer).** The harvester keeps only
  the normalized record, so **every future normalizer fix (all the §8.x items below)
  requires another full API re-crawl** — wasteful of Miha's rate budget. Storing a
  **privacy-stripped** raw response (drop `user_name`/`barista`/`*_notes`/`user_id`, keep
  `timeframe`/`data`/channels/`metadata`) would let future fixes re-normalize **offline**.
  Full bronze (§9.1) wants encrypted, access-controlled full raw incl. PII — heavier;
  the PII-stripped compromise fits the current privacy posture. **Recommend doing this
  before the *next* normalizer change so this re-harvest is the last full crawl.**
- **§8.2 (P0) unauthenticated `updated_after` is ignored.** `incremental` mode silently
  re-lists the whole public corpus (the filter is authenticated-only). Don't describe
  incremental as "only new/updated" until fixed (newest-first cutoff scan with an overlap
  window, or an owner snapshot/token).
- **§8.3 (P0) versioning not latest-write-wins.** Records are appended; `iter_store`
  yields every version → duplicates/old+new mix in stats. Needs a versioned event store +
  `latest-as-of(snapshot)` view, or an upserted current-state store.
- **§8.4 / §8.5 (P0) snapshot coherence + raw-vs-chart availability.** Moving newest-first
  pagination is not a coherent snapshot; and the default detail endpoint may return chart
  data OR `brewdata`, not both — don't advertise raw-payload preservation until verified.

## MEDIUM — normalizer/data-quality (each needs a re-harvest unless bronze lands first)
- **§8.7** flow is a *quantity-kind* problem (mass vs volumetric vs machine proxy), not
  just a unit label; add `quantity_kind` + provenance, don't force onto a `kg/s` axis.
- **§8.8** sample-tolerant series parsing (a single non-numeric sample currently drops the
  whole shot via the skip-guard); keep a validity mask, reject a channel only past a
  threshold; exclude booleans.
- **§8.9** duration parse drops its dirty-value flag (unlike dose/drink); use `_num`'s flag.
- **§8.10** source/device inference is a brittle substring list; build a versioned parser
  taxonomy (source app ≠ machine ≠ sensor); "unknown" explicit.
- **§8.11** privacy beyond dropped fields: `profile_title`/`grinder_*`/tags/exact
  timestamps/UUIDs/stable hashes are linkable; move salted hash → keyed HMAC with a
  per-release key; source-UUID in an access-controlled lookup only.
- **§8.12** deletion/tombstone/withdrawal policy (public→private/edited/deleted over time).
- **§8.13** record- and snapshot-level provenance (retrieval times, API/serializer version,
  payload hash, normalizer version, QC flags, per-snapshot counts).
- **§8.14** first-class time-series QC metrics (monotone time, dup/negative steps,
  sampling jitter, channel-length alignment, flatline, lag, weight-vs-scale-flow
  consistency) feeding declared eligibility rules — not one `flags` array.
- **§8.15** live-contract fixture suite (redacted real responses for every source family,
  zero sensory, ambiguous flow, revised/hidden shots, mixed series) + an `openapi.yaml`
  schema-diff test.

## SCIENTIFIC-USE framing (papers/wording — no re-harvest needed)
- **§4 vocabulary:** use "external ecological stress test / reference population / operating
  envelope / model-domain coverage audit / hypothesis-generating association"; **avoid**
  "validation / ground-truth permeability / channeling labels / causal effect / proof of
  mechanism." Carry into figure badges, captions, data-availability statements.
- **§4 levels:** A data/measurement validation · B domain coverage · C ecological stress
  test · D controlled independent validation. Visualizer supports A–C, **not D** for
  latent puck physics. Anchor to controlled data; population extends relevance, does not
  replace independent gates.
- **§7 priority products** (once the corpus is clean + frozen): P0 corpus census &
  quality atlas; P1 measurement/source dictionary; P2 commanded-vs-achieved controller
  atlas (likely most publishable); P3 operating-envelope × model-domain map; P4 phase
  segmentation; P5 resistance-phenotype atlas; P6 controlled↔ecological bridge; P7
  null-ladder residual study (→ narrow Paper B); P8 repeated-shot cohorts; P9 outcome
  consistency; P10 privacy-safe public dashboard.
- **Paper mapping (§Exec):** supporting role in Paper A; potentially central in the narrow
  temporal **Paper B2** and the **Paper 3** methods/resource paper (see `CLAIM_OWNERSHIP.md`).
- **§8/§9** freeze a **named corpus snapshot** (cutoff + API/serializer version + harvester
  commit + normalizer version) before any paper-grade analysis; publish code + aggregates,
  **not** the raw user corpus, unless redistribution is separately authorized.

## Scope note
`docs/visualizerCoffee_DATA_USE.md` is the authoritative detail. Only §8.1/§8.6 were
actioned immediately (the harvest was producing unusable data). The rest is a real
engineering program to be prioritized with Tim — the **bronze/raw-storage decision is the
lever** that determines whether future fixes cost another multi-hour crawl.
