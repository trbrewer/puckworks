#!/usr/bin/env python3
"""Prepare, qualify, then score one frozen research comparison; no training."""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
import os
from pathlib import Path
import sys

import numpy as np
from scipy.io import loadmat

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from puckworks.analysis import pannusch_equilibrium_limit as m

BUNDLE = ROOT/'docs/analysis/sci_h1_pannusch_equilibrium_limit_001'
DATA = ROOT/'puckworks/data/pannusch2024'
TASK = 'SCI-H1-PANNUSCH-EQUILIBRIUM-LIMIT-001'


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def read(p):
    return json.loads(Path(p).read_text())


def write(p, value):
    p = Path(p)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(value, sort_keys=True, indent=2, allow_nan=False)+'\n')


def rows(p):
    with Path(p).open(newline='') as f:
        return list(csv.DictReader(f))


def csvout(p, values):
    with Path(p).open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(values[0]), lineterminator='\n')
        w.writeheader()
        w.writerows(values)


def external_root():
    if os.environ.get('PUCKWORKS_EXTERNAL_DATA_ROOT'):
        return Path(os.environ['PUCKWORKS_EXTERNAL_DATA_ROOT'])
    cfg = Path.home()/'.config/puckworks/data_sources.json'
    return Path(read(cfg)['sources']['PANNUSCH2024_MENDELEY_FULL_REPOSITORY']['path'])


def profiles():
    """Only nonchemical target inputs; no outcome returned or scored."""
    source = rows(DATA/'prediction_fraction_replicates.csv')
    register = {r['shot_id']: r for r in rows(DATA/'experiment_register.csv')}
    result = []
    for condition in m.CONDITIONS:
        for replicate in (1, 2, 3):
            shot = condition.replace('C', 'E')+f'-R{replicate}'
            paired = []
            for analyte in m.SPECIES:
                g = sorted([r for r in source if r['shot_id'] == shot and r['analyte'] == analyte],
                           key=lambda r: int(r['fraction_id']))
                if tuple(int(r['fraction_id']) for r in g) != m.FRACTIONS:
                    raise ValueError('primary six-fraction membership mismatch')
                if any(r['validity'] != 'VALID' or r['condition_id'] != condition for r in g):
                    raise ValueError('invalid primary source record')
                for r in g:
                    if r['temperature_start_C'] != r['temperature_end_C'] or r['flow_start_mL_s'] != r['flow_end_mL_s']:
                        raise ValueError('nonconstant primary condition')
                windows = [[float(r['fraction_start_s']), float(r['fraction_end_s'])] for r in g]
                masses = [float(r['fraction_liquid_g_or_ml'])/1000 for r in g]
                paired.append((windows, masses))
                result.append(dict(condition=condition, shot=shot, analyte=analyte,
                                   source_fraction_ids=list(m.FRACTIONS), windows=windows,
                                   liquid_mass_kg=masses, temperature_C=float(g[0]['temperature_start_C']),
                                   flow_label=float(g[0]['flow_start_mL_s']), start_s=windows[0][0],
                                   grind=float(register[shot]['grind_setting'])))
            if paired[0] != paired[1]:
                raise ValueError('paired species windows/vial quantities differ')
    return result


def scenario(p):
    return m.Scenario(p['analyte'], p['temperature_C'], p['flow_label'], p['start_s'], p['grind'])


