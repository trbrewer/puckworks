"""Replay frozen pressure-fade and inherited fits on both inherited numerical grids; no fitting."""
import argparse
from concurrent.futures import ProcessPoolExecutor
import multiprocessing
from pathlib import Path
import time

import numpy as np
from scipy.signal import find_peaks

from . import joint_pressure_fade_001_run as R
from . import wetting_screen_001_report as P
from . import joint_mass_fade_001 as M
from . import mass_fade_diagnostics_001 as D

F, O, T = R.F, R.O, R.T
_DATA = _ARGS = None
SLICE_GRID = (0., .0125, .025, .05, .075, .1, .15, .2, .3, .45, .6)


def selected(data, work, arm, fold):
    ref = data['reference'][fold]
    if arm == R.ARMS[0]:
        p = ref['parameters']
        return dict(ref, parameters=[*p[:4], 0., p[-1]], arm=arm, fold=fold)
    if arm in ('refreshed_A_J1', 'A_J1_F'):
        return data['reused'][arm,fold]
    row = R.read(work/'fits'/f'{arm}_{fold}.json')
    if row['identity'] != R.identity() or row['fold'] != fold or row['mc_fixed_g'] != data['bank'][fold][4]:
        raise ValueError('Selected fit identity/fold/Mc changed')
    if row['training_brews'] != ref['training_brews']:
        raise ValueError('Selected training membership changed')
    return row


def peak(time, flow):
    """Native observer peak, exact ties and explicit finite-support boundaries."""
    time, flow = np.asarray(time), np.asarray(flow)
    ids = np.flatnonzero(flow == flow.max())
    local, _ = find_peaks(flow, plateau_size=True)
    interior = ids[(ids > 0) & (ids < len(time)-1)]
    flat = bool(np.all(flow == flow[0]))
    return dict(maximum_g_s=float(flow.max()), maximum_times_s=time[ids].tolist(),
                boundary_left=bool(0 in ids), boundary_right=bool(len(time)-1 in ids),
                interior_peak_times_s=time[local].tolist(),
                peak_status='flat; no unique peak' if flat else (
                    'interior global maximum' if len(interior) else 'no interior peak within horizon'),
                horizon_start_s=float(time[0]), horizon_end_s=float(time[-1]))


def evaluate_case(job):
    arm, scope, s = job; data, args = _DATA, _ARGS
    fold = R.R.label(s['nominal_pressure_bar'] if scope == 'LOCO' else None)
    fit = selected(data, args.work, arm, fold)
    if scope == 'LOCO' and s['brew'] in fit['training_brews']:
        raise ValueError('Held-out brew in training')
    p, mc = fit['parameters'], fit['mc_fixed_g']
    model = M if arm == 'A_J1_F' else F
    cpu = time.process_time()
    row = dict(arm=arm, scope=scope, brew=s['brew'], pressure_bar=s['nominal_pressure_bar'],
               fold=fold, parameters=p, mc_g=mc)
    ct, cp, cq, onset = data['native'][s['brew']]
    for step, dt in (('search', .02), ('fine', .005)):
        predictor = model.prepare(s, p, mc, dt)
        pred = predictor.chemistry(s['predict_horizon_s'])
        exposure = np.interp([60.,100.], predictor.time, predictor.exposure)
        if arm == 'A_J1_PF' and p[4] != 0.:
            np.testing.assert_array_equal(predictor.exposure, pred['pressure_exposure_bar_s'])
        np.testing.assert_allclose(predictor.mass, pred['liquid_g'], rtol=1e-12, atol=0)
        np.testing.assert_allclose(predictor.flow, pred['bed_flow_g_s'], rtol=1e-12, atol=0)
        obs = predictor.observer(s['observer_times_s'], accelerate=False)
        components = {name: T.beverage_observer(dict(time=pred['time'], beverage_g=pred[key]), ct)
                      for name,key in (('liquid','liquid_g'),('solute','solute_g'),('total','beverage_g'))}
        np.testing.assert_allclose(components['liquid']+components['solute'],components['total'],rtol=1e-12,atol=1e-12)
        windows=[]
        for clock, offset in O.SNAPSHOTS:
            old = data['observed'][s['brew'], clock, offset]
            center = T.observed_center(onset, clock, offset)
            w = dict(clock=clock, time_s=offset, observed=float(old['flow_g_s']),
                     pressure=float(old['pressure_bar']), start_s=center-1, end_s=center+1)
            for component, values in components.items():
                pressure, value, reason = O.paired_window(ct, cp, values, center)
                if reason != 'available' or old['available'] != 'True':
                    raise ValueError('Frozen complete window became unavailable')
                np.testing.assert_allclose(pressure,w['pressure'],rtol=1e-12,atol=1e-12)
                w[component] = float(value)
            np.testing.assert_allclose(w['liquid']+w['solute'],w['total'],rtol=1e-12,atol=1e-12)
            windows.append(w)
        endpoint=float(predictor.scored_flow([100.])[0])
        trace=predictor.scored_flow(s['trace_times_s'])
        errors=P.hydraulic_errors([s],[endpoint],[trace])
        errors={k:float(v[0]) for k,v in errors.items()}
        errors['onset']=R.R.W.squared_onset(obs,s['observed_onset_for_scoring_only_s'])
        artifact=args.work/'predictions'/f'{arm}_{scope}_{s["brew"]}_{step}.npz'
        np.savez_compressed(artifact,**{k:v for k,v in pred.items() if isinstance(v,np.ndarray)},
                            native_time=ct, native_pressure=cp, observed_flow=cq,
                            liquid_observer=components['liquid'], solute_observer=components['solute'],
                            total_observer=components['total'])
        flow_part,onset_part=F.J.loss_components(predictor.scored_flow(s['fit_times_s']),s['fit_flow_g_s'],obs,s['observed_onset_for_scoring_only_s'])
        row[step]=dict(dt=dt,observer=obs,windows=windows,endpoint_g_s=endpoint,
            exposure_60_bar_s=float(exposure[0]),exposure_100_bar_s=float(exposure[1]),
            recorded_late_fade_factor=float(np.exp(-p[4]*(exposure[1]-exposure[0]))) if arm=='A_J1_PF' else None,
            endpoint_residual_g_s=endpoint-s['observed_endpoint_g_s'],errors=errors,
            objective_flow=flow_part,objective_onset=onset_part,
            peak=peak(ct,components['total']),artifact=artifact.name,sha256=O.digest(artifact))
    row['cpu_seconds']=time.process_time()-cpu
    R.R.R.write_json(args.work/'predictions'/f'{arm}_{scope}_{s["brew"]}.json',row)
    return row


