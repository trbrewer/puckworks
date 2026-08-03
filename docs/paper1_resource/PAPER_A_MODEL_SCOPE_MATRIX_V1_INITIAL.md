# Paper A — model and evidence scope matrix

**Gate:** P0-G3a (initial). Regenerated as P0-G3b after all analyses are frozen.
**Operative plan:** `PAPER_1_PIVOT_AND_REDRAFT_PLAN_V2_2_1.md`
**Purpose:** state, for every proposition the programme may want to make, what kind of thing it is
and where it stops. Standalone by design — an earlier revision required this table *in the
manuscript*, which the same plan forbade writing.

---

## 1. Why this is separate from the claim ledger

The ledger records *what is claimed and on what evidence*. This matrix records *what kind of
statement it is*, because the recurring failure across four review rounds has been category error:
numerical verification described as physical validation, an input ablation described as causal
attribution, a surrogate geometry described as the objective's curvature.

Evidence type and robustness are **two independent fields**. Neither is a scalar tier. "Algebraic"
is not stronger than "empirical-descriptive" — they answer different questions and fail in different
ways.

---

## 2. Vocabularies

**Evidence type** — algebraic · numerical-model-structural · empirical-descriptive ·
operational-convention · inferential · prospective-model-based · physical-external ·
exploratory-oracle

**Robustness** — established-under-assumptions · verified-within-numerical-scope · refit-stable ·
heterogeneous · sensitivity-only · cross-fitted · externally-replicated · unresolved · withdrawn

---

## 3. The matrix

| proposition | evidence type | robustness | where it stops |
|---|---|---|---|
| `det(G) = W²·Var_w(s)`; Schur complement `W·Var_w(s)` | algebraic | established-under-assumptions | declared factorisation, log coordinates, **fixed** weights. Not MAPE curvature |
| Exact weighted-median MAPE level minimiser | algebraic | established-under-assumptions *(proposition owed, P0-G6)* | requires strictly positive `y_i`, `f_i`; minimiser may be an interval |
| The high-rate plateau is not a BDF artefact | numerical-model-structural | verified-within-numerical-scope | both paths share equations, spatial operator, parameterisation, omitted physics — independent **in time only** |
| Full-support contrasts survive the mesh/tolerance envelope | numerical-model-structural | verified-within-numerical-scope | **FULL-SUPPORT estimands only**; says nothing about fold medians |
| Coarse M1−M2 = +1.234 pp, 9/9 folds | empirical-descriptive | refit-stable | one campaign, one machine, two coffees; retrospective campaign-conditioned map; dependent folds |
| Fine M1−M2 = −0.037 pp, 7/9 negative | empirical-descriptive | heterogeneous | as above; **the pooled figure must never be reported without this** |
| M0−M2 policy contrast | empirical-descriptive | heterogeneous | published multiplier domain only; both arms receive the target map |
| 5 of 6 profiles right-censored at `κ = 500` | operational-convention | sensitivity-only | a **finite-domain observation** under one arbitrary tolerance; not an unbounded set |
| Pressure beats temperature ~21× per observation | prospective-model-based | unresolved | nominal `κ = 1`, per-observation; on **total** spread the grid carries 1.8× more |
| Endpoint variation beats the process grid ~2.2× | prospective-model-based | unresolved | designs are **unobserved** in this campaign |
| Flow-only response scores 8.408 % | exploratory-oracle | withdrawn | selected on held-out score; **not** a held-out result |
| Model beats level-only constant by 0.394 pp | empirical-descriptive | unresolved | refit-aware median −0.058 pp, 6/9 folds; **historical secondary only** |
| Real espresso reaches local equilibrium before displacement | physical-external | **unresolved — never asserted** | requires external measurement; outside this work |
| `κ` is a physical kinetic constant | physical-external | **withdrawn** | `κ` multiplies inherited Sherwood prefactors and absorbs model discrepancy |

---

## 4. Physics the model does not represent

Every claim above is conditional on these being absent from the declared model. They are recorded
because their absence bounds H1, H3 and the design recommendations, and because recent espresso
literature emphasises several of them.

- wetting and unsaturated infiltration
- evolving permeability and porosity; fines migration
- puck compression, swelling, poroelastic response
- axial dispersion; radial non-uniformity; channelling
- time-varying flow within a shot
- grind-dependent particle geometry — **frozen at centre-grind values throughout**
- model-form discrepancy generally

Any of these could create or destroy apparent sensitivity to the mass-transfer-rate multiplier. The
plateau is therefore a property of *this* model, and its physical status is open.

---

## 5. The three calibration and information layers

Compressing these into "source-calibrated" was flagged in review. They are distinct:

| layer | what is fitted | to what data |
|---|---|---|
| **L1 — inherited** | Sherwood prefactors `A1`/`A2`, equilibrium and transport closures | post-fit reconstruction of Schmieder fractionated kinetics, via Pannusch |
| **L2 — this paper** | multiplier `κ` and inventory level `I` | Angeloni **optimal-grind** chemical endpoints |
| **L3 — target inputs** | nothing fitted here | target-grind flow map, supplied at prediction time from target-grind shot times and conductivity polynomials |

Coarse/fine **chemical** observations enter at no layer. Target-grind **hydraulic** observations
enter at L3, which is why the current H3 result is retrospective rather than zero-target-data
prospective.

---

## 6. Information-availability classes for target-side inputs

Used by P0-G9. An input is classified by *when it would exist* in a real prediction workflow:

- **pre-shot** — known before the target shot is pulled (nominal grind setting, machine pressure)
- **contemporaneous** — measurable during the shot (flow trace, shot time)
- **post-shot** — available only afterwards, or fitted using the scored condition itself

The current map draws on per-granulometry shot times and fitted conductivity polynomials from the
target-grind campaign, so at least part of it is **post-shot** with respect to any scored condition.
P0-G9 must record this per prediction row.
