# Fire-cracker — Indoor Fire Rescue Drone

Research prototype for firefighter-assisted indoor reconnaissance, LiDAR/thermal observation, non-explosive suppression planning, rescue equipment handoff, and calming public-address messages.

**Status:** simulation-only, not suitable for emergency deployment. No physical flight control, suppressant discharge, payload release, or loudspeaker commands. Certified escape hoods are not general-purpose gas masks. Protective coverings cannot make movement through fire safe.

## Modules
- Fire scene mapping via simulated ROS 2 LiDAR and thermal observations
- Safety checks: occupancy, authorization, altitude, obstacle-clearance and evidence freshness
- Water mist and stationary certified clean-agent advisory
- Virtual protected equipment handoff and PA messaging
- Auditable event records

The complete local Phase 7 runnable archive is available in the originating ChatGPT conversation. This repository has begun receiving the safety-critical simulation modules; full parity with the archive should be checked before deployment or demonstration.

## Usage
All provided modules are Python 3 and standard-library compatible. No safety indication implies real-world clearance.

## MistBurst and gas-only planning (simulation only)

The `firecracker/mistburst.py` module adds three independent liquid formulations: MistBurst-W (water), MistBurst-G (approved gel) and MistBurst-R (approved long-term vegetation retardant), with mechanical pump, certified compressed air/nitrogen or simulation-only chemical gas generation as conceptual propulsion options. **Do not blend gel and retardant without product-specific validation.**

The same module compares gas-only clean agents: CO₂, argon, IG-541, FK-5-1-12 and HFC-227ea. Gas flooding is restricted to specialist engineered enclosures and is not recommended for occupied rescue rooms or outdoor vegetation. Assessment output never authorizes a gas release or nozzle/valve actuation.

Python example:
```python
from firecracker.mistburst import Scene, evaluate
scene = Scene(occupied=True, enclosure_confirmed=False, certified_equipment=False, responder_approval=False)
print(evaluate("MistBurst-W", scene, "mechanical_pump"))
```

Run the standard-library regression tests with `python -m unittest discover -s tests`. The software contains no working fire response actuator, drone flight integration or validated suppression effectiveness data.
