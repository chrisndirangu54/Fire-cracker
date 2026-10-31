"""Optional MAVLink telemetry observer, strictly read-only.

No command_long, set_mode, arm, takeoff, position targets, or actuator messages.
Install `pymavlink` separately in a hardware lab, and use only on a test bench.
"""
import argparse
import json
import time


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--connection',default='udpin:127.0.0.1:14550',help='SITL telemetry input (default localhost UDP)')
    args=p.parse_args()
    from pymavlink import mavutil
    link=mavutil.mavlink_connection(args.connection)
    while True:
        msg=link.recv_match(type=['HEARTBEAT','SYS_STATUS','LOCAL_POSITION_NED'],blocking=True,timeout=2)
        if msg:
            print(json.dumps({'received_at':time.time(),'kind':msg.get_type(),'data':msg.to_dict()},default=str),flush=True)
        else:print(json.dumps({'warning':'telemetry timeout; do not infer vehicle safety'}),flush=True)

if __name__=='__main__':main()
