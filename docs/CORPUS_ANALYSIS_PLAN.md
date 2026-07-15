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
| PR 2 | WP1 corpus atlas scaffold: shared eligibility engine, fixture-backed P0 census, pressure-only P2 metrics | **landed** (`puckworks/analysis/`) |
| PR 3 | WP2 registry schema v2: execution_role / provenance_class / evidence_strength + migration | **landed** (`registry.py` v2) |
| PR 4 | WP2 Paper-3 generators: Table 1, Appendix A, counts, gate matrix, registry export (producer-backed) | **landed** (`puckworks/paper3/`) |
| PR 5 | WP3 CI lanes + Paper-3 verify/release extension | **landed** (`.github/workflows/` + `paper3/build.py`) |
| PR 6 | WP4 frozen-snapshot bundle: final P0/P1/P2 aggregates + sensitivity + claim bundle | **BLOCKED on freeze** (needs a clean final crawl / maintainer export) |
| PR 7 | Paper integration (Paper 3 first; B2 only where evidence genuinely strengthens it) | **BLOCKED on PR 6** |

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

## PR 2 (WP1) — landed (`puckworks/analysis/`)
- **Shared eligibility engine** (`visualizer_eligibility.py`): profiles `census_all`,
  `hydraulic_valid`, `pressure_tracking_valid`, `mass_flow_tracking_valid`,
  `exploratory_proxy_flow`, `outcome_descriptive_only`; `eligibility_report` gives inclusion
  + exclusion-flow + source/user concentration.
- **P0 census** (`visualizer_census.py`): source/machine mix, channel availability, outcome
  coverage (SEPARATE tier), QC-by-source, duration/n-sample histograms, and a
  **one-shot-per-user** sensitivity block.
- **P2 pressure atlas** (`controller_atlas.py`): per-shot commanded-vs-achieved metrics
  (coverage, goal transitions, RMSE/nRMSE, median/p90 abs error, bias, overshoot), aggregated
  overall / by source family / one-shot-per-user. Hard guard: only pooling-safe pressure
  channels (ambiguous flow refused).
- Every product is a deterministic envelope with the snapshot manifest hash + an EXPLORATORY
  marker. Tests: `tests/test_visualizer_analysis.py`.
- **First live-store read (rehearsal, exploratory):** 6,200 shots; `integration_source` all
  `unknown` (confirms P1-06 — no source-side enum); pressure present 5,929; **max 366 shots
  from one of 480 users** → strong contributor concentration (why one-shot-per-user matters).
  Pressure atlas: 1,510 eligible (359 one-per-user), RMSE median ≈2.5 bar. NOT paper-grade.

### PR 2 remaining (before closing WP1)
- [ ] P1 measurement/source **dictionary render** (Markdown + CSV/JSON) as a scientific output.
- [ ] Flow tranche — deferred until quantity kinds are resolved (Gate C); pressure-first stands.
- [ ] Statistical guardrails beyond one-shot-per-user: user-clustered bootstrap, predeclared
      primary metrics (do at freeze).

## PR 3 (WP2.1) — registry schema v2 (`puckworks/registry.py`)
Split `kind` into typed `execution_role` / `provenance_class` / `evidence_strength`;
`register()` back-fills role+provenance from legacy kind/name (all 25 migrate with no edits),
rejects duplicate ids, validates enums. `kind` kept as deprecated compat. Known debt:
`evidence_strength` unclassified on all 25 (card-driven; never auto-assigned).

## PR 4 (WP2.3/2.4) — Paper 3 generators (`puckworks/paper3/registry_artifacts.py`)
Producer-generates, into `docs/paper3_resource/generated/` (deterministic; no timestamp/commit
embedded): `table1_registry_overview.md`, `appendixA_component_catalog.md`,
`registry_counts.json`, `component_gate_matrix.csv`, `registry_export.json` (with content
hashes). CLI `--write` / `--verify`. Test `test_registry_artifacts.py` fails CI on a stale or
hand-edited artifact (WP2.4). Remaining: populate `evidence_strength` from cards; wire
component→dataset ids + card cross-reference once components carry dataset ids.

