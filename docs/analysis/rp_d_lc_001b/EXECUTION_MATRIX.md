# RP-D-LC-001b — planned execution matrix

```
NO ROW IN THIS DOCUMENT HAS BEEN EXECUTED
solves_executed: 0     lb_solver_invoked: false
```

Machine-readable and authoritative: `generated/execution_matrix.json`, produced by
`rp_d_lc_001b_virtual_fixture.execution_matrix()`. This document is its human-readable face; where
they could disagree, the generated file wins and the tests bind the two.

## 1. Ordering and early stops

Phases run **strictly in order**; within a phase, rows run in the order the generator emits them.

```
P0  →  P1  →  P2 (freeze)  →  P3  →  P4  →  assemble/adjudicate
```

| point | early-stop behaviour |
|---|---|
| **P1** | if **no** candidate meets `ARTIFACT_BUDGET_R_ABS = 1e-3` at **both** resolutions, stop with `DESIGN_BLOCKED_PRE_EXECUTION`. P2, P3 and P4 are not run: **131 solves are refused**, and the tranche reports a design-blocked result rather than authorising primary computation |
| **P2** | if fewer than 3 admitted candidates have coupon-predicted `Ξ` inside the WP6 window, report the calibration-to-assembly gap and stop. **Do not re-select a second post-hoc family in the same frozen execution** |
| **P3** | any run reaching `max_steps` is `UNCONVERGED` and stops the phase. No retry at a looser tolerance |
| **P4** | a breached Route-A isolation bound gives `INVALID_EXECUTION` — never a relaxed second tolerance, never a switch to Route B |
| any | a failed required execution-validity control gives `INVALID_EXECUTION`; clauses 2–7 are not reached |

**Rerun / replicate policy.** No statistical replicates: every case is deterministic, with no RNG
and no shared state. One replicate per phase is run **solely** to demonstrate byte-identical
reproduction of the compact record. Convergence extensions are the forced-step audit rows only.

## 2. Counts

| class | rows | meaning |
|---|---|---|
| **mandatory scheduled** | **62** | P0 (14) + P1 (48) — everything that must run before the next review point |
| conditional on P1 | 24 | P2 bridge coupons; skipped entirely if no candidate clears the artifact budget |
| conditional on the freeze | 86 | all of P3; may run only from an expressly approved frozen head |
| conditional on P3 | 20 | P4 / Arm J |
| diagnostic only | 3 | determinism replicates |
| **maximum possible** | **195** | if every phase proceeds |

| phase | rows |
|---|---|
| P0 | 15 (14 + 1 determinism replicate) |
| P1 | 49 (48 + 1) |
| P2 | 24 |
| P3 | 87 (86 + 1) |
| P4 | 20 |

## 3. The rows

### P0 — common blocked characterisation · 14 solves · MANDATORY

| # | kind | S | forcing | state | variant | bridge | retained record |
|---|---|---|---|---|---|---|---|
| 1–3 | reference-blocked ladder | 2 | `1.0e-6` / `2.0e-6` / `4.0e-6` | `reference_blocked` | mirror | — | all 9 axial planes (volume **and** mass flux), node pressures + `sd`, lane fluxes at both outlet planes |
| 4–6 | reference-blocked ladder | 3 | `2.962962962962963e-7` / `5.925925925925926e-7` / `1.1851851851851852e-6` | `reference_blocked` | mirror | — | as above |
| 7–10 | axial coupon | 2 | central | coupon | high/low × orientation x/y | — | duct conductance `Q/(g L)`, both lattice orientations |
| 11–14 | axial coupon | 3 | central | coupon | high/low × orientation x/y | — | as above |

**Produces:** `c_field`, `A₁`, `A₂` for the reachable-set gate; `a_coupon`, `b_coupon`,
`c_coupon`; the blocked-side componentwise forcing-invariance evidence; the first mass-conservation
measurement in the programme's history.

### P1 — candidate identical-path controls · 48 solves · MANDATORY · DECISION-BEARING

12 scientific candidates × {`blocked`, `open`} × {S = 2, S = 3}, **central forcing**,
`variant = "identical"`.

| candidates | `w ∈ {3,5,7,9} × kz ∈ {2,3,4}` |
|---|---|
| retained record | full axial + transverse plane records; `R_identical`, its mass-flux counterpart, and every artifact form in `artifact_metrics()` |
| gate | `|R_identical − 1| ≤ 1e-3` at **both** resolutions |

