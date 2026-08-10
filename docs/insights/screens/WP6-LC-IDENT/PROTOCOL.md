# WP6-LC-IDENT — lateral-coupling identifiability protocol (FROZEN BEFORE EXECUTION)

```
HUMAN_SELECTED_POST_SNAPSHOT
CHEAP_SCIENTIFIC_SCREEN
NOT_A_PUBLICATION_RESULT
NOT_A_MODEL_VALIDATION_UPGRADE
```

**This document is committed before the screen module exists**, and it is what the screen is bound
to. Question, domain, observables, grids, controls, adversarial checks, sensitivity treatment,
decision rule, claim ceiling and stop conditions are fixed here and are **not revised after seeing
output**.

---

## 1. Authority

| item | value |
|---|---|
| base commit | `f77d0e328496dc1e85bf00fdb06ccdc52d8b2108` |
| base tree | `e305f2a57fca65b872ed62443f3b85520bb36f68` |
| base branch | `main`, identical to `origin/main`, working tree clean |
| screen branch | `insights/lateral-coupling-identifiability-screen` |
| screen identity | **`WP6-LC-IDENT`** (a stable slug — see §2) |
| governing card | `docs/cards/lateral_coupling_feasibility.md` §4, boxes 5 and 6 |
| roadmap gap | **G-lat** (`docs/ROADMAP.md` §4) |

**Load-bearing input hashes (SHA-256 at the base commit):**

```
puckworks/models/lateral_coupling.py                      ba1468993b6daed6ea703dab080727353c9cab3651ea84282df68b9e2e8f4ec0
puckworks/analysis/lateral_coupling_discrimination.py     8adbfb8317d0518cf229cd24e29242198138250b343dbf81048857a42b2efcf6
puckworks/analysis/lateral_proxy.py                       b72e5ff7b4c2b6558ad6bbadaff83789977df0f7aa29aff04c10d0bfda197756
docs/cards/lateral_coupling_feasibility.md                5babe8ab2311a7f908faca861e63289084ed37b0aeeea58de5c480bb774bbd01
CLAUDE.md                                                 e235f2e5f3387fa2309bea5139728db2f1556c5725b3b35c1fdb6b23a50b5665
docs/ONBOARDING.md                                        90fd26757897c49106f0f6826d1dec7e342f094892c0ec1299e4d012f5b344bb
```

The screen module recomputes these at run time and records them in `result.json`. A changed
load-bearing hash is recorded, not silently absorbed.

## 2. Candidate-selection record — and why this is not an `I-` number

This question was **selected by a human from a live model card**, not drawn from the generated
candidate portfolio. The 90-candidate portfolio at this base predates it and does not contain it.

**Selection route and reasoning.** `docs/cards/lateral_coupling_feasibility.md` §4 carries two OPEN
go/no-go boxes. Box 6 — *"the inference is not structurally non-identifiable"* — has never been
tested: the repository contains forward maps only and **no inverse anywhere** (§3). It is decidable
with algebra plus a model already in the tree; it needs no new dataset, no new machinery and no
compute campaign; and it directly challenges the box-5 parenthetical *"needs `k_lat` and `w`"*,
which asserts a measurement requirement that has never been checked against the model's own
structure. **No score field, ranking, lens or generator change was introduced, and the 90
candidates were not scored, ranked or inspected.**

The Insight Foundry has **no sanctioned identity mechanism for a post-snapshot human-selected
screen**: `docs/insights/ID_REGISTRY.json` is append-only and its `I-` numbers are content
fingerprints over *generated* candidate records (`INSIGHT_FOUNDRY_DESIGN.md` §1a). Minting an
`I-` number here would either require editing the generator or hand-editing the append-only
registry — both forbidden by `CLAUDE.md`.

So this screen uses a **stable slug**, `WP6-LC-IDENT`, and is labelled
`HUMAN_SELECTED_POST_SNAPSHOT` wherever it appears. Explicitly **not done by this screen**:

- no Foundry lens added or changed;
- no candidate generator added or changed;
- no portfolio scoring, ranking or rescoring — the 90 candidates were **not** inspected, scored or
  ordered;
