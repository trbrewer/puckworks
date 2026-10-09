"""Fixed 007 orchestration over unchanged production and scientific primitives.

All numerical entry points are called only by the locked, budgeted 007 worker.
The inherited schema identifies storage, never execution authority.
"""
from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
from types import SimpleNamespace
import gc
import json
import time

import numpy as np

from . import grudeva2026_baseline_observation_005 as obs
from . import grudeva2026_baseline_observation_005_diagnosis as diagnosis
from . import grudeva2026_baseline_observation_005_report as report
from . import grudeva2026_spatial_resolution_006 as previous
from .grudeva2026_spatial_resolution_006_report import individual_details

require = previous.require
write_new = previous.write_new
checkpoint = previous.checkpoint
ROOT = Path(__file__).resolve().parents[2]
DOCS = ROOT/'docs/analysis/model_grudeva2026_fine_baseline_qualification_007'
TASK = 'MODEL-GRUDEVA2026-FINE-BASELINE-QUALIFICATION-007'
BASE = dict(cells=512, modes=32, front_mesh_power=2., rtol=2e-8, atol=2e-10, max_step=.05)
ROWS = dict(baseline_512=BASE, control_512=BASE, repeat_512=BASE,
    modes_fine=dict(BASE, modes=64), time_fine=dict(BASE, rtol=2e-9, atol=2e-11, max_step=.025),
    bed_fine=dict(BASE, cells=1024), combined=dict(BASE, cells=1024, modes=64, rtol=2e-9, atol=2e-11, max_step=.025))
FULL = tuple(k for k in ROWS if k != 'baseline_512')
REFINEMENTS = FULL[2:]
ATTEMPTS = ('007-readout', '007-pilot', *('007-'+n for n in FULL), '007-reduction')
GATES = frozenset(('complete_status solver_segments horizon events activation_support required_times '
    'conservation aqueous_bounds grain_bounds phase_bounds front_support cup_quadrature cup_state_integral '
    'independent_inventory_sums public_inventory_algebra public_profile_reconstruction '
    'public_cup_outlet_reconstruction diagnostic_inlet tail_weights_rates '
    'diagnostic_liquid_profile_bounds diagnostic_grain_profile_bounds diagnostic_grain_history_bounds').split())
SEGMENT_SCIENCE = ('requested_interval', 'fixed', 'dripping', 'geometry', 'success', 'status', 'message',
    'nfev', 'njev', 'nlu', 'valid_interval', 'event_channels', 'dense_side', 'array_manifest')
QUALIFIED = 'FINE_BASELINE_RAW_OBSERVATION_NUMERICALLY_QUALIFIED_ON_DECLARED_CASES'
INCOMPLETE = 'FINE_BASELINE_QUALIFICATION_INCOMPLETE'


def controls(row, value):
    from puckworks.models.grudeva2026.reduced import Controls
    require(row in ROWS and value == ROWS[row], 'unauthorized row/settings')
    return Controls(**value)


def verify_plan(plan):
    from puckworks.models.grudeva2026.reduced import Parameters
    require(plan['task'] == TASK and plan['rows'] == ROWS, '007 matrix identity differs')
    require(plan['horizon'] == 8. and plan['pilot_horizon'] == .4, 'horizon differs')
    require(plan['parameters'] == asdict(Parameters()), 'canonical parameters differ')
    for key, horizon in [('requests', 8.), ('pilot_requests', .4)]:
        require(plan[key] == obs.requests(horizon), 'request differs: '+key)
    require(plan['segment_science_fields'] == list(SEGMENT_SCIENCE), 'equality projection changed')
    for scope in ('scientific_sources', 'adapter_sources'):
        for name, expected in plan[scope].items():
            require(obs.sha(ROOT/name) == expected, 'source mismatch: '+name)
    require(obs.sha(DOCS/'CONTRACT.md') == plan['contract_sha256'], 'contract changed')


def bound_json(folder, binding):
    name = binding['file']
    require(Path(name).name == name, 'unsafe evidence filename')
    path = Path(folder)/name
    require(obs.sha(path) == binding['sha256'], 'evidence identity mismatch: '+name)
    return obs.read_json(path)


