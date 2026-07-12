# G2 transient-discharge source notes

## What was located

The named Ellero & Navarini source is real:

- M. Ellero and L. Navarini, *Mesoscopic modelling and simulation of espresso coffee
  extraction*, Journal of Food Engineering 263 (2019), 181–194.
- DOI: 10.1016/j.jfoodeng.2019.05.038
- An open conference version is available at:
  https://upcommons.upc.edu/bitstreams/7992d37d-d17a-40cc-9f93-7d8e2bd8486d/download
- An author/institutional manuscript is listed at:
  https://bird.bcamath.org/bitstream/handle/20.500.11824/981/paperJFE.pdf?isAllowed=y&sequence=1

The open conference version contains a direct/inverse-discharge figure with a historical
experimental comparison. It specifies:

- viscous time for experiment: τ_v = (400 µm)^2 / 10^-6 m²/s = 0.16 s;
- direct forcing to t/τ_v ≈ 38;
- rest from 38–55;
- same-direction forcing after 55;
- second rest from 75–90;
- reversed forcing after 90;
- experimental initial flow rise removed because pressure was applied over finite time.

The figure is useful as a digitization target but is not raw data. The underlying historical
experiment is attributed to ASIC proceedings in the Petracco/Bandini lineage.

## Historical proceedings identified

1. Petracco, M. and Suggi Liverani, F. (1993), “Espresso coffee brewing dynamics:
   development of mathematical and computational model,” 15th International Scientific
   Colloquium on Coffee (ASIC).
2. Bandini, M. et al. (1997), “A reaction-diffusion computational model to simulate coffee
   percolation,” 17th International Scientific Colloquium on Coffee (ASIC).

## What is still missing

- the original experimental point series and uncertainty;
- a scan of the exact proceedings figures/tables if they contain more detail;
- a machine-readable discharge protocol and pressure/flow units.

## Recommended next step

1. Ask ASIC/illy archives and Ellero/Navarini for the raw transient-discharge series.
2. In parallel, digitize the experimental overlay in the 2019 figure and label it
   `figure_digitized`, not raw data.
3. Use `g2_transient_discharge_digitization_template.csv`.
4. Keep dimensional and dimensionless columns together; do not infer pressure magnitude if the
   source only supplies F/F0.