- `docs/insights/ID_REGISTRY.json` untouched;
- `docs/insights/generated/**` untouched;
- no candidate card materialised.

## 3. Bounded duplicate check (narrow, not a portfolio review)

Searched at the base commit for lateral-coupling identifiability, inversion of Ξ or `G_lat`,
boundary-only inference, mirror-path inversion, and total-flow-plus-outlet-share inference:

| where | finding |
|---|---|
| `docs/cards/lateral_coupling_feasibility.md` §4 | box 6 — *"the inference is not structurally non-identifiable"* — is **`[ ]` OPEN**. Box 5 — *"at least one accessible experiment/dataset can estimate Ξ (needs k_lat and w)"* — is **`[ ]` OPEN**. |
| `puckworks/models/lateral_coupling.py` | forward maps only (`model1_two_path`, `equalization_number`, `gap_remaining_fraction`). **No inverse anywhere.** |
| `puckworks/analysis/lateral_coupling_discrimination.py` | the only "inverse" in the module is `alpha_raw = (s − s₀)/(0.5 − s₀)`, the inverse of the **proxy share map** in α. It does not invert for Ξ or `G_lat`. |
| `docs/analysis/generated/lateral_coupling_discrimination.md` | closes with *"the measurability and identifiability go/no-go boxes stay OPEN"*. |
| `tests/test_lateral_coupling.py`, `tests/test_lateral_discrimination.py` | forward properties only (limits, conservation, swap, scaling). No recovery test. |
| `docs/insights/` screens I-010/024/040/045/072/076/090/093, `RETIRED_CANDIDATES.md` | none touches lateral coupling. |

**The question is open and is not duplicated.** Proceed.

## 4. Exact scientific question (frozen)

> In the controlled isoresistive-mirror two-path geometry already used by the lateral-coupling
> discrimination harness, is the mapping from physical lateral coupling to the pair
>
> **(total-flow ratio `R = Q/Q₀`, separate outlet-flow share `s = q₁/Q`)**
>
> one-to-one, so that **Ξ** can be recovered without separately measuring `k_lat` and `w`?

The primary result concerns **Ξ**, the exact pressure-equalization number
`Ξ = G_lat·(1/A₁ + 1/A₂)` — **not** the legacy provisional Λ regime labels, which appear nowhere
in this screen's result.

### Model domain

The exact steady two-path Darcy network `puckworks.models.lateral_coupling.model1_two_path`
only, under the existing `P_out = 0` gauge and the canonical sign convention
`q_lat_1to2 = G_lat·(p₁ − p₂)`. No N-path network, no PDE, no extraction clock, no time
dependence, no real data.

### Geometry parameterisation (frozen)

The isoresistive-mirror construction already in the harness:

```
g1_top = a     g1_bot = b     g2_top = b     g2_bot = a
```

so `A₁ = A₂ = A = a + b`. Signed axial contrast and coupling number:

```
c  = (a − b)/(a + b),   −1 < c < 1
Ξ  = G_lat·(1/A₁ + 1/A₂) = 2·G_lat/A
```

Inverted for construction: `a = A(1+c)/2`, `b = A(1−c)/2`, `G_lat = Ξ·A/2`. The **primary case is
`A = 4`, `c = 0.5` → (a, b) = (3, 1)**, exactly the harness's `isoresistive_mirror`. `P_in = 9.0e5`
(the harness value).

### Observables (the complete measured set)

```
Q0  total flow, lateral bridge BLOCKED   (G_lat = 0, same geometry)
q1  outlet flow of path 1, bridge OPEN
q2  outlet flow of path 2, bridge OPEN
Q   = q1 + q2
R   = Q / Q0
s   = q1 / Q
```

All four are **boundary** quantities. No interior pressure, no `k_lat`, no `w`, no lateral flux is
observed.

## 5. Predeclared analytic derivation (done by hand, before execution)

From the two steady node balances with `D = A + G_lat`:

```
D·p1 − G·p2 = a·P
−G·p1 + D·p2 = b·P            det = D² − G² = A(A + 2G) = A²(1 + Ξ)
```

so `p1 = P(aD + bG)/det`, `p2 = P(bD + aG)/det`, `q1 = b·p1`, `q2 = a·p2`. Writing
`ab = A²(1−c²)/4` and substituting `G = ΞA/2`, `D = A(1 + Ξ/2)`:

