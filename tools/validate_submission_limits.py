#!/usr/bin/env python3
"""Check the repository's JFE and APS submission text against stated limits."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]


def _section(text: str, heading_prefix: str) -> str:
    match = re.search(
        rf"^## {re.escape(heading_prefix)}[^\n]*\n+(.*?)(?=^## |\Z)",
        text,
        flags=re.MULTILINE | re.DOTALL,
    )
    if not match:
        raise ValueError(f"section not found: {heading_prefix!r}")
    return match.group(1).strip()


def _plain_markdown(text: str) -> str:
    text = re.sub(r"[*_`]", "", text)
    return text.strip()


def jfe_counts(root: Path = ROOT) -> dict[str, Any]:
    package = (root / "docs/submission/PAPER_A_JFE_PACKAGE.md").read_text(
        encoding="utf-8"
    )
    highlights = [
        line.removeprefix("• ").strip()
        for line in (
            root / "docs/submission/PAPER_A_JFE_HIGHLIGHTS.txt"
        ).read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    abstract = _plain_markdown(_section(package, "Abstract"))
    keyword_text = _plain_markdown(_section(package, "Keywords"))
    keywords = [item.strip() for item in keyword_text.split(";") if item.strip()]
    return {
        "abstract_words": len(abstract.split()),
        "keywords": len(keywords),
        "highlight_count": len(highlights),
        "highlight_characters": [len(item) for item in highlights],
    }


def aps_counts(root: Path = ROOT) -> dict[str, Any]:
    abstract_file = (
        root / "docs/submission/PAPER_B_APS_DFD_2026_ABSTRACT.md"
    ).read_text(encoding="utf-8")
    title = _plain_markdown(_section(abstract_file, "Title"))
    body = _plain_markdown(_section(abstract_file, "Abstract body"))
    funding = _plain_markdown(_section(abstract_file, "Funding acknowledgement"))
    return {
        "title_characters": len(title),
        "abstract_body_characters": len(body),
        "funding_characters": len(funding),
        "body_plus_funding_characters": len(body) + len(funding),
    }


def validate(root: Path = ROOT) -> tuple[bool, list[str], dict[str, Any]]:
    jfe = jfe_counts(root)
    aps = aps_counts(root)
    failures: list[str] = []
    if jfe["abstract_words"] > 250:
        failures.append("JFE abstract exceeds 250 words")
    if not 1 <= jfe["keywords"] <= 7:
        failures.append("JFE keyword count must be 1–7")
    if not 3 <= jfe["highlight_count"] <= 5:
        failures.append("JFE highlight count must be 3–5")
    for index, count in enumerate(jfe["highlight_characters"], start=1):
        if count > 85:
            failures.append(f"JFE highlight {index} exceeds 85 characters")
    if aps["title_characters"] > 300:
        failures.append("APS title exceeds 300 characters")
    if aps["body_plus_funding_characters"] > 2000:
        failures.append("APS abstract body plus funding exceeds 2,000 characters")
    return not failures, failures, {"jfe": jfe, "aps_dfd_2026": aps}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args(argv)
    ok, failures, counts = validate(args.root)
    print(json.dumps({"ok": ok, "counts": counts, "failures": failures}, indent=2))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
