# Detailed review of `PAPER_OUTLINE.md`

## Overall assessment

The **two-paper strategy is sound**, and Paper A is substantially closer to a defensible manuscript than Paper B. Paper B, however, is **not manuscript-ready in its current form**. Its central Result 1 rests on a submission-blocking aggregation error; Result 2 contains a useful null-first analysis but overstates what is identified and refers to a superseded coupling implementation; and Result 3 is an interesting exploratory numerical result, not yet an unconditional physical-instability finding. The outline’s own validation-strength discipline is excellent, but several headline sentences do not obey it.

My revised readiness judgment is:

| Element | Outline assessment | Review assessment |
|---|---:|---:|
| Two-paper division | Ready | **Sound** |
| Paper A core argument | Draft exists | **Amber–green** |
| Paper B title and abstract | Claim skeleton | **Red: major reframing needed** |
| Result 1: Schmieder discrimination | Ready | **Red: current target is invalid** |
| Result 2: 9-bar ladder | Ready | **Amber: useful but narrower than claimed** |
| Result 2: coupled κ(t) / Fig. 4 | Ready | **Red: based on superseded formulation** |
| Result 3: N-tube instability | Ready | **Red/amber: exploratory only** |
| Registry/Methods | Ready | **Amber: strong architecture, incomplete scientific specification** |
| Figures | Not started | **Do not start publication figures until analyses are corrected** |
| Submission readiness | Implied near-ready | **Not ready** |

---

## 1. Submission-blocking issue: the Schmieder “cup-mass” target is dimensionally invalid

This is the most consequential finding in the review.

The repository function `_schmieder_mass_vs_grind()` reads `target_flow_ml_s`, `grind_level`, and `mass_in_cup`, and then averages every qualifying `mass_in_cup` value within each flow–grind group. It does **not** filter or group by:

- component,
- mass unit,
- brew ratio,
- temperature,
- or experimental role.

