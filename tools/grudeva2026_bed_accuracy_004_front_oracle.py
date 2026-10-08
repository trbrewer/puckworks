"""Independent positive-diffusion prescribed-front oracle for diagnostic B.

No canonical run or production numerical import. The symmetric rank-one
travelling generator is checked against the original-shell matrix exponential.
"""
import argparse
import json
import numpy as np
from scipy.linalg import eigh,expm


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--implementation',choices=['003','004'],required=True)
    parser.add_argument('--output',type=__import__('pathlib').Path,required=True)
    args=parser.parse_args(argv)
    if args.implementation=='003':
        from puckworks.analysis import grudeva2026_conservative_003 as old
    else:
        from puckworks.analysis import grudeva2026_bed_accuracy_004 as old
    
    results={}
    # Independently assembled finite-shell travelling solution. Let k=delta*v/(1-a*v).
    # C=k*B, x'=-lambda*x+lambda*k*(w*x). Similar symmetric generator is rank one.
    # This is a prescribed-front diagnostic, NOT canonical front dynamics.
    r=old.Radial(128);v=.15;k=old.DELTA*v/(1-old.CAPACITY*v)
    p=np.sqrt(r.weights*r.rates)
    mu,q=eigh(np.diag(r.rates)-k*np.outer(p,p))
    left=(r.weights*np.sqrt(r.rates/r.weights))@q
    right=q.T@(np.sqrt(r.weights/r.rates)*old.INITIAL)
    amplitude=left*right
    
    def mean_exp(lo,hi):
     # Integral over ages [lo,hi]; pointwise limit if equal.
     return np.exp(-mu*lo)*(-np.expm1(-mu*(hi-lo)))/mu/(hi-lo)
    rows=[]
    for n in (32,64,128):
     for frac in (.2,.5,.8):
      s=(n//2+frac)/n;t=s/v
      f=np.r_[np.arange(n//2+1)/n,s]
      avg=np.array([k*np.sum(amplitude*mean_exp((s-b)/v,(s-a)/v)) for a,b in zip(f[:-1],f[1:])])
      exact=k*old.INITIAL
      inlet=k*np.sum(amplitude*np.exp(-mu*t))
      trace=old.face_values(avg,f,inlet)[-1]
      # Exact field integral is supplied to old transport; source is independently
      # determined by actual mean change on moving support.
      h=1e-5;g=f.copy();g[-1]+=v*h
      nxt=np.array([k*np.sum(amplitude*mean_exp((g[-1]-b)/v,(g[-1]-a)/v)) for a,b in zip(g[:-1],g[1:])])
      b0=np.diff(f)*avg/k;b1=np.diff(g)*nxt/k
      source=old.DELTA*(b0+old.INITIAL*np.r_[np.zeros(len(avg)-1),v*h]-b1)
      actual,flux,cf,_=old.transport_solve(avg,f,g,h,source,np.zeros(len(avg)),inlet=inlet)
      rows.append({'n':n,'fraction':frac,'exact_front':exact,'front_trace_error':abs(trace-exact),
       'evolved_average_step_error':float(max(abs(actual-nxt))),
       'front_amount_error':abs(flux[-1]-(h-old.CAPACITY*v*h)*exact)})
    results['travelling']=rows
    # Cross-check modal travelling oracle by matrix exponential in actual shell coordinates.
    w,l,d,u,forcing,_=r.op
    m=np.diag(d)+np.diag(l,-1)+np.diag(u,1)+k*forcing[:,None]*w[None,:]
    results['oracle_expm_error']=max(abs(float(w@expm(m*age)@np.full(128,old.INITIAL))-np.sum(amplitude*np.exp(-mu*age))) for age in (.0001,.002,.02,.2))
    args.output.write_text(json.dumps(results,indent=2,allow_nan=False)+'\n')
    print(json.dumps({'oracle_error':results['oracle_expm_error']}))


if __name__=='__main__':
    main()
