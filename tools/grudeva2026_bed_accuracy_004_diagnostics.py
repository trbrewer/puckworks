"""Three bounded 004 diagnostic families; explicit numerical invocation only.

Run through the task's external controller. Exact integral and physical-shell
matrix-exponential oracles are independent of the tested reconstruction.
"""
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
from scipy.linalg import expm


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--implementation',choices=['003','004'],required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args(argv)
    if args.implementation=='003':
        from puckworks.analysis import grudeva2026_conservative_003 as old
    else:
        from puckworks.analysis import grudeva2026_bed_accuracy_004 as old
    out=args.output.parent
    results={'source_sha256':hashlib.sha256(Path(old.__file__).read_bytes()).hexdigest()}
    
    def smooth(n,dt):
     f=np.linspace(0,1,n+1);v=np.diff(f);x=(f[:-1]+f[1:])/2
     mean=(np.diff(f**2)/2+np.diff(f**3)/3)/v
     c=.2*mean
     for i in range(round(.1/dt)):
      t=(i+.5)*dt
      source=dt*(old.CAPACITY*.1*v*mean+(.2+.1*t)*np.diff(f+f**2))
      c,_,_,_=old.transport_solve(c,f,f,dt,source,np.zeros(n))
     exact=.21*mean
     pts=np.linspace(0,1,601)
     return {'n':n,'dt':dt,'average':float(max(abs(c-exact))),
      'face':float(max(abs(old.face_values(c,f)-.21*(f+f*f)))),
      'point':max(abs(old.point_liquid(z,f,c)-.21*(z+z*z)) for z in pts)}
    results['A']=[smooth(n,1e-4) for n in (32,64,128)]+[smooth(128,5e-5)]
    
    # Independent shell matrix exponential for quadratic liquid time histories.
    r=old.Radial(32)
    w,l,d,u,forcing,_=r.op
    mat=np.diag(d)+np.diag(l,-1)+np.diag(u,1)
    # Augment with [1,t,t²,z], t'=1; z fixed. C=.2+.1*t+.03*t²+.05*z.
    aug=np.zeros((36,36));aug[:32,:32]=mat
    aug[:32,32:]=forcing[:,None]*np.array([.2,.1,.03,.05])
    aug[33,32]=1;aug[34,33]=2
    
    def state(t,z):
     tau=(-.16+np.sqrt(.16**2+.04*z))/.02
     y=np.r_[np.full(32,old.INITIAL),1,tau,tau*tau,z]
     return (expm(aug*(t-tau))@y)[:32]
    
    def cohort(t,left,right,order):
     nodes,weights=np.polynomial.legendre.leggauss(order)
     # Quadratic map at newest endpoint also controls initial surface layer.
     q=(nodes+1)/2;z=right-(right-left)*q*q
     return sum(weight*2*(right-left)*qi*state(t,zi) for weight,qi,zi in zip(weights/2,q,z))
    
    rows=[]
    for frac in (.2,.5,.8):
     n=32;t=.8;left=0.1;right=left+frac/n
     # Restrict to a cell admitted during the prescribed front history.
     stop=(-.16+np.sqrt(.16**2+.04*right))/.02
     a=cohort(stop,left,right,32);b=cohort(stop,left,right,64)
     rows.append({'fraction':frac,'cohort_oracle_change':float(max(abs(a-b)))})
    # Evolve all admission through a crossing, collecting individual fixed-cell integrals.
    for dt in (.004,.002,.001):
     f=np.linspace(0,.2,33);j=np.zeros((32,32));t=0.
     while t<.8:
      h=min(dt,.8-t);s0=.16*t+.01*t*t;s1=.16*(t+h)+.01*(t+h)**2
      v0=np.maximum(np.minimum(f[1:],s0)-f[:-1],0)
      v1=np.maximum(np.minimum(f[1:],s1)-f[:-1],0)
      z0=f[:-1]+v0/2;z1=f[:-1]+v1/2
      c0=.2+.1*t+.03*t*t+.05*z0
      c1=.2+.1*(t+h)+.03*(t+h)**2+.05*z1
      # Split at cell crossings so source projection alone is measured.
      nxt=f[f>s0+1e-14][0]
      if s1>nxt:
       crossing=(-.16+np.sqrt(.16**2+.04*nxt))/.02
       h=crossing-t;s1=nxt
       v1=np.maximum(np.minimum(f[1:],s1)-f[:-1],0);z1=f[:-1]+v1/2
       c1=.2+.1*(t+h)+.03*(t+h)**2+.05*z1
      j=r.advance(j,c0,c1,v0,v1-v0,h);t+=h
     s=.16*.8+.01*.8**2
     exact=np.stack([cohort(.8,left,min(right,s),64) if left<s else np.zeros(32) for left,right in zip(f[:-1],f[1:])],axis=1)
     rows.append({'dt':dt,'shell_integral_error':float(np.max(abs(r.shells(j)-exact))),
      'grain_amount_error':float(max(abs(r.means(j)-w@exact)))})
    results['B_admission']=rows
    
    # Exact square-root spatial field: integral and point values are independent.
    # Boundary-layer shape is a diagnostic, not a new physical canonical solution.
    curved=[]
    for n in (32,64,128):
     for frac in (.2,.5,.8,1.):
      s=(n//2+frac)/n
      f=np.r_[np.arange(n//2+1)/n,s]
      primitive=lambda z:.3*(z+2*(s-z)**1.5/(3*np.sqrt(s)))
      c=np.diff(primitive(f))/np.diff(f)
      trace=old.face_values(c,f)[-1]
      probe=s-.35/n
      truth=.3*(1-np.sqrt((s-probe)/s))
      center=(f[:-1]+f[1:])/2
      readout=(np.interp(probe,np.r_[0,center,s],np.r_[0,c,trace]) if args.implementation=='003' else old.point_liquid(probe,f,c))
      curved.append({'n':n,'fraction':frac,'front_error':abs(trace-.3),
        'point_forcing_error':abs(old.point_liquid(probe,f,c)-truth),'save_error':abs(readout-truth)})
    results['B_front_and_C_curved']=curved
    
    # Exact history forcing comparison: finite-shell grain ODE integrated independently
    # by augmented exponential for linear-in-time forcing of a curved spatial field.
    rows=[]
    for n in (32,64,128):
     f=np.linspace(0,1,n+1);v=np.diff(f)
     means=(np.diff(f*f)/2+np.diff(f**3)/3)/v
     z=.25123;exact=.2*(z+z*z);actual=old.point_liquid(z,f,.2*means)
     y0=np.full(32,old.INITIAL);age=.13
     true=exact+expm(mat*age)@(y0-exact)
     pred=r.advance(np.full((32,1),old.INITIAL),np.array([actual]),np.array([actual]),np.ones(1),np.zeros(1),age)
     rows.append({'n':n,'forcing_error':abs(actual-exact),'history_error':abs(float(r.means(pred)[0]-w@true)),
     'shell_oracle_error':float(max(abs(r.shells(r.advance(np.full((32,1),old.INITIAL),np.array([exact]),np.array([exact]),np.ones(1),np.zeros(1),age))[:,0]-true)))})
    results['C_smooth']=rows
    args.output.write_text(json.dumps(results,indent=2,allow_nan=False)+'\n')
    print(json.dumps({'implementation':args.implementation,'output':args.output.name}))


if __name__=='__main__':
    main()