def evaluate_objective(job):
    arm,fold=job;data,args=_DATA,_ARGS
    cpu=time.process_time();fit=selected(data,args.work,arm,fold)
    model = M if arm == 'A_J1_F' else F
    row=dict(arm=arm,fold=fold,parameters=fit['parameters'],mc_g=fit['mc_fixed_g'])
    for step,dt in (('search',.02),('fine',.005)):
        row[step]=model.objective(data,fit['parameters'],fit['held_condition_bar'],dt)
        if step=='search':
            np.testing.assert_allclose(row[step]['objective'],fit['objective'],rtol=1e-12,atol=0)
        if arm in ('A_J1_F','A_J1_PF'):
            zero=list(fit['parameters']);zero[4]=0.
            row['zero_'+step]=model.objective(data,zero,fit['held_condition_bar'],dt)
    row['cpu_seconds']=time.process_time()-cpu
    return row


def evaluate_slice(job):
    fold, product, kind = job
    fit = selected(_DATA,_ARGS.work,'A_J1_PF',fold)
    p = list(fit['parameters'])
    if kind == 'grid':
        p[4] = product/1300.
    cpu = time.process_time()
    result = F.objective(_DATA,p,fit['held_condition_bar'],dt=.02)
    return dict(fold=fold,record_type=kind,gamma_P=p[4],gamma_P_1300=p[4]*1300,
                requested_gamma_P_1300=product,Mc_g=fit['mc_fixed_g'],
                **result,cpu_seconds=time.process_time()-cpu)


def write_slices(data,args,rows):
    summaries=[]
    objectives={r['fold']:r for r in R.read(args.work/'EVALUATION.json')['objectives'] if r['arm']=='A_J1_PF'}
    for fold in data['reference']:
        fit=selected(data,args.work,'A_J1_PF',fold)
        grid=[r for r in rows if r['fold']==fold and r['record_type']=='grid']
        selected_row=next(r for r in rows if r['fold']==fold and r['record_type']=='selected')
        assert [r['requested_gamma_P_1300'] for r in grid]==list(SLICE_GRID)
        for field in ('objective','flow_component','onset_component','detected','intended','available'):
            assert selected_row[field]==fit[field], (fold,field)
            assert grid[0][field]==objectives[fold]['zero_search'][field], (fold,field,'zero slice')
        shape=D.slice_shape(SLICE_GRID,[r['objective'] for r in grid])
        product=selected_row['gamma_P_1300']
        below=[r for r in grid if r['requested_gamma_P_1300']<=product]
        above=[r for r in grid if r['requested_gamma_P_1300']>=product]
        strict_below=[r for r in grid if r['gamma_P']<fit['parameters'][4]]
        strict_above=[r for r in grid if r['gamma_P']>fit['parameters'][4]]
        bracketed=bool(strict_below and strict_above)
        local_minimum=bracketed and fit['objective']<=min(strict_below[-1]['objective'],strict_above[0]['objective'])
        summaries.append(dict(fold=fold,selected_gamma_P=fit['parameters'][4],selected_gamma_P_1300=product,
            selected_objective=fit['objective'],**shape,
            selected_minus_grid_minimum=fit['objective']-shape['grid_min_objective'],
            selected_bracketed_by_grid=bracketed,selected_no_worse_than_adjacent_grid=local_minimum,
            lower_neighbor=below[-1]['requested_gamma_P_1300'] if below else None,
            upper_neighbor=above[0]['requested_gamma_P_1300'] if above else None,
            objective_at_lower_neighbor=below[-1]['objective'] if below else None,
            objective_at_upper_neighbor=above[0]['objective'] if above else None))
    R.R.R.csv_write(R.OUT/'GAMMA_P_SLICES.csv',rows)
    R.R.R.csv_write(R.OUT/'SLICE_SUMMARY.csv',summaries)


