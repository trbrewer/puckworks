"""Bounded task CLI: qualify, verify, freeze, predict, score (separate phases).

Target concentrations are read only by qualification/scoring; calibrate() accepts
explicit deep arrays, and predict() accepts geometry plus mass support only.
"""
import argparse
import csv
import hashlib
import json
from pathlib import Path
import time
import platform
import numpy as np
import scipy
from scipy.optimize import least_squares
from . import moroney_transfer as model

ROOT=Path(__file__).resolve().parents[2]
DOC=ROOT/'docs/analysis/sci_md_moroney_transfer_001'
DATA=ROOT/'puckworks/data/moroney2015'
F3='fig03_cylindrical_chamber_profiles.csv'
F11='fig11_bed_mass_comparison.csv'
F7='fig07_cylindrical_model_vs_experiment.csv'


def digest(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_json(path,obj):
    Path(path).write_text(json.dumps(obj,indent=2,allow_nan=False)+'\n')


def rows(filename):
    return list(csv.DictReader(x for x in (DATA/filename).read_text().splitlines() if not x.startswith('#')))


def qualify():
    """Immutable row identities; candidate exclusions require original-PDF evidence."""
    known={('a','JK_60g_2.3bar_250ml_min','189.87','206.498'),
           ('a','JK_12.5g_0.5bar_250ml_min','190.06','161.812'),
           ('b','JK_60g_2.3bar_250ml_min','179.87','201.501'),
           ('b','JK_12.5g_0.5bar_250ml_min','180.05','156.815')}
    result=[]
    for name in [F3,F11,F7]:
        for i,r in enumerate(rows(name),1):
            role='observation'; status='accepted'; evidence='canonical Fig3 JK deep'
            if name==F3 and r['panel'] not in ['a','b']:
                status='excluded'; evidence='Cimbali outside primary fold'
            elif name==F11:
                key=(r['panel'],r['series'],r['Mbrew_g'],r['concentration_mg_per_g'])
                if key in known:
                    role='suspected_legend'; status='excluded_pending_pdf_confirmation'; evidence='owner identified suspected legend coordinate; original PDF confirmation required'
                elif '60g_' in r['series']:
                    role='duplicate'; status='excluded'; evidence='Fig11 blue repeats Fig3 JK deep lineage'
                else: evidence='Fig11 JK shallow target only'
            elif name==F7:
                role='model' if r['type']=='model' else 'duplicate'
                status='reference_only'; evidence='source model reproduction or duplicate Fig3; never calibration target'
            result.append(dict(file=name,source_sha256=digest(DATA/name),row_id=f'{name}:data:{i}',
                               row_number=i,status=status,role=role,evidence=evidence))
    # Confirmation is an independently inspectable object-evidence file, not residual screening.
    proof=DOC/'source_objects.json'
    if proof.exists():
        d=json.loads(proof.read_text())
        for r in result:
            if r['row_id'] in d.get('confirmed_legend_rows',[]):
                r['status']='excluded'; r['role']='legend'; r['evidence']='original PDF page 233 legend symbol; see source_objects.json'
    with (DOC/'qualified_rows.csv').open('w') as f:
        w=csv.DictWriter(f,fieldnames=list(result[0])); w.writeheader(); w.writerows(result)
    return result


def observations(which):
    """Deep-only read for training; target support export discards concentrations."""
    mapping=list(csv.DictReader((DOC/'qualified_rows.csv').open()))
    name=F3 if which=='deep' else F11
    accepted={r['row_id'] for r in mapping if r['file']==name and r['status']=='accepted'}
    out={}
    for panel,kind in [('a','pot'),('b','exit')]:
        rr=[r for i,r in enumerate(rows(name),1) if f'{name}:data:{i}' in accepted and r['panel']==panel]
        out[kind+'_mass']=np.array([float(r['Mbrew_g']) for r in rr])
        out[kind+'_obs']=np.array([float(r['concentration_mg_per_g']) for r in rr])
    return out


def freeze():
    """Freeze files and concentration-free target coordinates; no fits or scoring."""
    mapping=qualify()
    d=observations('shallow')
    write_json(DOC/'target_support.json',{k:v.tolist() for k,v in d.items() if k.endswith('_mass')})
    files=['puckworks/analysis/moroney_transfer.py','puckworks/analysis/moroney_transfer_run.py',
           'tests/test_moroney_transfer.py','docs/analysis/sci_md_moroney_transfer_001/protocol.json',
           'docs/analysis/sci_md_moroney_transfer_001/PROTOCOL.md',
           'docs/analysis/sci_md_moroney_transfer_001/qualified_rows.csv',
           'docs/analysis/sci_md_moroney_transfer_001/target_support.json',
           'docs/analysis/sci_md_moroney_transfer_001/identities.json']
    if (DOC/'source_objects.json').exists(): files.append('docs/analysis/sci_md_moroney_transfer_001/source_objects.json')
    files.extend('puckworks/data/moroney2015/'+x for x in [F3,F11,F7,'table1_batch_simulation_parameters.csv','table2_cylindrical_simulation_parameters.csv'])
    write_json(DOC/'freeze.json',{'files':{p:digest(ROOT/p) for p in files},
               'runtime':runtime_identity(),
               'source_ready':source_ready(mapping),
               'claim':'RETROSPECTIVE_SAME_SOURCE_MODEL_DEVELOPMENT'})


def runtime_identity():
    return {'python':platform.python_version(),'numpy':np.__version__,'scipy':scipy.__version__}


def source_ready(mapping):
    proof=DOC/'source_objects.json'
    if not proof.exists() or any('pending' in r['status'] for r in mapping): return False
    d=json.loads(proof.read_text())
    if len(d.get('pdf_sha256',''))!=64: return False
    for figure,panels,page in [('fig3',['a','b'],219),('fig11',['a','b'],233)]:
        audit=d.get('audits',{}).get(figure,{})
        if (audit.get('printed_page')!=page or audit.get('panels')!=panels
                or audit.get('visual_confirmation') is not True
                or not audit.get('axis_coordinates') or not audit.get('marker_objects')
                or not audit.get('classification_evidence')): return False
    return True


def verify_frozen_dependencies():
    f=json.loads((DOC/'freeze.json').read_text())
    for p,h in f['files'].items():
        if digest(ROOT/p)!=h: raise ValueError('frozen input changed: '+p)
    if not f['source_ready']: raise ValueError('original figure-object qualification incomplete')
    if f.get('runtime')!=runtime_identity(): raise ValueError('frozen numerical environment changed')
    return f


def require_review(review):
    verify_frozen_dependencies()
    r=json.loads(Path(review).read_text())
    if r.get('decision')!='APPROVED_FOR_SCORING' or r.get('freeze_sha256')!=digest(DOC/'freeze.json') or not r.get('reviewer') or not r.get('thresholds_accepted'):
        raise ValueError('independent pre-scoring approval absent or does not bind this freeze')


def transformed_empirical(x):
    y,a,lb,ld=x
    b1=np.exp(lb)
    return [y,a,b1,b1+np.exp(ld)]


def calibrate(training,config,family=None):
    """No target argument or target source read. Retains every deterministic start."""
    em,eo,pm,po=[training[k] for k in ['exit_mass','exit_obs','pot_mass','pot_obs']]
    support=np.unique(np.r_[0,em,pm])
    w=np.sqrt(model.mass_weights(em))
    wp=np.sqrt(model.mass_weights(pm))
    counter={'solver_calls':0,'failures':0,'nfev':0,'failure_records':[]}
    start_id=None
    empirical=family is None
    if empirical:
        starts=config['empirical_starts']; bounds=config['empirical_bounds']
    else:
        starts=config['mechanistic_starts']; bounds=config['mechanistic_bounds']
    records=[]; begin=time.perf_counter()
    def predict(x):
        counter['solver_calls']+=1
        if empirical: return model.empirical(support,transformed_empirical(x))
        p=model.solve(mass_g=support,n=config['fit_cells'],alpha=np.exp(x[0]),beta=np.exp(x[1]),split=x[2],**family)
        counter['nfev']+=p['nfev']; return p
    def residual(x):
        try:
            p=predict(x)
        except (ValueError,RuntimeError,FloatingPointError) as exc:
            counter['failure_records'].append({'start':start_id,'parameters':np.asarray(x).tolist(),'reason':str(exc)})
            counter['failures']+=1
            return np.full(len(em)+len(pm),1e6)
        e=(np.interp(em,support,p['exit_mg_g'])-eo)/5
        s=(np.interp(pm,support,p['delivered_g'])-model.pot_delivery(pm,po))/model.DEEP.dry_g*100
        return np.r_[w*e,config['pot_objective_weight']*wp*s]
    for i,start in enumerate(starts):
        start_id=i
        try:
            fit=least_squares(residual,start,bounds=bounds,max_nfev=config['max_nfev'],
                              ftol=1e-6,xtol=1e-6,gtol=1e-6,diff_step=1e-3)
            pars=transformed_empirical(fit.x) if empirical else [float(np.exp(fit.x[0])),float(np.exp(fit.x[1])),float(fit.x[2])]
            records.append(dict(start=i,x=fit.x.tolist(),parameters=pars,cost=float(2*fit.cost),
                                success=bool(fit.success),status=int(fit.status),message=fit.message,
                                evaluations=int(fit.nfev),boundary=fit.active_mask.tolist()))
        except (ValueError,RuntimeError) as e:
            records.append(dict(start=i,success=False,message=str(e)))
    eligible=[r for r in records if r.get('success') and r.get('cost',1e12)<1e10]
    if not eligible: return dict(records=records,selected=None,cost=counter,elapsed_s=time.perf_counter()-begin)
    best=min(eligible,key=lambda r:r['cost'])
    admitted=[r['start'] for r in eligible if r['cost']<=best['cost']*1.05+.01]
    return dict(records=records,selected=best['start'],admitted=admitted,cost=counter,elapsed_s=time.perf_counter()-begin)


def predict(review,out):
    require_review(review)
    out=Path(out); out.mkdir(parents=True,exist_ok=False)
    cfg=json.loads((DOC/'protocol.json').read_text())
    training=observations('deep')
    support=json.loads((DOC/'target_support.json').read_text())
    coordinates=[np.asarray(v)*p['mass_factor'] for v in list(support.values())+[training['exit_mass'],training['pot_mass']] for p in cfg['source_perturbations']]
    mass=np.unique(np.concatenate([np.linspace(0,max(x.max() for x in coordinates),1001)]+coordinates))
    fits={}; predictions={}; diagnostics={}
    begin=time.perf_counter()
    for perturb in cfg['source_perturbations']:
        tr={k:v.copy() for k,v in training.items()}
        for k in tr:
            tr[k]*=perturb['mass_factor'] if k.endswith('_mass') else perturb['concentration_factor']
            if k.endswith('_obs'): tr[k]+=perturb['concentration_offset_mg_g']
        variants=[('empirical',None)]+[(f['id'],{k:v for k,v in f.items() if k!='id'}) for f in cfg['families']]
        for label,family in variants:
            key=perturb['id']+'/'+label
            print(json.dumps({'phase':'calibration_started','family':key}),flush=True)
            fits[key]=calibrate(tr,cfg,family)
            write_json(out/'calibration.json',fits)  # retain completed work before final freeze
            print(json.dumps({'phase':'calibration_completed','family':key,
                  'selected':fits[key]['selected'],'elapsed_s':fits[key].get('elapsed_s'),
                  'cost':fits[key].get('cost',{})}),flush=True)
            if fits[key]['selected'] is None: continue
            for r in fits[key]['records']:
                if r['start'] not in fits[key]['admitted']: continue
                rid=key+'/'+str(r['start'])
                for c,cond in [('deep',model.DEEP),('shallow',model.SHALLOW)]:
                    if family is None:
                        for scaling in ['N_M','N_T']:
                            p=model.empirical(mass,r['parameters'],cond,scaling)
                            predictions[rid+'/'+scaling+'/'+c]={k:v.tolist() for k,v in p.items() if k!='pot_mg_g'}
                    else:
                        alpha,beta,split=r['parameters']; numer=[]
                        for n in cfg['resolutions']:
                            p=model.solve(cond,mass,n=n,alpha=alpha,beta=beta,split=split,**family)
                            numer.append(p)
                        tight=model.solve(cond,mass,n=cfg['resolutions'][-1],alpha=alpha,beta=beta,split=split,rtol=1e-9,atol=1e-14,**family)
                        finest=numer[-1]
                        diagnostics[rid+'/'+c]={'balance_relative':max(p['balance_relative'] for p in numer+[tight]),
                            'minimum_mass_kg':min(p['minimum_mass_kg'] for p in numer+[tight]),
                            'solver_calls':len(numer)+1,'nfev':sum(p['nfev'] for p in numer+[tight]),
                            'refinement':[{'outlet_rmse_mg_g':float(np.sqrt(np.sum(model.mass_weights((np.array(support['exit_mass']) if c=='shallow' else training['exit_mass'])*perturb['mass_factor'])*np.interp((np.array(support['exit_mass']) if c=='shallow' else training['exit_mass'])*perturb['mass_factor'],mass,p['exit_mg_g']-finest['exit_mg_g'])**2))), 'outlet_max_mg_g':float(np.max(abs(p['exit_mg_g']-finest['exit_mg_g']))),
                              'delivery_max_ey_pp':float(np.max(abs(p['delivered_g']-finest['delivered_g']))/cond.dry_g*100)} for p in numer[:-1]+[tight]]}
                        predictions[rid+'/'+c]={k:finest[k].tolist() for k in ['mass_g','exit_mg_g','delivered_g']}
    write_json(out/'calibration.json',fits); write_json(out/'numerics.json',diagnostics)
    write_json(out/'predictions.json',predictions)
    write_json(out/'prediction_freeze.json',{'protocol_freeze_sha256':digest(DOC/'freeze.json'),
         'files':{p:digest(out/p) for p in ['calibration.json','numerics.json','predictions.json']},
         'review_sha256':digest(review),'elapsed_s':time.perf_counter()-begin,
         'environment':{'python':platform.python_version(),'numpy':np.__version__,'scipy':scipy.__version__},
         'target_concentrations_attached':False})


def score(out):
    out=Path(out)
    if (out/'scores.json').exists(): raise ValueError('already scored; no retuning/re-score')
    verify_frozen_dependencies()
    lock=json.loads((out/'prediction_freeze.json').read_text())
    if lock['protocol_freeze_sha256']!=digest(DOC/'freeze.json'): raise ValueError('protocol changed')
    for p,h in lock['files'].items():
        if digest(out/p)!=h: raise ValueError('prediction bundle changed')
    data={'deep':observations('deep'),'shallow':observations('shallow')}
    predictions=json.loads((out/'predictions.json').read_text()); scores={}
    for key,p in predictions.items():
        cond=key.split('/')[-1]; c=model.DEEP if cond=='deep' else model.SHALLOW
        d=data[cond]
        perturb=next(x for x in json.loads((DOC/'protocol.json').read_text())['source_perturbations'] if x['id']==key.split('/')[0])
        d={k:v*perturb['mass_factor'] if k.endswith('_mass') else v*perturb['concentration_factor']+perturb['concentration_offset_mg_g'] for k,v in d.items()}
        scores[key]=model.metrics(p,d['exit_mass'],d['exit_obs'],d['pot_mass'],d['pot_obs'],c.dry_g)
        cfg=json.loads((DOC/'protocol.json').read_text())
        family=next((f for f in cfg['families'] if f['id']==key.split('/')[1]),None)
        basis=family['basis'] if family else 'dose'
        wash=c.rho_kg_m3*1000*model.volumes(c,basis)['mobile_m3']
        scores[key]['wash_through_reference_basis']=basis
        scores[key]['wash_through_mass_g']=wash
        for label,mask in [('early',d['exit_mass']<=wash),('post_wash',d['exit_mass']>wash)]:
            e=np.interp(d['exit_mass'][mask],p['mass_g'],p['exit_mg_g'])-d['exit_obs'][mask]
            scores[key][label+'_rmse_mg_g']=float(np.sqrt(np.mean(e**2))) if len(e) else None
    write_json(out/'scores.json',{'prediction_freeze_sha256':digest(out/'prediction_freeze.json'),'scores':scores})
    decide(out,scores)
    figures(out)


def verify(out):
    """Representative controls at three declared meshes, without observations."""
    cfg=json.loads((DOC/'protocol.json').read_text()); results={}
    for profile in ['uniform','linear']:
        for c in [model.DEEP,model.SHALLOW]:
            pred=[model.solve(c,n=n,profile=profile) for n in cfg['resolutions']]
            fine=pred[-1]
            results[f'{c.dose_g}/{profile}']={'mass_balance_relative':max(p['balance_relative'] for p in pred),
                'outlet_mesh_difference_mg_g':[float(np.max(abs(p['exit_mg_g']-fine['exit_mg_g']))) for p in pred[:-1]],
                'delivery_mesh_difference_ey_pp':[float(np.max(abs(p['delivered_g']-fine['delivered_g'])))/c.dry_g*100 for p in pred[:-1]],
                'nfev':sum(p['nfev'] for p in pred)}
    write_json(out,results)


def decide(out,scores):
    """Preserve hierarchy: parameter alternatives, readout, numerical allowance."""
    numer=json.loads((out/'numerics.json').read_text())
    fits=json.loads((out/'calibration.json').read_text())
    cfg=json.loads((DOC/'protocol.json').read_text())
    def allowance(key):
        if key not in numer: return (0.,0.)
        rr=numer[key]['refinement'][1:]  # adjacent finest + tightened tolerance
        return tuple(max(r[k] for r in rr) for k in ['outlet_rmse_mg_g','delivery_max_ey_pp'])
    def interval(keys,metric,index):
        return (min(scores[k][metric]-allowance(k)[index] for k in keys),
                max(scores[k][metric]+allowance(k)[index] for k in keys))
    def within(iv,limit):
        return 'PASS' if iv[1]<=limit else ('FAIL' if iv[0]>limit else 'UNRESOLVED')
    def adequacy(keys):
        return [within(interval(keys,'outlet_rmse_mg_g',0),5),
                within(interval(keys,'cumulative_max_ey_pp',1),1)] if keys else ['NOT_AVAILABLE']*2
    def fit_complete(label, empirical=False):
        for p in cfg['source_perturbations']:
            prefix=p['id']+'/'+label; fit=fits.get(prefix,{})
            if fit.get('selected') is None or not fit.get('admitted'): return False
            for start in fit['admitted']:
                for mode in (['N_M/','N_T/'] if empirical else ['']):
                    for cond in ['deep','shallow']:
                        if f'{prefix}/{start}/{mode}{cond}' not in scores: return False
        return True
    baseline_complete=fit_complete('empirical',True)
    baseline_report={}
    for mode in ['N_M','N_T']:
        b=[k for k in scores if '/empirical/' in k and '/'+mode+'/' in k]
        baseline_report[mode]={'coverage':'COMPLETE' if baseline_complete else 'INCOMPLETE',
            'deep_adequacy':adequacy([k for k in b if k.endswith('/deep')]),
            'shallow_adequacy':adequacy([k for k in b if k.endswith('/shallow')])}
    def instance(d,t,perturb):
        numeric=all(k in numer and allowance(k)[0]<=.5 and allowance(k)[1]<=.1
                    and numer[k]['balance_relative']<=1e-6 for k in [d,t])
        deep=adequacy([d]); target=adequacy([t]); gains={}
        ti=interval([t],'outlet_rmse_mg_g',0); si=interval([t],'cumulative_max_ey_pp',1)
        for mode in ['N_M','N_T']:
            b=[k for k in scores if k.startswith(perturb+'/empirical/') and k.endswith('/'+mode+'/shallow')]
            if not baseline_complete or not b: gains[mode]='UNRESOLVED'; continue
            bi=interval(b,'outlet_rmse_mg_g',0); bs=interval(b,'cumulative_max_ey_pp',1)
            margins=(bi[0]*.8-ti[1],bi[0]-ti[1]-1,bs[0]+.1-si[1])
            possible=(bi[1]*.8-ti[0],bi[1]-ti[0]-1,bs[1]+.1-si[0])
            gains[mode]='PASS' if min(margins)>=0 else ('FAIL' if min(possible)<0 else 'UNRESOLVED')
        if not numeric: label='NUMERICALLY_UNRESOLVED'
        elif 'FAIL' in deep: label='CALIBRATION_INADEQUATE'
        elif 'UNRESOLVED' in deep: label='UNRESOLVED'
        elif 'FAIL' in target: label='TESTED_TRANSFER_FAMILY_INADEQUATE'
        elif 'UNRESOLVED' in target+list(gains.values()): label='UNRESOLVED'
        elif all(x=='PASS' for x in gains.values()): label='TRANSFER_ADVANTAGE_FOR_TESTED_SOURCE_CONDITIONS'
        else: label='TRANSFER_ADEQUATE_NO_MATERIAL_ADVANTAGE'
        return {'numerics':'PASS' if numeric else 'UNRESOLVED','deep_adequacy':deep,
                'shallow_adequacy':target,'baseline_gain':gains,'overall':label}
    details={}
    for family in cfg['families']:
        label=family['id']
        if not fit_complete(label):
            details[label]={'overall':'CALIBRATION_INADEQUATE','coverage':'INCOMPLETE'}; continue
        instances={}; within_source_disagreement=False
        for perturb in cfg['source_perturbations']:
            prefix=perturb['id']+'/'+label
            for start in fits[prefix]['admitted']:
                rid=f'{prefix}/{start}'
                instances[f"{perturb['id']}/{start}"]=instance(rid+'/deep',rid+'/shallow',perturb['id'])
            here={v['overall'] for k,v in instances.items() if k.startswith(perturb['id']+'/')}
            established=here-{'UNRESOLVED','NUMERICALLY_UNRESOLVED'}
            within_source_disagreement |= len(established)>1
        labels={v['overall'] for v in instances.values()}
        if 'NUMERICALLY_UNRESOLVED' in labels: overall='NUMERICALLY_UNRESOLVED'
        elif within_source_disagreement: overall='INITIALIZATION_OR_PARAMETER_LIMITED'
        elif len(labels)==1: overall=next(iter(labels))
        else: overall='UNRESOLVED'  # source readout or numerical threshold straddling
        t=[k for k in scores if '/'+label+'/' in k and k.endswith('/shallow')]
        details[label]={'coverage':'COMPLETE','instances':instances,'parameter_decision_varies':within_source_disagreement,
            'source_or_threshold_decision_varies':len(labels)>1 and not within_source_disagreement,
            'outlet_interval_mg_g':interval(t,'outlet_rmse_mg_g',0),
            'cumulative_interval_ey_pp':interval(t,'cumulative_max_ey_pp',1),'overall':overall}
    labels={v['overall'] for v in details.values()}
    established=labels-{'UNRESOLVED','NUMERICALLY_UNRESOLVED'}
    if 'NUMERICALLY_UNRESOLVED' in labels: overall='NUMERICALLY_UNRESOLVED'
    elif len(established)>1 or 'INITIALIZATION_OR_PARAMETER_LIMITED' in labels:
        overall='INITIALIZATION_OR_PARAMETER_LIMITED'
    elif 'UNRESOLVED' in labels: overall='UNRESOLVED'
    else: overall=next(iter(labels))
    by_basis={basis:sorted({details[f['id']]['overall'] for f in cfg['families'] if f['basis']==basis})
              for basis in sorted({f['basis'] for f in cfg['families']})}
    write_json(out/'decisions.json',{'observation_contract':'QUALIFIED_FOR_DECLARED_USE',
        'baselines':baseline_report,'families':details,'volume_basis_decisions':by_basis,
        'initialization_parameter_sensitivity':'DECISION_VARIES' if len(established)>1 or any(v.get('parameter_decision_varies') for v in details.values()) else 'NO_ESTABLISHED_DECISION_DIFFERENCE',
        'overall':overall,'physical_validation':'NOT_ESTABLISHED','successor_execution':False})


def figure_data(out):
    return {'predictions':json.loads((Path(out)/'predictions.json').read_text())}


def figures(out):
    """Task-local VizSpecs; computational lines carry no experimental CI."""
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from puckworks.viz.spec import VizSpec
    from puckworks.public.schema import Producer
    preds=json.loads((out/'predictions.json').read_text())
    fits=json.loads((out/'calibration.json').read_text())
    data={c:observations(c) for c in ['deep','shallow']}
    specs=[]
    for i,title in enumerate(['Outlet concentration','Cumulative delivered solute','Startup and calibration sensitivity'],1):
        spec=VizSpec(id=f'moroney-transfer-{i}',title=title,class_=1,
            producer=Producer(module='puckworks.analysis.moroney_transfer_run',function='figure_data',result_map={'predictions':'predictions'},kwargs={'out':str(out)}),badge='EXPLORATORY_SIMULATION',
            evidence_strength='held out within the same campaign',
            fidelity_ceiling='Retrospective same-source conditional comparison; no espresso physical validation.',
            render_fn='puckworks.analysis.moroney_transfer_run:figures',components=[],caption='Markers: digitized observations. Lines: conditional predictions; no experimental confidence band.')
        assert not spec.validate(); specs.append(spec.to_dict())
        fig,axes=plt.subplots(1,2,figsize=(12,4.8))
        for ax,cond in zip(axes,['deep','shallow']):
            for key,p in preds.items():
                if not key.endswith('/'+cond): continue
                parts=key.split('/'); perturb,label,start=parts[:3]
                if i<3 and (perturb!='central' or int(start)!=fits[perturb+'/'+label]['selected']): continue
                name='/'.join(parts[1:-1]); empirical=label=='empirical'
                if i==3 and empirical: continue
                ax.plot(p['mass_g'],p['delivered_g'] if i==2 else p['exit_mg_g'],
                        label=name,alpha=.85 if i<3 else .45,lw=1.3,ls='--' if empirical else '-')
            d=data[cond]; kind='pot' if i==2 else 'exit'
            obs=model.pot_delivery(d['pot_mass'],d['pot_obs']) if i==2 else d['exit_obs']
            ax.scatter(d[kind+'_mass'],obs,marker='o',s=22,facecolors='none',edgecolors='black',label='digitized observations',zorder=3)
            ax.set(title=cond+' — '+('calibration' if cond=='deep' else 'retrospective transfer'),xlabel='Delivered beverage mass [g]',ylabel='Delivered solute [g]' if i==2 else 'Outlet concentration [mg/g]')
            if i==1 and cond=='deep':
                rr=[r for r in rows(F7) if r['panel']=='a' and r['type']=='model']
                ax.plot([float(r['Mbrew_kg'])*1000 for r in rr],[float(r['Cexit_kg_m3'])*1000/model.RHO for r in rr],':',color='black',label='published fitted model (reference)')
            # Coordinate-specific deep training extent of each empirical hypothesis.
            maxdeep=float(data['deep'][kind+'_mass'].max())
            if cond=='shallow':
                for mode,end in [('N_M',maxdeep*model.SHALLOW.dry_g/model.DEEP.dry_g),('N_T',maxdeep)]:
                    ax.axvline(end,color='grey',ls=':',lw=.8)
                    ax.text(end,ax.get_ylim()[1]*.8,mode+' training extent',rotation=90,fontsize=7)
            ax.grid(alpha=.2)
        if i<3: axes[1].legend(fontsize=6,ncol=2)
        fig.suptitle(title)
        fig.text(.5,.015,spec.badge_line()+' | retrospective; finite sensitivity family; not physical validation',ha='center',fontsize=8)
        fig.tight_layout(rect=[0,.04,1,.96]); fig.savefig(out/f'figure{i}.png',dpi=170); plt.close(fig)
    write_json(out/'viz_specs.json',specs)


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('phase',choices=['qualify','verify','freeze','predict','score'])
    ap.add_argument('--review'); ap.add_argument('--output',type=Path)
    a=ap.parse_args()
    if a.phase=='qualify': qualify()
    elif a.phase=='freeze': freeze()
    elif a.phase=='verify': verify(a.output or DOC/'verification.json')
    elif a.phase=='predict': predict(a.review,a.output)
    else: score(a.output)


if __name__=='__main__': main()
