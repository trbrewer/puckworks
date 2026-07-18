<!-- Landing page. The design authority is docs/PUBLIC_EXPERIENCE.md — edit that first.
     The project-pulse block is generated: `python tools/update_readme_pulse.py --write`. -->

<p align="center">
  <img src="docs/assets/readme/hero_image_logo.png"
       alt="Puckworks logo for evidence-first espresso process modeling — a teal espresso cup with gears above the puckworks wordmark and the line 'tested physics for espresso'."
       width="100%">
</p>

# puckworks

**Evidence-first models for what happens inside an espresso puck.**

Turn papers into typed components, challenge them with validation gates, and make their
assumptions, evidence, validity ranges, and model behavior comparable — while preserving what the
data can, and cannot, support.

<p align="center">
  <a href="https://colab.research.google.com/github/trbrewer/puckworks/blob/main/notebooks/puckworks_quickstart_colab.ipynb"><img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open the Puckworks CPU quickstart in Google Colab"></a>
</p>

**Try it now:**
[▶ Run the quickstart in Google Colab](https://colab.research.google.com/github/trbrewer/puckworks/blob/main/notebooks/puckworks_quickstart_colab.ipynb)
 · [⬇ Download the latest public release](https://github.com/trbrewer/puckworks/releases/latest)
 · [🔬 Explore the evidence](docs/public/README.md)
 · [📊 View current project status](docs/planning/STATE_OF_TRUTH.md)
 · [🧭 Learn the architecture](docs/ONBOARDING.md)
 · [🛠 Contribute a model or dataset](CONTRIBUTING.md)

> **New session (human or agent)? Start with [docs/ONBOARDING.md](docs/ONBOARDING.md).**

---

## Why Puckworks exists

Espresso extraction sits at the crossing of packed-bed flow, deformable porous media, wetting,
and dissolution kinetics. The literature is full of models — but they arrive with different
assumptions, different validity ranges, and claims of very different strength, and they are
almost never comparable head-to-head.

Puckworks makes them comparable **without hiding the assumptions**. It is a component
**registry**, not a mega-model: the process is decomposed into stages with typed contracts, and
each published model becomes a component carrying its provenance, assumptions, validity range,
and validation gates. A simulation is a *configuration* of components — never one monolith that
claims to explain everything.

The public value:

- **compare competing explanations** without burying the caveats;
- **retain provenance and evidence strength** at every step;
- **expose validity ranges and failed/null results** instead of hiding them;
- **make uncertainty actionable** through better measurement design;
- **make rigorous espresso-process science reachable** beyond manuscript readers.

## What it does

- **Typed contracts** at every stage boundary (`puckworks/contracts.py`) — strict SI units,
  validated inputs and outputs.
- **A component registry** (`puckworks/registry.py`) — each model registered with source,
  assumptions, and validity range.
- **Validation gates** wired to real reference data — a gate reports **PASS**, **FAIL**, **SKIP**,
  **ERROR**, or **ACKNOWLEDGED_EXCEPTION**; FAIL and ERROR make the suite fail, and zero-gate and
  policy-exception cases are represented explicitly rather than as silent passes.
- **Provenance discipline** — every result is reportable as *component names + versions + gate
  status*.

## How evidence moves through the system

<p align="center">
  <img src="docs/assets/readme/evidence-pipeline.svg"
       alt="How evidence moves through Puckworks: (1) a paper or dataset becomes (2) a model or source card capturing physics, assumptions and validity range; that becomes (3) a typed component with contracts and provenance; which faces (4) validation gates tested against real data, where exceptions are acknowledged not hidden; producing (5) an evidence-aware result labelled measured, derived, fitted, predicted or simulated; leading to (6) the next measurement or a bounded conclusion. Uncertainty feeds back to guide the next experiment."
       width="440">
</p>

Every reported series carries an origin label — **measured · derived · fitted · predicted ·
simulated** — or is marked **unsupported**. Puckworks never upgrades an evidence tag.

## What you can do today

- Install the released wheel and enumerate the registered components.
- Run the full validation-gate suite and see, per gate, PASS versus ACKNOWLEDGED_EXCEPTION.
- Inspect any component's provenance, assumptions, and validity range.
- Serialize a gate result for a reproducible record.

## Project pulse

<!-- puckworks-pulse:start -->

> Auto-generated from tracked repository state by `tools/update_readme_pulse.py` — inventory counts, not scientific claims. Regenerate with `--write`; CI fails if stale.

| Project pulse | |
|---|---|
| Latest public release | [`v0.2.0`](https://github.com/trbrewer/puckworks/releases/tag/v0.2.0) (`puckworks-0.2.0-py3-none-any.whl`; not on PyPI) |
| Development source | `0.3.0.dev0` (unreleased) |
| Registered components | 25 |
| Validation gates | 51 total — 50 PASS, 1 ACKNOWLEDGED_EXCEPTION (passed under the documented gate policy) |
| Active outcome | Deliver a versioned ShotExplanationBundle for one redistributable bundled shot |
| Blocked outcomes | 2 (external sign-off / data) |
| Supported Python | 3.10–3.13 (3.12 primary/release interpreter) |

<!-- puckworks-pulse:end -->

*Development status and the latest public release are shown separately above — do not read the
development source as a released capability.*

## Try it in Colab (no local setup)

The CPU-first [quickstart notebook](notebooks/puckworks_quickstart_colab.ipynb) runs top to
bottom on a normal Colab CPU in a few minutes. It **installs the latest recorded public
release wheel** — not unreleased main-branch code — and walks through the registry, the gates,
and how to read evidence strength honestly.

[▶ Open the quickstart in Google Colab](https://colab.research.google.com/github/trbrewer/puckworks/blob/main/notebooks/puckworks_quickstart_colab.ipynb)

Specialists: the advanced GPU / lattice-Boltzmann notebook remains at
[`notebooks/espresso_lb_colab.ipynb`](notebooks/espresso_lb_colab.ipynb).

**Coming in v0.3.0 — the Guided Espresso Pull.** A rights-independent, runnable *guided mechanism
explorer*: enter a bounded recipe and run one coherent, model-backed pull stage by stage, with
evidence-labelled traces, a visual report, and honest domain warnings (it does not model puck
wetting, physical first drip, a dynamic pressure profile, temperature response, or flavor). It is
**not released yet** — the public one-click Colab workflow activates when v0.3.0 ships. See
[`docs/GUIDED_ESPRESSO_PULL.md`](docs/GUIDED_ESPRESSO_PULL.md) and
[issue #48](https://github.com/trbrewer/puckworks/issues/48).

## Install the public release

> **puckworks is not published on PyPI.** The canonical distributions are attached to the
> [latest GitHub Release](https://github.com/trbrewer/puckworks/releases/latest).

Download `puckworks-<version>-py3-none-any.whl` from the release, then:

```
python -m pip install puckworks-0.2.0-py3-none-any.whl
python -c "import puckworks; s = puckworks.evaluate_all_gates(); print(s.summary_text())"
python -c "import puckworks; print(len(puckworks.components()), 'components registered')"
```

The same pure-Python wheel is smoke-tested on **Windows, macOS, and Linux** under Python 3.12;
interpreter CI additionally exercises Python 3.10, 3.12, and 3.13. Per-platform commands and the
support matrix: [`docs/ACCESSIBILITY.md`](docs/ACCESSIBILITY.md).

The **supported public API** is exactly `puckworks.__all__`; selected commonly-used entry points
from it include `evaluate_all_gates`, `components`, `get`, `Component`, `contracts`, `validate`,
`load_builtin_components`, `GateStatus`, `GateResult`, and `GateSuiteResult`. See
[`docs/API.md`](docs/API.md) for the full surface and stability policy; everything else is internal
research tooling. (The Colab quickstart installs the **v0.2.0** wheel — its API is v0.2.0's
`__all__`, which may differ from the unreleased main branch.)

Contributors / release builders: `python -m pip install -e ".[dev]"`; see
[`CONTRIBUTING.md`](CONTRIBUTING.md).

## Founding components

| stage | component | kind | source |
|---|---|---|---|
| extraction | cameron2020.extraction_bdf | runtime | Matter 2020 |
| bed_dynamics | brewer2026.streamtube (+ Rung B) | runtime | this project |
| infiltration | foster2025.infiltration | runtime | Phys. Fluids 2025 |
| packing | wadsworth2026.permeability | calibration | RSOS 2026 |
| packing | brewer2026.pack_generator | calibration | this project |
| flow | brewer2026.lb_reference / lb_taichi | calibration | this project |

The value ceiling of this registry is set by **validation data, not model count** — reference
datasets live in `puckworks/data/` with their sources documented.

## Choose your path

- **Enthusiast / layperson** → [run the Colab quickstart](notebooks/puckworks_quickstart_colab.ipynb)
  and read *How evidence moves through the system* above.
- **Researcher** → start at [docs/ONBOARDING.md](docs/ONBOARDING.md), then the model cards in
  `docs/cards/` (the source of truth for each model's physics) and
  [current status](docs/planning/STATE_OF_TRUTH.md).
- **Contributor** → [CONTRIBUTING.md](CONTRIBUTING.md) and the card-first process; the public API
  contract is [docs/API.md](docs/API.md).

## Current limits — what Puckworks deliberately does *not* claim

Puckworks is:

- **not** a universal mega-model;
- **not** an automatic channeling detector;
- **not** a flavor predictor;
- **not** a universal recipe optimizer;
- **not** a replacement for controlled experiments;
- **not** a mechanism oracle.

Most extraction agreements in the underlying science are *post-fit reconstruction*, not
independent validation. The registry surfaces conflicting constants and per-lineage inventories
side by side rather than merging them.

## Contribute

1. Write the **model card** from `docs/cards/TEMPLATE.md` (this is where papers get interrogated —
   before any code).
2. Implement under `puckworks/models/<key>/`, consuming and producing contract types.
3. Register in `puckworks/models/__init__.py` with assumptions + validity range.
4. Add at least one gate wired to real data in `puckworks/data/`.

Details: [CONTRIBUTING.md](CONTRIBUTING.md), [docs/API.md](docs/API.md), and the doc index
[docs/CURRENT.md](docs/CURRENT.md).

## Cite and license

Please cite via [`CITATION.cff`](CITATION.cff). Puckworks is released under the
[MIT License](LICENSE).
