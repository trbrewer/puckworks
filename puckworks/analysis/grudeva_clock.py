"""SCI-MD-GRUDEVA-CLOCK-001: conditional delivery, never a puck inventory solver.

Units at this research-only interface: seconds, grams beverage, grams solute,
and recorded TDS percent. Source: Grudeva espresso-model (permission documented
in docs/permissions/grudeva2025.md). Raw/row-level artifacts must remain private.
"""
import argparse
import csv
import hashlib
import json
import math
from functools import lru_cache
from pathlib import Path
import platform

import numpy as np
import scipy
from scipy.integrate import quad
from scipy.optimize import least_squares

SOURCE_COMMIT = '567ad8f3808eb74fbe3e470eaa333161bf2eac1c'
SOURCE_SHA = '291cadb1d06a009f758c158c95b020db551c127333e9dec6f6c581eac320130c'
NOTEBOOK_SHA = 'bccaa696080166f8b31587c17a7268a7c13ce9dd5d19d4beec349f64e2c70dff'
ROOT = Path(__file__).resolve().parents[2]
COORDS = ('shot', 'vial', 'mass_g', 'b_start_g', 't_start_s', 't_end_s')
SINGLE_STARTS = ((.2,.03,1),(.3,.08,1),(.1,.02,.5),(.5,.1,2),
                 (.25,.05,4),(.4,.15,.25),(.15,0,1),(.75,.3,3))
MIXED_STARTS = ((.2,.02,.02,1),(.3,.05,.05,1),(.1,.01,.01,.5),
                (.5,.05,.05,2),(.25,.025,.025,4),(.4,.075,.075,.25))
TREATMENTS = {'primary': ('unavailable','linear'),
              'literal_zero': ('literal','linear'),
              'time_u2': ('unavailable','u2'),
              'time_sqrt': ('unavailable','sqrt')}
NUM_TOL = 1e-6


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_json(path, value):
    """Exclusive creation preserves original evidence; caller chooses a new path."""
    with Path(path).open('x') as f:
        json.dump(value, f, indent=2, sort_keys=True, allow_nan=False)
        f.write('\n')


def read_json(path):
    return json.loads(Path(path).read_text())


def parse_source(path):
    """Rectangular 5-row blocks; never independently compact weight/TDS columns."""
    source_hash = digest(path)
    with Path(path).open(newline='') as f:
        lines = [r for r in csv.reader(f) if any(x.strip() for x in r)]
    if len(lines) % 5:
        raise ValueError('incomplete source block')
    records = []
    labels = ['Vial No.', 'Vial Weight', 'Vial+Coffee', 'Weight', 'TDS']
    width = max(len(r) for r in lines)-1
    for start in range(0, len(lines), 5):
        block = lines[start:start+5]
        if [r[0] for r in block] != labels:
            raise ValueError('source block labels changed')
        for col in range(1, width+1):
            vals = [float(r[col]) if col < len(r) and r[col].strip() else None
                    for r in block]
            vial, tare, gross, net, tds = vals
            present = vial is not None
            if present and vial != col:
                raise ValueError('vial identity is not the original column position')
            diff = None if tare is None or gross is None else gross-tare
            discrepancy = None if diff is None or net is None else net-diff
            regular = present and col <= 16
            records.append(dict(source_sha256=source_hash, shot=start//5+1, vial=col,
                source_lines=[start+1,start+5], present=present, tare_g=tare,
                gross_g=gross, recorded_net_g=net, gross_minus_tare_g=diff,
                net_discrepancy_g=discrepancy,
                discrepancy_at_source_precision=discrepancy is not None and abs(discrepancy)>.005,
                tds_pct=tds, tds_units='percent; PlotData cells 6/8',
                mass_g=net if present else None,
                mass_origin='recorded Weight; notebook authority' if net is not None else 'missing',
                tds_origin='recorded (may include source dilution correction)' if tds is not None else 'missing',
                t_start_s=2*(col-1) if regular else None,
                t_end_s=2*col if regular else None,
                clock_authority='thesis 2.1/2.2; PlotData cells 14/19' if regular else 'unqualified terminal clock',
                cohort='notebook13' if start//5 < 13 else 'extra_block_unqualified',
                window='regular16' if regular else ('terminal' if present else 'padding')))
    return records


