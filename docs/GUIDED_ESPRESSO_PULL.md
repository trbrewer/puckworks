# Guided Espresso Pull

A rights-independent, runnable **guided mechanism explorer** (issue #48). You enter a bounded recipe
and run one coherent, model-backed espresso pull on CPU, then watch it stage by stage with
evidence-labelled traces, a visual report, and honest domain warnings.

It is **not** an optimizer, a flavor/taste predictor, or a digital twin. It reports chemical
**composition** where supported — never sensory flavor. It ships and loads **no** upstream fixture
data; everything is computed from model code plus your inputs.

Public surface: `puckworks.product` (see [API.md](API.md)). It arrives in **v0.3.0** — the published
v0.2.0 wheel does not contain it.

## Presets

| preset | purpose | editable |
|---|---|---|
| `pv19_named` | fixed reference scenario — deterministic regression + a stage-scorecard example | none (fixed) |
| `guided_v1` | range-limited, user-adjustable guided mode centered on the well-understood region | the active controls below |

```python
from puckworks.product import load_pull_preset, simulate_pull, render_pull_report

recipe, config = load_pull_preset("guided_v1")
run = simulate_pull(recipe, config)          # deterministic; run_id derives from inputs
artifacts = render_pull_report(run, "guided_pull_report")   # JSON + Markdown + figures (needs [viz])
```

## The primary model

The one executed chain is `cameron2020.extraction_bdf`, a coherent, self-contained single-solute BDF
shot model spanning **grind → machine/flow → extraction → cup**. Its evidence strength is
code-verification against the source paper; the guided pull is badged `EXPLORATORY_SIMULATION` and is
**not** independently validated against a measured cup.

Every other registered component is dispositioned in the run's **coverage ledger** with an explicit
`executed` flag — only the primary model is executed. Alternatives are `CALIBRATION_ONLY`,
`AVAILABLE_AS_SEPARATE_LENS` (eligible but **not executed** — their conventions are not verified as a
causal adapter to the primary chain), or excluded. Nothing is blended into a consensus; the report
never claims a comparison it did not run.

## Inputs

### Active controls (each changes the calculation)

| input | evidence range | hard (solver) range | unit |
|---|---|---|---|
| `dose_g` | 15–25 | > 0 | g |
| `target_beverage_g` | 25–60 | > 0 | g |
| `pressure_bar` | 6–9 | > 0 | bar (prescribed constant) |
| `grind_setting` (EK43 dial) | 1.1–2.3 | 1.0–2.5 | dial |
| `coffee_profile` | `reference` only | model-backed selector | — |
| `domain_policy` | `warn` / `strict` | — | — |

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

- **Hard-invalid** inputs (non-positive dose/beverage/pressure, a non-liquid-water temperature, an
  out-of-solver grind, or a rejected unsupported field) are **REJECTED** — the run raises.
- **Evidence-range** departures are **WARNING** under `domain_policy="warn"` (the run completes and
  is flagged an extrapolation) and **block** under `"strict"`.
- Values are **never silently clamped**; the supplied value is preserved everywhere.

## Traces (authoritative, full solver precision)

`run.traces` are typed series copied straight from the solver result (not rebuilt from the rounded
final observables). JSON preserves full solver precision; only display renderers round. Each series
carries a **value role**: `prescribed_input`, `simulated`, or `derived`.

| trace / series | role | unit | derivation |
|---|---|---|---|
| prescribed pressure | prescribed_input | bar | the constant you set — an input, not a prediction |
| model flow | simulated | g/s | `area · q · rho_out`, `q` from `darcy_flux(gs, p_bar)` (constant) |
| cumulative beverage mass | derived | g | integral of the constant model flow; endpoint = target by construction |
| cumulative dissolved mass | simulated | g | model solute reaching the cup (`m_cup`), kg→g |
| cumulative extraction yield | derived | % | `100·(dissolved mass)/dose` |
| outlet concentration | simulated | kg/m³ | modeled outlet liquid concentration (`cl_out`) |
| end-of-shot liquid profile | simulated | kg/m³ vs m | `cl_final` along bed depth at `t_shot` |

## Explicit limitations

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
  to block extrapolations). Summary/JSON/Markdown modes need no matplotlib; `--figures` / `--report-dir`
  need the `puckworks[viz]` extra and print an actionable message if it is missing.
- **Colab (from v0.3.0):** [`notebooks/guided_espresso_pull_colab.ipynb`](../notebooks/guided_espresso_pull_colab.ipynb)
  with native form controls. Until v0.3.0 is released it runs only via a locally built candidate wheel
  (`PUCKWORKS_WHEEL`); the public one-click download-and-verify path activates with the release.
