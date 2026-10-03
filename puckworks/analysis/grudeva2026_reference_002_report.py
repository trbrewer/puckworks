"""Offline reduction of saved REFERENCE-002 runs; never executes a solver.

Baseline reuse/scoring is separate from the permissioned alternative numerical
core. No failed alternative is supplied to the publication scorer.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def audit_run(path):
    r = json.loads(path.read_text())
    data = np.array(r['records'])
    audit = []
    if 'boulder_mean_profiles' in r:
        z = np.array(r['physical_grain_z'])
        eta = np.array(r['eta'])
        for row, liquid, boulder in zip(data, r['liquid_profiles'], r['boulder_mean_profiles']):
            t, s = row[:2]
            boulder = np.array(boulder)
            active = z < s
            front_b = boulder[-1] if r['arrival'] is not None and t >= r['arrival'] else 1.388
            ib = np.trapezoid(np.r_[boulder[active], front_b], np.r_[z[active], s])
            ic = s*np.trapezoid(liquid, eta)
            phases = [ic+min(t, 1)-s, 3.2*(ic+1.388*(1-s)), .8*(ib+1.388*(1-s))]
            audit.append(phases)
    exceeds = np.flatnonzero(abs(data[:, 8]) > 1e-6)
    at = int(exceeds[0]) if len(exceeds) else None
    def snapshot(i):
        row = data[i]
        return {'time': float(row[0]), 'front': float(row[1]),
                'liquid': float(row[5]), 'fines': float(row[6]), 'boulders': float(row[7]),
                'bed': float(sum(row[5:8])), 'cup': float(row[3]),
                'normalized_residual': float(row[8]),
                'mapped_source_minus_boulder_loss': float(row[9]-(.8*1.388-row[7]))}
    indices = sorted(set([0, len(data)-1]+[int(np.argmin(abs(data[:, 0]-t)))
                                        for t in (.01, .4, 1., 3.2, 4.8, 6.4)]))
    return {'controls': r['controls'], 'raw_sha256': sha(path), 'core_sha256': r['source_sha256'],
            'status': r['status'], 'reason': r['reason'], 'arrival': r['arrival'],
            'last_observed_time': float(data[-1, 0]),
            'horizon_observation_available': bool(data[-1, 0] == r['controls']['horizon']),
            'max_normalized_conservation_residual': r['max_normalized_conservation_residual'],
            'conservation_passed': r['max_normalized_conservation_residual'] <= 1e-6,
            'phase_observer_recomputed_max_error': float(np.max(abs(np.array(audit)-data[:, 5:8]))) if audit else None,
            'observation_quadrature': 'Exact integral of piecewise-linear nodal representation; continuum error UNQUALIFIED',
            'cup_quadrature_difference': r['cup_quadrature_difference'],
            'grain_transfer_balance_max': r['grain_transfer_balance_max'],
            'grain_integrated_loss_check': r['grain_integrated_loss_check'],
            'first_sample_exceeding_conservation_budget': None if at is None else snapshot(at),
            'ledger_samples': [snapshot(i) for i in indices],
            'seconds': r['seconds'], 'max_rss_kib': r['max_rss_kib']}


def refinement(a, b):
    x, y = np.array(a['records']), np.array(b['records'])
    # Both datasets explicitly contain the same prescribed observations and
    # potentially different localized event rows. Interpolate only continuous
    # fields or outlet samples strictly outside the whole displaced jump interval.
    if a['arrival'] is None or b['arrival'] is None:
        return {'passed': False, 'reason': 'arrival unavailable'}
    lo, hi = sorted([a['arrival'], b['arrival']])
    available = (x[:, 0] >= y[0, 0]) & (x[:, 0] <= y[-1, 0])
    outside_jump = (x[:, 0] < lo-.025) | (x[:, 0] > hi+.025)
    smooth = available & outside_jump
    if not np.any(smooth):
        return {'passed': False, 'reason': 'no common smooth observation support',
                'included_outlet': 0, 'excluded_outlet': int(sum(available & ~outside_jump)),
                'unavailable_outlet': int(sum(~available))}
    outlet = abs(x[:, 2]-np.interp(x[:, 0], y[:, 0], y[:, 2]))[smooth]
    front = abs(x[:, 1]-np.interp(x[:, 0], y[:, 0], y[:, 1]))[available]
    inv = max(float(np.max(abs(x[:, k]-np.interp(x[:, 0], y[:, 0], y[:, k]))[available]))
              for k in range(3, 8))
    event = abs(a['arrival']-b['arrival'])
    return {'outlet_max_absolute': float(max(outlet)), 'arrival_absolute': event,
            'front_max_absolute': float(max(front)), 'phase_or_cup_max_absolute_diagnostic': inv,
            'included_outlet': int(sum(smooth)), 'excluded_outlet': int(sum(available & ~outside_jump)),
            'unavailable_outlet': int(sum(~available)),
            'passed': bool(max(outlet) <= .001 and event <= .001),
            'scope': 'outlet/event refinement gate only; no global or local accuracy inference'}


def reuse_baseline(root, baseline_dir):
    from puckworks.models.grudeva2026.reduced import Result
    from puckworks.models.grudeva2026.verification import publication_comparison
    folder = root/'docs/analysis/model_grudeva2026_reduced_001'
    old = json.loads((folder/'RESULTS.json').read_text())
    reuse = json.loads((folder/'REMEDIATION_REUSE.json').read_text())
    bindings = {name: sha(root/name) == item['current_sha256']
                for name, item in reuse['source_bindings'].items()}
    if not all(bindings.values()) or sha(folder/'RESULTS.json') != reuse['historical_report_sha256']:
        raise ValueError('baseline source or historical report identity changed')
    raw_hashes, phase_residuals = {}, {}
    normal = None
    for name, expected in reuse['historical_result_sha256'].items():
        r = json.loads((baseline_dir/(name+'.json')).read_text())['scientific_result']
        digest = hashlib.sha256(json.dumps(r, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()).hexdigest()
        if digest != expected:
            raise ValueError('baseline raw identity mismatch: '+name)
        raw_hashes[name] = digest
        inv = r['inventories']
        mass = sum(np.array(inv[k]) for k in ['external_liquid', 'fines', 'boulders_including_pores'])
        residual = (mass+np.array(r['cumulative_discharged_solute'])-inv['initial'])/inv['initial']
        phase_residuals[name] = float(max(abs(residual)))
        if name == 'normal':
            normal = Result(**r)
    publication = publication_comparison(normal)
    fixture = json.loads((root/'puckworks/data/grudeva2026/publication_reference.json').read_text())
    counts = {f: {'included': len(publication[f]['samples']),
                  'excluded': len(fixture[f])-len(publication[f]['samples']), 'unavailable': 0}
              for f in ['figure3', 'figure4']}
    return {'source_bindings_verified': bindings, 'original_report_sha256': sha(folder/'RESULTS.json'),
            'original_raw_hashes_verified': raw_hashes, 'refinement': old['refinement'],
            'original_events': old['runs']['normal']['events'],
            'phase_inventory_arithmetic_residuals': phase_residuals,
            'audit_limit': 'Archived phase inventories checked; raw cell states were not archived. No new independent cell-volume audit or instrumentation was executed.',
            'publication_replay': publication, 'publication_counts': counts,
            'evidence_class': 'HASH_VERIFIED_UNCHANGED_308_EVIDENCE_REUSE_NOT_NEW_BACKEND_QUALIFICATION'}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--runs-directory', type=Path, required=True)
    ap.add_argument('--baseline-directory', type=Path, required=True)
    ap.add_argument('--attempt-manifest', type=Path, help='optional retained execution ledger')
    ap.add_argument('--output', type=Path, required=True)
    args = ap.parse_args(argv)
    root = Path(__file__).resolve().parents[2]
    names = ['normal', 'bed_fine', 'radial_fine', 'time_fine', 'combined']
    audits = {n: audit_run(args.runs_directory/(n+'.json')) for n in names}
    raw = {n: json.loads((args.runs_directory/(n+'.json')).read_text()) for n in names}
    controls = {'normal': (128, 64, .001), 'bed_fine': (256, 64, .001),
                'radial_fine': (128, 128, .001), 'time_fine': (128, 64, .0005),
                'combined': (512, 128, .0005)}
    for name, (bed, shells, dt) in controls.items():
        expected = dict(bed=bed, shells=shells, dt=dt, horizon=8., diffusivity=1.)
        if raw[name]['controls'] != expected:
            raise ValueError('canonical qualification controls differ: '+name)
    refined = {n: refinement(raw['normal'], raw[n]) for n in names[1:]}
    limit = json.loads((args.runs_directory/'limit.json').read_text())
    d = np.array(limit['records'])
    limit_errors = {'front_relative': abs(limit['arrival']/5.4416-1),
                    'conservation': limit['max_normalized_conservation_residual'],
                    'liquid_max': float(np.max(np.abs(limit['liquid_profiles']))),
                    'grain_max_error': float(np.max(abs(np.array(limit['terminal_grain_means'])-1.388))),
                    'passed': bool(abs(limit['arrival']/5.4416-1) <= 1e-12 and
                                   limit['max_normalized_conservation_residual'] <= 1e-6 and
                                   max(abs(d[-1, 3]-(5.4416-1)), abs(d[-1, 7]-.8*1.388)) < 1e-12)}
    analytic = json.loads((args.runs_directory/'analytic.json').read_text())
    qualifies = (analytic['passed'] and limit_errors['passed'] and
                 all(x['passed'] for x in refined.values()) and
                 all(x['conservation_passed'] and x['horizon_observation_available'] and
                     x['status'] == 'EXECUTED_UNQUALIFIED' for x in audits.values()))
    report = {'task': 'MODEL-GRUDEVA2026-REFERENCE-002', 'governance': 'G2',
              'change_declaration': 'NUMERICAL_METHOD_CHANGE',
              'disposition': 'COMPARATOR_QUALIFICATION_INCOMPLETE' if not qualifies else 'REQUIRES_FULL_STATE_COMPARISON',
              'specified_equation_contract': 'DEFINED_AND_SOURCE_AUDITED',
              'analytical_radial_qualification': analytic, 'coupled_limit': limit_errors,
              'runs': audits, 'refinement': refined, 'comparator_qualified': bool(qualifies),
              'backend_to_backend': {'status': 'UNAVAILABLE', 'reason': 'Alternate coupled numerical qualification failed; no main comparison or oracle claim'},
              'earliest_interbackend_divergence': 'NOT_ADJUDICATED_UNQUALIFIED_COMPARATOR',
              'baseline': reuse_baseline(root, args.baseline_directory),
              'figure5': 'FIG5_REFERENCE_INCOMPLETE', 'physical_validation': 'NOT_ESTABLISHED',
              'scientific_coupled_attempts': None, 'automatic_successor': 'NONE',
              'numerical_requalification_after_final_scheduler_fix': 'NOT_EXECUTED_CAP_EXHAUSTED',
              'current_core_sha256': sha(root/'puckworks/analysis/grudeva2026_reference_002.py'),
              'source_hashes': {str(p.relative_to(root)): sha(p) for p in [
                  Path(__file__), root/'puckworks/analysis/grudeva2026_reference_002.py',
                  root/'docs/analysis/model_grudeva2026_reference_002/CONTRACT.md',
                  root/'tests/test_grudeva2026_reference_002.py']}}
    if args.attempt_manifest:
        attempts = json.loads(args.attempt_manifest.read_text())
        report['attempts'] = attempts
        report['scientific_coupled_attempts'] = len(attempts)
        report['resource_use'] = {
            'successful_coupled_seconds': sum(r['seconds'] or 0 for r in attempts),
            'peak_rss_kib': max(r.get('rss_kib', 0) for r in attempts),
            'failed_attempt_seconds': 'NOT_INDIVIDUALLY_RECORDED',
            'wall_time_limit': 3600, 'per_run_limit': 900, 'memory_limit_bytes': 2*1024**3,
            'coupled_count': len(attempts), 'failed_coupled_count': sum(r['status'] == 'FAILED' for r in attempts)}
    report['source_audit'] = {
        'article_inspected_sha256': '592304014b7be482b5fe2814d730f7d128f9ec2e77d6f7d25f8e0292c5fce5e5',
        'supplement_inspected_sha256': '5437e3310288c2a9506fbd1eb4c4d8854ec8f4293f6edcda5579bbdc9bae5179',
        'supplement_sections_read': 'E.2, E26-E33, pages 13-15',
        'figure3_figure4_reextracted_coordinates_equal': True,
        'pdf_container_difference': 'Inspected local PDF has different bytes from original fixture PDF; embedded figure hashes and every extracted coordinate/uncertainty agree',
        'fixture_changes': 'NONE', 'source_setting_alternatives': 0}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, sort_keys=True, indent=2, allow_nan=False)+'\n')
    print(report['disposition'])
    return 2 if not qualifies else 0


if __name__ == '__main__':
    raise SystemExit(main())