**No mirror recovery case is run or inspected in this phase.** The artifact is a geometry property,
so it is measured at central forcing only; the forcing ladder for the frozen candidate arrives in
P3.

### P2 — admissibility and bridge freeze · 24 solves · CONDITIONAL ON P1

12 scientific candidates × {S = 2, S = 3}, bridge coupon, central forcing.

Then, with **no further solving**:

1. reject every candidate failing the P1 artifact budget;
2. apply `reachable_set_admission()` using the **P0 reference-blocked** `c_field` (never a mirror
   output), the candidate's measured artifact bound and the frozen numerical-uncertainty and
   safety-margin terms;
3. apply `FREEZE_RULE` mechanically to the survivors' **coupon-predicted `Ξ`** — largest below the
   window, smallest above, three log-spaced inside, ties on smaller `w` then `kz`;
4. write and hash `runs/bridge_freeze.json`, binding the protocol, fixture-spec and matrix hashes.

**Expected selection size: 5.** The driver refuses `--mode p3` until this file exists and matches.

### P3 — primary mirror / path-swap experiment · 86 solves · CONDITIONAL ON THE FREEZE

| block | rows | detail |
|---|---|---|
| primary mirror | **60** | 5 frozen bridges × {S=2, S=3} × {`×0.5`, `×1`, `×2`} × {blocked, open} |
| path-swap control | **20** | 5 frozen bridges × {S=2, S=3} × {blocked, open}, central forcing, `swapped=True` |
| one-voxel adversarial | **4** | {`one_voxel_plug`, `one_voxel_slab`} × {blocked, open} at `S_FINE`, first frozen bridge |
| forced-step convergence audit | **2** | one case per resolution at `1.5 ×` its converged step count |

Retained per row: the full compact record, the boundary record (six keys, allowlist-validated) and
the field truth — built and recorded **in that order**, so nothing on the truth side can reach the
inference.

### P4 — Arm J return-path nuisance isolation · 20 solves · CONDITIONAL ON P3 · DECISION-BEARING

5 frozen bridges × {blocked, open} × {S = 2, S = 3}, central forcing, plenum obstructed.

Gate: `|R_obstructed/R_nominal − 1| ≤ 1e-3` and `|s_obstructed − s_nominal| ≤ 5e-4`, with the
induced changes in `ĉ`, `Ξ̂` and the sign of `s − ½` reported and never fitted. Arm J is **not**
silently omitted to shrink the matrix: 001 recorded 24 unrun Arm-J solves as available for this
tranche, and 20 of them are scheduled here against the corrected 5-candidate selection.

### Determinism replicates · 3 solves · DIAGNOSTIC ONLY

One case re-run in each of P0, P1 and P3; the compact record must reproduce byte-identically.

## 4. Positive and negative controls, by name

| control | where | what it proves |
|---|---|---|
| uniform-duct coupon (`ΔP = g·L` exactly) | P0 | the frozen pressure definition is coherent in the periodic body-force formulation — an analytic **positive** control |
| identical-path zero-lateral-driver | **P1** | opening the bridge does not widen the axial channel — the **negative** control that 001 failed |
| reference-blocked vs candidate-blocked `c_field` | P0 / P3 | the ports do not move the contrast — reported as a diagnostic, not re-gated |
| path swap | P3 | the signature reverses where it must and is preserved where it must |
| one-voxel adversarial asymmetry | P3 | how much a sub-1 % construction asymmetry can bias `Ξ̂` |
| plenum obstruction (Arm J) | P4 | the return path is isolated to the programme's 0.1 % scale |
| forced-step audit | P3 | the convergence criterion is sufficient for the observables |
| determinism replicate | all | the record is reproducible |

## 5. Compute

**Planning information only — clearly separated from every scientific admission criterion, and not
an assertion.** No wall-time estimate is claimed, because none has been measured for this geometry
and 001's timings were taken at a different forcing, a different divider and a different step count.
What is known: the S=2 domain is 112 × 48 × 16 lattice nodes and the S=3 domain is
168 × 72 × 24, on a float64 NumPy D3Q19 TRT kernel; 001's comparable sweep was recorded as "hours"
of CPU with `--jobs 6`. Heavy execution stays in `puckworks/validation/slow/` or local/Colab runs
and **never** enters normal CI (CLAUDE.md rule 3). `RUNDIR` is gitignored; the committed record is
compact scalars only.

## 6. What is refused right now

Every row above. The driver's solving modes raise `ExecutionNotAuthorised`, and P3/P4 additionally
raise `FreezeMissing` because no freeze artifact exists. Both refusals are asserted by test.
