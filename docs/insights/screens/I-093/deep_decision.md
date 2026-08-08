# I-093 Deep Screen Decision

```
DEEP_SCIENTIFIC_SCREEN
SYNTHETIC_GEOMETRY_RESULT
NOT_REAL_PUCK_VALIDATION
NOVELTY_INCREMENTAL
```

**Deep disposition: `BOUNDED_NULL`** — applied from the frozen rule in
[`DEEP_SCREEN_PROTOCOL.md`](DEEP_SCREEN_PROTOCOL.md) §8, unrevised.

| field | value |
|---|---|
| `finite_size_status` | `PASS_BY_NON_REJECTION_LOW_POWER` |
| `realization_variability_status` | `MATERIAL_AND_DOMINANT` |
| `closure_status` | `NOT_ADJUDICATED_COMPUTE_BOUND` |
| `overall_deep_disposition` | **`BOUNDED_NULL`** |
| `novelty_disposition` | `INCREMENTAL` |
| `issue_231_disposition` | `NOT_MATERIAL_TO_SELECTED_DECISION` |

## 1. The historical cheap result stands unchanged

The cheap screen returned **SURVIVE** and that remains the frozen historical result: its rule was
applied as written. It is not retroactively rewritten. What the deep screen adjudicates is its
**stated limitation** — the box-size sweep used **one realisation per size**.

## 2. The outcome-independent erratum, recorded separately

Two characterisation corrections were committed **before** any deep output was read, and neither
depends on this result: [`PROTOCOL_ERRATUM.md`](PROTOCOL_ERRATUM.md) (the "≥5 grain diameters"
figure is scoped to *sigma*, not permeability; no pack card exists; no repository correction is
warranted) and [`DEEP_PROTOCOL_ERRATUM.md`](DEEP_PROTOCOL_ERRATUM.md) (the deep budget statement
was wrong: the full 46-cell matrix needs ≈364 min against a 150-min budget).

## 3. Execution audit — all 46 frozen cells accounted

| status | cells |
|---|---|
| `CONVERGED` | **24** |
| `NOT_LAUNCHED_BUDGET_GUARD` | **22** |
| `SCIENTIFIC_NONCONVERGENCE` | 0 |
| `OPERATIONAL_FAILURE` | 0 |
| `EXACT_RETRY` | 0 |
| `IN_FLIGHT_AT_GUARD` | 0 |

Every launched cell converged; nothing failed, nothing was retried, and no realisation was
dropped. By section: **§3 16/16 complete**, **§4.1 2/2 complete**, **§4.2 6/16 partial**,
**§4.3 0/12 not launched**.

**Guard:** actual wall time **9743 s against a 9000 s budget** — a 743 s overrun, because the
frozen guard checks *before launching* and lets an admitted cell run to completion. That behaviour
was recorded before the run and was not changed. Output isolation: a single run process held all
results in memory and wrote one JSON at the end, so no shared mutable file was contended.

## 4. Seed semantics — `RELATED_NON_NESTED`

> Equal seeds initialize a common pseudorandom stream, but size-dependent coordinate mapping,
> placement history, stopping behavior, and draw count produce non-nested geometries. Equal-seed
> cases are not interpretable as the same physical realization at increasing size. No paired
> finite-size analysis is used. Cross-size statistical independence is not established.

Consequently **no paired differences were computed**, each size is summarised as its own ensemble,
and no figure connects equal seeds across sizes.

## 5. §3 finite-size result — the controlling question

Every realisation, n = 4 per size, all converged (k in lattice units, lu²):

| L | L/d | n | individual k | mean | median | sample SD (n−1) | CV | min | max | max/min |
|---|---|---|---|---|---|---|---|---|---|---|
| 48 | 2.4 | 4 | 3.120, 5.361, 7.605, 8.007 | 6.0234 | 6.4833 | 2.2589 | **0.375** | 3.1198 | 8.0072 | **2.567** |
| 64 | 3.2 | 4 | 4.616, 5.683, 5.982, 6.142 | 5.6057 | 5.8321 | 0.6865 | 0.122 | 4.6163 | 6.1421 | 1.331 |
| 80 | 4.0 | 4 | 4.210, 4.875, 5.246, 6.607 | 5.2343 | 5.0602 | 1.0106 | 0.193 | 4.2096 | 6.6070 | 1.570 |
| 100 | 5.0 | 4 | 4.239, 4.516, 5.135, 5.760 | 4.9124 | 4.8255 | 0.6777 | 0.138 | 4.2392 | 5.7596 | 1.359 |

