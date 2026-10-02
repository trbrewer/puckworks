"""Independent balance reduction of retained moments and measured state traces.
No solver, fitted parameters or residual-defined predictions.
"""
from pathlib import Path
import csv,json,re
import numpy as np
from scipy.integrate import simpson,cumulative_trapezoid
from scipy.io import loadmat,whosmat
ROOT=Path(__file__).resolve().parent
OLD=ROOT.parent/'sparse-execution-20261001T133411Z'

def parameters():
 text=(ROOT/'source/define_parameters.m').read_text()
 names=['R0','L','cs0','csat','phis','f1','a1','a2','tshot','rhoout','Mout','Ds_star','Deff_star','k']
 p={k:float(re.search(r'^'+k+r'\s*=\s*([0-9.eE+-]+);',text,re.M)[1]) for k in names}
 p['V']=np.pi*p['R0']**2*p['L'];p['eps']=1-p['phis'];p['beta']=p['csat']/p['cs0']
 p['factor_mg']=p['V']*p['csat']*1e6
 b1=3*p['phis']*p['f1']/p['a1'];b2=3*p['phis']*(1-p['f1'])/p['a2'];b0=(b1+b2)/2
 p.update(b1=b1/b0,b2=b2/b0,K=p['k']*p['cs0']**2*p['tshot']*b0,q=p['Mout']/(p['rhoout']*p['V']),D=p['Deff_star']*p['tshot']/p['L']**2)
 return p
P=parameters()

def endpoint(t,y,T):
 k=int(np.searchsorted(t,T));assert 0<=k<len(t)
 if t[k]==T:return y[k]
 a=(T-t[k-1])/(t[k]-t[k-1]);return (1-a)*y[k-1]+a*y[k]

def cut(t,y,T):
 k=int(np.searchsorted(t,T))
 if t[k]==T:return t[:k+1],y[:k+1]
 return np.append(t[:k],T),np.concatenate([y[:k],np.atleast_1d(endpoint(t,y,T))])

def integrate(t,y,T,method='trap'):
 x,z=cut(t,y,T)
 if len(x)==1:return 0.
 if method=='coarse':
  ix=np.unique(np.append(np.arange(0,len(x),2),len(x)-1));x=x[ix];z=z[ix]
 if method=='simpson':return float(simpson(z,x=x))
 return float(np.sum(np.diff(x)*(z[1:]+z[:-1])/2))

def inventories(H):
 f=P['factor_mg'];return np.column_stack([f*P['phis']*P['f1']/P['beta']*H[:,2],f*P['phis']*(1-P['f1'])/P['beta']*H[:,3],f*P['eps']*H[:,1]])

def observe(H,T,method='trap'):
 t=H[:,0];m=inventories(H);initial=float(m[0].sum());end=endpoint(t,m,T)
 adv=P['factor_mg']*P['q']*integrate(t,H[:,4],T,method)
 inletadv=P['factor_mg']*P['q']*integrate(t,H[:,11],T,method)
 inlet=P['factor_mg']*integrate(t,H[:,5],T,method)
 outlet=P['factor_mg']*integrate(t,H[:,6],T,method)
 core=initial-end.sum()-adv
 return dict(t_hat=T,t_seconds=T*P['tshot'],initial_mg=initial,fine_mg=float(end[0]),coarse_mg=float(end[1]),liquid_mg=float(end[2]),cup_mg=adv,inlet_advection_mg=inletadv,inlet_dispersion_mg=inlet-inletadv,inlet_total_mg=inlet,outlet_dispersion_mg=outlet,author_core_E_mg=float(core),observed_E_mg=float(core-outlet+inlet),author_vs_boundary_corrected_mg=float(inlet-outlet))

