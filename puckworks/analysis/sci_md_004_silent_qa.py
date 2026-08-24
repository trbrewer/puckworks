"""Pytest plugin for silent, provenance-aware protected-target integrity QA.

The plugin never compares visible output with target values.  It enforces that
marked tests originate no stdout, stderr, logs, or warnings, replaces every
visible protected-test identity with an opaque source-defined identifier, and
redacts all protected-test failures before pytest reporters can serialize them.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
import warnings
from pathlib import Path

import pytest

from puckworks.analysis.sci_md_004_target_guard import DENIED_RELATIVE_PATHS, ROOT

MARKER = "protected_target_integrity"
FAILURE_TEXT = "PROTECTED_TARGET_INTEGRITY_TEST_FAILED"
OPAQUE_RE = re.compile(r"^PTI-[0-9]{3}(?:-[0-9]{3})?$")
_DENIED = {
    os.path.normcase(str((ROOT / relative).resolve(strict=False))).casefold(): Path(relative).name
    for relative in DENIED_RELATIVE_PATHS
}


def _selector(item) -> str:
    path, line, function = item.location
    base = function.split("[")[0]
    return f"{Path(path).as_posix()}::{base}"


class SilentProtectedTargetPlugin:
    def __init__(self, config) -> None:
        manifest_path = config.getoption("--protected-test-manifest")
        if not manifest_path:
            raise pytest.UsageError("--protected-test-manifest is required")
        payload = json.loads(Path(manifest_path).read_text(encoding="utf-8"))
        self.mapping = payload["opaque_test_mapping"]
        self.test_manifest_hash = hashlib.sha256(Path(manifest_path).read_bytes()).hexdigest()
        self.output_path = config.getoption("--protected-qa-result")
        self.current_item = None
        self.current_opaque = None
        self.invocations: dict[str, int] = {}
        self.warned: set[str] = set()
        self.target_opens: dict[str, int] = {}
        self.results: list[dict] = []
        self.synthetic_canary = os.environ.get("SCI_MD_004_SYNTHETIC_CANARY", "")
        sys.addaudithook(self._audit)

    def _audit(self, event: str, args: tuple) -> None:
        if event != "open" or not args or not isinstance(args[0], (str, bytes, os.PathLike)):
            return
        path = Path(os.fsdecode(args[0]))
        if not path.is_absolute():
            path = Path.cwd() / path
        canonical = os.path.normcase(str(path.resolve(strict=False))).casefold()
        if self.current_opaque and self.synthetic_canary and self.synthetic_canary in str(path):
            raise PermissionError("SYNTHETIC_CANARY_TEMPORARY_FILENAME_REDACTED")
        category = _DENIED.get(canonical)
        if category is None:
            return
        if self.current_item is None or self.current_item.get_closest_marker(MARKER) is None:
            raise PermissionError(f"UNMARKED_PROTECTED_TARGET_ACCESS:{category}")
        self.target_opens[self.current_opaque] = self.target_opens.get(self.current_opaque, 0) + 1

    def pytest_collection_modifyitems(self, session, config, items) -> None:
        missing = []
        for item in items:
            if item.get_closest_marker(MARKER) is None:
                continue
            selector = _selector(item)
            base = self.mapping.get(selector)
            if base is None or not OPAQUE_RE.fullmatch(base):
                missing.append(selector)
                continue
            index = self.invocations.get(selector, 0) + 1
            self.invocations[selector] = index
            item._protected_opaque_id = base if index == 1 and not hasattr(item, "callspec") else f"{base}-{index:03d}"
            if self.synthetic_canary and self.synthetic_canary in item.nodeid:
                item._protected_node_id_violation = True
        if missing:
            raise pytest.UsageError("PROTECTED_TEST_MANIFEST_INCOMPLETE")

    @pytest.hookimpl(hookwrapper=True)
    def pytest_runtest_protocol(self, item, nextitem):
        if item.get_closest_marker(MARKER) is not None:
            self.current_item = item
            self.current_opaque = item._protected_opaque_id
        yield
        self.current_item = None
        self.current_opaque = None

    @pytest.hookimpl(hookwrapper=True)
    def pytest_runtest_call(self, item):
        if item.get_closest_marker(MARKER) is None:
            yield
            return
        with warnings.catch_warnings(record=True) as emitted:
            warnings.simplefilter("always")
            yield
        if emitted:
            item._protected_warning_emitted = True

    def pytest_warning_recorded(self, warning_message, when, nodeid, location) -> None:
        if self.current_opaque:
            self.warned.add(self.current_opaque)
            warning_message.message = UserWarning("PROTECTED_TARGET_TEST_EMITTED_WARNING")

    @pytest.hookimpl(hookwrapper=True)
    def pytest_runtest_makereport(self, item, call):
        outcome = yield
        report = outcome.get_result()
        if item.get_closest_marker(MARKER) is None:
            return
        opaque = item._protected_opaque_id
        output_kinds = set()
        if getattr(item, "_protected_node_id_violation", False):
            output_kinds.add("NODE_ID")
        for title, content in report.sections:
            if not content:
                continue
            folded = title.casefold()
            if "stdout" in folded:
                output_kinds.add("STDOUT")
            elif "stderr" in folded:
                output_kinds.add("STDERR")
            elif "log" in folded:
                output_kinds.add("LOG")
        if opaque in self.warned or getattr(item, "_protected_warning_emitted", False):
            output_kinds.add("WARNING")
        original_failed = report.failed
        if output_kinds and report.when in {"setup", "call", "teardown"}:
            report.outcome = "failed"
        if report.failed:
            generic = "PROTECTED_TARGET_TEST_NOT_SILENT" if output_kinds else "ASSERTION_OR_EXCEPTION"
            report.longrepr = (
                f"{FAILURE_TEXT}\nOPAQUE_TEST_ID={opaque}\n"
                f"FAILURE_PHASE={report.when}\nGENERIC_FAILURE_CLASS={generic}\n"
                "NO_TARGET_VALUE_DISCLOSED"
            )
        report.sections[:] = []
        report.nodeid = opaque
        if report.when == "call" or (report.failed and report.when != "call"):
            self.results.append({
                "opaque_test_id": opaque,
                "phase": report.when,
                "status": "FAIL" if report.failed else ("SKIP" if report.skipped else "PASS"),
                "generic_failure_class": (
                    "PROTECTED_TARGET_TEST_NOT_SILENT" if output_kinds else
                    ("ASSERTION_OR_EXCEPTION" if original_failed else None)
                ),
                "target_open_count": self.target_opens.get(opaque, 0),
            })

    def pytest_sessionfinish(self, session, exitstatus) -> None:
        if not self.output_path:
            return
        candidate = os.environ.get("SCI_MD_004_CANDIDATE_COMMIT", "UNRECORDED")
        payload = {
            "schema_version": "puckworks.sci-md-004-silent-target-qa/v1",
            "candidate_commit": candidate,
            "test_manifest_sha256": self.test_manifest_hash,
            "target_value_comparison_performed": False,
            "results": sorted(self.results, key=lambda row: row["opaque_test_id"]),
        }
        Path(self.output_path).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def pytest_addoption(parser) -> None:
    group = parser.getgroup("protected-target-silent-qa")
    group.addoption("--protected-test-manifest", action="store")
    group.addoption("--protected-qa-result", action="store")


def pytest_configure(config) -> None:
    if config.getoption("--protected-test-manifest"):
        config.pluginmanager.register(SilentProtectedTargetPlugin(config), "sci-md-004-silent-target-qa")
