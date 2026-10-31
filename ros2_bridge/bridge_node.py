"""ROS 2 read-only observation bridge.

Subscribe to /scan, /map, /odom and /fire/thermal_max_c (Float32).
Forward limited observations to the FastAPI dashboard. No publishers to motors,
flight controllers or suppressant actuators.

Run from a ROS 2 environment (rclpy, nav_msgs, sensor_msgs, std_msgs installed).
"""
import json
import math
import os
import time
import urllib.request
from rclpy.node import Node
import rclpy
from sensor_msgs.msg import LaserScan
from nav_msgs.msg import OccupancyGrid, Odometry
from std_msgs.msg import Float32

from safety import assess, clearance_from_laserscan

class FireRescueObserver(Node):
    def __init__(self):
        super().__init__('fire_rescue_readonly_observer')
        self.api=os.getenv('FIRE_RESCUE_API','http://127.0.0.1:8000').rstrip('/')
        self.token=os.getenv('DEMO_INGEST_TOKEN','')
        self.clearance=None; self.last_scan=None; self.odom=None; self.map=None; self.temp=None
        self.create_subscription(LaserScan,'/scan',self.on_scan,10)
        self.create_subscription(OccupancyGrid,'/map',self.on_map,10)
        self.create_subscription(Odometry,'/odom',self.on_odom,10)
        self.create_subscription(Float32,'/fire/thermal_max_c',self.on_temp,10)
        self.create_timer(0.5,self.push)
        self.get_logger().info('Read-only bridge started; flight and suppressant commands are disabled')

    def on_scan(self, msg):
        self.clearance=clearance_from_laserscan(msg.ranges,msg.range_min,msg.range_max)
        self.last_scan=time.monotonic()

    def on_map(self, msg):
        # Occupancy grid source is handled by actual SLAM provider (e.g. slam_toolbox).
        self.map=msg

    def on_odom(self, msg):
        self.odom=msg

    def on_temp(self, msg):
        self.temp=float(msg.data) if math.isfinite(msg.data) else None

    def push(self):
        age=None if self.last_scan is None else time.monotonic()-self.last_scan
        advisory=assess(clearance_m=self.clearance,battery=None,link=None,sensor_age_s=age,localization_ok=False)
        payload={'source':'ros2-readonly','clearance_m':self.clearance,
                 'scan_age_s':age,'localization_ok':False,'safety':advisory,
                 'thermal_max_c':self.temp,
                 'map_received':self.map is not None, 'odom_received':self.odom is not None}
        if self.odom:
            p=self.odom.pose.pose.position
            payload['odom_m']={'x':p.x,'y':p.y,'z':p.z}
        if not self.token:
            self.get_logger().warn('Set DEMO_INGEST_TOKEN to enable observation forwarding')
            return
        request=urllib.request.Request(self.api+'/api/ros2/observations',data=json.dumps(payload).encode(),
                      headers={'Content-Type':'application/json','X-Demo-Token':self.token},method='POST')
        try:
            with urllib.request.urlopen(request,timeout=0.6) as response:response.read()
        except Exception as exc:self.get_logger().warn(f'Dashboard forwarding unavailable: {exc}')


def main():
    rclpy.init(); node=FireRescueObserver()
    try:rclpy.spin(node)
    finally:node.destroy_node();rclpy.shutdown()

if __name__=='__main__':main()
