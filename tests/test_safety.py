import os
from fastapi.testclient import TestClient
from app import app
from safety import assess,clearance_from_laserscan

client=TestClient(app)

def test_clearance_filters_invalid():
    assert clearance_from_laserscan([float('nan'),float('inf'),0.1,1.2,2.3],0.2,10)==1.2
    assert clearance_from_laserscan([float('inf')],0.2,10) is None

def test_fails_closed_without_sensors():
    d=assess()
    assert d['advisory']=='HOLD' and not d['hardware_commands_allowed']
    assert 'LIDAR_UNAVAILABLE' in d['faults']

def test_obstacle_blocks_advisory():
    d=assess(clearance_m=0.2,battery=90,link=90,sensor_age_s=0.01,localization_ok=True)
    assert 'OBSTACLE_PROXIMITY' in d['faults']

def test_ros2_endpoint_reauth_and_server_enforced_safety(monkeypatch):
    monkeypatch.setenv('DEMO_INGEST_TOKEN','test-secret')
    payload={'source':'ros2-readonly','clearance_m':2,'scan_age_s':0.1,'localization_ok':True,'map_received':True,'safety':{'hardware_commands_allowed':True}}
    assert client.post('/api/ros2/observations',json=payload).status_code==403
    result=client.post('/api/ros2/observations',json=payload,headers={'X-Demo-Token':'test-secret'})
    assert result.status_code==200
    assert result.json()['ros2']['safety']['hardware_commands_allowed'] is False
    assert result.json()['ros2']['safety']['advisory']=='HOLD'
