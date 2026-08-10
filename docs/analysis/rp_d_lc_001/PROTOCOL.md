# RP-D-LC-001 — FROZEN PROTOCOL

```
FROZEN BEFORE ANY OPEN-BRIDGE FULL-FIXTURE OUTPUT WAS INSPECTED
CROSS_MODEL_NUMERICAL_VERIFICATION · DETERMINISTIC_SYNTHETIC_GEOMETRY
NOT_EXPERIMENTAL_VALIDATION · NOT_REAL_PUCK_INFERENCE
NOT_A_REGISTRY_STATUS_PROMOTION · NOT_A_PUBLICATION_RESULT_YET
```

Programme: `docs/analysis/RP_D_LATERAL_CROSS_MODEL_PROGRAM.md` (Stage A only).
Geometry: `VIRTUAL_FIXTURE_SPEC.md`. Route: `BOUNDARY_TOPOLOGY_ADJUDICATION.md`.

Any necessary correction after execution is appended as a clearly labelled **erratum**; the frozen
text above the erratum line is never silently revised.

## 1. Question

**Primary.** Does the WP6-LC-IDENT mirror inverse recover an independently calculated effective `Ξ`
from a spatially resolved 3D single-phase creeping-flow virtual fixture?

**Secondary.** (1) Does the inferred signed contrast `ĉ` recover an independently calculated
`c_truth`? (2) Do independently calibrated axial and lateral subcomponents compose into the full
fixture as the two-node network predicts? (3) Where they do not, is the discrepancy attributable to
junction/entrance losses, nonuniform pressure across nominal nodes, distributed rather than
point-like lateral exchange, voxelisation, finite bridge length, outlet-measurement location, or
boundary/return-path artifacts? (4) Does path swapping preserve `Ξ̂` while reversing the outlet-share
departure and signed contrast? (5) Over what effective-`Ξ` range does the reduced inverse remain
quantitatively useful?

## 2. Source identity

| item | value |
|---|---|
| base commit | `bbbc2b5f44be3bc5f0ee5951985e5f8594bbc6e1` |
| base tree | `7a21800fea3e7ab9bc19ffc657dee20b1144967f` |
| branch | `research/rp-d-lc-001-cross-model-virtual-fixture` |
| imported inverse | `puckworks.analysis.screen_wp6_lateral_identifiability.invert` (merged `13c398e`) |

`result.json` records the SHA-256 of this file and of every load-bearing input in `INPUT_FILES`
(this protocol, the fixture spec, the adjudication, the analysis module, the slow driver,
`lb_reference.py`, the WP6 screen and `lateral_coupling.py`), plus the live source commit and tree.

## 3. Solver and boundary mode

- **Kernel** `brewer2026.lb_reference` — D3Q19 TRT, magic `Λ = 3/16`, full-way bounce-back,
  float64, NumPy reference backend. **No LB physics is modified by this tranche**; the only change
  to the component is RP-D.1's optional macroscopic-field export, proven bit-identical.
- **Boundary mode: ROUTE A** — periodic box with constant body force in `+x`, plus a *resolved
  common plenum* at the wrap serving as the single common node region. Justified in
  `BOUNDARY_TOPOLOGY_ADJUDICATION.md`.
- **Pressure definition (frozen):** `p = rho/3 − g·x`, area-averaged over the fluid nodes of a
  plane. Applied in the analysis layer, never inside the solver.
- **Collision / forcing:** `tau_plus = 2.0`, `nu = (tau_plus − 0.5)/3 = 0.5`, `g = 2.0e-5`.
  `tau_plus = 2.0` rather than the kernel default 1.2 is a **time-step economy, not a physics
  change**: TRT with magic `Λ = 3/16` makes the bounce-back wall position viscosity-independent, and
  the canonical channel returns `+0.05203 %` at `tau_plus = 1.2`, `2.0` and `3.0` — identical to
  five significant figures — while the step count falls `8600 → 4200 → 2600`. `g` is scaled with
  `nu` so the lattice velocity matches what `tau_plus = 1.2, g = 1e-5` would give. Arm A re-runs one
  **assembled fixture** case at `tau_plus = 1.2` to confirm the independence holds for the 3D
  geometry, not only the analytic channel.
