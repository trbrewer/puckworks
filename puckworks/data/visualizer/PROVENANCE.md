# visualizer.coffee — data intake provenance (ROADMAP 0.13)

**Data-only intake.** No registry component, no physics gate — this is a
Phase-0 corpus plus an ingestion tool (`puckworks/lib/visualizer_harvest.py`).
Card: `docs/cards/visualizer_coffee.md` (verdict `data-only`). Manifest rows:
`visualizer/hydraulic_timeseries` and `visualizer/user_outcomes`
(two rows — the two evidence tiers are kept SEPARATE per ROADMAP §0).

## Source
- **API:** visualizer.coffee public REST API, `openapi.yaml` **v1.13.0**, base
  `https://visualizer.coffee/api`.
- **Scope:** PUBLIC read only (no auth). Endpoints used: `GET /shots`
  (paginated summaries `{id, clock, updated_at}`) and `GET /shots/{id}` (full
  record, one request each). We do **not** use any authenticated/write endpoint.
- **Harvest date range:** recorded per run in `raw/_cursor.json`
  (`last_updated_at`) and in the per-run summary printed by the CLI. The corpus
  is a moving target (user-contributed, continuously added).

## License / redistribution posture
The visualizer application is MIT (app code only). The shot corpus is
user-contributed and has no open data license, **but research use of the public
shots via the documented API is AUTHORIZED by Miha Rekar** (miha@visualizer.coffee,
email **2026-07-14**), on these conditions:

- **Access:** through the documented public API, **within the published rate
  limits** (the API enforces them via 429; no separate bulk export needed).
  Pagination + backoff + resume cursor as implemented here are explicitly
  sanctioned. **Published limits (API docs):** 50 req/min AND **200 req / 10 min** per
  client IP (unauthenticated). The **10-minute window is the binding sustained cap**
  (=20 req/min average), so a long crawl must average ≤20/min regardless of the 50/min
  burst allowance. Our harvester default is **18 req/min** (180 per 10-min window,
  evenly spaced → the 10-min window is respected inherently) with exponential backoff.
- **ATTRIBUTION (required in any published work):** clearly credit **Visualizer as
  the data source** and **collectively acknowledge the users who make their shots
  public** — *not* individually by name, but as a group whose contributions make
  the research possible. **This condition binds Paper 3 and any other output that
  uses this corpus** — see `docs/paper3_resource/PAPER_3_PUCKWORKS_OUTLINE.md`.
- **Share-back:** Miha is interested in seeing findings; share results back with
  the community where possible.
- The **raw harvested corpus is still NEVER committed** — `raw/shard_*.jsonl.gz`,
  `raw/_index.csv`, `raw/_cursor.json`, and the production salt `raw/../.harvest_salt`
  are gitignored (the grant is to *use* the public data via the API, not a grant to
  *redistribute* the user corpus from our repo; keeping it out also respects user
  privacy). Only the harvester code, offline fixtures, this `PROVENANCE.md`, the two
  MANIFEST rows, the data-only card, and the small DERIVED `aggregate_stats.csv` are
  tracked.
- **Production salt:** `puckworks/data/visualizer/.harvest_salt` (gitignored) holds a
  per-machine random salt so user hashes are not reproducible from the repo; keep it
  stable so incremental runs dedup correctly.

## Privacy (applied at ingest by `normalize_shot`)
Dropped and never stored: `user_name`, `user_id`, `avatar_url`, `barista`, and
all free-text (`espresso_notes`, `bean_notes`, `private_notes`, `notes`). The
only user linkage kept is a **salted one-way hash of `user_id`** (16 hex chars),
for dedup and selection-bias accounting. The salt defaults to a committed DEV
value with a loud warning; production harvests must set `PUCKWORKS_VIS_SALT`.

## Two evidence tiers (never merged into one "shot" record)
1. **hydraulic** — machine-logged pressure/flow/weight/temperature time series.
   *Reference-strength POPULATION data*: measured but uncontrolled and
   self-selected (public showcase/diagnostic skew). Serves an ecological
   cross-machine P–Q / flow envelope (G3 / P2 / P6). Commanded (`*_goal`) and
   achieved channels are separated; the pressure node identity is per §5.9.
2. **outcomes** — user-entered TDS / EY / sensory sliders. *NOT groundtruth*:
   uncalibrated across users, unknown refractometer / sampling protocol, sensory
   sliders not inter-rater calibrated. **Never gates an extraction outcome** —
   hypothesis / cross-reference only (contrast the controlled Schmieder /
   Angeloni / Egidi sets).

