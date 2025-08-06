import irsdk

import influxdb
import time
from datetime import datetime, timezone
from vars import telemetry_data

from influxdb_client_3 import InfluxDBClient3, Point, WritePrecision
from influxdb_client_3 import WriteOptions, write_client_options, InfluxDBError


class State:
    ir_connected = False
    last_car_setup_tick = -1

def check_iracing():
    if state.ir_connected and not (ir.is_initialized and ir.is_connected):
        state.ir_connected = False
        # don't forget to reset your State variables
        state.last_car_setup_tick = -1
        # we are shutting down ir library (clearing all internal variables)
        ir.shutdown()
        print('irsdk disconnected')
    elif not state.ir_connected and ir.startup() and ir.is_initialized and ir.is_connected:
        state.ir_connected = True
        print('irsdk connected')

def get_telemetry():
    # get session data, which track, cars etc
    ir.freeze_var_buffer_latest()

    for key, value in telemetry_data.items():
        value = ir[key]
        telemetry_data.update({key: value})


    return telemetry_data


def generate_telemetry_point(driver_name, telemetry_data) -> Point:
    print(telemetry_data["SessionTimeRemain"])

    return Point("telemetry_data") \
        .tag("driver", driver_name) \
        .tag("track", "monza") \
        .tag("sessionID", 1) \
        .tag("lap", int(telemetry_data["Lap"])) \
        .field("FuelLevel", telemetry_data["FuelLevel"]) \
        .field("FuelLevelPct", float(telemetry_data["FuelLevelPct"])) \
        .field("LapCompleted", int(telemetry_data["LapCompleted"])) \
        .field("SessionTimeRemain", float(telemetry_data["SessionTimeRemain"])) \
        .field("IsOnTrack", bool(telemetry_data["IsOnTrack"])) \
        .field("RRtempCM", float(telemetry_data["RRtempCM"])) \
        .field("RFtempCM", float(telemetry_data["RFtempCM"])) \
        .field("LFtempCM", float(telemetry_data["LFtempCM"])) \
        .field("LRtempCM", float(telemetry_data["LRtempCM"])) \
        .field("LapLastLapTime", int(telemetry_data["LapLastLapTime"]))\
        .time(datetime.now(timezone.utc), write_precision=WritePrecision.NS)

if __name__ == '__main__':
    # initializing ir and state
    ir = irsdk.IRSDK()
    state = State()

    try:
        # infinite loop
        while True:
            # check if we are connected to iracing
            check_iracing()
            # if we are, then process data
            if state.ir_connected:
                telemetry = get_telemetry()
                # collector.update(tel, session_info=Nil)

            for item in telemetry_data:
                influxdb.send_to_influxdb("Martijn", item)

            time.sleep(1)
    except KeyboardInterrupt:
        # press ctrl+c to exit
        pass
