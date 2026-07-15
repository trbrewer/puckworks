# visualizer.coffee data use for Puckworks

**Prepared:** 2026-07-15  
**Requested filename:** `visualizerCoffee_DATA_USE.md`  
**Scope:** source-code, API/schema, data-governance, scientific-use, validation, visualization, public-value, and publication review

---

## Executive assessment

The visualizer.coffee corpus can materially strengthen Puckworks, but its value is different from the value of a controlled laboratory dataset.

The corpus is strongest as:

1. **an empirical population of real espresso-machine boundary conditions and observed hydraulic trajectories**;
2. **an external ecological stress set for Puckworks models and assumptions**;
3. **a model-domain and relevance audit** showing which parts of real practice are covered, extrapolated, or missed;
4. **a machine/control-system dataset** because it exposes both commanded and achieved pressure/flow/temperature channels on many shots;
5. **a source of repeated-shot and natural-perturbation cohorts** that can generate discriminating hypotheses and select high-value controlled experiments;
6. **a flagship case study for Puckworks' evidence-aware software architecture, visualization rules, reproducibility system, and public-science narrative**.

It is much weaker as:

- direct ground truth for permeability, porosity, saturation, channeling, fines migration, swelling, or any other latent puck state;
- independent validation of extraction yield, total dissolved solids, or sensory models;
- evidence that a particular physical mechanism caused an observed trace;
- a basis for cross-grinder interpretation of grinder settings;
- a representative sample of all espresso users or all espresso shots.

The most important framing is:

> **Use visualizer.coffee as an empirical distribution over operating conditions and observed responses—not as a direct measurement of the hidden puck physics.**

That framing fits Puckworks unusually well. Puckworks already distinguishes models, observables, evidence strength, contracts, gates, and public-value outputs. It also already contains a Visualizer-specific harvester, provenance record, data-only card, and separate manifest entries for hydraulic telemetry and user-entered outcomes. The next step is therefore not merely “download a large dataset.” It is to convert an authorized corpus into a versioned, privacy-preserving, quality-audited reference population and then use it in ways that do not overclaim.

### Bottom-line recommendations

- **Make the first deliverable a corpus census and measurement-quality atlas, not a model fit.**
- **Freeze a named corpus snapshot before any paper-grade analysis.**
- **Repair several consequential intake issues before treating the current normalized store as canonical.** Most urgently, the current normalizer reads `timeframe` from `data.timeframe`, while the current Visualizer schema and serializer place it at top level; this can make valid live traces appear to have no time base. Other issues include unauthenticated incremental-update logic, record revision handling, valid zero sensory values, ambiguous flow quantity types, mixed-type time-series samples, moving pagination, and residual free-text/linkability risks.
- **Create a separate observed-telemetry contract rather than forcing these records into Puckworks' latent physical-state contracts.**
- **Anchor population analyses to controlled datasets or a controlled machine bench experiment.** Visualizer should extend external relevance and stress-testing; it should not silently replace Puckworks' independent validation gates.
- **Prioritize Paper B and the Puckworks methods/resource paper.** Visualizer has a supporting role in Paper A and a potentially central role in a narrower temporal-inference Paper B and in a third executable-evidence/resource paper.
- **Publish code, definitions, snapshot metadata, and privacy-safe aggregates—not the raw user-contributed corpus—unless redistribution is separately and explicitly authorized.**

---

## 1. Review scope, evidence, and important caveat

This assessment reviewed the public Visualizer application and repository, Visualizer API specification, Visualizer database schema, and relevant current Puckworks code and documentation, including:

- the Visualizer shot API and its native/Beanconqueror response schemas;
- the available hydraulic, goal, temperature, weight, state, scalar-context, outcome, tag, profile, and source-native `brewdata` fields;
- structured coffee-bag and roaster entities present in the Visualizer schema;
- Puckworks' component registry, typed contracts, validation harness/gates, roadmap, public-value plan, publication strategy, paper drafts, Visualizer data card, provenance record, manifest rows, harvester, tests, and visualization architecture.

**This was not a statistical analysis of a completed full-corpus harvest.** The reviewed Puckworks repository describes the harvest as in progress, and its tracked aggregate artifact was still effectively a placeholder at the reviewed state. Therefore, this report makes design and scientific-use recommendations but does not claim corpus-wide counts, prevalence estimates, device shares, channel coverage, or outcome frequencies. Those must be generated from the completed, frozen, quality-audited corpus.

This report also assumes that the permission described in Puckworks applies to the **public-shot corpus accessed through the documented API**, subject to the stated attribution, rate-limit, privacy, and non-redistribution posture. It does not assume permission to ingest private shots, private notes, account records, email addresses, or unrelated user data. A separate owner-provided database export could be scientifically useful, but its exact field scope, retention rules, deletion obligations, and redistribution terms should be documented before use.

---

## 2. What the Visualizer corpus can contain

### 2.1 Four analytically distinct layers

The Visualizer data should not be treated as one undifferentiated “shot” table. It contains at least four layers with different evidence properties.

| Layer | Examples | Scientific value | Main limitation |
|---|---|---|---|
| **Machine/hydraulic trajectories** | time, achieved pressure, achieved flow, scale-derived flow, beverage weight, water dispensed, basket/mix temperature, machine state | High for operating envelopes, controller behavior, phase segmentation, dynamic resistance phenotypes, model stress tests | Cross-device sensor meaning/calibration varies; puck and machine effects are entangled |
| **Commanded trajectories** | pressure goal, flow goal, temperature goal, shot profile | Very high for separating requested behavior from achieved behavior and identifying controller/machine limitations | Goal semantics and control modes differ by source/device |
| **Shot context** | dose, beverage mass, duration, profile title, grinder model/setting, roast level, tags, source-native `brewdata`, coffee-bag/roaster IDs | Useful for blocking, stratification, repeated-shot cohorts, source parsing, profile families, and measurement-quality analysis | Many values are optional, free text, nonstandard, or nonportable |
| **User-entered outcomes** | TDS, extraction yield, enjoyment and sensory sliders | Useful for algebraic consistency checks, within-user repeatability, missingness analysis, and exploratory hypothesis generation | Unknown instruments/protocols; sparse; self-reported; not inter-rater calibrated; selected not at random |

A fifth layer may be available under an explicitly authorized export or authenticated scope:

| Layer | Examples | Potential value | Caution |
|---|---|---|---|
| **Structured coffee/roaster metadata** | canonical coffee bag, country, region, farm/farmer, processing, variety, elevation, harvest, roast level, roaster | Stronger same-coffee blocking; ecological effect modification; normalization of free-text coffee identity | Public shot records expose IDs, but detailed coffee-bag/roaster access and bulk use require scope confirmation; many fields are contextual, not causal physical parameters |

### 2.2 Time-series channels exposed by the documented shot schema

The API specification describes common series including:

- `espresso_pressure`
- `espresso_flow`
- `espresso_flow_weight`
- `espresso_weight`
- `espresso_pressure_goal`
- `espresso_flow_goal`
- `espresso_temperature_goal`
- `espresso_temperature_mix`
- `espresso_temperature_basket`
- `espresso_water_dispensed`
- `espresso_state_change`
- a shared time vector

The source-native `brewdata` payload is especially important. It is not merely redundant storage: it is the best path to source-specific interpretation, parser/version detection, device taxonomy, raw units, control semantics, and schema-drift auditing. A normalized table should preserve a private pointer/hash to the exact authorized source payload and record which source-specific parser produced every normalized channel.

The API's generic time-series item type allows numbers, strings, booleans, and nulls. That matters operationally: a corpus harvester must parse individual samples tolerantly and record sample-level failures instead of assuming that every non-null series element can be converted with `float()`.

### 2.3 Why commanded and achieved channels are unusually valuable

Many public espresso datasets provide only an achieved pressure curve or a final recipe. Visualizer often provides both requested and achieved values. This enables analyses that are directly aligned with Puckworks' “machine can mimic puck behavior” theme:

- target-tracking error;
- controller lag and overshoot;
- saturation or clipping of machine capabilities;
- pressure-control versus flow-control behavior;
- profile transitions and phase timing;
- machine-side causes of flow dips, recoveries, oscillations, or apparent resistance changes;
- separation of “the profile asked for this” from “the coupled machine–puck system produced this.”

This is arguably the corpus' highest-value contribution to Puckworks.

### 2.4 The corpus is moving, selected, and heterogeneous

The public feed is continuously updated. Public shots are selected by users, and selection may favor successful shots, experiments, troubleshooting cases, unusual profiles, and users with compatible logging hardware. Device/source prevalence, firmware, parser behavior, machine ownership, user practices, and platform features can all drift over time.

Consequences:

- “number of shots” is not the effective sample size;
- heavy contributors can dominate a shot-weighted analysis;
- public shots are not a random sample of all Visualizer shots or all espresso shots;
- the same user, coffee, machine, and profile can generate many highly dependent records;
- field availability can depend on device integration and time period;
- a result discovered on one snapshot should be tested on a later, frozen snapshot or a controlled dataset.

---

## 3. What Puckworks already gets right

Puckworks has already established a strong conceptual posture for this source.

### 3.1 It treats Visualizer as data-only

The current Visualizer card explicitly avoids registering the corpus as a physical component and avoids attaching a physics validation gate. That is correct. A large observational corpus is not a constitutive law, and its size does not change its evidence class.

### 3.2 It separates hydraulic telemetry from user outcomes

The two Puckworks manifest entries—one for hydraulic time series and one for user outcomes—prevent machine-logged measurements and uncalibrated user-entered labels from being merged into a single misleading notion of “ground truth.” This separation should remain structural all the way through storage, access control, analysis, and visualization.

### 3.3 It uses appropriate evidence language

The card describes the hydraulics as measured but uncontrolled, self-selected, reference-strength population data. It describes TDS/EY/sensory as hypothesis/cross-reference information rather than a validation gate. That wording is scientifically defensible and should be carried into papers, figure badges, captions, dashboards, and data-availability statements.

### 3.4 It has a privacy and provenance posture

The current intake design:

- uses a salted one-way user linkage;
- drops named identity and obvious notes fields;
- keeps raw harvested records out of the repository;
- records authorization, attribution, and share-back expectations;
- tracks units and ambiguity flags;
- rate-limits and resumes the crawl;
- keeps the harvester outside normal validation-gate execution.

Those are good foundations. The recommendations below tighten rather than replace that architecture.

### 3.5 It already identifies sensible targets

The Puckworks roadmap/card points to three appropriate initial uses:

- an ecological machine pressure–flow envelope supporting the pump-characteristic gap;
- population hydraulic variability for temporal-model stress tests;
- a population view of inertial/Forchheimer relevance.

