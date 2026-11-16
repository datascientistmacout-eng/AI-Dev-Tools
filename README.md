# Match Day

Youth league results and standings. Coaches submit match results through a secret league link; a public page shows standings, recent results, and top scorers. See [product-spec.md](product-spec.md) for the full problem, functionality, and acceptance criteria, and [AGENTS.md](AGENTS.md) for how the agent team works.

## Run the backend locally

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

## Run the tests

```bash
cd backend
python -m pytest
```

Unit tests are in `backend/tests/unit`, integration tests in `backend/tests/integration`.

## Run everything with Docker

```bash
docker compose up --build
```

Open http://localhost:8080 for the app. The API docs are at http://localhost:8000/docs. Data is kept in a Postgres volume; `docker compose down -v` removes it.
