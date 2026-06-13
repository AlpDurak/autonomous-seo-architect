#!/usr/bin/env python3
"""Analyze web server logs for SEO crawl-budget and Googlebot signals."""

from __future__ import annotations

import argparse
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from seo_utils import now_iso, write_json, write_markdown, markdown_table


COMBINED_RE = re.compile(
    r'(?P<ip>\S+) \S+ \S+ \[(?P<time>[^\]]+)\] "(?P<method>\S+) (?P<path>\S+) (?P<protocol>[^"]+)" (?P<status>\d{3}) (?P<size>\S+) "(?P<referer>[^"]*)" "(?P<ua>[^"]*)"'
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Analyze server logs for SEO crawl signals.")
    parser.add_argument("--input", action="append", type=Path, required=True, help="Access log file. Repeatable.")
    parser.add_argument("--output", type=Path, default=Path(".seo-agent/evidence/server_log_analysis.json"))
    parser.add_argument("--markdown", type=Path, default=Path(".seo-agent/evidence/server_log_analysis.md"))
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    records = []
    for path in args.input:
        records.extend(parse_log(path))
    analysis = analyze(records)
    payload = {"schema_version": 1, "generated_at": now_iso(), "records_analyzed": len(records), **analysis}
    write_json(args.output, payload)
    write_markdown(args.markdown, render_markdown(payload))
    print(f"Wrote {args.output}")
    print(f"Wrote {args.markdown}")
    return 0


def parse_log(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        match = COMBINED_RE.search(line)
        if not match:
            continue
        data = match.groupdict()
        data["status"] = int(data["status"])
        data["source_file"] = str(path)
        data["is_googlebot"] = "googlebot" in data["ua"].lower()
        data["is_other_bot"] = "bot" in data["ua"].lower() or "crawler" in data["ua"].lower() or "spider" in data["ua"].lower()
        rows.append(data)
    return rows


def analyze(records: list[dict[str, Any]]) -> dict[str, Any]:
    status_counts = Counter(str(row["status"]) for row in records)
    googlebot = [row for row in records if row["is_googlebot"]]
    google_status = Counter(str(row["status"]) for row in googlebot)
    google_paths = Counter(row["path"] for row in googlebot)
    waste_paths = [
        {"path": path, "hits": hits}
        for path, hits in google_paths.most_common(100)
        if any(marker in path.lower() for marker in ("?", "sort=", "filter=", "session", "utm_", "/search"))
    ]
    error_paths: dict[str, Counter[str]] = defaultdict(Counter)
    for row in googlebot:
        if row["status"] >= 300:
            error_paths[str(row["status"])][row["path"]] += 1
    return {
        "summary": {
            "total_requests": len(records),
            "googlebot_requests": len(googlebot),
            "bot_requests": sum(1 for row in records if row["is_other_bot"]),
            "status_counts": dict(status_counts),
            "googlebot_status_counts": dict(google_status),
        },
        "googlebot_top_paths": [{"path": path, "hits": hits} for path, hits in google_paths.most_common(100)],
        "crawl_waste_candidates": waste_paths,
        "googlebot_error_paths": {
            status: [{"path": path, "hits": hits} for path, hits in counter.most_common(50)]
            for status, counter in error_paths.items()
        },
    }


def render_markdown(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    waste_rows = [[item["path"], item["hits"]] for item in payload["crawl_waste_candidates"][:50]]
    top_rows = [[item["path"], item["hits"]] for item in payload["googlebot_top_paths"][:50]]
    return "\n\n".join(
        [
            "# Server Log SEO Analysis",
            f"Generated: {payload['generated_at']}",
            f"Records analyzed: {payload['records_analyzed']}",
            f"Summary: {summary}",
            "## Googlebot Top Paths",
            markdown_table(["Path", "Hits"], top_rows),
            "## Crawl Waste Candidates",
            markdown_table(["Path", "Hits"], waste_rows),
        ]
    )


if __name__ == "__main__":
    raise SystemExit(main())
