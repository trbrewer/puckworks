# PUBLIC_EXPERIENCE.md — the design and review guide behind README.md

This is the durable authority for the Puckworks public homepage. `README.md` is the
*rendering*; this document is the *contract*. When the two disagree, this file wins and the
README is corrected. It is the reference for the standing public-experience program
(issue **#41**) and the accessibility program (issue **#43**).

This is a **standing** guide. It is never "done": every public release, public-API change, and
new runnable surface is a trigger to re-read §10 and revise.

---

## 1. Audience

The homepage serves four readers at once, in this priority order:

1. **The curious layperson** — an espresso enthusiast who found the repo and wants to know, in
   under 30 seconds, what it is and whether they can try it without installing anything.
2. **The researcher** — a scientist or engineer who wants to inspect provenance, validity
   ranges, and exactly how strong each claim is before trusting a number.
3. **The contributor** — someone who could add a model card, a dataset, or a component and needs
   to see the card-first process and the contribution path.
4. **The evaluator** — a reviewer, editor, or collaborator deciding whether the project is
   serious and honest.

No single reader is sacrificed for another: the layperson gets a one-click demo *and* the
researcher gets the evidence discipline, on the same page, in a deliberate reading order.

## 2. Project objective

> **Puckworks turns espresso-process research into composable, auditable components, tests those
> components against evidence, and communicates both what the measurements support and what they
> cannot establish.**

It is a **component registry**, not a mega-model. The process is decomposed into stages with
typed contracts; each published model becomes a component carrying provenance, assumptions, a
validity range, and validation gates. A simulation is a *configuration* of components — never one
monolith that claims to explain everything.

## 3. Public value

Puckworks exists to:

- **compare competing scientific explanations without hiding assumptions;**
- **retain provenance and evidence strength** at every step;
- **expose validity ranges and failed/null results** rather than burying them;
- **make uncertainty actionable through better measurement design;**
- **make rigorous espresso-process science accessible beyond manuscript readers.**

The public value is not "a better shot." It is a trustworthy, inspectable account of what is
actually known — and what is not.

## 4. Evidence and claim discipline

The homepage inherits the project's evidence-strength vocabulary and must never soften it.

- Every reported series carries an origin label: **measured · derived · fitted · predicted ·
  simulated**, plus **unsupported** for anything the release cannot establish.
- A validation gate reports one of the `GateStatus` values: **PASS**, **FAIL**, **SKIP**,
  **ERROR**, or **ACKNOWLEDGED_EXCEPTION**. Semantics (authoritative — the README and the homepage
  must match this):
  - **FAIL** and **ERROR** are **suite-failing** (a mandatory gate that FAILs or ERRORs makes the
    suite not pass); they are never presented as passes.
  - **SKIP** is permitted only when a gate is inapplicable in the current configuration (e.g. an
    optional dependency such as GPU/Taichi is absent); a SKIP is never counted as a PASS.
  - **ACKNOWLEDGED_EXCEPTION** is a *documented, maintainer-recorded* deviation with a recorded
    rationale; it is reported **separately** and **never** silently presented as a PASS, and it
    does **not** satisfy a mandatory gate in place of a real PASS.
  A gate outcome is never softened or narrowed; zero-gate and policy-exception cases are represented
  explicitly.
- Most extraction agreements in the science are *post-fit reconstruction*, not independent
  validation. The homepage never upgrades a tag.
- The README states what Puckworks **deliberately refuses to claim** (see the non-claims below),
  as prominently as what it does.

### Explicit non-claims (must appear on the homepage)

Puckworks is:

- **not a universal mega-model;**
- **not an automatic channeling detector;**
- **not a flavor predictor;**
- **not a universal recipe optimizer;**
- **not a replacement for controlled experiments;**
- **not a mechanism oracle.**

## 5. Homepage content architecture

The README follows this reading order (the layperson value is above the contributor detail):

1. Hero (wordmark + one-line mission)
2. One-sentence mission
3. Primary calls to action
4. Why Puckworks exists
5. What it does
6. How evidence moves through the system
7. What users can do today
8. Try it in Colab
9. Install the public release
10. Project pulse (generated)
11. Scientific stories / hooks
12. Audience paths (layperson · researcher · contributor)
13. Current limits (the non-claims)
14. Contribute
15. Cite and license

Objective, value, and process appear **before** deep contributor detail. The README stays a
landing page — it links out to `docs/` rather than absorbing the whole documentation site.

## 6. Visual language

- **Wordmark:** lowercase `puckworks`, system sans-serif, heavy weight.
- **Motif:** an espresso puck cross-section with stacked layers (the process decomposed into
  typed stages) and a downward flow arrow (pressure-driven infiltration).
- **Palette:** ink `#1a1f24`, teal accent `#0e7490` (light) / `#38bdf8` (dark), amber puck
  `#c98a3a`, a single restrained green `#3f7d3a` for the "bounded conclusion" terminus.
- **Assets** live locally and versioned under `docs/assets/readme/` — light + dark hero, the
  evidence pipeline, and a 1280×640 social preview. Source SVG stays reviewable; no embedded
  fonts (system stacks only); no huge binaries.
- **Restraint:** distinctive without a badge wall. At most a couple of status signals, never a
  wall of shields.

## 7. Accessibility requirements

Binding on every homepage visual and on `docs/ACCESSIBILITY.md`:

- meaningful, descriptive **alt text** on every image;
- **dark- and light-mode** support (theme-matched `<picture>` for the hero; self-contained light
  card for the diagram so it stays legible on any theme);
- **accessible contrast** for text and essential marks;
- **no information conveyed by color alone** — pipeline stages are numbered and labelled, gate
  outcomes are named in words;
- **no auto-playing animation** required to understand the page; any animation has a static
  equivalent;
- **mobile-readable** — relative sizing, a vertically-stacked pipeline diagram, no fixed-width
  layouts;
- **minimal dependence on third-party dynamic widgets** — prefer local assets and generated,
  committed content over live shields.

## 8. Dynamic/generated content policy

The **project-pulse** block is generated by `tools/update_readme_pulse.py` between the markers
`<!-- puckworks-pulse:start -->` and `<!-- puckworks-pulse:end -->`.

- It reads **only repository-controlled sources and public-package behavior**: the installed
  package (`puckworks.components()`, `evaluate_all_gates()`), `docs/status/current.json`,
  `docs/status/public_release.json`, and `pyproject.toml`.
- It makes **no network call in CI**, invokes **no live web service**, and inserts **no wall-clock
  time**.
- It **never** derives a scientific claim from the counts — they are inventory numbers.
- It **never** overwrites human-authored sections; it edits only between its markers.
- `--verify` fails CI when the block is stale; `--write` regenerates it.
- The **latest public release** is read from an explicit tracked source
  (`docs/status/public_release.json`), never guessed from the development version.

## 9. Release-versus-development wording

The homepage always distinguishes:

- **Latest public release** — the tagged GitHub Release, whose facts come from
  `docs/status/public_release.json` (the pulse block renders it; do not hard-code a version here).
  puckworks is **not on PyPI**; the canonical distribution is the release wheel.
- **Development source** — the live source version from `puckworks.__version__` / `pyproject.toml`
  (tracked in `docs/status/current.json`), clearly marked *unreleased*. These two facts change every
  release; reference the generated pulse and the status files rather than a literal version string, so
  this contract does not go stale.

No unreleased or rights-blocked capability may be presented as available. The Colab notebooks install
the **released** wheel, not main-branch source, and say so.

**Public runnable surfaces** (each subject to §4 evidence discipline, §6 visual language, and §7
accessibility): the registry quickstart Colab, the Guided Espresso Pull Colab, and — from the v0.4.0
line — the static **"The Cup Hides the Clock"** flat-valley interactive under `docs/public/site/`.
The interactive is a generated, framework-free HTML/CSS/JavaScript artifact built from the committed,
hash-bound Paper A result bundle: every number traces to a named producer or bundle field; it carries
evidence badges, a static text + image equivalent, meaningful alt text, keyboard operation, no
color-only semantics, and only local/versioned assets (no CDN, network, or tracking); and it amplifies
no claim beyond the generated evidence.

## 10. Monthly and release review checklist

Run this at every release, every public-API change, every new runnable surface, and at least
once a calendar month (issue #41):

- [ ] objective / value / process visible immediately (above the fold reading order);
- [ ] current release link resolves;
- [ ] one-click Colab demo opens the intended notebook and runs CPU-only;
- [ ] install commands are truthful (no PyPI claim; wheel path correct);
- [ ] project-pulse values regenerate clean (`--verify` passes);
- [ ] hero renders in both dark and light mode; diagram legible on both;
- [ ] every image has useful alt text;
- [ ] no stale public-API name (checked against `puckworks.__all__`);
- [ ] no stale component / gate / status number;
- [ ] no unsupported scientific claim; the non-claims are present;
- [ ] all important links resolve;
- [ ] README stays focused (below the documented size ceiling), not the whole doc site.

A review is only complete when a human records: date, reviewer, checks performed, changes made
(or a no-change rationale), and the next review trigger — appended to issue #41. A posted
reminder is **not** evidence a review happened.

## 11. Success measures

- A newcomer can state what Puckworks is, and whether they can try it, within ~30 seconds.
- The one-click Colab path completes on a normal CPU runtime in ≤ ~5 minutes.
- The evidence discipline (origin labels, gate outcomes, non-claims) is visible without scrolling
  into contributor detail.
- No support question reduces to "the README told me something that isn't true / isn't released."
- The same core wheel installs and smokes clean on Windows, macOS, and Linux.

## 12. Deferred website and native-application options

Recorded here so they are not rebuilt speculatively (see `docs/ACCESSIBILITY.md` for the full
policy):

- **GitHub Pages / static showcase** — evaluate only after a stable, human-readable product
  result exists.
- **JupyterLite / Pyodide** — browser-only feasibility, after dependency compatibility is tested.
- **Binder or equivalent** — secondary notebook route, only if startup reliability justifies it.
- **Native desktop app (PyInstaller / Briefcase / signed wrapper / local web bundle)** — evaluate
  only after a stable end-user workflow, stable I/O, a user-facing interface, an update/security
  policy, and code-signing/notarization responsibilities are all accepted. Not in scope now.

## 13. Standing cadences (all programs)

The durable review rhythm across the standing programs (issues #41, #42, #43). A scheduled
reminder is **not** evidence a review happened — a review is complete only when a human records
date, reviewer, checks performed, changes made (or a no-change rationale), and the next trigger.

| Program | Cadence |
|---|---|
| Public homepage (#41) | monthly + every release + every public-API change |
| Accessibility (#43) | quarterly + every release + every platform/dependency change |
| Literature metadata (#42) | weekly (automated discovery) |
| Venue / deadline verification (#42) | monthly, and immediately before any submission |
| Search-query review (#42) | quarterly |
| Public-demo / platform exploration (#43) | quarterly |
| Native-installer feasibility | only after stable end-user-workflow milestones |
| GitHub Pages / static showcase | only after the first stable human-readable product result |
