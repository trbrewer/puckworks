# I-093 — deep-screen protocol (FROZEN BEFORE EXECUTION)

```
DEEP_SCREEN
NOT_A_PUBLICATION_RESULT
NOT_A_MODEL_VALIDATION_UPGRADE
```

Committed **before** any deep execution, in its own commit, after the cheap screen returned
**SURVIVE** ([`decision.md`](decision.md)). Base `892e5ec78f7a0dcf1b1f2de85ccfff8f39e0effa`.

---

## 1. The exact surviving proposition

> On the synthetic overlapping-sphere family at R = 310.8 µm, the pore-scale permeability computed
> by `brewer2026.lb_reference` does **not** stabilise with box size up to and including the pack
> card's ≥5-grain-diameter guidance, and the ratio `k_LBM/k_closure` falls systematically with
> porosity for both continuum closures.

**This proposition is not yet established, and the deep screen exists to decide it.** The cheap
screen swept box size at **one seed** while realisation variance at fixed box size is 5–39 %,
which is the same order as the 18 % change between its two largest boxes. Both halves of the
proposition are therefore confounded with geometry-realisation noise.

## 2. Strongest alternative explanation

**The cheap screen's RVE arm is realisation scatter, not a representative-volume requirement.**
Single-realisation `k` at fixed L fluctuates by tens of percent because a finite periodic box
happens to contain a particular arrangement of pore throats; averaging over independent seeds would
collapse the apparent L-dependence and the solver would prove to be stabilised by ~3–4 grain
diameters after all.

If that is true, the honest deep outcome is a **bounded null**: the cheap screen's SURVIVE was
driven by my own under-powered sweep, the finding does not stand, and the record must say so.

A second alternative, carried forward unrefuted from the cheap screen: **synthetic spheres are not
a real puck**, so nothing here transfers to coffee. This bounds the ceiling under every outcome and
is not testable in this cycle.

## 3. The decisive test — multi-seed RVE

