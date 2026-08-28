from __future__ import annotations

import argparse
from copy import deepcopy
from pathlib import Path

import yaml

from tools.publishing.common import ValidationError, parse_frontmatter
from tools.publishing.validate_draft import validate


def render(meta: dict[str, object], body: str) -> str:
    return "---\n" + yaml.safe_dump(meta, sort_keys=False, allow_unicode=True) + "---\n" + body


def build(
    master: Path, output_dir: Path, platform: str, *, force: bool = False,
    repositories: dict[str, Path] | None = None, content_root: Path | None = None,
) -> Path:
    root = content_root or master.resolve().parents[2]
    result = validate(master, repositories, content_root=root)
    if not result.ok:
        raise ValidationError("master draft failed validation: " + "; ".join(result.errors))
    meta, body = parse_frontmatter(master)
    targets = meta.get("target_platforms", [])
    if platform not in targets:
        raise ValidationError(f"{platform} is not enabled in target_platforms")
    derived = deepcopy(meta)
    derived["status"] = "human_review"
    derived["derived_from"] = str(master)
    derived["platform"] = platform
    slug = str(meta["slug"])
    date_prefix = master.name[:10]
    output = output_dir / f"{date_prefix}-{slug}.{platform}.md"
    if output.exists() and not force:
        raise ValidationError(f"refusing to overwrite existing variant: {output}; use --force")
    if platform == "substack":
        disclosure = meta["ai_assistance"]["disclosure_substack"]
        body = body.replace("[PLATFORM DISCLOSURE]", str(disclosure))
    elif platform == "medium":
        cross = meta.get("cross_posting", {})
        canonical = cross.get("canonical_url") if isinstance(cross, dict) else None
        substack = cross.get("substack", {}) if isinstance(cross, dict) else {}
        if not canonical or not isinstance(substack, dict) or canonical != substack.get("url"):
            raise ValidationError("Medium generation requires the exact published Substack URL as canonical")
        derived["canonical_url"] = canonical
        derived["ai_assistance"]["substantive_human_rewrite_medium"] = False
        disclosure = meta["ai_assistance"]["disclosure_medium"]
        body = f"{disclosure}\n\n> **Human rewrite required:** This generated variant is not Medium-ready.\n\n" + body
        body = body.replace("[PLATFORM DISCLOSURE]", "")
    else:
        raise ValidationError(f"unsupported platform: {platform}")
    output_dir.mkdir(parents=True, exist_ok=True)
    output.write_text(render(derived, body), encoding="utf-8")
    return output


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("master", type=Path)
    parser.add_argument("--platform", required=True, choices=("substack", "medium"))
    parser.add_argument("--output-dir", type=Path, default=Path("content/variants"))
    parser.add_argument("--force", action="store_true", help="replace an existing generated variant")
    args = parser.parse_args()
    try:
        print(build(args.master, args.output_dir, args.platform, force=args.force))
    except ValidationError as exc:
        parser.error(str(exc))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
