# Paper 1 — pivot and redraft plan

> [!WARNING]
> **SUPERSEDED AND NOT OPERATIVE.** This document was reviewed in
> `PAPER_1_PIVOT_AND_REDRAFT_PLAN_REVIEW_20260801.md`, which found substantive defects that were
> verified and accepted: numerical verification presented as physical verification, a fold/group
> unit-of-analysis conflation, and — most seriously — **two headline claims built on pooled means
> that hide opposite coarse- and fine-grind results**, in violation of this document's own drafting
> rule. Use **`PAPER_1_PIVOT_AND_REDRAFT_PLAN_V2.md`**. This file is retained only for the audit
> trail.


**Prepared:** 1 August 2026
**Supersedes as the operative plan:** `paper1_recommended_scientific_pivot_and_revision_plan_20260801.md`
(whose Stage 1 was falsified — see §3.4)
**Evidence base:** merge `abb982c` plus pivot checks 1–2 and gates G3 and G4
**Status:** proposal for review. No manuscript file has been modified.

---

## 1. The decision in one paragraph

The paper currently leads with its **weakest** result and buries its **strongest**. The published
headline — a −0.394 pp mechanistic advantage over a level-only constant — survives refitting in only
6 of 9 folds with a median of −0.058 pp. Meanwhile the contrast that is sign-stable in **all nine**
folds, at **+0.524 pp**, is one the paper does not currently report at all: the value of the
target-grind hydraulic map. And the kinetic parameter the paper spends its length discussing sits,
for half the corpus, past a saturation shoulder beyond which a tenfold change moves the prediction
by less than one part in two thousand — verified on an independent integrator, not inferred from the
solver that produced it. The redraft should invert this hierarchy and lead with a physical claim
about when an espresso cup can and cannot see extraction kinetics.

---

## 2. The hypothesis

### H1 — primary, physical

> **The whole-cup response to extraction rate saturates.** Once the rate is fast enough that the
> grains approach local equilibrium with the surrounding liquid before it is displaced, the cup
> composition is set by extractable inventory and the equilibrium constant, and stops responding to
> the kinetics. Whether a given campaign can identify the rate therefore depends on **where its data
> sit relative to that shoulder** — and in this campaign the near-optimal set is unbounded above in
> five of six groups.

This is a claim about espresso, not about statistics. It says the measurement can fall into a regime
where it cannot see the physics it is routinely used to calibrate.

**Refinement forced by G3 (§3.6).** An earlier wording of H1 asserted flatly that the cup "cannot
see" the kinetics. The verification shows that is too strong: the model is strongly rate-responsive
below a multiplier of ~2 (+12 to +62 % per step) and flat above ~50 (+0.05 % per decade). The three
Arabica groups fit interior optima on the responsive shoulder; all three Robusta groups run past it.
That heterogeneity is not noise — **it explains why freezing the rate wins in 8 of 9 folds rather
than 9, and why the single exception is Arabica caffeine**, the group with the most interior fit.
The paper should make the shoulder the claim and the campaign's position on it an observation.

### H2 — mechanism, exact

> For a model whose prediction factorises as `ŷ_i = I · f_i(k)`, all local information about `k`
> after profiling the level `I` is the **weighted variance of the observations' log-rate
> sensitivities**: `det(G) = (Σw)² · Var_w(s)`. A design can therefore be screened for
> rate-separability **before any data are collected**.

### H3 — attribution

> What transfers across grind in this campaign is **exogenous hydraulic information** — the
> target-grind flow and collected-mass endpoint — not fitted kinetics and not particle geometry.

### H4 — consequence for practice

> When a design cannot separate a parameter, the parameter should be **frozen at an inherited
> value rather than fitted**. Fitting it converts an unidentified direction into calibration-set
> noise that transfers badly.

---

## 3. The evidence

All figures are from archived producers in the repository; every one is reproducible and gated.

