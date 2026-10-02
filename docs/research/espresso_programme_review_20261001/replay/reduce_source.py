"""Independent dimensional accounting of exported AUTHOR states; no solver or fit."""
import argparse
import csv
import json
import re
from pathlib import Path

import numpy as np
from scipy.integrate import simpson
from scipy.io import loadmat


def physical_parameters(path):
    text = Path(path).read_text()
    names = ('R0','L','a1','a2','rhoout','rhogrounds','csat','cs0','phis',
             'Mout','Ds_star','Deff_star','k','tshot','f1')
    out = {}
    for name in names:
        values = re.findall(r'^'+name+r'\s*=\s*([0-9.eE+-]+)\s*;',text,re.M)
        if len(values)!=1:
            raise ValueError('not one literal source parameter: '+name)
        out[name]=float(values[0])
    return out


def moments(state, n):
    z=np.linspace(0,1,n)
    edges=np.r_[0,(z[:-1]+z[1:])/2,1]
    weights=np.diff(edges**3)
    a=np.asarray(state)
    if a.shape!=(n+2*n*n,): raise ValueError('wrong source state size')
    fine=a[n:n+n*n].reshape(n,n) # rows are axial sites, columns radial cells
    coarse=a[n+n*n:].reshape(n,n)
    return np.array([np.trapezoid(a[:n],z),
                     np.trapezoid(fine@weights,z),np.trapezoid(coarse@weights,z)])


def prefix(t,y,end):
    t=np.asarray(t);y=np.asarray(y)
    if len(t)<3 or np.any(np.diff(t)<=0) or end<t[0] or end>t[-1]:
        raise ValueError('invalid or incomplete time support')
    k=np.searchsorted(t,end)
    if k<len(t) and t[k]==end: return t[:k+1],y[:k+1]
    return np.r_[t[:k],end],np.r_[y[:k],np.interp(end,t,y)]


def integral(t,y,end,method='trap'):
    tx,v=prefix(t,y,end)
    if method=='coarse':
        ii=np.unique(np.r_[np.arange(0,len(tx),2),len(tx)-1])
        return float(np.trapezoid(v[ii],tx[ii]))
    if method=='simpson': return float(simpson(v,x=tx))
    return float(np.trapezoid(v,tx))