**Forward map** (with `t ≡ 1/(1+Ξ) ∈ (0, 1]`):

```
R(c, Ξ) = [1 − c²/(1+Ξ)] / (1 − c²)          = (1 − c²t)/(1 − c²)
s(c, Ξ) = (1−c)[1 + c/(1+Ξ)] / (2[1 − c²/(1+Ξ)])
        = (1−c)(1 + Ξ + c) / (2(1 + Ξ − c²))
```

Two exact consequences used below:

```
R − 1   =  [c²/(1−c²)]·[Ξ/(1+Ξ)]                 (≥ 0; coupling never lowers total flow here)
s − 1/2 =  −c·Ξ / (2(1 + Ξ − c²))
```

**Candidate inverse.** Since `1 − c²t = R(1−c²)`, `2s(1−c²t) = (1−c)(1+ct)` gives
`2sR(1+c) = 1 + ct`; eliminating `ct` and dividing by `(1+c)` yields `Rc(2s−1) = 1 − R`, hence

```
ĉ  = (R − 1) / [R·(1 − 2s)]
t̂  = [1 − R·(1 − ĉ²)] / ĉ²
Ξ̂  = 1/t̂ − 1
```

**These identities are predeclared but not privileged.** The screen derives nothing from this
document at run time: it evaluates `model1_two_path` and falsifies the map and the inverse against
it. If they disagree, the screen reports the disagreement and the derivation is wrong, not the
model.

### Predeclared degeneracy classification

From the exact consequences above, `R = 1 ⟺ s = 1/2 ⟺ c·(t − 1) = 0`. So the degenerate fibre is
exactly `{Ξ = 0, any c} ∪ {c = 0, any Ξ}`, both mapping to `(R, s) = (1, 1/2)`:

| case | predeclared classification |
|---|---|
| **Ξ = 0** | no coupling signature. `R = 1`, `s = 1/2` for every `c`. Inverse is `0/0` — **observationally degenerate, must be reported undefined, never regularised**. |
| **c = 0** | identical paths, no mid-node pressure difference, so no lateral flow at any `G_lat`. `R = 1`, `s = 1/2` for every Ξ. **Ξ unidentifiable.** |
| **Ξ → ∞** | saturation: `R → 1 + c²/(1−c²)`, `s → (1−c)/2`. Structural identifiability may persist while `∂R/∂lnΞ`, `∂s/∂lnΞ → 0`, so practical sensitivity deteriorates. |
| **Ξ → 0⁺** | inverse exists but both signals vanish linearly in Ξ; measurement requirement diverges. |

Singular cases are classified and reported. They are **not** hidden, clipped, epsilon-shifted or
regularised.

## 6. Frozen grids

```
signed c :  −0.90 −0.75 −0.50 −0.25 −0.10  +0.10 +0.25 +0.50 +0.75 +0.90     (10)
Xi       :  0.0  ∪  10**linspace(−4, 3, 22)                                   (1 + 22)
A        :  4.0  (primary);  40.0 (×10 scale control)
primary  :  A = 4, c = +0.50  →  (a, b) = (3, 1)   — the harness isoresistive_mirror, exactly
```

`c = 0.0` and `Xi = 0.0` rows are run **on purpose** as the degenerate controls.

## 7. Required screen arms

### A. Analytic derivation
§5 above. Recorded in `decision.md`/`README.md`. No symbolic-algebra package required.

### B. Numerical recovery
Every nondegenerate `(c, Ξ)` grid point: build the mirror conductances, run `model1_two_path`
(coupled and at `G_lat = 0`), form `(R, s)` from boundary flows only, apply the inverse, report
`|ĉ − c|` and `|Ξ̂ − Ξ|/Ξ`.

**Software tolerance (a reproducibility bound, NOT a scientific uncertainty):**

```
forward-map agreement       |R_map − R_model| ≤ 1e-12·max(1, |R|)   and likewise for s
c recovery                  |ĉ − c|            ≤ 1e-9
Xi recovery                 |Ξ̂ − Ξ|            ≤ 1e-6·max(1e-12, Ξ)
```

