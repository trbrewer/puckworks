"""Paired reports from frozen replays; no fitting or parameter selection."""
import ast
import csv
import hashlib
import io
import json
import subprocess

import numpy as np

from . import joint_pressure_fade_001_evaluate as E
from . import pressure_peak_stage_b0 as B

R, F, O, P = E.R, E.F, E.O, E.P
OUT=R.OUT
LABELS={'saved_A_J1':'Saved A-J1','refreshed_A_J1':'Refreshed A-J1','A_J1_F':'A-J1-F','A_J1_PF':'A-J1-PF'}


def difference_fields(name, points, draws):
    """Primary pressure fade minus refreshed contrast inside identical draws."""
    return O.uncertainty(name,points[3]-points[1],draws[3]-draws[1])


def comparison(observed, observed_draws, points, draws):
    row=O.uncertainty('observed',observed,observed_draws)
    for arm,p,b in zip(R.ARMS,points,draws):
        row.update(O.uncertainty(arm,p,b))
        row.update(O.uncertainty('observed_minus_'+arm,observed-p,observed_draws-b))
    row.update(difference_fields('pressure_fade_minus_refreshed',points,draws))
    row.update(O.uncertainty('pressure_fade_minus_refreshed_absolute_error',
        abs(points[3]-observed)-abs(points[1]-observed),
        abs(draws[3]-observed_draws)-abs(draws[1]-observed_draws)))
    return row


