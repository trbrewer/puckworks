# Reproducing the Puckworks papers

This file states exactly what is needed to regenerate the manuscripts' numbers and figures, what is
guaranteed, and — as importantly — what is **not**.

## What "reproducible" means here

Three different properties get called reproducibility, and this repository keeps them apart because
they fail in different ways.

| Property | What it asserts | How it is checked |
|---|---|---|
| **Determinism** | The same commit and environment produce byte-identical artifacts | `paper3.archive create-archive` twice → identical sha256 |
| **Freshness** | Nothing in the release was hand-edited after it was generated | `paper3.build release` regenerates every artifact and compares |
| **Correctness** | The producers compute the right quantity | **Not** asserted by any of the above; see the caveat below |

The third is the one no build system can supply. A manuscript number can trace perfectly to a
producer that computes the wrong thing, and every provenance check will pass. The defect-injection
benchmark in the Paper 3 manuscript (§10) reports this explicitly as an undetected defect class,
alongside the others the guardrails cannot catch.

## Quick start

```bash
python -m pip install -e ".[dev,figures]"
pytest -q                                        # the quick gates (~13 min full suite)
python -c "from puckworks.registry import run_all_gates; run_all_gates()"
```

## Pinned environment

`docs/reproducibility/requirements-paper3.lock` pins the exact versions that **produced the
committed artifacts**, not merely a set that satisfies the declared floors. The distinction matters:
resolving `pyproject.toml` freshly today gives matplotlib 3.11.1, whereas the committed figures were
drawn with 3.11.0, so a lock generated without constraints would quietly describe a different
environment from the one that ran.

```bash
uv pip sync docs/reproducibility/requirements-paper3.lock
# or
python -m pip install -r docs/reproducibility/requirements-paper3.lock
```

`pyproject.toml` keeps deliberately **unbounded** floors (`numpy>=2.0`, `scipy>=1.13`) because the
library should stay installable alongside other packages. The lock is for reproducing a release; the
floors are for using the library. Do not conflate them.

Recorded producing environment: Python 3.13.13, numpy 2.5.1, scipy 1.18.0, matplotlib 3.11.0.
`python tools/check_release_environment.py` re-reports this at any time.

### Which lock file to use

Three lock artifacts exist and they answer different questions. They are **not** interchangeable,
and the older two predate the Paper 3 lock rather than being superseded by it.

| File | What it is | Installable elsewhere? | Use it for |
|---|---|---|---|
| `requirements-paper-release.lock` | **Direct** pins only (numpy/scipy/matplotlib) | Yes, but resolves transitives freshly | The Papers 1–2 release contract, per `docs/reproducibility/RELEASE_RUNBOOK.md` |
| `docs/reproducibility/requirements-paper3.lock` | **Full transitive** resolution, constrained to the producing environment | Yes — this is the one to `pip install -r` | Reproducing the Paper 3 figures and artifacts |
| `docs/reproducibility/requirements.lock` | `pip freeze` of the producing conda env | **No** — entries are `file:///` build paths | A *record* of what was installed; not a recipe |

The Paper 3 lock is regenerable, which is why the constraints it was compiled against are committed
rather than left in a scratch directory:

```bash
uv pip compile pyproject.toml --extra figures \
    -c docs/reproducibility/constraints-paper3.txt \
    -o docs/reproducibility/requirements-paper3.lock
```

The known gap: `requirements-paper-release.lock` is direct-only by design, so Papers 1–2 do not yet
have a transitive lock of the kind Paper 3 now has. `docs/HANDOFF_EXECUTION_SUMMARY_2026-07-13.md`
already records this as a pre-archival requirement; extending the Paper 3 approach to them is the
obvious closure and has not been done.

## Regenerating each paper

```bash
# Paper 1 (identifiability)
python -m puckworks.figures_paper_a render      # fast: redraw from the committed bundle
python -m puckworks.figures_paper_a compute     # SLOW (~25-30 min of PDE solves)
python -m puckworks.paper_a.build verify        # pins manuscript numbers to the bundle

# Paper 2 (temporal)
python -m puckworks.paper_b.build verify

# Paper 3 (registry/resource)
python -m puckworks.figures_paper3              # figures + source data + alt text
python -m puckworks.paper3.build verify
python -m puckworks.paper3.build release        # strict gate; see below
```