If a grid point exceeds these, the screen reports it as an **ill-conditioning finding at that
point**. The tolerance is not retuned to absorb it.

**Injectivity is also checked empirically**, not only algebraically: the minimum pairwise
`(R, s)` distance over all distinct nondegenerate grid points must be strictly positive, and the
closest pair is reported.

### C. Minimum-observable test (load-bearing)

1. **`Q` alone is confounded.** For any observed `R > 1` the exact solution set is the continuum
   `{ (c, Ξ(c)) : √(1 − 1/R) < |c| < 1 }` — a one-parameter family, each member reproducing `R`
   exactly. The screen constructs this family explicitly at the primary operating point and
   verifies every member reproduces the same `R` from the exact model.
2. **Does `s` collapse it?** Evaluate `s` along that same family and test whether `s` is strictly
   monotone in `c` along it (so that exactly one member matches the observed `s`).

A measurement is **not** declared necessary merely because the model has an internal state.

### D. Existing physical-vs-proxy adversary (reused, not duplicated)
`puckworks.analysis.lateral_coupling_discrimination.physical_row` is **called**, not
reimplemented. The frozen share proxy gets its strongest admissible **continuous** α fit
(`alpha_star_continuous`). No `α = f(Ξ)` law is invented. Question: can it jointly reproduce `R`
and `s` for the primary mirror case?

### E. Controls (all six run)

1. identical-path negative control (`c = 0`);
2. **path swap** `(a,b,b,a) → (b,a,a,b)` i.e. `c → −c`: `R` preserved; `s − 1/2` reverses sign;
   `ĉ` reverses; **`Ξ̂` unchanged**;
3. **×10 conductance scaling** (`A = 4 → 40` with `G_lat` scaled likewise, so Ξ is held): `q1`,
   `q2`, `Q0` scale by 10; `R`, `s`, `ĉ`, `Ξ̂` invariant;
4. zero-coupling limit (`Ξ = 0` → degenerate, reported undefined);
5. strong-coupling limit (compared against `strong_coupling_limit`);
6. conservation and sign checks under the canonical `q_lat_1to2` convention.

### F. Mirror-imperfection adversarial check

**The strongest alternative explanation:** *the inverse is an artifact of exact mirror symmetry and
will return a misleading Ξ when a real apparatus is only approximately mirrored.*

Deterministic, predeclared, **not random**: for each level `δ ∈ {1%, 2%, 5%}`, the **16 sign
corners** of `(g1_top, g1_bot, g2_top, g2_bot) = (a, b, b, a)·(1 ± δ)`. For each perturbed
geometry, at each of a predeclared Ξ set `{0.05, 0.1875, 0.75, 1.0, 5.0, 19.0}`:

- run the **exact general network** (not the mirror form);
- compute `Ξ_true` for the perturbed geometry as `G_lat·(1/A₁' + 1/A₂')` — the model's own exact
  equalization number for the geometry that actually exists;
- apply the **ideal mirror inverse** to `(R, s)`; report the bias in `Ξ̂` and `ĉ`;
- **separately**, supply the actual four conductances to a one-parameter inversion for `G_lat`
  and report its error.

The one-parameter inversion is exact, not a fit. For the general network
`Q/P = (N₀ + G·M)/(A₁A₂ + G·S)` with `N₀ = g1t·g1b·A₂ + g2t·g2b·A₁`,
`M = (g1t+g2t)(g1b+g2b)`, `S = A₁+A₂` — a Möbius function of `G`, hence invertible:

```
G_lat = [ (Q/P)·A₁A₂ − N₀ ] / [ M − (Q/P)·S ]
```

cross-checked against a bracketed bisection on the same `Q(G)`.

This must **distinguish three things**: structural identifiability of the ideal designed
experiment; bias from assuming unverified symmetry; recoverability when the real axial segments
are independently calibrated.

**The percentages are sensitivity scenarios. They are NOT claimed manufacturing tolerances.**

## 8. Sensitivity treatment — hypothetical scenarios, not an instrument model

**The repository retains no instrument or noise model for this experiment and this screen does not
invent one.** It reuses the existing 1 % / 2 % / 5 % sensitivity-floor convention already declared
in `lateral_coupling_discrimination.PRECISION_FLOORS`.

