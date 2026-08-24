"""Fail-closed semantic target guard for SCI-MD-004 Stage E0 R1."""
from __future__ import annotations

import hashlib
import json
import os
import sys
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parents[2]
FAILURE = "SCI_MD_004_STAGE_E0_R1_UNAUTHORIZED_SEMANTIC_HOLDOUT_ACCESS"

DENIED_RELATIVE_PATHS = (
    "docs/analysis/sci_md_004/angeloni_targets_long.csv",
    "puckworks/data/angeloni2023/bioactives.csv",
    "puckworks/data/angeloni2023/total_solids.csv",
    "puckworks/data/angeloni2023/lipids.csv",
)
PERMITTED_INPUT_RELATIVE_PATHS = (
    "docs/analysis/sci_md_004/angeloni_conditions.csv",
    "docs/analysis/sci_md_004/angeloni_inventories_long.csv",
)
OPAQUE_METADATA_RELATIVE_PATHS = (
    "docs/analysis/sci_md_004/data_contract.json",
    "docs/analysis/sci_md_004/bundle_manifest.json",
)
DENIED_APIS = (
    "puckworks.analysis.angeloni2023_multispecies.build_targets",
    "puckworks.analysis.angeloni2023_multispecies.build_contract",
    "puckworks.analysis.angeloni2023_multispecies.write_bundle",
    "puckworks.data.angeloni_bioactives",
    "puckworks.data.angeloni_total_solids",
    "puckworks.data.angeloni_lipids",
)
DENIED_MODULES = (
    "puckworks.analysis.angeloni2023_multispecies",
)


def _canonical(path: str | os.PathLike[str]) -> str:
    candidate = Path(path)
    if not candidate.is_absolute():
        candidate = ROOT / candidate
    return os.path.normcase(str(candidate.resolve(strict=False))).casefold()


_DENIED = frozenset(_canonical(path) for path in DENIED_RELATIVE_PATHS)


def assert_semantic_path_allowed(path: str | os.PathLike[str]) -> Path:
    resolved = Path(path)
    if not resolved.is_absolute():
        resolved = ROOT / resolved
    resolved = resolved.resolve(strict=False)
    canonical = os.path.normcase(str(resolved)).casefold()
    if canonical in _DENIED:
        raise PermissionError(f"{FAILURE}:{resolved.name}")
    return resolved


def assert_api_allowed(api: str) -> None:
    folded = api.casefold()
    if folded in {item.casefold() for item in DENIED_APIS}:
        raise PermissionError(f"{FAILURE}:TARGET_API")
    if folded in {item.casefold() for item in DENIED_MODULES}:
        raise PermissionError(f"{FAILURE}:TARGET_MODULE_IMPORT")


def assert_configuration_allowed(value: object) -> None:
    if isinstance(value, dict):
        for key, item in value.items():
            assert_configuration_allowed(key)
            assert_configuration_allowed(item)
    elif isinstance(value, (list, tuple, set)):
        for item in value:
            assert_configuration_allowed(item)
    elif isinstance(value, (str, os.PathLike)):
        text = str(value)
        for denied in DENIED_RELATIVE_PATHS:
            if denied.casefold() in text.replace("\\", "/").casefold():
                raise PermissionError(f"{FAILURE}:TARGET_PATH_IN_CONFIGURATION")
        for api in DENIED_APIS:
            if api.casefold() in text.casefold():
                raise PermissionError(f"{FAILURE}:TARGET_API_IN_CONFIGURATION")


def assert_environment_allowed(environment: dict[str, str] | None = None) -> None:
    assert_configuration_allowed(dict(os.environ if environment is None else environment))


def assert_subprocess_allowed(argv: Iterable[object], environment: dict[str, str] | None = None) -> None:
    assert_configuration_allowed([str(item) for item in argv])
    if environment is not None:
        assert_environment_allowed(environment)


class SemanticAccessGuard:
    """Record repository file opens and reject protected target paths.

    Python audit hooks cannot be removed.  One inert hook is installed per
    process; it acts only while this context is active.
    """

    _installed = False
    _active: "SemanticAccessGuard | None" = None

    def __init__(self) -> None:
        self._opened: set[Path] = set()

    @classmethod
    def _audit(cls, event: str, args: tuple) -> None:
        active = cls._active
        if active is None or event != "open" or not args:
            return
        raw = args[0]
        if not isinstance(raw, (str, bytes, os.PathLike)):
            return
        path = Path(os.fsdecode(raw))
        if not path.is_absolute():
            path = Path.cwd() / path
        resolved = assert_semantic_path_allowed(path)
        mode = args[1] if len(args) > 1 else "r"
        if isinstance(mode, str) and any(flag in mode for flag in "wax+"):
            return
        try:
            resolved.relative_to(ROOT)
        except ValueError:
            return
        active._opened.add(resolved)

    def __enter__(self) -> "SemanticAccessGuard":
        if SemanticAccessGuard._active is not None:
            raise RuntimeError("NESTED_SEMANTIC_ACCESS_GUARD")
        if not SemanticAccessGuard._installed:
            sys.addaudithook(SemanticAccessGuard._audit)
            SemanticAccessGuard._installed = True
        SemanticAccessGuard._active = self
        return self

    def __exit__(self, exc_type, exc, traceback) -> None:
        SemanticAccessGuard._active = None

    def manifest(self) -> dict:
        files = []
        for path in sorted(self._opened):
            relative = path.relative_to(ROOT).as_posix()
            files.append({
                "path": relative,
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None,
            })
        return {
            "schema_version": "puckworks.sci-md-004-stage-e0-r1-access/v1",
            "semantic_target_access": False,
            "opened_repository_files": files,
            "denied_target_paths": list(DENIED_RELATIVE_PATHS),
        }

    def write_manifest(self, destination: Path) -> None:
        destination.write_text(json.dumps(self.manifest(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