def observations(records, zero='unavailable', shots=tuple(range(1,14))):
    if zero not in ('unavailable','literal'):
        raise ValueError('unknown zero treatment')
    out=[]
    for shot in shots:
        group=sorted([r for r in records if r['shot']==shot and r['window']=='regular16'],
                     key=lambda r:r['vial'])
        if [r['vial'] for r in group] != list(range(1,17)):
            raise ValueError('incomplete regular window')
        b=0.
        for source in group:
            r=dict(source)
            m=r['mass_g']; tds=r['tds_pct']
            r['b_start_g']=b
            if m is None or not math.isfinite(m) or m<0:
                raise ValueError(f'unresolved beverage mass gap: shot {shot} vial {r["vial"]}')
            b+=m
            r['b_end_g']=b
            if m==0:
                r.update(solute_g=0.,eligible=False,reason='structural_zero_liquid')
            elif tds is None or (tds==0 and zero=='unavailable'):
                r.update(solute_g=None,eligible=False,reason='unavailable_chemistry')
            elif not math.isfinite(tds) or not 0<=tds<=100:
                raise ValueError('unqualified TDS percent')
            else:
                r.update(solute_g=m*tds/100,eligible=True,
                         reason='literal_ambiguous_zero' if tds==0 else 'measured_positive')
            out.append(r)
    return out


def audit(source, out):
    records=parse_source(source)
    obs=observations(records)
    discrepancy=[{'shot':r['shot'],'vial':r['vial'],'delta_g':r['net_discrepancy_g']}
                 for r in records if r['discrepancy_at_source_precision']]
    historical=list(csv.DictReader((ROOT/'puckworks/data/grudeva2025/exp13_per_vial_stats.csv').open()))
    all14=observations(records,zero='literal',shots=tuple(range(1,15)))
    reconciliation=[]
    for i in range(1,17):
        yy=[r['solute_g'] for r in all14 if r['vial']==i]
        mu,sd=float(np.mean(yy)),float(np.std(yy,ddof=1))
        old=historical[i-1]
        reconciliation.append(dict(vial=i,mean_round4=round(mu,4),sd_round4=round(sd,4),
            mean_matches=round(mu,4)==float(old['solubles_mean_g']),
            sd_matches=round(sd,4)==float(old['solubles_sd_g'])))
    summary=dict(source_sha256=digest(source),source_commit=SOURCE_COMMIT,
        raw_blocks=len(records)//18,rectangular_rows=len(records),
        present_vials=sum(r['present'] for r in records),
        primary_shots=13,regular_vials=len(obs),folds=list(range(1,14)),
        positive_scoring_vials=sum(r['eligible'] for r in obs),
        structural_zeros=sum(r['mass_g']==0 for r in obs),
        unavailable_chemistry=[{'shot':r['shot'],'vial':r['vial']} for r in obs if r['solute_g'] is None],
        terminal_vials=sum(r['window']=='terminal' for r in records),
        missing_tare=[{'shot':r['shot'],'vial':r['vial']} for r in records if r['present'] and r['tare_g'] is None],
        missing_tds=[{'shot':r['shot'],'vial':r['vial']} for r in records if r['present'] and r['tds_pct'] is None],
        net_discrepancies=discrepancy,historical_reconciliation=reconciliation,
        alternate14='SOURCE_CONTRACT_BLOCKED_FOR_NAMED_COMPARISON: extra block lacks physical-shot/cohort authority')
    write_json(out/'source_rows.json',records)
    write_json(out/'observations.json',obs)
    write_json(out/'source_audit.json',summary)
    return summary


@lru_cache(None)
def quadrature(order):
    v,w=np.polynomial.legendre.leggauss(order)
    v=(v+1)/2
    # u=v^8 regularizes p=.25 and sqrt(u) near zero; positive quadrature weights.
    return v**8, w/2*8*v**7


