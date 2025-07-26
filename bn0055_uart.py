#!/usr/bin/env python3
"""UART test script for AE‑BNO055‑BO (Bosch BNO055) 9-axis sensor"""

from __future__ import annotations

import sys
import time
import importlib.metadata as imm

import board
import busio
import serial
from adafruit_bno055 import BNO055_UART

# ─────────────────────────────────────────────────────
# Debug helper
# ─────────────────────────────────────────────────────
DEBUG_PREFIX = "[DEBUG]"

def _debug(msg: str) -> None:
    """Print debug messages to stderr."""
    print(f"{DEBUG_PREFIX} {msg}", file=sys.stderr)

# ─────────────────────────────────────────────────────
# UART設定
# ─────────────────────────────────────────────────────

UART_PORT = "/dev/serial0"  # 通常、Raspberry PiのUARTはここ
BAUDRATE = 115200           # BNO055のデフォルトボーレート（切り替え可能）
TIMEOUT = 1.0               # 秒

# ─────────────────────────────────────────────────────
# メイン処理
# ─────────────────────────────────────────────────────

def main() -> None:
    """UART経由で加速度データを読み取るループ"""
    _debug(f"adafruit_bno055 path = {BNO055_UART.__module__}")
    try:
        _debug(f"adafruit_bno055 version = {imm.version('adafruit-circuitpython-bno055')}")
    except imm.PackageNotFoundError:
        _debug("Unable to determine library version")

    _debug(f"Opening UART port: {UART_PORT} at {BAUDRATE} baud …")
    uart = serial.Serial(UART_PORT, baudrate=BAUDRATE, timeout=TIMEOUT)

    _debug("Creating BNO055 instance over UART …")
    sensor = BNO055_UART(uart)
    _debug("Sensor initialised successfully.")

    iteration = 0
    totalStartTime = time.time()
    for i in range(1000):
        try:
            startTime = time.time()
            iteration += 1
            # _debug(f"Reading acceleration (iteration #{iteration}) …")

            accel = sensor.acceleration
            if accel is None:
                _debug("Acceleration read returned None — sensor not ready?")
                time.sleep(0.5)
                continue

            ax, ay, az = accel
            # print(f"Accel X: {ax:7.2f} m/s²  Accel Y: {ay:7.2f} m/s²  Accel Z: {az:7.2f} m/s²")
            # print("-" * 60)
            elapsed = time.time() - startTime
            # _debug(f"Iteration #{iteration} completed in {elapsed:.3f} seconds.")
        except Exception as e:
            _debug(f"Error during reading: {e}")
        time.sleep(0.004)
    totalElapsed = time.time() - totalStartTime
    _debug(f"Total iterations: {iteration}, Total elapsed time: {totalElapsed:.3f} seconds.")
    if iteration > 0:
        _debug(f"Average time per iteration: {totalElapsed / iteration:.3f} seconds.")

if __name__ == "__main__":
    _debug("BNO055 UART test script starting …")
    try:
        main()
    except KeyboardInterrupt:
        _debug("User interrupted execution with Ctrl+C. Exiting.")
