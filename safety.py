"""Advisory-only safety assessment. Never authorizes autonomous flight or suppressant release."""
from __future__ import annotations
import math
import time
from dataclasses import dataclass

@dataclass(frozen=True)
class SafetyLimits:
    min_clearance_m: float = 0.75
    min_battery_percent: float = 25.0
    min_link_percent: float = 40.0
    stale_seconds: float = 2.0


def clearance_from_laserscan(ranges, range_min, range_max):
    """Return closest valid obstacle range; None if no usable scan returns."""
    if not (math.isfinite(range_min) and math.isfinite(range_max) and 0 <= range_min < range_max):
        return None
    valid = [float(x) for x in ranges if isinstance(x,(int,float)) and math.isfinite(x) and range_min <= x <= range_max]
    return min(valid) if valid else None


def assess(*, clearance_m=None, battery=None, link=None, sensor_age_s=None, localization_ok=False, limits=SafetyLimits()):
    faults=[]
    if clearance_m is None or not math.isfinite(clearance_m):faults.append('LIDAR_UNAVAILABLE')
    elif clearance_m < limits.min_clearance_m:faults.append('OBSTACLE_PROXIMITY')
    if battery is None or not math.isfinite(battery):faults.append('BATTERY_UNAVAILABLE')
    elif battery < limits.min_battery_percent:faults.append('LOW_BATTERY')
    if link is None or not math.isfinite(link):faults.append('LINK_UNAVAILABLE')
    elif link < limits.min_link_percent:faults.append('WEAK_LINK')
    if sensor_age_s is None or not math.isfinite(sensor_age_s) or sensor_age_s > limits.stale_seconds:faults.append('STALE_SENSOR_DATA')
    if not localization_ok:faults.append('LOCALIZATION_UNVERIFIED')
    return {'advisory':'HOLD' if faults else 'MONITOR_ONLY', 'faults':faults, 'hardware_commands_allowed':False}
