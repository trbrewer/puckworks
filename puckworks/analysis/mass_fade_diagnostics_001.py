"""Fixed gamma slices and observed ordering; no optimizer or fit updates.

Execute this file as a script, using the pinned #427 checkout for inherited
imports. Pure bookkeeping/statistical helpers remain importable on main.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor
import csv
import hashlib
import importlib
import json
import multiprocessing
from pathlib import Path
import subprocess
import sys
import time

import numpy as np
from scipy.stats import rankdata

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'docs/research/MASS_FADE_DIAGNOSTICS_001'
FADE_SHA = 'ec0dc887ca0f66338fe166cd4ed8e7cbf2994441'
WASZ_SHA = 'c4b4a07e110a3ede5013fd876a02a58ee6456eab'
DRAW_SHA = 'd599d80c854fd5a3cf9b9ca5d6fe1c617b222125bd1adcb36ad9edecd96801b6'
GRID = (0., .0025, .005, .01, .015, .02, .025, .03, .035, .04,
        .05, .06, .08, .10, .13, .17, .25, .40)
_R = _DATA = None


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    return json.loads(Path(path).read_text())


def table(path):
    with Path(path).open() as stream:
        return list(csv.DictReader(stream))


def write_json(path, value):
    Path(path).write_text(json.dumps(value, indent=2, allow_nan=False)+'\n')


def write_csv(path, rows):
    fields = list(dict.fromkeys(k for row in rows for k in row))
    with Path(path).open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fields, lineterminator='\n')
        writer.writeheader()
        for row in rows:
            writer.writerow({k: json.dumps(v) if isinstance(v, (list, dict)) else
                             '' if v is None or isinstance(v, float) and not np.isfinite(v) else v
                             for k, v in row.items()})


def gamma_vector(parameters, mc, product):
    """Change gamma only; fixed Mc is external and tau0 remains last."""
    p = np.array(parameters, dtype=float, copy=True)
    if p.shape != (6,) or not np.isfinite(p).all() or not np.isfinite(mc) or mc <= 0:
        raise ValueError('Invalid fixed vector/Mc')
    if not np.isfinite(product) or product < 0 or product/mc > .2:
        raise ValueError('Invalid gamma product')
    p[4] = product/mc
    return p.tolist()


def slice_shape(x, y):
    """Exact discrete shape and values, without a flatness tolerance."""
    x, y = np.asarray(x), np.asarray(y)
    if x.ndim != 1 or len(x) != len(y) or len(x) < 3 or not np.all(np.diff(x) > 0):
        raise ValueError('Need an ordered grid')
    if not np.isfinite(y).all():
        raise ValueError('Nonfinite slice')
    d = np.diff(y)
    minima = np.flatnonzero(y == y.min())
    local = [i for i in range(1, len(y)-1)
             if y[i] <= y[i-1] and y[i] <= y[i+1] and (y[i] < y[i-1] or y[i] < y[i+1])]
    if np.all(d == 0):
        shape = 'flat_exactly'
    elif np.all(d >= 0):
        shape = 'monotone_toward_smaller_gamma'
    elif np.all(d <= 0):
        shape = 'monotone_toward_larger_gamma'
    elif (np.all(np.diff(minima) == 1) and minima[0] > 0 and minima[-1] < len(y)-1
          and np.all(d[:minima[0]] <= 0) and np.all(d[minima[-1]:] >= 0)):
        shape = 'interior_minimum'
    else:
        shape = 'nonmonotone'
    return dict(shape=shape, grid_min_products=x[minima].tolist(), grid_min_objective=float(y.min()),
                grid_max_objective=float(y.max()), objective_span=float(np.ptp(y)),
                minimum_at_boundary=bool(0 in minima or len(y)-1 in minima),
                local_min_products=x[local].tolist(), adjacent_objective_changes=d.tolist())


def spearman(x, y):
    """Average-rank correlation on the last axis; constant ranks are undefined."""
    x, y = np.asarray(x, dtype=float), np.asarray(y, dtype=float)
    if x.shape != y.shape or not np.isfinite(x).all() or not np.isfinite(y).all():
        raise ValueError('Need paired finite values')
    a, b = rankdata(x, axis=-1), rankdata(y, axis=-1)
    a, b = a-a.mean(axis=-1, keepdims=True), b-b.mean(axis=-1, keepdims=True)
    den = np.sqrt((a*a).sum(axis=-1)*(b*b).sum(axis=-1))
    return np.divide((a*b).sum(axis=-1), den, out=np.full(den.shape, np.nan), where=den > 0)


def scale_mass(raw_time, raw_mass, clean_time, targets=(60., 100.)):
    """Recorded mass on exact native retained samples; no flow integration."""
    t, m, ct = (np.asarray(v, dtype=float) for v in (raw_time, raw_mass, clean_time))
    if t.shape != m.shape or not np.isfinite(t).all() or not np.isfinite(m).all():
        raise ValueError('Invalid raw scale')
    if len(ct) < 2 or not np.all(np.diff(t) > 0) or not np.all(np.diff(ct) > 0):
        raise ValueError('Invalid native support')
    ids = np.searchsorted(t, ct)
    if np.any(ids >= len(t)) or not np.array_equal(t[ids], ct):
        raise ValueError('Clean support is not a native raw subset')
    targets = np.asarray(targets)
    if targets.min() < ct[0] or targets.max() > ct[-1]:
        raise ValueError('Mass target outside retained support')
    pre = (t >= -2) & (t <= 0)
    baseline = float(np.median(m[pre]) if pre.any() else m[0])
    return np.interp(targets, ct, m[ids]-baseline), baseline, m[ids]-baseline


def authenticate(args):
    """Import and authenticate immutable #427 without changing its artifacts."""
    global _R
    for path, sha in ((args.fade_code, FADE_SHA), (args.wasz, WASZ_SHA)):
        actual = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=path).decode().strip()
        if actual != sha:
            raise ValueError('Wrong source checkout: '+str(path))
        subprocess.run(['git', 'diff', '--exit-code', sha, '--', 'puckworks', 'docs'], cwd=path,
                       check=True, stdout=subprocess.DEVNULL)
    if 'puckworks' in sys.modules:
        raise RuntimeError('Execute this file directly, not with -m, to isolate pinned imports')
    sys.path.insert(0, str(args.fade_code))
    _R = importlib.import_module('puckworks.analysis.joint_mass_fade_001_run')
    def forbidden(*a, **kw):
        raise RuntimeError('Optimization forbidden in this diagnostic')
    _R.minimize = forbidden
    assert Path(_R.__file__).resolve().is_relative_to(args.fade_code.resolve())
    old = args.fade_code/'docs/research/JOINT_MASS_FADE_001'
    receipt = read(old/'RUN_RECEIPT.json')
    for name, expected in receipt['artifact_sha256'].items():
        assert digest(old/name) == expected
    for name, expected in receipt['code_sha256'].items():
        assert digest(args.fade_code/name) == expected
    for name, expected in receipt['external_freeze_sha256'].items():
        assert digest(args.fade_evidence/name) == expected
    freeze = read(args.fade_evidence/'EVALUATION_FREEZE.json')
    for name, expected in freeze['fit_sha256'].items():
        assert digest(args.fade_evidence/name) == expected
    data = _R.load_data(args)
    assert _R.O.bank_digest(data['draws']) == DRAW_SHA
    records = [r for r in table(old/'FITS.csv') if r['arm'] != 'saved_A_J1']
    assert len(records) == 24
    fits = []
    for row in records:
        fit = read(args.fade_evidence/'fits'/f"{row['arm']}_{row['fold']}.json")
        assert fit['identity'] == _R.identity()
        assert fit['parameters'] == [float(row[k]) for k in _R.F.ORDER]
        assert fit['mc_fixed_g'] == float(row['Mc_g']) == data['bank'][row['fold']][4]
        assert fit['objective'] == float(row['objective_search'])
        assert fit['training_brews'] == data['reference'][row['fold']]['training_brews']
        fits.append(fit)
    manifest = dict(fade_head=FADE_SHA, observation_head=WASZ_SHA,
                    inherited_identity=_R.identity(), brew_order=[s['brew'] for s in data['sources']],
                    draw_bank_sha256=DRAW_SHA, input_paths={k:str(v) for k,v in vars(args).items() if isinstance(v,Path)},
                    source_bundle_sha256={p.name:digest(p) for p in old.iterdir() if p.is_file()},
                    source_fit_sha256=freeze['fit_sha256'], external_freeze_sha256=receipt['external_freeze_sha256'])
    return data, fits, manifest


