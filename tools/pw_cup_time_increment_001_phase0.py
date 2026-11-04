#!/usr/bin/env python3
"""Mass-only Phase 0 endpoints; no chemistry parser, fitting, or scoring.

Source: Dr. Yoana Grudeva, YoanaGrudeva/espresso-model at
567ad8f3808eb74fbe3e470eaa333161bf2eac1c. Derived outputs are
PERMISSION_DOCUMENTED, no SPDX licence, not relicensed under MIT;
see docs/permissions/grudeva2025.md. Originals remain external.
"""

import argparse
import csv
from decimal import Decimal, ROUND_FLOOR
import hashlib
import json
from pathlib import Path
import resource
from statistics import median
from typing import Iterable


SOURCE_SHA256 = "291cadb1d06a009f758c158c95b020db551c127333e9dec6f6c581eac320130c"
# CLOCK RESULT.md: positive-mass chemistry gaps at block 6/vial 3 and 13/vial 2.
# Reuse qualification metadata; never rediscover membership from chemistry here.
PRIMARY_SHOTS = (1, 2, 3, 4, 5, 7, 8, 9, 10, 11, 12)
ROW_LABELS = ("Vial No.", "Vial Weight", "Vial+Coffee", "Weight", "TDS")


def mass_windows(lines: Iterable[str]) -> dict[int, tuple[Decimal, ...]]:
    """Parse only regular vial identities and recorded Weight, preserving slots.

    Other row labels are checked for rectangular block alignment, but their
    payloads never enter the CSV parser or numeric conversion. No terminal or
    excluded-block value is converted. Hashing authenticates all original bytes.
    """
    windows = {}
    row_number = 0
    for line in lines:
        label = line.partition(",")[0].strip()
        if not label and not line.strip(", \t\r\n"):
            continue
        row_type = row_number % 5
        if label != ROW_LABELS[row_type]:
            raise ValueError("source block labels changed")
        shot = row_number // 5 + 1
        row_number += 1
        if shot not in PRIMARY_SHOTS or label not in ("Vial No.", "Weight"):
            continue
        fields = next(csv.reader([line]))[1:17]
        if len(fields) != 16:
            raise ValueError("incomplete regular mass window")
        values = tuple(Decimal(value.strip()) for value in fields)
        if label == "Vial No.":
            if values != tuple(Decimal(i) for i in range(1, 17)):
                raise ValueError("vial identity is not the original column position")
        else:
            if any(not v.is_finite() or v < 0 for v in values):
                raise ValueError("unresolved beverage mass gap")
            windows[shot] = values
    if row_number % 5 or row_number < 13 * 5 or tuple(windows) != PRIMARY_SHOTS:
        raise ValueError("incomplete qualified source blocks")
    return windows


def duration_at_mass(masses: tuple[Decimal, ...], endpoint: Decimal) -> Decimal:
    """Activation-clock crossing time, with exact decimal cumulative masses."""
    if endpoint <= 0:
        raise ValueError("endpoint must be positive")
    cumulative = Decimal(0)
    for index, mass in enumerate(masses):
        end = cumulative + mass
        if cumulative < endpoint <= end:
            u = (endpoint - cumulative) / mass
            return Decimal(2 * index) + 2 * u
        cumulative = end
    raise ValueError("endpoint exceeds regular-window mass")


def endpoint_summary(windows: dict[int, tuple[Decimal, ...]]) -> list[dict]:
    if tuple(windows) != PRIMARY_SHOTS:
        raise ValueError("expected the fixed 11 physical shots in source order")
    primary = min(sum(m) for m in windows.values()).quantize(
        Decimal("0.1"), rounding=ROUND_FLOOR
    )
    result = []
    for name, fraction in (("primary", "1"), ("secondary_0.5", "0.5"),
                           ("secondary_0.75", "0.75")):
        endpoint = primary * Decimal(fraction)
        times = [duration_at_mass(m, endpoint) for m in windows.values()]
        result.append({
            "endpoint": name,
            "mass_g": str(endpoint),
            "duration_min_s": float(min(times)),
            "duration_median_s": float(median(times)),
            "duration_max_s": float(max(times)),
        })
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True,
                        help="explicit pinned external exp13.csv (CLOCK priority route)")
    args = parser.parse_args()
    # One open handle: authenticate bytes, rewind, then inspect mass fields only.
    with args.source.open("rb") as stream:
        digest = hashlib.sha256()
        for chunk in iter(lambda: stream.read(65536), b""):
            digest.update(chunk)
        if digest.hexdigest() != SOURCE_SHA256:
            raise SystemExit("STOP: exp13.csv source SHA-256 mismatch")
        stream.seek(0)
        windows = mass_windows(line.decode("utf-8") for line in stream)
    summaries = endpoint_summary(windows)
    usage = resource.getrusage(resource.RUSAGE_SELF)
    print(json.dumps({
        "source_sha256": SOURCE_SHA256,
        "physical_shots": len(windows),
        "endpoints": summaries,
        "process_cpu_core_hours": (usage.ru_utime + usage.ru_stime) / 3600,
    }, indent=2))


if __name__ == "__main__":
    main()
