# PUBLIC_VALUE.md

## A public-value roadmap for `puckworks`

**Prepared:** 2026-07-12  
**Primary objective:** turn the repository's data, models, disagreements, negative results, and open experiments into material that a non-specialist coffee drinker can understand, care about, use, and share.

---

## Executive recommendation

The strongest public proposition for `puckworks` is **not yet “the definitive espresso recipe calculator.”** The repository is more distinctive—and currently more defensible—as an **evidence engine for what happens inside an espresso puck**:

> **Make hidden processes visible, test familiar explanations against null models, and show what measurement would actually settle the question.**

This framing fits the architecture of the project. `puckworks` is deliberately a component registry rather than a single mega-model; components carry provenance, assumptions, validity ranges, and validation gates. The repo also preserves conflicting constants, separates post-fit reconstruction from independent validation, and records negative transfer results. Those practices can become part of the public appeal rather than remaining internal scientific hygiene.

The three best flagship public stories already latent in the repository are:

1. **Before the first drop:** the first measured liquid in one fraction-resolved dataset was already about 97% of peak concentration, while infiltration models can reveal the invisible wetting front that precedes it.
2. **One curve, many causes:** a dip-and-recovery in flow can be produced by machine hydraulics alone, while a separate rising-flow trace does require time-dependent bed behavior. A flow curve is not a diagnosis.
3. **A good fit can still be wrong:** inventory and extraction rate can trade off so that a model fits a cup well at one grind yet fails badly at other grinds. Time-resolved fractions recover information that the whole cup erases.

A fourth story is especially valuable for credibility and likely shareability:

4. **We killed our favorite result:** the apparently dramatic fine-grind optimum weakened after correcting a mixed-unit aggregation and comparing the model bump with raw replicate variation. This is a rare, honest story about how a bold result was downgraded by better analysis.

The recommended program is therefore:

- Build a small **public-results layer** so every headline and visual is generated from the current harness, with evidence strength and caveats attached.
- Produce four short, high-clarity story packages from existing results before adding substantial new physics.
- Use model disagreement to design a small number of **mechanism-separating experiments** that ordinary espresso users can understand and, where feasible, help replicate.
- Delay broad recipe optimization claims until cross-coffee, cross-grinder, and cross-machine transfer is substantially stronger.

> **Shared with the submission track.** Several venues in `docs/SUBMISSION_TARGETS.md`
> are *public-facing* and therefore serve this public-value goal directly — the
> **Science-Driven Coffee Cup** (coffee ecosystem), the **APS Gallery of Fluid
> Motion** (public visual, deadline 2026-09-17), and the **World of Coffee / Coffee
> Science Foundation poster** (industry/practitioner). Where a story here maps to
> one of those, the two tracks point at each other: the PV story supplies the
> public figure/animation, the submission ledger supplies the deadline. Keep the
> evidence-strength labels and §3 guardrails identical across both.

---

## 1. What “public value” should mean here

A public-facing result should deliver at least two of the following, and the best results should deliver four or five:

| Public-value mode | What the audience receives | Example for `puckworks` |
|---|---|---|
| **Aha** | A counterintuitive fact or corrected intuition | A flow dip does not, by itself, prove the puck changed. |
| **Wonder** | A view of an otherwise invisible process | Wetting front, local flow concentration, extraction clocks. |
| **Action** | A change in measurement or brewing practice | Collect timed fractions; do not compare grinder dial numbers directly. |
| **Agency** | A way to run or contribute to an experiment | A standardized first-drip/fraction protocol or pressure-step test. |
| **Trust** | Clear separation of observation, fit, prediction, and speculation | “Measured,” “post-fit,” “within-rig prediction,” and “exploratory simulation” badges. |

The ideal public artifact has a simple five-part structure:

1. **Question:** a familiar coffee question in ordinary language.
2. **Surprise:** one sentence that changes the audience's expectation.
3. **Visual:** one main graphic or animation, not a dashboard of everything.
4. **Consequence:** what this changes in interpretation, measurement, or brewing.
5. **Scope sentence:** exactly where the result applies and what it does not prove.

A useful house template is:

> **Headline:** attention-worthy but not overgeneralized.  
> **Evidence sentence:** what was measured or simulated, on which data, and with what strength.  
> **Practical sentence:** what a coffee drinker should do differently, if anything.  
> **Limit sentence:** the most important alternative explanation or missing validation.

---

## 2. Why the current repository is unusually well suited to this goal

A parse of the referenced repository snapshot shows **25 registered components** and **64 manifest entries**, spanning machine behavior, infiltration, packing, flow, bed dynamics, extraction, and chemistry-related priors. More important than the counts, the repo already contains several public-facing ingredients that are difficult to retrofit into a conventional research codebase.

> *[verified 2026-07-12: 25 components (`len(components())`), 64 manifest data rows (`MANIFEST.csv` minus header) — matches the counts above. Re-verify against the live tree per §18 before publishing any count.]*

