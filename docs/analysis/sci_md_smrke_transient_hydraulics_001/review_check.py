"""Independent S1 arithmetic/readback check; never imports the producer.

Run from any directory with Python and Pillow. This verifies reported bounds
against native reading cells and the declared calibration corners; it does not
turn the graphical enclosure premises into laboratory uncertainty.
"""
from __future__ import annotations

import argparse
import colorsys
import csv
from fractions import Fraction
import hashlib
from io import BytesIO
import json
from pathlib import Path
import zipfile

from PIL import Image


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
DATA = ROOT / "puckworks/data/smrke2024/s1"
F = Fraction


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def csv_rows(path):
    with path.open() as stream:
        return list(csv.DictReader(stream))


def inverse_range(t0, t1):
    values = []
    for t in (t0, t1):
        for zero in (77, 79):
            for eighty in (1546, 1548):
                values.append(zero + t * (eighty - zero) / 80)
    return min(values), max(values)


def ordinate_range(y0, y1):
    values = []
    for y in (y0 - 2, y1 + 2):
        for zero in (942, 944):
            for seven in (77, 79):
                values.append(7 * (zero - y) / (zero - seven))
    return min(values), max(values)


def independent_integral(cells, start, stop):
    total_lower = total_upper = F(0)
    t = start
    pieces = 0
    while t < stop:
        end = min(stop, t + F(1, 20))
        xl, xu = inverse_range(t, end)
        hits = [c for c in cells if c["xl"] <= xu and xl <= c["xu"]]
        cursor = xl
        for c in sorted(hits, key=lambda c: (c["xl"], c["xu"])):
            assert c["xl"] <= cursor, ("unsupported horizontal support", t, c)
            cursor = max(cursor, c["xu"])
        assert cursor >= xu, ("uncovered right boundary", t)
        low, high = ordinate_range(min(c["yl"] for c in hits), max(c["yu"] for c in hits))
        total_lower += (end - t) * low
        total_upper += (end - t) * high
        pieces += 1
        t = end
    return total_lower / (stop - start), total_upper / (stop - start), pieces