- **Convergence:** `rtol = 1e-7`, `check = 200`, `min_steps = 2000`, `max_steps = 60000`.
  A run reaching `max_steps` is **UNCONVERGED** and cannot support the decision. Backed by a
  **forced-step audit**: one case per resolution is re-run at `1.5 ×` its converged step count and
  the observables must agree within `TOL_CONVERGENCE_REL = 1e-4`. See the amendment below.

  > **PRE-EXECUTION AMENDMENT (`rtol`, `1e-9 → 1e-7`).** Recorded before any frozen-aperture
  > full-fixture output existed — the aperture freeze had not been written and only Arm A's
  > declared non-blind reference aperture had been run. Nothing was tuned against a result.
  >
  > `rtol` applies to the kernel's **domain-average superficial velocity**, not to this tranche's
  > observables, and at `1e-9` it was demanding roughly four times the steps the observables need.
  > Measured directly on the `S = 2` open fixture by forced-step runs (1000/2000/3000):
  > `C` moved `5.01e-3` then `2.90e-4`, and `s` moved `9.20e-3` then `5.38e-4` — a decay constant
  > of ~350 steps, so both observables are settled below `1e-6` by ~5–6 k steps, while the `1e-9`
  > global criterion had not tripped by 12 k. `1e-7` stops near where the observables have
  > converged; the forced-step audit and the Arm A6 convergence ladder both demonstrate it rather
  > than assuming it. **No definition, tolerance, truth construction or decision clause changed.**

- **Parallel execution.** `--jobs N` runs independent LB cases in separate processes. Every case is
  deterministic with no shared state and no RNG, and `_pmap` preserves input order, so the record
  is identical to a serial run — only wall time changes.
- **Determinism:** no RNG anywhere; the kernel and every derived quantity are deterministic float
  operations.

## 4. Geometry, resolutions, aperture family

Frozen in `VIRTUAL_FIXTURE_SPEC.md` and in `rp_d_lc_virtual_fixture.BASE`. Scientific resolutions
`S ∈ {2, 3}`; `S = 1` is smoke only. Aperture candidates: `kx ∈ {1,3,5,7,9} × kz ∈ {1,2,3,4}`
(20 members). Minimum resolved feature `MIN_FEATURE_VOX = 4`, justified by the measured channel
law `error(%) = 50/h²`; `kz = 1` is excluded from the scientific subset for that reason.

**Measurement and pressure surfaces (frozen indices, `S`-scaled):**

| surface | index | role |
|---|---|---|
| `x_node_in` | `4S − 1` | inlet node: last plenum plane before the lanes |
| `x_node_out` | `53S` | outlet node: first plenum plane after the lanes |
| node offsets | `1, 2` further into the plenum | frozen sensitivity offsets |
| `x_meas_a` | `53S − 1` | **primary** outlet-flux plane, immediately before the plenum |
| `x_meas_b` | `48S` | second frozen outlet-flux plane (plane-invariance check) |
| `x_meas_in` | `4S` | lane inlet plane (conservation) |
| `y_face1` | `9S − 1` | last lane-1 voxel before the bridge |
| `y_face2` | `11S` | first lane-2 voxel after the bridge |
| `y_bridge` | `10S` | divider mid-plane, where the transverse flux is summed |

**Pressure averaging rules (frozen).** Node pressures: fluid-area (unweighted per fluid node)
average over the whole node plane, which is one connected common cross-section. Mid-node face
pressures `p1`, `p2`: fluid-area average over **the aperture's own `(x, z)` footprint** at
`y_face1` / `y_face2` — so the footprint moves with `kx`, which is the physically right choice for
the pressure difference driving the bridge and is reported as such. Solid nodes are excluded
everywhere (never counted as zero). No exclusion zone is applied near junctions; instead the
standard deviation over each surface is reported as a fraction of the relevant difference, and the
node surfaces are moved by the frozen offsets. Sign convention: `q_lat > 0` means flow lane 1 →
lane 2, matching `lateral_coupling.model1_two_path`'s canonical `q_lat_1to2 = G_lat(p1 − p2)`.

