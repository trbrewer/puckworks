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
`I-` number was minted; `ID_REGISTRY.json` and `docs/insights/candidates/` are **byte-unchanged** and the Foundry code (lenses, generators, scoring) is unchanged; `docs/insights/generated/**` was **regenerated** through `python -m puckworks.insights write`, never hand-edited — in the complete candidate and tension payloads only `source_commit`/`commit` provenance moved, and in `snapshot_manifest.json` the snapshot commit, the corrected card's input hash and the derived output hashes moved, with all other normalised manifest structure and content equal; and in `corpus_map.json` the corrected card's own entity attrs (`card_sha256`, `section_names`, `section_hashes`) moved — the map recording the card it is supposed to record, with no other entity, relation, warning or count touched. The 90
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
| analytic map vs the exact network, 230 grid points | agrees **to machine precision** (live max ≈ **8e−15**) | 1e−12 |
| recovered contrast, 220 nondegenerate points | max \|ĉ − c\| = **3.0e−12** | 1e−9 |
| recovered coupling | max \|Ξ̂ − Ξ\|/Ξ = **8.2e−11** | 1e−6 |
| injectivity, min pairwise `(R, s)` distance | **5.12e−06** (> 0) | — |

The first row is **floating-point agreement, not an algebraic-identity claim**. The analytic map
and the network solve are the same algebra evaluated two ways, so their difference is pure
rounding: the live maximum is 7.99e−15 in this environment and records as `0.0` in `result.json`
only after that artifact's 12-decimal rounding. The identity claim is the derivation itself, which
is a separate thing. `forward_map_max_abs_error_log10_upper_bound` records the exponent bound.

The degenerate fibre is exactly `{Ξ = 0, any c} ∪ {c = 0, any Ξ}`, because
`R = 1 ⟺ s = 1/2 ⟺ c(t−1) = 0`. Both are reported `degenerate_no_information` with `Ξ̂ = None` —
nothing is clipped, epsilon-shifted or regularised.

### 2. `Q` alone cannot *jointly* identify `(c, Ξ)`; `Q` + outlet share can — the load-bearing arm

**Stated exactly, because the unqualified form is wrong:** *when the signed axial contrast `c` is
not independently known*, total flow alone cannot jointly identify `(c, Ξ)`; adding the separate
outlet share identifies both in the exact nondegenerate mirror design.

**The full hierarchy — each rung demonstrated on the exact model** (`observable_hierarchy` in
`result.json`):

| what is known | observables | identifies |
|---|---|---|
| the mirror contrast `c`, independently and **nonzero** | `R` | **Ξ** — `R` alone *is* sufficient here |
| only that the fixture is built as an exact mirror | `R`, `s` | **`c` and Ξ** — the frozen primary result |
| all four axial conductances, calibrated and **nondegenerate** | pressure-normalised total flow | **`G_lat`** — no symmetry assumed |
| nothing beyond boundary flows (general geometry) | `q₁, q₂` blocked and open | **nothing** — 5 unknowns, 4 numbers |

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

| floor | frozen 22-point grid — points passing | continuous crossings (post-hoc) |
|---|---|---|
| **1 %** | **3 of 22**: Ξ = **0.464, 1.0, 2.154** | **Ξ ≈ 0.241 → 3.946** |
| 2 % | **0 of 22** | **no passing interval** |
| 5 % | **0 of 22** | **no passing interval** |

**The frozen result is the grid column, and it can only say which of 22 points pass** — the
minimum and maximum passing point are **not** a continuous boundary and must never be quoted as
one. The continuous column is a separate `POST_HOC_DIAGNOSTIC_NOT_IN_DECISION` that locates the
crossings by bounded bisection in `log10 Ξ` over the *same* exact map, inverse and 27-corner rule
(701-point scan, 60 halvings, no new dependency and no new threshold). It feeds no decision
clause — a test asserts that — and it confirms independently that **no continuous passing interval
exists at 2 % or 5 %**.

Sensitivity peaks exactly where the algebra says: `dR/dlnΞ` maximal at `Ξ = 1` (value `c²/(1−c²)/4`
= 1/12), `|ds/dlnΞ|` maximal at `Ξ = 1 − c² = 0.75` (value `c/8` = 0.0625). Conditioning degrades
as `1/Ξ` toward zero coupling and saturates for `Ξ ≫ 1`, as predicted.

