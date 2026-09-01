#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPOSITORY_ROOT="$(cd -- "$SCRIPT_DIR/.." && pwd)"

mkdir -p "$HOME/.codex"
cp "$REPOSITORY_ROOT/AGENTS.md" "$HOME/.codex/AGENTS.md"
