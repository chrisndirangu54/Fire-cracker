from rescue_assistance import RescueScene, plan_rescue, preview_pa
from suppression_planner import IndoorScene, assess_indoor

def test_default_fail_closed():
    assert not plan_rescue(RescueScene())["simulation_ready"]
    assert not assess_indoor(IndoorScene())["ready_for_tabletop_simulation"]

def test_no_actuation_even_when_all_checks_true():
    s = RescueScene(True, True, True, True, True, True)
    assert plan_rescue(s)["hardware_enabled"] is False
    i = IndoorScene(True, True, True, True, True, True)
    assert assess_indoor(i)["hardware_enabled"] is False

def test_pa_is_preview_only():
    p = preview_pa("reassure", incident_command_approved=True)
    assert p["preview_only"] and not p["broadcast_enabled"]
