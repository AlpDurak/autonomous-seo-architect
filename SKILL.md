---
name: autonomous-seo-architect
description: Use when auditing or optimizing a website/codebase for technical SEO, competitor keyword gaps, SERP competitors, website load speed, Google Search Console exports, on-page SEO, rendered DOM metadata, Core Web Vitals, structured data, internal linking, topical authority, AI search visibility, or safe framework-specific SEO code changes.
---

# Autonomous SEO Architect

## Operating Contract

Act as a senior technical SEO engineer and AI architect. Execute SEO work through auditable phases, persist state, pause at required approval gates, and never modify code before the approved checklist exists.

This skill is authoritative for projects that need autonomous SEO analysis, rendered DOM inspection, strategic SEO planning, safe code edits, and change reporting.

## Required Tools

Use only these tool families for SEO execution:

```yaml
tool_contract:
  filesystem_mcp:
    purpose:
      - read source files, config files, HTML, JSX, TSX, MD, MDX, XML, robots.txt, sitemap files
      - write project_manifesto.md
      - write seo_dynamic_checklist.md
      - write seo_opportunities.json
      - write seo_competitor_keyword_analysis.md
      - write seo_performance_audit.md
      - apply safe diffs to project files
      - write seo_changelog_report.md
      - persist .seo-agent/state.json and evidence files
      - persist optional imported GSC, SERP, keyword, and link-graph evidence under .seo-agent/
    required_capabilities:
      - list_directory
      - search_files
      - read_file
      - stat_file
      - hash_file
      - write_file
      - apply_patch_or_diff
  agent_browser_cli:
    command: agent-browser
    purpose:
      - load the local dev server
      - inspect rendered DOMs and accessibility trees
      - verify client-side metadata after edits
      - capture screenshots and Core Web Vitals/hydration evidence
    required_commands:
      - agent-browser open
      - agent-browser wait
      - agent-browser snapshot -i
      - agent-browser snapshot -i --json
      - agent-browser get
      - agent-browser eval --stdin
      - agent-browser vitals
      - agent-browser screenshot --full
      - agent-browser close
  ast_parser_linter_mcp:
    purpose:
      - detect framework and route ownership
      - parse HTML, JSX, TSX, MDX, XML, and config files
      - insert or modify metadata, head tags, JSON-LD, and route metadata safely
      - run available lint, format, typecheck, and build validation through project-defined commands when exposed
    required_capabilities:
      - parse_ast
      - query_ast
      - apply_ast_edit
      - lint_files
      - format_files
      - typecheck_or_build
  optional_user_provided_data:
    purpose:
      - ingest Google Search Console exports supplied by the user
      - ingest competitor keyword/ranking exports supplied by the user
      - ingest SERP exports or competitor URL lists supplied by the user
      - ingest seed keyword lists supplied by the user
    constraints:
      - do not access paid SEO accounts, Google accounts, or external APIs unless the user explicitly authorizes that tool/account
      - treat imported data as evidence with source, date, and confidence metadata
      - mark competitor and SERP claims as unverified when the source is inferred or incomplete
```

Forbidden tools:

```yaml
forbidden:
  - Playwright MCP
  - Puppeteer MCP
  - browser automation frameworks other than agent-browser CLI
  - blind regex rewrites of JSX/TSX/MDX when AST editing is available
  - automatic disavow uploads, outreach, or off-page actions without explicit user authorization
```

Shell usage is allowed only for `agent-browser` commands, project dev server commands needed to expose the local site, and project validation commands discovered from package/config files. Do not use Playwright or Puppeteer through shell either.

## Packaged Integrations

This package includes integration files for multiple AI coding hosts:

```yaml
packaged_files:
  codex:
    plugin_manifest: .codex-plugin/plugin.json
    mcp_bindings: .mcp.json
    companion_hook_manifest: hooks.json
  claude_code:
    marketplace_catalog: .claude-plugin/marketplace.json
    plugin_manifest: .claude-plugin/plugin.json
    mcp_bindings: mcp/claude.mcp.json
    native_hook_manifest: hooks/hooks.json
  gemini_cli:
    extension_manifest: gemini-extension.json
    context_file: GEMINI.md
    mcp_bindings: gemini-extension.json#mcpServers
    tool_exclusions: gemini-extension.json#excludeTools
  hook_runners:
    windows: hooks/seo-phase-gate.ps1
    posix: hooks/seo-phase-gate.sh
  state_guard: scripts/seo_state_guard.py
  state_schema: schemas/seo-state.schema.json
  opportunity_schema: schemas/seo-opportunities.schema.json
  data_import_schema: schemas/seo-data-import.schema.json
  evidence_scripts:
    static_crawler: scripts/collect_static_seo.py
    rendered_collector: scripts/collect_rendered_seo.py
    gsc_importer: scripts/import_gsc.py
    competitor_keyword_importer: scripts/import_competitor_keywords.py
    internal_link_graph: scripts/build_internal_link_graph.py
    pagespeed_crux: scripts/collect_pagespeed_crux.py
    structured_data_validator: scripts/validate_structured_data.py
    server_log_analyzer: scripts/analyze_server_logs.py
    opportunity_scorer: scripts/score_opportunities.py
    monitoring_snapshot: scripts/monitor_seo.py
  monitoring_config: configs/monitoring.example.json
  industry_playbooks:
    - playbooks/industry/saas.md
    - playbooks/industry/ecommerce.md
    - playbooks/industry/local.md
    - playbooks/industry/publisher.md
    - playbooks/industry/marketplace.md
    - playbooks/industry/international.md
    - playbooks/industry/programmatic.md
```

Use the host-specific MCP binding for the active runtime:

- Codex/default hosts: `.mcp.json`, using `${workspaceFolder}`.
- Claude Code: `mcp/claude.mcp.json`, using `${CLAUDE_PROJECT_DIR}`.
- Gemini CLI: `gemini-extension.json`, using `${workspacePath}`.

Use `scripts/seo_state_guard.py` to enforce phase gates wherever the host supports hooks. Claude Code loads `hooks/hooks.json` natively and blocks `PreToolUse` violations through exit code 2. Codex-compatible hosts can wire `hooks.json` as a companion manifest. Gemini CLI extensions do not expose the same hook lifecycle, so enforce the phase gates in reasoning, honor `excludeTools`, and call the guard manually when a check is needed.

## Mandatory Knowledge Ingestion

At the start of every SEO run, read every file in the packaged `intel/` directory and any relevant packaged `playbooks/industry/` file. Resolve the knowledge base in this order:

1. The package/plugin/extension root that contains this `SKILL.md`.
2. The repository root if running from a local clone.
3. A project-local `intel/` directory only when the user intentionally provides one.

If no `intel/` directory is available from those locations, stop and ask for the knowledge base. Do not perform an SEO audit from generic memory alone.

Industry playbook selection:

```yaml
industry_playbook_selection:
  saas: software, API, subscriptions, B2B SaaS, docs, integrations
  ecommerce: products, categories, variants, carts, inventory, merchant data
  local: physical locations, service areas, NAP, maps, local services
  publisher: articles, news, blogs, reviews, tutorials, editorial content
  marketplace: listings, sellers, jobs, rentals, profiles, user-generated inventory
  international: multiple countries, languages, currencies, hreflang, locale routing
  programmatic: generated pages, directories, templates, filter combinations, large-scale datasets
```

Persist the ingestion result in `.seo-agent/state.json`:

```json
{
  "knowledge_base": [
    {
      "path": "intel/example.md",
      "sha256": "hex",
      "bytes": 12345,
      "summary": "1-3 sentence synthesis"
    }
  ]
}
```

Persist optional user-provided data sources in `.seo-agent/state.json`:

```json
{
  "data_sources": {
    "competitor_keyword_exports": [
      {
        "path": ".seo-agent/imports/competitor-keywords.csv",
        "source": "Semrush Keyword Gap export",
        "provided_by_user": true,
        "confidence": "provided"
      }
    ],
    "serp_exports": [],
    "gsc_exports": [],
    "competitor_urls": []
  }
}
```

If imported data is available, normalize it into `.seo-agent/search_console_import.json` or reference it from `seo_opportunities.json`. Use `schemas/seo-data-import.schema.json` as the import envelope when creating normalized import manifests.

Distill the current `intel/` corpus into these rules during audits:

```yaml
seo_rules:
  robots_txt:
    - robots.txt must live at the top-level host/protocol/port path.
    - parse as UTF-8 text; merge duplicate user-agent groups; ignore empty lines.
    - warn on Crawl-delay because modern Googlebot ignores it.
    - resolve Allow/Disallow conflicts by longest matching path; on equal length, Allow wins.
    - process "*" wildcards and "$" end-of-string markers.
    - status behavior: 2xx parse rules, 3xx follow up to five redirects, 4xx means full access, 5xx means no access unless cached good copy applies.
    - flag files over 500 KiB because crawlers may ignore content beyond that limit.
  sitemaps:
    - XML must be UTF-8, entity escaped, and use valid urlset or sitemapindex roots.
    - each sitemap is limited to 50000 URLs and 52428800 uncompressed bytes.
    - loc values must be absolute URLs and under 2048 characters.
    - lastmod must use W3C date/datetime format.
    - sitemap indexes must not list other sitemap indexes.
    - referenced sitemaps must be in the same or lower directory unless cross-site ownership is proven.
    - validate image, video, news, and xhtml/hreflang namespaces only when used.
    - in each url entry, loc must come before extension elements.
    - video sitemap entries require thumbnail_loc and title.
    - hreflang values must use ISO 639-1 language and ISO 3166-1 alpha-2 region codes.
  canonicals:
    - canonical tags must be in head.
    - every indexable page should have exactly one self-referential canonical unless intentional syndication/deduplication is documented.
    - canonical targets must be absolute, return 200, and not be robots-blocked.
    - flag multiple canonicals, canonical/noindex conflicts, canonical chains, and canonical loops.
  rendering:
    - use agent-browser for rendered DOM inspection.
    - compare source/code expectations against rendered DOM; metadata that appears only after client JS is high risk.
    - flag CSR shells when core text, H1, links, or metadata are absent from server/source ownership.
    - capture hydration and runtime evidence with agent-browser vitals and DOM extraction.
  structured_data:
    - prefer JSON-LD in script[type="application/ld+json"].
    - require @context, @type, absolute URLs for url/image/sameAs, and ISO 8601 dates.
    - structured data must match visible page content; never mark up hidden or fabricated facts.
    - Product schema should include name, crawlable image, sku or gtin when available, nested brand, offers.price, priceCurrency, availability, priceValidUntil for sale pricing, itemCondition, and displayed aggregateRating/review when used.
    - Recipe schema should align with page headings and use images with crawlable URLs and suitable aspect ratios when available.
    - FAQPage is no longer a Google FAQ rich-result target, but can still support Schema.org, Bing, and AI extraction; use QAPage only for multiple user-submitted answers.
  core_web_vitals:
    - target LCP <= 2.5s, CLS <= 0.1, INP <= 200ms at the 75th percentile, especially mobile.
    - LCP remediation: reduce TTFB, make the LCP element discoverable in initial HTML, preload/fetchpriority high for hero assets, defer non-critical JS, inline critical CSS where appropriate.
    - CLS remediation: reserve dimensions/aspect-ratio for images/embeds/widgets, avoid late top insertions, use stable font loading, animate transform/opacity instead of layout properties.
    - INP remediation: split long tasks, yield with scheduler.yield where supported, offload heavy work to Web Workers, reduce DOM size, and avoid layout thrashing.
  load_speed:
    - classify speed evidence as lab, field, or inferred source-code evidence.
    - inspect LCP candidate discoverability, image sizing/format, preloads, fetchpriority, critical CSS, font loading, third-party scripts, hydration cost, route-level JS, TTFB, cache headers visible in code, and blocking resources.
    - prefer fixes that reduce render-blocking work before adding new dependencies.
    - separate local dev-server timing from production field data; do not overstate ranking impact from lab-only data.
  mobile_first:
    - mobile DOM is the indexing source of truth.
    - validate parity for content, links, metadata, structured data, and navigation between mobile and desktop.
  on_page:
    - title should usually be <= 60 characters, contain the primary keyword once near the front, and append brand at the end when useful.
    - meta description should usually be 150-160 characters, natural, click-oriented, and non-stuffed.
    - each URL should have one descriptive H1 with the primary topic.
    - H2/H3 structure should express topic hierarchy and question-style long-tail opportunities.
    - alt text should be natural, accurate, and usually under 125 characters; do not stuff keywords.
    - image filenames should be descriptive and hyphen-separated when changing assets is in scope.
  eeat:
    - classify YMYL risk before recommendations.
    - require author transparency, editorial standards, citations, date freshness, first-hand experience, and trust signals where topic risk demands them.
    - never fabricate credentials, reviews, prices, policies, experience, citations, or claims.
  internal_linking:
    - detect orphan pages and excessive click depth.
    - keep priority pages within 2-3 clicks of the homepage when feasible.
    - prefer hub-and-spoke topic clusters; pillar pages link to spokes and spokes link back to pillars.
    - use 2-5 contextual internal links per 1000 words as a planning range; keep total links under 150 unless navigation requires more.
    - maintain natural anchor diversity; avoid exact-match overuse.
    - build a link graph from source routes, sitemap entries, rendered navigation, and content links when enough URLs are known.
    - score each URL for inbound internal links, outbound internal links, click depth, anchor diversity, hub/spoke role, and orphan risk.
  semantic_content:
    - target entities and intent, not keyword density.
    - classify intent as informational, navigational, commercial, transactional, or generative.
    - use SERP-overlap clustering when external SERP data is provided or explicitly approved: 70%+ overlap means one page, 30-70% requires editorial review, below 30% usually requires separate pages.
    - use concise extraction architecture: answer core questions in the first 1-2 sentences of relevant sections.
    - identify entity gaps from competitors, but mark external competitor claims as unverified unless evidence is available.
  competitor_intelligence:
    - use competitor keyword exports, rank exports, SERP exports, GSC exports, or user-approved competitor URL snapshots when available.
    - distinguish business competitors from SERP competitors; SERP competitors are domains repeatedly visible for target query clusters.
    - classify keyword gaps as missing, weak, shared, unique, cannibalized, or decayed.
    - prioritize gaps by intent match, business relevance, page fit, realistic difficulty, content effort, internal-link support, and evidence confidence.
    - never copy competitor text, headings, or proprietary claims; extract patterns, entity coverage, and intent architecture only.
  search_console:
    - ingest user-provided GSC exports for queries, pages, impressions, clicks, CTR, average position, indexing, and Core Web Vitals where available.
    - find high-impression/low-CTR queries, striking-distance rankings, page-query mismatch, cannibalization candidates, decaying pages, and zero-click answer opportunities.
    - preserve privacy: do not request account access unless the user explicitly asks to connect an account or API.
  ai_visibility:
    - audit answer extraction readiness, direct definitions, Q&A structure, source/citation clarity, entity disambiguation, sameAs links, schema support, author/trust signals, and non-promotional tone.
    - mark LLM citation or AI Overview claims as unverified unless the user provides external evidence or authorizes external checks.
  off_page:
    - treat backlink, PR, unlinked mention, and disavow work as strategic recommendations unless the user grants external account/tool access.
    - natural profiles have diverse domains, topical relevance, mixed link attributes, varied anchors, and steady velocity.
    - toxic profiles show irrelevant domains, PBN/link-farm patterns, exact-match anchor excess, and unnatural spikes.
    - defensive anchor baseline: about 70% branded, 20% naked URL, 5% generic, 1-5% partial/LSI, and <1% exact-match unless competitor evidence supports otherwise.
    - recommend disavow only for confirmed manual unnatural-link actions or verified negative SEO attacks correlated with traffic/impression loss.
  recommendation_quality:
    - every opportunity must be falsifiable.
    - include expected impact, validation method, failure signal, leading indicator, dependencies, evidence confidence, and whether user-provided content is required.
    - separate code-fixable issues from strategic/content recommendations.
```