def check():
    contract = json.loads((DATA / "contract.json").read_text())
    source = contract["source"]
    docx = DATA.parent / source["docx"]
    assert sha(docx) == source["docx_sha256"]
    with zipfile.ZipFile(docx) as archive:
        payload = archive.read(source["image_member"])
    assert hashlib.sha256(payload).hexdigest() == source["image_sha256"]
    im = Image.open(BytesIO(payload)).convert("RGB")
    assert im.size == (1680, 1041)

    # Independently inspect dark tick strokes, not the numerical transform alone.
    xticks = [x for x in range(60, 1650)
              if sum(max(im.getpixel((x, y))) < 80 for y in range(944, 953)) >= 5]
    yticks = [y for y in range(60, 955)
              if sum(max(im.getpixel((x, y))) < 80 for x in range(68, 78)) >= 5]
    assert xticks == [78, 446, 813, 1180, 1547]
    assert yticks == [78, 202, 325, 449, 572, 696, 819, 943]
    assert contract["calibration"]["y_tick_values_g_s"] == list(range(8))
    assert contract["calibration"]["anchor_allowance_px"] == "1"
    assert contract["calibration"]["reading_allowance_y_px"] == "2"

    observations = csv_rows(DATA / "source_observations.csv")
    excluded = csv_rows(DATA / "excluded_ink.csv")
    assert not any(1200 <= int(r["x_px"]) <= 1639 and int(r["y_min_px"]) <= 286
                   for r in observations)
    assert any(r["colour"] == "yellow" and int(r["x_px"]) == 1272
               and int(r["y_min_px"]) <= 104 <= int(r["y_max_px"])
               and r["mask_id"] == "legend" for r in excluded)
    yellow_contact = [r for r in observations if r["colour"] == "yellow"
                      and 188 <= int(r["x_px"]) <= 192 and int(r["y_min_px"]) <= 82]
    assert len(yellow_contact) == 3
    assert all(r["clipping"] == "1" and r["flow_upper_g_s"] == "" for r in yellow_contact)

    # Every recorded native ordinate must actually be admitted source-colour ink.
    by_id = {r["observation_id"]: r for r in observations}
    raw_cells = csv_rows(DATA / "reading_cells.csv")
    native_checks = 0
    for c in raw_cells:
        if c["support_kind"] != "NATIVE_INK_COLUMN":
            continue
        for rid in c["support_readings"].split("|"):
            r = by_id[rid]
            for y in range(int(r["y_min_px"]), int(r["y_max_px"]) + 1):
                rgb = im.getpixel((int(r["x_px"]), y))
                h, saturation, value = colorsys.rgb_to_hsv(*(v / 255 for v in rgb))
                hlo, hhi, _ = contract["colour_rules"][r["colour"]]
                assert saturation >= .25 and value >= .15 and hlo <= 360 * h <= hhi
                native_checks += 1

    cells = [dict(parent=c["object_id"], xl=F(c["x_lower_px"]), xu=F(c["x_upper_px"]),
                  yl=F(c["y_lower_px"]), yu=F(c["y_upper_px"])) for c in raw_cells]
    objects = {o["id"]: o for o in json.loads((HERE / "QUALIFIED_OBJECTS.json").read_text())}
    blue_ranges = sorted(tuple(map(F, o["support_x_px"])) for o in objects.values()
                         if o["colour"] == "blue")
    assert blue_ranges == [(F("300.5"), F("401.5")), (F("406.5"), F("478.5"))]
    windows = json.loads((HERE / "WINDOW_WITNESSES.json").read_text())
    assert len(windows) == 232
    recomputed = {}
    for key, row in windows.items():
        if row["lower"] is None:
            continue
        obj = objects[row["object_id"]]
        support = list(map(F, obj["support_x_px"]))
        own = [c for c in cells if c["parent"] == obj["parent_region_id"]
               and support[0] <= c["xl"] and c["xu"] <= support[1]]
        lower, upper, pieces = independent_integral(own, F(row["start_s"]), F(row["end_s"]))
        assert (lower, upper) == (F(row["lower"]), F(row["upper"])), key
        recomputed[key] = dict(lower=str(lower), upper=str(upper), integration_pieces=pieces)
    assert len(recomputed) == 4
    temporal = json.loads((HERE / "TEMPORAL_COMPARISONS.json").read_text())
    assert all(row["status"] == "UNSUPPORTED" for row in temporal["ordered"] + temporal["recovery"])
    assert all(row["status"] in {"UNSUPPORTED", "UNINFORMATIVE"} for row in temporal["constant"])
    multipliers = json.loads((HERE / "MULTIPLIERS.json").read_text())
    assert len(multipliers) == 36 and all(row["status"] == "UNSUPPORTED" for row in multipliers)
    coverage = json.loads((HERE / "COVERAGE.json").read_text())
    assert len(coverage) == 12 and sum(row["nominal_extractions"] for row in coverage) == 36
    assert all(row["recovered_physical_shots"] == 0 and not row["condition_envelope_complete"]
               for row in coverage)

    strict = []
    comparisons = json.loads((HERE / "FINES_COMPARISONS.json").read_text())
    assert len({r["pair_id"] for r in comparisons}) == 18
    for row in comparisons:
        for pair in row["comparisons"]:
            aa, bb = [recomputed[w] for w in pair["windows"]]
            diff = [F(bb["lower"]) - F(aa["upper"]), F(bb["upper"]) - F(aa["lower"])]
            assert diff == list(map(F, pair["difference"]))
            if diff[0] > 0 or diff[1] < 0:
                strict.append(dict(pair_id=row["pair_id"], start_s=row["start_s"], end_s=row["end_s"],
                                   difference=list(map(str, diff)), windows=pair["windows"]))
    assert len(strict) == 1 and strict[0]["pair_id"] == "250:1:2"
    assert strict[0]["start_s"] == "6" and strict[0]["end_s"] == "9"
    assert F(strict[0]["difference"][1]) < 0
    return dict(review="INDEPENDENT_SOURCE_AND_EXACT_ARITHMETIC_CHECK", status="PASS",
                source_sha256=source["image_sha256"], native_pixel_readbacks=native_checks,
                independently_recomputed_windows=recomputed, strict_partial_bundle_witnesses=strict,
                limitation="Checks the declared graphical enclosures; no physical uncertainty or replicate validation.",
                hashes={str(p.relative_to(ROOT)): sha(p) for p in
                        [DATA / "contract.json", DATA / "regions.json", DATA / "qualification_correction.json",
                         DATA / "source_observations.csv", DATA / "excluded_ink.csv", DATA / "ink_fragments.csv",
                         DATA / "reading_cells.csv", DATA / "qualified_fragments.json", DATA / "CORRECTION.md",
                         HERE / "CONTRACT_FREEZE.json", HERE / "CONTRACT.md", HERE / "QUALIFIED_OBJECTS.json",
                         HERE / "WINDOW_WITNESSES.json", HERE / "FINES_COMPARISONS.json", HERE / "COVERAGE.json",
                         HERE / "TEMPORAL_COMPARISONS.json", HERE / "MULTIPLIERS.json", HERE / "DOMAIN_COVERAGE.json",
                         HERE / "SOURCE_OVERLAY.svg", HERE / "COMPARISON.svg", HERE / "RESULT.json",
                         HERE / "RESULT.md", HERE / "REVIEW.md", ROOT / "puckworks/analysis/smrke2024_transient.py",
                         ROOT / "puckworks/data/__init__.py", Path(__file__)]})


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    receipt = json.dumps(check(), indent=2) + "\n"
    if args.output:
        args.output.write_text(receipt)
    else:
        print(receipt, end="")
