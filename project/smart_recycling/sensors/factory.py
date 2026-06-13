from __future__ import annotations

from dataclasses import dataclass

from smart_recycling.config import Config
from smart_recycling.sensors.mock import MockPirSensor, MockUltrasonicSensor
from smart_recycling.sensors.pir import PirSensor
from smart_recycling.sensors.ultrasonic import UltrasonicSensor


@dataclass
class SensorSuite:
    pir: object | None = None
    ultrasonic: object | None = None

    def close(self) -> None:
        for sensor in (self.pir, self.ultrasonic):
            if sensor is not None:
                try:
                    sensor.close()
                except Exception:
                    pass


def build_sensors(config: Config, mock: bool = False) -> SensorSuite:
    if mock:
        return SensorSuite(pir=MockPirSensor(), ultrasonic=MockUltrasonicSensor())

    pir = None
    ultrasonic = None

    if config.sensors.pir.enabled:
        pir = PirSensor(config.sensors.pir.pin)

    if config.sensors.ultrasonic.enabled:
        ultrasonic = UltrasonicSensor(
            trigger_pin=config.sensors.ultrasonic.trigger_pin,
            echo_pin=config.sensors.ultrasonic.echo_pin,
            timeout_seconds=config.sensors.ultrasonic.timeout_seconds,
            samples=config.sensors.ultrasonic.samples,
            sample_delay_seconds=config.sensors.ultrasonic.sample_delay_seconds,
        )

    return SensorSuite(pir=pir, ultrasonic=ultrasonic)
