"""Process-lifetime audit hook installed before pytest is imported.

Only structural provenance is retained. Protected bytes and exception locals are never read.
"""
from __future__ import annotations

import contextlib
import contextvars
import hashlib
import inspect
import os
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MARKER = "protected_target_integrity"
COLLECTION_BLOCKED = "PROTECTED_TARGET_COLLECTION_OPEN_BLOCKED"

PROTECTED = {
    "ANGELONI_STAGE_A_TARGETS": ROOT / "docs/analysis/sci_md_004/angeloni_targets_long.csv",
    "ANGELONI_BIOACTIVES": ROOT / "puckworks/data/angeloni2023/bioactives.csv",
    "ANGELONI_TOTAL_SOLIDS": ROOT / "puckworks/data/angeloni2023/total_solids.csv",
    "ANGELONI_LIPIDS": ROOT / "puckworks/data/angeloni2023/lipids.csv",
}
FAILURE_CLASSES = {
    "collection": "SCI_MD_004_STAGE_E0_R3_COLLECTION_PURITY_FAILED",
    "unmarked": "SCI_MD_004_STAGE_E0_R3_UNMARKED_PROTECTED_TARGET_ACCESS",
    "architecture": "SCI_MD_004_STAGE_E0_R3_TARGET_TEST_ARCHITECTURE_BLOCKED",
}
_CANONICAL = {os.path.normcase(str(path.resolve())).casefold(): category for category, path in PROTECTED.items()}
if os.environ.get("SCI_MD_004_SYNTHETIC_PROTECTED_PATH"):
    synthetic = Path(os.environ["SCI_MD_004_SYNTHETIC_PROTECTED_PATH"]).resolve(strict=False)
    _CANONICAL[os.path.normcase(str(synthetic)).casefold()] = "SYNTHETIC_CANARY"


class ProtectedTargetDenied(PermissionError):
    """Opaque fail-closed exception; it intentionally carries no path or data."""


@dataclass
class ProtectedTargetCapability:
    opaque_test_id: str
    static_node_id: str
    allowed_categories: frozenset[str]
    candidate_commit: str
    read_only: bool
    pytest_phase: str


_capability: contextvars.ContextVar[ProtectedTargetCapability | None] = contextvars.ContextVar(
    "protected_target_capability", default=None
)


class AuditController:
    def __init__(self, candidate_commit: str) -> None:
        self.candidate_commit = candidate_commit
        self.pid = os.getpid()
        self.phase = "collection"
        self.collection_complete = False
        self.output_redaction_active = False
        self.events: list[dict] = []
        self._installed = False

    def install(self) -> None:
        if self._installed:
            return
        sys.addaudithook(self._audit)
        self._installed = True

    @contextlib.contextmanager
    def capability(self, value: ProtectedTargetCapability):
        token = _capability.set(value)
        try:
            yield
        finally:
            _capability.reset(token)

    @staticmethod
    def _mode(args: tuple) -> str:
        mode = args[1] if len(args) > 1 else "r"
        if isinstance(mode, str):
            return mode
        if isinstance(mode, int):
            return "read_only" if not mode & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC | os.O_APPEND) else "write"
        return "unknown"

    @staticmethod
    def _read_only(mode: str) -> bool:
        return mode in {"r", "rb", "rt", "read_only"}

    def _structural_frames(self) -> list[dict]:
        frames = []
        for frame_info in inspect.stack(context=0)[2:]:
            filename = Path(frame_info.filename).resolve(strict=False)
            try:
                relative = filename.relative_to(ROOT).as_posix()
            except ValueError:
                continue
            module = frame_info.frame.f_globals.get("__name__", "")
            frames.append({
                "module": str(module),
                "function": frame_info.function,
                "source_filename": relative,
                "source_line_number": frame_info.lineno,
            })
        return frames

    def _record(self, category: str, mode: str) -> dict:
        frames = self._structural_frames()
        encoded = "\n".join(
            f"{row['module']}|{row['function']}|{row['source_filename']}|{row['source_line_number']}"
            for row in frames
        ).encode()
        digest = hashlib.sha256(encoded).hexdigest()
        callsite = f"CPO-{len(self.events) + 1:03d}"
        primary = next((row for row in frames if row["source_filename"].startswith("tests/")), frames[0] if frames else {})
        capability = _capability.get()
        event = {
            "opaque_callsite_id": callsite,
            "protected_artifact_category": category,
            "attempted_access_mode": mode,
            "pytest_phase": capability.pytest_phase if capability else self.phase,
            "python_module": primary.get("module", "UNKNOWN"),
            "python_function": primary.get("function", "UNKNOWN"),
            "source_filename": primary.get("source_filename", "UNKNOWN"),
            "source_line_number": primary.get("source_line_number", 0),
            "collector_filename": primary.get("source_filename", "UNKNOWN"),
            "process_id": os.getpid(),
            "parent_process_id": os.getppid(),
            "static_node_id": capability.static_node_id if capability else None,
            "call_stack_sha256": digest,
            "candidate_commit": self.candidate_commit,
            "candidate_tree": os.environ.get("SCI_MD_004_CANDIDATE_TREE", "UNRECORDED"),
        }
        self.events.append(event)
        return event

    def _audit(self, event: str, args: tuple) -> None:
        if event != "open" or not args or not isinstance(args[0], (str, bytes, os.PathLike)):
            return
        path = Path(os.fsdecode(args[0]))
        if not path.is_absolute():
            path = Path.cwd() / path
        category = _CANONICAL.get(os.path.normcase(str(path.resolve(strict=False))).casefold())
        if category is None:
            return
        mode = self._mode(args)
        record = self._record(category, mode)
        if not self.collection_complete or self.phase == "collection":
            raise ProtectedTargetDenied(f"{COLLECTION_BLOCKED}\nCOLLECTION_CALLSITE={record['opaque_callsite_id']}")
        capability = _capability.get()
        semantic_module_present = any(
            row["module"].startswith("puckworks.analysis.sci_md_004_stage_e0")
            for row in self._structural_frames()
        )
        if (
            capability is None
            or os.getpid() != self.pid
            or capability.pytest_phase not in {"setup", "call", "teardown"}
            or category not in capability.allowed_categories
            or not capability.read_only
            or not self._read_only(mode)
            or not self.output_redaction_active
            or semantic_module_present
        ):
            raise ProtectedTargetDenied(FAILURE_CLASSES["unmarked"])
