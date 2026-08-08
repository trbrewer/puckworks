# I-072 — do `mo2023_2.swelling` and `brewer2026.streamtube` actually disagree, or only claim to?

```
CHEAP_SCIENTIFIC_SCREEN
NOT_A_PUBLICATION_RESULT
NOT_A_MODEL_VALIDATION_UPGRADE
```

**Decision: `RETIRE`** — different questions. **Neither component was executed.**

## What was run

```
python -m puckworks.analysis.screen_i072_matched_observable
```

Writes [`result.json`](result.json) and [`figures/primary.png`](figures/primary.png). The run is
free of RNG, wall-clock input and network dependency. Repeated execution **within one fixed
numerical environment** is exactly deterministic, and that exactness is asserted
(`test_screen_is_deterministic`). **Across** the supported CI environments the committed
artifact and a fresh result must have identical structure and identical non-floating content;
computed floating leaves must agree within the narrow candidate-local portability tolerances
frozen in `tests/test_screen_i072.py` (`test_committed_result_is_cross_platform_numerically_equivalent`).
Those tolerances bound how far two builds of NumPy/SciPy/BLAS disagree on the same arithmetic —
they are **software-reproducibility tolerances, not scientific or measurement uncertainty**, and
no decision-bearing margin depends on them.

```
python -m pytest tests/test_screen_i072.py -q
```

## Bundle

| file | what it is |
|---|---|
| [`PROTOCOL.md`](PROTOCOL.md) | frozen **before** the screen module existed, in its own commit |
| [`decision.md`](decision.md) | the decision record, blueprint Appendix C shape |
| [`result.json`](result.json) | machine-readable, hash-bound to the protocol and every input |
| [`figures/primary.png`](figures/primary.png) | the primary figure |

## The short version

The protocol puts a five-part compatibility gate in front of execution. It **fails on all five**,
so the screen ends at the gate and no model is run — which is the protocol's execution rule, and
`tests/test_screen_i072.py` enforces it by replacing every forbidden entry point with a tripwire
and running the whole screen, figure included.

What the gate found is sharper than "the observables are named differently". The two components
emit **orthogonal moments of the same flow field**, and each one's output is the other's exact
structural zero:

- `brewer2026.streamtube`'s tube multipliers are **unit-mean by construction**, so the bed-total
  flow ratio `q(t)/q(0)` — the quantity `mo2023_2.swelling` exists to compute — is **identically
  1** for every σ. Max |E[k] − 1| = 3.3 × 10⁻¹⁶ (quantile-midpoint, all σ) and 6.7 × 10⁻¹⁶
  (Gauss–Hermite, σ ≤ 1.5).
- `mo2023_2.swelling` is one 1-D column with no tube index, so the across-tube dispersion — the
  quantity `brewer2026.streamtube` exists to compute — is **identically 0** for every powder.

Their declared validity domains do not intersect either: a powder identity (no dial) versus EK43
dial 1.1–1.5, with no adapter permitted (rule 9 / ledger A9, G5).

The card that generated the tension row already said this in prose — *"complementary-competing …
a bed can have both; Mo's 1-D homogeneity is silent on channeling"*. The screen's contribution is
to make it exact and checkable.

## What this does **not** say

It does not say the two components agree — components that answer different questions neither
agree nor disagree. It does not say a real bed lacks either mechanism. It changes **no**
evidence label, rung or badge: `mo2023_2.swelling` remains `source_curve_reproduction` and
`brewer2026.streamtube` remains `within_campaign_held_out`. The full ceiling is in
[`decision.md`](decision.md).

## Two things worth carrying to the next screen

- **A dimensionless output is the easy trap.** Both components emit dimensionless quantities, so
  a plot of one against the other looks admissible and passes every unit check. The
  incompatibility is in the **index** — time versus tube — which no unit or normalisation audit
  would have caught. Check what a quantity is a function of, not only what it is measured in.
- **Compute the rescue before refusing it.** The d₃₂ coincidence is real: Mo powder M lands
  inside the streamtube's dial-derived Sauter span. A screen that had asserted "different grinds"
  without computing it would have been right for a reason it could not show, and a screen that
  had stopped at the coincidence would have been wrong. The refusal rests on the granulometry
  behind the number (fines radius differs 26 %, boulder radius 37 %), which only exists because
  the check was run.
