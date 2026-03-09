import pytest

from app.services.scheduling import ActivityNode, ScheduleError, compute_schedule


def test_critical_path_and_float():
    nodes = {
        1: ActivityNode(1, 4, "Mechanical"),
        2: ActivityNode(2, 4, "Mechanical"),
        3: ActivityNode(3, 2, "Mechanical"),
    }
    result = compute_schedule(nodes, [(1, 2), (1, 3)], {"G1", "G2"})
    assert result["project_finish"] == 8
    assert 2 in result["critical_path"]
    assert result["TF"][3] == 2


def test_cycle_detection():
    nodes = {1: ActivityNode(1, 1, "Mechanical"), 2: ActivityNode(2, 1, "Mechanical")}
    with pytest.raises(ScheduleError):
        compute_schedule(nodes, [(1, 2), (2, 1)], {"G2"})


def test_gate_constraint_blocks_electrical():
    nodes = {
        1: ActivityNode(1, 2, "Mechanical"),
        2: ActivityNode(2, 2, "Electrical"),
    }
    result = compute_schedule(nodes, [(1, 2)], {"G1"})
    assert result["ES"][2] > 1000