def reduce(case):
    case=Path(case)
    h=np.loadtxt(case/'history.csv',delimiter=',')
    if h.ndim!=2 or h.shape[1]!=12 or not np.isfinite(h).all():
        raise ValueError('invalid history')
    t=h[:,0]
    if t[0]!=0 or t[-1]!=10 or np.any(np.diff(t)<=0):
        raise ValueError('released horizon incomplete')
    s=loadmat(case/'snapshots.mat',simplify_cells=True)
    n=int(s['N']); dp=np.asarray(s['dimensionlessparameters']).ravel()
    p=physical_parameters(case/'define_parameters.m')
    V=np.pi*p['R0']**2*p['L']
    phi1=p['phis']*p['f1'];phi2=p['phis']*(1-p['f1'])
    b1=3*phi1/p['a1'];b2=3*phi2/p['a2'];b0=(b1+b2)/2
    expected=np.array([b1/b0,b2/b0,p['Ds_star']*p['tshot']/p['a1']**2,
      p['Ds_star']*p['tshot']/p['a2']**2,1/p['a1']/b0,1/p['a2']/b0,
      p['csat']/p['cs0'],p['Mout']/p['rhoout']/V,
      p['Deff_star']*p['tshot']/p['L']**2,p['k']*p['cs0']**2*p['tshot']*b0,
      p['cs0']/p['rhogrounds'],p['phis']])
    np.testing.assert_allclose(dp,expected,rtol=2e-13,atol=1e-14)
    for i,state in zip(np.atleast_1d(s['snapshot_indices']).astype(int),np.atleast_2d(s['snapshot_u'])):
        np.testing.assert_allclose(moments(state,n),h[i-1,1:4],rtol=2e-12,atol=2e-13)
    beta,q,alpha=dp[6],dp[7],dp[10]
    # kg-to-g is 1000; no assumed actual dry dose or separate solvent mass.
    factor=V*p['csat']*1000
    fine_initial=V*p['cs0']*phi1*h[0,2]*1000
    coarse_initial=V*p['cs0']*phi2*h[0,3]*1000
    liq_initial=factor*(1-p['phis'])*h[0,1]
    initial=fine_initial+coarse_initial+liq_initial
    rows=[]
    for end in [1.,10.]:
        state=np.array([np.interp(end,t,h[:,j]) for j in range(1,4)])
        fine=V*p['cs0']*phi1*state[1]*1000
        coarse=V*p['cs0']*phi2*state[2]*1000
        liquid=factor*(1-p['phis'])*state[0]
        cup=factor*q*integral(t,h[:,4],end)
        influx=factor*integral(t,h[:,5],end)
        outlet_disp=factor*integral(t,h[:,6],end)
        release1=factor*dp[0]*integral(t,h[:,7],end)
        release2=factor*dp[1]*integral(t,h[:,8],end)
        k=int(np.searchsorted(t,end))
        bracket=0. if t[k]==end else float(t[k]-t[k-1])
        r=dict(t_hat=end,seconds=end*p['tshot'],reference_density_liquid_throughput_g=end*q*V*p['rhoout']*1000,
          initial_solid_g=fine_initial+coarse_initial,final_fine_solute_g=fine,
          final_coarse_solute_g=coarse,final_solid_g=fine+coarse,
          liquid_solute_holdup_g=liquid,cup_advective_solute_g=cup,
          signed_inlet_solute_g=influx,signed_outlet_dispersive_solute_g=outlet_disp,
          conservation_residual_g=initial-fine-coarse-liquid-cup-outlet_disp+influx,
          fine_release_residual_g=fine_initial-fine-release1,
          coarse_release_residual_g=coarse_initial-coarse-release2,
          liquid_balance_residual_g=liquid-liq_initial-release1-release2-influx+cup+outlet_disp,
          author_EY_percent=100*alpha*q*beta*integral(t,h[:,4],end)/p['phis'],
          actual_dry_dose_g=None,physical_EY_percent=None,water_mass_g=None,beverage_mass_g=None,
          conditional_author_denominator_g=V*p['rhogrounds']*p['phis']*1000,
          conditional_main_eq25_dose_g=V*p['rhogrounds']/p['phis']*1000,
          conditional_bulk_density_dose_g=V*p['rhogrounds']*1000,
          endpoint_bracket_width_t_hat=bracket,
          cup_simpson_minus_trap_g=factor*q*(integral(t,h[:,4],end,'simpson')-integral(t,h[:,4],end)),
          cup_coarse_minus_trap_g=factor*q*(integral(t,h[:,4],end,'coarse')-integral(t,h[:,4],end)))
        for label in ['author_denominator','main_eq25_dose','bulk_density_dose']:
            r['conditional_EY_'+label+'_percent']=100*cup/r['conditional_'+label+'_g']
        rows.append(r)
    np.testing.assert_allclose(rows[-1]['author_EY_percent'],float(s['author_reported_EY']),rtol=2e-12,atol=2e-12)
    out=dict(source_commit='79ebefb72446eb706084e2392cab64bf0fad93a2',n=n,output_rows=len(t),
      backend=str(s['backend_version']),source_solver_seconds=float(s['comp_time']),
      physical_parameters=p,minimum_scaled_state=float(h[:,9].min()),maximum_scaled_state=float(h[:,10].max()),
      initial_algebraic_residual=float(s['initial_algebraic_residual']),endpoints=rows,
      interpretation='Source reproduction only. Conditional doses are distinct identities, not actual dry-dose measurements. Quadrature differences are diagnostics, not assay uncertainty or certified error bounds.')
    with (case/'endpoints.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=rows[0]);w.writeheader();w.writerows(rows)
    (case/'reduction.json').write_text(json.dumps(out,indent=2,allow_nan=False)+'\n')
    return out


if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('case',type=Path)
    a=ap.parse_args();print(json.dumps(reduce(a.case),indent=2))
