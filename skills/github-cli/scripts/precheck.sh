#!/usr/bin/env bash
# precheck.sh - check gh CLI installation and auth status.
# Usage: bash precheck.sh
# Exit codes: 0 ready; 1 not installed; 2 not logged in; 3 other.
# Output is ASCII to avoid encoding issues across terminals.

set -u
export LANG=${LANG:-en_US.UTF-8}

echo "[1/3] Check gh CLI installation..."
if ! command -v gh >/dev/null 2>&1; then
  echo "  [FAIL] gh not found. Install with: brew install gh"
  exit 1
fi
GH_PATH=$(command -v gh)
GH_VER=$(gh --version 2>/dev/null | head -1)
echo "  [OK] $GH_PATH"
echo "  [OK] $GH_VER"

echo "[2/3] Check auth status (github.com)..."
AUTH_OUT=$(gh auth status -h github.com 2>&1)
AUTH_RC=$?
if [ $AUTH_RC -ne 0 ]; then
  echo "  [FAIL] Not logged in or token invalid. Run: gh auth login"
  echo "  --- gh output ---"
  echo "$AUTH_OUT" | sed 's/^/  /'
  exit 2
fi
echo "$AUTH_OUT" | sed 's/^/  /'

echo "[3/3] Fetch current user..."
LOGIN=$(gh api user --jq '.login' 2>/dev/null)
if [ -z "$LOGIN" ]; then
  echo "  [WARN] Cannot read user.login. Token scope may be insufficient."
  exit 3
fi
echo "  [OK] Current user: $LOGIN"

echo
echo "All ready. You can start operating GitHub via gh."
exit 0
