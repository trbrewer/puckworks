# puckworks

A component **registry** for espresso process models — not a mega-model.
The process is decomposed into stages with typed contracts
(`puckworks/contracts.py`); each published model becomes a component with
provenance, assumptions, validity range, and **validation gates**
(`puckworks/registry.py`). A simulation is a *configuration*: one component per
runtime stage, plus offline calibration chains (LB, constitutive laws) feeding
parameters in.

**New session? Start with [docs/ONBOARDING.md](docs/ONBOARDING.md).**

## Founding components
| stage | component | kind | source |
|---|---|---|---|
| extraction | cameron2020.extraction_bdf | runtime | Matter 2020 |
| bed_dynamics | brewer2026.streamtube (+ Rung B) | runtime | this project |
| infiltration | foster2025.infiltration | runtime | Phys. Fluids 2025 |
| packing | wadsworth2026.permeability | calibration | RSOS 2026 |
| packing | brewer2026.pack_generator | calibration | this project |
| flow | brewer2026.lb_reference / lb_taichi | calibration | this project |

## Quickstart

> **puckworks is not currently published on PyPI.** The canonical v0.2.0 distributions are attached
> to the [v0.2.0 GitHub Release](https://github.com/trbrewer/puckworks/releases/tag/v0.2.0).

### Install the published GitHub release
Download `puckworks-0.2.0-py3-none-any.whl` from the release, then:
```
python -m pip install puckworks-0.2.0-py3-none-any.whl
```
Or, where direct remote-wheel installation is acceptable:
```
python -m pip install \
  "https://github.com/trbrewer/puckworks/releases/download/v0.2.0/puckworks-0.2.0-py3-none-any.whl"
```
Then:
```
python -c "import puckworks; s = puckworks.evaluate_all_gates(); print(s.summary_text())"
python -c "import puckworks; print(len(puckworks.components()), 'components registered')"
```
Supported Python: 3.10–3.13 (3.12 is the primary release interpreter).

The **supported public API** is `puckworks.__all__` (`evaluate_all_gates`, `components`, `get`,
`Component`, `contracts`, `validate`, …) — see [`docs/API.md`](docs/API.md) for the stability
policy. Everything else (`harness`, `analysis`, `paper3`, …) is internal research tooling.

### Contributor / release-builder install
```
python -m pip install -e ".[dev]"
```
Contributors and release builders can build and install locally instead:
`python -m puckworks.release build` (wheel + sdist + checksummed manifest) then
`pip install dist/puckworks-*.whl`; see `CONTRIBUTING.md`. Contributor extras:
`[figures] [harvest] [release] [lb] [viz]`. Test lanes + the card-first contribution process:
`docs/CI_LANES.md`, `CONTRIBUTING.md`, and the doc index `docs/CURRENT.md`.

## Adding a model
1. Write its **model card** from `docs/cards/TEMPLATE.md` (this is where papers
   get interrogated — do it before writing code).
2. Implement under `puckworks/models/<key>/`, consuming/producing contract types.
3. Register in `puckworks/models/__init__.py` with assumptions + validity range.
4. Give it at least one gate wired to real data in `puckworks/data/`.

## Provenance discipline
Every result should be reportable as: component names + versions + gate status.
Reference datasets (Cameron tables, Wadsworth Table 1, DE1 fixtures) live in
`puckworks/data/` with sources documented — the value ceiling of this registry
is set by validation data, not model count.

## Related artifacts
The Colab GPU sweep notebook, the paper build, and PUCK LAB live alongside this
package and consume it; see `notebooks/`.