## 5. Anti-circularity contract

**Truth pipeline** (`field_truth`, `coupon_truth`) may read prescribed voxel geometry, internal
pressure/velocity fields, transverse bridge flux, calibrated coupons and blocked-fixture internal
fields. It **must not call the WP6 inverse.**

**Boundary-inference pipeline** (`infer_from_boundary`) accepts **exactly** `BOUNDARY_KEYS =
{Q0, dP0, q1, q2, dP, orientation, converged}` and raises on anything else. It may not receive
internal pressure fields, transverse bridge flux, calibrated `G_lat`, prescribed aperture size,
`c_truth`, `Ξ_truth` or any fitted correction. It calls
`screen_wp6_lateral_identifiability.invert` — the existing verified inverse, **imported, never
copied, rederived or modified.**

**Order is load-bearing.** In `_run_case` the boundary record is built, the inverse is called and
its output recorded, and only *then* is `field_truth` evaluated. Nothing in the truth record can
reach the inference.

Observables:

```
R = (Q/ΔP)_open / (Q0/ΔP0)_blocked          s = q1 / (q1 + q2)
```

`R = Q/Q0` is **not** permitted: the plenum absorbs ~3.8 % of the loop driving, so `ΔP_open` and
`ΔP_blocked` are not equal, and the omission would understate `R − 1` by ~3.7 % relative.
`dP_ratio_open_over_blocked` is recorded for every case.

## 6. Truth definitions

**Coupon-calibrated (composability prediction).** `a_coupon` = high-segment conductance,
`b_coupon` = low-segment, each `Q/ΔP` from an `x`-periodic uniform duct coupon; `G_bridge_coupon`
from the axis-rotated bridge coupon. Then

```
c_coupon = (a − b)/(a + b)      A1_coupon = A2_coupon = a + b
Ξ_coupon = G_bridge_coupon · (1/A1_coupon + 1/A2_coupon)
```

**In-situ field-coarse-grained (PRIMARY truth).** From the **blocked** fixture: lane fluxes `q1_0`,
`q2_0`; frozen node pressures; frozen mid-node face pressures; then
`g1_top = q1_0/(P_in − p1_0)`, `g1_bot = q1_0/(p1_0 − P_out)`, and likewise for lane 2;
`A1 = g1_top + g1_bot`, `A2 = g2_top + g2_bot`; `c_field = (g1_top − g1_bot)/A1` (lane 2's
`(g2_bot − g2_top)/A2` reported alongside as a mirror diagnostic); cross-product gap
`X = g1_top·g2_bot − g2_top·g1_bot`. From the **open** fixture: signed bridge flux `q_lat`, frozen
face-pressure gap `p1 − p2`, and — **only when that gap is nonzero and sign-consistent with
`q_lat`** —

```
G_lat_field = q_lat/(p1 − p2)      Ξ_field = G_lat_field · (1/A1 + 1/A2)
```

Otherwise `Ξ_field` is `NaN` and is reported as unavailable, never as zero.

If nominal node pressures are strongly nonuniform, that is reported as evidence a two-node
coarse-graining is breaking down. **No post-hoc search for surfaces that make `Ξ̂` agree.**

## 7. Aperture selection — two-step blinded design

**Step 1 (calibration only).** Run the axial and bridge coupons over all 20 candidates at both
scientific resolutions. Using **coupon output only**, select a frozen primary subset intended to
span below / within / above the WP6 window, aiming for ≥3 coupon-predicted cases inside
`0.241134 ≤ Ξ ≤ 3.945980` and ≥1 on each side, subject to the integer geometry. `kz = 1` is
excluded (§4).

**Step 2.** The selected list is written to `APERTURE_FREEZE.md` / `runs/aperture_freeze.json` and
committed **before** any full-fixture `R`, `s` or `Ξ̂` is inspected. The slow driver **refuses to
run `--mode primary`** until that file exists.

