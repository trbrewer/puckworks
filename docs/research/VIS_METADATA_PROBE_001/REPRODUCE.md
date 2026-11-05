# Reproduction and request accounting

This is a metadata probe, not a hydraulic analysis. Raw responses, raw shot/user
identifiers, free text, profile values, array samples and user outcomes were not
persisted. Private retained evidence comprises salted sample tokens, field paths
and value types, controlled source categories, request-status logs and aggregate
disclosure checks. No original snapshot file or EWP file is changed.

## Frozen design and identities

Puckworks main/base: `4c5ebab5df79929813949df7113c21290dde40cc`.
The initial plan was committed at `126ed97`, and the documented-profile-route
amendment at `94a4e61`, both before the first Visualizer API request. Probe code
and its initial nine synthetic checks were committed at `4f080b6` before live
execution. Source-code documentation requests preceded API requests and are
accounted separately. No result motivated the sample or endpoint amendment.

Sample A was frozen at **2026-11-05T15:14:21Z**, seed **20261105**, with 150
Beanconqueror-parser and 150 unresolved shots. Its private salted-token manifest
SHA-256 is `869d1fb7e2ca46a4a79db858cfa6e33ae28a17839815d908c47e8db18d1fa8ef`.
The equal stratum allocation is a format probe, not a representative corpus
draw. Sample B is the first up-to-300 unique IDs from three 100-item listing
pages ordered by start time. Duplicates do not authorize another page. The
private B token manifest precedes every B detail request. Direct IDs exist only
in process memory; no original IDs are written by this probe.

