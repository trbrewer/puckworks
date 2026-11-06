"""Offline, linked-disclosure-controlled exports from private probe indicators."""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import csv
from datetime import datetime
import json
from pathlib import Path
import re

from scipy.stats import beta

from puckworks.analysis.vis_highpressure_prevalence_001 import (
    MAX_REQUESTS, MAX_SHOTS, sha, token, verify_snapshot,
)

WITHHELD = "WITHHELD"


def exact_interval(k, n):
    if not 0 <= k <= n or n == 0:
        raise ValueError("Invalid binomial counts")
    return (0. if k == 0 else float(beta.ppf(.025, k, n - k + 1)),
            1. if k == n else float(beta.ppf(.975, k + 1, n - k)))


def users(rows, indices):
    return {rows[i].get("user_token") for i in indices} - {None, ""}


def partition_safe(rows, memberships):
    """Every induced nonempty shot/user cell must satisfy inherited minima.

    Check joint signatures, including complements. A released user count also
    refines a user partition; overlapping nested events must not expose rare
    users by subtracting their distinct-user totals.
    """
    if not rows:
        return False
    atoms = defaultdict(set)
    for i in range(len(rows)):
        atoms[tuple(i in subset for subset in memberships)].add(i)
    if any(len(cell) < 20 or len(users(rows, cell)) < 10 for cell in atoms.values()):
        return False
    user_sets = [users(rows, subset) for subset in memberships]
    user_atoms = Counter(tuple(u in subset for subset in user_sets)
                         for u in users(rows, range(len(rows))))
    return all(n >= 10 for n in user_atoms.values())


class Disclosure:
    def __init__(self, rows):
        self.rows = rows
        self.memberships = []
        self.released = {}

    def consider(self, name, subset):
        subset = set(subset)
        if not partition_safe(self.rows, [*self.memberships, subset]):
            return False
        self.memberships.append(subset)
        self.released[name] = subset
        return True


def label_safe(label):
    """Fail closed; human approval is additionally required for real titles."""
    return (isinstance(label, str) and 0 < len(label) <= 100
            and not re.search(r"[\r\n\t@]|https?://|www\.|[0-9a-f]{8}-[0-9a-f-]{27,}",
                              label, re.I)
            and not label.startswith(("=", "+", "-", "@")))


