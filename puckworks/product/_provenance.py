"""Deterministic build-provenance provider (issue #32, PR 1).

The public bundle must record ``source_commit`` without a runtime Git call, a repository checkout, a
``.git`` inspection, a working-directory guess, or an implicit wall clock. This provider reads an
optional packaged resource (which a future release build may inject) and otherwise reports an unset
commit. The record semantics are complete now; the automatic injection mechanism is deferred.
"""
from __future__ import annotations

import importlib.resources as resources

from .. import __version__
from ._records import BuildProvenance

_COMMIT_RESOURCE = "_build_commit.txt"


def _packaged_commit() -> str | None:
    """Full commit written by a release build into the product package, if present. No Git call."""
    try:
        res = resources.files(__package__).joinpath(_COMMIT_RESOURCE)
        if res.is_file():
            text = res.read_text(encoding="utf-8").strip()
            return text or None
    except (FileNotFoundError, ModuleNotFoundError, OSError):
        return None
    return None


def build_provenance(source_commit: str | None = None, generation_timestamp: str | None = None) -> BuildProvenance:
    """Assemble :class:`BuildProvenance` for the current build.

    ``source_commit`` may be supplied explicitly (e.g. a fixed value for a deterministic golden
    object or a release-injected commit); otherwise a packaged resource is consulted. No Git command
    is ever run. ``generation_timestamp`` is an explicit input and is omitted from byte-stable golden
    output unless a caller supplies a fixed value.
    """
    commit: str | None
    if source_commit is not None:
        commit, src = source_commit, "explicit"
    else:
        commit = _packaged_commit()
        src = "packaged_resource" if commit else "unset"
    return BuildProvenance(
        package_version=__version__,
        provenance_source=src,
        source_commit=commit,
        generation_timestamp=generation_timestamp,
    )


__all__ = ["build_provenance"]
