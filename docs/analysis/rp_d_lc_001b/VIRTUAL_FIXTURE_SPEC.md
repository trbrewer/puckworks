# RP-D-LC-001b — corrected lateral-only virtual-fixture specification

```
DETERMINISTIC_SYNTHETIC_GEOMETRY — no random pack, no coffee morphology, no seed
PRE-EXECUTION — no solve has been run on any geometry described here
```

The single authority for the geometry is `puckworks/analysis/rp_d_lc_001b_virtual_fixture.py`
(`BASE`, `base_mask`, `scale`, `build_fixture`). This document states what that code builds and
why; where the two could disagree the code is the source of truth and
`tests/test_rp_d_lc_001b_preflight.py` binds it. Machine-readable geometry, including every mask
hash and topology invariant, is `generated/fixture_spec.json`.

`brewer2026.pack_generator` is **deliberately not used**. Random morphology would make it
impossible to tell whether a failure came from the inverse, the fixture, the boundary condition or
the pore realization.

## 1. Construction principle

The fixture is defined once on a **base template of 56 × 24 × 8 base voxels**; a resolution `S`
replicates every base voxel into an `S³` block (`np.repeat` on all three axes). Two resolutions are
therefore **exactly geometrically similar**: every length ratio, every aspect ratio and the
candidate family are identical, and no feature is resolved differently in any way other than voxel
count.

Flow is along `+x`. The box is periodic in `x` (the common plenum wraps) and closed by solid
no-slip walls on both `y` faces and both `z` faces, so the `y` and `z` wraps join solid to solid and
**no periodic lateral bypass exists**.

## 2. What changed from RP-D-LC-001, and why

001's divider was **2 base voxels** thick and its aperture pierced it in a single step. The void was
therefore open to **both lanes along its whole `kx` length** — a pocket in parallel with the lanes,
not merely a connection between them. The identical-path negative control fired exactly as designed
(with `X = 0` exactly and no lateral driver at all) and still measured
`observed R − network R = 0.014277334586`: the aperture **widened the axial channel**.

001b keeps the `x` and `z` layout unchanged and rebuilds the `y` layout so that the lane-facing
opening and the connecting duct are **different features**, and the lane-facing opening is
**present in the blocked fixture too**.

## 3. Base template

### x — flow direction (`nx = 56`, unchanged from 001)

| base stations | region |
|---|---|
| `{53,54,55,0,1,2,3}` (`min(x, 56−x) < 4`) | **common plenum**, full cross-section, one connected node region straddling the wrap |
| `4 … 23` (20) | **upstream segment** |
| `24 … 32` (9) | **transition band** — *both* lanes at the low slot height; hosts the bridge |
| `33 … 52` (20) | **downstream segment** |

Mirror planes: `x = 0` (inside the plenum) and `x = 28` (the centre of the transition band).

### y — lanes and the three-layer divider (`ny = 24`)

| base rows | region | thickness |
|---|---|---|
| `0` | wall | 1 |
| `1 … 8` | **lane 1** | 8 |
| `9, 10` | **port row A** (lane-1 facing) | 2 |
| `11, 12` | **duct row** (the connecting segment) | 2 |
| `13, 14` | **port row B** (lane-2 facing) | 2 |
| `15 … 22` | **lane 2** | 8 |
| `23` | wall | 1 |

The layout is **palindromic**: the `y` flip maps lane 1 ↔ lane 2, port row A ↔ port row B, and the
duct row onto itself. That is what makes the path swap an exact index operation.

The divider exists only over the lane region `x ∈ [4, 52]`; the plenum has no divider, which is
what makes it one common node rather than two.

### z — the conductance contrast (`nz = 8`, unchanged from 001)

`0` wall · fluid from `z = 1` upward · `7` wall. The slot height is the **only** thing that differs
between the two axial segments: `h_high = 6`, `h_low = 4`. The lane is wide (8) and short (4–6), so
it is a slot: conductance scales roughly as `h³`, giving a raw ratio `(6/4)³ = 3.375` and a nominal
signed contrast `c ≈ 0.54`, near the design target. **The geometric ratio is never used as a
conductance** — every `c`, `A₁`, `A₂` and `Ξ` comes from an independently *measured* conductance.

### Segment order

| region | lane 1 | lane 2 |
|---|---|---|
| upstream `4…23` | **high** | low |
| transition `24…32` | low | low |
| downstream `33…52` | low | **high** |

the physical realisation of `(g1_top, g1_bot, g2_top, g2_bot) = (a, b, b, a)`.

