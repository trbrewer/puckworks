"""Independent direct arithmetic for the decisive source operands.

No producer imports or classification helpers. Run after offline generation.
The native centre and anchor allowances are verified against the frozen contract.
"""
import argparse
import csv
from fractions import Fraction as F
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
DATA = ROOT / "puckworks/data/maille2021/swelling_evidence_001"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path(__file__).parent)
    args = parser.parse_args()
    contract = json.loads((DATA / "contract.json").read_text())
    assert contract["reading_allowance_px"] == "4"
    assert contract["anchor_allowance_px"] == "1"
    assert contract["axes"]["size_um"] == {"pixels": ["216", "11"], "values": ["0", "1600"]}
    with (DATA / "coordinates.csv").open() as file:
        rows = list(csv.DictReader(file))
    lookup = {(r["observation_id"], r["series_id"]): r for r in rows}
    assert len(lookup) == len(rows) == 24
    # Throughout these interior coordinates, extrema have both y anchors shifted
    # together: 216-y +/- (4+1), denominator205. Re-derive directly, not via code.
    def bound(y, maximum):
        return (F(maximum)*(216-int(y)-5)/205, F(maximum)*(216-int(y)+5)/205)
    intervals = {"R": [], "K_m_minus3": []}
    for oid in sorted({r["observation_id"] for r in rows}):
        med, upper, conc = [lookup[oid, s] for s in ("x50", "x90", "C_V")]
        assert med["x_px"] == upper["x_px"] == conc["x_px"]
        ml, mh = bound(med["y_px"], "1600")
        ul, uh = bound(upper["y_px"], "1600")
        cl, ch = bound(conc["y_px"], "0.4")
        intervals["R"].append((oid, ul/mh, uh/ml))
        intervals["K_m_minus3"].append((oid, cl/100/(mh/10**6)**3,
                                       ch/100/(ml/10**6)**3))
    result = json.loads((args.output / "RESULT.json").read_text())
    for key, values in intervals.items():
        for oid, lo, hi in values:
            row = next(r for r in result["observations"] if r["observation_id"] == oid)
            assert list(map(F, row[key]["exact"])) == [lo, hi]
        common_lo = max(lo for _, lo, _ in values)
        common_hi = min(hi for _, _, hi in values)
        print(key, "max lower", common_lo, "min upper", common_hi)
        assert (common_lo > common_hi) == (key == "K_m_minus3")
    first = intervals["K_m_minus3"][0]
    last = intervals["K_m_minus3"][-1]
    assert first[0] == "M21-LD-01-O01" and last[0] == "M21-LD-01-O08"
    assert first[1] > last[2]
    print("Independent O01-lower > O08-upper certificate PASS; graphical scope only")


if __name__ == "__main__":
    main()
