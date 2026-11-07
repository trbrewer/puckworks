# Reproduce the bounded prevalence probe

This is a descriptive public-listing probe, not a model validation or a new
canonical corpus. Data source: **Visualizer**; we collectively thank contributing
users who made their shots public. The owner-attested 2026-07-14 permission from
Miha Rekar covers this authorized research use, not raw redistribution.

## Source and frozen decisions

Base `4c5ebab5df79929813949df7113c21290dde40cc`; PLAN was committed at
`a0d7756` before shot API requests. The live collector was committed at
`bf6aadb`; the aggregate exporter at `1d72f66` was written and synthetic-tested
before inspecting prevalence results. Commit `2a356b9` subsequently added frozen
order checking and corrected audit handling of a missing Retry-After field on a
network-failure receipt, still before prevalence inspection. The live collector
did not change. The source snapshot remains the 465-file,
23,169-logical-record July-15 crawl, authenticated by the same complete file-map
digest as PR #420. Independent salted-token comparison verifies exclusion of
every selected shot from that snapshot.

The current [OpenAPI document](https://github.com/miharekar/visualizer/blob/main/openapi.yaml)
was checked before acquisition (Git blob
`c6c2614300529c74984e7a9632254b239d0e564a`). It documents unauthenticated public
listing, newest-first start-time ordering, the last-month upload restriction,
and 50 requests/minute plus 200/10 minutes per IP. No authentication, `full`
listing, profile download, source link traversal or larger harvest was used.
Schema discovery was separate from shot acquisition: two web documentation
opens failed, one GitHub fetch at a mistaken repository returned 404, and one
correct GitHub OpenAPI fetch succeeded. These retrieved no shots. PR #420 and
its retained source/schema files were also inspected read-only.

## Measurement and limits

The existing normalizer converts achieved pressure to Pa and reported weight to
kg. Only time, achieved pressure and reported weight reach the detector; pressure
goals and all flow channels are excluded. The detector mirrors the source-pinned
`puckworks/empirical/visualizer.py` extraction rules identified in PLAN. It does
not use the predictor's calibration/guard/scoring partition or import its models.
One thousand synthetic traces separately matched the pinned extraction-only
definitions' onset-left-censoring, gap and reset flags. Dynamic compilation
selected only empirical extraction definitions. The shared helper module also
imports model definitions, but no model was evaluated by the parity check.

Delivery onset is the first native weight sample **strictly above 1 g**.
Aligned finite support with nonnegative pressure is split at invalid samples
and gaps **greater than 2 s**. An evaluable trace contains at least one continuous
10 s post-onset block. Within those blocks, pressure is piecewise linear;
strict threshold crossings are interpolated. Equality breaks a stretch.
Duration must be at least 10 s, with a 1e-9 s rounding tolerance. A late event
means a qualifying stretch ends strictly after onset +40 or +60 s; it need not
start after that boundary. `reset_like` is any native adjacent weight decrease
strictly greater than 5 g. The primary analysis excludes these records, and the
inclusive analysis retains their diagnostic indicators without repairing weight.

Intervals are two-sided 95% Clopper–Pearson intervals. The all-selected result is
the fraction with a **confirmed recorded event**; unassessed records are not
certified negatives. The evaluable denominator is conditional on support and
reset status. Finite gaps can conceal events, and incomplete records are not
followed beyond the recorded trace. Left-censored onsets use the recorded first
sample, not a verified physical onset. Pressure node, sensor calibration,
reported-weight origin and continuing positive delivery are not authenticated.
These are telemetry descriptions, not confirmed high-pressure puck extractions.

Binomial intervals do not correct convenience selection, within-user dependence,
pagination movement or measurement error. Profile titles are recorded category
labels, not verified instructions or hardware. The shot projection is
10,000*k/N, using all selected shots; the distinct-user projection is 10,000*u/N.
The latter is linear scaling of observed user diversity, not a prediction of
distinct identities after repeated harvesting. No extrapolation to all espresso
users or enrichment factor for a title-targeted harvest is established.
User counts include only known salted user tokens; missing identity is not
imputed as a new user.

In PREVALENCE.csv, `late_s=0` means any qualifying stretch. Prevalence and interval
bounds are fractions, not percentages. Threshold and late-time rows overlap;
the two denominator rows repeat the same event count with different reference
sets. Do not add them. `WITHHELD` is not zero; `NA` and blank diagnostic fields
are not applicable. Projections use only the all-selected denominator.
PROFILE_COUNTS.csv concerns primary >10-bar events of any
qualifying duration location after onset, not just the >40 s subset.

## Private evidence and replay

Raw responses exist only in memory. Retained private evidence comprises the
salted sample tokens, salted user tokens, per-shot indicators and diagnostic
flags, exact profile-category labels, redacted request ledger, run receipts,
synthetic parity log, and release audit. No raw arrays, original identifiers,
notes or other source free text are retained. No such evidence enters Git.

Set `VIS_STORE` to the original retained crawl directory and `VIS_PRIVATE` to
the external evidence directory. Use the existing production salt in the source
parent directory; never print or copy it into Git. Historical live invocation
(already executed; **not authorization to repeat it**):

```bash
export PYTHONPATH="$PWD" OPENBLAS_NUM_THREADS=1
/usr/bin/time -f 'user_seconds=%U\nsystem_seconds=%S\nelapsed_seconds=%e\nexit_status=%x' \
  -o "$VIS_PRIVATE/probe.time" \
  python -m puckworks.analysis.vis_highpressure_prevalence_001 \
  --root "$VIS_STORE" --private "$VIS_PRIVATE"
```

The collector refuses an existing request ledger and enforces exact listing
parameters, the selected detail allowlist, no repeated details, the 2,000-entry
cap and the 2,020-attempt ceiling. Reproduction uses the saved indicators without
network requests:

```bash
python -m puckworks.analysis.vis_highpressure_prevalence_001_report \
  --root "$VIS_STORE" --private "$VIS_PRIVATE" \
  --output "$VIS_PRIVATE/reproduced"
diff -u docs/research/VIS_HIGHPRESSURE_PREVALENCE_001/PREVALENCE.csv \
  "$VIS_PRIVATE/reproduced/PREVALENCE.csv"
diff -u docs/research/VIS_HIGHPRESSURE_PREVALENCE_001/PROFILE_COUNTS.csv \
  "$VIS_PRIVATE/reproduced/PROFILE_COUNTS.csv"
python -m pytest -q tests/test_vis_highpressure_prevalence_001.py \
  tests/test_visualizer_harvest.py tests/test_visualizer_contract_shapes.py \
  tests/test_visualizer_store.py tests/test_data_privacy.py
ruff check puckworks/ tests/
python tools/readme_governance.py verify
```

The exporter accepts an optional private `--approved-titles` JSON list after
text review. Such approval cannot bypass count, user or linkage suppression.
The release checker refines joint shot-membership and user-membership partitions
for every proposed disclosure. Every nonempty implied shot cell must contain
20 shots and 10 known users; every implied user cell must contain 10 users.
Priority is primary >10-bar late-40, any, late-60, then >11 and >12, inclusive
diagnostics, denominators, quality flags and approved profile categories.
This protects higher-order intersections, complementary subtraction and nested
distinct-user subtraction. Withheld counts also withhold their intervals and
projections. The table does not give the number of withheld title categories.
Offline replay reproduces the aggregate tables from retained indicators. It
cannot recompute the original per-shot classification because raw traces were
not retained. The frozen code, synthetic tests, source identities and private
indicator hashes provide the audit trail for that single live pass.

## Execution receipts

The collector completed exactly once: **2,000 listing entries, two duplicates,
zero missing IDs or snapshot overlaps, 1,998 selected and processed details**.
Every one of the **2,018 attempts** returned HTTP 200: 20 listings and 1,998
details. There were no unavailable shots, retries, refusals, redirects, 429s,
Retry-After headers or backoff. No extra page or replacement was requested.
Requests ran **2026-11-06T14:36:45.127988Z–16:28:48.819268Z**.

Observed rolling maxima were **18/60 s and 180/600 s**. The limiter accumulated
6,244.689 seconds of waiting. Minimum logged UTC start spacing was **3.333304 s**,
29 microseconds below the nominal 3.333333 s interval stated in PLAN; timestamps
are taken after the monotonic limiter and guard work. Thus the nominal interval
is not an exact lower bound on logged wall-clock differences. Published limits
were respected throughout; no server rate-limit response occurred.

The source file-map hash matched before and after collection and again during
export. The independent token join found zero overlap with the snapshot; selected
tokens are unique and the measure records match the frozen sample in order.
The final joint shot/user disclosure audit passed. No category passed the
numerical/linkage checks, so no real profile-title text was approved for release.

Python **3.12.3**, NumPy **2.2.6**, SciPy **1.18.1**, requests **2.34.2**.
The live detector and PLAN stayed unchanged. After completion, the exporter
changed only the display of conditional-denominator projections from WITHHELD
to **NA**: the frozen projection rule uses all selected shots. No count, interval,
privacy decision or measurement changed. Final staging also required explicit LF
CSV line endings; parsed values and withheld cells matched the prior export.
All three export receipts are retained.

| Measured main job | User + system CPU seconds | Wall seconds |
|---|---:|---:|
| Source checks and live collection | 8.86 | 6,724.61 |
| Initial offline export | 1.45 | 1.46 |
| Export with NA display correction | 1.44 | 1.44 |
| Final export with explicit LF line endings | 1.44 | 1.45 |
| **Total** | **13.19 = 0.003664 core-hours** | |

The separate 1,000-trace extraction parity check used 18.67 CPU seconds.
Interactive inspections, title-release screening, additional integrity checks,
tests and hosted CI are excluded from the main-job cost and were not all metered.
This is not a total session CPU estimate.

| Artifact | SHA-256 |
|---|---|
| Frozen PLAN.md | `b01d83a4d4d29d592922ff1d086a49dcc199f8ef210d52cb0e096fe5bee64048` |
| Live collector, unchanged | `c6cfcfbd5eb15586c048037175d40e46825d2bc40fa2589e0b2f2b8a0c114eb9` |
| Final aggregate exporter | `2fffe2389558ffc8dc7827b4786c1889a4b32ded283a05298e200d5003f20feb` |
| Private sample manifest | `3b18ab3f8163b39b4d1ae58b892fece6cf3ac2db47abf8fd628cb59541610f65` |
| Private per-shot indicators | `ad576048af901f3ccd90fe336dfaac40e9216defcbd8a30fe377c71e90a7f6c3` |
| Private request ledger | `fadb4ea86c449091988c5ecdb2f62f988b24d6a8b3a75927b766d91046feddc1` |
| Private run receipt | `46173738705e471c3f4dc5579e757335d42c78d384b1454317f60b5c71ed7236` |
| PREVALENCE.csv | `31bb3aec99a3e4f6aeca59a8beecb80ece27b76b32bec13e94d1af6ac90a5e8f` |
| PROFILE_COUNTS.csv | `8b68150fae71e08175b025f2c8895ced298118f3d0311807967c739cf7d0a82f` |

Verification covers sample and request caps, independent snapshot deduplication,
synthetic stretch boundaries, extraction-flag parity, joint disclosure rules,
output replay and identifier screening: **102 focused tests passed**, along with
the 1,000-trace flag-parity check, actual-data release audit, Ruff and README
governance. Required hosted CI is linked on the PR
at the final head. CI is repository software QA, separate from the probe; no
model or score is used to select or analyze this sample. EWP, the snapshot,
registered components, defaults and canonical generated artifacts are unchanged.
