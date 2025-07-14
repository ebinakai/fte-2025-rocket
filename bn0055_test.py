#!/usr/bin/env python3
"""Minimal test script for the **AE‑BNO055‑BO (Bosch BNO055)**
9‑axis sensor‑fusion module on a Raspberry Pi using the I²C bus.

The script focuses on reading **raw acceleration** (m/s²) but can be
extended to fetch gyro, magnetometer, Euler angles, etc.

It mirrors the structure and debug verbosity of *bme280_test.py* so you
can drop it into the same environment without additional setup.

Prerequisites
-------------
```bash
# Install the CircuitPython driver and its dependencies
pip3 install --upgrade adafruit-circuitpython-bno055 adafruit-blinka RPi.GPIO
```

Wiring (BCM pin numbers)
------------------------
BNO055 | Raspberry Pi GPIO (BCM)
-------|------------------------
SDA    | GPIO2
SCL    | GPIO3
VIN    | 3 V3 (module on‑board regulator handles 3 – 5 V)
GND    | GND

If ADR pin is **LOW** (default), the I²C address is **0x28**.
If ADR pin is tied **HIGH**, it becomes **0x29**.
"""

from __future__ import annotations

import sys
import time
import importlib.metadata as imm

import board  # noqa: E402
import busio  # noqa: E402
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

SDA_PIN: int = 2            # GPIO2 (physical pin 3)
SCL_PIN: int = 3            # GPIO3 (physical pin 5)
I2C_BUS_ID: int = 1         # Default I²C bus on Raspberry Pi
BNO055_I2C_ADDR: int = 0x28  # 0x29 if ADR pin is HIGH

# ──────────────────────────────────────────────────────────────────────────────
# Main logic
# ──────────────────────────────────────────────────────────────────────────────

def main() -> None:
    """Continuously read acceleration data with debug output."""
    # Diagnostics: library path & version
    _debug(f"adafruit_bno055 path = {BNO055_I2C.__module__}")
    try:
        _debug(f"adafruit_bno055 version = {imm.version('adafruit-circuitpython-bno055')}")
    except imm.PackageNotFoundError:
        _debug("Unable to determine library version via importlib.metadata")

    _debug("Initialising I²C bus …")
    i2c = busio.I2C(board.SCL, board.SDA)

    _debug("Waiting for I²C lock …")
    while not i2c.try_lock():
        pass
    detected = [hex(addr) for addr in i2c.scan()]
    _debug(f"I²C devices detected: {detected}")
    i2c.unlock()

    _debug(f"Creating BNO055 instance at address {hex(BNO055_I2C_ADDR)} …")
    sensor = BNO055_I2C(i2c, address=BNO055_I2C_ADDR)
    _debug("Sensor initialised successfully.")

    print("Press Ctrl+C to stop…\n")

    iteration = 0
    while True:
        iteration += 1
        _debug(f"Reading acceleration (iteration #{iteration}) …")

        accel = sensor.acceleration  # Tuple[float, float, float] in m/s²
        if accel is None:
            _debug("Acceleration read returned None — sensor not ready?")
            time.sleep(0.5)
            continue

        ax, ay, az = accel
        print(f"Accel X: {ax:7.2f} m/s²  Accel Y: {ay:7.2f} m/s²  Accel Z: {az:7.2f} m/s²")
        print("-" * 60)

        time.sleep(0.2)


if __name__ == "__main__":
    _debug("BNO055 test script starting …")
    try:
        main()
    except KeyboardInterrupt:
        _debug("User interrupted execution with Ctrl+C. Exiting.")