def evaluate(job):
    fit, product, kind = job
    p = fit['parameters'] if kind == 'selected' else gamma_vector(fit['parameters'], fit['mc_fixed_g'], product)
    start = time.process_time()
    value = _R.F.objective(_DATA, p, fit['held_condition_bar'], dt=.02)
    return dict(arm=fit['arm'], fold=fit['fold'], record_type=kind, Mc_g=fit['mc_fixed_g'],
                gamma=p[4], gamma_Mc=p[4]*fit['mc_fixed_g'], requested_gamma_Mc=product,
                **value, cpu_seconds=time.process_time()-start)


def summarize_slices(fits, rows, args):
    old = args.fade_code/'docs/research/JOINT_MASS_FADE_001'
    old_objectives = {(r['arm'],r['fold']):r for r in read(args.fade_evidence/'EVALUATION.json')['objectives']}
    starts = table(old/'STARTS.csv')
    summaries, winners = [], []
    for fit in fits:
        key = fit['arm'], fit['fold']
        own = [r for r in rows if (r['arm'],r['fold']) == key]
        grid = [r for r in own if r['record_type'] == 'grid']
        selected = next(r for r in own if r['record_type'] == 'selected')
        assert len(grid) == len(GRID) and [r['requested_gamma_Mc'] for r in grid] == list(GRID)
        for field in ('objective','flow_component','onset_component','detected','intended','available'):
            assert selected[field] == fit[field], (key, field, 'selected mismatch')
            expected = old_objectives[key]['zero_search' if key[0] == 'A_J1_F' else 'search'][field]
            assert grid[0][field] == expected, (key, field, 'zero mismatch')
        x = np.array(GRID); y = np.array([r['objective'] for r in grid]); s = selected['gamma_Mc']
        lower, upper = x[x <= s], x[x >= s]
        shape = slice_shape(x,y)
        summaries.append(dict(arm=key[0], fold=key[1], selected_gamma_Mc=s,
            selected_objective=selected['objective'], **shape,
            selected_minus_grid_minimum=selected['objective']-shape['grid_min_objective'],
            selected_minus_nearest_min_product=float(s-min(shape['grid_min_products'], key=lambda v:abs(s-v))),
            lower_neighbor_product=float(lower[-1]) if len(lower) else None,
            upper_neighbor_product=float(upper[0]) if len(upper) else None,
            objective_at_lower_neighbor=float(y[x==lower[-1]][0]) if len(lower) else None,
            objective_at_upper_neighbor=float(y[x==upper[0]][0]) if len(upper) else None))
        if fit['arm'] == 'A_J1_F':
            start = next(r for r in starts if (r['arm'],r['fold'],int(r['start'])) == (*key,fit['winning_start']))
            assert json.loads(start['best_parameters']) == fit['parameters']
            winners.append(dict(fold=fit['fold'], winning_start=fit['winning_start'], origin=start['origin'],
                Mc_g=fit['mc_fixed_g'], initial_gamma_Mc=float(start['gamma_Mc']),
                final_gamma_Mc=s, final_minus_initial_gamma_Mc=s-float(start['gamma_Mc']),
                initial_parameters=json.loads(start['initial_parameters']), final_parameters=fit['parameters']))
    return summaries, winners


