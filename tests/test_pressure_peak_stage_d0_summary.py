"""CSV-only check of D0's descriptive fold-identification paragraph."""

import csv
import json
import math
from pathlib import Path
import re

import numpy as np
from numpy.testing import assert_allclose


def test_lc_fold_identification_paragraph():
    directory = Path(__file__).resolve().parents[1] / "docs/research/PRESSURE_PEAK_STAGE_D0"
    fits, residuals = {}, {}
    previous_limit = csv.field_size_limit(100_000_000)
    try:
        with (directory / "RESULT_TABLE.csv").open(newline="") as stream:
            for row in csv.DictReader(stream):
                if row["record_type"] == "refit":
                    key = (int(row["draw"]), row["candidate"], row["fold"])
                    assert key not in fits
                    fits[key] = json.loads(row["parameters"])
                elif row["record_type"] == "draw_metrics":
                    draw = int(row["draw"])
                    assert draw not in residuals
                    residuals[draw] = json.loads(row["values"])["LC"]["metrics"]["residual_3_5_g_s"]
    finally:
        csv.field_size_limit(previous_limit)

    assert set(residuals) == set(range(200))
    fold = "HYD-LOCO-3.5"
    negative = {draw for draw, value in residuals.items() if value < 0}
    remaining = set(residuals) - negative
    expected = []
    for form in ("LC", "A"):
        for selected in (True, False):
            values = np.sort([p["n"] for (_, candidate, name), p in fits.items()
                              if candidate == form and (name == fold) == selected])
            assert len(values) == (200 if selected else 2200)
            # The inherited interval is nearest rank, not interpolated percentiles.
            expected.append([np.median(values), *[values[math.ceil(p * len(values)) - 1]
                                                  for p in (0.025, 0.975)]])
    for field in ("n", "f", "Pd_bar"):
        for draws in (negative, remaining):
            values = [fits[draw, "LC", fold][field] for draw in sorted(draws)]
            expected.append([np.median(values), min(values), max(values)])

    summary = (directory / "SUMMARY.md").read_text()
    start = summary.index("Across the 200 refits, LC n median [nearest-rank 95% interval]")
    paragraph = summary[start:summary.index("\n\n", start)]
    number = r"([-+]?\d+(?:\.\d+)?(?:[eE][-+]?\d+)?)"
    triples = re.findall(number + r" \[" + number + r", " + number + r"\]", paragraph)
    assert_allclose(np.asarray(triples, dtype=float), expected, rtol=1e-12, atol=0)

    counts = re.search(r"negative in (\d+) of (\d+) draws", paragraph)
    assert counts is not None
    assert tuple(map(int, counts.groups())) == (len(negative), len(residuals))
    groups = re.search(r"for those (\d+) draws versus the remaining (\d+) draws", paragraph)
    assert groups is not None
    assert tuple(map(int, groups.groups())) == (len(negative), len(remaining))
    assert "other 11 folds pooled (2,200 fits, including DESCRIPTIVE_ALL)" in paragraph
    assert "For A, the corresponding n values" in paragraph
    assert "median [range] is n " in paragraph and "; f " in paragraph and "; Pd " in paragraph
    assert summary.index("| T2-F | -0.0252786") < start < summary.index("Observed within-2-bar ratio")
