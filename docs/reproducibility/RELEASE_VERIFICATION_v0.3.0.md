# puckworks v0.3.0 — release verification record

**Puckworks v0.3.0 was published as a GitHub-only release and verified from the public download.
It was not published to PyPI or another package registry.**

This is the durable, completed record for the v0.3.0 release (the Guided Espresso Pull). All hashes
are full 64-character SHA-256. The authoritative procedure lives in [`RELEASE_RUNBOOK.md`](RELEASE_RUNBOOK.md).

## 1. Release identity
| field | value |
|---|---|
| release name | puckworks v0.3.0 — Guided Espresso Pull |
| release URL | https://github.com/trbrewer/puckworks/releases/tag/v0.3.0 |
| published at | 2026-07-18T15:30:04Z |
| annotated tag | `v0.3.0` |
| tag-object hash | `0f2d105d1837a215103c69762f6a03aaf935b50a` |
| peeled source commit | `c5ab770b76ea2fb876c348ca48d802d604c112ca` |
| PR #51 merge commit | `b0144a66070b74313980d3146c4014d484910e50` |
| tag moved after publication? | no — tag object and peeled commit unchanged across all post-publication checks |
| package version | 0.3.0 |
| supported Python | 3.10 – 3.13 |
| primary release interpreter | 3.12 |

The annotated tag peels to the exact approved candidate commit, **not** to the PR merge commit. Main
advanced by the merge commit `b0144a6`, whose tree is identical to the tagged candidate `c5ab770`.

## 2. Authorization and scope
- Publication was an explicit human action (`gh release edit v0.3.0 --draft=false --latest`), not
  automated. It followed an explicit exact-head, exact-artifact maintainer approval naming the
  candidate commit, both filenames, and both SHA-256 hashes.
- The canonical public assets are the **exact maintainer-approved preserved bytes**, built once from a
  clean worktree. They were **not** replaced by any rebuilt file.
- No package-registry publication occurred.

## 3. Prepublication remediation (rejected candidate)
An earlier local candidate build at `b9e7ddfc01a37fb41540c24d2dbab91a0f47ff0d` was **rejected before
tagging or publication** because its package inventory contained three untracked raw CSV members that
were present only in the developer worktree
(`puckworks/data/pocketscience2024/Espresso water flow experiment - {LRR,Sworks High Flow,VST18}.csv`).
Those bytes (rejected wheel SHA-256 `a1da397b439dd0ee7bd008fdb3d3eebd83b2d5d0010f450e66e3a004ba4feacc`,
rejected sdist SHA-256 `a04a611387e8225809f962c53266fdb474ea9f561adce9bf392199edc6be75fc`) were
**never published**. The files were unintended, untracked, outside the reviewed distribution
inventory, and non-reproducible from the rejected candidate commit — this is not a statement that the
source data lacked permission (the repository provenance record states use is permitted with
attribution). Candidate `c5ab770` added a git-tracked package-inventory guard
(`tools/packaging_check.py::check_git_tracked`), was rebuilt from a clean worktree, and produced the
canonical corrected artifacts recorded below.

## 4. Workflow provenance
| workflow | event | run ID | head SHA | conclusion | notes |
|---|---|---|---|---|---|
| release (canonical) | push (tag `v0.3.0`) | 29649817585 | `c5ab770` | success | full offline suite + build + clean-room install |

The tag-triggered `release.yml` run independently rebuilt distributions. Those rebuilt archives are
byte-different from the approved bytes (workflow wheel SHA-256 c87f716200…, workflow sdist SHA-256
dd924f72ad…), which is expected because setuptools archive containers are not byte-reproducible. Their
extracted, git-tracked package contents were confirmed **equivalent** to the tagged candidate and
**leak-free** (the git-tracked inventory guard passed on them). Per the immutable-byte rule, the
rebuilt files were **not** published; the approved preserved bytes remain canonical.

## 5. Canonical artifact inventory (manually attached release assets)
Exactly **2** intentionally uploaded, checksum-controlled assets. GitHub additionally displays two
auto-generated `Source code` archives on the Release page; those are not counted here and are not
substitutes for the attached sdist.

| filename | role | bytes | SHA-256 | verified |
|---|---|---|---|---|
| `puckworks-0.3.0-py3-none-any.whl` | wheel (canonical) | 1036725 | `4a88931fc0bbc069365242fc5e3ef4d226da9225c80384b6d013028e4b7a3ec0` | yes |
| `puckworks-0.3.0.tar.gz` | sdist (canonical) | 1064496 | `dc89d1f40c2e8329ac34b7a474f7b03cb7f17c5c8952f9232a2a2daa3954b1ca` | yes |

## 6. Verification performed
- **Draft download** (bytes fetched back from the draft release): both hashes and sizes matched the
  approved values; `twine check` PASSED; git-tracked inventory guard clean.
- **Public authenticated download** (`gh release download`): wheel `4a88931…` (1,036,725 B), sdist
  `dc89d1f…` (1,064,496 B) — match.
- **Public direct-HTTPS download**: identical hashes and sizes — match.
- **Package-inventory guard** on the public bytes: no private paths, **no untracked files**, all
  required package data present. The three rejected raw CSV paths are **absent**.
- **Clean-room wheel install** (fresh venv, outside the checkout): `puckworks 0.3.0` imported from
  site-packages.
- **Clean-room sdist install** (fresh venv, outside the checkout): `puckworks 0.3.0` from
  site-packages.
- **Reference run** `puckworks-pull run --preset pv19_named --format summary`: EY 14.11%, TDS 7.05%,
  16.95 s, 40 g; first drip reported **unavailable** (not modeled); temperature identified as
  recorded-only.
- **Guided report** `puckworks-pull run --preset guided_v1 --figures`: produced
  `guided_pull_results.json`, `guided_pull_report.md`, `guided_pull_captions.txt`,
  `guided_pull_summary.png`, `pressure_flow.png`, `cup_progress.png`, `extraction_progress.png`.
- **Automated live notebook** (`notebooks/guided_espresso_pull_colab.ipynb`, no `PUCKWORKS_WHEEL`):
  downloaded the exact v0.3.0 wheel, printed Expected == Verified SHA-256 `4a88931…` and installed only
  after the match, imported version 0.3.0 from site-packages, and reached `GUIDED_PULL_COMPLETE` with
  no cell errors. This automated run is **not** a substitute for the human signed-out acceptance.

## 7. Scientific limitations (unchanged, by design)
The guided pull is an `EXPLORATORY_SIMULATION`, code-verified against the source paper, not
independently validated against a measured cup. It does not model physical first drip or puck wetting
(saturated-bed model), does not simulate a dynamic pressure profile (pressure is a prescribed constant
input), has no thermal transient (temperature is recorded-only), reports chemical composition (never
sensory flavor), and never executes or averages a parallel lens into a consensus. Bean label is
metadata only.

## 8. Distribution and registry
- GitHub Release assets only; **not on PyPI** (affirmative HTTP 404 at verification time).
- No private or rights-gated fixture is distributed in the wheel or sdist.