## State Machine

Maintain `.seo-agent/state.json` and obey it on resume.

```json
{
  "schema_version": 1,
  "current_phase": "phase_1_project_analysis",
  "approvals": {
    "phase_1_manifesto": false,
    "phase_2_checklist": false
  },
  "dev_server": {
    "url": null,
    "start_command": null
  },
  "targets": [],
  "artifacts": {
    "manifesto": "project_manifesto.md",
    "checklist": "seo_dynamic_checklist.md",
    "opportunities_json": "seo_opportunities.json",
    "competitor_keyword_analysis": "seo_competitor_keyword_analysis.md",
    "performance_audit": "seo_performance_audit.md",
    "report": "seo_changelog_report.md",
    "internal_link_graph": ".seo-agent/internal_link_graph.json",
    "search_console_import": ".seo-agent/search_console_import.json",
    "rendered_seo": ".seo-agent/evidence/rendered_seo.json",
    "static_crawl": ".seo-agent/evidence/static_crawl.json",
    "pagespeed_crux": ".seo-agent/evidence/pagespeed_crux.json",
    "structured_data_validation": ".seo-agent/evidence/structured_data_validation.json",
    "server_log_analysis": ".seo-agent/evidence/server_log_analysis.json",
    "opportunity_scores": ".seo-agent/opportunity_scores.json",
    "monitoring_snapshot": ".seo-agent/monitoring_snapshot.json",
    "evidence_dir": ".seo-agent/evidence"
  },
  "data_sources": {
    "competitor_keyword_exports": [],
    "serp_exports": [],
    "gsc_exports": [],
    "competitor_urls": []
  },
  "analysis_modules": {
    "competitor_keyword_gap": false,
    "serp_competitor_discovery": false,
    "competitor_content_entity_gap": false,
    "load_speed_audit": false,
    "gsc_opportunity_mining": false,
    "ai_visibility_audit": false,
    "internal_link_graph_scoring": false,
    "machine_readable_reporting": true,
    "falsifiable_recommendations": true,
    "structured_data_validation": true,
    "server_log_analysis": false,
    "opportunity_scoring": true,
    "monitoring_mode": false,
    "industry_playbooks": true
  },
  "file_hashes_before_edit": {},
  "changes": []
}
```

Phase gate rules:

```yaml
phase_gates:
  - Do not start Phase 2 until the user approves project_manifesto.md.
  - Do not start Phase 3 until the user approves seo_dynamic_checklist.md or a clearly scoped subset of it.
  - Do not edit project code in Phase 1 or Phase 2.
  - Do not edit files whose current hash differs from the Phase 3 baseline without re-reading and reconciling the user change.
  - Do not mark Phase 4 complete until rendered validation and code validation have both run or their blockers are documented.
```

## Agent-Browser Recipes

Use `agent-browser snapshot -i` as the default DOM-reading primitive because it returns token-efficient accessibility trees with `@eN` refs.

Open and inspect a target:

```bash
agent-browser open "$URL"
agent-browser wait --load networkidle
agent-browser snapshot -i --json
agent-browser snapshot -i -u --json
```

Extract SEO-critical rendered head and body signals:

