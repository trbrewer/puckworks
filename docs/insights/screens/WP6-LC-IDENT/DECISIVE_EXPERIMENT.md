# The smallest decisive experiment implied by WP6-LC-IDENT

```
HUMAN_SELECTED_POST_SNAPSHOT
CHEAP_SCIENTIFIC_SCREEN
NOT_A_PUBLICATION_RESULT
NOT_A_MODEL_VALIDATION_UPGRADE
```

**This is a specification, not an authorization to build, and not a claim that it is feasible.**
It follows from [`decision.md`](decision.md) and inherits its claim ceiling. **Paper 4 remains NOT
authorized.** Nothing here estimates a real puck's Ξ, and no apparatus is shown able to reach the
precision the screen calculates.

## 1. Concept — a two-lane, two-layer hydraulic analog

Not an espresso machine campaign. A rigid fixture with:

- **two adjacent axial lanes of equal uncoupled end-to-end resistance** (isoresistive);
- **lane 1**: high-conductance material above low-conductance material;
- **lane 2**: the same two materials in the **opposite order** (the mirror);
- **a controlled lateral bridge** joining the lanes at mid-depth, which can be **blocked or
  open** in the *same* fixture without disassembly;
- **the two outlet streams collected separately.**

This is the physical realisation of `(g1_top, g1_bot, g2_top, g2_bot) = (a, b, b, a)`. The design
target is the well-conditioned window the screen calculated: **Ξ ≈ 0.5–2**, and an axial contrast
near `c = 0.5` (a 3:1 conductance ratio between the two materials).

## 2. Minimum measurements

| quantity | why |
|---|---|
| inlet-to-outlet pressure difference | fixes the drive; the network is linear in it |
| **Q₀** — total flow, bridge **blocked** | the uncoupled reference |
| **Q** — total flow, bridge **open** | gives `R = Q/Q₀` |
| **q₁, q₂** — separate outlet flows, bridge **open** | gives `s = q₁/(q₁+q₂)` |
| **q₁⁰, q₂⁰** — separate outlet flows, bridge **blocked** | the symmetry pre-test (§5) |
| fluid temperature / viscosity basis | Darcy conductance is μ-dependent; must be held or recorded |
| geometry and packing records | establishes what was held fixed between blocked and open runs |

## 3. Primary derived quantities

```
R  = Q / Q0
s  = q1 / (q1 + q2)
ĉ  = (R − 1) / [R (1 − 2s)]
t̂  = [1 − R(1 − ĉ²)] / ĉ²
Ξ̂  = 1/t̂ − 1
```

verified exact against the model over the frozen grid (max relative error 8.2e−11).

## 4. Required controls

1. **Blocked lateral bridge** — the uncoupled reference, same fixture, same packing.
2. **Identical-path negative control** — both lanes built the same way. Predicts `R = 1`,
   `s = 1/2` at *every* coupling; any departure is apparatus asymmetry, not lateral coupling.
3. **Path-swapped mirror cell** — lanes exchanged. Predicts `R` and `Ξ̂` preserved, `s − 1/2`
   reversed in sign, `ĉ` reversed.
4. **Repeated assembly and repeated operation** — enough to estimate the actual measurement *and
   preparation* variability. See §6: the replicate count is **not** specified here.

## 5. The symmetry pre-test, and its limit — read this before trusting any Ξ̂

The inverse above assumes the fixture is a true mirror. The screen shows the assumption is
load-bearing: a **1 %** asymmetry can bias Ξ̂ by a factor of ~5 (worst case 4.33 relative), and 5 %
by ~13.6.

**Necessary check (cheap, same fixture):** with the bridge blocked, `q₁⁰/(q₁⁰+q₂⁰)` must equal
0.5. On the screen's 16-corner perturbation set this flags *exactly* the corners that bias the
inverse.

**But it is not sufficient.** The screen exhibits a one-parameter family of different geometries —
Ξ spanning a factor of **8** — that reproduce *all four* boundary flows exactly **and** have
blocked-share exactly 0.5. The blocked run fixes only each lane's end-to-end **series**
conductance; it cannot see the top/bottom **split**. Therefore:

- the **split must be controlled by construction** — same nominal layer depths, same materials,
  same packing protocol in both lanes — not verified after the fact from boundary flows;
