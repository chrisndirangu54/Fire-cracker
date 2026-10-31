from fastapi.testclient import TestClient
from app import app

client=TestClient(app)

def test_supply_denied_by_default():
    r=client.post('/api/rescue/supplies/evaluate',json={'supply':'certified_escape_hood'})
    assert r.status_code==200
    assert r.json()['decision']=='HOLD'
    assert r.json()['physical_delivery_enabled'] is False

def test_supply_sim_only_when_reviewed():
    r=client.post('/api/rescue/supplies/evaluate',json=dict(supply='heat_resistant_covering',firefighter_reviewed=True,protected_pickup_point=True,occupant_location_verified=True,route_verified=True,hardware_certified=True,air_monitoring_verified=True))
    assert r.json()['decision']=='SIMULATED_HANDOFF_REVIEWED'
    assert r.json()['hardware_outputs_enabled'] is False

def test_pa_denied_by_default():
    r=client.post('/api/rescue/pa/preview',json={'message':'stay_calm'})
    assert r.json()['decision']=='HOLD'
    assert r.json()['speaker_output_enabled'] is False

def test_pa_script_preview():
    r=client.post('/api/rescue/pa/preview',json=dict(message='do_not_enter_smoke',approved_by_incident_command=True,language_confirmed=True,audibility_reviewed=True))
    assert r.json()['decision']=='SIMULATED_PA_PREVIEW'
    assert 'Do not enter smoke' in r.json()['script']

def test_audit():
    r=client.get('/api/rescue/audit')
    assert r.status_code==200 and r.json()['hardware_outputs_enabled'] is False