## 4. The three fixture states

| state | port rows A and B | duct row | used in |
|---|---|---|---|
| `reference_blocked` | solid (no bridge structure at all) | solid | **P0 only** — the common blocked reference that supplies `c_field` for the admission gate |
| `blocked` | **open** over the footprint | solid | the denominator of `R` for a given candidate |
| `open` | **open** over the footprint | **open** over the footprint | the numerator of `R` |

**The blocked/open difference is exactly the duct-row footprint.** Asserted as an exact voxel-index
set equality at `S ∈ {1,2,3}` for every candidate: the differing voxel set is precisely
`x ∈ bridge_x`, `y ∈ duct_y`, `z ∈ bridge_z`, of size `(wS)(2S)(kz S)`, solid in the blocked fixture
and fluid in the open one.

**This is not identical-path subtraction.** No observable is corrected, fitted or post-processed. A
physically constructible apparatus (a fixture with two blind pockets) is built as the reference for
a physically constructible apparatus (the same fixture with the pockets joined). Because the ports
are common-mode, `R` compares the *same axial network* with the lateral connection off and on —
which is what the two-node model's `R` means, and what 001's blocked fixture did not provide.

## 5. Bridge candidate family

The bridge clears divider voxels and nothing else:

- `x`: `w` base voxels centred on `x = 28`; `w` must be **odd** so the footprint is centred on the
  mirror plane. `w ∈ {3, 5, 7, 9}` (9 fills the transition band).
- `y`: the full 2-base depth of each opened row.
- `z`: `kz` base voxels upward from `z = 1`, `kz ∈ {1, 2, 3, 4}` (4 is the full low slot height).

That is the **16-member predeclared candidate set** (`BRIDGE_CANDIDATES`). `kz = 1` is excluded from
the **12-member scientific subset** (§7) and remains a declared candidate so the exclusion is
visible rather than silent. The frozen selection is made from coupon output and the identical-path
artifact **only**, per `PROTOCOL.md` §11, and is committed before any full-fixture `R`, `s` or `Ξ̂`
is inspected.

`w = 1` is **not** a candidate: it would be 2 lattice voxels at `S = 2`, below the minimum resolved
feature.

## 6. Topology invariants — proven, not inspected

Every one of these is asserted on the mask by `bridge_topology()`, `connectivity()`,
`lane_connection()` and `blocked_open_delta()`, at `S ∈ {1,2,3}`, blocked and open:

| invariant | how it is established |
|---|---|
| **axial end caps solid** | `mask[bridge_x_lo − 1, divider_y, :]` and `mask[bridge_x_hi, divider_y, :]` are entirely solid |
| **no axial through-route confined to the bridge** | the `x` extent of divider-band fluid **inside the lane region** equals the footprint exactly, and its neighbours are solid across the whole divider cross-section |
| **intended lateral ports present** | both port rows are fully fluid over the footprint, in the blocked fixture as well as the open one |
| **the lateral connection exists only when open** | connected-component labelling on the lane traverse **with the plenum excluded**: lanes joined when open, separate when blocked and when reference. Global connectivity cannot decide this, because the plenum joins the lanes at both ends by design |
| **one connected fluid domain** | `x`-periodic union-find labelling returns a single component |
| **no periodic lateral bypass** | no fluid on any `y` or `z` face, so both wraps join solid to solid |
| **blocked/open delta** | exactly the duct-row footprint, by voxel-index set equality |
| **exact mirror symmetry** | `swap_paths(mirror_x(mask, S)) == mask` as array equality |
| **exact path swap** | `swap_paths(mask) == flip(mask, axis=1)`, an involution; the palindromic `y` layout is asserted arithmetically |
| **minimum feature resolution** | every critical feature ≥ `MIN_FEATURE_VOX = 4` lattice voxels at `S = 2` |

## 7. Resolutions and the minimum resolved feature

`S_COARSE = 2` and `S_FINE = 3` are the **scientific** resolutions (a 1.5× refinement).
`S_SMOKE = 1` exists for tests and carries no scientific claim.

Minimum feature sizes in lattice voxels:

| feature | base | S = 2 | S = 3 |
|---|---|---|---|
| lane width | 8 | 16 | 24 |
| high slot height `h_high` | 6 | 12 | 18 |
| low slot height `h_low` | 4 | 8 | 12 |
| bridge transverse length (port A → port B) | 6 | 12 | 18 |
| port row depth | 2 | 4 | 6 |
| duct row depth | 2 | 4 | 6 |
| bridge footprint `w = 3` (smallest) | 3 | 6 | 9 |
| bridge height `kz = 2` (smallest scientific) | 2 | 4 | 6 |
| bridge height `kz = 1` (**excluded**) | 1 | **2** | 3 |

