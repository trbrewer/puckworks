# Synthetic verification results

Disposition: **ENGINEERING_CAPABILITY_VERIFIED** for the mandatory small capability tests and the representative fixed-operator synthetic query. All four fixed operators qualify with compatibility ESTABLISHED. Software QA, author review and hosted checks are separate in [handoff](HANDOFF.md). G0 / NO_GOVERNING_PHYSICS_CHANGE / RESEARCH_ONLY; PHYSICAL_VALIDATION=NOT_ESTABLISHED.

The allowances are engineering estimates, not rigorous interval-arithmetic, continuum, statistical-confidence or physical certificates. No empirical predictive advantage or unique-state recovery is established. Earlier empirical two-assay predictors and all MASS-DELIVERY conclusions remain unchanged.

## Frozen synthetic input

Only history A and U from 005 VERIFICATION.md are reused; its SHA-256 is in RESULTS.json. Span [7,17] s, early [7,10), [10,12), finite target [12,17), caffeine/grind 1.7/source geometry. The deterministic generator uses only U, before forward evaluation, with total inventory 1e-4 kg. Construction and actual arrays are retained in `synthetic-inputs-full.json`, indexed by EXTERNAL_EVIDENCE_INDEX.json. It is a test generator, not an inferred starting state.

Early centers: [1.8758437701275475e-05, 1.29670843253215e-05] kg. Frozen bands: [[1.7558437701275476e-05, 1.9958437701275473e-05], [1.17670843253215e-05, 1.41670843253215e-05]] kg. Half-width 1.2000000000000002e-06 kg is exactly the specified synthetic assumption, not assay precision. The successful generating trajectory requested only the early windows and stopped at 12 s before future optimization. Bands are byte-identical across all levels and the correction.

## Fixed-operator intervals

All values below are kg. Epsilon is 1e-9 kg. Complete gaps include outer/inner relaxation, response, optimization, representable reconstruction and forward-replay uncertainty.

| N / h (s) | Unconditioned outer interval | Conditioned outer interval | Minimum gap | Maximum gap |
|---|---|---|---|---|
| N400-h0.02 | [1.205608418667377e-05, 2.708487175825335e-05] | [1.549691344345845e-05, 2.401380869902533e-05] | 1.0982635e-12 | 1.58329199e-12 |
| N400-h0.01 | [1.205609109237974e-05, 2.708486990225619e-05] | [1.549692278313437e-05, 2.401380798217329e-05] | 1.13630963e-12 | 1.64013589e-12 |
| N400-h0.005 | [1.205609280986094e-05, 2.708486944713085e-05] | [1.549692510897596e-05, 2.401380781635792e-05] | 1.21228432e-12 | 1.75363655e-12 |
| N800-h0.02 | [1.205711153912423e-05, 2.709484019193188e-05] | [1.548978762873997e-05, 2.40140165098376e-05] | 1.1692326e-12 | 1.69486879e-12 |

The representative minimum bracket is [1.5496913443458448e-5, 1.5496914541721946e-5]; maximum bracket [2.4013807115733347e-5, 2.4013808699025333e-5]. Its width falls from 1.5028787571579578e-5 to 8.516895255566885e-6 kg: absolute reduction 6.511892316012693e-6 kg, relative reduction 0.43329458780341723. Combined endpoint uncertainty is 2.7723617435223506e-12 kg; the reduction exceeds it. These values characterize this declared synthetic query only.

Conservation-only comparator at every level: [0, 9.067447797340304e-5] kg, from 1.2e-4 minus the two disjoint lower bands (sum 2.9325522026596976e-5). It uses no kinetic response and is a conservative bound, not the tightest joint union construction. Native unconditioned results retain their 005 qualification and witnesses; the N800 unconditioned baseline is explicitly pulled-back arithmetic qualification without separate baseline replay. It cannot certify failed conditioning.

## Compatibility and witnesses

Eight accepted witnesses pass strict original-coordinate cell, phase, total and sufficient observation checks after `FVChemicalState.from_cell_averages`. All eight fresh unchanged forward trajectories batch both early windows and the later target. All 24 prediction/replay intervals pass discrepancy checks; every complete early interval lies inside its supplied band. Parent accuracy remains NOT_ASSESSED. Maximum absolute prediction/replay discrepancy is 9.776166549179448e-20 kg; measured forward allowances range from 4.100992334105112e-14 to 2.2694475427264089e-13 kg.