**No silent caps.** The plotted `[Ξ̂_min, Ξ̂_max]` band spans only the scenario corners that returned
a *physical* inverse. Many returned none — at Ξ = 1e−4, 21 of the 27 corners — so **where corners
were dropped the true spread is worse than the band drawn**. Affected grid points: **15 of 22 at
1 %, 18 of 22 at 2 %, 22 of 22 at 5 %**. They are counted in `result.json`
(`n_grid_points_with_unrecoverable_corners`, `Xi_with_unrecoverable_corners`) and marked with ✕ on
the figure rather than dropped quietly. The `recovered_within_factor_two` flag is unaffected: it
requires **all 27** corners to return a finite physical Ξ̂, so it never benefits from a dropped one.

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

The inverse **partially self-diagnoses**, which is worth stating precisely because it is not a
rescue: at 1 % every one of the 96 corner×Ξ rows returns a physical-looking answer (0 flagged); at
2 %, 2 of 96 return an impossible one (\|ĉ\| ≥ 1 or t̂ outside (0,1]); at 5 %, 9 of 96 do. So a
badly mirrored fixture *sometimes* announces itself — and **87 of 96 times at 5 % it instead
returns a plausible, wrong Ξ**. An impossible answer is informative; a possible one is not
evidence the fixture was a mirror.

So the adversary **bites**: a 1 % asymmetry can return a Ξ off by a factor of ~5. It bites least
inside the well-conditioned window (worst bias 0.18 at Ξ = 0.75 and Ξ = 1.0) and worst at Ξ = 19
(4.33) and Ξ = 0.05 (1.07) — the same window is both the most resolvable and the most robust.

Three things are kept distinct and all three are reported: **structural identifiability of the
ideal design** (exact); **bias from assuming unverified symmetry** (large); **recoverability with
independently calibrated axial segments** — exact for any **nondegenerate** calibrated geometry
having a **nonzero uncoupled mid-node pressure gap**, no symmetry assumed, via the closed-form
Möbius inversion `G = [(Q/P)A₁A₂ − N₀]/[M − (Q/P)S]`, cross-checked by bisection.

**Correction (2026-08-09) — the calibrated route is not valid for "any geometry".** An earlier
wording of this screen said so; that is false in exactly one structural case. Differentiating the
Möbius form,

```
d(Q/P)/dG = [M·A₁A₂ − N₀·S]/(A₁A₂ + G·S)²  =  (g1_top·g2_bot − g2_top·g1_bot)² / (A₁A₂ + G·S)²
```

so with `X ≡ g1_top·g2_bot − g2_top·g1_bot` the inversion is one-to-one **iff `X ≠ 0`**, and `X = 0`
is exactly the condition that the two **uncoupled mid-node pressures are equal** — no lateral
driving pressure at any `G_lat`, so `Q` carries no information about it. Two consequences worth
keeping: the derivative is a *square*, so `Q` is non-decreasing in `G_lat` for every admissible
geometry; and the failure is **continuous**, `dG/d(Q/P) ~ 1/X²`, not abrupt.

**Structural degeneracy and numerical near-degeneracy are kept strictly apart** — conflating them
would assert a falsehood. Three classes, never two:

| class | condition | what is true |
|---|---|---|
| `structurally_degenerate_no_information` | **`X = 0` exactly** | uncoupled mid-node pressures equal; `Q` **exactly** independent of `G_lat`. The only structural case. |
| `numerically_unresolved_near_degenerate` | `X ≠ 0`, `X²` below the numerical-resolution threshold | the map **is** injective and `Q` is **not** independent of `G_lat`; this implementation declines to return a number because `dG/d(Q/P) ~ 1/X²` is too ill-conditioned. **No claim of exact equality.** |
| resolved | otherwise | the exact inversion runs unchanged |

Demonstrated rather than asserted (`calibrated_inversion_degeneracy`): `g = (2, 1, 4, 2)` — two
**non-identical** paths with proportional top/bottom split — has `X = 0` exactly, `p₁ = p₂`, and
`Q` exactly invariant across `G_lat ∈ {0, 0.5, 5, 500}`. By contrast `g = (2, 1, 4, 2.000001)` has
`X = 2e−6 ≠ 0`, an uncoupled pressure gap of **0.1 Pa** (not zero) and a `Q` span of 8.7e−15 (not
zero): it is reported `numerically_unresolved_near_degenerate`, **not** as a degeneracy. A resolved
near-degenerate row (`X = 0.04` against the mirror's `X = 8`) shows the conditioning decay
directly: recovery error grows from 2e−12 to 1.6e−8, tracking `1/X²`. **A real fixture therefore needs a margin on the uncoupled pressure gap,
not merely a nonzero one.** The erratum is appended to `PROTOCOL.md` rather than rewritten into
its frozen text. The mirror route is unaffected: there `X = A²c`, nonzero for every `c ≠ 0` on the
frozen grid — precisely the nondegenerate domain the decision rule already declares.

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
