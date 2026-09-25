# Source/readout contract

**BLOCKED_SOURCE_CONTRACT for flow and powder transfer.**
See the independent [source review](review/SOURCE_REVIEW.md) for page/table/figure
citations and bounded alternatives. This task actually inspected the original
30-page author manuscript, including rendered Eq37 and Figs7–9, its relevant
methods, Table1, equations and Appendix A. The institutional PDF is held
privately, identified in `identities.json`; the final typeset publisher PDF and
raw replicates/controller histories were not available in the configured family.
The six mounted family CSVs are byte-identical to the repository copies. No
other family was crawled. Unavailable here does not mean nonexistent.

The 51-row register preserves all supplied coordinates and original bytes.
No source values are replaced. E/4 has three tabulated rows through20g; additional
late markers are visible in the original Fig7 but have not been newly digitized.
Thus the supplied table's support is shorter than the original figure's support.
H is not a measured extraction condition in this table. Fig6 model K sweeps,
Fig3 simulated flow decay and Figs7–9 model lines are excluded targets.

`observation_register.csv` audits EY=strength*mass/dose at the two explicitly
named source dose alternatives (7.5g single shot and15g basket). These residuals
are not dose estimates and cannot resolve splitting. Nonzero residuals also
include independent summary averaging, rounded masses and digitization. The
averaging/covariance operator is not available; no independent paired EY/strength
samples, likelihood, confidence intervals or zero-uncertainty claims are made.
Bars are reported three-brew SD, not standard errors. Zero tabulated errors have
unknown uncertainty. Digitization error has no independently established bound.

The shared-material condition is unqualified. If the flow operator were resolved,
the owner's alternative permits one training-estimated inventory per powder,
unchanged at its withheld flow and equal across candidates. That does not permit
powder-transfer scoring. No alternative is currently activated or fitted.

The constants in the synthetic check (15g,29mm radius,13.5mm height,epsilon=.17,
rho=1000kg/m3,half collection) are a declared hypothetical combination, not a
qualified experimental observer. Porosity and free-fluid D=2e-9m2/s are source
literature assumptions; D caps the prospective diffusion search. Source nominal
particle density600kg/m3 with the stated geometry/porosity gives17.76g, not15g.
The kernel therefore accepts dose separately and makes no independent-density
claim. No dose, split, density, hold-up or clock is optimized.

Source attribution: Mo, Navarini, Suggi Liverani and Ellero,
*Modelling swelling effects in real espresso extraction using a 1-dimensional
coarse-grained model*, DOI10.1016/j.jfoodeng.2023.111843.
[Institutional source](https://bird.bcamath.org/handle/20.500.11824/2062).
The institutional item declares CC BY-NC-SA3.0 ES; original PDF and page renders
remain outside Git. Existing upstream data retain their notices and provenance;
the software license does not relicense them. The committed register references
existing rows rather than publishing a new source-value dump.
