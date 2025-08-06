# On each team member's PC
# Note: For InfluxDB 3.0, you'll typically use the 'influxdb_client_3' library.
# You might need to install it: pip install influxdb_client_3
import time

import influxdb_client_3
from influxdb_client_3 import InfluxDBClient3, Point, write_client_options, WriteOptions, \
    InfluxDBError  # Note the '3' in the import

import datetime

# Configuration for your InfluxDB 3.0 instance
# InfluxDB 3.0 uses 'database' instead of 'bucket'
INFLUXDB_HOST = "http://localhost:8181"  # Or https://us-east-1-1.aws.cloud2.influxdata.com if using cloud
INFLUXDB_TOKEN = "apiv3_fMQ4YUfXm2twQxfztaMvGrrrHtivTq8hm6ORkUpyhJmkSaewPpd450p417nmA9sYKaZn4cuaDzV3NXjazCWjRA"
INFLUXDB_ORG = "my_organization"
INFLUXDB_DATABASE = "iracing-telemetry"  # Changed from BUCKET to DATABASE

# --- Batching Configuration ---
# These parameters control how the client buffers and sends data.
BATCH_SIZE = 10000  # Number of points to accumulate before sending a batch
FLUSH_INTERVAL_MS = 1000  # Maximum time (in milliseconds) to wait before flushing,
# even if BATCH_SIZE is not reached (e.g., 1 second)
JITTER_INTERVAL_MS = 100  # Random delay (in milliseconds) added to flush_interval
# to prevent all clients from flushing at the exact same time.
RETRY_INTERVAL_MS = 5000  # How long to wait before retrying a failed batch
MAX_RETRIES = 5  # Maximum number of retries for a failed batch
MAX_RETRY_DELAY_MS = 30000  # Maximum delay between retries (exponential backoff)
EXPONENTIAL_BASE = 2  # Base for exponential backoff retry strategy

# Initialize the InfluxDB 3.0 client
# The client directly handles writing, no separate write_api needed


# client = InfluxDBClient3(host=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG, database=INFLUX_DATABASE,
#                          write_client_options=wco)



class TelemetrySender:
    def __init__(self, influxdb_client: InfluxDBClient3):
        self.influxdb_client = influxdb_client

    def send_data(self, telemetry):
        send_to_influxdb()



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

# write_options = WriteOptions(
#     batch_size=BATCH_SIZE,
#     flush_interval=FLUSH_INTERVAL_MS,
#     jitter_interval=JITTER_INTERVAL_MS,
#     retry_interval=RETRY_INTERVAL_MS,
#     max_retries=MAX_RETRIES,
#     max_retry_delay=MAX_RETRY_DELAY_MS,
#     exponential_base=EXPONENTIAL_BASE
# )

write_options = WriteOptions()


wco = write_client_options(
    write_options=write_options,
    success_callback=callback_handler.success,
    error_callback=callback_handler.error,
    retry_callback=callback_handler.retry
)


def send_to_influxdb(driver_name, telemetry_data):
    """
    Sends telemetry data to InfluxDB 3.0.

    Args:
        driver_name (str): The name of the driver (used as a tag).
        telemetry_data: An object (e.g., from pyirsdk) containing telemetry fields.
                        Assumed to have attributes like FuelLevel, Lap, Speed.
    """
    try:
        # InfluxDB 3.0 writes data as rows. A dictionary represents a single row.
        # 'measurement' is the equivalent of a table name in InfluxDB 3.0
        # Tags are key-value pairs that are indexed for fast querying.
        # Fields are the actual data values.
        # 'time' is automatically added by the client if not specified,
        # using the current timestamp.
        # data_row = {
        #     "measurement": "iracing_telemetry",
        #     "tags": {
        #         "driver": driver_name,
        #         "track": "monza",
        #         "car": "bmw m4 gt3",
        #         "lap": telemetry_data["Lap"]
        #     },
        #     "fields": {
        #         "FuelLevel": telemetry_data["FuelLevel"],
        #         "FuelLevelPct": telemetry_data["FuelLevelPct"],
        #         # Add other relevant telemetry fields here
        #         # Example: "rpm": telemetry_data.RPM,
        #         # Example: "gear": telemetry_data.Gear,
        #         # Example: "throttle": telemetry_data.Throttle,
        #         # Example: "brake": telemetry_data.Brake,
        #         # ...
        #     }
        # }

        # Write the data. The client handles the connection and writing.
        # InfluxDB 3.0 client's write method is designed for synchronous writes by default.
        #write_api.write(INFLUX_DATABASE, INFLUX_ORG, data_row)

            # print(telemetry_data[i])
        point = generate_telemetry_point(driver_name, telemetry_data)
        client.write(point)

        client.close()
        # print(f"Data sent for {driver_name} - Lap {telemetry_data.Lap}")

    except InfluxDBError as e:
        print(e.message)
        # client.close()
    except Exception as e:
        print(f"Error sending data to InfluxDB: {e}")
        # In a real application, you might want more sophisticated error logging
        # or retry mechanisms.


with InfluxDBClient3(
        host=INFLUXDB_HOST,
        token=INFLUXDB_TOKEN,
        database=INFLUXDB_DATABASE,
        write_client_options=wco  # Pass the configured write client options here
) as client:
    # write_api = client._write_api(write_options=SYNCHRONOUS)
    print(f"Connected to InfluxDB 3 at {INFLUXDB_HOST}, database: {INFLUXDB_DATABASE}")
    print(f"Batching configured: batch_size={BATCH_SIZE}, flush_interval={FLUSH_INTERVAL_MS}ms")

def generate_telemetry_point(driver_name, telemetry_data) -> Point:
    return Point("telemetry_data") \
        .tag("driver", driver_name) \
        .tag("track", "monza") \
        .tag("lap", telemetry_data["Lap"]) \
        .field("FuelLevel", telemetry_data["FuelLevel"])

# How to integrate this:
# 1. Ensure you have the 'influxdb_client_3' library installed (`pip install influxdb_client_3`).
# 2. Replace the placeholder INFLUX_URL, INFLUX_TOKEN, INFLUX_ORG, and INFLUX_DATABASE
#    with your actual InfluxDB 3.0 instance details.
# 3. Call `send_to_influxdb` inside your `pyirsdk` data polling loop,
#    passing the current driver's name and the `telemetry_data` object.

# Example usage within your pyirsdk loop (conceptual):
# import pyirsdk
# import time
#
# # ... (InfluxDB client initialization from above) ...
#
# def get_live_data_and_send():
#     try:
#         ir = pyirsdk.IrSDK()
#         driver_name = "TeamDriverA" # Replace with actual driver identification
#
#         while True:
#             telemetry_data = ir.telemetry_data
#             if telemetry_data:
#                 send_to_influxdb(driver_name, telemetry_data)
#             time.sleep(1)
#     except pyirsdk.exceptions.IrSdkException as e:
#         print(f"iRacing SDK Error: {e}")
#     except Exception as e:
#         print(f"An unexpected error occurred: {e}")
#
# if __name__ == "__main__":
#     print("Starting iRacing telemetry sender...")
#     get_live_data_and_send()
