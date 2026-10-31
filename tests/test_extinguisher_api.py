from fastapi.testclient import TestClient
from app import app
client=TestClient(app)

def test_catalog_contains_four_agents():
    r=client.get("/api/extinguisher/catalog")
    assert r.status_code==200
    assert set(r.json()["agents"])=={"water_mist","abc_dry_chemical","clean_agent","co2"}
    assert r.json()["hardware_release_enabled"] is False

def test_review_defaults_to_fail_closed():
    r=client.post("/api/extinguisher/evaluate",json={"agent":"water_mist"})
    assert r.status_code==200
    v=r.json()
    assert not v["tabletop_ready"]
    assert v["hardware_release_enabled"] is False
    assert v["simulated_discharge_status"]=="reviewed_only"
    assert v["live_observation"]["telemetry_advisory"]

def test_monitor_records_review_without_actuation():
    r=client.get("/api/extinguisher/status")
    assert r.status_code==200
    assert r.json()["hardware_release_enabled"] is False

def test_invalid_agent_is_rejected():
    assert client.post("/api/extinguisher/evaluate",json={"agent":"pyrotechnic"}).status_code==422