def prepare(args):
    root = external_root()
    admitted, paths = [], {}
    required = {'P24-MAT-PRED', 'P24-DOE-PRED', 'P24-HPLC-PRED', 'P24-M-PREP-PRED', 'P24-MASS-PRED'}
    for r in rows(DATA/'source_inputs.csv'):
        if r['source_id'] not in required:
            continue
        p = root/r['source_relpath']
        ok = p.is_file() and sha(p) == r['sha256']
        admitted.append(dict(source_id=r['source_id'], sha256=r['sha256'], status='VERIFIED' if ok else 'UNAVAILABLE_OR_MISMATCH',
                             role=r['scientific_role'], rights=r['rights_id']))
        if ok:
            paths[r['source_id']] = p
    if set(paths) != required:
        write(BUNDLE/'INPUT_MANIFEST.json', dict(task_id=TASK, sources=admitted, empirical='UNAVAILABLE'))
        raise ValueError('known external evidence unavailable or hash mismatch; see manifest')
    pp = profiles()
    exp = np.atleast_1d(loadmat(paths['P24-MAT-PRED'], squeeze_me=True, struct_as_record=False)['ExperimentalData'])
    maximum = 0.
    for p in pp:
        cid, rep = int(p['condition'][-2:]), int(p['shot'][-1])
        run = np.atleast_1d(exp[cid-1].run)[rep-1]
        t, v = np.asarray(run.tE).ravel(), np.asarray(run.mE).ravel()
        for fid, (a, b), mass in zip(m.FRACTIONS, p['windows'], p['liquid_mass_kg']):
            errors = [abs(a-(0 if fid == 1 else t[fid-2])), abs(b-t[fid-1]), abs(1000*mass-v[fid-1])]
            maximum = max(maximum, *errors)
    if maximum > 5.1e-9:
        raise ValueError('retained source-rounded windows or measured vial masses mismatch originals')
    pw = ['docs/cards/pannusch2024.md', 'docs/research/PANNUSCH_RAW_REPRO_001_REPORT.md',
          'docs/research/REVIEW_PW_EWP_2026-10-18_gpt6-astra-pro.md',
          'docs/data/ESPRESSO_DATA_GUIDE.md', 'docs/data/AVAILABLE_DATA_FIRST_POLICY.md',
          'puckworks/data/MANIFEST.csv', 'puckworks/data/AVAILABLE_DATA_REGISTER.json']
    pw += [str(x.relative_to(ROOT)) for x in [DATA/'source_inputs.csv', DATA/'prediction_fraction_replicates.csv',
           DATA/'experiment_register.csv', DATA/'prediction_conditions.csv', DATA/'fit_fraction_replicates.csv',
           DATA/'pannusch_raw_repro_001_result.json', DATA/'pannusch_transfer_eligibility.json',
           DATA/'table2_fitted_params.csv', DATA/'table2_grind_psi_ds2.csv']]
    ew = ['docs/analysis/xsv_pannusch_multimodel_001/'+x for x in
          ['OBSERVABLE_CONTRACT.json', 'SPLIT_CONTRACT.json', 'CALIBRATION_FREEZE.json',
           'C1_CALIBRATION_FREEZE_ADDENDUM.json', 'C1_REVIEW_MANDATED_METHODS_ADDENDUM.json',
           'MODEL_PRIVILEGE_REGISTRY.csv', 'RESULT.md', 'CONDITION_DIFFERENCES.csv']]
    ew += ['analysis/xsv_pannusch_multimodel_001/c1_correction.py']
    ew += ['docs/analysis/'+folder+'/'+name for folder, name in
           [('obs_pannusch_fraction_window_001', 'OBSERVER_RESULTS.csv'),
            ('obs_pannusch_fraction_window_001', 'SOURCE_LINEAGE.json'),
            ('obs_pannusch_fraction_window_001', 'RESULT.md'),
            ('sci_md_pannusch_flow_history_001', 'RESULT.md'),
            ('xsv_pannusch_ewp_input_mapping_001', 'RESULT.md')]]
    manifest = dict(task_id=TASK, source_status='KNOWN_EXTERNAL_EVIDENCE_AVAILABLE_AND_INSPECTED',
                    rights='CC-BY-NC-3.0; Pannusch et al.; DOI 10.17632/y2tz67f6ry.1',
                    exposure='SOURCE_INTERNAL; TARGET_EXPOSED; NOT_INDEPENDENT',
                    sources=admitted, retained_primary=dict(conditions=4, physical_shots=12, profiles=24,
                    scalar_observations=144, fraction_ids=list(m.FRACTIONS), original_join_max_rounding_error=maximum),
                    reused_puckworks={p: sha(ROOT/p) for p in pw},
                    reused_ewp={p: sha(args.ewp/p) for p in ew},
                    paired_reference=dict(status='AVAILABLE' if args.reference and args.reference.is_file() else 'UNAVAILABLE',
                    artifact='C1/predictions/paired_shot_analyte_errors.csv',
                    sha256=sha(args.reference) if args.reference and args.reference.is_file() else None,
                    role='Retained frozen calibration-only boundary-aware errors; no retraining'),
                    missing_components=['assay recovery/censoring covariance', 'window fit coefficient covariance',
                                        'physical source flow-label resolution', 'independent production inventory and initial state'],
                    inspection='Primary original MAT nonchemistry support inspected; five original hashes verified; source preprocessing/assay investigations reused, not repeated.')
    write(BUNDLE/'INPUT_MANIFEST.json', manifest)
    write(args.private/'inputs.json', pp)
    write(BUNDLE/'MODEL_CONSTANTS.json', [dict(condition=p['condition'], analyte=p['analyte'],
          temperature_C=p['temperature_C'], flow_label=p['flow_label'], start_s=p['start_s'],
          **scenario(p).constants()) for p in pp if p['shot'].endswith('R1')])
    print('Prepared 12 shots / 24 paired profiles / 144 observations; no target score.')


