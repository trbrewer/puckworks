from __future__ import annotations

import argparse
import re
import urllib.request


def canonical_from_html(html: str) -> str | None:
    match = re.search(r'<link[^>]+rel=["\']canonical["\'][^>]+href=["\']([^"\']+)', html, re.I)
    if not match:
        match = re.search(r'<link[^>]+href=["\']([^"\']+)["\'][^>]+rel=["\']canonical["\']', html, re.I)
    return match.group(1) if match else None


def check(url: str, expected: str) -> bool:
    request = urllib.request.Request(url, headers={"User-Agent": "puckworks-canonical-check/1"})
    with urllib.request.urlopen(request, timeout=20) as response:
        html = response.read().decode("utf-8", errors="replace")
    return canonical_from_html(html) == expected


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("url")
    parser.add_argument("--expected", required=True)
    args = parser.parse_args()
    ok = check(args.url, args.expected)
    print("PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
