# I-093 — do the continuum permeability closures preserve the pore-scale trend?

```
CHEAP_SCIENTIFIC_SCREEN
NOT_A_PUBLICATION_RESULT
NOT_A_MODEL_VALIDATION_UPGRADE
```

> ## ⚠ Deep maturation completed — this README is not the current conclusion
>
> **Deep maturation completed. The final deep disposition is `BOUNDED_NULL` under the frozen rule,
> with `finite_size_status: PASS_BY_NON_REJECTION_LOW_POWER`. This README preserves the historical
> cheap-screen SURVIVE; it is not the current scientific conclusion. The deep ensemble did not
> demonstrate convergence or determine an REV.** See **[`deep_decision.md`](deep_decision.md)**
> (and [`deep_result.json`](deep_result.json)).

**Historical cheap-screen decision: `SURVIVE`.** The one-seed sweep failed the frozen cheap
box-size criterion and therefore unlocked deep maturation, which ran in the same cycle.

## What was run

```
python -m puckworks.analysis.screen_i093_crossscale_permeability
```

Writes [`result.json`](result.json) and [`figures/primary.png`](figures/primary.png). **~66 min of
CPU, run locally — this is not a CI job** (CLAUDE.md rule 3: slow work stays out of CI). The
committed artifacts and the focused tests over them are what CI sees.

```
python -m pytest tests/test_screen_i093.py -q
```

Determinism note, in the terms Wave 3 established: the screen has no RNG beyond the *declared*
pack seeds, no wall-clock input and no network. Within one fixed numerical environment it is
exactly reproducible. Across environments the artifact's structure and non-floating content are
exact and computed floating leaves agree within the narrow portability tolerances in the focused
test — software-reproducibility tolerances, not scientific uncertainty.

## Bundle

| file | what it is |
|---|---|
| [`PROTOCOL.md`](PROTOCOL.md) | frozen **before** the screen module existed, in its own commit |
| [`decision.md`](decision.md) | the decision record, with the confound stated plainly |
| [`result.json`](result.json) | machine-readable, hash-bound to the protocol and every input |
| [`figures/primary.png`](figures/primary.png) | the primary figure |

## The short version

Two genuinely independent routes read the **same** generated voxel geometry — a pore-scale
lattice-Boltzmann solve (`brewer2026.lb_reference`, the CPU anchor) and an algebraic constitutive
closure (`wadsworth2026.permeability.k_percolation`, plus Carman–Kozeny). Because the geometry is
shared, none of the matched-domain problems that ended I-072, I-076 and I-090 can arise: no rig, no
coffee, no grinder dial, no pressure node, no observable convention to reconcile. The only
transformations are exact lattice→SI length conversions.

The solver is sound where there is an analytic answer: the plane-Poiseuille positive control
reproduces the exact permeability to **0.052 %**.

On the sphere packs the **one-seed cheap sweep did not satisfy its frozen box-size criterion**
(the multi-seed deep ensemble later returned `BOUNDED_NULL`; see
[`deep_decision.md`](deep_decision.md)). Sweeping L = 32 → 100 at fixed resolution
(1.6 → 5.0 grain diameters) gives k = 3.16, 3.12, 4.62, 4.21, **5.14** lu² — **non-monotone, still
rising at the largest box, and 18 % apart between the two largest** against a 5 % criterion frozen
before the run. The budget was not exhausted and 5.0 grain diameters *was* reached, so this is **not** a
compute bound (see the scoping correction below).

Secondarily, the ratio `k_LBM/k_closure` is not flat: it falls monotonically with porosity for
**both** closures (percolation G = 2.94, Carman–Kozeny G = 2.51, against a floor of 1.39). Both
continuum forms rise more steeply with φ than the pore-scale solve does here.

## What this does **not** say

It does not say the synthetic sphere family represents a real espresso puck — that is the
candidate's own strongest alternative, accepted and unrefuted, and it bounds everything above. It
does not validate or invalidate `wadsworth2026.permeability`, whose coffee-XCT validation used real
geometry and is untouched. It changes no evidence rung. **Numerical non-convergence is not
empirical invalidation.**

## The honest limitation, up front

**The RVE finding is confounded with geometry-realisation noise, and that is a flaw in how I froze
the protocol.** The RVE sweep used one seed; the **two-realization max/min range ratio** at fixed box size is 1.045–1.392
(≈ 4.5–39.2 % relative to the smaller value), the same order as the 18 % change between the two
largest boxes. So this screen cannot yet separate "a
real RVE requirement beyond 5 grain diameters" from "single-realisation scatter". The trend metric
inherits it, having been measured on non-converged output.

That is precisely what earns deep maturation rather than a confident headline, and resolving it
with a multi-seed sweep is the first item in [`DEEP_SCREEN_PROTOCOL.md`](DEEP_SCREEN_PROTOCOL.md).

## Two things worth carrying forward

- **A shared geometry dissolves the matched-domain problem.** Three Wave-3 candidates died because
  two routes could not be brought onto one scenario. Generating the geometry both routes read
  removes that class of blocker entirely — worth remembering when selecting future candidates.
- **Measure realization variability before interpreting a control-variable sweep.** The RVE sweep varied
  box size while realisation variance at fixed box size was never measured first. Had the family's
  seed spread been computed before the sweep rather than after, the protocol would have frozen a
  multi-seed RVE criterion from the start.

## Correction — what the "≥5 grain diameters" figure actually scopes

**Added after execution, on inspecting the registry text verbatim.** This bundle (and the frozen
`PROTOCOL.md` §6b) described ≥5 grain diameters as *"the pack card's declared box guidance"*, which
implied a permeability-representativeness statement. It is not one.

`brewer2026.pack_generator`'s declared range reads, in full:

> `grain radius >= 10 voxels; columns >= 5 grain diameters for sigma`

The ≥5 figure is scoped **to sigma** — the columnar heterogeneity field — and there is **no pack
card** in `docs/cards/`. **The repository has never claimed that 5 grain diameters is sufficient
for permeability**, so this screen contradicts no existing repository statement and **no card
correction is warranted or made.**

What changes, and what does not:

- **The decision does not change.** The frozen rule was applied as written and returned SURVIVE.
- **The measurement does not change.** The one-seed sweep had not satisfied its frozen cheap
  criterion by L/d = 5.0, whatever that figure was originally scoped to.
- **The framing does change.** Reaching 5 grain diameters is *not* reaching a declared permeability
  guidance, so the SURVIVE-vs-INCONCLUSIVE boundary drawn in this screen rests on a threshold with
  no repository-declared anchor for this observable. The result is better read as a **positive
  measurement** — the first domain-size calibration for this generator/solver pair — than as a
  finding against any existing guidance.

`PROTOCOL.md` is deliberately **left byte-unchanged**: it is the frozen record, `result.json` binds
its SHA-256, and editing it would both break that binding and make the mischaracterisation look
anticipated. It is corrected here instead.
