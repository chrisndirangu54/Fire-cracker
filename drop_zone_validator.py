"""Synthetic LiDAR/thermal zone evidence; never validates real human absence."""
from dataclasses import dataclass
from drop_safety import DropContext, evaluate

@dataclass(frozen=True)
class SimulatedZone:
    x:float=5.0
    y:float=5.0
    altitude_m:float=2.0
    scan_age_s:float=0.2
    clearance_m:float=2.0
    thermal_age_s:float=0.2
    thermal_target_confirmed:bool=True
    occupancy_clear:bool|None=True

def validate_zone(zone:SimulatedZone, battery:float, link:float, reviewed:bool):
    return evaluate(DropContext(zone.x,zone.y,zone.altitude_m,(1,1,34,22),zone.scan_age_s,zone.clearance_m,zone.thermal_age_s,zone.thermal_target_confirmed,zone.occupancy_clear,reviewed,battery,link))