These are valid, but each requires explicit measurement and identifiability caveats. In particular, a pressure–flow operating envelope measured while a puck is present is not automatically a pump characteristic, and a Forchheimer-like curve is not automatically an independently identified inertial permeability.

---

## 4. The central scientific distinction: stress-testing versus validation

The corpus can support several levels of scientific use. Calling all of them “validation” would erase important distinctions.

### Level A — Data integrity and measurement validation

Questions:

- Is time monotone and physically plausible?
- Are channel lengths aligned?
- Are units and quantity types known?
- Do weight and scale-derived flow agree after accounting for filtering/lag?
- Are goal and achieved channels semantically compatible?
- Are fields stable across parser/device versions?
- Are TDS, dose, beverage mass, and reported EY algebraically consistent?

This validates the **data pipeline and measurement interpretation**, not a puck model.

### Level B — Model-domain coverage and external relevance

Questions:

- What fraction of eligible shots lies inside a model's declared pressure, flow, temperature, dose, duration, and control-mode range?
- Which regions of actual practice are extrapolations?
- Are the literature model's nominal conditions central, rare, or outside the observed population?

This tests whether a model is relevant to real use, not whether its hidden mechanism is correct.

### Level C — Ecological external stress test

Questions:

- After models and feature definitions are frozen, how often do they violate physical constraints on held-out real traces?
- Which observed trajectory phenotypes cannot be represented by a specified static null?
- Do residual patterns recur across users, machines, and profile families?
- Does a model calibrated on controlled data maintain qualitative or quantitative performance across the population?

This is stronger than an internal fit, but weaker than controlled mechanism validation because confounding remains.

### Level D — Controlled independent validation

Questions:

- Under a preregistered experiment with known geometry, calibrated sensors, controlled coffee/grind/preparation, and held-out conditions, does the model predict the outcome within uncertainty?

Visualizer cannot by itself supply this level for most Puckworks mechanisms. It can identify the most relevant regimes and candidate perturbations for such experiments and can show whether controlled findings matter at population scale.

### Recommended wording

Use:

- “external ecological stress test”
- “reference population”
- “population operating envelope”
- “model-domain coverage audit”
- “held-out observational cohort”
- “hypothesis-generating association”
- “controlled-anchor transfer assessment”

Avoid:

- “millions-shot validation”
- “ground truth permeability”
- “channeling labels”
- “causal effect of profile/grinder/roast”
- “representative of espresso users”
- “proof of swelling/fines migration/poroelasticity”

---

## 5. Component-by-component opportunities in Puckworks

### 5.1 Machine stage

Relevant Puckworks components include `foster2025.machine_mode` and `sourcing2026.g3_pump_characteristic`.

#### High-value uses

1. **Commanded-versus-achieved tracking atlas**
   - pressure-goal error as a function of time, phase, goal slope, achieved flow, and machine/source;
   - flow-goal error under flow control;
   - response lag, overshoot, settling time, clipping, oscillation, and transition behavior;
   - target-tracking behavior at preinfusion, ramps, holds, declines, pauses, and end conditions.

2. **Empirical operating envelope**
   - joint density of achieved pressure and flow;
   - achieved pressure/flow conditional on command and control mode;
   - machine/source-specific coverage of the P–Q plane;
   - rare or unsupported operating regions.

3. **Machine-null construction and stress testing**
   - identify flow dips/recoveries explainable by controller and headspace dynamics without invoking changing puck permeability;
   - compare observed traces with the frozen Foster machine-mode null;
   - characterize residuals after accounting for target profiles and machine response.

4. **Controlled bench experiment design**
   - use the population to select representative target combinations for the planned pump/headspace bench work;
   - choose tests at dense operating regions plus high-leverage boundaries rather than arbitrary profiles;
   - quantify how much of the population a calibrated bench envelope would cover.

5. **Source-specific transfer functions**
   - estimate empirical command-to-achieved relationships within clearly defined machine/source classes;
   - detect integration/parser changes over time;
   - do not collapse all devices into one “espresso machine” model.

#### Important limit

A puck-loaded pressure–flow trace is a coupled observation of pump, controller, plumbing, headspace, puck resistance, basket/screen resistance, and sensors. It is not an independent pump curve. The population envelope can constrain plausible machine behavior and select bench conditions, but a controlled free-flow/deadhead/intermediate-load experiment remains necessary to identify a machine characteristic.

#### Concrete Puckworks output

Create a `visualizer_machine_tracking` analysis product with:

- source/device class;
- inferred control mode by phase;
- target and achieved trajectories;
- pressure and flow lag estimates;
- tracking RMSE/MAE normalized by target range;
- overshoot and saturation indicators;
- phase-transition residuals;
- evidence label: **observed, uncontrolled, ecological**.

### 5.2 Infiltration stage

Relevant component: `foster2025.infiltration`.

#### Potential observables

- onset of pressure rise;
- first machine-reported flow;
- first sustained positive scale-derived flow;
- first beverage-weight increase;
- preinfusion duration;
- pressure and water integrals before first beverage mass;
- pauses/blooms and subsequent recovery;
- timing between state transitions and observed flow/weight response.

These can produce a population distribution of fill/onset proxies and identify profiles that generate especially informative infiltration trajectories.

#### Uses

- check whether the component's declared validity range overlaps actual profile families;
- test whether predicted ordering of onset events is physically compatible with observed traces;
- identify outlying traces for manual source/parser review or controlled replication;
- select natural cohorts with similar dose/profile but different preinfusion schedules;
- estimate how strongly first-weight timing varies within repeated-profile/user groups.

#### Limits

First scale movement is not a direct wetting-front measurement. It is affected by basket and cup travel time, drips, scale filtering, auto-tare behavior, machine plumbing, and signal processing. Visualizer cannot directly observe partial saturation or front position. Use terms such as “first-flow proxy” and “first-weight proxy,” not “saturation time,” unless a source-specific calibration supports that mapping.

### 5.3 Flow stage: Darcy, inertial, and feedback models

Relevant components include `wadsworth2026.inertial`, `lee2023.feedback`, the lattice-Boltzmann references, and machine/flow couplings.

#### High-value uses

1. **Observed P–Q domain audit**
   - quantify the pressure and flow combinations under which espresso is actually operated;
   - compare them with each flow model's valid range;
   - identify where inertial contributions might plausibly matter.

2. **Apparent resistance trajectories**
   - where pressure-node meaning and flow quantity are sufficiently known, compute an explicitly labeled apparent resistance such as `R_app(t) = ΔP(t)/Q(t)` above a minimum-flow threshold;
   - analyze `log R_app`, derivatives, monotonicity, and phase changes;
   - never silently interpret this as intrinsic bed permeability.

3. **Segment-local Darcy/Forchheimer comparison**
   - within carefully selected quasi-stationary phases, compare `ΔP = aQ` with `ΔP = aQ + bQ²`;
   - use robust errors and account for time dependence;
   - report `a` and `b` as effective coupled-shot coefficients unless geometry, fluid properties, pressure nodes, and machine contribution are independently resolved.

4. **Control-mode stratification**
   - pressure control and flow control impose different observational constraints;
   - analyze them separately because identical bed dynamics can appear differently under feedback;
   - use goal channels to classify phase-level control mode rather than relying only on profile titles.

5. **Feedback signatures**
   - pressure/flow decoupling;
   - oscillation and phase lag;
   - controller saturation;
   - resistance changes masked by flow control or amplified by pressure control.

#### Limits

- `espresso_flow` can be volumetric for some sources and mass flow for others. It should not be converted to kg/s merely because the numeric scale resembles g/s.
- `espresso_flow_weight` is scale-derived mass flow and is often more interpretable, but it includes differentiation/filtering/lag and should be cross-checked against beverage weight.
- Bed area, depth, viscosity, screen resistance, and pressure-node identity are generally missing. Intrinsic permeability and inertial permeability are therefore not independently identified from most records.

### 5.4 Bed dynamics

Relevant components include:

- `waszkiewicz2025.poroelastic`
- `brewer2026.coupled_kappa_t`
- `fasano2000_partI.fines_migration`
- `mo2023_2.swelling`
- `brewer2026.streamtube`

This is the area in which the corpus is most tempting to overinterpret. It can strongly support **phenomenology and model discrimination design**, but it usually cannot identify the unique hidden mechanism.

#### Strong uses

1. **Dynamic-resistance phenotype atlas**
   - rising resistance;
   - falling resistance;
   - U-shaped or inverted-U behavior;
   - step changes;
   - oscillatory behavior;
   - pressure–flow hysteresis;
   - flow collapse or runaway under approximately stable commands;
   - disagreement between machine flow and scale-derived flow.

2. **Static-null adequacy test**
   - freeze a static bed/machine null and evaluate held-out eligible traces;
   - quantify how often a defined trajectory class requires temporal flexibility relative to that null;
   - distinguish “time variation is needed” from “a named mechanism is proved.”

3. **Residual fingerprinting**
   - cluster residual curves after accounting for commanded profile and machine response;
   - test whether fingerprints recur across users, devices, and profile families;
   - use recurrence to prioritize mechanisms and experiments.

4. **Sign constraints by control mode**
   - under pressure control, increasing resistance tends to reduce flow;
   - under flow control, increasing resistance tends to increase required pressure until machine limits intervene;
   - compare observed sign patterns with model predictions while retaining machine/control uncertainty.

5. **Natural perturbation discovery**
   - find repeated-profile cohorts with pressure changes, pauses, blooms, rebrew-like behavior, or profile reversals;
   - use these as hypothesis-generating analogues for Puckworks' planned discriminating experiments.

6. **Population prevalence after controlled definition**
   - once a phenotype and threshold are defined using controlled data or an earlier snapshot, estimate its prevalence in a later frozen population snapshot;
   - report both shot-weighted and user-weighted prevalence.

#### What the corpus cannot resolve alone

The same integrated pressure/flow/weight trace can be compatible with swelling, dissolution, poroelastic compaction, fines migration, channel formation, screen effects, machine feedback, or combinations. Visualizer should therefore support claims like:

> “A specified static closure is inadequate for this defined observational cohort.”

It should not support claims like:

> “The cohort proves that fines migration is the cause.”

### 5.5 Grind and packing

Relevant components include `wadsworth2026.grindmap`, `wadsworth2026.permeability`, and `brewer2026.pack_generator`.

#### Useful opportunities

- quantify how nonportable grinder-setting fields are across grinder models;
- identify within-user, within-grinder, within-coffee dial sequences;
- fit local monotone adapters only where repeated data support them;
- measure within-setting variability and detect whether nominally identical recipes occupy broad hydraulic regimes;
- select representative grind/packing conditions for controlled particle-size and permeability experiments;
- test whether Puckworks' literature validity ranges encompass the observed dose/flow/pressure regimes associated with named grinder classes.

