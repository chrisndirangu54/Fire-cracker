from certified_extinguisher_adapter import ExtinguisherObservation, review_extinguisher
import pytest

def test_fail_closed_by_default():
    r = review_extinguisher(ExtinguisherObservation(agent="water_mist"))
    assert not r["tabletop_ready"]
    assert r["hardware_release_enabled"] is False
    assert r["actuator_command"] is None

def test_approved_tabletop_still_no_hardware_commands():
    r = review_extinguisher(ExtinguisherObservation(
        agent="water_mist", pressure_ok=True, mounting_verified=True,
        mass_balance_verified=True, thermal_limits_verified=True,
        manufacturer_remote_actuation_approved=True,
        qualified_engineer_reviewed=True, firefighter_approved=True,
        people_clear=True, fresh_sensor_evidence=True,
        communication_healthy=True,
    ))
    assert r["tabletop_ready"]
    assert r["hardware_release_enabled"] is False
    assert r["actuator_command"] is None

def test_unknown_agent_rejected():
    with pytest.raises(ValueError):
        review_extinguisher(ExtinguisherObservation(agent="unknown"))
