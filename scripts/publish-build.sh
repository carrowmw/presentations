#!/usr/bin/env bash
set -euo pipefail

NAME="${1:-}"
SRC="${2:-builds/${NAME}_build}"

if [[ -z "$NAME" ]]; then
  echo "Usage: $0 <name> [<build-path>]" >&2
  exit 1
fi
if [[ ! -d "$SRC" ]]; then
  echo "Build folder not found: $SRC" >&2
  exit 1
fi

ROOT="$(git rev-parse --show-toplevel)"
PAGES_DIR="$(cd "$ROOT/.."; pwd)/presentations-pages"

# Ensure gh-pages worktree exists (handle already-existing case)
if ! git -C "$ROOT" worktree list --porcelain | grep -q "^worktree $PAGES_DIR$"; then
  git -C "$ROOT" fetch origin || true
  if git -C "$ROOT" ls-remote --exit-code --heads origin gh-pages >/dev/null 2>&1; then
    git -C "$ROOT" worktree add -B gh-pages "$PAGES_DIR" origin/gh-pages
  else
    git -C "$ROOT" worktree add -B gh-pages "$PAGES_DIR"
  fi
fi

# Publish (exclude nested git metadata)
rsync -av --delete --exclude '.git*' "$SRC"/ "$PAGES_DIR/$NAME"/

# Rebuild a simple index
{
  echo '<!doctype html><meta charset="utf-8"><title>Presentations</title>'
  echo '<h1>Presentations</h1><ul>'
  for d in "$PAGES_DIR"/*/ ; do
    base="$(basename "$d")"
    [[ "$base" == ".git" ]] && continue
    echo "  <li><a href=\"./$base/\">$base</a></li>"
  done
  echo '</ul>'
} > "$PAGES_DIR/index.html"

git -C "$PAGES_DIR" add -A
git -C "$PAGES_DIR" commit -m "Publish $NAME" || echo "No changes to commit for $NAME"
git -C "$PAGES_DIR" push origin gh-pages