def concentration(t,b,theta):
    c0,at,am,p=theta
    return c0*np.exp(-(at*t+am*b)**p)


def deliver(rows,theta,timing='linear',order=128,endpoint=None):
    """Integral c(t(b),b) db. Conserves delivery only, no grain inventory balance."""
    if timing not in ('linear','u2','sqrt') or endpoint not in (None,'start','end'):
        raise ValueError('unknown sampling assumption')
    if len(theta)!=4 or not np.isfinite(theta).all():
        raise ValueError('nonfinite parameters')
    c0,at,am,p=theta
    if not (0<=c0<=1 and 0<=at<=10 and 0<=am<=10 and .25<=p<=4):
        raise ValueError('parameter bounds')
    a=np.array([[r[k] for k in COORDS[2:]] for r in rows],float)
    if not len(a):
        return np.array([])
    m,b,t0,t1=a.T
    if not np.isfinite(a).all() or np.any(a<0) or np.any(t1<t0):
        raise ValueError('invalid coordinates')
    u,w=quadrature(order)
    f={'linear':u,'u2':u*u,'sqrt':np.sqrt(u)}[timing]
    t=t0[:,None]+(t1-t0)[:,None]*f
    if endpoint:
        t=(t0 if endpoint=='start' else t1)[:,None]
    y=m*np.sum(w*concentration(t,b[:,None]+m[:,None]*u,theta),axis=1)
    if not np.isfinite(y).all() or np.any(y < 0) or np.any(y>m+1e-12):
        raise FloatingPointError('delivery bound failure; no clipping')
    return y


def independent_delivery(r,theta,timing='linear',endpoint=None):
    m=r['mass_g']
    if m==0:
        return 0.,0.
    def f(u):
        time_u={'linear':u,'u2':u*u,'sqrt':math.sqrt(u)}[timing]
        t=r['t_start_s']+(r['t_end_s']-r['t_start_s'])*time_u
        if endpoint:
            t=r['t_start_s'] if endpoint=='start' else r['t_end_s']
        return m*float(concentration(t,r['b_start_g']+m*u,theta))
    return quad(f,0,1,epsabs=1e-11,epsrel=1e-11,limit=200)


def unpack(x,candidate):
    return (x[0],x[1],0.,x[2]) if candidate=='TIME' else (
        (x[0],0.,x[1],x[2]) if candidate=='MASS' else tuple(x))


