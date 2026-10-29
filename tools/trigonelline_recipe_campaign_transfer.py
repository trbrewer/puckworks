#!/usr/bin/env python3
"""Explicit private qualification, freeze and one-shot campaign entry points."""
from __future__ import annotations

import argparse
from pathlib import Path

from puckworks.analysis import trigonelline_recipe_campaign_transfer as task


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('qualify', 'freeze', 'run', 'manifest'))
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--old-out', type=Path)
    parser.add_argument('--session-start', type=float)
    args = parser.parse_args()
    if args.action == 'qualify':
        parser.error('--old-out and --session-start required') if args.old_out is None or args.session_start is None else None
        task.qualify(args.out, args.old_out, args.session_start)
    elif args.action == 'freeze':
        parser.error('--session-start required') if args.session_start is None else None
        task.freeze(args.out, args.session_start)
    elif args.action == 'run':
        parser.error('--old-out required') if args.old_out is None else None
        task.run(args.out, args.old_out)
    else:
        task.artifact_manifest(args.out)


if __name__ == '__main__':
    main()
