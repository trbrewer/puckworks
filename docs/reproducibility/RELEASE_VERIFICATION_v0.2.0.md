# puckworks v0.2.0 — release verification record

**Puckworks v0.2.0 was published as a GitHub-only release and verified from the public download.
It was not published to PyPI or another package registry.**

This is the durable, completed record for the v0.2.0 release. All hashes are full 64-character
SHA-256. The authoritative procedure lives in [`RELEASE_RUNBOOK.md`](RELEASE_RUNBOOK.md).

## 1. Release identity
| field | value |
|---|---|
| release name | puckworks v0.2.0 |
| release URL | https://github.com/trbrewer/puckworks/releases/tag/v0.2.0 |
| published at | 2026-07-17T01:08:00Z |
| annotated tag | `v0.2.0` |
| tag-object hash | `6501d561865a79ad904b970291dfb5c293417b98` |
| peeled source commit | `458ee70bb2eedd79231385fa2d2dad2e1d457aaf` |
| tag moved after publication? | no — tag object and peeled commit unchanged across all post-publication checks |
| package version | 0.2.0 |
| supported Python | 3.10 – 3.13 |
| primary release interpreter | 3.12 |

## 2. Authorization and scope
- Publication was an explicit human action (`gh release edit v0.2.0 --draft=false`), not automated.
- The canonical distributions came from the **tag-triggered** `release.yml` workflow run.
- The local Python 3.13 rehearsal wheel/sdist were **not** published.
- No package-registry publication occurred.

## 3. Workflow provenance
| workflow | event | run ID | run URL | head SHA | conclusion | notes / evidence |
|---|---|---|---|---|---|---|
| release (preflight) | workflow_dispatch | 29543296334 | https://github.com/trbrewer/puckworks/actions/runs/29543296334 | `458ee70` | success | build + clean-room wheel install |
| slow-science (preflight) | workflow_dispatch | 29543297221 | https://github.com/trbrewer/puckworks/actions/runs/29543297221 | `458ee70` | success | gate-report (passed, 51 results), coverage, pip-freeze |
| security (preflight) | workflow_dispatch | 29543298160 | https://github.com/trbrewer/puckworks/actions/runs/29543298160 | `458ee70` | success | pip-audit success; dependency-review **skipped** |
| release (canonical) | push (tag `v0.2.0`) | 29545862493 | https://github.com/trbrewer/puckworks/actions/runs/29545862493 | `458ee70` | success | produced the canonical wheel/sdist/manifest |

