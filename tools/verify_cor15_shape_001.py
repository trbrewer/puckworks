#!/usr/bin/env python3
"""Numerical verification of retained shape fits; no new scientific comparison."""
import hashlib
from importlib.metadata import version
import json
from pathlib import Path
import sys

import numpy as np
import scipy
from scipy.optimize import least_squares

from puckworks.analysis import cor15_shape_001 as c


def main():
    result=json.loads((c.OUTPUT/'RESULT.json').read_text())
    contract,coords=c.read_inputs()
    data=c.realize(contract,coords)
    checks=[]
    for s,fits in result['central_fits'].items():
        ii=[i for i,r in enumerate(coords) if r['series']==s]
        p,q=data[ii].T
        x,y=p/1e5,q*1e6
        for model in c.MODELS:
            saved=fits[model]
            if model in ['L0','FA']:
                basis=x if model=='L0' else c.fa_shape(p)
                pred=np.linalg.lstsq(basis[:,None],y,rcond=None)[0][0]*basis
            else:
                if model=='L1':
                    fun=lambda z:z[0]*np.maximum(x-z[1],0)
                    start=[saved['amplitude']*1e11,saved['P0_Pa']/1e5]
                    bounds=([0,-np.inf],[np.inf,x.max()])
                elif model=='L2':
                    fun=lambda z:z[0]*x**z[1]
                    start=[saved['amplitude']*1e6,saved['m']]
                    bounds=([0,0],[np.inf,np.inf])
                else:
                    fun=lambda z:z[0]*c.fa_shape(p,z[1])
                    start=[saved['amplitude']*1e6,saved['inverse_Pstar_bar']]
                    bounds=([0,0],[np.inf,np.inf])
                sol=least_squares(lambda z:fun(z)-y,start,bounds=bounds,
                                  xtol=1e-13,ftol=1e-13,gtol=1e-13)
                pred=fun(sol.x)
            rmse=np.sqrt(np.mean((pred-y)**2))/1e6
            checks.append(dict(series=s,model=model,independent_RMSE_m3_s=rmse,
                producer_RMSE_m3_s=saved['rmse'],absolute_difference_m3_s=abs(rmse-saved['rmse'])))
    c.write_csv(c.OUTPUT/'NUMERICAL_CHECK.csv',checks)
    paths=[c.DATA/'contract.json',c.DATA/'coordinates.csv',Path(c.__file__),Path(__file__),
           c.ROOT/'tools/report_cor15_shape_001.py', c.ROOT/'tools/cor15_shape_overlay.py',
           c.ROOT/'puckworks/data/romancorrochano2015/table2.csv',
           c.ROOT/'docs/analysis/sci_val_tamped_k_001/SOURCE_CONSISTENCY.json',
           c.ROOT/'docs/research/PRESSURE_PEAK_STAGE_D0/RESULT_TABLE.csv']
    outputs=list(c.OUTPUT.glob('*.csv'))+[c.OUTPUT/'RESULT.json',c.OUTPUT/'comparison.svg']
    receipt=dict(python=sys.version,numpy=np.__version__,scipy=scipy.__version__,
        matplotlib=version('matplotlib'), pillow=version('pillow'),
        source_pdf_sha256=contract['source_pdf_sha256'],
        source_image_sha256=contract['native_image_sha256'],
        inputs_sha256={str(p.relative_to(c.ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},
        outputs_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in outputs},
        largest_independent_RMSE_difference_m3_s=max(r['absolute_difference_m3_s'] for r in checks),
        method='Linear algebra for amplitudes; nonlinear least-squares refinement of central solutions, not proof of global uniqueness or scientific gate')
    (c.OUTPUT/'REPRODUCTION.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(receipt['largest_independent_RMSE_difference_m3_s'])


if __name__=='__main__':
    main()
