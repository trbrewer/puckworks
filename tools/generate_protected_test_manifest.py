"""Generate static opaque IDs for source-defined protected target tests."""
from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "tests/protected_target_test_manifest.json"


def build() -> dict:
    selectors = []
    for path in sorted((ROOT / "tests").glob("test_*.py")):
        source = path.read_text(encoding="utf-8")
        if "protected_target_integrity" not in source:
            continue
        tree = ast.parse(source)
        module_marked = any(
            isinstance(node, ast.Assign)
            and any(isinstance(target, ast.Name) and target.id == "pytestmark" for target in node.targets)
            and isinstance(node.value, ast.Attribute)
            and node.value.attr == "protected_target_integrity"
            for node in tree.body
        )
        for node in tree.body:
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) or not node.name.startswith("test_"):
                continue
            individually_marked = any(
                isinstance(decorator, ast.Attribute) and decorator.attr == "protected_target_integrity"
                for decorator in node.decorator_list
            )
            if module_marked or individually_marked:
                selectors.append((path.relative_to(ROOT).as_posix(), node.lineno, node.name))
    selectors.sort()
    mapping = {
        f"{path}::{name}": f"PTI-{index:03d}"
        for index, (path, _line, name) in enumerate(selectors, start=1)
    }
    source_manifest = "\n".join(f"{path}:{line}:{name}" for path, line, name in selectors) + "\n"
    return {
        "schema_version": "puckworks.protected-target-test-manifest/v1",
        "generation_basis": "STATIC_SOURCE_PATH_LINE_FUNCTION_NAME_NO_PARAMETER_REPR",
        "source_selector_sha256": hashlib.sha256(source_manifest.encode()).hexdigest(),
        "opaque_test_mapping": mapping,
    }


def main() -> None:
    OUTPUT.write_text(json.dumps(build(), indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
