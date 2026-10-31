"""Fire-Cracker MistBurst and gas-only fire-suppression planning.

Research software only: NEVER actuates flight, nozzles, cylinders, cartridges or valves.
All statuses are advisory and never constitute emergency clearance.
Standard-library compatible.
"""
from dataclasses import dataclass, asdict
from typing import Optional

FORMULATIONS = {
    "MistBurst-W": {"agent": "water", "purpose": "localized cooling", "scene": "fire_hotspot"},
    "MistBurst-G": {"agent": "approved water-enhancer gel", "purpose": "temporary adhesion", "scene": "vegetation_protection"},
    "MistBurst-R": {"agent": "approved long-term retardant", "purpose": "fireline protection", "scene": "outdoor_fireline"},
}
ATOMIZERS = {
    "mechanical_pump": {"status": "engineering_review"},
    "compressed_air": {"status": "engineering_review", "vessel_required": True},
    "compressed_nitrogen": {"status": "engineering_review", "vessel_required": True},
    "chemical_gas_generator": {"status": "simulation_only", "formulations": []},
}
GAS_ONLY = {
    "co2": {"name": "Carbon dioxide", "safe_in_occupied_scene": False, "warnings": "Severe asphyxiation hazard; re-ignition possible"},
    "ig01": {"name": "Argon", "safe_in_occupied_scene": False, "warnings": "Oxygen displacement hazard"},
    "ig541": {"name": "IG-541", "safe_in_occupied_scene": False, "warnings": "Engineered exposure restrictions"},
    "fk5112": {"name": "FK-5-1-12", "safe_in_occupied_scene": False, "warnings": "Decomposition products and exposure assessment required"},
    "hfc227ea": {"name": "HFC-227ea", "safe_in_occupied_scene": False, "warnings": "Decomposition/exposure and environmental restrictions"},
}

@dataclass(frozen=True)
class Scene:
    occupied: bool
    enclosure_confirmed: bool
    certified_equipment: bool
    responder_approval: bool
    environmental_clearance: bool = False

def evaluate(agent_id: str, scene: Scene, atomizer: Optional[str] = None) -> dict:
    if agent_id not in FORMULATIONS and agent_id not in GAS_ONLY:
        raise ValueError("Unknown suppression agent")
    issues = []
    if not scene.responder_approval: issues.append("Human fire-authority review required")
    if not scene.certified_equipment: issues.append("Certified equipment and formulation validation required")
    if not scene.environmental_clearance: issues.append("Environmental/occupant exposure assessment incomplete")
    if agent_id in GAS_ONLY:
        if scene.occupied: issues.append("Gas-only flooding not eligible for occupied rescue scene")
        if not scene.enclosure_confirmed: issues.append("Gas-only flooding requires an engineered enclosure")
        if atomizer: issues.append("Gas-only agents do not use MistBurst liquid atomization")
    else:
        if atomizer not in ATOMIZERS: issues.append("Valid atomizer must be selected")
        elif atomizer == "chemical_gas_generator": issues.append("Chemical gas generation is simulation-only")
        if atomizer in ("compressed_air", "compressed_nitrogen"):
            issues.append("Vessel/regulator validation must be performed independently")
        if agent_id == "MistBurst-R" and scene.occupied:
            issues.append("Long-term wildfire retardant not approved here for occupied indoor rooms")
    return {"agent": agent_id, "atomizer":atomizer, "scene":asdict(scene),
            "advisory_issues":issues,"needs_specialist_review":bool(issues),
            "simulation_only":True,"physical_actuation_enabled":False,
            "suppression_authorized":False,
            "warning":"Planning aid only. Never use output to trigger hardware or enter a burning space."}