def frozen_files():
    return [ROOT/'puckworks/analysis/pannusch_equilibrium_limit.py', Path(__file__),
            ROOT/'tests/test_pannusch_equilibrium_limit.py', BUNDLE/'PROTOCOL.md', BUNDLE/'INPUT_MANIFEST.json',
            BUNDLE/'MODEL_CONSTANTS.json'] + [ROOT/'puckworks/models/pannusch2024'/p for p in
            ('solver.py', 'closures.py', 'temperature_history_fv.py')]


def freeze(args):
    prior = sha(BUNDLE/'FREEZE.json') if (BUNDLE/'FREEZE.json').exists() else None
    write(BUNDLE/'FREEZE.json', dict(task_id=TASK, new_target_scores_computed=False,
          private_inputs_sha256=sha(args.private/'inputs.json'),
          reused_numerical_freeze_sha256=prior,
          correction='Input identity checks and output assembly only; unchanged numerical module and inputs; two failed synthetic charges retained',
          files={str(p.relative_to(ROOT)): sha(p) for p in frozen_files()},
          primary_integrations=96, synthetic_integrations=18,
          maximum_profile_rmse_allowance=.001, temporal_share_limit=1e-8))
    print(sha(BUNDLE/'FREEZE.json'))


def check_freeze():
    f = read(BUNDLE/'FREEZE.json')
    if any(sha(ROOT/p) != h for p, h in f['files'].items()):
        raise ValueError('frozen scientific/input identity changed')


def check_inputs(args):
    f = read(BUNDLE/'FREEZE.json')
    if sha(args.private/'inputs.json') != f['private_inputs_sha256']:
        raise ValueError('private model inputs differ from freeze')
    manifest = read(BUNDLE/'INPUT_MANIFEST.json')
    for p, h in manifest['reused_puckworks'].items():
        if sha(ROOT/p) != h:
            raise ValueError('retained Puckworks evidence differs from manifest: '+p)
    if args.ewp is not None:
        for p, h in manifest['reused_ewp'].items():
            if sha(args.ewp/p) != h:
                raise ValueError('retained EWP evidence differs from manifest: '+p)
    if read(args.private/'inputs.json') != profiles():
        raise ValueError('source membership or nonchemical observation inputs changed')


