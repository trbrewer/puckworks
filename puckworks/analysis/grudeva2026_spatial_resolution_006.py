"""Bounded 006 adapter: unchanged production evolution and 005 scientific readers."""
from __future__ import annotations

from dataclasses import asdict
import json
import os
import time
from pathlib import Path
from types import SimpleNamespace

import numpy as np

from . import grudeva2026_baseline_observation_005 as obs
from . import grudeva2026_baseline_observation_005_diagnosis as diagnosis
from . import grudeva2026_baseline_observation_005_report as inherited

TASK = 'MODEL-GRUDEVA2026-SPATIAL-RESOLUTION-006'
ROW = 'spatial_512'
CANDIDATE = dict(cells=512, modes=32, front_mesh_power=2., rtol=2e-8, atol=2e-10, max_step=.05)
ATTEMPTS = ('006-readout', '006-spatial-512', '006-reduction')
ROOT = Path(__file__).resolve().parents[2]
DOCS = ROOT/'docs/analysis/model_grudeva2026_spatial_resolution_006'
OLD_DOCS = ROOT/'docs/analysis/model_grudeva2026_baseline_observation_005'
REFERENCE_ALLOWANCE = 1e-11  # independent arithmetic check, never added to readout budget


def require(condition, reason):
    if not condition:
        raise ValueError(reason)


def candidate_controls(value):
    require(value == CANDIDATE, 'only the exact 512/32 candidate is authorized')
    from puckworks.models.grudeva2026.reduced import Controls
    return Controls(**value)


def write_new(path, value):
    payload = obs.canonical(diagnosis.array_json(value))+'\n'
    with Path(path).open('x') as stream:
        stream.write(payload); stream.flush(); os.fsync(stream.fileno())
    obs._sync_directory(Path(path).parent)


def checkpoint(path, value):
    # Reserved attempt name; durable partials, never replace the public checkpoint.
    from .grudeva2026_baseline_observation_005_attribution import checkpoint as save
    save(Path(path), diagnosis.array_json(value))


def verify_sources(plan):
    require(plan['task'] == TASK and plan['candidate'] == CANDIDATE, 'wrong task/candidate')
    for scope in ('scientific_sources', 'adapter_sources'):
        for name, expected in plan[scope].items():
            require(obs.sha(ROOT/name) == expected, 'source mismatch: '+name)
    require(obs.sha(DOCS/'CONTRACT.md') == plan['reporting_contract_sha256'], 'reporting contract changed')
    require(plan['request_hashes'] == {k: obs.digest(v) for k, v in obs.requests().items()},
            'public/diagnostic request changed')
    from puckworks.models.grudeva2026.reduced import Parameters
    require(plan['parameters'] == asdict(Parameters()), 'canonical parameters changed')


def historical_inputs(folder, plan, *, arrays=False):
    """Resolve metadata from frozen bindings, never from an inferred row filename."""
    folder = Path(folder)
    old = obs.read_json(OLD_DOCS/'ATTRIBUTION_PLAN.json')
    require(obs.sha(folder/'invocations.jsonl') == plan['historical_ledger']['sha256'],
            'closed 005 ledger changed')
    rows = {}
    for name in ('normal', 'bed_fine'):
        binding = plan['captures'][name]
        for filename, expected in binding['files'].items():
            require(Path(filename).name == filename, 'invalid evidence filename')
            require(obs.sha(folder/filename) == expected, 'historical evidence mismatch: '+filename)
        path = folder/binding['metadata_file']
        meta = obs.read_json(path)
        require(meta['task'] == obs.TASK and meta['row'] == name, 'historical task/row mismatch')
        errors = inherited.check_run(meta, obs.controls(name), binding['matrix_sha256'])
        require(not errors, '; '.join(errors))
        require(meta['environment'] == plan['environment'] == obs.environment(), 'environment mismatch')
        require(meta['controls'] == old['runs'][name]['controls'], 'wrong historical control')
        require(obs.read_json(folder/meta['public_checkpoint']['file']) == meta['public_result'],
                'complete public checkpoint differs')
        if arrays:
            tr = obs.Trajectory(path)
            try:
                require(tr.horizon == 8. and tr.arrival is not None, 'incomplete historical trajectory')
            finally:
                tr.close()
        rows[name] = meta
    for key in ('w', 'rates'):
        require(rows['normal']['geometry'][key] == rows['bed_fine']['geometry'][key],
                'historical spectrum mismatch')
    return rows


