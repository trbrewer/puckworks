"""Reduce a fresh optional replay; requires its complete moment/boundary histories."""
import argparse
from pathlib import Path

import numpy as np

import balance

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("case", type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    if args.out.exists():
        raise FileExistsError("new output file required")
    moments = np.loadtxt(args.case / "history.csv", delimiter=",")
    boundary = np.loadtxt(args.case / "boundary_history.csv", delimiter=",")
    records = [balance.attribute(moments, boundary, 40, time, method)
               for time in (0., 1., 10.) for method in ("trap", "simpson", "coarse")]
    balance.write_csv(args.out, records)
    print("Reduced supplied run; no solver executed; conditional dimensional accounting only")
