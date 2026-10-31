import pytest
from payload import PodReview

def test_stays_locked_without_human_clearance():
    p=PodReview();p.select(2)
    assert p.review('Test firefighter',False,zone_known=True,sensor_fresh=True)=='SAFE_LOCKED'
    with pytest.raises(ValueError):p.simulate(zone_known=True,sensor_fresh=True,human_clear=False)

def test_virtual_drop_only_after_review():
    p=PodReview();p.select(2)
    assert p.review('Test firefighter',True,zone_known=True,sensor_fresh=True)=='SIM_READY'
    assert p.simulate(zone_known=True,sensor_fresh=True,human_clear=True)=='SIMULATED_POD_DROP'
    assert 'NO HARDWARE OUTPUT' in p.audit[0]['detail']

def test_abort_and_retarget_cancel_approval():
    p=PodReview();p.select(1);p.review('Tester',True,zone_known=True,sensor_fresh=True)
    p.select(2)
    with pytest.raises(ValueError):p.simulate(zone_known=True,sensor_fresh=True,human_clear=True)
    p.abort();assert p.status=='SAFE_LOCKED'

def test_missing_or_stale_sensors_fail_closed():
    p=PodReview();p.select(1)
    assert p.review('Tester',True,zone_known=True,sensor_fresh=False)=='SAFE_LOCKED'
