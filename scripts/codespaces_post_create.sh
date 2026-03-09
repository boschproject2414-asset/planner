#!/usr/bin/env bash
set -euo pipefail

# Root npm workspace is optional (older branches may not include package.json)
if [[ -f package.json ]]; then
  npm install
else
  echo "No root package.json found; skipping root npm install"
fi

python3 -m pip install --upgrade pip
python3 -m pip install -r backend/requirements.txt
npm --prefix frontend install

echo "Codespace bootstrap complete."
echo "Run: make codespace-init"
echo "Then in two terminals: make codespace-backend and make codespace-frontend"
