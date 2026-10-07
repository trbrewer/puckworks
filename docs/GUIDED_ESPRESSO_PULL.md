# Guided Espresso Pull

A rights-independent, runnable **guided mechanism explorer** (issue #48). You enter a bounded recipe
and run one coherent, model-backed espresso pull on CPU, then watch it stage by stage with
evidence-labelled traces, a visual report, and honest domain warnings.

It is **not** an optimizer, a flavor/taste predictor, or a digital twin. It reports chemical
**composition** where supported — never sensory flavor. It ships and loads **no** upstream fixture
data; everything is computed from model code plus your inputs.

Public surface: `puckworks.product` (see [API.md](API.md)). Released in **v0.3.0** (GitHub-only; not on
PyPI).

The disclosures below describe the development source. They do not change the frozen v0.3.0
release or notebook installations pinned to that release.

## Presets

| preset | purpose | editable |
|---|---|---|
| `pv19_named` | fixed reference scenario — deterministic regression + a stage-scorecard example | none (fixed) |
| `guided_v1` | user-adjustable mode with configured product intervals and computational admission bounds | the active controls below |

```python
from puckworks.product import load_pull_preset, simulate_pull, render_pull_report

recipe, config = load_pull_preset("guided_v1")
run = simulate_pull(recipe, config)          # deterministic; run_id derives from inputs
artifacts = render_pull_report(run, "guided_pull_report")   # JSON + Markdown + figures (needs [viz])
```

## The primary model

The one executed chain is `cameron2020.extraction_bdf`, a coherent, self-contained single-solute BDF
shot model spanning **grind → machine/flow → extraction → cup**. Its evidence strength is
code verification, with source reproduction unresolved; the guided pull is badged `EXPLORATORY_SIMULATION` and is
**not** independently validated against a measured cup.

Every other registered component is dispositioned in the run's **coverage ledger** with an explicit
`executed` flag — only the primary model is executed. Alternatives are `CALIBRATION_ONLY`,
`AVAILABLE_AS_SEPARATE_LENS` (eligible but **not executed** — their conventions are not verified as a
causal adapter to the primary chain), or excluded. Nothing is blended into a consensus; the report
never claims a comparison it did not run.

## Inputs

### Active controls (each changes the calculation)

| input | configured product interval | computational admission bounds | unit |
|---|---|---|---|
| `dose_g` | 15–25 | > 0 and ≤ 100 | g |
| `target_beverage_g` | 25–60 | > 0 and ≤ 500 | g (prescribed target) |
| `pressure_bar` | 6–9 | > 0 and ≤ 20 | bar (prescribed model overpressure) |
| `grind_setting` (EK43 dial) | 1.1–2.3 | 1.0–2.5 | dial |
| `coffee_profile` | `reference` only | model-backed selector | — |
| `domain_policy` | `warn` / `strict` | — | — |

### Pressure convention and source support

`pressure_bar` is passed **unchanged** to the current Cameron overpressure-based calculation.
It is neither measured puck pressure nor an independently verified pressure drop across the bed.
The [development guide's primary-source account](research/ESPRESSO_DEVELOPMENT_GUIDE.md)
distinguishes the SI S1 **5-bar pump-overpressure** reference from the main paper's **6-bar
static-pressure** label (p. 638 and Fig. 5). Their pressure-reference and sensor-node equivalence
remain unresolved; this input does not apply a universal one-bar conversion. The older SI intake's
absolute/gauge interpretation is not a verified pressure transfer.

The source reference configuration is **20 g dose / 40 g beverage / 5 bar model overpressure**.
SI S5 explores scaled **3/5/7/9-bar model cases**, not four measured pressure campaigns. The
configured **6–9-bar interval is product policy, not an experimentally validated band**. Likewise,
15–25 g dose and 25–60 g beverage are product intervals: the SI's 16/18/20/22/24-g geometry
exploration does not validate every dose/beverage combination. The EK43 1.1–2.3 interval has seven
SI S3 shot-time settings as source support; the wider 1.0–2.5 microstructure knots permit
computational admission, not validation of every recipe or transfer to another grinder.

### Recorded-only inputs (do **not** affect the model)

- `brew_temperature_c` — recorded with the recipe but **not a model input** in v0.3.0 (there is no
  thermal transient). It is reported as a `NOT_APPLICABLE` domain finding, never as an extrapolation
  warning, and changing it changes no number.

### Rejected / unsupported inputs

- `bean_label` — **metadata only**. It never changes a numeric result and is excluded from the
  deterministic `run_id`. Contrast with `coffee_profile`, which selects the model-backed parameters.
- `preinfusion_s`, `preinfusion_pressure_bar` — **rejected** (no preinfusion-capable component is
  coupled; the primary model begins from a saturated bed).
- `basket_diameter_mm` — **rejected** (the solver uses a fixed basket radius; no override is consumed).
- `mean_particle_radius_m` — **rejected** for `guided_v1` (no verified adapter maps a physical radius
  to the model's dial). Supply an EK43 `grind_setting` instead.

Unsupported stage overrides, non-empty lens requests, non-constant pressure profiles, and unknown
config ids/versions are all rejected — the engine never accepts a configuration it cannot honestly
execute.

## Domain policy

- **Hard-invalid** inputs (dose/beverage/pressure outside the admission bounds above, a
  non-liquid-water temperature, grind outside the admitted table range, or an unsupported field)
  are **REJECTED** — the run raises. Admission does not guarantee numerical or physical safety.
- **Product-interval** departures are **WARNING** under `domain_policy="warn"` (the run can complete
  with warnings) and **block** under `"strict"`. Membership is `IN_DOMAIN`; these unchanged enum
  values classify product policy, not scientific evidence. The legacy JSON field `supported_range`
  carries that configured interval, not an empirical validation band.
- **5 bar** still warns (and blocks in strict mode), despite being the model's source reference.
  **6 and 9 bar** still satisfy the pressure interval in both modes. Neither outcome establishes
  physical validation. Leaving an interval does not by itself prove empirical extrapolation, and
  moving back inside does not guarantee a supported physical prediction.
- Values are **never silently clamped**; the supplied value is preserved everywhere.

## Traces (authoritative, full solver precision)

`run.traces` are typed series copied straight from the solver result (not rebuilt from the rounded
final observables). JSON preserves full solver precision; only display renderers round. Each series
carries a **value role**: `prescribed_input`, `simulated`, or `derived`.

| trace / series | role | unit | derivation |
|---|---|---|---|
| prescribed model overpressure | prescribed_input | bar | `pressure_bar` passed unchanged — an input, not a prediction |
| model flow | simulated | g/s | `area · q · rho_out`, `q` from `darcy_flux(gs, p_bar)` (constant) |
| cumulative beverage mass | derived | g | integral of the constant model flow; endpoint = target by construction |
| cumulative dissolved mass | simulated | g | model solute reaching the cup (`m_cup`), kg→g |
| cumulative extraction yield | derived | % | `100·(dissolved mass)/dose` |
| outlet concentration | simulated | kg/m³ | modeled outlet liquid concentration (`cl_out`) |
| end-of-shot liquid profile | simulated | kg/m³ vs m | `cl_final` along bed depth at `t_shot` |

## Explicit limitations

- **Historical Cameron source reproduction remains unresolved.** The Codex local audit of
  2026-09-30 (not independent human review) used 20 g dose / 40 g beverage / 5 bar model overpressure,
  N40/M24, EK43 GS 1.1–2.3, and the retained 118 kg/m³ grain inventory. Its RMSE was **7.102391 EY
  percentage points against the homogeneous curve** and **6.480780 EY percentage points against
  experimental means**. See the [original local audit](analysis/cameron_local_audit_20260930.md)
  and the [comparison and producer attribution](research/ESPRESSO_PROGRAMME_REVIEW_2026-10-01.md),
  sections B–C. The cause remains unresolved. These are historical reference-configuration scores,
  not newly computed scores, pointwise error bars, correction factors, or measured errors for the
  current recipe (including recipes at other pressures).
- **Physical first drip is unavailable.** The primary model begins from a saturated bed and does not
  model wetting or hydraulic breakthrough, so `first_drip_s` is reported as `unavailable`. The old
  first-positive-cup-solute time survives only as the honest diagnostic
  `first_modeled_solute_arrival_s` (a numerical marker, **not** physical first drip).
- **Wetting / infiltration is not modeled** in `guided_v1`.
- **Temperature has no effect** (recorded-only; no thermal transient).
- **Composition, not flavor** — a single soluble pool; no per-species composition, no sensory claim.

## Outputs

- `pull_run_to_json` / `pull_run_to_dict` — deterministic scientific payload (no wall-clock; traces at
  full precision).
- `pull_run_to_markdown` — a human report whose "Authoritative traces" section is a **static text
  equivalent** of the figures.
- `render_pull_report(run, out_dir)` — writes `guided_pull_results.json`, `guided_pull_report.md`,
  `guided_pull_summary.png`, `pressure_flow.png`, `cup_progress.png`, `extraction_progress.png`, and
  `guided_pull_captions.txt`. Every figure carries an `EXPLORATORY_SIMULATION` badge, direct
  labels with units, grayscale-readable line styles, and a fidelity-ceiling footer. The renderer
  consumes a completed `PullRun` — it never re-simulates or mutates it.

## Usage

- **Package:** `from puckworks.product import load_pull_preset, simulate_pull, render_pull_report`.
- **CLI:** `puckworks-pull presets` · `puckworks-pull run --preset guided_v1 --dose-g 20 --beverage-g 40
  --pressure-bar 9 --grind-setting 1.7 --report-dir build/guided-pull` (add `--domain-policy strict`
  to block product-interval departures). Summary/JSON/Markdown modes need no matplotlib; `--figures` / `--report-dir`
  need the `puckworks[viz]` extra and print an actionable message if it is missing.
- **Colab (released, one-click):** [`notebooks/guided_espresso_pull_colab.ipynb`](../notebooks/guided_espresso_pull_colab.ipynb)
  with native form controls. Its default path downloads the exact v0.3.0 release wheel and verifies
  the SHA-256 before installing; `PUCKWORKS_WHEEL` remains for hermetic (offline) testing.
- **Codespaces (development `0.4.0.dev0`):** the dynamic **Guided Pull Laboratory** UI —
  `streamlit run apps/lab_app.py` (installed via the `webapp` extra). It runs the development
  branch/version, not the released v0.3.0. See [`GUIDED_PULL_LABORATORY.md`](GUIDED_PULL_LABORATORY.md).
- **Actions (batch):** the manually dispatched `guided-pull-batch` workflow builds the current wheel and
  writes deterministic JSON/Markdown/figure artifacts — a reproducible batch runner, not a live UI.

## Runnable-environment matrix

| Path | What | Version |
|---|---|---|
| Colab quickstart / guided pull | released, one-click, browser | v0.3.0 wheel |
| CLI (`puckworks-pull`, `python -m puckworks.product.lab`) | local deterministic | installed package |
| Codespaces + Streamlit (`apps/lab_app.py`) | dynamic development UI | 0.4.0.dev0 (development) |
| Actions `guided-pull-batch` | reproducible batch artifacts | current wheel |
