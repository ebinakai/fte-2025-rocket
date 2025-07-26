import pigpio
import time
import board
from adafruit_bme280 import basic as adafruit_bme280  # noqa: E402
from adafruit_bno055 import BNO055_I2C  # noqa: E402

# ──────────────────────────────────────────────────────────────────────────────
# I²C configuration constants (BCM numbering)
# ──────────────────────────────────────────────────────────────────────────────

SDA_PIN: int = 2              # GPIO2 (physical pin 3)
SCL_PIN: int = 3              # GPIO3 (physical pin 5)
I2C_BUS_ID: int = 1           # Default I²C bus on Raspberry Pi

BME280_I2C_ADDR: int = 0x76   # 0x77 if CSB pin HIGH
BNO055_I2C_ADDR: int = 0x28   # 0x29 if ADR pin HIGH

class SensorReader:
    def __init__(self, pi, freq=100):
        self.pi = pi
        self.freq = freq
        self.tick = 0

        # I2C初期化
        i2c = board.I2C()
        self.bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c, address=BME280_I2C_ADDR)
        self.bno055 = BNO055_I2C(i2c, address=BNO055_I2C_ADDR)

        # タイマ割り込み用PWM出力ピンと入力ピン（ループバック）
        self.output_pin = 18  # PWM出力
        self.input_pin = 4    # 割り込み検出

        self.pi.set_mode(self.output_pin, pigpio.OUTPUT)
        self.pi.set_mode(self.input_pin, pigpio.INPUT)

        # 100Hz PWM信号出力
        self.pi.hardware_PWM(self.output_pin, freq, 500000)

        # 割り込みコールバック設定
        self.cb = self.pi.callback(self.input_pin, pigpio.RISING_EDGE, self.read_sensors)

    def read_sensors(self, gpio, level, tick):
        # タイマ割り込みで実行される処理
        pressure = self.bme280.pressure
        temperature = self.bme280.temperature
        acceleration = self.bno055.acceleration
        gyro = self.bno055.gyro
        euler = self.bno055.euler

        print(f"[{self.tick}] {time.time():.3f}s")
        print(f"  Pressure: {pressure:.2f} hPa, Temp: {temperature:.2f} °C")
        print(f"  Accel: {acceleration}, Gyro: {gyro}, Euler: {euler}")
        self.tick += 1

    def stop(self):
        self.cb.cancel()
        self.pi.hardware_PWM(self.output_pin, 0, 0)

# 実行
if __name__ == "__main__":
    pi = pigpio.pi()
    if not pi.connected:
        print("pigpioデーモンが起動していません")
        exit()

    try:
        reader = SensorReader(pi)
        time.sleep(10)  # 10秒間テスト実行
    finally:
        reader.stop()
        pi.stop()
