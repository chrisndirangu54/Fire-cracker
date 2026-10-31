"""Certified extinguisher adapter: advisory simulation only, NO actuator interfaces.

Commercial extinguishers must remain unmodified. Real remote actuation requires
written manufacturer approval, engineering review and independent certification.
"""
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from uuid import uuid4

AGENTS = frozenset({"water_mist", "abc_dry_chemical", "clean_agent", "co2"})

@dataclass(frozen=True)
class ExtinguisherObservation:
    agent: str
    pressure_ok: bool = False
    mounting_verified: bool = False
    mass_balance_verified: bool = False
    thermal_limits_verified: bool = False
    manufacturer_remote_actuation_approved: bool = False
    qualified_engineer_reviewed: bool = False
    firefighter_approved: bool = False
    people_clear: bool = False
    fresh_sensor_evidence: bool = False
    communication_healthy: bool = False

def review_extinguisher(observation: ExtinguisherObservation) -> dict:
    if observation.agent not in AGENTS:
        raise ValueError("Unknown extinguisher agent")
    gates = {
        "pressure_ok": observation.pressure_ok,
        "mounting_verified": observation.mounting_verified,
        "mass_balance_verified": observation.mass_balance_verified,
        "thermal_limits_verified": observation.thermal_limits_verified,
        "manufacturer_remote_actuation_approved": observation.manufacturer_remote_actuation_approved,
        "qualified_engineer_reviewed": observation.qualified_engineer_reviewed,
        "firefighter_approved": observation.firefighter_approved,
        "people_clear": observation.people_clear,
        "fresh_sensor_evidence": observation.fresh_sensor_evidence,
        "communication_healthy": observation.communication_healthy,
    }
    return {
        "event_id": str(uuid4()),
        "observed_at": datetime.now(timezone.utc).isoformat(),
        "agent": observation.agent,
        "tabletop_ready": all(gates.values()),
        "gates": gates,
        "failed_gates": [name for name, passed in gates.items() if not passed],
        "hardware_release_enabled": False,
        "actuator_command": None,
        "simulated_discharge_status": "not_dispatched",
        "warnings": [
            "No remotely controlled physical discharge, valve, solenoid or servo output",
            "Occupancy checks are not proof an area is unoccupied",
            "CO2 and clean agents require qualified exposure and enclosure assessment",
            "Manufacturer approval and fire-service acceptance required before field trials",
        ],
    }
