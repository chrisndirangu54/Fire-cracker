"""Fail-closed safety checks for synthetic indoor pod-deployment scenarios only."""
from dataclasses import dataclass

@dataclass(frozen=True)
class DropContext:
    x: float
    y: float
    altitude_m: float
    geofence: tuple[float,float,float,float]
    scan_age_s: float | None
    nearest_clearance_m: float | None
    thermal_age_s: float | None
    thermal_target_confirmed: bool
    occupancy_clear: bool | None
    human_reviewed: bool
    battery_pct: float
    link_pct: float


def evaluate(ctx: DropContext) -> list[str]:
    """Return reason codes, never a real-world authorization."""
    faults=[]
    x0,y0,x1,y1=ctx.geofence
    if not (x0 <= ctx.x <= x1 and y0 <= ctx.y <= y1):faults.append('OUTSIDE_SIM_GEOFENCE')
    if not (1.0 <= ctx.altitude_m <= 3.0):faults.append('ALTITUDE_OUTSIDE_SIM_BAND')
    if ctx.scan_age_s is None or ctx.scan_age_s > 1.0: faults.append('LIDAR_STALE_OR_MISSING')
    if ctx.nearest_clearance_m is None or ctx.nearest_clearance_m < 1.5: faults.append('OBSTACLE_CLEARANCE_UNVERIFIED')
    if ctx.thermal_age_s is None or ctx.thermal_age_s > 1.0: faults.append('THERMAL_STALE_OR_MISSING')
    if not ctx.thermal_target_confirmed: faults.append('THERMAL_TARGET_UNCONFIRMED')
    if ctx.occupancy_clear is not True: faults.append('HUMAN_OCCUPANCY_NOT_VERIFIED')
    if not ctx.human_reviewed: faults.append('REVIEW_REQUIRED')
    if ctx.battery_pct < 25: faults.append('LOW_BATTERY')
    if ctx.link_pct < 50: faults.append('WEAK_LINK')
    return faults
