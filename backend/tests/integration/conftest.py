import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db, make_engine
from app.main import app


@pytest.fixture()
def client():
    engine = make_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)

    def override():
        db = Session()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture()
def league(client):
    r = client.post(
        "/api/leagues",
        json={
            "name": "U12 Nairobi League",
            "teams": ["Lions", "Eagles", "Sharks"],
            "fixtures": [
                {"home": "Lions", "away": "Eagles"},
                {"home": "Eagles", "away": "Sharks"},
                {"home": "Sharks", "away": "Lions"},
            ],
        },
    )
    assert r.status_code == 201
    return r.json()


def submit(client, league, fixture_index, home, away, token=None, scorers=None):
    headers = {"X-Submit-Token": token or league["submit_token"]}
    fid = league["fixtures"][fixture_index]["id"]
    return client.post(
        f"/api/leagues/{league['slug']}/fixtures/{fid}/result",
        json={"home_score": home, "away_score": away, "scorers": scorers or []},
        headers=headers,
    )
