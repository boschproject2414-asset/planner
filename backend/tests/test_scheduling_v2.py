from datetime import date

import pytest

from app.services.scheduling_v2 import CycleError, recalc_forecast


def test_recalc_forecast_chain():
    activities = {
        1: {"planned_start": date(2026, 1, 1), "duration_days": 1},
        2: {"planned_start": date(2026, 1, 1), "duration_days": 2},
    }
    result = recalc_forecast(activities, [(1, 2)], date(2026, 1, 1))
    assert result[1][0] == date(2026, 1, 1)
    assert result[2][0] >= result[1][1]


def test_recalc_cycle_error():
    activities = {1: {"planned_start": date(2026, 1, 1), "duration_days": 1}, 2: {"planned_start": date(2026, 1, 1), "duration_days": 1}}
    with pytest.raises(CycleError):
        recalc_forecast(activities, [(1, 2), (2, 1)], date(2026, 1, 1))