**Justification, measured rather than assumed.** Arm A of the closed 001 tranche ran the canonical
plane channel over `h = 3 … 31` lattice units and the permeability error follows a clean
`error(%) = 50/h²` (measured: `h=3 → +5.556 %`, `5 → +2.000`, `7 → +1.020`, `11 → +0.413`,
`15 → +0.222`, `23 → +0.0945`, `31 → +0.0520`). So the frozen elements carry element-level
discretisation errors of ~0.8 % (`h_low`, S=2) down to ~0.15 % (`h_high`, S=3), and the smallest
scientific bridge feature ~3 % at S=2 and ~1.4 % at S=3. `kz = 1` would be a 2-voxel feature at S=2
with a ~12 % element error, and is therefore excluded. `MIN_FEATURE_VOX = 4`.

Because `Ξ_field` and `Ξ̂` are derived from the *same* run at the *same* resolution, an element-level
discretisation error is common to truth and inference and is not an error in their comparison; the
resolution-consistency test (`PROTOCOL.md` §6.5) is what bounds the residual, and its tolerance is
derived from exactly this law.

## 8. The two exact index transformations

Both are index operations on the *same* array. No allegedly equivalent geometry is ever rebuilt.

- **Mirror** `mirror_x(mask, S) = roll(flip(mask, axis=0), S, axis=0)` — the cellwise reflection
  `b → (56 − b) mod 56` with sub-cell order reversed.
- **Path swap** `swap_paths(mask) = flip(mask, axis=1)` — reflection of `y` about the divider
  mid-plane, exchanging lane 1 and lane 2, mapping port row A onto port row B and the duct row,
  both walls and both lanes onto themselves.

**Exact mirror symmetry** is the assertion `swap_paths(mirror_x(mask, S)) == mask`, checked as an
array equality at every resolution, blocked and open, before the adversarial perturbation. For the
exact mirror the two transformations coincide, so the path-swapped fixture is the original reflected
in `x` — a genuinely different flow problem, since the forcing still points `+x`.

## 9. Controls built into the geometry

- **Reference blocked fixture** — `bridge=None`. No bridge structure at all; the only geometry
  allowed to supply `c_field` to the reachable-set admission gate.
- **Blocked fixture** — `connected=False`. Identical to the open fixture in every voxel except the
  duct-row footprint.
- **Identical-path negative control** — `variant="identical"`: both lanes carry lane 1's segment
  order, so `X = g1t·g2b − g2t·g1b = 0` **exactly**, there is no uncoupled mid-node pressure gap,
  and nothing drives the bridge at any footprint. Predicts `R = 1`, `s = ½`, zero bridge flux — the
  decisive measurement of the residual axial artifact.
- **Path-swapped fixture** — `swapped=True`, produced by the exact `swap_paths` index map.
- **One-voxel adversarial asymmetry** (`PERTURBATIONS`, applied only at `S_FINE`):
  - `one_voxel_plug` — exactly **one** lattice voxel turned solid at base cell `(40, 4, 2)`, inside
    lane 1's downstream segment;
  - `one_voxel_slab` — lane 1's upstream-segment end plane moved by **one lattice voxel**, the
    smallest perturbation that changes a segment *length* rather than a point.

  Both are predeclared here, before execution, and both are reported whatever they show.

## 10. Coupons

- **Axial coupon** (`build_axial_coupon`) — a straight `x`-periodic duct reproducing one segment:
  same slot height, same lane width, same length (20 base voxels), same wall treatment (the 1-base
  outer wall on one side, the 6-base divider on the other, cropped to base `y ∈ [0, 14]` so the wrap
  joins the two solid regions). In a uniform periodic duct the pressure drop is `g·L` exactly, so
  `G = Q/(g·L)` needs no density field. Calibrated in **two lattice orientations** by rotating the
  *cross-section* (never the flow axis, which must stay `+x`), so lattice anisotropy is reported
  rather than assumed away.
