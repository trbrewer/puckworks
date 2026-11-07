"""No-fit controls for clocks, supported observations and paired resampling."""

import csv
import json
from pathlib import Path

import numpy as np
import pytest

from puckworks.analysis import wasz_turnover_time_001 as W


def test_paired_window_time_average_not_final_pressure():
    t = np.array([0., .2, 1., 2., 2.7, 4.])
    pressure, flow, reason = W.paired_window(t, 2*t + 1, 3*t - 2, 2.)
    assert reason == "available"
    assert pressure == pytest.approx(5.)
    assert flow == pytest.approx(4.)
    assert pressure != 2*t[-1] + 1


def test_no_padded_masked_or_unsupported_values():
    t = np.arange(10.)
    p, q = t + 1, t + 2
    # A padded tail may look finite but is never recorded support.
    assert W.paired_window(t, p, q, 6., support_end=6.5)[2] == "outside_recorded_support"
    valid = np.ones(len(t), dtype=bool)
    valid[5] = False
    assert W.paired_window(t, p, q, 5., valid=valid)[2] == "masked_or_nonfinite_support"
    masked = np.ma.array(q, mask=~valid)
    assert W.paired_window(t, p, masked, 5.)[2] == "masked_or_nonfinite_support"
    q[5] = np.nan
    assert W.paired_window(t, p, q, 5.)[2] == "masked_or_nonfinite_support"
    assert W.paired_window(t, p, q, .5)[2] == "outside_recorded_support"
    assert W.paired_window(t, p, q, np.nan)[2] == "onset_undetected"
    with pytest.raises(ValueError, match="strictly increasing"):
        W.paired_window([0, 1, 1], [1, 2, 3], [1, 2, 3], 1)


def test_synthetic_stable_clock_and_onset_interval_start(tmp_path):
    t = np.arange(0, 120.1, .1)
    p = np.where(t < 3., 0., 9.)
    mass = 7 + np.maximum(t - 12., 0.)
    path = tmp_path / "synthetic.txt"
    path.write_text("\n".join(json.dumps(dict(t=float(s*1000), p2=float(pp*100), m=float(m)))
                              for s, pp, m in zip(t, p, mass)))
    ct, cp, cq, onset, stable_offset = W.native_observation(path)
    assert stable_offset == pytest.approx(3.)
    assert ct[0] == 0
    # Absolute 12.5 s equals the strict mass threshold and does not qualify.
    # First >0.5 g is 12.6 s, so interval START is stable +9.6 s (not +11.6).
    assert onset == pytest.approx(9.6)
    assert W.paired_window(ct, cp, cq, onset + 10)[1] == pytest.approx(1.)
    assert W.paired_window(ct, cp, cq, 5)[2] == "available"  # before onset


def test_onset_strict_thresholds_and_failed_hold():
    t = np.arange(8.)
    assert W.B0.sustained_onset(t, np.ones(8), np.ones(8)) == 0
    assert np.isnan(W.B0.sustained_onset(t, np.full(8, .5), np.ones(8)))
    assert np.isnan(W.B0.sustained_onset(t, np.ones(8), np.full(8, .1)))
    flow = np.array([1., 1., 0., 0., 1., 1., 1., 1.])
    assert W.B0.sustained_onset(t, np.ones(8), flow) == 4


def test_shared_resamples_keep_brew_pressure_flow_and_time_together():
    condition = np.repeat([9., 11., 13.], 3)
    identity = np.arange(9.) + 1
    # Time offsets survive exactly iff all times use the same sampled identities.
    offsets = np.arange(len(W.SNAPSHOTS))[:, None]*100
    q = identity[None, :] + offsets
    p = q*2 + 7
    bank = W.draw_bank(condition)
    before = W.bank_digest(bank)
    mp, mq, bp, bq, counts = W.condition_statistics(p, q, condition, bank)
    np.testing.assert_allclose(bp, 2*bq + 7)
    np.testing.assert_allclose(mp, 2*mq + 7)
    for j in range(1, len(W.SNAPSHOTS)):
        np.testing.assert_allclose(bq[j] - bq[0], 100*j)
    assert counts.min() == 3
    assert W.bank_digest(bank) == before == W.bank_digest(W.draw_bank(condition))
    assert all(not d.flags.writeable for d in bank.values())


