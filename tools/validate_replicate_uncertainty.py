#!/usr/bin/env python3
"""Validate normalized replicate/uncertainty CSVs before weighted analyses."""
from __future__ import annotations
import argparse, csv, math
from pathlib import Path

REQUIRED = {"dataset", "condition_id", "analyte", "observable", "mean", "unit", "n", "sd", "rsd_percent", "uncertainty_source", "source_file", "source_table", "provenance_note"}

def _number(text: str, field: str, rowno: int, allow_blank: bool = False) -> float | None:
    if text.strip() == "" and allow_blank:
        return None
    try:
        value=float(text)
    except ValueError as exc:
        raise ValueError(f"row {rowno}: {field} is not numeric: {text!r}") from exc
    if not math.isfinite(value):
        raise ValueError(f"row {rowno}: {field} must be finite")
    return value

def validate(path: Path) -> int:
    errors=[]
    with path.open(newline="", encoding="utf-8-sig") as f:
        reader=csv.DictReader(f)
        missing=REQUIRED-set(reader.fieldnames or [])
        if missing:
            raise SystemExit(f"missing required columns: {sorted(missing)}")
        count=0
        for rowno,row in enumerate(reader,start=2):
            count+=1
            try:
                if not row["dataset"].strip() or not row["condition_id"].strip():
                    raise ValueError(f"row {rowno}: dataset and condition_id are required")
                mean=_number(row["mean"],"mean",rowno)
                n=_number(row["n"],"n",rowno,allow_blank=True)
                sd=_number(row["sd"],"sd",rowno,allow_blank=True)
                rsd=_number(row["rsd_percent"],"rsd_percent",rowno,allow_blank=True)
                if n is not None and (n < 1 or int(n) != n):
                    raise ValueError(f"row {rowno}: n must be a positive integer")
                if sd is None and rsd is None:
                    raise ValueError(f"row {rowno}: provide sd or rsd_percent")
                if sd is not None and sd < 0:
                    raise ValueError(f"row {rowno}: sd must be non-negative")
                if rsd is not None and rsd < 0:
                    raise ValueError(f"row {rowno}: rsd_percent must be non-negative")
                if sd is not None and rsd is not None and mean != 0:
                    implied=abs(mean)*rsd/100
                    tol=max(1e-12,0.005*max(abs(sd),abs(implied)))
                    if abs(sd-implied)>tol:
                        raise ValueError(f"row {rowno}: sd and RSD disagree ({sd} vs {implied})")
                if (sd == 0 or rsd == 0) and "rounded" not in row["provenance_note"].lower():
                    raise ValueError(f"row {rowno}: zero uncertainty needs a rounding/resolution note")
            except ValueError as exc:
                errors.append(str(exc))
    if errors:
        print("\n".join(errors))
        return 1
    print(f"validated {count} rows: {path}")
    return 0

def main() -> int:
    p=argparse.ArgumentParser()
    p.add_argument("csv_path", type=Path)
    a=p.parse_args()
    return validate(a.csv_path)
if __name__ == "__main__":
    raise SystemExit(main())
