# Match Day

Youth league results and standings. Coaches submit match results through a secret league link; a public page shows standings, recent results, and top scorers.

## Problem

Youth league organizers collect results through chat messages and spreadsheets, so standings are late or wrong. Match Day lets a coach submit a result in seconds. The league page updates immediately and can be shared by link.

## What it does

1. An organizer creates a league with teams. Every team plays every other once, and the app shows a secret submit token once.
2. A coach opens the submit page, enters the token, picks a fixture, and submits the score and optional scorers.
3. The server validates the result and recomputes standings: 3 points for a win, 1 for a draw, 0 for a loss, with tiebreakers of goal difference, then goals for.
4. Anyone with the public link sees standings, recent results, and top scorers.
5. Corrections replace the earlier result and keep the old value in an audit table.

## Expected behavior

- A valid result returns 201 and the public page reflects it.
- Negative or non-integer scores, unknown teams, or scorers exceeding the score return 422 and change nothing.
- A missing token returns 401; a wrong token returns 403.

## Live demo

- Production (Postgres): https://match-day-prod.onrender.com
- Dev (SQLite, resets on restart): https://match-day-dev.onrender.com

Free instances sleep after 15 minutes without traffic, so the first request can take about a minute.

## Run locally

```bash
docker compose up --build
```

Open http://localhost:8080 (app) or http://localhost:8000/docs (API). Data is stored in a Postgres volume; `docker compose down -v` removes it.

Without Docker:

```bash
cd backend
pip install -r requirements.txt
python -m uvicorn app.main:app --port 8000
```

```bash
cd frontend
npm install
npm run dev
```

## Tests

```bash
cd backend
python -m pytest
```

Unit tests cover the standings logic; integration tests cover the API. See [docs/testing.md](docs/testing.md).

## CI/CD

GitHub Actions runs the tests, a frontend build, and Docker builds on every pull request. After CI passes on `main`, the dev service deploys automatically. Production is deployed manually and needs approval. See [docs/deployment.md](docs/deployment.md) and [docs/release-process.md](docs/release-process.md).

## How the project was built

The spec is in [product-spec.md](product-spec.md) and the tasks are tracked as public GitHub issues with acceptance criteria. The agent team and process are in [AGENTS.md](AGENTS.md), [docs/agent-team.md](docs/agent-team.md) and [docs/process.md](docs/process.md).

## Status and limitations

Not implemented: observability (traces, metrics, correlated logs), the user-impact alert, and the on-call responder agent (issues #6 and #7). v1 has no accounts, results can only be corrected and not deleted, and lists are not paginated.