Scenario definition (frozen): each of the three independently measured flows `q₁`, `q₂`, `Q₀`
carries a relative floor `f`. The perturbation set is the **deterministic 3-level full factorial**
`(e₁, e₂, e₀) ∈ {−f, 0, +f}³` — 27 points, containing the 8 sign corners and the unperturbed
point. For each: `R' = (q₁(1+e₁) + q₂(1+e₂))/(Q₀(1+e₀))`, `s' = q₁(1+e₁)/(q₁(1+e₁) + q₂(1+e₂))`,
then the inverse.

Reported per Ξ in the primary mirror case:

- `|R − 1|`;
- `|s − 1/2|`, in absolute share units;
- `∂R/∂lnΞ` and `∂s/∂lnΞ` (closed form, from §5);
- worst-case recovered-Ξ interval `[min, max]` over the 27 scenario points, with non-physical or
  undefined points counted and reported rather than dropped;
- `recovered_within_factor_two` — true only when **all 27** points yield a finite physical `Ξ̂`
  **and** `max(Ξ̂)/Ξ ≤ 2` **and** `Ξ/min(Ξ̂) ≤ 2`.

The best-conditioned window per scenario is **calculated, not assumed**, and reported as the Ξ
interval where `recovered_within_factor_two` holds.

Throughout: these are hypothetical resolution scenarios; they are **not** instrument accuracies,
**not** experimental uncertainty, and no apparatus-feasibility claim is earned from them.

## 9. Frozen decision rule — applied without revision

**SURVIVE** if all seven hold:

1. the mirror forward map and inverse are algebraically valid;
2. the map from physical `(signed c, Ξ)` to `(R, s)` is one-to-one over the stated nondegenerate
   domain;
3. numerical recovery passes over the predeclared grid;
4. path swap and scale controls recover the same Ξ;
5. the identical-path and `Ξ = 0` cases correctly report **no information**;
6. `Q`-only inference is shown to be confounded while `Q` plus outlet share removes that
   confounding;
7. no continuous-α proxy reproduces the joint physical signature in the primary mirror case.

A SURVIVE licenses **only** this sentence:

> In the exact two-path mirror design, effective lateral coupling Ξ is structurally identifiable
> from blocked/open total-flow measurements and separate outlet-flow share. Separate `k_lat` and
> `w` measurements are not mathematically necessary to infer Ξ, although they remain necessary to
> decompose or physically interpret the effective conductance.

**RETIRE** if either: two distinct nondegenerate physical `(c, Ξ)` states produce exactly the same
`(R, s)`; or the candidate inverse fails the exact model, path-swap, scaling or conservation
controls.

**NEEDS_NEW_DATA** if structural identifiability is established but the result cannot specify a
finite measurement-resolution requirement or a minimally observable experiment without an
empirical noise or calibration input absent from the repository. **Not** to be used merely because
no apparatus has been built — the screen still calculates the resolution it would require.

## 10. Claim ceiling (binding on every output)

- cheap scientific screen; human-selected, post-snapshot;
- exact steady two-path Darcy network only;
- controlled mirror geometry only;
- **synthetic / mathematical identifiability, not empirical validation**;
- no evidence-rung promotion anywhere;
- no real-puck Ξ estimate, and no `k_lat` estimate;
- no claim that espresso occupies the transition regime, or any regime;
- **no Paper-4 authorization**;
- no proof that any apparatus can attain the required precision.

## 11. Stop conditions

Stop and report honestly if:

- the exact question turns out to be already answered in the tree;
- an applicable repository instruction forbids the work;
- a required physical parameter would have to be invented;
- the mirror construction is not implemented as assumed;
- the analytic and implemented models disagree;
- the current model has a demonstrated defect that invalidates the inference;
- the screen begins expanding toward N-path, PDE, dynamic extraction, or real-data fitting;
- completing it would require new Foundry infrastructure.

## 12. Card correction, conditional and deferred

**Only if the screen SURVIVES**, and only in a **separate, narrowly named commit made after the
result exists**, a factual correction to `docs/cards/lateral_coupling_feasibility.md` §4 may close
**box 6 only** (structural identifiability). Box 5 (accessible experiment) and the real-puck
transfer question stay **OPEN**. **Paper 4 is not authorized by this screen under any outcome.**

