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
      flow-minimum null (validated separately). **Rung 5 challengers (mo2023_2,
      fasano I/II, lee2023, RC-3b) are Phase 3 — pending those implementations.**
- [x] CHAT: which mechanism survives → `docs/ANALYSIS_P2.md` (§2.2; verdict partial by design — Φ(t) sufficient, discrimination pending Phase 3 rung 5)

## Parallel tracks (not sprint-gated)
- **TB**: §5.8 correspondence — Mo/Ellero (k1 units + volumes), Grudeva
  (repo check first), Egidi (Eq. 4 definitions); Wadsworth already out
- **INTAKE**: gap-target papers as found — G1 (Richards/two-phase), G2
  (Ellero J. Food Eng. 263; Mo 2021/2022), G9 (screen hydraulics), G10
  (extract rheology)
- **Colab**: full-grid Sweeps A/B (already queued); results → CHAT workup
- Phase 3 items (3.1–3.5) schedule after Sprint 9 defines the harness

## Public-value track (PV)
*Parallel workstream to the scientific sprints above. **Spec:** `docs/PUBLIC_VALUE.md`
(this table is the status ledger, PUBLIC_VALUE.md stays the spec — do not duplicate
its content here). **Guardrails:** PUBLIC_VALUE.md §3 are binding; every public
claim regenerates from a pinned commit and carries its evidence-strength label
UNCHANGED (measured / post-fit / verification / qualitative). Reference-strength and
labelled-proxy results stay labelled in public form.*

**Nothing here is built yet — all `not-started`.** This is integration + tracking
only; PV-00 (the public-results export layer) is a future build, not started.

Sequence tiers from PUBLIC_VALUE.md §17. "Sci-dependency / coupling" is the
load-bearing link that keeps the two tracks in sync: **a change on the scientific
side flags the coupled PV row, and vice versa.** Shared items are named so they are
not worked twice under two names — **PV-13 / PV-17 / PV-18 are the PUBLIC face of
gaps G10 / G3 / G1.**

