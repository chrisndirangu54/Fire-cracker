"""Indoor suppression decision-support simulation. No physical release endpoints."""
from dataclasses import dataclass

@dataclass(frozen=True)
class IndoorScene:
    incident_command_approved: bool = False
    fire_verified: bool = False
    sensor_data_fresh: bool = False
    occupants_clear: bool = False
    ventilation_reviewed: bool = False
    agent_certification_reviewed: bool = False

def assess_indoor(scene: IndoorScene) -> dict:
    gates = {
        "command_approval": scene.incident_command_approved,
        "fire_verified": scene.fire_verified,
        "fresh_sensors": scene.sensor_data_fresh,
        "occupants_clear": scene.occupants_clear,
        "ventilation_review": scene.ventilation_reviewed,
        "agent_certification_review": scene.agent_certification_reviewed,
    }
    return {
        "candidates": [
            {"agent": "water_mist", "delivery": "professionally validated fixed or tethered system"},
            {"agent": "certified_clean_agent", "delivery": "approved stationary system only"},
        ],
        "excluded": ["explosive devices", "chemically generated gas munitions", "dropped pressurized cartridges"],
        "ready_for_tabletop_simulation": all(gates.values()),
        "gates": gates,
        "hardware_enabled": False,
        "warning": "This is not a validated fire-suppression model or fireground clearance.",
    }
