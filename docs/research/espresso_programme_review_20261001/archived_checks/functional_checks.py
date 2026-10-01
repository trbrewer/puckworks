"""Compare source checkmass functional with retained moment diagnostics."""
from pathlib import Path
import json
import numpy as np
from scipy.io import loadmat
from balance import ROOT,OLD,P,inventories,write_csv
rows=[]
for run in ['reference_sparse','tight_sparse']:
 c=OLD/run;H=np.loadtxt(c/'history.csv',delimiter=',');s=loadmat(c/'snapshots.mat',simplify_cells=True)
 N=int(s['N']);h=1/(N-1);x=np.linspace(0,1,N);v=4*np.pi*(x*x*h+h**3/12)
 v[0]=4*np.pi/3*(h/2)**3;v[-1]=4*np.pi/3*(1-(1-h/2)**3)
 w=np.full(N,h);w[[0,-1]]=h/2;dp=np.asarray(s['dimensionlessparameters']).ravel()
 for i,u in zip(np.atleast_1d(s['snapshot_indices']).astype(int),np.atleast_2d(s['snapshot_u'])):
  fine=u[N:N+N*N].reshape(N,N);coarse=u[N+N*N:].reshape(N,N)
  author=P['factor_mg']*np.array([dp[0]/dp[6]/dp[4]*(w@(fine@v))/(4*np.pi),dp[1]/dp[6]/dp[5]*(w@(coarse@v))/(4*np.pi),P['eps']*(w@u[:N])])
  old=inventories(H)[i-1];diff=author-old
  assert np.max(abs(diff))<1e-8
  rows.append(dict(run=run,index=i,t_hat=H[i-1,0],fine_difference_mg=diff[0],coarse_difference_mg=diff[1],liquid_difference_mg=diff[2]))
write_csv(ROOT/'functional_equivalence.csv',rows)
print('Source checkmass inventory and executed reducer agree on all retained endpoint/bracket states; max difference mg:',max(abs(x[k]) for x in rows for k in ['fine_difference_mg','coarse_difference_mg','liquid_difference_mg']))
