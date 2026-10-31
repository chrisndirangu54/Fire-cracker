"""Simulation-only non-explosive retardant pod mission review.

No GPIO, servo, solenoid, MAVLink command, ROS command publication, or
physical payload release interfaces exist in this module.
"""
from dataclasses import dataclass, field
import time

@dataclass
class PodReview:
    status: str = 'SAFE_LOCKED'
    target_id: int | None = None
    reviewer: str | None = None
    human_clearance_confirmed: bool = False
    verified_epoch: float | None = None
    audit: list[dict] = field(default_factory=list)

    def record(self, action: str, detail: str):
        self.audit.insert(0, {'epoch_s': round(time.time(), 3), 'action': action, 'detail': detail})
        self.audit = self.audit[:100]

    def select(self, target_id: int):
        self.target_id = target_id
        self.reviewer = None
        self.human_clearance_confirmed = False
        self.verified_epoch = None
        self.status = 'AWAITING_ZONE_REVIEW'
        self.record('SELECT', f'Hotspot {target_id} selected for virtual pod review')

    def review(self, reviewer: str, human_clearance_confirmed: bool, *, zone_known: bool, sensor_fresh: bool):
        self.reviewer = reviewer
        self.human_clearance_confirmed = bool(human_clearance_confirmed)
        self.verified_epoch = time.time() if all((human_clearance_confirmed,zone_known,sensor_fresh)) else None
        self.status = 'SIM_READY' if self.verified_epoch is not None else 'SAFE_LOCKED'
        self.record('REVIEW', f'Zone known={zone_known}; telemetry fresh={sensor_fresh}; human-clear={human_clearance_confirmed}')
        return self.status

    def simulate(self, *, zone_known: bool, sensor_fresh: bool, human_clear: bool):
        if self.status != 'SIM_READY' or self.verified_epoch is None:
            raise ValueError('Explicit safety review required')
        if time.time() - self.verified_epoch > 30:
            self.abort('Safety review expired')
            raise ValueError('Safety review expired')
        if not all((zone_known,sensor_fresh,human_clear)):
            self.abort('Safety prerequisites changed')
            raise ValueError('Safety prerequisites changed')
        self.status = 'SIMULATED_POD_DROP'
        self.record('SIMULATE', f'Virtual non-explosive pod deployed to hotspot {self.target_id}; NO HARDWARE OUTPUT')
        return self.status

    def abort(self, reason='Operator aborted'):
        self.status = 'SAFE_LOCKED'
        self.verified_epoch = None
        self.human_clearance_confirmed = False
        self.record('ABORT', reason)
