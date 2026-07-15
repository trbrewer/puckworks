"""Visualizer live-contract canary (WP0.6 / WP3.1 live-contract lane).

Fetches exactly ONE list page + ONE shot detail and asserts the API still emits the schema
SHAPE the normalizer expects (top-level or nested `timeframe` + `data`, or `brewdata`). It
RETAINS NOTHING — no store write, no normalization, no user hashing — so it is safe to run on
a schedule as a drift alarm. It never probes or guesses ids: it reads the id the list returns.

Run live ONLY from the secret-gated live-contract workflow:
    python -m puckworks.lib.visualizer_canary
"""
import sys

from puckworks.lib.visualizer_harvest import (
    HarvestConfig, _RateLimiter, _get, _requests,
)


def _real_list(cfg):
    session = _requests().Session()
    return _get(cfg, session, _RateLimiter(cfg.max_req_per_min), "/shots", params={"page": 1})


def _real_detail(cfg, shot_id):
    session = _requests().Session()
    return _get(cfg, session, _RateLimiter(cfg.max_req_per_min), "/shots/%s" % shot_id)


def _list_shape_problems(page):
    if not isinstance(page, dict) or "data" not in page:
        return ["list_missing_data_key"]
    items = page["data"]
    if not isinstance(items, list):
        return ["list_data_not_array"]
    if not items:
        return ["list_empty"]
    first = items[0]
    return ["list_item_missing_%s" % k for k in ("id", "updated_at") if k not in first]


def _detail_shape(detail):
    """Return (problems, recognized_shape). Recognizes the shapes normalize_shot handles."""
    if not isinstance(detail, dict):
        return ["detail_not_object"], None
    problems = ["detail_missing_%s" % k for k in ("id", "updated_at") if k not in detail]
    if isinstance(detail.get("timeframe"), list):
        shape = "chart_data_toplevel"
    elif isinstance((detail.get("data") or {}).get("timeframe"), list):
        shape = "chart_data_nested"
    elif "brewdata" in detail:
        shape = "brewdata_only"
    else:
        shape = None
        problems.append("detail_no_recognized_shape")
    return problems, shape


def canary_check(cfg=None, list_fetcher=_real_list, detail_fetcher=_real_detail):
    """One list page + one detail; assert schema shape; retain nothing. Returns a report."""
    cfg = cfg or HarvestConfig(salt="canary-no-retention")   # salt unused: nothing is hashed
    page = list_fetcher(cfg)
    list_problems = _list_shape_problems(page)
    sid, detail_problems, shape = None, [], None
    if isinstance(page, dict) and isinstance(page.get("data"), list) and page["data"]:
        sid = page["data"][0].get("id")
    if sid is not None:
        detail_problems, shape = _detail_shape(detail_fetcher(cfg, sid))
    else:
        detail_problems = ["no_shot_id_to_probe"]
    problems = list_problems + detail_problems
    return {
        "ok": not problems,
        "detail_shape": shape,
        "n_requests": 2 if sid is not None else 1,
        "list_problems": list_problems,
        "detail_problems": detail_problems,
        "note": "schema-shape check only; NO user data retained or stored",
    }


def main(argv=None):   # pragma: no cover
    import json
    rep = canary_check()
    print(json.dumps(rep, indent=2))
    return 0 if rep["ok"] else 1


if __name__ == "__main__":   # pragma: no cover
    sys.exit(main())
