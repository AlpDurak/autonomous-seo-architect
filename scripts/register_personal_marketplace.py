#!/usr/bin/env python3
"""Register this plugin in Codex's default personal marketplace.

Expected layout:
  ~/plugins/autonomous-seo-architect

The generated marketplace entry uses the standard personal marketplace source
path: ./plugins/autonomous-seo-architect
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


PLUGIN_NAME = "autonomous-seo-architect"
MARKETPLACE_NAME = "personal"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Register Autonomous SEO Architect in the personal Codex marketplace.")
    parser.add_argument(
        "--marketplace",
        default=str(Path.home() / ".agents" / "plugins" / "marketplace.json"),
        help="Path to marketplace.json. Defaults to ~/.agents/plugins/marketplace.json.",
    )
    parser.add_argument(
        "--skip-location-check",
        action="store_true",
        help="Register even if this repo is not located at ~/plugins/autonomous-seo-architect.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Replace an existing autonomous-seo-architect marketplace entry.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = Path(__file__).resolve().parents[1]
    expected_root = Path.home() / "plugins" / PLUGIN_NAME
    marketplace_path = Path(args.marketplace).expanduser().resolve()

    if not args.skip_location_check and repo_root.resolve() != expected_root.resolve():
        print(f"Install location check failed: {repo_root}")
        print(f"Clone this repo to: {expected_root}")
        print("Or rerun with --skip-location-check if your Codex marketplace supports this layout.")
        return 2

    plugin_manifest = repo_root / ".codex-plugin" / "plugin.json"
    if not plugin_manifest.is_file():
        print(f"Missing plugin manifest: {plugin_manifest}")
        return 2

    marketplace = load_or_create_marketplace(marketplace_path)
    plugins = marketplace.setdefault("plugins", [])
    if not isinstance(plugins, list):
        print(f"{marketplace_path} field 'plugins' must be an array.")
        return 2

    entry = {
        "name": PLUGIN_NAME,
        "source": {
            "source": "local",
            "path": f"./plugins/{PLUGIN_NAME}",
        },
        "policy": {
            "installation": "AVAILABLE",
            "authentication": "ON_INSTALL",
        },
        "category": "Productivity",
    }

    for index, existing in enumerate(plugins):
        if isinstance(existing, dict) and existing.get("name") == PLUGIN_NAME:
            if not args.force:
                print(f"{PLUGIN_NAME} is already registered in {marketplace_path}. Use --force to replace it.")
                return 2
            plugins[index] = entry
            break
    else:
        plugins.append(entry)

    marketplace_path.parent.mkdir(parents=True, exist_ok=True)
    marketplace_path.write_text(json.dumps(marketplace, indent=2) + "\n", encoding="utf-8")
    print(f"Registered {PLUGIN_NAME} in {marketplace_path}")
    print(f"Next: codex plugin add {PLUGIN_NAME}@{marketplace.get('name', MARKETPLACE_NAME)}")
    return 0


def load_or_create_marketplace(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {
            "name": MARKETPLACE_NAME,
            "interface": {
                "displayName": "Personal",
            },
            "plugins": [],
        }
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a JSON object.")
    payload.setdefault("name", MARKETPLACE_NAME)
    payload.setdefault("interface", {"displayName": "Personal"})
    return payload


if __name__ == "__main__":
    raise SystemExit(main())
