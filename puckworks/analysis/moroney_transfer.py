"""Analysis-only conservative Moroney-2015 cylindrical reduction.

Research solver, not a registered component. See the task protocol for source,
initialization and volume conventions. States are solute masses (kg), not LDF
2019 concentrations. Kernel dissolution is complete at post-fill t=0.
"""
from dataclasses import dataclass, asdict
import numpy as np
from scipy.integrate import solve_ivp
from scipy.optimize import brentq
from scipy.sparse import lil_matrix

RHO = 965.3
CS = 1400.0
CSAT = 212.4
PHI_DRY = .56
Y_MAX = .143435 / (1 - PHI_DRY)
Q = 250e-6 / 60
AREA = np.pi * (.059 / 2)**2


@dataclass(frozen=True)
class Condition:
    dose_g: float
    length_m: float
    dp_pa: float
    flow_m3_s: float = Q
    rho_kg_m3: float = RHO
    moisture: float = .04

    def __post_init__(self):
        if (not np.isfinite(list(asdict(self).values())).all() or min(self.dose_g,self.length_m,self.rho_kg_m3)<=0
                or self.dp_pa<0 or self.flow_m3_s<0 or not 0<=self.moisture<1):
            raise ValueError('inadmissible condition')

    @property
    def dry_g(self):
        return self.dose_g * (1 - self.moisture)

    @property
    def mass_flow_g_s(self):
        return 1000 * self.rho_kg_m3 * self.flow_m3_s


DEEP = Condition(60, .0405, 230000)
SHALLOW = Condition(12.5, .0112, 50000)


def volumes(c=DEEP, basis='dose'):
    """Two explicit conditional reconciliations; neither porosity is measured.

    dose: measured dry-in-air porosity fixes grain volume; geometry fixes mobile
    volume. hydraulic: invert source KC closure, then dose fixes effective dry
    intragranular void fraction. Total solute is always Y_MAX * reported dry dose.
    """
    bed = AREA * c.length_m
    if basis == 'dose':
        grain = c.dry_g / 1000 / CS / (1 - PHI_DRY)
        eps = 1 - grain / bed
    elif basis == 'hydraulic':
        def f(e):
            k = (27.35e-6)**2 * e**3 / (36 * 3.1 * (1-e)**2)
            return k * (c.dp_pa / c.length_m + c.rho_kg_m3 * 9.81) / .315e-3 - c.flow_m3_s / AREA
        eps = brentq(f, .01, .95)
        grain = (1-eps)*bed
    else:
        raise ValueError('unknown volume basis')
    dry_void = 1 - c.dry_g / 1000 / CS / grain
    fc = Y_MAX * c.dry_g / 1000 / CS / grain
    if not (0 < eps < 1 and 0 < dry_void < dry_void + fc < 1):
        raise ValueError('inadmissible volume bookkeeping')
    return dict(bed_m3=bed, grain_m3=grain, mobile_m3=eps*bed,
                phi_h=eps, phi_dry=dry_void, phi_c=fc)


def observation(mass_g, exit_kg_m3, delivered_kg, rho=RHO):
    m = np.asarray(mass_g)
    s_g = 1000*np.asarray(delivered_kg)
    pot = np.divide(1000*s_g, m, out=np.full_like(m, np.nan, dtype=float), where=m>0)
    return dict(mass_g=m, exit_mg_g=1000*np.asarray(exit_kg_m3)/rho,
                delivered_g=s_g, pot_mg_g=pot)


def pot_delivery(mass_g, pot_mg_g):
    return np.asarray(mass_g)*np.asarray(pot_mg_g)/1000


