# Claim ownership — 3-paper portfolio fork

*Created 2026-07-14, executing the fork authorized against
`docs/PUBLICATION_STRATEGY_REVIEW.md` (§14). This is the authoritative map of which
publication **owns** each existing Puckworks claim/result. It exists to prevent the same
claim being made in two papers and to keep each claim in the venue where its evidence
chain is strongest.*

**Guiding principle (strategy §Executive):** *preserve all analyses, but publish each
claim in the paper where it has the clearest question, strongest evidence, and correct
audience.* **Reuse the work, not necessarily the current manuscript structure** — the
existing `PAPER_B_DRAFT.md` is retained intact as the broad technical synthesis and as
the source the forks draw from; nothing is deleted and no analysis code is moved.

## Portfolio

| # | Paper | Doc | Status |
|---|---|---|---|
| A | **The Cup Hides the Clock** — observation resolution & practical identifiability | `PAPER_A_DRAFT.md` | complete + submit (scope-frozen; 5th review in flight) |
| B2 | **One Flow Curve, Many Causes** — null-first temporal inference & perturbation design | `PAPER_B2_TEMPORAL_OUTLINE.md` | fork scaffold (recut from `PAPER_B_DRAFT.md`) |
| 3 | **Puckworks** — executable, provenance-aware evidence registry | `paper3_resource/PAPER_3_PUCKWORKS_OUTLINE.md` | develop as methods/resource paper |
| 4 | **Spatial concentration & control mode** (future) | `future/PAPER_4_SPATIAL_CONTROL_NOTE.md` | deferred until physics + data mature |
| — | Broad Paper B (superseded as a publication unit) | `PAPER_B_DRAFT.md` | **retained as technical synthesis + fork source; not itself submitted** |

## Claim → owning paper

| Current claim / result | Current home | Owner | Notes |
|---|---|---|---|
| Whole-cup endpoint reconstructs while inventory×rate stay weakly localized (practical identifiability) | Paper A R2 | **A** | core thesis |
| Fraction-resolved observation localizes the rate more than the aggregate (positive control) | Paper A §6 | **A** | same-model info demo (inverse-crime tier) |
| Named-solute blind MAPE 26.3 % (proxy-inclusive 22.7 % secondary) | Paper A R1 | **A** | 5th-review A-07 |
| Cross-grind endpoint prediction ≈ level-only null (8.2 % vs 8.6 %; worse 50/108) | Paper A R3 | **A** | endpoint stability, NOT mechanism transfer |
| Table 7 orthogonal inventory → conditional rate intersection (0.95; ±10 %→0.60–1.76) | Paper A R2 | **A** | conditional, not a CI |
| Waszkiewicz external target-profiled TDS shape localization | Paper A §6 | **A** | monotone-mass operator fixed (A-03) |
| Foster machine-only model reproduces a mid-shot flow minimum (published model curve, not data) | Paper B R2 | **B2** | Fig 1 of narrow B |
| κ(t) null-first ladder: Φ(t) beats constants, ties flexible cubic (block/window robust) | Paper B R2 | **B2** | core of narrow B |
| Cross-pressure leave-one-pressure-out + residual fingerprints | Paper B RC-3b | **B2** | within-campaign robustness |
| Isolated swelling branch predicts wrong-sign throttling at fixed pressure | Paper B Fig 3d | **B2** | sign/compatibility constraint |
| Discriminating experiments (pressure step / reversal / rebrew / spatial / first-drop) | Paper B / protocols | **B2** | closing falsifiable program |
| Typed observable/unit contracts; no silent field repurposing | `contracts.py` | **3** | methods contribution |
| Observable/unit linting (c_sat 170/212/224; pressure-node; TDS-proxy episodes) | ledger / gates | **3** | Demonstration 1 |
| Null-first model comparison as a **method** | Paper B R2 (reused) | **3** | Demonstration 2 (cite B2 for the science) |
| "More physics worsens a reconstruction" — failed extraction+swelling composition | Paper B Fig 4 | **3** | Demonstration 3 (negative result) |
| Schmieder RSM / grind-response audit | Paper B R1 | **3** | resource demo / context, not a physics headline |
| Broad mechanism evidence matrix | Paper B Fig 2 | **3** | evidence-taxonomy figure |
| Provenance/evidence tiers; manifests; claim bundles; strict release verification | ROADMAP §0/§7 + build | **3** | reproducibility architecture |
| Experiment-design-from-disagreement output | harnesses / PUBLIC_VALUE | **3** | Experiment-design section |
| End-to-end named-shot scorecard (PV-19) | PUBLIC_VALUE | **3** | evidentiary accounting demo |
| N-tube finite-time flow concentration; floor test; switching convergence | Paper B R3 | **4** | exploratory; deferred |
| Control-mode (flow vs pressure) & lateral-coupling proxy behaviour | Paper B R3 | **4** | needs a physical lateral operator (CARD-BLOCKED G-lat) |
| Fine-grind-dip anomaly as a central narrative | Paper B | **4** | demote from B2; future |

## Rules

1. A claim appears as a **headline** in exactly one paper. It may be **cited** (not
   re-derived) by another (e.g. Paper 3 cites B2 for the null-first science while using
   the ladder as a method demonstration).
2. Moving a claim's publication home does **not** move its code: the analysis stays in
   the shared registry (`puckworks/`), which is the point of Paper 3.
3. The broad `PAPER_B_DRAFT.md` is frozen as a synthesis/source; edits for the forks land
   in the new outline docs, not by gutting it.
4. Update this table whenever a claim is reassigned; it is the single source of truth for
   portfolio scope.
