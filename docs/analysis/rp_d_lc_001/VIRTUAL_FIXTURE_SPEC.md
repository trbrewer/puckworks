# RP-D-LC-001 — deterministic virtual-fixture specification

```
DETERMINISTIC_SYNTHETIC_GEOMETRY — no random pack, no coffee morphology, no seed
```

The single authority for the geometry is `puckworks/analysis/rp_d_lc_virtual_fixture.py`
(`BASE`, `base_mask`, `scale`, `build_fixture`). This document states what that code builds and
why; where the two could disagree, the code is the source of truth and the tests bind it.

`brewer2026.pack_generator` is **deliberately not used**. Random morphology would make it
impossible to tell whether a failure came from the inverse, the fixture, the boundary condition or
the pore realization.

## 1. Construction principle

The fixture is defined once on a **base template of 56 × 20 × 8 base voxels** and a resolution `S`
replicates every base voxel into an `S³` block (`np.repeat` on all three axes). Two resolutions are
therefore **exactly geometrically similar**: every length ratio, every aspect ratio and the aperture
family are identical, and no feature is resolved "differently" in any way other than voxel count.

Flow is along `+x`. The box is periodic in `x` (the common plenum wraps — see
`BOUNDARY_TOPOLOGY_ADJUDICATION.md`) and closed by solid no-slip walls on both `y` faces and both
`z` faces, so the `y` and `z` wraps join solid to solid and no periodic lateral bypass exists.

## 2. Base template

### x — flow direction (`nx = 56`)

| base stations | region |
|---|---|
| `{53,54,55,0,1,2,3}` (`min(x, 56-x) < 4`) | **common plenum**, full cross-section, one connected node region straddling the wrap |
| `4 … 23` (20) | **upstream segment** |
| `24 … 32` (9) | **transition band** — *both* lanes at the low slot height; hosts the bridge |
| `33 … 52` (20) | **downstream segment** |

The mirror planes are `x = 0` (inside the plenum) and `x = 28` (the centre of the transition band).

### y — lane separation (`ny = 20`)

`0` wall · `1…8` **lane 1** (width 8) · `9,10` **divider** (thickness 2) · `11…18` **lane 2**
(width 8) · `19` wall.

The divider exists only over the lane region `x ∈ [4, 52]`; the plenum has no divider, which is
what makes it one common node rather than two.

### z — the conductance contrast (`nz = 8`)

`0` wall · fluid from `z = 1` upward · `7` wall. The slot height is the **only** thing that differs
between the two axial segments:

- `h_high = 6` base voxels, `h_low = 4`.
- The lane is wide (8) and short (4–6), so it is a slot: conductance scales roughly as `h³`, giving
  a raw ratio `(6/4)³ = 3.375` and a nominal signed contrast `c ≈ 0.54` — near the design target
  `c ≈ 0.5` (a ~3:1 segment-conductance ratio).
- **The geometric ratio is never used as a conductance.** Every `c`, `A₁`, `A₂` and `Ξ` in the
  result comes from an independently *measured* conductance (coupon calibration, or in-situ field
  coarse-graining). The dimensions only place the design in the right region.

### Segment order

| region | lane 1 | lane 2 |
|---|---|---|
| upstream `4…23` | **high** | low |
| transition `24…32` | low | low |
| downstream `33…52` | low | **high** |

This is the physical realisation of `(g1_top, g1_bot, g2_top, g2_bot) = (a, b, b, a)`.

## 3. The two exact index transformations

Both are index operations on the *same* array. No allegedly equivalent geometry is ever rebuilt.

- **Mirror** `mirror_x(mask, S) = roll(flip(mask, axis=0), S, axis=0)` — the cellwise reflection
  `b → (56 - b) mod 56` with sub-cell order reversed.
- **Path swap** `swap_paths(mask) = flip(mask, axis=1)` — reflection of `y` about the divider
  mid-plane, exchanging lane 1 and lane 2 and mapping the divider and both walls onto themselves.

**Exact mirror symmetry** is the assertion `swap_paths(mirror_x(mask, S)) == mask`, checked as an
array equality at every resolution, blocked and open, before the adversarial perturbation. For the
exact mirror the two transformations coincide (`swap_paths(mask) == mirror_x(mask)`), so the
path-swapped fixture is the original reflected in `x` — a genuinely different flow problem, since
the forcing still points `+x`.

## 4. Bridge aperture family

The aperture clears divider voxels and nothing else:

- `x`: `kx` base voxels centred on `x = 28`; `kx` must be **odd** so the aperture is centred on the
  mirror plane. `kx ∈ {1, 3, 5, 7, 9}` (9 fills the transition band).
- `y`: the full divider thickness (both base rows).
- `z`: `kz` base voxels upward from `z = 1`, `kz ∈ {1, 2, 3, 4}` (4 is the full low slot height).

That is the **20-member predeclared candidate set** (`APERTURE_CANDIDATES`). The frozen scientific
subset is selected from **coupon output only**, per `PROTOCOL.md` §9, and recorded in
`APERTURE_FREEZE.md` before any full-fixture `R`, `s` or `Ξ̂` is inspected.