| Existing asset | Repo location | Public opportunity |
|---|---|---|
| Component registry with assumptions, validity ranges, and gates | [`README.md`](https://github.com/trbrewer/puckworks/blob/main/README.md), [`puckworks/registry.py`](https://github.com/trbrewer/puckworks/blob/main/puckworks/registry.py), [`puckworks/models/__init__.py`](https://github.com/trbrewer/puckworks/blob/main/puckworks/models/__init__.py) | “Model cards” that explain what each model can and cannot claim. |
| Evidence-strength vocabulary and no-silent-merge rules | [`CLAUDE.md`](https://github.com/trbrewer/puckworks/blob/main/CLAUDE.md) | A visible trust system: measured, post-fit, verification, qualitative. |
| Fraction-resolved TDS and eleven pressure traces | [`puckworks/data/MANIFEST.csv`](https://github.com/trbrewer/puckworks/blob/main/puckworks/data/MANIFEST.csv), [`puckworks/harness.py`](https://github.com/trbrewer/puckworks/blob/main/puckworks/harness.py) | First-drop story, pressure fingerprint map, mechanism-discrimination experiments. |
| Infiltration and first-drip models | Foster components described in the registry and roadmap | A scientifically labelled animation of the puck before liquid appears. |
| Multi-solute, fraction-resolved extraction model and independent transfer target | [`docs/ANALYSIS_transfer.md`](https://github.com/trbrewer/puckworks/blob/main/docs/ANALYSIS_transfer.md) | “The cup hides the clock” interactive and transfer challenge. |
| Static and dynamic heterogeneity models | [`docs/ANALYSIS_P2.md`](https://github.com/trbrewer/puckworks/blob/main/docs/ANALYSIS_P2.md), [`docs/P3_hypotheses.md`](https://github.com/trbrewer/puckworks/blob/main/docs/P3_hypotheses.md) | Channel formation animation, phase map, and a lesson in model capacity versus identification. |
| Packing generator and lattice-Boltzmann solvers | Registry plus `brewer2026.pack_generator`, `lb_reference`, and `lb_taichi` | Pore-scale flow visuals, provided they are labelled synthetic rather than literal coffee microstructure. |
| Existing paper figures generated from harness outputs | [`puckworks/figures.py`](https://github.com/trbrewer/puckworks/blob/main/puckworks/figures.py), [`docs/PAPER_B_DRAFT.md`](https://github.com/trbrewer/puckworks/blob/main/docs/PAPER_B_DRAFT.md) | Five ready-made scientific narratives that can be translated into public graphics. |
| Explicit gaps and staged acquisition protocols | [`docs/ROADMAP.md`](https://github.com/trbrewer/puckworks/blob/main/docs/ROADMAP.md) | Public experiments with a clear reason: pump curve, retention curve, liquor rheology, lateral flow, and grinder transfer. |

The key strategic advantage is that `puckworks` can make **uncertainty and disagreement interesting**. Most public espresso content presents a rule. This project can present a more compelling sequence:

> Here are three explanations. Here is why the usual observation cannot distinguish them. Here is the experiment that can.

That is both scientifically honest and narratively strong.

---

## 3. Non-negotiable public-communication guardrails

These guardrails are not merely defensive. Used consistently, they can become a recognizable feature of the project.

### 3.1 Separate observed, fitted, predicted, and simulated material

Every public visual should carry one of four prominent badges:

- **OBSERVED:** directly measured values or digitized published data.
- **RECONSTRUCTED:** a model evaluated on data used to fit or calibrate it.
- **PREDICTED:** held-out data, cross-pressure prediction, cross-grind transfer, or another genuine test.
- **EXPLORATORY SIMULATION:** a mechanism demonstration without direct empirical identification.

Do not hide this distinction in a caption. Put it in the graphic.

### 3.2 Pair every bold headline with a scope sentence

For example:

> **The first drop was already almost as concentrated as the peak.**  
> In one pressure-controlled, fraction-resolved dataset, the early/peak TDS ratio was 0.968; the first fraction had only one replicate, so this is a strong prompt for replication, not a universal law.

### 3.3 Do not turn a model animation into fake microscopy

The pack generator uses synthetic Boolean-sphere geometry, and the N-tube model is a reduced representation. Visuals should say **“simulated flow in a synthetic packing”** or **“one mechanistic lens”**, not “this is what your puck looks like.” When different components cannot be composed consistently, show parallel lenses rather than a seamless movie.

### 3.4 Use null models as protagonists

“The simplest explanation already produces this feature” is often more surprising than a complicated success. The Foster machine-only flow dip, the flat-flow baseline, and the failed shared-porosity composite are especially valuable public results.

### 3.5 Show raw points before trend lines

The corrected fine-grind analysis demonstrates why. Public graphics should default to replicate points and uncertainty, then reveal the fitted curve. Never let a response surface visually outrank the cells that generated it.

### 3.6 Never translate chemistry directly into taste without evidence

Caffeine, trigonelline, chlorogenic acids, and TDS are chemically meaningful, but they are not a complete sensory model. Use language such as **“chemical composition”** or **“measured compounds”**, not “bitterness extracted at 12 seconds,” unless supported by sensory or validated concentration–perception data.

### 3.7 Do not make grinder dials portable by implication

Use physical variables—particle-size moments, fines fraction, permeability, dose, bed depth—when comparing systems. A dial number may be shown only with a grinder-specific calibration and a conspicuous non-portability warning.

### 3.8 Do not launch a universal recipe optimizer prematurely

A consumer-facing optimizer would invite claims beyond the current transfer evidence. A safer near-term product is a **mechanism explorer** or **experiment planner** that shows model disagreement, validity ranges, and what additional measurement would reduce uncertainty.

---

## 4. Prioritization framework

Scores below are 1–5. **Ease** is reversed effort: 5 means an existing-analysis quick win; 1 means a substantial new experimental program. The total is a triage aid, not a scientific rank.

| ID | Task | Hook | Evidence readiness | Visual potential | Practical value | Ease | Total | Suggested priority |
|---|---|---:|---:|---:|---:|---:|---:|---|
| PV-00 | Public results and claim registry | 4 | 5 | 3 | 3 | 4 | 19 | **P0 foundation** |
| PV-01 | “The first drop is already strong” | 5 | 4 | 5 | 4 | 4 | 22 | **P0 flagship** |
| PV-02 | “The machine can fake a puck problem” | 5 | 4 | 5 | 4 | 4 | 22 | **P0 flagship** |
| PV-03 | “A good fit can still be wrong” | 5 | 5 | 5 | 4 | 3 | 22 | **P0 flagship** |
| PV-04 | “We killed our favorite result” | 5 | 4 | 5 | 4 | 4 | 22 | **P0 flagship** |
| PV-05 | “Adding physics made the model worse” | 5 | 4 | 5 | 3 | 5 | 22 | **P0 quick story** |
| PV-06 | Cross-pressure mechanism fingerprint | 4 | 4 | 5 | 4 | 3 | 20 | P1 |
| PV-07 | Compound extraction clocks and same-strength pairs | 5 | 3 | 5 | 5 | 3 | 21 | P1 |
| PV-08 | “Puck Court” evidence dashboard | 4 | 5 | 4 | 3 | 3 | 19 | P1 platform |
| PV-09 | Multi-lens hidden-puck movie | 5 | 3 | 5 | 4 | 3 | 20 | P1 |
| PV-10 | “A clean basket is not the bottleneck” | 5 | 3 | 5 | 5 | 4 | 22 | **P0/P1** |
| PV-11 | “Your grinder dial is not a unit” | 5 | 4 | 4 | 5 | 3 | 21 | P1 |
| PV-12 | Temperature: small extraction-chemistry effect, unresolved puck physics | 5 | 3 | 4 | 4 | 4 | 20 | P1 |
| PV-13 | Measure espresso-liquor viscosity | 4 | 2 | 5 | 5 | 2 | 18 | P2 experiment |
| PV-14 | Dynamic channeling under flow versus pressure control | 5 | 2 | 5 | 3 | 3 | 18 | P2 exploratory |
| PV-15 | Model-disagreement experiment recommender | 4 | 4 | 4 | 5 | 2 | 19 | P1/P2 |
| PV-16 | Public fraction and first-drip replication study | 5 | 3 | 4 | 5 | 2 | 19 | P2 participation |
| PV-17 | Pump-curve and screen-clogging bench study | 4 | 4 | 4 | 5 | 2 | 19 | P2 experiment |
| PV-18 | Coffee-bed retention and continuous-wetting measurement | 4 | 2 | 5 | 4 | 1 | 16 | P2/P3 research |
| PV-19 | “The best-understood espresso shot”: one named recipe, every component, evidence attached | 5 | 4 | 4 | 4 | 4 | 21 | **P0/P1 capstone story** |

A sensible execution rule is:

- **P0:** publishable from current data/models with modest engineering.
- **P1:** requires a new analysis or interactive but not a major physical campaign.
- **P2:** requires new measurements, hardware, collaborators, or substantial method development.

---
## 5. Detailed task backlog

### PV-00 — Build a public-results export and claim registry

**Public purpose:** make every article, animation, and headline traceable to the current code, data, evidence label, and validity range. This is the enabling task that prevents public outputs from drifting away from the scientific repository.

**Why it matters:** the current figures already follow the excellent rule that numbers come from harness or data functions rather than being hand-entered. Extend that discipline to public communication. A stable export layer also makes it cheap to produce a website, social cards, notebooks, and articles without duplicating analysis logic.

**Existing basis**

- [`puckworks/harness.py`](https://github.com/trbrewer/puckworks/blob/main/puckworks/harness.py) contains public-ready calculations such as `dissolution_speed_test`, `kappa_t_ladder`, `cross_pressure_discrimination`, `result1_magnitude_comparison`, `g4_temperature_sensitivity`, and `g9_series_resistance`.
- [`puckworks/figures.py`](https://github.com/trbrewer/puckworks/blob/main/puckworks/figures.py) already demonstrates generated-from-code figures.
- The registry and manifest already carry component and dataset provenance.

**Implementation tasks**

1. Add a presentation-only package such as `puckworks/public/`; do not register it as a physics component.
2. Define a `PublicClaim` schema with at least:
   - `claim_id`
   - `public_question`
   - `headline`
   - `plain_language_finding`
   - `numeric_result` and strict units
   - `uncertainty_or_sensitivity`
   - `evidence_strength`
   - `observation_fit_prediction_simulation` badge
   - component names and versions
   - dataset manifest IDs
   - validity range
   - primary caveat
   - practical implication
   - reproduction command
   - source commit hash
3. Implement exporters for JSON, CSV, and Markdown. Suggested command:

   ```bash
   python -m puckworks.public export --out docs/public/generated
   ```

4. Seed the claim registry with the findings in PV-01 through PV-12.
5. Add tests that fail when:
   - a numeric public claim has no unit;
   - a claim has no evidence-strength tag;
   - a simulated claim lacks a simulation badge;
   - a dataset ID is absent from the manifest;
   - a public number is hard-coded instead of generated by a named function;
   - a grinder dial is compared across grinders without an adapter warning.
6. Generate small “claim cards” automatically: headline, one result, one scope sentence, and a QR/link to reproduction.
7. Add a public changelog so that a revised result—such as the corrected fine-grind target—automatically invalidates stale cards.

**Suggested repo artifacts**

```text
puckworks/public/
  __init__.py
  schema.py
  claims.py
  export.py
  render_cards.py
docs/public/
  README.md
  claims.yml
  generated/
  stories/
validation/public/
  test_public_claims.py
```

**Completion criteria**

- One command regenerates every public number and card.
- Every card links to a gate or harness function and a manifest dataset.
- Changing a harness result causes a snapshot test or public-output diff.
- No public artifact requires copying a number from a paper draft by hand.

**Effort:** S, approximately 2–5 focused engineering days.  
**Public deliverable:** not a story by itself, but the foundation for a credible, continuously updated story series.

---

### PV-01 — “The first drop is already strong”: measured fractions plus a wetting-front reveal

**Working headline**

> **The first liquid out of this espresso puck was already about 97% as concentrated as the peak.**

**Public question:** is the first liquid weak because water has only just entered the puck, or can it already be close to saturated with soluble material?

**Existing finding:** in the Waszkiewicz fraction data used by `dissolution_speed_test()`, the early/peak TDS ratio is 0.968, from approximately 24.4% versus 25.2% TDS. This favors rapid dissolution in that configuration and is in tension with a roughly 23-second boulder-diffusion timescale. The first fraction, however, has only one replicate, and the result is one rig/configuration rather than a universal claim.

**Why a layperson should care**

- It overturns the intuitive picture that the first drops must be dilute.
- It separates **wetting time** from **dissolution speed**: liquid may take time to cross the puck while becoming chemically concentrated very quickly.
- It gives a concrete reason to collect fractions rather than judging extraction only from the final cup.
- It is ideal for animation because the most important event occurs before the viewer sees any coffee.

**Analysis and production tasks**

1. Re-run `dissolution_speed_test()` and export the measured fraction times, TDS values, early/peak ratio, and all available replicate information.
2. Quantify robustness to timing choices:
   - first measured fraction versus first two fractions pooled;
   - early/peak and early/final ratios;
   - uncertainty from reported replicates;
   - sensitivity to the first-drop time offset.
3. Run the Foster infiltration component over a small, valid grid of pressure, bed length, and grind-specific parameters to generate wetting-front position versus time and first-drip time.
4. Keep observation and model in separate visual layers:
   - **upper panel — OBSERVED:** fraction TDS points and raw replicates;
   - **lower panel — SIMULATED:** an advancing wetting front, clearly labelled as the Foster sharp-front model.
5. Produce a 15–30 second animation:
   - dry puck;
   - water enters and the front advances;
   - no liquid is yet visible below the basket;
   - first liquid exits;
   - a concentration gauge immediately appears near its peak.
6. Create a “what would falsify this?” panel: a dataset in which early TDS sits far below the peak would support slower dissolution or stronger inventory/transport limits.
7. Write a short article explaining the distinction among infiltration, dissolution, transport, and the visible first drop without equations in the main text.

**Deliverable package**

- A vertical social animation and a landscape web animation.
- A one-page interactive with a time slider.
- A public article: **“What happens inside an espresso puck before the first drop?”**
- A downloadable six-fraction replication protocol, linked to PV-16.
- A technical appendix that reproduces the ratio and model trajectory.

**Practical implication to test, not assume**

A common practice is to treat the first drops as inherently weak or chemically unimportant. This result suggests that claim should be measured rather than assumed. The project should not recommend discarding or retaining first drops on taste grounds until composition and sensory consequences are tested.

**Evidence-safe wording**

- Good: “In this dataset, the first measured fraction was already about 97% of peak TDS.”
- Avoid: “All espresso reaches full strength instantly.”
- Avoid: “The first drop contains all the flavor.”

**Strengthening experiment**

Repeat the fraction protocol across at least:

- three coffees with different roast/freshness;
- three grinds;
- two preinfusion strategies;
- pressure-controlled and flow-controlled shots where available.

A stronger public claim could be promoted if the lower confidence bound for early/peak concentration remains high across these conditions.

**Effort:** S for current-data story; M for a replicated experiment.  
**Primary repo dependencies:** `dissolution_speed_test`, Waszkiewicz TDS data, Foster infiltration component.  
**Public success signal:** viewers can correctly explain that “time before first drip” and “time to dissolve” are different processes.

---

### PV-02 — “The machine can fake a puck problem”: a null-first flow-curve explainer

**Working headline**

> **A flow dip can come from the espresso machine even when the puck model does nothing.**

**Public question:** when a flow curve dips and then recovers, does that prove swelling, fines migration, compaction, erosion, or channeling inside the coffee bed?

**Existing finding:** Foster's machine-only mode—pump plus headspace, with no changing-bed mechanism—reproduces an early dip-and-recovery in its fitted dataset. In a separate Waszkiewicz 9-bar rising-flow window, constant permeability and static pressure-dependent permeability both give a flat-error floor around 0.603 g/s, while a time-dependent dissolution-linked porosity trajectory reaches approximately 0.113 g/s RMSE, about 5.4 times better. The correct public lesson is nuanced: **one familiar curve shape is not a diagnosis, but some traces do contain time structure that a static bed cannot explain.**

**Why this can be highly engaging**

- It resembles a medical diagnostic puzzle: the same symptom can have multiple causes.
- It teaches causal reasoning without requiring advanced mathematics.
- It is immediately useful to people who inspect pressure/flow graphs and infer channeling from shape alone.
- It naturally supports an interactive “guess the cause” experience.

**Analysis and production tasks**

1. Export the Foster machine-only trace and its target data with a **RECONSTRUCTED** badge.
2. Export the Waszkiewicz 9-bar ladder with separate curves for:
   - constant permeability;
   - static pressure-only permeability;
   - time-dependent dissolution-linked porosity;
   - measured trace.
3. Never overlay the two datasets as though they were the same experiment. Use two clearly separated scenes:
   - **Scene A:** machine dynamics can create a dip-and-recovery.
   - **Scene B:** a later rising-flow trace at constant pressure defeats static-bed nulls.
4. Build an interactive quiz:
   - show only a flow curve;
   - ask the viewer to choose “swelling,” “channeling,” “machine,” or “not enough information”;
   - reveal that the curve alone is underdetermined;
   - progressively add pressure, machine state, fraction TDS, or cross-pressure behavior to show how evidence accumulates.
5. Translate RMSE into a public-facing visual such as residual bands or “distance from the measured curve,” while retaining the numeric metric in a details panel.
6. Add a causal diagram showing potential sources of a flow change: pump/headspace, pressure, permeability, viscosity, wetting, dissolution, fines, and spatial heterogeneity.
7. End with a diagnostic checklist for data logging rather than a simplistic cause label.

**Deliverable package**

- Interactive: **“Can you diagnose an espresso puck from its flow curve?”**
- 30–60 second comparison animation.
- Article: **“Your puck may be innocent: why one flow signature has many causes.”**
- A printable measurement checklist for home and café experiments.

**Practical implication**

Do not diagnose swelling or channeling from a dip-and-recovery alone. Record pressure, flow, first-drip time, beverage mass, control mode, and ideally timed TDS fractions. Compare repeated shots and perturb the system rather than interpreting one curve in isolation.

**Evidence-safe wording**

- Good: “A fitted machine-only model reproduced a dip-and-recovery, so that qualitative signature alone is not specific to the puck.”
- Good: “In the separate 9-bar trace, a time-dependent bed model beat the tested flat baselines.”
- Avoid: “Flow curves tell us nothing.” They become informative when paired with additional observables and controlled perturbations.
- Avoid: “Dissolution caused the rising flow.” It is sufficient in the tested model ladder, not uniquely identified.

**Extension**

Use PV-15 to select pressure-step, pause/resume, or control-mode experiments that maximize separation among machine, dissolution, poroelastic, and fines hypotheses.

**Effort:** S.  
**Primary repo dependencies:** Foster machine mode, `kappa_t_ladder`, `cross_pressure_discrimination`, Paper-B Figure 3.  
**Public success signal:** the audience chooses “not enough information” more often after viewing the explainer and can name one additional measurement that would help.

---

### PV-03 — “The cup hides the clock”: the inventory–kinetics flat-valley interactive

> **Corrected 2026-07-18 (matched-endpoint result).** The earlier large-error, transfer-failure
> framing was an artifact of an unmatched fixed-25 s integration window and is retired; the corrected
> reading uses a matched beverage endpoint. See `docs/ANALYSIS_transfer.md` and the corrected
> manuscript `docs/PAPER_A_DRAFT.md`; every number below is a field in the committed Paper A result
> bundle `docs/figures/paper_a/results.json`.

**Working headline**

> **The final cup can hide very different extraction clocks.**

**Public question:** can a model match the final cup while leaving its hidden rate and inventory unresolved?

**Corrected finding.** Fitting a per-species solid inventory and a kinetic rate scale to whole-cup
endpoints leaves the two **practically non-identifiable**: on the caffeine log-parameter objective the
SSE-Hessian **condition number is ≈ 1,930** and the local **inverse-curvature coupling is ≈ −0.99** (a
geometric objective-surface diagnostic, **not** a statistical parameter correlation). The
10%-near-optimal profiled-SSE rate set covers **≈ 76%** of the tested log-rate grid and is
**right-censored** at the upper tested boundary; the MAPE and SSE tolerance sets overlap with **Jaccard
≈ 0.86**. Yet endpoints predict reasonably: across held-out grinds the mechanistic model’s pooled MAPE
is **8.2%** versus **8.6%** for an O-trained **level-only constant**, and the mechanistic model is
**worse than the constant on 50 of 108** held-out points. So the endpoint is reasonably *stable* to
predict, but endpoint accuracy alone supplies little evidence that the kinetic **mechanism** transferred.
Retaining the clock helps: timed fractions sharpen the rate optimum that a collapsed cup flattens, and
an independently measured soluble inventory narrows the conditional rate range.

**Why this has exceptional public and paper value**

- It is a universal scientific lesson expressed through coffee: **fitting an endpoint, identifying
  parameters, predicting another condition, and demonstrating incremental mechanistic skill are four
  different things**.
- The “flat valley” is visually intuitive and interactive.
- It explains why time-resolved measurement matters.
- It is constructive: preserve the clock (timed fractions), measure inventory independently, and
  compare against a level-only null before crediting a mechanism.

**Analysis tasks (already available in the bundle)**

1. The profiled SSE/MAPE valley and a dense 2-D SSE surface over inventory and rate scale
   (`panel_caffeine.profile`, `panel_caffeine.surface`).
2. Identifiability diagnostics: SSE-Hessian condition number and local inverse-curvature coupling; the
   10%-near-optimal tolerance set with explicit right-censoring; the SSE↔MAPE Jaccard overlap
   (`identifiability_panel`).
3. The held-out comparison against the level-only constant baseline (`transfer_skill_vs_baselines`).
4. The fraction-versus-whole-cup positive control (`identifiability_fractions_vs_cup`).
5. The independent-inventory conditional rate (`table7_rate_constraint`).

**Interactive design (four scenes)**

1. **Same cup, different hidden parameters** — “amount available” and log-scale “speed of release”
   controls select precomputed grid points; the endpoint stays similar along the near-optimal valley.
2. **Keep or throw away the clock** — toggle whole-cup vs timed-fraction information and see the
   objective sharpen; label fraction results by their real evidence class (in-sample verification), not
   independent validation.
3. **Prediction is not identification** — mechanistic held-out MAPE 8.2% vs constant 8.6%, worse on
   50/108; show endpoint-prediction stability, parameter identifiability, and incremental skill
   *separately*, never one red/green score.
4. **What measurement would help** — timed fractions, independent inventory, multiple conditions, and a
   null baseline each constrain a different ambiguity.

**Practical implication**

A model tuned on one coffee and grind should not be credited with mechanism from endpoint accuracy
alone. To learn mechanism, preserve time (timed fractions), obtain independent inventory measurements,
and beat a simple level-only null — better *measurement design*, not a more confident endpoint fit,
distinguishes hidden mechanisms.

**Evidence-safe wording**

- Good: “The single-grind endpoint fit is **practically non-identifiable**; endpoint prediction is
  reasonably stable but adds little skill over a level-only null.”
- Avoid: “the mechanism transferred” — endpoint accuracy is not mechanistic validation.
- Avoid the earlier large-error, transfer-failure reading — superseded by the matched-endpoint result.
- Avoid calling the 10% objective set a **confidence interval**, or −0.99 a **statistical parameter
  correlation** — the first is a tested-domain threshold set, the second is objective-surface geometry.

**Effort:** M, a static generated interactive from the committed bundle (v0.4.0 line).
**Primary repo dependencies:** `docs/figures/paper_a/results.json`, `docs/ANALYSIS_transfer.md`,
`docs/PAPER_A_DRAFT.md`, `puckworks/validation/slow/angeloni_bracket.py`.
**Public success signal:** viewers can explain why two hidden parameters may compensate at the endpoint,
why timed fractions are more informative than a final cup, and why prediction stability is not mechanism.

---

### PV-04 — “We killed our favorite result”: a transparent analysis autopsy

**Working headline**

> **We thought a model had explained the fine-grind espresso dip. Then we checked the units and the raw replicates.**

**Public question:** how can an exciting scientific result disappear—or become much weaker—when the target variable and uncertainty are audited?

**Existing finding:** the original target mixed incompatible quantities, including milligram solute masses and gram TDS values, across conditions. After rebuilding the target as TDS-derived extraction yield at a fixed condition, the raw cells are monotone (about 18.3 → 19.4 → 19.6%), while a response-surface fit has a weak interior vertex around dial 1.75. The static channeling model can generate an interior maximum, but it appears in only 10/25 closure combinations, has median prominence around 0.14 EY point, and is near-flat at 9 bar at roughly 0.03 EY point. The measured raw contrast is monotone, and the model bump is small relative to replicate spread. The defensible conclusion is model capacity, not identification of channeling as the cause.

**Why this may be one of the most valuable public stories**

- It is a dramatic narrative with genuine stakes and a reversal.
- It demonstrates scientific self-correction rather than presenting only polished successes.
- It teaches three common errors: mixed units, fitted surfaces outranking raw data, and confusing “a model can make this shape” with “this mechanism caused the shape.”
- It builds trust in the project and differentiates it from confident coffee folklore.

**Analysis and production tasks**

1. Create a chronological “analysis autopsy” with four screens:
   - the tempting original result;
   - the unit audit;
   - the corrected raw TDS-EY cells;
   - the closure and magnitude sensitivity result.
2. Reproduce all raw replicates and uncertainty. Make the raw points the default view.
3. Add a toggle for:
   - raw fixed-condition cells;
   - response-surface curve;
   - model response;
   - model bump versus replicate spread.
4. Explain the distinction between:
   - grinder **dial** optimum;
   - physical **particle-size** reversal;
   - a response-surface vertex;
   - a statistically supported raw interior maximum.
5. Add a small automated “unit linting” demonstration showing why averaging mg and g is not merely inelegant but dimensionally invalid.
6. Publish the corrected claim and retain the retracted/previous claim in a visible revision log.
7. Invite readers to inspect the reproducibility command and compare the old and new outputs.

**Deliverable package**

- Scrollytelling article: **“How we falsified our own espresso headline.”**
- Before/after animation of the target construction.
- Shareable card: **“A model's bump was smaller than the shot-to-shot spread.”**
- Technical note on observable contracts and unit-safe aggregation.

**Practical implication**

Do not assume there is a universal “too fine” optimum from a dial-level response surface. Plot raw replicates, use a coherent yield measure, and distinguish machine-specific dial position from physical grind characteristics.

**Evidence-safe wording**

- Good: “Static heterogeneity remains a viable generator of an interior maximum, but the tested effect is fragile and weak; the data do not identify channeling as the cause.”
- Avoid: “The fine-grind dip is fake.” Fine-grind reversals may occur in other systems; this specific target did not robustly establish one.
- Avoid naming or blaming source authors for the project's own invalid aggregation. Frame it as an internal correction.

**Why this supports a viral paper or article**

Self-correction is usually invisible. Making the revision process public could travel beyond coffee audiences into data science and reproducible research communities.

**Effort:** S for an article using existing outputs; M for a polished interactive.  
**Primary repo dependencies:** `schmieder_interior_max_target`, `result1_magnitude_comparison`, `channeling_interior_max_sensitivity`, Paper-B Figure 1.  
**Public success signal:** readers can distinguish “capacity” from “identification” and understand why the raw cells matter more than the smooth curve.

---

### PV-05 — “Adding more physics made it worse”: the anti-mega-model story

**Working headline**

> **Adding swelling to the extraction model made the prediction worse than a flat line.**

**Public question:** does combining two plausible mechanisms automatically produce a more realistic espresso model?

**Existing finding:** in the shared-porosity composition diagnostic, the extraction-plus-swelling composite has a residual of about 0.648, worse than the flat null around 0.603. The useful result is not that either physical process is absent. It is that two individually plausible branches can be incompatible when they share a state variable or closure.

**Why this matters publicly**

- “More complex is not always better” is immediately understandable.
- It explains the repository's “component registry, not mega-model” philosophy through a concrete failure.
- It is visually simple: measured curve, extraction-only curve, combined curve, flat baseline.
- Negative results of this kind are rare and memorable.

**Tasks**

1. Re-render Paper-B Figure 4 as a public graphic with only four lines and direct labels.
2. Animate the assembly:
   - start from the flat null;
   - add extraction-linked porosity;
   - add swelling through the shared porosity;
   - reveal that the combined prediction over-closes and scores worse.
3. Explain state-variable compatibility with a physical analogy: two map layers can both be accurate individually but use inconsistent coordinate systems.
4. Add a technical inset showing where the shared porosity enters each branch; avoid implying that simple multiplication or addition is generally valid.
5. Create a “model Lego test” checklist:
   - same definition of porosity?
   - same reference volume?
   - same pressure node?
   - same time origin?
   - independently constrained parameters?
   - conservation preserved?
6. Turn the checklist into a reusable gate for future coupled components.

**Deliverables**

- Short article: **“Why espresso models do not simply snap together like Lego.”**
- 20-second animation suitable for social media.
- Developer-facing composition checklist linked from public material.

**Practical implication**

For consumers, the message is not “ignore physics.” It is “do not assume a more elaborate explanation is more trustworthy.” A simple baseline should remain visible, and a combined model must beat it.

**Evidence-safe wording**

- Good: “This particular shared-porosity composition performed worse than the tested flat baseline.”
- Avoid: “Swelling does not happen.” The result diagnoses the composition, not the existence of swelling.
- Avoid: “Simple models are always best.” Complexity is justified when it adds independently validated predictive value.

**Effort:** XS–S.  
**Primary repo dependencies:** `coupled_kappa_t`, Paper-B Figure 4.  
**Public success signal:** readers understand why the project compares components rather than silently stacking all available physics.

---
### PV-06 — Build a cross-pressure “mechanism fingerprint” map

**Working headline**

> **The explanation that works at 9 bar is not the explanation that wins everywhere.**

**Public question:** can changing pressure reveal which hidden mechanism is shaping the shot, even when several models fit one pressure similarly?

**Existing basis:** the repository has eleven pressure traces and a completed `cross_pressure_discrimination()` harness. The standing result is regime-dependent: no single tested permeability mechanism wins at every pressure. A dissolution-linked trajectory performs best on average out of sample, while other closures can be better in low- or mid-pressure regimes. This is within-rig generalization, not external validation.

**Public-value thesis:** a single shot is a photograph; a pressure sweep is a fingerprint. Instead of asking which model fits one curve, show how candidate mechanisms respond differently when the system is deliberately perturbed.

**Analysis tasks**

1. Freeze each model after a declared calibration pressure, initially 9 bar.
2. Predict all remaining pressures without refitting and calculate:
   - RMSE and normalized RMSE;
   - early slope, time to minimum, late slope, and total flow change;
   - uncertainty from measurement replicates and parameter sensitivity;
   - validity-range flags.
3. Repeat with leave-one-pressure-out calibration to check whether the conclusion depends on choosing 9 bar.
4. Build a pressure × mechanism heat map with three layers:
   - raw error;
   - rank by pressure;
   - evidence/validity mask.
5. Cluster pressures into regimes only if the grouping is robust under uncertainty. Avoid drawing hard boundaries from visual inspection alone.
6. Add counterfactual traces showing how each model changes when pressure is moved while all other declared inputs remain fixed.
7. Identify the pressure pair or sequence that maximizes model separation; pass that result to PV-15 as an experiment design.

**Interactive design**

- Pressure slider from the available dataset.
- Measured trace in a fixed panel.
- Candidate mechanisms appear one at a time, not as an unreadable bundle.
- A “fit here” button demonstrates how a mechanism can look convincing at the calibration pressure.
- A “test everywhere” button reveals the full fingerprint.

**Deliverables**

- Interactive **“Pressure fingerprint of an espresso puck.”**
- Public version of the residual heat map in Paper-B Figure 3.
- Technical note on fit-at-one-pressure versus predict-across-pressure.
- A ranked list of the most discriminating pressure protocols.

**Practical implication**

For capable machines, a controlled pressure perturbation can be more informative than repeating a nominal 9-bar shot. For ordinary users, the broad lesson is to change one controlled variable and inspect the response rather than infer mechanism from a single trace.

**Evidence-safe wording**

- Good: “Within this rig and dataset, model performance was pressure-regime dependent.”
- Avoid: “Low-pressure espresso is governed by mechanism X.” The current result compares adopted closures within one dataset.
- Avoid: “One mechanism is universally best.” The existing result says the opposite.

**Effort:** M.  
**Primary repo dependencies:** `cross_pressure_discrimination`, Waszkiewicz traces, Paper-B Figure 3.  
**Public success signal:** viewers understand why deliberate perturbations create more evidence than a single fitted shot.

---

### PV-07 — Build “compound extraction clocks” and search for same-strength, different-composition shots

**Working headlines**

> **The cup is not one substance: different coffee compounds leave on different clocks.**

and, if supported after analysis and validation:

> **Two espressos can have the same strength but different measured chemistry.**

**Public question:** does matching TDS or extraction yield guarantee that two cups have the same chemical composition?

**Existing basis:** the Pannusch/Schmieder lineage provides fraction-resolved kinetics for caffeine, trigonelline, 5-CQA, and TDS-like solids. The model reproduces its calibration data post-fit but has known transfer limitations across grind. That makes it useful as a hypothesis generator and visualization engine, not yet a universal composition predictor.

**Analysis tasks: extraction clocks**

1. For each measured compound and condition, calculate normalized cumulative extraction and timing summaries such as `t10`, `t50`, and `t90`.
2. Plot raw fraction concentrations and cumulative amounts, retaining run-to-run variation.
3. Determine which timing orderings are robust across temperature, flow, and brew ratio rather than highlighting one convenient condition.
4. Compare fraction-resolved curves with the same data collapsed to whole-cup values to reinforce the PV-03 information-loss result.
5. Avoid taste labels. Explain the compounds in neutral, accurate language and link to sensory literature only if a later review supports it.

**Analysis tasks: same-strength, different-composition search**

1. Generate recipes only within the Pannusch component's valid input range.
2. Simulate a grid or optimized set of flow, temperature, shot duration, and brew ratio.
3. Find pairs satisfying a strict endpoint match, for example:
   - TDS within a predeclared tolerance;
   - extraction yield within a predeclared tolerance;
   - beverage mass matched or explicitly displayed.
4. Among those pairs, maximize a composition-distance metric such as standardized Euclidean distance or Jensen–Shannon divergence over normalized compound fractions.
5. Repeat across plausible inventory and kinetic uncertainty. Reject pairs whose composition contrast is not robust.
6. Select a small number of experimentally feasible pairs and validate them with HPLC or another appropriate chemical assay before making a recipe claim.
7. Add a sensory study only after the chemical contrast is confirmed; pre-register whether the goal is triangle discrimination, preference, or attribute rating.

**Visual design**

- Four clocks or racing traces, one per measured compound.
- A cup-strength gauge that remains matched while a composition fingerprint changes.
- A clear division between **model-proposed pair** and **chemically validated pair**.

**Deliverables**

- Interactive **“What leaves the puck when?”**
- Animation of compound extraction clocks.
- Candidate protocol for matched-TDS/different-composition shots.
- Potential paper: **“Endpoint-equivalent espresso profiles with distinct multi-solute trajectories.”**

**Practical implication**

TDS and extraction yield are useful summaries, but they do not necessarily specify composition. Flow profiling may alter the temporal weighting of measured compounds even when the final strength is similar. This should remain a hypothesis until validated beyond the model's calibration setting.

**Evidence-safe wording**

- Good: “The calibrated model and fraction data contain different temporal profiles for measured compounds.”
- Avoid: “Caffeine extracts first” or another universal ordering unless the raw data support it across conditions.
- Avoid: “Same TDS means different flavor.” Chemical and sensory differences must be demonstrated separately.

**Effort:** M for analysis and interactive; L with chemical and sensory validation.  
**Primary repo dependencies:** Pannusch solver, Schmieder fractions, transfer analysis.  
**Public success signal:** users stop treating TDS as a complete chemical description and can explain why fraction timing matters.

---

### PV-08 — Create “Puck Court”: a public evidence dashboard, not a winner leaderboard

**Working concept:** each model enters as a witness with a stated scope. Data serve as cross-examination. Null models remain in the room. The output is an evidence matrix rather than a single score that rewards complexity or post-fit agreement.

**Public question:** with many scientific models of espresso, which ones reproduce their source data, which ones predict independent observations, where do they disagree, and what remains untested?

**Existing basis:** the registry includes component metadata and gates; the manifest records source, units, uncertainty, license, gate use, and validation strength. Paper-B Figure 2 already uses an evidence matrix rather than a winner scoreboard.

**Core dashboard views**

1. **Process map:** machine → infiltration → packing → flow → bed dynamics → extraction → cup observables.
2. **Component cards:** one sentence on purpose, assumptions, valid range, evidence badge, and one notable success or failure.
3. **Challenge cards:** conservation, source-data reconstruction, independent bracket, cross-pressure prediction, cross-grind transfer, composition compatibility, and failure cases.
4. **Disagreement cards:**
   - three `c_sat` values and distinct inventory conventions;
   - alternative temperature partition closures that disagree on direction;
   - static versus time-dependent permeability;
   - synthetic packing versus empirical permeability;
   - one-grind fit versus cross-grind prediction.
5. **Open-question cards:** what new observable would discriminate the current candidates?

**Featured mini-interactive: “What does extractable coffee mean?”**

The repo deliberately preserves `c_sat` values of 170, 212.4, and 224 kg m⁻³ and different inventory conventions. Build a visual that lets users switch lineages and see:

- the number;
- the volume or mass basis;
- whether it represents saturation, total soluble inventory, or a per-solute quantity;
- how silently merging them would change a predicted ceiling or timescale.

The public lesson is not “scientists cannot agree on a constant.” It is “the same-looking number can refer to different bookkeeping systems, and transparent models must expose that.”

**Implementation tasks**

1. Consume the PV-00 export rather than scraping source files in the frontend.
2. Define evidence badges directly from the repo vocabulary; do not invent a combined star rating.
3. Show gate results alongside validity range and calibration status.
4. Create filters by stage, data source, observable, and evidence strength.
5. Add “show me a failure” as a first-class navigation route.
6. Pin every public result to a commit and display when it last changed.
7. Include a one-click reproduction command for technical users.
8. Create a public glossary for permeability, porosity, TDS, extraction yield, post-fit, and identifiability.

**Deliverables**

- Static-first website that can also work without JavaScript for core claims.
- Shareable component and finding cards.
- An automatically generated “state of espresso modeling” report.
- Optional annual article: **“What the models agree on, disagree on, and cannot yet test.”**

**Practical implication**

Consumers gain a way to judge the strength of a coffee claim rather than only its confidence. Researchers gain a visible incentive to provide data, uncertainty, and held-out tests.

**Evidence-safe wording**

- Avoid declaring an overall “best model.” Different components answer different questions and have different evidence types.
- Do not rank a conservation verification above or below an independent experiment on one scalar axis; show dimensions separately.

**Effort:** M.  
**Primary repo dependencies:** registry, gates, manifest, PV-00, Paper-B Figure 2.  
**Public success signal:** users can distinguish verification from validation and can find both a success and a failure for a chosen model lineage.

---

### PV-09 — Produce a multi-lens “hidden puck” movie without building a fake mega-model

**Working headline**

> **An espresso shot begins long before you see the first drop. Here are four scientific lenses on what may be happening inside.**

**Public question:** can the project show the invisible wetting, pore flow, concentration, and permeability processes in a way that is visually compelling and scientifically honest?

**Key design decision:** do **not** force all components into one seamless causal movie unless their contracts and state definitions genuinely compose. Instead, use synchronized **parallel lenses** that share declared inputs but retain separate model labels.

**Suggested four-lens sequence**

1. **Wetting lens:** Foster sharp-front infiltration and first-drip timing.
2. **Pore-flow lens:** lattice-Boltzmann flow through a synthetic packing generated by `brewer2026.pack_generator`.
3. **Extraction lens:** concentration or extracted-mass progression from a selected extraction component.
4. **Heterogeneity lens:** streamtube or N-tube flow shares, clearly marked exploratory where appropriate.

A fifth strip can show **observables available to the machine/user**: pressure, flow, beverage mass, and TDS fractions. This contrast—rich hidden state versus sparse visible data—is itself the story.

**Production tasks**

1. Define a public visualization contract with common time, geometry orientation, and metadata, without pretending the models share every internal variable.
2. Select one reference recipe that lies within each chosen component's valid range; where ranges do not overlap, use separate scenes rather than extrapolating.
3. Generate a synthetic packing at sufficient resolution and verify the associated flow solve using existing LB gates.
4. Render 2D slices or volume paths with physical scale bars where meaningful.
5. Add explicit permanent labels:
   - “synthetic geometry”;
   - “simulation”;
   - component name;
   - evidence strength;
   - time and relevant input.
6. Include toggles for uniform versus heterogeneous flow, but do not make the heterogeneous version look more “real” merely because it is dramatic.
7. Synchronize a measured pressure/flow trace only when the simulated component is legitimately evaluated against that trace; otherwise show a generic reference input.
8. Produce a narrated version that explains what each lens omits.
9. Publish source frames and scripts so visual effects cannot outrun reproducibility.

**Deliverables**

- 60–90 second flagship animation.
- Scrollytelling web page with pause-and-inspect frames.
- Educational stills for talks and articles.
- A “simulation versus measurement” legend reused across all public media.

**Practical implication**

The main action is conceptual: a visible stream from a basket compresses several coupled processes into one number. Better diagnosis requires multiple observables and perturbations.

**Evidence-safe wording**

- Good: “These are model-based lenses on hidden processes.”
- Avoid: “This is a digital twin of your puck.”
- Avoid rendering synthetic spheres as photorealistic grounds without a prominent synthetic label.

**Effort:** M–L depending on rendering ambition.  
**Primary repo dependencies:** Foster infiltration, pack generator, LB solvers, extraction runtime, streamtube/N-tube analyses.  
**Public success signal:** viewers can name at least two hidden processes and recognize that the panels are different models rather than a literal scan.

---

### PV-10 — “A clean basket is not the bottleneck”: visualize the pressure-resistance budget

**Working headline**

> **In the current clean-screen estimate, the coffee puck has roughly 100,000 to 1,000,000 times more hydraulic resistance than the basket screen.**

**Public question:** when a shot runs slowly, is the basket itself usually the dominant restriction, or is the coffee bed doing almost all the hydraulic work?

**Existing finding:** the current geometry-based series-resistance calculation places clean basket/screen resistance approximately 5–6 orders of magnitude below the puck. The open question is fines clogging during a shot, not the clean screen.

**Why this is public-friendly**

- The scale difference is surprising and easy to visualize.
- It provides a practical diagnostic distinction between a clean basket and a clogged/damaged one.
- It can be represented as a pressure-budget or resistance-stack graphic.
- It naturally leads to a simple bench experiment that strengthens the result.

**Analysis tasks**

1. Re-run `g9_series_resistance()` across plausible puck permeability, basket geometry, dose, and bed depth.
2. Show a log-scale resistance stack with a plain-language translation of each order of magnitude.
3. Calculate the clogging factor required for screen resistance to become 1%, 10%, and 50% of total resistance.
4. Propagate uncertainty in hole count, hole diameter, screen thickness, and puck permeability.
5. Separate clean screen, fixture, and puck contributions where the data allow.
6. Avoid converting a geometry estimate into a measured universal constant.

**New validation experiment**

1. Measure water-only flow versus pressure through:
   - open fixture/no basket where feasible;
   - clean basket;
   - basket plus paper/filter accessory if relevant;
   - controlled fines loading or repeated uncleaned shots.
2. Fit a pressure-flow resistance curve and compare with the geometry model.
3. Quantify how much retained fines are required to move the basket into a material fraction of the total pressure drop.
4. Photograph or weigh retained solids to make the clogging state reproducible.

**Deliverables**

- Shareable logarithmic “where the pressure goes” graphic.
- Short video of water-only versus puck-loaded flow.
- Article: **“Is your basket slowing the shot, or is it almost all the puck?”**
- A cleaning/clogging threshold experiment linked to PV-17.

**Practical implication**

For a clean, intact basket in the modeled regime, changes in shot resistance should be investigated first through dose, grind, bed preparation, and coffee state—not attributed to the clean screen. Mid-shot fines clogging remains a plausible separate mechanism.

**Evidence-safe wording**

- Good: “The current clean-screen geometry estimate is 5–6 orders below the puck.”
- Avoid: “Baskets never matter.” Hole geometry, damage, accessories, oils, and fines clogging can matter.
- Avoid: “Precision baskets cannot change extraction.” Flow distribution and geometry may matter even when total hydraulic resistance is small.

**Effort:** S for current model visual; M for bench validation.  
**Primary repo dependencies:** `g9_series_resistance`, basket geometry data, G9 roadmap notes.  
**Public success signal:** the audience can distinguish total resistance from flow distribution and clean-screen behavior from clogging.

---

### PV-11 — “Your grinder dial is not a unit”: build a physical grind-translation study

**Working headline**

> **A grinder dial number is not a particle size, and it is not portable—even to another nominally similar grinder without calibration.**

**Public question:** why can one person's “grind 2” produce a completely different puck from another person's “grind 2,” and what physical measurements can replace dial folklore?

**Existing basis:** the roadmap identifies three incompatible dial spaces and explicitly forbids mapping them without a refit adapter. The Wadsworth grind map is grinder-, calibration-, burr-, and manufacturer-dependent. Existing models expose physical quantities such as particle-size moments, fines fraction, porosity, and permeability.

**Analysis tasks with existing data**

1. Build a visual dictionary for each on-file grinder/dial lineage:
   - dial range;
   - measured particle-size summary;
   - fines fraction or distribution breadth;
   - permeability where available;
   - coffee and burr context.
2. Plot dial position only within its own grinder panel; align panels by a physical latent variable, not by number.
3. Quantify how much prediction error is introduced by naively reusing a dial map across lineages.
4. Test candidate transferable features:
   - `d32` or another size moment;
   - fines mass/number fraction;
   - distribution breadth;
   - measured puck permeability;
   - shot hydraulic response under a standard dose and pressure.
5. Build an explicit per-grinder adapter API that refuses to return a translation outside its calibration range.

**New data study**

1. Select multiple grinders, including nominally identical units if possible.
2. Use the same coffee batch, environmental conditioning, dose, burr age documentation, and sample protocol.
3. Sample at 5–7 settings per grinder.
4. Measure PSD with a defensible method; retain raw distributions, not only a mean.
5. Measure a standardized hydraulic proxy such as permeability or flow under a controlled bed preparation.
6. Recalibrate after burr replacement/alignment to quantify drift.
7. Fit hierarchical per-grinder mappings to shared physical features.
8. Hold out grinders or units to test transfer; do not call an in-sample map a universal translator.

**Deliverables**

- Interactive **“Why your dial number does not transfer.”**
- Public calibration worksheet.
- A physical-grind comparison tool that reports uncertainty and refuses unsupported mappings.
- Potential paper: **“The non-portable espresso grinder dial: cross-unit calibration using PSD and permeability.”**

**Practical implication**

Recipe sharing should include grinder identity and, ideally, a physical or hydraulic calibration point. Users should dial by observed response and taste rather than expecting another person's number to transfer.

**Evidence-safe wording**

- Good: “Dial mappings are calibration-specific and require an adapter.”
- Avoid: “This tool translates every grinder.” A credible tool should be narrow and explicit about unsupported pairs.

**Effort:** M for existing-data explainer; L for a multi-grinder study.  
**Primary repo dependencies:** G5 roadmap gap, Wadsworth grind map, Cameron and Schmieder grinder contexts.  
**Public success signal:** fewer public recipe claims use bare dial numbers without grinder and calibration context.

---

### PV-12 — Temperature explainer: small equilibrium extraction effect, unresolved thermal puck physics

**Working headline**

> **Across 80–98°C, the modeled equilibrium extraction-chemistry effect was modest—and two accepted closures disagreed on its direction.**

**Public question:** does hotter water simply mean “more extraction,” or are temperature effects distributed among chemistry, viscosity, wetting, heat transfer, and sensory perception?

**Existing finding:** two independent partition closures change their partition quantity by less than about 15% over 80–98°C, with a propagated extraction-extent shift around 1.8 percentage points in the tested analysis. Measured cup concentration at the design-center grind and flow spans a median of roughly 3.4% across the temperature axis. The closures disagree on the sign of the partition trend. In-puck thermal transients and temperature-dependent wetting/swelling remain open.

**Why this is compelling**

- Temperature is one of the most discussed espresso variables.
- The result resists a simplistic “hotter extracts more” story.
- Opposite-sign model closures make uncertainty visible.
- It creates a strong reason to distinguish water-setpoint temperature from the evolving temperature inside the puck.

**Analysis tasks**

1. Re-run `g4_temperature_sensitivity()` and show:
   - each closure separately;
   - measured concentration span;
   - propagated extraction extent;
   - no averaged “consensus” line.
2. Separate four pathways in a causal map:
   - equilibrium partition/solubility;
   - diffusivity/kinetics;
   - liquid viscosity and flow;
   - transient puck temperature, wetting, and swelling.
3. Audit whether all compared values refer to the same temperature node—boiler, inlet, puck, or beverage.
4. Create an uncertainty-aware “what this result does not say” panel:
   - it does not say taste is temperature-insensitive;
   - it does not resolve volatile/aroma or reaction effects;
   - it does not establish uniform puck temperature;
   - it does not settle viscosity-mediated flow changes.
5. Design a new fractionated experiment with inlet and outlet temperature sensing, TDS fractions, and fixed hydraulic control.

**Deliverables**

- Interactive **“Where temperature enters an espresso shot.”**
- Two-arrow graphic showing opposite partition trends rather than averaging them away.
- Article: **“Hotter is not one mechanism.”**
- Experimental protocol for transient temperature plus fractions.

**Practical implication**

Temperature changes can matter, but the current evidence suggests that a simple equilibrium-chemistry explanation may account for only a modest part of the observed effect. Recipe advice should not translate this into “temperature does not matter”; it should motivate cleaner tests of which pathway matters.

**Evidence-safe wording**

- Good: “The extraction-chemistry contribution was small in the tested range and models disagreed on direction.”
- Avoid: “Temperature barely affects espresso.” Sensory, thermal, rheological, wetting, and volatile effects remain outside this result.

**Effort:** S for explainer; M–L for instrumented experiment.  
**Primary repo dependencies:** `g4_temperature_sensitivity`, Schmieder temperature data, G4 roadmap notes.  
**Public success signal:** viewers can name at least two temperature pathways other than simple solubility.

---
### PV-13 — Measure espresso-liquor viscosity: “the first drops are not just hot water”

**Working headline, after measurement**

> **The concentrated first liquid can be thick enough to change the shot's own hydraulics.**

**Public question:** flow models usually treat the liquid as water, but early espresso fractions can be highly concentrated. Does their viscosity materially suppress flow and alter the curve people attribute to the puck?

**Existing basis:** the current G10 reference analysis uses coffee-extract rheology above or near the espresso concentration range. It suggests viscosity around 1.27–1.90 times that of water and a directional Darcy-flow suppression to roughly 0.53–0.79 of the pure-water prediction for high-concentration early liquid, while late dilute/equilibrium flow is unchanged. This is a consistency check and extrapolation, not direct validation at espresso TDS and brewing temperature.

**Why this has public value**

- Viscosity is tangible: viewers can see droplets, capillary rise, or flow time.
- It connects chemistry back to hydraulics in a surprising feedback loop.
- A relatively compact measurement campaign could fill a named repository gap and create a reusable public dataset.
- It offers a plausible explanation for early-shot model bias without invoking a new bed mechanism.

**Experimental tasks**

1. Define the target domain before selecting equipment:
   - approximately 2–15% TDS, with denser sampling in the observed espresso range;
   - temperatures spanning practical measurement capability and model needs, ideally from near beverage temperature toward brewing temperature;
   - multiple coffees/roasts to test whether TDS alone predicts viscosity.
2. Choose a method suitable for small, hot, volatile samples:
   - micro-capillary viscometer;
   - rolling-ball microviscometer;
   - controlled-stress rheometer with evaporation control;
   - validated flow-through capillary cell.
3. Calibrate with water and certified viscosity standards at each temperature.
4. Prepare both:
   - real espresso fractions with measured TDS;
   - reconstituted or concentrated coffee extracts that allow a broader controlled grid.
5. Measure density as well as viscosity so kinematic and dynamic viscosity are not confused.
6. Test Newtonian behavior over the shear-rate range relevant to pore flow; report any non-Newtonian behavior rather than forcing a single value.
7. Fit a transparent `mu(T, TDS, coffee)` relation with uncertainty and a validity mask.
8. Add the measured closure as a calibration component only after a model card and gate exist.
9. Re-run the early-shot flow ladder with water versus measured liquor viscosity and quantify how much residual is removed without refitting unrelated parameters.
10. Hold out at least one coffee or concentration range for a transfer test.

**Public visualization**

- Side-by-side capillary or droplet motion for water and concentrated espresso at matched temperature.
- A time-dependent shot trace in which the liquid gradually approaches water-like viscosity as concentration falls.
- A pressure-budget animation showing how the same bed could pass less flow when the liquid itself is thicker.

**Deliverables**

- Open rheology dataset with calibration and uncertainty.
- New component/card for espresso-range `mu(T,TDS)` if justified.
- Article or paper: **“Rheology of espresso-strength coffee liquor and its hydraulic consequence.”**
- Public explainer: **“Why treating espresso as water may miss the first seconds.”**

**Practical implication**

A time-varying flow curve may partly reflect changing liquid properties, not only changing puck structure. This could affect how early-shot deviations are diagnosed and how models interpret pressure/flow data.

**Evidence-safe wording before new data**

- Good: “Reference coffee-extract data predict the correct direction, but espresso-range measurements are still needed.”
- Avoid: “Viscosity explains the early flow transient.” The present analysis only shows plausibility and bounded directional impact.

**Effort:** L unless a suitable rheometer and collaborator are already available.  
**Primary repo dependencies:** `g10_mu_bias_direction`, G10 data/cards and sourcing notes.  
**Public success signal:** a measured espresso-range closure materially improves held-out early-flow predictions without damaging late-flow behavior.

---

### PV-14 — Visualize dynamic channel concentration under flow versus pressure control

**Working headline**

> **In one near-choke simulation, fixed total flow created a winner-take-all channel; fixed pressure did not.**

**Public question:** can the way a machine controls a shot change whether small local differences grow into concentrated flow paths?

**Existing basis:** the exploratory N-tube union assigns each streamtube its own extraction-linked permeability clock. In the tested near-choke, no-lateral-coupling configuration, flow control drives the effective number of active channels toward one, while pressure control does not produce the same concentration. A homogenizing proxy also suppresses the effect. The result is closure-dependent, model-only, and lacks a physical transverse-Darcy coupling law. The finite-time gain near the shutoff floor is not a stability theorem.

**Why this is visually powerful**

- The audience can watch many nearly equal paths collapse toward one dominant path.
- The difference between “hold total flow” and “hold pressure” becomes intuitive.
- It suggests a concrete spatial measurement and paired control-mode experiment.
- It turns the abstract metric `N_eff` into a visible count of active pathways.

**Analysis tasks**

1. Reproduce `ntube_kappa_t_union()` for both control modes at the exact declared reference configuration.
2. Run the owed numerical sensitivity checks before public emphasis:
   - number of tubes;
   - timestep;
   - permeability floor;
   - pressure and grind;
   - alternative extraction clocks;
   - donor-parameter uncertainty;
   - homogenization strength.
3. Report `N_eff`, maximum single-tube share, and the full flow-share distribution over time.
4. Do not call the state “channeling” without qualification; use **“simulated flow concentration in a reduced streamtube model.”**
5. Build a phase map only over tested inputs, with a clearly visible “model-only” banner.
6. Explain why independent pressure-driven tubes lack the same fixed-total-flow competition.
7. Keep the floor-dependence diagnostic visible so the dramatic near-choke result is not presented as a general theorem.

**Visualization tasks**

- Render 50–200 vertical paths as streams whose widths represent flow share.
- Run flow-control and pressure-control animations side by side from the same initial heterogeneity.
- Add a counter showing `N_eff` and the largest path's share.
- Introduce the homogenizing proxy with a slider and explicitly say it is not yet a physical lateral-flow model.

**New experiment suggested by the model**

Develop a segmented outlet or quadrant collector that measures spatial flow over time. Compare paired shots with:

- fixed-flow versus fixed-pressure control;
- matched dose, grind, coffee, and total beverage mass;
- synchronized pressure, total flow, quadrant mass, first drip, and optionally bottomless video.

The primary outcome should be growth or decay of spatial flow-share inequality, not only final extraction yield.

**Deliverables**

- Exploratory animation: **“When one simulated path steals the flow.”**
- Technical sensitivity appendix.
- Segmented-flow experiment design.
- Potential methods paper only after a physical lateral coupling and spatial data exist.

**Practical implication**

Control mode may change the feedback structure of a shot, but the present result is not recipe advice. It motivates measuring spatial flow and treating machine control as part of the mechanism rather than an external setting.

**Evidence-safe wording**

- Good: “The tested reduced model concentrates flow under fixed-total-flow control and not under independent pressure control.”
- Avoid: “Flow control causes real espresso channeling.”
- Avoid: “The puck is mathematically unstable.” The current finite-time result is floor- and closure-sensitive and is not a completed physical stability analysis.

**Effort:** M for a robust model visualization; L for spatial validation.  
**Primary repo dependencies:** `ntube_kappa_t_union`, `ntube_finite_time_gain`, Paper-B Figure 5, G-lat.  
**Public success signal:** the animation produces a clear testable question rather than being mistaken for direct evidence of real channels.

---

### PV-15 — Build a model-disagreement experiment recommender

**Working headline**

> **Instead of asking which espresso theory fits best, ask which next shot would make them disagree most.**

**Public question:** given several plausible mechanisms, what pressure, flow, pause, or fraction-collection experiment would produce the most different predictions and therefore the most information?

**Strategic importance:** this is where `puckworks` can move from a model archive to a research instrument. It also converts uncertainty into an actionable output for collaborators, advanced home users, and cafés with programmable machines.

**Candidate mechanisms**

- machine/headspace dynamics;
- static pressure-dependent permeability;
- dissolution-linked porosity;
- poroelastic response;
- swelling;
- mobile fines or erosion candidates when implemented and adequately parameterized;
- incomplete wetting;
- time-varying viscosity;
- exploratory spatial concentration.

**Candidate interventions**

- constant-pressure shots at multiple pressures;
- constant-flow versus constant-pressure pairs;
- pressure steps, for example low → high → low;
- short pause and resume;
- alternate preinfusion duration;
- matched-output shots with different flow histories;
- same-puck second pass where scientifically and operationally appropriate;
- fraction collection at targeted times rather than uniform intervals.

**Implementation tasks**

1. Define a common experiment specification contract:
   - controllable inputs;
   - machine constraints;
   - measurement cadence and noise;
   - coffee/grind/dose metadata;
   - cost and repeat count.
2. For each candidate model, generate predictions only inside its valid range and propagate declared parameter uncertainty.
3. Define an information objective. Useful starting choices include:
   - maximum minimum pairwise standardized prediction distance;
   - expected information gain under a model prior;
   - mutual information between observable and model identity;
   - robust discrimination score penalized for parameter sensitivity and experimental cost.
4. Allow multiple observables:
   - pressure and flow;
   - first-drip time;
   - timed TDS;
   - total solids removed;
   - spatial outlet flow;
   - puck mass/height before and after;
   - temperature.
5. Optimize over feasible intervention sequences, not arbitrary mathematical inputs a real machine cannot execute.
6. Validate the recommender retrospectively: ask whether it selects the known informative comparison of whole-cup versus fraction-resolved data or single-pressure versus cross-pressure traces.
7. Produce prediction envelopes for the top three experiments and a plain-language reason each should discriminate.
8. Pre-register decision rules before running the physical experiment.
9. After data arrive, score every model without changing the intervention or metric post hoc.
10. Feed the result back into the claim registry whether the outcome is positive, negative, or inconclusive.

**Three high-priority initial protocols to evaluate**

1. **Pressure cycle:** low pressure → high pressure → low pressure. Reversible poroelastic behavior should respond differently from cumulative dissolution or irreversible fines redistribution.
2. **Control-mode pair:** fixed total flow versus fixed pressure with matched output. This directly probes the exploratory feedback highlighted in PV-14.
3. **Targeted fractions around first drip and recovery:** maximize sensitivity to wetting, dissolution speed, viscosity, and early machine dynamics.

**Deliverables**

- A notebook and command-line tool returning ranked experiments.
- An interactive **“Which next shot would teach us the most?”**
- Pre-registration templates and predicted traces.
- A rolling public series in which the audience sees the prediction before the result.

**Practical implication**

The tool should recommend measurements, not a supposedly optimal-tasting recipe. Its value is reducing wasted experiments and making competing explanations falsifiable.

**Evidence-safe wording**

- The recommender identifies experiments with high predicted separation under the current model set. It does not guarantee that any model contains the true mechanism.
- A result that rejects all candidates is scientifically valuable and should be designed as an allowed outcome.

**Effort:** L for a general tool; M for a constrained first version over existing pressure traces and three mechanisms.  
**Primary repo dependencies:** registry valid ranges, harness functions, cross-pressure analysis, public claim schema.  
**Public success signal:** a recommended experiment produces substantially more model separation than a conventional repeat shot and is interpretable before data collection.

---

### PV-16 — Launch a public first-drip and fraction-resolved replication study

**Working headline**

> **Help measure what the final cup hides.**

**Public question:** does the near-peak first fraction and the shape of the extraction clock replicate across ordinary coffees, machines, and recipes?

**Why this is valuable:** the strongest existing first-drop result is memorable but narrow. A carefully designed participation study can turn that limitation into engagement while producing exactly the time-resolved data the transfer analysis says are informative.

**Minimum protocol design**

1. Fix the scientific primary outcomes before recruitment:
   - first-drip time;
   - early/peak TDS ratio;
   - fraction timing and mass;
   - cumulative extraction curve;
   - shot pressure/flow trace if available.
2. Use six collection windows chosen for information, not convenience. A pilot should compare equal-time, equal-mass, and targeted early windows.
3. Require core metadata:
   - machine and control mode;
   - basket and dose;
   - coffee identity, roast date, roast level description, and storage;
   - grinder make/model and dial, with an explicit non-portability warning;
   - water temperature and chemistry if known;
   - preinfusion, pressure/flow program, beverage mass, shot time;
   - refractometer model and calibration.
4. Provide a collection jig or printable guide that reduces fraction-switching timing error.
5. Require repeated shots for a scientific tier; allow single shots in a demonstration tier but do not merge the evidence levels.
6. Record raw values and units, not only calculated extraction yield.
7. Include blank/calibration checks for scales and refractometers.
8. Build automated data validation for impossible times, inconsistent mass balance, missing units, and out-of-range TDS.
9. Use a hierarchical analysis that separates within-user, between-user, coffee, machine, and recipe variation.
10. Predefine promotion criteria for any broader headline, for example a high early/peak ratio across a substantial majority of conditions with uncertainty.

**Participation design**

- **Explorer tier:** first-drip time and video only.
- **Measurement tier:** six fractions and TDS.
- **Research tier:** replicates, logged pressure/flow, and standardized coffee or shared protocol.

This tiering keeps participation broad without pretending all submissions have equal evidentiary strength.

**Deliverables**

- Protocol PDF/Markdown and short demonstration video.
- Upload schema and automated quality report.
- Public map/dashboard of anonymized conditions and fraction curves.
- Periodic “what we learned” reports with raw distributions and caveats.
- An open benchmark dataset for extraction models.

**Practical implication**

Participants learn a technique—fraction-resolved measurement—that reveals extraction dynamics invisible in the final cup. The project gains cross-system data needed to test whether current findings generalize.

**Risks and mitigations**

- **Noisy refractometers:** retain calibration metadata and repeated readings.
- **Timing error:** use video or mass-triggered collection where possible.
- **Selection bias:** recruit beyond advanced profiling-machine users.
- **Unsafe generalization:** analyze machine/coffee strata and preserve single-shot versus replicate tiers.
- **License/privacy:** establish a clear data contribution license and anonymization policy.

**Effort:** L to run well; S–M for a closed pilot with 5–10 collaborators.  
**Primary repo dependencies:** Waszkiewicz fraction schema, manifest discipline, PV-01, PV-03.  
**Public success signal:** at least 100 quality-controlled repeated shots across multiple systems, with enough metadata to test generalization rather than merely display curves.

---

### PV-17 — Measure the machine and outlet: pump curve plus screen-clogging bench study

**Working headline**

> **Where did the pressure go—the pump, the puck, or a clogged outlet?**

**Public question:** how much of an espresso flow curve comes from the machine's pressure-flow characteristic, and when can fines make the basket/outlet resistance matter?

**Existing gaps addressed:** G3 needs a measured pump characteristic rather than a nominal envelope. G9 is resolved for a clean basket in the geometry estimate, but fines clogging during a shot remains unmeasured.

**Bench-study tasks: pump characteristic**

1. Identify the pressure node and sensor calibration explicitly—pump side, line, or basket.
2. Measure steady pressure versus flow over a safe, machine-supported range using controlled hydraulic restrictions.
3. Repeat at relevant temperatures and machine states if the pump/control system changes behavior.
4. Record hysteresis and controller dynamics, not only steady points.
5. Fit candidate forms only after inspecting the curve; do not force the current nominal quadratic if the measured shape differs.
6. Hold out part of the curve or repeated sessions for validation.
7. Document country calibration, firmware, pump type, and machine-specific settings.

**Bench-study tasks: clean and clogged outlet**

1. Measure water-only pressure-flow response for clean baskets and fixtures.
2. Introduce controlled fines masses or standardized clogging states.
3. Measure retained mass and image the screen after each condition.
4. Compare pre-shot and post-shot basket resistance if a safe protocol permits.
5. Fit a time- or loading-dependent outlet-resistance term only if the measurements support it.
6. Test whether the added closure improves held-out shot traces beyond the clean-screen model.

**Public visualization**

- An animated pressure budget that assigns pressure drop to machine, puck, and outlet.
- A clean-screen versus fines-loaded water-flow demonstration.
- A “same puck, different pump curve” counterfactual showing why machine characterization matters.

**Deliverables**

- Open measured pump and outlet curves with uncertainty.
- G3/G9 model-card updates and validation gates.
- Article/video: **“The espresso machine is part of the experiment.”**
- Calibration protocol other labs can repeat.

**Practical implication**

Flow-curve interpretation should include the machine's control and hydraulic response. A clean screen may be negligible in total resistance while a clogged outlet is a different state requiring measurement.

**Evidence-safe wording**

- Do not publish a curve from one machine as “the vibration-pump curve.”
- Do not infer clogging from a slow shot without a clean-state comparison and puck controls.

**Effort:** M–L, depending on instrumentation and machine access.  
**Primary repo dependencies:** G3 and G9 roadmap protocols, Foster machine mode, `g9_series_resistance`.  
**Public success signal:** the measured machine closure improves held-out flow predictions and the clogging threshold is quantified rather than anecdotal.

---

### PV-18 — Measure continuous coffee-bed wetting and retention, not just the front

**Working headline**

> **Before espresso flows, the puck is a partly wet porous material—and that middle state is almost unmeasured.**

**Public question:** how much water is held in a coffee bed at different suction/pressure states, and how easily does water move before the bed is fully saturated?

**Existing gap:** G1 is blocked on coffee-specific constitutive data, not another solver. Sharp-front models can predict a front location, but a continuous-saturation model needs a water-retention curve `theta(psi)` and relative permeability `K_r(theta)` or `K_r(psi)` for a coffee bed.

**Why this is a high-value research target**

- It directly addresses the invisible interval before first drip.
- It could discriminate incomplete wetting from static channeling using first-drip delay and saturation behavior.
- It unlocks a class of models already available in other porous-media fields.
- Imaging a wetting coffee bed is visually compelling even if the first study is an analog column rather than a real portafilter.

**Experimental pathways, in increasing sophistication**

1. **Controlled vertical imbibition column**
   - measure mass uptake, front position, and drainage over time;
   - useful pilot but insufficient by itself if it only gives a sharp-front `sqrt(t)` law.
2. **Pressure-plate or centrifuge retention measurement**
   - equilibrate tamped coffee at controlled suction states;
   - measure water content to build `theta(psi)`;
   - perform wetting and drainage branches to detect hysteresis.
3. **NMR/MRI moisture profiling**
   - measure continuous saturation profiles during imbibition;
   - ideal for observing the region behind and ahead of a nominal front.
4. **X-ray micro-CT with contrast strategy**
   - segment liquid saturation and structural change if resolution and contrast permit;
   - must distinguish swelling/geometry change from saturation.
5. **Transient inverse modeling**
   - infer retention and relative permeability jointly from multiple boundary conditions, with identifiability analysis and independent holdout experiments.

**Required design controls**

- coffee, roast, age, moisture, grind distribution, dose, bed density, and tamp;
- temperature and water chemistry;
- wetting versus drainage history;
- repeated packings to capture preparation variability;
- bed height and wall effects;
- swelling and mass loss, which can otherwise masquerade as saturation change.

**Analysis tasks**

1. Fit standard constitutive families only as candidates; compare them with nonparametric or spline alternatives.
2. Propagate parameter uncertainty into first-drip and flow predictions.
3. Test transfer across grind and bed density.
4. Compare continuous-saturation predictions with the existing sharp-front model on held-out observables.
5. Use PV-15 to choose boundary conditions that best separate retention-curve candidates.

**Deliverables**

- Open retention/relative-permeability dataset.
- Validated coffee-bed closure and model card.
- High-quality wetting-profile animation or imaging sequence.
- Potential paper: **“Water-retention and relative-permeability curves of tamped coffee beds.”**
- Public article: **“The hidden wet stage before espresso appears.”**

**Practical implication**

A physically grounded wetting model could explain why first-drip delay changes with grind or preparation and determine when “dry regions” are plausible. Until these data exist, incomplete-wetting stories should remain hypotheses rather than visual certainties.

**Evidence-safe wording**

- Good: “Coffee-specific continuous-saturation data are the missing ingredient.”
- Avoid: “The puck contains dry pockets” unless directly measured or robustly inferred.

**Effort:** L–XL and likely collaborator-dependent.  
**Primary repo dependencies:** G1 roadmap search target, Foster infiltration, wetting-atom probe.  
**Public success signal:** a measured constitutive curve predicts held-out first-drip/saturation behavior better than a sharp-front-only description.

### PV-19 — “The best-understood espresso shot”: one named recipe, every component, evidence attached

**Working headline**

> **We fixed one exact espresso shot — machine, grinder dial, dose, coffee, temperature — and pointed every model we have at it. Here is what physics can predict about that single shot today, and what no model can yet promise.**

**Public question:** if you fully specify a single espresso shot, how much of it can models actually predict — and where exactly does prediction stop and calibration begin?

**The named shot (fixed spec — do not vary):** DE1 (fixture A traces) · EK43 grinder at dial 1.7 · 20 g in / 40 g out · the Schmieder study coffee · water 80–98 °C. This is the point where the validity ranges of the strength chain (RC-1) and the flavor chain (RC-4) overlap: dial 1.7 sits inside Cameron’s 1.1–2.3 and pannusch’s 1.4–2.0 and is pannusch’s own fitted centre-grind.

**Existing finding:** the repository can already run this shot end-to-end with a registered, gated component in every occupied slot. Strength side (RC-1/RC-3a): parameter-free first-drip prediction 7.0 s / dead volume 8.8 g on this fixture (independent); Cameron Fig. 5 EY curve (independent); mass budgets closed. Flavor side (RC-4a): four-solute kinetics reproduce published fit MAPEs (post-fit) with the temperature set independent; RC-4b connects the machine model to the chemistry through a live adapter that reduces exactly to RC-4a on constant flow and shifts 6.6% under a flow ramp (verification). Three honest gaps are documented, not hidden: the fixture-A pressure-node identity is open (ROADMAP §5.9); the tamped fixture sits at/past the inertial-flow onset (§5.2 audit, Fo_F ≈ 0.86–5.7) so the Darcy slot runs flagged; and Cameron reads absolute EY/TDS low against both independent brackets (egidi; angeloni).

**Why a layperson should care**

- It answers the question people actually ask (“can you just simulate my shot?”) with a concrete, named shot instead of a vague yes.
- It makes evidence strength tangible: on ONE recipe the reader can see measured, post-fit, verification, and open-gap side by side.
- It shows why “the model works” is per-configuration: the bean is a validity parameter, the grinder dial is not a unit, and permeability is fitted per rig — complexity as the story, not the fine print.
- It sets up a cliffhanger that is actually true: the whole end-to-end flavor chain is one physical measurement away from independent validation.

**Analysis and production tasks**

1. Build a stage-by-stage scorecard for the named shot: stage · component · what it predicts here · experimental anchor · validation-strength label (verbatim from cards/gates; no promotions).
2. Run RC-1 end-to-end at the spec and export the EY/TDS trajectory with the Cameron low-read bias band drawn on it (egidi 19.1–22.6% bracket shown as OBSERVED context).
3. Run RC-4a on the Schmieder measured Q(t)/T(t) and RC-4b via the 1.8b adapter on foster machine-mode output; plot the two four-solute cup predictions side by side, labelled post-fit + independent-T (4a) vs verification (4b).
4. Mark the three honest gaps on the scorecard itself (§5.9 node, Fo_F flag, low-read bias) — each with one plain-language sentence.
5. State the packing caveat explicitly: κ = 1.196 was fitted to fixture A with its own coffee; the capstone protocol below therefore includes a one-step per-shot κ refit from the wadsworth prior (this is the documented tiering, not a workaround).
6. “One experiment wide” panel: what a single measured cup (TDS + caffeine + trigonelline + CGA) of this exact shot would promote, and what result would falsify the chain.
7. Short article + interactive scorecard; technical appendix regenerated from a pinned commit via PV-00 conventions.

**Deliverable package**

- A public article: **“The best-understood espresso shot”** (scorecard as hero graphic).
- An interactive per-stage scorecard (hover: component, anchor dataset, strength badge, caveat).
- A one-page printable spec of the named shot + capstone measurement protocol (links PV-15/PV-16 style participation later — closed pilot first).
- Technical appendix reproducing every number from the pinned commit.

**Evidence-safe wording**

- Good: “Every stage of this one shot runs inside a validated or independently gated component.”
- Good: “The flavor chain is verified end-to-end and validated in parts; the combined prediction has not yet been tested against a measured cup.”
- Avoid: “We can simulate any espresso shot.”
- Avoid: “The model predicts flavor” (unqualified).

**Strengthening experiment (the capstone shot — TB)**

Physically pull the named shot on the DE1 (Schmieder-matched coffee; per-shot κ refit step included) and measure the cup: TDS plus caffeine, trigonelline, and CGA; time-resolved fractions if feasible. A match within the stated per-solute bands would promote the end-to-end RC-4b chain from adapter-verified toward independently validated — arguably the single highest-leverage measurement available to the project. A miss is equally publishable under PV-04 conventions.

**Effort:** M for the current-data story; the capstone measurement is a TB item (assay access is the long pole).
**Primary repo dependencies:** RC-1/RC-3a/RC-4a/RC-4b configurations, `harness.py`, `gate_extraction_harness`, foster machine-mode gates, 1.8b adapter gate, egidi/angeloni bracket results, PV-00 export layer.
**Public success signal:** readers can correctly distinguish “validated on this rig” from “verified adapter” from “post-fit calibration” using the scorecard alone.

---
## 6. Convert the five existing scientific figures into five public stories

The repository already renders five manuscript figures from harness outputs. The fastest route to visible value is not to publish those figures unchanged; it is to create a public version of each with one message, one evidence badge, and one action or question.

| Existing scientific figure | Public story | Public redesign | Main caveat |
|---|---|---|---|
| **Fig. 1 — corrected fine-grind target and model capacity** | **“We killed our favorite result.”** | Reveal raw replicates first, then fitted surface, then model bump and uncertainty. Include a visible “claim revised” stamp. | Weak/fragile bump; no channeling identification. |
| **Fig. 2 — mechanism evidence matrix** | **“Puck Court: what each model has actually earned.”** | Replace dense matrix labels with expandable witness cards and evidence badges. | Do not collapse evidence dimensions into one winner score. |
| **Fig. 3 — machine null, 9-bar ladder, cross-pressure map** | **“One flow curve, many causes.”** | Interactive quiz plus fit-here/test-everywhere pressure slider. | Foster and Waszkiewicz panels are distinct datasets and windows. |
| **Fig. 4 — failed shared-porosity composition** | **“Adding physics made it worse.”** | Animate model assembly and show the composite crossing above the flat-null error. | Rejects the composition, not swelling itself. |
| **Fig. 5 — dynamic streamtube concentration** | **“When one simulated path steals the flow.”** | Side-by-side flow-control and pressure-control stream animations with `N_eff`. | Exploratory, closure- and floor-sensitive, no physical lateral coupling. |

### Public-figure specification

Every public version should include:

- a sentence-length title that states the finding, not the method;
- raw observations where available;
- a permanent observed/reconstructed/predicted/simulated badge;
- a one-line scope sentence inside the figure, not only in surrounding text;
- units in familiar and scientific forms where useful;
- direct labels rather than a distant legend;
- a “show details” layer for residuals, equations, and component IDs;
- alt text and a transcript for animations;
- a reproduction link generated by PV-00.

Do not use the same visual grammar for measured and simulated quantities. For example, use points or photographic/trace cues for observations and clearly styled fields/paths for simulations, plus text labels that survive grayscale and screenshots.

---

## 7. Additional low-cost story seeds from current results

These do not need to become standalone flagship projects immediately, but each could produce a short article, graphic, or recurring dashboard card.

### 7.1 “An extraction model read 3.7 yield points low—even though its ceiling was high enough”

The Cameron comparison lands around 15.4% extraction yield against an independent Egidi bracket beginning around 19.1%, while the model's inventory ceiling is above the bracket. The public insight is that a low prediction can arise from kinetics or bookkeeping conventions rather than an insufficient maximum inventory. Build a visual that separates **ceiling**, **rate**, and **observed endpoint**. Preserve the configuration-mismatch caveat and do not frame the comparison as a universal verdict on the model.

### 7.2 “Three scientific lineages use three different saturation concentrations”

Turn the 170 / 212.4 / 224 kg m⁻³ values into a units-and-definitions explainer. The surprise is not the numerical disagreement alone; it is that the quantities coexist with different inventory conventions and should not be silently averaged. This is a strong data-literacy card for PV-08.

### 7.3 “A fixed-flow experiment did not show the famous fine-grind dip”

The Mo fixed-flow data are monotone across grind in the on-file conditions. This is a useful contrast suggesting that machine/control coupling may be part of when a reversal appears. Build a side-by-side “fixed flow versus unconstrained flow” concept graphic, but do not claim control mode is the sole cause without a matched experiment.

### 7.4 “At constant 9 bar, a static pressure law cannot create a time trend”

This is a simple mathematical intuition story: if pressure is constant, a permeability function of pressure alone is also constant. Therefore, a rising flow trace needs time dependence somewhere—bed state, liquid properties, machine state, or another evolving variable. This could be a 20-second educational animation.

### 7.5 “Two temperature models agree on magnitude and disagree on direction”

This is a compact example of why averaging models can hide a conceptual difference. Show arrows of similar small size pointing opposite ways, then ask which direct measurement would resolve the convention.

### 7.6 “A clean screen can be negligible in resistance and still matter to distribution”

Clarify the difference between total pressure drop and spatial flow distribution. This nuance can prevent the PV-10 headline from being misread as “basket design never matters.”

### 7.7 “Different inertia diagnostics are not interchangeable”

The repository explicitly distinguishes Reynolds number and the Wadsworth Forchheimer number. A public methods card could show how two dimensionless-looking numbers answer different questions and why copying a threshold from one into the other is unsafe. This is more suitable for technically curious readers than a broad headline.

### 7.8 “The first dramatic explanation may be an unmeasured nuisance variable”

CO₂, concentration-dependent viscosity, temperature transients, and pump behavior can all confound early-shot mechanisms. A recurring “missing variable of the month” series could explain why a model gap is an invitation to measure rather than a license to invent a parameter.

---

## 8. High-potential article and paper packages

A “viral” result is most likely when the technical finding, visual reveal, and human narrative point in the same direction. The packages below are ordered by readiness and public potential.

### Package A — **The Cup Hides the Clock**

- **Core result:** whole-cup endpoints cannot separately identify inventory and kinetic rate; fractions can.
- **Human narrative:** a seemingly excellent fit collapses when the grind changes.
- **Hero visual:** flat inventory–rate valley transforming into a sharp trough when temporal fractions are restored.
- **Public article:** ready after polished uncertainty/profile analysis.
- **Academic paper:** high potential; the current transfer writeup already supplies the central argument and positive control.
- **Audience beyond coffee:** model calibration, inverse problems, chemical engineering, data science.

### Package B — **One Curve, Many Causes**

- **Core result:** machine-only dynamics can reproduce a familiar flow shape; cross-pressure perturbation provides more discrimination than one trace.
- **Human narrative:** a diagnostic graph invites an overconfident diagnosis.
- **Hero visual:** “guess the cause” reveal followed by the mechanism ladder.
- **Public article:** ready from existing outputs.
- **Academic paper:** part of the current Paper-B arc, with careful scope around fit, within-rig prediction, and mechanism non-uniqueness.
- **Audience beyond coffee:** causal inference and system identification.

### Package C — **How We Falsified Our Own Espresso Headline**

- **Core result:** mixed units and a smooth response surface supported a stronger story than the corrected raw observable and sensitivity analysis.
- **Human narrative:** excitement, audit, correction, better conclusion.
- **Hero visual:** original target dissolving into incompatible units, then raw replicate points appearing.
- **Public article:** immediately viable.
- **Academic output:** reproducible-analysis or methods note on observable contracts, target construction, and model capacity versus identification.
- **Audience beyond coffee:** open science, statistics, reproducibility, science journalism.

### Package D — **Before the First Drop**

- **Core result:** early liquid in one dataset is near peak TDS, while a wetting model shows hidden pre-outlet dynamics.
- **Human narrative:** the shot is chemically active before it becomes visible.
- **Hero visual:** advancing front plus concentration gauge at first drip.
- **Public article/video:** ready with current caveats.
- **Academic paper:** stronger after multi-coffee and multi-control replication.
- **Audience beyond coffee:** porous media, food science, general science media.

### Package E — **More Physics Made It Worse**

- **Core result:** an extraction-plus-swelling composition performs worse than a flat baseline.
- **Human narrative:** the seductive failure of “just add all the mechanisms.”
- **Hero visual:** residual rises as the second model is connected.
- **Public article/video:** immediately viable.
- **Academic role:** supports the registry/methods philosophy and Paper B.
- **Audience beyond coffee:** scientific software, multiphysics modeling, engineering.

### Package F — **Your Grinder Dial Is Not a Unit**

- **Core result:** grinder dial spaces are physically non-portable without calibration.
- **Human narrative:** why copied recipes fail even when people follow the number exactly.
- **Hero visual:** identical dial labels mapping to different PSD/permeability distributions.
- **Public article:** viable from current source comparison.
- **Academic paper:** requires a multi-grinder, multi-unit physical calibration study.
- **Audience beyond coffee:** large and practical; likely strong community participation.

### Package G — **The First Drops Are Not Water**

- **Core result sought:** direct espresso-range viscosity data and its effect on early flow.
- **Human narrative:** the liquid changes the hydraulics while it is being created.
- **Hero visual:** matched-temperature capillary flow of water and concentrated espresso.
- **Public article:** use as a question until measured.
- **Academic paper:** strong new-data opportunity if the measurement and held-out flow test are rigorous.

---

## 9. Evidence-safe headline bank

These are deliberately bold, but each is paired with the sentence that must accompany it.

| Bold headline | Required evidence sentence |
|---|---|
| **The first drop was already almost as concentrated as the peak.** | In one fraction-resolved dataset, early/peak TDS was 0.968; the first fraction was singly replicated and broader replication is needed. |
| **The machine can fake a puck problem.** | A fitted pump-plus-headspace model produced a dip-and-recovery without a changing-bed mechanism, so that curve shape alone is not diagnostic. |
| **A good fit can still be wrong.** | A single-grind refit reached about 7.2% holdout error but inventory and rate were non-identifiable and the calibration failed across held-out grinds. |
| **We killed our favorite espresso result.** | Correcting a mixed-unit target and inspecting raw replicates downgraded an apparent channeling explanation to fragile model capacity. |
| **Adding physics made the prediction worse than a flat line.** | One shared-porosity extraction-plus-swelling composition scored about 0.648 residual versus a 0.603 flat baseline; this rejects the composition, not swelling itself. |
| **A clean basket is not the main bottleneck.** | The current clean-screen geometry estimate is 5–6 orders of magnitude below puck resistance; clogging and distribution effects remain open. |
| **Your grinder dial is not a unit.** | Existing dial maps are grinder- and calibration-specific and should not be transferred without a measured adapter. |
| **The model that worked at 9 bar did not win everywhere.** | Across eleven within-rig pressure traces, mechanism performance was regime-dependent; no tested closure was universally best. |
| **The cup erased the information needed to learn the rate.** | Fraction-resolved scoring produced a sharp kinetic optimum, while collapsing the same data to a whole-cup endpoint flattened it. |
| **Scientists use different meanings of “extractable coffee.”** | The repository carries multiple saturation and inventory conventions side by side because they are not interchangeable quantities. |
| **Two temperature models disagreed on whether the partition increased or decreased.** | Both predicted a modest magnitude over 80–98°C but used closures with opposite directional trends; thermal puck physics remains unresolved. |
| **One simulated flow path stole almost everything.** | This occurred in a tested near-choke reduced model under fixed-total-flow control with no physical lateral coupling; it is exploratory, not direct observation. |
| **At constant pressure, a pressure-only bed law cannot create a time trend.** | In the 9-bar ladder, static pressure-dependent permeability ties the constant-permeability null; some evolving state is required in the tested window. |
| **Two equally strong cups may not be chemically identical.** | Treat this as a model-generated hypothesis until matched-TDS recipe pairs are confirmed chemically and, separately, sensorially. |
| **Hotter is not one mechanism.** | Equilibrium chemistry, diffusivity, viscosity, transient heat transfer, wetting, and sensory effects must be separated rather than collapsed into one temperature rule. |

A headline should be rejected or rewritten if its scope sentence is too long to display with it. That is usually a sign that the headline overreaches the evidence.

---

## 10. Reusable analysis techniques that will keep generating public value

The following techniques can be applied across the repository and should become standard utilities, not one-off notebook work.

### 10.1 Null-first ladders

Always compare a proposed mechanism with:

1. constant baseline;
2. machine-only baseline where relevant;
3. static state dependence;
4. simplest time dependence;
5. richer mechanism.

Public value comes from seeing exactly which rung becomes necessary.

### 10.2 Fit-here, test-there maps

For every calibrated result, show both:

- the conditions used to set parameters;
- a frozen-parameter prediction on another pressure, grind, coffee, machine, or time window.

This makes transfer visible and prevents a fitted line from being mistaken for prediction.

### 10.3 Profile-likelihood and compensation visualizations

Whenever two parameters can move the same observable, compute a profile surface and show the flat direction. The inventory–kinetics valley is the first example; porosity–permeability and pump–puck resistance may produce similar opportunities.

### 10.4 Effect size versus replicate variability

For every visually dramatic bump or optimum, compare:

- peak prominence;
- uncertainty in the fitted curve;
- raw within-cell spread;
- sensitivity to closure choices;
- whether the contrast changes sign.

This makes “smaller than the noise” a quantitative statement rather than rhetoric.

### 10.5 Closure-sensitivity maps

A mechanism that appears under one empirical closure may vanish under another. Build two-dimensional maps over closure parameters and show the fraction of plausible space where the public feature persists.

### 10.6 Observable and unit linting

Automate checks that prevent:

- mixed physical dimensions;
- cup mass being treated as extraction yield;
- dial position being treated as particle size;
- pressure nodes being silently exchanged;
- kinematic and dynamic viscosity being confused;
- fitted and held-out datasets being merged.

A visible “unit-safe” badge can become part of public trust.

### 10.7 Counterfactual pairs

Find two cases with the same visible endpoint but different hidden states, or the same hidden mechanism under different controls. Examples:

- same TDS, different compound profile;
- same flow curve, machine versus bed cause;
- same final EY, different temporal extraction path;
- same dial number, different PSD;
- same total flow, different spatial distribution.

Counterfactual pairs are naturally shareable because they reveal why intuition based on one observable can fail.

### 10.8 Experiment design by model disagreement

Use the ensemble as an acquisition function: choose the next condition where defensible models disagree most relative to measurement noise. Publish predictions before running the experiment.

### 10.9 Negative-result preservation

Maintain first-class public cards for:

- failed transfer;
- failed composition;
- null-model success;
- weak or vanished peak;
- closure disagreement;
- unresolved data gap.

A project that visibly preserves negative results will accumulate trust and unique content over time.

---
## 11. Technical implementation plan for public outputs

### 11.1 Suggested public claim schema

A human-readable YAML entry could look like this:

```yaml
claim_id: PV-FIRST-DROP-001
question: How concentrated is the first measured espresso fraction?
headline: The first measured liquid was about 97% of peak TDS.
status: active
result:
  value: 0.968
  quantity: early_to_peak_tds_ratio
  units: dimensionless
  uncertainty: first fraction has one replicate; show source replicates
badge: OBSERVED
strength: independent_within_rig
scope:
  dataset: waszkiewicz2025/tds_fractions
  configuration: source rig and fraction protocol
components:
  - none_for_ratio
related_models:
  - foster2025.infiltration
  - cameron2020.extraction_bdf
caveat: One dataset and configuration; not a universal dissolution law.
practical_implication: Measure early fractions rather than assuming they are dilute.
producer: puckworks.public.claims.first_drop
reproduce: python -m puckworks.public show PV-FIRST-DROP-001
```

The numeric field should be populated by code at export time rather than treated as the authoritative source in YAML.

### 11.2 Public artifact bundle per story

Each story should generate the same bundle:

```text
story-id/
  claim.json
  data.csv
  figure.svg
  figure.png
  animation.mp4          # when relevant
  alt-text.txt
  article.md
  methods.md
  provenance.json
  LICENSE_NOTES.md
```

This creates a consistent handoff to a static site, newsletter, journalist, conference talk, or social post.

### 11.3 Reproduction and CI

Add a public build command such as:

```bash
python -m puckworks.public build --all --strict
```

The strict build should fail when:

- a source gate is red;
- a claim points to a missing dataset or component;
- a result changed beyond a declared tolerance without a claim-status review;
- a simulated artifact lacks a badge;
- a public figure omits units or scope;
- a license note is missing;
- a dial comparison lacks a grinder-specific scope;
- a post-fit result is labelled predicted or independent.

Slow analyses should remain outside ordinary CI according to the repo rules. Cache their versioned outputs with the exact command and commit, then use a lightweight integrity check in the public build.

### 11.4 License-aware publishing

The manifest should drive what can be republished. Add fields or derived checks for:

- raw-data redistribution allowed;
- derived statistics allowed;
- figure-digitization restrictions;
- attribution text;
- non-commercial limitations;
- whether only code and a retrieval script may be distributed.

A public visualization should not silently embed source data whose license permits analysis but not redistribution. Where necessary, publish derived summaries and a retrieval/reproduction guide rather than the raw table.

### 11.5 Accessible design

- Provide text alternatives for every figure and a transcript for every animation.
- Do not rely on color alone for evidence categories or model identity.
- Use direct labels and plain-language units.
- Provide a reduced-motion version of animations.
- Make core claims available in static HTML/Markdown.
- Define every technical term at first use and offer an optional technical layer rather than stripping away accuracy.

### 11.6 Audience testing as part of “done”

Before release, test each flagship story with several people who drink coffee but do not work in porous-media modeling. Ask only:

1. What do you think the main finding was?
2. Was it measured or simulated?
3. What does it not prove?
4. What, if anything, would you do differently?

If the answers diverge from the intended claim, revise the artifact rather than adding a longer caption.

---

## 12. A 30/60/90-day execution roadmap

The schedule below assumes the goal is to demonstrate visible public value quickly while preserving the repository's scientific discipline. It can be compressed or expanded according to available engineering, design, and laboratory capacity.

### Days 1–30 — Establish the public pipeline and publish three quick wins

**Build**

- Implement PV-00 claim schema, exporter, provenance, and strict checks.
- Create a simple `docs/public/` landing page generated from current repo state.
- Define observed/reconstructed/predicted/exploratory visual badges.
- Create reusable figure and article templates.

**Publishable MVPs**

1. PV-01 first-drop measured graphic plus a simple wetting-front animation.
2. PV-02 machine-null versus time-dependent-bed explainer.
3. PV-05 failed-composition animation: more physics made it worse.
4. PV-10 clean-screen resistance card if the license and source audit are complete.

**Research work**

- Re-run all source harnesses and freeze public-output snapshots.
- Audit uncertainty, units, validity range, and license for each headline.
- Begin the dense profile surface for PV-03.

**Decision gate at day 30**

Do not judge only views. Use audience tests to determine whether viewers correctly identify what was observed, what was modeled, and the key limitation. Revise the visual grammar before producing more stories if those distinctions are unclear.

### Days 31–60 — Release the two strongest interactive narratives

**Build**

- Complete PV-03 inventory–kinetics flat-valley interactive.
- Complete PV-04 self-correction scrollytelling piece.
- Build the first PV-08 “Puck Court” page with 8–10 representative components rather than attempting the entire registry at once.
- Translate Paper-B Figures 1–4 into public versions.

**Research work**

- Add bootstrap/profile-likelihood analysis to the transfer result.
- Complete leave-one-pressure-out checks and public heat map for PV-06.
- Run a bounded same-TDS/different-composition search for PV-07, clearly as a model proposal.
- Build a constrained PV-15 recommender over three mechanisms and the available pressure protocols.

**Editorial work**

- Publish **“The Cup Hides the Clock.”**
- Publish **“How We Falsified Our Own Espresso Headline.”**
- Prepare a journalist/researcher packet with figures, methods, source links, and exact scope language.

**Decision gate at day 60**

Choose one new-data pilot based on three criteria:

1. model disagreement is large relative to expected measurement noise;
2. the result would change interpretation or practice;
3. the experiment produces a compelling observable or visual even if all current models fail.

The leading candidates are fraction replication, pump characterization, and a control-mode/pressure-step pair.

### Days 61–90 — Run a closed experimental pilot and launch the evidence dashboard

**Build**

- Expand PV-08 to the full registry and selected manifest datasets.
- Complete PV-06 pressure fingerprint interactive.
- Render PV-09 multi-lens hidden-puck prototype.
- Add a public revision log and “show me a failure” route.

**Experiment**

Run one closed, quality-controlled pilot before public crowdsourcing:

- 5–10 collaborators;
- standardized metadata and calibration;
- repeated shots;
- pre-registered primary outcome;
- automated data validation;
- predicted model traces published before analysis.

Recommended first pilot: **targeted early fractions plus pressure/flow logging across two preinfusion or pressure protocols.** It reinforces PV-01, PV-02, PV-03, and PV-15 simultaneously.

**Release**

- Publish the pilot protocol, predictions, result, and all allowed data.
- Publish an honest outcome even if no model separates.
- Decide whether the pilot is ready for PV-16 public participation or needs another closed iteration.

---

## 13. Suggested success metrics

Public value should not be reduced to clicks. Use four metric families.

### 13.1 Scientific integrity metrics

- 100% of numeric public claims generated from named functions.
- 100% carry evidence badge, strength, scope, caveat, and source IDs.
- 100% of simulated visuals permanently labelled.
- No post-fit result presented as held-out prediction.
- Every changed result triggers a public revision review.
- Every public dataset/artifact has a license note.

### 13.2 Comprehension metrics

For each flagship artifact, measure whether a non-specialist can correctly answer:

- the main finding;
- whether it was measured or simulated;
- the primary limitation;
- one useful consequence.

A suggested release threshold is at least 70–80% correct in a small pre-release comprehension test, with the limitation question weighted as heavily as the headline question.

### 13.3 Engagement metrics

Prefer indicators of retained value over raw impressions:

- completion rate for an animation or scrollytelling piece;
- saves/bookmarks and shares;
- clicks from a headline card to methods or reproduction;
- interactive completion rate;
- newsletter sign-ups attributable to a specific story;
- external articles that preserve the scope sentence;
- GitHub clones, issue discussions, and reproduced figures.

### 13.4 Research and action metrics

- number of quality-controlled contributed shots or fraction curves;
- number of independent replications;
- number of models tested on genuinely held-out conditions;
- reduction in model disagreement after a targeted experiment;
- new datasets that close a named roadmap gap;
- protocols adopted by another lab, café, or enthusiast group;
- a prediction made public before the corresponding experiment;
- negative results retained and cited rather than disappearing.

### 13.5 Practical-use metrics

For consumer-facing techniques, test whether users can perform them reliably:

- fraction timing error;
- refractometer repeatability;
- metadata completeness;
- between-user reproducibility;
- whether a diagnostic recommendation changes after better measurements;
- whether physical grind calibration predicts behavior better than dial number alone.

---

## 14. What not to build yet

These ideas are attractive but would likely overrun the current evidence.

### 14.1 A universal “best espresso recipe” engine

Cross-grind and cross-dataset transfer is not strong enough. A near-term tool should expose model disagreement and validity ranges rather than return a falsely precise optimum.

### 14.2 A photorealistic “digital twin” of a real puck

Synthetic sphere packings and reduced streamtubes are useful scientific objects, but they are not a scan of a user's coffee bed. A multi-lens simulation is safer and more informative.

### 14.3 A taste predictor from TDS and four compounds

Composition is not sensory perception. Build the chemistry layer first, then add pre-registered sensory validation.

### 14.4 A channeling detector based only on a bottomless video or flow curve

The machine null and model non-uniqueness argue directly against this. A credible detector would need spatially resolved validation, repeated shots, and control perturbations.

### 14.5 A universal grinder dial translator

Build per-grinder calibration adapters and physical-feature comparisons. Refuse unsupported translations rather than filling gaps with interpolation.

### 14.6 A single model leaderboard score

Verification, source-data reconstruction, independent validation, transfer, conservation, and runtime answer different questions. A composite score would recreate the silent-merging problem at the evaluation level.

### 14.7 A seamless all-physics simulation assembled from every component

The failed shared-porosity composition is a warning. New coupling should be justified by compatible contracts, conservation, independently constrained parameters, and a gate that beats the relevant null.

---
## 15. Issue-ready first backlog

The following tickets can be created directly. They are ordered so that early work produces visible artifacts while building reusable infrastructure.

### Issue 1 — `PV-00a: public claim schema + generated export`

**Work**

- Add `PublicClaim` schema and JSON/Markdown exporters.
- Implement claims for first-drop ratio, κ(t) ladder, failed composition, corrected fine-grind magnitude, transfer valley, clean-screen resistance, and temperature sensitivity.
- Attach dataset IDs, components, evidence badges, scope, caveats, and reproduction commands.
- Add strict validation tests.

**Done when**

- `python -m puckworks.public build --all --strict` succeeds on a green repository.
- Seven seed claims are generated without hand-entered result values.
- Deliberately mislabelling a post-fit claim as prediction makes a test fail.

### Issue 2 — `PV-01a: first-drop public figure + 30-second animation`

**Work**

- Export raw Waszkiewicz fraction data and replicate metadata.
- Calculate early/peak robustness variants.
- Generate one valid-range Foster wetting-front trajectory.
- Produce measured and simulated panels with permanent labels.
- Write article and alt text.

**Done when**

- The numeric result reproduces from the harness.
- The first-fraction replication limitation is inside the visual.
- A layperson test distinguishes wetting time from dissolution time.

### Issue 3 — `PV-02a: one-curve-many-causes interactive`

**Work**

- Build the machine-only scene and the separate 9-bar ladder scene.
- Add “guess the cause” and “add another observable” interaction.
- Include pressure, flow, first-drip, and fraction data as progressive evidence.

**Done when**

- The interface never implies the two source traces are one experiment.
- The correct answer to the initial curve-only question is “not enough information.”
- The 5.4× improvement is shown with its sufficiency-not-uniqueness caveat.

### Issue 4 — `PV-05a: failed-composition public animation`

**Work**

- Re-render the shared-porosity diagnostic with direct labels.
- Animate extraction-only → extraction plus swelling → flat-null comparison.
- Add the model-composition checklist.

**Done when**

- Residuals are generated from the current function.
- The graphic explicitly says the result rejects the composition, not swelling.
- The artifact can be embedded as a standalone 20-second clip.

### Issue 5 — `PV-03a: inventory–kinetics profile surface`

**Work**

- Generate dense error contours and profile likelihoods.
- Add bootstrap and fixed-inventory comparisons.
- Reproduce same-grind fit, held-out same-grind, held-out-grind, and fraction-positive-control panels.
- Implement the two-slider interactive.

**Done when**

- The flat direction and cross-grind failure are visible without reading methods.
- Parameters remain frozen during held-out prediction.
- A data-collapse toggle demonstrates loss of rate information.

### Issue 6 — `PV-04a: fine-grind analysis revision story`

**Work**

- Build a revision timeline from invalid aggregation to corrected target.
- Add raw replicates, uncertainty, RSM curve, model bump, and closure-sensitivity map.
- Create a permanent retraction/correction note for any superseded public claim.

**Done when**

- No mixed-unit quantity appears.
- The graphic distinguishes dial vertex, particle-size reversal, and raw-cell trend.
- The conclusion says model capacity, not causal identification.

### Issue 7 — `PV-08a: Puck Court MVP`

**Work**

- Publish 8–10 representative components and 6 challenge cards.
- Add evidence filters and a “show me a failure” route.
- Include the `c_sat`/inventory-convention mini-interactive.

**Done when**

- No overall winner score exists.
- Verification and independent validation are visibly distinct.
- Every displayed result links to provenance and reproduction.

### Issue 8 — `PV-15a: constrained experiment recommender + closed pilot protocol`

**Work**

- Compare at least three existing mechanisms over feasible pressure programs.
- Rank a pressure cycle, control-mode pair, and targeted fraction schedule.
- Generate pre-registration and data schema for the top protocol.

**Done when**

- The chosen intervention has greater predicted separation than a repeated nominal shot.
- Measurement noise and parameter uncertainty are included.
- “All models fail” is an explicit possible outcome.

---

## 16. Experiment portfolio: what each new measurement would resolve

| Experiment | Primary competing explanations | Key observable | Minimum hardware/data | Public visual | Main risk |
|---|---|---|---|---|---|
| Targeted early fractions | fast dissolution vs slower kinetics; wetting delay; viscosity | early/peak TDS, fraction curve, first drip | scale, fraction collector, refractometer, timing/video | concentration appears at first drip | switching/timing and refractometer error |
| Low→high→low pressure cycle | reversible poroelastic response vs cumulative dissolution/fines | hysteresis in flow and TDS | programmable pressure, logging, fractions | same pressure revisited with different history | machine/controller dynamics confound |
| Fixed-flow vs fixed-pressure pair | flow-stealing feedback vs independent paths | spatial flow-share inequality, total trace | profiling machine; ideally segmented collector | one path grows under one control mode | model result may not survive physical lateral coupling |
| Pump pressure-flow bench | machine dynamics vs puck change | measured pump/control characteristic | calibrated pressure and flow, safe restrictions | machine curve revealed outside coffee | machine-specific result and sensor-node ambiguity |
| Clean vs fines-loaded basket | clean-screen negligible vs clogging | outlet resistance and retained fines | water-flow bench, controlled fines, imaging/scale | clean basket suddenly becomes restrictive after loading | reproducing realistic clogging state |
| Espresso-liquor rheology | changing liquid properties vs changing bed | `mu(T,TDS)` and early-flow correction | microviscometer/rheometer, temperature control, TDS | water and espresso flow differently | small hot samples, evaporation, extrapolation |
| Retention/relative permeability | sharp-front wetting vs continuous saturation | `theta(psi)`, `K_r(theta)`, saturation profile | pressure plate/centrifuge or MRI/CT collaborator | bed gradually wets before first drip | swelling and dissolution confound water content |
| Multi-grinder calibration | portable dial myth vs physical grind features | PSD, fines fraction, permeability | multiple grinders, PSD method, standard coffee | same dial, different distributions | unit/burr variation and sampling bias |
| Matched-TDS profile pair | one-number strength vs composition trajectory | HPLC compound profile and sensory discrimination | profiling machine, chemical assay, panel | same strength gauge, different fingerprint | model transfer limitations; no sensory difference |
| Named-shot capstone cup (PV-19) | end-to-end model prediction vs per-slot post-fit calibration; Cameron absolute low-read | four-solute cup composition (TDS + caffeine/trigonelline/CGA) of the named shot; time-resolved fractions if feasible | DE1 + EK43 (dial 1.7, 20/40 g), Schmieder-matched coffee, per-shot κ refit, chemical assay, refractometer | one fully-specified shot: predicted vs measured cup on the scorecard — promotes the RC-4b end-to-end chain from verification toward independent, tests Cameron low-read on a fully specified shot, and exercises the per-shot κ refit tiering | assay access and per-solute band width are the long poles |

The first new-data experiment should ideally serve several stories at once. Targeted fractions with pressure/flow logging are especially efficient because they inform dissolution speed, identifiability, wetting, viscosity, machine dynamics, and cross-pressure interpretation.

---

## 17. Recommended first sequence

### Start immediately

1. **PV-00 public result layer.** It protects every later artifact and makes revisions cheap.
2. **PV-01 first-drop story.** It has the best combination of surprise, visual potential, and simple measured result.
3. **PV-02 machine-null story.** It teaches the project's null-first philosophy and is directly useful to profile-reading enthusiasts.
4. **PV-05 failed composition.** It is the fastest high-quality negative-result story and explains why the repo is not a mega-model.

### Build next

5. **PV-03 flat-valley interactive.** This is probably the strongest paper-quality result with relevance beyond coffee.
6. **PV-04 self-correction article.** This is likely the strongest trust-building and shareable research narrative.
7. **PV-06 pressure fingerprint.** It turns the repository into a mechanism-discrimination tool.
8. **PV-08 Puck Court.** Launch after the first claims establish the visual and evidence language.
9. **PV-19 best-understood-shot scorecard.** It converts the registry’s per-slot evidence discipline into a single concrete story, and its capstone measurement is a natural PV-15 candidate.

### Use those outputs to choose one experiment

10. Prototype **PV-15** and select a closed pilot, with targeted fractions as the default unless the disagreement calculation favors another intervention.
11. Expand to PV-16 public participation only after the closed pilot demonstrates acceptable timing, metadata, and measurement quality.

### Pursue as larger research programs

12. Grinder transfer (PV-11), viscosity (PV-13), spatial flow/control (PV-14), machine/outlet characterization (PV-17), and retention curves (PV-18).

This ordering maximizes public output per unit effort while preserving a path from communication to genuinely new science.

---

## 18. Repository source map used for this roadmap

The recommendations above are grounded primarily in the following current repository materials:

- [`README.md`](https://github.com/trbrewer/puckworks/blob/main/README.md) — project purpose, founding components, data/gate philosophy, and relationship to PUCK LAB.
- [`CLAUDE.md`](https://github.com/trbrewer/puckworks/blob/main/CLAUDE.md) — architecture rules, validation-strength vocabulary, manifest requirements, conflicting-constant policy, strict units, and grinder-dial non-portability.
- [`docs/ONBOARDING.md`](https://github.com/trbrewer/puckworks/blob/main/docs/ONBOARDING.md) — standing caveats and current interpretation of major analysis threads.
- [`docs/ROADMAP.md`](https://github.com/trbrewer/puckworks/blob/main/docs/ROADMAP.md) — development sequence, open gaps G1–G10/G-lat, current change log, and experiment/sourcing needs.
- [`docs/SPRINTS.md`](https://github.com/trbrewer/puckworks/blob/main/docs/SPRINTS.md) — implementation status and sequencing.
- [`docs/ANALYSIS_P2.md`](https://github.com/trbrewer/puckworks/blob/main/docs/ANALYSIS_P2.md) — extraction comparison, dissolution-speed discriminator, κ(t) ladder, corrected fine-grind verdict, and N-tube exploration.
- [`docs/P3_hypotheses.md`](https://github.com/trbrewer/puckworks/blob/main/docs/P3_hypotheses.md) — competing fine-grind hypotheses, model-capacity correction, and discriminating measurements.
- [`docs/ANALYSIS_transfer.md`](https://github.com/trbrewer/puckworks/blob/main/docs/ANALYSIS_transfer.md) — cross-dataset transfer failure, inventory–kinetics identifiability, and fraction-resolved positive control.
- [`docs/PAPER_OUTLINE.md`](https://github.com/trbrewer/puckworks/blob/main/docs/PAPER_OUTLINE.md) — paper division, corrected claim skeletons, figure plan, and readiness audit.
- [`docs/PAPER_B_DRAFT.md`](https://github.com/trbrewer/puckworks/blob/main/docs/PAPER_B_DRAFT.md) — current manuscript framing for mechanism discrimination.
- [`puckworks/harness.py`](https://github.com/trbrewer/puckworks/blob/main/puckworks/harness.py) — reproducible comparison and sensitivity functions that should feed public claims.
- [`puckworks/figures.py`](https://github.com/trbrewer/puckworks/blob/main/puckworks/figures.py) — generated Paper-B figures and a model for keeping numbers code-derived.
- [`puckworks/validation/gates.py`](https://github.com/trbrewer/puckworks/blob/main/puckworks/validation/gates.py) — quick validation and consistency gates.
- [`puckworks/data/MANIFEST.csv`](https://github.com/trbrewer/puckworks/blob/main/puckworks/data/MANIFEST.csv) — dataset provenance, units, uncertainty, license/access, gate use, and evidence strength.
- [`puckworks/models/__init__.py`](https://github.com/trbrewer/puckworks/blob/main/puckworks/models/__init__.py) — registered components, assumptions, valid ranges, and notes.

Because the repository is active, public outputs should always be regenerated from a pinned commit rather than treating the numeric examples in this planning document as a permanent source of truth.

---

## Closing assessment

`puckworks` already contains enough material to demonstrate substantial public value without waiting for a universal model or a new laboratory campaign. Its most distinctive asset is the combination of:

- hidden-process models that can be visualized;
- real data capable of rejecting simple stories;
- explicit nulls and held-out tests;
- negative results that remain visible;
- a disciplined language for evidence strength;
- open gaps that translate directly into understandable experiments.

The central public identity should be:

> **Espresso under cross-examination: what we can see, what the models infer, what the data rule out, and which next shot would tell us more.**

That identity can support bold headlines without sacrificing trust, because the caveat, evidence badge, and reproduction path are part of the product rather than an afterthought.