At `phis_target = 0.50` (the cheap screen's sweep porosity), run **N = 4 independent seeds** at
each box size `L ∈ {48, 64, 80, 100}` (L/d = 2.4, 3.2, 4.0, 5.0). L = 32 is dropped: at 1.6 grain
diameters it is below any plausible RVE and its cost is better spent on seeds.

For each L compute the seed **ensemble mean** `k̄(L)`, the sample standard deviation `s(L)`, and the
standard error `SE(L) = s(L)/√N`.

**Frozen stabilisation criterion on the ensemble means:**

```
STABILISED at L*  iff  for every swept L >= L*:
      |k̄(L) − k̄(L_max)|  <=  2 * sqrt( SE(L)^2 + SE(L_max)^2 )     (2-sigma, seed-averaged)
```

i.e. the remaining box-size dependence is not resolvable above realisation noise.

**Separation statistic (frozen, reported either way):**

```
R_sep = |k̄(L_max) − k̄(L_max-1)|  /  sqrt( SE(L_max)^2 + SE(L_max-1)^2 )
```

`R_sep > 2` means the box-size step is resolved above seed noise; `R_sep <= 2` means it is not.

## 4. Robustness, sensitivity and convergence requirements

1. **Solver-tolerance sensitivity.** Re-run one (L, seed) pair at `rtol = 1e-7` (10× tighter) and
   at `min_steps = 2000`. If `k` moves by more than 1 %, the cheap screen's convergence criterion
   was too loose and every number inherits that; report it as a numerical-uncertainty term.
2. **Porosity dependence of the RVE.** Repeat a two-size, multi-seed comparison (L = 64 vs 100) at
   the family extremes `phis_target = 0.35` and `0.60`. Dense packs plausibly need larger boxes;
   if the RVE behaviour is porosity-dependent, the trend metric is contaminated in a
   porosity-correlated way, which is the one way realisation noise *could* fake a systematic trend.
3. **Trend metric on stabilised means.** Recompute `G` from seed-averaged `k̄` at the largest
   affordable box, not from single realisations at L = 64. This is the scientifically meaningful
   version of the cheap screen's secondary result.
4. **Weakest defensible evidence treatment.** Recompute the decision using the *most* conservative
   uncertainty available (the largest of: seed SD, the tolerance sensitivity, the residual
   box-size step) as the agreement floor, alongside the closure's published ×/1.31 scatter.

## 5. Fit, calibration and holdout lineage

- `wadsworth2026.permeability` was **fitted and validated on real coffee via XCT + LBflow**
  (`docs/cards/wadsworth2026.md`). It is therefore *already* LB-anchored: agreement with an LB
  solver is weak evidence, and only **disagreement** is informative. Recorded again here so no
  outcome is over-read.
- Nothing in this screen is held out, and no independent evidence exists: both routes are
  computations on generated geometry. **No holdout claim may be made under any outcome.**
- No manifest dataset is consumed under any branch of this protocol.

## 6. Generality boundaries (frozen)

Whatever the outcome, it applies to: overlapping-sphere packs, monodisperse at R = 310.8 µm, zero
columnar heterogeneity, porosity 0.40–0.65, periodic boundaries, Stokes regime, D3Q19 TRT with
full-way bounce-back. It does **not** extend to: real coffee geometry, polydisperse or angular
grains, tamped beds, fines-bearing packs, or any other solver.

## 7. Novelty review (runs only after the internal maturation)

Questions: is the box-size (RVE) requirement for LB permeability in overlapping-sphere packs an
established quantity in the porous-media literature, and at what L/d does it converge? Is a
systematic porosity-dependent deviation between LB permeability and percolation/Carman–Kozeny
closures on sphere packs already reported?

Search concepts: *lattice Boltzmann permeability representative elementary volume sphere pack*;
*REV size porous media permeability LBM*; *Carman-Kozeny deviation overlapping spheres porosity
exponent*; *percolation permeability model coffee*.

Rules: prefer primary papers and official documentation; record terms, sources and date;
distinguish *not found in this search* from *does not exist*; ingest nothing without a rights
basis. **If network access is unavailable, complete the internal maturation and cap the novelty
language explicitly — state that external novelty was not established rather than substituting
confidence for a search.**

## 8. Deep decision logic (frozen)

| outcome | condition |
|---|---|
| **INSIGHT_SURVIVES** | ensemble means still fail the §3 stabilisation criterion **and** `R_sep > 2` — a genuine RVE requirement beyond 5 grain diameters exists on this family. |
| **BOUNDED_NULL** | ensemble means satisfy the criterion — the cheap screen's RVE arm was realisation scatter. The trend result is then re-decided on the stabilised means and reported as its own bounded finding. |
| **CORRECTION_ONLY** | the maturation shows the cheap screen's numbers were wrong for a demonstrable implementation reason rather than a scientific one. |
| **NEEDS_NEW_DATA** | reserved, and expected to be unused: this is a computational question and there is no measurement to request. A compute limit is **not** NEEDS_NEW_DATA. |

If the deep run cannot afford enough seeds to make `SE` meaningful, the outcome is an explicit
**compute bound** carrying whatever bounded result was obtained — never disguised as a data need.

## 9. Correction blast-radius procedure

If maturation demonstrates a **material scientific error** in the cheap screen (not merely a
weaker-than-hoped result):

1. document the exact defect and its evidence before changing anything;
2. keep the cheap-screen bundle as the historical record — do **not** rewrite `result.json`,
   `decision.md` or the figure to match the later finding;
3. record the correction in `deep_decision.md` and, if it changes a repository claim, in a separate
   narrowly named commit;
4. add a regression test proportional to the defect;
5. preserve unaffected numerics.

A bounded null is **not** a correction: it is a result.

## 10. Compute budget

**≤ 150 minutes** CPU on `lb_reference`, local, not CI. Measured single-run costs at this
resolution: L=48 ≈ 55 s, L=64 ≈ 183 s, L=80 ≈ 403 s, L=100 ≈ 726 s. The §3 design (4 seeds ×
{48,64,80,100}) is ≈ 91 min, leaving headroom for §4. If the budget is exceeded, stop and report
the bounded result plus the exact requirement that exceeded it.

## 11. Final claim ceilings (frozen, per outcome)

- **INSIGHT_SURVIVES** → *"On this synthetic sphere family, LB permeability requires a box larger
  than 5 grain diameters to stabilise, which is larger than the repository's own pack-card
  guidance."* A **methods** finding about the generator/solver pair. It would **not** be a claim
  about coffee, about `wadsworth2026.permeability`'s correctness, or about real pucks, and it would
  upgrade no evidence rung.
- **BOUNDED_NULL** → *"Once realisation noise is averaged, the solver stabilises by L/d ≈ X on this
  family; the cheap screen's apparent RVE requirement was single-realisation scatter."* Equally
  publishable internally as a negative result, and it must say plainly that the cheap screen's
  SURVIVE was driven by an under-powered sweep.
- Under **every** outcome: synthetic spheres are not a real puck; numerical convergence is not
  empirical validation; no evidence rung, model verdict or public claim changes.

## 12. Issue #231

```
issue_231_disposition: NOT_MATERIAL_TO_SELECTED_DECISION
```

Unchanged from the cheap screen: no manifest dataset is consumed, so no contested evidence rung is
load-bearing.