**The frozen criterion**, `|k̄(L) − k̄(L_max)| ≤ 2·√(SE(L)² + SE(L_max)²)`:

| L | Δ | Δ% | 2-SE band | within? |
|---|---|---|---|---|
| 48 | 1.1110 | 22.6 % | 2.3583 | ✔ |
| 64 | 0.6932 | 14.1 % | 0.9647 | ✔ |
| 80 | 0.3218 | 6.6 % | 1.2168 | ✔ |
| 100 | 0 | 0 | 0.9585 | ✔ |

⇒ `L* = 48`, `R_sep = 0.529`.

> **Permeability satisfied the frozen stabilization criterion over L/d = 2.4 to 5.0 for the tested
> synthetic generator/solver ensemble.**

### The power caveat, which is essential to reading that sentence

**This is a failure to reject, not a demonstration of equivalence, and no convergence is claimed.**
Two facts make that unavoidable:

- **`L*` is the *smallest* tested size.** A stabilisation test that "passes" at the bottom of its
  own sweep is telling you it cannot distinguish any size from any other.
- The ensemble means **decline monotonically** — 6.023 → 5.606 → 5.234 → 4.912, a **22.6 %** fall
  across the tested range — yet with n = 4 and per-size CV of **12–38 %**, the 2-SE band at L=48 is
  2.36 against a Δ of 1.11. The band simply absorbs the decline.
- `R_sep = 0.53` says the last box-size step is **not resolved above seed noise**.

**No REV is determined and none is claimed.** The frozen protocol defines no REV determination, so
neither an REV value nor an "REV exceeds the largest tested size" inference is stated.

## 6. Realisation variability versus the finite-size signal — the positive finding

- **Within-size** max/min: 2.567, 1.331, 1.570, 1.359. CV: 0.375, 0.122, 0.193, 0.138.
- **Between-size** change in the ensemble mean: 22.6 % total; steps of +7.4 %, +7.1 %, +6.6 %.
- **Individual values overlap heavily.** The L = 48 range (3.120–8.007) **entirely contains** the
  L = 100 range (4.239–5.760).
- **Ordering is not consistent across realisations** — at L = 100, seed 0 gives 5.135 while seed 2
  gives 4.239.

⇒ **Within-size dispersion is larger than the between-size signal.** Supported statement:

> Independent-realization variability is material relative to the apparent finite-domain signal,
> so a single-realization size sweep is insufficient for permeability inference for this generator
> over the tested domain.

No post-hoc significance test was introduced, and the variation is **not** called a stable noise
floor. Because the cross-size geometries are `RELATED_NON_NESTED`, no claim is made that changing
the seed label isolates domain size while holding morphology fixed.

### The single most direct demonstration

| L/d | cheap screen, seed 0 only | deep ensemble mean (n = 4) |
|---|---|---|
| 2.4 | 3.120 | 6.023 |
| 3.2 | 4.616 | 5.606 |
| 4.0 | 4.210 | 5.234 |
| 5.0 | 5.135 | 4.912 |

The cheap single-realisation sweep **rises**; the ensemble mean **falls**. The two trend in
**opposite directions**. That is why the cheap RVE arm does not survive — it was reading one
realisation's scatter as a size effect.

## 7. §4.1 — numerical convergence is not the explanation

Tightening `rtol` 1e-6 → 1e-7 and `min_steps` 1200 → 2000 at L = 64, seed 0 moved k by
**3.45 × 10⁻⁸ relative** (4.616343 → 4.616344 lu²), far inside the frozen 1 % limit. The cheap
screen's convergence criterion was adequate.

This cleanly separates the five sources: **implementation error** (positive control, 0.052 % on
plane-Poiseuille) and **discretisation/convergence error** (3 × 10⁻⁸) are both excluded, leaving
**realisation variability** as the dominant term, with **finite-domain dependence** unresolved and
**closure discrepancy** unadjudicated.

