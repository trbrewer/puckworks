"""Bounded SCI-MD-MASS-DELIVERY-002 adapter, FIT-only selection and audited scoring.

Permissioned raw data, optimizer traces and row-level outputs stay outside Git.
No registered mechanistic solver is run. Historical 001 software is reused read-only.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess

import numpy as np
from scipy.optimize import least_squares, lsq_linear

from . import mass_delivery as kernel
from . import pannusch_mass_delivery as old
from .conditioned_mass_delivery import (
    Model, CLAIMS, SEMANTICS, features, recipe_coefficients, integration_allowance,
)
from tools.pannusch2024_reconstruct import doe_conditions

ROOT = Path(__file__).resolve().parents[2]
DOC = ROOT/'docs/analysis/sci_md_mass_delivery_002'
HISTORICAL = ROOT/'docs/analysis/sci_md_mass_delivery_001'
TASK = 'SCI-MD-MASS-DELIVERY-002'
MODELS = ('M0', 'MT', 'MF', 'MTF', 'SETTING_AWARE_EMPIRICAL')
ACTIVE = {'MT': [0, 1, 2, 3, 5], 'MF': [0, 1, 2, 4, 6], 'MTF': list(range(7))}
SITE_CONDITIONS = ('FIT-C09', 'FIT-C14', 'FIT-C15', 'FIT-C10', 'FIT-C11')
EXPECTED = {'FIT-C09': (89., 2.), 'FIT-C10': (89., 1.), 'FIT-C11': (89., 3.),
            'FIT-C14': (80., 2.), 'FIT-C15': (98., 2.),
            'PRED-C01': (86., 2.), 'PRED-C02': (92., 2.),
            'PRED-C05': (90., 1.7), 'PRED-C06': (90., 2.3)}
COORD_KEYS = old.COORD_KEYS + ('temperature_K', 'source_flow_setting_code', 'setting_kind')
M0_SHA = '75aa34648f73883e975b16c2267594a247142e247713f14642641789f5e2182d'
write_json, digest, canonical_hash = old.write_json, old.digest, old.canonical_hash


def qualify_settings(paths):
    """Design-only source qualification. Does not read run.flow or chemistry."""
    designs, evidence = {}, {}
    register = old.rows(old.DATA/'experiment_register.csv')
    pred_register = {r['condition_id']: r for r in old.rows(old.DATA/'prediction_conditions.csv')}
    for label, count in (('FIT', 15), ('PRED', 8)):
        wb = old.workbook(paths['P24-DOE-'+label])
        sheet = wb['ExpSheet']
        headers = [str(sheet.cell(1, j).value).replace('\\n', ' ').replace('\n', ' ') for j in range(1, 13)]
        required = ('Flow_0', 'Flow_E', 'T_0', 'T_E') if label == 'PRED' else ('Flow (ml/s)', 'Temp (°C)')
        if not all(any(token in h for h in headers) for token in required):
            raise ValueError('SOURCE_CONTRACT_BLOCKED: nominal source-design header changed')
        design = doe_conditions(paths['P24-DOE-'+label], count, prediction=label == 'PRED')
        for d in design:
            cid = f"{label}-C{d['exp']:02d}"
            if label == 'FIT' and cid not in SITE_CONDITIONS:
                continue
            if d['dose'] != 20 or d['grind'] != 1.7:
                raise ValueError('SOURCE_CONTRACT_BLOCKED: grind/dose')
            constant = d['temp0'] == d['temp1'] and d['flow0'] == d['flow1']
            if cid in EXPECTED and (not constant or (d['temp0'], d['flow0']) != EXPECTED[cid]):
                raise ValueError('SOURCE_CONTRACT_BLOCKED: expected constant recipe')
            if label == 'PRED':
                r = pred_register[cid]
                if [float(r[k]) for k in ('temperature_start_C', 'temperature_end_C', 'flow_start_mL_s', 'flow_end_mL_s')] != [d['temp0'], d['temp1'], d['flow0'], d['flow1']]:
                    raise ValueError('SOURCE_CONTRACT_BLOCKED: programmed register disagreement')
            matches = [r for r in register if r['condition_id'] == cid]
            if {r['shot_id'] for r in matches} != {f"{label}-E{d['exp']:02d}-R{j}" for j in (1, 2, 3)}:
                raise ValueError('source physical-shot identity mismatch')
            if any(r['machine'] != 'DE1' or float(r['dose_g']) != 20 or float(r['grind_setting']) != 1.7 for r in matches):
                raise ValueError('source design context mismatch')
            if label == 'FIT' and any(float(r['nominal_temperature_program_id'][6:-1]) != d['temp0'] or float(r['nominal_flow_program_id'][6:-4]) != d['flow0'] for r in matches):
                raise ValueError('FIT program register mismatch')
            # Both designs use nominal 60/code collection duration, distinct from
            # run-level scale-derived flow. This is supporting design evidence only.
            row = 3*(d['exp']-1)+2
            duration = float(sheet.cell(row, 8).value)
            if constant and abs(duration*d['flow0']-60) > 1e-9:
                raise ValueError('SOURCE_CONTRACT_BLOCKED: collection-design convention')
            designs[cid] = dict(d, temperature_K=d['temp0']+273.15,
                               source_flow_setting_code=d['flow0'],
                               setting_kind='CONSTANT' if constant else 'VARIABLE')
        evidence[label] = {'source_id': 'P24-DOE-'+label, 'headers': headers,
                           'sha256': digest(paths['P24-DOE-'+label])}
    return designs, {'status': 'QUALIFIED_NOMINAL_SOURCE_DESIGN_CODE_ONLY',
        'semantics': SEMANTICS, 'design_evidence': evidence,
        'basis': 'Same DE1 source experiment design; labelled programmed flow axis and temperature axis; March start/end extension; common 60/code nominal collection convention; qualified program/register joins. Not number matching alone.',
        'physical_flow_conversion': 'UNRESOLVED_NOT_REQUIRED_NOT_PERFORMED',
        'run_flow_or_density_used': False, 'chemistry_used': False}


def coordinates(campaign, paths, designs):
    records = old.coordinates(campaign, paths)
    register = {r['shot_id']: r for r in old.rows(old.DATA/'experiment_register.csv')}
    for r in records:
        d, meta = designs[r['condition']], register[r['shot']]
        for key in ('temperature_K', 'source_flow_setting_code', 'setting_kind'):
            r[key] = d[key]
        for key in ('collection_date', 'coffee_product', 'coffee_lot_id', 'roast_batch_id'):
            r[key] = meta[key]
        r['source_design_date'] = d['date']
    expected_conditions = SITE_CONDITIONS if campaign == 'FIT_2021_12' else tuple(f'PRED-C{i:02d}' for i in range(1, 9))
    expected = {(c.replace('-C', '-E')+f'-R{j}', f) for c in expected_conditions for j in (1, 2, 3) for f in old.FIDS}
    if len(records) != len(expected) or {(r['shot'], r['fraction']) for r in records} != expected:
        raise ValueError('source assay identity matrix mismatch')
    return records


def project(records):
    return [{k: r[k] for k in COORD_KEYS} for r in records]


def ordered_fit(records):
    """Explicit FIT boundary, deterministic ordering and intact source sites."""
    if not records or any(r['campaign'] != 'FIT_2021_12' for r in records):
        raise ValueError('FIT stage rejects March chemistry')
    records = sorted(records, key=lambda r: (r['condition'], r['shot'], r['fraction']))
    if {r['condition'] for r in records} != set(SITE_CONDITIONS):
        raise ValueError('all five FIT settings required')
    ids = [(r['shot'], r['fraction']) for r in records]
    if len(ids) != len(set(ids)):
        raise ValueError('duplicate fit identity')
    for r in records:
        t, f = EXPECTED[r['condition']]
        if (r['temperature_K'], r['source_flow_setting_code'], r['setting_kind']) != (t+273.15, f, 'CONSTANT'):
            raise ValueError('FIT recipe mismatch')
    return records


def folds(records):
    records = ordered_fit(records)
    for replicate in (1, 2, 3):
        held = [r for r in records if r['shot'].endswith(f'-R{replicate}')]
        train = [r for r in records if not r['shot'].endswith(f'-R{replicate}')]
        if len({r['shot'] for r in held}) != 5 or len({r['shot'] for r in train}) != 10:
            raise ValueError('replicate fold physical-shot denominator mismatch')
        yield f'R{replicate}', train, held


def identity(records):
    return dict(old.identity(records), task=TASK, dose_g=20,
                design_semantics=SEMANTICS, comparison='RETROSPECTIVE_MODEL_DEVELOPMENT_COMPARISON',
                source_doi='10.17632/y2tz67f6ry.1',
                source_inputs_sha256=digest(old.DATA/'source_inputs.csv'))


def make_model(name, coefficients, training, **kwargs):
    return Model(TASK+'/'+name+'/v1', name, tuple(coefficients),
                 (0., max(r['b1'] for r in training)), identity(training), old.RIGHTS,
                 claims=CLAIMS+('SOURCE_INTERNAL', 'TARGET_EXPOSED', 'RETROSPECTIVE_MODEL_DEVELOPMENT_COMPARISON'), **kwargs)


class Budget:
    """Task-local append-only count; same ledger reused after a corrected attempt."""
    def __init__(self, path=None):
        self.path = Path(path) if path else None
        self.count = 0
        if self.path and self.path.exists():
            self.count = sum(json.loads(line)['event'] == 'START' for line in self.path.read_text().splitlines())

    def record(self, event):
        if self.path:
            with self.path.open('a') as stream:
                stream.write(json.dumps(event, sort_keys=True, allow_nan=False)+'\n')
                stream.flush()

    def start(self, name, start):
        if self.count >= 500:
            raise RuntimeError('total nonlinear start cap')
        self.count += 1
        self.record({'event': 'START', 'ordinal': self.count, 'fit': name, 'start': start})
        return self.count


def matrix_diagnostics(a):
    singular = np.linalg.svd(a, compute_uv=False)
    rank = int(np.linalg.matrix_rank(a))
    return {'rank': rank, 'columns': a.shape[1], 'singular_values': singular.tolist(),
            'condition_number': float(singular[0]/singular[-1]) if rank == a.shape[1] else None}


def fit_compact(training, family, starts, budget, fit_name):
    training = ordered_fit(training)
    if family not in ACTIVE or np.asarray(starts).shape != (16, 7):
        raise ValueError('frozen compact family and 16 starts required')
    good, weights = old.training_weights(training)
    b0, b1 = (np.array([r[k] for r in good]) for k in ('b0', 'b1'))
    y = np.array([r['q'] for r in good])
    t, f = features([r['temperature_K'] for r in good], [r['source_flow_setting_code'] for r in good])
    groups = [(t0, f0, (t == t0) & (f == f0)) for t0, f0 in sorted(set(zip(t, f)))]
    active = ACTIVE[family]
    lower = np.array([0, 0, .25, -3, -3, -3, -3])[active]
    upper = np.array([1, 10000, 4, 3, 3, 3, 3])[active]
    attempts, solutions = [], []
    for idx, base in enumerate(starts):
        start = np.array(base)[active]
        ordinal = budget.start(fit_name, start.tolist())
        calls, last = 0, {}

        def residual(x):
            nonlocal calls
            if calls >= 2000:
                raise RuntimeError('actual residual evaluation cap')
            calls += 1
            theta = np.zeros(7)
            theta[active] = x
            pred = np.zeros(len(good))
            for ti, fi, use in groups:
                pred[use] = kernel.compact_delivery(b0[use], b1[use], recipe_coefficients(theta, ti, fi))/(b1[use]-b0[use])
            r = 100*(pred-y)*weights
            last.update(parameters=theta.tolist(), loss=float(r@r))
            return r

        rec = {'start_index': idx, 'ordinal': ordinal, 'start': start.tolist(), 'active_parameters': active}
        try:
            initial = residual(start)
            rec['initial_loss'] = float(initial@initial)
            fit = least_squares(residual, start, bounds=(lower, upper), method='trf',
                jac='2-point', tr_solver='exact', loss='linear', ftol=1e-10, xtol=1e-10,
                gtol=1e-10, diff_step=1e-6, x_scale=np.array([.2, 50, 1, 1, 1, 1, 1])[active], max_nfev=2000)
            theta = np.zeros(7)
            theta[active] = fit.x
            rec.update(success=bool(fit.success), status=int(fit.status), message=fit.message,
                parameters=theta.tolist(), loss=float(2*fit.cost), optimizer_nfev=int(fit.nfev),
                optimizer_njev=int(fit.njev), boundary_hits=fit.active_mask.tolist(),
                local_jacobian=matrix_diagnostics(fit.jac))
            if fit.success:
                solutions.append((float(2*fit.cost), idx, theta.tolist()))
        except (RuntimeError, ValueError, FloatingPointError) as error:
            rec.update(success=False, message=str(error), last=last)
        rec['actual_residual_evaluations'] = calls
        budget.record(dict(rec, event='END', fit=fit_name))
        attempts.append(rec)
    if not solutions:
        return None, {'status': 'ALL_STARTS_FAILED', 'attempts': attempts}
    loss, idx, theta = min(solutions)
    return make_model(family, theta, training), {'status': 'CONVERGED', 'loss': loss,
        'selected_start': idx, 'attempts': attempts, 'parameter_identification': 'NOT_ESTABLISHED_BY_PREDICTIVE_FIT'}


def fit_empirical(training, count, penalty):
    training = ordered_fit(training)
    if count not in (5, 9) or penalty not in (0., .001, .1, 10.):
        raise ValueError('undeclared empirical hyperparameter')
    good, weights = old.training_weights(training)
    knots = np.linspace(0, max(r['b1'] for r in training), count)
    d2 = np.diff(np.eye(count), n=2, axis=0)*(count-1)**2
    profiles, diagnostics = [], []
    solves = 0
    for condition in SITE_CONDITIONS:
        use = [i for i, r in enumerate(good) if r['condition'] == condition]
        records = [good[i] for i in use]
        b0, b1 = (np.array([r[k] for r in records]) for k in ('b0', 'b1'))
        design = kernel.linear_basis_integral(b0, b1, knots)/(b1-b0)[:, None]
        observation = 100*np.sqrt(5)*weights[use, None]*design
        a = np.vstack((observation, 100*np.sqrt(penalty/(count-2))*d2))
        info = {'condition': condition, 'data_design': matrix_diagnostics(observation),
                'augmented_design': matrix_diagnostics(a)}
        if penalty == 0 and info['data_design']['rank'] < count:
            info['status'] = 'EXCLUDED_RANK_DEFICIENT_UNPENALIZED'
            diagnostics.append(info)
            profiles.append(None)
            continue
        target = np.r_[100*np.sqrt(5)*weights[use]*[r['q'] for r in records], np.zeros(count-2)]
        solves += 1
        fit = lsq_linear(a, target, bounds=(0., 1.), tol=1e-12, max_iter=1000, method='trf')
        info.update(status='CONVERGED' if fit.success else 'FAILED', message=fit.message,
                    iterations=fit.nit, objective=float(2*fit.cost), boundary_hits=fit.active_mask.tolist())
        diagnostics.append(info)
        profiles.append(tuple(fit.x) if fit.success else None)
    trace = {'knots': count, 'lambda': penalty, 'sites': diagnostics, 'bounded_linear_solves': solves}
    if any(p is None for p in profiles):
        trace['status'] = 'EXCLUDED_OR_FAILED'
        return None, trace
    trace.update(status='CONVERGED', objective=float(np.mean([r['objective'] for r in diagnostics])))
    return make_model('SETTING_AWARE_EMPIRICAL', profiles, training, knots_kg=tuple(knots)), trace


def predict(model, coords, verify=True):
    if any(set(r) != set(COORD_KEYS) for r in coords):
        raise ValueError('prediction requires coordinate/recipe-only records')
    out = []
    for r in coords:
        recipe = {k: r[k] for k in ('temperature_K', 'source_flow_setting_code')}
        d = model.predict(r['b0'], r['b1'], **recipe, setting_kind=r['setting_kind'], strict=False)
        supported = bool(d.in_domain)
        allowance = integration_allowance(model, r['b0'], r['b1'], **recipe) if supported and verify else 0.
        out.append(dict(r, in_domain=supported, unsupported_reason=str(d.unsupported_reason),
            predicted_solute_kg=float(d.solute_kg) if supported else None,
            integration_allowance_kg=allowance, numerical_qualified=supported and allowance <= 1e-9))
    return out


def m0_model():
    path = HISTORICAL/'models/MASS.json'
    if digest(path) != M0_SHA:
        raise ValueError('historical M0 artifact changed')
    m = kernel.Model.load(path)
    return Model(TASK+'/M0/v1', 'M0', m.coefficients+(0., 0., 0., 0.), m.domain_kg,
        {'original_model_id': m.model_id, 'original_artifact_sha256': M0_SHA,
         'original_fit_identity': m.fit_identity}, m.rights,
        claims=CLAIMS+('SOURCE_INTERNAL', 'TARGET_EXPOSED', 'RETROSPECTIVE_MODEL_DEVELOPMENT_COMPARISON'))


def prepare(out, budget_path):
    out = Path(out)
    out.mkdir(parents=True, exist_ok=False)
    paths = old.source_paths()
    designs, qualification = qualify_settings(paths)
    train_coords = coordinates('FIT_2021_12', paths, designs)
    target_coords = coordinates('PREDICTION_2022_03', paths, designs)
    training = ordered_fit(old.attach_chemistry(train_coords, allow_campaign='FIT_2021_12'))
    if not all(r['eligible'] for r in training):
        raise ValueError('expected 90 eligible TDS assays not verified')
    source = old.source_manifest(paths, train_coords, target_coords)
    source.update(task=TASK, setting_qualification=qualification,
        source_designs=designs, primary_coordinates_sha256=canonical_hash(project([r for r in target_coords if r['condition'] in old.PRIMARY])),
        condition_mass_extents_kg={c: [0., max(r['b1'] for r in training if r['condition'] == c)] for c in SITE_CONDITIONS},
        recipe_mass_product_domain='MODELING_ASSUMPTION_NOT_COMPLETE_JOINT_COVERAGE',
        final_mass_domain_kg=list(m0_model().domain_kg),
        metadata=[{k: r[k] for k in ('shot', 'collection_date', 'source_design_date', 'coffee_product', 'coffee_lot_id', 'roast_batch_id')} for r in train_coords+target_coords if r['fraction'] == 1])
    endpoint = max(r['b1'] for r in training)
    if abs(endpoint-.0635064) > 1e-15 or endpoint != m0_model().domain_kg[1]:
        raise ValueError('predecessor FIT domain mismatch')
    source['shape_borrowing_intervals_kg'] = {c: [v[1], endpoint] for c, v in source['condition_mass_extents_kg'].items() if v[1] < endpoint}
    write_json(out/'source.json', source)
    write_json(out/'training.json', training)
    write_json(out/'coordinates.json', project(target_coords))
    starts = json.loads((DOC/'STARTS.json').read_text())['starts']
    write_json(out/'starts.json', starts)
    budget = Budget(budget_path)
    initial_starts = budget.count
    fits, diagnostics, final_models = {}, {}, {'M0': m0_model()}
    split = list(folds(training))
    for fold, train, held in split+[('FINAL', training, [])]:
        for name in ACTIVE:
            model, trace = fit_compact(train, name, starts, budget, fold+'/'+name)
            fits[fold+'/'+name] = trace
            write_json(out/(fold+'_'+name+'_attempts.json'), trace)
            if model is None:
                raise RuntimeError('compact candidate failed; evidence and budget retained')
            if fold == 'FINAL':
                final_models[name] = model
            else:
                prediction = predict(model, project(held))
                diagnostics[fold+'/'+name] = {'model': model.to_dict(),
                    'shots': old.shot_metrics(held, prediction), 'predictions': prediction}
    selections, common_support = [], {}
    for count in (5, 9):
        for penalty in (0., .001, .1, 10.):
            cases = []
            for fold, train, held in split:
                model, trace = fit_empirical(train, count, penalty)
                case = {'fold': fold, 'fit': trace, 'training_sha256': canonical_hash(train)}
                if model is not None:
                    prediction = predict(model, project(held))
                    support = [(r['shot'], r['fraction']) for r in prediction if r['in_domain']]
                    if fold in common_support and common_support[fold] != support:
                        raise ValueError('empirical candidates differ in CV support')
                    common_support[fold] = support
                    shots = old.shot_metrics(held, prediction)
                    case.update(score=old.development_score(shots), shots=shots,
                        supported_assays=len(support), original_assays=len(held),
                        original_shots=5, original_conditions=5, knots_kg=list(model.knots_kg))
                cases.append(case)
            valid = all('score' in c for c in cases)
            selections.append({'knots': count, 'lambda': penalty, 'folds': cases,
                'status': 'ADMISSIBLE' if valid else 'EXCLUDED_OR_FAILED',
                'balanced_CV_R_pp': float(np.mean([c['score'] for c in cases])) if valid else None})
    eligible = [r for r in selections if r['status'] == 'ADMISSIBLE']
    if not eligible:
        write_json(out/'empirical_selection.json', {'candidates': selections, 'status': 'NO_ADMISSIBLE_CANDIDATE'})
        raise RuntimeError('no empirical candidate; full comparison blocked')
    best = min(r['balanced_CV_R_pp'] for r in eligible)
    selected = min((r for r in eligible if r['balanced_CV_R_pp'] <= best+1e-10), key=lambda r: (r['knots'], -r['lambda']))
    empirical, trace = fit_empirical(training, selected['knots'], selected['lambda'])
    if empirical is None:
        raise RuntimeError('all-FIT empirical unavailable')
    final_models['SETTING_AWARE_EMPIRICAL'] = empirical
    write_json(out/'empirical_selection.json', {'candidates': selections, 'selected': trace,
        'common_support': common_support, 'original_denominators': {'folds': 3, 'shots': 15, 'conditions_per_fold': 5, 'assays': 90},
        'claim': 'WITHIN_SETTING_REPLICATE_CV_PARTIAL_SUPPORT_DIAGNOSTIC_NOT_ADEQUACY'})
    write_json(out/'development.json', diagnostics)
    for name, model in final_models.items():
        model.save(out/(name+'.json'))
    predictions = {name: predict(final_models[name], project(target_coords)) for name in MODELS}
    write_json(out/'predictions.json', predictions)
    attempts = [a for fit in fits.values() for a in fit['attempts']]
    write_json(out/'execution.json', {'planned_nonlinear_starts': 192, 'new_nonlinear_starts': budget.count-initial_starts,
        'total_nonlinear_starts': budget.count, 'nonlinear_start_cap': 500,
        'actual_residual_evaluations': sum(a['actual_residual_evaluations'] for a in attempts),
        'max_calls_per_start': max(a['actual_residual_evaluations'] for a in attempts), 'call_cap_per_start': 2000,
        'failed_starts': sum(not a['success'] for a in attempts),
        'bounded_linear_solves': sum(f['fit']['bounded_linear_solves'] for r in selections for f in r['folds'])+trace['bounded_linear_solves'],
        'budget_ledger_sha256': digest(budget_path), 'later_campaign_chemistry_read': False,
        'native_ewp_runs': 0, 'numpy': np.__version__, 'scipy': __import__('scipy').__version__})
    print(json.dumps(json.loads((out/'execution.json').read_text()), indent=2))


FREEZE_PATHS = (
    'puckworks/analysis/conditioned_mass_delivery.py', 'puckworks/analysis/pannusch_conditioned_mass_delivery.py',
    'puckworks/analysis/mass_delivery.py', 'puckworks/analysis/pannusch_mass_delivery.py',
    'tools/pannusch2024_reconstruct.py', 'tools/data_availability_preflight.py',
    'tests/test_conditioned_mass_delivery.py',
    'docs/analysis/sci_md_mass_delivery_002/PROTOCOL.md',
    'docs/analysis/sci_md_mass_delivery_002/MODEL_CARD.md',
    'docs/analysis/sci_md_mass_delivery_002/STARTS.json',
    'docs/analysis/sci_md_mass_delivery_001/models/MASS.json',
    'docs/analysis/sci_md_mass_delivery_001/RESULTS.json',
)


def freeze(out):
    out = Path(out)
    if subprocess.check_output(['git', 'status', '--porcelain'], cwd=ROOT, text=True).strip():
        raise ValueError('commit implementation before freeze')
    write_json(out/'freeze.json', {'task': TASK,
        'producer_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
        'producer_tree': subprocess.check_output(['git', 'rev-parse', 'HEAD^{tree}'], cwd=ROOT, text=True).strip(),
        'code_and_protocol': {p: digest(ROOT/p) for p in FREEZE_PATHS},
        'artifacts': {p.name: digest(p) for p in sorted(out.glob('*.json'))},
        'review_status': 'INDEPENDENT_PRE_SCORE_AUDIT_REQUIRED',
        'primary_candidates': list(MODELS), 'primary_conditions': list(old.PRIMARY),
        'scoring_policy': 'ONE_PASS_NO_POST_SCORE_TUNING', 'physical_validation': 'NOT_ESTABLISHED'})
    print('Freeze SHA256:', digest(out/'freeze.json'))


def verify_before_score(out, review):
    out = Path(out)
    approved = json.loads(Path(review).read_text())
    frozen = json.loads((out/'freeze.json').read_text())
    if (approved.get('status') != 'APPROVED' or approved.get('independent') is not True
            or approved.get('freeze_sha256') != digest(out/'freeze.json')
            or approved.get('reviewed_head') != frozen['producer_commit']
            or approved.get('reviewed_tree') != frozen['producer_tree']):
        raise ValueError('independent exact-freeze pre-score approval required')
    for path, sha in frozen['code_and_protocol'].items():
        if digest(ROOT/path) != sha:
            raise ValueError('frozen implementation/protocol drift')
    for path, sha in frozen['artifacts'].items():
        if digest(out/path) != sha:
            raise ValueError('frozen artifact drift')
    old.verify_registers(json.loads((out/'source.json').read_text()))
    return frozen


def decision_axes(conditions):
    aggregates = {name: old.aggregate(conditions[name], old.PRIMARY) for name in MODELS}
    m0 = old.comparison(conditions, a='MTF', b='M0')
    empirical = old.comparison(conditions, a='MTF', b='SETTING_AWARE_EMPIRICAL')
    # Rename inherited reporting label without changing its numerical comparison.
    for c in (m0, empirical):
        if 'MASS_adequate' in c:
            c['MTF_adequate'] = c.pop('MASS_adequate')
    axes = {'A_absolute_adequacy': aggregates['MTF']['adequacy_status'],
            'B_material_gain_over_M0': m0['material_gain'],
            'C_empirical_competitiveness': empirical['competitive_status'],
            'D_material_superiority_over_empirical': empirical['material_gain']}
    if all(axes[k] == 'PASS' for k in list(axes)[:3]):
        disposition = 'CONDITIONING_EARNED'
    elif any(v not in ('PASS', 'FAIL') for v in axes.values()):
        disposition = 'SOURCE_SUPPORT_OR_NUMERICAL_COMPARISON_UNRESOLVED'
    elif axes['A_absolute_adequacy'] != 'PASS':
        disposition = 'TESTED_CONDITIONING_FAMILY_INADEQUATE'
    elif axes['C_empirical_competitiveness'] != 'PASS':
        disposition = 'EMPIRICAL_MODEL_PREFERABLE'
    else:
        disposition = 'ADEQUATE_BUT_MATERIAL_GAIN_NOT_ESTABLISHED'
    return {'axes': axes, 'disposition': disposition, 'groups': {'primary': aggregates},
            'comparisons': {'M0': m0, 'SETTING_AWARE_EMPIRICAL': empirical},
            'empirical_adequate': aggregates['SETTING_AWARE_EMPIRICAL']['adequacy_status']}


def replay_m0(conditions):
    historical = json.loads((HISTORICAL/'RESULTS.json').read_text())
    target = {r['condition']: r for r in historical['conditions']['MASS'] if r['condition'] in old.PRIMARY}
    deltas = []
    for r in conditions['M0']:
        if r['metrics'] is None:
            raise ValueError('M0 replay lacks full qualified support')
        for k in ('R_pp', 'B_pp', 'abs_B_pp'):
            delta = abs(r['metrics'][k]-target[r['condition']]['metrics'][k])
            deltas.append(delta)
            if delta > 1e-9:
                raise ValueError('M0 replay mismatch blocks scientific verdict')
    current = old.aggregate(conditions['M0'], old.PRIMARY)['metrics']
    reference = historical['groups']['primary']['MASS']['metrics']
    for k in ('R_pp', 'B_pp', 'abs_B_pp'):
        delta = abs(current[k]-reference[k])
        deltas.append(delta)
        if delta > 1e-9:
            raise ValueError('M0 balanced replay mismatch')
    return {'status': 'PASS', 'max_metric_difference_pp': max(deltas), 'tolerance_pp': 1e-9,
            'original_artifact_sha256': M0_SHA}


def score(out, review):
    out = Path(out)
    verify_before_score(out, review)
    write_json(out/'score_receipt.json', {'status': 'STARTED', 'freeze_sha256': digest(out/'freeze.json'),
        'review_sha256': digest(review), 'predictions_sha256': digest(out/'predictions.json')})
    paths = old.source_paths()
    designs, _ = qualify_settings(paths)
    coords = coordinates('PREDICTION_2022_03', paths, designs)
    if canonical_hash(coords) != json.loads((out/'source.json').read_text())['prediction_coordinates_sha256']:
        raise ValueError('target coordinates drift')
    coords = [r for r in coords if r['condition'] in old.PRIMARY]
    observed = old.attach_chemistry(coords, allow_campaign='PREDICTION_2022_03')
    predictions = json.loads((out/'predictions.json').read_text())
    if set(predictions) != set(MODELS):
        raise ValueError('candidate matrix mismatch')
    shots = {name: old.shot_metrics(observed, [r for r in predictions[name] if r['condition'] in old.PRIMARY]) for name in MODELS}
    conditions = {name: old.condition_metrics(records) for name, records in shots.items()}
    write_json(out/'primary_metrics.json', {'shots': shots, 'conditions': conditions})
    replay = replay_m0(conditions)
    result = decision_axes(conditions)
    result.update(task=TASK, conditions=conditions, m0_replay=replay, score_passes=1,
        rights=old.RIGHTS, physical_validation='NOT_ESTABLISHED',
        ramps={c: 'NOT_ADJUDICATED_VARIABLE_SETTING_INPUT' for c in old.TEMP+old.FLOW})
    write_json(out/'scores.json', result)
    write_json(out/'score_completion.json', {'status': 'COMPLETE', 'scores_sha256': digest(out/'scores.json')})
    print(json.dumps({'axes': result['axes'], 'disposition': result['disposition']}, indent=2))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=('prepare', 'freeze', 'score'))
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--budget-ledger', type=Path, help='same private task ledger across all real attempts')
    parser.add_argument('--review', type=Path)
    args = parser.parse_args()
    if args.output.resolve().is_relative_to(ROOT):
        parser.error('row-level evidence must remain outside repository')
    if args.command == 'prepare':
        if not args.budget_ledger:
            parser.error('--budget-ledger required')
        prepare(args.output, args.budget_ledger)
    elif args.command == 'freeze':
        freeze(args.output)
    else:
        if not args.review:
            parser.error('--review required')
        score(args.output, args.review)


if __name__ == '__main__':
    main()
