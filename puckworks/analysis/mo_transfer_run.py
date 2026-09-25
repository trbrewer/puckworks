"""Bounded fit/predict/once-only score primitives for SCI-MD-MO-TRANSFER-001.

This task's source contract currently blocks real-response execution. Numerical
verification and artifact preparation do not remove that gate.
"""
import hashlib
import json
from pathlib import Path
import numpy as np
from scipy.optimize import minimize
from .mo_transfer import simulate, populations, Bed

CANDIDATES = ('S0', 'S2', 'D2')
COORDINATE_KEYS = frozenset(('row_id', 'condition_id', 'powder', 'flow_m3_s', 'mass_kg',
                            'theta_f', 'theta_c', '2R_f_um', '2R_c_um'))


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def require_authority(contract, review, freeze_path):
    if not any(contract['eligible_axes'].values()):
        raise RuntimeError('BLOCKED_SOURCE_CONTRACT: '+ '; '.join(contract['missing_facts']))
    if contract['numerical_status'] != 'QUALIFIED':
        raise RuntimeError('NUMERICALLY_UNRESOLVED')
    if (review.get('decision') != 'APPROVED_FOR_SCORING'
            or review.get('freeze_sha256') != digest(freeze_path)):
        raise RuntimeError('INDEPENDENT_PRE_SCORING_REVIEW_PENDING_OR_MISMATCHED')


def grouped_folds(rows, axis):
    key = {'flow': 'flow_m3_s', 'powder': 'powder'}[axis]
    for level in sorted({r[key] for r in rows}):
        train = [dict(r) for r in rows if r[key] != level]
        # Enforced projection is the only held-fold payload admitted by fit_predict.
        coordinates = [{k:v for k,v in r.items() if k in COORDINATE_KEYS}
                       for r in rows if r[key] == level]
        yield str(level), train, coordinates


def condition_rmse(rows, predictions):
    groups = sorted({r['condition_id'] for r in rows})
    residual = np.asarray(predictions)-np.array([r['ey_pct'] for r in rows])
    return {g: float(np.sqrt(np.mean(residual[[r['condition_id']==g for r in rows]]**2)))
            for g in groups}


def adequate(rmses, allowance):
    values = np.asarray(list(rmses.values()))
    return bool(len(values) and np.mean(values)+allowance <= 1
                and np.max(values)+allowance <= 2)


def axis_decision(candidate, comparator, allowance_candidate, allowance_comparator,
                  training_candidate, training_comparator):
    """Nine-condition, conservative paired arithmetic; no absent folds allowed."""
    if len(candidate)!=9 or set(candidate)!=set(comparator):
        raise ValueError('complete matching nine-condition axis required')
    if len(training_candidate)!=3 or len(training_comparator)!=3:
        raise ValueError('all three training-fold dispositions required')
    keys = sorted(candidate)
    a, b = np.array([candidate[k] for k in keys]), np.array([comparator[k] for k in keys])
    ambiguity = allowance_candidate+allowance_comparator
    adequate_training = all(training_candidate) and all(training_comparator)
    gain = float(b.mean()-a.mean()-ambiguity)
    required = max(.25, .2*float(b.mean()))
    improving = int(np.count_nonzero(b-a > ambiguity))
    worsening = float(np.max(a-b+ambiguity))
    predictive = adequate(candidate, allowance_candidate)
    passed = adequate_training and predictive and gain >= required and improving>=7 and worsening<=.5
    return dict(verdict='MATERIAL_TRANSFER_GAIN' if passed else
                ('CALIBRATION_INADEQUATE' if not adequate_training else 'NO_EARNED_MATERIAL_GAIN'),
                candidate_score=float(a.mean()), comparator_score=float(b.mean()),
                conservative_gain=gain, required_gain=required,
                conditions_improved=improving, worst_worsening_with_allowance=worsening,
                predictive_adequacy=predictive, paired_training_adequacy=adequate_training)


def simpler_comparator(training_scores, allowance):
    # Ties within the combined numerical allowance choose S0.
    return 'S2' if training_scores['S2']+2*allowance < training_scores['S0'] else 'S0'