def verify(args):
    check_freeze()
    s = m.Scenario('caffeine', 90., 2.)
    front = s.constants()['front_s']
    w = np.array([[0., .2*front], [.2*front, .6*front], [.6*front, .95*front],
                  [.95*front, 1.05*front], [1.05*front, 1.3*front], [1.3*front, 2*front]])
    liquid = np.array([.008, .007, .006, .005, .004, .003])
    exact = m.equilibrium_averages(s, w)
    ep = m.normalize(exact, liquid)[0]
    fast = []
    for n in (50, 100, 200):
        grid = m.grid_equilibrium_averages(s, w, n)
        gp = m.normalize(grid, liquid)[0]
        for rate in (1., 10., 100.):
            c, ledger = m.finite_averages(s, w, cells=n, rate_scale=rate)
            p = m.normalize(c, liquid)[0]
            fast.append(dict(rate_scale=rate, share_rmse_to_continuum=m.rmse(p-ep),
                             share_rmse_to_grid_limit=m.rmse(p-gp),
                             grid_share_rmse_to_continuum=m.rmse(gp-ep), **ledger))
            print(f'synthetic N={n} rate={rate:g}', flush=True)
    base, budget = m.finite_averages(s, w, cells=40)
    rad, sol = m.independent_radau(s, w)
    base_share = m.normalize(base, liquid)[0]
    scale_checks = []
    for scale in (.001, 10.):
        c, _ = m.finite_averages(s, w, cells=40, scale=scale)
        eq = m.equilibrium_averages(s, w, scale=scale)
        scale_checks.append(dict(scale=scale, finite_max_share_difference=float(np.max(abs(m.normalize(c, liquid)[0]-base_share))),
                                 equilibrium_max_share_difference=float(np.max(abs(m.normalize(eq, liquid)[0]-ep))),
                                 finite_mass_ratio=float(np.sum(c*liquid)/np.sum(base*liquid))))
    state = sol.y[:, -1]
    st = s.system(40)
    independent_total = st.W*(m.ps.ALPHA_L*state[:40].sum()+st.as1*state[40:80].sum()
                              +m.ps.PHI_V2*st.as2*state[80:120].sum())+state[-1]
    result = dict(fast_transfer=fast, scale_checks=scale_checks, synthetic_integrations=16,
                  independent_radau_max_share_difference=float(np.max(abs(m.normalize(rad, liquid)[0]-base_share))),
                  independent_radau_mass_residual=abs(independent_total/st.M0(s.T)-1),
                  equilibrium_complete_delivery_relative_error=abs(s.Q*exact.dot(w[:, 1]-w[:, 0])/st.M0(s.T)-1),
                  rate_convergence_to_grid=all(next(x for x in fast if x['cells']==n and x['rate_scale']==100)['share_rmse_to_grid_limit']
                  < next(x for x in fast if x['cells']==n and x['rate_scale']==10)['share_rmse_to_grid_limit']
                  < next(x for x in fast if x['cells']==n and x['rate_scale']==1)['share_rmse_to_grid_limit'] for n in (50,100,200)))
    result['passed'] = bool(result['rate_convergence_to_grid'] and result['independent_radau_max_share_difference'] < 1e-8
                            and result['independent_radau_mass_residual'] < 1e-9
                            and max(x['finite_max_share_difference'] for x in scale_checks) < 1e-9
                            and result['equilibrium_complete_delivery_relative_error'] < 1e-12)
    write(BUNDLE/'VERIFICATION.json', result)
    csvout(BUNDLE/'FAST_TRANSFER.csv', fast)
    print('synthetic passed:', result['passed'])


