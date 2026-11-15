"""Pure standings computation: 3 points for a win, 1 for a draw, 0 for a loss.

Tiebreakers: goal difference, then goals for, then team name.
"""
from dataclasses import dataclass, field


@dataclass
class Row:
    team_id: int
    team: str
    played: int = 0
    won: int = 0
    drawn: int = 0
    lost: int = 0
    goals_for: int = 0
    goals_against: int = 0
    points: int = field(default=0)

    @property
    def goal_difference(self) -> int:
        return self.goals_for - self.goals_against


def compute_standings(teams, results):
    """teams: iterable of (team_id, name). results: iterable of
    (home_id, away_id, home_score, away_score)."""
    rows = {tid: Row(team_id=tid, team=name) for tid, name in teams}
    for home_id, away_id, hs, as_ in results:
        home, away = rows[home_id], rows[away_id]
        home.played += 1
        away.played += 1
        home.goals_for += hs
        home.goals_against += as_
        away.goals_for += as_
        away.goals_against += hs
        if hs > as_:
            home.won += 1
            away.lost += 1
            home.points += 3
        elif hs < as_:
            away.won += 1
            home.lost += 1
            away.points += 3
        else:
            home.drawn += 1
            away.drawn += 1
            home.points += 1
            away.points += 1
    return sorted(
        rows.values(),
        key=lambda r: (-r.points, -r.goal_difference, -r.goals_for, r.team.lower()),
    )