### 3.1 The rate is unidentified — and the evidence is near-deterministic, not statistical

`tools/paper_a_rate_domain_check.py` → `PAPER_A_RATE_DOMAIN_CHECK.json`

Widening the rate domain 77× (to 500 over 40 log-spaced points):

| group | rate\* at cap 6.5 | rate\* at cap 500 | fit gained | prediction moves over top decade |
|---|---:|---:|---:|---:|
| Arabica caffeine | interior | 0.79 | 0.167 pp | 0.050 % |
| Arabica trigonelline | interior | 1.82 | 0.030 pp | 0.000 % |
| Arabica 5-CQA | interior | 0.98 | 0.404 pp | 0.003 % |
| Robusta caffeine | **6.50 pinned** | 6.34 | 0.0002 pp | 0.050 % |
| Robusta trigonelline | **6.50 pinned** | **62.47** | 0.007 pp | 0.000 % |
| Robusta 5-CQA | **6.50 pinned** | **143.55** | 0.081 pp | 0.003 % |

- **6 of 6 groups saturate.** A tenfold change in the rate multiplier moves the predicted cup
  concentration by **< 0.05 %**.
- **5 of 6** near-optimal sets are still right-censored at the widened cap. The rate is unbounded
  above even after 77× more room.
- Robusta trigonelline's optimum relocates **twentyfold** (6.5 → 62.5) for 0.007 pp of fit.

This is the strongest kind of evidence in the paper because it is not a comparison of two numbers
with overlapping uncertainty — it is a response that has gone flat.

### 3.2 The hydraulic map is the load-bearing channel — the only sign-stable result

`tools/paper_a_information_parity.py`, `tools/paper_a_ablation_refit_stability.py`

| contrast | median | range | folds | sign stable |
|---|---:|---|---:|---|
| **M1 − M2** (common map vs target map) | **+0.524 pp** | [+0.288, +0.760] | **9/9 positive** | **yes** |
| M0 − M2 (freeze rate vs fit it) | −0.205 pp | [−0.535, **+0.010**] | 8/9 negative | no |
| model − equal-information empirical | −0.187 pp | [−2.249, +0.389] | 8/9 | no |
| model − level-only constant *(current headline)* | −0.058 pp | [−0.328, +0.416] | 6/9 | no |

Two things follow, and they should govern the redraft:

1. **M1 − M2 is the only contrast in the entire analysis whose sign survives refitting**, and its
   median exceeds the paper's current headline advantage (0.524 > 0.394).
2. The current headline is the **least** stable quantity we have.

### 3.3 Fitting the unidentified parameter costs accuracy

| arm | coarse | fine | pooled |
|---|---:|---:|---:|
| **M0** inherited rate, level only | 9.640 | 6.922 | **8.281** |
| M1 fitted rate and level, **common** map | 11.158 | 6.612 | 8.885 |
| M2 fitted rate and level, target map *(canonical)* | 10.167 | 6.709 | 8.438 |

Refit-aware: **M0 − M2 = −0.205 pp median, negative in 8 of 9 folds**, and the single exception is
**+0.010 pp** — a dead heat, not a reversal. Widening the rate domain moves this to −0.183 pp, so
it is not a capping artefact.

**Independent confirmation.** M0's 8.281 % is exactly the value produced last round by a *bug* that
accidentally omitted the rate multiplier. That bug made the arm rate-free, which is what M0 is by
construction. Two unrelated code paths, same number.

### 3.4 A two-parameter empirical response matches the whole model

A mechanism-free response in **flow alone** scores **8.408 %** against the mechanistic model's
8.438 %. This is archived as a **quarantined oracle upper bound** — the form was chosen by its
held-out score, which is selection on the test set — and may never be quoted as a held-out result.

The frozen-selection version scores 9.670 %, worse, because 73 % of fine-grind residence times fall
outside the calibration range, 1.6 calibration-spans beyond it. **The gap between 9.670 and 8.408 is
itself the finding:** nine calibration conditions cannot identify which hydraulic form to trust when
the target domain is extrapolative.

