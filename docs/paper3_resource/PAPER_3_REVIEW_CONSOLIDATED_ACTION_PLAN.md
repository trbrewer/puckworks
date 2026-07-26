# Paper 3 — Consolidated review action plan (2026-07-25)

Consolidates the two reviewer documents in this directory into one prioritized tracker:

- **Base full-manuscript review** — `PAPER_3_DETAILED_REVIEW_2026-07-25.md` (audit boundary
  `93358f8`, *before* the gate-4 work). 18 major comments **MC1–MC18** + P0/P1/P2 plan + a
  16-row consistency/stale-count audit. Overall: **major revision before preprint/submission**.
- **Update review** — `PAPER_3_UPDATED_DETAILED_REVIEW_2026-07-25.md` (boundary `b8c84be`, *after*
  PR #175). 16 change-specific comments **U1–U16** on the new §4.5 two-regime paragraph, plus a
  status table confirming **none of MC1–MC18 is resolved**. Overall: **keep the idea, rewrite &
  properly evidence it; major revision of the full paper continues**.

Both reviews are careful and reproduced our producers exactly. This plan does **not** re-litigate
their scientific verdicts; it records disposition and sequencing.

**Legend:** ✅ done in the consolidation PR · ⏭ deferred (needs its own scoped PR) ·
❓ needs a **Tim decision** · 🔁 needs the generation-pipeline fix (MC2).

---

## Part A — Change-specific comments (U1–U16) on the §4.5 two-regime paragraph

The paragraph and its supporting producers/tests/card were the subject of the update review.
Accuracy corrections are **done in this PR** (they are corrections to recently-merged work of ours):

| ID | Point | Disposition |
|---|---|---|
| **U1** | Name & cite Maille 2024 / Cameron 2020 / Roman-Corrochano 2017 | ✅ named in prose. ⏭ adding Maille & Roman to the **reference list** rides with MC9 (references). |
| **U2** | "grind-independent constants" conflates absolute vs dimensionless | ✅ paragraph, card, code + `finding` now say only the **weight & ratio** are grind-invariant; **absolute constants vary ~1.9×**. New field `absolute_timescales_are_grind_independent=False`; new test asserts absolute constants vary. |
| **U3** | Roman result is **fine-class only**, not "its own particle size" | ✅ paragraph/card/code restrict to the selected 20 µm fine class; new fields `particle_class`, `radius_m`, `coarse_class_status="not_evaluated_missing_radius"`; note larger R∝τ² could enter Maille's bands. Coarse d[4,3] still **not fabricated**. |
| **U4** | "single diffusion mode" is mathematically loose | ✅ replaced everywhere with **"one physical diffusion process"** (a sphere solution is many eigenmodes). |
| **U5** | Cameron "effectively one-regime" overstated (gs 2.5 separates) | ✅ replaced 50 % distance heuristic with a **one- vs two-exponential** comparison; report `single_exp_like` (3 of 4), `needs_model_selection` (gs 2.5), `two_exp_r2_gain`. Robust claim retained: **no fitted λ_fast in Maille's fast band**. New test pins gs 2.5 as *not* single-timescale. |
| **U11** | `two_regime_ports_to_roman` hard-coded | ✅ now **derived** from `shape_universal ∧ two_regime_beats_one ∧ none_in_maille_bands`. |
| **U14** | Stale docstring / test comment / language | ✅ cameron docstring "rights-deferred" line corrected; cameron test comment fixed (it checks `r2_two`, the bi-exp fit); "Crank diffusion mode" language replaced. |
| **U15** | "flow-limited" not established by the fit | ✅ replaced with **"aggregate flowing-bed response"** in paragraph/card/code. |
| **U16** | Disclose curves are **model-generated / qualitative** | ✅ paragraph now states model-generated + "qualitative model-to-model probes, not validation"; card/code already did. |
| **U6** | Identifiability (multistart, profile likelihood, bootstrap) beyond R² | ✅ #179: cameron MULTISTART `phi_multistart_span` + `non_identifiable` (finer grinds span φ≈0–1) alongside one-vs-two-exp. Full profile-likelihood/bootstrap still a deeper option, but the non-identifiability is demonstrated + tested. |
| **U8** | Roman fitting-protocol sensitivity (window, bath ratio, radius) | ✅ #179: `roman_protocol_sensitivity()` reproduces the reviewer's window (ratio 15.8→8.6) + bath-ratio tables from the registered solver; surfaced in §7.5. |
| **U9** | Define **portability as a vector**, not a Boolean | ✅ #179: both producers carry a six-dimension `portability_vector` (observable/mechanism/population/estimation identity; numerical compatibility; predictive transfer) + derived `portability_verdict`. |
| **U10** | Add **Paper 3 claim records** + generated result bundle for the two producers | ✅ **CLOSED 2026-07-25.** #179 landed the bundle; the maille **component registration** then removed the blocker, so both claims are now **formal adjudicated `EVIDENCE_LINKS` records** carried by `gate_maille_timescale_portability_cameron` / `..._roman` on `maille2024.two_regime` (evidence reconciles `--strict --scope paper3`). `timescale_semantics_bundle()` remains the richer machine-readable rendering of the same two claims, not a parallel unregistered set. |
| **U12** | Separate descriptive shape reuse from physical transfer | ✅ paragraph now says the shared form is a useful **descriptive** basis, not a physical contract. |
| **U13** | Move quantitative detail to a subsection/figure/supplement | ✅ U13 PR: §4.5 condensed to the principle; detail moved to new **§7.5 + Table 4a**. Figure (vs table) still open under MC12. |
| **U7** | State all protocol choices in the manuscript | ✅ partially (paragraph now names 400 s/τ=0/20 µm fine class); full method table ⏭ P1 with MC12. |

**Net:** all *accuracy/integrity* fixes (U1 prose, U2, U3, U4, U5, U11, U12, U14, U15, U16, U7-partial)
are done; the *added-rigor* asks (U6, U8, U9, U10, U13) are P1 and tracked below.

---

## Part B — Full-manuscript comments (MC1–MC18) with base P0/P1/P2 mapping

| ID | Title | Priority | Disposition |
|---|---|---|---|
| **MC6** | Infiltration "independently gated" overclaim | **P0 (immediate)** | ✅ **done in this PR** — Table 6 row reworded to "same-shot compatibility check across a predeclared porosity bracket — not an independent prediction". (Reviewer also wants a wider "independent/parameter-free/validation" sweep of figures/captions/notebooks ⏭.) |
| **MC1** | Decide publication genre | P1 | ✅ **DECIDED 2026-07-26 — Route A, methods/resource article**, matching the review's own P1-13 recommendation. The demonstrations, the failed composition and the defect-injection evaluation stay in the paper; in return it must meet methods-article expectations for evaluation and uncertainty, which §10 now partly discharges. Consequences accepted: figures (MC12) remain the submission blocker, and a 15–20 % trim of §2/§4 is owed. |
| **MC2** | Repair manuscript-generation pipeline (counts/tables generated + CI) | P0 | ◑ counts are now bound to the live registry/manifest with a **CI drift guard** (`test_paper3_manuscript_consistency`), proven three times since (27 components; 105 then 106 manifest rows). Remaining: the **freeze target** (❓ Tim). |
| **MC3** | Rewrite architecture around **schema v2** (`kind` deprecated) | P0 | ✅ §§2.1/3.2/3.3 rewritten; Table 1 + Appendix A generated from the live registry. |
| **MC4** | Separate evidence relation / outcome / artifact role / badge | P0 | ✅ Table 3 landed earlier; **the implementation now matches (2026-07-26)** — `PublicClaim` gained an `outcome` field and PV-03's compound `"negative validation"` label was decomposed into `qualitative` + `negative`. `validate()` rejects any compound label if reintroduced. |
| **MC5** | Fix abstract "weakest load-bearing link" vs evidence-vector | P0 | ✅ abstract reworded in the same P0 batch. |
| **MC7** | Define "executable" per layer (availability matrix) | P1 | ⏭ new machine-readable matrix. |
| **MC8** | Implemented capability vs architectural intent | P1 | ⏭ implementation-status table. |
| **MC9** | Rigorous **related work & novelty** (FAIR4RS, PROV, RO-Crate, model cards…) | P1 | ✅ #180: new §12 (6 traditions) + refs [14]–[22]; novelty scoped to joint operationalization. |
| **MC10** | **Evaluate the framework** (defect corpus + mutation tests) | P1 | ✅ **DONE (2026-07-26).** New §10 + `puckworks/paper3/defect_injection.py`: 18 realistic defects injected into isolated copies, 12 detected / 6 not. **The benchmark found a previously unknown gap**: the A7 range guard does NOT catch a permeability supplied in mm² (or cm²) anywhere in the espresso range, because a range check cannot separate units whose scale factor is smaller than the quantity's own 12-order spread; darcy IS caught. The corpus deliberately retains its known misses (agreement≠correctness, untyped pressure-node identity, physically-wrong-but-valid constants, process-only rules) and a test fails if they are removed or if any outcome changes. 9 tests. |
| **MC11** | Reduce duplication with companion papers (claim ownership) | P1 | ✅ **DONE (2026-07-26).** The repository already had `docs/CLAIM_OWNERSHIP.md`; the review's point was that no ownership table appeared **in the manuscript**, so a reader could not check the division. New §2.4 states, per claim, which paper owns it and what role it plays here — physical conclusions are asserted once, in the paper whose design supports them, and this paper asserts only methodological claims, citing companion results as worked examples of the architecture. Shared numbers come from shared producers, so they cannot diverge without a CI failure. |
| **MC12** | Complete & consolidate **figures** | **P0 (submission blocker)** | ✅ **DONE (2026-07-26).** All **seven** figures are generated by `puckworks/figures_paper3.py`, not specified: every number comes from a producer (registry inventory, `evidence_graph.evidence_vectors`, `CONSTANT_CONFLICTS`, `harness.kappa_t_ladder`, `coupled_kappa_t`, the campaign register, and the generated scorecard). Raster **and** vector emitted together; **five tidy source-data CSVs** so a reviewer can re-plot without the solver stack; and **alt text for every figure** — the accessibility statement promised text alternatives and no pipeline in the repo emitted any until now. 10 tests, including ones that check the CSVs equal the live producers. **Two of the three review-stated prerequisites had been cleared earlier the same day** (Fig 2 needed the evidence schema settled; Fig 5 needed the PV-05 numbers and sign semantics reconciled), and Fig 7 needed MC17. Remaining under P0-12: build from a frozen release rather than the working tree — ✅ **now closed by the REL row below**; only the archival DOI is left, and that is a deposit decision, not a build gap. |
| **MC13** | Strengthen quantitative/statistical reporting; reconcile RMSE 0.573 vs 0.603 | P1 | ✅ **0.573-vs-0.603 resolved:** 0.603 survives only in three ARCHIVED review/outline documents (`PAPER_OUTLINE.md`, `puckworks_paper_outline_review.md`, `PAPER_B_DRAFT_updated_detailed_review.md`); it was the flat null computed on the ladder's older effective 15–100 s window. Both live manuscripts report **0.573** from one producer on one declared 15–95 s window (`harness.kappa_t_ladder.rung1_const_kappa`), so nothing needs reconciling in the paper — the stale value is historical. **A second, real collision was found and fixed:** the composite RMSE (0.648) and the static κ(P) RMSE (0.648) are the SAME number to 1e-9, and both papers reported them as independent facts. The cause is structural — the imported swelling branch drives the shared porosity below ε₀ across 100 % of the window, so the dissolved-mass proxy sits on its floor, Φ→0, and the closure returns its own Φ→0 limit, the static curve. The composite prediction is CONSTANT to numerical precision. `composition_residual` now reports `phi_floor_fraction_in_window`, `predicted_flow_spread_g_per_s` and `reduces_to_static_limit`; both manuscripts state that the composition **removes** the temporal prediction rather than merely degrading it; 2 tests pin it. |
| **MC14** | Reconsider external community-corpus / governance | P1 | ✅ Tim decided **fully document** (the §7.4 ingestion demo makes the corpus load-bearing). §6.6 expanded with ~11 governance items (lawful basis/grant scope, human-subjects determination as OPEN, minimization/retention, access control, deletion/withdrawal, small-cell/linkage, free-text, hash threat model, incident response, snapshot provenance, aggregate disclosure) + reframed as **pseudonymized, not anonymized** (the salted hash is a persistent linkage key). |
| **MC15** | Make curated-corpus method reproducible | P1 | ⏭ method + denominators. |
| **MC16** | Scope & limits of typed contracts (per-layer defect table) | P1 | ✅ MC16/17/18 PR: new §4.1 Table 2 (per-layer catches + residual risk; permeability window = coarse sanity check). |
| **MC17** | Generate & rename named-shot scorecard; define `Fo_F` | P1 | ✅ **DONE (2026-07-26).** `Fo_F` was defined earlier (§4.4, diagnostic not correction). The scorecard is now generated by `paper3/named_shot_scorecard.py` and spliced into the manuscript between markers, with a `--verify` mode and a CI guard. **Statuses are DERIVED** from each selected component's scoped evidence vector (6 of 10 rows; the other 4 have no component and are declared), and numbers are executed from producers. Regenerating it exposed a defect: the row claiming an **"approximately 6.6 % ramp shift" has no producer anywhere in the repository**. It is **withdrawn** rather than reproduced, and a test keeps it withdrawn. The generated table is also richer than the hand-written one — the Flow law row carries three relations where the prose asserted one. 11 tests. |
| **MC18** | Temper cross-domain generalization | P1 | ✅ §13.4 reframed as a proposed pattern demonstrated in espresso (hypothesis), not empirical generalization. |
| **REL** | Build the paper from a **frozen release**, not the working tree (the residual under MC12) | **P0 (submission blocker)** | ✅ **DONE (2026-07-26).** Four pieces. (1) The figures, five source-data CSVs and `ALT_TEXT.md` were **absent from the deterministic archive** — added, 147 → **149 members**, byte-identical across two builds, still verifiable without the source checkout. (2) A **`release` verb** (`python -m puckworks.paper3.build release`) requiring a clean tree and proving **freshness by recomputation**: every generated artifact regenerates byte-identically and the archive hashes the same twice. Writes `docs/reproducibility/paper3_release_manifest.json`. (3) `bundle_contents()` now delegates to the archive with a floor list asserted, so the two cannot drift — this immediately caught **two evidence files the archive was missing**. (4) `REPRODUCIBILITY.md`, which separates determinism / freshness / **correctness**, states that correctness is *not* certified by any of them, and carries a **"What is NOT yet reproducible"** section. **Two self-corrections:** "commit-equality is structurally unsatisfiable" is true only **in-tree** — `tools/prepare_paper_release.py` achieves it out-of-tree for Papers 1–2 and does **not** yet cover Paper 3 (both facts now tested); and the first transitive lock named a **per-session scratch path** in twelve places, so the constraints are now committed at `docs/reproducibility/constraints-paper3.txt` and a guard is proven to fail on the original. 21 tests. **Remaining is the archival DOI**, which is a human deposit decision rather than a build gap. |

---

## Consolidated stale-count / consistency audit (base review §4, verified 2026-07-25)

| Item | Manuscript says | Repo actually (verified) | Fix |
|---|---|---|---|
| Component total | ~~25~~ **27** | 27 (`registry_counts.json`, after the maille2024 registration) | ✅ manuscript + generated Table 1 updated; CI drift guard binds them to the live registry |
| **Manifest total** | ~~70~~ **106** | **106 logical rows** (gloess2013 + waszkiewicz per-brew intakes) | ✅ manuscript updated; the CI drift guard now fails on any divergence |
| **Execution roles** | ~~11/13/1~~ **12 runtime / 15 calibration** | **12 runtime / 15 calibration / 0 / 0** (synthesis is a *provenance* class) | ✅ Table 1 regenerated; synthesis-as-role removed and guarded by a test |
| Registry schema | §3.2 foregrounds `kind` | schema v2: `kind` deprecated | ✅ §3.2/§3.3 rewritten around the v2 axes (MC3) |
| Evidence taxonomy | "Independent external", "Negative validation" | code: `controlled_independent`; no `negative_validation` strength | ⏭ Table 3 (MC4) |
| **Infiltration** | "independently gated" | same shot supplies pressure + fitted κ + evaluation | ✅ **fixed this PR** (MC6) |
| Release/readiness (Table 7) | editable-install-only; release owed | `v0.3.0` wheels/sdist, public Colabs, API docs, governance files exist | ✅ **rebuilt (2026-07-26)** against the verified tree (schema 0.7 not 0.6; 5 public notebooks; 20 CI workflows; CONTRIBUTING/CODE_OF_CONDUCT/CHANGELOG/CITATION.cff/issue templates present) and now names the four real blockers: no archival DOI, no pinned environment, no external reproduction, curated corpus |
| Figures | 7 specified | none embedded | ⏭ submission blocker (MC12) |
| Manuscript date | ~~15 July~~ **25 July 2026** | latest material merged 25 July 2026 | ◑ date updated; freezing to a **tag** still needs the MC2 freeze-target decision |

---

## What is DONE in the consolidation PR

1. **All §4.5 two-regime accuracy fixes** (U2, U3, U4, U5, U11, U12, U14, U15, U16; U1 & U7 partial):
   paragraph rewritten; PV §7.14 softened to match; `docs/cards/maille2024.md` gate 4 + status
   corrected; `puckworks/analysis/maille2024.py` producers reworked (one-vs-two-exp for cameron,
   derived roman verdict, fine-class fields, "physical diffusion process" language);
   `tests/test_maille2024.py` updated + 1 new test (gs 2.5 not single-timescale).
2. **MC6 infiltration overclaim** reworded in the manuscript (evidence integrity; both reviews flag
   it as immediate).
3. **This tracker** + both review docs intaken.

## What needs a Tim DECISION before the next batch

- **MC1 — publication genre** (JOSS short / JORS resource / full methods). Sets the length target and
  how much espresso detail stays. *Everything downstream (figure count, related-work depth, what
  moves to companion papers) keys off this.*
- **MC14 — external community-corpus section**: move to a data-governance paper, remove, or fully
  document the ethics/governance.
- **MC2 freeze target**: which tag/commit to pin the manuscript to.

## Recommended sequencing (after the genre decision)

1. **P0 generation/consistency batch** (MC2 + MC3 + the stale counts + date freeze): wire manuscript
   counts/tables to the generated artifacts + a CI drift test, rewrite §3.2 around schema v2,
   regenerate Table 1, update the date. This kills the whole stale-count class at once (and is the
   reviewers' single most-emphasized credibility issue).
2. **P0 localized integrity edits** (MC4 Table 3, MC5 weakest-link, remaining MC6 sweep).
3. **P1 rigor batch** for the gate-4 result (U6/U8/U9/U10/U13 + MC13): identifiability + sensitivity
   bundle, portability-as-vector, two claim records, move quantitative detail to a subsection/figure.
4. **P1 structure batch** (MC7/MC8/MC9/MC10/MC12/MC15): availability matrix, related work, framework
   evaluation, figures, corpus method.
5. **P2** archive/DOI/clean-room reproduction.
