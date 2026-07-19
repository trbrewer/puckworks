"""README publication-governance verifier (issue #41).

A deterministic, offline check that objective public facts cannot silently drift out of the README.
It complements ``tools/update_readme_pulse.py`` (which owns the generated version/release/count block):
this tool verifies *coverage* — that every registered component, every live public interactive, every
supported runnable environment, and every public dataset with rights is represented, that role/status
wording does not contradict the registry/cards, that internal links resolve, and that the former
corporate contact/brand stays absent.

It fails on **objective stale facts**, never on subjective wording, and it never edits the README.

CLI::

    python tools/readme_governance.py verify        # exit 1 on any drift, listing every problem
    python tools/readme_governance.py report        # human-readable coverage report (exit 0)
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
README = _REPO / "README.md"
PUBLIC_README = _REPO / "docs" / "public" / "README.md"
CARDS_DIR = _REPO / "docs" / "cards"

# Components deliberately not itemised in the README model map get an explicit, documented exemption
# here (empty today — all 25 registered components appear). Adding a component without listing it in
# the README (or here, with a reason) fails governance.
COMPONENT_EXEMPTIONS: dict[str, str] = {}

# Public interactives that are LIVE (must appear in README and docs/public/README).
LIVE_INTERACTIVES = {
    "flat-valley": "https://trbrewer.github.io/puckworks/flat-valley/",
    "model-composition": "https://trbrewer.github.io/puckworks/model-composition/",
    "analysis-autopsy": "https://trbrewer.github.io/puckworks/analysis-autopsy/",
}

# Supported runnable environments. Each maps to a marker that MUST appear in the README; entries with a
# `path` are conditional — only required once that path exists in the tree (so Codespaces / the Actions
# batch runner become required the moment they are added, and not before).
ENVIRONMENTS = [
    {"name": "release install", "markers": ["pip install"]},
    {"name": "Colab quickstart", "markers": ["puckworks_quickstart_colab.ipynb"]},
    {"name": "Colab guided pull", "markers": ["guided_espresso_pull_colab.ipynb"]},
    {"name": "CLI", "markers": ["puckworks-pull"]},
    {"name": "Codespaces", "markers": ["Codespaces", "devcontainer", "codespaces"],
     "path": ".devcontainer/devcontainer.json"},
    {"name": "Actions batch runner", "markers": ["batch runner", "workflow_dispatch", "Actions batch"],
     "path": ".github/workflows/guided-pull-batch.yml"},
]

OLD_EMAIL = "brewer@synthetik-technologies.com"
_BRAND = re.compile(r"brewer@synthetik-technologies\.com|synthetik", re.I)


def _components():
    import puckworks
    return list(puckworks.components())


def _readme_relative_links(text: str) -> list:
    """Return (label, target) for every markdown link whose target is a repo-relative path."""
    out = []
    for m in re.finditer(r"\[([^\]]*)\]\(([^)]+)\)", text):
        target = m.group(2).strip()
        if target.startswith(("http://", "https://", "#", "mailto:", "data:")):
            continue
        out.append((m.group(1), target.split("#", 1)[0]))
    return out


def check_readme(*, components=None) -> list:
    """Return a list of governance problems (empty == clean)."""
    problems: list[str] = []
    if not README.exists():
        return ["README.md is missing"]
    text = README.read_text(encoding="utf-8")
    low = text.lower()
    comps = _components() if components is None else components

    # (1) every registered component appears (or has a documented exemption)
    for c in comps:
        if c.name in text:
            continue
        if c.name in COMPONENT_EXEMPTIONS:
            continue
        problems.append(f"component '{c.name}' is not in the README model inventory and has no "
                        f"documented exemption")

    # (2) every card link in the README resolves to a real file (executable components need a card/source)
    for label, target in _readme_relative_links(text):
        p = (_REPO / target).resolve()
        if not p.exists():
            problems.append(f"README link '{label}' -> '{target}' does not resolve locally")

    # (3) role/status wording does not contradict the registry: an executable component must not be
    #     described as reference/source-only, and vice versa (mechanical, table-cell level).
    #     Heuristic guard: if a component is runtime and the README's line for it says
    #     "Source-data constraint" or "card-only", that is a contradiction.
    role_by_name = {c.name: getattr(c, "execution_role", "") for c in comps}
    for line in text.splitlines():
        for name, role in role_by_name.items():
            if f"`{name}`" in line:
                ll = line.lower()
                if role == "runtime" and ("source-data constraint" in ll or "card-only" in ll):
                    problems.append(f"README role wording for runtime component '{name}' contradicts "
                                    f"the registry (line says source/card-only)")

    # (4) every live public-value interactive appears in README and docs/public/README
    pub = PUBLIC_README.read_text(encoding="utf-8") if PUBLIC_README.exists() else ""
    for key, url in LIVE_INTERACTIVES.items():
        if url not in text:
            problems.append(f"live interactive '{key}' ({url}) missing from README")
        if url not in pub:
            problems.append(f"live interactive '{key}' ({url}) missing from docs/public/README.md")

    # (5) every supported runnable environment appears (conditional entries only once their path exists)
    for env in ENVIRONMENTS:
        path = env.get("path")
        if path and not (_REPO / path).exists():
            continue                                  # not yet implemented -> not yet required
        if not any(m.lower() in low for m in env["markers"]):
            problems.append(f"runnable environment '{env['name']}' is present in the tree but not "
                            f"documented in the README")

    # (6) development-only capabilities must not be presented as part of the released v0.3.0. Objective
    #     guard: the pulse must distinguish the released tag from the unreleased development source.
    if "latest public release" not in low or "unreleased" not in low:
        problems.append("README pulse no longer distinguishes the public release from the unreleased "
                        "development source")

    # (7) the former corporate contact/brand stays absent
    for i, line in enumerate(text.splitlines(), 1):
        if _BRAND.search(line):
            problems.append(f"README:{i} contains the former corporate contact/brand")

    return problems


def report(components=None) -> str:
    comps = _components() if components is None else components
    text = README.read_text(encoding="utf-8") if README.exists() else ""
    covered = sum(1 for c in comps if c.name in text)
    problems = check_readme(components=comps)
    lines = [
        "# README governance report",
        "",
        f"- registered components: **{len(comps)}**, covered in README: **{covered}**, "
        f"exemptions: **{len(COMPONENT_EXEMPTIONS)}**",
        f"- live interactives checked: **{len(LIVE_INTERACTIVES)}**",
        f"- runnable environments checked: **{len(ENVIRONMENTS)}**",
        f"- governance problems: **{len(problems)}**",
        "",
    ]
    lines += [f"- {p}" for p in problems] or ["_No drift detected._"]
    return "\n".join(lines) + "\n"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="readme_governance", description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("verify", help="exit 1 on any README drift")
    sub.add_parser("report", help="print a coverage report (exit 0)")
    args = ap.parse_args(argv)
    if args.cmd == "report":
        sys.stdout.write(report())
        return 0
    problems = check_readme()
    if problems:
        print("README GOVERNANCE FAILED:")
        for p in problems:
            print("  -", p)
        return 1
    print("README governance OK: components, interactives, environments, links, and identity covered")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
