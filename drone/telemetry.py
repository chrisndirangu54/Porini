"""Read-only MAVLink telemetry bridge. NEVER arms, takes off or sends flight commands."""
import os,json
from pymavlink import mavutil
def stream_telemetry():
    endpoint=os.environ.get("PORINI_MAVLINK_ENDPOINT","udpin:0.0.0.0:14550")
    connection=mavutil.mavlink_connection(endpoint)
    while True:
        msg=connection.recv_match(type=["GLOBAL_POSITION_INT","SYS_STATUS","HEARTBEAT"],blocking=True,timeout=5)
        if msg is None:continue
        data=msg.to_dict()
        yield {"type":msg.get_type(),"data":data,"source":"vehicle-telemetry-read-only"}
if __name__=="__main__":
    for item in stream_telemetry():print(json.dumps(item))
