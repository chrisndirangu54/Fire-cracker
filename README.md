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
