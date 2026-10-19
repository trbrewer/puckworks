# Independent technical review of Puckworks and Espresso Whole-Pull

**Presentation correction — 19 October 2026 UTC:** appendix prose now renders as prose; long reproduction payloads are expandable; the detailed census, crosswalks and source index use readable records. This is an editorial correction to the 18 October review, with no new scientific execution or changed verdict.

<a id="section-0"></a>

## 0. Identity and how to read this report



**Reviewer:** GPT-6 Astra Pro, ChatGPT workspace with Bash, Git and Python; three delegated reviewers for census/process, data/thresholds and EWP physics. **Review date:** 18 October 2026. **Execution:** FULL for read-only shell/Python review; no OpenFOAM execution. **Data access:** packaged public evidence and public aggregate results only; external collection not mounted; protected Angeloni targets off limits; no owner measurements registered in the supplied settings. Neither repository was edited, committed or pushed.

| Identity | Start | End |
|---|---|---|
| [PW](https://github.com/trbrewer/puckworks) main | `9dd456be7fd797b9cda0a2bbf50d1ac717d72835` | `9dd456be7fd797b9cda0a2bbf50d1ac717d72835` |
| [EWP](https://github.com/trbrewer/espresso-whole-pull) main | `4284e9460c8057053e95de7cfa2fb3590e68e9db` | `4284e9460c8057053e95de7cfa2fb3590e68e9db` |
| UTC time | `2026-10-18T22:06:06Z` | `2026-10-18T23:20:46Z` |

**Freshness [X]:** the final fetch found no intervening main integrations in either repository; all findings remain bound to the start commits. Tracked worktrees are unchanged. Appendix A.1 preserves the fetch/status receipt.

The attachment leaves owner settings and drafting SHAs unfilled. I used its defaults and reviewed current main; a delta from an unidentified drafting revision cannot be reconstructed. The activity census uses the fixed start time, with inclusive 30/60-day windows beginning `2026-09-18T22:06:06Z` and `2026-08-19T22:06:06Z`. **Effort used:** approximately 75 minutes elapsed through final refresh, with three parallel delegated audits; no reliable sum of agent-hours or per-phase labor was recorded. Environment: Linux 6.18.55 x86-64, glibc 2.39, Python 3.12.14. PW's isolated development environment resolved NumPy 2.5.4, SciPy 1.18.1 and pytest 9.1.1 within declared dependency bounds. EWP's isolated test environment used NumPy 1.26.4, SciPy 1.11.4 and jsonschema 4.23.0. These are review environments, not claims to reproduce every hosted CI platform.

Evidence tags apply to the associated claim: **[X]** executed/recomputed by the principal reviewer; **[R]** principal reviewer inspected the primary artifact; **[S]** summary or historical claim not independently reproduced; **[D+]** delegated work with load-bearing arithmetic/primary evidence rechecked; **[D−]** delegated work not rechecked; **[C]** displayed derivation; **[J]** reasoned judgment. A recomputation of public aggregate arithmetic does **not** imply access to private observations. Each finding states confidence and counter-evidence. Stable finding IDs are `F-O1-01`, etc.; recommendations are `R-01`, etc. Locators use `PW:path:Lfirst-Llast@9dd456b` or `EWP:path:Lfirst-Llast@4284e94`, expanded to full pinned commits in this header. Appendix E provides durable links. Commands and complete review scripts are embedded in Appendices A–B; no separate files are needed.

<a id="review-navigation"></a>

## Navigation

**Main review:** [Executive summary](#section-1) · [Objectives](#section-2) · [Methodology](#section-3) · [Assessment logic](#section-4) · [Development state](#section-5) · [Capabilities](#section-6) · [Experimental comparisons](#section-7) · [Earlier reviews](#section-8) · [Recommendations](#section-9) · [Owner decisions](#section-10) · [Limitations](#section-11) · [Second-reviewer handoff](#section-12).

**Evidence appendices:** [A — Commands and numerical evidence](#appendix-a) · [B — Frozen logic and reproduction archive](#appendix-b) · [C — Census and reconciliation](#appendix-c) · [D — Glossary](#appendix-d) · [E — Source links](#appendix-e).

**Direct appendix links:** [Frozen assessments](#appendix-b-1) · [13 complete scripts](#appendix-b-2) · [Census input JSON](#appendix-b-3) · [128 integration records](#appendix-c-3) · [Open work](#appendix-c-4) · [F1–F15 and R1–R15 crosswalks](#appendix-c-5).

Long reproduction payloads are in individually labelled expandable sections. Their complete contents remain in this Markdown file; a plain-text editor can also access them. Scientific conclusions, numerical values, source commits and original execution receipts are unchanged by this presentation correction.

<a id="section-1"></a>

## 1. Executive summary



**Verdict:** this is a productive, increasingly auditable research programme with useful conditional capabilities, but neither a validated whole-pull predictor nor evidence that hydraulics and beverage mass alone determine chemical delivery. The central negative physics conclusions survive review. Several negative task headlines, however, conceal narrower descriptive improvements that deserve explicit reporting.

The five most consequential findings are:

1. **Threshold correction is substantially sound but incomplete.** T02/T03 and the rheology, caffeine and 5-CQA addenda preserve historical contracts and distinguish decision resolution from usefulness. They do not justify blanket relaxation or adoption. The mass portion of T04 and several T06 gate-role repairs remain open. [X/R/D+; F-O3-03–08]
2. **The pressure limitation is structural for the examined poroelastic families.** P1 slightly improves mean-condition RMSE over the quadratic comparator, yet its high-pressure slope has the wrong sign. Both source curve families are monotone on their admitted domains. Rescaling cannot repair that behavior. [X/C; F-O3-02]
3. **The largest chemistry qualification is not a marginal near miss.** L12 improves primary 5-CQA RMSE but retains mean absolute shot bias A=0.254372 mg/g against A≤0.125 mg/g. Caffeine primary gains are positive against all three comparators; its temperature comparison against D0 reverses nominally. [X/R; F-O3-05–06]
4. **Whole-cup rate insensitivity does not establish local equilibrium.** Endpoint integration, finite inventory and parameter conditioning can hide kinetics. H1 remains unestablished for real espresso; a matched equilibrium-limit versus finite-rate fraction comparison is the useful next existing-data question. [R/C/J; F-O3-07]
5. **Science has advanced; current status maintenance has lagged.** PW has real numerical/model additions and EWP has new viscosity coupling. Integration counts do not establish excessive governance labor. Current-facing documents nevertheless retain merged-as-draft, old component-count and obsolete permission language. [X/R/D+; F-O1-01–03]

The five priority actions are: repair current status pointers using accepted merge evidence (R-01); finish the uncompleted mass part of T04 with the existing policy (R-02); extend the existing species-model question with the matched H1 comparison (R-03); screen a distinct pressure mechanism before another campaign (R-04); and finish T06 by aligning a few gate roles with existing stronger verification (R-05). These are continuations or narrow corrections, not new review ladders.

| Conclusion | Supporting findings | Strongest counter-evidence | Evidence that would overturn it |
|---|---|---|---|
| Whole-process predictive validity is not established | F-O2-01–04, F-O3-01–02 | Verified components, qualified R0, accurate conditional reconstructions | Independent controlled tests with frozen calibration, correct pressure/fraction responses and decision-relevant uncertainty |
| Preserve negative contracts while reporting limited gains | F-O3-03–06 | Some gains are stable under retained shot deletions and numerical allowances | A predeclared practical use where paired improvements survive adverse panels and meet its independent margin |
| Pressure rescaling is exhausted for these families | F-O3-02 | P1 has lower descriptive mean error; E2C is only partly evaluable | An admissible omitted term/domain that changes the derivative, plus qualified predictive evidence |
| H1 is unresolved, not established by endpoint behavior | F-O3-07 | Some whole-cup responses are weakly rate-sensitive | Matched observable-level evidence distinguishing equilibrium from finite-rate models under shared inputs |
| Governance should be targeted, with existing controls reused | F-O1-03 | Controls have caught real defects; source-size ratios are imperfect | Lane time records showing a different burden, or a concrete defect requiring a broader control |

<a id="section-2"></a>

## 2. Objectives and scope



I interpreted the owner's first concern as a question about **what a threshold is deciding**, not whether it can be made easier to pass. O1 covers operative implementations, recent development, blocks and status accuracy. O2 profiles capability for declared uses. O3 examines scored support, dependence, uncertainty, adverse comparisons and H1. O4 turns remaining questions into bounded actions without duplicating completed or active work.

Scientific claims in products and status documents are in scope. Outreach, aesthetics, publishing operations, routine release mechanics and dependency maintenance are otherwise excluded from technical judgment, although their integrations remain in the exhaustive census. No private collection census was rerun. Registered counts describe available metadata; they do not establish unobserved experiments. No protected target values, restricted source code or private rows are reproduced. Existing public aggregate scores can be discussed without reopening the underlying protected targets.

<a id="section-3"></a>

## 3. Methodology



I pinned normal full-history clones, read repository instructions for integrity/rights, identified the protected access policy before running model/data code, and froze an assessment logic document before primary-result audit. Each delegated reviewer froze its own independent view before opening the earlier syntheses. Reconciliation proceeded in parallel across scopes after those freezes; this is a documented deviation from a single globally sequential Phase 2/3 boundary. The attachment and supplied conversation context already disclosed results, so this was independent source checking, not a target-blind exercise.

The principal audit covered the registry, Guided Pull/Cameron equations and inventory, selected hydraulic and extraction gates, Grudeva 008/009, the decision-resolution policy, current-facing status and the load-bearing delegated calculations. Delegated audits covered EWP equations and retained pressure comparisons, the data register and mass/chemistry/rheology chains, and all recent main integrations. I reran the public aggregate scripts, pressure bootstrap/quadrature and census extraction and inspected their methods. The retained private shot-deletion vectors were not reconstructible here; statements about their extrema are explicitly retained-result evidence.

The purposive gate sample comprised Cameron conservation, extraction harness, temperature sensitivity, Foster CT, G10 bulk viscosity, Grudeva reduced verification, infiltration, LB channel, Pannusch closures/solver, Roman source MPE, and both Waszkiewicz fits. After excluding those, eight of 55 remaining registry gates and four of 11 remaining quick-only gates were sampled without replacement with `random.Random(20261018)` on sorted names. The selected names and complete frames are in Appendix C. I executed all 66 registry gates, plus the four sampled quick-only gates and the two purposive quick-only harnesses. The other sampled registry gates were therefore executed within the complete registry run, not counted as separate successes.

Four additional PW task bundles were drawn from 15 eligible tasks; four EWP bundles from 20. They supplement, rather than substitute for, the headline audit. Before result reads, the PW frame was corrected to exclude `generated`, a directory rather than a task; both frames/selections are preserved. A second delegated EWP sample was frozen but not executed after discovery of duplicate sampling. The census taxonomy was also amended before aggregate interpretation: its third bin now includes scientific analysis/comparison, split into retained-output-only, new scenario evaluation under unchanged equations, and source/data qualification. Otherwise fresh simulations under unchanged equations would be mislabeled as retained-output reanalysis.

**Execution [X/D+]:** all 66 registry gates passed, with the separate acknowledged exception preserved; all six additionally executed quick-only checks passed. PW's selected suite finished with **5,993 passed, 24 failed, 66 skipped and 762 deselected**. An unchanged-test rerun resolved 21 failures using an appropriate temporary-directory/process environment; three remain blocked by absent `/proc/pressure/memory` telemetry. EWP static verification passed **39/39**; its initial **1,635-test** suite had one failure and 23 errors, all belonging to the environment-affected groups whose narrow 42-test rerun passed. Neither original full-suite receipt is relabeled as a clean pass. EWP source-manifest, baseline-integrity and shell-syntax checks passed; none builds or runs OpenFOAM. Public reductions independently reproduced 312 later-task aggregate metrics, 286 early-MASS metrics plus 50 comparison components, all 32 rheology decisions, 27 synthetic policy cases, both pressure bootstrap panels and 21 closure quadratures. Detailed support and remaining limits are in Appendix A.

The audit does not assert every code path is correct. The sampled equation checks covered sign, domain, units, boundary treatment and parameter provenance; retained convergence evidence was evaluated separately from fresh execution. The original external review documents identified by hashes in the syntheses were not attached, so fidelity of each synthesis to its unavailable original cannot be verified. Appendix A records commands, exclusions, environmental repairs and the resulting limits.

<a id="section-4"></a>

## 4. Logic of assessment



The pre-audit rules were: preserve historical outcomes; never promote fitting or verification into independent physical validation; calculate discrepancies on the actual scoring support; report all predeclared comparators and adverse panels; retain missing uncertainty as missing; and recommend no experiment or successor without a named decision and duplicate check. These rules did not change after seeing results.

For a measured observable, use

$$E=S-D,\qquad u_{\mathrm{val}}=\sqrt{u_{\mathrm{num}}^2+u_{\mathrm{input}}^2+u_D^2}.$$

The square-root expression requires independence or an explicit covariance extension. These repositories often supply numerical differences, finite perturbations or figure-reading envelopes rather than standard uncertainties. I retain those as such. I do not add unrelated campaign scatter, treat absent instrument/input uncertainty as zero, or call a finite deletion envelope a confidence interval. Statistical distinguishability from zero is separate from acceptability for a practical use. This is consistent with the distinction between uncertainty and conformity requirements in [JCGM 106:2012](https://www.bipm.org/en/doi/10.59161/jcgm106-2012), and NASA's requirement to communicate uncertainty or its absence in [NASA-STD-7009B, §4.3](https://standards.nasa.gov/sites/default/files/standards/NASA/B/1/NASA-STD-7009B-Final-3-5-2024.pdf). These external sources frame judgment; they do not validate the espresso models.

Four separate statements accompany revisited results: **original contract**, **evidence resolution**, **usefulness for a named application**, and **adoption/authorization**. The accepted opt-in decision-resolution supplement implements this distinction; its point relation, contractual outcome and resolution are separate fields. A point contract may fail while a compatible interval overlaps the requirement. A finite sensitivity envelope can establish stability over named tested variants while a precision prerequisite remains failed. Neither automatically means empirical adequacy. [R/X] `PW:docs/governance/DECISION_RESOLUTION_POLICY.md:L31-L108@9dd456b`; `PW:puckworks/validation/decision_resolution.py:L21-L102@9dd456b`.

Maturity profiles are six ordinal judgments in the order **representation / physics / code verification / solution verification / physical validation / UQ-sensitivity**. Scores are 0 absent or unsupported, 1 partial, 2 systematic within a bounded declared use, and 3 sufficiently comprehensive and independently corroborated for that use. They are adapted from the six-element [Sandia PCMM report, SAND2007-5948](https://www.osti.gov/biblio/976951); no composite score is calculated. Different intended uses can legitimately receive different profiles for the same code. A zero in physical validation says nothing about whether numerical work is useful.

H1 was split prospectively into **H1a**, local chemical equilibration before exit; **H1b**, weak whole-cup response to extraction rate at fixed inventory/equilibrium law; and **H1c**, hydraulics plus collected mass sufficient for useful chemical predictions across conditions/species. H1b does not imply H1a or H1c. Support requires observable-level predictions under controlled common inputs; endpoint nonidentifiability alone is insufficient. Sign/domain derivations precede mechanism recommendations. Practical margins must come from a declared use independently of observed errors. Confidence concerns the stated bounded claim, not confidence in the entire programme.

<a id="section-5"></a>

## 5. Findings: O1 — state of development



### F-O1-01 — The scientific core advanced, although coupled predictive validity did not

**Claim and evidence [X/D+/J, High]:** PW has 28 components, 79 gate functions, 66 registry references and 13 quick-only functions. EWP has one 5,793-line solver-source area plus analysis/adapters; it is not a second 28-model registry. PW added the Foster post-saturation governing branch, Grudeva numerical implementations, conservative observation/state-set methods and further conditional-data comparisons. EWP's recent viscosity changes are genuine governing-physics changes; prescribed-pressure histories and radial-geometry compatibility expand numerical support. These are concrete developments, even though they do not establish full-pull prediction. Census scripts and all 128 integrations appear in Appendices B–C; primary declarations and paths determine classification rather than PR titles alone.

| Repository/window | Integrations | Merge / squash | Physics | Numerical | Scientific analysis | Assurance/governance | Docs/status | Product/UI |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| PW, 30 days | 54 | 33 / 21 | 1 | 15 | 31 | 2 | 4 | 1 |
| PW, 60 days | 65 | 44 / 21 | 1 | 15 | 37 | 5 | 4 | 3 |
| EWP, 30 days | 30 | 1 / 29 | 3 | 2 | 21 | 0 | 4 | 0 |
| EWP, 60 days | 63 | 34 / 29 | 4 | 5 | 46 | 2 | 6 | 0 |

Scientific-analysis subtypes retained/new/source are PW30 **6/23/2**, PW60 **6/24/7**, EWP30 **15/6/0**, EWP60 **18/21/7**. Fourteen EWP30 entries mirror already evaluated PW results. Cross-repository totals therefore overstate independent scientific work if interpreted without lineage. The two EWP integrations since 1 October are document links, but that shorter observation does not erase September physics changes. Mixed-purpose alternatives are retained for 15/20 PW and 16/20 EWP integrations in the 30/60-day windows; their marginal category ranges are in Appendix C and are not simultaneous confidence bounds.

**Counter-evidence:** numerical infrastructure, source reconstruction and empirical conditioning are not new governing mechanisms; many integrations carry large generated records. **Consequence:** assess progress by the question answered and reusable capability, not merge totals or the count of PASS tokens. The attachment's 54/30 “merges” are correct as integrations, but most recent EWP integrations are squash commits. **Related:** R-04, R-07.

### F-O1-02 — Current-facing status contains verified lifecycle and permission errors

**Claim and evidence [R/X/D+, High]:** current metadata still treats PW #318/#320 and several EWP result handoffs as draft/unmerged, despite their main ancestry. PW's current policy pointer says acceptance/merge is pending even though the owner explicitly accepted #335 on 15 October and it merged as `882584d110e1356091435ab8b002fb9abdd35ad6`. The [owner acceptance record](https://github.com/trbrewer/puckworks/pull/335#issuecomment-6192947145) makes the supplement prospectively available through case declarations; it does not authorize historical migration or production adoption. `PW:docs/CURRENT.md:L31-L35@9dd456b`; `PW:docs/status/current.json:L465-L497@9dd456b`; `EWP:docs/PROJECT_STATE.md:L3-L19@4284e94`.

PW's large current acceptance paragraph mixes an old 25-component claim and Grudeva rights-blocked language with a later permission statement; onboarding says no public-value deliverable is built although executable products exist. Those are presentational defects where historical text is being served as current state. `PW:docs/status/current.json:L131-L136@9dd456b`; `PW:docs/ONBOARDING.md:L104-L108@9dd456b`. A generator can faithfully reproduce stale inputs and still pass its consistency check.

**Counter-evidence:** dated receipts deliberately preserve pre-merge restrictions, and not every old line is wrong in historical context. **Consequence:** fix current pointers and add a concise dated reconciliation; preserve frozen receipts. Existing EWP #76 already provides the appropriate task. **Related:** R-01; T01/T03.

### F-O1-03 — Proportionality needs lane evidence, not a code-size verdict

**Claim and evidence [R/X/D+/J, Medium]:** controls caught real defects in Foster cached-oracle success handling, Pannusch joint-bound witnesses, and decision-helper role/basis accounting. The recent caffeine fallback-path correction reused unchanged reviewed science and bounded tests. These are examples of the existing SCI-GOV-001 principle working. Foster and caffeine include separate nonhuman reviews; Pannusch006 explicitly records an implementation-author self-review. None establishes independent human domain review or new experimental evidence. `PW:docs/analysis/model_foster2025_postsat_001/HANDOFF.md:L19-L48@9dd456b`; `PW:docs/analysis/model_pannusch2024_prefix_conditioned_006/REVIEW.md:L3-L7@9dd456b`; `PW:docs/analysis/val_case_caffeine_decision_resolution_001/FINAL_REVIEW_ADDENDUM.json` (pinned in Appendix E).

| Area | PW files / physical / nonblank LOC | EWP files / physical / nonblank LOC |
| --- | --- | --- |
| Models/solver | 55 / 10,305 / 9,055 | 7 / 5,793 / 5,583 |
| Analysis | 132 / 52,794 / 47,389 | 241 / 28,355 / 26,207 |
| Assurance/governance | 40 / 19,904 / 17,495 | 42 / 5,297 / 4,936 |
| Product/UI | 48 / 12,773 / 11,140 | 0 / 0 / 0 |
| Tests | 304 / 63,649 / 51,696 | 108 / 18,875 / 17,301 |
| Engineering tools | 102 / 26,869 / 23,518 | 64 / 15,557 / 14,223 |
| Other code | 66 / 20,055 / 17,646 | 42 / 9,653 / 8,765 |

The physical-line ratio (assurance + tests)/(models + analysis) is **1.324 PW / 0.708 EWP**; including all engineering tools raises it to **1.750 / 1.163**. These are transparent footprint screens, not labor estimates. Tests can directly verify physics, and analysis code contains assurance. No measured assurance/science time ratio is available. The historical approximately 4,800-line Paper 1 assurance layer guarding partly empty registries is already frozen by `PW:CLAUDE.md:L86-L109@9dd456b`; that documented overengineering should not be repeated or misrepresented as October's measured effort.

**Counter-evidence:** scientific PRs can conceal large governance burdens; low governance-primary counts do not prove efficiency. **Consequence:** apply the existing §11 circuit breakers to repeated unchanged-artifact review and correction scope; do not introduce a new framework or weaken controls protecting a real claim. Confidence is Medium because effort is unobserved. **Related:** R-07; T12. Authority: `PW:docs/governance/MINIMUM_NECESSARY_GOVERNANCE_STANDARD.md:L304-L316@9dd456b`.

### F-O1-04 — The important blocks have different causes and existing owners

**Claim and evidence [R/D+/J, High for recorded states]:** the pressure derivative is a structural limitation; chemical inventory authority and an unqualified response surrogate leave identifiability unresolved. Unavailable independent hydraulic holdouts are evidence blocks. Grudeva full-reference #333 has a saved-payload/integrity block. Pannusch #321's checked witness repair and archive-only closeout are complete on candidate `bd976d2d4b7fc516c005765befedf5911a89ab2e`; it awaits owner lifecycle disposition and any required current-base checks. Its historical prefix failure and transport cause remain unresolved. These distinct states were verified in the live PR bodies; another witness-repair campaign would duplicate work. The Stage F choice remains an owner decision, and home-lab planning is already open in EWP #117. Public aggregate results remain usable when private observations cannot be mounted here. Live issue/PR snapshots and defining locators are in Appendices A/C/E.

**Counter-evidence:** a procedural stop can protect against a substantive scientific misstatement; it is not automatically wasted process. **Consequence:** separate resolving a block from relaxing it. No solver run or successor is implicitly authorized by this review. **Related:** R-02–04, R-06–07.

<a id="section-6"></a>

## 6. Findings: O2 — maturity and capabilities



### F-O2-01 — The registry is an evidence catalogue, not 28 validated process models

**Claim and evidence [X/R, High]:** the registry run produced **66 PASS and one ACKNOWLEDGED_EXCEPTION** for a component without gates. Current component evidence metadata distributes as code verification 6, source-curve reproduction 7, post-fit reconstruction 5, qualitative capacity 5, sign/compatibility 3, within-campaign held-out 1 and exploratory synthesis 1; **zero** are tagged controlled independent. This is a census of registry labels, not proof that no independent measurements exist anywhere. `PW:puckworks/models/__init__.py:L486-L549@9dd456b`; `PW:puckworks/registry.py:L31-L40@9dd456b`.

**Counter-evidence:** held-condition predictions and useful code verification are substantial capabilities. Some gates deliberately preserve a negative scientific result. **Consequence:** retain both the evidence rung and intended use next to PASS. The public whole-process claim ceiling is appropriate; a single global “not validated” banner is insufficient to describe conditional usefulness. **Related:** R-01/R-05.

### F-O2-02 — Guided Pull conserves its model inventory but remains a source-qualified reconstruction

**Claim and evidence [R/X/C, High]:** Guided Pull executes one saturated, isothermal Cameron chain. Its axial liquid balance exchanges mass with diffusing spherical populations through the same surface flux,

$$G=k\,c_s(c_s-c_l)(c_{sat}-c_l),\qquad \beta=3\phi/a.$$

With concentrations in kg/m³ and `k` in m⁷ kg⁻² s⁻¹, `G` is kg m⁻² s⁻¹ and `βG` is a volumetric mass source. The prescribed flux is based on the source grinder/pressure interpolation, and the collection time is explicitly `M_out/(ρ_out A q)`. The requested beverage mass is thus an endpoint condition, not a prediction. A recipe temperature is recorded without a thermal equation. `PW:puckworks/models/cameron2020/extraction_bdf.py:L216-L239@9dd456b`, `PW:puckworks/models/cameron2020/extraction_bdf.py:L254-L354@9dd456b`; `PW:puckworks/product/_pull.py:L30-L110@9dd456b`.

The repaired off-knot geometry gives an independent inventory closure of −1.67×10⁻¹³ EY percentage points in my GS1.1, N20/M12 run. The operative initial inventory ceiling is **24.467473%**, not a universal 29.6%. Retaining printed Eq.25 produces **18.715912 mm** bed depth versus **22.625620 mm** under the ordinary bulk-density identity. That is a disclosed source/definition ambiguity; silently changing density, initial inventory or kinetic constants would create a new model. Existing `tests/test_cameron_inventory.py:L8-L40@9dd456b` checks off-knot geometry, independent shell-volume inventory and refinement behavior.

**Counter-evidence:** conservation is not agreement with Fig.5 or a mesh-independent recipe prediction. The local audit reports historical final-publisher RMSE **7.102391 EY pp** against the homogeneous curve and **6.480780 pp** against experimental means; these are different residuals, not recipe uncertainty bars. Their original digitization evidence is not retained here, so these values remain **[S]**, not fresh figure scores. `PW:docs/research/ESPRESSO_PROGRAMME_REVIEW_2026-10-01.md:L148-L157@9dd456b`. Current disclosure correctly calls source reproduction unresolved. **Consequence:** use the chain for traceable conditional sensitivity and model education, with its source limits; do not infer independent dose/grind/pressure optimization. **Related:** R-05.

### F-O2-03 — EWP's R0 and optional closures are bounded numerical capabilities

**Claim and evidence [R/D+/C/J, High for implemented mathematics; Medium for physical transfer]:** R0 is an idealized axisymmetric wedge with Darcy flow, a sharp filling front and finite-rate effective-solute transport. Its 9.011661 mm depth is derived from 20 g, assumed solid density 1,400 kg/m³ and porosity 0.4, not measured. There is no energy equation. Post-saturation transport pairs `∂t(φc)+∇·(u c)−∇·(φD∇c)=R` with `∂t M=−R`, where `R=kM max(1−c/Csat,0)` is capped by available inventory. M is mass per bed volume; c is mass per liquid volume. Paired sources have consistent mass units. Release suppression is not a universal discrete concentration bound. The roughly 41 g-at-30-s R0 endpoint is engineering calibration. `EWP:docs/MODEL_SPECIFICATION.md:L24-L144@4284e94`; `EWP:solver/espressoWholePullFoam/espressoWholePullFoam.C:L3213-L3317@4284e94`.

Prescribed flow requires a saturated static Darcy bed, uniform or axially layered; it excludes radial geometry, compaction, machine compliance and evolving permeability. Quasi-static compaction keeps mechanical porosity distinct from transport storage and solves no displacement/deforming mesh. The separate dissolution-indexed K option uses a prescribed dissolved-mass history, not evolved native inventory. Aggregate viscosity requires 90°C, density 965 kg/m³, saturation at time zero, static Darcy, and no indexed species/compaction/evolving K. Bulk mode supports constant-pressure uniform/axial cases; radial histories use local coupling. `EWP:solver/espressoWholePullFoam/espressoWholePullFoam.C:L749-L928@4284e94`, `EWP:solver/espressoWholePullFoam/espressoWholePullFoam.C:L2334-L2365@4284e94`, `EWP:solver/espressoWholePullFoam/espressoWholePullFoam.C:L2589-L2760@4284e94`.

EWP's deliberately retained runtime PW lock is `fc61c4670ec7bf801e40bb391aab16048b8da26b`, 456 commits/109 first-parent commits behind reviewed PW main. CI separately uses `a3428a4d4ad571ef3168a70e8a04620fca5d3520` with `2058d0e947ee9eb92c52d64f6165b810f1fb4732`; individual research consumers bind later producers. These are distinct authority roles, not an automatic integration defect. `EWP:dependencies/puckworks.lock.json:L1-L15@4284e94`; `EWP:.github/workflows/static-validation.yml:L43-L64@4284e94`.

**Counter-evidence:** conservation, analytic oracles and retained mesh/time/MPI studies support bounded numerical use. They do not qualify every option combination or physical transfer. No OpenFOAM trajectory ran here. **Consequence:** profile each supported use separately; retain R0's historical qualification without transferring it to all later modes. **Related:** F-O3-02/03; R-04/R-05.

### F-O2-04 — Grudeva numerical agreement and publication disagreement coexist

**Claim and evidence [X/R, High for retained arithmetic; Medium for causal interpretation]:** the 008 comparison covers P0/C0, P1/C0, P0/C1 and P1/C1. All 11 metric families and seven selected histories pass the frozen inter-implementation limits. Recomputing the stored witnesses gives a largest limit utilization of **0.215109**. This verifies arithmetic on retained maxima/witnesses; the complete external arrays were unavailable for a fresh maximum search. `PW:docs/analysis/model_grudeva2026_matched_comparison_008/RESULTS.json` and its protocol, pinned in Appendix E.

In 009, I recalculated **72 included** residuals among **124 rows**, with **52 exclusions**, and confirmed **17** same-direction shared primary failures retained under refinement. P0's maximum figure-3 concentration discrepancy is **+0.097062** against 0.015; front discrepancy **−0.013449** against 0.008; figure-4 arrival **+0.120850** against 0.025; concentration **+0.141397** against 0.015. The arrival reading bound is 0.010025, while refinement moves that event by orders of magnitude less than its discrepancy. That supports a resolved publication-reproduction mismatch for the declared event. It is not a complete validation uncertainty estimate. Horizontal reading uncertainty still needs propagation through steep concentration profiles before asserting all pointwise differences exceed full figure uncertainty. `PW:docs/analysis/model_grudeva2026_publication_reconciliation_009/RESULTS.json` (SHA-256 `b2895fe8bdf7b8b1e529a9830b036f18eff9100800331a0ae8953b9ae9d13862`).

**Counter-evidence:** agreement between independently written implementations does not exclude a shared equation interpretation, missing source condition, or reference mismatch. “First selected failure at dimensionless time 3.2” is not the first physical failure time. The quick Grudeva gate executes analytic and coupled verification; it does not load a saved PASS. **Consequence:** retain both numerical qualification and publication non-reconciliation, without diagnosing author error. Do not duplicate the already open full-reference 010 PR #333. **Related:** R-06; T07.

### Capability matrix and maturity profiles

Every profile is **[J]**, conditioned on its stated use. Brief score justifications follow the six numbers; source evidence and confidence are inherited from the cited findings and artifacts.

| Capability | Components/files and locator | Claimed use | Defensible use today | Evidence rung | Six-axis profile and reasons | Key limitation |
| --- | --- | --- | --- | --- | --- | --- |
| PW Cameron / Guided Pull | `PW:puckworks/product/_pull.py:L30-L110@9dd456b` | Recipe exploration | Conditional source-model sensitivity | Code verification; source reproduction unresolved | 1/1/2/1/0/1; 1D/isothermal; source closure; independent inventory; limited refinement; no independent validation; scenario sensitivity | Prescribed endpoint, calibrated flux and source ambiguities |
| PW Pannusch kinetics / histories | `PW:docs/cards/pannusch2024.md:L22-L60@9dd456b` | Temperature/flow/species delivery | Source reconstruction and qualified prescribed-history numerics | Post-fit reconstruction | 1/1/2/1/0/1; 1D; fitted h/K; conservation/identity; bounded history qualification; exposed targets; limited sensitivity | No native thermal/hydraulic prediction; flow convention unresolved |
| PW Grudeva reduced | `PW:docs/analysis/model_grudeva2026_matched_comparison_008/RESULTS.md:L1-L148@9dd456b` | Reference-model solution | Analytic/bed verification and matched-code comparison | Code/solution verification | 1/1/2/2/0/1; reduced geometry; specified source PDE; analytic oracles; bounded refinement; no experiment; input/source limits | Publication mismatch and #333 incomplete full reference |
| PW Foster machine/front | `PW:docs/analysis/model_foster2025_postsat_001/RESULTS.md:L1-L61@9dd456b` | Machine/wetting reconstruction | Source ODE port including post-saturation | Source-curve reproduction | 1/1/2/1/0/1; ideal geometry; lumped source laws; independent oracle; bounded solve; fitted CT; source sensitivity | Fitted κ/front support, no new campaign |
| PW hydraulic/material components | `PW:puckworks/validation/gates.py:L9-L78@9dd456b` | Permeability/flow laws | Analytic LB; source-law/adapter reproduction | Verification/reproduction | 1/1/2/1/0/1; idealized representation; conditioned constitutive laws; analytic check; limited numerical study; no transferable K validation; input sensitivity | Aggregate collapse and in-rig fitting are not independent transfer |
| PW empirical mass/chemistry | `PW:docs/analysis/sci_md_mass_delivery_006/RESULT.md:L11-L83@9dd456b` | Conditional later fractions | Measured-mass/early-assay prediction on declared support | Retrospective grouped prediction | 1/1/2/2/1/1; aggregate map; phenomenological; integration oracles; bounded intervals; exposed held conditions; finite influence | Validation 1 means partial within-source prediction, not independent campaign |
| PW streamtube | `PW:puckworks/models/__init__.py:L497-L498@9dd456b` | Heterogeneity/discrimination | Within-campaign held-out response | Within-campaign held-out | 1/1/1/1/1/1; ideal channels; candidate mechanisms; partial code/refinement evidence; within-campaign validation; sweeps | No independent campaign or unique mechanism identification |
| PW packing generator | `PW:puckworks/models/__init__.py:L497-L498@9dd456b` | Synthetic packing/flow capacity | Exploratory mechanism capacity | Qualitative capacity | 1/1/1/1/0/1; ideal packing; candidate flow law; partial code/refinement evidence; no physical validation; sweeps | No empirical-validation claim or unique mechanism identification |
| EWP R0 whole pull | `EWP:docs/MODEL_SPECIFICATION.md:L24-L144@4284e94` | Idealized whole pull | Calibrated reference and numerical benchmark | Numerically qualified | 1/1/2/2/0/1; wedge; simplified wetting/solute; analytic/conservation; bounded mesh/time; no independent validation; assumed-input sweeps | No validation transfer to added modes |
| EWP Darcy/Forchheimer + machine | `EWP:solver/espressoWholePullFoam/espressoWholePullFoam.C:L2834-L2846@4284e94`; `EWP:solver/espressoWholePullFoam/forchheimerResistance.H:L10-L64@4284e94`; `EWP:solver/espressoWholePullFoam/machineBoundaryModel.H:L291-L365@4284e94` | Hydraulic components | Declared static/layered component problems | Code/solution verification | 2/1/2/2/0/1; supported geometries; source correlations; analytic reference; component refinement; no physical holdout; sensitivity | Source-specific machine/input mapping |
| EWP uniform compaction | `EWP:solver/espressoWholePullFoam/poroelasticCompaction.H:L10-L150@4284e94` | Stress-dependent K | Bounded scalar/component mechanics | Code/solution verification | 1/1/2/2/0/1; fixed domain; no displacement; oracle; bounded nonlinear/refinement; wrong pressure response; sensitivity | Cannot generate turnover at fixed admissible parameters |
| EWP local/bulk/radial rheology | `EWP:solver/espressoWholePullFoam/espressoWholePullFoam.C:L749-L790@4284e94` | Concentration–mobility coupling | 90°C saturated static-Darcy studies | Computational approximation | 2/1/2/2/0/1; declared radial geometry; industrial source law; conservative/oracle tests; refinements; no shot-law validation; tested properties | Bulk and local compatibility differ; unscored tails/spatial cuts |
| EWP indexed species | `EWP:solver/espressoWholePullFoam/espressoWholePullFoam.C:L3328-L3369@4284e94` | Species delivery under flow | Passive species operator studies | Code verification | 1/1/2/1/0/1; fixed geometry; first-order effective laws; paired balances; empirical-use qualification blocked; no chemistry validation; limited sensitivity | MD008 inventory and MD009 surrogate limits |

<a id="section-7"></a>

## 7. Findings: O3 — experimental comparisons, thresholds and H1



### F-O3-01 — Data volume is substantial; independent information is the limiting quantity

**Claim and evidence [X/R/D+, High for register counts; Medium for unmounted holdings]:** there are **118 manifest rows and 46 family entries**, 43 marked packaged. Aliases and shared campaigns prevent interpreting these as 46 independent experiments. The external snapshot records 31,503 files, 17,859 unique contents and 4,482,119,523 bytes, but explicitly no corpus-wide observation total. These external counts were read from metadata, not rescanned. `PW:puckworks/data/LOCAL_CORPUS_SNAPSHOT.json:L22-L109@9dd456b`; `PW:docs/data/ESPRESSO_DATA_GUIDE.md:L156-L201@9dd456b`.

The protected Angeloni family still has empty `blocked_uses` and unknown target exposure in general discovery metadata, despite the explicit deny policy. Pannusch aliases also fail to consistently inherit exposure. This is a routing/documentation inconsistency; no protected-target leak was observed. Resolve it from existing policy and receipts, without reading values. `PW:puckworks/data/AVAILABLE_DATA_REGISTER.json:L72-L136@9dd456b`, `PW:puckworks/data/AVAILABLE_DATA_REGISTER.json:L1939-L2086@9dd456b`, `PW:puckworks/data/AVAILABLE_DATA_REGISTER.json:L2568-L2629@9dd456b`; `PW:docs/analysis/sci_md_004_stage_e0/target_access_policy.json:L3-L35@9dd456b`.

**Counter-evidence:** exposed data remain useful for model criticism, conditional prediction and observation-operator work. Unavailable private files are not absent files. **Consequence:** identify the next missing observable/independent unit or calibration join; do not commission a general corpus sweep or home experiment from file counts. **Related:** R-01/R-03/R-04; T11.

#### Evidence map

Rights below report repository provenance; they do not grant additional redistribution permission. Known independent units are kept separate from plotted samples, records and derivative observations. Detailed source locators and unresolved unit counts are in Appendix E.

| Family | Observables | Independent units / counted records | Location | Uncertainty | Rights | Consumed/exposed by | Unused potential |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Pannusch/Schmieder | Mass-window TDS/caffeine/trigonelline/5-CQA | 45 FIT +24 PRED shots; one campaign lineage | Public subsets/aggregates; originals external | Between-shot SD; incomplete assay/input propagation | CC-BY-NC-3.0 source data; paper separate | Fitting, model selection and repeated scoring | Matched fraction comparisons; no fresh holdout |
| Waszkiewicz | Pressure, mass, differentiated flow | 56 brews /11 pressures; one label alias | Packaged processed traces | Repeated-brew spread; SEM; pressure/systematic uncertainty incomplete | CC-BY-4.0 data; source code license separate | Static/dynamic fits; MD010–012 | Sensor/observable-qualified pressure critique |
| Grudeva experiments | Mass/vial solute | 13 qualified shots;11 transfer eligible;208 clock vials | Public aggregates; permissioned originals external | Heterogeneous shots; no same-condition assay-repeat estimate | Written permission,14Aug2026; no new redistribution | CLOCK/MASS007/008/stopping | Cross-source conditional use; no fresh cohort |
| Angeloni | 11 species, solids/lipids metadata | 66 shots per metadata | Protected; metadata only here | Not inspected | Deny policy controls | Prior use/protection; general metadata inconsistent | No semantic use under this review |
| Wadsworth | PSD, porosity, K | 22 table rows;21 usable K; aliases deduplicated | Packaged | Source/adapter uncertainty varies | CC-BY-4.0 | Closure and prior comparisons | Input-adapter sensitivity, not universal wet-puck K |
| Roman / Vaca | Tamped K, porosity, extraction | Roman triplicate summaries; Vaca9 conditions/50 dry pairs; no common shot total | Packaged tables/thesis extracts | Source SD and geometry qualifications | Roman2015 CC-BY-3.0; thesis/source-specific | Source-law, material and prior tests | Source-specific priors; avoid unmatched row fusion |
| Foster | CT front/headspace; machine response | Independent shot count unknown | Digitizations/derived fixtures | Source error bars plus reading allowances | Source-specific; no new grant inferred | Fitted ODE/CT reproduction | Wetting/observation constraints, no chemistry join |
| Maillé / Smrke | Batch/fraction extraction | Maillé21 materials/105 normalized cells; Smrke33 primary markers, shot IDs unresolved | Packaged summaries; raw replicates absent here | Normalization/marker dependence unresolved | Thesis/article-specific; SmrkeCC-BY-4.0 | Transfer/capacity tests | Observer-denominator qualification; do not count cells as shots |
| Khamitova / Liang | Composition versus settings; partition | 9×4 source settings /~42 digitized points; no qualified independent-unit total | Packaged summaries | HPLC means/RSD or missing point error | Source-specific | Published/calibrated source relations | Composition/partition constraints with original units |
| Moroney | Drip bed/outlet concentrations | 44 deep/28 shallow observations, not independent shots | Digitized source curves | Shared cumulative/fit dependence | Source-specific | Deep calibration and shallow transfer | Observation/model criticism; not espresso validation |
| PocketScience / Visualizer | Radial recovery / machine histories | 60 experimental rows /23,169 archive record identities; units not all independent | Permissioned external originals; public aggregates | Handling/observer limits; uncontrolled corpus; user TDS/EY unverified | Permission scope; no raw redistribution | Radial observer and prior empirical/native corpus studies | Specific missing joins/metadata; no broad repeat sweep |
| Rheology properties | μ, K,n, thermal properties | Property table cells; no matched espresso-shot count | Packaged/derived source tables | Source/domain spread, not a universal probability model | Per-table provenance | G10 and rheology coupling/reductions | Constitutive sensitivity; no fresh-shot law validation |

Sources: [R/D+] `PW:docs/data/ESPRESSO_DATA_GUIDE.md:L431-L954@9dd456b`; family routing in AVAILABLE_DATA_REGISTER; current task-specific counts supersede older family summaries. Unrecomputed obscure source counts are [D−]; none drives a new experiment or validation claim.

### F-O3-02 — The pressure failure survives both arithmetic and admissibility checks

**Claim and evidence [X/R/C, High within the stated family]:** SCI-MD-010/011 use 56 brews in 11 held-pressure-condition folds on `endpoint_100s` flow. I reproduced all complete per-brew errors, balanced metrics and both 2,000-draw paired bootstrap panels. Positive gain below is B1 loss minus candidate loss; losses are normalized by each fold's training response range.

| Arm | R, g/s | B, g/s | High-pressure slope, g/s/bar | Full paired normalized-loss gain interval (dimensionless) | Low-pressure normalized-loss gain interval (dimensionless) |
| --- | --- | --- | --- | --- | --- |
| B0 | 0.591602 | 0.000000 | 0.006551 | comparator | comparator |
| B1 | 0.293627 | -0.033784 | -0.340046 | comparator | comparator |
| E1 | 0.575656 | -0.159818 | 0.328534 | [-0.248759, -0.036163] | [-0.266933, 0.029735] |
| P1 | 0.274282 | 0.033585 | 0.016120 | [-0.040211, 0.062966] | [-0.082834, -0.003262] |
| E2C | full score unavailable | unavailable | incomplete | required comparisons unavailable | required comparisons unavailable |

E1 loses the full-domain ranking. P1's descriptive RMSE is lower, but its full-domain gain interval crosses zero and the low-pressure panel favors B1. E2C has only 50 predicted brews/10 conditions: no full score or required pairwise conclusion is available. B1 has the correct slope sign but substantially exaggerates the decline, so passing a sign test is insufficient. `EWP:docs/analysis/sci_md_010/BREW_RESULTS.csv`; `EWP:docs/analysis/sci_md_011/BREW_RESULTS.csv`; `EWP:scripts/sci_md_011_core.py:L183-L186@4284e94`.

For the native finite-porosity closure, with `X=ΔP/Pc`, `0≤X≤1`, `0<Φ<1` and positive `A,K0,μ,H,Pc`,

$$Q=\frac{AK_0P_c}{\mu H}\int_0^X\frac{(1-s)^3}{1-\Phi s}\,ds,
\qquad \frac{dQ}{d\Delta P}=\frac{AK_0}{\mu H}\frac{(1-X)^3}{1-\Phi X}\ge0.$$

The universal curve has derivative `4(1−X)³≥0`. If the source machine adapter is `Δp_m(q)=aq²+bq+c`, with positive a,b and nonnegative q, then `dq/dp_line=F′/[1+(2aq+b)F′]≥0`. Positive scale changes can produce saturation, not turnover. Independent quadrature matches 21 retained scalar-oracle values within 6.67×10⁻¹⁶. This is an analytic/source result, not an argument that every transient or differently fitted cross-fold sequence must be monotone. `EWP:solver/espressoWholePullFoam/poroelasticCompaction.H:L10-L150@4284e94`; [Waszkiewicz et al., source equations](https://arxiv.org/html/2512.21528v2).

SCI-MD-012's separate coupled-endpoint representability failure is repairable algebraically: five of six high-pressure brews exceed the frozen coupled ceiling **12.721464 bar**, and raising Pc by **1.528675%** restores representability at fixed Qc within the admitted bounds. All evaluated closure inputs remain in their valid domain. The positive machine-pressure drop mitigates the representability failure. This is not a fitted rescue and does not change the derivative. The dissolution coordinate also **increases** with dissolved mass/dose; reversing its sign would misread the source. `EWP:docs/analysis/sci_md_012/ROOT_FEASIBILITY.csv`; `EWP:solver/espressoWholePullFoam/espressoWholePullFoam.C:L2334-L2365@4284e94`.

On the three high-pressure condition means, the observed slope is **−0.0655064 g/s/bar**. With fixed pressure coordinates and independent condition means, `w_i=(p_i−p̄)/Σ(p_j−p̄)²` gives `u_repeat(b)=sqrt(Σw_i²s_i²/n_i)=0.0137346 g/s/bar`. The repeat-only normal approximation is [−0.0924263,−0.0385865]. It omits pressure uncertainty, flow calibration, input/fitting uncertainty and covariance, so it is **not full u_val**. The reported bootstrap likewise resamples frozen predictions without refitting. **Counter-evidence:** useful descriptive ranking survives, but no independent campaign does. **Consequence:** retain E2C retirement for this decision; require a sign-admissible new premise before another physics campaign. **Related:** R-04; T08.

### F-O3-03 — The new policy separates decisions correctly; finite envelopes remain finite

**Claim and evidence [R/X, High]:** #335's accepted prospective helper and 27 executed synthetic cases maintain distinct relation, contract and resolution outputs. Its provenance is retrospective-informed, and the individual addenda disclose prior target knowledge. Git records distinct protocol commits before result commits for the mass, caffeine and 5-CQA addenda. Rheology's first retained protocol and result appear in the same commit, so Git alone cannot establish their internal ordering. Committed chronology does not establish unseen private execution timing. No new independent validation is created.

T05 is particularly informative. Independent re-reduction of all **32** RHEOLOGY010 rows reproduces every numerical term, sum and original decision. All 24 primary envelopes lie below their approximation budgets. All eight secondary envelopes lie above the materiality budgets, but two TDS contrasts remain ineligible under the original `u≤0.2b` precision condition: SW_UP has `M=4.729164`, `u=0.0200386`; TR_UP `M=4.167558`, `u=0.0246375`, against the 0.020 pp precision ceiling. Their finite lower endpoints, **4.709125** and **4.142921 pp**, remain far above the 0.10 pp contrast budget. This supports stability over those tested variants while preserving original UNRESOLVED labels. `PW:docs/analysis/val_case_rheology_decision_resolution_001/RESULTS.md:L102-L174@9dd456b`; `EWP:docs/analysis/sci_md_rheology_010/METRICS.json`.

**Counter-evidence:** additive temporal/axial/radial/property differences are not certified continuum error bounds or confidence intervals. Unscored tails and in-puck spatial cuts remain outside qualification. RHEOLOGY011 already provides the histogram-preserving arrangement control; another generic “separate arrangement” study would duplicate it. **Consequence:** credit completed T05 and preserve narrow E2 reduction usefulness. Do not replace its 0.10 pp numerical budget with an empirical 1 pp adequacy budget. **Related:** R-02/R-07; T03/T05.

### F-O3-04 — Mass-conditioned prediction has value, with adverse cases and conditioning costs

**Claim and evidence [X/R/D+, High for aggregate comparisons]:** MASS006 C2 passes its primary conditional prediction contract. Its primary R is **0.480034 pp**, versus C0 **0.652055**, C1 **0.597587** and legacy empirical **0.779601**. Inputs include early assays and supplied mass windows; this is neither assay-free nor hydraulic prediction. C2 loses C05 to C0/C1 and complete C08 to every comparator. MASS007 improves over C0/C1 across its 11 eligible Grudeva shots, yet has only **7/11** adequate shots against nine required. MASS008 adaptation is adequate under its calibration-choice rule but fails incremental-value conjunctions. Its **110 ordered pairs reuse 11 shots and 55 suffix observations**. [R] `PW:docs/analysis/sci_md_mass_uncertainty_001/RESULTS.md:L44-L82@9dd456b`; [X] aggregate scripts.

Public gains and aggregates were re-reduced; published deletion summaries and code were inspected, but private deletion vectors were not independently replayed for MASS, caffeine or 5-CQA. Deleting a MASS008 identity from both calibration and target roles leaves 90 dependent pairs, not 90 experiments. All retained improvement ranges cross the 0.10 pp material-gain floor for that task; this is sensitivity, not population reliability. Earlier MASS001–003 failures have multiple condition/bias/increment causes and require their own scored-support reanalysis. A small balanced-R near miss alone is not a useful-results verdict.

**Counter-evidence:** the completed stopping-decision task shows C2, C0 and the fixed rule all succeed on **11/11** primary shots. This is positive application-specific evidence but no incremental C2 decision value. All four declared sensitivity contracts and the fixed-rule abstentions remain in Appendix A. `PW:docs/analysis/sci_md_mass_stop_decision_001/RESULT.md:L3-L65@9dd456b`. **Consequence:** do not recommend another generic stopping-rule study. Finish only the uncompleted T04 mass questions. **Related:** R-02; T02/T04.

### F-O3-05 — Caffeine's descriptive gains are real but fail the declared complexity rule

**Claim and evidence [X/R, High]:** all D0/S0/S1/S2 primary arms are adequate under their research budgets. S2 R is **0.125168 mg/g** and gains against S1/D0/S0 are **0.027021 / 0.067090 / 0.090397 mg/g**. Every retained primary shot deletion has positive gain, but even the largest is below the required 0.10 mg/g. The S1 comparison also fails the original condition-win count. Thus “no earned complexity” is correct for that contract; “no gain” would be false. `PW:docs/analysis/sci_md_caffeine_delivery_001/PROTOCOL.md:L69-L83@9dd456b`; `PW:docs/analysis/val_case_caffeine_decision_resolution_001/RESULTS.md:L38-L155@9dd456b`.

**Counter-evidence:** temperature S2 versus D0 is **−0.004761 mg/g**, with retained deletions spanning −0.024466 to +0.009810; complete C08 also favors D0 strongly. Flow coverage is only 23/24 windows, so a favorable partial comparison cannot establish full-flow usefulness. D0 uses no TDS; S1 already uses early-TDS information indirectly through C2. **Consequence:** all comparators, query information and adverse panels must remain visible. Practical adoption needs a separate use/margin, not a threshold lowered to fit these gains. **Related:** R-02/R-03; T04.

### F-O3-06 — 5-CQA improvement does not remove its systematic discrepancy

**Claim and evidence [X/R/C, High]:** L12 primary R **0.297495 mg/g** improves on L1M **0.343708** and L2M **0.349468**, but its mean absolute shot bias is **A=0.254372 mg/g** (signed B=−0.254372), against **A≤0.125**. Every primary condition is inadequate. This is not explained by narrowly missing a relative-gain requirement. The addendum correctly preserves inadequacy and reports the improvements. `PW:docs/analysis/sci_md_5cqa_assay_002/RESULTS.md:L21-L78@9dd456b`; `PW:docs/analysis/val_case_5cqa_decision_resolution_001/RESULTS.md:L3-L133@9dd456b`.

For each weighted shot, `R²=B²+V`, so

$$R_r-R_c=\frac{B_r^2-B_c^2}{R_r+R_c}+\frac{V_r-V_c}{R_r+R_c}.$$

The terms are computed per shot before nested averaging. L12/L1M's **+0.046213** gain decomposes into **−0.023312** squared-mean-error and **+0.069525** centered-residual contributions; L12/L2M's **+0.051973** into **+0.012736 / +0.039236**. These are residual geometry, not assay-noise estimates or causal calibration offsets. I reproduced the aggregate gains and the contribution identities; private per-shot decomposition/deletion inputs were unavailable. `PW:puckworks/analysis/five_cqa_decision_resolution.py:L186-L249@9dd456b`, `PW:puckworks/analysis/five_cqa_decision_resolution.py:L263-L392@9dd456b`.

**Counter-evidence:** L12 gains persist through all retained primary deletions, but its temperature comparison with L1M changes sign. L2M versus L1M is nominally worse in primary and consistently worse in temperature. Extensive feature extrapolation is retained rather than excluded. Earlier FIT/PRED calibration-equation reconstruction already preserved the failure; repeating it would duplicate completed work. An assumed additive offset remains unsupported. **Consequence:** a causal bias investigation requires new assay/calibration/observer provenance, not reinterpretation of this identity. The positive trigonelline mass-shape result remains a counterexample to a blanket “all chemistry models fail” claim. **Related:** R-03/R-08; T09.

### F-O3-07 — H1 remains a model-regime hypothesis, not an established espresso mechanism

**Claim and evidence [R/C/J, High for logical non-implication; Medium for empirical scope]:** for initially solute-free liquid, `c(0)=0`, in a fixed reservoir with constant positive `c_eq` and constant positive `k` over residence time τ, `dc/dt=k(c_eq−c)` gives `c/c_eq=1−exp(−Da)`, `Da=kτ`, and logarithmic rate sensitivity `Da/(exp(Da)−1)`. Large Da would support local equilibration under those assumptions. A weak integrated endpoint sensitivity can instead arise from inventory exhaustion, supplied endpoint conditioning or parameter confounding; the converse inference is invalid. MASS006–008 and TDS-conditioned chemistry arms consume early chemical information; caffeine D0 and trigonelline TR-D0 are mass-only at inference. All depend on supplied measured mass windows, so none establishes predicted hydraulics. The chemical inputs in the conditioned arms also prevent using their success as evidence of hydraulics-only sufficiency.

The prompt's H1 locus is superseded through v2, v2.1 and v2.2. The manifest names **v2.2.1 as candidate**, with no frozen-content commit; its H1 explicitly leaves real-espresso regime occupancy untested. `PW:docs/paper1_resource/PAPER_A_PLAN_MANIFEST_V1.json:L3-L4@9dd456b`, `PW:docs/paper1_resource/PAPER_A_PLAN_MANIFEST_V1.json:L457-L457@9dd456b`; `PW:docs/paper1_resource/PAPER_1_PIVOT_AND_REDRAFT_PLAN_V2_2_1.md:L105-L117@9dd456b`. The current early/peak harness already says that statistic cannot identify equilibrium; no correction is needed there. `PW:puckworks/harness.py:L85-L102@9dd456b`.

EWP MD008 rejects its inventory-scale shape-invariance assumption in **24/36** retained metric rows, maximum **0.080114** versus 10⁻⁶, with zero pressure change. MD009 has **117/324** surrogate validation rows above 2%, maximum **8.25543%**, and no chemistry target score. Those are limitations of the implemented model/approximation, not proof of physical equilibrium or universal kinetic nonidentifiability. [X] `EWP:validation/sci_md_008/INVENTORY_SCALE_INVARIANCE.csv`; `EWP:validation/sci_md_009/NONLINEAR_RESPONSE_VALIDATION.csv`.

**Counter-evidence:** some whole-cup responses and measured-mass predictors are useful in bounded regimes. **Consequence:** compare an explicitly derived equilibrium limit with finite-rate release on eligible exposed fraction/species support under identical hydraulics, inventory and partition information. Preserve existing #104's frozen shared/species contract; obtain a distinct scope decision before adding this comparator. An unidentifiable or source-blocked comparison is an acceptable result. **Related:** R-03.

### F-O3-08 — A few gate roles need repair; simple or negative gates are not inherently defective

**Claim and evidence [R/X/J, High]:** Cameron's 0.5 pp single-GS conservation tolerance permits **0.1 g**, about **2.04%** of initial modeled inventory at 20 g dose. Known repaired off-knot discrepancies fit inside that tolerance, while the existing inventory tests are much stronger. The gate is too loose for a conservation regression but does not demonstrate a current conservation bug. Wadsworth's geometric-mean ratio **0.912698** passes despite individual ratios **0.654168–1.755360**, five of 21 outside ±30%; it tests mean log bias, not pointwise accuracy. `PW:puckworks/validation/gates.py:L17-L24@9dd456b`, `PW:puckworks/validation/gates.py:L363-L376@9dd456b`.

The infiltration gate uses fitted κ despite “parameter-free” wording. Foster CT admits `max(reported error,0.5 mm)` and 4/8 front points, which is not a majority and is not independent validation. G10's single-case small-viscosity effect cannot establish that no concentration-dependent viscosity hook is warranted everywhere. These require scoped interpretation, not blanket tolerance changes. Conversely, the Roman sphere analytical gate and active Grudeva verification are meaningful; the Roman MPE gate checks source-table transcription; Maillé/P3 negative controls correctly pass when an expected incompatibility remains. I found no evidence that the inspected Grudeva gate simply returns a stored success. **Counter-evidence:** stronger inventory tests and current registry evidence labels already limit several risks. **Consequence:** complete the narrow T06 repairs and reuse existing tests. **Related:** R-05.

#### Model–data comparison matrix

`R` is the task's own aggregation of RMSE; `B` is signed mean error; `A` is mean absolute shot bias. Generally `A≠abs(B)`. Reported “contract PASS/FAIL” below concerns the frozen numerical or empirical rule. Where measurement/input components are missing, physical-error resolution is unavailable even when contract arithmetic is definite. All arms, stress panels and relevant retained sensitivities for the revisited comparisons are tabulated in Appendix A; no incomplete E2C/flow aggregate is substituted for full support.

| ID | Model/capability | Observable/units | Data/units | Comparison type | Scored support | Metric | E or discrepancy | u_val/components | Resolution | Threshold/role/basis | Assessment | Exposure | Locator |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| M01 | Cameron | EY, pp | PublisherFig5; digitizations unavailable | Source reconstruction | Historical20g/40g/5bar | RMSE | 7.102391 curve;6.480780 means [S] | No complete u_val | Source mismatch unresolved causally | No adopted practical tolerance | Do not treat as recipe error bars | Exposed | `PW:docs/research/ESPRESSO_PROGRAMME_REVIEW_2026-10-01.md:L148-L157@9dd456b` |
| M02 | Wadsworth law + adapter | K ratio | Table1;21 rows | Source-law reproduction | All usable K rows | GM ratio; scatter | GM .912698; range .654–1.755 | Input/error covariance absent | Aggregate check PASS; physical NA | GM(.7,1.2), curve reproduction | Not pointwise adequacy | Source fitted | `PW:puckworks/validation/gates.py:L17-L24@9dd456b` |
| M03 | Waszkiewicz PW | Flow, g/s | Same rig11 pressures;9bar time trace | Fit/reconstruction | Static curve; t≥15s | Static parameters; corr/terminal | Pc12.392,Qc1.897; terminal1.886−1.856 | No complete u_val | Regression PASS; physical NA | corr>.9, terminal relative<.1 | Source role only | Same-rig fits | `PW:puckworks/validation/gates.py:L44-L78@9dd456b` |
| M04 | Foster | Front/headspace, mm | CT/fitted curves; shot n unknown | Post-fit | 8 front/8 headspace points | RMSE; coverage | Fitted RMSE .002/.001;4/8,5/8 | max(source error,.5mm), not u_val | Port PASS; independent NA | RMSE<.2mm,≥4 points | Coverage wording overstates | Fitted campaign | `PW:puckworks/validation/gates.py:L1170-L1195@9dd456b` |
| M05 | EWP010/011 all arms | Flow, g/s | Wasz 56 brews/11 conditions | Retrospective LOCO | endpoint100s; full/low pressure | Mean-condition R; paired gain | All arms in pressure table | Slope-only u_repeat=.013735 g/s/bar; RMSE/gain full u_val unavailable | E1 ranking loss; P1 unresolved gain; E2C incomplete | Paired ranking/sign, no adequacy margin | Preserve sign and adverse panel | Target exposed | `EWP:docs/analysis/sci_md_011/RESULT.md:L7-L26@4284e94` |
| M06 | EWP WP03 compaction | Flow/mass, g/s and g | Same 5/9/11 bar source | Source-conditioned native comparison | 270 temporal samples/pressure, not independent | RMSE, bias, ordering | Flow R .472/.517/.535; mass B +4.092/+8.584/+9.104 [R] | Source bands only; no full u_val | Wrong endpoint ordering; numerically qualified | Observable ranking/reproduction | Structural warning; not fresh validation | Calibrated/exposed | `EWP:docs/wp03/WP03_002_RESULTS.md:L50-L59@4284e94`; `EWP:validation/wp03/WP03_002_CORRECTED_COMPARISON.json:L1-L945@4284e94` |
| M07 | Grudeva008/009 | Dimensionless fields/events | Numerical references/publication | Code comparison / reproduction | 4pairs;72included figure residuals | Max errors versus limits | 008 maxutil .215109;009arrival+.120850 | Reading .010025 + small refinement, no full figure propagation | 008PASS;009 event mismatch | .001 field etc / .025 arrival | Different questions; preserve both | Public source | `PW:docs/analysis/model_grudeva2026_publication_reconciliation_009/RESULTS.md:L3-L25@9dd456b` |
| M08 | MASS001–003 all arms | TDS, pp | Shared campaign; declared PRED panels | Exposed predictive comparisons | Original conditions/windows | Nested R,B,A, gain | All values in A.5; anchored empirical passes003 | No complete assay/input u_val | Historical fails/mixed; no global near-miss verdict | R≤1,A≤.5;gain .1+20% | Research budgets; practical basis absent | Target exposed | `PW:docs/analysis/sci_md_mass_delivery_003/RESULT.md:L7-L59@9dd456b` |
| M09 | MASS004/005 | TDS, pp | Same source; incomplete/fixed-assay scope | Predictor adequacy | Original denominators; qualified lower witnesses | R/A bounds | 004C01lower1.603167/1.410845 [R] | Numerical only | Definite scoped failures; not all missing | 1/.5 research budgets | Do not drop missing denominators | Exposed | `PW:docs/analysis/sci_md_mass_delivery_004/RESULT.md:L75-L106@9dd456b` |
| M10 | MASS006–008 | TDS, pp | 12 primary Pannusch / 11 Grudeva reused | Conditional transfer/adaptation | Measured suffix mass; 110 dependent pairs in 008 | R, A, count rules | 006 C2 R .480034; 007 A .532635; 008 R .483158 | Numerical bounds + finite deletions; missing assay/input | 006 PASS; 007 FAIL; 008 adequate/no increment | R≤1, A≤.5; original condition/shot/calibration counts | Scoped utility, no population guarantee | Exposed; early assays | `PW:docs/analysis/sci_md_mass_uncertainty_001/RESULTS.md:L44-L82@9dd456b` |
| M10b | MASS stopping decision | Additional solute g; suffix TDS % | Same 11 Grudeva shots | Conditional decision comparison | Original feasible endpoints and sensitivity contracts | Success, false feasibility, abstention, regret | C2/C0/FIXED primary 11/11; all sensitivities in A.5 [R/X] | Public counts checked; private oracle/regret not replayed | All primary rules succeed; no incremental C2 value | Additional solute≥.100 g AND suffix TDS≥2.0%; decision-count limits | Application-specific, distinct from prediction budgets | Exposed; measured mass and conditioned predictors | `PW:docs/analysis/sci_md_mass_stop_decision_001/PROTOCOL.md:L45-L51@9dd456b`; `PW:docs/analysis/sci_md_mass_stop_decision_001/PROTOCOL.md:L136-L149@9dd456b` |
| M11 | Caffeine D0/S0/S1/S2 | mg/g | 12primary,6temperature,6flow shots | Conditional chemistry | 48/24/23of24windows | NestedR,B,A;pairedgain | S2R.125168;B−.056349 | Numerical + deletion sensitivity; no full u_val | All primary adequate; complexity FAIL | R≤.50,A≤.25;gain≥.10AND15% | No practical basis demonstrated | Exposed | `PW:docs/analysis/sci_md_caffeine_delivery_001/RESULT.md:L7-L43@9dd456b` |
| M12 | 5CQA delivery/TDS/assay arms | mg/g | Same PRED lineage | Conditional chemistry | Same original/partial supports | R,B,A;decomposed gains | L12R.297495;A.254372;B−.254372 | Numerical + finite sensitivity; no full u_val | All current primary arms inadequate | R≤.25,A≤.125;gain≥.05AND15% | Bias failure is substantial; no offset inference | Exposed/extrapolated | `PW:docs/analysis/sci_md_5cqa_assay_002/RESULTS.md:L21-L78@9dd456b` |
| M13 | Trigonelline K0/D0 | mg/g | Same12primary source shots | Mass-shape predictive comparison | Declared assayed windows | R,B;pairedgain | D0R.134550;B−.026655;gain.594953 | Computational allowances, no full u_val | Positive original mass-shape result | R≤.25,A≤.125;gain≥.05AND15% | Named conditional gain, not kinetics | Exposed | `PW:docs/analysis/sci_md_trigonelline_delivery_001/RESULT.md:L9-L52@9dd456b` |
| M14 | Grudeva CLOCK | Vial solute, g | 13 shots; 208 regular vials = 180 positive-mass chemistry + 26 structural zeros + 2 chemistry gaps | Grouped retrospective prediction | Measured masses; terminal excluded | Mean vial RMSE; adequate-shot count | MASS/MIXED .01653832 (11/13 each); TIME .04307544 (3/13); TEMPLATE .04408708 (2/13) [R] | Raw/covariance unavailable | Conditional mass benefit; MIXED no increment | Shot RMSE≤.05 g AND max cumulative error≤.20 g in≥10/13 shots | Actual conditional utility; not flow prediction | Exposed | `EWP:docs/analysis/sci_md_grudeva_clock_001/RESULT.md:L15-L78@4284e94`; `PW:docs/analysis/sci_md_grudeva_clock_001/PROTOCOL.md:L154-L164@9dd456b` |
| M15 | Rheology007–011 | TDS pp, allocation, flow fractions | Computational C reference; no shots | Approximation/arrangement | Declared finite-mass support/tails excluded | Max deviations + additive variants | 010: 24 PASS; 8 secondary above budget, 2 precision failures | Finite numerical envelope only | Approximation useful; spatial/tail limits | TDS .10 pp; shares 1/2 pp; flow/path .01/.02 fractions; u≤.2 budget | Appropriate distinct metric-specific roles | No empirical validation | `PW:docs/analysis/val_case_rheology_decision_resolution_001/RESULTS.md:L62-L174@9dd456b` |
| M16 | Maillé/Moroney/Smrke/Radial | Source-specific observables | Source families in evidence map | Transfer/observer qualification | Declared masks/calibration/normalization | Family-specific;see retained bundles | Observer unresolved / calibrationFAIL / negative gains / nonunique radial state | Source-dependent; no pooled u_val | Preserve distinct stopped/negative claims | Family contracts, no shared noise floor | No universal theory rejection | Exposed | `PW:docs/analysis/sci_md_smrke_transfer_001/RESULT.md:L1-L163@9dd456b` |

#### Threshold audit

Basis quotations are at most 15 words and describe the stated role, not an inferred derivation. “None stated” means no independent practical-accuracy basis was found, not that no number was predeclared. Numerical envelopes, empirical uncertainty and engineering requirements remain separate columns in the reasoning.

| ID | Gate/task | Observable/support | Role | Threshold | Stated basis | Achieved | Resolution | Assessment | Consequence | Locator |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| T-A01 | Cameron gate | EY identity at GS1.9 | Conservation regression | abs gap<.5pp | “Self-contained mass-budget gate” | GS1.1 diagnostic gap−1.67e−13pp | Numerical invariant | Too loose; existing tests stronger | Reuse off-knot independent inventory | `PW:puckworks/validation/gates.py:L363-L376@9dd456b` |
| T-A02 | Wadsworth collapse | 21 K ratios | Source mean-log reproduction | .7<GM<1.2 | “reproduces from their own Table 1” | GM.912698;5outside±30% | Mean check only | Role-confused if treated pointwise | Report scatter/exposure | `PW:puckworks/validation/gates.py:L17-L24@9dd456b` |
| T-A03 | Infiltration | DE1 first drip | In-sample compatibility | Porosity bracket | “Parameter-free first-drip prediction” | 6.4<7.018<7.8s; fittedκ | Not independent | Role-confused wording | Align with existing evidence label | `PW:puckworks/validation/gates.py:L26-L42@9dd456b` |
| T-A04 | FosterCT | Fitted curves/CT points | Port + post-fit coverage | <.2mm;≥4points;floor.5mm | “line width” | RMSE.002/.001;coverage4/8,5/8 | Finite source allowance | Floor/majority wording needs qualification | Do not call independently validated | `PW:puckworks/validation/gates.py:L1170-L1195@9dd456b` |
| T-A05 | LB / Roman sphere | Analytical solution | Code verification | <.5%;sphere<.001 | “exact plane-Poiseuille solution” | LB.052%;sphere.000120 | Analytic comparison | Appropriate bounded role | Keep simple analytic controls | `PW:puckworks/validation/gates.py:L9-L15@9dd456b` |
| T-A06 | RomanMPE | Reported source MPE | Transcription regression | 15 rows; medium-MW max≤14.5%; its mean below low/high-MW means | “~+/-0.5 pp raster fidelity” | Medium-MW maximum 14.3%; mean 10.9% | Source table read | Role-confused as new prediction | Label reported-source statistics | `PW:puckworks/validation/gates.py:L859-L881@9dd456b` |
| T-A07 | G10bulk | One Cameron liquor field | Scenario sensitivity | μratio<1.15;supp<8%;endfactor>.95 | “Fast single-shot bound” | 1.043;4.12%;.9897 | One source-law scenario | Global safety inference too broad | Keep result; narrow scope | `PW:puckworks/validation/gates.py:L1481-L1498@9dd456b` |
| T-A08 | MASS001–003 | Original suffix TDS | Research adequacy/increment | R1,A.5;gain.1AND20% | none stated as practical accuracy | Multiple condition/bias failures;003empiricalPASS | No complete u_val | Practical basis unestablished; no blanket strictness verdict | Finish own-support T04 | `PW:docs/analysis/sci_md_mass_delivery_003/RESULT.md:L7-L59@9dd456b` |
| T-A09 | Caffeine | 12 primary shots | Research adequacy/increment | R≤.50, A≤.25; gain≥.10 AND≥15%, ≥3/4 definite wins, A deterioration≤.05 (mg/g) | “Predeclared research budgets” | gains .027/.067/.090, all<.10; S1 win count also fails | Numerically definite; deletions finite | Stringent for descriptive gain; not proven too strict for a use | Keep contract and all conjunctions, report gain | `PW:docs/analysis/sci_md_caffeine_delivery_001/PROTOCOL.md:L69-L83@9dd456b` |
| T-A10 | 5CQA | 12 primary shots | Adequacy + increment | Candidate R≤.25, A≤.125; gain≥.05 AND≥15%, ≥3/4 definite wins, A deterioration≤.025 (mg/g) | “engineering budgets” | L12 R .2975, A .2544; A deterioration vs L1M .038685 exceeds .025 | Numerical fail; empirical u incomplete | Near gain misses do not excuse inadequacy or bias deterioration | No automatic offset or adoption | `PW:docs/analysis/sci_md_5cqa_assay_002/PROTOCOL.md:L156-L174@9dd456b` |
| T-A11 | RHEOLOGY010/T05 | Finite-mass C comparison | Approximation + precision | TDS .10 pp; shares 1/2 pp; flow/path .01/.02; u≤.2 budget | none stated as experimental accuracy | 24 PASS; 2 secondary TDS precision-ineligible (u>.020 pp) | All 8 secondary finite envelopes above their metric budgets | Appropriate separate roles | Retain original labels/useful sensitivity | `PW:docs/analysis/val_case_rheology_decision_resolution_001/RESULTS.md:L62-L174@9dd456b` |
| T-A12 | Grudeva009 | Publication arrival/profile | Source reproduction | .025arrival;.015concentration | none stated as physical accuracy | arrival+.120850;readbound.010025 | Event mismatch;horizontal propagation incomplete | Do not rebrand as physical adequacy | Source/observer crosswalk | `PW:docs/analysis/model_grudeva2026_publication_reconciliation_009/RESULTS.md:L3-L25@9dd456b` |
| T-A13 | MASS006–008 | Declared condition, shot or calibration support | Research adequacy/increment | R≤1, A≤.5 pp; increments≥.10 pp AND≥15%; A deterioration≤.10 pp; exact distinct count/noninferiority rules in A.6 | “task working budgets” | 006 earned; 007 7/11 adequate; 008 A2 adequate, every increment fails a conjunction | Numerical decisions definite; finite dependent-shot sensitivity | No replacement by MASS001–003 20% rule or independent-binomial inference | Preserve every original axis and comparator | `PW:docs/analysis/sci_md_mass_delivery_008/PROTOCOL.md:L48-L73@9dd456b` |

### F-O3-09 — Interrupted comparisons and stopped transfers are informative, not random missing data

**Claim and evidence [R/D+/J, Medium]:** RP-D-LC-001 failed a volume-flux proxy at 1.028×10⁻³ versus 10⁻³; density-weighted mass conservation was **not evaluated**, so calling it measured mass nonconservation is wrong. Its changing Reynolds number under refinement and inversion instability independently prevent transfer adjudication. MD008/009 stops are also scientifically informative. Maillé's unresolved denominator/operator, Moroney's failed declared calibration family and Smrke's adverse tested-form gains do not justify blanket rejection of every related theory. `PW:docs/analysis/rp_d_lc_001/decision.md:L47-L57@9dd456b`; transfer results in Appendix E.

**Counter-evidence:** incomplete executions cannot establish a favorable comparison on the full original scope; qualified subsets retain their own limited use. Replay may be appropriate after a specific defect is resolved. **Consequence:** retain failure/coverage reasons and existing successors; do not treat missing cases as exchangeable omissions or start a fresh broad sweep. **Related:** R-07; T10/T11.

<a id="section-8"></a>

## 8. Reconciliation with earlier reviews and active work



The October 1 synthesis and October 6 Development Guide largely survive this audit in their **corrected**, bounded forms. Complete F1–F15 and R1–R15 implementation/correctness/agreement tables are in Appendix C.5. They distinguish a completed alternative from a rejected original recommendation. The unavailable original external reviews remain [S] sources by attribution; I cannot certify that each synthesis represented them fairly.

Important changes from the frozen independent view were: #335 owner acceptance is established, not merely its merge; #321's witness repair is complete, not an outstanding technical repair; the H1 plan chain ends in candidate v2.2.1, not v2; the Guided Pull pressure/source-error disclosures are already implemented by #324; and Grudeva's frontier is now 008/009/#333 rather than 003. No numerical finding was changed to agree with an earlier review. The phase-boundary corrections are preserved in Appendix B's frozen notes.

| Oct 9 item | Status at reviewed pins | Correctness/agreement and remaining scope |
|---|---|---|
| T01, canonical review/status | Partly implemented | Review/pointers merged; correct current lifecycle and exposure metadata, preserving history |
| T02, matched uncertainty | Scoped completion; broader queue partial | #334 and chemistry addenda respect support/dependence; full assay/input uncertainty and early mass tasks remain unavailable/incomplete |
| T03, resolution policy | Implemented and owner accepted | Correct opt-in separation; current proposed/pending header needs reconciliation; no automatic adoption |
| T04, retained empirical comparisons | Partly implemented | Caffeine/5-CQA complete; MASS007/008 dependence addressed; MASS001–003 remain the uncompleted scope |
| T05, rheology resolution | Implemented for 010 | 32-row reconstruction exact; preserve two precision-ineligible results and useful finite sensitivity |
| T06, gate roles/predicates | Not completed by follow-ups | Narrow current defects confirmed; stronger tests already exist; no general threshold relaxation |
| T07, Grudeva source crosswalk | Partial; #333 blocked | 008/009 complete; full-reference refinements not run; no multiplier repair or duplicate campaign |
| T08, pressure feasibility | No new successful mechanism | Existing monotonicity/retirement remains correct; distinguish root repair from physical turnover |
| T09, 5-CQA bias diagnosis | Partial | Residual decomposition complete; causal calibration/observer explanation unresolved |
| T10, interrupted work | Partial, case-specific dispositions exist | No common random-censoring interpretation; reuse existing RP-D/SCI-LC/XSV successors |
| T11, exact data gaps | Partial | Guide/ledger exist; repair metadata and name missing joins before new acquisition |
| T12, proportion/resource control | Implemented in sampled practice; not quantified programme-wide | Bounded corrections and evidence reuse work; no labor-share or general efficiency proof |

This table is [R/X/D+/J] for completed numerical addenda and current verified state; unstarted-scope judgments depend on the comprehensive integration/open-work search, not on an assumption that absent files imply absent private work. Authority: `PW:docs/research/ESPRESSO_THRESHOLD_AND_CAPABILITY_REVIEW_2026-10-09.md:L240-L318@9dd456b`; all five merged follow-up identities and protocol/result chronology appear in Appendix A.

<a id="section-9"></a>

## 9. Recommendations register



These are proposed next actions, **not authorization to execute them**. Repository-backed paths below mean the pinned files in Appendix E; their SHA-256 values are in the reuse manifest in Appendix A. “S” means about a day of agent work; “M” about a week; “L” longer. Effort excludes waiting for owner/source access. No new experiment is commissioned by this register.

| ID | Action | Priority | Type | Effort | Owner decision |
|---|---|---|---|---|---|
| R-01 | Correct current routing, lifecycle and units | P1 for exposure routing; P2 for prose | Correction/status | S | No new scientific decision |
| R-02 | Complete the remaining T04 mass interpretation | P1 | Data analysis | M | Confirm the already proposed case scope/access |
| R-03 | Decide and run an eligible matched H1 comparison | P1 | Data analysis/model comparison | M | Yes: distinct comparator scope |
| R-04 | Complete T08 pressure-mechanism feasibility | P1 | Model-development analysis | S | Yes: choose scope |
| R-05 | Finish T06 with existing verification | P2 | Test/verification and claim correction | S | Only for a new scientific acceptance basis |
| R-06 | Close the specific Grudeva source/observation gap | P1 | Source analysis | S–M | Only for new access/communication/run scope |
| R-07 | Reuse reviewed science and disposition existing tasks | P2 | Process simplification | S | #321/#333 lifecycle choices |
| R-08 | Test whether 5-CQA bias provenance is available | P1 | Data analysis | S | Only if unavailable provenance must be obtained |

### R-01 — Correct current routing, lifecycle and dimensional labels

- **Addresses/question:** F-O1-02, F-O3-01/08; T01/T11. Can a reader or discovery tool select the right evidence without false permission, absence or merge claims?
- **Governance:** G0; EWP `NO_GOVERNING_PHYSICS_CHANGE`.
- **Evidence to reuse:** access policy, AVAILABLE_DATA_REGISTER, current.json/CURRENT, #335 acceptance comment and merge, EWP PROJECT_STATE and `POROSITY_MATERIALITY.json`; hashes in Appendix A.
- **Steps:** (1) propagate deny/exposure lineage from existing authorities; (2) reconcile current lifecycle/count/permission pointers; (3) label porosity effects as dimensionless percentages; (4) regenerate affected views; (5) verify links, units and unchanged historical results.
- **Acceptance:** routing agrees with policy; unknowns remain explicit; actual source times and relative effects are distinguishable; frozen scores/defaults are unchanged. If authority conflicts remain, report them unresolved instead of guessing.
- **Stop/effort/dependencies:** stop if target inspection or scientific reinterpretation becomes necessary; S; only existing metadata required.
- **Duplicate check/owner:** use EWP #76 and T01/T11, not another status system. #324 disclosure work is excluded because complete. No new scientific owner decision.

### R-02 — Complete T04 for MASS001–003 on their own scoring support

- **Addresses/question:** F-O3-03–04; T02/T04. Which historical failures are stable under admitted input/numerical/shot perturbations, and is there any independently defined practical use?
- **Governance:** G1; EWP `NO_GOVERNING_PHYSICS_CHANGE` if a consumer update is needed.
- **Evidence:** original three RESULTS/PROTOCOL files, #334 method, accepted resolution policy; exact hashes in Appendix A.
- **Steps:** (1) freeze one case declaration using each original mask/aggregation and every arm; (2) check retained prediction/input availability; (3) propagate paired whole-shot effects and conditioning-input dependence where supported; (4) report historical contract, resolution, named use and adoption separately; (5) include temperature/flow exclusions and positive empirical controls.
- **Acceptance:** reproduce originals, preserve unavailable flow metrics, and admit stable fail, unresolved, or no practical margin. No population confidence from deletion alone, no refit or changed threshold. A descriptive gain is not automatic usefulness.
- **Stop/effort/dependencies:** missing retained inputs yield an explicit unavailable component; no guessed noise floor. M; external authorized retained evidence may be needed.
- **Duplicate check/owner:** #334/#338/#339/#340 are complete and reused; only the uncompleted mass scope remains. Confirm case scope/access, not the verdict.

### R-03 — Add a matched equilibrium-limit question without rewriting #104's frozen test

- **Addresses/question:** F-O3-05–07. Can available fraction chemistry distinguish equilibrium-limit delivery from finite-rate release given identical information?
- **Governance:** G1 for existing-model eligibility/analytic-limit comparison, EWP `NO_GOVERNING_PHYSICS_CHANGE`; a genuinely new governing closure requires a separately declared G2 change.
- **Evidence:** exposed Pannusch/Schmieder source contract and fraction windows, existing solver/cards, MD008/009 negative results, #104; hashes in Appendix A.
- **Steps:** (1) obtain a distinct comparator scope; (2) verify source flow/temperature semantics and informative fraction support; (3) derive the equilibrium limit, keeping inventory, partition and hydraulics equal; (4) freeze both arms and numerical budgets; (5) compare whole-shot grouped fraction/species responses and all adverse panels; (6) state which H1 subclaim is actually discriminated.
- **Acceptance:** outcome may favor either arm, show indistinguishability, or be blocked by observation/input nonidentifiability. Do not manufacture an infinite-rate proxy by an arbitrary large constant or fit inventory to rescue tested targets.
- **Stop/effort/dependencies:** stop before empirical scoring if support/authority or numerical separation fails; M; R-01 metadata and eligible source inputs.
- **Duplicate check/owner:** #104 is a frozen shared/species test, not existing permission for this contrast; MASS, MD008/009 and completed stopping tasks do not answer the matched-limit question. Owner scope decision required; Angeloni remains excluded.

### R-04 — Complete T08 pressure-mechanism feasibility before another campaign

- **Addresses/question:** F-O3-02; T08. Can a distinct, source-defined coupling produce the observed pressure response within an admissible domain?
- **Governance:** G1 source/feasibility analysis, EWP `NO_GOVERNING_PHYSICS_CHANGE`; new governing-law implementation is separately G2.
- **Evidence:** SCI-MD-010/011/012, source equations, matched pressure observables and existing data ledger; pinned hashes in Appendix A.
- **Steps:** (1) choose one distinct source-based premise; (2) derive its sign/domain constraints; (3) compare with the frozen observable and simpler alternatives; (4) map distinguishing inputs/outputs to existing holdings; (5) return feasible, infeasible or unresolved with the smallest justified next scope.
- **Acceptance:** the mechanism must permit the required response without pressure-specific retuning; a negative feasibility result or a justified decision to stop is complete. Saturation utility cannot substitute for the required declining response. No Qc/Pc sweep, automatic diffusion port or native run follows from authorization to plan.
- **Stop/effort/dependencies:** no admissible mechanism or distinguishing observable means stop; S; owner and source/method knowledge.
- **Duplicate check/owner:** continues T08, reusing MD012 instead of repeating root rescaling. SCI-ED-003 Stage F concerns M01/M02 method and closure feasibility; #117 audits existing evidence and prospective home-lab purchases, including telemetry qualification. Neither authorizes T08 mechanism work. Owner chooses the bounded scientific scope; no experiment or native run is authorized here.

### R-05 — Complete T06 by aligning a few gates with their actual purpose

- **Addresses/question:** F-O2-01–02, F-O3-08. Would the named verification gate reject its known defect, and does its PASS mean what readers are told?
- **Governance:** G0 for wording/wiring to unchanged requirements; G1 declaration if a scientific acceptance requirement changes. EWP `NO_GOVERNING_PHYSICS_CHANGE` for links only.
- **Evidence:** gates.py, existing Cameron inventory tests, selected gate results and source cards; hashes in Appendix A.
- **Steps:** (1) reuse the independent inventory reducer/off-knot support; (2) demonstrate detection of the known interpolation defect; (3) derive a numerical budget from that verification role; (4) correct fitted/coverage/single-case labels for infiltration, Foster, Wadsworth and G10; (5) run only affected verification and report negative controls by purpose.
- **Acceptance:** the repaired implementation passes and known defective behavior fails; no claim of universal accuracy, independent validation or blanket viscosity safety. If a gate is only source transcription, say so rather than inventing a model test.
- **Stop/effort/dependencies:** no new generic schema or all-gates rewrite; S; existing verified tests suffice.
- **Duplicate check/owner:** T06 continuation, not another Cameron repair. Source inventories and #324 disclosures are complete. A new practical threshold requires its own basis/decision.

### R-06 — Complete T07's source/observation crosswalk around the robust mismatch

- **Addresses/question:** F-O2-04. Which explicit source equation, normalization, boundary/initial condition or observation mapping could explain the retained arrival discrepancy?
- **Governance:** G1 source analysis; EWP `NO_GOVERNING_PHYSICS_CHANGE` if linked.
- **Evidence:** Grudeva 004/008/009, source-input identities and #333's accepted-state versus unavailable dense-output distinction; hashes in Appendix A.
- **Steps:** (1) reuse completed numerical comparisons; (2) build one equation/parameter/observable crosswalk against the exact publication; (3) propagate available horizontal reading bounds where slope matters; (4) list only unresolved source questions and the observation that could resolve each.
- **Acceptance:** an explicit supported mismatch, or a bounded unresolved source cause, is sufficient. Do not assert author error or create a fitted multiplier. Figure 5's missing profiles remain missing.
- **Stop/effort/dependencies:** no #333 retry, refinement or author message without its necessary authorization; S–M; exact accessible source evidence.
- **Duplicate check/owner:** T07 already proposed; 004/008/009 completed and #333 active. Reuse their crosswalk entries; if they already answer an item, close it without repetition. Owner needed only for new access, communication or execution scope.

### R-07 — Apply existing reuse rules and settle the existing queue

- **Addresses/question:** F-O1-03–04, F-O3-09; T10/T12. Which remaining work protects a real undecided claim?
- **Governance:** G0, EWP `NO_GOVERNING_PHYSICS_CHANGE`.
- **Evidence:** SCI-GOV-001 §11, Foster/caffeine bounded corrections, current #321/#333/#76/#117 states; hashes/URLs in Appendices A/C.
- **Steps:** (1) identify the affected claim for each correction; (2) reuse unchanged reviewed artifacts; (3) run bounded affected checks; (4) record technical completion separately from lifecycle/adoption; (5) retain interrupted outcomes and the Paper 1 assurance freeze.
- **Acceptance:** completed repairs do not spawn another science campaign; unresolved integrity stops remain unresolved. If labor imbalance is alleged, obtain lane time evidence rather than infer it from LOC. No required control is removed merely because it is verbose.
- **Stop/effort/dependencies:** stop a successor without new information or decision; S; existing governance and owners.
- **Duplicate check/owner:** no new governance framework, branch quota, package reorganization or review ladder. #321 awaits lifecycle disposition; #333 remains qualification-incomplete. Those owner choices remain separate.

### R-08 — Check 5-CQA calibration and observation provenance before proposing a bias correction

- **Addresses/question:** F-O3-06; T09. Is there new information that can distinguish assay/calibration, recovery, composition or predictor error?
- **Governance:** G1 data/provenance analysis; EWP `NO_GOVERNING_PHYSICS_CHANGE` if linked.
- **Evidence:** 5-CQA delivery/TDS/assay001/assay002, #340 decomposition, existing original-source manifests; hashes in Appendix A.
- **Steps:** (1) enumerate already checked FIT/PRED calibration reconstruction; (2) identify any remaining original calibration, dilution, recovery or interval-join records; (3) check their eligibility without outcome-driven exclusion; (4) report which causal explanations remain distinguishable.
- **Acceptance:** no new provenance, or no identifiable cause, is a valid negative result. The retained bias and every adverse panel remain; a residual decomposition alone never authorizes an additive offset.
- **Stop/effort/dependencies:** stop when available evidence cannot distinguish causes; S; authorized original records. Any new assay experiment needs a separate named decision/design after this check.
- **Duplicate check/owner:** T09 continuation; completed calibration reconstruction and #340 arithmetic are not repeated. Owner involvement only if missing provenance must be requested.

R-01, R-02, R-05, R-06 and R-08 can proceed independently within their access boundaries. R-03 needs the scope/eligibility decision; R-04 is an owner choice. R-07 applies throughout and should reduce repeated work, not become a dependency framework.

<a id="section-10"></a>

## 10. Decisions only the owner can make



Choose whether SCI-ED-003 Stage F is worth authorizing, declining or narrowing. That stage is nonadjudicative method feasibility for M01 paired absolute chemistry/mass closure plus shot-context M02; it is separate from T08 pressure-mechanism analysis and the conditional M04 dynamic-resistance task. `EWP:docs/analysis/sci_ed_003/MINIMUM_PROGRAMME.md:L3-L31@4284e94`. Decide whether the matched H1 comparator merits a distinct scope beside frozen #104; and whether a practically relevant margin/application justifies any model complexity beyond descriptive gains. Settle #321's completed candidate lifecycle separately from #333's incomplete qualification. Decide whether missing source/assay records should be requested. New external messages, native campaigns, laboratory work, purchases, protected access and production adoption are not authorized by this report.

<a id="section-11"></a>

## 11. Limitations and known unknowns



No OpenFOAM trajectory, original author MATLAB/Octave execution, complete private shot/deletion replay or new external-corpus scan was performed. Historic native metrics and figure scores retain their original provenance. Full numerical/input/measurement covariance is generally unavailable; no global noise floor or perfect-model false-failure probability was estimated. No empirical equivalence is claimed from an interval containing zero. Maturity and PR-purpose classifications are judgments with explicit scopes/alternatives, not measured scientific value or effort.

The protected routing inconsistency was inspected through metadata only. The current access guard remained authoritative. Exact scientific completeness of unmounted private holdings, original external review fairness and causal explanations of Grudeva/5-CQA discrepancies remain unknown. The safe test selectors and environmental failures mean this is not a claim of a clean all-platform/full-data test run. Strongest findings are algebraic/retained-arithmetic distinctions; weakest are maturity granularity, unmeasured governance burden and predictions about which future observable will be most discriminating.

<a id="section-12"></a>

## 12. Handoff to the second reviewer



Check these ten claims first, using the embedded scripts and pinned locators:

1. Every original rheology decision survives the 32-row reduction; two precision failures coexist with above-budget finite envelopes.
2. Caffeine gains include all three primary and temperature comparators; private deletion evidence is not mislabeled as newly recomputed observations.
3. 5-CQA bias, contribution identity and adverse L2M/temperature comparisons support the stated limits.
4. The finite-porosity and machine derivatives are nonnegative only under the stated admissible assumptions.
5. P1's lower descriptive error, crossing full interval and adverse low-pressure panel are all preserved; E2C is incomplete.
6. The 66+1 registry result, 28 component evidence labels and Cameron off-knot closure match current code.
7. Grudeva's event mismatch exceeds its reported reading/refinement scales without proving source author error or full Figure 5 reproduction.
8. The 30/60-day first-parent census and source-size ratios reproduce; mixed classifications/mirrored handoffs do not masquerade as labor.
9. #335 acceptance, #321 technical completion and #333 integrity stop remain distinct at your fresh head.
10. R-02–08 do not duplicate completed work or expand #104/Stage F execution permissions.

Most fragile claims are the six-axis maturity judgments, exact private-corpus independent-unit counts, historical Cameron digitization residuals [S], and causal/source interpretations. The complete per-integration classifications and original-review crosswalk include delegated judgment; extend those samples before treating them as exhaustive causal evidence. Exact reproduction commands are in Appendix A and full scripts in B. First refresh both heads, append affected merges, then check numbers before broadening tests.

Open questions: what independently justified application margin should complexity buy; what exact pressure/flow observable represents the apparatus boundary; can accessible inventory/partition information be held equal in the H1 comparison; which original assay/calibration records remain available; and what source condition explains the robust Grudeva arrival difference? None is answered by a new PASS token alone.

<a id="section-13"></a>

## 13. Change log for later reviewers



| Date | Reviewer | Section | Change | Reason | Evidence |
| --- | --- | --- | --- | --- | --- |
| 2026-10-19 UTC | Archival filing (Codex) | Publication note; Section 13; Appendices A–B | Derived three EWP script workspace roots from their extracted locations; made the recorded rerun command portable with explicit working directory; retained executed-source hashes and added portable-script hashes | G0 repository portability only; original receipts preserved; no scripts rerun or scientific changes | Verified presentation-corrected input SHA-256 `1ff3341ea5a613a1dc09e7915579da7efe66126e677316f3619067e1ed56e0db`; displayed portable-script digests in B.2; archived-file digest in the development guide |
| 2026-10-19 UTC | GPT-6 Astra Pro | Presentation; Appendices A–E | Added navigation; rendered frozen prose; folded raw payloads; stacked detailed records; escaped a literal HTML-like table value | Repair unreadable appendix presentation; scientific content and original code payloads preserved | Original review SHA-256 `60c88a4070824a80483e20a219fa64da8cfc127bc2db385d67ca5ea39afe477d`; 44 original fenced payloads preserved byte-for-byte |





<a id="appendix-a"></a>

## Appendix A — Commands, outputs and numerical evidence

[Back to navigation](#review-navigation)

All commands are read-only with respect to the reviewed repositories. Outputs and environments were placed in the review workspace. The shell examples below are exact operations or compact equivalent invocation forms for the embedded scripts. A second reviewer should retain the directory layout `puckworks/`, `espresso-whole-pull/`, `review_work/{scripts,data,ewp,census,results,logs}/`; the three archived EWP helper scripts derive the workspace root from their extracted script locations using `Path(__file__).resolve().parents[2]` (or `pathlib.Path`). The portable rerun command recorded in `augment_results.py` starts at that workspace root and explicitly changes into `espresso-whole-pull/`. Do not copy these commands into a protected-data session without retaining the stated exclusions.

<a id="appendix-a-1"></a>

### A.1 Identity, environment and scope



```bash
git clone https://github.com/trbrewer/puckworks
git clone https://github.com/trbrewer/espresso-whole-pull
git -C puckworks log -1 --format='%H %cI %s'
git -C espresso-whole-pull log -1 --format='%H %cI %s'
git -C puckworks fetch origin
git -C espresso-whole-pull fetch origin
git -C puckworks rev-parse HEAD origin/main
git -C espresso-whole-pull rev-parse HEAD origin/main
git -C puckworks status --short
git -C espresso-whole-pull status --short
```

```json
{
  "end_utc": "2026-10-18T23:20:46Z",
  "repositories": {
    "PW": {
      "start": "9dd456be7fd797b9cda0a2bbf50d1ac717d72835",
      "head": "9dd456be7fd797b9cda0a2bbf50d1ac717d72835",
      "origin_main": "9dd456be7fd797b9cda0a2bbf50d1ac717d72835",
      "new_integrations": [],
      "tracked_status": "",
      "fetch_exit": 0
    },
    "EWP": {
      "start": "4284e9460c8057053e95de7cfa2fb3590e68e9db",
      "head": "4284e9460c8057053e95de7cfa2fb3590e68e9db",
      "origin_main": "4284e9460c8057053e95de7cfa2fb3590e68e9db",
      "new_integrations": [],
      "tracked_status": "",
      "fetch_exit": 0
    }
  }
}
```

The final fetch is a freshness check, not a checkout/update of reviewed source. Full normal clones retain live remote branches. The additional EWP CI analysis-authority checkout is distinct from the runtime lock. No external-data root was set. The protected policy was read only as metadata; the four denied target paths and denied target-building/data APIs were not opened/called.

Orientation check [R/X]: PW source is `0.4.0.dev0` (`PW:pyproject.toml:L1-L5@9dd456b`); EWP is `0.2.0` (`EWP:VERSION:L1-L1@4284e94`). GitHub’s current [PW latest release](https://github.com/trbrewer/puckworks/releases/tag/v0.3.0) is v0.3.0, published 18 July 2026, with wheel and source-distribution assets; the API was checked in this session. PW’s statement that it is not on PyPI remains a repository distribution statement [S], not a fresh PyPI catalogue audit. The complete source-component and gate counts below confirm the prompt’s orientation; current lifecycle wording is corrected in F-O1-02.

```bash
python3.12 -m venv review_work/pwvenv
review_work/pwvenv/bin/python -m pip install -e './puckworks[dev]'
python3.12 -m venv review_work/ewp/venv
review_work/ewp/venv/bin/python -m pip install numpy==1.26.4 scipy==1.11.4 jsonschema==4.23.0
git clone --shared puckworks review_work/ewp/pw-authority
git -C review_work/ewp/pw-authority checkout --detach a3428a4d4ad571ef3168a70e8a04620fca5d3520
git -C review_work/ewp/pw-authority cat-file -t 2058d0e947ee9eb92c52d64f6165b810f1fb4732
```

```text
Linux 6.18.55 x86-64; glibc 2.39
PW: Python 3.12.14; NumPy 2.5.4; SciPy 1.18.1; pytest 9.1.1
EWP: Python 3.12.14; NumPy 1.26.4; SciPy 1.11.4; jsonschema 4.23.0
CI Python patch-version difference: 3.12.14 here versus 3.12.3 in EWP CI.
```

<a id="appendix-a-2"></a>

### A.2 Test receipts and environmental classification



```bash
cd puckworks
env PYTHONDONTWRITEBYTECODE=1 ../review_work/pwvenv/bin/python -m pytest -q \
  -m 'not slow and not live and not gpu and not external_data and not protected_target_integrity' \
  --deselect=tests/test_uncertainty_intake.py::test_angeloni_recovered_table_is_complete_and_self_consistent \
  --deselect=tests/test_uncertainty_intake.py::test_recovered_angeloni_canonical_summary_validates \
  > ../review_work/logs/pw-quick.log 2>&1
```

```text
24 failed, 5993 passed, 66 skipped, 762 deselected, 1 warning in 1705.88s (0:28:25)
```

[X] All 24 failed node IDs were selected from the original receipt by the complete `retry_pw_environment.py` in Appendix B. It asserts that no protected/Angeloni node is selected. Rerun settings were `TMPDIR=/dev/shm`, single BLAS/OpenMP threads and unchanged tests/guards, using approved execution outside the restrictive process sandbox.

```bash
review_work/pwvenv/bin/python review_work/scripts/retry_pw_environment.py
```

```text
=========================== short test summary info ============================
FAILED tests/test_grudeva2026_fine_baseline_qualification_007.py::test_os_limits_are_observed_not_replaced
FAILED tests/test_grudeva2026_matched_comparison_008.py::test_manufactured_execute_path_no_solver
FAILED tests/test_grudeva2026_publication_reconciliation_009.py::test_execution_is_offline_and_nonoverwriting
3 failed, 21 passed in 17.95s
```

The remaining three tests are the Grudeva 007 OS-limit observation, 008 manufactured execution and 009 offline/nonoverwriting execution tests. Each requires `/proc/pressure/memory`, absent on this host even outside the sandbox. No telemetry was fabricated. These are environment-blocked verification, not established model defects and not passing tests. Other initial failures involved loopback sockets, outside-Git private-output checks on temporary directories, and child resource-limit visibility. Their unchanged reruns passed.

EWP commands were executed by the delegated reviewer; the principal reviewer inspected the runner, receipts and environment diagnoses [D+].

```bash
review_work/ewp/venv/bin/python review_work/ewp/run_checks.py
```

| Check | Initial result | Elapsed wall time, s |
| --- | --- | --- |
| environment | 0 exit code | 0.230 |
| source_manifest | 0 exit code | 0.281 |
| static_validate | 0 exit code | 49.115 |
| unit_suite | 1 exit code | 712.022 |
| baseline_integrity | 0 exit code | 0.045 |
| shell_syntax | 0 exit code | 0.015 |

```text
----------------------------------------------------------------------
Ran 1635 tests in 710.433s

FAILED (failures=1, errors=23, skipped=21)
```

Twenty-two lifecycle errors and the reservation failure required consistent process identity between `os.getpid()` and `/proc`; one additional loader error required a temporary directory without a Git ancestor. Both groups were rerun together without modifying code:

```bash
cd espresso-whole-pull
TMPDIR=/dev/shm PYTHONDONTWRITEBYTECODE=1 ../review_work/ewp/venv/bin/python \
  -m unittest tests.test_sci_lc_001a_family_controller \
  tests.test_research_two_assay_mass_delivery.LoaderTests
```

```text
..........................................
----------------------------------------------------------------------
Ran 42 tests in 0.353s

OK
```

The 42-test rerun contains the affected groups plus their unaffected neighboring cases; it does not mean 42 initial failures. Optional-dependency/external-source skips remain skips. The administrative authority check in static validation is not independently authenticated without a supplied expected head/tree; source-manifest and baseline identity checks retain their own narrower meanings.

<a id="appendix-a-3"></a>

### A.3 Registry, local equations and independent reduction receipts



```bash
env PYTHONDONTWRITEBYTECODE=1 review_work/pwvenv/bin/python -c \
  'import puckworks; s=puckworks.evaluate_all_gates(); print(s.summary_text())'
review_work/pwvenv/bin/python review_work/scripts/gate_sample.py
env PYTHONDONTWRITEBYTECODE=1 review_work/pwvenv/bin/python review_work/scripts/root_primary_audit.py
python review_work/data/audit_primary.py
env PYTHONDONTWRITEBYTECODE=1 review_work/pwvenv/bin/python \
  -m puckworks.analysis.rheology_decision_resolution \
  --evidence-checkout espresso-whole-pull \
  --output review_work/data/rheology_reproduced.json
python review_work/data/audit_reanalysis.py
python review_work/data/audit_additional_aggregates.py
review_work/ewp/venv/bin/python review_work/ewp/recompute.py
review_work/ewp/venv/bin/python review_work/ewp/augment_results.py
python review_work/census/make_classifications.py
python review_work/census/build_census.py
python review_work/census/render_tables.py
```

```text
Registry: PASS 66; FAIL 0; SKIP 0; ERROR 0; ACKNOWLEDGED_EXCEPTION 1.
Registry elapsed: 157.539 s.
Later public aggregate checks: 312; maximum absolute reaggregation difference 4.440892098500626e-16.
Earlier MASS public metrics: 286; comparison components: 50; maximum difference 4.440892098500626e-16.
MASS stopping: 15 panel/arm rows; 105 public count/rate checks.
Rheology: 32/32 original numerical terms, sums and decisions reproduced.
Pressure: both retained 2,000-draw panels reproduced; seed 20260902.
Finite-porosity quadrature: 21 values; maximum absolute difference 6.661338147750939e-16.
```

The official public rheology reducer was also executed by the principal reviewer into a new scratch file; byte comparison returned exit 0:

```bash
env PYTHONDONTWRITEBYTECODE=1 review_work/pwvenv/bin/python \
  -m puckworks.analysis.rheology_decision_resolution \
  --evidence-checkout espresso-whole-pull \
  --output review_work/results/rheology_official_root.json
cmp review_work/results/rheology_official_root.json \
  puckworks/docs/analysis/val_case_rheology_decision_resolution_001/RESULTS.json
```

Registry outcomes [X]; no PASS below is upgraded beyond its registered evidence role:

| Component | Gate | Outcome |
| --- | --- | --- |
| brewer2026.coupled_kappa_t | gate_kappa_t_composition_diagnostic | PASS |
| brewer2026.coupled_kappa_t | gate_kappa_t_degeneracy | PASS |
| brewer2026.lb_reference | gate_lb_channel | PASS |
| brewer2026.lb_taichi | `<none>` | ACKNOWLEDGED_EXCEPTION |
| brewer2026.pack_generator | gate_pack_generator_admissible | PASS |
| brewer2026.streamtube | gate_streamtube_heldout | PASS |
| cameron2020.extraction_bdf | gate_cameron_conservation | PASS |
| cameron2020.extraction_bdf | gate_smrke2024_fast_extraction_shape | PASS |
| fasano2000_partI.fines_migration | gate_fasano_cor82_nonmonotone | PASS |
| fasano2000_partI.fines_migration | gate_fasano_freeboundary | PASS |
| fasano2000_partI.fines_migration | gate_fasano_reversal_signature | PASS |
| foster2025.infiltration | gate_infiltration_triangle | PASS |
| foster2025.machine_mode | gate_foster_ct_trajectory | PASS |
| foster2025.machine_mode | gate_foster_fig15_flowmin | PASS |
| foster2025.machine_mode | gate_foster_machine_tp_ts | PASS |
| grudeva2025.reduced | gate_grudeva_no_eps_kappa | PASS |
| grudeva2025.reduced | gate_grudeva_reduced_solver | PASS |
| grudeva2026.reduced | gate_grudeva2026_reduced | PASS |
| lee2023.feedback | gate_lee_feedback_negative_result | PASS |
| liang2021.desorption | gate_liang_eoven_ceiling | PASS |
| liang2021.desorption | gate_liang_kemax_refit | PASS |
| maille2024.phi_closure | gate_maille_e1_shell_depth | PASS |
| maille2024.phi_closure | gate_maille_phi_closure_consistency | PASS |
| maille2024.phi_closure | gate_maille_phi_split_vs_cameron | PASS |
| maille2024.two_regime | gate_maille_kinetics_ci_flags | PASS |
| maille2024.two_regime | gate_maille_timescale_portability_cameron | PASS |
| maille2024.two_regime | gate_maille_timescale_portability_roman | PASS |
| maille2024.two_regime | gate_maille_two_regime_reproduction | PASS |
| mo2023_2.coupled_bed | gate_mo2_coupled_bed_fig8 | PASS |
| mo2023_2.swelling | gate_mo2_fixed_flow_trends | PASS |
| mo2023_2.swelling | gate_mo2_k0_carman_kozeny | PASS |
| mo2023_2.swelling | gate_mo2_swelling_flow_decay | PASS |
| mo2023_2.swelling | gate_mo2_swelling_insensitivity | PASS |
| moroney2016.surrogate | gate_moroney2015_batch_ode | PASS |
| moroney2016.surrogate | gate_moroney2015_kappa_anchors | PASS |
| moroney2016.surrogate | gate_moroney2019_ldf_verification | PASS |
| moroney2016.surrogate | gate_moroney_fig6_washthrough | PASS |
| pannusch2024.closures | gate_pannusch_closures | PASS |
| pannusch2024.solver | gate_pannusch_solver_mape | PASS |
| romancorrochano2017.extraction | gate_roman_bed_flow_trend | PASS |
| romancorrochano2017.extraction | gate_roman_bed_mpe_parameter_free | PASS |
| romancorrochano2017.extraction | gate_roman_mw_temperature_trends | PASS |
| romancorrochano2017.extraction | gate_roman_sphere_solver | PASS |
| romancorrochano2017.extraction | gate_roman_tamped_kappa | PASS |
| romancorrochano2017.extraction | gate_roman_y0_ceiling_sizeexclusion | PASS |
| sourcing2026.g10_liquor_rheology | gate_g10_foursource_spread | PASS |
| sourcing2026.g10_liquor_rheology | gate_g10_intersource_spread | PASS |
| sourcing2026.g10_liquor_rheology | gate_g10_mu_bias_directional | PASS |
| sourcing2026.g10_liquor_rheology | gate_g10_reference_mu_above_water | PASS |
| sourcing2026.g10_liquor_rheology | gate_g10_sobolik_closures | PASS |
| sourcing2026.g10_liquor_rheology | gate_g10_sobolik_density | PASS |
| sourcing2026.g10_liquor_rheology | gate_g10_telisromero2000_thermal | PASS |
| sourcing2026.g10_liquor_rheology | gate_g10_telisromero_closure | PASS |
| sourcing2026.g10_liquor_rheology | gate_g10_telisromero_full_table | PASS |
| sourcing2026.g10_liquor_rheology | gate_g10_viscosity_bulk_negligible | PASS |
| sourcing2026.g10_liquor_rheology | gate_gagne2021_viscosity_discrimination | PASS |
| sourcing2026.g1_glassbead_analog | gate_g1_glassbead_closure_sane | PASS |
| sourcing2026.g3_pump_characteristic | gate_g3_pump_envelope_bounds_quadratic | PASS |
| wadsworth2026.grindmap | gate_grindmap_polydispersity | PASS |
| wadsworth2026.grindmap | gate_grindmap_refit | PASS |
| wadsworth2026.inertial | gate_inertial_darcy_recovery | PASS |
| wadsworth2026.inertial | gate_inertial_de1_audit | PASS |
| wadsworth2026.inertial | gate_inertial_fo_band | PASS |
| wadsworth2026.inertial | gate_mo_reynolds_overlay | PASS |
| wadsworth2026.permeability | gate_wadsworth_collapse | PASS |
| waszkiewicz2025.poroelastic | gate_waszkiewicz_dynamic_9bar | PASS |
| waszkiewicz2025.poroelastic | gate_waszkiewicz_static_refit | PASS |

Additional quick-only executions [X]:

```python
from puckworks.gate_runner import evaluate_gate
from puckworks.validation import gates
names = ['gate_p3_schmieder_peak_discrimination', 'gate_coupled_kappa_t', 'gate_g9_series_resistance', 'gate_bruno_solute_inventory_prior', 'gate_g4_temperature_sensitivity', 'gate_extraction_harness']
for name in names:
    print(evaluate_gate('review_quick', getattr(gates, name)).to_dict())
```

| Gate | Outcome | Seconds |
| --- | --- | --- |
| gate_p3_schmieder_peak_discrimination | PASS | 11.256 |
| gate_coupled_kappa_t | PASS | 0.563 |
| gate_g9_series_resistance | PASS | 0.001 |
| gate_bruno_solute_inventory_prior | PASS | 0.004 |
| gate_g4_temperature_sensitivity | PASS | 0.101 |
| gate_extraction_harness | PASS | 1.700 |

The following compact output contains public source/figure aggregates, not private observations. Grudeva witnesses are retained extrema; complete arrays were not rescanned.

```json
{
  "cameron": {
    "gs": 1.1,
    "N": 20,
    "M": 12,
    "EY_percent": 16.659271074137386,
    "EY_minus_solid_pp": -1.6697754290362354e-13,
    "inventory_ceiling_percent": 24.467473066666663,
    "current_gate_allowance_pp": 0.5,
    "gate_allowance_kg_at_20g": 0.0001,
    "gate_allowance_fraction_initial_inventory": 0.020435293772987802,
    "printed_depth_m": 0.018715912492197614,
    "bulk_identity_depth_m": 0.022625619550529028
  },
  "wadsworth": {
    "n": 21,
    "geometric_mean": 0.9126980232550467,
    "min_ratio": 0.6541684781662224,
    "max_ratio": 1.7553598443396474,
    "rms_log_ratio": 0.28293720964939223,
    "outside_30_percent": 5,
    "note": "Arithmetic on source table, not independent validation."
  },
  "publication009": {
    "input_hash": "b2895fe8bdf7b8b1e529a9830b036f18eff9100800331a0ae8953b9ae9d13862",
    "inputs": {
      "C0": {
        "counts": {
          "EXCLUDED": 13,
          "INCLUDED": 18
        },
        "n": 31,
        "families": {
          "figure3_concentration": {
            "target_id": "F3C-016",
            "signed_residual": 0.09699961117395267,
            "absolute_residual": 0.09699961117395267,
            "limit": 0.015,
            "extraction_bounds": {
              "c_uncertainty": 0.010456273764258554,
              "z_uncertainty": 0.0029542097488921715
            }
          },
          "figure3_front": {
            "target_id": "F3F-003",
            "signed_residual": -0.01345521083093193,
            "absolute_residual": 0.01345521083093193,
            "limit": 0.008,
            "extraction_bounds": {
              "z_uncertainty": 0.0029542097488921715
            }
          },
          "figure4_arrival": {
            "target_id": "F4A-001",
            "signed_residual": 0.12088406935098295,
            "absolute_residual": 0.12088406935098295,
            "limit": 0.025,
            "extraction_bounds": {
              "t_uncertainty": 0.010025062656641603
            }
          },
          "figure4_concentration": {
            "target_id": "F4C-004",
            "signed_residual": 0.14131064604731197,
            "absolute_residual": 0.14131064604731197,
            "limit": 0.015,
            "extraction_bounds": {
              "c_uncertainty": 0.0063025210084033615,
              "t_uncertainty": 0.010025062656641603
            }
          }
        }
      },
      "C1": {
        "counts": {
          "EXCLUDED": 13,
          "INCLUDED": 18
        },
        "n": 31,
        "families": {
          "figure3_concentration": {
            "target_id": "F3C-016",
            "signed_residual": 0.09704174991283221,
            "absolute_residual": 0.09704174991283221,
            "limit": 0.015,
            "extraction_bounds": {
              "c_uncertainty": 0.010456273764258554,
              "z_uncertainty": 0.0029542097488921715
            }
          },
          "figure3_front": {
            "target_id": "F3F-003",
            "signed_residual": -0.013451268668975946,
            "absolute_residual": 0.013451268668975946,
            "limit": 0.008,
            "extraction_bounds": {
              "z_uncertainty": 0.0029542097488921715
            }
          },
          "figure4_arrival": {
            "target_id": "F4A-001",
            "signed_residual": 0.1208607410578244,
            "absolute_residual": 0.1208607410578244,
            "limit": 0.025,
            "extraction_bounds": {
              "t_uncertainty": 0.010025062656641603
            }
          },
          "figure4_concentration": {
            "target_id": "F4C-004",
            "signed_residual": 0.1413868439561956,
            "absolute_residual": 0.1413868439561956,
            "limit": 0.015,
            "extraction_bounds": {
              "c_uncertainty": 0.0063025210084033615,
              "t_uncertainty": 0.010025062656641603
            }
          }
        }
      },
      "P0": {
        "counts": {
          "EXCLUDED": 13,
          "INCLUDED": 18
        },
        "n": 31,
        "families": {
          "figure3_concentration": {
            "target_id": "F3C-016",
            "signed_residual": 0.09706211176387364,
            "absolute_residual": 0.09706211176387364,
            "limit": 0.015,
            "extraction_bounds": {
              "c_uncertainty": 0.010456273764258554,
              "z_uncertainty": 0.0029542097488921715
            }
          },
          "figure3_front": {
            "target_id": "F3F-003",
            "signed_residual": -0.013449181931561194,
            "absolute_residual": 0.013449181931561194,
            "limit": 0.008,
            "extraction_bounds": {
              "z_uncertainty": 0.0029542097488921715
            }
          },
          "figure4_arrival": {
            "target_id": "F4A-001",
            "signed_residual": 0.12084982342895056,
            "absolute_residual": 0.12084982342895056,
            "limit": 0.025,
            "extraction_bounds": {
              "t_uncertainty": 0.010025062656641603
            }
          },
          "figure4_concentration": {
            "target_id": "F4C-004",
            "signed_residual": 0.1413974742031971,
            "absolute_residual": 0.1413974742031971,
            "limit": 0.015,
            "extraction_bounds": {
              "c_uncertainty": 0.0063025210084033615,
              "t_uncertainty": 0.010025062656641603
            }
          }
        }
      },
      "P1": {
        "counts": {
          "EXCLUDED": 13,
          "INCLUDED": 18
        },
        "n": 31,
        "families": {
          "figure3_concentration": {
            "target_id": "F3C-016",
            "signed_residual": 0.0970526983087232,
            "absolute_residual": 0.0970526983087232,
            "limit": 0.015,
            "extraction_bounds": {
              "c_uncertainty": 0.010456273764258554,
              "z_uncertainty": 0.0029542097488921715
            }
          },
          "figure3_front": {
            "target_id": "F3F-003",
            "signed_residual": -0.013449375234393268,
            "absolute_residual": 0.013449375234393268,
            "limit": 0.008,
            "extraction_bounds": {
              "z_uncertainty": 0.0029542097488921715
            }
          },
          "figure4_arrival": {
            "target_id": "F4A-001",
            "signed_residual": 0.12085089285270723,
            "absolute_residual": 0.12085089285270723,
            "limit": 0.025,
            "extraction_bounds": {
              "t_uncertainty": 0.010025062656641603
            }
          },
          "figure4_concentration": {
            "target_id": "F4C-004",
            "signed_residual": 0.14140017978178615,
            "absolute_residual": 0.14140017978178615,
            "limit": 0.015,
            "extraction_bounds": {
              "c_uncertainty": 0.0063025210084033615,
              "t_uncertainty": 0.010025062656641603
            }
          }
        }
      }
    },
    "total_rows": 124,
    "included_rows": 72,
    "excluded_rows": 52,
    "arithmetic_max_delta": 0.0,
    "primary_shared_failures": 17,
    "first_selected_shared_failure_time": 3.2,
    "persistent_count_stored": {
      "figure3_concentration": {
        "direction_changed_shared_ids": [],
        "persistent_shared_ids": [
          "F3C-004",
          "F3C-005",
          "F3C-006",
          "F3C-009",
          "F3C-010",
          "F3C-011",
          "F3C-014",
          "F3C-015",
          "F3C-016"
        ],
        "primary_only_shared_ids": [],
        "refinement_only_shared_ids": []
      },
      "figure3_front": {
        "direction_changed_shared_ids": [],
        "persistent_shared_ids": [
          "F3F-002",
          "F3F-003"
        ],
        "primary_only_shared_ids": [],
        "refinement_only_shared_ids": []
      },
      "figure4_arrival": {
        "direction_changed_shared_ids": [],
        "persistent_shared_ids": [
          "F4A-001"
        ],
        "primary_only_shared_ids": [],
        "refinement_only_shared_ids": []
      },
      "figure4_concentration": {
        "direction_changed_shared_ids": [],
        "persistent_shared_ids": [
          "F4C-004",
          "F4C-005",
          "F4C-006",
          "F4C-007",
          "F4C-008"
        ],
        "primary_only_shared_ids": [],
        "refinement_only_shared_ids": []
      }
    }
  },
  "matched008": {
    "pairs": [
      {
        "pair": "PRIMARY",
        "complete": true,
        "family_count": 11,
        "family_failures": 0,
        "maximum_ratio_to_limit": 0.2151092706801916,
        "arithmetic_max_delta": 0.0,
        "unavailable": 0
      },
      {
        "pair": "SECONDARY 1",
        "complete": true,
        "family_count": 11,
        "family_failures": 0,
        "maximum_ratio_to_limit": 0.20729446779471639,
        "arithmetic_max_delta": 0.0,
        "unavailable": 0
      },
      {
        "pair": "SECONDARY 2",
        "complete": true,
        "family_count": 11,
        "family_failures": 0,
        "maximum_ratio_to_limit": 0.08599234784711918,
        "arithmetic_max_delta": 0.0,
        "unavailable": 0
      },
      {
        "pair": "SECONDARY 3",
        "complete": true,
        "family_count": 11,
        "family_failures": 0,
        "maximum_ratio_to_limit": 0.09669881951324122,
        "arithmetic_max_delta": 0.0,
        "unavailable": 0
      }
    ],
    "new_production_simulations": 0,
    "new_comparator_simulations": 0
  }
}
```

Synthetic policy cases [X], distinct from empirical decisions:

```bash
env PYTHONDONTWRITEBYTECODE=1 review_work/pwvenv/bin/python puckworks/examples/decision_resolution.py --output review_work/results/decision_resolution_synthetic.json
```

| Case | Contract | Resolution | Assessment complete |
| --- | --- | --- | --- |
| A-lower-satisfies | PASS | PASS | True |
| A-upper-satisfies | PASS | PASS | True |
| B-lower-violates | FAIL | FAIL | True |
| B-upper-violates | FAIL | FAIL | True |
| C-lower-overlaps | UNRESOLVED | UNRESOLVED | True |
| C-upper-overlaps | UNRESOLVED | UNRESOLVED | True |
| D-equality-< | FAIL | FAIL | True |
| D-equality-<= | PASS | PASS | True |
| D-equality-> | FAIL | FAIL | True |
| D-equality->= | PASS | PASS | True |
| E-bound | PASS | PASS | True |
| E-sensitivity | PASS | UNRESOLVED | True |
| F-stable-effect-precision-fails | FAIL | UNRESOLVED | True |
| G-overlap-precision-fails | FAIL | UNRESOLVED | True |
| H-adequate-insufficient-increment | FAIL | FAIL | True |
| I-adverse-diagnostic-not-a-gate | PASS | PASS | True |
| I-count-fails | FAIL | FAIL | True |
| I-count-satisfied | PASS | PASS | True |
| I-count-satisfied-incomplete | PASS | PASS | False |
| I-count-unresolved | UNRESOLVED | UNRESOLVED | False |
| I-separate-complete-support-fails | FAIL | FAIL | False |
| J-contract-fail-resolution-overlap | FAIL | UNRESOLVED | True |
| J-point-only-pass | PASS | UNRESOLVED | True |
| K-full-scope-failure-incomplete | FAIL | FAIL | False |
| K-incompatible-subset | UNAVAILABLE | UNAVAILABLE | False |
| L-payload-integrity | UNAVAILABLE | UNAVAILABLE | False |
| L-source-identity | UNAVAILABLE | UNAVAILABLE | False |

<a id="appendix-a-4"></a>

### A.4 Retained EWP and source-evidence supplement



All EWP locators below use `@4284e94`, meaning commit `4284e9460c8057053e95de7cfa2fb3590e68e9db`. **[D+]** identifies the primary arithmetic re-executed by the principal reviewer through the supplied `recompute.py` and `augment_results.py`; **[R] READ RETAINED** identifies native/source receipts and values read without rerunning their originating simulations. Reading or reducing retained results is not a fresh OpenFOAM execution. No private observation/deletion vectors, protected chemistry targets or new fitted predictions enter this supplement. Decimal displays are rounded; primary artifacts retain full precision.

#### A.4.1 SCI-MD-010/011: complete arms, support and diagnostics

Each complete arm covers the same **56 physical brews in 11 held-pressure-condition folds**, using directly measured line pressure and the source's `endpoint_100s` equilibrium mass-flow response. B0/B1 are immutable reused baselines in 011, so their repeated appearances are not independent experiments. E1 is the reduced machine-coupled Darcy arm of 010; P1 is the universal poroelastic arm of 011. **[D+]** Every complete stored per-brew error `S−D`, mean-condition RMSE, mean-condition bias and full normalized loss reproduced. The normalized loss is the mean over conditions of that condition's RMSE divided by its outer-training response range. It is a predictive-ranking metric with no independently justified practical-accuracy margin.

| Arm / task | Mean condition RMSE, g/s | Mean condition bias S−D, g/s | Full normalized loss | Low-pressure normalized loss | High-pressure normalized loss |
|---|---:|---:|---:|---:|---:|
| B0 / 010 and 011 | 0.5916020493 | approximately 0 | 0.3178679861 | 0.4508338157 | 0.1514445655 |
| B1 / 010 and 011 | 0.2936269557 | −0.0337841818 | 0.1532500175 | 0.1496007779 | 0.1977209884 |
| E1 / 010 | 0.5756564539 | −0.1598178436 | 0.2989424256 | 0.2619262097 | 0.3834551715 |
| P1 / 011 | 0.2742823595 | +0.0335854672 | 0.1445544290 | 0.1912977368 | 0.1099777864 |
| E2C / 011 | **No full aggregate adjudication** | unavailable | unavailable | no adjudicative aggregate | no adjudicative aggregate |

Low pressure comprises the five conditions through nominal 5 bar; high pressure comprises nominal 9, 11 and 13 bar. The remaining conditions still enter the full score. Low/high losses and the ranges below are retained fold-summary reductions **[R/C]**, not additional fits. Source locators: `EWP:docs/analysis/sci_md_010/FOLD_RESULTS.csv:L1-L34@4284e94`; `EWP:docs/analysis/sci_md_011/FOLD_RESULTS.csv:L1-L45@4284e94`; `EWP:docs/analysis/sci_md_011/AGGREGATE_RESULTS.csv:L1-L5@4284e94`. The 010 report independently tabulates the full physical and normalized ranges at `EWP:docs/analysis/sci_md_010/RESULT.md:L37-L59@4284e94`.

| Complete arm | Fold RMSE range, g/s | Normalized fold-loss range | Predicted low slope, g/s/bar | Predicted high slope, g/s/bar | Low/high sign gates | Predicted peak, nominal bar |
|---|---:|---:|---:|---:|---|---:|
| B0 | 0.1427194230–1.5036816216 | 0.0739506847–0.9024603082 | −0.0504206839 | +0.0065506413 | FAIL / FAIL | 1 |
| B1 | 0.1155835214–0.7271585992 | 0.0598901002–0.3767803649 | +0.3491836917 | −0.3400461982 | PASS / PASS | 8 |
| E1 | 0.0617469731–1.4916518906 | 0.0319944605–0.7729058615 | +0.2037432786 | +0.3285343911 | PASS / FAIL | 13 |
| P1 | 0.0820617599–0.4899397572 | 0.0425206549–0.2538643986 | +0.2959757535 | +0.0161203010 | PASS / FAIL | 13 |
| Observations | — | — | +0.5042068394 | −0.0655064126 | reference | 6 |

The retained Spearman correlations are B0 −1; B1 0.7363636364; E1/P1 0.4454545455. Their pairwise ordering concordances are 0, 0.7818181818 and 0.6363636364 respectively. These describe the selected held-fold predictions; they are not independent physical-validation scores. Low slopes, peak/ordering diagnostics and sign labels are **[R]**; high-pressure slopes were also independently recomputed **[D+]**. Locators: `EWP:docs/analysis/sci_md_010/PRESSURE_RESPONSE_DIAGNOSTICS.json:L71-L88@4284e94`, `EWP:docs/analysis/sci_md_010/PRESSURE_RESPONSE_DIAGNOSTICS.json:L159-L176@4284e94`, `EWP:docs/analysis/sci_md_010/PRESSURE_RESPONSE_DIAGNOSTICS.json:L247-L265@4284e94`; `EWP:docs/analysis/sci_md_011/PRESSURE_RESPONSE_DIAGNOSTICS.json:L293-L313@4284e94`.

**All declared bootstrap pairs and both panels are shown below.** Positive gain is the first arm's normalized loss minus the second arm's; positive therefore favors the second arm. The intervals use **2,000 replicates, seed 20260902, condition-then-paired-brew resampling, nearest-rank quantiles and no refit**. Full/low intervals for the complete pairs reproduced **[D+]**. P1's low point gain is the direct difference of the two retained low-pressure losses **[R/C]**.

| Task / pair | Full point gain | Full paired 95% interval | Low-pressure point gain | Low-pressure paired 95% interval | Status |
|---|---:|---:|---:|---:|---|
| 010 / B1−E1 | −0.1456924081 | [−0.2487589901, −0.0361631740] | −0.1123254318 | [−0.2669334833, +0.0297352042] | COMPLETE |
| 011 / B1−P1 | +0.0086955885 | [−0.0402107972, +0.0629656016] | −0.0416969589 | [−0.0828338941, −0.0032617161] | COMPLETE |
| 011 / B1−E2C | unavailable | unavailable | unavailable | unavailable | REQUIRED_MODEL_BLOCKED |
| 011 / P1−E2C | unavailable | unavailable | unavailable | unavailable | REQUIRED_MODEL_BLOCKED |

There are no additional B0 bootstrap-pair intervals in these frozen result packages. E2C retains **50 predictions in 10 complete conditions**, with the required 13-bar fold blocked. No partial mean substitutes for its full score or either missing required pairwise comparison. The low-pressure panel favors B1 over P1 even though P1 has the best descriptive full mean RMSE. Sources: `EWP:docs/analysis/sci_md_010/UNCERTAINTY_RESULTS.json:L1-L66@4284e94`; `EWP:docs/analysis/sci_md_011/UNCERTAINTY_RESULTS.json:L1-L52@4284e94`; `EWP:docs/analysis/sci_md_011/PAIRWISE_COMPARISONS.json:L1-L46@4284e94`; `EWP:docs/analysis/sci_md_011/RESULT.md:L7-L26@4284e94`.

The high-pressure observed-slope repeat-only standard uncertainty is **0.0137346389 g/s/bar** under fixed pressure coordinates and independent condition-mean errors, giving normal-approximation limits [−0.0924263, −0.0385865] around the −0.0655064 slope **[D+]**. Pressure uncertainty, systematic flow calibration, model-input/fitting uncertainty and their covariance are not included. Neither this calculation nor the frozen-prediction bootstrap is full `u_val` or an independent-campaign uncertainty estimate.

#### A.4.2 WP03_002 selected corrected-compaction comparison — READ RETAINED

**[R] READ RETAINED:** the following are the three selected corrected-compaction cases, not new trajectories or fresh trace reductions. These transient comparisons are distinct from SCI-MD-010/011's 100-second equilibrium response. The contract uses `solver_time=source_time+3.0 s`, density **965 kg/m³**, and linear interpolation without extrapolation over nominal source **0–27 s** / solver **3–30 s**. The actual common sampled endpoint is source **26.926927 s** / solver **29.926927 s**, with **270 temporal samples per pressure**. Those samples are not 270 independent experiments. Bias is the retained signed mean `S−D` on that support.

| Nominal pressure | Observable / unit | RMSE | Signed bias S−D | Model at common endpoint | Source at common endpoint |
|---|---|---:|---:|---:|---:|
| 5 bar | Pressure / bar | 0.306315041 | +0.287465670 | 5.000000000 | 4.624770000 |
| 5 bar | Flow / g/s | 0.471678179 | +0.020593696 | 0.585354185 | 1.598666000 |
| 5 bar | Mass / g | 4.761346940 | +4.091636059 | 15.956580521 | 12.970263000 |
| 9 bar | Pressure / bar | 0.113034710 | +0.084348119 | 9.000000000 | 8.836711000 |
| 9 bar | Flow / g/s | 0.516631177 | +0.457190791 | 0.680973127 | 0.739666000 |
| 9 bar | Mass / g | 9.964731235 | +8.583596270 | 20.313852248 | 5.022265000 |
| 11 bar | Pressure / bar | 0.359142001 | +0.354786381 | 11.000000000 | 10.577998000 |
| 11 bar | Flow / g/s | 0.535402476 | +0.490633810 | 0.685942927 | 0.663059000 |
| 11 bar | Mass / g | 10.491557540 | +9.104454023 | 20.865737111 | 4.645474000 |

Primary locators: `EWP:validation/wp03/WP03_002_CORRECTED_COMPARISON.json:L77-L349@4284e94` (5 bar), `EWP:validation/wp03/WP03_002_CORRECTED_COMPARISON.json:L350-L621@4284e94` (9 bar), `EWP:validation/wp03/WP03_002_CORRECTED_COMPARISON.json:L622-L897@4284e94` (11 bar), and `EWP:validation/wp03/WP03_002_CORRECTED_COMPARISON.json:L900-L941@4284e94` (metric contract and ordering); summary `EWP:docs/wp03/WP03_002_RESULTS.md:L45-L64@4284e94`. The JSON's `corrected_compaction[*].metrics.<observable>.full` supplies RMSE/bias; `endpoint` supplies the displayed endpoints.

For these three cases, direct inspection of the displayed endpoints gives model flow/mass ordering **11>9>5**, source ordering **5>9>11**, consistent with the retained Spearman **−1**. Retained source-interval flow coverages are **10.3704%, 13.3333%, 2.2222%** for 5/9/11 bar; these are source-band coverage fractions, not confidence levels or complete validation uncertainty. Broader ordering claims about accepted V3 Darcy, Forchheimer, or other permeability-evolution families were **not recomputed in this selected comparison** and remain **[S]** if quoted from an earlier synthesis. No such broader ordering inference is required for the three-case discrepancy above.

Separate retained numerical receipts report bounded conservation, serial/MPI and timestep checks; the corrected Picard gate uses flow change, pressure change and final linear residual. Continuous analytical closure remains a distinct solution-verification diagnostic. The maximum accepted corrected three-term gate ratio is **0.8588275788**, while continuous-closure/old-tolerance ratios can reach **8.354781336** at otherwise converged iterations. These are different metrics and do not justify treating the source comparison as physically validated. `EWP:docs/wp03/WP03_002_RESULTS.md:L113-L124@4284e94`; `EWP:solver/espressoWholePullFoam/espressoWholePullFoam.C:L2783-L2799@4284e94`.

#### A.4.3 Native-equation and compatibility locator clauses

The following compact cross-references supplement the capability finding rather than extend its claim scope:

- **Darcy and conservative flux:** `EWP:solver/espressoWholePullFoam/espressoWholePullFoam.C:L2834-L2846@4284e94`. **Forchheimer inversion/source correlation:** `EWP:solver/espressoWholePullFoam/forchheimerResistance.H:L10-L64@4284e94`. **Machine compliance/supply coupling:** `EWP:solver/espressoWholePullFoam/machineBoundaryModel.H:L291-L365@4284e94`.
- **Paired source, storage and species:** `EWP:solver/espressoWholePullFoam/espressoWholePullFoam.C:L3213-L3369@4284e94`; actual-scenario boundedness caveat at `EWP:docs/MODEL_SPECIFICATION.md:L103-L118@4284e94`. Inventory is per bed volume; concentration is per liquid volume. Release suppression does not guarantee a universal discrete `c≤Csat` bound.
- **Prescribed-flow and compaction exclusions:** `EWP:solver/espressoWholePullFoam/espressoWholePullFoam.C:L793-L928@4284e94`; **mechanical/transport-porosity separation:** `EWP:solver/espressoWholePullFoam/espressoWholePullFoam.C:L2589-L2760@4284e94`; **source-driven, rather than native-inventory-driven, dissolution coordinate:** `EWP:solver/espressoWholePullFoam/espressoWholePullFoam.C:L2334-L2365@4284e94`.
- **Viscosity's admitted combinations:** `EWP:solver/espressoWholePullFoam/espressoWholePullFoam.C:L749-L790@4284e94`; **wet-fraction conversion and table domain:** `EWP:solver/espressoWholePullFoam/aggregateViscosity.H:L25-L67@4284e94`. Bulk mode does not inherit radial/history support; these are 90°C, saturated, static-Darcy, aggregate-solute studies.
- **Finite-Φ closure and nonnegative derivative:** `EWP:solver/espressoWholePullFoam/poroelasticCompaction.H:L10-L150@4284e94`. Independent quadrature matches 21 retained normalized oracle values within **6.66134×10⁻¹⁶ [D+]**. That is scalar mathematical verification; no native trajectory was executed here.

#### A.4.4 MD008/009 stops and MD012 representability

| Task | Retained scope and independently reduced metric | Threshold / outcome | Supported consequence |
|---|---|---|---|
| MD008 | Receipts report 18 native inventory cases; 36 species metric rows. **[D+]** 24 rows fail shape invariance; maximum absolute normalized-shape difference **0.08011412484**; maximum pressure difference **0 Pa**. | Shape tolerance **10⁻⁶**; subsequent numerical/convergence and chemistry comparison stages blocked. | Inventory amplitude affects normalized fractions in this implemented source law. No scored empirical kinetics or equilibrium verdict follows. |
| MD009 | Receipts report 498 historical plus 96 supplemental native cases. **[D+]** Of 324 surrogate-validation metric rows, **117** exceed the limit; maximum relative error **0.08255430450**. | Frozen quadratic response surrogate limit **0.02**; surrogate qualification fails. | Downstream identifiability, precision, bundle and pilot judgments are withheld. This is not proof of general nonidentifiability; no observed-chemistry score was issued. |
| MD012 | **[D+]** At the frozen pair, **1/6** 13-bar brews is representable and **5/6** exceed a common coupled ceiling **12.7214635886 bar**. All evaluated closure inputs are in domain and finite. | The positive adapter drop **0.4208515908 bar** mitigates the failure. | Coupled-endpoint representability fails; a function-domain defect is not causal. Root recovery and turnover adequacy remain separate questions. |

MD008 locators: `EWP:validation/sci_md_008/INVENTORY_SCALE_INVARIANCE.csv:L1-L37@4284e94`; `EWP:validation/sci_md_008/FINAL_REPORT.md:L23-L39@4284e94`. MD009: `EWP:validation/sci_md_009/NONLINEAR_RESPONSE_VALIDATION.csv:L1-L325@4284e94`; `EWP:validation/sci_md_009/FINAL_REPORT.md:L1-L3@4284e94`. The counts of historical native executions are **[R] receipts**, not fresh verification of their unmounted raw trajectories.

For MD012, frozen `Pc=12.3006119990 bar`, `Qc=1.9573833549 g/s`. At frozen Qc, the maximum algebraic Pc threshold is **12.4886484105 bar**, an increase of **0.1880364115 bar / 1.528675%**. At frozen Pc, the endpoint Qc threshold is **3.4147489133 g/s**, an increase of **74.454784%**. The retained witness `Pc=12.4886484115 bar` is within existing bounds and supplies nonnegative margins for all six. It is explicitly **not a fit, prediction or score**. Formal identifiability remains unadjudicated. Positive scale changes retain the family's monotonicity; they do not rescue its required falling high-pressure response. `EWP:docs/analysis/sci_md_012/ROOT_FEASIBILITY.csv:L1-L7@4284e94`; `EWP:docs/analysis/sci_md_012/PARAMETER_FEASIBILITY.json:L120-L126@4284e94`, `EWP:docs/analysis/sci_md_012/PARAMETER_FEASIBILITY.json:L163-L214@4284e94`; `EWP:docs/analysis/sci_md_012/RESULT.md:L9-L21@4284e94`.

#### A.4.5 Porosity materiality with the correct units

**[D+]** The two eligible porosity supports' absolute relative effects reproduce the primary JSON. They are source-conditioned sensitivity supports, not validated wet-puck material distributions. There are zero EWP-compatible permeability supports and three stress-only permeability representations; Figure 12's 50 dry rows qualify an operator and add zero propagated supports. The fixed-dose, mass-conserving 9-bar rule is `max(0.05, 10×0.001196176252)=0.05`; the **5% engineering floor** is owner-frozen, not publication-derived.

| Observable / unit | Baseline value | Wadsworth total-XCT value | Absolute relative effect | Vaca Table C1 value | Absolute relative effect |
|---|---:|---:|---:|---:|---:|
| First-drip time / s | 4.711696185 | 9.272604057 | 96.799702% | 3.061241201 | 35.028892% |
| Steady outlet flow / m³/s | 1.482675972×10⁻⁶ | 1.115960781×10⁻⁶ | 24.733333% | 1.779211166×10⁻⁶ | 20.000000% |
| Effective hydraulic resistance / Pa·s/m³ | 6.070105790×10¹¹ | 8.064799544×10¹¹ | 32.860939% | 5.058421492×10¹¹ | 16.666667% |
| Final **water** mass / kg | 0.03618205781 | 0.02232137734 | 38.308160% | 0.04625219953 | 27.831866% |

Both supports pass the bundle's materiality rule. The target-yield timing metric is explicitly not comparable for the Wadsworth case because the target is not reached on retained support; Vaca changes target reachability. It is not silently included as an ordinary paired timing error. The report's concrete correction is dimensional: `RESULT.md:L19-L20` displays numbers such as **0.967997** beneath `first_drip_time_s`, but those numbers are **dimensionless absolute relative effects**, not times. The JSON separates source value, baseline value and effect correctly. No gate or scientific input needs changing. `EWP:docs/analysis/ewp_porosity_permeability_prior_001/RESULT.md:L13-L32@4284e94`; `EWP:docs/analysis/ewp_porosity_permeability_prior_001/POROSITY_MATERIALITY.json:L18-L25@4284e94`, `EWP:docs/analysis/ewp_porosity_permeability_prior_001/POROSITY_MATERIALITY.json:L32-L80@4284e94`, `EWP:docs/analysis/ewp_porosity_permeability_prior_001/POROSITY_MATERIALITY.json:L87-L136@4284e94`.

<a id="appendix-a-5"></a>

### A.5 Complete public aggregate arm and panel tables



[X/R/D+] R is each task’s declared nested average of weighted shot RMSE, B its signed mean error, and A its mean absolute shot bias; therefore A is generally not abs(B). The principal reviewer reaggregated public condition means, not original private shots. Undefined full-flow scores remain undefined. Counts are original repeated physical shots/windows, not independent observations across model rows. Numerical allowances and paired gains are in A.6 and the complete scripts.

#### sci_md_mass_delivery_006

Original disposition: `LEARNED_TWO_ASSAY_MAPPING_EARNED`. Source: `PW:docs/analysis/sci_md_mass_delivery_006/RESULTS.json:L1-L1590@9dd456b`.

| Panel | Arm | Units | R | B | A | Original adequacy | Shots / windows |
| --- | --- | --- | --- | --- | --- | --- | --- |
| flow_stress | C0 | pp | unavailable | unavailable | unavailable | SOURCE_SUPPORT_INCOMPLETE | 6 / 24 |
| flow_stress | C1 | pp | unavailable | unavailable | unavailable | SOURCE_SUPPORT_INCOMPLETE | 6 / 24 |
| flow_stress | C2 | pp | unavailable | unavailable | unavailable | SOURCE_SUPPORT_INCOMPLETE | 6 / 24 |
| flow_stress | FIRST_ASSAY_EMPIRICAL | pp | unavailable | unavailable | unavailable | SOURCE_SUPPORT_INCOMPLETE | 6 / 24 |
| primary | C0 | pp | 0.652055304 | -0.410419087 | 0.410419087 | PASS | 12 / 48 |
| primary | C1 | pp | 0.597587226 | -0.400204688 | 0.400204688 | FAIL | 12 / 48 |
| primary | C2 | pp | 0.480034144 | -0.395566834 | 0.395566834 | PASS | 12 / 48 |
| primary | FIRST_ASSAY_EMPIRICAL | pp | 0.779600820 | -0.665653605 | 0.665653605 | FAIL | 12 / 48 |
| temperature_stress | C0 | pp | 0.444403238 | -0.279829117 | 0.279829117 | PASS | 6 / 24 |
| temperature_stress | C1 | pp | 0.450276620 | -0.324284632 | 0.324284632 | PASS | 6 / 24 |
| temperature_stress | C2 | pp | 0.332809539 | -0.256546866 | 0.256546866 | PASS | 6 / 24 |
| temperature_stress | FIRST_ASSAY_EMPIRICAL | pp | 0.627070411 | -0.487456830 | 0.487456830 | FAIL | 6 / 24 |

#### sci_md_caffeine_delivery_001

Original disposition: `SIMPLER_CAFFEINE_PREDICTOR_ADEQUATE_NO_EARNED_COMPLEXITY`. Source: `PW:docs/analysis/sci_md_caffeine_delivery_001/RESULTS.json:L1-L1567@9dd456b`.

| Panel | Arm | Units | R | B | A | Original adequacy | Shots / windows |
| --- | --- | --- | --- | --- | --- | --- | --- |
| flow_stress | D0 | mg/g | unavailable | unavailable | unavailable | NOT_ADJUDICATED_INCOMPLETE_SUPPORT | 6 / 24 |
| flow_stress | S0 | mg/g | unavailable | unavailable | unavailable | NOT_ADJUDICATED_INCOMPLETE_SUPPORT | 6 / 24 |
| flow_stress | S1 | mg/g | unavailable | unavailable | unavailable | NOT_ADJUDICATED_INCOMPLETE_SUPPORT | 6 / 24 |
| flow_stress | S2 | mg/g | unavailable | unavailable | unavailable | NOT_ADJUDICATED_INCOMPLETE_SUPPORT | 6 / 24 |
| primary | D0 | mg/g | 0.192258153 | -0.038568088 | 0.078832573 | PASS | 12 / 48 |
| primary | S0 | mg/g | 0.215565189 | -0.140025144 | 0.140025144 | PASS | 12 / 48 |
| primary | S1 | mg/g | 0.152188938 | -0.013100844 | 0.078570649 | PASS | 12 / 48 |
| primary | S2 | mg/g | 0.125168095 | -0.056349458 | 0.088412899 | PASS | 12 / 48 |
| temperature_stress | D0 | mg/g | 0.120398037 | -0.019367080 | 0.070562090 | PASS | 6 / 24 |
| temperature_stress | S0 | mg/g | 0.166697704 | -0.118762948 | 0.118762948 | PASS | 6 / 24 |
| temperature_stress | S1 | mg/g | 0.145712856 | 0.005294760 | 0.070482364 | PASS | 6 / 24 |
| temperature_stress | S2 | mg/g | 0.125159081 | -0.030072536 | 0.081111489 | PASS | 6 / 24 |

#### sci_md_trigonelline_delivery_001

Original disposition: `TRIGONELLINE_MASS_SHAPE_EARNED`. Source: `PW:docs/analysis/sci_md_trigonelline_delivery_001/RESULTS.json:L1-L930@9dd456b`.

| Panel | Arm | Units | R | B | A | Original adequacy | Shots / windows |
| --- | --- | --- | --- | --- | --- | --- | --- |
| flow_stress | TR-D0 | mg/g | unavailable | unavailable | unavailable | INCOMPLETE_SUPPORT | 6 / 24 |
| flow_stress | TR-K0 | mg/g | unavailable | unavailable | unavailable | FAIL | 6 / 24 |
| primary | TR-D0 | mg/g | 0.134549535 | -0.026655169 | 0.044153374 | PASS | 12 / 48 |
| primary | TR-K0 | mg/g | 0.729502678 | -0.029361182 | 0.081309882 | FAIL | 12 / 48 |
| temperature_stress | TR-D0 | mg/g | 0.074443763 | -0.044167198 | 0.065578108 | PASS | 6 / 24 |
| temperature_stress | TR-K0 | mg/g | 0.790872574 | -0.013429864 | 0.103166529 | FAIL | 6 / 24 |

#### sci_md_5cqa_delivery_001

Original disposition: `TESTED_FIVE_CQA_FAMILIES_INADEQUATE`. Source: `PW:docs/analysis/sci_md_5cqa_delivery_001/RESULTS.json:L1-L930@9dd456b`.

| Panel | Arm | Units | R | B | A | Original adequacy | Shots / windows |
| --- | --- | --- | --- | --- | --- | --- | --- |
| flow_stress | D0 | mg/g | unavailable | unavailable | unavailable | FAIL | 6 / 24 |
| flow_stress | E0 | mg/g | unavailable | unavailable | unavailable | FAIL | 6 / 24 |
| primary | D0 | mg/g | 0.363520937 | -0.340293651 | 0.340293651 | FAIL | 12 / 48 |
| primary | E0 | mg/g | 0.364510463 | -0.350130048 | 0.350130048 | FAIL | 12 / 48 |
| temperature_stress | D0 | mg/g | 0.381575187 | -0.352122634 | 0.352122634 | FAIL | 6 / 24 |
| temperature_stress | E0 | mg/g | 0.397964934 | -0.373730970 | 0.373730970 | FAIL | 6 / 24 |

#### sci_md_5cqa_tds_001

Original disposition: `TESTED_TDS_CONDITIONED_FIVE_CQA_FAMILIES_INADEQUATE`. Source: `PW:docs/analysis/sci_md_5cqa_tds_001/RESULTS.json:L1-L2293@9dd456b`.

| Panel | Arm | Units | R | B | A | Original adequacy | Shots / windows |
| --- | --- | --- | --- | --- | --- | --- | --- |
| flow_stress | D0 | mg/g | unavailable | unavailable | unavailable | FAIL | 6 / 24 |
| flow_stress | E0 | mg/g | unavailable | unavailable | unavailable | FAIL | 6 / 24 |
| flow_stress | S0 | mg/g | unavailable | unavailable | unavailable | FAIL | 6 / 24 |
| flow_stress | S1 | mg/g | unavailable | unavailable | unavailable | FAIL | 6 / 24 |
| flow_stress | S2 | mg/g | unavailable | unavailable | unavailable | FAIL | 6 / 24 |
| primary | D0 | mg/g | 0.363520937 | -0.340293651 | 0.340293651 | FAIL | 12 / 48 |
| primary | E0 | mg/g | 0.364510463 | -0.350130048 | 0.350130048 | FAIL | 12 / 48 |
| primary | S0 | mg/g | 0.401483179 | -0.378501430 | 0.378501430 | FAIL | 12 / 48 |
| primary | S1 | mg/g | 0.381662959 | -0.328948808 | 0.328948808 | FAIL | 12 / 48 |
| primary | S2 | mg/g | 0.410419926 | -0.364421908 | 0.364421908 | FAIL | 12 / 48 |
| temperature_stress | D0 | mg/g | 0.381575187 | -0.352122634 | 0.352122634 | FAIL | 6 / 24 |
| temperature_stress | E0 | mg/g | 0.397964934 | -0.373730970 | 0.373730970 | FAIL | 6 / 24 |
| temperature_stress | S0 | mg/g | 0.423576952 | -0.381909087 | 0.381909087 | FAIL | 6 / 24 |
| temperature_stress | S1 | mg/g | 0.420996898 | -0.340772904 | 0.340772904 | FAIL | 6 / 24 |
| temperature_stress | S2 | mg/g | 0.448422422 | -0.372552909 | 0.372552909 | FAIL | 6 / 24 |

#### sci_md_5cqa_assay_001

Original disposition: `TESTED_FIRST_ASSAY_FIVE_CQA_FAMILIES_INADEQUATE`. Source: `PW:docs/analysis/sci_md_5cqa_assay_001/RESULTS.json:L1-L1898@9dd456b`.

| Panel | Arm | Units | R | B | A | Original adequacy | Shots / windows |
| --- | --- | --- | --- | --- | --- | --- | --- |
| flow_stress | A1 | mg/g | unavailable | unavailable | unavailable | FAIL | 6 / 24 |
| flow_stress | D0 | mg/g | unavailable | unavailable | unavailable | FAIL | 6 / 24 |
| flow_stress | E0 | mg/g | unavailable | unavailable | unavailable | FAIL | 6 / 24 |
| flow_stress | L1 | mg/g | unavailable | unavailable | unavailable | FAIL | 6 / 24 |
| primary | A1 | mg/g | 0.365269251 | 0.210862047 | 0.220421504 | FAIL | 12 / 48 |
| primary | D0 | mg/g | 0.363520937 | -0.340293651 | 0.340293651 | FAIL | 12 / 48 |
| primary | E0 | mg/g | 0.364510463 | -0.350130048 | 0.350130048 | FAIL | 12 / 48 |
| primary | L1 | mg/g | 0.354341440 | -0.203434452 | 0.203434452 | FAIL | 12 / 48 |
| temperature_stress | A1 | mg/g | 0.323881345 | 0.199138423 | 0.207469603 | FAIL | 6 / 24 |
| temperature_stress | D0 | mg/g | 0.381575187 | -0.352122634 | 0.352122634 | FAIL | 6 / 24 |
| temperature_stress | E0 | mg/g | 0.397964934 | -0.373730970 | 0.373730970 | FAIL | 6 / 24 |
| temperature_stress | L1 | mg/g | 0.326164284 | -0.212770354 | 0.212770354 | FAIL | 6 / 24 |

#### sci_md_5cqa_assay_002

Original disposition: `TESTED_EARLY_ASSAY_FAMILIES_INADEQUATE`. Source: `PW:docs/analysis/sci_md_5cqa_assay_002/RESULTS.json:L1-L3352@9dd456b`.

| Panel | Arm | Units | R | B | A | Original adequacy | Shots / windows |
| --- | --- | --- | --- | --- | --- | --- | --- |
| flow_stress | L12 | mg/g | unavailable | unavailable | unavailable | FAIL | 6 / 24 |
| flow_stress | L1M | mg/g | unavailable | unavailable | unavailable | FAIL | 6 / 24 |
| flow_stress | L2M | mg/g | unavailable | unavailable | unavailable | FAIL | 6 / 24 |
| primary | L12 | mg/g | 0.297495166 | -0.254372362 | 0.254372362 | FAIL | 12 / 48 |
| primary | L1M | mg/g | 0.343708141 | -0.215687390 | 0.215687390 | FAIL | 12 / 48 |
| primary | L2M | mg/g | 0.349467750 | -0.269648531 | 0.269648531 | FAIL | 12 / 48 |
| temperature_stress | L12 | mg/g | 0.318352057 | -0.255187465 | 0.255187465 | FAIL | 6 / 24 |
| temperature_stress | L1M | mg/g | 0.317237236 | -0.242096411 | 0.242096411 | FAIL | 6 / 24 |
| temperature_stress | L2M | mg/g | 0.367115067 | -0.276350513 | 0.276350513 | FAIL | 6 / 24 |

#### sci_md_mass_delivery_007

Original disposition: `FROZEN_CONDITIONAL_TRANSFER_INADEQUATE_ON_DECLARED_COHORT`. Source: `PW:docs/analysis/sci_md_mass_delivery_007/RESULTS.json:L1-L359@9dd456b`.

| Panel | Arm | Units | R | B | A | Original adequacy | Shots / windows |
| --- | --- | --- | --- | --- | --- | --- | --- |
| primary | C0 | pp | 0.965470231 | 0.830450502 | 0.831110292 | FAIL | 11 / see task support |
| primary | C1 | pp | 1.001235186 | 0.969673066 | 0.969673066 | FAIL | 11 / see task support |
| primary | C2 | pp | 0.599148861 | 0.509950024 | 0.532634505 | FAIL | 11 / see task support |

#### sci_md_mass_delivery_008

Original disposition: `ADAPTATION_ADEQUATE_INCREMENT_NOT_ESTABLISHED`. Source: `PW:docs/analysis/sci_md_mass_delivery_008/RESULTS.json:L1-L561@9dd456b`.

| Panel | Arm | Units | R | B | A | Original adequacy | Shots / windows |
| --- | --- | --- | --- | --- | --- | --- | --- |
| primary | A0 | pp | 0.600495775 | 0.037845460 | 0.499012855 | FAIL | 11 / see task support |
| primary | A2 | pp | 0.483157724 | 0.012837522 | 0.346409646 | PASS | 11 / see task support |
| primary | F2 | pp | 0.599148861 | 0.509950024 | 0.532634505 | FAIL | 11 / see task support |
| primary | M | pp | 0.582649277 | -0.072253238 | 0.455719143 | FAIL | 11 / see task support |

```json
{
  "eligible_physical_shots": 11,
  "ordered_pairs": 110,
  "unique_suffix_windows": 55,
  "original_shots": 13,
  "prediction_slots_per_arm": 550
}
```

#### All complete primary and stress comparator gains

Positive gain favors the candidate. Positive ΔA means worsened mean absolute bias. Win counts in this table are arithmetic point wins; definite interval-qualified wins and full original conjunctions remain controlled by A.6 and each protocol.

| Task | Panel | Candidate / reference | Gain | Relative gain % | ΔA | Numerical gain allowance | Point wins / conditions | Units |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| sci_md_mass_delivery_006 | primary | C2 / C0 | 0.172021160 | 26.38138 | -0.014852253 | 6.21589e-12 | 3/4 | pp |
| sci_md_mass_delivery_006 | primary | C2 / C1 | 0.117553081 | 19.67128 | -0.004637854 | 6.21614e-12 | 3/4 | pp |
| sci_md_mass_delivery_006 | primary | C2 / FIRST_ASSAY_EMPIRICAL | 0.299566676 | 38.42565 | -0.270086771 | 3.3975e-12 | 4/4 | pp |
| sci_md_mass_delivery_006 | temperature_stress | C2 / C0 | 0.111593699 | 25.11091 | -0.023282251 | 6.19483e-12 | 2/2 | pp |
| sci_md_mass_delivery_006 | temperature_stress | C2 / C1 | 0.117467080 | 26.08776 | -0.067737765 | 6.19274e-12 | 2/2 | pp |
| sci_md_mass_delivery_006 | temperature_stress | C2 / FIRST_ASSAY_EMPIRICAL | 0.294260872 | 46.92629 | -0.230909964 | 3.38545e-12 | 2/2 | pp |
| sci_md_caffeine_delivery_001 | primary | S2 / S1 | 0.027020843 | 17.75480 | 0.009842251 | 5.71875e-11 | 2/4 | mg_g |
| sci_md_caffeine_delivery_001 | primary | S2 / D0 | 0.067090058 | 34.89582 | 0.009580327 | 5.71866e-11 | 3/4 | mg_g |
| sci_md_caffeine_delivery_001 | primary | S2 / S0 | 0.090397094 | 41.93492 | -0.051612245 | 5.71825e-11 | 4/4 | mg_g |
| sci_md_caffeine_delivery_001 | temperature_stress | S2 / S1 | 0.020553775 | 14.10567 | 0.010629124 | 5.7101e-11 | 2/2 | mg_g |
| sci_md_caffeine_delivery_001 | temperature_stress | S2 / D0 | -0.004761044 | -3.95442 | 0.010549399 | 5.70999e-11 | 1/2 | mg_g |
| sci_md_caffeine_delivery_001 | temperature_stress | S2 / S0 | 0.041538623 | 24.91853 | -0.037651459 | 5.70962e-11 | 2/2 | mg_g |
| sci_md_5cqa_assay_002 | primary | L12 / L1M | 0.046212975 | 13.44541 | 0.038684972 | 5.71157e-11 | 4/4 | mg_g |
| sci_md_5cqa_assay_002 | primary | L12 / L2M | 0.051972584 | 14.87193 | -0.015276169 | 5.71134e-11 | 4/4 | mg_g |
| sci_md_5cqa_assay_002 | temperature_stress | L12 / L1M | -0.001114821 | -0.35142 | 0.013091055 | 5.70299e-11 | 1/2 | mg_g |
| sci_md_5cqa_assay_002 | temperature_stress | L12 / L2M | 0.048763010 | 13.28276 | -0.021163048 | 5.70286e-11 | 2/2 | mg_g |
| sci_md_5cqa_assay_002 | primary | L2M / L1M | -0.005759608 | -1.67573 | 0.053961141 | 5.7115e-11 | 1/4 | mg_g |
| sci_md_5cqa_assay_002 | temperature_stress | L2M / L1M | -0.049877832 | -15.72257 | 0.034254103 | 5.7029e-11 | 0/2 | mg_g |
| sci_md_trigonelline_delivery_001 | primary | TR-D0 / TR-K0 | 0.594953143 | 81.55599 | -0.037156508 | 5.70693e-11 | 4/4 | mg_g |
| sci_md_trigonelline_delivery_001 | temperature_stress | TR-D0 / TR-K0 | 0.716428811 | 90.58714 | -0.037588421 | 5.69858e-11 | 2/2 | mg_g |

#### MASS001–003 and stopping controls

PW @ `9dd456be7fd797b9cda0a2bbf50d1ac717d72835`. [X/D+] Principal reviewer reran the public reducer. Reaggregated condition means, not private shot reconstruction. The embedded reducer regenerates every public condition, panel, comparator and original decision from the pinned source JSON.

| Task | Panel | Arm | R (pp) | Signed B (pp) | Mean abs B (pp) | Original adequacy |
| --- | --- | --- | ---: | ---: | ---: | --- |
| 001 | flow_ramp | BOUNDARY_AWARE_EMPIRICAL | undefined | undefined | undefined | FAIL |
| 001 | flow_ramp | MASS | undefined | undefined | undefined | FAIL |
| 001 | flow_ramp | TIME | undefined | undefined | undefined | FAIL |
| 001 | flow_ramp | TIME_sqrt | undefined | undefined | undefined | FAIL |
| 001 | flow_ramp | TIME_u2 | undefined | undefined | undefined | FAIL |
| 001 | primary | BOUNDARY_AWARE_EMPIRICAL | 1.0328808999 | 0.272208105738 | 0.276946633628 | FAIL |
| 001 | primary | MASS | 1.02593941184 | 0.271407727607 | 0.271560864765 | FAIL |
| 001 | primary | TIME | 1.11973490205 | 0.711001440837 | 0.918690621317 | FAIL |
| 001 | primary | TIME_sqrt | 1.27021377496 | 0.805366794004 | 1.03642055545 | FAIL |
| 001 | primary | TIME_u2 | 1.03262771436 | 0.618603222527 | 0.808554397848 | FAIL |
| 001 | temperature_ramp | BOUNDARY_AWARE_EMPIRICAL | 0.855579506036 | 0.219551474655 | 0.22301502188 | FAIL |
| 001 | temperature_ramp | MASS | 0.840938185826 | 0.210444058226 | 0.218677538446 | PASS |
| 001 | temperature_ramp | TIME | 0.968558736204 | 0.823669356218 | 0.823669356218 | FAIL |
| 001 | temperature_ramp | TIME_sqrt | 1.07244644672 | 0.915627884556 | 0.915627884556 | FAIL |
| 001 | temperature_ramp | TIME_u2 | 0.904069988064 | 0.731846784028 | 0.731846784028 | FAIL |
| 002 | primary | M0 | 1.02593941184 | 0.271407727607 | 0.271560864765 | FAIL |
| 002 | primary | MF | 1.03158649462 | 0.261212243144 | 0.267004151055 | FAIL |
| 002 | primary | MT | 1.03283124706 | 0.27876747147 | 0.287738486088 | FAIL |
| 002 | primary | MTF | 1.03818839656 | 0.268557195944 | 0.280478456871 | FAIL |
| 002 | primary | SETTING_AWARE_EMPIRICAL | 1.05334385459 | 0.244963969033 | 0.259395794945 | FAIL |
| 003 | primary | ANCHORED_EMPIRICAL | 0.776936999197 | -0.381107875888 | 0.381107875888 | PASS |
| 003 | primary | ANCHORED_MASS | 0.770456049335 | -0.441873702464 | 0.441873702464 | FAIL |
| 003 | primary | ANCHORED_SETTING_EMPIRICAL | 0.902826824849 | -0.166097640991 | 0.19059110834 | FAIL |
| 003 | primary | ANCHOR_PERSISTENCE | 13.9195978584 | 13.3352882404 | 13.3352882404 | FAIL |
| 003 | primary | UNANCHORED_EMPIRICAL | 0.953555266798 | 0.0530276898312 | 0.158148476968 | FAIL |
| 003 | primary | UNANCHORED_MASS | 0.911882717063 | 0.0299191257412 | 0.1369267221 | FAIL |
| 003 | primary | UNANCHORED_SETTING_EMPIRICAL | 1.06363262619 | 0.115220779358 | 0.167789113392 | FAIL |

MASS001 flow means remain undefined; original failure labels are retained. MASS002 C03/C04/C07/C08 remain NOT_ADJUDICATED_VARIABLE_SETTING_INPUT. MASS003 has no secondary panel in its public result; none is invented.

##### All mass-stop panels and controls

The following statistics are retained. Only public count partitions and ratios were independently checked; underlying feasibility, oracle and regret were not rerun.

| Panel | Arm | Successes/N | Missed feasible abstentions | Exact oracle choices | Median/max successful regret (g) |
| --- | --- | ---: | ---: | ---: | ---: |
| PRIMARY | C0 | 11/11 | 0 | 11 | 0/0 |
| PRIMARY | C2 | 11/11 | 0 | 11 | 0/0 |
| PRIMARY | FIXED | 11/11 | 0 | 0 | 3.01/3.72 |
| S1 | C0 | 11/11 | 0 | 11 | 0/0 |
| S1 | C2 | 11/11 | 0 | 11 | 0/0 |
| S1 | FIXED | 11/11 | 0 | 9 | 0/2.87 |
| S2 | C0 | 11/11 | 0 | 11 | 0/0 |
| S2 | C2 | 11/11 | 0 | 11 | 0/0 |
| S2 | FIXED | 10/11 | 1 | 0 | 6.235/7.54 |
| S3 | C0 | 11/11 | 0 | 11 | 0/0 |
| S3 | C2 | 11/11 | 0 | 11 | 0/0 |
| S3 | FIXED | 10/11 | 1 | 0 | 6.145/6.56 |
| S4 | C0 | 11/11 | 0 | 11 | 0/0 |
| S4 | C2 | 11/11 | 0 | 11 | 0/0 |
| S4 | FIXED | 11/11 | 0 | 0 | 3.01/3.72 |

Every arm/panel has zero false-feasible and numerically unresolved decisions. Eleven physical shots are repeatedly reused across these fifteen entries; this is not 165 independent trials.

##### Public comparison audit and scope

{
  "complete_panel_arm_count": 22,
  "unavailable_panel_arm_count_preserved": 5,
  "condition_summary_count": 88,
  "panel_metric_checks": 286,
  "comparison_component_checks": 50,
  "maximum_absolute_metric_delta": 4.440892098500626e-16,
  "maximum_absolute_comparison_delta": 0.0,
  "mass_stop_panel_arm_count": 15,
  "mass_stop_public_partition_and_rate_checks": 105
}

MASS006 temperature C2 versus FIRST_ASSAY_EMPIRICAL: recomputed full baseline gain **0.2942608719599868 pp**, retained whole-shot deletion range **0.258942–0.327771 pp**, relative range **0.439412–0.495996**. Full flow gains/deletion ranges remain unavailable against all three comparators. Source: PW `docs/analysis/sci_md_mass_uncertainty_001/RESULTS.md:L133–148@9dd456b`.

Source identities are given in A.8; the full reducer is in Appendix B.

#### MASS001–003 complete predeclared comparisons

| Task | Candidate / reference | Gain pp | Relative gain % | ΔA pp | Definite condition wins | Competitive | Material gain | Original gain subpredicates |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| sci_md_mass_delivery_001 | MASS / BOUNDARY_AWARE_EMPIRICAL | 0.006941488 | 0.67205 | -0.005385769 | 1 | FAIL | FAIL | ['FAIL', 'FAIL', 'PASS', 'FAIL'] |
| sci_md_mass_delivery_001 | MASS / TIME | 0.093795490 | 8.37658 | -0.647129757 | 1 | FAIL | FAIL | ['FAIL', 'FAIL', 'PASS', 'FAIL'] |
| sci_md_mass_delivery_001 | MASS / TIME_sqrt | 0.244274363 | 19.23096 | -0.764859691 | 2 | FAIL | FAIL | ['PASS', 'FAIL', 'PASS', 'FAIL'] |
| sci_md_mass_delivery_001 | MASS / TIME_u2 | 0.006688303 | 0.64770 | -0.536993533 | 1 | FAIL | FAIL | ['FAIL', 'FAIL', 'PASS', 'FAIL'] |
| sci_md_mass_delivery_002 | MTF / M0 | -0.012248985 | -1.19393 | 0.008917592 | 2 | FAIL | FAIL | ['FAIL', 'FAIL', 'PASS', 'FAIL'] |
| sci_md_mass_delivery_002 | MTF / SETTING_AWARE_EMPIRICAL | 0.015155458 | 1.43879 | 0.021082662 | 2 | FAIL | FAIL | ['FAIL', 'FAIL', 'PASS', 'FAIL'] |
| sci_md_mass_delivery_003 | ANCHORED_MASS / ANCHORED_EMPIRICAL | 0.006480950 | 0.83417 | 0.060765827 | 1 | FAIL | FAIL | ['FAIL', 'FAIL', 'PASS', 'FAIL'] |
| sci_md_mass_delivery_003 | ANCHORED_MASS / ANCHORED_SETTING_EMPIRICAL | 0.132370776 | 14.66181 | 0.251282594 | 4 | FAIL | FAIL | ['PASS', 'FAIL', 'FAIL', 'PASS'] |
| sci_md_mass_delivery_003 | ANCHORED_MASS / ANCHOR_PERSISTENCE | 13.149141809 | 94.46495 | -12.893414538 | 4 | FAIL | PASS | ['PASS', 'PASS', 'PASS', 'PASS'] |
| sci_md_mass_delivery_003 | ANCHORED_MASS / UNANCHORED_MASS | 0.141426668 | 15.50930 | 0.304946980 | 4 | FAIL | FAIL | ['PASS', 'FAIL', 'FAIL', 'PASS'] |

Original bootstrap/decomposition diagnostics for these early tasks were not independently replayed from private rows. The original condition, bias and gain failures remain sufficient to reject a global “just above RMSE threshold” interpretation. A.6 identifies the remaining prospective reanalysis scope.

<a id="appendix-a-6"></a>

### A.6 Detailed sensitivity and decision-predicate supplement



This supplement distinguishes the **original contractual predicates**, **public aggregate arithmetic**, and **retained finite sensitivity results**. Here, gain is ΔR = R(reference) − R(candidate); positive favors the candidate. A is the nested mean of **absolute individual-shot bias**, with absolute value taken before averaging; ΔA = A(candidate) − A(reference), so positive denotes deterioration. MASS-008 takes the absolute bias within each ordered pair before averaging. A is not the absolute value of the panel's signed B, and neither quantity is the 5CQA contribution from squared mean shot error.

**Evidence status:** baseline arithmetic and the 32 rheology rows use the principal reviewer's checked public reductions **[X/D+]**; original decisions are inspected historical contracts **[R]**. All empirical physical-shot deletion ranges, signs, decomposition sensitivities and individual-shot sign counts below are **[S: retained private reduction, not independently replayed]**. Their public summaries and reduction logic were inspected; this review did not access or reconstruct the private observation, prediction or deletion vectors. These finite extrema describe the specified retained trajectories conditional on frozen fits. They are **not confidence intervals**, population coverage bounds, assay uncertainty or prediction intervals for future shots. No private family is pooled with another family.

Full binary64 values are retained below except relative percentages, which are displayed to ten significant digits. Source keys and row line pins resolve through the source register at the end of this section.

#### A.6.1 MASS-006, MASS-007 and MASS-008 have different count and adequacy rules

| Task | Estimand and physical support | Adequacy and coverage conjunction | Increment and count conjunction | Original result |
|---|---|---|---|---|
| 006 | 12 primary shots; four conditions; 48 suffix windows. R and A are equal-shot means within condition, then equal-condition means. | A: **every** C2 primary condition has R ≤ 1.00 pp and A ≤ 0.50 pp; complete qualified scope. | B: C2/C1 gain ≥ 0.10 pp **and** ≥ 15%, ≥ 3 of 4 definite condition wins, ΔA ≤ 0.10 pp. C: A passes and C2 deteriorates by no more than 0.10 pp in **either R or A against each C0 and C1**. D: B's full material-gain conjunction against FIRST_ASSAY_EMPIRICAL on exact common legacy support. | All A/B/C/D PASS. C0 is also adequate. C0 gain is a separately retained secondary comparison; it does not replace the C1 or legacy requirement. |
| 007 | 11 eligible physical shots from 13 qualified; 55 positive suffix vials. Equal-shot summaries, without invented condition groups. | Coverage: N ≥ 10 and every declared suffix window supported and numerically qualified for **all three arms**. Arm A: mean R ≤ 1.00 pp, mean A ≤ 0.50 pp **and** ≥ ceil(0.75N) individual shots satisfying **both** limits: 9 of 11. | I0 = C2/C0 and I1 = C2/C1: each needs gain ≥ 0.10 pp **and** ≥ 15%, ≥ 9 of 11 definite paired-shot R wins and ΔA ≤ 0.10 pp. Both increments are needed for second-summary complexity. | All arms fail A: adequate-shot counts C0 3/11, C1 2/11, C2 7/11, required 9. C2 mean A = 0.5326345052494331 pp. I0/I1 both PASS with 11/11 wins. |
| 008 | The same 11 physical identities; 110 ordered off-diagonal pairs; 55 unique suffix observations and 550 prediction slots per arm. These are repeated uses of 11 shots. | Pair: R ≤ 1.00 pp and abs(B) ≤ 0.50 pp. Calibration choice: its row mean R ≤ 1.00, mean A ≤ 0.50 **and** ≥ 8 of 10 adequate target pairs. Arm: overall R ≤ 1.00, A ≤ 0.50 **and** ≥ 9 of 11 adequate calibration choices. | Each of I_CAL = A2/F2, I_CHEM = A2/A0, I_LOCAL = A2/M needs gain ≥ 0.10 pp **and** ≥ 15%, ≥ 9 of 11 definite **target-column** wins, ≥ 9 of 11 definite **calibration-row** wins, and ΔA ≤ 0.10 pp. | Only A2 passes A: 9/11 adequate calibration choices, versus F2 0/11, A0 3/11 and M 4/11. All three increments FAIL. A2's 81/110 adequate pairs do not fail an additional overall gate; the generic metadata value required_adequate_pairs = 83 is unused. |

Sources: `PW:docs/analysis/sci_md_mass_delivery_006/PROTOCOL.md:L85-L114@9dd456b`; `PW:docs/analysis/sci_md_mass_delivery_007/PROTOCOL.md:L89-L116@9dd456b`; `PW:docs/analysis/sci_md_mass_delivery_008/PROTOCOL.md:L46-L95@9dd456b`; `PW:docs/analysis/sci_md_mass_uncertainty_001/RESULTS.md:L44-L82@9dd456b`. These are task working budgets, not experimentally estimated errors or universal espresso-quality limits. Numerical allowances are propagated to the exact weighted summaries and paired comparisons. Strict disjoint R bounds establish a definite win; unresolved threshold overlap and original denominators are retained. A reference R lower bound ≤ 10⁻¹² pp cannot manufacture relative gain, and a positive full-scope decision requires all declared support.

| 008 increment | ΔR (pp) | Relative gain | ΔA (pp) | Target wins | Calibration wins | ΔR − 0.10 pp | Public source |
|---|---|---|---|---|---|---|---|
| I_CAL (A2/F2) | 0.11599113694120639 | 19.35931862% | -0.1862248596596054 | 8/11; need 9 | 9/11; need 9 | 0.01599113694120638 | MU:L12476 |
| I_CHEM (A2/A0) | 0.11733805182842133 | 19.54019606% | -0.15260320896430368 | 7/11; need 9 | 9/11; need 9 | 0.017338051828421325 | MU:L12471 |
| I_LOCAL (A2/M) | 0.09949155290022221 | 17.07571895% | -0.10930949708669874 | 8/11; need 9 | 7/11; need 9 | -0.0005084470997777923 | MU:L12481 |

I_CAL and I_CHEM fail target-win counts despite clearing both continuous gain margins. I_LOCAL fails target and calibration win counts as well as the absolute margin; its small absolute deficit is not its sole failing predicate. All three ΔA components pass.

**Complete MASS retained gain sensitivities [S; private vectors not replayed].** MASS-006 deletes one physical shot across every arm while retaining equal condition weights: 12 primary deletions leave 11 shots; six temperature deletions leave five. MASS-007 has 11 deletions leaving 10 shots. MASS-008 removes the same identity from **both calibration and target roles**, leaving 10 identities and exactly 90 pairs, without refitting. The table contains deletion-only point extrema, not allowance-expanded or probabilistic intervals.

| Task/panel | Candidate/reference | Baseline ΔR (pp) | Deletion ΔR extrema (pp) | Deletion relative extrema | Deletion ΔA extrema (pp) | Sign within declared deletions | Public source |
|---|---|---|---|---|---|---|---|
| 006 Primary | C2/C0 | 0.17202115976269483 | [0.13885924553599582, 0.21410194644813818] | [22.08559233%, 30.95478933%] | [-0.022595902596964368, -0.006262570365427544] | 12 positive | MU:L8016; MU:L8484 |
| 006 Primary | C2/C1 | 0.11755308137482323 | [0.09393924251545505, 0.1353578023682085] | [16.09065931%, 22.81728333%] | [-0.021474567694776348, 0.011071219317378422] | 12 positive | MU:L8021; MU:L8520 |
| 006 Primary | C2/legacy | 0.2995666756757429 | [0.269018006347546, 0.33107276692267523] | [34.56181229%, 42.07875608%] | [-0.30373516979311366, -0.23471195851478566] | 12 positive | MU:L8026; MU:L8556 |
| 006 Temperature | C2/C0 | 0.11159369893836607 | [0.07005574442814871, 0.14589016399670768] | [17.70683171%, 30.63370883%] | [-0.03566364991876961, -0.0024668923750623684] | 6 positive | MU:L8033; MU:L9007 |
| 006 Temperature | C2/C1 | 0.1174670802290943 | [0.1044508416880921, 0.13910245735632032] | [23.76765957%, 29.16691763%] | [-0.08988184525980905, -0.034176545311357776] | 6 positive | MU:L8038; MU:L9043 |
| 006 Temperature | C2/legacy | 0.2942608719599868 | [0.2589417906227431, 0.3277713647552068] | [43.94115031%, 49.59964277%] | [-0.30885985031326024, -0.1495701539689656] | 6 positive | MU:L8043; MU:L9079 |
| 007 | C2/C0 | 0.3663213705391827 | [0.31206292011328773, 0.4028961241799489] | [34.7180134%, 40.40117148%] | [-0.34043694565306293, -0.23944438617355246] | 11 positive | MU:L11198; MU:L11293 |
| 007 | C2/C1 | 0.4020863256074434 | [0.3529577860944594, 0.43174520140078165] | [36.96719524%, 42.84844787%] | [-0.46130698023494787, -0.39026319137984433] | 11 positive | MU:L11203; MU:L11329 |
| 008 | A2/F2 | 0.11599113694120639 | [0.08110785763606176, 0.20599124286436998] | [13.82236212%, 32.47392173%] | [-0.3010759360332706, -0.15457065074560006] | 11 positive | MU:L12476; MU:L12749 |
| 008 | A2/A0 | 0.11733805182842133 | [0.07281895935372384, 0.1594676437056392] | [12.58758301%, 26.41339492%] | [-0.20359977835397508, -0.10600565194491568] | 11 positive | MU:L12471; MU:L12713 |
| 008 | A2/M | 0.09949155290022221 | [0.0058774024241204925, 0.14925514265641965] | [1.148924726%, 25.14722596%] | [-0.17839975366134542, -0.019710859274947812] | 11 positive | MU:L12481; MU:L12785 |
| 006 Flow | C2/C0; C2/C1; C2/legacy | Full scope unavailable | Unavailable for every comparator | Unavailable | Unavailable | No full-scope sign count | MU; original 23/24 supported windows |

The **006 temperature legacy comparison is retained explicitly**: baseline gain 0.2942608719599868 pp, baseline ΔA −0.23090996356309595 pp, deletion gain 0.2589417906227431–0.3277713647552068 pp and relative gain 43.941150312896615–49.599642774367536%. Primary C2/C1 and temperature C2/C0 gain extrema cross the 0.10 pp margin. In 008 every comparator's gain range remains positive but crosses 0.10 pp; all three relative ranges also cross 15%. A finite positive gain range does not replace the original conjunction. C2 still loses 006 C05 to C0/C1 and complete C08 to all three comparators; missing C07 support prevents full-flow summaries.

C2's 007 deletion A extrema are **[0.4817059490906369, 0.5734214913300837] pp**: a deletion can lower that continuous metric below 0.50, while the original **7/11 adequate shots versus nine required** remains authoritative. In 008, A2's overall deletion A is **[0.2723455552968132, 0.3757959046861664] pp**, but the worst retained calibration row has A **[0.5160530782664906, 0.7524003624861751] pp** across deletions. Thus every deletion retains an adverse calibration choice above 0.50. These are distinct overall and worst-choice estimands. `PW:docs/analysis/sci_md_mass_uncertainty_001/RESULTS.md:L84-L163@9dd456b`.

**Stopping predicate, without repeating the 15-row all-arm table.** Only C2 is primary. The full frozen 11-shot cohort and identity/chronology checks must qualify; the rule requires **at least nine numerically qualified recorded-boundary decisions, at least nine measured successes, at most one FALSE_FEASIBLE, and no post-outcome scientific change**. All conditions are conjunctive. The primary benchmark is 0.100 g additional solute and 2.0% minimum suffix TDS; S1–S4 are respectively (0.050 g, 2.0%), (0.150 g, 2.0%), (0.100 g, 1.5%), and (0.100 g, 2.5%). C0 and FIXED are contextual comparators, not automatic replacement candidates. These are offline, assay-conditioned, recorded-mass boundary decisions; aggregate partition/rate checks do not replay private oracle or regret calculations. `PW:docs/analysis/sci_md_mass_stop_decision_001/PROTOCOL.md:L43-L54@9dd456b`; `PW:docs/analysis/sci_md_mass_stop_decision_001/PROTOCOL.md:L135-L151@9dd456b`.

#### A.6.2 Caffeine: all comparators, adverse panels and retained deletions

The original adequacy rule is R ≤ 0.50 mg/g **and** A ≤ 0.25 mg/g in **every** primary condition, separately for each arm. All four arms satisfy it. Each S2 increment against S1, D0 and S0 requires ΔR ≥ 0.10 mg/g **and** relative gain ≥ 15%, at least three of four definite condition wins, and ΔA ≤ 0.05 mg/g, with propagated numerical allowances. The relative predicate uses candidate R ≤ 0.85 × reference R with allowance on both terms, rather than the rounded displayed percentage. Primary increments remain FAIL: all miss absolute gain, and S2/S1 also misses the condition-win count. The temperature and partial-flow comparisons do not apply a three-of-four rule to two conditions or rescue the primary result.

Source: `PW:docs/analysis/sci_md_caffeine_delivery_001/PROTOCOL.md:L62-L90@9dd456b`; `PW:docs/analysis/val_case_caffeine_decision_resolution_001/RESULTS.md:L36-L107@9dd456b`.

| Panel | Candidate/reference | ΔR (mg/g) | Relative gain | ΔA (mg/g) | Definite condition wins | Paired-shot gain +/0/− [S] | Public source |
|---|---|---|---|---|---|---|---|
| Primary | S2/S1 | 0.027020843144462403 | 17.75480106% | 0.009842250621699675 | 2/4 | 7/0/5 | CF:L607 |
| Primary | S2/D0 | 0.06709005809020771 | 34.89581957% | 0.009580326559639016 | 3/4 | 9/0/3 | CF:L387 |
| Primary | S2/S0 | 0.09039709410321847 | 41.93492216% | -0.05161224513757616 | 4/4 | 11/0/1 | CF:L497 |
| Temperature | S2/S1 | 0.020553775235206823 | 14.10567042% | 0.010629124330355885 | 2/2 | 6/0/0 | CF:L1723 |
| Temperature | S2/D0 | -0.004761043888169336 | -3.954419864% | 0.010549398510053959 | 1/2 | 2/0/4 | CF:L1587 |
| Temperature | S2/S0 | 0.041538623328749996 | 24.91853355% | -0.037651459110317725 | 2/2 | 4/0/2 | CF:L1655 |
| Flow subset | S2/S1 | 0.07437953847530321 | 23.40111136% | -0.026330046500174537 | 2/2 | 6/0/0 | CF:L143 |
| Flow subset | S2/D0 | -0.042944265663731634 | -21.41619633% | 0.01699318720134023 | 1/2 | 2/0/4 | CF:L7 |
| Flow subset | S2/S0 | 0.07903958886787554 | 24.50792619% | -0.05947632874565642 | 2/2 | 4/0/2 | CF:L75 |

Definite and possible condition-win counts coincide in these rows. Primary retains 12 shots/48 windows; temperature six/24. Flow retains **all six shots and both equally weighted conditions with 23/24 supported windows**; its C07 shot uses three observed supported windows, so flow numbers and wins are subset diagnostics. D0 outperforms S2 in the temperature and flow aggregate comparisons. S2 loses primary C02 and C05 to S1, C05 to D0, temperature C03 to D0, and complete flow C08 to D0. The observed C08 D0 advantage is 0.117905924 mg/g at displayed precision. `PW:docs/analysis/val_case_caffeine_decision_resolution_001/RESULTS.md:L50-L79@9dd456b`.

| Panel | Comparison | Deletion-only ΔR extrema (mg/g) [S] | Baseline + deletions, allowance-expanded ΔR envelope [S] | Deletion gain +/0/− | Positive lower endpoints | Deletion definite-win range | Public source |
|---|---|---|---|---|---|---|---|
| Primary | S2/S1 | [0.016579807827516724, 0.03636342809891058] | [0.01657980777032956, 0.03636342815609885] | 12/0/0 | 12 | [2, 3] | CF:L1310-L1313 |
| Primary | S2/D0 | [0.04951982758203427, 0.08169802156718933] | [0.04951982752484775, 0.08169802162437668] | 12/0/0 | 12 | [3, 4] | CF:L848-L851 |
| Primary | S2/S0 | [0.08031528458380857, 0.09813177994540327] | [0.08031528452662534, 0.09813178000256997] | 12/0/0 | 12 | [4, 4] | CF:L1079-L1082 |
| Temperature | S2/S1 | [0.013750916107082678, 0.024692220027804523] | [0.013750916049980378, 0.02469222008490496] | 6/0/0 | 6 | [2, 2] | CF:L2258-L2261 |
| Temperature | S2/D0 | [-0.024466271114358562, 0.009809747458349227] | [-0.024466271171481497, 0.009809747515473654] | 3/0/3 | not all; exact count not reported | [0, 1] | CF:L1880-L1883 |
| Temperature | S2/S0 | [0.018609648406237245, 0.06358096182600592] | [0.018609648349117998, 0.06358096188312648] | 6/0/0 | 6 | [1, 2] | CF:L2069-L2072 |

| Panel | Comparison | Deletion ΔA extrema (mg/g) [S] | Baseline + deletions, allowance-expanded ΔA envelope [S] | Deletion relative-gain extrema | Passing absolute / relative / A predicates | Public source |
|---|---|---|---|---|---|---|
| Primary | S2/S1 | [-0.002329875975806625, 0.0240519806912408] | [-0.002329876032992196, 0.02405198074842659] | [11.42995235%, 21.79835964%] | 0/12; 10/12; 12/12 | CF:L1314-L1317 |
| Primary | S2/D0 | [0.001630868690101997, 0.01651434415547605] | [0.0016308686329173357, 0.01651434421266115] | [27.82078258%, 39.66693288%] | 0/12; 12/12; 12/12 | CF:L852-L855 |
| Primary | S2/S0 | [-0.06894063506322477, -0.040840933406836824] | [-0.0689406351203956, -0.04084093334962983] | [38.10581111%, 46.26599849%] | 0/12; 12/12; 12/12 | CF:L1083-L1086 |
| Temperature | S2/S1 | [0.005756753543355669, 0.01877648579530189] | [0.005756753486255798, 0.01877648585240366] | [9.410136901%, 16.89490647%] | 0/6; 4/6; 6/6 | CF:L2262-L2265 |
| Temperature | S2/D0 | [0.00486590002478432, 0.018804562059854216] | [0.004865899967685914, 0.018804562116955283] | [-21.57037688%, 7.986077603%] | 0/6; 0/6; 6/6 | CF:L1884-L1887 |
| Temperature | S2/S0 | [-0.0517556878295084, -0.020284534271652527] | [-0.05175568788662818, -0.020284534214534054] | [11.89105422%, 36.00141762%] | 0/6; 5/6; 6/6 | CF:L2073-L2076 |

Each deletion removes the same physical trajectory across all four arms, averages two remaining shots in the affected condition and three elsewhere, and preserves equal condition weights. The first sensitivity table separates **deletion-only points** from **baseline-plus-deletion envelopes**, each scenario using its own numerical allowance. All primary gains remain positive, but **not one primary deletion clears 0.10 mg/g**; even the S0 envelope maximum is 0.09813178000256997 mg/g. Temperature S2/D0 reverses sign across the six deletions (3 positive, 3 negative). No flow deletions or replacement historical verdicts are available. Numerical gain allowances of about 5.7 × 10⁻¹¹ mg/g do not supply assay, training or transfer uncertainty. `PW:docs/analysis/val_case_caffeine_decision_resolution_001/RESULTS.md:L81-L107@9dd456b`; `PW:docs/analysis/val_case_caffeine_decision_resolution_001/RESULTS.md:L148-L159@9dd456b`.

#### A.6.3 5CQA: complete placement/addition comparisons and adverse components

The original rule requires R ≤ 0.25 mg/g **and** A ≤ 0.125 mg/g in every primary condition, with complete qualified support. **Every arm fails both quantities in every primary condition.** A material comparison also requires candidate adequacy, ΔR ≥ 0.05 mg/g **and** relative gain ≥ 15%, at least three of four definite condition wins, and ΔA ≤ 0.025 mg/g. The two-assay route requires **both** L12/L1M and L12/L2M to pass. L2M/L1M is the separate single-assay placement comparison. Historical L1 is not L1M.

Sources: `PW:docs/analysis/sci_md_5cqa_assay_002/PROTOCOL.md:L156-L183@9dd456b`; `PW:docs/analysis/val_case_5cqa_decision_resolution_001/RESULTS.md:L74-L98@9dd456b`.

| Panel | Candidate/reference | ΔR (mg/g) | Relative gain | ΔA (mg/g) | Definite condition wins | Public source |
|---|---|---|---|---|---|---|
| Primary | L12/L1M | 0.046212975101692866 | 13.44541183% | 0.03868497174671243 | 4/4 | CQ:L25 |
| Primary | L12/L2M | 0.05197258355845147 | 14.87192555% | -0.015276169103026316 | 4/4 | CQ:L175 |
| Primary | L2M/L1M | -0.0057596084567586026 | -1.675726514% | 0.05396114084973874 | 1/4 | CQ:L325 |
| Temperature | L12/L1M | -0.001114821440196867 | -0.3514156961% | 0.013091054560020132 | 1/2 | CQ:L933 |
| Temperature | L12/L2M | 0.04876301030947494 | 13.28275918% | -0.021163048010420682 | 2/2 | CQ:L1040 |
| Temperature | L2M/L1M | -0.04987783174967181 | -15.72256537% | 0.034254102570440814 | 0/2 | CQ:L1147 |
| Flow subset | L12/L1M | 0.028039227310278303 | 8.728710241% | 0.031207359260034095 | 2/2 subset | CQ:L2101 |
| Flow subset | L12/L2M | 0.041608824023084634 | 12.42798279% | -0.03326304182194706 | 2/2 subset | CQ:L2114 |
| Flow subset | L2M/L1M | -0.013569596712806331 | -4.224263261% | 0.06447040108198115 | 0/2 subset | CQ:L2127 |

Primary and temperature definite/possible counts coincide. The three flow relative ratios (gain/reference R) and 2/2, 2/2, 0/2 subset-win counts are public-aggregate derivations independently recalculated by the principal reviewer **[X/C/D+]**, not full-flow or private-shot scores. Each subset win compares candidate R plus its allowance with reference R minus its allowance. All six shots and equal condition weights remain; the incomplete C07 shot contributes three supported windows. C07 L1M remains INCOMPLETE_SUPPORT; L2M and L12 retain definite A failures from original-three-shot-denominator lower bounds **0.16616461080161396** and **0.15403149456723195 mg/g**, respectively. Flow has no complete-panel decomposition or deletion analysis. `PW:docs/analysis/val_case_5cqa_decision_resolution_001/RESULTS.md:L90-L114@9dd456b`.

The additional flow-subset derivation is reproduced by this complete command, using only the public condition summaries already audited:

```bash
python - <<'PY'
from pathlib import Path
import json
p=json.loads(Path('puckworks/docs/analysis/sci_md_5cqa_assay_002/RESULTS.json').read_text())['panels']['flow_stress']
for candidate, reference in [('L12','L1M'),('L12','L2M'),('L2M','L1M')]:
    c,r=p[candidate],p[reference]
    cm,rm=c['supported_subset_diagnostic'],r['supported_subset_diagnostic']
    gain=rm['R_mg_g']-cm['R_mg_g']
    wins=0
    for condition in c['conditions']:
        cc=c['conditions'][condition]['supported_subset_diagnostic']
        rr=r['conditions'][condition]['supported_subset_diagnostic']
        wins += cc['R_mg_g']+cc['R_allowance_mg_g'] < rr['R_mg_g']-rr['R_allowance_mg_g']
    assert c['full_scope_metrics'] is None and r['full_scope_metrics'] is None
    print(candidate+'/'+reference, f'{100*gain/rm["R_mg_g"]:.9f}%', str(wins)+'/'+str(len(c['conditions'])))
PY
```

```text
L12/L1M 8.728710241% 2/2
L12/L2M 12.427982791% 2/2
L2M/L1M -4.224263261% 0/2
```

| Panel | Comparison | Deletion-only ΔR extrema (mg/g) [S] | Deletion direct-gain numerical envelope [S] | Point gain +/0/− | Numerically +/−/unresolved | Deletion definite-win range | Public source |
|---|---|---|---|---|---|---|---|
| Primary | L12/L1M | [0.036349266479333286, 0.05439051897983538] | [0.03634926642224318, 0.054390519036963486] | 12/0/0 | 12/0/0 | [3, 4] | CQ:L498-L501 |
| Primary | L12/L2M | [0.04394329479808279, 0.05818002923808274] | [0.04394329474099478, 0.058180029295208255] | 12/0/0 | 12/0/0 | [4, 4] | CQ:L645-L648 |
| Primary | L2M/L1M | [-0.012086135337925685, 0.002050319886923724] | [-0.012086135395040696, 0.002050319944028485] | 2/0/10 | 2/10/0 | [1, 2] | CQ:L789-L792 |
| Temperature | L12/L1M | [-0.014466031626646447, 0.01613881968316505] | [-0.01446603168362919, 0.016138819740216623] | 2/0/4 | 2/4/0 | [0, 2] | CQ:L1273-L1276 |
| Temperature | L12/L2M | [0.040772303645262575, 0.05872138955445033] | [0.040772303588212905, 0.05872138961150488] | 6/0/0 | 6/0/0 | [2, 2] | CQ:L1416-L1419 |
| Temperature | L2M/L1M | [-0.06373864193155959, -0.024633483962097524] | [-0.0637386419886145, -0.02463348390504708] | 0/0/6 | 0/6/0 | [0, 1] | CQ:L1558-L1561 |

| Panel | Comparison | Deletion ΔA extrema (mg/g) [S] | Deletion numerical ΔA envelope [S] | Deletion relative extrema | Passing absolute / relative / wins / A predicates | Public source |
|---|---|---|---|---|---|---|
| Primary | L12/L1M | [0.03081595067990439, 0.04486237910961577] | [0.030815950622805864, 0.04486237916674223] | [10.90210572%, 15.71542126%] | 3/12 / 2/12 / 12/12 / 0/12 | CQ:L502-L505 |
| Primary | L12/L2M | [-0.017564339133773116, -0.01223071085081151] | [-0.017564339190896956, -0.012230710793709795] | [12.88625183%, 16.67897288%] | 10/12 / 5/12 / 12/12 / 12/12 | CQ:L649-L652 |
| Primary | L2M/L1M | [0.047899626826179265, 0.062426718243388885] | [0.04789962676908149, 0.0624267183005146] | [-3.596767734%, 0.5647720477%] | 0/12 / 0/12 / 0/12 / 0/12 | CQ:L793-L796 |
| Temperature | L12/L1M | [0.0021355627693577794, 0.026206192264434547] | [0.0021355627123299283, 0.026206192321463682] | [-4.517777116%, 5.411149897%] | 0/6 / 0/6 / not applied / 5/6 | CQ:L1277-L1280 |
| Temperature | L12/L2M | [-0.02778326268237652, -0.012720689482195124] | [-0.027783262739425378, -0.012720689425213465] | [11.26550556%, 15.51880977%] | 2/6 / 1/6 / not applied / 6/6 | CQ:L1420-L1423 |
| Temperature | L2M/L1M | [0.0212049817877287, 0.04973402439992852] | [0.021204981730746888, 0.049734024456956634] | [-19.65947436%, -8.259307484%] | 0/6 / 0/6 / not applied / 1/6 | CQ:L1562-L1565 |

Original primary component vectors (absolute / relative / wins / A deterioration) are **FAIL/FAIL/PASS/FAIL** for L12/L1M, **PASS/FAIL/PASS/PASS** for L12/L2M, and **FAIL/FAIL/FAIL/FAIL** for L2M/L1M. Candidate inadequacy separately fails every final comparison. All arms remain inadequate in all 12 primary deletions, each leaving three originally failing conditions untouched. L12/L1M gains remain positive but ΔA remains above 0.025 in every primary deletion; L12/L2M clears ΔA in every deletion, while its relative margin changes side. L2M/L1M remains adverse in 10 of 12 primary deletions and all six temperature deletions. Temperature scalar counts are diagnostics only; the three-of-four rule is not applied. `PW:docs/analysis/val_case_5cqa_decision_resolution_001/RESULTS.md:L3-L34@9dd456b`; `PW:docs/analysis/val_case_5cqa_decision_resolution_001/RESULTS.md:L74-L88@9dd456b`.

The gain decomposition is performed per paired shot before nested averaging: C_B + C_V = ΔR, where C_B comes from the difference in squared mean shot error and C_V from within-shot centered residual variation, divided by the paired R sum. Both contributions are on the RMSE scale in mg/g; neither is ΔA, signed ΔB, an assay variance or a causal diagnosis. Their retained sensitivities preserve all adverse signs:

| Panel | Comparison | C_B deletion extrema (mg/g) [S] | C_B +/0/− | C_V deletion extrema (mg/g) [S] | C_V +/0/− | Public source |
|---|---|---|---|---|---|---|
| Primary | L12/L1M | [-0.027788152377488287, -0.017646319236603224] | 0/0/12 | [0.05706112010458588, 0.08204635882751923] | 12/0/0 | CQ:L579-L582 |
| Primary | L12/L2M | [0.009792064320125754, 0.014653389584814368] | 12/0/0 | [0.03017951824626709, 0.04400236231906311] | 12/0/0 | CQ:L726-L729 |
| Primary | L2M/L1M | [-0.03905782652353759, -0.02846122410386481] | 0/0/12 | [0.018641532137906012, 0.0352683162652902] | 12/0/0 | CQ:L870-L873 |
| Temperature | L12/L1M | [-0.023693339954588808, -0.0049658742731369465] | 0/0/6 | [-0.004667763972010052, 0.031265664664098455] | 4/0/2 | CQ:L1354-L1357 |
| Temperature | L12/L2M | [0.010959225175212558, 0.02684535053678757] | 6/0/0 | [0.013926953108475044, 0.03790836696359569] | 6/0/0 | CQ:L1497-L1500 |
| Temperature | L2M/L1M | [-0.043589349784283964, -0.020298395109532127] | 0/0/6 | [-0.04096297424582628, 0.015112693252812809] | 1/0/5 | CQ:L1639-L1642 |

All contribution point signs in this table agree with their separately propagated numerical endpoints. The favorable primary C_V offsets adverse C_B for L12/L1M in every deletion; the same sign pattern does not suffice for L2M/L1M in ten deletions. At temperature C04, L12/L1M improves A while its squared-mean-error contribution is adverse, illustrating why the quantities cannot be substituted. The bounds are propagated arithmetic under retained numerical allowances; assay/calibration, early-input, training/model-selection and cross-source uncertainty remain unquantified. `PW:docs/analysis/val_case_5cqa_decision_resolution_001/RESULTS.md:L5-L34@9dd456b`; `PW:docs/analysis/val_case_5cqa_decision_resolution_001/RESULTS.md:L61-L72@9dd456b`; `PW:docs/analysis/val_case_5cqa_decision_resolution_001/RESULTS.md:L110-L133@9dd456b`.

#### A.6.4 Exact 32-row rheology matrix: original eligibility and retained envelopes

**[X/D+] All 32 M values, additive allowance sums u, original decisions and envelope endpoints reproduce from the audited public aggregates.** Primary rows compare the communicating E2 approximation with NEW C. Secondary rows compare NEW annulus-fast C with OLD core-fast C and describe modeled contrast magnitude. C is a computational reference. Neither group is comparison with physical measurements.

The original primary rule needs complete valid evidence and **u ≤ 0.20b**, then PASS if **M + u < b**, FAIL if **M − u > b**, otherwise UNRESOLVED. The secondary adapter has the same precision eligibility: a qualified **M − u > b** is MATERIAL_MODELED_DELIVERY_CONTRAST; qualified **M + u < b** is BELOW_DECLARED_MATERIALITY_BUDGET. Equality, excessive allowance or missing evidence is unresolved. The numerical allowance sums temporal, axial, radial, applicable property and independent arithmetic sensitivities; primary radial refinement varies C with E2 held at base, whereas secondary refinement varies **both** C cases. No root-sum-square or certified continuum bound replaces that sum.

Source rules: `EWP:docs/analysis/sci_md_rheology_010/PROTOCOL.md:L103-L141@4284e94`. Table-source register: `PW:docs/analysis/val_case_rheology_decision_resolution_001/RESULTS.md:L60-L174@9dd456b`.

P = primary approximation; S = secondary magnitude. SW abbreviates SW_WATER_ANCHORED_90C; TR = TR_LINEAR. D_TDS_pp, D_share_mean_pp and D_share_peak_pp are percentage points; E_Qint, E_Qpeak and E_Spath are dimensionless fractions. MATERIAL abbreviates the full original label above. The relation column concerns the retained **[M − u, M + u] sensitivity envelope** only, independently of original precision eligibility. The small negative lower endpoint in one primary row is retained without clipping.

| Role | Law/history | Metric | M | u | b | Original = reproduced | Retained sensitivity envelope | Relation to b | Source |
|---|---|---|---|---|---|---|---|---|---|
| P | SW_DOWN | D_TDS_pp | 0.0006862702074013072 | 7.588117187743609e-05 | 0.1 | PASS | [0.0006103890355238711, 0.0007621513792787433] | BELOW | RH-MD:L71 |
| P | SW_DOWN | D_share_mean_pp | 0.12191013174585176 | 0.0035543452158612876 | 1.0 | PASS | [0.11835578652999047, 0.12546447696171303] | BELOW | RH-MD:L72 |
| P | SW_DOWN | D_share_peak_pp | 0.19392815153366633 | 0.005935809168295586 | 2.0 | PASS | [0.18799234236537074, 0.1998639607019619] | BELOW | RH-MD:L73 |
| P | SW_DOWN | E_Qint | 0.00020819034437933857 | 1.8484873155088523e-05 | 0.01 | PASS | [0.00018970547122425005, 0.0002266752175344271] | BELOW | RH-MD:L74 |
| P | SW_DOWN | E_Qpeak | 0.00030680031541751516 | 2.3545905679384874e-05 | 0.02 | PASS | [0.0002832544097381303, 0.00033034622109690004] | BELOW | RH-MD:L75 |
| P | SW_DOWN | E_Spath | 6.94980762590388e-06 | 2.5421770347658418e-06 | 0.01 | PASS | [4.407630591138038e-06, 9.491984660669722e-06] | BELOW | RH-MD:L76 |
| P | SW_UP | D_TDS_pp | 0.0016416118804567503 | 0.00037022157370448605 | 0.1 | PASS | [0.0012713903067522643, 0.0020118334541612366] | BELOW | RH-MD:L77 |
| P | SW_UP | D_share_mean_pp | 0.13342195393337022 | 0.004349976550462681 | 1.0 | PASS | [0.12907197738290754, 0.1377719304838329] | BELOW | RH-MD:L78 |
| P | SW_UP | D_share_peak_pp | 0.19114098471015445 | 0.006701221443529026 | 2.0 | PASS | [0.18443976326662542, 0.19784220615368348] | BELOW | RH-MD:L79 |
| P | SW_UP | E_Qint | 0.0002652488097675106 | 8.181261517384742e-06 | 0.01 | PASS | [0.00025706754825012584, 0.0002734300712848953] | BELOW | RH-MD:L80 |
| P | SW_UP | E_Qpeak | 0.00045082884769666375 | 2.567989958886024e-05 | 0.02 | PASS | [0.0004251489481078035, 0.000476508747285524] | BELOW | RH-MD:L81 |
| P | SW_UP | E_Spath | 3.323293283785817e-05 | 5.7848026348858526e-06 | 0.01 | PASS | [2.7448130202972318e-05, 3.901773547274402e-05] | BELOW | RH-MD:L82 |
| P | TR_DOWN | D_TDS_pp | 0.0018236925471377674 | 0.0005435320518924881 | 0.1 | PASS | [0.0012801604952452793, 0.0023672245990302553] | BELOW | RH-MD:L83 |
| P | TR_DOWN | D_share_mean_pp | 0.12749342924472423 | 0.004586289366550728 | 1.0 | PASS | [0.1229071398781735, 0.13207971861127496] | BELOW | RH-MD:L84 |
| P | TR_DOWN | D_share_peak_pp | 0.19461007254809454 | 0.007475521456267592 | 2.0 | PASS | [0.18713455109182695, 0.20208559400436213] | BELOW | RH-MD:L85 |
| P | TR_DOWN | E_Qint | 0.00012235985642854267 | 1.0200538302566683e-05 | 0.01 | PASS | [0.00011215931812597598, 0.00013256039473110934] | BELOW | RH-MD:L86 |
| P | TR_DOWN | E_Qpeak | 0.0002479775372849968 | 2.378205133824908e-05 | 0.02 | PASS | [0.00022419548594674772, 0.00027175958862324585] | BELOW | RH-MD:L87 |
| P | TR_DOWN | E_Spath | 4.815447158737767e-05 | 9.046551669328134e-06 | 0.01 | PASS | [3.9107919918049535e-05, 5.72010232567058e-05] | BELOW | RH-MD:L88 |
| P | TR_UP | D_TDS_pp | 0.0003466546710040319 | 0.00035110687893803174 | 0.1 | PASS | [-4.4522079339998294e-06, 0.0006977615499420637] | BELOW | RH-MD:L89 |
| P | TR_UP | D_share_mean_pp | 0.11494771845015583 | 0.0051668536577439 | 1.0 | PASS | [0.10978086479241193, 0.12011457210789973] | BELOW | RH-MD:L90 |
| P | TR_UP | D_share_peak_pp | 0.20534200935388575 | 0.007716655753331386 | 2.0 | PASS | [0.19762535360055436, 0.21305866510721713] | BELOW | RH-MD:L91 |
| P | TR_UP | E_Qint | 0.0002588342047879354 | 1.3781806348183302e-05 | 0.01 | PASS | [0.0002450523984397521, 0.0002726160111361187] | BELOW | RH-MD:L92 |
| P | TR_UP | E_Qpeak | 0.0005649012745840711 | 2.63569527523442e-05 | 0.02 | PASS | [0.0005385443218317269, 0.0005912582273364153] | BELOW | RH-MD:L93 |
| P | TR_UP | E_Spath | 7.132785699909617e-06 | 1.7662891895023625e-06 | 0.01 | PASS | [5.366496510407255e-06, 8.89907488941198e-06] | BELOW | RH-MD:L94 |
| S | SW_DOWN | D_TDS_pp | 2.9961869936522074 | 0.008489871284922845 | 0.1 | MATERIAL | [2.9876971223672846, 3.0046768649371303] | ABOVE | RH-MD:L112 |
| S | SW_DOWN | E_Spath | 0.13454591460346485 | 0.0002579901528011186 | 0.01 | MATERIAL | [0.13428792445066373, 0.13480390475626597] | ABOVE | RH-MD:L113 |
| S | SW_UP | D_TDS_pp | 4.72916388200526 | 0.02003863469420253 | 0.1 | UNRESOLVED | [4.709125247311057, 4.749202516699462] | ABOVE | RH-MD:L114 |
| S | SW_UP | E_Spath | 0.17374215804640541 | 0.0005989287595028481 | 0.01 | MATERIAL | [0.17314322928690257, 0.17434108680590826] | ABOVE | RH-MD:L115 |
| S | TR_DOWN | D_TDS_pp | 3.6051172269668292 | 0.012200786715594436 | 0.1 | MATERIAL | [3.592916440251235, 3.6173180136824237] | ABOVE | RH-MD:L116 |
| S | TR_DOWN | E_Spath | 0.16186762627185167 | 0.0003068914568216119 | 0.01 | MATERIAL | [0.16156073481503005, 0.16217451772867328] | ABOVE | RH-MD:L117 |
| S | TR_UP | D_TDS_pp | 4.167558448648455 | 0.02463748658612719 | 0.1 | UNRESOLVED | [4.142920962062328, 4.192195935234582] | ABOVE | RH-MD:L118 |
| S | TR_UP | E_Spath | 0.16993329918319527 | 0.00048081404725824894 | 0.01 | MATERIAL | [0.16945248513593703, 0.17041411323045352] | ABOVE | RH-MD:L119 |

All 24 primary rows PASS and have envelopes wholly below their approximation budgets. Six secondary rows are qualified MATERIAL; SW_UP and TR_UP D_TDS_pp remain **UNRESOLVED** because u = **0.02003863469420253** and **0.02463748658612719 pp**, respectively, exceed the original precision ceiling 0.20 × 0.10 = **0.020000000000000004** in binary64. Their envelopes nonetheless lie wholly above 0.10 pp. Thus eight above-budget envelope relations do **not** become eight qualified original material contrasts. The accepted helper separately leaves bound resolution UNRESOLVED for all 32 and the bound-based diagnostic contract UNAVAILABLE: sensitivity evidence does not establish an applicable uncertainty bound. `PW:docs/analysis/val_case_rheology_decision_resolution_001/RESULTS.md:L121-L176@9dd456b`.

The delivery support is frozen at **0.015983191 kg UP** and **0.016114389 kg DOWN**, about 76.87–95.03% of the respective retained terminal masses, with explicitly unscored tails. Hydraulic/allocation metrics use 0–30 s, a different support. E2 has two communicating radial cells at each axial station, not two globally lumped states. The 011 distribution-preserving arrangement test already reports eight below-budget contrasts and did not trigger conditional E2 execution; it limits causal attribution of the 010 reversal, which also changes the permeability distribution. `PW:docs/analysis/val_case_rheology_decision_resolution_001/RESULTS.md:L178-L234@9dd456b`.

#### A.6.5 Phase-3 chronology and interpretation of completion

The T05 protocol and its first public result both enter PW in **the same commit**, `8646a9d5b643f731620f5d447d6e1d79da694f4f` (author timestamp 2026-10-15T10:24:35−05:00). The addition history of `docs/analysis/val_case_rheology_decision_resolution_001/PROTOCOL.md` and `docs/analysis/val_case_rheology_decision_resolution_001/RESULTS.json` therefore establishes a **same-commit public record, not strict committed protocol-before-result precedence**. An ancestry test that accepts equality cannot establish that stronger claim. The public commit history alone also cannot certify the unseen private execution sequence. This qualification does not undo the checked arithmetic or authorize a new score.

The framework acceptance itself is resolved: the owner's acceptance of PW #335 at 2026-10-15T13:14:49Z and merge at 13:15:14Z, commit `882584d110e1356091435ab8b002fb9abdd35ad6`, make it available for independently authorized prospective case declarations. The current proposed/pending header is stale. Acceptance does not migrate historical contracts, grant empirical population bounds or authorize production adoption. Primary authority: [owner acceptance, PW #335](https://github.com/trbrewer/puckworks/pull/335#issuecomment-6192947145), independently checked by the principal reviewer; see also `PW:docs/analysis/val_case_rheology_decision_resolution_001/RESULTS.md:L50-L58@9dd456b`.

#### A.6 source register

All line pins are to the fixed review commits, not moving main. PW = `9dd456be7fd797b9cda0a2bbf50d1ac717d72835`; EWP = `4284e9460c8057053e95de7cfa2fb3590e68e9db`. In a row, `CF:Lx` means the exact line in the CF path below at that PW commit; range endpoints are cited as ranges when the value spans lines. Full private trajectories are not contained in these public aggregate locators.

| Key | Exact source path and pinned commit |
|---|---|
| MU | PW:docs/analysis/sci_md_mass_uncertainty_001/RESULTS.json@9dd456be7fd797b9cda0a2bbf50d1ac717d72835 |
| CF | PW:docs/analysis/val_case_caffeine_decision_resolution_001/RESULTS.json@9dd456be7fd797b9cda0a2bbf50d1ac717d72835 |
| CQ | PW:docs/analysis/val_case_5cqa_decision_resolution_001/RESULTS.json@9dd456be7fd797b9cda0a2bbf50d1ac717d72835 |
| RH | PW:docs/analysis/val_case_rheology_decision_resolution_001/RESULTS.json@9dd456be7fd797b9cda0a2bbf50d1ac717d72835 |
| RH-MD | PW:docs/analysis/val_case_rheology_decision_resolution_001/RESULTS.md@9dd456be7fd797b9cda0a2bbf50d1ac717d72835 |
| Rheology original | EWP:docs/analysis/sci_md_rheology_010/METRICS.json@4284e9460c8057053e95de7cfa2fb3590e68e9db |

The source-order additive rheology reproduction is retained in `review_work/data/reanalysis_checks.json`, `review_work/data/rheology_reproduced.json` and `review_work/data/audit_reanalysis.py`; public empirical aggregate checks are in `review_work/data/primary_audit.json` and `review_work/data/additional_aggregate_checks.json`. These scratch records document the review's arithmetic scope; they do not upgrade retained private sensitivity summaries to independently executed empirical reductions.

<a id="appendix-a-7"></a>

### A.7 Merge chronology, review identity and current work



The five post-9-October follow-ups are merged at the following main integrations [X/R]; case results remain retrospective. Source chronology is committed chronology only. In particular, `merge-base --is-ancestor` returns success for identical commits; that does not prove a protocol was committed strictly earlier.

| PR | Title | Main integration | UTC commit date |
| --- | --- | --- | --- |
| [PW #340](https://github.com/trbrewer/puckworks/pull/340) | T04: retain 5-CQA gain sensitivity and RMSE decomposition | 9dd456be7fd797b9cda0a2bbf50d1ac717d72835 | 2026-10-18T15:33:13-05:00 |
| [PW #339](https://github.com/trbrewer/puckworks/pull/339) | VAL-CASE-CAFFEINE-001: persistent primary gains, conditional stress benefit | 43ec258c3db49ff76cfb89e0ea27bc55ad8d2bae | 2026-10-18T13:36:32-05:00 |
| [PW #338](https://github.com/trbrewer/puckworks/pull/338) | VAL-CASE-RHEOLOGY-DECISION-RESOLUTION-001: preserve contracts and report numerical sensitivity | 79852f11073ef92041edff5ae0e951603084c706 | 2026-10-17T20:56:10-05:00 |
| [PW #335](https://github.com/trbrewer/puckworks/pull/335) | VAL-INFRA-DECISION-RESOLUTION-001: prospective policy and synthetic evaluator | 882584d110e1356091435ab8b002fb9abdd35ad6 | 2026-10-15T08:15:13-05:00 |
| [PW #334](https://github.com/trbrewer/puckworks/pull/334) | SCI-MD-MASS-UNCERTAINTY-001: audit retained scores and physical-shot sensitivity | 7975fbc39a649cb757702131e2b91b13439c7192 | 2026-10-14T07:44:08-05:00 |

| Bundle | First protocol commit | First result commit | Inference |
| --- | --- | --- | --- |
| sci_md_mass_uncertainty_001 | 14b8ab4d5ea5ba979e1e1f443ed1c1320ad0265f 2026-10-14T06:20:20-05:00 SCI-MD-MASS-UNCERTAINTY-001: freeze retrospective reduction protocol | e221e5d8e1167c73027c1a55b0afe0b1f054e155 2026-10-14T06:37:15-05:00 SCI-MD-MASS-UNCERTAINTY-001: retain all-arm results and bounded handoff | distinct preceding protocol commit |
| val_infra_decision_resolution_001 | No such PROTOCOL.md history | No such RESULTS.json history | not established by these paths |
| val_case_rheology_decision_resolution_001 | 8646a9d5b643f731620f5d447d6e1d79da694f4f 2026-10-15T10:24:35-05:00 VAL-CASE-RHEOLOGY-DECISION-RESOLUTION-001: preserve contracts and report sensitivity envelopes | 8646a9d5b643f731620f5d447d6e1d79da694f4f 2026-10-15T10:24:35-05:00 VAL-CASE-RHEOLOGY-DECISION-RESOLUTION-001: preserve contracts and report sensitivity envelopes | same initial commit; ordering not established |
| val_case_caffeine_decision_resolution_001 | 8fd0483448cac73df8511e6c9efd0d7e69926510 2026-10-18T11:22:04-05:00 VAL-CASE-CAFFEINE-001: freeze retrospective deletion protocol and input identities | f3f77594caa4396bd3a438a29402537f74ee6972 2026-10-18T11:28:15-05:00 VAL-CASE-CAFFEINE-001: reduce retained paired evidence and preserve historical decisions | distinct preceding protocol commit |
| val_case_5cqa_decision_resolution_001 | 4a330d6ebd5fc425d18061f0cfb20c15c2153508 2026-10-18T14:56:25-05:00 T04: declare and verify bounded 5-CQA retained-evidence addendum | a8d168da2145e89ee724d0f597a062dc3bd2b2e8 2026-10-18T15:02:09-05:00 T04: report authenticated 5-CQA sensitivity and decomposition | distinct preceding protocol commit |

| Live primary record | State / draft | Current candidate | Record updated |
| --- | --- | --- | --- |
| [321: MODEL-PANNUSCH2024-COMMON-PAST-CONTRAST-007: joint bounds and checked witness repair](https://github.com/trbrewer/puckworks/pull/321) | open / True | bd976d2d4b7fc516c005765befedf5911a89ab2e | 2026-10-06T11:59:21Z |
| [333: MODEL-GRUDEVA2026-010: accepted-state repeat verified; refinements blocked by payload mismatch](https://github.com/trbrewer/puckworks/pull/333) | open / True | d4462d7ccaa8454babf114855fcf430a74daa3f4 | 2026-10-11T01:38:31Z |
| [104: SCI-MD-006 — Nested shared-parameter versus species-specific production-law test](https://github.com/trbrewer/espresso-whole-pull/issues/104) | open / None | issue, not candidate | 2026-08-25T14:50:13Z |

The principal reviewer read those live bodies. #321’s repaired candidate is technically complete for its bounded engineering scope; its current-base CI was not established from the old receipt. #333’s accepted-state repeat is verified, but the dense arbitrary-time payload reconstruction failed and twelve refinements were not run. #104 preserves the original shared/species contract and excludes protected Angeloni access; a new H1 limit comparator is a distinct decision.

[PW #335 owner acceptance](https://github.com/trbrewer/puckworks/pull/335#issuecomment-6192947145) was recorded 2026-10-15T13:14:49Z, before merge at 13:15:14Z. Acceptance permits prospective opt-in case declarations and preserves the historical records; it does not adopt a model. Foster/caffeine reviewers are separate nonhuman agents; Pannusch006 records implementation-author self-review. No independent human domain review is inferred.


<a id="appendix-a-8"></a>

### A.8 Pinned source identities for reuse



[X] These SHA-256 values were calculated from the public, nonprotected source files in the reviewed checkout. They identify evidence to reuse, not a new governance requirement. Protected data files are not hashed or opened here. Full Git identities and line links are in Appendix E.

#### EWP

##### `.github/workflows/static-validation.yml`

**SHA-256:** `19fd8fb510f84e46cd69e5438452dfca869684f5cc796a4d198a15cbca85fc1c`

##### `README.md`

**SHA-256:** `5c9bacec3776aa830d29f0f50d834c696814f01d7cd32f843372711193f20b52`

##### `VERSION`

**SHA-256:** `1f930dd1f133c1f97a94fe3acb8db34372cf4c01ffdb2b3ff4ca72f9494121e9`

##### `dependencies/puckworks.lock.json`

**SHA-256:** `52b15ceef87d503a3e77c6e3c1cbed785185d2dde0b79647e5fbe309395d2f10`

##### `docs/MODEL_SPECIFICATION.md`

**SHA-256:** `b61289012c4a178d963514f49f4f1e6d4d3439ac36e4cc1096de8b806c06e858`

##### `docs/PROJECT_STATE.md`

**SHA-256:** `d0846e517f62cea5f805dc7f32ffa98297fa373c618b9393325743038fefd8fb`

##### `docs/analysis/data_leverage/VISUALIZER_PRIVATE_WORK_RECORD.md`

**SHA-256:** `04776d834668eefcc3b2e6fca7ed582ab8e8a8803791b44b57c8bef7b1a23f27`

##### `docs/analysis/ewp_porosity_permeability_prior_001/POROSITY_MATERIALITY.json`

**SHA-256:** `5ee7d7731073e833a2e41c49cf44fde0a20910c5a3ad1e12015824dc51d05b63`

##### `docs/analysis/ewp_porosity_permeability_prior_001/RESULT.md`

**SHA-256:** `fc3a27b7b8514251d8fbd3c882bf827fd938de1cacc4de1c50a5c2f43c49fdd5`

##### `docs/analysis/sci_ed_003/MINIMUM_PROGRAMME.md`

**SHA-256:** `372903500aadab8e6fd6b0ec17dde1c18120aceae34b456af39eda2caa1f11dc`

##### `docs/analysis/sci_ed_003/RESULT.md`

**SHA-256:** `07f26cd49d1cd8eb4f831ef796854c73633c419c488d3a2ebb5d06a555619730`

##### `docs/analysis/sci_md_010/BREW_RESULTS.csv`

**SHA-256:** `3a293f6a702f9cad357afe08689f07a2b54924f069355f4b6e7b7fc95dfd2e5f`

##### `docs/analysis/sci_md_010/FOLD_RESULTS.csv`

**SHA-256:** `3adf5f1bc965fa0a1d31c2c97fd12d2e59076c4b17a0b0cac0c5b621af805faa`

##### `docs/analysis/sci_md_010/PRESSURE_RESPONSE_DIAGNOSTICS.json`

**SHA-256:** `f35b42ace4f3f07992a46af8f1dcc2fa0689dd8554a0ff84f18a8f274f747bcd`

##### `docs/analysis/sci_md_010/RESULT.md`

**SHA-256:** `93f0c2c6c75c004c54a0b9e2f312c219bb7781c37703279e65a62640447a4cc7`

##### `docs/analysis/sci_md_010/UNCERTAINTY_RESULTS.json`

**SHA-256:** `4c40816e2eebd0c5448075175defbaaddcf99da1c9689d950ffb68fdfe2aaf56`

##### `docs/analysis/sci_md_011/AGGREGATE_RESULTS.csv`

**SHA-256:** `51675b20eb13df5a2b08199ceef021ccb063c6c6f47317d288948b1b8525d576`

##### `docs/analysis/sci_md_011/BREW_RESULTS.csv`

**SHA-256:** `7373b0e8f6174c327f9395dfb253b4fee943c40cbcffc11ffc1b9462951827dc`

##### `docs/analysis/sci_md_011/FOLD_RESULTS.csv`

**SHA-256:** `9b3d5236676512fb765f46aecf61fb6c00d110eb764eb10802b78e383d3245a1`

##### `docs/analysis/sci_md_011/PAIRWISE_COMPARISONS.json`

**SHA-256:** `5383f20befd5cf2bf2c5f66bda4edf30a2d7fd3cf4c3cef9713c5e0934665604`

##### `docs/analysis/sci_md_011/PRESSURE_RESPONSE_DIAGNOSTICS.json`

**SHA-256:** `35b6259ea2db82dc6b647db95880d67f0b1f602e8e974b87d981692a5bf4e140`

##### `docs/analysis/sci_md_011/RESULT.md`

**SHA-256:** `c61aa8706da104ba00560f444e3a95abec51b9c397c6c90de6a0ea17fd5f27db`

##### `docs/analysis/sci_md_011/UNCERTAINTY_RESULTS.json`

**SHA-256:** `73093487236505a2be053094a047d0d227a65e23c3e48d70ba66bdfe32dc813a`

##### `docs/analysis/sci_md_012/PARAMETER_FEASIBILITY.json`

**SHA-256:** `d2c156f0fa3b83279964abcf071c27cc2d8255ba8ecd4e3189070d864f0e709f`

##### `docs/analysis/sci_md_012/RESULT.md`

**SHA-256:** `bd751c0fdc37da6195d90b1bcaf3b8c61d589cb202db7b99b607049627fb0683`

##### `docs/analysis/sci_md_012/ROOT_FEASIBILITY.csv`

**SHA-256:** `a3c8d2359a40e2e08c47978060c5283db7c1127a622ebdf779686bc58052d6b7`

##### `docs/analysis/sci_md_grudeva_clock_001/RESULT.md`

**SHA-256:** `2c7f95a6f9fefa30cdd020e04d02f70e69d54eff230198acd01e4fc8fc770626`

##### `docs/analysis/sci_md_rheology_010/METRICS.json`

**SHA-256:** `a0bc4986348aafc90ae8d7a33a0b8162acd02f2688708f6b215340fded7b3c20`

##### `docs/analysis/sci_md_rheology_010/PROTOCOL.md`

**SHA-256:** `9f2a26fbb69c126768a67f15919143a6d0e58f7956fc28a44fa5cc7d84722174`

##### `docs/governance/MINIMUM_NECESSARY_GOVERNANCE_STANDARD.md`

**SHA-256:** `58c33923f02ca733d611ddc41173fce0e2f33a20d2908312b572f57822edc364`

##### `docs/wp03/WP03_002_RESULTS.md`

**SHA-256:** `ebed23ba4b0b70fbbb2ac37dee92753fcda31aebfa927eacfb6408e929b1e464`

##### `scripts/sci_md_011_core.py`

**SHA-256:** `3e3651cf19b01850cc94ce5e648c5b65b58f7c0fdb6d5bb972032e9d78ad70a5`

##### `solver/espressoWholePullFoam/aggregateViscosity.H`

**SHA-256:** `8b7ef1b7e4fc7ba0eb52dc2d06cb0b5770aa8021fe481af23f3a74c0c45fbb8c`

##### `solver/espressoWholePullFoam/espressoWholePullFoam.C`

**SHA-256:** `0e31905c1f174554cf192122e565d566ebd7327ac6d4a6a8cd7e4c2df3beb667`

##### `solver/espressoWholePullFoam/forchheimerResistance.H`

**SHA-256:** `0a035b0799ecc91cd5100da99801526df19e4a721d51afaa53e2a02eaf5af124`

##### `solver/espressoWholePullFoam/machineBoundaryModel.H`

**SHA-256:** `20d8e48ee6c4f9ffe6c61b40604760be65fc3ff4225f33f2cac5a61437baf719`

##### `solver/espressoWholePullFoam/poroelasticCompaction.H`

**SHA-256:** `4a673a52e9d690ac22b3ecc21b8cf2c9b7e32168bd62863465c7e53b9515b0b6`

##### `validation/sci_md_008/FINAL_REPORT.md`

**SHA-256:** `de1623ee00940916fa668102dad61b0a1f18f364792efa29cb2cfc2fdce631a3`

##### `validation/sci_md_008/INVENTORY_SCALE_INVARIANCE.csv`

**SHA-256:** `d5549532d84a2caaac2e3b46ed9f1e31a762c623ce6197e36d99ed5dbfa74a6d`

##### `validation/sci_md_009/FINAL_REPORT.md`

**SHA-256:** `53efa52ec0e2de79ccf0244d4a15ed4533eb8f5dcdba9b5dda396465372a3d7f`

##### `validation/sci_md_009/NONLINEAR_RESPONSE_VALIDATION.csv`

**SHA-256:** `4f7ad6048886649cd957221d0c6139e3fbf88aec0d0afd822c5ef1fef28d70f2`

##### `validation/wp03/WP03_002_CORRECTED_COMPARISON.json`

**SHA-256:** `6a6c6bd62dd6ffda209c79e24e9fc9506f74fdc421de9ff56400c15162f0600e`

#### PW

##### `CLAUDE.md`

**SHA-256:** `24e27b14f190c88fc573b85bd372e43ec1803e6dae96b4e7dceab70d5790b328`

##### `README.md`

**SHA-256:** `ead8ddbf5f9baa22073c19700beb8f428a6ac51142a4a6cb0f4caa9213d0d1c1`

##### `docs/CURRENT.md`

**SHA-256:** `876b9acf97bcd73a839d56e44cb7825930c4fd67402be1d16c3816881da7b4f5`

##### `docs/ONBOARDING.md`

**SHA-256:** `5d5aa48d1bc7373d98bee2c5a10b0d1450f7a64127e2cda39b1d04cb2d6eea7b`

##### `docs/ROADMAP.md`

**SHA-256:** `d5247790377d364bfae13313fe87bef1bad30fc94b4a620170fd4127687454a5`

##### `docs/analysis/model_foster2025_postsat_001/HANDOFF.md`

**SHA-256:** `1785de5665b0b21c7abbeddc5d676c8297d81c0bdbf07a36594bc6d4ea203259`

##### `docs/analysis/model_foster2025_postsat_001/RESULTS.md`

**SHA-256:** `1c85b8bff638bc09628d9fd4a5db9235513a656a34056085185f346d5968d8fc`

##### `docs/analysis/model_grudeva2026_bed_accuracy_004/RESULTS.md`

**SHA-256:** `7924895bf4d6174c8d52d0a41b8f222f1233ba6883e7f2c2408b213f27d9487b`

##### `docs/analysis/model_grudeva2026_matched_comparison_008/RESULTS.json`

**SHA-256:** `53d7df682e3a334e283e38536cfcb31d0eb76b40b4b86ddb0a1d2624142c414e`

##### `docs/analysis/model_grudeva2026_matched_comparison_008/RESULTS.md`

**SHA-256:** `b6dda44ea048fcbd256186345eecdf9ad50160d33411a6b30403476ecdda76d0`

##### `docs/analysis/model_grudeva2026_publication_reconciliation_009/RESULTS.json`

**SHA-256:** `b2895fe8bdf7b8b1e529a9830b036f18eff9100800331a0ae8953b9ae9d13862`

##### `docs/analysis/model_grudeva2026_publication_reconciliation_009/RESULTS.md`

**SHA-256:** `6e4aa8024d78a813c2bccc0d8e102c91fbd83e609b93c25c33666be3a37e77f1`

##### `docs/analysis/model_pannusch2024_prefix_conditioned_006/REVIEW.md`

**SHA-256:** `f38271d8e305bae2a7bab3872963454c977c87c26d8e51f15033c33f6580d089`

##### `docs/analysis/rp_d_lc_001/decision.md`

**SHA-256:** `f6be01bee027b693b80e8bb2d1952d94df459cc8d094ed4bc8495bef884ad616`

##### `docs/analysis/sci_md_004_stage_e0/target_access_policy.json`

**SHA-256:** `8f27422669cb83812c199a9f8340d1dd834e90538f7b904ce7bdc8d407006f89`

##### `docs/analysis/sci_md_5cqa_assay_001/RESULTS.json`

**SHA-256:** `eb30c4e2e570e64f66f43b64b4211c375bc7a20c2a50e4e7af2e3b7cc3196d64`

##### `docs/analysis/sci_md_5cqa_assay_002/PROTOCOL.md`

**SHA-256:** `1d3e01e77b93b1caa0455696936ea27a1383e230e2ee647609250f39adc1c4ef`

##### `docs/analysis/sci_md_5cqa_assay_002/RESULTS.json`

**SHA-256:** `8e5383f61e32d67a422737f025b52a8ecf0b61f00b267e7ce946385a12c32b39`

##### `docs/analysis/sci_md_5cqa_assay_002/RESULTS.md`

**SHA-256:** `c34eae1cff3f76a33d9bb3a92cabafaba3207144d4289c65aeed50f905730e76`

##### `docs/analysis/sci_md_5cqa_delivery_001/RESULTS.json`

**SHA-256:** `4e0a27e3cc88194a09023a399894e370341131b833926f2f2276ad473d9207e8`

##### `docs/analysis/sci_md_5cqa_tds_001/RESULTS.json`

**SHA-256:** `93348e7ade587f6515d4e30a8c0502eca0ab1e53bfda47c26559ad8e1e947d90`

##### `docs/analysis/sci_md_caffeine_delivery_001/PROTOCOL.md`

**SHA-256:** `edcdd59f60d58b0b30a23aa0a77c77d98a3a4a2363eb490e6690a2cdfcffcc0d`

##### `docs/analysis/sci_md_caffeine_delivery_001/RESULT.md`

**SHA-256:** `9f718dc8e2eb4c0fbc160dc801b81e69853588ff777a04b4d572491f83ee78a2`

##### `docs/analysis/sci_md_caffeine_delivery_001/RESULTS.json`

**SHA-256:** `f42708bb45acbdd3b637fc6db28c5236ff7e973c02dd5c489ea9f9c2569e7c06`

##### `docs/analysis/sci_md_grudeva_clock_001/PROTOCOL.md`

**SHA-256:** `795a416b7206d94bccfda01e799b0a9a98c0211161ea7760e80678435558941e`

##### `docs/analysis/sci_md_mass_delivery_001/PROTOCOL.md`

**SHA-256:** `c927815298aed74b04a5bb7b1c3f7acbf4762b9b8eff6a2e31ab0510ab2685b4`

##### `docs/analysis/sci_md_mass_delivery_001/RESULTS.json`

**SHA-256:** `38a3f358e1c28855cda076dd7f5fbf24be2bf430a6dc727a50e96b43558862ef`

##### `docs/analysis/sci_md_mass_delivery_002/PROTOCOL.md`

**SHA-256:** `ad02f7c936bc85fa524ba49b9d485cf63fbebc3c689b92cf336f072bbfff4dae`

##### `docs/analysis/sci_md_mass_delivery_002/RESULTS.json`

**SHA-256:** `189d014437391b0f7b3d33c9b5a98d16223edc5e0189c8772bd88c0a804966a9`

##### `docs/analysis/sci_md_mass_delivery_003/PROTOCOL.md`

**SHA-256:** `5d1e3f0cb2c11969e5cbee5c549f5d3521329d6e69cba997511f0d63441ca85e`

##### `docs/analysis/sci_md_mass_delivery_003/RESULT.md`

**SHA-256:** `91a68224daf71cfd7fa44b23d7f2c708d969f6589054a9623f0be6672abcdc0f`

##### `docs/analysis/sci_md_mass_delivery_003/RESULTS.json`

**SHA-256:** `11e37d0aed6f9ecbe462b5b5e4e8fe6f132b522f19d74c9e997a76cee1ef8e26`

##### `docs/analysis/sci_md_mass_delivery_004/RESULT.md`

**SHA-256:** `f8014ffb3d6ba3d379fceebba8dae0b74bd4894cdbfd3b730b6196c34567a84d`

##### `docs/analysis/sci_md_mass_delivery_006/PROTOCOL.md`

**SHA-256:** `59e345f753f147ad69f7cb4cf03f91c02f86d0272a5f7c03ad2f4b80999831d0`

##### `docs/analysis/sci_md_mass_delivery_006/RESULT.md`

**SHA-256:** `b3b00e3123108d35170a573bece83b9ffd2ad3d767e78abb6d5d8e09b1f03be6`

##### `docs/analysis/sci_md_mass_delivery_006/RESULTS.json`

**SHA-256:** `c1cae77cabfd55db0ba93989203537b773fa9334d8416f9082aae6729b9071b6`

##### `docs/analysis/sci_md_mass_delivery_007/PROTOCOL.md`

**SHA-256:** `327badc3bef399f4ad180da051083f88662b981019f5080273e255357ac5d477`

##### `docs/analysis/sci_md_mass_delivery_007/RESULTS.json`

**SHA-256:** `c5dd263b5998a1b560c867640c5408e79974b37ac035ca1665de401fe6c1c4ac`

##### `docs/analysis/sci_md_mass_delivery_008/PROTOCOL.md`

**SHA-256:** `4263e060736b572505b39b42754e87351148fefda141797f7047b7e75ef3923d`

##### `docs/analysis/sci_md_mass_delivery_008/RESULTS.json`

**SHA-256:** `ab5fda152dd06954516cfd04d44c3657217a7ba7475f285035188fdda5f5c8b3`

##### `docs/analysis/sci_md_mass_stop_decision_001/PROTOCOL.md`

**SHA-256:** `2325143442df0d8c096b43495f480e986b3764074a64ebef9794ec8619f4450a`

##### `docs/analysis/sci_md_mass_stop_decision_001/RESULT.md`

**SHA-256:** `2f8cdfe8f33f6e8f5a2d64a32b3ee09d77949d16e81df47a5d5a50f9200e8fab`

##### `docs/analysis/sci_md_mass_stop_decision_001/RESULTS.json`

**SHA-256:** `ac566004778cb8f6c1fb9de26053a6a6071c9bcea1934fafff948589f4835627`

##### `docs/analysis/sci_md_mass_uncertainty_001/PROTOCOL.md`

**SHA-256:** `8f0e8c05c7919a98ff8e787bef6b81896bc07a704e1afc30f8a54533d41457c3`

##### `docs/analysis/sci_md_mass_uncertainty_001/RESULTS.json`

**SHA-256:** `544dc9a78999c8fb09d73aca87864e538d34d8162f81f00415dbfd73ca0137b0`

##### `docs/analysis/sci_md_mass_uncertainty_001/RESULTS.md`

**SHA-256:** `293e5710f19919e16bdf5ce867865e9102da2ea41f0f95f0cc9acd36e4484897`

##### `docs/analysis/sci_md_smrke_transfer_001/RESULT.md`

**SHA-256:** `9bb949c595d784fbb71ba609ef94d523d544bfde4e61f1960df4a238c0e54eb3`

##### `docs/analysis/sci_md_trigonelline_delivery_001/RESULT.md`

**SHA-256:** `f6e50b0328a62c81a43aef707e2b8dd9709a3bf3722fb0f7513ad3fd84b89345`

##### `docs/analysis/sci_md_trigonelline_delivery_001/RESULTS.json`

**SHA-256:** `98654466f771f5928b4e6c05dd77598910993312346a2fa39a90bd4c5a10b20c`

##### `docs/analysis/sci_val_tamped_k_001/RESULT.md`

**SHA-256:** `d8f2ad286042fa34024e602a21dc466c904043383aedab6f9655daeb4acec6ab`

##### `docs/analysis/val_case_5cqa_decision_resolution_001/RESULTS.json`

**SHA-256:** `d4f6877a2a89cc41979153c006b114ca6ae263930a27ad14d17bf315e3d13436`

##### `docs/analysis/val_case_5cqa_decision_resolution_001/RESULTS.md`

**SHA-256:** `4fa78fae66611d454d671357352fad2d08e561d30e25e9d1136dbacfef882264`

##### `docs/analysis/val_case_caffeine_decision_resolution_001/FINAL_REVIEW_ADDENDUM.json`

**SHA-256:** `3557cde4c965d8664bf266f2eb55784528513e1d492ae21fa2f441cc996868e6`

##### `docs/analysis/val_case_caffeine_decision_resolution_001/RESULTS.json`

**SHA-256:** `b76b428448f3b1bf8cd3eae78b647dca88e856a6ea6d0aa8be74f61460d80cb2`

##### `docs/analysis/val_case_caffeine_decision_resolution_001/RESULTS.md`

**SHA-256:** `9dbf3426b564ccedd9d8d1935ef3f7073768c11249710443d8a66c1b75c0bc37`

##### `docs/analysis/val_case_rheology_decision_resolution_001/RESULTS.json`

**SHA-256:** `665cc4f0d905726a6e3ff55d60d20a3de82dde25aa73933ffa455a0907e4ccc1`

##### `docs/analysis/val_case_rheology_decision_resolution_001/RESULTS.md`

**SHA-256:** `456acb30e83f8cad0354251c17b9ea1ae320b3a303b188f1fb4890c2c9d07e0e`

##### `docs/cards/pannusch2024.md`

**SHA-256:** `538dc01dee353f215ceb502c6cd1d367ec27ab400b6e46d98bb934a0abb60e78`

##### `docs/data/ESPRESSO_DATA_GUIDE.md`

**SHA-256:** `450a780004d3fd8af5a7602398d6a9b1dd1b478968460530956a79552cfeee8d`

##### `docs/governance/DECISION_RESOLUTION_POLICY.md`

**SHA-256:** `db16e68aa0e7fbdb37bfb455c39455928115af65c207fc43ec133424cd72a552`

##### `docs/governance/MINIMUM_NECESSARY_GOVERNANCE_STANDARD.md`

**SHA-256:** `f2250c36133b71d927b9f0cf77db38ba0c2a1561fe6d5a8029250df5f78995c5`

##### `docs/paper1_resource/PAPER_1_PIVOT_AND_REDRAFT_PLAN_V2_2_1.md`

**SHA-256:** `1e4d786c90d11f72271670039bd071464d0419f03d99ffba0c0091808f7b655b`

##### `docs/paper1_resource/PAPER_A_PLAN_MANIFEST_V1.json`

**SHA-256:** `8d3634898623e2c7623a78fb959dc9b1369ca199500b1f307260df7a3756938c`

##### `docs/research/ESPRESSO_DEVELOPMENT_GUIDE.md`

**SHA-256:** `4981f808d385cddf0c625d5d3b723818b1feff8ba6587fa974b27d5b1da9fc13`

##### `docs/research/ESPRESSO_PROGRAMME_REVIEW_2026-10-01.md`

**SHA-256:** `f281e31e3fce3fee90299a776c1494b4418695321db2e6670c5ffc85b209c632`

##### `docs/research/ESPRESSO_THRESHOLD_AND_CAPABILITY_REVIEW_2026-10-09.md`

**SHA-256:** `21ea048798cdfad4af6374a83caacc3f3e5386d80588f36a8283ed56acf314c6`

##### `docs/status/current.json`

**SHA-256:** `07d8b30129ca41078435126ea1d46cb701f128c5522c033222c0493264fba248`

##### `puckworks/analysis/five_cqa_decision_resolution.py`

**SHA-256:** `db165d432e6eb423ead3cb0f0d4db2b21ec72458665e398adfbf3b241d9984e8`

##### `puckworks/data/AVAILABLE_DATA_REGISTER.json`

**SHA-256:** `750d4306d19e73a57e52051b10188e57302bebafe1fb538e1b1c97f802435759`

##### `puckworks/data/LOCAL_CORPUS_SNAPSHOT.json`

**SHA-256:** `50680d5c54aa2161910138caff53dfb786546e08d1e26c0a6fbe1193d2a2038d`

##### `puckworks/harness.py`

**SHA-256:** `30a64bf8c6140210231ece4fb12def58e99eba63ffd8ba90fa3d43df59289b37`

##### `puckworks/models/__init__.py`

**SHA-256:** `b97f3ebcc6f2023fcac5c05e532648866137018fec5345170024ed0d171f3833`

##### `puckworks/models/cameron2020/extraction_bdf.py`

**SHA-256:** `ab9ce925d07397e8effb8d17f909ecc1e42fed93ba3366de95669dd09be4b4a4`

##### `puckworks/product/_pull.py`

**SHA-256:** `fa5fed99d8fa20a836ee768567b85a77f9fe5bf10fd2d8e2e714b2914408134d`

##### `puckworks/registry.py`

**SHA-256:** `fb02392d6c17f0f54eec4c9d8d600e4429f8cdb6532a06e4f9824df80518bbda`

##### `puckworks/validation/decision_resolution.py`

**SHA-256:** `d9c3d2a6e949e1f617e813dab12680dff58acdd1e4904178910739d4876e7d90`

##### `puckworks/validation/gates.py`

**SHA-256:** `dce6300329b76e783bc122b3f9661b5816f05ee2eb3d3cf38f7c9fc9a9813451`

##### `pyproject.toml`

**SHA-256:** `d61165168cdff735bf24f29e89c94f1a5c7c32a2ead52480f478ab8d95d82617`

##### `tests/test_cameron_inventory.py`

**SHA-256:** `4f7e3df30e146e13f8f3929638607c746e6eb6f526b94a594f7e28a92c4331c1`


<a id="appendix-b"></a>

## Appendix B — Complete review scripts and frozen logic

[Back to navigation](#review-navigation)

All scripts below were written for this review and contain no private observations or restricted third-party source. The principal reviewer reran the scientific reducers and census extraction; `run_checks.py` records delegated EWP execution inspected by the principal reviewer. `report_tables.py` is an editorial/public-aggregate presentation reducer. Preserve each displayed relative filename when extracting. SHA-256 values bind the exact UTF-8 text, including its final newline. For the three portable EWP scripts, executed-source SHA-256 values identify the original executed versions; archived portable-script SHA-256 values bind the displayed versions. The other ten scripts and their hashes are unchanged. Original execution receipts concern the original scripts; archival filing did not rerun them. Output filenames refer to reproducible scratch products, not additional deliverables.

<a id="appendix-b-1"></a>

### B.1 Frozen assessment logic and later amendments



**Readable rendering of the frozen record.** Later corrections remain in the main review and the documented amendments.

##### Pre-audit logic, 2026-10-18

Frozen before primary-result audit. Reviewer: GPT-6 Astra Pro in ChatGPT, shell/Python available. PW 9dd456be7fd797b9cda0a2bbf50d1ac717d72835; EWP 4284e9460c8057053e95de7cfa2fb3590e68e9db. No OpenFOAM execution or external/private collection access. Protected targets off-limits. Original prompt has placeholders rather than drafting SHAs; do not invent them.

###### Decision rules

1. Preserve original contract outcomes. Assess uncertainty resolution, named-use usefulness and adoption separately. A deterministic numerical envelope is not a statistical confidence interval; missing input/experimental uncertainty prevents a complete validation uncertainty estimate.
2. Keep calibration, post-fit reconstruction, independent physical validation and numerical qualification distinct. Compute comparison error S-D in original units and on the exact scored support. Never derive an acceptance margin from the observed residual. Paired improvements must include every declared comparator and adverse panel and account for dependence; single-shot deletion measures sensitivity, not independent replication or significance.
3. Maturity profiles are (representation, physics, code verification, solution verification, physical validation, uncertainty), each 0 absent/unsupported; 1 partial/exploratory; 2 systematic within a declared bounded domain; 3 independently corroborated and sufficiently comprehensive for the stated intended use. They are reviewer judgments with supporting locators, not aggregate scores.
4. Census all main first-parent integrations in rolling 30/60-day windows ending at review-start UTC; separately distinguish true merge commits and squash integrations. Use primary purpose + changed paths/declarations to assign one category: governing physics, numerical methods, retained-evidence analysis, assurance/governance, documentation/status, product/UI. Publish per-change classifications and alternatives for mixed changes. Counts and changed lines are activity proxies, never person-hours.
5. Audit all headline-result families and downstream closures; sample remaining gates and task bundles without replacement using Python random.Random(20261018), sorted eligible names. Planned sample: eight remaining registry gates, four remaining quick-only gates if available, four remaining public task bundles per repository. Eligibility excludes protected-target paths, restricted source and tasks already selected for headline audit. Record actual frame and selected names before reading their results.
6. Severity follows consequence: P0 only current correctness or materially misleading claims; P1 the next question that can change a scientific decision; P2 useful consolidation; P3 optional. No new experiment without a named unresolved decision and review of existing holdings. No duplicate completed/in-flight tasks. No blanket threshold changes.
7. Apply SCI-GOV-001 circuit breakers to three major recent lanes with distinct scientific outcomes. Count controls that caught material scientific/identity errors versus assurance-only changes, without reverse-engineering all governance machinery.

###### H1 predeclared assessment

Separate H1a (local fluid approaches chemical equilibrium before exit), H1b (whole-cup endpoint has small extraction-rate sensitivity at fixed inventory and equilibrium law), and H1c (hydraulics + collected-mass endpoint suffice for useful prediction across conditions/species). H1b does not entail H1a or H1c. At fixed beverage mass, mass conservation and finite inventory can flatten endpoint response even while fraction histories retain kinetic sensitivity. Support would require correct out-of-fit fraction/species responses and weak rate sensitivity over an independently defensible rate range under controlled hydraulics. Refutation of broad H1 would be a reproducible fraction/species/flow or temperature effect exceeding scored-support uncertainty that hydraulics/inventory/equilibrium-only models cannot account for. Failure to identify rates from whole-cup endpoints alone supports nonidentifiability, not instantaneous equilibrium. Equilibrium must refer to a specified solute, temperature and accessible inventory. Derive sign/domain consequences before proposing a mechanism.

###### Prior exposure and amendments

The conversation supplies owner history and summaries of earlier tasks, and the attachment includes orientation results. These cannot be un-seen. Earlier review files will not be opened until Phase 3. The independent audit will trace claims to primary artifacts regardless of summaries. Record any changes to these criteria, samples or interpretations with reason in final methodology.

<details>
<summary>Show byte-exact frozen Markdown source 1</summary>

```markdown
# Pre-audit logic, 2026-10-18

Frozen before primary-result audit. Reviewer: GPT-6 Astra Pro in ChatGPT, shell/Python available. PW 9dd456be7fd797b9cda0a2bbf50d1ac717d72835; EWP 4284e9460c8057053e95de7cfa2fb3590e68e9db. No OpenFOAM execution or external/private collection access. Protected targets off-limits. Original prompt has placeholders rather than drafting SHAs; do not invent them.

## Decision rules

1. Preserve original contract outcomes. Assess uncertainty resolution, named-use usefulness and adoption separately. A deterministic numerical envelope is not a statistical confidence interval; missing input/experimental uncertainty prevents a complete validation uncertainty estimate.
2. Keep calibration, post-fit reconstruction, independent physical validation and numerical qualification distinct. Compute comparison error S-D in original units and on the exact scored support. Never derive an acceptance margin from the observed residual. Paired improvements must include every declared comparator and adverse panel and account for dependence; single-shot deletion measures sensitivity, not independent replication or significance.
3. Maturity profiles are (representation, physics, code verification, solution verification, physical validation, uncertainty), each 0 absent/unsupported; 1 partial/exploratory; 2 systematic within a declared bounded domain; 3 independently corroborated and sufficiently comprehensive for the stated intended use. They are reviewer judgments with supporting locators, not aggregate scores.
4. Census all main first-parent integrations in rolling 30/60-day windows ending at review-start UTC; separately distinguish true merge commits and squash integrations. Use primary purpose + changed paths/declarations to assign one category: governing physics, numerical methods, retained-evidence analysis, assurance/governance, documentation/status, product/UI. Publish per-change classifications and alternatives for mixed changes. Counts and changed lines are activity proxies, never person-hours.
5. Audit all headline-result families and downstream closures; sample remaining gates and task bundles without replacement using Python random.Random(20261018), sorted eligible names. Planned sample: eight remaining registry gates, four remaining quick-only gates if available, four remaining public task bundles per repository. Eligibility excludes protected-target paths, restricted source and tasks already selected for headline audit. Record actual frame and selected names before reading their results.
6. Severity follows consequence: P0 only current correctness or materially misleading claims; P1 the next question that can change a scientific decision; P2 useful consolidation; P3 optional. No new experiment without a named unresolved decision and review of existing holdings. No duplicate completed/in-flight tasks. No blanket threshold changes.
7. Apply SCI-GOV-001 circuit breakers to three major recent lanes with distinct scientific outcomes. Count controls that caught material scientific/identity errors versus assurance-only changes, without reverse-engineering all governance machinery.

## H1 predeclared assessment

Separate H1a (local fluid approaches chemical equilibrium before exit), H1b (whole-cup endpoint has small extraction-rate sensitivity at fixed inventory and equilibrium law), and H1c (hydraulics + collected-mass endpoint suffice for useful prediction across conditions/species). H1b does not entail H1a or H1c. At fixed beverage mass, mass conservation and finite inventory can flatten endpoint response even while fraction histories retain kinetic sensitivity. Support would require correct out-of-fit fraction/species responses and weak rate sensitivity over an independently defensible rate range under controlled hydraulics. Refutation of broad H1 would be a reproducible fraction/species/flow or temperature effect exceeding scored-support uncertainty that hydraulics/inventory/equilibrium-only models cannot account for. Failure to identify rates from whole-cup endpoints alone supports nonidentifiability, not instantaneous equilibrium. Equilibrium must refer to a specified solute, temperature and accessible inventory. Derive sign/domain consequences before proposing a mechanism.

## Prior exposure and amendments

The conversation supplies owner history and summaries of earlier tasks, and the attachment includes orientation results. These cannot be un-seen. Earlier review files will not be opened until Phase 3. The independent audit will trace claims to primary artifacts regardless of summaries. Record any changes to these criteria, samples or interpretations with reason in final methodology.
```

</details>


The preserved freeze predates primary-result audit. Later amendments: bin three became scientific analysis/comparison with retained/new/source subtypes; `generated` was removed from the PW task frame before result reads; the duplicate EWP frame was not executed; parallel per-agent Phase 2/3 boundaries replaced a single global boundary; final reconciliation corrected #321’s completed-witness status; the chronology reducer’s explanatory string was corrected to distinguish equal commits from strict precedence, without changing numerical results.

#### Frozen view: review_work/notes/ROOT_PHASE2_INDEPENDENT_VIEW.md

SHA-256 `84f65027fa0e3aa3830e1f6f34ff0502c4d286dc41b552b69310b178081f85ce`. Historical snapshot; any conflict with final findings is resolved by the documented amendments.

**Readable rendering of the frozen record.** Later corrections remain in the main review and the documented amendments.

##### Root independent view before Phase 3

PW 9dd456be7fd797b9cda0a2bbf50d1ac717d72835; EWP 4284e9460c8057053e95de7cfa2fb3590e68e9db. Earlier review files not yet opened by root. Root read orientation summaries; sub-agents performed scope-specific independent audits and are allowed reconciliation only after saving their own independent snapshots. Original attachment has no filled drafting SHA.

1. Registry: executed 28 components, 79 statically defined gate functions, 66 wired and 13 outside registry. Actual registry run: PASS66 + ACKNOWLEDGED_EXCEPTION1, 157.54 s on Python3.12.14/NumPy2.5.4/SciPy1.18.1. Metadata distribution code_verification6, within_campaign_held_out1, qualitative_capacity5, source_curve_reproduction7, post_fit_reconstruction5, exploratory_synthesis1, sign_or_compatibility3; zero controlled_independent. This is component metadata, not a census of every independently measured datum.
2. Cameron code conserves through matching solid/liquid exchange; source per-grain inventory 118, printed geometry retained. Off-knot GS1.1 N20/M12 EY-minus-solid=-1.6698e-13 pp. Ceiling24.467473%; printed L18.715912mm vs bulk-identity22.625620mm. Do not repair source ambiguity speculatively. Existing tests/test_cameron_inventory.py protects off-knot geometry and independent inventory. Live registry conservation allowance0.5pp is too loose for its stated code-verification role:0.1g at20g dose,2.04% initial inventory. Historical interpolation gaps up to0.152326pp fit inside it, although those are now repaired. Stronger test exists, so propose small consolidation, not another solver-repair programme.
3. Guided Pull is one saturated fixed-temperature Cameron chain with constant prescribed overpressure, measured grinder-specific flux interpolation; prescribed beverage mass determines t=Mout/(rho*A*q), so collected endpoint is not a prediction. Current product implementation and docs disclose source reproduction unresolved and historical errors. Historical6.480780/7.102391pp values not recomputed at this stage, label secondary pending evidence access.
4. Gate distinctions matter. Wadsworth aggregate collapse GM0.912698 over21 rows passes[.7,1.2] while ratios range.654168..1.755360; five outside±30%. This gate constrains mean log bias, not pointwise scatter or validation. Roman sphere analytic error.000120 vs.001 useful numerical gate. Roman parameter-free MPE gate is reported-source metric transcription, not current model accuracy. Maillé fast-fraction ratio4.6..9.0 is intentional negative compatibility result. Grudeva2026 quick gate actually computes analytic and coupled cases, not saved PASS lookup. First-drip bracket6.4..7.8 vs7.018 is in-sample compatibility given fitted kappa, despite stale 'parameter-free' wording in gate/card. Foster CT gate passes s4/8 and H5/8 within max(reported error,.5mm), plus near-exact fitted curve reproduction; do not call this independently validated CT.
5. Grudeva008 root recomputed stored witnesses for four pairs×11 families: all within frozen bounds, maximum used fraction.215109, zero unavailable; full arrays unavailable, no fresh solver. Grudeva009 root recomputed72 included residuals out of124 rows,52 excluded;17 same-direction common failures, retained refinements preserve17, first selected time3.2. Event residual+.120849823 with source read bound.0100251 and refined solver movement~1e-5 confirms numerical-publication mismatch on declared case. No physical validation or established author error.
6. H1 locus in prompt is SUPERSEDED by _V2 plan. Local early/peak TDS statistic in harness.py85-102 already correctly says it cannot identify equilibrium. Whole-cup response saturation can arise from inventory/observation integration; no logical implication of local equilibration for all compounds. Existing fraction chemistry is more informative than another endpoint aggregate. Any recommendation must clear current mass/chemistry task duplicate search and not access Angeloni protected targets.
7. Status authority current.json reproduces its page but contains old25-component and Grudeva-rights-blocked claims, inconsistent with live28 and existing documented permission. CURRENT.md says #335 policy pending merge despite commit ancestry. Generation freshness must be separated from semantic freshness. EWP core negative pressure status remains credible; exact scope needs own source/retained record checks.
8. No blanket threshold relaxation warranted. Absolute adequacy, paired descriptive gain, numerical resolution, sample sensitivity, and practical decision utility require different requirements. No more experiments can be justified from unavailable external collection alone.

###### Method change
The six-category development taxonomy is amended before aggregate reporting: category3=scientific analysis/comparison, with separate retained-output-only / new unchanged-equation evaluation / source-data-qualification subtypes. Otherwise new scientific runs with unchanged equations would be falsely counted as retained-output analysis. No scoring rule changes.

###### Outstanding at snapshot
PW full quick test still running; EWP safe checks delegated. Correction addenda T01-T12 and earlier review reconciliation pending. Threshold sample is in gate_sample.json; extra quick-only samples currently executing. P1 priorities tentative until duplication checks and Phase3.

<details>
<summary>Show byte-exact frozen Markdown source 2</summary>

```markdown
# Root independent view before Phase 3

PW 9dd456be7fd797b9cda0a2bbf50d1ac717d72835; EWP 4284e9460c8057053e95de7cfa2fb3590e68e9db. Earlier review files not yet opened by root. Root read orientation summaries; sub-agents performed scope-specific independent audits and are allowed reconciliation only after saving their own independent snapshots. Original attachment has no filled drafting SHA.

1. Registry: executed 28 components, 79 statically defined gate functions, 66 wired and 13 outside registry. Actual registry run: PASS66 + ACKNOWLEDGED_EXCEPTION1, 157.54 s on Python3.12.14/NumPy2.5.4/SciPy1.18.1. Metadata distribution code_verification6, within_campaign_held_out1, qualitative_capacity5, source_curve_reproduction7, post_fit_reconstruction5, exploratory_synthesis1, sign_or_compatibility3; zero controlled_independent. This is component metadata, not a census of every independently measured datum.
2. Cameron code conserves through matching solid/liquid exchange; source per-grain inventory 118, printed geometry retained. Off-knot GS1.1 N20/M12 EY-minus-solid=-1.6698e-13 pp. Ceiling24.467473%; printed L18.715912mm vs bulk-identity22.625620mm. Do not repair source ambiguity speculatively. Existing tests/test_cameron_inventory.py protects off-knot geometry and independent inventory. Live registry conservation allowance0.5pp is too loose for its stated code-verification role:0.1g at20g dose,2.04% initial inventory. Historical interpolation gaps up to0.152326pp fit inside it, although those are now repaired. Stronger test exists, so propose small consolidation, not another solver-repair programme.
3. Guided Pull is one saturated fixed-temperature Cameron chain with constant prescribed overpressure, measured grinder-specific flux interpolation; prescribed beverage mass determines t=Mout/(rho*A*q), so collected endpoint is not a prediction. Current product implementation and docs disclose source reproduction unresolved and historical errors. Historical6.480780/7.102391pp values not recomputed at this stage, label secondary pending evidence access.
4. Gate distinctions matter. Wadsworth aggregate collapse GM0.912698 over21 rows passes[.7,1.2] while ratios range.654168..1.755360; five outside±30%. This gate constrains mean log bias, not pointwise scatter or validation. Roman sphere analytic error.000120 vs.001 useful numerical gate. Roman parameter-free MPE gate is reported-source metric transcription, not current model accuracy. Maillé fast-fraction ratio4.6..9.0 is intentional negative compatibility result. Grudeva2026 quick gate actually computes analytic and coupled cases, not saved PASS lookup. First-drip bracket6.4..7.8 vs7.018 is in-sample compatibility given fitted kappa, despite stale 'parameter-free' wording in gate/card. Foster CT gate passes s4/8 and H5/8 within max(reported error,.5mm), plus near-exact fitted curve reproduction; do not call this independently validated CT.
5. Grudeva008 root recomputed stored witnesses for four pairs×11 families: all within frozen bounds, maximum used fraction.215109, zero unavailable; full arrays unavailable, no fresh solver. Grudeva009 root recomputed72 included residuals out of124 rows,52 excluded;17 same-direction common failures, retained refinements preserve17, first selected time3.2. Event residual+.120849823 with source read bound.0100251 and refined solver movement~1e-5 confirms numerical-publication mismatch on declared case. No physical validation or established author error.
6. H1 locus in prompt is SUPERSEDED by _V2 plan. Local early/peak TDS statistic in harness.py85-102 already correctly says it cannot identify equilibrium. Whole-cup response saturation can arise from inventory/observation integration; no logical implication of local equilibration for all compounds. Existing fraction chemistry is more informative than another endpoint aggregate. Any recommendation must clear current mass/chemistry task duplicate search and not access Angeloni protected targets.
7. Status authority current.json reproduces its page but contains old25-component and Grudeva-rights-blocked claims, inconsistent with live28 and existing documented permission. CURRENT.md says #335 policy pending merge despite commit ancestry. Generation freshness must be separated from semantic freshness. EWP core negative pressure status remains credible; exact scope needs own source/retained record checks.
8. No blanket threshold relaxation warranted. Absolute adequacy, paired descriptive gain, numerical resolution, sample sensitivity, and practical decision utility require different requirements. No more experiments can be justified from unavailable external collection alone.

## Method change
The six-category development taxonomy is amended before aggregate reporting: category3=scientific analysis/comparison, with separate retained-output-only / new unchanged-equation evaluation / source-data-qualification subtypes. Otherwise new scientific runs with unchanged equations would be falsely counted as retained-output analysis. No scoring rule changes.

## Outstanding at snapshot
PW full quick test still running; EWP safe checks delegated. Correction addenda T01-T12 and earlier review reconciliation pending. Threshold sample is in gate_sample.json; extra quick-only samples currently executing. P1 priorities tentative until duplication checks and Phase3.
```

</details>


#### Frozen view: review_work/data/PHASE2_INDEPENDENT_VIEW.md

SHA-256 `68820b051799dad5262d8d8311e0c69e813b38022e5b5f524545c8a05ffcb823`. Historical snapshot; any conflict with final findings is resolved by the documented amendments.

**Readable rendering of the frozen record.** Later corrections remain in the main review and the documented amendments.

##### Independent data/threshold/H1 assessment before Phase 3

Frozen 2026-10-18; PW 9dd456be7fd797b9cda0a2bbf50d1ac717d72835; EWP 4284e9460c8057053e95de7cfa2fb3590e68e9db. No earlier-review files or October decision-resolution addenda read. Owner-supplied orientation and prior-chat summaries were unavoidably known. Reading the requested pivot-plan H1 section exposed its qualitative interpretation and historical aggregate fitting statements; no protected data file/API was read. Angeloni denied paths/APIs and protected integrity tests were avoided. The source guide itself identifies all Angeloni material as hash-only; aggregate task outputs whose semantic targets could compromise this boundary will not be inspected.

###### Independent findings

1. Registry arithmetic confirms 118 manifest entries and 46 family-register entries, of which 43 say PACKAGED_IN_REPOSITORY. These are not 46 independent scientific campaigns. At least PANNUSCH2024 (MENDELEY REPO) and WADSWORTH2026_TABLE1 are alias/partial representations of existing lineages. The owner external snapshot records 31,503 files, not observations; 225 experimental-measurement files and 596 machine-log files do not determine shot counts. Raw Pannusch originals, Grudeva per-shot chemistry, native rheology histories and the Visualizer corpus are absent from this review environment, while public aggregates and metadata are available. A catalogue can neither prove corpus exhaustion nor independent validation eligibility.

2. The family-register target metadata need reconciliation: ANGELONI2023 has target_exposure=UNKNOWN, consumed_comparison_status=UNKNOWN and blocked_uses=[] although the explicit access policy prohibits semantic targets. Its historical-use descriptions include an independent multispecies target and older transfer gates. This metadata inconsistency should be corrected without consulting target values. Pannusch has explicit TARGET_EXPOSED status, but Schmieder's alias still says UNKNOWN. Recent Grudeva 13-shot/11-eligible work is not reflected by its physical_shot_count_if_known=UNKNOWN. This is a routing/claims issue, not a missing experiment.

3. The apparent negative extraction headlines hide useful conditional predictors, but the current original reports do explain them. MASS-006 C2's complete primary mean shot RMSE is 0.480034144200 pp with signed bias -0.395566834334 pp, and gains versus C0/C1/legacy are 0.172021159763/0.117553081375/0.299566675676 pp. It passes the declared research budgets. This is same-source, target-exposed, early-assay-conditioned prediction on 12 shots and 48 suffix intervals, not hydraulics, kinetic mechanism, inventory closure or independent validation. C05 and full C08 are adverse for C2; incomplete C07 cannot establish full-flow adequacy.

4. Caffeine S2 reduces primary RMSE versus S1/D0/S0 by 0.0270208431445/0.0670900580902/0.0903970941032 mg/g. Historical incremental gates fail correctly because each requires 0.10 mg/g plus 15%, condition wins and a bias constraint; versus S1 only 2/4 condition wins occur. All arms are adequate to the original 0.50/0.25 mg/g budgets. Thus 'no earned complexity' is true under that chosen contract and is not 'no predictive improvement.' Temperature reverses the S2–D0 comparison (-0.00476104388817 mg/g), and flow support is partial. No independent practical derivation of the absolute 0.10 margin is evident in the protocol. It is a research choice, neither assay uncertainty nor a validated utility boundary.

5. In 5CQA ASSAY-002, L12 improves average primary RMSE over both matched single-assay arms, by 0.0462129751017 and 0.0519725835585 mg/g. Nevertheless L12's signed bias is -0.254372361749 mg/g, over twice the 0.125 mg/g bias budget, and R=0.297495166244 versus 0.25. Its failure is not just a marginal RMS miss. Temperature L12/L1M is adverse. Earlier mass-only, TDS-conditioned and first-assay 5CQA families also fail; these are bounded tested families, not proof of universal chemical impossibility. TR-D0 trigonelline clearly improves over a constant mass-coordinate control (primary gain 0.594953143274 mg/g and signed bias -0.0266551689034) with all primary conditions adequate. A mass-shape learner's success is not equilibrium verification.

6. Reaggregation of complete condition metrics across seven public case families reproduces 312 retained panel metrics with maximum absolute delta 4.44e-16. It does not independently recreate private per-shot residuals, assay errors or fitted states. Per-interval numerical allowances are tiny (generally around 1e-11 mg/g or 1e-12 pp after propagation), while analytical and source/input uncertainties remain incomplete. A full u_val cannot be computed legitimately from these public aggregate scores. Failure against a stipulated research threshold may be computationally resolved, but physical model error is not quantified solely by tiny integration tolerances.

7. Rheology 008/009/010 concern numerical reduction against C, a computational source-conditioned reference. E2 means one communicating radial cell per zone at each axial station, 1,024 base cells in 008, not a two-state model and not the full EWP solver token E2 used elsewhere. 008's three candidates give 72/72 primary passes; 009 gives 24/24; 010 gives 24/24. They preserve finite pressure/law/geometry/mass supports and demonstrate bounded numerical usefulness. 010's secondary two UP fraction contrasts (about 4.17 and 4.73 pp) remain UNRESOLVED because empirical allowances exceed 0.02 pp, the fixed 20%-of-0.1-budget precision gate. Their M-u intervals are still far above 0.1. Preserve the original precision outcome and report the separation separately: demanding higher precision cannot plausibly change which side of this nominal boundary those retained finite numerical envelopes occupy. These are not experimental confidence intervals.

8. Rheology 011 already tests the changed arrangement while preserving the permeability histogram. All eight differences plus allowances remain below their budgets and its conditional full E2 run was correctly not triggered. 010 changed distribution/residence times as well as radial position; 011 is the existing control against interpreting 010 as unique lateral-position physics. No repeat of this question is needed. The E2 reduction remains unqualified for in-puck spatial assay contrasts whose cuts share one radial cell.

9. Existing transfer blockers differ. Maillé's 105 tabulated cells are present, but the replicate-selected-max observer is unidentified from pooled late summaries; this does not reject two-rate kinetics. Moroney's joint deep calibration fails across the declared finite family even where shallow outlet reconstruction looks good; shallow error is not independent validation after bad calibration. Smrke has digitized marker estimates and treatment groups without unique shot identities, so pixel points cannot be bootstrapped as physical shots. These are source/observable/model issues, not a reason to enlarge all thresholds.

10. H1a (local equilibrium before flushing), H1b (endpoint rate saturation), H1c (hydraulics/endpoint sufficiency) are distinct. The Pannusch code contains explicit finite exchange and equilibrium initial conditions; tuning/fitting a shoulder does not independently establish local equilibrium in real espresso. For a simple parcel dc/dt=k(c_eq-c), c/c_eq=1-exp(-k tau) and logarithmic rate sensitivity is Da/(exp(Da)-1), Da=k tau. A large Da is sufficient for local equilibrium under that fixed-reservoir approximation; a flat endpoint can also arise from inventory exhaustion, endpoint conditioning, or rate/inventory confounding. The current mass/caffeine/5CQA tasks condition on measured early chemistry and measured mass, which already contain kinetic information. Their success cannot demonstrate hydraulics-only sufficiency. Most informative available-data analysis is a species-resolved, equal-input comparison of equilibrium-limit and finite-rate fractional predictions on existing nonprotected Pannusch/Schmieder interventions, with numerical qualification, early-input propagation, fixed support and all adverse conditions; no need to commission new data until the external source audit establishes the limiting join. Check current species issues before turning this into a new recommendation.

###### Existing-work warning

MASS-STOP-DECISION-001 and model-engineering mass-stop bundles already exist on the pinned PW main. The original stop-decision JSON says FROZEN_C2_STOPPING_DECISION_ADEQUATE_ON_DECLARED_OFFLINE_CONTRACT; any next-task proposal must first inspect these bundles and open PRs. No stopped-source or threshold task should be silently restarted.

###### Reproduction

`python review_work/data/audit_primary.py` writes `review_work/data/primary_audit.json`. This reads only explicitly allowlisted public nonprotected aggregate JSON files and metadata. All results passed to the parent remain [D-] until rechecked there.

<details>
<summary>Show byte-exact frozen Markdown source 3</summary>

```markdown
# Independent data/threshold/H1 assessment before Phase 3

Frozen 2026-10-18; PW 9dd456be7fd797b9cda0a2bbf50d1ac717d72835; EWP 4284e9460c8057053e95de7cfa2fb3590e68e9db. No earlier-review files or October decision-resolution addenda read. Owner-supplied orientation and prior-chat summaries were unavoidably known. Reading the requested pivot-plan H1 section exposed its qualitative interpretation and historical aggregate fitting statements; no protected data file/API was read. Angeloni denied paths/APIs and protected integrity tests were avoided. The source guide itself identifies all Angeloni material as hash-only; aggregate task outputs whose semantic targets could compromise this boundary will not be inspected.

## Independent findings

1. Registry arithmetic confirms 118 manifest entries and 46 family-register entries, of which 43 say PACKAGED_IN_REPOSITORY. These are not 46 independent scientific campaigns. At least PANNUSCH2024 (MENDELEY REPO) and WADSWORTH2026_TABLE1 are alias/partial representations of existing lineages. The owner external snapshot records 31,503 files, not observations; 225 experimental-measurement files and 596 machine-log files do not determine shot counts. Raw Pannusch originals, Grudeva per-shot chemistry, native rheology histories and the Visualizer corpus are absent from this review environment, while public aggregates and metadata are available. A catalogue can neither prove corpus exhaustion nor independent validation eligibility.

2. The family-register target metadata need reconciliation: ANGELONI2023 has target_exposure=UNKNOWN, consumed_comparison_status=UNKNOWN and blocked_uses=[] although the explicit access policy prohibits semantic targets. Its historical-use descriptions include an independent multispecies target and older transfer gates. This metadata inconsistency should be corrected without consulting target values. Pannusch has explicit TARGET_EXPOSED status, but Schmieder's alias still says UNKNOWN. Recent Grudeva 13-shot/11-eligible work is not reflected by its physical_shot_count_if_known=UNKNOWN. This is a routing/claims issue, not a missing experiment.

3. The apparent negative extraction headlines hide useful conditional predictors, but the current original reports do explain them. MASS-006 C2's complete primary mean shot RMSE is 0.480034144200 pp with signed bias -0.395566834334 pp, and gains versus C0/C1/legacy are 0.172021159763/0.117553081375/0.299566675676 pp. It passes the declared research budgets. This is same-source, target-exposed, early-assay-conditioned prediction on 12 shots and 48 suffix intervals, not hydraulics, kinetic mechanism, inventory closure or independent validation. C05 and full C08 are adverse for C2; incomplete C07 cannot establish full-flow adequacy.

4. Caffeine S2 reduces primary RMSE versus S1/D0/S0 by 0.0270208431445/0.0670900580902/0.0903970941032 mg/g. Historical incremental gates fail correctly because each requires 0.10 mg/g plus 15%, condition wins and a bias constraint; versus S1 only 2/4 condition wins occur. All arms are adequate to the original 0.50/0.25 mg/g budgets. Thus 'no earned complexity' is true under that chosen contract and is not 'no predictive improvement.' Temperature reverses the S2–D0 comparison (-0.00476104388817 mg/g), and flow support is partial. No independent practical derivation of the absolute 0.10 margin is evident in the protocol. It is a research choice, neither assay uncertainty nor a validated utility boundary.

5. In 5CQA ASSAY-002, L12 improves average primary RMSE over both matched single-assay arms, by 0.0462129751017 and 0.0519725835585 mg/g. Nevertheless L12's signed bias is -0.254372361749 mg/g, over twice the 0.125 mg/g bias budget, and R=0.297495166244 versus 0.25. Its failure is not just a marginal RMS miss. Temperature L12/L1M is adverse. Earlier mass-only, TDS-conditioned and first-assay 5CQA families also fail; these are bounded tested families, not proof of universal chemical impossibility. TR-D0 trigonelline clearly improves over a constant mass-coordinate control (primary gain 0.594953143274 mg/g and signed bias -0.0266551689034) with all primary conditions adequate. A mass-shape learner's success is not equilibrium verification.

6. Reaggregation of complete condition metrics across seven public case families reproduces 312 retained panel metrics with maximum absolute delta 4.44e-16. It does not independently recreate private per-shot residuals, assay errors or fitted states. Per-interval numerical allowances are tiny (generally around 1e-11 mg/g or 1e-12 pp after propagation), while analytical and source/input uncertainties remain incomplete. A full u_val cannot be computed legitimately from these public aggregate scores. Failure against a stipulated research threshold may be computationally resolved, but physical model error is not quantified solely by tiny integration tolerances.

7. Rheology 008/009/010 concern numerical reduction against C, a computational source-conditioned reference. E2 means one communicating radial cell per zone at each axial station, 1,024 base cells in 008, not a two-state model and not the full EWP solver token E2 used elsewhere. 008's three candidates give 72/72 primary passes; 009 gives 24/24; 010 gives 24/24. They preserve finite pressure/law/geometry/mass supports and demonstrate bounded numerical usefulness. 010's secondary two UP fraction contrasts (about 4.17 and 4.73 pp) remain UNRESOLVED because empirical allowances exceed 0.02 pp, the fixed 20%-of-0.1-budget precision gate. Their M-u intervals are still far above 0.1. Preserve the original precision outcome and report the separation separately: demanding higher precision cannot plausibly change which side of this nominal boundary those retained finite numerical envelopes occupy. These are not experimental confidence intervals.

8. Rheology 011 already tests the changed arrangement while preserving the permeability histogram. All eight differences plus allowances remain below their budgets and its conditional full E2 run was correctly not triggered. 010 changed distribution/residence times as well as radial position; 011 is the existing control against interpreting 010 as unique lateral-position physics. No repeat of this question is needed. The E2 reduction remains unqualified for in-puck spatial assay contrasts whose cuts share one radial cell.

9. Existing transfer blockers differ. Maillé's 105 tabulated cells are present, but the replicate-selected-max observer is unidentified from pooled late summaries; this does not reject two-rate kinetics. Moroney's joint deep calibration fails across the declared finite family even where shallow outlet reconstruction looks good; shallow error is not independent validation after bad calibration. Smrke has digitized marker estimates and treatment groups without unique shot identities, so pixel points cannot be bootstrapped as physical shots. These are source/observable/model issues, not a reason to enlarge all thresholds.

10. H1a (local equilibrium before flushing), H1b (endpoint rate saturation), H1c (hydraulics/endpoint sufficiency) are distinct. The Pannusch code contains explicit finite exchange and equilibrium initial conditions; tuning/fitting a shoulder does not independently establish local equilibrium in real espresso. For a simple parcel dc/dt=k(c_eq-c), c/c_eq=1-exp(-k tau) and logarithmic rate sensitivity is Da/(exp(Da)-1), Da=k tau. A large Da is sufficient for local equilibrium under that fixed-reservoir approximation; a flat endpoint can also arise from inventory exhaustion, endpoint conditioning, or rate/inventory confounding. The current mass/caffeine/5CQA tasks condition on measured early chemistry and measured mass, which already contain kinetic information. Their success cannot demonstrate hydraulics-only sufficiency. Most informative available-data analysis is a species-resolved, equal-input comparison of equilibrium-limit and finite-rate fractional predictions on existing nonprotected Pannusch/Schmieder interventions, with numerical qualification, early-input propagation, fixed support and all adverse conditions; no need to commission new data until the external source audit establishes the limiting join. Check current species issues before turning this into a new recommendation.

## Existing-work warning

MASS-STOP-DECISION-001 and model-engineering mass-stop bundles already exist on the pinned PW main. The original stop-decision JSON says FROZEN_C2_STOPPING_DECISION_ADEQUATE_ON_DECLARED_OFFLINE_CONTRACT; any next-task proposal must first inspect these bundles and open PRs. No stopped-source or threshold task should be silently restarted.

## Reproduction

`python review_work/data/audit_primary.py` writes `review_work/data/primary_audit.json`. This reads only explicitly allowlisted public nonprotected aggregate JSON files and metadata. All results passed to the parent remain [D-] until rechecked there.
```

</details>


#### Frozen view: review_work/ewp/PHASE2_INDEPENDENT_VIEW.md

SHA-256 `7c05e6acf5ca4dc5b0148385ba526230482dc1ee32ec1514adcac90fb8a4bd52`. Historical snapshot; any conflict with final findings is resolved by the documented amendments.

**Readable rendering of the frozen record.** Later corrections remain in the main review and the documented amendments.

##### EWP independent view before Phase 3

Recorded after EWP Phase 1 orientation and primary code/result inspection; prior-review files and October corrective bundles have not been opened by this subagent. The prompt and EWP onboarding exposed summaries that cannot be un-seen. This snapshot preserves the judgment before reconciliation. Pin: EWP `4284e9460c8057053e95de7cfa2fb3590e68e9db`; PW `9dd456be7fd797b9cda0a2bbf50d1ac717d72835`. All results below are delegated `[D−]` until independently rechecked by root.

1. **The hydraulic shortfall survives separation of software and science.** Current C++ Darcy flow, transport and source signs/units agree with their stated equations. WP03-002 correctly removed a continuous scalar-flow approximation error from the discrete Picard stopping rule; current C:L2783–2799 retains it as a diagnostic. Its corrected full-solver cases still reverse the source 5/9/11-bar ranking. Finite-porosity compaction decreases local permeability with effective stress, but the integrated pressure–flow relation is nondecreasing. These are compatible facts, not a sign contradiction.

2. **SCI-MD-010 is a reduced-component comparison, not a full-solver verdict.** Independently recomputing 56 retained brew predictions over 11 condition-held-out folds gives mean condition RMSE B0=0.5916020493, B1 quadratic=0.2936269557, E1 machine-coupled fixed Darcy=0.5756564539 g/s. Normalized B1−E1 gain −0.1456924081 has the exact retained nested bootstrap interval [−0.2487589901,−0.0361631740]; low-pressure interval [−0.2669334833,+0.0297352042]. No practical accuracy margin is implied by this relative ranking. Full EWP E2 is unadjudicated because this lane lacks its qualified inputs.

3. **SCI-MD-011 contains meaningful counterevidence to an undifferentiated negative headline.** P1 universal poroelastic mean condition RMSE=0.2742823595 g/s, slightly better than B1=0.2936269557. Its normalized B1−P1 gain +0.0086955885 has the exact retained interval [−0.0402107972,+0.0629656016]; low-pressure interval [−0.0828338941,−0.0032617161] favors B1. Thus no stable overall gain is established, but the candidate has descriptive predictive content. E2C has only ten complete folds and cannot be adjudicated from their attractive partial score.

4. **E2C root repair and turnover are different questions.** SCI-MD-012 retains six 13-bar endpoint rows, with five outside the frozen coupled pressure ceiling. The family admits a root after an algebraic Pc increase of about 1.53% within its original bounds. That witness is not a fit. The source and C++ closures give `dJ/dx=(1−x)^3/(1−Phi*x)>=0` for `0<=x<=1,0<Phi<1`; universal derivative is `4(1−x)^3`. Positive Qc/Pc rescaling cannot introduce turnover. The positive quadratic machine drop preserves derivative sign. Retirement from this specific development priority is justified independently of fit failure; general poroelastic architecture is not rejected.

5. **The directional gate requires precise labeling.** The declared requirement “NONPOSITIVE_OR_SATURATING” is implemented as predicted slope `<=0`. For a strictly increasing saturating family it is effectively a turnover/flat-slope test, not a general test of useful saturation approximation. Retrospective revision of its threshold would not earn adoption: the gain remains uncertain and the observed high-pressure direction is negative. On the actual three high-pressure condition means (9,11,13 nominal bar), independently propagated between-brew repeatability gives slope −0.0655064126 and standard uncertainty 0.0137346389 g/s/bar. This assumes independent group mean errors and fixed measured pressure coordinates; it excludes pressure uncertainty and machine-calibration covariance, hence is not full validation uncertainty. P1 slope is +0.0161203010, B1 −0.3400461982, E1 +0.3285343911. A correct sign alone plainly does not establish accurate slope magnitude.

6. **Optional concentration-dependent viscosity is a substantial existing capability missing from the prompt's compact feature list.** The 5,793 C++/header lines include local lagged μ(c) and autonomous bulk-state viscosity. Production startup checks restrict coupling to 90°C, rho965, initial saturation, static Darcy, and selected uniform/axial/radial prescribed-pressure paths. Compaction, dissolution-indexed permeability, indexed species, dry wetting and arbitrary combinations are not currently integrated with viscosity. This materially limits the whole-process interpretation of positive rheology reduction results; it does not erase their computational value.

7. **H1 remains divided.** The finite source is `R=k*M*max(1−c/Csat,0)`, one-way and inventory-capped. It is not a thermodynamic equilibrium proof or general discrete maximum principle. The documented coarse-step overshoot is algebraically reproducible and already disclosed. A useful mass-coordinate empirical predictor does not establish that pore liquid reaches equilibrium. EWP008 reports an 0.080114 normalized fraction-shape change with inventory scale versus a 1e-6 invariance requirement; EWP009 response qualification fails at 0.0825543 versus0.02. Neither compares eligible physical target values, and neither rejects extraction chemistry generally. These results constrain using normalized fractions to evade unknown inventory. Local equilibrium, endpoint rate insensitivity and cross-condition hydraulic sufficiency remain separate hypotheses.

8. **The runtime lock is intentionally distinct from active research authority.** Runtime PW is fc61c467 (2026-07-28). CI uses a3428a4 and also needs the2058d0e object; task handoffs can pin later PW code. Current PW capabilities do not automatically become production EWP capabilities. This is a bounded integration choice, not evidence of broken synchronization.

9. **Random sample supports conditional reuse rather than corpus exhaustion.** Seed20261018 selected four of20 eligible public EWP bundles: data fusion, Grudeva clock, porosity prior and Pannusch flow history. Fusion has no common EWP K/boundary support; two porosity alternatives remain source-conditioned. Porosity sensitivity uses an explicit5% engineering floor exceeding its numerical floor. Its result prose, however, labels dimensionless relative effects with dimensional observable names, e.g.0.967997 as first_drip_time_s when the JSON gives actual time9.272604s versus4.711696s. A narrow G0 unit-label correction is warranted. Grudeva MASS wins over TIME/TEMPLATE on retained aggregates but consumes measured beverage mass. Pannusch source instructions and fitted beverage outflow do not establish true inlet-flow history; no eligible nonidentity source boundary was manufactured.

10. **Status maintenance and governance should be proportional.** Several current-entry paragraphs still describe merged September PRs as open/unmerged. The source/model qualification caveats are generally honest; lifecycle status is stale. Do not use this as a reason to re-review frozen scientific bundles. Candidate priorities: make current status truthful; protect useful conditional capabilities in the capability matrix; complete one genuinely discriminating equal-input H1 test if not already covered by an existing lane; request an owner decision on the already-defined Stage F contract only where existing data cannot supply the named absolute closure. No new mechanism sweep, E2C rescue, dependency refresh for its own sake, or repeated radial-reduction task is indicated.

###### Reproduction status at snapshot

`review_work/ewp/run_checks.py`: source manifest and static checks pass; full unit suite still running, with at least one failure to classify after the traceback is emitted. Environment pins match NumPy1.26.4/SciPy1.11.4/jsonschema4.23.0; Python3.12.14 differs from CI3.12.3. Initial package installation failed only because of sandbox network access, then succeeded with approved escalation. No OpenFOAM execution, protected target access, fitting, production mutation, or private collection access. `review_work/ewp/recompute.py` independently recomputes retained errors, loss bootstrap and scored-support repeatability; results in `recomputed.json`.

<details>
<summary>Show byte-exact frozen Markdown source 4</summary>

```markdown
# EWP independent view before Phase 3

Recorded after EWP Phase 1 orientation and primary code/result inspection; prior-review files and October corrective bundles have not been opened by this subagent. The prompt and EWP onboarding exposed summaries that cannot be un-seen. This snapshot preserves the judgment before reconciliation. Pin: EWP `4284e9460c8057053e95de7cfa2fb3590e68e9db`; PW `9dd456be7fd797b9cda0a2bbf50d1ac717d72835`. All results below are delegated `[D−]` until independently rechecked by root.

1. **The hydraulic shortfall survives separation of software and science.** Current C++ Darcy flow, transport and source signs/units agree with their stated equations. WP03-002 correctly removed a continuous scalar-flow approximation error from the discrete Picard stopping rule; current C:L2783–2799 retains it as a diagnostic. Its corrected full-solver cases still reverse the source 5/9/11-bar ranking. Finite-porosity compaction decreases local permeability with effective stress, but the integrated pressure–flow relation is nondecreasing. These are compatible facts, not a sign contradiction.

2. **SCI-MD-010 is a reduced-component comparison, not a full-solver verdict.** Independently recomputing 56 retained brew predictions over 11 condition-held-out folds gives mean condition RMSE B0=0.5916020493, B1 quadratic=0.2936269557, E1 machine-coupled fixed Darcy=0.5756564539 g/s. Normalized B1−E1 gain −0.1456924081 has the exact retained nested bootstrap interval [−0.2487589901,−0.0361631740]; low-pressure interval [−0.2669334833,+0.0297352042]. No practical accuracy margin is implied by this relative ranking. Full EWP E2 is unadjudicated because this lane lacks its qualified inputs.

3. **SCI-MD-011 contains meaningful counterevidence to an undifferentiated negative headline.** P1 universal poroelastic mean condition RMSE=0.2742823595 g/s, slightly better than B1=0.2936269557. Its normalized B1−P1 gain +0.0086955885 has the exact retained interval [−0.0402107972,+0.0629656016]; low-pressure interval [−0.0828338941,−0.0032617161] favors B1. Thus no stable overall gain is established, but the candidate has descriptive predictive content. E2C has only ten complete folds and cannot be adjudicated from their attractive partial score.

4. **E2C root repair and turnover are different questions.** SCI-MD-012 retains six 13-bar endpoint rows, with five outside the frozen coupled pressure ceiling. The family admits a root after an algebraic Pc increase of about 1.53% within its original bounds. That witness is not a fit. The source and C++ closures give `dJ/dx=(1−x)^3/(1−Phi*x)>=0` for `0<=x<=1,0<Phi<1`; universal derivative is `4(1−x)^3`. Positive Qc/Pc rescaling cannot introduce turnover. The positive quadratic machine drop preserves derivative sign. Retirement from this specific development priority is justified independently of fit failure; general poroelastic architecture is not rejected.

5. **The directional gate requires precise labeling.** The declared requirement “NONPOSITIVE_OR_SATURATING” is implemented as predicted slope `<=0`. For a strictly increasing saturating family it is effectively a turnover/flat-slope test, not a general test of useful saturation approximation. Retrospective revision of its threshold would not earn adoption: the gain remains uncertain and the observed high-pressure direction is negative. On the actual three high-pressure condition means (9,11,13 nominal bar), independently propagated between-brew repeatability gives slope −0.0655064126 and standard uncertainty 0.0137346389 g/s/bar. This assumes independent group mean errors and fixed measured pressure coordinates; it excludes pressure uncertainty and machine-calibration covariance, hence is not full validation uncertainty. P1 slope is +0.0161203010, B1 −0.3400461982, E1 +0.3285343911. A correct sign alone plainly does not establish accurate slope magnitude.

6. **Optional concentration-dependent viscosity is a substantial existing capability missing from the prompt's compact feature list.** The 5,793 C++/header lines include local lagged μ(c) and autonomous bulk-state viscosity. Production startup checks restrict coupling to 90°C, rho965, initial saturation, static Darcy, and selected uniform/axial/radial prescribed-pressure paths. Compaction, dissolution-indexed permeability, indexed species, dry wetting and arbitrary combinations are not currently integrated with viscosity. This materially limits the whole-process interpretation of positive rheology reduction results; it does not erase their computational value.

7. **H1 remains divided.** The finite source is `R=k*M*max(1−c/Csat,0)`, one-way and inventory-capped. It is not a thermodynamic equilibrium proof or general discrete maximum principle. The documented coarse-step overshoot is algebraically reproducible and already disclosed. A useful mass-coordinate empirical predictor does not establish that pore liquid reaches equilibrium. EWP008 reports an 0.080114 normalized fraction-shape change with inventory scale versus a 1e-6 invariance requirement; EWP009 response qualification fails at 0.0825543 versus0.02. Neither compares eligible physical target values, and neither rejects extraction chemistry generally. These results constrain using normalized fractions to evade unknown inventory. Local equilibrium, endpoint rate insensitivity and cross-condition hydraulic sufficiency remain separate hypotheses.

8. **The runtime lock is intentionally distinct from active research authority.** Runtime PW is fc61c467 (2026-07-28). CI uses a3428a4 and also needs the2058d0e object; task handoffs can pin later PW code. Current PW capabilities do not automatically become production EWP capabilities. This is a bounded integration choice, not evidence of broken synchronization.

9. **Random sample supports conditional reuse rather than corpus exhaustion.** Seed20261018 selected four of20 eligible public EWP bundles: data fusion, Grudeva clock, porosity prior and Pannusch flow history. Fusion has no common EWP K/boundary support; two porosity alternatives remain source-conditioned. Porosity sensitivity uses an explicit5% engineering floor exceeding its numerical floor. Its result prose, however, labels dimensionless relative effects with dimensional observable names, e.g.0.967997 as first_drip_time_s when the JSON gives actual time9.272604s versus4.711696s. A narrow G0 unit-label correction is warranted. Grudeva MASS wins over TIME/TEMPLATE on retained aggregates but consumes measured beverage mass. Pannusch source instructions and fitted beverage outflow do not establish true inlet-flow history; no eligible nonidentity source boundary was manufactured.

10. **Status maintenance and governance should be proportional.** Several current-entry paragraphs still describe merged September PRs as open/unmerged. The source/model qualification caveats are generally honest; lifecycle status is stale. Do not use this as a reason to re-review frozen scientific bundles. Candidate priorities: make current status truthful; protect useful conditional capabilities in the capability matrix; complete one genuinely discriminating equal-input H1 test if not already covered by an existing lane; request an owner decision on the already-defined Stage F contract only where existing data cannot supply the named absolute closure. No new mechanism sweep, E2C rescue, dependency refresh for its own sake, or repeated radial-reduction task is indicated.

## Reproduction status at snapshot

`review_work/ewp/run_checks.py`: source manifest and static checks pass; full unit suite still running, with at least one failure to classify after the traceback is emitted. Environment pins match NumPy1.26.4/SciPy1.11.4/jsonschema4.23.0; Python3.12.14 differs from CI3.12.3. Initial package installation failed only because of sandbox network access, then succeeded with approved escalation. No OpenFOAM execution, protected target access, fitting, production mutation, or private collection access. `review_work/ewp/recompute.py` independently recomputes retained errors, loss bootstrap and scored-support repeatability; results in `recomputed.json`.
```

</details>


#### Frozen view: review_work/notes/census.md

SHA-256 `f1ffaf693ec5db2a54708c918427d9d9c989a01c9ef565df9a8bc06a3c940cfd`. Historical snapshot; any conflict with final findings is resolved by the documented amendments.

**Readable rendering of the frozen record.** Later corrections remain in the main review and the documented amendments.

##### Census, governance and status review — independent Phase 2 snapshot

Frozen 2026-10-18 22:27 UTC before this reviewer opened either earlier review or the Development Guide. PW = `9dd456be7fd797b9cda0a2bbf50d1ac717d72835`; EWP = `4284e9460c8057053e95de7cfa2fb3590e68e9db`. This is a sub-review for the root review. `[X]` means locally recomputed by this reviewer, `[R]` inspected primary retained artifact, `[J]` reviewer judgment. Original private rows, protected targets, model APIs, integrity tests and native solvers were not run. Repository trees were not modified.

###### Method and complete activity census

The census endpoint is exactly **2026-10-18T22:06:06Z**. The inclusive windows begin 2026-09-18T22:06:06Z and 2026-08-19T22:06:06Z. `build_census.py` enumerates the entire pinned first-parent history before filtering committer timestamps, so an out-of-order timestamp cannot terminate the history traversal prematurely. Each integration is counted once, with parent count distinguishing real merge commits from squash integrations. All 128 integrations in the union of the two repositories' 60-day windows were reconciled to merged GitHub PRs, including manual merge commits PW #261 and EWP #123. GitHub merge state does not by itself adjudicate scientific success or adoption.

**Prospective taxonomy amendment:** the original pre-audit third category was “retained-evidence analysis.” Before aggregation, it was amended with root agreement to **scientific analysis/comparison**, with required subtypes “retained-output only,” “new scenario evaluation under unchanged equations,” and “source/data qualification.” Reason: the old taxonomy omitted new experiments in existing computational models and new empirical fits/predictions on existing observations. It would incorrectly label new native EWP integrations as mere reanalysis. “New scenario” includes new model fits/predictions under unchanged model equations, not only native solver calls. Governing physics and numerical capability are classified by the substantive change; declarations corroborate but do not overrule semantics. EWP #171 is numerical/geometry capability (alternative scientific scenario study), with 32 new integrations, not retained-output analysis.

All rows, changed paths, numstats, commit identities, current PR titles, change-declaration metadata, primary categories, subtypes, mixed alternatives and reasons are in `review_work/census/integrations.json` and `integrations.csv`. `make_classifications.py` holds the explicit assignment of every PR. Recompute with `python review_work/census/make_classifications.py` then `python review_work/census/build_census.py`. Saved live metadata are inputs to title/PR reconciliation. These are **activity and footprint proxies, not time sheets, person-hours, scientific value scores, or independent experiment counts**.

###### Snapshot record 1 — PW 30 d

**Integrations:** 54

**True merge / squash:** 33 / 21

**Governing physics:** 1

**Numerical methods:** 15

**Scientific analysis:** 31

**Assurance/governance:** 2

**Documentation/status:** 4

**Product/UI:** 1

**Mixed:** 15

###### Snapshot record 2 — PW 60 d

**Integrations:** 65

**True merge / squash:** 44 / 21

**Governing physics:** 1

**Numerical methods:** 15

**Scientific analysis:** 37

**Assurance/governance:** 5

**Documentation/status:** 4

**Product/UI:** 3

**Mixed:** 20

###### Snapshot record 3 — EWP 30 d

**Integrations:** 30

**True merge / squash:** 1 / 29

**Governing physics:** 3

**Numerical methods:** 2

**Scientific analysis:** 21

**Assurance/governance:** 0

**Documentation/status:** 4

**Product/UI:** 0

**Mixed:** 16

###### Snapshot record 4 — EWP 60 d

**Integrations:** 63

**True merge / squash:** 34 / 29

**Governing physics:** 4

**Numerical methods:** 5

**Scientific analysis:** 46

**Assurance/governance:** 2

**Documentation/status:** 6

**Product/UI:** 0

**Mixed:** 20


`[X]` Scientific subtypes retained/new/source: PW30 **6/23/2**, PW60 **6/24/7**, EWP30 **15/6/0**, EWP60 **18/21/7**. Fourteen of EWP30's 15 retained-only integrations are mirrors/consumers of PW studies; sixteen of EWP60's 18 are mirrors. Counting both repositories together would double-count much of this scientific work.

Mixed alternatives yield marginal category bounds in the same category order: PW30 **1–2 / 8–20 / 26–37 / 2–4 / 2–5 / 0–2**; PW60 **1–2 / 8–21 / 28–44 / 4–10 / 2–5 / 2–4**; EWP30 **3–3 / 0–2 / 7–23 / 0–0 / 4–18 / 0–0**; EWP60 **4–5 / 2–5 / 30–49 / 1–2 / 6–22 / 0–0**. These bounds are not simultaneously attainable; EWP's large documentation/analysis ambiguity is mostly duplicated handoffs. Changed textual lines include generated output and must not be interpreted as implementation effort.

**Independent interpretation:** this census does not support a claim that recent development is simply governance instead of science. It contains a real governing-equation extension (Foster post-saturation), a new Grudeva numerical realization and qualification work, new native EWP physics/geometry/scenario evaluations, and extensive source-conditioned analysis. Conversely, low counts of governance-primary PRs cannot establish low governance labor: scientific PRs bundle their controls and a single PR can contain a long repair chain. No time allocation evidence was available.

###### Static footprint

`[X]` All tracked files are counted from `git ls-tree`, not working-tree discovery; tracked files matched by local ignore rules are still included. Code extension/path rules and individual file hashes/line counts are in `build_census.py`, `code_files.csv` and `static_inventory.json`. AST inspection executes no code. Physical lines include comments and blanks; nonblank totals are separate. Path categories are exclusive but not a semantic partition of assurance versus science.

| Area | PW files / physical LOC | EWP files / physical LOC |
|---|---:|---:|
| Models/solver | 55 / 10,305 | 7 / 5,793 |
| Analysis | 132 / 52,794 | 241 / 28,355 |
| Assurance/governance | 40 / 19,904 | 42 / 5,297 |
| Product/UI | 48 / 12,773 | 0 / 0 |
| Tests | 304 / 63,649 | 108 / 18,875 |
| Engineering tools | 102 / 26,869 | 64 / 15,557 |
| Other code | 66 / 20,055 | 42 / 9,653 |

PW has 2,871 tracked files, 1,761 under docs; EWP has 2,438 and 927. PW has 56 immediate `docs/analysis` directories, including the non-task `generated` directory, hence 55 candidate task directories before scientific eligibility exclusions; EWP has 48. PW has 28 `Component(...)` constructors, 79 top-level `gate_` functions, 66 registry gate references and 13 quick-only gate functions. Static test-function definitions: PW 4,420 in 304 Python files; EWP 1,575 in 104 Python files. These are not collected/parameterized test case counts. No test AST failed parsing.

PW assurance-plus-tests/model-plus-analysis physical LOC ratio is 1.324; EWP 0.708. Including all engineering tools makes these 1.750 and 1.163. Those ratios are sensitivity screens, not evidence that SCI-GOV's labor circuit breaker has fired: many tests directly check science, analysis modules contain assurance, and effort is unobserved.

###### Status freshness and nonduplicate work

`[R/X]` Fresh generation and semantic freshness differ. PW `docs/status/current.json:135–136@PW` simultaneously records Grudeva permission granted 2026-08-14 and repeats RIGHTS_BLOCKED in every context plus 25/23 component counts in one large acceptance-evidence paragraph. Some content is a legitimate historical release record, but this mixed paragraph reads as current (“Today resolves all 25”), while the current registry has 28. `docs/ONBOARDING.md:104–108@PW` says nothing in the PV track is built, although implemented PV deliverables are described in the current README/status. This is a bounded documentation defect, not a reason to change historical release facts.

`[R/X]` PW `current.json:465@PW` still seeks disposition of draft #318, merged at `28c32df8ed996043f943b777e9312016e8b5ce05`; `:495–497` similarly treats #320 as draft, merged at `f08677b177d9569068941cbb602c7b88f3aca769`. `docs/CURRENT.md:31–35@PW` says the resolution policy's merge is pending, but #335 merged at `882584d110e1356091435ab8b002fb9abdd35ad6` and caffeine `FINAL_REVIEW.json:87@PW` explicitly binds policy merge acceptance to it. Correct merge state; do not infer automatic scientific adoption from merging.

`[R/X]` EWP `docs/PROJECT_STATE.md:3–19@EWP` calls merged linked PRs #200/#198/#196/#194/#192 and earlier work open/unmerged. These are prominent current-facing entries, not merely buried historical provenance. Preserve dated original outcomes and add a current reconciled pointer; existing **EWP issue #76** already requests post-merge reconciliation/durable result pointers. Do that existing task rather than create another process framework or duplicate issue.

Live read-only snapshots are `PW_open_prs.json`, `EWP_open_prs.json`, corresponding open-issue JSON, and `selected_pr_metadata.json`. Open work materially constrains recommendations: **PW #333** is Grudeva 010 accepted-state repeat/full qualification blocked by saved-payload mismatch; its execution restrictions and unresolved integrity stop must remain. **PW #321** is Pannusch common-past 007 joint-bound witness repair, already in flight. Neither should be recreated as a new task. **EWP #117** already audits existing evidence before home-lab purchases; its body relies on an older ABSENT Visualizer-store state, so disposition should account for later recovered holdings before treating it as the current acquisition plan. EWP #104 already tracks shared-vs-species models. PW #313 temperature history, #311 Foster post-saturation, #67 Grudeva, #231 first-drip evidence, #96 experiments, #36 export and #240 frozen Foundry provenance also constrain novelty. No requested code change was made.

###### Frozen random PW bundle sample

Frame/sample are in `bundle_sample.json`, fixed with `random.Random(20261018)` before reading result bodies. The initial PW frame included `generated`; it was removed as a non-task before result reads, preserving both original and amended frames/selections. Final eligible frame n=15, sample n=4. EWP's duplicate frame in this artifact was not executed; use the EWP reviewer's separately frozen `review_work/ewp/sample.json`.

1. **Smrke transfer:** `docs/analysis/sci_md_smrke_transfer_001/{CONTRACT.md,RESULT.md}@PW` preserves 33 primary/46 all-marker estimates with unresolved shot identities; it does not invent independent raw replicates. Tested fines corrections worsen central held-arm performance, with negative gain under all 18 source treatments. The failure to earn complexity is not explained solely by a harsh positive-gain threshold. Its source-conditioned finite-window conclusions do not establish in-shot kinetics or physical validation. `[R/J]`
2. **Radial observation:** `docs/analysis/sci_md_radial_obs_001/{CONTRACT.json,RESULT.md}@PW` reconstructs source workbook formulas and distinguishes operational recoverable-solute contrasts from radial solid depletion. Retained liquid, recovery/handling and initial inventory remain essential assumptions; a mass-conserving counterexample establishes nonuniqueness. The retained report records 1,672 formula cells replayed, three source rejection events, an anomalous Sworks label/TDS mismatch and nine rounding inconsistencies without silent repairs. This is useful source metrology, not evidence of a validated radial state field. `[R/J]`
3. **Foster post-saturation:** `docs/analysis/model_foster2025_postsat_001/CONTRACT.md:40–50,RESULTS.md,HANDOFF.md:19–48@PW` adds the missing published post-saturation branch; all declared qualification gates pass. The review found a cached-oracle false-green pathway (unsuccessful caches or partial dense-output extrapolation could have passed), while all 12 actual retained executions were successful. A bounded fix and synthetic checks reused their valid trajectories. A failed entry finite-difference derivative check remains historical; actual RHS verification supplies the qualified argument. This is real scientific implementation and a substantive verification control. `[R/J]`
4. **RP-D-LC-001:** `docs/analysis/rp_d_lc_001/decision.md:47–57@PW` is INVALID_EXECUTION and transfer is NOT_ADJUDICATED. The frozen **volume-flux proxy** failed slightly (1.028e-3 against 1e-3); actual mass conservation was **NOT_EVALUATED**, because density-weighted flux was not retained. Calling this a demonstrated mass-conservation failure is incorrect. Grid refinement changed Re because fixed lattice forcing/viscosity makes Re scale cubically with refinement. Negative-control axial widening and inversion instability independently limit the mechanism inference. The scientific role of the 1e-4 pressure-forcing budget can be reviewed prospectively, but this does not erase the independent defects. Existing RP-D-LC-001b work must be checked rather than recommended again. `[R/J]`

###### Proportional governance and actual review identities

Both repositories' `docs/governance/MINIMUM_NECESSARY_GOVERNANCE_STANDARD.md` contain the same operative SCI-GOV-001 controls, with PW appending a prospective policy pointer. Its §11 circuit breakers are a sound current authority. The observations below support scoped reuse, not a wholesale relaxation of safety or scientific contracts.

| Recent lane | Scientific result and material control | Non-scientific overhead / circuit-breaker judgment |
|---|---|---|
| Foster post-saturation, PW #312 | Correct published post-saturation physics branch; separate reviewer exposed a cached-oracle false-green condition; finite-difference failure retained, actual RHS verified | First reducer list/scalar reporting failure and an I040 generic-`append` scanner collision were non-scientific repairs. Reuse of all 12 valid trajectories and bounded synthetic checks is appropriate. No evidence here of repeated full science execution for those repairs. |
| Pannusch numerical/prefix-conditioned 004–006 | Explicit inner/outer bounds and feasible witness bookkeeping address real interval guarantees; #321 addresses the remaining joint witness defect | `model_pannusch2024_prefix_conditioned_006/REVIEW.md:3–7` calls itself a **Codex implementation-author** record, explicitly neither independent nor human. It is G0/synthetic and does not claim an independent pre-score scientific review. Do not count it as human validation or prescribe a new review ladder; finish the existing witness repair. |
| Caffeine decision-resolution #339 | Fresh delegated Codex review independently recalculated retained comparison/deletion arithmetic and scoped conclusions; historical result preserved | PRE review repaired a manifest classification/hash issue; final addendum repaired absent-public-fallback filenames (`SCORE_COMPLETION.JSON` etc.). It classified the latter as software assembly, reused unchanged reviewed science by hashes, and ran the bounded 33-test set. This is a concrete successful application of proportional governance, not another mandatory full scoring ladder. |

`[R]` Caffeine `PRE_ANALYSIS_REVIEW.json`, `FINAL_REVIEW.json` and `FINAL_REVIEW_ADDENDUM.json` identify a fresh delegated **nonhuman Codex agent**, not a human subject-matter reviewer. MASS-DELIVERY-006 `PRE_SCORE_REVIEW.json` likewise names a fresh Codex agent, separate from the implementation author. Different agent identity provides process separation, not independent human expertise or a second empirical dataset. Exact hashes and retained math help auditability; no claim of human corroboration follows.

`[R/J]` PW `CLAUDE.md:86–109` explicitly freezes a historical ~4,800-line Paper 1 assurance layer partly guarding empty registries, after rounds 10–12 found defects in previous gates. This is direct documented historical overengineering, already recognized by current policy. It supports retaining the freeze and reopening only for a real decision or shipped-text defect; it does not quantify October labor or justify dismantling science controls.

###### Independent priorities before earlier-review reconciliation

- **P1/P2 bounded status repair:** reconcile current-facing lifecycle/permission/capability text and close or update existing queue entries using the already completed PR evidence and existing EWP #76. Preserve historical outcomes and distinguish owner adoption from merge state. No new status framework.
- **P1 existing task disposition:** finish or explicitly stop #333 and #321 against their actual unresolved integrity/witness requirements. Do not authorize a successor ladder from an invalid/incomplete result.
- **P2 governance consolidation:** keep the existing SCI-GOV reuse and stop rules; request lane effort logs only if asserting a time-ratio circuit breaker. Apply bounded correction to software/reporting defects without resetting unchanged science. This is a practice recommendation, not an additional assurance subsystem.
- **No new home-lab or corpus acquisition from this sub-review alone:** disposition #117 against recovered holdings; root's corpus/physics analyses determine any decision-specific gap. The census itself cannot prioritize a new experiment.

###### Phase 3 reconciliation

To be appended after the independently frozen section above; earlier reviews will be treated as secondary sources, not primary proof.

<details>
<summary>Show byte-exact frozen Markdown source 5</summary>

```markdown
# Census, governance and status review — independent Phase 2 snapshot

Frozen 2026-10-18 22:27 UTC before this reviewer opened either earlier review or the Development Guide. PW = `9dd456be7fd797b9cda0a2bbf50d1ac717d72835`; EWP = `4284e9460c8057053e95de7cfa2fb3590e68e9db`. This is a sub-review for the root review. `[X]` means locally recomputed by this reviewer, `[R]` inspected primary retained artifact, `[J]` reviewer judgment. Original private rows, protected targets, model APIs, integrity tests and native solvers were not run. Repository trees were not modified.

## Method and complete activity census

The census endpoint is exactly **2026-10-18T22:06:06Z**. The inclusive windows begin 2026-09-18T22:06:06Z and 2026-08-19T22:06:06Z. `build_census.py` enumerates the entire pinned first-parent history before filtering committer timestamps, so an out-of-order timestamp cannot terminate the history traversal prematurely. Each integration is counted once, with parent count distinguishing real merge commits from squash integrations. All 128 integrations in the union of the two repositories' 60-day windows were reconciled to merged GitHub PRs, including manual merge commits PW #261 and EWP #123. GitHub merge state does not by itself adjudicate scientific success or adoption.

**Prospective taxonomy amendment:** the original pre-audit third category was “retained-evidence analysis.” Before aggregation, it was amended with root agreement to **scientific analysis/comparison**, with required subtypes “retained-output only,” “new scenario evaluation under unchanged equations,” and “source/data qualification.” Reason: the old taxonomy omitted new experiments in existing computational models and new empirical fits/predictions on existing observations. It would incorrectly label new native EWP integrations as mere reanalysis. “New scenario” includes new model fits/predictions under unchanged model equations, not only native solver calls. Governing physics and numerical capability are classified by the substantive change; declarations corroborate but do not overrule semantics. EWP #171 is numerical/geometry capability (alternative scientific scenario study), with 32 new integrations, not retained-output analysis.

All rows, changed paths, numstats, commit identities, current PR titles, change-declaration metadata, primary categories, subtypes, mixed alternatives and reasons are in `review_work/census/integrations.json` and `integrations.csv`. `make_classifications.py` holds the explicit assignment of every PR. Recompute with `python review_work/census/make_classifications.py` then `python review_work/census/build_census.py`. Saved live metadata are inputs to title/PR reconciliation. These are **activity and footprint proxies, not time sheets, person-hours, scientific value scores, or independent experiment counts**.

| Repository/window | Integrations | True merge / squash | Governing physics | Numerical methods | Scientific analysis | Assurance/governance | Documentation/status | Product/UI | Mixed |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| PW 30 d | 54 | 33 / 21 | 1 | 15 | 31 | 2 | 4 | 1 | 15 |
| PW 60 d | 65 | 44 / 21 | 1 | 15 | 37 | 5 | 4 | 3 | 20 |
| EWP 30 d | 30 | 1 / 29 | 3 | 2 | 21 | 0 | 4 | 0 | 16 |
| EWP 60 d | 63 | 34 / 29 | 4 | 5 | 46 | 2 | 6 | 0 | 20 |

`[X]` Scientific subtypes retained/new/source: PW30 **6/23/2**, PW60 **6/24/7**, EWP30 **15/6/0**, EWP60 **18/21/7**. Fourteen of EWP30's 15 retained-only integrations are mirrors/consumers of PW studies; sixteen of EWP60's 18 are mirrors. Counting both repositories together would double-count much of this scientific work.

Mixed alternatives yield marginal category bounds in the same category order: PW30 **1–2 / 8–20 / 26–37 / 2–4 / 2–5 / 0–2**; PW60 **1–2 / 8–21 / 28–44 / 4–10 / 2–5 / 2–4**; EWP30 **3–3 / 0–2 / 7–23 / 0–0 / 4–18 / 0–0**; EWP60 **4–5 / 2–5 / 30–49 / 1–2 / 6–22 / 0–0**. These bounds are not simultaneously attainable; EWP's large documentation/analysis ambiguity is mostly duplicated handoffs. Changed textual lines include generated output and must not be interpreted as implementation effort.

**Independent interpretation:** this census does not support a claim that recent development is simply governance instead of science. It contains a real governing-equation extension (Foster post-saturation), a new Grudeva numerical realization and qualification work, new native EWP physics/geometry/scenario evaluations, and extensive source-conditioned analysis. Conversely, low counts of governance-primary PRs cannot establish low governance labor: scientific PRs bundle their controls and a single PR can contain a long repair chain. No time allocation evidence was available.

## Static footprint

`[X]` All tracked files are counted from `git ls-tree`, not working-tree discovery; tracked files matched by local ignore rules are still included. Code extension/path rules and individual file hashes/line counts are in `build_census.py`, `code_files.csv` and `static_inventory.json`. AST inspection executes no code. Physical lines include comments and blanks; nonblank totals are separate. Path categories are exclusive but not a semantic partition of assurance versus science.

| Area | PW files / physical LOC | EWP files / physical LOC |
|---|---:|---:|
| Models/solver | 55 / 10,305 | 7 / 5,793 |
| Analysis | 132 / 52,794 | 241 / 28,355 |
| Assurance/governance | 40 / 19,904 | 42 / 5,297 |
| Product/UI | 48 / 12,773 | 0 / 0 |
| Tests | 304 / 63,649 | 108 / 18,875 |
| Engineering tools | 102 / 26,869 | 64 / 15,557 |
| Other code | 66 / 20,055 | 42 / 9,653 |

PW has 2,871 tracked files, 1,761 under docs; EWP has 2,438 and 927. PW has 56 immediate `docs/analysis` directories, including the non-task `generated` directory, hence 55 candidate task directories before scientific eligibility exclusions; EWP has 48. PW has 28 `Component(...)` constructors, 79 top-level `gate_` functions, 66 registry gate references and 13 quick-only gate functions. Static test-function definitions: PW 4,420 in 304 Python files; EWP 1,575 in 104 Python files. These are not collected/parameterized test case counts. No test AST failed parsing.

PW assurance-plus-tests/model-plus-analysis physical LOC ratio is 1.324; EWP 0.708. Including all engineering tools makes these 1.750 and 1.163. Those ratios are sensitivity screens, not evidence that SCI-GOV's labor circuit breaker has fired: many tests directly check science, analysis modules contain assurance, and effort is unobserved.

## Status freshness and nonduplicate work

`[R/X]` Fresh generation and semantic freshness differ. PW `docs/status/current.json:135–136@PW` simultaneously records Grudeva permission granted 2026-08-14 and repeats RIGHTS_BLOCKED in every context plus 25/23 component counts in one large acceptance-evidence paragraph. Some content is a legitimate historical release record, but this mixed paragraph reads as current (“Today resolves all 25”), while the current registry has 28. `docs/ONBOARDING.md:104–108@PW` says nothing in the PV track is built, although implemented PV deliverables are described in the current README/status. This is a bounded documentation defect, not a reason to change historical release facts.

`[R/X]` PW `current.json:465@PW` still seeks disposition of draft #318, merged at `28c32df8ed996043f943b777e9312016e8b5ce05`; `:495–497` similarly treats #320 as draft, merged at `f08677b177d9569068941cbb602c7b88f3aca769`. `docs/CURRENT.md:31–35@PW` says the resolution policy's merge is pending, but #335 merged at `882584d110e1356091435ab8b002fb9abdd35ad6` and caffeine `FINAL_REVIEW.json:87@PW` explicitly binds policy merge acceptance to it. Correct merge state; do not infer automatic scientific adoption from merging.

`[R/X]` EWP `docs/PROJECT_STATE.md:3–19@EWP` calls merged linked PRs #200/#198/#196/#194/#192 and earlier work open/unmerged. These are prominent current-facing entries, not merely buried historical provenance. Preserve dated original outcomes and add a current reconciled pointer; existing **EWP issue #76** already requests post-merge reconciliation/durable result pointers. Do that existing task rather than create another process framework or duplicate issue.

Live read-only snapshots are `PW_open_prs.json`, `EWP_open_prs.json`, corresponding open-issue JSON, and `selected_pr_metadata.json`. Open work materially constrains recommendations: **PW #333** is Grudeva 010 accepted-state repeat/full qualification blocked by saved-payload mismatch; its execution restrictions and unresolved integrity stop must remain. **PW #321** is Pannusch common-past 007 joint-bound witness repair, already in flight. Neither should be recreated as a new task. **EWP #117** already audits existing evidence before home-lab purchases; its body relies on an older ABSENT Visualizer-store state, so disposition should account for later recovered holdings before treating it as the current acquisition plan. EWP #104 already tracks shared-vs-species models. PW #313 temperature history, #311 Foster post-saturation, #67 Grudeva, #231 first-drip evidence, #96 experiments, #36 export and #240 frozen Foundry provenance also constrain novelty. No requested code change was made.

## Frozen random PW bundle sample

Frame/sample are in `bundle_sample.json`, fixed with `random.Random(20261018)` before reading result bodies. The initial PW frame included `generated`; it was removed as a non-task before result reads, preserving both original and amended frames/selections. Final eligible frame n=15, sample n=4. EWP's duplicate frame in this artifact was not executed; use the EWP reviewer's separately frozen `review_work/ewp/sample.json`.

1. **Smrke transfer:** `docs/analysis/sci_md_smrke_transfer_001/{CONTRACT.md,RESULT.md}@PW` preserves 33 primary/46 all-marker estimates with unresolved shot identities; it does not invent independent raw replicates. Tested fines corrections worsen central held-arm performance, with negative gain under all 18 source treatments. The failure to earn complexity is not explained solely by a harsh positive-gain threshold. Its source-conditioned finite-window conclusions do not establish in-shot kinetics or physical validation. `[R/J]`
2. **Radial observation:** `docs/analysis/sci_md_radial_obs_001/{CONTRACT.json,RESULT.md}@PW` reconstructs source workbook formulas and distinguishes operational recoverable-solute contrasts from radial solid depletion. Retained liquid, recovery/handling and initial inventory remain essential assumptions; a mass-conserving counterexample establishes nonuniqueness. The retained report records 1,672 formula cells replayed, three source rejection events, an anomalous Sworks label/TDS mismatch and nine rounding inconsistencies without silent repairs. This is useful source metrology, not evidence of a validated radial state field. `[R/J]`
3. **Foster post-saturation:** `docs/analysis/model_foster2025_postsat_001/CONTRACT.md:40–50,RESULTS.md,HANDOFF.md:19–48@PW` adds the missing published post-saturation branch; all declared qualification gates pass. The review found a cached-oracle false-green pathway (unsuccessful caches or partial dense-output extrapolation could have passed), while all 12 actual retained executions were successful. A bounded fix and synthetic checks reused their valid trajectories. A failed entry finite-difference derivative check remains historical; actual RHS verification supplies the qualified argument. This is real scientific implementation and a substantive verification control. `[R/J]`
4. **RP-D-LC-001:** `docs/analysis/rp_d_lc_001/decision.md:47–57@PW` is INVALID_EXECUTION and transfer is NOT_ADJUDICATED. The frozen **volume-flux proxy** failed slightly (1.028e-3 against 1e-3); actual mass conservation was **NOT_EVALUATED**, because density-weighted flux was not retained. Calling this a demonstrated mass-conservation failure is incorrect. Grid refinement changed Re because fixed lattice forcing/viscosity makes Re scale cubically with refinement. Negative-control axial widening and inversion instability independently limit the mechanism inference. The scientific role of the 1e-4 pressure-forcing budget can be reviewed prospectively, but this does not erase the independent defects. Existing RP-D-LC-001b work must be checked rather than recommended again. `[R/J]`

## Proportional governance and actual review identities

Both repositories' `docs/governance/MINIMUM_NECESSARY_GOVERNANCE_STANDARD.md` contain the same operative SCI-GOV-001 controls, with PW appending a prospective policy pointer. Its §11 circuit breakers are a sound current authority. The observations below support scoped reuse, not a wholesale relaxation of safety or scientific contracts.

| Recent lane | Scientific result and material control | Non-scientific overhead / circuit-breaker judgment |
|---|---|---|
| Foster post-saturation, PW #312 | Correct published post-saturation physics branch; separate reviewer exposed a cached-oracle false-green condition; finite-difference failure retained, actual RHS verified | First reducer list/scalar reporting failure and an I040 generic-`append` scanner collision were non-scientific repairs. Reuse of all 12 valid trajectories and bounded synthetic checks is appropriate. No evidence here of repeated full science execution for those repairs. |
| Pannusch numerical/prefix-conditioned 004–006 | Explicit inner/outer bounds and feasible witness bookkeeping address real interval guarantees; #321 addresses the remaining joint witness defect | `model_pannusch2024_prefix_conditioned_006/REVIEW.md:3–7` calls itself a **Codex implementation-author** record, explicitly neither independent nor human. It is G0/synthetic and does not claim an independent pre-score scientific review. Do not count it as human validation or prescribe a new review ladder; finish the existing witness repair. |
| Caffeine decision-resolution #339 | Fresh delegated Codex review independently recalculated retained comparison/deletion arithmetic and scoped conclusions; historical result preserved | PRE review repaired a manifest classification/hash issue; final addendum repaired absent-public-fallback filenames (`SCORE_COMPLETION.JSON` etc.). It classified the latter as software assembly, reused unchanged reviewed science by hashes, and ran the bounded 33-test set. This is a concrete successful application of proportional governance, not another mandatory full scoring ladder. |

`[R]` Caffeine `PRE_ANALYSIS_REVIEW.json`, `FINAL_REVIEW.json` and `FINAL_REVIEW_ADDENDUM.json` identify a fresh delegated **nonhuman Codex agent**, not a human subject-matter reviewer. MASS-DELIVERY-006 `PRE_SCORE_REVIEW.json` likewise names a fresh Codex agent, separate from the implementation author. Different agent identity provides process separation, not independent human expertise or a second empirical dataset. Exact hashes and retained math help auditability; no claim of human corroboration follows.

`[R/J]` PW `CLAUDE.md:86–109` explicitly freezes a historical ~4,800-line Paper 1 assurance layer partly guarding empty registries, after rounds 10–12 found defects in previous gates. This is direct documented historical overengineering, already recognized by current policy. It supports retaining the freeze and reopening only for a real decision or shipped-text defect; it does not quantify October labor or justify dismantling science controls.

## Independent priorities before earlier-review reconciliation

- **P1/P2 bounded status repair:** reconcile current-facing lifecycle/permission/capability text and close or update existing queue entries using the already completed PR evidence and existing EWP #76. Preserve historical outcomes and distinguish owner adoption from merge state. No new status framework.
- **P1 existing task disposition:** finish or explicitly stop #333 and #321 against their actual unresolved integrity/witness requirements. Do not authorize a successor ladder from an invalid/incomplete result.
- **P2 governance consolidation:** keep the existing SCI-GOV reuse and stop rules; request lane effort logs only if asserting a time-ratio circuit breaker. Apply bounded correction to software/reporting defects without resetting unchanged science. This is a practice recommendation, not an additional assurance subsystem.
- **No new home-lab or corpus acquisition from this sub-review alone:** disposition #117 against recovered holdings; root's corpus/physics analyses determine any decision-specific gap. The census itself cannot prioritize a new experiment.

## Phase 3 reconciliation

To be appended after the independently frozen section above; earlier reviews will be treated as secondary sources, not primary proof.
```

</details>


<a id="appendix-b-2"></a>

### B.2 Reproduction scripts



#### review_work/scripts/root_primary_audit.py

SHA-256 `af86a16a397212f02058a18d31398a2352d61c563054a3cbc9d571e7a6d5e125`.

<details>
<summary>Show complete Python source — review_work/scripts/root_primary_audit.py</summary>

```python
import json, math, hashlib, time
from pathlib import Path
from collections import Counter
import numpy as np

root = Path(__file__).resolve().parents[2]
pw = root / 'puckworks'
out = {}

from puckworks.models.cameron2020 import extraction_bdf as cam
result = cam.simulate_shot(1.1, N=20, M=12)
out['cameron'] = {'gs':1.1,'N':20,'M':12,'EY_percent':result.EY,'EY_minus_solid_pp':result.EY-result.EY_solid,'inventory_ceiling_percent':cam.inventory_ceiling_percent(), 'current_gate_allowance_pp':0.5,'gate_allowance_kg_at_20g':.5/100*.020,'gate_allowance_fraction_initial_inventory':.5/cam.inventory_ceiling_percent(), 'printed_depth_m':cam.bed_depth(.020),'bulk_identity_depth_m':.020/cam.RHO_GROUNDS/(np.pi*cam.R0**2)}
from puckworks.models.wadsworth2026 import permeability as wp
ratios=np.array([r['k_m2']/wp.k_star(r['phi_p'],r['s_p'])/r['phi_p']**wp.B_PERC for r in wp.table1()])
out['wadsworth']={'n':len(ratios),'geometric_mean':float(np.exp(np.log(ratios).mean())), 'min_ratio':float(ratios.min()),'max_ratio':float(ratios.max()), 'rms_log_ratio':float(np.sqrt(np.mean(np.log(ratios)**2))), 'outside_30_percent':int(np.sum(np.abs(ratios-1)>.30)), 'note':'Arithmetic on source table, not independent validation.'}
pubpath=pw/'docs/analysis/model_grudeva2026_publication_reconciliation_009/RESULTS.json'
d=json.loads(pubpath.read_text())
inputs={}; checks=[]
for name, inp in d['inputs'].items():
    rows=inp['rows']; counts=Counter(r['classification'] for r in rows)
    included=[r for r in rows if r['classification']=='INCLUDED']
    checks.extend(abs((r['model']-r['publication'])-r['signed_residual']) for r in included)
    fams={}
    for family in sorted({r['family'] for r in included}):
        same=[r for r in included if r['family']==family]
        worst=max(same,key=lambda r:abs(r['model']-r['publication']))
        fams[family]={k:worst[k] for k in ('target_id','signed_residual','absolute_residual','limit','extraction_bounds')}
    inputs[name]={'counts':dict(counts),'n':len(rows),'families':fams}
primary=[]
for f in d['primary']['families'].values():
    primary.extend(f['common_included'])
shared=[r for r in primary if abs(r['production']-r['publication'])>r['limit'] and abs(r['comparator']-r['publication'])>r['limit'] and (r['production']-r['publication'])*(r['comparator']-r['publication'])>0]
out['publication009']={'input_hash':hashlib.sha256(pubpath.read_bytes()).hexdigest(),'inputs':inputs,'total_rows':sum(v['n'] for v in inputs.values()), 'included_rows':sum(v['counts'].get('INCLUDED',0) for v in inputs.values()),'excluded_rows':sum(v['counts'].get('EXCLUDED',0) for v in inputs.values()), 'arithmetic_max_delta':max(checks),'primary_shared_failures':len(shared),'first_selected_shared_failure_time':min(r['coordinates'].get('t',math.inf) for r in shared), 'persistent_count_stored':d['refinement_outcomes']['witness_persistence']}
m=json.loads((pw/'docs/analysis/model_grudeva2026_matched_comparison_008/RESULTS.json').read_text())
pairs=[]
for p in m['pairs']:
    fs=p['families']
    pairs.append({'pair':p['pair'],'complete':p['complete'],'family_count':len(fs),'family_failures':sum(x.get('status',x.get('result'))=='FAIL' for x in fs.values()), 'maximum_ratio_to_limit':max(x['max_absolute']/x['limit'] for x in fs.values()),'arithmetic_max_delta':max(abs((x['production']-x['comparator'])-x['signed_difference']) for x in fs.values()),'unavailable':sum(x['unavailable'] for x in fs.values())})
out['matched008']={'pairs':pairs,'new_production_simulations':m['new_production_simulations'],'new_comparator_simulations':m['new_comparator_simulations']}
(root/'review_work/results/root_primary_audit.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
```

</details>


#### review_work/scripts/gate_sample.py

SHA-256 `0b32811a2c8f7ff0f4672299d14f90bcac716e7abed7e0f4a0ff3dbac5f43b53`.

<details>
<summary>Show complete Python source — review_work/scripts/gate_sample.py</summary>

```python
import ast, json, random
from pathlib import Path

root = Path(__file__).resolve().parents[2]
gate_path = root / 'puckworks/puckworks/validation/gates.py'
tree = ast.parse(gate_path.read_text())
all_gates = sorted(n.name for n in tree.body if isinstance(n, ast.FunctionDef) and n.name.startswith('gate_'))
regtree = ast.parse((root / 'puckworks/puckworks/models/__init__.py').read_text())
wired = sorted({n.attr for n in ast.walk(regtree) if isinstance(n, ast.Attribute) and isinstance(n.value, ast.Name) and n.value.id == 'G' and n.attr.startswith('gate_')})
mandatory = sorted(set('gate_cameron_conservation gate_pannusch_solver_mape gate_pannusch_closures gate_waszkiewicz_static_refit gate_waszkiewicz_dynamic_9bar gate_infiltration_triangle gate_foster_ct_trajectory gate_lb_channel gate_grudeva2026_reduced gate_roman_bed_mpe_parameter_free gate_g10_viscosity_bulk_negligible gate_extraction_harness gate_g4_temperature_sensitivity'.split()))
registry_frame = sorted(set(wired) - set(mandatory))
quick_only_frame = sorted(set(all_gates) - set(wired) - set(mandatory))
rng = random.Random(20261018)
result = {'seed':20261018,'defined_count':len(all_gates),'wired_count':len(wired),'quick_only_total':len(set(all_gates)-set(wired)), 'mandatory':mandatory, 'registry_frame':registry_frame,'quick_only_frame':quick_only_frame, 'registry_sample':rng.sample(registry_frame,8),'quick_only_sample':rng.sample(quick_only_frame,min(4,len(quick_only_frame)))}
(root/'review_work/results/gate_sample.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
```

</details>


#### review_work/scripts/retry_pw_environment.py

SHA-256 `38e74a4ade35a315828615c8c4cd5840dab5e4d3274c889d9758be09bd88454b`.

<details>
<summary>Show complete Python source — review_work/scripts/retry_pw_environment.py</summary>

```python
"""Rerun only the observed environment-sensitive failures, unchanged."""
from pathlib import Path
import json, os, subprocess, time

root = Path(__file__).resolve().parents[2]
log = root/'review_work/logs/pw-quick.log'
nodes = [line.split()[1] for line in log.read_text().splitlines() if line.startswith('FAILED tests/')]
assert len(nodes) == 24
assert not any('angeloni' in n.lower() or 'protected_target_integrity' in n for n in nodes)
command = [str(root/'review_work/pwvenv/bin/python'), '-m', 'pytest', '-q',
           '-o', 'cache_dir='+str(root/'review_work/pw-retry-cache'), *nodes]
environment = os.environ.copy()
environment.update(TMPDIR='/dev/shm', OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1',
                   PYTHONDONTWRITEBYTECODE='1')
start = time.monotonic()
with (root/'review_work/logs/pw-environment-rerun.log').open('w') as output:
    result = subprocess.run(command, cwd=root/'puckworks', env=environment,
                            stdout=output, stderr=subprocess.STDOUT)
report = dict(command=command, temporary_directory='/dev/shm',
              selected_tests=nodes, count=len(nodes), exit_code=result.returncode,
              wall_seconds=time.monotonic()-start,
              scope='Narrow unchanged-test rerun; no original suite relabeling')
(root/'review_work/results/pw-environment-rerun.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
raise SystemExit(result.returncode)
```

</details>


#### review_work/data/audit_primary.py

SHA-256 `eb66e8606109b33552fc78b99e20235fce641e5809bdaf08df39997a66fcc937`.

<details>
<summary>Show complete Python source — review_work/data/audit_primary.py</summary>

```python
"""Read-only independent aggregate arithmetic; no private or protected data APIs."""
from pathlib import Path
import collections
import csv
import hashlib
import json
import statistics

ROOT = Path(__file__).resolve().parents[2]
PW = ROOT / 'puckworks'
OUT = Path(__file__).resolve().parent

def read(rel):
    return json.loads((PW / rel).read_text())

manifest = list(csv.DictReader((PW / 'puckworks/data/MANIFEST.csv').open()))
register = read('puckworks/data/AVAILABLE_DATA_REGISTER.json')
snapshot = read('puckworks/data/LOCAL_CORPUS_SNAPSHOT.json')
report = {
    'pw_commit': '9dd456be7fd797b9cda0a2bbf50d1ac717d72835',
    'scope': 'PUBLIC_NONPROTECTED_AGGREGATES_ONLY',
    'manifest_count': len(manifest),
    'family_entry_count': len(register['families']),
    'family_access_counts': dict(collections.Counter(f['raw_access_status'] for f in register['families'])),
    'external_snapshot': {k:snapshot[k] for k in ('files','bytes','unique_sha256_contents','observation_count','by_content_role','status')},
    'checks': [],
    'cases': {},
}

def metrics(arm):
    return arm.get('full_scope_metrics')

for name in ('sci_md_mass_delivery_006', 'sci_md_caffeine_delivery_001',
             'sci_md_trigonelline_delivery_001', 'sci_md_5cqa_delivery_001',
             'sci_md_5cqa_tds_001', 'sci_md_5cqa_assay_001', 'sci_md_5cqa_assay_002'):
    rel = f'docs/analysis/{name}/RESULTS.json'
    d = read(rel)
    case = {'disposition': d['disposition'], 'source_sha256': hashlib.sha256((PW/rel).read_bytes()).hexdigest(), 'panels': {}}
    for panel, arms in d['panels'].items():
        table = {}
        for arm, a in arms.items():
            m = metrics(a)
            table[arm] = {'complete': a['complete_scope'], 'metrics': m,
                          'original_shots':a['original_shots'], 'original_slots':a['original_slots'],
                          'adequacy':a.get('adequacy',a.get('full_scope_adequacy'))}
            if m:
                for k, value in m.items():
                    # Full panel = equal condition averages, without changing support.
                    if all(metrics(c) and k in metrics(c) for c in a['conditions'].values()):
                        rebuilt = statistics.mean(metrics(c)[k] for c in a['conditions'].values())
                        report['checks'].append({'task':name,'panel':panel,'arm':arm,'metric':k,
                                                 'retained':value,'rebuilt':rebuilt,'abs_delta':abs(rebuilt-value)})
        case['panels'][panel] = table
    report['cases'][name] = case

report['comparisons'] = []
for name, candidate, refs in (
    ('sci_md_mass_delivery_006','C2',('C0','C1','FIRST_ASSAY_EMPIRICAL')),
    ('sci_md_caffeine_delivery_001','S2',('S1','D0','S0')),
    ('sci_md_5cqa_assay_002','L12',('L1M','L2M')),
    ('sci_md_5cqa_assay_002','L2M',('L1M',)),
    ('sci_md_trigonelline_delivery_001','TR-D0',('TR-K0',)),
):
    d = read(f'docs/analysis/{name}/RESULTS.json')
    for panel, arms in d['panels'].items():
        c = metrics(arms[candidate])
        if c is None: continue
        suffix = 'pp' if 'R_pp' in c else 'mg_g'
        for ref in refs:
            r = metrics(arms[ref])
            gain = r[f'R_{suffix}'] - c[f'R_{suffix}']
            report['comparisons'].append({'task':name,'panel':panel,'candidate':candidate,'reference':ref,
                'units':suffix,'rmse_gain':gain,'relative_gain_percent':100*gain/r[f'R_{suffix}'],
                'candidate_signed_bias':c[f'B_{suffix}'],'reference_signed_bias':r[f'B_{suffix}'],
                'absolute_bias_deterioration':c[f'absB_{suffix}']-r[f'absB_{suffix}'],
                'numerical_gain_allowance':c[f'R_allowance_{suffix}']+r[f'R_allowance_{suffix}'],
                'condition_wins':sum(metrics(arms[ref]['conditions'][q])[f'R_{suffix}'] > metrics(v)[f'R_{suffix}'] for q,v in arms[candidate]['conditions'].items()),
                'condition_count':len(arms[candidate]['conditions'])})

for name in ('sci_md_mass_delivery_007','sci_md_mass_delivery_008'):
    d = read(f'docs/analysis/{name}/RESULTS.json')
    report['cases'][name] = {'disposition':d['disposition'],'arms':{a:{'adequacy':v['adequacy'],'metrics':v.get('full_scope_metrics',v.get('metrics'))} for a,v in d['arms'].items()}}
    if name.endswith('008'):
        report['cases'][name]['counts'] = {k:d[k] for k in ('eligible_physical_shots','ordered_pairs','unique_suffix_windows','original_shots','prediction_slots_per_arm')}

report['aggregation_max_abs_delta'] = max(x['abs_delta'] for x in report['checks'])
(OUT/'primary_audit.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k in ('manifest_count','family_entry_count','family_access_counts','aggregation_max_abs_delta')},indent=2))
print('aggregate_checks',len(report['checks']))
for v in report['comparisons']:
    print(v['task'],v['panel'],v['candidate'],v['reference'], 'gain',format(v['rmse_gain'],'.12g'),'bias',format(v['candidate_signed_bias'],'.12g'),'units',v['units'])
```

</details>


#### review_work/data/audit_reanalysis.py

SHA-256 `8c2f866d668fe1f4b1efb1df18ae1c646bb112ab5a7054978a5aca795e956265`.

<details>
<summary>Show complete Python source — review_work/data/audit_reanalysis.py</summary>

```python
"""Public-only checks of October addenda; private rows are not reconstructed."""
import collections
import hashlib
import json
import math
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[2]
PW, EWP = ROOT/'puckworks', ROOT/'espresso-whole-pull'
OUT = Path(__file__).resolve().parent

def read(path):
    return json.loads(path.read_text())

result = {'scope':'NONPROTECTED_PUBLIC_AGGREGATE_CHECKS; NO_PRIVATE_DELETION_RECOMPUTATION'}
r = read(EWP/'docs/analysis/sci_md_rheology_010/METRICS.json')
rows=[]
for group in ('primary','secondary'):
    for name, case in r[group].items():
        for metric, saved in case['decisions'].items():
            base=case['variants']['base'][metric]
            terms={k:abs(case['variants'][variant][metric]-base) for k,variant in
                   [('time','temporal'),('axial','axial'),('Cradial' if group=='primary' else 'both_C_radial','radial')]}
            terms['property']=abs(case['variants']['property'][metric]-base) if 'property' in case['variants'] else 0.
            terms['arithmetic']=max(v[metric] for v in case['arithmetic'].values())
            total=math.fsum(terms.values())
            b=saved['budget']; eligible=total <= .2*b
            below=base+total < b; above=base-total > b
            predicted='UNRESOLVED'
            if eligible:
                if below: predicted='PASS' if group=='primary' else 'BELOW_DECLARED_MATERIALITY_BUDGET'
                elif above: predicted='FAIL' if group=='primary' else 'MATERIAL_MODELED_DELIVERY_CONTRAST'
            rows.append({'group':group,'case':name,'metric':metric,'M':base,'u':total,'budget':b,
                         'components_equal':terms==saved['terms'],'sum_delta':total-saved['u_total'],
                         'decision':predicted,'original':saved['decision'],'precision_eligible':eligible,
                         'envelope':'BELOW' if below else 'ABOVE' if above else 'OVERLAP',
                         'lower':base-total,'upper':base+total,'above_margin':base-total-b})
assert len(rows)==32
assert all(x['components_equal'] and x['sum_delta']==0 and x['decision']==x['original'] for x in rows)
result['rheology']=rows
result['rheology_counts']={g:{'decisions':dict(collections.Counter(x['decision'] for x in rows if x['group']==g)),
                           'envelopes':dict(collections.Counter(x['envelope'] for x in rows if x['group']==g))}
                           for g in ('primary','secondary')}
reproduced=OUT/'rheology_reproduced.json'
saved=PW/'docs/analysis/val_case_rheology_decision_resolution_001/RESULTS.json'
result['rheology_official_reducer_byte_identical']=reproduced.read_bytes()==saved.read_bytes()

caf=read(PW/'docs/analysis/val_case_caffeine_decision_resolution_001/RESULTS.json')
caf_old=read(PW/'docs/analysis/sci_md_caffeine_delivery_001/RESULTS.json')
result['caffeine']=[]
for panel in ('primary','temperature_stress'):
    for ref, entry in caf['analysis'][panel]['sensitivity'].items():
        orig=caf_old['panels'][panel]
        gain=orig[ref]['full_scope_metrics']['R_mg_g']-orig['S2']['full_scope_metrics']['R_mg_g']
        assert gain==entry['baseline']['R_improvement_mg_g']
        result['caffeine'].append({'panel':panel,'ref':ref,'baseline_gain_recomputed':gain,
            'private_deletions_recomputed':False,'retained_deletion_range':entry['deletion_ranges']['R_improvement_mg_g'],
            'retained_sign_counts':entry['deletion_gain_sign_counts'],
            'retained_baseline_and_deletion_envelope':entry['baseline_plus_deletions_envelopes']['R_improvement_mg_g'],
            'all_numerical_lower_endpoints_positive':entry['all_deletion_allowance_lower_endpoints_strictly_positive']})

five=read(PW/'docs/analysis/val_case_5cqa_decision_resolution_001/RESULTS.json')
five_old=read(PW/'docs/analysis/sci_md_5cqa_assay_002/RESULTS.json')
cb='squared_mean_shot_error_contribution_mg_g'
cv='within_shot_centered_residual_variation_contribution_mg_g'
result['five_cqa']=[]
for panel, entry in five['analysis'].items():
    for pair, base in entry['baseline'].items():
        candidate,ref=pair.split('_vs_')
        orig=five_old['panels'][panel]
        gain=orig[ref]['full_scope_metrics']['R_mg_g']-orig[candidate]['full_scope_metrics']['R_mg_g']
        assert gain==base['R_improvement_mg_g']
        deviation=base[cb]+base[cv]-gain
        assert abs(deviation)<1e-15
        ds=entry['deletions'][pair]
        result['five_cqa'].append({'panel':panel,'pair':pair,'baseline_gain_recomputed':gain,
            'retained_squared_mean_contribution':base[cb],'retained_centered_residual_contribution':base[cv],
            'decomposition_sum_delta':deviation,'private_deletions_recomputed':False,
            'retained_deletion_range':ds['ranges']['R_improvement_mg_g'],
            'retained_sign_counts':ds['sign_counts']['R_improvement_mg_g'],
            'retained_numerical_envelope':ds['numerical_envelopes']['direct_gain_enclosure']})

result['protocol_chronology']=[]
for bundle in ('sci_md_mass_uncertainty_001','val_infra_decision_resolution_001','val_case_rheology_decision_resolution_001',
               'val_case_caffeine_decision_resolution_001','val_case_5cqa_decision_resolution_001'):
    paths=[f'docs/analysis/{bundle}/{name}' for name in ('PROTOCOL.md','RESULTS.json')]
    commits=[]
    for p in paths:
        text=subprocess.check_output(['git','-C',str(PW),'log','--reverse','--format=%H %cI %s','--',p],text=True)
        commits.append(text.strip().splitlines())
    if all(commits):
        spec=commits[0][0].split()[0]; results=commits[1][0].split()[0]
        ancestor=subprocess.run(['git','-C',str(PW),'merge-base','--is-ancestor',spec,results],capture_output=True).returncode==0
    else: ancestor=None
    result['protocol_chronology'].append({'bundle':bundle,'protocol_history':commits[0],'result_history':commits[1],
        'initial_protocol_ancestor_of_initial_result':ancestor,
        'caveat':'Git verifies committed ancestry, including equality when protocol and result first appear together; no assertion of private execution timing.'})

(OUT/'reanalysis_checks.json').write_text(json.dumps(result,indent=2)+'\n')
print('rheology',json.dumps(result['rheology_counts']))
print('official_rheology_bytes_equal',result['rheology_official_reducer_byte_identical'])
for key in ('caffeine','five_cqa'):
    for r in result[key]: print(key,json.dumps(r))
for c in result['protocol_chronology']: print('chronology',c['bundle'],c['initial_protocol_ancestor_of_initial_result'])
```

</details>


#### review_work/data/audit_additional_aggregates.py

SHA-256 `96c9c2ea2a5c5dc6b470a754319bfe089812df593fd2f17dad3079cadab2e84b`.

<details>
<summary>Show complete Python source — review_work/data/audit_additional_aggregates.py</summary>

```python
"""Bounded public-aggregate audit: MASS001/002/003 and mass-stop.

No source resolver, model, private shot vector or target scorer is imported.
Arithmetic reaggregation verifies the public summaries, not underlying observations.
"""
from pathlib import Path
import hashlib
import json
import math

ROOT = Path(__file__).resolve().parents[2]
PW = ROOT / 'puckworks'
OUT = Path(__file__).resolve().parent
SHA = '9dd456be7fd797b9cda0a2bbf50d1ac717d72835'


def read_case(name):
    p = PW / 'docs/analysis' / name / 'RESULTS.json'
    b = p.read_bytes()
    return json.loads(b), {
        'path': str(p.relative_to(PW)),
        'commit': SHA,
        'sha256': hashlib.sha256(b).hexdigest(),
    }


def compare(actual, retained, context):
    delta = actual - retained
    # Arithmetic identity tolerance only; no historical threshold changes.
    tol = 8 * math.ulp(max(1., abs(actual), abs(retained)))
    assert abs(delta) <= tol, (context, actual, retained, delta)
    return {'recomputed': actual, 'retained': retained, 'delta': delta}


result = {
    'scope': 'PUBLIC_CONDITION_AGGREGATES_ONLY; NO_PRIVATE_RECONSTRUCTION',
    'claim_ceiling': 'Aggregate arithmetic and public count consistency, not observation/prediction or native-run replay.',
    'cases': {},
}
all_metric_checks = []
all_comparison_checks = []
for number, candidate in [(1, 'MASS'), (2, 'MTF'), (3, 'ANCHORED_MASS')]:
    name = f'sci_md_mass_delivery_{number:03d}'
    d, identity = read_case(name)
    case = {'identity': identity, 'disposition': d['disposition'],
            'panels': {}, 'comparisons': {}, 'candidate': candidate}
    groups = d.get('groups', {'primary': d.get('balanced')})
    for panel, arms in groups.items():
        case['panels'][panel] = {}
        for arm, saved in arms.items():
            expected = saved['expected_conditions']
            rows = [r for r in d['conditions'][arm] if r['condition'] in expected]
            assert len(rows) == len(expected) == saved['conditions']
            assert {r['condition'] for r in rows} == set(expected)
            checks = {}
            if saved['metrics'] is not None:
                assert all(r['metrics'] is not None for r in rows)
                for key, retained in saved['metrics'].items():
                    value = sum(r['metrics'][key] for r in rows) / len(rows)
                    check = compare(value, retained, (name, panel, arm, key))
                    checks[key] = check
                    all_metric_checks.append(check)
            else:
                # Do not turn any available subset into a full-panel metric.
                assert any(r['metrics'] is None for r in rows)
            passing = sum(r['adequacy'] == 'PASS' for r in rows)
            assert passing == saved['passing_conditions']
            case['panels'][panel][arm] = {
                'condition_ids': expected,
                'physical_shots': sum(r['shots'] for r in rows),
                'qualified_shots': sum(r['qualified_shots'] for r in rows),
                'retained_condition_summaries': rows,
                'retained_panel': saved,
                'metric_reaggregation': checks,
                'passing_conditions_recomputed': passing,
                'full_panel_reaggregation': 'COMPLETE' if checks else 'UNAVAILABLE_IN_ORIGINAL_PRESERVED',
            }
    for ref, original in d['comparisons'].items():
        c = groups['primary'][candidate]['metrics']
        r = groups['primary'][ref]['metrics']
        values = {
            'R_reduction_pp': r['R_pp'] - c['R_pp'],
            'relative_R_reduction': (r['R_pp'] - c['R_pp']) / r['R_pp'],
            'abs_B_deterioration_pp': c['abs_B_pp'] - r['abs_B_pp'],
            'R_delta_allowance_pp': c['R_allowance_pp'] + r['R_allowance_pp'],
            'abs_B_delta_allowance_pp': c['B_allowance_pp'] + r['B_allowance_pp'],
        }
        checks = {key: compare(value, original[key], (name, ref, key))
                  for key, value in values.items()}
        all_comparison_checks.extend(checks.values())
        case['comparisons'][ref] = {'recomputed': checks, 'retained': original}
    case['secondary_scope'] = d.get('ramps', 'PANELS_ABOVE' if number == 1 else 'NO_SECONDARY_PANEL_PUBLISHED_IN_THIS_RESULT')
    # Preserve descriptive bootstrap summaries as producer evidence, not new CIs.
    if 'bootstrap' in d:
        case['retained_bootstrap'] = d['bootstrap']
        case['bootstrap_recomputed'] = False
    if 'diagnostics' in d:
        case['retained_diagnostics'] = d['diagnostics']
        case['diagnostics_recomputed_from_private_rows'] = False
    result['cases'][name] = case

stop, identity = read_case('sci_md_mass_stop_decision_001')
stop_checks = []
for panel, arms in stop['metrics'].items():
    assert set(arms) == {'C0', 'C2', 'FIXED'}
    for arm, v in arms.items():
        n = v['eligible_physical_shots']
        assert n == stop['N'] == 11
        checks = {
            'denominator_matches': n == stop['N'],
            'decision_partition': v['qualified_decisions'] + v['abstentions'] + v['numerically_unresolved'] == n,
            'abstention_partition': v['correct_abstentions'] + v['missed_feasible_abstentions'] == v['abstentions'],
            'success_rate_all': v['successes'] / n == v['successes_over_all_shots'],
            'success_rate_decisions': v['successes'] / v['qualified_decisions'] == v['successes_among_decisions'],
            'successful_choice_partition': v['exact_oracle_choices'] + v['successful_choices_later_than_oracle'] == v['successes'],
            'observed_feasible_bounds': 0 <= v['observed_feasible_shots'] <= n,
        }
        assert all(checks.values()), (panel, arm, checks)
        stop_checks.append({'panel': panel, 'arm': arm, 'checks': checks, 'retained_metrics': v})
result['mass_stop'] = {
    'identity': identity, 'retained_result': stop,
    'public_count_checks': stop_checks,
    'private_action_join_recomputed': False,
    'limitation': 'No public per-condition/shot action input is reduced. Counts, ratios and partitions alone are checked; feasibility, oracle and regret remain retained producer statistics.',
}

# Complete the MASS006 influence map with every primary/temperature comparator.
unc, uid = read_case('sci_md_mass_uncertainty_001')
mass6, m6id = read_case('sci_md_mass_delivery_006')
gains = []
for panel in ('primary', 'temperature_stress', 'flow_stress'):
    p = mass6['panels'][panel]
    for ref in ('C0', 'C1', 'FIRST_ASSAY_EMPIRICAL'):
        c = p['C2']['full_scope_metrics']
        r = p[ref]['full_scope_metrics']
        gains.append({'panel': panel, 'candidate': 'C2', 'reference': ref,
                      'full_scope_baseline_gain_pp': None if c is None or r is None else r['R_pp'] - c['R_pp'],
                      'full_scope_defined': c is not None and r is not None})
result['mass006_all_comparator_baseline_gains'] = gains
result['summary'] = {
    'complete_panel_arm_count': sum(v['full_panel_reaggregation'] == 'COMPLETE' for c in result['cases'].values() for p in c['panels'].values() for v in p.values()),
    'unavailable_panel_arm_count_preserved': sum(v['full_panel_reaggregation'] != 'COMPLETE' for c in result['cases'].values() for p in c['panels'].values() for v in p.values()),
    'condition_summary_count': sum(len(rows) for n in (1,2,3) for rows in read_case(f'sci_md_mass_delivery_{n:03d}')[0]['conditions'].values()),
    'panel_metric_checks': len(all_metric_checks),
    'comparison_component_checks': len(all_comparison_checks),
    'maximum_absolute_metric_delta': max(abs(r['delta']) for r in all_metric_checks),
    'maximum_absolute_comparison_delta': max(abs(r['delta']) for r in all_comparison_checks),
    'mass_stop_panel_arm_count': len(stop_checks),
    'mass_stop_public_partition_and_rate_checks': sum(len(r['checks']) for r in stop_checks),
}
(OUT / 'additional_aggregate_checks.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result['summary'], indent=2))
for name, case in result['cases'].items():
    for panel, arms in case['panels'].items():
        for arm, v in arms.items():
            m = v['retained_panel']['metrics']
            print(name, panel, arm, None if m is None else {k:m[k] for k in ('R_pp','B_pp','abs_B_pp')}, v['retained_panel']['adequacy_status'])
print('mass006_all_comparator_baseline_gains', json.dumps(gains))
```

</details>


#### review_work/ewp/run_checks.py

Executed-source SHA-256 `a31c4034ef4bf791f35e91126fb91d7397da84886edff04e494143582540bed7`.

Archived portable-script SHA-256 `b4880b364da8f592135a3df227c422a3ee3320229544a8d59e6f9d17600f309b`.

<details>
<summary>Show complete Python source — review_work/ewp/run_checks.py</summary>

```python
import json, os, pathlib, platform, subprocess, sys, time

ROOT = pathlib.Path(__file__).resolve().parents[2]
REPO = ROOT / 'espresso-whole-pull'
OUT = ROOT / 'review_work/ewp'
PY = str(OUT / 'venv/bin/python')
env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1',
    EWP_POROSITY_PERMEABILITY_PRIOR_PUCKWORKS_ROOT=str(OUT/'pw-authority'),
    SCI_MD_012_PUCKWORKS_ROOT=str(OUT/'pw-authority'))
env.pop('PUCKWORKS_EXTERNAL_DATA_ROOT', None)
checks = [
 ('environment', [PY, '-c', "import platform,importlib.metadata,numpy,scipy; print(platform.python_version(),numpy.__version__,scipy.__version__,importlib.metadata.version('jsonschema'))"]),
 ('source_manifest', [PY, 'scripts/verify_source_manifest.py', '--root', '.']),
 ('static_validate', [PY, 'scripts/static_validate.py', '--root', '.']),
 ('unit_suite', [PY, '-m', 'unittest', 'discover', '-s', 'tests', '-p', 'test_*.py']),
 ('baseline_integrity', [PY, 'scripts/verify_v0_1_4_baseline_integrity.py', '--root', '.', '--output', str(OUT/'baseline_integrity.json')]),
 ('shell_syntax', ['bash', '-c', "bash -n Allrun Allverify Allclean Allwmake scripts/*.sh scripts/lib/*.sh"]),
]
records=[]
for name, cmd in checks:
    start=time.monotonic()
    log=OUT/'logs'/f'{name}.txt'
    with log.open('w') as fh:
        result=subprocess.run(cmd,cwd=REPO,env=env,stdout=fh,stderr=subprocess.STDOUT)
    row={'name':name,'cmd':cmd,'cwd':str(REPO),'exit':result.returncode,'seconds':time.monotonic()-start,'log':str(log)}
    records.append(row)
    (OUT/'checks.json').write_text(json.dumps({'evidence':'D-minus until root rechecks','checks':records},indent=2)+'\n')
    print(json.dumps(row),flush=True)
```

</details>


#### review_work/ewp/recompute.py

Executed-source SHA-256 `ed1cb3559e2771c8529a021c0973151dd975ea888c40a6ba44ab0bfebfb30ad9`.

Archived portable-script SHA-256 `ce6b50049443bd7fb495c0a76d812841e205f949999a67abf556634e1362e628`.

<details>
<summary>Show complete Python source — review_work/ewp/recompute.py</summary>

```python
"""Retained-result recomputation; no fitting, native runs, or protected inputs."""
from pathlib import Path
import csv, hashlib, json, math, random, statistics, sys
import numpy as np
from scipy.integrate import quad

ROOT=Path(__file__).resolve().parents[2]
REPO=ROOT/'espresso-whole-pull'
OUT=ROOT/'review_work/ewp'
def rows(path):
    with (REPO/path).open() as f:return list(csv.DictReader(f))
def avg(xs):return sum(xs)/len(xs)
def rms(xs):return math.sqrt(avg([x*x for x in xs]))
def nr(xs,p):return sorted(xs)[max(0,math.ceil(p*len(xs))-1)]
def audit(task):
    source=f'docs/analysis/{task}/BREW_RESULTS.csv'
    data=rows(source)
    by={}
    for row in data:
        if not row['predicted_flow_g_s']:continue
        by.setdefault(row['model_id'],{}).setdefault(row['outer_fold'],[]).append(row)
    result={}
    for model,folds in by.items():
        fm={}
        for fold,rs in folds.items():
            err=[float(r['predicted_flow_g_s'])-float(r['observed_flow_g_s']) for r in rs]
            fm[fold]={'n':len(rs),'rmse_g_s':rms(err),'mean_error_g_s':avg(err),
                      'normalized_rmse':rms(err)/float(rs[0]['training_scale_g_s'])}
        result[model]={'n_brews':sum(v['n'] for v in fm.values()),'n_conditions':len(fm),
           'status':'COMPLETE' if len(fm)==11 else 'INCOMPLETE_DIAGNOSTIC_ONLY_NO_AGGREGATE_ADJUDICATION',
           'mean_condition_rmse_g_s':avg([v['rmse_g_s'] for v in fm.values()]),
           'normalized_loss':avg([v['normalized_rmse'] for v in fm.values()]),
           'mean_condition_error_g_s':avg([v['mean_error_g_s'] for v in fm.values()]),
           'max_error_column_discrepancy_g_s':max(abs((float(r['predicted_flow_g_s'])-float(r['observed_flow_g_s']))-float(r['error_g_s'])) for rs in folds.values() for r in rs)}
    cond=[]
    base=by['HYD_B0_TRAINING_MEAN']
    for fold,rs in base.items():
        q=[float(r['observed_flow_g_s']) for r in rs]
        p=[float(r['line_pressure_bar']) for r in rs]
        cond.append({'fold':fold,'condition':rs[0]['condition_id'],'n':len(rs),
                     'mean_pressure_bar':avg(p),'mean_observed_flow_g_s':avg(q),
                     'repeat_sd_g_s':statistics.stdev(q),
                     'repeat_mean_standard_uncertainty_g_s':statistics.stdev(q)/math.sqrt(len(rs))})
    cond.sort(key=lambda r:r['mean_pressure_bar'])
    hi=[r for r in cond if r['mean_pressure_bar']>=8.5]
    p=np.array([r['mean_pressure_bar'] for r in hi]); q=np.array([r['mean_observed_flow_g_s'] for r in hi]); w=(p-p.mean())/sum((p-p.mean())**2)
    slope=float(w@q)
    uslope=math.sqrt(sum(float(wi)**2*r['repeat_mean_standard_uncertainty_g_s']**2 for wi,r in zip(w,hi)))
    slopes={'observed_slope_g_s_bar':slope,'repeat_only_standard_uncertainty_g_s_bar':uslope,
            'normal_approx_repeat_only_95_range':[slope-1.96*uslope,slope+1.96*uslope],
            'support_conditions':[r['condition'] for r in hi],
            'qualifications':['fixed observed pressure coordinates','independent group mean errors assumed',
              'between-brew sampling variance only; not instrument uncertainty',
              'pressure and calibration input uncertainties unavailable; not full u_val']}
    for model,folds in by.items():
        if any(r['fold'] not in folds for r in hi):
            slopes[model]={'status':'REQUIRED_MODEL_BLOCKED_NO_COMPLETE_SLOPE'}
            continue
        ps=[avg([float(x['predicted_flow_g_s']) for x in folds[r['fold']]]) for r in hi]
        slopes[model]={'predicted_slope_g_s_bar':float(w@np.array(ps)),
                      'slope_error_g_s_bar':float(w@np.array(ps))-slope}
    return data,by,result,cond,slopes

def bootstrap(by,a,b,low=False,count=2000,seed=20260902):
    folds=sorted(set(by[a])&set(by[b]))
    if low:folds=[f for f in folds if avg([float(r['line_pressure_bar']) for r in by[a][f]])<=5.25]
    errors={}
    scales={}
    for model in (a,b):
        for f in folds:
            errors[f,model]={r['physical_unit_id']:(float(r['predicted_flow_g_s'])-float(r['observed_flow_g_s']))**2 for r in by[model][f]}
            scales[f]=float(by[model][f][0]['training_scale_g_s'])
    rng=random.Random(seed);samples=[]
    for _ in range(count):
        sampled=[rng.choice(folds) for _ in folds]; loss={a:0.,b:0.}
        for f in sampled:
            shared=sorted(errors[f,a].keys() & errors[f,b].keys())
            picked=[rng.choice(shared) for _ in shared]
            for model in (a,b):
                loss[model]+=math.sqrt(avg([errors[f,model][u] for u in picked]))/scales[f]
        samples.append((loss[a]-loss[b])/len(folds))
    return {'n':count,'seed':seed,'lower':nr(samples,.025),'upper':nr(samples,.975),
            'unit':'condition then paired brew; no refitting','quantiles':'nearest rank'}

results={'evidence':'D-minus until root rechecks','ewp_commit':'4284e9460c8057053e95de7cfa2fb3590e68e9db','tasks':{}}
for task,pair in [('sci_md_010',('HYD_B1_PRESSURE_QUADRATIC','HYD_E1_LUMPED_DARCY')),('sci_md_011',('HYD_B1_PRESSURE_QUADRATIC','HYD_P1_POROELASTIC_UNIVERSAL_LIMIT'))]:
    data,by,metrics,conditions,slopes=audit(task)
    entry={'metrics':metrics,'scored_support_repeatability':conditions,'high_pressure_direction':slopes,
        'paired_comparison':{'pair':pair,'full':bootstrap(by,*pair),'low_pressure':bootstrap(by,*pair,low=True)},
        'source_sha256':hashlib.sha256((REPO/f'docs/analysis/{task}/BREW_RESULTS.csv').read_bytes()).hexdigest()}
    results['tasks'][task]=entry

# Independent quadrature verifies the scalar C++ oracle's finite-porosity integral.
oracle=rows('docs/analysis/sci_md_011/CLOSURE_ORACLE_RESULTS.csv')
results['oracle_columns']=list(oracle[0])
orow=[]
for phi in (.1,.12202109866812735,.4):
    for x in (0.,.1,.25,.5,.9,.999999,1.):
        j=quad(lambda z:(1-z)**3/(1-phi*z),0,x,epsabs=1e-13,epsrel=1e-13)[0]
        j1=quad(lambda z:(1-z)**3/(1-phi*z),0,1,epsabs=1e-13,epsrel=1e-13)[0]
        orow.append({'phi':phi,'x':x,'quadrature_J':j,'normalized_q':j/j1,'derivative':(1-x)**3/(1-phi*x)})
results['independent_closure_quadrature']=orow
oracle_errors=[]
for row in oracle:
    phi=float(row['phi']);x=float(row['x'])
    j=quad(lambda z:(1-z)**3/(1-phi*z),0,x,epsabs=1e-13,epsrel=1e-13)[0]
    j1=quad(lambda z:(1-z)**3/(1-phi*z),0,1,epsabs=1e-13,epsrel=1e-13)[0]
    oracle_errors.append(abs(float(row['production_fphi'])-j/j1))
results['quadrature_oracle_check']={'n':len(oracle),'max_abs_normalized_q_error':max(oracle_errors)}

# R0 source-suppression counterexample in the existing specification: mass-conservative overshoot.
phi=.4;ms=235.2;c=0.;dt=5.;k=.15;cap=180.
release=min(k*ms*max(1-c/cap,0),ms/dt)
cnew=c+dt*release/phi;msnew=ms-dt*release
results['closed_cell_diagnostic']={'initial_ms_kg_m3_bed':ms,'step_s':dt,'release_kg_m3_bed_s':release,
    'new_c_kg_m3_liquid':cnew,'ceiling_kg_m3_liquid':cap,
    'mass_residual_kg_m3_bed':ms-(msnew+phi*cnew),'not_admissible_R0_timestep':True}
results['R0_timescale_diagnostic']={'local_fixed_inventory_relaxation_time_s':phi*cap/(k*ms),
    'pore_water_volume_mL':.020/(1400*(1-phi))*phi*1e6,
    'plug_nominal_residence_time_s':(.020/(1400*(1-phi))*phi*1e6)/1.482675972,
    'qualifier':'assumed fixed local inventory and R0 hydraulic reference; not observed equilibrium or a particle-history estimate'}

(OUT/'recomputed.json').write_text(json.dumps(results,indent=2)+'\n')
print(json.dumps({t:{'metrics':v['metrics'],'paired_comparison':v['paired_comparison'],
 'high_pressure_direction':v['high_pressure_direction']} for t,v in results['tasks'].items()},indent=2))
```

</details>


#### review_work/ewp/augment_results.py

Executed-source SHA-256 `36cfc43802478cd8a4f7fc2d32257a76a4d8a61ecf4742ea61832ee5cdc67a49`.

Archived portable-script SHA-256 `9d92aa5c2b062364f89d4b43147be1a9cab076145f6c9e375c7f2ff4cadf7bd3`.

<details>
<summary>Show complete Python source — review_work/ewp/augment_results.py</summary>

```python
"""Supplement the frozen independent EWP recomputation with aggregate checks."""
from pathlib import Path
import csv, hashlib, json, math, subprocess

BASE=Path(__file__).resolve().parents[2]
REPO=BASE/'espresso-whole-pull'
OUT=BASE/'review_work/ewp'
def read_json(p): return json.loads((REPO/p).read_text())
def rows(p):
    with (REPO/p).open() as f: return list(csv.DictReader(f))
x=json.loads((OUT/'recomputed.json').read_text())
x['environment']={'python':'3.12.14','CI_python':'3.12.3','numpy':'1.26.4','scipy':'1.11.4','jsonschema':'4.23.0',
  'external_data_root':'UNSET','OpenFOAM_runs':0,'tracked_repo_mutation':False,
  'full_suite':{'tests':1635,'seconds_reported':710.433,'failures':1,'errors':23,'skipped':21,
    'classification':'22 errors and 1 failure from sandbox /proc PID mismatch; 1 error from /tmp Git ancestor'},
  'affected_rerun':{'tests':42,'seconds_reported':.353,'result':'OK','scope':'unmodified lifecycle module and two-assay LoaderTests',
    'command':'cd espresso-whole-pull && TMPDIR=/dev/shm PYTHONDONTWRITEBYTECODE=1 ../review_work/ewp/venv/bin/python -m unittest tests.test_sci_lc_001a_family_controller tests.test_research_two_assay_mass_delivery.LoaderTests',
    'execution':'approved escalation; no mocks or test modifications'}}

for task,file,field in [('sci_md_008','INVENTORY_SCALE_INVARIANCE.csv','fraction_shape_max_absolute_difference'),
                        ('sci_md_009','NONLINEAR_RESPONSE_VALIDATION.csv','relative_error')]:
    source=f'validation/{task}/{file}'; r=rows(source)
    result={'n_metric_rows':len(r),'maximum_metric':max(float(z[field]) for z in r),
      'failed_metric_rows':sum(z['status']=='FAIL' for z in r),
      'source_sha256':hashlib.sha256((REPO/source).read_bytes()).hexdigest(),
      'evidence':'reduction of retained synthetic/native metric rows; no native execution'}
    if task=='sci_md_008':
        result['maximum_pressure_difference_Pa']=max(float(z['pressure_max_absolute_difference_Pa']) for z in r)
        result['thresholds']=sorted(set(float(z['shape_tolerance']) for z in r))
    else: result['threshold']=.02
    x[task]=result

r=rows('docs/analysis/sci_md_012/ROOT_FEASIBILITY.csv')
a,b,c=.017184292098914252,.03670858658698296,.2831597837775055
q=float(r[0]['q_hi_g_s']); p=float(r[0]['frozen_Pc_bar']); eps=1e-10
drop=a*q*q+b*q+c; ceiling=p*(1-eps)+drop
required=max((float(z['measured_line_pressure_bar'])-drop)/(1-eps) for z in r)
x['sci_md_012_recomputed']={'n_brews':len(r),'feasible_brews':sum(float(z['measured_line_pressure_bar'])<=ceiling for z in r),
   'frozen_coupled_ceiling_bar':ceiling,'positive_adapter_drop_bar':drop,
   'maximum_ceiling_discrepancy_bar':max(abs(ceiling-float(z['coupled_line_pressure_ceiling_bar'])) for z in r),
   'maximum_required_Pc_bar':required,'relative_Pc_increase':(required-p)/p,
   'all_closure_evaluations_finite':all(z['fphi_finite']=='True' for z in r),
   'qualifier':'algebraic representability only, no refit or score'}

material=read_json('docs/analysis/ewp_porosity_permeability_prior_001/POROSITY_MATERIALITY.json')
errors=[]; support=[]
for s in material['support_decisions']:
    obs=s['observables']; reduced={}
    for k,z in obs.items():
        if 'relative_effect' in z:
            value=abs(z['source_value']-z['baseline_value'])/abs(z['baseline_value'])
            errors.append(abs(value-z['relative_effect']))
            reduced[k]={'baseline':z['baseline_value'],'source':z['source_value'],'absolute_relative_effect':value}
    support.append({'support':s['support_id'],'observables':reduced})
x['porosity_materiality']={'threshold':max(material['absolute_engineering_floor'],material['maximum_relative_convergence_uncertainty']*material['numerical_separation_multiplier']),
   'maximum_relative_effect_discrepancy':max(errors),'support':support,
   'prose_defect':'RESULT.md L19-20 labels dimensionless relative_effect using dimensional observable names; JSON correct'}

comparison=read_json('validation/wp03/WP03_002_CORRECTED_COMPARISON.json')
compact=[]
for s in comparison['corrected_compaction']:
    compact.append({'id':s['id'],'pressure_bar':s['pressure_bar'],'endpoint':s['endpoint'],
      'metrics':{k:s['metrics'][k]['full'] for k in ('pressure','flow','mass')},
      'source_window_s':s['metrics']['source_window_s'],'model_window_s':s['metrics']['model_window_s']})
x['wp03_retained_comparison']={'evidence':'READ_RETAINED_NOT_RERUN','metric_contract':comparison['metric_contract'],'cases':compact,
  'ordering':comparison['ordering'],'uncertainty':'source_uncertainty_coverage is retained-source interval coverage, not full validation uncertainty; u_num/u_input/covariance unavailable'}
x['runtime_lock_distance']={'from':'fc61c4670ec7bf801e40bb391aab16048b8da26b','to':'9dd456be7fd797b9cda0a2bbf50d1ac717d72835',
  'all_commits':int(subprocess.check_output(['git','-C',str(BASE/'puckworks'),'rev-list','--count','fc61c4670ec7bf801e40bb391aab16048b8da26b..9dd456be7fd797b9cda0a2bbf50d1ac717d72835'])),
  'first_parent':int(subprocess.check_output(['git','-C',str(BASE/'puckworks'),'rev-list','--first-parent','--count','fc61c4670ec7bf801e40bb391aab16048b8da26b..9dd456be7fd797b9cda0a2bbf50d1ac717d72835']))}
(OUT/'results.json').write_text(json.dumps(x,indent=2)+'\n')
print(json.dumps({k:x[k] for k in ('sci_md_008','sci_md_009','sci_md_012_recomputed','runtime_lock_distance')},indent=2))
```

</details>


#### review_work/census/make_classifications.py

SHA-256 `e4f44180a50b258061b96173dbd2747b1dfe09f07e62bca53bf8554f97c1428d`.

<details>
<summary>Show complete Python source — review_work/census/make_classifications.py</summary>

```python
"""Material-purpose classification fixed after title/path/declaration inspection.

Amendment to preaudit (approved by root before aggregation): rename bin three
from retained-evidence analysis to scientific analysis/comparison. New scenario
runs and empirical predictor evaluations under unchanged production equations
cannot truthfully be called retained-output-only work. Every analysis row has
one of three subtypes. All bins describe integrated activity, not person-hours.
"""
import json
from pathlib import Path
OUT=Path(__file__).resolve().parent
d={}
def add(repo,nums,cat,reason,subtype=None,alternatives=(),mirror=False):
    for n in nums:
        key=f'{repo}:{n}'
        assert key not in d,key
        d[key]={'category':cat,'alternative_categories':list(alternatives),'classification_reason':reason,'mirrored_result_handoff':mirror}
        if subtype: d[key]['analysis_subtype']=subtype

add('PW',[312],'governing_physics','Complete the source post-saturation headspace ODE and water accounting in the operative Foster machine model; declared GOVERNING_PHYSICS_CHANGE.')
add('PW',[326,325,318,317,315,314,310,309],'numerical_methods','Implement or repair an extraction numerical backend, comparator, initial-state/forcing API or conservative observer; primary code delta and NUMERICAL_METHOD_CHANGE declaration agree.')
add('PW',[308],'numerical_methods','Add an independent source-equation Grudeva reduced solver, registry gates and reference runner. Classified as numerical implementation; new solver representation and product wiring make physics/product alternatives reasonable.',alternatives=('governing_physics','product_ui'))
add('PW',[304],'numerical_methods','Repair off-knot geometric inventory consistency and operative initial-inventory accounting; selected PR declaration NUMERICAL_METHOD_CHANGE. Same integration also audits evidence bindings and refreshes claims.',alternatives=('assurance_governance',))
add('PW',[301,302,303],'numerical_methods','Add inverse stopping or finite/continuous assay-set bounding algorithms over the retained conditional-tail predictor; new mathematical query capability without changed production equations.',alternatives=('scientific_analysis',))
add('PW',[319,320],'numerical_methods','Add checked finite-volume state-set delivery bounds and prefix-conditioned optimization/certificates. New numerical query capability over unchanged forward equations.',alternatives=('scientific_analysis',))
add('PW',[340,339,338,334,331,330],'scientific_analysis','Recalculate declared metrics/sensitivity or compare previously retained qualified outputs; no new forward scientific execution.','retained-output only')
add('PW',[329,328,327],'scientific_analysis','Qualify or diagnose unchanged numerical routes through fresh bounded baseline/refinement evaluations and retained-evidence arithmetic; no method delta.','new scenario evaluation under unchanged equations',alternatives=('numerical_methods',))
add('PW',[307,300,299,298,297,296,295,294,292,290,288,286,284,282,280,278,276,268],'scientific_analysis','Develop/evaluate conditional empirical predictors or test source transfer using existing source evidence. Includes new fits/predictions or prescribed-case computations, not retained-output-only reanalysis.','new scenario evaluation under unchanged equations')
add('PW',[274,272],'scientific_analysis','Primary purpose is source-conditioned extraction transfer/calibration adjudication; construction/verification of a conservative analysis reference is also substantive.','new scenario evaluation under unchanged equations',alternatives=('numerical_methods',))
add('PW',[270,266,252,246],'scientific_analysis','Qualify source normalization, observation/inventory semantics, or protected-adapter metadata before scientific use; source/data-contract analysis, not new production physics.','source/data qualification')
add('PW',[259],'scientific_analysis','Source-faithful Pannusch reconstruction, fit/prediction eligibility and metric attribution; includes model/source corrections and gates. Earlier review conclusions not used for classification.','source/data qualification',alternatives=('numerical_methods',))
add('PW',[261],'scientific_analysis','Reviewed external-corpus authority and complete family inventory; data-source qualification with discovery/governance tooling.','source/data qualification',alternatives=('assurance_governance',))
add('PW',[254],'scientific_analysis','Prospective species inventory/extractability measurement contract and source/method/laboratory qualification; no data acquisition. Large control package makes assurance a plausible alternative.','source/data qualification',alternatives=('assurance_governance',))
add('PW',[244],'scientific_analysis','Common-observable response atlas, observability and measurement-value screen; substantial evidence-schema and verifier machinery alongside scientific comparison.','new scenario evaluation under unchanged equations',alternatives=('assurance_governance',))
add('PW',[335,323,260,251],'assurance_governance','Prospective decision helper/policy, CI budget, available-data preflight infrastructure, or silent protected-integrity QA and parameterization-freeze controls.')
add('PW',[263],'assurance_governance','Repair pressure-bearing provenance and preserve schema-v6 data during enrichment; source-boundary qualification is a secondary scientific use.',alternatives=('scientific_analysis',))
add('PW',[332,322],'documentation_status','Canonical review/development guide and navigation only; no source runtime or scientific comparison modified.')
add('PW',[305],'documentation_status','Preserve an independent review and its audit/replay evidence; earlier review conclusions not used at classification.',alternatives=('scientific_analysis',))
add('PW',[265],'documentation_status','Make the inspected external-data collection discoverable through a canonical guide and generated index; builds supporting inventory tooling.',alternatives=('assurance_governance',))
add('PW',[324],'product_ui','Disclose Guided Pull pressure/evidence limitations on executable product report surfaces.',alternatives=('documentation_status',))
add('PW',[255,256],'product_ui','Publishing-system foundation or its outward safety correction; counted for completeness but outreach/release mechanics are out of scientific scope.')

add('EWP',[152,158,160,95],'governing_physics','Add/alter native local-versus-aggregate/radial viscosity coupling or indexed passive-species state equations; declared GOVERNING_PHYSICS_CHANGE.')
add('EWP',[113,110],'numerical_methods','Add discrete prescribed-flow boundary or exact mass-defined fraction observer; declared NUMERICAL_METHOD_CHANGE.')
add('EWP',[146],'numerical_methods','Add native piecewise-linear prescribed-pressure history with independent integration/probe verification. Contract declares no governing-physics change; temporal forcing interface is a numerical capability.',alternatives=('governing_physics',))
add('EWP',[166],'numerical_methods','Repair native initial-scalar compatibility under pressure-history forcing and qualify its transfer; unchanged equations, material initialization behavior plus new case evaluation.',alternatives=('scientific_analysis',))
add('EWP',[171],'numerical_methods','Add conforming interface-aligned radial geometry/case-generation option and evaluate arrangement sensitivity; native equations/operators unchanged, fresh native runs performed.',alternatives=('scientific_analysis',))
add('EWP',[200,198,196,194,192,190,188,186,184,182,180,178,176,174,106,87],'scientific_analysis','Integrate an exact research consumer or documented handoff of an already evaluated Puckworks result; no independent repetition of the scientific dataset.','retained-output only',mirror=True,alternatives=('documentation_status',))
add('EWP',[172],'scientific_analysis','Observe retained native snapshots through a source-assay diagnostic with new observer arithmetic; no new native runs.','retained-output only')
add('EWP',[169,164,162,156,154,150,142,140,132,131,129,127,125,121,115,114,103,101,99,71,80],'scientific_analysis','New source/model/scenario evaluations under unchanged production equations, mechanism/comparator tests, or protected scoring metadata. Actual protected target values not inspected.','new scenario evaluation under unchanged equations')
add('EWP',[144],'scientific_analysis','Reconstruct monotonicity/domain and failure cause from the existing finite-porosity branch and source equations; no new production run.','retained-output only')
add('EWP',[136,134,123,138,108,97,89],'scientific_analysis','Source/input/parameter/measurement-contract qualification or evidence fusion; no new governing equations and no physical data collection.','source/data qualification')
add('EWP',[119],'assurance_governance','Install available-data preflight and existing-data leverage controls/programme; source qualification and scientific next-decision analysis are also substantial.',alternatives=('scientific_analysis',))
add('EWP',[116],'assurance_governance','Adopt data-first task-selection and proportional-correction policy; no scientific execution or solver changes.')
add('EWP',[204,202,201,167,148,111],'documentation_status','Link canonical reviews/data guide, preserve private work record or reconcile already-completed qualification/status; no runtime science delta.')

(OUT/'classifications.json').write_text(json.dumps(d,indent=2)+'\n')
print(f'{len(d)} first-parent integrations classified')
```

</details>


#### review_work/census/build_census.py

SHA-256 `c91f3bf23c5fa85fb7b1df4f2f47cb2fa68053f63b6df70affd276f069d1eed3`.

<details>
<summary>Show complete Python source — review_work/census/build_census.py</summary>

```python
#!/usr/bin/env python3
"""Read-only first-parent integration and static file/AST census.

Usage: python review_work/census/build_census.py [--classifications PATH]
All inputs are pinned Git objects, not the possibly modified working tree.
No dataset values, model APIs, protected integrity tests or solver are executed.
Files protected by target policy are not opened. Restricted source is counted
only; no source text is emitted. Earlier reviews are not opened.
"""
from __future__ import annotations
import argparse, ast, collections, csv, datetime as dt, hashlib, io, json, pathlib, re, subprocess

ROOT = pathlib.Path(__file__).resolve().parents[2]
OUT = pathlib.Path(__file__).resolve().parent
END = dt.datetime.fromisoformat('2026-10-18T22:06:06+00:00')
REPOS = {
    'PW': ('puckworks', '9dd456be7fd797b9cda0a2bbf50d1ac717d72835'),
    'EWP': ('espresso-whole-pull', '4284e9460c8057053e95de7cfa2fb3590e68e9db'),
}
DENIED = {
    'docs/analysis/sci_md_004/angeloni_targets_long.csv',
    'puckworks/data/angeloni2023/bioactives.csv',
    'puckworks/data/angeloni2023/total_solids.csv',
    'puckworks/data/angeloni2023/lipids.csv',
}
CODE_EXT = {'.py', '.C', '.H', '.cpp', '.h', '.cc', '.c', '.sh', '.js', '.ts', '.tsx', '.jsx'}
DECL = re.compile(r'\b(?:NO_GOVERNING_PHYSICS_CHANGE|SOURCE_SCENARIO_CHANGE_ONLY|NUMERICAL_METHOD_CHANGE|GOVERNING_PHYSICS_CHANGE|GEOMETRY_COMPATIBILITY_NO_GOVERNING_PHYSICS_CHANGE)\b')
CATS = ['governing_physics', 'numerical_methods', 'scientific_analysis', 'assurance_governance', 'documentation_status', 'product_ui']

def git(repo, *args, binary=False):
    return subprocess.check_output(['git', '-C', str(ROOT/repo), *args], text=not binary)

def blob(repo, sha, path):
    if path in DENIED:
        raise ValueError('protected path')
    return git(repo, 'show', f'{sha}:{path}', binary=True)

def code_area(tag, path):
    """Exhaustive exclusive path classification, not semantic LOC attribution."""
    if path.startswith('tests/') or path.startswith('test/'):
        return 'tests'
    if tag == 'PW':
        if path.startswith('puckworks/models/'):
            return 'models'
        if path.startswith('puckworks/analysis/'):
            return 'analysis'
        if path.startswith(('puckworks/validation/', 'puckworks/paper_a/', 'puckworks/paper3/', 'puckworks/paper1/', 'puckworks/claims/')) or pathlib.PurePosixPath(path).name in {'gate_runner.py', 'statusdoc.py'}:
            return 'assurance_governance'
        if path.startswith(('puckworks/product/', 'puckworks/viz/', 'apps/', 'site/', 'docs/assets/')):
            return 'product_ui'
        if path.startswith(('tools/', '.github/')):
            return 'engineering_tools'
        return 'other_code'
    if path.startswith('solver/'):
        return 'models'
    if path.startswith(('analysis/', 'tools/sci_', 'tools/xsv_', 'tools/obs_', 'tools/inventory_scaled_composition/')):
        return 'analysis'
    if path.startswith('scripts/'):
        name=pathlib.PurePosixPath(path).name
        if name.startswith(('verify_', 'validate_', 'static_validate', 'check_', 'audit_', 'replay_')):
            return 'assurance_governance'
        if name.startswith(('research_', 'run_sci_', 'report_sci_', 'diagnose_sci_', 'analyze_', 'analyse_', 'sci_', 'obs_', 'xsv_', 'run_xsv_', 'run_obs_', 'run_ewp_', 'run_pannusch_', 'data_leverage')):
            return 'analysis'
        return 'engineering_tools'
    return 'other_code'

def parse_numstat(repo, sha, parent):
    rows=[]
    for line in git(repo, 'diff', '--numstat', '--no-renames', parent, sha).splitlines():
        add,delete,path=line.split('\t',2)
        rows.append({'path':path,'added':int(add) if add!='-' else None,'deleted':int(delete) if delete!='-' else None})
    return rows

def declarations(repo,sha,files,message):
    # Only declaration metadata; never output file text or target values.
    found=[{'path':'COMMIT_MESSAGE','tokens':sorted(set(DECL.findall(message)))}]
    for f in files:
        p=f['path']
        if p in DENIED or p.startswith(('docs/research/', 'puckworks/data/','tests/')):
            continue
        name=pathlib.PurePosixPath(p).name.lower()
        if not p.startswith(('docs/analysis/','docs/wp','provenance/')) or not (name.endswith(('.md','.json')) and any(k in name for k in ('contract','protocol','authority','handoff'))):
            continue
        try: text=blob(repo,sha,p).decode('utf-8')
        except (subprocess.CalledProcessError,UnicodeDecodeError): continue
        tokens=sorted(set(DECL.findall(text)))
        if tokens:
            found.append({'path':p,'tokens':tokens})
    return [r for r in found if r['tokens']]

def integrations():
    rows=[]
    for tag,(repo,sha) in REPOS.items():
        # Enumerate full first-parent history then filter timestamps explicitly;
        # --since can omit commits beyond an out-of-order timestamp boundary.
        log=git(repo,'log',sha,'--first-parent','--format=%H%x1f%cI%x1f%P%x1f%s%x1f%b%x1e')
        for rec in log.split('\x1e'):
            if not rec.strip(): continue
            h,date,parents,subject,body=rec.strip('\n').split('\x1f',4)
            date_obj=dt.datetime.fromisoformat(date)
            if not END-dt.timedelta(days=60) <= date_obj <= END: continue
            pp=parents.split()
            files=parse_numstat(repo,h,pp[0]) if pp else []
            m=re.search(r'(?:pull request |Merge PR |\(#)(?:#)?(\d+)',subject,re.I)
            if not m:
                m=re.search(r'#(\d+)',subject)
            pr=int(m.group(1)) if m else None
            # Default merge messages put the PR's title in the first body line.
            title=next((x.strip() for x in body.splitlines() if x.strip()),subject) if subject.startswith('Merge pull request') and ' from ' in subject else subject
            rows.append({'repository':tag,'sha':h,'committer_date':date,'in_30d':date_obj>=END-dt.timedelta(days=30),'integration_kind':'merge_commit' if len(pp)>1 else ('squash_pr' if pr else 'direct_first_parent'), 'pr':pr,'subject':subject,'title':title,'parents':pp,'files':files,'declarations':declarations(repo,h,files,subject+'\n'+body),'added':sum(f['added'] or 0 for f in files),'deleted':sum(f['deleted'] or 0 for f in files)})
    return rows

def static_inventory():
    allrows=[]
    summaries={}
    for tag,(repo,sha) in REPOS.items():
        paths=git(repo,'ls-tree','-r','--name-only',sha).splitlines()
        docs=[p for p in paths if p.startswith('docs/')]
        bundles=sorted({p.split('/')[2] for p in paths if p.startswith('docs/analysis/') and len(p.split('/'))>3})
        s={'sha':sha,'tracked_files':len(paths),'docs_files':len(docs),'analysis_bundles':len(bundles),'analysis_bundle_names':bundles,'areas':{},'python_static_test_functions':0,'python_test_files':0,'test_ast_failures':[]}
        for p in paths:
            if p in DENIED or (pathlib.PurePosixPath(p).suffix not in CODE_EXT and pathlib.PurePosixPath(p).name not in {'Allwmake','Allrun','Allverify','Allclean'}):
                continue
            try: data=blob(repo,sha,p)
            except subprocess.CalledProcessError: continue
            try: text=data.decode('utf-8')
            except UnicodeDecodeError: continue
            area=code_area(tag,p)
            row={'repository':tag,'path':p,'area':area,'physical_lines':len(text.splitlines()),'nonblank_lines':sum(bool(l.strip()) for l in text.splitlines()),'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest(),'static_test_functions':0}
            # AST parsing executes nothing and emits only a count, including for
            # tests excluded from execution by the protected-target policy.
            if area=='tests' and p.endswith('.py'):
                s['python_test_files']+=1
                try:
                    tree=ast.parse(text)
                    row['static_test_functions']=sum(isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)) and n.name.startswith('test_') for n in ast.walk(tree))
                    s['python_static_test_functions']+=row['static_test_functions']
                except SyntaxError:
                    s['test_ast_failures'].append(p)
            a=s['areas'].setdefault(area,{'files':0,'physical_lines':0,'nonblank_lines':0})
            a['files']+=1
            a['physical_lines']+=row['physical_lines']
            a['nonblank_lines']+=row['nonblank_lines']
            allrows.append(row)
        if tag=='PW':
            mod=ast.parse(blob(repo,sha,'puckworks/models/__init__.py').decode())
            s['component_constructor_calls']=sum(isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=='Component' for n in ast.walk(mod))
            # Count each registered gate variable/attribute in Component.gates.
            calls=[n for n in ast.walk(mod) if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=='Component']
            gate_nodes=[kw.value for n in calls for kw in n.keywords if kw.arg=='gates']
            s['component_gate_refs']=[]
            for g in gate_nodes:
                for n in ast.walk(g):
                    if isinstance(n,ast.Attribute) and n.attr.startswith('gate_'): s['component_gate_refs'].append(n.attr)
                    elif isinstance(n,ast.Name) and n.id.startswith('gate_'): s['component_gate_refs'].append(n.id)
            gg=ast.parse(blob(repo,sha,'puckworks/validation/gates.py').decode())
            s['gate_function_names']=[n.name for n in gg.body if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)) and n.name.startswith('gate_')]
            s['gate_functions']=len(s['gate_function_names'])
            s['registered_gate_refs_count']=len(s['component_gate_refs'])
            s['unregistered_gate_function_names']=sorted(set(s['gate_function_names'])-set(s['component_gate_refs']))
        summaries[tag]=s
    return summaries,allrows

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--classifications',type=pathlib.Path,default=OUT/'classifications.json')
    args=ap.parse_args()
    rows=integrations()
    metadata_path=OUT/'all_pr_metadata_selected.json'
    metadata=json.loads(metadata_path.read_text())['rows'] if metadata_path.exists() else []
    for r in rows:
        prmeta=next((m for m in metadata if m.get('repository')==r['repository'] and m.get('merge_commit_sha')==r['sha']),None)
        if prmeta:
            r['pr']=prmeta['pr']
            r['title']=prmeta['title']
            r['pr_url']=prmeta.get('url')
            r['pr_live_merged']=prmeta.get('merged')
            r['pr_selected_declarations']=prmeta.get('selected_declarations',[])
            r['pr_mentioned_declarations']=prmeta.get('declaration_tokens',[])
    classifications=json.loads(args.classifications.read_text()) if args.classifications.exists() else {}
    for r in rows:
        key=f"{r['repository']}:{r['pr'] if r['pr'] else r['sha'][:7]}"
        r.update(classifications.get(key,{'category':'UNCLASSIFIED','alternative_categories':[],'classification_reason':''}))
    inv,files=static_inventory()
    summary={'end_utc':END.isoformat(),'start_30d_utc':(END-dt.timedelta(days=30)).isoformat(),'start_60d_utc':(END-dt.timedelta(days=60)).isoformat(),'identity':REPOS,'integration_counts':{},'static_inventory':inv,'limitations':['Activity counts and changed lines do not measure labor hours.','Physical and nonblank lines are path-based source size, not semantic scientific effort.','Static test functions are not parametrized collected test cases.','A squash PR is identified from its first-parent commit title; manual merges without PR number remain separately traceable.']}
    for tag in REPOS:
        for days in (30,60):
            subset=[r for r in rows if r['repository']==tag and (days==60 or r['in_30d'])]
            summary['integration_counts'][f'{tag}_{days}d']={'n':len(subset),'kinds':dict(collections.Counter(r['integration_kind'] for r in subset)),'categories':dict(collections.Counter(r['category'] for r in subset)),'category_marginal_bounds':{c:{'min':sum(r['category']==c and not r.get('alternative_categories') for r in subset),'max':sum(r['category']==c or c in r.get('alternative_categories',[]) for r in subset)} for c in CATS},'scientific_subtypes':dict(collections.Counter(r.get('analysis_subtype','unspecified') for r in subset if r['category']=='scientific_analysis')),'mirrored_result_handoffs':sum(r.get('mirrored_result_handoff',False) for r in subset),'mixed':sum(bool(r.get('alternative_categories')) for r in subset),'added':sum(r['added'] for r in subset),'deleted':sum(r['deleted'] for r in subset)}
    for name,data in [('integrations.json',rows),('static_inventory.json',inv),('summary.json',summary)]:
        (OUT/name).write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n')
    flat=[]
    for r in rows:
        flat.append({k:r[k] for k in ['repository','sha','committer_date','in_30d','integration_kind','pr','title','category','classification_reason','added','deleted']}|{'analysis_subtype':r.get('analysis_subtype',''),'mirrored_result_handoff':r.get('mirrored_result_handoff',False),'alternative_categories':';'.join(r.get('alternative_categories',[])),'pr_selected_declarations':';'.join(r.get('pr_selected_declarations',[])),'declaration_tokens':';'.join(sorted({t for d in r['declarations'] for t in d['tokens']})),'paths':';'.join(f['path'] for f in r['files'])})
    for name,data in [('integrations.csv',flat),('code_files.csv',files)]:
        with (OUT/name).open('w',newline='') as f:
            w=csv.DictWriter(f,fieldnames=list(data[0]));w.writeheader();w.writerows(data)
    print(json.dumps({k:v for k,v in summary.items() if k not in {'static_inventory','identity'}},indent=2))
    print('STATIC',json.dumps({tag:{k:v for k,v in s.items() if k not in {'analysis_bundle_names','component_gate_refs','gate_function_names','unregistered_gate_function_names'}} for tag,s in inv.items()},indent=2))

if __name__=='__main__': main()
```

</details>


#### review_work/census/render_tables.py

SHA-256 `296ac3d5b2e38be0a0ee1b4c638d2008f707a4beee110911556aa43d2d357806`.

<details>
<summary>Show complete Python source — review_work/census/render_tables.py</summary>

```python
#!/usr/bin/env python3
"""Render complete integration classification table from frozen census JSON.

This is a presentation reducer; it does not reclassify changes. The table groups
paths for readability. Full exact changed-path lists remain in integrations.json
and integrations.csv, with all-file numstats and classification rationale.
"""
import collections
import datetime as dt
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
rows = json.loads((HERE / 'integrations.json').read_text())
labels = {
    'governing_physics': 'Physics',
    'numerical_methods': 'Numerics',
    'scientific_analysis': 'Science',
    'assurance_governance': 'Assurance',
    'documentation_status': 'Docs/status',
    'product_ui': 'Product/UI',
}
subtypes = {
    'retained-output only': 'Retained only',
    'new scenario evaluation under unchanged equations': 'New evaluation',
    'source/data qualification': 'Source qualification',
}
decls = {
    'NO_GOVERNING_PHYSICS_CHANGE': 'NO-GOV',
    'SOURCE_SCENARIO_CHANGE_ONLY': 'SCENARIO',
    'NUMERICAL_METHOD_CHANGE': 'NUMERICAL',
    'GOVERNING_PHYSICS_CHANGE': 'GOV',
    'GEOMETRY_COMPATIBILITY_NO_GOVERNING_PHYSICS_CHANGE': 'GEOMETRY/NO-GOV',
}

def esc(s):
    return str(s).replace('|', '\\|').replace('\n', ' ')

def path_group(path):
    parts = path.split('/')
    if path.startswith(('docs/analysis/', 'puckworks/models/', 'puckworks/analysis/', 'tools/')) and len(parts) > 3:
        return '/'.join(parts[:3]) + '/'
    if len(parts) > 2:
        return '/'.join(parts[:2]) + '/'
    if len(parts) > 1:
        return parts[0] + '/'
    return path

out = ['# Complete first-parent integration classification census', '',
       'Endpoint 2026-10-18T22:06:06Z; 60-day window inclusive from 2026-08-19T22:06:06Z; '
       'a **30** in the window column also places that integration in the 30-day window '
       'from 2026-09-18T22:06:06Z. Dates below are UTC committer dates. M = actual merge; '
       'S = single-parent squash PR. All rows mapped to merged PRs. The complete exact '
       'SHA, paths and per-path numstats, metadata and rationale accompany this table in '
       '`integrations.json` / `integrations.csv`.', '',
       'Labels: Physics = governing-physics change; Numerics = numerical/geometry/solver '
       'capability; Science = scientific analysis/comparison. Its subtypes are retained-output '
       'only, new scenario evaluation under unchanged equations (including newly fitted '
       'empirical models), and source/data qualification. Alternate labels are plausible '
       'primary-purpose classifications, not extra integrations. Mirror marks PW-result '
       'handoffs in EWP, not a second independent study. Declaration abbreviations are '
       'the literal declared change types, with NO-GOV = NO_GOVERNING_PHYSICS_CHANGE; '
       'SCENARIO = SOURCE_SCENARIO_CHANGE_ONLY; NUMERICAL = NUMERICAL_METHOD_CHANGE; '
       'GOV = GOVERNING_PHYSICS_CHANGE; GEOMETRY/NO-GOV = '
       'GEOMETRY_COMPATIBILITY_NO_GOVERNING_PHYSICS_CHANGE. “none found” is absence '
       'from bounded metadata extraction, not proof no declaration exists. '
       '“PR:” means selected PR declaration; “file:” means declaration token observed in '
       'a changed contract/protocol/authority/handoff. File tokens can include predecessor '
       'descriptions and do not automatically describe the current change. Paths show the '
       'three largest changed path groups plus the total exact file count; no count is '
       'a person-hour estimate.', '']
for repo in ('PW', 'EWP'):
    selected = [r for r in rows if r['repository'] == repo]
    out += [f'## {repo}: all {len(selected)} integrations in 60 days', '',
            '| UTC date / window | PR / merge SHA | Title | Primary / scientific subtype | Alternative / mirror | Declaration metadata | Changed path groups |',
            '|---|---|---|---|---|---|---|']
    for r in selected:
        date = dt.datetime.fromisoformat(r['committer_date']).astimezone(dt.timezone.utc).strftime('%Y-%m-%d')
        window = '30+60' if r['in_30d'] else '60'
        kind = 'M' if r['integration_kind'] == 'merge_commit' else 'S'
        pr = f"[#{r['pr']}]({r['pr_url']}) {kind} `{r['sha'][:12]}`"
        category = labels[r['category']]
        if r.get('analysis_subtype'):
            category += ' / ' + subtypes[r['analysis_subtype']]
        alternate = ', '.join(labels[x] for x in r.get('alternative_categories', [])) or '—'
        if r.get('mirrored_result_handoff'):
            alternate += '; mirror'
        pr_d = r.get('pr_selected_declarations', [])
        file_d = sorted({x for f in r.get('declarations', []) for x in f['tokens']} - set(pr_d))
        declaration = ('PR: ' + ', '.join(decls[x] for x in pr_d)) if pr_d else ''
        if file_d:
            declaration += ('; ' if declaration else '') + 'file: ' + ', '.join(decls[x] for x in file_d)
        declaration = declaration or 'none found'
        groups = collections.Counter(path_group(f['path']) for f in r['files'])
        paths = '; '.join(f'`{p}` ({n})' for p,n in sorted(groups.items(), key=lambda t:(-t[1],t[0]))[:3])
        paths += f"; {len(r['files'])} files total"
        out.append('| ' + ' | '.join(esc(x) for x in (f'{date} / {window}', pr, r['title'], category, alternate, declaration, paths)) + ' |')
    out += ['']
(HERE / 'integrations_table.md').write_text('\n'.join(out) + '\n')
print(f'Rendered {len(rows)} integrations into {HERE / "integrations_table.md"}')
```

</details>


#### review_work/report_tables.py

SHA-256 `ead1df68237815737b6e0390c98d3db687abe3ca04c56b23c90adb39197cb786`.

<details>
<summary>Show complete Python source — review_work/report_tables.py</summary>

```python
"""Presentation-only reducers for the one-file review; public aggregates only."""
from pathlib import Path
import collections, hashlib, json, math

ROOT = Path(__file__).resolve().parents[1]
PW = ROOT/'puckworks'
EWP = ROOT/'espresso-whole-pull'
WORK = ROOT/'review_work'

def read(p): return json.loads(p.read_text())
def escape(x): return str(x).replace('|','\\|').replace('\n',' ')
def table(headers, rows):
    return '\n'.join(['| '+' | '.join(headers)+' |', '| '+' | '.join(['---']*len(headers))+' |']+
                     ['| '+' | '.join(escape(v) for v in row)+' |' for row in rows])
def loc(repo,path,a=1,b=None):
    p=(PW if repo=='PW' else EWP)/path
    assert p.is_file(),p
    n=len(p.read_text().splitlines())
    b=b or n
    assert 1<=a<=b<=n,(p,a,b,n)
    return f'`{repo}:{path}:L{a}-L{b}@'+('9dd456b' if repo=='PW' else '4284e94')+'`'
def f(v, digits=6):
    if v is None:return 'unavailable'
    if isinstance(v,str):return v
    return f'{v:.{digits}f}'

def build_parts():
    parts={}
    inv=read(WORK/'census/static_inventory.json')
    rows=[]
    for key,label in [('models','Models/solver'),('analysis','Analysis'),('assurance_governance','Assurance/governance'),('product_ui','Product/UI'),('tests','Tests'),('engineering_tools','Engineering tools'),('other_code','Other code')]:
        vals=[]
        for tag in ('PW','EWP'):
            a=inv[tag]['areas'].get(key,{'files':0,'physical_lines':0,'nonblank_lines':0})
            vals.append(f"{a['files']:,} / {a['physical_lines']:,} / {a['nonblank_lines']:,}")
        rows.append([label,*vals])
    parts['LOC_TABLE']=table(['Area','PW files / physical / nonblank LOC','EWP files / physical / nonblank LOC'],rows)

    parts['EWP_CAPABILITY_FINDING']='''**Claim and evidence [R/D+/C/J, High for implemented mathematics; Medium for physical transfer]:** R0 is an idealized axisymmetric wedge with Darcy flow, a sharp filling front and finite-rate effective-solute transport. Its 9.011661 mm depth is derived from 20 g, assumed solid density 1,400 kg/m³ and porosity 0.4, not measured. There is no energy equation. Post-saturation transport pairs `∂t(φc)+∇·(u c)−∇·(φD∇c)=R` with `∂t M=−R`, where `R=kM max(1−c/Csat,0)` is capped by available inventory. M is mass per bed volume; c is mass per liquid volume. Paired sources have consistent mass units. Release suppression is not a universal discrete concentration bound. The roughly 41 g-at-30-s R0 endpoint is engineering calibration. `EWP:docs/MODEL_SPECIFICATION.md:L24-L144@4284e94`; `EWP:solver/espressoWholePullFoam/espressoWholePullFoam.C:L3213-L3317@4284e94`.

Prescribed flow requires a saturated static Darcy bed, uniform or axially layered; it excludes radial geometry, compaction, machine compliance and evolving permeability. Quasi-static compaction keeps mechanical porosity distinct from transport storage and solves no displacement/deforming mesh. The separate dissolution-indexed K option uses a prescribed dissolved-mass history, not evolved native inventory. Aggregate viscosity requires 90°C, density 965 kg/m³, saturation at time zero, static Darcy, and no indexed species/compaction/evolving K. Bulk mode supports constant-pressure uniform/axial cases; radial histories use local coupling. `EWP:solver/espressoWholePullFoam/espressoWholePullFoam.C:L749-L928@4284e94`, `:L2334-L2365@4284e94`, `:L2589-L2760@4284e94`.

EWP's deliberately retained runtime PW lock is `fc61c4670ec7bf801e40bb391aab16048b8da26b`, 456 commits/109 first-parent commits behind reviewed PW main. CI separately uses `a3428a4d4ad571ef3168a70e8a04620fca5d3520` with `2058d0e947ee9eb92c52d64f6165b810f1fb4732`; individual research consumers bind later producers. These are distinct authority roles, not an automatic integration defect. `EWP:dependencies/puckworks.lock.json:L1-L15@4284e94`; `EWP:.github/workflows/static-validation.yml:L43-L64@4284e94`.

**Counter-evidence:** conservation, analytic oracles and retained mesh/time/MPI studies support bounded numerical use. They do not qualify every option combination or physical transfer. No OpenFOAM trajectory ran here. **Consequence:** profile each supported use separately; retain R0's historical qualification without transferring it to all later modes. **Related:** F-O3-02/03; R-04/R-05.'''

    cap=[]
    def caprow(name,files,claimed,use,rung,profile,why,limit):
        cap.append([name,files,claimed,use,rung,profile+'; '+why,limit])
    caprow('PW Cameron / Guided Pull',loc('PW','puckworks/product/_pull.py',30,110),'Recipe exploration','Conditional source-model sensitivity','Code verification; source reproduction unresolved','1/1/2/1/0/1','1D/isothermal; source closure; independent inventory; limited refinement; no independent validation; scenario sensitivity','Prescribed endpoint, calibrated flux and source ambiguities')
    caprow('PW Pannusch kinetics / histories',loc('PW','docs/cards/pannusch2024.md',22,60),'Temperature/flow/species delivery','Source reconstruction and qualified prescribed-history numerics','Post-fit reconstruction','1/1/2/1/0/1','1D; fitted h/K; conservation/identity; bounded history qualification; exposed targets; limited sensitivity','No native thermal/hydraulic prediction; flow convention unresolved')
    caprow('PW Grudeva reduced',loc('PW','docs/analysis/model_grudeva2026_matched_comparison_008/RESULTS.md'),'Reference-model solution','Analytic/bed verification and matched-code comparison','Code/solution verification','1/1/2/2/0/1','reduced geometry; specified source PDE; analytic oracles; bounded refinement; no experiment; input/source limits','Publication mismatch and #333 incomplete full reference')
    caprow('PW Foster machine/front',loc('PW','docs/analysis/model_foster2025_postsat_001/RESULTS.md'),'Machine/wetting reconstruction','Source ODE port including post-saturation','Source-curve reproduction','1/1/2/1/0/1','ideal geometry; lumped source laws; independent oracle; bounded solve; fitted CT; source sensitivity','Fitted κ/front support, no new campaign')
    caprow('PW hydraulic/material components',loc('PW','puckworks/validation/gates.py',9,78),'Permeability/flow laws','Analytic LB; source-law/adapter reproduction','Verification/reproduction','1/1/2/1/0/1','idealized representation; conditioned constitutive laws; analytic check; limited numerical study; no transferable K validation; input sensitivity','Aggregate collapse and in-rig fitting are not independent transfer')
    caprow('PW empirical mass/chemistry',loc('PW','docs/analysis/sci_md_mass_delivery_006/RESULT.md',11,83),'Conditional later fractions','Measured-mass/early-assay prediction on declared support','Retrospective grouped prediction','1/1/2/2/1/1','aggregate map; phenomenological; integration oracles; bounded intervals; exposed held conditions; finite influence','Validation 1 means partial within-source prediction, not independent campaign')
    caprow('PW streamtube',loc('PW','puckworks/models/__init__.py',497,498),'Heterogeneity/discrimination','Within-campaign held-out response','Within-campaign held-out','1/1/1/1/1/1','ideal channels; candidate mechanisms; partial code/refinement evidence; within-campaign validation; sweeps','No independent campaign or unique mechanism identification')
    caprow('PW packing generator',loc('PW','puckworks/models/__init__.py',497,498),'Synthetic packing/flow capacity','Exploratory mechanism capacity','Qualitative capacity','1/1/1/1/0/1','ideal packing; candidate flow law; partial code/refinement evidence; no physical validation; sweeps','No empirical-validation claim or unique mechanism identification')
    caprow('EWP R0 whole pull',loc('EWP','docs/MODEL_SPECIFICATION.md',24,144),'Idealized whole pull','Calibrated reference and numerical benchmark','Numerically qualified','1/1/2/2/0/1','wedge; simplified wetting/solute; analytic/conservation; bounded mesh/time; no independent validation; assumed-input sweeps','No validation transfer to added modes')
    caprow('EWP Darcy/Forchheimer + machine',loc('EWP','solver/espressoWholePullFoam/espressoWholePullFoam.C',2834,2846)+'; '+loc('EWP','solver/espressoWholePullFoam/forchheimerResistance.H',10,64)+'; '+loc('EWP','solver/espressoWholePullFoam/machineBoundaryModel.H',291,365),'Hydraulic components','Declared static/layered component problems','Code/solution verification','2/1/2/2/0/1','supported geometries; source correlations; analytic reference; component refinement; no physical holdout; sensitivity','Source-specific machine/input mapping')
    caprow('EWP uniform compaction',loc('EWP','solver/espressoWholePullFoam/poroelasticCompaction.H',10,150),'Stress-dependent K','Bounded scalar/component mechanics','Code/solution verification','1/1/2/2/0/1','fixed domain; no displacement; oracle; bounded nonlinear/refinement; wrong pressure response; sensitivity','Cannot generate turnover at fixed admissible parameters')
    caprow('EWP local/bulk/radial rheology',loc('EWP','solver/espressoWholePullFoam/espressoWholePullFoam.C',749,790),'Concentration–mobility coupling','90°C saturated static-Darcy studies','Computational approximation','2/1/2/2/0/1','declared radial geometry; industrial source law; conservative/oracle tests; refinements; no shot-law validation; tested properties','Bulk and local compatibility differ; unscored tails/spatial cuts')
    caprow('EWP indexed species',loc('EWP','solver/espressoWholePullFoam/espressoWholePullFoam.C',3328,3369),'Species delivery under flow','Passive species operator studies','Code verification','1/1/2/1/0/1','fixed geometry; first-order effective laws; paired balances; empirical-use qualification blocked; no chemistry validation; limited sensitivity','MD008 inventory and MD009 surrogate limits')
    parts['CAPABILITY_MATRIX']=table(['Capability','Components/files and locator','Claimed use','Defensible use today','Evidence rung','Six-axis profile and reasons','Key limitation'],cap)

    guide=loc('PW','docs/data/ESPRESSO_DATA_GUIDE.md',431,954)
    ev=[
      ['Pannusch/Schmieder','Mass-window TDS/caffeine/trigonelline/5-CQA','45 FIT +24 PRED shots; one campaign lineage','Public subsets/aggregates; originals external','Between-shot SD; incomplete assay/input propagation','CC-BY-NC-3.0 source data; paper separate','Fitting, model selection and repeated scoring','Matched fraction comparisons; no fresh holdout'],
      ['Waszkiewicz','Pressure, mass, differentiated flow','56 brews /11 pressures; one label alias','Packaged processed traces','Repeated-brew spread; SEM; pressure/systematic uncertainty incomplete','CC-BY-4.0 data; source code license separate','Static/dynamic fits; MD010–012','Sensor/observable-qualified pressure critique'],
      ['Grudeva experiments','Mass/vial solute','13 qualified shots;11 transfer eligible;208 clock vials','Public aggregates; permissioned originals external','Heterogeneous shots; no same-condition assay-repeat estimate','Written permission,14Aug2026; no new redistribution','CLOCK/MASS007/008/stopping','Cross-source conditional use; no fresh cohort'],
      ['Angeloni','11 species, solids/lipids metadata','66 shots per metadata','Protected; metadata only here','Not inspected','Deny policy controls','Prior use/protection; general metadata inconsistent','No semantic use under this review'],
      ['Wadsworth','PSD, porosity, K','22 table rows;21 usable K; aliases deduplicated','Packaged','Source/adapter uncertainty varies','CC-BY-4.0','Closure and prior comparisons','Input-adapter sensitivity, not universal wet-puck K'],
      ['Roman / Vaca','Tamped K, porosity, extraction','Roman triplicate summaries; Vaca9 conditions/50 dry pairs; no common shot total','Packaged tables/thesis extracts','Source SD and geometry qualifications','Roman2015 CC-BY-3.0; thesis/source-specific','Source-law, material and prior tests','Source-specific priors; avoid unmatched row fusion'],
      ['Foster','CT front/headspace; machine response','Independent shot count unknown','Digitizations/derived fixtures','Source error bars plus reading allowances','Source-specific; no new grant inferred','Fitted ODE/CT reproduction','Wetting/observation constraints, no chemistry join'],
      ['Maillé / Smrke','Batch/fraction extraction','Maillé21 materials/105 normalized cells; Smrke33 primary markers, shot IDs unresolved','Packaged summaries; raw replicates absent here','Normalization/marker dependence unresolved','Thesis/article-specific; SmrkeCC-BY-4.0','Transfer/capacity tests','Observer-denominator qualification; do not count cells as shots'],
      ['Khamitova / Liang','Composition versus settings; partition','9×4 source settings /~42 digitized points; no qualified independent-unit total','Packaged summaries','HPLC means/RSD or missing point error','Source-specific','Published/calibrated source relations','Composition/partition constraints with original units'],
      ['Moroney','Drip bed/outlet concentrations','44 deep/28 shallow observations, not independent shots','Digitized source curves','Shared cumulative/fit dependence','Source-specific','Deep calibration and shallow transfer','Observation/model criticism; not espresso validation'],
      ['PocketScience / Visualizer','Radial recovery / machine histories','60 experimental rows /23,169 archive record identities; units not all independent','Permissioned external originals; public aggregates','Handling/observer limits; uncontrolled corpus; user TDS/EY unverified','Permission scope; no raw redistribution','Radial observer and prior empirical/native corpus studies','Specific missing joins/metadata; no broad repeat sweep'],
      ['Rheology properties','μ, K,n, thermal properties','Property table cells; no matched espresso-shot count','Packaged/derived source tables','Source/domain spread, not a universal probability model','Per-table provenance','G10 and rheology coupling/reductions','Constitutive sensitivity; no fresh-shot law validation'],
    ]
    parts['EVIDENCE_MAP']=table(['Family','Observables','Independent units / counted records','Location','Uncertainty','Rights','Consumed/exposed by','Unused potential'],ev)+'\n\nSources: [R/D+] '+guide+'; family routing in AVAILABLE_DATA_REGISTER; current task-specific counts supersede older family summaries. Unrecomputed obscure source counts are [D−]; none drives a new experiment or validation claim.'

    r=read(WORK/'ewp/results.json')
    m10=r['tasks']['sci_md_010']['metrics'];m11=r['tasks']['sci_md_011']['metrics']
    pressure=[]
    for name,key,d in [('B0','HYD_B0_TRAINING_MEAN',m10),('B1','HYD_B1_PRESSURE_QUADRATIC',m10),('E1','HYD_E1_LUMPED_DARCY',m10),('P1','HYD_P1_POROELASTIC_UNIVERSAL_LIMIT',m11)]:
        v=d[key]; src=r['tasks']['sci_md_010' if name in ('B0','B1','E1') else 'sci_md_011']
        pair=src['paired_comparison'] if name in ('E1','P1') else None
        def interval(k):return '['+f(pair[k]['lower'])+', '+f(pair[k]['upper'])+']' if pair else 'comparator'
        pressure.append([name,f(v['mean_condition_rmse_g_s']),f(v['mean_condition_error_g_s']),f(src['high_pressure_direction'][key]['predicted_slope_g_s_bar']),interval('full'),interval('low_pressure')])
    pressure.append(['E2C','full score unavailable','unavailable','incomplete','required comparisons unavailable','required comparisons unavailable'])
    parts['PRESSURE_TABLE']=table(['Arm','R, g/s','B, g/s','High-pressure slope, g/s/bar','Full paired normalized-loss gain interval (dimensionless)','Low-pressure normalized-loss gain interval (dimensionless)'],pressure)

    cmp=[]
    def cr(i,model,obs,data,typ,support,metric,E,u,res,threshold,assess,exposure,source):
        cmp.append([i,model,obs,data,typ,support,metric,E,u,res,threshold,assess,exposure,source])
    cr('M01','Cameron','EY, pp','PublisherFig5; digitizations unavailable','Source reconstruction','Historical20g/40g/5bar','RMSE','7.102391 curve;6.480780 means [S]','No complete u_val','Source mismatch unresolved causally','No adopted practical tolerance','Do not treat as recipe error bars','Exposed',loc('PW','docs/research/ESPRESSO_PROGRAMME_REVIEW_2026-10-01.md',148,157))
    cr('M02','Wadsworth law + adapter','K ratio','Table1;21 rows','Source-law reproduction','All usable K rows','GM ratio; scatter','GM .912698; range .654–1.755','Input/error covariance absent','Aggregate check PASS; physical NA','GM(.7,1.2), curve reproduction','Not pointwise adequacy','Source fitted',loc('PW','puckworks/validation/gates.py',17,24))
    cr('M03','Waszkiewicz PW','Flow, g/s','Same rig11 pressures;9bar time trace','Fit/reconstruction','Static curve; t≥15s','Static parameters; corr/terminal','Pc12.392,Qc1.897; terminal1.886−1.856','No complete u_val','Regression PASS; physical NA','corr>.9, terminal relative<.1','Source role only','Same-rig fits',loc('PW','puckworks/validation/gates.py',44,78))
    cr('M04','Foster','Front/headspace, mm','CT/fitted curves; shot n unknown','Post-fit','8 front/8 headspace points','RMSE; coverage','Fitted RMSE .002/.001;4/8,5/8','max(source error,.5mm), not u_val','Port PASS; independent NA','RMSE<.2mm,≥4 points','Coverage wording overstates','Fitted campaign',loc('PW','puckworks/validation/gates.py',1170,1195))
    cr('M05','EWP010/011 all arms','Flow, g/s','Wasz 56 brews/11 conditions','Retrospective LOCO','endpoint100s; full/low pressure','Mean-condition R; paired gain','All arms in pressure table','Slope-only u_repeat=.013735 g/s/bar; RMSE/gain full u_val unavailable','E1 ranking loss; P1 unresolved gain; E2C incomplete','Paired ranking/sign, no adequacy margin','Preserve sign and adverse panel','Target exposed',loc('EWP','docs/analysis/sci_md_011/RESULT.md',7,26))
    cr('M06','EWP WP03 compaction','Flow/mass, g/s and g','Same 5/9/11 bar source','Source-conditioned native comparison','270 temporal samples/pressure, not independent','RMSE, bias, ordering','Flow R .472/.517/.535; mass B +4.092/+8.584/+9.104 [R]','Source bands only; no full u_val','Wrong endpoint ordering; numerically qualified','Observable ranking/reproduction','Structural warning; not fresh validation','Calibrated/exposed',loc('EWP','docs/wp03/WP03_002_RESULTS.md',50,59)+'; '+loc('EWP','validation/wp03/WP03_002_CORRECTED_COMPARISON.json'))
    cr('M07','Grudeva008/009','Dimensionless fields/events','Numerical references/publication','Code comparison / reproduction','4pairs;72included figure residuals','Max errors versus limits','008 maxutil .215109;009arrival+.120850','Reading .010025 + small refinement, no full figure propagation','008PASS;009 event mismatch','.001 field etc / .025 arrival','Different questions; preserve both','Public source',loc('PW','docs/analysis/model_grudeva2026_publication_reconciliation_009/RESULTS.md',3,25))
    cr('M08','MASS001–003 all arms','TDS, pp','Shared campaign; declared PRED panels','Exposed predictive comparisons','Original conditions/windows','Nested R,B,A, gain','All values in A.5; anchored empirical passes003','No complete assay/input u_val','Historical fails/mixed; no global near-miss verdict','R≤1,A≤.5;gain .1+20%','Research budgets; practical basis absent','Target exposed',loc('PW','docs/analysis/sci_md_mass_delivery_003/RESULT.md',7,59))
    cr('M09','MASS004/005','TDS, pp','Same source; incomplete/fixed-assay scope','Predictor adequacy','Original denominators; qualified lower witnesses','R/A bounds','004C01lower1.603167/1.410845 [R]','Numerical only','Definite scoped failures; not all missing','1/.5 research budgets','Do not drop missing denominators','Exposed',loc('PW','docs/analysis/sci_md_mass_delivery_004/RESULT.md',75,106))
    cr('M10','MASS006–008','TDS, pp','12 primary Pannusch / 11 Grudeva reused','Conditional transfer/adaptation','Measured suffix mass; 110 dependent pairs in 008','R, A, count rules','006 C2 R .480034; 007 A .532635; 008 R .483158','Numerical bounds + finite deletions; missing assay/input','006 PASS; 007 FAIL; 008 adequate/no increment','R≤1, A≤.5; original condition/shot/calibration counts','Scoped utility, no population guarantee','Exposed; early assays',loc('PW','docs/analysis/sci_md_mass_uncertainty_001/RESULTS.md',44,82))
    cr('M10b','MASS stopping decision','Additional solute g; suffix TDS %','Same 11 Grudeva shots','Conditional decision comparison','Original feasible endpoints and sensitivity contracts','Success, false feasibility, abstention, regret','C2/C0/FIXED primary 11/11; all sensitivities in A.5 [R/X]','Public counts checked; private oracle/regret not replayed','All primary rules succeed; no incremental C2 value','Additional solute≥.100 g AND suffix TDS≥2.0%; decision-count limits','Application-specific, distinct from prediction budgets','Exposed; measured mass and conditioned predictors',loc('PW','docs/analysis/sci_md_mass_stop_decision_001/PROTOCOL.md',45,51)+'; '+loc('PW','docs/analysis/sci_md_mass_stop_decision_001/PROTOCOL.md',136,149))
    cr('M11','Caffeine D0/S0/S1/S2','mg/g','12primary,6temperature,6flow shots','Conditional chemistry','48/24/23of24windows','NestedR,B,A;pairedgain','S2R.125168;B−.056349','Numerical + deletion sensitivity; no full u_val','All primary adequate; complexity FAIL','R≤.50,A≤.25;gain≥.10AND15%','No practical basis demonstrated','Exposed',loc('PW','docs/analysis/sci_md_caffeine_delivery_001/RESULT.md',7,43))
    cr('M12','5CQA delivery/TDS/assay arms','mg/g','Same PRED lineage','Conditional chemistry','Same original/partial supports','R,B,A;decomposed gains','L12R.297495;A.254372;B−.254372','Numerical + finite sensitivity; no full u_val','All current primary arms inadequate','R≤.25,A≤.125;gain≥.05AND15%','Bias failure is substantial; no offset inference','Exposed/extrapolated',loc('PW','docs/analysis/sci_md_5cqa_assay_002/RESULTS.md',21,78))
    cr('M13','Trigonelline K0/D0','mg/g','Same12primary source shots','Mass-shape predictive comparison','Declared assayed windows','R,B;pairedgain','D0R.134550;B−.026655;gain.594953','Computational allowances, no full u_val','Positive original mass-shape result','R≤.25,A≤.125;gain≥.05AND15%','Named conditional gain, not kinetics','Exposed',loc('PW','docs/analysis/sci_md_trigonelline_delivery_001/RESULT.md',9,52))
    cr('M14','Grudeva CLOCK','Vial solute, g','13 shots; 208 regular vials = 180 positive-mass chemistry + 26 structural zeros + 2 chemistry gaps','Grouped retrospective prediction','Measured masses; terminal excluded','Mean vial RMSE; adequate-shot count','MASS/MIXED .01653832 (11/13 each); TIME .04307544 (3/13); TEMPLATE .04408708 (2/13) [R]','Raw/covariance unavailable','Conditional mass benefit; MIXED no increment','Shot RMSE≤.05 g AND max cumulative error≤.20 g in≥10/13 shots','Actual conditional utility; not flow prediction','Exposed',loc('EWP','docs/analysis/sci_md_grudeva_clock_001/RESULT.md',15,78)+'; '+loc('PW','docs/analysis/sci_md_grudeva_clock_001/PROTOCOL.md',154,164))
    cr('M15','Rheology007–011','TDS pp, allocation, flow fractions','Computational C reference; no shots','Approximation/arrangement','Declared finite-mass support/tails excluded','Max deviations + additive variants','010: 24 PASS; 8 secondary above budget, 2 precision failures','Finite numerical envelope only','Approximation useful; spatial/tail limits','TDS .10 pp; shares 1/2 pp; flow/path .01/.02 fractions; u≤.2 budget','Appropriate distinct metric-specific roles','No empirical validation',loc('PW','docs/analysis/val_case_rheology_decision_resolution_001/RESULTS.md',62,174))
    cr('M16','Maillé/Moroney/Smrke/Radial','Source-specific observables','Source families in evidence map','Transfer/observer qualification','Declared masks/calibration/normalization','Family-specific;see retained bundles','Observer unresolved / calibrationFAIL / negative gains / nonunique radial state','Source-dependent; no pooled u_val','Preserve distinct stopped/negative claims','Family contracts, no shared noise floor','No universal theory rejection','Exposed',loc('PW','docs/analysis/sci_md_smrke_transfer_001/RESULT.md'))
    parts['MODEL_COMPARISONS']=table(['ID','Model/capability','Observable/units','Data/units','Comparison type','Scored support','Metric','E or discrepancy','u_val/components','Resolution','Threshold/role/basis','Assessment','Exposure','Locator'],cmp)

    tr=[]
    def th(i,gate,obs,role,threshold,basis,achieved,resolution,assessment,consequence,path,a,b):
        tr.append([i,gate,obs,role,threshold,basis,achieved,resolution,assessment,consequence,loc('PW',path,a,b)])
    th('T-A01','Cameron gate','EY identity at GS1.9','Conservation regression','abs gap<.5pp','“Self-contained mass-budget gate”','GS1.1 diagnostic gap−1.67e−13pp','Numerical invariant','Too loose; existing tests stronger','Reuse off-knot independent inventory','puckworks/validation/gates.py',363,376)
    th('T-A02','Wadsworth collapse','21 K ratios','Source mean-log reproduction','.7<GM<1.2','“reproduces from their own Table 1”','GM.912698;5outside±30%','Mean check only','Role-confused if treated pointwise','Report scatter/exposure','puckworks/validation/gates.py',17,24)
    th('T-A03','Infiltration','DE1 first drip','In-sample compatibility','Porosity bracket','“Parameter-free first-drip prediction”','6.4<7.018<7.8s; fittedκ','Not independent','Role-confused wording','Align with existing evidence label','puckworks/validation/gates.py',26,42)
    th('T-A04','FosterCT','Fitted curves/CT points','Port + post-fit coverage','<.2mm;≥4points;floor.5mm','“line width”','RMSE.002/.001;coverage4/8,5/8','Finite source allowance','Floor/majority wording needs qualification','Do not call independently validated','puckworks/validation/gates.py',1170,1195)
    th('T-A05','LB / Roman sphere','Analytical solution','Code verification','<.5%;sphere<.001','“exact plane-Poiseuille solution”','LB.052%;sphere.000120','Analytic comparison','Appropriate bounded role','Keep simple analytic controls','puckworks/validation/gates.py',9,15)
    th('T-A06','RomanMPE','Reported source MPE','Transcription regression','15 rows; medium-MW max≤14.5%; its mean below low/high-MW means','“~+/-0.5 pp raster fidelity”','Medium-MW maximum 14.3%; mean 10.9%','Source table read','Role-confused as new prediction','Label reported-source statistics','puckworks/validation/gates.py',859,881)
    th('T-A07','G10bulk','One Cameron liquor field','Scenario sensitivity','μratio<1.15;supp<8%;endfactor>.95','“Fast single-shot bound”','1.043;4.12%;.9897','One source-law scenario','Global safety inference too broad','Keep result; narrow scope','puckworks/validation/gates.py',1481,1498)
    th('T-A08','MASS001–003','Original suffix TDS','Research adequacy/increment','R1,A.5;gain.1AND20%','none stated as practical accuracy','Multiple condition/bias failures;003empiricalPASS','No complete u_val','Practical basis unestablished; no blanket strictness verdict','Finish own-support T04','docs/analysis/sci_md_mass_delivery_003/RESULT.md',7,59)
    th('T-A09','Caffeine','12 primary shots','Research adequacy/increment','R≤.50, A≤.25; gain≥.10 AND≥15%, ≥3/4 definite wins, A deterioration≤.05 (mg/g)','“Predeclared research budgets”','gains .027/.067/.090, all<.10; S1 win count also fails','Numerically definite; deletions finite','Stringent for descriptive gain; not proven too strict for a use','Keep contract and all conjunctions, report gain','docs/analysis/sci_md_caffeine_delivery_001/PROTOCOL.md',69,83)
    th('T-A10','5CQA','12 primary shots','Adequacy + increment','Candidate R≤.25, A≤.125; gain≥.05 AND≥15%, ≥3/4 definite wins, A deterioration≤.025 (mg/g)','“engineering budgets”','L12 R .2975, A .2544; A deterioration vs L1M .038685 exceeds .025','Numerical fail; empirical u incomplete','Near gain misses do not excuse inadequacy or bias deterioration','No automatic offset or adoption','docs/analysis/sci_md_5cqa_assay_002/PROTOCOL.md',156,174)
    th('T-A11','RHEOLOGY010/T05','Finite-mass C comparison','Approximation + precision','TDS .10 pp; shares 1/2 pp; flow/path .01/.02; u≤.2 budget','none stated as experimental accuracy','24 PASS; 2 secondary TDS precision-ineligible (u>.020 pp)','All 8 secondary finite envelopes above their metric budgets','Appropriate separate roles','Retain original labels/useful sensitivity','docs/analysis/val_case_rheology_decision_resolution_001/RESULTS.md',62,174)
    th('T-A12','Grudeva009','Publication arrival/profile','Source reproduction','.025arrival;.015concentration','none stated as physical accuracy','arrival+.120850;readbound.010025','Event mismatch;horizontal propagation incomplete','Do not rebrand as physical adequacy','Source/observer crosswalk','docs/analysis/model_grudeva2026_publication_reconciliation_009/RESULTS.md',3,25)
    th('T-A13','MASS006–008','Declared condition, shot or calibration support','Research adequacy/increment','R≤1, A≤.5 pp; increments≥.10 pp AND≥15%; A deterioration≤.10 pp; exact distinct count/noninferiority rules in A.6','“task working budgets”','006 earned; 007 7/11 adequate; 008 A2 adequate, every increment fails a conjunction','Numerical decisions definite; finite dependent-shot sensitivity','No replacement by MASS001–003 20% rule or independent-binomial inference','Preserve every original axis and comparator','docs/analysis/sci_md_mass_delivery_008/PROTOCOL.md',48,73)
    parts['THRESHOLD_TABLE']=table(['ID','Gate/task','Observable/support','Role','Threshold','Stated basis','Achieved','Resolution','Assessment','Consequence','Locator'],tr)
    return parts

if __name__=='__main__':
    p=build_parts()
    (WORK/'report_parts.json').write_text(json.dumps(p,indent=2)+'\n')
    print('parts',len(p))
```

</details>


<a id="appendix-b-3"></a>

### B.3 Selected live PR declaration metadata required by the census



Save the following JSON as `review_work/census/all_pr_metadata_selected.json`. It contains exactly the fields used by the extraction script, omitting irrelevant personal/repository metadata. The full changed paths, numstats and commit identities are reproduced from the pinned Git trees by `build_census.py`; manual classifications and alternatives are completely specified by `make_classifications.py`.

<details>
<summary>Show complete 128-record reproduction input — B.3 Selected live PR declaration metadata required by the census</summary>

```json
{
  "fetched_at_utc": "2026-10-18 22:17:58 UTC",
  "source": "GitHub get_pr_info; no body/source/target content retained; enum declaration metadata only; selected_declarations use checked boxes where several declaration tokens appear, otherwise sole mentioned token",
  "rows": [
    {
      "repository": "PW",
      "pr": 340,
      "url": "https://github.com/trbrewer/puckworks/pull/340",
      "title": "T04: retain 5-CQA gain sensitivity and RMSE decomposition",
      "merged": true,
      "merge_commit_sha": "9dd456be7fd797b9cda0a2bbf50d1ac717d72835",
      "selected_declarations": [
        "NO_GOVERNING_PHYSICS_CHANGE"
      ],
      "declaration_tokens": [
        "NO_GOVERNING_PHYSICS_CHANGE"
      ]
    },
    {
      "repository": "PW",
      "pr": 339,
      "url": "https://github.com/trbrewer/puckworks/pull/339",
      "title": "VAL-CASE-CAFFEINE-001: persistent primary gains, conditional stress benefit",
      "merged": true,
      "merge_commit_sha": "43ec258c3db49ff76cfb89e0ea27bc55ad8d2bae",
      "selected_declarations": [
        "NO_GOVERNING_PHYSICS_CHANGE"
      ],
      "declaration_tokens": [
        "NO_GOVERNING_PHYSICS_CHANGE"
      ]
    },
    {
      "repository": "PW",
      "pr": 338,
      "url": "https://github.com/trbrewer/puckworks/pull/338",
      "title": "VAL-CASE-RHEOLOGY-DECISION-RESOLUTION-001: preserve contracts and report numerical sensitivity",
      "merged": true,
      "merge_commit_sha": "79852f11073ef92041edff5ae0e951603084c706",
      "selected_declarations": [
        "NO_GOVERNING_PHYSICS_CHANGE"
      ],
      "declaration_tokens": [
        "NO_GOVERNING_PHYSICS_CHANGE"
      ]
    },
    {
      "repository": "PW",
      "pr": 335,
      "url": "https://github.com/trbrewer/puckworks/pull/335",
      "title": "VAL-INFRA-DECISION-RESOLUTION-001: prospective policy and synthetic evaluator",
      "merged": true,
      "merge_commit_sha": "882584d110e1356091435ab8b002fb9abdd35ad6",
      "selected_declarations": [
        "NO_GOVERNING_PHYSICS_CHANGE"
      ],
      "declaration_tokens": [
        "NO_GOVERNING_PHYSICS_CHANGE"
      ]
    },
    {
      "repository": "PW",
      "pr": 334,
      "url": "https://github.com/trbrewer/puckworks/pull/334",
      "title": "SCI-MD-MASS-UNCERTAINTY-001: audit retained scores and physical-shot sensitivity",
      "merged": true,
      "merge_commit_sha": "7975fbc39a649cb757702131e2b91b13439c7192",
      "selected_declarations": [
        "NO_GOVERNING_PHYSICS_CHANGE"
      ],
      "declaration_tokens": [
        "NO_GOVERNING_PHYSICS_CHANGE"
      ]
    },
    {
      "repository": "PW",
      "pr": 332,
      "url": "https://github.com/trbrewer/puckworks/pull/332",
      "title": "docs: preserve the October 9 threshold and capability review",
      "merged": true,
      "merge_commit_sha": "3cd308ac5bed39acff3d995108b5178a53c982ee",
      "selected_declarations": [
        "NO_GOVERNING_PHYSICS_CHANGE"
      ],
      "declaration_tokens": [
        "NO_GOVERNING_PHYSICS_CHANGE"
      ]
    },
    {
      "repository": "PW",
      "pr": 331,
      "url": "https://github.com/trbrewer/puckworks/pull/331",
      "title": "MODEL-GRUDEVA2026-009: qualified methods corroborate publication discrepancies",
      "merged": true,
      "merge_commit_sha": "3afe04dc9e0e0d1537bebe5220eb42d48ef7becd",
      "selected_declarations": [
        "NO_GOVERNING_PHYSICS_CHANGE"
      ],
      "declaration_tokens": [
        "NO_GOVERNING_PHYSICS_CHANGE"
      ]
    },
    {
      "repository": "PW",
      "pr": 330,
      "url": "https://github.com/trbrewer/puckworks/pull/330",
      "title": "MODEL-GRUDEVA2026-MATCHED-COMPARISON-008: compare retained qualified baselines",
      "merged": true,
      "merge_commit_sha": "ab28bd1d20b4fec43d6023a15bc628ee9f0bebcc",
      "selected_declarations": [
        "NO_GOVERNING_PHYSICS_CHANGE"
      ],
      "declaration_tokens": [
        "NO_GOVERNING_PHYSICS_CHANGE"
      ]
    },
    {
      "repository": "PW",
      "pr": 329,
      "url": "https://github.com/trbrewer/puckworks/pull/329",
      "title": "0.4: complete Grudeva fine-baseline qualification 007",
      "merged": true,
      "merge_commit_sha": "37f62d80ce972141b515b48c893244780e6dd097",
      "selected_declarations": [
        "NO_GOVERNING_PHYSICS_CHANGE"
      ],
      "declaration_tokens": [
        "NO_GOVERNING_PHYSICS_CHANGE"
      ]
    },
    {
      "repository": "PW",
      "pr": 328,
      "url": "https://github.com/trbrewer/puckworks/pull/328",
      "title": "67: bounded 512-cell spatial assessment passes declared gates (006)",
      "merged": true,
      "merge_commit_sha": "751d5de1badf287f28de811f511ac1a49acda157",
      "selected_declarations": [
        "NO_GOVERNING_PHYSICS_CHANGE"
      ],
      "declaration_tokens": [
        "NO_GOVERNING_PHYSICS_CHANGE"
      ]
    },
    {
      "repository": "PW",
      "pr": 327,
      "url": "https://github.com/trbrewer/puckworks/pull/327",
      "title": "67: Grudeva2026 baseline observation 005 — single-axis diagnosis, qualification incomplete",
      "merged": true,
      "merge_commit_sha": "5e07a1992c404cb5e605757c1125e5866f326378",
      "selected_declarations": [
        "NO_GOVERNING_PHYSICS_CHANGE"
      ],
      "declaration_tokens": [
        "NO_GOVERNING_PHYSICS_CHANGE"
      ]
    },
    {
      "repository": "PW",
      "pr": 326,
      "url": "https://github.com/trbrewer/puckworks/pull/326",
      "title": "1.7b: qualify Grudeva bed-accuracy comparator (#67)",
      "merged": true,
      "merge_commit_sha": "45f594b92e6bed01f254158fa002ef82519fd5a6",
      "selected_declarations": [
        "NUMERICAL_METHOD_CHANGE"
      ],
      "declaration_tokens": [
        "NUMERICAL_METHOD_CHANGE"
      ]
    },
    {
      "repository": "PW",
      "pr": 325,
      "url": "https://github.com/trbrewer/puckworks/pull/325",
      "title": "MODEL-PANNUSCH2024-FLOW-CONSISTENT-OBSERVATION-001: qualify opt-in volume-clock observer",
      "merged": true,
      "merge_commit_sha": "4536775551c4ebd20a339e5143940532894d0d40",
      "selected_declarations": [
        "NUMERICAL_METHOD_CHANGE"
      ],
      "declaration_tokens": [
        "NUMERICAL_METHOD_CHANGE"
      ]
    },
    {
      "repository": "PW",
      "pr": 324,
      "url": "https://github.com/trbrewer/puckworks/pull/324",
      "title": "PV-19A: disclose Guided Pull pressure and evidence limits",
      "merged": true,
      "merge_commit_sha": "b9ad38c6ebfe96d90462254dfb664dd789036b31",
      "selected_declarations": [],
      "declaration_tokens": []
    },
    {
      "repository": "PW",
      "pr": 322,
      "url": "https://github.com/trbrewer/puckworks/pull/322",
      "title": "ESPRESSO-DEVELOPMENT-GUIDE-001: explain PW/EWP capabilities, evidence and next decisions",
      "merged": true,
      "merge_commit_sha": "149aebfb80539a2e0533d28134c8ef6f253e7d7d",
      "selected_declarations": [
        "NO_GOVERNING_PHYSICS_CHANGE"
      ],
      "declaration_tokens": [
        "NO_GOVERNING_PHYSICS_CHANGE"
      ]
    },
    {
      "repository": "PW",
      "pr": 323,
      "url": "https://github.com/trbrewer/puckworks/pull/323",
      "title": "ci: bound unchanged quality coverage job at 45 minutes",
      "merged": true,
      "merge_commit_sha": "501fa069e2e524053d50e926e7298a9f213dd4e4",
      "selected_declarations": [
        "NO_GOVERNING_PHYSICS_CHANGE"
      ],
      "declaration_tokens": [
        "NO_GOVERNING_PHYSICS_CHANGE"
      ]
    },
    {
      "repository": "PW",
      "pr": 320,
      "url": "https://github.com/trbrewer/puckworks/pull/320",
      "title": "Add prefix-conditioned finite-fraction delivery bounds (006)",
      "merged": true,
      "merge_commit_sha": "f08677b177d9569068941cbb602c7b88f3aca769",
      "selected_declarations": [
        "NO_GOVERNING_PHYSICS_CHANGE"
      ],
      "declaration_tokens": [
        "NO_GOVERNING_PHYSICS_CHANGE"
      ]
    },
    {
      "repository": "PW",
      "pr": 319,
      "url": "https://github.com/trbrewer/puckworks/pull/319",
      "title": "MODEL-PANNUSCH2024-STATE-ENVELOPE-005: bound shared-state FV delivery",
      "merged": true,
      "merge_commit_sha": "4f652dee3a43e9e97dc555173cb469d424cdc69a",
      "selected_declarations": [
        "NO_GOVERNING_PHYSICS_CHANGE"
      ],
      "declaration_tokens": [
        "NO_GOVERNING_PHYSICS_CHANGE"
      ]
    },
    {
      "repository": "PW",
      "pr": 318,
      "url": "https://github.com/trbrewer/puckworks/pull/318",
      "title": "004: add explicit FV chemical states and checked continuation",
      "merged": true,
      "merge_commit_sha": "28c32df8ed996043f943b777e9312016e8b5ce05",
      "selected_declarations": [
        "NUMERICAL_METHOD_CHANGE"
      ],
      "declaration_tokens": [
        "NUMERICAL_METHOD_CHANGE"
      ]
    },
    {
      "repository": "PW",
      "pr": 317,
      "url": "https://github.com/trbrewer/puckworks/pull/317",
      "title": "MODEL-PANNUSCH2024-FLOW-TEMP-FV-003: prescribed flow and temperature FV research API",
      "merged": true,
      "merge_commit_sha": "58b6cd2f29af3fa4372119ba59f8a6a1446369cc",
      "selected_declarations": [
        "NUMERICAL_METHOD_CHANGE"
      ],
      "declaration_tokens": [
        "NUMERICAL_METHOD_CHANGE"
      ]
    },
    {
      "repository": "PW",
      "pr": 315,
      "url": "https://github.com/trbrewer/puckworks/pull/315",
      "title": "MODEL-PANNUSCH2024-POSITIVE-FV-002: conservative positive FV research backend (stacked)",
      "merged": true,
      "merge_commit_sha": "1d780b7fb57df4693e22e564010c891602df119d",
      "selected_declarations": [
        "NUMERICAL_METHOD_CHANGE"
      ],
      "declaration_tokens": [
        "NUMERICAL_METHOD_CHANGE"
      ]
    },
    {
      "repository": "PW",
      "pr": 314,
      "url": "https://github.com/trbrewer/puckworks/pull/314",
      "title": "MODEL-PANNUSCH2024-TEMP-HISTORY-001: prescribed temperature API; qualification incomplete",
      "merged": true,
      "merge_commit_sha": "1e9f85a5e42d206baf05a0a95aa81847d506c9d5",
      "selected_declarations": [
        "NUMERICAL_METHOD_CHANGE"
      ],
      "declaration_tokens": [
        "NUMERICAL_METHOD_CHANGE"
      ]
    },
    {
      "repository": "PW",
      "pr": 312,
      "url": "https://github.com/trbrewer/puckworks/pull/312",
      "title": "1.6: complete Foster post-saturation headspace and water accounting",
      "merged": true,
      "merge_commit_sha": "95f6b54f1f00fda100fad9c994ac99037e50f801",
      "selected_declarations": [
        "GOVERNING_PHYSICS_CHANGE"
      ],
      "declaration_tokens": [
        "GOVERNING_PHYSICS_CHANGE"
      ]
    },
    {
      "repository": "PW",
      "pr": 310,
      "url": "https://github.com/trbrewer/puckworks/pull/310",
      "title": "MODEL-GRUDEVA2026-CONSERVATIVE-003: conservative repair, coupled qualification incomplete",
      "merged": true,
      "merge_commit_sha": "5745f615637dbfe95065b48339c3fe566fa58d66",
      "selected_declarations": [
        "NUMERICAL_METHOD_CHANGE"
      ],
      "declaration_tokens": [
        "NUMERICAL_METHOD_CHANGE"
      ]
    },
    {
      "repository": "PW",
      "pr": 309,
      "url": "https://github.com/trbrewer/puckworks/pull/309",
      "title": "MODEL-GRUDEVA2026-REFERENCE-002: bounded comparator qualification incomplete",
      "merged": true,
      "merge_commit_sha": "73b55cf807051b3ce2a0740bdb768f821f002668",
      "selected_declarations": [
        "NUMERICAL_METHOD_CHANGE"
      ],
      "declaration_tokens": [
        "NUMERICAL_METHOD_CHANGE"
      ]
    },
    {
      "repository": "PW",
      "pr": 308,
      "url": "https://github.com/trbrewer/puckworks/pull/308",
      "title": "Add independently derived Grudeva EJAM reduced solver and native reference runner",
      "merged": true,
      "merge_commit_sha": "8f5607799ff08ced4524b58aef653b8760a448d9",
      "selected_declarations": [
        "NO_GOVERNING_PHYSICS_CHANGE"
      ],
      "declaration_tokens": [
        "NO_GOVERNING_PHYSICS_CHANGE"
      ]
    },
    {
      "repository": "PW",
      "pr": 307,
      "url": "https://github.com/trbrewer/puckworks/pull/307",
      "title": "SCI-MD-MASS-STOP-DECISION-001: record adequate observed-boundary replay",
      "merged": true,
      "merge_commit_sha": "ca663733c0cd1d171899e137a7256ab29e857f35",
      "selected_declarations": [
        "NO_GOVERNING_PHYSICS_CHANGE"
      ],
      "declaration_tokens": [
        "NO_GOVERNING_PHYSICS_CHANGE"
      ]
    },
    {
      "repository": "PW",
      "pr": 305,
      "url": "https://github.com/trbrewer/puckworks/pull/305",
      "title": "docs: preserve espresso review, source execution and mass-budget findings",
      "merged": true,
      "merge_commit_sha": "54edb7683154bec005c586279b87606aa0427530",
      "selected_declarations": [
        "NO_GOVERNING_PHYSICS_CHANGE"
      ],
      "declaration_tokens": [
        "NO_GOVERNING_PHYSICS_CHANGE"
      ]
    },
    {
      "repository": "PW",
      "pr": 304,
      "url": "https://github.com/trbrewer/puckworks/pull/304",
      "title": "Fix Cameron inventory accounting and audit evidence bindings",
      "merged": true,
      "merge_commit_sha": "15479363ab3bcd879364628a1938879f2db8c05c",
      "selected_declarations": [
        "NUMERICAL_METHOD_CHANGE"
      ],
      "declaration_tokens": [
        "NO_GOVERNING_PHYSICS_CHANGE",
        "NUMERICAL_METHOD_CHANGE"
      ]
    },
    {
      "repository": "PW",
      "pr": 303,
      "url": "https://github.com/trbrewer/puckworks/pull/303",
      "title": "MODEL-ENG-ROBUST-MASS-STOP-001: continuous assay-robust stopping enclosures",
      "merged": true,
      "merge_commit_sha": "713c3c229568bb189c548f4c8a490b69a6319bef",
      "selected_declarations": [
        "NO_GOVERNING_PHYSICS_CHANGE"
      ],
      "declaration_tokens": [
        "NO_GOVERNING_PHYSICS_CHANGE"
      ]
    },
    {
      "repository": "PW",
      "pr": 302,
      "url": "https://github.com/trbrewer/puckworks/pull/302",
      "title": "MODEL-ENG-ASSAY-ENVELOPE-001: bounded-assay delivery envelopes",
      "merged": true,
      "merge_commit_sha": "8fa96fc3fd993264af1dfadc2942327133fe80db",
      "selected_declarations": [
        "NO_GOVERNING_PHYSICS_CHANGE"
      ],
      "declaration_tokens": [
        "NO_GOVERNING_PHYSICS_CHANGE"
      ]
    },
    {
      "repository": "PW",
      "pr": 301,
      "url": "https://github.com/trbrewer/puckworks/pull/301",
      "title": "MODEL-ENG-MASS-STOP-001: add complete inverse stopping-mass queries",
      "merged": true,
      "merge_commit_sha": "e33153b22036e2900bfd35873bba0808b245cb2e",
      "selected_declarations": [
        "NO_GOVERNING_PHYSICS_CHANGE"
      ],
      "declaration_tokens": [
        "NO_GOVERNING_PHYSICS_CHANGE"
      ]
    },
    {
      "repository": "PW",
      "pr": 300,
      "url": "https://github.com/trbrewer/puckworks/pull/300",
      "title": "SCI-MD-5CQA-ASSAY-002: matched early-assay families fail primary adequacy",
      "merged": true,
      "merge_commit_sha": "d9924186a0daceacd083e1d3f2edcc9749d85d2d",
      "selected_declarations": [
        "NO_GOVERNING_PHYSICS_CHANGE"
      ],
      "declaration_tokens": [
        "NO_GOVERNING_PHYSICS_CHANGE"
      ]
    },
    {
      "repository": "PW",
      "pr": 299,
      "url": "https://github.com/trbrewer/puckworks/pull/299",
      "title": "SCI-MD-5CQA-ASSAY-001: first-assay families fail primary adequacy",
      "merged": true,
      "merge_commit_sha": "e6567a392e6d0c340cad71cbe744100b515e0e31",
      "selected_declarations": [
        "NO_GOVERNING_PHYSICS_CHANGE"
      ],
      "declaration_tokens": [
        "NO_GOVERNING_PHYSICS_CHANGE"
      ]
    },
    {
      "repository": "PW",
      "pr": 298,
      "url": "https://github.com/trbrewer/puckworks/pull/298",
      "title": "SCI-MD-5CQA-TDS-001: close negative early-TDS-conditioned 5-CQA comparison",
      "merged": true,
      "merge_commit_sha": "db6f509d20ea089b6649d9eb9c3270cef8edc7a2",
      "selected_declarations": [
        "NO_GOVERNING_PHYSICS_CHANGE"
      ],
      "declaration_tokens": [
        "NO_GOVERNING_PHYSICS_CHANGE"
      ]
    },
    {
      "repository": "PW",
      "pr": 297,
      "url": "https://github.com/trbrewer/puckworks/pull/297",
      "title": "SCI-MD-5CQA-DELIVERY-001: repair WP6 history and complete negative E0/D0 comparison",
      "merged": true,
      "merge_commit_sha": "7df8db644ad0cfd08866bf91565e3d80445e046c",
      "selected_declarations": [
        "NO_GOVERNING_PHYSICS_CHANGE"
      ],
      "declaration_tokens": [
        "NO_GOVERNING_PHYSICS_CHANGE"
      ]
    },
    {
      "repository": "PW",
      "pr": 296,
      "url": "https://github.com/trbrewer/puckworks/pull/296",
      "title": "SCI-VAL-TAMPED-K-001: consolidated-input adapter fails frozen screen",
      "merged": true,
      "merge_commit_sha": "14c6b0992fc558594d2c8617c79264c066000e47",
      "selected_declarations": [
        "NO_GOVERNING_PHYSICS_CHANGE"
      ],
      "declaration_tokens": [
        "NO_GOVERNING_PHYSICS_CHANGE"
      ]
    },
    {
      "repository": "PW",
      "pr": 295,
      "url": "https://github.com/trbrewer/puckworks/pull/295",
      "title": "SCI-MD-TRIGONELLINE-DELIVERY-001: qualify mass-only prediction on the frozen campaign",
      "merged": true,
      "merge_commit_sha": "baa707d65a01e28999771a237939964ef85bb1d8",
      "selected_declarations": [
        "NO_GOVERNING_PHYSICS_CHANGE"
      ],
      "declaration_tokens": [
        "NO_GOVERNING_PHYSICS_CHANGE"
      ]
    },
    {
      "repository": "PW",
      "pr": 294,
      "url": "https://github.com/trbrewer/puckworks/pull/294",
      "title": "SCI-MD-MASS-DELIVERY-008: adequate one-shot adaptation; increments not earned",
      "merged": true,
      "merge_commit_sha": "a37e3005a2a694971e8220dedae14ed6d2e7c71f",
      "selected_declarations": [
        "NO_GOVERNING_PHYSICS_CHANGE"
      ],
      "declaration_tokens": [
        "NO_GOVERNING_PHYSICS_CHANGE"
      ]
    },
    {
      "repository": "PW",
      "pr": 292,
      "url": "https://github.com/trbrewer/puckworks/pull/292",
      "title": "SCI-MD-MASS-DELIVERY-007: frozen pooled transfer fails adequacy despite earned increments",
      "merged": true,
      "merge_commit_sha": "173d4265e17b7e79f1d8792dc9a49b1c5ef90985",
      "selected_declarations": [
        "NO_GOVERNING_PHYSICS_CHANGE"
      ],
      "declaration_tokens": [
        "NO_GOVERNING_PHYSICS_CHANGE"
      ]
    },
    {
      "repository": "PW",
      "pr": 290,
      "url": "https://github.com/trbrewer/puckworks/pull/290",
      "title": "SCI-MD-CAFFEINE-DELIVERY-001: adequate simpler predictors, no earned complexity",
      "merged": true,
      "merge_commit_sha": "6edc5b827999bd9896f8d8762406a79c97c893ab",
      "selected_declarations": [
        "NO_GOVERNING_PHYSICS_CHANGE"
      ],
      "declaration_tokens": [
        "NO_GOVERNING_PHYSICS_CHANGE"
      ]
    },
    {
      "repository": "PW",
      "pr": 288,
      "url": "https://github.com/trbrewer/puckworks/pull/288",
      "title": "SCI-MD-MASS-DELIVERY-006: learn conditional tail delivery from complete FIT trajectories",
      "merged": true,
      "merge_commit_sha": "5bd2bf8916e7619534787ab04e18b3874fa24880",
      "selected_declarations": [
        "NO_GOVERNING_PHYSICS_CHANGE"
      ],
      "declaration_tokens": [
        "NO_GOVERNING_PHYSICS_CHANGE"
      ]
    },
    {
      "repository": "PW",
      "pr": 286,
      "url": "https://github.com/trbrewer/puckworks/pull/286",
      "title": "SCI-MD-MASS-DELIVERY-005: two-assay predictor and audited inadequacy result",
      "merged": true,
      "merge_commit_sha": "08027c10f25b126b4cfdf8947a699d5058cac2ed",
      "selected_declarations": [
        "NO_GOVERNING_PHYSICS_CHANGE"
      ],
      "declaration_tokens": [
        "NO_GOVERNING_PHYSICS_CHANGE"
      ]
    },
    {
      "repository": "PW",
      "pr": 284,
      "url": "https://github.com/trbrewer/puckworks/pull/284",
      "title": "SCI-MD-MASS-DELIVERY-004: frozen empirical transfer fails C01 adequacy",
      "merged": true,
      "merge_commit_sha": "5cc38629482a1eb40e9b8ee5695d5589b7a65c32",
      "selected_declarations": [
        "NO_GOVERNING_PHYSICS_CHANGE"
      ],
      "declaration_tokens": [
        "NO_GOVERNING_PHYSICS_CHANGE"
      ]
    },
    {
      "repository": "PW",
      "pr": 282,
      "url": "https://github.com/trbrewer/puckworks/pull/282",
      "title": "SCI-MD-MASS-DELIVERY-003: single-anchor delivery implementation and negative result",
      "merged": true,
      "merge_commit_sha": "5bdedcce8d6c704cadf4f73f2979f1f131b7f067",
      "selected_declarations": [
        "NO_GOVERNING_PHYSICS_CHANGE"
      ],
      "declaration_tokens": [
        "NO_GOVERNING_PHYSICS_CHANGE"
      ]
    },
    {
      "repository": "PW",
      "pr": 280,
      "url": "https://github.com/trbrewer/puckworks/pull/280",
      "title": "SCI-MD-MASS-DELIVERY-002: conditioning complexity not earned in source comparison",
      "merged": true,
      "merge_commit_sha": "afe8205ab1f5a39842b14fe302e2979f7faf3d43",
      "selected_declarations": [
        "NO_GOVERNING_PHYSICS_CHANGE"
      ],
      "declaration_tokens": [
        "NO_GOVERNING_PHYSICS_CHANGE"
      ]
    },
    {
      "repository": "PW",
      "pr": 278,
      "url": "https://github.com/trbrewer/puckworks/pull/278",
      "title": "SCI-MD-MASS-DELIVERY-001: add research delivery; campaign adequacy condition-limited",
      "merged": true,
      "merge_commit_sha": "69f9ef3453294709ef575d63b156d9d78c49d2db",
      "selected_declarations": [
        "NO_GOVERNING_PHYSICS_CHANGE"
      ],
      "declaration_tokens": [
        "NO_GOVERNING_PHYSICS_CHANGE"
      ]
    },
    {
      "repository": "PW",
      "pr": 276,
      "url": "https://github.com/trbrewer/puckworks/pull/276",
      "title": "SCI-MD-GRUDEVA-CLOCK-001: held-shot beverage-mass gain",
      "merged": true,
      "merge_commit_sha": "85442cbc6341a872a90769ba5217ca3f375b4c2a",
      "selected_declarations": [
        "NO_GOVERNING_PHYSICS_CHANGE"
      ],
      "declaration_tokens": [
        "NO_GOVERNING_PHYSICS_CHANGE"
      ]
    },
    {
      "repository": "PW",
      "pr": 274,
      "url": "https://github.com/trbrewer/puckworks/pull/274",
      "title": "SCI-MD-MO-TRANSFER-001: conservative reference; source and numerical gates unresolved",
      "merged": true,
      "merge_commit_sha": "09ee96b56220b5db75051efebbb575b9b1cb49d8",
      "selected_declarations": [
        "NUMERICAL_METHOD_CHANGE"
      ],
      "declaration_tokens": [
        "NUMERICAL_METHOD_CHANGE"
      ]
    },
    {
      "repository": "PW",
      "pr": 272,
      "url": "https://github.com/trbrewer/puckworks/pull/272",
      "title": "SCI-MD-MORONEY-TRANSFER-001: execute conservative transfer; calibration inadequate",
      "merged": true,
      "merge_commit_sha": "3ed109d60ffcaaca502345ab56e19b116198934e",
      "selected_declarations": [],
      "declaration_tokens": []
    },
    {
      "repository": "PW",
      "pr": 270,
      "url": "https://github.com/trbrewer/puckworks/pull/270",
      "title": "SCI-MD-MAILLE-TRANSFER-001: audit unresolved replicate normalization",
      "merged": true,
      "merge_commit_sha": "e95d4585aa2dd9ab6eaa9da4f6aa8d311109e5ba",
      "selected_declarations": [
        "NO_GOVERNING_PHYSICS_CHANGE"
      ],
      "declaration_tokens": [
        "NO_GOVERNING_PHYSICS_CHANGE"
      ]
    },
    {
      "repository": "PW",
      "pr": 268,
      "url": "https://github.com/trbrewer/puckworks/pull/268",
      "title": "SCI-MD-SMRKE-TRANSFER-001: test endpoint transfer and incremental fines prediction",
      "merged": true,
      "merge_commit_sha": "1648fa095f1aca133616b8a4bb07dcae569a91d2",
      "selected_declarations": [
        "NO_GOVERNING_PHYSICS_CHANGE"
      ],
      "declaration_tokens": [
        "NO_GOVERNING_PHYSICS_CHANGE"
      ]
    },
    {
      "repository": "PW",
      "pr": 266,
      "url": "https://github.com/trbrewer/puckworks/pull/266",
      "title": "SCI-MD-RADIAL-OBS-001: reconstruct Pocket Science spent-puck assay",
      "merged": true,
      "merge_commit_sha": "e786b7846a19da8fae4f02b52b8a2dbbf8b8abee",
      "selected_declarations": [
        "NO_GOVERNING_PHYSICS_CHANGE"
      ],
      "declaration_tokens": [
        "NO_GOVERNING_PHYSICS_CHANGE"
      ]
    },
    {
      "repository": "PW",
      "pr": 265,
      "url": "https://github.com/trbrewer/puckworks/pull/265",
      "title": "DATA-CORPUS-GUIDE-001: make external espresso evidence discoverable",
      "merged": true,
      "merge_commit_sha": "518fb9c480dbcef475789f48f25843238ff8a9d4",
      "selected_declarations": [
        "NO_GOVERNING_PHYSICS_CHANGE"
      ],
      "declaration_tokens": [
        "NO_GOVERNING_PHYSICS_CHANGE"
      ]
    },
    {
      "repository": "PW",
      "pr": 263,
      "url": "https://github.com/trbrewer/puckworks/pull/263",
      "title": "EWP-RWB-001 reconciliation — gate pressure-bearing provenance and preserve schema-v6 data during enrichment",
      "merged": true,
      "merge_commit_sha": "2058d0e947ee9eb92c52d64f6165b810f1fb4732",
      "selected_declarations": [],
      "declaration_tokens": []
    },
    {
      "repository": "PW",
      "pr": 260,
      "url": "https://github.com/trbrewer/puckworks/pull/260",
      "title": "PANNUSCH-PRIOR-IMPACT-001 — Add enduring available-data register and preflight",
      "merged": true,
      "merge_commit_sha": "7cf18d7bc388f636d9bca98e6e1a1def4bf08cf5",
      "selected_declarations": [],
      "declaration_tokens": []
    },
    {
      "repository": "PW",
      "pr": 259,
      "url": "https://github.com/trbrewer/puckworks/pull/259",
      "title": "PANNUSCH-RAW-REPRO-001 — Source-faithful reconstruction and transfer eligibility",
      "merged": true,
      "merge_commit_sha": "57f7e74eef92aa9d83ae0995f8b6123663b37548",
      "selected_declarations": [
        "NO_GOVERNING_PHYSICS_CHANGE"
      ],
      "declaration_tokens": [
        "NO_GOVERNING_PHYSICS_CHANGE"
      ]
    },
    {
      "repository": "PW",
      "pr": 256,
      "url": "https://github.com/trbrewer/puckworks/pull/256",
      "title": "PW-PUB-001-C1: complete post-merge publishing safeguards",
      "merged": true,
      "merge_commit_sha": "dfe0bdc761574e3327fa96f1d84e8199e156c192",
      "selected_declarations": [],
      "declaration_tokens": []
    },
    {
      "repository": "PW",
      "pr": 255,
      "url": "https://github.com/trbrewer/puckworks/pull/255",
      "title": "PW-PUB-001: implement publishing-system foundation",
      "merged": true,
      "merge_commit_sha": "02b416eab26346060057ff8ab4a87f213f9006bf",
      "selected_declarations": [],
      "declaration_tokens": []
    },
    {
      "repository": "PW",
      "pr": 254,
      "url": "https://github.com/trbrewer/puckworks/pull/254",
      "title": "SCI-ED-002 R2A: qualify the scientifically blocked protocol candidate",
      "merged": true,
      "merge_commit_sha": "a67c5cd6018961d290f9e560b78e95074f7654ef",
      "selected_declarations": [],
      "declaration_tokens": []
    },
    {
      "repository": "PW",
      "pr": 252,
      "url": "https://github.com/trbrewer/puckworks/pull/252",
      "title": "SCI-MD-007: inventory evidence atlas and feasibility screen",
      "merged": true,
      "merge_commit_sha": "9b92333b3dc69d0a28de54568d8c48535cf5aa41",
      "selected_declarations": [],
      "declaration_tokens": []
    },
    {
      "repository": "PW",
      "pr": 251,
      "url": "https://github.com/trbrewer/puckworks/pull/251",
      "title": "SCI-MD-004 Stage E0 R3 — freeze target-blind training bundle with silent QA",
      "merged": true,
      "merge_commit_sha": "5ce003e751aac516b5de3d9ede4e6910627e2b12",
      "selected_declarations": [],
      "declaration_tokens": []
    },
    {
      "repository": "PW",
      "pr": 246,
      "url": "https://github.com/trbrewer/puckworks/pull/246",
      "title": "SCI-MD-004 Stage A — multispecies data contract and protected Angeloni adapter",
      "merged": true,
      "merge_commit_sha": "64b67a39801e4cedff42be2da54d38cb3e416e3e",
      "selected_declarations": [
        "NO_GOVERNING_PHYSICS_CHANGE"
      ],
      "declaration_tokens": [
        "NO_GOVERNING_PHYSICS_CHANGE"
      ]
    },
    {
      "repository": "PW",
      "pr": 244,
      "url": "https://github.com/trbrewer/puckworks/pull/244",
      "title": "science: implement RP-A-001 common-observable response atlas",
      "merged": true,
      "merge_commit_sha": "378e4c8c094bce3599eeadbcb237464d738596e7",
      "selected_declarations": [],
      "declaration_tokens": []
    },
    {
      "repository": "EWP",
      "pr": 204,
      "url": "https://github.com/trbrewer/espresso-whole-pull/pull/204",
      "title": "docs: link the canonical October 9 threshold and capability review",
      "merged": true,
      "merge_commit_sha": "4284e9460c8057053e95de7cfa2fb3590e68e9db",
      "selected_declarations": [
        "NO_GOVERNING_PHYSICS_CHANGE"
      ],
      "declaration_tokens": [
        "GOVERNING_PHYSICS_CHANGE",
        "NO_GOVERNING_PHYSICS_CHANGE",
        "NUMERICAL_METHOD_CHANGE",
        "SOURCE_SCENARIO_CHANGE_ONLY"
      ]
    },
    {
      "repository": "EWP",
      "pr": 202,
      "url": "https://github.com/trbrewer/espresso-whole-pull/pull/202",
      "title": "ESPRESSO-DEVELOPMENT-GUIDE-001: link the canonical PW/EWP development guide",
      "merged": true,
      "merge_commit_sha": "16eec1dda24ebf658965eddcf1a6fffa81903b32",
      "selected_declarations": [
        "NO_GOVERNING_PHYSICS_CHANGE"
      ],
      "declaration_tokens": [
        "GOVERNING_PHYSICS_CHANGE",
        "NO_GOVERNING_PHYSICS_CHANGE",
        "NUMERICAL_METHOD_CHANGE",
        "SOURCE_SCENARIO_CHANGE_ONLY"
      ]
    },
    {
      "repository": "EWP",
      "pr": 201,
      "url": "https://github.com/trbrewer/espresso-whole-pull/pull/201",
      "title": "Clarify R0 geometry, extraction limits and endpoint definitions",
      "merged": true,
      "merge_commit_sha": "73ec476ffe6ac626705ca949e28b32935ddf2992",
      "selected_declarations": [
        "NO_GOVERNING_PHYSICS_CHANGE"
      ],
      "declaration_tokens": [
        "GOVERNING_PHYSICS_CHANGE",
        "NO_GOVERNING_PHYSICS_CHANGE",
        "NUMERICAL_METHOD_CHANGE",
        "SOURCE_SCENARIO_CHANGE_ONLY"
      ]
    },
    {
      "repository": "EWP",
      "pr": 200,
      "url": "https://github.com/trbrewer/espresso-whole-pull/pull/200",
      "title": "SCI-MD-MASS-DELIVERY-008: consume frozen one-shot adaptation result",
      "merged": true,
      "merge_commit_sha": "f15a417cbf3c7528ac734537bb844cab6dc98287",
      "selected_declarations": [
        "NO_GOVERNING_PHYSICS_CHANGE"
      ],
      "declaration_tokens": [
        "NO_GOVERNING_PHYSICS_CHANGE"
      ]
    },
    {
      "repository": "EWP",
      "pr": 198,
      "url": "https://github.com/trbrewer/espresso-whole-pull/pull/198",
      "title": "SCI-MD-MASS-DELIVERY-007: exact consumer and inadequate frozen transfer result",
      "merged": true,
      "merge_commit_sha": "3f5ad6121f37fbad33348e92c65263b13378ef30",
      "selected_declarations": [
        "NO_GOVERNING_PHYSICS_CHANGE"
      ],
      "declaration_tokens": [
        "NO_GOVERNING_PHYSICS_CHANGE"
      ]
    },
    {
      "repository": "EWP",
      "pr": 196,
      "url": "https://github.com/trbrewer/espresso-whole-pull/pull/196",
      "title": "SCI-MD-CAFFEINE-DELIVERY-001: exact research consumer and bounded result",
      "merged": true,
      "merge_commit_sha": "022107a2d9e4d10effe970f5d5989abc188fae3f",
      "selected_declarations": [
        "NO_GOVERNING_PHYSICS_CHANGE"
      ],
      "declaration_tokens": [
        "NO_GOVERNING_PHYSICS_CHANGE"
      ]
    },
    {
      "repository": "EWP",
      "pr": 194,
      "url": "https://github.com/trbrewer/espresso-whole-pull/pull/194",
      "title": "SCI-MD-MASS-DELIVERY-006: exact-pinned learned-tail research consumer",
      "merged": true,
      "merge_commit_sha": "ffb6638e18164dc407c30d24d323a5d828c6b532",
      "selected_declarations": [
        "NO_GOVERNING_PHYSICS_CHANGE"
      ],
      "declaration_tokens": [
        "NO_GOVERNING_PHYSICS_CHANGE"
      ]
    },
    {
      "repository": "EWP",
      "pr": 192,
      "url": "https://github.com/trbrewer/espresso-whole-pull/pull/192",
      "title": "SCI-MD-MASS-DELIVERY-005: isolated consumer and negative research handoff",
      "merged": true,
      "merge_commit_sha": "3f5326443fd1b0c334d1b67208718a0a85e89e27",
      "selected_declarations": [
        "NO_GOVERNING_PHYSICS_CHANGE"
      ],
      "declaration_tokens": [
        "NO_GOVERNING_PHYSICS_CHANGE"
      ]
    },
    {
      "repository": "EWP",
      "pr": 190,
      "url": "https://github.com/trbrewer/espresso-whole-pull/pull/190",
      "title": "SCI-MD-MASS-DELIVERY-004: bind empirical transfer inadequacy",
      "merged": true,
      "merge_commit_sha": "2ea8d05dc91727119dd3163f896d9561127f5e6d",
      "selected_declarations": [
        "NO_GOVERNING_PHYSICS_CHANGE"
      ],
      "declaration_tokens": [
        "NO_GOVERNING_PHYSICS_CHANGE"
      ]
    },
    {
      "repository": "EWP",
      "pr": 188,
      "url": "https://github.com/trbrewer/espresso-whole-pull/pull/188",
      "title": "SCI-MD-MASS-DELIVERY-003: pinned anchored-delivery consumer and negative result",
      "merged": true,
      "merge_commit_sha": "28451ffcc717056e42f05372422f78ac2a671374",
      "selected_declarations": [
        "NO_GOVERNING_PHYSICS_CHANGE"
      ],
      "declaration_tokens": [
        "NO_GOVERNING_PHYSICS_CHANGE"
      ]
    },
    {
      "repository": "EWP",
      "pr": 186,
      "url": "https://github.com/trbrewer/espresso-whole-pull/pull/186",
      "title": "SCI-MD-MASS-DELIVERY-002: pinned consumer and negative conditioning result",
      "merged": true,
      "merge_commit_sha": "0900e9ac065159502efeeb4776b288bba0b302d2",
      "selected_declarations": [
        "NO_GOVERNING_PHYSICS_CHANGE"
      ],
      "declaration_tokens": [
        "NO_GOVERNING_PHYSICS_CHANGE"
      ]
    },
    {
      "repository": "EWP",
      "pr": 184,
      "url": "https://github.com/trbrewer/espresso-whole-pull/pull/184",
      "title": "SCI-MD-MASS-DELIVERY-001: add pinned research consumer and condition-limited result",
      "merged": true,
      "merge_commit_sha": "386cba18c421d4f0944450f412fd055ca2127a19",
      "selected_declarations": [
        "NO_GOVERNING_PHYSICS_CHANGE"
      ],
      "declaration_tokens": [
        "GOVERNING_PHYSICS_CHANGE",
        "NO_GOVERNING_PHYSICS_CHANGE",
        "NUMERICAL_METHOD_CHANGE",
        "SOURCE_SCENARIO_CHANGE_ONLY"
      ]
    },
    {
      "repository": "EWP",
      "pr": 182,
      "url": "https://github.com/trbrewer/espresso-whole-pull/pull/182",
      "title": "SCI-MD-GRUDEVA-CLOCK-001: qualified mass-coordinate research handoff",
      "merged": true,
      "merge_commit_sha": "9b11bafddb2e64c1b5af7c64026d8a5910dee0b7",
      "selected_declarations": [
        "NO_GOVERNING_PHYSICS_CHANGE"
      ],
      "declaration_tokens": [
        "GOVERNING_PHYSICS_CHANGE",
        "NO_GOVERNING_PHYSICS_CHANGE",
        "NUMERICAL_METHOD_CHANGE",
        "SOURCE_SCENARIO_CHANGE_ONLY"
      ]
    },
    {
      "repository": "EWP",
      "pr": 180,
      "url": "https://github.com/trbrewer/espresso-whole-pull/pull/180",
      "title": "SCI-MD-MO-TRANSFER-001: exact unresolved research handoff",
      "merged": true,
      "merge_commit_sha": "064d7a7894127ccc389d8d3a03b66da0a3ada27a",
      "selected_declarations": [
        "NO_GOVERNING_PHYSICS_CHANGE"
      ],
      "declaration_tokens": [
        "NO_GOVERNING_PHYSICS_CHANGE"
      ]
    },
    {
      "repository": "EWP",
      "pr": 178,
      "url": "https://github.com/trbrewer/espresso-whole-pull/pull/178",
      "title": "SCI-MD-MORONEY-TRANSFER-001: consume calibration-inadequate result",
      "merged": true,
      "merge_commit_sha": "51ac2a0bc0d4f083dcbd6f6285c7f32f27d2c6be",
      "selected_declarations": [
        "NO_GOVERNING_PHYSICS_CHANGE"
      ],
      "declaration_tokens": [
        "NO_GOVERNING_PHYSICS_CHANGE"
      ]
    },
    {
      "repository": "EWP",
      "pr": 176,
      "url": "https://github.com/trbrewer/espresso-whole-pull/pull/176",
      "title": "SCI-MD-MAILLE-TRANSFER-001: hand off source-contract block",
      "merged": true,
      "merge_commit_sha": "09cdda7fb4b28229be34915a3371c79229316cee",
      "selected_declarations": [
        "NO_GOVERNING_PHYSICS_CHANGE"
      ],
      "declaration_tokens": [
        "NO_GOVERNING_PHYSICS_CHANGE"
      ]
    },
    {
      "repository": "EWP",
      "pr": 174,
      "url": "https://github.com/trbrewer/espresso-whole-pull/pull/174",
      "title": "SCI-MD-SMRKE-TRANSFER-001: hand off endpoint rejection and no fines gain",
      "merged": true,
      "merge_commit_sha": "3ca164871cb4cdfdd2958f1ef34c6e62a8d8bb35",
      "selected_declarations": [
        "NO_GOVERNING_PHYSICS_CHANGE"
      ],
      "declaration_tokens": [
        "GOVERNING_PHYSICS_CHANGE",
        "NO_GOVERNING_PHYSICS_CHANGE",
        "NUMERICAL_METHOD_CHANGE",
        "SOURCE_SCENARIO_CHANGE_ONLY"
      ]
    },
    {
      "repository": "EWP",
      "pr": 172,
      "url": "https://github.com/trbrewer/espresso-whole-pull/pull/172",
      "title": "SCI-MD-RADIAL-OBS-001: conditional assay diagnostic on retained fields",
      "merged": true,
      "merge_commit_sha": "6a001b54834522554d13b244e5a5509764f15355",
      "selected_declarations": [
        "NO_GOVERNING_PHYSICS_CHANGE"
      ],
      "declaration_tokens": [
        "NO_GOVERNING_PHYSICS_CHANGE"
      ]
    },
    {
      "repository": "EWP",
      "pr": 171,
      "url": "https://github.com/trbrewer/espresso-whole-pull/pull/171",
      "title": "SCI-MD-RHEOLOGY-011: distribution-preserving relocation, qualified delivery null",
      "merged": true,
      "merge_commit_sha": "8353125fac20b1e06709d7dfbcd4e0544d002164",
      "selected_declarations": [
        "GEOMETRY_COMPATIBILITY_NO_GOVERNING_PHYSICS_CHANGE"
      ],
      "declaration_tokens": [
        "GEOMETRY_COMPATIBILITY_NO_GOVERNING_PHYSICS_CHANGE"
      ]
    },
    {
      "repository": "EWP",
      "pr": 169,
      "url": "https://github.com/trbrewer/espresso-whole-pull/pull/169",
      "title": "SCI-MD-RHEOLOGY-010: matched-conductance reversal and E2 transfer",
      "merged": true,
      "merge_commit_sha": "63fd95ec1cdfeffbf184194bf5319bf9a8249c38",
      "selected_declarations": [
        "SOURCE_SCENARIO_CHANGE_ONLY"
      ],
      "declaration_tokens": [
        "SOURCE_SCENARIO_CHANGE_ONLY"
      ]
    },
    {
      "repository": "EWP",
      "pr": 167,
      "url": "https://github.com/trbrewer/espresso-whole-pull/pull/167",
      "title": "DATA-CORPUS-GUIDE-001: connect EWP to the inspected external collection",
      "merged": true,
      "merge_commit_sha": "cba79537e177938b2607c2979344b13acb56a9f2",
      "selected_declarations": [
        "NO_GOVERNING_PHYSICS_CHANGE"
      ],
      "declaration_tokens": [
        "GOVERNING_PHYSICS_CHANGE",
        "NO_GOVERNING_PHYSICS_CHANGE",
        "NUMERICAL_METHOD_CHANGE",
        "SOURCE_SCENARIO_CHANGE_ONLY"
      ]
    },
    {
      "repository": "EWP",
      "pr": 166,
      "url": "https://github.com/trbrewer/espresso-whole-pull/pull/166",
      "title": "SCI-MD-RHEOLOGY-009: qualify pressure-history compatibility and E2 transfer",
      "merged": true,
      "merge_commit_sha": "dd05d3dd8dd8f690941f22e1583acf2026a23955",
      "selected_declarations": [
        "NO_GOVERNING_PHYSICS_CHANGE"
      ],
      "declaration_tokens": [
        "GOVERNING_PHYSICS_CHANGE",
        "NO_GOVERNING_PHYSICS_CHANGE",
        "NUMERICAL_METHOD_CHANGE",
        "SOURCE_SCENARIO_CHANGE_ONLY"
      ]
    },
    {
      "repository": "EWP",
      "pr": 164,
      "url": "https://github.com/trbrewer/espresso-whole-pull/pull/164",
      "title": "SCI-MD-RHEOLOGY-008: E2 passes the communicating radial reduction budgets",
      "merged": true,
      "merge_commit_sha": "3960b4a9c4b05aa3f3cdec1dade33eb16c485d24",
      "selected_declarations": [
        "SOURCE_SCENARIO_CHANGE_ONLY"
      ],
      "declaration_tokens": [
        "SOURCE_SCENARIO_CHANGE_ONLY"
      ]
    },
    {
      "repository": "EWP",
      "pr": 162,
      "url": "https://github.com/trbrewer/espresso-whole-pull/pull/162",
      "title": "SCI-MD-RHEOLOGY-007: test autonomous parallel paths against native radial coupling",
      "merged": true,
      "merge_commit_sha": "7bd046eb1697b7ca0a6869c39098efab6f31f3c7",
      "selected_declarations": [
        "SOURCE_SCENARIO_CHANGE_ONLY"
      ],
      "declaration_tokens": [
        "SOURCE_SCENARIO_CHANGE_ONLY"
      ]
    },
    {
      "repository": "EWP",
      "pr": 160,
      "url": "https://github.com/trbrewer/espresso-whole-pull/pull/160",
      "title": "SCI-MD-RHEOLOGY-006: native radial viscosity coupling and flow allocation",
      "merged": true,
      "merge_commit_sha": "e5b3ef819f9692973f674d5da52511d3b3dad07c",
      "selected_declarations": [
        "GOVERNING_PHYSICS_CHANGE"
      ],
      "declaration_tokens": [
        "GOVERNING_PHYSICS_CHANGE",
        "NO_GOVERNING_PHYSICS_CHANGE"
      ]
    },
    {
      "repository": "EWP",
      "pr": 158,
      "url": "https://github.com/trbrewer/espresso-whole-pull/pull/158",
      "title": "SCI-MD-RHEOLOGY-005: test autonomous bulk-state viscosity against local coupling",
      "merged": true,
      "merge_commit_sha": "db705b644bbc2c3f719690448657e845f2a8f65b",
      "selected_declarations": [
        "GOVERNING_PHYSICS_CHANGE"
      ],
      "declaration_tokens": [
        "GOVERNING_PHYSICS_CHANGE"
      ]
    },
    {
      "repository": "EWP",
      "pr": 156,
      "url": "https://github.com/trbrewer/espresso-whole-pull/pull/156",
      "title": "SCI-MD-RHEOLOGY-004: compare aggregate delivery at matched output",
      "merged": true,
      "merge_commit_sha": "ab29a805217010f8c441047aaa04e6b4adaca3fe",
      "selected_declarations": [
        "SOURCE_SCENARIO_CHANGE_ONLY"
      ],
      "declaration_tokens": [
        "GOVERNING_PHYSICS_CHANGE",
        "NO_GOVERNING_PHYSICS_CHANGE",
        "NUMERICAL_METHOD_CHANGE",
        "SOURCE_SCENARIO_CHANGE_ONLY"
      ]
    },
    {
      "repository": "EWP",
      "pr": 154,
      "url": "https://github.com/trbrewer/espresso-whole-pull/pull/154",
      "title": "SCI-MD-RHEOLOGY-003: test hydraulic result across viscosity laws",
      "merged": true,
      "merge_commit_sha": "2542e2ea3925abcb64a881293b6dc8743e3be056",
      "selected_declarations": [
        "SOURCE_SCENARIO_CHANGE_ONLY"
      ],
      "declaration_tokens": [
        "SOURCE_SCENARIO_CHANGE_ONLY"
      ]
    },
    {
      "repository": "EWP",
      "pr": 152,
      "url": "https://github.com/trbrewer/espresso-whole-pull/pull/152",
      "title": "SCI-MD-RHEOLOGY-002: native aggregate viscosity feedback and bounded result",
      "merged": true,
      "merge_commit_sha": "d40e0e64316d57dd4b685089daf07e3a13a11974",
      "selected_declarations": [
        "GOVERNING_PHYSICS_CHANGE"
      ],
      "declaration_tokens": [
        "GOVERNING_PHYSICS_CHANGE"
      ]
    },
    {
      "repository": "EWP",
      "pr": 150,
      "url": "https://github.com/trbrewer/espresso-whole-pull/pull/150",
      "title": "SCI-MD-RHEOLOGY-001: quantify EWP viscosity state dependence",
      "merged": true,
      "merge_commit_sha": "14fc4c8a4a94ffa54ffafd5c2c99037c1af680b9",
      "selected_declarations": [],
      "declaration_tokens": [
        "NO_GOVERNING_PHYSICS_CHANGE",
        "SOURCE_SCENARIO_CHANGE_ONLY"
      ]
    },
    {
      "repository": "EWP",
      "pr": 148,
      "url": "https://github.com/trbrewer/espresso-whole-pull/pull/148",
      "title": "VIS-EWP-RECORD-001: preserve private Visualizer work record",
      "merged": true,
      "merge_commit_sha": "ac49fe939f9e7fb38ba4eabc95d65e2fa47ee666",
      "selected_declarations": [
        "NO_GOVERNING_PHYSICS_CHANGE"
      ],
      "declaration_tokens": [
        "NO_GOVERNING_PHYSICS_CHANGE"
      ]
    },
    {
      "repository": "EWP",
      "pr": 146,
      "url": "https://github.com/trbrewer/espresso-whole-pull/pull/146",
      "title": "XSV-PRESSURE-001: add native prescribed-pressure history",
      "merged": true,
      "merge_commit_sha": "73e3836f0ecdf14be61f504a5c7c7ae2019a250c",
      "selected_declarations": [
        "NO_GOVERNING_PHYSICS_CHANGE"
      ],
      "declaration_tokens": [
        "NO_GOVERNING_PHYSICS_CHANGE"
      ]
    },
    {
      "repository": "EWP",
      "pr": 144,
      "url": "https://github.com/trbrewer/espresso-whole-pull/pull/144",
      "title": "SCI-MD-012: diagnose and disposition E2C 13-bar root blocker",
      "merged": true,
      "merge_commit_sha": "d4a93971cd7a80c8670b83017e4283e9d34dabf0",
      "selected_declarations": [
        "NO_GOVERNING_PHYSICS_CHANGE"
      ],
      "declaration_tokens": [
        "NO_GOVERNING_PHYSICS_CHANGE"
      ]
    },
    {
      "repository": "EWP",
      "pr": 142,
      "url": "https://github.com/trbrewer/espresso-whole-pull/pull/142",
      "title": "SCI-MD-011: freeze high-pressure poroelastic closure adjudication",
      "merged": true,
      "merge_commit_sha": "6451cfe04ff10bd9c4ec706ccafc895619cf9851",
      "selected_declarations": [
        "NO_GOVERNING_PHYSICS_CHANGE"
      ],
      "declaration_tokens": [
        "NO_GOVERNING_PHYSICS_CHANGE"
      ]
    },
    {
      "repository": "EWP",
      "pr": 140,
      "url": "https://github.com/trbrewer/espresso-whole-pull/pull/140",
      "title": "SCI-MD-010 — Observable-first model utility and architecture audit",
      "merged": true,
      "merge_commit_sha": "375b19b96096cf1d9681ab26efec7ed02b87dd09",
      "selected_declarations": [],
      "declaration_tokens": []
    },
    {
      "repository": "EWP",
      "pr": 138,
      "url": "https://github.com/trbrewer/espresso-whole-pull/pull/138",
      "title": "SCI-ED-003 — define minimum targeted closure contract",
      "merged": true,
      "merge_commit_sha": "f8bd4cc5c4c05869ceda75e273784781b8429c28",
      "selected_declarations": [
        "NO_GOVERNING_PHYSICS_CHANGE"
      ],
      "declaration_tokens": [
        "NO_GOVERNING_PHYSICS_CHANGE"
      ]
    },
    {
      "repository": "EWP",
      "pr": 136,
      "url": "https://github.com/trbrewer/espresso-whole-pull/pull/136",
      "title": "SCI-DATA-FUSION-001 — audited Phase B complementary result",
      "merged": true,
      "merge_commit_sha": "bd031c5acfbfb41e378424e5358a932a8f2f5a50",
      "selected_declarations": [],
      "declaration_tokens": []
    },
    {
      "repository": "EWP",
      "pr": 134,
      "url": "https://github.com/trbrewer/espresso-whole-pull/pull/134",
      "title": "XSV-PANNUSCH-EWP-INPUT-MAPPING-001 — Pannusch-to-EWP input mapping qualification",
      "merged": true,
      "merge_commit_sha": "2bf996596bb7408c2b5e2fc1eb0f7a65e5f5bae2",
      "selected_declarations": [
        "NO_GOVERNING_PHYSICS_CHANGE"
      ],
      "declaration_tokens": [
        "NO_GOVERNING_PHYSICS_CHANGE"
      ]
    },
    {
      "repository": "EWP",
      "pr": 132,
      "url": "https://github.com/trbrewer/espresso-whole-pull/pull/132",
      "title": "SCI-MD-PANNUSCH-FLOW-HISTORY-001 source qualification",
      "merged": true,
      "merge_commit_sha": "7c79c8c6bf4670cb8ade7fb107ecdfd73afa827e",
      "selected_declarations": [],
      "declaration_tokens": [
        "NO_GOVERNING_PHYSICS_CHANGE",
        "SOURCE_SCENARIO_CHANGE_ONLY"
      ]
    },
    {
      "repository": "EWP",
      "pr": 131,
      "url": "https://github.com/trbrewer/espresso-whole-pull/pull/131",
      "title": "OBS-PANNUSCH-FRACTION-WINDOW-001 — qualify source joins and test the Pannusch fraction-window observer",
      "merged": true,
      "merge_commit_sha": "c81a1e3af1e55bac81e12443e26f3e45f43319e6",
      "selected_declarations": [],
      "declaration_tokens": [
        "NO_GOVERNING_PHYSICS_CHANGE",
        "SOURCE_SCENARIO_CHANGE_ONLY"
      ]
    },
    {
      "repository": "EWP",
      "pr": 129,
      "url": "https://github.com/trbrewer/espresso-whole-pull/pull/129",
      "title": "EWP-REAL-WORLD-BOUNDARIES-001 — qualify recent-public operating boundaries and map porosity-conditioned EWP responses",
      "merged": true,
      "merge_commit_sha": "97d586fe21ca28cf7ef80a03ec0e15f3032ac0b5",
      "selected_declarations": [],
      "declaration_tokens": [
        "NO_GOVERNING_PHYSICS_CHANGE",
        "SOURCE_SCENARIO_CHANGE_ONLY"
      ]
    },
    {
      "repository": "EWP",
      "pr": 127,
      "url": "https://github.com/trbrewer/espresso-whole-pull/pull/127",
      "title": "EWP-POROSITY-PERMEABILITY-PRIOR-001 — qualify separate static hydraulic supports and execute bounded sensitivity",
      "merged": true,
      "merge_commit_sha": "34deac91170f49587820e60b6e357bfdc3e0874a",
      "selected_declarations": [],
      "declaration_tokens": [
        "NO_GOVERNING_PHYSICS_CHANGE",
        "SOURCE_SCENARIO_CHANGE_ONLY"
      ]
    },
    {
      "repository": "EWP",
      "pr": 125,
      "url": "https://github.com/trbrewer/espresso-whole-pull/pull/125",
      "title": "XSV-WASZKIEWICZ-DYNAMIC-HYD-001 — Adoption-grade resistance comparison and final test-authority reconciliation",
      "merged": true,
      "merge_commit_sha": "9c7b8b286d7a9943c72e35b8ea88cd592949488f",
      "selected_declarations": [],
      "declaration_tokens": []
    },
    {
      "repository": "EWP",
      "pr": 121,
      "url": "https://github.com/trbrewer/espresso-whole-pull/pull/121",
      "title": "XSV-PANNUSCH-MULTIMODEL-001 — Privilege-matched comparison of Pannusch fraction models",
      "merged": true,
      "merge_commit_sha": "36b68dc2670349738871ed2aad233357b1474123",
      "selected_declarations": [],
      "declaration_tokens": []
    },
    {
      "repository": "EWP",
      "pr": 119,
      "url": "https://github.com/trbrewer/espresso-whole-pull/pull/119",
      "title": "PANNUSCH-PRIOR-IMPACT-001 / ESPRESSO-DATA-LEVERAGE-001 — Install available-data controls and model-advancement programme",
      "merged": true,
      "merge_commit_sha": "1519a0294eda106ceeff9c56cd57c8027bdcd9cf",
      "selected_declarations": [],
      "declaration_tokens": []
    },
    {
      "repository": "EWP",
      "pr": 116,
      "url": "https://github.com/trbrewer/espresso-whole-pull/pull/116",
      "title": "Adopt data-first scientific development plan",
      "merged": true,
      "merge_commit_sha": "d1c4ea125fdd041991a5d1b1380cf4bfc2de31a9",
      "selected_declarations": [
        "NO_GOVERNING_PHYSICS_CHANGE"
      ],
      "declaration_tokens": [
        "NO_GOVERNING_PHYSICS_CHANGE"
      ]
    },
    {
      "repository": "EWP",
      "pr": 115,
      "url": "https://github.com/trbrewer/espresso-whole-pull/pull/115",
      "title": "SCI-MD-009-C1: terminal nonlinear-response qualification stop",
      "merged": true,
      "merge_commit_sha": "834820049a98e5084495bda94fc8f3c8234b062d",
      "selected_declarations": [
        "NO_GOVERNING_PHYSICS_CHANGE"
      ],
      "declaration_tokens": [
        "NO_GOVERNING_PHYSICS_CHANGE"
      ]
    },
    {
      "repository": "EWP",
      "pr": 114,
      "url": "https://github.com/trbrewer/espresso-whole-pull/pull/114",
      "title": "SCI-MD-008: prescribed-flow exact-fraction production reconstruction",
      "merged": true,
      "merge_commit_sha": "c33422204962e693d6410eae9024a79ddd776f94",
      "selected_declarations": [],
      "declaration_tokens": []
    },
    {
      "repository": "EWP",
      "pr": 113,
      "url": "https://github.com/trbrewer/espresso-whole-pull/pull/113",
      "title": "XSV-FLOW-001: add discrete prescribed-flow boundary mode",
      "merged": true,
      "merge_commit_sha": "3874865e124dba0340ca93626b9bbf80f1385664",
      "selected_declarations": [
        "NUMERICAL_METHOD_CHANGE"
      ],
      "declaration_tokens": [
        "NUMERICAL_METHOD_CHANGE"
      ]
    },
    {
      "repository": "EWP",
      "pr": 111,
      "url": "https://github.com/trbrewer/espresso-whole-pull/pull/111",
      "title": "Docs: reconcile final XSV-FRAC-001 merged status",
      "merged": true,
      "merge_commit_sha": "85190cf68cd80789d19f7836d88294c1030c6ff9",
      "selected_declarations": [],
      "declaration_tokens": []
    },
    {
      "repository": "EWP",
      "pr": 110,
      "url": "https://github.com/trbrewer/espresso-whole-pull/pull/110",
      "title": "XSV-FRAC-001: exact mass-defined multispecies cup fractions",
      "merged": true,
      "merge_commit_sha": "5b87d787aaf51fdd353c16ee9e08b6f6c6e83347",
      "selected_declarations": [
        "NUMERICAL_METHOD_CHANGE"
      ],
      "declaration_tokens": [
        "NUMERICAL_METHOD_CHANGE"
      ]
    },
    {
      "repository": "EWP",
      "pr": 108,
      "url": "https://github.com/trbrewer/espresso-whole-pull/pull/108",
      "title": "SCI-ED-002 R2A: qualify the blocked measurement-contract consumer",
      "merged": true,
      "merge_commit_sha": "fc668afbeb7782d3d342b8ba403fb6c1dee396d4",
      "selected_declarations": [],
      "declaration_tokens": []
    },
    {
      "repository": "EWP",
      "pr": 106,
      "url": "https://github.com/trbrewer/espresso-whole-pull/pull/106",
      "title": "SCI-MD-007: consume locked inventory feasibility result",
      "merged": true,
      "merge_commit_sha": "f31330d2bfb0c07c3afb5a1dd12a37d9c9752175",
      "selected_declarations": [],
      "declaration_tokens": []
    },
    {
      "repository": "EWP",
      "pr": 103,
      "url": "https://github.com/trbrewer/espresso-whole-pull/pull/103",
      "title": "SCI-MD-005 — evaluate production-consistent species-release mapping",
      "merged": true,
      "merge_commit_sha": "434c657fa35e1e36003c67b57062b216cddcc151",
      "selected_declarations": [
        "NO_GOVERNING_PHYSICS_CHANGE"
      ],
      "declaration_tokens": [
        "NO_GOVERNING_PHYSICS_CHANGE"
      ]
    },
    {
      "repository": "EWP",
      "pr": 101,
      "url": "https://github.com/trbrewer/espresso-whole-pull/pull/101",
      "title": "SCI-MD-004 Stage E1 — conditional hydraulic reconciliation and protected result",
      "merged": true,
      "merge_commit_sha": "3748703cfad8eb76a648e3de64871584aa7f66bb",
      "selected_declarations": [
        "NO_GOVERNING_PHYSICS_CHANGE"
      ],
      "declaration_tokens": [
        "NO_GOVERNING_PHYSICS_CHANGE"
      ]
    },
    {
      "repository": "EWP",
      "pr": 99,
      "url": "https://github.com/trbrewer/espresso-whole-pull/pull/99",
      "title": "SCI-MD-004 Stage E1 — record protected multispecies holdout result",
      "merged": true,
      "merge_commit_sha": "2d719ca226a124fb90d2c5ffff3a995d4a652c4f",
      "selected_declarations": [
        "NO_GOVERNING_PHYSICS_CHANGE"
      ],
      "declaration_tokens": [
        "NO_GOVERNING_PHYSICS_CHANGE"
      ]
    },
    {
      "repository": "EWP",
      "pr": 97,
      "url": "https://github.com/trbrewer/espresso-whole-pull/pull/97",
      "title": "SCI-MD-004 Stage E0: freeze target-blind parameterization",
      "merged": true,
      "merge_commit_sha": "c50c9a6ab122f3668372c7801c004f5fdc27beca",
      "selected_declarations": [
        "NO_GOVERNING_PHYSICS_CHANGE"
      ],
      "declaration_tokens": [
        "NO_GOVERNING_PHYSICS_CHANGE"
      ]
    },
    {
      "repository": "EWP",
      "pr": 95,
      "url": "https://github.com/trbrewer/espresso-whole-pull/pull/95",
      "title": "SCI-MD-004 Stage C R2 — verified indexed passive-species transport",
      "merged": true,
      "merge_commit_sha": "78e5ff5aecd23f9a67a83c6820942afae090b226",
      "selected_declarations": [],
      "declaration_tokens": []
    },
    {
      "repository": "EWP",
      "pr": 89,
      "url": "https://github.com/trbrewer/espresso-whole-pull/pull/89",
      "title": "SCI-MD-004 Stage A — multispecies contract and exact reduction design",
      "merged": true,
      "merge_commit_sha": "bf4de34310fcc433071e00ee7fa51082a37d1c4c",
      "selected_declarations": [
        "NO_GOVERNING_PHYSICS_CHANGE"
      ],
      "declaration_tokens": [
        "NO_GOVERNING_PHYSICS_CHANGE"
      ]
    },
    {
      "repository": "EWP",
      "pr": 87,
      "url": "https://github.com/trbrewer/espresso-whole-pull/pull/87",
      "title": "science: add SCI-MD-003 atlas consumer",
      "merged": true,
      "merge_commit_sha": "0d2fa7595c44f1f190e61af11db9d510a940f9e6",
      "selected_declarations": [
        "NO_GOVERNING_PHYSICS_CHANGE"
      ],
      "declaration_tokens": [
        "NO_GOVERNING_PHYSICS_CHANGE"
      ]
    },
    {
      "repository": "EWP",
      "pr": 71,
      "url": "https://github.com/trbrewer/espresso-whole-pull/pull/71",
      "title": "SCI-LC-001A: final accelerated closeout candidate",
      "merged": true,
      "merge_commit_sha": "73a7b184dacf6c8779d5c2e826ef3f11e8d362ee",
      "selected_declarations": [],
      "declaration_tokens": []
    },
    {
      "repository": "EWP",
      "pr": 80,
      "url": "https://github.com/trbrewer/espresso-whole-pull/pull/80",
      "title": "SCI-ED-001: virtual pressure-program mechanism-discrimination screen",
      "merged": true,
      "merge_commit_sha": "9ac7bf88340b5c12a0003729ac4e998b7bf67626",
      "selected_declarations": [],
      "declaration_tokens": []
    },
    {
      "repository": "PW",
      "pr": 261,
      "url": "https://github.com/trbrewer/puckworks/pull/261",
      "title": "ESPRESSO-CORPUS-LEVERAGE-002-C1 — Integrate reviewed local-corpus authority",
      "merged": true,
      "merge_commit_sha": "a3428a4d4ad571ef3168a70e8a04620fca5d3520",
      "selected_declarations": [],
      "declaration_tokens": []
    },
    {
      "repository": "EWP",
      "pr": 123,
      "url": "https://github.com/trbrewer/espresso-whole-pull/pull/123",
      "title": "ESPRESSO-CORPUS-LEVERAGE-002-C1 — Integrate reviewed whole-corpus portfolio and Waszkiewicz handoff",
      "merged": true,
      "merge_commit_sha": "992eb00c297a6146b92b632c761ecfa5c6d1e9cd",
      "selected_declarations": [],
      "declaration_tokens": []
    }
  ]
}
```

</details>



<a id="appendix-c"></a>

## Appendix C — Census, sampling, open work and earlier-review reconciliation

[Back to navigation](#review-navigation)

This appendix assembles the frozen review artifacts without a new scientific execution or a new GitHub query. **PW** means `trbrewer/puckworks` at `9dd456be7fd797b9cda0a2bbf50d1ac717d72835` (**@9dd456b**); **EWP** means `trbrewer/espresso-whole-pull` at `4284e9460c8057053e95de7cfa2fb3590e68e9db` (**@4284e94**). Open-work snapshots have their own observation timestamps in C.4; they are not restamped to the census endpoint.

**Evidence:** `[X]` labels census/static arithmetic re-executed by the principal reviewer. Per-PR primary-purpose choices, sample interpretations and the broader historical reconciliation remain delegated judgments, conservatively `[D−/J]` unless the principal finding explicitly rechecks the specific claim. Historical producer executions/statistics and unavailable original-review attribution remain `[S]`. A rechecked count does not promote all source interpretations behind that count. Main findings retain their own narrower `[R]`, `[X]` and `[D+]` support.

<a id="appendix-c-1"></a>

### C.1 — Static footprint and complete integration aggregates



#### C.1.1 — Method and temporal frame

The inclusive census endpoint is **2026-10-18T22:06:06Z**. The 30-day frame begins **2026-09-18T22:06:06Z** and the 60-day frame **2026-08-19T22:06:06Z**. The extraction enumerates each pinned repository’s entire first-parent history before filtering committer timestamps, avoiding early history termination from an out-of-order date. Each integration is counted once. A commit with multiple parents is a true merge; a single-parent PR integration is a squash. All 128 entries in the union of the two 60-day frames map to merged PRs, including manual merge commits PW #261 and EWP #123. The overlapping 30/60-day counts must not be added.

The prospective taxonomy amendment changed the third category from “retained-evidence analysis” to **scientific analysis/comparison**, with mandatory subtypes **retained-output only**, **new scenario evaluation under unchanged equations**, and **source/data qualification**. It was agreed before aggregate interpretation because new native integrations and new empirical fits under unchanged model equations were missing from the original taxonomy. “New evaluation” includes newly fitted empirical models on existing evidence, not only native solver calls. Scientific and numerical semantics control the primary purpose; declaration metadata corroborates that judgment and can also mention predecessors. Counts and text changes are **activity/footprint proxies, not labor hours, independent experiments, scientific-value scores or causal evidence of process burden**.

#### C.1.2 — Integration and scientific-subtype counts [X; category judgments D−/J]

| Metric | PW 30d | PW 60d | EWP 30d | EWP 60d |
| --- | --- | --- | --- | --- |
| Integrations | 54 | 65 | 30 | 63 |
| True merge / squash | 33 / 21 | 44 / 21 | 1 / 29 | 34 / 29 |
| Governing physics | 1 | 1 | 3 | 4 |
| Numerical methods | 15 | 15 | 2 | 5 |
| Scientific analysis | 31 | 37 | 21 | 46 |
| Assurance/governance | 2 | 5 | 0 | 2 |
| Documentation/status | 4 | 4 | 4 | 6 |
| Product/UI | 1 | 3 | 0 | 0 |
| Mixed-purpose | 15 | 20 | 16 | 20 |

| Frame | Retained-output only | New evaluation under unchanged equations | Source/data qualification | Mirrored PW-result handoffs in EWP |
| --- | --- | --- | --- | --- |
| PW 30d | 6 | 23 | 2 | 0 |
| PW 60d | 6 | 24 | 7 | 0 |
| EWP 30d | 15 | 6 | 0 | 14 |
| EWP 60d | 18 | 21 | 7 | 16 |

Fourteen of EWP30’s 15 retained-only integrations and sixteen of EWP60’s 18 are PW-result handoffs/consumers. These are not second independent experiments. The complete per-change records makes the lineage overlap visible.

#### C.1.3 — Marginal classification ranges [X conditional on explicit D−/J alternatives]

| Metric | PW 30d | PW 60d | EWP 30d | EWP 60d |
| --- | --- | --- | --- | --- |
| Governing physics | 1–2 | 1–2 | 3–3 | 4–5 |
| Numerical methods | 8–20 | 8–21 | 0–2 | 2–5 |
| Scientific analysis | 26–37 | 28–44 | 7–23 | 30–49 |
| Assurance/governance | 2–4 | 4–10 | 0–0 | 1–2 |
| Documentation/status | 2–5 | 2–5 | 4–18 | 6–22 |
| Product/UI | 0–2 | 2–4 | 0–0 | 0–0 |

Each range moves a mixed integration only among its recorded plausible alternatives. These are **marginal, not simultaneously attainable**, and are not confidence intervals. The broad EWP science/documentation range largely reflects how mirrored handoffs are classified. It does not conceal uncertainty in the underlying number of integrations.

#### C.1.4 — All-text change counts [X]

| Frame | Text lines added | Text lines deleted |
| --- | --- | --- |
| PW 30d | 1,217,361 | 20,073 |
| PW 60d | 1,289,043 | 26,750 |
| EWP 30d | 324,332 | 390 |
| EWP 60d | 576,347 | 1,668 |

These are first-parent `git diff --numstat --no-renames` totals. Generated result records, documentation, code and text data are all included; binary numstats are not counted as text. These totals are particularly unsuitable as implementation-effort estimates. The pinned-tree static footprint below is a separate measurement.

#### C.1.5 — Tracked-tree code and document footprint [X]

| Area | PW files / physical / nonblank LOC | EWP files / physical / nonblank LOC |
| --- | --- | --- |
| Models/solver | 55 / 10,305 / 9,055 | 7 / 5,793 / 5,583 |
| Analysis | 132 / 52,794 / 47,389 | 241 / 28,355 / 26,207 |
| Assurance/governance | 40 / 19,904 / 17,495 | 42 / 5,297 / 4,936 |
| Product/UI | 48 / 12,773 / 11,140 | 0 / 0 / 0 |
| Tests | 304 / 63,649 / 51,696 | 108 / 18,875 / 17,301 |
| Engineering tools | 102 / 26,869 / 23,518 | 64 / 15,557 / 14,223 |
| Other code | 66 / 20,055 / 17,646 | 42 / 9,653 / 8,765 |

| Metric | PW | EWP |
| --- | --- | --- |
| Tracked files | 2,871 | 2,438 |
| Files under docs | 1,761 | 927 |
| Immediate docs/analysis directories | 56 | 48 |
| Python test files | 304 | 104 |
| Static test-function definitions | 4,420 | 1,575 |
| Test AST parse failures | 0 | 0 |

PW’s 56 analysis directories include the non-task `generated`, giving 55 task-like directories before sample eligibility exclusions; EWP has 48 immediate analysis directories. PW has **28 `Component(...)` constructors, 79 top-level `gate_` functions, 66 registered gate references and 13 quick-only functions**. Static test-function definitions are not collected or parametrized test-case counts. EWP’s test code-file total includes four non-Python files in addition to its 104 Python test files.

All files are enumerated from pinned `git ls-tree`, including tracked files that local ignore rules would hide from default filesystem discovery. Code extensions are `.py`, `.C`, `.H`, `.cpp`, `.h`, `.cc`, `.c`, `.sh`, `.js`, `.ts`, `.tsx`, `.jsx`, plus `Allwmake`, `Allrun`, `Allverify`, `Allclean`. Physical LOC includes blank/comment lines; nonblank LOC is reported separately. The mutually exclusive path rules are implemented in Appendix B’s `build_census.py`; these are not a semantic partition of assurance versus science. AST parsing executes no models or tests and emits counts. Denied target data paths are excluded.

The physical-line ratio **(assurance + tests)/(models + analysis)** is **1.324 PW / 0.708 EWP**; adding all engineering tools to the numerator gives **1.750 / 1.163**. Scientific tests can dominate useful verification, and analysis modules can contain assurance. Neither ratio establishes a governance/science time ratio or fires SCI-GOV’s effort circuit breaker by itself. The EWP production PW lock remains deliberate: it is 456 graph commits / 109 first-parent integrations behind the reviewed PW main, without that distance constituting an automatic repin requirement.

<a id="appendix-c-2"></a>

### C.2 — Exact frozen sample frames and selections



Sample names and order below are the complete frozen records. No sampling was repeated to obtain a preferred outcome. The seed was **20261018**, selection without replacement on sorted eligible names. The root gate record and the independent repository bundle records are separate draws; the JSON preserves actual frames and selected order. Selected registry gates were executed within the complete registry run and must not be counted as additional independent successes.

#### C.2.1 — PW registry and quick-only gates

Recorded source: `review_work/results/gate_sample.json`. The purposive list contains 13 gates; remaining frames are 55 registry gates and 11 quick-only gates. The sampled counts are eight and four. The record below includes all exclusions represented by the purposive list and both complete frames.

<details>
<summary>Show exact frozen sample record — C.2.1 — PW registry and quick-only gates</summary>

```json
{
  "seed": 20261018,
  "defined_count": 79,
  "wired_count": 66,
  "quick_only_total": 13,
  "mandatory": [
    "gate_cameron_conservation",
    "gate_extraction_harness",
    "gate_foster_ct_trajectory",
    "gate_g10_viscosity_bulk_negligible",
    "gate_g4_temperature_sensitivity",
    "gate_grudeva2026_reduced",
    "gate_infiltration_triangle",
    "gate_lb_channel",
    "gate_pannusch_closures",
    "gate_pannusch_solver_mape",
    "gate_roman_bed_mpe_parameter_free",
    "gate_waszkiewicz_dynamic_9bar",
    "gate_waszkiewicz_static_refit"
  ],
  "registry_frame": [
    "gate_fasano_cor82_nonmonotone",
    "gate_fasano_freeboundary",
    "gate_fasano_reversal_signature",
    "gate_foster_fig15_flowmin",
    "gate_foster_machine_tp_ts",
    "gate_g10_foursource_spread",
    "gate_g10_intersource_spread",
    "gate_g10_mu_bias_directional",
    "gate_g10_reference_mu_above_water",
    "gate_g10_sobolik_closures",
    "gate_g10_sobolik_density",
    "gate_g10_telisromero2000_thermal",
    "gate_g10_telisromero_closure",
    "gate_g10_telisromero_full_table",
    "gate_g1_glassbead_closure_sane",
    "gate_g3_pump_envelope_bounds_quadratic",
    "gate_gagne2021_viscosity_discrimination",
    "gate_grindmap_polydispersity",
    "gate_grindmap_refit",
    "gate_grudeva_no_eps_kappa",
    "gate_grudeva_reduced_solver",
    "gate_inertial_darcy_recovery",
    "gate_inertial_de1_audit",
    "gate_inertial_fo_band",
    "gate_kappa_t_composition_diagnostic",
    "gate_kappa_t_degeneracy",
    "gate_lee_feedback_negative_result",
    "gate_liang_eoven_ceiling",
    "gate_liang_kemax_refit",
    "gate_maille_e1_shell_depth",
    "gate_maille_kinetics_ci_flags",
    "gate_maille_phi_closure_consistency",
    "gate_maille_phi_split_vs_cameron",
    "gate_maille_timescale_portability_cameron",
    "gate_maille_timescale_portability_roman",
    "gate_maille_two_regime_reproduction",
    "gate_mo2_coupled_bed_fig8",
    "gate_mo2_fixed_flow_trends",
    "gate_mo2_k0_carman_kozeny",
    "gate_mo2_swelling_flow_decay",
    "gate_mo2_swelling_insensitivity",
    "gate_mo_reynolds_overlay",
    "gate_moroney2015_batch_ode",
    "gate_moroney2015_kappa_anchors",
    "gate_moroney2019_ldf_verification",
    "gate_moroney_fig6_washthrough",
    "gate_pack_generator_admissible",
    "gate_roman_bed_flow_trend",
    "gate_roman_mw_temperature_trends",
    "gate_roman_sphere_solver",
    "gate_roman_tamped_kappa",
    "gate_roman_y0_ceiling_sizeexclusion",
    "gate_smrke2024_fast_extraction_shape",
    "gate_streamtube_heldout",
    "gate_wadsworth_collapse"
  ],
  "quick_only_frame": [
    "gate_bruno_solute_inventory_prior",
    "gate_coupled_kappa_t",
    "gate_egidi_bracket",
    "gate_g9_series_resistance",
    "gate_ntube_kappa_t_union",
    "gate_p2_cross_pressure",
    "gate_p2_kappa_ladder",
    "gate_p3_channeling_sigma_sweep",
    "gate_p3_schmieder_peak_discrimination",
    "gate_pannusch_qt_adapter",
    "gate_unified_kappa_t"
  ],
  "registry_sample": [
    "gate_wadsworth_collapse",
    "gate_roman_tamped_kappa",
    "gate_g10_telisromero_closure",
    "gate_inertial_darcy_recovery",
    "gate_roman_sphere_solver",
    "gate_foster_machine_tp_ts",
    "gate_maille_e1_shell_depth",
    "gate_maille_phi_split_vs_cameron"
  ],
  "quick_only_sample": [
    "gate_p3_schmieder_peak_discrimination",
    "gate_coupled_kappa_t",
    "gate_g9_series_resistance",
    "gate_bruno_solute_inventory_prior"
  ]
}
```

</details>


#### C.2.2 — Executed PW task-bundle sample and its pre-read amendment

Task bundles are immediate `PW:docs/analysis/<name>/@9dd456b` directories. The original 16-directory frame included `generated`, which is not a task bundle. It was removed **before sampled result reading** and the selection redrawn using the same fixed seed. Both original and corrected frames/selections are preserved. The resulting eligible frame is 15 tasks, with four sampled. Headline/protected prefixes were excluded as recorded, not after seeing results.

<details>
<summary>Show exact frozen sample record — C.2.2 — Executed PW task-bundle sample and its pre-read amendment</summary>

```json
{
  "rule": "Independent Random(20261018) per sorted repository frame; immediate docs/analysis directories; predeclared excluded prefixes",
  "excluded_prefixes": [
    "sci_md_010",
    "sci_md_011",
    "sci_md_012",
    "sci_md_mass",
    "sci_md_caffeine",
    "sci_md_trigonelline",
    "sci_md_5cqa",
    "sci_md_rheology",
    "model_grudeva2026",
    "model_pannusch2024",
    "val_case",
    "val_infra",
    "sci_md_004"
  ],
  "PW": {
    "sha": "9dd456be7fd797b9cda0a2bbf50d1ac717d72835",
    "seed": 20261018,
    "frame": [
      "model_eng_assay_envelope_001",
      "model_eng_mass_stop_001",
      "model_eng_robust_mass_stop_001",
      "model_foster2025_postsat_001",
      "rp_a_001",
      "rp_d_lc_001",
      "sci_ed_002",
      "sci_md_007",
      "sci_md_grudeva_clock_001",
      "sci_md_maille_transfer_001",
      "sci_md_mo_transfer_001",
      "sci_md_moroney_transfer_001",
      "sci_md_radial_obs_001",
      "sci_md_smrke_transfer_001",
      "sci_val_tamped_k_001"
    ],
    "n_frame": 15,
    "sample": [
      "sci_md_smrke_transfer_001",
      "sci_md_radial_obs_001",
      "model_foster2025_postsat_001",
      "rp_d_lc_001"
    ],
    "original_frame": [
      "generated",
      "model_eng_assay_envelope_001",
      "model_eng_mass_stop_001",
      "model_eng_robust_mass_stop_001",
      "model_foster2025_postsat_001",
      "rp_a_001",
      "rp_d_lc_001",
      "sci_ed_002",
      "sci_md_007",
      "sci_md_grudeva_clock_001",
      "sci_md_maille_transfer_001",
      "sci_md_mo_transfer_001",
      "sci_md_moroney_transfer_001",
      "sci_md_radial_obs_001",
      "sci_md_smrke_transfer_001",
      "sci_val_tamped_k_001"
    ],
    "original_sample": [
      "rp_d_lc_001",
      "rp_a_001",
      "sci_md_moroney_transfer_001",
      "model_eng_assay_envelope_001"
    ]
  },
  "amendment_before_result_reads": "Excluded PW generated, which is a generated artifact directory rather than a task bundle. Original frame/sample retained below; no sampled results read before this correction. EWP sample frozen here will not execute, because another reviewer had independently frozen its EWP sample."
}
```

</details>


#### C.2.3 — Executed EWP task-bundle sample

Recorded source: `review_work/ewp/sample.json`. Task directories resolve as `EWP:docs/analysis/<name>/@4284e94`. The full eligible frame is 20 tasks, with four sampled. The record’s `D-minus until root rechecks` is its original evidence label; the main report identifies any subsequently rechecked sample claim individually.

<details>
<summary>Show exact frozen sample record — C.2.3 — Executed EWP task-bundle sample</summary>

```json
{
  "seed": 20261018,
  "frame": [
    "espresso_corpus_leverage_002",
    "espresso_data_leverage_001",
    "ewp_porosity_permeability_prior_001",
    "ewp_real_world_boundaries_001",
    "obs_pannusch_fraction_window_001",
    "pannusch_prior_impact_001",
    "sci_data_fusion_001",
    "sci_ed_001",
    "sci_lc_001a",
    "sci_md_003",
    "sci_md_grudeva_clock_001",
    "sci_md_maille_transfer_001",
    "sci_md_mo_transfer_001",
    "sci_md_moroney_transfer_001",
    "sci_md_pannusch_flow_history_001",
    "sci_md_radial_obs_001",
    "sci_md_smrke_transfer_001",
    "xsv_pannusch_ewp_input_mapping_001",
    "xsv_pannusch_multimodel_001",
    "xsv_waszkiewicz_dynamic_hyd_001"
  ],
  "excluded": [
    "sci_ed_003",
    "sci_md_002a",
    "sci_md_002b",
    "sci_md_002c",
    "sci_md_008",
    "sci_md_009",
    "sci_md_009_c1",
    "sci_md_010",
    "sci_md_011",
    "sci_md_012"
  ],
  "excluded_prefixes": [
    "sci_md_mass_delivery_",
    "sci_md_caffeine_delivery_",
    "sci_md_rheology_",
    "sci_md_004",
    "data_leverage"
  ],
  "sample": [
    "sci_data_fusion_001",
    "sci_md_grudeva_clock_001",
    "ewp_porosity_permeability_prior_001",
    "sci_md_pannusch_flow_history_001"
  ],
  "phase": "frozen before sampled result reading",
  "evidence": "D-minus until root rechecks"
}
```

</details>


#### C.2.4 — Duplicate EWP frame, preserved but not executed

A second reviewer independently froze the following 25-directory EWP frame before discovering the EWP reviewer’s existing sample. It was **not executed** and is not another sample of inspected results. Its differing eligibility choices therefore did not expand or replace the executed frame. It is retained to make the sampling amendment auditable.

<details>
<summary>Show exact frozen sample record — C.2.4 — Duplicate EWP frame, preserved but not executed</summary>

```json
{
  "rule": "Independent Random(20261018) per sorted repository frame; immediate docs/analysis directories; predeclared excluded prefixes",
  "excluded_prefixes": [
    "sci_md_010",
    "sci_md_011",
    "sci_md_012",
    "sci_md_mass",
    "sci_md_caffeine",
    "sci_md_trigonelline",
    "sci_md_5cqa",
    "sci_md_rheology",
    "model_grudeva2026",
    "model_pannusch2024",
    "val_case",
    "val_infra",
    "sci_md_004"
  ],
  "EWP_duplicate": {
    "sha": "4284e9460c8057053e95de7cfa2fb3590e68e9db",
    "seed": 20261018,
    "frame": [
      "data_leverage",
      "espresso_corpus_leverage_002",
      "espresso_data_leverage_001",
      "ewp_porosity_permeability_prior_001",
      "ewp_real_world_boundaries_001",
      "obs_pannusch_fraction_window_001",
      "pannusch_prior_impact_001",
      "sci_data_fusion_001",
      "sci_ed_001",
      "sci_ed_003",
      "sci_lc_001a",
      "sci_md_002a",
      "sci_md_002b",
      "sci_md_002c",
      "sci_md_003",
      "sci_md_grudeva_clock_001",
      "sci_md_maille_transfer_001",
      "sci_md_mo_transfer_001",
      "sci_md_moroney_transfer_001",
      "sci_md_pannusch_flow_history_001",
      "sci_md_radial_obs_001",
      "sci_md_smrke_transfer_001",
      "xsv_pannusch_ewp_input_mapping_001",
      "xsv_pannusch_multimodel_001",
      "xsv_waszkiewicz_dynamic_hyd_001"
    ],
    "n_frame": 25,
    "sample": [
      "pannusch_prior_impact_001",
      "sci_lc_001a",
      "xsv_waszkiewicz_dynamic_hyd_001",
      "espresso_data_leverage_001"
    ],
    "execution_status": "NOT_EXECUTED_DUPLICATE_FRAME; primary EWP sample at review_work/ewp/sample.json"
  }
}
```

</details>


<a id="appendix-c-3"></a>

### C.3 — Complete 128-integration census



The following is the complete per-integration census, not a selected example list. Git identities, dates and numerical aggregates are `[X]`; primary-purpose and alternative labels remain `[D−/J]` except where independently supported in the main findings. **Appendix B embeds the extraction/classification/rendering scripts and selected PR metadata, including `all_pr_metadata_selected.json`; together with the pinned full-history Git trees they regenerate all exact paths, per-path numstats, full commit identities and classification reasons.** The inline paths are grouped for readability, not a claim that only those groups changed.

Endpoint 2026-10-18T22:06:06Z; 60-day window inclusive from 2026-08-19T22:06:06Z; a **30** in the window field also places that integration in the 30-day window from 2026-09-18T22:06:06Z. Dates below are UTC committer dates. M = actual merge; S = single-parent squash PR. All records mapped to merged PRs. The full exact identities, changed-path lists, per-path numstats and rationale are reproducible using the embedded Appendix B inputs and pinned repositories; no separate review artifact is required.

Labels: Physics = governing-physics change; Numerics = numerical/geometry/solver capability; Science = scientific analysis/comparison. Its subtypes are retained-output only, new scenario evaluation under unchanged equations (including newly fitted empirical models), and source/data qualification. Alternate labels are plausible primary-purpose classifications, not extra integrations. Mirror marks PW-result handoffs in EWP, not a second independent study. Declaration abbreviations are the literal declared change types, with NO-GOV = NO_GOVERNING_PHYSICS_CHANGE; SCENARIO = SOURCE_SCENARIO_CHANGE_ONLY; NUMERICAL = NUMERICAL_METHOD_CHANGE; GOV = GOVERNING_PHYSICS_CHANGE; GEOMETRY/NO-GOV = GEOMETRY_COMPATIBILITY_NO_GOVERNING_PHYSICS_CHANGE. “none found” is absence from bounded metadata extraction, not proof no declaration exists. “PR:” means selected PR declaration; “file:” means declaration token observed in a changed contract/protocol/authority/handoff. File tokens can include predecessor descriptions and do not automatically describe the current change. Paths show the three largest changed path groups plus the total exact file count; no count is a person-hour estimate.

#### C.3.1 — PW: all 65 integrations in 60 days

<a id="census-pw-340"></a>

##### PW #340 — T04: retain 5-CQA gain sensitivity and RMSE decomposition

**UTC date / window:** 2026-10-18 / 30+60

**PR / merge SHA:** [#340](https://github.com/trbrewer/puckworks/pull/340) M `9dd456be7fd7`

**Primary / scientific subtype:** Science / Retained only

**Alternative / mirror:** —

**Declaration metadata:** PR: NO-GOV

**Changed path groups:** `docs/analysis/val_case_5cqa_decision_resolution_001/` (10); `docs/` (2); `puckworks/analysis/` (1); 14 files total

<a id="census-pw-339"></a>

##### PW #339 — VAL-CASE-CAFFEINE-001: persistent primary gains, conditional stress benefit

**UTC date / window:** 2026-10-18 / 30+60

**PR / merge SHA:** [#339](https://github.com/trbrewer/puckworks/pull/339) M `43ec258c3db4`

**Primary / scientific subtype:** Science / Retained only

**Alternative / mirror:** —

**Declaration metadata:** PR: NO-GOV

**Changed path groups:** `docs/analysis/val_case_caffeine_decision_resolution_001/` (9); `docs/` (1); `puckworks/analysis/` (1); 12 files total

<a id="census-pw-338"></a>

##### PW #338 — VAL-CASE-RHEOLOGY-DECISION-RESOLUTION-001: preserve contracts and report numerical sensitivity

**UTC date / window:** 2026-10-18 / 30+60

**PR / merge SHA:** [#338](https://github.com/trbrewer/puckworks/pull/338) M `79852f11073e`

**Primary / scientific subtype:** Science / Retained only

**Alternative / mirror:** —

**Declaration metadata:** PR: NO-GOV

**Changed path groups:** `docs/analysis/val_case_rheology_decision_resolution_001/` (7); `docs/` (1); `puckworks/analysis/` (1); 11 files total

<a id="census-pw-335"></a>

##### PW #335 — VAL-INFRA-DECISION-RESOLUTION-001: prospective policy and synthetic evaluator

**UTC date / window:** 2026-10-15 / 30+60

**PR / merge SHA:** [#335](https://github.com/trbrewer/puckworks/pull/335) M `882584d110e1`

**Primary / scientific subtype:** Assurance

**Alternative / mirror:** —

**Declaration metadata:** PR: NO-GOV

**Changed path groups:** `docs/governance/` (2); `docs/` (1); `docs/analysis/val_infra_decision_resolution_001/` (1); 7 files total

<a id="census-pw-334"></a>

##### PW #334 — SCI-MD-MASS-UNCERTAINTY-001: audit retained scores and physical-shot sensitivity

**UTC date / window:** 2026-10-14 / 30+60

**PR / merge SHA:** [#334](https://github.com/trbrewer/puckworks/pull/334) M `7975fbc39a64`

**Primary / scientific subtype:** Science / Retained only

**Alternative / mirror:** —

**Declaration metadata:** PR: NO-GOV

**Changed path groups:** `docs/analysis/sci_md_mass_uncertainty_001/` (4); `docs/` (1); `docs/planning/` (1); 9 files total

<a id="census-pw-332"></a>

##### PW #332 — docs: preserve the October 9 threshold and capability review

**UTC date / window:** 2026-10-09 / 30+60

**PR / merge SHA:** [#332](https://github.com/trbrewer/puckworks/pull/332) M `3cd308ac5bed`

**Primary / scientific subtype:** Docs/status

**Alternative / mirror:** —

**Declaration metadata:** PR: NO-GOV

**Changed path groups:** `docs/research/` (2); `docs/` (1); 3 files total

<a id="census-pw-331"></a>

##### PW #331 — MODEL-GRUDEVA2026-009: qualified methods corroborate publication discrepancies

**UTC date / window:** 2026-10-09 / 30+60

**PR / merge SHA:** [#331](https://github.com/trbrewer/puckworks/pull/331) M `3afe04dc9e0e`

**Primary / scientific subtype:** Science / Retained only

**Alternative / mirror:** —

**Declaration metadata:** PR: NO-GOV

**Changed path groups:** `docs/analysis/model_grudeva2026_publication_reconciliation_009/` (10); `docs/insights/` (8); `docs/` (2); 24 files total

<a id="census-pw-330"></a>

##### PW #330 — MODEL-GRUDEVA2026-MATCHED-COMPARISON-008: compare retained qualified baselines

**UTC date / window:** 2026-10-09 / 30+60

**PR / merge SHA:** [#330](https://github.com/trbrewer/puckworks/pull/330) M `ab28bd1d20b4`

**Primary / scientific subtype:** Science / Retained only

**Alternative / mirror:** —

**Declaration metadata:** PR: NO-GOV

**Changed path groups:** `docs/analysis/model_grudeva2026_matched_comparison_008/` (12); `docs/insights/` (8); `docs/` (2); 26 files total

<a id="census-pw-329"></a>

##### PW #329 — 0.4: complete Grudeva fine-baseline qualification 007

**UTC date / window:** 2026-10-09 / 30+60

**PR / merge SHA:** [#329](https://github.com/trbrewer/puckworks/pull/329) M `37f62d80ce97`

**Primary / scientific subtype:** Science / New evaluation

**Alternative / mirror:** Numerics

**Declaration metadata:** PR: NO-GOV

**Changed path groups:** `docs/analysis/model_grudeva2026_fine_baseline_qualification_007/` (40); `puckworks/analysis/` (3); `tests/` (3); 51 files total

<a id="census-pw-328"></a>

##### PW #328 — 67: bounded 512-cell spatial assessment passes declared gates (006)

**UTC date / window:** 2026-10-09 / 30+60

**PR / merge SHA:** [#328](https://github.com/trbrewer/puckworks/pull/328) M `751d5de1badf`

**Primary / scientific subtype:** Science / New evaluation

**Alternative / mirror:** Numerics

**Declaration metadata:** PR: NO-GOV

**Changed path groups:** `docs/analysis/model_grudeva2026_spatial_resolution_006/` (10); `docs/` (2); `puckworks/analysis/` (2); 16 files total

<a id="census-pw-327"></a>

##### PW #327 — 67: Grudeva2026 baseline observation 005 — single-axis diagnosis, qualification incomplete

**UTC date / window:** 2026-10-08 / 30+60

**PR / merge SHA:** [#327](https://github.com/trbrewer/puckworks/pull/327) M `5e07a1992c40`

**Primary / scientific subtype:** Science / New evaluation

**Alternative / mirror:** Numerics

**Declaration metadata:** PR: NO-GOV

**Changed path groups:** `docs/analysis/model_grudeva2026_baseline_observation_005/` (13); `tests/` (6); `puckworks/analysis/` (4); 26 files total

<a id="census-pw-326"></a>

##### PW #326 — 1.7b: qualify Grudeva bed-accuracy comparator (#67)

**UTC date / window:** 2026-10-08 / 30+60

**PR / merge SHA:** [#326](https://github.com/trbrewer/puckworks/pull/326) M `45f594b92e6b`

**Primary / scientific subtype:** Numerics

**Alternative / mirror:** —

**Declaration metadata:** PR: NUMERICAL

**Changed path groups:** `tools/` (7); `docs/analysis/model_grudeva2026_bed_accuracy_004/` (5); `docs/` (2); 24 files total

<a id="census-pw-325"></a>

##### PW #325 — MODEL-PANNUSCH2024-FLOW-CONSISTENT-OBSERVATION-001: qualify opt-in volume-clock observer

**UTC date / window:** 2026-10-08 / 30+60

**PR / merge SHA:** [#325](https://github.com/trbrewer/puckworks/pull/325) M `4536775551c4`

**Primary / scientific subtype:** Numerics

**Alternative / mirror:** —

**Declaration metadata:** PR: NUMERICAL

**Changed path groups:** `docs/analysis/model_pannusch2024_flow_consistent_observation_001/` (9); `docs/insights/` (8); `docs/` (2); 25 files total

<a id="census-pw-324"></a>

##### PW #324 — PV-19A: disclose Guided Pull pressure and evidence limits

**UTC date / window:** 2026-10-07 / 30+60

**PR / merge SHA:** [#324](https://github.com/trbrewer/puckworks/pull/324) M `b9ad38c6ebfe`

**Primary / scientific subtype:** Product/UI

**Alternative / mirror:** Docs/status

**Declaration metadata:** none found

**Changed path groups:** `puckworks/product/` (2); `docs/` (1); `puckworks/viz/` (1); 6 files total

<a id="census-pw-322"></a>

##### PW #322 — ESPRESSO-DEVELOPMENT-GUIDE-001: explain PW/EWP capabilities, evidence and next decisions

**UTC date / window:** 2026-10-07 / 30+60

**PR / merge SHA:** [#322](https://github.com/trbrewer/puckworks/pull/322) M `149aebfb8053`

**Primary / scientific subtype:** Docs/status

**Alternative / mirror:** —

**Declaration metadata:** PR: NO-GOV

**Changed path groups:** `docs/` (1); `docs/research/` (1); 2 files total

<a id="census-pw-323"></a>

##### PW #323 — ci: bound unchanged quality coverage job at 45 minutes

**UTC date / window:** 2026-10-07 / 30+60

**PR / merge SHA:** [#323](https://github.com/trbrewer/puckworks/pull/323) M `501fa069e2e5`

**Primary / scientific subtype:** Assurance

**Alternative / mirror:** —

**Declaration metadata:** PR: NO-GOV

**Changed path groups:** `.github/workflows/` (1); 1 files total

<a id="census-pw-320"></a>

##### PW #320 — Add prefix-conditioned finite-fraction delivery bounds (006)

**UTC date / window:** 2026-10-05 / 30+60

**PR / merge SHA:** [#320](https://github.com/trbrewer/puckworks/pull/320) M `f08677b177d9`

**Primary / scientific subtype:** Numerics

**Alternative / mirror:** Science

**Declaration metadata:** PR: NO-GOV

**Changed path groups:** `docs/analysis/model_pannusch2024_prefix_conditioned_006/` (21); `docs/insights/` (8); `docs/` (3); 40 files total

<a id="census-pw-319"></a>

##### PW #319 — MODEL-PANNUSCH2024-STATE-ENVELOPE-005: bound shared-state FV delivery

**UTC date / window:** 2026-10-05 / 30+60

**PR / merge SHA:** [#319](https://github.com/trbrewer/puckworks/pull/319) M `4f652dee3a43`

**Primary / scientific subtype:** Numerics

**Alternative / mirror:** Science

**Declaration metadata:** PR: NO-GOV

**Changed path groups:** `docs/analysis/model_pannusch2024_state_envelope_005/` (10); `docs/insights/` (8); `docs/` (3); 29 files total

<a id="census-pw-318"></a>

##### PW #318 — 004: add explicit FV chemical states and checked continuation

**UTC date / window:** 2026-10-04 / 30+60

**PR / merge SHA:** [#318](https://github.com/trbrewer/puckworks/pull/318) M `28c32df8ed99`

**Primary / scientific subtype:** Numerics

**Alternative / mirror:** —

**Declaration metadata:** PR: NUMERICAL

**Changed path groups:** `docs/analysis/model_pannusch2024_stateful_fv_004/` (12); `docs/insights/` (8); `docs/` (3); 35 files total

<a id="census-pw-317"></a>

##### PW #317 — MODEL-PANNUSCH2024-FLOW-TEMP-FV-003: prescribed flow and temperature FV research API

**UTC date / window:** 2026-10-04 / 30+60

**PR / merge SHA:** [#317](https://github.com/trbrewer/puckworks/pull/317) M `58b6cd2f29af`

**Primary / scientific subtype:** Numerics

**Alternative / mirror:** —

**Declaration metadata:** PR: NUMERICAL

**Changed path groups:** `docs/analysis/model_pannusch2024_flow_temp_fv_003/` (10); `docs/insights/` (8); `docs/` (2); 30 files total

<a id="census-pw-315"></a>

##### PW #315 — MODEL-PANNUSCH2024-POSITIVE-FV-002: conservative positive FV research backend (stacked)

**UTC date / window:** 2026-10-04 / 30+60

**PR / merge SHA:** [#315](https://github.com/trbrewer/puckworks/pull/315) M `1d780b7fb57d`

**Primary / scientific subtype:** Numerics

**Alternative / mirror:** —

**Declaration metadata:** PR: NUMERICAL

**Changed path groups:** `docs/analysis/model_pannusch2024_positive_fv_002/` (10); `docs/insights/` (8); `docs/` (2); 29 files total

<a id="census-pw-314"></a>

##### PW #314 — MODEL-PANNUSCH2024-TEMP-HISTORY-001: prescribed temperature API; qualification incomplete

**UTC date / window:** 2026-10-04 / 30+60

**PR / merge SHA:** [#314](https://github.com/trbrewer/puckworks/pull/314) M `1e9f85a5e42d`

**Primary / scientific subtype:** Numerics

**Alternative / mirror:** —

**Declaration metadata:** PR: NUMERICAL

**Changed path groups:** `docs/analysis/model_pannusch2024_temp_history_001/` (8); `docs/insights/` (8); `docs/` (3); 28 files total

<a id="census-pw-312"></a>

##### PW #312 — 1.6: complete Foster post-saturation headspace and water accounting

**UTC date / window:** 2026-10-03 / 30+60

**PR / merge SHA:** [#312](https://github.com/trbrewer/puckworks/pull/312) M `95f6b54f1f00`

**Primary / scientific subtype:** Physics

**Alternative / mirror:** —

**Declaration metadata:** PR: GOV

**Changed path groups:** `docs/insights/` (8); `docs/analysis/model_foster2025_postsat_001/` (4); `tests/` (4); 29 files total

<a id="census-pw-310"></a>

##### PW #310 — MODEL-GRUDEVA2026-CONSERVATIVE-003: conservative repair, coupled qualification incomplete

**UTC date / window:** 2026-10-03 / 30+60

**PR / merge SHA:** [#310](https://github.com/trbrewer/puckworks/pull/310) M `5745f615637d`

**Primary / scientific subtype:** Numerics

**Alternative / mirror:** —

**Declaration metadata:** PR: NUMERICAL

**Changed path groups:** `docs/insights/` (8); `docs/analysis/model_grudeva2026_conservative_003/` (5); `puckworks/analysis/` (3); 21 files total

<a id="census-pw-309"></a>

##### PW #309 — MODEL-GRUDEVA2026-REFERENCE-002: bounded comparator qualification incomplete

**UTC date / window:** 2026-10-03 / 30+60

**PR / merge SHA:** [#309](https://github.com/trbrewer/puckworks/pull/309) M `73b55cf80705`

**Primary / scientific subtype:** Numerics

**Alternative / mirror:** —

**Declaration metadata:** PR: NUMERICAL

**Changed path groups:** `docs/insights/` (8); `docs/analysis/model_grudeva2026_reference_002/` (4); `puckworks/analysis/` (2); 18 files total

<a id="census-pw-308"></a>

##### PW #308 — Add independently derived Grudeva EJAM reduced solver and native reference runner

**UTC date / window:** 2026-10-03 / 30+60

**PR / merge SHA:** [#308](https://github.com/trbrewer/puckworks/pull/308) M `8f5607799ff0`

**Primary / scientific subtype:** Numerics

**Alternative / mirror:** Physics, Product/UI

**Declaration metadata:** PR: NO-GOV; file: NUMERICAL

**Changed path groups:** `docs/paper3_resource/` (13); `tests/` (13); `docs/insights/` (12); 95 files total

<a id="census-pw-307"></a>

##### PW #307 — SCI-MD-MASS-STOP-DECISION-001: record adequate observed-boundary replay

**UTC date / window:** 2026-10-02 / 30+60

**PR / merge SHA:** [#307](https://github.com/trbrewer/puckworks/pull/307) M `ca663733c0cd`

**Primary / scientific subtype:** Science / New evaluation

**Alternative / mirror:** —

**Declaration metadata:** PR: NO-GOV

**Changed path groups:** `docs/analysis/sci_md_mass_stop_decision_001/` (17); `docs/` (3); `puckworks/analysis/` (2); 24 files total

<a id="census-pw-305"></a>

##### PW #305 — docs: preserve espresso review, source execution and mass-budget findings

**UTC date / window:** 2026-10-02 / 30+60

**PR / merge SHA:** [#305](https://github.com/trbrewer/puckworks/pull/305) M `54edb7683154`

**Primary / scientific subtype:** Docs/status

**Alternative / mirror:** Science

**Declaration metadata:** PR: NO-GOV

**Changed path groups:** `docs/research/` (60); `README.md` (1); 61 files total

<a id="census-pw-304"></a>

##### PW #304 — Fix Cameron inventory accounting and audit evidence bindings

**UTC date / window:** 2026-09-30 / 30+60

**PR / merge SHA:** [#304](https://github.com/trbrewer/puckworks/pull/304) S `15479363ab3b`

**Primary / scientific subtype:** Numerics

**Alternative / mirror:** Assurance

**Declaration metadata:** PR: NUMERICAL; file: NO-GOV

**Changed path groups:** `docs/cards/` (15); `tests/` (10); `docs/insights/` (8); 62 files total

<a id="census-pw-303"></a>

##### PW #303 — MODEL-ENG-ROBUST-MASS-STOP-001: continuous assay-robust stopping enclosures

**UTC date / window:** 2026-09-30 / 30+60

**PR / merge SHA:** [#303](https://github.com/trbrewer/puckworks/pull/303) S `713c3c229568`

**Primary / scientific subtype:** Numerics

**Alternative / mirror:** Science

**Declaration metadata:** PR: NO-GOV

**Changed path groups:** `docs/` (3); `docs/analysis/model_eng_robust_mass_stop_001/` (2); `puckworks/analysis/` (1); 7 files total

<a id="census-pw-302"></a>

##### PW #302 — MODEL-ENG-ASSAY-ENVELOPE-001: bounded-assay delivery envelopes

**UTC date / window:** 2026-09-30 / 30+60

**PR / merge SHA:** [#302](https://github.com/trbrewer/puckworks/pull/302) S `8fa96fc3fd99`

**Primary / scientific subtype:** Numerics

**Alternative / mirror:** Science

**Declaration metadata:** PR: NO-GOV

**Changed path groups:** `docs/` (3); `docs/analysis/model_eng_assay_envelope_001/` (2); `puckworks/analysis/` (1); 7 files total

<a id="census-pw-301"></a>

##### PW #301 — MODEL-ENG-MASS-STOP-001: add complete inverse stopping-mass queries

**UTC date / window:** 2026-09-30 / 30+60

**PR / merge SHA:** [#301](https://github.com/trbrewer/puckworks/pull/301) S `e33153b22036`

**Primary / scientific subtype:** Numerics

**Alternative / mirror:** Science

**Declaration metadata:** PR: NO-GOV

**Changed path groups:** `docs/` (3); `docs/analysis/model_eng_mass_stop_001/` (2); `puckworks/analysis/` (1); 7 files total

<a id="census-pw-300"></a>

##### PW #300 — SCI-MD-5CQA-ASSAY-002: matched early-assay families fail primary adequacy

**UTC date / window:** 2026-09-29 / 30+60

**PR / merge SHA:** [#300](https://github.com/trbrewer/puckworks/pull/300) S `d9924186a0da`

**Primary / scientific subtype:** Science / New evaluation

**Alternative / mirror:** —

**Declaration metadata:** PR: NO-GOV

**Changed path groups:** `docs/analysis/sci_md_5cqa_assay_002/` (31); `docs/` (3); `puckworks/analysis/` (3); 40 files total

<a id="census-pw-299"></a>

##### PW #299 — SCI-MD-5CQA-ASSAY-001: first-assay families fail primary adequacy

**UTC date / window:** 2026-09-29 / 30+60

**PR / merge SHA:** [#299](https://github.com/trbrewer/puckworks/pull/299) M `e6567a392e6d`

**Primary / scientific subtype:** Science / New evaluation

**Alternative / mirror:** —

**Declaration metadata:** PR: NO-GOV

**Changed path groups:** `docs/analysis/sci_md_5cqa_assay_001/` (29); `docs/` (3); `puckworks/analysis/` (3); 38 files total

<a id="census-pw-298"></a>

##### PW #298 — SCI-MD-5CQA-TDS-001: close negative early-TDS-conditioned 5-CQA comparison

**UTC date / window:** 2026-09-29 / 30+60

**PR / merge SHA:** [#298](https://github.com/trbrewer/puckworks/pull/298) M `db6f509d20ea`

**Primary / scientific subtype:** Science / New evaluation

**Alternative / mirror:** —

**Declaration metadata:** PR: NO-GOV

**Changed path groups:** `docs/analysis/sci_md_5cqa_tds_001/` (28); `docs/` (3); `puckworks/analysis/` (3); 37 files total

<a id="census-pw-297"></a>

##### PW #297 — SCI-MD-5CQA-DELIVERY-001: repair WP6 history and complete negative E0/D0 comparison

**UTC date / window:** 2026-09-29 / 30+60

**PR / merge SHA:** [#297](https://github.com/trbrewer/puckworks/pull/297) M `7df8db644ad0`

**Primary / scientific subtype:** Science / New evaluation

**Alternative / mirror:** —

**Declaration metadata:** PR: NO-GOV

**Changed path groups:** `docs/analysis/sci_md_5cqa_delivery_001/` (28); `tests/` (4); `docs/` (3); 39 files total

<a id="census-pw-296"></a>

##### PW #296 — SCI-VAL-TAMPED-K-001: consolidated-input adapter fails frozen screen

**UTC date / window:** 2026-09-28 / 30+60

**PR / merge SHA:** [#296](https://github.com/trbrewer/puckworks/pull/296) M `14c6b0992fc5`

**Primary / scientific subtype:** Science / New evaluation

**Alternative / mirror:** —

**Declaration metadata:** PR: NO-GOV

**Changed path groups:** `docs/analysis/sci_val_tamped_k_001/` (14); `docs/insights/` (13); `docs/` (6); 42 files total

<a id="census-pw-295"></a>

##### PW #295 — SCI-MD-TRIGONELLINE-DELIVERY-001: qualify mass-only prediction on the frozen campaign

**UTC date / window:** 2026-09-28 / 30+60

**PR / merge SHA:** [#295](https://github.com/trbrewer/puckworks/pull/295) S `baa707d65a01`

**Primary / scientific subtype:** Science / New evaluation

**Alternative / mirror:** —

**Declaration metadata:** PR: NO-GOV

**Changed path groups:** `docs/analysis/sci_md_trigonelline_delivery_001/` (28); `puckworks/analysis/` (3); `tests/` (3); 36 files total

<a id="census-pw-294"></a>

##### PW #294 — SCI-MD-MASS-DELIVERY-008: adequate one-shot adaptation; increments not earned

**UTC date / window:** 2026-09-27 / 30+60

**PR / merge SHA:** [#294](https://github.com/trbrewer/puckworks/pull/294) S `a37e3005a2a6`

**Primary / scientific subtype:** Science / New evaluation

**Alternative / mirror:** —

**Declaration metadata:** PR: NO-GOV

**Changed path groups:** `docs/analysis/sci_md_mass_delivery_008/` (18); `puckworks/analysis/` (3); `docs/` (2); 26 files total

<a id="census-pw-292"></a>

##### PW #292 — SCI-MD-MASS-DELIVERY-007: frozen pooled transfer fails adequacy despite earned increments

**UTC date / window:** 2026-09-27 / 30+60

**PR / merge SHA:** [#292](https://github.com/trbrewer/puckworks/pull/292) S `173d4265e17b`

**Primary / scientific subtype:** Science / New evaluation

**Alternative / mirror:** —

**Declaration metadata:** PR: NO-GOV

**Changed path groups:** `docs/analysis/sci_md_mass_delivery_007/` (19); `docs/` (2); `puckworks/analysis/` (2); 25 files total

<a id="census-pw-290"></a>

##### PW #290 — SCI-MD-CAFFEINE-DELIVERY-001: adequate simpler predictors, no earned complexity

**UTC date / window:** 2026-09-27 / 30+60

**PR / merge SHA:** [#290](https://github.com/trbrewer/puckworks/pull/290) S `6edc5b827999`

**Primary / scientific subtype:** Science / New evaluation

**Alternative / mirror:** —

**Declaration metadata:** PR: NO-GOV

**Changed path groups:** `docs/analysis/sci_md_caffeine_delivery_001/` (26); `puckworks/analysis/` (4); `tests/` (3); 36 files total

<a id="census-pw-288"></a>

##### PW #288 — SCI-MD-MASS-DELIVERY-006: learn conditional tail delivery from complete FIT trajectories

**UTC date / window:** 2026-09-27 / 30+60

**PR / merge SHA:** [#288](https://github.com/trbrewer/puckworks/pull/288) S `5bd2bf8916e7`

**Primary / scientific subtype:** Science / New evaluation

**Alternative / mirror:** —

**Declaration metadata:** PR: NO-GOV

**Changed path groups:** `docs/analysis/sci_md_mass_delivery_006/` (20); `puckworks/analysis/` (4); `tests/` (3); 30 files total

<a id="census-pw-286"></a>

##### PW #286 — SCI-MD-MASS-DELIVERY-005: two-assay predictor and audited inadequacy result

**UTC date / window:** 2026-09-27 / 30+60

**PR / merge SHA:** [#286](https://github.com/trbrewer/puckworks/pull/286) S `08027c10f25b`

**Primary / scientific subtype:** Science / New evaluation

**Alternative / mirror:** —

**Declaration metadata:** PR: NO-GOV

**Changed path groups:** `docs/analysis/sci_md_mass_delivery_005/` (19); `docs/` (2); `puckworks/analysis/` (2); 26 files total

<a id="census-pw-284"></a>

##### PW #284 — SCI-MD-MASS-DELIVERY-004: frozen empirical transfer fails C01 adequacy

**UTC date / window:** 2026-09-27 / 30+60

**PR / merge SHA:** [#284](https://github.com/trbrewer/puckworks/pull/284) S `5cc38629482a`

**Primary / scientific subtype:** Science / New evaluation

**Alternative / mirror:** —

**Declaration metadata:** PR: NO-GOV

**Changed path groups:** `docs/analysis/sci_md_mass_delivery_004/` (21); `docs/` (2); `puckworks/analysis/` (1); 25 files total

<a id="census-pw-282"></a>

##### PW #282 — SCI-MD-MASS-DELIVERY-003: single-anchor delivery implementation and negative result

**UTC date / window:** 2026-09-26 / 30+60

**PR / merge SHA:** [#282](https://github.com/trbrewer/puckworks/pull/282) S `5bdedcce8d6c`

**Primary / scientific subtype:** Science / New evaluation

**Alternative / mirror:** —

**Declaration metadata:** PR: NO-GOV

**Changed path groups:** `docs/analysis/sci_md_mass_delivery_003/` (16); `docs/` (2); `puckworks/analysis/` (2); 21 files total

<a id="census-pw-280"></a>

##### PW #280 — SCI-MD-MASS-DELIVERY-002: conditioning complexity not earned in source comparison

**UTC date / window:** 2026-09-26 / 30+60

**PR / merge SHA:** [#280](https://github.com/trbrewer/puckworks/pull/280) S `afe8205ab1f5`

**Primary / scientific subtype:** Science / New evaluation

**Alternative / mirror:** —

**Declaration metadata:** PR: NO-GOV

**Changed path groups:** `docs/analysis/sci_md_mass_delivery_002/` (21); `docs/` (2); `puckworks/analysis/` (2); 26 files total

<a id="census-pw-278"></a>

##### PW #278 — SCI-MD-MASS-DELIVERY-001: add research delivery; campaign adequacy condition-limited

**UTC date / window:** 2026-09-26 / 30+60

**PR / merge SHA:** [#278](https://github.com/trbrewer/puckworks/pull/278) S `69f9ef345329`

**Primary / scientific subtype:** Science / New evaluation

**Alternative / mirror:** —

**Declaration metadata:** PR: NO-GOV

**Changed path groups:** `docs/analysis/sci_md_mass_delivery_001/` (19); `docs/` (2); `puckworks/analysis/` (2); 24 files total

<a id="census-pw-276"></a>

##### PW #276 — SCI-MD-GRUDEVA-CLOCK-001: held-shot beverage-mass gain

**UTC date / window:** 2026-09-25 / 30+60

**PR / merge SHA:** [#276](https://github.com/trbrewer/puckworks/pull/276) M `85442cbc6341`

**Primary / scientific subtype:** Science / New evaluation

**Alternative / mirror:** —

**Declaration metadata:** PR: NO-GOV

**Changed path groups:** `docs/analysis/sci_md_grudeva_clock_001/` (17); `puckworks/analysis/` (1); `tests/` (1); 19 files total

<a id="census-pw-274"></a>

##### PW #274 — SCI-MD-MO-TRANSFER-001: conservative reference; source and numerical gates unresolved

**UTC date / window:** 2026-09-25 / 30+60

**PR / merge SHA:** [#274](https://github.com/trbrewer/puckworks/pull/274) S `09ee96b56220`

**Primary / scientific subtype:** Science / New evaluation

**Alternative / mirror:** Numerics

**Declaration metadata:** PR: NUMERICAL

**Changed path groups:** `docs/analysis/sci_md_mo_transfer_001/` (29); `puckworks/analysis/` (3); `tests/` (2); 35 files total

<a id="census-pw-272"></a>

##### PW #272 — SCI-MD-MORONEY-TRANSFER-001: execute conservative transfer; calibration inadequate

**UTC date / window:** 2026-09-25 / 30+60

**PR / merge SHA:** [#272](https://github.com/trbrewer/puckworks/pull/272) S `3ed109d60ffc`

**Primary / scientific subtype:** Science / New evaluation

**Alternative / mirror:** Numerics

**Declaration metadata:** file: NO-GOV, NUMERICAL

**Changed path groups:** `docs/analysis/sci_md_moroney_transfer_001/` (34); `puckworks/analysis/` (3); `tests/` (2); 41 files total

<a id="census-pw-270"></a>

##### PW #270 — SCI-MD-MAILLE-TRANSFER-001: audit unresolved replicate normalization

**UTC date / window:** 2026-09-24 / 30+60

**PR / merge SHA:** [#270](https://github.com/trbrewer/puckworks/pull/270) S `e95d4585aa2d`

**Primary / scientific subtype:** Science / Source qualification

**Alternative / mirror:** —

**Declaration metadata:** PR: NO-GOV

**Changed path groups:** `docs/analysis/sci_md_maille_transfer_001/` (3); `puckworks/analysis/` (1); `tests/` (1); 6 files total

<a id="census-pw-268"></a>

##### PW #268 — SCI-MD-SMRKE-TRANSFER-001: test endpoint transfer and incremental fines prediction

**UTC date / window:** 2026-09-24 / 30+60

**PR / merge SHA:** [#268](https://github.com/trbrewer/puckworks/pull/268) S `1648fa095f1a`

**Primary / scientific subtype:** Science / New evaluation

**Alternative / mirror:** —

**Declaration metadata:** PR: NO-GOV

**Changed path groups:** `docs/analysis/sci_md_smrke_transfer_001/` (21); `docs/` (2); `puckworks/analysis/` (1); 26 files total

<a id="census-pw-266"></a>

##### PW #266 — SCI-MD-RADIAL-OBS-001: reconstruct Pocket Science spent-puck assay

**UTC date / window:** 2026-09-24 / 30+60

**PR / merge SHA:** [#266](https://github.com/trbrewer/puckworks/pull/266) S `e786b7846a19`

**Primary / scientific subtype:** Science / Source qualification

**Alternative / mirror:** —

**Declaration metadata:** PR: NO-GOV

**Changed path groups:** `docs/insights/` (11); `docs/analysis/sci_md_radial_obs_001/` (6); `puckworks/data/` (4); 33 files total

<a id="census-pw-265"></a>

##### PW #265 — DATA-CORPUS-GUIDE-001: make external espresso evidence discoverable

**UTC date / window:** 2026-09-23 / 30+60

**PR / merge SHA:** [#265](https://github.com/trbrewer/puckworks/pull/265) S `518fb9c480db`

**Primary / scientific subtype:** Docs/status

**Alternative / mirror:** Assurance

**Declaration metadata:** PR: NO-GOV

**Changed path groups:** `tools/` (3); `docs/` (2); `docs/data/` (2); 14 files total

<a id="census-pw-263"></a>

##### PW #263 — EWP-RWB-001 reconciliation — gate pressure-bearing provenance and preserve schema-v6 data during enrichment

**UTC date / window:** 2026-09-01 / 60

**PR / merge SHA:** [#263](https://github.com/trbrewer/puckworks/pull/263) M `2058d0e947ee`

**Primary / scientific subtype:** Assurance

**Alternative / mirror:** Science

**Declaration metadata:** none found

**Changed path groups:** `puckworks/data/` (23); `docs/insights/` (8); `docs/` (2); 37 files total

<a id="census-pw-261"></a>

##### PW #261 — ESPRESSO-CORPUS-LEVERAGE-002-C1 — Integrate reviewed local-corpus authority

**UTC date / window:** 2026-08-31 / 60

**PR / merge SHA:** [#261](https://github.com/trbrewer/puckworks/pull/261) M `a3428a4d4ad5`

**Primary / scientific subtype:** Science / Source qualification

**Alternative / mirror:** Assurance

**Declaration metadata:** none found

**Changed path groups:** `puckworks/data/` (9); `docs/insights/` (8); `tools/` (3); 24 files total

<a id="census-pw-260"></a>

##### PW #260 — PANNUSCH-PRIOR-IMPACT-001 — Add enduring available-data register and preflight

**UTC date / window:** 2026-08-30 / 60

**PR / merge SHA:** [#260](https://github.com/trbrewer/puckworks/pull/260) M `7cf18d7bc388`

**Primary / scientific subtype:** Assurance

**Alternative / mirror:** —

**Declaration metadata:** none found

**Changed path groups:** `docs/` (3); `docs/data/` (2); `tests/` (2); 11 files total

<a id="census-pw-259"></a>

##### PW #259 — PANNUSCH-RAW-REPRO-001 — Source-faithful reconstruction and transfer eligibility

**UTC date / window:** 2026-08-30 / 60

**PR / merge SHA:** [#259](https://github.com/trbrewer/puckworks/pull/259) M `57f7e74eef92`

**Primary / scientific subtype:** Science / Source qualification

**Alternative / mirror:** Numerics

**Declaration metadata:** PR: NO-GOV

**Changed path groups:** `puckworks/data/` (21); `docs/insights/` (9); `docs/analysis/sci_md_007/` (2); 48 files total

<a id="census-pw-256"></a>

##### PW #256 — PW-PUB-001-C1: complete post-merge publishing safeguards

**UTC date / window:** 2026-08-28 / 60

**PR / merge SHA:** [#256](https://github.com/trbrewer/puckworks/pull/256) M `dfe0bdc76157`

**Primary / scientific subtype:** Product/UI

**Alternative / mirror:** —

**Declaration metadata:** none found

**Changed path groups:** `tools/publishing/` (4); `docs/publishing/` (3); `tests/publishing/` (2); 10 files total

<a id="census-pw-255"></a>

##### PW #255 — PW-PUB-001: implement publishing-system foundation

**UTC date / window:** 2026-08-28 / 60

**PR / merge SHA:** [#255](https://github.com/trbrewer/puckworks/pull/255) M `02b416eab263`

**Primary / scientific subtype:** Product/UI

**Alternative / mirror:** —

**Declaration metadata:** none found

**Changed path groups:** `tools/publishing/` (10); `docs/publishing/` (4); `.github/workflows/` (2); 25 files total

<a id="census-pw-254"></a>

##### PW #254 — SCI-ED-002 R2A: qualify the scientifically blocked protocol candidate

**UTC date / window:** 2026-08-27 / 60

**PR / merge SHA:** [#254](https://github.com/trbrewer/puckworks/pull/254) M `a67c5cd60189`

**Primary / scientific subtype:** Science / Source qualification

**Alternative / mirror:** Assurance

**Declaration metadata:** none found

**Changed path groups:** `docs/analysis/sci_ed_002/` (97); `tests/` (4); `tools/` (4); 108 files total

<a id="census-pw-252"></a>

##### PW #252 — SCI-MD-007: inventory evidence atlas and feasibility screen

**UTC date / window:** 2026-08-26 / 60

**PR / merge SHA:** [#252](https://github.com/trbrewer/puckworks/pull/252) M `9b92333b3dc6`

**Primary / scientific subtype:** Science / Source qualification

**Alternative / mirror:** —

**Declaration metadata:** file: NO-GOV

**Changed path groups:** `docs/analysis/sci_md_007/` (32); `docs/insights/` (11); `puckworks/data/` (10); 73 files total

<a id="census-pw-251"></a>

##### PW #251 — SCI-MD-004 Stage E0 R3 — freeze target-blind training bundle with silent QA

**UTC date / window:** 2026-08-24 / 60

**PR / merge SHA:** [#251](https://github.com/trbrewer/puckworks/pull/251) M `5ce003e751aa`

**Primary / scientific subtype:** Assurance

**Alternative / mirror:** —

**Declaration metadata:** file: NO-GOV

**Changed path groups:** `tests/` (20); `docs/analysis/sci_md_004_stage_e0/` (10); `tools/protected_target_qa/` (6); 54 files total

<a id="census-pw-246"></a>

##### PW #246 — SCI-MD-004 Stage A — multispecies data contract and protected Angeloni adapter

**UTC date / window:** 2026-08-23 / 60

**PR / merge SHA:** [#246](https://github.com/trbrewer/puckworks/pull/246) M `64b67a39801e`

**Primary / scientific subtype:** Science / Source qualification

**Alternative / mirror:** —

**Declaration metadata:** PR: NO-GOV

**Changed path groups:** `docs/analysis/sci_md_004/` (6); `puckworks/analysis/` (1); `tests/` (1); 8 files total

<a id="census-pw-244"></a>

##### PW #244 — science: implement RP-A-001 common-observable response atlas

**UTC date / window:** 2026-08-23 / 60

**PR / merge SHA:** [#244](https://github.com/trbrewer/puckworks/pull/244) M `378e4c8c094b`

**Primary / scientific subtype:** Science / New evaluation

**Alternative / mirror:** Assurance

**Declaration metadata:** none found

**Changed path groups:** `docs/analysis/rp_a_001/` (170); `puckworks/analysis/response_atlas/` (13); `tests/` (7); 194 files total


#### C.3.2 — EWP: all 63 integrations in 60 days

<a id="census-ewp-204"></a>

##### EWP #204 — docs: link the canonical October 9 threshold and capability review

**UTC date / window:** 2026-10-09 / 30+60

**PR / merge SHA:** [#204](https://github.com/trbrewer/espresso-whole-pull/pull/204) S `4284e9460c80`

**Primary / scientific subtype:** Docs/status

**Alternative / mirror:** —

**Declaration metadata:** PR: NO-GOV

**Changed path groups:** `docs/` (1); 1 files total

<a id="census-ewp-202"></a>

##### EWP #202 — ESPRESSO-DEVELOPMENT-GUIDE-001: link the canonical PW/EWP development guide

**UTC date / window:** 2026-10-07 / 30+60

**PR / merge SHA:** [#202](https://github.com/trbrewer/espresso-whole-pull/pull/202) S `16eec1dda24e`

**Primary / scientific subtype:** Docs/status

**Alternative / mirror:** —

**Declaration metadata:** PR: NO-GOV

**Changed path groups:** `docs/` (1); 1 files total

<a id="census-ewp-201"></a>

##### EWP #201 — Clarify R0 geometry, extraction limits and endpoint definitions

**UTC date / window:** 2026-09-30 / 30+60

**PR / merge SHA:** [#201](https://github.com/trbrewer/espresso-whole-pull/pull/201) S `73ec476ffe6a`

**Primary / scientific subtype:** Docs/status

**Alternative / mirror:** —

**Declaration metadata:** PR: NO-GOV

**Changed path groups:** `docs/` (2); `PACKAGE_QA_STATUS.json` (1); `SOURCE_PACKAGE_MANIFEST.json` (1); 4 files total

<a id="census-ewp-200"></a>

##### EWP #200 — SCI-MD-MASS-DELIVERY-008: consume frozen one-shot adaptation result

**UTC date / window:** 2026-09-27 / 30+60

**PR / merge SHA:** [#200](https://github.com/trbrewer/espresso-whole-pull/pull/200) S `f15a417cbf3c`

**Primary / scientific subtype:** Science / Retained only

**Alternative / mirror:** Docs/status; mirror

**Declaration metadata:** PR: NO-GOV

**Changed path groups:** `docs/analysis/sci_md_mass_delivery_008/` (5); `docs/` (2); `PACKAGE_QA_STATUS.json` (1); 14 files total

<a id="census-ewp-198"></a>

##### EWP #198 — SCI-MD-MASS-DELIVERY-007: exact consumer and inadequate frozen transfer result

**UTC date / window:** 2026-09-27 / 30+60

**PR / merge SHA:** [#198](https://github.com/trbrewer/espresso-whole-pull/pull/198) S `3f5ad6121f37`

**Primary / scientific subtype:** Science / Retained only

**Alternative / mirror:** Docs/status; mirror

**Declaration metadata:** PR: NO-GOV

**Changed path groups:** `docs/analysis/sci_md_mass_delivery_007/` (16); `docs/` (3); `PACKAGE_QA_STATUS.json` (1); 26 files total

<a id="census-ewp-196"></a>

##### EWP #196 — SCI-MD-CAFFEINE-DELIVERY-001: exact research consumer and bounded result

**UTC date / window:** 2026-09-27 / 30+60

**PR / merge SHA:** [#196](https://github.com/trbrewer/espresso-whole-pull/pull/196) S `022107a2d9e4`

**Primary / scientific subtype:** Science / Retained only

**Alternative / mirror:** Docs/status; mirror

**Declaration metadata:** PR: NO-GOV

**Changed path groups:** `docs/analysis/sci_md_caffeine_delivery_001/` (15); `PACKAGE_QA_STATUS.json` (1); `SOURCE_PACKAGE_MANIFEST.json` (1); 20 files total

<a id="census-ewp-194"></a>

##### EWP #194 — SCI-MD-MASS-DELIVERY-006: exact-pinned learned-tail research consumer

**UTC date / window:** 2026-09-27 / 30+60

**PR / merge SHA:** [#194](https://github.com/trbrewer/espresso-whole-pull/pull/194) S `ffb6638e1816`

**Primary / scientific subtype:** Science / Retained only

**Alternative / mirror:** Docs/status; mirror

**Declaration metadata:** PR: NO-GOV

**Changed path groups:** `docs/analysis/sci_md_mass_delivery_006/` (8); `docs/` (3); `PACKAGE_QA_STATUS.json` (1); 18 files total

<a id="census-ewp-192"></a>

##### EWP #192 — SCI-MD-MASS-DELIVERY-005: isolated consumer and negative research handoff

**UTC date / window:** 2026-09-27 / 30+60

**PR / merge SHA:** [#192](https://github.com/trbrewer/espresso-whole-pull/pull/192) S `3f5326443fd1`

**Primary / scientific subtype:** Science / Retained only

**Alternative / mirror:** Docs/status; mirror

**Declaration metadata:** PR: NO-GOV

**Changed path groups:** `docs/analysis/sci_md_mass_delivery_005/` (4); `docs/` (3); `PACKAGE_QA_STATUS.json` (1); 14 files total

<a id="census-ewp-190"></a>

##### EWP #190 — SCI-MD-MASS-DELIVERY-004: bind empirical transfer inadequacy

**UTC date / window:** 2026-09-27 / 30+60

**PR / merge SHA:** [#190](https://github.com/trbrewer/espresso-whole-pull/pull/190) S `2ea8d05dc917`

**Primary / scientific subtype:** Science / Retained only

**Alternative / mirror:** Docs/status; mirror

**Declaration metadata:** PR: NO-GOV

**Changed path groups:** `docs/analysis/sci_md_mass_delivery_004/` (4); `PACKAGE_QA_STATUS.json` (1); `SOURCE_PACKAGE_MANIFEST.json` (1); 10 files total

<a id="census-ewp-188"></a>

##### EWP #188 — SCI-MD-MASS-DELIVERY-003: pinned anchored-delivery consumer and negative result

**UTC date / window:** 2026-09-26 / 30+60

**PR / merge SHA:** [#188](https://github.com/trbrewer/espresso-whole-pull/pull/188) S `28451ffcc717`

**Primary / scientific subtype:** Science / Retained only

**Alternative / mirror:** Docs/status; mirror

**Declaration metadata:** PR: NO-GOV

**Changed path groups:** `docs/analysis/sci_md_mass_delivery_003/` (16); `docs/` (2); `PACKAGE_QA_STATUS.json` (1); 25 files total

<a id="census-ewp-186"></a>

##### EWP #186 — SCI-MD-MASS-DELIVERY-002: pinned consumer and negative conditioning result

**UTC date / window:** 2026-09-26 / 30+60

**PR / merge SHA:** [#186](https://github.com/trbrewer/espresso-whole-pull/pull/186) S `0900e9ac0651`

**Primary / scientific subtype:** Science / Retained only

**Alternative / mirror:** Docs/status; mirror

**Declaration metadata:** PR: NO-GOV

**Changed path groups:** `docs/analysis/sci_md_mass_delivery_002/` (9); `docs/` (2); `PACKAGE_QA_STATUS.json` (1); 17 files total

<a id="census-ewp-184"></a>

##### EWP #184 — SCI-MD-MASS-DELIVERY-001: add pinned research consumer and condition-limited result

**UTC date / window:** 2026-09-26 / 30+60

**PR / merge SHA:** [#184](https://github.com/trbrewer/espresso-whole-pull/pull/184) S `386cba18c421`

**Primary / scientific subtype:** Science / Retained only

**Alternative / mirror:** Docs/status; mirror

**Declaration metadata:** PR: NO-GOV

**Changed path groups:** `docs/analysis/sci_md_mass_delivery_001/` (4); `PACKAGE_QA_STATUS.json` (1); `SOURCE_PACKAGE_MANIFEST.json` (1); 10 files total

<a id="census-ewp-182"></a>

##### EWP #182 — SCI-MD-GRUDEVA-CLOCK-001: qualified mass-coordinate research handoff

**UTC date / window:** 2026-09-25 / 30+60

**PR / merge SHA:** [#182](https://github.com/trbrewer/espresso-whole-pull/pull/182) M `9b11bafddb2e`

**Primary / scientific subtype:** Science / Retained only

**Alternative / mirror:** Docs/status; mirror

**Declaration metadata:** PR: NO-GOV

**Changed path groups:** `docs/analysis/sci_md_grudeva_clock_001/` (3); `PACKAGE_QA_STATUS.json` (1); `SOURCE_PACKAGE_MANIFEST.json` (1); 7 files total

<a id="census-ewp-180"></a>

##### EWP #180 — SCI-MD-MO-TRANSFER-001: exact unresolved research handoff

**UTC date / window:** 2026-09-25 / 30+60

**PR / merge SHA:** [#180](https://github.com/trbrewer/espresso-whole-pull/pull/180) S `064d7a789412`

**Primary / scientific subtype:** Science / Retained only

**Alternative / mirror:** Docs/status; mirror

**Declaration metadata:** PR: NO-GOV

**Changed path groups:** `docs/analysis/sci_md_mo_transfer_001/` (3); `docs/` (2); `PACKAGE_QA_STATUS.json` (1); 9 files total

<a id="census-ewp-178"></a>

##### EWP #178 — SCI-MD-MORONEY-TRANSFER-001: consume calibration-inadequate result

**UTC date / window:** 2026-09-25 / 30+60

**PR / merge SHA:** [#178](https://github.com/trbrewer/espresso-whole-pull/pull/178) S `51ac2a0bc0d4`

**Primary / scientific subtype:** Science / Retained only

**Alternative / mirror:** Docs/status; mirror

**Declaration metadata:** PR: NO-GOV

**Changed path groups:** `docs/` (2); `docs/analysis/sci_md_moroney_transfer_001/` (2); `PACKAGE_QA_STATUS.json` (1); 8 files total

<a id="census-ewp-176"></a>

##### EWP #176 — SCI-MD-MAILLE-TRANSFER-001: hand off source-contract block

**UTC date / window:** 2026-09-24 / 30+60

**PR / merge SHA:** [#176](https://github.com/trbrewer/espresso-whole-pull/pull/176) S `09cdda7fb4b2`

**Primary / scientific subtype:** Science / Retained only

**Alternative / mirror:** Docs/status; mirror

**Declaration metadata:** PR: NO-GOV

**Changed path groups:** `docs/` (2); `docs/analysis/sci_md_maille_transfer_001/` (2); `PACKAGE_QA_STATUS.json` (1); 8 files total

<a id="census-ewp-174"></a>

##### EWP #174 — SCI-MD-SMRKE-TRANSFER-001: hand off endpoint rejection and no fines gain

**UTC date / window:** 2026-09-24 / 30+60

**PR / merge SHA:** [#174](https://github.com/trbrewer/espresso-whole-pull/pull/174) S `3ca164871cb4`

**Primary / scientific subtype:** Science / Retained only

**Alternative / mirror:** Docs/status; mirror

**Declaration metadata:** PR: NO-GOV

**Changed path groups:** `docs/analysis/sci_md_smrke_transfer_001/` (3); `PACKAGE_QA_STATUS.json` (1); `SOURCE_PACKAGE_MANIFEST.json` (1); 8 files total

<a id="census-ewp-172"></a>

##### EWP #172 — SCI-MD-RADIAL-OBS-001: conditional assay diagnostic on retained fields

**UTC date / window:** 2026-09-24 / 30+60

**PR / merge SHA:** [#172](https://github.com/trbrewer/espresso-whole-pull/pull/172) S `6a001b548345`

**Primary / scientific subtype:** Science / Retained only

**Alternative / mirror:** —

**Declaration metadata:** PR: NO-GOV

**Changed path groups:** `docs/analysis/sci_md_radial_obs_001/` (9); `tools/sci_md_radial_obs_001/` (3); `PACKAGE_QA_STATUS.json` (1); 19 files total

<a id="census-ewp-171"></a>

##### EWP #171 — SCI-MD-RHEOLOGY-011: distribution-preserving relocation, qualified delivery null

**UTC date / window:** 2026-09-24 / 30+60

**PR / merge SHA:** [#171](https://github.com/trbrewer/espresso-whole-pull/pull/171) S `8353125fac20`

**Primary / scientific subtype:** Numerics

**Alternative / mirror:** Science

**Declaration metadata:** PR: GEOMETRY/NO-GOV; file: NO-GOV

**Changed path groups:** `docs/analysis/sci_md_rheology_011/` (35); `tools/sci_md_rheology_011/` (11); `scripts/` (6); 56 files total

<a id="census-ewp-169"></a>

##### EWP #169 — SCI-MD-RHEOLOGY-010: matched-conductance reversal and E2 transfer

**UTC date / window:** 2026-09-23 / 30+60

**PR / merge SHA:** [#169](https://github.com/trbrewer/espresso-whole-pull/pull/169) S `63fd95ec1cdf`

**Primary / scientific subtype:** Science / New evaluation

**Alternative / mirror:** —

**Declaration metadata:** PR: SCENARIO

**Changed path groups:** `docs/analysis/sci_md_rheology_010/` (26); `tools/sci_md_rheology_010/` (8); `tests/` (2); 40 files total

<a id="census-ewp-167"></a>

##### EWP #167 — DATA-CORPUS-GUIDE-001: connect EWP to the inspected external collection

**UTC date / window:** 2026-09-23 / 30+60

**PR / merge SHA:** [#167](https://github.com/trbrewer/espresso-whole-pull/pull/167) S `cba79537e177`

**Primary / scientific subtype:** Docs/status

**Alternative / mirror:** —

**Declaration metadata:** PR: NO-GOV

**Changed path groups:** `docs/` (2); `AGENTS.md` (1); `PACKAGE_QA_STATUS.json` (1); 6 files total

<a id="census-ewp-166"></a>

##### EWP #166 — SCI-MD-RHEOLOGY-009: qualify pressure-history compatibility and E2 transfer

**UTC date / window:** 2026-09-23 / 30+60

**PR / merge SHA:** [#166](https://github.com/trbrewer/espresso-whole-pull/pull/166) S `dd05d3dd8dd8`

**Primary / scientific subtype:** Numerics

**Alternative / mirror:** Science

**Declaration metadata:** PR: NO-GOV; file: SCENARIO

**Changed path groups:** `docs/analysis/sci_md_rheology_009/` (28); `tools/sci_md_rheology_009/` (7); `scripts/` (4); 46 files total

<a id="census-ewp-164"></a>

##### EWP #164 — SCI-MD-RHEOLOGY-008: E2 passes the communicating radial reduction budgets

**UTC date / window:** 2026-09-22 / 30+60

**PR / merge SHA:** [#164](https://github.com/trbrewer/espresso-whole-pull/pull/164) S `3960b4a9c4b0`

**Primary / scientific subtype:** Science / New evaluation

**Alternative / mirror:** —

**Declaration metadata:** PR: SCENARIO

**Changed path groups:** `docs/analysis/sci_md_rheology_008/` (23); `tools/sci_md_rheology_008/` (9); `PACKAGE_QA_STATUS.json` (1); 37 files total

<a id="census-ewp-162"></a>

##### EWP #162 — SCI-MD-RHEOLOGY-007: test autonomous parallel paths against native radial coupling

**UTC date / window:** 2026-09-22 / 30+60

**PR / merge SHA:** [#162](https://github.com/trbrewer/espresso-whole-pull/pull/162) S `7bd046eb1697`

**Primary / scientific subtype:** Science / New evaluation

**Alternative / mirror:** —

**Declaration metadata:** PR: SCENARIO

**Changed path groups:** `docs/analysis/sci_md_rheology_007/` (18); `tools/sci_md_rheology_007/` (8); `PACKAGE_QA_STATUS.json` (1); 31 files total

<a id="census-ewp-160"></a>

##### EWP #160 — SCI-MD-RHEOLOGY-006: native radial viscosity coupling and flow allocation

**UTC date / window:** 2026-09-22 / 30+60

**PR / merge SHA:** [#160](https://github.com/trbrewer/espresso-whole-pull/pull/160) S `e5b3ef819f96`

**Primary / scientific subtype:** Physics

**Alternative / mirror:** —

**Declaration metadata:** PR: GOV

**Changed path groups:** `docs/analysis/sci_md_rheology_006/` (16); `tools/sci_md_rheology_006/` (9); `scripts/` (6); 38 files total

<a id="census-ewp-158"></a>

##### EWP #158 — SCI-MD-RHEOLOGY-005: test autonomous bulk-state viscosity against local coupling

**UTC date / window:** 2026-09-22 / 30+60

**PR / merge SHA:** [#158](https://github.com/trbrewer/espresso-whole-pull/pull/158) S `db705b644bbc`

**Primary / scientific subtype:** Physics

**Alternative / mirror:** —

**Declaration metadata:** PR: GOV

**Changed path groups:** `docs/analysis/sci_md_rheology_005/` (13); `tools/sci_md_rheology_005/` (7); `scripts/` (5); 34 files total

<a id="census-ewp-156"></a>

##### EWP #156 — SCI-MD-RHEOLOGY-004: compare aggregate delivery at matched output

**UTC date / window:** 2026-09-22 / 30+60

**PR / merge SHA:** [#156](https://github.com/trbrewer/espresso-whole-pull/pull/156) S `ab29a8052170`

**Primary / scientific subtype:** Science / New evaluation

**Alternative / mirror:** —

**Declaration metadata:** PR: SCENARIO

**Changed path groups:** `docs/analysis/sci_md_rheology_004/` (13); `tools/sci_md_rheology_004/` (6); `docs/` (2); 24 files total

<a id="census-ewp-154"></a>

##### EWP #154 — SCI-MD-RHEOLOGY-003: test hydraulic result across viscosity laws

**UTC date / window:** 2026-09-22 / 30+60

**PR / merge SHA:** [#154](https://github.com/trbrewer/espresso-whole-pull/pull/154) S `2542e2ea3925`

**Primary / scientific subtype:** Science / New evaluation

**Alternative / mirror:** —

**Declaration metadata:** PR: SCENARIO

**Changed path groups:** `docs/analysis/sci_md_rheology_003/` (15); `tools/sci_md_rheology_003/` (7); `docs/` (2); 27 files total

<a id="census-ewp-152"></a>

##### EWP #152 — SCI-MD-RHEOLOGY-002: native aggregate viscosity feedback and bounded result

**UTC date / window:** 2026-09-21 / 30+60

**PR / merge SHA:** [#152](https://github.com/trbrewer/espresso-whole-pull/pull/152) S `d40e0e64316d`

**Primary / scientific subtype:** Physics

**Alternative / mirror:** —

**Declaration metadata:** PR: GOV

**Changed path groups:** `docs/analysis/sci_md_rheology_002/` (12); `tools/sci_md_rheology_002/` (9); `scripts/` (4); 34 files total

<a id="census-ewp-150"></a>

##### EWP #150 — SCI-MD-RHEOLOGY-001: quantify EWP viscosity state dependence

**UTC date / window:** 2026-09-21 / 30+60

**PR / merge SHA:** [#150](https://github.com/trbrewer/espresso-whole-pull/pull/150) S `14fc4c8a4a94`

**Primary / scientific subtype:** Science / New evaluation

**Alternative / mirror:** —

**Declaration metadata:** file: SCENARIO

**Changed path groups:** `docs/analysis/sci_md_rheology_001/` (18); `scripts/` (3); `tools/sci_md_rheology_001/` (3); 30 files total

<a id="census-ewp-148"></a>

##### EWP #148 — VIS-EWP-RECORD-001: preserve private Visualizer work record

**UTC date / window:** 2026-09-05 / 60

**PR / merge SHA:** [#148](https://github.com/trbrewer/espresso-whole-pull/pull/148) M `ac49fe939f9e`

**Primary / scientific subtype:** Docs/status

**Alternative / mirror:** —

**Declaration metadata:** PR: NO-GOV

**Changed path groups:** `docs/analysis/data_leverage/` (3); `docs/` (2); `PACKAGE_QA_STATUS.json` (1); 8 files total

<a id="census-ewp-146"></a>

##### EWP #146 — XSV-PRESSURE-001: add native prescribed-pressure history

**UTC date / window:** 2026-09-05 / 60

**PR / merge SHA:** [#146](https://github.com/trbrewer/espresso-whole-pull/pull/146) M `73e3836f0ecd`

**Primary / scientific subtype:** Numerics

**Alternative / mirror:** Physics

**Declaration metadata:** PR: NO-GOV

**Changed path groups:** `validation/xsv_pressure_001/` (24); `scripts/` (6); `tests/` (5); 45 files total

<a id="census-ewp-144"></a>

##### EWP #144 — SCI-MD-012: diagnose and disposition E2C 13-bar root blocker

**UTC date / window:** 2026-09-04 / 60

**PR / merge SHA:** [#144](https://github.com/trbrewer/espresso-whole-pull/pull/144) M `d4a93971cd7a`

**Primary / scientific subtype:** Science / Retained only

**Alternative / mirror:** —

**Declaration metadata:** PR: NO-GOV

**Changed path groups:** `docs/analysis/sci_md_012/` (7); `tests/` (6); `docs/strategy/` (5); 32 files total

<a id="census-ewp-142"></a>

##### EWP #142 — SCI-MD-011: freeze high-pressure poroelastic closure adjudication

**UTC date / window:** 2026-09-03 / 60

**PR / merge SHA:** [#142](https://github.com/trbrewer/espresso-whole-pull/pull/142) M `6451cfe04ff1`

**Primary / scientific subtype:** Science / New evaluation

**Alternative / mirror:** —

**Declaration metadata:** PR: NO-GOV

**Changed path groups:** `docs/analysis/sci_md_011/` (33); `scripts/` (6); `tests/` (6); 62 files total

<a id="census-ewp-140"></a>

##### EWP #140 — SCI-MD-010 — Observable-first model utility and architecture audit

**UTC date / window:** 2026-09-03 / 60

**PR / merge SHA:** [#140](https://github.com/trbrewer/espresso-whole-pull/pull/140) M `375b19b96096`

**Primary / scientific subtype:** Science / New evaluation

**Alternative / mirror:** —

**Declaration metadata:** file: NO-GOV

**Changed path groups:** `docs/analysis/sci_md_010/` (38); `docs/strategy/` (5); `docs/` (4); 57 files total

<a id="census-ewp-138"></a>

##### EWP #138 — SCI-ED-003 — define minimum targeted closure contract

**UTC date / window:** 2026-09-02 / 60

**PR / merge SHA:** [#138](https://github.com/trbrewer/espresso-whole-pull/pull/138) M `f8bd4cc5c4c0`

**Primary / scientific subtype:** Science / Source qualification

**Alternative / mirror:** —

**Declaration metadata:** PR: NO-GOV

**Changed path groups:** `docs/analysis/sci_ed_003/` (13); `tests/` (6); `docs/strategy/` (5); 38 files total

<a id="census-ewp-136"></a>

##### EWP #136 — SCI-DATA-FUSION-001 — audited Phase B complementary result

**UTC date / window:** 2026-09-02 / 60

**PR / merge SHA:** [#136](https://github.com/trbrewer/espresso-whole-pull/pull/136) M `bd031c5acfbf`

**Primary / scientific subtype:** Science / Source qualification

**Alternative / mirror:** —

**Declaration metadata:** file: NO-GOV

**Changed path groups:** `docs/analysis/sci_data_fusion_001/` (32); `analysis/sci_data_fusion_001/` (23); `tests/` (5); 73 files total

<a id="census-ewp-134"></a>

##### EWP #134 — XSV-PANNUSCH-EWP-INPUT-MAPPING-001 — Pannusch-to-EWP input mapping qualification

**UTC date / window:** 2026-09-02 / 60

**PR / merge SHA:** [#134](https://github.com/trbrewer/espresso-whole-pull/pull/134) M `2bf996596bb7`

**Primary / scientific subtype:** Science / Source qualification

**Alternative / mirror:** —

**Declaration metadata:** PR: NO-GOV

**Changed path groups:** `docs/analysis/xsv_pannusch_ewp_input_mapping_001/` (8); `tests/` (4); `PACKAGE_QA_STATUS.json` (1); 19 files total

<a id="census-ewp-132"></a>

##### EWP #132 — SCI-MD-PANNUSCH-FLOW-HISTORY-001 source qualification

**UTC date / window:** 2026-09-02 / 60

**PR / merge SHA:** [#132](https://github.com/trbrewer/espresso-whole-pull/pull/132) M `7c79c8c6bf46`

**Primary / scientific subtype:** Science / New evaluation

**Alternative / mirror:** —

**Declaration metadata:** file: NO-GOV, SCENARIO

**Changed path groups:** `docs/analysis/sci_md_pannusch_flow_history_001/` (15); `analysis/sci_md_pannusch_flow_history_001/` (4); `tests/` (4); 33 files total

<a id="census-ewp-131"></a>

##### EWP #131 — OBS-PANNUSCH-FRACTION-WINDOW-001 — qualify source joins and test the Pannusch fraction-window observer

**UTC date / window:** 2026-09-01 / 60

**PR / merge SHA:** [#131](https://github.com/trbrewer/espresso-whole-pull/pull/131) M `c81a1e3af1e5`

**Primary / scientific subtype:** Science / New evaluation

**Alternative / mirror:** —

**Declaration metadata:** file: NO-GOV, SCENARIO

**Changed path groups:** `docs/analysis/obs_pannusch_fraction_window_001/` (14); `analysis/obs_pannusch_fraction_window_001/` (5); `tests/` (4); 35 files total

<a id="census-ewp-129"></a>

##### EWP #129 — EWP-REAL-WORLD-BOUNDARIES-001 — qualify recent-public operating boundaries and map porosity-conditioned EWP responses

**UTC date / window:** 2026-09-01 / 60

**PR / merge SHA:** [#129](https://github.com/trbrewer/espresso-whole-pull/pull/129) M `97d586fe21ca`

**Primary / scientific subtype:** Science / New evaluation

**Alternative / mirror:** —

**Declaration metadata:** file: SCENARIO

**Changed path groups:** `docs/analysis/ewp_real_world_boundaries_001/` (20); `analysis/ewp_real_world_boundaries_001/` (6); `tests/` (4); 42 files total

<a id="census-ewp-127"></a>

##### EWP #127 — EWP-POROSITY-PERMEABILITY-PRIOR-001 — qualify separate static hydraulic supports and execute bounded sensitivity

**UTC date / window:** 2026-09-01 / 60

**PR / merge SHA:** [#127](https://github.com/trbrewer/espresso-whole-pull/pull/127) M `34deac91170f`

**Primary / scientific subtype:** Science / New evaluation

**Alternative / mirror:** —

**Declaration metadata:** file: NO-GOV, SCENARIO

**Changed path groups:** `docs/analysis/ewp_porosity_permeability_prior_001/` (22); `analysis/ewp_porosity_permeability_prior_001/` (13); `tests/` (4); 49 files total

<a id="census-ewp-125"></a>

##### EWP #125 — XSV-WASZKIEWICZ-DYNAMIC-HYD-001 — Adoption-grade resistance comparison and final test-authority reconciliation

**UTC date / window:** 2026-08-31 / 60

**PR / merge SHA:** [#125](https://github.com/trbrewer/espresso-whole-pull/pull/125) M `9c7b8b286d7a`

**Primary / scientific subtype:** Science / New evaluation

**Alternative / mirror:** —

**Declaration metadata:** none found

**Changed path groups:** `docs/analysis/xsv_waszkiewicz_dynamic_hyd_001/` (46); `analysis/xsv_waszkiewicz_dynamic_hyd_001/` (8); `tests/` (6); 72 files total

<a id="census-ewp-123"></a>

##### EWP #123 — ESPRESSO-CORPUS-LEVERAGE-002-C1 — Integrate reviewed whole-corpus portfolio and Waszkiewicz handoff

**UTC date / window:** 2026-08-31 / 60

**PR / merge SHA:** [#123](https://github.com/trbrewer/espresso-whole-pull/pull/123) M `992eb00c297a`

**Primary / scientific subtype:** Science / Source qualification

**Alternative / mirror:** —

**Declaration metadata:** none found

**Changed path groups:** `docs/analysis/espresso_corpus_leverage_002/` (5); `docs/analysis/data_leverage/` (4); `tests/` (4); 28 files total

<a id="census-ewp-121"></a>

##### EWP #121 — XSV-PANNUSCH-MULTIMODEL-001 — Privilege-matched comparison of Pannusch fraction models

**UTC date / window:** 2026-08-31 / 60

**PR / merge SHA:** [#121](https://github.com/trbrewer/espresso-whole-pull/pull/121) M `36b68dc26703`

**Primary / scientific subtype:** Science / New evaluation

**Alternative / mirror:** —

**Declaration metadata:** none found

**Changed path groups:** `docs/analysis/xsv_pannusch_multimodel_001/` (29); `analysis/xsv_pannusch_multimodel_001/` (5); `docs/strategy/` (3); 44 files total

<a id="census-ewp-119"></a>

##### EWP #119 — PANNUSCH-PRIOR-IMPACT-001 / ESPRESSO-DATA-LEVERAGE-001 — Install available-data controls and model-advancement programme

**UTC date / window:** 2026-08-30 / 60

**PR / merge SHA:** [#119](https://github.com/trbrewer/espresso-whole-pull/pull/119) M `1519a0294eda`

**Primary / scientific subtype:** Assurance

**Alternative / mirror:** Science

**Declaration metadata:** none found

**Changed path groups:** `docs/analysis/pannusch_prior_impact_001/` (18); `docs/analysis/espresso_data_leverage_001/` (9); `docs/strategy/` (4); 47 files total

<a id="census-ewp-116"></a>

##### EWP #116 — Adopt data-first scientific development plan

**UTC date / window:** 2026-08-29 / 60

**PR / merge SHA:** [#116](https://github.com/trbrewer/espresso-whole-pull/pull/116) M `d1c4ea125fdd`

**Primary / scientific subtype:** Assurance

**Alternative / mirror:** —

**Declaration metadata:** PR: NO-GOV

**Changed path groups:** `docs/` (4); `docs/strategy/` (4); `tests/` (2); 15 files total

<a id="census-ewp-115"></a>

##### EWP #115 — SCI-MD-009-C1: terminal nonlinear-response qualification stop

**UTC date / window:** 2026-08-29 / 60

**PR / merge SHA:** [#115](https://github.com/trbrewer/espresso-whole-pull/pull/115) M `834820049a98`

**Primary / scientific subtype:** Science / New evaluation

**Alternative / mirror:** —

**Declaration metadata:** PR: NO-GOV

**Changed path groups:** `validation/sci_md_009/` (61); `tools/sci_md_009/` (6); `docs/` (2); 72 files total

<a id="census-ewp-114"></a>

##### EWP #114 — SCI-MD-008: prescribed-flow exact-fraction production reconstruction

**UTC date / window:** 2026-08-29 / 60

**PR / merge SHA:** [#114](https://github.com/trbrewer/espresso-whole-pull/pull/114) M `c33422204962`

**Primary / scientific subtype:** Science / New evaluation

**Alternative / mirror:** —

**Declaration metadata:** none found

**Changed path groups:** `validation/sci_md_008/` (22); `tools/sci_md_008/` (3); `docs/` (2); 30 files total

<a id="census-ewp-113"></a>

##### EWP #113 — XSV-FLOW-001: add discrete prescribed-flow boundary mode

**UTC date / window:** 2026-08-28 / 60

**PR / merge SHA:** [#113](https://github.com/trbrewer/espresso-whole-pull/pull/113) M `3874865e124d`

**Primary / scientific subtype:** Numerics

**Alternative / mirror:** —

**Declaration metadata:** PR: NUMERICAL

**Changed path groups:** `tools/xsv_flow_001/` (4); `solver/espressoWholePullFoam/` (2); `validation/xsv_flow_001/` (2); 15 files total

<a id="census-ewp-111"></a>

##### EWP #111 — Docs: reconcile final XSV-FRAC-001 merged status

**UTC date / window:** 2026-08-27 / 60

**PR / merge SHA:** [#111](https://github.com/trbrewer/espresso-whole-pull/pull/111) M `85190cf68cd8`

**Primary / scientific subtype:** Docs/status

**Alternative / mirror:** —

**Declaration metadata:** none found

**Changed path groups:** `validation/xsv_frac_001/` (2); `PACKAGE_QA_STATUS.json` (1); `SOURCE_PACKAGE_MANIFEST.json` (1); 7 files total

<a id="census-ewp-110"></a>

##### EWP #110 — XSV-FRAC-001: exact mass-defined multispecies cup fractions

**UTC date / window:** 2026-08-27 / 60

**PR / merge SHA:** [#110](https://github.com/trbrewer/espresso-whole-pull/pull/110) M `5b87d787aaf5`

**Primary / scientific subtype:** Numerics

**Alternative / mirror:** —

**Declaration metadata:** PR: NUMERICAL

**Changed path groups:** `tools/xsv_frac_001/` (6); `validation/xsv_frac_001/` (5); `validation/contracts/` (3); 24 files total

<a id="census-ewp-108"></a>

##### EWP #108 — SCI-ED-002 R2A: qualify the blocked measurement-contract consumer

**UTC date / window:** 2026-08-27 / 60

**PR / merge SHA:** [#108](https://github.com/trbrewer/espresso-whole-pull/pull/108) M `fc668afbeb77`

**Primary / scientific subtype:** Science / Source qualification

**Alternative / mirror:** —

**Declaration metadata:** none found

**Changed path groups:** `docs/validation/` (81); `tests/` (8); `scripts/` (3); 100 files total

<a id="census-ewp-106"></a>

##### EWP #106 — SCI-MD-007: consume locked inventory feasibility result

**UTC date / window:** 2026-08-26 / 60

**PR / merge SHA:** [#106](https://github.com/trbrewer/espresso-whole-pull/pull/106) M `f31330d2bfb0`

**Primary / scientific subtype:** Science / Retained only

**Alternative / mirror:** Docs/status; mirror

**Declaration metadata:** none found

**Changed path groups:** `docs/validation/` (10); `tests/` (2); `PACKAGE_QA_STATUS.json` (1); 18 files total

<a id="census-ewp-103"></a>

##### EWP #103 — SCI-MD-005 — evaluate production-consistent species-release mapping

**UTC date / window:** 2026-08-25 / 60

**PR / merge SHA:** [#103](https://github.com/trbrewer/espresso-whole-pull/pull/103) M `434c657fa35e`

**Primary / scientific subtype:** Science / New evaluation

**Alternative / mirror:** —

**Declaration metadata:** PR: NO-GOV

**Changed path groups:** `tools/sci_md_005/` (5); `validation/sci_md_005/` (5); `docs/` (2); 19 files total

<a id="census-ewp-101"></a>

##### EWP #101 — SCI-MD-004 Stage E1 — conditional hydraulic reconciliation and protected result

**UTC date / window:** 2026-08-25 / 60

**PR / merge SHA:** [#101](https://github.com/trbrewer/espresso-whole-pull/pull/101) M `3748703cfad8`

**Primary / scientific subtype:** Science / New evaluation

**Alternative / mirror:** —

**Declaration metadata:** PR: NO-GOV

**Changed path groups:** `validation/sci_md_004_stage_e1_hydraulic_reconciliation/` (284); `tools/` (3); `tests/` (2); 293 files total

<a id="census-ewp-99"></a>

##### EWP #99 — SCI-MD-004 Stage E1 — record protected multispecies holdout result

**UTC date / window:** 2026-08-25 / 60

**PR / merge SHA:** [#99](https://github.com/trbrewer/espresso-whole-pull/pull/99) M `2d719ca226a1`

**Primary / scientific subtype:** Science / New evaluation

**Alternative / mirror:** —

**Declaration metadata:** PR: NO-GOV

**Changed path groups:** `validation/sci_md_004_stage_e1/` (11); `tests/` (3); `tools/sci_md_004_stage_e1/` (3); 21 files total

<a id="census-ewp-97"></a>

##### EWP #97 — SCI-MD-004 Stage E0: freeze target-blind parameterization

**UTC date / window:** 2026-08-25 / 60

**PR / merge SHA:** [#97](https://github.com/trbrewer/espresso-whole-pull/pull/97) M `c50c9a6ab122`

**Primary / scientific subtype:** Science / Source qualification

**Alternative / mirror:** —

**Declaration metadata:** PR: NO-GOV

**Changed path groups:** `validation/sci_md_004_stage_e0/` (6); `tests/` (3); `AGENTS.md` (1); 17 files total

<a id="census-ewp-95"></a>

##### EWP #95 — SCI-MD-004 Stage C R2 — verified indexed passive-species transport

**UTC date / window:** 2026-08-24 / 60

**PR / merge SHA:** [#95](https://github.com/trbrewer/espresso-whole-pull/pull/95) M `78e5ff5aecd2`

**Primary / scientific subtype:** Physics

**Alternative / mirror:** —

**Declaration metadata:** none found

**Changed path groups:** `docs/validation/` (9); `tools/sci_md_004_stage_c/` (6); `docs/` (3); 28 files total

<a id="census-ewp-89"></a>

##### EWP #89 — SCI-MD-004 Stage A — multispecies contract and exact reduction design

**UTC date / window:** 2026-08-23 / 60

**PR / merge SHA:** [#89](https://github.com/trbrewer/espresso-whole-pull/pull/89) M `bf4de34310fc`

**Primary / scientific subtype:** Science / Source qualification

**Alternative / mirror:** —

**Declaration metadata:** PR: NO-GOV

**Changed path groups:** `tools/sci_md_004_contract/` (3); `docs/validation/` (2); `PACKAGE_QA_STATUS.json` (1); 10 files total

<a id="census-ewp-87"></a>

##### EWP #87 — science: add SCI-MD-003 atlas consumer

**UTC date / window:** 2026-08-23 / 60

**PR / merge SHA:** [#87](https://github.com/trbrewer/espresso-whole-pull/pull/87) M `0d2fa7595c44`

**Primary / scientific subtype:** Science / Retained only

**Alternative / mirror:** Docs/status; mirror

**Declaration metadata:** PR: NO-GOV

**Changed path groups:** `docs/analysis/sci_md_003/` (25); `tools/sci_md_003_atlas/` (3); `docs/` (2); 33 files total

<a id="census-ewp-71"></a>

##### EWP #71 — SCI-LC-001A: final accelerated closeout candidate

**UTC date / window:** 2026-08-20 / 60

**PR / merge SHA:** [#71](https://github.com/trbrewer/espresso-whole-pull/pull/71) M `73a7b184dacf`

**Primary / scientific subtype:** Science / New evaluation

**Alternative / mirror:** —

**Declaration metadata:** none found

**Changed path groups:** `docs/analysis/sci_lc_001a/` (13); `scripts/` (9); `tests/` (9); 48 files total

<a id="census-ewp-80"></a>

##### EWP #80 — SCI-ED-001: virtual pressure-program mechanism-discrimination screen

**UTC date / window:** 2026-08-20 / 60

**PR / merge SHA:** [#80](https://github.com/trbrewer/espresso-whole-pull/pull/80) M `9ac7bf88340b`

**Primary / scientific subtype:** Science / New evaluation

**Alternative / mirror:** —

**Declaration metadata:** none found

**Changed path groups:** `validation/cases/` (29); `docs/analysis/sci_ed_001/` (8); `scripts/` (3); 46 files total



Final root query at **2026-10-18T23:20:46Z** [X/R] found unchanged open-work membership: PW eight PRs/seventeen issues; EWP two PRs/three issues. The #321/#333 candidate identities and recorded update times also match the earlier snapshot. The original observation timestamps below remain preserved.

<a id="appendix-c-4"></a>

### C.4 — Complete open PR/issue snapshot and overlap map



These four saved open-state search snapshots each record **2026-10-18T22:13Z** as their observation time (minute precision). They include **8 PW PRs, 2 EWP PRs, 17 PW issues and 3 EWP issues**. Titles and URLs below are verbatim snapshot fields. “Open” means returned by the recorded open-state search; individual search rows do not supply usable creation/update/state fields, so no such timestamps or draft statuses are inferred here. Current candidate distinctions for #321/#333 and frozen #104 were subsequently rechecked by the principal reviewer, as reported in the main findings. Existing priority prefixes in titles are the issue authors’ labels, not this review’s priority judgments.

#### C.4.1 — PW pull requests

Snapshot: `2026-10-18T22:13Z`; recorded source `PW_open_prs.json`. Listing evidence `[D−]`; independently rechecked items are identified in the overlap map.

##### Open-work record 1 — #337

**Exact title:** ci: bump actions/download-artifact from 8.0.1 to 8.0.2

**URL:** [https://github.com/trbrewer/puckworks/pull/337](https://github.com/trbrewer/puckworks/pull/337)

##### Open-work record 2 — #336

**Exact title:** ci: bump actions/upload-artifact from 7.0.1 to 7.0.2

**URL:** [https://github.com/trbrewer/puckworks/pull/336](https://github.com/trbrewer/puckworks/pull/336)

##### Open-work record 3 — #333

**Exact title:** MODEL-GRUDEVA2026-010: accepted-state repeat verified; refinements blocked by payload mismatch

**URL:** [https://github.com/trbrewer/puckworks/pull/333](https://github.com/trbrewer/puckworks/pull/333)

##### Open-work record 4 — #264

**Exact title:** ci: bump actions/deploy-pages from 5.0.0 to 5.0.1

**URL:** [https://github.com/trbrewer/puckworks/pull/264](https://github.com/trbrewer/puckworks/pull/264)

##### Open-work record 5 — #321

**Exact title:** MODEL-PANNUSCH2024-COMMON-PAST-CONTRAST-007: joint bounds and checked witness repair

**URL:** [https://github.com/trbrewer/puckworks/pull/321](https://github.com/trbrewer/puckworks/pull/321)

##### Open-work record 6 — #257

**Exact title:** PW-PUB-002-R1: reader-first launch article and editorial reset

**URL:** [https://github.com/trbrewer/puckworks/pull/257](https://github.com/trbrewer/puckworks/pull/257)

##### Open-work record 7 — #129

**Exact title:** ci: bump actions/setup-python from 6.3.0 to 7.0.0

**URL:** [https://github.com/trbrewer/puckworks/pull/129](https://github.com/trbrewer/puckworks/pull/129)

##### Open-work record 8 — #128

**Exact title:** ci: bump actions/checkout from 7.0.0 to 7.0.1

**URL:** [https://github.com/trbrewer/puckworks/pull/128](https://github.com/trbrewer/puckworks/pull/128)


#### C.4.2 — EWP pull requests

Snapshot: `2026-10-18T22:13Z`; recorded source `EWP_open_prs.json`. Listing evidence `[D−]`; independently rechecked items are identified in the overlap map.

##### Open-work record 1 — #130

**Exact title:** Bump actions/upload-artifact from 6 to 7

**URL:** [https://github.com/trbrewer/espresso-whole-pull/pull/130](https://github.com/trbrewer/espresso-whole-pull/pull/130)

##### Open-work record 2 — #117

**Exact title:** Audit existing evidence before home-laboratory purchases

**URL:** [https://github.com/trbrewer/espresso-whole-pull/pull/117](https://github.com/trbrewer/espresso-whole-pull/pull/117)


#### C.4.3 — PW issues

Snapshot: `2026-10-18T22:13Z`; recorded source `PW_open_issues.json`. Listing evidence `[D−]`; independently rechecked items are identified in the overlap map.

##### Open-work record 1 — #48

**Exact title:** PV-19A: guided end-to-end espresso pull simulator

**URL:** [https://github.com/trbrewer/puckworks/issues/48](https://github.com/trbrewer/puckworks/issues/48)

##### Open-work record 2 — #313

**Exact title:** MODEL-PANNUSCH2024-TEMP-HISTORY-001: prescribed uniform temperature history

**URL:** [https://github.com/trbrewer/puckworks/issues/313](https://github.com/trbrewer/puckworks/issues/313)

##### Open-work record 3 — #311

**Exact title:** MODEL-FOSTER2025-POSTSAT-001: complete existing machine-mode headspace dynamics

**URL:** [https://github.com/trbrewer/puckworks/issues/311](https://github.com/trbrewer/puckworks/issues/311)

##### Open-work record 4 — #240

**Exact title:** Harden frozen protocol provenance across remaining Foundry screens

**URL:** [https://github.com/trbrewer/puckworks/issues/240](https://github.com/trbrewer/puckworks/issues/240)

##### Open-work record 5 — #67

**Exact title:** model: implement the Grudeva 2026 infiltration–extraction reduced solver

**URL:** [https://github.com/trbrewer/puckworks/issues/67](https://github.com/trbrewer/puckworks/issues/67)

##### Open-work record 6 — #231

**Exact title:** science: adjudicate de1_fixtureA first-drip evidence strength

**URL:** [https://github.com/trbrewer/puckworks/issues/231](https://github.com/trbrewer/puckworks/issues/231)

##### Open-work record 7 — #42

**Exact title:** P1: operate a recurring Puckworks literature, venue, and collaboration radar

**URL:** [https://github.com/trbrewer/puckworks/issues/42](https://github.com/trbrewer/puckworks/issues/42)

##### Open-work record 8 — #43

**Exact title:** P1: maintain one-click demos and cross-platform Puckworks accessibility

**URL:** [https://github.com/trbrewer/puckworks/issues/43](https://github.com/trbrewer/puckworks/issues/43)

##### Open-work record 9 — #70

**Exact title:** PV-19B: Guided Pull Laboratory — compare compatible models and expose the full component registry

**URL:** [https://github.com/trbrewer/puckworks/issues/70](https://github.com/trbrewer/puckworks/issues/70)

##### Open-work record 10 — #96

**Exact title:** Experimental data program: collect the measurements needed to test and extend Puckworks

**URL:** [https://github.com/trbrewer/puckworks/issues/96](https://github.com/trbrewer/puckworks/issues/96)

##### Open-work record 11 — #46

**Exact title:** P1 (standing): research intake + model/registry-impact review (private uploads + card/registry deltas)

**URL:** [https://github.com/trbrewer/puckworks/issues/46](https://github.com/trbrewer/puckworks/issues/46)

##### Open-work record 12 — #41

**Exact title:** P1: maintain a living, high-impact Puckworks repository homepage

**URL:** [https://github.com/trbrewer/puckworks/issues/41](https://github.com/trbrewer/puckworks/issues/41)

##### Open-work record 13 — #38

**Exact title:** P1 (future): release-bundle automation from one canonical build

**URL:** [https://github.com/trbrewer/puckworks/issues/38](https://github.com/trbrewer/puckworks/issues/38)

##### Open-work record 14 — #36

**Exact title:** P3: obtain a sanctioned immutable visualizer.coffee corpus export

**URL:** [https://github.com/trbrewer/puckworks/issues/36](https://github.com/trbrewer/puckworks/issues/36)

##### Open-work record 15 — #32

**Exact title:** P0: deliver one evidence-aware bundled-shot explanation bundle

**URL:** [https://github.com/trbrewer/puckworks/issues/32](https://github.com/trbrewer/puckworks/issues/32)

##### Open-work record 16 — #39

**Exact title:** P1 (future): harness characterization before decomposition

**URL:** [https://github.com/trbrewer/puckworks/issues/39](https://github.com/trbrewer/puckworks/issues/39)

##### Open-work record 17 — #37

**Exact title:** P2: add privacy-safe Visualizer operating-envelope context to product results

**URL:** [https://github.com/trbrewer/puckworks/issues/37](https://github.com/trbrewer/puckworks/issues/37)


#### C.4.4 — EWP issues

Snapshot: `2026-10-18T22:13Z`; recorded source `EWP_open_issues.json`. Listing evidence `[D−]`; independently rechecked items are identified in the overlap map.

##### Open-work record 1 — #104

**Exact title:** SCI-MD-006 — Nested shared-parameter versus species-specific production-law test

**URL:** [https://github.com/trbrewer/espresso-whole-pull/issues/104](https://github.com/trbrewer/espresso-whole-pull/issues/104)

##### Open-work record 2 — #76

**Exact title:** Post-merge SCI-MD administrative reconciliation and durability follow-up

**URL:** [https://github.com/trbrewer/espresso-whole-pull/issues/76](https://github.com/trbrewer/espresso-whole-pull/issues/76)

##### Open-work record 3 — #34

**Exact title:** WP03-001 — Saturated quasi-static poroelastic compaction

**URL:** [https://github.com/trbrewer/espresso-whole-pull/issues/34](https://github.com/trbrewer/espresso-whole-pull/issues/34)


#### C.4.5 — Consequences for recommendations

##### Open-work record 1 — PW #321 — [R] current candidate distinction

**Overlap and nonduplicate action:** Checked-witness repair and archive-only closeout are technically complete at bd976d2d4b7fc516c005765befedf5911a89ab2e; owner lifecycle disposition and any required current-base check remain. Historical prefix failure and transport cause stay unresolved. No repeat witness-repair campaign.

##### Open-work record 2 — PW #333 / issue #67 — [R] current incomplete qualification

**Overlap and nonduplicate action:** Accepted-state repeat and arbitrary-time/full-reference availability are distinct. Saved-payload mismatch blocks the required reconstruction/refinements. Reuse 004/008/009; do not re-create those completed comparisons or silently treat accepted-state agreement as full qualification.

##### Open-work record 3 — EWP #104 — [R] frozen contract distinction

**Overlap and nonduplicate action:** Existing SCI-MD-006 is a frozen nested shared-parameter versus species-specific test. A matched equilibrium-limit H1 comparator requires its own declared scope; #104 supplies no existing permission for that different comparison.

##### Open-work record 4 — EWP #76; PW #41/#48/#70 — [R/D−] status/navigation overlap

**Overlap and nonduplicate action:** Use the existing post-merge reconciliation and product/navigation owners to correct demonstrated current-facing lifecycle/permission/count fields. PW #324 pressure/source-disclosure work is complete; no new status system or duplicate disclosure task.

##### Open-work record 5 — EWP #117; PW #96/#36 — [D−] prior evidence/measurement planning

**Overlap and nonduplicate action:** The open evidence-before-purchases review includes Flair telemetry/first-drip and a same-lot initial/fraction/spent chain. Its older ABSENT Visualizer-store premise must be reconciled with later recovered holdings. Do not repeat broad corpus acquisition or purchase planning. SCI-ED-003 Stage F is chemistry/closure/metrology feasibility, distinct from T08 pressure-mechanism analysis.

##### Open-work record 6 — PW #311/#313 — [D−] completed implementation versus issue lifecycle

**Overlap and nonduplicate action:** Foster post-saturation and prescribed-temperature/history capabilities already exist. Open issue state does not establish absent implementation; check retained qualifications and finish any actual lifecycle item without rebuilding the capability.

##### Open-work record 7 — PW #231 — [D−] evidence-role correction

**Overlap and nonduplicate action:** First-drip evidence strength already has an issue. T06 should reuse that issue and the actual source/fit/observation contract, not create another empirical gate or claim independent validation.

##### Open-work record 8 — EWP #34 — [D−] existing native compaction

**Overlap and nonduplicate action:** Quasi-static compaction already exists, with the retained WP03 pressure-response limitations. Do not recommend pressure-dependent permeability as an absent mechanism merely because this issue remains open.

##### Open-work record 9 — PW #240/#39 — [D−] bounded assurance/characterization

**Overlap and nonduplicate action:** These are existing proposed hardening/characterization lanes. Respect the Paper 1 freeze and SCI-GOV circuit breakers; no speculative expansion follows from this review’s LOC counts.

##### Open-work record 10 — PW #32/#37/#43/#46 — [D−] existing product/intake context

**Overlap and nonduplicate action:** Explanation bundles, privacy-safe operating context, accessibility and source intake already have owners/items. Reuse them for a demonstrated reader/input problem; do not infer a new scientific experiment from their open status.

##### Open-work record 11 — PW #42/#38/#257 and dependency PRs — [D−] scope boundary

**Overlap and nonduplicate action:** Research radar, release/publishing work and dependency updates remain visible in the exhaustive snapshots/census but are outside the core scientific-priority judgment. Their presence does not measure governance labor.


<a id="appendix-c-5"></a>

### C.5 — Complete Oct 1 F1–F15 and Development Guide R1–R15 crosswalk



This is the complete delegated reconciliation after the independent view was frozen. **All 15 F identifiers and all 15 R identifiers are retained.** The principal reviewer has explicitly rechecked the census/static counts and the main-body claims concerning #335 acceptance, #321 technical completion, #333 incomplete qualification, #104’s distinct frozen scope, and #324’s completed disclosure. The broader row interpretations are conservatively `[D−/J]`; historical producer execution/statistics and original-review descriptions remain `[S]`. These labels prevent a delegated source read from being silently promoted to principal execution.

#### C.5.1 — Locator key

Repository prefixes resolve to the full pins at the top of this appendix. A task directory name denotes `docs/analysis/<directory>/` in the named repository. Line suffixes such as `:100–113` mean source lines, not a new result range. The following key resolves every abbreviated filename or document label used in the crosswalk; where a row supplies a full locator, it overrides this shorthand.

##### Crosswalk record 1 — Oct 1 / October 1 / Oct1

**Full pinned path or external receipt:** `PW:docs/research/ESPRESSO_PROGRAMME_REVIEW_2026-10-01.md@9dd456b`

**Relevant support:** F table L109–L125; remaining-action groups L662–L668

##### Crosswalk record 2 — Guide / Development Guide

**Full pinned path or external receipt:** `PW:docs/research/ESPRESSO_DEVELOPMENT_GUIDE.md@9dd456b`

**Relevant support:** R table L549–L565; metadata/lineage L61–L169

##### Crosswalk record 3 — _pull.py

**Full pinned path or external receipt:** `PW:puckworks/product/_pull.py@9dd456b`

**Relevant support:** Pressure/source disclosures L55–L83

##### Crosswalk record 4 — extraction_bdf.py

**Full pinned path or external receipt:** `PW:puckworks/models/cameron2020/extraction_bdf.py@9dd456b`

**Relevant support:** DOI L9; interpolation L100–L113; volume/ceiling L130–L147

##### Crosswalk record 5 — harness.py

**Full pinned path or external receipt:** `PW:puckworks/harness.py@9dd456b`

**Relevant support:** Comparator definition and interpretation L190–L231

##### Crosswalk record 6 — validation/gates.py / gates.py

**Full pinned path or external receipt:** `PW:puckworks/validation/gates.py@9dd456b`

**Relevant support:** Water-fraction conversion L1517–L1520 and L1655–L1671

##### Crosswalk record 7 — CLAUDE.md

**Full pinned path or external receipt:** `PW:CLAUDE.md@9dd456b`

**Relevant support:** Paper 1 freeze L86–L109

##### Crosswalk record 8 — SCI-GOV

**Full pinned path or external receipt:** `PW:docs/governance/MINIMUM_NECESSARY_GOVERNANCE_STANDARD.md@9dd456b`

**Relevant support:** Correction/reuse L208–L244; authorization L302; circuit breakers L304–L316

##### Crosswalk record 9 — EWP SCI-GOV copy

**Full pinned path or external receipt:** `EWP:docs/governance/MINIMUM_NECESSARY_GOVERNANCE_STANDARD.md@4284e94`

**Relevant support:** Same operative correction/reuse/circuit-breaker text

##### Crosswalk record 10 — current.json

**Full pinned path or external receipt:** `PW:docs/status/current.json@9dd456b`

**Relevant support:** Mixed permission/count L135–L136; lifecycle L465 and L495–L497

##### Crosswalk record 11 — CURRENT

**Full pinned path or external receipt:** `PW:docs/CURRENT.md@9dd456b`

**Relevant support:** Policy pointer L31–L35

##### Crosswalk record 12 — ONBOARDING

**Full pinned path or external receipt:** `PW:docs/ONBOARDING.md@9dd456b`

**Relevant support:** PV state L104–L108

##### Crosswalk record 13 — policy

**Full pinned path or external receipt:** `PW:docs/governance/DECISION_RESOLUTION_POLICY.md@9dd456b`

**Relevant support:** Proposed/pending header L3–L5

##### Crosswalk record 14 — PW README

**Full pinned path or external receipt:** `PW:README.md@9dd456b`

**Relevant support:** Current public capability/navigation; see main findings for exact audited rows

##### Crosswalk record 15 — EWP README

**Full pinned path or external receipt:** `EWP:README.md@4284e94`

**Relevant support:** Current research/scope L14–L48; provenance/comparison context L54–L103

##### Crosswalk record 16 — PROJECT_STATE

**Full pinned path or external receipt:** `EWP:docs/PROJECT_STATE.md@4284e94`

**Relevant support:** Prominent stale lifecycle entries L3–L19

##### Crosswalk record 17 — caffeine FINAL_REVIEW_ADDENDUM.json

**Full pinned path or external receipt:** `PW:docs/analysis/val_case_caffeine_decision_resolution_001/FINAL_REVIEW_ADDENDUM.json@9dd456b`

**Relevant support:** Bounded fallback repair L3–L17; actual reviewer/reuse L36–L43

##### Crosswalk record 18 — model_grudeva2026_bed_accuracy_004/RESULTS.md

**Full pinned path or external receipt:** `PW:docs/analysis/model_grudeva2026_bed_accuracy_004/RESULTS.md@9dd456b`

**Relevant support:** Disposition L3–L4; comparison L128–L146

##### Crosswalk record 19 — Grudeva 008

**Full pinned path or external receipt:** `PW:docs/analysis/model_grudeva2026_matched_comparison_008/RESULTS.md@9dd456b`

**Relevant support:** Complete matched retained-implementation comparison

##### Crosswalk record 20 — publication_reconciliation_009/RESULTS.md / 009

**Full pinned path or external receipt:** `PW:docs/analysis/model_grudeva2026_publication_reconciliation_009/RESULTS.md@9dd456b`

**Relevant support:** Disposition/panels L3–L25; Figure 5 limit L112

##### Crosswalk record 21 — sci_val_tamped_k_001/RESULT.md

**Full pinned path or external receipt:** `PW:docs/analysis/sci_val_tamped_k_001/RESULT.md@9dd456b`

**Relevant support:** Registered law plus input-adapter comparison

##### Crosswalk record 22 — ewp_porosity_permeability_prior_001

**Full pinned path or external receipt:** `EWP:docs/analysis/ewp_porosity_permeability_prior_001/RESULT.md@4284e94`

**Relevant support:** Source-conditioned porosity/permeability prior assessment

##### Crosswalk record 23 — sci_ed_003/RESULT.md

**Full pinned path or external receipt:** `EWP:docs/analysis/sci_ed_003/RESULT.md@4284e94`

**Relevant support:** Closure contract and Stage F/D boundary L5–L21

##### Crosswalk record 24 — SCI-ED-003 Stage F/D

**Full pinned path or external receipt:** `EWP:docs/analysis/sci_ed_003/MINIMUM_PROGRAMME.md@4284e94`

**Relevant support:** Chemistry/closure/context scope and separate conditional mechanisms L3–L31

##### Crosswalk record 25 — VISUALIZER_PRIVATE_WORK_RECORD.md

**Full pinned path or external receipt:** `EWP:docs/analysis/data_leverage/VISUALIZER_PRIVATE_WORK_RECORD.md@4284e94`

**Relevant support:** Prior empirical/native programme L63–L78

##### Crosswalk record 26 — RP-D-LC-001b

**Full pinned path or external receipt:** `PW:docs/ROADMAP.md@9dd456b`

**Relevant support:** Existing successor/navigation context; do not recreate from original invalid result

##### Crosswalk record 27 — PW #335 owner acceptance

**Full pinned path or external receipt:** [https://github.com/trbrewer/puckworks/pull/335#issuecomment-6192947145](https://github.com/trbrewer/puckworks/pull/335#issuecomment-6192947145)

**Relevant support:** Principal readback; merge 882584d110e1356091435ab8b002fb9abdd35ad6

##### Crosswalk record 28 — PW #321 completed candidate

**Full pinned path or external receipt:** [https://github.com/trbrewer/puckworks/pull/321](https://github.com/trbrewer/puckworks/pull/321)

**Relevant support:** bd976d2d4b7fc516c005765befedf5911a89ab2e; distinct from reviewed merged main

##### Crosswalk record 29 — PW #333 blocked candidate

**Full pinned path or external receipt:** [https://github.com/trbrewer/puckworks/pull/333](https://github.com/trbrewer/puckworks/pull/333)

**Relevant support:** Accepted-state repeat versus full-reference/integrity qualification

##### Crosswalk record 30 — EWP #104 / #117 / #76

**Full pinned path or external receipt:** [https://github.com/trbrewer/espresso-whole-pull](https://github.com/trbrewer/espresso-whole-pull)

**Relevant support:** Exact individual issue/PR URLs and titles in C.4


#### C.5.2 — Scope, authority and post-freeze correction

This section was prepared only after `census.md` froze this reviewer's independent Phase 2 view. Both repository documents were then read in full: `docs/research/ESPRESSO_PROGRAMME_REVIEW_2026-10-01.md` (706 lines) and `docs/research/ESPRESSO_DEVELOPMENT_GUIDE.md` (785 lines). Their earlier external original reviews were **not** directly available to this reviewer; their descriptions of those reviews remain secondary attribution. No original reviewer is invented or recast as a human. Both locators below are at PW `9dd456be7fd797b9cda0a2bbf50d1ac717d72835`; EWP locators are at `4284e9460c8057053e95de7cfa2fb3590e68e9db`.

Status concerns the concrete finding/action, not whether the physical model is validated. “Implemented” means the specified bounded correction/study/documentation exists. “Partly implemented” means a relevant subtask is complete while the named scientific question remains. “Obsolete” means that repeating the original proposal would duplicate work or rest on a refuted premise. A declined proposal can be obsolete without being implemented. `[S]` indicates the historical synthesis; `[D−]` a delegated primary-artifact interpretation not fully rechecked by the principal reviewer; `[X]` census/Git arithmetic re-executed by the principal reviewer; `[J]` assessment. These categories do not turn retained producer statistics into new execution.

**Post-freeze correction to the Phase 2 shorthand for #321:** the current live PR body reports the checked-witness repair and archive-only closeout **complete**, `ENGINEERING_CAPABILITY_VERIFIED`, on published candidate `bd976d2d4b7fc516c005765befedf5911a89ab2e`. Its reported Oct 6 state is `READY_FOR_OWNER_MERGE`, with no remaining candidate evidence-identity mismatch. The historical prefix failure and transport root cause remain unresolved and do not establish general execution reliability. Thus the needed next step is **owner lifecycle disposition and any current-base checks required for that candidate**, not another witness-repair campaign. This corrects “finish the existing witness repair” in the frozen notes without rewriting that historical snapshot. Current CI against Oct 18 main was not independently established by the Oct 6 PR-body receipt. #333 remains a different, genuinely incomplete full-qualification/integrity task.

#### C.5.3 — Oct 1 F1–F15: complete finding/action crosswalk

The exact historical dispositions are in Oct 1 review lines 109–125. These records reconcile them to current source and our independent observations rather than merely adopting the old review's headings.

##### Crosswalk record 1 — **F1 Cameron figure reproduction**

**Current implementation status:** **Partly implemented**: released-source sparse execution and N40 accounting completed; exact matched publication reproduction unresolved

**Is the finding/action correct, and do I agree?:** **Agree with the narrowed finding** of configuration-specific mismatch. Do not turn RMSE into a universal pointwise deficit or treat sparse Octave as MATLAB/source-figure equivalence.

**Controlling current evidence / consequence:** Current `PW:puckworks/product/_pull.py:L66-L73@9dd456b` explicitly retains both historical residuals with exact 20/40/5-bar configuration and limits. Oct 1 §§F/G, lines 415–637, bind completed sparse execution/accounting. Figure generator/parameter/dose clarification remains a distinct source question; no repeat runtime installation. `[D−/S/J]`

##### Crosswalk record 2 — **F2 raise inventory to repair Cameron**

**Current implementation status:** **Obsolete as a proposed repair**; normalization/accounting investigation implemented

**Is the finding/action correct, and do I agree?:** **Disagree with automatic inventory tuning**; agree on actual dry-dose EY and unresolved source density convention. The operative ceiling does not preclude ordinary observed yields.

**Controlling current evidence / consequence:** `PW:puckworks/models/cameron2020/extraction_bdf.py:L130-L147@9dd456b` separates implemented bed volume and actual-dose inventory ceiling; Oct 1:475–498 preserves source conventions. Adjusting `c_s0` to reduce a figure residual would be calibration, not a demonstrated correction. `[D−/S/J]`

##### Crosswalk record 3 — **F3 axial convergence / holdup explanation**

**Current implementation status:** **Implemented** for identifying and repairing the off-knot bookkeeping defect; source spatial refinement remains separate

**Is the finding/action correct, and do I agree?:** **Agree with revised attribution**, not the original holdup explanation. Published-source endpoint discretization deficit and PW F13 were distinct defects.

**Controlling current evidence / consequence:** Current `grind_microstructure`, `PW:puckworks/models/cameron2020/extraction_bdf.py:L100-L113@9dd456b`, derives both areas from interpolated phase/radius; Oct 1:129–146 and :500–637 preserve distinct source-scheme accounting. Do not reopen completed F13 as a missing holdup term. `[D−/S/J]`

##### Crosswalk record 4 — **F4 many gates are simple / evidence taxonomy**

**Current implementation status:** **Partly implemented**: complete counts and manual purpose categories exist; current review separately audits present gates

**Is the finding/action correct, and do I agree?:** **Agree that gate success needs purpose/exposure labels**, but not that simple analytical gates have little value or that counts are validations. Historical 65 comparisons do not automatically describe the present 66 registered gate refs.

**Controlling current evidence / consequence:** Current static AST census: 28 components, 79 functions, 66 registry refs and 13 quick-only; Oct 1:170–182 explicitly binds historical 65-category taxonomy to its old pin. The principal reviewer's independent present-gate sample governs current evidence conclusions. `[X/D−/S/J]`

##### Crosswalk record 5 — **F5 Cameron DOI**

**Current implementation status:** **Implemented**

**Is the finding/action correct, and do I agree?:** **Agree, corrected; no repeat action.**

**Controlling current evidence / consequence:** `PW:puckworks/models/cameron2020/extraction_bdf.py:L9@9dd456b` carries `10.1016/j.matt.2019.12.019`; PW #304 integration verified in full history. `[D−/X]`

##### Crosswalk record 6 — **F6 process is principal causal obstacle**

**Current implementation status:** **Obsolete as an established causal claim**; proportionate-governance policy is implemented

**Is the finding/action correct, and do I agree?:** **Causality not established.** The current census contains real governing/numerical/scientific work; labor is not observed. Historical Paper 1 overengineering is directly documented and already frozen.

**Controlling current evidence / consequence:** Census all 128 integrations; `PW:CLAUDE.md:L86-L109@9dd456b`; SCI-GOV §11:304–316. Preserve concrete circuit breakers, reject claims of measured labor share or process causality from counts. `[X/D−/J]`

##### Crosswalk record 7 — **F7 replace shallow R0 with ~19 mm**

**Current implementation status:** **Obsolete as a universal replacement**; geometry/source-prior assessment implemented

**Is the finding/action correct, and do I agree?:** **Agree with separating bulk/grain/storage definitions and source-specific sensitivities.** No source in this sub-review establishes a universal correct R0 material depth.

**Controlling current evidence / consequence:** Oct 1:221–239; existing EWP `ewp_porosity_permeability_prior_001` (also in EWP independent sample). A jointly qualified material/geometry/storage bridge would be new information; retuning depth by intuition is not. `[S/D−/J]`

##### Crosswalk record 8 — **F8 first-order EWP extraction is inferior / saturation cap**

**Current implementation status:** **Partly implemented**: native release/transport verification exists; intragrain diffusion remains absent from the scalar native branch

**Is the finding/action correct, and do I agree?:** **Agree with the missing-state description, disagree with automatic inferiority or a port mandate.** Release suppression is not a solved concentration hard cap, and numerical closure is not physical validation.

**Controlling current evidence / consequence:** Native source/agent audit controls current implementation; Oct 1:241–247 records coarse-step saturation overshoot with conservation. A new kinetics law needs a distinct observable and fair baseline. `[S/D−/J]`

##### Crosswalk record 9 — **F9 EWP has no data comparisons / too expensive mesh**

**Current implementation status:** **Obsolete as an absence claim**; numerical and data comparisons implemented, physical validation incomplete

**Is the finding/action correct, and do I agree?:** **Disagree with no-comparisons claim; agree with limitations.** Converged wrong WP03 ordering is substantive negative evidence. Mesh count alone establishes neither effort nor spatial adequacy.

**Controlling current evidence / consequence:** EWP `README.md:14–33,75–103` distinguishes implemented source comparisons, calibration and no physical validation; native/physics review covers WP03 and selected rheology studies. `[D−/J]`

##### Crosswalk record 10 — **F10 physics navigation consumes most of a day**

**Current implementation status:** **Partly implemented**: synthesis/guide/README navigation added; current lifecycle drift persists

**Is the finding/action correct, and do I agree?:** **Agree on concrete navigation improvements; elapsed effort claim unmeasured.** Additive historical guidance has not kept current-status fields synchronized.

**Controlling current evidence / consequence:** PW guide/CURRENT/README and EWP README exist; current.json:135–136,465,495–497 and EWP PROJECT_STATE:3–19 supply bounded stale claims. Correct existing sources, not create another guide. `[D−/X/J]`

##### Crosswalk record 11 — **F11 programme never tests a registered component**

**Current implementation status:** **Obsolete/refuted claim**; registered Wadsworth law plus adapter comparison implemented

**Is the finding/action correct, and do I agree?:** **Agree with the Oct 1 refutation.** Law-plus-adapter inadequacy does not isolate native law from input-proxy error.

**Controlling current evidence / consequence:** `PW:docs/analysis/sci_val_tamped_k_001/RESULT.md@9dd456b` and Oct 1:327–331. The main report's data/component audit supplies current quantitative replay; no duplicate comparison. `[D−/S/J]`

##### Crosswalk record 12 — **F12 remove hashes to unblock corrections**

**Current implementation status:** **Implemented** as the alternative separation of historical identity from current reducer behavior

**Is the finding/action correct, and do I agree?:** **Agree with scoped separation; disagree with removing identity controls wholesale.** Current caffeine bounded addendum is a concrete functioning example of unchanged-science reuse.

**Controlling current evidence / consequence:** Oct 1:79–88 records source-identity/current-reducer split and authorship correction. Caffeine `PW:docs/analysis/val_case_caffeine_decision_resolution_001/FINAL_REVIEW_ADDENDUM.json:L3-L17,L36-L43@9dd456b` limits repair to missing public fallback, reuses reviewed scientific hashes and runs affected checks. `[D−/S/J]`

##### Crosswalk record 13 — **F13 phase/radius/area inventory inconsistency**

**Current implementation status:** **Implemented**

**Is the finding/action correct, and do I agree?:** **Agree; correction survives in current source.** Physical inventory consistency is a meaningful invariant, not mere assurance overhead.

**Controlling current evidence / consequence:** `PW:puckworks/models/cameron2020/extraction_bdf.py:L100-L113@9dd456b`; PW #304 `15479363ab3bcd879364628a1938879f2db8c05c`. Current definition is algebraically `b_i*a_i/3=phi_i`. No repeat repair. `[D−/X/J]`

##### Crosswalk record 14 — **F14 flexible comparator actually tested constant / H1 overreach**

**Current implementation status:** **Implemented** for comparator and interpretation; mechanistic H1 discrimination remains open

**Is the finding/action correct, and do I agree?:** **Agree.** An empirical time-varying fit versus a constant tests time variation; comparing against the actual cubic remains required. Early maxima do not identify instantaneous equilibration.

**Controlling current evidence / consequence:** `PW:puckworks/harness.py:L190-L231@9dd456b` computes the cubic and compares it explicitly; retained readout says kinetics are not identified by this coupling. Do not count later endpoint sensitivity addenda as a kinetic identification experiment. `[D−/J]`

##### Crosswalk record 15 — **F15 wrong fraction basis in viscosity conversion**

**Current implementation status:** **Implemented**

**Is the finding/action correct, and do I agree?:** **Agree; current passing ordering gate alone would not prove units correct.** Correct conversion survives.

**Controlling current evidence / consequence:** `PW:puckworks/validation/gates.py:L1517-L1520,L1655-L1671@9dd456b` uses water fraction `1-dry_solids_fraction` for Telis-Romero density. PW #304 verified in integration census. `[D−/X/J]`


#### C.5.4 — Oct 1 remaining-action groups (§H:662–668)

##### Crosswalk record 1 — Runtime/source execution, F13/F14/F15 repair, C01 arithmetic reconstruction, N40 signed-budget attribution

**Current status / assessment:** **Implemented.** Repetition is not a new recommendation. Our review does not relabel aggregate-only retained evidence as full raw trajectory replay.

##### Crosswalk record 2 — Exact Fig. 5 generator/parameters and dose convention

**Current status / assessment:** **Not started as a newly qualified source resolution in the inspected post-Oct 1 main history.** Disclosure is now implemented by #324; original reproduction question remains. No retune follows.

##### Crosswalk record 3 — R0 material geometry and separately qualified storage

**Current status / assessment:** **Partly implemented** through prior/source sensitivities; measured same-material R0 bridge not established. No universal 19-mm replacement.

##### Crosswalk record 4 — C01 synchronized clocks, primed samples, flow/recovery joins and analytical convention

**Current status / assessment:** **Partly implemented**: reconstruction and explicit gap inventory exist; source-authorized mechanistic bridge/complete closure still not established. The main report's data review controls any new source result. Do not recreate the completed assay arithmetic or treat exposed records as blind.

##### Crosswalk record 5 — Matched H1 discrimination

**Current status / assessment:** **Not started as a qualifying independent mechanistic discrimination in this review's identified changes.** New conditional prediction/sensitivity evidence is useful but not an equilibrium proof.

##### Crosswalk record 6 — Cameron spatial sensitivity/source-scheme repair

**Current status / assessment:** **Not started as a new source-scheme refinement/repair in the inspected post-Oct 1 census.** Existing PW numerical qualifications remain; do not conflate source and PW discretizations or authorize repair without a named decision.


#### C.5.5 — Development Guide R1–R15: complete action crosswalk

Original recommendation headings/dispositions are at Guide:549–565. The guide is explicitly dated Oct 6 and calls its rows historical (lines 3–11), so superseded recommendations are **history**, not necessarily a current false claim. Its current-facing pointers should lead readers to later status. Do not edit historical outcomes to make them appear prospectively predicted.

##### Crosswalk record 1 — **R1 Disclose and gate Cameron offset**

**Status at current pins:** **Implemented in the revised, bounded form** via PW #324; original new empirical gate not adopted

**Correctness, agreement and present action:** **Agree with disclosure; disagree with an arbitrary gate or output correction.** `PW:puckworks/product/_pull.py:L66-L73@9dd456b` now states exact historical reference configuration, source/experimental residual distinction, nonhuman provenance and no per-recipe error bar. Do not recommend that completed disclosure again. `[D−/S/J]`

##### Crosswalk record 2 — **R2 Fix pressure evidence range/scaling**

**Status at current pins:** **Implemented in the revised disclosure form** via #324; pressure/scaling numerics preserved

**Correctness, agreement and present action:** **Agree.** `PW:puckworks/product/_pull.py:L55-L65,L74-L83@9dd456b` explicitly separates prescribed model overpressure, SI5/main6 ambiguity, model exploration, product admission and physical qualification. No universal one-bar conversion or hydraulic substitution is justified. Remains a scientific source question, not an unimplemented label fix. `[D−/S/J]`

##### Crosswalk record 3 — **R3 Resolve Grudeva ~2.2 factor**

**Status at current pins:** **Partly implemented; original factor repair and 003-era next step obsolete**

**Correctness, agreement and present action:** **Agree with refusing a multiplier repair.** `PW:docs/analysis/model_grudeva2026_bed_accuracy_004/RESULTS.md:L3-L4,L128-L146@9dd456b` reports numerical bed qualification; 008 compares matched implementations; `PW:docs/analysis/model_grudeva2026_publication_reconciliation_009/RESULTS.md:L3-L25@9dd456b` reports corroborated publication discrepancy. Figure5 remains incomplete (009:112). Open **#333** is the current 010 repeat/full-reference qualification task, still blocked by saved-payload integrity mismatch. Disposition the existing task within its retained integrity restrictions; no automatic retry, arbitrary-time reconstruction, refinement, duplicate re-extraction, 004 or 008/009 campaign. `[D−/S/J]`

##### Crosswalk record 4 — **R4 Report gates by evidence tier**

**Status at current pins:** **Partly implemented** through existing cards, guide, census and explicit evidence distinctions

**Correctness, agreement and present action:** **Agree with purpose/exposure reporting, not a new mandatory schema.** Historical numerical/reference/data/self-consistency predicates need separate interpretation. Current static/selected-gate audit is sufficient for this review; extending registry infrastructure should require a concrete product or scientific decision. `[D−/S/J]`

##### Crosswalk record 5 — **R5 Close SCI-MD and write synthesis**

**Status at current pins:** **Implemented in the revised synthesis/scoped-closure form**

**Correctness, agreement and present action:** **Agree with preserving completed decisions and reopening only on a new substantive premise; disagree with blanket archival.** Oct1 synthesis, guide and later retained uncertainty/decision-resolution addenda exist. Smrke has robust negative tested-form gain; trigonelline and empirical mappings supply positive bounded counterexamples to “all negative.” `[D−/S/J]`

##### Crosswalk record 6 — **R6 Open EWP governing-physics window judged by WP03**

**Status at current pins:** **Obsolete as specified**

**Correctness, agreement and present action:** **Agree with the guide's replacement.** Native pressure-dependent permeability already exists; E2C is retired by SCI-MD-012. Intragrain chemistry and hydraulic change need distinct observables and controls. The current 30-day EWP census also includes three governing-physics-primary changes; the blanket premise that no physics work can occur is false. No automatic diffusion/Waszkiewicz port. `[X/D−/J]`

##### Crosswalk record 7 — **R7 Nothing else in EWP until R6**

**Status at current pins:** **Implemented as bounded sequencing; original total freeze obsolete**

**Correctness, agreement and present action:** **Agree with isolating mechanism questions and preserving closed decisions, disagree with an indefinite repository freeze.** Current data-first three-test gate and explicit no-successor dispositions already provide sequencing. New source/numerical capability work can be useful under a different qualified question. `[D−/S/J]`

##### Crosswalk record 8 — **R8 Run EXP-001/EXP-003 personally**

**Status at current pins:** **Not started as execution; staged design/preflight partly implemented**

**Correctness, agreement and present action:** **Agree with deferral until a named missing observable changes a decision.** EWP `EWP:docs/analysis/sci_ed_003/RESULT.md:L5-L21@4284e94` defines M01 plus contextual M02 and preserves StageF/D unauthorised; it records no lab observations. Existing **#117** already audits evidence before purchases and must be reconciled to recovered holdings, not duplicated. Ownership of data is not the criterion for independent validation. `[D−/S/J]`

##### Crosswalk record 9 — **R9 Visualizer for hydraulics only**

**Status at current pins:** **Implemented in substantial source-qualified empirical/native work; proposed new pooled law inference obsolete**

**Correctness, agreement and present action:** **Agree that descriptive/matched hydraulics can be useful without chemistry; disagree with treating corpus pressure slopes as material constitutive laws.** `EWP:docs/analysis/data_leverage/VISUALIZER_PRIVATE_WORK_RECORD.md:L63-L78@4284e94` records 6,655 observations across 213 repeated cohorts, prior empirical tests and 120+28 native runs (retained producer reports, not this review's executions). Controller/sensor/flow semantics remain unresolved. This is not a new unused corpus or untouched cohort. `[D−/S/J]`

##### Crosswalk record 10 — **R10 Move research outside importable package**

**Status at current pins:** **Not started; deliberately deferred**

**Correctness, agreement and present action:** **Agree with deferral.** Analysis remains importable (132 PW code files in our path census), with real consumer APIs and an explicitly retained EWP runtime pin. No demonstrated incompatibility/performance problem justifies moving modules. Do not recommend package churn from LOC ratios. `[X/D−/J]`

##### Crosswalk record 11 — **R11 Prune branches / consolidate status**

**Status at current pins:** **Partly implemented**: guide/navigation exists; precise stale current-facing rows remain

**Correctness, agreement and present action:** **Agree with bounded status reconciliation; no branch quota/deletion request.** PW current.json:135–136,465,495–497; ONBOARDING:104–108; CURRENT:31–35; policy:3–5. EWP PROJECT_STATE:3–19. Existing **EWP #76** already owns post-merge reconciliation. The principal reviewer independently verified #335 owner acceptance in GitHub comment6192947145 and merge882584d, so both merge and acceptance-pending language may be updated; preserve the historical proposal ID/receipts. `[D−/S/J]`

##### Crosswalk record 12 — **R12 Rewrite EWP README around physics**

**Status at current pins:** **Partly implemented / bounded staged version implemented**

**Correctness, agreement and present action:** **Agree with concise source-to-observable explanations, not a sprawling rewrite.** Current README:35–48 describes native scope, missing mechanisms and claim limits; :14–33 gives current research/adoption ceiling; :54–103 links provenance and data comparisons. Remaining lifecycle drift is in PROJECT_STATE; fix that existing source instead of rewriting the README again. `[D−/S/J]`

##### Crosswalk record 13 — **R13 Rebalance tests**

**Status at current pins:** **Implemented as existing risk-based/reuse policy; quota proposal obsolete**

**Correctness, agreement and present action:** **Agree with meaningful analytical/numerical/empirical tests by claim, disagree with a 40%-file target or mandatory new measurement gate for every function.** SCI-GOV:208–244 and304–316 already call for bounded repairs and no repeated unchanged-science review. Foster cached-oracle defect was material; caffeine fallback repair reused unchanged science. Static LOC cannot establish governance time. `[D−/S/J]`

##### Crosswalk record 14 — **R14 Standing execution envelope**

**Status at current pins:** **Not started as universal delegated authority; bounded task authorization exists**

**Correctness, agreement and present action:** **Agree that a genuinely owner-granted scope can reduce repetitive prompting; no evidence here supports silently expanding into StageF/D or a new native campaign.** SCI-GOV:302 says authorization should not restate normal commands/rules, already reducing ceremony. Current #333/#321 work has specific scope; use it instead of creating new permission ladders. `[D−/S/J]`

##### Crosswalk record 15 — **R15 Require discriminating dataset before any analysis**

**Status at current pins:** **Implemented in the corrected oracle/nonduplication form**

**Correctness, agreement and present action:** **Agree with a discriminating oracle and possible decision change; disagree with requiring new empirical data for numerical corrections.** Foster's analytical source equations and independent numerical oracle were sufficient to repair a real defect. New scenarios can distinguish representations without constituting physical validation. Existing EWP three-test gate is adequate policy; do not add another register. `[D−/S/J]`


#### C.5.6 — Consequences for the current recommendation register

1. **Remove completed R1/R2 disclosure work and R3's 003/figure-re-extraction proposals from the next-work list.** Credit #324 and 004/008/009 explicitly. Do not reopen F13/F14/F15, prior Visualizer corpus-wide work, C01 arithmetic or RP-D-LC-001b.
2. **Use a P2 bounded status correction under existing owners/issue #76.** The independent Phase2 wording “P1/P2” is resolved here to P2: these are current-facing documentation/lifecycle defects; no observed code path was shown to execute the wrong science because of them. Some falsely imply current permission blockers or occupy finished queue slots, so they deserve repair, but no new framework.
3. **Keep #333 and #321 as the actual existing tasks, with different dispositions.** #333 retains an incomplete numerical/integrity result; #321's repaired candidate reports bounded engineering qualification and awaits lifecycle disposition (plus any necessary current-base check), not repeated witness repair. Neither should generate an automatic successor or duplicate task ID.
4. **Disposition #117 against recovered evidence, then let the named remaining metrology/observer gap determine any acquisition request.** An inaccessible source in this environment is not absent data. No blanket “collect your own data” or “the corpus is exhausted” recommendation follows.
5. **Keep proportionate governance while documenting concrete outcomes.** The sampled modern controls caught source/oracle/integrity errors and sometimes only reporting defects; observed scoped reuse was successful. No time-ratio or causal conclusion is justified by the exhaustive activity/LOC census.

#### C.5.7 — Reconciliation limits

This is not a fresh Octave/OpenFOAM, protected-target or raw-private-data replay. The main report's current physics, source/data and safe numerical executions control any stronger scientific conclusions. The old external O/S reviews remain indirectly attributed through the guide. All 128 integration classifications have explicit alternatives and retained-output subtypes, so numerical capabilities and new scenario integrations are not erased by a “NO_GOVERNING_PHYSICS_CHANGE” declaration. Branch counts and elapsed reviewer time were not measured as causal evidence.


<a id="appendix-d"></a>

## Appendix D — Status-token and model-token glossary

[Back to navigation](#review-navigation)

These translations preserve the repository namespace; none authorizes execution or adoption.

| Token / namespace | Meaning in this report |
| --- | --- |
| PW PASS | The named gate’s declared predicate passed; inspect its evidence rung and support. |
| PW ACKNOWLEDGED_EXCEPTION | A registered component intentionally has no registry gates; not an extra numerical validation. |
| EWP NOT_VALIDATED / PHYSICAL_VALIDATION=NOT_ESTABLISHED | The whole solver has no established independent physical-validation claim for the stated use. |
| R0 numerically qualified | The immutable declared reference passed its bounded historical numerical qualification, not every later option. |
| OWNER_DECISION_PENDING | The named owner choice remains open; analysis/results do not supply execution permission. |
| PREDICTIVE_RANKING_ONLY | Comparison ranks model losses; no practical-accuracy acceptance margin is thereby defined. |
| SOURCE_SUPPORT_INCOMPLETE | Original required support is missing; available subsets remain diagnostics. |
| NUMERICALLY_UNRESOLVED / UNRESOLVED | A stated numerical/precision requirement cannot decide the declared question; resolve the exact task namespace. |
| LEARNED_TWO_ASSAY_MAPPING_EARNED | MASS006 passes all original conditional-prediction axes; supplied chemistry and mass remain inputs. |
| FROZEN_CONDITIONAL_TRANSFER_INADEQUATE_ON_DECLARED_COHORT | MASS007 fails its stated transfer adequacy, despite descriptive improvements. |
| ADAPTATION_ADEQUATE_INCREMENT_NOT_ESTABLISHED | MASS008 A2 passes its adaptation adequacy but does not pass every complexity increment. |
| MATERIAL_MODELED_DELIVERY_CONTRAST | A qualified difference between computational rheology variants; not a measured espresso effect. |
| ENGINEERING_CAPABILITY_VERIFIED / READY_FOR_OWNER_MERGE | #321’s recorded bounded engineering completion and lifecycle readiness; not fresh CI at every later base. |
| E2 in SCI-MD-010 | The full native solver family; do not equate it with the reduced rheology model. |
| E2 in RHEOLOGY008–011 | A reduced two-radial-cell representation per axial station, not two global lumped states. |
| E2C in SCI-MD-010/011/012 | Finite-porosity component curve with incomplete required pressure predictions and retired current priority. |
| B0 / B1 / E1 / P1 | Pressure training mean / empirical quadratic / lumped Darcy / universal poroelastic component. |
| C0/C1/C2; F2/A0/A2/M | Task-local mass predictors; definitions and conditioning differ across transfer/adaptation tasks. |
| D0/S0/S1/S2 versus TR-D0/TR-K0 | Caffeine and trigonelline arm namespaces are separate; do not infer the same inputs from similar IDs. |
| L1M/L2M/L12 | 5-CQA conditional arms with different early-assay summaries; retained exposure and extrapolation apply. |
| G0–G3 and change declarations | Governance scope and equation-change classification, not scientific maturity or evidence quality. |


<a id="appendix-e"></a>

## Appendix E — Durable locator index

[Back to navigation](#review-navigation)

Every link below uses the full reviewed commit. A whole-file range is used for structured results where the named JSON key/table is the operative locator. The review’s commands and scripts bind newly computed aggregates; GitHub PR/issue links bind live records at the stated retrieval times. Abbreviated crosswalk paths are resolved in Appendix C’s key.

#### EWP

##### `.github/workflows/static-validation.yml`

- [L43–L64](https://github.com/trbrewer/espresso-whole-pull/blob/4284e9460c8057053e95de7cfa2fb3590e68e9db/.github/workflows/static-validation.yml#L43-L64)

##### `README.md`

- [L1–L1](https://github.com/trbrewer/espresso-whole-pull/blob/4284e9460c8057053e95de7cfa2fb3590e68e9db/README.md#L1-L1)

##### `VERSION`

- [L1–L1](https://github.com/trbrewer/espresso-whole-pull/blob/4284e9460c8057053e95de7cfa2fb3590e68e9db/VERSION#L1-L1)

##### `dependencies/puckworks.lock.json`

- [L1–L15](https://github.com/trbrewer/espresso-whole-pull/blob/4284e9460c8057053e95de7cfa2fb3590e68e9db/dependencies/puckworks.lock.json#L1-L15)

##### `docs/MODEL_SPECIFICATION.md`

- [L24–L144](https://github.com/trbrewer/espresso-whole-pull/blob/4284e9460c8057053e95de7cfa2fb3590e68e9db/docs/MODEL_SPECIFICATION.md#L24-L144)
- [L103–L118](https://github.com/trbrewer/espresso-whole-pull/blob/4284e9460c8057053e95de7cfa2fb3590e68e9db/docs/MODEL_SPECIFICATION.md#L103-L118)

##### `docs/PROJECT_STATE.md`

- [L1–L1](https://github.com/trbrewer/espresso-whole-pull/blob/4284e9460c8057053e95de7cfa2fb3590e68e9db/docs/PROJECT_STATE.md#L1-L1)
- [L1–L1093](https://github.com/trbrewer/espresso-whole-pull/blob/4284e9460c8057053e95de7cfa2fb3590e68e9db/docs/PROJECT_STATE.md#L1-L1093)
- [L3–L19](https://github.com/trbrewer/espresso-whole-pull/blob/4284e9460c8057053e95de7cfa2fb3590e68e9db/docs/PROJECT_STATE.md#L3-L19)

##### `docs/analysis/data_leverage/VISUALIZER_PRIVATE_WORK_RECORD.md`

- [L1–L1](https://github.com/trbrewer/espresso-whole-pull/blob/4284e9460c8057053e95de7cfa2fb3590e68e9db/docs/analysis/data_leverage/VISUALIZER_PRIVATE_WORK_RECORD.md#L1-L1)
- [L63–L78](https://github.com/trbrewer/espresso-whole-pull/blob/4284e9460c8057053e95de7cfa2fb3590e68e9db/docs/analysis/data_leverage/VISUALIZER_PRIVATE_WORK_RECORD.md#L63-L78)

##### `docs/analysis/ewp_porosity_permeability_prior_001/POROSITY_MATERIALITY.json`

- [L1–L141](https://github.com/trbrewer/espresso-whole-pull/blob/4284e9460c8057053e95de7cfa2fb3590e68e9db/docs/analysis/ewp_porosity_permeability_prior_001/POROSITY_MATERIALITY.json#L1-L141)
- [L18–L25](https://github.com/trbrewer/espresso-whole-pull/blob/4284e9460c8057053e95de7cfa2fb3590e68e9db/docs/analysis/ewp_porosity_permeability_prior_001/POROSITY_MATERIALITY.json#L18-L25)
- [L32–L80](https://github.com/trbrewer/espresso-whole-pull/blob/4284e9460c8057053e95de7cfa2fb3590e68e9db/docs/analysis/ewp_porosity_permeability_prior_001/POROSITY_MATERIALITY.json#L32-L80)
- [L87–L136](https://github.com/trbrewer/espresso-whole-pull/blob/4284e9460c8057053e95de7cfa2fb3590e68e9db/docs/analysis/ewp_porosity_permeability_prior_001/POROSITY_MATERIALITY.json#L87-L136)

##### `docs/analysis/ewp_porosity_permeability_prior_001/RESULT.md`

- [L1–L1](https://github.com/trbrewer/espresso-whole-pull/blob/4284e9460c8057053e95de7cfa2fb3590e68e9db/docs/analysis/ewp_porosity_permeability_prior_001/RESULT.md#L1-L1)
- [L13–L32](https://github.com/trbrewer/espresso-whole-pull/blob/4284e9460c8057053e95de7cfa2fb3590e68e9db/docs/analysis/ewp_porosity_permeability_prior_001/RESULT.md#L13-L32)

##### `docs/analysis/sci_ed_003/MINIMUM_PROGRAMME.md`

- [L1–L1](https://github.com/trbrewer/espresso-whole-pull/blob/4284e9460c8057053e95de7cfa2fb3590e68e9db/docs/analysis/sci_ed_003/MINIMUM_PROGRAMME.md#L1-L1)
- [L3–L31](https://github.com/trbrewer/espresso-whole-pull/blob/4284e9460c8057053e95de7cfa2fb3590e68e9db/docs/analysis/sci_ed_003/MINIMUM_PROGRAMME.md#L3-L31)

##### `docs/analysis/sci_ed_003/RESULT.md`

- [L1–L1](https://github.com/trbrewer/espresso-whole-pull/blob/4284e9460c8057053e95de7cfa2fb3590e68e9db/docs/analysis/sci_ed_003/RESULT.md#L1-L1)
- [L5–L21](https://github.com/trbrewer/espresso-whole-pull/blob/4284e9460c8057053e95de7cfa2fb3590e68e9db/docs/analysis/sci_ed_003/RESULT.md#L5-L21)

##### `docs/analysis/sci_md_010/BREW_RESULTS.csv`

- [L1–L1](https://github.com/trbrewer/espresso-whole-pull/blob/4284e9460c8057053e95de7cfa2fb3590e68e9db/docs/analysis/sci_md_010/BREW_RESULTS.csv#L1-L1)

##### `docs/analysis/sci_md_010/FOLD_RESULTS.csv`

- [L1–L34](https://github.com/trbrewer/espresso-whole-pull/blob/4284e9460c8057053e95de7cfa2fb3590e68e9db/docs/analysis/sci_md_010/FOLD_RESULTS.csv#L1-L34)

##### `docs/analysis/sci_md_010/PRESSURE_RESPONSE_DIAGNOSTICS.json`

- [L71–L88](https://github.com/trbrewer/espresso-whole-pull/blob/4284e9460c8057053e95de7cfa2fb3590e68e9db/docs/analysis/sci_md_010/PRESSURE_RESPONSE_DIAGNOSTICS.json#L71-L88)
- [L159–L176](https://github.com/trbrewer/espresso-whole-pull/blob/4284e9460c8057053e95de7cfa2fb3590e68e9db/docs/analysis/sci_md_010/PRESSURE_RESPONSE_DIAGNOSTICS.json#L159-L176)
- [L247–L265](https://github.com/trbrewer/espresso-whole-pull/blob/4284e9460c8057053e95de7cfa2fb3590e68e9db/docs/analysis/sci_md_010/PRESSURE_RESPONSE_DIAGNOSTICS.json#L247-L265)

##### `docs/analysis/sci_md_010/RESULT.md`

- [L37–L59](https://github.com/trbrewer/espresso-whole-pull/blob/4284e9460c8057053e95de7cfa2fb3590e68e9db/docs/analysis/sci_md_010/RESULT.md#L37-L59)

##### `docs/analysis/sci_md_010/UNCERTAINTY_RESULTS.json`

- [L1–L66](https://github.com/trbrewer/espresso-whole-pull/blob/4284e9460c8057053e95de7cfa2fb3590e68e9db/docs/analysis/sci_md_010/UNCERTAINTY_RESULTS.json#L1-L66)

##### `docs/analysis/sci_md_011/AGGREGATE_RESULTS.csv`

- [L1–L5](https://github.com/trbrewer/espresso-whole-pull/blob/4284e9460c8057053e95de7cfa2fb3590e68e9db/docs/analysis/sci_md_011/AGGREGATE_RESULTS.csv#L1-L5)

##### `docs/analysis/sci_md_011/BREW_RESULTS.csv`

- [L1–L1](https://github.com/trbrewer/espresso-whole-pull/blob/4284e9460c8057053e95de7cfa2fb3590e68e9db/docs/analysis/sci_md_011/BREW_RESULTS.csv#L1-L1)

##### `docs/analysis/sci_md_011/FOLD_RESULTS.csv`

- [L1–L45](https://github.com/trbrewer/espresso-whole-pull/blob/4284e9460c8057053e95de7cfa2fb3590e68e9db/docs/analysis/sci_md_011/FOLD_RESULTS.csv#L1-L45)

##### `docs/analysis/sci_md_011/PAIRWISE_COMPARISONS.json`

- [L1–L46](https://github.com/trbrewer/espresso-whole-pull/blob/4284e9460c8057053e95de7cfa2fb3590e68e9db/docs/analysis/sci_md_011/PAIRWISE_COMPARISONS.json#L1-L46)

##### `docs/analysis/sci_md_011/PRESSURE_RESPONSE_DIAGNOSTICS.json`

- [L293–L313](https://github.com/trbrewer/espresso-whole-pull/blob/4284e9460c8057053e95de7cfa2fb3590e68e9db/docs/analysis/sci_md_011/PRESSURE_RESPONSE_DIAGNOSTICS.json#L293-L313)

##### `docs/analysis/sci_md_011/RESULT.md`

- [L7–L26](https://github.com/trbrewer/espresso-whole-pull/blob/4284e9460c8057053e95de7cfa2fb3590e68e9db/docs/analysis/sci_md_011/RESULT.md#L7-L26)

##### `docs/analysis/sci_md_011/UNCERTAINTY_RESULTS.json`

- [L1–L52](https://github.com/trbrewer/espresso-whole-pull/blob/4284e9460c8057053e95de7cfa2fb3590e68e9db/docs/analysis/sci_md_011/UNCERTAINTY_RESULTS.json#L1-L52)

##### `docs/analysis/sci_md_012/PARAMETER_FEASIBILITY.json`

- [L120–L126](https://github.com/trbrewer/espresso-whole-pull/blob/4284e9460c8057053e95de7cfa2fb3590e68e9db/docs/analysis/sci_md_012/PARAMETER_FEASIBILITY.json#L120-L126)
- [L163–L214](https://github.com/trbrewer/espresso-whole-pull/blob/4284e9460c8057053e95de7cfa2fb3590e68e9db/docs/analysis/sci_md_012/PARAMETER_FEASIBILITY.json#L163-L214)

##### `docs/analysis/sci_md_012/RESULT.md`

- [L9–L21](https://github.com/trbrewer/espresso-whole-pull/blob/4284e9460c8057053e95de7cfa2fb3590e68e9db/docs/analysis/sci_md_012/RESULT.md#L9-L21)

##### `docs/analysis/sci_md_012/ROOT_FEASIBILITY.csv`

- [L1–L1](https://github.com/trbrewer/espresso-whole-pull/blob/4284e9460c8057053e95de7cfa2fb3590e68e9db/docs/analysis/sci_md_012/ROOT_FEASIBILITY.csv#L1-L1)
- [L1–L7](https://github.com/trbrewer/espresso-whole-pull/blob/4284e9460c8057053e95de7cfa2fb3590e68e9db/docs/analysis/sci_md_012/ROOT_FEASIBILITY.csv#L1-L7)

##### `docs/analysis/sci_md_grudeva_clock_001/RESULT.md`

- [L15–L78](https://github.com/trbrewer/espresso-whole-pull/blob/4284e9460c8057053e95de7cfa2fb3590e68e9db/docs/analysis/sci_md_grudeva_clock_001/RESULT.md#L15-L78)

##### `docs/analysis/sci_md_rheology_010/METRICS.json`

- [L1–L1](https://github.com/trbrewer/espresso-whole-pull/blob/4284e9460c8057053e95de7cfa2fb3590e68e9db/docs/analysis/sci_md_rheology_010/METRICS.json#L1-L1)

##### `docs/analysis/sci_md_rheology_010/PROTOCOL.md`

- [L103–L141](https://github.com/trbrewer/espresso-whole-pull/blob/4284e9460c8057053e95de7cfa2fb3590e68e9db/docs/analysis/sci_md_rheology_010/PROTOCOL.md#L103-L141)

##### `docs/governance/MINIMUM_NECESSARY_GOVERNANCE_STANDARD.md`

- [L1–L1](https://github.com/trbrewer/espresso-whole-pull/blob/4284e9460c8057053e95de7cfa2fb3590e68e9db/docs/governance/MINIMUM_NECESSARY_GOVERNANCE_STANDARD.md#L1-L1)

##### `docs/wp03/WP03_002_RESULTS.md`

- [L45–L64](https://github.com/trbrewer/espresso-whole-pull/blob/4284e9460c8057053e95de7cfa2fb3590e68e9db/docs/wp03/WP03_002_RESULTS.md#L45-L64)
- [L50–L59](https://github.com/trbrewer/espresso-whole-pull/blob/4284e9460c8057053e95de7cfa2fb3590e68e9db/docs/wp03/WP03_002_RESULTS.md#L50-L59)
- [L113–L124](https://github.com/trbrewer/espresso-whole-pull/blob/4284e9460c8057053e95de7cfa2fb3590e68e9db/docs/wp03/WP03_002_RESULTS.md#L113-L124)

##### `scripts/sci_md_011_core.py`

- [L183–L186](https://github.com/trbrewer/espresso-whole-pull/blob/4284e9460c8057053e95de7cfa2fb3590e68e9db/scripts/sci_md_011_core.py#L183-L186)

##### `solver/espressoWholePullFoam/aggregateViscosity.H`

- [L25–L67](https://github.com/trbrewer/espresso-whole-pull/blob/4284e9460c8057053e95de7cfa2fb3590e68e9db/solver/espressoWholePullFoam/aggregateViscosity.H#L25-L67)

##### `solver/espressoWholePullFoam/espressoWholePullFoam.C`

- [L749–L790](https://github.com/trbrewer/espresso-whole-pull/blob/4284e9460c8057053e95de7cfa2fb3590e68e9db/solver/espressoWholePullFoam/espressoWholePullFoam.C#L749-L790)
- [L749–L928](https://github.com/trbrewer/espresso-whole-pull/blob/4284e9460c8057053e95de7cfa2fb3590e68e9db/solver/espressoWholePullFoam/espressoWholePullFoam.C#L749-L928)
- [L793–L928](https://github.com/trbrewer/espresso-whole-pull/blob/4284e9460c8057053e95de7cfa2fb3590e68e9db/solver/espressoWholePullFoam/espressoWholePullFoam.C#L793-L928)
- [L2334–L2365](https://github.com/trbrewer/espresso-whole-pull/blob/4284e9460c8057053e95de7cfa2fb3590e68e9db/solver/espressoWholePullFoam/espressoWholePullFoam.C#L2334-L2365)
- [L2589–L2760](https://github.com/trbrewer/espresso-whole-pull/blob/4284e9460c8057053e95de7cfa2fb3590e68e9db/solver/espressoWholePullFoam/espressoWholePullFoam.C#L2589-L2760)
- [L2783–L2799](https://github.com/trbrewer/espresso-whole-pull/blob/4284e9460c8057053e95de7cfa2fb3590e68e9db/solver/espressoWholePullFoam/espressoWholePullFoam.C#L2783-L2799)
- [L2834–L2846](https://github.com/trbrewer/espresso-whole-pull/blob/4284e9460c8057053e95de7cfa2fb3590e68e9db/solver/espressoWholePullFoam/espressoWholePullFoam.C#L2834-L2846)
- [L3213–L3317](https://github.com/trbrewer/espresso-whole-pull/blob/4284e9460c8057053e95de7cfa2fb3590e68e9db/solver/espressoWholePullFoam/espressoWholePullFoam.C#L3213-L3317)
- [L3213–L3369](https://github.com/trbrewer/espresso-whole-pull/blob/4284e9460c8057053e95de7cfa2fb3590e68e9db/solver/espressoWholePullFoam/espressoWholePullFoam.C#L3213-L3369)
- [L3328–L3369](https://github.com/trbrewer/espresso-whole-pull/blob/4284e9460c8057053e95de7cfa2fb3590e68e9db/solver/espressoWholePullFoam/espressoWholePullFoam.C#L3328-L3369)

##### `solver/espressoWholePullFoam/forchheimerResistance.H`

- [L10–L64](https://github.com/trbrewer/espresso-whole-pull/blob/4284e9460c8057053e95de7cfa2fb3590e68e9db/solver/espressoWholePullFoam/forchheimerResistance.H#L10-L64)

##### `solver/espressoWholePullFoam/machineBoundaryModel.H`

- [L291–L365](https://github.com/trbrewer/espresso-whole-pull/blob/4284e9460c8057053e95de7cfa2fb3590e68e9db/solver/espressoWholePullFoam/machineBoundaryModel.H#L291-L365)

##### `solver/espressoWholePullFoam/poroelasticCompaction.H`

- [L10–L150](https://github.com/trbrewer/espresso-whole-pull/blob/4284e9460c8057053e95de7cfa2fb3590e68e9db/solver/espressoWholePullFoam/poroelasticCompaction.H#L10-L150)

##### `validation/sci_md_008/FINAL_REPORT.md`

- [L23–L39](https://github.com/trbrewer/espresso-whole-pull/blob/4284e9460c8057053e95de7cfa2fb3590e68e9db/validation/sci_md_008/FINAL_REPORT.md#L23-L39)

##### `validation/sci_md_008/INVENTORY_SCALE_INVARIANCE.csv`

- [L1–L1](https://github.com/trbrewer/espresso-whole-pull/blob/4284e9460c8057053e95de7cfa2fb3590e68e9db/validation/sci_md_008/INVENTORY_SCALE_INVARIANCE.csv#L1-L1)
- [L1–L37](https://github.com/trbrewer/espresso-whole-pull/blob/4284e9460c8057053e95de7cfa2fb3590e68e9db/validation/sci_md_008/INVENTORY_SCALE_INVARIANCE.csv#L1-L37)

##### `validation/sci_md_009/FINAL_REPORT.md`

- [L1–L3](https://github.com/trbrewer/espresso-whole-pull/blob/4284e9460c8057053e95de7cfa2fb3590e68e9db/validation/sci_md_009/FINAL_REPORT.md#L1-L3)

##### `validation/sci_md_009/NONLINEAR_RESPONSE_VALIDATION.csv`

- [L1–L1](https://github.com/trbrewer/espresso-whole-pull/blob/4284e9460c8057053e95de7cfa2fb3590e68e9db/validation/sci_md_009/NONLINEAR_RESPONSE_VALIDATION.csv#L1-L1)
- [L1–L325](https://github.com/trbrewer/espresso-whole-pull/blob/4284e9460c8057053e95de7cfa2fb3590e68e9db/validation/sci_md_009/NONLINEAR_RESPONSE_VALIDATION.csv#L1-L325)

##### `validation/wp03/WP03_002_CORRECTED_COMPARISON.json`

- [L1–L945](https://github.com/trbrewer/espresso-whole-pull/blob/4284e9460c8057053e95de7cfa2fb3590e68e9db/validation/wp03/WP03_002_CORRECTED_COMPARISON.json#L1-L945)
- [L77–L349](https://github.com/trbrewer/espresso-whole-pull/blob/4284e9460c8057053e95de7cfa2fb3590e68e9db/validation/wp03/WP03_002_CORRECTED_COMPARISON.json#L77-L349)
- [L350–L621](https://github.com/trbrewer/espresso-whole-pull/blob/4284e9460c8057053e95de7cfa2fb3590e68e9db/validation/wp03/WP03_002_CORRECTED_COMPARISON.json#L350-L621)
- [L622–L897](https://github.com/trbrewer/espresso-whole-pull/blob/4284e9460c8057053e95de7cfa2fb3590e68e9db/validation/wp03/WP03_002_CORRECTED_COMPARISON.json#L622-L897)
- [L900–L941](https://github.com/trbrewer/espresso-whole-pull/blob/4284e9460c8057053e95de7cfa2fb3590e68e9db/validation/wp03/WP03_002_CORRECTED_COMPARISON.json#L900-L941)

#### PW

##### `CLAUDE.md`

- [L1–L1](https://github.com/trbrewer/puckworks/blob/9dd456be7fd797b9cda0a2bbf50d1ac717d72835/CLAUDE.md#L1-L1)
- [L86–L109](https://github.com/trbrewer/puckworks/blob/9dd456be7fd797b9cda0a2bbf50d1ac717d72835/CLAUDE.md#L86-L109)

##### `README.md`

- [L1–L1](https://github.com/trbrewer/puckworks/blob/9dd456be7fd797b9cda0a2bbf50d1ac717d72835/README.md#L1-L1)

##### `docs/CURRENT.md`

- [L1–L1](https://github.com/trbrewer/puckworks/blob/9dd456be7fd797b9cda0a2bbf50d1ac717d72835/docs/CURRENT.md#L1-L1)
- [L1–L56](https://github.com/trbrewer/puckworks/blob/9dd456be7fd797b9cda0a2bbf50d1ac717d72835/docs/CURRENT.md#L1-L56)
- [L31–L35](https://github.com/trbrewer/puckworks/blob/9dd456be7fd797b9cda0a2bbf50d1ac717d72835/docs/CURRENT.md#L31-L35)

##### `docs/ONBOARDING.md`

- [L1–L1](https://github.com/trbrewer/puckworks/blob/9dd456be7fd797b9cda0a2bbf50d1ac717d72835/docs/ONBOARDING.md#L1-L1)
- [L104–L108](https://github.com/trbrewer/puckworks/blob/9dd456be7fd797b9cda0a2bbf50d1ac717d72835/docs/ONBOARDING.md#L104-L108)

##### `docs/ROADMAP.md`

- [L1–L1](https://github.com/trbrewer/puckworks/blob/9dd456be7fd797b9cda0a2bbf50d1ac717d72835/docs/ROADMAP.md#L1-L1)

##### `docs/analysis/model_foster2025_postsat_001/HANDOFF.md`

- [L19–L48](https://github.com/trbrewer/puckworks/blob/9dd456be7fd797b9cda0a2bbf50d1ac717d72835/docs/analysis/model_foster2025_postsat_001/HANDOFF.md#L19-L48)

##### `docs/analysis/model_foster2025_postsat_001/RESULTS.md`

- [L1–L61](https://github.com/trbrewer/puckworks/blob/9dd456be7fd797b9cda0a2bbf50d1ac717d72835/docs/analysis/model_foster2025_postsat_001/RESULTS.md#L1-L61)

##### `docs/analysis/model_grudeva2026_bed_accuracy_004/RESULTS.md`

- [L1–L1](https://github.com/trbrewer/puckworks/blob/9dd456be7fd797b9cda0a2bbf50d1ac717d72835/docs/analysis/model_grudeva2026_bed_accuracy_004/RESULTS.md#L1-L1)
- [L3–L4](https://github.com/trbrewer/puckworks/blob/9dd456be7fd797b9cda0a2bbf50d1ac717d72835/docs/analysis/model_grudeva2026_bed_accuracy_004/RESULTS.md#L3-L4)

##### `docs/analysis/model_grudeva2026_matched_comparison_008/RESULTS.json`

- [L1–L1](https://github.com/trbrewer/puckworks/blob/9dd456be7fd797b9cda0a2bbf50d1ac717d72835/docs/analysis/model_grudeva2026_matched_comparison_008/RESULTS.json#L1-L1)

##### `docs/analysis/model_grudeva2026_matched_comparison_008/RESULTS.md`

- [L1–L1](https://github.com/trbrewer/puckworks/blob/9dd456be7fd797b9cda0a2bbf50d1ac717d72835/docs/analysis/model_grudeva2026_matched_comparison_008/RESULTS.md#L1-L1)
- [L1–L148](https://github.com/trbrewer/puckworks/blob/9dd456be7fd797b9cda0a2bbf50d1ac717d72835/docs/analysis/model_grudeva2026_matched_comparison_008/RESULTS.md#L1-L148)

##### `docs/analysis/model_grudeva2026_publication_reconciliation_009/RESULTS.json`

- [L1–L1](https://github.com/trbrewer/puckworks/blob/9dd456be7fd797b9cda0a2bbf50d1ac717d72835/docs/analysis/model_grudeva2026_publication_reconciliation_009/RESULTS.json#L1-L1)

##### `docs/analysis/model_grudeva2026_publication_reconciliation_009/RESULTS.md`

- [L1–L1](https://github.com/trbrewer/puckworks/blob/9dd456be7fd797b9cda0a2bbf50d1ac717d72835/docs/analysis/model_grudeva2026_publication_reconciliation_009/RESULTS.md#L1-L1)
- [L3–L25](https://github.com/trbrewer/puckworks/blob/9dd456be7fd797b9cda0a2bbf50d1ac717d72835/docs/analysis/model_grudeva2026_publication_reconciliation_009/RESULTS.md#L3-L25)

##### `docs/analysis/model_pannusch2024_prefix_conditioned_006/REVIEW.md`

- [L3–L7](https://github.com/trbrewer/puckworks/blob/9dd456be7fd797b9cda0a2bbf50d1ac717d72835/docs/analysis/model_pannusch2024_prefix_conditioned_006/REVIEW.md#L3-L7)

##### `docs/analysis/rp_d_lc_001/decision.md`

- [L47–L57](https://github.com/trbrewer/puckworks/blob/9dd456be7fd797b9cda0a2bbf50d1ac717d72835/docs/analysis/rp_d_lc_001/decision.md#L47-L57)

##### `docs/analysis/sci_md_004_stage_e0/target_access_policy.json`

- [L1–L36](https://github.com/trbrewer/puckworks/blob/9dd456be7fd797b9cda0a2bbf50d1ac717d72835/docs/analysis/sci_md_004_stage_e0/target_access_policy.json#L1-L36)
- [L3–L35](https://github.com/trbrewer/puckworks/blob/9dd456be7fd797b9cda0a2bbf50d1ac717d72835/docs/analysis/sci_md_004_stage_e0/target_access_policy.json#L3-L35)

##### `docs/analysis/sci_md_5cqa_assay_001/RESULTS.json`

- [L1–L1898](https://github.com/trbrewer/puckworks/blob/9dd456be7fd797b9cda0a2bbf50d1ac717d72835/docs/analysis/sci_md_5cqa_assay_001/RESULTS.json#L1-L1898)

##### `docs/analysis/sci_md_5cqa_assay_002/PROTOCOL.md`

- [L1–L220](https://github.com/trbrewer/puckworks/blob/9dd456be7fd797b9cda0a2bbf50d1ac717d72835/docs/analysis/sci_md_5cqa_assay_002/PROTOCOL.md#L1-L220)
- [L156–L174](https://github.com/trbrewer/puckworks/blob/9dd456be7fd797b9cda0a2bbf50d1ac717d72835/docs/analysis/sci_md_5cqa_assay_002/PROTOCOL.md#L156-L174)
- [L156–L183](https://github.com/trbrewer/puckworks/blob/9dd456be7fd797b9cda0a2bbf50d1ac717d72835/docs/analysis/sci_md_5cqa_assay_002/PROTOCOL.md#L156-L183)

##### `docs/analysis/sci_md_5cqa_assay_002/RESULTS.json`

- [L1–L3352](https://github.com/trbrewer/puckworks/blob/9dd456be7fd797b9cda0a2bbf50d1ac717d72835/docs/analysis/sci_md_5cqa_assay_002/RESULTS.json#L1-L3352)

##### `docs/analysis/sci_md_5cqa_assay_002/RESULTS.md`

- [L21–L78](https://github.com/trbrewer/puckworks/blob/9dd456be7fd797b9cda0a2bbf50d1ac717d72835/docs/analysis/sci_md_5cqa_assay_002/RESULTS.md#L21-L78)

##### `docs/analysis/sci_md_5cqa_delivery_001/RESULTS.json`

- [L1–L930](https://github.com/trbrewer/puckworks/blob/9dd456be7fd797b9cda0a2bbf50d1ac717d72835/docs/analysis/sci_md_5cqa_delivery_001/RESULTS.json#L1-L930)

##### `docs/analysis/sci_md_5cqa_tds_001/RESULTS.json`

- [L1–L2293](https://github.com/trbrewer/puckworks/blob/9dd456be7fd797b9cda0a2bbf50d1ac717d72835/docs/analysis/sci_md_5cqa_tds_001/RESULTS.json#L1-L2293)

##### `docs/analysis/sci_md_caffeine_delivery_001/PROTOCOL.md`

- [L1–L102](https://github.com/trbrewer/puckworks/blob/9dd456be7fd797b9cda0a2bbf50d1ac717d72835/docs/analysis/sci_md_caffeine_delivery_001/PROTOCOL.md#L1-L102)
- [L62–L90](https://github.com/trbrewer/puckworks/blob/9dd456be7fd797b9cda0a2bbf50d1ac717d72835/docs/analysis/sci_md_caffeine_delivery_001/PROTOCOL.md#L62-L90)
- [L69–L83](https://github.com/trbrewer/puckworks/blob/9dd456be7fd797b9cda0a2bbf50d1ac717d72835/docs/analysis/sci_md_caffeine_delivery_001/PROTOCOL.md#L69-L83)

##### `docs/analysis/sci_md_caffeine_delivery_001/RESULT.md`

- [L7–L43](https://github.com/trbrewer/puckworks/blob/9dd456be7fd797b9cda0a2bbf50d1ac717d72835/docs/analysis/sci_md_caffeine_delivery_001/RESULT.md#L7-L43)

##### `docs/analysis/sci_md_caffeine_delivery_001/RESULTS.json`

- [L1–L1567](https://github.com/trbrewer/puckworks/blob/9dd456be7fd797b9cda0a2bbf50d1ac717d72835/docs/analysis/sci_md_caffeine_delivery_001/RESULTS.json#L1-L1567)

##### `docs/analysis/sci_md_grudeva_clock_001/PROTOCOL.md`

- [L154–L164](https://github.com/trbrewer/puckworks/blob/9dd456be7fd797b9cda0a2bbf50d1ac717d72835/docs/analysis/sci_md_grudeva_clock_001/PROTOCOL.md#L154-L164)

##### `docs/analysis/sci_md_mass_delivery_001/PROTOCOL.md`

- [L1–L141](https://github.com/trbrewer/puckworks/blob/9dd456be7fd797b9cda0a2bbf50d1ac717d72835/docs/analysis/sci_md_mass_delivery_001/PROTOCOL.md#L1-L141)

##### `docs/analysis/sci_md_mass_delivery_001/RESULTS.json`

- [L1–L1312](https://github.com/trbrewer/puckworks/blob/9dd456be7fd797b9cda0a2bbf50d1ac717d72835/docs/analysis/sci_md_mass_delivery_001/RESULTS.json#L1-L1312)

##### `docs/analysis/sci_md_mass_delivery_002/PROTOCOL.md`

- [L1–L149](https://github.com/trbrewer/puckworks/blob/9dd456be7fd797b9cda0a2bbf50d1ac717d72835/docs/analysis/sci_md_mass_delivery_002/PROTOCOL.md#L1-L149)

##### `docs/analysis/sci_md_mass_delivery_002/RESULTS.json`

- [L1–L647](https://github.com/trbrewer/puckworks/blob/9dd456be7fd797b9cda0a2bbf50d1ac717d72835/docs/analysis/sci_md_mass_delivery_002/RESULTS.json#L1-L647)

##### `docs/analysis/sci_md_mass_delivery_003/PROTOCOL.md`

- [L1–L84](https://github.com/trbrewer/puckworks/blob/9dd456be7fd797b9cda0a2bbf50d1ac717d72835/docs/analysis/sci_md_mass_delivery_003/PROTOCOL.md#L1-L84)

##### `docs/analysis/sci_md_mass_delivery_003/RESULT.md`

- [L7–L59](https://github.com/trbrewer/puckworks/blob/9dd456be7fd797b9cda0a2bbf50d1ac717d72835/docs/analysis/sci_md_mass_delivery_003/RESULT.md#L7-L59)

##### `docs/analysis/sci_md_mass_delivery_003/RESULTS.json`

- [L1–L2779](https://github.com/trbrewer/puckworks/blob/9dd456be7fd797b9cda0a2bbf50d1ac717d72835/docs/analysis/sci_md_mass_delivery_003/RESULTS.json#L1-L2779)

##### `docs/analysis/sci_md_mass_delivery_004/RESULT.md`

- [L75–L106](https://github.com/trbrewer/puckworks/blob/9dd456be7fd797b9cda0a2bbf50d1ac717d72835/docs/analysis/sci_md_mass_delivery_004/RESULT.md#L75-L106)

##### `docs/analysis/sci_md_mass_delivery_006/PROTOCOL.md`

- [L1–L128](https://github.com/trbrewer/puckworks/blob/9dd456be7fd797b9cda0a2bbf50d1ac717d72835/docs/analysis/sci_md_mass_delivery_006/PROTOCOL.md#L1-L128)
- [L85–L114](https://github.com/trbrewer/puckworks/blob/9dd456be7fd797b9cda0a2bbf50d1ac717d72835/docs/analysis/sci_md_mass_delivery_006/PROTOCOL.md#L85-L114)

##### `docs/analysis/sci_md_mass_delivery_006/RESULT.md`

- [L11–L83](https://github.com/trbrewer/puckworks/blob/9dd456be7fd797b9cda0a2bbf50d1ac717d72835/docs/analysis/sci_md_mass_delivery_006/RESULT.md#L11-L83)

##### `docs/analysis/sci_md_mass_delivery_006/RESULTS.json`

- [L1–L1590](https://github.com/trbrewer/puckworks/blob/9dd456be7fd797b9cda0a2bbf50d1ac717d72835/docs/analysis/sci_md_mass_delivery_006/RESULTS.json#L1-L1590)

##### `docs/analysis/sci_md_mass_delivery_007/PROTOCOL.md`

- [L1–L170](https://github.com/trbrewer/puckworks/blob/9dd456be7fd797b9cda0a2bbf50d1ac717d72835/docs/analysis/sci_md_mass_delivery_007/PROTOCOL.md#L1-L170)
- [L89–L116](https://github.com/trbrewer/puckworks/blob/9dd456be7fd797b9cda0a2bbf50d1ac717d72835/docs/analysis/sci_md_mass_delivery_007/PROTOCOL.md#L89-L116)

##### `docs/analysis/sci_md_mass_delivery_007/RESULTS.json`

- [L1–L359](https://github.com/trbrewer/puckworks/blob/9dd456be7fd797b9cda0a2bbf50d1ac717d72835/docs/analysis/sci_md_mass_delivery_007/RESULTS.json#L1-L359)

##### `docs/analysis/sci_md_mass_delivery_008/PROTOCOL.md`

- [L1–L131](https://github.com/trbrewer/puckworks/blob/9dd456be7fd797b9cda0a2bbf50d1ac717d72835/docs/analysis/sci_md_mass_delivery_008/PROTOCOL.md#L1-L131)
- [L46–L95](https://github.com/trbrewer/puckworks/blob/9dd456be7fd797b9cda0a2bbf50d1ac717d72835/docs/analysis/sci_md_mass_delivery_008/PROTOCOL.md#L46-L95)
- [L48–L73](https://github.com/trbrewer/puckworks/blob/9dd456be7fd797b9cda0a2bbf50d1ac717d72835/docs/analysis/sci_md_mass_delivery_008/PROTOCOL.md#L48-L73)

##### `docs/analysis/sci_md_mass_delivery_008/RESULTS.json`

- [L1–L561](https://github.com/trbrewer/puckworks/blob/9dd456be7fd797b9cda0a2bbf50d1ac717d72835/docs/analysis/sci_md_mass_delivery_008/RESULTS.json#L1-L561)

##### `docs/analysis/sci_md_mass_stop_decision_001/PROTOCOL.md`

- [L1–L167](https://github.com/trbrewer/puckworks/blob/9dd456be7fd797b9cda0a2bbf50d1ac717d72835/docs/analysis/sci_md_mass_stop_decision_001/PROTOCOL.md#L1-L167)
- [L43–L54](https://github.com/trbrewer/puckworks/blob/9dd456be7fd797b9cda0a2bbf50d1ac717d72835/docs/analysis/sci_md_mass_stop_decision_001/PROTOCOL.md#L43-L54)
- [L45–L51](https://github.com/trbrewer/puckworks/blob/9dd456be7fd797b9cda0a2bbf50d1ac717d72835/docs/analysis/sci_md_mass_stop_decision_001/PROTOCOL.md#L45-L51)
- [L135–L151](https://github.com/trbrewer/puckworks/blob/9dd456be7fd797b9cda0a2bbf50d1ac717d72835/docs/analysis/sci_md_mass_stop_decision_001/PROTOCOL.md#L135-L151)
- [L136–L149](https://github.com/trbrewer/puckworks/blob/9dd456be7fd797b9cda0a2bbf50d1ac717d72835/docs/analysis/sci_md_mass_stop_decision_001/PROTOCOL.md#L136-L149)

##### `docs/analysis/sci_md_mass_stop_decision_001/RESULT.md`

- [L3–L65](https://github.com/trbrewer/puckworks/blob/9dd456be7fd797b9cda0a2bbf50d1ac717d72835/docs/analysis/sci_md_mass_stop_decision_001/RESULT.md#L3-L65)

##### `docs/analysis/sci_md_mass_stop_decision_001/RESULTS.json`

- [L1–L345](https://github.com/trbrewer/puckworks/blob/9dd456be7fd797b9cda0a2bbf50d1ac717d72835/docs/analysis/sci_md_mass_stop_decision_001/RESULTS.json#L1-L345)

##### `docs/analysis/sci_md_mass_uncertainty_001/PROTOCOL.md`

- [L1–L131](https://github.com/trbrewer/puckworks/blob/9dd456be7fd797b9cda0a2bbf50d1ac717d72835/docs/analysis/sci_md_mass_uncertainty_001/PROTOCOL.md#L1-L131)

##### `docs/analysis/sci_md_mass_uncertainty_001/RESULTS.json`

- [L1–L1](https://github.com/trbrewer/puckworks/blob/9dd456be7fd797b9cda0a2bbf50d1ac717d72835/docs/analysis/sci_md_mass_uncertainty_001/RESULTS.json#L1-L1)
- [L1–L13682](https://github.com/trbrewer/puckworks/blob/9dd456be7fd797b9cda0a2bbf50d1ac717d72835/docs/analysis/sci_md_mass_uncertainty_001/RESULTS.json#L1-L13682)

##### `docs/analysis/sci_md_mass_uncertainty_001/RESULTS.md`

- [L44–L82](https://github.com/trbrewer/puckworks/blob/9dd456be7fd797b9cda0a2bbf50d1ac717d72835/docs/analysis/sci_md_mass_uncertainty_001/RESULTS.md#L44-L82)
- [L84–L163](https://github.com/trbrewer/puckworks/blob/9dd456be7fd797b9cda0a2bbf50d1ac717d72835/docs/analysis/sci_md_mass_uncertainty_001/RESULTS.md#L84-L163)

##### `docs/analysis/sci_md_smrke_transfer_001/RESULT.md`

- [L1–L163](https://github.com/trbrewer/puckworks/blob/9dd456be7fd797b9cda0a2bbf50d1ac717d72835/docs/analysis/sci_md_smrke_transfer_001/RESULT.md#L1-L163)

##### `docs/analysis/sci_md_trigonelline_delivery_001/RESULT.md`

- [L9–L52](https://github.com/trbrewer/puckworks/blob/9dd456be7fd797b9cda0a2bbf50d1ac717d72835/docs/analysis/sci_md_trigonelline_delivery_001/RESULT.md#L9-L52)

##### `docs/analysis/sci_md_trigonelline_delivery_001/RESULTS.json`

- [L1–L930](https://github.com/trbrewer/puckworks/blob/9dd456be7fd797b9cda0a2bbf50d1ac717d72835/docs/analysis/sci_md_trigonelline_delivery_001/RESULTS.json#L1-L930)

##### `docs/analysis/sci_val_tamped_k_001/RESULT.md`

- [L1–L1](https://github.com/trbrewer/puckworks/blob/9dd456be7fd797b9cda0a2bbf50d1ac717d72835/docs/analysis/sci_val_tamped_k_001/RESULT.md#L1-L1)

##### `docs/analysis/val_case_5cqa_decision_resolution_001/RESULTS.json`

- [L1–L1](https://github.com/trbrewer/puckworks/blob/9dd456be7fd797b9cda0a2bbf50d1ac717d72835/docs/analysis/val_case_5cqa_decision_resolution_001/RESULTS.json#L1-L1)

##### `docs/analysis/val_case_5cqa_decision_resolution_001/RESULTS.md`

- [L3–L34](https://github.com/trbrewer/puckworks/blob/9dd456be7fd797b9cda0a2bbf50d1ac717d72835/docs/analysis/val_case_5cqa_decision_resolution_001/RESULTS.md#L3-L34)
- [L3–L133](https://github.com/trbrewer/puckworks/blob/9dd456be7fd797b9cda0a2bbf50d1ac717d72835/docs/analysis/val_case_5cqa_decision_resolution_001/RESULTS.md#L3-L133)
- [L5–L34](https://github.com/trbrewer/puckworks/blob/9dd456be7fd797b9cda0a2bbf50d1ac717d72835/docs/analysis/val_case_5cqa_decision_resolution_001/RESULTS.md#L5-L34)
- [L61–L72](https://github.com/trbrewer/puckworks/blob/9dd456be7fd797b9cda0a2bbf50d1ac717d72835/docs/analysis/val_case_5cqa_decision_resolution_001/RESULTS.md#L61-L72)
- [L74–L88](https://github.com/trbrewer/puckworks/blob/9dd456be7fd797b9cda0a2bbf50d1ac717d72835/docs/analysis/val_case_5cqa_decision_resolution_001/RESULTS.md#L74-L88)
- [L74–L98](https://github.com/trbrewer/puckworks/blob/9dd456be7fd797b9cda0a2bbf50d1ac717d72835/docs/analysis/val_case_5cqa_decision_resolution_001/RESULTS.md#L74-L98)
- [L90–L114](https://github.com/trbrewer/puckworks/blob/9dd456be7fd797b9cda0a2bbf50d1ac717d72835/docs/analysis/val_case_5cqa_decision_resolution_001/RESULTS.md#L90-L114)
- [L110–L133](https://github.com/trbrewer/puckworks/blob/9dd456be7fd797b9cda0a2bbf50d1ac717d72835/docs/analysis/val_case_5cqa_decision_resolution_001/RESULTS.md#L110-L133)

##### `docs/analysis/val_case_caffeine_decision_resolution_001/FINAL_REVIEW_ADDENDUM.json`

- [L1–L1](https://github.com/trbrewer/puckworks/blob/9dd456be7fd797b9cda0a2bbf50d1ac717d72835/docs/analysis/val_case_caffeine_decision_resolution_001/FINAL_REVIEW_ADDENDUM.json#L1-L1)
- [L1–L57](https://github.com/trbrewer/puckworks/blob/9dd456be7fd797b9cda0a2bbf50d1ac717d72835/docs/analysis/val_case_caffeine_decision_resolution_001/FINAL_REVIEW_ADDENDUM.json#L1-L57)
- [L3–L17](https://github.com/trbrewer/puckworks/blob/9dd456be7fd797b9cda0a2bbf50d1ac717d72835/docs/analysis/val_case_caffeine_decision_resolution_001/FINAL_REVIEW_ADDENDUM.json#L3-L17)

##### `docs/analysis/val_case_caffeine_decision_resolution_001/RESULTS.json`

- [L1–L1](https://github.com/trbrewer/puckworks/blob/9dd456be7fd797b9cda0a2bbf50d1ac717d72835/docs/analysis/val_case_caffeine_decision_resolution_001/RESULTS.json#L1-L1)

##### `docs/analysis/val_case_caffeine_decision_resolution_001/RESULTS.md`

- [L36–L107](https://github.com/trbrewer/puckworks/blob/9dd456be7fd797b9cda0a2bbf50d1ac717d72835/docs/analysis/val_case_caffeine_decision_resolution_001/RESULTS.md#L36-L107)
- [L38–L155](https://github.com/trbrewer/puckworks/blob/9dd456be7fd797b9cda0a2bbf50d1ac717d72835/docs/analysis/val_case_caffeine_decision_resolution_001/RESULTS.md#L38-L155)
- [L50–L79](https://github.com/trbrewer/puckworks/blob/9dd456be7fd797b9cda0a2bbf50d1ac717d72835/docs/analysis/val_case_caffeine_decision_resolution_001/RESULTS.md#L50-L79)
- [L81–L107](https://github.com/trbrewer/puckworks/blob/9dd456be7fd797b9cda0a2bbf50d1ac717d72835/docs/analysis/val_case_caffeine_decision_resolution_001/RESULTS.md#L81-L107)
- [L148–L159](https://github.com/trbrewer/puckworks/blob/9dd456be7fd797b9cda0a2bbf50d1ac717d72835/docs/analysis/val_case_caffeine_decision_resolution_001/RESULTS.md#L148-L159)

##### `docs/analysis/val_case_rheology_decision_resolution_001/RESULTS.json`

- [L1–L1](https://github.com/trbrewer/puckworks/blob/9dd456be7fd797b9cda0a2bbf50d1ac717d72835/docs/analysis/val_case_rheology_decision_resolution_001/RESULTS.json#L1-L1)

##### `docs/analysis/val_case_rheology_decision_resolution_001/RESULTS.md`

- [L1–L1](https://github.com/trbrewer/puckworks/blob/9dd456be7fd797b9cda0a2bbf50d1ac717d72835/docs/analysis/val_case_rheology_decision_resolution_001/RESULTS.md#L1-L1)
- [L50–L58](https://github.com/trbrewer/puckworks/blob/9dd456be7fd797b9cda0a2bbf50d1ac717d72835/docs/analysis/val_case_rheology_decision_resolution_001/RESULTS.md#L50-L58)
- [L60–L174](https://github.com/trbrewer/puckworks/blob/9dd456be7fd797b9cda0a2bbf50d1ac717d72835/docs/analysis/val_case_rheology_decision_resolution_001/RESULTS.md#L60-L174)
- [L62–L174](https://github.com/trbrewer/puckworks/blob/9dd456be7fd797b9cda0a2bbf50d1ac717d72835/docs/analysis/val_case_rheology_decision_resolution_001/RESULTS.md#L62-L174)
- [L102–L174](https://github.com/trbrewer/puckworks/blob/9dd456be7fd797b9cda0a2bbf50d1ac717d72835/docs/analysis/val_case_rheology_decision_resolution_001/RESULTS.md#L102-L174)
- [L121–L176](https://github.com/trbrewer/puckworks/blob/9dd456be7fd797b9cda0a2bbf50d1ac717d72835/docs/analysis/val_case_rheology_decision_resolution_001/RESULTS.md#L121-L176)
- [L178–L234](https://github.com/trbrewer/puckworks/blob/9dd456be7fd797b9cda0a2bbf50d1ac717d72835/docs/analysis/val_case_rheology_decision_resolution_001/RESULTS.md#L178-L234)

##### `docs/cards/pannusch2024.md`

- [L1–L455](https://github.com/trbrewer/puckworks/blob/9dd456be7fd797b9cda0a2bbf50d1ac717d72835/docs/cards/pannusch2024.md#L1-L455)
- [L22–L60](https://github.com/trbrewer/puckworks/blob/9dd456be7fd797b9cda0a2bbf50d1ac717d72835/docs/cards/pannusch2024.md#L22-L60)

##### `docs/data/ESPRESSO_DATA_GUIDE.md`

- [L156–L201](https://github.com/trbrewer/puckworks/blob/9dd456be7fd797b9cda0a2bbf50d1ac717d72835/docs/data/ESPRESSO_DATA_GUIDE.md#L156-L201)
- [L431–L954](https://github.com/trbrewer/puckworks/blob/9dd456be7fd797b9cda0a2bbf50d1ac717d72835/docs/data/ESPRESSO_DATA_GUIDE.md#L431-L954)

##### `docs/governance/DECISION_RESOLUTION_POLICY.md`

- [L1–L1](https://github.com/trbrewer/puckworks/blob/9dd456be7fd797b9cda0a2bbf50d1ac717d72835/docs/governance/DECISION_RESOLUTION_POLICY.md#L1-L1)
- [L1–L242](https://github.com/trbrewer/puckworks/blob/9dd456be7fd797b9cda0a2bbf50d1ac717d72835/docs/governance/DECISION_RESOLUTION_POLICY.md#L1-L242)
- [L31–L108](https://github.com/trbrewer/puckworks/blob/9dd456be7fd797b9cda0a2bbf50d1ac717d72835/docs/governance/DECISION_RESOLUTION_POLICY.md#L31-L108)

##### `docs/governance/MINIMUM_NECESSARY_GOVERNANCE_STANDARD.md`

- [L1–L1](https://github.com/trbrewer/puckworks/blob/9dd456be7fd797b9cda0a2bbf50d1ac717d72835/docs/governance/MINIMUM_NECESSARY_GOVERNANCE_STANDARD.md#L1-L1)
- [L1–L359](https://github.com/trbrewer/puckworks/blob/9dd456be7fd797b9cda0a2bbf50d1ac717d72835/docs/governance/MINIMUM_NECESSARY_GOVERNANCE_STANDARD.md#L1-L359)
- [L304–L316](https://github.com/trbrewer/puckworks/blob/9dd456be7fd797b9cda0a2bbf50d1ac717d72835/docs/governance/MINIMUM_NECESSARY_GOVERNANCE_STANDARD.md#L304-L316)

##### `docs/paper1_resource/PAPER_1_PIVOT_AND_REDRAFT_PLAN_V2_2_1.md`

- [L105–L117](https://github.com/trbrewer/puckworks/blob/9dd456be7fd797b9cda0a2bbf50d1ac717d72835/docs/paper1_resource/PAPER_1_PIVOT_AND_REDRAFT_PLAN_V2_2_1.md#L105-L117)

##### `docs/paper1_resource/PAPER_A_PLAN_MANIFEST_V1.json`

- [L3–L4](https://github.com/trbrewer/puckworks/blob/9dd456be7fd797b9cda0a2bbf50d1ac717d72835/docs/paper1_resource/PAPER_A_PLAN_MANIFEST_V1.json#L3-L4)
- [L457–L457](https://github.com/trbrewer/puckworks/blob/9dd456be7fd797b9cda0a2bbf50d1ac717d72835/docs/paper1_resource/PAPER_A_PLAN_MANIFEST_V1.json#L457-L457)

##### `docs/research/ESPRESSO_DEVELOPMENT_GUIDE.md`

- [L1–L1](https://github.com/trbrewer/puckworks/blob/9dd456be7fd797b9cda0a2bbf50d1ac717d72835/docs/research/ESPRESSO_DEVELOPMENT_GUIDE.md#L1-L1)

##### `docs/research/ESPRESSO_PROGRAMME_REVIEW_2026-10-01.md`

- [L1–L1](https://github.com/trbrewer/puckworks/blob/9dd456be7fd797b9cda0a2bbf50d1ac717d72835/docs/research/ESPRESSO_PROGRAMME_REVIEW_2026-10-01.md#L1-L1)
- [L148–L157](https://github.com/trbrewer/puckworks/blob/9dd456be7fd797b9cda0a2bbf50d1ac717d72835/docs/research/ESPRESSO_PROGRAMME_REVIEW_2026-10-01.md#L148-L157)

##### `docs/research/ESPRESSO_THRESHOLD_AND_CAPABILITY_REVIEW_2026-10-09.md`

- [L240–L318](https://github.com/trbrewer/puckworks/blob/9dd456be7fd797b9cda0a2bbf50d1ac717d72835/docs/research/ESPRESSO_THRESHOLD_AND_CAPABILITY_REVIEW_2026-10-09.md#L240-L318)

##### `docs/status/current.json`

- [L1–L1](https://github.com/trbrewer/puckworks/blob/9dd456be7fd797b9cda0a2bbf50d1ac717d72835/docs/status/current.json#L1-L1)
- [L1–L502](https://github.com/trbrewer/puckworks/blob/9dd456be7fd797b9cda0a2bbf50d1ac717d72835/docs/status/current.json#L1-L502)
- [L131–L136](https://github.com/trbrewer/puckworks/blob/9dd456be7fd797b9cda0a2bbf50d1ac717d72835/docs/status/current.json#L131-L136)
- [L465–L497](https://github.com/trbrewer/puckworks/blob/9dd456be7fd797b9cda0a2bbf50d1ac717d72835/docs/status/current.json#L465-L497)

##### `puckworks/analysis/five_cqa_decision_resolution.py`

- [L186–L249](https://github.com/trbrewer/puckworks/blob/9dd456be7fd797b9cda0a2bbf50d1ac717d72835/puckworks/analysis/five_cqa_decision_resolution.py#L186-L249)
- [L263–L392](https://github.com/trbrewer/puckworks/blob/9dd456be7fd797b9cda0a2bbf50d1ac717d72835/puckworks/analysis/five_cqa_decision_resolution.py#L263-L392)

##### `puckworks/data/AVAILABLE_DATA_REGISTER.json`

- [L1–L3351](https://github.com/trbrewer/puckworks/blob/9dd456be7fd797b9cda0a2bbf50d1ac717d72835/puckworks/data/AVAILABLE_DATA_REGISTER.json#L1-L3351)
- [L72–L136](https://github.com/trbrewer/puckworks/blob/9dd456be7fd797b9cda0a2bbf50d1ac717d72835/puckworks/data/AVAILABLE_DATA_REGISTER.json#L72-L136)
- [L1939–L2086](https://github.com/trbrewer/puckworks/blob/9dd456be7fd797b9cda0a2bbf50d1ac717d72835/puckworks/data/AVAILABLE_DATA_REGISTER.json#L1939-L2086)
- [L2568–L2629](https://github.com/trbrewer/puckworks/blob/9dd456be7fd797b9cda0a2bbf50d1ac717d72835/puckworks/data/AVAILABLE_DATA_REGISTER.json#L2568-L2629)

##### `puckworks/data/LOCAL_CORPUS_SNAPSHOT.json`

- [L22–L109](https://github.com/trbrewer/puckworks/blob/9dd456be7fd797b9cda0a2bbf50d1ac717d72835/puckworks/data/LOCAL_CORPUS_SNAPSHOT.json#L22-L109)

##### `puckworks/harness.py`

- [L1–L1](https://github.com/trbrewer/puckworks/blob/9dd456be7fd797b9cda0a2bbf50d1ac717d72835/puckworks/harness.py#L1-L1)
- [L85–L102](https://github.com/trbrewer/puckworks/blob/9dd456be7fd797b9cda0a2bbf50d1ac717d72835/puckworks/harness.py#L85-L102)
- [L190–L231](https://github.com/trbrewer/puckworks/blob/9dd456be7fd797b9cda0a2bbf50d1ac717d72835/puckworks/harness.py#L190-L231)

##### `puckworks/models/__init__.py`

- [L486–L549](https://github.com/trbrewer/puckworks/blob/9dd456be7fd797b9cda0a2bbf50d1ac717d72835/puckworks/models/__init__.py#L486-L549)
- [L497–L498](https://github.com/trbrewer/puckworks/blob/9dd456be7fd797b9cda0a2bbf50d1ac717d72835/puckworks/models/__init__.py#L497-L498)

##### `puckworks/models/cameron2020/extraction_bdf.py`

- [L1–L1](https://github.com/trbrewer/puckworks/blob/9dd456be7fd797b9cda0a2bbf50d1ac717d72835/puckworks/models/cameron2020/extraction_bdf.py#L1-L1)
- [L9–L366](https://github.com/trbrewer/puckworks/blob/9dd456be7fd797b9cda0a2bbf50d1ac717d72835/puckworks/models/cameron2020/extraction_bdf.py#L9-L366)
- [L100–L113](https://github.com/trbrewer/puckworks/blob/9dd456be7fd797b9cda0a2bbf50d1ac717d72835/puckworks/models/cameron2020/extraction_bdf.py#L100-L113)
- [L130–L147](https://github.com/trbrewer/puckworks/blob/9dd456be7fd797b9cda0a2bbf50d1ac717d72835/puckworks/models/cameron2020/extraction_bdf.py#L130-L147)
- [L216–L239](https://github.com/trbrewer/puckworks/blob/9dd456be7fd797b9cda0a2bbf50d1ac717d72835/puckworks/models/cameron2020/extraction_bdf.py#L216-L239)
- [L254–L354](https://github.com/trbrewer/puckworks/blob/9dd456be7fd797b9cda0a2bbf50d1ac717d72835/puckworks/models/cameron2020/extraction_bdf.py#L254-L354)

##### `puckworks/product/_pull.py`

- [L1–L1](https://github.com/trbrewer/puckworks/blob/9dd456be7fd797b9cda0a2bbf50d1ac717d72835/puckworks/product/_pull.py#L1-L1)
- [L30–L110](https://github.com/trbrewer/puckworks/blob/9dd456be7fd797b9cda0a2bbf50d1ac717d72835/puckworks/product/_pull.py#L30-L110)
- [L55–L65](https://github.com/trbrewer/puckworks/blob/9dd456be7fd797b9cda0a2bbf50d1ac717d72835/puckworks/product/_pull.py#L55-L65)
- [L66–L73](https://github.com/trbrewer/puckworks/blob/9dd456be7fd797b9cda0a2bbf50d1ac717d72835/puckworks/product/_pull.py#L66-L73)

##### `puckworks/registry.py`

- [L31–L40](https://github.com/trbrewer/puckworks/blob/9dd456be7fd797b9cda0a2bbf50d1ac717d72835/puckworks/registry.py#L31-L40)

##### `puckworks/validation/decision_resolution.py`

- [L21–L102](https://github.com/trbrewer/puckworks/blob/9dd456be7fd797b9cda0a2bbf50d1ac717d72835/puckworks/validation/decision_resolution.py#L21-L102)

##### `puckworks/validation/gates.py`

- [L1–L1](https://github.com/trbrewer/puckworks/blob/9dd456be7fd797b9cda0a2bbf50d1ac717d72835/puckworks/validation/gates.py#L1-L1)
- [L9–L15](https://github.com/trbrewer/puckworks/blob/9dd456be7fd797b9cda0a2bbf50d1ac717d72835/puckworks/validation/gates.py#L9-L15)
- [L9–L78](https://github.com/trbrewer/puckworks/blob/9dd456be7fd797b9cda0a2bbf50d1ac717d72835/puckworks/validation/gates.py#L9-L78)
- [L17–L24](https://github.com/trbrewer/puckworks/blob/9dd456be7fd797b9cda0a2bbf50d1ac717d72835/puckworks/validation/gates.py#L17-L24)
- [L26–L42](https://github.com/trbrewer/puckworks/blob/9dd456be7fd797b9cda0a2bbf50d1ac717d72835/puckworks/validation/gates.py#L26-L42)
- [L44–L78](https://github.com/trbrewer/puckworks/blob/9dd456be7fd797b9cda0a2bbf50d1ac717d72835/puckworks/validation/gates.py#L44-L78)
- [L363–L376](https://github.com/trbrewer/puckworks/blob/9dd456be7fd797b9cda0a2bbf50d1ac717d72835/puckworks/validation/gates.py#L363-L376)
- [L859–L881](https://github.com/trbrewer/puckworks/blob/9dd456be7fd797b9cda0a2bbf50d1ac717d72835/puckworks/validation/gates.py#L859-L881)
- [L1170–L1195](https://github.com/trbrewer/puckworks/blob/9dd456be7fd797b9cda0a2bbf50d1ac717d72835/puckworks/validation/gates.py#L1170-L1195)
- [L1481–L1498](https://github.com/trbrewer/puckworks/blob/9dd456be7fd797b9cda0a2bbf50d1ac717d72835/puckworks/validation/gates.py#L1481-L1498)
- [L1517–L1520](https://github.com/trbrewer/puckworks/blob/9dd456be7fd797b9cda0a2bbf50d1ac717d72835/puckworks/validation/gates.py#L1517-L1520)

##### `pyproject.toml`

- [L1–L5](https://github.com/trbrewer/puckworks/blob/9dd456be7fd797b9cda0a2bbf50d1ac717d72835/pyproject.toml#L1-L5)

##### `tests/test_cameron_inventory.py`

- [L1–L40](https://github.com/trbrewer/puckworks/blob/9dd456be7fd797b9cda0a2bbf50d1ac717d72835/tests/test_cameron_inventory.py#L1-L40)

**Archival publication note — 19 October 2026 UTC (REVIEW-PW-EWP-20261018, G0):** this filing preserves the owner-supplied presentation-corrected review (663,603 bytes; input SHA-256 `1ff3341ea5a613a1dc09e7915579da7efe66126e677316f3619067e1ed56e0db`). Only the three embedded EWP scripts’ workspace derivation, one recorded rerun-command path, associated digest labels and Appendix A/B provenance wording were made portable, with this note and the Section 13 entry added. This archive is not byte-identical to the supplied file. Original execution receipts concern the original scripts; filing did not rerun them or change scientific findings, results or authority. R-01–R-08 remain proposals requiring separate decisions. The older original-review hash in the existing change log is historical provenance, not the verified input identity for this filing.
