# RP-D-LC-001 — deterministic 3D lateral-coupling virtual fixture

```
CROSS_MODEL_NUMERICAL_VERIFICATION
DETERMINISTIC_SYNTHETIC_GEOMETRY
NOT_EXPERIMENTAL_VALIDATION
NOT_REAL_PUCK_INFERENCE
NOT_A_REGISTRY_STATUS_PROMOTION
NOT_A_PUBLICATION_RESULT_YET
```

**Not an Insight Foundry screen.** No `I-` number, no candidate, no lens, no generator, no scoring;
`docs/insights/ID_REGISTRY.json` is untouched. This is Stage A of the bounded RP-D activation in
`docs/analysis/RP_D_LATERAL_CROSS_MODEL_PROGRAM.md`.

## 1. Why this tranche was selected

`WP6-LC-IDENT` established **structural identifiability**: in the isoresistive-mirror two-path
design the map `(c, Ξ) → (R, s)` is one-to-one, with an exact closed-form inverse verified against
`model1_two_path` to ~1e-11. But that test was entirely *internal to the two-node network* — the
inverse was checked against the same algebra that produced its inputs.

That leaves one sharp, cheap, decisive question:

> **Is Ξ a coarse-grained physical quantity, or only a parameter of the two-node network?**

`brewer2026.lb_reference` — a D3Q19 TRT Stokes kernel that knows nothing about nodes, contrasts or
Ξ — can generate ground truth independently. If the boundary inverse recovers an independently
field-derived effective Ξ from that solver's fixture, Ξ has survived a test it could have failed.
If it does not, that is a bounded negative result about the reduction, obtained **before** an
apparatus is built.

This is the *virtual* rehearsal of the physical fixture specified in
`docs/insights/screens/WP6-LC-IDENT/DECISIVE_EXPERIMENT.md`. It cannot substitute for that
experiment and does not close the card's box 5.

## 2. What is in this bundle

| file | what it is |
|---|---|
| `PROTOCOL.md` | the frozen protocol, with pre-execution amendments and post-execution errata |
| `VIRTUAL_FIXTURE_SPEC.md` | the deterministic geometry, its exact symmetries and the aperture family |
| `BOUNDARY_TOPOLOGY_ADJUDICATION.md` | why Route A is admissible, and what it does not dispose of |
| `APERTURE_FREEZE.md` | step 2 of the blinded design — the frozen aperture subset and the rule |
| `result.json` | the machine-readable record: every arm, control, clause and hash |
| `summary.csv` | one row per case |
| `decision.md` | question, truth, result, strongest alternative explanation, disposition |
| `figures/primary.png` | four panels; **not** registered in the publication viz registry |
| `runs/run_record.json` | the compact scalar record the whole bundle regenerates from |

## 3. Exact commands

Heavy execution (NOT CI — hours of CPU; `RUNDIR` is a gitignored scratch directory):

```
python -m puckworks.validation.slow.rp_d_lc_001 --backend reference --mode arm_a   --jobs 6 --output RUNDIR
python -m puckworks.validation.slow.rp_d_lc_001 --backend reference --mode coupons --jobs 6 --output RUNDIR
python -m puckworks.validation.slow.rp_d_lc_001 --mode freeze  --output RUNDIR      # writes APERTURE_FREEZE.md
#   -> review and COMMIT the freeze before the next line
python -m puckworks.validation.slow.rp_d_lc_001 --backend reference --mode primary --jobs 6 --output RUNDIR
python -m puckworks.validation.slow.rp_d_lc_001 --mode assemble --output RUNDIR
```

CI-safe regeneration and checks (seconds):

```
python -m puckworks.analysis.rp_d_lc_virtual_fixture --write
python -m puckworks.analysis.rp_d_lc_virtual_fixture --verify
python -m pytest tests/test_rp_d_lc_virtual_fixture.py -q
```

`--jobs N` runs independent LB cases in separate processes. Every case is deterministic with no
shared state and no RNG and `_pmap` preserves order, so the record is identical to a serial run.

**Expected compute location:** local CPU or Colab. Never normal CI (CLAUDE.md rule 3). The full
sweep is hours of D3Q19 TRT on `float64`; the committed record is compact scalars only, and the
driver refuses to serialise a field array.

## 4. Compact result

**`INVALID_EXECUTION`** — `evidence_use: DIAGNOSTIC_ONLY_INVALID_EXECUTION`,
`cross_model_transfer_adjudicated: false`.

Execution validity failed on three evidence-based controls, `primary_cause` being
`componentwise_creeping_flow_control`: the reduced flux `Q/g` and `Q0/g` drift by 2.4–4.0e-4 across
×0.5/×1/×2 forcing against a frozen 1e-4, so the internal field quantities could not serve as
forcing-independent numerical truth. `ΔP/g` is linear to 2.4e-8 on the same rows, so the drift is
in the flux alone. The frozen **volume-flux uniformity proxy** also fails at S=3 (1.028e-3 vs 1e-3);
actual `mass_conservation` is **NOT_EVALUATED** because `Σρu_x` was never retained (E4b), and
`grid_refinement` is **NOT_EVALUATED** because the two resolutions did not hold dynamic similarity
(`Re(S=3)/Re(S=2) = 3.375`, E5). Clauses 2–7 were computed but never reached, and carry
`adjudicative: false` (E6).