def release_tables(rows, approved_titles=()):
    """Greedy predeclared disclosure priority; all rejected values stay hidden."""
    disclosure = Disclosure(rows)
    full = set(range(len(rows)))
    primary = {i for i, r in enumerate(rows)
               if r["status"] == "evaluable" and r.get("reset_like") is False}
    inclusive = {i for i, r in enumerate(rows) if r["status"] == "evaluable"}
    # Protect the decision first, followed by the parent >10 event and late tail.
    keys = [f"gt{p}_late{t}" for p in (10, 11, 12) for t in (40, 0, 60)]
    event_sets = {}
    for group, cohort in (("primary", primary), ("inclusive", inclusive)):
        for key in keys:
            chosen = {i for i in cohort if rows[i]["events"].get(key, False)}
            name = group + ":" + key
            event_sets[name] = chosen
            disclosure.consider(name, chosen)
    # A denominator is itself a disclosure and cannot reveal a rare remainder.
    denominator_safe = {"all_selected": disclosure.consider("all_selected", full),
                        "primary_evaluable": disclosure.consider("primary_evaluable", primary),
                        "inclusive_evaluable": disclosure.consider("inclusive_evaluable", inclusive)}
    output = []
    for group in ("primary", "inclusive"):
        for key in keys:
            name = group + ":" + key
            threshold, late = key.removeprefix("gt").split("_late")
            for denominator, base in (("all_selected", full),
                                      (group + "_evaluable", primary if group == "primary"
                                       else inclusive)):
                released = (name in disclosure.released and denominator_safe[denominator]
                            and bool(base))
                row = dict(metric="sustained_high_pressure", analysis=group,
                           threshold_bar=threshold, minimum_duration_s=10, late_s=late,
                           denominator=denominator, n=len(base) if denominator_safe[denominator]
                           else WITHHELD, events=WITHHELD, qualifying_users=WITHHELD,
                           prevalence=WITHHELD, ci95_lower=WITHHELD, ci95_upper=WITHHELD,
                           projected_shots_per_10000=WITHHELD,
                           projected_users_per_10000=WITHHELD,
                           release_status="RELEASED" if released else WITHHELD)
                if released:
                    k, u, n = len(event_sets[name]), len(users(rows, event_sets[name])), len(base)
                    lo, hi = exact_interval(k, n)
                    row.update(events=k, qualifying_users=u, prevalence=k / n,
                               ci95_lower=lo, ci95_upper=hi)
                    if denominator == "all_selected":
                        row.update(projected_shots_per_10000=k / n * 10000,
                                   projected_users_per_10000=u / n * 10000)
                output.append(row)
    diagnostics = {"evaluable_nonreset": primary, "evaluable_inclusive": inclusive}
    for status in sorted({r["status"] for r in rows}):
        diagnostics["status_" + status] = {i for i, r in enumerate(rows) if r["status"] == status}
    for flag in ("reset_like", "onset_left_censored", "gap", "incomplete_support"):
        diagnostics[flag] = {i for i, r in enumerate(rows) if r.get(flag) is True}
    for name, subset in diagnostics.items():
        released = disclosure.consider("diagnostic:" + name, subset)
        output.append(dict(metric=name, analysis="diagnostic", denominator="all_selected",
                           n=len(rows), events=len(subset) if released else WITHHELD,
                           qualifying_users=len(users(rows, subset)) if released else WITHHELD,
                           release_status="RELEASED" if released else WITHHELD))
    profiles = []
    qualifying = event_sets["primary:gt10_late0"]
    categories = defaultdict(set)
    for i in qualifying:
        categories[rows[i].get("profile_title")].add(i)
    withheld = False
    for title, subset in sorted(categories.items(), key=lambda x: (-len(x[1]), x[0] or "")):
        allowed = title is None or (title in approved_titles and label_safe(title))
        released = allowed and disclosure.consider("profile:" + (title or "MISSING"), subset)
        if released:
            profiles.append(dict(profile_title=title if title is not None else "MISSING_TITLE",
                                 shots=len(subset), distinct_users=len(users(rows, subset)),
                                 release_status="RELEASED"))
        else:
            withheld = True
    if withheld:
        profiles.append(dict(profile_title=WITHHELD, shots=WITHHELD,
                             distinct_users=WITHHELD, release_status=WITHHELD))
    if not profiles:
        # Do not disclose zero qualifying profiles if that parent was withheld.
        profiles.append(dict(profile_title="ALL_TITLES", shots=0 if (
            "primary:gt10_late0" in disclosure.released and not qualifying) else WITHHELD,
            distinct_users=0 if "primary:gt10_late0" in disclosure.released and not qualifying
            else WITHHELD, release_status="RELEASED" if (
                "primary:gt10_late0" in disclosure.released and not qualifying) else WITHHELD))
    assert partition_safe(rows, disclosure.memberships) or not disclosure.memberships
    return output, profiles, disclosure