def trajectory_tables(data,records):
    sources=data['sources'];condition=data['condition'];bank=data['draws'];nominal=np.array(list(bank))
    shape=(len(O.SNAPSHOTS),len(sources))
    pressure,observed=np.zeros(shape),np.zeros(shape)
    for j,(clock,target) in enumerate(O.SNAPSHOTS):
        for i,s in enumerate(sources):
            r=data['observed'][s['brew'],clock,target]
            assert r['available']=='True'
            pressure[j,i]=float(r['pressure_bar']);observed[j,i]=float(r['flow_g_s'])
    mp,mq,bp,bq,_=O.condition_statistics(pressure,observed,condition,bank)
    os,obs=O.high_slope(mp,mq,nominal),O.high_slope(bp,bq,nominal)
    lookup={(r['arm'],r['scope'],r['brew']):r for r in records}
    trajectory,late,contributions,numerics=[],[],[],[]
    stats={}
    for scope in R.SCOPES:
        for step in ('fine','search'):
            for component in ('total','liquid','solute'):
                values=[];draws=[]
                for arm in R.ARMS:
                    q=np.array([[lookup[arm,scope,s['brew']][step]['windows'][j][component] for s in sources] for j in range(shape[0])])
                    _,pq,_,pbq,_=O.condition_statistics(pressure,q,condition,bank)
                    values.append(pq);draws.append(pbq)
                stats[scope,step,component]=(np.array(values),np.array(draws))
        values,draws=stats[scope,'fine','total']
        for j,(clock,target) in enumerate(O.SNAPSHOTS):
            ps=np.array([O.high_slope(mp,v,nominal)[j] for v in values])
            pbs=np.array([O.high_slope(bp,b,nominal)[j] for b in draws])
            coarse_slopes=np.array([O.high_slope(mp,v,nominal)[j] for v in stats[scope,'search','total'][0]])
            for i,arm in enumerate(R.ARMS):
                numerics.append(dict(record_type='high_pressure_slope',arm=arm,scope=scope,clock=clock,time_s=target,
                    search=coarse_slopes[i],fine=ps[i],fine_minus_search=ps[i]-coarse_slopes[i],units='g/s/bar'))
            trajectory.append(dict(scope=scope,record_type='high_pressure_slope',clock=clock,time_s=target,
                units='g/s/bar',**comparison(os[j],obs[j],ps,pbs)))
            for k,c in enumerate(nominal):
                trajectory.append(dict(scope=scope,record_type='level',clock=clock,time_s=target,pressure_bar=c,
                    matched_window_pressure_bar=mp[j,k],units='g/s',
                    **comparison(mq[j,k],bq[j,:,k],values[:,j,k],draws[:,j,:,k])))
        phases=[(10,40),(40,60),(60,100)]
        for start,end in phases:
            a=O.SNAPSHOTS.index(('stable_pressure',start));b=O.SNAPSHOTS.index(('stable_pressure',end))
            od,obd=mq[b]-mq[a],bq[b]-bq[a]
            vd,bd=values[:,b]-values[:,a],draws[:,b]-draws[:,a]
            for k,c in enumerate(nominal):
                row=dict(scope=scope,record_type='phase',clock='stable_pressure',start_s=start,end_s=end,
                         pressure_bar=c,units='g/s',**comparison(od[k],obd[:,k],vd[:,k],bd[:,:,k]))
                if c in (9,11,13):
                    trajectory.append(row)
                if (start,end)==(60,100):
                    for arm,value in zip(R.ARMS,vd[:,k]):
                        row[arm+'_direction_error']=('invented_decline' if od[k]>0 and value<0 else
                            'missed_decline' if od[k]<0 and value>=0 else 'same_point_direction')
                    late.append(row)
                for component in ('liquid','solute','total'):
                    vv,bb=stats[scope,'fine',component]
                    points=vv[:,b,k]-vv[:,a,k];boots=bb[:,b,:,k]-bb[:,a,:,k]
                    contributions.append(dict(scope=scope,component=component,start_s=start,end_s=end,
                        pressure_bar=c,**{key:value for arm,point,boot in zip(R.ARMS,points,boots)
                                         for key,value in O.uncertainty(arm,point,boot).items()},
                        **difference_fields('pressure_fade_minus_refreshed',points,boots)))
                coarse=stats[scope,'search','total'][0]
                for i,arm in enumerate(R.ARMS):
                    cv=coarse[i,b,k]-coarse[i,a,k]
                    numerics.append(dict(record_type='phase',arm=arm,scope=scope,pressure_bar=c,start_s=start,end_s=end,
                        search= float(cv),fine=float(vd[i,k]),fine_minus_search=float(vd[i,k]-cv),units='g/s'))
            i,k=list(nominal).index(9.),list(nominal).index(13.)
            trajectory.append(dict(scope=scope,record_type='phase',clock='stable_pressure',start_s=start,end_s=end,
                pressure_bar='9_minus_13',units='g/s',**comparison(od[i]-od[k],obd[:,i]-obd[:,k],vd[:,i]-vd[:,k],bd[:,:,i]-bd[:,:,k])))
        for j,(clock,target) in enumerate(O.SNAPSHOTS):
            for k,c in enumerate(nominal):
                for i,arm in enumerate(R.ARMS):
                    cv=stats[scope,'search','total'][0][i,j,k]
                    numerics.append(dict(record_type='level',arm=arm,scope=scope,clock=clock,time_s=target,pressure_bar=c,
                        search=float(cv),fine=float(values[i,j,k]),fine_minus_search=float(values[i,j,k]-cv),units='g/s'))
    # Exact continuity against #424's retained compact levels, not rounded prose.
    old=R.table(_ARGS.replay/'docs/research/TURNOVER_TIME_REPLAY_001/PREDICTED_BY_TIME.csv')
    for r in old:
        if r['model']!='A-J1':
            continue
        j=O.SNAPSHOTS.index((r['clock'],int(r['time_s'])));k=list(nominal).index(float(r['nominal_pressure_bar']))
        np.testing.assert_allclose(stats[r['scope'],'fine','total'][0][0,j,k],float(r['predicted_beverage_flow_g_s']),rtol=1e-12,atol=1e-12)
    split_csv=subprocess.check_output(['git','show',
        '717d7494efa09de2bcd2249c7186dedb17fa3136:docs/research/TURNOVER_REPLAY_DECOMPOSITION_001/PHASE_CONTRIBUTIONS.csv'],cwd=R.ROOT).decode()
    for old in csv.DictReader(io.StringIO(split_csv)):
        if old['model']!='A-J1':
            continue
        for component in ('liquid','solute','total'):
            row=next(r for r in contributions if r['scope']==old['scope'] and r['component']==component
                and r['pressure_bar']==float(old['nominal_pressure_bar'])
                and r['start_s']==int(old['start_time_s']) and r['end_s']==int(old['end_time_s']))
            for suffix in ('','_lo','_hi'):
                target=old.get(component+'_change_g_s'+suffix)
                if target:
                    np.testing.assert_allclose(row['saved_A_J1'+suffix],float(target),rtol=1e-12,atol=1e-12)
    return trajectory,late,contributions,numerics


