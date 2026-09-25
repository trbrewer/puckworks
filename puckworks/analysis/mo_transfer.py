"""Conservative research-only Mo fixed-flow candidates; no registry integration.

Extensive equations and delayed-cell wetting are in the task CONTRACT.md.
Source dose/outlet/clock qualification is deliberately outside this numerical kernel.
"""
from dataclasses import dataclass
import numpy as np
from scipy.integrate import solve_ivp
from scipy.sparse import lil_matrix


@dataclass(frozen=True)
class Bed:
    dose_kg: float
    radius_m: float
    height_m: float
    porosity: float
    density_kg_m3: float
    collection_fraction: float

    def validate(self):
        a = np.array([self.dose_kg, self.radius_m, self.height_m,
                      self.porosity, self.density_kg_m3, self.collection_fraction])
        if not np.all(np.isfinite(a)) or np.any(a <= 0):
            raise ValueError('positive finite bed/observer constants required')
        if self.porosity >= 1 or self.collection_fraction > 1:
            raise ValueError('invalid porosity or collection fraction')


def populations(row):
    """Published volume weights and diameters in micrometres -> radii in metres."""
    weights = np.array([row['theta_f'], row['theta_c']], dtype=float)
    radii = np.array([row['2R_f_um'], row['2R_c_um']], dtype=float) * 0.5e-6
    if (not np.all(np.isfinite(weights)) or np.any(weights < 0)
            or not np.isclose(weights.sum(), 1, atol=1e-12, rtol=0)
            or not np.all(np.isfinite(radii)) or np.any(radii <= 0)):
        raise ValueError('invalid measured populations')
    keep = weights > 0
    return weights[keep], radii[keep]


def radial_geometry(nr):
    edges = np.linspace(0, 1, nr+1)
    return np.diff(edges**3), (edges[:-1]+edges[1:])/2, edges[1:-1]


def particle_derivative(mass, volumes, radii, liquid_c, scale, partition, candidate):
    """Mass rate per layer/population/shell and identical liquid gain.

    Inputs use one consistent arbitrary mass unit. No numerical concentration
    clipping: maximum is the source's one-way interface constitutive rule.
    """
    nr = mass.shape[-1]
    w, centers, faces = radial_geometry(nr)
    c = mass / (volumes[..., None]*w)
    dm = np.zeros_like(mass)
    if candidate == 'D2':
        conductance = 3*volumes*scale/radii[None, :]**2
        flux = conductance[..., None]*faces**2*nr*(c[..., :-1]-c[..., 1:])
        dm[..., :-1] -= flux
        dm[..., 1:] += flux
        out = conductance/(1-centers[-1])*np.maximum(c[..., -1]-liquid_c[:, None]/partition, 0)
    else:
        rate = scale if candidate == 'S0' else scale*(100e-6/radii)**2
        out = rate*volumes*np.maximum(c[..., 0]-liquid_c[:, None]/partition, 0)
    dm[..., -1] -= out
    return dm, out.sum(axis=1)


