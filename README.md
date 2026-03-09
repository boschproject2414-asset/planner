# Atlas v2 - Planning Twin (FastAPI + React)

Atlas v2 is a lightweight digital twin planner for engine-on-trolley projects.
It focuses on planning speed and daily execution learning loops (not heavy gate bureaucracy).

## Modules
- Portfolio
- Project Home
- Activities (grid + task drawer)
- Gantt & Dependencies
- Materials
- Delays & Root Causes
- Baselines & Actions

## Backend v2 capabilities
- PostgreSQL/SQLite persistence via SQLAlchemy + Alembic
- Dependency cycle detection + forecast recalculation
- Delay event detection from schedule variance
- Material risk endpoint (late or stuck)
- Daily/EOD logging
- Baseline snapshot + variance report
- Import preview + activity import (CSV/XLSX)

## Run (GitHub Codespaces)
```bash
npm install
npm run setup
make codespace-init
```
Terminal 1:
```bash
npm run dev:backend
```
Terminal 2:
```bash
npm run dev:frontend
```
Open forwarded ports:
- UI: 5173
- API: 8000

## Quick seed for v2
```bash
curl -X POST http://localhost:8000/api/v2/seed
```
Then open `/portfolio` in frontend.

## Key v2 endpoints
- `GET /api/v2/portfolio`
- `POST /api/v2/projects`
- `GET /api/v2/projects/{id}/home`
- `GET /api/v2/projects/{id}/activities`
- `POST /api/v2/activities`
- `POST /api/v2/projects/{id}/recalculate`
- `GET /api/v2/projects/{id}/dependencies`
- `GET /api/v2/projects/{id}/materials`
- `GET /api/v2/projects/{id}/material-risks`
- `POST /api/v2/projects/{id}/daily-logs`
- `GET /api/v2/projects/{id}/delays`
- `GET /api/v2/projects/{id}/actions`
- `POST /api/v2/projects/{id}/baselines`
- `GET /api/v2/projects/{id}/baseline-variance`
- `POST /api/v2/import/preview`
- `POST /api/v2/projects/{id}/import/activities`

## Tests
```bash
cd backend && pytest -q
```

## Publish branch to GitHub
```bash
make publish-github REPO_URL=https://github.com/<org-or-user>/planner.git BRANCH=$(git branch --show-current)
```


## Codespaces troubleshooting (`ENOENT: /workspaces/planner/package.json`)
If `npm install` at repo root fails with `ENOENT` for `package.json`, your branch likely does not include the root workspace file yet. Use branch-agnostic commands:

```bash
python3 -m pip install -r backend/requirements.txt
npm --prefix frontend install
make codespace-init
make codespace-backend   # terminal 1
make codespace-frontend  # terminal 2
```

If you intended to use root scripts (`npm run setup`, `npm run dev:backend`), switch/pull to a branch that contains root `package.json`.
