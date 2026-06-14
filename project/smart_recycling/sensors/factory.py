# ==================================================
# Gachon University
# Introduction to Internet of Things (13966_001)
# 2026-1 Semester Team C
#
# Sensors factory
# ==================================================
from __future__ import annotations
from dataclasses import dataclass
from smart_recycling.config import Config
from smart_recycling.sensors.mock import MockPirSensor, MockUltrasonicSensor
from smart_recycling.sensors.pir import PirSensor
from smart_recycling.sensors.ultrasonic import UltrasonicSensor
from .bin_ultrasonic import BinUltrasonicSensor
from .temp_humidity import TempHumiditySensor
from .servo import ServoLid

# Code for creating and managing sensors
# Managing all sensors
@dataclass
class SensorSuite:
    # pir sensor
    pir: object | None = None
    # ultrasonic sensor
    ultrasonic: object | None = None
    # temperature and humidity sensor
    temp_humidity: object | None = None
    # bin ultrasonic sensor for capacity
    bin_ultrasonic: object | None = None
    # Servo
    lid: object | None = None

    # clear if program ends
    def close(self) -> None:
        for sensor in (self.pir, self.ultrasonic, 
                       self.temp_humidity, self.bin_ultrasonic, self.lid):
            if sensor is not None:
                try:
                    sensor.close()
                except Exception:
                    pass

# create sensor
def build_sensors(config: Config, mock: bool = False) -> SensorSuite:
    # mock sensor for test
    if mock:
        return SensorSuite(pir=MockPirSensor(), ultrasonic=MockUltrasonicSensor())

    pir = None
    ultrasonic = None
    temp_humidity = None
    bin_ultrasonic = None
    lid = None

    # create pir if it is enable
    if config.sensors.pir.enabled:
        pir = PirSensor(config.sensors.pir.pin)

    # create Ultrasonic if it is enable
    if config.sensors.ultrasonic.enabled:
        ultrasonic = UltrasonicSensor(
            trigger_pin=config.sensors.ultrasonic.trigger_pin,          # transmit
            echo_pin=config.sensors.ultrasonic.echo_pin,                # receive
            timeout_seconds=config.sensors.ultrasonic.timeout_seconds,  # Measurement time limit
            samples=config.sensors.ultrasonic.samples,                  # number of samples
            sample_delay_seconds=config.sensors.ultrasonic.sample_delay_seconds, # Measurement interval
        )
    
    # create temp_humidity if it is enabled
    if config.sensors.temp_humidity.enabled:
        temp_humidity = TempHumiditySensor(config.sensors.temp_humidity.pin)
 
    # create bin_ultrasonic if it is enabled
    if config.sensors.bin_ultrasonic.enabled:
        bin_ultrasonic = BinUltrasonicSensor(
            trigger_pin=config.sensors.bin_ultrasonic.trigger_pin,
            echo_pin=config.sensors.bin_ultrasonic.echo_pin,
            bin_depth_cm=config.sensors.bin_ultrasonic.bin_depth_cm,
            full_threshold_cm=config.sensors.bin_ultrasonic.full_threshold_cm,
            timeout_seconds=config.sensors.bin_ultrasonic.timeout_seconds,
            samples=config.sensors.bin_ultrasonic.samples,
            sample_delay_seconds=config.sensors.bin_ultrasonic.sample_delay_seconds,
        )

    if config.sensors.lid.enabled:
        lid = ServoLid(config.sensors.lid.pin)

    return SensorSuite(pir=pir, ultrasonic=ultrasonic, temp_humidity=temp_humidity,
        bin_ultrasonic=bin_ultrasonic, lid=lid,)