# Minimum external fraction-dataset schema (handoff §2.7)

The target schema for any incoming external fraction-resolved dataset (Kuhn, Vaca
Guerra, or future). One row per (dataset, condition, replicate, fraction, analyte).
Preserve source values unchanged; any transformation (time shift, unit conversion,
interpolation) happens in a derived table with a logged transformation.

```text
dataset_id
condition_id
replicate_id
coffee_id
origin
roast
dose_g
machine
basket
pressure_bar
temperature_C
flow_ml_s_or_trace_id
grind_setting
psd_d10_um
psd_d50_um
psd_d90_um
sieve_band
tamp_N
fraction_index
t_start_s
t_end_s
cumulative_beverage_g
fraction_mass_g
analyte
concentration
unit
assay
lod
loq
uncertainty_type
uncertainty_value
source_doi
source_file
source_row
license
```

## Observation operator (handoff §2.2)
A fraction is a **mass/volume-weighted mean over its collected interval**, not a
midpoint point-concentration:
`C_i = ∫ ṁ_out C_out dt / ∫ ṁ_out dt` over `[t_i, t_{i+1}]`; the whole cup is the
same integral over `[t_0, t_f]`. The **same** simulated trajectory must generate both
the fraction and the integrated observables — that is the clean information-content
comparison. Do not mix mass and volume without a documented density convention.
