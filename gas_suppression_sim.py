"""Educational virtual clean-agent discharge. No chemistry, pressures or actuators.

The arbitrary 'coverage index' is NOT a concentration, extinguisher design value,
minimum extinguishing concentration, exposure estimate, or suitable system sizing.
"""
from dataclasses import dataclass, field
from datetime import datetime, timezone

AGENTS = {
    'certified_inert_gas': 'Certified inert-gas system (virtual)',
    'certified_clean_agent': 'Certified clean-agent cartridge (virtual)',
}

@dataclass
class VirtualGasModule:
    log: list[dict] = field(default_factory=list)

    def evaluate(self, *, agent: str, room_enclosed: bool, people_present: bool | None,
                 firefighter_approved: bool, ventilation: str, sensor_status: str,
                 release_mode: str):
        faults = []
        if agent not in AGENTS: faults.append('UNKNOWN_CERTIFIED_AGENT')
        if people_present is not False: faults.append('OCCUPANCY_NOT_CONFIRMED_CLEAR')
        if not room_enclosed: faults.append('OPEN_OR_UNCONTAINED_SPACE')
        if not firefighter_approved: faults.append('FIREFIGHTER_REVIEW_REQUIRED')
        if sensor_status != 'valid_simulated': faults.append('SENSOR_EVIDENCE_MISSING')
        if ventilation not in ('low', 'moderate', 'high'): faults.append('UNKNOWN_VENTILATION')
        if release_mode != 'fixed_or_tethered': faults.append('PRESSURIZED_OR_REACTIVE_DROPPED_PAYLOAD_PROHIBITED')
        # Abstract values for comparing leak scenarios; no physical units.
        retention = {'low': 0.85, 'moderate': 0.45, 'high': 0.12}.get(ventilation, 0.0)
        result = {
            'mode': 'SIMULATION_ONLY',
            'hardware_output': False,
            'release_performed': False,
            'agent': agent,
            'delivery': 'virtual stationary/tethered certified module',
            'decision': 'SCENARIO_REJECTED' if faults else 'VIRTUAL_SCENARIO_ACCEPTED',
            'faults': faults,
            'relative_retention_index': round(retention, 2) if not faults else None,
            'retention_units': 'arbitrary; NOT concentration or suppression effectiveness',
            'warnings': [
                'No chemical reaction recipe, pressure vessel, firing sequence, or dropped gas munition is modeled.',
                'Oxygen-deficiency, toxic exposure, heat and oxygen monitoring require professional assessment.',
                'This abstract model cannot predict extinguishment or firefighter safety.'
            ],
        }
        self.log.insert(0, {'time': datetime.now(timezone.utc).isoformat(),
                            'agent': agent, 'decision': result['decision'], 'faults': faults})
        self.log = self.log[:250]
        return result