```bash
agent-browser eval --stdin <<'JS'
JSON.stringify({
  url: location.href,
  title: document.title || null,
  metaDescription: document.querySelector('meta[name="description"]')?.content || null,
  robots: document.querySelector('meta[name="robots"]')?.content || null,
  canonical: document.querySelector('link[rel="canonical"]')?.href || null,
  canonicalCount: document.querySelectorAll('link[rel="canonical"]').length,
  hreflang: Array.from(document.querySelectorAll('link[rel="alternate"][hreflang]')).map(e => ({
    hreflang: e.getAttribute('hreflang'),
    href: e.href
  })),
  h1: Array.from(document.querySelectorAll('h1')).map(e => e.innerText.trim()).filter(Boolean),
  headings: Array.from(document.querySelectorAll('h1,h2,h3')).map(e => ({
    tag: e.tagName.toLowerCase(),
    text: e.innerText.trim()
  })).filter(e => e.text),
  imagesMissingAlt: Array.from(document.images).filter(img => !img.hasAttribute('alt') || img.alt.trim() === '').map(img => img.currentSrc || img.src),
  internalLinks: Array.from(document.querySelectorAll('a[href]')).map(a => ({
    text: a.innerText.trim(),
    href: a.href
  })).filter(a => a.href.startsWith(location.origin)),
  jsonLd: Array.from(document.querySelectorAll('script[type="application/ld+json"]')).map(s => s.textContent.trim())
}, null, 2)
JS
```

Capture performance and hydration evidence:

```bash
agent-browser open --enable react-devtools "$URL"
agent-browser wait --load networkidle
agent-browser vitals "$URL"
agent-browser screenshot --full ".seo-agent/evidence/page.png"
```

Extract load-speed diagnostics from the rendered page:

```bash
agent-browser eval --stdin <<'JS'
JSON.stringify({
  url: location.href,
  navigation: (() => {
    const nav = performance.getEntriesByType('navigation')[0]
    if (!nav) return null
    return {
      type: nav.type,
      transferSize: nav.transferSize,
      encodedBodySize: nav.encodedBodySize,
      domContentLoadedMs: Math.round(nav.domContentLoadedEventEnd),
      loadEventMs: Math.round(nav.loadEventEnd),
      ttfbMs: Math.round(nav.responseStart - nav.requestStart)
    }
  })(),
  resources: performance.getEntriesByType('resource').map(r => ({
    name: r.name,
    initiatorType: r.initiatorType,
    durationMs: Math.round(r.duration),
    transferSize: r.transferSize || 0,
    renderBlockingStatus: r.renderBlockingStatus || 'unknown'
  })).sort((a, b) => b.durationMs - a.durationMs).slice(0, 50),
  images: Array.from(document.images).map(img => ({
    src: img.currentSrc || img.src,
    loading: img.loading || '',
    fetchPriority: img.fetchPriority || '',
    width: img.width,
    height: img.height,
    naturalWidth: img.naturalWidth,
    naturalHeight: img.naturalHeight,
    hasExplicitSize: img.hasAttribute('width') && img.hasAttribute('height')
  })),
  scripts: Array.from(document.scripts).map(s => ({
    src: s.src || '[inline]',
    async: s.async,
    defer: s.defer,
    type: s.type || 'classic'
  })),
  stylesheets: Array.from(document.querySelectorAll('link[rel="stylesheet"]')).map(l => l.href),
  preloads: Array.from(document.querySelectorAll('link[rel="preload"],link[rel="preconnect"],link[rel="dns-prefetch"]')).map(l => ({
    rel: l.rel,
    as: l.as || '',
    href: l.href
  }))
}, null, 2)
JS
```

Interact only through fresh refs:

```bash
agent-browser snapshot -i
agent-browser click @e1
agent-browser wait --load networkidle
agent-browser snapshot -i
```

Close sessions when finished:

```bash
agent-browser close
```

## Evidence Automation Scripts

Use these packaged scripts whenever the required input exists. They are stdlib-only and write auditable artifacts under `.seo-agent/` unless otherwise noted.

```bash
# Static crawl: status codes, source HTML SEO tags, links, images, JSON-LD, duplicates
python scripts/collect_static_seo.py --url "$URL" --crawl-depth 1 --max-urls 100 --output .seo-agent/evidence/static_crawl.json

# Rendered DOM collector: agent-browser snapshots, rendered metadata, links, images, JSON-LD, vitals
python scripts/collect_rendered_seo.py --url "$URL" --output .seo-agent/evidence/rendered_seo.json

# Optional public URL performance APIs: PageSpeed Insights and CrUX
python scripts/collect_pagespeed_crux.py --url "$PUBLIC_URL" --strategy both --output .seo-agent/evidence/pagespeed_crux.json

# Google Search Console export import
python scripts/import_gsc.py --input path/to/gsc-export.csv --output .seo-agent/search_console_import.json

# Competitor keyword/ranking export import
python scripts/import_competitor_keywords.py --target-domain example.com --input path/to/competitor.csv --target-input path/to/target.csv

# Internal link graph from collected evidence
python scripts/build_internal_link_graph.py --home-url "$URL" --input .seo-agent/evidence/rendered_seo.json --input .seo-agent/evidence/static_crawl.json

# JSON-LD syntax/basic hygiene validation
python scripts/validate_structured_data.py --input .seo-agent/evidence/rendered_seo.json

# Server log SEO analysis, when logs are user-provided
python scripts/analyze_server_logs.py --input path/to/access.log

# Priority scoring for machine-readable opportunities
python scripts/score_opportunities.py --input seo_opportunities.json

# Monitoring snapshot and delta report
python scripts/monitor_seo.py --previous .seo-agent/monitoring_snapshot.previous.json
```

Script usage rules:

- Do not run PageSpeed Insights or CrUX against non-public, private, staging, or third-party URLs unless the user authorizes it.
- Do not request API keys unless a public field-data workflow is explicitly useful. `PSI_API_KEY` is optional for PageSpeed Insights; `CRUX_API_KEY` is required for CrUX API.
- Do not analyze server logs unless the user provides them and confirms they may be processed locally.
- Treat script outputs as evidence, not truth without context; local dev speed, lab data, field data, logs, and GSC exports each answer different questions.
- Use `scripts/score_opportunities.py` after writing `seo_opportunities.json`, then reflect priority bands in `seo_dynamic_checklist.md` and `seo_changelog_report.md`.

## Phase 1: Project Analysis and Manifesto Generation

Goal: understand the codebase, rendered site, brand, audience, keyword architecture, competitor landscape, available ranking data, load-speed baseline, and measurement assumptions without editing code.

Required steps:

1. Read `.seo-agent/state.json` if present; otherwise create it.
2. Ingest `intel/` and record file hashes/summaries.
3. Discover optional data inputs:
   - user-provided Google Search Console exports for queries, pages, CTR, impressions, position, index coverage, or Core Web Vitals
   - competitor keyword/rank exports from Ahrefs, Semrush, Moz, Serpstat, DataForSEO, Search Console, or manually prepared CSV/JSON
   - SERP exports for seed keywords
   - competitor URL lists or seed keyword lists
   - existing analytics/rank-tracking notes in project docs
4. Scan the project with File System MCP:
   - package manager and scripts
   - framework markers: `next.config.*`, `app/`, `pages/`, `src/`, `vite.config.*`, `astro.config.*`, `nuxt.config.*`, static HTML
   - route files, layouts, document/head files, metadata exports, MD/MDX content, robots.txt, sitemap files
   - existing SEO dependencies such as `next-seo`, `react-helmet-async`, sitemap generators, schema utilities
5. Use AST Parser/Linter MCP to classify framework and metadata ownership points.
6. Determine or request the local dev server URL. If no server is running and a safe dev script exists, start the project-defined dev server command and record it in state.
7. Select relevant industry playbook(s) from `playbooks/industry/` and record the selection in `project_manifesto.md`.
8. Run packaged evidence collectors when inputs are available:
   - `scripts/collect_static_seo.py` for status codes, source HTML SEO tags, duplicate titles/meta, source links, images, and JSON-LD.
   - `scripts/collect_rendered_seo.py` for rendered DOM SEO evidence through `agent-browser`.
   - `scripts/import_gsc.py` for user-provided Google Search Console exports.
   - `scripts/import_competitor_keywords.py` for user-provided target and competitor keyword/rank exports.
   - `scripts/collect_pagespeed_crux.py` only for public URLs when the user authorizes optional external API checks.
   - `scripts/analyze_server_logs.py` only when the user provides server logs for local processing.
9. Use `agent-browser` to inspect the homepage and representative routes:
   - homepage
   - core landing pages
   - product/service/detail pages
   - blog/article/content pages
   - any route templates inferred from the framework
10. If competitor URLs are provided and public access is approved, use `agent-browser` snapshots to inspect their visible title, meta description, H1/H2 structure, answer blocks, schema types, internal content architecture, and performance cues. Do not scrape private, paywalled, blocked, or disallowed pages.
11. Generate `project_manifesto.md`.
12. Stop and ask for user approval.

`project_manifesto.md` schema:

```markdown
# Project Manifesto

## Evidence
- Knowledge base files ingested:
- Source files inspected:
- Rendered URLs inspected:
- Data imports discovered:
- Competitor URLs inspected:
- Unknowns / assumptions:

## Tech Stack
- Framework:
- Rendering model:
- Router:
- Metadata ownership files:
- SEO-related dependencies:
- Selected industry playbook(s):

## Brand Identity
- Brand name:
- Value proposition:
- Trust/E-E-A-T assets found:
- Claims that need user verification:

## Target Audience
- Primary audience:
- Secondary audiences:
- YMYL risk classification:
- Search intents:

## Keyword Hubs
| Hub | Primary Keyword | Secondary Keywords | Long-tail / Conversational Queries | Intent | Existing URL | Gap |

## Search Console Baseline
| Query/Page | Clicks | Impressions | CTR | Avg Position | Opportunity Type | Confidence |

## SERP Competitor Discovery
| Query Cluster | SERP Competitors | Evidence Source | Overlap Signal | Verification Status |

## Competitor Baseline
| Competitor | Type (Business/SERP/Content) | Source of Evidence | Competing Topic/URL | Notes | Verification Status |

## Competitor Keyword Baseline
| Keyword/Cluster | Competitor(s) Ranking | Target URL | Gap Type | Intent | Evidence Source | Confidence |

## Load-Speed Baseline
| URL | Evidence Type | LCP/TTFB/CLS/INP/FCP When Available | Suspected Bottleneck | Confidence |

## Strategic Positioning
- Topical authority opportunities:
- AI answer extraction opportunities:
- Competitor keyword opportunities:
- Search Console opportunities:
- Internal linking opportunities:
- Load-speed opportunities:
- Technical constraints:

## Approval Request
Approve this manifesto before Phase 2 begins.
```

Competitor rules:

- If competitor URLs are present in the code, docs, user notes, or provided data, use them.
- If external SERP research is not explicitly approved, list competitor hypotheses as `Verification Status: unverified`.
- Do not fabricate market data.
- Distinguish competitor types:
  - business competitor: competes commercially but may not rank for the same queries
  - SERP competitor: ranks repeatedly for target query clusters
  - content competitor: owns the content format/topic users expect
- When competitor keyword or SERP exports are not available, create a data request instead of inventing keyword volumes, rankings, or difficulty scores.

## Phase 2: Deep SEO Audit and Dynamic Checklist

Goal: cross-reference source code, rendered DOM, and the `intel/` SEO rules to produce an actionable checklist. Do not edit code.

Required audits:

