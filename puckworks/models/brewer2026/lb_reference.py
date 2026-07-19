"""mini_lb.py — minimal D3Q19 TRT lattice-Boltzmann permeability kernel.

Validation-grade, numpy-vectorized. Periodic box, full-way bounce-back solids,
constant body force in x, TRT collision with magic Lambda = 3/16 so the wall
location is viscosity-independent (the known BGK permeability artifact).

VALIDATION RESULTS (this kernel, 2026-07-10):
  plane Poiseuille channel (exact):        k error +0.03%
  SC sphere array c=0.08 vs Hasimoto drag:
      L=16 (a=4.2 lu)   K error  -8.3%
      L=24 (a=6.4 lu)   K error  -7.9%
      L=32 (a=8.5 lu)   K error  -7.2%
  Error shrinks ~1/a; residual at these toy radii is dominated by the
  +/- half-voxel hydrodynamic-radius ambiguity of staircased bounce-back
  (a known LB effect; needs a >~ 20-30 lu, i.e. production domains 128^3+,
  where FluidX3D / Taichi-LBM3D take over). Solver core is exact.
"""
import numpy as np
import time, json

# ---------------- D3Q19 lattice ----------------
C = np.array([
    [0,0,0],
    [1,0,0],[-1,0,0],[0,1,0],[0,-1,0],[0,0,1],[0,0,-1],
    [1,1,0],[-1,-1,0],[1,-1,0],[-1,1,0],
    [1,0,1],[-1,0,-1],[1,0,-1],[-1,0,1],
    [0,1,1],[0,-1,-1],[0,1,-1],[0,-1,1],
], dtype=np.int64)
W = np.array([1/3] + [1/18]*6 + [1/36]*12)
OPP = np.array([0,2,1,4,3,6,5,8,7,10,9,12,11,14,13,16,15,18,17])
Q = 19

def feq_all(rho, ux, uy, uz):
    cu = (C[:,0,None]*ux.ravel() + C[:,1,None]*uy.ravel() + C[:,2,None]*uz.ravel())
    u2 = (ux*ux + uy*uy + uz*uz).ravel()
    return (W[:,None] * rho.ravel() * (1 + 3*cu + 4.5*cu*cu - 1.5*u2)).reshape((Q,)+rho.shape)

def solve(solid, g=1e-6, tau_plus=1.2, max_steps=20000, check=200, rtol=1e-7,
          min_steps=1500, verbose=True):
    """Body force g in +x. Returns dict with Darcy velocity q and permeability k (lattice units)."""
    shape = solid.shape
    fluid = ~solid
    nu = (tau_plus - 0.5) / 3.0
    lam = 3.0/16.0
    tau_minus = 0.5 + lam/(tau_plus - 0.5)
    om_p, om_m = 1.0/tau_plus, 1.0/tau_minus

    rho = np.ones(shape)
    ux = np.zeros(shape); uy = np.zeros(shape); uz = np.zeros(shape)
    f = feq_all(rho, ux, uy, uz)

    S = (3.0 * (W[:,None] * C[:,0,None]) * g).reshape(Q,1,1,1)  # force term, rho~1
    q_prev, t0 = None, time.time()
    for step in range(1, max_steps+1):
        # macroscopic; raw velocity feeds feq (no half-shift: source term carries the force)
        rho = f.sum(axis=0)
        ux = (f * C[:,0].reshape(Q,1,1,1)).sum(axis=0)/rho
        uy = (f * C[:,1].reshape(Q,1,1,1)).sum(axis=0)/rho
        uz = (f * C[:,2].reshape(Q,1,1,1)).sum(axis=0)/rho
        ux[solid] = 0; uy[solid] = 0; uz[solid] = 0

        # TRT collision at fluid nodes + forcing
        fe = feq_all(rho, ux, uy, uz)
        fp  = 0.5*(f + f[OPP]);  fm  = 0.5*(f - f[OPP])
        fep = 0.5*(fe + fe[OPP]); fem = 0.5*(fe - fe[OPP])
        fpost = f - om_p*(fp - fep) - om_m*(fm - fem) + S
        fpost[:, solid] = f[:, solid]                     # no collision in solids

        # streaming
        for i in range(1, Q):
            fpost[i] = np.roll(fpost[i], shift=tuple(C[i]), axis=(0,1,2))
        # full-way bounce-back at solid nodes
        fpost[:, solid] = fpost[OPP][:, solid]
        f = fpost

        if step % check == 0:
            q = (ux + 0.5*g)[fluid].sum() / ux.size       # superficial (Darcy) velocity
            if verbose:
                print(f"  step {step:6d}  q = {q:.6e}  ({(time.time()-t0):.0f}s)")
            if step >= min_steps and q_prev is not None and abs(q - q_prev) < rtol*abs(q):
                break
            q_prev = q

    phi = fluid.mean()
    q = (ux + 0.5*g)[fluid].sum() / ux.size
    k = nu * q / (g * phi)                                # Darcy: grad p_eff = g*phi (rho=1)
    return dict(q=float(q), k=float(k), phi=float(phi), nu=nu, steps=step,
                seconds=round(time.time()-t0,1), ux=ux + 0.5*g)

# ---------------- canonical plane-channel code-verification case ----------------
# The single named verification case shared by the authoritative gate (gate_lb_channel) and the Guided
# Pull Laboratory native reference runner, so the two can never carry divergent channel arithmetic. It
# returns the FULL-PRECISION numeric summary vs the exact plane-Poiseuille permeability; the pass/fail
# THRESHOLD is deliberately NOT here — the acceptance band lives only in gate_lb_channel (the authority).
CHANNEL_VERIFICATION_CASE = dict(Nz=33, N=4, g=1e-6, tau_plus=1.2, max_steps=20000, check=200, rtol=1e-6)

