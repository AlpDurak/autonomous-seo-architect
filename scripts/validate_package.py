#!/usr/bin/env python3
"""Validate the public Autonomous SEO Architect package layout."""

from __future__ import annotations

import json
import py_compile
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
JSON_FILES = [
    ".codex-plugin/plugin.json",
    ".claude-plugin/plugin.json",
    ".claude-plugin/marketplace.json",
    ".mcp.json",
    "gemini-extension.json",
    "hooks.json",
    "hooks/hooks.json",
    "mcp/claude.mcp.json",
    "schemas/hooks.schema.json",
    "schemas/seo-data-import.schema.json",
    "schemas/seo-opportunities.schema.json",
    "schemas/seo-state.schema.json",
    ".seo-agent/state.json",
]
PYTHON_FILES = [
    "scripts/analyze_server_logs.py",
    "scripts/build_internal_link_graph.py",
    "scripts/collect_pagespeed_crux.py",
    "scripts/collect_rendered_seo.py",
    "scripts/collect_static_seo.py",
    "scripts/import_competitor_keywords.py",
    "scripts/import_gsc.py",
    "scripts/monitor_seo.py",
    "scripts/seo_state_guard.py",
    "scripts/score_opportunities.py",
    "scripts/seo_utils.py",
    "scripts/register_personal_marketplace.py",
    "scripts/validate_structured_data.py",
    "scripts/validate_package.py",
]


def main() -> int:
    failures: list[str] = []
    failures.extend(check_files_exist())
    failures.extend(check_json())
    failures.extend(check_python())
    failures.extend(check_guard())

    if failures:
        for failure in failures:
            print(f"error: {failure}", file=sys.stderr)
        return 1

    print("Package validation passed.")
    return 0


def check_files_exist() -> list[str]:
    required = [
        "README.md",
        "LICENSE",
        "SKILL.md",
        "GEMINI.md",
        "skills/autonomous-seo-architect/SKILL.md",
        "hooks/seo-phase-gate.ps1",
        "hooks/seo-phase-gate.sh",
        "intel/seo-audit-checklist.md",
        "schemas/seo-opportunities.schema.json",
        "schemas/seo-data-import.schema.json",
        "configs/monitoring.example.json",
        "playbooks/industry/saas.md",
        "playbooks/industry/ecommerce.md",
        "playbooks/industry/local.md",
        "playbooks/industry/publisher.md",
        "playbooks/industry/marketplace.md",
        "playbooks/industry/international.md",
        "playbooks/industry/programmatic.md",
    ]
    return [f"Missing required file: {path}" for path in required if not (ROOT / path).is_file()]


def check_json() -> list[str]:
    errors: list[str] = []
    for path in JSON_FILES:
        try:
            with (ROOT / path).open(encoding="utf-8") as handle:
                json.load(handle)
        except Exception as exc:  # noqa: BLE001 - validation should report all parse failures.
            errors.append(f"{path}: {exc}")
    return errors


def check_python() -> list[str]:
    errors: list[str] = []
    with tempfile.TemporaryDirectory(prefix="asa-pycompile-") as temp_dir:
        temp_root = Path(temp_dir)
        for path in PYTHON_FILES:
            try:
                py_compile.compile(str(ROOT / path), cfile=str(temp_root / f"{Path(path).stem}.pyc"), doraise=True)
            except py_compile.PyCompileError as exc:
                errors.append(f"{path}: {exc.msg}")
    return errors


def check_guard() -> list[str]:
    commands = [
        [
            sys.executable,
            "scripts/seo_state_guard.py",
            "init-state",
            "--workspace",
            ".",
            "--json",
        ],
        [
            sys.executable,
            "scripts/seo_state_guard.py",
            "pre-edit",
            "--workspace",
            ".",
            "--target",
            "project_manifesto.md",
            "--json",
        ],
    ]
    errors: list[str] = []
    for command in commands:
        completed = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=False)
        if completed.returncode != 0:
            errors.append(f"{' '.join(command)} failed: {completed.stderr.strip() or completed.stdout.strip()}")

    blocked = subprocess.run(
        [sys.executable, "scripts/seo_state_guard.py", "pre-shell", "--workspace", "."],
        cwd=ROOT,
        input='{"tool_input":{"command":"npx playwright test"}}',
        text=True,
        capture_output=True,
        check=False,
    )
    if blocked.returncode != 2:
        errors.append("pre-shell did not block Playwright usage")

    return errors


if __name__ == "__main__":
    raise SystemExit(main())
