#!/usr/bin/env python3
"""Normalize Google Search Console exports for SEO opportunity mining."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from seo_utils import first_value, load_records, now_iso, parse_float, parse_int, write_json, write_markdown, markdown_table


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Normalize Google Search Console CSV/JSON exports.")
    parser.add_argument("--input", action="append", type=Path, required=True, help="GSC CSV/JSON export. Repeatable.")
    parser.add_argument("--output", type=Path, default=Path(".seo-agent/search_console_import.json"))
    parser.add_argument("--markdown", type=Path, default=Path(".seo-agent/search_console_import.md"))
    parser.add_argument("--source", default="Google Search Console export")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    rows: list[dict[str, Any]] = []
    for path in args.input:
        for record in load_records(path):
            normalized = normalize_gsc_record(record, path, args.source)
            if normalized:
                rows.append(normalized)

    opportunities = classify(rows)
    payload = {
        "schema_version": 1,
        "generated_at": now_iso(),
        "source": args.source,
        "records": rows,
        "opportunities": opportunities,
    }
    write_json(args.output, payload)
    write_markdown(args.markdown, render_markdown(payload))
    print(f"Wrote {args.output}")
    print(f"Wrote {args.markdown}")
    return 0


def normalize_gsc_record(record: dict[str, Any], path: Path, source: str) -> dict[str, Any] | None:
    query = first_value(record, "query", "top queries", "search query", "keyword")
    page = first_value(record, "page", "url", "landing page", "pages")
    clicks = parse_int(first_value(record, "clicks"))
    impressions = parse_int(first_value(record, "impressions"))
    ctr = parse_float(first_value(record, "ctr", "click through rate", "click-through rate"))
    position = parse_float(first_value(record, "position", "avg position", "average position"))
    if not any([query, page, clicks is not None, impressions is not None, ctr is not None, position is not None]):
        return None
    if ctr is not None and ctr > 1:
        ctr = ctr / 100.0
    return {
        "query": query or "",
        "page": page or "",
        "clicks": clicks,
        "impressions": impressions,
        "ctr": ctr,
        "position": position,
        "device": first_value(record, "device") or "",
        "country": first_value(record, "country") or "",
        "date": first_value(record, "date") or "",
        "source_file": str(path),
        "source": source,
        "confidence": "provided",
    }


def classify(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    opportunities: list[dict[str, Any]] = []
    for index, row in enumerate(rows, start=1):
        impressions = row.get("impressions") or 0
        clicks = row.get("clicks") or 0
        ctr = row.get("ctr")
        position = row.get("position")
        tags: list[str] = []
        if impressions >= 100 and (ctr is not None and ctr < 0.02):
            tags.append("high_impression_low_ctr")
        if position is not None and 4 <= position <= 20:
            tags.append("striking_distance")
        if impressions >= 100 and clicks == 0:
            tags.append("zero_click")
        if row.get("query") and row.get("page") and position is not None and position > 20:
            tags.append("page_query_mismatch_candidate")
        for tag in tags:
            opportunities.append(
                {
                    "id": f"GSC-DATA-{len(opportunities) + 1:03d}",
                    "type": tag,
                    "query": row.get("query", ""),
                    "page": row.get("page", ""),
                    "clicks": clicks,
                    "impressions": impressions,
                    "ctr": ctr,
                    "position": position,
                    "source_record": index,
                    "confidence": "provided",
                }
            )
    return opportunities


def render_markdown(payload: dict[str, Any]) -> str:
    rows = [
        [
            item["id"],
            item["type"],
            item.get("query", ""),
            item.get("page", ""),
            item.get("impressions", ""),
            item.get("ctr", ""),
            item.get("position", ""),
        ]
        for item in payload["opportunities"][:100]
    ]
    return "\n\n".join(
        [
            "# Search Console Import",
            f"Generated: {payload['generated_at']}",
            markdown_table(["ID", "Type", "Query", "Page", "Impressions", "CTR", "Position"], rows),
        ]
    )


if __name__ == "__main__":
    raise SystemExit(main())
