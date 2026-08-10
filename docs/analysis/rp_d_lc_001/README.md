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
- **Two resolutions only** (`S = 2, 3`, a 1.5× refinement). Enough to expose voxelisation
  sensitivity, not enough for a Richardson extrapolation.
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

**Stage B (`RP-D-LC-002`, deterministic porous-segment fixtures) may be proposed only if** this
tranche returned `CROSS_MODEL_RECOVERY` or `MECHANISM_ONLY` **and** the pressure-nonuniformity
diagnostics show a two-node coarse-graining is defensible. Deterministic morphology only — no
seeded ensembles, which are Stage C.

Stage B is **not** authorized by this bundle. Each later stage needs its own human authorization
and its own entry condition; see `docs/analysis/RP_D_LATERAL_CROSS_MODEL_PROGRAM.md`.
