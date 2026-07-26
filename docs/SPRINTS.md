# docs/SPRINTS.md — development sprints (rev. 1, from ROADMAP rev. 2)

Each sprint ≈ one Claude Code session (S items may pair; M items stand alone).
Definition of done, every sprint: gates green (`pytest -v`), manifest rows for
any data, registry entries for any component, ROADMAP §7.1 + this checklist
updated, one commit per item. Venue key: **CC** = Claude Code in repo ·
**INTAKE** = card project conversation · **CHAT** = analysis session ·
**TB** = Tim task (correspondence etc.).

## Sprint 0 — plumbing (CC, done when this file exists in repo)
- [x] Commit `docs/ROADMAP.md` (rev. 2), `CLAUDE.md`, `docs/SPRINTS.md`
- [x] Create `puckworks/data/MANIFEST.csv` header per ROADMAP §3 manifest rule
- [x] Add `validation/slow/` stub with README (what belongs there vs CI)

## Sprint D1 — public-data intake, priority 1 (CC) [items 0.1, 0.2, 0.6]
- [x] 0.1 Schmieder/Pannusch: Mendeley kinetics + Tables A1/2/3 + S1 fractions
      — Tim dropped Foods 12,2871 supplementary + XML → `data/schmieder2023/`
      (Tables A1/2/3 + S1/S2 parsed exact; Exp7 == card). Pannusch Mendeley repo
      on disk (gitignored); its Table 2/PSD deferred to 1.8a. Loaders + 3 smoke
      tests + 6 manifest rows.
- [x] 0.2 Waszkiewicz: Zenodo traces ×11 P, TDS fractions, calib curve, brewer quadratic, PSD
      — Zenodo 10.5281/zenodo.18046315 pulled → `data/waszkiewicz2025/`;
      loaders + smoke tests + 7 manifest rows.
- [~] 0.6 Wadsworth PSD zip (22 samples); record the 8.1e-17 erratum
      — erratum recorded + Table 1 manifest row added; **PSD zip not published
      with paper → Tim requested from authors** (pending). 1.5's gate uses
      Table 1 (in repo), so 1.5 not hard-blocked.
- DoD extra: manifest rows incl. validation-strength column; loader smoke tests
- Note: Zenodo/Mendeley may need Tim to download and drop files if CC's network blocks them
- ✅ grindmap card DOI == permeability DOI: Tim confirms ONE paper covers both (resolved)

## Sprint D2 — transcriptions (CC) [0.3, 0.5, 0.7-tables, 0.8, 0.10]
- [ ] egidi2024 Tables 1–3 · romancorrochano Table 6.1 + 4.9/4.10 ·
      grudeva Table 3.1/3.2 + param sets (flag P_app typo) · bruno Table 2 ·
      moroney Table 1
- DoD extra: known-typo entries (§5.7) carried into manifest caveat column

## Sprint D3 — digitizations (CC or CHAT for figure reading) [0.4, 0.9, 0.11, 0.12]
- [ ] mo2023 Tables 1–5 + Fig. 8a — **k1-units caveat column mandatory (§5.3)**
- [ ] liang2021 Figs. 3–5 · foster2025_2 Figs. 6/8/12–15 + Tables I/II ·
      fasano Figs. 8.1/8.4 (flag qualitative)

## Sprint D4 — angeloni2023 multi-species intake (data-only) [DONE]
- [x] cards committed: `angeloni2023` (data-only), `egidi2018` (skip)
- [x] Table 7 inventories → `data/angeloni2023/inventories.csv` (16 rows) + loader
- [x] Tables 2–5 (Tim dropped the xlsx) → `bioactives.csv` (66 shots × 11 species,
      joined to Table 1 conditions + on/off-grid flag), `total_solids.csv`,
      `lipids.csv` (66 each) + loaders + 4 MANIFEST rows + smoke tests
- [x] `gate_angeloni_multispecies_bracket` (`validation/slow/angeloni_bracket.py`,
      slow/not CI): TS/TDS bracket — cameron reproduces the finer→higher grind
      ordering but reads ~2–4 TDS pts **LOW** vs angeloni (0/3 bracketed), the
      SAME direction as the egidi bracket → **Cameron-reads-low confirmed on a
      2nd independent dataset**. Report-style (misses are the finding).

## Sprint D5 — visualizer.coffee harvester + intake (CC, data-only tool) [DONE]
*Phase-0 data intake + ingestion tool — NO registry component, NO physics gate
(CLAUDE.md rule 1 governs components; a harvester is tooling). Item 0.13.*
- [x] (A) `puckworks/lib/visualizer_harvest.py` — new `puckworks/lib/` subpackage;
      HarvestConfig + list/fetch/normalize + harvest_all/incremental + stats;
      `requests` behind the new `[harvest]` extra (lazy import; core imports
      without it). Rate-limited ≤30 req/min, exp-backoff on 429/5xx, resume
      cursor + `--max-requests`, gzip-JSONL shards + `_index.csv`.
- [x] (A) two-tier `normalize_shot`: SEPARATE hydraulic / outcomes tiers; SI at
      the boundary + per-channel units block; missing/off-unit FLAGGED (rule 7);
      privacy drop (user/notes gone; salted user-id hash only).
- [x] (B) `data/visualizer/PROVENANCE.md` (tracked) — source/scope, privacy,
      license posture (corpus not redistributed; §5.8), the field map.
- [x] (C) loaders `visualizer_index` / `visualizer_iter_shots` (degrade cleanly;
      raise "run the harvester" when absent) / `visualizer_hydraulic` /
      `visualizer_outcomes` (SI accessors, rule-7 asserts).
- [x] (D) `stats --write-aggregate` → DERIVED `aggregate_stats.csv` (tracked;
      counts/mixes/histograms/unit-audit, NO per-shot rows) — committed zero-state,
      Tim refreshes after a local `full`.
- [x] (E) `tests/test_visualizer_harvest.py` + 3 synthetic fixtures — offline
      only, tier split / privacy / units / missing→null+flag / loader degrade;
      NOT in run_all_gates.
- [x] (F) two MANIFEST rows (`visualizer/hydraulic_timeseries` reference-strength
      population; `visualizer/user_outcomes` not-groundtruth), tiers separate.
- [x] (G) data-only card `docs/cards/visualizer_coffee.md` (verdict data-only).
- Corpus is **not** populated in-repo (gitignored, no license to redistribute):
  Tim runs `python -m puckworks.lib.visualizer_harvest full` locally, then
  `stats --write-aggregate` to refresh the tracked CSV.

## Sprint 1 — first components (CC) [1.2 + 1.5, both S; needs D1]
- [x] 1.2 waszkiewicz2025 poroelastic κ(P,Φ) — refit (Q_c,P_c)=(1.90,12);
      9-bar Q(t) with zero extra params (RC-3a scope only)
      → `waszkiewicz2025.poroelastic` registered; 2 gates green (static refit
      == (12.39,1.897); 9-bar Q(t) parameter-free long-run 1.6% / corr 0.982).
- [x] 1.5 wadsworth2026_grindmap — refit β,R0; S(G) monotonicity; A9 adapter stub
      → `wadsworth2026.grindmap` registered (calibration/grind); 2 gates green.
      Tim dropped the full Table 1 → `data/wadsworth2026/`. Refit ⟨R⟩=βG+R₀
      (R²=0.994); S=⟨R⟩⟨R²⟩/⟨R³⟩ reconstructs reported S (<5e-3); S(G) rises
      0.46→0.78; A9 dial-space adapter stub (guards cross-grinder porting).
      ✅ **card β,R₀ typo corrected 2026-07-11** to 5.805e-5/1.380e-4 (was
      4.3505e-5/1.016e-4); card == component now. Raw 22-PSD zip still pending (0.6).

## Sprint 2 — inertial flow (CC) [1.1, S; needs D3-mo + ledger A7]
- [x] A7: FlowLaw/k_I contract fields + strict SI assertion
      → `contracts.FlowLaw` + `assert_si_permeability` + `BedState.k_I_m`;
      SCHEMA_VERSION 0.1→0.2 (additive).
- [x] 1.1 wadsworth2026_inertial — reproduce Fo_F band 0.0161–0.0639;
      Darcy recovery k_I→∞; **§5.2 shared-dimensional audit table on DE1
      fixture A** (this gate settles the three-way regime disagreement)
      → `wadsworth2026.inertial` registered; 3 gates green. Band 0.0161–0.0638
      (eq2.7); Darcy recovery exact; **§5.2 settled**: DE1 tamped Fo_F ≈
      0.86 (eq2.8) / 5.7 (eq2.7) — ≫ untamped band, at/past inertial onset
      (backlog 0.3–0.9 side). ✅ **Mo Re overlay done** (0.4 dropped): mo2023
      Fig 8a → Re 0.85–3.85 at SPH conds (`gate_mo_reynolds_overlay`); §5.2 now
      shows all three (backlog Fo~0.3–0.9, wadsworth Fo_F 0.016–0.064, Mo Re
      0.84–3.86) side by side — NOT interchangeable. k₁-units caveat (§5.3) carried.

## Sprint 3 — extraction anchors (CC) [1.3 + 1.4, both S; needs D2/D3]
- [x] 1.3 liang2021 kernels — K·E_max=0.215 refit; E_oven kernel;
      long-time cameron ceiling probe (§5.5)
      → `liang2021.desorption` gated (Tim dropped Figs 3/4/5). K·E_max refit
      0.219 from Fig3; E_oven kernel MAPE 0.088 vs Fig4; §5.5: equilibrium
      ceiling 0.215 < cameron inventory 0.245 (K<1, distinct quantities).
- [x] 1.4 moroney2016 surrogate — Fig. 6 reproduction; mutual-validation vs
      cameron BDF at matched limit
      → `moroney2016.surrogate` gated (Table 1 transcribed; Fig6 digitized).
      Leading-order composite reproduces plateau + wash-through (c=½ at t≈3.1
      vs data 3.1); **qualitative** — tail needs outer soln (not on card).
      ⚠ cameron-BDF mutual-validation = **regime-blocked**: the two models sit in
      different regimes (Cameron espresso ε≈1.6, clean-water IC; Moroney JK-drip
      ε≈0.13, saturated IC) — a clean cross-solver overlay needs matched-parameter
      alignment (CHAT/research), not a mechanical gate. Fig-6 gate stands.

## Sprint 4 — Grudeva reconciliation (INTAKE, not CC) [1.7a, S]
- [x] Resolve card-of-record vs CUP open-access source: Eq. 74 brackets;
      thesis-vs-paper parameter identity; vial-vs-verification configs;
      φ_lb=0 ruling. Output: merged card of record → commit; §5.1 resolved → §7.2
- Blocks Sprint 5. This is source-reconciliation work — do it in the card
  project with both documents, not in the repo.
- Done: `grudeva2025.md` card of record committed (retired grudeva2023/2026);
  adjudicated no-ε form; two named configs; emergent κ/P_app decade-error
  finding (κ ≈ 2.2e-15). §5.1 → §7.2. Sprint 5 unblocked (G0 first).

