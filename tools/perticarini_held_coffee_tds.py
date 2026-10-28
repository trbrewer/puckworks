"""Run the pre-frozen private Perticarini/Egidi TDS comparison."""
import argparse
from pathlib import Path
from puckworks.analysis.perticarini_held_coffee_tds import run


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    result = run(args.root, args.output)
    print(result['status'])


if __name__ == '__main__':
    main()
