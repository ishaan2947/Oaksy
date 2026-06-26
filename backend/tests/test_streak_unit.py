from datetime import date, timedelta

from app.routers.users import _streaks

# Fixed reference so the tests don't depend on the wall clock / timezone.
TODAY = date(2026, 6, 25)


def d(n):
    return TODAY - timedelta(days=n)


def s(days):
    return _streaks(days, today=TODAY)


def test_empty():
    assert s([]) == (0, 0)


def test_today_only():
    assert s([d(0)]) == (1, 1)


def test_yesterday_still_alive():
    assert s([d(1)]) == (1, 1)


def test_missed_day_breaks_current():
    # last play 2 days ago -> current 0, longest 1
    assert s([d(2)]) == (0, 1)


def test_three_day_current():
    assert s([d(2), d(1), d(0)]) == (3, 3)


def test_longest_in_past():
    assert s([d(20), d(19), d(18), d(17), d(0)]) == (1, 4)


def test_duplicate_days_collapse():
    assert s([d(0), d(0), d(1)]) == (2, 2)
