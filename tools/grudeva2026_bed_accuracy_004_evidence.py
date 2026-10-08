"""Offline evidence assembly: unchanged frozen gates plus identities and 003 comparison.

Never executes trajectories. The frozen reporter decides all matrix gates.
This writer adds public-safe attempt accounting, lineage, family C oracle
verification and matched-control comparisons; differences from 003 never
establish accuracy by themselves.
"""
import argparse
import inspect
import json
from pathlib import Path

from puckworks.analysis import grudeva2026_bed_accuracy_004_report as report
from puckworks.analysis import grudeva2026_conservative_003 as old


def counts(comparison):
    for row in comparison.values():
        if isinstance(row, dict) and 'included' in row:
            row['requested'] = row['included']+row['excluded']+row['unavailable']
    return comparison


def assemble(folder, matrix, baseline):
    result = report.reduce_saved(folder, matrix)
    root = Path(old.__file__).parents[2]
    historical = report.read(root/'docs/analysis/model_grudeva2026_conservative_003/RESULTS.json')
    archived = {}
    bindings = {}
    for name in ('normal', 'bed_fine'):
        path = baseline/(name+'-compat-final.json')
        expected = historical['runs'][name]['artifact_sha256']
        if report.sha(path) != expected:
            raise ValueError('historical artifact mismatch: '+name)
        archived[name] = report.read(path)
        if archived[name]['source_sha256'] != report.sha(old.__file__):
            raise ValueError('historical execution source mismatch')
        if archived[name]['radial_source_sha256'] != report.sha(Path(old.__file__).with_name('grudeva2026_reference_002.py')):
            raise ValueError('historical radial source mismatch')
        if archived[name]['controls'] != report.controls(name):
            raise ValueError('historical controls mismatch')
        bindings[name] = {'artifact_sha256': expected, 'source_sha256': archived[name]['source_sha256'],
                          'controls': archived[name]['controls'], 'seconds': archived[name]['seconds']}
    old_difference = counts(report.refinement(archived['normal'], archived['bed_fine']))
    changes = {}
    for name in archived:
        changes[name] = counts(report.refinement(archived[name], report.read(folder/(name+'-final.json'))))
    ratios = {name: row['max_absolute']/result['refinements']['bed_fine'][name]['max_absolute']
              if result['refinements']['bed_fine'][name]['max_absolute'] else None
              for name, row in old_difference.items() if isinstance(row, dict) and 'max_absolute' in row}
    result['unchanged_003_comparison'] = dict(bindings=bindings, bed_refinement=old_difference,
        output_changes=changes, bed_error_reduction_factors=ratios,
        interpretation='Same controls and inherited masks; no equal-cost superiority claim; no production comparison.')
    _, starts, ends = report.resource_audit(folder)
    attempts = []
    for name, start in starts.items():
        end = ends[name]
        safe = lambda value: str(value).replace(str(folder), '$EVIDENCE').replace(str(root), '$REPOSITORY')
        attempts.append(dict(name=name, kind=start['kind'], phase=start['phase'],
            start_utc=start['utc'], end_utc=end['utc'], seconds=end['seconds'], exit_code=end['exit_code'],
            time_ceiling=start['time_ceiling'], memory_bytes=start['memory_bytes'],
            peak_rss_bytes=end.get('peak_rss_bytes'), log_sha256=end['log_sha256'],
            artifact_sha256=end.get('artifact_sha256'), source_hashes=start['source_hashes'],
            command=[safe(arg) for arg in start['command']]))
    result['attempts'] = attempts
    result['raw_ledger_sha256'] = report.sha(folder/'invocations.jsonl')
    result['diagnostic_artifacts'] = {name: report.sha(folder/name) for name in (
        'diagnostics.json', 'diagnosis-front.json', 'diagnostics-corrected.json',
        'diagnostics-final.json', 'diagnosis-front-corrected.json', 'diagnostics-bound.json',
        'pilot64-root.json', 'pilot512-root.json', 'pilot-final.json',
        'pilot-crossing-fixed.json', 'local-final.json', 'local-bound.json', 'minimum-receipt.json')}
    snapshots = {start['source_hashes'].get('puckworks/analysis/grudeva2026_bed_accuracy_004.py')
                 for start in starts.values()} - {None}
    for digest in snapshots:
        if report.sha(folder/'scientific-snapshots'/(digest+'.py')) != digest:
            raise ValueError('development source snapshot missing')
    result['retained_004_scientific_snapshots'] = sorted(snapshots)
    result['environment'] = report.read(folder/'environment.json')
    result['environment_sha256'] = report.sha(folder/'environment.json')
    result['intake_preservation_sha256'] = report.sha(folder/'preservation.json')
    for path, digest in report.read(folder/'preservation.json').items():
        if report.sha(root/path) != digest:
            raise ValueError('historical preservation mismatch: '+path)
    result['historical_preservation_passed'] = True
    result['supplementary_family_C'] = report.read(folder/'history-oracle.json')
    result['supplementary_family_C_sha256'] = report.sha(folder/'history-oracle.json')
    result['supplementary_family_C_source_sha256'] = report.sha(root/'tools/grudeva2026_bed_accuracy_004_history_oracle.py')
    family_c = result['supplementary_family_C']
    if (family_c['source_sha256'] != result['supplementary_family_C_source_sha256']
            or family_c['core_sha256'] != report.sha(root/'puckworks/analysis/grudeva2026_bed_accuracy_004.py')
            or ends['history-oracle']['artifact_sha256'] != result['supplementary_family_C_sha256']):
        raise ValueError('Supplementary family C execution/source binding mismatch')
    if not result['supplementary_family_C']['oracle_passed']:
        result.update(qualified=False, disposition=report.INCOMPLETE,
                      blocker='Supplementary family C oracle did not meet its predeclared uncertainty criterion.')
    result['primary_sources'] = dict(article_sha256='592304014b7be482b5fe2814d730f7d128f9ec2e77d6f7d25f8e0292c5fce5e5',
        article_pdf_pages=[16,17,18], supplement_sha256='5437e3310288c2a9506fbd1eb4c4d8854ec8f4293f6edcda5579bbdc9bae5179',
        supplement_pdf_pages=[13,14,15], matches_003=True)
    import hashlib
    result['observation_support_generator_sha256'] = hashlib.sha256(inspect.getsource(old.observation_support).encode()).hexdigest()
    result['degrees_of_freedom'] = {name: dict(liquid=c['bed'], grain=c['bed']*c['shells'],
        fixed_histories=7*c['shells'], total_evolved=c['bed']+(c['bed']+7)*c['shells'],
        dense_radial_transform_entries=c['shells']**2, extra_cohorts=0)
        for name in report.ROWS for c in [report.controls(name)]}
    result['evidence_writer_sha256'] = report.sha(__file__)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--runs-directory', type=Path, required=True)
    parser.add_argument('--matrix', type=Path, required=True)
    parser.add_argument('--baseline-directory', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    try:
        result = assemble(args.runs_directory.resolve(), args.matrix, args.baseline_directory)
    except (ValueError, KeyError, TypeError, IndexError, OSError, OverflowError) as exc:
        result = dict(disposition=report.INCOMPLETE, qualified=False, blocker=str(exc),
                      physical_validation='NOT_ESTABLISHED')
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True, allow_nan=False)+'\n')
    print(json.dumps({key: result[key] for key in ('disposition', 'qualified')}))
    return 0 if result['qualified'] else 2


if __name__ == '__main__':
    raise SystemExit(main())