def metric_tables(data,records):
    condition=data['condition'];sources=data['sources'];groups,samples=P.paired_samples(condition)
    inherited=_ARGS.joint/'PAIRED_RESAMPLES.json'
    manifest=R.read(R.ROOT/'docs/research/JOINT_CLOCK_001/RUN_MANIFEST.json')
    R.T.checked_hash(inherited,manifest['resamples_sha256'])
    assert samples==R.read(inherited)
    sample_bytes=json.dumps(samples,separators=(',',':')).encode()
    ( _ARGS.work/'J1_RESAMPLES.json').write_bytes(sample_bytes)
    lookup={(r['arm'],r['scope'],r['brew']):r for r in records}
    rows,scores,numerics,onsets,criteria=[],[],[],[],[]
    for scope in R.SCOPES:
        chosen=[[lookup[a,scope,s['brew']] for s in sources] for a in R.ARMS]
        detected=np.array([[r['fine']['observer']['detected'] for r in rr] for rr in chosen])
        for metric in ('endpoint','primary_trace','companion_trace','onset'):
            square=np.array([[r['fine']['errors'][metric] for r in rr] for rr in chosen])
            coarse=np.array([[r['search']['errors'][metric] for r in rr] for rr in chosen])
            values,draws=P.score_and_draws(square,groups,samples)
            cv,_=P.score_and_draws(coarse,groups,samples)
            for subset,ids,point,boot in [('ALL',np.arange(56),values,draws)]+[
                (str(p),g,np.sqrt(square[:,g].mean(axis=1)),
                 np.sqrt(square[:,data['draws'][p]].mean(axis=-1)).T) for p,g in zip(F.J.W.NOMINAL,groups)]:
                for i,arm in enumerate(R.ARMS):
                    n=int(detected[i,ids].sum());bound=metric=='onset' and n<len(ids)
                    scores.append(dict(arm=arm,scope=scope,pressure_bar=subset,metric=metric,value=float(point[i]),
                        units='s' if metric=='onset' else 'g/s',
                        lower_95=float(np.quantile(boot[:,i],.025)),upper_95=float(np.quantile(boot[:,i],.975)),
                        intended=len(ids),available=len(ids),detected=n,is_lower_bound=bound))
                for left,right in ((3,1),(3,2),(2,1),(1,0),(3,0)):
                    bound=metric=='onset' and not detected[[left,right]][:,ids].all()
                    ci=np.quantile(boot[:,left]-boot[:,right],[.025,.975])
                    rows.append(dict(scope=scope,pressure_bar=subset,metric=metric,left=R.ARMS[left],right=R.ARMS[right],
                        units='s' if metric=='onset' else 'g/s',
                        left_value=point[left],right_value=point[right],difference=point[left]-point[right],
                        lower_95=ci[0],upper_95=ci[1],left_detected=int(detected[left,ids].sum()),right_detected=int(detected[right,ids].sum()),
                        intended=len(ids),available=len(ids),interpretation='difference of computed bounds; not a bound on true error difference' if bound else 'paired RMSE difference'))
            for i,arm in enumerate(R.ARMS):
                numerics.append(dict(record_type='cohort_metric',scope=scope,arm=arm,metric=metric,search=cv[i],fine=values[i],fine_minus_search=values[i]-cv[i]))
        for i,arm in enumerate(R.ARMS):
            response=P.response(np.array([r['fine']['endpoint_g_s'] for r in chosen[i]]),
                np.array([s['pressure_bar'][-1] for s in sources]),condition)
            criteria.append(dict(scope=scope,arm=arm,record_type='endpoint_response',**response))
            for s,r in zip(sources,chosen[i]):
                fine,coarse=r['fine']['observer'],r['search']['observer']
                observed=s['observed_onset_for_scoring_only_s']
                onsets.append(dict(scope=scope,arm=arm,brew=s['brew'],pressure_bar=s['nominal_pressure_bar'],observed_s=observed,
                    predicted_s=fine['onset_s'],detected=fine['detected'],censor_bound_s=fine['censor_bound_s'],
                    error_or_bound_s=(fine['onset_s'] if fine['detected'] else fine['censor_bound_s'])-observed))
                numerics.append(dict(record_type='detector',scope=scope,arm=arm,brew=s['brew'],pressure_bar=s['nominal_pressure_bar'],
                    fine=fine['onset_s'],search=coarse['onset_s'],fine_detected=fine['detected'],search_detected=coarse['detected'],
                    detection_changed=fine['detected']!=coarse['detected'],fine_minus_search=fine['onset_s']-coarse['onset_s'] if fine['detected'] and coarse['detected'] else None))
            # Inherited late trend uses its original fine grid/weights, separate
            # from the +60->100 two-window trajectory contrast.
            trends=[]
            ft=np.array(data['fixture']['fine_times_s'])
            for j,r in enumerate(chosen[i]):
                w=np.array(data['fixture']['late_weights'][j]);use=w!=0
                with np.load(_ARGS.work/'predictions'/r['fine']['artifact']) as a:
                    if ft[use].max()>a['time'][-1]:
                        raise ValueError('Missing inherited late trend support')
                    trends.append(float(np.dot(np.interp(ft[use],a['time'],a['bed_flow_g_s']),w[use])))
            for p,g in zip(F.J.W.NOMINAL,groups):
                value=float(np.mean(np.array(trends)[g]));sign=B.mean_trend_sign(value)
                criteria.append(dict(scope=scope,arm=arm,record_type='inherited_late_trend',pressure_bar=p,
                    predicted_g_s_s=value,observed_g_s_s=float(np.mean(np.array(data['fixture']['observed_late_trend'])[g])),
                    sign=sign,resolved_rising_condition=p in (2,3.5,4,5,6),matches_rising=sign=='POSITIVE'))
    return rows,scores,numerics,onsets,criteria,hashlib.sha256(sample_bytes).hexdigest()


