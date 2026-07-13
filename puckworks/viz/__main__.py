"""CLI for the viz layer.

    python -m puckworks.viz list                       # honesty audit at a glance
    python -m puckworks.viz compute [--id ID]          # run (cached) producers
    python -m puckworks.viz render  [--id ID] [--class 1|2] [--with-3d] [--video]
    python -m puckworks.viz gallery                     # regenerate GALLERY.md

Heavy renders (LB / 3D / video) run LOCALLY or in Colab, never in CI: `render`
skips slow specs unless --with-3d/--video/--slow selects them.
"""
from __future__ import annotations
import argparse

from .registry import (VIZZES, viz_by_id, render_all, compute_all, write_gallery,
                       validate_all)


def _cmd_list(_a):
    errs = validate_all()
    print(f"{len(VIZZES)} visuals · honesty contract: "
          f"{'CLEAN' if not errs else str(len(errs)) + ' VIOLATIONS'}")
    for v in VIZZES:
        slow = " [slow]" if v.slow else ""
        print(f"  {v.id:26s} class {v.class_} · [{v.badge}] · {v.evidence_strength}"
              f"{slow}\n      producer {v.producer.ref()} · ceiling: "
              f"{v.fidelity_ceiling[:70]}...")
    for e in errs:
        print("  VIOLATION:", e)
    return 1 if errs else 0


def _cmd_compute(a):
    sel = [a.id] if a.id else None
    for r in compute_all(select=sel, run_slow=a.slow or bool(a.id)):
        print(" ", r)
    return 0


def _cmd_render(a):
    sel = [a.id] if a.id else None
    run_slow = a.slow or a.video or a.with_3d or bool(a.id)
    for r in render_all(select=sel, cls=a.klass, with_3d=a.with_3d, video=a.video,
                        run_slow=run_slow, hires=a.hires):
        print(" ", r)
    return 0


def _cmd_gallery(_a):
    path = write_gallery()
    print("wrote", path)
    return 0


def main(argv=None):
    p = argparse.ArgumentParser(prog="puckworks.viz")
    sub = p.add_subparsers(dest="cmd", required=True)
    for name in ("list", "compute", "render", "gallery"):
        sp = sub.add_parser(name)
        sp.add_argument("--id", default=None)
        sp.add_argument("--class", dest="klass", type=int, choices=(1, 2), default=None)
        sp.add_argument("--out", default="docs/figures/viz")
        sp.add_argument("--with-3d", dest="with_3d", action="store_true")
        sp.add_argument("--video", action="store_true")
        sp.add_argument("--slow", action="store_true")
        sp.add_argument("--hires", action="store_true",
                        help="also write 300-dpi stills to frames/ (gitignored)")
    a = p.parse_args(argv)
    return {"list": _cmd_list, "compute": _cmd_compute, "render": _cmd_render,
            "gallery": _cmd_gallery}[a.cmd](a)


if __name__ == "__main__":
    raise SystemExit(main())
