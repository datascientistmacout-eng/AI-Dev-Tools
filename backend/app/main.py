import hashlib
import hmac
import re
import secrets
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, Header, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from . import models
from .database import Base, engine, get_db
from .schemas import LeagueCreate, ResultIn
from .standings import compute_standings


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="Match Day", lifespan=lifespan)


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def make_slug(name: str) -> str:
    base = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-") or "league"
    return f"{base}-{secrets.token_hex(3)}"


def get_league(db: Session, slug: str) -> models.League:
    league = db.scalar(select(models.League).where(models.League.slug == slug))
    if league is None:
        raise HTTPException(404, "League not found")
    return league


def require_token(league: models.League, token: str | None):
    if not token:
        raise HTTPException(401, "Missing submit token")
    if not hmac.compare_digest(hash_token(token), league.token_hash):
        raise HTTPException(403, "Invalid submit token")


def league_out(league: models.League) -> dict:
    return {
        "name": league.name,
        "slug": league.slug,
        "teams": [{"id": t.id, "name": t.name} for t in league.teams],
        "fixtures": [
            {"id": f.id, "home": f.home_team.name, "away": f.away_team.name, "played": f.result is not None}
            for f in league.fixtures
        ],
    }


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.post("/api/leagues", status_code=201)
def create_league(body: LeagueCreate, db: Session = Depends(get_db)):
    token = secrets.token_urlsafe(24)
    league = models.League(name=body.name.strip(), slug=make_slug(body.name), token_hash=hash_token(token))
    by_name = {}
    for name in body.teams:
        team = models.Team(name=name.strip())
        league.teams.append(team)
        by_name[name.strip().lower()] = team
    for f in body.fixtures:
        league.fixtures.append(
            models.Fixture(home_team=by_name[f.home.strip().lower()], away_team=by_name[f.away.strip().lower()])
        )
    db.add(league)
    db.commit()
    out = league_out(league)
    out["submit_token"] = token  # shown only once
    return out


@app.get("/api/leagues/{slug}")
def read_league(slug: str, db: Session = Depends(get_db)):
    return league_out(get_league(db, slug))


@app.post("/api/leagues/{slug}/fixtures/{fixture_id}/result", status_code=201)
def submit_result(
    slug: str,
    fixture_id: int,
    body: ResultIn,
    x_submit_token: str | None = Header(default=None),
    db: Session = Depends(get_db),
):
    league = get_league(db, slug)
    require_token(league, x_submit_token)
    fixture = db.get(models.Fixture, fixture_id)
    if fixture is None or fixture.league_id != league.id:
        raise HTTPException(404, "Fixture not found in this league")

    teams = {fixture.home_team.name.lower(): fixture.home_team, fixture.away_team.name.lower(): fixture.away_team}
    goals = {fixture.home_team_id: 0, fixture.away_team_id: 0}
    for s in body.scorers:
        team = teams.get(s.team.strip().lower())
        if team is None:
            raise HTTPException(422, f"Scorer team '{s.team}' is not playing in this fixture")
        goals[team.id] += s.goals
    if goals[fixture.home_team_id] > body.home_score or goals[fixture.away_team_id] > body.away_score:
        raise HTTPException(422, "Scorer goals exceed the team's score")

    old = fixture.result
    if old is not None:
        db.add(
            models.ResultAudit(
                fixture_id=fixture.id,
                home_score=old.home_score,
                away_score=old.away_score,
                submitted_at=old.submitted_at,
            )
        )
        fixture.result = None
        db.flush()

    result = models.Result(home_score=body.home_score, away_score=body.away_score)
    for s in body.scorers:
        result.scorers.append(
            models.Scorer(team_id=teams[s.team.strip().lower()].id, player=s.player.strip(), goals=s.goals)
        )
    fixture.result = result
    db.commit()
    return {
        "fixture_id": fixture.id,
        "home_score": result.home_score,
        "away_score": result.away_score,
        "corrected": old is not None,
    }


@app.get("/api/leagues/{slug}/standings")
def standings(slug: str, db: Session = Depends(get_db)):
    league = get_league(db, slug)
    rows = compute_standings(
        [(t.id, t.name) for t in league.teams],
        [
            (f.home_team_id, f.away_team_id, f.result.home_score, f.result.away_score)
            for f in league.fixtures
            if f.result is not None
        ],
    )
    return [
        {
            "position": i,
            "team": r.team,
            "played": r.played,
            "won": r.won,
            "drawn": r.drawn,
            "lost": r.lost,
            "goals_for": r.goals_for,
            "goals_against": r.goals_against,
            "goal_difference": r.goal_difference,
            "points": r.points,
        }
        for i, r in enumerate(rows, start=1)
    ]


@app.get("/api/leagues/{slug}/results")
def recent_results(slug: str, limit: int = 10, db: Session = Depends(get_db)):
    league = get_league(db, slug)
    played = sorted((f for f in league.fixtures if f.result), key=lambda f: f.result.submitted_at, reverse=True)
    return [
        {
            "fixture_id": f.id,
            "home": f.home_team.name,
            "away": f.away_team.name,
            "home_score": f.result.home_score,
            "away_score": f.result.away_score,
        }
        for f in played[: max(1, min(limit, 50))]
    ]


@app.get("/api/leagues/{slug}/scorers")
def top_scorers(slug: str, db: Session = Depends(get_db)):
    league = get_league(db, slug)
    totals: dict[tuple[str, str], int] = {}
    names = {t.id: t.name for t in league.teams}
    for f in league.fixtures:
        if f.result:
            for s in f.result.scorers:
                key = (s.player, names[s.team_id])
                totals[key] = totals.get(key, 0) + s.goals
    ranked = sorted(totals.items(), key=lambda kv: (-kv[1], kv[0][0].lower()))
    return [{"player": p, "team": t, "goals": g} for (p, t), g in ranked[:10]]