## PR 5 (WP3) — CI lanes + Paper 3 verify (`.github/workflows/`, `puckworks/paper3/build.py`)
Five separated lanes: **quick-pr** (3.10+3.12 matrix, offline unit/integrity — was `gates.yml`),
**generated-artifacts** (`registry_artifacts --verify` + `build verify`, fails on drift),
**slow-science** (dispatch+weekly), **live-contract** (scheduled canary, secret-gated, stub
until the WP0 canary lands), **release** (tag/dispatch clean-build + verify). `paper3.build
verify` is the CI gate: fails on stale artifacts / invalid enums / missing bundle files;
unclassified evidence is a warning. Tag/Zenodo/DOI stay human. Tests: `test_paper3_build.py`.

## BLOCKED beyond PR 5
- **PR 6 (freeze bundle)** and **PR 7 (paper integration)** require a **frozen publication
  snapshot** — a clean final crawl under the current schema OR a maintainer static export.
  The in-flight crawl is exploratory/mixed-schema (WP0 0.3) and must not be frozen as-is.
  These are the definition-of-success items that need the Miha export / a deliberate re-crawl.

## Remaining UNBLOCKED sub-items
- ✅ WP1.3 measurement/source **dictionary render** (md/csv/json, producer-backed).
- ✅ WP0.5 QC-columns tabular accessor (`CorpusSnapshot.qc_table()` + `QC_COLUMNS`).
- ✅ WP0.6 redacted live-shape **fixture matrix** + contract test
  (`tests/fixtures/visualizer/shapes/`, `test_visualizer_contract_shapes.py`).
- ✅ WP2 **evidence_strength** — populated card-driven (weakest-defensible tier) in one
  auditable block (`puckworks/models/__init__.py` `_EVIDENCE_STRENGTH`); registry now fully
  classified, `validate_registry`/`build verify` clean, Appendix A carries tiers. Spread:
  1 controlled_independent (foster infiltration), 1 exploratory_synthesis (coupled_kappa_t),
  5 post_fit_reconstruction, 5 source_curve_reproduction, 5 qualitative_capacity,
  4 code_verification, 3 sign_or_compatibility, 1 within_campaign_held_out.
  **OPEN FOR REVIEW before any Paper 3 submission** — low-confidence calls to sanity-check:
  `foster2025.infiltration`=controlled_independent (a loose parameter-free first-drip bracket
  on an independent rig — downgradeable to sign_or_compatibility); `moroney2016.surrogate` &
  `lee2023.feedback`=qualitative_capacity (reproduce a source curve but sign/shape-only);
  `mo2023_2.coupled_bed`=post_fit_reconstruction (no true held-out condition);
  `romancorrochano2017.extraction`=sign_or_compatibility (Crank-verified solver but
  reality-facing evidence is trend-only, raw curves unpublished).
- ✅ WP0 live-contract **canary** — `puckworks/lib/visualizer_canary.py` (1 list + 1 detail,
  retains nothing), wired into the secret-gated live-contract lane.
- WP5 bounded B2 review prep — P2, manuscript work; better after the atlas is frozen / reviewer input.

## Cycle Definition-of-Success — status
Met except the freeze-dependent + card-driven items:
- ✅ stable snapshot interface; direct shard reads discouraged (CorpusSnapshot is the entry point)
- ✅ deterministic manifests exposing revisions/conflicts/exclusions
- ✅ privacy-stripped replay layer (Bronze) OR corpus classified exploratory-only (both)
- ✅ P0 census + P1 dictionary + pressure-first P2 atlas run end-to-end
- ✅ partial vs frozen cannot be confused (classification + EXPLORATORY marker)
- ✅ user/profile/source sensitivity automatic (one-shot-per-user)
- ✅ Paper 3 Table 1 + Appendix A generated from typed live metadata
- ✅ registry role/provenance/evidence vocabularies explicit (evidence values = card debt)
- ✅ CI quick / generated-artifact / slow / live-contract / release lanes
- ⛔ final bundle from a clean checkout of a FROZEN snapshot — blocked on freeze (PR6)
- ✅ manuscript language respects the ecological ceiling (EXPLORATORY-marked outputs)

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