def test_missing_resampled_identity_never_redrawn():
    condition = np.array([9., 9., 11., 11., 13., 13.])
    q = np.array([[np.nan, 2., 3., 4., 5., 6.]])
    p = q + 10
    bank = W.draw_bank(condition)
    _, _, bp, bq, counts = W.condition_statistics(p, q, condition, bank)
    missing_draws = np.all(bank[9.] == 0, axis=1)
    assert missing_draws.any()
    assert np.isnan(bq[0, missing_draws, 0]).all()
    assert np.isnan(bp[0, missing_draws, 0]).all()
    np.testing.assert_allclose(bq[0, ~missing_draws, 0], 2.)
    assert counts[0, 0] == 1


def test_slope_is_unweighted_condition_mean_slope_and_requires_all_three():
    nominal = np.array([1., 9., 11., 13.])
    p = np.array([1., 8.8, 10.5, 12.6])
    q = 3 - .1*p
    q[0] = 100  # Not part of the high-pressure slope.
    assert W.high_slope(p, q, nominal) == pytest.approx(-.1)
    q[-1] = np.nan
    assert np.isnan(W.high_slope(p, q, nominal))


def test_maximum_ties_edge_missing_and_nonpositive_ratio():
    nominal = np.array([1., 9., 11., 13.])
    selected, edge, ratio, missing = W.maximum(np.array([0., 2., 2., 1.]), nominal)
    assert selected == [9., 11.] and not edge and ratio == .5 and missing == []
    selected, edge, ratio, missing = W.maximum(np.array([np.nan, 2., 1., 1.]), nominal)
    assert selected == [9.] and edge and missing == [1.] and ratio == .5
    assert np.isnan(W.maximum(np.zeros(4), nominal)[2])
    assert W.maximum(np.full(4, np.nan), nominal)[0] == []


def test_committed_stage_a_reference_and_time_series_contract():
    def rows(name):
        with (W.OUT / name).open() as stream:
            return list(csv.DictReader(stream))
    reference = rows("STAGE_A_REFERENCE.csv")
    response = next(r for r in reference if r["record_type"] == "response")
    assert float(response["slope_g_s_bar"]) == pytest.approx(-.06550641262782862, abs=1e-10)
    assert float(response["maximum_nominal_bar"]) == 6.
    with (W.ROOT / "docs/research/PRESSURE_PEAK_STAGE_A/RESULT_TABLE.csv").open() as stream:
        old = json.loads(next(csv.DictReader(stream))["observed per-pressure flow g/s"])
    for row, expected in zip((r for r in reference if r["record_type"] == "condition"), old):
        assert float(row["flow_g_s"]) == expected["mean"]
        assert float(row["pressure_bar"]) == expected["direct_line"]
    brews = rows("PER_BREW_BY_TIME.csv")
    assert len(brews) == 560 and len({r["brew"] for r in brews}) == 56
    assert "12-8-6_alt" not in {r["brew"] for r in brews}
    assert {(r["clock"], int(r["time_s"])) for r in brews} == set(W.SNAPSHOTS)
    for row in brews:
        if row["available"] == "True":
            start, end = float(row["window_start_stable_s"]), float(row["window_end_stable_s"])
            assert end - start == pytest.approx(2)
            assert float(row["recorded_start_stable_s"]) <= start < end <= float(row["recorded_end_stable_s"])
            expected_center = int(row["time_s"]) + (float(row["onset_stable_s"]) if row["clock"] == "onset" else 0)
            assert (start + end)/2 == pytest.approx(expected_center)
    assert len(rows("AVAILABILITY.csv")) == 110


@pytest.mark.external_data
def test_exact_stage_a_external_reproduction():
    ewp = Path("/home/tim/ewp-form-a-001")
    if not ewp.exists():
        pytest.skip("Read-only EWP reference is not mounted")
    brews, _ = W.stage_a_reference(ewp)
    assert len(brews.ids) == 56
