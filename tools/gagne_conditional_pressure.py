#!/usr/bin/env python3
"""Execute the frozen research-only comparison. Raw arrays must stay outside Git.

Reproduce: install research-only jaxgsa==1.3.1 (Python >=3.12), then run
python tools/gagne_conditional_pressure.py --private-output OUTSIDE_REPO --output BUNDLE
The task PLAN.json must exist and all hash-bound inputs must match.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor
import csv
import hashlib
import importlib.metadata
import json
import multiprocessing
import os
from pathlib import Path
import sys
import time

# Bound BLAS/JAX threads before importing any numerical library. Worker processes
# use spawn so no JAX runtime is forked. This changes no numerical algorithm.
for variable in ('OPENBLAS_NUM_THREADS', 'OMP_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ[variable] = '1'
os.environ.setdefault('JAX_PLATFORMS', 'cpu')

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from puckworks.analysis import gagne_conditional_pressure as model  # noqa: E402

BUNDLE = ROOT / 'docs/analysis/sci_md_gagne_conditional_pressure_001'
PAIRS = ('V/B', 'V/N', 'B/N', 'V/W', 'B/W', 'W/N')
_DATA = None


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + '\n')


def init_worker(shots):
    global _DATA
    _DATA = shots


def run_fit(job):
    held, arm, counts, screen, temperature, tighter = job
    weights = model.training_counts(counts, held)
    result = model.fit(_DATA, weights, arm, screen['ST'], temperature, tighter)
    one = _DATA.subset([held])
    pred, amp = model.predict(one, arm, result['theta'], temperature)
    return dict(held=held, arm=arm, fit=result, screen=screen,
                mse=float(model.per_shot_mse(one, pred)[0]),
                prediction=pred[0].tolist(), amplitude=float(amp[0]))


def check_budget(start):
    if time.monotonic() - start > 5400:
        raise TimeoutError('Frozen 90-minute numerical budget exhausted; retain checkpoints')


def folds(shots, temperature, private, label, start, tighter=False, screens=None):
    counts = np.ones(len(shots.ids), dtype=int)
    keys = [(held, arm) for held in range(len(shots.ids)) for arm in ('V', 'B')]
    if screens is None:
        screening = model.Screening(shots, temperature)
        screens = screening.many([(arm, model.training_counts(counts, held)) for held, arm in keys])
    jobs = [(held, arm, counts, screen, temperature, tighter)
            for (held, arm), screen in zip(keys, screens, strict=True)]
    predictions = {arm: model.predict(shots, arm, use_temperature=temperature)[0]
                   for arm in ('N', 'W')}
    predictions.update({arm: np.empty_like(shots.pressure) for arm in ('V', 'B')})
    with ProcessPoolExecutor(max_workers=4, mp_context=multiprocessing.get_context('spawn'),
                             initializer=init_worker, initargs=(shots,)) as pool:
        results = list(pool.map(run_fit, jobs))
    for r in results:
        predictions[r['arm']][r['held']] = r['prediction']
    write_json(private / (label + '_fits.json'), results)
    np.savez_compressed(private / (label + '_predictions.npz'), **predictions,
                        time=shots.t, pressure=shots.pressure, flow=shots.flow,
                        temperature=shots.temperature, volume=shots.volume,
                        anchor_weights=shots.wa, evaluation_weights=shots.we)
    losses = {arm: float(np.sqrt(np.mean(model.per_shot_mse(shots, pred))))
              for arm, pred in predictions.items()}
    check_budget(start)
    print(label, 'completed', round(time.monotonic()-start, 1), 'seconds', flush=True)
    return predictions, losses, results, screens


def bootstrap(shots, private, start):
    rng = np.random.default_rng(model.SEED)
    counts = np.array([np.bincount(rng.integers(0, len(shots.ids), len(shots.ids)),
                                 minlength=len(shots.ids)) for _ in range(1000)])
    np.save(private / 'bootstrap_counts.npy', counts)
    # Explicit invalid-replicate records; absent replicate losses remain NaN in
    # private numeric arrays and are never silently made zero or omitted from n.
    losses = np.full((1000, 4), np.nan)
    invalid = []
    shot_rmse = np.full((1000, len(shots.ids), 4), np.nan)
    screening = model.Screening(shots)
    control_mse = {arm: model.per_shot_mse(shots, model.predict(shots, arm)[0])
                   for arm in ('N', 'W')}
    st_summary = []
    with ProcessPoolExecutor(max_workers=4, mp_context=multiprocessing.get_context('spawn'),
                             initializer=init_worker, initargs=(shots,)) as pool, \
            (private / 'bootstrap_fit_log.jsonl').open('w') as log:
        for lo in range(0, 1000, 10):
            check_budget(start)
            keys = []
            requests = []
            for b in range(lo, min(lo+10, 1000)):
                if np.count_nonzero(counts[b]) < 2:
                    invalid.append(dict(replicate=b, reason='all copies are the same physical shot'))
                    continue
                for held in np.flatnonzero(counts[b]):
                    for arm in ('V', 'B'):
                        keys.append((b, int(held), arm))
                        requests.append((arm, model.training_counts(counts[b], held)))
            screens = screening.many(requests) if requests else []
            jobs = [(held, arm, counts[b], screen, True, False)
                    for (b, held, arm), screen in zip(keys, screens, strict=True)]
            accum = {}
            for (b, held, arm), result in zip(keys, pool.map(run_fit, jobs), strict=True):
                accum.setdefault(b, {}).setdefault(arm, 0.)
                accum[b][arm] += counts[b, held] * result['mse'] / counts[b].sum()
                shot_rmse[b, held, model.ARMS.index(arm)] = np.sqrt(result['mse'])
                # Include multiplicity and every optimizer start; no raw traces.
                result.pop('prediction')
                log.write(json.dumps(dict(replicate=b, counts=counts[b].tolist(), **result))+'\n')
                st_summary.append(result['screen'])
            for b, values in accum.items():
                for arm in ('N', 'W'):
                    values[arm] = float(np.dot(counts[b], control_mse[arm]) / counts[b].sum())
                    present = np.flatnonzero(counts[b])
                    shot_rmse[b, present, model.ARMS.index(arm)] = np.sqrt(control_mse[arm][present])
                losses[b] = [np.sqrt(values[arm]) for arm in model.ARMS]
            log.flush()
            np.save(private / 'bootstrap_losses.npy', losses)
            if lo % 50 == 0 or lo == 990:
                print('bootstrap', lo+10, '/1000', round(time.monotonic()-start, 1), 'seconds', flush=True)
    check_budget(start)
    np.save(private / 'bootstrap_shot_rmse.npy', shot_rmse)
    return losses, invalid, st_summary, shot_rmse


def compare(losses, boot):
    comparisons = {}
    for pair in PAIRS:
        a, b = pair.split('/')
        x, y = boot[:, model.ARMS.index(a)], boot[:, model.ARMS.index(b)]
        finite = np.isfinite(x) & np.isfinite(y) & (y > 0)
        gci = np.quantile(1-x[finite]/y[finite], [.025, .975]).tolist()
        dci = np.quantile(x[finite]-y[finite], [.025, .975]).tolist()
        gain = 1-losses[a]/losses[b]
        comparisons[pair] = dict(difference_bar=losses[a]-losses[b], gain=gain,
                                 difference_ci95_bar=dci, gain_ci95=gci,
                                 valid_replicates=int(finite.sum()),
                                 band=model.band(gain), ci_bands=model.intersected_bands(gci),
                                 boundary_sensitivity=[dict(lower=.1*l, upper=.25*u,
                                     band=model.band(gain, .1*l, .25*u),
                                     ci_bands=model.intersected_bands(gci, .1*l, .25*u))
                                     for l in (.75, 1., 1.25) for u in (.75, 1., 1.25)])
    return comparisons


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--private-output', type=Path, required=True)
    parser.add_argument('--output', type=Path, default=BUNDLE)
    args = parser.parse_args()
    private = args.private_output.resolve()
    if private.is_relative_to(ROOT):
        raise ValueError('Detailed source-derived arrays must remain outside Git')
    private.mkdir(parents=True, exist_ok=True, mode=0o700)
    args.output.mkdir(parents=True, exist_ok=True)
    plan_path = BUNDLE / 'PLAN.json'
    plan = json.loads(plan_path.read_text())
    for path, sha in plan['sources'].items():
        if digest(ROOT/path) != sha:
            raise ValueError('Hash-bound input changed: '+path)
    start = time.monotonic()
    write_json(private/'execution_start.json', dict(plan_sha256=digest(plan_path),
               started_utc=__import__('datetime').datetime.now(__import__('datetime').timezone.utc).isoformat(),
               implementation_sha256=digest(ROOT/'puckworks/analysis/gagne_conditional_pressure.py'),
               runner_sha256=digest(Path(__file__))))
    shots = model.prepare()
    if len(shots.ids) != 11 or shots.na != 24 or shots.we.shape[1] != 134:
        raise ValueError('Frozen 11-shot/sample identity contract failed')
    for shot, row in zip(shots.ids, plan['shots'], strict=True):
        if shot != row['id']:
            raise ValueError('Shot identity changed')
    predictions, losses, results, screens = folds(shots, True, private, 'primary', start)
    # Primary checkpoint is retained even if the budget is exhausted later.
    write_json(private/'primary_checkpoint.json', dict(losses=losses, screens=screens))
    boot, invalid, boot_screens, shot_boot = bootstrap(shots, private, start)
    comparisons = compare(losses, boot)
    sensitivities = {}
    for scenario in plan['sensitivities']:
        scenario_shots = model.prepare(drift=scenario['flow_drift'])
        _, sloss, sresults, _ = folds(scenario_shots, scenario['h'], private,
                                       scenario['name'], start)
        sensitivities[scenario['name']] = dict(losses_bar=sloss,
            gains={pair:1-sloss[pair[0]]/sloss[pair[2]] for pair in PAIRS},
            free_dimensions=[r['fit']['free_dimensions'] for r in sresults])
    _, reference, ref_results, _ = folds(shots, True, private, 'tighter_reference', start,
                                         tighter=True, screens=screens)
    reduction = {arm:model.independent_loss(shots,pred) for arm,pred in predictions.items()}
    numerical_delta = {arm:abs(reference[arm]-losses[arm]) for arm in model.ARMS}
    rows = []
    for arm in model.ARMS:
        score = model.shot_scores(shots, predictions[arm])
        for i,sid in enumerate(shots.ids):
            row = dict(shot_id=sid, arm=arm, anchor_samples=shots.na,
                       evaluation_samples=shots.we.shape[1],
                       **{key:float(value[i]) for key,value in score.items()})
            if arm in ('V','B'):
                r = next(r for r in results if r['held']==i and r['arm']==arm)
                row.update(a=r['fit']['theta'][0], L_ml=np.exp(r['fit']['theta'][1]),
                           free_dimensions=r['fit']['free_dimensions'],
                           a_boundary=min(r['fit']['u'][0],1-r['fit']['u'][0])<1e-7,
                           L_boundary=min(r['fit']['u'][1],1-r['fit']['u'][1])<1e-7)
            distribution = shot_boot[:, i, model.ARMS.index(arm)]
            finite = distribution[np.isfinite(distribution)]
            low, high = np.quantile(finite, [.025, .975])
            row.update(refit_rmse_p025_bar=float(low), refit_rmse_p975_bar=float(high),
                       refit_replicates=int(len(finite)))
            rows.append(row)
    fields = list(dict.fromkeys(key for row in rows for key in row))
    with (args.output/'SHOT_SCORES.csv').open('w') as stream:
        writer=csv.DictWriter(stream,fieldnames=fields);writer.writeheader();writer.writerows(rows)
    mse={arm:model.per_shot_mse(shots,pred) for arm,pred in predictions.items()}
    influence=[]
    for i,sid in enumerate(shots.ids):
        reduced={arm:float(np.sqrt(np.mean(np.delete(v,i)))) for arm,v in mse.items()}
        influence.append(dict(shot_id=sid,removed_score_only_losses=reduced,
             removed_score_only_gains={pair:1-reduced[pair[0]]/reduced[pair[2]] for pair in PAIRS},
             paired_mse_bar2={pair:float(mse[pair[0]][i]-mse[pair[2]][i]) for pair in PAIRS}))
    st=np.array([s['ST'] for s in boot_screens]); dims=[s['free_dimensions'] for s in boot_screens]
    decision=('RETAIN_V_CONDITIONAL_PREDICTOR' if all(comparisons[p]['gain_ci95'][0]>0 for p in ('V/B','V/N'))
              else 'RETAIN_SIMPLER_COMPARATOR' if any(comparisons[p]['gain_ci95'][1]<0 for p in ('V/B','V/N'))
              else 'V_ADVANTAGE_UNRESOLVED')
    output=dict(task=plan['task'],plan_sha256=digest(plan_path),decision=decision,
        physical_shots=len(shots.ids),anchor_samples=264,evaluation_samples=1474,
        coverage={a:'11/11 shots; 1474/1474 evaluation observations' for a in model.ARMS},
        primary_losses_bar=losses,comparisons=comparisons,
        per_shot_uncertainty='RMSE 2.5/97.5 percentiles conditional on that identity being sampled; training-refit variation only, not sensor or future-shot prediction intervals. N/W are degenerate because training does not affect them.',
        screening_design=dict(base_n=512, expanded=2048, unique_evaluations=2048),
        bootstrap=dict(requested=1000,invalid=invalid,finite=int(np.isfinite(boot).all(axis=1).sum()),
                       seed=model.SEED,fit_count=len(boot_screens),
                       ST_min=st.min(axis=0).tolist(),ST_max=st.max(axis=0).tolist(),
                       free_dimension_counts={str(d):dims.count(d) for d in set(dims)}),
        primary_fits=[{k:v for k,v in r.items() if k not in ('prediction',)} for r in results],
        sensitivities=sensitivities,influence=influence,
        numerics=dict(target_bar=.001,tighter_losses_bar=reference,
                      aggregate_loss_changes_bar=numerical_delta,
                      target_met=max(numerical_delta.values())<=.001,
                      independent_losses_bar=reduction,
                      independent_reduction_max_delta=max(abs(reduction[a]-losses[a]) for a in model.ARMS),
                      primary_max_start_nfev=max(s['nfev'] for r in results for s in r['fit']['starts']),
                      primary_nonconverged_starts=sum(not s['success'] for r in results for s in r['fit']['starts'])),
        compute=dict(wall_seconds=time.monotonic()-start,budget_seconds=5400,workers=4,
                     versions={p:importlib.metadata.version(p) for p in ('numpy','scipy','jax','jaxgsa')},
                     implementation_sha256=digest(ROOT/'puckworks/analysis/gagne_conditional_pressure.py'),
                     runner_sha256=digest(Path(__file__))),
        private_artifacts={p.name:digest(p) for p in sorted(private.iterdir()) if p.is_file()
                           and any(s in p.name for s in ('prediction','bootstrap','fits.json','execution_start'))})
    # Keep the public bundle compact: all nine starts stay in private receipts;
    # fitted parameters, bounds, ST intervals, dimensions and cost are public.
    for r in output['primary_fits']:
        r['fit']['start_summary']=dict(count=len(r['fit']['starts']),
            max_nfev=max(s['nfev'] for s in r['fit']['starts']),
            nonconverged=sum(not s['success'] for s in r['fit']['starts']))
        del r['fit']['starts']
    write_json(args.output/'COMPARISONS.json',output)
    print(json.dumps(dict(decision=decision,losses=losses,wall_seconds=time.monotonic()-start)),flush=True)


if __name__ == '__main__':
    main()