def baseline_inputs(folder, historical, plan, *, arrays=False):
    """Preserve original 006 task, attempt, plan and artifact identities."""
    binding = plan['reuse']
    for filename, expected in binding['files'].items():
        require(Path(filename).name == filename, 'unsafe predecessor filename')
        require(obs.sha(Path(folder)/filename) == expected, '006 artifact changed: '+filename)
    require(obs.sha(Path(historical)/'invocations.jsonl') == binding['005_ledger_sha256'], '005 ledger changed')
    original_plan=obs.read_json(previous.DOCS/'PLAN.json')
    require(binding['005_ledger_sha256']==original_plan['historical_ledger']['sha256'] and
            obs.digest(str(Path(folder).resolve()))==original_plan['evidence_root_sha256'] and
            obs.digest(str(Path(historical).resolve()))==original_plan['historical_root_sha256'],
            'original predecessor ledger/root binding differs')
    meta = bound_json(folder, binding['metadata'])
    require(meta['task'] == previous.TASK and meta['row'] == previous.ROW and
            meta['attempt'] == '006-spatial-512', 'original baseline authority differs')
    require(meta['environment'] == plan['environment'] == obs.environment(), 'baseline environment mismatch')
    require(meta['adapter_sources'] == obs.read_json(previous.DOCS/'PLAN.json')['adapter_sources'],
            'original adapter binding differs')
    require(not report.check_run(meta, BASE, obs.sha(previous.DOCS/'PLAN.json')), 'invalid 006 baseline metadata')
    require(bound_json(folder, meta['public_checkpoint']) == meta['public_result'], 'baseline public Result differs')
    accounting = obs.read_json(previous.DOCS/'ACCOUNTING.json')['resources']
    require(accounting['passed'] and not accounting['unresolved_starts'] and
            (accounting['full'], accounting['short'], accounting['seconds']) == (1, 2, 166.21631713100942),
            '006 accounting is not the accepted closed record')
    ledger = [json.loads(s) for s in (Path(folder)/'invocations.jsonl').read_text().splitlines()]
    ends = {r['name']: r for r in ledger if r['event'] == 'end'}
    require(set(ends)==set(accounting['ends']) and all(
        ends[n].get(k)==v for n,end in accounting['ends'].items() for k,v in end.items()), '006 closed end receipts differ')
    require(ends['006-spatial-512']['artifact_sha256'] == binding['metadata']['sha256'] and
            ends['006-spatial-512']['observations_sha256'] == binding['observations']['sha256'],
            '006 ledger capture/observation binding differs')
    require(sum(e['seconds'] for e in ends.values()) == accounting['seconds'], '006 consumption differs')
    if arrays:
        tr = obs.Trajectory(Path(folder)/binding['metadata']['file'])
        try:
            require(tr.horizon == 8. and tr.arrival is not None and len(tr.segments) == 3,
                    'baseline segment/event/horizon coverage differs')
        finally:
            tr.close()
    return meta


