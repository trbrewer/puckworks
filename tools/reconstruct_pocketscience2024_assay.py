#!/usr/bin/env python3
"""Explicit local check. Never publishes private source rows or aggregates."""
import argparse
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from puckworks.analysis.pocketscience2024_assay import replay_workbook, compare_exports


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--root',type=Path)
    p.add_argument('--output',type=Path,required=True,help='external private result JSON')
    args=p.parse_args()
    if args.root is None:
        import os
        from tools.inventory_local_corpus import config_path
        config=json.loads(config_path().read_text())
        args.root=Path(os.environ.get('PUCKWORKS_EXTERNAL_DATA_ROOT') or config['inventory']['root'])
    repo=Path(__file__).resolve().parents[1]
    if args.output.resolve().is_relative_to(repo):p.error('source replay output must be external')
    import hashlib
    doc=repo/'docs/analysis/sci_md_radial_obs_001'
    sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    contract=json.loads((doc/'CONTRACT.json').read_text())
    audit=json.loads((doc/'AUDIT.json').read_text())
    if audit['status']!='PASS' or audit['contract_sha256']!=sha(doc/'CONTRACT.json'):
        p.error('exact independent pre-analysis audit required')
    for name,h in contract['puckworks_code_sha256'].items():
        if sha(repo/name)!=h:p.error('frozen source code changed')
    for name,h in contract['source_files_sha256'].items():
        if sha(args.root/'pocketscience2024'/name)!=h:p.error('source identity changed: '+name)
    source=args.root/'pocketscience2024'/'Espresso water flow experiment.xlsx'
    result=replay_workbook(source)
    result["export_comparison"]=compare_exports(source.parent,result)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    print(json.dumps(dict(experimental_shots=len(result['experimental_rows']),conditions=len(result['condition_means']),formula_cells=len(result['cell_replay']),discrepancies=len(result['discrepancies']),unsupported=len(result['unsupported']))))

if __name__=='__main__':main()