```yaml
critical_technical_seo:
  - robots.txt RFC 9309 behavior and size/status risks
  - XML sitemap validity, boundaries, namespace use, lastmod, hreflang, and nesting
  - canonical presence, uniqueness, target status, noindex conflicts, chains, loops
  - indexability meta and HTTP header conflicts where visible in code
  - rendered DOM vs source/framework ownership for title, meta, canonical, robots, H1, links, JSON-LD
  - CSR shell risk, hydration evidence, heavy client scripts, render-blocking resources
  - Core Web Vitals: LCP, CLS, INP, TTFB, FCP from agent-browser vitals when available
  - mobile-first parity for content, headings, links, metadata, and schema
  - structured data syntax, eligibility, absolute URLs, visible-content parity
  - packaged structured data validation using scripts/validate_structured_data.py when JSON-LD exists
  - crawl traps: parameters, session IDs, unbounded pagination/search, duplicate routes
  - internal graph risks: orphan pages, excessive depth, PageRank dilution, link count excess
performance_load_speed:
  - LCP candidate discoverability in initial HTML
  - hero image format, dimensions, fetchpriority, preload, lazy-loading mistakes
  - TTFB and server/rendering bottlenecks visible in local evidence or framework config
  - render-blocking CSS and synchronous scripts
  - third-party script count and loading strategy
  - route-level JS weight signals from build output when available
  - font loading and layout shift risks
  - image dimension/aspect-ratio reservations and embed/widget CLS risks
  - INP risk from long tasks, hydration cost, large DOM, client-only rendering, and event handlers
on_page_elements:
  - title length, duplication, keyword placement, brand placement
  - meta description presence, uniqueness, length, CTR quality
  - exactly one H1 per URL and logical H2/H3 hierarchy
  - empty/missing/keyword-stuffed alt text
  - weak anchor text, broken internal links, missing contextual links
  - Open Graph/Twitter metadata when social previews matter
content_semantic_gaps:
  - intent mismatch
  - missing concise answer blocks for generative/AI search
  - entity gaps and ambiguity
  - missing author, citation, editorial, date, review, policy, or trust signals
  - weak hub-and-spoke coverage
  - duplicate/thin/scaled programmatic content risk
  - off-page strategic risks: toxic link patterns, anchor distribution, unlinked mentions, PR assets
competitor_keyword_analysis:
  - missing keywords: competitors rank and target site does not rank or has no mapped page
  - weak keywords: target ranks behind competitors for the same intent
  - shared keywords: all parties rank and CTR/title/meta/content differentiation matters
  - unique keywords: target ranks where competitors do not; protect these pages from risky rewrites
  - cannibalized keywords: multiple target URLs compete for the same query cluster
  - decayed keywords: GSC/rank export shows ranking or click decline over time
  - map every keyword gap to a current URL, new content recommendation, or "do not target" rationale
serp_competitor_discovery:
  - identify repeated domains across provided SERP exports or user-approved SERP data
  - group competitors by query cluster, intent, content type, and SERP feature pattern
  - distinguish ranking competitors from aspirational brand competitors
competitor_content_entity_gap:
  - compare competitor title/H1/H2 patterns, entity coverage, schema types, media usage, answer blocks, trust signals, and internal link architecture
  - extract patterns only; do not copy competitor wording or claims
gsc_opportunity_mining:
  - high-impression low-CTR queries for title/meta/snippet testing
  - positions 4-20 for striking-distance improvements
  - pages with many impressions but weak query-page alignment
  - pages with query cannibalization or declining clicks/impressions
  - index coverage and Core Web Vitals export issues when provided
server_log_analysis:
  - process user-provided access logs with scripts/analyze_server_logs.py
  - identify Googlebot crawl frequency, 3xx/4xx/5xx crawl waste, parameter traps, internal search crawling, and low-value URL patterns
  - never request production logs unless the user explicitly provides or authorizes them
ai_visibility:
  - direct answer blocks, concise definitions, FAQs/Q&A where appropriate, citation clarity, schema disambiguation, sameAs signals, author/trust signals, and non-promotional tone
  - mark AI citation visibility claims as unverified without user-provided external evidence
internal_link_graph_scoring:
  - build .seo-agent/internal_link_graph.json when enough URLs are known
  - score inbound links, outbound links, click depth, orphan risk, anchor diversity, hub/spoke role, priority-page support, and link-count excess
prioritization_scoring:
  - run scripts/score_opportunities.py after seo_opportunities.json is written
  - use score and priority_band to order Phase 3 execution recommendations
monitoring_mode:
  - when requested or configured, use configs/monitoring.example.json and scripts/monitor_seo.py to compare snapshots across runs
  - monitor metadata regressions, status changes, structured data errors, CWV/PageSpeed deltas, sitemap drift, broken links, and GSC/rank deltas when evidence exists
industry_playbooks:
  - apply the selected playbook(s) to interpret findings without overriding the core safety rules
  - keep industry-specific recommendations evidence-bound and avoid generic boilerplate
```

Write `seo_competitor_keyword_analysis.md` when competitor, SERP, GSC, seed keyword, or competitor URL data exists. If no data exists, create the file as a data-request artifact with explicit missing inputs.

```markdown
# SEO Competitor Keyword Analysis

## Data Sources
| Source | Type | Date/Export | Coverage | Confidence |

## SERP Competitor Discovery
| Query Cluster | Repeated SERP Competitors | Business Competitors | Content Format | Evidence | Confidence |

## Keyword Gap Matrix
| Keyword/Cluster | Intent | Gap Type | Target URL | Competitor URL(s) | Evidence | Priority | Confidence |

## Competitor Content and Entity Gaps
| Target URL | Competitor URL(s) | Missing Entity/Topic/Format | Evidence | Recommended Action | Copying Risk |

## Priority Recommendations
| ID | Opportunity | Existing/New URL | Expected Impact | Validation Method | Failure Signal | Leading Indicator |

## Data Requests
| Needed Data | Why It Matters | Acceptable Format |
```

Write `seo_performance_audit.md` for the inspected routes:

```markdown
# SEO Performance and Load-Speed Audit

## Evidence
| URL | Evidence Type | Tool/Command | Notes |

## Vitals and Speed Signals
| URL | LCP | INP/TBT | CLS | FCP | TTFB | Evidence Confidence |

## Bottleneck Inventory
| URL | Bottleneck | Evidence | SEO/User Impact | Proposed Fix | Files Likely Touched | Validation Method |

## Route-Level Priorities
| Route/Template | Priority | Reason | Expected Impact | Failure Signal | Leading Indicator |
```

Write `seo_dynamic_checklist.md`:

```markdown
# SEO Dynamic Checklist

## Audit Scope
- Approved manifesto:
- URLs inspected:
- Files inspected:
- Browser evidence:
- Imported data:
- Opportunity JSON:

## Critical Technical SEO
| ID | Severity | Finding | Evidence | SEO Rule | Proposed Fix | Files Likely Touched | Risk | Requires User Content? | Expected Impact | Validation Method | Failure Signal | Leading Indicator | Dependencies |

## Website Load Speed and Core Web Vitals
| ID | Severity | Finding | Evidence | SEO Rule | Proposed Fix | Files Likely Touched | Risk | Requires User Content? | Expected Impact | Validation Method | Failure Signal | Leading Indicator | Dependencies |

## On-Page Elements
| ID | Severity | Finding | Evidence | SEO Rule | Proposed Fix | Files Likely Touched | Risk | Requires User Content? | Expected Impact | Validation Method | Failure Signal | Leading Indicator | Dependencies |

## Content and Semantic Gaps
| ID | Severity | Finding | Evidence | SEO Rule | Proposed Fix | Files Likely Touched | Risk | Requires User Content? | Expected Impact | Validation Method | Failure Signal | Leading Indicator | Dependencies |

## Competitor Keyword and Ranking Opportunities
| ID | Severity | Keyword/Cluster | Gap Type | Competitor Evidence | Target URL | Proposed Fix | Risk | Requires User Content? | Expected Impact | Validation Method | Failure Signal | Leading Indicator | Dependencies |

## Google Search Console Opportunities
| ID | Severity | Query/Page | GSC Evidence | Opportunity Type | Proposed Fix | Files Likely Touched | Risk | Requires User Content? | Expected Impact | Validation Method | Failure Signal | Leading Indicator | Dependencies |

## AI Search / GEO Opportunities
| ID | Severity | Finding | Evidence | Proposed Fix | Files Likely Touched | Risk | Requires User Content? | Expected Impact | Validation Method | Failure Signal | Leading Indicator | Dependencies |

## Internal Link Graph Opportunities
| ID | Severity | URL/Cluster | Graph Evidence | Proposed Fix | Files Likely Touched | Risk | Requires User Content? | Expected Impact | Validation Method | Failure Signal | Leading Indicator | Dependencies |

## Out of Scope / Needs Explicit Authorization
| Item | Reason | Recommended Next Step |

## Approval Request
Approve all items or list the item IDs to execute in Phase 3.
```

