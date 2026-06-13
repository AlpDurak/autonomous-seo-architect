# Autonomous SEO Architect

Autonomous SEO Architect is a multi-host AI agent package for technical SEO audits and safe SEO code changes. It analyzes source code, inspects rendered DOM output with Vercel's `agent-browser` CLI, generates user-approved SEO strategy artifacts, applies framework-aware edits, and writes an exhaustive changelog report.

It is packaged for Codex, Claude Code, and Gemini CLI.

## What It Does

- Ingests the packaged SEO research corpus in `intel/`.
- Detects project stack and SEO ownership files across Next.js, React/Vite, static HTML, MDX/Markdown, XML sitemaps, robots.txt, and common config files.
- Uses `agent-browser snapshot -i` and `agent-browser eval --stdin` for rendered DOM inspection.
- Runs competitor keyword gap analysis from user-provided exports, SERP exports, seed keywords, or approved competitor URL snapshots.
- Distinguishes business competitors from true SERP competitors and maps missing/weak/shared/unique/cannibalized/decayed keyword gaps.
- Audits website load speed with LCP, TTFB, CLS, INP risk, render-blocking resources, image sizing, font loading, third-party scripts, and hydration-cost evidence.
- Mines user-provided Google Search Console exports for high-impression/low-CTR queries, striking-distance keywords, cannibalization, decays, and page-query mismatch.
- Scores internal link graph opportunities: orphan risk, click depth, hub/spoke support, anchor diversity, and priority-page flow.
- Audits AI search readiness for answer extraction, entity disambiguation, schema support, trust signals, and citation-friendly structure.
- Ships stdlib-only evidence scripts for crawling, rendered DOM collection, GSC import, competitor keyword import, PageSpeed/CrUX, JSON-LD validation, log analysis, opportunity scoring, and monitoring snapshots.
- Includes industry playbooks for SaaS, ecommerce, local, publisher/blog, marketplace, international, and programmatic SEO.
- Requires approval after `project_manifesto.md` and again after `seo_dynamic_checklist.md`.
- Uses filesystem MCP plus AST-aware MCP for safe source reads, diffs, metadata insertion, and validation.
- Checks rendered metadata, canonicals, robots directives, headings, alt text, JSON-LD, internal links, mobile parity, Core Web Vitals evidence, and semantic content gaps.
- Produces `.seo-agent/state.json`, `project_manifesto.md`, `seo_competitor_keyword_analysis.md`, `seo_performance_audit.md`, `seo_dynamic_checklist.md`, `seo_opportunities.json`, and `seo_changelog_report.md`.

## Safety Model

The skill runs in four phases:

1. **Project Analysis and Manifesto Generation**
   Generates `project_manifesto.md`, then pauses for user approval.
2. **Deep SEO Audit and Dynamic Checklist**
   Generates `seo_dynamic_checklist.md`, then pauses for user approval.
3. **Safe Code Execution**
   Applies only approved checklist items with narrow diffs and AST-aware edits.
4. **Validation and Reporting**
   Reopens changed pages with `agent-browser` and writes `seo_changelog_report.md`.

The included guard blocks project-code edits until the Phase 2 checklist is approved and blocks Playwright/Puppeteer usage because rendered DOM work must use `agent-browser`.

## Repository Layout

```text
.
|-- .claude-plugin/
|   |-- marketplace.json              # Claude Code marketplace catalog
|   `-- plugin.json                   # Claude Code plugin manifest
|-- .codex-plugin/plugin.json         # Codex plugin manifest
|-- .github/workflows/validate.yml    # Public repo validation workflow
|-- .mcp.json                         # Codex/default MCP bindings
|-- configs/monitoring.example.json   # Monitoring mode example config
|-- gemini-extension.json             # Gemini CLI extension manifest
|-- GEMINI.md                         # Gemini CLI extension context
|-- SKILL.md                          # Root skill document
|-- hooks.json                        # Codex/compatible companion hook manifest
|-- hooks/
|   |-- hooks.json                    # Claude Code native hook config
|   |-- seo-phase-gate.ps1            # Windows hook wrapper
|   `-- seo-phase-gate.sh             # POSIX hook wrapper
|-- intel/                            # SEO research corpus
|-- mcp/claude.mcp.json               # Claude Code MCP bindings
|-- playbooks/industry/               # Industry-specific SEO modules
|-- schemas/                          # Hook, state, import, and opportunity schemas
|-- scripts/
|   |-- analyze_server_logs.py
|   |-- build_internal_link_graph.py
|   |-- collect_pagespeed_crux.py
|   |-- collect_rendered_seo.py
|   |-- collect_static_seo.py
|   |-- import_competitor_keywords.py
|   |-- import_gsc.py
|   |-- monitor_seo.py
|   |-- register_personal_marketplace.py
|   |-- score_opportunities.py
|   |-- seo_state_guard.py
|   |-- validate_structured_data.py
|   `-- validate_package.py
`-- skills/autonomous-seo-architect/SKILL.md
```

