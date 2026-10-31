# ROS 2 integration — safety-scoped prototype

This repository supports **observation only**. It does not fly an aircraft or open a suppression valve. The ROS 2 node subscribes to standard `sensor_msgs/msg/LaserScan`, `nav_msgs/msg/OccupancyGrid`, `nav_msgs/msg/Odometry` and `std_msgs/msg/Float32` topics. It forwards scan proximity, whether a map and odometry have been received, raw odometry position (not a verified world-frame pose), and maximum thermal temperature. **A scalar thermal maximum is not a radiometric image or hotspot geolocation.** No fusion between these coordinate frames is claimed.

## Dependencies

Use an existing ROS 2 installation, such as Jazzy, with `rclpy`, `sensor_msgs`, `nav_msgs`, `std_msgs`, and a compatible LiDAR driver. For mapping, `slam_toolbox` can subscribe to `/scan`; proper laser-to-base transforms and odometry are required. Standard 2D SLAM and occupancy grids alone are not safe flight localization: aerial vehicles also require verified 3D positioning, altitude sensing, dynamic-obstacle perception and flight-controller-level failsafes.

## Running (in a dedicated test laboratory)

Terminal A (Python API environment):

```bash
export DEMO_INGEST_TOKEN='replace-with-long-random-test-token'
uvicorn app:app --host 127.0.0.1 --port 8000
```

Terminal B (ROS 2 environment):

```bash
source /opt/ros/jazzy/setup.bash
export DEMO_INGEST_TOKEN='replace-with-long-random-test-token'
export PYTHONPATH="$PWD:$PYTHONPATH"
python3 ros2_bridge/bridge_node.py
```

Optionally use `ros2 launch slam_toolbox online_async_launch.py` with appropriate configured transforms and mapping parameters. This starts SLAM **outside** the dashboard; the API only reports whether map messages have been observed. If the ROS environment's Python version differs from the web service environment, run them separately as processes.

Optional read-only MAVLink observation, using **SITL** as the source:

```bash
pip install pymavlink
python ros2_bridge/mavlink_observer.py --connection udpin:127.0.0.1:14550
```

This listener never sends flight commands and does not automatically bind its data to the dashboard. Never expose the demonstration token or observation API on a public network. No authentication is provided for dashboard viewing: keep it bound to localhost.

## Safety validation still needed

A qualified UAS/fire-safety team must validate thermal sensor calibration and smoke effects, LiDAR degradation in heavy particulate, 3D SLAM integrity, coordinate-frame calibration, collision avoidance in dynamic spaces, communication-loss behavior, thermal limits of electronics and battery packs, people detection, certified extinguishing agent compatibility, and firefighter approval workflow. Avoid substituting the `MONITOR_ONLY` status for certification or permission to fly.
