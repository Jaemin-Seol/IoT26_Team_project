from __future__ import annotations

from dataclasses import dataclass

from smart_recycling.config import Config
from smart_recycling.sensors.mock import MockPirSensor, MockUltrasonicSensor
from smart_recycling.sensors.pir import PirSensor
from smart_recycling.sensors.ultrasonic import UltrasonicSensor

# Code for creating and managing sensors
# Managing all sensors
@dataclass
class SensorSuite:
    # pir sensor
    pir: object | None = None
    # ultrasonic sensor
    ultrasonic: object | None = None

    # clear if program ends
    def close(self) -> None:
        for sensor in (self.pir, self.ultrasonic):
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
    return SensorSuite(pir=pir, ultrasonic=ultrasonic)