## Requirements

- Node.js and `npx`.
- Python 3.10+.
- Vercel `agent-browser` CLI:

```bash
npm i -g agent-browser
agent-browser install
agent-browser doctor --offline --quick
```

The MCP bindings use:

- `@modelcontextprotocol/server-filesystem@2026.1.14`
- `@chousyn/ast-grep-mcp@0.1.1`

Optional data inputs for richer ranking analysis:

- Google Search Console CSV/JSON exports for queries, pages, index coverage, and Core Web Vitals.
- Competitor keyword or rank exports from Ahrefs, Semrush, Moz, Serpstat, DataForSEO, or another SEO platform.
- SERP exports for seed query clusters.
- Competitor URL lists approved for public rendered-page inspection.

The package does not require paid SEO APIs. It treats live SEO accounts and external APIs as explicit opt-in integrations.

## Evidence Scripts

These scripts are optional, local, and stdlib-only.

```bash
python scripts/collect_static_seo.py --url https://example.com --crawl-depth 1
python scripts/collect_rendered_seo.py --url http://localhost:3000
python scripts/import_gsc.py --input exports/gsc.csv
python scripts/import_competitor_keywords.py --target-domain example.com --input exports/competitor.csv --target-input exports/target.csv
python scripts/build_internal_link_graph.py --home-url https://example.com --input .seo-agent/evidence/static_crawl.json
python scripts/collect_pagespeed_crux.py --url https://example.com --strategy both
python scripts/validate_structured_data.py --input .seo-agent/evidence/rendered_seo.json
python scripts/analyze_server_logs.py --input logs/access.log
python scripts/score_opportunities.py --input seo_opportunities.json
python scripts/monitor_seo.py --previous .seo-agent/monitoring_snapshot.previous.json
```

`collect_rendered_seo.py` calls Vercel `agent-browser`; it does not use Playwright or Puppeteer. `collect_pagespeed_crux.py` uses public Google endpoints only when you run it. `CRUX_API_KEY` is required for CrUX; `PSI_API_KEY` is optional for PageSpeed Insights.

## Install for Codex

Clone the repo into Codex's standard personal plugin location.

PowerShell:

```powershell
git clone https://github.com/AlpDurak/autonomous-seo-architect.git "$env:USERPROFILE\plugins\autonomous-seo-architect"
cd "$env:USERPROFILE\plugins\autonomous-seo-architect"
python scripts\register_personal_marketplace.py
codex plugin add autonomous-seo-architect@personal
```

Bash:

```bash
git clone https://github.com/AlpDurak/autonomous-seo-architect.git "$HOME/plugins/autonomous-seo-architect"
cd "$HOME/plugins/autonomous-seo-architect"
python scripts/register_personal_marketplace.py
codex plugin add autonomous-seo-architect@personal
```

Start a new Codex thread after installation so the skill and MCP bindings load cleanly.

## Install for Claude Code

Claude Code can install this repository as a marketplace. From Claude Code or the Claude CLI:

```bash
claude plugin marketplace add AlpDurak/autonomous-seo-architect
claude plugin install autonomous-seo-architect@autonomous-seo-architect
```

For local development from a clone:

```bash
claude plugin validate .
claude plugin marketplace add .
claude plugin install autonomous-seo-architect@autonomous-seo-architect
```

Then reload plugins in any open Claude Code session:

```text
/reload-plugins
```

Claude Code loads:

- `skills/autonomous-seo-architect/SKILL.md`
- `hooks/hooks.json`
- `mcp/claude.mcp.json`

The Claude hook commands call `scripts/seo_state_guard.py` directly and rely on Claude Code's exit-code-2 blocking behavior for `PreToolUse`.

## Install for Gemini CLI

Install as a Gemini CLI extension from GitHub:

```bash
gemini extensions install https://github.com/AlpDurak/autonomous-seo-architect
gemini extensions list
```

Open Gemini CLI in the project you want to audit and confirm MCP servers are available:

```text
/mcp
```

Gemini CLI loads:

- `gemini-extension.json`
- `GEMINI.md`
- MCP servers bound to `${workspacePath}`
- `excludeTools` entries that block Playwright/Puppeteer shell commands

Gemini extensions do not currently expose the same native hook lifecycle as Claude Code. The package therefore uses Gemini extension config plus `GEMINI.md` instructions and the shared state guard for manual checks.

## Standalone Skill Only

If you only want the instruction file, install the skill folder directly. This does not install MCP bindings, hooks, or Gemini extension config.

