#!/usr/bin/env sh
set -eu

EVENT="${1:-pre-edit}"
shift || true

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
PACKAGE_ROOT=$(CDPATH= cd -- "$SCRIPT_DIR/.." && pwd)
WORKSPACE="${SEO_AGENT_WORKSPACE:-${CLAUDE_PROJECT_DIR:-$(pwd)}}"
GUARD="$PACKAGE_ROOT/scripts/seo_state_guard.py"

exec python "$GUARD" "$EVENT" --workspace "$WORKSPACE" --json "$@"