## 13. Budget

One executable module, focused tests, one figure, one bundle, one decision, one experiment
specification. Algebraic/network work only — sub-second execution, no compute campaign. If it
wants more, it is not a cheap screen.

---

## POST-EXECUTION FACTUAL ERRATUM — 2026-08-09

**The frozen text above is NOT rewritten.** This erratum is appended after execution, in the
repository's established style (cf. `I-076/PROTOCOL.md`, `I-093/PROTOCOL_ERRATUM.md`), because a
statement in §7F was factually incomplete.

### What §7F said

> `Q/P = (N₀ + G·M)/(A₁A₂ + G·S)` … — a Möbius function of `G`, hence invertible

### What is missing

**A nondegeneracy condition.** Differentiating,

```
d(Q/P)/dG = [M·A₁A₂ − N₀·S] / (A₁A₂ + G·S)²
          = (g1_top·g2_bot − g2_top·g1_bot)² / (A₁A₂ + G·S)²
```

so with `X ≡ g1_top·g2_bot − g2_top·g1_bot`:

- the calibrated inversion is strictly monotone, hence **one-to-one, iff `X ≠ 0`**;
- it is **structurally singular when `X = 0`**;
- `X = 0` is exactly the condition that the two **uncoupled mid-node pressures are equal**
  (`p_i(G=0) = g_i_top·P/(g_i_top+g_i_bot)`, so `p₁ = p₂ ⟺ g1_top·g2_bot = g2_top·g1_bot`). With
  no uncoupled pressure gap, no lateral pressure drives the bridge at any `G_lat`, `Q` is exactly
  independent of `G_lat`, and the boundary measurement carries **no information** about it;
- near that condition the inversion is **poorly conditioned**, `dG/d(Q/P) ~ 1/X²`, degrading
  continuously rather than failing abruptly.

A Möbius map is invertible only when its determinant is nonzero; §7F asserted invertibility
without recording that condition. `g = (2, 1, 4, 2)` is a concrete counterexample: two
*non-identical* paths with proportional top/bottom split, `X = 0`, `p₁ = p₂ = 0.6·P`, and `Q`
numerically invariant across `G_lat ∈ {0, 0.5, 5, 500}`.

### What this changes, and what it does not

**It does not affect the mirror result or any frozen decision clause.** The mirror inverse of §5
is a different route, and for the mirror `X = a² − b² = A²c`, which is nonzero for every
`c ≠ 0` on the frozen grid — i.e. exactly the nondegenerate domain the decision rule already
declares. All seven clauses of §9 are unchanged and still evaluate true; the decision remains
**SURVIVE**; card box 6 stays closed and box 5 stays open; Paper 4 stays unauthorized.

**It does change one secondary claim.** Every statement that the calibrated-axials route works
for *"any geometry"* is corrected to:

> any **nondegenerate** calibrated geometry having a **nonzero uncoupled mid-node pressure gap**
> (`g1_top·g2_bot ≠ g2_top·g1_bot`).

`invert_G_from_known_axials` now reports `structurally_degenerate_no_information` in that case
rather than returning a number, and the demonstration is in `result.json` under
`arm_f_mirror_imperfection.calibrated_inversion_degeneracy`.

## POST-EXECUTION ADDENDUM — post-hoc diagnostics added 2026-08-09

Three diagnostics were added **after** the decision and are labelled
`POST_HOC_DIAGNOSTIC_NOT_IN_DECISION`. None feeds any clause of the §9 rule — a test asserts it —
and none changed the decision:

1. **the blocked-bridge outlet share** as a partial symmetry pre-test, and the one-parameter
   geometry family it cannot see;
2. **the calibrated-inversion degeneracy** above;
3. **the continuous factor-of-two window**. §8 fixes a 22-point Ξ grid, which can only report
   *which grid points pass*; the minimum and maximum passing grid point are **not** a continuous
   boundary estimate. The crossings are located by bounded bisection in `log10 Ξ` over the same
   exact map, inverse and 27-corner rule. The frozen-grid result is reported unchanged alongside.
