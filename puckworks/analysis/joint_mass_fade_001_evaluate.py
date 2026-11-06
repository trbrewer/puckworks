"""Replay frozen mass-fade fits on both inherited numerical grids; no fitting."""
import argparse
from concurrent.futures import ProcessPoolExecutor
import multiprocessing
from pathlib import Path
import time

import numpy as np
from scipy.signal import find_peaks

from . import joint_mass_fade_001_run as R
from . import wetting_screen_001_report as P

F, O, T = R.F, R.O, R.T
_DATA = _ARGS = None


def selected(data, work, arm, fold):
    ref = data['reference'][fold]
    if arm == R.ARMS[0]:
        p = ref['parameters']
        return dict(ref, parameters=[*p[:4], 0., p[-1]], arm=arm, fold=fold)
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
    cpu = time.process_time()
    row = dict(arm=arm, scope=scope, brew=s['brew'], pressure_bar=s['nominal_pressure_bar'],
               fold=fold, parameters=p, mc_g=mc)
    ct, cp, cq, onset = data['native'][s['brew']]
    for step, dt in (('search', .02), ('fine', .005)):
        predictor = F.prepare(s, p, mc, dt)
        pred = predictor.chemistry(s['predict_horizon_s'])
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
            endpoint_residual_g_s=endpoint-s['observed_endpoint_g_s'],errors=errors,
            objective_flow=flow_part,objective_onset=onset_part,
            peak=peak(ct,components['total']),artifact=artifact.name,sha256=O.digest(artifact))
    row['cpu_seconds']=time.process_time()-cpu
    R.R.R.write_json(args.work/'predictions'/f'{arm}_{scope}_{s["brew"]}.json',row)
    return row


def evaluate_objective(job):
    arm,fold=job;data,args=_DATA,_ARGS
    cpu=time.process_time();fit=selected(data,args.work,arm,fold)
    row=dict(arm=arm,fold=fold,parameters=fit['parameters'],mc_g=fit['mc_fixed_g'],
             **F.regime(fit['parameters'][4],fit['mc_fixed_g']))
    for step,dt in (('search',.02),('fine',.005)):
        row[step]=F.objective(data,fit['parameters'],fit['held_condition_bar'],dt)
        if step=='search':
            np.testing.assert_allclose(row[step]['objective'],fit['objective'],rtol=1e-12,atol=0)
        if arm=='A_J1_F':
            zero=list(fit['parameters']);zero[4]=0.
            row['zero_'+step]=F.objective(data,zero,fit['held_condition_bar'],dt)
    row['cpu_seconds']=time.process_time()-cpu
    return row


def parser():
    p=argparse.ArgumentParser(description=__doc__)
    for flag in ('ewp','native','raw','screen','joint','lc','wasz','replay','work'):
        p.add_argument('--'+flag,type=Path,required=True)
    p.add_argument('--workers',type=int,default=32)
    return p


def main():
    global _DATA,_ARGS
    _ARGS=args=parser().parse_args();_DATA=data=R.load_data(args)
    frozen={arm:{fold:selected(data,args.work,arm,fold)['parameters'] for fold in data['reference']} for arm in R.ARMS}
    freeze=dict(identity=R.identity(),fits=frozen,draw_hash=O.bank_digest(data['draws']))
    path=args.work/'EVALUATION_FREEZE.json'
    if path.exists() and R.read(path)!=freeze:
        raise ValueError('Frozen selection changed')
    R.R.R.write_json(path,freeze)
    with ProcessPoolExecutor(max_workers=args.workers,mp_context=multiprocessing.get_context('fork')) as pool:
        objectives=list(pool.map(evaluate_objective,[(a,f) for a in R.ARMS for f in data['reference']]))
        rows=list(pool.map(evaluate_case,[(a,scope,s) for a in R.ARMS for scope in R.SCOPES for s in data['sources']]))
    R.R.R.write_json(args.work/'EVALUATION.json',dict(identity=R.identity(),evaluator_sha256=O.digest(__file__),
        objectives=objectives,records=rows,cpu_seconds=sum(r['cpu_seconds'] for r in objectives+rows)))


if __name__=='__main__':
    main()