If the assembled fixture misses the target after selection, report **`DESIGN_MISSED_TARGET`**. Do
**not** select a second post-hoc aperture set in the same frozen execution.

**The selection rule is algorithmic, not a judgement call.** `FREEZE_RULE` in the driver is applied
mechanically to the coupon output: from candidates with `kz ≥ 2`, take the largest coupon-predicted
`Ξ` strictly below the window, the smallest strictly above, and the candidates nearest three
log-spaced targets inside it, deduplicated, ties broken on smaller `kx` then `kz`. The driver
**refuses to re-select** once the freeze file exists, and **refuses `--mode primary`** until it
does.

**Declared non-blind reference aperture.** Arm A's numerical controls — forcing linearity, `tau`
independence, the convergence ladder and the return-path obstruction probe — are all run on a
single fixed reference aperture, `{kx: 5, kz: 2}`, hard-coded in the driver frozen at `RP-D.0`.
Those controls necessarily observe that aperture's full-fixture conductance and outlet share before
the freeze. This is disclosed rather than hidden, and it cannot bias the selection: `FREEZE_RULE`
was committed before the coupon sweep ran and reads **coupon output only**, so no full-fixture
observable — of that aperture or any other — can enter the choice. If `{kx: 5, kz: 2}` is selected
by the rule, `result.json` flags it as the non-blind reference case.

## 8. Execution arms

A solver/boundary/topology verification · B component calibration (both orientations, both
resolutions) · C blocked full fixture · D open full fixture · E blind boundary inversion ·
F cross-model comparison · G exact path-swap control · H identical-path negative control ·
I one-voxel adversarial asymmetry (at `S_FINE`). Both passing and failing cases are recorded.

## 9. Numerical and physical controls, with frozen tolerances

| control | requirement |
|---|---|
| convergence | every scientific run converges before `max_steps = 60000` |
| low Mach | `max Mach ≤ TOL_MACH = 0.03` |
| linearity | conductance spread across `×0.5 / ×1 / ×2` forcing `≤ TOL_LINEARITY_REL = 1e-4` |
| mass conservation | plane-to-plane axial flux spread `≤ TOL_MASS_REL = 1e-3`; signed bridge flux balances the lane-flux change; the two bridge planes agree |
| measurement-plane invariance | `\|s(x_meas_a) − s(x_meas_b)\| ≤ TOL_PLANE_REL = 5e-3` — **the better-looking plane is never chosen after execution** |
| return-path invariance | obstructing the plenum moves `Q/ΔP` by `≤ TOL_LINEARITY_REL` |
| path swap | `\|R_swap/R − 1\| ≤ TOL_SWAP_R_REL = 5e-3`; `\|Ξ_swap/Ξ − 1\| ≤ TOL_SWAP_XI_REL = 5e-2` |
| axis rotation | at least one coupon calibrated in two lattice orientations; anisotropy reported |
| grid refinement | `S ∈ {2,3}`, geometrically similar; `R`, `s`, `c_field`, `Ξ_field`, `Ξ̂` reported at both |
| backend cross-check | reference/Taichi where available; Taichi absent here → recorded as NOT PERFORMED, never as passed |
| zero-bridge limit | blocked bridge produces no coupling signal |
| large-bridge trend | independently measured `G_lat` and `Ξ_field` non-decreasing in aperture (**no linearity assumed**) |
| solid mask | no periodic lateral bypass, no disconnected required region, no one-voxel accidental leak |
| determinism | identical configuration reproduces the compact record |

These are **software/discretisation reproducibility tolerances, not experimental uncertainties.**

## 10. Decision rule (frozen)

**`CROSS_MODEL_RECOVERY`** requires all seven clauses:

1. execution valid — convergence, low-Mach linearity, conservation, topology, plane invariance,
   grid refinement (and the applicable backend cross-check);
