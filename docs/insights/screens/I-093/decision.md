# I-093 Cheap Screen Decision

```
CHEAP_SCIENTIFIC_SCREEN
NOT_A_PUBLICATION_RESULT
NOT_A_MODEL_VALIDATION_UPGRADE
```

## Question

Across the geometries the pack generator can produce, does the continuum closure reproduce the
pore-scale solver's permeability trend? (Candidate **I-093**, tension row **T-0174**, lens
`scale_mismatch`.)

## Evidence unit

One generated voxel geometry, read by **both** routes. No manifest dataset is consumed: this
screen compares two computational routes, so nothing is scored, held out, or assigned an evidence
rung.

## Method

Frozen in [`PROTOCOL.md`](PROTOCOL.md) before this screen existed. Grain radius exactly 10 voxels
(the pack card's admissibility floor), R = 310.8 µm and porosity 0.40–0.65 — both inside
`wadsworth2026.permeability`'s declared ⟨R⟩ 145–818 µm and φ_p 0.37–0.67. `brewer2026.lb_reference`
is the anchor; `lb_taichi` is not used.

- **Comparability gate** (fail-closed, before any solve): **passed 4/4**.
- **Positive control**: `channel_verification` reproduces the exact plane-Poiseuille permeability
  to **0.052 %** (k = 80.125 vs 80.083 lu², converged). The solver is sound on a geometry with an
  analytic answer.
- **RVE sweep first**, then the porosity family at L = 64, two seeds per porosity.
- Total compute **3938 s of the 7200 s budget**; run locally, not in CI.

## Result

### 1. The pore-scale solver does not converge in box size — the decisive finding

| L | L/d (grain diameters) | φ | k [lu²] | steps |
|---|---|---|---|---|
| 32 | 1.60 | 0.4940 | 3.160 | 600 |
| 48 | 2.40 | 0.4951 | 3.120 | 1000 |
| 64 | 3.20 | 0.4896 | 4.616 | 1200 |
| 80 | 4.00 | 0.4977 | 4.210 | 1400 |
| 100 | **5.00** | 0.4977 | **5.135** | 1400 |

The sweep **reached the pack card's own ≥5-grain-diameter box guidance** and `k` is still moving:
the change between the two largest boxes is **18.0 %** against the frozen 5 % criterion, the
sequence is **non-monotone**, and `k` is still rising at the largest box. No `L*` satisfies the
frozen stabilisation criterion.

**This is not a compute bound.** The budget was not exhausted (3938 s of 7200 s) and the card's
declared box guidance *was* reached. The candidate's INCONCLUSIVE arm — "the solver cannot be run
at an RVE size large enough to stabilise" — therefore does **not** apply.

### 2. The ratio is not flat across the family — secondary, and confounded

At L = 64 the ratio `k_LBM/k_closure` spans **27.5–80.7** for the percolation closure
(**G = 2.94**) and **2.8–6.3** for Carman–Kozeny (**G = 2.51**), against a frozen agreement floor
of **1.39** (the larger of the measured solver uncertainty U = 1.392 and the closure's own
published ×/1.31 collapse scatter).

The ratio falls **systematically and monotonically with porosity** for both closures (figure panel
b): both continuum forms rise more steeply with φ than the pore-scale solve does on these sphere
packs. A systematic monotone trend in φ is not what uncorrelated realisation noise looks like,
which is why it is reported — but see the confound below before reading it as established.

## Primary figure

[`figures/primary.png`](figures/primary.png) — (a) both routes on the same geometry; (b) the trend
test, is the ratio flat; (c) RVE stabilisation with the pack card's ≥5-grain-diameter line marked.

## Decision

**SURVIVE**

Applied from the candidate's own frozen rule, unrevised: *"SURVIVE if the closure and solver
trends diverge inside the geometry family, **or** no RVE size stabilises the solver."* **Both**
arms evaluate true under the criteria fixed before execution. The RVE arm is the cleaner of the
two.

## The confound this screen cannot resolve — stated plainly

**The RVE arm is confounded with geometry-realisation noise, and that is a limitation of my own
screen design, not of the data.** The frozen protocol swept box size at **one seed**, while the
family measured seed-to-seed spread at fixed L of **1.05–1.39** (5–39 %, and 23 % at the swept
porosity φ_s = 0.50). The 18 % change between the two largest boxes is *the same order* as
realisation variance at fixed box size. So on this evidence alone I cannot separate:

- a genuine representative-elementary-volume requirement larger than 5 grain diameters, from
- single-realisation scatter that would average out over seeds.

The trend arm inherits the problem: `G` was measured at L = 64 on solver output that is **not**
RVE-converged, so RVE bias cannot be separated from a true closure/solver shape mismatch. `U_rve`
in `result.json` (1.112) is computed as k(64)/k(100) and **understates** the real RVE uncertainty,
because a non-converged sequence has no bounded uncertainty at all.

This is exactly what deep maturation is for, and it is the first thing
[`DEEP_SCREEN_PROTOCOL.md`](DEEP_SCREEN_PROTOCOL.md) must resolve: a multi-seed RVE sweep that
separates box-size dependence from realisation variance.

## Adversarial checks

None overturned the decision; two changed how it must be read.

- **A1 — synthetic spheres are not a real puck.** Accepted and unrefuted. The generator makes
  overlapping spheres; the closure was fitted to angular coffee grains. This screen cannot test
  representativeness and does not try. It is the reason the ceiling is bounded to the synthetic
  family.
- **A2 — is the divergence merely the angularity term?** No. G with α = 0 is **2.936** versus
  2.936 with the declared α = 4808 /m — identical, because `exp(−2αR)` is porosity-independent at
  fixed R and so shifts the prefactor without touching the trend spread.
- **A3 — connected vs total porosity.** G is **unchanged** (2.936). The reason matters and is not
  flattering to either route: `lb_reference` reports the total fluid fraction, which here equals
  the pack porosity exactly, so **neither route computes connected porosity** and closed pores are
  counted as pore space by both. The check does not discriminate; it documents a shared
  limitation.
- **A4 — is the finding specific to the percolation form?** No. Carman–Kozeny shows the same
  systematic decline (G = 2.51). Both continuum forms are steeper in φ than the solver.
- **A5 — is G inside seed noise?** No: U_seed = 1.392 versus G = 2.94, about 2×. But this compares
  G against *seed* noise only; it does not address the *RVE* confound above.

## Strongest alternative explanation

The candidate's own: **the synthetic geometries are not representative of a real puck, so neither
curve is the reference.** Accepted, unrefuted, and load-bearing on the ceiling. Nothing here
adjudicates `wadsworth2026.permeability`'s own coffee-XCT validation, which used real geometry and
is untouched.

A second alternative, raised by the result itself: the non-stabilisation may be a property of
*overlapping-sphere packs at these porosities* rather than of the solver or of porous media
generally. This screen cannot distinguish those either.

## Claim ceiling

- A **cheap screen** over a synthetic overlapping-sphere family at one grain radius. Not a
  publication result; not a validation-strength promotion.
- It does **not** establish real-puck representativeness.
- It does **not** validate or invalidate `wadsworth2026.permeability`; its coffee-XCT validation is
  untouched and unadjudicated here.
- It does **not** upgrade `brewer2026.lb_reference` beyond `code_verification` or
  `brewer2026.pack_generator` beyond `qualitative_capacity`.
- The closure is itself LB-anchored (`docs/cards/wadsworth2026.md`: *"Validated by XCT + LBflow on
  2 coffees × 11 grinds"*), so agreement would have been weak evidence; divergence is the
  informative direction — but see the confound.
- **Numerical non-convergence is not empirical invalidation.** The strongest defensible statement
  today is: *on this synthetic family, the pore-scale route has not been shown to be RVE-converged
  at or below 5 grain diameters, and until it is, no trend comparison against a continuum closure
  on these geometries can be treated as established.*

## Next action

Deep maturation is unlocked by this SURVIVE and runs in the same cycle — beginning with the
multi-seed RVE sweep that the confound above demands. See
[`DEEP_SCREEN_PROTOCOL.md`](DEEP_SCREEN_PROTOCOL.md).

This candidate is **not** retired and is **not** in `RETIRED_CANDIDATES.md`.

## Issue #231

```
issue_231_disposition: NOT_MATERIAL_TO_SELECTED_DECISION
```

This screen consumes no manifest dataset, so no evidence rung — contested or otherwise — is
load-bearing for its decision or its maximum claim. No `de1_fixtureA` authority is read or relied
upon.

## Reproduction

```
python -m puckworks.analysis.screen_i093_crossscale_permeability
python -m pytest tests/test_screen_i093.py -q
```

Runs locally, ~66 min CPU. Not a CI job.

## Source commit

Base `892e5ec78f7a0dcf1b1f2de85ccfff8f39e0effa`. `result.json` binds the SHA-256 of `PROTOCOL.md`
and of every load-bearing input.
