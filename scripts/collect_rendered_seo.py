#!/usr/bin/env python3
"""Collect rendered SEO evidence with Vercel agent-browser."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from seo_utils import load_urls, now_iso, write_json


SEO_EXTRACTION_JS = r"""
JSON.stringify({
  url: location.href,
  title: document.title || null,
  metaDescription: document.querySelector('meta[name="description"]')?.content || null,
  robots: document.querySelector('meta[name="robots"]')?.content || null,
  canonical: document.querySelector('link[rel="canonical"]')?.href || null,
  canonicalCount: document.querySelectorAll('link[rel="canonical"]').length,
  hreflang: Array.from(document.querySelectorAll('link[rel="alternate"][hreflang]')).map(e => ({
    hreflang: e.getAttribute('hreflang'),
    href: e.href
  })),
  h1: Array.from(document.querySelectorAll('h1')).map(e => e.innerText.trim()).filter(Boolean),
  headings: Array.from(document.querySelectorAll('h1,h2,h3')).map(e => ({
    tag: e.tagName.toLowerCase(),
    text: e.innerText.trim()
  })).filter(e => e.text),
  images: Array.from(document.images).map(img => ({
    src: img.currentSrc || img.src,
    alt: img.getAttribute('alt'),
    loading: img.loading || '',
    fetchPriority: img.fetchPriority || '',
    width: img.width,
    height: img.height,
    naturalWidth: img.naturalWidth,
    naturalHeight: img.naturalHeight,
    hasExplicitSize: img.hasAttribute('width') && img.hasAttribute('height')
  })),
  internalLinks: Array.from(document.querySelectorAll('a[href]')).map(a => ({
    text: a.innerText.trim(),
    href: a.href
  })).filter(a => a.href.startsWith(location.origin)),
  externalLinks: Array.from(document.querySelectorAll('a[href]')).map(a => ({
    text: a.innerText.trim(),
    href: a.href
  })).filter(a => !a.href.startsWith(location.origin)),
  jsonLd: Array.from(document.querySelectorAll('script[type="application/ld+json"]')).map(s => s.textContent.trim())
}, null, 2)
"""


PERF_EXTRACTION_JS = r"""
JSON.stringify({
  navigation: (() => {
    const nav = performance.getEntriesByType('navigation')[0]
    if (!nav) return null
    return {
      type: nav.type,
      transferSize: nav.transferSize,
      encodedBodySize: nav.encodedBodySize,
      domContentLoadedMs: Math.round(nav.domContentLoadedEventEnd),
      loadEventMs: Math.round(nav.loadEventEnd),
      ttfbMs: Math.round(nav.responseStart - nav.requestStart)
    }
  })(),
  resources: performance.getEntriesByType('resource').map(r => ({
    name: r.name,
    initiatorType: r.initiatorType,
    durationMs: Math.round(r.duration),
    transferSize: r.transferSize || 0,
    renderBlockingStatus: r.renderBlockingStatus || 'unknown'
  })).sort((a, b) => b.durationMs - a.durationMs).slice(0, 50),
  scripts: Array.from(document.scripts).map(s => ({
    src: s.src || '[inline]',
    async: s.async,
    defer: s.defer,
    type: s.type || 'classic'
  })),
  stylesheets: Array.from(document.querySelectorAll('link[rel="stylesheet"]')).map(l => l.href),
  preloads: Array.from(document.querySelectorAll('link[rel="preload"],link[rel="preconnect"],link[rel="dns-prefetch"]')).map(l => ({
    rel: l.rel,
    as: l.as || '',
    href: l.href
  }))
}, null, 2)
"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Collect rendered SEO evidence using agent-browser.")
    parser.add_argument("--url", action="append", default=[], help="URL to inspect. Repeatable.")
    parser.add_argument("--urls-file", action="append", type=Path, default=[], help="Text file with one URL per line.")
    parser.add_argument("--output", type=Path, default=Path(".seo-agent/evidence/rendered_seo.json"))
    parser.add_argument("--snapshot-dir", type=Path, default=Path(".seo-agent/evidence/snapshots"))
    parser.add_argument("--skip-vitals", action="store_true", help="Skip agent-browser vitals calls.")
    parser.add_argument("--keep-open", action="store_true", help="Do not close agent-browser at the end.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    urls = load_urls(args.url, args.urls_file)
    if not urls:
        print("error: provide at least one --url or --urls-file entry", file=sys.stderr)
        return 2

    results: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []
    args.snapshot_dir.mkdir(parents=True, exist_ok=True)

    try:
        for index, url in enumerate(urls, start=1):
            try:
                run_agent(["open", url])
                run_agent(["wait", "--load", "networkidle"])
                snapshot_text = run_agent(["snapshot", "-i"])
                seo = eval_json(SEO_EXTRACTION_JS)
                perf = eval_json(PERF_EXTRACTION_JS)
                vitals = None if args.skip_vitals else run_agent(["vitals", url], allow_failure=True)
                snapshot_path = args.snapshot_dir / f"rendered-{index:03d}.txt"
                snapshot_path.write_text(snapshot_text, encoding="utf-8")
                results.append(
                    {
                        "url": url,
                        "collected_at": now_iso(),
                        "snapshot_path": str(snapshot_path),
                        "seo": seo,
                        "performance": perf,
                        "agent_browser_vitals": vitals,
                    }
                )
            except Exception as exc:  # noqa: BLE001 - collector should continue across URLs.
                errors.append({"url": url, "error": str(exc)})
    finally:
        if not args.keep_open:
            run_agent(["close"], allow_failure=True)

    write_json(
        args.output,
        {
            "schema_version": 1,
            "generated_at": now_iso(),
            "tool": "agent-browser",
            "results": results,
            "errors": errors,
        },
    )
    print(f"Wrote {args.output}")
    return 0 if not errors else 1


def run_agent(args: list[str], *, allow_failure: bool = False) -> str:
    completed = subprocess.run(["agent-browser", *args], text=True, capture_output=True, check=False)
    if completed.returncode != 0 and not allow_failure:
        raise RuntimeError(completed.stderr.strip() or completed.stdout.strip() or f"agent-browser {' '.join(args)} failed")
    return completed.stdout.strip()


def eval_json(script: str) -> Any:
    completed = subprocess.run(["agent-browser", "eval", "--stdin"], input=script, text=True, capture_output=True, check=False)
    if completed.returncode != 0:
        raise RuntimeError(completed.stderr.strip() or completed.stdout.strip() or "agent-browser eval failed")
    raw = completed.stdout.strip()
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {"raw": raw}


if __name__ == "__main__":
    raise SystemExit(main())