#### Hard limit

A grinder dial is not a particle-size distribution. Cross-grinder numeric settings cannot be pooled as a continuous grind variable. Even within one grinder model, burr alignment, burr type, zero point, calibration, seasoning, and user notation differ. Visualizer can support **within-unit ordering and repeatability analyses** and reinforce Puckworks' public message that grinder dials are not universal units; it cannot replace PSD measurements.

### 5.6 Extraction models

Relevant components include `cameron2020.extraction_bdf`, `pannusch2024.solver`, `grudeva2025.reduced`, `moroney2016.surrogate`, `romancorrochano2017.extraction`, `liang2021.desorption`, and `mo2023_2.coupled_bed`.

#### Strongest use: forcing and domain relevance

Visualizer's achieved flow, pressure, temperature, dose, beverage mass, and duration can define realistic forcing trajectories and operating domains for forward simulations. Specific uses include:

- replacing idealized constant-flow or nominal-temperature inputs with measured forcing in clearly labeled sensitivity runs;
- comparing model output under observed versus nominal profiles;
- auditing whether literature-valid flow/temperature/grind ranges cover the observed population;
- generating a library of representative forcing trajectories by profile/control/device class;
- testing numerical robustness across real irregular time grids and transitions;
- identifying operating regions for which no current extraction model has a defensible validity claim.

This can improve Puckworks even without trusting any reported extraction outcome.

#### User-entered TDS and EY

These fields are useful for:

1. **Algebraic consistency checks**
   - compare reported EY with the value implied by TDS, beverage mass, and dose under the stated convention;
   - classify consistent, inconsistent, convention-ambiguous, and insufficient records;
   - do not automatically overwrite the user's value.

2. **Measurement reliability studies**
   - within-user repeated-shot variability;
   - within-coffee/profile repeatability;
   - sensitivity to missing/dirty dose and beverage fields;
   - temporal drift suggestive of instrument or protocol changes.

3. **Exploratory associations**
   - after within-user centering and strict grouping, examine associations between trajectory features and outcomes;
   - use hierarchical models and user-level calibration terms;
   - treat results as targets for controlled replication.

4. **Outcome-observation design**
   - quantify how rarely endpoint chemistry is recorded relative to hydraulic telemetry;
   - demonstrate the mismatch between rich time-resolved hydraulics and sparse endpoint chemistry;
   - motivate temporally resolved chemical measurements and Puckworks Paper A's observation-design thesis.

They should not be used to claim external validation of a mechanistic extraction model unless a protocol-qualified subset can be independently established.

#### Sensory fields

Sensory sliders can support:

- within-user preference consistency;
- ordinal, user-centered exploratory models;
- missingness/selection analysis;
- hypothesis generation for controlled tasting.

They should not be treated as inter-rater calibrated sensory scores, universal utility, or objective cup quality. A model trained to predict them would mainly learn who records ratings, personal scale usage, device/profile preferences, and other confounding unless the design is very carefully restricted.

### 5.7 Temperature and thermal context

The basket, mix, and goal temperature channels can support:

- target-tracking and transient response by device/source;
- temperature-domain coverage for extraction closures;
- phase-level temperature stability metrics;
- interaction analyses between flow regime and measured temperature;
- selection of real thermal trajectories for model forcing.

However, basket-sensor temperature is not necessarily puck-fluid temperature. Sensor placement, filtering, source semantics, and machine thermal architecture must be recorded. Source-specific interpretation is essential.

### 5.8 Structured coffee context

The Visualizer database schema includes canonical and user coffee-bag entities with fields such as country, region, farm/farmer, processing, variety, elevation, harvest information, roast level, roaster, and tasting notes. Public shot detail can carry roaster and coffee-bag IDs.

With explicit authorization and a documented access route, structured coffee context could support:

- matching repeated shots from the same coffee more reliably than free text;
- blocking or random effects for coffee bag and roaster;
- ecological stratification by roast or process;
- identification of underrepresented contexts;
- testing whether model residuals differ systematically by broad coffee context;
- recruitment/selection of coffees for controlled follow-up.

It should be treated as contextual effect modification, not as a direct physical parameterization of solubility, permeability, or swelling. Tasting notes and user-entered bag notes should remain excluded or tightly governed because they are free text and may carry identification or subjective information. Canonical entities are preferable to user-specific records wherever possible.

---

## 6. A recommended validation and inference design

### 6.1 Controlled anchor plus population transfer

A robust Puckworks design would use the following sequence:

1. **Use controlled literature or bench data to define and, where appropriate, calibrate a model.**
2. **Freeze equations, parameters or fitting rules, inclusion criteria, feature definitions, and error metrics.**
3. **Apply the frozen analysis to an eligible Visualizer snapshot.**
4. **Measure coverage, constraint violations, residual structure, and phenotype prevalence.**
5. **Use population residuals to design a discriminating controlled experiment.**
6. **Test the mechanism under control, then return to the population to assess external relevance.**

This creates a productive loop:

> controlled identification → ecological stress test → experiment selection → controlled discrimination → population relevance

### 6.2 Separate discovery and confirmation snapshots

Because the corpus is continuously growing, it can support temporal confirmation if handled carefully.

- **Discovery snapshot:** develop parsers, QC rules, phenotypes, and hypotheses.
- **Frozen confirmation snapshot:** later records not used in rule creation.
- **Controlled confirmation:** where causal/mechanistic claims require it.

Do not repeatedly inspect a single corpus and describe the final thresholds as preregistered. Record the exact snapshot cutoff, API version, harvester commit, normalizer version, and query/feature code commit.

### 6.3 Group-aware splits

Random shot-level train/test splits would leak heavily. Split or cluster by:

- internal pseudonymous user group;
- machine/source class;
- profile signature;
- coffee-bag ID where available;
- grinder unit/model where defensible;
- time period;
- repeated-shot sequence.

Useful stress splits include:

- leave-user-out;
- leave-machine-family-out;
- leave-profile-family-out;
- temporal holdout;
- leave-coffee-out for coffee-qualified subsets;
- leave-control-mode-out for transfer claims.

### 6.4 Weighting and effective sample size

Always report at least:

- raw shot count;
- unique internal user-group count;
- machine/source count;
- profile-family count;
- median and upper-tail shots per user;
- shot-weighted estimates;
- user-balanced estimates;
- cluster-bootstrap or hierarchical uncertainty.

A corpus with many shots from a few contributors can have excellent trace diversity but a much smaller effective sample size for user-level or practice-level claims.

### 6.5 Missingness is part of the scientific result

TDS, EY, sensory ratings, grinder context, roast fields, and some channels are not missing at random. Model the probability that an outcome is recorded as a function of observable source, user activity, profile, date, and shot context. Report outcome analyses conditional on recording rather than pretending the observed subset is representative.

Do not impute missing user outcomes for causal or validation claims. Imputation may be useful for engineering dashboards, but it should not manufacture evidence.

### 6.6 Suggested external stress-test scorecard

For each Puckworks model, report:

| Dimension | Question |
|---|---|
| **Eligibility** | What records have the required observables and interpretable units? |
| **Domain coverage** | What share lies inside the model's declared validity range? |
| **Physical validity** | Does the model violate mass, sign, monotonicity, or bound constraints? |
| **Trajectory fit** | How well does it represent held-out observed trajectories under fixed rules? |
| **Uncertainty calibration** | Do prediction intervals cover at their stated rate? |
| **Residual structure** | Are errors systematic by phase, device, profile, user, or control mode? |
| **Transfer** | Does performance hold for unseen users/machines/profiles/time periods? |
| **Sensitivity** | Are conclusions stable to channel choice, time alignment, pressure-node assumption, and unit ambiguity? |
| **Evidence ceiling** | What can and cannot be inferred given the observational design? |

A model can score well on domain coverage and physical validity while still lacking mechanism identification. Preserve those distinctions.

---

## 7. High-priority analyses and data products

### Priority 0 — Corpus census and quality atlas

This should be the first full-corpus product and the basis for all later inclusion criteria.

Report:

- total current records and unique latest-version records;
- public-shot date range and update-date range;
- records by source parser, machine class, and API/payload schema version;
- records and users by year/month;
- shots per internal user group and concentration metrics;
- channel availability matrix by source and period;
- time-grid sampling-rate distributions;
- nonmonotone or duplicate timestamps;
- channel-length mismatches;
- mixed-type and unparseable sample rates;
- pressure, flow, weight, temperature, dose, beverage, and duration plausibility flags;
- `espresso_flow` quantity-kind certainty;
- scale-flow versus differentiated-weight agreement;
- goal-channel availability and control-mode inferability;
- duplicate IDs, updated revisions, deleted/unavailable records, and latest-wins compaction results;
- free-text and identifier privacy review;
- TDS/EY/sensory coverage and consistency;
- profile, device, and user concentration;
- snapshot hash and software versions.

This product has independent public value. It tells the Visualizer community which integrations are complete and comparable and tells Puckworks what the corpus can honestly support.

### Priority 1 — Measurement ontology and source/device dictionary

Create a maintained table for every source parser/device class:

- source detection rule;
- raw payload version/signature;
- pressure node and gauge/absolute status;
- flow quantity type and raw unit;
- scale-flow derivation/filter behavior where known;
- temperature sensor meaning;
- goal semantics;
- state-code meanings;
- expected sample rate;
- known firmware/parser transitions;
- confidence and provenance;
- eligible analyses.

Unknown should be an explicit category, not coerced into the majority convention.

### Priority 2 — Commanded/achieved controller atlas

This is likely the most immediately publishable Visualizer–Puckworks scientific product.

For eligible source classes:

- goal-versus-achieved overlays by phase;
- lag, overshoot, settling, saturation, and tracking errors;
- error distributions across pressure and flow goals;
- effect of simultaneous flow/pressure conditions;
- pressure-control and flow-control comparisons;
- device/source and profile-family variation;
- user-balanced as well as shot-weighted summaries;
- example traces chosen by prespecified quantiles, not visual appeal.

### Priority 3 — Real-world operating envelope and model-domain map

Produce joint distributions of:

- pressure × scale-derived flow;
- pressure × machine-reported flow, separated by known quantity kind;
- flow × temperature;
- dose × beverage mass;
- duration × beverage ratio;
- phase-level rather than only shot-level operating points.

Overlay each Puckworks component's declared valid region. The result is a concrete inventory of:

- well-covered regions;
- extrapolation regions;
- unsupported common regimes;
- literature regimes that are rare in actual use;
- regimes that should guide new controlled experiments.

### Priority 4 — Shot-phase segmentation library

Develop source-aware segmentation into observable phases such as:

