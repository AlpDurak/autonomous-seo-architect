#!/usr/bin/env python3
"""Validate JSON-LD syntax and basic structured-data hygiene."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

from seo_utils import now_iso, write_json, write_markdown, markdown_table


JSONLD_RE = re.compile(r"<script[^>]+type=[\"']application/ld\+json[\"'][^>]*>(.*?)</script>", re.I | re.S)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate JSON-LD from HTML files or collected SEO evidence.")
    parser.add_argument("--input", action="append", type=Path, required=True, help="HTML or rendered/static SEO JSON. Repeatable.")
    parser.add_argument("--output", type=Path, default=Path(".seo-agent/evidence/structured_data_validation.json"))
    parser.add_argument("--markdown", type=Path, default=Path(".seo-agent/evidence/structured_data_validation.md"))
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    results: list[dict[str, Any]] = []
    for path in args.input:
        results.extend(validate_path(path))
    payload = {"schema_version": 1, "generated_at": now_iso(), "results": results}
    write_json(args.output, payload)
    write_markdown(args.markdown, render_markdown(payload))
    print(f"Wrote {args.output}")
    print(f"Wrote {args.markdown}")
    return 0 if all(not result["errors"] for result in results) else 1


def validate_path(path: Path) -> list[dict[str, Any]]:
    text = path.read_text(encoding="utf-8-sig", errors="replace")
    if path.suffix.lower() == ".json":
        payload = json.loads(text)
        blocks: list[tuple[str, str]] = []
        for result in payload.get("results", []):
            url = result.get("url") or result.get("final_url") or ""
            seo = result.get("seo", {})
            if isinstance(seo, dict) and "seo" in seo:
                seo = seo["seo"]
            for block in seo.get("jsonLd", []) or []:
                blocks.append((url, block))
        return [validate_block(path, url, block, index) for index, (url, block) in enumerate(blocks, start=1)]
    return [validate_block(path, str(path), block, index) for index, block in enumerate(JSONLD_RE.findall(text), start=1)]


def validate_block(path: Path, url: str, block: str, index: int) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    types: list[str] = []
    try:
        parsed = json.loads(block)
    except json.JSONDecodeError as exc:
        return {
            "source": str(path),
            "url": url,
            "block": index,
            "types": [],
            "errors": [f"JSON parse error: {exc}"],
            "warnings": [],
        }
    nodes = flatten_nodes(parsed)
    for node in nodes:
        node_type = node.get("@type")
        if isinstance(node_type, list):
            types.extend(str(value) for value in node_type)
        elif node_type:
            types.append(str(node_type))
        if "@context" not in node and not inherited_context(parsed):
            warnings.append("Missing @context on node or graph root.")
        if "@type" not in node:
            warnings.append("Missing @type on a JSON-LD node.")
        for key in ("url", "image", "sameAs"):
            value = node.get(key)
            if value and not has_absolute_url(value):
                warnings.append(f"{key} should use absolute URLs.")
    return {"source": str(path), "url": url, "block": index, "types": sorted(set(types)), "errors": errors, "warnings": sorted(set(warnings))}


def flatten_nodes(value: Any) -> list[dict[str, Any]]:
    if isinstance(value, list):
        return [node for item in value for node in flatten_nodes(item)]
    if isinstance(value, dict):
        if isinstance(value.get("@graph"), list):
            return [node for node in value["@graph"] if isinstance(node, dict)]
        return [value]
    return []


def inherited_context(value: Any) -> bool:
    return isinstance(value, dict) and "@context" in value


def has_absolute_url(value: Any) -> bool:
    if isinstance(value, str):
        return value.startswith("http://") or value.startswith("https://")
    if isinstance(value, list):
        return all(has_absolute_url(item) for item in value if isinstance(item, str))
    if isinstance(value, dict):
        return has_absolute_url(value.get("url") or value.get("@id") or "")
    return True


def render_markdown(payload: dict[str, Any]) -> str:
    rows = [
        [item["url"], ", ".join(item["types"]), "; ".join(item["errors"]), "; ".join(item["warnings"])]
        for item in payload["results"]
    ]
    return "\n\n".join(["# Structured Data Validation", f"Generated: {payload['generated_at']}", markdown_table(["URL", "Types", "Errors", "Warnings"], rows)])


if __name__ == "__main__":
    raise SystemExit(main())
