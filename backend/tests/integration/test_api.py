from sqlalchemy import select

from tests.integration.conftest import submit


def test_create_league_returns_slug_and_token_once(client, league):
    assert league["slug"].startswith("u12-nairobi-league-")
    assert league["submit_token"]
    r = client.get(f"/api/leagues/{league['slug']}")
    assert r.status_code == 200
    assert "submit_token" not in r.json()
    assert [t["name"] for t in r.json()["teams"]] == ["Lions", "Eagles", "Sharks"]
    assert len(r.json()["fixtures"]) == 3


def test_create_league_rejects_unknown_fixture_team(client):
    r = client.post(
        "/api/leagues",
        json={"name": "X", "teams": ["A", "B"], "fixtures": [{"home": "A", "away": "Z"}]},
    )
    assert r.status_code == 422


def test_unknown_league_404(client):
    assert client.get("/api/leagues/nope").status_code == 404


def test_valid_result_returns_201_and_updates_standings(client, league):
    r = submit(client, league, 0, 2, 1)
    assert r.status_code == 201
    table = client.get(f"/api/leagues/{league['slug']}/standings").json()
    assert table[0]["team"] == "Lions" and table[0]["points"] == 3
    assert table[0]["position"] == 1


def test_negative_score_rejected_and_nothing_changes(client, league):
    r = submit(client, league, 0, -1, 0)
    assert r.status_code == 422
    table = client.get(f"/api/leagues/{league['slug']}/standings").json()
    assert all(row["played"] == 0 for row in table)


def test_non_integer_score_rejected(client, league):
    fid = league["fixtures"][0]["id"]
    r = client.post(
        f"/api/leagues/{league['slug']}/fixtures/{fid}/result",
        json={"home_score": "two", "away_score": 1},
        headers={"X-Submit-Token": league["submit_token"]},
    )
    assert r.status_code == 422


def test_missing_token_401_wrong_token_403(client, league):
    fid = league["fixtures"][0]["id"]
    url = f"/api/leagues/{league['slug']}/fixtures/{fid}/result"
    body = {"home_score": 1, "away_score": 0}
    assert client.post(url, json=body).status_code == 401
    assert client.post(url, json=body, headers={"X-Submit-Token": "bad"}).status_code == 403


def test_fixture_from_other_league_404(client, league):
    other = client.post("/api/leagues", json={"name": "Other", "teams": ["A", "B"], "fixtures": [{"home": "A", "away": "B"}]}).json()
    foreign_fixture = other["fixtures"][0]["id"]
    r = client.post(
        f"/api/leagues/{league['slug']}/fixtures/{foreign_fixture}/result",
        json={"home_score": 1, "away_score": 0},
        headers={"X-Submit-Token": league["submit_token"]},
    )
    assert r.status_code == 404


def test_correction_replaces_result_and_writes_audit(client, league):
    from app import models
    from app.main import app
    from app.database import get_db

    assert submit(client, league, 0, 2, 1).json()["corrected"] is False
    r = submit(client, league, 0, 0, 3)
    assert r.status_code == 201 and r.json()["corrected"] is True

    table = client.get(f"/api/leagues/{league['slug']}/standings").json()
    assert table[0]["team"] == "Eagles" and table[0]["points"] == 3

    db = next(app.dependency_overrides[get_db]())
    audits = db.scalars(select(models.ResultAudit)).all()
    assert len(audits) == 1 and (audits[0].home_score, audits[0].away_score) == (2, 1)


def test_scorers_validated_and_aggregated(client, league):
    ok = submit(client, league, 0, 2, 0, scorers=[{"team": "Lions", "player": "Kuol", "goals": 2}])
    assert ok.status_code == 201
    too_many = submit(client, league, 1, 1, 0, scorers=[{"team": "Eagles", "player": "Deng", "goals": 3}])
    assert too_many.status_code == 422
    wrong_team = submit(client, league, 1, 1, 0, scorers=[{"team": "Lions", "player": "Kuol", "goals": 1}])
    assert wrong_team.status_code == 422
    top = client.get(f"/api/leagues/{league['slug']}/scorers").json()
    assert top == [{"player": "Kuol", "team": "Lions", "goals": 2}]


def test_recent_results_lists_played_fixtures(client, league):
    submit(client, league, 0, 1, 1)
    submit(client, league, 1, 0, 2)
    res = client.get(f"/api/leagues/{league['slug']}/results").json()
    assert len(res) == 2
    assert {(r["home"], r["away"]) for r in res} == {("Lions", "Eagles"), ("Eagles", "Sharks")}
