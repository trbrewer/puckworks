# G10 coffee-liquor rheology source notes

## Immediately usable open source

Khomyakov, Mordanov & Khomyakova (2020), DOI 10.1088/1755-1315/548/2/022040, is open under CC BY 3.0.
It reports coffee-extract properties for dry-solids mass fractions 0.15–0.70 and
temperatures 20–80 °C.

Files in this bundle:

- `khomyakov2020_kinematic_viscosity.csv`: exact transcription of measured Table 1.
- `khomyakov2020_dynamic_viscosity_regression.csv`: exact Table 2 coefficients.
- `khomyakov2020_regression_consistency_FLAGGED.csv`: a diagnostic showing that literal
  evaluation of the printed power law does not reproduce Table 1-derived values.
- `khomyakov2020_density_equation_FLAGGED.csv`: the printed density relation and its unresolved
  sign conflict.

## Critical fit limits

1. The lowest measured dry-solids fraction is 15 wt%. Typical espresso beverage TDS can be
   below this, so this source must not be silently extrapolated to lower TDS.
2. The source is industrial soluble-coffee extract, not a fraction-resolved espresso dataset.
3. The printed density equation has an internal contradiction:
   - narrative: density decreases with temperature;
   - equation: `rho = 932 + 0.8*T + 509*f`, which increases with temperature.
4. The viscosity regressions are described by the authors as rough estimates; published mean
   approximation errors range from 4.0% to 16.2%, and no f=0.25 regression row is supplied.
5. More importantly, literal evaluation of the printed equation with temperature in °C does
   not reproduce dynamic viscosity derived from the measured kinematic-viscosity table. The
   equation or its temperature convention therefore needs author clarification.

## Stronger candidate sources to acquire

- Telis-Romero et al. (2000), *Temperature and water content influence on thermophysical
  properties of coffee extract*, DOI 10.1080/10942910009524642; reported domain 10–50% solids,
  30–82 °C, including density.
- Telis-Romero et al. (2001), *Rheological properties and fluid dynamics of coffee extract*,
  DOI 10.1111/j.1745-4530.2001.tb00541.x; reported domain 10–51% solids and 18–92 °C.
- Burmester, Fehr & Eggers (2011), cited as covering approximately 0–40% solids and 20–60 °C.

## Recommended repository status

Mark G10 `PARTIALLY SOURCED`, not resolved. The measured kinematic-viscosity table is useful
as a bounded source dataset, but the published dynamic-viscosity regression must remain
quarantined. A production closure still needs:

- verified density data;
- coverage below 15 wt% solids;
- preferably espresso-liquor rather than evaporator-feed measurements.