def parameter_fields(arm,p,mc):
    mass_gamma=p[4] if arm=='A_J1_F' else 0.
    pressure_gamma=p[4] if arm=='A_J1_PF' else 0.
    row=dict(a=p[0],Pstar=p[1],n=p[2],Pd=p[3],tau0=p[-1],gamma=mass_gamma,
             gamma_Mc=mass_gamma*mc,gamma_P=pressure_gamma,gamma_P_1300=pressure_gamma*1300,Mc_g=mc)
    if arm=='A_J1_F':
        row.update(E.M.regime(mass_gamma,mc))
    return row


def fit_tables(data,index):
    fits,starts,numerics=[],[],[]
    objectives={(r['arm'],r['fold']):r for r in index['objectives']}
    for arm in R.ARMS:
        for fold in data['reference']:
            selected=E.selected(data,_ARGS.work,arm,fold);p=selected['parameters'];obj=objectives[arm,fold]
            assert p==obj['parameters'] and selected['mc_fixed_g']==obj['mc_g']
            model=E.M if arm=='A_J1_F' else F
            z=model.coordinates(p);lo,hi=model.bounds()
            distances={name:dict(lower=float(v-l),upper=float(h-v) if np.isfinite(h) else None,
                at_lower=bool(v==l),at_upper=bool(v==h)) for name,v,l,h in zip(model.ORDER,z,lo,hi)}
            r=dict(arm=arm,fold=fold,**parameter_fields(arm,p,selected['mc_fixed_g']),
                boundary_contacts=distances,reused=arm!='A_J1_PF',
                objective_search=obj['search']['objective'],objective_fine=obj['fine']['objective'],
                training_detected_search=obj['search']['detected'],training_detected_fine=obj['fine']['detected'],
                training_intended=obj['search']['intended'])
            if arm=='A_J1_PF':
                own=[]
                for i in range(19):
                    record=R.read(_ARGS.work/'starts'/f'{arm}_{fold}_{i:02d}.json')
                    assert record['identity']==R.identity()
                    best=record['best'];initial=record['initial_parameters']
                    own.append(best['objective'])
                    starts.append(dict(arm=arm,fold=fold,start=i,origin=record['origin'],
                        initial_parameters=initial,gamma_P=initial[4],gamma_P_1300=record['gamma_P_1300'],
                        final_gamma_P=best['parameters'][4],final_gamma_P_1300=best['parameters'][4]*1300,
                        Mc_g=selected['mc_fixed_g'],initial_objective=record['initial_objective'],
                        best_objective=best['objective'],best_parameters=best['parameters'],
                        returned_objective=record['returned_objective'],success=record['success'],
                        status=record['status'],evaluations=record['evaluations'],
                        cpu_seconds=record['cpu_seconds'],trials_sha256=record['trials_sha256']))
                r.update(winning_start=selected['winning_start'],start_best_min=min(own),start_best_max=max(own),
                         start_objective_spread=max(own)-min(own),optimizer_core_hours=selected['cpu_seconds']/3600)
                r['pressure_fade_minus_refreshed_search']=obj['search']['objective']-objectives['refreshed_A_J1',fold]['search']['objective']
                assert r['pressure_fade_minus_refreshed_search']<=0.
            if arm in ('A_J1_F','A_J1_PF'):
                for step in ('search','fine'):
                    r['frozen_gamma_zero_objective_'+step]=obj['zero_'+step]['objective']
                    r['fade_minus_frozen_zero_'+step]=obj[step]['objective']-obj['zero_'+step]['objective']
                numerics.append(dict(record_type='frozen_gamma_zero_objective',arm=arm,fold=fold,
                    search=obj['zero_search']['objective'],fine=obj['zero_fine']['objective'],
                    fine_minus_search=obj['zero_fine']['objective']-obj['zero_search']['objective'],
                    search_detected=obj['zero_search']['detected'],fine_detected=obj['zero_fine']['detected']))
            fits.append(r)
            numerics.append(dict(record_type='training_objective',arm=arm,fold=fold,search=obj['search']['objective'],fine=obj['fine']['objective'],
                fine_minus_search=obj['fine']['objective']-obj['search']['objective'],search_detected=obj['search']['detected'],fine_detected=obj['fine']['detected']))
    return fits,starts,numerics