def observed_ordering(data, args):
    O = _R.O
    rows, values = [], []
    fields = ('mass60_g','mass100_g','pressure60_bar','pressure100_bar','achieved_pressure_bar',
              'flow60_g_s','flow100_g_s','late_change_g_s')
    for source in data['sources']:
        brew = source['brew']
        t,p,m,_ = O.B0.raw_trace(args.raw/'measurements_time_dependent'/f'{brew}.txt')
        ct,cp,cq,_ = O.B0.clean_course(t,p,m)
        masses, baseline, native_mass = scale_mass(t,m,ct)
        assert O.B0.sustained_onset(ct,native_mass,cq) == data['native'][brew][3]
        windows = []
        for target in (60,100):
            old = data['observed'][brew,'stable_pressure',target]
            pressure,flow,reason = O.paired_window(ct,cp,cq,target)
            assert reason == 'available' and old['available'] == 'True'
            np.testing.assert_allclose([pressure,flow,ct[0],ct[-1],target-1,target+1],
                [float(old[k]) for k in ('pressure_bar','flow_g_s','recorded_start_stable_s',
                 'recorded_end_stable_s','window_start_stable_s','window_end_stable_s')],rtol=1e-12,atol=1e-12)
            windows.append((pressure,flow))
        (p60,q60),(p100,q100) = windows
        value = [*masses,p60,p100,(p60+p100)/2,q60,q100,q100-q60]
        values.append(value)
        rows.append(dict(record_type='brew',brew=brew,nominal_pressure_bar=source['nominal_pressure_bar'],
            n_brews=1,baseline_g=baseline,support_start_s=float(ct[0]),support_end_s=float(ct[-1]),
            stable_start_s=60,stable_end_s=100,duration_s=40,**dict(zip(fields,value))))
    values = np.array(values)
    means = np.stack([values[data['condition']==c].mean(axis=0) for c in data['draws']])
    boot = np.stack([values[ids].mean(axis=1) for ids in data['draws'].values()],axis=1)
    historical = table(args.wasz/'docs/research/WASZ_TURNOVER_TIME_001/CONDITION_MEANS_BY_TIME.csv')
    for k,c in enumerate(data['draws']):
        row = dict(record_type='condition',brew='CONDITION_MEAN',nominal_pressure_bar=c,
                   n_brews=int(np.sum(data['condition']==c)),stable_start_s=60,stable_end_s=100,duration_s=40)
        for j,field in enumerate(fields):
            row.update(O.uncertainty(field,means[k,j],boot[:,k,j]))
        old = next(r for r in historical if r['clock']=='stable_pressure' and r['time_s']=='60'
                   and float(r['nominal_pressure_bar'])==c)
        for suffix in ('','_lo','_hi'):
            np.testing.assert_allclose(row['late_change_g_s'+suffix],
                float(old['stable100_minus_current_flow_g_s'+suffix]),rtol=1e-12,atol=1e-12)
        rows.append(row)
    correlations=[]; draws={}
    for name,j in (('mass60_g',0),('achieved_pressure_bar',4),('elapsed_duration_s',None)):
        x = means[:,j] if j is not None else np.full(11,40.)
        bx = boot[:,:,j] if j is not None else np.full((1000,11),40.)
        rho,br = spearman(x,means[:,-1]),spearman(bx,boot[:,:,-1])
        draws[name]=br
        correlations.append(dict(predictor=name,conditions=11,**O.uncertainty('rho',rho,br),
            interpretation='descriptive; fixed eleven conditions' if j is not None else 'undefined: identical elapsed duration'))
    contrast = np.abs(draws['mass60_g'])-np.abs(draws['achieved_pressure_bar'])
    correlations.append(dict(predictor='abs_rho_mass_minus_abs_rho_pressure',conditions=11,
        **O.uncertainty('rho',abs(correlations[0]['rho'])-abs(correlations[1]['rho']),contrast),
        interpretation='paired descriptive difference in absolute rank correlations'))
    np.savez_compressed(args.work/'OBSERVED_BOOTSTRAPS.npz',values=values,means=means,bootstrap=boot,
                        nominal=np.array(list(data['draws'])),**draws)
    return rows, correlations


