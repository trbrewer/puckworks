# Contributing to puckworks

puckworks is a **component registry for espresso process models**: typed contracts, model/
source cards, and validation gates. Work is card-first and evidence-gated. Start at
[`docs/CURRENT.md`](docs/CURRENT.md).

## Setup

```
python -m venv .venv && . .venv/bin/activate
pip install -e ".[dev]"            # + [figures] for figure tests, [harvest] for the canary,
                                   #   [release] for the release pipeline
pytest -q -m "not slow and not live and not gpu and not external_data"   # the quick lane (~15 s)
```

## Test lanes

See [`docs/CI_LANES.md`](docs/CI_LANES.md). Quick CI is offline (a fixture blocks the network),
runs on Python 3.10 + 3.12, and excludes `slow`/`live`/`gpu`/`external_data`. Mark heavy tests
`@pytest.mark.slow` (add the nodeid to `tests/conftest.py::SLOW`); mark anything hitting the
network `live` or `external_data`.

## The component/card-first process

1. A **model/source card** in `docs/cards/<key>.md` exists first — physics, assumptions,
   validity range, evidence offered. Never implement from memory of a paper.
2. A module under `puckworks/models/<key>/`, registered in `puckworks/models/__init__.py` with
   explicit `execution_role` / `provenance_class` / `evidence_strength`.
3. At least one **gate** wired to real data in `puckworks/data/`.
4. Data lands with a `MANIFEST.csv` row (source, units, uncertainty, license, validation
   strength). Strict SI at contract boundaries.

Never upgrade an author's validation claim. Feasibility-only, exploratory, and blocked states
are valid outcomes and must stay visible.

## Regenerating artifacts

```
python -m puckworks.paper3.registry_artifacts --write     # registry tables / evidence exports
python -m puckworks.paper_a.build verify                  # Paper A claim ↔ manuscript check
python tools/experimental_data_needs.py render            # the campaign table in EXPERIMENTAL_DATA_NEEDS.md
```
`generated-artifacts` CI fails on any stale diff — regenerate and commit.

## Contributing experimental data

Puckworks needs measurements (see [`docs/EXPERIMENTAL_DATA_NEEDS.md`](docs/EXPERIMENTAL_DATA_NEEDS.md)).
The workflow: open an **Experimental data proposal** issue *before* collecting/uploading; confirm the
scientific question, fields + units, rights, and privacy; collect raw data without overwriting or
smoothing it and preserve every replicate + exclusion; deposit large raw data in an external repository
(Zenodo / OSF) with a DOI; submit metadata + a data dictionary + checksums + a licence + calibration +
uncertainty + analysis code + the DOI. Maintainers update `puckworks/data/MANIFEST.csv` **only after
acceptance**, and a gate lands in a *separate* scientific PR. A submission never auto-authorizes a model
or an evidence-label upgrade. No private or unlicensed data may be committed. `campaigns` are validated
by `python tools/experimental_data_needs.py verify`.

## Pull requests

- Branch, open a PR (the template guides you). Keep PRs narrow and reviewable.
- Required checks (`quick-pr` on 3.10 + 3.12, `generated-artifacts`) must pass.
- Changes to registry/contracts, CI/release, data/privacy, or publication artifacts get the
  matching `CODEOWNERS` review.
- Completion claims cite evidence at an exact commit (CI run, artifact, or recorded decision);
  use the state vocabulary — no bare "DONE".

## Releases

`python -m puckworks.release build` builds a wheel + sdist, `twine check`s them, and writes a
checksummed manifest; `release.yml` additionally installs the wheel clean-room. See R4.

## Activation / state-change PRs (process guard, learned from PR #65)

An activation/release/state PR touches a set of files that must land *together*. PR #65 was needed
because an activation commit's `git add` silently omitted `CHANGELOG.md`, leaving a stale claim on
`main`. Before merging any activation/state/release PR:

- write the **expected-file checklist** for the change;
- run `git diff --name-only <base>...HEAD` and confirm it matches (no intended file — CHANGELOG,
  `docs/status/current.json`, generated artifacts — omitted from the commit);
- regenerate generated artifacts (`tools/update_readme_pulse.py --write`, `statusdoc --write`,
  `tools/readme_governance.py verify`) and confirm the tree is **clean** afterwards;
- reconcile CHANGELOG / current-state prose with what actually shipped.

This is a completeness check, **not** a requirement that every PR edit CHANGELOG.

## README publication governance (issue #41)

Objective public facts must not silently drift out of the README. `tools/readme_governance.py verify`
checks that every registered component, every live public interactive, every supported runnable
environment, and every documented dataset is represented, that role/status wording does not contradict
the registry/cards, that internal links resolve, and that the former corporate contact/brand stays
absent. The `readme-governance` workflow runs it read-only on public-surface PRs and posts a monthly
audit note to issue #41.

## Project independence

Puckworks is independently developed and is not affiliated with or sponsored by any employer or
company. The maintainer contact is t_r_brewer@hotmail.com.
