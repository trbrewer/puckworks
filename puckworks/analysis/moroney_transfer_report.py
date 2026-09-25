"""Task reporting over frozen Moroney transfer outputs; never fits or selects on target.

Inventory audit replays frozen parameter sets, checks trajectory identity and retains
separate reservoir masses. Summary/plots require the once-only scored bundle.
"""
import argparse
import csv
import json
from pathlib import Path
import time
import numpy as np
from . import moroney_transfer as model, moroney_transfer_run as run


def read(out,name):
    return json.loads((Path(out)/name).read_text())


def checked(out):
    run.verify_frozen_dependencies()
    lock=read(out,'prediction_freeze.json')
    if lock['protocol_freeze_sha256']!=run.digest(run.DOC/'freeze.json'):
        raise ValueError('changed scientific freeze')
    for name,digest in lock['files'].items():
        if run.digest(Path(out)/name)!=digest: raise ValueError('changed frozen prediction input')
    return read(out,'predictions.json'),read(out,'calibration.json'),read(run.DOC,'protocol.json')


def inventory(out):
    """Additional deterministic budget audit, with no target concentration read."""
    out=Path(out)
    if (out/'inventory_audit.json').exists(): raise ValueError('inventory audit already exists')
    preds,fits,cfg=checked(out); records={}; begin=time.perf_counter()
    target=read(run.DOC,'target_support.json'); deep=run.observations('deep')
    for key,p in preds.items():
        perturb,label,start,condition=key.split('/') if '/empirical/' not in key else (None,)*4
        if label is None: continue
        family=next(f for f in cfg['families'] if f['id']==label)
        parameters=next(r['parameters'] for r in fits[perturb+'/'+label]['records'] if r['start']==int(start))
        c=model.DEEP if condition=='deep' else model.SHALLOW
        support=deep if condition=='deep' else target
        factor=next(r['mass_factor'] for r in cfg['source_perturbations'] if r['id']==perturb)
        samples=np.unique(np.r_[0,np.asarray(support['exit_mass'])*factor,np.asarray(support['pot_mass'])*factor])
        m=np.asarray(p['mass_g']);indices=np.searchsorted(m,samples)
        if not np.allclose(m[indices],samples,rtol=0,atol=1e-10): raise ValueError('audit support differs')
        q=model.solve(c,m,n=cfg['resolutions'][-1],alpha=parameters[0],beta=parameters[1],split=parameters[2],**{k:v for k,v in family.items() if k!='id'})
        delta=max(float(np.max(abs(q[k]-np.asarray(p[k])))) for k in ['exit_mg_g','delivered_g'])
        if delta>1e-10: raise ValueError('inventory replay changed frozen trajectory')
        records[key]={'mass_g':m[indices].tolist(),'initial_inventory_g':q['initial_inventory_g'],
            'parameters':parameters,'initialization':family,'balance_relative':q['balance_relative'],
            'minimum_mass_kg':q['minimum_mass_kg'],'nfev':q['nfev'],'trajectory_replay_max_difference':delta,
            **{k:q[k][indices].tolist() for k in ['retained_mobile_g','retained_internal_g','remaining_surface_g','remaining_kernel_solid_g','delivered_g','losses_g']}}
    run.write_json(out/'inventory_audit.json',{'role':'REPLAY_OF_FROZEN_PARAMETERS_NO_REFIT_NO_TARGET_CONCENTRATIONS',
        'prediction_freeze_sha256':run.digest(out/'prediction_freeze.json'),
        'reporter_sha256':run.digest(Path(__file__)),'solver_calls':len(records),
        'nfev':sum(r['nfev'] for r in records.values()),'elapsed_s':time.perf_counter()-begin,'records':records})