The resulting values are then treated as one cup-mass response and fed directly into the P3 gate. ([source code](https://raw.githubusercontent.com/trbrewer/puckworks/main/puckworks/harness.py))

That aggregation is not scientifically meaningful. The Schmieder dataset contains separate cup masses for trigonelline, caffeine, 5-CQA, and TDS, each at three brew ratios. The named compounds are measured in **mg**, while TDS is expressed in **g**. The source’s response surfaces are fitted separately for every component × brew-ratio combination, with flow, grind, and temperature as distinct predictors. ([dataset card](https://raw.githubusercontent.com/trbrewer/puckworks/main/docs/cards/schmieder2023.md))

Applying the current repository aggregation to the current CSV exactly reproduces the documented low-flow sequence:

- 96.786
- 97.684
- 96.546

But these numbers are an arithmetic average of unlike quantities: mg-valued solute masses and g-valued TDS masses, across different beverage masses and components. They have **no coherent unit**. Consequently, the outline’s description of a “~1 g/97 g” peak is incorrect: 97 is neither beverage mass nor a valid component mass. The P3 document records the same mixed aggregate as the supposedly real experimental target. ([P3 hypotheses](https://raw.githubusercontent.com/trbrewer/puckworks/main/docs/P3_hypotheses.md))

### The underlying response is also not species-independent

As an illustrative check, I separated the low-flow data by observable and brew ratio. The following is for brew ratio 1/2 and uses the same raw grouping logic; it is **not yet a corrected fixed-temperature analysis**:

| Observable | Unit | GL 1.4 | GL 1.7 | GL 2.0 | Raw shape |
|---|---:|---:|---:|---:|---|
| TDS mass | g | 4.008 | 4.096 | 3.917 | Interior maximum |
| Trigonelline | mg | 98.74 | 102.10 | 101.31 | Interior maximum |
| Caffeine | mg | 186.51 | 184.60 | 180.35 | Monotone decrease |
| 5-CQA | mg | 120.21 | 122.73 | 122.99 | Monotone increase |

Thus, even before controlling temperature, there is no universal “cup-mass shape.” The grind response depends on which observable is being discussed.

The raw grouping also combines temperature conditions. For example, in the low-flow data the endpoint grind levels pool 80 °C and 98 °C observations, while the central grind is represented at 89 °C. Because the source explicitly models temperature alongside grind and flow, direct averaging does not isolate a grind effect. The Schmieder card also reports weak RSM predictive quality and a mean cup-mass RSD of 2.5%, so peak prominence and uncertainty must be quantified rather than inferred from an argmax. ([dataset card](https://raw.githubusercontent.com/trbrewer/puckworks/main/docs/cards/schmieder2023.md))

### Consequence for Result 1

The current `gate_p3_schmieder_peak_discrimination` can pass while testing an invalid target. Its passing establishes software reproducibility of the aggregation, not scientific validity of the target. The statements below therefore cannot presently stand:

- “the Schmieder peak is real,”
- “only channeling reproduces it physically,”
- “the fine-grind dip is a channeling phenomenon,”
- “Result 1 is ready.”

This does **not** establish that the channeling hypothesis is wrong. It establishes that the current gate cannot adjudicate it.

### Required correction

The analysis should be rebuilt around one clearly defined observable. The most natural target for comparison with an extraction-yield model is either:

1. TDS-derived EY at one brew ratio, or
2. each solute mass separately, with a matching solute-specific model prediction.

For each target, the analysis should:

- hold brew ratio and temperature fixed, or use the published response-surface model to estimate the grind response at common flow and temperature;
- retain replicate-level uncertainty;
- test peak prominence and confidence, not merely whether the numerical argmax is interior;
- compare both **shape and effect magnitude**;
- state which observable supports or does not support a fine-grind maximum;
- add a data-schema gate that forbids averaging across mixed units, components, or brew ratios.

The repository’s “no silent constant merge” principle should be extended to a **no silent observable merge** rule.

---

## 2. Publication architecture

### Paper A should remain separate and should be finished first

The Paper A split is well justified. Its core result is conceptually clean: single-grind whole-cup data leave inventory and rate non-identifiable, cross-grind transfer fails, and fraction-resolved observations recover rate information. The repository analysis distinguishes same-grind post-fit performance from held-out cross-grind failure and includes a positive control showing that temporal fractions sharpen the rate objective. That is a coherent paper with a clear methodological lesson. ([transfer analysis](https://raw.githubusercontent.com/trbrewer/puckworks/main/docs/ANALYSIS_transfer.md))

I would still call Paper A **amber–green rather than nearly finished**, because an analysis write-up is not yet a manuscript. It needs a proper Methods section, uncertainty treatment, related work, figures, a pinned software revision, and a journal-specific narrative. But its central evidentiary chain is much stronger than Paper B’s.

### Paper B currently joins three different phenomena

Paper B combines:

1. a cross-study, grind-dependent extraction response;
2. a time-dependent flow trace at a fixed grind and pressure;
3. an exploratory synthetic multi-tube instability.

These are related through a proposed mechanism hierarchy, but they are not yet a demonstrated causal chain. In particular:

- Result 1 uses a **static heterogeneity ensemble**;
- Result 2 concerns **whole-bed temporal porosity evolution**;
- Result 3 creates a new dynamic coupling that has not been experimentally validated.

Calling all three “the fine-grind flow anomaly” conflates an **extraction-yield anomaly across grind** with a **flow-history anomaly over time**. Calling the result an “instability” also conflates the static mechanism in Result 1 with the numerical runaway introduced only in Result 3.

A combined Paper B remains possible, but its thesis should be “mechanism discrimination and model-hierarchy limits,” not “the anomaly is a channeling instability.” If Result 3 matures into a genuine stability analysis, it may be better as a separate applied-mathematics paper.

---

## 3. Title and abstract claims

### Current title

> “The fine-grind flow anomaly is a channeling instability”

This is too strong in three ways:

1. The primary empirical target is an extraction/cup-composition response, not simply a flow anomaly.
2. The static channeling model is shown only to be capable of generating an interior maximum under an empirical closure.
3. No physical instability has yet been established analytically or experimentally.

A safer working title is:

> **Mechanism discrimination for the fine-grind espresso extraction anomaly and a stability test of uncoupled streamtube models**

A more compact alternative is:

> **Testing mechanisms for the fine-grind espresso anomaly: static heterogeneity and dynamic streamtube instability**

The latter should be used only after explicitly qualifying “instability” as a model result.

### Current abstract

The abstract presently stacks three different evidentiary levels as though they were equally established:

- qualitative shape generation,
- post-fit reconstruction on one rig,
- exploratory numerical synthesis.

The repository’s own validation vocabulary distinguishes these levels and should control the verbs used. ([roadmap](https://raw.githubusercontent.com/trbrewer/puckworks/main/docs/ROADMAP.md))

| Evidence level | Appropriate language |
|---|---|
| Independent observation | “shows,” “measures,” “predicts held-out data” |
| Post-fit reconstruction | “reconstructs,” “is consistent with” |
| Qualitative discrimination | “can generate,” “does not generate under the tested parameterization” |
| Exploratory synthesis | “exhibits in the tested configuration,” “motivates” |
| Not supported here | “identifies,” “proves,” “is the mechanism,” “unconditionally” |

The abstract should therefore avoid:

- “only static channeling reproduces [the experimental anomaly]” until the target is corrected;
- “time-dependent bed mechanism is required” without specifying the tested null set and trace window;
- “unconditionally unstable”;
- “single channel” based solely on a top-decile metric;
- “lateral pressure equalization” for what is currently a numerical mixing regularizer.

---

## 4. Result 1: static channeling discrimination

### What the repository does support

The static streamtube model has a clear mechanism: permeability heterogeneity is represented by a unit-mean lognormal distribution, and the model’s concave EY response causes heterogeneity to reduce ensemble yield. A grind-dependent empirical σ closure can therefore convert a monotone homogeneous response into a peaked ensemble response. ([streamtube model](https://raw.githubusercontent.com/trbrewer/puckworks/main/puckworks/models/brewer2026/streamtube.py))

That is a useful **model-capacity result**:

> A calibrated static-heterogeneity model can generate an interior extraction maximum.

It is not yet a causal identification result.

### “Physical parameters” is not an appropriate binary label

The `brewer2026.streamtube` registry entry explicitly says that σ(φ₁) is an **empirical closure**, calibrated over a limited dial range and not externally validated. The component entry also has no component-level `gates=` assignment. ([model registry](https://raw.githubusercontent.com/trbrewer/puckworks/main/puckworks/models/__init__.py))

Thus, describing the channeling result as arising from “physical parameters” gives it a stronger status than the repository itself assigns. A fairer comparison is:

> Among the four currently instrumented response generators, the empirical static-heterogeneity closure generates an interior maximum without imposing the deliberately altered Lee saturation ceiling.

That still leaves several questions:

- Was σ calibrated to the same feature now being treated as a prediction?
- How much does peak formation depend on `s_ref`, exponent `m`, grid resolution, and pressure?
- Does the model reproduce the observed peak magnitude, rather than merely an argmax?
- Does the result persist over the uncertainty in fines fraction and σ?
- Is the effect robust for the corrected TDS/EY observable?

### The scoreboard is incomplete

The repository describes five hypotheses, but the gate compares only four entries: static channeling, Lee feedback, size-exclusion inventory, and a homogeneous/diffusion null. Incomplete wetting is not implemented, and Pannusch is described as a pointer rather than an independent mechanism. The gate itself is explicitly qualitative and shape-only. ([P3 hypotheses](https://raw.githubusercontent.com/trbrewer/puckworks/main/docs/P3_hypotheses.md))

Figure 2 should therefore not be a binary “winner” scoreboard. It should include columns such as:

| Mechanism | Implemented? | Observable matched? | Parameters independently constrained? | Generates peak? | Evidence strength |
|---|---|---|---|---|---|
| Static heterogeneity | Yes | EY proxy | Empirical calibration | Yes | Qualitative |
| Incomplete wetting | No | First-drip delay proposed | — | Unknown | Open |
| Lee feedback | Yes | EY | Source + altered ceiling test | Only altered case | Negative/qualitative |
| Size-exclusion inventory | Yes | Inventory ceiling | Different observable | No | Qualitative |
| Homogeneous extraction | Yes | EY | Source model | No | Qualitative |
| Pannusch pointer | Not a standalone mechanism | — | — | — | Not tested |

### Recommended Result 1 wording

After the target is corrected, the strongest defensible wording would be:

> “Of the currently implemented response generators, the empirically calibrated static-heterogeneity model is the only one that produces an interior grind maximum under its registered parameterization. This establishes mechanism viability, not unique identification; incomplete wetting remains untested.”

---

## 5. Result 2: null-first κ(t) ladder

### The null-first design is one of the outline’s strongest features

The principle that a bed-side mechanism must beat a machine-only null is methodologically excellent. The repository also correctly notes that the Foster pump/headspace flow minimum is a **separate early-shot phenomenon**, not the same residual used for the saturated Waszkiewicz ladder. The ROADMAP classifies the Foster figure reconstruction as post-fit rather than independent validation. ([harness](https://raw.githubusercontent.com/trbrewer/puckworks/main/puckworks/harness.py))

The manuscript should therefore present this as:

> “Machine dynamics can independently create a dip-and-recovery signature, so that qualitative signature alone does not identify a bed mechanism.”

It should not visually or verbally imply that the Foster model was nested and rejected on the same Waszkiewicz 15–115 s trace.

### The 9-bar ladder is informative but narrower than stated

On the specified 9-bar window, the empirical Φ(t) model beats the two flat baselines by approximately 5.4×. However:

- the static κ(P) model being flat at fixed pressure is structurally inevitable;
- the empirical dissolution trajectory comes from the same apparatus;
- the Waszkiewicz card identifies soft circularity because dissolved mass is derived from TDS and flow measured on that rig;
- other time-dependent bed or machine mechanisms are not exhausted by these baselines. ([validation gates](https://raw.githubusercontent.com/trbrewer/puckworks/main/puckworks/validation/gates.py))

The correct conclusion is therefore:

> “Within the tested 9-bar saturated-flow ladder, a time-varying porosity trajectory is required to outperform the specified flat baselines, and the empirical dissolution-linked Φ(t) trajectory is sufficient. It is not uniquely identified.”

That is stronger scientifically than the less qualified “a time-dependent bed mechanism is required,” because it states exactly what was compared.

### Cross-pressure discrimination is already complete in the repository

The outline calls cross-pressure generalization a “would-be independent discriminator” and lists its completion as an open gap. That is stale. The repository already implements and gates the comparison, and its result is explicitly **regime-dependent**:

- empirical Φ(t) has the best mean away from the 9-bar home trace;
- RC-3b wins at low pressure;
- the static model wins in the middle-pressure range;
- there is no universal winner. ([validation gates](https://raw.githubusercontent.com/trbrewer/puckworks/main/puckworks/validation/gates.py))

This result should be promoted into the main text, because it is more scientifically interesting than a single winner.

It should not, however, be called fully independent validation. The equilibrium parameters \(P_c\) and \(Q_c\) were fitted using 60 brews spanning all 11 pressures, and the constants are explicitly rig-, coffee-, and grind-specific. The analysis is best described as **within-rig cross-pressure generalization**, partly out of sample with respect to the time-dependent 9-bar trace, not external validation. ([Waszkiewicz card](https://raw.githubusercontent.com/trbrewer/puckworks/main/docs/cards/waszkiewicz2025.md))

### “Poroelastic closure is required” needs scope

The repository supports the narrower statement that the near-choke poroelastic closure is needed to reproduce the observed large flow rise from the adopted small porosity change. Kozeny–Carman is too gentle for that specific reconstruction. The registered component explicitly labels this a framework-level result and warns against calling it a validated κ(t) law. ([model registry](https://raw.githubusercontent.com/trbrewer/puckworks/main/puckworks/models/__init__.py))

Use:

> “The tested 14× rise cannot be reconstructed from the adopted porosity trajectory using the auxiliary Kozeny–Carman relation; the near-choke poroelastic closure supplies the required sensitivity.”

Avoid a universal statement that Kozeny–Carman is physically invalid for espresso beds.

---

## 6. Result 2 / Figure 4: the outline uses a superseded coupling formulation

This is the second major technical problem.

The outline cites `gate_coupled_kappa_t` and proposes a non-monotone “swelling closes, then extraction opens” κ trajectory. That gate operates on an older multiplicative harness composition. The harness explicitly states that this construction is not a registered component and has no card. ([validation gates](https://raw.githubusercontent.com/trbrewer/puckworks/main/puckworks/validation/gates.py))

The repository now contains a registered shared-porosity synthesis that **replaces** the multiplicative approximation because the latter double-counts pore volume. In the current model, branches compose on one porosity state rather than multiplying independently evaluated factors. ([coupled κ(t) card](https://raw.githubusercontent.com/trbrewer/puckworks/main/docs/cards/brewer2026_coupled_kappa_t.md))

More importantly, the registered model’s current result is not the attractive non-monotone trajectory suggested by the outline:

- extraction-only reproduces the poroelastic rung;
- adding the swelling branch over-closes the bed;
- the composite residual rises to about 0.648 g/s;
- this is worse than the approximately 0.603 g/s flat null;
- the repository interprets this as a mis-scaled swelling branch, not a successful full coupling. ([model registry](https://raw.githubusercontent.com/trbrewer/puckworks/main/puckworks/models/__init__.py))

Therefore:

1. Figure 4 should **not** be generated from the old multiplicative harness.
2. The paper should report the shared-porosity composition’s negative result.
3. The old gate should either be removed from the manuscript path or clearly labeled historical/diagnostic.
4. The model card and code need synchronization: the card still says “proposed; implementation to follow,” while the model is already implemented and registered. ([coupled κ(t) card](https://raw.githubusercontent.com/trbrewer/puckworks/main/docs/cards/brewer2026_coupled_kappa_t.md))

A scientifically useful Figure 4 would show:

- extraction-only shared-porosity reconstruction;
- extraction + swelling composite;
- observed 9-bar trace;
- flat baseline;
- the resulting residual increase and porosity trajectory.

That turns the figure into an honest branch-compatibility test rather than an illustrative success plot.

---

## 7. Result 3: N-tube runaway

### What is genuinely interesting

The N-tube construction asks an important question: does assigning each heterogeneous streamtube its own extraction-driven conductance clock cause the heterogeneity to self-limit or amplify? The tested poroelastic configuration exhibits strong flow concentration, whereas the auxiliary Kozeny–Carman configuration remains bounded. That is a valuable exploratory finding and a sensible motivation for a physical lateral-coupling model. ([harness](https://github.com/trbrewer/puckworks/raw/refs/heads/main/puckworks/harness.py))

### “Unconditionally unstable” is unsupported

The gate tests a small set of configurations:

- one fine grind;
- one default heterogeneity closure;
- one pressure;
- \(N=200\);
- two time-step subdivisions;
- one Kozeny–Carman control;
- one large lateral regularization value.

There is no parameter sweep establishing instability for all admissible heterogeneity, pressure, flow, closure slope, clock, or tube count, and there is no linear or nonlinear stability proof. The correct phrase is:

> “The uncoupled model exhibits runaway flow concentration in the tested near-choke configuration.”

“Unconditional” should be reserved for a demonstrated stability criterion or theorem.

### “Single-channel latch” is not measured

The reported metric is the **top-decile flow share**. At \(N=200\), that metric sums the largest 20 tubes. A top-decile share approaching one shows concentration in the leading decile, not flow through one channel.

The model should additionally report:

- maximum single-tube share;
- effective number of active channels, such as \(1/\sum s_i^2\);
- Gini coefficient or entropy;
- spatial or ranked flow-share trajectories.

Until then, use “top-decile concentration” rather than “single-channel latch.”

### The “lateral pressure equalization” term is a numerical regularizer

The code implements:

\[
w_i \leftarrow (1-\lambda) w_i + \lambda,
\]

which blends each flow share toward the uniform value. This is a homogenizing regularizer; it is not derived from a transverse pressure equation, network conductance, or Darcy exchange between adjacent tubes. ([harness](https://github.com/trbrewer/puckworks/raw/refs/heads/main/puckworks/harness.py))

Showing that this regularizer suppresses runaway establishes:

> imposed homogenization can suppress the numerical positive feedback.

It does not yet establish:

> physical lateral pressure equalization is necessary and sufficient.

A physical upgrade should introduce neighboring-tube exchange through a shared pressure field or transverse conductance network and then derive the stability boundary in terms of lateral conductance versus axial near-choke sensitivity.

### The reported EY collapse has a pressure inconsistency

The dynamic conductance calculation defaults to 9 bar, but the final EY calculation constructs `EYResponse(..., p_bar=5.0)` explicitly. Thus the quoted 16% → 2.5% EY comparison combines a 9-bar dynamic flow calculation with a 5-bar extraction response. ([harness](https://github.com/trbrewer/puckworks/raw/refs/heads/main/puckworks/harness.py))

The exact EY-collapse numbers should not appear in a manuscript until this is corrected and rerun. This does not necessarily remove the flow-concentration result, but it invalidates the current quantitative EY consequence.

### Work needed before Result 3 can become a headline result

At minimum:

1. fix the 5-bar/9-bar inconsistency;
2. replace the uniform-mixing parameter with a physically derived lateral exchange model;
3. perform a linear stability analysis around the uniform-flow state;
4. produce a phase diagram over heterogeneity, pressure, closure sensitivity, flow versus pressure control, lateral conductance, tube count, and extraction clock;
5. test alternative extraction clocks and donor uncertainty;
6. use adaptive or systematically converged integration;
7. report single-tube and effective-channel metrics;
8. distinguish a model-instability result from an experimentally observed channeling instability.

Until then, Result 3 belongs in an exploratory section or appendix. It is not “ready, with only Figure 5 remaining.”

---

## 8. Methods and registry claims

### Strengths

The registry architecture is genuinely valuable:

- typed stage-state contracts;
- explicit assumptions and validity ranges;
- named component provenance;
- configuration rather than a monolithic merged model;
- an unusually disciplined validation-strength vocabulary. ([README](https://raw.githubusercontent.com/trbrewer/puckworks/main/README.md))

The distinction among independent validation, post-fit reconstruction, verification, and qualitative evidence is particularly strong and should remain visible in every results table and figure caption. ([roadmap](https://raw.githubusercontent.com/trbrewer/puckworks/main/docs/ROADMAP.md))

### “Each model has at least one gate to real data” is inaccurate

The registry permits components with empty gate lists. For example, `brewer2026.streamtube` is registered without a `gates=` field. Some other gates are mass-budget checks, model-to-model verification, or qualitative shape checks rather than real-data validation. ([model registry](https://raw.githubusercontent.com/trbrewer/puckworks/main/puckworks/models/__init__.py))

The manuscript should say:

> “Components carry provenance, assumptions, and validity ranges; where available, named gates record evidence ranging from numerical verification to independent experimental comparison.”

It should not claim universal real-data gating.

### A passing QUICK gate is not scientific validation

The test suite simply iterates through `QUICK` and asserts that each function returns `passed=True`. The QUICK collection includes qualitative P3 and N-tube gates as well as the older coupled-κ gate. This is useful regression testing, but it cannot convert a qualitative assertion into independent validation. ([test gates](https://raw.githubusercontent.com/trbrewer/puckworks/main/tests/test_gates.py))

The paper should explicitly separate:

- **software regression:** the code continues to return the recorded result;
- **numerical verification:** budgets, convergence, reductions;
- **post-fit reproduction:** source data reconstructed with fitted parameters;
- **scientific validation:** prediction against genuinely unused data;
- **mechanism discrimination:** competing predictions tested on a valid common observable.

### “Code is the spec” is not sufficient for a manuscript

The paper still needs:

- governing equations;
- preprocessing and filtering rules;
- observable definitions and units;
- parameter provenance;
- calibration versus evaluation splits;
- uncertainty propagation;
- inclusion/exclusion criteria;
- exact software environment;
- a pinned commit or archived release.

The mixed-unit Schmieder aggregation demonstrates why code alone cannot substitute for a written data contract.

---

## 9. Discussion and claimed practical interpretation

The strongest unifying idea in the outline is not “channeling is proved.” It is:

> Integrated observables can erase the structure needed to distinguish mechanisms.

That theme works well across the project:

- Paper A: whole-cup endpoints hide inventory–kinetics separation, while fractions restore it.
- Result 2: one pressure trace leaves several time-dependent mechanisms partially degenerate.
- Result 3: a model suggests that spatially resolved flow information would be more discriminating.

However, the per-tube observations in Result 3 are simulated rather than experimental. The Discussion should therefore say the model **motivates spatial observables**, not that per-tube data have already discriminated the mechanism.

The barista-facing conclusion should be weakened from:

> “the fine-grind dip is flow heterogeneity”

to:

> “static flow heterogeneity remains a viable candidate generator of the fine-grind response, pending a corrected observable analysis and direct spatial validation.”

Likewise, the distinction between flow-controlled and pressure-controlled instability should not be asserted until both control modes have actually been simulated or analyzed in the dynamic model.

The G-lat gap is well motivated, but “cross-pressure discrimination completion” should be removed from the open-gap list because the repository already contains a completed, regime-dependent comparison.

---

## 10. Revised figure plan

The current recommendation to render Figures 1–5 first should be reversed. The figures would presently harden invalid or superseded analyses into manuscript graphics.

### Figure 1 — corrected experimental target

Show one observable at a time, preferably TDS-derived EY:

- raw replicate points;
- fixed flow, brew ratio, and temperature;
- uncertainty intervals;
- peak prominence;
- separate panel for the normalized model response.

Do not overlay mixed-unit component masses with model EY.

### Figure 2 — mechanism evidence matrix

Replace the winner scoreboard with a matrix containing:

- implemented versus unimplemented;
- calibrated versus independently constrained;
- matched observable;
- predicted shape;
- evidence strength;
- unresolved discriminating experiment.

### Figure 3 — null-first ladder and cross-pressure outcome

Separate:

- the Foster early-shot machine-only demonstration;
- the Waszkiewicz saturated 9-bar ladder;
- a pressure-by-mechanism residual heat map.

Label the Foster result as post-fit/source-model reconstruction and the cross-pressure test as within-rig generalization.

### Figure 4 — shared-porosity composition diagnostic

Show the current registered formulation:

- extraction-only;
- extraction + swelling;
- observed trace;
- flat baseline;
- the failed composite residual.

This negative result is more informative than the superseded multiplicative non-monotone curve.

### Figure 5 — stability map rather than three illustrative curves

A publication-grade stability figure should contain:

- phase boundary versus lateral conductance and near-choke sensitivity;
- flow-control and pressure-control cases;
- effective number of channels or maximum channel share;
- convergence and tube-count checks;
- selected trajectories illustrating stable, concentrating, and regularized regimes.

---

## 11. Revised readiness audit

| Element | Revised status | Requirement before submission |
|---|---|---|
| Paper A core identifiability result | **Amber–green** | Convert analysis to manuscript; uncertainty, related work, reproducibility package |
| Paper B framing/title | **Red** | Separate extraction anomaly, flow-trace result, and model instability |
| Schmieder target | **Red / blocking** | Rebuild by component, unit, brew ratio, temperature, and uncertainty |
| Static-channeling result | **Red** | Rerun against corrected target; sensitivity and magnitude tests |
| P2 9-bar ladder | **Amber** | Narrow claim to tested nulls/window; expose same-rig circularity |
| Cross-pressure result | **Amber** | Report completed regime-dependent result; stop calling it pending or fully independent |
| Coupled κ(t) synthesis | **Red** | Retire old multiplicative figure; use shared-porosity implementation and report failed full composition |
| N-tube model | **Red/amber exploratory** | Fix pressure mismatch; physical lateral model; stability analysis and parameter sweep |
| Registry Methods | **Amber** | Correct universal gate claim; add observable/unit contracts; pin revision |
| Related work and novelty | **Red** | Complete before claiming no prior head-to-head comparison |
| Figures | **Red** | Generate only after corrected analyses |
| Overall Paper B | **Not submission-ready** | Substantial scientific reanalysis, not only prose and rendering |

---

## 12. Priority revision sequence

1. **Fix the Schmieder data adapter and invalidate the current P3 gate until corrected.** Add unit/component/brew-ratio assertions so the present aggregation cannot silently recur.

2. **Recompute Result 1** for a physically matched observable at fixed conditions, with replicate uncertainty and peak-prominence tests. Re-run parameter and closure sensitivity before choosing the title.

3. **Clean the coupled-κ lineage.** Reconcile the model card, registered implementation, old multiplicative harness, and QUICK gates. Figure 4 must use the shared-porosity model.

4. **Rewrite Result 2 around its actual evidence:** a useful 9-bar null ladder, soft circularity, and completed regime-dependent cross-pressure results.

5. **Repair and deepen Result 3:** fix pressure consistency, derive physical lateral coupling, and conduct stability and robustness analyses.

6. **Only then generate figures, write the abstract, and complete related work.** Pin the exact commit or archive a release used for every manuscript number.

The sentence “Results 1–3 need no further computation” should be deleted. Result 1 requires a full reanalysis; Result 2 requires recomputation or at least regenerated outputs from the current registered synthesis; and Result 3 requires both corrections and substantial new stability work.

---

## Recommended revised thesis

A defensible combined-paper thesis would be:

> “We use a registry-based, null-first hierarchy to test which model classes can generate the fine-grind espresso response and the time-dependent flow observed in separate experiments. After enforcing matched observables and validation-strength labels, static heterogeneity is assessed as a candidate explanation rather than uniquely identified, empirical time-dependent porosity is shown to outperform specified flat baselines with regime-dependent cross-pressure performance, and an exploratory uncoupled streamtube extension reveals a numerical flow-concentration failure that motivates physically derived lateral coupling.”

That framing preserves the project’s genuine contributions—transparent mechanism comparison, negative results, and model-limit discovery—without claiming more identification than the current evidence supports.

**Bottom line:** finish Paper A first. Treat Paper B as a promising research program and corrected analysis plan, not a manuscript requiring only figures and prose. The immediate next task is the Schmieder observable repair, because the present title, abstract, Result 1 verdict, and readiness assessment all depend on it.