def initial_state(c, n, split, amplitude, profile, basis):
    if n < 1 or not 0 < split <= 1 or not 0 <= amplitude <= 1:
        raise ValueError('invalid initialization parameter')
    v = volumes(c, basis)
    g, h = v['grain_m3']/n, v['mobile_m3']/n
    inventory = Y_MAX*c.dry_g/1000/n
    x = (np.arange(n)+.5)/n  # inlet -> outlet, reverse of paper z
    if profile == 'uniform':
        shape = np.ones(n)
    elif profile == 'linear':
        shape = x
    else:
        raise ValueError('unknown profile')
    mobile = amplitude*CSAT*shape*h
    kernel = np.full(n, (1-split)*inventory)
    surface = split*inventory-mobile
    phi = v['phi_dry']+(inventory-surface)/(CS*g)
    if np.any(surface < 0) or np.any(kernel/(g*phi) > CSAT) or np.any(phi >= 1):
        raise ValueError('initial inventory or saturation violated; no clipping')
    return np.r_[mobile, kernel, surface, 0.], v


def system(c, n, alpha, beta, split, amplitude, profile, basis, published_control=False):
    if min(alpha, beta) < 0 or not np.isfinite([alpha, beta]).all():
        raise ValueError('invalid transfer multipliers')
    y0, v = initial_state(c,n,split,amplitude,profile,basis)
    g, h = v['grain_m3']/n, v['mobile_m3']/n
    inventory = Y_MAX*c.dry_g/1000/n
    surface0 = split*inventory
    if published_control:
        if c != DEEP or profile != 'uniform' or amplitude != 1:
            raise ValueError('published control is only Table2 JK deep uniform csat')
        bed=AREA*c.length_m; g=.8*bed/n; h=.2*bed/n
        mh=np.full(n,CSAT*h); mv=np.full(n,.6231*78.88*g)
        surface0=.11*CS*g; ms=np.full(n,surface0)-mh
        inventory=float(mh[0]+mv[0]+ms[0])
        v=dict(bed_m3=bed,grain_m3=n*g,mobile_m3=n*h,phi_h=.2,
               phi_dry=.6231-(inventory-ms[0])/(CS*g),phi_c=.143435)
        y0=np.r_[mh,mv,ms,0.]
    def rhs(_t,y):
        mh, mv, ms = y[:n], y[n:2*n], y[2*n:3*n]
        phi = v['phi_dry']+(inventory-ms)/(CS*g)
        ch, cv = mh/h, mv/(phi*g)
        exchange = g*alpha*phi**(4/3)*2.2e-9*6/(322.49e-6*282e-6)*(cv-ch)
        surface = g*beta*12*2.2e-9*v['phi_c']/(27.35e-6*30e-6)*(CSAT-ch)*ms/surface0
        adv = c.flow_m3_s*(np.r_[0.,ch[:-1]]-ch)
        return np.r_[adv+exchange+surface, -exchange, -surface, c.flow_m3_s*ch[-1]]
    sparsity = lil_matrix((3*n+1,3*n+1),dtype=int)
    for i in range(n):
        for row in (i,n+i,2*n+i):
            sparsity[row,[i,n+i,2*n+i]]=1
        if i: sparsity[i,i-1]=1
    sparsity[-1,n-1]=1
    return y0, rhs, sparsity.tocsr(), v