## `normalize_shot` field map (raw → tidy; units in → out)
SI is asserted at the store boundary; raw units are recorded per channel in the
tidy record's `units` block; missing/off-unit fields are **flagged**, not
silently coerced (CLAUDE.md rule 7).

### hydraulic tier — series on the shared `data.timeframe` vector
| raw `data.*` key | tidy key | raw unit | stored unit |
|---|---|---|---|
| timeframe | time__s | s | s |
| espresso_pressure | pressure__Pa | bar | Pa |
| espresso_pressure_goal | pressure_goal__Pa | bar | Pa |
| espresso_flow | flow_reported__native* | native | *(none — native)* |
| espresso_flow_weight | mass_flow_from_scale__kg_per_s | g/s | kg/s |
| espresso_flow_goal | flow_goal_reported__native* | native | *(none — native)* |
| espresso_weight | weight__kg | g | kg |
| espresso_water_dispensed | water_dispensed__kg | g | kg |
| espresso_temperature_basket | temperature_basket__K | degC | K |
| espresso_temperature_mix | temperature_mix__K | degC | K |
| espresso_temperature_goal | temperature_goal__K | degC | K |
| espresso_state_change | state_change | code | code |

\* SERIALIZER_REVIEW §8: `espresso_flow` / `espresso_flow_goal` are pump/model estimates
that may be volumetric (mL/s), mass (g/s), or a machine proxy — so they are **kept native**
(no conversion, `units.si = None`, a `semantic` tag) under `flow_reported__native` /
`flow_goal_reported__native` and are flagged `unit_ambiguous:*`. They are NOT surfaced by
`visualizer_hydraulic` (the SI accessor). Only `espresso_flow_weight` (scale-derived) is a
confirmed mass flow and becomes SI `mass_flow_from_scale__kg_per_s`.

### outcomes tier (user-entered; separate)
| raw key | tidy key | raw unit | stored unit |
|---|---|---|---|
| drink_tds | outcomes.tds__fraction | % | fraction |
| drink_ey | outcomes.ey__fraction | % | fraction |
| fragrance/aroma/flavor/aftertaste/acidity/bitterness/sweetness/mouthfeel/espresso_enjoyment | outcomes.sensory.* | int | int |

### context tier
| raw key | tidy key | raw unit | stored unit |
|---|---|---|---|
| bean_weight | context.dose__kg | g | kg |
| drink_weight | context.drink_weight__kg | g | kg |
| duration | context.duration__s | s | s |
| grinder_model / grinder_setting | context.grinder_* | — | — |
| (brewdata source key) | context.machine | — | — |
| profile_title / roast_level / tags | context.* | — | — |

## Store layout (all under `puckworks/data/visualizer/`, gitignored except this file + `aggregate_stats.csv`)
```
raw/shard_*.jsonl.gz   # normalized TidyShot records (NOT committed)
raw/_index.csv         # per-shot 1-line summary for selection-bias accounting (NOT committed)
raw/_cursor.json       # resume / incremental cursor (NOT committed)
aggregate_stats.csv    # DERIVED aggregate stats only (TRACKED)
```

## How to (re)populate
```
pip install -e ".[harvest]"
export PUCKWORKS_VIS_SALT=$(cat puckworks/data/visualizer/.harvest_salt)   # keep this salt STABLE
python -m puckworks.lib.visualizer_harvest full            # initial crawl (default 18/min)
python -m puckworks.lib.visualizer_harvest incremental     # re-run: only new/updated
python -m puckworks.lib.visualizer_harvest stats --write-aggregate        # refresh the tracked CSV
```
**Rate:** the default **18/min** respects the binding **200-req/10-min** IP limit (=20/min
average) with margin; do **not** raise it above ~19/min for a *sustained* crawl even
though 50/min is allowed as a short burst — sustained 25–30/min exceeds 200/10min and
returns 429 (observed 2026-07-14). The harvester backs off + stops gracefully + resumes
on any 429, so it is safe either way, but 18/min avoids tripping the window at all.
**Completing the full corpus is a multi-hour uninterrupted run** — best on a machine
without a background-job reaper. The crawl is fully resumable (id-dedup + `_cursor.json`):
re-run `full` and it continues from where it stopped, with **no data loss** on interruption
(the crawl also stops gracefully if free disk drops below `--min-free-gb`, default 1 GB).
Refresh `aggregate_stats.csv` (the only tracked derived artifact) once substantially complete.
Tests use the committed fixtures in `tests/fixtures/visualizer/`, never the live
API. The harvester is not a test dependency and is not in `run_all_gates`.