def fit(training,candidate,timing='linear',nested=None):
    rows=[r for r in training if r['eligible'] and r['mass_g']>0]
    shots=sorted({r['shot'] for r in training})
    counts={s:sum(r['shot']==s for r in rows) for s in shots}
    if not rows or min(counts.values())==0:
        raise ValueError('insufficient eligible training support')
    weights=np.array([1/math.sqrt(len(shots)*counts[r['shot']]) for r in rows])
    target=np.array([r['solute_g'] for r in rows])
    if candidate=='MIXED':
        if nested is not None and any(nested[k]['theta'] is None for k in ('TIME','MASS')):
            return dict(theta=None,attempts=[],status='NESTED_SOLUTION_UNAVAILABLE')
        if nested is None:
            raise ValueError('training-only nested solutions required')
        starts=list(MIXED_STARTS)+[tuple(nested[k]['theta']) for k in ('TIME','MASS')]
        bounds=([0,0,0,.25],[1,10,10,4]); scale=[.2,.05,.05,1]
    else:
        starts=SINGLE_STARTS; bounds=([0,0,.25],[1,10,4]); scale=[.2,.05,1]
    attempts=[]; solutions=[]
    for index,start in enumerate(starts):
        calls=0
        last={}
        def residual(x):
            nonlocal calls
            if calls>=2000:
                raise RuntimeError('objective evaluation budget exhausted')
            calls+=1
            value=(deliver(rows,unpack(x,candidate),timing)-target)*weights
            last.update(theta=list(unpack(x,candidate)),loss=float(value@value))
            return value
        initial=residual(start)
        initial_loss=float(initial@initial)
        try:
            result=least_squares(residual,start,bounds=bounds,method='trf',jac='2-point',
                ftol=1e-10,xtol=1e-10,gtol=1e-10,x_scale=scale,diff_step=1e-6,
                max_nfev=2000,tr_solver='exact',loss='linear',verbose=0)
            loss=float(2*result.cost)
            success=bool(result.success)
            theta=unpack(result.x,candidate)
            rec=dict(start_index=index,start=list(start),calls=calls,
                status=int(result.status),success=success,message=str(result.message),
                loss=loss,initial_loss=initial_loss,theta=list(theta),
                optimizer_nfev=int(result.nfev),optimizer_njev=int(result.njev))
            if success:
                solutions.append((loss,index,theta,'optimizer'))
                # Retain exact nested limits (TRF otherwise nudges bound starts inward).
                if candidate=='MIXED' and index>=6:
                    solutions.append((initial_loss,index,unpack(start,candidate),'exact_nested_start'))
        except (RuntimeError,ValueError,FloatingPointError) as exc:
            rec=dict(start_index=index,start=list(start),calls=calls,success=False,
                     status=-99,message=str(exc),initial_loss=initial_loss,
                     last_evaluated_theta=last.get('theta'),last_evaluated_loss=last.get('loss'),
                     optimizer_nfev=None,optimizer_njev=None,
                     optimizer_counters_status='unavailable after exception; calls retains exact wrapper count')
        attempts.append(rec)
    if not solutions:
        return dict(theta=None,attempts=attempts,status='ALL_STARTS_FAILED')
    loss,index,theta,origin=min(solutions,key=lambda z:(z[0],z[1]))
    labels=('c0','a_t_per_s','a_m_per_g','p')
    lo=(0,0,0,.25);hi=(1,10,10,4)
    active=[labels[i] for i,v in enumerate(theta) if min(abs(v-lo[i]),abs(v-hi[i]))<=1e-7
            and not (candidate=='TIME' and i==2) and not (candidate=='MASS' and i==1)]
    return dict(theta=list(theta),loss=loss,selected_start=index,selected_origin=origin,
                attempts=attempts,boundary_hits=active,status='CONVERGED')


def template(training,coordinates):
    bypos={}
    for r in training:
        if r['eligible'] and r['mass_g']>0:
            bypos.setdefault(r['vial'],[]).append(r['tds_pct']/100)
    if not bypos:
        raise ValueError('no template support')
    means={v:float(np.mean(x)) for v,x in bypos.items()}
    fallback=[];y=[]
    for r in coordinates:
        v=r['vial']
        nearest=min(means,key=lambda q:(abs(q-v),q))
        if v not in means:
            fallback.append(dict(vial=v,used=nearest,structural_zero=r['mass_g']==0))
        y.append(r['mass_g']*means[nearest])
    return np.array(y),dict(position_means=means,support_counts={v:len(x) for v,x in bypos.items()},
                           effective_positions=len(means),fallbacks=fallback)


def fold_predict(rows,held,timing='linear',reuse=None):
    # Response projection occurs before any operation in this fold. No held eligibility mask.
    training=[r for r in rows if r['shot']!=held]
    coordinates=[{k:r[k] for k in COORDS} for r in rows if r['shot']==held]
    fitted={};predictions={}
    for candidate in ('TIME','MASS','MIXED','TEMPLATE'):
        if reuse is not None and candidate in ('MASS','TEMPLATE'):
            fitted[candidate]=reuse['fits'][candidate]
            predictions[candidate]=reuse['predictions'][candidate]
            continue
        if candidate=='TEMPLATE':
            pred,record=template(training,coordinates)
            fitted[candidate]=record
            predictions[candidate]=[dict(**r,yhat_g=float(y),numerical_allowance_g=0.)
                                    for r,y in zip(coordinates,pred)]
            continue
        record=fit(training,candidate,timing,nested=fitted)
        fitted[candidate]=record
        if record['theta'] is None:
            predictions[candidate]=None
            continue
        theta=record['theta']
        y=deliver(coordinates,theta,timing)
        fine=deliver(coordinates,theta,timing,order=256)
        lower=deliver(coordinates,theta,timing,endpoint='end')
        upper=deliver(coordinates,theta,timing,endpoint='start')
        result=[]
        for i,r in enumerate(coordinates):
            q,err=independent_delivery(r,theta,timing)
            qlo,elo=independent_delivery(r,theta,timing,endpoint='end')
            qhi,ehi=independent_delivery(r,theta,timing,endpoint='start')
            allowance=max(abs(y[i]-fine[i]),abs(y[i]-q)+err,
                          abs(lower[i]-qlo)+elo,abs(upper[i]-qhi)+ehi)
            if lower[i]>y[i]+1e-12 or y[i]>upper[i]+1e-12:
                raise FloatingPointError('endpoint order failure')
            result.append(dict(**r,yhat_g=float(y[i]),endpoint_lower_g=float(lower[i]),
                endpoint_upper_g=float(upper[i]),numerical_allowance_g=float(allowance)))
        predictions[candidate]=result
    return dict(held_shot=held,timing=timing,training_shots=sorted({r['shot'] for r in training}),
                fits=fitted,predictions=predictions)


