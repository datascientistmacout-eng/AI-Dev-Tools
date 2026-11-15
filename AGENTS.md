# AGENTS.md

Guidance for any AI agent working in this repository. Read this file first, then follow the links to the doc you need.

## Project

**Match Day** lets youth league organizers and coaches submit match results and publishes live standings, recent results, and top scorers on a shareable page. Full description: [product-spec.md](product-spec.md).

## Stack

- Frontend: React + Vite (`frontend/`)
- Backend: FastAPI + SQLAlchemy (`backend/`), SQLite by default via `DATABASE_URL`
- Tests: `pytest` (backend, run with `uv run python -m pytest`), `npm test` (frontend)
- Run everything locally: `docker compose up`
- Telemetry: OpenTelemetry, Collector, Prometheus, Loki, Tempo, Grafana
- CI/CD: GitHub Actions (`.github/workflows/`)

## Where to find things

| Need | Read |
|---|---|
| What we are building and acceptance criteria | [product-spec.md](product-spec.md) |
| Who does what | [docs/agent-team.md](docs/agent-team.md) |
| How work flows from issue to production | [docs/process.md](docs/process.md) |
| Testing approach and commands | [docs/testing.md](docs/testing.md) |
| Deployment and environments | [docs/deployment.md](docs/deployment.md) |
| Release and rollback | [docs/release-process.md](docs/release-process.md) |
| Observability, alerts, responder agent | [docs/observability.md](docs/observability.md) |
| API contract | [openapi.yaml](openapi.yaml) |

## Rules for all agents

1. Work from a GitHub issue. Reference its number in your branch name, commits, and PR (`#12`).
2. The acceptance criteria on the issue are the definition of done. Do not expand scope.
3. Never commit secrets, submit tokens, or personal data. Never send them to logs or telemetry.
4. Every change ships with tests. Run the full test command before opening a PR.
5. Keep the API and `openapi.yaml` in sync.
6. Do not push to `main`. Open a PR; CI must pass.
7. Production deploys are manual and require human approval. Agents never approve their own deploys.
8. If requirements are unclear, comment on the issue instead of guessing.
