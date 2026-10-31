import pytest
from drop_zone_validator import SimulatedZone, validate_zone
from payload_controller import VirtualPayloadController

def test_fail_closed_missing_occupancy():
    faults=validate_zone(SimulatedZone(occupancy_clear=None),80,90,True)
    assert 'HUMAN_OCCUPANCY_NOT_VERIFIED' in faults

def test_reject_stale_lidar_and_geofence():
    faults=validate_zone(SimulatedZone(x=40,scan_age_s=2),80,90,True)
    assert 'OUTSIDE_SIM_GEOFENCE' in faults
    assert 'LIDAR_STALE_OR_MISSING' in faults

def test_two_step_virtual_latch():
    p=VirtualPayloadController();p.select(1)
    assert p.verify('Operator',[])=='VERIFIED'
    with pytest.raises(ValueError):p.release([])
    assert p.phase=='LOCKED'
    p.verify('Operator',[])
    assert p.arm([])=='ARMED_SIM'
    assert p.release([])=='SIMULATED_RELEASE'
    assert p.bay_sensor_closed

def test_faults_relock_and_audit():
    p=VirtualPayloadController();p.select(1);p.verify('Operator',[])
    with pytest.raises(ValueError):p.arm(['WEAK_LINK'])
    assert p.phase=='LOCKED'
    assert any(e['action']=='ABORT' for e in p.audit)