def predict(args):
    check_freeze()
    check_inputs(args)
    dest = args.private/'predictions'
    dest.mkdir(parents=True, exist_ok=True)
    records = []
    for p in read(args.private/'inputs.json'):
        s = scenario(p)
        cache = dest/(p['shot']+'-'+p['analyte']+'.json')
        if cache.exists():
            record = read(cache)
            if record['freeze_sha256'] != sha(BUNDLE/'FREEZE.json'):
                raise ValueError('stale prediction cache')
            records.append(record)
            continue
        concentrations, ledgers = [], []
        for n, halves in ((400, False), (800, False), (1600, False), (1600, True)):
            c, ledger = m.finite_averages(s, p['windows'], cells=n, halves=halves)
            concentrations.append(c)
            ledgers.append(ledger)
        c0, c1, nominal, temporal = concentrations
        constants = s.constants()
        error = 2*abs(nominal-c1)+abs(nominal-temporal)+1e-11*constants['c_s0']
        finite, delta, q = m.normalize(nominal, p['liquid_mass_kg'], errors=error, inventory_kg=constants['initial_total_kg'])
        eq = m.equilibrium_averages(s, p['windows'])
        equil, _, eq_q = m.normalize(eq, p['liquid_mass_kg'], inventory_kg=constants['initial_total_kg'])
        temporal_delta = float(np.max(abs(finite-m.normalize(temporal, p['liquid_mass_kg'])[0])))
        coarse_change, fine_change = float(np.max(abs(c1-c0))), float(np.max(abs(nominal-c1)))
        ratio = fine_change/coarse_change if coarse_change else 0.
        contraction = ratio <= .8 or max(coarse_change, fine_change) < 1e-10*constants['c_s0']
        record = dict(**p, freeze_sha256=sha(BUNDLE/'FREEZE.json'), constants=constants,
                      finite=finite.tolist(), equilibrium=equil.tolist(), finite_share_allowance=delta.tolist(),
                      finite_loss_allowance=m.rmse(delta), equilibrium_loss_allowance=1e-12,
                      finite_concentration=nominal.tolist(), equilibrium_concentration=eq.tolist(),
                      finite_conditional_kg=q.tolist(), equilibrium_conditional_kg=eq_q.tolist(),
                      concentration_allowance=error.tolist(), temporal_share_change=temporal_delta,
                      spatial_contraction_ratio=ratio, ledgers=ledgers,
                      qualified=bool(contraction and m.rmse(delta) <= .001 and temporal_delta <= 1e-8))
        write(cache, record)
        records.append(record)
        print(p['shot'], p['analyte'], 'qualified', record['qualified'], 'allowance', record['finite_loss_allowance'], flush=True)
    write(args.private/'predictions.json', records)
    summary = dict(profiles=len(records), integrations=4*len(records), all_qualified=all(r['qualified'] for r in records),
                   max_loss_allowance=max(r['finite_loss_allowance'] for r in records),
                   max_temporal_share_change=max(r['temporal_share_change'] for r in records),
                   max_spatial_contraction_ratio=max(r['spatial_contraction_ratio'] for r in records),
                   max_mass_residual=max(g['mass_balance_relative'] for r in records for g in r['ledgers']),
                   prediction_sha256=sha(args.private/'predictions.json'), freeze_sha256=sha(BUNDLE/'FREEZE.json'))
    write(BUNDLE/'NUMERICS.json', summary)