The plane-Poiseuille control establishes solver correctness for the reference flow only. It does
**not** establish convergence for every porous realisation, representative-volume adequacy,
empirical validity, or closure validity.

## 8. §4.2 — partial, non-decisional

6 of 16 cells ran: porosity `phis_target = 0.35` only, with **n = 4 at L = 64 and n = 2 at
L = 100**; `phis_target = 0.60` is **entirely missing**. The recorded arm shows a 30.7 % mean
difference with R_sep = 2.06 — *suggestive* of porosity-dependent box behaviour, and **explicitly
not a decision**: the comparison is unbalanced, the second porosity is absent, and the frozen
protocol defines no partial porosity rule. Retained as partial, non-decisional evidence.

## 9. §4.3 and the closure sub-result — compute-bounded

**All 12 cells `NOT_LAUNCHED_BUDGET_GUARD`.**

> The frozen deep closure matrix was not completed within the 150-minute compute budget. The
> cheap-screen monotonic ratio trend was therefore **not deep-confirmed or deep-rejected**.
> Completed §4 cells are retained as partial, non-decisional evidence.

This is **not**: closure failure; evidence that either closure is valid; evidence that either
closure is invalid; NEEDS_NEW_DATA; or an empirical-data limitation. It is a synthetic-compute
limitation. **The cheap screen's monotonic ratio trend does not carry forward and has no deep
standing.**

## 10. Why the overall disposition is BOUNDED_NULL

The frozen rule keys on the finite-size ensemble: stabilised ⇒ `BOUNDED_NULL`. It fired, and it is
applied unrevised. §8's description matches what happened — *"the cheap screen's RVE arm was
realisation scatter"* — and the second clause, re-deciding the trend on stabilised means, **could
not execute**, which is recorded rather than papered over.

So the bounded null has two honest halves: the cheap screen's finite-size claim is **withdrawn**,
and stabilisation is **not demonstrated either**. At this power the data support neither direction.

## 11. Strongest remaining alternative

**Synthetic overlapping spheres are not a real puck.** Accepted, unrefuted, and load-bearing on
every claim above. A second, live alternative: with n = 4 the study is underpowered, so a genuine
finite-size effect of ~20 % could exist and remain invisible here. Nothing in this screen excludes
it — which is precisely why no convergence is claimed.

## 12. Claim ceiling

**A — synthetic generator/solver.** For `brewer2026.pack_generator` + `brewer2026.lb_reference` at
R = 310.8 µm, grain radius 10 voxels, φ ≈ 0.49, over L/d = 2.4–5.0 with n = 4 realisations per
size: independent-realisation variability is material and dominates the apparent finite-domain
signal, so a single-realisation size sweep is insufficient for permeability inference over this
generator and domain.

**B — domain size.** The frozen 2σ criterion is satisfied over L/d = 2.4–5.0, but **by
non-rejection at low power**, not by demonstrated convergence. No REV is determined or claimed.

**C — continuum closures.** **Not adjudicated.** Nothing is established for or against either
closure.

**D — repository guidance.** The repository did **not** claim that five grain diameters was
sufficient for permeability. **No pack-card or registry correction was warranted or made.**

**E — real pucks and novelty.** No real-puck permeability validation was performed and no
representativeness of the synthetic morphology was established. Prior literature already contains
universal sphere-pack permeability scaling and permeability-REV analyses
([`NOVELTY_REVIEW.md`](NOVELTY_REVIEW.md)); the contribution is **incremental and
repository-specific** — a *first repository-bound calibration*, not a first measurement.

## 13. Reproduction

```
python -m puckworks.analysis.deep_screen_i093_rve        # ~2.7 h CPU, local, NOT a CI job
python -m puckworks.analysis.deep_i093_adjudicate        # deterministic, seconds
python -m pytest tests/test_deep_screen_i093.py -q
```

Raw run preserved byte-identical as [`deep_run_raw.json`](deep_run_raw.json); the adjudication is a
pure function of it plus [`expected_run_matrix.json`](expected_run_matrix.json).

## 14. Source commit

Base `892e5ec78f7a0dcf1b1f2de85ccfff8f39e0effa`. `deep_result.json` binds the base, both protocol
hashes, both erratum hashes, the cheap result hash, the expected-matrix hash and the raw-run hash.