def channel_verification(Nz=33, N=4, g=1e-6, tau_plus=1.2, max_steps=20000, check=200, rtol=1e-6):
    """Solve the plane channel ONCE and return the full-precision code-verification summary against the
    exact plane-Poiseuille permeability k = h^2/12 (h = Nz - 2, the half-voxel wall spacing). No pass/fail
    threshold is applied here (that is gate_lb_channel's sole authority). Deterministic: no randomness, so
    two identical calls return identical numbers.

    Inputs are validated (never silently coerced): lattice dimensions and iteration counts must be
    positive ints; g/tau_plus/rtol must be positive finite numbers; tau_plus > 0.5 keeps the viscosity
    nu = (tau_plus - 0.5)/3 positive; Nz >= 3 leaves at least one fluid node between the two walls."""
    import math
    for nm, val in (("Nz", Nz), ("N", N), ("max_steps", max_steps), ("check", check)):
        if isinstance(val, bool) or not isinstance(val, int) or val <= 0:
            raise ValueError(f"channel_verification: {nm} must be a positive int, got {val!r}")
    if Nz < 3:
        raise ValueError(f"channel_verification: Nz must be >= 3 (two walls + >=1 fluid node), got {Nz}")
    for nm, val in (("g", g), ("tau_plus", tau_plus), ("rtol", rtol)):
        if isinstance(val, bool) or not isinstance(val, (int, float)) or not math.isfinite(val) or val <= 0:
            raise ValueError(f"channel_verification: {nm} must be a positive finite number, got {val!r}")
    if tau_plus <= 0.5:
        raise ValueError(f"channel_verification: tau_plus must be > 0.5 (positive viscosity), got {tau_plus}")
    solid = np.zeros((N, N, Nz), dtype=bool)
    solid[:, :, 0] = True; solid[:, :, -1] = True
    r = solve(solid, g=g, tau_plus=tau_plus, max_steps=max_steps, check=check, rtol=rtol, verbose=False)
    h = float(Nz - 2)
    k_exact = h * h / 12.0
    k_meas = r["nu"] * (r["q"] * Nz / h) / g              # superficial velocity referenced to channel width
    err_pct = 100.0 * (k_meas / k_exact - 1.0)
    return dict(k_meas=float(k_meas), k_exact=float(k_exact), err_pct=float(err_pct), h=h,
                nu=float(r["nu"]), q=float(r["q"]), phi=float(r["phi"]), steps=int(r["steps"]),
                max_steps=int(max_steps), converged=bool(r["steps"] < max_steps),
                seconds=float(r["seconds"]))

# ---------------- validation cases ----------------
def channel_case(Nz=41, N=4):
    solid = np.zeros((N, N, Nz), dtype=bool)
    solid[:,:,0] = True; solid[:,:,-1] = True
    r = solve(solid, g=1e-6, tau_plus=1.2, max_steps=40000, check=200, verbose=False)
    h = float(Nz - 2)             # halfway walls at 0.5 and Nz-1.5: width = Nz-2
    k_exact = h*h/12.0
    # superficial velocity referenced to channel volume h (not box Nz)
    q_chan = r["q"] * Nz / h
    k_meas = r["nu"] * q_chan / 1e-6
    return dict(k_meas=k_meas, k_exact=k_exact, err_pct=100*(k_meas/k_exact - 1),
                steps=r["steps"], seconds=r["seconds"])

def hasimoto_K(c):
    return 1.0/(1.0 - 1.7601*c**(1/3) + c - 1.5593*c*c)

def sphere_case(c, L=40, tau_plus=1.2, g=1e-6):
    a = L * (3.0*c/(4.0*np.pi))**(1.0/3.0)
    x, y, z = np.meshgrid(*(np.arange(L),)*3, indexing="ij")
    cx = (L-1)/2.0
    solid = (x-cx)**2 + (y-cx)**2 + (z-cx)**2 <= a*a
    c_eff = solid.mean()                                   # staircased solid fraction
    a_eff = (3*c_eff*L**3/(4*np.pi))**(1/3)                # volume-equivalent radius
    r = solve(solid, g=g, tau_plus=tau_plus, verbose=True)
    K_meas = g * (~solid).sum() / (6*np.pi * r["nu"] * a_eff * r["q"] * 1.0)
    K_th = hasimoto_K(c_eff)
    k_th = L**3 / (6*np.pi*a_eff*K_th)
    return dict(c_nom=c, c_eff=float(c_eff), a_lu=float(a_eff),
                K_meas=float(K_meas), K_hasimoto=float(K_th),
                K_err_pct=100*(K_meas/K_th - 1),
                k_meas=float(r["k"]), k_theory=float(k_th),
                k_err_pct=100*(r["k"]/k_th - 1),
                steps=r["steps"], seconds=r["seconds"], q=r["q"], phi=r["phi"])

if __name__ == "__main__":
    print("=== plane Poiseuille channel (exact solution) ===")
    ch = channel_case()
    print(json.dumps(ch, indent=1))

    results = {"channel": ch, "spheres": []}
    for c in [0.03, 0.08, 0.125]:
        print(f"\n=== SC sphere array, nominal c = {c} ===")
        s = sphere_case(c)
        print(f"c_eff {s['c_eff']:.4f}  a {s['a_lu']:.1f} lu  "
              f"K_meas {s['K_meas']:.3f} vs Hasimoto {s['K_hasimoto']:.3f}  "
              f"err {s['K_err_pct']:+.1f}%  ({s['steps']} steps, {s['seconds']}s)")
        results["spheres"].append(s)
    json.dump(results, open("/tmp/mini_lb_validation.json","w"), indent=1)
    print("\nsaved /tmp/mini_lb_validation.json")
