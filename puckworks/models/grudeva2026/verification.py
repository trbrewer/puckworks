"""One authoritative gate/budget definition; no saved-PASS consumption."""
from __future__ import annotations

from importlib.resources import files
import json
import numpy as np

from .kernel import spherical_history
from .reduced import Controls, Parameters, Result, front_speed, simulate

BUDGETS = {"front_relative": 1e-12, "kernel_flux_absolute": 2e-4,
           "kernel_mean_absolute": 2e-5, "conservation_normalized": 1e-6,
           "outlet_refinement_absolute": 1e-3, "event_refinement_absolute": 1e-3,
           "figure3_concentration_absolute": .015, "figure3_front_absolute": .008,
           "figure4_concentration_absolute": .015, "figure4_event_absolute": .025,
           "jump_time_exclusion": .025}


def reference_fixture(name: str) -> dict:
    if name not in ("analytic_reference.json", "publication_reference.json"):
        raise ValueError("unknown Grudeva reference fixture")
    return json.loads(files("puckworks.data").joinpath("grudeva2026", name).read_text())


def quick_verification() -> dict:
    """Run independent analytical fixtures and a bounded real coupled case."""
    fixture = reference_fixture("analytic_reference.json")
    p = Parameters()
    front_errors = [abs(front_speed(row['c_front'], p)/row['speed']-1)
                    for row in fixture['constant_front']]
    case = fixture['sphere']
    r = spherical_history(case['times'], case['boundary'], case['initial'],
                          diffusivity=case['diffusivity'], q_b=case['q_b'])
    flux_error = max(abs(x-y) for x,y in zip(r['flux'][1:], case['flux'][1:]))
    mean_error = max(abs(x-y) for x,y in zip(r['mean'], case['mean']))
    coupled = simulate(controls=Controls(cells=64, modes=16), times=[0,.1,.4], profile_z=[0,.5,1])
    metrics = {'front_max_relative_error': max(front_errors), 'flux_max_absolute_error': flux_error,
               'grain_mean_max_absolute_error': mean_error,
               'coupled_status': coupled.status,
               'coupled_conservation': coupled.diagnostics.get('max_normalized_conservation_residual')}
    passed = (max(front_errors) <= BUDGETS['front_relative'] and
              flux_error <= BUDGETS['kernel_flux_absolute'] and
              mean_error <= BUDGETS['kernel_mean_absolute'] and coupled.status == 'COMPLETED')
    return {'passed': bool(passed), 'evidence_strength': 'code_verification',
            'metrics': metrics, 'publication_reproduction': 'NOT_EARNED_BY_THIS_QUICK_GATE',
            'physical_validation': 'NOT_ESTABLISHED'}


def publication_comparison(result: Result) -> dict:
    """Qualified raster samples only, with jump/event uncertainty kept separate."""
    f = reference_fixture('publication_reference.json')
    if result.status != 'COMPLETED':
        return {'figure3': {'status': 'UNAVAILABLE'}, 'figure4': {'status': 'UNAVAILABLE'},
                'figure5': f['figure5'], 'reason': 'Numerical solution did not qualify'}
    times = np.array(result.time)
    event = result.events['desaturation_exit']
    rows3, rows4, fronts = [], [], []
    for row in f['figure3']:
        hits = np.flatnonzero(np.isclose(times, row['t'], rtol=0, atol=1e-12))
        if not len(hits):
            raise ValueError('reference comparison requires all four exact Figure 3 times')
        i = hits[0]
        # Avoid the moving jump on both reference and computed sides. Report support explicitly.
        reference_front = next((v['z'] for v in f['figure3_fronts'] if v['t'] == row['t']), 1.)
        # The interval BETWEEN displaced jumps is event mismatch, not smooth-curve error.
        if min(reference_front, result.s_d[i])-.008 <= row['z'] <= max(reference_front, result.s_d[i])+.008:
            continue
        predicted = float(np.interp(row['z'], result.profile_z, result.liquid_profiles[i]))
        rows3.append({**row, 'computed': predicted, 'absolute_error': abs(predicted-row['c'])})
    for row in f['figure3_fronts']:
        i = int(np.flatnonzero(np.isclose(times, row['t'], rtol=0, atol=1e-12))[0])
        predicted = result.s_d[i]
        fronts.append({**row, 'computed': predicted, 'absolute_error': abs(predicted-row['z'])})
    for row in f['figure4']:
        if event is None or (min(event, f['figure4_event']['t'])-BUDGETS['jump_time_exclusion'] <= row['t'] <=
                             max(event, f['figure4_event']['t'])+BUDGETS['jump_time_exclusion']):
            continue
        hits = np.flatnonzero(np.isclose(times, row['t'], rtol=0, atol=1e-12))
        if not len(hits):
            raise ValueError('reference comparison requires exact Figure 4 sample times')
        predicted = result.outlet_concentration[int(hits[0])]
        rows4.append({**row, 'computed': predicted, 'absolute_error': abs(predicted-row['c'])})
    error3 = max(r['absolute_error'] for r in rows3)
    front_error = max(r['absolute_error'] for r in fronts)
    error4 = max(r['absolute_error'] for r in rows4)
    event_error = None if event is None else abs(event-f['figure4_event']['t'])
    return {'figure3': {'status': 'PASS' if error3<=BUDGETS['figure3_concentration_absolute'] and
                       front_error<=BUDGETS['figure3_front_absolute'] else 'FAIL',
                       'concentration_max_absolute_error': error3, 'front_max_absolute_error': front_error,
                       'samples': rows3, 'fronts': fronts},
            'figure4': {'status': 'PASS' if error4<=BUDGETS['figure4_concentration_absolute'] and
                       event_error is not None and event_error<=BUDGETS['figure4_event_absolute'] else 'FAIL',
                       'concentration_max_absolute_error': error4, 'event_absolute_error': event_error,
                       'reference_event': f['figure4_event'], 'samples': rows4},
            'figure5': f['figure5'], 'reference_strength': 'qualified selected raster samples; not author arrays',
            'physical_validation': 'NOT_ESTABLISHED'}


def reference_times() -> list[float]:
    f = reference_fixture('publication_reference.json')
    return sorted(set([0., .4, 1., 3.2, 4.8, 6.4, 8.]+list(np.linspace(6.51,7.1,60))+
                      [row['t'] for row in f['figure4']]))
