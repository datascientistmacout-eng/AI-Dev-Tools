# Testing

## Backend

Unit tests (`backend/tests/unit`) cover the standings logic: points, draws, and tiebreakers.
Integration tests (`backend/tests/integration`) call the API against an in-memory database: league creation, result validation, token checks, corrections with audit rows, scorers, and results listing.

Run both with one command:

```bash
cd backend
python -m pytest
```

## CI

`.github/workflows/ci.yml` runs on every pull request and on pushes to `main`:

- `backend-tests`: installs dependencies and runs `python -m pytest`
- `frontend-build`: runs `npm run build`
- `docker-build`: runs `docker compose build`

A pull request should only be merged when all three checks pass.