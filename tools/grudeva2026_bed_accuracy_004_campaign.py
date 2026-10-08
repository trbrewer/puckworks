"""Execute exactly the frozen seven-row 004 campaign through its external ledger."""
import argparse
import json
from pathlib import Path
import subprocess
import sys

from puckworks.analysis.grudeva2026_bed_accuracy_004_report import sha, scientific_sources


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--runs-directory', type=Path, required=True)
    parser.add_argument('--matrix', type=Path, required=True)
    args = parser.parse_args()
    folder = args.runs_directory.resolve()
    plan = json.loads(args.matrix.read_text())
    if plan['scientific_sources'] != scientific_sources():
        raise ValueError('frozen scientific source mismatch')
    if plan['controller_sha256'] != sha(folder/'invoke.py'):
        raise ValueError('external controller mismatch')
    for name in plan['scheduling']['order']:
        row = plan['runs'][name]
        command = [sys.executable, str(folder/'invoke.py'), row['attempt'],
                   'full', 'final', sys.executable, '-m',
                   'puckworks.analysis.grudeva2026_bed_accuracy_004']
        for key, value in row['controls'].items():
            command += ['--'+key, str(value)]
        command += ['--output', str(folder/row['file'])]
        print('START '+name, flush=True)
        subprocess.run(command, check=True)
        print('END '+name, flush=True)


if __name__ == '__main__':
    main()
