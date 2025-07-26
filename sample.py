#!/usr/bin/env python3
"""Combined test script for **Bosch BME280** (env-sensor) and
**AE-BNO055-BO (Bosch BNO055)** 9-axis sensor-fusion module on a Raspberry Pi.

Reads **temperature / humidity / pressure** from the BME280 and
**raw acceleration** from the BNO055 using the same I²C bus, and prints
both sets once per second with detailed debug output.

Prerequisites (same venv as individual tests)
--------------------------------------------
```bash
pip3 install --upgrade \
    adafruit-circuitpython-bme280 \
    adafruit-circuitpython-bno055 \
    adafruit-blinka RPi.GPIO
```

If the BNO055 ADR pin is tied **HIGH**, change `BNO055_I2C_ADDR` to
`0x29`. For the BME280, swap `BME280_I2C_ADDR` between `0x76` and `0x77`
as required.
"""

from __future__ import annotations

import sys
import time
import importlib.metadata as imm

import board  # noqa: E402
import busio  # noqa: E402
from adafruit_bme280 import basic as adafruit_bme280  # noqa: E402
from adafruit_bno055 import BNO055_I2C  # noqa: E402

# ──────────────────────────────────────────────────────────────────────────────
# Debug helper
# ──────────────────────────────────────────────────────────────────────────────

DEBUG_PREFIX = "[DEBUG]"

def _debug(msg: str) -> None:
    """Print *msg* to stderr with a common prefix."""
    print(f"{DEBUG_PREFIX} {msg}", file=sys.stderr)

# ──────────────────────────────────────────────────────────────────────────────
# I²C configuration constants (BCM numbering)
# ──────────────────────────────────────────────────────────────────────────────

SDA_PIN: int = 2              # GPIO2 (physical pin 3)
SCL_PIN: int = 3              # GPIO3 (physical pin 5)
I2C_BUS_ID: int = 1           # Default I²C bus on Raspberry Pi

BME280_I2C_ADDR: int = 0x76   # 0x77 if CSB pin HIGH
BNO055_I2C_ADDR: int = 0x28   # 0x29 if ADR pin HIGH

# ──────────────────────────────────────────────────────────────────────────────
# Main logic
# ──────────────────────────────────────────────────────────────────────────────

def main() -> None:
    """Continuously read both sensors with debug output."""
    # Diagnostics: show library versions
    for pkg in ("adafruit-circuitpython-bme280", "adafruit-circuitpython-bno055"):
        try:
            _debug(f"{pkg} version = {imm.version(pkg)}")
        except imm.PackageNotFoundError:
            _debug(f"Unable to determine {pkg} version via importlib.metadata")

    _debug("Initialising I²C bus …")
    i2c = busio.I2C(board.SCL, board.SDA)

    _debug("Waiting for I²C lock …")
    while not i2c.try_lock():
        pass
    detected = [hex(addr) for addr in i2c.scan()]
    _debug(f"I²C devices detected: {detected}")
    i2c.unlock()

    # Instantiate sensors
    _debug(f"Creating BME280 instance at {hex(BME280_I2C_ADDR)} …")
    bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c, address=BME280_I2C_ADDR)

    _debug(f"Creating BNO055 instance at {hex(BNO055_I2C_ADDR)} …")
    bno055 = BNO055_I2C(i2c, address=BNO055_I2C_ADDR)
    _debug("Sensors initialised successfully.")

    print("Press Ctrl+C to stop…\n")
    iteration = 0
    while True:
        iteration += 1
        _debug(f"Reading sensors (iteration #{iteration}) …")

        # BME280 readings
        temp_c = bme280.temperature
        humidity = bme280.humidity
        pressure = bme280.pressure

        # BNO055 acceleration
        accel = bno055.acceleration
        if accel is None:
            _debug("Acceleration read returned None — sensor not ready?")
            accel = (float("nan"),) * 3
        ax, ay, az = accel

        # Print consolidated line
        print(
            f"Temp: {temp_c:6.2f} °C  Hum: {humidity:6.2f} %  "
            f"Pres: {pressure:7.2f} hPa  |  "
            f"Accel X: {ax:7.2f} m/s²  Y: {ay:7.2f} m/s²  Z: {az:7.2f} m/s²"
        )
        print("=" * 100)

        time.sleep(1)


if __name__ == "__main__":
    _debug("Combined sensor test script starting …")
    try:
        main()
    except KeyboardInterrupt:
        _debug("User interrupted execution with Ctrl+C. Exiting.")