def summarize(out):
    out=Path(out);_,fits,cfg=checked(out);scored=read(out,'scores.json')
    if scored['prediction_freeze_sha256']!=run.digest(out/'prediction_freeze.json'): raise ValueError('score identity mismatch')
    scores=scored['scores'];numer=read(out,'numerics.json');rows=[]
    for label in [f['id'] for f in cfg['families']]+['N_M','N_T']:
        empirical=label in ['N_M','N_T'];fit=fits['central/'+('empirical' if empirical else label)]
        row={'candidate':label,'selected_deep_start':fit['selected']}
        if fit['selected'] is not None:
            prefix=f"central/{'empirical' if empirical else label}/{fit['selected']}"+('/'+label if empirical else '')
            for cond in ['deep','shallow']:
                s=scores[prefix+'/'+cond]
                for name in ['outlet_rmse_mg_g','cumulative_max_ey_pp','endpoint_ey_pp','early_rmse_mg_g','post_wash_rmse_mg_g']:
                    if name in s: row[cond+'_'+name]=s[name]
            row['parameters']=next(r['parameters'] for r in fit['records'] if r['start']==fit['selected'])
        rows.append(row)
    fields=list(dict.fromkeys(k for r in rows for k in r))
    with (out/'central_comparison.csv').open('w') as f:
        w=csv.DictWriter(f,fieldnames=fields,lineterminator='\n');w.writeheader();w.writerows(rows)
    mechanisms=[r for k,r in fits.items() if not k.endswith('/empirical')]
    baselines=[r for k,r in fits.items() if k.endswith('/empirical')]
    all_starts=[r for f in fits.values() for r in f['records']]
    summary={'overall':read(out,'decisions.json')['overall'],'central_deep_selected_comparison':rows,
        'scientific_freeze_sha256':run.digest(run.DOC/'freeze.json'),'prediction_freeze_sha256':run.digest(out/'prediction_freeze.json'),
        'reporter_sha256':run.digest(Path(__file__)),'calibrated_families':len(fits),'deterministic_starts_executed':len(all_starts),
        'unsuccessful_starts':sum(not r['success'] for r in all_starts),
        'boundary_hitting_starts':sum(any(r.get('boundary',[])) for r in all_starts),
        'mechanistic_calibration_solver_calls':sum(f['cost']['solver_calls'] for f in mechanisms),
        'mechanistic_calibration_rhs_evaluations':sum(f['cost']['nfev'] for f in mechanisms),
        'calibration_integration_failures':sum(f['cost']['failures'] for f in mechanisms),
        'empirical_function_calls':sum(f['cost']['solver_calls'] for f in baselines),
        'prediction_numerical_solver_calls':sum(n['solver_calls'] for n in numer.values()),
        'prediction_numerical_rhs_evaluations':sum(n['nfev'] for n in numer.values()),
        'prediction_elapsed_s':read(out,'prediction_freeze.json')['elapsed_s'],
        'max_balance_relative':max((n['balance_relative'] for n in numer.values()),default=None),
        'max_adjacent_or_tight_outlet_mg_g':max((r['outlet_rmse_mg_g'] for n in numer.values() for r in n['refinement'][1:]),default=None),
        'max_adjacent_or_tight_delivery_ey_pp':max((r['delivery_max_ey_pp'] for n in numer.values() for r in n['refinement'][1:]),default=None),
        'scope':'RETROSPECTIVE_SAME_SOURCE_MODEL_DEVELOPMENT','physical_validation':'NOT_ESTABLISHED'}
    run.write_json(out/'summary.json',summary)


def figure_data(out):
    return {'predictions':read(out,'predictions.json'),'scores':read(out,'scores.json'),'calibration':read(out,'calibration.json')}


