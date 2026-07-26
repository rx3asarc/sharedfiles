#!/usr/bin/env bash
# Install Video Intelligence for either Claude Code or Codex.
set -euo pipefail

agent="${1:-}"
root="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

case "$agent" in
  claude)
    destination="$HOME/.claude/skills/video-intelligence"
    ;;
  codex)
    destination="$HOME/.codex/skills/video-intelligence"
    ;;
  *)
    echo "Usage: bash install_skill.sh claude"
    echo "   or: bash install_skill.sh codex"
    exit 1
    ;;
esac

mkdir -p "$destination"
rsync -a --delete \
  --exclude '.git' \
  --exclude '__pycache__' \
  --exclude 'output' \
  --exclude 'tmp' \
  --exclude 'media' \
  "$root/" "$destination/"

echo "Installed Video Intelligence for $agent."
echo "Open a new $agent session, then point it at a local video."
