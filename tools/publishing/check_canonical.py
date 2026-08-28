from __future__ import annotations

import argparse
import urllib.error
import urllib.request
from html.parser import HTMLParser
from urllib.parse import urlparse


class CanonicalParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.values: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = {key.casefold(): value for key, value in attrs}
        rel = set((values.get("rel") or "").casefold().split())
        href = values.get("href")
        if tag.casefold() == "link" and "canonical" in rel and href:
            self.values.append(href)


def canonical_from_html(html: str) -> str | None:
    parser = CanonicalParser()
    parser.feed(html)
    return parser.values[0] if len(parser.values) == 1 else None


def check(url: str, expected: str) -> bool:
    for value in (url, expected):
        parsed = urlparse(value)
        if parsed.scheme != "https" or not parsed.netloc:
            return False
    request = urllib.request.Request(url, headers={"User-Agent": "puckworks-canonical-check/1"})
    with urllib.request.urlopen(request, timeout=20) as response:
        content_type = response.headers.get_content_type()
        if response.status != 200 or content_type not in {"text/html", "application/xhtml+xml"}:
            return False
        html = response.read(2_000_001)
        if len(html) > 2_000_000:
            return False
        html = html.decode(response.headers.get_content_charset() or "utf-8", errors="replace")
    return canonical_from_html(html) == expected


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("url")
    parser.add_argument("--expected", required=True)
    args = parser.parse_args()
    try:
        ok = check(args.url, args.expected)
    except (urllib.error.URLError, TimeoutError, UnicodeError, ValueError) as exc:
        print(f"FAIL: canonical check could not complete: {exc}")
        return 1
    print("PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
