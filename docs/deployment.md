# Deployment

The app is one container (FastAPI serving the built React frontend), built from the root Dockerfile and hosted on Render.

| Environment | URL | Database |
|---|---|---|
| dev | https://match-day-dev.onrender.com | SQLite (resets on restart) |
| production | https://match-day-prod.onrender.com | Render Postgres |

Free instances sleep after 15 minutes without traffic, so the first request can take about a minute.

## How deploys happen

- Auto-deploy is turned off on both Render services. GitHub Actions triggers every deploy through a deploy hook.
- Dev: when CI succeeds on main, the Deploy workflow's deploy-dev job calls the dev hook automatically.
- Production: run the Deploy workflow manually (Actions, Deploy, Run workflow). The deploy-production job waits for approval from a required reviewer before it calls the production hook.
- The hook URLs are stored as the secret RENDER_DEPLOY_HOOK in the dev and production GitHub environments. They are never committed to the repository.

## Local run

docker compose up --build serves the app at http://localhost:8080 with Postgres.
