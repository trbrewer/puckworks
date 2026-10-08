"""Family C completion: independently prescribed histories and profile integrals.

Explicit short verification, never a canonical trajectory or a new solver.
Uses the contract's <1e-9 oracle criterion and >10x uncertainty discriminator.
"""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
from scipy.linalg import expm

from puckworks.analysis import grudeva2026_bed_accuracy_004 as new
from puckworks.analysis import grudeva2026_conservative_003 as old


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    r=old.Radial(24)
    w,lower,diagonal,upper,forcing,_=r.op
    physical=np.diag(diagonal)+np.diag(lower,-1)+np.diag(upper,1)
    augmented=np.zeros((28,28));augmented[:24,:24]=physical
    # C(t,z)=.15+.08*z+.05*t+.02*t² with independently prescribed activation.
    augmented[:24,24:]=forcing[:,None]*np.array([.15,.08,.05,.02])
    augmented[26,24]=1.;augmented[27,26]=2.
    activation=lambda z:2*z+.2*z*z
    boundary=lambda t,z:.15+.08*z+.05*t+.02*t*t
    def shell(t,z):
        tau=activation(z)
        return (expm((t-tau)*augmented)@np.r_[np.full(24,old.INITIAL),1.,z,tau,tau*tau])[:24]
    def value(t,z):return float(w@shell(t,z))
    def integrals(t,faces,order):
        nodes,weights=np.polynomial.legendre.leggauss(order)
        q=(nodes+1)/2
        return np.array([sum(weight*qi*value(t,right-(right-left)*qi*qi)
                            for weight,qi in zip(weights,q))
                         for left,right in zip(faces[:-1],faces[1:])])
    profiles=[]
    for n in (32,64,128):
        for fraction in (.2,.5,.8):
            s=(n//2+fraction)/n;t=activation(s)
            faces=np.r_[np.arange(n//2+1)/n,s]
            m=integrals(t,faces,32);m2=integrals(t,faces,64)
            probes=[0.,.1,.25,faces[-2]+.5*(s-faces[-2]),s]
            center=(faces[:-1]+faces[1:])/2
            for point in probes:
                true=value(t,point)
                linear=float(np.interp(point,np.r_[0.,center,s],np.r_[value(t,0.),m,old.INITIAL]))
                corrected=new.point_liquid(point,faces,m,inlet=value(t,0.))
                profiles.append(dict(n=n,fraction=fraction,point=point,age=t-activation(point),
                    old_save_error=abs(linear-true),new_profile_error=abs(corrected-true),
                    oracle_change=float(max(abs(m-m2)))))
        for elapsed in (.003,.05):
            t=activation(1.)+elapsed;faces=np.linspace(0.,1.,n+1)
            m=integrals(t,faces,32);m2=integrals(t,faces,64)
            for point in (0.,.25,.99,1.):
                true=value(t,point)
                # Canonical endpoint readout uses the separately integrated
                # fixed-z history. Record that path separately below.
                corrected=new.point_liquid(point,faces,m,1.+elapsed/2.4,value(t,0.))
                profiles.append(dict(n=n,post_exit_elapsed=elapsed,point=point,age=t-activation(point),
                    new_integral_profile_error=abs(corrected-true),oracle_change=float(max(abs(m-m2)))))
    histories=[]
    for z in (0.,.1,.25,.501,1.):
        for age in (.02,.13):
            for dt in (.004,.002,.001):
                tau=activation(z);t=tau;j=np.full((24,1),old.INITIAL)
                end=tau+age
                while t<end:
                    h=min(dt,end-t)
                    j=r.advance(j,np.array([boundary(t,z)]),np.array([boundary(t+h,z)]),
                                np.ones(1),np.zeros(1),h)
                    t+=h
                error=float(w@abs(r.shells(j)[:,0]-shell(end,z)))
                histories.append(dict(z=z,activation=tau,age=age,dt=dt,
                    actual_history_mean_error=abs(float(r.means(j)[0])-value(end,z)),
                    shell_amount_l1_error=error))
    oracle=max(row['oracle_change'] for row in profiles)
    result=dict(family='C',role='post-implementation completion of predeclared diagnostic',
                profiles=profiles,histories=histories,oracle_change=oracle,
                oracle_passed=bool(oracle<1e-9),physical_validation='NOT_ESTABLISHED',
                source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                core_sha256=hashlib.sha256(Path(new.__file__).read_bytes()).hexdigest())
    args.output.write_text(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+'\n')
    print(json.dumps({'oracle_change':oracle,'passed':result['oracle_passed']}))
    return 0 if result['oracle_passed'] else 2


if __name__=='__main__':
    raise SystemExit(main())
