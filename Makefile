BRANCH ?= $(shell git branch --show-current)

up:
	docker compose up --build -d

migrate:
	docker compose exec backend alembic upgrade head

seed:
	docker compose exec backend python -m app.scripts.seed_data

seed-v2:
	docker compose exec backend python -m app.scripts.seed_v2

test:
	docker compose exec backend pytest -q

lint:
	docker compose exec backend ruff check app tests
	docker compose exec backend black --check app tests

codespace-init:
	cd backend && alembic upgrade head
	cd backend && python -m app.scripts.seed_v2

codespace-backend:
	cd backend && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

codespace-frontend:
	cd frontend && npm run dev -- --host 0.0.0.0 --port 5173

git-info:
	@echo "Branch: $(BRANCH)"
	@echo "Remotes:"
	@git remote -v || true

publish-github:
	@test -n "$(REPO_URL)" || (echo "Usage: make publish-github REPO_URL=https://github.com/<org>/<repo>.git [BRANCH=$(BRANCH)]" && exit 1)
	@bash scripts/publish_to_github.sh "$(REPO_URL)" "$(BRANCH)"
