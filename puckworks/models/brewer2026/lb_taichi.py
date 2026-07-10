"""taichi_lb.py — Taichi port of the validated mini_lb D3Q19 TRT permeability kernel.

Same physics as mini_lb.py (validated: plane Poiseuille +0.03%; SC sphere
arrays -7..-8% at toy radii, converging ~1/a). One-line switch between CPU
(analysis/testing, e.g. in a Claude session) and GPU (production on a local
card): change ARCH below or pass arch= to init_lb().

    import taichi_lb as tlb
    tlb.init_lb(arch="gpu")                    # or "cpu"
    r = tlb.solve(solid, g=1e-6, tau_plus=1.5) # solid: numpy bool (L,L,L)
    r["k"], r["ux"]                            # permeability (lu), velocity field

API and conventions match mini_lb.solve() so the two kernels cross-check:
periodic box, full-way bounce-back, constant body force in +x, TRT with
magic Lambda = 3/16, raw-velocity equilibrium + source-term forcing,
half-force correction applied at measurement only.
"""
import numpy as np
import time

try:
    import taichi as ti
except ImportError:      # optional dependency: pip install puckworks[lb]
    ti = None

# ---------------- D3Q19 lattice (identical ordering to mini_lb) ----------------
C_np = np.array([
    [0,0,0],
    [1,0,0],[-1,0,0],[0,1,0],[0,-1,0],[0,0,1],[0,0,-1],
    [1,1,0],[-1,-1,0],[1,-1,0],[-1,1,0],
    [1,0,1],[-1,0,-1],[1,0,-1],[-1,0,1],
    [0,1,1],[0,-1,-1],[0,1,-1],[0,-1,1]], dtype=np.int32)
W_np = np.array([1/3] + [1/18]*6 + [1/36]*12)
OPP_np = np.array([0,2,1,4,3,6,5,8,7,10,9,12,11,14,13,16,15,18,17], dtype=np.int32)
Q = 19

_state = {}

def init_lb(arch="cpu", dtype="f64"):
    """arch: 'cpu' or 'gpu' (CUDA/Vulkan/Metal via ti.gpu). dtype: 'f64' or 'f32'.
    f32 halves memory (Colab T4: ~300^3 domains) but requires a stronger driving
    force to stay above rounding: use g ~ 1e-4 (Stokes linearity makes this free;
    Ma ~ 1e-3, Re << 1). Re-initializes the Taichi runtime, freeing prior fields —
    sweep drivers should call this once per run to avoid field accumulation."""
    fp = ti.f64 if dtype == "f64" else ti.f32
    ti.init(arch=ti.gpu if arch == "gpu" else ti.cpu, default_fp=fp)
    _state["dtype"] = fp
    _state["ready"] = True

