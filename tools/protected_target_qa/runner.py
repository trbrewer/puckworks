"""Pytest launcher and plugin for collection-pure item-scoped access."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import warnings
from pathlib import Path

from .audit import MARKER, AuditController, ProtectedTargetCapability
from .collection_diagnostic import classify
from .reporting import write_json

# This module is the launcher entry point. Install before importing pytest.
_CONTROLLER = AuditController(os.environ.get("SCI_MD_004_CANDIDATE_COMMIT", "UNRECORDED"))
_CONTROLLER.install()
import pytest  # noqa: E402

OPAQUE_RE = re.compile(r"^PTI-[0-9]{3}(?:-[0-9]{3})?$")
FAILURE_TEXT = "PROTECTED_TARGET_INTEGRITY_TEST_FAILED"


class ProtectedQAPlugin:
    def __init__(self, controller: AuditController, manifest_path: str, result_path: str | None) -> None:
        self.controller = controller
        self.manifest_path = Path(manifest_path)
        payload = json.loads(self.manifest_path.read_text(encoding="utf-8"))
        self.entries = {row["static_node_id"]: row for row in payload["tests"]}
        self.result_path = result_path
        self.results = []
        self.opens: dict[str, int] = {}
        self.warned: set[str] = set()
        self.invocations: dict[str, int] = {}

    @staticmethod
    def _selector(item) -> str:
        path, _line, function = item.location
        return f"{Path(path).as_posix()}::{function.split('[')[0]}"

    def pytest_collection_modifyitems(self, items) -> None:
        missing = []
        for item in items:
            if item.get_closest_marker(MARKER) is None:
                continue
            selector = self._selector(item)
            entry = self.entries.get(selector)
            if entry is None:
                missing.append(selector)
                continue
            index = self.invocations.get(selector, 0) + 1
            self.invocations[selector] = index
            item._protected_entry = entry
            item._protected_opaque_id = entry["opaque_test_id"] if index == 1 and not hasattr(item, "callspec") else f"{entry['opaque_test_id']}-{index:03d}"
        if missing:
            raise RuntimeError("PROTECTED_TEST_MANIFEST_INCOMPLETE")

    def pytest_collection_finish(self, session) -> None:
        self.controller.collection_complete = True
        self.controller.phase = "post_collection"

    def pytest_runtest_protocol(self, item, nextitem):
        if item.get_closest_marker(MARKER) is None:
            return None
        entry = item._protected_entry
        capability = ProtectedTargetCapability(
            opaque_test_id=item._protected_opaque_id,
            static_node_id=entry["static_node_id"],
            allowed_categories=frozenset(entry["permitted_protected_artifact_categories"]),
            candidate_commit=self.controller.candidate_commit,
            read_only=True,
            pytest_phase="setup",
        )
        with self.controller.capability(capability):
            self.controller.phase = "execution"
            self.controller.output_redaction_active = True
            self._current_opaque = item._protected_opaque_id
            item._protected_capability = capability
            try:
                from _pytest.runner import runtestprotocol
                with warnings.catch_warnings():
                    warnings.simplefilter("error")
                    runtestprotocol(item, nextitem=nextitem)
                return True
            finally:
                self.controller.output_redaction_active = False
                del self._current_opaque

    @staticmethod
    def _phase_capability(capability, phase):
        return ProtectedTargetCapability(
            capability.opaque_test_id, capability.static_node_id, capability.allowed_categories,
            capability.candidate_commit, capability.read_only, phase,
        )

    def pytest_runtest_setup(self, item):
        if item.get_closest_marker(MARKER):
            item._protected_capability.pytest_phase = "setup"

    def pytest_runtest_call(self, item):
        if item.get_closest_marker(MARKER):
            item._protected_capability.pytest_phase = "call"

    def pytest_runtest_teardown(self, item):
        if item.get_closest_marker(MARKER):
            item._protected_capability.pytest_phase = "teardown"

    def pytest_warning_recorded(self, warning_message, when, nodeid, location) -> None:
        if hasattr(self, "_current_opaque"):
            self.warned.add(self._current_opaque)
            warning_message.message = UserWarning("PROTECTED_TARGET_TEST_EMITTED_WARNING")

    @pytest.hookimpl(hookwrapper=True)
    def pytest_runtest_makereport(self, item, call):
        outcome = yield
        report = outcome.get_result()
        if item.get_closest_marker(MARKER) is None:
            return
        opaque = item._protected_opaque_id
        output_kinds = set()
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
        if opaque in self.warned:
            output_kinds.add("WARNING")
        original_failed = report.failed
        if output_kinds and report.when in {"setup", "call", "teardown"}:
            report.outcome = "failed"
        if report.failed:
            failure_class = "PROTECTED_TARGET_TEST_NOT_SILENT" if output_kinds else "ASSERTION_OR_EXCEPTION"
            report.longrepr = (
                f"{FAILURE_TEXT}\nOPAQUE_TEST_ID={opaque}\n"
                f"FAILURE_PHASE={report.when}\nGENERIC_FAILURE_CLASS={failure_class}\n"
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
            })

    def pytest_sessionfinish(self, session, exitstatus) -> None:
        self.controller.phase = "reporting"
        events = self.controller.events
        payload = {
            "schema_version": "puckworks.sci-md-004-stage-e0-r3-protected-qa/v1",
            "candidate_commit": self.controller.candidate_commit,
            "manifest_sha256": hashlib.sha256(self.manifest_path.read_bytes()).hexdigest(),
            "collection_protected_open_count": sum(e["pytest_phase"] == "collection" for e in events),
            "target_value_comparison_performed": False,
            "events": events,
            "results": self.results,
        }
        write_json(self.result_path, payload)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--protected-test-manifest", required=True)
    parser.add_argument("--protected-qa-result")
    parser.add_argument("--collection-diagnostic")
    known, pytest_args = parser.parse_known_args(argv)
    controller = _CONTROLLER
    plugin = ProtectedQAPlugin(controller, known.protected_test_manifest, known.protected_qa_result)
    exit_code = pytest.main(pytest_args, plugins=[plugin])
    if controller.events and any(event["pytest_phase"] == "collection" for event in controller.events):
        event = controller.events[0]
        write_json(known.collection_diagnostic, {
            "result": "PROTECTED_TARGET_COLLECTION_OPEN_BLOCKED",
            "classification": classify(event),
            "event": event,
            "target_content_returned": False,
            "target_value_recorded": False,
        })
        print("PROTECTED_TARGET_COLLECTION_OPEN_BLOCKED", file=sys.stderr)
        print(f"COLLECTION_CALLSITE={event['opaque_callsite_id']}", file=sys.stderr)
    return int(exit_code)
