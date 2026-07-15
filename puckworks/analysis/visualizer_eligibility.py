"""Shared eligibility engine for the corpus atlas (WP1.1).

Named eligibility PROFILES replace figure-specific filters, so every analysis (census,
pressure atlas, ...) uses the same inclusion logic and reports the same exclusion flow.
Each profile is a function ``shot -> reason_or_None`` (None means included). Reasons are
short, stable tokens so exclusion tables are countable and comparable across analyses.
"""
from collections import Counter


def _hy(shot):
    return shot.get("hydraulic") or {}


def _has_channel(shot, name):
    s = _hy(shot).get(name)
    return bool(s) and any(x is not None for x in s)


def _hydraulic_valid(shot):
    qc = shot.get("qc") or {}
    if not qc.get("time_present"):
        return "no_time_base"
    if (shot.get("n_samples") or 0) < 2:
        return "too_few_samples"
    if qc.get("time_monotonic") is False:
        return "non_monotonic_time"
    if not any(_has_channel(shot, c) for c in
               ("pressure__Pa", "mass_flow_from_scale__kg_per_s", "weight__kg")):
        return "no_hydraulic_channel"
    return None


def _pressure_tracking(shot):
    r = _hydraulic_valid(shot)
    if r:
        return r
    if not _has_channel(shot, "pressure__Pa"):
        return "no_pressure"
    if not _has_channel(shot, "pressure_goal__Pa"):
        return "no_pressure_goal"
    return None


def _mass_flow_tracking(shot):
    r = _hydraulic_valid(shot)
    if r:
        return r
    if not _has_channel(shot, "mass_flow_from_scale__kg_per_s"):
        return "no_scale_mass_flow"
    return None


def _exploratory_proxy_flow(shot):
    # deliberately loose: this profile is for exploratory-only proxy-flow work and must never
    # be pooled with mass_flow_tracking (the channel is unit-ambiguous, canonical_unit=None).
    if not _has_channel(shot, "flow_reported__native"):
        return "no_reported_flow"
    return None


def _outcome_descriptive_only(shot):
    oc = shot.get("outcomes") or {}
    has = (oc.get("tds__fraction") is not None or oc.get("ey__fraction") is not None
           or any(v is not None for v in (oc.get("sensory") or {}).values()))
    return None if has else "no_outcome"


PROFILES = {
    "census_all": lambda shot: None,
    "hydraulic_valid": _hydraulic_valid,
    "pressure_tracking_valid": _pressure_tracking,
    "mass_flow_tracking_valid": _mass_flow_tracking,
    "exploratory_proxy_flow": _exploratory_proxy_flow,
    "outcome_descriptive_only": _outcome_descriptive_only,
}


def is_included(shot, profile):
    """Return None if `shot` is included under `profile`, else a short exclusion reason."""
    if profile not in PROFILES:
        raise KeyError("unknown eligibility profile %r; known: %r"
                       % (profile, sorted(PROFILES)))
    return PROFILES[profile](shot)


def eligibility_report(snapshot, profile):
    """Run `profile` over `snapshot.latest()` and report inclusion, the exclusion flow (by
    reason), source/machine concentration of included shots, and repeated-user concentration
    (so a few prolific contributors can't masquerade as population breadth, WP1.2)."""
    fn = PROFILES[profile]
    included = 0
    excl = Counter()
    machines, sources, users = Counter(), Counter(), Counter()
    for shot in snapshot.latest():
        reason = fn(shot)
        if reason is None:
            included += 1
            ctx = shot.get("context") or {}
            machines[ctx.get("machine") or "unknown"] += 1
            sources[ctx.get("integration_source") or "unknown"] += 1
            hu = shot.get("hashed_user")
            if hu:
                users[hu] += 1
        else:
            excl[reason] += 1
    return {
        "profile": profile,
        "n_included": included,
        "n_excluded": sum(excl.values()),
        "exclusion_reasons": dict(excl),
        "machine_mix": dict(machines),
        "source_mix": dict(sources),
        "n_unique_users_included": len(users),
        "max_shots_per_user": max(users.values()) if users else 0,
    }
