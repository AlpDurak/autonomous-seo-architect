# Autonomous SEO Architect

Use this extension when the user asks Gemini CLI to audit or optimize SEO for a local website or codebase.

## Required Workflow

1. Read `SKILL.md` or `skills/autonomous-seo-architect/SKILL.md` before doing SEO work.
2. Read every file in `intel/` before creating the manifesto, checklist, or code changes.
3. Use the MCP servers from `gemini-extension.json` for filesystem and AST-aware work. The extension binds them to `${workspacePath}`.
4. Use Vercel `agent-browser` through shell commands for rendered DOM inspection:
   - `agent-browser open <url>`
   - `agent-browser wait --load networkidle`
   - `agent-browser snapshot -i`
   - `agent-browser eval --stdin`
   - `agent-browser vitals <url>`
5. Do not use Playwright or Puppeteer.
6. Do not edit project code before `project_manifesto.md` and `seo_dynamic_checklist.md` are approved.
7. When user-provided exports exist, ingest competitor keyword/rank data, SERP data, and Google Search Console data before producing Phase 2 findings.
8. Always write `seo_opportunities.json` with falsifiable recommendations: expected impact, validation method, failure signal, leading indicator, confidence, and status.
9. Prefer packaged scripts for repeatable evidence collection when their inputs are available.

## Phases

- Phase 1: Generate `project_manifesto.md`, then pause for approval.
- Phase 2: Generate `seo_competitor_keyword_analysis.md`, `seo_performance_audit.md`, `seo_dynamic_checklist.md`, and `seo_opportunities.json`, then pause for approval.
- Phase 3: Execute only approved checklist items using narrow diffs and AST-aware edits.
- Phase 4: Revisit changed pages with `agent-browser` and write `seo_changelog_report.md`.

## Approved Analysis Modules

- Competitor keyword gap analysis: missing, weak, shared, unique, cannibalized, decayed, and irrelevant keyword gaps.
- SERP competitor discovery: distinguish commercial competitors from domains repeatedly ranking for query clusters.
- Competitor content/entity gaps: compare visible structure and entities without copying competitor content.
- Website load speed: LCP, TTFB, CLS, INP risk, resource loading, image sizing, fonts, third-party scripts, and hydration cost.
- Google Search Console export mining: CTR gaps, striking-distance keywords, page-query mismatch, cannibalization, and decays.
- AI search readiness: answer extraction, entity disambiguation, schema support, trust signals, and citation-friendly structure.
- Internal link graph scoring: orphan risk, click depth, anchor diversity, hub/spoke coverage, and priority-page support.
- Structured data validation: parse JSON-LD and flag syntax/basic hygiene issues.
- Server log analysis: use only user-provided logs to evaluate crawl-budget waste and Googlebot errors.
- Monitoring mode: compare snapshots for regressions in metadata, speed, structured data, and crawl signals.

## Evidence Scripts

```bash
python scripts/collect_static_seo.py --url <url> --crawl-depth 1
python scripts/collect_rendered_seo.py --url <url>
python scripts/import_gsc.py --input <gsc-export.csv>
python scripts/import_competitor_keywords.py --target-domain <domain> --input <competitor-export.csv> --target-input <target-export.csv>
python scripts/build_internal_link_graph.py --home-url <url> --input .seo-agent/evidence/rendered_seo.json
python scripts/collect_pagespeed_crux.py --url <public-url> --strategy both
python scripts/validate_structured_data.py --input .seo-agent/evidence/rendered_seo.json
python scripts/analyze_server_logs.py --input <access.log>
python scripts/score_opportunities.py --input seo_opportunities.json
python scripts/monitor_seo.py --previous .seo-agent/monitoring_snapshot.previous.json
```

Use the industry playbooks in `playbooks/industry/` when the site type is clear.

## State Guard

Gemini CLI extensions do not provide the Claude-style hook lifecycle used by this package. Enforce the phase gates in reasoning, honor `excludeTools`, and keep `.seo-agent/state.json` current.

When working from a local clone of this repository, initialize local run state with:

```bash
python scripts/seo_state_guard.py init-state --workspace . --json
```

When this package is installed as a Gemini extension, use the same guard script from the installed extension directory if a manual check is needed.
