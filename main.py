import pigpio
import time
import board
import csv
import threading
import collections
from datetime import datetime
from adafruit_bme280 import basic as adafruit_bme280  # noqa: E402
from adafruit_bno055 import BNO055_I2C  # noqa: E402

# 実行時間
RUN_TIME = 10  # seconds

# I2C定義
SDA_PIN = 2
SCL_PIN = 3
I2C_BUS_ID = 1
BME280_I2C_ADDR = 0x76
BNO055_I2C_ADDR = 0x28

class SensorReader:
    def __init__(self, pi, freq=100, output_file="sensor_log.csv", flush_interval=1.0):
        self.pi = pi
        self.freq = freq
        self.tick = 0
        self.output_file = output_file
        self.flush_interval = flush_interval
        self.running = True

        self.buffer = collections.deque()
        self.lock = threading.Lock()

        # I2C初期化
        i2c = board.I2C()
        self.bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c, address=BME280_I2C_ADDR)
        self.bno055 = BNO055_I2C(i2c, address=BNO055_I2C_ADDR)

        # 最新センサデータ（スレッド間共有）
        self.latest = {
            "pressure": None,
            "temperature": None,
            "accel": (None, None, None),
            "gyro": (None, None, None),
            "euler": (None, None, None)
        }

        self.data_lock = threading.Lock()

        # センサ読み取りスレッド起動
        self.bme_thread = threading.Thread(target=self.read_bme280_loop)
        self.bno_thread = threading.Thread(target=self.read_bno055_loop)
        self.bme_thread.start()
        self.bno_thread.start()

        # GPIO設定とPWM開始
        self.output_pin = 18
        self.input_pin = 17
        self.pi.set_mode(self.output_pin, pigpio.OUTPUT)
        self.pi.set_mode(self.input_pin, pigpio.INPUT)
        self.pi.hardware_PWM(self.output_pin, freq, 500000)

        # 割込み登録
        self.cb = self.pi.callback(self.input_pin, pigpio.RISING_EDGE, self.read_sensors)

        # 書き出しスレッド起動
        self.writer_thread = threading.Thread(target=self.flush_to_csv_loop)
        self.writer_thread.start()

        # ヘッダ書き込み
        with open(self.output_file, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                "tick", "timestamp",
                "pressure_hPa", "temp_C",
                "accel_x", "accel_y", "accel_z",
                "gyro_x", "gyro_y", "gyro_z",
                "euler_x", "euler_y", "euler_z"
            ])

    def read_bme280_loop(self):
        while self.running:
            try:
                pressure = self.bme280.pressure
                temperature = self.bme280.temperature
                with self.data_lock:
                    self.latest["pressure"] = pressure
                    self.latest["temperature"] = temperature
            except Exception as e:
                print(f"[BME280] 読み取りエラー: {e}")
            time.sleep(0.005) # ポーリング処理 200Hz


    def read_bno055_loop(self):
        while self.running:
            try:
                accel = self.bno055.acceleration or (None, None, None)
                gyro = self.bno055.gyro or (None, None, None)
                euler = self.bno055.euler or (None, None, None)
                with self.data_lock:
                    self.latest["accel"] = accel
                    self.latest["gyro"] = gyro
                    self.latest["euler"] = euler
            except Exception as e:
                print(f"[BNO055] 読み取りエラー: {e}")
            time.sleep(0.005) # ポーリング処理 200Hz

    def read_sensors(self, gpio, level, tick):
        timestamp = time.time()
        try:
            with self.data_lock:
                pressure = self.latest["pressure"]
                temperature = self.latest["temperature"]
                accel = self.latest["accel"]
                gyro = self.latest["gyro"]
                euler = self.latest["euler"]

            row = [
                self.tick, timestamp,
                pressure, temperature,
                *(accel or (None, None, None)),
                *(gyro or (None, None, None)),
                *(euler or (None, None, None))
            ]

            with self.lock:
                self.buffer.append(row)

            self.tick += 1
        except Exception as e:
            print(f"[{self.tick}] 読み取りエラー: {e}")

    def flush_to_csv_loop(self):
        while self.running:
            time.sleep(self.flush_interval)
            with self.lock:
                rows = list(self.buffer)
                self.buffer.clear()
            if rows:
                with open(self.output_file, "a", newline="") as f:
                    writer = csv.writer(f)
                    writer.writerows(rows)

    def stop(self):
        self.running = False
        self.cb.cancel()
        self.pi.hardware_PWM(self.output_pin, 0, 0)
        self.writer_thread.join()
        self.bme_thread.join()
        self.bno_thread.join()


if __name__ == "__main__":
    pi = pigpio.pi()
    if not pi.connected:
        print("pigpiod が起動していません")
        exit()

    # 現在時刻を使ってファイル名を生成
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    output_filename = f"sensor_log_{timestamp}.csv"
    
    reader = SensorReader(pi, freq=100, output_file=output_filename)
    try:
        print(f"記録を開始しました（ファイル: {output_filename}）")
        time.sleep(RUN_TIME)
    except KeyboardInterrupt:
        print("終了処理中...")
    finally:
        reader.stop()
        pi.stop()