def fixture_summary(family, cells, modes, frozen):
    """Spectrum-aware reporting only; expected values remain the unchanged diagnosis."""
    require([dict(t=c['t'], z=c['z']) for c in family['cases']] == frozen['cases'], 'fixture coordinates differ')
    rows = [dict(t=c['t'], z=z, age=age, signed_error=e, eligible=eligible)
        for c in family['cases'] for z, age, e, eligible in
        zip(c['z'], c['age'], c['signed_error'], c['positive_age_mask'])]
    require(len(rows) == 139 and sum(r['eligible'] for r in rows) == 84, 'fixture support differs')
    require(all(r['age'] == r['t']-r['z']/.2 and r['eligible'] == (r['age'] >= .02) for r in rows),
            'fixture eligibility differs')
    def summary(selected):
        finite = [r for r in selected if np.isfinite(r['signed_error'])]
        maximum = max(finite, key=lambda r: abs(r['signed_error'])) if finite else None
        return dict(requested=len(selected), included=len(finite), excluded=0, unavailable=len(selected)-len(finite),
            maximum=maximum, max_absolute=abs(maximum['signed_error']) if maximum else None, allowance=2e-5,
            signed_min=min(finite, key=lambda r:r['signed_error']) if finite else None,
            signed_max=max(finite, key=lambda r:r['signed_error']) if finite else None,
            exceedances=sum(abs(r['signed_error']) > 2e-5 for r in finite),
            passed=bool(finite) and len(finite)==len(selected) and all(abs(r['signed_error'])<=2e-5 for r in finite))
    indices = sorted({0, 31, modes-1, modes})
    expected = [(frozen['cases'][s['case_index']]['t'], s['cell'] % cells, k)
        for s in frozen['independent_average_subset'] for k in indices]
    checks = family['independent_average_checks']
    actual = [(c['t'], c['cell'], c['mode']) for c in checks]
    require(len(expected) == len(set(expected)) and sorted(actual) == sorted(expected),
            'independent reference identities differ')
    valid = [c for c in checks if np.isfinite(c['signed_difference']) and
             np.isfinite(c['quadrature_estimated_error']) and c['quadrature_estimated_error'] >= 0]
    maximum = max(valid, key=lambda c:abs(c['signed_difference'])+c['quadrature_estimated_error']) if valid else None
    uncertainty = abs(maximum['signed_difference'])+maximum['quadrature_estimated_error'] if maximum else None
    reference = dict(required_identities=expected, mode_indices=indices, requested=len(expected), included=len(valid),
        excluded=0, unavailable=len(expected)-len(valid), maximum=maximum, discrepancy_plus_uncertainty=uncertainty,
        allowance=1e-11, passed=len(valid)==len(expected) and uncertainty is not None and uncertainty <= 1e-11)
    endpoints = [r for r in rows if r['z'] == min(.2*r['t'], 1.)]
    return dict(requested=139, included=84, excluded=55, unavailable=139-sum(np.isfinite(r['signed_error']) for r in rows),
        eligible=summary([r for r in rows if r['eligible']]), younger=summary([r for r in rows if not r['eligible']]),
        all_points=summary(rows), raw_polynomial_endpoints=summary(endpoints), independent_reference=reference,
        advancing_front_assignment=[dict(t=r['t'], z=r['z'], actual=obs.INITIAL, expected=obs.INITIAL,
            assignment_error=0., raw_polynomial_signed_error=r['signed_error']) for r in endpoints if r['t']<5.])