def fade_factors(data,index):
    rows=[]
    for fold in data['reference']:
        fit=E.selected(data,_ARGS.work,'A_J1_PF',fold);gamma=fit['parameters'][4]
        for p in F.J.W.NOMINAL:
            rows.append(dict(record_type='constant_nominal_pressure',fold=fold,pressure_bar=p,
                gamma_P=gamma,duration_s=40.,exposure_increment_bar_s=p*40.,fade_factor=float(np.exp(-gamma*p*40.))))
    for r in index['records']:
        if r['arm']!='A_J1_PF':
            continue
        value=r['fine'];exposure=value['exposure_100_bar_s']-value['exposure_60_bar_s']
        rows.append(dict(record_type='recorded_pressure',fold=r['fold'],scope=r['scope'],brew=r['brew'],
            pressure_bar=r['pressure_bar'],gamma_P=r['parameters'][4],duration_s=40.,
            exposure_60_bar_s=value['exposure_60_bar_s'],exposure_100_bar_s=value['exposure_100_bar_s'],
            exposure_increment_bar_s=exposure,fade_factor=value['recorded_late_fade_factor']))
    return rows


def curves_and_peaks(data,records):
    lookup={(r['arm'],r['scope'],r['brew']):r for r in records}
    curves,peaks={},[]
    for scope in R.SCOPES:
        for p in F.J.W.NOMINAL:
            sources=[s for s in data['sources'] if s['nominal_pressure_bar']==p]
            for arm in R.ARMS:
                arrays=[]
                for s in sources:
                    r=lookup[arm,scope,s['brew']]
                    with np.load(_ARGS.work/'predictions'/r['fine']['artifact']) as a:
                        arrays.append({k:a[k] for k in ('native_time','observed_flow','total_observer')})
                    peaks.append(dict(scope=scope,arm=arm,pressure_bar=p,brew=s['brew'],fold=r['fold'],
                        **parameter_fields(arm,r['parameters'],r['mc_g']),**r['fine']['peak']))
                start=max(a['native_time'][0] for a in arrays);end=min(a['native_time'][-1] for a in arrays)
                grid=np.arange(np.ceil(start*10)/10,np.floor(end*10)/10+.01,.1)
                observed=np.mean([np.interp(grid,a['native_time'],a['observed_flow']) for a in arrays],axis=0)
                predicted=np.mean([np.interp(grid,a['native_time'],a['total_observer']) for a in arrays],axis=0)
                curves[scope,p,arm]=(grid,observed,predicted)
                r=lookup[arm,scope,sources[0]['brew']]
                peaks.append(dict(scope=scope,arm=arm,pressure_bar=p,brew='CONDITION_MEAN',fold=r['fold'],
                    **parameter_fields(arm,r['parameters'],r['mc_g']),
                    mean_support='0.1-s interpolation of native observed flows on common clean support',**E.peak(grid,predicted)))
    return curves,peaks


