"""Deterministic native reference and optional refinement CLI (outside quick CI)."""
from __future__ import annotations

import argparse
from dataclasses import replace
import hashlib
from importlib.resources import files
import json
from pathlib import Path
import time

import numpy as np

from .reduced import Controls, Parameters
from .verification import BUDGETS


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output', type=Path, required=True, help='compact JSON report destination')
    ap.add_argument('--refine', action='store_true', help='independent space/time/modal checks plus pore refill')
    ap.add_argument('--raw-directory', type=Path, help='optional external full-precision run archive')
    args = ap.parse_args(argv)
    from puckworks.product.lab_reference_producers import grudeva2026_reference_summary
    controls = Controls()
    cases = {'normal': (Parameters(), controls)}
    if args.refine:
        cases.update({'space_coarse': (Parameters(), replace(controls, cells=controls.cells//2)),
                      'space_fine': (Parameters(), replace(controls, cells=controls.cells*2)),
                      'time_fine': (Parameters(), replace(controls, rtol=controls.rtol/10,
                                                         atol=controls.atol/10, max_step=controls.max_step/2)),
                      'modes_fine': (Parameters(), replace(controls, modes=controls.modes*2)),
                      'pore_refill': (Parameters(varphi_lb=.25, source_id='SYNTHETIC_PORE_REFILL'), controls)})
    summaries, runs, durations = {}, {}, {}
    for name, (p, c) in cases.items():
        start = time.perf_counter()
        summary = grudeva2026_reference_summary(parameters=p, controls=c)
        durations[name] = time.perf_counter()-start
        result = summary['scientific_result']
        runs[name] = result
        summaries[name] = {'parameters': result['parameters'], 'controls': result['controls'],
                           'status': result['status'], 'events': {key: value for key,value in result['events'].items()
                                                               if not key.endswith('_profile_z')},
                           'diagnostics': result['diagnostics'],
                           'final_inventory': {key: value[-1] if isinstance(value,list) else value
                                               for key,value in result['inventories'].items()},
                           'result_sha256': hashlib.sha256(json.dumps(result,sort_keys=True,separators=(',',':'),
                                                                       allow_nan=False).encode()).hexdigest()}
        if args.raw_directory:
            args.raw_directory.mkdir(parents=True, exist_ok=True)
            (args.raw_directory/f'{name}.json').write_text(json.dumps(summary,sort_keys=True,indent=2,allow_nan=False)+'\n')
        if name == 'normal':
            reference, quick = summary['reference_qualification'], summary['gate_verdict']
    comparisons = {}
    base = runs['normal']
    for name in ('space_fine','time_fine','modes_fine'):
        if name not in runs:
            continue
        other = runs[name]
        if base['status'] != 'COMPLETED' or other['status'] != 'COMPLETED':
            comparisons[name] = {'passed': False, 'reason': 'Numerical run failed'}
            continue
        t=np.asarray(base['time'])
        events=[base['events']['desaturation_exit'],other['events']['desaturation_exit']]
        mask=np.ones(t.size,dtype=bool)
        for event in events:
            if event is not None:
                mask &= abs(t-event)>BUDGETS['jump_time_exclusion']
        error=float(np.max(np.abs(np.asarray(base['outlet_concentration'])-
                                  other['outlet_concentration'])[mask]))
        dt=None if None in events else abs(events[0]-events[1])
        comparisons[name]={'max_outlet_change':error,'event_change':dt,
                           'passed':error<=BUDGETS['outlet_refinement_absolute'] and dt is not None and
                           dt<=BUDGETS['event_refinement_absolute']}
    numeric = quick['passed'] and all(r['status']=='COMPLETED' for r in runs.values())
    refined = args.refine and all(row['passed'] for row in comparisons.values())
    all_refs = all(reference[key]['status']=='PASS' for key in ('figure3','figure4','figure5'))
    disposition = ('GRUDEVA2026_REDUCED_SOLVER_VERIFIED_AGAINST_PUBLISHED_ASYMPTOTIC_REFERENCE'
                   if numeric and refined and all_refs else
                   'GRUDEVA2026_STANDALONE_NUMERICALLY_VERIFIED_REFERENCE_INCOMPLETE'
                   if numeric and refined else 'NUMERICAL_VERIFICATION_FAILED' if args.refine else
                   'SINGLE_RUN_COMPLETE_REFINEMENT_NOT_ASSESSED')
    module_dir=Path(__file__).parent
    hashes={f'puckworks/models/grudeva2026/{p.name}':hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(module_dir.glob('*.py'))}
    for name in ('analytic_reference.json','publication_reference.json'):
        hashes[f'puckworks/data/grudeva2026/{name}']=hashlib.sha256(files('puckworks.data').joinpath('grudeva2026',name).read_bytes()).hexdigest()
    report={'task':'MODEL-GRUDEVA2026-REDUCED-001','governance':'G2',
            'change_declaration':'NUMERICAL_METHOD_CHANGE','disposition':disposition,
            'physical_validation':'NOT_ESTABLISHED','quick_verification':quick,'budgets':BUDGETS,
            'runs':summaries,'refinement':comparisons,'publication_references':reference,
            'runtime_seconds_not_scientific_hash_inputs':durations,'source_hashes':hashes,
            'limits':['No experimental validation or common-scenario adapter',
                      'Figure 5 reference arrays/settings/grid unavailable',
                      'Figures 3/4 mismatches remain failures at unchanged published parameters/budgets']}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(report,sort_keys=True,indent=2,allow_nan=False)+'\n')
    print(disposition)
    return 0 if numeric and (not args.refine or refined) else 1


if __name__=='__main__':
    raise SystemExit(main())