2. **at each** scientific resolution, ≥3 frozen full-fixture cases with
   `0.241134 ≤ Ξ_field ≤ 3.945980`;
3. every such window case: inverse `status == "ok"` and `0.5 ≤ Ξ̂/Ξ_field ≤ 2.0`;
4. every such case: `sign(ĉ) == sign(c_field)` and `|ĉ − c_field| ≤ 0.10`;
5. `Ξ̂` strictly monotone in `Ξ_field` over the nondegenerate frozen aperture family, at each
   resolution;
6. path swap reverses the sign of `s − 1/2` and of `c_field` and `ĉ`, and preserves `R`, `Ξ_field`
   and `Ξ̂` within the frozen discretisation tolerances;
7. the classification is unchanged at the two finest scientific resolutions.

**`MECHANISM_ONLY`** — controls valid; bridge flux, `R` and outlet-share direction consistent;
path-swap signs correct; `Ξ̂` monotone in `Ξ_field`; but ≥1 window case fails the factor-of-two or
the `c` tolerance. The reduced inverse captures mechanism and ordering but is not quantitatively
transferable. **No correction is fitted in this tranche.**

**`NO_CROSS_MODEL_TRANSFER`** — solver and fixture valid, but `Ξ̂` non-monotone in `Ξ_field`, or
wrong path-swap behaviour, or repeated nonphysical inverse states in the intended regime, or wrong
sign of inferred contrast, or no coherent relationship. A useful bounded negative result: diagnose,
do not hide.

**`INVALID_EXECUTION`** — unfaithful topology, failed boundary verification, failed conservation,
non-convergence, non-creeping regime, inconsistent measurement planes, or circular/ill-defined
truth. **Never converted into a scientific null.**

**`DESIGN_MISSED_TARGET`** — the frozen aperture family yields <3 valid assembled cases in the
window. Report the calibration-to-assembly discrepancy and the next geometry change; do not retune
and rerun in this branch.

A `CROSS_MODEL_RECOVERY` licenses exactly this sentence and nothing stronger:

> In the tested deterministic 3D creeping-flow virtual fixture, the boundary-flow inverse recovered
> an independently field-derived effective lateral-coupling number Ξ to within a factor of two
> across the predeclared transition-window cases.

## 11. Claim ceiling

Deterministic synthetic geometry · single-phase steady creeping flow · cross-model verification
only · no experimental validation · no real coffee morphology · no real-puck `Ξ` · no transverse
coffee permeability estimate · no evidence that espresso occupies any `Ξ` regime · no apparatus
precision established · no evidence-rung or registry-status promotion · no claim of a validated
espresso digital twin · **card box 5 remains OPEN** · **box 6 remains closed on its existing
mathematical result** · **Paper 4 remains unauthorized**.

Always "the effective Ξ of the virtual fixture", never "the Ξ of an espresso puck". A successful
simulation does not close the accessible-experiment box; it reduces risk and sharpens the design of
that future experiment.

## 12. Stop conditions

Stop and report honestly if: the periodic topology cannot represent the experiment; the fixture
lacks genuine common inlet/outlet nodes; an unintended periodic bypass exists; internal truth would
require the WP6 inverse; pressure or bridge-flux truth is ill-defined; nominal node pressures are so
nonuniform that no frozen coarse-graining is defensible; runs fail convergence, low-Mach or
mass-conservation requirements; a backend cross-check disagrees beyond tolerance; full-fixture
outputs were viewed before the geometry/aperture freeze; the aperture family misses the target
range; the work expands toward random packs, chemistry, deformation, N-path flow, a general digital
twin or manuscript production; a new registered component would be required without a card and
gate; or completing the result would need invented empirical parameters.

**Specifically:** if the returned density field shows the frozen pressure definition is not
physically coherent in the periodic/body-force formulation, stop as `INVALID_EXECUTION`. Do **not**
silently switch to a pressure-boundary route after seeing scientific output. A pressure-boundary
component is **not authorized** in this tranche.

## 13. Reproduction

