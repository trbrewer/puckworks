# WP6-LC-IDENT Cheap Screen Decision

```
HUMAN_SELECTED_POST_SNAPSHOT
CHEAP_SCIENTIFIC_SCREEN
NOT_A_PUBLICATION_RESULT
NOT_A_MODEL_VALIDATION_UPGRADE
```

## Question

In the controlled isoresistive-mirror two-path geometry already used by the lateral-coupling
discrimination harness, is the mapping from physical lateral coupling to the pair
**(total-flow ratio `R = Q/Q₀`, separate outlet-flow share `s = q₁/Q`)** one-to-one, so that the
exact pressure-equalization number **Ξ** can be recovered without separately measuring `k_lat`
and `w`?

Human-selected from `docs/cards/lateral_coupling_feasibility.md` §4, go/no-go box 6 (*"the
inference is not structurally non-identifiable"* — **OPEN**). **Not** a generated candidate: no
`I-` number was minted, `ID_REGISTRY.json` and the generated portfolio are untouched, and the 90
candidates were not scored, ranked or inspected.

## Evidence unit

One exact steady two-path Darcy network solve (`models.lateral_coupling.model1_two_path`).
**No manifest dataset is consumed** — nothing is scored, held out, or assigned an evidence rung.
The result is synthetic/mathematical, not empirical.

## Method

Frozen in [`PROTOCOL.md`](PROTOCOL.md) before this screen's module existed, and SHA-256-bound to
it. The mirror is parameterised by the signed axial contrast `c = (a−b)/(a+b)` and `Ξ = 2G_lat/A`;
the primary case `A = 4, c = 0.5` is exactly the harness's `isoresistive_mirror` `(3,1,1,3)`.
Only **boundary** quantities are read: `Q₀` (bridge blocked), `q₁`, `q₂` (bridge open).

Six arms: analytic derivation · numerical recovery on a predeclared 10 × 22 `(c, Ξ)` grid ·
the minimum-observable test · the existing physical-vs-proxy adversary, *called* not
reimplemented · six controls · a 16-sign-corner mirror-imperfection adversary at 1 %/2 %/5 %.

## Result

### 1. The forward map and the inverse are exact

Hand-derived before execution and then falsified against the network, not assumed:

```
R(c, Ξ) = [1 − c²/(1+Ξ)] / (1 − c²)          ĉ  = (R − 1) / [R (1 − 2s)]
s(c, Ξ) = (1−c)(1 + Ξ + c) / (2(1 + Ξ − c²)) t̂  = [1 − R(1 − ĉ²)] / ĉ²      Ξ̂ = 1/t̂ − 1
```

| check | result | frozen tolerance |
|---|---|---|
| analytic map vs the exact network, 230 grid points | max abs error **0** | 1e−12 |
| recovered contrast, 220 nondegenerate points | max \|ĉ − c\| = **3.0e−12** | 1e−9 |
| recovered coupling | max \|Ξ̂ − Ξ\|/Ξ = **8.2e−11** | 1e−6 |
| injectivity, min pairwise `(R, s)` distance | **5.12e−06** (> 0) | — |

The degenerate fibre is exactly `{Ξ = 0, any c} ∪ {c = 0, any Ξ}`, because
`R = 1 ⟺ s = 1/2 ⟺ c(t−1) = 0`. Both are reported `degenerate_no_information` with `Ξ̂ = None` —
nothing is clipped, epsilon-shifted or regularised.

### 2. `Q` alone is confounded; `Q` + outlet share is not — the load-bearing arm

For an observed `R > 1` the exact solution set is a continuum,
`{(c, Ξ(c)) : √(1−1/R) < |c| < 1}`, **of both signs of `c`** — because `R` depends on `c` only
through `c²`. At each of six operating points a 24-member family was constructed and every member
reproduced the observed `R` exactly from the exact model. **None reproduced the observed `s`.**

The collapse is exact rather than numerical: along any fixed-`R` family the model satisfies

```
s − 1/2 = −(R − 1) / (2 R c)
```

identically, which is strictly monotone in `c` on each sign branch and sign-separated across them.
So one extra measurement — the separate outlet share — is *demonstrated* necessary and sufficient,
not asserted from the model having an internal state.

### 3. Controls all pass

Path swap preserves `R`, reverses `s − 1/2` and `ĉ`, and leaves `Ξ̂` unchanged. ×10 conductance
scaling multiplies `q₁`, `q₂`, `Q₀` by 10 and leaves `R`, `s`, `ĉ`, `Ξ̂` invariant. Node and global
residuals ~0; the canonical `q_lat_1to2 = G_lat(p₁−p₂)` sign holds everywhere. The identical-path
and `Ξ = 0` cases report no information. No continuous α reproduces the joint signature at any
tested Ξ: for the mirror, `s₀ = 0.5` makes the proxy share α-invariant while the frozen completion
holds `Q/Q₀ = 1`, so it misses **both** observables at once.

### 4. Practical resolution — calculated, and demanding

Hypothetical scenarios only, reusing the existing 1 %/2 %/5 % floor convention: each of `q₁`, `q₂`,
`Q₀` carries a relative floor `f`, over the deterministic 27-point `{−f, 0, +f}³` factorial.

| floor | Ξ recoverable within a factor of two |
|---|---|
| **1 %** | **Ξ ∈ [0.464, 2.15]** (3 of 22 grid points, contiguous) |
| 2 % | **none** |
| 5 % | **none** |

Sensitivity peaks exactly where the algebra says: `dR/dlnΞ` maximal at `Ξ = 1` (value `c²/(1−c²)/4`
= 1/12), `|ds/dlnΞ|` maximal at `Ξ = 1 − c² = 0.75` (value `c/8` = 0.0625). Conditioning degrades
as `1/Ξ` toward zero coupling and saturates for `Ξ ≫ 1`, as predicted.

## Primary figure

[`figures/primary.png`](figures/primary.png) — (a) both boundary signatures versus Ξ with the
1 %/2 %/5 % scenarios marked; (b) the confounded `Q`-only family versus the unique `Q`+share
solution, both signs of `c` shown; (c) the worst-case recovered-Ξ envelope per scenario and the
well-conditioned window.

## Adversarial check

**Deterministic 16 sign corners** of `(a,b,b,a)·(1 ± δ)` at δ = 1 %, 2 %, 5 %, run through the
**exact general network**, with the ideal mirror inverse then misapplied to the boundary data.

| δ | worst \|Ξ̂ − Ξ\|/Ξ, ideal inverse | median | worst \|ĉ − c\| | calibrated-axials inversion |
|---|---|---|---|---|
| 1 % | **4.33** | 0.103 | 0.230 | **exact** (0, bisection agrees) |
| 2 % | **6.01** | — | — | **exact** |
| 5 % | **12.59** | — | — | **exact** |

So the adversary **bites**: a 1 % asymmetry can return a Ξ off by a factor of ~5. It bites least
inside the well-conditioned window (worst bias 0.18 at Ξ = 0.75 and Ξ = 1.0) and worst at Ξ = 19
(4.33) and Ξ = 0.05 (1.07) — the same window is both the most resolvable and the most robust.

Three things are kept distinct and all three are reported: **structural identifiability of the
ideal design** (exact); **bias from assuming unverified symmetry** (large); **recoverability with
independently calibrated axial segments** (exact for *any* geometry, no symmetry assumed, via the
closed-form Möbius inversion `G = [(Q/P)A₁A₂ − N₀]/[M − (Q/P)S]`, cross-checked by bisection).

## Strongest alternative explanation

*"The inverse is an artifact of exact mirror symmetry."* **Partly true, and it bounds the claim.**
Two post-hoc diagnostics (labelled `POST_HOC_DIAGNOSTIC_NOT_IN_DECISION`; neither feeds any
decision clause):

- **The blocked-bridge outlet share is a partial boundary test of the symmetry.** On the 16-corner
  set it flags *exactly* the biasing corners: the 4 of 16 that remain exact mirrors have zero
  blocked-share departure and zero Ξ bias; all 12 that break the mirror show both.
- **But it is necessary, not sufficient.** A one-parameter family of genuinely different
  geometries — Ξ spanning **0.3125 to 2.5, a factor of 8** — reproduces **all four** boundary flows
  exactly *and* has blocked-share exactly 0.5 for every member. The blocked run fixes only the two
  end-to-end **series** conductances; each lane's top/bottom **split** is invisible to it.
  Parameter counting agrees: 5 unknowns, 4 boundary numbers, 1-dimensional deficiency.

**Conclusion:** boundary flows do not identify Ξ for an *arbitrary* two-lane apparatus. The mirror
**construction** is what closes the system — and it is a design assumption about the fixture, not a
measurement of `k_lat` or `w`. That distinction is preserved in the licensed claim.

A separate bounded finding: `model1_two_path` forms `det = a·d − G_lat²` and loses
~`log10(G_lat/A)` significant digits to cancellation. The first Ξ deviating from the analytic map
by more than 1e−9 is **Ξ = 1e9**; this screen's grid tops out at **Ξ = 1e3**, six orders inside the
sound region. It is a floating-point conditioning limit, **not** a physical defect and not a defect
that invalidates this inference.

## Decision

**SURVIVE**

All seven frozen clauses evaluate true, and a finite measurement-resolution requirement was
calculable without any new empirical input — so the `NEEDS_NEW_DATA` arm does not apply.

## Why

The map is one-to-one on the nondegenerate domain, the inverse is exact against the model, every
control holds, the degeneracies report no information rather than a number, `Q` alone is
demonstrably confounded while `Q` + outlet share is demonstrably unique, and the frozen share
proxy cannot reach the joint signature at any α.

## Claim ceiling

**The strongest thing this licenses anyone to say, verbatim:**

> In the exact two-path mirror design, effective lateral coupling Ξ is structurally identifiable
> from blocked/open total-flow measurements and separate outlet-flow share. Separate `k_lat` and
> `w` measurements are not mathematically necessary to infer Ξ, although they remain necessary to
> decompose or physically interpret the effective conductance.

And nothing beyond it. This is a cheap scientific screen: **synthetic/mathematical identifiability
in an exact steady two-path Darcy network under a controlled mirror geometry — not empirical
validation of anything.** It promotes **no** evidence rung. It produces **no** real-puck Ξ and
**no** `k_lat` estimate. It makes **no** claim that espresso occupies the transition regime or any
regime. The 1 %/2 %/5 % figures are hypothetical resolution scenarios, **not** instrument
accuracies, **not** experimental uncertainty; **no apparatus is shown able to attain the required
precision**. **Paper 4 remains NOT authorized.**

## Next action

1. A narrowly scoped factual correction to `docs/cards/lateral_coupling_feasibility.md` §4,
   closing **box 6 only** and qualifying the *"needs k_lat and w"* parenthetical on box 5. Box 5
   (accessible experiment) and real-puck transfer stay **OPEN**.
2. [`DECISIVE_EXPERIMENT.md`](DECISIVE_EXPERIMENT.md) — the smallest experiment this implies: a
   two-lane, two-layer hydraulic analog with a blockable lateral bridge. It is a **specification**,
   not an authorization to build, and it does not authorize Paper 4.

## Reproduction

```
python -m puckworks.analysis.screen_wp6_lateral_identifiability --write
python -m puckworks.analysis.screen_wp6_lateral_identifiability --verify
python -m pytest tests/test_screen_wp6_lateral_identifiability.py -q
```

Sub-second, deterministic, no compute campaign. `result.json` carries a `content_sha256` and the
SHA-256 of the protocol and every load-bearing source.

## Source commit

`f77d0e328496dc1e85bf00fdb06ccdc52d8b2108` (branch
`insights/lateral-coupling-identifiability-screen`).
