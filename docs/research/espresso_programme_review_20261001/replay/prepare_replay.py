"""Prepare a NEW private replay workspace; does not execute any model."""
import argparse
import hashlib
import json
import shutil
from pathlib import Path

HERE = Path(__file__).resolve().parent


def prepare(author_source, out, case):
    identity = json.loads((HERE.parent / "balance/SOURCE_IDENTITIES.json").read_text())
    for name, expected in identity["source_sha256"].items():
        actual = hashlib.sha256((author_source / name).read_bytes()).hexdigest()
        if actual != expected:
            raise ValueError("not the pinned source bytes: " + name)
    if out.exists():
        raise FileExistsError("fresh output workspace required")
    out.mkdir(parents=True)
    (out / "source").mkdir()
    dest = out / case
    dest.mkdir()
    for name in identity["source_sha256"]:
        shutil.copyfile(author_source / name, out / "source" / name)
        shutil.copyfile(author_source / name, dest / name)
    shutil.copyfile(HERE / "LICENSE.author", out / "source/LICENSE")
    for path in HERE.iterdir():
        if path.suffix in (".m", ".py") and path.name != "prepare_replay.py":
            shutil.copyfile(path, out / path.name)
    shutil.copyfile(HERE / "templates" / (case + ".m"), dest / "instrumented_run.m")
    shutil.copyfile(HERE / "export_moments.m", dest / "export_moments.m")
    shutil.copyfile(HERE / "export_boundary.m", dest / "export_boundary.m")
    (dest / "run_case.m").write_text(
        "addpath('..');\nrun('instrumented_run.m');\n"
        "run('export_moments.m');\nrun('export_boundary.m');\n")
    print("Prepared only; source/fixture runtime UNEXECUTED:", out)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--author-source", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--case", choices=("reference", "tight", "early"), required=True)
    args = parser.parse_args()
    prepare(args.author_source.resolve(), args.out.resolve(), args.case)
