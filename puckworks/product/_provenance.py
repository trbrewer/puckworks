"""Deterministic build-provenance provider (issue #32, PR 1).

The public bundle must record a **full** ``source_commit`` without a runtime Git call, a repository
checkout, a ``.git`` inspection, a working-directory guess, or an implicit wall clock. A caller
supplies the commit explicitly, or a packaged resource (which a future release build may inject)
provides it. If neither exists, :func:`build_provenance` raises — it never returns an ``unset`` record.
"""
from __future__ import annotations

import importlib.resources as resources
import re

from .. import __version__
from ._enums import ProvenanceSource
from ._records import BuildProvenance

_COMMIT_RESOURCE = "_build_provenance.json"
_COMMIT_RE = re.compile(r"^[0-9a-f]{40}$")


class ProvenanceUnavailableError(RuntimeError):
    """Raised when no explicit or packaged source commit is available for a public bundle."""


def _packaged_commit() -> str | None:
    """Full commit written by a release build into the product package, if present. No Git call."""
    import json
    try:
        res = resources.files(__package__).joinpath(_COMMIT_RESOURCE)
        if res.is_file():
            data = json.loads(res.read_text(encoding="utf-8"))
            commit = str(data.get("source_commit", "")).strip()
            return commit or None
    except (FileNotFoundError, ModuleNotFoundError, OSError, ValueError):
        return None
    return None


def dev_build_identifier(source_commit: str) -> str:
    """A development build identifier for unreleased next-minor work, e.g. ``dev+<short>``."""
    if not _COMMIT_RE.match(source_commit or ""):
        raise ValueError("dev_build_identifier requires a full 40-hex commit")
    return f"dev+{source_commit[:12]}"


def build_provenance(
    *,
    source_commit: str | None = None,
    build_identifier: str | None = None,
    generation_timestamp: str | None = None,
) -> BuildProvenance:
    """Assemble :class:`BuildProvenance` with a mandatory full ``source_commit``.

    ``source_commit`` may be supplied explicitly (e.g. a fixed value for a deterministic golden object
    or a release-injected commit); otherwise a packaged ``_build_provenance.json`` resource is
    consulted. No Git command is ever run, and the working directory does not affect the result.
    Raises :class:`ProvenanceUnavailableError` if neither source is available — an ``unset`` public
    bundle is not permitted. ``generation_timestamp`` is an explicit input, omitted from byte-stable
    golden output unless a caller supplies a fixed value.
    """
    if source_commit is not None:
        commit, src = source_commit, ProvenanceSource.EXPLICIT
    else:
        packaged = _packaged_commit()
        if packaged is None:
            raise ProvenanceUnavailableError(
                "no source_commit available: supply source_commit explicitly, or provide a packaged "
                "_build_provenance.json (release builds inject it). A public bundle must not be 'unset'."
            )
        commit, src = packaged, ProvenanceSource.PACKAGED_RESOURCE
    return BuildProvenance(
        package_version=__version__,
        provenance_source=src,
        source_commit=commit,
        build_identifier=build_identifier,
        generation_timestamp=generation_timestamp,
    )


__all__ = ["build_provenance", "dev_build_identifier", "ProvenanceUnavailableError"]