Codex:

```bash
mkdir -p "$HOME/.codex/skills/autonomous-seo-architect"
cp ./skills/autonomous-seo-architect/SKILL.md "$HOME/.codex/skills/autonomous-seo-architect/SKILL.md"
```

Claude Code:

```bash
mkdir -p "$HOME/.claude/skills/autonomous-seo-architect"
cp ./skills/autonomous-seo-architect/SKILL.md "$HOME/.claude/skills/autonomous-seo-architect/SKILL.md"
```

For full autonomous operation, prefer the plugin or extension install so the packaged `intel/`, MCP bindings, and hooks are available.

## MCP Bindings

This repo ships three MCP configs:

- `.mcp.json` for Codex and hosts that support `${workspaceFolder}`.
- `mcp/claude.mcp.json` for Claude Code, using `${CLAUDE_PROJECT_DIR}`.
- `gemini-extension.json` for Gemini CLI, using `${workspacePath}`.

Each config declares:

```json
{
  "mcpServers": {
    "seo-filesystem": {},
    "seo-ast-grep": {}
  }
}
```

`seo-filesystem` gives the agent scoped file access for source files, manifests, reports, and approved diffs. `seo-ast-grep` gives the agent AST-aware search and rewrite support for framework-safe metadata and structured data edits.

If a host does not expand the documented workspace variable, replace it with an absolute project path.

## Hooks and Guards

Shared guard:

```bash
python scripts/seo_state_guard.py init-state --workspace . --json
python scripts/seo_state_guard.py pre-edit --workspace . --target project_manifesto.md --json
python scripts/seo_state_guard.py pre-shell --workspace . --json
```

Codex/compatible companion hook manifest:

```text
hooks.json
```

Claude Code native hook manifest:

```text
hooks/hooks.json
```

Hook wrappers:

```bash
./hooks/seo-phase-gate.sh pre-edit
```

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\hooks\seo-phase-gate.ps1 pre-edit
```

Set `SEO_AGENT_WORKSPACE` when the hook command runs from outside the audited project.

## Validate the Package

Basic validation:

```bash
python scripts/validate_package.py
python -m py_compile scripts/seo_state_guard.py scripts/register_personal_marketplace.py
python scripts/seo_state_guard.py init-state --workspace . --json
python scripts/register_personal_marketplace.py --help
```

Host validators, when available:

```bash
python <path-to-skill-creator>/scripts/quick_validate.py .
python <path-to-plugin-creator>/scripts/validate_plugin.py .
claude plugin validate .
gemini extensions install https://github.com/AlpDurak/autonomous-seo-architect
```

## Usage Prompts

```text
Use Autonomous SEO Architect to run Phase 1 for this project.
```

```text
Use Autonomous SEO Architect to audit this local dev server: http://localhost:3000
```

```text
Use Autonomous SEO Architect to execute approved checklist items TECH-001 and ONPAGE-003.
```

## Runtime Artifacts

During a real SEO run, the agent creates:

- `.seo-agent/state.json`
- `.seo-agent/evidence/`
- `.seo-agent/internal_link_graph.json`
- `.seo-agent/search_console_import.json`
- `.seo-agent/evidence/rendered_seo.json`
- `.seo-agent/evidence/static_crawl.json`
- `.seo-agent/evidence/pagespeed_crux.json`
- `.seo-agent/evidence/structured_data_validation.json`
- `.seo-agent/evidence/server_log_analysis.json`
- `.seo-agent/opportunity_scores.json`
- `.seo-agent/monitoring_snapshot.json`
- `project_manifesto.md`
- `seo_competitor_keyword_analysis.md`
- `seo_performance_audit.md`
- `seo_dynamic_checklist.md`
- `seo_opportunities.json`
- `seo_changelog_report.md`

`seo_opportunities.json` is the machine-readable report. It mirrors checklist items and includes module, severity, evidence, proposed fix, expected impact, validation method, failure signal, leading indicator, dependencies, status, and confidence.

## Important Constraints

- Do not use Playwright or Puppeteer for rendered DOM work; use `agent-browser`.
- Do not edit project code before the checklist is approved.
- Do not fabricate author credentials, reviews, prices, citations, policies, or first-hand claims.
- Do not fabricate keyword volumes, rankings, competitor performance, search demand, or Google Search Console data.
- Do not copy competitor content; use competitor analysis to identify intent, entity, structure, and differentiation opportunities.
- Do not run public PageSpeed/CrUX checks, competitor snapshots, or server-log analysis unless the target/input is authorized by the user.
- Treat off-page SEO actions such as outreach or disavow submission as recommendations unless the user explicitly authorizes external account/tool use.

## License

MIT. See `LICENSE`.