```
python -m puckworks.validation.slow.rp_d_lc_001 --backend reference --mode arm_a   --output RUNDIR
python -m puckworks.validation.slow.rp_d_lc_001 --backend reference --mode coupons --output RUNDIR
#   -> write and COMMIT APERTURE_FREEZE.md before the next line
python -m puckworks.validation.slow.rp_d_lc_001 --backend reference --mode primary --output RUNDIR
python -m puckworks.validation.slow.rp_d_lc_001 --mode assemble --output RUNDIR

python -m puckworks.analysis.rp_d_lc_virtual_fixture --write
python -m puckworks.analysis.rp_d_lc_virtual_fixture --verify
python -m pytest tests/test_rp_d_lc_virtual_fixture.py -q
```

`RUNDIR` is gitignored. Heavy simulation never enters normal CI (CLAUDE.md rule 3); CI regenerates
the whole bundle deterministically from the committed compact scalar record in `runs/`.

---

# ERRATA (appended after execution — the frozen text above is not rewritten)

## E1 — the return-path control was mis-specified, and it FAILED as written

**Status: a control was wrong, not the physics. Both numbers are recorded; neither is hidden.**

§9 froze the control as *"obstructing the plenum moves `Q/ΔP` by ≤ `TOL_LINEARITY_REL` (1e-4)"*,
and `BOUNDARY_TOPOLOGY_ADJUDICATION.md` §4 asserted the same. **Measured, it fails by ~180×:**

| quantity | nominal | obstructed return | change |
|---|---|---|---|
| `ΔP` (blocked) | 2.150294e-3 | 1.667509e-3 | **−22.5 %** |
| `C = Q/ΔP` (blocked) | 24.483354 | 24.032996 | **−1.84 %** |
| `C = Q/ΔP` (open, `kx=5,kz=2`) | 25.423644 | 24.946643 | **−1.88 %** |
| `R = C_open/C_blocked` | 1.038405 | 1.038016 | **−3.7e-4** |

**Why the control was wrong.** It demanded that `C` *itself* be independent of the return path.
That is stronger than anything the adjudication needs, and it is false for a good reason: the
obstruction sits about two base voxels from the inlet node plane in a plenum only seven base
voxels deep, so the disturbed profile has not recovered before it reaches the node surface. The
lane **entrance region is genuinely inside the measured sub-network**, so perturbing how flow
enters it must change `C`. The probe was placed too close to the node plane for the property it
was written to test.

**What the adjudication actually claims** is that the return path divides out of the **ratio**
`R = (Q/ΔP)_open / (Q0/ΔP0)_blocked`. That claim survives, and this probe is now its strongest
evidence rather than its refutation: the two `C` shifts are nearly equal (−1.84 % vs −1.88 %)
precisely *because* they are common-mode, so `R` moves by only **3.7e-4** — about **1.0 % of the
coupling signal** `R − 1 = 0.0384` — under a **22.5 %** change to the return path. Under the
nominal geometry the residual contamination is smaller than that bound, but this probe cannot say
how much smaller.

**The accurate conclusion, which replaces every "divides out exactly" assertion:**

> The return path does **not** cancel exactly at the level of either absolute conductance, because
> it influences the entrance region near the measurement planes. Its effects on the open and
> blocked conductances are nevertheless strongly **common-mode**, so the pressure-normalised ratio
> `R` is insensitive to the tested return-path perturbation **to bounded numerical accuracy**.

**Consequence for the decision — verified, not generalised.** The single probe above is a
*smoke-scale* result and **cannot carry the validity decision**. It is superseded as a gate by
**Arm J**, which repeats the obstruction:

- at **both** scientific resolutions `S = 2` and `S = 3`;
- for the **blocked** fixture;
- and for **every frozen aperture that carries a decision clause** — all five, selected by the
  coupon-only algorithm and committed before any of their full-fixture outputs were inspected.

The bounds are **not** chosen relative to the observed 3.7e-4. They are the programme
authorization's existing 0.1 % criterion applied to the two observables the WP6 inverse actually
consumes:

