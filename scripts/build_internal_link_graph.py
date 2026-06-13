#!/usr/bin/env python3
"""Build an internal link graph from collected SEO evidence."""

from __future__ import annotations

import argparse
from collections import Counter, deque
from pathlib import Path
from typing import Any

from seo_utils import normalize_url, now_iso, same_origin, write_json, write_markdown, markdown_table
from seo_utils import read_json


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build internal link graph from rendered/static SEO evidence JSON.")
    parser.add_argument("--input", action="append", type=Path, required=True, help="rendered_seo.json or static_crawl.json. Repeatable.")
    parser.add_argument("--home-url", required=True)
    parser.add_argument("--output", type=Path, default=Path(".seo-agent/internal_link_graph.json"))
    parser.add_argument("--markdown", type=Path, default=Path(".seo-agent/internal_link_graph.md"))
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    home_url = normalize_url(args.home_url)
    pages = load_pages(args.input, home_url)
    graph = build_graph(pages, home_url)
    write_json(args.output, graph)
    write_markdown(args.markdown, render_markdown(graph))
    print(f"Wrote {args.output}")
    print(f"Wrote {args.markdown}")
    return 0


def load_pages(paths: list[Path], home_url: str) -> dict[str, dict[str, Any]]:
    pages: dict[str, dict[str, Any]] = {}
    for path in paths:
        payload = read_json(path, {})
        for result in payload.get("results", []):
            url = normalize_url(result.get("url") or result.get("final_url") or result.get("seo", {}).get("url") or "")
            if not url:
                continue
            seo = result.get("seo", {})
            if "seo" in seo:
                seo = seo["seo"]
            links = seo.get("internalLinks", []) or []
            normalized_links = []
            for link in links:
                href = normalize_url(link.get("href", ""), url)
                if href and same_origin(home_url, href):
                    normalized_links.append({"href": href, "text": link.get("text", "")})
            pages[url] = {
                "url": url,
                "title": seo.get("title"),
                "h1": seo.get("h1", []),
                "links": normalized_links,
            }
    return pages


def build_graph(pages: dict[str, dict[str, Any]], home_url: str) -> dict[str, Any]:
    all_urls = set(pages)
    for page in pages.values():
        for link in page["links"]:
            all_urls.add(link["href"])

    inbound: dict[str, list[dict[str, str]]] = {url: [] for url in all_urls}
    outbound: dict[str, list[dict[str, str]]] = {url: [] for url in all_urls}
    anchors: dict[str, Counter[str]] = {url: Counter() for url in all_urls}
    for source, page in pages.items():
        for link in page["links"]:
            target = link["href"]
            outbound.setdefault(source, []).append({"href": target, "text": link.get("text", "")})
            inbound.setdefault(target, []).append({"href": source, "text": link.get("text", "")})
            if link.get("text"):
                anchors[target][link["text"].lower()] += 1

    depth = compute_depth(home_url, outbound)
    nodes = []
    for url in sorted(all_urls):
        in_count = len(inbound.get(url, []))
        out_count = len(outbound.get(url, []))
        node_depth = depth.get(url)
        anchor_count = len(anchors.get(url, {}))
        orphan = url != home_url and in_count == 0
        excessive_depth = node_depth is None or node_depth > 3
        link_count_excess = out_count > 150
        score = 100
        if orphan:
            score -= 45
        if excessive_depth:
            score -= 25
        if anchor_count <= 1 and in_count > 3:
            score -= 10
        if link_count_excess:
            score -= 10
        nodes.append(
            {
                "url": url,
                "inbound_count": in_count,
                "outbound_count": out_count,
                "click_depth": node_depth,
                "anchor_diversity": anchor_count,
                "orphan": orphan,
                "excessive_depth": excessive_depth,
                "link_count_excess": link_count_excess,
                "score": max(score, 0),
                "top_anchors": anchors.get(url, Counter()).most_common(10),
            }
        )
    return {
        "schema_version": 1,
        "generated_at": now_iso(),
        "home_url": home_url,
        "nodes": nodes,
        "edges": [
            {"source": source, "target": link["href"], "anchor": link.get("text", "")}
            for source, links in outbound.items()
            for link in links
        ],
        "summary": {
            "url_count": len(nodes),
            "orphan_count": sum(1 for node in nodes if node["orphan"]),
            "excessive_depth_count": sum(1 for node in nodes if node["excessive_depth"]),
            "link_count_excess_count": sum(1 for node in nodes if node["link_count_excess"]),
        },
    }


def compute_depth(home_url: str, outbound: dict[str, list[dict[str, str]]]) -> dict[str, int]:
    depth = {home_url: 0}
    queue: deque[str] = deque([home_url])
    while queue:
        current = queue.popleft()
        for link in outbound.get(current, []):
            target = link["href"]
            if target not in depth:
                depth[target] = depth[current] + 1
                queue.append(target)
    return depth


def render_markdown(graph: dict[str, Any]) -> str:
    rows = [
        [
            node["url"],
            node["inbound_count"],
            node["outbound_count"],
            node["click_depth"],
            node["anchor_diversity"],
            node["orphan"],
            node["score"],
        ]
        for node in sorted(graph["nodes"], key=lambda item: item["score"])[:100]
    ]
    return "\n\n".join(
        [
            "# Internal Link Graph",
            f"Generated: {graph['generated_at']}",
            f"Home URL: {graph['home_url']}",
            f"Summary: {graph['summary']}",
            markdown_table(["URL", "Inbound", "Outbound", "Depth", "Anchors", "Orphan", "Score"], rows),
        ]
    )


if __name__ == "__main__":
    raise SystemExit(main())