def fixture_plan():
    plan = obs.read_json(OLD_DOCS/'DIAGNOSIS_PLAN.json')['fixture']
    ages = [case['t']-z/.2 for case in plan['cases'] for z in case['z']]
    require(len(ages) == 139 and sum(age >= .02 for age in ages) == 84,
            'literal frozen fixture eligibility changed')
    require(plan['grain_allowance'] == 2e-5 and plan['initial'] == obs.INITIAL,
            'fixture allowance/initial value changed')
    return plan


def summarize_fixture_family(family):
    rows = [dict(t=c['t'], z=z, age=age, signed_error=error, eligible=eligible)
            for c in family['cases']
            for z, age, error, eligible in zip(c['z'], c['age'], c['signed_error'], c['positive_age_mask'])]
    require(len(rows) == 139 and sum(r['eligible'] for r in rows) == 84, 'fixture support mismatch')
    require(all(np.isfinite(r['signed_error']) for r in rows), 'fixture unavailable/nonfinite support')
    def summary(selected):
        if not selected:
            return dict(included=0, unavailable=0, maximum=None, passed=False, reason='empty support')
        maximum = max(selected, key=lambda r: abs(r['signed_error']))
        return dict(included=len(selected), unavailable=0, maximum=maximum,
                    max_absolute=abs(maximum['signed_error']), signed_min=min(selected, key=lambda r:r['signed_error']),
                    signed_max=max(selected, key=lambda r:r['signed_error']),
                    exceedances=sum(abs(r['signed_error']) > 2e-5 for r in selected),
                    allowance=2e-5, passed=all(abs(r['signed_error']) <= 2e-5 for r in selected))
    checks = family['independent_average_checks']
    require(len(checks) == 18, 'independent reference subset incomplete')
    valid = [c for c in checks if np.isfinite(c['signed_difference'])
             and np.isfinite(c['quadrature_estimated_error']) and c['quadrature_estimated_error'] >= 0]
    uncertainty = max((abs(c['signed_difference'])+c['quadrature_estimated_error'] for c in valid), default=None)
    reference = dict(requested=18, included=len(valid), excluded=0, unavailable=18-len(valid),
        max_discrepancy=max((abs(c['signed_difference']) for c in valid), default=None),
        max_reported_uncertainty=max((c['quadrature_estimated_error'] for c in valid), default=None),
        discrepancy_plus_uncertainty=uncertainty, allowance=REFERENCE_ALLOWANCE,
        maximum=max(valid, key=lambda c:abs(c['signed_difference'])+c['quadrature_estimated_error']) if valid else None,
        passed=bool(len(valid) == 18 and uncertainty is not None and uncertainty <= REFERENCE_ALLOWANCE),
        reason=None if len(valid) == 18 else 'nonfinite discrepancy or invalid numerical uncertainty')
    endpoints = [r for r in rows if r['z'] == min(.2*r['t'], 1.)]
    advancing = [dict(t=r['t'], z=r['z'], age=r['age'], raw_polynomial_signed_error=r['signed_error'],
                      actual_front_assignment=obs.INITIAL, expected_initial=obs.INITIAL, assignment_error=0.)
                 for r in endpoints if r['t'] < 5.]
    return dict(requested=139, included=84, excluded=55, unavailable=0,
        eligible=summary([r for r in rows if r['eligible']]), younger=summary([r for r in rows if not r['eligible']]),
        all_points=summary(rows), raw_polynomial_endpoints=summary(endpoints),
        advancing_front_assignment=advancing, independent_reference=reference)


