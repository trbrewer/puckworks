"""SCI-MD-MASS-DELIVERY-001 source adapter and bounded development/evaluation.

Raw inputs and row-level outputs belong outside Git. Source-derived artifacts
retain Pannusch/Schmieder attribution and CC-BY-NC-3.0 treatment.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess

import numpy as np
from scipy.optimize import least_squares, lsq_linear

from puckworks.analysis.mass_delivery import (
    Model, compact_delivery, concentration_to_fraction, integration_allowance,
    linear_basis_integral, mass_to_kg, LIMITATIONS,
)
# Reuse the qualified reconstruction's source resolution, parser and assay mapping.
from tools.data_availability_preflight import config_path
from tools.pannusch2024_reconstruct import SAMP, FIDS, rows, mat, workbook, digest

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / 'puckworks/data/pannusch2024'
TASK = 'SCI-MD-MASS-DELIVERY-001'
FIT = (9, 10, 11, 14, 15)
PRIMARY = ('PRED-C01', 'PRED-C02', 'PRED-C05', 'PRED-C06')
TEMP = ('PRED-C03', 'PRED-C04')
FLOW = ('PRED-C07', 'PRED-C08')
STARTS = ((.2,.03,1),(.3,.08,1),(.1,.02,.5),(.5,.1,2),
          (.25,.05,4),(.4,.15,.25),(.15,0,1),(.75,.3,3))
RIGHTS = 'CC-BY-NC-3.0; Pannusch/Schmieder; Mendeley 10.17632/y2tz67f6ry.1; derived artifact, not MIT'
COORD_KEYS = ('campaign', 'condition', 'shot', 'fraction', 'mass_kg', 'b0', 'b1',
              't0', 't1', 'source_id', 'mass_basis', 'mass_prefix')
MODELS = ('MASS', 'TIME', 'TIME_u2', 'TIME_sqrt', 'BOUNDARY_AWARE_EMPIRICAL')


def write_json(path, value):
    with Path(path).open('x') as f:
        json.dump(value, f, sort_keys=True, indent=2, allow_nan=False)
        f.write('\n')


def canonical_hash(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, allow_nan=False).encode()).hexdigest()


def source_paths():
    root = os.environ.get('PUCKWORKS_EXTERNAL_DATA_ROOT')
    if not root:
        root = json.loads(config_path().read_text())['sources'][
            'PANNUSCH2024_MENDELEY_FULL_REPOSITORY']['path']
    needed = ('P24-MAT-FIT', 'P24-MAT-PRED', 'P24-M-PREP-FIT', 'P24-M-PREP-PRED',
              'P24-DOE-FIT', 'P24-DOE-PRED')
    result = {}
    for r in rows(DATA/'source_inputs.csv'):
        if r['source_id'] in needed:
            p = Path(root)/r['source_relpath']
            if digest(p) != r['sha256']:
                raise ValueError('source hash mismatch: '+r['source_id'])
            result[r['source_id']] = p
    if set(result) != set(needed):
        raise ValueError('missing source identity')
    return result


def deduplicate(records, keys):
    out = {}
    for row in records:
        key = tuple(row[k] for k in keys)
        if key in out and out[key] != row:
            raise ValueError('conflicting duplicate analytical identity')
        out[key] = row
    return list(out.values())


def mass_coordinates(run):
    """Read existing shot-specific complete prefixes; never accepts chemistry."""
    masses = np.asarray(run.mE, float)
    prefix = np.asarray(run.mE_cum, float)
    times = np.asarray(run.tE, float)
    if len(masses) not in (10, 11) or masses.shape != prefix.shape or times.shape != prefix.shape:
        raise ValueError('incomplete source collection sequence')
    if not np.isfinite([masses, prefix, times]).all() or np.any(masses <= 0):
        raise ValueError('invalid source mass prefix')
    if not np.allclose(prefix, np.cumsum(masses), atol=1e-10, rtol=0):
        raise ValueError('source mass-prefix disagreement')
    if np.any(np.diff(np.r_[0., times]) <= 0):
        raise ValueError('invalid source collection clock')
    out = []
    for idx, fid in zip(SAMP, FIDS):
        out.append({'fraction': fid, 'mass_kg': float(mass_to_kg(masses[idx], 'g')),
                    'b0': float(mass_to_kg(prefix[idx-1] if idx else 0., 'g')),
                    'b1': float(mass_to_kg(prefix[idx], 'g')),
                    't0': float(times[idx-1] if idx else 0.), 't1': float(times[idx]),
                    'mass_basis': 'MEASURED_MASS_G',
                    'mass_prefix': 'SOURCE_SHOT_mE_cum_ALL_INTERVENING_VIALS',
                    'collection_count': len(masses),
                    'collection_mass_kg': float(mass_to_kg(prefix[-1], 'g'))})
    return out


def measured_mass_check(path, shot_index, run, prediction):
    # Read only mass cells for this physical shot. Workbook IDs are source ordinal IDs.
    sheet = workbook(path)['SampleWeights']
    if prediction or shot_index <= 32:
        row, col = 2*shot_index+1, 3
    else:
        row, col = 2*(shot_index-32)+1, 15
    expected_id = sheet.cell(row, col-2).value
    if expected_id != shot_index:
        raise ValueError('source workbook physical-shot ID mismatch')
    net = []
    for j in range(len(run.mE)):
        empty, full = sheet.cell(row, col+j).value, sheet.cell(row+1, col+j).value
        if not isinstance(empty, (int, float)) or not isinstance(full, (int, float)):
            raise ValueError('missing measured prefix; source imputation is not measured mass')
        net.append(full-empty)
    if not np.allclose(net, run.mE, atol=1e-10, rtol=0):
        raise ValueError('workbook and qualified source mass disagreement')


def coordinates(campaign, paths):
    prediction = campaign == 'PREDICTION_2022_03'
    if campaign not in ('FIT_2021_12', 'PREDICTION_2022_03'):
        raise ValueError('unsupported campaign')
    label = 'PRED' if prediction else 'FIT'
    source_id = 'P24-MAT-'+label
    experiments = tuple(range(1, 9)) if prediction else FIT
    register = [r for r in rows(DATA/'experiment_register.csv')
                if r['campaign_id'] == campaign and int(r['source_experiment_id']) in experiments]
    expected = {f'{label}-E{i:02d}-R{j}' for i in experiments for j in (1, 2, 3)}
    if len(register) != len(expected) or {r['shot_id'] for r in register} != expected:
        raise ValueError('material source cohort mismatch')
    grinds = {(r['campaign_id'], int(r['source_experiment_id'])): float(r['grind_setting'])
              for r in rows(DATA/'experiment_grind_assignments.csv')}
    objects = mat(paths[source_id])['ExperimentalData']
    result = []
    for record in register:
        i, j = int(record['source_experiment_id']), int(record['physical_replicate_id'])
        if grinds[(campaign, i)] != 1.7 or float(record['grind_setting']) != 1.7:
            raise ValueError('material grind mismatch')
        run = objects[i-1].run[j-1]
        measured_mass_check(paths['P24-DOE-'+label], 3*(i-1)+j, run, prediction)
        for r in mass_coordinates(run):
            result.append(dict(r, campaign=campaign, condition=record['condition_id'],
                               shot=record['shot_id'], source_id=source_id))
    return result


def attach_chemistry(coords, *, allow_campaign):
    """Only training stage calls with FIT; scoring calls PRED after audit/hash gate."""
    if {r['campaign'] for r in coords} != {allow_campaign}:
        raise ValueError('chemistry role violation')
    pred = allow_campaign == 'PREDICTION_2022_03'
    name = 'prediction_fraction_replicates.csv' if pred else 'fit_fraction_replicates.csv'
    source = deduplicate([r for r in rows(DATA/name) if r['analyte'] == 'TDS'],
                         ('campaign_id', 'shot_id', 'fraction_id', 'analyte'))
    index = {(r['shot_id'], int(r['fraction_id'])): r for r in source}
    out = []
    for coordinate in coords:
        r = index[(coordinate['shot'], coordinate['fraction'])]
        if r['campaign_id'] != coordinate['campaign'] or r['condition_id'] != coordinate['condition']:
            raise ValueError('chemical identity mismatch')
        if r['concentration_unit'] != 'percent' or (not pred and r['fraction_basis'] != 'MEASURED_MASS_G'):
            raise ValueError('unsupported source unit/basis')
        mass = float(mass_to_kg(float(r['fraction_liquid_g_or_ml']), 'g'))
        if abs(mass-coordinate['mass_kg']) > 5.01e-12:
            raise ValueError('rounded source mass mismatch')
        value = r['measured_concentration' if pred else 'concentration_value']
        valid = r['validity'] == 'VALID' and value != ''
        q = float(concentration_to_fraction(float(value), 'percent')) if valid else None
        solute = coordinate['mass_kg']*q if valid else None
        rounding = 0.
        if valid:
            derived = float(mass_to_kg(float(r['derived_analyte_mass_mg' if pred else 'analyte_mass_mg']), 'mg'))
            rounding = coordinate['mass_kg']*5e-11 + q*5e-12 + 5e-15
            if abs(solute-derived) > rounding+1e-17:
                raise ValueError('source-derived solute differs beyond displayed rounding')
        out.append(dict(coordinate, eligible=valid, q=q, solute_kg=solute,
                        source_rounding_allowance_kg=rounding))
    return out


def project(rows_):
    return [{k: r[k] for k in COORD_KEYS} for r in rows_]


def arrays(records):
    return tuple(np.array([r[k] for r in records], float) for k in ('b0', 'b1', 't0', 't1'))


def training_weights(records):
    if any(r['campaign'] != 'FIT_2021_12' for r in records):
        raise ValueError('held campaign cannot enter fitting')
    conditions = sorted({r['condition'] for r in records})
    shots = {c: sorted({r['shot'] for r in records if r['condition'] == c}) for c in conditions}
    totals = {s: sum(r['mass_kg'] for r in records if r['shot'] == s and r['eligible'])
              for ss in shots.values() for s in ss}
    if not totals or min(totals.values()) <= 0:
        raise ValueError('empty training shot support')
    good = [r for r in records if r['eligible'] and r['mass_kg'] > 0]
    weights = np.array([np.sqrt(r['mass_kg']/(len(conditions)*len(shots[r['condition']])*totals[r['shot']]))
                        for r in good])
    return good, weights


def identity(records):
    return {'task': TASK, 'campaign': 'FIT_2021_12', 'grind': 1.7,
            'conditions': sorted({r['condition'] for r in records}),
            'shots': sorted({r['shot'] for r in records}), 'training_sha256': canonical_hash(records),
            'target_exposure': 'TARGET_EXPOSED', 'source_scope': 'SOURCE_INTERNAL'}


def make_model(name, coeff, training, **kwargs):
    return Model(TASK+'/'+name+'/v1', 'TIME' if name.startswith('TIME') else name,
                 tuple(coeff), (0., max(r['b1'] for r in training)), identity(training), RIGHTS,
                 claims=LIMITATIONS+('SOURCE_INTERNAL', 'TARGET_EXPOSED',
                                      'PANNUSCH_SOURCE_SPECIFIC_COEFFICIENTS'), **kwargs)


def fit_compact(training, name):
    good, weights = training_weights(training)
    b0, b1, t0, t1 = arrays(good)
    y = np.array([r['q'] for r in good])
    time = name.startswith('TIME')
    timing = name.removeprefix('TIME_') if '_' in name else 'linear'
    factor = 1 if time else 1000
    attempts, solutions = [], []
    for idx, base in enumerate(STARTS):
        start = np.array(base)*[1, factor, 1]
        calls, last = 0, {}
        def residual(x):
            nonlocal calls
            if calls >= 2000:
                raise RuntimeError('actual residual evaluation cap')
            calls += 1
            pred = compact_delivery(b0, b1, x, time_bounds=(t0, t1) if time else None,
                                    timing=timing)/(b1-b0)
            r = 100*(pred-y)*weights
            last.update(parameters=x.tolist(), loss=float(r@r))
            return r
        initial = residual(start)
        rec = {'start_index': idx, 'start': start.tolist(), 'initial_loss': float(initial@initial)}
        try:
            fit = least_squares(residual, start, bounds=([0,0,.25],[1,10*factor,4]),
                                method='trf', jac='2-point', tr_solver='exact', loss='linear',
                                ftol=1e-10, xtol=1e-10, gtol=1e-10, diff_step=1e-6,
                                x_scale=[.2,.05*factor,1], max_nfev=2000)
            rec.update(success=bool(fit.success), status=int(fit.status), message=fit.message,
                       parameters=fit.x.tolist(), loss=float(2*fit.cost),
                       optimizer_nfev=int(fit.nfev), optimizer_njev=int(fit.njev))
            if fit.success:
                solutions.append((float(2*fit.cost), idx, fit.x.tolist()))
        except (RuntimeError, ValueError, FloatingPointError) as error:
            rec.update(success=False, message=str(error), last=last,
                       optimizer_nfev=None, optimizer_njev=None)
        rec['actual_residual_evaluations'] = calls
        attempts.append(rec)
    if not solutions:
        return None, {'attempts': attempts, 'status': 'ALL_STARTS_FAILED'}
    loss, idx, theta = min(solutions)
    kwargs = {'timing': timing, 'time_domain_s': (0., max(r['t1'] for r in training))} if time else {}
    model = make_model(name, theta, training, **kwargs)
    return model, {'attempts': attempts, 'selected_start': idx, 'loss': loss, 'status': 'CONVERGED'}


def fit_empirical(training, count, penalty):
    good, weights = training_weights(training)
    b0, b1, _, _ = arrays(good)
    knots = np.linspace(0, max(r['b1'] for r in training), count)
    design = linear_basis_integral(b0, b1, knots)/(b1-b0)[:, None]
    d2 = np.diff(np.eye(count), n=2, axis=0)*(count-1)**2
    a = np.vstack((100*weights[:, None]*design, 100*np.sqrt(penalty/(count-2))*d2))
    y = np.r_[100*weights*np.array([r['q'] for r in good]), np.zeros(count-2)]
    fit = lsq_linear(a, y, bounds=(0., 1.), tol=1e-12, max_iter=1000, method='trf')
    if not fit.success:
        raise RuntimeError('bounded empirical fit failed')
    model = make_model('BOUNDARY_AWARE_EMPIRICAL', fit.x, training, knots_kg=tuple(knots))
    return model, {'knots': count, 'lambda': penalty, 'cost': float(2*fit.cost),
                   'iterations': fit.nit, 'status': int(fit.status)}


def loco(records):
    for condition in sorted({r['condition'] for r in records}):
        train = [r for r in records if r['condition'] != condition]
        held = [r for r in records if r['condition'] == condition]
        if {r['shot'] for r in train} & {r['shot'] for r in held}:
            raise ValueError('physical shot split leak')
        yield condition, train, held


def predict(model, coords, verify=True):
    # This projection is an explicit information-flow boundary: no chemistry or totals.
    if any(set(r) != set(COORD_KEYS) for r in coords):
        raise ValueError('prediction requires coordinate-only records')
    b0, b1, t0, t1 = arrays(coords)
    tb = (t0, t1) if model.family == 'TIME' else None
    delivery = model.predict(b0, b1, time_bounds=tb, strict=False)
    result = []
    for i, r in enumerate(coords):
        supported = bool(delivery.in_domain[i])
        allowance = integration_allowance(model, r['b0'], r['b1'],
                    (r['t0'], r['t1']) if model.family == 'TIME' else None) if supported and verify else 0.
        result.append(dict(r, predicted_solute_kg=float(delivery.solute_kg[i]) if supported else None,
                           in_domain=supported, integration_allowance_kg=allowance,
                           numerical_qualified=supported and allowance <= 1e-9))
    return result


def shot_metrics(observed, predicted):
    if [(r['shot'], r['fraction']) for r in observed] != [(r['shot'], r['fraction']) for r in predicted]:
        raise ValueError('prediction/observation identity mismatch')
    result = []
    for shot in sorted({r['shot'] for r in observed}):
        pairs = [(o, p) for o, p in zip(observed, predicted) if o['shot'] == shot]
        eligible = [(o, p) for o, p in pairs if o['eligible'] and o['mass_kg'] > 0]
        supported = [(o, p) for o, p in eligible if p['in_domain']]
        r = {'shot': shot, 'condition': pairs[0][0]['condition'],
             'expected_assays': len(pairs), 'valid_assays': len(eligible),
             'supported_assays': len(supported),
             'out_of_domain_fractions': [o['fraction'] for o, p in pairs if not p['in_domain']],
             'assayed_mass_kg': sum(o['mass_kg'] for o, _ in eligible),
             'complete_collected_mass_kg': pairs[0][0]['collection_mass_kg'],
             'collection_intervals': pairs[0][0]['collection_count'],
             'chemistry_interval_coverage': len(eligible)/pairs[0][0]['collection_count'],
             'numerically_qualified': all(p['numerical_qualified'] for _, p in supported),
             'full_support': len(supported) == len(eligible) == len(pairs)}
        r['chemistry_mass_coverage'] = r['assayed_mass_kg']/r['complete_collected_mass_kg']
        metric = None
        if supported:
            mass = np.array([o['mass_kg'] for o, _ in supported])
            delta = np.array([p['predicted_solute_kg']-o['solute_kg'] for o, p in supported])
            allowance = np.array([p['integration_allowance_kg'] for _, p in supported])
            e = 100*delta/mass
            R = float(np.sqrt(np.sum(mass*e**2)/sum(mass)))
            B = float(100*sum(delta)/sum(mass))
            metric = {'R_pp': R, 'B_pp': B, 'abs_B_pp': abs(B),
                      'interval_solute_RMSE_g': float(1000*np.sqrt(np.mean(delta**2))),
                      'signed_assayed_total_error_g': float(1000*sum(delta)),
                      'absolute_assayed_total_error_g': float(1000*abs(sum(delta))),
                      'max_running_assayed_residual_g': float(1000*max(abs(np.cumsum(delta)))),
                      'R_allowance_pp': float(np.sqrt(sum(mass*(100*allowance/mass)**2)/sum(mass))),
                      'B_allowance_pp': float(100*sum(allowance)/sum(mass)),
                      'interval_RMSE_allowance_g': float(1000*np.sqrt(np.mean(allowance**2))),
                      'total_and_running_allowance_g': float(1000*sum(allowance)),
                      'max_interval_allowance_kg': float(max(allowance)),
                      'source_rounding_total_allowance_kg': float(sum(o['source_rounding_allowance_kg'] for o, _ in supported))}
        r['metrics'] = metric if r['full_support'] else None
        r['supported_only_diagnostic'] = metric if not r['full_support'] else None
        result.append(r)
    return result


def threshold(value, allowance, upper):
    if value+allowance <= upper:
        return 'PASS'
    if value-allowance > upper:
        return 'FAIL'
    return 'NUMERICALLY_UNRESOLVED'


def condition_metrics(shots):
    out = []
    for c in sorted({r['condition'] for r in shots}):
        rr = [r for r in shots if r['condition'] == c]
        valid = all(r['metrics'] is not None and r['numerically_qualified'] for r in rr)
        metric = {k: float(np.mean([r['metrics'][k] for r in rr])) for k in rr[0]['metrics']} if valid else None
        status = 'UNSUPPORTED_OR_UNQUALIFIED'
        if valid:
            decisions = [threshold(metric['R_pp'], metric['R_allowance_pp'], 1.),
                         threshold(metric['abs_B_pp'], metric['B_allowance_pp'], .5)]
            status = 'FAIL' if 'FAIL' in decisions else ('PASS' if decisions == ['PASS', 'PASS'] else 'NUMERICALLY_UNRESOLVED')
        out.append({'condition': c, 'shots': len(rr), 'qualified_shots': sum(r['full_support'] and r['numerically_qualified'] for r in rr),
                    'metrics': metric, 'adequacy': status})
    return out


def aggregate(conditions, expected):
    selected = [c for c in conditions if c['condition'] in expected]
    if {c['condition'] for c in selected} != set(expected):
        raise ValueError('condition denominator mismatch')
    valid = all(c['metrics'] is not None for c in selected)
    metric = {k: float(np.mean([c['metrics'][k] for c in selected])) for k in selected[0]['metrics']} if valid else None
    return {'expected_conditions': list(expected), 'conditions': len(selected),
            'passing_conditions': sum(c['adequacy'] == 'PASS' for c in selected),
            'adequate': all(c['adequacy'] == 'PASS' for c in selected),
            'adequacy_status': ('FAIL' if any(c['adequacy'] == 'FAIL' for c in selected) else
                'UNSUPPORTED_OR_UNQUALIFIED' if not valid else
                'PASS' if all(c['adequacy'] == 'PASS' for c in selected) else 'NUMERICALLY_UNRESOLVED'),
            'metrics': metric}


def development_score(shots):
    # All candidates share identical MASS domain within a fold. Any unsupported
    # observations remain counted; this is selection diagnostic, never adequacy.
    values = [r['metrics'] or r['supported_only_diagnostic'] for r in shots]
    if any(v is None for v in values):
        raise ValueError('no common supported LOCO diagnostic')
    return float(np.mean([r['R_pp'] for r in values]))


def source_manifest(paths, training_coords, held_coords):
    registers = ('source_inputs.csv', 'experiment_register.csv', 'experiment_grind_assignments.csv',
                 'exclusion_register.csv', 'fit_fraction_replicates.csv', 'prediction_fraction_replicates.csv',
                 'prediction_conditions.csv', 'DATA_DICTIONARY.md', 'PROVENANCE.md')
    return {'task': TASK, 'rights': RIGHTS, 'source_files': {k: digest(v) for k, v in paths.items()},
            'registers': {k: digest(DATA/k) for k in registers},
            'training': {'conditions': 5, 'shots': 15, 'assays': 90, 'source_experiments': list(FIT), 'grind': 1.7},
            'primary': {'conditions': list(PRIMARY), 'shots': 12, 'assays': 72},
            'temperature_ramp': {'conditions': list(TEMP), 'shots': 6, 'assays': 36},
            'flow_ramp': {'conditions': list(FLOW), 'shots': 6, 'assays': 36},
            'training_coordinates_sha256': canonical_hash(training_coords),
            'prediction_coordinates_sha256': canonical_hash(held_coords),
            'coordinate_chemistry_access': False, 'target_exposure': 'TARGET_EXPOSED',
            'source_scope': 'SOURCE_INTERNAL', 'excluded_other_grind_shots': 30,
            'TDS_spill_exclusions': 0, 'experiment_46_used': False,
            'collection_prefix_authority': 'Each exact source run.mE_cum; complete mE and workbook measured net mass checked',
            'missing_mass_prefixes': 0}


def train_and_predict(out):
    out = Path(out)
    out.mkdir(parents=True, exist_ok=False)
    paths = source_paths()
    train_coords = coordinates('FIT_2021_12', paths)
    held_coords = coordinates('PREDICTION_2022_03', paths)
    training = attach_chemistry(train_coords, allow_campaign='FIT_2021_12')
    write_json(out/'source.json', source_manifest(paths, train_coords, held_coords))
    write_json(out/'training.json', training)
    fits, diagnostics, final_models = {}, {}, {}
    # Fit all compact diagnostics and final candidates before later target access.
    for fold, train, held in list(loco(training))+[('FINAL', training, [])]:
        for name in MODELS[:-1]:
            model, trace = fit_compact(train, name)
            fits[fold+'/'+name] = trace
            write_json(out/(fold+'_'+name+'_attempts.json'), trace)
            if model is None:
                raise RuntimeError('compact candidate unavailable; retain failed attempts')
            if fold == 'FINAL':
                model.save(out/(name+'.json'))
                final_models[name] = model
            else:
                predictions = predict(model, project(held))
                diagnostics[fold+'/'+name] = {'model': model.to_dict(),
                    'shots': shot_metrics(held, predictions), 'predictions': predictions}
        write_json(out/(fold+'_compact_attempts.json'), {k:v for k,v in fits.items() if k.startswith(fold+'/')})
    selections = []
    for count in (5, 9):
        for penalty in (0., .001, .1, 10.):
            cases = []
            for fold, train, held in loco(training):
                model, trace = fit_empirical(train, count, penalty)
                predictions = predict(model, project(held))
                shots = shot_metrics(held, predictions)
                cases.append({'held_condition': fold, 'training_identity': model.fit_identity,
                              'knots_kg': list(model.knots_kg), 'fit': trace, 'shots': shots,
                              'score': development_score(shots)})
            selections.append({'knots': count, 'lambda': penalty,
                               'mean_LOCO_R_pp': float(np.mean([r['score'] for r in cases])), 'folds': cases})
    best = min(r['mean_LOCO_R_pp'] for r in selections)
    selected = min((r for r in selections if r['mean_LOCO_R_pp'] <= best+1e-10),
                   key=lambda r: (r['knots'], -r['lambda']))
    model, trace = fit_empirical(training, selected['knots'], selected['lambda'])
    model.save(out/'BOUNDARY_AWARE_EMPIRICAL.json')
    final_models['BOUNDARY_AWARE_EMPIRICAL'] = model
    write_json(out/'empirical_selection.json', {'candidates': selections, 'selected': trace,
                'selection_is_not_unbiased_test': True, 'domain_policy': 'fold-training only; supported diagnostic with complete accounting'})
    write_json(out/'development.json', diagnostics)
    predictions = {name: predict(model, project(held_coords)) for name, model in final_models.items()}
    write_json(out/'predictions.json', predictions)
    write_json(out/'execution.json', {'expected_nonlinear_starts': 192,
        'actual_nonlinear_starts': sum(len(r['attempts']) for r in fits.values()),
        'actual_residual_evaluations': sum(a['actual_residual_evaluations'] for r in fits.values() for a in r['attempts']),
        'failed_starts': sum(not a['success'] for r in fits.values() for a in r['attempts']),
        'max_calls_per_start': max(a['actual_residual_evaluations'] for r in fits.values() for a in r['attempts']),
        'nonlinear_start_cap': 500, 'actual_call_cap_per_start': 2000,
        'native_runs': 0, 'later_campaign_chemistry_read': False,
        'numpy': np.__version__, 'scipy': __import__('scipy').__version__})
    print(json.dumps(json.loads((out/'execution.json').read_text()), indent=2))


def freeze(out):
    out = Path(out)
    paths = ['puckworks/analysis/mass_delivery.py', 'puckworks/analysis/pannusch_mass_delivery.py',
             'tests/test_mass_delivery.py', 'docs/analysis/sci_md_mass_delivery_001/PROTOCOL.md',
             'tools/pannusch2024_reconstruct.py', 'tools/data_availability_preflight.py']
    payload = {'task': TASK, 'producer_commit': subprocess.check_output(['git','rev-parse','HEAD'], cwd=ROOT, text=True).strip(),
               'producer_tree': subprocess.check_output(['git','rev-parse','HEAD^{tree}'], cwd=ROOT, text=True).strip(),
               'code_and_protocol': {p: digest(ROOT/p) for p in paths},
               'artifacts': {p.name: digest(p) for p in sorted(out.glob('*.json'))},
               'review_status': 'INDEPENDENT_PRE_SCORE_AUDIT_REQUIRED',
               'scoring_policy': 'one final score; no post-score model repair or retuning',
               'working_budgets_pp': {'R': 1., 'abs_B': .5, 'competitive_margin': .1, 'material_absolute': .1},
               'material_relative': .2, 'bootstrap_replicates': 2000, 'bootstrap_seed': 20260926}
    write_json(out/'freeze.json', payload)
    print('Freeze SHA256:', digest(out/'freeze.json'))


def comparison(conditions, a='MASS', b='BOUNDARY_AWARE_EMPIRICAL'):
    ca = [r for r in conditions[a] if r['condition'] in PRIMARY]
    cb = [r for r in conditions[b] if r['condition'] in PRIMARY]
    aa, bb = aggregate(ca, PRIMARY), aggregate(cb, PRIMARY)
    if aa['metrics'] is None or bb['metrics'] is None:
        return {'status': 'NOT_ADJUDICATED_SUPPORT_OR_NUMERICS', 'competitive': False, 'competitive_status': 'NOT_ADJUDICATED_SUPPORT_OR_NUMERICS',
                'material_gain': 'NOT_ADJUDICATED_SUPPORT_OR_NUMERICS'}
    am, bm = aa['metrics'], bb['metrics']
    delta, error = bm['R_pp']-am['R_pp'], bm['R_allowance_pp']+am['R_allowance_pp']
    bias, bias_err = am['abs_B_pp']-bm['abs_B_pp'], am['B_allowance_pp']+bm['B_allowance_pp']
    comp = [threshold(-delta, error, .1), threshold(bias, bias_err, .1)]
    wins_lo = sum(y['metrics']['R_pp']-x['metrics']['R_pp'] > y['metrics']['R_allowance_pp']+x['metrics']['R_allowance_pp'] for x,y in zip(ca,cb))
    wins_hi = sum(y['metrics']['R_pp']-x['metrics']['R_pp'] > -y['metrics']['R_allowance_pp']-x['metrics']['R_allowance_pp'] for x,y in zip(ca,cb))
    gain = [threshold(-delta, error, -.1),
            threshold(am['R_pp']-.8*bm['R_pp'], am['R_allowance_pp']+.8*bm['R_allowance_pp'], 0),
            threshold(bias, bias_err, .1), 'PASS' if wins_lo >= 3 else ('FAIL' if wins_hi < 3 else 'NUMERICALLY_UNRESOLVED')]
    def status(gates):
        return 'FAIL' if 'FAIL' in gates else ('PASS' if set(gates) == {'PASS'} else 'NUMERICALLY_UNRESOLVED')
    return {'status': 'QUALIFIED', 'R_reduction_pp': delta, 'relative_R_reduction': delta/bm['R_pp'],
            'R_delta_allowance_pp': error, 'abs_B_deterioration_pp': bias,
            'abs_B_delta_allowance_pp': bias_err, 'conditions_improved_definite': wins_lo,
            'conditions_improved_possible': wins_hi, 'competitive_gates': comp,
            'competitive': aa['adequate'] and status(comp) == 'PASS',
            'competitive_status': status(comp+[aa['adequacy_status']]),
            'material_gain_gates': gain, 'material_gain': status(gain), 'MASS_adequate': aa['adequate']}


def bootstrap(shots, conditions=PRIMARY):
    if any(r['metrics'] is None for name in MODELS for r in shots[name] if r['condition'] in conditions):
        return {'status': 'NOT_ADJUDICATED_SUPPORT', 'replicates': 0, 'planned_replicates': 2000}
    index = {name: {r['shot']: r for r in rr} for name, rr in shots.items()}
    ids = {c: sorted(r['shot'] for r in shots['MASS'] if r['condition'] == c) for c in conditions}
    rng = np.random.Generator(np.random.PCG64(20260926))
    draws = {name: [] for name in MODELS}
    for _ in range(2000):
        selected = [list(rng.choice(ids[c], len(ids[c]), replace=True))
                    for c in rng.choice(conditions, len(conditions), replace=True)]
        for name in MODELS:
            draws[name].append([float(np.mean([np.mean([index[name][s]['metrics'][k] for s in group]) for group in selected]))
                                for k in ('R_pp', 'abs_B_pp')])
    out = {'status': 'DESCRIPTIVE_ONLY_FOUR_PRIMARY_CONDITIONS', 'replicates': 2000,
           'method': 'paired conditions then shots; intact fraction vectors; PCG64 20260926', 'models': {}, 'paired_MASS_minus': {}}
    for name in MODELS:
        values = np.array(draws[name])
        out['models'][name] = np.percentile(values, [2.5, 97.5], axis=0).T.tolist()
        if name != 'MASS':
            out['paired_MASS_minus'][name] = np.percentile(np.array(draws['MASS'])-values, [2.5, 97.5], axis=0).T.tolist()
    return out


def verify_registers(source, data_root=DATA):
    for path, expected in source['registers'].items():
        if digest(Path(data_root)/path) != expected:
            raise ValueError('frozen source register drift: '+path)


def score(out, review):
    out = Path(out)
    approved = json.loads(Path(review).read_text())
    if approved.get('status') != 'APPROVED' or approved.get('freeze_sha256') != digest(out/'freeze.json') or approved.get('independent') is not True:
        raise ValueError('independent exact-freeze pre-score approval missing')
    frozen = json.loads((out/'freeze.json').read_text())
    for path, sha in frozen['code_and_protocol'].items():
        if digest(ROOT/path) != sha:
            raise ValueError('frozen code/protocol changed')
    for path, sha in frozen['artifacts'].items():
        if digest(out/path) != sha:
            raise ValueError('frozen artifact changed')
    verify_registers(json.loads((out/'source.json').read_text()))
    if (out/'score_receipt.json').exists():
        raise FileExistsError('score already invoked; preserve original evidence')
    write_json(out/'score_receipt.json', {'status': 'STARTED', 'freeze_sha256': digest(out/'freeze.json'),
        'review_sha256': digest(review), 'prediction_sha256': digest(out/'predictions.json')})
    paths = source_paths()
    coords = coordinates('PREDICTION_2022_03', paths)
    if canonical_hash(coords) != json.loads((out/'source.json').read_text())['prediction_coordinates_sha256']:
        raise ValueError('frozen prediction coordinate drift')
    observed = attach_chemistry(coords, allow_campaign='PREDICTION_2022_03')
    predictions = json.loads((out/'predictions.json').read_text())
    if set(predictions) != set(MODELS):
        raise ValueError('candidate matrix mismatch')
    shots = {name: shot_metrics(observed, predictions[name]) for name in MODELS}
    conditions = {name: condition_metrics(rr) for name, rr in shots.items()}
    aggregate_results = {group: {name: aggregate(cc, expected) for name, cc in conditions.items()}
                         for group, expected in [('primary', PRIMARY), ('temperature_ramp', TEMP), ('flow_ramp', FLOW)]}
    comparisons = {name: comparison(conditions, b=name) for name in MODELS if name != 'MASS'}
    write_json(out/'scores.json', {'shots': shots, 'conditions': conditions, 'groups': aggregate_results,
                                 'comparisons': comparisons, 'bootstrap': bootstrap(shots),
                                 'claims': LIMITATIONS+('SOURCE_INTERNAL', 'TARGET_EXPOSED'),
                                 'score_passes': 1, 'rights': RIGHTS})
    write_json(out/'score_completion.json', {'status': 'COMPLETE', 'scores_sha256': digest(out/'scores.json'),
                                          'score_receipt_sha256': digest(out/'score_receipt.json')})
    print(json.dumps({'groups': aggregate_results, 'comparisons': comparisons}, indent=2))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=('prepare', 'freeze', 'score'))
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--review', type=Path)
    args = parser.parse_args()
    if args.command == 'prepare':
        train_and_predict(args.output)
    elif args.command == 'freeze':
        freeze(args.output)
    elif args.command == 'score':
        if not args.review:
            parser.error('--review required for scoring')
        score(args.output, args.review)


if __name__ == '__main__':
    main()
