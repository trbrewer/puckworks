# PW-VIS-HIGHPRESSURE-PREVALENCE-001

Frozen before shot requests, 2026-11-06. Base:
`4c5ebab5df79929813949df7113c21290dde40cc`. Governance G0: bounded descriptive
acquisition and counting, no accepted corpus, model, score, or default changes.
The owner authorizes this probe and an unmerged draft PR with auto-merge off,
under Miha Rekar's owner-attested 2026-07-14 permission and PR #420 handling.
EWP and the existing snapshot remain read-only. No successor harvest is started.

## Fixed sample and requests

Read the documented unauthenticated `GET /api/shots`, `sort=start_time`,
`items=100`, pages 1–20 once each, stopping at an empty page. Inspect at most
2,000 listing entries. Deduplicate native IDs in returned order, exclude every
ID in the authenticated July-15 snapshot (23,169 logical records), and freeze
the selected salted tokens before fetching details. No extra pages or replacements
for duplicates, overlaps, missing IDs, failed fetches, or rejected telemetry.
Pagination can move during acquisition: this is a recent public convenience
window, not a random sample or a server-side snapshot. The current API restricts
unauthenticated listings to uploads from the last month; brew dates can differ.

Fetch each selected detail once using `GET /api/shots/{id}`; no profile endpoint
is needed. Ceiling: 20 listing + 2,000 detail attempts = 2,020; no retries.
Reuse the shared 18 requests/minute limiter (at least 3.333333 seconds between
starts), below published 50/minute and 200/10-minute limits. Record UTC request
starts/ends, endpoint kind, status, Retry-After and limiter waits, never URLs
containing identifiers. Stop the entire probe on refusal, 401/403, 429, redirect,
network failure, unexpected response/status, or permission uncertainty. Detail
404/410 means unavailable, without replacement. Record documentation retrieval
separately. An existing request ledger prevents implicit live reruns.

The inspected source is `visualizer/hydraulic_timeseries`, including actual
snapshot structure/index and the PR #420 handling code, not catalog metadata
alone. Before/after source-file hashes must match
`6769656c8555d940bf79a2243a784c38b63066d3fe231227628667d251ba4d5b`
(465 files; inventory identity
`f46181ee8c461fab055b73511148dd26888c7c5b3cb1bc908aad6ab9db2bb766`).
Current [API documentation](https://github.com/miharekar/visualizer/blob/main/openapi.yaml)
was checked before requests; the returned Git blob is
`c6c2614300529c74984e7a9632254b239d0e564a`.

## Frozen measurement

Use achieved `espresso_pressure`, reported `espresso_weight`, and shared
`timeframe`, through the existing SI normalizer. Never use pressure goals or
estimated/generic flow to identify a stretch. Reuse the extraction rules from
`puckworks/empirical/visualizer.py` at
`d4386441fbc387c0a83219817dac6f4bce3b94a3`, file SHA-256
`419b15eface9a82fe95efc87acbf025832911b393449b84d88165b027110bb22`:
finite strictly increasing times; aligned pressure and weight; delivery onset
at the first native sample with weight strictly greater than 1 g; finite common
support, nonnegative pressure, gaps at most 2 s; `reset_like` when any adjacent
reported-weight increment is strictly below -5 g. No repair, smoothing or
monotonic-weight enforcement. Primary analysis excludes reset-like records;
an inclusive diagnostic is retained subject to linked suppression.

The empirical module is not on main. Mirror its extraction/support rules in a
task-local detector, without importing its model code. Its calibration/guard/
scoring partition is specific to prediction and is not used for this descriptive
probe. An evaluable record has at least one continuous 10 s post-onset support
block. Invalid support splits blocks; it is never bridged. Short/invalid/no-onset
records remain unassessed, not confirmed negative. Also record left-censored
onsets; late timing is relative to the recorded onset, not a verified physical
onset. Reported weight does not authenticate scale origin or continuing delivery.

Within valid post-onset support, pressure is linear between native samples.
Find connected intervals strictly above 10, 11 and 12 bar. Equality breaks a
stretch; interpolate crossings, never interpolate across invalid support or
gaps. A qualifying interval lasts at least 10 s (1e-9 s numerical tolerance).
For each threshold count any qualifying interval, any ending strictly after
onset +40 s, and any ending strictly after +60 s. The entire 10 s interval need
not lie beyond the late boundary. No minimum total shot duration beyond the
interval itself and no model-based extraction or physical validation claim.

## Denominators, release and decision

Keep per-shot status/flags, nine indicators, salted shot/user tokens and exact
recorded profile titles privately outside Git. Process raw responses in memory
only; retain no raw arrays, raw identifiers, notes or other free text. A profile
title is used only as a category label; no interpretation, fuzzy merging or
hardware inference. Exact titles may enter the public category table only after
20-shot/10-known-distinct-user and text/linkage screening. Missing titles are a
separate category. Identifying/unsafe labels are withheld, never copied into Git.

Report confirmed-event prevalence k/N for all selected shots (unassessed records
are not confirmed positives, not biological negatives), and k/n among evaluable
non-reset records; give denominators and evaluability/reset diagnostics when
releasable. Use two-sided 95% Clopper–Pearson exact binomial intervals. These
intervals describe a binomial reference, not selection or within-user dependence;
do not claim population-representative confidence coverage.

All nonempty released cells require at least 20 shots and 10 known users.
Apply complementary suppression and linked suppression across thresholds, late
boundaries, reset sensitivity, denominators, profiles and projections. Check
the induced joint partition, not just individual marginal cells; remove lower
priority disclosures if any implied nonempty cell fails the minima. Zero can be
released within a safe parent; a small nonzero count cannot. Withheld counts,
intervals, user totals and projections stay withheld everywhere, including prose.
No count of withheld profile categories or recoverable residual is published.

For released events, project qualifying shots as 10,000*k/N and qualifying
distinct users as 10,000*u/N. Label both as linear projections from this sample;
user projection assumes the same user diversity per shot and cannot predict
repeat-user saturation. Show the observed qualifying-user count only when safe.
Project all >10-bar events and the >40 s subset where release rules allow.
The target decision concerns the >10-bar, >40 s subset: recommend targeting only
if this cell clears the existing release minima; otherwise say “too rare to
target” at this probe's resolution, not universal absence. If releasable, end
SUMMARY with “a targeted harvest could yield about N qualifying shots per 10,000”.

## Verification and outputs

Commit this PLAN before requests. Unit-test strict thresholds, interpolation,
10/40/60 s boundaries, irregular sampling, gaps, invalid channels, reset flags,
deduplication, sample/request caps and linked suppression using synthetic data.
Check actual sample membership against the unchanged snapshot, request counts,
and every committed output against disclosure rules. Required hosted CI is
software QA only; the probe runs no model, fitting or score. Publish SUMMARY.md,
PREVALENCE.csv, PROFILE_COUNTS.csv and REPRODUCE.md here, plus task-local code and
focused tests. Record source/plan/code/evidence hashes, UTC dates, request/rate
behaviour and measured main-job CPU cost. No raw data enters Git.

Data source: Visualizer. We collectively thank contributing users who made their
shots public. Research permission does not grant raw redistribution or imply
endorsement.