### 3.5 The design has almost no rate-sensitivity diversity

`PAPER_A_DESIGN_SEPARABILITY.json`

| design | median RSI |
|---|---:|
| single condition | 0.0000 |
| vary temperature only | 0.0005 |
| vary pressure only | 0.0113 (**21×** temperature) |
| full 3×3 grid, 9 conditions | 0.0113 |
| **two extreme corners, 2 conditions** | **0.0131** |
| **vary collected-mass endpoint (20/40/60 g)** | **0.0252 (2.2× the grid)** |

RSI is ~10⁻² everywhere, never order unity. Two well-chosen conditions beat all nine; the endpoint
is the strongest lever available.

### 3.6 The saturation is physical, not a solver floor — G3 **PASSED**

`tools/paper_a_saturation_verification.py` → `PAPER_A_SATURATION_VERIFICATION.json`

Every term of the production right-hand side is linear in the state, so the semi-discrete system is
`dz/dt = A z` and can be solved **exactly** by matrix exponential — no time stepping, no adaptive
error control, no numerical Jacobian, none of the machinery that emits the overflow warnings.

| check | result |
|---|---|
| `_rhs` is exactly linear | superposition error **4.2 × 10⁻¹⁶** |
| operator reproduces `_rhs` state by state (rate 1 and rate 500) | **2 × 10⁻¹⁶** |
| **BDF vs matrix exponential, worst over 3 solutes × 5 rates** | **0.000122 %** |
| saturation reproduced on the independent path (decade spread) | 0.053 %, 0.000 %, 0.002 % |
| convergence to a finite rate-independent limit | increments fall **7.2–8.9 orders** to the arithmetic noise floor |

Two integrators sharing no time-stepping machinery agree to about one part per million, *including
deep in the saturated regime*, and the prediction converges to a limit. A solver floor does not
produce a convergent sequence.

**Falsification control.** The same code path shows a **large** response where one is expected: over
the unsaturated decade 0.01 → 0.1 the prediction moves **+56 %**. Flatness at high rate is therefore
a measurement, not a property of the code.

The full response curve, which is what motivates the H1 refinement above:

| rate multiplier | 0.01 | 0.1 | 0.5 | 1.0 | 2.0 | 6.5 | 50 | 500 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| change in prediction | — | +56.1 % | +62.5 % | +16.4 % | +12.4 % | +13.0 % | +5.3 % | **+0.05 %** |

### 3.7 The contrasts are numerically robust — G4 **PASSED**

`tools/paper_a_numerical_envelope.py` → `PAPER_A_NUMERICAL_ENVELOPE.json`

Both arms refitted from scratch inside every configuration, so a mesh change was free to move the
fitted rate as well as the scores. The `expm` path is exact in time, so the two error sources are
**separated** rather than pooled:

| configuration | M1 − M2 | M0 − M2 | runtime |
|---|---:|---:|---:|
| exact-in-time, 100 nodes | +0.4471 | −0.1572 | 16 s |
| exact-in-time, 200 nodes | +0.4471 | −0.1572 | 62 s |
| exact-in-time, 400 nodes | +0.4471 | −0.1572 | 312 s |
| BDF, 200 nodes, tol 10⁻⁵ | +0.4471 | −0.1573 | 144 s |
| BDF, 200 nodes, tol 10⁻⁶ *(production)* | +0.4471 | −0.1572 | 206 s |
| BDF, 200 nodes, tol 10⁻⁷ | +0.4471 | −0.1572 | 280 s |
| **range** | **0.0000** | **0.0001** | |

Time-integration error against the exact reference is **0.00000 pp** at production tolerance.

Two incidental findings worth carrying into the draft:

