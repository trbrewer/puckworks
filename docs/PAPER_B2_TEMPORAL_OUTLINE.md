# Paper B2 — One Flow Curve, Many Causes (narrow temporal-inference paper)

*Fork scaffold created 2026-07-14 per `PUBLICATION_STRATEGY_REVIEW.md` §3.7–3.11.
This is the **plan**, not a manuscript. It recuts the strongest portion of the broad
`PAPER_B_DRAFT.md` (retained intact as the synthesis/source). Claim ownership is fixed
in `CLAIM_OWNERSHIP.md`.*

**Title:** *One flow curve, many causes: null-first inference for machine and porous-bed
dynamics in espresso.* (Alt: *What an integrated flow trace can identify in an evolving
porous bed.*)

**Primary claim (maximum defensible):** *An integrated flow trace can establish the need
for temporal dynamics relative to specified static nulls, but it does not uniquely
identify the underlying bed mechanism; controlled perturbations provide greater
discrimination.*

**Verb discipline (inherited):** "reconstructs / is consistent with / requires temporal
flexibility"; never "identifies / proves the mechanism / channeling instability."

## Structure (§3.8)

- **Introduction** — flow-curve shapes are read mechanistically; similar shapes arise
  from machine *and* bed processes; reconstruction ≠ identification; null-first ladder +
  held-out pressure tests; objective = discriminating experiment design.
- **Data & observable definitions** — Foster machine model; Waszkiewicz flow/TDS
  pressure campaign; strict separation of measured traces vs published model curves vs
  digitized reconstructions; pressure/flow/time/concentration conventions; scoring
  windows + preprocessing.
- **Model-comparison ladder** — machine-only; constant/static-κ(P); time-varying Φ(t);
  flexible temporal null (cubic); residual + window-sensitivity + block-length
  sensitivity (already implemented, `result2_residual_diagnostics`).
- **Cross-pressure assessment** — shared calibration vs leave-one-pressure-out;
  per-pressure held-out metrics; residual fingerprints; explicit scope.
- **Sign & compatibility constraints** — isolated resistance-increasing (swelling) branch
  at fixed pressure predicts wrong-sign throttling; does NOT exclude swelling/fines in a
  coupled bed; optional concise failed-composition pointer (headline owned by Paper 3).
- **Discriminating experiments** — pressure step; pressure reversal; spent-puck rebrew;
  spatial/depth-resolved end state; predicted direction/hysteresis per surviving
  mechanism (build on `PROTOCOL_kappa_t_discrimination.md` + the pressure-step spec).
- **Discussion** — what one trace supports / cannot identify; why perturbation beats
  another fit; campaign limits; implications for porous-media inference.

## Figure set (§3.9)

1. Machine null (dip/recovery) + observed rising-flow case.
2. Null-first temporal ladder (constants / static / Φ(t) / flexible null; residuals;
   scoring window).
3. Cross-pressure held-out assessment (LOPO + per-pressure fingerprints; shared-cal as a
   separate comparator, not conflated).
4. Mechanism-by-perturbation prediction matrix (step / reversal / rebrew / control-mode /
   spatial end state / first-drop) — the falsifiable program.
- **Supplement:** block-length + window sensitivity, parameter provenance, residual ACF,
  alternative time-varying closures, detailed sign tests, optional RSM context.

## Explicitly removed from the main narrow paper (§3.10 — owned elsewhere)

- Schmieder RSM / grind-response audit → **Paper 3**.
- Broad evidence matrix over unrelated observables → **Paper 3**.
- N-tube floor test / concentration trajectories → **Paper 4** (future).
- Fine-grind anomaly as a central narrative → **Paper 4**.
- Software-function references, internal review IDs, open task ledgers → out.

## Publication threshold (§3.11)

Credible **applied process-modeling / systems-identification** paper now, if claims stay
conditional. A stronger **fluid-physics** submission needs one of: (1) a controlled
pressure-step / reversal / rebrew experiment (highest-value upgrade — turns "many
mechanisms compatible" into "an intervention separated them"); (2) a formal
observability/perturbation-design analysis; or (3) a physical lateral model with
stability/balance/convergence evidence. For conference use: temporal story without the
RSM lead and without any channeling-instability claim.

## Source material in the current repo (reuse, don't re-derive)

`harness.result2_residual_diagnostics` (ladder + residual/window/block-length),
`cross_pressure_discrimination` + `lopo_waszkiewicz_pressure`, the swelling sign panel
(current Fig 3d), `models/foster2025`, `PROTOCOL_kappa_t_discrimination.md`, and the
pressure-step/flow-reversal protocol spec.
