#!/usr/bin/env bash
# Install the Python tools' dependencies in Claude Code cloud sessions.
# Local sessions are left alone (install with: pip install -r requirements.txt).
set -u
[ "${CLAUDE_CODE_REMOTE:-}" = "true" ] || exit 0
cd "${CLAUDE_PROJECT_DIR:-.}"
python3 -m pip install -q -r requirements.txt 2>/dev/null \
  || python3 -m pip install -q --break-system-packages -r requirements.txt \
  || echo "warning: pip install -r requirements.txt failed; rendering tools may be unavailable" >&2
exit 0