def rates(B,N):
 # Raw boundary liquid and surface concentrations, NOT output residual derivatives.
 t,c1,c2,c3,cm2,cm1,cn,f1,g1,fn,gn=B.T
 h=1/(N-1); G=lambda l,s:P['K']*(1-l)*s*(s-P['beta']*l)
 S1=P['b1']*G(c1,f1)+P['b2']*G(c1,g1); SN=P['b1']*G(cn,fn)+P['b2']*G(cn,gn)
 adv=P['q']/2*(cn-cm1+c1+c2);disp=P['D']/h*(cn-cm1-c2+c1)
 return dict(advection=adv,dispersion=disp,endpoint_release=-h/2*(S1+SN),endpoint_storage=P['eps']*h/2*(c1+cn),S1=S1,SN=SN,
  inlet_constraint=(P['q']+1.5*P['D']/h)*c1-2*P['D']/h*c2+.5*P['D']/h*c3,
  outlet_constraint=.5*cm2-2*cm1+1.5*cn)

def attribute(H,B,N,T,method):
 assert np.array_equal(H[:,0],B[:,0]);t=H[:,0];rate=rates(B,N);row=observe(H,T,method)
 row.update(N=N,quadrature=method)
 for name in ['advection','dispersion','endpoint_release']:
  row[name+'_contribution_mg']=-P['factor_mg']*integrate(t,rate[name],T,method)
 row['endpoint_storage_contribution_mg']=-P['factor_mg']*(endpoint(t,rate['endpoint_storage'],T)-rate['endpoint_storage'][0])
 row['boundary_flux_contribution_mg']=row['inlet_total_mg']-row['outlet_dispersion_mg']
 row['predicted_E_mg']=observe(H,0)['observed_E_mg']+sum(row[k+'_contribution_mg'] for k in ['advection','dispersion','endpoint_release','endpoint_storage','boundary_flux'])
 row['remainder_mg']=row['observed_E_mg']-row['predicted_E_mg']
 for name in ['advection','dispersion','endpoint_release','endpoint_storage','boundary_flux']:
  row[name+'_absolute_mg']=abs(row[name+'_contribution_mg'])
 row['sum_absolute_components_mg']=sum(row[name+'_absolute_mg'] for name in ['advection','dispersion','endpoint_release','endpoint_storage','boundary_flux'])
 start=inventories(H)[0]
 rel1=P['factor_mg']*P['b1']*integrate(t,H[:,7],T,method)
 rel2=P['factor_mg']*P['b2']*integrate(t,H[:,8],T,method)
 row['fine_release_residual_mg']=start[0]-row['fine_mg']-rel1
 row['coarse_release_residual_mg']=start[1]-row['coarse_mg']-rel2
 row['liquid_balance_residual_mg']=row['liquid_mg']-start[2]-rel1-rel2-row['inlet_total_mg']+row['cup_mg']+row['outlet_dispersion_mg']
 return row

def write_csv(path,rows):
 with Path(path).open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

def reconstruct_old():
 rows=[];storage={};checks=[]
 for name in ['reference_sparse','tight_sparse']:
  c=OLD/name; H=np.loadtxt(c/'history.csv',delimiter=',');ref=json.loads((c/'reduction.json').read_text())
  for T in [0.,1.,10.]:
   row=observe(H,T);row['run']=name;rows.append(row)
   if T:
    prior=next(x for x in ref['endpoints'] if x['t_hat']==T)
    errors={key:row[new]-1000*prior[key] for key,new in [('initial_solid_g','initial_mg'),('final_fine_solute_g','fine_mg'),('final_coarse_solute_g','coarse_mg'),('liquid_solute_holdup_g','liquid_mg'),('cup_advective_solute_g','cup_mg'),('conservation_residual_g','observed_E_mg')]}
    assert max(abs(x) for x in errors.values())<1e-8
    checks.append(dict(run=name,t_hat=T,errors_mg=errors))
  storage[name]={'history_shape':list(H.shape),'snapshot_variables':whosmat(c/'snapshots.mat'),'diagnostic_snapshot_count':len(list(c.glob('diagnostic_*.mat'))),'full_N40_trajectory_retained':False,'missing_rate_fields':['c2','cN-1','endpoint particle surfaces']}
 write_csv(ROOT/'original_reconstruction.csv',rows)
 (ROOT/'original_reconstruction_check.json').write_text(json.dumps(checks,indent=2)+'\n')
 (ROOT/'retained_fields.json').write_text(json.dumps(storage,indent=2)+'\n')
 print(json.dumps(rows,indent=2))
if __name__=='__main__':reconstruct_old()
