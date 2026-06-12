---
name: autonomous-seo-architect
description: Use when auditing or optimizing a website/codebase for technical SEO, on-page SEO, rendered DOM metadata, Core Web Vitals, structured data, internal linking, topical authority, AI search visibility, or safe framework-specific SEO code changes.
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
      - apply safe diffs to project files
      - write seo_changelog_report.md
      - persist .seo-agent/state.json and evidence files
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
```

Use the host-specific MCP binding for the active runtime:

- Codex/default hosts: `.mcp.json`, using `${workspaceFolder}`.
- Claude Code: `mcp/claude.mcp.json`, using `${CLAUDE_PROJECT_DIR}`.
- Gemini CLI: `gemini-extension.json`, using `${workspacePath}`.

Use `scripts/seo_state_guard.py` to enforce phase gates wherever the host supports hooks. Claude Code loads `hooks/hooks.json` natively and blocks `PreToolUse` violations through exit code 2. Codex-compatible hosts can wire `hooks.json` as a companion manifest. Gemini CLI extensions do not expose the same hook lifecycle, so enforce the phase gates in reasoning, honor `excludeTools`, and call the guard manually when a check is needed.

## Mandatory Knowledge Ingestion

At the start of every SEO run, read every file in the packaged `intel/` directory. Resolve it in this order:

1. The package/plugin/extension root that contains this `SKILL.md`.
2. The repository root if running from a local clone.
3. A project-local `intel/` directory only when the user intentionally provides one.

If no `intel/` directory is available from those locations, stop and ask for the knowledge base. Do not perform an SEO audit from generic memory alone.

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
  semantic_content:
    - target entities and intent, not keyword density.
    - classify intent as informational, navigational, commercial, transactional, or generative.
    - use SERP-overlap clustering when external SERP data is provided or explicitly approved: 70%+ overlap means one page, 30-70% requires editorial review, below 30% usually requires separate pages.
    - use concise extraction architecture: answer core questions in the first 1-2 sentences of relevant sections.
    - identify entity gaps from competitors, but mark external competitor claims as unverified unless evidence is available.
  off_page:
    - treat backlink, PR, unlinked mention, and disavow work as strategic recommendations unless the user grants external account/tool access.
    - natural profiles have diverse domains, topical relevance, mixed link attributes, varied anchors, and steady velocity.
    - toxic profiles show irrelevant domains, PBN/link-farm patterns, exact-match anchor excess, and unnatural spikes.
    - defensive anchor baseline: about 70% branded, 20% naked URL, 5% generic, 1-5% partial/LSI, and <1% exact-match unless competitor evidence supports otherwise.
    - recommend disavow only for confirmed manual unnatural-link actions or verified negative SEO attacks correlated with traffic/impression loss.
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
    "report": "seo_changelog_report.md",
    "evidence_dir": ".seo-agent/evidence"
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

## Phase 1: Project Analysis and Manifesto Generation

Goal: understand the codebase, rendered site, brand, audience, keyword architecture, and competitor assumptions without editing code.

Required steps:

1. Read `.seo-agent/state.json` if present; otherwise create it.
2. Ingest `intel/` and record file hashes/summaries.
3. Scan the project with File System MCP:
   - package manager and scripts
   - framework markers: `next.config.*`, `app/`, `pages/`, `src/`, `vite.config.*`, `astro.config.*`, `nuxt.config.*`, static HTML
   - route files, layouts, document/head files, metadata exports, MD/MDX content, robots.txt, sitemap files
   - existing SEO dependencies such as `next-seo`, `react-helmet-async`, sitemap generators, schema utilities
4. Use AST Parser/Linter MCP to classify framework and metadata ownership points.
5. Determine or request the local dev server URL. If no server is running and a safe dev script exists, start the project-defined dev server command and record it in state.
6. Use `agent-browser` to inspect the homepage and representative routes:
   - homepage
   - core landing pages
   - product/service/detail pages
   - blog/article/content pages
   - any route templates inferred from the framework
7. Generate `project_manifesto.md`.
8. Stop and ask for user approval.

`project_manifesto.md` schema:

```markdown
# Project Manifesto

