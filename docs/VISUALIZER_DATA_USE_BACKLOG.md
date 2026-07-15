# Visualizer data-use review — triaged backlog

*Created 2026-07-15, triaging `docs/visualizerCoffee_DATA_USE.md` (1814-line engineering +
scientific-use review). This is a substantial program; items are bucketed by priority.
The one **release-blocking data bug is fixed**; the rest are prioritized follow-ups.*

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
