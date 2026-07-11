# Phase 1/2 analysis writeups (CHAT deliverable: items 2.1, 2.2, 2.3, 1.4)

Companion to the code harnesses; every number below is reproducible from
`puckworks.harness` or `puckworks/validation/slow/`. Validation-strength tags
follow ROADMAP §0 and are load-bearing: nothing here upgrades an agreement
beyond its tag.

---

## 2.1 Extraction-harness workup (Sprint 8)

**Normalization hazards, surfaced not merged.** Three c_sat values coexist
across lineages (170 / 212.4 / 224 kg m⁻³) with three inventory conventions
(per-bed-volume, per-grain incl. internal pores, per-solute). The harness
prints them side by side on every run; any cross-lineage comparison below is
conditional on this table and none of it is averaged away.

**Strength-tagged results.**

| comparison | result | strength | reading |
|---|---|---|---|
| pannusch ↔ Schmieder kinetics | MAPE 6.4% (caffeine), 10.2% (trigonelline), 7.2% (5-CQA), 6.7% (TDS) | post-fit reconstruction | transcription + solver fidelity confirmed; says nothing about predictive skill |
| grudeva ↔ per-vial masses | 2.89 g vs 2.95 g total solubles | post-fit reconstruction | same: seven quantities were fitted to these 13 shots |
| liang ceiling ↔ cameron ceiling | 0.215 vs 0.245 | independent (distinct quantities, K<1) | consistent ordering; not a contradiction since the ceilings measure different inventories |
| cameron ↔ egidi EY bracket | 15.4% vs [19.1, 22.6] | independent bracket | **out of bracket, low — the headline discrepancy** |

**The Cameron-reads-low finding.** At the matched configuration Cameron's
solver lands 3.7 EY points below the egidi bracket floor while its own
inventory ceiling (24.5%) sits above the bracket — so the model is not
ceiling-limited here; it is kinetics- or convention-limited. Candidate
explanations, deliberately unadjudicated: (a) the per-bed-volume inventory
convention vs egidi's per-grain c₀ = 200 kg m⁻³; (b) diffusion-limited boulder
kinetics that §5.6 independently disfavors; (c) configuration mismatch in the
mapping (egidi's brew geometry vs Cameron's espresso tables). House rule
applies: this is reported as a discrepancy, not "fixed". The §5.6 result makes
(b) the leading suspect but does not convict it.

**§5.6 dissolution-speed discriminator.** Waszkiewicz TDS fractions give
early/peak = 0.968 (24.4% vs 25.2% TDS): the first liquid out is already at
~97% of peak concentration. Boulder-diffusion timescale at Cameron parameters
is ~23 s — if extraction were boulder-diffusion-limited, early TDS would sit
well below peak. Verdict: **near-instant dissolution favored** in this
dataset, consistent with Grudeva's saturated-plateau mechanism (fast fines
saturate the liquid) and in tension with Cameron's rate picture. Strength:
independent, single dataset, one brewing configuration — a discriminator, not
a universal law.

**Grudeva G1/convergence (closes RECONCILIATION LOG Issue 1).** Resolution
study: s_d⁻¹(1) = 2.80/2.83/2.82 and totals 2.92–2.98 g across N = 150→400 —
converged (verification). ε-form discrimination at the same configuration:
no-ε form gives s_d⁻¹(1) = 2.83; the printed-ε forms (10⁻², 10⁻³) give
0.44–0.45 — the saturated plateau does not merely shorten, it **collapses**,
because the printed ε effectively deletes the liquid-phase storage term. The
adjudication is no longer only derivational: implemented as printed, the model
loses its signature qualitative feature. Correspondence question (a) can now
cite an executed computation.

---

## 2.2 Which κ(t) mechanism survives? (Sprint 9 — partial verdict by design)

**The null that must be beaten first.** Foster's machine mode (pump +
headspace, zero bed mechanisms) reproduces the mid-shot flow minimum:
min(Q_p, f)/Q_m = 0.181 at ~2 s, RMSE 1×10⁻⁴ against the digitized Fig. 15.
The classic "flow dips then recovers" observation therefore carries **no
evidential weight for any bed-side story** (swelling, compaction, fines,
erosion) on its own. This null is the ladder's rung 2 and the single most
clarifying result of the phase.

**The ladder on Waszkiewicz 9-bar rising flow.**

| rung | mechanism | RMSE (g/s) |
|---|---|---|
| 1 | constant κ | 0.603 |
| 3 | static κ(P) | 0.603 |
| 4 | dissolution-driven Φ(t) | **0.113** |

Rung 3's exact tie with rung 1 is itself informative: at constant 9 bar a
static pressure dependence is observationally identical to a constant — the
rising flow is *time* structure, and only a time-dependent bed can source it.
Rung 4 beats the flat floor 5.4×: **a time-dependent bed mechanism is
genuinely required, and dissolution-driven porosity growth is sufficient.**

**What this does and does not settle.** Sufficient is not unique. The
challengers — mo2023_2 fines migration, fasano I/II, lee2023
dissolution–flow instability, and RC-3b poroelastic κ(P, Φ) — are Phase 3;
until they run, the verdict is: *mechanism needed; Φ(t) fits; discrimination
pending.* Two design notes for the Phase-3 discrimination so it is decisive
rather than another tie:

1. **Cross-pressure generalization is the discriminator Waszkiewicz makes
   possible.** Eleven pressures exist. Fit each mechanism at 9 bar only, then
   predict the other traces. Dissolution-Φ(t) predicts flow-history-integrated
   (mass-removed) structure; poroelastic κ(P, Φ) predicts partially reversible
   pressure structure; fines transport predicts depth-asymmetric, largely
   irreversible structure. They degenerate at one pressure and separate across
   the set.
2. **Relation to the streamtube erosion story (brewer2026 Rung B):** rung 4's
   success is consistent with erosion but does not select it — bulk
   dissolution opening porosity is the more parsimonious reading at fixed
   9 bar. The erosion signature remains flow *acceleration concentrated in
   fast tubes*; that requires per-tube or per-depth observables, not a single
   flow trace.

---

## 2.3 Fine-grind-dip verdict (P3)

Scoreboard against `docs/P3_hypotheses.md`, folding in the harness evidence:

- **Disfavored as a primary cause:** pure boulder-diffusion kinetics
  (hypothesis-adjacent, via §5.6 — the liquid saturates too fast for slow
  boulder kinetics to carry a grind-direction reversal by themselves).
- **Alive and now instrumented:** #1 static channeling (grindmap supplies the
  ⟨R⟩/S chain; the σ(φ₁) per-grind sweep is runnable) and #2 incomplete
  wetting (foster components gated; but its sharp-front model *declines the
  coarse grind*, so this hypothesis genuinely lives in gap G1,
  continuous-saturation flow — not yet on file).
- **Untested:** #3 lee2023 (with a documented required negative-result gate)
  and #4 size-exclusion inventory (needs 0.5 intake). #5 pannusch is a
  pointer, not a mechanism, per its card.
- **Shared constraint standing over all five:** schmieder2023's non-monotonic
  cup mass peaking at GL 1.7 at fixed flow. Nothing currently on file
  reproduces it, because nothing capable of it has been run against it.

**Verdict: open, honestly — but the program is now closed-form.** The two
computations that most reduce uncertainty, in order: (i) the σ(φ₁) sweep
(streamtube × grindmap → does a monotone σ(grind) reproduce the schmieder
peak?); (ii) a minimal continuous-saturation wetting model for G1 (Richards-
type), which is the only way #2 gets a quantitative shot. Note also that #1
and #2 are not mutually exclusive — incomplete wetting is the k→0 atom that
the lognormal explicitly lacks (foster card); a composite distribution with a
wetting-failure mass at zero is a legitimate unified candidate. Cheap
experimental discriminator available to us: per-grind first-drip timing on
the DE1 (wetting delay moves it; static channeling does not).

---

## 1.4 moroney ↔ cameron mutual validation: matched-parameter design

**Why it is regime-blocked as-is.** Cameron: espresso, ε ≈ 1.6, clean-water
initial condition. Moroney surrogate: drip filter, ε = 0.127, pre-saturated
bed, leading-order asymptotics with O(ε) ≈ 13% truncation. Neither can visit
the other's home regime — the surrogate diverges at ε ~ 1, and Cameron's flux
tables do not extend to filter conditions. Comparison at either native
configuration would measure regime mismatch, not model agreement.

**Design: meet in the surrogate's valid domain, sweep toward its edge.**

1. *Common configuration.* Moroney's own drip-filter parameter set, mapped
   through the adapter: shared c_sat lineage already holds (both 212.4,
   per-bed-volume — the one cross-lineage pairing the hazards table
   permits), same φ fields, grain radii, bed depth; impose the same q
   directly (bypass Cameron's flux table entirely — MachineState fixed-q
   path).
2. *Two solver switches on the Cameron side (small, flagged):* pre-saturated
   initial condition c_l(0) = c_sat (matching Moroney's well-wetted start),
   and q imposed rather than table-derived. Both are config flags, not
   physics edits.
3. *Sweep.* Vary q to run ε = t_a/t_d across {0.05, 0.10, 0.127, 0.20, 0.30}.
   Observables: outlet concentration trace and cumulative EY(t).
4. *Acceptance logic — asymptotic, not pointwise.* At each ε, tolerance =
   truncation budget + grid budget: |ΔEY| ≤ 1.5·ε·EY + 0.15 pts. Mutual
   validation passes if (a) agreement holds within budget for ε ≤ 0.2 and
   (b) the divergence *grows ~linearly in ε* — i.e., the disagreement is
   attributable to the surrogate's own declared truncation. A flat or
   ε-independent offset instead indicates a real model difference and fails.
5. *Directionality and strength.* Cameron BDF acts as the "full model"
   reference (Moroney's full model is not implemented); this is
   **verification-strength mutual validation** — two independent codebases,
   overlapping asymptotic regime — and must be tagged so. It is not
   independent experimental validation of either.

Deliverable for the CC session: `harness.moroney_cameron_matched(eps_grid)`
returning the per-ε table plus the linearity diagnostic, and a slow-gate
wrapping criterion (a)+(b). Estimated effort S given both components exist.

---

*Status implications:* 2.1 and 2.2 complete (2.2 verdict partial by design,
pending Phase 3); 2.3 remains a living verdict with its two next computations
named; 1.4 design ready for a CC session. ROADMAP §7.1 entries and SPRINTS
ticks accompany this file's commit.
