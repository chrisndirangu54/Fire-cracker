"""Simulation-only firefighter rescue-assistance planner. Never actuates hardware."""
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from uuid import uuid4

APPROVED_PA = {
    "reassure": "Emergency services are responding. Stay calm and listen for instructions.",
    "stay_put": "If your exit is blocked by smoke or heat, stay in a safer enclosed room, close the door and tell emergency services your location.",
    "responder_help": "Firefighters are on their way. Follow their instructions and do not enter smoke-filled areas.",
}

@dataclass(frozen=True)
class RescueScene:
    operator_approved: bool = False
    verified_occupant: bool = False
    personnel_clear: bool = False
    fresh_sensors: bool = False
    safe_handoff_route: bool = False
    rated_equipment: bool = False

def plan_rescue(scene: RescueScene, equipment: str = "escape_hood") -> dict:
    if equipment not in {"escape_hood", "evacuation_covering"}:
        raise ValueError("Unsupported rescue equipment")
    checks = {
        "operator_approval": scene.operator_approved,
        "occupant_verified": scene.verified_occupant,
        "people_clear_of_handoff_area": scene.personnel_clear,
        "sensor_data_fresh": scene.fresh_sensors,
        "handoff_route_checked": scene.safe_handoff_route,
        "equipment_certification_checked": scene.rated_equipment,
    }
    return {
        "event_id": str(uuid4()),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "equipment": equipment,
        "simulation_ready": all(checks.values()),
        "checks": checks,
        "hardware_enabled": False,
        "instructions": "Human-supervised protected handoff only; no aerial drop",
        "warning": "Escape hoods are product-specific and do not universally protect against carbon monoxide or oxygen deficiency; coverings are not fireproof.",
    }

def preview_pa(message_key: str, incident_command_approved: bool = False) -> dict:
    if message_key not in APPROVED_PA:
        raise ValueError("Unknown or unapproved PA message")
    return {
        "message": APPROVED_PA[message_key],
        "preview_only": True,
        "approved_for_simulation": bool(incident_command_approved),
        "broadcast_enabled": False,
    }