## Sprint 5 — Grudeva reduced model (CC) [1.7b, M; needs Sprint 4, A5/A6]
- [x] G5-pre: contracts.py — add fines_radius_m to GrindState (additive), bump SCHEMA_VERSION to 0.3 (0.2 already used by A7)
- [x] Mass budget (verification) · Fig. 4/5 ε-convergence (verification) ·
      per-vial masses within 1 SD (post-fit — label) · first-drip vs foster2025
      on fixture A (independent, weak) → **creates RC-2, verification-gated**
      → `grudeva2025.reduced` registered (**faithful port of the released
      reference solver** — G0: capacitance carries NO ε, confirming the
      adjudication). Gates: (G2) solute budget total 2.92 g vs exp 2.95 g;
      (G3) per-vial masses 9/13 within 1 SD (post-fit); (G4) κ Eq6.14@9.2bar
      = 2.27e-15 == adjudicated. Slow ladder: resolution-converged s_d⁻¹(1)≈2.82;
      **ε-form discrimination** (no-ε plateau 2.83/2.96 g vs printed-ε 0.44/2.52 g
      — LOG Issue 1). Vial data from reference repo `exp13.csv`.
      ⚠ V1 (φ_l/φ_T=1) config numerically stiff in explicit boulder scheme —
      café config (anchored to exp13) carries the demonstration.

## Sprint 6 — multi-solute extraction (CC) [1.8a, M; needs D1, A3/A6]
- [x] pannusch2024 measured-flow solver — fit MAPEs (post-fit) + temperature
      set (independent); quarantine flow-regime + CGA confound → **creates RC-4a**
      → `pannusch2024.closures` (constitutive slice) **and** `pannusch2024.solver`
      (full 1D two-grain multi-solute PDE, method-of-lines 5-pt biased upwind +
      BDF) both gated, **faithful ports of the released MATLAB**. Reproduces the
      fit MAPEs vs Schmieder kinetics: **TDS 6.7 / caffeine 6.4 / trigonelline
      10.2 / CGA 7.2 %** (published 6.07/4.59/7.85/4.98; post-fit). exp7 caffeine
      single-solve MAPE 3.9%. Constituent-part unit tests (FD exactness,
      Jacobian sparsity, single-exp). Slow ladder: per-exp breakdown + resolution.
      ⚠ centre-grind (1.7) for all exps (per-exp grind in opaque source list;
      <15% ψ/d_s2 spread → 2nd-order). **RC-4a created.**

## Sprint 7 — machine mode (CC) [1.6, M; needs A1 + D3-foster]
- [x] A1 pressure-node fields (p_p/p_h/P_basket/ΔP_bed) per RC-3 node table
      → `MachineState` p_p/p_h/P_basket/dP_bed + `PumpHeadspace`; SCHEMA 0.3→0.4.
- [x] foster2025_2 Eqs. 2–7 — t_p=0.823 s, t_s=6.669 s, Fig. 15 flow-minimum
      (post-fit); DE1 first-drip triangle rerun (independent) → **RC-3a runnable**
      → `foster2025.machine_mode` gated (3 gates). t_p=0.823/t_s=6.665; **Fig 15
      flow-minimum reproduced** (Q/Qm=0.181 @2s, RMSE 1e-4) = P2 null baseline;
      s(t)/H(t) match paper fitted curves to line width + bracket 4-5/8 CT points
      (Figs 12-14). Fig 15 Q_norm = bed flow min(Qp,f)/Qm (Eq 18), not pump flow.
- [x] §5.9 pressure-node identification for fixture A + Waszkiewicz recorded in manifests
      → Waszkiewicz basket_pressure=P_basket / pressure=line; DE1 node open.
- [x] 1.8b (S): pannusch machine-driven adapter → RC-4b
      → `pannusch2024.solver.simulate_fractions_qt` (A2): time-varying Q(t) input
      (Sherwood + advection recomputed per step). `gate_pannusch_qt_adapter`:
      reduces to RC-4a exactly on constant flow (0.0 rel err); a +15% flow ramp
      shifts the prediction 6.6% → the adapter is live. **RC-4b created.**

## Sprint 8 — extraction harness (CC+CHAT) [2.1, M; needs Sprints 3,5,6 + A5]
- [x] Matched-input runs: cameron/grudeva/pannusch(TDS) vs Cameron tables,
      egidi bracket, Schmieder kinetics, Grudeva vials, Waszkiewicz fractions —
      per-dataset residuals with strength tags; §5.6 dissolution-speed test
      → `puckworks/harness.py` + `gate_extraction_harness` + slow full report.
      Surfaces P1 hazards (c_sat {170,212.4,224} NOT merged, §5.4; per-model
      inventory ref, A5); per-dataset residuals tagged (pannusch→Schmieder
      post-fit MAPE, grudeva→vials post-fit, liang→cameron §5.5 independent).
      **§5.6 settled**: Waszkiewicz TDS early/peak=0.968 → **near-instant
      dissolution** (vs cameron diffusion-limited; τ_boulder≈23 s).
      ✅ **egidi bracket done** (0.3 dropped): `data/egidi2024/table2` + harness +
      `gate_egidi_bracket` — RC-1 EY bracket 19.1–22.6%; cameron reads ~15%
      (below the bracket — documented, reported not asserted). Cameron's own
      flux/microstructure data (**SI Tables S1–S5**, not "Tables 2/7/8") is in
      `extraction_bdf.py` and cameron is gated on its mass budget — no drop needed
      there; a Fig. 5 EY-curve gate is still optional.
- [x] P3 hypothesis file (2.3, docs part): `docs/P3_hypotheses.md` — the
      5-hypothesis registry with current component/harness evidence.
- [x] CHAT: results workup + P3 verdict → `docs/ANALYSIS_P2.md` (§2.1, §2.3)

## Sprint 9 — κ(t) discrimination harness (CC+CHAT) [2.2, M; needs Sprints 1,7 + A8]
- [x] A8 per-depth-cell porosity/fines fields
      → `BedState.porosity_profile / fines_mobile / fines_bound`; SCHEMA 0.4→0.5.
- [~] P2 null-first ladder implementation on Waszkiewicz + fixture-A traces;
      RC-3b enters as rung 5
      → `harness.kappa_t_ladder()` + `gate_p2_kappa_ladder`. On the Waszkiewicz
      9-bar RISING flow: **rung 4 Φ(t) (RMSE 0.113) beats the flat null rungs
      1/3 (0.603) by 5.4×** → a bed mechanism IS needed. Rung 2 = foster
      flow-minimum null (validated separately). **Rung 5 RC-3b + rung 5b swelling
      wired; discrimination now sign-decisive (2026-07-12):** the matrix-resistance
      challengers (mo2023_2 swelling RMSE 1.082 / r=−0.95; fasano I fines-migration
      by Lemma 8.3) predict the WRONG SIGN → refuted; dissolution-Φ(t) survives.
      fasano II parameter-blocked, lee2023 off-observable (declared).
- [x] CHAT: which mechanism survives → `docs/ANALYSIS_P2.md` (§2.2; verdict **partial but sign-decisive** — Φ(t) fits and is the only correct-sign branch; swelling + fines-migration refuted by sign; fasano-II blocked / lee2023 off-observable; fines-vs-dissolution quant. discrimination awaits the pressure-step/reversal protocol)

## Sprint V1 — visualization layer (CC, tooling) [DONE]
*A CONSUMING viz layer (`puckworks/viz/`, ROADMAP §8) — NO registry component,
NO physics gate. Item 8.1.*
- [x] viz skeleton: `spec.py` (VizSpec + `.validate()` + FIDELITY_CEILINGS),
      `palette.py`, `registry.py` (10 VIZZES + badge/provenance `stamp_fig` +
      `write_gallery`), `producers.py`; `[viz]`/`[viz3d]` lazy extras.
- [x] class-1 diagrams (process schematic, shot metric frame, κ(t) ladder,
      identifiability valley) routed through the SAME producers as the paper
      figures — `figures.py` untouched, Paper-B PNGs unchanged.
- [x] class-2 renders (Stokes verification field, synthetic pack + heterogeneity
      field, wetting front, channeling one-config, fines-migration mechanism;
      pyvista 3D behind `[viz3d]`).
- [x] PV-09 `hidden_puck_movie` — parallel labelled lenses on one shared clock
      (display only), each its own badge; NOT a mega-model.
- [x] `tests/test_viz.py` (9, offline, NOT in run_all_gates): honesty contract,
      anti-fabrication rejection, badge-stamp-present, ceiling coverage, and the
      acceptance test (generated `GALLERY.md` reproduces `GALLERY_SEED.md`).
- [x] Heavy renders gitignored; thumbs + `data.json` + `GALLERY.md` tracked.
- Each P0 public story gets a bound visual: PV-01/PV-02 → shot_metric_frame +
      wetting_front; PV-03 → identifiability_valley; PV-04 → the ladder; PV-05 →
      (composition diagnostic, future); PV-06 → channeling/shot lenses.

## Parallel tracks (not sprint-gated)
- **TB**: §5.8 correspondence — Mo/Ellero (k1 units + volumes), Grudeva
  (repo check first), Egidi (Eq. 4 definitions); Wadsworth already out; PV-19
  capstone shot — pull the named shot (DE1, EK43 dial 1.7, 20/40, Schmieder-matched
  coffee, per-shot κ refit) and measure cup TDS + caffeine/trigonelline/CGA (fractions
  if feasible); promotes RC-4b. **Miha Rekar (miha@visualizer.coffee)** — sanctioned
  research/bulk use of the visualizer.coffee shot corpus (§5.8): **SENT 2026-07-13 by
  Tim, awaiting reply**; the public API harvest is already in place (0.13), this gates
  redistribution/publication use.
- **INTAKE**: gap-target papers as found — G1 (Richards/two-phase), G2
  (Ellero J. Food Eng. 263; Mo 2021/2022), G9 (screen hydraulics), ~~G10
  (extract rheology)~~ **✅ CLOSED 2026-07-15** (Telis-Romero 2000/2001 cards +
  Table 1/2 drop + μ(c,T) sensitivity study → negligible-at-shot-TDS)
- **Colab / local**: full-grid Sweeps A/B (already queued); results → CHAT workup.
  Also the HEAVY/3D/video viz renders (`python -m puckworks.viz render --with-3d
  --video`, ROADMAP §8) run locally or in Colab — like the LB sweeps, NEVER in CI.
- Phase 3 items (3.1–3.5) schedule after Sprint 9 defines the harness

## Public-value track (PV)
*Parallel workstream to the scientific sprints above. **Spec:** `docs/PUBLIC_VALUE.md`
(this table is the status ledger, PUBLIC_VALUE.md stays the spec — do not duplicate
its content here). **Guardrails:** PUBLIC_VALUE.md §3 are binding; every public
claim regenerates from a pinned commit and carries its evidence-strength label
UNCHANGED (measured / post-fit / verification / qualitative). Reference-strength and
labelled-proxy results stay labelled in public form.*

