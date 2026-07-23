"""P1.1 — public-boundary units / array / trace validation. These are ADDITIVE helpers; this
file also carries the bar-vs-pascal factor-of-100000 regression guard.
"""
import numpy as np
import pytest

from puckworks import validate as V


def test_bar_pascal_conversion_and_the_factor_of_100000():
    assert V.bar_gauge_to_pa(9.0) == 9.0e5                  # 9 bar == 900000 Pa
    assert V.pa_to_bar_gauge(9.0e5) == 9.0
    assert V.bar_gauge_to_pa(0.0) == 0.0
    # the classic error: a bar value (~9) passed where Pa (~9e5) is expected
    assert V.is_plausible_pressure_pa(9.0e5) is True
    assert V.is_plausible_pressure_pa(9.0) is False         # 9 Pa is implausibly low -> flagged
    assert V.is_plausible_pressure_pa(9.0e9) is False       # implausibly high
    with pytest.raises(ValueError, match="off by ~1e5"):
        V.assert_pressure_pa(9.0, "P_in")
    assert V.assert_pressure_pa(9.0e5) == 9.0e5


def test_is_plausible_pressure_pa_arrays():
    assert V.is_plausible_pressure_pa(np.array([2e5, 9e5, 1.2e6])) is True
    assert V.is_plausible_pressure_pa(np.array([9e5, 9.0])) is False   # one bad element fails


def test_array_validators_pass_and_fail():
    V.require_finite([1.0, 2.0]); V.require_positive([1e-6, 3.0])
    V.require_nonnegative([0.0, 1.0]); V.require_fraction([0.0, 0.5, 1.0])
    V.require_monotonic_increasing([0.0, 1.0, 2.0])
    with pytest.raises(ValueError, match="non-finite"):
        V.require_finite([1.0, np.nan])
    with pytest.raises(ValueError, match="strictly positive"):
        V.require_positive([1.0, 0.0])
    with pytest.raises(ValueError, match=r"\[0, 1\]"):
        V.require_fraction([0.0, 1.5])
    with pytest.raises(ValueError, match="strictly increasing"):
        V.require_monotonic_increasing([0.0, 1.0, 1.0])     # equal step not allowed (strict)


def test_require_aligned_and_ndim():
    assert V.require_aligned({"t": [0, 1, 2], "q": [1, 2, 3]}) == 3
    with pytest.raises(ValueError, match="misaligned"):
        V.require_aligned({"t": [0, 1, 2], "q": [1, 2]})
    V.require_ndim(np.zeros((3, 3)), 2)
    with pytest.raises(ValueError, match="must be 1-D"):
        V.require_ndim(np.zeros((3, 3)), 1)


def test_closure_vocabulary():
    assert V.require_closure("poroelastic") == "poroelastic"
    assert V.Closure.CK.value == "ck"
    with pytest.raises(ValueError, match="unknown closure"):
        V.require_closure("magic")


def test_trace_validation():
    t = np.array([0.0, 1.0, 2.0])
    tr = V.Trace(time=t, channels={"flow_g_s": np.array([0.0, 1.0, 1.5])},
                 units={"flow_g_s": "g/s"}, source="test").validate()
    assert tr._validated
    # misaligned channel
    with pytest.raises(ValueError, match="!= time length"):
        V.Trace(time=t, channels={"q": np.array([0.0, 1.0])}, units={"q": "g/s"}).validate()
    # non-monotonic time
    with pytest.raises(ValueError, match="strictly increasing"):
        V.Trace(time=np.array([0.0, 2.0, 1.0]), channels={"q": np.zeros(3)},
                units={"q": "g/s"}).validate()
    # missing unit (now caught by exact channel<->unit key coverage)
    with pytest.raises(ValueError, match="must exactly match channel keys"):
        V.Trace(time=t, channels={"q": np.zeros(3)}, units={}).validate()
    # PW-VAL-001/002: scalar time, infinite channel, 2-D channel, and extra unit key all rejected
    with pytest.raises(ValueError, match="1-D"):
        V.Trace(time=5.0, channels={"q": np.zeros(1)}, units={"q": "g/s"}).validate()
    with pytest.raises(ValueError, match="infinite"):
        V.Trace(time=t, channels={"q": np.array([0.0, np.inf, 1.0])}, units={"q": "g/s"}).validate()
    with pytest.raises(ValueError, match="1-D"):
        V.Trace(time=t, channels={"q": np.zeros((3, 2))}, units={"q": "g/s"}).validate()
    with pytest.raises(ValueError, match="must exactly match"):
        V.Trace(time=t, channels={"q": np.zeros(3)}, units={"q": "g/s", "x": "y"}).validate()
    # nan is still an allowed missing marker and serializes strictly (allow_nan=False)
    import json
    tr2 = V.Trace(time=t, channels={"q": np.array([0.0, np.nan, 1.0])}, units={"q": "g/s"})
    json.loads(tr2.to_json())


def test_trace_to_dict_preserves_missing_as_null():
    t = np.array([0.0, 1.0])
    d = V.Trace(time=t, channels={"q": np.array([1.0, np.nan])},
                units={"q": "g/s"}, source="s").validate().to_dict()
    assert d["schema_version"] == V.TRACE_SCHEMA_VERSION
    assert d["channels"]["q"] == [1.0, None]                # nan -> None, never dropped
    assert d["units"] == {"q": "g/s"}
