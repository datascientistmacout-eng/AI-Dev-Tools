# Match Day: Youth League Results and Standings

## Problem

Youth league organizers collect match results through chat messages and spreadsheets, so standings are late, wrong, or both. Match Day lets a coach or volunteer submit a result in seconds. The league's standings and results page then updates immediately and can be shared by link.

## Users

- **Organizer**: creates a league, teams, and fixtures, and receives two links: a secret submit link and a public link.
- **Coach/volunteer**: uses the submit link to enter results.
- **Parent/player**: uses the public link to see standings, recent results, and top scorers.

## Functionality (v1)

1. Create a league with teams and fixtures. The league gets a secret submit token and a public slug.
2. Submit a result for a fixture: a score for each team, plus optional scorers. Requests require the submit token.
3. Validation rules:
   - Scores are non-negative integers.
   - Both teams belong to the league.
   - A fixture has only one active result. A correction replaces it, and the old value is kept in an audit log.
4. Standings are computed on the server: 3 points for a win, 1 for a draw, 0 for a loss. Tiebreakers: goal difference, then goals for.
5. A public page shows standings, recent results, and top scorers.
6. Every submission and correction is stored with a timestamp for traceability.

## Out of scope (v1)

User accounts, pagination, notifications, multiple sports.

## Expected behavior

- A valid result returns 201, and the public page reflects it on refresh.
- An invalid result returns 422 with a clear message and changes nothing.
- A missing or wrong token returns 401 or 403.

## Stack

React + Vite frontend, FastAPI + SQLAlchemy backend, SQLite by default via `DATABASE_URL`.

## Observability and alerting

- Key journey: submit result, validate, recompute standings, publish.
- One trace ID ties together metrics, traces, and structured logs for that request.
- No tokens or personal data are sent to telemetry.
- User-impact alert: fires when the share of failed or slow result submissions exceeds a threshold over a rolling window.
- On-call responder agent: wakes on the alert, inspects logs and traces, and opens a fix PR or applies a rollback.

## Tasks and acceptance criteria

Tracked as public GitHub issues. Each issue links back to this spec.

### 1. Leagues, teams, fixtures API
- POST creates a league with teams and fixtures.
- The response includes the public slug and the submit token once.
- GET by slug returns teams and fixtures.
- Data persists across restarts.

### 2. Submit result with validation
- A valid result returns 201.
- Negative or non-integer scores return 422.
- A team outside the league returns 422.
- A missing or wrong token returns 401 or 403.
- A second submission for the same fixture replaces the first and writes an audit row.

### 3. Server-side standings
- 3/1/0 points, tiebreak by goal difference then goals for.
- The endpoint returns standings sorted correctly.
- Unit tests cover a draw, a tie, and a correction that changes the table.

### 4. Public league page
- Loads from the public slug without a token.
- Shows standings, the last 10 results, and top scorers.
- Shows a friendly empty state for a new league.

### 5. Observability of the submit journey
- OpenTelemetry traces cover submit, validate, and recompute.
- Structured logs and metrics carry the same trace ID.
- No token or personal data appears in telemetry.
- Signals are viewable in Grafana, Loki, and Tempo.

### 6. User-impact alert and responder agent
- An alert fires when submit failures or slow submits exceed a threshold over a rolling window.
- The alert triggers the responder service, which inspects logs and traces and opens a fix PR or applies a rollback.
- The run is recorded on the tracker.

### 7. Tests, Docker Compose, CI/CD
- Unit and integration tests run with one command and pass.
- The whole system, including the database, starts with `docker compose up`.
- CI runs tests on every PR.
- CD deploys to dev automatically and requires manual approval for production.

### 8. Docs
- `AGENTS.md` points to modular docs for process and the agent team.
- The README matches this spec.