def verify_freeze(freeze_path,review_path,source):
    freeze=read_json(freeze_path);review=read_json(review_path)
    if review.get('decision')!='APPROVED_FOR_SCORING' or review.get('freeze_sha256')!=digest(freeze_path):
        raise RuntimeError('independent pre-scoring approval missing or mismatched')
    if digest(source)!=freeze['source_sha256'] or digest(source)!=SOURCE_SHA:
        raise RuntimeError('source identity mismatch')
    for path,sha in freeze['files'].items():
        if digest(ROOT/path)!=sha:
            raise RuntimeError('frozen software/protocol changed: '+path)
    return freeze


def run_predictions(source,freeze_path,review_path,out):
    freeze=verify_freeze(freeze_path,review_path,source)
    if out.exists():
        raise FileExistsError('use a new immutable prediction directory')
    out.mkdir()
    records=parse_source(source); manifests={};primary={}
    for treatment,(zero,timing) in TREATMENTS.items():
        rows=observations(records,zero)
        for held in range(1,14):
            print(treatment,held,flush=True)
            reuse=primary.get(held) if treatment.startswith('time_') else None
            fold=fold_predict(rows,held,timing,reuse)
            if treatment=='primary':
                primary[held]=fold
            name=f'{treatment}-{held:02}.json'
            write_json(out/name,fold)
            manifests[name]=digest(out/name)
    manifest=dict(freeze_sha256=digest(freeze_path),review_sha256=digest(review_path),
        source_sha256=digest(source),files=manifests,environment=environment(),
        software_identity=freeze['software_identity'])
    write_json(out/'manifest.json',manifest)
    for path in out.iterdir():
        path.chmod(0o444)


def environment():
    return dict(python=platform.python_version(),numpy=np.__version__,scipy=scipy.__version__)


def metrics(observed,predicted):
    pred={r['vial']:r for r in predicted}
    use=[r for r in observed if r['eligible'] and r['mass_g']>0]
    residual=np.array([pred[r['vial']]['yhat_g']-r['solute_g'] for r in use])
    errors=np.array([pred[r['vial']]['numerical_allowance_g'] for r in use])
    tdserr=residual/np.array([r['mass_g'] for r in use])*100
    return dict(n_positive=len(use),n_structural_zero=sum(r['mass_g']==0 for r in observed),
        unavailable_vials=[r['vial'] for r in observed if r['solute_g'] is None],
        support='full_regular_window' if all(r['solute_g'] is not None for r in observed) else 'observed_support',
        evaluated_vials=[r['vial'] for r in use],
        vial_rmse_g=float(np.sqrt(np.mean(residual**2))),
        signed_support_total_error_g=float(residual.sum()),
        absolute_support_total_error_g=float(abs(residual.sum())),
        max_abs_cumulative_residual_g=float(np.max(abs(np.cumsum(residual)))),
        tds_rmse_pp=float(np.sqrt(np.mean(tdserr**2))),tds_mean_error_pp=float(tdserr.mean()),
        tds_denominator='eligible positive-beverage-mass vials; per-vial measured g',
        rmse_allowance_g=float(np.sqrt(np.mean(errors**2))),
        cumulative_allowance_g=float(errors.sum()),numerical_max_g=float(errors.max()),
        all_prediction_numerical_max_g=max(r['numerical_allowance_g'] for r in predicted))


