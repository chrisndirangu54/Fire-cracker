"""Fire-suppression decision-support simulation. No actuator integration.

Recommendations are illustrative, not fire engineering approval or live dispatch.
"""
from dataclasses import dataclass, asdict
from typing import Literal

Environment = Literal['indoor', 'forest']

@dataclass(frozen=True)
class Scenario:
    environment: Environment
    fire_class: str = 'unknown'
    people_present: bool = True
    wind_mps: float = 0.0
    near_waterway: bool = False
    sensor_fresh: bool = False
    operator_approved: bool = False
    area_verified: bool = False


def assess(s: Scenario) -> dict:
    reasons = []
    if not s.sensor_fresh:
        reasons.append('Sensor evidence is stale or missing')
    if not s.operator_approved:
        reasons.append('Firefighter/incident-command approval missing')
    if not s.area_verified:
        reasons.append('Area and personnel clearance not verified')
    if s.people_present:
        reasons.append('Personnel may be in the proposed application area')
    if s.fire_class == 'unknown':
        reasons.append('Fire class is unverified; agent compatibility unknown')

    if s.environment == 'forest':
        options = ['water cooling (simulation)', 'approved wildfire retardant (simulation)',
                   'approved Class A wetting agent (simulation)']
        if s.wind_mps >= 6:
            reasons.append('Wind drift risk: spray application should be reconsidered')
        if s.near_waterway:
            reasons.append('Environmental restriction: prohibit chemical retardant/foam near waterways until reviewed')
        exclusions = ['gas-cloud suppression', 'compressed-gas drops', 'reactive-gas capsules']
    elif s.environment == 'indoor':
        options = ['water-mist cooling (simulation)', 'certified stationary clean-agent concept (simulation)']
        exclusions = ['gas release into occupied spaces', 'dropped pressurized capsules',
                      'unreviewed agent on energized equipment']
        if s.people_present:
            reasons.append('Do not simulate clean-agent recommendation as safe for occupied spaces')
    else:
        raise ValueError('Unsupported environment')
    return {'environment': s.environment, 'candidate_modes': options,
            'excluded_modes': exclusions, 'simulation_ready': not bool(reasons),
            'warnings': reasons, 'actuator_command': None,
            'disclaimer': 'Decision-support exercise only; no live deployment authority.'}
