# Fire Rescue Drone — Indoor Firefighter Command Prototype

A runnable **software simulation** for a proposed LiDAR/infrared indoor firefighting drone. The dashboard includes a synthetic occupancy grid, simulated patrolling, thermal hotspots, battery and radio telemetry, manual target review, event log, and a mock suppression visualization.

## Run
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app:app --reload
```
Open **http://127.0.0.1:8000**. To run tests: `pytest -q`.

## Optional sensor-test ingestion
To supply synthetic or recorded test-bench observations, set `DEMO_INGEST_TOKEN` to a strong test credential and POST a JSON sample to `/api/observations` with `X-Demo-Token`. Coordinates are grid coordinates. This is a **test-rig data interface**, not a validated live LiDAR driver or telemetry system.

```bash
curl -X POST http://127.0.0.1:8000/api/observations \
 -H 'Content-Type: application/json' -H 'X-Demo-Token: YOUR_TEST_TOKEN' \
 -d '{"source":"test-rig","x":5,"y":5,"battery":90,"link_quality":95,"temperature_c":40,"hotspots":[{"x":25,"y":7,"temperature_c":220,"confidence":0.92}]}'
```

## Safety boundaries
- No propulsion commands, flight stabilization, route-following hardware integration, valve actuation, or ignition mechanisms.
- The grid and hotspots are simulated; detection confidence is not calibrated. Thermal cameras do **not** necessarily see reliably through dense smoke, flames, or reflective surfaces; LiDAR performance can degrade in particulate smoke.
- Suppression requests never trigger any real-world actuator. Do not connect the demo endpoint to valves or energetic devices.
- An operational product needs an appropriate flight controller, certified payload, redundancy, C2 loss procedures, collision safety, heat/smoke testing, firefighter human-factor validation, and approval by applicable authorities.
- Keep human control over safety-critical actions, with independent hardware interlocks and emergency stop systems validated by qualified engineers.

## Suggested architecture for eventual research
Sensor acquisition and time sync → calibrated thermal / depth fusion → localization and occupancy mapping → candidate heat-anomaly analysis → firefighter UI / approval → independent certified suppression controller. Every subsystem must be bench-tested before any live-fire trials.

## Phase 2: ROS 2 observation bridge

See [docs/ROS2_INTEGRATION.md](docs/ROS2_INTEGRATION.md) for ROS 2 topics, read-only MAVLink telemetry, bench setup, and validation limitations.

New modules:
- `safety.py`: conservative, advisory-only obstacle and sensor-freshness checks.
- `ros2_bridge/bridge_node.py`: subscribes to LiDAR, SLAM map, odometry and scalar thermal temperature; forwards authenticated observations to the existing API.
- `ros2_bridge/mavlink_observer.py`: optional read-only simulator flight-controller telemetry.
- `/api/ros2/observations`: authenticated sensor endpoint; server computes independent HOLD advisory.

There are **no** flight, motor or suppressant actuator commands.

## Phase 3: Non-explosive payload *simulation*

The dashboard now includes a **virtual sealed retardant-pod** workflow: select a hotspot, enter a reviewer name, explicitly confirm that the *synthetic* drop zone contains no people, review the scenario, simulate a drop, or abort. The backend retains an in-memory audit history. A new selection cancels prior authorization. The review expires after 30 seconds. Missing prerequisites fail closed. This does **not** detect people or validate a real drop zone; the checkbox is a training assumption, not a safety sensor.

There is **no** actuator, servo, solenoid, motor controller, MAVLink command publisher, ROS actuator publisher, explosives, or chemical reaction interface. The release endpoint only changes a synthetic state. Do not use it for physical deployment or life-safety decisions. For operational suppression, partner with qualified firefighters and certified suppression-equipment manufacturers.

## Phase 4 — virtual non-explosive retardant pod integration

The web console now includes a separate **advanced virtual pod** panel, with a simulated
geofence, altitude, LiDAR clearance and freshness, thermal target, synthetic occupancy
verification, two-step verify/arm, release simulation, abort, virtual servo/solenoid
latch and bay-sensor feedback, plus a JSON audit endpoint.

The server is **not** connected to physical relays, GPIO, servo/solenoid motors, PX4
actuators or a deployment mechanism. All checks use explicitly synthetic inputs; the
software cannot reliably establish that a real room is clear of people. It is NOT a
safety authorization for an actual drop. Indoor capsule impacts, liquid compatibility,
water exposure to energized equipment and toxic agent exposure require a qualified
fire-protection engineer and approved testing. Consider a certified fixed or tethered
micro-mist/clean-agent system instead of falling pods near firefighters.

API: `POST /api/virtual-payload/verify`, `/arm`, `/release`, `/abort` and
`GET /api/virtual-payload/audit`. Verify, arm and release require the same
`VirtualZoneRequest` scenario and a selected hotspot. Reviews expire after 30 s,
arming after 10 s. Virtual latch always returns to the closed position after a
successful simulated release.

## Phase 5 — virtual certified gas-agent module

The dashboard now supports a **purely virtual** stationary/tethered clean-agent or inert-gas cartridge scenario, including enclosure, ventilation, synthetic occupancy status, hypothetical sensor evidence and firefighter review. POST `/api/virtual-gas/evaluate` and GET `/api/virtual-gas/audit` provide a training-only decision and in-memory record.

The retention index is an **arbitrary instructional indicator**, not agent concentration, extinguishing performance, safety exposure, a pressure calculation or a device-sizing method. No chemical reactions or pressurized munitions are modeled. Dropped gas canisters are explicitly rejected. The simulator has no actuator controls, and even accepted scenarios **never discharge** anything. An operational system must be designed with certified hardware by licensed fire-protection specialists, assessed for occupant exposure and coordinated with incident command.

## Phase 7 — occupant assistance (simulation only)

The console adds a **Rescue supplies · virtual handoff** panel and **Calming PA · script preview** panel. Both use `rescue_assistance.py` with conservative default-deny checks and a JSON audit at `/api/rescue/audit`.

- `POST /api/rescue/supplies/evaluate`: assesses a *simulated* protected handoff of a manufacturer-certified fire escape hood or appropriately rated heat-resistant evacuation covering. Requires firefighter review, independently verified occupant location, protected pickup point, route review, equipment certification, and atmospheric-hazard review.
- `POST /api/rescue/pa/preview`: returns a prewritten supportive announcement for human review only when incident-command approval, language, and audibility are confirmed. No speaker output.
- `GET /api/rescue/audit`: reports simulation audit events.

**Safety boundaries:** A conventional particulate/chemical gas mask does not reliably protect from carbon monoxide, oxygen deficiency, or fire gases. An escape hood must be certified for relevant hazards and used according to the manufacturer and firefighter guidance; no covering is fireproof. Never drop objects onto people. These endpoints do not open a latch, actuate a servo, fly a drone, or transmit audio, and do not constitute a medical or fire rescue system.