def figure(curves):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    plt.rcParams.update({'font.size':9,'svg.hashsalt':'JOINT_PRESSURE_FADE_001'})
    fig,axes=plt.subplots(2,5,figsize=(16,7),sharex=True,sharey=True)
    colors=['#777777','#1261a0','#c84b20','#24823c'];styles=[':','--','-.','-']
    for row,scope in enumerate(R.SCOPES):
        for col,p in enumerate((4.,6.,9.,11.,13.)):
            ax=axes[row,col]
            for i,arm in enumerate(R.ARMS):
                t,y,q=curves[scope,p,arm];use=t<=105
                if i==0:
                    ax.plot(t[use],y[use],color='black',lw=1.6,label='Observed')
                ax.plot(t[use],q[use],color=colors[i],ls=styles[i],lw=1.6,label=LABELS[arm])
            ax.set_title(f'{p:g} bar · '+('LOCO' if scope=='LOCO' else 'DESCRIPTIVE_ALL'))
            ax.grid(alpha=.15)
            if col==0:
                ax.set_ylabel('Beverage observer flow (g/s)')
            if row==1:
                ax.set_xlabel('Time since stable pressure (s)')
    handles,labels=axes[0,0].get_legend_handles_labels()
    fig.legend(handles,labels,loc='lower center',ncol=5,frameon=False)
    fig.suptitle('Pressure-time conductance fade: frozen trajectories at 0.005 s',fontsize=14)
    fig.text(.5,.055,'Equal-brew means on shared native clean support · LOCO pools held-condition fits · DESCRIPTIVE_ALL is in-sample',ha='center',fontsize=9)
    fig.subplots_adjust(top=.89,bottom=.16,wspace=.1,hspace=.28)
    path=OUT/'FLOW.svg'
    fig.savefig(path,metadata={'Date':None})
    # Matplotlib path serialization leaves trailing blanks; normalize the
    # generated text without changing the SVG geometry or its rendering.
    path.write_text('\n'.join(line.rstrip() for line in path.read_text().splitlines())+'\n')
    plt.close(fig)