Slow analyses are separated from the quick gates by design and are **not** run in CI; see
`docs/CI_LANES.md`.

## The strict release gate

`python -m puckworks.paper3.build release` fails unless **all** of the following hold:

1. the standard `verify` passes (no stale generated artifacts, valid registry, complete bundle);
2. the working tree is **clean**;
3. every generated artifact **regenerates byte-identically** — the generated evidence artifacts,
   Appendix B, the named-shot scorecard, and every figure source-data CSV;
4. the deterministic archive builds to the **same sha256 twice**.

### Why freshness is defined by recomputation, not by commit equality

An earlier design required `bundle.source_commit == HEAD`. **In-tree** that is unsatisfiable:
committing the bundle advances `HEAD`, so a committed bundle always reads one commit stale.

It is *not* unsatisfiable in general. `tools/prepare_paper_release.py` breaks the cycle by building
outside the source tree — clean checkout, detached worktree at `HEAD`, generated artifacts computed
into an external staging directory, verified there, then overlaid onto `git archive HEAD`. Inside
the resulting archive, source tag commit == `manifest.source_commit` == `bundle.source_commit`. See
`docs/reproducibility/RELEASE_RUNBOOK.md`.

**That tool currently covers Papers 1 and 2 only; Paper 3 is not yet wired into it.** Until it is,
the Paper 3 gate asserts the in-tree property instead: *"nothing here was hand-edited after it was
generated"*, which is exactly what recomputation tests. This mirrors the split between
`generated_from_commit` and `last_verified_against_commit` in the public claim schema — the commit
an artifact was produced at and the commit it was last checked against are different facts and are
recorded separately.

## The archive

```bash
python -m puckworks.paper3.archive create-archive --out dist/paper3_archive.tar.gz
python -m puckworks.paper3.archive verify-archive dist/paper3_archive.tar.gz
```

The archive is byte-deterministic (sorted members, fixed mtime from the commit's committer time,
uid/gid 0, gzip mtime 0) and carries an embedded per-member manifest with path, size, sha256, role
and redistributability. `verify-archive` works **without the source checkout**, which is the point:
a reviewer with only the tarball can confirm every member.

It is fail-closed. It refuses to include private or raw corpus paths, any member lacking a
redistributability classification, obvious secrets, or absolute paths.

The archive is also the single definition of the paper bundle: `paper3.build.bundle_contents()`
delegates to it, with a small floor list asserted so a globbing change cannot silently drop the
manuscript. That unification immediately caught two evidence files the archive had been missing.

## What is NOT yet reproducible

Stated plainly, because a reproducibility document that only lists successes is not useful:

- **No archival DOI.** The current release is GitHub-only (`registry_status: github_only`). Until a
  Zenodo deposit exists, citations point at a moving repository rather than a frozen record.
- **No independent reproduction.** Nobody outside the originating team has rebuilt these artifacts,
  so every claim here is self-attested.
- **Correctness is not certified**, only agreement — see the table at the top and Paper 3 §10.
- **Some data is retrieval-only or rights-blocked** and cannot be redistributed in the archive; the
  manifest records which, and the archive refuses to include them rather than shipping them
  quietly.
- **The corpus is curated, not systematic.** The indexed literature search is a submission gate that
  has not been executed.

## Provenance conventions

- Every manuscript-facing number traces to a named producer; a number with no producer is
  **withdrawn** rather than printed. This is enforced by tests, and it has already removed two
  values that did not trace.
- Evidence relations are recorded per observable (a *scoped* evidence vector), never as one score
  per component, and no ordering over relations exists anywhere in the implementation.
- Source licences and redistribution rights are recorded per dataset in
  `puckworks/data/MANIFEST.csv`; GPL-licensed source code from upstream papers is **not** ingested,
  and reductions are re-implemented from documented method descriptions.
