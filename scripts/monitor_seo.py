#!/usr/bin/env python3
"""Create and compare lightweight SEO monitoring snapshots."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from seo_utils import now_iso, read_json, write_json, write_markdown, markdown_table


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create or compare SEO monitoring snapshots.")
    parser.add_argument("--config", type=Path, default=Path("configs/monitoring.example.json"))
    parser.add_argument("--rendered", type=Path, default=Path(".seo-agent/evidence/rendered_seo.json"))
    parser.add_argument("--static", type=Path, default=Path(".seo-agent/evidence/static_crawl.json"))
    parser.add_argument("--pagespeed", type=Path, default=Path(".seo-agent/evidence/pagespeed_crux.json"))
    parser.add_argument("--structured-data", type=Path, default=Path(".seo-agent/evidence/structured_data_validation.json"))
    parser.add_argument("--previous", type=Path, default=None)
    parser.add_argument("--output", type=Path, default=Path(".seo-agent/monitoring_snapshot.json"))
    parser.add_argument("--markdown", type=Path, default=Path(".seo-agent/monitoring_report.md"))
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    snapshot = {
        "schema_version": 1,
        "generated_at": now_iso(),
        "config": read_json(args.config, {}),
        "signals": {
            "rendered": summarize_rendered(read_json(args.rendered, {})),
            "static": summarize_static(read_json(args.static, {})),
            "pagespeed": summarize_pagespeed(read_json(args.pagespeed, {})),
            "structured_data": summarize_structured(read_json(args.structured_data, {})),
        },
        "deltas": {},
    }
    if args.previous and args.previous.is_file():
        snapshot["deltas"] = compare(snapshot, read_json(args.previous, {}))
    write_json(args.output, snapshot)
    write_markdown(args.markdown, render_markdown(snapshot))
    print(f"Wrote {args.output}")
    print(f"Wrote {args.markdown}")
    return 0


def summarize_rendered(payload: dict[str, Any]) -> dict[str, Any]:
    results = payload.get("results", [])
    return {
        "url_count": len(results),
        "missing_title": count(results, lambda r: not nested(r, "seo", "title")),
        "missing_meta_description": count(results, lambda r: not nested(r, "seo", "metaDescription")),
        "missing_canonical": count(results, lambda r: not nested(r, "seo", "canonical")),
        "h1_issues": count(results, lambda r: len(nested(r, "seo", "h1") or []) != 1),
    }


def summarize_static(payload: dict[str, Any]) -> dict[str, Any]:
    results = payload.get("results", [])
    return {
        "url_count": len(results),
        "non_200": count(results, lambda r: r.get("status") != 200),
        "duplicate_titles": len(payload.get("duplicates", {}).get("title", {})),
        "duplicate_meta_descriptions": len(payload.get("duplicates", {}).get("metaDescription", {})),
    }


def summarize_pagespeed(payload: dict[str, Any]) -> dict[str, Any]:
    scores = []
    for result in payload.get("results", []):
        for strategy in result.get("pagespeed", {}).values():
            if strategy.get("performance_score") is not None:
                scores.append(strategy["performance_score"])
    return {"url_count": len(payload.get("results", [])), "avg_performance_score": round(sum(scores) / len(scores), 1) if scores else None}


def summarize_structured(payload: dict[str, Any]) -> dict[str, Any]:
    results = payload.get("results", [])
    return {
        "block_count": len(results),
        "error_count": sum(len(item.get("errors", [])) for item in results),
        "warning_count": sum(len(item.get("warnings", [])) for item in results),
    }


def compare(current: dict[str, Any], previous: dict[str, Any]) -> dict[str, Any]:
    deltas: dict[str, Any] = {}
    for group, signals in current.get("signals", {}).items():
        prior = previous.get("signals", {}).get(group, {})
        deltas[group] = {
            key: value - prior.get(key, 0)
            for key, value in signals.items()
            if isinstance(value, (int, float)) and isinstance(prior.get(key, 0), (int, float))
        }
    return deltas


def count(items: list[Any], predicate: Any) -> int:
    return sum(1 for item in items if predicate(item))


def nested(value: dict[str, Any], *keys: str) -> Any:
    current: Any = value
    for key in keys:
        if not isinstance(current, dict):
            return None
        current = current.get(key)
    return current


def render_markdown(snapshot: dict[str, Any]) -> str:
    rows = []
    for group, signals in snapshot["signals"].items():
        for key, value in signals.items():
            rows.append([group, key, value, snapshot.get("deltas", {}).get(group, {}).get(key, "")])
    return "\n\n".join(
        [
            "# SEO Monitoring Report",
            f"Generated: {snapshot['generated_at']}",
            markdown_table(["Group", "Signal", "Value", "Delta"], rows),
        ]
    )


if __name__ == "__main__":
    raise SystemExit(main())