- **Bridge coupon** (`build_bridge_coupon`) — **axis-rotated**: the whole three-layer divider
  traverse (port A → duct → port B) with its footprint, rebuilt so the transverse bridge axis lies
  along the solver's `+x`. The existing x-directed kernel therefore measures the transverse
  conductance directly with **no invented anisotropy correction**. Plena of the transition-band slot
  height sit on both sides and join through the wrap, exactly as the fixture's common node does.
  Frozen: plenum depth 6 base voxels each side, walled span 13 base voxels, divider traverse 6 base
  voxels. Only the **connected** bridge has a coupon — a blocked bridge conducts nothing by
  construction.

The bridge coupon cannot reproduce the assembled context — its plena are not the fixture's lanes.
That is the point: the coupon prediction is a **composability prediction**, deliberately separate
from the in-situ field truth, and the gap between them is a reported quantity.

## 10b. Lateral pressure faces (correction `PREFLIGHT-C2`)

The two frozen faces that measure the lateral driving-pressure difference, over the **exact bridge
`(x, z)` footprint**:

| face | lattice row | side |
|---|---|---|
| `y_face1` | `9S - 1` | last lane-1 row before the divider |
| `y_face2` | `15S` | first lane-2 row after the divider |

Both are fully fluid over the footprint in every bridge-carrying state and share it exactly —
asserted per case. The effective pressure is the same convention the axial records use,
`p_eff = rho/3 - g*x`, evaluated **nodewise before averaging**, so the body-force potential is
subtracted correctly across a multi-`x` footprint. Fluid nodes only; solids excluded, never counted
as zero.

`delta_p_lateral` is formed **pointwise** (face 1 minus face 2 at the same node) and then averaged.
Because both faces span the same footprint, the axial pressure gradient across it is common to them
and cancels **exactly**; the pointwise spread therefore measures genuine face-to-face nonuniformity
and its standard error is the conservative uncertainty on the mean gap. The individual face spreads
are retained as a **coarse-graining diagnostic** — as 001 reported them — explicitly not as an
uncertainty on the gap.

Sign convention: `delta_p_lateral = p_face1 - p_face2`, **positive drives lane 1 -> lane 2 along
+y**, matching `lateral_coupling.model1_two_path`'s canonical `q_lat_1to2 = G_lat(p1 - p2)`.

For an identical-path control the geometry supplies only the **expectation** of a zero lateral
driver; execution validity additionally requires the **measured** gap to clear
`TOL_LATERAL_DRIVER_REL`. A geometry label may never certify the premise of the negative control
(`PREFLIGHT_ERRATA.md` PE-15).

## 11. Recorded per geometry

`geometry dimensions · every named region and measurement plane · solid/fluid counts ·
connected-component checks · the lane-region lateral-connection verdict · the bridge topology audit
· the blocked/open delta · the minimum-feature report · SHA-256 of every mask (over the packed bits
plus the shape) · the transformation used for the path swap`. Large field arrays are **never**
committed. Regeneration is a single deterministic call:

```python
from puckworks.analysis import rp_d_lc_001b_virtual_fixture as vf
mask, meta = vf.build_fixture(S, bridge={"w": .., "kz": ..}, connected=True,
                              variant="mirror", swapped=False)
```

## 12. Coordinate reference — the transition band at `S = 1`, `w = 3`, `kz = 2`

`x = 28` (the mirror plane), viewed in the `y–z` plane. `#` solid, `.` fluid, `P` port row,
`D` duct row.

```
   z=7  # # # # # # # # # # # # # # # # # # # # # # # #     wall
   z=6  # # # # # # # # # # # # # # # # # # # # # # # #     (above the low slot: solid)
   z=5  # # # # # # # # # # # # # # # # # # # # # # # #
   z=4  # . . . . . . . . # # # # # # . . . . . . . . #     lanes only
   z=3  # . . . . . . . . # # # # # # . . . . . . . . #
   z=2  # . . . . . . . . P P D D P P . . . . . . . . #     bridge (kz = 2)
   z=1  # . . . . . . . . P P D D P P . . . . . . . . #
   z=0  # # # # # # # # # # # # # # # # # # # # # # # #     wall
        y=0 1 2 3 4 5 6 7 8 9 . 11. 13. 15. . . . . 2223
             \--- lane 1 ---/ \--A--/\-D-/\--B--/ \--- lane 2 ---/
```

In the **blocked** fixture the two `D` columns are solid and the `P` columns are unchanged; in the
**reference** fixture all six divider columns are solid. At `x = 28 ± 2` (outside the `w = 3`
footprint) all six divider columns are solid in every state — the axial end caps.

These diagrams and the coordinate tables in `generated/fixture_spec.json` are **design artifacts**,
generated without running the solver. They are not scientific results.