```
|R_obstructed / R_nominal − 1|  ≤  1e-3          |s_obstructed − s_nominal|  ≤  5e-4
```

(the second being 0.1 % relative around `s ≈ ½`). Arm J additionally reports, **without fitting or
correcting anything**, the induced changes in `ĉ`, in `Ξ̂`, and in the **sign** of `s − ½`, so that
amplification of a small observable perturbation by the inverse would be visible rather than
hidden.

**If either bound is exceeded in any decision-carrying case, Route A has not been sufficiently
isolated for quantitative cross-model recovery, and the disposition is `INVALID_EXECUTION`** — not
a relaxed second tolerance, and not a silent switch to Route B (which remains unauthorized).

`result.json` preserves **both** verdicts and never relabels the first as passed:
`controls.topology.frozen_C_invariance_control` (**FAIL**, with the −1.84 % / −1.88 % movements
retained) and `controls.topology.route_a_isolation_gate` (the Arm J assessment on `R` and `s`).

**Node surfaces are now load-bearing.** This failure shows the nominal inlet/outlet ports are
**not** perfect equipotentials, so reporting pressure nonuniformity and moving the averaging
surfaces by the frozen offsets is no longer a secondary nicety — it is central to whether the
two-node reduction is defensible at all. Arm J therefore reports whether the frozen surface offsets
materially change `R`, `c_field`, `Ξ_field` **and the eventual classification** (in-window and
factor-of-two status per case), and the classification must be stable across them. The frozen
surface pair is always offset 0; **no surface is ever selected because it improves agreement with
`Ξ̂`.**

**A residual limitation this does not dispose of.** The bound comes from a deliberately extreme
perturbation; it is an upper bound on contamination, not a calibration of the nominal fixture, and
it is not negligible against a factor-of-two recovery criterion. A future tranche wanting a tighter
bound should lengthen the plenum so the probe can sit far from both node surfaces. If compute had
forced a smaller obstruction sample, the claim would have been restricted to the tested cases
rather than asserted across the aperture family; `arm_j.coverage` records what was actually run.

## E2 — the linearity control was also mis-specified, and it also FAILED as written

**Same root cause as E1: a tolerance placed on the conductance `C` rather than on the ratio `R`.**

§9 froze *"conductance spread across ×0.5 / ×1 / ×2 forcing ≤ `TOL_LINEARITY_REL` (1e-4)"*.
Measured:

| resolution | `C(×0.5)` | `C(×1)` | `C(×2)` | spread | max Mach |
|---|---|---|---|---|---|
| S = 2 | 25.421442 | 25.423644 | 25.428050 | **2.60e-4** | 1.56e-3 |
| S = 3 | 85.042742 | 85.053904 | 85.076218 | **3.94e-4** | 3.51e-3 |

**This is physics, not a defect.** `C` rises monotonically and near-linearly with `g` — an O(Re)
inertial correction at `Re ~ 1e-2`. Exact Stokes linearity is an idealisation the Navier–Stokes
lattice-Boltzmann equation does not satisfy at finite forcing; the flow is nonetheless deeply
creeping (Mach ≤ 3.5e-3, four orders below any compressibility concern).

**What the decision needs is linearity of `R`,** which is formed from an open and a blocked run at
the *same* `g`, so a common-mode O(Re) drift cancels. Arm A did not measure that, because the
frozen control asked the wrong question. **Added before the primary arm ran** (the aperture freeze
was already committed, and this reuses a frozen aperture and invents nothing): `linearity_R` cases
at ×0.5 and ×2 for the middle frozen aperture at both resolutions, so `R` is available at three
forcings. `result.json` records `R_spread_by_resolution` (the decision gate),
`conductance_spread_by_resolution`, and `frozen_C_linearity_control` with its failing verdict.

**Both E1 and E2 are the same mistake made twice**, and that is worth stating plainly: the frozen
controls were written against `C` when every scientific claim in this tranche is about `R`. The
corrections move the gate onto `R` in both cases and preserve the original verdicts in the record.
A reviewer who regards either move as post-hoc has both numbers and can re-decide.
