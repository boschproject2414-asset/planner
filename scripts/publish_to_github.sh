#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 <github_repo_url> [branch_name]"
  echo "Example: $0 https://github.com/acme/planner.git work"
  exit 1
fi

REPO_URL="$1"
BRANCH="${2:-$(git branch --show-current)}"

if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "Not inside a git repository"
  exit 1
fi

if [[ -z "$(git status --porcelain)" ]]; then
  echo "Working tree clean"
else
  echo "Working tree has uncommitted changes. Commit or stash before publishing."
  exit 1
fi

if git remote get-url origin >/dev/null 2>&1; then
  git remote set-url origin "$REPO_URL"
  echo "Updated existing origin remote"
else
  git remote add origin "$REPO_URL"
  echo "Added origin remote"
fi

echo "Fetching remote refs..."
git fetch origin || true

echo "Pushing branch '$BRANCH' to origin..."
git push -u origin "$BRANCH"

echo
if git ls-remote --exit-code --heads origin main >/dev/null 2>&1; then
  echo "Next steps to merge into main:"
  echo "  git checkout main"
  echo "  git pull origin main"
  echo "  git merge $BRANCH"
  echo "  git push origin main"
  echo "Or open a Pull Request: $BRANCH -> main"
else
  echo "Remote has no main branch yet. You can create it with:"
  echo "  git push -u origin $BRANCH:main"
fi
