# Intake ledger — what's owed, blocked, or optional

Single running list of external data the project still needs. Refreshed
2026-07-12 (supersedes the 0.1/0.6-only version). Authoritative cross-refs:
ROADMAP §3 (manifest/intake table), §4 (gaps), §5.8 (correspondence tracker);
SPRINTS status log.

## Access constraint (governs how everything below arrives)
This CC environment (verified 2026-07-10) **reaches** Zenodo (API + files),
the Mendeley **public** API, arXiv, DataCite/figshare/Dryad APIs. It is
**blocked (Cloudflare-403)** on **MDPI** (`www.mdpi.com`) and **Royal Society**
(`royalsocietypublishing.org`) — browser headers don't help — and the Mendeley
public API will **not** enumerate a dataset's subfolders (needs a manual
"Download all"). Consequence: anything hosted only on MDPI/RS, or in a Mendeley
subfolder, must be **downloaded by Tim and dropped into `puckworks/data/`**.
See memory `data-host-reachability`.

Legend: 🔴 blocks a named gap · 🟡 pending a drop/reply · 🟢 optional upgrade
(has a working fallback) · ✅ resolved.

---

## Tier 1 — hard-missing data that blocks a gap (no source on file)

Four of five are acquisition/search projects, not quick drops.

### 🔴 G1 — coffee-bed water-retention curve θ(ψ) + relative permeability K_r
- **Unblocks:** the Richards G1 unsaturated-flow / wetting model + P3
  hypothesis #2 (incomplete wetting).
- **Need:** a *measured*, saturation-resolved retention curve θ(ψ) (and K_r(θ/ψ)),
  or fitted van-Genuchten / Brooks–Corey (α, n, θ_r, θ_s) with real units — **NOT**
  a wetting-front position trace. Full acceptance criteria + negative filter +
  search strategy in `docs/cards/g1_retention_search_target.md`.
- **Status:** OPEN SEARCH — no COFFEE source identified. This is a soil-physics /
  porous-media literature hunt (pressure-plate/centrifuge retention; NMR/MRI
  moisture profiling; µCT saturation segmentation on coffee), not a known drop.
- **2026-07-12:** Reference-strength glass-bead analog now on disk
  (`g1_glassbead_analog/`, gated `gate_g1_glassbead_closure_sane`); coffee
  retention search target STILL OPEN.

### 🟡 G3 — measured pump characteristic
- **Unblocks:** RC-3 machine mode (currently rests on a *nominal* manufacturer
  quadratic; foster2025_2 + waszkiewicz supply only one rig each).
- **Need:** a real pump/flow bench curve, DE1 preferred.
- **Status (2026-07-12, 🔴→🟡):** Ulka envelope + DE1-shape context on disk
  (`g3_pump_characteristic/`, gated `gate_g3_pump_envelope_bounds_quadratic`);
  independent DE1 curve needs a TB bench pull or Decent request (new §5.8 line).
  True DE1 Q(P) is closed ESP32 firmware.

### 🟡 G10 — coffee-liquor rheology
- **Unblocks:** the shared early-shot bias across RC-2/RC-3 gates (every
  flow-coupled model on file uses pure-water μ, ρ).
- **Need:** coffee-extract **viscosity & density vs TDS and temperature**.
- **Status (🟡):** Telis-Romero reference envelope on disk
  (`g10_liquor_rheology/`, gated `gate_g10_reference_mu_above_water`).
  **2026-07-12 — second measured source added:** khomyakov2020 MEASURED kinematic
  viscosity grid (15–70 wt% × 20–80 °C, CC BY 3.0) →
  `g10_liquor_rheology/khomyakov2020_kinematic_viscosity.csv`, loader
  `khomyakov_kinematic_viscosity`, smoke-tested, card `khomyakov2020.md`. Its
  density + dynamic-viscosity **regressions are QUARANTINED** (sign/typeset
  conflicts; `*_FLAGGED/_QUARANTINED.csv`, not loaded). **Still 🟡:** khomyakov's
  15 wt% floor is ABOVE espresso TDS (4–12 wt%) so espresso stays an
  extrapolation; a production espresso μ(T,c) closure still needs a sub-15 wt%
  measured source (Telis-Romero 2000/2001 full tables — Tim institutional drop;
  author-clarification draft in `docs/sourcing/`) and/or a true espresso-TDS
  measurement for independent strength.

### 🔴 G2 — transient-discharge validation data
- **Unblocks:** G2 mass-conserving 5-state mobile-fines transport (fasano2000_partI
  is a 3-state skeleton with every parameter unidentified; ellero2019 was skipped
  as a component).
- **Need:** **ASIC 1993/1997 Petracco/Bandini** transient-discharge proceedings;
  and/or **Ellero & Navarini, J. Food Eng. 263 (2019)** raw discharge series.
