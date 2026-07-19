# ACCESSIBILITY.md — one-click access and cross-platform support

The authority for the standing accessibility program (issue **#43**). It defines the supported
platforms, the one-click paths, and the review cadence. Support levels here are only claimed once
the corresponding CI lane is green — see §3.

## 1. Accessibility objective

Minimize the distance between discovering Puckworks and obtaining a useful, scientifically honest
result — for programmers and non-programmers, and for keyboard and screen-reader users.

Concretely:

- a **layperson** can get a real result with **zero install** (Colab);
- a **user** can install **one wheel** and have it work identically on Windows, macOS, and Linux;
- **no** access path presents an unreleased or rights-blocked capability as available.

## 2. One-click paths

| Path | Who it is for | Cost to start |
|---|---|---|
| [CPU Colab quickstart](../notebooks/puckworks_quickstart_colab.ipynb) | laypeople, first look | none — runs in the browser |
| [Guided Pull **Laboratory** Colab](../notebooks/guided_pull_laboratory_colab.ipynb) | laypeople who want to run a shot | none — a form + one **▶ Run** button, no terminal |
| Release wheel install | users, scripting | one `pip install` of the release wheel |
| Advanced GPU / LB notebook (`../notebooks/espresso_lb_colab.ipynb`) | specialists | GPU runtime |

The quickstart is CPU-first, needs no secret and no private data, and installs the **released
wheel** — not unreleased development code.

The **Guided Pull Laboratory** Colab is the layperson path for *running a bounded shot*: fill a short
form, press one **▶ Run the Laboratory** button — no Python, shell, `pip`, or CLI to type. It runs
**privately** in the user's own Colab runtime (execution context `LOCAL_PRIVATE`); "private" means the
model runs in a runtime the user controls and does **not** mean it is cleared for public hosting. Because
the Laboratory ships in the unreleased `0.4.0.dev0`, this notebook installs an **exact commit-pinned
DEVELOPMENT PREVIEW** (option B below), never mutable `main` and never under a "v0.3.0 release" badge. It
is not a digital twin, optimizer, or taste predictor; component self-checks are each a model's *own*
reference case, not a prediction of the chosen shot. `grudeva2025.reduced` is rights-blocked and never
runs (#73).

## 3. Core platform-support matrix

The core package ships as **one pure-Python wheel** (`puckworks-<version>-py3-none-any.whl`).
There are **no** separate Windows/macOS/Linux downloads — the same artifact runs everywhere. This
is verified by portability testing, not by building a different wheel per OS.

**Verified by:** the [`platform-smoke`](../.github/workflows/platform-smoke.yml) workflow builds
**one** wheel and installs *that exact artifact* on `ubuntu-latest`, `windows-latest`, and
`macos-latest` (Python 3.12), then imports from site-packages, enumerates components, runs the
public gate evaluation, serializes/reloads a public result, runs the public-API tests, and
uninstalls cleanly.

| Platform | Core wheel | How verified |
|---|---|---|
| Linux (`ubuntu-latest`) | ✅ tested | `platform-smoke` job on every qualifying PR + release tag |
| Windows (`windows-latest`) | ✅ tested | `platform-smoke` job on every qualifying PR + release tag |
| macOS (`macos-latest`) | ✅ tested | `platform-smoke` job on every qualifying PR + release tag |

> A row is only marked **tested** when the `platform-smoke` workflow is green for the current
> package version. Until that job passes on a change, treat the claim as *pending* — do not assert
> platform support ahead of a passing test. (During authoring, the macOS path was also smoked
> locally on arm64 / Python 3.13.)

## 4. Python version support

Declared support: **3.10 – 3.13**, per `pyproject.toml` (3.12 is the primary/release interpreter).
**Interpreter CI** (`quick-pr`) exercises **3.10, 3.12, and 3.13**; 3.11 is declared but not in the
CI matrix. The cross-OS `platform-smoke` matrix runs under Python **3.12** only — it proves *artifact
portability across operating systems*, distinct from *interpreter-version coverage*. Floors
(`numpy>=2.0`, `scipy>=1.13`) are proven on Python 3.10 by the `min-deps` lane.

## 5. Optional-extra support

The **core** support level above applies to installing the downloaded core wheel (numpy + scipy
only) — puckworks is **not on PyPI**, so it cannot be installed from an index by name; install the
release wheel per §7. Optional extras are **not** guaranteed the same cross-platform level unless
separately tested:

| Extra | Adds | Platform note |
|---|---|---|
| `figures` | matplotlib | pure-Python plotting; broadly portable |
| `harvest` | requests | networking helper; not exercised by the core smoke |
| `lb` | taichi | **GPU/JIT**; not part of core platform verification |
| `viz` | matplotlib, pillow, imageio | raster/video output; broadly portable |
| `viz3d` | pyvista, vtk | **native VTK**; platform-dependent, not core-verified |

Do not read the core matrix as covering GPU (`taichi`), 3-D (`pyvista`/`vtk`), or any extra —
those carry their own, weaker guarantees.

## 6. Colab

- The [quickstart](../notebooks/puckworks_quickstart_colab.ipynb) is the primary layperson *first-look*
  path (registry tour). It installs the release wheel.
- The [Guided Pull Laboratory](../notebooks/guided_pull_laboratory_colab.ipynb) is the layperson
  *run-a-shot* path: a form + one **▶ Run** button, `LOCAL_PRIVATE` execution through the shared
  rights-safe service (`puckworks.product.lab_service`). Three experience modes map to explicit bounded
  requests — *Guided shot only* (primary lens, no references), *Guided shot + component self-checks*
  (primary lens + interactive-fast references), *Catalog only* (the producer-free Explorer — runs
  nothing). It installs a **commit-pinned DEVELOPMENT PREVIEW** (`0.4.0.dev0`), not a released wheel; the
  `notebook-smoke` `laboratory-hermetic` job builds the current dev wheel, installs it via
  `PUCKWORKS_WHEEL`, executes the notebook with no network, and asserts the `GUIDED_PULL_LAB_COMPLETE`
  marker. It carries no committed outputs and requests no secret or upload.
- The advanced GPU/LB notebook (`../notebooks/espresso_lb_colab.ipynb`) is retained for specialists
  and is unchanged.

> **Human acceptance (pending, #43):** before the Laboratory Colab is called usable, a human must open
> it from the badge, *not* open a terminal, change one form value, press the single run control, see the
> evidence-range message + results + caveats + downloads, and confirm no Puckworks upload or secret is
> requested. Not yet performed.

## 7. Local installation

Copy-paste, per platform. puckworks is **not on PyPI** — download
`puckworks-<version>-py3-none-any.whl` from the
[latest release](https://github.com/trbrewer/puckworks/releases/latest) first.

**Windows (PowerShell)**
```
py -m pip install .\puckworks-0.2.0-py3-none-any.whl
py -c "import puckworks; print(len(puckworks.components()), 'components')"
```

**macOS (Terminal)**
```
python3 -m pip install ./puckworks-0.2.0-py3-none-any.whl
python3 -c "import puckworks; print(len(puckworks.components()), 'components')"
```

**Linux (shell)**
```
python3 -m pip install ./puckworks-0.2.0-py3-none-any.whl
python3 -c "import puckworks; print(len(puckworks.components()), 'components')"
```

**Google Colab**
```
!pip install https://github.com/trbrewer/puckworks/releases/download/v0.2.0/puckworks-0.2.0-py3-none-any.whl
```

No OS-specific release archives are published — there is no platform-specific payload to justify
them.

## 8. Contributor cloud environments

- **GitHub Codespaces** — evaluated as a contributor/workshop path (dev container reproducing
  `pip install -e ".[dev]"`). Not yet built; recorded for later.
- Contributors today use a local editable install; see [`../CONTRIBUTING.md`](../CONTRIBUTING.md).

## 9. Static web and native-app roadmap

Recorded so nothing is built speculatively:

- **GitHub Pages / static showcase** — after a stable, human-readable product result exists.
- **JupyterLite / Pyodide** — browser-only feasibility, after dependency compatibility is tested
  (numpy/scipy under Pyodide).
- **Binder or equivalent** — secondary notebook route, only if startup reliability justifies the
  maintenance.
- **Native desktop app** (PyInstaller · Briefcase · signed wrapper · local web bundle) — evaluate
  **only after** a stable end-user workflow, stable inputs/outputs, a user-facing interface, an
  update/security policy, and accepted code-signing/notarization responsibilities. **No installer
  is produced now.**

## 10. Release acceptance checklist

Before a release is considered accessible (issue #43):

- [ ] `platform-smoke` green on Ubuntu, Windows, macOS (Python 3.12);
- [ ] the release wheel is `py3-none-any` (one artifact, all platforms);
- [ ] the Colab quickstart runs CPU-only within its time bound, installing the **released** wheel;
- [ ] the advanced GPU notebook still runs for specialists;
- [ ] per-platform install commands in §7 match the release filename;
- [ ] optional-extra caveats (§5) are accurate;
- [ ] no OS-specific archive was invented.

## 11. Recurring review cadence

Review this document and the access surface (issue #43):

- at every release;
- quarterly;
- after any dependency-floor change;
- after any public-API change;
- after any Colab platform change;
- after any Windows/macOS/Linux CI regression;
- when a new user workflow becomes stable.

A review is complete only when a human records date, reviewer, checks performed, changes made (or
a no-change rationale), and the next review trigger — appended to issue #43. A scheduled reminder
is not evidence a review happened.
