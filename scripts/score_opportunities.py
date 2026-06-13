#!/usr/bin/env python3
"""Score SEO opportunities by impact, confidence, effort, and risk."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from seo_utils import confidence_weight, now_iso, read_json, severity_weight, write_json, write_markdown, markdown_table


MODULE_WEIGHTS = {
    "critical_technical_seo": 1.25,
    "load_speed": 1.15,
    "competitor_keyword_gap": 1.15,
    "gsc_opportunity_mining": 1.1,
    "internal_link_graph": 1.05,
    "ai_visibility": 1.0,
    "on_page_elements": 0.95,
    "content_semantic_gaps": 0.9,
    "serp_competitor_discovery": 0.85,
    "competitor_content_entity_gap": 0.85,
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Score seo_opportunities.json.")
    parser.add_argument("--input", type=Path, default=Path("seo_opportunities.json"))
    parser.add_argument("--output", type=Path, default=Path(".seo-agent/opportunity_scores.json"))
    parser.add_argument("--markdown", type=Path, default=Path(".seo-agent/opportunity_scores.md"))
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = read_json(args.input)
    if not payload:
        raise SystemExit(f"Missing or empty {args.input}")
    scored = []
    for item in payload.get("opportunities", []):
        score = score_item(item)
        enriched = {**item, "priority_score": score, "priority_band": band(score)}
        scored.append(enriched)
    scored.sort(key=lambda item: item["priority_score"], reverse=True)
    output = {
        "schema_version": 1,
        "generated_at": now_iso(),
        "source": str(args.input),
        "scoring_model": {
            "severity": "critical=100 high=75 medium=45 low=20",
            "confidence": "observed=100 provided=85 inferred=55 unverified=25",
            "module_multiplier": MODULE_WEIGHTS,
            "penalties": "content-needed -8, high-risk -8, external authorization -12, blocked/deferred -20",
        },
        "opportunities": scored,
    }
    write_json(args.output, output)
    write_markdown(args.markdown, render_markdown(output))
    print(f"Wrote {args.output}")
    print(f"Wrote {args.markdown}")
    return 0


def score_item(item: dict[str, Any]) -> int:
    base = severity_weight(item.get("severity", "low"))
    confidence = confidence_weight(item.get("confidence", "inferred"))
    module_multiplier = MODULE_WEIGHTS.get(item.get("module", ""), 1.0)
    score = (base * 0.65 + confidence * 0.35) * module_multiplier
    risk = str(item.get("risk", "")).lower()
    status = str(item.get("status", "")).lower()
    if item.get("requires_user_content"):
        score -= 8
    if "high" in risk or "risky" in risk:
        score -= 8
    if "external" in risk or "authorization" in risk:
        score -= 12
    if status in {"blocked", "deferred"}:
        score -= 20
    return max(0, min(100, int(round(score))))


def band(score: int) -> str:
    if score >= 80:
        return "P0"
    if score >= 60:
        return "P1"
    if score >= 40:
        return "P2"
    return "P3"


def render_markdown(payload: dict[str, Any]) -> str:
    rows = [
        [
            item.get("id", ""),
            item.get("priority_score", ""),
            item.get("priority_band", ""),
            item.get("module", ""),
            item.get("severity", ""),
            item.get("finding", "")[:120],
        ]
        for item in payload["opportunities"][:100]
    ]
    return "\n\n".join(
        [
            "# SEO Opportunity Scores",
            f"Generated: {payload['generated_at']}",
            markdown_table(["ID", "Score", "Band", "Module", "Severity", "Finding"], rows),
        ]
    )


if __name__ == "__main__":
    raise SystemExit(main())
