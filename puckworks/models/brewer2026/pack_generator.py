"""puck_pack.py — synthetic coffee-puck generator + column-flux sigma pipeline.

Step-3 groundwork for the microstructural sigma study:
  make_pack()    Boolean (overlapping-sphere) packing at any target solid fraction,
                 boulder radius from Cameron's microstructure table for a grind
                 setting, with a controllable columnar heterogeneity field standing
                 in for fines-driven clustering (explicit 12 um fines need ~4 um
                 voxels -> FluidX3D-scale domains; flagged, not silently ignored).
  sigma_micro()  Partition an LB velocity field into streamtube columns, measure
                 the per-column flux distribution, fit lognormal sigma, and report
                 the same observables our paper anchors sigma to (CV, top-quartile
                 flow share).

Overlapping spheres are deliberate: the percolation permeability law of
Wadsworth et al. 2026 was validated on exactly this model class (their refs
20, 26), so synthetic packs stay inside the validated universality class.
"""
import numpy as np
from scipy.ndimage import gaussian_filter

def boulder_radius_um(gs):
    """Cameron boulder radius for a grind setting, in microns (standalone-safe)."""
    try:
        from puckworks.models.cameron2020 import extraction_bdf as em
        return float(em.grind_microstructure(gs)[2]) * 1e6
    except ImportError:
        import numpy as _np
        return float(_np.interp(gs, [1.0, 1.5, 2.0, 2.5], [273.9, 335.4, 335.4, 410.8]))

def _sphere_stencil(r):
    n = int(np.ceil(r))
    dx, dy, dz = np.meshgrid(*(np.arange(-n, n+1),)*3, indexing="ij")
    m = dx*dx + dy*dy + dz*dz <= r*r
    return dx[m], dy[m], dz[m]

def hetero_field(L, corr_len, seed):
    """Columnar (y,z) heterogeneity field, zero mean, unit std, periodic."""
    rng = np.random.default_rng(seed)
    h = gaussian_filter(rng.standard_normal((L, L)), corr_len, mode="wrap")
    return (h - h.mean()) / h.std()

def make_pack(L=40, voxel_um=30.0, gs=1.3, phis_target=0.55,
              hetero_amp=0.0, hetero_len=8, seed=0, batch=64, verbose=True,
              r_um=None, w_floor=0.25):
    """Periodic boolean pack. Boulder radius a2(gs) from Cameron's table.

    hetero_amp modulates local placement probability with a columnar field:
    amp=0 -> statistically uniform; amp~1-2 -> strongly channelled bed.
    Returns (solid, meta).
    """
    try:
        from puckworks.models.cameron2020 import extraction_bdf as em
        phi1, phi2, a2, _, _ = em.grind_microstructure(gs)
    except ImportError:                      # standalone (e.g. Colab): baked-in table
        _GS  = [np.float64(1.0), np.float64(1.5), np.float64(2.0), np.float64(2.5)]
        _A2  = [np.float64(273.9), np.float64(335.4), np.float64(335.4), np.float64(410.8)]
        _PH1 = [np.float64(0.1689), np.float64(0.1343), np.float64(0.12), np.float64(0.078)]
        import numpy as _np
        a2   = _np.interp(gs, _GS, _A2) * 1e-6
        phi1 = _np.interp(gs, _GS, _PH1)
        phi2 = 0.0
    if r_um is not None:                    # explicit grain radius (e.g. Wadsworth <R>)
        a2 = r_um * 1e-6
    r_vox = a2*1e6 / voxel_um
    if 12.0/voxel_um >= 1.0/3.0:
        fines_note = ("fines (a1 = 12 um) are sub-voxel at %.0f um resolution; "
                      "represented implicitly via the heterogeneity field" % voxel_um)
    else:
        fines_note = "resolution admits explicit fines (not implemented in this demo)"

    rng = np.random.default_rng(seed)
    H = hetero_field(L, hetero_len, seed+1)
    # Weight floor: channels are preferential paths THROUGH grains, not empty
    # pipes -- and open slabs also make LB spin-up time scale as width^2.
    w = np.clip(1.0 + hetero_amp*H, w_floor, None)   # acceptance weight per (y,z)
    w /= w.max()

    dx, dy, dz = _sphere_stencil(r_vox)
    solid = np.zeros((L, L, L), dtype=bool)
    n_placed = 0
    done = False
    while not done:
        cx = rng.integers(0, L, batch)
        cy = rng.integers(0, L, batch)
        cz = rng.integers(0, L, batch)
        keep = rng.random(batch) < w[cy, cz]
        for x0, y0, z0 in zip(cx[keep], cy[keep], cz[keep]):
            solid[(x0+dx) % L, (y0+dy) % L, (z0+dz) % L] = True
            n_placed += 1
            if solid.mean() >= phis_target:
                done = True
                break
    meta = dict(L=L, voxel_um=voxel_um, gs=gs, a2_um=a2*1e6, r_vox=float(r_vox),
                phis=float(solid.mean()), phi=float(1-solid.mean()),
                n_spheres=n_placed, hetero_amp=hetero_amp, hetero_len=hetero_len,
                fines_note=fines_note, seed=seed)
    if verbose:
        print(f"pack: L={L} ({L*voxel_um/1000:.2f} mm), boulder r={r_vox:.1f} vox, "
              f"{n_placed} spheres, phis={solid.mean():.3f}, amp={hetero_amp}")
    return solid, meta

def sigma_micro(ux, solid, ncol=4, g=None):
    """Streamtube-column flux statistics from an LB velocity field (flow along x).

    Partitions the (y,z) cross-section into ncol x ncol columns, computes each
    column's superficial flux, normalizes to unit mean, and reports:
      sigma  - std of ln(flux)  (the lognormal spread our ensemble model uses)
      cv     - coefficient of variation of column flux
      top25  - fraction of total flow carried by the fastest quarter of columns
    """
    L = ux.shape[1]
    u = ux.copy(); u[solid] = 0.0
    edges = np.linspace(0, L, ncol+1).astype(int)
    q = np.zeros((ncol, ncol))
    for i in range(ncol):
        for j in range(ncol):
            q[i, j] = u[:, edges[i]:edges[i+1], edges[j]:edges[j+1]].mean()
    k = q.ravel() / q.mean()
    kpos = np.clip(k, 1e-6, None)
    sig = float(np.std(np.log(kpos), ddof=1))
    cv = float(np.std(k, ddof=1))
    ks = np.sort(k)[::-1]
    n25 = max(1, len(k)//4)
    top25 = float(ks[:n25].sum() / ks.sum())
    return dict(sigma=sig, cv=cv, top25=top25, columns=k.round(3).tolist())

if __name__ == "__main__":
    import json, sys
    amp = float(sys.argv[1]) if len(sys.argv) > 1 else 0.0
    tag = sys.argv[2] if len(sys.argv) > 2 else ("A" if amp == 0 else "B")
    solid, meta = make_pack(L=40, voxel_um=30.0, gs=1.3, phis_target=0.55,
                            hetero_amp=amp, hetero_len=8, seed=42)
    np.savez_compressed(f"/tmp/pack_{tag}.npz", solid=solid, meta=json.dumps(meta))
    print("saved /tmp/pack_%s.npz  |  %s" % (tag, meta["fines_note"]))