def _screen_assess(folder, historical, plan):
    """Consolidated A invocation. Includes safe array validation and all new fixtures."""
    metas = historical_inputs(historical, plan, arrays=True)
    geometry = metas['normal']['geometry']
    from puckworks.models.grudeva2026.kernel import modal_spectrum
    w, rates = modal_spectrum(1., 32)
    require(np.array_equal(w, geometry['w']) and np.array_equal(rates, geometry['rates']),
            'actual production 32+tail spectrum differs')
    spectral = obs.spectrum_audit(w, rates)
    require(max(spectral['weight_error'], spectral['rate_relative_error']) <= obs.ALGEBRA,
            'independent spectrum check failed')
    frozen = fixture_plan()
    old_diag = obs.read_json(Path(historical)/plan['normal_fixture']['file'])
    require(obs.sha(Path(historical)/plan['normal_fixture']['file']) == plan['normal_fixture']['sha256'],
            'original 128/32 fixture identity mismatch')
    require(old_diag['plan_sha256'] == obs.sha(OLD_DOCS/'DIAGNOSIS_PLAN.json'), 'fixture plan mismatch')
    reused = old_diag['manufactured']['normal']
    require(reused['spectrum_weights'] == w.tolist() and reused['spectrum_rates'] == rates.tolist(),
            'reused normal fixture spectrum differs')
    require(reused['cells'] == 128 and reused['modes_including_tail'] == 33, 'reused fixture mesh differs')
    inherited_fixtures = inherited.fixture_audit(Path(historical), obs.read_json(OLD_DOCS/'MATRIX.json'))
    result = dict(task=TASK, attempt=ATTEMPTS[0], disposition='READOUT_ASSESSMENT_INCOMPLETE',
                  physical_validation='NOT_ESTABLISHED', spectrum=spectral, meshes={},
                  inherited_fixture_gates=inherited_fixtures, production_attempted=False,
                  plan_sha256=obs.sha(DOCS/'PLAN.json'))
    path = Path(folder)/(ATTEMPTS[0]+'.json')
    checkpoint(path, result)
    for cells in (128, 256, 512):
        carrier = SimpleNamespace(n=cells, m=33, weights=w, rates=rates,
                                  faces=1-(1-np.arange(cells+1)/cells)**2)
        raw = reused if cells == 128 else diagnosis.fixture_diagnosis(carrier, frozen)
        # Verify the literal coordinates even for reused evidence.
        for family in raw['families'].values():
            require([{'t':c['t'], 'z':c['z']} for c in family['cases']] == frozen['cases'],
                    'reused/new fixture physical support differs')
        summaries = {name:summarize_fixture_family(f) for name,f in raw['families'].items()}
        require(set(summaries) == {'zero_boundary', 'nonconstant'}, 'missing fixture family')
        result['meshes'][str(cells)] = dict(reused=cells == 128, families=summaries)
        if cells != 128:
            write_new(Path(folder)/f'006-fixture-{cells}-arrays.json', raw)
        checkpoint(path, result)
    result['reference_valid'] = all(f['independent_reference']['passed']
        for mesh in result['meshes'].values() for f in mesh['families'].values())
    result['passed'] = (result['reference_valid'] and inherited_fixtures['passed'] and
                       all(f['eligible']['passed'] for f in result['meshes']['512']['families'].values()))
    result['disposition'] = ('DECLARED_READOUT_PREREQUISITE_PASSED' if result['passed'] else
        'SOURCE_OR_REFERENCE_UNRESOLVED' if not result['reference_valid'] or not inherited_fixtures['passed']
        else 'FIXED_READOUT_PREREQUISITE_FAILS')
    checkpoint(path, result)
    return result


def screen(folder, historical, plan):
    """Retain structured failed prerequisites and missing support, including early failures."""
    path = Path(folder)/(ATTEMPTS[0]+'.json')
    initial = dict(task=TASK, attempt=ATTEMPTS[0], passed=False,
        disposition='READOUT_ASSESSMENT_INCOMPLETE', production_attempted=False,
        physical_validation='NOT_ESTABLISHED', plan_sha256=obs.sha(DOCS/'PLAN.json'), meshes={})
    write_new(path, initial)
    try:
        return _screen_assess(folder, historical, plan)
    except Exception as exc:
        result = obs.read_json(path)
        result.update(passed=False, disposition='SOURCE_OR_REFERENCE_UNRESOLVED',
                      failure=dict(type=type(exc).__name__, reason=str(exc)))
        for cells in (128,256,512):
            result['meshes'].setdefault(str(cells), dict(families={name:dict(requested=139,
                included=0, excluded=0, unavailable=139, eligible_requested=84, younger_requested=55,
                passed=False, reason='assessment did not complete') for name in ('zero_boundary','nonconstant')}))
        if isinstance(exc, MemoryError):
            result.update(conclusion='D', disposition='FIXED_RESOURCE_MEMORY_EXHAUSTED')
        checkpoint(path,result)
        raise


def require_screen(folder, plan, accounting):
    end = accounting['ends'].get(ATTEMPTS[0], {})
    path = Path(folder)/(ATTEMPTS[0]+'.json')
    require(end.get('exit_code') == 0 and path.is_file(), 'readout invocation did not complete')
    require(end.get('artifact_sha256') == obs.sha(path), 'readout evidence identity mismatch')
    screen_result = obs.read_json(path)
    require(screen_result.get('passed') is True and screen_result.get('task') == TASK,
            'readout prerequisite did not pass; production forbidden')
    require(screen_result['plan_sha256'] == obs.sha(DOCS/'PLAN.json'), 'readout plan differs')
    require(plan['production_feasibility']['established'], 'production feasibility unresolved')


