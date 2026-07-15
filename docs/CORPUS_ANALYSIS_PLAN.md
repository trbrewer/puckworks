# Corpus-analysis + Paper-3 reproducibility program — status tracker

*Executing the 2026-07-15 next-step plan. Decision: **corpus-analysis track**, but the first
deliverable is the **minimum corpus-integrity / freeze gate (WP0)**, with a bounded Paper-3
reproducibility lane in parallel. Do NOT produce manuscript headline numbers from the partial
moving corpus; do NOT let analysis code read raw shards directly; do NOT pool proxy/volumetric/
mass flow; keep Visualizer telemetry inside the ecological-evidence ceiling.*

## Merge sequence
| PR | Work package | Status |
|---|---|---|
| PR 1 | WP0 snapshot contract: canonical view, latest-version semantics, manifest, measurement dictionary, QC, v2-bronze design | **in progress** (snapshot contract + dictionary + manifest landed) |
| PR 2 | WP1 corpus atlas scaffold: shared eligibility engine, fixture-backed P0 census, pressure-only P2 metrics | todo |
| PR 3 | WP2 registry schema v2: execution_role / provenance_class / evidence_strength + migration | todo |
| PR 4 | WP2 Paper-3 generators: Table 1, Appendix A, evidence matrix, registry export (producer-backed) | todo |
| PR 5 | WP3 CI lanes + Paper-3 verify/release extension | todo |
| PR 6 | WP4 frozen-snapshot bundle: final P0/P1/P2 aggregates + sensitivity + claim bundle | blocked on freeze |
| PR 7 | Paper integration (Paper 3 first; B2 only where evidence genuinely strengthens it) | todo |

## PR 1 (WP0) — landed so far (`puckworks/data/visualizer_store.py`)
- **Canonical snapshot view** — `CorpusSnapshot(out_dir, name, classification, as_of)`; the
  only supported analysis entry point (re-exported as `puckworks.data.CorpusSnapshot`).
  `.latest()` = one logical record per shot id (max updated_at, ties→last-written, optional
  `as_of` cutoff); `.iter_versions()` = append-only history for audit.
- **Integrity diagnostics** — `.integrity_stats()`: logical-record / stored-version counts,
  **revisions**, same-timestamp **conflicts**, and **missing-updated_at** counts (visible,
  not silently discarded).
- **Deterministic snapshot manifest** — `.manifest()` / `freeze_snapshot(...)`: store + schema
  + harvester identity, integrity counts, per-shard hashes, reconcile status, and a manifest
  content digest; **classification** ∈ {exploratory-window, current-state, publication-freeze}.
  Re-reading produces a byte-identical manifest.
- **P1 minimum measurement dictionary** — `MEASUREMENT_DICTIONARY` first tranche (time,
  pressure + goal, scale-derived mass flow, machine-reported/proxy flow + goal, cumulative
  weight, state) with quantity kind, raw/canonical unit, sensor, **commanded-vs-achieved**,
  ambiguity, eligibility. `is_pooling_safe(channel)` refuses ambiguous/native flow onto a
  physical axis (P0.4 guardrail).
- Tests: `tests/test_visualizer_store.py` (dedup/latest, integrity, as_of, deterministic
  manifest, dictionary + pooling guard).

### PR 1 remaining (before closing WP0)
- [ ] QC as first-class **columns** on the snapshot latest view (currently per-record `qc` +
      flags exist; expose a tabular QC accessor for the atlas).
- [ ] v2 bronze **sidecar** decision recorded: current bronze already stores a PII-stripped
      payload + hash + hashed_user; formalize `source_family` + retrieval metadata and the
      v1-normalized-only vs v2-bronze-backed compatibility rule in the manifest.
- [ ] Redacted live-shape **fixtures** (top-level + legacy timeframe, revised records, zero
      sensory, mixed samples, ambiguous flow, missing goals, differing source families).
- [ ] Small scheduled **live-contract canary** (schema-shape only; no retention) — WP3/CI lane.

## Handling the in-flight crawl (WP0 0.3)
The running crawl is **exploratory / rehearsal**, NOT a publication snapshot. It mixes v1
normalized-only (~3.5k pre-Bronze) and v2 bronze-backed shots; the final publication crawl
must be a clean v-current run (or a maintainer export). Any snapshot built from it must carry
`classification: exploratory-window`.

## Stop/go gates
- **A (analysis architecture)** — ✅ dedup snapshot view + measurement dictionary exist → may
  build the atlas against fixtures / exploratory shards.
- **B (paper-grade stats)** — needs a named immutable snapshot + manifest + QC + eligibility.
- **C (flow atlas)** — needs explicit flow quantity kinds/provenance → pressure atlas first.
- **D (B2 integration)** — needs user/profile/source-robust findings within ecological language.
- **E (Paper 3 submission)** — non-stale generated artifacts, quick/slow CI split, clean-release
  reproduction, explicit licensing, one external reproduction.
