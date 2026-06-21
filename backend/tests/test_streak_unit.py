from datetime import date, timedelta

from app.routers.users import _streaks


def d(n):
    return date.today() - timedelta(days=n)


def test_empty():
    assert _streaks([]) == (0, 0)


def test_today_only():
    assert _streaks([d(0)]) == (1, 1)


def test_yesterday_still_alive():
    assert _streaks([d(1)]) == (1, 1)


def test_missed_day_breaks_current():
    # last play 2 days ago -> current 0, longest 1
    assert _streaks([d(2)]) == (0, 1)


def test_three_day_current():
    assert _streaks([d(2), d(1), d(0)]) == (3, 3)


def test_longest_in_past():
    assert _streaks([d(20), d(19), d(18), d(17), d(0)]) == (1, 4)


def test_duplicate_days_collapse():
    assert _streaks([d(0), d(0), d(1)]) == (2, 2)
