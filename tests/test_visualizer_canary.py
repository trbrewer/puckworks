"""Offline tests for the live-contract canary (WP0.6). Injected fake transport — NO network,
no data retained. Verifies shape recognition and drift detection."""
from puckworks.lib import visualizer_canary as canary


def _list(items):
    return lambda cfg: {"data": items}


def test_canary_passes_on_chart_data_toplevel():
    fl = _list([{"id": "x", "updated_at": 1}])
    fd = lambda cfg, sid: {"id": sid, "updated_at": 1, "timeframe": [0, 1],
                           "data": {"espresso_pressure": [6, 9]}}
    rep = canary.canary_check(list_fetcher=fl, detail_fetcher=fd)
    assert rep["ok"] is True and rep["detail_shape"] == "chart_data_toplevel"
    assert rep["n_requests"] == 2 and "NO user data retained" in rep["note"]


def test_canary_recognizes_nested_and_brewdata_shapes():
    fl = _list([{"id": "x", "updated_at": 1}])
    nested = canary.canary_check(list_fetcher=fl,
                                 detail_fetcher=lambda c, s: {"id": s, "updated_at": 1,
                                                              "data": {"timeframe": [0, 1]}})
    assert nested["detail_shape"] == "chart_data_nested" and nested["ok"]
    bd = canary.canary_check(list_fetcher=fl,
                             detail_fetcher=lambda c, s: {"id": s, "updated_at": 1,
                                                          "brewdata": {"decent": {}}})
    assert bd["detail_shape"] == "brewdata_only" and bd["ok"]


def test_canary_flags_missing_timeframe_drift():
    fl = _list([{"id": "x", "updated_at": 1}])
    # a detail with values but NO recognized time-base shape (the original P0 regression)
    fd = lambda cfg, sid: {"id": sid, "updated_at": 1, "data": {"espresso_pressure": [6, 9]}}
    rep = canary.canary_check(list_fetcher=fl, detail_fetcher=fd)
    assert rep["ok"] is False
    assert "detail_no_recognized_shape" in rep["detail_problems"]


def test_canary_flags_list_schema_drift():
    rep = canary.canary_check(list_fetcher=lambda cfg: {"results": []},  # wrong key
                              detail_fetcher=lambda c, s: {})
    assert rep["ok"] is False and "list_missing_data_key" in rep["list_problems"]