- **Status (🔴, but no longer a blind search — 2026-07-12):** the ellero2019
  **primary source is located** (open institutional PDF; supplies the direct/inverse
  forcing schedule + τ_v=0.16 s + a plotted experimental overlay) — but **NOT a
  raw-data release**; the points are embedded in a figure and the ASIC 1993/1997
  proceedings remain hard to obtain. So G2 is now a **defined acquisition/
  digitization task**: request raw series from Ellero/Navarini/ASIC/illy AND
  digitize the 2019 overlay as a labelled fallback (never call digitized points
  raw). Source notes + digitization template + request path in `docs/sourcing/`
  (`G2_TRANSIENT_DISCHARGE_SOURCE_NOTES.md`, `g2_..._digitization_template.csv`).

### 🟡 0.6 — Wadsworth raw 22-sample PSD zip
- **Unblocks:** full `pack_generator` PSD-prior validation. **Does NOT block 1.5**
  (its gate uses Table 1, already in `wadsworth2026/`).
- **Need:** the R / R_min / R_max distributions for all 22 grinds.
- **Status:** PENDING AUTHORS — not published with the paper (R. Soc. Open Sci.
  13, 252031; RS is Cloudflare-403 here; not on figshare/Dryad). Tim requested it
  2026-07. **Drop when received →** `puckworks/data/wadsworth2026_psd/`.

---

## Tier 2 — exists but not yet intaken (transcription/drop)

### ✅ 0.8 — bruno2026 Table 2 — RESOLVED (2026-07-12)
- Transcribed from the open CC BY 4.0 article (Sci. Rep. 16, 15857) →
  `data/bruno2026/` (long + wide), loaders `bruno_roasted_composition`/`_wide`,
  MANIFEST row, smoke test. Data-only inventory prior for G6/A4 (never
  Bruno-ODE → extraction, per card). **The last outstanding transcription item.**

*Note:* the SPRINTS `[ ]` checkboxes for egidi2024, romancorrochano (4.9/4.10/6.1),
mo2023, liang2021, foster2025_2, and fasano are **stale** — each has working
loaders and gated components (data already on disk). With bruno2026 done, **no
transcription item remains outstanding**.

### Acquisition instruments on disk (`docs/sourcing/`)
For the still-blocked items, ready-to-send request drafts + measurement schemas
are preserved so they are one step from acquisition (do NOT auto-send):
- **G1** — experiment protocol, retention-measurement CSV schema, author-request
  email (G1 is an experiment-design task, not a web search).
- **G3** — DE1 pressure-sweep bench protocol, Q(P) CSV schema, Decent request.
- **G2** — ellero2019 source notes + digitization template + ASIC/illy request.
- **G10** — khomyakov density-sign author-clarification email; Telis-Romero targets.
- **0.6** — Wadsworth PSD-ZIP follow-up email.
- Provenance: `BLOCKED_INTAKE_SOURCING_REPORT.md`, `SOURCE_MANIFEST.csv`,
  `TIER3_LEADS.md`.

---

## Tier 3 — optional upgrades (correspondence not yet sent; all have fallbacks)

None block a gate. From ROADMAP §5.8:

- 🟢 **Wadsworth group** — segmented XCT volumes (fallback: published PSD moments).
  *Awaiting reply.*
- 🟢 **Mo / Ellero group** — microCT volumes, SPH params, **k₁-units clarification**
  (§5.3 caveat live). Fallback: use k^D only.
- 🟢 **Grudeva** — vial raw data + forthcoming experimental companion → upgrades
  RC-2 from post-fit to `gated + data`. Check the GitHub repo first.
- 🟢 **Egidi group** — ρ and φ_s definitions in Eq. 4 (blocks *quantitative*
  EY-gate use of Eq. 4; bracket use is fine).
- 🟢 **Foster group** — raw CT time series (not critical; figures digitizable).
- 🟢 **Fasano-era illy / ASIC** — Eq. 8.2 a,b,c coefficients (fallback: digitized
  Figs 8.1/8.4, qualitative). Same source as the G2 transient-discharge data.

---

## ✅ Resolved (kept for provenance)

- **0.1 Schmieder / Pannusch** — Schmieder kinetics DONE (Tim drop 2026-07-10:
  Foods 12, 2871 suppl. + XML → `schmieder2023/`). Pannusch Mendeley repo on
  disk (gitignored); Table 2 params parsed via item 1.8a
  (`pannusch2024/table2_fitted_params.csv`).
- **1.5 grind-map** — full Table 1 dropped → `wadsworth2026/`; `grindmap` landed
  & gated; card β,R₀ typo corrected 2026-07-11 (5.805e-5 / 1.380e-4, R²=0.994).
  (Raw 22-PSD zip is the still-pending 0.6 item above.)
- **D4 angeloni2023** — full 66-shot intake (Tim xlsx drop): bioactives / total
  solids / lipids / inventories → 4 loaders + manifests. First independent
  multi-species target for pannusch2024. (MDPI-blocked chemistry was the block;
  the drop resolved it.)
- **Card provenance** — `wadsworth2026_grindmap.md` and the permeability paper
  share DOI `10.1098/rsos.252031`: one paper covers both. No card error.
