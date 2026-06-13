#!/usr/bin/env python3
"""Collect optional PageSpeed Insights and CrUX evidence for public URLs."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from seo_utils import load_urls, now_iso, write_json


PSI_ENDPOINT = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"
CRUX_ENDPOINT = "https://chromeuxreport.googleapis.com/v1/records:queryRecord"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Collect PageSpeed Insights and CrUX metrics.")
    parser.add_argument("--url", action="append", default=[], help="Public URL. Repeatable.")
    parser.add_argument("--urls-file", action="append", type=Path, default=[])
    parser.add_argument("--strategy", choices=("mobile", "desktop", "both"), default="mobile")
    parser.add_argument("--psi-key", default=os.environ.get("PSI_API_KEY", ""))
    parser.add_argument("--crux-key", default=os.environ.get("CRUX_API_KEY", ""))
    parser.add_argument("--skip-psi", action="store_true")
    parser.add_argument("--skip-crux", action="store_true")
    parser.add_argument("--output", type=Path, default=Path(".seo-agent/evidence/pagespeed_crux.json"))
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    urls = load_urls(args.url, args.urls_file)
    if not urls:
        print("error: provide --url or --urls-file", file=sys.stderr)
        return 2
    strategies = ["mobile", "desktop"] if args.strategy == "both" else [args.strategy]
    results: list[dict[str, Any]] = []
    for url in urls:
        item: dict[str, Any] = {"url": url, "collected_at": now_iso(), "pagespeed": {}, "crux": None, "errors": []}
        if not args.skip_psi:
            for strategy in strategies:
                try:
                    item["pagespeed"][strategy] = collect_psi(url, strategy, args.psi_key)
                except Exception as exc:  # noqa: BLE001
                    item["errors"].append({"tool": "pagespeed", "strategy": strategy, "error": str(exc)})
        if not args.skip_crux:
            if args.crux_key:
                try:
                    item["crux"] = collect_crux(url, args.crux_key)
                except Exception as exc:  # noqa: BLE001
                    item["errors"].append({"tool": "crux", "error": str(exc)})
            else:
                item["errors"].append({"tool": "crux", "error": "CRUX_API_KEY is required for CrUX API"})
        results.append(item)
    write_json(args.output, {"schema_version": 1, "generated_at": now_iso(), "results": results})
    print(f"Wrote {args.output}")
    return 0


def collect_psi(url: str, strategy: str, key: str) -> dict[str, Any]:
    params = {"url": url, "strategy": strategy, "category": "performance"}
    if key:
        params["key"] = key
    raw = http_json(f"{PSI_ENDPOINT}?{urlencode(params)}")
    lighthouse = raw.get("lighthouseResult", {})
    audits = lighthouse.get("audits", {})
    return {
        "strategy": strategy,
        "performance_score": score(lighthouse.get("categories", {}).get("performance", {}).get("score")),
        "metrics": {
            "lcp_ms": numeric_value(audits, "largest-contentful-paint"),
            "cls": numeric_value(audits, "cumulative-layout-shift"),
            "tbt_ms": numeric_value(audits, "total-blocking-time"),
            "fcp_ms": numeric_value(audits, "first-contentful-paint"),
            "speed_index_ms": numeric_value(audits, "speed-index"),
        },
        "opportunities": extract_opportunities(audits),
        "raw_id": raw.get("id"),
    }


def collect_crux(url: str, key: str) -> dict[str, Any]:
    request = Request(
        f"{CRUX_ENDPOINT}?key={key}",
        data=json.dumps({"url": url}).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urlopen(request, timeout=30) as response:
        raw = json.loads(response.read().decode("utf-8"))
    metrics = raw.get("record", {}).get("metrics", {})
    return {
        "metrics": {
            name: metric.get("percentiles") or metric.get("histogram")
            for name, metric in metrics.items()
        },
        "collectionPeriod": raw.get("record", {}).get("collectionPeriod"),
    }


def http_json(url: str) -> dict[str, Any]:
    with urlopen(Request(url, headers={"User-Agent": "AutonomousSEOArchitect/0.1"}), timeout=60) as response:
        return json.loads(response.read().decode("utf-8"))


def score(value: Any) -> int | None:
    if isinstance(value, (int, float)):
        return int(round(value * 100))
    return None


def numeric_value(audits: dict[str, Any], key: str) -> Any:
    return audits.get(key, {}).get("numericValue")


def extract_opportunities(audits: dict[str, Any]) -> list[dict[str, Any]]:
    opportunities: list[dict[str, Any]] = []
    for key, audit in audits.items():
        details = audit.get("details", {})
        if details.get("type") == "opportunity" or audit.get("scoreDisplayMode") == "metricSavings":
            opportunities.append(
                {
                    "id": key,
                    "title": audit.get("title"),
                    "description": audit.get("description"),
                    "score": audit.get("score"),
                    "numericValue": audit.get("numericValue"),
                }
            )
    return opportunities


if __name__ == "__main__":
    raise SystemExit(main())
