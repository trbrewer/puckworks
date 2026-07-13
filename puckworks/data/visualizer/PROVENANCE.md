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
The visualizer application is MIT (app code only). The **shot corpus has NO
research-use license** and is user-contributed. Therefore:

- The **raw harvested corpus is NEVER committed** — `raw/shard_*.jsonl.gz`,
  `raw/_index.csv` and `raw/_cursor.json` are gitignored (same mechanism as the
  pannusch2024 Mendeley drop).
- **Internal calibration use only; not redistributed.** Correspondence with
  Miha Rekar (miha@visualizer.coffee) for sanctioned bulk/research use is
  pending (ROADMAP §5.8). The public API works without it, but redistribution
  or publication use is gated on that reply.
- Only these are tracked (force-added): the harvester code, the offline
  fixtures, this `PROVENANCE.md`, the two MANIFEST rows, the data-only card, and
  the small DERIVED `aggregate_stats.csv` (counts / coverage histograms / unit
  audit — **NOT** shot data).

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
| espresso_flow | flow__kg_per_s | g/s* | kg/s |
| espresso_flow_weight | flow_weight__kg_per_s | g/s | kg/s |
| espresso_flow_goal | flow_goal__kg_per_s | g/s* | kg/s |
| espresso_weight | weight__kg | g | kg |
| espresso_water_dispensed | water_dispensed__kg | g | kg |
| espresso_temperature_basket | temperature_basket__K | degC | K |
| espresso_temperature_mix | temperature_mix__K | degC | K |
| espresso_temperature_goal | temperature_goal__K | degC | K |
| espresso_state_change | state_change | code | code |

\* `espresso_flow` / `espresso_flow_goal` may be volumetric (mL/s) rather than
mass (g/s) depending on the source machine — flagged `unit_ambiguous:*`.
`espresso_flow_weight` (scale-derived) is the trustworthier flow channel.

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
export PUCKWORKS_VIS_SALT="<a private salt>"    # production runs MUST set this
python -m puckworks.lib.visualizer_harvest full            # initial crawl
python -m puckworks.lib.visualizer_harvest incremental     # re-run: only new/updated
python -m puckworks.lib.visualizer_harvest stats --write-aggregate   # refresh the tracked CSV
```
Tests use the committed fixtures in `tests/fixtures/visualizer/`, never the live
API. The harvester is not a test dependency and is not in `run_all_gates`.
