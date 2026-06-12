#!/usr/bin/env python3
"""Phase and tool guard for the Autonomous SEO Architect skill.

The guard is intentionally host-agnostic. It can be called from a hook runner,
CI job, or manually. It reads optional JSON from stdin and exits non-zero when
an operation violates the skill's phase gates.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from pathlib import Path
from typing import Any


DEFAULT_STATE: dict[str, Any] = {
    "schema_version": 1,
    "current_phase": "phase_1_project_analysis",
    "approvals": {
        "phase_1_manifesto": False,
        "phase_2_checklist": False,
    },
    "dev_server": {
        "url": None,
        "start_command": None,
    },
    "targets": [],
    "artifacts": {
        "manifesto": "project_manifesto.md",
        "checklist": "seo_dynamic_checklist.md",
        "report": "seo_changelog_report.md",
        "evidence_dir": ".seo-agent/evidence",
    },
    "file_hashes_before_edit": {},
    "changes": [],
}

FORBIDDEN_SHELL_PATTERNS = (
    re.compile(r"\bplaywright\b", re.IGNORECASE),
    re.compile(r"\bpuppeteer\b", re.IGNORECASE),
    re.compile(r"\bnpx\s+(-y\s+)?playwright\b", re.IGNORECASE),
)

PHASE_ARTIFACTS = {
    "project_manifesto.md",
    "seo_dynamic_checklist.md",
    "seo_changelog_report.md",
    "SKILL.md",
    "README.md",
    "GEMINI.md",
    "LICENSE",
    "gemini-extension.json",
    "hooks.json",
    ".mcp.json",
    ".codex-plugin/plugin.json",
    ".claude-plugin/plugin.json",
    ".claude-plugin/marketplace.json",
    "mcp/claude.mcp.json",
}

PHASE_ARTIFACT_PREFIXES = (
    ".seo-agent/",
    "intel/",
    "hooks/",
    "scripts/",
    "schemas/",
    "skills/",
    ".codex-plugin/",
    ".claude-plugin/",
    "mcp/",
    ".github/",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Guard SEO agent phase transitions and tool usage.")
    parser.add_argument(
        "event",
        choices=("init-state", "pre-phase2", "pre-edit", "pre-shell", "pre-complete"),
    )
    parser.add_argument("--workspace", default=".", help="Workspace root containing .seo-agent/state.json")
    parser.add_argument("--target", default="", help="Target file path when known")
    parser.add_argument("--tool", default="", help="Tool name when known")
    parser.add_argument("--json", action="store_true", help="Emit a JSON result")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    workspace = Path(args.workspace).resolve()
    payload = read_stdin_json()
    state_path = workspace / ".seo-agent" / "state.json"

    if args.event == "init-state":
        state = load_state_or_default(state_path)
        write_state(state_path, state)
        return emit(args, True, ["Initialized SEO state."], [])

    if args.event == "pre-shell":
        return check_pre_shell(args, payload)

    if args.event == "pre-edit":
        target = first_present(
            args.target,
            os.environ.get("SEO_HOOK_TARGET", ""),
            extract_path(payload),
        )
        rel_target = normalize_target(workspace, target)
        if rel_target and is_phase_artifact(rel_target):
            return emit(args, True, [f"Allowed phase artifact edit: {rel_target}"], [])

    state = load_state(state_path)
    if state is None:
        return emit(
            args,
            False,
            [],
            ["Missing .seo-agent/state.json. Run the skill Phase 1 setup or call init-state first."],
        )

    if args.event == "pre-phase2":
        return check_pre_phase2(args, workspace, state)
    if args.event == "pre-edit":
        return check_pre_edit(args, workspace, state, payload)
    if args.event == "pre-complete":
        return check_pre_complete(args, workspace, state)

    return emit(args, False, [], [f"Unsupported event: {args.event}"])


def read_stdin_json() -> dict[str, Any]:
    if sys.stdin.isatty():
        return {}
    raw = sys.stdin.read().strip()
    if not raw:
        return {}
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        return {"_raw": raw}
    return parsed if isinstance(parsed, dict) else {"payload": parsed}


def load_state(path: Path) -> dict[str, Any] | None:
    if not path.is_file():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return data if isinstance(data, dict) else None


def load_state_or_default(path: Path) -> dict[str, Any]:
    return load_state(path) or json.loads(json.dumps(DEFAULT_STATE))


def write_state(path: Path, state: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")


def check_pre_phase2(args: argparse.Namespace, workspace: Path, state: dict[str, Any]) -> int:
    approvals = state.get("approvals", {})
    errors: list[str] = []
    if approvals.get("phase_1_manifesto") is not True:
        errors.append("Phase 2 is blocked until approvals.phase_1_manifesto is true.")
    if not (workspace / "project_manifesto.md").is_file():
        errors.append("Phase 2 is blocked because project_manifesto.md does not exist.")
    return emit(args, not errors, [], errors)


def check_pre_edit(
    args: argparse.Namespace,
    workspace: Path,
    state: dict[str, Any],
    payload: dict[str, Any],
) -> int:
    target = first_present(
        args.target,
        os.environ.get("SEO_HOOK_TARGET", ""),
        extract_path(payload),
    )
    rel_target = normalize_target(workspace, target)
    warnings: list[str] = []
    errors: list[str] = []

    if not rel_target:
        warnings.append("No target path was provided; applying approval gate only.")
    elif is_phase_artifact(rel_target):
        return emit(args, True, [f"Allowed phase artifact edit: {rel_target}"], [])

    approvals = state.get("approvals", {})
    if approvals.get("phase_2_checklist") is not True:
        errors.append("Project code edits are blocked until approvals.phase_2_checklist is true.")
    if not (workspace / "seo_dynamic_checklist.md").is_file():
        errors.append("Project code edits are blocked because seo_dynamic_checklist.md does not exist.")

    if rel_target:
        baseline_hashes = state.get("file_hashes_before_edit", {})
        if isinstance(baseline_hashes, dict) and rel_target in baseline_hashes:
            current_path = workspace / rel_target
            if current_path.is_file():
                current_hash = sha256_file(current_path)
                if current_hash != baseline_hashes[rel_target]:
                    errors.append(
                        f"{rel_target} changed after the Phase 3 baseline; re-read and reconcile before editing."
                    )

    return emit(args, not errors, warnings, errors)


def check_pre_shell(args: argparse.Namespace, payload: dict[str, Any]) -> int:
    command = first_present(
        os.environ.get("SEO_HOOK_COMMAND", ""),
        extract_command(payload),
        payload.get("_raw", "") if isinstance(payload.get("_raw"), str) else "",
    )
    errors = []
    if command and any(pattern.search(command) for pattern in FORBIDDEN_SHELL_PATTERNS):
        errors.append("Shell command blocked: this SEO skill requires agent-browser, not Playwright or Puppeteer.")
    return emit(args, not errors, [], errors)


def check_pre_complete(args: argparse.Namespace, workspace: Path, state: dict[str, Any]) -> int:
    approvals = state.get("approvals", {})
    warnings: list[str] = []
    errors: list[str] = []

    required = [
        ("project_manifesto.md", approvals.get("phase_1_manifesto") is True),
        ("seo_dynamic_checklist.md", approvals.get("phase_2_checklist") is True),
        ("seo_changelog_report.md", True),
    ]
    for filename, approved in required:
        if not (workspace / filename).is_file():
            warnings.append(f"Completion check: {filename} is missing.")
        if filename != "seo_changelog_report.md" and not approved:
            warnings.append(f"Completion check: approval for {filename} is not recorded in state.")

    evidence_dir = workspace / ".seo-agent" / "evidence"
    if not evidence_dir.exists():
        warnings.append("Completion check: .seo-agent/evidence is missing.")

    # Stop hooks are advisory in hooks.json, so emit success with warnings.
    return emit(args, not errors, warnings, errors)


def extract_path(payload: dict[str, Any]) -> str:
    candidates = [
        payload.get("target"),
        payload.get("path"),
        payload.get("file_path"),
        payload.get("filePath"),
        nested(payload, ("tool_input", "path")),
        nested(payload, ("tool_input", "file_path")),
        nested(payload, ("tool_input", "filePath")),
        nested(payload, ("params", "path")),
        nested(payload, ("params", "file_path")),
    ]
    for value in candidates:
        if isinstance(value, str) and value.strip():
            return value
    return ""


def extract_command(payload: dict[str, Any]) -> str:
    candidates = [
        payload.get("command"),
        nested(payload, ("tool_input", "command")),
        nested(payload, ("params", "command")),
    ]
    for value in candidates:
        if isinstance(value, str) and value.strip():
            return value
    return ""


def nested(payload: dict[str, Any], keys: tuple[str, ...]) -> Any:
    current: Any = payload
    for key in keys:
        if not isinstance(current, dict):
            return None
        current = current.get(key)
    return current


def first_present(*values: Any) -> str:
    for value in values:
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ""


def normalize_target(workspace: Path, raw_target: str) -> str:
    if not raw_target:
        return ""
    path = Path(raw_target)
    if not path.is_absolute():
        path = workspace / path
    try:
        resolved = path.resolve()
        rel = resolved.relative_to(workspace)
    except ValueError:
        return ""
    return rel.as_posix()


def is_phase_artifact(rel_path: str) -> bool:
    if rel_path in PHASE_ARTIFACTS:
        return True
    return any(rel_path.startswith(prefix) for prefix in PHASE_ARTIFACT_PREFIXES)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def emit(args: argparse.Namespace, ok: bool, warnings: list[str], errors: list[str]) -> int:
    result = {
        "ok": ok,
        "event": args.event,
        "warnings": warnings,
        "errors": errors,
    }
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        for warning in warnings:
            print(f"warning: {warning}", file=sys.stderr)
        for error in errors:
            print(f"error: {error}", file=sys.stderr)
    return 0 if ok else 2


if __name__ == "__main__":
    raise SystemExit(main())