def solve(solid_np, g=1e-6, tau_plus=1.5, max_steps=20000, check=100,
          rtol=1e-6, min_steps=1500, verbose=True):
    if not _state.get("ready"):
        init_lb()
    L = solid_np.shape[0]
    assert solid_np.shape == (L, L, L), "cubic domains only in this port"
    fdt = _state["dtype"]

    nu = (tau_plus - 0.5) / 3.0
    lam = 3.0/16.0
    tau_minus = 0.5 + lam/(tau_plus - 0.5)
    om_p, om_m = 1.0/tau_plus, 1.0/tau_minus

    f     = ti.field(fdt, shape=(Q, L, L, L))
    fpost = ti.field(fdt, shape=(Q, L, L, L))
    solid = ti.field(ti.i8, shape=(L, L, L))
    ux    = ti.field(fdt, shape=(L, L, L))
    C   = ti.Vector.field(3, ti.i32, shape=Q)
    Wt  = ti.field(fdt, shape=Q)
    OPP = ti.field(ti.i32, shape=Q)
    C.from_numpy(C_np); Wt.from_numpy(W_np); OPP.from_numpy(OPP_np)
    solid.from_numpy(solid_np.astype(np.int8))

    @ti.kernel
    def init_eq():
        for x, y, z in ti.ndrange(L, L, L):
            for i in ti.static(range(Q)):
                f[i, x, y, z] = Wt[i]

    @ti.kernel
    def collide():
        for x, y, z in ti.ndrange(L, L, L):
            if solid[x, y, z] == 1:
                for i in ti.static(range(Q)):
                    fpost[i, x, y, z] = f[i, x, y, z]
            else:
                rho = 0.0
                u = ti.Vector([0.0, 0.0, 0.0])
                for i in ti.static(range(Q)):
                    fi = f[i, x, y, z]
                    rho += fi
                    u += fi * ti.Vector([ti.cast(C[i][0], fdt),
                                         ti.cast(C[i][1], fdt),
                                         ti.cast(C[i][2], fdt)])
                u /= rho
                u2 = u.dot(u)
                for i in ti.static(range(Q)):
                    cu  = (C[i][0]*u[0] + C[i][1]*u[1] + C[i][2]*u[2])
                    feq_i = Wt[i]*rho*(1.0 + 3.0*cu + 4.5*cu*cu - 1.5*u2)
                    j = OPP[i]
                    cuj = (C[j][0]*u[0] + C[j][1]*u[1] + C[j][2]*u[2])
                    feq_j = Wt[j]*rho*(1.0 + 3.0*cuj + 4.5*cuj*cuj - 1.5*u2)
                    fp  = 0.5*(f[i,x,y,z] + f[j,x,y,z]);  fep = 0.5*(feq_i + feq_j)
                    fm  = 0.5*(f[i,x,y,z] - f[j,x,y,z]);  fem = 0.5*(feq_i - feq_j)
                    S = 3.0*Wt[i]*ti.cast(C[i][0], fdt)*g
                    fpost[i, x, y, z] = f[i,x,y,z] - om_p*(fp-fep) - om_m*(fm-fem) + S

    @ti.kernel
    def stream_bb():
        # push streaming with periodic wrap
        for x, y, z in ti.ndrange(L, L, L):
            for i in ti.static(range(Q)):
                xn = (x + C[i][0] + L) % L    # +L: '%' on negatives differs across backends
                yn = (y + C[i][1] + L) % L
                zn = (z + C[i][2] + L) % L
                f[i, xn, yn, zn] = fpost[i, x, y, z]
        # full-way bounce-back at solids (after all writes complete)
        ti.loop_config(serialize=False)
        for x, y, z in ti.ndrange(L, L, L):
            if solid[x, y, z] == 1:
                for i in ti.static(range(1, Q, 2)):   # pair heads: (1,2)(3,4)...(17,18)
                    j = OPP[i]
                    tmp = f[i, x, y, z]
                    f[i, x, y, z] = f[j, x, y, z]
                    f[j, x, y, z] = tmp

    qsum = ti.field(ti.f64, shape=())
    umax = ti.field(ti.f64, shape=())

    @ti.kernel
    def measure_q():
        qsum[None] = 0.0
        umax[None] = 0.0
        for x, y, z in ti.ndrange(L, L, L):
            if solid[x, y, z] == 0:
                rho = 0.0
                m = ti.Vector([0.0, 0.0, 0.0])
                for i in ti.static(range(Q)):
                    fi = f[i, x, y, z]
                    rho += fi
                    m += fi * ti.Vector([ti.cast(C[i][0], fdt),
                                         ti.cast(C[i][1], fdt),
                                         ti.cast(C[i][2], fdt)])
                u = m / rho
                qsum[None] += ti.cast(u[0] + 0.5*g, ti.f64)   # f64 accumulation
                ti.atomic_max(umax[None], ti.cast(u.norm(), ti.f64))

    @ti.kernel
    def export_ux():
        for x, y, z in ti.ndrange(L, L, L):
            if solid[x, y, z] == 1:
                ux[x, y, z] = 0.0
            else:
                rho = 0.0; mx = 0.0
                for i in ti.static(range(Q)):
                    rho += f[i, x, y, z]
                    mx += f[i, x, y, z]*C[i][0]
                ux[x, y, z] = mx/rho + 0.5*g

    init_eq()
    q_prev, t0 = None, time.time()
    step = 0
    for step in range(1, max_steps+1):
        collide()
        stream_bb()
        if step % check == 0:
            measure_q()
            q = qsum[None] / (L*L*L)
            um = umax[None]
            if not np.isfinite(q):
                raise FloatingPointError(
                    f"NaN at step {step}: lattice velocity blew up. Reduce g "
                    f"(heterogeneous/channelled packs need g ~ 3e-6; u_max scales "
                    f"as g x channel_width^2 / nu and must stay << 0.1).")
            if um > 0.10:
                print(f"  WARNING step {step}: u_max = {um:.3f} lattice units "
                      f"(Mach ~ {um*3**0.5:.2f}) - reduce g before trusting results")
            if verbose:
                print(f"  step {step:6d}  q = {q:.6e}  u_max = {um:.2e}  ({time.time()-t0:.0f}s)")
            if step >= min_steps and q_prev is not None and abs(q - q_prev) < rtol*abs(q):
                break
            q_prev = q

    if step == max_steps:
        print(f"  WARNING: hit max_steps={max_steps} without meeting rtol={rtol} "
              f"- treat k and the flow field as UNCONVERGED")
    measure_q()
    q = qsum[None] / (L*L*L)
    export_ux()
    phi = 1.0 - solid_np.mean()
    return dict(q=float(q), k=float(nu*q/(g*phi)), phi=float(phi), nu=nu,
                steps=step, seconds=round(time.time()-t0, 1),
                ux=ux.to_numpy())

# Bounce-back swap: pairs are adjacent in this ordering, (1,2)(3,4)...(17,18),
# so iterating the odd pair-heads i = 1,3,...,17 exchanges each pair exactly once.

if __name__ == "__main__":
    import json
    init_lb(arch="cpu")
    # channel validation, identical bookkeeping to mini_lb
    Nz = 41
    solid = np.zeros((Nz, Nz, Nz), dtype=bool)   # cubic for this port
    solid[:, :, 0] = True; solid[:, :, -1] = True
    r = solve(solid, g=1e-6, tau_plus=1.2, max_steps=40000, verbose=False)
    h = float(Nz - 2)
    q_chan = r["q"] * Nz / h
    k_meas = r["nu"] * q_chan / 1e-6
    k_exact = h*h/12.0
    print(f"channel: k = {k_meas:.3f} vs exact {k_exact:.3f}  "
          f"err {100*(k_meas/k_exact-1):+.3f}%  ({r['steps']} steps, {r['seconds']}s)")
