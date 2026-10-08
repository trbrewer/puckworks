"""Fail-closed offline reduction of 004 artifacts; this module never runs solvers."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
from . import grudeva2026_bed_accuracy_004 as core
from . import grudeva2026_conservative_003 as inherited
from .grudeva2026_conservative_003_report import refinement

QUALIFIED = 'COMPARATOR_NUMERICALLY_QUALIFIED_ON_DECLARED_CASES'
INCOMPLETE = 'BED_ACCURACY_QUALIFICATION_INCOMPLETE'
ROWS = dict(normal=(512,3200,.002,1.), bed_fine=(1024,3200,.002,1.),
            radial_fine=(512,6400,.002,1.), time_fine=(512,3200,.001,1.),
            combined=(1024,6400,.001,1.), limit=(32,16,.01,0.),
            repeat=(512,3200,.002,1.))
HISTORY_Z = [.025,.1,.25,.5,.75,.9,1.]


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def digest(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',', ':'),allow_nan=False).encode()).hexdigest()


def read(path):
    def reject(value):
        raise ValueError('nonfinite JSON constant: '+value)
    data=json.loads(Path(path).read_text(),parse_constant=reject)
    # Also reject overflowing valid JSON numbers such as 1e999.
    def finite(v):
        if isinstance(v,float) and not np.isfinite(v): raise ValueError('nonfinite value')
        if isinstance(v,dict):
            for x in v.values(): finite(x)
        if isinstance(v,list):
            for x in v: finite(x)
    finite(data)
    return data


def controls(name):
    bed,shells,dt,diffusivity=ROWS[name]
    return dict(bed=bed,shells=shells,dt=dt,diffusivity=diffusivity,horizon=8.)


def scientific_sources():
    root=Path(core.__file__).parents[2]
    paths=[Path(core.__file__),Path(inherited.__file__),
           Path(core.__file__).with_name('grudeva2026_reference_002.py'),
           root/'puckworks/data/grudeva2026/publication_reference.json']
    return {str(p.relative_to(root)):sha(p) for p in paths}


def audit_run(r, expected):
    if r['controls'] != expected or r['configuration_sha256'] != digest(expected):
        raise ValueError('configuration mismatch')
    sources=scientific_sources()
    for key,path in [('source_sha256','puckworks/analysis/grudeva2026_bed_accuracy_004.py'),
                     ('inherited_source_sha256','puckworks/analysis/grudeva2026_conservative_003.py'),
                     ('radial_source_sha256','puckworks/analysis/grudeva2026_reference_002.py')]:
        if r[key]!=sources[path]: raise ValueError('executed source mismatch: '+key)
    t,z=inherited.observation_support(8.)
    if r['z']!=z.tolist() or r['grain_history_z']!=HISTORY_Z:
        raise ValueError('spatial/history support mismatch')
    records=np.asarray(r['records'],float);accepted=np.asarray(r['accepted'],float)
    obs=r['observations']
    if records.ndim!=2 or records.shape[1]!=8 or accepted.ndim!=2 or accepted.shape[1]!=12:
        raise ValueError('malformed or empty state arrays')
    if len(records)!=len(obs) or records[0,0]!=0 or records[-1,0]!=8 or accepted[-1,0]!=8:
        raise ValueError('missing initial/terminal support')
    if np.any(np.diff(records[:,0])<=0) or np.any(np.diff(accepted[:,0])<=0):
        raise ValueError('nonmonotone time support')
    if np.any(np.min(abs(records[:,0,None]-t[None,:]),axis=0)>2e-13):
        raise ValueError('missing requested time')
    activation=np.asarray(r['activation'],float);ha=np.asarray(r['grain_history_activation'],float)
    if activation.shape!=z.shape or ha.shape!=(7,) or not np.all(np.isfinite(np.r_[activation,ha])):
        raise ValueError('missing activation/history support')
    if not 1<r['arrival']<8: raise ValueError('missing desaturation exit')
    events={e['kind']:e for e in r['events']}
    if set(events)!={'first_drip','desaturation_exit'} or len(r['events'])!=2:
        raise ValueError('missing or duplicate events')
    if events['first_drip']['t']!=1 or events['first_drip']['outlet_left']!=0 or events['first_drip']['outlet_right']!=1:
        raise ValueError('first-drip event mismatch')
    event=events['desaturation_exit']
    if event['t']!=r['arrival'] or event['outlet_left']!=1:
        raise ValueError('exit event mismatch')
    if not np.any(records[:,0]==r['arrival']): raise ValueError('missing event state')
    if not np.any(accepted[:,0]==1.) or not np.any(accepted[:,0]==r['arrival']):
        raise ValueError('accepted evolution omits an event split')
    exitrow=records[np.flatnonzero(records[:,0]==r['arrival'])[0]]
    if event['outlet_right']!=exitrow[2]: raise ValueError('one-sided exit state mismatch')
    crossings=[o for o in obs if o['event'] in ('cell_crossing','exit')]
    if len(crossings)!=expected['bed'] or not np.allclose([o['faces'][-1] for o in crossings],np.arange(1,expected['bed']+1)/expected['bed'],rtol=0,atol=2e-14):
        raise ValueError('missing cell crossing states')
    phases=[];cmin=0.;cmax=0.;bmin=core.INITIAL
    for record,o in zip(records,obs):
        if o['t']!=record[0]: raise ValueError('observation time differs from state')
        f,c,b=map(lambda key:np.asarray(o[key],float),('faces','liquid_cells','grain_integrals'))
        if c.ndim!=1 or b.shape!=c.shape or f.shape!=(len(c)+1,) or f[0]!=0 or f[-1]!=record[1] or np.any(np.diff(f)<0):
            raise ValueError('invalid physical volumes')
        if record[0]>0 and np.any(np.diff(f)<=0): raise ValueError('zero-volume saved cell')
        cp,bp,hist=[np.asarray(o[key],float) for key in ('liquid_profile','grain_profile','grain_history')]
        if cp.shape!=z.shape or bp.shape!=z.shape or hist.shape!=(7,): raise ValueError('missing profile/history')
        if not all(np.all(np.isfinite(x)) for x in (f,c,b,cp,bp,hist)): raise ValueError('nonfinite state')
        ic=sum((right-left)*value for left,right,value in zip(f[:-1],f[1:],c))
        ib=sum(b);time,s=record[:2]
        phases.append([ic+min(time,1)-s,3.2*(ic+1.388*(1-s)),.8*(ib+1.388*(1-s))])
        cmin=min(cmin,float(min(c)),float(min(cp)));cmax=max(cmax,float(max(c)),float(max(cp)))
        bmin=min(bmin,float(min(bp)),float(min(hist)))
    phases=np.asarray(phases)
    residual=(phases.sum(axis=1)+records[:,3]-5.552)/5.552
    allowance=inherited.ALGEBRA_RTOL*accepted[:,10]+abs(accepted[:,9])
    if np.any(allowance<=0): raise ValueError('invalid amount allowance')
    fraction=max(abs(accepted[:,7])/allowance)
    linear=max(abs(accepted[:,9])/(inherited.ALGEBRA_RTOL*accepted[:,10]))
    quadrature=0.;previous_t=previous_trace=0.;cup_error=0.
    for row in accepted:
        now,trace=row[0],row[11]
        if previous_t>=1:
            if previous_t<r['arrival']: quadrature+=now-previous_t
            else:
                q=1/np.sqrt(3)
                values=[(previous_trace+trace)/2+(trace-previous_trace)*u/2 for u in (-q,q)]
                quadrature+=(now-previous_t)*sum(values)/2
        cup_error=max(cup_error,abs(quadrature-row[2]));previous_t,previous_trace=now,trace
    phase_error=float(np.max(abs(phases-records[:,4:7])))
    global_error=float(max(max(abs(residual)),max(abs(accepted[:,6]))))
    bounds=(min(cmin,r['aqueous_min'])>=-1e-8 and max(cmax,r['aqueous_max'])<=1+1e-8
            and min(bmin,r['grain_mean_min'],float(phases.min()))>=-1e-8
            and max(accepted[:,1]-np.minimum(accepted[:,0],1))<=1e-10)
    passed=(r['status']=='EXECUTED_UNQUALIFIED' and r['reason'] is None and bounds
            and global_error<=1e-6 and fraction<=1 and linear<=1 and phase_error<=5e-13
            and cup_error<=5e-12 and r['independent_shell_integral_error']<=5e-13)
    return dict(passed=bool(passed),status=r['status'],arrival=r['arrival'],
                max_global_normalized_residual=global_error,local_amount_allowance_fraction=float(fraction),
                linear_solve_allowance_fraction=float(linear),phase_reconstruction_error=phase_error,
                independent_split_cup_error=cup_error,shell_integral_error=r['independent_shell_integral_error'],
                bounds_passed=bool(bounds),aqueous_min=cmin,aqueous_max=cmax,grain_min=bmin,
                support=dict(times=len(t),z=len(z),histories=7,crossings=len(crossings),events=2,
                             unavailable=0),terminal_phase_inventory=phases[-1].tolist(),
                terminal_cup=float(records[-1,3]),accepted_steps=len(accepted),seconds=r['seconds'])


def resource_audit(folder):
    rows=[read_line(line) for line in (folder/'invocations.jsonl').read_text().splitlines()]
    starts={};ends={}
    for row in rows:
        if row['event'] not in ('start', 'end'): raise ValueError('invalid ledger event')
        dest=starts if row['event']=='start' else ends
        if row['name'] in dest: raise ValueError('duplicate attempt')
        dest[row['name']]=row
    if starts.keys()!=ends.keys(): raise ValueError('unresolved invocation')
    spent=sum(row['seconds'] for row in ends.values());full=sum(r['kind']=='full' for r in starts.values())
    if spent>3600 or full>24: raise ValueError('aggregate resource ceiling exceeded')
    for name,start in starts.items():
        end=ends[name]
        if start['time_ceiling']>900 or end['seconds']>900 or start['memory_bytes']!=2*1024**3:
            raise ValueError('invocation resource ceiling exceeded')
        if end['seconds']<0: raise ValueError('negative resource time')
    return dict(full_attempts=full,short_attempts=len(starts)-full,aggregate_seconds=spent,
                unresolved=0,passed=True),starts,ends


def read_line(line):
    row=json.loads(line)
    if any(isinstance(v,float) and not np.isfinite(v) for v in row.values()):
        raise ValueError('nonfinite ledger')
    return row


def reduce_saved(folder,matrix_path):
    plan=read(matrix_path)
    if set(plan['runs'])!=set(ROWS): raise ValueError('missing/extra mandatory rows')
    if plan['scientific_sources']!=scientific_sources(): raise ValueError('frozen source mismatch')
    if plan['reporter_sha256']!=sha(__file__): raise ValueError('frozen reporter mismatch')
    if plan['controller_sha256']!=sha(folder/'invoke.py'): raise ValueError('controller mismatch')
    root=Path(core.__file__).parents[2]
    for path,expected in plan['verification_sources'].items():
        if sha(root/path)!=expected: raise ValueError('verification/observer source mismatch')
    resources,starts,ends=resource_audit(folder)
    raw={};audits={}
    for name,entry in plan['runs'].items():
        if entry['controls']!=controls(name): raise ValueError('mandatory controls changed')
        path=folder/entry['file'];r=read(path)
        start=starts[entry['attempt']];end=ends[entry['attempt']]
        if start['kind']!='full' or end['exit_code']!=2 or end['artifact_sha256']!=sha(path):
            raise ValueError('execution/artifact binding mismatch')
        if start['source_hashes']['puckworks/analysis/grudeva2026_bed_accuracy_004.py']!=r['source_sha256']:
            raise ValueError('executed source ledger mismatch')
        raw[name]=r;audits[name]=audit_run(r,controls(name))
        audits[name]['artifact_sha256']=sha(path)
    local=read(folder/plan['local'])
    local_end=ends[plan['local_attempt']]
    if local_end['exit_code']!=0 or local_end['artifact_sha256']!=sha(folder/plan['local']):
        raise ValueError('local verification execution binding mismatch')
    if not local['passed'] or local['scientific_sources']!=scientific_sources():
        raise ValueError('local verification missing or source mismatch')
    if not local['minimum_dependencies_passed']: raise ValueError('minimum dependency qualification absent')
    if local['verification_source_sha256']!=sha(root/'tools/grudeva2026_bed_accuracy_004_verify.py'):
        raise ValueError('local verification source mismatch')
    if local['radial']['core_sha256']!=sha(inherited.__file__):
        raise ValueError('inherited radial source mismatch')
    radial_rows=local['radial']['radial']
    for shells in (3200,6400):
        selected=[r for r in radial_rows if r['shells']==shells]
        if len(selected)!=4 or any(r['flux_error']>2e-4 or r['mean_error']>2e-5 or not r['passed'] for r in selected):
            raise ValueError('radial analytical qualification absent or failed')
    if local['radial']['front_relative_error']>1e-12:
        raise ValueError('constant-front qualification failed')
    diffs={n:refinement(raw['normal'],raw[n]) for n in ('bed_fine','radial_fine','time_fine','combined')}
    for comparison in diffs.values():
        for row in comparison.values():
            if isinstance(row,dict) and 'included' in row:
                row['requested']=row['included']+row['excluded']+row['unavailable']
    repeat=digest({k:v for k,v in raw['normal'].items() if k!='seconds'})==digest({k:v for k,v in raw['repeat'].items() if k!='seconds'})
    limit=raw['limit'];record=np.asarray(limit['records'])
    err=abs(limit['arrival']/5.4416-1)
    grain=max(max(abs(np.array(o['grain_integrals'])/np.diff(o['faces'])-1.388)) for o in limit['observations'] if o['t']>0)
    speed=float(max(abs(record[:,1]-np.minimum(record[:,0]/5.4416,1))))
    limit_ok=(err<=1e-12 and grain<=1e-12 and speed<=1e-12 and abs(record[-1,3]-4.4416)<=1e-12)
    qualified=(all(a['passed'] for a in audits.values()) and all(d['passed'] for d in diffs.values())
               and repeat and limit_ok)
    return dict(task='MODEL-GRUDEVA2026-BED-ACCURACY-004',disposition=QUALIFIED if qualified else INCOMPLETE,
                qualified=bool(qualified),runs=audits,refinements=diffs,
                deterministic_repeat=bool(repeat),zero_diffusion=dict(passed=bool(limit_ok),arrival_relative_error=err,
                front_absolute_error=speed,grain_error=float(grain)),local_qualification=local,
                resources=resources,scientific_sources=scientific_sources(),matrix_sha256=sha(matrix_path),
                reporter_sha256=sha(__file__),physical_validation='NOT_ESTABLISHED',software_qa='REPORTED_SEPARATELY',
                hosted_ci='PENDING_VERIFICATION',independent_review='PENDING_EXACT_HEAD',
                production_comparison='NOT_EXECUTED',automatic_successor='NONE')


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--runs-directory',type=Path,required=True)
    p.add_argument('--matrix',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    args=p.parse_args(argv)
    try: result=reduce_saved(args.runs_directory,args.matrix)
    except (ValueError,KeyError,TypeError,IndexError,OSError,OverflowError) as exc:
        result=dict(disposition=INCOMPLETE,qualified=False,blocker=str(exc),physical_validation='NOT_ESTABLISHED')
    args.output.write_text(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+'\n')
    print(json.dumps({k:result[k] for k in ('disposition','qualified')}))
    return 0 if result['qualified'] else 2


if __name__=='__main__':
    raise SystemExit(main())
