#!/usr/bin/env python3
"""Collect static HTTP/HTML SEO evidence and lightweight crawl signals."""

from __future__ import annotations

import argparse
import json
import re
import sys
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from seo_utils import load_urls, normalize_url, now_iso, same_origin, write_json


class SEOHTMLParser(HTMLParser):
    def __init__(self, base_url: str) -> None:
        super().__init__(convert_charrefs=True)
        self.base_url = base_url
        self.stack: list[str] = []
        self.title_parts: list[str] = []
        self.current_heading: str | None = None
        self.current_anchor: dict[str, str] | None = None
        self.headings: list[dict[str, str]] = []
        self.links: list[dict[str, str]] = []
        self.images: list[dict[str, str]] = []
        self.meta: list[dict[str, str]] = []
        self.canonicals: list[str] = []
        self.json_ld: list[str] = []
        self._json_ld_active = False
        self._json_ld_parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr = {k.lower(): v or "" for k, v in attrs}
        self.stack.append(tag)
        if tag == "meta":
            self.meta.append(attr)
        elif tag == "link" and attr.get("rel", "").lower() == "canonical":
            self.canonicals.append(normalize_url(attr.get("href", ""), self.base_url))
        elif tag in {"h1", "h2", "h3"}:
            self.current_heading = tag
            self._heading_parts: list[str] = []
        elif tag == "a" and attr.get("href"):
            self.current_anchor = {"href": normalize_url(attr["href"], self.base_url), "text": ""}
            self._anchor_parts: list[str] = []
        elif tag == "img":
            self.images.append(
                {
                    "src": normalize_url(attr.get("src", ""), self.base_url),
                    "alt": attr.get("alt", ""),
                    "width": attr.get("width", ""),
                    "height": attr.get("height", ""),
                    "loading": attr.get("loading", ""),
                }
            )
        elif tag == "script" and attr.get("type", "").lower() == "application/ld+json":
            self._json_ld_active = True
            self._json_ld_parts = []

    def handle_endtag(self, tag: str) -> None:
        if tag == "title":
            pass
        if self.current_heading == tag:
            text = " ".join("".join(self._heading_parts).split())
            if text:
                self.headings.append({"tag": tag, "text": text})
            self.current_heading = None
        if tag == "a" and self.current_anchor is not None:
            self.current_anchor["text"] = " ".join("".join(self._anchor_parts).split())
            if self.current_anchor["href"]:
                self.links.append(self.current_anchor)
            self.current_anchor = None
        if tag == "script" and self._json_ld_active:
            text = "".join(self._json_ld_parts).strip()
            if text:
                self.json_ld.append(text)
            self._json_ld_active = False
        if self.stack:
            self.stack.pop()

    def handle_data(self, data: str) -> None:
        if not self.stack:
            return
        tag = self.stack[-1]
        if tag == "title":
            self.title_parts.append(data)
        if self.current_heading:
            self._heading_parts.append(data)
        if self.current_anchor is not None:
            self._anchor_parts.append(data)
        if self._json_ld_active:
            self._json_ld_parts.append(data)

    def result(self) -> dict[str, Any]:
        description = None
        robots = None
        for meta in self.meta:
            name = meta.get("name", "").lower()
            prop = meta.get("property", "").lower()
            if name == "description":
                description = meta.get("content", "")
            if name == "robots":
                robots = meta.get("content", "")
            if prop.startswith("og:"):
                pass
        internal_links = [link for link in self.links if same_origin(self.base_url, link["href"])]
        external_links = [link for link in self.links if link["href"] and not same_origin(self.base_url, link["href"])]
        return {
            "title": " ".join("".join(self.title_parts).split()) or None,
            "metaDescription": description,
            "robots": robots,
            "canonical": self.canonicals[0] if self.canonicals else None,
            "canonicalCount": len([value for value in self.canonicals if value]),
            "h1": [h["text"] for h in self.headings if h["tag"] == "h1"],
            "headings": self.headings,
            "images": self.images,
            "imagesMissingAlt": [img["src"] for img in self.images if not img.get("alt")],
            "internalLinks": internal_links,
            "externalLinks": external_links,
            "jsonLd": self.json_ld,
        }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Collect static SEO evidence from URLs.")
    parser.add_argument("--url", action="append", default=[], help="URL to inspect. Repeatable.")
    parser.add_argument("--urls-file", action="append", type=Path, default=[])
    parser.add_argument("--sitemap", action="append", default=[], help="Sitemap URL or local sitemap XML path.")
    parser.add_argument("--crawl-depth", type=int, default=0, help="Follow internal links up to this depth.")
    parser.add_argument("--max-urls", type=int, default=100)
    parser.add_argument("--output", type=Path, default=Path(".seo-agent/evidence/static_crawl.json"))
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    seeds = load_urls(args.url, args.urls_file)
    seeds.extend(load_sitemap_urls(args.sitemap))
    queue = [(url, 0) for url in dict.fromkeys(seeds)]
    seen: set[str] = set()
    results: list[dict[str, Any]] = []

    while queue and len(seen) < args.max_urls:
        url, depth = queue.pop(0)
        if url in seen:
            continue
        seen.add(url)
        evidence = fetch_and_parse(url)
        evidence["depth"] = depth
        results.append(evidence)
        if args.crawl_depth > 0 and depth < args.crawl_depth:
            for link in evidence.get("seo", {}).get("internalLinks", []):
                href = link.get("href", "")
                if href and href not in seen and len(queue) + len(seen) < args.max_urls:
                    queue.append((href, depth + 1))

    payload = {
        "schema_version": 1,
        "generated_at": now_iso(),
        "results": results,
        "duplicates": duplicate_signals(results),
    }
    write_json(args.output, payload)
    print(f"Wrote {args.output}")
    return 0 if results else 1


