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

## Phases

- Phase 1: Generate `project_manifesto.md`, then pause for approval.
- Phase 2: Generate `seo_dynamic_checklist.md`, then pause for approval.
- Phase 3: Execute only approved checklist items using narrow diffs and AST-aware edits.
- Phase 4: Revisit changed pages with `agent-browser` and write `seo_changelog_report.md`.

## State Guard

Gemini CLI extensions do not provide the Claude-style hook lifecycle used by this package. Enforce the phase gates in reasoning, honor `excludeTools`, and keep `.seo-agent/state.json` current.

When working from a local clone of this repository, initialize local run state with:

```bash
python scripts/seo_state_guard.py init-state --workspace . --json
```

When this package is installed as a Gemini extension, use the same guard script from the installed extension directory if a manual check is needed.
