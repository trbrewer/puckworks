#!/usr/bin/env python3
"""Generate the README "project pulse" block deterministically from repository-controlled sources.

The block lives between two literal HTML-comment markers in README.md:

    <!-- puckworks-pulse:start -->
    ... generated content ...
    <!-- puckworks-pulse:end -->

Sources (all repository-controlled or public-package behavior — NO network, NO wall clock):

  * development/source version .............. puckworks.__version__ (falls back to pyproject.toml)
  * latest recorded public release .......... docs/status/public_release.json  (explicit tracked source)
  * registered component count .............. puckworks.components()
  * total gate count + outcome summary ...... puckworks.evaluate_all_gates().counts_by_status
  * current active outcome title ............ docs/status/current.json (state == "active")
  * current blocked-outcome count ........... docs/status/current.json (state == "blocked")
  * supported Python range .................. pyproject.toml classifiers

Usage:
    python tools/update_readme_pulse.py --write     # regenerate the block in place
    python tools/update_readme_pulse.py --verify     # exit 1 if the block is stale (CI gate)
    python tools/update_readme_pulse.py --print      # print the freshly generated block only

Design rules (kept honest on purpose):
  * The numbers are inventory counts, NOT scientific claims. No count here is interpreted.
  * Human-authored README prose outside the markers is never touched.
  * No current wall-clock time is inserted; the block is a pure function of tracked state.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
README = REPO_ROOT / "README.md"
CURRENT_JSON = REPO_ROOT / "docs" / "status" / "current.json"
PUBLIC_RELEASE_JSON = REPO_ROOT / "docs" / "status" / "public_release.json"
PYPROJECT = REPO_ROOT / "pyproject.toml"

START = "<!-- puckworks-pulse:start -->"
END = "<!-- puckworks-pulse:end -->"


def _source_version() -> str:
    try:
        import puckworks  # public-package behavior

        return str(puckworks.__version__)
    except Exception:
        m = re.search(r'^version\s*=\s*"([^"]+)"', PYPROJECT.read_text(encoding="utf-8"), re.M)
        return m.group(1) if m else "unknown"


def _python_range() -> str:
    text = PYPROJECT.read_text(encoding="utf-8")
    vers = sorted(set(re.findall(r"Programming Language :: Python :: (3\.\d+)", text)),
                  key=lambda v: tuple(int(p) for p in v.split(".")))
    if not vers:
        return "3.10–3.13"
    return f"{vers[0]}–{vers[-1]} (3.12 primary/release interpreter)"


def _registry_counts() -> tuple[int, dict[str, int], bool]:
    """(component_count, gate_counts_by_status, gate_suite_passed)."""
    import puckworks

    puckworks.load_builtin_components()
    n_components = len(puckworks.components())
    suite = puckworks.evaluate_all_gates()
    counts = {str(getattr(k, "value", k)): int(v) for k, v in suite.counts_by_status.items()}
    return n_components, counts, bool(suite.passed)


def _status_outcomes() -> tuple[str, int]:
    """(active_outcome_title, blocked_outcome_count) from the canonical status source."""
    data = json.loads(CURRENT_JSON.read_text(encoding="utf-8"))
    items = data.get("items", [])
    active = [it for it in items if it.get("state") == "active"]
    blocked = [it for it in items if it.get("state") == "blocked"]
    active_title = active[0]["title"] if active else "(none active)"
    return active_title, len(blocked)


def _public_release() -> dict:
    # Consume the ONE validated release record — fail loudly rather than render stale/invalid facts.
    import release_record

    return release_record.load_validated(PUBLIC_RELEASE_JSON)


def render_block() -> str:
    src_version = _source_version()
    py_range = _python_range()
    n_components, gate_counts, gate_passed = _registry_counts()
    active_title, n_blocked = _status_outcomes()
    rel = _public_release()

    total_gates = sum(gate_counts.values())
    # Deterministic ordering of the outcome summary.
    order = ["PASS", "ACKNOWLEDGED_EXCEPTION", "FAIL", "ERROR", "SKIP"]
    parts = [f"{gate_counts[k]} {k}" for k in order if gate_counts.get(k)]
    outcome_summary = ", ".join(parts) if parts else "no gates"
    suite_word = ("passed under the documented gate policy" if gate_passed
                  else "gate failure present")

    rel_line = (
        f"[`{rel['tag']}`]({rel['release_url']}) "
        f"(`{rel['wheel_filename']}`; not on PyPI)"
    )

    lines = [
        START,
        "",
        "> Auto-generated from tracked repository state by "
        "`tools/update_readme_pulse.py` — inventory counts, not scientific claims. "
        "Regenerate with `--write`; CI fails if stale.",
        "",
        "| Project pulse | |",
        "|---|---|",
        f"| Latest public release | {rel_line} |",
        f"| Development source | `{src_version}` (unreleased) |",
        f"| Registered components | {n_components} |",
        f"| Validation gates | {total_gates} total — {outcome_summary} ({suite_word}) |",
        f"| Active outcome | {active_title} |",
        f"| Blocked outcomes | {n_blocked} (external sign-off / data) |",
        f"| Supported Python | {py_range} |",
        "",
        END,
    ]
    return "\n".join(lines)


def _splice(readme_text: str, block: str) -> str:
    if START not in readme_text or END not in readme_text:
        raise SystemExit(
            f"README is missing the pulse markers {START!r} / {END!r}; add them first."
        )
    pattern = re.compile(re.escape(START) + r".*?" + re.escape(END), re.S)
    return pattern.sub(lambda _m: block, readme_text, count=1)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--write", action="store_true", help="regenerate the block in README.md")
    g.add_argument("--verify", action="store_true", help="exit 1 if the block is stale")
    g.add_argument("--print", dest="do_print", action="store_true", help="print the block only")
    args = ap.parse_args(argv)

    block = render_block()

    if args.do_print:
        print(block)
        return 0

    original = README.read_text(encoding="utf-8")
    updated = _splice(original, block)

    if args.write:
        if updated != original:
            README.write_text(updated, encoding="utf-8")
            print("README pulse block updated.")
        else:
            print("README pulse block already current.")
        return 0

    if args.verify:
        if updated != original:
            print(
                "STALE: README pulse block is out of date. Run "
                "`python tools/update_readme_pulse.py --write` and commit.",
                file=sys.stderr,
            )
            return 1
        print("README pulse block is current.")
        return 0

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
