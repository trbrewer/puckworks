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
```
`generated-artifacts` CI fails on any stale diff — regenerate and commit.

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

## Project independence

Puckworks is independently developed and is not affiliated with or sponsored by any employer or
company. The maintainer contact is t_r_brewer@hotmail.com.