def readout(folder, prior, historical, plan):
    path = folder/'007-readout.json'
    result = dict(task=TASK, attempt='007-readout', plan_sha256=obs.sha(DOCS/'PLAN.json'), passed=False,
        physical_validation='NOT_ESTABLISHED', meshes={}, baseline_reuse=False)
    write_new(path, result)
    try:
        meta = baseline_inputs(prior, historical, plan, arrays=True)
        baseline = bound_json(prior, plan['reuse']['observations'])
        accepted = obs.read_json(previous.DOCS/'RESULTS.json')
        gates = report.numeric_gates(baseline, meta)
        require(set(gates)==GATES and gates==accepted['candidate_gates'] and all(gates.values()), 'baseline audit binding failed')
        require(baseline['audits']==accepted['candidate_audits'], 'baseline audit values differ')
        result.update(baseline_reuse=True, baseline_gates=gates)
        result['inherited_fixture_gates'] = report.fixture_audit(historical, obs.read_json(previous.OLD_DOCS/'MATRIX.json'))
        frozen = previous.fixture_plan()
        from puckworks.models.grudeva2026.kernel import modal_spectrum
        for cells, modes in ((512,32), (512,64), (1024,32), (1024,64)):
            w, rates = modal_spectrum(1., modes)
            spectral = obs.spectrum_audit(w, rates)
            require(max(spectral['weight_error'], spectral['rate_relative_error']) <= obs.ALGEBRA, 'invalid spectrum')
            if (cells,modes)==(512,32):
                raw = bound_json(prior, plan['reuse']['fixture'])
                require(raw['spectrum_weights']==meta['geometry']['w'] and raw['spectrum_rates']==meta['geometry']['rates'],
                        'reused fixture spectrum differs from capture')
            else:
                carrier = SimpleNamespace(n=cells, m=modes+1, weights=w, rates=rates,
                    faces=1-(1-np.arange(cells+1)/cells)**2)
                raw = diagnosis.fixture_diagnosis(carrier, frozen)
                write_new(folder/f'007-fixture-{cells}-{modes}.json', raw)
            require(raw['cells']==cells and raw['modes_including_tail']==modes+1 and
                    raw['spectrum_weights']==w.tolist() and raw['spectrum_rates']==rates.tolist(), 'fixture configuration differs')
            require(set(raw['families'])=={'zero_boundary','nonconstant'}, 'missing fixture family')
            result['meshes'][f'{cells}/{modes}'] = dict(reused=(cells,modes)==(512,32), spectrum=spectral,
                weights=w.tolist(), rates=rates.tolist(), families={n:fixture_summary(f,cells,modes,frozen)
                    for n,f in raw['families'].items()})
            checkpoint(path,result)
        result['passed'] = result['inherited_fixture_gates']['passed'] and all(
            f['eligible']['passed'] and f['independent_reference']['passed'] and not f['unavailable']
            for m in result['meshes'].values() for f in m['families'].values())
    except Exception as exc:
        result['failure'] = dict(type=type(exc).__name__, reason=str(exc), category='source_environment_rights')
        for key in ('512/32','512/64','1024/32','1024/64'):
            result['meshes'].setdefault(key,dict(families={name:dict(requested=139,included=0,excluded=0,
                unavailable=139,eligible_requested=84,younger_requested=55,passed=False,
                reason='required assessment unavailable') for name in ('zero_boundary','nonconstant')}))
        checkpoint(path,result)
        raise
    checkpoint(path,result)
    return result


def validate_new(meta, row, plan, *, pilot=False):
    """Validate genuine 007 metadata; do not impersonate a predecessor task."""
    request = plan['pilot_requests' if pilot else 'requests']
    attempt = '007-pilot' if pilot else '007-'+row
    require(meta['task']==TASK and meta['attempt']==attempt and meta['row']==row, '007 execution binding differs')
    require(meta['horizon']==(.4 if pilot else 8.) and meta['controls']==ROWS[row], '007 settings differ')
    require(meta['observed']==(row!='control_512'), 'control/repeat observation authority differs')
    require(meta['matrix_sha256']==obs.sha(DOCS/'PLAN.json') and meta['adapter_sources']==plan['adapter_sources'], '007 source/plan differs')
    require(meta['environment']==plan['environment']==obs.environment(), '007 environment differs')
    require(meta['parameters']==plan['parameters'] and meta['sources']==obs.sources(), 'scientific binding differs')
    require(meta['requests']==request and meta['request_hashes']=={k:obs.digest(v) for k,v in request.items()}, 'request binding differs')
    public = meta['public_result']
    require(obs.digest(public)==meta['public_result_sha256'] and public['controls']==ROWS[row] and
            public['parameters']==plan['parameters'], 'complete public Result binding differs')
    require(public['time']==request['public_times'] and public['profile_z']==request['public_z'], 'public support differs')
    if not pilot:
        require(not report.check_run(meta, ROWS[row], obs.sha(DOCS/'PLAN.json')), 'inherited capture checks failed')
    if meta['observed']:
        require(meta['restored'] and meta['public_result_unchanged_after_capture'] and
                meta['returned']==meta['solve_invocations']==len(meta['segments'])>0, 'capture incomplete')
        for s in meta['segments']:
            require(s['attempt']==attempt and all(s.get(k)=='PASS' for k in
                ('capture_outcome','artifact_integrity','array_fidelity','numerical_replay')), 'persistence incomplete')
            require(s['live_replay']['allowance_fraction']<=1 and
                max(s['live_replay']['accepted_state_error'],s['live_replay']['event_state_error'])<=obs.ALGEBRA*8,
                'live replay failed')


