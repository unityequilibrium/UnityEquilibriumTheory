from docs.scripts.audit.audit_topic13_thermometry_window import eligible_delays


def test_strict_source_boundary_does_not_shift_time():
    delays = [-1., 42.3, 100., 100.1]
    assert eligible_delays(delays, 100.) == [3]
    assert delays == [-1., 42.3, 100., 100.1]


def test_empty_eligible_window_is_not_filled():
    assert eligible_delays([-2., 0., 9.], 100.) == []
