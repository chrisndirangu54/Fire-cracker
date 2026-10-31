"""Virtual servo/solenoid latch state machine. Absolutely no hardware dependencies."""
from dataclasses import dataclass, field
import time

@dataclass
class VirtualPayloadController:
    phase:str='LOCKED'
    target_id:int|None=None
    reviewer:str|None=None
    review_time:float|None=None
    arm_time:float|None=None
    bay_sensor_closed:bool=True
    audit:list[dict]=field(default_factory=list)

    def _log(self, action, result, faults=()):
        self.audit.insert(0, {'at':time.time(),'action':action,'result':result,'faults':list(faults),'target_id':self.target_id,'virtual_latch_closed':self.bay_sensor_closed})
        self.audit=self.audit[:250]

    def select(self,target_id):
        self.abort('Target change')
        self.target_id=target_id
        self._log('TARGET_SELECTED','REVIEW_REQUIRED')

    def verify(self,reviewer,faults):
        self.reviewer=reviewer
        if faults:
            self.phase='LOCKED';self._log('VERIFY','DENIED',faults)
        else:
            self.phase='VERIFIED';self.review_time=time.monotonic();self._log('VERIFY','ACCEPTED_SIM_ONLY')
        return self.phase

    def arm(self,faults):
        if self.phase!='VERIFIED' or self.review_time is None or time.monotonic()-self.review_time>30 or faults:
            self.abort('Arm denied: invalid/expired review or scenario faults')
            raise ValueError('Review invalid, expired, or safety faults present')
        self.phase='ARMED_SIM';self.arm_time=time.monotonic();self._log('ARM','ARMED_SIM_ONLY')
        return self.phase

    def release(self,faults):
        if self.phase!='ARMED_SIM' or self.arm_time is None or time.monotonic()-self.arm_time>10 or faults:
            self.abort('Release denied: invalid/expired arm or scenario faults')
            raise ValueError('Arming invalid, expired, or safety faults present')
        self.phase='SIMULATED_RELEASE'
        self.bay_sensor_closed=False
        self._log('VIRTUAL_SERVO_OPEN','SIMULATED_RELEASE_ONLY')
        self.bay_sensor_closed=True
        self._log('VIRTUAL_BAY_SENSOR','CLOSED_AFTER_SIMULATION')
        return self.phase

    def abort(self,reason='Operator abort'):
        self.phase='LOCKED';self.review_time=None;self.arm_time=None;self.bay_sensor_closed=True
        self._log('ABORT',reason)
