# Colab preflight — four top README notebooks (2026-07-21)

**This is an automated preflight, NOT signed-out acceptance.** It records the checks
that can be verified from source and by hermetic offline execution. The rows marked
`BROWSER PENDING` and `MAINTAINER APPROVAL PENDING` require a real signed-out browser
run and maintainer sign-off; they are tracked in **#48** (guided-pull acceptance) and
**#43** (standing accessibility program), which both stay **open**.

Status vocabulary: `AUTOMATED PASS` · `AUTOMATED FAIL` · `BROWSER PENDING` ·
`BROWSER PASS` · `MAINTAINER APPROVAL PENDING` · `MAINTAINER APPROVED`.

- **Tree tested:** branch `product/colab-explicit-downloads-c31c81b` @ `d3af797`
  (parent `c31c81b`, the current `origin/main`).
- **Baseline defect at `c31c81b`:** the Full Laboratory Tour and Guided Espresso Pull
  notebooks called `google.colab.files.download()` during normal notebook flow, so
  "Run all" triggered browser download prompts — recorded below as `AUTOMATED FAIL`
  at `c31c81b`, `AUTOMATED PASS` on this branch after the explicit-FileLink fix.
- **Automated commands used** (repeatable):
  - contract tests — `pytest -q tests/test_lab_colab_notebook.py tests/test_pull_notebook.py tests/test_linked_pull_notebook.py tests/test_readme.py` → 105 passed
  - gates — `python -c "from puckworks.registry import run_all_gates; run_all_gates()"` → `PASSED (PASS=50, ACKNOWLEDGED_EXCEPTION=1)`
  - hermetic execution — build the current dev wheel, `PUCKWORKS_WHEEL=<wheel> jupyter nbconvert --to notebook --execute` outside the checkout, then `.github/scripts/check_notebook_marker.py` for the marker. Both changed notebooks: marker present, no cell errors, all report files written, no browser download in headless.
  - pin reachability — `git merge-base --is-ancestor <pin> origin/main`
  - imports-at-pin — `git cat-file -e <pin>:puckworks/product/<module>.py` for every imported module

## Notebooks

| # | README label | notebook | install source | pin / release | recorded hash | completion marker |
|---|---|---|---|---|---|---|
| 1 | Full Laboratory Tour | `guided_pull_laboratory_colab.ipynb` | git+ pinned dev preview (`0.4.0.dev0`) | `97015d0f51af6c8a3fd5ebeb21f90a6ae57af1e1` | n/a (source pin) | `GUIDED_PULL_LAB_COMPLETE` |
| 2 | Espresso Model Relay | `illustrative_linked_pull_colab.ipynb` | git+ pinned dev preview (`0.4.0.dev0`) | `851c735c2ba3dc9ccba00b4db8d7ad7758625ddc` | n/a (source pin) | `LINKED_PULL_RELAY_COMPLETE` |
| 3 | Guided Espresso Pull | `guided_espresso_pull_colab.ipynb` | released wheel | `v0.3.0` | `4a88931fc0bbc069365242fc5e3ef4d226da9225c80384b6d013028e4b7a3ec0` | `GUIDED_PULL_COMPLETE` |
| 4 | Quickstart | `puckworks_quickstart_colab.ipynb` | released wheel + SHA-256 verify | `v0.3.0` | `4a88931fc0bbc069365242fc5e3ef4d226da9225c80384b6d013028e4b7a3ec0` | `QUICKSTART_COMPLETE` |

## Evidence grid

| Check | Tour | Relay | Guided Pull | Quickstart |
|---|---|---|---|---|
| README links the notebook | AUTOMATED PASS | AUTOMATED PASS | AUTOMATED PASS | AUTOMATED PASS |
| Completion marker present in source | AUTOMATED PASS | AUTOMATED PASS | AUTOMATED PASS | AUTOMATED PASS |
| Completion marker on hermetic offline run | AUTOMATED PASS | (not re-run here) | AUTOMATED PASS | (release-wheel lane) |
| Pin reachable from main | AUTOMATED PASS | AUTOMATED PASS | n/a (release) | n/a (release) |
| Every imported module exists at pin | AUTOMATED PASS (8 `lab_*`) | AUTOMATED PASS (2) | n/a | n/a |
| No committed cell outputs / execution_count | AUTOMATED PASS | AUTOMATED PASS | AUTOMATED PASS | AUTOMATED PASS |
| Scope / limitations language present | AUTOMATED PASS | AUTOMATED PASS | AUTOMATED PASS | AUTOMATED PASS |
| No private / rights-blocked data exposed | AUTOMATED PASS (grudeva blocked, #73) | AUTOMATED PASS (grudeva blocked) | AUTOMATED PASS | AUTOMATED PASS |
| Automatic-download policy @ `c31c81b` | AUTOMATED FAIL — direct `files.download()` | AUTOMATED PASS — FileLink | AUTOMATED FAIL — `files.download()` loop | AUTOMATED PASS — no report download |
| Automatic-download policy @ `d3af797` | AUTOMATED PASS — FileLink | AUTOMATED PASS — FileLink | AUTOMATED PASS — FileLink | AUTOMATED PASS — no report download |
| README link opens signed-out | BROWSER PENDING | BROWSER PENDING | BROWSER PENDING | BROWSER PENDING |
| Fresh runtime installs cleanly (no stale-pin / hash / ImportError) | BROWSER PENDING | BROWSER PENDING | BROWSER PENDING | BROWSER PENDING |
| Scope warning renders visibly after ▶ Run | BROWSER PENDING | BROWSER PENDING | BROWSER PENDING | BROWSER PENDING |
| No download prompt during "Run all" | BROWSER PENDING | BROWSER PENDING | BROWSER PENDING | BROWSER PENDING |
| Exports offered as explicit click links | BROWSER PENDING | BROWSER PENDING | BROWSER PENDING | BROWSER PENDING |
| Maintainer approval at tested SHA | MAINTAINER APPROVAL PENDING | MAINTAINER APPROVAL PENDING | MAINTAINER APPROVAL PENDING | MAINTAINER APPROVAL PENDING |

## What remains before #48 can advance

A human must, in a genuinely signed-out browser, for each notebook: open it from the
exact README link; open a fresh Colab runtime; Run all; confirm install completes
without stale-pin/hash/import errors; confirm the scope warning renders; confirm the
completion marker appears; confirm **no download prompt fires during Run all**; click
each offered export link and confirm the file downloads only then; confirm no
unexpected auth prompt and no rights-blocked data. Record exact main SHA, notebook URL,
browser/version, date/time, runtime type, and per-row result on **#48**, then obtain
maintainer approval for that SHA. Only then may the `BROWSER PENDING` /
`MAINTAINER APPROVAL PENDING` rows change. After the notebook-UX PR merges, rerun this
automated grid at the new exact `main` SHA and post the amended result to #48.
