# PW-VIS-METADATA-PROBE-001 — frozen sample and request boundary

2026-11-05. Fetched main/base: `4c5ebab5df79929813949df7113c21290dde40cc`.
Isolated branch `pw-vis-metadata-probe-001`; EWP read-only. The owner explicitly
authorizes this metadata-only API probe under the existing 2026-07-14 permission
and execution through an open, unmerged draft PR with auto-merge disabled.

Question: can documented public shot responses supply the machine, parser,
profile/frame/stage/controller and measured-scale lineage missing in #419?
No hydraulic quantities, segmentation, grouping contrasts or turnover will run.

## Sources and sample fixed before requests

FILES_INSPECTED: Visualizer card/data guide, data-use/publication guidance,
harvester, X1 and native reconciliation, and #419 QUALIFICATION.csv at
`90c7d6fea8ade41891f83ab96d47b675bb18d3e3`. The retained snapshot has 23,169
logical records: 1,004 explicitly identified Beanconqueror parser records and
22,165 unresolved formats. No machine identity is inferred from a parser.

**A: 300 existing shots.** Reauthenticate the 465-file July-15 snapshot against
the owner inventory. Join canonical `(id, updated_at)` keys to Bronze explicit
parser fields. Draw **150 per existing format stratum**, without replacement,
using Python `random.Random(20261105)`: sorted native IDs within strata, strata
in order `VISUALIZER_BEANCONQUEROR`, `UNRESOLVED`. This deliberately balances
the rare known format; pooled A shares are sample shares, not corpus estimates.
Freeze an external manifest of salted shot tokens and stratum labels before
any network request; native IDs exist in memory only and can be regenerated
from the unchanged snapshot. No unavailable shot is replaced.

**B: up to 300 recent public shots.** Use the documented listing endpoint's
newest-first `sort=start_time`, `items=100`, pages 1–3, exactly once each until
empty. Keep the first 300 unique listed IDs in returned order; skip duplicates
without querying extra pages. Freeze salted tokens before B detail requests.
This is the recent-public listing at request time, not a representative sample
or a guarantee of physically recent brewing. Record listing dates and overlap
with A. A/B overlap uses one cached detail response and counts in both samples.

## Requests and privacy

Use the existing harvester's public listing/detail functions, salted-user
handling, privacy stripping and shared **18 requests/minute** limiter (within
50/min and 200/10 min). At most 600 distinct shot-detail requests plus 3 listing
requests, plus at most one `GET /shots/{id}/profile?format=json` per selected
shot whose detail response advertises `profile_url`. A wrapper counts every
HTTP attempt, including failures/retries, and enforces a total **1,203
API-attempt ceiling**. No extra shots, other endpoints, tokens, authentication
or paid access. Fetch B's listing first, then A and B details/profiles.
401/403, an access/permission refusal, or questionable permission scope stops
the entire probe. A shot-specific 404/410 is unavailable, not an absent field;
do not replace it. A 429 stops the probe and is reported with Retry-After;
transient network/5xx retries remain within the ceiling. Never work around a
refusal. Published documentation/source-code retrieval is recorded separately
from shot/API requests and cannot retrieve additional shot records.

Pre-request amendment: initial commit `126ed97` allowed detail endpoints only
(603 attempts). Public schema v1.21.0 at Visualizer source
`9ef3d0de47b438fb55a44aed80e646b1deef37d8` documents the separate JSON profile
endpoint and its availability flag; the serializer omits native structures from
chart-data shot responses. This amendment includes that relevant metadata route
before any Visualizer API request. Sample A was already frozen unchanged at
2026-11-05T15:14:21Z, manifest digest
`869d1fb7e2ca46a4a79db858cfa6e33ae28a17839815d908c47e8db18d1fa8ef`.
No shot response or field-availability outcome motivated this change. A profile
422 means no profile, not an access refusal; do not request its CSV telemetry.

Raw responses are processed in memory only. Reuse `_strip_pii` and `hash_user`,
then retain only allowlisted field paths, value **types**, presence/ambiguity
flags, controlled format/machine categories and salted tokens in private files
outside Git. Do not retain free text, raw identifiers, URLs linking to shots,
raw arrays, profile titles, coffee/grinder values or user outcomes. No existing
snapshot file is written. Raw identifiers in exception URLs must be redacted.

## Interpretation fixed before results

Inspect the current documented schema and public parser source at a recorded
revision. A public source revision is a candidate for deployed semantics, not
proof of deployment. Interpret source-specific native fields; generic normalized
channel names alone never establish scale origin, active brewing, control mode
or inactive flow limits. Missing/null/zero/-1 goals remain distinct. Distinguish
user-reported machine labels, software-written identity and verified hardware.

For each shot record present/absent/ambiguous/unavailable, native field path and
value type for machine, parser, profile identity/structure, pressure/flow
priority and limits, stage markers and measured/estimated scale-flow lineage.
Also record metadata availability required for #419 matching: salted user,
grinder/setting, dose, coffee/roast and preceding profile/temperature history.
No values or hydraulic comparisons are needed. Full #419 qualification includes
window-level flow/weight consistency and limiter inactivity plus matched groups;
this probe can report metadata sufficiency but cannot certify those unexecuted
conditions. Keep full qualification UNKNOWN unless an explicit missing field
already makes it impossible; never promote metadata sufficiency to full success.

For A compare the same paths with stored privacy-filtered Bronze and retained
normalized fields. Separate absent now, preserved, demonstrably privacy-dropped,
not carried into normalized representation, and source-changed/unknown. A field
newly present now is not proof that the old harvester dropped it. Classify
historical loss only where stored/source code evidence supports that attribution.

Publish aggregate counts by A/B, format and machine where the existing 20-shot/
10-user minima and complementary/linkage rules permit; suppress unsafe cells.
Report denominators, unavailable responses and ALL-requirement counts without
treating unknown as false or a failed fetch as an absent field. Credit Visualizer
and contributors collectively. The conclusion is bounded to this probe; do not
claim universal absence from a limited sample or failed API access.

## Delivery

Commit this plan before any request. Output SUMMARY.md, FIELD_AVAILABILITY.csv
and REPRODUCE.md with request ledger totals/dates, rate-limit behavior, snapshot
and source/code hashes, core-hours and limitations. Retain detailed evidence
privately. Focused synthetic tests cover sampling/order, request ceiling,
privacy and field semantics. Run required CI. A fresh read-only reviewer checks
design, measured/estimated interpretation, privacy and final claims. No larger
harvest or turnover successor is authorized.
