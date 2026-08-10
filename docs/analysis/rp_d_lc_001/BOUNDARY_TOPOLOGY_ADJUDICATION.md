# RP-D-LC-001 — boundary and topology adjudication

```
READ-ONLY ADJUDICATION — decides the execution route, produces no scientific result
CROSS_MODEL_NUMERICAL_VERIFICATION · DETERMINISTIC_SYNTHETIC_GEOMETRY
NOT_EXPERIMENTAL_VALIDATION · NOT_A_REGISTRY_STATUS_PROMOTION
```

**Verdict: ROUTE A is admissible** — the existing periodic / body-force D3Q19 TRT kernel, with a
resolved common plenum, faithfully represents the two-lane fixture, **provided the observables are
pressure-normalised**. The return path then divides out *exactly*, by construction rather than by
being small. Route B (a new pressure-boundary component) is **not required and is not built**.

The route is recorded as **`ROUTE_A_HISTORICAL_PROVENANCE`**, because reaching it required one
non-physical correction: see §7.

---

## 1. The question

The intended experiment has one common inlet manifold, two distinct lanes, one common outlet
manifold, separately measurable lane flows immediately before the outlet manifold, and a blockable
lateral bridge between the lane mid-regions. The existing kernel offers a **periodic box with a
constant body force in +x**. A periodic box does not automatically represent that topology, and
this document does not assume it does.

## 2. The pressure field exists and is well defined

With a constant body force `g` in `+x` and `rho ≈ 1`, the steady Stokes balance the kernel solves is

```
0 = -c_s^2 grad(rho) + g x_hat + mu lap(u),      c_s^2 = 1/3
```

Define the **physical** pressure

```
p(x,y,z) = rho(x,y,z)/3 - g*x                                     (PRESSURE DEFINITION, FROZEN)
```

Then `grad p = c_s^2 grad(rho) - g x_hat`, so the balance above is exactly `0 = -grad p + mu lap(u)`
— ordinary Stokes flow driven by a pressure gradient. The lattice density therefore carries the
**periodic part** of the pressure and the `-g*x` ramp carries the mean gradient. Both halves are
needed; neither alone is the pressure.