def evaluate_peak_condition(job):
    """Every selected PF vector at every condition; peak diagnostics, not extra LOCO scores."""
    fold, pressure = job
    fit=selected(_DATA,_ARGS.work,'A_J1_PF',fold)
    sources=[s for s in _DATA['sources'] if s['nominal_pressure_bar']==pressure]
    cpu=time.process_time();curves=[];rows=[]
    common=dict(arm='A_J1_PF',scope='ALL_FIT_CONDITION_DIAGNOSTIC',fold=fold,
        pressure_bar=pressure,gamma_P=fit['parameters'][4],Mc_g=fit['mc_fixed_g'],dt=.005,
        condition_in_training=fit['held_condition_bar']!=pressure,
        is_held_out_condition=fit['held_condition_bar']==pressure)
    for s in sources:
        predictor=F.prepare(s,fit['parameters'],fit['mc_fixed_g'],dt=.005)
        pred=predictor.chemistry(s['predict_horizon_s'])
        ct=_DATA['native'][s['brew']][0]
        observed=T.beverage_observer(pred,ct)
        curves.append((ct,observed))
        rows.append(dict(**common,brew=s['brew'],**peak(ct,observed)))
    start=max(t[0] for t,q in curves);end=min(t[-1] for t,q in curves)
    grid=np.arange(np.ceil(start*10)/10,np.floor(end*10)/10+.01,.1)
    average=np.mean([np.interp(grid,t,q) for t,q in curves],axis=0)
    rows.append(dict(**common,brew='CONDITION_MEAN',
        mean_support='0.1-s interpolation of native observed flows on common clean support',**peak(grid,average)))
    return dict(rows=rows,cpu_seconds=time.process_time()-cpu)


def parser():
    p=argparse.ArgumentParser(description=__doc__)
    for flag in ('ewp','native','raw','screen','joint','lc','wasz','replay','fade-evidence','work'):
        p.add_argument('--'+flag,type=Path,required=True)
    p.add_argument('--workers',type=int,default=32)
    return p


def main():
    global _DATA,_ARGS
    _ARGS=args=parser().parse_args();_DATA=data=R.load_data(args)
    frozen={arm:{fold:selected(data,args.work,arm,fold)['parameters'] for fold in data['reference']} for arm in R.ARMS}
    fit_hashes={str(path.relative_to(args.work)):O.digest(path) for path in sorted((args.work/'fits').glob('*.json'))}
    if len(fit_hashes)!=12:
        raise ValueError('Expected exactly 12 selected pressure-fade fits before replay')
    freeze=dict(identity=R.identity(),fits=frozen,fit_sha256=fit_hashes,draw_hash=O.bank_digest(data['draws']))
    path=args.work/'EVALUATION_FREEZE.json'
    if path.exists() and R.read(path)!=freeze:
        raise ValueError('Frozen selection changed')
    R.R.R.write_json(path,freeze)
    with ProcessPoolExecutor(max_workers=args.workers,mp_context=multiprocessing.get_context('fork')) as pool:
        objectives=list(pool.map(evaluate_objective,[(a,f) for a in R.ARMS for f in data['reference']]))
        rows=list(pool.map(evaluate_case,[(a,scope,s) for a in R.ARMS for scope in R.SCOPES for s in data['sources']]))
    R.R.R.write_json(args.work/'EVALUATION.json',dict(identity=R.identity(),evaluator_sha256=O.digest(__file__),
        objectives=objectives,records=rows,cpu_seconds=sum(r['cpu_seconds'] for r in objectives+rows)))
    with ProcessPoolExecutor(max_workers=args.workers,mp_context=multiprocessing.get_context('fork')) as pool:
        slices=list(pool.map(evaluate_slice,[(fold,value,'grid') for fold in data['reference'] for value in SLICE_GRID]+[(fold,None,'selected') for fold in data['reference']]))
    R.R.R.write_json(args.work/'SLICES.json',dict(identity=R.identity(),records=slices))
    write_slices(data,args,slices)
    with ProcessPoolExecutor(max_workers=args.workers,mp_context=multiprocessing.get_context('fork')) as pool:
        peaks=list(pool.map(evaluate_peak_condition,[(fold,p) for fold in data['reference'] for p in F.J.W.NOMINAL]))
    R.R.R.write_json(args.work/'PEAKS_ALL_FITS.json',dict(identity=R.identity(),records=peaks))
    R.R.R.csv_write(R.OUT/'PEAKS_ALL_FITS.csv',[row for result in peaks for row in result['rows']])


if __name__=='__main__':
    main()