def solve(c=DEEP, mass_g=None, *, n=160, alpha=.1833, beta=.0447,
          split=.11/.143435, amplitude=.9, profile='uniform', basis='dose',
          rtol=1e-7, atol=1e-12, published_control=False):
    if mass_g is None: mass_g=np.linspace(0,1000,501)
    mass_g=np.asarray(mass_g,dtype=float)
    if c.flow_m3_s <= 0 or np.any(~np.isfinite(mass_g)) or np.any(mass_g < 0):
        raise ValueError('flow must be positive and mass finite/nonnegative')
    if mass_g.ndim != 1 or len(mass_g)<2 or np.any(np.diff(mass_g)<=0):
        raise ValueError('strictly increasing mass support required')
    y0,rhs,sparsity,v=system(c,n,alpha,beta,split,amplitude,profile,basis,published_control)
    sol=solve_ivp(rhs,(0,mass_g[-1]/c.mass_flow_g_s),y0,method='BDF',
                  t_eval=mass_g/c.mass_flow_g_s,rtol=rtol,atol=atol,jac_sparsity=sparsity)
    if not sol.success: raise RuntimeError(sol.message)
    inventory=float(y0.sum())
    residual=np.max(abs(sol.y.sum(axis=0)-inventory))/inventory
    mh,mv,ms=sol.y[:n],sol.y[n:2*n],sol.y[2*n:3*n]
    phi=v['phi_dry']+(inventory/n-ms)/(CS*v['grain_m3']/n)
    ch=mh/(v['mobile_m3']/n)
    cv=mv/(phi*v['grain_m3']/n)
    # Numerical roundoff is reported, never clipped. Larger violations reject.
    min_mass=float(sol.y.min())
    if min_mass < -10*atol or np.max(ch)>CSAT+1e-4 or np.max(cv)>CSAT+1e-4:
        raise RuntimeError('inadmissible numerical state')
    if residual>1e-6: raise RuntimeError('solute balance failed')
    out=observation(mass_g,ch[-1],sol.y[-1],c.rho_kg_m3)
    out.update(retained_mobile_g=1000*mh.sum(axis=0),retained_internal_g=1000*mv.sum(axis=0),
               remaining_surface_g=1000*ms.sum(axis=0),remaining_kernel_solid_g=np.zeros(len(mass_g)),
               losses_g=np.zeros(len(mass_g)),initial_inventory_g=inventory*1000,
               balance_relative=float(residual),minimum_mass_kg=min_mass,
               nfev=sol.nfev,njev=sol.njev,nlu=sol.nlu,volumes=v,condition=asdict(c))
    return out


def empirical(mass_g, params, c=DEEP, scaling='N_M'):
    """One finite cumulative model: analytic derivative and pot observer."""
    y,a,b1,b2=params
    if not (0<=y<=Y_MAX and 0<=a<=1 and 0<b1<=b2):
        raise ValueError('inadmissible empirical parameters')
    if scaling=='N_M': factor=c.dry_g/DEEP.dry_g
    elif scaling=='N_T': factor=c.mass_flow_g_s/DEEP.mass_flow_g_s
    else: raise ValueError('unknown transfer hypothesis')
    b1,b2=b1*factor,b2*factor
    m=np.asarray(mass_g)
    s=c.dry_g*y*(-a*np.expm1(-m/b1)-(1-a)*np.expm1(-m/b2))
    ds=c.dry_g*y*(a*np.exp(-m/b1)/b1+(1-a)*np.exp(-m/b2)/b2)
    return observation(m,ds*c.rho_kg_m3,s/1000,c.rho_kg_m3)


def mass_weights(m):
    m=np.asarray(m)
    if len(m)<2 or np.any(np.diff(m)<=0): raise ValueError('invalid support')
    w=np.r_[np.diff(m)[0]/2,(m[2:]-m[:-2])/2,np.diff(m)[-1]/2]
    return w/w.sum()


def metrics(pred, exit_mass, exit_obs, pot_mass, pot_obs, dry_g):
    for coordinates in (exit_mass,pot_mass):
        if min(coordinates)<pred['mass_g'][0] or max(coordinates)>pred['mass_g'][-1]:
            raise ValueError('observation outside frozen prediction support')
    e=np.interp(exit_mass,pred['mass_g'],pred['exit_mg_g'])-exit_obs
    d=(np.interp(pot_mass,pred['mass_g'],pred['delivered_g'])-pot_delivery(pot_mass,pot_obs))/dry_g*100
    return dict(outlet_rmse_mg_g=float(np.sqrt(np.sum(mass_weights(exit_mass)*e**2))),
                cumulative_max_ey_pp=float(np.max(abs(d))),endpoint_ey_pp=float(d[-1]))