- idle/baseline;
- fill/pressurization;
- preinfusion;
- ramp;
- pressure hold;
- flow hold;
- decline;
- pause/bloom;
- end/depressurization.

Use state codes when reliable and goal/achieved change points otherwise. Store phase boundaries, confidence, and method. This is a prerequisite for interpretable cross-shot features; whole-shot averages will obscure the dynamics Puckworks is trying to understand.

### Priority 5 — Dynamic hydraulic resistance phenotype atlas

After quality filtering and source stratification:

- define apparent-resistance features with explicit pressure-node/flow assumptions;
- classify trajectory shapes using interpretable features first;
- use functional PCA or clustering as a secondary descriptive tool;
- publish median and uncertainty bands for clusters;
- quantify stability across clustering choices;
- test recurrence in held-out time periods and machine families;
- manually audit representative source payloads.

Do not name clusters after mechanisms until controlled discrimination supports the names. Use neutral labels such as “late resistance decline” or “mid-shot pressure–flow decoupling.”

### Priority 6 — Controlled-versus-ecological bridge

Pair the planned machine bench/pump-characteristic experiment and controlled Puckworks fixtures with Visualizer distributions:

- show where controlled traces lie in the population envelope;
- assess which ecological regimes the bench calibration covers;
- quantify the machine contribution before interpreting bed changes;
- use population density to weight the practical relevance of controlled findings.

### Priority 7 — Model residual and null-ladder study

For a preregistered eligible cohort:

1. profile/goal-only baseline;
2. machine-only dynamic null;
3. static hydraulic bed closure;
4. flexible time-varying effective resistance;
5. selected mechanistic bed models where observables permit.

Compare predictive performance on grouped holdouts, but preserve the distinction between a flexible temporal comparator and a physical mechanism. This analysis is a natural bridge to the narrower Paper B.

### Priority 8 — Repeated-shot cohorts

Build privacy-preserving internal cohort keys for:

- user × machine × profile signature;
- user × machine × coffee-bag ID × profile;
- user × grinder × coffee × near-adjacent time;
- explicit natural perturbation families.

Use these to estimate:

- within-group repeatability;
- between-group variation;
- local effects of target pressure/flow changes;
- measurement noise;
- outcome recording consistency;
- candidate controlled protocols.

### Priority 9 — Outcome consistency and exploratory modeling

Only after the hydraulic and scalar pipeline is stable:

- reported versus algebraically reconstructed EY;
- within-user TDS/EY repeatability;
- instrument/protocol change-point candidates;
- outcome missingness model;
- hierarchical, user-centered associations;
- explicit exploratory badge and separate output tables.

### Priority 10 — Privacy-safe public dashboard and community report

A public product could show:

- corpus/channel census;
- machine/source coverage;
- goal-tracking distributions;
- operating envelopes;
- model-domain coverage;
- neutral trajectory phenotypes;
- data quality and known limitations;
- controlled versus ecological evidence labels;
- no raw shot IDs, exact user trajectories, unique profile names, or small identifying cells.


---

## 8. Intake and engineering review: issues to resolve before canonical use

The existing Puckworks intake is thoughtful: it rate-limits, resumes, separates hydraulic telemetry from user outcomes, records units, drops several direct identifiers, keeps raw derivatives out of Git, and is deliberately excluded from physics gates. However, a source-level comparison against the current Visualizer API reveals several issues that can materially alter the harvested corpus or its scientific interpretation.

### 8.1 P0: the current normalizer appears to read `timeframe` from the wrong location

This is the most consequential finding in the review.

