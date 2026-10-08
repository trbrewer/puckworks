"""Explicit bounded local verification, separate from saved-result reporting."""
import argparse
import json
from pathlib import Path
from puckworks.analysis.grudeva2026_conservative_003_report import local_qualification
from puckworks.analysis.grudeva2026_bed_accuracy_004_report import read,sha,scientific_sources


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--diagnostics',type=Path,required=True)
    parser.add_argument('--minimum-receipt',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args(argv)
    diag=read(args.diagnostics);minimum=read(args.minimum_receipt)
    sources=scientific_sources()
    if diag['source_sha256']!=sources['puckworks/analysis/grudeva2026_bed_accuracy_004.py']:
        raise ValueError('diagnostic source mismatch')
    if minimum['scientific_sources']!=sources or not minimum['passed']:
        raise ValueError('minimum-dependency source/check mismatch')
    if not minimum['numpy'].startswith('2.0.') or not minimum['scipy'].startswith('1.13.'):
        raise ValueError('minimum dependencies not exercised')
    a=diag['A']
    checks={name:a[1][name]/a[2][name]>=3 for name in ('average','face','point')}
    checks['time_control']=all(abs(a[2][name]-a[3][name])<.1*a[2][name] for name in ('average','face','point'))
    checks['curved_reconstruction']=all(max(row[name] for row in diag['B_front_and_C_curved'])<1e-11 for name in ('front_error','point_forcing_error','save_error'))
    checks['cohort_oracle']=max(row.get('cohort_oracle_change',0) for row in diag['B_admission'])<1e-9
    radial=local_qualification()  # unchanged analytical fixture implementation, explicit execution
    result=dict(passed=bool(radial['passed'] and all(checks.values())),radial=radial,
                diagnostics=diag,checks=checks,scientific_sources=sources,
                minimum_dependencies_passed=True,minimum_receipt=minimum,
                minimum_receipt_sha256=sha(args.minimum_receipt),
                diagnostics_sha256=sha(args.diagnostics),verification_source_sha256=sha(__file__),
                physical_validation='NOT_ESTABLISHED')
    args.output.write_text(json.dumps(result,sort_keys=True,indent=2,allow_nan=False)+'\n')
    print(json.dumps({'passed':result['passed'],'checks':checks}))
    return 0 if result['passed'] else 2


if __name__=='__main__':
    raise SystemExit(main())