`dependency-review` is skipped on `workflow_dispatch` because it is a PR-scoped check (it diffs a
pull request's dependency changes and has no base to diff on a dispatch). The applicable
exact-commit audit is `pip-audit`, which **succeeded**.

## 4. Canonical artifact inventory (manually attached release assets)
Ten intentionally uploaded, checksum-controlled assets. `SHA256SUMS.txt` governs this attached set.

| filename | role | bytes | SHA-256 | source | verified |
|---|---|---|---|---|---|
| `puckworks-0.2.0-py3-none-any.whl` | wheel (canonical) | 992913 | `0a54f8782e4173132308af24ce0c88bb48a2d334071382c07c0ff5ecc9082df1` | tag-run 29545862493 | yes |
| `puckworks-0.2.0.tar.gz` | sdist (canonical) | 999722 | `8b60626328897077ffd1f8de886a086610d808e5fa3a2c829e71a817bf59aaad` | tag-run 29545862493 | yes |
| `release_manifest.json` | build provenance | 627 | `ab7d4d94194eb3232ece5510e9f2b982d4efe835dc86aab7531d909da2cead51` | tag-run 29545862493 | yes |
| `requirements-release.lock.txt` | py3.12 hashed lock | 7557 | `6c342564a5f4bb6e6a1dc6faafb13a23646752555c11a93b9ec963ffbd242888` | local py3.12 (validated) | yes |
| `paper3_archive.tar.gz` | evidence archive | 2267062 | `c7deb85c52338393e750546b365ba040354948d301e1f2df9b8ba663a85936a7` | deterministic build | yes |
| `paper3_archive.tar.gz.sha256` | archive sidecar | 88 | `7fdc40c0ef6f0d404882b5d4c5e22636373914ac1f9787af144e8e90f2f3f8fc` | sidecar | yes |
| `gate_report.json` | authoritative gate report | 30132 | `414cf8cdfb9224af74d8456aeea53cb951d5d2ce391e0ffc31cf34dbde02b936` | slow-science 29543297221 | yes |
| `evidence_report.json` | evidence-graph summary | 1554 | `c322a45631835c165e30ffe71593dcd7d806923adb924caaee11490d2ffa7b4f` | tag-run 29545862493 | yes |
| `release_provenance.json` | provenance record | 3298 | `1a039122fe5cb88da1fb00cd9e4ea984e7355d8406085639db55f9455be422e7` | assembled | yes |
| `SHA256SUMS.txt` | checksums (attached set) | 815 | `7837f1e82eb80686b0efb467d54eca5e7e9a264ec5ca55cf9247f453ea39d9e3` | assembled | yes |

**Asset-count note:** there are **10** intentionally uploaded, checksum-controlled assets. The
GitHub Release page displays **12** entries because GitHub adds two automatically generated
source-code archives (`Source code (zip)` and `Source code (tar.gz)`). Those auto archives are
**not** substitutes for the canonical attached sdist (`puckworks-0.2.0.tar.gz`) or the Paper 3
archive, and are outside the scope of `SHA256SUMS.txt`.

## 5. Distribution verification
- `release_manifest.json`: source commit `458ee70bb2eedd79231385fa2d2dad2e1d457aaf`, `dirty=false`,
  build Python `3.12.13`, platform `Linux-6.17.0-1020-azure-x86_64-with-glibc2.39`,
  `manifest_sha256=7fca84d0a3e7dcbf26161a673c2c7699d49ec5a5e48d0fd034d119abe8e0fd87`.
- Both canonical artifacts match their recorded manifest hashes.
- `twine check`: PASSED for wheel and sdist.
- Path inventory: wheel 226 entries, sdist 324 entries.
- Privacy/allowlist: clean — no private visualizer data (`visualizer/raw`, `normalized_v3`,
  `crawl_*`, `aggregate_stats.csv`), no coverage/cache/notebook/scratchpad/temporary paths.
- Cross-build comparison (canonical tag-run vs. dispatch-run vs. local py3.13 rehearsal): **0
  file-content differences** (226 wheel files, 270 sdist files byte-identical); path inventories
  identical. Archive-container SHA-256 differs across independent builds (timestamps/ordering) — a
  permitted, non-substantive difference. Substantive package/data/metadata content is byte-identical.

## 6. Dependency lock
- Interpreter Python `3.12.13`; pip `26.1.2`; pip-tools `7.5.3`.
- Resolved: `numpy==2.5.1`, `scipy==1.18.0`.
- Full lock SHA-256: `6c342564a5f4bb6e6a1dc6faafb13a23646752555c11a93b9ec963ffbd242888`.
- `pip install --require-hashes -r requirements-release.lock.txt` succeeded in a clean py3.12 venv.
- **Distinct** from `requirements-paper-release.lock` (that file is a ~353-byte direct-dependency
  record; this is the full transitive, hash-enforced release lock, 7557 bytes). It is a versioned
  **public release asset**, not a source-tree file.

## 7. Paper 3 archive
- Full SHA-256: `c7deb85c52338393e750546b365ba040354948d301e1f2df9b8ba663a85936a7`.
- Built **twice** from a clean detached worktree using only the canonical distributions →
  **byte-identical** SHA-256 (deterministic).
- Embedded source commit `458ee70bb2eedd79231385fa2d2dad2e1d457aaf`; generator version `0.2.0`; 74 members.
- Embedded distribution hashes equal the canonical wheel/sdist hashes above.
- `verify-archive`: every member present with recorded sha256. Redistributability/privacy: clean
  (no private paths). Worktree clean before and after creation.

## 8. Gate and evidence result
- 25 registered components.
- 51 total gate results: **50 PASS + 1 ACKNOWLEDGED_EXCEPTION**; suite `passed=true`.
- The one acknowledged exception — `brewer2026.lb_taichi`: its code-verification evidence is a
  0.003% cross-check to `lb_reference` performed in the Colab **notebook rather than CI**. Taichi is
  an optional dependency and the package must import without it. The physics anchor is
  `lb_reference.gate_lb_channel`. This is an expected, documented exception, not a failed gate.

## 9. Public-download verification (after the release became public)
Performed by downloading all assets from the public release into a fresh directory:
- complete filename-set check: identical to the attached set;
- `SHA256SUMS.txt` validation: all OK;
- canonical wheel/sdist hash equality vs. §4: equal;
- `twine check` (wheel + sdist): PASSED;
- Python 3.12 installed-wheel smoke: version `0.2.0`, import from `site-packages`, 25 components,
  gates PASSED (50 PASS + 1 ACKNOWLEDGED_EXCEPTION), `to_dict()` serialization round-trip, bundled
  example (`evaluate_all_gates().summary_text()`), clean uninstall;
- downloaded-sdist rebuild (fresh py3.12) + smoke: 25 components, gates PASSED.

## 10. Registry status
As verified on 2026-07-17, `puckworks` 0.2.0 was **not present on PyPI** (the project page returned
HTTP 404). Registry publication is a separate, explicitly approved operation and may be performed
later; this record does not imply the name will remain unclaimed indefinitely.

## 11. Final disposition
- All R0 and Phase 2–10 release work is complete and verified.
- The remaining repository action is the post-release status and documentation PR that adds this
  record, extends the runbook, corrects installation guidance, and marks `v0.2.0-release` complete.