def figures(slices, summaries, observations):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    plt.rcParams.update({'font.size':8,'svg.hashsalt':'MASS_FADE_DIAGNOSTICS_001'})
    def save(fig,name):
        path=OUT/name
        fig.savefig(path,metadata={'Date':None})
        path.write_text('\n'.join(s.rstrip() for s in path.read_text().splitlines())+'\n')
        plt.close(fig)
    folds=list(dict.fromkeys(r['fold'] for r in slices))
    fig,axes=plt.subplots(3,4,figsize=(14,9),sharex=True)
    for ax,fold in zip(axes.flat,folds):
        inset=ax.inset_axes([.08,.46,.52,.48])
        for arm,color,label in (('A_J1_F','#c84b20','Fade coordinates'),('refreshed_A_J1','#1261a0','Control coordinates')):
            rows=[r for r in slices if r['fold']==fold and r['arm']==arm]
            g=[r for r in rows if r['record_type']=='grid']; s=next(r for r in rows if r['record_type']=='selected')
            ax.plot(GRID,[r['objective'] for r in g],'.-',color=color,label=label)
            ax.plot(s['gamma_Mc'],s['objective'],'*',color=color,ms=10,label='Selected point' if arm=='A_J1_F' else None)
            near=[r for r in g if r['requested_gamma_Mc']<=.06]
            inset.plot([r['gamma_Mc'] for r in near],[r['objective'] for r in near],'.-',color=color,lw=1,ms=2)
            inset.plot(s['gamma_Mc'],s['objective'],'*',color=color,ms=6)
        inset.set_xlim(0,.06);inset.set_xticks([0,.03,.06]);inset.tick_params(labelsize=6)
        inset.set_title('Linear zoom: 0–.06',fontsize=7,pad=2);inset.grid(alpha=.15)
        ax.set_xscale('symlog',linthresh=.0025)
        ax.set_title(fold.replace('HYD-LOCO-','LOCO '));ax.grid(alpha=.18)
        ax.set_xlabel('γMc (linear near zero; log spacing above .0025)')
        ax.set_ylabel('Training objective')
    handles,labels=axes.flat[0].get_legend_handles_labels()
    fig.legend(handles,labels,loc='lower center',ncol=3,frameon=False)
    fig.suptitle('Fixed-coordinate gamma slices · 0.02 s · no optimization')
    fig.tight_layout(rect=(0,.045,1,.96));save(fig,'GAMMA_SLICES.svg')
    fig,axes=plt.subplots(1,2,figsize=(11,4.8),sharey=True)
    for ax,field,label in zip(axes,('mass60_g','achieved_pressure_bar'),
                             ('Observed delivered beverage mass at +60 s (g)','Achieved line pressure: mean of +60/+100-s windows (bar)')):
        brew=[r for r in observations if r['record_type']=='brew']
        cond=[r for r in observations if r['record_type']=='condition']
        ax.scatter([r[field] for r in brew],[r['late_change_g_s'] for r in brew],color='#777777',alpha=.25,s=16,label='Individual brew')
        for r in cond:
            x,y=r[field],r['late_change_g_s']
            ax.errorbar(x,y,yerr=[[y-r['late_change_g_s_lo']],[r['late_change_g_s_hi']-y]],
                        color='#1261a0',fmt='o',ms=5,capsize=3)
            ax.annotate(f"{r['nominal_pressure_bar']:g}",(x,y),xytext=(4,4),textcoords='offset points',fontsize=8)
        ax.axhline(0,color='black',lw=.7,alpha=.5);ax.set_xlabel(label);ax.grid(alpha=.15)
    axes[0].set_ylabel('Observed +60→100-s beverage-flow change (g/s)')
    fig.suptitle('Eleven condition means with paired 95% intervals · labels: nominal bar')
    fig.text(.5,.015,'Shared whole-brew resamples; fixed conditions and elapsed times. Descriptive ordering, no fitted relationship.',ha='center',fontsize=9)
    fig.tight_layout(rect=(0,.055,1,.94));save(fig,'LATE_CHANGE_ORDERING.svg')


