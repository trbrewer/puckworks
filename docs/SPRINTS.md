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
      (backlog 0.3–0.9 side). ⚠ Mo Re overlay needs 0.4 (mo2023) — deferred.

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
      ⚠ cameron-BDF mutual-validation = **deferred** future gate (hard).

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
- [ ] A1 pressure-node fields (p_p/p_h/P_basket/ΔP_bed) per RC-3 node table
- [ ] foster2025_2 Eqs. 2–7 — t_p=0.823 s, t_s=6.669 s, Fig. 15 flow-minimum
      (post-fit); DE1 first-drip triangle rerun (independent) → **RC-3a runnable**
- [ ] §5.9 pressure-node identification for fixture A + Waszkiewicz recorded in manifests
- [ ] 1.8b (S): pannusch machine-driven adapter → RC-4b

## Sprint 8 — extraction harness (CC+CHAT) [2.1, M; needs Sprints 3,5,6 + A5]
- [ ] Matched-input runs: cameron/grudeva/pannusch(TDS) vs Cameron tables,
      egidi bracket, Schmieder kinetics, Grudeva vials, Waszkiewicz fractions —
      per-dataset residuals with strength tags; §5.6 dissolution-speed test
- [ ] CHAT: results workup + P3 hypothesis file update (2.3)

## Sprint 9 — κ(t) discrimination harness (CC+CHAT) [2.2, M; needs Sprints 1,7 + A8]
- [ ] A8 per-depth-cell porosity/fines fields
- [ ] P2 null-first ladder implementation on Waszkiewicz + fixture-A traces;
      RC-3b enters as rung 5
- [ ] CHAT: which mechanism survives — feeds the paper

## Parallel tracks (not sprint-gated)
- **TB**: §5.8 correspondence — Mo/Ellero (k1 units + volumes), Grudeva
  (repo check first), Egidi (Eq. 4 definitions); Wadsworth already out
- **INTAKE**: gap-target papers as found — G1 (Richards/two-phase), G2
  (Ellero J. Food Eng. 263; Mo 2021/2022), G9 (screen hydraulics), G10
  (extract rheology)
- **Colab**: full-grid Sweeps A/B (already queued); results → CHAT workup
- Phase 3 items (3.1–3.5) schedule after Sprint 9 defines the harness

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
