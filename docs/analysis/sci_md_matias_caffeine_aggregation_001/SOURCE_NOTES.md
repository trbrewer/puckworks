# Accepted source reuse

The canonical dataset remains `matias2023/fig3_caffeine_fractions`: ten means
across four physical extractions. This task directly inspected and read the
underlying committed `puckworks/data/matias2023/observations.csv`, its column
meanings, fraction IDs and support, plus `figure_geometry.json`, PROVENANCE,
SOURCE_NOTES, the Matias card, MANIFEST/register and #364's accepted bundle.
All 25 files in its artifact manifest match their accepted SHA256 identities.

| Input | SHA256 |
|---|---|
| observations.csv | 6f2f8a426159de950a518768a11b326376ead1f2a1de91f8ca6f0c77d5f6cd0a |
| figure_geometry.json | 6f56f7a6548d38df0db12602b6528768fb8eecafb15ae61ba59ead0af935928e |
| accepted scientific packet | fdb531f2806114feec1dab388a0e6751e1a18b07c49086127bdfc7d96cffc2e8 |

Accepted head: `a777ce74573c2f0a302f310b79d3b0966f76b249`, merged in #364.
Actual new-task base: `91a8d92a027ffde1c15a841d694b2c8a51f2e637`.
[Accepted qualification](../sci_md_matias_caffeine_fraction_shape_001/SOURCE_NOTES.md)
and [review](../sci_md_matias_caffeine_fraction_shape_001/REVIEW.md) remain unchanged.
No PDF/source archive was reopened, re-digitized, recalibrated or republished.
The accepted graphical radius is unchanged. No external individual raw traces
were inspected; no new corpus census or exhaustion claim is made.

Source attribution: Matias, A. F. V., Valente-Matias, D. F., Neng, N. R.,
Nogueira, J. M. F., Andrade Jr., J. S., Coelho, R. C. V., and Araújo, N. A. M.
(2023), “Continuum model for extraction and retention in porous media,”
*Physics of Fluids* 35(12), 123611,
[DOI 10.1063/5.0176273](https://doi.org/10.1063/5.0176273), numerical source
[arXiv:2304.03161v2](https://arxiv.org/abs/2304.03161v2).
Source-derived observations, result tables and replot retain
[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/), credited above.
Changes here: exact shape analysis, diagnostics and replot. First-party code
retains the repository MIT license. No source artwork is added.

Authoritative z and band endpoints are rational log10(c/(1 mg/L)) strings;
approximate mg/L is never logged back into the analysis. Ten original IDs F01–F10
and x=0,...,9 remain fixed. Centers are RECOVERED except F10
CLIPPED_BUT_RECOVERED; F01–F06 vertical endpoints are COVERED_BUT_RECOVERED,
F07–F09 RECOVERED, F10 CLIPPED_BUT_RECOVERED. Horizontal statuses and
UNDOCUMENTED_SEMANTICS are retained in support.csv; they do not fit spacing,
collection boundaries or a volume uncertainty model.

The observation is each nominal consecutive 5 mL finite-vial concentration,
aggregated over the same four extractions with fixed positive weights; arithmetic
means use 1/4. SE supplies no individual traces, covariance, extraction identities
or varying weights. Temperature was uncontrolled. Separate one-capsule Soxhlet
(5.57943 g, 70 mg) is context, not a shared inventory normalization. No volume-to-time
or volume-to-mass mapping is authenticated. Actual unequal-volume robustness is
NOT_ESTABLISHED. Existing source-internal/post-fit reconstruction evidence labels
remain unchanged; no new cohort or external-corpus family is created.
