# Puckworks experimental data — templates and principles

Fill these templates for a submission (see [`../../EXPERIMENTAL_DATA_NEEDS.md`](../../EXPERIMENTAL_DATA_NEEDS.md)
and the [protocol packs](../protocols/)). The CSV files are **header-only**: they are the data dictionary,
not data. Validate a filled submission directory with
`python tools/experimental_data_needs.py validate-submission <dir>`.

## Common identifiers

`campaign_id`, `site_id`, `apparatus_id`, `coffee_lot_id`, `grinder_id`, `basket_id`, `shot_id`,
`replicate_id`, `fraction_id` (where applicable), the time base, and `raw_or_processed` on every table.

## Raw-data principles

- Preserve instrument-native **raw** files; never overwrite raw values, and mark every row
  `raw_or_processed`. A processed alias must not overwrite the raw file it derives from.
- Record the **timezone separately** from the experiment time; time series use **monotonic elapsed
  seconds** (`elapsed_s`), non-decreasing.
- Retain the native sampling rate; record any resampling/filtering **separately** (as processed).
- Include calibration **before and after** where possible (`calibration.csv`).
- Distinguish `missing`, `below_detection`, `not_measured`, and `invalid` — a missing value is **never**
  zero (chemistry rows carry an explicit `measurement_status`).
- Preserve **failed runs and exclusions** with reasons (`exclusions.csv`, and `included`/`exclusion_reason`
  on `shot_metadata.csv`); never silently discard a replicate.
- Use privacy-safe `site_id` / contributor identifiers; avoid personally identifying data.

## Instrument and synchronization guidance

For every signal (see `apparatus.yml`) record: physical observable, instrument, native unit, calibration,
uncertainty, clock source, synchronization method, offset/drift estimate, conversion method, processed
output, and whether it is **prescribed** or **measured**.

Do **not** prescribe a universal sampling frequency. Instead: preserve the fastest valid native rate;
derive a minimum useful rate from the fastest phenomenon plus anti-aliasing/synchronization needs; and
document that pilot calculation. Unknown design values use `DESIGN_CALCULATION_REQUIRED`,
`SENSOR_SELECTION_REQUIRED`, or `PILOT_REQUIRED`.

## Replication and design

Do not invent a number of shots. Require a pilot variance estimate; an effect size tied to the scientific
discriminator; a power/precision calculation where inferential claims are planned; blocking by coffee
lot / day / operator / machine where appropriate; randomized or counterbalanced order where interventions
permit; a **holdout** predeclared before any fitting; a preregistered primary observable + analysis; and
complete replicate accounting.

## Synthetic test fixture

`fixtures/synthetic/` is a **`SYNTHETIC_TEST_FIXTURE`** used only to test the parsers/QC. It is impossible
to mistake for measured data, is excluded from `puckworks/data/MANIFEST.csv` evidence, and is never used
to validate a scientific model or support a public claim.
