"""Scan exactly one submission file with injected text, for the round-12 probe regressions.

Kept out of the test module so the probe file reads as the reviewer's counterexamples rather than as
fixture plumbing. The copy keeps its original BASENAME, because rule scope is keyed on it — a helper
that renamed the file would scope every rule out and report a serene, meaningless zero.
"""
from __future__ import annotations

import pathlib
import shutil
import sys
import tempfile

REPO = pathlib.Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from tools import paper_a_consistency as C  # noqa: E402

_REDIRECTED = ("CONVERSION", "PACKAGE", "HIGHLIGHTS", "COVER_LETTER", "SUPPLEMENT",
               "UPLOAD_CAPTIONS", "CANONICAL")


def scan_one(attr: str, injected: str) -> list[str]:
    """Append ``injected`` to a copy of ``C.<attr>``, scan only that file, restore, return problems."""
    saved = {name: getattr(C, name) for name in _REDIRECTED}
    saved["SUBMISSION_FILES"] = C.SUBMISSION_FILES
    root = pathlib.Path(tempfile.mkdtemp())
    try:
        src = getattr(C, attr)
        dst = root / src.name
        shutil.copy(src, dst)
        dst.write_text(dst.read_text(encoding="utf-8") + "\n\n" + injected + "\n", encoding="utf-8")
        for name in _REDIRECTED:
            setattr(C, name, root / "absent.md")
        setattr(C, attr, dst)
        C.SUBMISSION_FILES = (dst,)
        return C._placeholders_and_process_language()
    finally:
        for name, value in saved.items():
            setattr(C, name, value)
