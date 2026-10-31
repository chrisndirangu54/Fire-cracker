from suppression_planner import Scenario, assess

def test_defaults_fail_closed():
    r = assess(Scenario('indoor'))
    assert not r['simulation_ready'] and r['actuator_command'] is None

def test_forest_waterway_guard():
    r = assess(Scenario('forest', fire_class='vegetation', people_present=False,
                        near_waterway=True, sensor_fresh=True, operator_approved=True,
                        area_verified=True))
    assert not r['simulation_ready']
    assert any('waterway' in x for x in r['warnings'])

def test_windy_forest_guard():
    r = assess(Scenario('forest', fire_class='vegetation', people_present=False,
                        wind_mps=9, sensor_fresh=True, operator_approved=True,
                        area_verified=True))
    assert not r['simulation_ready']

def test_no_physical_control():
    r = assess(Scenario('indoor', fire_class='ordinary', people_present=False,
                        sensor_fresh=True, operator_approved=True, area_verified=True))
    assert r['simulation_ready'] and r['actuator_command'] is None
