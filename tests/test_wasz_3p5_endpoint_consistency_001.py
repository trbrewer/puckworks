"""Focused no-fit audit checks; synthetic chronology and endpoint semantics."""
import csv
import hashlib
import json
from pathlib import Path

import numpy as np
import pytest

from puckworks.analysis import wasz_3p5_endpoint_consistency_001 as W


def test_raw_audit_keeps_missing_mass_rows_and_original_order():
    text = '\n'.join(json.dumps(r) for r in (
        {"t": 1000, "p2": 200, "m": 0},
        {"t": 2000, "p2": 200},  # Must not be removed before interval audit.
        {"t": 2000, "p2": 200, "m": 1},
        {"t": 1500, "p2": 200, "m": 2},
        {"t": 5000, "p2": 200, "m": 3}))
    audit, records = W.audit_raw(text)
    assert [r["t"] for r in records] == [1000, 2000, 2000, 1500, 5000]
    assert audit["missing_m"] == 1
    assert audit["repeated_timestamp_records"] == 1
    assert audit["adjacent_nonincreasing_timestamps"] == 2
    assert audit["raw_adjacent_dt_min_s"] == -.5
    assert audit["raw_adjacent_dt_median_s"] == .5
    assert audit["largest_gaps"][0] == {"from_line": 4, "to_line": 5, "dt_s": 3.5}


def test_missing_timestamps_and_malformed_lines_are_not_bridged():
    audit, records = W.audit_raw(
        '{"t":0,"m":0}\n{"m":1}\n{"t":5000,"m":2}\n\ninvalid\n{"t":6000}')
    assert len(records) == 6
    assert audit["blank_lines"] == 1
    assert audit["malformed_lines"] == 1
    assert audit["adjacent_timestamp_pairs"] == 0
    assert audit["raw_adjacent_dt_max_s"] is None
    assert audit["raw_end_timestamp_s"] == 6.


def test_endpoint_pressure_pairs_time_not_final_record_or_nominal_label():
    assert W.endpoint_pressure([0, 50, 100, 110], [0, 1, 3, 9]) == 3.
    assert W.endpoint_pressure([0, 80, 120], [0, 2, 6]) == 4.


@pytest.mark.parametrize("times,pressure", [
    ([0, 99], [1, 2]), ([101, 120], [1, 2]),
    ([0, 110, 100], [1, 2, 3]), ([0, 100, 100], [1, 2, 3]),
    ([0, 100], [1, np.nan]),
])
def test_endpoint_pairing_rejects_extrapolation_or_reordering(times, pressure):
    with pytest.raises(ValueError, match="Unsupported or unordered"):
        W.endpoint_pressure(times, pressure)


def test_excursions_preserve_named_support_and_inherited_band():
    r = W.excursions([-3, -2, -1, 0], [.5, .7, 1.3, 1.], .9, 1.1)
    assert r["below_band_duration_s"] == 2
    assert r["longest_below_band_duration_s"] == 2
    assert r["above_band_duration_s"] == 1
    assert r["overshoot_above_upper_band_bar"] == pytest.approx(.2)
    assert r["below_band_intervals_s"] == [[-3., -1.]]
    assert r["above_band_intervals_s"] == [[-1., 0.]]


def test_step_comparison_uses_condition_means_and_leaves_zero_undefined():
    pairs = [dict(nominal_pressure_bar=p, endpoint_flow_g_s=q, endpoint_line_pressure_bar=a)
             for p, q, a in ((2., 1., 1.5), (2., 3., 2.5), (3.5, 5., 2.), (4., 6., 4.))]
    rows = W.adjacent_steps(pairs)
    assert rows[0]["change_g_s_per_bar"] == 2.
    assert rows[1]["change_g_s_per_bar"] is None
    assert rows[3]["change_g_s_per_bar"] == .5


def test_compact_artifacts_preserve_all_brews_and_source_identities():
    out = W.OUT
    if not (out / "ENDPOINT_PAIRS.csv").exists():
        pytest.skip("Compact outputs not yet generated")
    with (out / "ENDPOINT_PAIRS.csv").open() as f:
        rows = list(csv.DictReader(f))
    trace_ids = {name for g in W.D.waszkiewicz_traces_per_brew(include_aliases=False).values()
                 for name in g}
    assert len(rows) == 56
    assert {r["brew"] for r in rows} == trace_ids
    targets = {r["shot_id"]: float(r["mass_flow_rate__g_per_s"])
               for r in W.D.waszkiewicz_equilibrium_windows() if r["window"] == "endpoint_100s"}
    for r in rows:
        assert float(r["endpoint_flow_g_s"]) == targets[r["brew"]]
        assert float(r["pressure_difference_bar"]) == 0
        assert float(r["flow_difference_g_s"]) == 0
    hashes = json.loads((out / "INPUT_HASHES.json").read_text())
    for name in ("traces_per_brew.csv", "equilibrium_windows.csv"):
        path = Path("puckworks/data/waszkiewicz2025") / name
        assert hashlib.sha256((W.ROOT / path).read_bytes()).hexdigest() == hashes["PW:"+str(path)]
    verification = json.loads((out / "VERIFICATION.json").read_text())
    assert verification["raw_audit_completed_before_preprocessing"]
    assert verification["saved_observed_flows_onsets_identical"]
    assert verification["model_fits"] == verification["model_evaluations"] == verification["model_scores"] == 0