def figures(out):
    """Observed-window views and labelled finite-sensitivity ranges, no refitting."""
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from puckworks.viz.spec import VizSpec
    from puckworks.public.schema import Producer
    out=Path(out);preds,fits,cfg=checked(out);scores=read(out,'scores.json')['scores'];numer=read(out,'numerics.json')
    labels=[f['id'] for f in cfg['families']]+['N_M','N_T'];colors={f:plt.get_cmap('tab10')(i) for i,f in enumerate(labels[:10])};colors.update(N_M='black',N_T='#9c2a82')
    data={c:run.observations(c) for c in ['deep','shallow']};specs=[]
    def candidate_key(label):
        empirical=label in ['N_M','N_T'];base='central/'+('empirical' if empirical else label);start=fits[base]['selected']
        return None if start is None else f'{base}/{start}'+('/'+label if empirical else '')
    for number,title in [(1,'Outlet concentration'),(2,'Cumulative delivered solute'),(3,'Initialization and calibration sensitivity')]:
        spec=VizSpec(id=f'moroney-transfer-{number}',title=title,class_=1,
            producer=Producer(module='puckworks.analysis.moroney_transfer_report',function='figure_data',result_map={k:k for k in ['predictions','scores','calibration']},kwargs={'out':str(out)}),
            badge='EXPLORATORY_SIMULATION',evidence_strength='held out within the same campaign',
            fidelity_ceiling='Retrospective same-source conditional comparison; no espresso physical validation.',
            render_fn='puckworks.analysis.moroney_transfer_report:figures',components=[],
            caption='Markers are digitized observations or declared computations as labelled. Ranges span the finite readout/start family plus numerical allowances, not experimental confidence intervals.')
        assert not spec.validate();specs.append(spec.to_dict())
        fig,axes=plt.subplots(1,2,figsize=(13,6 if number<3 else 7),sharey=number==3)
        if number<3:
            kind='exit' if number==1 else 'pot'
            for ax,cond in zip(axes,['deep','shallow']):
                for label in labels:
                    key=candidate_key(label)
                    if key is None or key+'/'+cond not in preds: continue
                    p=preds[key+'/'+cond];empirical=label in ['N_M','N_T']
                    ax.plot(p['mass_g'],p['exit_mg_g'] if number==1 else p['delivered_g'],color=colors[label],lw=2 if empirical else 1.1,alpha=.95 if empirical else .8,ls='--' if empirical else '-',label=label.replace('_',' '))
                d=data[cond];obs=d['exit_obs'] if number==1 else model.pot_delivery(d['pot_mass'],d['pot_obs'])
                ax.scatter(d[kind+'_mass'],obs,s=22,facecolors='white',edgecolors='black',zorder=5,label='observations')
                end=float(d[kind+'_mass'].max());ax.set_xlim(0,end*1.025)
                ax.set(xlabel='Delivered beverage mass [g]',ylabel='Outlet [mg/g]' if number==1 else 'Delivered solute [g]',title=cond+' — '+('calibration' if cond=='deep' else 'transfer'))
                if cond=='deep' and number==1:
                    rr=[r for r in run.rows(run.F7) if r['panel']=='a' and r['type']=='model'];ax.plot([float(r['Mbrew_kg'])*1000 for r in rr],[float(r['Cexit_kg_m3'])*1000/model.RHO for r in rr],':',color='grey',label='source fitted model reference')
                if cond=='shallow':
                    boundary=float(data['deep'][kind+'_mass'].max())*model.SHALLOW.dry_g/model.DEEP.dry_g
                    ax.axvline(boundary,color='grey',ls=':',lw=.8);ax.text(boundary,ax.get_ylim()[1]*.8,'N_M training extent',rotation=90,fontsize=8)
                ax.grid(alpha=.2)
            handles,names=axes[0].get_legend_handles_labels();fig.legend(handles,names,loc='lower center',bbox_to_anchor=(.5,.035),ncol=4,fontsize=7)
        else:
            for row,label in enumerate(labels):
                keys=[k for k in scores if k.endswith('/shallow') and (('/'+label+'/' in k) if label not in ['N_M','N_T'] else k.endswith('/'+label+'/shallow'))]
                center=candidate_key(label);deep_ok=False
                if center is not None:
                    ds=scores[center+'/deep'];deep_ok=ds['outlet_rmse_mg_g']<=5 and ds['cumulative_max_ey_pp']<=1
                for ax,metric,num_metric in zip(axes,['outlet_rmse_mg_g','cumulative_max_ey_pp'],['outlet_rmse_mg_g','delivery_max_ey_pp']):
                    if not keys: continue
                    values=[scores[k][metric] for k in keys]
                    allowances=[max((r[num_metric] for r in numer[k]['refinement'][1:]),default=0) if k in numer else 0 for k in keys]
                    ax.hlines(row,max(0,min(v-a for v,a in zip(values,allowances))),max(v+a for v,a in zip(values,allowances)),color=colors[label],lw=2)
                    ax.scatter(values,[row]*len(values),s=10,color=colors[label],alpha=.5)
                    if center is not None: ax.scatter(scores[center+'/shallow'][metric],row,marker='o' if deep_ok else 'x',s=45,color=colors[label],zorder=4)
            for ax,budget,xlabel in zip(axes,[5,1],['Shallow outlet RMSE [mg/g]','Shallow maximum delivery error [dry-dose EY pp]']):
                ax.axvline(budget,color='black',ls='--',label='adequacy budget');ax.set_xlabel(xlabel);ax.set_xlim(left=0);ax.grid(axis='x',alpha=.2)
            axes[0].set_yticks(range(len(labels)),[x.replace('_',' ') for x in labels]);axes[0].invert_yaxis()
            fig.text(.5,.065,'Ranges: finite source/start sensitivity + numerical allowance. x: central deep fit exceeds a budget. No confidence intervals.',ha='center',fontsize=8)
        fig.suptitle(title);fig.text(.5,.01,spec.badge_line()+' | retrospective same-source test; PHYSICAL_VALIDATION NOT_ESTABLISHED',ha='center',fontsize=8)
        fig.tight_layout(rect=[0,.19 if number<3 else .1,1,.95]);fig.savefig(out/f'figure{number}.png',dpi=180);plt.close(fig)
    run.write_json(out/'viz_specs.json',specs)


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('phase',choices=['inventory','summary','figures']);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    {'inventory':inventory,'summary':summarize,'figures':figures}[a.phase](a.output)


if __name__=='__main__': main()
