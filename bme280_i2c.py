#!/usr/bin/env python3
"""Minimal test script for a BME280 temperature / humidity / pressure sensor
on a Raspberry Pi using the I²C interface.

Added DEBUG print statements to help trace the control flow and collected
sensor data.  No functional changes were made.

Prerequisites
-------------
1. **Enable I²C on the Raspberry Pi** (see earlier notes)
2. **Install libraries**
   ```bash
   pip3 install adafruit-circuitpython-bme280 adafruit-blinka RPi.GPIO
   ```

Wiring (BCM pin numbers)
------------------------
BME280 | Raspberry Pi GPIO (BCM)
-------|------------------------
SDA    | GPIO{SDA_PIN}
SCL    | GPIO{SCL_PIN}
VCC    | 3 V3 (pin 1 or 17)
GND    | GND  (pin 6, 9, 14…)
"""

from __future__ import annotations

import sys
import time

import board  # noqa: E402  – import order preserved on purpose
import busio  # noqa: E402
from adafruit_bme280 import basic as adafruit_bme280

# ──────────────────────────────────────────────────────────────────────────────
# Debug helper
# ──────────────────────────────────────────────────────────────────────────────

DEBUG_PREFIX = "[DEBUG]"

def _debug(msg: str) -> None:
    """Print *msg* to stderr with a common prefix."""
    print(f"{DEBUG_PREFIX} {msg}", file=sys.stderr)

# ──────────────────────────────────────────────────────────────────────────────
# GPIO / I²C configuration (BCM numbering)
# ──────────────────────────────────────────────────────────────────────────────

SDA_PIN: int = 2           # GPIO2  (physical pin 3)
SCL_PIN: int = 3           # GPIO3  (physical pin 5)
I2C_BUS_ID: int = 1        # Raspberry Pi uses I²C bus 1 by default
BME280_I2C_ADDR: int = 0x76  # Change to 0x77 if your board is jumpered so

# ──────────────────────────────────────────────────────────────────────────────
# Sensor setup
# ──────────────────────────────────────────────────────────────────────────────

def main() -> None:
    """Continuously read and print sensor values with debug output."""
    _debug("Initialising I²C bus …")
    i2c = busio.I2C(board.SCL, board.SDA)

    _debug("Waiting for I²C lock …")
    while not i2c.try_lock():
        pass
    detected = [hex(addr) for addr in i2c.scan()]
    _debug(f"I²C devices detected: {detected}")
    i2c.unlock()

    _debug(f"Creating BME280 instance at address {hex(BME280_I2C_ADDR)} …")
    bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c, address=BME280_I2C_ADDR)
    _debug("Sensor initialised successfully.")

    print("Press Ctrl+C to stop…\n")

    iteration = 0
    while True:
        iteration += 1
        _debug(f"Reading sensor values (iteration #{iteration}) …")

        temperature = bme280.temperature
        humidity = bme280.humidity
        pressure = bme280.pressure

        print(f"Temperature : {temperature:6.2f} °C")
        print(f"Humidity    : {humidity:6.2f} %")
        print(f"Pressure    : {pressure:6.2f} hPa")
        print("-" * 40)

        time.sleep(2)


if __name__ == "__main__":
    _debug("BME280 test script starting …")
    try:
        main()
    except KeyboardInterrupt:
        _debug("User interrupted execution with Ctrl+C. Exiting.")
