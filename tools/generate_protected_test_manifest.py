"""Generate the R3 source-only protected-test manifest without importing tests."""
from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "tests/protected_target_test_manifest.json"
MARKER = "protected_target_integrity"
CATEGORIES = (
    "ANGELONI_STAGE_A_TARGETS", "ANGELONI_BIOACTIVES",
    "ANGELONI_TOTAL_SOLIDS", "ANGELONI_LIPIDS",
)
MODULE_CATEGORIES = {
    "tests/test_data_loaders.py": ("ANGELONI_BIOACTIVES", "ANGELONI_TOTAL_SOLIDS", "ANGELONI_LIPIDS"),
    "tests/test_paper_a_model_contract.py": ("ANGELONI_BIOACTIVES",),
    "tests/test_paper_a_source_observations.py": ("ANGELONI_BIOACTIVES",),
    "tests/test_paper_a_source_schema.py": ("ANGELONI_BIOACTIVES",),
    "tests/test_paper_a_transfer_contract.py": ("ANGELONI_BIOACTIVES",),
    "tests/test_sci_md_004_silent_qa.py": ("ANGELONI_BIOACTIVES",),
    "tests/test_sci_md_004_stage_a.py": CATEGORIES,
    "tests/test_sci_md_004_stage_e0_r1.py": ("ANGELONI_STAGE_A_TARGETS",),
    "tests/test_screen_i010.py": ("ANGELONI_TOTAL_SOLIDS",),
}
TARGET_CALLS = {
    "angeloni_bioactives", "angeloni_total_solids", "angeloni_lipids",
}
TARGET_PATH_TOKENS = {
    "angeloni_targets_long.csv", "bioactives.csv", "total_solids.csv", "lipids.csv",
}


def _decorated(node: ast.AST) -> bool:
    return any(isinstance(part, ast.Attribute) and part.attr == MARKER
               for decorator in getattr(node, "decorator_list", []) for part in ast.walk(decorator))


def _module_marked(tree: ast.Module) -> bool:
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        if not any(isinstance(target, ast.Name) and target.id == "pytestmark" for target in node.targets):
            continue
        if any(isinstance(part, ast.Attribute) and part.attr == MARKER for part in ast.walk(node.value)):
            return True
    return False


def _target_references(tree: ast.Module) -> list[tuple[int, str]]:
    references = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            name = node.func.id if isinstance(node.func, ast.Name) else (node.func.attr if isinstance(node.func, ast.Attribute) else "")
            if name in TARGET_CALLS:
                references.append((node.lineno, f"call:{name}"))
            elif isinstance(node.func, ast.Attribute) and isinstance(node.func.value, ast.Name):
                if (node.func.value.id, name) in {("ORACLE", "read_source_records"), ("SS", "preflight")}:
                    references.append((node.lineno, f"call:{node.func.value.id}.{name}"))
                elif node.func.value.id == "adapter" and name in {"build_targets", "build_contract", "write_bundle"}:
                    references.append((node.lineno, f"call:adapter.{name}"))
        elif isinstance(node, ast.Constant) and isinstance(node.value, str):
            if any(token in node.value for token in TARGET_PATH_TOKENS):
                references.append((node.lineno, "protected-path-reference"))
    return sorted(set(references))


def build() -> dict:
    selectors = []
    coverage = []
    violations = []
    for path in sorted((ROOT / "tests").glob("test_*.py")):
        relative = path.relative_to(ROOT).as_posix()
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=relative)
        module_marked = _module_marked(tree)
        for line, kind in _target_references(tree):
            coverage.append({"module_path": relative, "source_line_number": line, "reference_kind": kind})
            if not module_marked:
                containing = next((node for node in ast.walk(tree)
                    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
                    and node.lineno <= line <= getattr(node, "end_lineno", node.lineno)
                    and _decorated(node)), None)
                if containing is None:
                    violations.append({"module_path": relative, "source_line_number": line, "reference_kind": kind})
        for node in tree.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name.startswith("test_"):
                if module_marked or _decorated(node):
                    selectors.append((relative, node.lineno, node.name))
    selectors.sort()
    tests = [{
        "static_module_path": path,
        "static_function_name": name,
        "static_node_id": f"{path}::{name}",
        "opaque_test_id": f"PTI-{index:03d}",
        "permitted_protected_artifact_categories": list(MODULE_CATEGORIES.get(path, ("ANGELONI_BIOACTIVES",))),
        "expected_execution_phase": ["setup", "call", "teardown"],
        "marker_name": MARKER,
    } for index, (path, _line, name) in enumerate(selectors, start=1)]
    source = "\n".join(f"{path}:{line}:{name}" for path, line, name in selectors) + "\n"
    return {
        "schema_version": "puckworks.protected-target-test-manifest/v2",
        "generation_basis": "STATIC_AST_NO_TEST_IMPORT_NO_API_EXECUTION",
        "source_selector_sha256": hashlib.sha256(source.encode()).hexdigest(),
        "tests": tests,
        "static_target_reference_coverage": coverage,
        "coverage_violations": violations,
    }


def main() -> None:
    payload = build()
    if payload["coverage_violations"]:
        raise SystemExit("PROTECTED_TEST_STATIC_MARKER_COVERAGE_FAILED")
    OUTPUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