The bounded box projection changes only 1.017432153440224e-22 to 4.421280374095933e-22 kg in L1 mass. It is accepted only after rechecking ALL original and actual inner constraints. No phase/total rebalancing, band widening, hidden residual tolerance or observation deletion occurs. Raw masses, residuals, projected masses, work, mass changes, final residuals and all LP evidence are retained. A projection violating one observation is rejected by regression test. Outer optimizers remain relaxation optimizers; the separate checked witnesses supply only the attainable sides.

## Discretization sensitivity

| Comparison | Outer lower change | Outer upper change | Outer width change |
|---|---|---|---|
| temporal-.02-.01 | 9.33967592392e-12 | -7.16852040239e-13 | -1.00565279642e-11 |
| temporal-.01-.005 | 2.32584158977e-12 | -1.65815376431e-13 | -2.4916569662e-12 |
| mesh-N400-N800 | -7.12581471847e-09 | 2.0781081227e-10 | 7.33362553074e-09 |

The complete maximum-change brackets for both temporal refinements include zero; their signs remain unresolved at the declared numerical resolution. Minimum-change brackets are positive. The coarse-to-fine minimum-change bracket is [-7.126912981973455e-9, -7.124645485876563e-9] kg, exceeding epsilon in magnitude. Its maximum-change bracket is [2.0611594348275155e-10, 2.093941042557784e-10] kg. Compatibility remains established at every level.

N800 uses explicit P^T*g and |P|^T*a in the original 1200 coarse mass coordinates; P splits each phase mass equally into two children. Each replay uses P*m with the fine plan. No independent fine-cell freedom, recentered observations or changed physical history. These are sensitivity findings only: no continuum bound, resolved discretization tolerance or monotone-convergence claim. Historical 004 remains IMPLEMENTED_QUALIFICATION_INCOMPLETE and resolved_temporal_decrease=FAIL.

## Failures, corrections and resources

One initial generating trajectory correctly returned PLANNED_STOP; an overly narrow harness status test rejected it before bands or future queries existed. Its replacement is charged, and GENERATION_STATUS_FAILURE.json / GENERATOR_CORRECTION.json preserve that failure. The first four queries produced checked outer endpoints but unresolved witnesses and infeasible bounded repair LPs. INITIAL_RESULTS.json is retained unchanged. The named correction separates actual inner constraints from the stricter witness-search reserve and tests a bounded box projection against ALL constraints. Small tests passed before the correction campaign. All original native responses and bands were reused; the runner asserts that every corrected outer endpoint equals its original endpoint exactly. No response or generator was rerun for this correction.

Total charged propagations: 34/64 = 24 backward passes + two early generating trajectories + eight witness trajectories. LP invocations: 64/160, including eight unsuccessful initial repair LPs. Exponential actions: 144,860, including split/check/window actions and the discarded generator. Aggregate campaign wall: 170.267721461/1800 s; summed child numerical wall: 151.674363460 s. Maximum observed child peak RSS: 355,324 KiB (aggregate simultaneous parent/child memory was not measured). Every call stayed inside its external 120 s propagation / 30 s LP deadline; no native timeout occurred.

Python 3.12.3, NumPy 2.5.3, SciPy 1.18.1; OPENBLAS_NUM_THREADS=OMP_NUM_THREADS=MKL_NUM_THREADS=1. Per-call timing, peak RSS, termination, counts and named corrections are in RESOURCES.json. Normal N<=12 tests/CI are separate. The persistent common-Git-directory receipt is not reset. No unused allowance authorizes more exploration.

Strict compact JSON retains identities and array hashes; optional full arrays and all original optimizer vectors are retained outside Git and indexed. Reproduction commands and public API are in README.md. Full-mesh reruns require respecting the existing consumed receipt, not changing directories. Evidence is reused by unchanged producer/forward/plan/band hashes after documentation edits. No original-observation access, EWP execution, source acquisition, laboratory action, release or successor occurred.