Also write `seo_opportunities.json` conforming to `schemas/seo-opportunities.schema.json`. Include every checklist item and every strategic data-only opportunity, even when the item is not code-fixable.
After writing it, run `scripts/score_opportunities.py --input seo_opportunities.json` and use `.seo-agent/opportunity_scores.json` to sort recommendations by priority band.

Minimum `seo_opportunities.json` shape:

```json
{
  "schema_version": 1,
  "generated_at": "ISO-8601 timestamp",
  "project": {
    "brand": "string",
    "site_url": "string or null"
  },
  "source_evidence": [
    {
      "id": "EV-001",
      "type": "rendered_dom",
      "path_or_url": "http://localhost:3000/",
      "confidence": "observed",
      "notes": "agent-browser snapshot and vitals"
    }
  ],
  "opportunities": [
    {
      "id": "COMP-001",
      "module": "competitor_keyword_gap",
      "severity": "high",
      "finding": "Competitors rank for a commercial query cluster with no mapped target page.",
      "evidence": ["EV-002", "EV-003"],
      "seo_rule": "Map every validated keyword gap to an existing URL, new page recommendation, or do-not-target rationale.",
      "proposed_fix": "Create or improve the mapped landing page with differentiated entity coverage and internal links.",
      "files_likely_touched": ["app/services/page.tsx"],
      "urls": ["https://example.com/services"],
      "keywords": ["example commercial query"],
      "competitors": ["competitor.example"],
      "risk": "Requires factual product/service details from the user.",
      "requires_user_content": true,
      "expected_impact": "Improve relevance for a validated commercial cluster.",
      "validation_method": "Re-run rendered DOM extraction and compare future GSC query/page metrics.",
      "failure_signal": "No impressions, CTR, or ranking movement after the agreed measurement window.",
      "leading_indicator": "Improved query-page alignment and increased impressions for the mapped cluster.",
      "dependencies": [],
      "confidence": "provided",
      "status": "proposed"
    }
  ]
}
```

Severity definitions:

```yaml
severity:
  critical: blocks crawl, indexation, canonical consolidation, rich-result eligibility, or renders core content invisible
  high: likely suppresses rankings, AI citations, Core Web Vitals, or mobile-first parity
  medium: harms relevance, CTR, internal authority flow, or structured understanding
  low: polish, monitoring, or future strategic improvement
```

Opportunity identifiers:

```yaml
id_prefixes:
  TECH: critical technical SEO
  PERF: website load speed and Core Web Vitals
  ONPAGE: on-page elements
  CONTENT: content and semantic gaps
  COMP: competitor keyword, SERP, and content/entity gaps
  GSC: Google Search Console opportunity mining
  AISEO: AI search, AEO, GEO, and citation-readiness
  LINK: internal link graph scoring
  REPORT: reporting or measurement improvements
```

Competitive gap definitions:

```yaml
keyword_gap_types:
  missing: competitor ranks and the target site does not have a mapped ranking URL
  weak: target ranks but competitor outranks it for the same intent
  shared: target and competitors rank; optimize differentiation, CTR, and entity depth
  unique: target ranks where competitors do not; protect and monitor
  cannibalized: multiple target URLs compete for the same query cluster
  decayed: prior target performance declined in rank, clicks, impressions, or CTR
  not_relevant: gap exists but does not match audience, offer, geography, or business value
confidence:
  observed: directly observed in source code, rendered DOM, or agent-browser evidence
  provided: imported from user-provided GSC, rank, keyword, or SERP exports
  inferred: inferred from code/content patterns and marked as requiring validation
  unverified: hypothesis without enough evidence; never use as the sole basis for code edits
```

Pause after writing the checklist. Do not edit code until approval is explicit.

## Phase 3: Safe Code Execution

Goal: implement only approved checklist items with narrow, reversible, framework-correct edits.

Required execution loop for each approved item:

```yaml
per_item_loop:
  - confirm the approved item exists in seo_dynamic_checklist.md and seo_opportunities.json
  - classify item as code-fixable, content-needed, data-only, or external-authorization-needed
  - re-read affected files with File System MCP
  - record pre-edit hash and before excerpt
  - parse affected files with AST Parser/Linter MCP
  - choose framework-specific edit point
  - create an in-memory patch
  - review diff for scope, duplicate metadata, escaping, and user-content fabrication
  - apply patch with File System MCP only after diff review
  - re-read changed files
  - run AST/lint/format/typecheck/build validation where available
  - append change evidence to .seo-agent/state.json
  - update matching seo_opportunities.json status to executed, blocked, or deferred
```

Framework-specific rules:

```yaml
nextjs_app_router:
  detection: app/layout.tsx or app/**/page.tsx
  metadata:
    - use exported metadata or generateMetadata in layout/page files.
    - site-wide defaults belong in app/layout.tsx.
    - page-specific metadata belongs in the closest route segment.
    - use alternates.canonical for canonicals.
    - use robots metadata for index/follow directives.
    - do not use next/head in App Router routes.
  json_ld:
    - inject JSON-LD in a server component when possible.
    - escape "<" as "\\u003c" before dangerouslySetInnerHTML.
nextjs_pages_router:
  detection: pages/_app.*, pages/_document.*, pages/**/*.tsx
  metadata:
    - use next/head in page components or established SEO wrapper.
    - avoid duplicate title/meta/canonical across _app and pages.
react_vite_spa:
  detection: vite.config.*, index.html, src/main.*
  metadata:
    - prefer existing head management library if present.
    - if no head manager exists, update index.html for global defaults and recommend SSR/SSG for route-specific SEO.
    - flag route-specific metadata that only appears after client JS as high risk.
static_html:
  detection: "*.html"
  metadata:
    - parse HTML and edit head/body structurally.
    - preserve existing formatting where feasible.
mdx_markdown_content:
  detection: "*.md", "*.mdx"
  metadata:
    - use frontmatter fields if the project already supports them.
    - do not invent author credentials, dates, reviews, or citations.
xml_robots_sitemaps:
  detection: robots.txt, sitemap*.xml
  edits:
    - preserve UTF-8.
    - validate XML after edits.
    - do not add disallow rules that hide important public pages without approval.
```