* **Spatial convergence is already achieved at 100 nodes** — the raw prediction differs by 4 × 10⁻¹¹
  relative between 100 and 400. The five-point biased-upwind operator is exact to degree 4 and the
  outlet trajectory is smooth, so the mesh was never the risk.
* The envelope cost **17 minutes**, against the multi-hour estimate carried since the domain-referee
  round. That estimate was made before the linear structure was noticed.

**Control.** A stability result this clean must be shown to be capable of failing. Tests assert that
the node-count patch really changes the computed prediction, and that tightening the BDF tolerance
moves the answer *toward* the exact solution. Without those, an envelope whose patch had silently
failed would report perfect stability.

### 3.8 What was removed from the evidence base

- **Schmieder's "measured complete cups" are not measurements.** 427 of 432 reproduce as the
  integral of the authors' own exponential fit to the fractions (median difference 0.000032 %
  against a reported cup RSD of 2.5 %). The measured-cup-versus-fraction contrast is circular and
  **cannot be run on any corpus we hold**. This kills the previous plan's Stage 1.
- **Half the corpus never had an identified rate.** All three Robusta groups were boundary-pinned.

---

## 4. Evidential hierarchy for the redraft

The redraft must state claims at the strength the evidence supports, and no higher.

| tier | claim | basis |
|---|---|---|
| **A — near-deterministic** | The rate is unidentified; the cup response to it is flat | 6/6 groups, <0.05 % over a decade |
| **A** | Exact separability identity | algebra, tested |
| **B — sign-stable under refit** | The target-grind hydraulic map is load-bearing (+0.524 pp) | 9/9 folds |
| **C — strong but not sign-stable** | Fitting the rate does not improve transfer and usually costs ~0.2 pp | 8/9 folds, exception +0.010 |
| **C** | A mechanism-free flow response matches the model | oracle bound, quarantined |
| **D — screen only** | RSI predicts profile width | 5/6 groups, median ρ = −0.61 |
| **E — do not lead with** | model − constant = −0.394 pp | 6/9 folds, median −0.058 |

---

## 5. What we are **not** claiming

Carried from the frozen assurance layer and the domain referee, plus new ones.

1. **Not** that espresso extraction kinetics are non-identifiable in general — only that *this
   observation operator* (whole cup at a matched endpoint) cannot see them.
2. **Not** that whole-cup experiments are useless. §3.5 says varied endpoints or pressures create
   real sensitivity diversity; a better-designed cup experiment could identify the rate.
3. **Not** that the fitted multiplier is an intrinsic kinetic constant. It scales inherited Sherwood
   prefactors and absorbs model discrepancy.
4. **Not** validation of a physical grind mechanism. Particle geometry is frozen.
5. **Not** a calibrated interval or equivalence conclusion from nine dependent folds.
6. **Not** that fitting a parameter is harmful in general — the claim is conditional on the design
   failing to separate it.
7. **Symmetry still binds, but its direction has reversed.** The P0 criterion required that no
   surface establish either that the advantage is real *or* that it is absent. The new thesis is
   more negative about mechanism, so the live risk is now **over-claiming that fitting is harmful**.
   `claim_policy.SURFACE_ASSERTIONS` must be **rebuilt around the new propositions**, not patched —
   the current registry encodes the old symmetry.

---

## 6. Gates before drafting

The previous plan's rule stands and was vindicated: *do not write while results are moving.*

| gate | question | status |
|---|---|---|
| **G1** | Is the boundary-pinned rate an artefact? | **PASSED** — saturating degeneracy, 6/6 |
| **G2** | Is M0 − M2 stable to calibration choice? | **PASSED with a caveat** — 8/9, exception +0.010 |
| **G3** | Is the saturation numerical or physical? | **PASSED** — physical; two integrators agree to 0.000122 %, §3.6 |
| **G4** | Do the load-bearing contrasts survive discretisation and tolerance change? | **PASSED** — both unmoved to <0.0001 pp, §3.7 |
| **G5** | Indexed novelty search | **OPEN — cannot be done in this environment** |