def write_csv(path, rows):
    fields = list(dict.fromkeys(k for row in rows for k in row))
    with path.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def audit_requests(private, run, sample, rows):
    ledger = [json.loads(s) for s in (private / "REQUESTS.jsonl").read_text().splitlines()]
    assert len(sample["selected"]) <= MAX_SHOTS
    assert len(set(sample["selected"])) == len(sample["selected"])
    assert len(rows) <= len(sample["selected"])
    assert len({r["shot_token"] for r in rows}) == len(rows)
    assert {r["shot_token"] for r in rows} <= set(sample["selected"])
    assert [r["shot_token"] for r in rows] == sample["selected"][:len(rows)]
    assert sample["snapshot_overlap_after_exclusion"] == 0
    assert run["snapshot_unchanged"]
    assert len(ledger) == run["api_attempts"] <= MAX_REQUESTS
    counts = Counter(r["kind"] for r in ledger)
    assert counts["listing"] <= 20 and counts["detail"] <= len(sample["selected"])
    assert sum(counts.values()) == counts["listing"] + counts["detail"]
    starts = [datetime.fromisoformat(r["started_utc"]).timestamp() for r in ledger]
    rolling = {s: max((sum(t - s < x <= t for x in starts) for t in starts), default=0)
               for s in (60, 600)}
    assert rolling[60] <= 18 and rolling[600] <= 180
    frozen = datetime.fromisoformat(sample["frozen_utc"])
    assert all(datetime.fromisoformat(r["started_utc"]) >= frozen
               for r in ledger if r["kind"] == "detail")
    return dict(requests=len(ledger), by_kind=dict(counts),
                statuses=dict(Counter(str(r["status"]) for r in ledger)),
                first_request_utc=ledger[0]["started_utc"] if ledger else None,
                last_response_utc=ledger[-1]["ended_utc"] if ledger else None,
                max_per_60s=rolling[60], max_per_600s=rolling[600],
                minimum_start_spacing_s=min((b - a for a, b in zip(starts, starts[1:])),
                                            default=None),
                retry_after_responses=sum(bool(r.get("retry_after")) for r in ledger))


def export(private, output, root, approved_titles=()):
    run = json.loads((private / "RUN.json").read_text())
    sample = json.loads((private / "SAMPLE.json").read_text())
    existing, snapshot_receipt = verify_snapshot(root)
    salt = (root.parent / ".harvest_salt").read_text().strip()
    assert salt
    old_tokens = {token(salt, s) for s in existing}
    assert not old_tokens & set(sample["selected"])
    rows = [json.loads(s) for s in (private / "MEASURES.jsonl").read_text().splitlines()]
    request_audit = audit_requests(private, run, sample, rows)
    processed = {r["shot_token"] for r in rows}
    rows += [dict(shot_token=t, user_token=None, profile_title=None,
                  status="unrequested_after_stop", events={})
             for t in sample["selected"] if t not in processed]
    prevalence, profiles, disclosure = release_tables(rows, approved_titles)
    output.mkdir(parents=True, exist_ok=True)
    write_csv(output / "PREVALENCE.csv", prevalence)
    write_csv(output / "PROFILE_COUNTS.csv", profiles)
    text = "\n".join((output / f).read_text() for f in ("PREVALENCE.csv", "PROFILE_COUNTS.csv"))
    for row in rows:
        for key in ("shot_token", "user_token"):
            assert not row.get(key) or row[key] not in text
    assert not re.search(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}", text)
    audit = dict(request_audit=request_audit, selected=len(rows),
                 snapshot=snapshot_receipt, independently_checked_snapshot_overlap=0,
                 release_joint_partition_safe=partition_safe(rows, disclosure.memberships),
                 released_cells=len(disclosure.released),
                 private_hashes={f: sha(private / f) for f in
                                 ("SAMPLE.json", "MEASURES.jsonl", "REQUESTS.jsonl", "RUN.json")},
                 output_hashes={f: sha(output / f) for f in ("PREVALENCE.csv", "PROFILE_COUNTS.csv")})
    (private / "REPORT_AUDIT.json").write_text(json.dumps(audit, indent=2) + "\n")
    print(json.dumps(audit, indent=2))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--private", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--approved-titles", type=Path)
    args = parser.parse_args()
    approved = json.loads(args.approved_titles.read_text()) if args.approved_titles else []
    export(args.private, args.output, args.root, approved)


if __name__ == "__main__":
    main()
