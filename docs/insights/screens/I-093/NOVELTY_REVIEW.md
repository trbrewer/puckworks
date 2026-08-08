# I-093 — external novelty review

```
DEEP_SCREEN SUPPORTING DOCUMENT
NOT_A_PUBLICATION_RESULT
```

**Conducted 2026-08-08**, after the cheap screen returned SURVIVE, per
[`DEEP_SCREEN_PROTOCOL.md`](DEEP_SCREEN_PROTOCOL.md) §7 — never before, so the search could not
shape the result.

## Result

**`INCREMENTAL`.**

> Prior literature has investigated permeability representative volumes and universal permeability
> scaling in sphere packs. I-093's potential contribution is repository-specific: a reproducible
> calibration of finite-domain and realization effects for the Puckworks overlapping-sphere
> generator and pore-scale solver.

That is the strongest statement this review supports, and nothing in this bundle is stated more
strongly. Both halves of the cheap screen's proposition correspond to questions the porous-media
literature has already addressed, at least at abstract level.

**Abstract-level inspection and "not found in this search" do not establish exhaustive novelty.**
This review demonstrates *prior related work*; it is not a priority proof.

## Search record

| item | value |
|---|---|
| date | 2026-08-08 |
| access | web search available; **primary full texts were NOT retrievable** (`journals.aps.org` returned HTTP 403) |
| evidence level | **abstract- and summary-level only** for the APS papers |
| exhaustiveness | establishes **prior related work**, not an exhaustive priority proof |

**Search concepts used** (from the frozen protocol §7):

- `lattice Boltzmann permeability representative elementary volume size sphere pack REV convergence`
- `REV size permeability sphere packing how many grain diameters domain size convergence percent`
- `"universal scaling" permeability random packs overlapping nonoverlapping particles percolation threshold Kozeny-Carman`

## What the literature already establishes

**1. Permeability REVs in random sphere packs have been investigated before.** Phys. Rev. E 64,
066702 (2001) reports LBM and pore-network permeability analysis of random sphere packings and
states that it determines an REV *with respect to permeability*, compared against experiments and
empirical relations.

> **Correction to an earlier draft of this review.** That draft asserted that *"the literature
> places the permeability REV at 10–15 grain diameters."* **That statement was not supported by the
> sources I actually inspected and has been withdrawn.** The ~15-diameter figure came from
> Particuology 27, 88–94, which is a **DEM representative-volume study of polydisperse granular
> packings** — a structural/mechanical REV, which is *not* automatically a permeability REV. The
> accessible abstract of PRE 64, 066702 does **not** state a 10–15-diameter permeability threshold,
> and I did not obtain its full text.

The source-faithful statement is:

> Prior literature has directly investigated permeability REVs in random sphere packs, while
> related granular representative-volume studies commonly report scales larger than five particle
> diameters. **The exact threshold is property-, geometry-, criterion- and boundary-condition-
> dependent**, and no inspected primary source in this search fixes a numerical value for the
> permeability REV of overlapping-sphere packs.

⇒ The cheap screen's finding that permeability had not converged by **5.0** grain diameters is
therefore **not surprising in the light of prior work**, but prior work as inspected here does not
supply the specific threshold. What this screen measures is the gap for *this repository's own
generator and solver*, which is the part that is genuinely new to the repository.

**2. A universal permeability collapse for overlapping-sphere packs is published.** Vollmer et al.
(2022) report that packs of both hard and overlapping spheres, of any size or size distribution,
collapse onto a universal curve above the percolation threshold, and — directly relevant to how
this screen normalised — that the **inverse specific surface area, rather than an effective sphere
size or pore size, is the universal controlling length scale** for hydraulic properties. An earlier
universal-scaling result for sphere packings dates to 1994.

⇒ A trend comparison for overlapping spheres is therefore not new ground, and the choice of length
scale matters. Notably, `wadsworth2026.permeability` already normalises with
`k_star = 2(1−φ_p)/s_p²`, i.e. on specific surface area — **aligned with the published universal
length scale**, which is a point in that closure's favour and is recorded here rather than left
implicit.