| PV | short name | status | tier (§17) | depends-on | sci-dependency / coupling | spec |
|---|---|---|---|---|---|---|
| PV-00 | public-results export + claim registry | not-started | now | — (foundation) | `harness.py` public-ready fns + `figures.py` + registry/manifest provenance | [§5](PUBLIC_VALUE.md#pv-00--build-a-public-results-export-and-claim-registry) |
| PV-01 | "the first drop is already strong" | not-started | now | — (pairs w/ PV-16) | `dissolution_speed_test` + foster2025_2 infiltration + fraction TDS; **G1 retention analog is REFERENCE-strength — label rides along** | [§5](PUBLIC_VALUE.md#pv-01--the-first-drop-is-already-strong-measured-fractions-plus-a-wetting-front-reveal) |
| PV-02 | "the machine can fake a puck problem" | not-started | now | — (feeds PV-15) | Foster machine mode + `kappa_t_ladder` + `cross_pressure_discrimination` + the leave-one-pressure-out diagnostic (`ANALYSIS_cv_residual.md`) | [§5](PUBLIC_VALUE.md#pv-02--the-machine-can-fake-a-puck-problem-a-null-first-flow-curve-explainer) |
| PV-05 | "adding physics made it worse" | not-started | now | — | `coupled_kappa_t` failed shared-porosity composite (anti-mega-model; Paper-B Fig 4) | [§5](PUBLIC_VALUE.md#pv-05--adding-more-physics-made-it-worse-the-anti-mega-model-story) |
| PV-03 | "a good fit can still be wrong" | not-started | next | — | `ANALYSIS_transfer.md` inventory–kinetics identifiability (flat valley); Pannusch solver, Angeloni | [§5](PUBLIC_VALUE.md#pv-03--a-good-fit-can-still-be-wrong-the-inventorykinetics-flat-valley-interactive) |
| PV-04 | "we killed our favorite result" | not-started | next | — | corrected fine-grind verdict (`ANALYSIS_P2.md` / `P3_hypotheses.md`); `schmieder_interior_max_target`, `result1_magnitude_comparison`, `channeling_interior_max_sensitivity` | [§5](PUBLIC_VALUE.md#pv-04--we-killed-our-favorite-result-a-transparent-analysis-autopsy) |
| PV-06 | cross-pressure mechanism fingerprint | not-started | next | — (feeds PV-15) | waszkiewicz 11-pressure traces + `cross_pressure_discrimination`; Paper-B Fig 3 | [§5](PUBLIC_VALUE.md#pv-06--build-a-cross-pressure-mechanism-fingerprint-map) |
| PV-08 | "Puck Court" evidence dashboard | not-started | next | PV-00 | registry + gates + manifest; Paper-B Fig 2 (evidence matrix, not a leaderboard) | [§5](PUBLIC_VALUE.md#pv-08--create-puck-court-a-public-evidence-dashboard-not-a-winner-leaderboard) |
| PV-15 | model-disagreement experiment recommender | not-started | experiment | PV-02, PV-06 | consumes cross-mechanism disagreement across the harnesses | [§5](PUBLIC_VALUE.md#pv-15--build-a-model-disagreement-experiment-recommender) |
| PV-16 | public first-drip / fraction replication | not-started | experiment | PV-01, PV-15 pilot | PV-01 protocol → public participation (after closed pilot) | [§5](PUBLIC_VALUE.md#pv-16--launch-a-public-first-drip-and-fraction-resolved-replication-study) |
| PV-11 | "your grinder dial is not a unit" | not-started | program | — | G5 dial-non-portability gap + Wadsworth grind map (ledger A9/G5, rule 9) | [§5](PUBLIC_VALUE.md#pv-11--your-grinder-dial-is-not-a-unit-build-a-physical-grind-translation-study) |
| PV-13 | measure espresso-liquor viscosity | not-started | program | — | **PUBLIC FACE of gap G10** (liquor rheology); current G10 is REFERENCE-strength extrapolation — label rides along | [§5](PUBLIC_VALUE.md#pv-13--measure-espresso-liquor-viscosity-the-first-drops-are-not-just-hot-water) |
| PV-14 | dynamic channeling, flow vs pressure | not-started | program | — | `ntube_finite_time_gain`; **BOUNDED by the lateral-coupling PROXY (CARD-BLOCKED, rule 1) — cannot claim physical lateral coupling until a card exists** | [§5](PUBLIC_VALUE.md#pv-14--visualize-dynamic-channel-concentration-under-flow-versus-pressure-control) |
| PV-17 | pump-curve + screen-clogging bench | not-started | program | (validates PV-10) | **PUBLIC FACE of gap G3** (pump curve); also feeds G9 screen-clogging (`g9_series_resistance`) | [§5](PUBLIC_VALUE.md#pv-17--measure-the-machine-and-outlet-pump-curve-plus-screen-clogging-bench-study) |
| PV-18 | coffee-bed retention / continuous wetting | not-started | program | — | **PUBLIC FACE of gap G1** (retention curve θ(ψ)/K(ψ)); the measurement that would replace the reference-strength G1 analog PV-01 uses | [§5](PUBLIC_VALUE.md#pv-18--measure-continuous-coffee-bed-wetting-and-retention-not-just-the-front) |
| PV-07 | compound extraction clocks | not-started | unsequenced (P1) | — | Pannusch solver + Schmieder fractions + transfer analysis (hypothesis generator only, transfer-limited) | [§5](PUBLIC_VALUE.md#pv-07--build-compound-extraction-clocks-and-search-for-same-strength-different-composition-shots) |
| PV-09 | multi-lens "hidden puck" movie | not-started | unsequenced (P1) | — | Foster infiltration + pack_generator + LB solvers + extraction + streamtube/N-tube (parallel labelled lenses, no fake mega-model) | [§5](PUBLIC_VALUE.md#pv-09--produce-a-multi-lens-hidden-puck-movie-without-building-a-fake-mega-model) |
| PV-10 | "a clean basket is not the bottleneck" | not-started | unsequenced (P0/P1) | — | `g9_series_resistance` + basket geometry (gap G9); PV-17 provides the bench validation | [§5](PUBLIC_VALUE.md#pv-10--a-clean-basket-is-not-the-bottleneck-visualize-the-pressure-resistance-budget) |
| PV-12 | temperature explainer | not-started | unsequenced (P1) | — | `g4_temperature_sensitivity` + Schmieder temperature data (gap G4; two closures disagree on SIGN — surface, don't average) | [§5](PUBLIC_VALUE.md#pv-12--temperature-explainer-small-equilibrium-extraction-effect-unresolved-thermal-puck-physics) |

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
