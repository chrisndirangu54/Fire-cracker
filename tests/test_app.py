from fastapi.testclient import TestClient
from app import app
client=TestClient(app)
def test_health_disabled():
    assert client.get('/api/health').json()['hardware_outputs_enabled'] is False
def test_simulation():
    assert client.post('/api/sim/reset').status_code==200
    assert client.post('/api/sim/start').json()['mission_status']=='EXPLORING'
    state=client.post('/api/sim/step').json()
    assert state['tick']==1
    assert state['capabilities']['physical_suppression'] is False
def test_discharge_requires_target_and_is_mock():
    client.post('/api/sim/reset')
    assert client.post('/api/sim/discharge').status_code==409
    assert client.post('/api/target',json={'hotspot_id':1}).status_code==200
    state=client.post('/api/sim/discharge').json()
    assert state['suppression_state']=='SIMULATED_DISCHARGE'
    assert state['capabilities']['physical_suppression'] is False
def test_ingestion_rejects_unauthenticated():
    response=client.post('/api/observations',json={'source':'test-rig','x':5,'y':5,'battery':80,'link_quality':90,'temperature_c':40})
    assert response.status_code==403
