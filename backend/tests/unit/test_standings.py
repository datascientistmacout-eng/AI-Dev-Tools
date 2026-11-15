from app.standings import compute_standings

TEAMS = [(1, "Lions"), (2, "Eagles"), (3, "Sharks")]


def test_win_draw_loss_points():
    rows = compute_standings(TEAMS, [(1, 2, 2, 0), (2, 3, 1, 1)])
    by = {r.team: r for r in rows}
    assert by["Lions"].points == 3
    assert by["Eagles"].points == 1
    assert by["Sharks"].points == 1
    assert by["Lions"].won == 1 and by["Eagles"].lost == 1


def test_draw_gives_one_point_each():
    rows = compute_standings(TEAMS, [(1, 2, 1, 1)])
    by = {r.team: r for r in rows}
    assert by["Lions"].points == by["Eagles"].points == 1
    assert by["Lions"].drawn == by["Eagles"].drawn == 1


def test_tiebreak_goal_difference_then_goals_for():
    # Lions and Eagles both finish on 3 points.
    results = [(1, 3, 3, 2), (2, 3, 1, 0)]
    rows = compute_standings(TEAMS, results)
    assert [r.team for r in rows][:2] == ["Lions", "Eagles"]  # +1 GD each, Lions scored more
    assert rows[0].goal_difference == rows[1].goal_difference == 1


def test_no_results_alphabetical_zero_points():
    rows = compute_standings(TEAMS, [])
    assert [r.team for r in rows] == ["Eagles", "Lions", "Sharks"]
    assert all(r.points == 0 and r.played == 0 for r in rows)