def comparison(a,b):
    """Candidate a versus comparator b, paired in original shot order."""
    ra=np.array([v['vial_rmse_g'] for v in a]);rb=np.array([v['vial_rmse_g'] for v in b])
    ta=np.array([v['absolute_support_total_error_g'] for v in a])
    tb=np.array([v['absolute_support_total_error_g'] for v in b])
    conditions=dict(relative_20_percent=bool(ra.mean()<=.8*rb.mean()),
        absolute_005_g=bool(rb.mean()-ra.mean()>=.005),
        paired_75_percent=bool(sum(ra<rb)>=math.ceil(.75*len(ra))),
        total_non_deterioration=bool(ta.mean()-tb.mean()<=.05))
    return dict(conditions=conditions,material=all(conditions.values()),
        candidate_mean_rmse_g=float(ra.mean()),comparator_mean_rmse_g=float(rb.mean()),
        mean_rmse_reduction_g=float(rb.mean()-ra.mean()),
        relative_reduction=float(1-ra.mean()/rb.mean()) if rb.mean() else None,
        shots_improved=int(sum(ra<rb)),required_shots=math.ceil(.75*len(ra)),
        mean_absolute_total_deterioration_g=float(ta.mean()-tb.mean()),
        paired_candidate_minus_comparator_rmse_g=(ra-rb).tolist())


def decisions(group):
    agg={}
    for model,rows in group.items():
        passes=sum(r['vial_rmse_g']<=.05 and r['max_abs_cumulative_residual_g']<=.20 for r in rows)
        agg[model]=dict(mean_vial_rmse_g=float(np.mean([r['vial_rmse_g'] for r in rows])),
            mean_absolute_support_total_error_g=float(np.mean([r['absolute_support_total_error_g'] for r in rows])),
            adequate_shots=passes,required_shots=math.ceil(.75*len(rows)),adequate=passes>=math.ceil(.75*len(rows)))
    comparisons={a+'_vs_'+b:comparison(group[a],group[b]) for a,b in
                 [('MASS','TIME'),('MIXED','TIME'),('MIXED','MASS'),('TIME','TEMPLATE'),('MASS','TEMPLATE'),('MIXED','TEMPLATE')]}
    for m in ('TIME','MASS','MIXED'):
        agg[m]['competitive_with_template']=(agg[m]['adequate'] and
            agg[m]['mean_vial_rmse_g']<=agg['TEMPLATE']['mean_vial_rmse_g']+.005 and
            agg[m]['mean_absolute_support_total_error_g']<=agg['TEMPLATE']['mean_absolute_support_total_error_g']+.05)
    return dict(aggregate=agg,comparisons=comparisons,
        mass_increment=comparisons['MASS_vs_TIME']['material'],
        mixed_increment=agg['MIXED']['adequate'] and comparisons['MIXED_vs_TIME']['material'] and comparisons['MIXED_vs_MASS']['material'])


def numerical_decision_stability(group,nominal):
    """Conservative metric boxes; decisions unresolved if any corner can differ.

    Per-model coherent +/- corners also enclose paired comparison worst cases;
    all 16 corners include candidate-high/comparator-low and reverse.
    """
    import itertools
    from copy import deepcopy
    def signature(result):
        return (result['mass_increment'],result['mixed_increment'],
                tuple((v['adequate'],v.get('competitive_with_template')) for v in result['aggregate'].values()),
                tuple(tuple(c['conditions'].values()) for c in result['comparisons'].values()))
    sig=signature(nominal)
    for signs in itertools.product((-1,1),repeat=4):
        altered=deepcopy(group)
        for (model,rows),sign in zip(altered.items(),signs):
            for r in rows:
                r['vial_rmse_g']=max(0,r['vial_rmse_g']+sign*r['rmse_allowance_g'])
                for key in ('absolute_support_total_error_g','max_abs_cumulative_residual_g'):
                    r[key]=max(0,r[key]+sign*r['cumulative_allowance_g'])
        if signature(decisions(altered))!=sig:
            return False
    return True