### G3 and G4 are both closed; R0 is now the critical path

G3 verified the paper's central mechanism and passed (§3.6). The semi-discrete system turned out to
be **exactly linear**, so the matrix-exponential reference is not an approximation to the production
model but the same model integrated without any time stepping. BDF and `expm` agree to 0.000122 %,
including deep in the saturated regime, and the prediction converges to a finite limit. **H1's
mechanism is verified.**

Two consequences beyond the gate:

* the linear structure is now a **capability**, not just a check — the `expm` path is fast, exact,
  and free of the overflow warnings, so G4 can use it as its reference rather than comparing BDF
  against itself;
* the response curve it produced forced the H1 refinement in §2: the saturation is a **shoulder**,
  and the campaign's groups sit on both sides of it.

**G4 passed (§3.7).** Both contrasts are unmoved across the envelope: M1 − M2 is identical to
four decimal places at every configuration, and M0 − M2 varies by 0.0001 pp. The `expm` reference
made it possible to separate the two error sources instead of pooling them, and to measure BDF's
time-integration error against truth rather than against another approximation.

**G5** cannot be closed here (no Scopus/WoS/Compendex; MDPI and Royal Society Cloudflare-blocked).
No "first" or "to our knowledge" phrasing may enter the draft until it is closed by someone with
database access. This is an environment limit, not a task.

---

## 7. Draft plan

### 7.1 Working title

**What a Whole Espresso Cup Cannot See: Equilibrium-Limited Composition, Unidentifiable Kinetics,
and Hydraulic Transfer**

Alternatives: *"Whole-Cup Espresso Composition Is Inventory-Limited, Not Rate-Limited"*;
*"Fitting What the Measurement Cannot See"*.

### 7.2 Structure

| § | content | leads with |
|---|---|---|
| 1 | Introduction — cup accuracy is routinely read as kinetic validation | the question, not the benchmark |
| 2 | Model, observation operators, and the exact factorisation | H2 identity |
| 3 | The design cannot separate the rate | RSI, profiles, **saturation** |
| 4 | Neither can the fit: the rate is unbounded above | rate-domain check |
| 5 | Consequence — freezing beats fitting | M0/M1/M2, refit-aware |
| 6 | What actually transfers: hydraulics | **M1 − M2, the 9/9 result** |
| 7 | Designing an espresso experiment that *can* see the rate | endpoints, pressure, corners |
| 8 | Discussion, limits, and what a decisive experiment would measure | |

The cross-grind case becomes §6's demonstration. **−0.394 pp does not appear in the abstract.**

### 7.3 Rules for the draft

1. **No pooled number without its disaggregation on the same page.** The coarse/fine asymmetry sat
   in the archive for five rounds because a pooled mean was reported alone.
2. **Every quantitative claim carries its refit-aware stability** where one exists.
3. **Generated blocks for all headline numbers** — the existing artefact → generator → manuscript
   chain, with pre-insertion claim scanning.
4. **Write §§3–6 first**, abstract and conclusions last.

---

## 8. Review plan

Thirteen rounds produced a clear lesson: **reviews of the assurance layer found defects in the
assurance layer; the one review that asked scientific questions changed the result.** The review
plan is built around that.

### 8.1 What went wrong before, and the countermeasure

