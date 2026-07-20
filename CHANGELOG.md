# Changelog

Notable changes. Format loosely follows Keep a Changelog; scientific/component changes are
tracked in detail in `docs/ROADMAP.md` §7.1.

## Unreleased

- **Deep-dive figure presentation/readability pass (#43) — formatting only.** The educational tour
  figures are now laid out by a new `puckworks.viz.tour_style` with a **reserved header band** (evidence
  badge) and **reserved footer band** (concise provenance + the fidelity ceiling wrapped as a `Scope:`
  paragraph), built from stacked matplotlib subfigures — so the badge never overlaps a title and the
  footer never overlaps an axis label. A local typography scale keeps every visible label ≥8 pt
  (retiring the old 5.2 pt footer); no process-wide `rcParams` are touched. `stamp_fig` delegates to an
  **idempotent** tour stamp when a figure carries the reserved bands, and keeps the ordinary corner stamp
  for every other figure. Draw functions gained `presentation="notebook"|"standalone"`: notebook figures
  no longer repeat the headline/question the notebook prints, small multiples share one figure-level axis
  label, and the reference-condition star is explained once. Per-figure fixes: the Foster wetting front
  is windowed to the saturation event (it was invisible on a 100 s axis); the LB profile is normalized to
  fraction-of-maximum with wall/centre labels (no six-decimal lattice ticks); the synthetic pack is a
  compact solid-vs-pore + heterogeneity-field landscape with a visual key and colorbar (no lattice ticks).
  The novice explanation is restructured by a new tested `puckworks.product.lab_tour_notebook_display`
  into short labelled sections (*What changes · What the model shows · Why this happens · Scope*) with all
  technical evidence in a collapsed `<details>` block and **humanized** fixed inputs (`Dose: 20 g`, not
  `dose_g=20.0`); the Colab deep dive is reworked to match (public headings, retina inline). Structural
  bounding-box/typography tests (`tests/test_tour_layout.py`) guard the collisions from recurring. NO
  computed value, badge, evidence strength, fidelity ceiling, VizSpec metadata, component ordering, rights
  behavior, tour route, or scientific hash changed; no status promotion.

- **Educational insight figures for the Full-Tour deep dive; gate scorecards removed (#43).** The novice
  deep dive no longer plots any scientific-check / gate numbers (the `_gate_figure` path,
  `_PASS_COLOR`/`_FAIL_COLOR`, and the "condition index" scorecard are deleted from
  `lab_tour_plots`) — gate metrics are technical evidence of trust, not a novice figure. In their place,
  a new `puckworks.product.lab_tour_insights.component_figures(result, …)` returns **0, 1, or several**
  VizSpec-governed educational figures per component, each teaching ONE relationship the model actually
  produces, drawn from an **authoritative producer** (no equations reimplemented, no gate math copied) and
  stamped with its badge + evidence strength + fidelity ceiling. Caption numbers are recomputed via a new,
  tested relationship analyzer (`puckworks.viz.relationship.classify_relationship`) that labels a curve
  increasing / decreasing / approximately_flat / non_monotonic / insufficient and refuses to call a
  one-grid-point wobble a reversal. `cameron2020.extraction_bdf` is the **hero** — first deep-dive
  component (`HERO_COMPONENT_IDS`) with three figures: the whole simulated shot over time, a pressure
  sweep (EY falls as pressure rises, in-model), and a beverage-mass / brew-ratio sweep — plus reused
  VizSpecs give at least five other components a figure. Every educational producer call **obeys the
  component's tour rights decision**: a not-executed, rights-blocked, or optional-unavailable component
  receives zero producer calls and a finite `no_figure_reason` (`NO_DEFENSIBLE_PUBLIC_RELATIONSHIP_YET` /
  `RIGHTS_BLOCKED` / `OPTIONAL_DEPENDENCY_UNAVAILABLE` / `REFERENCE_ONLY` / `TOO_EXPENSIVE_FOR_DEFAULT_
  TOUR`). Educational sweeps stay OUT of the canonical tour scientific hash; the frozen tour execution
  contract is unchanged.

- **Per-model narratives + figures for the Full Tour (#43).** Two new package modules support a
  layperson, per-model results view. `puckworks.product.lab_component_stories` carries, for every
  registered component, its espresso **process stage** (chronological), an exact **snapshot of the README
  model map** (Role + "What physics it represents", with `verify_component_stories` failing if the
  snapshot drifts from the live README), a plain **what it computes**, and a **layperson espresso
  implications** note framed as a general, caveated relationship (never a validated prediction — a
  standing disclaimer and per-note caveats enforce this). `puckworks.product.lab_tour_plots.
  component_figure` renders ONE matplotlib figure from a component's **actual** tour output (never
  fabricated) with a plain caption — a common-scenario time series, a measured-vs-reference bar, a
  first-drip bracket, or PASS/FAIL gate-metric bars — and returns `None` (a status note, not a fake plot)
  for blocked/optional/no-output components. No backend is forced, so figures embed inline in a notebook.
  The Colab notebook now renders a **per-model deep dive**: one illustrated card per model in espresso
  process order (Grind → … → Extraction), each with the stage + model, full reference, role and physics,
  a plot of its own output with a plain caption, what it computes, and — caveated — what that might mean
  for the cup. (The notebook's pinned dev-preview commit is bumped to a main commit that contains the two
  modules; a static test binds the pin to the modules the notebook imports.)

- **Fix: Colab Laboratory ImportError on `lab_tour` (#43).** The notebook's commit-pinned DEVELOPMENT
  PREVIEW pointed at a commit predating `puckworks.product.lab_tour` (the pin had not been bumped when the
  Full Laboratory Tour landed), so a real Colab run failed with `cannot import name 'lab_tour'` in the
  coverage-preview cell. Bumped `PIN_COMMIT` to a main commit that contains all three tour modules, and
  added a regression guard (`test_pinned_commit_contains_every_imported_puckworks_module`) that verifies —
  via `git cat-file` at the pinned commit — that every `puckworks.product` module the notebook imports
  exists there (the hermetic notebook smoke installs a local wheel and cannot catch a stale `git+` pin).
  Also hardened the install cell: every dev build shares version `0.4.0.dev0`, so a plain `pip install`
  would SKIP an already-present copy and leave stale code — the cell now **uninstalls first, then
  installs** the pinned build, refuses to continue (with "Runtime → Restart runtime" guidance) if an
  older `puckworks` was already imported in the session, and the environment-check cell fast-fails with
  the same guidance if `lab_tour` is missing.

- **Progressive Full-Tour results in Colab (#43):** `puckworks.product.lab_tour_display.
  tour_display_sections()` turns a tour result into ordered, plain-language sections — **Overview**, **Your
  reference shot**, the espresso-stage sections (Grind / Packing / Machine / Wetting / Flow / Bed dynamics
  / Extraction, empty ones omitted), **Calibration and evidence checks**, **Components not run**, and
  **Technical provenance** — with every registered component in exactly ONE section (`assert_every_
  component_shown_once`). Each card leads with a plain badge and headline (never the internal id, which
  sits in technical detail) and answers what ran, where its inputs came from, whether it is comparable to
  another result (always "compared only to itself"), and what it does **not** establish. The Colab
  notebook renders these sections; the human-acceptance checklist for the novice Full-Tour journey is
  recorded in `docs/ACCESSIBILITY.md` (#43, pending). No component numerics changed.

- **Rights-aware component-check runner (#43/#70):** `puckworks.product.lab_component_checks.
  run_component_checks(component_ids, *, execution_context)` is the Laboratory's single, rights-aware way
  to run a SELECTED set of components' registered gate(s) — the Laboratory never exposes an unfiltered
  `evaluate_all_gates()`. Rights are resolved BEFORE any gate/model/import call (a `RIGHTS_BLOCKED`
  component receives ZERO gate calls, returned as a typed non-scientific resolution; public contexts keep
  the affirmative code/output requirement — no broadening); it reuses the authoritative `gate_runner`
  (thresholds/formulas not copied), isolates failures per-component and per-gate, and keeps `EXECUTED` /
  `CHECK_FAILED` / `EXECUTION_ERROR` / `RIGHTS_BLOCKED` / `RIGHTS_NOT_CLEARED` / `NO_GATE_ACKNOWLEDGED` /
  `NOT_SELECTED` distinct (a numerical exception is an error, never a scientific zero). Each result carries
  gate id/status/metrics/units, evidence, a deterministic scientific hash, duration, and a fidelity
  ceiling (a gate pass is NOT experimental validation and NOT a full simulation). The Full Laboratory Tour
  now delegates its scientific-check routes to this one runner (single source). No component numerics
  changed.

- **Full Laboratory Tour — all available components, honestly (#43/#70):** `puckworks.product.lab_tour`
  turns the Laboratory into a broad walk of the whole registry. A **versioned, frozen** manifest
  (`full_laboratory_tour_v1`) resolves **every** registered component to exactly **one** primary route —
  `COMMON_SCENARIO` / `NATIVE_REFERENCE` / `SCIENTIFIC_CHECK` / `OPTIONAL_DEPENDENCY` / `RIGHTS_BLOCKED` /
  `NO_EXECUTION_PATH` (finite enums). `verify_tour_manifest()` fails when a new component is unclassified,
  a rights/runner change contradicts a frozen route, or a native runner/adapter is orphaned, so the tour
  never silently expands. `execute_laboratory_tour(scenario_request, *, manifest_id, execution_context)`
  runs each route through the rights-safe `lab_service` (preflight before producer) and returns one
  `TourComponentResult` per component, stage-grouped, with deterministic scientific hashes over canonical
  content only. Today it resolves all **25** components and exercises **23** eligible code paths — 1
  common-scenario (Cameron), 4 native references (including the batch-only LB reference, which
  `interactive_fast` omits), and 18 registered scientific checks (reusing `gate_runner`, rights-filtered,
  per-gate isolation) — with 1 rights-blocked (`grudeva2025.reduced`, **zero** producer/gate calls, #73)
  and 1 optional (`brewer2026.lb_taichi`). Incompatible outputs are never averaged, ranked, or overlaid
  (every component is comparable only to itself; only the common lens has a comparability group). The Colab
  notebook gains four experience modes — **Full Laboratory Tour (default)**, Quick Tour, Your Shot Only,
  Model Library Only — a pre-run coverage preview, and stage-grouped result cards with plain-language
  badges (USES YOUR SHOT / NATIVE REFERENCE CASE / SCIENTIFIC CHECK / …). In a public context the tour
  still runs only affirmatively-cleared components (no widening). "Ran successfully" and "directly
  comparable" stay separate facts; a gate pass is not experimental validation; a native reference is not a
  prediction of the entered shot. No version/tag change.

- **Public/local Streamlit split + producer-free Explorer + one execution facade (#43/#70):** every
  Laboratory surface (batch, Colab, both Streamlit apps) now runs through a single rights-safe service,
  `puckworks.product.lab_service.execute_lab_request(request, *, execution_context, …)` — explicit context
  required, rights preflight before any producer, one blocked selection blocks the whole request, and a
  typed blocked result carries the rights decision ONLY (no report/trace/observable/hash). A new
  producer-free `puckworks.product.lab_explorer.explorer_catalog()` exposes the full registry in plain
  language with **zero** execution (reuses the committed catalog + rights; keeps code/data/output rights
  separate; public-live availability is affirmative-rights-only — today just `brewer2026.lb_reference`).
  Two Streamlit entrypoints replace the single dev app: `apps/lab_app.py` (`LOCAL_PRIVATE`, dev) and
  `apps/lab_public_app.py` (`PUBLIC_ARTIFACT`, **fixed in code** — never user/query/env selectable) with a
  *Model library* (Explorer, runs nothing), *Component self-checks* (only rights-cleared components run
  live; download carries the preflight + provenance), and a *Try a reference shot* view disabled with a
  plain explanation + private-Colab link while Cameron is `NOT_REVIEWED`. Shared context-independent
  presentation/logic lives in `apps/lab_ui_common.py` (plain-language labels; chart text-alternative
  tables; novice result ordering). A Streamlit-Cloud deployment manifest (`requirements.txt`, minimal
  deps, no GPU/3-D) + `docs/DEPLOYMENT.md` document the maintainer deploy; `codespaces-ci` now health-
  smokes both apps. No public URL is advertised until a human verifies it signed out (#43). No public
  execution widened — rights states unchanged; Grudeva stays `RIGHTS_BLOCKED` (#73). No version/tag change.

- **Form-driven Guided Pull Laboratory Colab (#43):** `notebooks/guided_pull_laboratory_colab.ipynb` — a
  layperson browser path to *run a bounded shot* with a short form and one **▶ Run the Laboratory**
  button, no Python/shell/`pip`/CLI to type. It executes through the shared rights-safe service
  (`puckworks.product.lab_service`) with an explicit `LOCAL_PRIVATE` context, documented as a private
  user-controlled runtime that is **not** a public-hosting clearance. Three experience modes map to
  explicit finite requests — *Guided shot only* (primary lens, references none), *Guided shot + component
  self-checks* (primary lens + interactive-fast references), *Catalog only* (the producer-free Explorer,
  runs nothing). Install is an **exact commit-pinned DEVELOPMENT PREVIEW** (`0.4.0.dev0`), never mutable
  `main`, never under a v0.3.0 badge; the notebook shows package version, pinned commit, and install
  source. It carries no committed outputs, requests no secret or upload, and emits a
  `GUIDED_PULL_LAB_COMPLETE` sentinel. A `notebook-smoke` `laboratory-hermetic` job builds the current dev
  wheel, installs it via `PUCKWORKS_WHEEL`, executes the notebook with no network, and asserts the marker;
  a static contract test pins one visible run cell, no terminal instruction, the pinned-preview install,
  the service+context, the mode mapping, and that Grudeva is never offered. Human sign-off (open from
  badge, no terminal, one run) remains pending (#43). No version/tag/release change.

- **First affirmatively-cleared public-artifact path — `brewer2026.lb_reference` (#70):** the first
  tightly-bounded, per-component public-execution path, and the first affirmative outward rights clearance
  in the repository. A bounded provenance review (`docs/rights_review_notes.md`) established that
  `brewer2026.lb_reference` is **first-party** in-repo code (git blame 138/138 lines Tim Brewer, `c54a2a6`;
  no port/copy/licence marker) whose verification input is **generated synthetically in code** and whose
  reference is the **analytic** plane-Poiseuille `k = h²/12` — so `puckworks.rights` records code `CLEAR`,
  data `NOT_APPLICABLE`, output `CLEAR`, bounded to that LB channel code-verification path and clearing no
  other component, author, model class, or namespace. A **fourth** genuinely-executed native reference
  runner ships (`brewer2026.lb_reference`, `batch-only`): its producer solves the canonical synthetic
  channel once and its runner delegates the pass/fail band to `gate_lb_channel` verbatim (the acceptance
  literal is single-sourced — a new `lb_reference.channel_verification()` helper is shared by gate and
  runner, and the gate output is byte-identical). A request selecting **exactly** that runner
  (`lens_selection_policy=none`, `reference_selection_policy=selected`,
  `requested_reference_runner_ids=("brewer2026.lb_reference",)`) passes the `PUBLIC_ARTIFACT` preflight and
  runs precisely one native producer; the batch now carries the cleared preflight record + execution
  context in the artifact and makes the required-figure gate honest for a references-only run (a trace panel
  is required only when a lens executed; the absence is recorded, never silently skipped). This is **not** a
  generic bypass: the default/broad public batch still selects the `NOT_REVIEWED` Cameron lens and blocks
  before any producer; a mixed request pairing the cleared LB runner with any `NOT_REVIEWED` runner blocks as
  a whole; the clearance never propagates; `grudeva2025.reduced` stays `RIGHTS_BLOCKED` in every context
  (#73). Fidelity ceiling is explicit in code and docs — *synthetic plane-channel numerical code
  verification; does not validate porous coffee-bed physics, predict espresso extraction, establish
  experimental accuracy, or provide a comparable beverage metric.* No version/tag/numeric change (registry
  gates PASS=50 unchanged).

- **Roman-Corrochano second-lens readiness — deferred, not faked (#70):** `romancorrochano2017.extraction` is execution-ready on the shared scenario (inputs map without invention; **no** grinder-dial mapping) and would be a **separate-panel relative-trend** lens (`NOT_COMPARABLE` with Cameron EY/TDS — never converted, no difference/ratio/ranking). But adding it for public use requires an affirmative rights review (code execution + output redistribution) that was **not** completed — both remain `NOT_REVIEWED` — so **no adapter is implemented** and its public path is blocked by the rights preflight. `quantity_semantics.roman_corrochano_lens_readiness()` records this deterministically (`adapter_status: DEFERRED_PENDING_RIGHTS_REVIEW`, `validation_campaign: EXP-006`); a test pins that no Roman adapter is registered, selecting it runs no producer, and its output is never presented as absolute EY/TDS. #70 stays open.

- **Model→measurement matrix + catalog/quantity consolidation (#46/#70):** the Laboratory component catalog is now linked to the authoritative experiment metadata. `tools/experimental_data_needs.py` gains `model_to_measurement_matrix()` (one row per registered component: role → current evidence → campaigns → gates enabled → measurement-agenda blockers) and `validate_matrix_coverage()`, which requires every runtime/runner component to either name a campaign or carry a **documented exemption** (`grudeva2025.reduced` rights-blocked #73, `foster2025.machine_mode` machine-mode backlog, `wadsworth2026.inertial` inertial-flow backlog). The matrix renders deterministically into a second marker-bounded section of `EXPERIMENTAL_DATA_NEEDS.md`; `verify` now checks coverage; no component is silently omitted. `reference_basis.adapter_readiness` is explicitly **deprecated for readiness decisions** in favour of `quantity_semantics` (which separates shared-scenario execution readiness from output comparability and treats per-species / flow-trend / profile as non-denominator axes); it is retained only for the fail-closed inventory-conversion machinery. No model numerics changed (the Cameron lens still executes identically).

- **Community protocol + submission templates (#46):** the experimental-data campaigns are now executable. A template bundle (`docs/data_requests/templates/`: `campaign_metadata.yml`, `apparatus.yml`, header-only `calibration.csv` / `shot_metadata.csv` / `shot_timeseries.csv` / `fraction_metadata.csv` / `chemistry_measurements.csv` / `exclusions.csv` / `file_manifest.csv`, and a README of raw-data + instrument/synchronization + replication principles) plus executable **protocol packs** for EXP-001 (telemetry + chemistry), EXP-002 (dry-puck infiltration + physical first drip), EXP-006 (species-resolved fractions), and an EXP-005 index that points to the existing κ(t) protocol rather than rewriting it. A `validate-submission <dir>` command fail-closes on: missing required files, missing licence/calibration, duplicate/unknown shot ids, non-monotonic `elapsed_s`, non-finite values, duplicate rows, a checksum mismatch against `file_manifest.csv`, a missing raw/processed distinction, and a missing chemistry value with no status (a missing value is **never** inferred as zero). A clearly-labelled `SYNTHETIC_TEST_FIXTURE` exercises the parser/QC only — it is excluded from the data manifest and never used to validate a model. No measured value, sample size, sampling rate, tolerance, or acceptance threshold is invented (unknowns stay `DESIGN_CALCULATION_REQUIRED` / `SENSOR_SELECTION_REQUIRED` / `PILOT_REQUIRED`).

- **Experimental-data program (#46, #96):** Puckworks now publishes the measurements it needs. A community-facing entry page (`docs/EXPERIMENTAL_DATA_NEEDS.md`) explains why more data is needed, the evidence levels, the difference between fitting/verification/reconstruction/validation/discrimination/transfer, how to collect and submit data, rights/privacy, how accepted data become gates, and what Puckworks will **not** infer. A machine-readable catalog (`docs/data_requests/experimental_campaigns.yml`, schema documented) seeds eight campaigns (EXP-001…008) covering whole-shot telemetry + cup chemistry, dry-puck infiltration + physical first drip, grinder PSD/packing/permeability, poroelastic deformation, κ(t) mechanism discrimination, species-resolved fractions, spatial channeling, and cross-condition replication — each naming its target components/gates, quantity definitions, and the measurement-agenda blocker it resolves. `tools/experimental_data_needs.py` (verify/list/show/render) validates every campaign against the live registry + quantity ontology, enforces that every structured blocker is mapped (or explicitly deferred), and renders the campaign table deterministically into a marker-bounded doc section. No measured value / sample size / sampling rate / tolerance / threshold is invented (unknowns use `DESIGN_CALCULATION_REQUIRED` / `SENSOR_SELECTION_REQUIRED` / `PILOT_REQUIRED`); no private data is committed. A submission issue form and README/CONTRIBUTING sections make the workflow discoverable; a submission never auto-authorizes a model or an evidence upgrade. Standing issue #96 opened.

- **Rights preflight at the public Laboratory boundary (#73):** public Laboratory execution and public output publication are now genuinely rights-gated **before any producer runs**. A finite execution-context vocabulary (`LOCAL_PRIVATE` / `CI_VERIFICATION_NO_PUBLISH` / `PUBLIC_BATCH` / `PUBLIC_ARTIFACT`) is passed explicitly (never inferred from an env var's presence). `puckworks.product.lab_rights_gate.preflight()` resolves each selected common lens and native reference against the use-specific policy: local contexts follow `may_execute_locally` (block only on `RIGHTS_BLOCKED`); `PUBLIC_BATCH` requires affirmative code clearance; `PUBLIC_ARTIFACT` additionally requires affirmative output-redistribution clearance. The Actions batch runs the preflight first — a blocked public request writes only `…rights_preflight.json` (the rights decision, **no scientific output**) and fails; **zero producers are invoked** (call-count tested). Because `cameron2020.extraction_bdf` is `NOT_REVIEWED`, a `PUBLIC_ARTIFACT` run is **expected to block** until that review completes; the `guided-pull-batch` workflow now declares `PUBLIC_ARTIFACT`, uploads the preflight diagnostic on block, and the README no longer describes the public batch as generally available. A bounded rights review of Cameron + the native runners was performed and documented (`docs/rights_review_notes.md`): evidence gathered (Cameron is a documented independent reimplementation of the published Matter 2020 equations, unlike Grudeva's port), but retained `NOT_REVIEWED` and the outward path blocked pending a maintainer determination. Grudeva stays `RIGHTS_BLOCKED`; there is no generic bypass. No version/tag/numeric change.

- **Software authorship + commit identity (metadata only):** Puckworks is now credited as co-developed by **Tim Brewer** (`@trbrewer`) and **Peter Vonk** across `CITATION.cff` (software authors), `pyproject.toml` `[project].authors` (verified in the built wheel METADATA), a new root `AUTHORS.md`, and a README "Developers and citation" section. Software authorship is kept distinct from paper/manuscript bylines (unchanged — they remain author placeholders) and from Git commit history. A new `.mailmap` canonicalizes the erroneous historical commit identity (the moontowerrisk address, associated with the m00ntower GitHub account) and a bare-username variant to `Tim Brewer <t_r_brewer@hotmail.com>` — Git history is **not** rewritten (`git log --use-mailmap` now shows a single canonical identity). README governance gains an authorship check (both authors present + agreeing across surfaces; the erroneous identity is never a current author). No Peter email / ORCID / GitHub / affiliation was invented; no manuscript byline changed; no version/tag/release fact changed.

- **Research-radar recall gold set + current-main scan (#42 / #46):** the 51-candidate all-negative fixture measures precision only; a new metadata-only **positive gold set** (titles + DOIs of papers already carded here — `cameron2020` / `waszkiewicz2025` / `foster2025` / `wadsworth2026`; **no abstracts or copyrighted text**) tests **recall**. `research_radar.recall_metrics()` reports recall over the known-positive universe and names any missed positive (a regression is surfaced, not hidden). The coffee anchor retains every positive (recall 1.0) and drops every medical/petroleum/IoT negative; porous-media families stay deliberately broad (not coffee-gated). A scan-only radar run from current main (run 29698912098, head `a49d66b`, `publish_issue=false`) retained 51 candidates — again all off-domain false positives, **0 relevant** — with no issue auto-published and no implementation authorized.

- **Model-selection controls + semantic-safe panels (#43 / #70):** the Streamlit UI now exposes the full request — preset, recipe overrides, `domain_policy`, `lens_selection_policy` (primary/all_ready/selected/none) with a selected-lens multiselect, and `reference_selection_policy` with a selected-reference multiselect — and shows a **pre-execution preview** (selected lens ids + adapter readiness + rights eligibility, resolved reference ids + runtime class) so a model is never executed merely because it is available. The Actions batch accepts the same selection via validated `LAB_LENS_SELECTION_POLICY` / `LAB_LENS_IDS` / `LAB_REFERENCE_SELECTION_POLICY` / `LAB_REFERENCE_IDS` (parsed in Python, never shell-interpolated; an ambiguous combination is an explicit error). Panels are now **component-qualified** (`component::trace::unit`) so identical trace ids from two components can never collide, and each carries a `semantic_group` (reference basis + unit) — `assert_semantic_safe()` rejects a same-id/different-group collision, because same unit is necessary but **not** sufficient to share a panel. No science recomputed in the view layer.

- **Recomputed hash API + artifact replay verification (#70):** the public `scientific_sha256` / `capability_snapshot_sha256` / `artifact_sha256` now **always recompute** from the report's own content (never return the embedded claim under a computing name); explicit `embedded_scientific_sha256` / `embedded_capability_sha256` / `embedded_artifact_sha256` read the stored claim. `BuildProvenance` is format-validated (git-hex source commit, 64-hex wheel sha, numeric run id, non-empty version; `None` is a visible gap). A new `verify-artifact` CLI + `lab.verify_artifact()` verify at four **independent** levels — schema (required fields, finite JSON, schema version), integrity (recompute all three hashes vs the embedded claims), **producer replay** (reconstruct the request, rerun the producer, compare the fresh scientific hash, report the first differing path on mismatch), and build identity (compare installed version + wheel sha when supplied, else `not_verified` rather than guessing). A self-consistent artifact is never conflated with a producer-reproduced one. The Actions batch runner now writes into a **staging** directory, verifies the artifact, and atomically renames staging → final — on failure no partially valid final directory is left (a failure summary is written outside it); the manifest gains the capability hash, the lens/reference/domain policies, and the verification result. No model numerics changed.

- **Orthogonal quantity semantics + separated readiness axes (#70):** the old `reference_basis.QUANTITY_BASES` conflated a true reference denominator, spatial discretization, species cardinality, phase, and a relative-trend output class. New `puckworks.product.quantity_semantics` makes each axis independent (`QuantityDefinition`: numerator, reference-basis **denominator only**, phase, species scope, spatial support, temporal support, aggregation, unit, role) — `per_species` / `flow_trend` / `liquid_phase_profile` are no longer encoded as denominators. A plot **compatibility signature** decides when two series may share an ordinary axis or have a difference/ratio computed (same unit is necessary but **not** sufficient; a relative trend is never overlaid with an absolute EY/TDS). Crucially it separates the two decisions that were entangled: **shared-scenario execution readiness** (`READY_FOR_SHARED_SCENARIO` / `INPUT_ADAPTER_REQUIRED` / …) and **output comparability** (`DIRECTLY_OVERLAID` / `FACETED_SEPARATELY` / `NOT_COMPARABLE` / …). Re-audit: `romancorrochano2017.extraction` is execution-ready as a **separate trend panel** yet its output is `NOT_COMPARABLE` to Cameron EY; `mo`/`pannusch` are `INPUT_ADAPTER_REQUIRED` + `FACETED_SEPARATELY`; `grudeva` is rights-blocked — **no candidate is directly comparable to Cameron EY**, and a model does not need an EY/TDS conversion merely to execute. A structured `measurement_agenda()` turns each input blocker into an acquisition action. No model numerics changed; no second lens added.

- **Single-source native reference producers + result contract v2 (#70):** each native reference runner now consumes ONE shared full-precision summary producer (`puckworks.product.lab_reference_producers`) instead of re-deriving the fitted quantity / collapse statistic / first-drip bracket inline; the gate remains the pass/tolerance authority and a test binds the two (they compute the same values). The Foster first-drip threshold is a single named model constant `foster2025.infiltration.FIRST_DRIP_THRESHOLD_G` consumed by **both** the gate and the runner (the gate's own `argmax` first-drip is replaced by the explicit `observed_first_drip_s` crossing — no numerics change; the `0.5`/`0.7`/`1.2` literals no longer appear as executable constants in the runner). Producer precision is preserved (outputs carry the exact `value` plus a separate rounded `display_value`; rounding never happens before canonical hashing). Failure results satisfy the full schema with a finite `execution_state` vocabulary and a **sanitized, path-free** error message (no stack traces or filesystem paths leak into a published artifact). Runner results consume the centralized code/data/output rights and flag outputs not cleared for public redistribution. No model numerics or gate verdicts changed (gates PASS=50 unchanged).

- **Explicit Guided Pull Laboratory component catalog (#70):** the component matrix no longer infers common-scenario compatibility from a broad `stage`/`kind`/`role` substring heuristic. A committed `puckworks.product.lab_catalog` states one authoritative record per registered component — the **disposition** and **adapter capability** are explicit; registry-derived fields (module, card path, stage, role, evidence, provenance, **gate ids**, validity range) are declared and validated against `puckworks.components()`; runner/adapter capability, rights (code/data/output + public-use eligibility), and quantity basis are consumed from their authoritative sources. `validate_catalog()` is a CI gate: a missing entry, an unknown gate id, an unresolved runner/adapter id, a rights mismatch, or a rights-blocked component not dispositioned `RIGHTS_BLOCKED` fails. `lab._lab_spec` consumes the catalog (an AST test proves it no longer compares against stage/kind literals); the redundant `_COMMON_SCENARIO_LENSES` dict is removed in favour of the `ADAPTERS` registry. No component count is hard-coded; the env-dependent optional-dependency skip remains a runtime overlay, not a committed capability. No model numerics changed.

- **Adapter-driven common-scenario lens execution (Lab schema v5, #70):** the Laboratory no longer "runs Cameron, then reports a selection" — it prepares a model-independent scenario, resolves the selected lenses, evaluates each lens's OWN domain, and executes **only** the selected, ready, in-domain lenses. `prepare_scenario()` calls no producer; a `LensAdapterSpec` protocol wraps each model (the first adapter wraps Cameron and calls the existing `simulate_pull` — no equation re-implemented); a finite `lens_selection_policy` (`primary` / `all_ready` / `selected` / `none`) replaces the future-expanding empty-tuple default (`requested_lens_ids` requires `selected`; duplicates are canonicalized; adding a future adapter never changes `primary`). The producer is now invoked **only** for a selected+ready+in-domain lens: selecting `none`, a registered-but-non-ready component, a rights-blocked lens, or a domain-blocked Cameron runs **no** producer; the executed-lens count equals the producer-invocation count; a fake adapter executes independently of Cameron; and one adapter failing never erases another. Each `LensResult` records requested/readiness/rights-use/domain/producer-invoked/status/mapping/outputs/decline-reason. Reference selection now resolves **components** (a registered component with no runner is `RUNNER_NOT_IMPLEMENTED`, a rights-blocked one is `RIGHTS_BLOCKED` and never executed; only a non-registered id is "unknown"). No model numerics changed; Cameron remains the only executable lens.

- **Affirmative rights clearance + release safety (#73):** rights are now **use-specific** — one state is never universally sufficient. New policy functions (`may_execute_locally`, `may_execute_in_public_batch`, `may_publish_outputs`, `may_include_code_in_release`, `may_include_data_in_release`) each consult the relevant code/data/output field with the strictness that use demands: a `RIGHTS_BLOCKED` component is refused everywhere; `NOT_REVIEWED` stays inspectable **locally** but is a visible **gap** for public execution, output redistribution, and release (never reported as "clear"); only affirmative clearances (`CLEAR`/`PERMISSION_DOCUMENTED`/`INDEPENDENT_REIMPLEMENTATION`) permit an outward or release use. The **generic release bypass is removed** — there is no `--allow-rights-blocked` flag; the guard hard-blocks only on code not cleared for release inclusion and passes once the blocked module is absent (an authorized removal makes it pass, not a "build anyway" flag), while `NOT_REVIEWED` gaps are reported, not silently passed. `RightsRecord` gains validation (ISO review date; reviewed determinations require source + date; `RIGHTS_BLOCKED` requires a decision issue + reason; `PERMISSION_DOCUMENTED` requires permission metadata; `NOT_APPLICABLE` requires a reason; unknown/lowercase vocabulary and duplicate/unregistered records are rejected, with a `tombstone` exemption for removed components). Product-local `"clear"` claims are gone: `RunnerSpec` no longer defaults to `"clear"` (runner results consume the centralized record's code/data/output states + a public-output decision), the adapter audit derives rights from the registry, and reference-basis admissibility consumes the use-specific policy. A structured `review_backlog()` surfaces the reviews still owed (Cameron code+outputs first). No model numerics changed; Grudeva 2025 stays rights-blocked pending #73.

- **Deterministic research-impact source scope (#46):** `tools/research_impact.py` now has an explicit source-scope contract. The default **committed** scope examines only git-tracked cards/intake (via `git ls-files`), so the canonical report is reproducible from a commit and never silently incorporates a maintainer's untracked local files; **working_tree** scope opts in to untracked files for local authoring, and a non-git directory degrades to a recorded `working_tree_fallback` rather than a false `committed`. The report gains a `source_scope` block (`scope`, `requested_scope`, tracked/untracked counts, `excluded_untracked_paths`) and `schema_version` 2. CI and the standing-issue workflow pass `--source-scope committed` explicitly. Verified: run 29693508558 (head `3d9e254`) reproduces byte-for-byte from a clean detached worktree at the same SHA; the previous local divergence was exactly the 17 untracked cards, now excluded by committed scope.

- **Research-radar 51-candidate adjudication fixture + precision metrics (#42 / #46):** the FIRST real research-radar scan (workflow run 29666830887, source commit `5f300c00`, artifact SHA-256 `21a53ad1…`) is committed verbatim as a regression fixture with its recorded human adjudication (all 51 retained candidates are off-domain false positives from the broad generic query families; **0 relevant**). A deterministic `research_radar.adjudication_metrics()` computes precision@retained (0.00) and per-query-family precision (every generic family 0.00; coffee-anchored families quiet) over the human labels — it derives no relevance itself, only tallies the adjudication, rejects a non-vocabulary label, and surfaces any unlabelled candidate rather than hiding it. This guards against a classifier change silently turning off-domain noise into apparent relevance. The scheduled/dispatchable `research-impact` workflow was exercised from `main` (run 29691062085): intake validated, the deterministic registry-impact report computed + uploaded, and the idempotent monthly note appended to #46.

- **Guided Pull Laboratory reference-basis ontology + fail-closed inventory adapters (#70):** groundwork for a *possible* second common-scenario lens — delivered as the ontology + validators + audit, **not** a second lens (none is ready). A finite quantity-basis vocabulary (`bed_volume` / `grain_volume` / `per_bed_cell` / `per_species` / `liquid_phase_profile` / `flow_trend` / …) makes each component's reference basis a typed value instead of prose; inventory-conversion primitives are **fail-closed** — the only registered rule is the identity (same basis), so every cross-basis request raises `UnsupportedConversion` (the framework never invents a scale factor), and a conservation primitive rejects any transform that does not conserve total solute inventory. Second-lens admissibility is therefore mechanical: `mo2023_2.coupled_bed` (per-bed-cell) and `pannusch2024.solver` (per-species) have no validated conversion to Cameron's bed-volume basis, `romancorrochano2017.extraction` is a flow trend (not an absolute EY/TDS), and `grudeva2025.reduced` is rights-blocked (#73) — **no candidate is admissible, so no second lens is added.** The existing prose adapter audit is now bound to the typed basis (they cannot disagree). No model numerics changed.

- **Guided Pull Laboratory native-runner authority + validation + selection (#70):** every pass/band verdict a native reference runner reports is now the **authoritative gate verdict** — the runner *calls its component's quick gate* (`gate_waszkiewicz_static_refit`, `gate_wadsworth_collapse`, `gate_infiltration_triangle`) and surfaces it verbatim, so a magic number (the wadsworth `0.7 < ratio < 1.2` collapse band, the foster `> 0.5 g` first-drip threshold, the waszkiewicz refit tolerances) can never drift between a runner and its authority. The foster first-drip crossing is now **explicit** — when the weight never crosses the threshold there is no first drip (reported `unavailable`), never a spurious `argmax`-of-all-False sample at t[0]. `RunnerSpec` and the runner registry are validated (runtime-class vocabulary, key/component-id match, registration, rights consistency), results are schema-sanitized + finite (a NaN or a unit/role-less output becomes `FAILED`, never a malformed result), and selection is explicit (`run_selected` raises on an unknown id by default — never a silent drop; `available_runners()` / `runtime_class()` expose the selectable set). No model numerics or gate thresholds changed.

- **Guided Pull Laboratory unit-safe scientific figures (#43 / #70):** the shared plotting layer (`lab.render_data`) is now **unit-safe by construction** — every source trace is split into one panel per unit, so a single ordinary y-axis never overlays incompatible units (bar / g/s / g / % / kg/m³). An explicit `lab.assert_unit_safe()` validator rejects a mixed-unit panel, and both the Streamlit UI and the Actions batch render through it (they *cannot* draw a mixed-unit axis). The batch now emits one figure **and** a CSV text-alternative per panel, records a `panel_inventory` in the manifest, and keeps the required-figure gate (no plottable panel fails the job). The Streamlit UI adds a per-unit panel selector, per-panel data table + CSV download, an axis unit label, and a `domain_policy` (warn/strict) control that surfaces the operational block path. No science recomputed in the view layer.

- **Guided Pull Laboratory request semantics + layered integrity (schema v4, #70):** the Lab request is now honest and operational. `domain_policy` (`warn`/`strict`) is enforced through the authoritative product domain BEFORE the producer runs — a `REJECTED` input blocks under any policy and a `WARNING` blocks under `strict`; when blocked the scientific producer is **not** invoked and the lens is surfaced as `REQUESTED_BUT_NOT_EXECUTABLE` (never produced as zero). `requested_lens_ids` actually selects the common-scenario lenses (unknown id raises; non-executable id surfaced, not dropped; `executed_common_scenario_lenses` is derived). `reference_selection_policy` (`none`/`interactive_fast`/`selected`) is unambiguous (unknown selected id raises). Static native-runner/adapter **capability** is separated from per-request **execution** state (a validated `ComponentLabSpec`, with a `METADATA_INCOMPLETE` fallback rather than an invented capability). Integrity is now **three recomputed layers** — `scientific_payload_sha256` (invariant to build identity, Python version, and optional-dependency installation), `capability_snapshot_sha256` (env-dependent), `artifact_sha256` (full) — with `verify_integrity()` tamper detection and finite canonical JSON (`NaN`/`Infinity` rejected). No model numerics changed; the executed common-scenario lens is still Cameron only; no multi-model validation claim.

- **Centralized component rights + Grudeva legacy containment (#73):** a single authoritative rights registry (`puckworks.rights`) with distinct code/data/output states and a finite vocabulary (CLEAR / PERMISSION_DOCUMENTED / INDEPENDENT_REIMPLEMENTATION / RIGHTS_REVIEW_REQUIRED / RIGHTS_BLOCKED / NOT_REVIEWED / NOT_APPLICABLE; an unreviewed component is NOT_REVIEWED, not CLEAR). `grudeva2025.reduced` is code RIGHTS_BLOCKED pending #73; the Guided Pull Laboratory, native runners, and adapters consume the registry (the product-local rights dictionary is removed) and refuse it; a release-readiness guard fails if a rights-blocked component would enter a new artifact; README governance rejects an 'Executable model' label for it. README/card/module/registry wording corrected to 'Legacy - rights-blocked pending #73' (retained in history; not for new execution/integration). No model numerics changed; v0.3.0 history/assets untouched. #73 stays open pending the maintainer decision.

- **Guided Pull Laboratory second-lens adapter-readiness audit (#70):** a deterministic audit (`puckworks.product.lab_adapter_audit`) of the extraction candidates against the common scenario. Finite decisions: `pannusch2024.solver` and `mo2023_2.coupled_bed` -> ADAPTER_REQUIRES_TESTED_CONVERSION, `romancorrochano2017.extraction` -> OUTPUTS_NOT_COMPARABLE, `grudeva2025.reduced` -> RIGHTS_BLOCKED (#73). No candidate is ready without an invented conversion, so **no second common-scenario lens is added** — the honest dispositions + report are the deliverable.

- **Scheduled research-intake/registry-impact automation (#46):** a `research-impact` workflow (PR read-only; scheduled/dispatch posts a monthly note to #46 from trusted main, `issues:write` gated; SHA-pinned) that validates the intake records and computes the deterministic `tools/research_impact.py` report. Added radar precision-regression fixtures (relevant espresso extraction / porous-bed infiltration / espresso telemetry vs irrelevant medical / petroleum / IoT classes); the first scan's precision is recorded on #42 (51 retained, 0 relevant — generic families noisy; porous-media physics families deliberately kept broad, not coffee-gated).

- **Guided Pull Laboratory native reference runners (development):** three genuinely-executed native reference cases (`waszkiewicz2025.poroelastic` static refit, `wadsworth2026.permeability` Table-1 percolation collapse, `foster2025.infiltration` first-drip bracket), each reusing the validation-gate callables (no equation duplication), with per-runner failure isolation. The Lab now separates executed native references from not-yet-implemented coverage; `grudeva2025.reduced` stays RIGHTS_BLOCKED (#73).

- **Guided Pull Laboratory contract hardening (schema v3, development `0.4.0.dev0`):** exact scenario
  identity + override provenance (`guided_v1` runs are no longer mislabelled `pv19_named`); typed
  `ScenarioRequest`/`ScenarioExecution` records; separated **scientific-payload** vs **full-artifact**
  integrity hashes (the downloadable artifact now carries `source_commit`/`package_version`/
  `workflow_run_id`/`wheel_sha256`, supplied explicitly — no git subprocess in the producer); correct
  observable roles (prescribed/derived/simulated/unsupported/diagnostic); an explicit component
  capability/rights matrix (with `grudeva2025.reduced` marked **RIGHTS_BLOCKED** pending issue #73);
  honest reference-suite coverage (executed results vs not-yet-implemented placeholders); real
  scientific trace plots in the Streamlit UI and the Actions batch (required figure — the batch fails if
  it cannot render); and an artifact hash manifest. Still one executed common-scenario lens (Cameron);
  no multi-model validation claim.

- **Guided Pull Laboratory** (development `0.4.0.dev0`, not released): `puckworks.product.lab` exposes
  the full component registry as a coverage matrix and runs the compatible subset as independent model
  lenses (one executed extraction lens today) — never a validated digital twin. Added a Codespaces
  devcontainer + Streamlit UI (`apps/lab_app.py`, `webapp` extra; not a core dependency) and a
  reproducible `guided-pull-batch` Actions runner. Browser/Pyodide hosting is a documented feasibility
  note only (`docs/PAGES_FEASIBILITY.md`); nothing is deployed to a third-party host.

## 0.4.0.dev0

Development line opened after the v0.3.0 release. Source/development builds identify themselves as
`0.4.0.dev0`; the latest **public release remains v0.3.0** (GitHub Release; not on PyPI) and its
install/notebook guidance is unchanged. Unreleased work is tracked above and in `docs/ROADMAP.md`
§7.1. Three static, generated public interactives are now **live** (no new model coupling): PV-03
"The Cup Hides the Clock", PV-05 "More Physics Made It Worse", and **PV-04** "How We Falsified Our Own
Espresso Headline" (<https://trbrewer.github.io/puckworks/analysis-autopsy/>) — the analysis autopsy
exposing replicate-level extraction-yield points, per-panel evidence partitions, and the corrected
middle-minus-coarse (dial 1.7 − dial 2.0) result. No next public-value product lane has been
authoritatively selected — selection is pending. This is development-line work only — not a release
candidate; the latest public release remains v0.3.0.

## 0.3.0

First functional minor after v0.2.0. Adds the caller-owned input boundary and the **Guided Espresso
Pull** — a rights-independent, runnable *guided mechanism explorer* — under the supported
`puckworks.product` API. Rights-independent throughout: no upstream fixture data is shipped or loaded.
puckworks remains **GitHub-only** (not on PyPI).

### Added

- `puckworks.product.normalize_shot_input` — a rights-independent normalization boundary mapping
  caller-owned / synthetic channels to a versioned `ShotInput`.
- Guided Espresso Pull core: `PullRecipe` / `PullConfig` / `PullRun` / `StageResult` /
  `DomainFinding` / `ComponentCoverage`, `simulate_pull`, `evaluate_domain`, the `pv19_named`
  (fixed reference) and `guided_v1` (range-limited) presets, deterministic JSON/Markdown export, a
  full 25-component coverage ledger, and the `puckworks-pull` CLI. The one executed chain is the
  coherent `cameron2020.extraction_bdf` shot model; every other component gets an explicit
  disposition rather than being silently coupled.
- Authoritative `PullRun.traces` (`PullSeries` / `PullTrace`) copied from the solver at full
  precision, each labelled by value role (prescribed input · simulated output · derived quantity).
- Stage-by-stage visual report: `render_pull_report` → `PullReportArtifacts` (evidence-badged
  figures + captions + JSON/Markdown), matplotlib kept lazy so the core stays matplotlib-free;
  `puckworks-pull run … --report-dir/--figures`.
- Guided Colab notebook (`notebooks/guided_espresso_pull_colab.ipynb`) with native `#@param`
  controls, a `PUCKWORKS_WHEEL` override for hermetic testing, and SHA-256 hash-verified install.

### Changed

- README hero updated to the maintainer-supplied logo; the development-source line now reads
  `0.3.0`. The latest **public release remains v0.2.0** until v0.3.0 is published.

### Scientific / evidence

- The guided pull is an `EXPLORATORY_SIMULATION`, code-verified against the source paper, **not**
  independently validated against a measured cup. It does **not** model puck wetting, physical first
  drip (reported `unavailable`; the old number survives only as a diagnostic), a dynamic pressure
  profile (pressure is a prescribed constant input), or a thermal transient (temperature is
  recorded-only). It reports chemical **composition**, never sensory flavor, and never averages
  alternative components into a consensus.

## 0.2.0

First verifiable post-0.1 release: canonical status, complete gate evaluation, a deterministic
Paper 3 archive, a hardened CI supply chain, and a fully-adjudicated per-claim evidence graph.

### Added
- **Canonical status source of truth**: `docs/status/current.json` → generated
  `STATE_OF_TRUTH.md` (`python -m puckworks.statusdoc`); a CI verifier rejects stale/contradictory
  state; `--audit-ruleset` reads the actual GitHub required-checks setting.
- **Typed gate evaluation** (`puckworks.gate_runner`): `GateStatus`/`GateResult`/`GateSuiteResult`;
  every gate runs (no short-circuit); exceptions become `ERROR`; zero-gate components are explicit
  (`SKIP`/`ACKNOWLEDGED_EXCEPTION`), never a vacuous pass. `run_all_gates` kept as a compat wrapper.
- **Deterministic Paper 3 archive** (`puckworks.paper3.archive`): `create/verify/inspect-archive`
  build a byte-reproducible `.tar.gz` with a per-member sha256 + role + provenance manifest,
  verifiable without the source checkout; privacy/redistributability fail-closed scan.
- **Paper 3 per-claim evidence graph** (schema v2): 51/51 gate wirings adjudicated; scope-aware
  strict modes (`--scope paper3` release gate, `--scope all`); component→gate roll-up and
  zero-gate policies enforced.
- **Lateral-coupling discrimination harness**: exact Ξ equalization group, continuous-α proxy
  matching; representational/mathematical distinguishability only (Paper 4 NOT authorized).
- **Publication-freeze lifecycle**, **sanctioned-export** contract + synthetic pipeline, and
  **pressure-atlas v2** (from the convergence lane).
- Supply-chain: `security.yml` (dependency-review + pip-audit); SHA-pinned Actions; a `min-deps`
  lane proving the dependency floors.

### Changed
- Supported Python stated explicitly (3.10–3.13; 3.12 primary); dependency floors `numpy>=2.0`
  (uses `np.trapezoid`), `scipy>=1.13`.
- `foster2025.infiltration` evidence tier demoted `controlled_independent → sign_or_compatibility`
  under the roll-up policy (ROADMAP §7.1); the registry declares no `controlled_independent`
  component.
- Registry metadata validation raises explicit exceptions (survives `python -O`); state
  vocabulary formalized.
- `paper3.build bundle` renamed to `list-bundle` (it lists paths; use `archive create-archive`).

### Fixed
- **Red CI repaired** (R0/R1): matplotlib-dependent figure tests ran in the `.[dev]`-only quick
  lane; now `importorskip("matplotlib")` + `.[figures]` in slow-science. Invalid job-level
  `secrets` in `if:` replaced with a `vars`-gated pattern.
- `all(...)` short-circuit in the gate runner (later failures were hidden) — see gate_runner.
- **Private corpus could leak into the distribution**: the broad `puckworks.data` `**/*.csv`
  package-data glob swept `visualizer/{raw,normalized_v3,crawl_*}` + `aggregate_stats.csv` into the
  wheel/sdist. Added `exclude-package-data` + a `packaging` CI job that inventories the built
  distributions (no private paths; required data present) and clean-room-installs the wheel.

### Scientific / evidence
- Every asserted Paper-3 claim carries an honest per-gate tier, relationship, caveat, and
  claim-not-supported statement; no tier is promoted by inference. G10 viscosity tensions and the
  c_sat 212.4/224/170 constant are surfaced (not merged).

### Data / provenance
- New MANIFEST dataset `cameron2020/fig5_grind_deviation` (rule-5 intake) backing the streamtube
  held-out gate.

### Compatibility / migration
- `run_gates`/`run_all_gates` remain Boolean wrappers over the typed runner.
- `bundle` still works but warns; prefer `list-bundle` / `create-archive`.
- No public numerical behaviour change; existing examples reproduce.

## 0.1.0
- Initial registry scaffold: 7 founding components, 3 gated.