This is a definition, not an approximation, and it is falsifiable: in a *uniform* duct the flow is
fully developed, `mu lap(u) = -g` pointwise, so `grad p = 0` in the periodic part and the density
must be constant. Arm A checks exactly that (the uniform-duct coupons must return `ΔP = g*L` to the
solver's convergence tolerance). If the returned density field had contradicted this, the tranche
would have stopped as `INVALID_EXECUTION` rather than switching route.

`x` is single-valued on the lane traverse (`x_node_in < x_node_out`, no wrap between them), so the
node-to-node drop is unambiguous:

```
ΔP = (rho_bar_A - rho_bar_B)/3 + g*(x_B - x_A)
```

with `rho_bar` the fluid-area average over the node plane.

## 3. Question 1 — can a periodic box carry two genuine common end nodes?

**Yes, and with no additional return duct.** The fixture places a resolved plenum at the wrap:
base stations `{53,54,55,0,1,2,3}` form one connected, full-cross-section fluid body, so the lane
exits at `x = lane_hi` and the lane entrances at `x = lane_lo` are served by **the same** region.
That region *is* the common manifold; the periodic wrap is the manifold's interior, not an extra
element bolted on.

Electrically the fixture is a loop with a distributed EMF: total driving `E = g*N_x` is split
between the lane sub-network (`R_L`) and the plenum (`R_P`), so `ΔP_lanes = E * R_L/(R_L + R_P)`.

## 4. Question 2 — the return path's effect on the measured ratio, and why it cancels

`R_P` is **not** negligible and is not claimed to be. Measured on the probe fixture, the plenum
absorbs about **3.8 %** of the loop driving (`ΔP/(g·L_lane) = 1.0778` where `L_lane = x_B - x_A`,
against `N_x/L_lane = 1.12` if the lanes took all of it).

### It does NOT cancel exactly — it cancels as a common mode, to a measured bound

**This subsection was falsified by its own probe and is superseded by erratum E1 in
`PROTOCOL.md`. The original claim is struck through, not deleted.**

> ~~`Q/ΔP` is a property of the lane sub-network and of nothing else, so the return path is absent
> from `R` **identically**, not to 0.1 %.~~

That is **false**, and the probe designed to demonstrate it disproved it instead. Obstructing the
plenum moves the absolute conductance by **−1.84 %** (blocked) and **−1.88 %** (open) — far outside
the `1e-4` the frozen control demanded. The reason is physical, not numerical: the obstruction sits
about two base voxels from the inlet node plane in a plenum only seven base voxels deep, so it
alters the lane **entrance** field, and the entrance region is genuinely inside what the
calculation treats as the measured sub-network. **The absolute lane conductance `Q/ΔP` is not
separable from the surrounding plenum.**

What survives, and what Route A actually needs, is weaker and is stated exactly:

> The return path does not cancel exactly at the level of either absolute conductance, because it
> influences the entrance region near the measurement planes. Its effects on the open and blocked
> conductances are nevertheless **strongly common-mode**, so the pressure-normalised ratio
> `R = (Q/ΔP)_open / (Q0/ΔP0)_blocked` is insensitive to the tested return-path perturbation **to
> bounded numerical accuracy**.

Measured: the two conductance shifts differ by only 0.04 percentage points, so `R` moves by
**3.7e-4** — about **1 %** of the coupling signal `R − 1 = 0.0384` — under a **22.5 %** change in
`ΔP`. That bound is verified against a predeclared criterion, **not generalised from one probe**:
Arm J re-runs the obstruction at **both scientific resolutions**, for the blocked fixture and for
**every frozen aperture that carries a decision clause**, and gates on

```
|R_obstructed / R_nominal − 1|  ≤  1e-3        |s_obstructed − s_nominal|  ≤  5e-4
```

with the induced changes in `ĉ`, `Ξ̂` and the sign of `s − ½` reported (never fitted or corrected),
so that amplification of a small observable perturbation by the inverse would be visible. If either
bound is exceeded in a decision-carrying case, Route A has **not** been sufficiently isolated and
the disposition is `INVALID_EXECUTION` — not a relaxed tolerance and not a switch to Route B.

### What is still demonstrated

1. **Forcing invariance.** The lane conductance is a linear-response property of the driving.
   Probe (**S = 1**, `tau_plus = 1.2`, `g = 0.5/1/2 × 1e-5`): `Q/ΔP = 6.759357 / 6.759506 /
   6.759804`, a spread of **6.6e-5 across a factor of four in forcing**, while `ΔP` itself changed
   by that same factor of four. **This probe is at the smoke resolution and carries no decision.**
   The scientific-resolution statement is Arm A's `×0.5/×1/×2` sweep, and it too found the
   conductance is only *approximately* linear — a genuine O(Re) drift of 2.6e-4 (S=2) and 3.9e-4
   (S=3) that likewise cancels in `R` (erratum **E2**).
2. **The obstruction probe preserves both fixture symmetries**, so it cannot itself break the
   mirror, and it touches no lane voxel.

### Why `R = Q/Q0` is NOT permitted here

The brief allows reporting `R = Q/Q0` only when `ΔP_open` and `ΔP_blocked` are demonstrably equal.
They are not. With `f0 = Q0*R_P/E ≈ 0.037` and a coupling signal `Q/Q0 - 1 = δ`, the omitted factor
is `ΔP0/ΔP ≈ 1 + f0*δ`, so using flows alone would understate `R - 1` by roughly **3.7 % relative**
— comparable to the discretisation budget and large enough to move `Ξ̂`. The pressure-normalised
form is therefore **mandatory**, and `dP_ratio_open_over_blocked` is recorded for every case.

### Why the return path cannot mimic lateral coupling

Three separate reasons, and the argument does not rest on any one:

1. **It is a common node, not a shortcut.** The plenum joins the two lanes at *both ends*. Between
   the frozen node planes the lanes are strictly parallel with no interior connection, which is
   precisely the two-node network's own topology — the baseline the experiment is defined against,
   not a confound added to it.
2. **It is identical in both runs.** The blocked and open masks differ *only* in the aperture
   voxels (asserted: the two mask hashes differ, and the geometric difference is exactly the
   aperture footprint). A structure present unchanged in numerator and denominator cannot produce
   `R ≠ 1`.
3. **The negative control fires.** The identical-path fixture (Arm H) keeps the same plenum and the
   same open aperture but removes the axial contrast, so `X = g1t·g2b - g2t·g1b = 0` and nothing
   drives the bridge. It predicts `R = 1`, `s = 1/2`, zero bridge flux. If the plenum were acting
   as a lateral coupler, this control would depart — it is the direct experimental test of this
   question, and it is executed rather than argued.

## 5. Question 3 — can the existing output provide the required observables?

Only after **RP-D.1**, and this was the tranche's real blocker.

| required | source | available? |
|---|---|---|
| total open and blocked flow `Q`, `Q0` | sum of lane fluxes at a frozen plane, from `ux` | yes, always |
| separate downstream lane flows `q1`, `q2` | `ux` restricted to each lane's `y` slice | yes, always |
| pressure or pressure-equivalent | `rho` → `p = rho/3 - g*x` | **needed `return_fields`** |
| transverse bridge flux | `uy` summed over the aperture footprint | **needed `return_fields`** |
| mass-conservation residuals | plane-to-plane `ux` sums | yes, always |

`solve()` returned `ux` only. It now optionally returns `rho`, `uy` and `uz` (`EXPORTABLE_FIELDS`),
with every standard output bit-identical — see §7 and `tests/test_lb_reference_field_export.py`.

The bridge flux is measured **two ways** — directly from `uy` on the divider mid-plane, and from
`uy` on the adjacent plane — and `q_lat_plane_rel_diff` is reported. Steady-state mass conservation
additionally requires it to equal the change in lane axial flux across the bridge.

## 6. Questions 4 and 5 — lateral bypass, and blocked-vs-open identity

**No periodic lateral bypass exists.** The mask is solid on the whole `y = 0`, `y = ny-1`, `z = 0`
and `z = nz-1` faces, so the `y` and `z` wraps join solid to solid. `connectivity()` asserts
`fluid_on_y_face == fluid_on_z_face == False` and that the fluid space forms **one** component
under `x`-periodic labelling, at every resolution and for blocked and open masks alike.

**The topology is otherwise identical between blocked and open.** Both masks come from the same
constructor with `aperture=None` vs `aperture={kx,kz}`; the aperture argument clears divider voxels
and touches nothing else. The exact voxel-index mirror symmetry
`swap_paths(mirror_x(mask)) == mask` holds for both.

Measured at S=1/2/3, blocked and open (`arm_a.topology`): mirror exact ✓, single connected
component ✓, no fluid on any `y` or `z` face ✓. Blocked outlet share on the probe fixture:
**0.499996** (departure 3.8e-6), plane-to-plane axial flux drift **5.2e-5** relative, maximum Mach
**8.9e-5 – 3.6e-4** — deeply creeping.

## 7. The one non-physical obstacle, and how it was resolved

Route A was physically admissible from the start. What blocked it was **diagnostic field access**,
not topology, and the obstacle was a **test defect**, not a property of the science:

`tests/test_screen_i093.py` compared every source digest recorded in the frozen I-093 screen's
`result.json` against the **current working tree**. Adding an inert optional return value to
`lb_reference.solve` therefore reddened I-093 — and, through `deep_result.json`'s binding of the
cheap result's hash, the deep bundle too. Satisfying that check by regeneration would have cost
~8 h of re-execution (cheap ~1.1 h + deep ~7.0 h, from the bundles' own recorded `wall_s`) to
reproduce a **byte-identical scientific result**.

That invariant is wrong. A frozen result must stay bound to the source it *actually ran*, which git
preserves, not to whatever that file later becomes. The check now recovers the historical blobs at
the commit that added the I-093 protocol (**89dd0978**) and hashes them as raw bytes; all five
recorded digests match, `lb_reference.py` → `9a60371d…a989f` included.

Consequently:

- Route A was physically admissible; the pressure-normalised periodic execution passed its frozen
  controls (§4, §6).
- The initial blocker was **diagnostic field access, not topology**.
- The existing component gained an **optional, numerically inert field export** — no new component,
  no new solver mode, no registry or evidence change.
- A **historical-provenance test was corrected**.
- **No I-093 scientific execution or artifact was regenerated**; the bundle diff against the branch
  base is zero lines, guarded by `tests/test_i093_bundle_immutability.py`.
- **Route B was not required** and is not authorized in this tranche.

The I-093 screen is **not** stale and **not** invalid. Its historical provenance was always
sufficient; the live-tree test encoded the wrong invariant.

## 8. Residual limitations this adjudication does NOT dispose of

Recorded here so they are not mistaken for settled:

- **Nominal node pressures are not uniform.** The node planes sit in the plenum next to the lane
  mouths, where the pressure varies across the section. Every node pressure is reported with its
  fluid-area standard deviation as a fraction of `ΔP`, and the node surfaces are moved by frozen
  offsets to expose the sensitivity. If that nonuniformity is large, a two-node coarse-graining is
  breaking down — which is a finding, not something to tune away.
- **The mid "node" is a region, not a point.** The bridge spans up to 9 base voxels of `x`, so
  `p1` and `p2` are area averages over the aperture footprint and therefore depend on `kx`. Frozen
  as such, with a fixed-footprint variant reported as sensitivity.
- **Junction and entrance losses are inside the measured sub-network**, by design. They are part of
  what the coupon-vs-field comparison is meant to expose, not an error to correct.
- **No backend cross-check.** Taichi is not installed here, and the port asserts cubic domains and
  exports `ux` only. Recorded as NOT PERFORMED, never as passed.