def capture(path, plan):
    """One original public request to unchanged production; 005 schema is storage only."""
    from puckworks.models.grudeva2026 import reduced
    from puckworks import rights
    require(rights.may_execute_locally('grudeva2026.reduced').allowed, 'local execution rights unavailable')
    path = Path(path)
    require(not path.exists(), 'immutable attempt output exists')
    request = obs.requests()
    ctrl = candidate_controls(plan['candidate'])
    size = 2+ctrl.cells*(ctrl.modes+2)
    base = dict(schema=obs.SCHEMA, storage_semantics='unchanged 005 format only; execution authority is 006',
        task=TASK, row=ROW, attempt=ATTEMPTS[1], status='EXECUTED_UNQUALIFIED', observed=True,
        controls=asdict(ctrl), parameters=asdict(reduced.Parameters()), requests=request,
        request_hashes={k:obs.digest(v) for k,v in request.items()}, sources=obs.sources(),
        adapter_sources=plan['adapter_sources'], environment=obs.environment(),
        matrix_sha256=obs.sha(DOCS/'PLAN.json'), physical_validation='NOT_ESTABLISHED', segments=[],
        state_layout={'size':size, 'modal_shape':[ctrl.modes+1,ctrl.cells], 'modal_axis':0,
                      'order':'s,liquid,mode-major,cup'})
    original = reduced.solve_ivp
    captured = []
    def persist():
        for i, segment in enumerate(captured):
            try:
                if segment['solution'] is not None:
                    base.setdefault('geometry', obs._production_geometry(segment))
                saved = obs.save_segment(path.parent, f'{path.stem}-segment-{i}.npz', segment, size,
                                         attempt=ATTEMPTS[1], segment_index=i)
            except Exception as exc:
                saved = getattr(exc, 'metadata', {'unavailable_reason':type(exc).__name__+': '+str(exc)})
            base['segments'].append(saved)
            checkpoint(path, base)
    stage_start = time.perf_counter()
    try:
        with obs.capture_returns(reduced) as captured:
            result = reduced.simulate(controls=ctrl, times=request['public_times'], profile_z=request['public_z'])
    except BaseException as exc:
        try:
            base.update(original_exception={'type':type(exc).__name__, 'message':str(exc)},
                restored=reduced.solve_ivp is original, solve_invocations=len(captured),
                returned=sum(s['solution'] is not None for s in captured))
            write_new(path, base)
            persist()
        except Exception:
            pass
        raise
    base['phase_seconds'] = {'production_call':time.perf_counter()-stage_start}
    stage_start = time.perf_counter()
    public_bytes = result.canonical_json()
    base.update(public_result=json.loads(public_bytes), public_result_sha256=obs.digest(json.loads(public_bytes)),
                restored=reduced.solve_ivp is original, solve_invocations=len(captured),
                returned=sum(s['solution'] is not None for s in captured),
                return_identity='same retained object returned by unchanged capture_returns seam')
    public = path.with_name(path.stem+'-public-result.json')
    # Retain the complete Result before anything diagnostic can fail.
    try:
        write_new(public, base['public_result'])
        base['public_checkpoint'] = dict(file=public.name, sha256=obs.sha(public))
    except Exception as exc:
        base['public_checkpoint_failure'] = dict(type=type(exc).__name__, message=str(exc))
        write_new(path, base)
        raise
    write_new(path, base)
    base['phase_seconds']['public_checkpoint'] = time.perf_counter()-stage_start
    stage_start = time.perf_counter()
    persist()
    base['phase_seconds']['segment_persistence_fidelity_replay'] = time.perf_counter()-stage_start
    base['public_result_unchanged_after_capture'] = result.canonical_json() == public_bytes
    base['retained_numerical_bytes'] = sum(s.get('numerical_bytes', 0) for s in base['segments'])
    checkpoint(path, base)
    # All live fidelity/replay checks have finished; release solver-owned dense arrays
    # before the offline observer allocates its complete diagnostic panel.
    captured.clear()
    errors = inherited.check_run(base, CANDIDATE, obs.sha(DOCS/'PLAN.json'))
    if any(s.get('failure', {}).get('exception_type') == 'MemoryError' for s in base['segments']):
        raise MemoryError('segment persistence exhausted fixed address space')
    require(not errors, '; '.join(errors))
    stage_start = time.perf_counter()
    observed = obs.observe_saved(path)
    write_new(path.with_name(path.stem+'-observations.json'), observed)
    base['phase_seconds']['observation_audits_persistence'] = time.perf_counter()-stage_start
    checkpoint(path, base)
    return base