def parser():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('fade-code','fade-evidence','ewp','native','raw','screen','joint','lc','wasz','replay','work'):
        p.add_argument('--'+name,type=Path,required=True)
    p.add_argument('--workers',type=int,default=24)
    p.add_argument('--report-from-cache',action='store_true',help='Regenerate summaries/figures from authenticated saved evaluations; no objective calls')
    return p


def main():
    global _DATA
    args=parser().parse_args();args.work.mkdir(parents=True,exist_ok=True)
    plan='docs/research/MASS_FADE_DIAGNOSTICS_001/PLAN.md'
    committed=subprocess.check_output(['git','show','HEAD:'+plan],cwd=ROOT)
    assert hashlib.sha256(committed).hexdigest()==digest(ROOT/plan)
    _DATA,fits,manifest=authenticate(args)
    manifest.update(plan_sha256=digest(ROOT/plan),code_sha256=digest(__file__),grid=list(GRID))
    jobs=[(fit,x,'grid') for fit in fits for x in GRID]+[(fit,None,'selected') for fit in fits]
    if args.report_from_cache:
        prior=read(OUT/'VERIFICATION.json'); previous=read(OUT/'INPUT_MANIFEST.json')
        assert digest(args.work/'OBJECTIVE_EVALUATIONS.json')==prior['objective_evaluations_sha256']
        for key,value in manifest.items():
            if key!='code_sha256':
                assert previous[key]==value, ('Changed cached-evaluation input',key)
        manifest['objective_code_sha256']=previous.get('objective_code_sha256',previous['code_sha256'])
        assert digest(args.work/'OBJECTIVE_SOURCE.py')==manifest['objective_code_sha256']
        slices=read(args.work/'OBJECTIVE_EVALUATIONS.json')
    else:
        manifest['objective_code_sha256']=digest(__file__)
        (args.work/'OBJECTIVE_SOURCE.py').write_bytes(Path(__file__).read_bytes())
        with ProcessPoolExecutor(max_workers=args.workers,mp_context=multiprocessing.get_context('fork')) as pool:
            slices=list(pool.map(evaluate,jobs))
        write_json(args.work/'OBJECTIVE_EVALUATIONS.json',slices)
    assert len(slices)==len(jobs)
    for row,(fit,x,kind) in zip(slices,jobs):
        assert (row['arm'],row['fold'],row['record_type'])==(fit['arm'],fit['fold'],kind)
        assert row['parameters']==(fit['parameters'] if kind=='selected' else gamma_vector(fit['parameters'],fit['mc_fixed_g'],x))
    write_json(OUT/'INPUT_MANIFEST.json',manifest)
    summaries,winners=summarize_slices(fits,slices,args)
    observations,correlations=observed_ordering(_DATA,args)
    for name,rows in (('GAMMA_SLICES',slices),('SLICE_SUMMARY',summaries),('START_VS_FINAL',winners),
                      ('LATE_CHANGE_ORDERING',observations),('CORRELATIONS',correlations)):
        write_csv(OUT/(name+'.csv'),rows)
    figures(slices,summaries,observations)
    write_json(OUT/'VERIFICATION.json',dict(grid_evaluations=432,selected_evaluations=24,
        exact_selected_reproduction=24,exact_zero_reproduction=24,observed_brews=56,
        observed_conditions=11,paired_windows_reproduced=112,mass_support_and_baseline_checks=56,
        source_late_intervals_reproduced=11,draw_bank_sha256=DRAW_SHA,
        input_manifest_sha256=digest(OUT/'INPUT_MANIFEST.json'),code_sha256=digest(__file__),
        objective_code_sha256=manifest['objective_code_sha256'],
        external_artifact_sha256={p.name:digest(p) for p in args.work.glob('*.npz')},
        objective_evaluations_sha256=digest(args.work/'OBJECTIVE_EVALUATIONS.json')))


if __name__=='__main__':
    main()