**The cross-model transfer question is therefore UNADJUDICATED, not negative.** Every `Ξ̂`,
`Ξ_field`, contrast, monotonicity and path-swap number in this bundle is diagnostic only and may
not be quoted as recovery, mechanism-only transfer, or a weak quantitative success at any strength.

Two fixture findings came out of it, both from controls doing their job. The identical-path
negative control shows the bridge aperture **widens the axial channel**: with `X = 0` exactly and
zero lateral flux the geometry-aware `(a,b,a,b)` network predicts `R = 1`, `s = ½` at any coupling,
yet the observed residual is `R − 1 = 0.014277334586` — and at the largest aperture the observed `R − 1 = 0.1338` **exceeds
the two-node model's hard ceiling** `c²/(1−c²) = 0.1155`, so no `(c, Ξ)` can reproduce it. What held
up: topology, exact voxel mirror symmetry, connectivity, no periodic bypass, the frozen pressure
definition, τ-independence, convergence, and a perfect path-swap signature on all ten rows.

See `decision.md` for the adjudicated statement and `result.json` for the machine-readable record.

## 5. Limitations

Beyond the claim ceiling in §6, and stated so they are not mistaken for settled:

- **Return-path contamination is bounded, not eliminated.** The deliberately extreme obstruction
  probe moves `R` by ~1 % of the coupling signal. That is an upper bound from an extreme
  perturbation, not a calibration of the nominal fixture, and it is not negligible against a
  factor-of-two criterion. See `PROTOCOL.md` erratum **E1** — the frozen form of that control was
  mis-specified and **failed as written**; both numbers are recorded.
- **The mid "node" is a region, not a point.** `p1`, `p2` are area averages over the aperture
  footprint, so they depend on `kx`. Pressure nonuniformity over every nominal node surface is
  reported as a fraction of the relevant difference rather than hidden inside a mean.
- **Junction and entrance losses sit inside the measured sub-network** by design. Separating them
  is what the coupon-vs-field comparison is for; it is not corrected away.
- **No backend cross-check.** Taichi is not installed in this environment, and the port asserts
  cubic domains and exports `ux` only. Recorded as NOT PERFORMED — never as passed.
- **The two resolutions are not a grid-convergence study.** They ran at identical lattice `g` and
  `nu` with lengths ∝ `S`, so `Re(S=3)/Re(S=2) = (3/2)³ = 3.375` — two different dimensionless
  problems (E5). Their paired rows are retained as `fixed_lattice_forcing_resolution_comparison`,
  a diagnostic; `grid_refinement` is NOT_EVALUATED.
- **Smooth slot segments, not porous media.** Whether the conclusion survives when the axial
  elements are genuine Darcy media is Stage B, and is not answered here.
- **Software reproducibility tolerances are not experimental uncertainties.** Nothing here
  estimates an apparatus precision.

## 6. Claim ceiling

Deterministic synthetic geometry · single-phase steady creeping flow · **cross-model numerical
verification only** · no experimental validation · no real coffee morphology · no real-puck `Ξ` ·
no transverse coffee permeability estimate · no evidence that espresso occupies any `Ξ` regime ·
no apparatus precision established · no evidence-rung or registry-status promotion · no claim of a
validated espresso digital twin · **card box 5 remains OPEN** · **box 6 remains closed on its
existing mathematical result** · **Paper 4 remains unauthorized**.

Always "the effective Ξ of the virtual fixture", never "the Ξ of an espresso puck". A successful
simulation does not close the accessible-experiment box; it reduces risk and sharpens the design of
that future experiment.

## 7. Next-stage entry condition

**Stage B is NOT entered.** Its entry condition was `CROSS_MODEL_RECOVERY` or `MECHANISM_ONLY`;
this tranche returned `INVALID_EXECUTION`, so the condition is unmet and the transfer question is
unadjudicated rather than answered.

The next step is a **separately frozen `RP-D-LC-001b`** — a re-execution of *this* question, not a
new one:

1. **Reduce the forcing.** ×4 is the arithmetic minimum against the 3.96e-4 worst case; ×8–10 gives
   margin. The Re-scaling must be **verified by that protocol's own forcing ladder**, not assumed,
   and must not be used to rescue this execution. Reduced forcing is also the shared remedy for E4.
2. **Redesign the bridge so it is a lateral path only.** The identical-path control shows the
   present aperture adds axial cross-section worth `R − 1 = 0.0143`. Either remove that degree of
   freedom geometrically, or calibrate and subtract it using the identical-path fixture at every
   aperture — predeclared, never fitted after seeing `Ξ̂`.
3. **Keep the design inside the model's reachable set:** require `R − 1 < c²/(1−c²)` with margin at
   every frozen aperture, checked from coupon output before the freeze.

Also measure mass flux `∫ρu·dA` rather than volume flux (E4). Arm J's 24 solves were not run and
remain available for that tranche. Each later stage needs its own human authorization
and its own entry condition; see `docs/analysis/RP_D_LATERAL_CROSS_MODEL_PROGRAM.md`.