**3. Closure applicability is porosity-regime-dependent.** The abstract of PRE 105, L043301 places
percolation-theory predictions **below φ ≈ 0.30**, Kozeny–Carman at **φ ≈ 0.30–0.40**, and dilute
Stokes expansions **above φ ≈ 0.40**. **Qualification stated by the authors:** the high-porosity
dilute-Stokes statement is framed **for lattice models**, so it is *not* direct proof for a random
overlapping-sphere family such as this repository's generator, and is not presented as such here.

⇒ This screen's family spans **φ = 0.40–0.65**, i.e. above the band where either comparator is the
literature's expected form. Both closures being *too steep in φ* relative to the pore-scale solve
is consistent with applying low-porosity functional forms in a high-porosity regime.

**This does not convict `wadsworth2026.permeability`.** That closure's exponent was *fitted to
coffee* and its declared validity is φ_p 0.37–0.67, so its in-range use on coffee is empirically
justified regardless of what the generic functional form does on spheres. The distinction matters
and is preserved.

## What this screen still contributes

Bounded, internal, and worth recording:

1. **A measured domain-size calibration for this generator/solver pair**, which the repository did
   not previously have. **Important scoping correction:** the registry's declared range for
   `brewer2026.pack_generator` reads *"grain radius >= 10 voxels; columns >= 5 grain diameters
   **for sigma**"* — the ≥5 figure is scoped to the columnar heterogeneity field σ, **not** to
   permeability. The repository therefore never claimed 5 grain diameters was sufficient for
   permeability, and nothing here contradicts it. The contribution is a positive measurement, not
   a correction of an existing claim.
2. **A preliminary two-realization dispersion measurement** for this generator, which did not previously exist in
   the repository and which is what makes any future RVE claim here falsifiable. **Stated
   precisely** (an earlier draft wrote "5–39 % spread" without defining the statistic): across the
   six porosities the cheap screen's **two-realization max/min range ratio** at fixed box size,
   `max(k_seed_1, k_seed_2) / min(k_seed_1, k_seed_2)`, ranged **1.045–1.392** — approximately
   **4.5–39.2 % relative to the smaller of the two values**. This is an *observed two-realization
   dispersion*, and it is **not** a coefficient of variation, a standard deviation, a confidence
   interval, an uncertainty width, a population estimate, or a realization-noise floor. Only the
   deep multi-realization ensemble can establish a defensible realization-variability statistic.
3. **A recorded length-scale caution**: comparing on R when the published universal control is
   1/s_p.

## Explicit limits of this review

- **"Not found in this search" is not "does not exist."** Three query families over one session, US
  web search only.
- **Primary texts were not read.** APS full texts returned HTTP 403; conclusions above rest on
  abstracts and search-result summaries. No novelty claim in this bundle may be stated more
  strongly than that evidence supports, and none is.
- Nothing was ingested, copied or redistributed. No paywalled content was obtained or stored; only
  publicly returned bibliographic and abstract-level material was consulted.
- This review adjudicates **novelty only**. It does not validate, invalidate or re-rank any
  repository component, and it changes no evidence rung.

## Sources consulted

- [Universal scaling for the permeability of random packs of overlapping and nonoverlapping particles — Phys. Rev. E 105, L043301 (2022)](https://doi.org/10.1103/PhysRevE.105.L043301)
- [Universal scaling of fluid permeability for sphere packings — Phys. Rev. E 50, 403 (1994)](https://doi.org/10.1103/physreve.50.403)
- [Pore-scale modeling of saturated permeabilities in random sphere packings — Phys. Rev. E 64, 066702 (2001)](https://journals.aps.org/pre/abstract/10.1103/PhysRevE.64.066702)
- [Permeability of packs of polydisperse hard spheres — Phys. Rev. E 103, 062613 (2021)](https://doi.org/10.1103/PhysRevE.103.062613)
- [Lattice Boltzmann Modelling of Fluid Flow through Porous Media: Pore-Structure vs Representative Elementary Volume Methods — Energies 16, 5354](https://doi.org/10.3390/en16145354)
- [Representative elementary volume analysis of polydisperse granular packings using DEM](https://www.sciencedirect.com/science/article/abs/pii/S1674200115001649)
- [Modeling single-phase permeability in uniform grain packs (arXiv:2001.10835)](https://arxiv.org/pdf/2001.10835)
- [Numerical simulation of transport in porous media: some problems from micro to macro scale (arXiv:1807.00688)](https://arxiv.org/pdf/1807.00688)
