import irsdk

import time
from datetime import datetime, timezone

from vars import telemetry_vars

from influxdb_client_3 import InfluxDBClient3, Point, WritePrecision
from influxdb_client_3 import WriteOptions, write_client_options, InfluxDBError


INFLUXDB_HOST = "http://localhost:8181"
INFLUXDB_DATABASE = "iracing-telemetry"
INFLUXDB_TOKEN = "apiv3_fMQ4YUfXm2twQxfztaMvGrrrHtivTq8hm6ORkUpyhJmkSaewPpd450p417nmA9sYKaZn4cuaDzV3NXjazCWjRA" # just for testing

class BatchingCallback:
    """
    A simple callback class to monitor batch write operations.
    These methods are called by the client when a batch is successfully written,
    fails, or is retried.
    """
    def __init__(self):
        self.write_count = 0
        self.error_count = 0
        self.retry_count = 0

    def success(self, conf: dict, data: str):
        """Called when a batch is successfully written."""
        self.write_count += 1
        print(f"Successfully wrote batch {self.write_count}: data: {data[:50]}...") # Print first 50 chars of data
        # print(f"Successfully wrote batch {self.write_count}")

    def error(self, conf: dict, data: str, exception: InfluxDBError):
        """Called when a batch fails to write."""
        self.error_count += 1
        print(f"ERROR writing batch: config: {conf}, data: {data[:50]}... due to: {exception}")

    def retry(self, conf: dict, data: str, exception: InfluxDBError):
        """Called when a batch write is retried."""
        self.retry_count += 1
        print(f"RETRYING batch: config: {conf}, data: {data[:50]}... due to: {exception}")


callback_handler = BatchingCallback()

# Define WriteOptions for batching behavior
write_options = WriteOptions(
    batch_size=100,
    flush_interval=1000,  # Flush data to InfluxDB every 1 second
    jitter_interval=100,
    retry_interval=5000,
    max_retries=5,
    max_retry_delay=5000,
    exponential_base=2
)

# Create write client options with callbacks and batching options
wco = write_client_options(
    success_callback=callback_handler.success,
    error_callback=callback_handler.error,
    retry_callback=callback_handler.retry,
    write_options=write_options
)

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


def get_telemetry_data():
    # get session data, which track, cars etc
    ir.freeze_var_buffer_latest()

    for key, value in telemetry_vars.telemetry_data.items():
        value = ir[key]
        telemetry_vars.telemetry_data.update({key: value})

    return telemetry_vars.telemetry_data


def generate_telemetry_point(driver_name, telemetry_item) -> Point:
    print(telemetry_item["SessionTimeRemain"])

    return Point("telemetry_data") \
        .tag("driver", driver_name) \
        .tag("track", "monza") \
        .tag("sessionID", 1) \
        .tag("lap", int(telemetry_item["Lap"])) \
        .field("FuelLevel", telemetry_item["FuelLevel"]) \
        .field("FuelLevelPct", float(telemetry_item["FuelLevelPct"])) \
        .field("LapCompleted", int(telemetry_item["LapCompleted"])) \
        .field("SessionTimeRemain", float(telemetry_item["SessionTimeRemain"])) \
        .field("IsOnTrack", bool(telemetry_item["IsOnTrack"])) \
        .field("RRtempCM", float(telemetry_item["RRtempCM"])) \
        .field("RFtempCM", float(telemetry_item["RFtempCM"])) \
        .field("LFtempCM", float(telemetry_item["LFtempCM"])) \
        .field("LRtempCM", float(telemetry_item["LRtempCM"])) \
        .field("LapLastLapTime", int(telemetry_item["LapLastLapTime"])) \
        .field("IsInGarage", bool(telemetry_item["IsInGarage"])) \
        .field("OnPitRoad", bool(telemetry_item["OnPitRoad"])) \
        .time(datetime.now(timezone.utc), write_precision=WritePrecision.NS)


if __name__ == '__main__':
    # initializing ir and state
    ir = irsdk.IRSDK()
    state = State()

    # Initialize the InfluxDB 3 Client using the 'with' statement
    with InfluxDBClient3(
        host=INFLUXDB_HOST,
        token=INFLUXDB_TOKEN if INFLUXDB_TOKEN else None,
        database=INFLUXDB_DATABASE,
        write_client_options=wco
    ) as client:
        print(f"Connected to InfluxDB 3 at {INFLUXDB_HOST}, database: {INFLUXDB_DATABASE}")
        print(f"Batching configured: batch_size={write_options.batch_size}, flush_interval={write_options.flush_interval}ms")
        print("Press Ctrl+C to stop the script.")

        try:
            # infinite loop
            while True:
                # check if we are connected to iracing
                check_iracing()
                # if we are, then process data
                if state.ir_connected:
                    telemetry_data = get_telemetry_data()
                    point = generate_telemetry_point("Martijn", telemetry_data)
                    try:
                        client.write(point, write_options=write_options)
                    except InfluxDBError as e:
                        print(e)
                time.sleep(1)
        except KeyboardInterrupt:
            client.close()
            client.disconnect()
            # press ctrl+c to exit