## Evidence
- Knowledge base files ingested:
- Source files inspected:
- Rendered URLs inspected:
- Unknowns / assumptions:

## Tech Stack
- Framework:
- Rendering model:
- Router:
- Metadata ownership files:
- SEO-related dependencies:

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

## Competitor Baseline
| Competitor | Source of Evidence | Competing Topic/URL | Notes | Verification Status |

## Strategic Positioning
- Topical authority opportunities:
- AI answer extraction opportunities:
- Internal linking opportunities:
- Technical constraints:

## Approval Request
Approve this manifesto before Phase 2 begins.
```

Competitor rules:

- If competitor URLs are present in the code, docs, user notes, or provided data, use them.
- If external SERP research is not explicitly approved, list competitor hypotheses as `Verification Status: unverified`.
- Do not fabricate market data.

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
  - crawl traps: parameters, session IDs, unbounded pagination/search, duplicate routes
  - internal graph risks: orphan pages, excessive depth, PageRank dilution, link count excess
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
```

Write `seo_dynamic_checklist.md`:

```markdown
# SEO Dynamic Checklist

## Audit Scope
- Approved manifesto:
- URLs inspected:
- Files inspected:
- Browser evidence:

## Critical Technical SEO
| ID | Severity | Finding | Evidence | SEO Rule | Proposed Fix | Files Likely Touched | Risk | Requires User Content? |

## On-Page Elements
| ID | Severity | Finding | Evidence | SEO Rule | Proposed Fix | Files Likely Touched | Risk | Requires User Content? |

## Content and Semantic Gaps
| ID | Severity | Finding | Evidence | SEO Rule | Proposed Fix | Files Likely Touched | Risk | Requires User Content? |

## Out of Scope / Needs Explicit Authorization
| Item | Reason | Recommended Next Step |

## Approval Request
Approve all items or list the item IDs to execute in Phase 3.
```

Severity definitions:

```yaml
severity:
  critical: blocks crawl, indexation, canonical consolidation, rich-result eligibility, or renders core content invisible
  high: likely suppresses rankings, AI citations, Core Web Vitals, or mobile-first parity
  medium: harms relevance, CTR, internal authority flow, or structured understanding
  low: polish, monitoring, or future strategic improvement
```

Pause after writing the checklist. Do not edit code until approval is explicit.

## Phase 3: Safe Code Execution

Goal: implement only approved checklist items with narrow, reversible, framework-correct edits.

Required execution loop for each approved item:

```yaml
per_item_loop:
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
4. Confirm:
   - title, meta description, canonical, robots, hreflang, and JSON-LD render as intended
   - exactly one H1 where required
   - no duplicate canonical or contradictory noindex/canonical
   - structured data parses as JSON and matches visible content
   - mobile-critical content is not hidden from the rendered DOM
   - no new hydration or severe vitals regression is evident from available evidence
5. Write `seo_changelog_report.md`.

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
| ID | Severity | SEO Rule | File(s) | Before | After | Validation Evidence | Residual Risk |

## Files Touched
| File | Hash Before | Hash After | Change Type | Reason |

## Rendered Validation
| URL | Title | Meta Description | Canonical | H1 Count | JSON-LD Types | Vitals/Hydration Evidence | Status |

## Technical SEO Outcomes
- Crawl/indexability:
- Canonicalization:
- Structured data:
- Core Web Vitals:
- Mobile-first parity:
- Internal linking:

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
  - approved code changes were applied through safe diffs
  - touched files passed available AST/lint/typecheck/build validation or blockers are documented
  - modified pages were revisited with agent-browser
  - seo_changelog_report.md contains every touched file, before/after states, SEO rule justification, and validation evidence
```

If any criterion cannot be met, report the blocker precisely and do not claim completion.