def load_sitemap_urls(values: list[str]) -> list[str]:
    urls: list[str] = []
    for value in values:
        try:
            if "://" not in value and Path(value).is_file():
                raw = Path(value).read_text(encoding="utf-8")
            else:
                raw = urlopen(Request(value, headers={"User-Agent": "AutonomousSEOArchitect/0.1"}), timeout=20).read().decode("utf-8", "replace")
            root = ET.fromstring(raw)
            for element in root.iter():
                if element.tag.endswith("loc") and element.text:
                    normalized = normalize_url(element.text.strip())
                    if normalized:
                        urls.append(normalized)
        except Exception as exc:  # noqa: BLE001
            print(f"warning: could not parse sitemap {value}: {exc}", file=sys.stderr)
    return urls


def fetch_and_parse(url: str) -> dict[str, Any]:
    request = Request(url, headers={"User-Agent": "AutonomousSEOArchitect/0.1"})
    status = None
    final_url = url
    html = ""
    headers: dict[str, str] = {}
    error = None
    try:
        with urlopen(request, timeout=20) as response:
            status = response.status
            final_url = response.geturl()
            headers = {k.lower(): v for k, v in response.headers.items()}
            content_type = headers.get("content-type", "")
            raw = response.read(5_000_000)
            if "html" in content_type or raw.lstrip().startswith(b"<!") or raw.lstrip().startswith(b"<html"):
                html = raw.decode(detect_charset(content_type), "replace")
    except HTTPError as exc:
        status = exc.code
        headers = {k.lower(): v for k, v in exc.headers.items()}
        error = str(exc)
    except URLError as exc:
        error = str(exc)

    seo: dict[str, Any] = {}
    if html:
        parser = SEOHTMLParser(final_url)
        parser.feed(html)
        seo = parser.result()
    return {
        "url": url,
        "final_url": final_url,
        "status": status,
        "headers": headers,
        "error": error,
        "seo": seo,
    }


def detect_charset(content_type: str) -> str:
    match = re.search(r"charset=([^;\s]+)", content_type, re.I)
    return match.group(1) if match else "utf-8"


def duplicate_signals(results: list[dict[str, Any]]) -> dict[str, Any]:
    buckets: dict[str, dict[str, list[str]]] = {"title": {}, "metaDescription": {}, "canonical": {}}
    for result in results:
        url = result.get("url", "")
        seo = result.get("seo", {})
        for key in buckets:
            value = (seo.get(key) or "").strip()
            if value:
                buckets[key].setdefault(value, []).append(url)
    return {
        key: {value: urls for value, urls in values.items() if len(urls) > 1}
        for key, values in buckets.items()
    }


if __name__ == "__main__":
    raise SystemExit(main())