def fit_predict(training_rows, held_coordinates, candidate, contract, start_index):
    """One deterministic start; callers must establish review authority first.

    Held response fields are rejected even if unused. All objective evaluations,
    failed evaluations and cache hits count toward the same <=100-call budget.
    No analytical amplitude reduction or additional normalization is used.
    """
    if any(set(r)-COORDINATE_KEYS for r in held_coordinates):
        raise ValueError('withheld response or unknown fields passed to fitting')
    if start_index not in (0,1) or candidate not in CANDIDATES:
        raise ValueError('unregistered candidate/start')
    if not contract['source_ready']:
        raise RuntimeError('BLOCKED_SOURCE_CONTRACT')
    if contract['inventory_sharing'] not in ('per_powder_flow_only', 'shared'):
        raise ValueError('inventory sharing has not been qualified')
    bed = Bed(**contract['bed'])
    powders = sorted({r['powder'] for r in training_rows})
    per_powder = contract['inventory_sharing']=='per_powder_flow_only'
    labels = powders if per_powder else ['shared']
    if per_powder and any(r['powder'] not in powders for r in held_coordinates):
        raise ValueError('powder-transfer forbidden with per-powder inventory')
    lower, upper = contract['bounds'][candidate]
    bounds = [(np.log10(.0001),0)]*len(labels)+list(zip(np.log10(lower),np.log10(upper)))
    start = contract['starts'][candidate][start_index]
    x0 = np.log10([start[0]]*len(labels)+start[1:])
    record = dict(candidate=candidate,start=start_index,evaluations=0,cache_hits=0,
                  trajectories_launched=0,trajectories_completed=0,solver_calls=0,
                  failed_evaluations=[], evaluated_parameters=[], best_loss=None,
                  solver_calls_are_lower_bound_if_trajectory_fails=True)
    cache = {}
    best = [np.inf,None,None]

    def predict(rows, parameters):
        values = np.empty(len(rows))
        for condition in sorted({r['condition_id'] for r in rows}):
            indices = [i for i,r in enumerate(rows) if r['condition_id']==condition]
            subset = [rows[i] for i in indices]
            order = np.argsort([r['mass_kg'] for r in subset])
            first = subset[0]
            wi,ri = populations(first)
            inventory = parameters[labels.index(first['powder'])] if per_powder else parameters[0]
            record['trajectories_launched'] += 1
            result = simulate(candidate,bed,wi,ri,first['flow_m3_s'],inventory,
                              parameters[-2],parameters[-1],
                              [subset[i]['mass_kg'] for i in order],**contract['numerics'])
            record['trajectories_completed'] += 1
            record['solver_calls'] += result['solver_calls']
            for i,v in zip(order,result['ey_pct']):
                values[indices[i]] = v
        return values

    def objective(x):
        record['evaluations'] += 1
        if record['evaluations']>100:
            raise RuntimeError('evaluation cap exceeded')
        key = tuple(x)
        if key in cache:
            record['cache_hits'] += 1
            return cache[key]
        params = 10**np.asarray(x)
        record['evaluated_parameters'].append(params.tolist())
        try:
            values = predict(training_rows,params)
            rmses = condition_rmse(training_rows,values)
            loss = float(np.mean(np.square(list(rmses.values()))))
            if loss<best[0]:
                best[:] = [loss,params.copy(),values.copy()]
        except (RuntimeError, ValueError, FloatingPointError) as exc:
            record['failed_evaluations'].append(dict(parameters=params.tolist(),reason=str(exc)))
            loss = 1e30
        cache[key] = loss
        return loss

    fit = minimize(objective,x0,method='Nelder-Mead',bounds=bounds,
                   options=dict(maxfev=100,xatol=1e-4,fatol=1e-6,adaptive=False))
    record['stopping_reason'] = str(fit.message)
    record['optimizer_success'] = bool(fit.success)
    if best[1] is None:
        record['status'] = 'NO_VALID_TRAINING_EVALUATION'
        return record
    record.update(status='COMPLETED_BOUNDED_START',best_loss=best[0],parameters=best[1].tolist(),
                  training_predictions=best[2].tolist())
    record['bound_hits'] = [i for i,(x,(lo,hi)) in enumerate(zip(np.log10(best[1]),bounds))
                           if min(abs(x-lo),abs(x-hi))<=1e-4]
    try:
        record['held_predictions'] = predict(held_coordinates,best[1]).tolist()
    except (RuntimeError,ValueError,FloatingPointError) as exc:
        record.update(status='PREDICTION_FAILED',prediction_failure=str(exc))
    return record


def freeze_predictions(path, records):
    path = Path(path)
    with path.open('x') as f:
        json.dump(records,f,indent=2,allow_nan=False)
        f.write('\n')
    return digest(path)


def score_once(prediction_path, expected_hash, marker_path, rows, predictions):
    """Scoring consumes an already frozen bundle; exclusive marker prevents replay."""
    if digest(prediction_path)!=expected_hash:
        raise ValueError('prediction freeze mismatch')
    # Caller must pass the values actually present in the frozen record.
    frozen = json.loads(Path(prediction_path).read_text())
    if [r['row_id'] for r in rows] != frozen['row_ids']:
        raise ValueError('row identity/order differs from immutable artifact')
    if predictions != frozen['predictions']:
        raise ValueError('predictions differ from immutable artifact')
    with Path(marker_path).open('x') as f:
        json.dump({'prediction_sha256':expected_hash,'status':'SCORING_INVOKED'},f)
    return condition_rmse(rows,predictions)


def main():
    import argparse
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--bundle',type=Path,default=Path(__file__).resolve().parents[2]/'docs/analysis/sci_md_mo_transfer_001')
    args=parser.parse_args()
    contract=json.loads((args.bundle/'contract.json').read_text())
    review_path=args.bundle/'review/pre_scoring_approval.json'
    review=json.loads(review_path.read_text()) if review_path.exists() else {}
    require_authority(contract,review,args.bundle/'freeze.json')
    # A resolved operator materially changes this source-blocked preparation.
    # Do not let hand-edited readiness flags silently authorize a new experiment.
    raise RuntimeError('SOURCE_QUALIFIED_ORCHESTRATION_NOT_RELEASED: preparation only; no fitted run exists')


if __name__=='__main__':
    main()