The July-15 source is authenticated through X1's reader: all 465 files match the
owner inventory, 23,169 logical records, no revisions or timestamp conflicts.
Source file-map SHA-256:
`6769656c8555d940bf79a2243a784c38b63066d3fe231227628667d251ba4d5b`;
inventory content identity:
`f46181ee8c461fab055b73511148dd26888c7c5b3cb1bc908aad6ab9db2bb766`.
This is the same source as [#419's qualification table](https://github.com/trbrewer/puckworks/blob/90c7d6fea8ade41891f83ab96d47b675bb18d3e3/docs/research/VIS_TURNOVER_001/QUALIFICATION.csv).

## Commands

Python 3.12.3; existing Puckworks development environment plus the optional
`requests` dependency. Set `VIS_STORE` to the retained crawl directory,
`VIS_INVENTORY` to its owner inventory, and `VIS_PRIVATE` to an external evidence
directory. The production salt is read from the existing parent store without
printing or copying it. Local locators and salts are not published.

Historical live sequence (already executed; **not an instruction to repeat the
probe or start another harvest**):

```bash
export PYTHONPATH="$PWD" OPENBLAS_NUM_THREADS=1
mkdir -p "$VIS_PRIVATE"
python -m puckworks.analysis.vis_metadata_probe_001 freeze \
  --root "$VIS_STORE" --inventory "$VIS_INVENTORY" --private "$VIS_PRIVATE"
# PLAN and the documented-profile amendment were committed before this step.
/usr/bin/time -f 'user_seconds=%U\nsystem_seconds=%S\nelapsed_seconds=%e\nexit_status=%x' \
  -o "$VIS_PRIVATE/probe.time" \
  python -m puckworks.analysis.vis_metadata_probe_001 probe \
  --root "$VIS_STORE" --inventory "$VIS_INVENTORY" --private "$VIS_PRIVATE"
```

The probe rejects an existing request ledger, so accidental live replay cannot
silently double the sample or request budget. A future live probe would need
separate owner authorization and would observe a different API state. Exact
offline reproduction uses the retained private field-type evidence:

```bash
python -m puckworks.analysis.vis_metadata_probe_001_report \
  --root "$VIS_STORE" --inventory "$VIS_INVENTORY" --private "$VIS_PRIVATE" \
  --output "$VIS_PRIVATE/reproduced"
diff -u docs/research/VIS_METADATA_PROBE_001/FIELD_AVAILABILITY.csv \
  "$VIS_PRIVATE/reproduced/FIELD_AVAILABILITY.csv"
python -m pytest -q tests/test_vis_metadata_probe_001.py \
  tests/test_visualizer_harvest.py tests/test_visualizer_contract_shapes.py \
  tests/test_visualizer_store.py tests/test_data_privacy.py
ruff check puckworks/ tests/
python tools/readme_governance.py verify
```

## Field meanings and disclosure

The CSV counts allowlisted native paths with non-null types as structurally
present, counts null separately, and distinguishes missing keys in returned
payloads. Empty containers are not certified as informative. `PROFILE.` marks
the supplemental JSON endpoint. Profiles not returned/requested are not counted
as missing fields in an inspected profile. No frame values are used to assign
stages, infer controller activity or compute a pressure-flow quantity.

`privacy_dropped_now` applies the inherited stripping policy to current
responses; it does not by itself establish a historical loss. The historical
profile-title loss is confirmed only where the saved normalized
`context.profile_present` flag supplies that evidence. Other newly present paths
with no historical authority remain source-change/loss UNKNOWN. Nested parser
provenance was retained in Bronze even when not carried into the normalized
integration label. [Source interpretation](SOURCE_INTERPRETATION.md) explains
the measured/estimated-flow distinction and serializer routes.

Existing 20-shot/10-distinct-user minima are applied to each published format
group and field cell, including complementary suppression. The complement test
conservatively requires ten users outside the present-cell user set. A full safe
format partition is published, or sample-level `ALL` rows, never both. Unsafe
within-row and nested-field differences trigger linked suppression. Related
profile counts are suppressed across both arms when needed to prevent recovery
from the required global profile-request total. Unsafe distributions remain
private. Request-status totals are operational bookkeeping, not a published
user/configuration stratum. No per-shot keys or context values enter Git.

Review identified a capture defect: numeric types do not distinguish negative-one,
zero and positive goals, and the collector omitted limiter `value`/`range`, exit
`condition`/`value`, and legacy `advanced_shot`/`settings_profile_type` paths.
These are explicitly **NOT_CAPTURED**, never missing at source. The original
plan's stronger sentinel distinction was not achieved. The live collector was
kept fixed; no extra requests or altered sample were used to repair this loss.
Consequently this probe cannot establish profile/control completeness. Generic
flow/weight lineage and hardware also remain unqualified. Full #419 window/group
qualification is unexecuted; zero established qualifications is distinct from
zero actually qualifying shots. Their actual qualification remains UNKNOWN.

## Execution receipts

The run completed without retries, refusals, unavailable responses or 429s.
Sample B contains 299 unique IDs from 300 listing entries; A/B overlap is zero.
All 599 detail responses and all 427 advertised JSON-profile responses returned
HTTP 200. There were exactly **1,029 API attempts**: 3 listing + 599 detail + 427
profile, below the amended 1,203 ceiling. No extra page or replacement was used.
The first request began **2026-11-05T15:24:25.999505Z**; the final response ended
**2026-11-05T16:21:38.794037Z**. Minimum observed start spacing was
3.333335 seconds; rolling maxima were 18 requests/60 seconds and 180/600 seconds,
below the documented 50/200 limits. The shared limiter recorded 3,169.560 seconds
of waiting. No Retry-After header or backoff was encountered.

Source discovery was separate: 19 GitHub file-fetch calls (14 successful,
including one repeated serializer read; five initial wrong-path 404s), one
GitHub code search, one `git ls-remote`, and two browser documentation opens.
These retrieved public source/schema documentation, no additional shots. All
13 unique retained source files match their Git blobs at the pinned revision;
the export helper's extra trailing newline was removed after exact blob checks.

| Measured main job | User + system CPU seconds | Wall seconds |
|---|---:|---:|
| Source authentication and sample A freeze | 8.75 | 8.77 |
| Failed local preflight: missing optional `requests`; zero API requests | 16.06 | 16.08 |
| Complete bounded live probe | 21.45 | 3,449.07 |
| Offline aggregate export and source reauthentication | 17.98 | 18.02 |
| **Total** | **64.24 = 0.017844 core-hours** | |

All failed-attempt logs/timers are retained. Interactive progress inspections,
source retrieval, environment setup, tests, review and hosted CI are excluded
and were not separately CPU-metered; this is measured main-job cost, not total
interactive-session CPU. No model evaluation or optimizer ran.

Retained private evidence: SAMPLE_A.json, SAMPLE_B.json, REQUESTS.jsonl,
FIELDS.jsonl, RUN.json, REPORT_AUDIT.json, exact source copies/hashes and timers.
The final export has 250 field rows, including explicit NOT_CAPTURED entries.
Actual-data checks confirm sample ordering/freeze before requests, 599 unique
tokens, the 1,203 ceiling, 427 conditional profile requests, unchanged source
identity and absence of private tokens/UUIDs from the public bundle.

| Artifact | SHA-256 |
|---|---|
| Amended PLAN.md | `969472dc281750eb77bc43818c784b57f884b64517ced86683151714d2b5127a` |
| Probe code, unchanged during live execution | `534f2e460b572227a10209722d0246c669d04547cf0d432b6f6dd5427d76dfa2` |
| Aggregate report code | `bedffe161c08f4e10ba91891deaccdfa41d28b83dfdd77c63848a6095708e88b` |
| Private sample B manifest | `48d33b9f8b6e9fc1cb468258664b3f3aca6c0cf785cfe19e098fc1c6407f5de6` |
| Private per-shot field/type evidence | `d745ab6774d5a9e7aaf3c5562eab3a0405059699d3b6a45d6ecb5dd3001b97be` |
| Private request ledger | `6917541ed1a88da781aadf28b520e0272f542b7ee58dbdf1e9441bd2c1219328` |

Local verification includes focused synthetic/privacy/harvester checks, Ruff
and README governance. The independent review record and required hosted CI at
the final head are linked in the PR; no scientific claim is upgraded by CI.

Data source: **Visualizer**. We collectively thank users who made their shots
public. Permission is the owner-attested 2026-07-14 research-use grant; it does
not grant raw redistribution or imply endorsement of this probe.
