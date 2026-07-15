"""P0 corpus census + quality atlas (WP1.2).

Descriptive, source-stratified counts over a CorpusSnapshot: record/shot counts, source and
machine mix, channel availability, time-base / sampling quality, duration and telemetry-length
distributions, outcome coverage (kept SEPARATE from hydraulics), QC pass/fail by source
family, and user/profile concentration with a one-shot-per-user sensitivity summary so a few
prolific contributors cannot masquerade as population breadth.
"""
from collections import Counter, defaultdict

from puckworks.data import visualizer_store as vs
from puckworks.analysis import histogram, product_envelope
from puckworks.analysis.visualizer_eligibility import _has_channel

_DURATION_EDGES = [0, 15, 20, 25, 30, 35, 40, 60, 1e9]
_NSAMPLE_EDGES = [0, 50, 100, 200, 400, 800, 1600, 1e9]


def _first_per_user(snapshot):
    """Yield one shot per hashed_user (the first seen), for the concentration sensitivity."""
    seen = set()
    for shot in snapshot.latest():
        hu = shot.get("hashed_user")
        if hu is None:
            yield shot                      # unhashed shots each count once
        elif hu not in seen:
            seen.add(hu)
            yield shot


def _census_counts(shots):
    """Core descriptive counts over an iterable of latest-version shots."""
    n = 0
    machines, sources = Counter(), Counter()
    channel_present = Counter()
    outcome = Counter()
    qc_by_source = defaultdict(lambda: Counter())
    durations, n_samples = [], []
    users = Counter()
    for shot in shots:
        n += 1
        ctx = shot.get("context") or {}
        m = ctx.get("machine") or "unknown"
        src = ctx.get("integration_source") or "unknown"
        machines[m] += 1
        sources[src] += 1
        for ch in vs.MEASUREMENT_DICTIONARY:
            if _has_channel(shot, ch):
                channel_present[ch] += 1
        oc = shot.get("outcomes") or {}
        if oc.get("tds__fraction") is not None:
            outcome["tds"] += 1
        if oc.get("ey__fraction") is not None:
            outcome["ey"] += 1
        if any(v is not None for v in (oc.get("sensory") or {}).values()):
            outcome["sensory"] += 1
        qc = shot.get("qc") or {}
        mono = qc.get("time_monotonic")
        qc_by_source[src]["time_ok" if mono is True else
                          ("time_bad" if mono is False else "time_insufficient")] += 1
        dur = ctx.get("duration__s")
        if isinstance(dur, (int, float)):
            durations.append(dur)
        n_samples.append(shot.get("n_samples") or 0)
        hu = shot.get("hashed_user")
        if hu:
            users[hu] += 1
    return {
        "n_shots": n,
        "machine_mix": dict(machines),
        "source_mix": dict(sources),
        "channel_availability": dict(channel_present),
        "outcome_coverage": dict(outcome),          # SEPARATE from hydraulics by construction
        "qc_by_source_family": {k: dict(v) for k, v in qc_by_source.items()},
        "duration_hist_s": histogram(durations, _DURATION_EDGES),
        "n_samples_hist": histogram(n_samples, _NSAMPLE_EDGES),
        "n_unique_users": len(users),
        "max_shots_per_user": max(users.values()) if users else 0,
    }


def corpus_census(snapshot):
    """Full P0 census product: all-shots counts, integrity diagnostics, and a one-shot-per-user
    sensitivity block. Returns a deterministic product envelope."""
    integrity = snapshot.integrity_stats()
    results = {
        "integrity": integrity,
        "all_shots": _census_counts(snapshot.latest()),
        "one_shot_per_user": _census_counts(_first_per_user(snapshot)),
    }
    return product_envelope(
        snapshot, "corpus_census", results,
        config={"channels": sorted(vs.MEASUREMENT_DICTIONARY)},
        metric_defs={
            "one_shot_per_user": "counts recomputed keeping the first shot per hashed_user, "
                                 "to expose prolific-contributor concentration",
            "outcome_coverage": "user-entered TDS/EY/sensory presence — a SEPARATE evidence "
                                "tier, never merged with hydraulic telemetry",
        })