def score(source,bundle,out):
    manifest=read_json(bundle/'manifest.json')
    if digest(source)!=manifest['source_sha256']:
        raise RuntimeError('scoring source mismatch')
    for name,sha in manifest['files'].items():
        if digest(bundle/name)!=sha:
            raise RuntimeError('immutable prediction mismatch')
    # Claim once-only before accessing any comparative metric; a failure is retained.
    out.mkdir()
    write_json(out/'score_receipt.json',dict(prediction_manifest_sha256=digest(bundle/'manifest.json')))
    records=parse_source(source);results={}
    for treatment,(zero,timing) in TREATMENTS.items():
        observations_all=observations(records,zero);group={m:[] for m in ('TIME','MASS','MIXED','TEMPLATE')}
        failures=[]
        for held in range(1,14):
            fold=read_json(bundle/f'{treatment}-{held:02}.json')
            obs=[r for r in observations_all if r['shot']==held]
            for model in group:
                pred=fold['predictions'][model]
                if pred is None:
                    failures.append(dict(shot=held,model=model));continue
                group[model].append(dict(shot=held,**metrics(obs,pred)))
        result=dict(per_shot=group,failures=failures,expected_shots=13,
                    disposition='NUMERICALLY_UNRESOLVED',
                    unresolved_reason='failed folds; no denominator reduction' if failures else None)
        if not failures:
            result.update(decisions(group))
            result['numerically_qualified']=all(r['all_prediction_numerical_max_g']<NUM_TOL for rows in group.values() for r in rows)
            result['decision_stable_to_numerical_allowance']=numerical_decision_stability(group,result)
            if result['numerically_qualified'] and result['decision_stable_to_numerical_allowance']:
                result['disposition']='NUMERICALLY_QUALIFIED'
                result['scientific_dispositions']=dict(
                    adequacy={m:('ADEQUATE_FOR_DECLARED_SUPPORT' if v['adequate'] else
                                 'TESTED_FORM_INADEQUATE') for m,v in result['aggregate'].items()},
                    mass_increment=('MASS_CLOCK_GAIN_UNDER_DECLARED_CONDITIONS' if result['mass_increment']
                                    else 'NO_MATERIAL_MASS_CLOCK_GAIN'),
                    mixed_increment=('MIXED_CLOCK_COMPLEXITY_EARNED_UNDER_DECLARED_CONDITIONS'
                                     if result['mixed_increment'] else 'MIXED_CLOCK_COMPLEXITY_NOT_EARNED'),
                    template_competitiveness={m:('COMPACT_PREDICTOR_COMPETITIVE_WITH_TEMPLATE'
                        if result['aggregate'][m]['competitive_with_template'] else 'NO_ESTABLISHED_ADVANTAGE')
                        for m in ('TIME','MASS','MIXED')})
            else:
                result['unresolved_reason']='integration target or numerical decision stability failed; nominal diagnostics only'
        if result['disposition']=='NUMERICALLY_UNRESOLVED':
            result['scientific_dispositions']={key:'NUMERICALLY_UNRESOLVED' for key in
                ('adequacy','mass_increment','mixed_increment','template_competitiveness')}
        results[treatment]=result
    write_json(out/'scores.json',results)
    (out/'scores.json').chmod(0o444)
    return results