| observed failure | countermeasure |
|---|---|
| Load-bearing **premises** were never tested: Angeloni transcription unverified for 12 rounds; Schmieder cups assumed independent; rate domain assumed to bracket the optimum. Each was eventually found, and each was wrong or unchecked. | **Premise audit round (R0) comes first.** Every load-bearing assumption gets an executable, *falsifiable* test before drafting. A test that cannot return the other answer is not a test. |
| **Pooled numbers hid structure** for multiple rounds. | Disaggregation rule (§7.3.1), enforced by a gate. |
| **My own new tools shipped bugs through a green chain** — omitted rate multiplier, uncaptioned table, malformed sentence. Gates check claims and numbers, not correctness of new code or English. | Every new producer must **recover a published value by an independent path** before its novel output is trusted. This is what caught the rate-multiplier bug and what confirmed M0. |
| **Rounds 10–12 hardened gates against hypothetical defects** while the registry was empty. | The freeze holds. Review effort is spent on premises and physics, not on the taxonomy. |
| **Wording disputes consumed rounds** with no acceptance criterion. | Editorial review is a **separate, single, terminal round** with a closed checklist. Scientific reviewers are asked not to comment on wording. |
| **Selection-on-test-set nearly reported as a result** (the 8.408 % oracle). | Any number chosen with knowledge of held-out data is archived with a `status` string and tested to stay separated from held-out scores. |

### 8.2 Rounds

| round | reviewer | scope | acceptance criterion |
|---|---|---|---|
| **R0** | internal | Premise audit: every assumption in §3 gets a falsifiable test | every premise has a test that can return the opposite verdict |
| **R1** | numerical / scientific-computing | Audit the completed G3 and G4: is the linear-operator argument sound, are the controls adequate? | no defect found in the exact-in-time reference or in the falsification controls |
| **R2** | inverse-problems / parameter-estimation specialist | H2 derivation, RSI scope, profile logic | no local result overextended to a global claim; no Fisher/uncertainty language |
| **R3** | espresso experimentalist / food-process engineer | H1 and H3 physical plausibility, §7 design guidance | the design recommendations are actionable and not artefacts of one machine |
| **R4** | skeptical statistical reviewer | Every claim vs its tier in §4 | no claim stated above its tier; all refit-aware caveats present |
| **R5** | editorial only | Prose, figures, tables, length | closed checklist; **no scientific re-litigation** |

R1 remains first among the external rounds. G3 and G4 have passed, so its job is now to attack that work rather than wait on it — the linear-operator argument is the single point on which H1's verification rests.

### 8.3 Standing questions for every scientific reviewer

1. Which claim in §4 is stated above its tier?
2. Which premise in §3 would you not have checked, and would it change the conclusion?
3. Is any refitted quantity described as held out?
4. Is any local, model-based result described as global or calibrated?
5. What experiment would falsify H1, and does the paper say so?

### 8.4 Termination rule

A round closes when no finding contradicts §4's tier assignment. **Wording preferences that do not
violate a tier assignment are editorial and are deferred to R5.** This replaces "no reviewer
objects", which is unfalsifiable and cost us three rounds.

---

## 9. Risks

| risk | severity | mitigation |
|---|---|---|
| ~~Saturation is numerical, not physical~~ | ~~fatal to H1~~ | **RETIRED** — G3 passed, §3.6 |
| M0 − M2 weakens further under a fuller analysis | moderate | claim is already tiered at C ("does not improve", not "harms") |
| One campaign, one machine, two roasts | inherent | scope every claim to the operator and campaign; H2 is model-general, H1 is not |
| Novelty overstated | reputational | G5 unclosed ⇒ no "first"/"to our knowledge" language at all |
| Claim registry encodes the old symmetry | moderate | rebuild `SURFACE_ASSERTIONS` around the new propositions (§5.7) |

---

## 10. Sequence

1. ~~**G3** — independent numerical path.~~ **DONE: saturation is physical.**
2. ~~**G4** — envelope on the contrasts.~~ **DONE: both robust.**
3. **R0** — premise audit; falsifiable test per assumption. *Now the critical path.*
4. Rebuild the claim registry around H1–H4.
5. Draft §§3–6, then 7–8, then 1–2, then abstract.
6. **R1 → R5.**
7. G5 by whoever has database access; novelty language added only then.

Steps 1 and 2 have returned; **no numerical objection to the redraft remains open**. The drafting sequence can begin once R0 closes.