def main():
    global _ARGS
    _ARGS=args=E.parser().parse_args();data=R.load_data(args)
    index=R.read(args.work/'EVALUATION.json')
    assert index['identity']==R.identity()
    if index['evaluator_sha256']!=O.digest(E.__file__):
        # A peak-table serialization repair may reuse unchanged numerical work.
        archived=args.work/'EVALUATOR_EXECUTED.py'
        assert O.digest(archived)==index['evaluator_sha256']
        previous=ast.parse(archived.read_text());current=ast.parse(R.ROOT.joinpath(E.__file__).read_text())
        for name in ('selected','peak','evaluate_case','evaluate_objective','evaluate_slice','write_slices'):
            old=next(n for n in previous.body if isinstance(n,ast.FunctionDef) and n.name==name)
            new=next(n for n in current.body if isinstance(n,ast.FunctionDef) and n.name==name)
            assert ast.dump(old)==ast.dump(new), name
        recovery=R.read(args.work/'PEAK_RECOVERY.json')
        assert recovery['evaluation_sha256']==O.digest(args.work/'EVALUATION.json')
        assert recovery['slices_sha256']==O.digest(args.work/'SLICES.json')
        assert recovery['evaluator_sha256']==O.digest(E.__file__)
    freeze=R.read(args.work/'EVALUATION_FREEZE.json')
    assert freeze['identity']==R.identity()
    for path,digest in freeze['fit_sha256'].items():
        R.T.checked_hash(args.work/path,digest)
    records=index['records']
    assert len(records)==448 and len({(r['arm'],r['scope'],r['brew']) for r in records})==448
    for r in records:
        assert r['parameters']==freeze['fits'][r['arm']][r['fold']]
        for step in ('fine','search'):
            R.T.checked_hash(args.work/'predictions'/r[step]['artifact'],r[step]['sha256'])
    old=R.read(args.fade_evidence/'EVALUATION.json')
    prior={(r['arm'],r['scope'],r['brew']):r for r in old['records']}
    for r in records:
        if r['arm']=='A_J1_PF':
            continue
        before=prior[r['arm'],r['scope'],r['brew']]
        for step in ('search','fine'):
            assert r[step]['windows']==before[step]['windows']
            assert r[step]['observer']==before[step]['observer']
            assert r[step]['errors']==before[step]['errors']
    trajectory,late,contributions,numerics=trajectory_tables(data,records)
    paired,scores,ns,onsets,criteria,bank_hash=metric_tables(data,records);numerics+=ns
    fits,starts,ns=fit_tables(data,index);numerics+=ns
    curves,peaks=curves_and_peaks(data,records)
    all_peak_index=R.read(args.work/'PEAKS_ALL_FITS.json')
    assert all_peak_index['identity']==R.identity()
    all_peaks=[r for result in all_peak_index['records'] for r in result['rows']]
    assert len(all_peaks)==804 and len(all_peak_index['records'])==132
    lookup={(r['fold'],r['pressure_bar'],r['brew']):r for r in all_peaks}
    for r in peaks:
        if r['arm']=='A_J1_PF':
            full=lookup[r['fold'],r['pressure_bar'],r['brew']]
            for field in ('maximum_g_s','maximum_times_s','boundary_left','boundary_right',
                          'interior_peak_times_s','peak_status','horizon_start_s','horizon_end_s'):
                assert r[field]==full[field], (r['fold'],r['brew'],field)
    for name,rows in [('FITS',fits),('STARTS',starts),('METRICS_PAIRED',paired),('METRICS',scores),
                      ('TRAJECTORY_COMPARISON',trajectory),('CROSS_CONDITION_LATE',late),('CONTRIBUTIONS',contributions),
                      ('NUMERICAL_SENSITIVITY',numerics),('FADE_FACTORS',fade_factors(data,index)),('ONSETS',onsets),('INHERITED_CRITERIA',criteria),('PEAKS',peaks)]:
        R.R.R.csv_write(OUT/(name+'.csv'),rows)
    figure(curves)
    R.R.R.write_json(OUT/'VERIFICATION.json',dict(fit_problems=12,reused_fits=36,scheduled_starts=len(starts),
        cases=len(records),steps=[.02,.005],windows_per_step=len(records)*10,
        draw_bank_sha256=O.bank_digest(data['draws']),j1_metric_draw_bank_sha256=bank_hash,
        j1_inherited_draw_file_sha256=O.digest(args.joint/'PAIRED_RESAMPLES.json'),
        j1_draw_content_identical=True,
        saved_J1_continuity='all #424 compact levels reproduced at rtol=atol=1e-12',
        saved_J1_component_continuity='all #425 phase components and available intervals reproduced at rtol=atol=1e-12',
        reference=R.read(args.work/'REFERENCE.json'),identity=R.identity(),
        evaluator_sha256=O.digest(E.__file__),reporter_sha256=O.digest(__file__),
        inherited_arm_replay_exact=True,
        all_fit_condition_peak_pairs=132,all_fit_peak_rows=804,primary_peaks_reproduced_exactly=True,
        all_detection_step_agrees=all(r.get('detection_changed') is not True for r in numerics)))


if __name__=='__main__':
    main()