## 5. Resolutions and the minimum resolved feature

`S_COARSE = 2` and `S_FINE = 3` are the **scientific** resolutions (a 1.5× refinement).
`S_SMOKE = 1` exists for tests and carries no scientific claim.

Minimum feature sizes in lattice units:

| feature | S = 2 | S = 3 |
|---|---|---|
| low slot height `h_low` | 8 | 12 |
| high slot height `h_high` | 12 | 18 |
| lane width | 16 | 24 |
| divider thickness (= bridge length) | 4 | 6 |
| aperture `kz = 2` (smallest frozen) | 4 | 6 |
| aperture `kz = 1` (**excluded**) | 2 | 3 |

**Justification, measured rather than assumed.** Arm A runs the canonical plane channel over
`h = 3 … 31` lattice units and the permeability error follows a clean

```
error(%) = 50 / h^2
```

(measured: `h=3 → +5.556 %`, `5 → +2.000`, `7 → +1.020`, `11 → +0.413`, `15 → +0.222`,
`23 → +0.0945`, `31 → +0.0520`). So the frozen elements carry element-level discretisation errors
of ~0.8 % (`h_low`, S=2) down to ~0.15 % (`h_high`, S=3), and the smallest frozen aperture ~3 % at
S=2 and ~1.4 % at S=3. `kz = 1` would be a 2-voxel feature at S=2 with a ~12 % element error and is
therefore **excluded from the scientific subset** — it remains a candidate only so the exclusion is
visible rather than silent. `MIN_FEATURE_VOX = 4`.

Because `Ξ_field` and `Ξ̂` are derived from the *same* run at the *same* resolution, an element-level
discretisation error is common to truth and inference and is not an error in their comparison;
the grid-refinement arm is what bounds the residual.

## 6. Controls built into the geometry

- **Blocked fixture** — `aperture=None`. Identical in every voxel except the aperture footprint.
- **Identical-path negative control** — `variant="identical"`: both lanes carry lane 1's segment
  order, so `X = g1t·g2b − g2t·g1b = 0` exactly, there is no uncoupled mid-node pressure gap, and
  nothing drives the bridge at any aperture. Predicts `R = 1`, `s = 1/2`, zero bridge flux.
- **Path-swapped fixture** — `swapped=True`, produced by the exact `swap_paths` index map.
- **One-voxel adversarial asymmetry** (`PERTURBATIONS`, applied only at `S_FINE`):
  - `one_voxel_plug` — exactly **one** lattice voxel turned solid at base cell `(40, 4, 2)`, inside
    lane 1's downstream segment. The literal one-voxel case.
  - `one_voxel_slab` — lane 1's upstream-segment end plane moved by **one lattice voxel**
    (a one-voxel-*thick* slab, `24 × 6 = 144` voxels at S=3). This is the smallest perturbation that
    changes a segment *length* rather than a point, and it is the informative one: a single interior
    voxel in a duct of this size is far below the 1 % asymmetry scale that WP6-LC-IDENT showed can
    bias `Ξ̂` by ~5×.

  Both are predeclared here, before execution, and both are reported whatever they show.

## 7. Coupons

- **Axial coupon** (`build_axial_coupon`) — a straight `x`-periodic duct reproducing one segment:
  same slot height, same lane width, same length (20 base voxels), and the same wall treatment
  (the 1-base outer wall on one side, the 2-base divider on the other, cropped to base `y ∈ [0,10]`
  so the wrap joins the two walls). In a uniform periodic duct the pressure drop is `g·L` exactly,
  so `G = Q/(g·L)` needs no density field — and Arm A checks the density-based value agrees.
  Calibrated in **two lattice orientations** (`x` and `y`, by transposing the mask) so lattice
  anisotropy is reported rather than assumed away.
- **Bridge coupon** (`build_bridge_coupon`) — **axis-rotated**: the divider slab and its aperture
  are rebuilt with the transverse (bridge) axis along the solver's `+x`, so the existing x-directed
  kernel measures the transverse conductance directly with **no invented anisotropy correction**.
  Plena of the transition-band slot height sit on both sides and join through the wrap, exactly as
  the full fixture's common node does. Frozen: plenum depth 6 base voxels each side, transverse
  span 13 base voxels (walled), divider thickness 2 base voxels.

The bridge coupon cannot reproduce the assembled context — its plena are not the fixture's lanes.
That is the point: §8.1 of the protocol is a **composability prediction**, deliberately separate
from the §8.2 in-situ truth, and the gap between them is a reported quantity.

## 8. Recorded per geometry

`geometry dimensions · every named region and measurement plane · solid/fluid counts ·
connected-component checks · SHA-256 of every mask (`mask_hash`, over the packed bits plus the
shape) · the transformation used for the path swap`. Large field arrays are **never** committed;
`_json_default` raises on an ndarray so a run record cannot accidentally carry one. Regeneration is
a single deterministic call, recorded in `result.json`:

```python
from puckworks.analysis import rp_d_lc_virtual_fixture as vf
mask, meta = vf.build_fixture(S, aperture={"kx": .., "kz": ..}, variant="mirror", swapped=False)
```