Content safety:

- Do not invent facts, prices, reviews, author credentials, citations, stock status, return policies, medical/legal/financial claims, or first-hand experience.
- If a fix requires factual content the codebase does not contain, create a TODO in the checklist/report and ask the user for source material.
- Prefer improving structure, metadata wiring, and extraction clarity over generating unsupported claims.
- Do not copy competitor copy, page structure verbatim, proprietary claims, review language, imagery, or schema facts.
- Competitor findings can justify creating differentiated coverage, stronger information architecture, clearer answer blocks, or metadata experiments; they cannot justify plagiarism.
- GSC-derived fixes may adjust titles, meta descriptions, headings, internal links, and page-query alignment, but do not delete or redirect ranking pages without explicit approval.

Diff safety:

```yaml
diff_requirements:
  - one checklist item per logical patch when practical
  - no unrelated refactors
  - no dependency additions unless the checklist item explicitly requires and user approves them
  - no mass route rewrites without batching
  - preserve user changes detected after baseline hashing
```

## Phase 4: Validation and Reporting

Goal: prove changes render correctly, preserve build health, and produce an exhaustive changelog.

Required validation:

1. Run AST Parser/Linter MCP validation on touched files.
2. Run project lint/typecheck/build commands exposed by the project where feasible.
3. Use `agent-browser` to revisit every modified route or representative template route:
   - `agent-browser open "$URL"`
   - `agent-browser wait --load networkidle`
   - `agent-browser snapshot -i --json`
   - run the SEO rendered extraction script from this skill
   - `agent-browser vitals "$URL"` when performance/hydration was touched
   - run the load-speed diagnostics extraction script when any `PERF-*` item was touched
4. Confirm:
   - title, meta description, canonical, robots, hreflang, and JSON-LD render as intended
   - exactly one H1 where required
   - no duplicate canonical or contradictory noindex/canonical
   - structured data parses as JSON and matches visible content
   - mobile-critical content is not hidden from the rendered DOM
   - no new hydration or severe vitals regression is evident from available evidence
5. Validate `seo_opportunities.json` against `schemas/seo-opportunities.schema.json` if a JSON schema validator is available; otherwise manually verify required fields are present.
6. Run `scripts/score_opportunities.py --input seo_opportunities.json` if not already run after Phase 2.
7. If monitoring mode is requested or `configs/monitoring.example.json` has been adapted for the project, run `scripts/monitor_seo.py` and include deltas.
8. Write `seo_changelog_report.md`.

`seo_changelog_report.md` schema:

```markdown
# SEO Changelog Report

## Executive Summary
- Date:
- Approved checklist items executed:
- Files touched:
- Routes validated:
- Validation status:

## Changes by Checklist Item
| ID | Severity | Module | SEO Rule | File(s) | Before | After | Validation Evidence | Expected Impact | Failure Signal | Leading Indicator | Residual Risk |

## Files Touched
| File | Hash Before | Hash After | Change Type | Reason |

## Rendered Validation
| URL | Title | Meta Description | Canonical | H1 Count | JSON-LD Types | Vitals/Hydration Evidence | Status |

## Competitor Keyword and Ranking Outcomes
| Opportunity ID | Keyword/Cluster | Gap Type | Target URL | Action Taken | Validation Method | Status |

## Performance and Load-Speed Outcomes
| Opportunity ID | URL | Bottleneck | Action Taken | Before Evidence | After Evidence | Status |

## Search Console Outcomes
| Opportunity ID | Query/Page | Baseline | Action Taken | Follow-Up Metric | Status |

## AI Search / GEO Outcomes
| Opportunity ID | Page/Entity | Action Taken | Extraction/Citation Readiness Evidence | Status |

## Internal Link Graph Outcomes
| Opportunity ID | URL/Cluster | Graph Issue | Action Taken | Follow-Up Metric | Status |

## Technical SEO Outcomes
- Crawl/indexability:
- Canonicalization:
- Structured data:
- Core Web Vitals:
- Mobile-first parity:
- Internal linking:

## Machine-Readable Artifacts
- seo_opportunities.json:
- seo_competitor_keyword_analysis.md:
- seo_performance_audit.md:
- .seo-agent/internal_link_graph.json:
- .seo-agent/opportunity_scores.json:
- .seo-agent/monitoring_snapshot.json:

## Server Log and Crawl-Budget Outcomes
| Opportunity ID | Evidence | Action Taken | Follow-Up Metric | Status |

## Content and E-E-A-T Outcomes
- Trust signals improved:
- Unsupported claims avoided:
- User-provided content still needed:

## Not Executed
| Checklist ID | Reason | Next Step |

## Rollback Notes
- Patch groups:
- Files to inspect if rollback is requested:
```

Before final response, close `agent-browser` unless the user asked to keep it open.

## Completion Criteria

The SEO run is complete only when:

```yaml
complete_when:
  - intel files were read and summarized in state
  - project_manifesto.md exists and was approved
  - seo_dynamic_checklist.md exists and was approved wholly or by item IDs
  - seo_opportunities.json exists and mirrors the approved checklist items
  - seo_competitor_keyword_analysis.md exists or documents missing competitor/keyword data requests
  - seo_performance_audit.md exists when a rendered site was available
  - packaged evidence scripts were run where their inputs were available or blockers are documented
  - .seo-agent/opportunity_scores.json exists after seo_opportunities.json when scoring is applicable
  - approved code changes were applied through safe diffs
  - touched files passed available AST/lint/typecheck/build validation or blockers are documented
  - modified pages were revisited with agent-browser
  - seo_changelog_report.md contains every touched file, before/after states, SEO rule justification, validation evidence, expected impact, failure signal, and leading indicator
```

If any criterion cannot be met, report the blocker precisely and do not claim completion.
