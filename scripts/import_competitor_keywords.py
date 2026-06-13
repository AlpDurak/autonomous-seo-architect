#!/usr/bin/env python3
"""Normalize competitor keyword exports and derive basic gap types."""

from __future__ import annotations

import argparse
from collections import defaultdict
from pathlib import Path
from typing import Any

from seo_utils import domain_of, first_value, load_records, now_iso, parse_float, parse_int, write_json, write_markdown, markdown_table


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Normalize competitor keyword exports from common SEO tools.")
    parser.add_argument("--input", action="append", type=Path, required=True, help="Competitor CSV/JSON export. Repeatable.")
    parser.add_argument("--target-domain", required=True, help="The audited domain.")
    parser.add_argument("--target-input", action="append", type=Path, default=[], help="Target-site keyword export. Repeatable.")
    parser.add_argument("--output", type=Path, default=Path(".seo-agent/competitor_keyword_import.json"))
    parser.add_argument("--markdown", type=Path, default=Path("seo_competitor_keyword_analysis.md"))
    parser.add_argument("--source", default="competitor keyword export")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    target_domain = domain_of(args.target_domain)
    competitor_rows = load_keyword_rows(args.input, args.source)
    target_rows = load_keyword_rows(args.target_input, "target keyword export")
    gaps = classify_gaps(competitor_rows, target_rows, target_domain)
    payload = {
        "schema_version": 1,
        "generated_at": now_iso(),
        "target_domain": target_domain,
        "competitor_records": competitor_rows,
        "target_records": target_rows,
        "keyword_gaps": gaps,
    }
    write_json(args.output, payload)
    write_markdown(args.markdown, render_markdown(payload))
    print(f"Wrote {args.output}")
    print(f"Wrote {args.markdown}")
    return 0


def load_keyword_rows(paths: list[Path], source: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for path in paths:
        for record in load_records(path):
            normalized = normalize_keyword_record(record, path, source)
            if normalized:
                rows.append(normalized)
    return rows


def normalize_keyword_record(record: dict[str, Any], path: Path, source: str) -> dict[str, Any] | None:
    keyword = first_value(record, "keyword", "query", "search term", "top keyword")
    url = first_value(record, "url", "page", "landing page", "ranking url", "current url")
    domain = first_value(record, "domain", "competitor", "site", "root domain")
    if not domain and url:
        domain = domain_of(str(url))
    position = parse_float(first_value(record, "position", "rank", "organic position", "current position"))
    volume = parse_int(first_value(record, "volume", "search volume", "sv"))
    difficulty = parse_float(first_value(record, "difficulty", "keyword difficulty", "kd"))
    intent = first_value(record, "intent", "search intent") or ""
    if not keyword:
        return None
    return {
        "keyword": str(keyword).strip(),
        "domain": domain_of(str(domain)) if domain else "",
        "url": str(url or "").strip(),
        "position": position,
        "volume": volume,
        "difficulty": difficulty,
        "intent": str(intent).strip().lower(),
        "source_file": str(path),
        "source": source,
        "confidence": "provided",
    }


def classify_gaps(competitors: list[dict[str, Any]], target: list[dict[str, Any]], target_domain: str) -> list[dict[str, Any]]:
    target_by_keyword: dict[str, list[dict[str, Any]]] = defaultdict(list)
    competitor_by_keyword: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in target:
        target_by_keyword[row["keyword"].lower()].append(row)
    for row in competitors:
        if row.get("domain") != target_domain:
            competitor_by_keyword[row["keyword"].lower()].append(row)

    gaps: list[dict[str, Any]] = []
    for keyword, comp_rows in sorted(competitor_by_keyword.items()):
        target_rows = target_by_keyword.get(keyword, [])
        best_comp = min([r for r in comp_rows if r.get("position") is not None], key=lambda r: r["position"], default=comp_rows[0])
        best_target = min([r for r in target_rows if r.get("position") is not None], key=lambda r: r["position"], default=None)
        if not target_rows:
            gap_type = "missing"
        elif best_target and best_comp.get("position") is not None and best_target.get("position") is not None and best_target["position"] > best_comp["position"]:
            gap_type = "weak"
        elif len({row.get("url") for row in target_rows if row.get("url")}) > 1:
            gap_type = "cannibalized"
        else:
            gap_type = "shared"
        gaps.append(
            {
                "id": f"COMP-DATA-{len(gaps) + 1:03d}",
                "keyword": best_comp["keyword"],
                "gap_type": gap_type,
                "intent": best_comp.get("intent", ""),
                "volume": best_comp.get("volume"),
                "difficulty": best_comp.get("difficulty"),
                "competitors": sorted({row.get("domain", "") for row in comp_rows if row.get("domain")}),
                "competitor_urls": sorted({row.get("url", "") for row in comp_rows if row.get("url")}),
                "target_urls": sorted({row.get("url", "") for row in target_rows if row.get("url")}),
                "best_competitor_position": best_comp.get("position"),
                "best_target_position": best_target.get("position") if best_target else None,
                "confidence": "provided",
            }
        )
    return gaps


def render_markdown(payload: dict[str, Any]) -> str:
    gap_rows = [
        [
            row["id"],
            row["keyword"],
            row["gap_type"],
            ", ".join(row.get("competitors", [])[:3]),
            row.get("best_competitor_position", ""),
            row.get("best_target_position", ""),
            row.get("volume", ""),
            row.get("difficulty", ""),
        ]
        for row in payload["keyword_gaps"][:200]
    ]
    return "\n\n".join(
        [
            "# SEO Competitor Keyword Analysis",
            f"Generated: {payload['generated_at']}",
            f"Target domain: {payload['target_domain']}",
            "## Keyword Gap Matrix",
            markdown_table(["ID", "Keyword", "Gap Type", "Competitors", "Best Competitor", "Best Target", "Volume", "Difficulty"], gap_rows),
            "## Data Requests",
            "| Needed Data | Why It Matters | Acceptable Format |",
            "| --- | --- | --- |",
            "| Target keyword export | Needed to distinguish missing vs weak/shared/cannibalized gaps | CSV/JSON with keyword, URL, position |",
        ]
    )


if __name__ == "__main__":
    raise SystemExit(main())
