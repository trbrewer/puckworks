#!/usr/bin/env python3
"""Semantic scanner for withdrawn assertions on Paper 1 claim surfaces.

Replaces a blanket quote-stripping heuristic that was applied uniformly to Markdown, JSON and
Python. That heuristic was defensible for Markdown prose — where quoting a phrase really does turn
an assertion into a mention — and **catastrophic** everywhere else, because JSON values and Python
string literals live inside quotes. The demonstration that motivated this module:

    {"verdict": "PHYSICAL"}              -> '{ :  }'
    label = "RATE RECALIBRATION ALONE"   -> 'label =  '

so the rules written to catch exactly those two things could never fire. Only one hand-written
semantic test happened to inspect the saturation archive; every other archive and producer was
scanned by a control that had already deleted the content it was meant to read.

This module inspects each file according to what it is:

* **JSON** — parsed; every object key and every string scalar is a candidate assertion, located by
  JSON pointer. Quotes are structure, not quotation.
* **Python** — parsed with `ast` for docstrings and string constants, and with `tokenize` for
  comments. A string literal in a producer is an output label or a docstring: it asserts.
* **Markdown** — fenced code is removed, then the mention-versus-assert rule applies, because prose
  documenting a withdrawn claim must be able to name it.

Anything else is read as plain text and treated like Markdown prose.

Exemptions are explicit records, never filename conventions: `path`, `pattern`, `reason`, and a
`max_occurrences` so that a NEW occurrence beyond the reviewed count still fails.
"""
from __future__ import annotations

import ast
import io
import json
import pathlib
import re
import tokenize
from dataclasses import dataclass

#: Spans that MENTION rather than assert, in prose only.
_PROSE_QUOTED = re.compile(r"\"[^\"\n]*\"|“[^”\n]*”|`[^`\n]*`")

#: Fenced code blocks in Markdown.
_FENCE = re.compile(r"^```.*?^```", re.S | re.M)


@dataclass(frozen=True)
class Finding:
    path: str
    rule: str
    why: str
    location: str
    excerpt: str

    def __str__(self) -> str:
        return "%s [%s] %s — %s :: %s" % (self.path, self.location, self.rule, self.why,
                                          self.excerpt[:90])


# ─────────────────────────────────────────────────────────────────────────────────────────────
# Per-format extraction of the strings a file ASSERTS
# ─────────────────────────────────────────────────────────────────────────────────────────────


def _json_assertions(text: str):
    """(location, string) for every key and string scalar, located by JSON pointer."""
    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:            # a malformed active archive is itself a defect
        yield ("<parse>", "JSON parse error: %s" % exc)
        return

    def walk(node, pointer):
        if isinstance(node, dict):
            for key, value in node.items():
                here = "%s/%s" % (pointer, key)
                yield ("%s (key)" % here, str(key))
                # A composite "key: value" is emitted for scalar members so that a rule may target
                # a FIELD rather than a bare string. Without it, a rule written as
                # `"verdict": "PHYSICAL"` can never match a parsed document — the same class of
                # defect as the quote-stripping bug, one level down, and it was caught only because
                # the adversarial probe was run before the clean result was believed.
                if isinstance(value, (str, int, float, bool)) or value is None:
                    yield ("%s (field)" % here, "%s: %s" % (key, value))
                yield from walk(value, here)
        elif isinstance(node, list):
            for i, value in enumerate(node):
                yield from walk(value, "%s/%d" % (pointer, i))
        elif isinstance(node, str):
            yield (pointer or "/", node)

    yield from walk(data, "")


def _python_assertions(text: str):
    """Docstrings, string constants and comments — everything a producer states in its own voice."""
    try:
        tree = ast.parse(text)
    except SyntaxError as exc:
        yield ("<parse>", "Python syntax error: %s" % exc)
        return

    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            yield ("line %d" % getattr(node, "lineno", 0), node.value)

    try:
        for tok in tokenize.generate_tokens(io.StringIO(text).readline):
            if tok.type == tokenize.COMMENT:
                yield ("line %d (comment)" % tok.start[0], tok.string)
    except (tokenize.TokenError, IndentationError):
        pass                                        # ast already reported anything fatal


def _prose_assertions(text: str):
    """Markdown and plain text: drop fenced code, then treat quoted spans as mentions."""
    body = _FENCE.sub(" ", text)
    for i, line in enumerate(body.splitlines(), 1):
        stripped = _PROSE_QUOTED.sub(" ", line)
        if stripped.strip():
            yield ("line %d" % i, stripped)


def assertions(path: pathlib.Path):
    text = path.read_text(encoding="utf-8")
    suffix = path.suffix.lower()
    if suffix == ".json":
        return _json_assertions(text)
    if suffix == ".py":
        return _python_assertions(text)
    return _prose_assertions(text)


# ─────────────────────────────────────────────────────────────────────────────────────────────
# Scanning
# ─────────────────────────────────────────────────────────────────────────────────────────────


def scan(repo: pathlib.Path, surfaces, rules, exemptions=()) -> list:
    """Findings across `surfaces`, with explicit per-path exemptions applied.

    An exemption caps the number of permitted occurrences, so a reviewed historical quotation stays
    permitted while a NEW occurrence of the same phrase in the same file still fails.
    """
    allowed = {}
    for ex in exemptions or ():
        allowed[(ex["path"], ex["pattern"])] = int(ex.get("max_occurrences", 1))

    findings = []
    for rel in surfaces:
        path = repo / rel
        if not path.exists():
            findings.append(Finding(rel, "<missing>", "declared claim surface does not exist",
                                    "-", ""))
            continue
        items = list(assertions(path))
        for rule in rules:
            pattern, why = rule["pattern"], rule["why"]
            hits = [(loc, txt) for loc, txt in items if re.search(pattern, txt, flags=re.I)]
            budget = allowed.get((rel, pattern), 0)
            for loc, txt in hits[budget:]:
                findings.append(Finding(rel, pattern, why, loc, txt))
    return findings


def discover(repo: pathlib.Path, globs) -> set:
    found = set()
    for pattern in globs:
        for path in repo.glob(pattern):
            if path.is_file():
                found.add(path.relative_to(repo).as_posix())
    return found


def load_manifest(repo: pathlib.Path) -> dict:
    path = repo / "docs" / "paper1_resource" / "PAPER_A_PLAN_MANIFEST_V1.json"
    return json.loads(path.read_text(encoding="utf-8"))


def main(argv=None) -> int:
    import argparse

    repo = pathlib.Path(__file__).resolve().parents[1]
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.parse_args(argv)

    m = load_manifest(repo)
    findings = scan(repo, m["active_claim_surfaces"], m["banned_assertions"],
                    m.get("assertion_exemptions", ()))
    for f in findings:
        print(f)
    print("\n%d finding(s) across %d active surfaces."
          % (len(findings), len(m["active_claim_surfaces"])))
    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