**Present state (2026-07-18).** The public-value layer is no longer empty: **PV-00**
(the public-results export + claim registry) is **complete**, **PV-03** "The Cup Hides
the Clock" is **complete and live** on GitHub Pages, and the **Guided Espresso Pull**
shipped in **v0.3.0** (signed-out human Colab acceptance pending under issue #48).
**PV-05** ("More Physics Made It Worse") is **complete and live**
(trbrewer.github.io/puckworks/model-composition/); **PV-04** (the analysis
autopsy) is now **complete and live**
(trbrewer.github.io/puckworks/analysis-autopsy/, issue #62). No next PV product
lane has been authoritatively selected — selection is pending. All other PV items
remain not started.

Sequence tiers from PUBLIC_VALUE.md §17. "Sci-dependency / coupling" is the
load-bearing link that keeps the two tracks in sync: **a change on the scientific
side flags the coupled PV row, and vice versa.** Shared items are named so they are
not worked twice under two names — **PV-13 / PV-17 / PV-18 are the PUBLIC face of
gaps G10 / G3 / G1.**

| PV | short name | status | tier (§17) | depends-on | sci-dependency / coupling | spec |
|---|---|---|---|---|---|---|
| PV-00 | public-results export + claim registry | complete | now | — (foundation) | `harness.py` public-ready fns + `figures.py` + registry/manifest provenance; **the viz layer (§8) CONSUMES this claim/producer registry — VizSpecs bind to public.schema.Producer** | [§5](PUBLIC_VALUE.md#pv-00--build-a-public-results-export-and-claim-registry) |
| PV-01 | "the first drop is already strong" | not-started | now | — (pairs w/ PV-16) | `dissolution_speed_test` + foster2025_2 infiltration + fraction TDS; **G1 retention analog is REFERENCE-strength — label rides along** | [§5](PUBLIC_VALUE.md#pv-01--the-first-drop-is-already-strong-measured-fractions-plus-a-wetting-front-reveal) |
| PV-02 | "the machine can fake a puck problem" | not-started | now | — (feeds PV-15) | Foster machine mode + `kappa_t_ladder` + `cross_pressure_discrimination` + the leave-one-pressure-out diagnostic (`ANALYSIS_cv_residual.md`) | [§5](PUBLIC_VALUE.md#pv-02--the-machine-can-fake-a-puck-problem-a-null-first-flow-curve-explainer) |
| PV-05 | "more physics made it worse" | complete (live) | — | — | `coupled_kappa_t` failed shared-porosity composite (anti-mega-model; Paper-B Fig 4); static interactive via `public.model_composition`; live at trbrewer.github.io/puckworks/model-composition/ | [§5](PUBLIC_VALUE.md#pv-05--adding-more-physics-made-it-worse-the-anti-mega-model-story) |
| PV-03 | "a good fit can still be wrong" | complete (live) | — | — | `ANALYSIS_transfer.md` inventory–kinetics identifiability (flat valley); Pannusch solver, Angeloni; live at trbrewer.github.io/puckworks/flat-valley/ | [§5](PUBLIC_VALUE.md#pv-03--a-good-fit-can-still-be-wrong-the-inventorykinetics-flat-valley-interactive) |
| PV-04 | "we killed our favorite result" | complete (live) | — | — | corrected fine-grind verdict (`ANALYSIS_P2.md` / `P3_hypotheses.md`); `result1_magnitude_comparison` -> `public.analysis_autopsy`; live at trbrewer.github.io/puckworks/analysis-autopsy/ | [§5](PUBLIC_VALUE.md#pv-04--we-killed-our-favorite-result-a-transparent-analysis-autopsy) |
| PV-06 | cross-pressure mechanism fingerprint | not-started | next | — (feeds PV-15) | waszkiewicz 11-pressure traces + `cross_pressure_discrimination`; Paper-B Fig 3; **visualizer.coffee is the at-scale ECOLOGICAL companion (0.13) — reference-strength, selection-biased; label rides along, does NOT upgrade** | [§5](PUBLIC_VALUE.md#pv-06--build-a-cross-pressure-mechanism-fingerprint-map) |
| PV-08 | "Puck Court" evidence dashboard | not-started | next | PV-00 | registry + gates + manifest; Paper-B Fig 2 (evidence matrix, not a leaderboard); **renders VizSpecs (§8), not a leaderboard** | [§5](PUBLIC_VALUE.md#pv-08--create-puck-court-a-public-evidence-dashboard-not-a-winner-leaderboard) |
| PV-15 | model-disagreement experiment recommender | not-started | experiment | PV-02, PV-06 | consumes cross-mechanism disagreement across the harnesses | [§5](PUBLIC_VALUE.md#pv-15--build-a-model-disagreement-experiment-recommender) |
| PV-16 | public first-drip / fraction replication | not-started | experiment | PV-01, PV-15 pilot | PV-01 protocol → public participation (after closed pilot) | [§5](PUBLIC_VALUE.md#pv-16--launch-a-public-first-drip-and-fraction-resolved-replication-study) |
| PV-11 | "your grinder dial is not a unit" | not-started | program | — | G5 dial-non-portability gap + Wadsworth grind map (ledger A9/G5, rule 9) | [§5](PUBLIC_VALUE.md#pv-11--your-grinder-dial-is-not-a-unit-build-a-physical-grind-translation-study) |
| PV-13 | measure espresso-liquor viscosity | not-started | program | — | **PUBLIC FACE of gap G10** (liquor rheology); current G10 is REFERENCE-strength extrapolation — label rides along | [§5](PUBLIC_VALUE.md#pv-13--measure-espresso-liquor-viscosity-the-first-drops-are-not-just-hot-water) |
| PV-14 | dynamic channeling, flow vs pressure | not-started | program | — | `ntube_finite_time_gain`; **BOUNDED by the lateral-coupling PROXY (CARD-BLOCKED, rule 1) — cannot claim physical lateral coupling until a card exists** | [§5](PUBLIC_VALUE.md#pv-14--visualize-dynamic-channel-concentration-under-flow-versus-pressure-control) |
| PV-17 | pump-curve + screen-clogging bench | not-started | program | (validates PV-10) | **PUBLIC FACE of gap G3** (pump curve); also feeds G9 screen-clogging (`g9_series_resistance`); **visualizer.coffee is its at-scale ECOLOGICAL companion (0.13) — the controlled bench pull calibrates the uncontrolled population's selection bias; label rides along** | [§5](PUBLIC_VALUE.md#pv-17--measure-the-machine-and-outlet-pump-curve-plus-screen-clogging-bench-study) |
| PV-18 | coffee-bed retention / continuous wetting | not-started | program | — | **PUBLIC FACE of gap G1** (retention curve θ(ψ)/K(ψ)); the measurement that would replace the reference-strength G1 analog PV-01 uses | [§5](PUBLIC_VALUE.md#pv-18--measure-continuous-coffee-bed-wetting-and-retention-not-just-the-front) |
| PV-07 | compound extraction clocks | not-started | unsequenced (P1) | — | Pannusch solver + Schmieder fractions + transfer analysis (hypothesis generator only, transfer-limited) | [§5](PUBLIC_VALUE.md#pv-07--build-compound-extraction-clocks-and-search-for-same-strength-different-composition-shots) |
| PV-09 | multi-lens "hidden puck" movie | not-started | unsequenced (P1) | — | Foster infiltration + pack_generator + LB solvers + extraction + streamtube/N-tube (parallel labelled lenses, no fake mega-model); **the montage IS the viz `hidden_puck_movie` VizSpec (§8) — thumb built, video local** | [§5](PUBLIC_VALUE.md#pv-09--produce-a-multi-lens-hidden-puck-movie-without-building-a-fake-mega-model) |
| PV-10 | "a clean basket is not the bottleneck" | not-started | unsequenced (P0/P1) | — | `g9_series_resistance` + basket geometry (gap G9); PV-17 provides the bench validation | [§5](PUBLIC_VALUE.md#pv-10--a-clean-basket-is-not-the-bottleneck-visualize-the-pressure-resistance-budget) |
| PV-12 | temperature explainer | not-started | unsequenced (P1) | — | `g4_temperature_sensitivity` + Schmieder temperature data (gap G4; two closures disagree on SIGN — surface, don't average) | [§5](PUBLIC_VALUE.md#pv-12--temperature-explainer-small-equilibrium-extraction-effect-unresolved-thermal-puck-physics) |
| PV-19 | "the best-understood espresso shot" (named-shot capstone scorecard) | Guided Pull shipped v0.3.0 (acceptance pending #48); capstone scorecard not-started | next | PV-00 | RC-1 + RC-4a gates, 1.8b adapter (RC-4b verification), §5.9 node identity, §5.2 Fo_F audit, Cameron low-read (egidi/angeloni brackets); **TB capstone cup measurement would promote RC-4b** | [§5](PUBLIC_VALUE.md#pv-19--the-best-understood-espresso-shot-one-named-recipe-every-component-evidence-attached) |
| PV-20 | "why you can't just bolt every espresso model together" (model-interoperability audit + mega-model article) | not-started | next candidate (P0/P1) | PV-00; audited Relay provenance | Espresso Model Relay manifest + runtime `LinkRecord`s + A01–A12 assumption ledger + model cards + unit/basis contracts + PV-05 + PV-19; **public article now, academic home pending a Paper-3 overlap audit**; compatibility audit must run on the STABILIZED Relay (software defects are not physics incompatibilities) | [§5](PUBLIC_VALUE.md#pv-20--why-you-cant-just-bolt-every-espresso-model-together-an-interoperability-audit-and-a-path-to-a-unified-framework) |
| PV-21 | "which espresso controls actually move the modeled cup?" (candidate) | not-started | candidate (program) | RP-A schema; valid-range/observable audit | PUBLIC face of **RP-C** global sensitivity & decision-relevance (ROADMAP §9 research programs, scheduled backlog); consumes the RP-A response atlas; per-model rankings, **no pooled leaderboard**, evidence labels ride along | [§5](PUBLIC_VALUE.md#pv-21--which-espresso-controls-actually-move-the-modeled-cup-candidate) |

## Research-program backlog (scheduled; NOT in the current sprint)
*Session-sized candidate slices for the six research programs captured in ROADMAP §9
(RP-A…RP-F). **Full scope lives in ROADMAP §9, not here.** None of these is in the current
sprint or the active queue (`docs/status/current.json`); they schedule in the §9 dependency
order. Documenting a slice does not start, validate, or promote it.*

| slice | program | depends on | effort | next gate / acceptance evidence |
|---|---|---|---|---|
| RP-A.1 parameter/observable/comparability schema + inventory | RP-A | registry valid ranges; §5.9/A1 node + §5.10/A10 observable conventions | M | machine-readable schema artifact; unit + valid-range + determinism tests green; missing-relationship cells explicit |
| RP-A.2 bounded response-atlas pilot (3 components) | RP-A | RP-A.1 | M | per-component response reports + one matched-comparison/disagreement report with comparability tags; tests green |
| RP-B.1 tier→protocol-pack generator over EXP-009 | RP-B | PV-15 contract; campaign schema; `templates/` | M | EXP-009 emits a capability-tier protocol pack with preregistration + submission validator |
| RP-F.1 bottom-filter-paper protocol pack | RP-F | EXP-009 (landed); `templates/` | S | `protocols/protocol_EXP-009.md` with one predeclared primary outcome + design placeholders |
| RP-F.2 filter-paper feasibility pilot (TB) | RP-F | RP-F.1; apparatus + contributor | M | pilot dataset; efficacy and mechanism reported SEPARATELY; treatment-by-control-mode read |
| RP-C.1 global-sensitivity pilot | RP-C | RP-A.1; valid-range/observable audit | M | local + screening rankings reproducible; convergence + ranking-stability checks pass; separate control vs parameter rankings |
| RP-D.1 Taichi Stage-0 architecture + V&V matrix | RP-D | — | S | Stage-0 scope/contracts/card + verification/validation matrix; NO new registered component yet |
| RP-D.2 Taichi Stage-1/2 general geometry + verified 3D hydraulics | RP-D | RP-D.1 | M–L | analytic channel + sphere/porous benchmarks, grid/timestep convergence, CPU/reference cross-check; heavy runs LOCAL/Colab only, never CI |
| RP-E.1 XCT prep interfaces (descriptors, data contracts, baseline fixtures) | RP-E | — | S | descriptor defs + geometry interfaces + baseline synthetic fixtures; NO XCT-conditioned fitting |
| RP-E.2 XCT-conditioned generation | RP-E | **BLOCKED** on §5.8 Wadsworth segmented-XCT scans + rights | M–L | (blocked until data + metadata + rights arrive) |

Public articles (PV-08 / PV-21 / PV-10 outputs) only after reproducible non-trivial or tightly
bounded-null results exist; paper assessment only after novelty + evidence are reviewed.

## Submission track
*Tracking surface for paper/venue submissions. **Spec + deadlines:**
`docs/SUBMISSION_TARGETS.md` (front-edge ledger at its top — do not duplicate its
tables here). **Deadline-bearing:** recheck each portal before submitting; mark a
passed deadline PASSED, never delete. **Readiness gate (PAPER_OUTLINE):** Paper A is
amber–green (journal + conference actionable after manuscript conversion); Paper B is
red (conference ABSTRACT ONLY — journal routes held until the reanalysis /
related-work / physical-lateral-coupling gaps are closed). Abstract wording obeys the
§1 claim discipline. Status: `not-started` / `drafting` / `submitted` / `accepted` /
`declined` / `PASSED`. **All not-started** — no submission actioned yet.*

> ⏰ **APS DFD 2026-07-24 (Paper B abstract) is the nearest action** — ~12 days from
> the 2026-07-12 authoring date. Internal target 2026-07-23.

| venue | paper | deadline | status | owner-note | spec |
|---|---|---|---|---|---|
| APS DFD 2026 (oral abstract) | B | 2026-07-24 | not-started | **actionable NOW** (abstract ≠ manuscript); verb discipline binding | [ledger](SUBMISSION_TARGETS.md#deadline-ledger-front-edge) · [§B1](SUBMISSION_TARGETS.md#b1-aps-division-of-fluid-dynamics-annual-meeting-2026--priority-1-urgent) |
| InterPore 2027 minisymposium proposal | B | 2026-08-14 | not-started | organizer route; recruit 2 co-organizers | [§6.2](SUBMISSION_TARGETS.md#62-interpore-2027-minisymposium-proposal--organizer-route-for-paper-b) |
| CoFE 2026 (abstract) | A / B | 2026-08-15 | not-started | optional; distinct A vs B abstracts | [§A3](SUBMISSION_TARGETS.md#a3-conference-of-food-engineering-2026-cofe--priority-3) |
| SDCC 2026 (oral abstract) | A (+B) | 2026-09-01 | not-started | Paper A priority-1 conference; **shared with PV track** | [§A1](SUBMISSION_TARGETS.md#a1-science-driven-coffee-cup-2026--priority-1) |
| Gallery of Fluid Motion 2026 | B | 2026-09-17 | not-started | public visual companion; **shared with PV track** | [§6.1](SUBMISSION_TARGETS.md#61-aps-gallery-of-fluid-motion-2026--public-visual-companion-to-paper-b) |
| Pittcon 2027 (oral abstract) | A (B cond.) | 2026-09-28 | not-started | analytical-method framing | [§A2](SUBMISSION_TARGETS.md#a2-pittcon-2027-oral-session--priority-2) |
| ACS Spring 2027 | A (B med) | opens 2026-08-03, close 09-28 | not-started | inspect symposia 3 Aug before drafting | [§7.1](SUBMISSION_TARGETS.md#71-acs-spring-2027--opens-3-august-2026) |
| Foods 2027 (abstract) | A / B | 2027-01-24 | not-started | fallback only | [§A5](SUBMISSION_TARGETS.md#a5-foods-2027--priority-5--broad-fallback) |
| *Journal of Food Engineering* | A | rolling | not-started | **first journal**, after manuscript conversion | [§A-J1](SUBMISSION_TARGETS.md#a-j1-journal-of-food-engineering--recommended-first-journal) |
| *Transport in Porous Media* / *Physics of Fluids* | B | rolling | not-started | **HELD** — do not submit until APS DFD feedback + related-work + lateral-coupling done | [§B-J2](SUBMISSION_TARGETS.md#b-j2-transport-in-porous-media--best-pure-scope-fit) |
| World of Coffee 2027 / CSF poster · ASIC 2027 | A / B | TBD (monitor) | not-started | calls not yet posted; watchlist (WoC shared with PV) | [§7.2](SUBMISSION_TARGETS.md#72-world-of-coffee-new-orleans-2027--coffee-science-foundation-scientific-poster-session) |

## Status log
| date | sprint | outcome |
|---|---|---|
| 2026-07-10 | 0 | plumbing: ROADMAP rev.2 → `docs/ROADMAP.md`; `MANIFEST.csv` header; `validation/slow/` stub + README; `.DS_Store` ignored |
| 2026-07-10 | D1 | 0.2 Waszkiewicz Zenodo intake complete (data/waszkiewicz2025/ + loaders + 5 smoke tests + 7 manifest rows). 0.6 partial (erratum + Table 1 manifest row; PSD zip blocked). 0.1 blocked (Mendeley folder / MDPI 403). Blocked items → data/BLOCKED_INTAKE.md |
| 2026-07-10 | D1 | 0.1 Schmieder kinetics landed after Tim drop (data/schmieder2023/: Tables A1/2/3 + S1/S2 parsed from supplementary xlsx + JATS XML; 9 loader smoke tests total). Pannusch repo on disk, Table 2/PSD deferred to 1.8a. 0.6 PSD zip → Tim requested from authors. grindmap==permeability one-paper confirmed. |
| 2026-07-10 | 1 | 1.2 waszkiewicz2025.poroelastic gated (static refit == published; 9-bar Q(t) parameter-free). 1.5 wadsworth2026.grindmap gated after Tim dropped full Table 1 (⟨R⟩=βG+R₀ refit R²=0.994; S(G); A9 stub) — card β,R₀ flagged as non-reproducing. run_all_gates green; 10 loader tests. Sprint 1 done. |
| 2026-07-11 | 2 | A7 (FlowLaw/SI guard, SCHEMA 0.2) + 1.1 wadsworth2026.inertial gated; §5.2 settled (tamped DE1 Fo_F ≈0.86/5.7 ≫ untamped band). Mo Re overlay deferred (0.4). |
| 2026-07-11 | 3 | 1.3 liang2021.desorption + 1.4 moroney2016.surrogate gated after Tim dropped liang Figs 3/4/5 + moroney Fig 6 (+ Table1 transcribed). 13 gates green; 12 loader tests. moroney-vs-cameron mutual-validation deferred. |
| 2026-07-11 | Sprint 4 | complete — merged card committed; 5.1 resolved; emergent κ/P_app decade-error finding; Sprint 5 unblocked, G0 first. |
| 2026-07-11 | Sprint 5 | 1.7b `grudeva2025.reduced` gated (faithful port of released solver; G0 no-ε confirmed). G5-pre contract (fines_radius_m, SCHEMA 0.3). 15 quick gates + slow ladder; 13 loader tests. Creates RC-2 (verification-gated). |
| 2026-07-11 | Sprint 6 (partial) | 1.8a closures slice: `pannusch2024.closures` gated (Wilke-Chang/Sherwood/van't Hoff/water props ported from MATLAB; μ@90C==card). Table 2 params transcribed. Full PDE solver + RC-4a MAPE reproduction deferred. 16 quick gates; 14 loader tests. |
| 2026-07-11 | Sprint 6 (complete) | 1.8a full solver: `pannusch2024.solver` gated — 1D two-grain multi-solute PDE (5-pt biased upwind + BDF, sparse Jacobian), faithful MATLAB port. Reproduces fit MAPEs (TDS 6.7/caf 6.4/tri 10.2/CGA 7.2% vs pub 6.07/4.59/7.85/4.98). Experimental kinetics extracted from ExperimentalData.mat. Constituent unit tests + slow ladder. RC-4a created. 15 components; 17 quick gates; 18 tests (~16s). |
| 2026-07-11 | Sprint 7 (partial) | A1 pressure-node contract fields (SCHEMA 0.4) + `foster2025.machine_mode` verification-gated (t_p=0.823/t_s=6.665 from Table I/II; t_shift offset caught). §5.9 nodes in manifests. Fig 15 + 1.8b pending. 16 components. |
| 2026-07-11 | Sprint 8 (CC part) | 2.1 P1 extraction harness: `puckworks/harness.py` + `gate_extraction_harness` — surfaces c_sat/inventory hazards (no silent merge), tagged per-dataset residuals, §5.6 dissolution discriminator (near-instant dissolution, early/peak 0.968). CHAT workup (2.3) not-CC. 18 quick gates; 21 tests. |
| 2026-07-11 | Sprint 7 done | 1.6 foster machine-mode data-validated vs digitized Figs 12-15 (Tim drop): Fig 15 flow-minimum Q/Qm=0.181@2s RMSE 1e-4 (P2 null baseline); trajectory matches fitted curves to line width. 20 gates. |
| 2026-07-11 | Sprint 9 (CC part) | 2.2 A8 per-cell BedState fields (SCHEMA 0.5) + P2 null-first ladder: on 9-bar rising flow, Φ(t) rung 4 (RMSE 0.113) beats flat null rungs (0.603) 5.4×. Rung 5 challengers Phase 3. CHAT (which mechanism survives) not-CC. 21 quick gates; 23 tests. |
| 2026-07-11 | D4 (partial) | angeloni2023 + egidi2018 cards committed; D4 intake PARTIAL — Table 7 inventories (16 rows) + loader + manifest; 66-shot chemistry (Tables 2-5) BLOCKED pending Tim drop (MDPI Cloudflare-blocked, not in card, not fabricated). G1 refined (egidi2018 = soil Richards solver; gap is constitutive θ(ψ)/K(ψ); interim = a4a17a9 wetting-atom probe). angeloni = first independent multi-species target for pannusch2024. |
| 2026-07-11 | D4 done | angeloni2023 full 66-shot intake (Tim dropped xlsx Tables 1-7): bioactives (66×11 species, joined to conditions + on/off-grid), total_solids, lipids, inventories → loaders + 4 manifest rows + smoke tests. gate_angeloni_multispecies_bracket (slow): cameron reads ~2-4 TDS pts LOW vs angeloni TS (0/3 bracketed) but matches the finer→higher ordering → Cameron-reads-low confirmed on a 2nd independent dataset (after egidi). |
| 2026-07-11 | angeloni brackets | pannusch<->angeloni multi-species: (envelope) pannusch brackets ALL 4 species (CF/TR/5CQA/TDS) in the angeloni ranges where cameron's TDS reads low. (PER-CONDITION, granulometry O on-grid, p->flow via angeloni tau) overall MAPE 31% (22-50% by species) >> the envelope 'all-in' and angeloni's own ~9-13% model -> the envelope bracket was OPTIMISTIC; pannusch does NOT predict angeloni per-condition. Inventory-matching helps caffeine, hurts trigonelline (not pure inventory); only Arabica TDS response-shape transfers (r=0.73). Independent; flow-map caveat in manifest. Both in validation/slow/angeloni_bracket.py. |
| 2026-07-11 | flow-map refinement | pannusch<->angeloni per-condition: refined Darcy q~p/mu(T) flow map (registered viscosity, not fitted) closes 31.3->26.5% overall (4.8 pp, the residence-time part). +inventory-matching -> caffeine ~15% (near angeloni's own ~9%); but trigonelline/5CQA stay 20-47% = genuine per-species KINETIC gap, closable only by refitting to the angeloni coffee. Arabica TDS shape still r=0.74. Honest PARTIAL closure. |
| 2026-07-11 | pannusch refit | pannusch kinetics refit to the angeloni coffee (post-fit calibration): per solute/variety, c_s0 (analytic level) + rate_scale (Sherwood kinetics) on 9 on-grid granulometry-O, held out 2 off-grid O. Mean holdout MAPE 7.2% -> transfer gap CLOSED under refit. Decomposition: caffeine rate 1.0 (pure inventory; fitted c_s0 recovers Table 7), trigonelline rate 0.4 (genuine kinetic difference). Post-fit on-grid + 2-pt holdout (weak independent). Kept in validation/slow/ (9-pt fit, gran O only); not registered. |
| 2026-07-11 | refit C/F validation | NEGATIVE result (tempers the refit): the granulometry-O refit does NOT transfer to held-out C/F (~25-49% MAPE vs O holdout ~7%), and the (rate_scale,c_s0) split is degenerate/flow-confounded (caffeine rate flips 0.4/0.4/2.5 across O/C/F; c_s0 swings 2.3x for a fixed inventory). Earlier 'gap closed / inventory-vs-kinetic decomposition' was over-read -> pannusch stays a schmieder-fit runtime; angeloni is a transfer target it does not meet across grind. |
| 2026-07-13 | D5 done | 0.13 visualizer.coffee harvester + two-tier intake (data-only tool; NO component/gate). puckworks/lib/ new subpackage; [harvest] extra (lazy requests). Hydraulic (reference-strength population) vs user-outcomes (not groundtruth) kept SEPARATE; SI at boundary + rule-7 flags; privacy drop + salted user-id hash; corpus gitignored/NOT redistributed (Miha corr. pending §5.8). 2 MANIFEST rows + data-only card visualizer_coffee + PROVENANCE + DERIVED aggregate_stats.csv (zero-state; Tim refreshes locally). 14 offline tests (fixtures, not live API); NOT in run_all_gates. |
| 2026-07-13 | D5 corr. | Tim SENT the Miha Rekar (visualizer.coffee) corpus-use request email — sanctioned bulk/research use + possible export; awaiting reply. Gates redistribution/publication use only (public-API harvest already in place, 0.13). Status flipped across §5.8 / SPRINTS TB / REVIEW_BACKLOG / email footer / SOURCE_MANIFEST. |
| 2026-07-13 | V1 done | 8.1 visualization layer (puckworks/viz/) — evidence-bound VizSpecs (10), NO component/gate; extends public/ badge system. Class-1 route through the SAME producers as the paper figures (figures.py untouched); class-2 2D fields now, 3D behind [viz3d]; PV-09 hidden_puck_movie multi-lens montage. Badge+evidence+fidelity-ceiling drawn INTO every graphic. Heavy renders gitignored/local; thumbs+data.json+GALLERY.md tracked. Generated GALLERY reproduces the hand-authored GALLERY_SEED (ceilings verbatim; 3 sanctioned Note-1 composite divergences recorded in ROADMAP §7.1). tests/test_viz.py (9, offline, not in run_all_gates). |
| 2026-07-15 | 3 cards reviewed | abedi2025 → SKIP (vendor dry-powder blog, feeds nothing; card is the record). hargarten2020 → DATA-ONLY (printed Table 2 swelling-progress + scalar anchors → data/hargarten2020/ + loaders + 2 manifest rows + smoke test; PSD/particle figures OWED; feeds not-yet-open bed_dynamics swelling backlog). khomyakov2020_2 → fuller re-card of the intaken khomyakov paper, cross-linked; its finding actioned as gate_g10_intersource_spread (khomyakov measured μ ~+37% above TR2001 in the X_w 80–85% overlap). G10 verdict shown ROBUST to it: sensitivity study re-run with the coffee-μ excess doubled still gives ≤5.3% shot-integrated → no runtime hook (7th g10 gate). |
| 2026-07-15 | G10 CLOSED | Telis-Romero coffee-liquor rheology gap closed (Tim dropped the 2001 μ + 2000 ρ/Cp/k/α cards, then the digitized Table 1/2). (1) `telisromero2001` Eq (10)/(12)/(13) μ(T,X_w) closures + (2) `telisromero2000` ρ/Cp/k/α closures (data-only companion; Eq-6 α typo corrected; fraction-vs-percent guard) + (3) full Table 1/2 digitized (51 measured cells; closures reproduce them at the authors' own fit quality). New `analysis.g10_viscosity_sensitivity` drives the measured μ(c,T) through cameron2020's in-pore liquor field: across the espresso envelope the liquor never approaches saturation (μ ≤ 1.05× water), so the constant-water-μ Darcy error is ≤~3% shot-integrated → **no runtime μ(c,T) hook warranted; RC-2/RC-3 early-shot bias is NOT bulk viscosity**. 6 g10 gates green (incl. `gate_g10_telisromero_full_table`, `gate_g10_viscosity_bulk_negligible`); evidence `source_curve_reproduction`. Fixed a dilute-clamp μ-mapping bug + an import-order C_S0 global-state leak (pinned cameron's published 118.0). ROADMAP §4 + BLOCKED_INTAKE marked ✅ CLOSED. Only optional upgrade left: an independent espresso-TDS viscosity measurement. 240 tests pass. |
| 2026-07-19 | PV-19B lab | Fourth genuinely-executed native reference runner: `brewer2026.lb_reference` (`batch-only`) — solves the canonical synthetic plane channel and compares to the exact plane-Poiseuille `k=h²/12`; shared `channel_verification()` helper single-sources the arithmetic for gate + runner (gate byte-identical); pass/fail delegated to `gate_lb_channel`. First affirmative outward rights clearance (code CLEAR / data NOT_APPLICABLE / output CLEAR; first-party, synthetic input, analytic reference — `docs/rights_review_notes.md`, #70). First selected-references-only `PUBLIC_ARTIFACT` path: a request for exactly this runner passes preflight and runs one native producer; broad/default/mixed public requests still block before any producer. NOT coffee/espresso validation — code verification only. The broader Laboratory, public batch, Roman lens, and the validation program remain open; Grudeva stays blocked (#73). |
| 2026-07-19 | PV-19B access | Browser-accessible Laboratory. One rights-safe execution facade (`puckworks.product.lab_service.execute_lab_request`: explicit context, preflight before any producer, typed blocked result with no science) consumed by the batch, Colab, and both Streamlit apps. Producer-free Explorer (`lab_explorer.explorer_catalog`, zero execution). Form-driven novice Colab `guided_pull_laboratory_colab.ipynb` (one Run button, LOCAL_PRIVATE, commit-pinned dev preview; hermetic smoke → GUIDED_PULL_LAB_COMPLETE). Public/local Streamlit split: `apps/lab_public_app.py` (PUBLIC_ARTIFACT fixed in code; Model library runs nothing; cleared-only self-checks; reference-shot disabled pending Cameron) + `apps/lab_app.py` (LOCAL_PRIVATE). Deploy manifest (`requirements.txt`) + `docs/DEPLOYMENT.md`; codespaces-ci health-smokes both apps. README features the Laboratory Colab beside the quickstart. No rights widened; Grudeva blocked (#73); human signed-out sign-off + deploy remain (#43). |
| 2026-07-19 | PV-19B tour | Full Laboratory Tour (`puckworks.product.lab_tour`). Versioned FROZEN manifest `full_laboratory_tour_v1` resolves all 25 components to one primary route each (COMMON_SCENARIO/NATIVE_REFERENCE/SCIENTIFIC_CHECK/OPTIONAL_DEPENDENCY/RIGHTS_BLOCKED/NO_EXECUTION_PATH); `verify_tour_manifest()` fails on an unclassified/contradicted route. `execute_laboratory_tour()` runs each route through `lab_service` (preflight before producer) → one stage-grouped TourComponentResult per component, deterministic hashes. Today 23/25 executed (1 common + 4 native + 18 checks via rights-filtered gate_runner); grudeva RIGHTS_BLOCKED with ZERO calls (#73); lb_taichi optional. No averaging/overlay; public runs only cleared components. Colab default = Full Laboratory Tour (4 modes, coverage preview, stage-grouped badge cards); hermetic smoke: 25 resolved / 23 executed / marker. PR2 (rights-aware check-runner API + strict contract tests) and PR3 (UX polish) to follow. |
| 2026-07-20 | PV-19B deep dive | Educational insight figures for the Full-Tour per-model deep dive. Gate scorecards REMOVED from the novice view (`_gate_figure`/`_PASS_COLOR`/`_FAIL_COLOR`/"condition index" deleted from `lab_tour_plots`; a scientific check alone yields no figure). New `lab_tour_insights.component_figures()` → 0/1/many VizSpec-governed figures per component, each teaching one model relationship from an authoritative producer (no equations reimplemented/copied), badge+evidence+ceiling stamped. New tested analyzer `viz.relationship.classify_relationship` recomputes caption numbers (increasing/decreasing/flat/non_monotonic/insufficient; wobble ≠ reversal). `cameron2020.extraction_bdf` = hero (`HERO_COMPONENT_IDS`, first deep-dive) with 3 figures (whole shot / pressure sweep EY↓ / beverage-mass sweep); reused VizSpecs give ≥5 other components a figure. Every educational producer call obeys the component's tour rights decision (rights-blocked/optional/not-executed → zero calls + finite `no_figure_reason`). Educational sweeps stay out of the tour scientific hash; frozen execution contract unchanged. PR-A = modules+tests+docs+gallery (this commit); PR-B = notebook Cameron-hero-first rework + pin bump to a PR-A commit. |
| 2026-07-20 | PV-19B figure polish | Presentation/readability pass on the deep-dive educational figures (formatting only — no science change). New `viz.tour_style`: reserved header (badge) + footer (`Scope:` wrapped ceiling) subfigure bands so nothing overlaps an Axes; local ≥8 pt typography (retires 5.2 pt footer); `presentation="notebook"|"standalone"`; shared figure-level axis labels; the reference star explained once; idempotent tour stamp (ordinary stamp unchanged for other figures). Per-figure fixes: Foster wetting front windowed to the event; LB profile normalized (fraction-of-max, wall/centre labels, no six-decimal ticks); pack a compact solid/pore + heterogeneity-field landscape with key + colorbar. New tested `product.lab_tour_notebook_display` → structured labelled sections + collapsed `<details>` evidence block + humanized fixed inputs; notebook restructured (public headings, no repeated question, retina inline). Structural bounding-box/typography tests (`test_tour_layout`). No value/badge/ceiling/route/hash/ordering/rights change. PR-A = modules+tests+docs (this commit); PR-B = notebook + pin bump to the PR-A commit. |
| 2026-07-20 | PV-19C relay | **Espresso Model Relay** (`illustrative_linked_pull_v1`) — a NEW product, separate from the Full Laboratory Tour (which is unchanged, hash `2054b04d…` regression-pinned). Product engine `puckworks.product.linked_pull` (+ manifest/records/adapters/narrative/display/figures) runs one illustrative pull as a directed acyclic one-way relay: authoritative producers only, typed `LinkedValue`/`LinkRecord`/`AssumptionRecord` (A01–A12), frozen manifest covering all 25 components. Default fast run executes 19 components / 11 hand-offs (2 direct, 7 adapters, 2 assumptions), Cameron baseline + one-way Cameron→Waszkiewicz + streamtube heterogeneity + reduced Pannusch multi-solute + alternative lenses + no-averaging dashboard. Grudeva zero calls; Taichi optional; no taste/confidence score; deterministic hashes (not validation). Rights preflight before every producer; `LOCAL_PRIVATE`, public fail-closed. CLI + new one-click, output-free, commit-pinned Colab notebook (`LINKED_PULL_RELAY_COMPLETE`); figures reuse existing VizSpecs. Fast ~4 s CPU. PR-A = engine+modules+tests+docs; PR-B = notebook + pin bump to the PR-A commit. |
| 2026-07-21 | PV-19C hardening | **Post-merge stabilization + a real integrity fix.** Removed the streamtube→Cameron `C_S0` import-time global mutation (Cameron `simulate_shot(c_s0=…)` param; streamtube passes its own basis) — Cameron is now import-order invariant; the Full Laboratory Tour clean hash is CORRECTED `2054b04d…`→`1c1434ef…` (the old value captured pollution — the tour read Cameron EY 17.06 % not its own 14.11 %). Truthful accounting: pannusch solver → NOT_SELECTED (release clock is closures-derived), fast-mode LB → NOT_SELECTED (not a missing dep), Taichi never the reference solve, 5 mis-labelled EXECUTED_WITH_ASSUMPTIONS → EXECUTED → audited fast run **18 executions / 10 hand-offs / 9 assumptions**. Removed silent wetting `k=2e-13` fallback + dissolution `np.clip` (explicit domain rejection + recorded zero-start mask); runtime links only after a completed transfer. Strict canonical serializer (`allow_nan=False`, never `default=str`). Result-bound figures (draw from the completed result, zero model calls, owned by component, no `2e-13`). Notebook: no auto-download (FileLink), figures by owner. README "Four public paths"→"Five", counts corrected, blanket "not coupled" reworded; ROADMAP §7.1 + repo-truth tests. NOT a validation upgrade. All gates pass (50+1); full suite green. CI phantom = harmless matrix-grouping placeholder (leaf jobs passed). |
| 2026-07-24 | cards | 7 methods/reference cards committed — **NO component/gate/data/manifest/evidence change; `run_all_gates` unchanged (PASS=58)**. Inverse-problems/identifiability: `liu2025` (OED + profile-likelihood + PMP model-discrimination) + `bakeer2025` (Bayesian/FIM distributed-field informativeness) → **implement-later** offline auditing layer for thin-data fits (cameron2020 rate constants, brewer2026 σ(φ1)) and P(t)-discrimination design; `boulle2026` (structural noise-free one-shot identifiability) → **skip** (niche held by liu2025). Multiphase-LB wetting reserve for the incomplete-wetting backlog: `kupershtokh2009` (EDM/arbitrary-EOS, method-of-record) + `huang2016` (3rd-order MRT closure Λ≡1/12, k₁/k₂) → **implement-later** contingency; `wang2027` (liquid-Na MRT-LBM, wrong regime, unpublished sᵢ/k₁/k₂) → **skip**, defers to those two (cross-linked). `li2026` (shape-dependent granular column collapse, 2 mm cohesionless grains) → **skip** (no stage/contract/backlog hook; Eq-8 coeffs preserved in card). Net 4 implement-later, 3 skip; cards are the record. |
| 2026-07-24 | venues | **Paper 3 venue scouting started** + venue reminder fired (docs/ops only; no science/code). `docs/SUBMISSION_TARGETS.md` §11a profiles the software-paper route (JOSS primary · SoftwareX · JORS · methods-journal fallback) with readiness gates (tagged release + Zenodo DOI — repo v0.4.0.dev0) and anti-double-submit rule; **labelled initial scouting — portal details UNVERIFIED, no deadlines asserted (rolling)**. Paper 3 flagged as the home for the just-carded identifiability/experiment-design methods (liu2025/bakeer2025/kupershtokh2009/huang2016), not Paper A/B. Manually dispatched `venue-deadline-review` (run 30108167054) to post a fresh verification checklist to #42; auto-reminder stays opt-out (`ENABLE_VENUE_REMINDERS` unset). Paper 4 scouting still owed. |
| 2026-07-24 | venues | **Paper 4 (spatial/control) venue scouting — CONTINGENT / BLOCKED** (docs only). New `docs/SUBMISSION_TARGETS.md` §11b, blocker front-and-centre: **Paper 4 is NOT authorized** (card-blocked on G-lat; go/no-go boxes OPEN — Ξ-measurability via `k_lat`/`w`, and inference identifiability). Contingent ladder reuses Paper B's porous-media/fluid-physics venues (Transport in Porous Media primary · PoF · PRF · JFM stretch) + a speculative control-systems alt (J. Process Control / Comput. Chem. Eng., unverified); scope sourced from `docs/future/PAPER_4_SPATIAL_CONTROL_NOTE.md`, not invented. Interim (not-blocked) homes noted (Gallery of Fluid Motion visual, technical note, spatial-experiment-design guide → Paper B2/3); near-term action is closing G-lat, not submission. Unverified, no deadlines, own unset Verified date. Paper 4 scouting now **done (as a blocked watchlist)**. |
| 2026-07-24 | paper-A review | **Paper 1/A external desk-review intaken + triaged** (docs only; no manuscript edit/science/evidence change). Verified every load-bearing claim of `paper1_resource/PAPER_1_DETAILED_REVIEW-20260724.md` (verdict: major revision) against current `main` — all CONFIRMED: live JFE↔DRAFT version drift (5 stale phrases vs 4 corrected), `2.x`-under-§3 numbering, undefended Table 7 `1 kg = 1 L` basis (Angeloni card L53), L9 editorial note + `Strength:`×4 + object-names + placeholders, no consistency gate. Built `PAPER_1_REVIEW_ACTION_PLAN.md`: all 15 major comments + P0/P1/P2 triaged by priority × owner ([mech]/[author]/[analysis]/[external]). Did NOT patch the manuscript — MC1 requires picking ONE canonical source first (recommend `PAPER_A_DRAFT.md`) + a drift guard; author decision gates the mechanical stream. Nothing upgraded. |
| 2026-07-24 | paper-A [mech] | **Mechanical batch landed** (canonical = `PAPER_A_DRAFT.md`, author-approved; no scientific rewording/evidence change). Synced the JFE conversion to the canonical draft: 5 retired overclaim phrases → corrected wording (profile range ratio / conditional 1-D intersection band / cross-grind endpoint prediction / 40 mL matched-volume / in-sample comparator ladder); Methods `2.x`→`3.x`; removed L9 note, de-tagged 4 inline `Strength:` labels to prose, removed availability scaffolding. New guard `tools/paper_a_consistency.py` + `tests/test_paper_a_consistency.py` (5 tests, quick-pr lane) catches drift at PR time. Deferred (author/analysis, tracked): in-text §-ref remap, evidence→study-design table, placeholder fills, Table 7 units audit, uncertainty reruns. `run_all_gates` unaffected. |
| 2026-07-24 | paper-A P0-4 | **Table 7 dimensional audit → demoted to qualitative** (down-scope; no evidence upgrade). `PAPER_A_TABLE7_UNITS_AUDIT.md`: the intersection equates two `mg/mL` values whose volume bases aren't shown to match (pannusch `c_s0` fitted+unanchored; Angeloni Table 7 = dry `mg/kg` assay via undefended `1 kg=1 L`); the assay alone spans ~4.8–16.3 mg/mL (~3.4×) ≫ the ±10 % propagated, so `rate ≈ 0.95 [0.60–1.76]` isn't secure. Demoted in canonical DRAFT + synced JFE (kept the intersection-band framing, dropped the numbers, added the caveat); guard +1 required anti-regression phrase (`qualitative, not a quantitative rate constraint`); docstring caveat on `table7_rate_constraint` (no computation change). Qualitative claim preserved. Guard 6 req/5 banned green; guard tests 5 pass. |
| 2026-07-24 | paper-A P0-5 A+B | **Uncertainty reruns delivered** (author-approved: sweep framing, Huber, both bootstrap units; descriptive, no evidence upgrade). Binding constraint: named-solute per-cell RSD unavailable → sensitivity sweep, not calibrated inference. **(A)** new pure `_profile_objectives` (reuses PDE matrix) wired into `identifiability_panel` — SSE/relative-L2/Huber all leave the inventory–rate valley broad (10 % set 31–76 % of the log-rate grid, mostly boundary-censored; rate-at-min shifts 0.66→0.58→0.86) → degeneracy is design-driven, not an unweighted-SSE artefact. **(B)** new pure `paired_clustered_bootstrap` over per-point records from `transfer_skill_vs_baselines` (B=8000, seed 0) — ΔMAPE 95 % CI **[−0.73,+0.03] pp cond-in-group (includes 0)** / [−0.75,−0.03] group → ~0.4 pp null-skill **indistinguishable from zero**. Written into canonical DRAFT + JFE (§4/§5 + limitations); `PAPER_A_P0-5_RESULTS.md`; 7 CI unit tests (`test_paper_a_uncertainty.py`). Deferred: (C) LOCO refit-in-loop; calibrated named-solute weighting (replicate drop); Robusta TR/5-CQA panels. `run_all_gates` PASS=58 unaffected. |
| 2026-07-24 | paper-A P0-5 C | **Coverage-calibrated LOCO interval delivered** (bounded; descriptive, no evidence upgrade). New `loco_coverage_interval` + pure `_oob_coverage_bootstrap`: F is data-independent → cached once, each replicate resamples the 9 (T,p) conditions, **refits** rate+level on in-bag, scores **out-of-bag** (600 reps, arithmetic refit-in-loop, no leakage). Held-out MAPE **7.4 %, 95 % [4.3, 11.5] %** — *wider* than the descriptive [5.0,8.2]/[5.1,8.3] (they omit refitting variability); centre slightly above LOCO 6.5 % (OOB sets larger) → complements LOCO. Written into DRAFT + JFE (§5 + limitations); `PAPER_A_P0-5_RESULTS.md`; 2 new CI unit tests (9 total). Guard green. Owed: named-solute weighting (replicate drop); Robusta TR/5-CQA panels. |
| 2026-07-24 | cards (batch 2) | 9 cards reviewed + committed — **6 skip, 1 implement-later, 2 calibration-provider (data + gates OWED); NO component/gate/data/manifest/evidence change; `run_all_gates` PASS=58**. Analytical-caffeine skip family: `wale2023`/`legasmuhammed2021`/`yu2021`/`mystkowska2024` (no bed/flow/time-axis; printed errors; dominated by schmieder/angeloni/maille/bruno). Wetting-LB reserve: `kusumaatmaja2010` → **implement-later** (free-energy binary LB — MRT + Bouzidi + Cahn wetting BC, the piece `kupershtokh2009` lacks); `bellantoni2025` → **skip** (IB sharp-interface LB, structurally worse-suited). Vaca Guerra: `vacaguerra2023a` → **calibration-provider** (σ→porosity→modified-Kozeny K; first σ→porosity→K chain, tamped regime where wadsworth extrapolates); `vacaguerra2025_leseprobe` → **skip** (reading-sample, pointer only). `maille2024` → **calibration-provider** (best early-time <30 s per-species dataset + PSD→φ fast-fraction closure Cameron lacks). Both calibration-providers card-only: source tables not in card (vacaguerra Table C.1; maille Tables 6.3/6.4/5.x + per-bin PSD) + blocking gates (vacaguerra β-sign + µ/G10 renorm; maille E1 shell depth) → data intake + gates owed (fetch/drop). |
| 2026-07-25 | vacaguerra2023a intake | **Data intake (Tim drop) + 3 verifications; blocking sign error RESOLVED; `run_all_gates` PASS=58 unchanged.** Digitized Table C.1 (9 permeability points) + Tables 1–3 (PSD + ANOVA coeffs) + Fig. 12 → `data/vacaguerra2023a/` + PROVENANCE + 5 loaders + 5 MANIFEST rows. `analysis/vacaguerra2023a.py` (8 CI tests): **(1)** printed +β signs give unphysical ω 0.48–0.62 → registry adopts **−k₃β/−x₃β** (retires the card's blocking gate); **(2)** Fig-12 cross-device validation **R²=0.942**; **(3)** independent Darcy K reproduces the authors' band (7/9 in range, all order-of-mag; loosest 17.5 g beds ~1.3–1.7× above; post-fit Eq-11 KC ~5× below the µ=3.5 mPa·s Darcy, ≈ the µ/G10 factor). **(4)** wadsworth cross-eval (adapter flagged: φ_p←ε₀, R←d₃₂/2 Sauter) — wadsworth (validated untamped φ_p 0.37–0.67) **overpredicts the measured tamped Darcy K by ~13–31× (median 23×)**, worsening as ε₀ drops below 0.37 (tightest 25× / loosest 15×; larger under G10 µ) → localizes the tamped-extrapolation breakdown; promotes neither. Verification/reconstruction/discrimination strength (single material). No registered component (card = offline only). Owed: component registration, µ→G10 λ refit. Card: card-only → data-intaken. |
| 2026-07-25 | vacaguerra2023a λ refit | **µ→G10 λ refit** (analysis only; `run_all_gates` PASS=58). `permeability_lambda_refit`: Eq-11 λ is viscosity-convention-dependent (λ∝√µ). Published **λ=7.5** (fit to authors' K) → **3.47** vs the independent Darcy K at µ=3.5 mPa·s → **≈10.0** under the registry G10 espresso-liquor µ (≈0.42 mPa·s @ 65 C, telisromero). +1 CI test (10 total). **Decision: kept as data + analysis provider — component registration declined** (card = offline only; single-material/post-fit; avoids public tour/relay/evidence churn). Nothing further owed on vacaguerra2023a. |
| 2026-07-25 | vacaguerra2023a propagation | **Unblocked propagation of the wadsworth cross-eval** (docs only; no evidence promotion). **(1)** Gap-ledger §6 P4/G9: vacaguerra2023a recorded as 2nd measured tamped-κ dataset; the Wadsworth tamped extrapolation now **quantified ~13–31× (median ~20×)** as a G9 gate target. **(2)** Paper 3 §10 Table 5: new tamped-permeability disagreement row + paragraph (verification strength, neither promoted; surgical, not a 4th headline case). **(3)** PV §7.12: new data-literacy card feeding PV-15 (verification/discrimination tier; not-a-validated-law caveat). Blocked & skipped: maille2024 φ-split Paper A trigger (data owed). |
| 2026-07-25 | maille2024 table intake | **14 thesis tables digitized (Tim drop, unredacted) + 3 verifications; E1 shell-depth RESOLVED; `run_all_gates` PASS=58.** `data/maille2024/` + PROVENANCE + 11 loaders + 10 MANIFEST rows + README ref. `analysis/maille2024.py` (6 CI tests): **(1)** printed Eq-6.9 one-cell-layer wrong → **two-layer** reproduces Table 6.3 θ_v,coarse (mean|err| 0.018 vs 0.207; ~doubles φ); **(2)** φ = fines+coarse exact + θ_v,fines↔Table-5.4 <186µm to 0.003; **(3)** the 2 E5 impossible-CI rows (ΩT/3-CQA, ΩL/quinic) flagged unusable. Datasets: φ closure, hybrid + liquid/air PSD (P1 fines-method hazard), caffeine/3-CQA + organic-acid λ_fast/λ_slow, equilibrium conc., tabulated early-time curves, SSA, porosity (5.6/5.9 unredacted). Verification/reconstruction strength (single origin, batch WMBR, coarse grind). No component. Owed: φ-split-vs-Cameron (BLOCKED — Cameron binned PSD absent), extraction figures (in progress). Card: card-only → data-intaken. |
| 2026-07-25 | maille figures + Cameron PSD | **The two owed maille computations landed** (Tim drop; `run_all_gates` PASS=58). Digitized maille Figs 4.6-4.10 (ΩA, 5 compounds → `maille_extraction_curves`) + Cameron Fig-2 binned PSD (4 grinds → `cameron2020_psd`); +2 MANIFEST, +4 CI tests (14). **(4)** two-regime Eq-6.2 reproduction: tabulated φ/λ reproduce the ΩA curves to **MAPE 4-10%** (≈ model MPE). **(5)** φ-split-vs-Cameron (headline, was Cameron-side-blocked): maille φ on Cameron's PSD ≈ **0.85-0.94** (extrapolation), **both** maille φ and Cameron fines fraction **decrease with coarser grind** (sign agreement) but differ **~5-9×** — **not commensurable** (maille fast = fines<186µm + coarse shells; Cameron fast = 12µm class) → registry-surfaced observable-semantics disagreement, not a validation. maille2024 complete; nothing further owed. |
| 2026-07-25 | Paper 3 MC14 corpus governance | Fully documented §6.6 (Tim decision — §7.4 demo makes the corpus load-bearing): ~11 governance items (lawful basis, human-subjects determination flagged OPEN, minimization/retention, access control, deletion/withdrawal, small-cell/linkage, free-text, hash threat model, incident response, snapshot provenance, aggregate disclosure) + reframed **pseudonymized, not anonymized** (salted hash = persistent linkage key). Posture/commitments, not completed determinations. Guards green. |
| 2026-07-25 | Paper 2 (B2) Tim decisions | Removed viscosity/Gagné material (4.6): §5.4 keeps dissolution-opening as scored sign-carrier + degenerate-candidate note; Table 4 row / §6.5 Gagné / Limitation-2 apparatus deleted; full material reserved in `docs/future/PAPER_B2_VISCOSITY_GAGNE_RESERVED.md` for the perturbation-program follow-up. Retitled 'many **explanations**' (E16); dropped 'systems identification' keyword (4.12). build verify 18/18. |
| 2026-07-25 | Paper 2 (B2) review accuracy pass | Intake + tracker (`PAPER_2_REVIEW_ACTION_PLAN.md`) for the B2 review (major revision; headline RMSEs reproduced). Applied E1–E13 down-scoping: 'establishes a need'→'supports temporal flexibility'; 'measured 9-bar trace'→'preprocessed across-shot mean' + new observation-operator para (§2.4, incl. `*_std`=SEM); Φ(t) reuse caveats; cubic→'same-trace descriptive benchmark'; moving-block→'conditional fixed-loss resampling sensitivity'; resolved viscosity contradiction→qualitative sign candidate. **Verified** solids_calibration.csv sign-doc error (`1 - tanh` vs code `1 + tanh`, poroelastic.py Eq. 20; doc-only) — fix **deferred** to the 4.13 release rebuild (SHA256 pinned in manifest + PV-04 snapshot). Added recorded-pressure robustness (<0.001). Deferred: per-shot ladder / LOSO Φ(t) cross-fit / shot-level uncertainty / residuals / release (analysis), + viscosity remove-vs-integrate & title decisions. 14 tests pass. |
| 2026-07-25 | Paper 3 localized P1 (MC16/17/18) | MC16: new Table 2 (§4.1) = per-contract-layer catches/residual-risk (permeability window = coarse sanity check); state-carrier table -> Table 2a. MC17: define Fo_F = k_I*rho*|u|/mu in §4.4 (order-unity inertial onset; regime DIAGNOSTIC not validated correction; no bare 'Fo'). MC18: §13.4 cross-domain reach reframed as a proposed pattern demonstrated in espresso, not an empirical generalization. Tests pass; evidence reconciles. |
| 2026-07-25 | Paper 3 P1 gate-4 rigor complete (U13) | Condensed §4.5 to the principle (shared curve form != shared physical contract) and moved detail to new **§7.5 'Shared curve form, non-shared parameters'** + generated **Table 4a** (same fast/slow form, 3 evidentiary meanings), citing the producers + timescale_semantics_bundle(). Reports U6 multistart non-identifiability + U8 protocol sensitivity + U2/U3 caveats, all producer-backed. Gate-4 rigor thread complete (U2-U16 done bar U1-partial). 25 tests pass; evidence reconciles. |
| 2026-07-25 | Paper 3 P1 related work (MC9) | Added §12 "Related work and novelty" (6 traditions: FAIR/FAIR4RS, PROV/RO-Crate, Model Cards/Datasheets, reproducible practice, model-interchange standards), each with the gap Puckworks fills; §12.6 scopes novelty to "joint operationalization". +9 refs [14]-[22] with DOIs; Discussion/Limitations/Conclusions renumbered §13/§14/§15. 8 tests pass; evidence reconciles. |
| 2026-07-25 | Paper 3 P0 localized | MC5: abstract "weakest load-bearing link" → non-scalar "distinct evidence relations of all load-bearing components" (matches §5 evidence-vector). MC4: Table 3 rewritten as four separated axes (relation/outcome/role/badge); rows now the exact `EVIDENCE_STRENGTHS` enum ("Independent external"→`controlled_independent`); "Negative validation" removed as a category, reframed as outcome polarity. Drift guard +1 test (every enum value documented). MC6 clean. 13 tests pass; evidence reconciles. |
| 2026-07-25 | Paper 3 P0 generation/consistency | First scoped batch (genre decided = full methods/resource; P0 gen/consistency first). Bound manuscript counts to the live registry: manifest **70→104**, Table 1 roles **11/13/1-synthesis → 12/13/0** (synthesis = provenance not role), date 15→25 July. Rewrote **§3.2/§3.3** around schema-v2 axes (execution_role/provenance_class/evidence_strength; `kind` deprecated; 4 execution roles, adapter/diagnostic uninstantiated; project_synthesis reframed). **New CI drift guard** `tests/test_paper3_manuscript_consistency.py` (4 tests) parses the prose and asserts counts/roles == live registry/MANIFEST — makes the manuscript's "CI fails on drift" claim true. 41 tests pass; evidence reconciles; build verify ok; gates PASS=58. Deferred: figures, related work, framework eval, P1 gate-4 rigor, Table 3/abstract edits, MC14 corpus decision, freeze-to-tag. |
| 2026-07-25 | Paper 3 review consolidation | Merged two reviewer docs (base MC1–MC18 + update U1–U16) into `PAPER_3_REVIEW_CONSOLIDATED_ACTION_PLAN.md`. Applied the gate-4 §4.5 **accuracy corrections** both reviews flag (fixes to our own #175 work): U2 shape-vs-absolute (only weight/ratio grind-invariant; absolute constants vary ~1.9×), U3 fine-class-only (coarse d[4,3] not evaluated/not fabricated), U4 "one physical diffusion process", U5 cameron one-vs-two-exp (3 of 4 single-exp-like; gs 2.5 → model selection), U11 derived verdict, U12/U15/U16 descriptive-not-contract + model-generated/qualitative, U14 stale docstring/test. Fixed **MC6** infiltration "independently gated" → same-shot compatibility (P0 integrity). Deferred (genre decision / generation-pipeline): counts 70→104, roles 11/13/1→12/13/0, schema-v2 §3.2, figures, related work, framework eval, claim records. 13 maille tests pass; evidence reconciles; gates PASS=58. |
| 2026-07-25 | gate-4 propagation (docs) | Propagated the completed gate-4 finding (two-regime ports to neither cameron nor roman) into narrative — companion to the φ-split propagation. **Paper 3 §4.5**: paragraph on the two-regime *structure* — a shared bi-exponential form collapses (cameron) or gives a single-mode Crank pair 2 orders off (roman), meaning its fast/slow parameters name three different constructs; **a good fit is not evidence of a shared quantity**. **PV §7.14** ("'fast then slow' in three models, three reasons") — qualitative sequel to §7.13, seeds PV-15. Observable-semantics point (not §10 measurement map); no gap-ledger/component change. |
| 2026-07-25 | maille gate 4 (roman half) → COMPLETE | Landed the Roman-Corrochano **stirred-vessel** half of gate 4 (`cross_model_timescale_roman()`, +1 CI test) — the genuine well-mixed config. **Rights-scope correction:** not rights-blocked for research use (same `published_port`/`NOT_REVIEWED` class as cameron2020, already run here); #100 gates only the public Laboratory product lens. Roman's raw curves were never published → model-generated via its Crank-verified `stirred_vessel` solver (single med-MW species, fine class R~20µm). **Finding (a "miss"):** universal Crank shape (grind-independent φ~0.32, ratio~12.3 = one diffusion mode's short/long-time signature, two-regime-*shaped* R²~0.999 vs ~0.95 one-exp) — **not** maille's material-varying two-**pool** split; fine-class timescales ~2 orders below maille's bands (coarse d[4,3] not published → not fabricated). **Gate 4 now COMPLETE: maille's two-regime ports to neither cameron nor roman.** Both halves qualitative; no component/gap-ledger change. |
| 2026-07-25 | maille gate 4 (cameron half) | Landed the cameron-only half of maille gate 4 (cross-model timescale portability) as a **qualitative** non-portability probe (`cross_model_timescale_cameron()`, +1 CI test). Fit Eq 6.2 to cameron2020's simulated extraction curve → the fast/slow split **collapses** (λ_fast ~23-32 s, above maille's 19.1 s ceiling, ~= λ_slow for the 3 finer grinds); cameron is single-timescale (~30 s) with **no maille-fast component** → decomposition does **not** port. Heavily caveated: cameron has no well-mixed config (flowing bed; fit its cup curve), run to exhaustion (~400 s) past its ~30 s recipe, one lumped solute (τ=0). Not a validation. Roman-Corrochano stirred-vessel half stays **rights-deferred (#100)**. No component/gap-ledger change. |
| 2026-07-25 | φ-split propagation (docs) | Propagated the maille φ-split-vs-Cameron finding into narrative: **Paper 3 §4.5** fast-fraction-semantics paragraph (same-name-≠-same-quantity, ~5-9× definitional gap, alongside inventory/saturation examples) + **PV §7.13** consumer data-literacy card (verification/discrimination tier, not-a-validation + extrapolation caveats, no-experiment-settles-a-definition note, feeds PV-08). No gap-ledger/component/evidence change — this is a resolved semantics finding, not an open data need (contrast wadsworth → §10 map). ROADMAP §7.1 logged. |
| 2026-07-25 | maille2024 REGISTERED (+A11 contract) | **Card-status data-intaken → REGISTERED; `run_all_gates` PASS=58 → 65.** Two calibration components, one per stage, matching the card's two Interface-mapping roles: **`maille2024.phi_closure`** (grind, `code_verification`) with Eqs 6.7–6.9 and the **PSD-binning adapter** the card listed as a dependency, and **`maille2024.two_regime`** (extraction, `source_curve_reproduction`) with Eqs 6.1/6.2 + the λ tables. Both `calibration`, never runtime (no bed/pressure/flow; K=1 violated in espresso; no EY/TDS). **φ_closure deliberately NOT promoted** to `source_curve_reproduction` — the per-bin PSD is unpublished, so the E1 gate reproduces Table 6.3 only via the D[4,3] approximation. **7 quick gates** (~2.4 s): E1 shell depth (pins the two-layer convention), φ-closure consistency, φ-split-vs-Cameron (negative/diagnostic — sign agreement, ~5–9× gap, NOT commensurable), two-regime reproduction, E5 CI flags (pinned to an exact set → fails in BOTH directions, so a silent "fix" of the source is a failure), + the two gate-4 portability probes. **U10 CLOSED:** the two timescale-semantics claim records are now formal EVIDENCE_LINKS claims (the registration was the exact blocker the bundle's module note recorded). **Contract A11 (SCHEMA 0.6 → 0.7):** `GrindState.fines_threshold_um / fines_dispersion_method / fines_basis` — declarations, **not conversions**; `assert_fines_fraction_comparable` refuses a mismatch *and* an undeclared convention. New P1 grind-side hazard subtable (maille Table 5.2: ~2× fines-fraction disagreement by dispersion method on the same material). Manuscript counts rebound 25 → 27 (12 runtime / 15 calibration); generated Table 1 + Appendix A regenerated. 39 maille tests; evidence reconciles `--strict --scope paper3`. |
| 2026-07-25 | cards (batch 3) | **5 cards triaged — 2 skip, 1 documentation-propagation, 1 data intake, 1 intake blocked; `run_all_gates` unchanged PASS=65.** `cordoba2019` → **SKIP** (cold immersion, no model, superseded by angeloni2023) and `puellesbulnes2025` → **SKIP** (non-espresso ANOVA, transposed method labels, maps to no contract) — the card is the record. `gagne2019` → **documentation only** per its own estimate: ROADMAP §5.10 now sources the EY kernel as **`EY = C·B/D`** (percolation/espresso), with the `1/(1−C)` term flagged as **9–14 % relative** at espresso (not filter's sub-0.5 %), espresso **L ≈ 0.49** from foster's `W_dead` 8.8 g/18 g (bracket 0.42–0.78) rather than filter L ≈ 2, and the `M_ret ≈ 0` assumption carried as **disputed in-source**; new P1 row for the **≈1 pt** moisture/CO₂ EY-comparability offset. Not registered — no dataset, so no gate (rule 1). `gloess2013` → **data-intaken** (DE endpoint only: 16.01 g → 60 ml, 9 bar, 92 °C, 28.7 s) with a per-quantity `extraction_method` column keeping exact text values apart from figure reads — **TDS ≈ 5.5 % and EY ≈ 20 % are figure reads** (ESM not retrieved); loader + PROVENANCE + MANIFEST (104 → 105) + 7 tests; no gate (one pooled composite, one coffee). `melrose2019bed` → **data-only, BLOCKED** → `BLOCKED_INTAKE.md`: needs a Figs 1/2/8 digitization **and** the batch companion (`Y_max`/PSD) before its fits are usable; **Fig. 2's measured rising-then-falling flow resistance is the κ(t) prize**; noted that it re-analyses the same Corrochano-2017 brews, so it is not independent corroboration. |
| 2026-07-25 | waszkiewicz per-brew intake → B2 4.1 | **Paper B2 review 4.1 (per-shot ladder) CLOSED; primary claim strengthened, secondary refuted; `run_all_gates` unchanged PASS=65.** The blocker was an **intake gap, not missing data** — the 57 raw per-brew traces were on Zenodo (record **CC-BY-4.0**) but only the per-pressure means were ingested, and their `*_std` is a **standard ERROR** (`sem`), so shot spread was unrecoverable and the ladder's unit was the time point. Landed `traces_per_brew` (57 shots, 11 pressures, **9 bar ×5**); reduction re-implemented from the documented method (deposit script is GPLv3, **not ingested**); **verified to reproduce the published means on all 11 000 rows to 5e-7**. New `analysis.waszkiewicz_shot_level` + 8 tests. Shot-as-unit (15–95 s): constant 0.580, static 0.661, **Φ(t) 0.189**, cubic 0.107 g/s; **noise floor 0.149 g/s**. **Φ(t) beats the constant on 5/5 shots** at 2.6× the floor (ordering robust), but **Φ(t)-vs-cubic (0.083 ± 0.050) sits inside the floor → not resolvable**, so "nearly reaches the flexible floor" cannot be asserted; and Φ(t)'s 0.116 is against the *mean*, 0.189 against real shots. **4.3/4.4 reclassified blocked-on-data** (TDS replicates aren't shot-matched → no Φ(t) cross-fit; correspondence item). Manuscript untouched by design. Manifest 105 → 106. |
| 2026-07-26 | Paper 3 frozen-release build | **The last non-DOI submission blocker closed.** (1) Figures, five source-data CSVs and `ALT_TEXT.md` added to the deterministic archive — **147 → 149 members**, byte-identical across two builds, still verifiable without the source checkout. (2) New **`release` verb** (`python -m puckworks.paper3.build release`): clean tree required, **freshness proven by RECOMPUTATION** (every generated artifact regenerates byte-identically; archive hashes the same twice), writes `docs/reproducibility/paper3_release_manifest.json`. (3) `bundle_contents()` delegates to the archive with a floor list asserted so the two cannot drift — **immediately caught two evidence files the archive was missing**. (4) `REPRODUCIBILITY.md`: determinism / freshness / **correctness** kept apart, correctness explicitly **not** certified by either of the others, plus "What is NOT yet reproducible". **Two self-corrections, both tested:** "commit-equality is structurally unsatisfiable" holds only **in-tree** (`tools/prepare_paper_release.py` achieves it out-of-tree for Papers 1–2, and does **not** cover Paper 3); and the first `requirements-paper3.lock` named a **per-session scratch path** in 12 lines, so `docs/reproducibility/constraints-paper3.txt` is now committed, the lock regenerated, and a guard proven to fail on the original. `REPRODUCIBILITY.md` now distinguishes the three lock artifacts (direct-only / transitive / `pip freeze` record). 21 tests; full suite green (1830 passed, 1 skipped). **Remaining: the archival DOI** — a human deposit decision, not a build gap. Papers 1–2 still lack a transitive lock. |