The current [Visualizer OpenAPI schema](https://github.com/miharekar/visualizer/blob/main/openapi.yaml) places `timeframe` at the **top level** of a shot-detail response, alongside `data`. The current [Visualizer shot serializer](https://github.com/miharekar/visualizer/blob/main/app/models/shot/jsonable.rb) likewise adds:

```text
shot.timeframe
shot.data
```

when chart data are available. By contrast, the [Puckworks normalizer](https://github.com/trbrewer/puckworks/blob/main/puckworks/lib/visualizer_harvest.py) currently does conceptually this:

```python
data = raw.get("data") or {}
timeframe = data.get("timeframe")
```

That expects `data.timeframe`, not the documented top-level `timeframe`. The Puckworks tests appear to use synthetic fixtures following the nested assumption, so they do not establish compatibility with the live API contract.

**Likely consequence:** live records may retain pressure/flow arrays under `data` while being marked `missing:timeframe`, assigned `n_samples = 0`, and deprived of the shared time vector. Depending on downstream filters, this could make a successful crawl look like a corpus with little or no usable time-series data.

**Required action:** verify immediately against a small authorized live sample, then support both layouts during migration:

```python
timeframe = raw.get("timeframe")
if timeframe is None:
    timeframe = (raw.get("data") or {}).get("timeframe")  # legacy/fixture fallback
```

Add a contract test generated from a real, redacted API response and a schema-conformance test against `openapi.yaml`. Update the Puckworks provenance field map from `data.timeframe` to top-level `timeframe`. Do not begin paper-grade corpus statistics until this is resolved and any already-normalized records are reprocessed.

### 8.2 P0: unauthenticated `updated_after` does not implement the current incremental strategy

The Puckworks incremental crawl sends `updated_after=<cursor>` while accessing the public API without authentication. Visualizer's [API documentation](https://github.com/miharekar/visualizer/blob/main/openapi.yaml) states that `updated_after` applies only to authenticated requests, and the [shots controller](https://github.com/miharekar/visualizer/blob/main/app/controllers/api/shots_controller.rb) applies the filter only when a current user is present. For a public unauthenticated crawl, the parameter is therefore ignored even though sorting by `updated_at` still works.

This has two implications:

1. “Incremental” can re-list the entire public corpus rather than only changed records.
2. Appending every fetched revision can inflate counts and silently create multiple versions of the same shot.

Recommended options, in order of robustness:

1. **Owner-provided immutable snapshot plus periodic delta or tombstone export.** This is best for reproducible science and minimizes API load.
2. **A sanctioned read token or API enhancement** that permits a public-corpus `updated_after` filter under the agreed research scope.
3. **Newest-first cutoff scan:** sort by `updated_at`, scan from page 1, and stop only after an overlap window of records all predate the previous high-water mark and their `(id, updated_at)` versions are already known. Because timestamps can tie, use an overlap rather than a single timestamp comparison.
4. **Periodic full reconciliation:** perform a complete public-ID re-scan at scheduled snapshot boundaries to find deletions, privacy changes, and missed updates.

The current documentation should not describe unauthenticated incremental mode as “only new/updated” or as guaranteed idempotent until the implementation matches one of these designs.

### 8.3 P0: record versions are appended, but the analytical store is not actually latest-write-wins

The incremental code comments describe last-write-wins behavior, yet the store appends normalized records to new shards and appends rows to `_index.csv`. `iter_store` then yields every stored record. There is no compaction or version selection in that iterator, and the index is not an upsert table.

Consequences include:

- duplicate shots in aggregate statistics;
- old and new versions appearing in the same analysis;
- inconsistent context or outcomes across revisions;
- biased user and device counts;
- inability to reproduce the public state at a named cutoff.

Use one of two explicit designs:

- **Versioned event store:** retain every `(source_shot_id, updated_at, payload_hash)` privately and build a deterministic latest-as-of view for analysis; or
- **Upserted current-state store:** replace older normalized rows and retain only a separate audit log of revision hashes.

The first design is more defensible for research. A queryable `shot_versions` table plus a materialized `shots_latest_as_of(snapshot_cutoff)` view makes revisions visible without allowing them to double-count.

### 8.4 P0: moving newest-first pagination is not a snapshot

The full crawl resumes near its last page and rewinds three pages to absorb some boundary movement. That is practical, but it cannot guarantee a coherent snapshot while new shots arrive and older records change visibility. New records shift page boundaries; deletions contract them; ties in sort order can reorder records.

A rewind reduces risk but is not a proof of completeness. For a scientific release:

- prefer an owner-generated snapshot or stable server-side cursor;
- otherwise retain all observed `(id, updated_at)` list rows, repeatedly scan with overlap, and reconcile until no new versions appear over a complete pass;
- record the acquisition interval rather than pretending the corpus existed at one instant;
- freeze a logical cutoff and document records excluded because their state could not be established at that cutoff.

### 8.5 P0: distinguish raw payload availability from chart-data availability

The current Visualizer serializer returns top-level `timeframe` and `data` when parsed chart data exist; otherwise it returns `brewdata`. It does not necessarily return both in one default shot-detail response. Puckworks' data card and provenance text currently imply that source-native `brewdata` is preserved for every shot while also describing chart series.

That assumption should be tested and revised. For each source type, determine whether:

- the default endpoint exposes chart data only;
- raw `brewdata` can be requested through another documented format or endpoint;
- an owner-provided export is needed to retain the source-native payload;
- source/parser identity can be recovered from `metadata` or another field when `brewdata` is absent.

This matters because source-native payloads are often the best way to resolve machine identity, units, parser versions, state codes, and source-specific semantics. Do not advertise raw-payload preservation unless the harvest actually receives and stores it under the authorized scope.

### 8.6 P1: valid zero sensory scores are currently erased

Visualizer [validates the tasting-assessment fields](https://github.com/miharekar/visualizer/blob/main/app/models/shot.rb) as integers from 0 through 15. The Puckworks normalizer uses truthiness when converting sensory fields, so a valid `0` becomes `None`. This distorts missingness, distributions, and any within-user analysis.

Use explicit missingness tests:

```python
if isinstance(v, (int, float)) and not isinstance(v, bool):
    sensory[key] = int(v)
else:
    sensory[key] = None
```

Then range-check against the source schema, flag out-of-range values, and preserve the distinction among `0`, missing, malformed, and not applicable. The generic numeric helper should also use field-specific missing-value rules: zero may be a placeholder for some outcome fields, but it is not universally missing.

### 8.7 P1: flow is a quantity-type problem, not only a unit-label problem

The harvester converts `espresso_flow` and `espresso_flow_goal` from nominal g/s to kg/s while also flagging that they may be volumetric. A flag does not undo the numerical claim made by the stored key `flow__kg_per_s`.

The normalized representation should include:

- `quantity_kind`: `mass_flow`, `volumetric_flow`, `machine_proxy`, or `unknown`;
- `raw_unit` and `raw_values`;
- `si_unit` and `si_values` only when the quantity kind and conversion are established;
- `source_channel` and parser/device provenance;
- measurement node and derivation method, such as scale derivative versus machine estimate;
- a density assumption and uncertainty only when a volumetric-to-mass conversion is intentionally performed.

`espresso_flow_weight` may be the most defensible mass-flow signal for many records, but even it should undergo lag, filtering, scale-resolution, tare, and derivative-consistency checks. Never place ambiguous machine flow and verified mass flow on the same quantitative axis without a visible distinction.

### 8.8 P1: mixed-type samples can cause whole records to be skipped

The API schema permits generic series values that may include numbers, strings, booleans, or nulls. The current list conversion applies `float(x)` to each non-null element. A single nonnumeric value can throw, after which the outer crawl guard skips the entire shot.

Use sample-tolerant parsing:

- parse each sample independently;
- retain a boolean validity mask and original sample count;
- flag counts by failure type;
- reject a channel only when a predefined invalid fraction is exceeded;
- reject a shot only when required-channel criteria fail;
- retain raw values privately for audit.

Also explicitly exclude booleans from numeric conversion: in Python, `bool` is a subclass of `int`, but a state-like `true` is not a valid pressure sample.

### 8.9 P1: duration parsing discards its dirty-value audit flag

Dose and beverage-mass parsing retain the “dirty value” indicator, but duration takes only the parsed value and drops the flag. A string such as `"25 s"` becomes 25 without preserving the fact that a suffix was stripped.

Use the same helper pattern for every scalar, store `raw_value` privately, and record both parse status and conversion rule. This is small in code but important for an evidence system whose stated rule is not to silently coerce off-unit values.

### 8.10 P1: machine/source inference is too brittle for the stated corpus

The inference key list covers Decent, Meticulous, Beanconqueror, Gaggiuino, and GaggiMate. Visualizer explicitly supports Smart Espresso Profiler, Pressensor, and additional devices, and the set is designed to grow. A fixed substring list will create a large and changing “unknown” category and can misclassify composite payloads.

Build a versioned source dictionary from Visualizer's actual parser/import taxonomy. Preserve at least:

- ingestion source/application;
- machine make/model when known;
- sensor package;
- parser and parser version;
- firmware/software version where available;
- chart-data normalization version;
- confidence and evidence path used for classification.

Treat “source application,” “machine,” and “sensor” as separate fields. A Beanconqueror record may describe a brew captured by another device; a pressure profiler may not identify the espresso machine.

### 8.11 P1: privacy classification should extend beyond the explicitly dropped fields

The current privacy note says all free text is dropped, but the normalized context retains `profile_title`, `grinder_model`, `grinder_setting`, `roast_level`, and tags. Some of these may be standardized labels; others can be user-created and identifying. Exact timestamps, rare machine/profile combinations, source shot UUIDs, and stable user hashes can also enable linkage back to a public Visualizer page.

Recommended classification:

| Field type | Internal restricted store | Analysis store | Public release |
|---|---:|---:|---:|
| Source shot UUID | Yes | Replace with random internal key | No |
| Exact timestamp | Yes if authorized | Coarsen or derive relative time | No exact value |
| User ID | No after keyed transform | Keyed internal pseudonym | No stable cross-release key |
| Profile title | Yes if needed | Canonical profile signature or reviewed category | No raw rare title |
| Grinder model | Reviewed normalized taxonomy | Category/model with frequency controls | Aggregate only where safe |
| Grinder setting | Raw restricted | Within-device normalized or binned | Never portrayed as cross-grinder unit |
| Tags | Raw restricted | Allowlist or mapped ontology | Aggregate, minimum-cell rules |
| Free-form notes | Exclude unless separately justified | No | No |

Replace plain salted hashing with a keyed HMAC for internal linkage. Use a different random release key—or omit user-level identifiers entirely—for every public derivative. Store the source UUID only in an access-controlled lookup. A 64-bit truncated pseudonym may be acceptable for an internal grouping key after collision checks, but it should not be treated as anonymous or published as-is.

### 8.12 P1: deletions, privacy changes, and tombstones need an explicit policy

A shot that was public at harvest time may later be deleted, edited, or made private. A research corpus needs a documented policy for:

- periodic public-state reconciliation;
- tombstone records;
- removal from future analytical snapshots;
- whether already-published aggregate results are regenerated;
- retention of restricted historical payloads;
- owner/user withdrawal requests;
- incident response if a private field is unintentionally ingested.

Permission to access a public corpus is not automatically a permanent right to redistribute or retain every historical version. Confirm these rules with Visualizer and record them in the snapshot manifest.

### 8.13 P1: provenance needs to be record-level and snapshot-level

For each record version, retain:

- source shot ID in the restricted lookup;
- source `updated_at` and visibility state;
- list and detail retrieval timestamps;
- HTTP/API schema version where available;
- Visualizer source commit or release identifier used to interpret the response;
- response format and endpoint parameters;
- raw payload cryptographic hash;
- source/parser/device classification evidence;
- normalizer schema version and Puckworks commit;
- transformation log, units, quantity kinds, and QC flags.

For each snapshot, retain counts of listed, fetched, normalized, rejected, superseded, tombstoned, unresolved, and publishable records, plus hashes of the manifests and code environment. This is the bridge between “a crawl happened” and a reproducible evidence object.

### 8.14 P1: time-series quality controls need to be first-class, not a small flag list

Add tests and metrics for:

- finite and monotone time;
- duplicated timestamps;
- negative or extreme time steps;
- median sampling interval and jitter;
- channel length/alignment;
- null and invalid-sample fractions;
- impossible values and clipping;
- flatline/stuck sensors;
- discontinuities and resets;
- pressure–flow–weight temporal lag;
- derivative consistency between weight and scale-derived flow;
- goal/achieved channel compatibility;
- temperature channel identity and plausibility;
- state-code coverage and source-specific semantics;
- truncation before shot completion;
- pre-shot and post-shot padding.

These metrics should be stored, summarized, and used in declared eligibility rules. A single `flags` array is useful for audit but insufficient for weighting, thresholding, or explaining exclusions.

### 8.15 Recommended live-contract test suite

Before a full re-harvest, create a small, permission-compliant set of redacted fixtures representing every common response family:

1. chart-data response with top-level `timeframe`;
2. no-chart response with `brewdata` only;
3. Beanconqueror-formatted response;
4. every major source/device/parser family;
5. nulls and mixed series values;
6. sensory score equal to zero;
7. ambiguous and known flow quantities;
8. revised shot with the same ID and newer `updated_at`;
9. shot that becomes unavailable;
10. hidden shot time and missing user identity;
11. zero, string, unit-suffixed, and malformed scalar fields;
12. unequal channel lengths and nonmonotone time.

Run these against both the normalizer and a schema-diff check. Keep synthetic fixtures for edge cases, but do not let synthetic layout assumptions substitute for live API compatibility.

---

## 9. Recommended data architecture and Puckworks contracts

### 9.1 Use bronze, silver, and gold layers with different access rules

#### Bronze: authorized source records

Purpose: forensic reproducibility, parser repair, and version history.

- exact authorized API response or owner-provided export;
- immutable, encrypted, access-controlled, and never committed to the public repository;
- one object per source record version;
- content hash, retrieval metadata, and permission scope;
- separate lookup for source IDs and internal IDs;
- explicit retention/deletion policy.

The bronze layer should not be assumed to contain both chart data and native `brewdata`; record what was actually returned.

#### Silver: normalized observed telemetry

Purpose: reusable scientific analysis without direct identifiers.

Recommended central entities:

- `ObservedShot`: one latest-as-of or versioned observation with context and evidence metadata;
- `TelemetryTrace`: shared time base plus channel objects;
- `ObservedChannel`: raw/normalized values, quantity kind, units, node, derivation, source, and QC;
- `ShotOutcomeObservation`: user-entered TDS/EY/sensory stored separately with its own access and evidence label;
- `ShotContextObservation`: normalized machine, sensor, source, coffee, grinder, profile, and timing context;
- `ShotVersion`: source update/version lineage;
- `QualityAssessment`: eligibility, metrics, flags, and reasoned exclusions.

Prefer columnar Parquet files queried with DuckDB or an equivalent analytical engine. Partition by snapshot and broad source family rather than by sensitive user or exact date. Use Zstandard compression and a machine-readable schema registry.

#### Gold: derived and publishable products

Purpose: model inputs, figures, tables, and public value.

- shot-phase boundaries;
- quality-qualified feature tables;
- profile signatures;
- controller metrics;
- operating-envelope summaries;
- model residuals and domain indicators;
- privacy-safe aggregate tables;
- figure-ready data with evidence badges and minimum-cell checks;
- no source UUIDs, exact timestamps, raw text, or reusable public user hashes.

Every gold object should identify the silver snapshot, code commit, eligibility rule, feature-definition version, weighting scheme, and privacy transformation.

### 9.2 Add an explicit observed-data contract instead of coercing telemetry into latent states

Puckworks' typed physical contracts represent machine state, bed state, and shot-result state. Visualizer records are observations of selected channels, not complete instances of those latent states. A separate contract prevents accidental imputation.

A conceptual structure:

```python
@dataclass(frozen=True)
class ObservedChannel:
    name: str
    source_key: str
    values_raw: ArrayLike
    raw_unit: str | None
    quantity_kind: Literal[
        "pressure", "mass_flow", "volumetric_flow", "mass",
        "temperature", "state_code", "unknown"
    ]
    values_si: ArrayLike | None
    si_unit: str | None
    measurement_node: str | None
    derivation: str | None
    source_family: str | None
    qc_mask: ArrayLike
    evidence: EvidenceTag

@dataclass(frozen=True)
class ObservedShot:
    internal_id: str
    version: str
    time_s: ArrayLike | None
    channels: Mapping[str, ObservedChannel]
    context: ShotContextObservation
    outcomes_ref: str | None
    quality: QualityAssessment
    provenance: ProvenanceRef
```

Adapters may then provide **measured forcing** to a Puckworks model:

- recorded pressure as a boundary condition;
- verified scale mass flow as an observed response;
- goal trajectories as controller commands;
- temperature as observed forcing/context.

Adapters should never fill unobserved permeability, porosity, saturation, puck height, particle-size distribution, or channel geometry. Those remain parameters or latent states with declared priors and identifiability limits.

### 9.3 Register the corpus as a data product, not a physics component

The existing “data-only; no gate” posture is correct. Extend the registry only enough to make the data product discoverable and versioned:

- dataset ID and snapshot ID;
- eligible stages: machine, flow, bed-dynamics, extraction-forcing;
- evidence tier;
- source/permission reference;
- input/output schema versions;
- supported adapters;
- known quantity ambiguities;
- permitted gate roles: none, reference envelope, external stress set, or exploratory outcome association.

Do not create the impression that passing an ecological dataset through a model runner promotes it to controlled validation.

### 9.4 Snapshot manifest template

Each frozen corpus should have a manifest resembling:

```yaml
snapshot_id: visualizer-public-2026-08-31-v1
logical_cutoff_utc: 2026-08-31T23:59:59Z
acquisition_started_utc: ...
acquisition_completed_utc: ...
permission_reference: visualizer-data-permission-2026-07-14
source_api_spec: 1.13.0
source_repo_commit: ...
harvester_commit: ...
normalizer_schema: 2
listed_ids: ...
fetched_versions: ...
latest_public_records: ...
tombstoned_or_unavailable: ...
normalization_failures: ...
hydraulic_eligible: ...
outcome_records: ...
raw_manifest_sha256: ...
silver_manifest_sha256: ...
exclusion_rule_version: ...
privacy_release_rule_version: ...
notes: ...
```

The manifest should contain aggregate counts only and can be public even when the corpus is not.

---

## 10. Suggested feature definitions and analytical safeguards

Feature engineering is where observational telemetry can quietly become overinterpreted physics. Every feature should state its observable inputs, units, eligibility rules, phase, and physical meaning.

### 10.1 Time-base and channel-quality features

Per shot and per channel:

- `n_samples_raw`, `n_samples_valid`;
- duration from time vector and scalar duration disagreement;
- median `dt`, interquartile range of `dt`, maximum gap;
- nonmonotone and duplicate-time counts;
- valid fraction and longest valid run;
- number of resets/discontinuities;
- flatline fraction;
- clipping fraction;
- alignment status relative to the shared time base;
- source/parser/device family;
- quantity-kind confidence.

Publish these before any physical feature distributions. They define what the corpus can support.

### 10.2 Phase and control-mode features

Identify preinfusion, pressure/flow ramp, main extraction, declining/taper phase, and termination using source state codes when reliable. Otherwise use a versioned change-point algorithm based on goal and achieved trajectories. Store:

- phase boundaries;
- segmentation method;
- confidence;
- ambiguous/unsegmented status;
- active control objective by interval: pressure, flow, mixed, open loop, or unknown.

Control mode is essential because the same observed pressure–flow shape has a different interpretation under pressure control and flow control.

### 10.3 Commanded-versus-achieved features

For compatible goal and achieved channels:

- error trajectory `e(t) = goal(t) - achieved(t)`;
- phase-specific RMSE and median absolute error;
- time to enter tolerance band;
- overshoot and undershoot;
- steady-state bias;
- lag from goal change to achieved response;
- saturation/clipping duration;
- oscillation or hunting score;
- termination discrepancy;
- fraction of the shot governed by each goal type.

These features support a machine/control atlas and help isolate which apparent puck behavior may instead be actuator or controller behavior.

### 10.4 Operating-envelope features

Use robust summaries rather than only maxima:

- phase-specific median, 10th, and 90th percentile pressure;
- verified mass-flow summaries and separate ambiguous-flow summaries;
- peak and integrated pressure/flow exposure;
- beverage mass and dose when valid;
- brew ratio;
- shot duration and active extraction duration;
- temperature goal and achieved temperature summaries;
- time and state at first sustained beverage-mass increase;
- profile-signature family.

Create model-domain indicators from these features, but keep each model's declared domain separate. A shot can be in domain for the machine model and out of domain for an extraction model.

### 10.5 Apparent hydraulic resistance features

Under a clearly stated pressure-node and flow-quantity interpretation, define an observational effective resistance such as:

\[
R_{\mathrm{app}}(t)=\frac{\Delta P(t)}{Q(t)}.
\]

Safeguards:

- use only intervals above declared pressure and flow thresholds;
- never divide by near-zero flow;
- keep mass-flow and volumetric-flow forms distinct;
- state whether atmospheric outlet pressure is assumed;
- label the quantity “apparent” or “effective,” not permeability;
- propagate pressure/flow uncertainty when available;
- do not compare values across different pressure nodes without transformation or stratification.

Useful derived descriptors include:

- early, middle, and late median `R_app`;
- slopes of `log R_app` by phase;
- maximum decline and its timing;
- sign changes;
- pressure–flow hysteresis-loop area;
- recovery or rebound after control transitions;
- neutral trajectory labels such as stable, early rise, late decline, or nonmonotonic.

These are phenotype variables. Mechanism names such as “channeling,” “fines migration,” or “swelling” require independent discrimination.

### 10.6 Weight/flow consistency and machine diagnostics

Where both beverage weight and scale-derived flow are present:

1. smooth weight with a declared causal or zero-phase method, depending use;
2. differentiate weight with uncertainty-aware filtering;
3. estimate time lag against the reported scale-flow channel;
4. quantify gain, offset, and residual structure;
5. flag tare events, scale saturation, and post-drip behavior.

Water-dispensed versus beverage-mass differences can be useful machine/system diagnostics. They are **not** direct puck-retention measurements without accounting for headspace, plumbing, bypass, evaporation, scale timing, and post-shot liquid.

### 10.7 Profile signatures

Raw profile titles are inconsistent and potentially identifying. Create a canonical signature from the available goal curves and control transitions:

- resample goals to a standard relative-time or phase grid;
- encode pressure/flow control segments, transition thresholds, and termination rule when available;
- quantize within a declared tolerance;
- hash the canonical representation;
- cluster near-equivalent signatures separately from exact hashes.

This supports repeated-shot analysis while avoiding dependence on user-created names. Preserve title-to-signature mapping only in the restricted layer.

### 10.8 Outcome consistency features

For records with valid dose, beverage mass, and TDS, compare reported EY to the algebraic relation:

\[
EY_{calc}=\frac{TDS_{fraction}\,m_{beverage}}{m_{dose}}.
\]

Use this as a **consistency check**, not proof of accuracy. Classify:

- algebraically consistent within tolerance;
- percentage/fraction convention mismatch;
- probable stale field after shot edit;
- missing prerequisite;
- implausible or unparseable.

For TDS/EY association analyses, keep instrument/protocol unknownness explicit, prioritize within-user or within-device contrasts, and model the probability that an outcome was recorded.

### 10.9 Repeatability and natural-perturbation features

Define privacy-preserving internal groups such as:

- user × machine × exact profile signature;
- user × machine × coffee-bag ID × profile signature;
- user × grinder × coffee × profile within a bounded date interval;
- adjacent shots with one visible command change;
- repeated named controlled test submitted by collaborators.

Estimate within-group covariance, not only shot-level variance. Require sufficient records per group and report how much the largest users dominate each result. Natural perturbations are valuable for hypothesis generation, but they are not randomized interventions.

---

## 11. Visualization strategy within Puckworks' honesty architecture

Puckworks' evidence-bound visualization system is an excellent fit for this corpus. Visualizer-derived figures should be generated from registered specifications whose inputs, evidence class, eligibility rule, denominator, weighting, and privacy status are machine-readable.

### 11.1 Recommended visualization specifications

| Suggested `VizSpec` | Purpose | Required honesty features |
|---|---|---|
| `visualizer_corpus_census` | Counts by acquisition status, source family, time period, and evidence tier | Snapshot ID; no claim of population representativeness |
| `visualizer_channel_coverage` | Fraction of records with each channel and valid time base | Numerator/denominator and quality threshold on every panel |
| `visualizer_missingness_map` | Joint missingness by source/device and period | Separate “not supported” from “supported but missing” |
| `visualizer_operating_envelope` | Density of pressure, verified flow, duration, dose, ratio, and temperature | User-balanced and shot-weighted variants; quantity types separated |
| `visualizer_target_tracking` | Goal versus achieved behavior by phase/control mode | Command/measurement distinction, machine/source stratification |
| `visualizer_flow_weight_consistency` | Scale-flow versus derivative-of-weight diagnostics | Lag/filter method and uncertainty shown |
| `visualizer_resistance_phenotypes` | Neutral apparent-resistance trajectory families | “Observed/ecological” badge; no mechanism labels |
| `visualizer_model_domain_coverage` | In-domain, boundary, and extrapolation regions for each model | Model version and domain definition embedded |
| `visualizer_null_ladder` | Held-out residual comparison among declared model classes | Grouped split, metric definitions, no causal language |
| `visualizer_repeatability` | Within-group versus between-group variability | Group definition, minimum group size, user dominance |
| `visualizer_outcome_consistency` | Reported versus reconstructed EY and missingness | “User-entered/exploratory” badge; no accuracy claim |
| `visualizer_evidence_funnel` | Listed → fetched → normalized → quality-qualified → model-eligible | Exclusion reasons and counts |
| `visualizer_controlled_bridge` | Location of controlled Puckworks traces inside the ecological envelope | Controlled and ecological evidence visibly distinct |
| `visualizer_profile_landscape` | Privacy-safe profile-signature families | No raw titles or rare identifying signatures |

### 11.2 Presentation rules

- Prefer densities, quantile ribbons, hex bins, and stratified summaries over thousands of overlapping shot traces.
- Provide both **shot-weighted** and **user-balanced** estimates where user linkage is available internally.
- Never display an “average shot” without defining phase alignment, inclusion rules, weighting, and uncertainty.
- Show eligible counts and total candidate counts directly on every plot.
- Keep machine/source panels separate until measurement compatibility is demonstrated.
- Never combine mass flow, volumetric flow, and unknown machine proxy values on one numeric scale.
- Suppress or pool small cells and rare combinations; test dominance by a single user.
- Remove source UUIDs, exact dates/times, raw profile titles, and hover metadata that can recreate a public-shot lookup.
- Use evidence badges such as **controlled**, **measured ecological**, **user-entered exploratory**, and **model-derived**.
- Make exclusions inspectable through aggregate reason counts, not hidden preprocessing.
- For public dashboards, generate static privacy-reviewed extracts rather than querying the restricted corpus directly.

### 11.3 A particularly strong narrative figure set

A concise paper or public report could use this sequence:

1. **Evidence funnel:** what was accessible and what survived quality controls.
2. **Measurement map:** which devices/sources contribute which observables.
3. **Operating envelope:** where real shots occur relative to model assumptions.
4. **Command versus achievement:** why machine behavior must be separated from puck behavior.
5. **Neutral dynamic-resistance phenotypes:** recurrent observational structures.
6. **Controlled bridge:** controlled fixtures positioned within the ecological population.
7. **Null ladder on held-out groups:** what added model flexibility explains.
8. **Claim boundary panel:** what the corpus does and does not identify.

That sequence tells a scientifically honest story before presenting any headline model result.

---

## 12. Narrative and public value

### 12.1 The core narrative: microscope plus telescope

Puckworks' controlled experiments and literature benchmarks are the **microscope**: they isolate variables, calibrate sensors, and test mechanisms. Visualizer is the **telescope** or **census instrument**: it reveals the diversity, prevalence, and practical operating regimes that a small controlled study cannot cover.

The combined argument is stronger than either alone:

- controlled work asks, “Can this mechanism be distinguished under known conditions?”;
- the community corpus asks, “Do the resulting regimes and signatures occur in real use, and how often?”;
- Puckworks' contracts and evidence tags prevent those questions from being conflated.

This can become a defining Puckworks contribution: not merely another espresso model, but a reproducible way to connect mechanistic evidence, machine telemetry, community data, and public claims.

### 12.2 Concrete public-value outputs

The corpus can support useful products even when no model is “validated”:

- a device/source measurement dictionary explaining what each channel means;
- anonymous channel-availability and quality reports that help Visualizer improve parsers;
- controller goal-tracking benchmarks by broad source family;
- operating envelopes that show users whether a model or recipe claim applies to their regime;
- clear examples of machine limitations that can masquerade as puck defects;
- a public guide to pressure versus flow control;
- a demonstration that grinder dial settings are not transferable physical units;
- a map of known unknowns and missing measurements;
- community-selected regimes for future controlled tests;
- privacy-safe reproducible figures and data definitions other researchers can reuse.

These align particularly well with Puckworks' existing public-value themes around machine-versus-puck diagnosis, cross-pressure behavior, control modes, pump characterization, and locating a controlled shot within a broader population.

### 12.3 Community reciprocity

The corpus exists because users chose to make shot records public and because Visualizer invested in ingestion, normalization, and access infrastructure. The research relationship should therefore include:

- collective acknowledgment of contributing users;
- early sharing of data-quality findings with Visualizer maintainers;
- a plain-language community report before or alongside papers;
- reproducible aggregate definitions so Visualizer can independently reproduce findings;
- a correction pathway for source-semantic mistakes;
- no public “bad machine” ranking based on uncontrolled, self-selected records;
- clear explanation of selection bias and nonrepresentativeness;
- share-back of parser/source dictionaries and privacy-safe aggregate tools where practical.

The highest public value may be a trustworthy measurement map and claim-boundary framework, not a leaderboard.

---

## 13. Publication opportunities

### 13.1 Paper A: “The Cup Hides the Clock”

Visualizer should play a supporting, not central validation, role.

Strong contributions:

- quantify how often rich hydraulic trajectories coexist with sparse endpoint chemistry;
- demonstrate the information lost when a dynamic process is summarized by beverage mass, duration, TDS, or EY alone;
- show the range of real forcing trajectories for extraction models;
- motivate time-resolved observation design;
- provide ecological examples of trajectories that share similar endpoints but differ dynamically.

Claim boundary: Visualizer outcomes should not validate extraction kinetics or endpoint chemistry. Use controlled chemistry datasets for that. Visualizer can establish prevalence and observation-design relevance.

### 13.2 Narrow Paper B: “One Flow Curve, Many Causes”

This is the strongest direct scientific fit.

A defensible design:

1. define and freeze the null ladder using controlled or literature-anchored data;
2. establish machine/controller behavior with commanded-versus-achieved channels;
3. define an eligible ecological cohort with known pressure/flow quantity and node;
4. compare static and time-varying effective-resistance descriptions on grouped held-out records;
5. characterize recurrent residual/trajectory phenotypes;
6. show whether phenotypes recur across users, time periods, profiles, and source families;
7. select controlled perturbation experiments that discriminate among plausible mechanisms.

Potential conclusion: a static hydraulic closure is insufficient for a specified, quality-qualified cohort and time-varying effective resistance is frequently needed to describe observed trajectories. That is meaningful. It is not yet proof that one named mechanism caused the temporal change.

### 13.3 Paper 3: Puckworks methods/resource paper

Visualizer could be a flagship case study for the Puckworks architecture:

- authorized community-data intake;
- source/API contract testing;
- immutable snapshots and provenance;
- unit and quantity-type handling;
- privacy transformations;
- separation of observables, latent states, and outcomes;
- evidence tiers and gate restrictions;
- ecological stress tests versus controlled validation;
- evidence-bound visualizations;
- executable claim boundaries.

A strong methods result would show that the same framework can ingest a large heterogeneous corpus without allowing it to overrule stronger controlled evidence merely because it has a larger sample size.

### 13.4 A separate data/methods note

A focused article could be warranted after the corpus is frozen and quality-audited. A possible theme:

> **Bridging community espresso telemetry and provenance-aware physical-model evaluation**

Its central contributions would be the measurement ontology, source dictionary, schema/version strategy, quality funnel, privacy model, snapshot manifest, and reproducible population summaries. Raw redistribution is not necessary if code, definitions, metadata, and permitted aggregates are sufficient to reproduce analyses under authorized access.

### 13.5 Future controlled follow-up paper

Use population density and phenotype prevalence to select conditions for a multi-machine controlled experiment:

- common versus rare control regimes;
- early versus late resistance decline;
- pressure-control versus flow-control responses;
- pump-limited versus puck-limited regions;
- repeated coffee/grind/preparation interventions;
- synchronized pressure-node and mass-flow instrumentation.

This creates a transparent chain from community observation to controlled discrimination and back to population relevance.

### 13.6 Claims and titles to avoid

Avoid headlines such as:

- “validated on the entire Visualizer corpus”;
- “large-N proof of channeling”;
- “machine-learning model discovers puck permeability”;
- “universal espresso pump curve from public shots”;
- “sensory optimization across thousands of users.”

Prefer:

- “external ecological stress test”;
- “observed operating envelope”;
- “apparent-resistance phenotype”;
- “population relevance of controlled regimes”;
- “user-entered outcome consistency and exploratory association.”

---

## 14. Prioritized roadmap and decision gates

### Phase P0 — Repair and governance before full canonical harvest

1. Confirm exact permission scope, retention, deletion, redistribution, and share-back obligations in a durable record.
2. Fix top-level `timeframe` parsing and add live-contract fixtures.
3. Replace unauthenticated `updated_after` logic with a valid snapshot/delta strategy.
4. Implement version-aware latest-as-of views and tombstones.
5. Separate flow quantity kinds and stop asserting kg/s for ambiguous channels.
6. Preserve valid zero sensory values and add field-specific missingness.
7. Implement sample-tolerant series parsing and QC masks.
8. Expand source/device/parser taxonomy.
9. Classify retained context for privacy and linkability.
10. Reconcile whether raw `brewdata` is actually available with chart data.
11. Define snapshot manifest and hash scheme.
12. Reprocess all previously harvested records after schema changes.

**Gate P0:** no corpus-wide scientific statistic is canonical until the live response contract, version semantics, and quantity types pass review.

### Phase P1 — Corpus census and measurement ontology

Deliverables:

- source/device/parser dictionary;
- API-field and quantity ontology;
- evidence funnel;
- channel coverage and missingness atlas;
- time-base and unit quality report;
- user dominance and temporal acquisition profile;
- privacy risk review;
- frozen discovery snapshot.

**Gate P1:** every analysis variable has a source path, quantity kind, unit, measurement node, QC rule, and evidence label.

### Phase P2 — Machine and operating-envelope products

Deliverables:

- phase segmentation library;
- goal-achieved controller atlas;
- verified-flow operating envelope;
- profile signatures;
- model-domain coverage matrix;
- controlled-fixture location within the population.

**Gate P2:** incompatible source/device channels are not pooled, and all aggregate estimates show shot-weighted and user-balanced sensitivity where applicable.

### Phase P3 — Dynamic-resistance and model stress tests

Deliverables:

- preregistered eligible cohort;
- static-null and flexible-temporal comparator;
- grouped holdout design;
- neutral phenotype atlas;
- residual recurrence tests;
- sensitivity to node/flow assumptions;
- frozen confirmation snapshot.

**Gate P3:** no mechanism name is attached to a phenotype unless a controlled discrimination test supports it.

### Phase P4 — Papers and public outputs

Deliverables:

- Paper A supporting figures;
- narrow Paper B external stress-test section;
- Paper 3 corpus case study;
- privacy-safe public dashboard or report;
- collective attribution and community acknowledgment;
- share-back package for Visualizer maintainers.

**Gate P4:** every public figure is generated from a reviewed gold extract with minimum-cell, dominance, linkability, and evidence-label checks.

### Phase P5 — Outcomes and controlled follow-up

Deliverables:

- outcome consistency analysis;
- within-user exploratory models;
- missing-outcome model;
- selected controlled multi-machine experiment;
- post-study population relevance analysis.

**Gate P5:** user-entered outcomes remain exploratory unless independently measured under a documented protocol.

### Cross-cutting stop rules

Stop or quarantine an analysis when:

- the time base is absent or incompatible;
- flow quantity kind is unknown for a quantitative flow claim;
- pressure node is material and unresolved;
- a few users dominate the result beyond the declared threshold;
- revisions or duplicates cannot be resolved;
- the discovery and confirmation sets overlap improperly;
- a public output contains raw IDs, exact timestamps, rare titles, or small identifying cells;
- a result changes materially under user-balanced versus shot-weighted analysis without that dependence being central to the conclusion;
- an observational phenotype is being described as a causal mechanism.

---

## 15. Claim boundaries

### 15.1 Claims the corpus can support after quality control

- The distribution of **observed** telemetry and context among eligible public Visualizer records in a named snapshot.
- Channel availability, time-base quality, missingness, and source heterogeneity.
- Commanded-versus-achieved tracking for compatible channels and devices.
- The fraction of eligible records inside or outside a Puckworks model's declared operating domain.
- Whether a specified model violates physical constraints or shows systematic residuals on a grouped, held-out ecological cohort.
- Whether neutral observational trajectory phenotypes recur across users, profile families, source families, or time periods.
- Whether controlled Puckworks experiments occupy common, rare, or uncovered regions of the observed operating envelope.
- Exploratory within-user or tightly blocked associations, with confounding and selection limitations stated.
- Algebraic consistency of user-entered TDS/EY with dose and beverage mass.

### 15.2 Claims it cannot support by itself

- Representativeness of all espresso shots, machines, or users.
- Direct measurement of puck permeability, porosity, saturation, swelling, erosion, fines migration, or channel geometry.
- Causal identification of channeling or another mechanism from pressure/flow shape alone.
- Causal effects of profile, roast, grinder, preparation, or coffee on extraction or sensory outcomes.
- Cross-grinder comparability of dial settings.
- Ground-truth TDS, EY, or sensory preference.
- A universal pump curve or machine closure without controlled calibration and known hydraulic topology.
- Redistribution rights to the user-contributed corpus merely because the Visualizer application code is MIT licensed.
- Permanent public status or consent for every previously visible shot without an agreed retention policy.

### 15.3 Recommended evidence labels

Use a compact vocabulary consistently in tables, model cards, and figures:

- **CONTROLLED:** preregistered or documented experiment with known intervention and calibrated measurements.
- **REFERENCE:** literature or fixture data useful for comparison but not fully independent validation.
- **ECOLOGICAL MEASURED:** machine/sensor telemetry from uncontrolled public use.
- **USER-ENTERED EXPLORATORY:** TDS, EY, sensory, and optional context supplied without a standardized research protocol.
- **MODEL-DERIVED:** latent states, inferred parameters, residual features, and simulated quantities.
- **UNKNOWN/AMBIGUOUS:** unresolved source, node, unit, or quantity type; excluded from claims requiring resolution.

Large sample size should never promote one label to another.

---

## 16. Attribution, data availability, and governance language

### 16.1 Suggested acknowledgment

> Shot telemetry was obtained from Visualizer (visualizer.coffee) with permission from Miha Rekar. We collectively thank the Visualizer users who chose to make their shots public; their contributions made this analysis possible.

Adjust the wording to match the final written permission and journal style. Credit Visualizer prominently in methods, data availability, figures derived from the corpus, and the repository's dataset card—not only in supplementary material.

### 16.2 Suggested data-availability statement

> Raw user-contributed Visualizer records are not redistributed by Puckworks. Analysis code, schema and quantity definitions, eligibility and quality-control rules, snapshot metadata, transformation provenance, and privacy-preserving aggregate or derived statistics are made available through the Puckworks repository. Access to source records remains governed by Visualizer and the project's authorization from the data steward.

Do not imply that a public API or an MIT application license grants an open-data license for the corpus. If an owner-provided export is used, describe its access scope separately.

### 16.3 Suggested methods language for evidence strength

> Visualizer records were treated as ecological machine-logged observations. They were used to characterize operating regimes, assess model-domain coverage, and externally stress-test frozen model specifications. They were not treated as controlled ground truth for latent puck states, extraction chemistry, or sensory outcomes. User-entered TDS, extraction yield, and sensory fields were analyzed separately and labeled exploratory.

### 16.4 Governance checklist to resolve with Visualizer

Document answers to these questions before the first public result:

- Does authorization cover all public-shot detail fields or only specified fields?
- Is a bulk owner-generated export permitted, and may source-native payloads be retained?
- What is the allowed retention period?
- What happens when a shot becomes private or is deleted?
- May restricted historical versions be retained for reproducibility?
- Which aggregate or row-level derivatives may be shared?
- Are minimum aggregation or user-count thresholds desired?
- Is recontact or individual attribution prohibited?
- How should security or privacy incidents be reported?
- How should Visualizer and contributing users be acknowledged?
- What share-back format would be most useful to the community?

---

## 17. Final recommendation

The Visualizer corpus should become a major **reference population** inside Puckworks, but not a shortcut around controlled evidence. Its distinctive contribution is the combination of real-world diversity, time-resolved machine telemetry, commanded and achieved channels, repeat observations, and optional context. That combination can reveal where Puckworks models matter, where they fail, which assumptions are routinely violated, and which controlled experiments deserve priority.

The best near-term sequence is:

1. repair the live API contract and versioning issues;
2. freeze a governed, quality-audited snapshot;
3. publish the census, measurement ontology, and goal-achieved machine atlas;
4. map Puckworks model domains onto the population;
5. run a preregistered external stress test of static versus time-varying hydraulic descriptions;
6. connect the ecological results to controlled machine and puck experiments;
7. use outcomes only as a separate exploratory layer;
8. release privacy-safe aggregates, executable definitions, and an evidence-honest public narrative.

Done this way, Visualizer does more than add sample size. It gives Puckworks an empirical bridge from controlled physics to the messy distribution of real espresso practice—and gives the project a compelling demonstration of how community data can increase scientific relevance without weakening scientific standards.

---

## Appendix A. Field-to-use map

| Visualizer field or field family | Primary Puckworks use | Evidence role | Key safeguards |
|---|---|---|---|
| Top-level `timeframe` | Shared time base, phase features, model forcing | Ecological measured | Contract fix; monotonicity; sampling QC |
| `data.espresso_pressure` | Machine/flow boundary, apparent resistance | Ecological measured | Pressure node, calibration, control mode |
| `data.espresso_pressure_goal` | Commanded-versus-achieved, profile signature | Command/setting | Goal semantics and source compatibility |
| `data.espresso_flow_weight` | Mass-flow response, weight derivative check | Ecological measured | Lag, scale filtering, derivative QC |
| `data.espresso_flow` | Device flow observation/proxy | Ecological measured/ambiguous | Quantity kind; do not assume mass flow |
| `data.espresso_flow_goal` | Controller command | Command/setting | Volumetric/mass ambiguity; control-mode semantics |
| `data.espresso_weight` | Beverage trajectory, onset, termination | Ecological measured | Scale lag, tare, post-drip, unit QC |
| `data.espresso_water_dispensed` | Machine/system mass proxy | Ecological measured | Not direct puck retention; topology effects |
| Basket/mix/goal temperatures | Thermal context, controller behavior | Ecological measured/command | Sensor location and source semantics |
| `espresso_state_change` | Phase/control segmentation | Device-coded observation | Source-specific state dictionary |
| Dose/bean weight | Blocking, brew ratio, extraction consistency | User-entered/device context | Parse status; stale values; unit suffixes |
| Drink weight | Brew ratio, EY consistency | User-entered/device context | Compare scalar with weight trace |
| Duration | QC and context | Context | Retain dirty parse status; compare time vector |
| Profile title | Restricted mapping to profile signature | Context | Free-text/linkability risk; do not publish raw |
| Grinder model | Stratification and taxonomy | Context | Normalize names; selection/confounding |
| Grinder setting | Within-grinder natural perturbations | Context | Never treat as cross-grinder physical unit |
| Roast level | Exploratory stratification | Context | Subjective/nonstandard; confounding |
| Tags | Ontology candidate, cohort definition | Context | Allowlist/map; privacy review; sparse cells |
| Source-native `brewdata` | Source parsing, raw semantics, firmware/device context | Provenance | May be mutually exclusive with chart data in default response |
| `metadata` | Source/format/provenance hints | Provenance/context | Schema drift and privacy review |
| Coffee-bag/roaster IDs | Same-coffee blocking and structured context | Context | Confirm access scope; no public linkage |
| TDS | Outcome consistency and exploratory association | User-entered exploratory | Unknown instrument/protocol; missing-not-at-random |
| EY | Consistency check and exploratory association | User-entered exploratory | Reconstruct where possible; not ground truth |
| Sensory sliders | Within-user exploratory preference analysis | User-entered exploratory | Preserve zero; non-calibrated; no cross-user scale assumption |
| User ID | Internal grouping after keyed transform | Sensitive linkage | HMAC, restricted lookup, no stable public pseudonym |
| Shot UUID | Revision reconciliation | Sensitive linkage | Replace in analysis; never publish |
| Start time | Temporal drift and grouping | Sensitive context | Coarsen; hidden for some users; linkability |
| `updated_at` | Versioning and snapshot cutoff | Provenance | Ties, revision logic, authenticated filter limitation |

---

## Appendix B. Analysis matrix

| Analysis | Minimum required fields | Preferred cohort | Output | Validation status |
|---|---|---|---|---|
| Corpus census | ID/version, source, QC metadata | All listed/fetched records | Evidence funnel and coverage tables | Pipeline validation only |
| Goal tracking | Time, compatible goal and achieved channel | Known source/control mode | Error/lag/overshoot distributions | Machine ecological benchmark |
| Operating envelope | Time, pressure, verified flow or weight, context | Quality-qualified, source-stratified | Density and model-domain map | External relevance |
| Apparent-resistance phenotype | Time, known pressure node, known flow quantity | Main extraction intervals | Neutral trajectory classes | Ecological stress evidence |
| Static-null test | Above plus frozen model and grouped splits | Held-out users/profile families | Residual scorecard | External stress test, not mechanism proof |
| Controlled bridge | Controlled fixture plus same observables | Compatible source/domain | Population-location figure | Supports generalizability |
| Repeatability | Internal user key, machine, profile/coffee grouping | Repeated cohorts | Variance decomposition | Exploratory observational |
| Outcome consistency | Dose, beverage mass, TDS, EY | Complete valid scalars | Reported versus reconstructed EY | Data-quality check |
| Outcome association | Outcomes plus context and telemetry | Repeated, tightly blocked cohorts | Hierarchical exploratory estimates | Not causal/ground truth |
| Public dashboard | Gold aggregates only | Privacy-reviewed | Community report | Public value, no validation promotion |

---

## Appendix C. Sources reviewed

### Visualizer

- Visualizer site: <https://visualizer.coffee/>
- Visualizer repository: <https://github.com/miharekar/visualizer>
- API specification: <https://github.com/miharekar/visualizer/blob/main/openapi.yaml>
- API shots controller: <https://github.com/miharekar/visualizer/blob/main/app/controllers/api/shots_controller.rb>
- Shot API serializer: <https://github.com/miharekar/visualizer/blob/main/app/models/shot/jsonable.rb>
- Shot model and tasting validation: <https://github.com/miharekar/visualizer/blob/main/app/models/shot.rb>
- Database schema: <https://github.com/miharekar/visualizer/blob/main/db/schema.rb>

### Puckworks

- Puckworks repository: <https://github.com/trbrewer/puckworks>
- Visualizer harvester: <https://github.com/trbrewer/puckworks/blob/main/puckworks/lib/visualizer_harvest.py>
- Visualizer data card: <https://github.com/trbrewer/puckworks/blob/main/docs/cards/visualizer_coffee.md>
- Visualizer provenance record: <https://github.com/trbrewer/puckworks/blob/main/puckworks/data/visualizer/PROVENANCE.md>
- Roadmap: <https://github.com/trbrewer/puckworks/blob/main/docs/ROADMAP.md>
- Public-value plan: <https://github.com/trbrewer/puckworks/blob/main/docs/PUBLIC_VALUE.md>
- Publication-strategy review: <https://github.com/trbrewer/puckworks/blob/main/docs/PUBLICATION_STRATEGY_REVIEW.md>
- Typed contracts: <https://github.com/trbrewer/puckworks/blob/main/puckworks/contracts.py>
- Registry: <https://github.com/trbrewer/puckworks/blob/main/puckworks/registry.py>
- Visualization specification: <https://github.com/trbrewer/puckworks/blob/main/puckworks/viz/spec.py>
- Visualization registry: <https://github.com/trbrewer/puckworks/blob/main/puckworks/viz/registry.py>

### Review boundary

Repository and API claims in this document reflect the source state reviewed on **2026-07-15**. Because both repositories and the API can change, the frozen Puckworks analysis should record exact commits and the API/schema version used. Corpus prevalence claims are intentionally absent because this review did not complete or statistically analyze the full authorized harvest.
