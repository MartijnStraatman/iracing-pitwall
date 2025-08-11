# WIP: iRacing Telemetry to InfluxDB

This project is a Python script that captures live telemetry data from the iRacing simulator and streams it to an InfluxDB database. It's designed to provide a robust way to collect, store, and analyze your race data for performance insights.

## Features

* **Real-Time Data Streaming:** Captures telemetry variables from iRacing with a one-second interval.

* **InfluxDB Integration:** Uses the official `influxdb_client_3` library for efficient batch writing to an InfluxDB database.

* **Automatic Session Info:** Automatically fetches the track name, driver's name, and a unique session ID from iRacing.

* **Command-Line Configuration:** Allows easy setup of InfluxDB connection details without modifying the code.

* **Graceful Shutdown:** The script handles disconnections from iRacing and shuts down cleanly using `Ctrl+C`.

## Prerequisites

Before running this script, you'll need the following:

1. **Python 3.x:** Installed on your system.

2. **iRacing:** The simulator must be running and connected.

3. **InfluxDB:** A running instance of InfluxDB (e.g., InfluxDB 3.0 via Docker).

## Installation

Follow these steps to set up the project.

### 1. Clone the Repository

First, clone this repository to your local machine.