def score(args):
    check_freeze()
    check_inputs(args)
    audit = read(args.audit)
    if audit.get('status') != 'APPROVED' or audit.get('freeze_sha256') != sha(BUNDLE/'FREEZE.json'):
        raise ValueError('independent pre-score audit absent/mismatched')
    numerics = read(BUNDLE/'NUMERICS.json')
    if not numerics['all_qualified'] or not read(BUNDLE/'VERIFICATION.json')['passed']:
        raise ValueError('numerical comparison unavailable')
    if sha(args.private/'predictions.json') != numerics['prediction_sha256']:
        raise ValueError('prediction identity changed')
    prediction = read(args.private/'predictions.json')
    pp = read(args.private/'inputs.json')
    if len(prediction) != 24 or len(pp) != 24:
        raise ValueError('incomplete prediction support')
    for record, model_input in zip(prediction, pp):
        if {k: record[k] for k in model_input} != model_input:
            raise ValueError('prediction inputs do not equal frozen inputs')
    accepted_freezes = {sha(BUNDLE/'FREEZE.json'), read(BUNDLE/'FREEZE.json')['reused_numerical_freeze_sha256']}
    if any(r['freeze_sha256'] not in accepted_freezes for r in prediction):
        raise ValueError('unknown numerical producer freeze')
    targets = rows(DATA/'prediction_fraction_replicates.csv')
    historical = rows(args.ewp/'docs/analysis/obs_pannusch_fraction_window_001/OBSERVER_RESULTS.csv')
    manifest = read(BUNDLE/'INPUT_MANIFEST.json')
    reference = None
    if manifest['paired_reference']['status'] == 'AVAILABLE':
        if sha(args.reference) != manifest['paired_reference']['sha256']:
            raise ValueError('paired reference hash mismatch')
        rr = rows(args.reference)
        reference = {(r['condition'], r['shot'], r['analyte']): r for r in rr}
        if len(reference) != 24 or len(rr) != 24:
            raise ValueError('paired reference support mismatch')
    errors, detail = [], []
    for p in prediction:
        g = sorted([r for r in targets if r['shot_id']==p['shot'] and r['analyte']==p['analyte']], key=lambda r:int(r['fraction_id']))
        obs_mass = np.array([float(r['derived_analyte_mass_mg']) for r in g])
        if not np.isfinite(obs_mass).all() or np.any(obs_mass < 0) or obs_mass.sum() <= 0:
            raise ValueError('invalid observed profile')
        obs = obs_mass/obs_mass.sum()
        old = sorted([r for r in historical if r['shot_id']==p['shot'] and r['analyte']==p['analyte']], key=lambda r:int(r['profile_position']))
        if len(old) != 6 or tuple(int(r['source_fraction_id']) for r in old) != m.FRACTIONS:
            raise ValueError('historical support mismatch')
        if np.max(abs(obs-np.array([float(r['observed_share']) for r in old]))) > 1e-12:
            raise ValueError('historical target mismatch')
        historical_windows = np.array([[float(r['window_start_s']), float(r['window_end_s'])] for r in old])
        if np.max(abs(historical_windows-np.array(p['windows']))) > 5.1e-9:
            raise ValueError('historical observation windows differ')
        hp = np.array([float(r['O0_predicted_share']) for r in old])
        h_loss = m.rmse(hp-obs)
        e = dict(condition=p['condition'], shot=p['shot'], analyte=p['analyte'])
        for arm in ('finite', 'equilibrium'):
            residual = np.asarray(p[arm])-obs
            e[arm] = m.rmse(residual)
            e[arm+'_early'] = float(residual[:2].sum())
            e[arm+'_tail'] = float(residual[-2:].sum())
            e[arm+'_cumulative_rmse'] = m.rmse(np.cumsum(residual))
            e[arm+'_allowance'] = p[arm+'_loss_allowance']
        e.update(gain_finite=e['equilibrium']-e['finite'], gain_allowance=e['finite_allowance']+e['equilibrium_allowance'],
                 historical_loss=h_loss, finite_minus_historical=e['finite']-h_loss,
                 finite_historical_max_share_delta=float(np.max(abs(np.asarray(p['finite'])-hp))),
                 arm_prediction_rmse=m.rmse(np.asarray(p['finite'])-p['equilibrium']))
        if reference is not None:
            ref = reference[(p['condition'], p['shot'], p['analyte'])]
            if abs(float(ref['pannusch'])-h_loss)>1e-10:
                raise ValueError('C1 retained paired error identity not reproduced')
            e['boundary'] = float(ref['boundary'])
            e['gain_finite_vs_boundary'] = e['boundary']-e['finite']
            e['gain_equilibrium_vs_boundary'] = e['boundary']-e['equilibrium']
        errors.append(e)
        for j in range(6):
            detail.append(dict(condition=p['condition'], shot=p['shot'], analyte=p['analyte'], position=j+1,
                               source_fraction_id=m.FRACTIONS[j], observed=obs[j], finite=p['finite'][j], equilibrium=p['equilibrium'][j],
                               finite_residual=p['finite'][j]-obs[j], equilibrium_residual=p['equilibrium'][j]-obs[j],
                               finite_allowance=p['finite_share_allowance'][j]))
    write(args.private/'scored_profiles.json', errors)
    csvout(args.private/'fraction_results.csv', detail)
    measures = [k for k in errors[0] if k not in ('condition', 'shot', 'analyte')]
    summary = []
    for cond in ('ALL',)+m.CONDITIONS:
        for analyte in ('BOTH',)+m.SPECIES:
            sel = [r for r in errors if (cond=='ALL' or r['condition']==cond) and (analyte=='BOTH' or r['analyte']==analyte)]
            summary.append(dict(condition=cond, analyte=analyte, **{k:m.balanced(sel,k) for k in measures}))
    csvout(BUNDLE/'LOSSES.csv', summary)
    family = []
    omissions = [('BASELINE','NONE')]+[('LEAVE_SHOT_OUT',s) for s in sorted({r['shot'] for r in errors})]+[('LEAVE_CONDITION_OUT',c) for c in m.CONDITIONS]
    for kind, identity in omissions:
        sel = [r for r in errors if not (kind=='LEAVE_SHOT_OUT' and r['shot']==identity) and not (kind=='LEAVE_CONDITION_OUT' and r['condition']==identity)]
        for analyte in ('BOTH',)+m.SPECIES:
            chosen = [r for r in sel if analyte=='BOTH' or r['analyte']==analyte]
            r = dict(reduction=kind, omitted=identity, analyte=analyte, **{k:m.balanced(chosen,k) for k in measures})
            r['numerically_resolved'] = abs(r['gain_finite'])>r['gain_allowance']
            family.append(r)
    csvout(BUNDLE/'DELETIONS.csv', family)
    residuals = []
    for analyte in ('BOTH',)+m.SPECIES:
        for j in range(1,7):
            sel = [r for r in detail if r['position']==j and (analyte=='BOTH' or r['analyte']==analyte)]
            residuals.append(dict(analyte=analyte, position=j, source_fraction_id=m.FRACTIONS[j-1],
                                 **{k:m.balanced(sel,k) for k in ('finite_residual','equilibrium_residual','finite_allowance')}))
    csvout(BUNDLE/'RESIDUALS.csv', residuals)
    result = dict(task_id=TASK, baseline=summary[0], finite_sensitivity_cases=17,
                  sensitivity={a:dict(gain_min=min(r['gain_finite'] for r in family if r['analyte']==a),
                  gain_max=max(r['gain_finite'] for r in family if r['analyte']==a),
                  positive_count=sum(r['gain_finite']>0 for r in family if r['analyte']==a),
                  resolved_count=sum(r['numerically_resolved'] for r in family if r['analyte']==a)) for a in ('BOTH',)+m.SPECIES},
                  empirical_reference='PAIRED_RETAINED_ERRORS_REUSED' if reference else 'UNAVAILABLE',
                  practical_materiality='NOT_ESTABLISHED', PHYSICAL_VALIDATION='NOT_ESTABLISHED',
                  freeze_sha256=sha(BUNDLE/'FREEZE.json'), prediction_sha256=numerics['prediction_sha256'],
                  private_scored_profiles_sha256=sha(args.private/'scored_profiles.json'),
                  private_fraction_results_sha256=sha(args.private/'fraction_results.csv'))
    write(BUNDLE/'RESULTS.json', result)
    print(json.dumps(result, indent=2))


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('stage', choices=('prepare','freeze','verify','predict','score'))
    p.add_argument('--private', type=Path, required=True)
    p.add_argument('--ewp', type=Path)
    p.add_argument('--reference', type=Path)
    p.add_argument('--audit', type=Path)
    args = p.parse_args()
    args.private.mkdir(parents=True, exist_ok=True)
    globals()[args.stage](args)


if __name__ == '__main__':
    main()