def equality(a, b):
    """No public scientific fields or observation fields are excluded."""
    return dict(passed=obs.canonical(a)==obs.canonical(b), left_sha256=obs.digest(a), right_sha256=obs.digest(b))


def repeat_equality(meta, base, observed, baseline):
    fields = {k:equality(meta[k],base[k]) for k in ('public_result','controls','parameters','requests','sources','environment','geometry','state_layout')}
    fields['retained_scientific_state'] = equality(
        [{k:s[k] for k in SEGMENT_SCIENCE} for s in meta['segments']],
        [{k:s[k] for k in SEGMENT_SCIENCE} for s in base['segments']])
    fields['complete_observations_and_audits'] = equality(observed,baseline)
    return dict(passed=all(v['passed'] for v in fields.values()), fields=fields)


def pilot_gates(observed, meta):
    """Full-horizon event/activation gates do not apply to the truncated pilot."""
    gates = report.numeric_gates(observed,meta)
    gates['horizon'] = observed['audits']['horizon']==.4
    gates['events'] = not observed['events'] and observed['arrival'] is None
    front = observed['records'][-1][1]
    gates['activation_support'] = all((t is not None and 0<=t<=.4) if z<=front else t is None
        for zs,ts in ((observed['z'],observed['activation']),
                      (observed['grain_history_z'],observed['grain_history_activation'])) for z,t in zip(zs,ts))
    require(set(gates)==GATES, 'pilot audit coverage differs')
    return gates


