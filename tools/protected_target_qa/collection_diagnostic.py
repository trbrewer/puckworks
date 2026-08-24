"""Sanitized structural classification for blocked collection opens."""
from __future__ import annotations


def classify(event: dict) -> str:
    function = event.get("python_function", "")
    filename = event.get("source_filename", "")
    if function == "pytest_generate_tests":
        return "PYTEST_GENERATE_TESTS_ACCESS"
    if function.startswith("pytest_") and "plugin" in filename:
        return "COLLECTION_HOOK_ACCESS"
    if function == "<module>":
        return "MODULE_IMPORT_SIDE_EFFECT"
    if filename.startswith("tests/") and function.startswith("_"):
        return "PARAMETRIZATION_DURING_COLLECTION"
    return "OTHER_STRUCTURAL_CALLSITE"