- **or** the four axial segment conductances must be **independently calibrated**, in which case
  `G_lat` follows exactly from `Q` alone with **no symmetry assumption at all**
  (`G = [(Q/P)A₁A₂ − N₀]/[M − (Q/P)S]`, exact for any geometry).

Report which of the two routes was used. They license different statements.

**Do not treat a physical-looking Ξ̂ as evidence the fixture was a mirror.** The inverse can return
an impossible answer (`|ĉ| ≥ 1`, or `t̂` outside `(0,1]`) when the geometry is badly off, and that
*is* a useful alarm — but it fires rarely: 0 of 96 perturbed cases at 1 %, 2 of 96 at 2 %, 9 of 96
at 5 %. At 5 % the inverse returned a plausible **wrong** Ξ in 87 of 96 cases. Treat an impossible
Ξ̂ as a hard stop; treat a possible one as carrying no information about symmetry.

## 6. Precision requirement and sample size — the calculation, not an invented `n`

**Do not adopt a replicate count from this document. There is none.** The screen supplies the
required precision; the pilot supplies the variance; together they give `n`.

**Pilot measurements needed (and not present in this repository):**

- repeated blocked-bridge runs on one assembly → within-assembly relative SD of each flow, `σ_op`;
- repeated **re-assembly** of the same nominal cell → between-assembly relative SD, `σ_prep`;
- both are needed: `σ₁² = σ_op² + σ_prep²`. Preparation variability is the one an operational
  repeat cannot see, and it is the one that moves a packed bed.

**Detection limit.** For the primary mirror (`c = 0.5`), both signatures are linear in Ξ near zero:
`R − 1 ≈ Ξ/3` and `|s − 1/2| ≈ Ξ/3`. Requiring a `z`-multiple of the standard error over `n`
replicates:

```
Ξ_min(n)  ≈  3 z σ̂₁ / √n
```

So with a measured `σ̂₁` and a chosen `z`, `n = (3 z σ̂₁ / Ξ_target)²`. Nothing here presumes a
value of `σ̂₁`.

**Estimation to within a factor of two.** This is the binding requirement, and it is stricter than
the linearised detection limit — because the joint `(R, s) → (ĉ, Ξ̂)` inversion amplifies error in
a way a single-observable linearisation does not capture. The screen's 27-point worst-case envelope
gives:

| relative floor on each of `q₁`, `q₂`, `Q₀` | Ξ recoverable within a factor of two |
|---|---|
| **1 %** | Ξ ∈ **[0.46, 2.15]** |
| 2 % | **none** |
| 5 % | **none** |

**Design the fixture for Ξ ≈ 0.5–2 and budget ~1 % effective flow reproducibility** (i.e.
`σ̂₁/√n ≲ 0.01`). Outside that window the experiment can still *detect* coupling while being unable
to *place* Ξ within a factor of two — report the two outcomes separately; they are different
claims.

These are the screen's hypothetical resolution scenarios. **They are not instrument accuracies and
not experimental uncertainty**, and the repository retains no instrument or noise model for this
experiment.

## 7. Predicted signatures

**Physical lateral coupling:**

- `R` departs from one (and, in this mirror, always *upward*: `R − 1 = [c²/(1−c²)][Ξ/(1+Ξ)] ≥ 0`);
- outlet share departs from one half;
- **the outlet-share departure reverses sign under path swap**;
- **the total-flow effect and the recovered Ξ are preserved under path swap.**

**Construction asymmetry (the confound):**

- a departure already appears with the bridge **blocked**;
- the effect fails to reverse correctly under path swap;
- **Ξ̂ changes materially under the swap.**

**Null:**

- open and blocked cases are indistinguishable within *measured* uncertainty;
- no Ξ above the experiment's own calculated detection limit `Ξ_min(n)` is supported. Report that
  limit — a null without it is not a result.

## 8. What a positive result would and would not mean

**Would:** identify the *effective* Ξ of that fixture from boundary measurements alone, without
ever measuring `k_lat` or `w`.

**Would not:**

- decompose Ξ into `k_lat`, lateral area and spacing `w` — that still requires those quantities;
- establish the Ξ of a real espresso puck. This is a hydraulic analog with engineered layers; a
  real-coffee experiment is a **separate later step** with its own design;
- place espresso in any regime;
- validate `model1_two_path` empirically beyond the two-lane analog it was built to describe;
- authorize Paper 4.