def simulate_row(folder, prior, plan, row, *, pilot=False):
    from puckworks.models.grudeva2026 import reduced
    from puckworks import rights
    require(rights.may_execute_locally('grudeva2026.reduced').allowed, 'local execution rights unavailable')
    attempt = '007-pilot' if pilot else '007-'+row
    path = folder/(attempt+'.json')
    request = plan['pilot_requests' if pilot else 'requests']
    ctrl = controls(row,plan['rows'][row])
    size = 2+ctrl.cells*(ctrl.modes+2)
    observed_call = row!='control_512'
    meta = dict(schema=obs.SCHEMA, storage_semantics='005 storage format only; 007 execution authority',
        task=TASK, attempt=attempt, row=row, horizon=.4 if pilot else 8., observed=observed_call,
        status='EXECUTED_UNQUALIFIED', passed=False, controls=asdict(ctrl), parameters=plan['parameters'],
        requests=request, request_hashes={k:obs.digest(v) for k,v in request.items()}, sources=obs.sources(),
        adapter_sources=plan['adapter_sources'], environment=obs.environment(), matrix_sha256=obs.sha(DOCS/'PLAN.json'),
        physical_validation='NOT_ESTABLISHED', segments=[], phase_seconds={},
        state_layout=dict(size=size, modal_shape=[ctrl.modes+1,ctrl.cells], modal_axis=0, order='s,liquid,mode-major,cup'))
    write_new(path,meta)
    captured=[]
    original = reduced.solve_ivp
    def persist():
        for i,segment in enumerate(captured):
            try:
                if segment['solution'] is not None:
                    meta.setdefault('geometry',obs._production_geometry(segment))
                saved = obs.save_segment(folder,f'{attempt}-segment-{i}.npz',segment,size,attempt=attempt,segment_index=i)
            except Exception as exc:
                saved = getattr(exc,'metadata',dict(unavailable_reason=type(exc).__name__+': '+str(exc)))
            meta['segments'].append(saved)
            checkpoint(path,meta)
    started=time.perf_counter()
    try:
        if observed_call:
            with obs.capture_returns(reduced) as captured:
                result=reduced.simulate(controls=ctrl,times=request['public_times'],profile_z=request['public_z'])
        else:
            # Ordinary production call: no capture context, diagnostic callback or replacement seam.
            result=reduced.simulate(controls=ctrl,times=request['public_times'],profile_z=request['public_z'])
    except BaseException as exc:
        meta['original_exception']=dict(type=type(exc).__name__,message=str(exc))
        meta['restored']=reduced.solve_ivp is original
        try:
            checkpoint(path,meta)
            if observed_call:
                persist()
        except Exception:
            pass  # persistence cannot replace the original production exception
        raise
    meta['phase_seconds']['production']=time.perf_counter()-started
    started=time.perf_counter()
    public_bytes=result.canonical_json()
    meta.update(public_result=json.loads(public_bytes),public_result_sha256=obs.digest(json.loads(public_bytes)),
        restored=reduced.solve_ivp is original,solve_invocations=len(captured),returned=sum(s['solution'] is not None for s in captured))
    checkpoint(path,meta)  # keep the complete returned Result even if checkpoint publication fails
    public=folder/(attempt+'-public-result.json')
    write_new(public,meta['public_result'])
    meta['public_checkpoint']=dict(file=public.name,sha256=obs.sha(public))
    checkpoint(path,meta)
    meta['phase_seconds']['public_checkpoint']=time.perf_counter()-started
    started=time.perf_counter()
    if observed_call:
        persist()
    meta['public_result_unchanged_after_capture']=result.canonical_json()==public_bytes
    captured.clear()
    gc.collect()
    meta['phase_seconds']['persistence']=time.perf_counter()-started
    checkpoint(path,meta)
    validate_new(meta,row,plan,pilot=pilot)
    require(bound_json(folder,meta['public_checkpoint'])==meta['public_result'], 'public checkpoint mismatch')
    if not observed_call:
        base=bound_json(prior,plan['reuse']['metadata'])
        meta['neutrality']=equality(meta['public_result'],base['public_result'])
        meta['passed']=meta['neutrality']['passed'] and meta['public_result']['status']=='COMPLETED'
    else:
        started=time.perf_counter()
        observed=obs.observe_saved(path)
        observation_path=folder/(attempt+'-observations.json')
        write_new(observation_path,observed)
        meta['observation_binding']=dict(file=observation_path.name,sha256=obs.sha(observation_path))
        meta['gates']=pilot_gates(observed,meta) if pilot else report.numeric_gates(observed,meta)
        require(set(meta['gates'])==GATES, 'individual audit coverage differs')
        meta['audits']=observed['audits']
        meta['passed']=all(meta['gates'].values())
        checkpoint(path,meta)
        if not pilot:
            tr=obs.Trajectory(path)
            try:
                meta['individual_details']=individual_details(tr,observed)
            finally:
                tr.close()
            require(set(meta['individual_details'])==GATES, 'individual detail coverage differs')
            checkpoint(path,meta)
            base=bound_json(prior,plan['reuse']['metadata'])
            baseline=bound_json(prior,plan['reuse']['observations'])
            if row=='repeat_512':
                meta['repeatability']=repeat_equality(meta,base,observed,baseline)
                meta['passed'] &= meta['repeatability']['passed']
            else:
                meta['refinement']=report.refinement(baseline,observed)
                meta['passed'] &= comparisons_pass(meta['refinement'])
            del baseline
        meta['phase_seconds']['observations_audits_comparison']=time.perf_counter()-started
    meta['status']='ROW_PASSED' if meta['passed'] else 'EXECUTED_UNQUALIFIED'
    checkpoint(path,meta)
    return meta


def comparisons_pass(metrics):
    return set(metrics)==set(report.BUDGETS) and all(m['passed'] and m['included']>0 and m['unavailable']==0 for m in metrics.values())