def simulate(candidate, bed, weights, radii, flow_m3_s, inventory, kinetic, partition,
             masses_kg, nz=24, nr=12, rtol=1e-7, atol=1e-10):
    """Solve dry-fill transport at exact cup-mass coordinates, including zero.

    inventory is a fraction of dry dose, kinetic is s^-1 (S0/S2) or m²/s (D2).
    Unit-inventory integration makes numerical tolerances inventory-relative;
    returned extensive masses and observers all share the same inventory scale.
    """
    bed.validate()
    target = np.asarray(masses_kg, dtype=float)
    weights, radii = np.asarray(weights, float), np.asarray(radii, float)
    if candidate not in ('S0', 'S2', 'D2'):
        raise ValueError('unknown candidate')
    if (target.ndim != 1 or not target.size or not np.all(np.isfinite(target))
            or np.any(target < 0) or np.any(np.diff(target) <= 0)):
        raise ValueError('target masses must be finite, nonnegative and strictly increasing')
    if (not np.all(np.isfinite([flow_m3_s, inventory, kinetic, partition, rtol, atol]))
            or flow_m3_s <= 0 or not 0 <= inventory <= 1 or kinetic < 0
            or partition <= 0 or nz < 1 or nr < 1 or rtol <= 0 or atol <= 0):
        raise ValueError('invalid simulation parameters')
    if (weights.ndim != 1 or radii.shape != weights.shape or np.any(weights < 0)
            or not np.all(np.isfinite(weights)) or not np.all(np.isfinite(radii))
            or np.any(radii <= 0) or not np.isclose(weights.sum(), 1, atol=1e-12, rtol=0)):
        raise ValueError('invalid populations')
    keep = weights > 0
    weights, radii = weights[keep], radii[keep]
    if candidate == 'S0':
        weights, radii = np.ones(1), np.array([100e-6])
    if candidate != 'D2':
        nr = 1
    npop = len(weights)
    vcell = np.pi*bed.radius_m**2*bed.height_m/nz
    water_cell = bed.porosity*vcell
    solid = np.broadcast_to((1-bed.porosity)*vcell*weights, (nz, npop)).copy()
    w, _, _ = radial_geometry(nr)
    ns = nz*npop*nr
    y = np.r_[(solid[..., None]*w/solid.sum()).ravel(), np.zeros(nz+1)]
    fill_dt = water_cell/flow_m3_s
    fill_time = nz*fill_dt
    times = fill_time+target/(bed.density_kg_m3*bed.collection_fraction*flow_m3_s)
    # Include pump-on, fill faces and all actual target coordinates in diagnostic output.
    samples = np.unique(np.r_[0, np.arange(1,nz+1)*fill_dt, times])
    outputs = np.empty((len(samples), len(y)))
    outputs[0] = y
    sparsity = lil_matrix((len(y), len(y)), dtype=int)
    for j in range(nz):
        li = ns+j
        sparsity[li, li] = 1
        if j:
            sparsity[li, li-1] = 1
        for p in range(npop):
            ids = np.arange((j*npop+p)*nr, (j*npop+p+1)*nr)
            for a, idx in enumerate(ids):
                sparsity[idx, ids[max(0,a-1):min(nr,a+2)]] = 1
            sparsity[ids[-1], li] = 1
            sparsity[li, ids[-1]] = 1
    sparsity[-1, ns+nz-1] = 1
    min_state = float(y.min())
    max_balance = 0.0
    min_delivery_increment = 0.0
    solver_calls = nfev = njev = nlu = 0
    boundaries = list(np.arange(nz+1)*fill_dt)
    if times[-1] > fill_time:
        boundaries.append(float(times[-1]))
    for phase, (t0, t1) in enumerate(zip(boundaries[:-1], boundaries[1:])):
        active = min(phase, nz)

        def rhs(t, state):
            ds = np.zeros((nz, npop, nr))
            liquid = state[ns:ns+nz]
            adv = np.zeros(nz)
            gain = np.zeros(nz)
            if active:
                c = liquid[:active]/water_cell
                ds[:active], gain[:active] = particle_derivative(
                    state[:ns].reshape(nz,npop,nr)[:active], solid[:active],
                    radii, c, kinetic, partition, candidate)
                adv[:active] = flow_m3_s*c
            dl = gain-adv
            dl[1:] += adv[:-1]
            return np.r_[ds.ravel(), dl, adv[-1]]

        result = solve_ivp(rhs, (t0, t1), y, method='BDF', dense_output=True,
                           rtol=rtol, atol=atol, jac_sparsity=sparsity.tocsr())
        solver_calls += 1
        nfev += result.nfev
        njev += result.njev
        nlu += result.nlu
        if not result.success:
            raise RuntimeError(f'numerical solve failed: {result.message}')
        min_state = min(min_state, float(result.y.min()))
        max_balance = max(max_balance, float(abs(result.y.sum(axis=0)-1).max()))
        min_delivery_increment = min(min_delivery_increment, float(np.diff(result.y[-1]).min()))
        mask = (samples > t0) & (samples <= t1)
        outputs[mask] = result.sol(samples[mask]).T
        y = result.y[:, -1]
    # A scaled tolerance is reported, never used to alter the states.
    positivity_tolerance = 50*atol
    if min_state < -positivity_tolerance or min_delivery_increment < -positivity_tolerance:
        raise RuntimeError('negative mass or delivered-solute regression')
    if max_balance > 1e-6:
        raise RuntimeError('solute balance failure')
    initial = inventory*bed.dose_kg
    output_mass = outputs*initial
    cup_volume = flow_m3_s*np.maximum(samples-fill_time,0)
    admitted = flow_m3_s*samples
    stored = np.minimum(admitted, nz*water_cell)
    water_residual = float(np.max(abs(stored+cup_volume-admitted))/max(admitted[-1],1e-300))
    idx = np.searchsorted(samples, times)
    delivered = output_mass[idx,-1]*bed.collection_fraction
    strength = np.full_like(target, np.nan)
    np.divide(100*delivered, target, out=strength, where=target>0)
    return dict(masses_kg=target, ey_pct=100*delivered/(bed.dose_kg*bed.collection_fraction),
                strength_pct=strength, particle_kg=output_mass[idx,:ns].sum(axis=1),
                liquid_solute_kg=output_mass[idx,ns:ns+nz].sum(axis=1),
                delivered_whole_kg=output_mass[idx,-1],
                trajectory_time_s=samples, trajectory_delivered_kg=output_mass[:,-1],
                trajectory_cup_m3=cup_volume, fill_time_s=fill_time,
                solute_balance_relative=max_balance, water_balance_relative=water_residual,
                min_state_inventory_fraction=min_state,
                positivity_tolerance_inventory_fraction=positivity_tolerance,
                solver_calls=solver_calls, nfev=nfev, njev=njev, nlu=nlu)


def interpolate_supported(x, y, target):
    x, y, target = np.asarray(x), np.asarray(y), np.asarray(target)
    if (x.ndim != 1 or len(x)<2 or y.shape != x.shape or np.any(np.diff(x)<=0)
            or not all(np.all(np.isfinite(a)) for a in (x,y,target))
            or np.any(target < x[0]) or np.any(target > x[-1])):
        raise ValueError('unsupported interpolation')
    return np.interp(target, x, y)
