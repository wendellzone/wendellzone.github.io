#!/usr/bin/env bash
# rename-user-remotes.sh
# Rewrite all local git remotes from <old> to <new> after a GitHub username change.
#
# Usage:
#   bash rename-user-remotes.sh <old_user> <new_user> [--apply]
#
# By default runs in DRY-RUN mode and only prints what would change.
# Add --apply to actually rewrite the remotes.
#
# Scans up to depth 6 under $HOME by default; override with SEARCH_ROOT env var.

set -u

OLD="${1:-}"
NEW="${2:-}"
MODE="${3:-dry}"   # dry | --apply

if [ -z "$OLD" ] || [ -z "$NEW" ]; then
  echo "Usage: $0 <old_user> <new_user> [--apply]"
  exit 64
fi

ROOT="${SEARCH_ROOT:-$HOME}"
echo "Search root : $ROOT"
echo "Old account : $OLD"
echo "New account : $NEW"
if [ "$MODE" = "--apply" ]; then
  echo "Mode        : APPLY (will rewrite remotes)"
else
  echo "Mode        : DRY-RUN (use --apply to actually rewrite)"
fi
echo

count_total=0
count_changed=0
while IFS= read -r gitdir; do
  repo=$(dirname "$gitdir")
  for r in $(git -C "$repo" remote 2>/dev/null); do
    url=$(git -C "$repo" remote get-url "$r" 2>/dev/null)
    case "$url" in
      *github.com*${OLD}*)
        count_total=$((count_total+1))
        # 保留协议形式：ssh git@github.com:OLD/X | https://github.com/OLD/X
        new_url=$(echo "$url" | sed -E "s#([:/])${OLD}/#\1${NEW}/#")
        echo "[REPO] $repo"
        echo "  $r: $url"
        echo "    -> $new_url"
        if [ "$MODE" = "--apply" ]; then
          git -C "$repo" remote set-url "$r" "$new_url"
          if [ $? -eq 0 ]; then
            echo "    [OK] updated"
            count_changed=$((count_changed+1))
          else
            echo "    [FAIL] git remote set-url failed"
          fi
        fi
        ;;
    esac
  done
done < <(find "$ROOT" -maxdepth 6 -name ".git" -type d 2>/dev/null)

echo
echo "Matched remotes: $count_total"
if [ "$MODE" = "--apply" ]; then
  echo "Updated remotes: $count_changed"
else
  echo "(dry-run, nothing was changed)"
fi