def report(bundle,scores,out,source):
    """Private row-level plots; permitted aggregate results exported separately."""
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    out.mkdir()
    results=read_json(scores/'scores.json')
    observations_all=observations(parse_source(source))
    fig,axes=plt.subplots(2,2,figsize=(10,8))
    residual_fig,residual_axes=plt.subplots(2,2,figsize=(10,8))
    for ax,rx,model in zip(axes.flat,residual_axes.flat,('TIME','MASS','MIXED','TEMPLATE')):
        for held in range(1,14):
            fold=read_json(bundle/f'primary-{held:02}.json')
            if fold['predictions'][model] is None:
                ax.text(.02,.98-.05*(held-1),f'shot {held}: FAILED',transform=ax.transAxes,va='top')
                rx.text(.02,.98-.05*(held-1),f'shot {held}: FAILED',transform=rx.transAxes,va='top')
                continue
            pred={r['vial']:r for r in fold['predictions'][model]}
            obs=[r for r in observations_all if r['shot']==held and r['eligible']]
            y=np.array([r['solute_g'] for r in obs])
            yh=np.array([pred[r['vial']]['yhat_g'] for r in obs])
            ax.scatter(y,yh,s=12,alpha=.7)
            rx.plot([r['vial'] for r in obs],np.cumsum(yh-y),'.-',lw=.7)
            for r in observations_all:
                if r['shot']==held and r['solute_g'] is None:
                    rx.axvline(r['vial'],color='grey',alpha=.1)
        ax.plot([0,.5],[0,.5],'k:',lw=.7)
        ax.set(title=model,xlabel='Observed vial solute (g)',ylabel='Held-shot prediction (g)')
        rx.axhline(0,color='black',lw=.5)
        rx.set(title=model,xlabel='Vial position (nominal 2 s)',ylabel='Cumulative residual over observed support (g)')
    fig.suptitle('Primary: '+results['primary']['disposition']+'; 180 eligible vials / 26 structural zeros')
    residual_fig.suptitle('Primary: gaps at shot 6/vial 3 and shot 13/vial 2 omitted; grey marks gaps')
    fig.tight_layout();fig.savefig(out/'predicted_observed.png');plt.close(fig)
    residual_fig.tight_layout();residual_fig.savefig(out/'cumulative_residuals.png');plt.close(residual_fig)
    fig,ax=plt.subplots(figsize=(8,4))
    for model in ('TIME','MASS','MIXED','TEMPLATE'):
        rows=results['primary']['per_shot'][model]
        ax.plot([r['shot'] for r in rows],[r['vial_rmse_g'] for r in rows],'.-',label=model)
    ax.axhline(.05,color='black',ls=':');ax.set(xlabel='Held shot (original block)',ylabel='Vial solute RMSE (g)',title='Held-shot positive-mass observed support; 2 chemistry gaps')
    ax.legend();fig.tight_layout();fig.savefig(out/'paired_errors.png');plt.close(fig)
    fig,ax=plt.subplots(figsize=(8,4))
    for model in ('TIME','MASS','MIXED','TEMPLATE'):
        ax.plot(list(results),[results[t].get('aggregate',{}).get(model,{}).get('mean_vial_rmse_g',np.nan) for t in results],'.-',label=model)
    ax.set(ylabel='Equal-shot mean RMSE (g)',title='Bounded zero/timing sensitivities; extra cohort unqualified')
    ax.legend();fig.tight_layout();fig.savefig(out/'sensitivities.png');plt.close(fig)
    public={t:{k:v for k,v in result.items() if k not in ('per_shot','comparisons')} for t,result in results.items()}
    for t in public:
        public[t]['comparisons']={k:{kk:vv for kk,vv in v.items() if not kk.startswith('paired_')} for k,v in results[t].get('comparisons',{}).items()}
    write_json(out/'aggregate.json',public)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('operation',choices=['audit','fit-predict','score','report'])
    p.add_argument('--source',type=Path);p.add_argument('--out',type=Path,required=True)
    p.add_argument('--freeze',type=Path);p.add_argument('--review',type=Path)
    p.add_argument('--bundle',type=Path);p.add_argument('--scores',type=Path)
    a=p.parse_args()
    if a.operation=='audit':
        a.out.mkdir();audit(a.source,a.out)
    elif a.operation=='fit-predict':
        run_predictions(a.source,a.freeze,a.review,a.out)
    elif a.operation=='score':
        score(a.source,a.bundle,a.out)
    else:
        report(a.bundle,a.scores,a.out,a.source)


if __name__=='__main__':
    main()
