# CI lanes (R2)

Every test belongs to exactly one **primary lane** (enforced by
`tests/test_ci_lanes.py::test_lanes_partition_every_test`). Markers are registered in
`pyproject.toml` (`[tool.pytest.ini_options].markers`); the slow set is declared once in
`tests/conftest.py` and auto-applied at collection. Offline lanes are **provably** network-free
(an autouse `_block_network` fixture raises on any non-loopback connect unless a test is marked
`live`/`external_data`).

| lane | workflow | trigger | selector | extras | network | duration | artifacts | required |
|---|---|---|---|---|---|---|---|---|
| **quick** | `gates.yml` | push(main) + PR | `-m "not slow and not live and not gpu and not external_data"` | `.[dev]` | blocked | ~15 s | JUnit on fail | **yes** (3.10 + 3.12, `fail-fast: false`) |
| **generated-artifacts** | `generated-artifacts.yml` | push(main) + PR | `paper3.registry_artifacts --verify` + `paper3.build verify` | `.[dev]` | none | ~20 s | — | **yes** |
| **slow-science** | `slow-science.yml` | dispatch + weekly cron | `-m slow` then offline full-suite backstop | `.[dev,figures]` | blocked (offline) | minutes | JUnit + durations + pip-freeze | no |
| **live-contract** | `live-contract.yml` | dispatch + weekly cron | `visualizer_canary` (1 list + 1 detail) | `.[harvest]` | **live**, bounded | seconds | none (no retention) | no; gated on `vars.RUN_LIVE_CANARY` |
| **release** | `release.yml` | tag `v*`/`paper3-v*` + dispatch | full suite + `paper3.build verify` + artifact upload | `.[dev]` | none | minutes | generated + reproducibility | no |

## Markers

- `slow` — science-heavy (>~2 s). Excluded from quick; run by slow-science. Declared in
  `conftest.SLOW`; a policy test forbids stale/renamed entries.
- `live` — hits the live Visualizer API (bounded, secret/var-gated). Manual/scheduled only.
- `external_data` — needs non-redistributable external data. Manual only.
- `gpu` — needs a GPU / taichi. Manual only.

`live`/`gpu`/`external_data` tests **cannot** enter quick CI (excluded by the selector and by
the partition test). Missing credentials/hardware ⇒ explicit skip, never a false pass.

## Owner

CI/release workflows: repository maintainer (see `CODEOWNERS`). Changes to lane selectors or
the slow list must keep `test_ci_lanes.py` green.
