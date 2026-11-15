from pydantic import BaseModel, Field, model_validator


class FixtureIn(BaseModel):
    home: str = Field(min_length=1, max_length=80)
    away: str = Field(min_length=1, max_length=80)


class LeagueCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    teams: list[str] = Field(min_length=2)
    fixtures: list[FixtureIn] = []

    @model_validator(mode="after")
    def check_teams_and_fixtures(self):
        names = [t.strip() for t in self.teams]
        if any(not n for n in names):
            raise ValueError("team names must not be blank")
        if len({n.lower() for n in names}) != len(names):
            raise ValueError("team names must be unique")
        known = {n.lower() for n in names}
        for f in self.fixtures:
            if f.home.strip().lower() not in known or f.away.strip().lower() not in known:
                raise ValueError("fixture teams must belong to the league")
            if f.home.strip().lower() == f.away.strip().lower():
                raise ValueError("a team cannot play itself")
        return self


class ScorerIn(BaseModel):
    team: str
    player: str = Field(min_length=1, max_length=80)
    goals: int = Field(ge=1)


class ResultIn(BaseModel):
    home_score: int = Field(ge=0)
    away_score: int = Field(ge=0)
    scorers: list[ScorerIn] = []