def reduction(folder, prior, plan, audit):
    """The one solver-free reduction, including failure closeout and missing rows."""
    result=dict(task=TASK, plan_sha256=obs.sha(DOCS/'PLAN.json'), physical_validation='NOT_ESTABLISHED',
        disposition=INCOMPLETE, rows={}, comparisons={}, prerequisites={}, preliminary_accounting=audit,
        baseline_original_identity=plan['reuse']['metadata'], reasons={})
    for name in ATTEMPTS[:-1]:
        end=audit['ends'].get(name)
        path=folder/(name+'.json')
        if not end:
            result['rows'][name]=dict(status='NOT_RUN', passed=False)
            continue
        if not path.is_file() or obs.sha(path)!=end.get('artifact_sha256'):
            result['rows'][name]=dict(status='EXECUTION_INCOMPLETE',passed=False,reason='no identity-bound output',
                execution_exit_code=end['exit_code'],termination=end.get('termination'))
            continue
        r=obs.read_json(path)
        require(r['task']==TASK and r.get('plan_sha256',r.get('matrix_sha256'))==obs.sha(DOCS/'PLAN.json'), 'reduction binding differs')
        if name in ('007-readout','007-pilot'):
            result['prerequisites'][name]=dict(passed=r.get('passed',False),artifact_sha256=obs.sha(path),
                failure=r.get('failure'),gates=r.get('gates'),baseline_reuse=r.get('baseline_reuse'))
        result['rows'][name]={k:r[k] for k in ('status','passed','gates','audits','individual_details','neutrality','repeatability','phase_seconds','failure','original_exception') if k in r}
        result['rows'][name]['execution_exit_code']=end['exit_code']
        result['rows'][name]['termination']=end.get('termination')
        result['rows'][name]['artifact_sha256']=obs.sha(path)
        if name[4:] in REFINEMENTS:
            result['comparisons'][name[4:]]=r.get('refinement',report.unavailable_metrics('row did not complete comparison'))
    for row in REFINEMENTS:
        result['comparisons'].setdefault(row,report.unavailable_metrics('NOT_RUN or unavailable row'))
    accepted=obs.read_json(previous.DOCS/'RESULTS.json')
    result['baseline_gates']=accepted['candidate_gates']
    result['baseline_individual_details']=accepted['individual_details']
    result['baseline_reuse_validated']=result['prerequisites'].get('007-readout',{}).get('baseline_reuse') is True
    success=(all(result['rows'][n].get('passed',False) and audit['ends'].get(n,{}).get('exit_code')==0 for n in ATTEMPTS[:-1])
        and all(comparisons_pass(m) for m in result['comparisons'].values()) and all(result['baseline_gates'].values()))
    # The current reduction start is explicitly preliminary; closure is accounting-only.
    result['disposition']=QUALIFIED if success else INCOMPLETE
    result['reasons']={
        'integration_software': [], 'source_environment_rights': [],
        'resources_execution': [n+': '+r.get('status','PREREQUISITE_INCOMPLETE') for n,r in result['rows'].items()
            if r.get('status') in ('NOT_RUN','EXECUTION_INCOMPLETE') or r.get('execution_exit_code',0) not in (0,2) or r.get('termination')],
        'persistence_replay_observation': [],
        'neutrality_repeatability': [n for n in ('007-control_512','007-repeat_512') if not result['rows'][n].get('passed',False)],
        'individual_audits': {n:[k for k,v in r.get('gates',{}).items() if not v] for n,r in result['rows'].items() if r.get('gates') and not all(r['gates'].values())},
        'refinements': {n:[k for k,v in m.items() if not v['passed']] for n,m in result['comparisons'].items() if not comparisons_pass(m)}}
    for n,r in result['rows'].items():
        if r.get('failure'):
            result['reasons'][r['failure']['category']].append(dict(attempt=n,**r['failure']))
    if not result['prerequisites'].get('007-readout',{}).get('passed'):
        result['reasons']['persistence_replay_observation'].append('required readout unavailable or failed')
    admission=folder/'ADMISSION.json'
    if admission.exists():
        receipt=obs.read_json(admission)
        require(receipt['task']==TASK and receipt['plan_sha256']==obs.sha(DOCS/'PLAN.json'), 'admission binding differs')
        result['admission']=dict(file=admission.name,sha256=obs.sha(admission),passed=receipt['passed'])
        if not receipt['passed']:
            result['reasons']['resources_execution'].append(receipt.get('reason',receipt['conclusion']))
    write_new(folder/'007-reduction.json',result)
    return result
